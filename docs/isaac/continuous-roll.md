---
title: Train the duck to keep rolling
description: Warm-start a policy, run a short training test, tune the rewards, and evaluate continuous forward rolls.
prev:
  text: Train a walking policy
  link: /isaac/training
next:
  text: Parameters and rewards
  link: /isaac/roll-parameters
---

<script setup>
import RollShowcase from '../.vitepress/theme/RollShowcase.vue'
</script>

# Train the duck to keep rolling

Watch the result first. Then work through the steps that got us there.

<RollShowcase />

This tutorial takes you through **setup → starting from an existing policy → short training runs → replay and diagnosis → reward tuning → checkpoint selection**.
The commands, parameter choices, and intermediate experiments all follow that same route.

We initialize the actor and observation normalizer from Pollen Robotics' `roulade.onnx`, then use PPO to improve continuous forward rolling.
In the recorded batch evaluation, eight slightly different starting poses each produced 39 consecutive rolls in 50 seconds, with no resets. Mean absolute lateral displacement was about 0.70 m.
This is a flat-ground simulation case study. Direction control and recovery from disturbances are useful next steps.

## Where should you start?

| What you want to do | Where to go |
| --- | --- |
| Run training and replay yourself | Continue on this page |
| Understand the parameter choices | [Parameters and rewards](./roll-parameters) |
| Find out what to check when training stalls | [Three rounds of debugging](./roll-debugging) |
| Compare checkpoints, evaluate a batch, and record video | [Evaluation and video export](./roll-validation) |

## 1. Get the environment ready {#setup}

You need a Linux computer with an NVIDIA GPU that can run Isaac Sim and Isaac Lab. You can read the tutorial and watch the videos on a Mac; run the training commands in the Linux simulation environment.
If you have not set it up yet, follow [installation](../guide/installation), then complete a [short walking-policy training run](./training).
This case does not require ROS 2 nodes. You can connect ROS 2 once the policy is working well.

The recorded setup used Ubuntu 24.04, an RTX 4080 SUPER with 16 GB VRAM, Isaac Sim 6.0.1, Isaac Lab 3.0.0 beta 2, and RSL-RL 5.0.1.
See [Tested setup](../reference/environment) for the version and driver details. On another setup, start with the small test below.

::: info Check that your code matches the tutorial
This walkthrough uses the `--full-roll-v2` and `--straight-roll` implementations included with it. Older checkouts may not have these options.
Before training, check that the following file exists and that the command help lists the required options.
:::

### Terminal A: repository root

If you already have the repository, use that checkout. For a first download, follow the [installation page](../guide/installation). Replace the first path with your own Isaac Lab directory:

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
nvidia-smi
test -x "$ISAACLAB_DIR/isaaclab.sh"
test -f source/microduck_isaac_lab/microduck_isaac_lab/tasks/velocity/full_roll_env_cfg.py
"$ISAACLAB_DIR/isaaclab.sh" -p scripts/train_isaac_velocity.py --help
```

You should see GPU information and help entries for `--full-roll-v2`, `--straight-roll`, and `--resume-checkpoint`.
The `test` commands are silent; check their exit status. If either fails, fix the path or get the matching code before moving on.

Fetch the pinned upstream policy and make the project's ONNX Runtime available to Isaac's Python:

```bash
bash scripts/fetch_upstream.sh
bash scripts/setup_isaac_python_env.sh
export PYTHONPATH="$PWD/work/isaac_python_pkgs${PYTHONPATH:+:$PYTHONPATH}"
test -s reference/microduck/policies/roulade.onnx
"$ISAACLAB_DIR/isaaclab.sh" -p -c \
  'import onnx, onnxruntime, torch; import importlib.metadata as m; print("torch", torch.__version__, "rsl-rl", m.version("rsl-rl-lib"), "onnx", onnx.__version__, "ort", onnxruntime.__version__)'
```

`onnx` reads the network so we can copy its weights; `onnxruntime` runs the original ONNX policy directly. They are separate packages.
`setup_isaac_python_env.sh` only installs the project's local ONNX Runtime dependency. If `onnx` or RSL-RL is missing, install the matching dependency in the active Isaac Lab Python environment, then repeat the check.
A successful import in the system Python does not check Isaac's Python environment.

`fetch_upstream.sh` uses the fixed commits in `upstream.lock`. It stops if an existing reference checkout has uncommitted changes; preserve your changes before continuing.
See [Licensing](../project/licensing) for the robot model and policy sources.

## 2. Create an experiment directory and a time limit

Run these commands in the same terminal. The later steps reuse these variables:

```bash
roll_session="work/isaac_training/roll-tutorial-$(date +%Y%m%d-%H%M%S)"
roll_evidence="artifacts/isaac/$(basename "$roll_session")"
mkdir -p "$roll_session" "$roll_evidence"
roll_deadline=$(date -u -d '+120 minutes' +%Y-%m-%dT%H:%M:%S+00:00)
printf 'Experiment directory: %s\nOverall deadline: %s\n' "$roll_session" "$roll_deadline"
```

`date -d` uses the Ubuntu / GNU date syntax. Set the overall deadline once and keep it when retrying; do not add another 120 minutes each time.
Use `run_before_deadline.py` for both training and replay. It enforces a per-stage time limit and the overall deadline, with time reserved for shutdown.
The 120 minutes are a maximum budget. Finish early when the result meets your target.

## 3. Start with just five training iterations

Use 64 environments to check warm-starting, simulation, PPO updates, and file output. `--full-roll-v2` selects the full-turn rewards and the corrected reset height.

```bash
MICRODUCK_TRAIN_ENVS=64 MICRODUCK_TRAIN_ITERATIONS=5 \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 600 \
  --status "$roll_evidence/smoke-status.json" -- \
  bash scripts/train_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --viz none \
    --init-policy-onnx reference/microduck/policies/roulade.onnx \
    --log-root "$roll_session/smoke"
