# VelStand v8: get up and turn on command

No new circus trick this time. Two basics come first: get up after a fall, and actually turn when asked.
Upstream released VelStand v8 on 2026-10-12. Start with the results, unpack the training changes,
then plan a controlled comparison of your own.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Reading path</span><strong>Results → causes → training → checks</strong></div>
  <div role="listitem"><span>Training stack</span><strong>MuJoCo / mjlab + CUDA</strong></div>
  <div role="listitem"><span>Project defaults</span><strong>Kept unchanged</strong></div>
  <div role="listitem"><span>Evidence</span><strong>Upstream report; local retest pending</strong></div>
</div>

::: info Optional reading, not a new default setup
The existing `upstream.lock`, v7 downloader, Isaac playground, historical USD and continuous-roll case study stay unchanged.
This page covers upstream MuJoCo/mjlab VelStand. It does not turn the [native Isaac Lab walking task](../isaac/training)
into v8. Follow the original steps if you simply want to run the existing tutorial.
:::

## 1. Results first: what improved? {#results}

VelStand combines walking, standing at zero velocity and fall recovery in one policy.
v8 addresses two v7 weaknesses: getting stuck in some face-up poses, and barely turning despite a yaw command.

| Upstream comparison | v7 | v8 |
| --- | --- | --- |
| Recovery success, face-up with randomized joints | 73% | 94% |
| Recovery success, side-lying with randomized joints | 91% | 96% |
| Recovery success, sitting starts | 89% | 99% |
| In-place yaw at a +0.6 rad/s command | +0.08 rad/s | +0.52 rad/s |
| In-place yaw at a −0.6 rad/s command | −0.03 rad/s | −0.57 rad/s |

Source: the [upstream v8 training record](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/docs/velstand_policy.md).
The simulation evaluation uses flat terrain with backlash. Recovery tests use two groups of 128 environments
per start family, observed for 12 seconds. Yaw values average the upright environments after the first 2 seconds;
they are not overall success rates that also account for falls.
Upstream separately records physical-robot tests of getting up, turning and walking. **These are not this project's retest results.**

Limits remain: slow in-place turning around 0.3 rad/s is weak, body-height control is still not learned,
and forward-speed tracking did not improve by the same margin. Better recovery and turning do not mean every skill improved.

## 2. Why more training is not always the answer {#method}

### Recovery: check what the teacher is teaching

This recipe does not start with random behavior. The student inherits walking, then PPO improves it using rewards.
Behavior cloning (BC) also learns from two frozen teachers: preserve walking when upright, learn recovery when fallen.
The basic routing assigns mainly sub-25° tilt states to the walking teacher and over-35° states to the recovery teacher,
leaving the band between them to PPO. Standing body control has additional routing.

The recovery teacher itself can freeze in certain leg configurations, so the student copies that behavior.
v8 does not hide joint information from the student. It **changes only the recovery teacher's input at large tilt**:

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

### Turning: calibrate the teacher and align the reward

The walking teacher has its own yaw dead zone, which direct imitation passes on to the student.
During training, v8 looks up the command that makes that teacher produce approximately the desired turn,
then uses the resulting action as the teaching target. **The student still receives the true command.**
This is not a hidden input boost at deployment.

| Change | Upstream setting | Rationale |
| --- | --- | --- |
| Teacher yaw mapping | Interpolate by planar speed, target yaw rate and turn direction | Left/right responses differ; one constant multiplier is insufficient |
| Fine yaw reward | `track_yaw_fine`: std 0.35, weight 2 | More sensitive to small errors than the previous width of about 0.71; std is the reward-kernel width, not sensor noise |
| In-place turns | 20% of twist-command resamples | Ensure the policy actually practices turning in place |
| Minimum turn magnitude | 0.2 rad/s | Include slower turns without claiming that the whole low-speed range now works |

The table lives in `ANCHOR_YAW_REMAP`. A different teacher needs its own calibration.
`ENABLE_YAW_FIX` is a retained failed-experiment switch and stays `False`;
the effective route uses `ENABLE_ANCHOR_YAW_REMAP=True`. Do not enable both just because one is named “fix.”
Do not apply the old v7 runtime yaw-compensation formula on top of v8 either.
The pinned configuration above contains these parameters and switches.

## 3. Try the weights without changing defaults {#try-v8}

Use fixed revisions rather than a moving `main` or tag:

| Purpose | Pinned version |
| --- | --- |
| Merged v8 source reference | `b02fdea4902c2b93b7d34a83a6f05da4ececb7d3` |
| Official v8 policy set | `665ae4eb20bfe13bca1ef4ea6d4bb6b4a096e448` |
| `velstand.onnx` SHA-256 | `2fc7f8ee6acd7d0d3f66a99927b5d5a56589aeed02ec714de329b252d5ccf492` |

