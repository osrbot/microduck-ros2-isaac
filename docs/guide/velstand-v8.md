# Train recovery and turning

This chapter explains how teacher models, starting poses and rewards can improve recovery and turning.
Using the official VelStand model as an example, we look at which parameters changed, why they changed,
and how to check the result.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Skills</span><strong>Recover and turn</strong></div>
  <div role="listitem"><span>Simulator</span><strong>MuJoCo</strong></div>
  <div role="listitem"><span>Model</span><strong>VelStand</strong></div>
  <div role="listitem"><span>Practice</span><strong>Chapter 17</strong></div>
</div>

To start a training run, follow [chapter 17: Continue training a model](./training-checkpoints).
This chapter uses MuJoCo/mjlab; the Isaac Lab instructions remain in [chapter 10](../isaac/training).

## 1. Training results {#results}

VelStand combines walking, standing at zero velocity and fall recovery in one policy.
Further training addresses two weaknesses: getting stuck in some face-up poses, and barely turning despite a yaw command.

| Upstream comparison | Before | After |
| --- | --- | --- |
| Recovery success, face-up with randomized joints | 73% | 94% |
| Recovery success, side-lying with randomized joints | 91% | 96% |
| Recovery success, sitting starts | 89% | 99% |
| In-place yaw at a +0.6 rad/s command | +0.08 rad/s | +0.52 rad/s |
| In-place yaw at a −0.6 rad/s command | −0.03 rad/s | −0.57 rad/s |

Source: the [upstream training record](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/docs/velstand_policy.md).
The simulation evaluation uses flat terrain with backlash. Recovery tests use two groups of 128 environments
per start family, observed for 12 seconds. Yaw values average the upright environments after the first 2 seconds;
they are not overall success rates that also account for falls.
Upstream also records physical-robot tests. The table contains its simulation results, which this project has not retested.

Slow in-place turning around 0.3 rad/s and body-height control still need improvement.
Forward-speed tracking did not improve by the same margin.

## 2. How recovery and turning are trained {#method}

### Recovery: adjust teacher inputs and starting poses

The student continues from an existing walking model, and PPO adjusts its behavior using rewards.
Behavior cloning (BC) also learns from two frozen teachers: preserve walking when upright, learn recovery when fallen.
The basic routing assigns mainly sub-25° tilt states to the walking teacher and over-35° states to the recovery teacher,
leaving the band between them to PPO. Standing body control has additional routing.

The recovery teacher can stop in certain leg configurations, and the student copies that behavior.
The change works by **changing the recovery teacher's input when the body tilt is large**:

| Change | Upstream setting | Reason |
| --- | --- | --- |
| Teacher-input masking gate | Tilt above 75° | Avoid the stuck joint configurations when fully down; restore full input during the later rise |
| Masked input | Zero observation columns `[6:48]` | Joint-relative positions, velocities and previous actions; gravity direction remains available |
| Random joint starts | 50% within the prone-start branch | Cover more than the standard HOME leg pose |
| Random spatial orientation | 25% within the prone-start branch | Cover more landing orientations; these starts also randomize joints |
| Sitting starts | A separate 5% of all resets | Include the transition from sitting to standing |

These probabilities have different denominators; do not add them together.
Zero relative joint position means the HOME reference pose in the teacher's input, not a physical reset of the joints.
Neither the student input nor the simulated state is masked or reset.
The 35° teaching gate and the 75° teacher-masking gate serve different purposes.
See [teacher inputs and BC](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/tasks/distill.py)
and the [VelStand configuration](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/tasks/microduck_velstand_env_cfg.py).

### Turning: calibrate teacher actions and adjust rewards

The walking teacher has its own yaw dead zone, which direct imitation passes on to the student.
During training, the controller looks up the command that makes that teacher produce approximately the desired turn,
then uses the resulting action as the teaching target. **The student always receives the true target command.**
The adjustment applies to the teacher's action generation during training.

