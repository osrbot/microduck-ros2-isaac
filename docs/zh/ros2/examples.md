# ROS 2 例程：没有真机，也能把鸭玩明白

买不到真机没关系，这一页只走仿真路线。你可以先在 RViz 看懂关节和 TF，再让 ROS 2 去指挥
Isaac 里的策略。两条路线都能直接运行，不需要自己拼一长串 topic 命令。

## 先选一只玩法

| 想做什么 | 运行什么 | 需要 Isaac Sim 吗 |
| --- | --- | --- |
| 看完整模型，自己拖 14 个关节 | `view_microduck.launch.py use_gui:=true` | 不需要 |
| 看鸭子自动点头、摆头、原地踏步 | `rviz_motion_demo.launch.py` | 不需要 |
| 自动走路、转身、踢球、捡球、坐下再起身 | `isaac_showcase.launch.py` | 需要 |
| 自己用键盘遥控 | `microduck_teleop` | 需要 |

先构建三个 ROS 2 包：

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install \
  --packages-select microduck_description microduck_control_bridge microduck_examples
source install/setup.bash
cd ..
```

## 例程一：只开 RViz，让鸭子自己扭起来

```bash
ros2 launch microduck_examples rviz_motion_demo.launch.py
```

默认的 `showcase` 会让 MicroDuck 看左、看右、点头、交替抬腿，最后再鞠个躬。它会循环播放，适合
第一次检查模型是不是完整、14 个关节是不是都接对了。

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros2-rviz-motion-demo.webp" alt="MicroDuck ROS 2 自动关节例程在 RViz 中交替抬腿" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>这是例程实际跑出来的一帧。</strong>右腿抬起、左脚支撑，RobotModel 和 TF 都正常；它不是摆拍的默认站姿。</figcaption>
</figure>

想换节目：

```bash
# 只摇头点头，来打个招呼
ros2 launch microduck_examples rviz_motion_demo.launch.py routine:=hello

# 只做原地踏步示意，播放速度提高到 1.5 倍
ros2 launch microduck_examples rviz_motion_demo.launch.py \
  routine:=walk speed:=1.5

# 只播一遍，然后回到默认站姿
ros2 launch microduck_examples rviz_motion_demo.launch.py repeat:=false
```

可用节目只有三个：`hello`、`walk`、`showcase`。示例里的每个姿态都检查过 URDF 关节限位。

::: warning 这只是“关节动画”
这个例程发布 `JointState` 给 RViz，方便认识模型、关节和 TF。它没有重力、接触、控制器和策略，
所以不能拿来判断鸭子在真实物理里能不能站稳。要看动力学和强化学习策略，请继续下一个例程。
:::

## 例程二：ROS 2 自动指挥 Isaac 表演一轮

终端 A 先启动 Isaac 游乐场：

```bash
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

看到鸭子和黄色小球以后，终端 B 运行：

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 launch microduck_examples isaac_showcase.launch.py
```

程序会先等 Isaac 的真实 telemetry 接通，然后自动执行：

```text
reset → 摆头打招呼 → 前进 → 左转 → 左踢 → 右踢
      → 低头捡球 → 坐下 → 起身 → reset
```

RViz 会同时显示 Isaac 返回的 14 个关节和 `world → base_link` 位姿。终端里还会打印当前步骤、策略
切换和 upright 状态，所以不是把命令发出去就假装成功。

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-live.webp" alt="ROS 2 接收 Isaac telemetry 后在 RViz 中显示完整 MicroDuck" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>一边看 Isaac，一边看 RViz。</strong>两边是同一轮仿真的实时状态，不是两只各玩各的鸭。</figcaption>
</figure>

不想一次全演完，可以换短节目：

```bash
# 只走路、转弯和横移
ros2 launch microduck_examples isaac_showcase.launch.py sequence:=walk

# 只玩摆头、踢球、捡球、坐起和前滚
ros2 launch microduck_examples isaac_showcase.launch.py sequence:=skills

# 用 0.5 倍速慢慢看一轮完整节目
ros2 launch microduck_examples isaac_showcase.launch.py \
  sequence:=showcase speed:=0.5
```

`speed` 可以在 `0.0～1.0` 之间减慢节目。它不能超过 `1.0`，因为踢球、捡球和坐起策略有固定的
真实执行时间，硬加速只会让下一个命令来得太早。如果 30 秒内收不到 Isaac telemetry，例程会报错
退出，不会对着空气演完一整套。

## 例程三：方向盘交给你

Isaac 和 bridge 已经启动时，新开一个终端：

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 run microduck_control_bridge microduck_teleop
```

常用按键：

| 按键 | 动作 |
| --- | --- |
| `W / S` | 前进 / 后退 |
| `A / D` | 左转 / 右转 |
| `Q / E` | 左移 / 右移 |
| `Y` | 坐下 / 起身 |
| `G` | 低头捡球 |
| `K / M` | 左踢 / 右踢 |
| `R` | 前滚 |
| `X` | 停车 |
| `0` | reset |

## 看看 ROS 2 到底传了什么

自动节目或键盘遥控运行时，可以再开一个终端观察：

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash

ros2 topic hz /joint_states
ros2 topic echo /microduck/policy_state
ros2 run tf2_ros tf2_echo world base_link
```

想把这一轮保存下来复盘：

```bash
mkdir -p work/rosbags
ros2 bag record -o work/rosbags/microduck_showcase \
  /cmd_vel /microduck/behavior /microduck/head_command \
  /joint_states /microduck/policy_state /microduck/upright /tf /tf_static
```

这几条例程跑顺以后，再去[用 ROS 2 遥控 Isaac](/zh/ros2/isaac-control)看每个 topic 的手动命令，
或者直接去[训练一只会走的鸭](/zh/isaac/training)改奖励和训练参数。
