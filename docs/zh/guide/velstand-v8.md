# VelStand v8：摔倒会起，转弯听话

这一回先不加新杂技，把两件基本功练好：摔倒后别躺平，想拐弯时别原地发呆。
上游在 2026-10-12 发布了 VelStand v8，本页先看它改进了什么，再拆解训练方法，最后说明怎样做自己的对照实验。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>阅读路线</span><strong>效果 → 原因 → 训练 → 验收</strong></div>
  <div role="listitem"><span>训练环境</span><strong>MuJoCo / mjlab + CUDA</strong></div>
  <div role="listitem"><span>本项目默认</span><strong>保留原版本，不自动切换</strong></div>
  <div role="listitem"><span>证据状态</span><strong>上游报告，本项目待复测</strong></div>
</div>

::: info 这是选读，不是新的默认安装步骤
现有 `upstream.lock`、v7 下载入口、Isaac 游乐场、历史 USD 和连续翻滚案例都不变。
本页讲的是上游 MuJoCo/mjlab 的 VelStand，不是把[原生 Isaac Lab 行走任务](../isaac/training)改成 v8。
只想跟着原教程玩鸭，继续原来的步骤即可。
:::

## 1. 先看结果：改善在哪里？ {#results}

VelStand 用一个策略完成行走、零速度站立和跌倒恢复。v8 主要补上了 v7 的两个短板：
某些仰躺姿态起不来，以及转向指令给了、身体却没怎么转。

| 上游对照项 | v7 | v8 |
| --- | --- | --- |
| 仰躺、随机关节姿态起身成功率 | 73% | 94% |
| 侧躺、随机关节姿态起身成功率 | 91% | 96% |
| 坐姿起身成功率 | 89% | 99% |
| 原地转向指令 +0.6 rad/s，实际角速度 | +0.08 rad/s | +0.52 rad/s |
| 原地转向指令 −0.6 rad/s，实际角速度 | −0.03 rad/s | −0.57 rad/s |

数据来自[上游 v8 训练记录](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/docs/velstand_policy.md)：
仿真评估使用平地与齿隙模型；起身测试每类为两组、每组 128 个环境、观察 12 秒；
转向数值取前 2 秒之后仍直立环境的均值，不是把摔倒样本也计入的总体成功率。
上游另记录了实机起身、转向和行走测试。**这些不是本项目复测成绩。**

改善也有边界：约 0.3 rad/s 的慢速原地转向仍偏弱，身体高度控制仍未学会；
普通前向速度跟踪没有同等幅度的提升。不要把“更会起身和转弯”读成“所有动作都升级了”。

## 2. 为什么多练几轮不一定有用？ {#method}

### 起身：先检查老师有没有教错

这条训练路线不是从随机动作开始。学生继承已有行走能力，PPO 用奖励继续优化；
同时用行为克隆（BC）向两个冻结的老师学习：直立时保住走路，倒下时学习起身。
基础路由以身体倾角区分，行走老师主要管小于 25° 的状态，起身老师主要管大于 35° 的状态，
中间留给 PPO；站立身体控制还有单独的路由。

问题是，起身老师遇到某些腿部姿态也会卡住，学生连“躺着不动”一起学走了。
v8 的处理不是让学生看不见关节，而是**只在大倾角时，修改起身老师看到的输入**：

| 改动 | 上游设置 | 为什么这样改 |
| --- | --- | --- |
| 起身老师的遮蔽阈值 | 倾角大于 75° | 倒得很彻底时绕开卡住的关节组合；起身后半程恢复完整输入 |
| 遮蔽范围 | 观测 `[6:48]` 置零 | 包含关节相对位置、速度、上一次动作；保留重力方向等输入 |
| 随机关节初始化 | 倒地初始化分支内 50% | 不只练标准 HOME 腿姿 |
| 随机空间朝向 | 倒地初始化分支内 25% | 覆盖更多落地朝向；这一类也随机化关节 |
| 坐姿初始化 | 全部重置的独立 5% 分支 | 补上坐着到站起来的过程 |

这些概率不是同一个分母，不能直接相加。零相对关节位置表示 HOME 参考姿态，
不表示把仿真里的关节瞬间摆回 HOME；学生和物理状态都没有被遮蔽或重置。
35° 是起身老师参与教学的门槛，75° 是遮蔽老师输入的门槛，也不能混为一谈。
实现见[教师输入与 BC](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/tasks/distill.py)
和[VelStand 配置](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/tasks/microduck_velstand_env_cfg.py)。

