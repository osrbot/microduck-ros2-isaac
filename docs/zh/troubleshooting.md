# 故障排查

## RViz 相机不能移动

使用仓库当前 RViz 配置。选择 **Move Camera**（或按 `M`），在空白 3D 区域左键拖动，滚轮缩放。若工具栏或 Views 不存在，可能是旧安装覆盖了当前 workspace：

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 pkg prefix microduck_description
```

输出应指向当前 workspace 的 `install/`。

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

运行 `./scripts/setup_isaac_python_env.sh`。依赖必须位于 `work/isaac_python_pkgs`；安装进无关系统 Python 不能满足 Isaac 自带解释器。

## Isaac 出现 `ERROR_DEVICE_LOST`

始终通过 `scripts/run_isaac_policy.sh` 启动。脚本隔离单一 Vulkan ICD 并关闭多 GPU 渲染。新主机应显式设置 `MICRODUCK_VULKAN_ICD` 和 `MICRODUCK_ISAAC_ACTIVE_GPU`，不要删除驱动 manifest。

## Isaac 长 GUI 任务像是卡住

观察每 5 个仿真秒输出的进度。GUI 慢于真实时间很常见；进度停止且窗口无响应才是故障信号。已记录主机运行 60 个仿真秒约需 3 分钟。

## 完整验证提示缺少环境

`validate_all.sh` 需要固定上游 checkout、MuJoCo 环境和 Isaac 专用 ONNX Runtime。先完成[安装](/zh/guide/installation)。
