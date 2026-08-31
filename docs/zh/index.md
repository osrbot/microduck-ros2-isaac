---
layout: home

hero:
  name: "MicroDuck ROS 2 + Isaac Sim"
  text: "同一份模型，两条实用机器人工作流。"
  tagline: "面向 ROS 2 可视化、经过验证的 USD 资产与官方 ONNX 策略回放的可复现社区项目，并明确展示证据与能力边界。"
  image:
    src: /hero-pipeline.svg
    alt: MicroDuck ROS 2 与 Isaac Sim 工作流
  actions:
    - theme: brand
      text: 从 ROS 2 开始
      link: /zh/guide/
    - theme: alt
      text: 在 Isaac Sim 中运行
      link: /zh/isaac/

features:
  - icon: 🧭
    title: ROS 2 与 RViz
    details: 构建 Jazzy description 包，检查完整运动学树，并操作策略使用的全部 14 个关节。
  - icon: ◈
    title: 经过验证的 USD
    details: 使用 Isaac 导入器转换固定版本 MJCF，再检查刚体、关节、质量、单位和碰撞状态。
  - icon: ∿
    title: ONNX 策略回放
    details: 重建官方 61 输入到 14 输出的策略契约，以 50 Hz 回放站立或行走策略。
---

<section class="md-home-section">
  <h2>围绕可验证契约构建</h2>
  <p class="md-home-lead">项目将 Pollen Robotics 固定版本的 MJCF 与已发布策略作为源输入。ROS 和 Isaac 输出属于派生产物，需要检查并记录证据，而不是因为“能在查看器里打开”就默认正确。</p>
  <div class="md-proof-grid">
    <div class="md-proof-card"><span class="md-proof-value">15</span><span class="md-proof-label">选定仿真模型中的物理刚体</span></div>
    <div class="md-proof-card"><span class="md-proof-value">14</span><span class="md-proof-label">已发布策略契约中的可动关节</span></div>
    <div class="md-proof-card"><span class="md-proof-value">61 → 14</span><span class="md-proof-label">ONNX 观测与动作维度</span></div>
    <div class="md-proof-card"><span class="md-proof-value">50 Hz</span><span class="md-proof-label">两条策略回放路径的推理频率</span></div>
  </div>
  <div class="md-boundary">
    <span class="md-boundary-mark">i</span>
    <div><strong>开始前先理解能力边界</strong><p>这是独立社区项目。目前提供 description、可视化、USD 转换与策略回放，不代表原生 Isaac Lab 训练、ROS 到 Isaac 控制或实体机器人驱动已经完成。</p></div>
  </div>
</section>

<section class="md-home-section md-home-next">
  <div class="md-section-kicker">从小目标开始</div>
  <h2>选择你今天需要得到的结果</h2>
  <div class="md-route-grid">
    <a class="md-route-card md-route-orange" href="./guide/"><span>01</span><strong>准备项目</strong><p>固定上游输入，只安装当前路线真正需要的运行环境。</p></a>
    <a class="md-route-card md-route-aqua" href="./ros2/"><span>02</span><strong>在 ROS 2 中检查</strong><p>构建 description，打开 RViz，并操作策略使用的全部关节。</p></a>
    <a class="md-route-card md-route-pink" href="./isaac/"><span>03</span><strong>在 Isaac 中回放</strong><p>先验证 USD 契约，再运行站立或行走 ONNX 策略。</p></a>
  </div>
  <p class="md-home-links"><a href="./troubleshooting">故障排查</a><span>·</span><a href="./faq">常见问题</a><span>·</span><a href="./reference/limitations">已知限制</a><span>·</span><a href="./project/licensing">许可边界</a></p>
</section>
