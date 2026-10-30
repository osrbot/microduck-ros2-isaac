# Continue training a model

This chapter shows how to load an official trained MicroDuck model, continue training it, and export your own model.
It uses **MuJoCo/mjlab**. For the Isaac Lab task introduced earlier, return to [chapter 10](../isaac/training).

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Simulator</span><strong>MuJoCo</strong></div>
  <div role="listitem"><span>Platform</span><strong>Linux + CUDA</strong></div>
  <div role="listitem"><span>Models</span><strong>1 learner + 2 teachers</strong></div>
  <div role="listitem"><span>First run</span><strong>5 updates</strong></div>
</div>

> Validation status: the commands have been checked against upstream source. GPU training still needs testing in this project.

## 1. Set up the training environment {#sources}

Use a Linux computer with an NVIDIA GPU, a working driver, Python **3.12** and `uv`.
Open a terminal at this project's root and run the commands below. They create a separate training directory and install its dependencies.
If `reference/microduck_rl-training/` already exists, check its revision and local changes before reusing it.

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

Run the remaining commands from `reference/microduck_rl-training/` in the same terminal.
Downloaded models go in `reference/training-checkpoints/hub/`; logs go in this project's `work/training-checkpoints/logs/`.

## 2. Download the models and set the teachers {#inputs}

This example uses three models:

| Model | Purpose |
| --- | --- |
| VelStand | The model you will continue training; it can already walk, stand and recover from falls |
| Recovery teacher | Provides reference actions for getting up |
| Walking teacher | Helps preserve the existing walking behavior |

A teacher is a trained model that provides reference actions. The training program uses both teachers and rewards to improve the learner.

Copy the whole block below into your terminal. It downloads all three models and their documentation, then checks file integrity.

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

Three `verified` lines mean all three models were downloaded and passed the file check.

Next, open `src/mjlab_microduck/tasks/distill.py` in the current training directory, find `default_bc_cfg()`,
and change these four existing settings to the following values:

```python
"hf_checkpoint": "hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/microduck_stand/69u48n8l_9750",
"anchor_hf_checkpoint": "hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velocity2/441tzs6d_3750",
"wandb_run_path": None,
"anchor_wandb_run_path": None,
```

The first two settings select the teacher downloads. Setting the other two to `None` makes a failed download report an error directly.
Keep `checkpoint_path` and `anchor_checkpoint_path` at `None` as well so the configured downloads are used.

Check your changes and the training command:

```bash
git diff --check
git diff -- src/mjlab_microduck/tasks/distill.py
uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck --help
```

`git diff` should show only those four changed settings. The final command should display the training program's help.

## 3. Start training {#training}

Start with **64 parallel environments and 5 PPO updates**. PPO is the reinforcement learning algorithm used here.
This short run checks model loading, training and saving. Run it when the GPU is available:

```bash
env -u MICRODUCK_WARM_START uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --init-checkpoint hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velstand/0045i2si_2749 \
  --env.scene.num-envs 64 --agent.max-iterations 5 \
  --agent.seed 20261030 --agent.logger tensorboard \
  --agent.run-name hub-smoke --agent.save-interval 1
```

The main parameters are:

| Parameter | Purpose |
| --- | --- |
| `--init-checkpoint` | Continue from the downloaded VelStand model |
| `--env.scene.num-envs 64` | Run 64 simulation environments at once; reduce this if GPU memory runs out |
| `--agent.max-iterations 5` | Perform 5 updates in this run while keeping the saved training progress |
| `--agent.save-interval 1` | Save a model after each update |
| `--agent.logger tensorboard` | Store training logs locally |
| `--agent.seed 20261030` | Fix the random seed for this experiment so later comparisons can record the same setting |

The initial `env -u MICRODUCK_WARM_START` preserves the saved iteration and curriculum counters.
Use the command as shown with `--init-checkpoint`; it does not need an additional `--agent.resume` or `--wandb-run-path`.

## 4. Check the results {#evaluation}

When the program finishes, open `logs/rsl_rl/velstand/<timestamp>_hub-smoke/` and check these three items:

1. `params/env.yaml` and `params/agent.yaml`: the environment and training settings for this run.
2. New `model_*.pt` files: the models saved during this run.
3. Training logs: no NaNs, out-of-memory errors or teacher-loading failures, and no unexpected reset of curriculum progress.

Five updates mainly check that the process works. Before a longer run, keep the original `model_2749.pt` as your baseline.
Change one category at a time, such as rewards or starting poses, then compare under the same conditions:

| Behavior | What to check |
| --- | --- |
| Recovery | Start face-down, face-up, on the side and sitting; record successes, recovery time and re-falls |
| Turning | Test left and right turns both in place and while walking; compare commanded and actual yaw rates |
| Walking | Compare speed error, lateral drift and falls |
| Smoothness | Look for sudden body shaking or hard foot impacts, and save the complete replay |

