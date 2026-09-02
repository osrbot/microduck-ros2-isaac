#!/usr/bin/env python3
"""Bridge ROS 2 commands and Isaac playground telemetry over localhost UDP."""

from __future__ import annotations

import json
import socket
import time
import uuid

from geometry_msgs.msg import TransformStamped, Twist
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, Empty, Float64MultiArray, String
from tf2_ros import TransformBroadcaster

from .protocol import (
    BODY_LIMITS,
    HEAD_LIMITS,
    POLICY_JOINTS,
    VELOCITY_LIMITS,
    clip_vector,
    normalize_behavior,
    validate_telemetry,
)


class MicroDuckBridge(Node):
    def __init__(self) -> None:
        super().__init__("microduck_control_bridge")
        self.declare_parameter("command_host", "127.0.0.1")
        self.declare_parameter("command_port", 5055)
        self.declare_parameter("telemetry_bind", "127.0.0.1")
        self.declare_parameter("telemetry_port", 5056)
        self.declare_parameter("command_rate_hz", 20.0)
        self.declare_parameter("telemetry_timeout_s", 1.0)

        command_host = self.get_parameter("command_host").value
        command_port = int(self.get_parameter("command_port").value)
        telemetry_bind = self.get_parameter("telemetry_bind").value
        telemetry_port = int(self.get_parameter("telemetry_port").value)
        command_rate_hz = float(self.get_parameter("command_rate_hz").value)
        self.telemetry_timeout_s = float(self.get_parameter("telemetry_timeout_s").value)
        if command_rate_hz <= 0.0 or self.telemetry_timeout_s <= 0.0:
            raise ValueError("Command rate and telemetry timeout must be positive")
        if not 0 < command_port < 65536 or not 0 < telemetry_port < 65536:
            raise ValueError("UDP ports must be between 1 and 65535")

        self.command_target = (str(command_host), command_port)
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.receiver.bind((str(telemetry_bind), telemetry_port))
        self.receiver.setblocking(False)

        self.velocity = [0.0, 0.0, 0.0]
        self.head = [0.0, 0.0, 0.0, 0.0]
        self.body = [0.0] * 6
        self.behavior = ""
        self.session = uuid.uuid4().hex
        self.behavior_sequence = 0
        self.reset_sequence = 0
        self.started_monotonic = time.monotonic()
        self.last_telemetry_monotonic: float | None = None
        self.reported_timeout = False

        self.joint_state_publisher = self.create_publisher(JointState, "joint_states", 10)
        self.policy_state_publisher = self.create_publisher(
            String, "microduck/policy_state", 10
        )
        self.upright_publisher = self.create_publisher(Bool, "microduck/upright", 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.create_subscription(Twist, "cmd_vel", self.on_velocity, 10)
        self.create_subscription(
            JointState, "microduck/head_command", self.on_head_command, 10
        )
        self.create_subscription(
            Float64MultiArray, "microduck/body_command", self.on_body_command, 10
        )
        self.create_subscription(String, "microduck/behavior", self.on_behavior, 10)
        self.create_subscription(Empty, "microduck/reset", self.on_reset, 10)
        self.create_timer(1.0 / command_rate_hz, self.tick)
        self.get_logger().info(
            f"Commanding Isaac at {self.command_target[0]}:{self.command_target[1]}; "
            f"listening for telemetry on {telemetry_bind}:{telemetry_port}"
        )

    def destroy_node(self) -> bool:
        self.sender.close()
        self.receiver.close()
        return super().destroy_node()

    def on_velocity(self, message: Twist) -> None:
        self.velocity = clip_vector(
            (message.linear.x, message.linear.y, message.angular.z), VELOCITY_LIMITS
        )

    def on_head_command(self, message: JointState) -> None:
        if message.name:
            by_name = dict(zip(message.name, message.position))
            missing = [name for name in POLICY_JOINTS[5:9] if name not in by_name]
            if missing:
                self.get_logger().warning(f"Head command is missing joints: {missing}")
                return
            values = [by_name[name] for name in POLICY_JOINTS[5:9]]
        else:
            values = list(message.position)
        try:
            self.head = clip_vector(values, HEAD_LIMITS)
        except ValueError as error:
            self.get_logger().warning(str(error))

    def on_behavior(self, message: String) -> None:
        try:
            self.behavior = normalize_behavior(message.data)
        except ValueError as error:
            self.get_logger().warning(str(error))
            return
        self.behavior_sequence += 1

    def on_body_command(self, message: Float64MultiArray) -> None:
        try:
            self.body = clip_vector(message.data, BODY_LIMITS)
        except ValueError as error:
            self.get_logger().warning(str(error))

    def on_reset(self, _message: Empty) -> None:
        self.reset_sequence += 1

    def tick(self) -> None:
        command = {
            "version": 1,
            "session": self.session,
            "velocity": self.velocity,
            "head": self.head,
            "body": self.body,
            "behavior": self.behavior,
            "behavior_sequence": self.behavior_sequence,
            "reset_sequence": self.reset_sequence,
        }
        self.sender.sendto(
            json.dumps(command, separators=(",", ":"), allow_nan=False).encode("utf-8"),
            self.command_target,
        )
        self.receive_telemetry()
        telemetry_reference = (
            self.last_telemetry_monotonic
            if self.last_telemetry_monotonic is not None
            else self.started_monotonic
        )
        if (
            time.monotonic() - telemetry_reference > self.telemetry_timeout_s
            and not self.reported_timeout
        ):
            self.get_logger().warning(
                "No recent Isaac telemetry; check run_isaac_playground.sh"
            )
            self.reported_timeout = True

    def receive_telemetry(self) -> None:
        newest = None
        while True:
            try:
                payload, _ = self.receiver.recvfrom(65535)
            except BlockingIOError:
                break
            try:
                candidate = json.loads(payload.decode("utf-8"))
                newest = validate_telemetry(candidate)
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                self.get_logger().warning(f"Discarded invalid Isaac telemetry: {error}")
        if newest is None:
            return
        self.last_telemetry_monotonic = time.monotonic()
        self.reported_timeout = False
        stamp = self.get_clock().now().to_msg()

        joint_state = JointState()
        joint_state.header.stamp = stamp
        joint_state.name = list(POLICY_JOINTS)
        joint_state.position = newest["joint_positions"]
        self.joint_state_publisher.publish(joint_state)

        transform = TransformStamped()
        transform.header.stamp = stamp
        transform.header.frame_id = "world"
        transform.child_frame_id = "base_link"
        position = newest["root_position"]
        quaternion = newest["root_quaternion_xyzw"]
        transform.transform.translation.x = position[0]
        transform.transform.translation.y = position[1]
        transform.transform.translation.z = position[2]
        transform.transform.rotation.x = quaternion[0]
        transform.transform.rotation.y = quaternion[1]
        transform.transform.rotation.z = quaternion[2]
        transform.transform.rotation.w = quaternion[3]
        self.tf_broadcaster.sendTransform(transform)

        state = String()
        state.data = json.dumps(
            {
                "policy": newest["policy"],
                "upright": newest["upright"],
                "tilt_rad": newest["tilt_rad"],
            },
            separators=(",", ":"),
        )
        self.policy_state_publisher.publish(state)
        upright = Bool()
        upright.data = newest["upright"]
        self.upright_publisher.publish(upright)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = MicroDuckBridge()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
