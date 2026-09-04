---
title: 连续翻滚：三轮调试复盘
description: 从没有完整翻转，到修正初始化、稳定续翻和改善方向，逐轮看现象与参数变化。
prev:
  text: 参数和奖励怎么设计
  link: /zh/isaac/roll-parameters
next:
  text: 回放验收与素材导出
  link: /zh/isaac/roll-validation
---

<script setup>
import { withBase } from 'vitepress'
import RollPhaseChart from '../../.vitepress/theme/RollPhaseChart.vue'
</script>

# 从没翻成，到连续翻起来

先看三轮结束后的变化，再回到每一步怎么判断。
这次调试采用“短段训练 → 保存检查点 → 独立回放 → 决定下一步”的节奏。连续翻滚稳定后，才把重点转向方向。

## 三轮发生了什么

| 阶段 | 主要工作 | 独立回放 | 下一步判断 |
| --- | --- | --- | --- |
| 初始诊断 | 检查原 ONNX 的动作范围和翻转计数 | 截断 / 不截断两种设置均为 0 圈 | 重新定义进度奖励，继续排查初始化 |
| 第一轮 | 完整净角度进度 + 整圈奖励；回放时修正高度并扩大场地 | 1 个环境 / 30 s，17 圈连续、0 重置，横向位移约 7.20 m | 把高度修正纳入训练，保留方向问题 |
| 第二轮 | 正确高度起步，继续训练 | 8 个环境 / 各 50 s，36～37 圈连续、0 重置，平均横向位移约 −12.36 m | 连续性达到目标，开始约束方向 |
| 第三轮 | 滚动轴对齐、更强侧向速度和偏轴约束 | 8 个环境 / 各 50 s，全部 39 圈连续、0 重置，平均绝对横向位移约 0.70 m | 选定检查点，录制并整理结果 |

第一轮与后两轮的时长和初始状态不同，表格用来理解调试路线。比较模型优劣时，应再使用相同设置回放。
第二轮表中的负数表示横向方向；第三轮使用绝对值平均，避免正负偏移相互抵消。

## 初始诊断：为什么有角速度却没有整圈？ {#diagnosis}

早期配置用正向俯仰角速度、角速度跟踪、目标前进速度和高度带奖励鼓励运动。
这种定义允许机器人在小范围内摆动，或者停在容易得分的姿态。继续增加 iteration，可能只是让同一种行为更加稳定。

本次先回放公开的 `roulade.onnx`，检查动作接口和实际姿态：

- 保留 `±1` 截断：15 秒内 0 个完整翻转；约 15.9% 的原始动作被截断。
- 去掉截断：30 秒内仍为 0 个完整翻转。
- 两段回放的净相位最大变化约 2.35 rad，即约 135°，还没有走完 360°。

这两段诊断的对象都是原始 ONNX。早期长训模型单独保留，不混入这个对比。

<RollPhaseChart />

**怎么查：** 同时记录原始动作幅度、净翻转相位、完整圈数和视频。
动作范围暴露了接口问题；去掉截断之后的结果又说明，还需要修改任务定义。
如果只观察正向角速度积分，反复向前摆动就会不断累计，看起来一直在进步。

### 自己做一次相同类型的诊断

