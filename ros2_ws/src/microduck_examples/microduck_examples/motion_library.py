"""Pure-Python joint motion library used by the RViz example."""

from __future__ import annotations

from dataclasses import dataclass
import math


JOINT_NAMES = (
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

JOINT_LIMITS = (
    (-0.436332312999, 0.523598775598),
    (-0.383972435439, 0.383972435439),
    (-1.5707963268, 1.57079632679),
    (-1.5707963268, 1.57079632679),
    (-1.57079632679, 1.57079632679),
    (-1.57079632679, 1.0471975512),
    (-1.57079632679, 1.57079632679),
    (-2.96705972839, 2.96705972839),
    (-0.436332312999, 0.436332312999),
    (-0.523598775598, 0.436332312999),
    (-0.383972435439, 0.383972435439),
    (-1.57079632679, 1.57079632679),
    (-1.57079632679, 1.57079632679),
    (-1.57079632679, 1.57079632679),
)


def _pose(**changes: float) -> tuple[float, ...]:
    values = list(HOME_POSE)
    for joint_name, value in changes.items():
        values[JOINT_NAMES.index(joint_name)] = value
    return tuple(values)


POSES = {
    "home": HOME_POSE,
    "look_left": _pose(head_yaw=0.90, head_roll=0.12),
    "look_right": _pose(head_yaw=-0.90, head_roll=-0.12),
    "nod_down": _pose(neck_pitch=0.18, head_pitch=-0.32),
    "nod_up": _pose(neck_pitch=0.48, head_pitch=0.52),
    "step_left": _pose(
        left_hip_roll=-0.20,
        left_hip_pitch=-0.78,
        left_knee=-0.42,
        left_ankle=0.62,
        right_hip_roll=0.02,
    ),
    "step_right": _pose(
        right_hip_roll=0.20,
        right_hip_pitch=0.78,
        right_knee=0.42,
        right_ankle=-0.62,
        left_hip_roll=-0.02,
    ),
    "wide_stance": _pose(
        left_hip_roll=-0.23,
        right_hip_roll=0.23,
        left_knee=-0.18,
        right_knee=0.18,
    ),
    "bow": _pose(
        left_hip_pitch=-0.72,
        left_knee=-0.20,
        left_ankle=0.61,
        neck_pitch=0.05,
        head_pitch=-0.28,
        right_hip_pitch=0.72,
        right_knee=0.20,
        right_ankle=-0.61,
    ),
}


@dataclass(frozen=True)
class Keyframe:
    """A named pose reached over ``duration_s`` seconds."""

    label: str
    pose_name: str
    duration_s: float


ROUTINES = {
    "hello": (
        Keyframe("ready", "home", 0.6),
        Keyframe("look left", "look_left", 0.8),
        Keyframe("look right", "look_right", 1.1),
        Keyframe("nod", "nod_down", 0.6),
        Keyframe("look up", "nod_up", 0.6),
        Keyframe("hello complete", "home", 0.8),
    ),
    "walk": (
        Keyframe("ready", "wide_stance", 0.7),
        Keyframe("left step", "step_left", 0.7),
        Keyframe("right step", "step_right", 0.9),
        Keyframe("left step", "step_left", 0.9),
        Keyframe("right step", "step_right", 0.9),
        Keyframe("walk complete", "home", 0.8),
    ),
    "showcase": (
        Keyframe("ready", "home", 0.5),
        Keyframe("look left", "look_left", 0.7),
        Keyframe("look right", "look_right", 1.0),
        Keyframe("nod", "nod_down", 0.6),
        Keyframe("left step", "step_left", 0.8),
        Keyframe("right step", "step_right", 1.0),
        Keyframe("left step", "step_left", 1.0),
        Keyframe("wide stance", "wide_stance", 0.7),
        Keyframe("take a bow", "bow", 0.9),
        Keyframe("showcase complete", "home", 0.9),
    ),
}


def routine_duration(routine_name: str) -> float:
    """Return a routine's duration in seconds."""

    try:
        return sum(frame.duration_s for frame in ROUTINES[routine_name])
    except KeyError as error:
        choices = ", ".join(sorted(ROUTINES))
        raise ValueError(f"Unknown routine {routine_name!r}; choose {choices}") from error


def sample_routine(
    routine_name: str,
    elapsed_s: float,
    *,
    repeat: bool = False,
) -> tuple[tuple[float, ...], str, bool]:
    """Sample a smooth joint pose, label, and completion flag."""

    if not math.isfinite(elapsed_s) or elapsed_s < 0.0:
        raise ValueError("elapsed_s must be finite and non-negative")
    try:
        frames = ROUTINES[routine_name]
    except KeyError as error:
        choices = ", ".join(sorted(ROUTINES))
        raise ValueError(f"Unknown routine {routine_name!r}; choose {choices}") from error

    duration = routine_duration(routine_name)
    done = elapsed_s >= duration
    if repeat:
        elapsed_s %= duration
        done = False
    elif done:
        final = frames[-1]
        return POSES[final.pose_name], final.label, True

    previous_pose = HOME_POSE
    cursor = 0.0
    for frame in frames:
        frame_end = cursor + frame.duration_s
        if elapsed_s < frame_end:
            phase = (elapsed_s - cursor) / frame.duration_s
            eased = 0.5 - 0.5 * math.cos(math.pi * phase)
            target_pose = POSES[frame.pose_name]
            pose = tuple(
                start + (target - start) * eased
                for start, target in zip(previous_pose, target_pose, strict=True)
            )
            return pose, frame.label, done
        previous_pose = POSES[frame.pose_name]
        cursor = frame_end

    raise RuntimeError("Routine sampling fell outside the validated timeline")


def validate_motion_library() -> None:
    """Reject invalid example poses when the package is imported."""

    if len(JOINT_NAMES) != len(HOME_POSE) or len(JOINT_NAMES) != len(JOINT_LIMITS):
        raise ValueError("Joint names, home pose, and limits must have equal length")
    for pose_name, pose in POSES.items():
        if len(pose) != len(JOINT_NAMES):
            raise ValueError(f"Pose {pose_name!r} does not contain 14 joints")
        for joint_name, value, limits in zip(
            JOINT_NAMES, pose, JOINT_LIMITS, strict=True
        ):
            if not math.isfinite(value) or not limits[0] <= value <= limits[1]:
                raise ValueError(
                    f"Pose {pose_name!r} puts {joint_name} outside {limits}: {value}"
                )
    for routine_name, frames in ROUTINES.items():
        if not frames or frames[-1].pose_name != "home":
            raise ValueError(f"Routine {routine_name!r} must finish at home")
        for frame in frames:
            if frame.pose_name not in POSES or frame.duration_s <= 0.0:
                raise ValueError(f"Routine {routine_name!r} has an invalid keyframe")


validate_motion_library()
