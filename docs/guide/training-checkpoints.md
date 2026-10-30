# Continue from a training checkpoint

An ONNX file lets the duck perform a learned behavior. A full training checkpoint gives you a starting point
for teaching it more. Upstream published training bundles on 2026-10-27. This guide uses the final VelStand
checkpoint to work through **input verification → a small continuation run → independent evaluation → candidate export**,
without changing the existing introductory route.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Outcome</span><strong>Run log and trial model</strong></div>
  <div role="listitem"><span>Platform</span><strong>Linux · CUDA</strong></div>
  <div role="listitem"><span>Starting point</span><strong>Student + two teachers</strong></div>
  <div role="listitem"><span>Checks</span><strong>Docs checked; GPU run pending</strong></div>
</div>

::: info Keep the two routes separate
This page continues training from a published result. The [original two-stage experiment](./velstand-v8#training)
explains how that result was produced. They are not the same experiment. This page does not submit paid cloud jobs,
upload logs or policies, or replace `upstream.lock`, the Isaac playground, historical USD assets or
the [native Isaac training task](../isaac/training).
The procedure below still requires validation on a Linux GPU; it is not a newly completed training result from this project.
:::

## 1. What is available, and what is still missing? {#available}

As checked on 2026-10-30, the official [training repository](https://huggingface.co/pollen-robotics/microduck-training/tree/64d28ce092253c509b51031ec7ccb53790a00d0d)
contains 9 checkpoint bundles. Start with one route whose inputs and purpose are clear:

| Input | Bundle ID | Role here |
| --- | --- | --- |
| Final VelStand | `velstand/0045i2si_2749` | Student checkpoint to continue from |
| Recovery teacher | `microduck_stand/69u48n8l_9750` | Preserve recovery demonstrations |
| Walking teacher | `velocity2/441tzs6d_3750` | Avoid forgetting how to walk while improving recovery |
| Roll | `microduck_roulade/blrqbcit_750` | A `.pt` is public, but its source commit is missing; not our strict-reproduction example |

ONNX is for deployed inference. A full `.pt` can contain the actor, critic, normalization, optimizer,
iteration and curriculum step count. `bundle.json` records file provenance, hashes, teachers and parent checkpoints;
`wandb_config.yaml` records configuration. Download availability does not establish loading compatibility or better behavior after training.

The checked training revision still lacks the historical v7 starting point `j4i6yoq2_1250` and stage A result
`qz5g3bwi_1750`. The complete recovery and yaw evaluation scripts are also absent from the selected public source.
We can therefore prepare to **continue from the final result**, but cannot claim that every input needed to
reproduce the full original statistics is available.

## 2. Pin the source and inputs {#sources}

| Input | Revision used here |
| --- | --- |
| Source with the bundle entry point | `bae39f5900b318f7e87fc485c30a31213cfa14eb` |
| Training repository revision | `64d28ce092253c509b51031ec7ccb53790a00d0d` |
| Student file | `model_2749.pt` |
| Student SHA-256 | `2c185f1e6982a0a43d41403239bc0c5b0a9d654e4840d25572200c16abe2aa6b` |
| Original training source | `3750776761ecfaa5671b36972087cafba45b8527` |

The original training revision predates `--init-checkpoint`. Checking out old code and copying a new command will not work.
This page selects the newer revision with that entry point. Compared with the original revision, the VelStand environment
configuration, `mdp.py` and `uv.lock` are unchanged; teacher loading gains a Hub path. This is a compatibility continuation
experiment, not an exact replay of the old runtime environment. See the [pinned source comparison](https://github.com/pollen-robotics/microduck_rl/compare/3750776761ecfaa5671b36972087cafba45b8527...bae39f5900b318f7e87fc485c30a31213cfa14eb).

::: warning A filename does not establish that a patch exists
This VelStand bundle lists `uncommitted.diff`, but its contents are a Git status record showing a clean working tree
and an empty `git diff` section. It is not a patch to apply. Read it before deciding; do not blindly run `git apply`.
Likewise, do not combine the bundle README's historical checkout with its newer entry-point example and call it verified.
:::

<div class="md-step-kicker"><span>STEP A</span><strong>Linux host with CUDA · this project's repository root</strong></div>

Use an NVIDIA GPU, a working driver, Python **3.12** and `uv`; upstream requires Python below 3.13.
A Mac can read the material and check the docs, but this page supplies no Mac training acceptance result.
Do not switch the default `reference/microduck_rl/` checkout. Create a separate experiment directory below.
If it already exists, inspect its revision and changes rather than forcing a checkout or overwriting an earlier experiment.

```bash
git clone --filter=blob:none --no-checkout \
  https://github.com/pollen-robotics/microduck_rl.git reference/microduck_rl-training
cd reference/microduck_rl-training
git checkout --detach bae39f5900b318f7e87fc485c30a31213cfa14eb
mkdir -p ../../work/training-checkpoints/logs
ln -s ../../work/training-checkpoints/logs logs
export HF_HUB_CACHE="$PWD/../training-checkpoints/hub"
uv sync --frozen
```

Run the remaining commands in this checkout and the same terminal. Source belongs under `reference/`, the shared
download cache under `reference/training-checkpoints/hub/`, and the log symlink points to
`work/training-checkpoints/logs/`. Restore `HF_HUB_CACHE` in a new terminal to avoid downloading another copy elsewhere.

## 3. Check provenance before downloading, and hashes before loading {#inputs}

This block only downloads the three trusted official checkpoints and their documentation. It does not deserialize
`.pt` files or start training. Metadata and files come from the same immutable revision; any hash mismatch stops the check.

```bash
uv run python - <<'PY'
import hashlib
import json
from pathlib import Path
from huggingface_hub import hf_hub_download

repo = "pollen-robotics/microduck-training"
revision = "64d28ce092253c509b51031ec7ccb53790a00d0d"
bundles = (
    "velstand/0045i2si_2749",
    "microduck_stand/69u48n8l_9750",
    "velocity2/441tzs6d_3750",
)
for bundle in bundles:
    prefix = f"bundles/{bundle}"
    meta_path = hf_hub_download(repo, f"{prefix}/bundle.json", revision=revision)
    meta = json.loads(Path(meta_path).read_text())
    if meta["id"] != bundle:
        raise ValueError(f"bundle ID mismatch: {bundle}")
    name = meta["checkpoint_file"]
    if Path(name).name != name or not name.endswith(".pt"):
        raise ValueError(f"invalid checkpoint filename: {bundle}")
    checkpoint = Path(hf_hub_download(repo, f"{prefix}/{name}", revision=revision))
    with checkpoint.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != meta["checkpoint_sha256"]:
        raise ValueError(f"hash mismatch: {bundle}")
    if bundle == bundles[0]:
        if actual != "2c185f1e6982a0a43d41403239bc0c5b0a9d654e4840d25572200c16abe2aa6b":
            raise ValueError("student differs from this guide's pinned checkpoint")
    for filename in ("README.md", "wandb_config.yaml"):
        hf_hub_download(repo, f"{prefix}/{filename}", revision=revision)
    if meta["code"].get("uncommitted_diff"):
        hf_hub_download(repo, f"{prefix}/uncommitted.diff", revision=revision)
    print(f"verified {bundle} {actual}")
PY
```

Expect three `verified` lines. They establish that downloaded bytes match the manifest, not that the behavior passes.
Recheck provenance when choosing another bundle: a matching hash does not make an untrusted `.pt` safe to load.

### Pin both teachers as well

In the **separate checkout**, open `src/mjlab_microduck/tasks/distill.py`, find `default_bc_cfg()`,
and replace only these four existing field values. Do not add a second configuration:

```python
"hf_checkpoint": "hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/microduck_stand/69u48n8l_9750",
"anchor_hf_checkpoint": "hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velocity2/441tzs6d_3750",
"wandb_run_path": None,
"anchor_wandb_run_path": None,
```

The first two prevent teachers from following a moving remote `main`. The last two disable fallback to W&B when
the Hub fetch fails. Keep `checkpoint_path` and `anchor_checkpoint_path` at `None`; they take precedence over the Hub.
Read the downloaded student's configuration to check teacher identity, observation/action order, normalization and rewards.
Then inspect your local changes:

```bash
git diff --check
git diff -- src/mjlab_microduck/tasks/distill.py
uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck --help
```

Only the four field values should differ at this point. Retain that diff as an experiment input; do not submit it to the
official repository. If a teacher is unavailable, fix the download instead of disabling BC to force training to start.

## 4. Run five updates to check the pipeline {#training}

Check that the GPU is available, then try 64 environments and 5 PPO updates. These are this tutorial's small smoke-test
budget, not upstream's training budget, a minimum GPU specification or a success-rate promise.

```bash
env -u MICRODUCK_WARM_START uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --init-checkpoint hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velstand/0045i2si_2749 \
  --env.scene.num-envs 64 --agent.max-iterations 5 \
  --agent.seed 20261030 --agent.logger tensorboard \
  --agent.run-name hub-smoke --agent.save-interval 1
```

Do not combine `--init-checkpoint` with `--agent.resume` or `--wandb-run-path`.
Removing `MICRODUCK_WARM_START` preserves iteration and curriculum counters: same-task continuation should not silently
restart the curriculum. `--agent.max-iterations 5` supplies the number of updates for this invocation; it does not change
the saved iteration from 2749 to 5. The seed records conditions, but does not promise bitwise equality across hardware.
`tensorboard` writes local logs without requiring this run to be uploaded to W&B.

Check these four items before increasing the environment count or budget:

1. The student and both teachers load without shape errors, W&B fallback or missing files.
2. Simulation values, PPO losses and actions remain finite, without NaNs, out-of-memory errors or persistent abnormal contacts.
3. `logs/rsl_rl/velstand/<timestamp>_hub-smoke/` contains `params/env.yaml`, `params/agent.yaml` and new `model_*.pt` files.
4. Checkpoints and logs can be read again, and curriculum counters did not unexpectedly reset. Inspect metrics separately
   to determine whether BC received enough samples; exiting after five updates does not establish learned behavior.

If any check fails, use the [troubleshooting table](#troubleshooting). If they pass, still complete the baseline evaluation
below before a bounded fine-tuning run. Change only one category at a time—environment count, rewards or curriculum—and
record why. Give the new candidate its own name, not “official v8”.

## 5. Evaluate under matched conditions, then export your candidate {#evaluation}

Use the downloaded `model_2749.pt` as the baseline, then compare your candidate with the same model, action scaling,
sampling rate, initial states and metric definitions. Select on development cases and retest in independent processes
with new seeds.

| Question | What to record |
| --- | --- |
| Does it recover better? | Successes/total, recovery time and re-falls, separated by face-down, face-up, side and sitting starts |
| Does it follow yaw commands? | Commanded versus actual yaw, separated by in-place/moving and both signs; do not drop falls from the denominator |
| Has walking regressed? | Speed error, lateral drift and falls against the matched baseline |
| Is motion smooth? | Body angular rates, contact impacts and continuous real-time footage, not just a selected successful moment |

This is an evaluation design, **not an included one-command evaluator**. Upstream's
`claude_experiments/velstand_rise_battery.py` and `velstand_yaw_probe.py` are still absent from the selected public Git tree.
Do not claim to reproduce their percentages until the matching tools are obtained, or equivalent definitions are implemented
and published. See the [existing evaluation principles](./velstand-v8#evaluation).

Select a checkpoint from your own run and replace the absolute path below with the real file.
Export produces a candidate; it does not install it on a robot or replace a default model:

```bash
candidate=/absolute/path/to/your/model_selected.pt
test -f "$candidate" || exit 1
export_dir="$PWD/../../artifacts/training-checkpoints/export-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$export_dir"
uv run scripts/export.py Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --checkpoint-file "$candidate" --onnx-file "$export_dir/velstand-candidate.onnx"
sha256sum "$candidate" "$export_dir/velstand-candidate.onnx"
```

The exporter includes observation normalization and metadata such as `task_id`, `checkpoint_sha256`, `export_commit`
and `export_dirty`. An `export_dirty=true` value may come from the teacher pinning above: retain and explain that diff
instead of discarding experiment changes merely to make the flag false. The exporting source revision is not the original
training revision; keep both the bundle metadata and your new run's provenance.
Test ONNX playback separately after export. Moving to Isaac additionally requires observation, action-scale, actuator
and skill-transition checks.

## 6. Troubleshoot the right layer {#troubleshooting}

| Symptom | First check |
| --- | --- |
| `--init-checkpoint` is unrecognized | Are you still in the historical `3750776`/v8 checkout? Check HEAD and locked dependencies; do not upgrade the whole system |
| A failed Hub fetch asks for W&B login | Are both teacher W&B paths `None`? Fix the download rather than substituting random teachers |
| `.pt` shape or normalization mismatch | Task ID, student/teacher identities, configuration and input hashes; renaming a file is not a fix |
| Continuation restarts the curriculum | Check for a leftover `MICRODUCK_WARM_START=1`; ordinary resume and a new-task warm start are different |
| GPU out of memory | Reduce environment count and stop only your own trial, not another project's active work |
| Reward improves while behavior regresses | Return to matched behavior evaluation; retain the baseline and do not promote a training curve |

## 7. Preserve evidence before considering sharing {#provenance}

Record “parameter → rationale → change → comparison → decision”: source SHA and diff, dependency lock, all three input
hashes, task and seeds, exact launch arguments, environment/reward configurations, output hashes, independent evaluation
and real-time footage. Working records belong in `work/training-checkpoints/`, candidates and evidence in
`artifacts/training-checkpoints/`, and a finished tutorial companion package in `output/`. Do not overwrite historical results.

Upstream now provides `share-training` / `publish --share-training`, but this page does not invoke them automatically.
A bundle may contain full commands, usernames, uncommitted source differences, W&B configuration and private paths.
Review credentials and unrelated content before sharing; a private-by-default destination does not remove that obligation.
The official training repository's checked model card does not declare a license. This project does not rehost or relicense
the weights; establish the applicable license before redistribution, and distinguish code from meshes as described in
the [project licensing notes](../project/licensing).

Implementation sources: [training-bundle guide](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/docs/training_checkpoints.md),
[checkpoint entry point](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/src/mjlab_microduck/checkpoints.py),
and [pinned student provenance](https://huggingface.co/pollen-robotics/microduck-training/blob/64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velstand/0045i2si_2749/bundle.json).

<div class="md-page-complete">
  <strong>The takeaway: not just a behavior to play, but a checkpoint to continue from.</strong>
  <p>Verify the checkpoint and teachers, take a small training step, then use matched results to decide whether to adopt it—and leave a trail the next reader can follow.</p>
</div>
