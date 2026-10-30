# 拿到训练存档，接着练

以前拿到 ONNX，是让鸭子表演已经学会的动作；现在拿到完整训练存档，才有条件接着教它。
上游在 2026-10-27 公开了训练包。本页以最终 VelStand 检查点为例，走完
**核对输入 → 小规模续训 → 独立评估 → 导出候选**，不改变原来的入门路线。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>你会得到</span><strong>续训记录与候选模型</strong></div>
  <div role="listitem"><span>运行环境</span><strong>Linux · CUDA</strong></div>
  <div role="listitem"><span>起点</span><strong>学生 + 两个教师</strong></div>
  <div role="listitem"><span>本项目验证</span><strong>文档已检查，GPU 续训待验证</strong></div>
</div>

::: info 先分清两条路线
本页是从已发布策略继续训练；[原始两阶段实验](./velstand-v8#training)解释这个策略怎样形成。
两者不能混成同一次实验。本页不启动云端付费任务、不上传日志或策略，也不替换
`upstream.lock`、Isaac 游乐场、历史 USD 或[原生 Isaac 训练任务](../isaac/training)。
下面是待在 Linux GPU 上验证的操作流程，不是本项目已完成的新训练成绩。
:::

## 1. 先看拿到了什么，还缺什么 {#available}

截至 2026-10-30，官方[训练包目录](https://huggingface.co/pollen-robotics/microduck-training/tree/64d28ce092253c509b51031ec7ccb53790a00d0d)
公开了 9 组检查点。这里先选一条输入比较完整、目标清楚的路线：

| 材料 | 训练包 ID | 本页用途 |
| --- | --- | --- |
| 最终 VelStand | `velstand/0045i2si_2749` | 学生的续训起点 |
| 起身教师 | `microduck_stand/69u48n8l_9750` | 保留倒地恢复的示范 |
| 行走教师 | `velocity2/441tzs6d_3750` | 避免练起身时忘了走路 |
| 翻滚 | `microduck_roulade/blrqbcit_750` | 已有 `.pt`，但源码提交号缺失；暂不作为本页的严格复现示例 |

ONNX 用于部署推理；完整 `.pt` 可以包含 actor、critic、归一化、优化器、迭代号和课程步数。
`bundle.json` 记录这些文件的来源、哈希、教师和父检查点；`wandb_config.yaml` 记录配置。
文件能下载，不等于当前环境一定能加载，也不等于续训一定更好。

本页核对的训练库中，旧实验的 v7 起点 `j4i6yoq2_1250` 和阶段 A 结果 `qz5g3bwi_1750` 仍未收录。
完整起身、转向评估脚本也仍不在所选公开源码中。因此可以准备**从最终结果继续训练**，
但还不能声称已经具备从头重演全部上游统计的材料。

## 2. 固定源码和输入，别让一次实验混入两个版本 {#sources}

| 输入 | 本页固定值 |
| --- | --- |
| 带训练包入口的源码 | `bae39f5900b318f7e87fc485c30a31213cfa14eb` |
| 训练包库版本 | `64d28ce092253c509b51031ec7ccb53790a00d0d` |
| 学生文件 | `model_2749.pt` |
| 学生 SHA-256 | `2c185f1e6982a0a43d41403239bc0c5b0a9d654e4840d25572200c16abe2aa6b` |
| 原始训练源码 | `3750776761ecfaa5671b36972087cafba45b8527` |

原始训练源码没有新加入的 `--init-checkpoint`。不能一边检出旧提交，一边照抄新命令。
本页选择带入口的新提交；与原始提交比较，VelStand 环境配置、`mdp.py` 和 `uv.lock` 没有差异，
教师加载增加了 Hub 路径。这里做的是兼容性续训实验，不是逐字重演旧运行环境。
源码比较见[固定差异](https://github.com/pollen-robotics/microduck_rl/compare/3750776761ecfaa5671b36972087cafba45b8527...bae39f5900b318f7e87fc485c30a31213cfa14eb)。

::: warning 不要仅凭文件名应用补丁
这个 VelStand 包虽然列出 `uncommitted.diff`，实际内容是 Git 状态记录，显示工作区干净，
`git diff` 部分为空，不是待应用的补丁。先读文件，再判断；不要盲目执行 `git apply`。
同样，不要把 bundle README 里的旧源码检出与新入口拼起来当作已验证命令。
:::

<div class="md-step-kicker"><span>步骤 A</span><strong>有 CUDA 的 Linux 主机 · 本项目仓库根目录</strong></div>

需要 NVIDIA GPU、可用驱动、Python **3.12** 和 `uv`；上游要求 Python 小于 3.13。
Mac 可阅读材料、做文档检查，但本页没有提供 Mac 训练验收结果。
不要切换默认的 `reference/microduck_rl/`。下面创建独立实验目录；若目录已存在，
先核对版本和修改，不强制检出、不覆盖旧实验。

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

后续命令都在这个 checkout、同一终端中执行。源码归 `reference/`，共享下载缓存归
`reference/training-checkpoints/hub/`，日志通过链接归 `work/training-checkpoints/logs/`。
换终端后重新设置 `HF_HUB_CACHE`，避免把同一份权重下载到另一处。

## 3. 下载前核对来源，加载前核对哈希 {#inputs}

这一段只下载三个可信官方检查点及其说明，不反序列化 `.pt`，不启动训练。
元数据与文件都从同一个不可变版本获取；任意哈希不符就停止。

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

预期出现三行 `verified`。这只证明下载字节与清单匹配，不证明行为通过。
以后换成其他训练包，也必须重新核对来源；哈希匹配不能让不可信 `.pt` 变安全。

### 两个老师也必须固定版本

在**独立 checkout** 的 `src/mjlab_microduck/tasks/distill.py` 中，找到 `default_bc_cfg()`，
只替换以下四个已有字段的值，不添加第二份配置：

```python
"hf_checkpoint": "hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/microduck_stand/69u48n8l_9750",
"anchor_hf_checkpoint": "hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velocity2/441tzs6d_3750",
"wandb_run_path": None,
"anchor_wandb_run_path": None,
```

前两项防止教师随远端 `main` 变化；后两项禁止 Hub 失败后偷偷回退到另一套 W&B 下载。
`checkpoint_path` 和 `anchor_checkpoint_path` 保持 `None`，其优先级高于 Hub。
读取刚下载的学生配置核对教师身份、观测/动作顺序、归一化和奖励，再检查本地差异：

```bash
git diff --check
git diff -- src/mjlab_microduck/tasks/distill.py
uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck --help
```

此时只应有四个配置值的变更。保留这份差异作为实验输入，不提交回官方仓库。
教师取不到时先修下载，不删除 BC 来让训练“勉强启动”。

## 4. 先跑五轮，检查管线而不是刷成绩 {#training}

确认 GPU 空闲后，先检查 64 个环境、5 次 PPO 更新。这些是本教程的低成本检查预算，
不是上游训练预算、最低显卡规格或成功率承诺。

```bash
env -u MICRODUCK_WARM_START uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --init-checkpoint hf://pollen-robotics/microduck-training@64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velstand/0045i2si_2749 \
  --env.scene.num-envs 64 --agent.max-iterations 5 \
  --agent.seed 20261030 --agent.logger tensorboard \
  --agent.run-name hub-smoke --agent.save-interval 1
```

`--init-checkpoint` 不与 `--agent.resume` 或 `--wandb-run-path` 混用。
移除 `MICRODUCK_WARM_START` 是为了保留迭代号和课程计数；同任务续训不应该把课程突然清零。
`--agent.max-iterations 5` 传给 runner 的是本次更新次数，不是把已有的 2749 轮改成 5。
固定种子用于记录条件，不保证不同硬件间逐位一致。
`tensorboard` 只写本地日志，不要求把本轮实验写入 W&B。

先看这四项，再决定是否增加环境数和预算：

1. 学生和两个教师均成功加载，没有形状错误、W&B 回退或缺失文件。
2. 仿真、PPO 损失和动作都是有限值，没有 NaN、显存溢出或持续异常接触。
3. `logs/rsl_rl/velstand/<时间戳>_hub-smoke/` 中有 `params/env.yaml`、`params/agent.yaml` 和新的 `model_*.pt`。
4. 检查点和日志可重新读取，课程计数没有意外归零；BC 是否获得足够样本另看指标，不能只凭“五轮退出”判断学到了动作。

失败时先处理[排错表](#troubleshooting)。通过后，仍需先完成下一节的基线评估，再开展有界微调；
一次只改变环境数量、奖励或课程中的一类因素，并写明理由。新候选使用自己的名称，不继续冒用“官方 v8”。

## 5. 同条件评估，然后导出自己的候选 {#evaluation}

先把下载的 `model_2749.pt` 当基线，再比较自己的候选；两者使用相同模型、动作缩放、
采样率、初始状态和统计定义。选模用开发集，最后在独立进程里换新种子复测。

| 问题 | 记录什么 |
| --- | --- |
| 是否更会起身？ | 按正躺、仰躺、侧躺和坐姿分别记录成功/总数、起身耗时、再次摔倒 |
| 是否听转向指令？ | 原地/行走、正负方向分别记录指令与实际角速度；摔倒样本不能从分母消失 |
| 是否忘了走路？ | 速度误差、左右漂移、跌倒次数，与基线同条件对照 |
| 动作是否平顺？ | 身体角速度、接触冲击和连续原速录像，不能只挑一小段成功镜头 |

这里提供的是评估设计，**没有附带完整的一键评估器**。
上游提到的 `claude_experiments/velstand_rise_battery.py` 和 `velstand_yaw_probe.py` 仍未公开在所选 Git 树中。
未取得或自行实现并公开等价定义前，不宣称复现其百分比。参考[既有验收原则](./velstand-v8#evaluation)。

在自己的 run 中选出检查点，将下方绝对路径改为真实文件。导出只生成候选，不安装到机器人或替换默认模型：

```bash
candidate=/absolute/path/to/your/model_selected.pt
test -f "$candidate" || exit 1
export_dir="$PWD/../../artifacts/training-checkpoints/export-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$export_dir"
uv run scripts/export.py Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --checkpoint-file "$candidate" --onnx-file "$export_dir/velstand-candidate.onnx"
sha256sum "$candidate" "$export_dir/velstand-candidate.onnx"
```

导出器会合入观测归一化，并写入 `task_id`、`checkpoint_sha256`、`export_commit`、`export_dirty` 等元数据。
`export_dirty=true` 可能来自前面的教师固定修改；应保留并解释，不能为了让它变成 false 丢掉实验差异。
导出源码版本不等于原始训练源码版本，仍要同时保留 `bundle.json` 和新 run 的来源记录。
导出后需单独做 ONNX 回放；进入 Isaac 还要验证观测、动作缩放、执行器与动作衔接。

## 6. 出问题时，先查哪一层？ {#troubleshooting}

| 现象 | 先检查 |
| --- | --- |
| 不认识 `--init-checkpoint` | 是否还在旧的 `3750776`/v8 实验目录；检查当前 HEAD 和锁定依赖，不升级整套系统 |
| Hub 下载失败后要求 W&B 登录 | 教师的两项 W&B 路径是否已设为 `None`；先修下载，不换成随机教师 |
| `.pt` 形状或归一化不匹配 | 任务 ID、学生/教师身份、配置和输入哈希，不以重命名文件解决 |
| 续训从课程第零步开始 | 是否残留 `MICRODUCK_WARM_START=1`；普通 resume 与新任务 warm start 是两回事 |
| 显存不足 | 先降低环境数、停本轮自己的试验；不停止其他项目的正常任务 |
| 奖励上涨，动作却退步 | 回到同条件行为评估，保留基线，不凭训练曲线替换默认 |

## 7. 留好记录，再考虑分享 {#provenance}

每轮留下“参数 → 依据 → 改动 → 对照 → 决定”：源码 SHA 和差异、依赖锁、三个输入哈希、
任务与种子、完整启动参数、环境/奖励配置、输出检查点哈希、独立评估和原速录像。
过程在 `work/training-checkpoints/`，候选与证据在 `artifacts/training-checkpoints/`，
整理好的教程配套交付进入 `output/`；不要覆盖旧结果。

上游新增了 `share-training` / `publish --share-training`，但本页不自动调用。
训练包可能携带完整命令、用户名、源码未提交差异、W&B 配置和私有路径；分享前逐项清理凭据和无关内容。
工具创建的包默认私有，也不代表可以跳过审核。官方训练库在本次核对的模型卡中未声明许可证，
本项目不重新托管或重新授予权重许可；分发前核实对应许可，代码/网格仍按[项目许可说明](../project/licensing)区分。

实现依据：[训练包说明](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/docs/training_checkpoints.md)、
[检查点入口](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/src/mjlab_microduck/checkpoints.py)、
[固定学生来源记录](https://huggingface.co/pollen-robotics/microduck-training/blob/64d28ce092253c509b51031ec7ccb53790a00d0d/bundles/velstand/0045i2si_2749/bundle.json)。

<div class="md-page-complete">
  <strong>这一页的收获：拿到的不只是动作，还有继续训练的起点。</strong>
  <p>先核对存档和老师，再小步续训；用同条件结果决定是否采用，让下一位读者也能追上你的实验。</p>
</div>
