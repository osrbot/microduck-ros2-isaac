"""Gym registration for the native MicroDuck velocity task."""

import gymnasium as gym

from . import agents


gym.register(
    id="Isaac-MicroDuck-Velocity-Flat-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.velocity_env_cfg:MicroDuckVelocityFlatEnvCfg",
        "rsl_rl_cfg_entry_point": (
            f"{agents.__name__}.rsl_rl_ppo_cfg:MicroDuckVelocityPPORunnerCfg"
        ),
    },
)

gym.register(
    id="Isaac-MicroDuck-Velocity-Aggressive-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": (
            f"{__name__}.aggressive_env_cfg:MicroDuckAggressiveVelocityEnvCfg"
        ),
        "rsl_rl_cfg_entry_point": (
            f"{agents.__name__}.rsl_rl_ppo_cfg:MicroDuckAggressivePPORunnerCfg"
        ),
    },
)

gym.register(
    id="Isaac-MicroDuck-Velocity-Aggressive-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": (
            f"{__name__}.aggressive_env_cfg:MicroDuckAggressiveVelocityEnvCfg_PLAY"
        ),
        "rsl_rl_cfg_entry_point": (
            f"{agents.__name__}.rsl_rl_ppo_cfg:MicroDuckAggressivePPORunnerCfg"
        ),
    },
)

gym.register(
    id="Isaac-MicroDuck-Velocity-Flat-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.velocity_env_cfg:MicroDuckVelocityFlatEnvCfg_PLAY",
        "rsl_rl_cfg_entry_point": (
            f"{agents.__name__}.rsl_rl_ppo_cfg:MicroDuckVelocityPPORunnerCfg"
        ),
    },
)

gym.register(
    id="Isaac-MicroDuck-Continuous-Roll-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": (
            f"{__name__}.continuous_roll_env_cfg:MicroDuckContinuousRollEnvCfg"
        ),
        "rsl_rl_cfg_entry_point": (
            f"{agents.__name__}.rsl_rl_ppo_cfg:MicroDuckContinuousRollPPORunnerCfg"
        ),
    },
)

gym.register(
    id="Isaac-MicroDuck-Continuous-Roll-Play-v0",
    entry_point="isaaclab.envs:ManagerBasedRLEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": (
            f"{__name__}.continuous_roll_env_cfg:MicroDuckContinuousRollEnvCfg_PLAY"
        ),
        "rsl_rl_cfg_entry_point": (
            f"{agents.__name__}.rsl_rl_ppo_cfg:MicroDuckContinuousRollPPORunnerCfg"
        ),
    },
)
