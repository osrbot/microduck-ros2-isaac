"""Continuous forward-roll curriculum warm-started from the released skill.

The observation and action shapes stay identical to the existing 61D/14D
policy family.  Inversion and floor contact are part of this task, so its
termination and reward definitions are intentionally separate from walking.
"""

from __future__ import annotations

import math

from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.utils.configclass import configclass

import isaaclab_tasks.manager_based.locomotion.velocity.mdp as base_mdp

from . import mdp
from .velocity_env_cfg import (
    CommandsCfg,
    EventsCfg,
    MicroDuckVelocityFlatEnvCfg,
    POLICY_ASSET_CFG,
)


ZERO_HEAD_COMMAND = ((0.0, 0.0),) * 4
ZERO_BODY_COMMAND = ((0.0, 0.0),) * 6


@configclass
class ContinuousRollCommandsCfg(CommandsCfg):
    """Keep the shared command block at zero to match the roll skill input."""

    base_velocity = mdp.TurnInPlaceVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(12.0, 12.0),
        rel_standing_envs=0.0,
        rel_heading_envs=0.0,
        heading_command=False,
        rel_turn_in_place_envs=0.0,
        turn_in_place_yaw_range=(0.0, 0.0),
        rel_sprint_envs=0.0,
        sprint_speed_range=(0.0, 0.0),
        sprint_lateral_range=(0.0, 0.0),
        sprint_yaw_range=(0.0, 0.0),
        sprint_reverse_fraction=0.0,
        debug_vis=False,
        ranges=base_mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(0.0, 0.0),
            lin_vel_y=(0.0, 0.0),
            ang_vel_z=(0.0, 0.0),
        ),
    )
    head_pose = mdp.UniformVectorCommandCfg(
        resampling_time_range=(12.0, 12.0), ranges=ZERO_HEAD_COMMAND
    )
    body_pose = mdp.UniformVectorCommandCfg(
        resampling_time_range=(12.0, 12.0), ranges=ZERO_BODY_COMMAND
    )


@configclass
class ContinuousRollEventsCfg(EventsCfg):
    """Use small reset variations and bounded pushes for roll recovery."""

    base_mass = EventTerm(
        func=base_mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="trunk_base"),
            "mass_distribution_params": (0.95, 1.05),
            "operation": "scale",
            "distribution": "uniform",
        },
    )
    reset_base = EventTerm(
        func=base_mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {
                "x": (-0.02, 0.02),
                "y": (-0.02, 0.02),
                "roll": (-0.05, 0.05),
                "pitch": (-0.12, 0.12),
                "yaw": (-0.10, 0.10),
            },
            "velocity_range": {
                "x": (-0.04, 0.08),
                "y": (-0.03, 0.03),
                "z": (-0.02, 0.02),
                "roll": (-0.08, 0.08),
                "pitch": (0.0, 0.45),
                "yaw": (-0.08, 0.08),
            },
        },
    )
    reset_joints = EventTerm(
        func=base_mdp.reset_joints_by_scale,
        mode="reset",
        params={"position_range": (0.97, 1.03), "velocity_range": (-0.03, 0.03)},
    )
    push_robot = EventTerm(
        func=base_mdp.push_by_setting_velocity,
        mode="interval",
        interval_range_s=(5.0, 8.0),
        params={"velocity_range": {"x": (-0.08, 0.08), "y": (-0.08, 0.08)}},
    )


@configclass
class ContinuousRollRewardsCfg:
    """Reward repeatable forward rolls without rewarding airborne spinning."""

    roll_rate_tracking = RewTerm(
        func=mdp.forward_pitch_rate_tracking,
        weight=2.5,
        params={"target_rate": 3.6, "std": 2.0, "asset_cfg": POLICY_ASSET_CFG},
    )
    roll_progress = RewTerm(
        func=mdp.forward_pitch_rate_progress,
        weight=1.5,
        params={"target_rate": 3.6, "asset_cfg": POLICY_ASSET_CFG},
    )
    reverse_rotation = RewTerm(
        func=mdp.reverse_pitch_rate_l1,
        weight=-0.35,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )
    forward_velocity = RewTerm(
        func=mdp.forward_world_velocity_tracking,
        weight=1.0,
        params={"target_speed": 0.12, "std": 0.22, "asset_cfg": POLICY_ASSET_CFG},
    )
    floor_band = RewTerm(
        func=mdp.root_height_soft_band,
        weight=0.5,
        params={
            "minimum_height": 0.035,
            "maximum_height": 0.16,
            "std": 0.05,
            "asset_cfg": POLICY_ASSET_CFG,
        },
    )
    lateral_drift = RewTerm(
        func=mdp.lateral_world_velocity_l2,
        weight=-1.5,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )
    off_axis_rotation = RewTerm(
        func=mdp.off_axis_angular_velocity_l2,
        weight=-0.08,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )
    vertical_velocity = RewTerm(func=base_mdp.lin_vel_z_l2, weight=-0.02)
    joint_torques = RewTerm(
        func=base_mdp.joint_torques_l2,
        weight=-1.0e-5,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )
    joint_acceleration = RewTerm(
        func=base_mdp.joint_acc_l2,
        weight=-1.0e-7,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )
    action_rate = RewTerm(func=base_mdp.action_rate_l2, weight=-0.02)
    joint_limits = RewTerm(
        func=base_mdp.joint_pos_limits,
        weight=-3.0,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )


