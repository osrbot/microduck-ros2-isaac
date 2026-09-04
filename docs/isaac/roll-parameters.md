---
title: Continuous rolling — parameters and rewards
description: Understand the policy interface, inherited settings, tuning choices, and evaluation thresholds.
prev:
  text: Train the duck to keep rolling
  link: /isaac/continuous-roll
next:
  text: Three rounds of debugging
  link: /isaac/roll-debugging
---

# Parameters and rewards

Where do these numbers come from? Which one should you change when the motion looks wrong?
Use this order: **check the model interface and reset → make the reward match the goal → inspect short runs → tune the optimizer**.
If the duck starts inside the floor, a different learning rate is unlikely to help.

## 1. Find the configuration that actually runs

| File or entry point | What it controls |
| --- | --- |
| `tasks/velocity/velocity_env_cfg.py` | Model, joint actions, 61-value observation, and simulation time step |
| `tasks/velocity/continuous_roll_env_cfg.py` | Rolling command interface, basic termination rules, and early configuration |
| `tasks/velocity/full_roll_env_cfg.py` | Full-turn rewards, corrected resets, and direction tuning for this case |
| `tasks/velocity/agents/rsl_rl_ppo_cfg.py` | Baseline PPO networks and optimization settings |
| `scripts/train_isaac_velocity.py` | Command-line options, overrides, warm-starting, and resuming |
| `roll_metrics.py` | Independent orientation tracking and full-turn counting |

The first four files are under `source/microduck_isaac_lab/microduck_isaac_lab/`. So is `roll_metrics.py`.
With `--full-roll-v2`, the training script also overrides `clip_actions=None`, `save_interval=100`, `learning_rate=1e-4`, and `desired_kl=0.005`.
The saved **`params/env.yaml` and `params/agent.yaml` are therefore the configuration snapshots for that run**.
If you change any of those four settings, check the script's overrides too; editing only the base class may have no effect.

To tune direction rewards, edit the relevant `weight` in `StraightFullRollRewardsCfg` in `full_roll_env_cfg.py`, then enable it with `--straight-roll`.
Create a new run for each experiment, save the configuration changes, and replay it before keeping the result. Retain the original checkpoint and settings so you can go back.

## 2. Keep the policy interface consistent

### Why 61 observations and 14 actions?

These dimensions come from the existing policy's input and output contract. The 61 observation values appear in this order:

```text
Body angular velocity 3 + projected gravity 3
+ relative joint positions 14 + relative joint velocities 14
+ previous actions 14 + commands 13 = 61
```

The 13 commands contain 3 velocity, 4 head, and 6 body values. All are zero in this task, matching the original rolling policy's inputs.
This policy does not accept a target heading. Direction rewards use a fixed world axis.

The 14 actions are joint-position offsets in the agreed joint order. With `scale=1.0` and `use_default_offset=True`:

```text
Target joint position = default joint position + policy action
```

Here, each action is an offset in radians. Changing observation order, joint order, units, the default pose, or normalization statistics can make the old network produce unsuitable actions.
Check the whole interface, not just the array lengths.

### Action clipping is different from PPO clipping

- `clip_actions=1.0` clamps actions to `[-1, 1]` at the control interface.
- `algorithm.clip_param=0.16` is PPO's probability-ratio clipping parameter. It does not limit motor action amplitude.

In the initial diagnosis, about 15.9% of the original policy's raw actions exceeded `±1`; the largest absolute value was about 3.04.
The full-roll configuration therefore restores the output range needed by that policy. Removing the clamp alone still produced no full turns; rewards and initialization also needed work.
The model's actuator torque, speed, and joint limits remain in place. Check limits and safety constraints again for different hardware or a different action interface.

### What does the warm start copy?

`warm_start_actor_from_onnx()` copies the actor's MLP weights, biases, and observation-normalization statistics. Exploration noise is initialized by the runner configuration.
The critic learns value estimates through PPO. Starting with an existing actor helps exploration begin near a rolling motion, so the time taken here is not a budget for training from random weights.
When changing the source ONNX, check names, layer sizes, normalization data, and SHA-256 first.

## 3. Timing, batch size, and starting height

