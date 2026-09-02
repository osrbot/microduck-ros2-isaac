# Install what you need

## Clone the repository

```bash
git clone https://github.com/osrbot/microduck-ros2-isaac.git
cd microduck-ros2-isaac
```

The ROS 2 package and Isaac USD are included. No conversion is required.

## For the ROS 2 tutorial

The commands below are for Ubuntu 24.04 with ROS 2 Jazzy:

```bash
sudo apt update
sudo apt install \
  ros-jazzy-desktop \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-xacro \
  python3-colcon-common-extensions
```

After installation, continue with [Open MicroDuck in RViz](/ros2/).

## For the Isaac Sim tutorial

Install NVIDIA Isaac Sim and Isaac Lab first. This project was tested with:

- Ubuntu 24.04;
- Isaac Sim 6.0.1 standalone;
- Isaac Lab 3.0.0 beta 2;
- an NVIDIA GPU with a working driver and Vulkan setup;
- `git`, `bash`, Python 3.12, and `uv`.

If your Isaac Lab checkout is not at `~/rlgpu_ws/IsaacLab`, tell the scripts
where it is:

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
```

For single-policy playback or the skill playground, fetch the released policy
files and install ONNX Runtime in the project-local environment:

```bash
./scripts/fetch_upstream.sh
./scripts/setup_isaac_python_env.sh
```

These commands create ignored `reference/` and `work/` directories inside the
project. They do not modify your Isaac Lab checkout.

Continue with [Open MicroDuck in Isaac Sim](/isaac/). The native training task
does not require ONNX Runtime, but uses the same Isaac Sim and Isaac Lab setup.

::: tip Other versions may work
The list above is the tested setup. With another Isaac release, open the USD
before trying policy playback.
:::
