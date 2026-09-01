# 让 MicroDuck 在 Isaac Sim 里走起来

这部分假设电脑里已经安装 Isaac Sim 和 Isaac Lab。USD 已经在仓库里；下面只需要下载公开策略，
并在项目目录准备 ONNX Runtime。环境准备好以后，就可以正式放鸭开跑。

## 1. 准备策略运行环境

在仓库根目录运行：

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

如果 Isaac Lab 正好在默认的 `~/rlgpu_ws/IsaacLab`，可以省略 `ISAACLAB_DIR`。

## 2. 放鸭开跑

在带图形桌面的 Linux 中运行：

```bash
./scripts/run_isaac_policy.sh \
  --duration 60 \
  --vx 0.3 \
  --action-scale 0.9 \
  --follow-camera \
  --viz kit
```

Isaac Sim 会打开，把 MicroDuck 放到地面上，然后运行行走策略，镜头会跟随机器人。仿真速度可能
比真实时间慢，终端每五个仿真秒会输出一次进度。

## 想让它先乖乖站好

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_stand.onnx \
  --duration 30 \
  --action-scale 1.0 \
  --follow-camera \
  --viz kit
```

## 不看画面，先跑一小圈

下面的命令适合快速检查环境：

```bash
./scripts/run_isaac_policy.sh \
  --duration 10 \
  --vx 0.3 \
  --action-scale 0.9 \
  --headless
```

运行结束后会把简单结果写到 `artifacts/isaac/policy_rollout.json`。普通教程不需要阅读这个文件，
只有排查问题时才用得上。

## 鸭子走着走着，Isaac Sim 崩了？

- 通过 `run_isaac_policy.sh` 启动，不要直接运行 Python 文件。包装脚本会在需要时只选择一个
  NVIDIA Vulkan 设备。
- 开始新任务前先关闭其他 Isaac Sim 窗口。
- 先用空场景确认 NVIDIA 驱动、Vulkan 和 Isaac Sim 本身可以稳定运行。
- 尝试无界面命令。如果 headless 正常而 GUI 崩溃，问题更可能在渲染或桌面会话。
- GPU 环境变量和进一步检查见[故障排查](/zh/troubleshooting)。

::: details 高级设置
包装脚本默认使用 `cuda:0`。多 GPU 主机确实需要时可以覆盖：

```bash
export MICRODUCK_ISAAC_DEVICE=cuda:0
export MICRODUCK_VULKAN_ICD=/etc/vulkan/icd.d/nvidia_icd.json
export MICRODUCK_ISAAC_ACTIVE_GPU=0
```

公开策略读取 61 个数值，控制仿真模型里的 14 个关节。物理频率为 200 Hz，策略推理频率为
50 Hz。这些信息在修改运行器时有用，第一次回放时不用先理解。
:::

这里提供的是策略回放，不是开箱即用的 Isaac Lab 训练任务。当前项目不包含 reward、reset、
curriculum 或 ROS 到 Isaac 的控制桥。
