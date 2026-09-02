# MicroDuck ROS 2 + Isaac Sim

[简体中文](README.zh-CN.md) · [Read the tutorial](https://osrbot.github.io/microduck-ros2-isaac/)

This repository provides a hands-on tutorial for using the public
[Pollen Robotics MicroDuck](https://pollen-robotics.com/microduck/) model with
ROS 2 Jazzy and NVIDIA Isaac Sim. It has three practical paths:

- open the complete robot in RViz and move its joints with sliders;
- open the included USD in Isaac Sim and play the released walking, sitting,
  ground-pick, kick, and roll policies;
- train a new flat-ground velocity policy with the native Isaac Lab task, or
  drive the Isaac playground from ROS 2.

Start with ROS 2 for the quickest setup. Isaac Sim is not required for that
path.

## ROS 2 quick start

Install ROS 2 Jazzy Desktop and `python3-colcon-common-extensions`, then run:

```bash
git clone https://github.com/osrbot/microduck-ros2-isaac.git
cd microduck-ros2-isaac/ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

MicroDuck should appear in RViz. Use the Joint State Publisher window to move
its 14 joints. See the
[ROS 2 tutorial](https://osrbot.github.io/microduck-ros2-isaac/ros2/) for camera
controls and missing-part checks.

Run an automatic nodding, stepping, and bowing routine without Isaac:

```bash
ros2 launch microduck_examples rviz_motion_demo.launch.py
```

See the [ROS 2 examples](https://osrbot.github.io/microduck-ros2-isaac/ros2/examples)
for the RViz motions, ROS-to-Isaac showcase, and keyboard controls.

## Isaac Sim playground

The included USD stage is:

```text
assets/isaac/robot_allcollisions/robot_allcollisions.usda
```

Open that file in Isaac Sim to inspect the model. To open the multi-skill
playground, use an existing Isaac Sim and Isaac Lab installation:

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
./scripts/run_isaac_playground.sh --follow-camera --viz kit
```

See the [Isaac Sim tutorial](https://osrbot.github.io/microduck-ros2-isaac/isaac/)
for the keyboard map, ROS 2 bridge, training task, and headless checks.

## Isaac Lab training smoke

The repository includes the native task
`Isaac-MicroDuck-Velocity-Flat-v0`. Start with a five-iteration pipeline check:

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/train_isaac_velocity.sh
```

Five iterations validate task registration, simulation, PPO updates, and
checkpoint output; they are not enough to learn a gait. See the
[training tutorial](https://osrbot.github.io/microduck-ros2-isaac/isaac/training).

## What is in the repository

- `ros2_ws/src/microduck_description/`: ROS 2 description package, meshes,
  launch file, and RViz configuration.
- `ros2_ws/src/microduck_control_bridge/`: ROS commands and Isaac telemetry for
  the localhost playground.
- `ros2_ws/src/microduck_examples/`: RViz-only motions and automatic
  ROS-to-Isaac showcase programs.
- `assets/isaac/`: the generated USD used by the Isaac tutorial.
- `source/microduck_isaac_lab/`: native Isaac Lab task and RSL-RL PPO config.
- `scripts/`: setup, conversion, playback, training, validation, and
  maintenance tools.
- `docs/`: the bilingual tutorial website.
- `artifacts/`: technical test records for contributors who want the details.

This project focuses on visualization, simulation, and learning experiments.
It does not include a physical robot driver or `ros2_control`. The Isaac task
uses an implicit-PD approximation and is not a sim-to-real claim.

## Credits and licensing

This is an independent community project and is not endorsed by Pollen
Robotics. Original integration code and documentation are Apache-2.0.
Upstream-derived meshes, Xacro, and USD remain subject to the model terms
described by Pollen Robotics as “Creative Commons BY-SA-NC” without a stated
version. See [`NOTICE-MICRODUCK.md`](NOTICE-MICRODUCK.md) before redistribution
or commercial use.
