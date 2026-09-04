---
title: Continuous rolling — evaluation and video export
description: Choose a checkpoint, check full turns and continuity, measure lateral drift, and record a 1080p demonstration.
prev:
  text: Three rounds of debugging
  link: /isaac/roll-debugging
next:
  text: Make a new training task
  link: /isaac/custom-environment
---

# Choose a model, evaluate it, then record it

This last step connects a saved training checkpoint to its behavior in replay.
Check continuous motion, resets, and turn gaps first, then compare lateral drift. Use the same checkpoint for the batch evaluation and the video.

## The final recorded result

| Check | Batch replay | Separate video run |
| --- | --- | --- |
| Count and duration | 8 environments, 50 seconds each | 1 environment, 50 seconds |
| Full / consecutive forward turns | 39 / 39 in every environment | 39 / 39 |
| Resets | 0 | 0 |
| Maximum full-turn gap | At most 1.40 seconds | 1.42 seconds |
| Lateral displacement | Mean absolute: 0.699 m; maximum absolute: 1.426 m | 1.152 m |
| Starting state | Seed 109, each orientation angle ±0.03 rad, joint scaling ±0.003 | Default deterministic standing pose |

Initial root height was `0.125 m`. The batch used eight starting states generated with one seed. It did not cover multiple independent seeds, complex terrain, external pushes, or a physical robot.
The recorded replay length is 50 seconds. To test longer-term stability, increase both the PLAY episode limit and the test duration, then evaluate again.

## 1. Identify the checkpoint you selected

The delivered model is round 3's `model_600.pt`, copied as `model_best.pt`.
That round also saved `model_final.pt` at the end; `training-final-summary.json` describes the end of the training round.
The batch and recording reports for checkpoint 600 correspond to the model shown on these pages.

Run all commands from the repository root. Keep the environment, `PYTHONPATH`, `roll_evidence`, and `roll_deadline` from the [main walkthrough](./continuous-roll).
Choose a candidate from your own training directory after a short replay, for example:

```bash
roll_checkpoint="$roll_session/direction/RUN_TIMESTAMP/model_600.pt"
test -s "$roll_checkpoint" && sha256sum "$roll_checkpoint"
```

Replace `RUN_TIMESTAMP` with your actual run directory. Checkpoint labels depend on the resume point and save schedule. Every command below passes `--checkpoint` explicitly to avoid selecting another run.
Only load `.pt` checkpoints from a trusted source.

::: info If you have the experiment package
The local delivery package is at `output/continuous-roll-training/roll120-20260904-073725/`.
If you have that package, point `roll_checkpoint` at its `model_best.pt`.
The video is available on this website; the model weights are not distributed with the tutorial. Without the package, use your own trained checkpoint for the steps below.
:::

## 2. Evaluate eight slightly different starting states

```bash
test -s "$roll_checkpoint" && \
MICRODUCK_PLAY_ENVS=8 MICRODUCK_PLAY_STEPS=2500 \
MICRODUCK_PLAY_TIMEOUT=240 \
MICRODUCK_PLAY_OUTPUT="$roll_evidence/batch-validation.json" \
MICRODUCK_PLAY_SCREENSHOT="$roll_evidence/batch-preview.png" \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 260 \
  --status "$roll_evidence/batch-status.json" -- \
  bash scripts/play_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --viz none \
    --checkpoint "$roll_checkpoint" --arena-half-width 25 \
    --reset-perturbation 0.03 --seed 109 \
    --trace "$roll_evidence/batch-trace.json"
```

`--reset-perturbation 0.03` gives roll / pitch / yaw a range of `±0.03 rad` each and scales joint positions by `1 ± 0.003`.
`2500 × 0.02 s = 50 s`. Wall-clock execution can be faster or slower than that; check the report's actual step count to confirm the replay completed.

Replay uses a lateral arena half-width of 25 m to leave room for sustained motion; the training baseline uses 1 m.
Widening the arena affects out-of-bounds resets, so report turns, resets, and lateral displacement together.
Measure drift separately: staying inside a wide boundary does not by itself show precise direction control.

## 3. Which report fields matter most?

| Field | How to read it |
| --- | --- |
| `completed_forward_turns` | Total full forward turns completed by each environment |
| `max_consecutive_forward_turns` | Longest consecutive chain seen in each environment; resets and clear reversals break the current chain |
| `done_count` | Total terminations / resets across all environments; the target here is 0 |
| `turn_completion_times_s` | Simulated times at which each environment completed its turns |
| `maximum_full_turn_gap_s_per_env` | Longest gap, including the wait before the first turn and after the last turn |
| `sustained_roll_passed` | Every environment has at least 3 consecutive turns, there are no resets, and the maximum gap is at most 3 seconds |
| `mean_abs_lateral_displacement_m` | Mean absolute final lateral displacement across environments, so opposite drifts do not cancel |
| `max_abs_lateral_displacement_m` | Largest absolute final lateral displacement among the samples |

