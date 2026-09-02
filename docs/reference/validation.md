# How this project was tested

The project keeps evidence levels separate. A later level cannot retroactively
prove an earlier contract, and a GUI screenshot cannot replace structural or
runtime checks.

| Level | What is checked | Status in recorded matrix |
| --- | --- | --- |
| Source identity | Immutable upstream revisions | Passed |
| MJCF structure | Bodies, joints, sensors, actuators, policy shapes | Passed |
| MuJoCo runtime | Released standing and walking policies | Passed |
| USD structure | Units, bodies, joints, mass, collisions | Passed |
| Isaac runtime | 61-to-14 adapter and ONNX execution | Passed |
| Skill playground | Policy loading, switching, and finite playback | Passed |
| Native training smoke | Task registration, parallel envs, PPO update, checkpoint | Passed |
| Behavioral smoke parity | Finite/upright runs with matching command and timing | Passed |
| ROS package/runtime | Generation, pose parity, build, launch, JointState, TF | Passed |
| ROS-to-Isaac bridge | Limits plus live ROS → Isaac → ROS policy/state round trip | Passed |
| GUI interaction/stability | RViz input and bounded Isaac Kit run | Passed on one host |
| Final production demo | Human visual approval and capture rehearsal | Not yet accepted |
| Hardware | Real robot and fifteenth mouth actuator | Not tested |

## Run the headless suite

```bash
./scripts/validate_all.sh
```

The thirteen stages check sources and environment, pure-Python contracts, MuJoCo
baselines, USD conversion, Isaac single- and multi-policy playback, native
training smoke, cross-engine comparison, ROS packages, description runtime,
the bridge protocol, and a live ROS-to-Isaac playground round trip.

## Fixed numerical contracts

- Physics timestep: 0.005 s; policy decimation: 4; control rate: 50 Hz.
- Policy input: `obs[1,61]`; output: `actions[1,14]`.
- Walking scale: 0.9; standing scale: 1.0.
- Source-to-ROS pose comparison: 109 transforms with `1e-9` rotation tolerance.
- The mouth actuator is outside the selected MJCF/ONNX contract.

See [recorded results](./results) for actual values and retained artifact names.
