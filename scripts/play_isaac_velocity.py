#!/usr/bin/env python3
"""Replay a MicroDuck Isaac Lab checkpoint and save a compact run report."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata as metadata
import json
import math
from pathlib import Path
import time
import traceback

from isaaclab.app import AppLauncher


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_ROOT = (
    PROJECT_ROOT / "work/isaac_training/logs/rsl_rl/microduck_velocity_flat"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/isaac/velocity_playback.json"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--checkpoint", type=Path, default=None)
parser.add_argument("--num-envs", type=int, default=1)
parser.add_argument("--steps", type=int, default=200)
parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
parser.add_argument("--screenshot", type=Path, default=None)
parser.add_argument("--completion-file", type=Path, default=None, help=argparse.SUPPRESS)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

if args_cli.num_envs <= 0:
    parser.error("--num-envs must be positive")
if args_cli.steps <= 0:
    parser.error("--steps must be positive")
if args_cli.screenshot is not None:
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
    candidates = list(args_cli.log_root.expanduser().resolve().glob("*/model_final.pt"))
    if not candidates:
        raise FileNotFoundError(
            f"No model_final.pt found below {args_cli.log_root}. Run training first."
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
        MicroDuckVelocityPPORunnerCfg,
    )
    from microduck_isaac_lab.tasks.velocity.velocity_env_cfg import (
        MicroDuckVelocityFlatEnvCfg_PLAY,
    )

    installed_rsl_rl = metadata.version("rsl-rl-lib")
    if version.parse(installed_rsl_rl) < version.parse("5.0.1"):
        raise RuntimeError(
            f"RSL-RL 5.0.1 or newer is required; found {installed_rsl_rl}"
        )

    checkpoint = select_checkpoint()
    output = args_cli.output.expanduser().resolve()
    screenshot = (
        args_cli.screenshot.expanduser().resolve()
        if args_cli.screenshot is not None
        else None
    )

    env_cfg = MicroDuckVelocityFlatEnvCfg_PLAY()
    agent_cfg = MicroDuckVelocityPPORunnerCfg()
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_rsl_rl)
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.sim.device = args_cli.device
    env_cfg.seed = agent_cfg.seed
    env_cfg.commands.base_velocity.debug_vis = False
    env_cfg.viewer.eye = (0.55, -0.55, 0.32)
    env_cfg.viewer.lookat = (0.0, 0.0, 0.12)
    agent_cfg.device = args_cli.device
    if screenshot is not None:
        import isaaclab.sim as sim_utils
        from isaaclab.sensors.camera import CameraCfg
        from isaaclab_physx.renderers import IsaacRtxRendererCfg

        env_cfg.scene.playback_camera = CameraCfg(
            prim_path="{ENV_REGEX_NS}/PlaybackCamera",
            update_period=0.0,
            height=720,
            width=960,
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
    started = time.monotonic()
    try:
        print(f"MICRODUCK_PLAYBACK_CHECKPOINT={checkpoint}", flush=True)
        env = gym.make(
            "Isaac-MicroDuck-Velocity-Flat-Play-v0",
            cfg=env_cfg,
            render_mode=None,
        )
        playback_camera = None
        if screenshot is not None:
            playback_camera = env.unwrapped.scene.sensors["playback_camera"]
            playback_camera.set_world_poses_from_view(
                np.asarray([[0.55, -0.55, 0.32]], dtype=np.float32),
                np.asarray([[0.0, 0.0, 0.12]], dtype=np.float32),
            )
        for sensor_name, expected_body in (
            ("left_foot_contact", "ankle_left"),
            ("right_foot_contact", "ankle_right"),
        ):
            sensor = env.unwrapped.scene.sensors[sensor_name]
            if sensor.num_sensors != 1 or sensor.body_names != [expected_body]:
                raise RuntimeError(
                    f"{sensor_name} did not resolve exactly one {expected_body} body"
                )

        env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
        runner = OnPolicyRunner(
            env,
            agent_cfg.to_dict(),
            log_dir=None,
            device=agent_cfg.device,
        )
        runner.load(str(checkpoint), map_location=agent_cfg.device)
        policy = runner.get_inference_policy(device=agent_cfg.device)
        obs = env.get_observations()

        reward_sum = 0.0
        done_count = 0
        min_root_height = math.inf
        max_root_height = -math.inf
        with torch.inference_mode():
            for step in range(args_cli.steps):
                actions = policy(obs)
                if not bool(torch.isfinite(actions).all()):
                    raise FloatingPointError(f"Non-finite action at step {step}")
                obs, rewards, dones, _ = env.step(actions)
                if not bool(torch.isfinite(rewards).all()):
                    raise FloatingPointError(f"Non-finite reward at step {step}")
                if not all(bool(torch.isfinite(value).all()) for value in obs.values()):
                    raise FloatingPointError(f"Non-finite observation at step {step}")
                reward_sum += float(rewards.sum().item())
                done_count += int(dones.sum().item())
                root_height = env.unwrapped.scene["robot"].data.root_pos_w.torch[:, 2]
                min_root_height = min(min_root_height, float(root_height.min().item()))
                max_root_height = max(max_root_height, float(root_height.max().item()))

        print("MICRODUCK_PLAYBACK_STAGE=inference-complete", flush=True)
        screenshot_info = None
        if screenshot is not None:
            print("MICRODUCK_PLAYBACK_STAGE=screenshot-start", flush=True)
            if playback_camera is None:
                raise RuntimeError("Playback camera was not created")
            frame = playback_camera.data.output["rgb"]
            frame = getattr(frame, "torch", frame)[0]
            if hasattr(frame, "detach"):
                frame = frame.detach().cpu().numpy()
            if frame is None:
                raise RuntimeError("Isaac playback did not return an RGB frame")
            frame = np.asarray(frame)
            if frame.ndim != 3 or frame.shape[2] not in (3, 4):
                raise RuntimeError(
                    f"Isaac playback did not return a valid RGB frame: "
                    f"{frame.shape}"
                )

            screenshot.parent.mkdir(parents=True, exist_ok=True)
            from PIL import Image

            image_mode = "RGBA" if frame.shape[2] == 4 else "RGB"
            Image.fromarray(frame, mode=image_mode).save(screenshot)
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
        summary = {
            "task": "Isaac-MicroDuck-Velocity-Flat-Play-v0",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "checkpoint": str(checkpoint),
            "num_envs": args_cli.num_envs,
            "steps": args_cli.steps,
            "device": agent_cfg.device,
            "rsl_rl_version": installed_rsl_rl,
            "mean_reward_per_env_step": reward_sum
            / (args_cli.num_envs * args_cli.steps),
            "done_count": done_count,
            "min_root_height_m": min_root_height,
            "max_root_height_m": max_root_height,
            "elapsed_s": elapsed_s,
            "screenshot": screenshot_info,
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        if args_cli.completion_file is not None:
            args_cli.completion_file.write_text("complete\n", encoding="utf-8")
        print(json.dumps(summary, indent=2), flush=True)
        print("MICRODUCK_PLAYBACK_STAGE=complete", flush=True)
        return 0
    finally:
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
