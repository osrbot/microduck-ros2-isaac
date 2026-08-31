# Troubleshooting

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

The package must exist under `work/isaac_python_pkgs`; installing into an
unrelated system Python does not satisfy Isaac's bundled interpreter.

## Isaac fails with `ERROR_DEVICE_LOST`

Always launch through `scripts/run_isaac_policy.sh`. It isolates one Vulkan ICD
and disables multi-GPU rendering. Check the printed ICD and active GPU. On a new
host, set `MICRODUCK_VULKAN_ICD` and `MICRODUCK_ISAAC_ACTIVE_GPU` explicitly
rather than deleting driver manifests.

## Isaac looks frozen during a long GUI run

Watch the five-second simulation progress lines. GUI playback can be slower than
real time. Lack of progress and an unresponsive window are failure signals;
three minutes of wall time for a 60-second simulation was normal on the recorded
host.

## Full validation says setup is missing

`validate_all.sh` expects pinned checkouts, the MuJoCo environment, and Isaac's
project-local ONNX Runtime. Complete [installation](/guide/installation) first.