@configclass
class ContinuousRollTerminationsCfg:
    """Allow complete inversion and terminate only timeouts or runaway state."""

    time_out = DoneTerm(func=base_mdp.time_out, time_out=True)
    out_of_bounds = DoneTerm(
        func=mdp.root_state_out_of_bounds,
        params={
            "maximum_forward_distance": 12.0,
            "maximum_lateral_distance": 1.0,
            "maximum_height": 0.45,
            "asset_cfg": POLICY_ASSET_CFG,
        },
    )


@configclass
class ContinuousRollCurriculumCfg:
    """Grow from the released one-roll cadence into sustained fast rolling."""

    roll_tracking_target = CurrTerm(
        func=mdp.set_reward_float_param_schedule,
        params={
            "term_name": "roll_rate_tracking",
            "param_name": "target_rate",
            "stages": (
                (0, 3.6),
                (700 * 32, 4.3),
                (1600 * 32, 5.0),
                (3200 * 32, 5.8),
            ),
        },
    )
    roll_progress_target = CurrTerm(
        func=mdp.set_reward_float_param_schedule,
        params={
            "term_name": "roll_progress",
            "param_name": "target_rate",
            "stages": (
                (0, 3.6),
                (700 * 32, 4.3),
                (1600 * 32, 5.0),
                (3200 * 32, 5.8),
            ),
        },
    )
    forward_speed_target = CurrTerm(
        func=mdp.set_reward_float_param_schedule,
        params={
            "term_name": "forward_velocity",
            "param_name": "target_speed",
            "stages": (
                (0, 0.12),
                (900 * 32, 0.18),
                (2000 * 32, 0.24),
                (4000 * 32, 0.30),
            ),
        },
    )
    roll_progress_weight = CurrTerm(
        func=mdp.set_reward_weight_schedule,
        params={
            "term_name": "roll_progress",
            "stages": ((0, 1.5), (1200 * 32, 2.0), (3000 * 32, 2.5)),
        },
    )
    action_rate = CurrTerm(
        func=mdp.set_reward_weight_schedule,
        params={
            "term_name": "action_rate",
            "stages": ((0, -0.02), (1500 * 32, -0.04), (3500 * 32, -0.07)),
        },
    )


@configclass
class MicroDuckContinuousRollEnvCfg(MicroDuckVelocityFlatEnvCfg):
    """Long-episode training configuration for repeated forward rolls."""

    commands: ContinuousRollCommandsCfg = ContinuousRollCommandsCfg()
    rewards: ContinuousRollRewardsCfg = ContinuousRollRewardsCfg()
    events: ContinuousRollEventsCfg = ContinuousRollEventsCfg()
    terminations: ContinuousRollTerminationsCfg = ContinuousRollTerminationsCfg()
    curriculum: ContinuousRollCurriculumCfg = ContinuousRollCurriculumCfg()

    def __post_init__(self) -> None:
        super().__post_init__()
        self.episode_length_s = 30.0
        self.actions.joint_pos.scale = 1.0


@configclass
class MicroDuckContinuousRollEnvCfg_PLAY(MicroDuckContinuousRollEnvCfg):
    """Deterministic configuration for long roll-count evaluation."""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.episode_length_s = 60.0
        self.scene.num_envs = 1
        self.scene.env_spacing = 1.0
        self.observations.policy.enable_corruption = False
        self.events.physics_material = None
        self.events.base_mass = None
        self.events.push_robot = None
        self.events.reset_base.params["pose_range"] = {}
        self.events.reset_base.params["velocity_range"] = {}
        self.events.reset_joints.params["position_range"] = (1.0, 1.0)
        self.events.reset_joints.params["velocity_range"] = (0.0, 0.0)
        self.terminations.out_of_bounds.params["maximum_forward_distance"] = 25.0
