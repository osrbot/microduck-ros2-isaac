---
title: 训练一只会连续翻滚的鸭
description: 从策略热启动、第一次短训练，到奖励设计、三轮调参和连续前滚翻验收。
prev:
  text: 训练一只会走的鸭
  link: /zh/isaac/training
next:
  text: 参数和奖励怎么设计
  link: /zh/isaac/roll-parameters
---

<script setup>
import RollShowcase from '../../.vitepress/theme/RollShowcase.vue'
</script>

# 训练一只会连续翻滚的鸭

先看我们要练到什么样，再一步步把它做出来。

<RollShowcase />

这套教程带你完成：**准备环境 → 从已有策略起步 → 短训练 → 看回放找问题 → 调奖励 → 选择模型**。
你会用到的命令、参数来历和中间实验，都放在同一条学习路线里。

本例以 Pollen Robotics 的 `roulade.onnx` 初始化 Actor 和观测归一化，再用 PPO 优化连续翻滚。
已记录的批量回放中，8 个轻微不同的初始姿态各运行 50 秒，均连续完成 39 圈、零重置；平均绝对横向偏移约 0.70 m。
这是平地仿真案例，后续仍可继续改善方向和扰动恢复能力。

## 从哪一页开始？

| 你现在想做什么 | 去哪里 |
| --- | --- |
| 先亲手跑通训练和回放 | 继续读本页 |
| 理解参数为什么这样设 | [参数和奖励](./roll-parameters) |
| 学会“没练成时怎么查” | [三轮调试复盘](./roll-debugging) |
| 比较检查点、批量验收、录视频 | [回放验收与素材导出](./roll-validation) |

## 1. 先把环境准备好 {#setup}

需要一台能运行 Isaac Sim / Isaac Lab 的 Linux + NVIDIA GPU 电脑。Mac 可以阅读教程、查看视频，训练命令在 Linux 仿真环境中执行。
没有装好环境时，先走[环境准备](../guide/installation)，再做一次[行走任务的短训练](./training)。
本案例不依赖 ROS 2 节点；ROS 2 接入可以放到策略稳定之后。

本次记录的组合：Ubuntu 24.04、RTX 4080 SUPER 16 GB、Isaac Sim 6.0.1、Isaac Lab 3.0.0 beta 2、RSL-RL 5.0.1。
完整的版本和驱动信息见[测试环境](../reference/environment)。其他组合先做下面的小测试。

::: info 确认代码与教程配套
本专题使用配套的 `--full-roll-v2` 和 `--straight-roll` 实现。旧版本可能尚无这些选项。
开始操作前确认下面的文件存在，命令帮助中也包含所需选项。
:::

### 终端 A：项目根目录

已有项目直接进入原目录。首次获取项目可参考[安装页](../guide/installation)。将第一行替换成自己的 Isaac Lab 路径：

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
nvidia-smi
test -x "$ISAACLAB_DIR/isaaclab.sh"
test -f source/microduck_isaac_lab/microduck_isaac_lab/tasks/velocity/full_roll_env_cfg.py
"$ISAACLAB_DIR/isaaclab.sh" -p scripts/train_isaac_velocity.py --help
```

应看到 GPU 信息，帮助中包含 `--full-roll-v2`、`--straight-roll`、`--resume-checkpoint`。
文件检查无输出时看退出码；失败就先修正路径或取得配套版本，不要直接跳到长训练。

获取锁定的上游策略，并让 Isaac Python 能找到项目内的 ONNX Runtime：

```bash
bash scripts/fetch_upstream.sh
bash scripts/setup_isaac_python_env.sh
export PYTHONPATH="$PWD/work/isaac_python_pkgs${PYTHONPATH:+:$PYTHONPATH}"
test -s reference/microduck/policies/roulade.onnx
"$ISAACLAB_DIR/isaaclab.sh" -p -c \
  'import onnx, onnxruntime, torch; import importlib.metadata as m; print("torch", torch.__version__, "rsl-rl", m.version("rsl-rl-lib"), "onnx", onnx.__version__, "ort", onnxruntime.__version__)'
```

`onnx` 用于读取并拷贝网络权重；`onnxruntime` 用于直接回放原始 ONNX。它们是两个包。
`setup_isaac_python_env.sh` 只补项目内的 ONNX Runtime；若仍缺 `onnx` 或 RSL-RL，先在当前 Isaac Lab 的 Python 环境补齐对应依赖，再重跑检查。
不要把系统 Python 的导入成功当作 Isaac Python 的检查结果。

`fetch_upstream.sh` 按 `upstream.lock` 获取固定提交；已有参考仓库有未保存修改时会退出，请先保留自己的修改。
机器人模型与策略来源见[许可说明](../project/licensing)。

## 2. 给这次实验建立独立目录和时间上限

下面在同一个终端里执行，后面会继续使用这些变量：

```bash
roll_session="work/isaac_training/roll-tutorial-$(date +%Y%m%d-%H%M%S)"
roll_evidence="artifacts/isaac/$(basename "$roll_session")"
mkdir -p "$roll_session" "$roll_evidence"
roll_deadline=$(date -u -d '+120 minutes' +%Y-%m-%dT%H:%M:%S+00:00)
printf '本次目录：%s\n总截止时间：%s\n' "$roll_session" "$roll_deadline"
```

`date -d` 是这里的 Ubuntu / GNU date 写法。总截止时间只设置一次，重试时沿用，不重新加 120 分钟。
训练、回放都可以交给 `run_before_deadline.py`：它同时限制本阶段耗时和整次实验截止时间，并预留退出时间。
120 分钟是预算上限，效果达到要求即可收尾；不要为了凑满时间继续训练。

## 3. 第一次只跑 5 轮

先用 64 个环境验证热启动、仿真、PPO 更新和文件输出。`--full-roll-v2` 选择完整翻转奖励和正确的重置高度。

```bash
MICRODUCK_TRAIN_ENVS=64 MICRODUCK_TRAIN_ITERATIONS=5 \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 600 \
  --status "$roll_evidence/smoke-status.json" -- \
  bash scripts/train_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --viz none \
    --init-policy-onnx reference/microduck/policies/roulade.onnx \
    --log-root "$roll_session/smoke"
