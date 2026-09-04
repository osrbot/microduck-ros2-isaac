"""Forward-biased high-speed curriculum for the MicroDuck velocity task.

This profile stays separate from the conservative flat-velocity baseline.  It
trains running, fast turns, and recovery from stronger planar pushes.  Rolling
remains a separately validated skill policy; mixing a full somersault objective
into this locomotion reward would make both behaviors difficult to evaluate.
"""

from __future__ import annotations

import math

from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.configclass import configclass

import isaaclab_tasks.manager_based.locomotion.velocity.mdp as base_mdp

from ...contract import HEAD_INITIAL_RANGES
from . import mdp
from .velocity_env_cfg import (
    CommandsCfg,
    CurriculumCfg,
    EventsCfg,
    FEET_ASSET_CFG,
    HEAD_ASSET_CFG,
    LEG_ASSET_CFG,
    MicroDuckVelocityFlatEnvCfg,
    POLICY_ASSET_CFG,
    RewardsCfg,
)


@configclass
class AggressiveCommandsCfg(CommandsCfg):
    """Start learnable, then let the curriculum introduce sprint episodes."""

    base_velocity = mdp.TurnInPlaceVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(3.0, 6.0),
        rel_standing_envs=0.01,
        rel_heading_envs=0.0,
        heading_command=False,
        rel_turn_in_place_envs=0.15,
        turn_in_place_yaw_range=(0.5, 1.1),
        rel_sprint_envs=0.0,
        sprint_speed_range=(0.55, 0.70),
        sprint_lateral_range=(-0.12, 0.12),
        sprint_yaw_range=(-0.50, 0.50),
        sprint_reverse_fraction=0.05,
        debug_vis=False,
        ranges=base_mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(-0.35, 0.55),
            lin_vel_y=(-0.25, 0.25),
            ang_vel_z=(-0.9, 0.9),
        ),
    )


@configclass
class AggressiveEventsCfg(EventsCfg):
    """Use stronger but bounded pushes without changing actuator limits."""

    base_mass = EventTerm(
        func=base_mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="trunk_base"),
            "mass_distribution_params": (0.85, 1.15),
            "operation": "scale",
            "distribution": "uniform",
        },
    )
    push_robot = EventTerm(
        func=base_mdp.push_by_setting_velocity,
        mode="interval",
        interval_range_s=(4.0, 7.0),
        params={"velocity_range": {"x": (-0.45, 0.45), "y": (-0.45, 0.45)}},
    )


@configclass
class AggressiveRewardsCfg(RewardsCfg):
    """Prioritize speed tracking while retaining anti-jitter safety terms."""

    track_linear_velocity = RewTerm(
        func=base_mdp.track_lin_vel_xy_exp,
        weight=3.5,
        params={"command_name": "base_velocity", "std": math.sqrt(0.08)},
    )
    track_angular_velocity = RewTerm(
        func=base_mdp.track_ang_vel_z_exp,
        weight=1.75,
        params={"command_name": "base_velocity", "std": math.sqrt(0.4)},
    )
    head_pose_tracking = RewTerm(
        func=mdp.head_pose_tracking,
        weight=0.75,
        params={
            "command_name": "head_pose",
            "std": 0.55,
            "asset_cfg": HEAD_ASSET_CFG,
        },
    )
    home_pose = RewTerm(
        func=mdp.joint_pose_tracking,
        weight=1.0,
        params={"std": 0.60, "asset_cfg": LEG_ASSET_CFG},
    )
    flat_orientation = RewTerm(func=base_mdp.flat_orientation_l2, weight=-0.8)
    vertical_velocity = RewTerm(func=base_mdp.lin_vel_z_l2, weight=-0.35)
    body_angular_velocity = RewTerm(func=base_mdp.ang_vel_xy_l2, weight=-0.04)
    joint_acceleration = RewTerm(
        func=base_mdp.joint_acc_l2,
        weight=-1.0e-7,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )
    action_rate = RewTerm(func=base_mdp.action_rate_l2, weight=-0.03)
    joint_limits = RewTerm(
        func=base_mdp.joint_pos_limits,
        weight=-3.0,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )
    feet_air_time = RewTerm(
        func=mdp.split_feet_air_time_positive_biped,
        weight=4.0,
        params={
            "sensor_names": ("left_foot_contact", "right_foot_contact"),
            "command_name": "base_velocity",
            "threshold": 0.16,
        },
    )
    feet_flight_time = RewTerm(
        func=mdp.split_feet_flight_time_biped,
        weight=0.0,
        params={
            "sensor_names": ("left_foot_contact", "right_foot_contact"),
            "command_name": "base_velocity",
            "threshold": 0.08,
            "minimum_command_speed": 0.65,
        },
    )
    feet_slide = RewTerm(
        func=mdp.split_feet_slide,
        weight=-0.20,
        params={
            "sensor_names": ("left_foot_contact", "right_foot_contact"),
            "asset_cfg": FEET_ASSET_CFG,
        },
    )


