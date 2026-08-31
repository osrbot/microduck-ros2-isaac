# 直播演示指南

推荐教学主线是：

```text
固定上游源 -> 可复现转换 -> ROS 描述
             -> Isaac 回放官方策略 -> 与 MuJoCo 诚实对比
```

## 开播前

1. 在 Linux/Isaac 主机运行 `./scripts/validate_all.sh`。
2. 在实际采集的同一桌面会话彩排 RViz 和 Isaac。
3. 打开[验证结果](/zh/reference/results)，作为 GUI 故障时的技术证据。
4. 验证后录制一段短 RViz/Isaac 本地备用视频；使用时明确说明是录像。
5. 确认直播符合[许可边界](./licensing)，特别是赞助或变现直播。

## 推荐 25 分钟结构

| 时间 | 环节 | 核心讲点 |
| ---: | --- | --- |
| 2 分钟 | 项目边界 | 独立项目、固定上游、许可说明 |
| 4 分钟 | 模型契约 | 15 刚体、14 关节、61 观测、14 动作 |
| 5 分钟 | ROS 2 | TF、visual/collision、交互关节 |
| 4 分钟 | USD | 为什么“能打开”不等于结构正确 |
| 6 分钟 | Isaac | 200 Hz 物理、50 Hz 策略、跟随镜头 |
| 4 分钟 | 证据 | smoke parity 通过，轨迹/训练一致未通过 |

## RViz 演示

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

教学时建议逐个移动滑块；**Randomize** 只用于视觉 smoke test，下一环节前点击 **Center**。collision 仅在讲解碰撞时启用。

## Isaac 演示

先站立：

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_stand.onnx \
  --duration 30 --action-scale 1.0 --follow-camera --viz kit
```

再行走：

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_walking.onnx \
  --duration 60 --vx 0.3 --action-scale 0.9 --follow-camera --viz kit
```

已验证主机中 60 个仿真秒约需 3 分钟真实时间。判断依据是每 5 个仿真秒的进度，而不是必须实时运行；若进度停止且窗口无响应，用 Ctrl+C 退出。

可以说：复用了 Pollen 固定版本公开模型和策略；ROS packaging 与 Isaac 回放是社区新增；相同 61→14 契约在两个已记录 smoke 场景保持 finite/upright；执行器和接触尚未达到轨迹或训练一致。

不要说“官方 Isaac 版”“训练完成”“精确物理一致”“硬件可直接用”或“ROS 已经控制机器人”。