| Change | Upstream setting | Rationale |
| --- | --- | --- |
| Teacher yaw mapping | Interpolate by planar speed, target yaw rate and turn direction | Left/right responses differ; one constant multiplier is insufficient |
| Fine yaw reward | `track_yaw_fine`: std 0.35, weight 2 | More sensitive to small errors than the previous width of about 0.71; std is the reward-kernel width, not sensor noise |
| In-place turns | 20% of twist-command resamples | Ensure the policy actually practices turning in place |
| Minimum turn magnitude | 0.2 rad/s | Include slower turns without claiming that the whole low-speed range now works |

The table lives in `ANCHOR_YAW_REMAP`. A different teacher needs its own calibration.
This example uses `ENABLE_ANCHOR_YAW_REMAP=True`.
`ENABLE_YAW_FIX` belongs to an unsuccessful experiment and stays `False`.
Disable the old runtime yaw compensation when using the updated model to avoid applying a second correction.
The pinned configuration above contains these parameters and switches.

## 3. Download and try the model {#try-v8}

::: details Source revisions and model checksums
Use fixed revisions rather than a moving `main` or tag:

| Purpose | Pinned version |
| --- | --- |
| Source used by this chapter | `b02fdea4902c2b93b7d34a83a6f05da4ececb7d3` |
| Policy set used by this chapter | `665ae4eb20bfe13bca1ef4ea6d4bb6b4a096e448` |
| `velstand.onnx` SHA-256 | `2fc7f8ee6acd7d0d3f66a99927b5d5a56589aeed02ec714de329b252d5ccf492` |

