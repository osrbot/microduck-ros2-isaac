#!/usr/bin/env python3
"""Play released MicroDuck skills interactively in Isaac Sim."""

from __future__ import annotations

import argparse
from collections import deque
import json
import math
from pathlib import Path
import socket
import time
from typing import NamedTuple

from isaaclab.app import AppLauncher

from microduck_playground_core import (
    ACTION_SIZE,
    HOME_POSE,
    OBSERVATION_SIZE,
    POLICY_JOINTS,
    PlaygroundController,
    validate_udp_command,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_USD = PROJECT_ROOT / "assets/isaac/robot_allcollisions/robot_allcollisions.usda"
DEFAULT_POLICY_DIR = PROJECT_ROOT / "reference/microduck/policies"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/isaac/playground_session.json"

PHYSICS_TIMESTEP_S = 0.005
CONTROL_DECIMATION = 4
CONTROL_HZ = 1.0 / (PHYSICS_TIMESTEP_S * CONTROL_DECIMATION)
BALL_OFFSET_X = 0.09
BALL_OFFSET_ABS_Y = 0.042
BALL_RADIUS_M = 0.035


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--usd", type=Path, default=DEFAULT_USD)
parser.add_argument(
    "--walking-policy", type=Path, default=DEFAULT_POLICY_DIR / "alpha_walking.onnx"
)
parser.add_argument(
    "--standing-policy", type=Path, default=DEFAULT_POLICY_DIR / "alpha_stand.onnx"
)
parser.add_argument(
    "--sitstand-policy", type=Path, default=DEFAULT_POLICY_DIR / "alpha_sitstand.onnx"
)
parser.add_argument(
    "--ground-pick-policy",
    type=Path,
    default=DEFAULT_POLICY_DIR / "alpha_ground_pick.onnx",
)
parser.add_argument(
    "--kick-left-policy", type=Path, default=DEFAULT_POLICY_DIR / "ball_kick_left.onnx"
)
parser.add_argument(
    "--kick-right-policy", type=Path, default=DEFAULT_POLICY_DIR / "ball_kick_right.onnx"
)
parser.add_argument("--roulade-policy", type=Path, default=DEFAULT_POLICY_DIR / "roulade.onnx")
parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
parser.add_argument(
    "--duration",
    type=float,
    default=0.0,
    help="Simulation seconds to run; zero keeps the playground open until the window closes.",
)
parser.add_argument(
    "--action-scale",
    type=float,
    default=None,
    help="Override every policy action scale; default follows the pinned MicroDuck runtime.",
)
parser.add_argument("--stiffness", type=float, default=0.55)
parser.add_argument("--damping", type=float, default=0.053)
parser.add_argument("--effort-limit", type=float, default=0.96)
parser.add_argument("--head-lowpass", type=float, default=0.5)
parser.add_argument("--legs-lowpass", type=float, default=0.7)
parser.add_argument("--switch-threshold", type=float, default=0.05)
parser.add_argument("--ground-pick-period", type=float, default=4.0)
parser.add_argument("--follow-camera", action="store_true")
parser.add_argument("--no-keyboard", action="store_true")
parser.add_argument("--ros-bind", default="127.0.0.1")
parser.add_argument("--ros-command-port", type=int, default=5055)
parser.add_argument("--ros-telemetry-host", default="127.0.0.1")
parser.add_argument("--ros-telemetry-port", type=int, default=5056)
parser.add_argument("--ros-deadman", type=float, default=0.5)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app


import numpy as np
import onnxruntime as ort
import torch

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import Articulation, RigidObject
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.assets.rigid_object import RigidObjectCfg
from isaaclab.devices import Se2Keyboard, Se2KeyboardCfg
from isaaclab.sim import SimulationContext
from isaaclab.utils.math import quat_apply, quat_apply_inverse


class PolicySession(NamedTuple):
    session: ort.InferenceSession
    input_name: str
    output_name: str


class RosUdpControl:
    """Small localhost transport that keeps ROS out of Isaac's Python process."""

    def __init__(
        self,
        bind_host: str,
        command_port: int,
        telemetry_host: str,
        telemetry_port: int,
        deadman_s: float,
    ) -> None:
        if not 0 < command_port < 65536 or not 0 < telemetry_port < 65536:
            raise ValueError("ROS UDP ports must be between 1 and 65535")
        if deadman_s <= 0.0:
            raise ValueError("--ros-deadman must be positive")
        self.deadman_s = deadman_s
        self.telemetry_target = (telemetry_host, telemetry_port)
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.receiver.bind((bind_host, command_port))
        self.receiver.setblocking(False)
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.last_received_monotonic: float | None = None
        # The ROS bridge starts both counters at zero. Matching that baseline
        # prevents the first ordinary command packet from causing a reset.
        self.last_behavior_sequence = 0
        self.last_reset_sequence = 0
        self.last_session: str | None = None
        self._stale_command_cleared = False

    def close(self) -> None:
        self.receiver.close()
        self.sender.close()

    def poll(self, controller: PlaygroundController) -> bool:
        newest: dict[str, object] | None = None
        while True:
            try:
                payload, _ = self.receiver.recvfrom(65535)
            except BlockingIOError:
                break
            try:
                candidate = json.loads(payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if isinstance(candidate, dict):
                newest = candidate

        if newest is not None:
            try:
                command = validate_udp_command(newest)
                session = str(command["session"])
                if session != self.last_session:
                    self.last_session = session
                    self.last_behavior_sequence = 0
                    self.last_reset_sequence = 0

                controller.set_velocity(*command["velocity"])
                controller.set_head(command["head"])
                controller.set_body(command["body"])

                behavior_sequence = int(command["behavior_sequence"])
                reset_sequence = int(command["reset_sequence"])
                behavior = str(command["behavior"])

                if (
                    behavior_sequence > self.last_behavior_sequence
                    and behavior
                ):
                    if not controller.trigger(behavior):
                        print(f"Behavior unavailable or busy: {behavior}")
                    self.last_behavior_sequence = behavior_sequence

                if reset_sequence > self.last_reset_sequence:
                    controller.reset()
                    self.last_reset_sequence = reset_sequence
            except (TypeError, ValueError, OverflowError) as error:
                print(f"Discarded invalid ROS UDP command: {error}")
            else:
                self.last_received_monotonic = time.monotonic()
                self._stale_command_cleared = False

        if self.last_received_monotonic is None:
            return False
        active = time.monotonic() - self.last_received_monotonic <= self.deadman_s
        if not active and not self._stale_command_cleared:
            controller.set_velocity(0.0, 0.0, 0.0)
            self._stale_command_cleared = True
        return active

    def send_telemetry(self, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload, separators=(",", ":"), allow_nan=False).encode("utf-8")
        self.sender.sendto(encoded, self.telemetry_target)


def build_robot_cfg() -> ArticulationCfg:
    return ArticulationCfg(
        prim_path="/World/MicroDuck",
        articulation_root_prim_path="/Geometry/trunk_base",
        spawn=sim_utils.UsdFileCfg(
            usd_path=str(args_cli.usd.resolve()),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                max_depenetration_velocity=1.0,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=2,
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, 0.005)),
        actuators={
            "policy_joints": ImplicitActuatorCfg(
                joint_names_expr=[".*"],
                effort_limit_sim=args_cli.effort_limit,
                velocity_limit_sim=6.0,
                stiffness=args_cli.stiffness,
                damping=args_cli.damping,
            )
        },
    )


def build_ball_cfg() -> RigidObjectCfg:
    return RigidObjectCfg(
        prim_path="/World/Ball",
        spawn=sim_utils.SphereCfg(
            radius=BALL_RADIUS_M,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                max_depenetration_velocity=1.0,
            ),
            mass_props=sim_utils.MassPropertiesCfg(mass=0.015),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            visual_material=sim_utils.PreviewSurfaceCfg(
                diffuse_color=(1.0, 0.55, 0.05),
                roughness=0.35,
            ),
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.3, 0.0, BALL_RADIUS_M)),
    )


