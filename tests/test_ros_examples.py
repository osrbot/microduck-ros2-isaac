"""Pure-Python checks for the public ROS 2 example package."""

from __future__ import annotations

from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_SOURCE = PROJECT_ROOT / "ros2_ws/src/microduck_examples"
sys.path.insert(0, str(EXAMPLES_SOURCE))

from microduck_examples.isaac_sequences import SEQUENCES, sequence_duration  # noqa: E402
from microduck_examples.motion_library import (  # noqa: E402
    HOME_POSE,
    JOINT_LIMITS,
    JOINT_NAMES,
    POSES,
    ROUTINES,
    routine_duration,
    sample_routine,
)


class RosExampleTests(unittest.TestCase):
    def test_all_visual_poses_stay_inside_urdf_limits(self) -> None:
        self.assertEqual(len(JOINT_NAMES), 14)
        for pose_name, pose in POSES.items():
            self.assertEqual(len(pose), len(JOINT_NAMES), pose_name)
            for value, limits in zip(pose, JOINT_LIMITS, strict=True):
                self.assertGreaterEqual(value, limits[0], pose_name)
                self.assertLessEqual(value, limits[1], pose_name)

    def test_visual_routines_finish_at_home(self) -> None:
        for routine_name in ROUTINES:
            duration = routine_duration(routine_name)
            pose, _, done = sample_routine(routine_name, duration)
            self.assertTrue(done)
            self.assertEqual(pose, HOME_POSE)

    def test_isaac_sequences_are_reset_bounded(self) -> None:
        self.assertEqual(set(SEQUENCES), {"walk", "skills", "showcase"})
        for sequence_name, steps in SEQUENCES.items():
            self.assertGreater(sequence_duration(sequence_name), 0.0)
            self.assertTrue(steps[0].reset)
            self.assertTrue(steps[-1].reset)
            self.assertFalse(steps[-1].behavior)


if __name__ == "__main__":
    unittest.main()
