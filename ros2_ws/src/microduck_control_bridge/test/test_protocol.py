"""Package-level tests for the ROS-to-Isaac UDP protocol helpers."""

from __future__ import annotations

import math
import unittest

from microduck_control_bridge import protocol


def valid_telemetry() -> dict[str, object]:
    """Return a minimal valid telemetry packet in policy joint order."""

    return {
        "policy": "standing",
        "joint_names": list(protocol.POLICY_JOINTS),
        "joint_positions": [0.0] * len(protocol.POLICY_JOINTS),
        "root_position": [0.0, 0.0, 0.125],
        "root_quaternion_xyzw": [0.0, 0.0, 0.0, 1.0],
        "upright": True,
        "tilt_rad": 0.0,
    }


class ProtocolTests(unittest.TestCase):
    """Exercise validation through the installed ROS package import."""

    def test_command_vectors_are_clipped_and_reject_non_finite_values(self) -> None:
        self.assertEqual(
            protocol.clip_vector([1.0, -1.0, 2.0], protocol.VELOCITY_LIMITS),
            [0.4, -0.3, 1.0],
        )
        with self.assertRaisesRegex(ValueError, "finite"):
            protocol.clip_vector([math.nan, 0.0, 0.0], protocol.VELOCITY_LIMITS)

    def test_behavior_aliases_are_normalized(self) -> None:
        self.assertEqual(protocol.normalize_behavior("ground-pick"), "ground_pick")
        self.assertEqual(protocol.normalize_behavior("sit-toggle"), "sitstand")
        with self.assertRaisesRegex(ValueError, "Unsupported behavior"):
            protocol.normalize_behavior("fly")

    def test_telemetry_requires_joint_order_and_normalized_quaternion(self) -> None:
        payload = valid_telemetry()
        self.assertIs(protocol.validate_telemetry(payload)["upright"], True)

        payload["joint_names"] = list(reversed(protocol.POLICY_JOINTS))
        with self.assertRaisesRegex(ValueError, "joint order"):
            protocol.validate_telemetry(payload)

        payload = valid_telemetry()
        payload["root_quaternion_xyzw"] = [0.0, 0.0, 0.0, 0.0]
        with self.assertRaisesRegex(ValueError, "not normalized"):
            protocol.validate_telemetry(payload)


if __name__ == "__main__":
    unittest.main()
