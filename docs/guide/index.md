# Start here: pick your first route

First visit? Follow the pages in order. We check your computer before the first
command, start with the lighter ROS 2 route, and move into Isaac Sim after that.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Reading time</span><strong>3 minutes</strong></div>
  <div role="listitem"><span>For</span><strong>First-time visitors</strong></div>
  <div role="listitem"><span>Terminals</span><strong>None yet</strong></div>
  <div role="listitem"><span>Next</span><strong>Check your computer</strong></div>
</div>

## Check your computer first

| Route | You need | You do not need yet |
| --- | --- | --- |
| ROS 2 and RViz | Ubuntu 24.04 and ROS 2 Jazzy | NVIDIA GPU or Isaac Sim |
| Isaac Sim | Ubuntu 24.04, NVIDIA GPU, Isaac Sim | A real robot |
| Isaac Lab policies and training | Isaac Sim and Isaac Lab | A physical MicroDuck or a sim-to-real setup |

The fully tested Isaac setup is **Isaac Sim 6.0.1 standalone + Isaac Lab 3.0.0
beta 2**. Other versions may work, but start with the [full requirements and
checks](./installation) before chasing an Isaac error.

## Which route should you take?

<div class="md-route-grid md-route-grid-two">
  <div class="md-route-card md-route-orange">
    <span>ROUTE 1 · RECOMMENDED</span>
    <strong>Start with ROS 2</strong>
    <p>See the whole duck in RViz, move all 14 joints, then try the ready-made motion examples. No Isaac Sim needed.</p>
  </div>
  <div class="md-route-card md-route-aqua">
    <span>ROUTE 2 · AFTER ROS 2</span>
    <strong>Move on to Isaac Sim</strong>
    <p>Open the included USD, play one walking policy, then try the keyboard playground and training.</p>
  </div>
</div>

## The simple order

1. **Check the computer and install only what your route needs.**
2. **Try ROS 2 first.** It is faster to set up and easier to troubleshoot.
3. **Open Isaac Sim next.** Start with the included USD, then add policies.
4. **Train last.** Run the short five-iteration check before a long job.

::: tip No real robot is needed
This tutorial is for simulation, learning, and open-source demos. The ROS 2
examples are not a hardware driver, and an Isaac checkpoint is not ready for a
physical robot without separate work and testing.
:::

<div class="md-page-complete">
  <strong>Route picked? Good.</strong>
  <p>Use the single “Next page” button below. It checks your computer and shows the terminal shortcuts before the first real command.</p>
</div>
