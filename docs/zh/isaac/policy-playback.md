# 回放 ONNX 策略

运行器在 Isaac Sim 中重建已发布的策略接口。它是策略回放适配层，不是原生 Isaac Lab 训练环境。

## 无界面站立测试

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_stand.onnx \
  --duration 5 --action-scale 1.0 --headless \
  --output artifacts/isaac/policy_stand_local.json
```

## 无界面行走测试

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_walking.onnx \
  --duration 10 --vx 0.3 --action-scale 0.9 --headless \
  --output artifacts/isaac/policy_walk_local.json
```

## 可视化回放

在带 `DISPLAY` 的图形桌面会话中运行：

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_walking.onnx \
  --duration 60 --vx 0.3 --action-scale 0.9 \
  --follow-camera --viz kit
```

包装脚本在发现重复 NVIDIA Vulkan ICD 时选择单一 manifest，关闭 Kit 多 GPU 渲染，并让渲染 GPU 与计算设备一致。仅在你的主机确实需要时覆盖：

```bash
export MICRODUCK_ISAAC_DEVICE=cuda:0
export MICRODUCK_VULKAN_ICD=/etc/vulkan/icd.d/nvidia_icd.json
export MICRODUCK_ISAAC_ACTIVE_GPU=0
```

Kit GUI 回放可能明显慢于真实时间，长任务每五个仿真秒输出一次进度。

## 策略契约

| 观测块 | 宽度 |
| --- | ---: |
| 基座角速度 | 3 |
| 投影重力 | 3 |
| 相对 home 的关节位置 | 14 |
| 关节速度 | 14 |
| 上一次原始动作 | 14 |
| twist、头部姿态与身体姿态命令 | 13 |
| **总计** | **61** |

14 维输出从策略关节顺序映射到 Isaac 关节顺序，然后按下式应用：

```text
target = 官方 home pose + action scale * 原始策略动作
```

物理频率 200 Hz，推理频率 50 Hz。当前 Isaac 执行器是简化 implicit-PD，因此只声明有限值/保持直立的行为 smoke parity，不声明与 MuJoCo 轨迹相同。

每次运行生成 JSON，记录输入、命令、时序、根姿态、最大倾角、推理耗时和 finite/upright 状态。视频不能替代这份可复核证据。
