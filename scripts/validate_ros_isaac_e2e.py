#!/usr/bin/env python3
"""Validate a live ROS 2 -> Isaac playground -> ROS 2 round trip."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, String
from tf2_msgs.msg import TFMessage


POLICY_JOINTS = (
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
)


class LiveIsaacProbe(Node):
    """Publish one real command and collect the resulting ROS telemetry."""

    def __init__(self) -> None:
        super().__init__("microduck_ros_isaac_e2e_probe")
        self.velocity_publisher = self.create_publisher(Twist, "cmd_vel", 10)
        self.behavior_publisher = self.create_publisher(
            String, "microduck/behavior", 10
        )
        self.joint_messages = 0
        self.policy_messages = 0
        self.observed_policies: set[str] = set()
        self.upright: bool | None = None
        self.world_to_base = False
        self.last_joint_positions: list[float] | None = None
        self.command_sent = False
        self.create_subscription(JointState, "joint_states", self.on_joint_state, 10)
        self.create_subscription(
            String, "microduck/policy_state", self.on_policy_state, 10
        )
        self.create_subscription(Bool, "microduck/upright", self.on_upright, 10)
        self.create_subscription(TFMessage, "/tf", self.on_tf, 10)

    def send_command_when_connected(self) -> None:
        if self.command_sent or self.behavior_publisher.get_subscription_count() == 0:
            return
        velocity = Twist()
        velocity.linear.x = 0.2
        self.velocity_publisher.publish(velocity)
        behavior = String()
        behavior.data = "kick_left"
        self.behavior_publisher.publish(behavior)
        self.command_sent = True

    def on_joint_state(self, message: JointState) -> None:
        if tuple(message.name) != POLICY_JOINTS:
            raise RuntimeError(f"Unexpected live joint order: {tuple(message.name)}")
        positions = [float(value) for value in message.position]
        if len(positions) != len(POLICY_JOINTS) or not all(
            math.isfinite(value) for value in positions
        ):
            raise RuntimeError("Live Isaac JointState is incomplete or non-finite")
        self.last_joint_positions = positions
        self.joint_messages += 1

    def on_policy_state(self, message: String) -> None:
        state = json.loads(message.data)
        policy = state.get("policy")
        if not isinstance(policy, str) or not policy:
            raise RuntimeError(f"Invalid live policy state: {state}")
        self.observed_policies.add(policy)
        self.policy_messages += 1

    def on_upright(self, message: Bool) -> None:
        self.upright = bool(message.data)

    def on_tf(self, message: TFMessage) -> None:
        for transform in message.transforms:
            if (
                transform.header.frame_id == "world"
                and transform.child_frame_id == "base_link"
            ):
                self.world_to_base = True

    def telemetry_ready(self) -> bool:
        return (
            self.joint_messages > 0
            and self.policy_messages > 0
            and self.upright is not None
            and self.world_to_base
        )


def load_fresh_playground_report(path: Path, started_wall_time: float) -> dict:
    if not path.is_file() or path.stat().st_mtime < started_wall_time:
        raise FileNotFoundError(path)
    report = json.loads(path.read_text(encoding="utf-8"))
    switches = report.get("policy_switches")
    if not isinstance(switches, list) or not any(
        isinstance(item, dict) and item.get("to") == "kick_left"
        for item in switches
    ):
        raise RuntimeError("Isaac report did not record the ROS kick_left command")
    final = report.get("final")
    if not isinstance(final, dict) or tuple(final.get("joint_names", ())) != POLICY_JOINTS:
        raise RuntimeError("Isaac report does not preserve the 14-joint contract")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--playground-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()
    if args.timeout <= 0.0:
        parser.error("--timeout must be positive")

    started_wall_time = time.time()
    started_monotonic = time.monotonic()
    deadline = started_monotonic + args.timeout
    rclpy.init()
    probe = LiveIsaacProbe()
    report = None
    try:
        while time.monotonic() < deadline:
            probe.send_command_when_connected()
            rclpy.spin_once(probe, timeout_sec=0.05)
            if probe.telemetry_ready():
                try:
                    report = load_fresh_playground_report(
                        args.playground_report.resolve(), started_wall_time
                    )
                except FileNotFoundError:
                    continue
                break
        if not probe.command_sent:
            raise RuntimeError("ROS bridge never subscribed to the behavior command")
        if not probe.telemetry_ready():
            raise RuntimeError(
                "Live Isaac telemetry did not produce JointState, policy, upright, and TF"
            )
        if report is None:
            raise RuntimeError("A fresh completed Isaac playground report did not arrive")

        summary = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "command": {"velocity": [0.2, 0.0, 0.0], "behavior": "kick_left"},
            "joint_messages": probe.joint_messages,
            "policy_messages": probe.policy_messages,
            "observed_policies": sorted(probe.observed_policies),
            "upright_last": probe.upright,
            "world_to_base_tf": probe.world_to_base,
            "joint_count": len(probe.last_joint_positions or ()),
            "isaac_policy_switches": report["policy_switches"],
            "elapsed_s": time.monotonic() - started_monotonic,
        }
        output = args.output.expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2), flush=True)
        print("ROS_ISAAC_E2E_STAGE=complete", flush=True)
        return 0
    finally:
        probe.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
