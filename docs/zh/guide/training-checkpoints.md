# 用现成模型继续训练

这一章教你加载官方已经训练好的 MicroDuck 模型，在它的基础上继续训练，最后导出自己的模型。
使用的是 **MuJoCo/mjlab**。如果你要继续做前面的 Isaac Lab 任务，请看[第 10 章](../isaac/training)。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>仿真平台</span><strong>MuJoCo</strong></div>
  <div role="listitem"><span>运行环境</span><strong>Linux + CUDA</strong></div>
  <div role="listitem"><span>需要模型</span><strong>1 个训练模型 + 2 个教师</strong></div>
  <div role="listitem"><span>第一次运行</span><strong>先做 5 次更新</strong></div>
</div>

> 验证进度：命令已按上游源码核对，GPU 训练步骤尚未在本项目实测。

## 1. 准备训练环境 {#sources}

准备一台带 NVIDIA 显卡的 Linux 电脑，安装好驱动、Python **3.12** 和 `uv`。
在本项目根目录打开终端，执行下面的命令。它会创建单独的训练目录并安装依赖。
如果 `reference/microduck_rl-training/` 已存在，先检查里面的版本和修改，再决定是否复用。

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

后面的命令都在 `reference/microduck_rl-training/` 中、同一个终端里执行。
下载的模型保存在 `reference/training-checkpoints/hub/`，日志保存在本项目的 `work/training-checkpoints/logs/`。

## 2. 下载模型，设置教师 {#inputs}

这次用三个模型：

| 模型 | 作用 |
| --- | --- |
| VelStand | 你要继续训练的模型，已有行走、站立和起身能力 |
| 起身教师 | 训练时提供起身动作的参考 |
| 行走教师 | 帮助保留原有的行走能力 |

“教师”就是提供参考动作的现成模型。训练程序会同时参考两个教师，再根据奖励调整正在训练的模型。

把下面整段复制到终端运行。它会下载三个模型及其说明文件，并自动检查下载是否完整。

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

看到三行 `verified`，说明三个模型都已下载并通过文件校验。

然后打开当前训练目录下的 `src/mjlab_microduck/tasks/distill.py`，找到 `default_bc_cfg()`，
把下面四个已有配置项改成这些值：

```python
"hf_checkpoint": "hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/microduck_stand/69u48n8l_9750",
"anchor_hf_checkpoint": "hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velocity2/441tzs6d_3750",
"wandb_run_path": None,
"anchor_wandb_run_path": None,
```

前两项指定教师模型的下载地址；后两项设为 `None`，让下载失败时直接报错，方便排查。
`checkpoint_path` 和 `anchor_checkpoint_path` 也保持 `None`，以便使用上述下载地址。

改完后检查配置和训练命令是否可用：

```bash
git diff --check
git diff -- src/mjlab_microduck/tasks/distill.py
uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck --help
```

`git diff` 应只显示刚修改的四个配置项，最后一条命令应显示训练程序的帮助。

## 3. 启动训练 {#training}

先用 **64 个并行环境、5 次 PPO 更新**试跑。PPO 是这里使用的强化学习算法；
这次短跑用来检查加载、训练和保存是否正常。显卡空闲时执行：

```bash
env -u MICRODUCK_WARM_START uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --init-checkpoint hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velstand/0045i2si_2749 \
  --env.scene.num-envs 64 --agent.max-iterations 5 \
  --agent.seed 20261030 --agent.logger tensorboard \
  --agent.run-name hub-smoke --agent.save-interval 1
```

几个主要参数的含义：

| 参数 | 作用 |
| --- | --- |
| `--init-checkpoint` | 从刚下载的 VelStand 模型继续训练 |
| `--env.scene.num-envs 64` | 同时运行 64 个仿真环境；显存不足时可减少 |
| `--agent.max-iterations 5` | 本次执行 5 次更新，保留原有训练进度 |
| `--agent.save-interval 1` | 每次更新后保存模型 |
| `--agent.logger tensorboard` | 把训练日志保存在本机 |
| `--agent.seed 20261030` | 固定本次实验的随机种子，便于后续对比 |

命令开头的 `env -u MICRODUCK_WARM_START` 用来保留已有的训练轮数和课程进度。
使用 `--init-checkpoint` 时，保持这条命令的写法即可，无需再添加 `--agent.resume` 或 `--wandb-run-path`。

## 4. 检查训练结果 {#evaluation}

程序结束后，打开 `logs/rsl_rl/velstand/<时间戳>_hub-smoke/`，确认有这三个结果：

1. `params/env.yaml` 和 `params/agent.yaml`：本次环境与训练参数。
2. 新的 `model_*.pt`：本次保存的模型。
3. 训练日志：没有 NaN、显存不足、教师模型加载失败等错误，课程进度也没有意外归零。

五次更新主要用于检查流程。正式训练前，先保留原始 `model_2749.pt`，作为对比用的原模型。
后续每次只调整一类设置，例如奖励或初始姿态，再在相同条件下比较：

| 检查动作 | 看什么 |
| --- | --- |
| 起身 | 从俯卧、仰卧、侧躺和坐姿开始，记录成功次数、用时和再次摔倒次数 |
| 转向 | 分别测试原地和行走中的左右转向，比较目标角速度与实际角速度 |
| 行走 | 比较速度误差、左右漂移和摔倒次数 |
| 动作平顺性 | 观察身体是否突然抖动、脚部冲击是否明显，并保留完整回放 |

