"""Native Isaac Lab flat-ground velocity task for MicroDuck.

This first task is an Isaac-native teaching and experimentation environment.
It preserves the upstream 61D observation and 14D action contracts, but still
uses the repository's validated implicit-PD approximation rather than BAM.
Consequently, success here is not a sim2real claim.
"""

from __future__ import annotations

import math

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg, AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.managers import CurriculumTermCfg as CurrTerm
from isaaclab.managers import EventTermCfg as EventTerm
from isaaclab.managers import ObservationGroupCfg as ObsGroup
from isaaclab.managers import ObservationTermCfg as ObsTerm
from isaaclab.managers import RewardTermCfg as RewTerm
from isaaclab.managers import SceneEntityCfg
from isaaclab.managers import TerminationTermCfg as DoneTerm
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.utils.configclass import configclass
from isaaclab.utils.noise import UniformNoiseCfg as Unoise
from isaaclab_physx.sensors import ContactSensorCfg

import isaaclab_tasks.manager_based.locomotion.velocity.mdp as base_mdp

from ...assets import MICRODUCK_CFG
from ...contract import (
    BODY_COMMAND_RANGES,
    HEAD_INITIAL_RANGES,
    HEAD_JOINTS,
    POLICY_JOINTS,
)
from . import mdp


POLICY_ASSET_CFG = SceneEntityCfg(
    "robot", joint_names=list(POLICY_JOINTS), preserve_order=True
)
HEAD_ASSET_CFG = SceneEntityCfg(
    "robot", joint_names=list(HEAD_JOINTS), preserve_order=True
)
LEG_ASSET_CFG = SceneEntityCfg(
    "robot",
    joint_names=list(POLICY_JOINTS[:5] + POLICY_JOINTS[9:]),
    preserve_order=True,
)
FEET_ASSET_CFG = SceneEntityCfg(
    "robot", body_names=["ankle_left", "ankle_right"]
)


@configclass
class MicroDuckSceneCfg(InteractiveSceneCfg):
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=False,
    )
    robot: ArticulationCfg = MICRODUCK_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    # The converted MicroDuck USD keeps rigid bodies in a nested joint tree.
    # Separate exact foot sensors avoid the flat-body-path assumption used by
    # a single ``Robot/.*`` contact view in the pinned PhysX backend. A sensor
    # on the nested articulation root is deliberately omitted: this backend
    # expands it to ``trunk_base/trunk_base``. Root height and orientation
    # terms below still terminate falls deterministically.
    left_foot_contact = ContactSensorCfg(
        prim_path=(
            "{ENV_REGEX_NS}/Robot/Geometry/trunk_base/yaw2roll/hip_l/"
            "upper_leg_left/leg/ankle_left"
        ),
        history_length=3,
        track_air_time=True,
    )
    right_foot_contact = ContactSensorCfg(
        prim_path=(
            "{ENV_REGEX_NS}/Robot/Geometry/trunk_base/bearing_roll/hip_l_2/"
            "upper_leg_right/leg_2/ankle_right"
        ),
        history_length=3,
        track_air_time=True,
    )
    sky_light = AssetBaseCfg(
        prim_path="/World/skyLight",
        spawn=sim_utils.DomeLightCfg(intensity=1000.0, color=(0.85, 0.88, 1.0)),
    )


@configclass
class CommandsCfg:
    base_velocity = mdp.TurnInPlaceVelocityCommandCfg(
        asset_name="robot",
        resampling_time_range=(5.0, 8.0),
        rel_standing_envs=0.02,
        rel_heading_envs=0.0,
        heading_command=False,
        rel_turn_in_place_envs=0.15,
        turn_in_place_yaw_range=(0.4, 1.0),
        debug_vis=False,
        ranges=base_mdp.UniformVelocityCommandCfg.Ranges(
            lin_vel_x=(-0.4, 0.4),
            lin_vel_y=(-0.3, 0.3),
            ang_vel_z=(-1.0, 1.0),
        ),
    )
    head_pose = mdp.UniformVectorCommandCfg(
        resampling_time_range=(2.0, 5.0),
        ranges=HEAD_INITIAL_RANGES,
    )
    # Kept as a small randomized observation slot for 61D policy-family parity.
    # This first velocity task deliberately has no body-pose tracking reward.
    body_pose = mdp.UniformVectorCommandCfg(
        resampling_time_range=(2.0, 5.0),
        ranges=BODY_COMMAND_RANGES,
    )