```

启动时会打印 `MICRODUCK_RUN_DIR=...`，把这个目录记下来。随后应出现：

```text
MICRODUCK_TRAIN_STAGE=creating_environment
MICRODUCK_TRAIN_STAGE=creating_runner
MICRODUCK_TRAIN_STAGE=loading_roll_actor
MICRODUCK_ROLL_WARM_START_SHA256=...
MICRODUCK_TRAIN_STAGE=learning
MICRODUCK_TRAIN_STAGE=saving
MICRODUCK_TRAIN_STAGE=complete
```

运行目录里应有 `model_final.pt`、`training_summary.json`、`params/env.yaml` 和 `params/agent.yaml`。
本例原始策略的 SHA-256 为 `3d60da08fc13f29c1b57f41977aa898132c0d60042100149d8e775affcbca32b`。
摘要中的 `warm_start.sha256` 可以用来核对自己是否从相同权重起步。

首次加载可能较慢，先看 stage 是否推进，别重复启动进程。显存不足先把环境数降到 16。
5 轮只检查训练流程；动作是否已经连续，要由下一步回放判断。

## 4. 回放刚保存的模型

用终端打印的真实目录替换示例路径，显式指定检查点，避免误加载其他实验：

```bash
roll_checkpoint="$roll_session/smoke/替换为实际运行时间目录/model_final.pt"
test -s "$roll_checkpoint" && \
MICRODUCK_PLAY_STEPS=1500 MICRODUCK_PLAY_TIMEOUT=240 \
MICRODUCK_PLAY_OUTPUT="$roll_evidence/smoke-play.json" \
MICRODUCK_PLAY_SCREENSHOT="$roll_evidence/smoke-play.png" \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 260 \
  --status "$roll_evidence/smoke-play-status.json" -- \
  bash scripts/play_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --viz none \
    --arena-half-width 25 --checkpoint "$roll_checkpoint" \
    --video "$roll_evidence/smoke-play.mp4" \
    --trace "$roll_evidence/smoke-trace.json"
```

1500 个控制步是 30 秒仿真时间。脚本使用跟随相机录制，最后输出 `MICRODUCK_PLAYBACK_STAGE=complete`。
打开 MP4 看起步、完整翻转、连续性，再看 JSON 的 `completed_forward_turns`、`max_consecutive_forward_turns` 和 `done_count`。
如果没有完成整圈，先进入[调试复盘](./roll-debugging)，不要只增加训练轮数。

## 5. 流程通过后，再做短段训练

本次使用了 1024 个并行环境。显存较小可以逐档增加，但环境数变化也会改变每轮采样量，学习曲线不必与本例一致。
下面是**新的短段实验建议**：新开一个最多 300 次更新的训练段，15 分钟内结束。
它采用已经修正高度的配置，历史第一轮的错误初始化只在复盘页分析。

```bash
MICRODUCK_TRAIN_ENVS=1024 MICRODUCK_TRAIN_ITERATIONS=300 \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 900 \
  --status "$roll_evidence/roll-status.json" -- \
  bash scripts/train_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --viz none \
    --init-policy-onnx reference/microduck/policies/roulade.onnx \
    --log-root "$roll_session/roll"
```

这条命令重新从原始 Actor 开始；若要延续某次训练，必须显式传 `--resume-checkpoint`，具体见[第三轮续训示例](./roll-debugging#direction-training)。
每保存约 100 次更新就有一个检查点。等训练段结束后，逐个回放候选模型，再决定是否续训。
不要直接运行未设置轮数的旧版长训包装入口。

### 终端 B：边训练边看曲线

在同一项目目录启动 TensorBoard，把路径换成终端 A 打印的本次目录：

```bash
tensorboard --logdir work/isaac_training/替换为本次roll-tutorial目录
```

浏览器打开 TensorBoard 打印的本机地址。在 Scalars 里搜索 `Episode_Reward`、`Loss`、`Train` 等分组，实际标签随 RSL-RL 版本而异。
优先看完整翻转相关奖励、episode length、动作平滑惩罚和学习率；然后与同一个检查点的回放对照。
改变奖励定义后，总 reward 的绝对值不能直接横向排名。

如果连续翻滚已稳定但横向偏移大，就进入方向调优；如果还没完成整圈，先检查重置、动作接口和进度奖励。
本次修正过程在 120 分钟预算内提前收束，记录汇总时用时约 24 分钟；这是已有策略热启动条件下的本次实验耗时，其他机器和策略需要自行测量。

## 跑完这一页，你应该留下什么

- 一份参数快照和明确来源的检查点；
- 一段可打开的回放视频；
- 一份圈数、连续圈数、重置和偏移报告；
- 一句具体判断：还没翻完整、已经连续但偏航，或已达到本阶段目标。

下一页把这些现象与参数连起来：从控制频率和初始高度开始，再进入奖励与 PPO。
