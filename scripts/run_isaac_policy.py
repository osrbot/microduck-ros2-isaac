#!/usr/bin/env python3
"""Run an official MicroDuck ONNX policy against the converted Isaac asset."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import time

from isaaclab.app import AppLauncher


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_USD = (
    PROJECT_ROOT
    / "assets/isaac/robot_allcollisions/robot_allcollisions.usda"
)
DEFAULT_POLICY = PROJECT_ROOT / "reference/microduck/policies/alpha_walking.onnx"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/isaac/policy_rollout.json"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--usd", type=Path, default=DEFAULT_USD)
parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
parser.add_argument("--duration", type=float, default=5.0)
parser.add_argument("--vx", type=float, default=0.0)
parser.add_argument("--vy", type=float, default=0.0)
parser.add_argument("--yaw-rate", type=float, default=0.0)
parser.add_argument("--action-scale", type=float, default=1.0)
parser.add_argument("--stiffness", type=float, default=0.55)
parser.add_argument("--damping", type=float, default=0.053)
parser.add_argument("--effort-limit", type=float, default=0.96)
parser.add_argument(
    "--follow-camera",
    action="store_true",
    help="Keep the Kit viewport centered on the robot; use together with --viz kit.",
)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import numpy as np
import onnxruntime as ort
import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.sim import SimulationContext
from isaaclab.utils.math import quat_apply_inverse


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

PHYSICS_TIMESTEP_S = 0.005
CONTROL_DECIMATION = 4
CONTROL_HZ = 1.0 / (PHYSICS_TIMESTEP_S * CONTROL_DECIMATION)


def build_robot_cfg() -> ArticulationCfg:
    """Build the imported floating-base articulation with the MJCF actuator model."""
    return ArticulationCfg(
        prim_path="/World/MicroDuck",
        articulation_root_prim_path="/Geometry/trunk_base",
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(args_cli.usd.resolve()),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                max_depenetration_velocity=1.0,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=2,
            ),
        ),
        # trunk_base is authored at z=0.12 within the imported asset.  The
        # floating rigid-body pose is written explicitly after reset.
        init_state=ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, 0.005)),
        actuators={
            "policy_joints": ImplicitActuatorCfg(
                joint_names_expr=[".*"],
                effort_limit_sim=args_cli.effort_limit,
                velocity_limit_sim=6.0,
                stiffness=args_cli.stiffness,
                damping=args_cli.damping,
            )
        },
    )


def relative_path(path: Path) -> str:
    """Return a project-relative path where possible."""
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def open_policy(path: Path) -> tuple[ort.InferenceSession, str, str]:
    """Load the ONNX graph and enforce the upstream 61-to-14 contract."""
    session = ort.InferenceSession(
        str(path.resolve()), providers=["CPUExecutionProvider"]
    )
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    if len(inputs) != 1 or inputs[0].shape[-1] != 61:
        raise ValueError(f"Policy input is not obs[1,61]: {inputs}")
    if len(outputs) != 1 or outputs[0].shape[-1] != 14:
        raise ValueError(f"Policy output is not actions[1,14]: {outputs}")
    # Warm up before the timed control loop, matching the hardware runtime.
    zero_observation = np.zeros((1, 61), dtype=np.float32)
    session.run([outputs[0].name], {inputs[0].name: zero_observation})
    return session, inputs[0].name, outputs[0].name


def initialize_robot(
    robot: Articulation, sim: SimulationContext
) -> tuple[torch.Tensor, torch.Tensor]:
    """Write a known root pose and home joint state to PhysX."""
    joint_names = tuple(robot.joint_names)
    if set(joint_names) != set(POLICY_JOINTS):
        raise ValueError(
            f"Isaac joint names differ from policy contract: {joint_names}"
        )

    policy_to_isaac = torch.tensor(
        [joint_names.index(name) for name in POLICY_JOINTS],
        dtype=torch.long,
        device=sim.device,
    )
    home_policy = torch.tensor(
        [HOME_POSE], dtype=robot.data.joint_pos.torch.dtype, device=sim.device
    )
    home_isaac = torch.empty_like(home_policy)
    home_isaac[:, policy_to_isaac] = home_policy

    root_pose = robot.data.default_root_pose.torch.clone()
    root_pose[:, :3] = torch.tensor(
        [0.0, 0.0, 0.125], dtype=root_pose.dtype, device=sim.device
    )
    # Isaac Lab 3.0 pose tensors use quaternion order (x, y, z, w).
    root_pose[:, 3:] = torch.tensor(
        [0.0, 0.0, 0.0, 1.0], dtype=root_pose.dtype, device=sim.device
    )
    robot.write_root_pose_to_sim_index(root_pose=root_pose)
    robot.write_root_velocity_to_sim_index(
        root_velocity=torch.zeros_like(robot.data.default_root_vel.torch)
    )
    robot.write_joint_position_to_sim_index(position=home_isaac)
    robot.write_joint_velocity_to_sim_index(velocity=torch.zeros_like(home_isaac))
    robot.reset()
    return policy_to_isaac, home_policy


def main() -> int:
    """Run the policy rollout and write machine-readable evidence."""
    if args_cli.duration <= 0.0:
        raise ValueError("--duration must be positive")
    if not args_cli.usd.is_file():
        raise FileNotFoundError(args_cli.usd)
    if not args_cli.policy.is_file():
        raise FileNotFoundError(args_cli.policy)

    session, input_name, output_name = open_policy(args_cli.policy)
    sim_cfg = sim_utils.SimulationCfg(
        dt=PHYSICS_TIMESTEP_S,
        render_interval=CONTROL_DECIMATION,
        device=args_cli.device,
    )
    sim = SimulationContext(sim_cfg)
    ground_cfg = sim_utils.GroundPlaneCfg(
        physics_material=sim_utils.RigidBodyMaterialCfg(
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        )
    )
    ground_cfg.func("/World/Ground", ground_cfg)
    light_cfg = sim_utils.DomeLightCfg(
        intensity=2000.0, color=(0.75, 0.75, 0.75)
    )
    light_cfg.func("/World/Light", light_cfg)

    robot = Articulation(cfg=build_robot_cfg())
    sim.reset()
    robot.reset()
    policy_to_isaac, home_policy = initialize_robot(robot, sim)
    if args_cli.follow_camera:
        sim.set_camera_view(eye=(0.45, -0.45, 0.3), target=(0.0, 0.0, 0.11))

    command = torch.zeros((1, 13), dtype=torch.float32, device=sim.device)
    command[0, 0:3] = torch.tensor(
        [args_cli.vx, args_cli.vy, args_cli.yaw_rate],
        dtype=torch.float32,
        device=sim.device,
    )
    last_action = torch.zeros((1, 14), dtype=torch.float32, device=sim.device)
    gravity_world = torch.tensor(
        [[0.0, 0.0, -1.0]], dtype=torch.float32, device=sim.device
    )
    control_steps = round(args_cli.duration * CONTROL_HZ)

    trace: list[dict[str, float]] = []
    inference_times_ms: list[float] = []
    finite = True
    max_abs_action = 0.0
    rollout_started = time.perf_counter()
    progress_interval_steps = round(5.0 * CONTROL_HZ)

    for control_step in range(control_steps):
        root_quat = robot.data.root_quat_w.torch
        base_ang_vel = quat_apply_inverse(
            root_quat, robot.data.root_ang_vel_w.torch
        )
        projected_gravity = quat_apply_inverse(root_quat, gravity_world)
        joint_pos_policy = robot.data.joint_pos.torch[:, policy_to_isaac]
        joint_vel_policy = robot.data.joint_vel.torch[:, policy_to_isaac]
        observation = torch.cat(
            (
                base_ang_vel,
                projected_gravity,
                joint_pos_policy - home_policy,
                joint_vel_policy,
                last_action,
                command,
            ),
            dim=1,
        )
        if observation.shape != (1, 61) or not bool(
            torch.isfinite(observation).all()
        ):
            raise FloatingPointError(
                f"Invalid observation at control step {control_step}"
            )

        observation_np = observation.cpu().numpy().astype(np.float32, copy=False)
        started = time.perf_counter()
        action_np = session.run(
            [output_name], {input_name: observation_np}
        )[0]
        inference_times_ms.append((time.perf_counter() - started) * 1000.0)
        action = torch.as_tensor(
            action_np.reshape(1, 14), dtype=torch.float32, device=sim.device
        )
        if not bool(torch.isfinite(action).all()):
            raise FloatingPointError(
                f"Invalid policy output at control step {control_step}"
            )

        target_policy = home_policy + args_cli.action_scale * action
        target_isaac = torch.empty_like(target_policy)
        target_isaac[:, policy_to_isaac] = target_policy
        last_action = action
        max_abs_action = max(max_abs_action, float(torch.max(torch.abs(action)).item()))

        for _ in range(CONTROL_DECIMATION):
            robot.set_joint_position_target_index(target=target_isaac)
            robot.write_data_to_sim()
            sim.step()
            robot.update(sim.get_physics_dt())

        root_pos = robot.data.root_pos_w.torch
        root_quat = robot.data.root_quat_w.torch
        projected_gravity = quat_apply_inverse(root_quat, gravity_world)
        tilt = torch.acos(torch.clamp(-projected_gravity[:, 2], -1.0, 1.0))
        finite = finite and bool(
            torch.isfinite(root_pos).all()
            and torch.isfinite(root_quat).all()
            and torch.isfinite(robot.data.joint_pos.torch).all()
            and torch.isfinite(robot.data.joint_vel.torch).all()
        )
        trace.append(
            {
                "time_s": (control_step + 1) / CONTROL_HZ,
                "root_x_m": float(root_pos[0, 0].item()),
                "root_y_m": float(root_pos[0, 1].item()),
                "root_z_m": float(root_pos[0, 2].item()),
                "tilt_rad": float(tilt[0].item()),
                "max_abs_action": float(torch.max(torch.abs(action)).item()),
            }
        )
        if args_cli.follow_camera and control_step % 5 == 0:
            root_x = float(root_pos[0, 0].item())
            root_y = float(root_pos[0, 1].item())
            sim.set_camera_view(
                eye=(root_x + 0.45, root_y - 0.45, 0.3),
                target=(root_x, root_y, 0.11),
            )

        completed_steps = control_step + 1
        if (
            completed_steps % progress_interval_steps == 0
            or completed_steps == control_steps
        ):
            simulation_time_s = completed_steps / CONTROL_HZ
            elapsed_s = time.perf_counter() - rollout_started
            realtime_factor = simulation_time_s / max(elapsed_s, 1.0e-9)
            print(
                "Rollout progress: "
                f"sim={simulation_time_s:.1f}/{args_cli.duration:.1f}s, "
                f"wall={elapsed_s:.1f}s, realtime_factor={realtime_factor:.2f}",
                flush=True,
            )

    final = trace[-1]
    rollout_wall_time_s = time.perf_counter() - rollout_started
    summary = {
        "finite": finite,
        "upright_at_end": bool(
            finite and final["root_z_m"] > 0.08 and final["tilt_rad"] < 0.8
        ),
        "duration_s": args_cli.duration,
        "physics_timestep_s": PHYSICS_TIMESTEP_S,
        "control_hz": CONTROL_HZ,
        "decimation": CONTROL_DECIMATION,
        "command": command[0].cpu().tolist(),
        "action_scale": args_cli.action_scale,
        "start_root_z_m": 0.125,
        "final_root_xyz_m": [
            final["root_x_m"],
            final["root_y_m"],
            final["root_z_m"],
        ],
        "min_root_z_m": min(item["root_z_m"] for item in trace),
        "max_tilt_rad": max(item["tilt_rad"] for item in trace),
        "final_tilt_rad": final["tilt_rad"],
        "max_abs_action": max_abs_action,
        "inference_ms_mean": float(np.mean(inference_times_ms)),
        "inference_ms_max": float(np.max(inference_times_ms)),
        "rollout_wall_time_s": rollout_wall_time_s,
        "realtime_factor": args_cli.duration / rollout_wall_time_s,
    }
    report = {
        "usd": relative_path(args_cli.usd),
        "policy": relative_path(args_cli.policy),
        "device": str(sim.device),
        "onnxruntime_version": ort.__version__,
        "onnx_execution_provider": "CPUExecutionProvider",
        "follow_camera": args_cli.follow_camera,
        "policy_joint_order": list(POLICY_JOINTS),
        "isaac_joint_order": list(robot.joint_names),
        "actuator": {
            "stiffness_nm_per_rad": args_cli.stiffness,
            "damping_nm_s_per_rad": args_cli.damping,
            "effort_limit_nm": args_cli.effort_limit,
        },
        "summary": summary,
        "trace": trace,
    }
    args_cli.output.parent.mkdir(parents=True, exist_ok=True)
    args_cli.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Wrote {args_cli.output}")
    return 0 if summary["upright_at_end"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        simulation_app.close()
