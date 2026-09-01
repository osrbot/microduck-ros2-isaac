# Open MicroDuck in RViz

The repository includes the robot description, meshes, launch file, and RViz
configuration.

## 1. Build the package

From the repository root:

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

If ROS 2 or `colcon` is missing, return to [installation](/guide/installation).

## 2. Launch RViz

```bash
ros2 launch microduck_description view_microduck.launch.py
```

RViz should open with MicroDuck standing in its default home pose.

## 3. Move the joints

Stop the previous launch with <kbd>Ctrl</kbd>+<kbd>C</kbd>, then run:

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

A Joint State Publisher window will appear. Move a slider and the matching
joint should move in RViz.

## Expected result

- RViz opens without red errors in the RobotModel display.
- The complete head, body, two legs, and feet are visible.
- Left-drag rotates the view, the mouse wheel zooms, and middle-drag pans.
- Moving a slider changes the robot pose.

Continue with [RViz controls and joints](./rviz).

## Useful launch options

| Option | What it does |
| --- | --- |
| `use_gui:=true` | Opens the joint sliders |
| `rviz_fullscreen:=true` | Opens RViz fullscreen when the desktop cannot maximize it |
| `use_rviz:=false` | Runs the description and TF nodes without RViz |
| `with_collision_meshes:=true` | Adds collision geometry for debugging |

::: details For contributors: regenerate the description
You only need this when changing the upstream model or generator:

```bash
cd ..
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
./scripts/generate_ros_description.py
./scripts/validate_ros2_package.sh
```

After regenerating, rebuild the ROS workspace and restart the launch.
:::
