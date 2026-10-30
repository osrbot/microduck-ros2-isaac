# 故障排查

从对应现象开始检查。除明确写了 `cd ros2_ws` 的代码块外，命令均在项目根目录执行。
ROS 命令使用已经加载 ROS 和工作区环境的终端。Humble 用户将命令中的 `jazzy` 换成 `humble`。

## RViz 相机不能移动

使用仓库当前 RViz 配置。选择 **Move Camera**（或按 `M`），在空白 3D 区域左键拖动，滚轮缩放。若工具栏或 Views 不存在，可能是旧安装覆盖了当前 workspace：

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 pkg prefix microduck_description
```

输出应指向当前 workspace 的 `install/`。

## Humble 中 RViz 启动后崩溃

如果命令包含 `rviz_fullscreen:=true`，先删掉它，再启动：

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

`rviz_fullscreen` 是本项目的 launch 选项，不是 RViz 自带参数。Humble 已报告强制全屏会崩溃；先使用默认窗口，打开后再手动调整大小。

## RViz 缺件或部件分离

```bash
./scripts/generate_ros_description.py
work/mujoco_env/bin/python scripts/validate_ros_mjcf_pose_parity.py
./scripts/validate_ros2_package.sh
```

然后查看 RobotModel → Links 的第一个资源错误。颈部/腿部脱离通常是修复 ±90° pitch 之前的旧 Xacro；整个 link 消失通常是 mesh URI 或复制资源问题。完整流程见 [RViz 页面](/zh/ros2/rviz)。

## 关节滑块没有效果

确认使用 `use_gui:=true`，再检查：

```bash
ros2 topic echo /joint_states --once
ros2 topic hz /joint_states
ros2 run tf2_ros tf2_echo world ankle_left
```

若 JointState 变化而 TF 不变，检查 `robot_state_publisher` 是否运行且使用同一份 `robot_description`。

## Isaac 提示缺少 ONNX Runtime

```bash
./scripts/setup_isaac_python_env.sh
```

依赖应安装到 `work/isaac_python_pkgs`，供 Isaac 自带的 Python 读取。安装到系统 Python 后仍然可能提示缺失。

## Isaac 出现 `ERROR_DEVICE_LOST`

使用对应教程的 `.sh` 启动脚本，例如 `scripts/run_isaac_policy.sh`。这些入口会选择单一 Vulkan ICD 并关闭多 GPU 渲染。
先检查启动日志中的 ICD 和 GPU；需要更换时设置 `MICRODUCK_VULKAN_ICD` 和 `MICRODUCK_ISAAC_ACTIVE_GPU`，保留系统驱动文件。

## Isaac 长 GUI 任务像是卡住

观察每 5 个仿真秒输出的进度。GUI 慢于真实时间很常见；进度停止且窗口无响应才是故障信号。已记录主机运行 60 个仿真秒约需 3 分钟。

## 完整验证提示缺少环境

`validate_all.sh` 需要固定上游 checkout、MuJoCo 环境和 Isaac 专用 ONNX Runtime。先完成[安装](/zh/guide/installation)。
