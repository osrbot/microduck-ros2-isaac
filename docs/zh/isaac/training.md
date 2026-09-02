# 在 Isaac Lab 训练一只会走的鸭

这一页不回放现成 ONNX，而是运行仓库自己的 Isaac Lab 任务，让 PPO 从奖励里学习平地速度和头部控制。
先花十几分钟验证训练流水线，再决定要不要投入几千轮正式实验。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>流水线检查</span><strong>约 10–30 分钟</strong></div>
  <div role="listitem"><span>正式训练</span><strong>数小时起，视 GPU 而定</strong></div>
  <div role="listitem"><span>需要环境</span><strong>Isaac Sim + Isaac Lab</strong></div>
  <div role="listitem"><span>最终产物</span><strong>checkpoint、曲线和回放图</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>走完这页，你会亲手完成</strong>
  <ul>
    <li>启动 <code>Isaac-MicroDuck-Velocity-Flat-v0</code> 原生任务；</li>
    <li>跑完 5 个 iteration，并确认 checkpoint 真的落盘；</li>
    <li>用 TensorBoard 观察训练，而不是只等终端结束；</li>
    <li>重新加载最新 checkpoint，产出 JSON 报告和回放截图；</li>
    <li>分清“流水线跑通”“奖励上升”和“鸭子真的会走”这三件事。</li>
  </ul>
</div>

## 先看全流程，别跑到一半迷路

| 阶段 | 你要做什么 | 过关标准 |
| --- | --- | --- |
| 1. 环境预检 | 确认 GPU 与 Isaac Lab 启动器 | `nvidia-smi` 正常，`isaaclab.sh` 可执行 |
| 2. Smoke 训练 | 64 环境、5 iteration | 输出 `MICRODUCK_TRAIN_STAGE=complete` |
| 3. 查看产物 | 找到新 run 目录 | 有 `model_final.pt` 和 `training_summary.json` |
| 4. 正式实验 | 增加环境数与轮数 | 曲线稳定，摔倒率下降，动作不靠抖动刷分 |
| 5. 回放验收 | 加载 checkpoint 跑 200 步 | JSON、截图生成，亲眼确认动作 |

<div class="md-terminal-map" role="list" aria-label="终端分工">
  <div role="listitem"><strong>终端 A</strong><p>训练进程。正式训练时一直保留，用来观察 stage 和错误。</p></div>
  <div role="listitem"><strong>终端 B</strong><p>TensorBoard。训练开始后再开，不会打断终端 A。</p></div>
  <div role="listitem"><strong>回放窗口</strong><p>训练结束后启动；用画面检查策略到底学成什么样。</p></div>
</div>

<div class="md-command-steps">
  <strong>先开终端 A，终端 B 先不用急</strong>
  <p>按 <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd> 打开终端 A，<code>cd</code> 到仓库根目录。A 从预检一直负责训练；等正式训练开始后，再按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> 打开终端 B 跑 TensorBoard。</p>
</div>

<div class="md-step-kicker"><span>步骤 1</span><strong>终端 A · 按 Ctrl + Alt + T 打开</strong></div>

## 先做环境预检

