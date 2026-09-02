"""Pure-Python command sequences for the ROS-to-Isaac examples."""

from __future__ import annotations

from dataclasses import dataclass
import math


VELOCITY_LIMITS = (0.4, 0.3, 1.0)
HEAD_LIMITS = (1.10, 1.10, 1.40, 0.31)
BEHAVIORS = frozenset(
    {
        "sit",
        "stand",
        "ground_pick",
        "kick_left",
        "kick_right",
        "roulade",
    }
)


@dataclass(frozen=True)
class DemoStep:
    """One visible stage in an Isaac showcase."""

    label: str
    duration_s: float
    velocity: tuple[float, float, float] = (0.0, 0.0, 0.0)
    head: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    behavior: str = ""
    reset: bool = False


RESET = DemoStep("reset the playground", 1.2, reset=True)
FINISH = DemoStep("back to the starting line", 1.2, reset=True)

WALK_SEQUENCE = (
    RESET,
    DemoStep("walk forward", 3.0, velocity=(0.30, 0.0, 0.0)),
    DemoStep("stop", 1.0),
    DemoStep("turn left", 2.5, velocity=(0.0, 0.0, 0.75)),
    DemoStep("stop", 1.0),
    DemoStep("sidestep right", 2.2, velocity=(0.0, -0.20, 0.0)),
    DemoStep("stop", 1.0),
    FINISH,
)

SKILL_SEQUENCE = (
    RESET,
    DemoStep("look left", 1.2, head=(0.10, -0.10, 0.75, 0.12)),
    DemoStep("look right", 1.5, head=(0.10, -0.10, -0.75, -0.12)),
    DemoStep("look ahead", 0.8),
    DemoStep("left kick", 1.8, behavior="kick_left"),
    DemoStep("right kick", 1.8, behavior="kick_right"),
    DemoStep("pick from the ground", 3.4, behavior="ground_pick"),
    DemoStep("sit down", 2.5, behavior="sit"),
    DemoStep("stand up", 2.0, behavior="stand"),
    DemoStep("forward roll", 2.2, behavior="roulade"),
    FINISH,
)

SHOWCASE_SEQUENCE = (
    RESET,
    DemoStep("say hello", 1.2, head=(0.10, -0.10, 0.75, 0.12)),
    DemoStep("look the other way", 1.4, head=(0.10, -0.10, -0.75, -0.12)),
    DemoStep("eyes front", 0.8),
    DemoStep("walk forward", 3.0, velocity=(0.30, 0.0, 0.0)),
    DemoStep("stop", 0.9),
    DemoStep("turn left", 2.4, velocity=(0.0, 0.0, 0.75)),
    DemoStep("stop", 0.9),
    DemoStep("left kick", 1.8, behavior="kick_left"),
    DemoStep("right kick", 1.8, behavior="kick_right"),
    DemoStep("pick from the ground", 3.4, behavior="ground_pick"),
    DemoStep("sit down", 2.5, behavior="sit"),
    DemoStep("stand up", 2.0, behavior="stand"),
    FINISH,
)

SEQUENCES = {
    "walk": WALK_SEQUENCE,
    "skills": SKILL_SEQUENCE,
    "showcase": SHOWCASE_SEQUENCE,
}


def sequence_duration(sequence_name: str) -> float:
    """Return a showcase duration in seconds."""

    try:
        return sum(step.duration_s for step in SEQUENCES[sequence_name])
    except KeyError as error:
        choices = ", ".join(sorted(SEQUENCES))
        raise ValueError(f"Unknown sequence {sequence_name!r}; choose {choices}") from error


def validate_sequences() -> None:
    """Validate all public example commands at import time."""

    for sequence_name, steps in SEQUENCES.items():
        if not steps or not steps[0].reset or not steps[-1].reset:
            raise ValueError(f"Sequence {sequence_name!r} must start and finish reset")
        for step in steps:
            values = (*step.velocity, *step.head, step.duration_s)
            if not all(math.isfinite(value) for value in values):
                raise ValueError(f"Sequence {sequence_name!r} contains non-finite data")
            if step.duration_s <= 0.0:
                raise ValueError(f"Sequence {sequence_name!r} has a zero-length step")
            if any(
                abs(value) > limit
                for value, limit in zip(step.velocity, VELOCITY_LIMITS, strict=True)
            ):
                raise ValueError(f"Sequence {sequence_name!r} exceeds velocity limits")
            if any(
                abs(value) > limit
                for value, limit in zip(step.head, HEAD_LIMITS, strict=True)
            ):
                raise ValueError(f"Sequence {sequence_name!r} exceeds head limits")
            if step.behavior and step.behavior not in BEHAVIORS:
                raise ValueError(f"Sequence {sequence_name!r} has an unknown behavior")


validate_sequences()
