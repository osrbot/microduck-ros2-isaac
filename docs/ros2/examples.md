# ROS 2 examples for a simulation-first MicroDuck

No physical robot is required. Start with joints and TF in RViz, then let ROS 2
command the policies running in Isaac. These examples replace long chains of
manual `ros2 topic pub` commands with repeatable programs.

## Pick an example

| Goal | Entry point | Isaac Sim required |
| --- | --- | --- |
| Inspect the model and move all 14 joints | `view_microduck.launch.py use_gui:=true` | No |
| Play a nod, head turn, and stepping animation | `rviz_motion_demo.launch.py` | No |
| Walk, turn, kick, pick, sit, and stand automatically | `isaac_showcase.launch.py` | Yes |
| Drive the playground from the keyboard | `microduck_teleop` | Yes |

Build the three ROS 2 packages first:

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install \
  --packages-select microduck_description microduck_control_bridge microduck_examples
source install/setup.bash
cd ..
```

## Example 1: an RViz-only motion demo

```bash
ros2 launch microduck_examples rviz_motion_demo.launch.py
```

The default `showcase` routine turns and nods the head, alternates the legs,
and finishes with a bow. It loops so you can inspect the model and all 14 joint
connections.

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros2-rviz-motion-demo.webp" alt="MicroDuck lifting one leg during the ROS 2 RViz motion example" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>A real frame from the example.</strong> The right leg is raised while the left foot supports the pose; RobotModel and TF are both healthy.</figcaption>
</figure>

Choose a shorter routine or change its speed:

```bash
ros2 launch microduck_examples rviz_motion_demo.launch.py routine:=hello
ros2 launch microduck_examples rviz_motion_demo.launch.py \
  routine:=walk speed:=1.5
ros2 launch microduck_examples rviz_motion_demo.launch.py repeat:=false
```

The available routines are `hello`, `walk`, and `showcase`. Every example pose
is checked against the URDF joint limits.

::: warning This is joint animation, not physics
The node publishes `JointState` for RViz. It has no gravity, contacts,
controller, or learned policy, so it cannot show whether the robot is
dynamically stable.
:::

## Example 2: an automatic ROS-to-Isaac showcase

Start the Isaac playground in terminal A:

```bash
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

After the duck and yellow ball appear, run this in terminal B:

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 launch microduck_examples isaac_showcase.launch.py
```

The example waits for real Isaac telemetry and then performs:

```text
reset → look around → walk → turn → left kick → right kick
      → ground pick → sit → stand → reset
```

RViz displays the 14 joint positions and `world → base_link` pose returned by
Isaac. The terminal also reports each step, policy transition, and upright
state.

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-live.webp" alt="RViz displaying live Isaac telemetry for MicroDuck" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>Isaac and RViz show the same simulation run.</strong> ROS sends commands and receives the live state.</figcaption>
</figure>

Choose a shorter sequence or change playback speed:

```bash
ros2 launch microduck_examples isaac_showcase.launch.py sequence:=walk
ros2 launch microduck_examples isaac_showcase.launch.py sequence:=skills
ros2 launch microduck_examples isaac_showcase.launch.py \
  sequence:=showcase speed:=0.5
```

Use `speed` between `0.0` and `1.0` to slow the sequence down. Values above
`1.0` are rejected because the learned kick, pick, sit, and stand policies have
fixed real-time durations. If telemetry does not arrive within 30 seconds, the
example exits with an error instead of pretending that the commands ran.

## Example 3: take the keyboard

With Isaac and the bridge running, open another terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run microduck_control_bridge microduck_teleop
```

Use `W/S` to move, `A/D` to turn, `Q/E` to sidestep, `Y` to sit or stand,
`G` to pick, `K/M` to kick, `R` to roll, `X` to stop, and `0` to reset.

## Inspect and record the ROS graph

While either Isaac example is running:

```bash
ros2 topic hz /joint_states
ros2 topic echo /microduck/policy_state
ros2 run tf2_ros tf2_echo world base_link
```

Record a run for later inspection:

```bash
mkdir -p work/rosbags
ros2 bag record -o work/rosbags/microduck_showcase \
  /cmd_vel /microduck/behavior /microduck/head_command \
  /joint_states /microduck/policy_state /microduck/upright /tf /tf_static
```

Continue with [manual ROS 2 commands](/ros2/isaac-control) or move on to the
[Isaac Lab training task](/isaac/training).
