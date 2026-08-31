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

"""Visualize MicroDuck in its official home pose or with interactive sliders."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import Command, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description() -> LaunchDescription:
    package_share = FindPackageShare('microduck_description')
    xacro_file = PathJoinSubstitution([package_share, 'urdf', 'microduck.urdf.xacro'])
    rviz_file = PathJoinSubstitution([package_share, 'rviz', 'microduck.rviz'])

    use_gui = LaunchConfiguration('use_gui')
    use_rviz = LaunchConfiguration('use_rviz')
    rviz_fullscreen = LaunchConfiguration('rviz_fullscreen')
    with_collision_meshes = LaunchConfiguration('with_collision_meshes')
    joint_velocity_limit = LaunchConfiguration('joint_velocity_limit')
    robot_description = ParameterValue(
        Command(
            [
                'xacro ',
                xacro_file,
                ' with_collision_meshes:=',
                with_collision_meshes,
                ' joint_velocity_limit:=',
                joint_velocity_limit,
            ]
        ),
        value_type=str,
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument('use_gui', default_value='false'),
            DeclareLaunchArgument('use_rviz', default_value='true'),
            DeclareLaunchArgument('rviz_fullscreen', default_value='false'),
            DeclareLaunchArgument('with_collision_meshes', default_value='false'),
            DeclareLaunchArgument('joint_velocity_limit', default_value='6.0'),
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                parameters=[{'robot_description': robot_description}],
                output='screen',
            ),
            Node(
                package='tf2_ros',
                executable='static_transform_publisher',
                arguments=[
                    '--x',
                    '0',
                    '--y',
                    '0',
                    '--z',
                    '0.12',
                    '--frame-id',
                    'world',
                    '--child-frame-id',
                    'base_link',
                ],
                output='screen',
            ),
            Node(
                package='joint_state_publisher_gui',
                executable='joint_state_publisher_gui',
                parameters=[{'robot_description': robot_description}],
                condition=IfCondition(use_gui),
                output='screen',
            ),
            Node(
                package='microduck_description',
                executable='publish_home_pose',
                condition=UnlessCondition(use_gui),
                output='screen',
            ),
            GroupAction(
                condition=IfCondition(use_rviz),
                actions=[
                    Node(
                        package='rviz2',
                        executable='rviz2',
                        arguments=['-d', rviz_file],
                        condition=UnlessCondition(rviz_fullscreen),
                        output='screen',
                    ),
                    Node(
                        package='rviz2',
                        executable='rviz2',
                        arguments=['-d', rviz_file, '--fullscreen'],
                        condition=IfCondition(rviz_fullscreen),
                        output='screen',
                    ),
                ],
            ),
        ]
    )
