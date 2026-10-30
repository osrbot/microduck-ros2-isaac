# FAQ

Quick answers for the questions that usually come up on a first run.

## What can I do with this project today?

- Open the complete MicroDuck model in RViz and move all 14 joints.
- Run ready-made ROS 2 motion examples.
- Open the included USD in Isaac Sim.
- Play released walking and skill policies.
- Train flat-ground walking in Isaac Lab and practice tuning with the [continuous-roll case study](/isaac/continuous-roll).
- Try recovery and turning in MuJoCo, or [download a model and continue training](/guide/training-checkpoints).
- Send commands from ROS 2 to the local Isaac playground and see the pose in RViz.

## What can it not do yet?

- It does not control a physical MicroDuck. There is no `ros2_control`, servo
  driver, calibration, or hardware safety setup here.
- An Isaac checkpoint cannot go straight onto a real robot.
- Isaac and MuJoCo do not produce the same path. Their contacts and actuator
  models are different.
- The physical mouth actuator is not part of the released simulation model or
  policies.

## Do I need ROS 2 and Isaac Sim together?

No. Start with ROS 2 if you only want RViz, joints, and the motion examples.
Install Isaac Sim only when you want physics, policies, the playground, or
training. The ROS-to-Isaac bridge is an optional later step.

## Does the repository already include URDF, USD, and a ROS 2 package?

Yes. `microduck_description` provides the ROS robot description, meshes,
inertias, TF/RViz launch, home pose, and joint sliders. The generated Isaac USD
is also included. First-time users do not need to convert either model.

## Can Isaac Sim use the model directly?

Yes. Open the included top-level USD to inspect the model. Use the ready-made
runners for one-policy playback or the keyboard playground. Training a new
checkpoint is a separate Isaac Lab route.

## Why are there 14 joints instead of 15 actuators?

The released MJCF and policies contain 14 movable joints. The physical runtime
mentions a mouth actuator, but the public simulation model does not define its
geometry, limits, or policy behavior.

## Where do the mass and inertia values come from?

The values come from upstream MJCF. Conversion checks compare mass, inertia,
and poses to confirm that ROS and Isaac models preserve the source data. This
project has not independently measured these values on physical hardware.

## Can I use the assets commercially?

Model meshes use **CC BY-NC-SA 4.0**, which includes a non-commercial restriction.
MJCF descriptions and this project's original code use **Apache-2.0**. See
[licensing](/project/licensing) for the file scope, and confirm permission with
Pollen Robotics for commercial, sponsored, or monetized use of the meshes.

## Something broke. Where do I start?

Use [Troubleshooting](/troubleshooting). It starts with the exact symptom —
missing RViz parts, a missing command, an Isaac crash, or a policy that will not
load — so you do not have to read the whole site again.
