# 从这里开始：先选一条路线

第一次来，就按页面顺序走。我们先看电脑能不能跑，再从比较轻的 ROS 2 开始，最后把鸭子放进
Isaac Sim。按你选择的路线安装所需软件即可。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>阅读时间</span><strong>3 分钟</strong></div>
  <div role="listitem"><span>适合谁</span><strong>第一次打开仓库的人</strong></div>
  <div role="listitem"><span>需要终端</span><strong>先不用</strong></div>
  <div role="listitem"><span>下一步</span><strong>检查你的电脑</strong></div>
</div>

## 先看电脑能跑哪条路线

| 路线 | 需要准备 | 暂时不需要 |
| --- | --- | --- |
| ROS 2 和 RViz | Ubuntu 24.04、ROS 2 Jazzy | NVIDIA 显卡、Isaac Sim |
| Isaac Sim | Ubuntu 24.04、NVIDIA 显卡、Isaac Sim | 真机 |
| Isaac Lab 策略和训练 | Isaac Sim、Isaac Lab | 实体 MicroDuck、sim2real 配方 |

完整测试过的 Isaac 组合是 **Isaac Sim 6.0.1 standalone + Isaac Lab 3.0.0 beta 2**。
使用其他版本前，请先对照[完整环境要求与检查](./installation)。

## 选择学习路线

<div class="md-route-grid md-route-grid-two">
  <div class="md-route-card md-route-orange">
    <span>路线 1 · 最推荐</span>
    <strong>先玩 ROS 2</strong>
    <p>在 RViz 里看到完整模型，活动 14 个关节，再跑几个现成动作。不需要 Isaac Sim。</p>
  </div>
  <div class="md-route-card md-route-aqua">
    <span>路线 2 · ROS 2 之后</span>
    <strong>再去 Isaac Sim</strong>
    <p>打开仓库自带 USD，先让鸭子走起来，再玩键盘动作和训练。</p>
  </div>
</div>

## 顺着这四步走就行

1. **先检查电脑，只安装当前路线需要的软件。**
2. **先玩 ROS 2。** 准备快、反馈快，模型哪里不对也更容易看出来。
3. **再开 Isaac Sim。** 先打开现成 USD，再加策略，不要一上来就训练。
4. **最后再训练。** 正式跑很久以前，先做 5 轮小测试。

::: tip 没有真机也能把教程玩完
本教程的操作都在仿真中完成。实体机器人部署还需要驱动适配和硬件测试。
:::

<div class="md-page-complete">
  <strong>下一步：准备环境</strong>
  <p>点击下一页，检查电脑环境，并学习打开终端、粘贴命令和确认运行结果。</p>
</div>
