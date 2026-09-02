# 打开 MicroDuck 多动作游乐场

单独回放行走策略只是热身。游乐场会一次加载公开的整套 61→14 ONNX 策略，让同一只鸭子按指令在
站立、行走和几个小绝活之间切换，还会在踢球前把一颗 70 mm、15 g 的球摆到脚边。

## 1. 准备公开策略

如果前面还没做过，在仓库根目录运行：

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

## 2. 开门，放鸭

```bash
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="MicroDuck 多动作游乐场在 Isaac Lab 中实际运行" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>看到鸭子和黄色小球，就算开门成功。</strong>这是实际运行窗口；初次加载扩展会慢一点，别在它热身时连续开好几个 Isaac。</figcaption>
</figure>

窗口打开后，方向键和 <kbd>Z</kbd>/<kbd>X</kbd> 控制前后、转向与横移。松开后速度归零，运行器会从
walking 自动切回 standing。

| 按键 | 鸭子会做什么 |
| --- | --- |
| <kbd>Y</kbd> | 坐下 / 起身 |
| <kbd>G</kbd> | 低头碰地，再回到站立 |
| <kbd>K</kbd> / <kbd>M</kbd> | 左脚 / 右脚踢球 |
| <kbd>R</kbd> | 向前滚一圈 |
| <kbd>W</kbd>/<kbd>S</kbd> | 调 neck pitch |
| <kbd>A</kbd>/<kbd>D</kbd> | 调 head pitch |
| <kbd>Q</kbd>/<kbd>E</kbd> | 调 head yaw |
| <kbd>C</kbd>/<kbd>V</kbd> | 调 head roll |
| <kbd>H</kbd> | 头部命令回中 |
| <kbd>Backspace</kbd> | 机器人和球回到初始位置 |

某个动作的 ONNX 文件不存在时，启动日志会明确写出 `Skipped`，其他可用动作仍能玩。动作正在执行时
再次按别的绝活键不会硬切策略，避免鸭子在半个前滚里突然想踢球。

游乐场默认跟随锁定版 MicroDuck 运行时的控制手感：walking 的 action scale 是 `0.9`，其他策略是
`1.0`；头部和腿部分别用 `0.5` / `0.7` 的低通系数。它们都能用命令行覆盖，但直播前别随手拧，
不然鸭子很容易从“活泼”变成“抽象”。

## 3. 先跑一次无界面自检

直播前可以先确认模型、策略和物理循环都能启动：

```bash
./scripts/run_isaac_playground.sh \
  --duration 5 \
  --no-keyboard \
  --headless
```

结果会写入 `artifacts/isaac/playground_session.json`。这是运行记录，不是“动作训练成功”的证明。

## 这里到底用了什么策略？

这些动作来自 Pollen Robotics 发布的 MicroDuck 策略，原本由
[microduck_rl](https://github.com/pollen-robotics/microduck_rl) 在 MuJoCo/mjlab 中训练。本页做的是把它们放进
Isaac Sim 交互回放，并没有把上游训练过程偷换成 Isaac 训练。

想让 ROS 2 发命令、RViz 同步显示当前姿态，继续去
[用 ROS 2 遥控 Isaac 里的鸭子](/zh/ros2/isaac-control)。那里按三个终端拆好了完整命令、预期画面、
RViz 视角操作和一键闭环测试。想自己训练一只新的，去
[训练一只会走的鸭](./training)。
