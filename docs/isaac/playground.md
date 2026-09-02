# Open the MicroDuck skill playground

Single-policy playback is only a warm-up. The playground loads the released
61→14 ONNX policy family and switches one simulated duck between standing,
walking, sitting, ground pick, ball kicks, and a forward roll. A 70 mm, 15 g
ball is placed beside the selected foot before each kick.

## 1. Prepare the released policies

From the repository root:

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

## 2. Open the playground

```bash
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="The live MicroDuck multi-skill playground in Isaac Lab" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>The playground is ready when the duck and yellow ball appear.</strong>This is a real run. The first Kit launch may take a little longer while extensions load.</figcaption>
</figure>

Use the arrow keys and <kbd>Z</kbd>/<kbd>X</kbd> for forward, yaw, and lateral
velocity. Releasing them returns the command to zero and switches walking back
to standing.

| Key | Action |
| --- | --- |
| <kbd>Y</kbd> | Sit / rise |
| <kbd>G</kbd> | Ground pick |
| <kbd>K</kbd> / <kbd>M</kbd> | Kick with the left / right foot |
| <kbd>R</kbd> | Forward roll |
| <kbd>W</kbd>/<kbd>S</kbd> | Neck pitch command |
| <kbd>A</kbd>/<kbd>D</kbd> | Head pitch command |
| <kbd>Q</kbd>/<kbd>E</kbd> | Head yaw command |
| <kbd>C</kbd>/<kbd>V</kbd> | Head roll command |
| <kbd>H</kbd> | Center the head command |
| <kbd>Backspace</kbd> | Reset the robot and ball |

Missing optional ONNX files are reported as `Skipped`; available skills still
load. A new trick is ignored while another timed skill is mid-motion so the
duck cannot switch from half a roll directly into a kick.

The defaults follow the pinned MicroDuck runtime: walking uses a `0.9` action
scale, the other skills use `1.0`, and head/leg targets use `0.5` / `0.7`
low-pass coefficients. They can be overridden from the CLI, but the defaults
are the useful demo baseline.

## 3. Run a headless smoke test

```bash
./scripts/run_isaac_playground.sh \
  --duration 5 \
  --no-keyboard \
  --headless
```

The run writes `artifacts/isaac/playground_session.json`. It is a playback
record, not evidence that a new policy was trained.

The policies come from Pollen Robotics and were trained by
[microduck_rl](https://github.com/pollen-robotics/microduck_rl) in MuJoCo/mjlab.
This page adds interactive Isaac playback; it does not relabel that upstream
training as Isaac training.

Next, [drive the playground from ROS 2](/ros2/isaac-control) for the complete
three-terminal commands, expected screens, RViz camera controls, and live
round-trip check, or
[train a new walking policy](./training).