def open_policy(path: Path) -> PolicySession:
    session = ort.InferenceSession(str(path.resolve()), providers=["CPUExecutionProvider"])
    inputs = session.get_inputs()
    outputs = session.get_outputs()
    if len(inputs) != 1 or inputs[0].shape[-1] != OBSERVATION_SIZE:
        raise ValueError(f"{path.name}: expected one {OBSERVATION_SIZE}D input, got {inputs}")
    if len(outputs) != 1 or outputs[0].shape[-1] != ACTION_SIZE:
        raise ValueError(f"{path.name}: expected one {ACTION_SIZE}D output, got {outputs}")
    zero_observation = np.zeros((1, OBSERVATION_SIZE), dtype=np.float32)
    session.run([outputs[0].name], {inputs[0].name: zero_observation})
    return PolicySession(session, inputs[0].name, outputs[0].name)


def load_policies() -> dict[str, PolicySession]:
    candidates = {
        "walking": args_cli.walking_policy,
        "standing": args_cli.standing_policy,
        "sitstand": args_cli.sitstand_policy,
        "ground_pick": args_cli.ground_pick_policy,
        "kick_left": args_cli.kick_left_policy,
        "kick_right": args_cli.kick_right_policy,
        "roulade": args_cli.roulade_policy,
    }
    policies: dict[str, PolicySession] = {}
    for name, path in candidates.items():
        if path.is_file():
            policies[name] = open_policy(path)
            print(f"Loaded {name:>11}: {path}")
        else:
            print(f"Skipped {name:>11}: {path} is unavailable")
    if not set(policies).intersection({"walking", "standing", "sitstand"}):
        raise FileNotFoundError(
            "No base policy is available. Run ./scripts/fetch_upstream.sh "
            "before opening the playground."
        )
    return policies


