---
layout: home

hero:
  name: "MicroDuck"
  text: "Ready? Go Go Duck!"
  tagline: "See the duck in RViz. Move its joints. Let it run in Isaac Sim."
  image:
    src: /images/hero-microduck-meme.webp?v=1
    alt: A playful hybrid of a yellow meme duck and the MicroDuck robot
  actions:
    - theme: brand
      text: Start here
      link: /guide/
    - theme: alt
      text: Check requirements
      link: /guide/installation

features:
  - icon: 👀
    title: Open in RViz
    details: Build the ROS 2 package and meet the whole duck.
  - icon: 🎛️
    title: Move all 14 joints
    details: Drag the sliders and watch every joint move.
  - icon: 🦆
    title: Try cool moves, then train
    details: Make the duck sit, kick, and roll. Ready for more? Train your own walking policy in Isaac Lab.
---

<section class="md-home-section">
  <div class="md-section-kicker">CHECK THIS FIRST</div>
  <h2>Can your computer run it?</h2>
  <p class="md-home-lead">The ROS 2 route is light. Isaac Sim needs an NVIDIA GPU and more software. Check this before you copy any command.</p>
  <div class="md-requirement-grid">
    <div class="md-requirement-card md-route-orange"><span>ROS 2 + RViz</span><strong>Ubuntu 24.04 + ROS 2 Jazzy</strong><p>No NVIDIA GPU or Isaac Sim needed.</p></div>
    <div class="md-requirement-card md-route-aqua"><span>Isaac Sim</span><strong>Ubuntu 24.04 + NVIDIA GPU</strong><p>Tested with Isaac Sim 6.0.1 and Isaac Lab 3.0.0 beta 2.</p></div>
  </div>
  <p class="md-home-start"><a href="./guide/installation">See the full requirements →</a></p>
</section>

<section class="md-home-section">
  <h2>What will you play with?</h2>
  <p class="md-home-lead">These cards show what is ahead. The step-by-step route starts with your computer, then moves from ROS 2 to Isaac Sim.</p>
  <div class="md-route-grid">
    <div class="md-route-card md-route-orange"><span>01</span><strong>ROS 2 and RViz</strong><p>See the full duck, move the camera, and try all 14 joints.</p></div>
    <div class="md-route-card md-route-aqua"><span>02</span><strong>Isaac playground</strong><p>Make the duck walk, sit, pick, kick, and roll.</p></div>
    <div class="md-route-card md-route-pink"><span>03</span><strong>Train your own policy</strong><p>Run a small Isaac Lab check, then teach the duck a new move.</p></div>
  </div>
  <p class="md-home-start"><a href="./guide/">Start step by step →</a></p>
</section>

<section class="md-home-section md-duck-gallery">
  <div class="md-section-kicker">LOOK, DUCKS!</div>
  <h2>Say hi to MicroDuck</h2>
  <div class="md-duck-gallery-grid">
    <figure class="md-image-card md-image-card-main">
      <img src="/images/microduck-waddle-lab.webp" alt="Colorful illustration of MicroDuck waddling from RViz toward Isaac Sim" width="1440" height="960" loading="lazy">
      <figcaption><strong>ROS 2 to Isaac Sim</strong><span>This picture shows the route. Open a tutorial for real screenshots and quick fixes.</span></figcaption>
    </figure>
    <figure class="md-image-card md-image-card-lineup">
      <div class="md-lineup-stage"><img src="/images/microduck-lineup.webp" alt="Four physical MicroDuck robots in different colors and poses" width="1839" height="638" loading="lazy"></div>
      <figcaption><strong>MicroDuck lineup</strong><span>Four ducks, four moods.</span><a href="https://github.com/pollen-robotics/microduck">Image source: Pollen Robotics MicroDuck ↗</a></figcaption>
    </figure>
  </div>
</section>

<section class="md-home-section md-home-next">
  <div class="md-first-duck-row">
    <div><div class="md-section-kicker">LET'S GO</div><h2>Ready to play?</h2></div>
    <div class="md-play-duck" role="img" aria-label="Come play!"><span>Come play!</span><img src="/images/play-duck-sticker.webp" alt="" width="640" height="640" loading="lazy"></div>
  </div>
  <p>Use the guided route the first time. It checks your computer before the first command and keeps one clear next step at the bottom of every page.</p>
  <p class="md-home-start"><a href="./guide/">Start with step 1 →</a></p>
  <p class="md-home-links"><a href="./guide/installation">Requirements</a><span>·</span><a href="./troubleshooting">Troubleshooting</a><span>·</span><a href="./faq">FAQ</a><span>·</span><a href="./project/licensing">Licensing</a></p>
</section>
