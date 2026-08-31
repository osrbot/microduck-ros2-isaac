# 安装与准备

项目固定了 MicroDuck 模型和策略的上游版本。记录验证结果时必须先获取这些提交，不要用持续变化的上游分支替代。

## 通用要求

- Git 与 Bash
- 完整流程已验证于 Ubuntu 24.04 x86_64
- Python 3.12
- Isaac 路线需要已有的 Isaac Sim 与 Isaac Lab 安装

未来公开后可按以下方式克隆：

```bash
git clone https://github.com/osrbot/microduck-ros2-isaac.git
cd microduck-ros2-isaac
```

当前阶段仓库仍在本地准备，公开远端尚未创建，请直接使用现有项目目录。

## 获取固定版本输入

```bash
./scripts/fetch_upstream.sh
```

脚本读取根目录的 `upstream.lock`，在被 Git 忽略的 `reference/` 下创建可复现 checkout。

## 准备 MuJoCo 基准

```bash
./scripts/setup_mujoco_env.sh
./scripts/run_official_baseline.sh
```

这一步生成源模型清单和后续对比所需的参考 rollout。仅查看已经生成好的 ROS 包时可以不运行它，但不能因此声称完成全链路验证。

## 安装 ROS 2 依赖

```bash
sudo apt update
sudo apt install \
  ros-jazzy-desktop \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-xacro \
  python3-colcon-common-extensions
```

然后进入[ROS 2 构建与启动](/zh/ros2/)。

## 准备 Isaac Sim

已验证环境使用 Isaac Sim 6.0.1 standalone 和 Isaac Lab 3.0.0 beta 2。若 Isaac Lab 不在默认目录，请指定：

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

脚本把 ONNX Runtime 1.24.4 安装到 `work/isaac_python_pkgs`，不会修改 Isaac Lab checkout。然后进入[USD 转换](/zh/isaac/)。

## 检查环境

```bash
./scripts/check_environment.sh
```

请与[已验证环境](/zh/reference/environment)对照。其他版本可能可以运行，但属于新的测试矩阵，不能自动继承已有结果。
