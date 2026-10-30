# Troubleshooting

Start with the matching symptom. Run commands from the project root unless a block
explicitly starts with `cd ros2_ws`. Use a terminal with ROS and the workspace
environment loaded for ROS commands. On Humble, replace `jazzy` with `humble`.

## RViz camera does not move

Use the repository's current RViz config. Select **Move Camera** (or press `M`),
left-drag empty space, and use the wheel to zoom. If the toolbar or Views panel
is absent, an older installed package may be shadowing the current workspace:

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 pkg prefix microduck_description
```

The prefix should point into this workspace's `install/` directory.

## RViz crashes at startup on Humble

If the command includes `rviz_fullscreen:=true`, remove it and launch again:

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

`rviz_fullscreen` is a project launch option, not a built-in RViz parameter.
Forced fullscreen has been reported to crash on Humble. Start in the default
window and resize it after it opens.

## RViz is missing or detaching parts

Run the targeted checks:

```bash
./scripts/generate_ros_description.py
work/mujoco_env/bin/python scripts/validate_ros_mjcf_pose_parity.py
./scripts/validate_ros2_package.sh
```

Then inspect RobotModel → Links for the first resource error. Detached neck or
leg visuals often indicate stale generated Xacro from before the ±90° pitch
conversion fix; a completely absent link usually indicates a mesh URI or copied
asset problem. See [the RViz diagnostic flow](/ros2/rviz).

## Joint sliders do nothing

Confirm `use_gui:=true`, then inspect:

```bash
ros2 topic echo /joint_states --once
ros2 topic hz /joint_states
ros2 run tf2_ros tf2_echo world ankle_left
```

If JointState changes but TF does not, verify `robot_state_publisher` is running
and has the same `robot_description`.

## Isaac reports missing ONNX Runtime

```bash
./scripts/setup_isaac_python_env.sh
```

The package belongs in `work/isaac_python_pkgs`, where Isaac's bundled Python
can load it. Installing it into system Python alone may leave this error unresolved.

## Isaac fails with `ERROR_DEVICE_LOST`

Use the `.sh` entry point from the relevant chapter, such as
`scripts/run_isaac_policy.sh`. These wrappers select one Vulkan ICD and disable
multi-GPU rendering. Check the ICD and active GPU in the startup log. Set
`MICRODUCK_VULKAN_ICD` and `MICRODUCK_ISAAC_ACTIVE_GPU` if needed, keeping the
system driver files in place.

## Isaac looks frozen during a long GUI run

Watch the five-second simulation progress lines. GUI playback can be slower than
real time. Lack of progress and an unresponsive window are failure signals;
three minutes of wall time for a 60-second simulation was normal on the recorded
host.

## Full validation says setup is missing

`validate_all.sh` expects pinned checkouts, the MuJoCo environment, and Isaac's
project-local ONNX Runtime. Complete [installation](/guide/installation) first.
