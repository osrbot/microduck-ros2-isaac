# Play with MicroDuck in Isaac Sim

One walking policy was just the warm-up. Here the duck can stand, walk, sit,
pick from the ground, kick a ball, and roll forward. The playground uses the
ready-made 61→14 ONNX policies. It puts a 70 mm, 15 g ball beside the foot before
each kick.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Time</span><strong>15–25 minutes</strong></div>
  <div role="listitem"><span>Controls</span><strong>Keyboard or ROS 2</strong></div>
  <div role="listitem"><span>Moves</span><strong>Walking + five tricks</strong></div>
  <div role="listitem"><span>Result</span><strong>A duck you can control and reset</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>Start with the window. Try headless later.</strong>
  <ul>
    <li>check that every ready-made policy loads;</li>
    <li>walk, turn, and finish at least two moves;</li>
    <li>reset the robot and ball;</li>
    <li>run a five-second test without the window.</li>
  </ul>
</div>

<div class="md-command-steps">
  <strong>You only need Terminal A</strong>
  <p>Press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd> and <code>cd</code> to the repository root. Do not paste the headless command into the same terminal while the GUI playground is running; stop the GUI with <kbd>Ctrl</kbd>+<kbd>C</kbd> first.</p>
</div>

## 1. Get the ready-made moves

From the repository root:

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

You only need to prepare these files once. Startup prints `Loaded` or `Skipped` for each policy; if every base policy is
skipped, fix the download before testing keyboard controls.

## 2. Open the playground

```bash
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

The prompt does not return while the playground runs. Terminal output reports
each policy as `Loaded` or `Skipped`, then the Isaac window opens. The first Kit
extension load may be slow; do not launch a duplicate process.

<div class="md-result-label">REAL RUN · PLAYGROUND OPEN</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="The live MicroDuck multi-skill playground in Isaac Lab" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>The playground is ready when the duck and yellow ball appear.</strong>This is a real run. The first Kit launch may take a little longer while extensions load.</figcaption>
</figure>

Click once inside the **Isaac viewport** so it owns keyboard focus. Keys will not
reach the duck while focus remains in Terminal or a side panel. Use the arrow
keys and <kbd>Z</kbd>/<kbd>X</kbd> for forward, yaw, and lateral
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

<div class="md-checkpoint">
  <strong>The controls work!</strong>
  <p>Velocity returns to standing when keys are released, at least two skills finish, and <kbd>Backspace</kbd> resets both robot and ball. Rejecting a new skill while another is busy is a safety feature.</p>
</div>

<div class="md-result-label">REAL RUN · WALK, TURN, AND SIT</div>

<div class="md-runtime-grid md-runtime-grid-three">
  <figure class="md-doc-figure">
    <img src="/images/isaac-action-walk.webp" alt="MicroDuck walking forward in the Isaac skill playground" width="1200" height="750" loading="lazy">
    <figcaption><strong>Walk.</strong>A velocity command switches the active policy from standing to walking.</figcaption>
  </figure>
  <figure class="md-doc-figure">
    <img src="/images/isaac-action-turn.webp" alt="MicroDuck turning in the Isaac skill playground" width="1200" height="750" loading="lazy">
    <figcaption><strong>Turn.</strong>The follow camera rotates with the duck while the yaw command is active.</figcaption>
  </figure>
  <figure class="md-doc-figure">
    <img src="/images/isaac-action-sit.webp" alt="MicroDuck performing the sit action in the Isaac skill playground" width="1200" height="750" loading="lazy">
    <figcaption><strong>Sit.</strong>Press <kbd>Y</kbd> to lower the body; press it again after the action finishes to rise.</figcaption>
  </figure>
</div>

## 3. Run a quick test without the window

Return to terminal A, press <kbd>Ctrl</kbd>+<kbd>C</kbd> to close the GUI, and wait
for the prompt before running:

```bash
./scripts/run_isaac_playground.sh \
  --duration 5 \
  --no-keyboard \
  --headless
```

The run writes `artifacts/isaac/playground_session.json`. It is a playback
record, not evidence that a new policy was trained.

```bash
test -s artifacts/isaac/playground_session.json \
  && echo "Playground report: OK"
```

`Playground report: OK` confirms that the five-second run wrote a non-empty
report.

The policies come from Pollen Robotics and were trained by
[microduck_rl](https://github.com/pollen-robotics/microduck_rl) in MuJoCo/mjlab.
This page adds interactive Isaac playback; it does not relabel that upstream
training as Isaac training.

<div class="md-page-complete">
  <strong>The duck is ready to play!</strong>
  <p>You changed moves, reset the duck and ball, and saved a headless report. The next page controls this playground from ROS 2.</p>
</div>
