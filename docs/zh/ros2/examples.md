# 运行 ROS 2 动作和遥控例程

本页提供三个例程：RViz 关节动画、ROS 2 控制 Isaac 自动执行动作，以及键盘遥控。
先运行只需要 ROS 2 的例程；安装好 Isaac 后再做后两项。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>RViz 例程</span><strong>约 5 分钟</strong></div>
  <div role="listitem"><span>Isaac 联动</span><strong>约 15–25 分钟</strong></div>
  <div role="listitem"><span>真机要求</span><strong>不需要</strong></div>
  <div role="listitem"><span>完成结果</span><strong>自动动作、遥控与状态观察</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>建议按这个顺序玩</strong>
  <ul>
    <li>先跑 RViz-only 例程，确认模型、14 关节和 TF；</li>
    <li>有 Isaac 环境再跑自动 showcase；</li>
    <li>最后用键盘遥控，并查看 ROS 话题中的状态数据。</li>
  </ul>
</div>

## 选择例程

| 想做什么 | 运行什么 | 需要 Isaac Sim 吗 |
| --- | --- | --- |
| 看完整模型，自己拖 14 个关节 | `view_microduck.launch.py use_gui:=true` | 不需要 |
| 看鸭子自动点头、摆头、原地踏步 | `rviz_motion_demo.launch.py` | 不需要 |
| 自动走路、转身、踢球、低头碰地、坐下再起身 | `isaac_showcase.launch.py` | 需要 |
| 自己用键盘遥控 | `microduck_teleop` | 需要 |

<div class="md-command-steps">
  <strong>从终端 A 开始</strong>
  <p>按 <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd> 打开终端，<code>cd</code> 到仓库根目录。每次只运行一个 launch；想换节目时，先在当前终端按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 停掉上一个。</p>
</div>

先构建三个 ROS 2 包：

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install \
  --packages-select microduck_description microduck_control_bridge microduck_examples
source install/setup.bash
cd ..
```

成功时末尾应是 `Summary: 3 packages finished`。如果有失败包，先留在这个终端修好，不要继续启动例程。

<div class="md-checkpoint">
  <strong>三个例程包都能被 ROS 找到</strong>
  <p>构建没有失败，并且执行 <code>ros2 pkg prefix microduck_examples</code> 能返回当前 workspace 下的安装路径。</p>
</div>

## 例程一：在 RViz 中播放关节动画

```bash
ros2 launch microduck_examples rviz_motion_demo.launch.py
```

默认的 `showcase` 会让 MicroDuck 看左、看右、点头、交替抬腿，最后再鞠个躬。它会循环播放，适合
第一次检查模型是不是完整、14 个关节是不是都接对了。

<div class="md-result-label">真实运行截图 · RViz-only 例程</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros2-rviz-motion-demo.webp" alt="MicroDuck ROS 2 自动关节例程在 RViz 中交替抬腿" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>抬腿动作示例。</strong>右腿抬起，RobotModel 和 TF 显示正常。</figcaption>
</figure>

想换节目时，先在终端按 <kbd>Ctrl</kbd>+<kbd>C</kbd>，等上一个例程退出，再从下面 **任选一条** 运行。
不要把三条 launch 一次性全部粘贴：第一条没退出时，后两条不会开始。

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

::: info RViz 中的动作
这个例程通过 `JointState` 展示关节运动和 TF。重力、接触和强化学习策略在后面的 Isaac 例程中运行。
:::

<div class="md-checkpoint">
  <strong>RViz-only 例程过关</strong>
  <p>动作会循环播放，头部和双腿按顺序运动，终端没有超出 URDF 限位或关节名错误。到这里完全不需要 Isaac。</p>
</div>

## 例程二：通过 ROS 2 控制 Isaac 动作

先完成[多动作游乐场](../isaac/playground)的环境与策略准备，再回到这里执行。

如果 RViz-only 例程还在运行，先按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 关掉。终端 A 回到仓库根目录后启动
Isaac 游乐场：

```bash
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

