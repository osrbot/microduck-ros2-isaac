#!/usr/bin/env python3
"""Run a repeatable ROS 2 command showcase against the Isaac playground."""

from __future__ import annotations

import json
import time

from geometry_msgs.msg import Twist
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import Bool, Empty, String

from .isaac_sequences import SEQUENCES, DemoStep, sequence_duration


class IsaacShowcase(Node):
    """Publish a deterministic command sequence and watch Isaac telemetry."""

    def __init__(self) -> None:
        super().__init__("microduck_isaac_showcase")
        self.declare_parameter("sequence", "showcase")
        self.declare_parameter("speed", 1.0)
        self.declare_parameter("telemetry_timeout_s", 30.0)
        self.declare_parameter("start_delay_s", 1.0)

        self.sequence_name = str(self.get_parameter("sequence").value)
        self.speed = float(self.get_parameter("speed").value)
        self.telemetry_timeout_s = float(
            self.get_parameter("telemetry_timeout_s").value
        )
        self.start_delay_s = float(self.get_parameter("start_delay_s").value)
        if self.sequence_name not in SEQUENCES:
            choices = ", ".join(sorted(SEQUENCES))
            raise ValueError(
                f"Unknown sequence {self.sequence_name!r}; choose {choices}"
            )
        if not 0.0 < self.speed <= 1.0:
            raise ValueError(
                "speed must be greater than zero and no more than 1.0; "
                "learned behaviors have fixed real-time durations"
            )
        if self.telemetry_timeout_s <= 0.0:
            raise ValueError("telemetry_timeout_s must be positive")
        if self.start_delay_s < 0.0:
            raise ValueError("start_delay_s must be non-negative")

        self.steps = SEQUENCES[self.sequence_name]
        self.velocity_publisher = self.create_publisher(Twist, "cmd_vel", 10)
        self.head_publisher = self.create_publisher(
            JointState, "microduck/head_command", 10
        )
        self.behavior_publisher = self.create_publisher(
            String, "microduck/behavior", 10
        )
        self.reset_publisher = self.create_publisher(Empty, "microduck/reset", 10)
        self.create_subscription(
            String, "microduck/policy_state", self.on_policy_state, 10
        )
        self.create_subscription(Bool, "microduck/upright", self.on_upright, 10)

        self.created_monotonic = time.monotonic()
        self.telemetry_started_monotonic: float | None = None
        self.step_started_monotonic: float | None = None
        self.step_index = 0
        self.entered_step = False
        self.last_policy = ""
        self.last_upright: bool | None = None
        self.done = False
        self.failure_message = ""
        self.create_timer(0.05, self.tick)
        duration = sequence_duration(self.sequence_name) / self.speed
        self.get_logger().info(
            f"Waiting for Isaac telemetry, then running {self.sequence_name!r} "
            f"({duration:.1f} s at {self.speed:.2f}x)"
        )

    def on_policy_state(self, message: String) -> None:
        if self.telemetry_started_monotonic is None:
            self.telemetry_started_monotonic = time.monotonic()
            self.get_logger().info("Isaac telemetry connected; the duck is listening")
        try:
            payload = json.loads(message.data)
            policy = str(payload.get("policy", ""))
        except (json.JSONDecodeError, AttributeError):
            policy = ""
        if policy and policy != self.last_policy:
            self.get_logger().info(f"Isaac policy: {policy}")
            self.last_policy = policy

    def on_upright(self, message: Bool) -> None:
        upright = bool(message.data)
        if self.last_upright is not None and upright != self.last_upright:
            if upright:
                self.get_logger().info("Isaac upright: true")
            else:
                self.get_logger().warning("Isaac upright: false")
        self.last_upright = upright

    def publish_velocity(self, values: tuple[float, float, float]) -> None:
        message = Twist()
        message.linear.x, message.linear.y, message.angular.z = values
        self.velocity_publisher.publish(message)

    def publish_head(self, values: tuple[float, float, float, float]) -> None:
        message = JointState()
        message.header.stamp = self.get_clock().now().to_msg()
        message.name = ["neck_pitch", "head_pitch", "head_yaw", "head_roll"]
        message.position = list(values)
        self.head_publisher.publish(message)

    def enter_step(self, step: DemoStep) -> None:
        self.get_logger().info(
            f"Demo {self.step_index + 1}/{len(self.steps)}: {step.label}"
        )
        if step.reset:
            self.reset_publisher.publish(Empty())
        if step.behavior:
            message = String()
            message.data = step.behavior
            self.behavior_publisher.publish(message)
        self.entered_step = True

    def tick(self) -> None:
        if self.done:
            return
        now = time.monotonic()
        if self.telemetry_started_monotonic is None:
            if now - self.created_monotonic > self.telemetry_timeout_s:
                self.failure_message = (
                    "No Isaac telemetry arrived. Start run_isaac_playground.sh "
                    "before this example."
                )
                self.get_logger().error(self.failure_message)
                self.done = True
            return
        if now - self.telemetry_started_monotonic < self.start_delay_s:
            return

        step = self.steps[self.step_index]
        if self.step_started_monotonic is None:
            self.step_started_monotonic = now
        if not self.entered_step:
            self.enter_step(step)
        self.publish_velocity(step.velocity)
        self.publish_head(step.head)

        if (now - self.step_started_monotonic) * self.speed < step.duration_s:
            return
        self.step_index += 1
        self.step_started_monotonic = now
        self.entered_step = False
        if self.step_index >= len(self.steps):
            self.publish_safe_stop()
            self.get_logger().info(
                f"{self.sequence_name.capitalize()} complete. Go Go Duck!"
            )
            self.done = True

    def publish_safe_stop(self) -> None:
        self.publish_velocity((0.0, 0.0, 0.0))
        self.publish_head((0.0, 0.0, 0.0, 0.0))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = IsaacShowcase()
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
        for _ in range(3):
            node.publish_safe_stop()
            rclpy.spin_once(node, timeout_sec=0.05)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        failure_message = node.failure_message
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    if failure_message:
        raise RuntimeError(failure_message)


if __name__ == "__main__":
    main()
