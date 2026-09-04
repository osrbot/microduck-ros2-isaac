#!/usr/bin/env python3
"""Replay a MicroDuck Isaac Lab checkpoint and save a compact run report."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata as metadata
import json
import math
from pathlib import Path
import shutil
import subprocess
import time
import traceback

from isaaclab.app import AppLauncher


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_ROOT = (
    PROJECT_ROOT / "work/isaac_training/logs/rsl_rl/microduck_velocity_flat"
)
DEFAULT_AGGRESSIVE_LOG_ROOT = (
    PROJECT_ROOT / "work/isaac_training/logs/rsl_rl/microduck_velocity_aggressive"
)
DEFAULT_CONTINUOUS_ROLL_LOG_ROOT = (
    PROJECT_ROOT / "work/isaac_training/logs/rsl_rl/microduck_continuous_roll"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/isaac/velocity_playback.json"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--checkpoint", type=Path, default=None)
parser.add_argument("--policy-onnx", type=Path, default=None)
parser.add_argument("--unclipped-actions", action="store_true")
parser.add_argument("--full-roll-v2", action="store_true")
parser.add_argument("--trace", type=Path, default=None)
parser.add_argument("--reset-root-height", type=float, default=None)
parser.add_argument("--arena-half-width", type=float, default=None)
parser.add_argument("--reset-perturbation", type=float, default=0.0)
parser.add_argument("--seed", type=int, default=None)
parser.add_argument("--num-envs", type=int, default=1)
parser.add_argument("--steps", type=int, default=200)
parser.add_argument(
    "--profile",
    choices=("baseline", "aggressive", "continuous_roll"),
    default="baseline",
)
parser.add_argument("--log-root", type=Path, default=None)
parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
parser.add_argument("--screenshot", type=Path, default=None)
parser.add_argument("--video", type=Path, default=None)
parser.add_argument("--video-fps", type=int, default=25)
parser.add_argument("--video-every", type=int, default=2)
parser.add_argument("--video-width", type=int, default=1920)
parser.add_argument("--video-height", type=int, default=1080)
parser.add_argument("--command-vx", type=float, default=None)
parser.add_argument("--command-vy", type=float, default=None)
parser.add_argument("--command-yaw", type=float, default=None)
parser.add_argument("--completion-file", type=Path, default=None, help=argparse.SUPPRESS)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

if args_cli.num_envs <= 0:
    parser.error("--num-envs must be positive")
if args_cli.policy_onnx is not None and args_cli.checkpoint is not None:
    parser.error("Choose either --policy-onnx or --checkpoint")
if args_cli.full_roll_v2 and args_cli.profile != "continuous_roll":
    parser.error("--full-roll-v2 requires --profile continuous_roll")
if args_cli.reset_root_height is not None and args_cli.reset_root_height <= 0:
    parser.error("--reset-root-height must be positive")
if args_cli.arena_half_width is not None and args_cli.arena_half_width <= 0:
    parser.error("--arena-half-width must be positive")
if args_cli.reset_perturbation < 0:
    parser.error("--reset-perturbation must be non-negative")
if args_cli.steps <= 0:
    parser.error("--steps must be positive")
if args_cli.video_fps <= 0:
    parser.error("--video-fps must be positive")
if args_cli.video_every <= 0:
    parser.error("--video-every must be positive")
if args_cli.video_width <= 0 or args_cli.video_height <= 0:
    parser.error("--video-width and --video-height must be positive")
if args_cli.screenshot is not None or args_cli.video is not None:
    args_cli.enable_cameras = True

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


def select_checkpoint() -> Path:
    """Return the requested checkpoint or the newest completed local run."""

    if args_cli.checkpoint is not None:
        checkpoint = args_cli.checkpoint.expanduser().resolve()
        if not checkpoint.is_file():
            raise FileNotFoundError(checkpoint)
        return checkpoint
    default_log_root = {
        "baseline": DEFAULT_LOG_ROOT,
        "aggressive": DEFAULT_AGGRESSIVE_LOG_ROOT,
        "continuous_roll": DEFAULT_CONTINUOUS_ROLL_LOG_ROOT,
    }[args_cli.profile]
    log_root = (
        args_cli.log_root.expanduser().resolve()
        if args_cli.log_root is not None
        else default_log_root.resolve()
    )
    candidates = list(log_root.glob("*/model_final.pt"))
    if not candidates:
        raise FileNotFoundError(
            f"No model_final.pt found below {log_root}. Run training first."
        )
    return max(candidates, key=lambda path: (path.stat().st_mtime_ns, str(path)))


def main() -> int:
    """Load one checkpoint, run deterministic inference, and save evidence."""

    import gymnasium as gym
    import numpy as np
    import torch
    from packaging import version
    from rsl_rl.runners import OnPolicyRunner

    from isaaclab_rl.rsl_rl import (
        RslRlVecEnvWrapper,
        handle_deprecated_rsl_rl_cfg,
    )

    import microduck_isaac_lab  # noqa: F401
    from microduck_isaac_lab.tasks.velocity.agents.rsl_rl_ppo_cfg import (
        MicroDuckAggressivePPORunnerCfg,
        MicroDuckContinuousRollPPORunnerCfg,
        MicroDuckVelocityPPORunnerCfg,
    )
    from microduck_isaac_lab.tasks.velocity.aggressive_env_cfg import (
        MicroDuckAggressiveVelocityEnvCfg_PLAY,
    )
    from microduck_isaac_lab.tasks.velocity.continuous_roll_env_cfg import (
        MicroDuckContinuousRollEnvCfg_PLAY,
    )
    from microduck_isaac_lab.tasks.velocity.velocity_env_cfg import (
        MicroDuckVelocityFlatEnvCfg_PLAY,
    )

    installed_rsl_rl = metadata.version("rsl-rl-lib")
    if version.parse(installed_rsl_rl) < version.parse("5.0.1"):
        raise RuntimeError(
            f"RSL-RL 5.0.1 or newer is required; found {installed_rsl_rl}"
        )

    checkpoint = args_cli.policy_onnx.resolve() if args_cli.policy_onnx else select_checkpoint()
    output = args_cli.output.expanduser().resolve()
    screenshot = (
        args_cli.screenshot.expanduser().resolve()
        if args_cli.screenshot is not None
        else None
    )

    if args_cli.profile == "continuous_roll":
        task_id = "Isaac-MicroDuck-Continuous-Roll-Play-v0"
        env_cfg = MicroDuckContinuousRollEnvCfg_PLAY()
        agent_cfg = MicroDuckContinuousRollPPORunnerCfg()
    elif args_cli.profile == "aggressive":
        task_id = "Isaac-MicroDuck-Velocity-Aggressive-Play-v0"
        env_cfg = MicroDuckAggressiveVelocityEnvCfg_PLAY()
        agent_cfg = MicroDuckAggressivePPORunnerCfg()
    else:
        task_id = "Isaac-MicroDuck-Velocity-Flat-Play-v0"
        env_cfg = MicroDuckVelocityFlatEnvCfg_PLAY()
        agent_cfg = MicroDuckVelocityPPORunnerCfg()
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_rsl_rl)
    if args_cli.full_roll_v2:
        from microduck_isaac_lab.tasks.velocity.full_roll_env_cfg import FullRollEnvCfg_PLAY
        env_cfg = FullRollEnvCfg_PLAY()
        agent_cfg.clip_actions = None
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.sim.device = args_cli.device
    env_cfg.seed = agent_cfg.seed
    if args_cli.seed is not None:
        env_cfg.seed = args_cli.seed
    env_cfg.commands.base_velocity.debug_vis = False
    if args_cli.reset_root_height is not None:
        offset_z = args_cli.reset_root_height - env_cfg.scene.robot.init_state.pos[2]
        env_cfg.events.reset_base.params["pose_range"]["z"] = (offset_z, offset_z)
    if args_cli.arena_half_width is not None:
        env_cfg.terminations.out_of_bounds.params["maximum_lateral_distance"] = args_cli.arena_half_width
    if args_cli.reset_perturbation > 0:
        variation = args_cli.reset_perturbation
        env_cfg.events.reset_base.params["pose_range"].update(
            roll=(-variation, variation), pitch=(-variation, variation), yaw=(-variation, variation)
        )
        env_cfg.events.reset_joints.params["position_range"] = (1 - variation * 0.1, 1 + variation * 0.1)
    env_cfg.viewer.eye = (0.55, -0.55, 0.32)
    env_cfg.viewer.lookat = (0.0, 0.0, 0.12)
    agent_cfg.device = args_cli.device
    if args_cli.unclipped_actions:
        agent_cfg.clip_actions = None
    control_dt_s = env_cfg.sim.dt * env_cfg.decimation
    video = (
        args_cli.video.expanduser().resolve()
        if args_cli.video is not None
        else None
    )
    if screenshot is not None or video is not None:
        import isaaclab.sim as sim_utils
        from isaaclab.sensors.camera import CameraCfg
        from isaaclab_physx.renderers import IsaacRtxRendererCfg

        env_cfg.scene.playback_camera = CameraCfg(
            prim_path="{ENV_REGEX_NS}/PlaybackCamera",
            update_period=0.0,
            height=args_cli.video_height,
            width=args_cli.video_width,
            data_types=["rgb"],
            renderer_cfg=IsaacRtxRendererCfg(),
            spawn=sim_utils.PinholeCameraCfg(
                focal_length=24.0,
                focus_distance=400.0,
                horizontal_aperture=20.955,
                clipping_range=(0.01, 100.0),
            ),
        )

    env = None
    video_process = None
    fixed_command = any(
        value is not None
        for value in (args_cli.command_vx, args_cli.command_vy, args_cli.command_yaw)
    )
    command = (
        float(args_cli.command_vx or 0.0),
        float(args_cli.command_vy or 0.0),
        float(args_cli.command_yaw or 0.0),
    )

    def camera_rgb(playback_camera):
        frame = playback_camera.data.output["rgb"]
        frame = getattr(frame, "torch", frame)[0]
        if hasattr(frame, "detach"):
            frame = frame.detach().cpu().numpy()
        if frame is None:
            raise RuntimeError("Isaac playback did not return an RGB frame")
        frame = np.asarray(frame)
        if frame.ndim != 3 or frame.shape[2] not in (3, 4):
            raise RuntimeError(
                f"Isaac playback did not return a valid RGB frame: {frame.shape}"
            )
        return np.ascontiguousarray(frame[:, :, :3], dtype=np.uint8)

    started = time.monotonic()
    try:
        print(f"MICRODUCK_PLAYBACK_CHECKPOINT={checkpoint}", flush=True)
        env = gym.make(
            task_id,
            cfg=env_cfg,
            render_mode=None,
        )
        playback_camera = None
        if screenshot is not None or video is not None:
            playback_camera = env.unwrapped.scene.sensors["playback_camera"]

        def update_camera_pose() -> None:
            if playback_camera is None:
                return
            root_position = (
                env.unwrapped.scene["robot"]
                .data.root_pos_w.torch[0]
                .detach()
                .cpu()
                .numpy()
            )
            playback_camera.set_world_poses_from_view(
                np.asarray(
                    [root_position + np.asarray([0.85, -0.85, 0.42])],
                    dtype=np.float32,
                ),
                np.asarray(
                    [root_position + np.asarray([0.0, 0.0, 0.10])],
                    dtype=np.float32,
                ),
            )

        update_camera_pose()
        for sensor_name, expected_body in (
            ("left_foot_contact", "ankle_left"),
            ("right_foot_contact", "ankle_right"),
        ):
            sensor = env.unwrapped.scene.sensors[sensor_name]
            if sensor.num_sensors != 1 or sensor.body_names != [expected_body]:
                raise RuntimeError(
                    f"{sensor_name} did not resolve exactly one {expected_body} body"
                )

        command_term = env.unwrapped.command_manager.get_term("base_velocity")

        def apply_fixed_command() -> None:
            if fixed_command:
                command_term.vel_command_b[:, 0] = command[0]
                command_term.vel_command_b[:, 1] = command[1]
                command_term.vel_command_b[:, 2] = command[2]

        apply_fixed_command()
        env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
        if args_cli.policy_onnx:
            import onnxruntime as ort
            session = ort.InferenceSession(str(checkpoint), providers=["CPUExecutionProvider"])

            def policy(observations):
                value = observations["policy"].detach().cpu().numpy()
                action = session.run(None, {session.get_inputs()[0].name: value})[0]
                return torch.as_tensor(action, device=agent_cfg.device)
        else:
            runner = OnPolicyRunner(
                env,
                agent_cfg.to_dict(),
                log_dir=None,
                device=agent_cfg.device,
            )
            runner.load(str(checkpoint), map_location=agent_cfg.device)
            policy = runner.get_inference_policy(device=agent_cfg.device)
        obs = env.get_observations()
        from microduck_isaac_lab.roll_metrics import ForwardTurnCounter
        turn_counter = ForwardTurnCounter(args_cli.num_envs, agent_cfg.device)
        turn_counter.update(env.unwrapped.scene["robot"].data.projected_gravity_b.torch)
        initial_root_height = env.unwrapped.scene["robot"].data.root_pos_w.torch[:, 2].cpu().tolist()
        trace_rows = []
        turn_completion_times = [[] for _ in range(args_cli.num_envs)]
        action_max = 0.0
        actions_above_one = 0

        video_frame_count = 0
        if video is not None:
            if playback_camera is None:
                raise RuntimeError("Playback camera was not created")
            ffmpeg = shutil.which("ffmpeg")
            if ffmpeg is None:
                raise RuntimeError("ffmpeg is required for playback video capture")
            video.parent.mkdir(parents=True, exist_ok=True)
            video_process = subprocess.Popen(
                [
                    ffmpeg,
                    "-nostdin",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-f",
                    "rawvideo",
                    "-pixel_format",
                    "rgb24",
                    "-video_size",
                    f"{args_cli.video_width}x{args_cli.video_height}",
                    "-framerate",
                    str(args_cli.video_fps),
                    "-i",
                    "-",
                    "-an",
                    "-c:v",
                    "h264_nvenc",
                    "-preset",
                    "p4",
                    "-tune",
                    "hq",
                    "-rc",
                    "vbr",
                    "-cq",
                    "20",
                    "-b:v",
                    "5M",
                    "-pix_fmt",
                    "yuv420p",
                    str(video),
                ],
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        reward_sum = 0.0
        done_count = 0
        min_root_height = math.inf
        max_root_height = -math.inf
        planar_speed_sum = 0.0
        max_planar_speed = 0.0
        positive_pitch_rotation = torch.zeros(
            args_cli.num_envs, dtype=torch.float32, device=agent_cfg.device
        )
        reverse_pitch_rotation = torch.zeros_like(positive_pitch_rotation)
        off_axis_rotation = torch.zeros_like(positive_pitch_rotation)
        initial_root_xy = (
            env.unwrapped.scene["robot"].data.root_pos_w.torch[:, :2].clone()
        )
        previous_root_xy = initial_root_xy.clone()
        accumulated_root_delta_xy = torch.zeros_like(initial_root_xy)
        with torch.inference_mode():
            for step in range(args_cli.steps):
                update_camera_pose()
                if fixed_command:
                    apply_fixed_command()
                    obs = env.get_observations()
                actions = policy(obs)
                action_max = max(action_max, float(actions.abs().max().item()))
                actions_above_one += int((actions.abs() > 1.0).sum().item())
                if not bool(torch.isfinite(actions).all()):
                    raise FloatingPointError(f"Non-finite action at step {step}")
                obs, rewards, dones, _ = env.step(actions)
                if not bool(torch.isfinite(rewards).all()):
                    raise FloatingPointError(f"Non-finite reward at step {step}")
                if not all(bool(torch.isfinite(value).all()) for value in obs.values()):
                    raise FloatingPointError(f"Non-finite observation at step {step}")
                reward_sum += float(rewards.sum().item())
                done_count += int(dones.sum().item())
                turn_counter.update(
                    env.unwrapped.scene["robot"].data.projected_gravity_b.torch,
                    dones.bool(),
                )
                if bool(turn_counter.new_turns.any()):
                    for env_index in torch.nonzero(turn_counter.new_turns).flatten().cpu().tolist():
                        turn_completion_times[env_index].append((step + 1) * control_dt_s)
                if args_cli.trace:
                    trace_rows.append({
                        "step": step,
                        "phase": turn_counter.phase.cpu().tolist(),
                        "net_phase": turn_counter.net.cpu().tolist(),
                        "turns": turn_counter.total_turns.cpu().tolist(),
                        "done": dones.cpu().tolist(),
                        "gravity_body": env.unwrapped.scene["robot"].data.projected_gravity_b.torch.cpu().tolist(),
                        "root_position": env.unwrapped.scene["robot"].data.root_pos_w.torch.cpu().tolist(),
                    })
                root_height = env.unwrapped.scene["robot"].data.root_pos_w.torch[:, 2]
                min_root_height = min(min_root_height, float(root_height.min().item()))
                max_root_height = max(max_root_height, float(root_height.max().item()))
                root_velocity = (
                    env.unwrapped.scene["robot"].data.root_lin_vel_b.torch[:, :2]
                )
                planar_speed = torch.linalg.norm(root_velocity, dim=1)
                planar_speed_sum += float(planar_speed.sum().item())
                max_planar_speed = max(
                    max_planar_speed, float(planar_speed.max().item())
                )
                angular_velocity = (
                    env.unwrapped.scene["robot"].data.root_ang_vel_b.torch
                )
                pitch_delta = angular_velocity[:, 1] * control_dt_s
                positive_pitch_rotation += torch.clamp(pitch_delta, min=0.0)
                reverse_pitch_rotation += torch.clamp(-pitch_delta, min=0.0)
                off_axis_rotation += torch.linalg.norm(
                    angular_velocity[:, (0, 2)], dim=1
                ) * control_dt_s
                current_root_xy = (
                    env.unwrapped.scene["robot"].data.root_pos_w.torch[:, :2]
                )
                step_delta_xy = current_root_xy - previous_root_xy
                valid_transition = ~dones.bool()
                accumulated_root_delta_xy[valid_transition] += step_delta_xy[
                    valid_transition
                ]
                previous_root_xy = current_root_xy.clone()
                if video_process is not None and step % args_cli.video_every == 0:
                    if video_process.stdin is None or playback_camera is None:
                        raise RuntimeError("Playback video encoder is unavailable")
                    video_process.stdin.write(camera_rgb(playback_camera).tobytes())
                    video_frame_count += 1

        final_root_xy = env.unwrapped.scene["robot"].data.root_pos_w.torch[:, :2]
        root_delta_xy = accumulated_root_delta_xy
        root_displacement = torch.linalg.norm(root_delta_xy, dim=1)
        mean_forward_rolls = float(
            (positive_pitch_rotation / (2.0 * math.pi)).mean().item()
        )
        mean_reverse_rolls = float(
            (reverse_pitch_rotation / (2.0 * math.pi)).mean().item()
        )

        video_info = None
        if video_process is not None:
            if video_process.stdin is None or video_process.stderr is None:
                raise RuntimeError("Playback video encoder pipes are unavailable")
            video_process.stdin.close()
            encoder_stderr = video_process.stderr.read().decode(
                "utf-8", errors="replace"
            )
            encoder_exit = video_process.wait()
            if encoder_exit != 0:
                raise RuntimeError(
                    f"Playback video encoder failed ({encoder_exit}): "
                    f"{encoder_stderr.strip()}"
                )
            if video is None or not video.is_file() or video.stat().st_size == 0:
                raise RuntimeError("Playback video was not created")
            video_info = {
                "path": str(video),
                "bytes": video.stat().st_size,
                "frames": video_frame_count,
                "fps": args_cli.video_fps,
                "duration_s": video_frame_count / args_cli.video_fps,
                "width": args_cli.video_width,
                "height": args_cli.video_height,
            }
            video_process = None

        print("MICRODUCK_PLAYBACK_STAGE=inference-complete", flush=True)
        screenshot_info = None
        if screenshot is not None:
            print("MICRODUCK_PLAYBACK_STAGE=screenshot-start", flush=True)
            if playback_camera is None:
                raise RuntimeError("Playback camera was not created")
            frame = camera_rgb(playback_camera)

            screenshot.parent.mkdir(parents=True, exist_ok=True)
            from PIL import Image

            Image.fromarray(frame, mode="RGB").save(screenshot)
            if not screenshot.is_file() or screenshot.stat().st_size == 0:
                raise RuntimeError(f"Screenshot was not created: {screenshot}")
            screenshot_info = {
                "path": str(screenshot),
                "bytes": screenshot.stat().st_size,
                "shape": list(frame.shape),
                "mean_pixel": float(np.asarray(frame).mean()),
            }
            print("MICRODUCK_PLAYBACK_STAGE=screenshot-complete", flush=True)

        elapsed_s = time.monotonic() - started
        maximum_turn_gaps = [
            max(b - a for a, b in zip([0.0] + times, times + [args_cli.steps * control_dt_s]))
            for times in turn_completion_times
        ]
        summary = {
            "task": task_id,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "checkpoint": str(checkpoint),
            "profile": args_cli.profile,
            "full_roll_v2": args_cli.full_roll_v2,
            "clip_actions": agent_cfg.clip_actions,
            "initial_root_height_m": initial_root_height,
            "reset_root_height_override_m": args_cli.reset_root_height,
            "arena_half_width_override_m": args_cli.arena_half_width,
            "reset_perturbation_rad": args_cli.reset_perturbation,
            "seed": env_cfg.seed,
            "policy_format": "onnx" if args_cli.policy_onnx else "rsl_rl",
            "maximum_raw_action": action_max,
            "raw_action_fraction_above_one": actions_above_one / (args_cli.steps * args_cli.num_envs * 14),
            "completed_forward_turns": turn_counter.total_turns.cpu().tolist(),
            "max_consecutive_forward_turns": turn_counter.max_consecutive.cpu().tolist(),
            "roll_acceptance_passed": bool((turn_counter.max_consecutive >= 3).all()) and done_count == 0,
            "turn_completion_times_s": turn_completion_times,
            "maximum_full_turn_gap_s_per_env": maximum_turn_gaps,
            "sustained_roll_passed": bool((turn_counter.max_consecutive >= 3).all()) and done_count == 0 and max(maximum_turn_gaps) <= 3.0,
            "num_envs": args_cli.num_envs,
            "steps": args_cli.steps,
            "command": command if fixed_command else None,
            "device": agent_cfg.device,
            "rsl_rl_version": installed_rsl_rl,
            "mean_reward_per_env_step": reward_sum
            / (args_cli.num_envs * args_cli.steps),
            "done_count": done_count,
            "min_root_height_m": min_root_height,
            "max_root_height_m": max_root_height,
            "mean_planar_speed_mps": planar_speed_sum
            / (args_cli.num_envs * args_cli.steps),
            "max_planar_speed_mps": max_planar_speed,
            "mean_root_displacement_m": float(root_displacement.mean().item()),
            "mean_forward_displacement_m": float(root_delta_xy[:, 0].mean().item()),
            "mean_lateral_displacement_m": float(root_delta_xy[:, 1].mean().item()),
            "forward_displacement_m_per_env": root_delta_xy[:, 0].cpu().tolist(),
            "lateral_displacement_m_per_env": root_delta_xy[:, 1].cpu().tolist(),
            "mean_abs_lateral_displacement_m": float(root_delta_xy[:, 1].abs().mean().item()),
            "max_abs_lateral_displacement_m": float(root_delta_xy[:, 1].abs().max().item()),
            "mean_forward_rolls": mean_forward_rolls,
            "mean_reverse_rolls": mean_reverse_rolls,
            "mean_off_axis_rotation_rad": float(off_axis_rotation.mean().item()),
            "forward_rotation_fraction": mean_forward_rolls
            / max(mean_forward_rolls + mean_reverse_rolls, 1.0e-9),
            "elapsed_s": elapsed_s,
            "screenshot": screenshot_info,
            "video": video_info,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        if args_cli.trace:
            args_cli.trace.parent.mkdir(parents=True, exist_ok=True)
            args_cli.trace.write_text(json.dumps(trace_rows) + "\n", encoding="utf-8")
        if args_cli.completion_file is not None:
            args_cli.completion_file.write_text("complete\n", encoding="utf-8")
        print(json.dumps(summary, indent=2), flush=True)
        print("MICRODUCK_PLAYBACK_STAGE=complete", flush=True)
        return 0
    finally:
        if video_process is not None:
            if video_process.stdin is not None and not video_process.stdin.closed:
                video_process.stdin.close()
            video_process.terminate()
            video_process.wait(timeout=10)
        if env is not None:
            env.close()


if __name__ == "__main__":
    exit_code = 0
    try:
        exit_code = main()
    except BaseException:  # Print the real failure before Kit tears down logging.
        traceback.print_exc()
        exit_code = 1
    finally:
        simulation_app.close()
    raise SystemExit(exit_code)