训练任务不需要 ONNX Runtime，但需要正常的 Isaac Sim、Isaac Lab 和 CUDA。先运行：

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
nvidia-smi
test -x "$ISAACLAB_DIR/isaaclab.sh" && echo "Isaac Lab launcher: OK"
```

如果 Isaac Lab 正好位于 `~/rlgpu_ws/IsaacLab`，可以省略 `export`，脚本会使用默认路径。多 GPU 主机
默认使用 `cuda:0`；第一次不要同时开其他 Isaac Sim 窗口。

<div class="md-checkpoint">
  <strong>预检通过再开训练</strong>
  <p>GPU 能被驱动识别，并且终端打印 <code>Isaac Lab launcher: OK</code>。这一步失败时，训练脚本只会更晚报同一个问题。</p>
</div>

<div class="md-step-kicker"><span>步骤 2</span><strong>终端 A · 第一次只跑 smoke</strong></div>

## 跑 5 轮训练流水线检查

```bash
./scripts/train_isaac_velocity.sh
```

按 <kbd>Enter</kbd> 后提示符不会返回。终端还在持续输出、GPU 仍有占用时，不要再次执行训练命令。
第一次创建 64 个环境可能在某个阶段停留几分钟，先看 stage 有没有继续推进。

脚本默认创建 64 个并行环境、训练 5 个 iteration。启动阶段会比较慢，终端依次出现这些标记：

```text
MICRODUCK_TRAIN_STAGE=creating_environment
MICRODUCK_TRAIN_STAGE=wrapping_environment
MICRODUCK_TRAIN_STAGE=creating_runner
MICRODUCK_TRAIN_STAGE=learning
MICRODUCK_TRAIN_STAGE=saving
MICRODUCK_TRAIN_STAGE=complete
```

中间还会打印左右脚 contact sensor 的绑定信息和 PPO iteration 表格。最后一行到达 `complete` 才算
脚本完整结束；只看到 Isaac 窗口打开不算训练成功。

::: warning 5 轮不会教会鸭子走路
这一步只验证“任务注册 → 多环境仿真 → PPO 更新 → checkpoint 保存”。姿态笨拙、奖励很低都不意外。
它是烟雾报警器测试，不是毕业典礼。
:::

显存紧张时，可以先用本项目已经跑过的最小配置检查一次：

```bash
MICRODUCK_TRAIN_ENVS=16 \
MICRODUCK_TRAIN_ITERATIONS=1 \
./scripts/train_isaac_velocity.sh
```

<div class="md-checkpoint">
  <strong>训练进程这一关通过</strong>
  <p>终端没有 traceback，并以 <code>MICRODUCK_TRAIN_STAGE=complete</code> 收尾。若进程被杀、显存不足或停在 saving 之前，都不能算完成。</p>
</div>

<div class="md-step-kicker"><span>步骤 3</span><strong>终端 A · 检查文件</strong></div>

## 确认 checkpoint 真的落盘

每次训练会创建带时间戳的 run 目录：

```text
work/isaac_training/logs/rsl_rl/microduck_velocity_flat/YYYY-MM-DD_HH-MM-SS/
```

列出最新 checkpoint：

```bash
find work/isaac_training/logs/rsl_rl/microduck_velocity_flat \
  -name model_final.pt -type f -print | sort | tail -n 1
```

对应目录中应至少包含：

```text
model_final.pt
training_summary.json
params/env.yaml
params/agent.yaml
```

`training_summary.json` 记录环境数、iteration、设备、耗时和 checkpoint 路径。它能证明脚本完成并保存，
但不能证明策略已经学会稳定行走。

<div class="md-checkpoint">
  <strong>文件这一关通过</strong>
  <p><code>model_final.pt</code> 与 <code>training_summary.json</code> 位于同一个新 run 目录，而且文件不是空的。现在才值得增加训练预算。</p>
</div>

<div class="md-step-kicker"><span>步骤 4</span><strong>终端 A + 终端 B</strong></div>

## 开始一次正式实验

不要直接照抄最大参数。根据显存从 64、256、512 个环境逐步上调，确认一档稳定后再增加。下面是完整
实验的示例预算，不是所有显卡都适合：

```bash
MICRODUCK_TRAIN_ENVS=1024 \
MICRODUCK_TRAIN_ITERATIONS=4000 \
./scripts/train_isaac_velocity.sh
```

训练启动并进入 `learning` 后，把终端 A 留着。按
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> 新开终端 B，`cd` 到仓库根目录后运行：

```bash
tensorboard --logdir work/isaac_training/logs/rsl_rl/microduck_velocity_flat
```

终端 B 会打印一个地址，通常是 `http://localhost:6006/`。按住 <kbd>Ctrl</kbd> 点击地址，或复制到同一台
Ubuntu 电脑的浏览器。TensorBoard 会一直运行；看完后回到终端 B 按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 关闭。

打开 TensorBoard 给出的本地地址，重点看：

- 总奖励是否在较长区间内上升，而不是偶尔尖峰；
- episode length 是否增加，摔倒和 reset 是否减少；
- 速度跟踪项是否改善；
- action-rate 惩罚是否失控；
- 不同 seed 或不同 run 的趋势是否一致。

如果显存不足，先降低 `MICRODUCK_TRAIN_ENVS`；如果 reward 上升但姿态越来越抖，别继续堆 iteration，
先回放策略并检查 reward 是否鼓励了错误动作。

<div class="md-step-kicker"><span>步骤 5</span><strong>训练结束后 · 仓库根目录</strong></div>

## 回放最新 checkpoint

```bash
./scripts/play_isaac_velocity.sh
```

包装脚本会自动选择最新 `model_final.pt`，默认运行 1 个环境、200 步，并生成：

