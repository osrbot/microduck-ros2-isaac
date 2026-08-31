# Install and prepare

The repository pins the upstream MicroDuck model and policy revisions. Fetch
those revisions first; do not substitute a moving upstream branch in a recorded
validation run.

## Common requirements

- Git and Bash
- Ubuntu 24.04 x86_64 for the validated full workflow
- Python 3.12
- An existing Isaac Sim and Isaac Lab installation for the Isaac path

Clone the project, then enter its root:

```bash
git clone https://github.com/osrbot/microduck-ros2-isaac.git
cd microduck-ros2-isaac
```

The public repository does not exist yet while this documentation is being
prepared locally. Use the checked-out project directory until publication.

## Fetch immutable inputs

```bash
./scripts/fetch_upstream.sh
```

The script reads [`upstream.lock`](https://github.com/osrbot/microduck-ros2-isaac/blob/main/upstream.lock)
and creates reproducible checkouts under `reference/`. That directory is local
and intentionally not committed.

## Prepare the MuJoCo baseline

```bash
./scripts/setup_mujoco_env.sh
./scripts/run_official_baseline.sh
```

This provides the source-model inventory and reference rollouts used by later
comparison. It is part of verification, not a requirement for merely viewing
an already generated ROS package.

## Add ROS 2

Install ROS 2 Jazzy and the packages used by the description workspace:

```bash
sudo apt update
sudo apt install \
  ros-jazzy-desktop \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-xacro \
  python3-colcon-common-extensions
```

Continue with [ROS 2 build and launch](/ros2/).

## Add Isaac Sim

The validated host uses Isaac Sim 6.0.1 standalone and an Isaac Lab 3.0.0 beta
2 checkout. Point the scripts at your existing checkout when it is elsewhere:

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

This installs ONNX Runtime 1.24.4 into `work/isaac_python_pkgs`; it does not
modify the Isaac Lab checkout. Continue with [USD conversion](/isaac/).

## Verify the environment

```bash
./scripts/check_environment.sh
```

Compare your setup with the [validated environment](/reference/environment).
Different versions may work, but they are a new test matrix rather than proof
that the recorded results automatically transfer.
