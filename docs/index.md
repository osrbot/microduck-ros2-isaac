---
layout: home

hero:
  name: "MicroDuck ROS 2 + Isaac Sim"
  text: "One model. Two practical robotics workflows."
  tagline: "A reproducible community integration for ROS 2 visualization, validated USD assets, and released ONNX policy playback — with the evidence and limitations kept visible."
  image:
    src: /hero-pipeline.svg
    alt: MicroDuck ROS 2 and Isaac Sim workflow
  actions:
    - theme: brand
      text: Start with ROS 2
      link: /guide/
    - theme: alt
      text: Run in Isaac Sim
      link: /isaac/

features:
  - icon: 🧭
    title: ROS 2 and RViz
    details: Build a Jazzy description package, inspect the complete kinematic tree, and articulate all 14 policy joints.
  - icon: ◈
    title: Validated USD
    details: Convert the pinned MJCF with Isaac's importer, then check bodies, joints, mass, units, and collision state.
  - icon: ∿
    title: ONNX policy playback
    details: Reconstruct the released 61-to-14 policy contract and replay standing or walking at 50 Hz.
---

<section class="md-home-section">
  <h2>Built around verifiable contracts</h2>
  <p class="md-home-lead">The project keeps Pollen Robotics' pinned MJCF and released policies as source inputs. ROS and Isaac outputs are derived, inspected, and reported instead of being treated as correct because they open in a viewer.</p>
  <div class="md-proof-grid">
    <div class="md-proof-card"><span class="md-proof-value">15</span><span class="md-proof-label">physical bodies in the selected simulation model</span></div>
    <div class="md-proof-card"><span class="md-proof-value">14</span><span class="md-proof-label">movable joints in the released policy contract</span></div>
    <div class="md-proof-card"><span class="md-proof-value">61 → 14</span><span class="md-proof-label">ONNX observation and action dimensions</span></div>
    <div class="md-proof-card"><span class="md-proof-value">50 Hz</span><span class="md-proof-label">policy inference rate in both playback paths</span></div>
  </div>
  <div class="md-boundary">
    <span class="md-boundary-mark">i</span>
    <div><strong>Know the boundary before you start</strong><p>This is an independent community project. It currently provides description, visualization, USD conversion, and policy playback — not native Isaac Lab training, ROS-to-Isaac control, or a physical-robot driver.</p></div>
  </div>
</section>

<section class="md-home-section md-home-next">
  <div class="md-section-kicker">START SMALL</div>
  <h2>Choose the result you need today</h2>
  <div class="md-route-grid">
    <a class="md-route-card md-route-orange" href="./guide/"><span>01</span><strong>Prepare the project</strong><p>Pin upstream inputs and install only the runtime your path needs.</p></a>
    <a class="md-route-card md-route-aqua" href="./ros2/"><span>02</span><strong>Inspect in ROS 2</strong><p>Build the description, open RViz, and articulate all policy joints.</p></a>
    <a class="md-route-card md-route-pink" href="./isaac/"><span>03</span><strong>Replay in Isaac</strong><p>Inspect the USD contract, then run standing or walking ONNX policies.</p></a>
  </div>
  <p class="md-home-links"><a href="./troubleshooting">Troubleshooting</a><span>·</span><a href="./faq">FAQ</a><span>·</span><a href="./reference/limitations">Known limitations</a><span>·</span><a href="./project/licensing">Licensing</a></p>
</section>
