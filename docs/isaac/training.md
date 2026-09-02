# Train a walking duck in Isaac Lab

This path does not replay an existing ONNX file. It launches this repository's
native Isaac Lab task, clones many MicroDuck environments, and lets PPO learn
from reward feedback. Start with five iterations to check the pipeline before
spending thousands of iterations on an experiment.

## What the task contains

`Isaac-MicroDuck-Velocity-Flat-v0` focuses on flat-ground velocity and head
pose control:

- 14 joint-position actions;
- a 61-value observation in the released policy order;
- planar velocity, four head commands, and six body-command slots retained for
  the 61-value interface;
- biped single-stance, foot-slip, velocity/head tracking, fall resets, pushes,
  and mass/friction randomization;
- curricula that introduce more standing samples, stronger action smoothing,
  and wider head commands after gait bootstrap, plus a 15% turn-in-place bucket;
- an RSL-RL PPO actor and critic.

Keeping the 61-value contract makes later export and runtime comparison easier.
This remains an independent Isaac teaching task, not a replacement for the BAM
actuator and sim-to-real recipe in upstream `microduck_rl`.

The body-command slot is sampled only over a tiny range and has no body-pose
tracking reward in this first task. It preserves the interface; it is not a
claimed learned body-pose skill. Kick, sit/stand, ground-pick, and roulade stay
in the [multi-skill playground](./playground) as separate released policies,
while this native task learns a new velocity-and-head policy.

## 1. Run a five-iteration smoke training

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/train_isaac_velocity.sh
```

The default is 64 environments for 5 iterations. Logs and checkpoints are
written below:

```text
work/isaac_training/logs/rsl_rl/microduck_velocity_flat/
```

Finishing five iterations proves the registration, simulation, PPO update, and
checkpoint path runs. It does not produce a useful gait yet.

To reproduce the smallest configuration already exercised by this project, run
16 environments for one iteration:

```bash
MICRODUCK_TRAIN_ENVS=16 \
MICRODUCK_TRAIN_ITERATIONS=1 \
./scripts/train_isaac_velocity.sh
```

The recorded run collected 384 steps at about 530 steps/s, completed one PPO
update, and wrote `model_final.pt` on an RTX 4080 SUPER. Treat those numbers as
one host reference, not a benchmark. The important result is a clean finish and
a real checkpoint on disk.

## 2. Start a real experiment

Increase the budget only after the smoke run is clean:

```bash
MICRODUCK_TRAIN_ENVS=1024 \
MICRODUCK_TRAIN_ITERATIONS=4000 \
./scripts/train_isaac_velocity.sh
```

Watch total reward, velocity tracking, episode length, falls, and action-rate
terms in TensorBoard. Also view the checkpoint: a rising scalar can still hide
a policy that learned to shake instead of walk.

```bash
tensorboard --logdir work/isaac_training/logs/rsl_rl/microduck_velocity_flat
```

## 3. Play the newest checkpoint

```bash
./scripts/play_isaac_velocity.sh
```

The wrapper selects the newest `model_final.pt`, runs one environment for 200
steps, and saves both a machine-readable report and a clean 960×720 frame:

```text
artifacts/isaac/velocity_playback.json
artifacts/isaac/velocity_playback.png
```

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-training-playback.webp" alt="Clean playback of a one-iteration native Isaac Lab MicroDuck checkpoint" width="960" height="720" loading="lazy"></div>
  <figcaption><strong>This frame proves that the checkpoint reloads and renders.</strong>It came from a single PPO iteration, so an awkward pose is expected; a saved image is not evidence of a learned gait.</figcaption>
</figure>

Choose a checkpoint explicitly with `--checkpoint /path/to/model_final.pt`, or
change the run length with `MICRODUCK_PLAY_STEPS`. Playback validates finite
observations, actions, rewards, both foot-contact sensors, and image capture.
It does not export ONNX and it does not turn a five-iteration smoke checkpoint
into a walking policy. Train long enough, then judge the motion as well as the
numbers.

## Can this checkpoint go directly onto hardware?

No such claim is made. The current Isaac task uses an implicit-PD approximation
and does not reproduce all BAM XL330 electrical, friction, saturation, battery,
backlash, and communication-delay behavior. It is useful for Isaac Lab learning
and reward experiments; hardware deployment requires separate model, export,
safety, and physical validation gates.

Continue with [build another training task](./custom-environment).