The manifest still declares 61 observations, 14 actions and 50 Hz control.
Only `velstand.onnx` differs from the tutorial’s default weights; the other nine ONNX hashes match.
The robot XML/STL files are also unchanged in this RL diff.
Sources: the [pinned policy manifest](https://huggingface.co/pollen-robotics/microduck-policies/blob/665ae4eb20bfe13bca1ef4ea6d4bb6b4a096e448/manifest.json)
and [source comparison](https://github.com/pollen-robotics/microduck_rl/compare/ceca01706143d729305baa94cbd8ab990979e325...b02fdea4902c2b93b7d34a83a6f05da4ececb7d3).
:::

<div class="md-step-kicker"><span>OPTION A</span><strong>Terminal A · this project's repository root</strong></div>

Follow the [existing setup](./installation) for the default inputs, then prepare the local MuJoCo environment:

```bash
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
```

Download the recovery and turning model into its own directory using this project's existing checked downloader.
A mismatched existing file causes an error instead of being overwritten; an identical file is only verified.

```bash
work/mujoco_env/bin/python - <<'PY'
from pathlib import Path
import sys
sys.path.insert(0, str(Path("scripts").resolve()))
from fetch_policies import fetch_file, file_sha256

revision = "665ae4eb20bfe13bca1ef4ea6d4bb6b4a096e448"
expected = "2fc7f8ee6acd7d0d3f66a99927b5d5a56589aeed02ec714de329b252d5ccf492"
target = Path("reference/policies/v8/velstand.onnx")
fetch_file(
    f"https://huggingface.co/pollen-robotics/microduck-policies/resolve/{revision}/velstand.onnx",
    target, expected,
)
print(target, file_sha256(target))
PY
```

Probe the default and updated models with identical settings. A new timestamped report directory keeps earlier evidence intact:

```bash
probe_dir="$PWD/artifacts/velstand-v8/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$probe_dir"
for policy_version in v7 v8; do
  work/mujoco_env/bin/python scripts/run_mujoco_baseline.py \
    --policy "reference/policies/$policy_version/velstand.onnx" \
    --duration 10 --vx 0.3 --action-scale 0.9 \
    --output "$probe_dir/$policy_version.json"
done
```

This is a short compatibility check in the existing simplified ground-contact model:
inspect loading, finite values and posture. Full recovery and turning tests require the training environment described below. These commands have been checked against source and still need GPU testing.

## 4. Two-stage training settings {#training}

Training has two stages: improve recovery, then refine turning. To continue training yourself, follow [chapter 17](./training-checkpoints) to download the public model and both teachers.

The original experiment commands below are retained for studying the parameter choices and training process.

:::: details Original two-stage experiment: settings and commands
### Prepare the training models

Full training needs a Linux/CUDA GPU, Python 3.12, `uv` and the upstream locked dependencies.
The task is `Mjlab-VelStand-Rough-Backlash-MicroDuck`: full collisions, rough terrain,
BAM XL330 actuators and backlash.

BC loads two teachers in addition to the resume checkpoint. Confirm access to these original `.pt` files first:

| Input | Upstream W&B run | File |
| --- | --- | --- |
| Initial walking model | `pollen-robotics/mjlab_microduck/j4i6yoq2` | `model_1250.pt` |
| Recovery teacher | `pollen-robotics/mjlab_microduck/69u48n8l` | `model_9750.pt` |
| Walking teacher | `pollen-robotics/mjlab_microduck/441tzs6d` | `model_3750.pt` |
| Selected upstream stage A result | `pollen-robotics/mjlab_microduck/qz5g3bwi` | `model_1750.pt` |

::: tip You can now continue from the final model
The final VelStand model and both teachers are public. Follow [chapter 17](./training-checkpoints) to use them.
This section keeps the original two-stage experiment's settings and commands;
`j4i6yoq2_1250` and `qz5g3bwi_1750` still require access to the original files.
The two chapters use different source revisions, so use the complete commands from the chapter you are following.
:::

This historical experiment requires the original `.pt` files listed above; public access to some of them has not been confirmed.
ONNX files are for inference. Continued training requires `.pt` models containing training state.
Load `.pt` files only from trusted sources, and record their provenance and SHA-256 hashes.

### Prepare a separate experiment checkout

<div class="md-step-kicker"><span>OPTION B</span><strong>Linux host with CUDA · this project's repository root</strong></div>

Do not switch the default `reference/microduck_rl/` checkout.
The following creates a separate source directory for this experiment.
If it already exists, inspect its version and local changes instead of cloning again or forcing a checkout.

```bash
git clone --filter=blob:none --no-checkout \
  https://github.com/pollen-robotics/microduck_rl.git reference/microduck_rl-v8
cd reference/microduck_rl-v8
git checkout --detach b02fdea4902c2b93b7d34a83a6f05da4ececb7d3
mkdir -p ../../work/velstand-v8/logs
ln -s ../../work/velstand-v8/logs logs
uv sync --frozen
```

The `logs` symlink places training records under this project's `work/velstand-v8/logs/`.
Read the upstream CLI help and sign in to your own W&B account.
Initial downloads may require that account to have access to the source runs.
Do not write your experiment records into the official project.

```bash
uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck --help
uv run wandb login
```

### Stage A: train recovery

Upstream used `333ef7b` for this stage: joint masking and broader starting states, without stage B's yaw remap.
Use the matching revision to examine the effect of these recovery settings separately.

```bash
git checkout --detach 333ef7b03c0463bdebfcd6e2be0592de76c2bbcc
uv sync --frozen
env -u MICRODUCK_WARM_START uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --env.scene.num-envs 4096 --agent.resume True \
  --wandb-run-path pollen-robotics/mjlab_microduck/j4i6yoq2 \
  --wandb-checkpoint-name model_1250.pt \
  --agent.max_iterations 1500
```

This is the upstream reference budget, not a minimum GPU requirement or a completion-time promise.
First reduce the environment count and iteration budget to check checkpoint loading, BC teachers and saving.
A small pipeline check does not reproduce the reported performance.
That upstream run reached 2749, but **1750** was selected. Newest is not necessarily best.

### Stage B: train turning

Wait for the previous training process to exit before switching source.
This stage uses `3750776`, adding the teacher yaw remap and fine yaw reward:

The example below reads upstream's stage A checkpoint. **To continue your own stage A,
replace the run and checkpoint first.** It does not automatically resume your previous experiment.

```bash
git checkout --detach 3750776761ecfaa5671b36972087cafba45b8527
uv sync --frozen
env -u MICRODUCK_WARM_START uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --env.scene.num-envs 4096 --agent.resume True \
  --wandb-run-path pollen-robotics/mjlab_microduck/qz5g3bwi \
  --wandb-checkpoint-name model_1750.pt \
  --agent.max_iterations 1000
```

These commands use the upstream experiment files. To continue your own stage A model,
replace the second command's run and checkpoint with your selected file, and give the new model its own name.

Both stages use ordinary resume, preserving step counts and curriculum progress for fine-tuning.
The commands explicitly remove `MICRODUCK_WARM_START` to avoid inheriting an old `=1` setting that resets the curricula.
That environment variable is not the same as the retained `WARM_START=True` configuration constant.
See the [upstream load patch](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/tasks/mdp.py).

::::

## 5. Check behavior and export the model {#evaluation}

Track recovery, turning and walking separately. Select on development cases, then evaluate in independent processes
with new seeds. Use the table below to plan the tests; automated statistics require a separate evaluation script.

| Check | Keep identical | Save |
| --- | --- | --- |
| Recovery | Start families, joint randomization, model and duration for both candidates | Successes/total, stuck rate, recovery time, re-falls |
| Turning | Both signs; separate in-place and moving turns | Actual yaw rate, error and falls, not only surviving samples |
| Straight walking | Commands, friction and actuator settings | Actual speed, lateral/yaw drift and falls |
| Smoothness | Sampling rate and measurement interval | Body angular velocity, impacts and continuous real-time recovery video |

Fix recovery height/tilt thresholds, the required stable-standing duration, timeouts and denominators before comparing.
Use the same criteria for both versions. The same principle applies to [continuous-roll acceptance](../isaac/roll-validation).

::: info The automatic evaluation scripts are not public
The upstream record refers to `claude_experiments/velstand_rise_battery.py`, `velstand_yaw_probe.py`
and related scripts that are absent from the selected source. Reproducing the official statistics requires these scripts
or an implementation with the same, documented evaluation conditions.
:::

Export your selected checkpoint with the [upstream exporter](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/export.py)
so observation normalization is included in ONNX. Replace the absolute checkpoint placeholder with your actual file.
Still run from `reference/microduck_rl-v8/`:

```bash
export_dir="$PWD/../../artifacts/velstand-v8/export-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$export_dir"
uv run scripts/export.py Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --checkpoint-file /absolute/path/to/model_selected.pt \
  --onnx-file "$export_dir/velstand.onnx"
sha256sum "$export_dir/velstand.onnx"
```

Keep the source SHA, `uv.lock`, input/teacher/output checkpoint hashes, environment and reward configurations,
seeds, raw logs, independent evaluations and real-time footage for each run so other readers can reproduce the experiment and parameter changes.
Use `work/velstand-v8/` for working records and `artifacts/velstand-v8/` for evidence and export candidates;
place a completed tutorial companion package in `output/` without overwriting historical cases.

## 6. Checks before using the model in Isaac {#adoption}

First complete the matched MuJoCo comparison. Then separately check the Isaac observation order, action scales,
actuator differences, walking/recovery behavior and transitions to other skills.
Equal interface dimensions do not establish equal behavior across engines.

Test the recovery and turning model in MuJoCo first. The Isaac playground keeps its paired models and controller settings; see [Model and source versions](../reference/upstream-alignment).

<div class="md-page-complete">
  <strong>Next: load a model and start training</strong>
  <p>Chapter 17 walks through environment setup, model download, training, result checks and export in one small continuation run.</p>
</div>
