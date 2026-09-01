# RViz controls and joint sliders

## Camera controls

The supplied RViz profile starts with **Move Camera** selected:

- left-drag rotates around the robot;
- the mouse wheel zooms;
- middle-drag pans the view.

If a remote desktop will not let you maximize RViz, launch it fullscreen:

```bash
ros2 launch microduck_description view_microduck.launch.py \
  rviz_fullscreen:=true
```

Dragging the robot itself does not move a joint. Use the sliders instead.

## Move the joints

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

Move one slider at a time, or click **Randomize** for a quick demonstration.
The public simulation model used here contains 14 movable joints.

## Missing or detached parts

<figure class="md-doc-figure md-bug-figure">
  <img src="/images/rviz-missing-parts.png" alt="Incorrect RViz view with MicroDuck's head detached and visible parts missing" width="646" height="674" loading="lazy">
  <figcaption><strong>This view is incorrect.</strong> Follow the checks below if the head floats, the body has a large gap, or the left and right sides do not match.</figcaption>
</figure>

1. Rotate around the robot first. Some parts are hidden from the front view.
2. In the **Views** panel, click **Reset**.
3. In **RobotModel**, make sure **Visual Enabled** is on and **Alpha** is `1`.
4. Expand **Links**. A mesh that failed to load will show an error beside its
   link name.
5. Check the launch terminal for a failed
   `package://microduck_description/meshes/...` path.
6. Re-source the workspace and launch again:

   ```bash
   cd ros2_ws
   source /opt/ros/jazzy/setup.bash
   source install/setup.bash
   ros2 launch microduck_description view_microduck.launch.py use_gui:=true
   ```

Do not turn on collision geometry to fill a missing visual part. Collision
meshes are a simpler debugging view and are not a replacement for the visible
model.

## The sliders move, but the robot does not

Open another terminal, source the workspace, and check that joint states are
being published:

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic echo /joint_states --once
```

If no message appears, restart the launch with `use_gui:=true` and check the
Joint State Publisher terminal for errors.

## Optional: show collision geometry

```bash
ros2 launch microduck_description view_microduck.launch.py \
  with_collision_meshes:=true
```

Then enable **Collision Enabled** in RobotModel. Turn it off again for normal
viewing because it makes RViz heavier.

See [troubleshooting](/troubleshooting) if RViz still freezes or a mesh path
keeps failing.
