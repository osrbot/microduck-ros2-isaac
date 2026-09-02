# FAQ

Quick answers for the questions that usually come up on a first run.

## What can I do with this project today?

- Open the complete MicroDuck model in RViz and move all 14 joints.
- Run ready-made ROS 2 motion examples.
- Open the included USD in Isaac Sim.
- Play released walking and skill policies.
- Train the included flat-velocity task in Isaac Lab.
- Send commands from ROS 2 to the local Isaac playground and see the pose in RViz.

## What can it not do yet?

- It does not control a physical MicroDuck. There is no `ros2_control`, servo
  driver, calibration, or hardware safety setup here.
- An Isaac checkpoint cannot go straight onto a real robot.
- Isaac and MuJoCo do not produce the same path. Their contacts and actuator
  models are different.
- The physical mouth actuator is not part of the released simulation model or
  policies, so this project does not invent one.

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

## Are the mass and inertia values checked?

The repository checks that the converted ROS and Isaac models agree with the
pinned source model. That catches broken conversion, but it is not an
independent measurement of a manufactured robot.

## Can I use the assets commercially?

Do not assume so. Upstream describes the 3D files as “Creative Commons BY-SA-NC”
without naming a version. Read [licensing](/project/licensing) and ask Pollen
Robotics before commercial, sponsored, or monetized use.

## Something broke. Where do I start?

Use [Troubleshooting](/troubleshooting). It starts with the exact symptom —
missing RViz parts, a missing command, an Isaac crash, or a policy that will not
load — so you do not have to read the whole site again.
