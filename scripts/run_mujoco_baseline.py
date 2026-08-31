#!/usr/bin/env python3
"""Run a deterministic, headless MicroDuck ONNX rollout in official MuJoCo."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import mujoco
import numpy as np
import onnxruntime as ort


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = PROJECT_ROOT / "reference"
DEFAULT_SCENE = (
    REFERENCE_ROOT / "microduck_rl/src/mjlab_microduck/robot/microduck/scene.xml"
)
DEFAULT_POLICY = REFERENCE_ROOT / "microduck/policies/alpha_walking.onnx"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/baseline/mujoco_rollout.json"

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

HOME_POSE = np.asarray(
    [
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
    ],
    dtype=np.float32,
)


def object_id(model: mujoco.MjModel, obj_type: mujoco.mjtObj, name: str) -> int:
    """Resolve a named MuJoCo object and fail with context when absent."""
    index = mujoco.mj_name2id(model, obj_type, name)
    if index < 0:
        raise ValueError(f"Missing MuJoCo object {name!r} ({obj_type})")
    return index


def quat_rotate_inverse(quat_wxyz: np.ndarray, vector: np.ndarray) -> np.ndarray:
    """Rotate a world-frame vector into the quaternion's local frame."""
    scalar = float(quat_wxyz[0])
    xyz = quat_wxyz[1:4]
    return (
        vector * (2.0 * scalar * scalar - 1.0)
        - 2.0 * scalar * np.cross(xyz, vector)
        + 2.0 * xyz * np.dot(xyz, vector)
    )