@configclass
class ActionsCfg:
    joint_pos = base_mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=list(POLICY_JOINTS),
        scale=1.0,
        use_default_offset=True,
        preserve_order=True,
    )


@configclass
class ObservationsCfg:
    @configclass
    class PolicyCfg(ObsGroup):
        # Order is the public policy contract:
        # ang_vel(3), gravity(3), q(14), qd(14), last_action(14), commands(13).
        base_ang_vel = ObsTerm(
            func=base_mdp.base_ang_vel,
            noise=Unoise(n_min=-0.03, n_max=0.03),
        )
        projected_gravity = ObsTerm(
            func=base_mdp.projected_gravity,
            noise=Unoise(n_min=-0.01, n_max=0.01),
        )
        joint_pos = ObsTerm(
            func=base_mdp.joint_pos_rel,
            params={"asset_cfg": POLICY_ASSET_CFG},
            noise=Unoise(n_min=-0.001, n_max=0.001),
        )
        joint_vel = ObsTerm(
            func=base_mdp.joint_vel_rel,
            params={"asset_cfg": POLICY_ASSET_CFG},
            noise=Unoise(n_min=-0.25, n_max=0.25),
        )
        actions = ObsTerm(func=base_mdp.last_action)
        velocity_command = ObsTerm(
            func=base_mdp.generated_commands,
            params={"command_name": "base_velocity"},
        )
        head_command = ObsTerm(
            func=base_mdp.generated_commands,
            params={"command_name": "head_pose"},
        )
        body_command = ObsTerm(
            func=base_mdp.generated_commands,
            params={"command_name": "body_pose"},
        )

        def __post_init__(self) -> None:
            self.enable_corruption = True
            self.concatenate_terms = True

    policy: PolicyCfg = PolicyCfg()


@configclass
class EventsCfg:
    physics_material = EventTerm(
        func=base_mdp.randomize_rigid_body_material,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names=".*"),
            "static_friction_range": (0.8, 1.2),
            "dynamic_friction_range": (0.7, 1.1),
            "restitution_range": (0.0, 0.0),
            "num_buckets": 64,
        },
    )
    base_mass = EventTerm(
        func=base_mdp.randomize_rigid_body_mass,
        mode="startup",
        params={
            "asset_cfg": SceneEntityCfg("robot", body_names="trunk_base"),
            "mass_distribution_params": (0.9, 1.1),
            "operation": "scale",
            "distribution": "uniform",
        },
    )
    reset_base = EventTerm(
        func=base_mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-0.05, 0.05), "y": (-0.05, 0.05), "yaw": (-math.pi, math.pi)},
            "velocity_range": {
                "x": (-0.1, 0.1),
                "y": (-0.1, 0.1),
                "z": (-0.05, 0.05),
                "roll": (-0.1, 0.1),
                "pitch": (-0.1, 0.1),
                "yaw": (-0.1, 0.1),
            },
        },
    )
    reset_joints = EventTerm(
        func=base_mdp.reset_joints_by_scale,
        mode="reset",
        params={"position_range": (0.9, 1.1), "velocity_range": (0.0, 0.0)},
    )
    push_robot = EventTerm(
        func=base_mdp.push_by_setting_velocity,
        mode="interval",
        interval_range_s=(4.0, 7.0),
        params={"velocity_range": {"x": (-0.3, 0.3), "y": (-0.3, 0.3)}},
    )


