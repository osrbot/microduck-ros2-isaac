# How this project was tested

Check model files, simulation, training, and ROS communication in turn, saving
a separate report for each. Prepare the [Linux, ROS, and Isaac environment](./environment)
before running the full suite.

The table below describes the historical matrix. The [October alignment](./upstream-alignment)
has separate local-only evidence; new-source Isaac and ROS runtime checks are pending.

| Level | What is checked | Status in recorded matrix |
| --- | --- | --- |
| Source identity | Immutable upstream revisions | Passed |
| MJCF structure | Bodies, joints, sensors, actuators, policy shapes | Passed |
| MuJoCo runtime | Released standing and walking policies | Passed |
| USD structure | Units, bodies, joints, mass, collisions | Passed |
| Isaac runtime | 61-to-14 adapter and ONNX execution | Passed |
| Skill playground | Policy loading, switching, and finite playback | Passed |
| Short training run | Task registration, parallel envs, PPO update, checkpoint | Passed |
| Cross-engine short playback | Finite/upright runs with matching command and timing | Passed |
| ROS package/runtime | Generation, pose parity, build, launch, JointState, TF | Passed |
| ROS-to-Isaac bridge | Limits plus live ROS → Isaac → ROS policy/state round trip | Passed |
| GUI interaction/stability | RViz input and bounded Isaac Kit run | Passed on one host |
| Final production demo | Human visual approval and capture rehearsal | Not yet accepted |
| Hardware | Real robot and fifteenth mouth actuator | Not tested |

## Run the headless suite

```bash
./scripts/validate_all.sh
```

The thirteen stages check sources and environment, Python interfaces, MuJoCo
baselines, USD conversion, Isaac single- and multi-policy playback, short
training, cross-engine comparison, ROS packages, description runtime,
the bridge protocol, and a live ROS-to-Isaac playground round trip.
It starts a short training run and needs an available Linux GPU/ROS host.
The converter now writes a separate ground-contact candidate and refuses to
overwrite it; archive an existing candidate before a deliberate regeneration.
Native training and the later ROS bridge stages still use the historical USD.

## Numerical settings and interfaces

- Physics timestep: 0.005 s; policy decimation: 4; control rate: 50 Hz.
- Policy input: `obs[1,61]`; output: `actions[1,14]`.
- Walking scale: 0.9; standing scale: 1.0.
- Source-to-ROS pose comparison: 109 transforms with `1e-9` rotation tolerance.
- The selected MJCF and ONNX models do not include the mouth actuator.

See [recorded results](./results) for actual values and retained artifact names.
