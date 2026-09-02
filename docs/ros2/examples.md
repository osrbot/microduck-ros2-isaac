# Try three ROS 2 examples

No real robot needed. Start with a moving duck in RViz. Then let ROS 2 control
the duck in Isaac Sim. The examples save you from typing long chains of
`ros2 topic pub` commands.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>RViz demo</span><strong>About 5 minutes</strong></div>
  <div role="listitem"><span>Isaac round trip</span><strong>15–25 minutes</strong></div>
  <div role="listitem"><span>Hardware</span><strong>Not required</strong></div>
  <div role="listitem"><span>Result</span><strong>Motion, keyboard control, and live state</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>Try them in this order</strong>
  <ul>
    <li>run the RViz-only demo to check joints and TF;</li>
    <li>run the Isaac showcase when that environment is ready;</li>
    <li>take keyboard control and inspect the live ROS topics.</li>
  </ul>
</div>

## Pick an example

| Goal | Entry point | Isaac Sim required |
| --- | --- | --- |
| Inspect the model and move all 14 joints | `view_microduck.launch.py use_gui:=true` | No |
| Play a nod, head turn, and stepping animation | `rviz_motion_demo.launch.py` | No |
| Walk, turn, kick, pick, sit, and stand automatically | `isaac_showcase.launch.py` | Yes |
| Drive the playground from the keyboard | `microduck_teleop` | Yes |

<div class="md-command-steps">
  <strong>Start in terminal A</strong>
  <p>Press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd>, then <code>cd</code> to the repository root. Run one launch at a time. Press <kbd>Ctrl</kbd>+<kbd>C</kbd> before switching to another example.</p>
</div>

Build the three ROS 2 packages first:

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install \
  --packages-select microduck_description microduck_control_bridge microduck_examples
source install/setup.bash
cd ..
```

A clean build ends with `Summary: 3 packages finished`. Fix any failed package before launching an example.

<div class="md-checkpoint">
  <strong>The examples are ready!</strong>
  <p><code>ros2 pkg prefix microduck_examples</code> returns this workspace's install path.</p>
</div>

## Example 1: an RViz-only motion demo

```bash
ros2 launch microduck_examples rviz_motion_demo.launch.py
```

The default `showcase` routine turns and nods the head, alternates the legs,
and finishes with a bow. It loops so you can inspect the model and all 14 joint
connections.

<div class="md-result-label">REAL RUN · RVIZ-ONLY EXAMPLE</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros2-rviz-motion-demo.webp" alt="MicroDuck lifting one leg during the ROS 2 RViz motion example" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>A real frame from the example.</strong> The right leg is raised while the left foot supports the pose; RobotModel and TF are both healthy.</figcaption>
</figure>

To change routines, press <kbd>Ctrl</kbd>+<kbd>C</kbd>, wait for the current launch
to exit, and run **one** command below. Do not paste all three at once; the first
launch blocks until it is stopped.

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

<div class="md-checkpoint">
  <strong>The RViz demo works!</strong>
  <p>The sequence loops, head and legs move in order, and no joint-name or limit error appears. Isaac is not involved.</p>
</div>

## Example 2: let ROS 2 control Isaac

Stop the RViz-only example with <kbd>Ctrl</kbd>+<kbd>C</kbd> if it is still
running. Return terminal A to the repository root and start the playground:

```bash
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

After the duck and yellow ball appear, leave terminal A running. Press
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> to open terminal B, `cd` to the
repository root, and run:

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

<div class="md-result-label">REAL RUN · ROS → ISAAC → RVIZ</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-live.webp" alt="RViz displaying live Isaac telemetry for MicroDuck" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>Isaac and RViz show the same simulation run.</strong> ROS sends commands and receives the live state.</figcaption>
</figure>

To try a shorter sequence, stop the current one in terminal B with
<kbd>Ctrl</kbd>+<kbd>C</kbd>, then run **one** command below:

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

## Example 3: grab the keyboard

With Isaac and the bridge running, press
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> to open terminal C:

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run microduck_control_bridge microduck_teleop
```

Use `W/S` to move, `A/D` to turn, `Q/E` to sidestep, `Y` to sit or stand,
`G` to pick, `K/M` to kick, `R` to roll, `X` to stop, and `0` to reset.

## Watch and save the ROS topics

While either Isaac example is running, open another terminal. Each command
below streams output, so run **one at a time**. Press <kbd>Ctrl</kbd>+<kbd>C</kbd>
before trying the next:

```bash
ros2 topic hz /joint_states
ros2 topic echo /microduck/policy_state
ros2 run tf2_ros tf2_echo world base_link
```

`topic hz` should keep printing a rate, `policy_state` should show `standing`,
`walking`, or a skill name, and `tf2_echo` should stream the
`world → base_link` transform.

Record a run for later inspection:

```bash
mkdir -p work/rosbags
ros2 bag record -o work/rosbags/microduck_showcase \
  /cmd_vel /microduck/behavior /microduck/head_command \
  /joint_states /microduck/policy_state /microduck/upright /tf /tf_static
```

Press <kbd>Ctrl</kbd>+<kbd>C</kbd> after the run. Wait for the recorder to close
cleanly and return to the prompt, then inspect
`work/rosbags/microduck_showcase/`. Closing the terminal directly can interrupt
the bag finalization.

<div class="md-page-complete">
  <strong>You tried the whole ROS 2 set!</strong>
  <p>You ran the motion examples and learned how to drive and record them. The next page opens the included MicroDuck USD in Isaac Sim.</p>
</div>
