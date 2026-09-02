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
      text: 从这里开始
      link: /zh/guide/
    - theme: alt
      text: 先看环境要求
      link: /zh/guide/installation

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
  <div class="md-section-kicker">先看电脑，别急着敲命令</div>
  <h2>你的电脑能跑哪条路线？</h2>
  <p class="md-home-lead">ROS 2 路线比较轻，Isaac Sim 则需要 NVIDIA 显卡和更多软件。先看清楚，再决定怎么开玩。</p>
  <div class="md-requirement-grid">
    <div class="md-requirement-card md-route-orange"><span>ROS 2 + RViz</span><strong>Ubuntu 24.04 + ROS 2 Jazzy</strong><p>不需要 NVIDIA 显卡，也不需要 Isaac Sim。</p></div>
    <div class="md-requirement-card md-route-aqua"><span>Isaac Sim</span><strong>Ubuntu 24.04 + NVIDIA GPU</strong><p>完整测试组合是 Isaac Sim 6.0.1 与 Isaac Lab 3.0.0 beta 2。</p></div>
  </div>
  <p class="md-home-start"><a href="./guide/installation">查看完整环境要求 →</a></p>
</section>

<section class="md-home-section">
  <h2>一路上会玩到什么？</h2>
  <p class="md-home-lead">下面只是预告，不会把你直接扔进半路。正式教程会先检查电脑，再从 ROS 2 一步一步走到 Isaac Sim。</p>
  <div class="md-route-grid">
    <div class="md-route-card md-route-orange"><span>01</span><strong>把鸭子请进 RViz</strong><p>看完整模型、转镜头，再试试 14 个关节。</p></div>
    <div class="md-route-card md-route-aqua"><span>02</span><strong>打开 Isaac 游乐场</strong><p>走路、坐起、低头碰地、踢球和前滚。</p></div>
    <div class="md-route-card md-route-pink"><span>03</span><strong>自己教一只鸭</strong><p>先跑小测试，再用 Isaac Lab 训练新动作。</p></div>
  </div>
  <p class="md-home-start"><a href="./guide/">按步骤开始 →</a></p>
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
  <p>第一次来就走引导路线：先看电脑，再运行命令。每一页底部只留一个明确的“下一页”，不会突然把你扔到别的章节。</p>
  <p class="md-home-start"><a href="./guide/">从第 1 步开始 →</a></p>
  <p class="md-home-links"><a href="./guide/installation">环境要求</a><span>·</span><a href="./troubleshooting">遇到问题</a><span>·</span><a href="./faq">常见问题</a><span>·</span><a href="./project/licensing">来源与许可</a></p>
</section>
