# Use RViz

## Move the camera

The supplied profile starts with **Move Camera** selected. Left-drag rotates the
Orbit view, the mouse wheel zooms, and middle-drag pans. If remote desktop window
controls cannot maximize RViz, relaunch with:

```bash
ros2 launch microduck_description view_microduck.launch.py \
  rviz_fullscreen:=true
```

RViz is not a mesh editor. Dragging the robot does not move joints.

## Move the joints

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

Use the Joint State Publisher sliders or **Randomize**. The expected chain is:

```text
joint_state_publisher_gui -> /joint_states -> robot_state_publisher -> /tf -> RViz
```

The released simulation/policy contract contains 14 movable joints. The
physical mouth actuator is outside this description and is not invented as a
fifteenth simulation joint.

## If RViz looks like parts are missing

First distinguish a camera/occlusion issue from a description issue:

1. Use **Reset** in the Views panel, then orbit around the robot.
2. In **RobotModel**, confirm `Visual Enabled` is checked and `Alpha` is `1`.
3. Expand `Links`; a missing mesh reports an error for that link. Copy the exact
   link name and resource error.
4. Check the launch terminal for `package://microduck_description/meshes/...`
   load failures.
5. Verify the generated description and its copied meshes:

   ```bash
   ./scripts/generate_ros_description.py
   ./scripts/validate_ros2_package.sh
   ```

6. Re-source the current workspace before relaunching:

   ```bash
   cd ros2_ws
   source /opt/ros/jazzy/setup.bash
   source install/setup.bash
   ```

Do not enable collision meshes to “fill” missing visual parts. Collision
geometry is intentionally simpler and is a separate diagnostic layer.

## Inspect collision geometry

```bash
ros2 launch microduck_description view_microduck.launch.py \
  with_collision_meshes:=true
```

Then enable **Collision Enabled** in RobotModel. Turn it off again for normal
presentation; rendering visual and collision meshes together adds roughly
171,000 triangles on top of the visual model.

## Symptoms and likely causes

| Symptom | Check first |
| --- | --- |
| Camera cannot rotate or zoom | Use the repository RViz config; verify the Tools block was loaded |
| Neck or leg appears detached | Regenerate from the current converter and run pose parity |
| Whole link is absent | RobotModel link error and mesh URI |
| Gray model is visible but detail is hidden | Lighting, camera angle, and visual Alpha |
| Sliders move but RViz does not | `/joint_states`, `/tf`, and the sourced overlay |

See [troubleshooting](/troubleshooting) for command-level diagnostics.
