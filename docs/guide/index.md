# Start here: choose your duck run

You do not need to install every tool or read every page. Pick the result you want today, finish one route, then decide
whether to keep going.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Reading time</span><strong>3 minutes</strong></div>
  <div role="listitem"><span>For</span><strong>First-time visitors</strong></div>
  <div role="listitem"><span>Terminals</span><strong>None yet</strong></div>
  <div role="listitem"><span>You leave with</span><strong>One clear starting route</strong></div>
</div>

## Pick one route

<div class="md-route-grid">
  <a class="md-route-card md-route-orange" href="/microduck-ros2-isaac/ros2/">
    <span>ROUTE 1 · 10–15 MIN · RECOMMENDED</span>
    <strong>Start with ROS 2</strong>
    <p>Open the complete model in RViz, move all 14 joints, then run the nod, step, and bow demo. Isaac Sim is not required.</p>
  </a>
  <a class="md-route-card md-route-aqua" href="/microduck-ros2-isaac/isaac/">
    <span>ROUTE 2 · 20–30 MIN</span>
    <strong>Continue in Isaac Sim</strong>
    <p>Open the included USD, replay a walking policy, then use the playground for sitting, kicking, ground pick, and rolling.</p>
  </a>
  <a class="md-route-card md-route-pink" href="/microduck-ros2-isaac/ros2/isaac-control">
    <span>ROUTE 3 · 25–40 MIN</span>
    <strong>Drive Isaac from ROS 2</strong>
    <p>Use three terminals to send ROS commands into Isaac and return the live pose to RViz.</p>
  </a>
</div>

## Not sure? Use this order

1. **ROS 2 first.** Check the model, meshes, joints, and TF with the lightest setup.
2. **One Isaac policy next.** Check the GPU, Vulkan, Isaac Sim, and a released policy together.
3. **Open the playground.** Switch skills from the keyboard and learn what is already available.
4. **Train last.** Run the five-iteration smoke test before spending hours on a full experiment.

Each stage has a visible pass condition. If something breaks, you know whether the issue belongs to ROS, rendering,
policy playback, or training.

## Minimum setup by route

| Route | You need | You do not need yet |
| --- | --- | --- |
| ROS 2 / RViz | Ubuntu 24.04 and ROS 2 Jazzy | NVIDIA GPU or Isaac Sim |
| Open the USD | Linux and Isaac Sim | USD conversion |
| Policy playground | Isaac Sim, Isaac Lab, NVIDIA GPU | Training your own policy |
| Native training | Isaac Sim, Isaac Lab, enough VRAM | Physical hardware or a sim-to-real claim |

<div class="md-page-complete">
  <strong>Route chosen? Move on.</strong>
  <p>The setup page starts with terminal shortcuts, copy and paste, and opening another window, then gives separate ROS 2 and Isaac pass checks.</p>
</div>

<div class="md-next-grid">
  <a class="md-next-card" href="/microduck-ros2-isaac/guide/installation"><span>NEXT FOR EVERY ROUTE</span><strong>Install and check the environment →</strong><p>Learn the terminal keys, clone the repository, and check ROS 2 or Isaac Lab.</p></a>
  <a class="md-next-card" href="/microduck-ros2-isaac/ros2/"><span>ALREADY SET UP</span><strong>Open MicroDuck in RViz →</strong><p>Build the description package, inspect the model, and move a joint.</p></a>
</div>
