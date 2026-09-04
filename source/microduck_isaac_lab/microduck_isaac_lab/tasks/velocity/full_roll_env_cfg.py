"""Isolated V2 attempt: full orientation progress, with no +/-1 action crop.

The original continuous-roll configuration is preserved for reproducibility.
This profile first solves repetition without random pushes or speed demands.
"""

from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.utils.configclass import configclass
import isaaclab_tasks.manager_based.locomotion.velocity.mdp as base_mdp

from . import mdp
from .continuous_roll_env_cfg import MicroDuckContinuousRollEnvCfg
from .velocity_env_cfg import POLICY_ASSET_CFG


@configclass
class FullRollRewardsCfg:
    frontier = RewTerm(func=mdp.full_roll_frontier_progress, weight=8.0, params={"asset_cfg": POLICY_ASSET_CFG})
    full_turn = RewTerm(func=mdp.full_roll_completion, weight=6.0, params={"asset_cfg": POLICY_ASSET_CFG})
    reverse_rotation = RewTerm(func=mdp.reverse_pitch_rate_l1, weight=-0.05, params={"asset_cfg": POLICY_ASSET_CFG})
    flatness = RewTerm(func=mdp.roll_flatness_l2, weight=-0.5, params={"asset_cfg": POLICY_ASSET_CFG})
    off_axis_rotation = RewTerm(func=mdp.off_axis_angular_velocity_l2, weight=-0.01, params={"asset_cfg": POLICY_ASSET_CFG})
    lateral_drift = RewTerm(func=mdp.lateral_world_velocity_l2, weight=-0.2, params={"asset_cfg": POLICY_ASSET_CFG})
    action_rate = RewTerm(func=base_mdp.action_rate_l2, weight=-0.02)
    joint_limits = RewTerm(func=base_mdp.joint_pos_limits, weight=-0.1, params={"asset_cfg": POLICY_ASSET_CFG})
    joint_torques = RewTerm(func=base_mdp.joint_torques_l2, weight=-1e-5, params={"asset_cfg": POLICY_ASSET_CFG})


@configclass
class FullRollEnvCfg(MicroDuckContinuousRollEnvCfg):
    rewards: FullRollRewardsCfg = FullRollRewardsCfg()
    curriculum = None

    def __post_init__(self):
        super().__post_init__()
        self.episode_length_s = 12.0
        self.observations.policy.enable_corruption = False
        self.events.physics_material = None
        self.events.base_mass = None
        self.events.push_robot = None
        # The nested USD has a 0.12 m authored trunk offset. The reset API
        # uses cfg.init_state.pos (0.005 m), not that composed spawn pose.
        # Add the offset explicitly so resets start at 0.125 m, above ground.
        self.events.reset_base.params["pose_range"] = {"z": (0.12, 0.12), "pitch": (-0.05, 0.05)}
        self.events.reset_base.params["velocity_range"] = {}
        self.events.reset_joints.params["position_range"] = (0.995, 1.005)
        self.events.reset_joints.params["velocity_range"] = (0.0, 0.0)


@configclass
class FullRollEnvCfg_PLAY(FullRollEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.episode_length_s = 60.0
        self.events.reset_base.params["pose_range"] = {"z": (0.12, 0.12)}
        self.events.reset_joints.params["position_range"] = (1.0, 1.0)
        self.terminations.out_of_bounds.params["maximum_forward_distance"] = 25.0


@configclass
class StraightFullRollRewardsCfg(FullRollRewardsCfg):
    axis_alignment = RewTerm(func=mdp.roll_axis_alignment_error, weight=-3.0, params={"asset_cfg": POLICY_ASSET_CFG})
    lateral_drift = RewTerm(func=mdp.lateral_world_velocity_l2, weight=-3.0, params={"asset_cfg": POLICY_ASSET_CFG})
    off_axis_rotation = RewTerm(func=mdp.off_axis_angular_velocity_l2, weight=-0.03, params={"asset_cfg": POLICY_ASSET_CFG})


@configclass
class StraightFullRollEnvCfg(FullRollEnvCfg):
    rewards: StraightFullRollRewardsCfg = StraightFullRollRewardsCfg()