```

The script prints `MICRODUCK_RUN_DIR=...` at startup. Keep that path. You should then see these stages:

```text
MICRODUCK_TRAIN_STAGE=creating_environment
MICRODUCK_TRAIN_STAGE=creating_runner
MICRODUCK_TRAIN_STAGE=loading_roll_actor
MICRODUCK_ROLL_WARM_START_SHA256=...
MICRODUCK_TRAIN_STAGE=learning
MICRODUCK_TRAIN_STAGE=saving
MICRODUCK_TRAIN_STAGE=complete
```

The run directory should contain `model_final.pt`, `training_summary.json`, `params/env.yaml`, and `params/agent.yaml`.
The source policy used here has SHA-256 `3d60da08fc13f29c1b57f41977aa898132c0d60042100149d8e775affcbca32b`.
Compare it with `warm_start.sha256` in your summary to check that you started from the same weights.

The first launch can take a while. Watch for stage changes instead of starting a second process. If you run out of VRAM, reduce the environment count to 16 first.
Five iterations check the training pipeline. The next replay tells you what the policy actually does.

## 4. Replay the model you just saved

Replace `RUN_TIMESTAMP` with the run directory printed in the terminal. Specify the checkpoint explicitly so you do not load another experiment by mistake:

```bash
roll_checkpoint="$roll_session/smoke/RUN_TIMESTAMP/model_final.pt"
test -s "$roll_checkpoint" && \
MICRODUCK_PLAY_STEPS=1500 MICRODUCK_PLAY_TIMEOUT=240 \
MICRODUCK_PLAY_OUTPUT="$roll_evidence/smoke-play.json" \
MICRODUCK_PLAY_SCREENSHOT="$roll_evidence/smoke-play.png" \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 260 \
  --status "$roll_evidence/smoke-play-status.json" -- \
  bash scripts/play_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --viz none \
    --arena-half-width 25 --checkpoint "$roll_checkpoint" \
    --video "$roll_evidence/smoke-play.mp4" \
    --trace "$roll_evidence/smoke-trace.json"
```

At this control rate, 1500 steps cover 30 seconds of simulation. The script records a follow camera and finishes with `MICRODUCK_PLAYBACK_STAGE=complete`.
Watch the MP4 for the start, full turns, and continuity. Then check `completed_forward_turns`, `max_consecutive_forward_turns`, and `done_count` in the JSON report.
If the duck never completes a full turn, go to the [debugging walkthrough](./roll-debugging) before simply adding more iterations.

## 5. Once the pipeline works, try a short training run

The recorded experiment used 1024 parallel environments. With less VRAM, increase the count gradually. Changing it also changes the amount of data collected per update, so your learning curve may differ.
For a **new short experiment**, start a fresh run of up to 300 updates, capped at 15 minutes.
This command uses the corrected reset height. The historical first-round initialization problem is explained on the debugging page.

```bash
MICRODUCK_TRAIN_ENVS=1024 MICRODUCK_TRAIN_ITERATIONS=300 \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 900 \
  --status "$roll_evidence/roll-status.json" -- \
  bash scripts/train_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --viz none \
    --init-policy-onnx reference/microduck/policies/roulade.onnx \
    --log-root "$roll_session/roll"
```

This starts again from the original actor. To continue a previous run, pass `--resume-checkpoint` explicitly; see the [direction-training example](./roll-debugging#direction-training).
A checkpoint is saved roughly every 100 updates. Once the training segment ends, replay the candidates before deciding whether to continue.
Avoid older long-run wrapper commands that do not set an explicit iteration budget.

### Terminal B: watch the training curves

Start TensorBoard from the same repository. Replace `YOUR_ROLL_TUTORIAL_DIRECTORY` with the experiment directory printed in terminal A:

```bash
tensorboard --logdir work/isaac_training/YOUR_ROLL_TUTORIAL_DIRECTORY
```

Open the local address printed by TensorBoard. In Scalars, look for groups such as `Episode_Reward`, `Loss`, and `Train`; exact tags depend on the RSL-RL version.
Start with the full-turn reward terms, episode length, action-smoothness penalty, and learning rate. Compare them with a replay of the same checkpoint.
When the reward definition changes, raw total rewards are no longer directly comparable across runs.

If the duck keeps rolling but drifts sideways, work on direction. If it still cannot complete a turn, check resets, the action interface, and the progress reward first.
This recorded debugging session finished early within the 120-minute budget: about 24 minutes had elapsed when the summary was written. It used a warm-started policy; measure the time needed for your own hardware and starting policy.

## What should you have by now?

- A parameter snapshot and a checkpoint with a known source.
- A replay video that opens correctly.
- A report of full turns, consecutive turns, resets, and displacement.
- A clear next step: complete the first turn, reduce drift, or move on to final evaluation.

The next page connects those observations to the parameters, starting with control frequency and reset height, then moving on to rewards and PPO.
