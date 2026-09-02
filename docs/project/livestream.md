# Livestream guide

The recommended teaching story is:

```text
pinned source -> reproducible conversion -> ROS description
              -> released policy in Isaac -> honest MuJoCo comparison
```

## Before going live

1. Run `./scripts/validate_all.sh` on the Linux/Isaac host.
2. Rehearse RViz and Isaac from the exact desktop session being captured.
3. Keep [recorded results](/reference/results) open as an evidence fallback.
4. Record a short local RViz and Isaac fallback clip after validation and label
   it clearly if used.
5. Confirm the stream is compatible with the [license boundary](./licensing),
   especially if the stream is sponsored or monetized.

## Suggested 25-minute lesson

| Time | Segment | Teaching point |
| ---: | --- | --- |
| 2 min | Boundary | Independent project, pinned upstream, license notice |
| 4 min | Contract | 15 bodies, 14 joints, 61 observations, 14 actions |
| 5 min | ROS 2 | TF, visual/collision layers, interactive joints |
| 4 min | USD | Why opening a stage is not structural validation |
| 6 min | Isaac | 200 Hz physics, 50 Hz policy, follow camera |
| 4 min | Evidence | Smoke parity passed; trajectory/training parity did not |

## RViz commands

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

Use individual sliders for teaching. **Randomize** is a visual smoke test; click
**Center** before moving to the next segment. Enable collision meshes only for
the collision explanation.

## Isaac commands

Start with a standing check:

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_stand.onnx \
  --duration 30 --action-scale 1.0 --follow-camera --viz kit
```

Then walk:

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_walking.onnx \
  --duration 60 --vx 0.3 --action-scale 0.9 --follow-camera --viz kit
```

On the validated host, 60 seconds of simulated GUI playback took roughly three
minutes of wall time. Printed five-second simulation progress matters more than
real-time speed. Stop with Ctrl+C if progress or the UI truly stalls.

## Claims that match the evidence

- The project uses Pollen's public model and policies at pinned commits.
- ROS packaging and Isaac playback are independent community additions.
- The same 61-to-14 policy contract remains finite and upright in both recorded
  smoke scenarios.
- Actuator/contact models are not calibrated for trajectory or training parity.

Avoid “official Isaac version,” “training complete,” “exact physics parity,”
“hardware-ready,” or “ROS controls the robot.”
