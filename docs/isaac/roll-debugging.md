---
title: Continuous rolling — three rounds of debugging
description: Follow the changes from incomplete turns to continuous rolling, then improve direction with targeted rewards.
prev:
  text: Parameters and rewards
  link: /isaac/roll-parameters
next:
  text: Evaluation and video export
  link: /isaac/roll-validation
---

<script setup>
import { withBase } from 'vitepress'
import RollPhaseChart from '../.vitepress/theme/RollPhaseChart.vue'
</script>

# From incomplete turns to continuous rolls

Start with the changes across the three rounds, then look at how each decision was made.
The rhythm was simple: **short training segment → saved checkpoint → independent replay → next decision**. Once continuous rolling worked, we focused on direction.

## What changed across the three rounds?

| Stage | Main change | Independent replay | Next decision |
| --- | --- | --- | --- |
| Initial diagnosis | Check the original ONNX action range and full-turn count | 0 full turns, both with and without action clipping | Redefine progress and keep checking initialization |
| Round 1 | Reward new net-angle progress and full turns; correct height and widen the arena during replay | 1 environment / 30 s: 17 consecutive turns, 0 resets, about 7.20 m lateral displacement | Put the height correction into training; revisit direction later |
| Round 2 | Resume training with the corrected starting height | 8 environments / 50 s each: 36–37 consecutive turns, 0 resets, mean lateral displacement about −12.36 m | Continuity meets the target; start constraining direction |
| Round 3 | Align the rolling axis and strengthen lateral-velocity and off-axis penalties | 8 environments / 50 s each: all 39 consecutive turns, 0 resets, mean absolute lateral displacement about 0.70 m | Select a checkpoint, record it, and package the results |

Round 1 used a different replay duration and starting state from the later rounds. This table explains the debugging route; compare models again under matching conditions when ranking them.
The negative value in round 2 indicates lateral direction. Round 3 reports a mean of absolute values so opposite drifts cannot cancel out.

## Initial diagnosis: angular velocity, but no full turns {#diagnosis}

The early configuration encouraged motion with positive pitch angular velocity, angular-velocity tracking, target forward speed, and a height-band reward.
The duck could earn reward by rocking over a small angle or staying in a convenient pose. More iterations could simply reinforce that behavior.

We first replayed the public `roulade.onnx` to inspect the action interface and body orientation:

- With the `±1` action clamp: 0 full turns in 15 seconds; about 15.9% of raw actions were clipped.
- Without the clamp: still 0 full turns in 30 seconds.
- In both replays, the maximum net phase change was about 2.35 rad, or 135°—short of a full 360°.

Both diagnostic runs used the original ONNX. The earlier long-training model was kept separately and was not part of this comparison.

<RollPhaseChart />

**What to record:** raw action magnitude, net rotation phase, full-turn count, and video together.
The action range revealed an interface issue. The unclipped replay showed that the task definition still needed work.
Integrating only positive angular velocity would keep counting repeated forward rocking as progress.

### Run the same kind of diagnostic yourself