| Parameter | Value and source | How to interpret or adjust it |
| --- | --- | --- |
| Physics time step | `0.005 s`, inherited from the simulation baseline | 200 physics steps per second; recheck contacts and control behavior after changing it |
| Control decimation | `4`, inherited | One action every 4 physics steps: `0.02 s / 50 Hz` |
| Parallel environments | 64 for the smoke test; 1024 for the experiment | Fit within VRAM first; more environments also mean more data per update |
| Rollout per environment | `32` steps, inherited from the rolling PPO configuration | 1024 × 32 = 32,768 transitions per update; 0.64 simulated seconds per environment |
| Training episode | `12 s`, set for this full-roll task | At most 600 control steps; termination conditions can reset it earlier |
| Evaluation length | `2500` steps, or 50 s | Longer replays reveal whether rolling continues; the PLAY episode limit is 60 s |
| Checkpoint interval | `100` updates, adjusted for this experiment | Get candidates sooner, at the cost of more disk space |

An iteration collects a rollout and performs learning updates. Environment steps, simulated time, and wall-clock time are different quantities.
When resuming, `--max-iterations` specifies additional iterations. Checkpoint numbers are iteration labels; label 600 does not mean the entire experiment used only 600 updates.

### Where does `0.125 m` come from?

The trunk inside the USD has a `0.12 m` offset, while the configured initial root position is `0.005 m`. The position produced when the stage was first composed did not match the position used by the reset API.
We add a `0.12 m` z offset during reset:

```text
Root height after reset = 0.005 m + 0.12 m = 0.125 m
```

This corrects the coordinates for this model. With another model, check the authored transform, root position, foot contact, and `initial_root_height_m` instead of reusing this height blindly.
Training starts with pitch in `±0.05 rad`, joint-position scaling in `0.995–1.005`, and zero initial velocities.

## 4. Define what forward progress means

For each environment, compute pitch phase from the gravity vector `g` expressed in the body frame:

```text
phase = atan2(g.x, -g.z)
delta = wrap the difference between successive phases to [-π, π)
net = net + delta
peak = max(previous peak, net)
new_progress = peak - previous peak
```

Turning backward reduces `net`. Revisiting an angle already reached earns no new progress reward; only passing the previous peak does.
Each time `peak` crosses another `2π`, the counter records a full turn.

