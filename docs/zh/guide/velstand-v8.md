# 训练鸭子起身和转向

这一章介绍怎样通过教师模型、初始姿态和奖励设置，改善鸭子的起身和转向动作。
我们以官方 VelStand 模型为例，说明如何调整参数，以及怎样检查效果。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>学习内容</span><strong>起身与转向</strong></div>
  <div role="listitem"><span>仿真平台</span><strong>MuJoCo</strong></div>
  <div role="listitem"><span>所用模型</span><strong>VelStand</strong></div>
  <div role="listitem"><span>动手操作</span><strong>第 17 章继续训练</strong></div>
</div>

想直接动手，可以接着看[第 17 章：用现成模型继续训练](./training-checkpoints)。
本章使用 MuJoCo/mjlab；Isaac Lab 的操作仍按[第 10 章](../isaac/training)进行。

## 1. 训练效果 {#results}

VelStand 用一个策略完成行走、零速度站立和跌倒恢复。后续训练主要改善了两个问题：
某些仰躺姿态起不来，以及转向指令给了、身体却没怎么转。

| 上游对照项 | 改进前 | 改进后 |
| --- | --- | --- |
| 仰躺、随机关节姿态起身成功率 | 73% | 94% |
| 侧躺、随机关节姿态起身成功率 | 91% | 96% |
| 坐姿起身成功率 | 89% | 99% |
| 原地转向指令 +0.6 rad/s，实际角速度 | +0.08 rad/s | +0.52 rad/s |
| 原地转向指令 −0.6 rad/s，实际角速度 | −0.03 rad/s | −0.57 rad/s |

数据来自[上游训练记录](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/docs/velstand_policy.md)：
仿真评估使用平地与齿隙模型；起身测试每类为两组、每组 128 个环境、观察 12 秒；
转向数值取前 2 秒之后仍直立环境的均值，不是把摔倒样本也计入的总体成功率。
上游另记录了实机测试；表中为其仿真评估结果，本项目尚未复测。

仍待改善的动作包括约 0.3 rad/s 的慢速原地转向和身体高度控制。
普通前向速度跟踪没有同等幅度的提升。

## 2. 起身和转向的训练方法 {#method}

### 起身：调整教师输入和初始姿态

学生从已有行走模型继续训练，PPO 根据奖励调整动作；
同时用行为克隆（BC）向两个冻结的教师学习：直立时保住走路，倒下时学习起身。
基础路由以身体倾角区分，行走教师主要管小于 25° 的状态，起身教师主要管大于 35° 的状态，
中间的倾角范围主要由 PPO 优化；站立时的身体控制另有教师选择规则。

起身教师遇到某些腿部姿态时会停住，学生也会模仿这一行为。
处理方式是：**在身体倾角较大时，修改起身教师看到的输入**。

| 改动 | 上游设置 | 为什么这样改 |
| --- | --- | --- |
| 起身教师的遮蔽阈值 | 倾角大于 75° | 倒得很彻底时绕开卡住的关节组合；起身后半程恢复完整输入 |
| 遮蔽范围 | 观测 `[6:48]` 置零 | 包含关节相对位置、速度、上一次动作；保留重力方向等输入 |
| 随机关节初始化 | 倒地初始化分支内 50% | 不只练标准 HOME 腿姿 |
| 随机空间朝向 | 倒地初始化分支内 25% | 覆盖更多落地朝向；这一类也随机化关节 |
| 坐姿初始化 | 全部重置的独立 5% 分支 | 补上坐着到站起来的过程 |

这些概率不是同一个分母，不能直接相加。零相对关节位置表示 HOME 参考姿态，
不表示把仿真里的关节瞬间摆回 HOME；学生和物理状态都没有被遮蔽或重置。
35° 是起身教师参与教学的门槛，75° 是遮蔽教师输入的门槛，也不能混为一谈。
实现见[教师输入与 BC](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/tasks/distill.py)
和[VelStand 配置](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/tasks/microduck_velstand_env_cfg.py)。