def initialize_robot(
    robot: Articulation, sim: SimulationContext
) -> tuple[torch.Tensor, torch.Tensor]:
    joint_names = tuple(robot.joint_names)
    if set(joint_names) != set(POLICY_JOINTS):
        raise ValueError(f"Isaac joint names differ from policy contract: {joint_names}")
    policy_to_isaac = torch.tensor(
        [joint_names.index(name) for name in POLICY_JOINTS],
        dtype=torch.long,
        device=sim.device,
    )
    home_policy = torch.tensor(
        [HOME_POSE], dtype=robot.data.joint_pos.torch.dtype, device=sim.device
    )
    home_isaac = torch.empty_like(home_policy)
    home_isaac[:, policy_to_isaac] = home_policy
    root_pose = robot.data.default_root_pose.torch.clone()
    root_pose[:, :3] = torch.tensor([0.0, 0.0, 0.125], dtype=root_pose.dtype, device=sim.device)
    root_pose[:, 3:] = torch.tensor([0.0, 0.0, 0.0, 1.0], dtype=root_pose.dtype, device=sim.device)
    robot.write_root_pose_to_sim_index(root_pose=root_pose)
    robot.write_root_velocity_to_sim_index(
        root_velocity=torch.zeros_like(robot.data.default_root_vel.torch)
    )
    robot.write_joint_position_to_sim_index(position=home_isaac)
    robot.write_joint_velocity_to_sim_index(velocity=torch.zeros_like(home_isaac))
    robot.reset()
    return policy_to_isaac, home_policy


def place_ball(ball: RigidObject, robot: Articulation, side: str, sim: SimulationContext) -> None:
    root_quat = robot.data.root_quat_w.torch
    lateral = BALL_OFFSET_ABS_Y if side == "left" else -BALL_OFFSET_ABS_Y
    local_offset = torch.tensor(
        [[BALL_OFFSET_X, lateral, 0.0]], dtype=root_quat.dtype, device=sim.device
    )
    world_offset = quat_apply(root_quat, local_offset)
    ball_pose = ball.data.default_root_pose.torch.clone()
    ball_pose[:, :3] = robot.data.root_pos_w.torch + world_offset
    ball_pose[:, 2] = BALL_RADIUS_M
    ball_pose[:, 3:] = torch.tensor(
        [0.0, 0.0, 0.0, 1.0], dtype=ball_pose.dtype, device=sim.device
    )
    ball.write_root_pose_to_sim_index(root_pose=ball_pose)
    ball.write_root_velocity_to_sim_index(
        root_velocity=torch.zeros_like(ball.data.default_root_vel.torch)
    )
    ball.reset()


