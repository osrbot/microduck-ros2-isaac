# 用 ROS 2 遥控 Isaac 里的鸭子

三个终端，一只鸭。终端 A 跑 Isaac Sim，终端 B 打开 ROS 2 bridge 和 RViz，终端 C 负责发命令。
照着这一页走完，你会亲眼看到同一个动作同时出现在 Isaac 和 RViz 里。

这条路线已经在 Ubuntu 24.04、ROS 2 Jazzy、Isaac Sim 6.0.1 standalone 和 Isaac Lab 3.0.0 beta 2
上完整跑过。下面的图片也是这次实际运行留下的，不是示意图。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>预计时间</span><strong>25–40 分钟</strong></div>
  <div role="listitem"><span>前置环境</span><strong>ROS 2 + Isaac 已分别跑通</strong></div>
  <div role="listitem"><span>终端数量</span><strong>A、B、C 共 3 个</strong></div>
  <div role="listitem"><span>完成结果</span><strong>ROS 指令与 Isaac 状态闭环</strong></div>
</div>

<div class="md-terminal-map" role="list" aria-label="三终端分工">
  <div role="listitem"><strong>终端 A · Isaac</strong><p>运行多动作游乐场，窗口与物理循环一直保留。</p></div>
  <div role="listitem"><strong>终端 B · Bridge</strong><p>运行 ROS bridge、Robot State Publisher 与 RViz。</p></div>
  <div role="listitem"><strong>终端 C · 命令</strong><p>发布速度、绝活、头部和 reset 指令，观察返回 topic。</p></div>
</div>

<div class="md-command-steps">
  <strong>先把三个窗口摆好，再放鸭</strong>
  <p>按 <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd> 打开终端 A，再按两次 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> 得到 B、C。三个窗口都用 <code>cd /你的路径/microduck-ros2-isaac</code> 进入仓库根目录。A、B、C 只是窗口标签，不是三台电脑。</p>
</div>

::: tip 屏幕放不下三个窗口？
用 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>T</kbd> 开三个标签页也可以。建议把标签页重命名为 `A-Isaac`、
`B-Bridge`、`C-Command`，避免把停止命令发错窗口。
:::

## 开始前：把公开策略准备好

如果你还没走过[安装页](/zh/guide/installation)，先运行一次：

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

后面再次玩鸭不用重复下载；`ISAACLAB_DIR` 不是默认路径时，每个新终端都要重新 export。

## 1. 先把 ROS 2 小桥搭好

切到终端 B 运行：

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install \
  --packages-select microduck_description microduck_control_bridge
source install/setup.bash
cd ..
```

正常结束时会看到类似：

```text
Summary: 2 packages finished
```

如果这里还没通过，先别急着叫鸭子上场。构建问题留在终端里最好查，拖到 Isaac 启动以后反而容易
把两件事搅在一起。

## 2. 终端 A：先把鸭子请进 Isaac

```bash
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

第一次启动要加载扩展，等一会儿很正常。看到完整的 MicroDuck、地面和黄色小球，就说明模型、物理和
公开策略都已经进场。这个终端先别关。

<div class="md-result-label">真实运行截图 · 终端 A 启动成功</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="MicroDuck 多动作游乐场在 Isaac Lab 中实际运行的窗口" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>终端 A 跑起来以后应该长这样。</strong>鸭子和球都在场，视口会跟着机器人移动；图片来自本项目的真实 GUI 测试。</figcaption>
</figure>

如果窗口里没有鸭子，先看终端 A 有没有 `Traceback`、资源缺失或 Vulkan 错误。不要继续启动第二个
Isaac 窗口——两只鸭抢同一块显卡，事情通常不会更简单。

## 3. 终端 B：打开 bridge 和 RViz

