#!/usr/bin/env python3
"""Train the native MicroDuck velocity task after starting Isaac Sim safely."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import time

from isaaclab.app import AppLauncher


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_ROOT = (
    PROJECT_ROOT / "work/isaac_training/logs/rsl_rl/microduck_velocity_flat"
)

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--num-envs", type=int, default=64)
parser.add_argument("--max-iterations", type=int, default=5)
parser.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
parser.add_argument("--completion-file", type=Path, default=None, help=argparse.SUPPRESS)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

if args_cli.num_envs <= 0:
    parser.error("--num-envs must be positive")
if args_cli.max_iterations <= 0:
    parser.error("--max-iterations must be positive")

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


def main() -> int:
    """Build the task directly and run RSL-RL without preloading Kit modules."""

    import importlib.metadata as metadata

    import gymnasium as gym
    import torch
    from packaging import version
    from rsl_rl.runners import OnPolicyRunner

    from isaaclab.utils.io import dump_yaml
    from isaaclab_rl.rsl_rl import (
        RslRlVecEnvWrapper,
        handle_deprecated_rsl_rl_cfg,
    )

    import microduck_isaac_lab  # noqa: F401
    from microduck_isaac_lab.tasks.velocity.agents.rsl_rl_ppo_cfg import (
        MicroDuckVelocityPPORunnerCfg,
    )
    from microduck_isaac_lab.tasks.velocity.velocity_env_cfg import (
        MicroDuckVelocityFlatEnvCfg,
    )

    installed_rsl_rl = metadata.version("rsl-rl-lib")
    if version.parse(installed_rsl_rl) < version.parse("5.0.1"):
        raise RuntimeError(
            f"RSL-RL 5.0.1 or newer is required; found {installed_rsl_rl}"
        )

    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = False

    env_cfg = MicroDuckVelocityFlatEnvCfg()
    agent_cfg = MicroDuckVelocityPPORunnerCfg()
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_rsl_rl)
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.sim.device = args_cli.device
    env_cfg.seed = agent_cfg.seed
    agent_cfg.device = args_cli.device
    agent_cfg.max_iterations = args_cli.max_iterations

    run_dir = args_cli.log_root.resolve() / datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )
    params_dir = run_dir / "params"
    params_dir.mkdir(parents=True, exist_ok=False)
    env_cfg.log_dir = str(run_dir)
    print(f"MICRODUCK_RUN_DIR={run_dir}")

    env = None
    started = time.monotonic()
    try:
        print("MICRODUCK_TRAIN_STAGE=creating_environment", flush=True)
        env = gym.make("Isaac-MicroDuck-Velocity-Flat-v0", cfg=env_cfg)
        for sensor_name, expected_body in (
            ("left_foot_contact", "ankle_left"),
            ("right_foot_contact", "ankle_right"),
        ):
            sensor = env.unwrapped.scene.sensors[sensor_name]
            body_names = sensor.body_names
            if sensor.num_sensors != 1 or body_names != [expected_body]:
                raise RuntimeError(
                    f"{sensor_name} resolved {sensor.num_sensors} bodies: "
                    f"{body_names}; expected [{expected_body!r}]"
                )
            print(
                "MICRODUCK_CONTACT_SENSOR="
                f"{sensor_name}:{sensor.num_sensors}:{body_names[0]}",
                flush=True,
            )
        print("MICRODUCK_TRAIN_STAGE=wrapping_environment", flush=True)
        env = RslRlVecEnvWrapper(env, clip_actions=agent_cfg.clip_actions)
        print("MICRODUCK_TRAIN_STAGE=creating_runner", flush=True)
        runner = OnPolicyRunner(
            env,
            agent_cfg.to_dict(),
            log_dir=str(run_dir),
            device=agent_cfg.device,
        )
        print("MICRODUCK_TRAIN_STAGE=learning", flush=True)
        dump_yaml(str(params_dir / "env.yaml"), env_cfg)
        dump_yaml(str(params_dir / "agent.yaml"), agent_cfg)
        runner.learn(
            num_learning_iterations=agent_cfg.max_iterations,
            init_at_random_ep_len=True,
        )
        print("MICRODUCK_TRAIN_STAGE=saving", flush=True)
        final_checkpoint = run_dir / "model_final.pt"
        runner.save(str(final_checkpoint))
        elapsed_s = time.monotonic() - started
        summary = {
            "task": "Isaac-MicroDuck-Velocity-Flat-v0",
            "num_envs": args_cli.num_envs,
            "max_iterations": agent_cfg.max_iterations,
            "device": agent_cfg.device,
            "rsl_rl_version": installed_rsl_rl,
            "elapsed_s": elapsed_s,
            "checkpoint": str(final_checkpoint),
        }
        (run_dir / "training_summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
        if args_cli.completion_file is not None:
            args_cli.completion_file.write_text("complete\n", encoding="utf-8")
        print(json.dumps(summary, indent=2))
        print("MICRODUCK_TRAIN_STAGE=complete", flush=True)
        return 0
    finally:
        if env is not None:
            env.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        simulation_app.close()
