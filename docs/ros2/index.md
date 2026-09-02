# Open MicroDuck in RViz with ROS 2

This is the quickest full route. Build the package, see the whole duck in RViz,
move all 14 joints, and read real `/joint_states` data. You do not need Isaac Sim
or a real robot.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Time</span><strong>10–15 minutes</strong></div>
  <div role="listitem"><span>Environment</span><strong>Ubuntu 24.04 + Jazzy</strong></div>
  <div role="listitem"><span>Windows</span><strong>1 terminal + 2 GUIs</strong></div>
  <div role="listitem"><span>Result</span><strong>Complete model, 14 movable joints</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>You will</strong>
  <ul>
    <li>build only <code>microduck_description</code>;</li>
    <li>check the head, body, both legs, and both feet;</li>
    <li>move joints with Joint State Publisher;</li>
    <li>read one real <code>/joint_states</code> message.</li>
  </ul>
</div>

::: tip Starting directory
The first command assumes you are at the repository root, where `README.md` and `ros2_ws/` are visible.
:::

## Pick the launch you need

These are the options you will use most. The first run below uses the default;
the joint-slider step adds `use_gui:=true`.

| Option | Use it when |
| --- | --- |
| `use_gui:=true` | You want the joint sliders |
| `rviz_fullscreen:=true` | A remote desktop cannot maximize RViz |
| `use_rviz:=false` | You only need the description and TF nodes |
| `with_collision_meshes:=true` | You are debugging collision geometry |

For example, open the sliders and full-screen RViz together:

```bash
ros2 launch microduck_description view_microduck.launch.py \
  use_gui:=true rviz_fullscreen:=true
```

<div class="md-command-steps">
  <strong>Open Terminal A</strong>
  <p>Press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd>. If it opens in your home directory, run <code>cd /your/path/microduck-ros2-isaac</code> with the real repository path.</p>
</div>

<div class="md-step-kicker"><span>STEP 1</span><strong>Terminal A · Ctrl + Alt + T</strong></div>

## Build the description package

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select microduck_description
source install/setup.bash
```

A successful build ends with output similar to:

```text
Summary: 1 package finished
```

Confirm that ROS finds the package in this workspace:

```bash
ros2 pkg prefix microduck_description
```

The path should end in `ros2_ws/install/microduck_description`. If the package is missing, source
`install/setup.bash` again. If `colcon` is missing, return to [installation](/guide/installation).

<div class="md-checkpoint">
  <strong>Build looks good!</strong>
  <p>No package failed, and <code>ros2 pkg prefix</code> returns the current workspace path. Fix build errors before opening RViz.</p>
</div>

<div class="md-step-kicker"><span>STEP 2</span><strong>Terminal A · ros2_ws</strong></div>

## Open the duck

```bash
ros2 launch microduck_description view_microduck.launch.py
```

This command keeps running, so the prompt does not return while RViz is open.
**Leave Terminal A open.** RViz should show MicroDuck on the grid. Check these
items before moving the camera:

1. `RobotModel` has no red error.
2. The head and body are connected.
3. Both legs and both feet are visible.
4. The grid remains stable with `base_link` as the fixed frame.

<div class="md-result-label">REAL RUN · RVIZ IS OPEN</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros2-rviz-motion-demo.webp" alt="The ROS 2 motion example showing the complete MicroDuck in RViz" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>Your duck should have all these parts.</strong>This image comes from the motion demo, so one leg is up. The command above opens the home pose.</figcaption>
</figure>

<div class="md-checkpoint">
  <strong>The duck looks right!</strong>
  <p>The complete robot is visible and RobotModel reports no mesh-path error. If parts are missing, use the <a href="/microduck-ros2-isaac/ros2/rviz">missing-part checklist</a> before moving on.</p>
</div>

<div class="md-step-kicker"><span>STEP 3</span><strong>Terminal A · restart with the GUI</strong></div>

## Move the joints

Press <kbd>Ctrl</kbd>+<kbd>C</kbd> in Terminal A, wait for the launch to stop, then run:

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

RViz and Joint State Publisher should open. Move `head_yaw` slightly, return it near zero, then move one knee. The
matching joint chain should move in RViz. These sliders publish joint positions; they do not simulate gravity or contact.

<div class="md-result-label">OFFICIAL UI REFERENCE · JOINT STATE PUBLISHER</div>

<figure class="md-doc-figure md-jsp-figure">
  <div class="md-doc-image-stage md-jsp-stage"><img src="/images/joint-state-publisher-gui-official.png" alt="Official ROS 2 Joint State Publisher slider window" width="272" height="194" loading="lazy"></div>
  <figcaption><strong>The slider window follows this layout.</strong>This official ROS package screenshot uses the generic names <code>joint_A</code>, <code>joint_B</code>, and <code>joint_C</code>. MicroDuck shows 14 real joint names instead. Move one slider, then check the matching motion in RViz. <a href="https://github.com/ros/joint_state_publisher/tree/ros2/joint_state_publisher_gui">Image source: ROS joint_state_publisher_gui ↗</a></figcaption>
</figure>

<div class="md-step-kicker"><span>STEP 4</span><strong>Terminal B · new terminal</strong></div>

## Check the ROS message

Leave terminal A, RViz, and the sliders running. Press
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> in Terminal to open window B. Use
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>T</kbd> if you prefer a new tab.

```bash
cd /path/to/microduck-ros2-isaac/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic echo /joint_states --once
```

Replace `/path/to/microduck-ros2-isaac` with the real repository path. The
command prints one YAML message and exits. Its shape is similar to:

```yaml
name: [left_hip_yaw, ..., right_ankle]
position: [0.0, ..., 0.0]
```

The message contains `name` and `position`; `name` has 14 joints. Move a slider,
press <kbd>↑</kbd> in the terminal to recall the command, and press <kbd>Enter</kbd> to confirm
that the related position changes.

<div class="md-checkpoint">
  <strong>ROS data looks good!</strong>
  <p><code>/joint_states</code> returns all 14 joints and changes with the sliders. Both visualization and state publication now work.</p>
</div>

<div class="md-page-complete">
  <strong>Your first ROS 2 duck run is done!</strong>
  <p>You built the package, saw the full duck, moved its joints, and read its ROS state. The next page shows how to move the camera and fix missing parts.</p>
</div>
