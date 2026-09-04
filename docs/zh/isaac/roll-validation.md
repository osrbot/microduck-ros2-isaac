---
title: 连续翻滚：回放验收与素材导出
description: 显式选择检查点，复验完整圈数、连续间隔和横向位移，录制 1080p 演示并保存实验包。
prev:
  text: 三轮调试复盘
  link: /zh/isaac/roll-debugging
next:
  text: 自己做一个训练任务
  link: /zh/isaac/custom-environment
---

# 选择模型，验收，再录一段

最后一步把“训练保存了什么”和“回放表现怎么样”对应起来。
选模型时先看连续动作、重置和时间间隔，再比较横向偏移；把同一个检查点用于批量测试和视频录制。

## 先看本次最终结果

| 检查项 | 批量回放 | 单独录制的视频 |
| --- | --- | --- |
| 数量与时长 | 8 个环境，各 50 秒 | 1 个环境，50 秒 |
| 完整 / 连续前滚翻 | 每个均 39 / 39 圈 | 39 / 39 圈 |
| 重置 | 0 次 | 0 次 |
| 最长整圈间隔 | 最大 1.40 秒 | 1.42 秒 |
| 横向位移 | 平均绝对值 0.699 m，最大绝对值 1.426 m | 1.152 m |
| 初始状态 | seed 109，姿态各 ±0.03 rad，关节缩放 ±0.003 | 默认确定性站姿 |

起始根高度为 `0.125 m`。批量测试使用一个 seed 的 8 个不同初始状态，尚未覆盖多个独立 seed、复杂地面、外部推扰或实体机器人。
本次回放长度是 50 秒；更长时间的稳定性需要延长 PLAY episode 和测试时长后另行验证。

## 1. 明确选中哪一个检查点

本次交付选择第三轮 `model_600.pt`，复制后的名字是 `model_best.pt`。
第三轮末尾还保存了 `model_final.pt`；`training-final-summary.json` 描述该轮结束情况。
检查点 600 的批量报告和录制报告，才对应页面展示的模型。

所有命令从项目根目录运行。环境、`PYTHONPATH`、`roll_evidence` 和 `roll_deadline` 沿用[实战主线](./continuous-roll)。
在自己的训练目录中选一个经过短回放的候选，例如：

```bash
roll_checkpoint="$roll_session/direction/替换为实际运行时间目录/model_600.pt"
test -s "$roll_checkpoint" && sha256sum "$roll_checkpoint"
```

文件标签随续训起点和保存时机变化，以实际目录为准。下面每次都显式传 `--checkpoint`，避免自动选到别的 run。
只加载来源可信的 `.pt` 检查点。

::: info 已有素材包的使用方式
本地交付包位于 `output/continuous-roll-training/roll120-20260904-073725/`。
拿到该包时可以把 `roll_checkpoint` 指向其中的 `model_best.pt`。
网页已提供视频预览；模型文件不随教程公开分发。没有交付包的读者使用自己训练的检查点即可完成后续流程。
:::

## 2. 用 8 个轻微不同的起点复验

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

`--reset-perturbation 0.03` 给 roll / pitch / yaw 各 `±0.03 rad`，关节位置比例为 `1 ± 0.003`。
`2500 × 0.02 s = 50 s`。GPU 运行耗时可以大于或小于 50 秒，按报告里的实际步数判断是否完整执行。

回放将横向边界半宽设成 25 m，为持续动作留出空间；训练基线的横向边界为 1 m。
场地放宽会影响越界重置，所以圈数、重置与横向位移要一起报告。
横向位移依旧单独量化，不把“没有越界”直接解释为方向精度高。

## 3. 报告中哪些字段最重要？

