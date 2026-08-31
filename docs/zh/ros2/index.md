# 构建 ROS 2 机器人描述

`microduck_description` 由固定版本 MJCF 生成，包含一个无质量 ROS `base_link`、15 个物理 link、一个固定根关节、14 个旋转关节、网格、惯性、launch 文件和 RViz 配置。

## 生成并验证

在仓库根目录运行：

```bash
./scripts/generate_ros_description.py
work/mujoco_env/bin/python scripts/validate_ros_mjcf_pose_parity.py
./scripts/validate_ros2_package.sh
```

位姿检查会把 109 个 body-joint、惯性、visual 和 collision 原点与源 MJCF 对比，也覆盖容易让颈部或腿部网格分离的精确 ±90° pitch 情况。

## 手动构建

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## 启动演示配置

```bash
ros2 launch microduck_description view_microduck.launch.py
```

默认配置优先保证演示流畅：只加载 visual 网格、不加载 collision 网格、RViz 上限 15 FPS、隐藏 TF 坐标轴并发布静态官方 home pose。

| 参数 | 默认值 | 用途 |
| --- | --- | --- |
| `use_gui` | `false` | 打开 14 个策略关节滑块 |
| `use_rviz` | `true` | 启动 RViz |
| `rviz_fullscreen` | `false` | 窗口无法最大化时强制全屏 |
| `with_collision_meshes` | `false` | 额外加载碰撞网格 |
| `joint_velocity_limit` | `6.0` | 仿真/规划占位值，不是硬件真值 |

例如：

```bash
ros2 launch microduck_description view_microduck.launch.py \
  use_gui:=true rviz_fullscreen:=true
```

## 运行时验收

```bash
./scripts/validate_ros2_runtime.sh
```

该脚本检查实际运行节点、`robot_description`、官方 14 关节 home pose、JointState 和 TF。仅仅构建成功不等于运行契约成立。
