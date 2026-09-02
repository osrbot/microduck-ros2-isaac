"""Pure-Python checks for the ROS/Isaac localhost protocol."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = (
    PROJECT_ROOT
    / "ros2_ws/src/microduck_control_bridge/microduck_control_bridge/protocol.py"
)
E2E_PROBE_PATH = PROJECT_ROOT / "scripts/validate_ros_isaac_e2e.py"
E2E_WRAPPER_PATH = PROJECT_ROOT / "scripts/validate_ros_isaac_e2e.sh"


def load_protocol():
    spec = importlib.util.spec_from_file_location("microduck_bridge_protocol", PROTOCOL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {PROTOCOL_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RosBridgeProtocolTests(unittest.TestCase):
    def test_live_e2e_requires_real_isaac_switch_and_ros_telemetry(self) -> None:
        probe = E2E_PROBE_PATH.read_text(encoding="utf-8")
        self.assertIn('behavior.data = "kick_left"', probe)
        self.assertIn('item.get("to") == "kick_left"', probe)
        self.assertIn("probe.telemetry_ready()", probe)
        self.assertIn("world_to_base_tf", probe)

        wrapper = E2E_WRAPPER_PATH.read_text(encoding="utf-8")
        self.assertIn("run_isaac_playground.sh", wrapper)
        self.assertIn("isaac_playground.launch.py", wrapper)
        self.assertIn("timeout --signal=INT --kill-after=10s", wrapper)

    def test_commands_are_clipped(self) -> None:
        protocol = load_protocol()
        self.assertEqual(
            protocol.clip_vector([1.0, -1.0, 2.0], protocol.VELOCITY_LIMITS),
            [0.4, -0.3, 1.0],
        )
        self.assertEqual(
            protocol.clip_vector([1.0] * 6, protocol.BODY_LIMITS),
            list(protocol.BODY_LIMITS),
        )

    def test_behavior_aliases_are_normalized(self) -> None:
        protocol = load_protocol()
        self.assertEqual(protocol.normalize_behavior("ground-pick"), "ground_pick")
        self.assertEqual(protocol.normalize_behavior("sit"), "sit")
        self.assertEqual(protocol.normalize_behavior("stand"), "stand")
        self.assertEqual(protocol.normalize_behavior("sit-toggle"), "sitstand")
        with self.assertRaises(ValueError):
            protocol.normalize_behavior("fly")

    def test_telemetry_enforces_joint_order(self) -> None:
        protocol = load_protocol()
        payload = {
            "policy": "walking",
            "joint_names": list(protocol.POLICY_JOINTS),
            "joint_positions": [0.0] * 14,
            "root_position": [0.0, 0.0, 0.125],
            "root_quaternion_xyzw": [0.0, 0.0, 0.0, 1.0],
            "upright": True,
            "tilt_rad": 0.0,
        }
        self.assertTrue(protocol.validate_telemetry(payload)["upright"])
        payload["joint_names"][0], payload["joint_names"][1] = (
            payload["joint_names"][1],
            payload["joint_names"][0],
        )
        with self.assertRaises(ValueError):
            protocol.validate_telemetry(payload)

    def test_telemetry_rejects_wrong_types_and_bad_quaternion(self) -> None:
        protocol = load_protocol()
        with self.assertRaises(ValueError):
            protocol.validate_telemetry([])
        payload = {
            "policy": "standing",
            "joint_names": list(protocol.POLICY_JOINTS),
            "joint_positions": [0.0] * 14,
            "root_position": [0.0, 0.0, 0.125],
            "root_quaternion_xyzw": [0.0, 0.0, 0.0, 0.0],
            "upright": "yes",
            "tilt_rad": 0.0,
        }
        with self.assertRaises(ValueError):
            protocol.validate_telemetry(payload)


if __name__ == "__main__":
    unittest.main()
