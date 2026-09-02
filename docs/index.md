---
layout: home

hero:
  name: "MicroDuck"
  text: "Ready? Go Go Duck!"
  tagline: "Open MicroDuck in RViz, move its joints, or run a policy in Isaac Sim."
  image:
    src: /images/hero-microduck-meme.webp?v=1
    alt: A playful hybrid of a yellow meme duck and the MicroDuck robot
  actions:
    - theme: brand
      text: Start with ROS 2
      link: /ros2/
    - theme: alt
      text: Open in Isaac Sim
      link: /isaac/

features:
  - icon: 👀
    title: Open in RViz
    details: Build the included ROS 2 package and inspect the complete model.
  - icon: 🎛️
    title: Move all 14 joints
    details: Use the Joint State Publisher sliders to test every movable joint.
  - icon: 🦆
    title: Play skills, then train
    details: Switch sitting, kicking, and rolling skills, or start a native Isaac Lab task.
---

<section class="md-home-section">
  <h2>Choose a tutorial</h2>
  <p class="md-home-lead">Use ROS 2 for visualization and controls. Use Isaac Sim for the skill playground or native policy training.</p>
  <div class="md-route-grid">
    <a class="md-route-card md-route-orange" href="./ros2/"><span>01</span><strong>ROS 2 and RViz</strong><p>Build the package, inspect the model, and move its joints.</p></a>
    <a class="md-route-card md-route-aqua" href="./isaac/playground"><span>02</span><strong>Skill playground</strong><p>Walk, sit, pick, kick, and roll from one interactive runner.</p></a>
    <a class="md-route-card md-route-pink" href="./troubleshooting"><span>03</span><strong>Troubleshooting</strong><p>Fix missing meshes, RViz controls, or Isaac Sim and GPU errors.</p></a>
  </div>
</section>

<section class="md-home-section md-duck-gallery">
  <div class="md-section-kicker">PREVIEW</div>
  <h2>See what is included</h2>
  <div class="md-duck-gallery-grid">
    <figure class="md-image-card md-image-card-main">
      <img src="/images/microduck-waddle-lab.webp" alt="Colorful illustration of MicroDuck waddling from RViz toward Isaac Sim" width="1440" height="960" loading="lazy">
      <figcaption><strong>ROS 2 to Isaac Sim</strong><span>A route illustration; the tutorials contain the actual previews and troubleshooting screenshots.</span></figcaption>
    </figure>
    <figure class="md-image-card md-image-card-lineup">
      <div class="md-lineup-stage"><img src="/images/microduck-lineup.webp" alt="Four physical MicroDuck robots in different colors and poses" width="1839" height="638" loading="lazy"></div>
      <figcaption><strong>MicroDuck lineup</strong><span>Four robots from the official MicroDuck project page.</span><a href="https://github.com/pollen-robotics/microduck">Image source: Pollen Robotics MicroDuck ↗</a></figcaption>
    </figure>
  </div>
</section>

<section class="md-home-section md-home-next">
  <div class="md-first-duck-row">
    <div><div class="md-section-kicker">START HERE</div><h2>New here?</h2></div>
    <div class="md-play-duck" role="img" aria-label="Come play!"><span>Come play!</span><img src="/images/play-duck-sticker.webp" alt="" width="640" height="640" loading="lazy"></div>
  </div>
  <p>Start with <a href="./ros2/">ROS 2 and RViz</a> for the quickest setup. If Isaac Sim and Isaac Lab are ready, open the <a href="./isaac/playground">skill playground</a>, then try <a href="./isaac/training">native training</a>.</p>
  <p class="md-home-links"><a href="./guide/">Start</a><span>·</span><a href="./faq">FAQ</a><span>·</span><a href="./reference/limitations">Limitations</a><span>·</span><a href="./project/licensing">Licensing</a></p>
</section>