先完成[主线环境预检](./continuous-roll#setup)，沿用同一终端中的 `roll_evidence` 和 `roll_deadline`。
下面使用当前已经修正高度的回放配置，适合检查新环境；历史诊断使用的旧配置和数值保留在本页复盘中。

```bash
MICRODUCK_PLAY_STEPS=1500 MICRODUCK_PLAY_TIMEOUT=240 \
MICRODUCK_PLAY_OUTPUT="$roll_evidence/onnx-check.json" \
MICRODUCK_PLAY_SCREENSHOT="$roll_evidence/onnx-check.png" \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 260 \
  --status "$roll_evidence/onnx-check-status.json" -- \
  bash scripts/play_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --viz none \
    --policy-onnx reference/microduck/policies/roulade.onnx \
    --arena-half-width 25 --trace "$roll_evidence/onnx-check-trace.json"
```

看报告中的 `maximum_raw_action`、`raw_action_fraction_above_one`、`completed_forward_turns`。
`--full-roll-v2` 已经关闭动作截断，无需再重复传 `--unclipped-actions`。
要做新的截断对照实验，应只改变动作限幅，保持高度、场地、时长和 seed 相同；不要直接移除整个 profile 来冒充单变量比较。

## 第一轮：先学会跨过完整的 360°

### 改了什么

从原 Actor 和归一化统计热启动，保留模型执行器设置，使用：

- 新达到的净翻转角度奖励，权重 8；
- 每完成一圈的奖励，权重 6；
- 关闭旧动作截断，移除目标线速度和高度带得分；
- 暂停质量、摩擦、推扰与观测噪声，episode 12 秒；
- 初始学习率 `1e-4`，目标 KL `0.005`，1024 个环境。

这些是同一轮的组合调整，不能根据一次结果断言某一项单独贡献了多少。

### 回放暴露了第二个问题

最初回放检查点 100：30 秒里累计 17 圈，但最长连续链只有 6 圈，且发生了 2 次越界重置。
继续查看重置遥测，发现嵌套 USD 的根偏移没有一致地进入 reset 位置。

我们在独立回放中把根高度修正为 `0.125 m`，并把横向场地半宽从 1 m 放宽到 10 m，观察连续动作：
结果变成 17 圈连续、零重置，最长整圈间隔 1.80 秒。
两个设置同时变化，因此这里的零重置结果同时受初始化修正和边界放宽影响。

<figure class="md-doc-figure">
  <video controls playsinline preload="none" width="1280" height="720" style="display:block;width:100%;height:auto;aspect-ratio:16/9;background:#252832" aria-label="第一轮检查点 100 的修正高度回放，前 10 秒片段">
    <source :src="withBase('/media/continuous-roll/first-rolls.mp4')" type="video/mp4" />
  </video>
  <figcaption>第一轮检查点 100：修正高度后的回放，截取前 10 秒。完整 30 秒记录完成 17 圈，但横向位移约 7.20 m。</figcaption>
</figure>

**这一轮的结论：** 完整动作已经出现，出生高度需要统一，方向仍需优化。
第一轮计划最多 1200 次更新或 900 秒；得到诊断结果后提前停止，最后日志标签 245，保留已保存的检查点 200 供下一轮续训。

## 第二轮：把正确的起点放进训练

在训练 reset 中加入 z 偏移 `0.12 m`，从第一轮检查点 200 继续。
保持完整翻转奖励，先观察能否从多个轻微不同的站姿连续翻起来。

本轮检查点 300 在 8 个环境中各回放 50 秒，圈数为：

```text
37, 36, 37, 36, 36, 36, 36, 37
```

所有环境零重置，最长连续链等于各自总圈数。初始根高度均为 `0.125 m`，roll / pitch / yaw 各 `±0.03 rad`，关节初值缩放 `±0.003`，seed 为 109。
这里是同一个 seed 下的 8 个初始状态样本。

连续动作已经达到阶段目标，但平均前向位移约 12.12 m、平均横向位移约 −12.36 m。
只看圈数会错过这个问题，所以第三轮开始单独改善方向。

第二轮计划追加 800 次更新，上限 750 秒，实际在日志标签 547 后提前停止；检查点 500 已保存。
下一轮从**已做批量回放的检查点 300**起步，保留它作为回退模型。

## 第三轮：让翻滚方向更稳定 {#direction-training}

### 调整前先想清楚约束什么

直接惩罚所有角速度会抑制翻滚，要求身体一直直立也会与动作目标冲突。
这次保留 pitch 转动自由度，约束翻滚平面和横向运动：

```text
新增滚动轴对齐：               -3
横向速度平方权重：     -0.2 → -3
偏轴角速度平方权重：  -0.01 → -0.03
净角度进度 / 整圈奖励：        8 / 6（保持）
```

本轮从第二轮检查点 300 追加 600 次更新，日志标签为 300～899，正常完成。
随后选择有独立批量回放记录的第三轮检查点 600，命名为交付模型 `model_best.pt`。
“最佳”在这里指通过本次选模标准的候选，不代表评估过所有保存点。

### 自己续训时怎么操作

沿用主线中的实验目录和绝对截止时间，把检查点路径换成自己**已回放通过**的候选：

```bash
roll_checkpoint="$roll_session/roll/替换为实际运行时间目录/model_200.pt"
test -s "$roll_checkpoint" && \
MICRODUCK_TRAIN_ENVS=1024 MICRODUCK_TRAIN_ITERATIONS=600 \
python3 scripts/run_before_deadline.py \
  --deadline "$roll_deadline" --max-seconds 600 \
  --status "$roll_evidence/direction-status.json" -- \
  bash scripts/train_isaac_velocity.sh \
    --profile continuous_roll --full-roll-v2 --straight-roll --viz none \
    --resume-checkpoint "$roll_checkpoint" \
    --log-root "$roll_session/direction"
```

期望看到 `loading_resume_checkpoint`、`MICRODUCK_ROLL_RESUME_SHA256=...` 和新的 run 目录。
`--straight-roll` 开启方向奖励；回放入口仍使用 `--full-roll-v2`，因为推理时只需要一致的观测、动作和重置配置。
选模依据是回放行为指标，回放报告的总 reward 不能当作方向训练奖励的直接复算。

## 如果你遇到别的结果，按这个顺序查

| 现象 | 先检查 | 然后尝试 |
| --- | --- | --- |
| 起步就穿地、弹飞或散架 | 根高度、碰撞、坐标和资产版本 | 修正初始化后短回放，不先改 PPO |
| 反复前后摆，没有整圈 | 净相位、进度奖励、动作输出范围 | 检查奖励是否重复支付同一段动作 |
| 会翻，但几圈就重置 | `done_count`、终止位置、episode 时长 | 区分越界、超时与动作失败 |
| 扩大场地后一直斜着走 | 横向位移和滚动轴方向 | 在相同回放条件下比较方向约束 |
| 圈数上去了，关节动作很抖 | 动作变化、力矩项、KL、学习率 | 一次调整一组约束，保留原模型 |
| 很平稳，却不愿意起翻 | 主任务奖励与约束项的实际量级 | 检查平滑/姿态约束是否压过任务奖励 |
| 换 seed 或出生姿态就失败 | 训练与回放的初始分布 | 小步扩大随机化，再复验 |

## 把自己的调参记录写成五行

```text
观察：在同一组回放里，具体哪里不理想？
假设：哪个配置或接口可能造成这个现象？
改变：本轮修改哪一组参数，旧值和新值是什么？
比较：同样的时长、seed、场地和初始扰动，指标怎样变化？
决定：保留、回退，还是继续查另一个问题？
```

达到阶段目标就进入验收；预算耗尽时保存可用结果和失败记录，不自动延长。
下一页给出批量回放、指标读取和录制命令，把选模与素材整理一起完成。