### 转向：校准教师动作，调整奖励

行走教师本身存在转向死区，直接模仿会把它也继承下来。
训练中先根据教师的响应表换算转向指令，让教师做出接近目标的动作，再把动作教给学生。
**学生始终接收真实的目标指令**，这项调整发生在训练时的教师动作生成过程中。

| 改动 | 上游设置 | 调参依据 |
| --- | --- | --- |
| 教师转向映射 | 按平面速度、目标角速度、左右方向查表插值 | 左右响应不完全对称，固定倍率不够 |
| 精细转向奖励 | `track_yaw_fine`：std 0.35，权重 2 | 比原来约 0.71 的宽容区间更关注小误差；std 是奖励核宽度，不是传感器噪声 |
| 原地转向样本 | 速度指令重采样时占 20% | 保证训练真的见到原地转向 |
| 最小转向幅度 | 0.2 rad/s | 覆盖低速区，但不代表低速区已经全部达标 |

映射表在 `ANCHOR_YAW_REMAP` 中，不能换一位教师还照用旧表。
本例使用 `ENABLE_ANCHOR_YAW_REMAP=True`。
`ENABLE_YAW_FIX` 来自一次效果不佳的实验，保持 `False`。
使用改进后的模型时，关闭旧运行时的转向补偿，避免重复修正。参数与开关均见上述固定版本配置。

## 3. 下载模型并试运行 {#try-v8}

::: details 源码和模型校验信息
本页采用以下固定来源，避免以后 `main` 或标签移动，让同一条命令拿到不同文件：

| 用途 | 固定版本 |
| --- | --- |
| 本章对应源码 | `b02fdea4902c2b93b7d34a83a6f05da4ececb7d3` |
| 本章使用的策略集 | `665ae4eb20bfe13bca1ef4ea6d4bb6b4a096e448` |
| `velstand.onnx` SHA-256 | `2fc7f8ee6acd7d0d3f66a99927b5d5a56589aeed02ec714de329b252d5ccf492` |

