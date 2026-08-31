# Known limitations

## Isaac playback is not a training environment

The USD and runner support inspection, extension, and policy playback. They do
not implement the upstream reward, observations with training noise, reset
logic, curriculum, environment replication, or native Isaac Lab task APIs.

The runner approximates actuation with implicit PD: 0.55 N·m/rad stiffness,
0.053 N·m·s/rad damping, and a 0.96 N·m effort limit. Upstream models BAM XL330
electrical, friction, saturation, battery, and delay behavior in more detail.

## Smoke parity is not trajectory parity

Both engines remain upright in the recorded scenarios, but displacement and
lateral drift differ materially. Do not use current Isaac trajectories or
rewards as a numerical replacement for upstream MuJoCo results.

## ROS is description-first

The package supplies geometry, kinematics, inertias, TF, RViz, and a home pose.
It does not provide `ros2_control`, Dynamixel communication, a ROS-to-Isaac
bridge, calibration, or hardware acceptance.

The default Xacro velocity limit of 6.0 rad/s is an explicit simulation/planning
fallback. It is not an authoritative hardware safety limit.

## The physical mouth actuator is outside the model

The selected MJCF and policies expose 14 movable joints. Upstream physical
runtime documentation also mentions a mouth actuator, but the simulation model
does not define its geometry, inertia, limits, or policy behavior. This project
does not invent them.

## Collision filtering is simplified

Isaac's importer drops MJCF collision bitmasks. The one source
`self_collision_only` sensor mesh is disabled from general collision. Exact
selective self-collision parity would require validated PhysX collision groups.

## GUI evidence is host-specific

The wrapper mitigates duplicate NVIDIA ICD manifests for project launches; it
does not repair the host driver installation. Launching Isaac another way may
still reproduce the GPU failure. The detailed ROS visual model can also be
limited by remote-desktop encoding at 4K despite a 15 FPS cap.

## Model redistribution needs clarification

Pollen Robotics describes the 3D files as “Creative Commons BY-SA-NC” without a
version. Derived assets should be treated as non-commercial, attribution
required, and share-alike until the author clarifies the exact license. See
[licensing](/project/licensing).
