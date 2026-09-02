# Copyright 2026 OSRBOT
# SPDX-License-Identifier: Apache-2.0

"""Animate MicroDuck in RViz without starting Isaac Sim."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition, UnlessCondition
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
    rviz_fullscreen = LaunchConfiguration("rviz_fullscreen")

    return LaunchDescription(
        [
            DeclareLaunchArgument("routine", default_value="showcase"),
            DeclareLaunchArgument("speed", default_value="1.0"),
            DeclareLaunchArgument("repeat", default_value="true"),
            DeclareLaunchArgument("use_rviz", default_value="true"),
            DeclareLaunchArgument("rviz_fullscreen", default_value="false"),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": robot_description}],
                output="screen",
            ),
            Node(
                package="tf2_ros",
                executable="static_transform_publisher",
                arguments=[
                    "--x",
                    "0",
                    "--y",
                    "0",
                    "--z",
                    "0.12",
                    "--frame-id",
                    "world",
                    "--child-frame-id",
                    "base_link",
                ],
                output="screen",
            ),
            Node(
                package="microduck_examples",
                executable="rviz_motion_demo",
                parameters=[
                    {
                        "routine": LaunchConfiguration("routine"),
                        "speed": ParameterValue(
                            LaunchConfiguration("speed"), value_type=float
                        ),
                        "repeat": ParameterValue(
                            LaunchConfiguration("repeat"), value_type=bool
                        ),
                    }
                ],
                output="screen",
            ),
            GroupAction(
                condition=IfCondition(use_rviz),
                actions=[
                    Node(
                        package="rviz2",
                        executable="rviz2",
                        arguments=["-d", rviz_file],
                        condition=UnlessCondition(rviz_fullscreen),
                        output="screen",
                    ),
                    Node(
                        package="rviz2",
                        executable="rviz2",
                        arguments=["-d", rviz_file, "--fullscreen"],
                        condition=IfCondition(rviz_fullscreen),
                        output="screen",
                    ),
                ],
            ),
        ]
    )
