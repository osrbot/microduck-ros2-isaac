#!/usr/bin/env python3
"""Pure-Python state machine shared by the Isaac MicroDuck playground.

The module deliberately has no Isaac Sim, ROS, NumPy, or ONNX dependency so
policy switching and the 61-dimensional command contract can be tested on any
development machine.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
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

OBSERVATION_SIZE = 61
ACTION_SIZE = 14
COMMAND_SIZE = 13
HEAD_COMMAND_LIMITS = (1.10, 1.10, 1.40, 0.31)
VELOCITY_COMMAND_LIMITS = (0.4, 0.3, 1.0)
BODY_COMMAND_LIMITS = (
    0.02,
    0.02,
    0.03,
    math.radians(30.0),
    math.radians(30.0),
    math.radians(30.0),
)

# These defaults mirror the pinned ``robotd`` control path in
# pollen-robotics/microduck at the revision recorded in ``upstream.lock``.
WALKING_ACTION_SCALE = 0.9
SKILL_ACTION_SCALE = 1.0
GROUND_PICK_END_PHASE = 0.7
SITSTAND_RISE_SECONDS = 1.0
UDP_PROTOCOL_VERSION = 1

TIMED_BEHAVIOR_SECONDS = {
    "kick_left": 0.5,
    "kick_right": 0.5,
    "roulade": 1.0,
}

KNOWN_POLICIES = frozenset(
    {
        "walking",
        "standing",
        "sitstand",
        "ground_pick",
        *TIMED_BEHAVIOR_SECONDS,
    }
)


def _clip(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _validate_vector(
    values: object,
    limits: tuple[float, ...],
    label: str,
) -> list[float]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise ValueError(f"{label} command must be a numeric sequence")
    if len(values) != len(limits):
        raise ValueError(f"{label} command must contain {len(limits)} values, got {len(values)}")
    converted = [float(value) for value in values]
    if not all(math.isfinite(value) for value in converted):
        raise ValueError(f"{label} command must contain only finite values")
    return [
        _clip(value, -limit, limit)
        for value, limit in zip(converted, limits, strict=True)
    ]


def _validate_sequence(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label} must be a non-negative integer")
    return value


def validate_udp_command(payload: object) -> dict[str, object]:
    """Validate one ROS bridge packet before it can mutate controller state."""
    if not isinstance(payload, Mapping):
        raise ValueError("ROS UDP command must be a JSON object")
    if payload.get("version") != UDP_PROTOCOL_VERSION:
        raise ValueError("unsupported ROS UDP command version")

    session = payload.get("session", "legacy")
    if not isinstance(session, str) or not session.strip() or len(session) > 128:
        raise ValueError("ROS UDP session must be a non-empty string up to 128 characters")

    behavior = payload.get("behavior", "")
    if not isinstance(behavior, str):
        raise ValueError("behavior must be a string")

    return {
        "session": session,
        "velocity": _validate_vector(
            payload.get("velocity", [0.0, 0.0, 0.0]),
            VELOCITY_COMMAND_LIMITS,
            "Velocity",
        ),
        "head": _validate_vector(
            payload.get("head", [0.0, 0.0, 0.0, 0.0]),
            HEAD_COMMAND_LIMITS,
            "Head",
        ),
        "body": _validate_vector(
            payload.get("body", [0.0] * 6),
            BODY_COMMAND_LIMITS,
            "Body",
        ),
        "behavior": behavior,
        "behavior_sequence": _validate_sequence(
            payload.get("behavior_sequence", 0), "behavior_sequence"
        ),
        "reset_sequence": _validate_sequence(
            payload.get("reset_sequence", 0), "reset_sequence"
        ),
    }


@dataclass
class PlaygroundController:
    """Select a policy and build its shared 13-dimensional command block."""

    available_policies: set[str]
    switch_threshold: float = 0.05
    ground_pick_period_s: float = 4.0
    velocity_command: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    head_command: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    body_command: list[float] = field(default_factory=lambda: [0.0] * 6)

    def __post_init__(self) -> None:
        unknown = self.available_policies.difference(KNOWN_POLICIES)
        if unknown:
            raise ValueError(f"Unknown policy names: {sorted(unknown)}")
        if not self.available_policies.intersection({"walking", "standing", "sitstand"}):
            raise ValueError("At least one walking, standing, or sitstand policy is required")
        if self.switch_threshold < 0.0:
            raise ValueError("switch_threshold must be non-negative")
        if self.ground_pick_period_s <= 0.0:
            raise ValueError("ground_pick_period_s must be positive")
        self.current_policy = self._idle_policy()
        self.sit_state = "up"
        self.rise_time_left_s = 0.0
        self.ground_pick_phase = 0.0
        self.timed_behavior: str | None = None
        self.timed_behavior_left_s = 0.0
        self.reset_requested = False

    def _idle_policy(self) -> str:
        if "standing" in self.available_policies:
            return "standing"
        if "walking" in self.available_policies:
            return "walking"
        return "sitstand"

    def _automatic_locomotion_policy(self) -> str:
        speed = math.sqrt(sum(value * value for value in self.velocity_command))
        if speed <= self.switch_threshold and "standing" in self.available_policies:
            return "standing"
        if "walking" in self.available_policies:
            return "walking"
        if "standing" in self.available_policies:
            return "standing"
        return "sitstand"

    def reset(self) -> None:
        """Reset commands and request a physics-state reset from the runner."""
        self.velocity_command[:] = [0.0, 0.0, 0.0]
        self.head_command[:] = [0.0, 0.0, 0.0, 0.0]
        self.body_command[:] = [0.0] * 6
        self.sit_state = "up"
        self.rise_time_left_s = 0.0
        self.ground_pick_phase = 0.0
        self.timed_behavior = None
        self.timed_behavior_left_s = 0.0
        self.current_policy = self._idle_policy()
        self.reset_requested = True

    def consume_reset_request(self) -> bool:
        requested = self.reset_requested
        self.reset_requested = False
        return requested

    def set_velocity(self, vx: float, vy: float, yaw_rate: float) -> None:
        self.velocity_command[:] = _validate_vector(
            [vx, vy, yaw_rate], VELOCITY_COMMAND_LIMITS, "Velocity"
        )
        if (
            self.timed_behavior is None
            and self.current_policy != "ground_pick"
            and self.sit_state == "up"
        ):
            self.current_policy = self._automatic_locomotion_policy()

    def set_head(self, values: list[float] | tuple[float, ...]) -> None:
        self.head_command[:] = _validate_vector(values, HEAD_COMMAND_LIMITS, "Head")

    def set_body(self, values: list[float] | tuple[float, ...]) -> None:
        """Set `[x, y, z, roll, pitch, yaw]` body-pose command slots."""
        self.body_command[:] = _validate_vector(values, BODY_COMMAND_LIMITS, "Body")

    def bump_head(self, index: int, delta: float) -> None:
        if index not in range(4):
            raise IndexError(index)
        values = self.head_command.copy()
        values[index] += delta
        self.set_head(values)

    def clear_head(self) -> None:
        self.head_command[:] = [0.0, 0.0, 0.0, 0.0]

    def toggle_sitstand(self) -> bool:
        if "sitstand" not in self.available_policies:
            return False
        if self.timed_behavior is not None or self.current_policy == "ground_pick":
            return False
        if self.sit_state == "rising":
            return False
        self.velocity_command[:] = [0.0, 0.0, 0.0]
        if self.sit_state == "up":
            self.sit_state = "sitting"
        else:
            self.sit_state = "rising"
            self.rise_time_left_s = SITSTAND_RISE_SECONDS
        self.current_policy = "sitstand"
        return True

    def request_posture(self, posture: str) -> bool:
        """Request an explicit sit or stand posture without toggle ambiguity."""
        if "sitstand" not in self.available_policies:
            return False
        normalized = posture.strip().lower()
        if normalized == "sit":
            if self.sit_state == "sitting":
                return True
            if self.sit_state != "up":
                return False
            return self.toggle_sitstand()
        if normalized == "stand":
            if self.sit_state == "up":
                return True
            if self.sit_state != "sitting":
                return False
            return self.toggle_sitstand()
        raise ValueError(f"Unknown posture: {posture}")

    def trigger_ground_pick(self) -> bool:
        if "ground_pick" not in self.available_policies:
            return False
        if self.timed_behavior is not None or self.sit_state != "up":
            return False
        self.velocity_command[:] = [0.0, 0.0, 0.0]
        self.ground_pick_phase = 0.0
        self.current_policy = "ground_pick"
        return True

    def trigger_timed_behavior(self, name: str) -> bool:
        if name not in TIMED_BEHAVIOR_SECONDS:
            raise ValueError(f"Not a timed behavior: {name}")
        if name not in self.available_policies:
            return False
        if (
            self.timed_behavior is not None
            or self.current_policy == "ground_pick"
            or self.sit_state != "up"
        ):
            return False
        self.velocity_command[:] = [0.0, 0.0, 0.0]
        self.timed_behavior = name
        self.timed_behavior_left_s = TIMED_BEHAVIOR_SECONDS[name]
        self.current_policy = name
        return True

    def trigger(self, name: str) -> bool:
        """Handle a behavior name from the keyboard or ROS bridge."""
        normalized = name.strip().lower().replace("-", "_")
        if normalized in {"sitstand", "sit_toggle"}:
            return self.toggle_sitstand()
        if normalized in {"sit", "stand"}:
            return self.request_posture(normalized)
        if normalized in {"ground_pick", "pick"}:
            return self.trigger_ground_pick()
        if normalized in TIMED_BEHAVIOR_SECONDS:
            return self.trigger_timed_behavior(normalized)
        if normalized in {"walk", "walking", "locomotion"}:
            if self.timed_behavior is not None or self.current_policy == "ground_pick":
                return False
            if self.sit_state == "sitting":
                return self.request_posture("stand")
            if self.sit_state == "rising":
                return True
            self.current_policy = self._automatic_locomotion_policy()
            return True
        if normalized == "reset":
            self.reset()
            return True
        return False

    def update(self, dt: float) -> None:
        """Advance timed skills and return to locomotion when they finish."""
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        if self.timed_behavior is not None:
            self.timed_behavior_left_s -= dt
            if self.timed_behavior_left_s <= 0.0:
                self.timed_behavior = None
                self.timed_behavior_left_s = 0.0
                self.current_policy = self._automatic_locomotion_policy()
            return
        if self.current_policy == "ground_pick":
            self.ground_pick_phase += dt / self.ground_pick_period_s
            if self.ground_pick_phase >= GROUND_PICK_END_PHASE:
                self.ground_pick_phase = 0.0
                self.current_policy = self._automatic_locomotion_policy()
            return
        if self.sit_state == "rising":
            self.rise_time_left_s -= dt
            if self.rise_time_left_s <= 0.0:
                self.sit_state = "up"
                self.rise_time_left_s = 0.0
                self.current_policy = self._automatic_locomotion_policy()
                return
        if self.sit_state != "up":
            self.current_policy = "sitstand"
        else:
            self.current_policy = self._automatic_locomotion_policy()

    def action_scale(self) -> float:
        """Return the pinned runtime's action scale for the active policy."""
        if self.current_policy == "walking":
            return WALKING_ACTION_SCALE
        return SKILL_ACTION_SCALE

    def command(self) -> tuple[float, ...]:
        """Return `[twist(3), head_pose(4), body_pose(6)]`."""
        if self.timed_behavior is not None:
            return (0.0,) * COMMAND_SIZE
        if self.current_policy == "ground_pick":
            phase = 2.0 * math.pi * self.ground_pick_phase
            twist = (math.cos(phase), math.sin(phase), 0.0)
            return twist + (0.0,) * 10
        if self.current_policy == "sitstand":
            posture = 1.0 if self.sit_state == "sitting" else 0.0
            twist = (posture, 0.0, 0.0)
            return (*twist, *self.head_command, *self.body_command)
        if self.current_policy == "walking":
            return (*self.velocity_command, *self.head_command, *self.body_command)
        return (0.0, 0.0, 0.0, *self.head_command, *self.body_command)


def validate_policy_contract() -> None:
    """Fail early if a future edit breaks the shared runtime dimensions."""
    if len(POLICY_JOINTS) != ACTION_SIZE:
        raise AssertionError("Policy joint order must contain 14 joints")
    if len(HOME_POSE) != ACTION_SIZE:
        raise AssertionError("Home pose must contain 14 joint values")
    proprioception_size = 3 + 3 + ACTION_SIZE + ACTION_SIZE + ACTION_SIZE
    if proprioception_size + COMMAND_SIZE != OBSERVATION_SIZE:
        raise AssertionError("Observation contract must remain 61-dimensional")


validate_policy_contract()