def configure_keyboard(controller: PlaygroundController):
    pending: deque[tuple[str, object]] = deque()
    if args_cli.no_keyboard or args_cli.headless:
        return None, pending
    keyboard = Se2Keyboard(
        Se2KeyboardCfg(
            v_x_sensitivity=0.35,
            v_y_sensitivity=0.25,
            omega_z_sensitivity=0.8,
            sim_device=args_cli.device,
        )
    )

    def queue_behavior(name: str):
        return lambda: pending.append(("behavior", name))

    def queue_head(index: int, delta: float):
        return lambda: pending.append(("head", (index, delta)))

    keyboard.add_callback("Y", queue_behavior("sitstand"))
    keyboard.add_callback("G", queue_behavior("ground_pick"))
    keyboard.add_callback("K", queue_behavior("kick_left"))
    keyboard.add_callback("M", queue_behavior("kick_right"))
    keyboard.add_callback("R", queue_behavior("roulade"))
    keyboard.add_callback("BACKSPACE", queue_behavior("reset"))
    keyboard.add_callback("W", queue_head(0, 0.08))
    keyboard.add_callback("S", queue_head(0, -0.08))
    keyboard.add_callback("A", queue_head(1, 0.08))
    keyboard.add_callback("D", queue_head(1, -0.08))
    keyboard.add_callback("Q", queue_head(2, 0.10))
    keyboard.add_callback("E", queue_head(2, -0.10))
    keyboard.add_callback("C", queue_head(3, 0.04))
    keyboard.add_callback("V", queue_head(3, -0.04))
    keyboard.add_callback("H", lambda: pending.append(("clear_head", None)))
    print(keyboard)
    print(
        "MicroDuck skills:\n"
        "  Y sit/stand | G ground pick | K/M kick left/right | R roulade\n"
        "  W/S neck | A/D head pitch | Q/E head yaw | C/V head roll | H center head\n"
        "  Backspace reset robot | L stop velocity"
    )
    return keyboard, pending


def process_keyboard_events(
    controller: PlaygroundController,
    pending: deque[tuple[str, object]],
) -> None:
    while pending:
        event_type, value = pending.popleft()
        if event_type == "behavior":
            if not controller.trigger(str(value)):
                print(f"Behavior unavailable or busy: {value}")
        elif event_type == "head":
            index, delta = value
            controller.bump_head(int(index), float(delta))
            print(f"Head command: {[round(item, 3) for item in controller.head_command]}")
        elif event_type == "clear_head":
            controller.clear_head()
            print("Head command centered")


def make_telemetry(
    robot: Articulation,
    policy_to_isaac: torch.Tensor,
    controller: PlaygroundController,
    action_scale: float,
) -> dict[str, object]:
    root_pos = robot.data.root_pos_w.torch[0]
    root_quat = robot.data.root_quat_w.torch[0]
    joint_pos = robot.data.joint_pos.torch[0, policy_to_isaac]
    projected_gravity = robot.data.projected_gravity_b.torch[0]
    tilt = math.acos(max(-1.0, min(1.0, float(-projected_gravity[2].item()))))
    return {
        "stamp_monotonic_s": time.monotonic(),
        "policy": controller.current_policy,
        "action_scale": action_scale,
        "command": list(controller.command()),
        "joint_names": list(POLICY_JOINTS),
        "joint_positions": joint_pos.cpu().tolist(),
        "root_position": root_pos.cpu().tolist(),
        "root_quaternion_xyzw": root_quat.cpu().tolist(),
        "upright": bool(float(root_pos[2].item()) > 0.08 and tilt < 0.8),
        "tilt_rad": tilt,
    }


