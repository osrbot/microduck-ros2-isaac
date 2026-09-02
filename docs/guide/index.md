# Choose a tutorial

Use ROS 2 to inspect the model and move its joints. Use Isaac Sim for released
skills or to train a new policy with the native task.

## ROS 2 and RViz

This tutorial covers:

- see the complete MicroDuck model in RViz;
- rotate and zoom the camera;
- move the robot's joints with sliders;
- reuse the description package in another ROS 2 project.

You need Ubuntu 24.04 and ROS 2 Jazzy. Isaac Sim is not required.

**Expected result:** MicroDuck appears in RViz. With the GUI enabled, a second
window controls all 14 joints.

[Open the ROS 2 tutorial →](/ros2/)

## Isaac Sim

This tutorial covers:

- open the included MicroDuck USD;
- inspect the robot in Isaac Sim;
- run the released standing or walking policy;
- switch sitting, ground pick, kick, and roll skills;
- run a native Isaac Lab PPO training task;
- record a short simulation video or livestream demonstration.

You need a Linux computer with a supported NVIDIA GPU, Isaac Sim, and Isaac Lab.

**Expected result:** MicroDuck opens in Isaac Sim, responds to skill commands,
and the training path can produce a new checkpoint.

[Open the Isaac Sim tutorial →](/isaac/)

## ROS 2 and Isaac together

Use the three-terminal route when you want ROS commands to drive the live
Isaac playground and return the pose to RViz. It includes every command,
expected screen, action example, and the headless round-trip check.

[Drive the Isaac duck from ROS 2 →](/ros2/isaac-control)

## Maintenance tools are optional

Conversion scripts, validators, and JSON test records are for contributors.
They are not required for either tutorial.

Next: [installation](./installation).
