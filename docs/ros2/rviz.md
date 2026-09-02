# Move the camera and joints in RViz

First check the camera. Then check the meshes. Last, check the joint data. Follow
that order, and you will not need to restart RViz and hope for the best.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Time</span><strong>8–12 minutes</strong></div>
  <div role="listitem"><span>Prerequisite</span><strong>RViz already opens</strong></div>
  <div role="listitem"><span>Windows</span><strong>RViz + one terminal</strong></div>
  <div role="listitem"><span>Result</span><strong>Camera, parts, and joints all work</strong></div>
</div>

<div class="md-step-kicker"><span>STEP 1</span><strong>RViz window</strong></div>

## Move the camera

The supplied RViz profile starts with **Move Camera** selected:

- left-drag rotates around the robot;
- the mouse wheel zooms;
- middle-drag pans the view.

<div class="md-result-label">REAL RUN · AFTER ROTATING AND ZOOMING</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-camera.webp" alt="Close RViz view after rotating and zooming the Orbit camera" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>Moving the camera only changes your view.</strong>The duck stays together. This real RViz picture was taken after a turn and zoom.</figcaption>
</figure>

If a remote desktop will not let you maximize RViz, launch it fullscreen:

```bash
ros2 launch microduck_description view_microduck.launch.py \
  rviz_fullscreen:=true
```

Dragging the robot itself does not move a joint. Use the sliders instead.

<div class="md-checkpoint">
  <strong>The camera works!</strong>
  <p>Left-drag rotates, the wheel zooms, and middle-drag pans. If nothing moves, select <strong>Move Camera</strong> in the toolbar.</p>
</div>

<div class="md-step-kicker"><span>STEP 2</span><strong>Terminal · sourced ros2_ws</strong></div>

## Move the joints

If the previous launch is still running, return to its terminal, press
<kbd>Ctrl</kbd>+<kbd>C</kbd>, and wait for the log to stop before running:

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

Move one slider at a time, or click **Randomize** for a quick demonstration.
The public simulation model used here contains 14 movable joints.

<div class="md-checkpoint">
  <strong>The joints move!</strong>
  <p>Moving one slider changes the matching joint chain, and returning it to zero restores a recognizable pose.</p>
</div>

<div class="md-step-kicker"><span>STEP 3</span><strong>Only when the model looks incomplete</strong></div>

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

<div class="md-step-kicker"><span>STEP 4</span><strong>Open Terminal B · check ROS data</strong></div>

## The sliders move, but the duck does not

Keep RViz and the sliders running. Press
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> in the original terminal to open a
new window, source the workspace, and check that joint states are being
published:

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic echo /joint_states --once
```

The command exits after one message. Seeing `name:` and `position:` means data
arrived. If it waits forever, check that Joint State Publisher is still running.

If no message appears, restart the launch with `use_gui:=true` and check the
Joint State Publisher terminal for errors.

## Optional: show collision geometry

```bash
ros2 launch microduck_description view_microduck.launch.py \
  with_collision_meshes:=true
```

Then enable **Collision Enabled** in RobotModel. Turn it off again for normal
viewing because it makes RViz heavier.

<div class="md-page-complete">
  <strong>RViz looks good!</strong>
  <p>The camera moves, every part is there, and ROS can read all 14 joints. The next page runs the ready-made ROS 2 motion examples.</p>
</div>
