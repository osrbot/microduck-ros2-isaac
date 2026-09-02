# 从这里开始：今天怎么遛鸭？

不用从头读到尾，也不用先装齐 ROS 2、Isaac Sim 和一大筐工具。先选今天想看到的结果，走完一条，
再决定要不要继续加戏。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>阅读时间</span><strong>3 分钟</strong></div>
  <div role="listitem"><span>适合谁</span><strong>第一次打开仓库的人</strong></div>
  <div role="listitem"><span>需要终端</span><strong>先不用</strong></div>
  <div role="listitem"><span>读完得到</span><strong>一条明确的起跑路线</strong></div>
</div>

## 三条路线，挑一条开玩

<div class="md-route-grid">
  <a class="md-route-card md-route-orange" href="/microduck-ros2-isaac/zh/ros2/">
    <span>路线 1 · 10–15 分钟 · 最推荐</span>
    <strong>先玩 ROS 2</strong>
    <p>在 RViz 里看到完整模型，用滑块活动 14 个关节，再跑点头、踏步和鞠躬例程。不需要 Isaac Sim。</p>
  </a>
  <a class="md-route-card md-route-aqua" href="/microduck-ros2-isaac/zh/isaac/">
    <span>路线 2 · 20–30 分钟</span>
    <strong>再去 Isaac Sim</strong>
    <p>打开仓库自带 USD，回放行走策略，再进多动作游乐场切换坐起、踢球、捡球和前滚。</p>
  </a>
  <a class="md-route-card md-route-pink" href="/microduck-ros2-isaac/zh/ros2/isaac-control">
    <span>路线 3 · 25–40 分钟</span>
    <strong>让 ROS 2 指挥 Isaac</strong>
    <p>三个终端完成 ROS 命令、Isaac 动作和 RViz 状态回传的闭环，适合演示、录屏和继续开发。</p>
  </a>
</div>

## 不知道选哪个？照这个顺序

1. **先走 ROS 2 路线。** 安装轻、反馈快，先确认模型、网格、关节和 TF 都正常。
2. **再走 Isaac 单策略路线。** 确认显卡、Vulkan、Isaac Sim 和公开策略能一起跑。
3. **然后进多动作游乐场。** 用键盘切动作，先把现成能力玩明白。
4. **最后再训练。** 先做 5 轮 smoke，确认任务、PPO 和 checkpoint 流水线，再开正式实验。

这样每一步都有清楚的成功画面。某一步出错时，也知道问题停在哪一层，不会把 ROS、渲染、策略和训练
搅成一锅鸭汤。

## 开始前只确认这几件事

| 你想走的路线 | 最低准备 | 不需要先做什么 |
| --- | --- | --- |
| ROS 2 / RViz | Ubuntu 24.04、ROS 2 Jazzy | 不需要 NVIDIA 显卡，不需要 Isaac |
| Isaac 查看模型 | Linux、Isaac Sim | 不需要重新转换 USD |
| 策略游乐场 | Isaac Sim、Isaac Lab、NVIDIA GPU | 不需要先训练策略 |
| 原生训练 | Isaac Sim、Isaac Lab、足够显存 | 不需要真机，不承诺直接 sim2real |

::: tip 真机暂时不在这条路线里
当前教程以仿真、教学和开源演示为主。ROS 2 例程不等于真机驱动，Isaac checkpoint 也不等于可以直接
下发到实体机器人。我们会把每一层证据写清楚，不让鸭子替我们吹牛。
:::

<div class="md-page-complete">
  <strong>路线选好了，就别继续在目录口徘徊。</strong>
  <p>下一页先把仓库和对应环境准备好；从“怎么打开终端、怎么粘贴、怎么新开窗口”开始，再分别给 ROS 2 与 Isaac 的命令、检查方法和成功标志。</p>
</div>

<div class="md-next-grid">
  <a class="md-next-card" href="/microduck-ros2-isaac/zh/guide/installation"><span>所有路线的下一站</span><strong>安装与环境检查 →</strong><p>先学终端快捷键，再克隆仓库并检查 ROS 2 或 Isaac Lab。</p></a>
  <a class="md-next-card" href="/microduck-ros2-isaac/zh/ros2/"><span>环境已经准备好</span><strong>直接把鸭子请进 RViz →</strong><p>构建 description 包，打开模型，再拖动关节。</p></a>
</div>