选出较好的模型后，重新启动评估进程，换一组随机种子再测一次。
上游完整评估脚本尚未公开，本页提供检查项目；自动统计需要补齐评估脚本，见[版本与来源](#available)。

## 5. 导出 ONNX 模型 {#export}

从自己的训练目录里选一个 `model_*.pt`，把下方第一行换成它的实际绝对路径，再运行：

```bash
candidate=/absolute/path/to/your/model_selected.pt
test -f "$candidate" || exit 1
export_dir="$PWD/../../artifacts/training-checkpoints/export-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$export_dir"
uv run scripts/export.py Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --checkpoint-file "$candidate" --onnx-file "$export_dir/velstand-candidate.onnx"
sha256sum "$candidate" "$export_dir/velstand-candidate.onnx"
```

导出的 `velstand-candidate.onnx` 会放在本项目 `artifacts/training-checkpoints/` 下的新目录中。
导出器会一并保存观测归一化参数。接下来先用 ONNX 做回放，检查动作是否与训练时一致。
如果要接入 Isaac，还需要核对观测顺序、动作缩放和执行器设置。

## 常见问题 {#troubleshooting}

| 问题 | 处理方法 |
| --- | --- |
| 提示不认识 `--init-checkpoint` | 回到第 1 步检查源码版本，旧版源码没有这个参数 |
| 下载失败后要求登录 W&B | 检查两个教师的 W&B 配置是否都设为 `None`，再处理下载错误 |
| 模型加载时报维度不匹配 | 检查任务名称，以及训练模型和教师文件是否选对 |
| 训练进度从零开始 | 检查命令开头是否保留了 `env -u MICRODUCK_WARM_START` |
| 显存不足 | 减少 `--env.scene.num-envs`，再重新试跑 |
| 奖励变高，但动作变差 | 用第 4 步的动作测试与原模型比较，重新检查奖励设置 |

## 版本与来源 {#available}

下面保留本例的具体版本，便于遇到问题时核对。

::: details 查看源码、模型版本和文件校验值

| 项目 | 本例使用的版本 |
| --- | --- |
| 训练源码 | `bae39f5900b318f7e87fc485c30a31213cfa14eb` |
| 官方训练模型库 | `64d28ce092253c509b51031ec7ccb53790a00d0d` |
| VelStand | `velstand/0045i2si_2749`，文件 `model_2749.pt` |
| 起身教师 | `microduck_stand/69u48n8l_9750` |
| 行走教师 | `velocity2/441tzs6d_3750` |
| VelStand 文件 SHA-256 | `2c185f1e6982a0a43d41403239bc0c5b0a9d654e4840d25572200c16abe2aa6b` |

该模型最初使用源码 `3750776761ecfaa5671b36972087cafba45b8527` 训练。本教程选用较新的源码，
因为它增加了 `--init-checkpoint`；对照两个提交，VelStand 环境配置、`mdp.py` 和 `uv.lock` 没有变化。
[查看源码差异](https://github.com/pollen-robotics/microduck_rl/compare/3750776761ecfaa5671b36972087cafba45b8527...bae39f5900b318f7e87fc485c30a31213cfa14eb)。

这个训练包中的 `uncommitted.diff` 只有工作区状态记录，补丁内容为空，无需应用。
截至 2026-10-30，官方模型库公开了 9 组检查点；原始实验的 `j4i6yoq2_1250` 和 `qz5g3bwi_1750` 尚未收录。
翻滚模型 `microduck_roulade/blrqbcit_750` 已有 `.pt`，但缺少原始源码提交号。
本章因此从已公开的最终 VelStand 模型继续训练。原始训练过程见[起身与转向训练](./velstand-v8#training)。

上游提到的 `claude_experiments/velstand_rise_battery.py`、`velstand_yaw_probe.py` 未在所选源码中公开。
要复现上游报告的成功率，需要取得这些脚本，或实现并说明等价的评估条件。

:::

## 保存训练记录 {#provenance}

每次训练保存四类内容：使用的代码和模型版本、修改的参数及理由、训练日志、动作测试结果。
日志放在 `work/training-checkpoints/`，导出的模型和回放放在 `artifacts/training-checkpoints/`，
整理好的教程配套文件放在 `output/`。

::: details 模型来源、导出信息和分享注意事项

下载时保留 `bundle.json`、`wandb_config.yaml` 和校验值。只加载来源可信的 `.pt` 文件。
导出模型中的 `task_id`、`checkpoint_sha256`、`export_commit` 和 `export_dirty` 用来追踪模型来源。
前面修改了教师配置，所以可能出现 `export_dirty=true`；保留这份配置改动即可。
本教程的实验目录与原有 `upstream.lock` 配置独立，项目默认模型保持原设置。

上游的 `share-training` 和 `publish --share-training` 可以分享训练包。
分享前检查命令、配置和源码差异中是否包含密码、令牌或私人路径。
官方训练库本次核对的模型卡未声明权重许可证，重新分发前需确认许可；参见[项目许可说明](../project/licensing)。

参考资料：[训练包用法](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/docs/training_checkpoints.md)、
[检查点加载代码](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/src/mjlab_microduck/checkpoints.py)、
[官方模型目录](https://huggingface.co/pollen-robotics/microduck-training/tree/64d28ce092253c509b51031ec7ccb53790a00d0d)、
[VelStand 来源记录](https://huggingface.co/pollen-robotics/microduck-training/blob/64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velstand/0045i2si_2749/bundle.json)。

:::