@configclass
class RewardsCfg:
    track_linear_velocity = RewTerm(
        func=base_mdp.track_lin_vel_xy_exp,
        weight=2.0,
        params={"command_name": "base_velocity", "std": math.sqrt(0.1)},
    )
    track_angular_velocity = RewTerm(
        func=base_mdp.track_ang_vel_z_exp,
        weight=2.0,
        params={"command_name": "base_velocity", "std": math.sqrt(0.5)},
    )
    head_pose_tracking = RewTerm(
        func=mdp.head_pose_tracking,
        weight=2.0,
        params={"command_name": "head_pose", "std": 0.5, "asset_cfg": HEAD_ASSET_CFG},
    )
    home_pose = RewTerm(
        func=mdp.joint_pose_tracking,
        weight=1.0,
        params={"std": 0.45, "asset_cfg": LEG_ASSET_CFG},
    )
    flat_orientation = RewTerm(func=base_mdp.flat_orientation_l2, weight=-1.0)
    vertical_velocity = RewTerm(func=base_mdp.lin_vel_z_l2, weight=-1.0)
    body_angular_velocity = RewTerm(func=base_mdp.ang_vel_xy_l2, weight=-0.05)
    joint_torques = RewTerm(
        func=base_mdp.joint_torques_l2,
        weight=-1.0e-5,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )
    joint_acceleration = RewTerm(
        func=base_mdp.joint_acc_l2,
        weight=-2.5e-7,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )
    action_rate = RewTerm(func=base_mdp.action_rate_l2, weight=-0.1)
    joint_limits = RewTerm(
        func=base_mdp.joint_pos_limits,
        weight=-2.0,
        params={"asset_cfg": POLICY_ASSET_CFG},
    )
    feet_air_time = RewTerm(
        func=mdp.split_feet_air_time_positive_biped,
        weight=3.0,
        params={
            "sensor_names": ("left_foot_contact", "right_foot_contact"),
            "command_name": "base_velocity",
            "threshold": 0.125,
        },
    )
    feet_slide = RewTerm(
        func=mdp.split_feet_slide,
        weight=-0.1,
        params={
            "sensor_names": ("left_foot_contact", "right_foot_contact"),
            "asset_cfg": FEET_ASSET_CFG,
        },
    )


@configclass
class TerminationsCfg:
    time_out = DoneTerm(func=base_mdp.time_out, time_out=True)
    low_root = DoneTerm(
        func=base_mdp.root_height_below_minimum,
        params={"minimum_height": 0.06},
    )
    bad_orientation = DoneTerm(
        func=base_mdp.bad_orientation,
        params={"limit_angle": 1.0},
    )


@configclass
class CurriculumCfg:
    action_rate = CurrTerm(
        func=mdp.set_reward_weight_schedule,
        params={
            "term_name": "action_rate",
            "stages": (
                (0, -0.1),
                (500 * 24, -0.2),
                (750 * 24, -0.4),
                (1000 * 24, -0.6),
                (1250 * 24, -0.8),
                (1500 * 24, -1.0),
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
                    500 * 24,
                    ((-0.17, 0.17), (-0.17, 0.17), (-0.21, 0.21), (-0.047, 0.047)),
                ),
                (
                    1000 * 24,
                    ((-0.39, 0.39), (-0.39, 0.39), (-0.49, 0.49), (-0.11, 0.11)),
                ),
                (
                    1500 * 24,
                    ((-0.72, 0.72), (-0.72, 0.72), (-0.91, 0.91), (-0.20, 0.20)),
                ),
                (
                    2000 * 24,
                    ((-1.10, 1.10), (-1.10, 1.10), (-1.40, 1.40), (-0.31, 0.31)),
                ),
            ),
        },
    )
    standing_fraction = CurrTerm(
        func=mdp.set_velocity_standing_fraction,
        params={
            "command_name": "base_velocity",
            "stages": (
                (0, 0.02),
                (500 * 24, 0.05),
                (750 * 24, 0.10),
                (1000 * 24, 0.15),
                (1500 * 24, 0.20),
                (2000 * 24, 0.25),
            ),
        },
    )


@configclass
class MicroDuckVelocityFlatEnvCfg(ManagerBasedRLEnvCfg):
    sim: SimulationCfg = SimulationCfg()
    scene: MicroDuckSceneCfg = MicroDuckSceneCfg(num_envs=4096, env_spacing=1.0)
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    rewards: RewardsCfg = RewardsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    events: EventsCfg = EventsCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self) -> None:
        self.decimation = 4
        self.episode_length_s = 20.0
        self.sim.dt = 0.005
        self.sim.render_interval = self.decimation
        self.sim.physics_material = self.scene.terrain.physics_material
        self.scene.left_foot_contact.update_period = self.sim.dt
        self.scene.right_foot_contact.update_period = self.sim.dt


@configclass
class MicroDuckVelocityFlatEnvCfg_PLAY(MicroDuckVelocityFlatEnvCfg):
    def __post_init__(self) -> None:
        super().__post_init__()
        self.scene.num_envs = 4
        self.scene.env_spacing = 1.0
        self.observations.policy.enable_corruption = False
        self.commands.base_velocity.debug_vis = True
        self.events.base_mass = None
        self.events.push_robot = None
