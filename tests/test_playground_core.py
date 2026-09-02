"""Regression tests for MicroDuck playground policy switching."""

from __future__ import annotations

import math
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from microduck_playground_core import (  # noqa: E402
    ACTION_SIZE,
    BODY_COMMAND_LIMITS,
    COMMAND_SIZE,
    GROUND_PICK_END_PHASE,
    OBSERVATION_SIZE,
    POLICY_JOINTS,
    SITSTAND_RISE_SECONDS,
    TIMED_BEHAVIOR_SECONDS,
    PlaygroundController,
    validate_udp_command,
)


ALL_POLICIES = {
    "walking",
    "standing",
    "sitstand",
    "ground_pick",
    "kick_left",
    "kick_right",
    "roulade",
}


class PolicyContractTests(unittest.TestCase):
    def test_dimensions_are_stable(self) -> None:
        self.assertEqual(len(POLICY_JOINTS), ACTION_SIZE)
        self.assertEqual(COMMAND_SIZE, 13)
        self.assertEqual(OBSERVATION_SIZE, 61)

    def test_walk_and_stand_switch_on_velocity(self) -> None:
        controller = PlaygroundController(available_policies=ALL_POLICIES.copy())
        self.assertEqual(controller.current_policy, "standing")
        controller.set_velocity(0.3, 0.0, 0.0)
        self.assertEqual(controller.current_policy, "walking")
        self.assertEqual(controller.command()[:3], (0.3, 0.0, 0.0))
        controller.set_velocity(0.0, 0.0, 0.0)
        self.assertEqual(controller.current_policy, "standing")

    def test_sitstand_uses_posture_flag(self) -> None:
        controller = PlaygroundController(available_policies=ALL_POLICIES.copy())
        self.assertTrue(controller.toggle_sitstand())
        self.assertEqual(controller.current_policy, "sitstand")
        self.assertEqual(controller.command()[:3], (1.0, 0.0, 0.0))
        self.assertTrue(controller.toggle_sitstand())
        self.assertEqual(controller.command()[:3], (0.0, 0.0, 0.0))
        self.assertEqual(controller.sit_state, "rising")
        controller.update(SITSTAND_RISE_SECONDS)
        self.assertEqual(controller.current_policy, "standing")

    def test_explicit_posture_commands_are_idempotent(self) -> None:
        controller = PlaygroundController(available_policies=ALL_POLICIES.copy())
        self.assertTrue(controller.trigger("stand"))
        self.assertEqual(controller.sit_state, "up")
        self.assertTrue(controller.trigger("sit"))
        self.assertTrue(controller.trigger("sit"))
        self.assertEqual(controller.sit_state, "sitting")
        self.assertTrue(controller.trigger("stand"))
        self.assertEqual(controller.sit_state, "rising")

    def test_ground_pick_encodes_one_phase_cycle(self) -> None:
        controller = PlaygroundController(available_policies=ALL_POLICIES.copy())
        self.assertTrue(controller.trigger_ground_pick())
        self.assertEqual(controller.command()[:3], (1.0, 0.0, 0.0))
        controller.update(controller.ground_pick_period_s / 4.0)
        phase_command = controller.command()[:3]
        self.assertAlmostEqual(phase_command[0], 0.0, places=7)
        self.assertAlmostEqual(phase_command[1], 1.0, places=7)
        controller.update(
            (GROUND_PICK_END_PHASE - 0.25) * controller.ground_pick_period_s
        )
        self.assertEqual(controller.current_policy, "standing")

    def test_ground_pick_zero_pads_head_and_body_commands(self) -> None:
        controller = PlaygroundController(available_policies=ALL_POLICIES.copy())
        controller.set_head([0.2, -0.2, 0.4, 0.1])
        controller.set_body([0.01, -0.01, 0.02, 0.1, -0.1, 0.2])
        self.assertTrue(controller.trigger_ground_pick())
        self.assertEqual(controller.command()[3:], (0.0,) * 10)

    def test_timed_behavior_zeroes_commands_and_returns(self) -> None:
        controller = PlaygroundController(available_policies=ALL_POLICIES.copy())
        controller.set_velocity(0.3, 0.1, -0.2)
        controller.set_head([0.2, -0.2, 0.4, 0.1])
        self.assertTrue(controller.trigger_timed_behavior("roulade"))
        self.assertEqual(controller.command(), (0.0,) * COMMAND_SIZE)
        controller.update(TIMED_BEHAVIOR_SECONDS["roulade"])
        self.assertEqual(controller.current_policy, "standing")

    def test_policy_specific_action_scale_matches_runtime(self) -> None:
        controller = PlaygroundController(available_policies=ALL_POLICIES.copy())
        self.assertEqual(controller.action_scale(), 1.0)
        controller.set_velocity(0.2, 0.0, 0.0)
        self.assertEqual(controller.current_policy, "walking")
        self.assertEqual(controller.action_scale(), 0.9)
        self.assertTrue(controller.trigger_timed_behavior("kick_left"))
        self.assertEqual(controller.action_scale(), 1.0)

    def test_head_commands_are_clipped(self) -> None:
        controller = PlaygroundController(available_policies=ALL_POLICIES.copy())
        controller.set_head([2.0, -2.0, 2.0, -2.0])
        self.assertEqual(controller.head_command, [1.1, -1.1, 1.4, -0.31])
        self.assertTrue(all(math.isfinite(value) for value in controller.command()))

    def test_velocity_and_body_commands_are_validated(self) -> None:
        controller = PlaygroundController(available_policies=ALL_POLICIES.copy())
        controller.set_velocity(2.0, -2.0, 3.0)
        self.assertEqual(controller.velocity_command, [0.4, -0.3, 1.0])
        controller.set_body([0.2, -0.2, 0.2, 1.0, -1.0, 1.0])
        self.assertEqual(
            controller.body_command,
            [
                BODY_COMMAND_LIMITS[0],
                -BODY_COMMAND_LIMITS[1],
                BODY_COMMAND_LIMITS[2],
                BODY_COMMAND_LIMITS[3],
                -BODY_COMMAND_LIMITS[4],
                BODY_COMMAND_LIMITS[5],
            ],
        )
        with self.assertRaises(ValueError):
            controller.set_head([0.0, math.nan, 0.0, 0.0])

    def test_missing_optional_policy_is_rejected_without_state_change(self) -> None:
        controller = PlaygroundController(available_policies={"walking", "standing"})
        self.assertFalse(controller.trigger("kick_left"))
        self.assertEqual(controller.current_policy, "standing")

    def test_walk_request_rises_before_locomotion(self) -> None:
        controller = PlaygroundController(available_policies=ALL_POLICIES.copy())
        self.assertTrue(controller.trigger("sit"))
        self.assertTrue(controller.trigger("walk"))
        self.assertEqual(controller.sit_state, "rising")
        self.assertEqual(controller.current_policy, "sitstand")
        controller.update(SITSTAND_RISE_SECONDS)
        self.assertEqual(controller.current_policy, "standing")

    def test_udp_command_is_atomic_clipped_and_session_aware(self) -> None:
        command = validate_udp_command(
            {
                "version": 1,
                "session": "bridge-a",
                "velocity": [2.0, -2.0, 3.0],
                "head": [2.0, -2.0, 2.0, -2.0],
                "body": [1.0] * 6,
                "behavior": "kick_left",
                "behavior_sequence": 1,
                "reset_sequence": 0,
            }
        )
        self.assertEqual(command["session"], "bridge-a")
        self.assertEqual(command["velocity"], [0.4, -0.3, 1.0])
        self.assertEqual(command["behavior_sequence"], 1)
        with self.assertRaises(ValueError):
            validate_udp_command(
                {
                    "version": 1,
                    "session": "bridge-a",
                    "velocity": [0.0, float("nan"), 0.0],
                }
            )
        with self.assertRaises(ValueError):
            validate_udp_command(
                {
                    "version": 1,
                    "session": "bridge-a",
                    "behavior_sequence": True,
                }
            )


if __name__ == "__main__":
    unittest.main()