@configclass
class AggressiveCurriculumCfg(CurriculumCfg):
    """Bootstrap standing, then widen speed and add short flight phases."""

    velocity_commands = CurrTerm(
        func=mdp.set_aggressive_velocity_command_schedule,
        params={
            "command_name": "base_velocity",
            "stages": (
                (0, (-0.35, 0.55), (-0.25, 0.25), (-0.9, 0.9), 0.00, (0.55, 0.70)),
                (500 * 32, (-0.45, 0.75), (-0.30, 0.30), (-1.2, 1.2), 0.10, (0.65, 0.85)),
                (1000 * 32, (-0.55, 1.00), (-0.40, 0.40), (-1.6, 1.6), 0.20, (0.80, 1.10)),
                (1800 * 32, (-0.65, 1.20), (-0.50, 0.50), (-2.0, 2.0), 0.30, (0.95, 1.30)),
                (3000 * 32, (-0.75, 1.35), (-0.55, 0.55), (-2.2, 2.2), 0.35, (1.05, 1.40)),
            ),
        },
    )
    home_pose = CurrTerm(
        func=mdp.set_reward_weight_schedule,
        params={
            "term_name": "home_pose",
            "stages": (
                (0, 1.0),
                (400 * 32, 0.75),
                (800 * 32, 0.55),
                (1500 * 32, 0.35),
            ),
        },
    )
    flight_time = CurrTerm(
        func=mdp.set_reward_weight_schedule,
        params={
            "term_name": "feet_flight_time",
            "stages": (
                (0, 0.0),
                (700 * 32, 0.15),
                (1200 * 32, 0.30),
                (2000 * 32, 0.45),
            ),
        },
    )
    action_rate = CurrTerm(
        func=mdp.set_reward_weight_schedule,
        params={
            "term_name": "action_rate",
            "stages": (
                (0, -0.03),
                (500 * 32, -0.06),
                (1000 * 32, -0.12),
                (1800 * 32, -0.20),
                (3000 * 32, -0.30),
            ),
        },
    )
    head_range = CurrTerm(
        func=mdp.set_vector_command_range_schedule,
        params={
            "command_name": "head_pose",
            "stages": (
                (0, HEAD_INITIAL_RANGES),
                (
                    900 * 32,
                    ((-0.12, 0.12), (-0.12, 0.12), (-0.18, 0.18), (-0.04, 0.04)),
                ),
                (
                    1800 * 32,
                    ((-0.25, 0.25), (-0.25, 0.25), (-0.35, 0.35), (-0.08, 0.08)),
                ),
            ),
        },
    )
    standing_fraction = CurrTerm(
        func=mdp.set_velocity_standing_fraction,
        params={
            "command_name": "base_velocity",
            "stages": (
                (0, 0.01),
                (800 * 32, 0.03),
                (1600 * 32, 0.05),
                (2600 * 32, 0.08),
            ),
        },
    )


@configclass
class MicroDuckAggressiveVelocityEnvCfg(MicroDuckVelocityFlatEnvCfg):
    """Training profile for fast locomotion and stronger recovery."""

    commands: AggressiveCommandsCfg = AggressiveCommandsCfg()
    rewards: AggressiveRewardsCfg = AggressiveRewardsCfg()
    events: AggressiveEventsCfg = AggressiveEventsCfg()
    curriculum: AggressiveCurriculumCfg = AggressiveCurriculumCfg()

    def __post_init__(self) -> None:
        super().__post_init__()
        self.episode_length_s = 16.0
        self.actions.joint_pos.scale = 1.05


@configclass
class MicroDuckAggressiveVelocityEnvCfg_PLAY(MicroDuckAggressiveVelocityEnvCfg):
    """Deterministic single-run configuration for visual evaluation."""

    def __post_init__(self) -> None:
        super().__post_init__()
        self.scene.num_envs = 4
        self.scene.env_spacing = 1.0
        self.observations.policy.enable_corruption = False
        self.commands.base_velocity.debug_vis = False
        self.events.base_mass = None
        self.events.push_robot = None
