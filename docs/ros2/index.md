# Build the ROS 2 description

The `microduck_description` package is generated from the pinned MJCF. It
contains a massless ROS `base_link`, 15 physical links, one fixed root joint,
14 revolute joints, meshes, inertias, launch files, and an RViz profile.

## Generate and validate

From the repository root:

```bash
./scripts/generate_ros_description.py
work/mujoco_env/bin/python scripts/validate_ros_mjcf_pose_parity.py
./scripts/validate_ros2_package.sh
```

The pose validator compares 109 body-joint, inertial, visual, and collision
origins against the source MJCF. It also covers the exact ±90° pitch cases that
can otherwise make neck or leg meshes appear detached.

## Build manually

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Launch the presentation profile

```bash
ros2 launch microduck_description view_microduck.launch.py
```

The default is intentionally light: visual meshes, no collision meshes, a
15 FPS RViz render cap, hidden TF axes, and the static official home pose.

Useful launch arguments:

| Argument | Default | Purpose |
| --- | --- | --- |
| `use_gui` | `false` | Open sliders for all 14 policy joints |
| `use_rviz` | `true` | Start RViz with the package profile |
| `rviz_fullscreen` | `false` | Work around a window that cannot be maximized |
| `with_collision_meshes` | `false` | Load the extra collision geometry |
| `joint_velocity_limit` | `6.0` | Placeholder URDF velocity limit, not hardware truth |

Example:

```bash
ros2 launch microduck_description view_microduck.launch.py \
  use_gui:=true rviz_fullscreen:=true
```

## Runtime acceptance

```bash
./scripts/validate_ros2_runtime.sh
```

This checks the running nodes, `robot_description`, the official 14-joint home
pose, joint states, and TF. A successful build alone does not establish these
runtime contracts.