### 转向：标定老师，再让奖励对准目标

行走老师本身存在转向死区，直接模仿会把它也继承下来。
v8 在训练中先根据老师的响应表换算转向指令，让老师做出接近目标的动作，再把动作教给学生。
**学生仍接收真实目标指令**，不是在部署时把用户输入偷偷放大。

| 改动 | 上游设置 | 调参依据 |
| --- | --- | --- |
| 教师转向映射 | 按平面速度、目标角速度、左右方向查表插值 | 左右响应不完全对称，固定倍率不够 |
| 精细转向奖励 | `track_yaw_fine`：std 0.35，权重 2 | 比原来约 0.71 的宽容区间更关注小误差；std 是奖励核宽度，不是传感器噪声 |
| 原地转向样本 | 速度指令重采样时占 20% | 保证训练真的见到原地转向 |
| 最小转向幅度 | 0.2 rad/s | 覆盖低速区，但不代表低速区已经全部达标 |

映射表在 `ANCHOR_YAW_REMAP` 中，不能换一位老师还照用旧表。
`ENABLE_YAW_FIX` 是上游保留的失败实验开关，当前为 `False`；
有效路线是 `ENABLE_ANCHOR_YAW_REMAP=True`，不要看到名字里有 “fix” 就把两个都打开。
v7 的旧运行时转向补偿公式也不能叠加给 v8。参数与开关均见上述固定版本配置。

## 3. 先试权重，不动默认路线 {#try-v8}

本页采用以下固定来源，避免以后 `main` 或标签移动，让同一条命令拿到不同文件：

| 用途 | 固定版本 |
| --- | --- |
| v8 合并后的源码说明 | `b02fdea4902c2b93b7d34a83a6f05da4ececb7d3` |
| v8 官方策略集 | `665ae4eb20bfe13bca1ef4ea6d4bb6b4a096e448` |
| `velstand.onnx` SHA-256 | `2fc7f8ee6acd7d0d3f66a99927b5d5a56589aeed02ec714de329b252d5ccf492` |

