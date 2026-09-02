# Train a walking duck in Isaac Lab

This page runs the repository's native Isaac Lab task instead of replaying a released ONNX file. First validate the full
training pipeline; only then spend hours on a real PPO experiment.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Pipeline check</span><strong>About 10–30 minutes</strong></div>
  <div role="listitem"><span>Full training</span><strong>Hours, depending on GPU</strong></div>
  <div role="listitem"><span>Environment</span><strong>Isaac Sim + Isaac Lab</strong></div>
  <div role="listitem"><span>Outputs</span><strong>Checkpoint, curves, replay image</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>You will complete the whole loop</strong>
  <ul>
    <li>start <code>Isaac-MicroDuck-Velocity-Flat-v0</code>;</li>
    <li>finish five iterations and verify the checkpoint on disk;</li>
    <li>watch the run in TensorBoard;</li>
    <li>reload the newest checkpoint and save a report and image;</li>
    <li>separate “pipeline works” from “policy learned to walk.”</li>
  </ul>
</div>

## The complete route

| Stage | Action | Pass condition |
| --- | --- | --- |
| 1. Preflight | Check the GPU and Isaac Lab launcher | `nvidia-smi` works and `isaaclab.sh` is executable |
| 2. Smoke train | Run 64 environments for 5 iterations | Output reaches `MICRODUCK_TRAIN_STAGE=complete` |
| 3. Inspect files | Find the new run directory | `model_final.pt` and `training_summary.json` exist |
| 4. Full experiment | Increase environments and iterations | Stable trends and sensible replayed motion |
| 5. Replay | Load the checkpoint for 200 steps | JSON and image are saved; motion is inspected |

<div class="md-terminal-map" role="list" aria-label="Terminal roles">
  <div role="listitem"><strong>Terminal A</strong><p>Training process. Keep it visible for stages and errors.</p></div>
  <div role="listitem"><strong>Terminal B</strong><p>TensorBoard, started after training begins.</p></div>
  <div role="listitem"><strong>Replay window</strong><p>Opened after training to inspect actual behavior.</p></div>
</div>

<div class="md-command-steps">
  <strong>Open terminal A first; terminal B can wait</strong>
  <p>Press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd> and <code>cd</code> to the repository root. Terminal A owns preflight and training. After a full run starts, press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> for terminal B and TensorBoard.</p>
</div>

<div class="md-step-kicker"><span>STEP 1</span><strong>Terminal A · Ctrl + Alt + T</strong></div>

## Run the preflight check

The native task does not need ONNX Runtime, but it does need working CUDA and Isaac Lab:

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
nvidia-smi
test -x "$ISAACLAB_DIR/isaaclab.sh" && echo "Isaac Lab launcher: OK"
```

Skip the export when Isaac Lab is at `~/rlgpu_ws/IsaacLab`. Close other Isaac windows before the first run.

<div class="md-checkpoint">
  <strong>Continue when preflight passes</strong>
  <p>The GPU is visible and the terminal prints <code>Isaac Lab launcher: OK</code>.</p>
</div>

<div class="md-step-kicker"><span>STEP 2</span><strong>Terminal A · smoke test first</strong></div>

## Run five training iterations

```bash
./scripts/train_isaac_velocity.sh
```

The prompt does not return while training runs. Do not start the command again
while terminal output continues or the GPU is active. Creating 64 environments
can hold one stage for several minutes on the first launch.

The default is 64 environments for 5 iterations. Startup may take a while. The stage markers appear in this order:

```text
MICRODUCK_TRAIN_STAGE=creating_environment
MICRODUCK_TRAIN_STAGE=wrapping_environment
MICRODUCK_TRAIN_STAGE=creating_runner
MICRODUCK_TRAIN_STAGE=learning
MICRODUCK_TRAIN_STAGE=saving
MICRODUCK_TRAIN_STAGE=complete
```

The run is complete only when the final marker appears. Opening an Isaac window or printing one PPO table is not enough.

::: warning Five iterations do not teach a gait
This run checks task registration, simulation, PPO updates, and checkpoint saving. It is a pipeline test, not a trained
walking policy.
:::

For the smallest configuration already exercised by this project:

```bash
MICRODUCK_TRAIN_ENVS=16 \
MICRODUCK_TRAIN_ITERATIONS=1 \
./scripts/train_isaac_velocity.sh
```

<div class="md-checkpoint">
  <strong>Training process passed</strong>
  <p>No traceback occurred, and the run ended with <code>MICRODUCK_TRAIN_STAGE=complete</code>. An OOM or interrupted save is a failed run.</p>
</div>

<div class="md-step-kicker"><span>STEP 3</span><strong>Terminal A · inspect the files</strong></div>

## Verify the checkpoint

Each run creates a timestamped directory:

```text
work/isaac_training/logs/rsl_rl/microduck_velocity_flat/YYYY-MM-DD_HH-MM-SS/
```

Find the newest checkpoint:

```bash
find work/isaac_training/logs/rsl_rl/microduck_velocity_flat \
  -name model_final.pt -type f -print | sort | tail -n 1