Complete the [environment preflight](./continuous-roll#setup) first, and reuse `roll_evidence` and `roll_deadline` in the same terminal.
The command below uses the current replay configuration with its corrected height. Use it to check a new setup; the historical diagnostic above used the earlier configuration.

```bash
MICRODUCK_PLAY_STEPS=1500 MICRODUCK_PLAY_TIMEOUT=240 \
MICRODUCK_PLAY_OUTPUT="$roll_evidence/onnx-check.json" \
MICRODUCK_PLAY_SCREENSHOT="$roll_evidence/onnx-check.png" \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 260 \
  --status "$roll_evidence/onnx-check-status.json" -- \
  bash scripts/play_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --viz none \
    --policy-onnx reference/microduck/policies/roulade.onnx \
    --arena-half-width 25 --trace "$roll_evidence/onnx-check-trace.json"
```

Read `maximum_raw_action`, `raw_action_fraction_above_one`, and `completed_forward_turns` in the report.
`--full-roll-v2` already disables action clipping, so you do not need an additional `--unclipped-actions` flag.
For a new clipping comparison, change only the clamp and keep height, arena, duration, and seed fixed. Removing the whole profile would change more than one variable.

## Round 1: get through the full 360°

### What we changed

We warm-started from the original actor and normalization statistics, kept the model's actuator settings, and used:

- A reward for newly reached net rotation, with weight 8.
- A full-turn completion reward, with weight 6.
- No legacy action clamp, target-linear-velocity reward, or height-band reward.
- No mass or friction randomization, pushes, or observation noise; a 12-second episode.
- An initial learning rate of `1e-4`, target KL of `0.005`, and 1024 environments.

These were combined changes in one round. A single result cannot tell us the isolated contribution of each setting.

### Replay exposed a second problem

The first replay of checkpoint 100 completed 17 turns in 30 seconds, but its longest consecutive chain was only 6 turns, with 2 out-of-bounds resets.
Reset telemetry showed that the nested USD's root offset had not been applied consistently to the reset position.

In an independent replay, we corrected the root height to `0.125 m` and widened the lateral arena half-width from 1 m to 10 m.
That produced 17 consecutive turns, no resets, and a maximum full-turn gap of 1.80 seconds.
Both settings changed, so both the height correction and the wider boundary affected the no-reset result.

<figure class="md-doc-figure">
  <video controls playsinline preload="none" width="1280" height="720" style="display:block;width:100%;height:auto;aspect-ratio:16/9;background:#252832" aria-label="First 10 seconds of round 1 checkpoint 100 replayed with the corrected height">
    <source :src="withBase('/media/continuous-roll/first-rolls.mp4')" type="video/mp4" />
  </video>
  <figcaption>Round 1, checkpoint 100, replayed with the corrected height: the first 10 seconds. The full 30-second run completed 17 turns, with about 7.20 m of lateral displacement.</figcaption>
</figure>

**The takeaway:** full turns were now possible, starting height needed to be consistent, and direction still needed work.
Round 1 was budgeted for up to 1200 updates or 900 seconds. We stopped early after gathering the diagnostic results. The last logged iteration label was 245; saved checkpoint 200 was kept for the next round.

## Round 2: train from the corrected starting height

We added the `0.12 m` z offset to training resets and resumed from round 1 checkpoint 200.
The full-turn rewards stayed the same. The next question was whether the duck could keep rolling from several slightly different starting poses.

This round's checkpoint 300 was replayed in eight environments for 50 seconds each. Full-turn counts were:

```text
37, 36, 37, 36, 36, 36, 36, 37
```

Every environment had zero resets, and its longest consecutive chain equaled its total turn count. All started at a root height of `0.125 m`, with roll / pitch / yaw each perturbed by `±0.03 rad`, joint-position scaling perturbed by `±0.003`, and seed 109.
These were eight starting-state samples generated using one seed.

Continuity met the stage target, but mean forward displacement was about 12.12 m and mean lateral displacement was about −12.36 m.
Turn counts alone would miss that drift, so round 3 focused on direction.

Round 2 allowed 800 additional updates and at most 750 seconds. It stopped early after iteration label 547, with checkpoint 500 saved.
For the next round, we chose **checkpoint 300, which had already passed batch replay**, and retained it as the fallback model.

## Round 3: improve the rolling direction {#direction-training}

### Decide what to constrain

Penalizing all angular velocity would suppress rolling. Requiring an upright body would also conflict with the goal.
We kept pitch rotation free and constrained the rolling plane and sideways motion:

```text
New rolling-axis alignment weight:       -3
Squared lateral-velocity weight:  -0.2 → -3
Squared off-axis velocity weight: -0.01 → -0.03
Net-progress / full-turn weights:    8 / 6 (unchanged)
```

Starting from round 2 checkpoint 300, this round completed 600 additional updates, with iteration labels 300–899.
We then selected round 3 checkpoint 600, which had an independent batch evaluation, and named the delivered copy `model_best.pt`.
Here, “best” identifies the candidate selected under this experiment's criteria; it does not imply every saved checkpoint was evaluated.

### Resume your own run

Reuse the experiment directory and absolute deadline from the main walkthrough. Replace the checkpoint path with a candidate **you have already checked in replay**:

```bash
roll_checkpoint="$roll_session/roll/RUN_TIMESTAMP/model_200.pt"
test -s "$roll_checkpoint" && \
MICRODUCK_TRAIN_ENVS=1024 MICRODUCK_TRAIN_ITERATIONS=600 \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 600 \
  --status "$roll_evidence/direction-status.json" -- \
  bash scripts/train_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --straight-roll --viz none \
    --resume-checkpoint "$roll_checkpoint" \
    --log-root "$roll_session/direction"
```

Look for `loading_resume_checkpoint`, `MICRODUCK_ROLL_RESUME_SHA256=...`, and a new run directory.
`--straight-roll` enables the direction rewards. Replay still uses `--full-roll-v2`, because inference needs matching observations, actions, and resets, not the training reward terms.
Choose checkpoints by replayed behavior. The replay report's total reward is not a direct recalculation of the direction-training objective.

## If you get a different result, check in this order

| Symptom | Check first | Then try |
| --- | --- | --- |
| Starts inside the floor, flies away, or breaks apart | Root height, collisions, coordinates, and asset version | Correct initialization and replay briefly before changing PPO |
| Rocks forward and backward without a full turn | Net phase, progress reward, and action range | Check whether the same partial motion earns reward repeatedly |
| Rolls a few times, then resets | `done_count`, termination position, and episode duration | Separate boundary exits, timeouts, and motion failures |
| Keeps moving diagonally in a wider arena | Lateral displacement and rolling-axis direction | Compare direction rewards under matching replay conditions |
| More turns, but jittery joints | Action changes, torque terms, KL, and learning rate | Adjust one group of constraints at a time and retain the old model |
| Smooth and stable, but reluctant to start rolling | Actual magnitudes of task rewards and penalties | Check whether smoothness or posture penalties dominate the task reward |
| Fails with a different seed or starting pose | Training and evaluation starting-state distributions | Widen randomization gradually, then evaluate again |

## Keep a five-line tuning record

```text
Observation: What looks wrong under the same replay conditions?
Hypothesis: Which setting or interface might explain it?
Change: Which parameter group changed, and from what values to what values?
Comparison: With the same duration, seed, arena, and perturbations, what changed?
Decision: Keep it, roll back, or investigate another cause?
```

Move on to evaluation when the stage target is met. If the budget runs out, save useful results and failed attempts without automatically extending the deadline.
The next page covers batch replay, reading the metrics, and recording the selected checkpoint.