官方清单仍声明 61 维观测、14 维动作、50 Hz 控制。本次策略集只有 `velstand.onnx`
与我们锁定的 v7 权重不同，其余九个 ONNX 的哈希一致；模型 XML/STL 也没有在这次 RL 差异中改变。
来源：[固定版策略清单](https://huggingface.co/pollen-robotics/microduck-policies/blob/665ae4eb20bfe13bca1ef4ea6d4bb6b4a096e448/manifest.json)
与[源码差异](https://github.com/pollen-robotics/microduck_rl/compare/ceca01706143d729305baa94cbd8ab990979e325...b02fdea4902c2b93b7d34a83a6f05da4ececb7d3)。

<div class="md-step-kicker"><span>选做 A</span><strong>终端 A · 本项目仓库根目录</strong></div>

先按[原有环境准备](./installation)取得默认输入，再准备本地 MuJoCo 环境：

```bash
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
```

下面只下载 v8 的一个文件到独立目录，复用项目现有的校验下载器。
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

接着用相同条件分别检查 v7 和 v8。报告放进新的时间戳目录，不覆盖原记录：

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
不是 Rough + Backlash 起身或转向评估，也没有替换 Isaac 游乐场的控制器。
本页新增命令尚未完成本项目的 v8 运行时复测。

## 4. 训练方法：分两阶段继续训练 {#training}

### 先备齐检查点，不要拿 ONNX 充当训练存档

正式训练需要 Linux/CUDA GPU、Python 3.12、`uv`，并使用上游锁定依赖。
任务是 `Mjlab-VelStand-Rough-Backlash-MicroDuck`：包含全碰撞模型、粗糙地形、
BAM XL330 执行器与齿隙，不是前面的简化接地探测环境。

除了续训输入，BC 还会加载两个老师。开始前确认有权限获取以下原始 `.pt`：

| 材料 | 上游 W&B run | 文件 |
| --- | --- | --- |
| v7 续训起点 | `pollen-robotics/mjlab_microduck/j4i6yoq2` | `model_1250.pt` |
| 起身老师 | `pollen-robotics/mjlab_microduck/69u48n8l` | `model_9750.pt` |
| 行走老师 | `pollen-robotics/mjlab_microduck/441tzs6d` | `model_3750.pt` |
| 上游阶段 A 的选模结果 | `pollen-robotics/mjlab_microduck/qz5g3bwi` | `model_1750.pt` |

本项目未验证这些 W&B 文件的公开下载权限。访问不到就先停在权重体验与方法学习，
不要把 ONNX 改名成 `.pt`；ONNX 没有完整的训练状态，也不能代替两个老师的检查点。
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

### 阶段 A：把卡住的起身教顺

上游这个阶段使用 `333ef7b`，只有关节遮蔽与更广的初始姿态，还没有阶段 B 的转向映射。
不要直接用最新配置冒充同一组起身消融。

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
BC 老师与保存流程；小规模检查通过不等于复现了上表成绩。
上游这次 run 最后到 2749，但选用的是 **1750**：最新文件不一定最好。

### 阶段 B：保住起身，再校准转向

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

这两段命令展示的是**上游原始谱系**：第二段显式读取上游的阶段 A 产物，
不会自动接上你刚训练的结果。串联自己的实验时，要把第二段的 run 和 checkpoint 换成
自己经过独立评估选出的阶段 A 产物，并记录新来源；不能继续标成官方 v8。

两个阶段都是普通 resume：保留步数与课程进度，继续微调。
因此命令显式移除 `MICRODUCK_WARM_START`，避免继承终端里旧的 `=1` 设置而把课程清零。
不要把这个环境变量和源码中保留的 `WARM_START=True` 配置常量混淆。
计数行为见[上游加载补丁](https://github.com/pollen-robotics/microduck_rl/blob/b02fdea4902c2b93b7d34a83a6f05da4ececb7d3/src/mjlab_microduck/tasks/mdp.py)。

## 5. 怎么选模，才不只是奖励更好看？ {#evaluation}

建议分开记录起身、转向和行走：先用开发集选检查点，再用独立进程与新种子评估。
下面是本项目建议的复测清单，不是已经提供的一键评估器，也不是已完成测试。

| 检查 | 保持一致的条件 | 应保存的结果 |
| --- | --- | --- |
| 起身 | v7/v8 使用相同姿态族、关节随机化、模型和时长 | 成功/总数、卡住率、起身耗时、再次摔倒 |
| 转向 | 正负指令分别测，区分原地与行走 | 实际角速度、误差、摔倒数；不要只报存活样本 |
| 直行 | 相同速度指令、摩擦与执行器参数 | 实际速度、左右漂移、摔倒数 |
| 平顺性 | 相同采样率与统计区间 | 身体角速度、冲击、恢复后的连续原速视频 |

起身完成的高度/倾角阈值、持续站稳时间、超时与分母必须先固定，再比较模型。
不要让 v7 用严标准、v8 用宽标准；同样的原则也用于[连续翻滚验收](../isaac/roll-validation)。

::: warning 上游评估脚本有公开缺口
上游记录提到的 `claude_experiments/velstand_rise_battery.py`、`velstand_yaw_probe.py`
等脚本不在这个固定版本的公开 Git 树中。不能照抄路径就声称读者可以复现官方统计。
严格复现需要取得对应评估脚本和定义，或自行实现并公开一套标明差异的评估器。
训练命令有来源，不代表检查点权限、评估工具和实机环境都已齐备。
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
独立评估报告及原速录像。只有 ONNX 和一段好看的视频，下一位读者很难复现你的决定。
过程放 `work/velstand-v8/`，测试证据和导出候选放 `artifacts/velstand-v8/`；
整理完成的教程配套包再进入 `output/`，不要覆盖历史案例。

## 6. 什么时候才替换默认版本？ {#adoption}

先完成 MuJoCo 的同条件对照，再单独检查 Isaac 的观测顺序、动作缩放、执行器差异、
行走/起身和其他动作切换。控制维度相同，不代表两个引擎下的行为已经一致。

本项目当前只补充 v8 方法说明：默认下载仍取 v7，游乐场仍用历史行走/站立与坐起组合；
没有启动训练、更新 USD 或宣布 v8 已通过本地验收。
具体保留版本见[上游对齐说明](../reference/upstream-alignment)。

<div class="md-page-complete">
  <strong>这一页的收获：不只换个权重，还知道为什么要换。</strong>
  <p>先确认老师、数据和奖励各自的问题，再小步训练、独立验收。等新策略在自己的环境里确实更好，再让它接班。</p>
</div>
