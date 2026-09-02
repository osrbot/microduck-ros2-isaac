"""Contract tests for the runnable ROS 2 examples."""

from __future__ import annotations

import unittest

from microduck_examples.isaac_sequences import SEQUENCES, sequence_duration
from microduck_examples.motion_library import (
    HOME_POSE,
    JOINT_LIMITS,
    JOINT_NAMES,
    POSES,
    ROUTINES,
    routine_duration,
    sample_routine,
)


class ExampleContractTests(unittest.TestCase):
    """Keep published example motions finite, bounded, and repeatable."""

    def test_rviz_poses_follow_the_14_joint_contract(self) -> None:
        self.assertEqual(len(JOINT_NAMES), 14)
        for pose in POSES.values():
            self.assertEqual(len(pose), len(JOINT_NAMES))
            for value, limits in zip(pose, JOINT_LIMITS, strict=True):
                self.assertGreaterEqual(value, limits[0])
                self.assertLessEqual(value, limits[1])

    def test_rviz_routines_return_home_and_repeat(self) -> None:
        for name in ROUTINES:
            duration = routine_duration(name)
            final_pose, _, done = sample_routine(name, duration)
            self.assertTrue(done)
            self.assertEqual(final_pose, HOME_POSE)
            repeated_pose, _, repeated_done = sample_routine(
                name, duration, repeat=True
            )
            self.assertFalse(repeated_done)
            self.assertEqual(repeated_pose, HOME_POSE)

    def test_isaac_sequences_are_safe_and_reset_both_ends(self) -> None:
        self.assertEqual(set(SEQUENCES), {"walk", "skills", "showcase"})
        for name, steps in SEQUENCES.items():
            self.assertGreater(sequence_duration(name), 0.0)
            self.assertTrue(steps[0].reset)
            self.assertTrue(steps[-1].reset)
            self.assertEqual(steps[-1].velocity, (0.0, 0.0, 0.0))


if __name__ == "__main__":
    unittest.main()
