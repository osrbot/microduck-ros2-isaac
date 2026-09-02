# ROS 2 例程：没有真机，也能把鸭玩明白

买不到真机没关系，这一页只走仿真路线。你可以先在 RViz 看懂关节和 TF，再让 ROS 2 去指挥
Isaac 里的策略。两条路线都能直接运行，不需要自己拼一长串 topic 命令。

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
    <li>最后把方向盘交给键盘，并用 topic 验证 ROS 数据。</li>
  </ul>
</div>

## 先选一只玩法

| 想做什么 | 运行什么 | 需要 Isaac Sim 吗 |
| --- | --- | --- |
| 看完整模型，自己拖 14 个关节 | `view_microduck.launch.py use_gui:=true` | 不需要 |
| 看鸭子自动点头、摆头、原地踏步 | `rviz_motion_demo.launch.py` | 不需要 |
| 自动走路、转身、踢球、捡球、坐下再起身 | `isaac_showcase.launch.py` | 需要 |
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

## 例程一：只开 RViz，让鸭子自己扭起来

```bash
ros2 launch microduck_examples rviz_motion_demo.launch.py
```

默认的 `showcase` 会让 MicroDuck 看左、看右、点头、交替抬腿，最后再鞠个躬。它会循环播放，适合
第一次检查模型是不是完整、14 个关节是不是都接对了。

<div class="md-result-label">真实运行截图 · RViz-only 例程</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros2-rviz-motion-demo.webp" alt="MicroDuck ROS 2 自动关节例程在 RViz 中交替抬腿" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>这是例程实际跑出来的一帧。</strong>右腿抬起、左脚支撑，RobotModel 和 TF 都正常；它不是摆拍的默认站姿。</figcaption>
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

::: warning 这只是“关节动画”
这个例程发布 `JointState` 给 RViz，方便认识模型、关节和 TF。它没有重力、接触、控制器和策略，
所以不能拿来判断鸭子在真实物理里能不能站稳。要看动力学和强化学习策略，请继续下一个例程。
:::

<div class="md-checkpoint">
  <strong>RViz-only 例程过关</strong>
  <p>动作会循环播放，头部和双腿按顺序运动，终端没有超出 URDF 限位或关节名错误。到这里完全不需要 Isaac。</p>
</div>

## 例程二：ROS 2 自动指挥 Isaac 表演一轮

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

程序会先等 Isaac 的真实 telemetry 接通，然后自动执行：

```text
reset → 摆头打招呼 → 前进 → 左转 → 左踢 → 右踢
      → 低头捡球 → 坐下 → 起身 → reset
```

RViz 会同时显示 Isaac 返回的 14 个关节和 `world → base_link` 位姿。终端里还会打印当前步骤、策略
切换和 upright 状态，所以不是把命令发出去就假装成功。

<div class="md-result-label">真实运行截图 · ROS → Isaac → RViz 接通后</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-live.webp" alt="ROS 2 接收 Isaac telemetry 后在 RViz 中显示完整 MicroDuck" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>一边看 Isaac，一边看 RViz。</strong>两边是同一轮仿真的实时状态，不是两只各玩各的鸭。</figcaption>
</figure>

不想一次全演完，可以在终端 B 按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 停止，然后从下面 **任选一条** 短节目：

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

<div class="md-checkpoint">
  <strong>ROS → Isaac → RViz 闭环过关</strong>
  <p>终端打印步骤切换；Isaac 里的鸭执行动作；RViz 同时更新姿态。三件事缺一件，都先不要称为闭环成功。</p>
</div>

## 例程三：方向盘交给你

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
| `G` | 低头捡球 |
| `K / M` | 左踢 / 右踢 |
| `R` | 前滚 |
| `X` | 停车 |
| `0` | reset |

## 看看 ROS 2 到底传了什么

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
会持续显示 `world → base_link` 的平移和旋转。不是让三个命令同时挤在一个终端里。

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
