# Frequently asked questions

## Does the repository contain URDF and USD?

Yes. It contains the generated ROS Xacro/meshes and a generated Isaac USD asset.
Both derive from the pinned upstream MJCF and remain subject to the model's
upstream terms.

## Is there a ROS 2 package?

Yes: `microduck_description`. It provides robot description, meshes, inertias,
TF/RViz launch, an official home-pose publisher, and optional joint sliders.

## Can Isaac Sim use it directly?

The included USD and runner support inspected policy playback in Isaac Sim
6.0.1 on the recorded host. This does not mean a native Isaac Lab training task
exists.

## Can ROS control Isaac or the real robot?

No. There is currently no ROS-to-Isaac bridge, `ros2_control` stack, hardware
driver, or servo calibration in this project.

## Why are there 14 joints instead of 15 actuators?

The released MJCF and policies define 14 movable joints. A mouth actuator is
mentioned by the physical runtime but absent from this simulation/policy
contract, so its behavior is not guessed.

## Are the inertia and model poses verified?

All 15 physical inertia matrices are positive definite, total mass agrees
across source/ROS/Isaac, and 109 source-to-ROS pose matrices pass the recorded
tolerance. This validates conversion consistency, not independent measurement
of manufactured hardware.

## Why do MuJoCo and Isaac walk differently?

They use different contacts and actuator models. Both recorded runs stay finite
and upright, but trajectory parity is explicitly not claimed.

## Can I use the assets commercially?

Do not assume so. Upstream labels the 3D files “Creative Commons BY-SA-NC” but
does not provide a version. Read [licensing](/project/licensing) and ask Pollen
Robotics for clarification when commercial, sponsored, or monetized use matters.
