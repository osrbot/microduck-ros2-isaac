"""Runtime constants shared by MicroDuck's native Isaac Lab tasks."""

from __future__ import annotations


POLICY_JOINTS = (
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
)

HOME_POSE = (
    0.0,
    -0.0873,
    -0.4579,
    -0.0049,
    0.4530,
    0.3491,
    0.3491,
    0.0,
    0.0,
    0.0,
    0.0873,
    0.4579,
    0.0049,
    -0.4530,
)

ACTION_SIZE = 14
COMMAND_SIZE = 13
OBSERVATION_SIZE = 61
HEAD_JOINTS = POLICY_JOINTS[5:9]
HEAD_INITIAL_RANGES = (
    (-0.05, 0.05),
    (-0.05, 0.05),
    (-0.07, 0.07),
    (-0.015, 0.015),
)
BODY_COMMAND_RANGES = (
    (-0.005, 0.005),
    (-0.005, 0.005),
    (-0.005, 0.005),
    (-0.05, 0.05),
    (-0.05, 0.05),
    (-0.05, 0.05),
)


def validate_contract() -> None:
    if len(POLICY_JOINTS) != ACTION_SIZE or len(HOME_POSE) != ACTION_SIZE:
        raise AssertionError("MicroDuck action and home-pose contracts must remain 14-dimensional")
    if 3 + 3 + ACTION_SIZE * 3 + COMMAND_SIZE != OBSERVATION_SIZE:
        raise AssertionError("MicroDuck actor observation must remain 61-dimensional")


validate_contract()