回到刚才构建成功的终端 B。它应该位于仓库根目录；如果你关掉了它，就按
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> 重开并 `cd` 回仓库：

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
ros2 launch microduck_control_bridge isaac_playground.launch.py
```

你会看到三个节点启动：

```text
robot_state_publisher
microduck_control_bridge
rviz2
```

RViz 会接收 Isaac 发来的 14 个关节位置和 `world → base_link` 位姿。这里显示的是仿真器正在发生的
动作，不是 Joint State Publisher 的手工滑块。

<div class="md-result-label">真实运行截图 · 终端 B 的 bridge 接通后</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-live.webp" alt="RViz 中完整显示由 Isaac 实时驱动的 MicroDuck" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>bridge 接通后，RViz 里应该是一只完整的鸭。</strong>头、颈、身体、两条腿和两只脚都在；左侧的 MicroDuck 和 Ground grid 状态正常。</figcaption>
</figure>

::: warning RViz 里只剩半只鸭？
机器人走远以后，RViz 的 Orbit 相机仍可能盯着原来的世界坐标，看起来就像“零件跑了”。先点
**Focus Camera**，或者发送本页后面的 reset，再拖动视角确认。模型真的缺件时，`MicroDuck` 显示项会报错；
单纯走出镜头不是缺件。
:::

## 4. 终端 C：让它走两步

切到终端 C（还没有就按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> 新开），加载 ROS 环境：

```bash
source /opt/ros/jazzy/setup.bash
source ros2_ws/install/setup.bash
```

下面这条命令以 10 Hz 连续发送 4 秒前进命令。相比只发一帧，它更容易看清完整步态：

```bash
ros2 topic pub -r 10 --times 40 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.30, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

终端会打印 `publisher: beginning loop` 和发布次数，4 秒左右自动回到提示符。此时才执行停车命令。

走完记得停车：

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"
```

<div class="md-result-label">真实运行截图 · 前进与转向命令</div>

<div class="md-runtime-grid">
  <figure class="md-doc-figure">
    <img src="/images/isaac-action-walk.webp" alt="MicroDuck 接收 ROS 2 前进命令后在 Isaac 中迈步" width="1200" height="750" loading="lazy">
    <figcaption><strong>前进。</strong>策略会从 standing 切到 walking；命令停下后再回到 standing。</figcaption>
  </figure>
  <figure class="md-doc-figure">
    <img src="/images/isaac-action-turn.webp" alt="MicroDuck 接收 ROS 2 转向命令后在 Isaac 中转身" width="1200" height="750" loading="lazy">
    <figcaption><strong>转向。</strong>球可能跑到镜头边缘，鸭子还在认真干活。</figcaption>
  </figure>
</div>

想让它原地向左转，发送：

```bash
ros2 topic pub -r 10 --times 35 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.75}}"
```

转完也发送一次上面的零速度命令。这个习惯很朴素，但对仿真和真机都很友好。

## 5. 再点几个小绝活

绝活动作用同一个 topic，只需要换 `data`：

```bash
ros2 topic pub --once /microduck/behavior std_msgs/msg/String \
  "{data: kick_left}"
```

| `data` | 鸭子会做什么 |
| --- | --- |
| `kick_left` | 左脚踢球 |
| `kick_right` | 右脚踢球 |
| `ground_pick` | 低头碰地，再回来 |
| `sitstand` | 坐下；再发一次会起身 |
| `roulade` | 向前滚一圈 |

踢球动作只有约半秒，前滚约一秒。一个动作还没做完时，不要马上塞进另一个绝活；运行器会拒绝硬切，
免得鸭子半个前滚突然决定踢球。

<div class="md-result-label">真实运行截图 · sitstand 命令</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-action-sit.webp" alt="MicroDuck 接收 sitstand 命令后在 Isaac 中降低身体" width="1200" height="750" loading="lazy"></div>
  <figcaption><strong>sitstand 正在执行。</strong>头和身体会明显降低；再发一次同样的命令，它会重新站起来。</figcaption>
</figure>

头部命令按 `neck_pitch, head_pitch, head_yaw, head_roll` 排列。这是我们实际测试过的一组：

```bash
ros2 topic pub --once /microduck/head_command sensor_msgs/msg/JointState \
  "{name: ['neck_pitch', 'head_pitch', 'head_yaw', 'head_roll'], position: [0.15, -0.20, 0.75, 0.18]}"
```

让脑袋回中：

```bash
ros2 topic pub --once /microduck/head_command sensor_msgs/msg/JointState \
  "{name: ['neck_pitch', 'head_pitch', 'head_yaw', 'head_roll'], position: [0.0, 0.0, 0.0, 0.0]}"
