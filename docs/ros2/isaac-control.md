# Drive the Isaac duck from ROS 2

Three terminals, one duck. Terminal A runs Isaac Sim, terminal B starts the ROS
bridge and RViz, and terminal C sends commands. Follow this page end to end and
you will see the same live motion in Isaac and RViz.

This exact route was exercised on Ubuntu 24.04, ROS 2 Jazzy, Isaac Sim 6.0.1
standalone, and Isaac Lab 3.0.0 beta 2. The screenshots below are from that run.

::: tip First time here?
Open all three terminals in the repository root. A, B, and C are only labels;
you do not need three computers.
:::

## Before you start: prepare the released policies

If you have not completed the [installation guide](/guide/installation), run
this once:

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

You do not need to download the policies every time. Export `ISAACLAB_DIR` in
each new terminal when Isaac Lab is not installed at the default path.

## 1. Build the ROS bridge

In terminal B:

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install \
  --packages-select microduck_description microduck_control_bridge
source install/setup.bash
cd ..
```

A clean build ends with something like:

```text
Summary: 2 packages finished
```

Fix build errors here before starting Isaac. Keeping setup and runtime problems
separate makes both much easier to diagnose.

## 2. Terminal A: start the Isaac playground

```bash
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

The first launch may take a while while Kit loads extensions. Leave terminal A
open once you can see the complete MicroDuck, the floor, and the yellow ball.

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="The live MicroDuck multi-skill playground in Isaac Lab" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>This is the expected terminal-A result.</strong>The robot and ball are both in the scene, and the viewport follows the robot. This is a real project run, not a concept render.</figcaption>
</figure>

If the robot is missing, check terminal A for a traceback, missing assets, or a
Vulkan error. Do not start a second Isaac process while the first one is still
running.

## 3. Terminal B: start the bridge and RViz

Open a new terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 launch microduck_control_bridge isaac_playground.launch.py
```

The launch starts `robot_state_publisher`, `microduck_control_bridge`, and
`rviz2`. RViz follows the 14 live joint positions and the
`world → base_link` pose coming from Isaac; it is not a manual joint-slider
demo.

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-live.webp" alt="RViz showing the complete MicroDuck pose streamed from Isaac" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>A healthy bridge shows one complete duck in RViz.</strong>The head, neck, body, both legs, and both feet are present, and the MicroDuck and Ground grid displays are healthy.</figcaption>
</figure>

::: warning Does RViz show only part of the robot?
The Orbit camera stays focused on its world-space target while the robot walks.
The robot may simply have left the view. Use **Focus Camera**, reset the
playground, then rotate the view before assuming meshes are missing.
:::

## 4. Terminal C: take a few steps

Open a third terminal and source the workspace:

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
```

Publish a forward command at 10 Hz for four seconds:

```bash
ros2 topic pub -r 10 --times 40 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.30, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

Then stop explicitly:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

<div class="md-runtime-grid">
  <figure class="md-doc-figure">
    <img src="/images/isaac-action-walk.webp" alt="MicroDuck walking in Isaac after a ROS 2 velocity command" width="1200" height="750" loading="lazy">
    <figcaption><strong>Forward.</strong>The active policy changes from standing to walking, then returns to standing after the command stops.</figcaption>
  </figure>
  <figure class="md-doc-figure">
    <img src="/images/isaac-action-turn.webp" alt="MicroDuck turning in Isaac after a ROS 2 yaw command" width="1200" height="750" loading="lazy">
    <figcaption><strong>Turn.</strong>The ball may drift toward the edge of the following camera while the duck keeps moving.</figcaption>
  </figure>
</div>

Turn left in place with:

```bash
ros2 topic pub -r 10 --times 35 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.75}}"
```

Publish the zero-velocity message again when the turn is complete.

## 5. Trigger a skill

All discrete skills use the same topic. Change only `data`:

```bash
ros2 topic pub --once /microduck/behavior std_msgs/msg/String \
  "{data: kick_left}"
