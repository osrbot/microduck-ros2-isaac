# 安装需要的软件

## 克隆教程仓库

```bash
git clone https://github.com/osrbot/microduck-ros2-isaac.git
cd microduck-ros2-isaac
```

ROS 2 功能包和 Isaac USD 已经放在仓库里。第一次运行不需要重新生成它们。

## ROS 2 路线

下面的命令适用于 Ubuntu 24.04 和 ROS 2 Jazzy：

```bash
sudo apt update
sudo apt install \
  ros-jazzy-desktop \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-xacro \
  python3-colcon-common-extensions
```

安装完成后继续：[在 RViz 打开 MicroDuck](/zh/ros2/)。

## Isaac Sim 路线

先安装 NVIDIA Isaac Sim 和 Isaac Lab。本项目实际测试过的组合是：

- Ubuntu 24.04；
- Isaac Sim 6.0.1 standalone；
- Isaac Lab 3.0.0 beta 2；
- 能正常使用驱动和 Vulkan 的 NVIDIA 显卡；
- `git`、`bash`、Python 3.12 和 `uv`。

如果 Isaac Lab 不在 `~/rlgpu_ws/IsaacLab`，先告诉脚本它在哪里：

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
```

仓库已经带了 USD。要运行单策略或多动作游乐场，再下载公开策略文件并准备项目自己的 ONNX Runtime：

```bash
./scripts/fetch_upstream.sh
./scripts/setup_isaac_python_env.sh
```

这些命令只会在项目里创建被 Git 忽略的 `reference/` 和 `work/`，不会修改你的 Isaac Lab。

安装完成后继续：[在 Isaac Sim 打开 MicroDuck](/zh/isaac/)。原生训练任务不需要 ONNX Runtime，
但使用同一套 Isaac Sim / Isaac Lab 安装。

::: tip 其他版本也可能可以运行
上面的版本是我们实际使用过的组合，不代表其他版本一定不能用。如果你使用更新的 Isaac，建议先
打开仓库自带的 USD，确认模型能加载，再继续运行策略。
:::
