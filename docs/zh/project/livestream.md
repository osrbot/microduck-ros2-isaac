# 直播演示指南

按“先看动作 → 自己控制 → 查看数据 → 开始训练”的顺序演示。下面安排约 25 分钟；
训练启动较慢时，可以一边看日志一边解释参数，再回放提前准备好的模型。

## 开播前准备

1. 完成安装、RViz 和 Isaac 的对应章节，并在录屏使用的同一桌面上各运行一次。
2. 提前下载模型，准备一个已回放过的训练检查点。
3. 把终端放在左侧，RViz 或 Isaac 放在右侧；窗口文字保持可读，桌面目录不要进入录屏范围。
4. 按下表彩排，记录启动等待时间。模型和素材的使用条件见[许可说明](./licensing)。

## 25 分钟演示安排

| 时间 | 操作 | 讲解重点 |
| --- | --- | --- |
| 0–2 分钟 | 播放一段行走或[连续翻滚视频](../isaac/continuous-roll) | 介绍本次要学会的操作 |
| 2–7 分钟 | 打开 RViz，转动视角并移动关节 | 模型、关节和 TF 怎样对应 |
| 7–12 分钟 | 在 Isaac 中运行站立、行走，再试键盘动作 | 速度命令怎样影响动作 |
| 12–17 分钟 | [从 ROS 2 发送命令](../ros2/isaac-control)，在 RViz 看状态 | 命令发到哪里，状态怎样回来 |
| 17–22 分钟 | [启动短训练](../isaac/training)，展示保存的模型并回放 | 奖励、训练更新、模型保存和加载 |
| 22–25 分钟 | 回顾步骤，说明下一次怎样改参数 | 引导观众按教程复现 |

## RViz：先看模型，再动关节

在项目根目录新开终端，执行：

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

Humble 用户将 `jazzy` 换成 `humble`，保持默认窗口启动。先旋转和缩放视角，再逐个拖动关节滑块；
讲完后点 **Center** 回到默认姿态。碰撞几何只在讲到对应部分时显示。

## Isaac：站立、行走和键盘控制

在项目根目录另开终端。先运行站立策略：

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/policies/v7/alpha_stand.onnx \
  --duration 30 --action-scale 1.0 --follow-camera --viz kit
```

等程序结束后再运行行走策略：

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/policies/v7/alpha_walking.onnx \
  --duration 60 --vx 0.3 --action-scale 0.9 --follow-camera --viz kit
```

指着动作解释 `vx=0.3` 是前进速度命令，再打开[多动作游乐场](../isaac/playground)演示转向、踢球、碰地和坐起。
每完成一个动作，留几秒让观众看清结果，再切到下一个。

仿真速度会受显卡和窗口影响。在记录的测试主机上，60 秒仿真约需 3 分钟；排练时按自己的机器调整节奏。
若进度输出停止且窗口无响应，按 `Ctrl+C` 退出，按[故障排查](../troubleshooting)处理。

## 训练环节：先解释，再操作

按[第 10 章](../isaac/training)运行 5 次更新，指出日志中的训练阶段、保存路径和配置文件。
随后加载准备好的检查点，让观众看到“修改参数 → 训练 → 保存 → 回放”的完整流程。
讲连续翻滚时，可用[三轮调参记录](../isaac/roll-debugging)解释每次看到了什么问题、改了什么、结果如何。

把下载、软件安装和重复加载放在开播前完成。演示中每个环节都围绕一个操作和一个可见结果展开。