看到鸭子和黄色小球以后，保持终端 A 不动。按
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> 新开终端 B，`cd` 到仓库根目录后运行：

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 launch microduck_examples isaac_showcase.launch.py
```

程序收到 Isaac 返回的状态后，会自动执行：

```text
reset → 摆头打招呼 → 前进 → 左转 → 左踢 → 右踢
      → 低头碰地 → 坐下 → 起身 → reset
```

RViz 会同时显示 Isaac 返回的 14 个关节和 `world → base_link` 位姿。终端里还会打印当前步骤、策略
切换和 upright 状态，便于确认当前执行到哪一步。

<div class="md-result-label">真实运行截图 · ROS → Isaac → RViz 接通后</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-live.webp" alt="ROS 2 接收 Isaac telemetry 后在 RViz 中显示完整 MicroDuck" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>一边看 Isaac，一边看 RViz。</strong>RViz 显示 Isaac 返回的关节位置和机身位姿。</figcaption>
</figure>

不想一次全演完，可以在终端 B 按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 停止，然后从下面 **任选一条** 短节目：

```bash
# 只走路、转弯和横移
ros2 launch microduck_examples isaac_showcase.launch.py sequence:=walk

# 只玩摆头、踢球、碰地、坐起和前滚
ros2 launch microduck_examples isaac_showcase.launch.py sequence:=skills

# 用 0.5 倍速慢慢看一轮完整节目
ros2 launch microduck_examples isaac_showcase.launch.py \
  sequence:=showcase speed:=0.5
```

`speed` 可以在 `0.0～1.0` 之间减慢节目。它不能超过 `1.0`，因为踢球、碰地和坐起策略有固定的
真实执行时间，硬加速只会让下一个命令来得太早。如果 30 秒内收不到 Isaac telemetry，例程会报错
退出；此时检查 Isaac 是否仍在运行。

<div class="md-checkpoint">
  <strong>ROS 控制和状态接收正常</strong>
  <p>终端打印步骤切换；Isaac 里的鸭执行动作；RViz 同时更新姿态。缺少其中一项时，检查对应终端的报错。</p>
</div>

## 例程三：用键盘遥控

Isaac 和 bridge 已经启动时，再按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> 打开终端 C：

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
| `G` | 低头碰地 |
| `K / M` | 左踢 / 右踢 |
| `R` | 前滚 |
| `X` | 停车 |
| `0` | reset |

## 查看和录制 ROS 2 消息

自动节目或键盘遥控运行时，可以再开一个终端观察。下面三条都是持续输出命令，**一次选一条**；看够后按
<kbd>Ctrl</kbd>+<kbd>C</kbd> 停止，再换下一条：

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash

ros2 topic hz /joint_states
ros2 topic echo /microduck/policy_state
ros2 run tf2_ros tf2_echo world base_link
```

正常时，`topic hz` 会持续打印频率，`policy_state` 会出现 `standing`、`walking` 或绝活名称，`tf2_echo`
会持续显示 `world → base_link` 的平移和旋转。

想把这一轮保存下来复盘：

```bash
mkdir -p work/rosbags
ros2 bag record -o work/rosbags/microduck_showcase \
  /cmd_vel /microduck/behavior /microduck/head_command \
  /joint_states /microduck/policy_state /microduck/upright /tf /tf_static
```

录够以后按 <kbd>Ctrl</kbd>+<kbd>C</kbd>。看到 `closing` / `split` 一类收尾日志并回到提示符，再检查
`work/rosbags/microduck_showcase/` 目录；直接关终端可能让录制来不及正常收尾。

<div class="md-page-complete">
  <strong>ROS 2 的几个动作都玩过了。</strong>
  <p>你已经会运行、键盘控制和录包。下一页把仓库自带的 MicroDuck USD 放进 Isaac Sim。</p>
</div>
