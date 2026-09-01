# MicroDuck ROS 2 + Isaac Sim

[English](README.md) · [打开中文教程](https://osrbot.github.io/microduck-ros2-isaac/zh/)

把这只开源小鸭子请进 RViz，扭扭脖子、动动腿，再放到 Isaac Sim 里溜两圈。

这是一份可以直接照着做的
[Pollen Robotics MicroDuck](https://pollen-robotics.com/microduck/) 上手教程，覆盖
ROS 2 Jazzy 和 NVIDIA Isaac Sim。少讲一点干巴巴的理论，先让鸭子出现在屏幕上。

你可以带它走两条路线：

- 在 RViz 里打开完整模型，用滑块移动关节；
- 在 Isaac Sim 里打开仓库自带的 USD，运行已经发布的行走策略。

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

## Isaac Sim 快速开始

仓库已经带了可以直接打开的 USD：

```text
assets/isaac/robot_allcollisions/robot_allcollisions.usda
```

先在 Isaac Sim 里打开它，鸭子就算顺利进场了。要让它走起来，需要电脑里已经安装 Isaac Sim 和
Isaac Lab：

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
./scripts/run_isaac_policy.sh \
  --duration 60 --vx 0.3 --action-scale 0.9 \
  --follow-camera --viz kit
```

安装说明和无界面运行方式见
[Isaac Sim 教程](https://osrbot.github.io/microduck-ros2-isaac/zh/isaac/)。

## 仓库里有什么

- `ros2_ws/src/microduck_description/`：ROS 2 description 包、网格、launch 和 RViz 配置。
- `assets/isaac/`：Isaac 教程直接使用的 USD。
- `scripts/`：环境准备、模型转换、策略运行和维护脚本。
- `docs/`：中英文教程网站。
- `artifacts/`：给维护者查看的技术测试记录，不是入门必读内容。

这个项目主要解决模型查看和仿真运行，不包含实体机器人驱动、`ros2_control`，也不是开箱即用的
Isaac Lab 训练任务。

## 来源与许可

这是独立社区项目，不代表 Pollen Robotics 官方。原创兼容代码和文档使用 Apache-2.0。
上游模型派生的网格、Xacro 和 USD 继续遵守 Pollen Robotics 所描述的
“Creative Commons BY-SA-NC（版本未注明）”。再分发或商业使用前请阅读
[`NOTICE-MICRODUCK.md`](NOTICE-MICRODUCK.md)。
