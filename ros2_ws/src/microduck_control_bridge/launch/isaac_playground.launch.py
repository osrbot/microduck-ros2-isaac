# Copyright 2026 OSRBOT
# SPDX-License-Identifier: Apache-2.0

"""Visualize live telemetry from the MicroDuck Isaac playground in RViz."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    description_share = FindPackageShare("microduck_description")
    xacro_file = PathJoinSubstitution(
        [description_share, "urdf", "microduck.urdf.xacro"]
    )
    rviz_file = PathJoinSubstitution([description_share, "rviz", "microduck.rviz"])
    robot_description = ParameterValue(
        Command(["xacro ", xacro_file, " with_collision_meshes:=false"]),
        value_type=str,
    )
    use_rviz = LaunchConfiguration("use_rviz")
    command_port = ParameterValue(
        LaunchConfiguration("command_port"), value_type=int
    )
    telemetry_port = ParameterValue(
        LaunchConfiguration("telemetry_port"), value_type=int
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("command_host", default_value="127.0.0.1"),
            DeclareLaunchArgument("command_port", default_value="5055"),
            DeclareLaunchArgument("telemetry_bind", default_value="127.0.0.1"),
            DeclareLaunchArgument("telemetry_port", default_value="5056"),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": robot_description}],
                output="screen",
            ),
            Node(
                package="microduck_control_bridge",
                executable="microduck_bridge",
                parameters=[
                    {
                        "command_host": LaunchConfiguration("command_host"),
                        "command_port": command_port,
                        "telemetry_bind": LaunchConfiguration("telemetry_bind"),
                        "telemetry_port": telemetry_port,
                    }
                ],
                output="screen",
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                arguments=["-d", rviz_file],
                condition=IfCondition(use_rviz),
                output="screen",
            ),
        ]
    )