```

玩乱了也没关系，一键把机器人和球送回起点：

```bash
ros2 topic pub --once /microduck/reset std_msgs/msg/Empty "{}"
```

## 6. RViz 视角怎么拖

先选左上角的 **Move Camera**：

- 鼠标左键拖动：绕机器人旋转；
- 鼠标滚轮或右键拖动：拉近、拉远；
- 鼠标中键拖动：平移焦点；
- 机器人走出画面：点 **Focus Camera**，或者 reset 后重新聚焦。

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-camera.webp" alt="RViz Orbit 相机经过实际旋转和缩放后的 MicroDuck 近景" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>这张是实际拖动和滚轮缩放后的画面。</strong>左侧 Distance 从 0.38 变成约 0.23，Yaw 和 Pitch 也变化了，所以不是“按钮看起来能点”的假检查。</figcaption>
</figure>

## 7. 看看 ROS 到底收到了什么

先看节点和 topics：

```bash
ros2 node list
ros2 topic list
```

成功时至少能找到：

```text
/microduck_control_bridge
/robot_state_publisher
/rviz
/joint_states
/microduck/policy_state
/microduck/upright
/tf
```

抽一帧关节状态：

```bash
ros2 topic echo --once /joint_states
```

`name` 应该有 14 项，从 `left_hip_yaw` 到 `right_ankle`。再看当前策略：

```bash
ros2 topic echo /microduck/policy_state
```

这条命令会持续等新消息，不会自己结束。观察完站立、行走或绝活切换后，按
<kbd>Ctrl</kbd>+<kbd>C</kbd> 回到提示符。

站稳时会看到类似：

```yaml
data: '{"policy":"standing","upright":true,"tilt_rad":0.0026}'
```

`ground_pick` 主动降低身体时，`upright` 可能短暂变成 `false`，随后恢复。这不等于鸭子一定摔了；如果你
把这个字段拿去做强化学习终止条件，需要把主动低姿态和真正摔倒分开处理。

## 8. 不开窗口，检查完整闭环

想快速确认 ROS → Isaac → ROS 整条链路，而不是手工开三个终端：

```bash
./scripts/validate_ros_isaac_e2e.sh
```

这条自检会自己启动和关闭 headless 进程。等待它回到提示符再看结论；中途按
<kbd>Ctrl</kbd>+<kbd>C</kbd> 只能说明你中断了测试，不能算通过。

脚本会启动真实的 headless Isaac 游乐场，从 ROS 2 发送 `kick_left`，再等 JointState、策略状态、upright
和 TF 回来。通过时应满足：

- 收到持续更新的 14 关节 JointState；
- 收到 `world → base_link`；
- 策略记录里真的出现 `kick_left`，不是只把命令发进空气；
- JSON 报告写入 `artifacts/isaac/`。

::: details 这次实测的参考数字
本次完整闭环收到 317 帧 JointState 和 316 帧策略状态，并记录到
`standing → kick_left → walking`。消息数量会随机器速度和运行时间变化，不必追求一模一样。
:::

## 9. 玩完怎么正常关门

推荐按 C、B、A 的顺序收尾：

1. 终端 C 先发送零速度或 reset；
2. 终端 B 按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 关闭 bridge 和 RViz；
3. 终端 A 按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 关闭 Isaac。

bridge 正常退出时会显示 `process has finished cleanly`，不应该留下
`ExternalShutdownException` traceback。端口占用报错时，也先确认是不是上一只鸭还没退场。

<div class="md-page-complete">
  <strong>三终端闭环完成。</strong>
  <p>你已经看到 ROS 命令进入 Isaac、14 关节与位姿回到 RViz，并学会正常关闭三个进程。下一步可以继续做交互演示，也可以把控制对象换成自己的训练策略。</p>
</div>

<div class="md-next-grid">
  <a class="md-next-card" href="/microduck-ros2-isaac/zh/isaac/playground"><span>继续互动</span><strong>回到多动作游乐场 →</strong><p>用键盘切动作，适合直播与录屏。</p></a>
  <a class="md-next-card" href="/microduck-ros2-isaac/zh/isaac/training"><span>继续开发</span><strong>训练自己的平地策略 →</strong><p>跑通 smoke、曲线、checkpoint 和回放闭环。</p></a>
</div>
