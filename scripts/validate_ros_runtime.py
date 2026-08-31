#!/usr/bin/python3
"""Check the live MicroDuck ROS graph, home joint state and TF chain."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import time

import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from tf2_ros import Buffer, TransformListener


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/ros/runtime_smoke.json"

JOINT_NAMES = (
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

HOME_POSE = (
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
)


def normalize_node_names(names: list[str]) -> list[str]:
    """Remove ROS CLI noise and normalize generated node suffixes."""
    normalized = set()
    for name in names:
        if name.startswith("_ros2cli_daemon_"):
            continue
        if name.startswith("static_transform_publisher_"):
            name = "static_transform_publisher"
        normalized.add(name)
    return sorted(normalized)


class RuntimeProbe(Node):
    def __init__(self) -> None:
        super().__init__("microduck_runtime_validator")
        self.joint_state: JointState | None = None
        self.robot_description: str | None = None
        self.create_subscription(JointState, "/joint_states", self.on_joint_state, 10)
        description_qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.create_subscription(
            String,
            "/robot_description",
            self.on_robot_description,
            description_qos,
        )
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)

    def on_joint_state(self, message: JointState) -> None:
        self.joint_state = message

    def on_robot_description(self, message: String) -> None:
        self.robot_description = message.data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.timeout <= 0.0:
        raise ValueError("--timeout must be positive")

    rclpy.init()
    node = RuntimeProbe()
    transform = None
    deadline = time.monotonic() + args.timeout
    try:
        while time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
            if node.joint_state is not None and node.robot_description is not None:
                try:
                    transform = node.tf_buffer.lookup_transform(
                        "world",
                        "ankle_left",
                        Time(),
                        timeout=Duration(seconds=0.1),
                    )
                except Exception:
                    transform = None
                if transform is not None:
                    break

        raw_nodes = [name for name, _ in node.get_node_names_and_namespaces()]
        nodes = normalize_node_names(raw_nodes)
        required_nodes = {
            "microduck_home_pose_publisher",
            "robot_state_publisher",
            "static_transform_publisher",
        }
        joint_state = node.joint_state
        positions_match = bool(
            joint_state is not None
            and tuple(joint_state.name) == JOINT_NAMES
            and len(joint_state.position) == len(HOME_POSE)
            and all(
                math.isclose(actual, expected, abs_tol=1e-9)
                for actual, expected in zip(joint_state.position, HOME_POSE, strict=True)
            )
        )
        description_valid = bool(
            node.robot_description
            and '<robot name="microduck">' in node.robot_description
            and "base_link_to_trunk_base" in node.robot_description
        )
        transform_finite = False
        transform_data = None
        if transform is not None:
            translation = transform.transform.translation
            rotation = transform.transform.rotation
            values = (
                translation.x,
                translation.y,
                translation.z,
                rotation.x,
                rotation.y,
                rotation.z,
                rotation.w,
            )
            transform_finite = all(math.isfinite(value) for value in values)
            transform_data = {
                "parent": transform.header.frame_id,
                "child": transform.child_frame_id,
                "translation_m": list(values[:3]),
                "quaternion_xyzw": list(values[3:]),
            }

        checks = {
            "required_nodes_present": required_nodes.issubset(nodes),
            "home_joint_state_matches": positions_match,
            "robot_description_received": description_valid,
            "world_to_left_ankle_tf_available": transform_finite,
        }
        report = {
            "nodes": nodes,
            "joint_names": list(joint_state.name) if joint_state else None,
            "joint_positions_rad": list(joint_state.position) if joint_state else None,
            "robot_description_bytes": len(node.robot_description or ""),
            "world_to_left_ankle": transform_data,
            "checks": checks,
            "all_checks_pass": all(checks.values()),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0 if report["all_checks_pass"] else 1
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
