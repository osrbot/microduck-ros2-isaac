#!/usr/bin/env python3
"""Animate the MicroDuck description in RViz without a physics simulator."""

from __future__ import annotations

import time

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import JointState

from .motion_library import JOINT_NAMES, ROUTINES, sample_routine


class RvizMotionDemo(Node):
    """Publish a smooth, joint-limit-safe demonstration trajectory."""

    def __init__(self) -> None:
        super().__init__("microduck_rviz_motion_demo")
        self.declare_parameter("routine", "showcase")
        self.declare_parameter("speed", 1.0)
        self.declare_parameter("repeat", True)
        self.declare_parameter("publish_rate_hz", 20.0)

        self.routine = str(self.get_parameter("routine").value)
        self.speed = float(self.get_parameter("speed").value)
        self.repeat = bool(self.get_parameter("repeat").value)
        publish_rate_hz = float(self.get_parameter("publish_rate_hz").value)
        if self.routine not in ROUTINES:
            choices = ", ".join(sorted(ROUTINES))
            raise ValueError(f"Unknown routine {self.routine!r}; choose {choices}")
        if self.speed <= 0.0 or publish_rate_hz <= 0.0:
            raise ValueError("speed and publish_rate_hz must be positive")

        self.publisher = self.create_publisher(JointState, "joint_states", 10)
        self.started_monotonic = time.monotonic()
        self.last_label = ""
        self.completion_logged = False
        self.create_timer(1.0 / publish_rate_hz, self.publish_pose)
        self.get_logger().info(
            f"Starting RViz-only {self.routine!r} routine at {self.speed:.2f}x. "
            "This animates JointState; it is not a physics simulation."
        )

    def publish_pose(self) -> None:
        elapsed_s = (time.monotonic() - self.started_monotonic) * self.speed
        pose, label, done = sample_routine(
            self.routine,
            elapsed_s,
            repeat=self.repeat,
        )
        message = JointState()
        message.header.stamp = self.get_clock().now().to_msg()
        message.name = list(JOINT_NAMES)
        message.position = list(pose)
        self.publisher.publish(message)
        if label != self.last_label:
            self.get_logger().info(f"RViz demo: {label}")
            self.last_label = label
        if done and not self.completion_logged:
            self.get_logger().info("RViz demo complete; holding the home pose")
            self.completion_logged = True


def main(args=None) -> None:
    rclpy.init(args=args)
    node = RvizMotionDemo()
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