| 字段 | 怎么读 |
| --- | --- |
| `completed_forward_turns` | 每个环境累计完成的完整前向翻转圈数 |
| `max_consecutive_forward_turns` | 每个环境历史上最长连续链，重置和明显反转会打断当前链 |
| `done_count` | 全部环境累计终止 / 重置次数；本阶段要求 0 |
| `turn_completion_times_s` | 每个环境完成各圈的仿真时刻 |
| `maximum_full_turn_gap_s_per_env` | 最长整圈间隔，包含起步和最后一圈到结束之间的等待 |
| `sustained_roll_passed` | 全部环境至少有 3 圈连续链、零重置、最大间隔不超过 3 秒 |
| `mean_abs_lateral_displacement_m` | 各环境最终横向位移绝对值的平均，避免正负抵消 |
| `max_abs_lateral_displacement_m` | 最差样本的最终横向偏移绝对值 |

其中 `roll_acceptance_passed` 只检查连续圈数与零重置，`sustained_roll_passed` 进一步检查时间间隔。
报告中兼容保留的 `mean_forward_rolls` 来源于正向角速度积分；阅读完整圈数时使用 `completed_forward_turns`。
姿态计数用于检查朝前翻转，贴地接触、滑移和外观动作仍要结合视频观察。

可以直接抽出主要数据：

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

达到连续翻滚门槛后，方向指标越小越好，但还需要结合前向运动和动作自然程度判断。
如果任务要求固定方向或指定位置，应另设对应误差阈值；本例没有训练目标方向命令或精密位置控制。

## 4. 比较候选，而不只挑最大的文件编号

在相同 seed、50 秒时长、场地和扰动下回放检查点 100、200、300 等候选。每个候选使用独立输出目录。
优先级建议：

1. 无非有限值、无异常起步；
2. 完整圈数、连续链与时间间隔满足目标；
3. 同等连续性下，比较横向偏移、关节抖动和动作表现；
4. 换一些初始状态，确认改善不局限于单一样本。

多 seed、更长回放、摩擦和质量变化是后续扩展实验。先把本阶段的设置固定并保存，再增加难度。
训练与回放的奖励配置可能不同，跨轮总 reward 不能替代上述统一回放比较。

## 5. 为选定模型录一段 1080p 视频

录制前确认 `ffmpeg` 在 Linux 的 `PATH` 中可用，并包含 `h264_nvenc` 编码器；脚本使用 NVIDIA 硬件编码。以下使用 1920 × 1080 相机，每 2 个控制步采一帧，25 fps 编码，50 秒共 1250 帧。

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

视频由仿真相机输出，分辨率与桌面显示器无关。录制跟随视角的动作段时，无需把终端或桌面文件夹放进画面。
本例导出的是无解说音轨素材，可以在直播中插播，也可以后续剪入讲解。

检查编码信息和完整解码：

```bash
ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration \
  -of json "$roll_evidence/continuous-forward-roll.mp4"
ffmpeg -v error -i "$roll_evidence/continuous-forward-roll.mp4" -f null -
```

预期为 1920 × 1080、25 fps、约 50 秒。最后一条无错误输出表示完整解码通过。
仍需打开视频查看起步、中段和结尾，并核对这次录制自己的 `video-validation.json`，不要只沿用批量结果。

## 6. 把模型、参数和素材放在一起

模型名可以简短，但来源要明确。推荐这样的实验包：

```text
output/continuous-roll-training/你的实验编号/
├── README.md                  # 选中哪个检查点、如何回放、当前表现
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

参数取自选定检查点所在的 run，回放报告应指向同一个模型。README 记录源目录、训练配置、测试设置、圈数、间隔和偏移。
原始逐步轨迹、日志和失败候选留在 `artifacts/`，过程说明留在 `work/`。
在新建包目录中为明确的交付文件生成校验清单，再用 `sha256sum -c SHA256SUMS` 检查。

训练和回放有独立超时保护；实验结束时确认相关进程已退出、GPU 使用回落，不重启已经达到截止时间的实验。
本次教程整理复用了已有记录，没有启动新的长训练。

到这里，你已经完成一个完整训练案例：明确动作目标、搭建任务、短训调参、用统一条件选择模型，并导出可展示的成果。
下一页把相同方法迁移到踢球、起身等新任务。
