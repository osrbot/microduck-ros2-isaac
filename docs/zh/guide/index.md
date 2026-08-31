# 选择你的使用路线

本仓库基于同一组固定版本的 MicroDuck 上游输入，提供两条彼此独立的工作流。先选择与你目标一致的最短路线。

## 我想在 ROS 2 中查看机器人

如果你需要机器人描述、TF 树、RViz 模型或交互关节滑块，选择 ROS 2 路线。它不依赖 Isaac Sim。

1. 完成[安装与准备](./installation)。
2. [构建 ROS 2 description 包](/zh/ros2/)。
3. [打开并操作 RViz](/zh/ros2/rviz)。

预期结果：RViz 中显示完整的 15 刚体模型，可保持官方 home pose，也可用滑块操作策略使用的 14 个关节。

## 我想在 Isaac Sim 中运行官方策略

如果你需要经过验证的 USD articulation，或希望回放已发布的 ONNX 策略，选择 Isaac 路线。

1. 完成[安装与准备](./installation)。
2. [转换并检查 USD](/zh/isaac/)。
3. [回放 ONNX 策略](/zh/isaac/policy-playback)。

预期结果：15 刚体、14 关节的机器人在 Isaac 中以 50 Hz 执行 61 输入、14 输出的站立或行走策略。

## 我想复现全部记录结果

两套环境都准备好后运行：

```bash
./scripts/validate_all.sh
```

脚本包含八个无界面验证阶段，但不能代替人工 GUI 验收、直播彩排、实体硬件测试或原生 Isaac Lab 训练。

## 当前能力边界

| 已提供 | 尚未提供 |
| --- | --- |
| ROS 2 Jazzy 描述与 RViz | 实体机器人驱动 |
| 生成并检查过的 Isaac USD | ROS 到 Isaac 控制桥 |
| MuJoCo 与 Isaac 策略回放 | 原生 Isaac Lab 训练环境 |
| 可保留的 JSON 验证证据 | 硬件标定和安全极限 |

公开演示前请先阅读[已知限制](/zh/reference/limitations)。