```

| `data` | Result |
| --- | --- |
| `kick_left` | Kick with the left foot |
| `kick_right` | Kick with the right foot |
| `ground_pick` | Lower to the floor and return |
| `sitstand` | Sit; publish it again to rise |
| `roulade` | Roll forward |

Kicks last about half a second and the roll lasts about one second. Let one
timed skill finish before requesting another; the controller rejects an unsafe
mid-motion switch.

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-action-sit.webp" alt="MicroDuck lowering its body during the sitstand skill in Isaac" width="1200" height="750" loading="lazy"></div>
  <figcaption><strong>sitstand in progress.</strong>The head and body lower visibly. Publish the same command again to rise.</figcaption>
</figure>

The head fields are ordered as `neck_pitch, head_pitch, head_yaw, head_roll`.
This command was used in the live test:

```bash
ros2 topic pub --once /microduck/head_command sensor_msgs/msg/JointState \
  "{name: ['neck_pitch', 'head_pitch', 'head_yaw', 'head_roll'], position: [0.15, -0.20, 0.75, 0.18]}"
```

Center the head:

```bash
ros2 topic pub --once /microduck/head_command sensor_msgs/msg/JointState \
  "{name: ['neck_pitch', 'head_pitch', 'head_yaw', 'head_roll'], position: [0.0, 0.0, 0.0, 0.0]}"
```

Reset the robot and ball at any time:

```bash
ros2 topic pub --once /microduck/reset std_msgs/msg/Empty "{}"
```

## 6. Move the RViz camera

Select **Move Camera** in RViz:

- drag with the left button to orbit;
- use the wheel or right-button drag to zoom;
- drag with the middle button to move the focal point;
- use **Focus Camera** or reset if the robot leaves the view.

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-camera.webp" alt="MicroDuck close-up after rotating and zooming the RViz Orbit camera" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>This frame follows a real drag-and-zoom test.</strong>Distance changed from 0.38 to about 0.23, and both Yaw and Pitch changed.</figcaption>
</figure>

## 7. Inspect live ROS state

List the graph:

```bash
ros2 node list
ros2 topic list
```

A healthy run includes the bridge, robot state publisher, RViz,
`/joint_states`, `/microduck/policy_state`, `/microduck/upright`, and `/tf`.

Read one joint message:

```bash
ros2 topic echo --once /joint_states
```

The `name` array contains 14 entries from `left_hip_yaw` to `right_ankle`.
Watch policy switches with:

```bash
ros2 topic echo /microduck/policy_state
```

A settled robot reports something like:

```yaml
data: '{"policy":"standing","upright":true,"tilt_rad":0.0026}'
```

`ground_pick` deliberately lowers the body and can briefly report
`upright:false` before recovering. If you use this field as an RL termination
condition, distinguish intentional low postures from an actual fall.

## 8. Check the full round trip headlessly

Run the live ROS → Isaac → ROS check without opening the three windows:

```bash
./scripts/validate_ros_isaac_e2e.sh
```

The script starts the real headless playground, publishes `kick_left` from ROS,
and waits for JointState, policy, upright, and TF messages to return. A passing
run has all 14 joints, `world → base_link`, a real `kick_left` policy switch,
and JSON reports below `artifacts/isaac/`.

::: details Numbers from the recorded run
The retained run received 317 JointState messages and 316 policy messages and
recorded `standing → kick_left → walking`. Message counts vary with host speed
and run length; they are reference values, not a target.
:::

## 9. Shut everything down cleanly

Stop C, B, then A:

1. publish zero velocity or reset from terminal C;
2. press <kbd>Ctrl</kbd>+<kbd>C</kbd> in terminal B;
3. press <kbd>Ctrl</kbd>+<kbd>C</kbd> in terminal A.

The bridge should report `process has finished cleanly`, without an
`ExternalShutdownException` traceback. If a later launch says a UDP port is in
use, first check whether an earlier duck is still running.

Continue with the [multi-skill playground](/isaac/playground), or start an
[Isaac Lab walking experiment](/isaac/training).
