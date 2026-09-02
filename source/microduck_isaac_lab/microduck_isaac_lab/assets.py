"""MicroDuck articulation configuration for the pinned Isaac Lab toolchain."""

from __future__ import annotations

import os
from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

from .contract import HOME_POSE, POLICY_JOINTS


PACKAGE_FILE = Path(__file__).resolve()
DEFAULT_PROJECT_ROOT = PACKAGE_FILE.parents[3]
PROJECT_ROOT = Path(os.environ.get("MICRODUCK_PROJECT_DIR", DEFAULT_PROJECT_ROOT)).resolve()
MICRODUCK_USD = PROJECT_ROOT / "assets/isaac/robot_allcollisions/robot_allcollisions.usda"

if not MICRODUCK_USD.is_file():
    raise FileNotFoundError(
        f"MicroDuck USD is unavailable at {MICRODUCK_USD}. "
        "Set MICRODUCK_PROJECT_DIR to the repository root."
    )


MICRODUCK_CFG = ArticulationCfg(
    # Leave the nested articulation root to backend discovery. With replicated
    # ManagerBased environments, the pinned PhysX backend otherwise appends
    # the explicit suffix twice and probes ``trunk_base/trunk_base``.
    articulation_root_prim_path=None,
    spawn=sim_utils.UsdFileCfg(
        usd_path=str(MICRODUCK_USD),
        activate_contact_sensors=True,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=20.0,
            max_angular_velocity=30.0,
            max_depenetration_velocity=1.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=2,
        ),
    ),
    # The imported stage authors trunk_base at z=0.12. This 5 mm stage offset
    # produces the validated 0.125 m initial root height.
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.005),
        joint_pos=dict(zip(POLICY_JOINTS, HOME_POSE, strict=True)),
        joint_vel={".*": 0.0},
    ),
    soft_joint_pos_limit_factor=0.9,
    actuators={
        "policy_joints": ImplicitActuatorCfg(
            joint_names_expr=list(POLICY_JOINTS),
            effort_limit_sim=0.96,
            velocity_limit_sim=6.0,
            stiffness=0.55,
            damping=0.053,
        )
    },
)
