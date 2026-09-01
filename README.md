# MicroDuck ROS 2 + Isaac Sim

[简体中文](README.zh-CN.md) · [Read the tutorial](https://osrbot.github.io/microduck-ros2-isaac/)

This repository provides a hands-on tutorial for using the public
[Pollen Robotics MicroDuck](https://pollen-robotics.com/microduck/) model with
ROS 2 Jazzy and NVIDIA Isaac Sim. It has two paths:

- open the complete robot in RViz and move its joints with sliders;
- open the included USD in Isaac Sim and run the released walking policy.

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

## Isaac Sim quick start

The included USD stage is:

```text
assets/isaac/robot_allcollisions/robot_allcollisions.usda
```

Open that file in Isaac Sim to inspect the model. To run the walking policy,
use an existing Isaac Sim and Isaac Lab installation:

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
./scripts/run_isaac_policy.sh \
  --duration 60 --vx 0.3 --action-scale 0.9 \
  --follow-camera --viz kit
```

See the [Isaac Sim tutorial](https://osrbot.github.io/microduck-ros2-isaac/isaac/)
for setup details and a headless option.

## What is in the repository

- `ros2_ws/src/microduck_description/`: ROS 2 description package, meshes,
  launch file, and RViz configuration.
- `assets/isaac/`: the generated USD used by the Isaac tutorial.
- `scripts/`: setup, conversion, policy playback, and maintenance tools.
- `docs/`: the bilingual tutorial website.
- `artifacts/`: technical test records for contributors who want the details.

This project focuses on visualization and simulation. It does not include a
physical robot driver, `ros2_control`, or a ready-made Isaac Lab training task.

## Credits and licensing

This is an independent community project and is not endorsed by Pollen
Robotics. Original integration code and documentation are Apache-2.0.
Upstream-derived meshes, Xacro, and USD remain subject to the model terms
described by Pollen Robotics as “Creative Commons BY-SA-NC” without a stated
version. See [`NOTICE-MICRODUCK.md`](NOTICE-MICRODUCK.md) before redistribution
or commercial use.