`roll_acceptance_passed` checks consecutive-turn counts and zero resets. `sustained_roll_passed` also checks the time gaps.
The legacy field `mean_forward_rolls` is based on integrated positive angular velocity. Use `completed_forward_turns` for full-turn counts.
Orientation-based counting checks forward rotation; inspect the video as well for ground contact, sliding, and the appearance of the motion.

Extract the main fields with:

```bash
python3 - "$roll_evidence/batch-validation.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    report = json.load(stream)
for key in (
    "checkpoint", "num_envs", "steps", "seed",
    "completed_forward_turns", "max_consecutive_forward_turns",
    "done_count", "maximum_full_turn_gap_s_per_env",
    "sustained_roll_passed", "mean_abs_lateral_displacement_m",
    "max_abs_lateral_displacement_m",
):
    print(f"{key}: {report[key]}")
PY
```

Once continuity passes, smaller direction errors are preferable, but consider forward motion and movement quality too.
If your task requires a fixed heading or a target position, define error thresholds for those goals. This example does not train commanded headings or precision position control.

## 4. Compare candidates, not just checkpoint numbers

Replay candidates such as checkpoints 100, 200, and 300 with the same seed, 50-second duration, arena, and perturbations. Give each candidate a separate output directory.
Use this order:

1. Reject non-finite values and abnormal starts.
2. Check full turns, consecutive chains, and time gaps against the target.
3. With comparable continuity, compare lateral drift, joint jitter, and movement quality.
4. Try other starting states to check that an improvement is not limited to one sample.

Multiple seeds, longer replays, and friction or mass changes are follow-up experiments. Save the current settings and results before adding difficulty.
Training and replay can use different reward configurations. Total rewards from different rounds are not a substitute for these matched replay comparisons.

## 5. Record the selected model in 1080p

Make sure `ffmpeg` is available on the Linux `PATH` with the `h264_nvenc` encoder; this script uses NVIDIA hardware encoding. This command uses a 1920 × 1080 camera, captures every 2 control steps, and encodes at 25 fps: 1250 frames over 50 seconds.

```bash
command -v ffmpeg
ffmpeg -hide_banner -encoders | grep h264_nvenc
test -s "$roll_checkpoint" && \
MICRODUCK_PLAY_ENVS=1 MICRODUCK_PLAY_STEPS=2500 \
MICRODUCK_PLAY_TIMEOUT=300 \
MICRODUCK_PLAY_OUTPUT="$roll_evidence/video-validation.json" \
MICRODUCK_PLAY_SCREENSHOT="$roll_evidence/preview.png" \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 320 \
  --status "$roll_evidence/video-status.json" -- \
  bash scripts/play_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --viz none \
    --checkpoint "$roll_checkpoint" --arena-half-width 25 \
    --video "$roll_evidence/continuous-forward-roll.mp4" \
    --video-width 1920 --video-height 1080 \
    --video-fps 25 --video-every 2
```

The simulation camera determines the video resolution, independently of the desktop monitor. For a follow-camera motion clip, the terminal and desktop folders do not need to appear in the frame.
This example exports footage without narration. You can show it during a livestream or edit it into a tutorial later.

Check the encoding details and decode the entire file:

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration \
  -of json "$roll_evidence/continuous-forward-roll.mp4"
ffmpeg -v error -i "$roll_evidence/continuous-forward-roll.mp4" -f null -
```

Expect 1920 × 1080, 25 fps, and about 50 seconds. The final command should complete successfully without error output.
Still open the video and inspect the start, middle, and end. Check this recording's own `video-validation.json` rather than reusing the batch results.

## 6. Keep the model, settings, and footage together

A short model filename is fine as long as its source is clear. A useful experiment package looks like this:

```text
output/continuous-roll-training/YOUR_EXPERIMENT_ID/
├── README.md                  # Selected checkpoint, replay steps, and results
├── model_best.pt
├── params/
│   ├── env.yaml
│   └── agent.yaml
├── batch-validation.json
├── video-validation.json
├── continuous-forward-roll.mp4
├── preview.png
└── SHA256SUMS
```

Take the parameter snapshots from the selected checkpoint's run. Both replay reports should identify the same model. In the README, record the source directory, training configuration, test conditions, turn counts, gaps, and displacement.
Keep raw step traces, logs, and failed candidates in `artifacts/`, and process notes in `work/`.
In the new package directory, create a checksum manifest for the explicitly selected delivery files, then verify it with `sha256sum -c SHA256SUMS`.

Training and replay have separate timeout protection. When the experiment ends, confirm that their processes have exited and GPU usage has dropped. Do not restart an experiment after its deadline.
This tutorial was assembled from the existing experiment records; preparing it did not start another long training run.

You have now worked through a complete training case: define the motion, build the task, tune short runs, compare models under consistent conditions, and export the result.
The next page applies the same process to new tasks such as kicking or standing up.
