# MicroDuck ROS 2 examples

This package contains simulation-only examples:

- `rviz_motion_demo.launch.py` animates the 14-joint description in RViz;
- `isaac_showcase.launch.py` runs repeatable ROS commands against the Isaac
  playground and displays its live telemetry in RViz.

These examples publish commands and visualization states. They are not a
physical robot driver and do not provide `ros2_control` hardware interfaces.
