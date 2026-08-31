# MicroDuck ROS 2 + Isaac Sim

[简体中文](README.zh-CN.md) · [Documentation](https://osrbot.github.io/microduck-ros2-isaac/)

An independent, reproducible ROS 2 Jazzy and NVIDIA Isaac Sim compatibility
project for [Pollen Robotics MicroDuck](https://pollen-robotics.com/microduck/).
It keeps pinned upstream MJCF and released ONNX policies as source inputs, then
adds ROS visualization, an inspected USD articulation, policy playback, and
machine-readable validation evidence.

> This is a community project. It is not affiliated with or endorsed by Pollen
> Robotics, and it is not a native Isaac Lab training environment.

## What is included

| Path | Ready now | Explicit boundary |
| --- | --- | --- |
| ROS 2 | `microduck_description`, 15 physical links, 14 joints, inertias, RViz, TF, sliders | No hardware driver or `ros2_control` |
| Isaac Sim | Converted USD, collision correction, structural validator | Not training/contact/actuator parity |
| Policy | Released ONNX playback, 61 → 14 contract, 50 Hz loop | No ROS-to-Isaac bridge |
| Evidence | MuJoCo/Isaac rollouts, ROS runtime checks, retained JSON | No real-robot acceptance |

The physical runtime mentions a mouth actuator, but the selected public MJCF
and policies define 14 movable joints. This project does not invent the missing
simulation geometry, limits, or policy behavior.

## Start here

Fetch the immutable upstream inputs and create the MuJoCo reference environment:

```bash
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
./scripts/run_official_baseline.sh
```

Build and open the ROS 2 description:

```bash
./scripts/generate_ros_description.py
./scripts/validate_ros2_package.sh
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

Prepare Isaac, convert the USD, and run the walking policy:

```bash
cd ../
./scripts/setup_isaac_python_env.sh
./scripts/convert_mjcf_to_usd.sh
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_walking.onnx \
  --duration 10 --vx 0.3 --action-scale 0.9 --headless \
  --output artifacts/isaac/policy_walk_local.json
```

Run all eight headless validation stages after both environments are ready:

```bash
./scripts/validate_all.sh
```

Use the [getting-started guide](https://osrbot.github.io/microduck-ros2-isaac/guide/)
for prerequisites and path-specific instructions. The documentation source can
also be previewed locally with Node.js 24:

```bash
npm ci
npm run docs:dev
```

## Recorded matrix

Validated on Ubuntu 24.04, ROS 2 Jazzy, RTX 4080 SUPER, Isaac Sim 6.0.1, and
Isaac Lab 3.0.0 beta 2. The recorded model has 15 bodies, 14 movable joints,
about 0.737243 kg total mass, and a `61 -> 14` ONNX interface at 50 Hz.

Read the [results](https://osrbot.github.io/microduck-ros2-isaac/reference/results)
and [known limitations](https://osrbot.github.io/microduck-ros2-isaac/reference/limitations)
before reusing these claims on another host or version.

## Repository layout

- `ros2_ws/src/microduck_description/`: ROS 2 package.
- `assets/isaac/`: generated and inspected USD asset.
- `scripts/`: fetch, conversion, playback, and validation tools.
- `artifacts/`: retained machine-readable evidence.
- `docs/`: bilingual VitePress documentation.
- `reference/`: pinned upstream checkouts, generated locally and ignored.
- `work/`: rebuildable environments and logs, ignored.

## Licensing

Original integration code and documentation are Apache-2.0. Upstream-derived
meshes, Xacro, and USD remain subject to Pollen Robotics' model terms, described
upstream as “Creative Commons BY-SA-NC” without a stated version. Treat this as
a mixed-license repository, preserve attribution, and read
[`NOTICE-MICRODUCK.md`](NOTICE-MICRODUCK.md) before redistribution or monetized
use.
