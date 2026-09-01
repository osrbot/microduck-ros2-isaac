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
    title: 放鸭开跑
    details: 直接打开仓库自带的 USD，再让它运行已经发布的站立或行走策略。
---

<section class="md-home-section">
  <h2>今天想怎么玩这只鸭子？</h2>
  <p class="md-home-lead">不用先啃模型格式和参数表。选 ROS 2 或 Isaac Sim，复制命令开跑，看看这只鸭子有没有乖乖出现在该出现的地方。</p>
  <div class="md-route-grid">
    <a class="md-route-card md-route-orange" href="./ros2/"><span>01</span><strong>把鸭子请进 RViz</strong><p>构建功能包，转转镜头，再试试关节滑块。</p></a>
    <a class="md-route-card md-route-aqua" href="./isaac/"><span>02</span><strong>放进 Isaac Sim 遛两圈</strong><p>打开已经准备好的 USD，然后用跟随镜头运行行走策略。</p></a>
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
  <p>电脑里已经装好 Isaac Sim 和 Isaac Lab，就直接去 <a href="./isaac/">Isaac Sim 教程</a>。USD 已经打包好了，不用先折腾转换就能把鸭子打开。</p>
  <p class="md-home-links"><a href="./guide/">从这里开始</a><span>·</span><a href="./faq">常见问题</a><span>·</span><a href="./reference/limitations">目前没有什么</a><span>·</span><a href="./project/licensing">来源与许可</a></p>
</section>
