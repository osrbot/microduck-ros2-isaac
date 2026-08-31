# MicroDuck ROS 2 + Isaac Sim

[English](README.md) · [在线文档](https://osrbot.github.io/microduck-ros2-isaac/zh/)

这是面向 [Pollen Robotics MicroDuck](https://pollen-robotics.com/microduck/) 的独立、可复现 ROS 2 Jazzy 与 NVIDIA Isaac Sim 兼容项目。项目把固定版本上游 MJCF 与已发布 ONNX 策略作为源输入，增加 ROS 可视化、经过检查的 USD、策略回放和机器可读验证证据。

> 这是社区项目，与 Pollen Robotics 不存在隶属或背书关系，也不是原生 Isaac Lab 训练环境。

## 当前包含什么

| 路线 | 已提供 | 明确不包含 |
| --- | --- | --- |
| ROS 2 | `microduck_description`、15 个物理 link、14 个关节、惯性、RViz、TF、滑块 | 硬件驱动和 `ros2_control` |
| Isaac Sim | 转换后的 USD、碰撞修正、结构检查 | 训练/接触/执行器物理一致 |
| 策略 | 官方 ONNX 回放、61 → 14 契约、50 Hz | ROS 到 Isaac bridge |
| 证据 | MuJoCo/Isaac rollout、ROS runtime、JSON | 实体机器人验收 |

实体运行时提到嘴部执行器，但选定公开 MJCF 和策略只定义 14 个可动关节。本项目不会虚构缺少的仿真几何、极限和策略行为。

## 快速开始

固定上游输入并建立 MuJoCo 参考环境：

```bash
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
./scripts/run_official_baseline.sh
```

构建并打开 ROS 2 描述：

```bash
./scripts/generate_ros_description.py
./scripts/validate_ros2_package.sh
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

准备 Isaac、转换 USD 并运行行走策略：

```bash
cd ../
./scripts/setup_isaac_python_env.sh
./scripts/convert_mjcf_to_usd.sh
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_walking.onnx \
  --duration 10 --vx 0.3 --action-scale 0.9 --headless \
  --output artifacts/isaac/policy_walk_local.json
```

两套环境就绪后运行全部八个无界面验证阶段：

```bash
./scripts/validate_all.sh
```

完整要求与分路线教程见[入门文档](https://osrbot.github.io/microduck-ros2-isaac/zh/guide/)。Node.js 24 下可本地预览文档：

```bash
npm ci
npm run docs:dev
```

## 已记录测试矩阵

已验证于 Ubuntu 24.04、ROS 2 Jazzy、RTX 4080 SUPER、Isaac Sim 6.0.1 与 Isaac Lab 3.0.0 beta 2。模型包含 15 个刚体、14 个可动关节、约 0.737243 kg 总质量，并以 50 Hz 执行 `61 -> 14` ONNX 契约。

在其他主机或版本复用结论前，请阅读[验证结果](https://osrbot.github.io/microduck-ros2-isaac/zh/reference/results)和[已知限制](https://osrbot.github.io/microduck-ros2-isaac/zh/reference/limitations)。

## 许可

原创兼容代码与文档采用 Apache-2.0。来自上游模型的网格、Xacro 和 USD 继续受 Pollen Robotics 模型条款约束；上游描述为“Creative Commons BY-SA-NC”但没有注明版本。请把本项目视为混合许可仓库，保留署名，并在再分发或变现前阅读 [`NOTICE-MICRODUCK.md`](NOTICE-MICRODUCK.md)。