```text
artifacts/isaac/velocity_playback.json
artifacts/isaac/velocity_playback.png
```

终端最后应看到：

```text
MICRODUCK_PLAYBACK_STAGE=inference-complete
MICRODUCK_PLAYBACK_STAGE=screenshot-complete
MICRODUCK_PLAYBACK_STAGE=complete
```

<div class="md-result-label">真实运行截图 · checkpoint 回放命令完成后</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-training-playback.webp" alt="MicroDuck 原生 Isaac Lab 一轮 smoke checkpoint 的干净回放画面" width="960" height="720" loading="lazy"></div>
  <figcaption><strong>这张图证明 checkpoint 能被重新加载并渲染。</strong>它只训练了 1 轮，所以姿态有点笨拙完全正常。正式实验要看连续动作、曲线和多次回放，不能拿一张截图冒充“已经会走”。</figcaption>
</figure>

想指定某个 checkpoint：

```bash
./scripts/play_isaac_velocity.sh \
  --checkpoint /path/to/model_final.pt
```

想延长回放：

```bash
MICRODUCK_PLAY_STEPS=1000 ./scripts/play_isaac_velocity.sh
```

这两种回放一次只选一种。GUI 还开着时先等它结束，或在终端按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 后再换命令，
不要同时开两个 Isaac 回放抢显卡。

回放会检查观测、动作和奖励是否为有限值，左右脚 contact sensor 是否连接，以及截图是否成功写入。
它不会自动导出 ONNX，也不会自动判断步态好不好；最后一关仍然要靠你看连续运动。

## 这只训练鸭到底学了什么？

任务名是 `Isaac-MicroDuck-Velocity-Flat-v0`，当前版本专注于平地速度和头部姿态：

- 14 个关节位置动作；
- 61 维观测，与公开策略家族保持同样顺序；
- 前后、横移、转向与 4 个头部命令；
- 单脚支撑、脚底打滑、速度/头部跟踪、摔倒重置与动作平滑奖励；
- 推扰动、质量与摩擦随机化；
- RSL-RL PPO，actor/critic 为小型 MLP。

61 维里还保留 6 个 body command 槽位，但第一版没有 body-pose tracking reward。它们是接口占位，
不是已经学会的身体位姿技能。踢球、坐起、低头碰地和前滚仍由[多动作游乐场](./playground)回放
各自公开策略；当前原生训练只负责新的平地行走与头部控制实验。

## 常见问题

| 现象 | 处理顺序 |
| --- | --- |
| `Isaac Lab launcher not found` | 检查 `ISAACLAB_DIR`，确认目录里有可执行的 `isaaclab.sh` |
| CUDA out of memory | 先把 `MICRODUCK_TRAIN_ENVS` 降到 16 或 64 |
| 训练有 iteration，但没有 checkpoint | 确认是否到达 `saving` 和 `complete`，不要把中断当完成 |
| TensorBoard 没有曲线 | 检查 logdir 是否指向 `microduck_velocity_flat`，并刷新 run |
| 回放提示没有 `model_final.pt` | 训练尚未完整保存，或 `--checkpoint` 路径写错 |
| 奖励上升但动作很抖 | 回放连续动作，检查 action-rate 与任务 reward，不要只继续加轮数 |

## 能直接上真机吗？

不能直接这样下结论。当前任务使用 implicit-PD 近似，没有复刻 BAM XL330 的电气、摩擦、饱和、电池、
背隙和通信延迟。它适合学习 Isaac Lab、做 reward 实验和比较策略；真机部署还需要执行器模型、域随机化、
导出契约、安全限制与实体测试。当前没有真机，也不会把仿真结果写成真机验收。

<div class="md-page-complete">
  <strong>训练闭环到这里才算完整。</strong>
  <p>你已经从环境预检走到 smoke、checkpoint、TensorBoard 和回放验收。下一次实验只改一个变量，并保留 run 目录，才看得出改动到底帮了忙还是添了乱。</p>
</div>

<div class="md-next-grid">
  <a class="md-next-card" href="/microduck-ros2-isaac/zh/isaac/custom-environment"><span>继续开发</span><strong>把平地行走改成新任务 →</strong><p>从场景、成功条件、reward、终止与课程逐项设计。</p></a>
  <a class="md-next-card" href="/microduck-ros2-isaac/zh/isaac/playground"><span>先看现成动作</span><strong>回游乐场玩踢球与起身 →</strong><p>对照公开策略的动作效果，再决定下一项训练目标。</p></a>
</div>
