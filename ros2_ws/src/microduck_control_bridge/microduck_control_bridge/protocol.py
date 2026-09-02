"""Validation helpers for the localhost ROS-to-Isaac UDP protocol."""

from __future__ import annotations

import math


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

VELOCITY_LIMITS = (0.4, 0.3, 1.0)
HEAD_LIMITS = (1.10, 1.10, 1.40, 0.31)
BODY_LIMITS = (
    0.02,
    0.02,
    0.03,
    math.radians(30.0),
    math.radians(30.0),
    math.radians(30.0),
)
BEHAVIORS = frozenset(
    {
        "walk",
        "sit",
        "stand",
        "sitstand",
        "ground_pick",
        "kick_left",
        "kick_right",
        "roulade",
    }
)


def clip_vector(values, limits: tuple[float, ...]) -> list[float]:
    values = tuple(float(value) for value in values)
    if len(values) != len(limits):
        raise ValueError(f"Expected {len(limits)} values, got {len(values)}")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Commands must be finite")
    return [max(-limit, min(limit, value)) for value, limit in zip(values, limits, strict=True)]


def normalize_behavior(value: str) -> str:
    behavior = value.strip().lower().replace("-", "_")
    aliases = {
        "sit_toggle": "sitstand",
        "walking": "walk",
        "locomotion": "walk",
        "pick": "ground_pick",
    }
    behavior = aliases.get(behavior, behavior)
    if behavior not in BEHAVIORS:
        raise ValueError(f"Unsupported behavior: {value!r}")
    return behavior


def validate_telemetry(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise ValueError("Telemetry must be a JSON object")
    required = {
        "policy",
        "joint_names",
        "joint_positions",
        "root_position",
        "root_quaternion_xyzw",
        "upright",
        "tilt_rad",
    }
    missing = required.difference(payload)
    if missing:
        raise ValueError(f"Telemetry fields missing: {sorted(missing)}")
    if not isinstance(payload["policy"], str) or not payload["policy"]:
        raise ValueError("Telemetry policy must be a non-empty string")
    try:
        if tuple(payload["joint_names"]) != POLICY_JOINTS:
            raise ValueError(
                "Telemetry joint order differs from the 14-joint policy contract"
            )
        positions = [float(value) for value in payload["joint_positions"]]
        root_position = [float(value) for value in payload["root_position"]]
        root_quaternion = [float(value) for value in payload["root_quaternion_xyzw"]]
        tilt_rad = float(payload["tilt_rad"])
    except (TypeError, ValueError) as error:
        raise ValueError(f"Telemetry vectors are invalid: {error}") from error
    if len(positions) != 14 or len(root_position) != 3 or len(root_quaternion) != 4:
        raise ValueError("Telemetry vector dimensions are invalid")
    values = positions + root_position + root_quaternion + [tilt_rad]
    if not all(math.isfinite(value) for value in values):
        raise ValueError("Telemetry contains a non-finite value")
    if not isinstance(payload["upright"], bool):
        raise ValueError("Telemetry upright flag must be boolean")
    if not 0.0 <= tilt_rad <= math.pi:
        raise ValueError("Telemetry tilt must be between zero and pi radians")
    quaternion_norm = math.sqrt(sum(value * value for value in root_quaternion))
    if abs(quaternion_norm - 1.0) > 0.01:
        raise ValueError("Telemetry root quaternion is not normalized")
    root_quaternion = [value / quaternion_norm for value in root_quaternion]
    return {
        **payload,
        "joint_positions": positions,
        "root_position": root_position,
        "root_quaternion_xyzw": root_quaternion,
        "upright": payload["upright"],
        "tilt_rad": tilt_rad,
    }
