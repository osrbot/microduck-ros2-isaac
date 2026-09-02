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
