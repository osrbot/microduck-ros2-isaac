# Choose your path

This repository supports two independent workflows built from the same pinned
MicroDuck sources. Start with the shortest path that matches your goal.

## I want to inspect the robot in ROS 2

Use the ROS 2 path when you need a kinematic description, TF tree, RViz model,
or interactive joint sliders. It does **not** require Isaac Sim.

1. Complete [installation](./installation).
2. [Build the ROS 2 package](/ros2/).
3. [Open and operate RViz](/ros2/rviz).

Expected result: a complete 15-body model in the official home pose, or an
articulated model controlled by 14 joint sliders.

## I want to run the released policy in Isaac Sim

Use the Isaac path when you need a validated USD articulation or want to replay
one of the released ONNX policies.

1. Complete [installation](./installation).
2. [Convert and inspect the USD](/isaac/).
3. [Replay a policy](/isaac/policy-playback).

Expected result: a 15-body, 14-joint articulation standing or walking under a
61-input, 14-output ONNX policy at 50 Hz.

## I want to reproduce every recorded check

After both environments are ready, run:

```bash
./scripts/validate_all.sh
```

This executes eight headless stages. It does not replace human GUI review,
livestream rehearsal, hardware testing, or native Isaac Lab training.

## Capability boundary

| Available now | Not provided yet |
| --- | --- |
| ROS 2 Jazzy description and RViz | Physical robot driver |
| Generated and inspected Isaac USD | ROS-to-Isaac control bridge |
| MuJoCo and Isaac policy playback | Native Isaac Lab training environment |
| Retained JSON validation evidence | Hardware calibration or safety limits |

Read [known limitations](/reference/limitations) before presenting results.
