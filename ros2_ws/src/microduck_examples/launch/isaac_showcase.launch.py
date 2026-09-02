# Copyright 2026 OSRBOT
# SPDX-License-Identifier: Apache-2.0

"""Run an automatic ROS 2 showcase against the MicroDuck Isaac playground."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    bridge_launch = PathJoinSubstitution(
        [
            FindPackageShare("microduck_control_bridge"),
            "launch",
            "isaac_playground.launch.py",
        ]
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument("sequence", default_value="showcase"),
            DeclareLaunchArgument("speed", default_value="1.0"),
            DeclareLaunchArgument("telemetry_timeout_s", default_value="30.0"),
            DeclareLaunchArgument("start_delay_s", default_value="1.0"),
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("command_host", default_value="127.0.0.1"),
            DeclareLaunchArgument("command_port", default_value="5055"),
            DeclareLaunchArgument("telemetry_bind", default_value="127.0.0.1"),
            DeclareLaunchArgument("telemetry_port", default_value="5056"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(bridge_launch),
                launch_arguments={
                    "use_rviz": LaunchConfiguration("use_rviz"),
                    "command_host": LaunchConfiguration("command_host"),
                    "command_port": LaunchConfiguration("command_port"),
                    "telemetry_bind": LaunchConfiguration("telemetry_bind"),
                    "telemetry_port": LaunchConfiguration("telemetry_port"),
                }.items(),
            ),
            Node(
                package="microduck_examples",
                executable="isaac_showcase",
                parameters=[
                    {
                        "sequence": LaunchConfiguration("sequence"),
                        "speed": ParameterValue(
                            LaunchConfiguration("speed"), value_type=float
                        ),
                        "telemetry_timeout_s": ParameterValue(
                            LaunchConfiguration("telemetry_timeout_s"),
                            value_type=float,
                        ),
                        "start_delay_s": ParameterValue(
                            LaunchConfiguration("start_delay_s"), value_type=float
                        ),
                    }
                ],
                output="screen",
            ),
        ]
    )
