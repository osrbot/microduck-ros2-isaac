---
layout: home

hero:
  name: "MicroDuck"
  text: "一起来玩鸭？"
  tagline: "不先讲一堆干巴巴的理论：看模型、动关节、跑策略，跟着步骤把这只开源小鸭子真正玩起来。"
  image:
    src: /images/hero-microduck-meme.webp?v=1
    alt: 招手走来的表情包黄鸭与 MicroDuck 机器人融合角色
  actions:
    - theme: brand
      text: 先玩 ROS 2
      link: /zh/ros2/
    - theme: alt
      text: 再去 Isaac Sim
      link: /zh/isaac/

features:
  - icon: 👀
    title: 先让鸭子露个脸
    details: 构建仓库里已经准备好的 ROS 2 功能包，让完整的 MicroDuck 出现在 RViz 里。
  - icon: 🎛️
    title: 扭扭脖子，动动腿
    details: 拖动 Joint State Publisher 滑块，看看公开仿真模型里的 14 个关节都能怎么动。
  - icon: 🦆
    title: 玩动作，再自己教
    details: 在 Isaac Sim 切换坐起、踢球和前滚，也能从原生 Isaac Lab 任务开始训练。
---

<section class="md-home-section">
  <h2>今天想怎么玩这只鸭子？</h2>
  <p class="md-home-lead">不用先啃模型格式和参数表。选 ROS 2 或 Isaac Sim，先把鸭子玩起来，再决定要不要自己训练一张新策略。</p>
  <div class="md-route-grid">
    <a class="md-route-card md-route-orange" href="./ros2/"><span>01</span><strong>把鸭子请进 RViz</strong><p>构建功能包，转转镜头，再试试关节滑块。</p></a>
    <a class="md-route-card md-route-aqua" href="./isaac/playground"><span>02</span><strong>打开多动作游乐场</strong><p>走路、坐起、低头碰地、踢球、前滚，键盘说换就换。</p></a>
    <a class="md-route-card md-route-pink" href="./troubleshooting"><span>03</span><strong>鸭子闹脾气了？</strong><p>处理 RViz 缺件、画面卡住，以及 Isaac Sim 启动或 GPU 崩溃问题。</p></a>
  </div>
</section>

<section class="md-home-section md-duck-gallery">
  <div class="md-section-kicker">鸭子出没，请注意</div>
  <h2>先看两眼，再决定怎么遛</h2>
  <div class="md-duck-gallery-grid">
    <figure class="md-image-card md-image-card-main">
      <img src="/images/microduck-waddle-lab.webp" alt="MicroDuck 从 RViz 走向 Isaac Sim 的彩色插图" width="1440" height="960" loading="lazy">
      <figcaption><strong>从 RViz 一路溜达到 Isaac Sim</strong><span>这是路线示意插图；真正的模型预览和排错截图都放在对应教程里。</span></figcaption>
    </figure>
    <figure class="md-image-card md-image-card-lineup">
      <div class="md-lineup-stage"><img src="/images/microduck-lineup.webp" alt="四种配色和姿态的 MicroDuck 实体机器人" width="1839" height="638" loading="lazy"></div>
      <figcaption><strong>先认个鸭</strong><span>MicroDuck 官方项目展示图：四只鸭，四种心情。</span><a href="https://github.com/pollen-robotics/microduck">图片来源：Pollen Robotics MicroDuck ↗</a></figcaption>
    </figure>
  </div>
</section>

<section class="md-home-section md-home-next">
  <div class="md-first-duck-row">
    <div><div class="md-section-kicker">挑一条路线，开鸭</div><h2>第一次玩鸭，从哪儿下手？</h2></div>
    <div class="md-play-duck" role="img" aria-label="来玩鸭"><span>来玩鸭</span><img src="/images/play-duck-sticker.webp" alt="" width="640" height="640" loading="lazy"></div>
  </div>
  <p>想最快和鸭子打个照面，就从 <a href="./ros2/">ROS 2 与 RViz</a> 开始。不需要 Isaac Sim，也不要求 NVIDIA 显卡。</p>
  <p>电脑里已经装好 Isaac Sim 和 Isaac Lab，就直接去 <a href="./isaac/playground">多动作游乐场</a>。想自己教它走路，再接着做 <a href="./isaac/training">Isaac Lab 训练</a>。</p>
  <p class="md-home-links"><a href="./guide/">从这里开始</a><span>·</span><a href="./faq">常见问题</a><span>·</span><a href="./reference/limitations">目前没有什么</a><span>·</span><a href="./project/licensing">来源与许可</a></p>
</section>
