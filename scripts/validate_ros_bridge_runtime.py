#!/usr/bin/env python3
"""Exercise the ROS-to-Isaac bridge against a tiny fake UDP simulator."""

from __future__ import annotations

import json
import math
import socket
import time

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, Float64MultiArray, String
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
COMMAND_PORT = 15055
TELEMETRY_PORT = 15056


class BridgeProbe(Node):
    def __init__(self) -> None:
        super().__init__("microduck_bridge_probe")
        self.velocity_publisher = self.create_publisher(Twist, "cmd_vel", 10)
        self.behavior_publisher = self.create_publisher(
            String, "microduck/behavior", 10
        )
        self.body_publisher = self.create_publisher(
            Float64MultiArray, "microduck/body_command", 10
        )
        self.joint_state: JointState | None = None
        self.policy_state: String | None = None
        self.upright: Bool | None = None
        self.world_to_base = False
        self.create_subscription(JointState, "joint_states", self.on_joint_state, 10)
        self.create_subscription(
            String, "microduck/policy_state", self.on_policy_state, 10
        )
        self.create_subscription(Bool, "microduck/upright", self.on_upright, 10)
        self.create_subscription(TFMessage, "/tf", self.on_tf, 10)

    def on_joint_state(self, message: JointState) -> None:
        self.joint_state = message

    def on_policy_state(self, message: String) -> None:
        self.policy_state = message

    def on_upright(self, message: Bool) -> None:
        self.upright = message

    def on_tf(self, message: TFMessage) -> None:
        for transform in message.transforms:
            if (
                transform.header.frame_id == "world"
                and transform.child_frame_id == "base_link"
            ):
                self.world_to_base = True


def main() -> int:
    expected_velocity = [0.4, -0.3, 1.0]
    expected_body = [
        0.02,
        0.02,
        0.03,
        math.radians(30.0),
        math.radians(30.0),
        math.radians(30.0),
    ]
    command_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    command_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    command_socket.bind(("127.0.0.1", COMMAND_PORT))
    command_socket.setblocking(False)
    telemetry_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    rclpy.init()
    probe = BridgeProbe()
    received_command = None
    matched_command = None
    sent_telemetry = False
    deadline = time.monotonic() + 10.0
    next_publish = 0.0
    try:
        while time.monotonic() < deadline:
            now = time.monotonic()
            if now >= next_publish:
                velocity = Twist()
                velocity.linear.x = 0.8
                velocity.linear.y = -0.7
                velocity.angular.z = 2.0
                probe.velocity_publisher.publish(velocity)
                behavior = String()
                behavior.data = "kick-left"
                probe.behavior_publisher.publish(behavior)
                body = Float64MultiArray()
                body.data = [1.0] * 6
                probe.body_publisher.publish(body)
                next_publish = now + 0.2

            rclpy.spin_once(probe, timeout_sec=0.05)
            while True:
                try:
                    raw_command, _ = command_socket.recvfrom(65535)
                except BlockingIOError:
                    break
                received_command = json.loads(raw_command.decode("utf-8"))
                if (
                    received_command.get("velocity") == expected_velocity
                    and received_command.get("behavior") == "kick_left"
                    and received_command.get("body") == expected_body
                ):
                    matched_command = received_command

            if matched_command is not None and not sent_telemetry:
                telemetry = {
                    "policy": "kick_left",
                    "joint_names": list(POLICY_JOINTS),
                    "joint_positions": [index / 100.0 for index in range(14)],
                    "root_position": [0.1, -0.2, 0.125],
                    "root_quaternion_xyzw": [0.0, 0.0, 0.0, 1.0],
                    "upright": True,
                    "tilt_rad": 0.01,
                }
                telemetry_socket.sendto(
                    json.dumps(telemetry).encode("utf-8"),
                    ("127.0.0.1", TELEMETRY_PORT),
                )
                sent_telemetry = True

            if (
                sent_telemetry
                and probe.joint_state is not None
                and probe.policy_state is not None
                and probe.upright is not None
                and probe.world_to_base
            ):
                break

        if matched_command is None:
            if received_command is None:
                raise RuntimeError("No command packet arrived from microduck_control_bridge")
            raise RuntimeError(
                f"No complete clipped command arrived; last packet: {received_command}"
            )
        received_command = matched_command
        if received_command.get("velocity") != expected_velocity:
            raise RuntimeError(f"Unexpected clipped velocity: {received_command}")
        if received_command.get("behavior") != "kick_left":
            raise RuntimeError(f"Unexpected behavior command: {received_command}")
        if received_command.get("body") != expected_body:
            raise RuntimeError(f"Unexpected clipped body command: {received_command}")
        if probe.joint_state is None or tuple(probe.joint_state.name) != POLICY_JOINTS:
            raise RuntimeError("Bridge did not publish the 14-joint telemetry contract")
        if probe.policy_state is None:
            raise RuntimeError("Bridge did not publish microduck/policy_state")
        state = json.loads(probe.policy_state.data)
        if state.get("policy") != "kick_left":
            raise RuntimeError(f"Unexpected policy state: {state}")
        if probe.upright is None or not probe.upright.data:
            raise RuntimeError("Bridge did not publish the upright state")
        if not probe.world_to_base:
            raise RuntimeError("Bridge did not broadcast world -> base_link")
        print("ROS bridge command, telemetry, JointState, policy, upright, and TF passed.")
        return 0
    finally:
        probe.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        command_socket.close()
        telemetry_socket.close()


if __name__ == "__main__":
    raise SystemExit(main())
