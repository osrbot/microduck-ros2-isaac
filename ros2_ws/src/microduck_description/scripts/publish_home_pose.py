#!/usr/bin/python3
# Copyright 2026 OSRBOT
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Publish the official MicroDuck 14-joint home pose for visualization."""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


JOINT_NAMES = [
    'left_hip_yaw',
    'left_hip_roll',
    'left_hip_pitch',
    'left_knee',
    'left_ankle',
    'neck_pitch',
    'head_pitch',
    'head_yaw',
    'head_roll',
    'right_hip_yaw',
    'right_hip_roll',
    'right_hip_pitch',
    'right_knee',
    'right_ankle',
]

HOME_POSE = [
    0.0,
    -0.0873,
    -0.4579,
    -0.0049,
    0.4530,
    0.3491,
    0.3491,
    0.0,
    0.0,
    0.0,
    0.0873,
    0.4579,
    0.0049,
    -0.4530,
]


class HomePosePublisher(Node):
    def __init__(self) -> None:
        super().__init__('microduck_home_pose_publisher')
        self.publisher = self.create_publisher(JointState, 'joint_states', 10)
        # The pose is static; 10 Hz keeps late subscribers robust without
        # needlessly rebuilding the full high-detail robot at 30 Hz in RViz.
        self.timer = self.create_timer(1.0 / 10.0, self.publish_pose)

    def publish_pose(self) -> None:
        message = JointState()
        message.header.stamp = self.get_clock().now().to_msg()
        message.name = JOINT_NAMES
        message.position = HOME_POSE
        self.publisher.publish(message)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = HomePosePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