The manifest still declares 61 observations, 14 actions and 50 Hz control.
Only `velstand.onnx` differs from our pinned v7 weights; the other nine ONNX hashes match.
The robot XML/STL files are also unchanged in this RL diff.
Sources: the [pinned policy manifest](https://huggingface.co/pollen-robotics/microduck-policies/blob/665ae4eb20bfe13bca1ef4ea6d4bb6b4a096e448/manifest.json)
and [source comparison](https://github.com/pollen-robotics/microduck_rl/compare/ceca01706143d729305baa94cbd8ab990979e325...b02fdea4902c2b93b7d34a83a6f05da4ececb7d3).

<div class="md-step-kicker"><span>OPTION A</span><strong>Terminal A · this project's repository root</strong></div>

Follow the [existing setup](./installation) for the default inputs, then prepare the local MuJoCo environment:

```bash
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
```

Download just the v8 weight into its own directory using this project's existing checked downloader.
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

Probe v7 and v8 with identical settings. A new timestamped report directory keeps earlier evidence intact:

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
inspect loading, finite values and posture. It is not a Rough + Backlash recovery or yaw evaluation,
and it does not replace the Isaac playground controller.
These new commands have not completed this project's v8 runtime retest.

## 4. Training: continue in two stages {#training}

### Obtain the checkpoints first; ONNX is not a training save

Full training needs a Linux/CUDA GPU, Python 3.12, `uv` and the upstream locked dependencies.
The task is `Mjlab-VelStand-Rough-Backlash-MicroDuck`: full collisions, rough terrain,
BAM XL330 actuators and backlash, not the simplified probe environment above.

BC loads two teachers in addition to the resume checkpoint. Confirm access to these original `.pt` files first:

| Input | Upstream W&B run | File |
| --- | --- | --- |
| v7 resume checkpoint | `pollen-robotics/mjlab_microduck/j4i6yoq2` | `model_1250.pt` |
| Recovery teacher | `pollen-robotics/mjlab_microduck/69u48n8l` | `model_9750.pt` |
| Walking teacher | `pollen-robotics/mjlab_microduck/441tzs6d` | `model_3750.pt` |
| Selected upstream stage A result | `pollen-robotics/mjlab_microduck/qz5g3bwi` | `model_1750.pt` |

This project has not verified public download access to those W&B files.
If they are unavailable, stop at weight playback and studying the method.
Renaming an ONNX file to `.pt` does not restore training state or replace the teachers' checkpoints.
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

### Stage A: fix the stuck recovery

Upstream used `333ef7b` for this stage: joint masking and broader starting states, without stage B's yaw remap.
Using the latest combined configuration would not reproduce the same recovery ablation.

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

### Stage B: keep recovery and calibrate turning

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

These commands show the **original upstream lineage**: the second explicitly reads upstream's stage A result,
not the output you just trained. To chain your own experiment, replace its run and checkpoint with
your independently evaluated stage A selection and record the new provenance.
Do not label your new run as the official v8.

Both stages use ordinary resume, preserving step counts and curriculum progress for fine-tuning.
The commands explicitly remove `MICRODUCK_WARM_START` to avoid inheriting an old `=1` setting that resets the curricula.
That environment variable is not the same as the retained `WARM_START=True` configuration constant.
See the [upstream load patch](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/tasks/mdp.py).

## 5. Select checkpoints by behavior, not just reward {#evaluation}

Track recovery, turning and walking separately. Select on development cases, then evaluate in independent processes
with new seeds. The checklist below is this project's proposed retest design, not an included one-command evaluator
or an already completed test.

| Check | Keep identical | Save |
| --- | --- | --- |
| Recovery | Start families, joint randomization, model and duration for v7/v8 | Successes/total, stuck rate, recovery time, re-falls |
| Turning | Both signs; separate in-place and moving turns | Actual yaw rate, error and falls, not only surviving samples |
| Straight walking | Commands, friction and actuator settings | Actual speed, lateral/yaw drift and falls |
| Smoothness | Sampling rate and measurement interval | Body angular velocity, impacts and continuous real-time recovery video |

Fix recovery height/tilt thresholds, the required stable-standing duration, timeouts and denominators before comparing.
Do not grade v7 strictly and v8 generously. The same principle applies to [continuous-roll acceptance](../isaac/roll-validation).

::: warning A gap in the public evaluation tools
The upstream record refers to `claude_experiments/velstand_rise_battery.py`, `velstand_yaw_probe.py`
and related scripts that are absent from the pinned public Git tree.
Copying those paths does not make the official statistics reproducible.
Strict reproduction requires obtaining the matching tools and definitions, or implementing and publishing an evaluator
with its differences stated. Sourced training commands do not establish checkpoint access, available evaluation tools or hardware readiness.
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
seeds, raw logs, independent evaluations and real-time footage for each run.
An ONNX file and one attractive video are not enough for another reader to reproduce your decisions.
Use `work/velstand-v8/` for working records and `artifacts/velstand-v8/` for evidence and export candidates;
place a completed tutorial companion package in `output/` without overwriting historical cases.

## 6. When should v8 become the default? {#adoption}

First complete the matched MuJoCo comparison. Then separately check the Isaac observation order, action scales,
actuator differences, walking/recovery behavior and transitions to other skills.
Equal interface dimensions do not establish equal behavior across engines.

This project currently adds only the v8 method guide: the default downloader still selects v7,
and the playground retains its historical walking/standing and sitting combination.
This update does not start training, update the USD or claim local acceptance of v8.
See [upstream alignment](../reference/upstream-alignment) for the retained versions.

<div class="md-page-complete">
  <strong>Now you know why to consider a new weight, not just where to download it.</strong>
  <p>Check the teachers, data and rewards, then train in small steps and evaluate independently. Promote a new policy only after it works better in your own environment.</p>
</div>