def main() -> int:
    if args_cli.duration < 0.0:
        raise ValueError("--duration must be zero or positive")
    if not args_cli.usd.is_file():
        raise FileNotFoundError(args_cli.usd)
    if args_cli.action_scale is not None and (
        not math.isfinite(args_cli.action_scale) or args_cli.action_scale <= 0.0
    ):
        raise ValueError("--action-scale must be finite and positive")
    for option, value in (
        ("--head-lowpass", args_cli.head_lowpass),
        ("--legs-lowpass", args_cli.legs_lowpass),
    ):
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"{option} must be between zero and one")

    policies = load_policies()
    controller = PlaygroundController(
        available_policies=set(policies),
        switch_threshold=args_cli.switch_threshold,
        ground_pick_period_s=args_cli.ground_pick_period,
    )
    ros_control = RosUdpControl(
        args_cli.ros_bind,
        args_cli.ros_command_port,
        args_cli.ros_telemetry_host,
        args_cli.ros_telemetry_port,
        args_cli.ros_deadman,
    )
    keyboard, pending_keyboard = configure_keyboard(controller)

    sim_cfg = sim_utils.SimulationCfg(
        dt=PHYSICS_TIMESTEP_S,
        render_interval=CONTROL_DECIMATION,
        device=args_cli.device,
    )
    sim = SimulationContext(sim_cfg)
    ground_cfg = sim_utils.GroundPlaneCfg(
        physics_material=sim_utils.RigidBodyMaterialCfg(
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        )
    )
    ground_cfg.func("/World/Ground", ground_cfg)
    light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
    light_cfg.func("/World/Light", light_cfg)
    robot = Articulation(cfg=build_robot_cfg())
    ball = RigidObject(cfg=build_ball_cfg())
    sim.reset()
    robot.reset()
    ball.reset()
    policy_to_isaac, home_policy = initialize_robot(robot, sim)
    place_ball(ball, robot, "left", sim)
    if args_cli.follow_camera:
        sim.set_camera_view(eye=(0.45, -0.45, 0.3), target=(0.0, 0.0, 0.11))

    gravity_world = torch.tensor([[0.0, 0.0, -1.0]], dtype=torch.float32, device=sim.device)
    last_action = torch.zeros((1, ACTION_SIZE), dtype=torch.float32, device=sim.device)
    previous_target_policy = home_policy.clone()
    simulated_time_s = 0.0
    telemetry_period_steps = max(1, round(CONTROL_HZ / 20.0))
    policy_switches: list[dict[str, object]] = []
    previous_policy = controller.current_policy
    print(f"Playground ready. Active policy: {controller.current_policy}")

    try:
        control_step = 0
        while simulation_app.is_running() and (
            args_cli.duration == 0.0 or simulated_time_s < args_cli.duration
        ):
            remote_active = ros_control.poll(controller)
            process_keyboard_events(controller, pending_keyboard)
            if keyboard is not None and not remote_active:
                velocity = keyboard.advance().cpu().tolist()
                controller.set_velocity(*velocity)
            if controller.consume_reset_request():
                policy_to_isaac, home_policy = initialize_robot(robot, sim)
                place_ball(ball, robot, "left", sim)
                last_action.zero_()
                previous_target_policy = home_policy.clone()
                print("MicroDuck reset to home pose")

            if controller.current_policy != previous_policy:
                policy_switches.append(
                    {
                        "time_s": simulated_time_s,
                        "from": previous_policy,
                        "to": controller.current_policy,
                    }
                )
                print(f"Policy: {previous_policy} -> {controller.current_policy}")
                if controller.current_policy == "kick_left":
                    place_ball(ball, robot, "left", sim)
                elif controller.current_policy == "kick_right":
                    place_ball(ball, robot, "right", sim)
                previous_policy = controller.current_policy

            command = torch.tensor(
                [controller.command()], dtype=torch.float32, device=sim.device
            )
            root_quat = robot.data.root_quat_w.torch
            base_ang_vel = quat_apply_inverse(root_quat, robot.data.root_ang_vel_w.torch)
            projected_gravity = quat_apply_inverse(root_quat, gravity_world)
            joint_pos_policy = robot.data.joint_pos.torch[:, policy_to_isaac]
            joint_vel_policy = robot.data.joint_vel.torch[:, policy_to_isaac]
            observation = torch.cat(
                (
                    base_ang_vel,
                    projected_gravity,
                    joint_pos_policy - home_policy,
                    joint_vel_policy,
                    last_action,
                    command,
                ),
                dim=1,
            )
            if observation.shape != (1, OBSERVATION_SIZE) or not bool(
                torch.isfinite(observation).all()
            ):
                raise FloatingPointError(f"Invalid observation at control step {control_step}")

            policy = policies[controller.current_policy]
            action_np = policy.session.run(
                [policy.output_name],
                {policy.input_name: observation.cpu().numpy().astype(np.float32, copy=False)},
            )[0]
            action = torch.as_tensor(
                action_np.reshape(1, ACTION_SIZE), dtype=torch.float32, device=sim.device
            )
            if not bool(torch.isfinite(action).all()):
                raise FloatingPointError(f"Invalid action at control step {control_step}")
            action_scale = (
                args_cli.action_scale
                if args_cli.action_scale is not None
                else controller.action_scale()
            )
            raw_target_policy = home_policy + action_scale * action
            target_policy = raw_target_policy.clone()
            target_policy[:, 5:9] = (
                args_cli.head_lowpass * raw_target_policy[:, 5:9]
                + (1.0 - args_cli.head_lowpass) * previous_target_policy[:, 5:9]
            )
            target_policy[:, :5] = (
                args_cli.legs_lowpass * raw_target_policy[:, :5]
                + (1.0 - args_cli.legs_lowpass) * previous_target_policy[:, :5]
            )
            target_policy[:, 9:] = (
                args_cli.legs_lowpass * raw_target_policy[:, 9:]
                + (1.0 - args_cli.legs_lowpass) * previous_target_policy[:, 9:]
            )
            target_isaac = torch.empty_like(target_policy)
            target_isaac[:, policy_to_isaac] = target_policy
            last_action = action
            previous_target_policy = target_policy

            for _ in range(CONTROL_DECIMATION):
                robot.set_joint_position_target_index(target=target_isaac)
                robot.write_data_to_sim()
                ball.write_data_to_sim()
                sim.step()
                robot.update(sim.get_physics_dt())
                ball.update(sim.get_physics_dt())

            if args_cli.follow_camera and control_step % 5 == 0:
                root_pos = robot.data.root_pos_w.torch[0]
                root_x = float(root_pos[0].item())
                root_y = float(root_pos[1].item())
                sim.set_camera_view(
                    eye=(root_x + 0.45, root_y - 0.45, 0.3),
                    target=(root_x, root_y, 0.11),
                )
            if control_step % telemetry_period_steps == 0:
                ros_control.send_telemetry(
                    make_telemetry(
                        robot, policy_to_isaac, controller, action_scale
                    )
                )

            # Advance skill windows after the tick that used them, matching
            # the pinned robot runtime's control-loop ordering.
            controller.update(1.0 / CONTROL_HZ)
            control_step += 1
            simulated_time_s = control_step / CONTROL_HZ

        final_action_scale = (
            args_cli.action_scale
            if args_cli.action_scale is not None
            else controller.action_scale()
        )
        telemetry = make_telemetry(
            robot, policy_to_isaac, controller, final_action_scale
        )
        report = {
            "duration_s": simulated_time_s,
            "control_hz": CONTROL_HZ,
            "physics_timestep_s": PHYSICS_TIMESTEP_S,
            "tuning": {
                "action_scale_override": args_cli.action_scale,
                "head_lowpass": args_cli.head_lowpass,
                "legs_lowpass": args_cli.legs_lowpass,
            },
            "available_policies": sorted(policies),
            "final": telemetry,
            "policy_switches": policy_switches,
            "ros_udp": {
                "command_bind": f"{args_cli.ros_bind}:{args_cli.ros_command_port}",
                "telemetry_target": f"{args_cli.ros_telemetry_host}:{args_cli.ros_telemetry_port}",
            },
        }
        args_cli.output.parent.mkdir(parents=True, exist_ok=True)
        args_cli.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {args_cli.output}")
        return 0
    finally:
        ros_control.close()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        simulation_app.close()
