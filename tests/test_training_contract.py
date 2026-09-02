"""Static contract checks for the external Isaac Lab task package."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    PROJECT_ROOT
    / "source/microduck_isaac_lab/microduck_isaac_lab/contract.py"
)
ENV_CFG_PATH = (
    PROJECT_ROOT
    / "source/microduck_isaac_lab/microduck_isaac_lab/tasks/velocity/velocity_env_cfg.py"
)
ASSET_CFG_PATH = (
    PROJECT_ROOT
    / "source/microduck_isaac_lab/microduck_isaac_lab/assets.py"
)
TRAIN_ENTRYPOINT_PATH = PROJECT_ROOT / "scripts/train_isaac_velocity.py"
TRAIN_WRAPPER_PATH = PROJECT_ROOT / "scripts/train_isaac_velocity.sh"
PLAY_ENTRYPOINT_PATH = PROJECT_ROOT / "scripts/play_isaac_velocity.py"
PLAY_WRAPPER_PATH = PROJECT_ROOT / "scripts/play_isaac_velocity.sh"
USD_POSTPROCESS_PATH = PROJECT_ROOT / "scripts/postprocess_isaac_usd.py"
ISAAC_WRAPPER_PATHS = (
    PROJECT_ROOT / "scripts/run_isaac_playground.sh",
    TRAIN_WRAPPER_PATH,
    PROJECT_ROOT / "scripts/play_isaac_velocity.sh",
)


def load_contract_module():
    spec = importlib.util.spec_from_file_location("microduck_training_contract", CONTRACT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {CONTRACT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TrainingContractTests(unittest.TestCase):
    def test_dimensions_and_joint_order(self) -> None:
        contract = load_contract_module()
        self.assertEqual(contract.ACTION_SIZE, 14)
        self.assertEqual(contract.COMMAND_SIZE, 13)
        self.assertEqual(contract.OBSERVATION_SIZE, 61)
        self.assertEqual(len(contract.POLICY_JOINTS), 14)
        self.assertEqual(len(contract.HOME_POSE), 14)

    def test_observation_terms_preserve_public_order(self) -> None:
        source = ENV_CFG_PATH.read_text(encoding="utf-8")
        terms = (
            "base_ang_vel",
            "projected_gravity",
            "joint_pos",
            "joint_vel",
            "actions",
            "velocity_command",
            "head_command",
            "body_command",
        )
        positions = [source.index(f"        {term} = ObsTerm") for term in terms]
        self.assertEqual(positions, sorted(positions))

    def test_task_ids_exist(self) -> None:
        registration = (ENV_CFG_PATH.parent / "__init__.py").read_text(encoding="utf-8")
        self.assertIn("Isaac-MicroDuck-Velocity-Flat-v0", registration)
        self.assertIn("Isaac-MicroDuck-Velocity-Flat-Play-v0", registration)

    def test_rsl_rl_observation_groups_are_explicit(self) -> None:
        agent_cfg = (
            ENV_CFG_PATH.parent / "agents/rsl_rl_ppo_cfg.py"
        ).read_text(encoding="utf-8")
        self.assertIn(
            'obs_groups = {"actor": ["policy"], "critic": ["policy"]}',
            agent_cfg,
        )

    def test_contact_sensor_uses_exact_pinned_physx_import(self) -> None:
        source = ENV_CFG_PATH.read_text(encoding="utf-8")
        self.assertIn("from isaaclab_physx.sensors import ContactSensorCfg", source)

    def test_nested_articulation_root_uses_backend_discovery(self) -> None:
        source = ASSET_CFG_PATH.read_text(encoding="utf-8")
        self.assertIn("articulation_root_prim_path=None", source)
        self.assertNotIn('articulation_root_prim_path="/Geometry/trunk_base"', source)

    def test_usd_postprocess_enables_nested_foot_contacts(self) -> None:
        source = USD_POSTPROCESS_PATH.read_text(encoding="utf-8")
        self.assertIn("NESTED_FOOT_CONTACT_PRIMS", source)
        self.assertIn('"ankle_left"', source)
        self.assertIn('"upper_leg_right/leg_2/ankle_right"', source)
        self.assertIn('prim.AddAppliedSchema("PhysxContactReportAPI")', source)
        self.assertIn('"all_nested_foot_contacts_enabled"', source)

    def test_velocity_config_imports_from_package_root(self) -> None:
        tree = ast.parse(ENV_CFG_PATH.read_text(encoding="utf-8"))
        relative_imports = {
            (node.module, node.level)
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.level
        }
        self.assertIn(("assets", 3), relative_imports)
        self.assertIn(("contract", 3), relative_imports)

    def test_training_starts_app_before_loading_task_modules(self) -> None:
        source = TRAIN_ENTRYPOINT_PATH.read_text(encoding="utf-8")
        app_start = source.index("app_launcher = AppLauncher(args_cli)")
        task_import = source.index("    import microduck_isaac_lab")
        self.assertLess(app_start, task_import)
        self.assertIn("handle_deprecated_rsl_rl_cfg", source)
        self.assertIn(
            "agent_cfg = handle_deprecated_rsl_rl_cfg(agent_cfg, installed_rsl_rl)",
            source,
        )
        self.assertIn("MICRODUCK_CONTACT_SENSOR=", source)
        self.assertNotIn("diagnostic-no-contact", source)
        self.assertIn("runner.learn(", source)
        self.assertIn('runner.save(str(final_checkpoint))', source)
        self.assertIn('args_cli.completion_file.write_text("complete\\n"', source)

        wrapper = TRAIN_WRAPPER_PATH.read_text(encoding="utf-8")
        self.assertIn('isaaclab.sh" -p "$project_dir/scripts/train_isaac_velocity.py"', wrapper)
        self.assertIn("microduck-training-complete", wrapper)
        self.assertIn('"$completion_state" != "complete"', wrapper)

    def test_playback_is_direct_validated_and_captures_evidence(self) -> None:
        source = PLAY_ENTRYPOINT_PATH.read_text(encoding="utf-8")
        app_start = source.index("app_launcher = AppLauncher(args_cli)")
        task_import = source.index("    import microduck_isaac_lab")
        self.assertLess(app_start, task_import)
        self.assertIn("handle_deprecated_rsl_rl_cfg", source)
        self.assertIn('glob("*/model_final.pt")', source)
        self.assertIn("runner.load(str(checkpoint)", source)
        self.assertIn("env_cfg.scene.playback_camera = CameraCfg", source)
        self.assertIn('playback_camera.data.output["rgb"]', source)
        self.assertIn("env_cfg.commands.base_velocity.debug_vis = False", source)
        self.assertNotIn("env.unwrapped.render(recompute=True)", source)
        self.assertIn("Image.fromarray", source)
        self.assertIn("traceback.print_exc()", source)
        self.assertIn("MICRODUCK_PLAYBACK_STAGE=complete", source)

        wrapper = PLAY_WRAPPER_PATH.read_text(encoding="utf-8")
        self.assertIn(
            'isaaclab.sh" -p "$project_dir/scripts/play_isaac_velocity.py"',
            wrapper,
        )
        self.assertIn("microduck-playback-complete", wrapper)
        self.assertIn("MICRODUCK_PLAY_TIMEOUT", wrapper)
        self.assertIn("timeout --signal=INT --kill-after=10s", wrapper)
        self.assertIn('"$completion_state" != "complete"', wrapper)

    def test_velocity_task_uses_nested_rig_gait_and_single_stage_curricula(self) -> None:
        source = ENV_CFG_PATH.read_text(encoding="utf-8")
        self.assertIn("left_foot_contact = ContactSensorCfg", source)
        self.assertIn("right_foot_contact = ContactSensorCfg", source)
        self.assertIn("func=mdp.split_feet_air_time_positive_biped", source)
        self.assertIn("func=mdp.split_feet_slide", source)
        self.assertIn("func=mdp.set_vector_command_range_schedule", source)
        self.assertIn("func=mdp.set_reward_weight_schedule", source)
        self.assertIn("base_velocity = mdp.TurnInPlaceVelocityCommandCfg", source)
        self.assertIn("rel_turn_in_place_envs=0.15", source)
        self.assertNotIn('prim_path="{ENV_REGEX_NS}/Robot/.*"', source)
        self.assertNotIn("trunk_contact = ContactSensorCfg", source)

    def test_isaac_wrappers_keep_crash_dumps_local(self) -> None:
        for wrapper_path in ISAAC_WRAPPER_PATHS:
            with self.subTest(wrapper=wrapper_path.name):
                source = wrapper_path.read_text(encoding="utf-8")
                self.assertIn("--/crashreporter/skipOldDumpUpload=1", source)
                self.assertIn("--/crashreporter/preserveDump=1", source)


if __name__ == "__main__":
    unittest.main()
