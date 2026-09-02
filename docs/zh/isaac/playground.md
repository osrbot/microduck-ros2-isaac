# 打开 MicroDuck 多动作游乐场

单独回放行走策略只是热身。游乐场会一次加载公开的整套 61→14 ONNX 策略，让同一只鸭子按指令在
站立、行走和几个小绝活之间切换，还会在踢球前把一颗 70 mm、15 g 的球摆到脚边。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>预计时间</span><strong>15–25 分钟</strong></div>
  <div role="listitem"><span>控制方式</span><strong>键盘或 ROS 2</strong></div>
  <div role="listitem"><span>动作数量</span><strong>走路 + 5 类绝活</strong></div>
  <div role="listitem"><span>完成结果</span><strong>可互动、可自检、可演示</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>建议先 GUI 后 headless</strong>
  <ul>
    <li>确认公开策略逐个加载；</li>
    <li>用键盘走路、转向并触发至少两个绝活；</li>
    <li>reset 回到起点；</li>
    <li>最后用 5 秒 headless 命令检查脚本可重复启动。</li>
  </ul>
</div>

<div class="md-command-steps">
  <strong>开一个终端 A 就够了</strong>
  <p>按 <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd>，<code>cd</code> 到仓库根目录。GUI 游乐场运行时不要在同一个终端继续粘贴 headless 命令；玩完先按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 收掉 GUI。</p>
</div>

## 1. 准备公开策略

如果前面还没做过，在仓库根目录运行：

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

只需成功准备一次。启动时终端会逐项打印 `Loaded` 或 `Skipped`；需要的策略若全部 `Skipped`，先回到
这一步检查下载，不要对着空游乐场按键。

## 2. 开门，放鸭

```bash
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

命令启动后提示符不会返回。终端依次打印策略的 `Loaded` / `Skipped`，随后打开 Isaac 窗口；第一次加载
Kit 扩展会慢一些，不要连续按 <kbd>Enter</kbd> 或重复启动。

<div class="md-result-label">真实运行截图 · 游乐场打开后</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="MicroDuck 多动作游乐场在 Isaac Lab 中实际运行" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>看到鸭子和黄色小球，就算开门成功。</strong>这是实际运行窗口；初次加载扩展会慢一点，别在它热身时连续开好几个 Isaac。</figcaption>
</figure>

窗口打开后，先用鼠标点一下 **Isaac 视口**，让键盘焦点进入画面；如果焦点还在终端或侧边栏，按键不会
送给鸭子。方向键和 <kbd>Z</kbd>/<kbd>X</kbd> 控制前后、转向与横移。松开后速度归零，运行器会从
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

<div class="md-checkpoint">
  <strong>互动这一关通过</strong>
  <p>速度键松开后能停回 standing；至少两个绝活动作能完整执行；<kbd>Backspace</kbd> 能把机器人和球送回起点。动作忙时拒绝硬切属于保护，不是按键失灵。</p>
</div>

<div class="md-result-label">真实动作截图 · 走鸭、转鸭、坐鸭</div>

<div class="md-runtime-grid md-runtime-grid-three">
  <figure class="md-doc-figure">
    <img src="/images/isaac-action-walk.webp" alt="MicroDuck 在 Isaac 多动作游乐场中向前走" width="1200" height="750" loading="lazy">
    <figcaption><strong>走鸭。</strong>方向键给出速度后，策略从 standing 切到 walking。</figcaption>
  </figure>
  <figure class="md-doc-figure">
    <img src="/images/isaac-action-turn.webp" alt="MicroDuck 在 Isaac 多动作游乐场中转向" width="1200" height="750" loading="lazy">
    <figcaption><strong>转鸭。</strong>按左右方向键时，跟随镜头会陪它一起转。</figcaption>
  </figure>
  <figure class="md-doc-figure">
    <img src="/images/isaac-action-sit.webp" alt="MicroDuck 在 Isaac 多动作游乐场中执行坐下动作" width="1200" height="750" loading="lazy">
    <figcaption><strong>坐鸭。</strong>按 <kbd>Y</kbd> 后身体降低；动作结束再按一次会站起。</figcaption>
  </figure>
</div>

## 3. 先跑一次无界面自检

先回到终端 A 按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 关闭 GUI，等提示符重新出现。直播前可以再确认模型、策略和
物理循环都能无界面启动：

```bash
./scripts/run_isaac_playground.sh \
  --duration 5 \
  --no-keyboard \
  --headless
```

结果会写入 `artifacts/isaac/playground_session.json`。这是运行记录，不是“动作训练成功”的证明。

```bash
test -s artifacts/isaac/playground_session.json \
  && echo "Playground report: OK"
```

看到 `Playground report: OK` 才说明 5 秒自检留下了非空报告。

## 这里到底用了什么策略？

这些动作来自 Pollen Robotics 发布的 MicroDuck 策略，原本由
[microduck_rl](https://github.com/pollen-robotics/microduck_rl) 在 MuJoCo/mjlab 中训练。本页做的是把它们放进
Isaac Sim 交互回放，并没有把上游训练过程偷换成 Isaac 训练。

<div class="md-page-complete">
  <strong>这下真的玩起来了。</strong>
  <p>你会切动作、重置鸭子和小球，也跑过无界面检查。下一页把键盘换成 ROS 2 命令。</p>
</div>