def parse_args() -> argparse.Namespace:
    """Parse rollout options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", type=Path, default=DEFAULT_SCENE)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--duration", type=float, default=5.0)
    parser.add_argument("--vx", type=float, default=0.0)
    parser.add_argument("--vy", type=float, default=0.0)
    parser.add_argument("--yaw-rate", type=float, default=0.0)
    parser.add_argument("--action-scale", type=float, default=1.0)
    parser.add_argument("--control-hz", type=float, default=50.0)
    parser.add_argument(
        "--simulation-timestep",
        type=float,
        default=0.005,
        help="MuJoCo physics timestep in seconds; 0.005 matches the official inference script.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def rollout(args: argparse.Namespace) -> dict[str, Any]:
    """Execute the rollout and return a compact trace and summary."""
    model = mujoco.MjModel.from_xml_path(str(args.scene.resolve()))
    model.opt.timestep = args.simulation_timestep
    data = mujoco.MjData(model)

    if model.nu != len(POLICY_JOINTS):
        raise ValueError(f"Expected 14 actuators, got {model.nu}")

    joint_ids = model.actuator_trnid[:, 0].astype(int)
    joint_names = tuple(
        mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, int(index))
        for index in joint_ids
    )
    if joint_names != POLICY_JOINTS:
        raise ValueError(
            "Actuator joint order differs from the policy contract:\n"
            f"expected={POLICY_JOINTS}\nactual={joint_names}"
        )

    qpos_indices = model.jnt_qposadr[joint_ids].astype(int)
    qvel_indices = model.jnt_dofadr[joint_ids].astype(int)
    root_joint_id = object_id(
        model, mujoco.mjtObj.mjOBJ_JOINT, "trunk_base_freejoint"
    )
    root_qpos = int(model.jnt_qposadr[root_joint_id])
    trunk_body_id = object_id(model, mujoco.mjtObj.mjOBJ_BODY, "trunk_base")
    gyro_id = object_id(model, mujoco.mjtObj.mjOBJ_SENSOR, "imu_ang_vel")
    gyro_address = int(model.sensor_adr[gyro_id])

    data.qpos[root_qpos : root_qpos + 3] = (0.0, 0.0, 0.125)
    data.qpos[root_qpos + 3 : root_qpos + 7] = (1.0, 0.0, 0.0, 0.0)
    data.qpos[qpos_indices] = HOME_POSE
    data.ctrl[:] = HOME_POSE
    mujoco.mj_forward(model, data)

    session = ort.InferenceSession(
        str(args.policy.resolve()), providers=["CPUExecutionProvider"]
    )
    if len(session.get_inputs()) != 1 or session.get_inputs()[0].shape[-1] != 61:
        raise ValueError(f"Policy input is not obs[1,61]: {session.get_inputs()}")
    if len(session.get_outputs()) != 1 or session.get_outputs()[0].shape[-1] != 14:
        raise ValueError(f"Policy output is not actions[1,14]: {session.get_outputs()}")
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    control_period = 1.0 / args.control_hz
    decimation = round(control_period / model.opt.timestep)
    if not math.isclose(
        decimation * model.opt.timestep, control_period, rel_tol=0.0, abs_tol=1e-9
    ):
        raise ValueError(
            f"Simulation timestep {model.opt.timestep} cannot produce {args.control_hz} Hz"
        )

    command = np.zeros(13, dtype=np.float32)
    command[0:3] = (args.vx, args.vy, args.yaw_rate)
    last_action = np.zeros(14, dtype=np.float32)
    gravity_world = np.asarray([0.0, 0.0, -1.0], dtype=np.float32)
    trace = []
    steps = round(args.duration * args.control_hz)

    for control_step in range(steps):
        gyro = data.sensordata[gyro_address : gyro_address + 3].astype(np.float32)
        quat = data.xquat[trunk_body_id].astype(np.float32)
        projected_gravity = quat_rotate_inverse(quat, gravity_world).astype(np.float32)
        joint_pos = data.qpos[qpos_indices].astype(np.float32) - HOME_POSE
        joint_vel = data.qvel[qvel_indices].astype(np.float32)
        observation = np.concatenate(
            (gyro, projected_gravity, joint_pos, joint_vel, last_action, command)
        ).astype(np.float32)
        if observation.shape != (61,) or not np.all(np.isfinite(observation)):
            raise FloatingPointError(
                f"Invalid observation at control step {control_step}: {observation}"
            )

        action = session.run(
            [output_name], {input_name: observation.reshape(1, 61)}
        )[0].reshape(14).astype(np.float32)
        if not np.all(np.isfinite(action)):
            raise FloatingPointError(
                f"Invalid policy output at control step {control_step}: {action}"
            )
        data.ctrl[:] = HOME_POSE + args.action_scale * action
        last_action = action

        for _ in range(decimation):
            mujoco.mj_step(model, data)

        quat = data.xquat[trunk_body_id].astype(np.float32)
        projected_gravity = quat_rotate_inverse(quat, gravity_world)
        tilt_rad = math.acos(float(np.clip(-projected_gravity[2], -1.0, 1.0)))
        trace.append(
            {
                "time_s": float(data.time),
                "root_x_m": float(data.qpos[root_qpos]),
                "root_y_m": float(data.qpos[root_qpos + 1]),
                "root_z_m": float(data.qpos[root_qpos + 2]),
                "tilt_rad": tilt_rad,
                "max_abs_action": float(np.max(np.abs(action))),
            }
        )

    finite = bool(
        np.all(np.isfinite(data.qpos))
        and np.all(np.isfinite(data.qvel))
        and all(math.isfinite(item["tilt_rad"]) for item in trace)
    )
    final = trace[-1]
    summary = {
        "finite": finite,
        "duration_s": args.duration,
        "control_hz": args.control_hz,
        "simulation_timestep_s": float(model.opt.timestep),
        "decimation": decimation,
        "command": command.tolist(),
        "action_scale": args.action_scale,
        "start_root_z_m": 0.125,
        "final_root_xyz_m": [
            final["root_x_m"],
            final["root_y_m"],
            final["root_z_m"],
        ],
        "min_root_z_m": min(item["root_z_m"] for item in trace),
        "max_tilt_rad": max(item["tilt_rad"] for item in trace),
        "final_tilt_rad": final["tilt_rad"],
    }
    summary["upright_at_end"] = bool(
        finite and final["root_z_m"] > 0.08 and final["tilt_rad"] < 0.8
    )
    return {
        "scene": str(args.scene.resolve().relative_to(PROJECT_ROOT)),
        "policy": str(args.policy.resolve().relative_to(PROJECT_ROOT)),
        "joint_order": list(POLICY_JOINTS),
        "summary": summary,
        "trace": trace,
    }


def main() -> int:
    """Run the requested baseline and write its evidence."""
    args = parse_args()
    if args.duration <= 0.0:
        raise ValueError("--duration must be positive")
    if args.simulation_timestep <= 0.0:
        raise ValueError("--simulation-timestep must be positive")
    report = rollout(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    print(f"Wrote {args.output}")
    return 0 if report["summary"]["upright_at_end"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