For example, repeat “120° forward, 120° backward” ten times. Integrating only positive angular velocity keeps adding progress, but the net angle returns to the start and the full-turn count stays at zero.
See the [diagnostic chart](./roll-debugging#diagnosis).

### Read weights 8 and 6 together with dt

Isaac Lab's reward manager accumulates each term as `weight × term × dt`; see the [RewardManager documentation](https://isaac-sim.github.io/IsaacLab/main/source/api/lab/isaaclab.managers.html#isaaclab.managers.RewardManager).
We handle the progress rate and the discrete completion event separately:

```text
Progress term = min(new_progress / dt, 6 rad/s) / (2π)
Progress reward = 8 × term × dt

Full-turn term = new full turns this step / dt
Full-turn reward = 6 × new full turns this step
```

Without hitting the rate cap, one full turn of new progress earns about 8 accumulated reward units, plus 6 for completing the turn.
The empirical cap of 6 rad/s prevents sudden large angle changes from earning excessive progress reward. It does not cap physical angular velocity.

Weights 8 and 6 provide ongoing guidance and a completion bonus. They are tuning choices for this run, not the result of an exhaustive search.
Too much emphasis on progress can produce rough motion; a sparse completion reward alone can make exploration difficult. After adjusting either, inspect full turns, smoothness, and resets, and keep a checkpoint you can return to.

### What does each penalty control?

These are the direction-training settings. Squared terms grow quickly with error, so weights cannot be compared without considering units and term magnitudes.

| Term | Weight | Penalized quantity | What to watch after changing it |
| --- | --- | --- | --- |
| Backward pitch motion | `-0.05` | Backward pitch angular speed, rad/s | Less rocking back, without preventing the first roll |
| Sideways tilt | `-0.5` | Projected gravity `g_y²`, dimensionless | Less sideways falling while still allowing inversion |
| Rolling-axis alignment | `-3` | `1 - the world-Y component of the body's Y axis` | A more consistent rolling plane |
| Lateral velocity | `-3`; `-0.2` in rounds 1–2 | World-frame `v_y²`, m²/s² | Less lateral drift without losing turns |
| Off-axis rotation | `-0.03`; `-0.01` in rounds 1–2 | Body-frame `ω_x² + ω_z²`, rad²/s² | Less side roll and yaw while preserving forward rolls |
| Action changes | `-0.02` | Sum of squared differences between successive joint actions | Less jitter; too much penalty can discourage starting |
| Soft joint-limit violation | `-0.1` | Joint-position distance outside the soft limits | Fewer violations without suppressing the motion |
| Joint torque | `-1e-5` | Sum of squared torques, N²·m² | Less sustained high-torque contact |

Forward rolling rotates the body around its Y axis. Pure pitch rotation leaves that axis unchanged, so aligning it with world Y constrains the rolling plane while allowing the body to turn upside down.
Requiring the body's Z axis to stay upright would oppose the full roll itself.

The full-roll configuration removes the early target-linear-velocity rewards, the height-band reward that could pay even while stationary, and the automatic speed curriculum.
First make the full motion learnable, then improve direction. This experiment did not also increase torque limits, change gravity, or apply extra assisting forces.

## 5. PPO settings: preserve the useful starting motion

These values come from `MicroDuckContinuousRollPPORunnerCfg` and the `--full-roll-v2` overrides. Network sizes and most hyperparameters were inherited from the rolling baseline.
The [original PPO paper](https://arxiv.org/abs/1707.06347) explains the algorithm. The values below are this project's choices; the paper does not prescribe optimal settings for this robot.

| Parameter | Value used here | Role and tuning guidance |
| --- | --- | --- |
| Actor / critic | `512 / 256 / 128`, ELU | Match the existing actor architecture; keep layer sizes unchanged for the warm start |
| Initial learning rate | `1e-4`; early rolling configuration: `1.5e-4` | Smaller updates; check KL as well if motion degrades quickly |
| Schedule / desired KL | `adaptive / 0.005`; early KL target: `0.008` | Adapt learning rate to policy change; a smaller target is usually more conservative |
| PPO clip | `0.16` | Probability-ratio clipping in the update objective, separate from action clamping |
| Gamma / GAE lambda | `0.995 / 0.95` | Baseline return-discount and advantage-estimation settings; not tuned independently here |
| Entropy coefficient | `0.003` | Retain exploration; too much can disrupt useful motion, too little can stall progress |
| Initial action standard deviation | `0.28` | Explore around the existing actor's output; distinct from the entropy coefficient |
| Epochs / mini-batches | `5 / 8` | Five passes over each rollout; about 4096 samples per mini-batch with 1024 environments |
| Max gradient norm | `0.8` | Limit gradient magnitude; still check observations and rewards for non-finite values |
| Value-loss coefficient | `1.0` | Critic loss weight, inherited from the baseline |
| Training seed | `108` | Fix the training seed for this run; evaluate again after changing it |

The adaptive schedule changes the learning rate. Resuming a `.pt` checkpoint also restores state such as the optimizer, so `1e-4` is a configured initial value; use the logs for the actual learning rate.
Learning rate, KL, and rewards can change together between stages. This is an engineering debugging record, not a single-factor ablation study.

## 6. Why start with limited randomization?

Observation noise, mass randomization, friction randomization, and periodic pushes are disabled here. Only small starting-pose and joint perturbations remain.
That makes it easier to distinguish a hard-to-learn objective from an environment made too difficult by randomization.

Once continuous motion is stable, add one group of randomizations at a time and reuse the same evaluation metrics. Wider friction, pose, mass, and external-force ranges are future experiments, not part of this result.
Changing randomization, learning rate, rewards, and networks together makes a single total-reward curve hard to interpret.

## 7. Know where the evaluation thresholds come from

| Threshold | Purpose | Rationale and trade-off |
| --- | --- | --- |
| `abs(g_y) < 0.55` | Avoid unreliable pitch projection near a sideways pose | An engineering validity range; recheck it for a different motion |
| Phase change per step `< 1.2 rad` | Reject discontinuous phase jumps | A continuity guard chosen for 50 Hz sampling |
| Backward excursion `> π/2` | Break the current consecutive-turn chain | Allow small reversals, but start a new chain after a clear reversal |
| At least 3 consecutive turns and no resets | Basic continuous-motion check | The minimum stage target defined for this experiment |
| Maximum full-turn gap `≤ 3 s` | Reject a few rolls followed by a long stop | An engineering acceptance limit, including the start and end of the replay |

The counter retains the longest chain seen so far. The time-gap check is also needed to detect a long stop afterward.
Unit tests cover rocking, reversals, resets, sideways poses, and independent counting across environments. After changing thresholds, rerun the tests and inspect the pose trace and video.

You now know which settings must match the interface and which can be tuned from observed behavior. The next page puts these decisions together across the three recorded rounds.
