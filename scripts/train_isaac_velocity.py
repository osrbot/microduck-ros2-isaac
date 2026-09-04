#!/usr/bin/env python3
"""Train the native MicroDuck velocity task after starting Isaac Sim safely."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import time

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
DEFAULT_ROLL_POLICY = PROJECT_ROOT / "reference/microduck/policies/roulade.onnx"

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--num-envs", type=int, default=64)
parser.add_argument("--max-iterations", type=int, default=5)
parser.add_argument(
    "--profile",
    choices=("baseline", "aggressive", "continuous_roll"),
    default="baseline",
)
parser.add_argument("--log-root", type=Path, default=None)
parser.add_argument("--full-roll-v2", action="store_true")
parser.add_argument("--straight-roll", action="store_true")
parser.add_argument(
    "--init-policy-onnx",
    type=Path,
    default=DEFAULT_ROLL_POLICY,
    help="Actor ONNX used to warm-start the continuous-roll profile.",
)
parser.add_argument(
    "--resume-checkpoint",
    type=Path,
    default=None,
    help="Continue a continuous-roll run from an RSL-RL checkpoint.",
)
parser.add_argument("--completion-file", type=Path, default=None, help=argparse.SUPPRESS)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

if args_cli.num_envs <= 0:
    parser.error("--num-envs must be positive")
if args_cli.max_iterations <= 0:
    parser.error("--max-iterations must be positive")
if args_cli.straight_roll and not args_cli.full_roll_v2:
    parser.error("--straight-roll requires --full-roll-v2")

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


def warm_start_actor_from_onnx(runner, policy_path: Path, torch) -> dict[str, object]:
    """Load the released actor MLP and observation statistics into RSL-RL."""

    import onnx
    from onnx import numpy_helper

    policy_path = policy_path.expanduser().resolve()
    if not policy_path.is_file():
        raise FileNotFoundError(policy_path)
    model = onnx.load(str(policy_path))
    initializers = {
        item.name: numpy_helper.to_array(item) for item in model.graph.initializer
    }
    actor = runner.alg.actor
    state = actor.state_dict()
    copied: list[str] = []

    def copy_initializer(source_name: str, target_name: str) -> None:
        if source_name not in initializers:
            raise KeyError(f"ONNX initializer is missing: {source_name}")
        if target_name not in state:
            raise KeyError(f"RSL actor state is missing: {target_name}")
        value = torch.as_tensor(
            initializers[source_name].copy(), dtype=state[target_name].dtype
        ).reshape(state[target_name].shape)
        state[target_name] = value.to(device=state[target_name].device)
        copied.append(target_name)

    copy_initializer("obs_normalizer._mean", "obs_normalizer._mean")
    for layer in (0, 2, 4, 6):
        copy_initializer(f"mlp.{layer}.weight", f"mlp.{layer}.weight")
        copy_initializer(f"mlp.{layer}.bias", f"mlp.{layer}.bias")

    std_candidates = [
        name
        for name, value in initializers.items()
        if name.startswith("onnx::Div") and value.size == 61
    ]
    if len(std_candidates) != 1:
        raise RuntimeError(
            "Expected one 61D observation divisor in roll ONNX, found "
            f"{std_candidates}"
        )
    std = torch.as_tensor(
        initializers[std_candidates[0]].copy(),
        dtype=state["obs_normalizer._std"].dtype,
    ).reshape(state["obs_normalizer._std"].shape)
    std = std.clamp_min(1.0e-6).to(device=state["obs_normalizer._std"].device)
    state["obs_normalizer._std"] = std
    state["obs_normalizer._var"] = torch.square(std)
    state["obs_normalizer.count"] = torch.full_like(
        state["obs_normalizer.count"], 1_000_000.0
    )
    copied.extend(
        ["obs_normalizer._std", "obs_normalizer._var", "obs_normalizer.count"]
    )
    actor.load_state_dict(state)
    digest = hashlib.sha256(policy_path.read_bytes()).hexdigest()
    return {
        "path": str(policy_path),
        "sha256": digest,
        "copied_actor_state": copied,
        "observation_std_initializer": std_candidates[0],
    }


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
        MicroDuckAggressivePPORunnerCfg,
        MicroDuckContinuousRollPPORunnerCfg,
        MicroDuckVelocityPPORunnerCfg,
    )
    from microduck_isaac_lab.tasks.velocity.aggressive_env_cfg import (
        MicroDuckAggressiveVelocityEnvCfg,
    )
    from microduck_isaac_lab.tasks.velocity.continuous_roll_env_cfg import (
        MicroDuckContinuousRollEnvCfg,
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

    if args_cli.profile == "continuous_roll":
        task_id = "Isaac-MicroDuck-Continuous-Roll-v0"
        default_log_root = DEFAULT_CONTINUOUS_ROLL_LOG_ROOT
        env_cfg = MicroDuckContinuousRollEnvCfg()
        agent_cfg = MicroDuckContinuousRollPPORunnerCfg()
    elif args_cli.profile == "aggressive":
        task_id = "Isaac-MicroDuck-Velocity-Aggressive-v0"
        default_log_root = DEFAULT_AGGRESSIVE_LOG_ROOT
        env_cfg = MicroDuckAggressiveVelocityEnvCfg()
        agent_cfg = MicroDuckAggressivePPORunnerCfg()
    else:
        task_id = "Isaac-MicroDuck-Velocity-Flat-v0"
        default_log_root = DEFAULT_LOG_ROOT
        env_cfg = MicroDuckVelocityFlatEnvCfg()
        agent_cfg = MicroDuckVelocityPPORunnerCfg()
    agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_rsl_rl)
    if args_cli.full_roll_v2:
        if args_cli.profile != "continuous_roll":
            raise ValueError("--full-roll-v2 requires --profile continuous_roll")
        from microduck_isaac_lab.tasks.velocity.full_roll_env_cfg import FullRollEnvCfg
        env_cfg = FullRollEnvCfg()
        agent_cfg.clip_actions = None
        agent_cfg.save_interval = 100
        agent_cfg.algorithm.learning_rate = 1e-4
        agent_cfg.algorithm.desired_kl = 0.005
        if args_cli.straight_roll:
            from microduck_isaac_lab.tasks.velocity.full_roll_env_cfg import StraightFullRollEnvCfg
            env_cfg = StraightFullRollEnvCfg()
    env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.sim.device = args_cli.device
    env_cfg.seed = agent_cfg.seed
    agent_cfg.device = args_cli.device
    agent_cfg.max_iterations = args_cli.max_iterations

    log_root = (
        args_cli.log_root.expanduser().resolve()
        if args_cli.log_root is not None
        else default_log_root.resolve()
    )
    run_dir = log_root / datetime.now().strftime(
        "%Y-%m-%d_%H-%M-%S"
    )
    params_dir = run_dir / "params"
    params_dir.mkdir(parents=True, exist_ok=False)
    env_cfg.log_dir = str(run_dir)
    print(f"MICRODUCK_RUN_DIR={run_dir}")

    env = None
    warm_start = None
    resume = None
    started = time.monotonic()
    try:
        print("MICRODUCK_TRAIN_STAGE=creating_environment", flush=True)
        env = gym.make(task_id, cfg=env_cfg)
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
        if args_cli.profile == "continuous_roll" and args_cli.resume_checkpoint is not None:
            resume_checkpoint = args_cli.resume_checkpoint.expanduser().resolve()
            if not resume_checkpoint.is_file():
                raise FileNotFoundError(resume_checkpoint)
            print("MICRODUCK_TRAIN_STAGE=loading_resume_checkpoint", flush=True)
            runner.load(str(resume_checkpoint), map_location=agent_cfg.device)
            resume = {
                "path": str(resume_checkpoint),
                "sha256": hashlib.sha256(resume_checkpoint.read_bytes()).hexdigest(),
            }
            print(
                "MICRODUCK_ROLL_RESUME_SHA256=" + str(resume["sha256"]),
                flush=True,
            )
        elif args_cli.profile == "continuous_roll":
            print("MICRODUCK_TRAIN_STAGE=loading_roll_actor", flush=True)
            warm_start = warm_start_actor_from_onnx(
                runner, args_cli.init_policy_onnx, torch
            )
            print(
                "MICRODUCK_ROLL_WARM_START_SHA256=" + str(warm_start["sha256"]),
                flush=True,
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
            "task": task_id,
            "profile": args_cli.profile,
            "full_roll_v2": args_cli.full_roll_v2,
            "straight_roll": args_cli.straight_roll,
            "num_envs": args_cli.num_envs,
            "max_iterations": agent_cfg.max_iterations,
            "device": agent_cfg.device,
            "rsl_rl_version": installed_rsl_rl,
            "elapsed_s": elapsed_s,
            "checkpoint": str(final_checkpoint),
            "warm_start": warm_start,
            "resume": resume,
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
