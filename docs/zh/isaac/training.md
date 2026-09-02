# 在 Isaac Lab 训练一只会走的鸭

这里不再回放现成 ONNX，而是启动仓库自己的原生 Isaac Lab 任务：同时复制许多只 MicroDuck，让 PPO
根据奖励反复试走。先用 5 个 iteration 验证流水线，再决定要不要投入几千轮正式训练。

## 先认识这个任务

任务名是 `Isaac-MicroDuck-Velocity-Flat-v0`，第一版专注于平地速度和头部姿态：

- 动作：14 个关节位置目标；
- 观测：61 维，与公开策略家族保持相同顺序；
- 命令：前后、横移、转向、4 个头部命令，以及为 61 维接口保留的 6 个 body command 槽位；
- 训练要素：双足单脚支撑、脚底打滑、速度/头部跟踪、摔倒重置、推扰动、质量与摩擦随机化；
- 课程：先让鸭子学会迈步，再逐步增加站立样本、动作平滑强度和头部活动范围，并留出 15% 样本专练原地转向；
- 算法：RSL-RL PPO，actor/critic 都是小型 MLP。

保持 61 维的意义是以后导出和运行时更容易对齐，但这套任务仍是独立的 Isaac 教学环境，不冒充上游
`microduck_rl` 的 BAM 执行器和完整 sim2real 配方。

这里的 body command 会以很小的范围进入观测，但第一版没有给它 body-pose tracking reward：它是接口
占位，不是一个已经学会的身体位姿技能。现成的踢球、坐起、低头碰地和前滚仍由
[多动作游乐场](./playground)回放各自的公开策略；当前原生训练只负责“新学一套平地行走 + 头部控制”。

## 1. 跑 5 轮冒烟训练

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/train_isaac_velocity.sh
```

脚本默认使用 64 个环境、5 个 iteration，并把日志留在：

```text
work/isaac_training/logs/rsl_rl/microduck_velocity_flat/
```

看到环境创建、PPO 开始采样并完成 5 轮，说明“任务注册 → 多环境仿真 → 网络更新 → checkpoint”这条链
跑通了。5 轮还学不会走，这是流水线检查，不是毕业典礼。

想先照着本项目已经跑过的最小配置复现，可以用 16 个环境、1 个 iteration：

```bash
MICRODUCK_TRAIN_ENVS=16 \
MICRODUCK_TRAIN_ITERATIONS=1 \
./scripts/train_isaac_velocity.sh
```

这次实测采集了 384 step，约 530 step/s，完成一次 PPO 更新并写出 `model_final.pt`。这些数字只是
RTX 4080 SUPER 上的一次参考，不是跑分目标；真正要确认的是训练没有中途退出，而且 checkpoint
确实落盘。

## 2. 开始一次真正的实验

显存够用时可以逐步增加环境和轮数：

```bash
MICRODUCK_TRAIN_ENVS=1024 \
MICRODUCK_TRAIN_ITERATIONS=4000 \
./scripts/train_isaac_velocity.sh
```

不要一上来盲跑 4000 轮。先看 TensorBoard 里的总奖励、速度跟踪、episode length、摔倒频率和
action-rate 项，再打开 checkpoint 看动作是不是“真的在走”，而不是靠抖动刷分。

```bash
tensorboard --logdir work/isaac_training/logs/rsl_rl/microduck_velocity_flat
```

## 3. 回放最新 checkpoint

```bash
./scripts/play_isaac_velocity.sh
```

脚本会选择最新的 `model_final.pt`，默认让 1 只鸭子跑 200 步，并留下报告和一张干净的 960×720
截图：

```text
artifacts/isaac/velocity_playback.json
artifacts/isaac/velocity_playback.png
```

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-training-playback.webp" alt="MicroDuck 原生 Isaac Lab 一轮 smoke checkpoint 的干净回放画面" width="960" height="720" loading="lazy"></div>
  <figcaption><strong>这张图证明 checkpoint 能被重新加载并渲染。</strong>它只训练了 1 轮，所以姿态有点笨拙完全正常；别把“会生成截图”写成“已经学会走路”。</figcaption>
</figure>

想点名某个 checkpoint，可以加 `--checkpoint /path/to/model_final.pt`；想多跑一会儿，可以设置
`MICRODUCK_PLAY_STEPS`。回放会检查观测、动作、奖励是否为有限值，左右脚接触传感器是否真的连上，
以及截图有没有落盘。它不会自动导出 ONNX，更不会把 5 轮 smoke 训练魔法变成会走路的鸭子——正式训练
跑够以后，曲线要看，动作也要亲眼看。

## 训练结果能直接上真机吗？

不能直接这样下结论。当前 Isaac 任务使用经过回放验证的 implicit-PD 近似，没有复刻上游 BAM XL330
的电气、摩擦、饱和、电池、背隙和通信延迟。它适合学 Isaac Lab、做奖励实验和比较策略；真机部署仍需
单独的执行器模型、域随机化、导出契约、安全限制和实体测试。

想做踢球、起身或障碍地形，下一页讲清楚[怎样再造一个训练任务](./custom-environment)。
