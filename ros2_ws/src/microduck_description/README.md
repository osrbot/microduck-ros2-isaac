# microduck_description

ROS 2 Jazzy description package generated from Pollen Robotics' pinned
`microduck_rl` MJCF model.

See the project [ROS 2 tutorial](https://osrbot.github.io/microduck-ros2-isaac/ros2/)
and [RViz troubleshooting guide](https://osrbot.github.io/microduck-ros2-isaac/ros2/rviz)
for the complete build, interaction, and missing-part diagnostic flow.

The generated Xacro preserves the 15-physical-link/14-joint kinematic tree, joint axes and
ranges, full inertia tensors, visual meshes, dedicated collision meshes, and the
selected MJCF actuator effort/damping/friction constants. The 14 movable joints
match the 14-action policy contract; the mouth is not a movable joint in this
upstream simulation model. A massless ROS `base_link` and one fixed joint sit above
`trunk_base` so KDL can retain the real trunk inertia without a root-link warning.
The generator also preserves the full rotation matrix at MJCF quaternion
singularities; `scripts/validate_ros_mjcf_pose_parity.py` checks all 109 generated
poses against the pinned source model.

## View the official home pose

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select microduck_description
source install/setup.bash
ros2 launch microduck_description view_microduck.launch.py
```

Set `use_gui:=true` to replace the official home-pose publisher with interactive
joint sliders. Set `use_rviz:=false` for a headless TF/description smoke test.
The default RViz launch omits collision meshes, hides the TF display, caps RViz
at 15 FPS, and publishes the static home pose at 10 Hz to stay responsive over a
4K remote desktop. None of those presentation defaults removes data from the
Xacro: use `with_collision_meshes:=true` and enable RobotModel collisions when
you need the full collision view. `Move Camera` is the first toolbar tool: select
it (or press `M`), then left-drag to rotate the Orbit view and use the mouse wheel
to zoom. The robot itself does not move in the default home-pose launch.

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

Move any slider—or click `Randomize` for a quick smoke test—to publish a new
14-joint state and update the robot mesh through `robot_state_publisher`.
After regenerating the Xacro, restart the launch because
`robot_state_publisher` caches `robot_description` at startup.

Force a true fullscreen window when desktop maximize is unavailable:

```bash
ros2 launch microduck_description view_microduck.launch.py rviz_fullscreen:=true
```

## Important model boundaries

- Total source-model mass is approximately `0.737243 kg`.
- Effort (`0.96 N m`), damping (`0.053 N m s/rad`) and friction (`0.0048 N m`)
  come from the MJCF `chosen_actuator` class.
- Upstream does not provide authoritative per-joint velocity limits. The Xacro's
  `6.0 rad/s` default is an explicit simulation/planning fallback and can be
  overridden with `joint_velocity_limit:=...`; do not treat it as a measured
  hardware safety limit.
- This package is a description/visualization package. It does not include a
  Dynamixel hardware driver or claim real-robot `ros2_control` validation.

## Provenance and licensing

The generator records the exact upstream revision in the Xacro header and the
project artifact report. Code in this package is Apache-2.0. Pollen Robotics says
the 3D model files are "Creative Commons BY-SA-NC" but does not state a license
version in the upstream README. Treat the meshes as non-commercial and preserve
attribution/share-alike until that ambiguity is resolved with the author.
