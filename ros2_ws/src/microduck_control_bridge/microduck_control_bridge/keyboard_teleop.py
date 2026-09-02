#!/usr/bin/env python3
"""Tiny terminal teleop for MicroDuck velocity and skill commands."""

from __future__ import annotations

import select
import sys
import termios
import tty

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from std_msgs.msg import Empty, String


HELP = """
MicroDuck ROS 2 teleop
  w/s forward/back     a/d turn       q/e sidestep      x stop
  y sit/stand          g ground pick  k/m kick L/R      r roulade
  0 reset              ? help         Ctrl-C quit
""".strip()


class KeyboardTeleop(Node):
    def __init__(self) -> None:
        super().__init__("microduck_keyboard_teleop")
        self.velocity_publisher = self.create_publisher(Twist, "cmd_vel", 10)
        self.behavior_publisher = self.create_publisher(
            String, "microduck/behavior", 10
        )
        self.reset_publisher = self.create_publisher(Empty, "microduck/reset", 10)
        self.velocity = [0.0, 0.0, 0.0]
        self.create_timer(0.05, self.publish_velocity)

    def publish_velocity(self) -> None:
        message = Twist()
        message.linear.x = self.velocity[0]
        message.linear.y = self.velocity[1]
        message.angular.z = self.velocity[2]
        self.velocity_publisher.publish(message)

    def handle_key(self, key: str) -> bool:
        velocity_commands = {
            "w": [0.3, 0.0, 0.0],
            "s": [-0.2, 0.0, 0.0],
            "a": [0.0, 0.0, 0.8],
            "d": [0.0, 0.0, -0.8],
            "q": [0.0, 0.2, 0.0],
            "e": [0.0, -0.2, 0.0],
            "x": [0.0, 0.0, 0.0],
        }
        behavior_commands = {
            "y": "sitstand",
            "g": "ground_pick",
            "k": "kick_left",
            "m": "kick_right",
            "r": "roulade",
        }
        if key in velocity_commands:
            self.velocity = velocity_commands[key]
        elif key in behavior_commands:
            message = String()
            message.data = behavior_commands[key]
            self.behavior_publisher.publish(message)
        elif key == "0":
            self.velocity = [0.0, 0.0, 0.0]
            self.reset_publisher.publish(Empty())
        elif key == "?":
            print(HELP, flush=True)
        elif key == "\x03":
            return False
        return True


def main(args=None) -> None:
    if not sys.stdin.isatty():
        raise RuntimeError("microduck_teleop requires an interactive terminal")
    rclpy.init(args=args)
    node = KeyboardTeleop()
    old_settings = termios.tcgetattr(sys.stdin)
    print(HELP, flush=True)
    try:
        tty.setcbreak(sys.stdin.fileno())
        running = True
        while rclpy.ok() and running:
            rclpy.spin_once(node, timeout_sec=0.02)
            readable, _, _ = select.select([sys.stdin], [], [], 0.03)
            if readable:
                running = node.handle_key(sys.stdin.read(1).lower())
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        node.velocity = [0.0, 0.0, 0.0]
        node.publish_velocity()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