After choosing a model, start a fresh evaluation process and test with another set of random seeds.
The complete upstream evaluation scripts are not public. This page lists the checks; automated scoring requires those scripts or an equivalent implementation.
See [Versions and sources](#available).

## 5. Export an ONNX model {#export}

Choose a `model_*.pt` from your own training run, replace the first line below with its actual absolute path, and run:

```bash
candidate=/absolute/path/to/your/model_selected.pt
test -f "$candidate" || exit 1
export_dir="$PWD/../../artifacts/training-checkpoints/export-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$export_dir"
uv run scripts/export.py Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --checkpoint-file "$candidate" --onnx-file "$export_dir/velstand-candidate.onnx"
sha256sum "$candidate" "$export_dir/velstand-candidate.onnx"
```

The exported `velstand-candidate.onnx` goes into a new directory under this project's `artifacts/training-checkpoints/`.
The exporter includes the observation-normalization parameters. Replay the ONNX model next and check that its behavior matches training.
Using it in Isaac also requires checking observation order, action scaling and actuator settings.

## Troubleshooting {#troubleshooting}

| Problem | What to do |
| --- | --- |
| `--init-checkpoint` is unrecognized | Check the source revision in step 1; older code does not have this argument |
| A failed download asks for W&B login | Check that both teacher W&B settings are `None`, then resolve the download error |
| Model loading reports a shape mismatch | Check the task name and that the learner and teacher files are the intended ones |
| Training progress starts at zero | Check that the command still begins with `env -u MICRODUCK_WARM_START` |
| GPU memory runs out | Reduce `--env.scene.num-envs` and retry the short run |
| Reward rises but behavior gets worse | Compare with the original model using step 4, then review the reward settings |

## Versions and sources {#available}

The exact versions used in this example are kept below for troubleshooting.

::: details Source revisions, model versions and file checksums

| Item | Version used here |
| --- | --- |
| Training source | `bae39f5900b318f7e87fc485c30a31213cfa14eb` |
| Official training model repository | `64d28ce092253c509b51031ec7ccb53790a00d0d` |
| VelStand | `velstand/0045i2si_2749`, file `model_2749.pt` |
| Recovery teacher | `microduck_stand/69u48n8l_9750` |
| Walking teacher | `velocity2/441tzs6d_3750` |
| VelStand file SHA-256 | `2c185f1e6982a0a43d41403239bc0c5b0a9d654e4840d25572200c16abe2aa6b` |

The model was originally trained with source `3750776761ecfaa5671b36972087cafba45b8527`.
This tutorial uses a newer revision because it adds `--init-checkpoint`. The VelStand environment configuration,
`mdp.py` and `uv.lock` are unchanged between the two revisions.
[View the source comparison](https://github.com/pollen-robotics/microduck_rl/compare/3750776761ecfaa5671b36972087cafba45b8527...bae39f5900b318f7e87fc485c30a31213cfa14eb).

The bundle's `uncommitted.diff` contains only a working-tree status record and an empty diff; no patch needs applying.
As checked on 2026-10-30, the official repository has 9 bundles. The original experiment's `j4i6yoq2_1250` and `qz5g3bwi_1750` are still absent.
The roll bundle `microduck_roulade/blrqbcit_750` has a `.pt` file but no original source commit.
This chapter therefore continues from the published final VelStand model.
For the original training process, see [Recovery and turning training](./velstand-v8#training).

The upstream scripts `claude_experiments/velstand_rise_battery.py` and `velstand_yaw_probe.py` are absent from the selected source.
Reproducing the reported success rates requires those scripts or an implementation with equivalent, documented evaluation conditions.

:::

## Keep a training record {#provenance}

Save four things for each run: code and model versions, parameter changes and their reasons, training logs, and behavior-test results.
Use `work/training-checkpoints/` for logs, `artifacts/training-checkpoints/` for exported models and replays,
and `output/` for the finished tutorial companion files.

::: details Model provenance, export metadata and sharing

Keep `bundle.json`, `wandb_config.yaml` and the file checksums from the download. Load `.pt` files only from trusted sources.
The exported model's `task_id`, `checkpoint_sha256`, `export_commit` and `export_dirty` track its provenance.
Changing the teacher settings earlier may produce `export_dirty=true`; retain that configuration diff.
This experiment uses a separate directory, while the project's default models and `upstream.lock` settings stay as configured.

Upstream provides `share-training` and `publish --share-training` for sharing training bundles.
Before sharing, check commands, configuration and source diffs for passwords, tokens and private paths.
The checked official model card does not declare a weight license; confirm permission before redistributing weights.
See the [project licensing notes](../project/licensing).

References: [training-bundle guide](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/docs/training_checkpoints.md),
[checkpoint-loading code](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/src/mjlab_microduck/checkpoints.py),
[official model directory](https://huggingface.co/pollen-robotics/microduck-training/tree/64d28ce092253c509b51031ec7ccb53790a00d0d),
and [VelStand provenance](https://huggingface.co/pollen-robotics/microduck-training/blob/64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velstand/0045i2si_2749/bundle.json).

:::