官方清单仍声明 61 维观测、14 维动作、50 Hz 控制。本次策略集只有 `velstand.onnx`
与教程默认权重不同，其余九个 ONNX 的哈希一致；模型 XML/STL 也没有在这次 RL 差异中改变。
来源：[固定版策略清单](https://huggingface.co/pollen-robotics/microduck-policies/blob/665ae4eb20bfe13bca1ef4ea6d4bb6b4a096e448/manifest.json)
与[源码差异](https://github.com/pollen-robotics/microduck_rl/compare/ceca01706143d729305baa94cbd8ab990979e325...b02fdea4902c2b93b7d34a83a6f05da4ececb7d3)。
:::

<div class="md-step-kicker"><span>选做 A</span><strong>终端 A · 本项目仓库根目录</strong></div>

先按[原有环境准备](./installation)取得默认输入，再准备本地 MuJoCo 环境：

```bash
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
```

下面下载用于起身和转向的模型到独立目录，复用项目现有的校验下载器。
已有文件不一致时会报错，不会覆盖；相同文件重复执行只校验。

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

接着用相同条件分别检查默认模型与改进后的模型。报告放进新的时间戳目录，不覆盖原记录：

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

这是现有简化接地模型中的短时兼容性检查，查看能否加载、数值是否有限、姿态是否正常；
完整的起身和转向测试需使用后文的训练环境。本节运行命令已按源码核对，尚待 GPU 复测。

## 4. 两阶段训练参数 {#training}

训练分为两步：先改善起身，再调整转向。想亲手继续训练，直接按[第 17 章](./training-checkpoints)下载已公开的模型和两个教师。

下方保留上游原始实验的命令，供核对参数和研究训练过程时查阅。

:::: details 原始两阶段实验：参数与命令
### 准备训练模型

正式训练需要 Linux/CUDA GPU、Python 3.12、`uv`，并使用上游锁定依赖。
任务是 `Mjlab-VelStand-Rough-Backlash-MicroDuck`：包含全碰撞模型、粗糙地形、
BAM XL330 执行器与齿隙。

除了续训输入，BC 还会加载两个教师。开始前确认有权限获取以下原始 `.pt`：

| 材料 | 上游 W&B run | 文件 |
| --- | --- | --- |
| 初始行走模型 | `pollen-robotics/mjlab_microduck/j4i6yoq2` | `model_1250.pt` |
| 起身教师 | `pollen-robotics/mjlab_microduck/69u48n8l` | `model_9750.pt` |
| 行走教师 | `pollen-robotics/mjlab_microduck/441tzs6d` | `model_3750.pt` |
| 上游阶段 A 的选模结果 | `pollen-robotics/mjlab_microduck/qz5g3bwi` | `model_1750.pt` |

::: tip 现在可以从最终模型继续训练
最终 VelStand 模型和两个教师已经公开，具体操作见[第 17 章](./training-checkpoints)。
本节保留原始两阶段实验的参数和命令；其中 `j4i6yoq2_1250`、`qz5g3bwi_1750` 仍需取得访问权限。
两章使用不同源码版本，请分别使用各自页面中的完整命令。
:::

这套历史实验需要表中的原始 `.pt` 文件；其中部分文件尚未确认可公开下载。
ONNX 用于推理，继续训练需要保存了训练状态的 `.pt` 模型。
只加载可信来源的 `.pt`，同时保存来源与 SHA-256。

### 建独立实验目录

<div class="md-step-kicker"><span>选做 B</span><strong>有 CUDA 的 Linux 主机 · 本项目仓库根目录</strong></div>

不切换 `reference/microduck_rl/` 的默认 checkout。下面只为这条实验路线准备独立源码；
如果目录已经存在，先检查它的版本和本地修改，不重复克隆或强制检出。

```bash
git clone --filter=blob:none --no-checkout \
  https://github.com/pollen-robotics/microduck_rl.git reference/microduck_rl-v8
cd reference/microduck_rl-v8
git checkout --detach b02fdea4902c2b93b7d34a83a6f05da4ececb7d3
mkdir -p ../../work/velstand-v8/logs
ln -s ../../work/velstand-v8/logs logs
uv sync --frozen
```

训练日志通过 `logs` 链接归入本项目 `work/velstand-v8/logs/`。
先看上游 CLI 帮助，再确认登录的是自己的 W&B 账号；首次下载可能需要该账号对源 run 的访问权限。
不要向官方项目写入自己的实验记录。

```bash
uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck --help
uv run wandb login
```

### 阶段 A：训练起身

上游这个阶段使用 `333ef7b`，只有关节遮蔽与更广的初始姿态，还没有阶段 B 的转向映射。
使用对应提交，便于单独观察这些起身设置带来的变化。

```bash
git checkout --detach 333ef7b03c0463bdebfcd6e2be0592de76c2bbcc
uv sync --frozen
env -u MICRODUCK_WARM_START uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --env.scene.num-envs 4096 --agent.resume True \
  --wandb-run-path pollen-robotics/mjlab_microduck/j4i6yoq2 \
  --wandb-checkpoint-name model_1250.pt \
  --agent.max_iterations 1500
```

这是上游的参考预算，不是显卡最低要求或耗时承诺。第一次应先降低环境数和迭代预算检查加载、
BC 教师与保存流程；小规模检查通过不等于复现了上表成绩。
上游这次 run 最后到 2749，但选用的是 **1750**：最新文件不一定最好。

### 阶段 B：训练转向

前一训练进程退出后才能切换源码。此阶段对应 `3750776`，增加教师转向映射与精细转向奖励：

下面的示例读取上游的阶段 A 检查点。**要接自己的阶段 A，先替换命令中的 run 与 checkpoint，**
不要直接把示例当成自己上一轮的续训。

```bash
git checkout --detach 3750776761ecfaa5671b36972087cafba45b8527
uv sync --frozen
env -u MICRODUCK_WARM_START uv run train Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --env.scene.num-envs 4096 --agent.resume True \
  --wandb-run-path pollen-robotics/mjlab_microduck/qz5g3bwi \
  --wandb-checkpoint-name model_1750.pt \
  --agent.max_iterations 1000
```

这两段命令使用的是上游实验文件。接着训练自己的阶段 A 模型时，
把第二段的 run 和 checkpoint 换成自己选出的文件，并为新模型单独命名。

两个阶段都是普通 resume：保留步数与课程进度，继续微调。
因此命令显式移除 `MICRODUCK_WARM_START`，避免继承终端里旧的 `=1` 设置而把课程清零。
不要把这个环境变量和源码中保留的 `WARM_START=True` 配置常量混淆。
计数行为见[上游加载补丁](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/tasks/mdp.py)。

::::

## 5. 检查动作并导出模型 {#evaluation}

建议分开记录起身、转向和行走：先用开发集选检查点，再用独立进程与新种子评估。
按下表设置测试项目；自动统计需要另行准备评估脚本。

| 检查 | 保持一致的条件 | 应保存的结果 |
| --- | --- | --- |
| 起身 | 两个模型使用相同姿态族、关节随机化、模型和时长 | 成功/总数、卡住率、起身耗时、再次摔倒 |
| 转向 | 正负指令分别测，区分原地与行走 | 实际角速度、误差、摔倒数；不要只报存活样本 |
| 直行 | 相同速度指令、摩擦与执行器参数 | 实际速度、左右漂移、摔倒数 |
| 平顺性 | 相同采样率与统计区间 | 身体角速度、冲击、恢复后的连续原速视频 |

起身完成的高度/倾角阈值、持续站稳时间、超时与分母必须先固定，再比较模型。
两个版本使用同一判定标准；同样的比较方法也用于[连续翻滚验收](../isaac/roll-validation)。

::: info 自动评估脚本尚未公开
上游记录提到的 `claude_experiments/velstand_rise_battery.py`、`velstand_yaw_probe.py`
等脚本不在所选源码中。复现官方统计需要取得这些脚本，或自行实现并说明相同的评估条件。
:::

导出自己的已选检查点时，使用[上游导出器](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/export.py)，
让观测归一化一起进入 ONNX。下面的绝对路径必须换成自己的真实文件；仍在 `reference/microduck_rl-v8/` 执行：

```bash
export_dir="$PWD/../../artifacts/velstand-v8/export-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$export_dir"
uv run scripts/export.py Mjlab-VelStand-Rough-Backlash-MicroDuck \
  --checkpoint-file /absolute/path/to/model_selected.pt \
  --onnx-file "$export_dir/velstand.onnx"
sha256sum "$export_dir/velstand.onnx"
```

每轮保留源码 SHA、`uv.lock`、输入/教师/输出检查点哈希、环境与奖励配置、种子、原始日志、
独立评估报告及原速录像，方便其他读者复现实验和调参过程。
过程放 `work/velstand-v8/`，测试证据和导出候选放 `artifacts/velstand-v8/`；
整理完成的教程配套包再进入 `output/`，不要覆盖历史案例。

## 6. 在 Isaac 中使用前的检查 {#adoption}

先完成 MuJoCo 的同条件对照，再单独检查 Isaac 的观测顺序、动作缩放、执行器差异、
行走/起身和其他动作切换。控制维度相同，不代表两个引擎下的行为已经一致。

本章介绍的起身与转向模型先在 MuJoCo 中测试。Isaac 游乐场继续使用已配套的模型与控制参数；来源见[模型与源码版本](../reference/upstream-alignment)。

<div class="md-page-complete">
  <strong>下一步：加载模型，开始训练</strong>
  <p>第 17 章按环境准备、模型下载、训练、检查结果和导出的顺序，带你完成一次小规模续训。</p>
</div>
