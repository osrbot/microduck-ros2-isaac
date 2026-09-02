# MicroDuck ROS 2 + Isaac Sim

[English](README.md) · [打开中文教程](https://osrbot.github.io/microduck-ros2-isaac/zh/)

把这只开源小鸭子请进 RViz，扭扭脖子、动动腿，再放到 Isaac Sim 里溜两圈。

这是一份可以直接照着做的
[Pollen Robotics MicroDuck](https://pollen-robotics.com/microduck/) 上手教程，覆盖
ROS 2 Jazzy 和 NVIDIA Isaac Sim。少讲一点干巴巴的理论，先让鸭子出现在屏幕上。

你可以带它走三条路线：

- 在 RViz 里打开完整模型，用滑块移动关节；
- 在 Isaac Sim 里打开仓库自带的 USD，玩行走、坐起、低头碰地、踢球和前滚策略；
- 用原生 Isaac Lab 任务训练新的平地行走策略，或者让 ROS 2 遥控 Isaac 游乐场。

只想先和鸭子打个照面？从 ROS 2 开始就行，不需要安装 Isaac Sim。

## ROS 2 快速开始

先安装 ROS 2 Jazzy Desktop 和 `python3-colcon-common-extensions`，然后运行：

```bash
git clone https://github.com/osrbot/microduck-ros2-isaac.git
cd microduck-ros2-isaac/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

RViz 会把 MicroDuck 请到屏幕中央，另一个窗口里有 14 个关节滑块。镜头怎么移动、鸭子看起来
少了零件时怎么检查，见
[ROS 2 教程](https://osrbot.github.io/microduck-ros2-isaac/zh/ros2/)。

不想自己拖滑块，可以让它自动点头、踏步和鞠躬：

```bash
ros2 launch microduck_examples rviz_motion_demo.launch.py
```

完整的 RViz 动作、ROS 遥控 Isaac 和自动动作编排见
[ROS 2 例程](https://osrbot.github.io/microduck-ros2-isaac/zh/ros2/examples)。

## Isaac Sim 多动作游乐场

仓库已经带了可以直接打开的 USD：

```text
assets/isaac/robot_allcollisions/robot_allcollisions.usda
```

先在 Isaac Sim 里打开它，鸭子就算顺利进场了。要让它一次玩多个动作，需要电脑里已经安装
Isaac Sim 和 Isaac Lab：

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

安装说明和无界面运行方式见
[Isaac Sim 教程](https://osrbot.github.io/microduck-ros2-isaac/zh/isaac/)，里面也有 ROS 2 遥控和训练路线。

## Isaac Lab 训练冒烟

仓库已经包含原生任务 `Isaac-MicroDuck-Velocity-Flat-v0`。先用 5 个 iteration 检查整条训练链：

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/train_isaac_velocity.sh
```

5 轮只证明任务注册、多环境仿真、PPO 更新和 checkpoint 能跑，不代表鸭子已经学会走。正式实验见
[训练教程](https://osrbot.github.io/microduck-ros2-isaac/zh/isaac/training)。

## 仓库里有什么

- `ros2_ws/src/microduck_description/`：ROS 2 description 包、网格、launch 和 RViz 配置。
- `ros2_ws/src/microduck_control_bridge/`：ROS 命令与 Isaac 游乐场状态桥。
- `ros2_ws/src/microduck_examples/`：纯 RViz 动作和 ROS→Isaac 自动表演例程。
- `assets/isaac/`：Isaac 教程直接使用的 USD。
- `source/microduck_isaac_lab/`：原生 Isaac Lab 任务和 RSL-RL PPO 配置。
- `scripts/`：环境准备、模型转换、策略游乐场、训练和验证脚本。
- `docs/`：中英文教程网站。
- `artifacts/`：给维护者查看的技术测试记录，不是入门必读内容。

这个项目解决模型查看、仿真互动和学习实验，不包含实体机器人驱动或 `ros2_control`。Isaac 训练任务
使用 implicit-PD 近似，不等于已经完成 sim2real。

## 来源与许可

这是独立社区项目，不代表 Pollen Robotics 官方。原创兼容代码和文档使用 Apache-2.0。
上游模型派生的网格、Xacro 和 USD 继续遵守 Pollen Robotics 所描述的
“Creative Commons BY-SA-NC（版本未注明）”。再分发或商业使用前请阅读
[`NOTICE-MICRODUCK.md`](NOTICE-MICRODUCK.md)。