```

The same run directory should contain:

```text
model_final.pt
training_summary.json
params/env.yaml
params/agent.yaml
```

`training_summary.json` records the environment count, iterations, device, elapsed time, and checkpoint path. It proves
the run saved successfully; it does not prove a useful gait.

<div class="md-checkpoint">
  <strong>File check passed</strong>
  <p><code>model_final.pt</code> and <code>training_summary.json</code> are non-empty and belong to the same new run.</p>
</div>

<div class="md-step-kicker"><span>STEP 4</span><strong>Terminal A + Terminal B</strong></div>

## Start a full experiment

Scale from 64 to 256 or 512 environments first. Use the larger example only when VRAM and the smoke run are stable:

```bash
MICRODUCK_TRAIN_ENVS=1024 \
MICRODUCK_TRAIN_ITERATIONS=4000 \
./scripts/train_isaac_velocity.sh
```

After training reaches `learning`, leave terminal A running. Press
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> for terminal B, `cd` to the repository
root, and run:

```bash
tensorboard --logdir work/isaac_training/logs/rsl_rl/microduck_velocity_flat
```

Terminal B prints a URL, usually `http://localhost:6006/`. <kbd>Ctrl</kbd>-click
it or paste it into a browser on the same Ubuntu computer. TensorBoard keeps
running; press <kbd>Ctrl</kbd>+<kbd>C</kbd> in terminal B when finished.

Inspect long-term reward trends, episode length, falls, velocity tracking, and action-rate penalties. A rising scalar can
still hide a policy that learned to shake. Reduce `MICRODUCK_TRAIN_ENVS` after an OOM; replay the policy before adding
more iterations when the motion looks wrong.

<div class="md-step-kicker"><span>STEP 5</span><strong>After training · repository root</strong></div>

## Replay the newest checkpoint

```bash
./scripts/play_isaac_velocity.sh
```

The wrapper selects the newest `model_final.pt`, runs one environment for 200 steps, and writes:

```text
artifacts/isaac/velocity_playback.json
artifacts/isaac/velocity_playback.png
```

The terminal should finish with:

```text
MICRODUCK_PLAYBACK_STAGE=inference-complete
MICRODUCK_PLAYBACK_STAGE=screenshot-complete
MICRODUCK_PLAYBACK_STAGE=complete
```

<div class="md-result-label">REAL RUN · AFTER CHECKPOINT REPLAY</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-training-playback.webp" alt="Replay of a one-iteration native Isaac Lab MicroDuck checkpoint" width="960" height="720" loading="lazy"></div>
  <figcaption><strong>This frame proves that the checkpoint reloads and renders.</strong>It came from one PPO iteration, so the awkward pose is expected. Judge a full experiment from continuous motion, curves, and repeated replays.</figcaption>
</figure>

Select a checkpoint or extend replay:

```bash
./scripts/play_isaac_velocity.sh --checkpoint /path/to/model_final.pt
MICRODUCK_PLAY_STEPS=1000 ./scripts/play_isaac_velocity.sh
```

Choose one replay form at a time. Wait for the current GUI to exit, or press
<kbd>Ctrl</kbd>+<kbd>C</kbd> before changing commands. Two Isaac replays should
not compete for the GPU.

Replay checks finite observations, actions, and rewards, both foot-contact sensors, and image capture. It does not export
ONNX or automatically grade the gait.

## What does this task learn?

`Isaac-MicroDuck-Velocity-Flat-v0` currently contains:

- 14 joint-position actions;
- a 61-value observation in the released policy order;
- planar velocity and four head commands;
- stance, slip, velocity/head tracking, fall-reset, and action-smoothing terms;
- pushes plus mass and friction randomization;
- an RSL-RL PPO actor and critic.

Six body-command slots remain in the 61-value interface, but this first task has no body-pose tracking reward. Kicking,
sit/stand, ground pick, and roulade remain released policies in the [playground](./playground).

## Common problems

| Symptom | First action |
| --- | --- |
| Isaac Lab launcher missing | Fix `ISAACLAB_DIR` |
| CUDA out of memory | Reduce `MICRODUCK_TRAIN_ENVS` to 16 or 64 |
| Iterations printed, no checkpoint | Confirm the run reached `saving` and `complete` |
| TensorBoard shows no curves | Point it at `microduck_velocity_flat` and refresh runs |
| Replay finds no checkpoint | Complete training or pass the correct `--checkpoint` path |
| Reward rises but motion shakes | Inspect replay and the reward design before adding iterations |

## Can this checkpoint go directly onto hardware?

No. The task uses an implicit-PD approximation and does not reproduce all BAM XL330 electrical, friction, saturation,
battery, backlash, or communication-delay behavior. Hardware deployment requires separate actuator modeling, export,
safety, domain randomization, and physical validation.

<div class="md-page-complete">
  <strong>The training loop is now complete.</strong>
  <p>You moved from preflight to smoke training, checkpoint inspection, TensorBoard, and replay. Change one experiment variable at a time and keep each run directory.</p>
</div>

<div class="md-next-grid">
  <a class="md-next-card" href="/microduck-ros2-isaac/isaac/custom-environment"><span>BUILD NEXT</span><strong>Design another training task →</strong><p>Define the scene, success condition, reward, termination, and replay gate.</p></a>
  <a class="md-next-card" href="/microduck-ros2-isaac/isaac/playground"><span>COMPARE SKILLS</span><strong>Return to the released playground →</strong><p>Study existing kick, recovery, and sit/stand behavior.</p></a>
</div>
