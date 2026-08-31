# Recorded results

Validation date: 2026-08-31 (Asia/Shanghai). JSON files below `artifacts/` are
the machine-readable evidence; this page is the human summary.

## Inputs and structure

- `microduck_rl`: `d424a0c899f6b33cbd3daeb279913134349c0b63`
- `microduck`: `590b986bd8c0d50ae02cb3ea2f59c463b6828168`
- Nine released policies: input width 61, output width 14.
- Physical model mass: approximately 0.737243 kg.
- 15 physical bodies and 14 movable joints.

## Policy rollouts

| Engine and scenario | Duration | Final root xyz (m) | Max tilt | Result |
| --- | ---: | --- | ---: | --- |
| MuJoCo walk, `vx=0.3`, scale 0.9 | 10 s | `[1.151052, -0.217529, 0.117609]` | 0.063937 rad | finite, upright |
| Isaac stand, scale 1.0 | 5 s | `[0.001080, -0.000970, 0.116149]` | 0.022275 rad | finite, upright |
| Isaac walk, `vx=0.3`, scale 0.9 | 10 s | `[1.481570, 0.412802, 0.118544]` | 0.068429 rad | finite, upright |
| Isaac Kit walk, same command | 60 s | `[-0.086344, 6.222491, 0.120011]` | 0.068429 rad | finite, upright, clean exit |

The matched 10-second walks pass behavioral smoke checks: timing, command, and
scale match; both runs remain finite and upright. Final height differs by
0.000935 m and maximum tilt by 0.004493 rad.

Forward displacement differs by about 28.7%, and lateral drift differs in both
magnitude and direction. Therefore these numbers explicitly reject a claim of
trajectory parity. Isaac uses PhysX contacts and a simplified implicit-PD
actuator; the upstream training stack uses MuJoCo and a detailed BAM XL330
model.

## Generated USD

- 15 rigid bodies and 14 revolute joints.
- 81 mesh instances with collision API.
- 10 enabled collision meshes.
- 70 visual meshes plus one source sensor mesh have collision disabled.
- Units, axes, limits, articulation root, total mass, and names pass inspection.

## ROS 2 description

- Massless `base_link`, 15 physical links, one fixed root joint, 14 revolute joints.
- 70 visual instances, 10 collision instances, 38 unique mesh files.
- About 796,792 visual triangles; optional collision geometry adds about 171,146.
- All 15 physical inertia matrices are positive definite.
- 109 pose matrices compared: translation error 0 m; maximum rotation-matrix
  error `4.90e-12` against a `1e-9` tolerance.
- Xacro expansion, `check_urdf`, colcon build, and 5/5 ament tests passed.
- Runtime validation received the required nodes, description, home joint state,
  and `world -> ankle_left` TF.

## GUI evidence

RViz ran fullscreen for 75 seconds on the validated host. Automated input
confirmed default Orbit rotation and zoom. The joint GUI changed all 14 joints,
TF changed, and the rendered robot changed. A quaternion singularity defect that
made neck and leg meshes look detached was corrected and is guarded by the
109-pose comparison.

The first 60-second Isaac Kit run reproduced a duplicate-Vulkan-ICD GPU crash.
With the project wrapper selecting one ICD and disabling multi-GPU rendering,
the same simulation finished, exited 0, and created no new GPU dump.

These results do not establish native training parity, hardware behavior, or
final livestream/capture acceptance.
