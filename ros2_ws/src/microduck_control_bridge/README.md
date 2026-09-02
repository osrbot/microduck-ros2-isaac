# microduck_control_bridge

ROS 2 command and telemetry bridge for the local MicroDuck Isaac playground.

The bridge deliberately keeps `rclpy` outside Isaac Sim's bundled Python. ROS
commands are sent over localhost UDP to `run_isaac_playground.py`; Isaac sends
joint states, base pose, current policy, and upright state back to this node.
This is a teaching/simulation bridge, not a physical-robot driver.

## Topics

Commands consumed by the bridge:

- `cmd_vel` (`geometry_msgs/Twist`);
- `microduck/head_command` (`sensor_msgs/JointState`);
- `microduck/body_command` (`std_msgs/Float64MultiArray`), ordered
  `[x, y, z, roll, pitch, yaw]`;
- `microduck/behavior` (`std_msgs/String`): `walk`, explicit `sit` / `stand`,
  toggle `sitstand`, `ground_pick`, `kick_left`, `kick_right`, or `roulade`;
- `microduck/reset` (`std_msgs/Empty`).

State published from Isaac:

- `joint_states`;
- `microduck/policy_state`;
- `microduck/upright`;
- `world -> base_link` TF.

Launch the bridge, robot description, and RViz with:

```bash
ros2 launch microduck_control_bridge isaac_playground.launch.py
```

Run the small terminal controller with:

```bash
ros2 run microduck_control_bridge microduck_teleop
```
