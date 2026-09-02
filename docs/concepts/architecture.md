# Architecture

This project is an independent compatibility and teaching layer around pinned
Pollen Robotics inputs. Generated ROS and Isaac files are outputs, not new
authoritative robot specifications.

```text
pinned microduck_rl MJCF
        |-- MuJoCo inventory and reference rollouts
        |-- generated Xacro + copied meshes --> ROS 2 / TF / RViz
        `-- Isaac MJCF importer --> collision correction --> validated USD

pinned microduck policies
        |-- MuJoCo 61 -> 14 playback
        `-- Isaac skill playground <--> localhost UDP <--> ROS 2 / RViz

validated MicroDuck USD
        `-- native Isaac Lab task --> RSL-RL PPO --> new checkpoint
```

## Reproducible source layer

`upstream.lock` records immutable commits. `scripts/fetch_upstream.sh` checks
them out below ignored `reference/` directories. This separates source identity
from generated files and prevents a moving branch from silently changing a
demonstration.

## ROS description layer

The generator preserves all 15 physical MJCF bodies, their inertias, 14 hinges,
and referenced geometry. A massless `base_link` is added above `trunk_base` so
KDL can consume the tree without discarding or moving the physical trunk
inertia. Quaternion poses are converted through rotation matrices, including
the source's exact ±90° pitch singularities.

## Isaac layer

Isaac Lab's MJCF importer produces the stage. The project changes only the
collision state required to restore one source filtering intent, then checks
the complete stage against recorded invariants.

## Policy adapter layer

Both runners use the same 61-value observation order, 14-value output order,
home pose, command layout, 200 Hz physics step, and 50 Hz policy cadence. Each
engine still retains its own contact and actuator behavior.

## Training and ROS interaction layer

The native Isaac Lab task reuses the USD and 61→14 contract, then adds parallel
environments, rewards, resets, randomization, curriculum, and RSL-RL PPO. The
ROS bridge stays outside Isaac's Python environment and exchanges localhost UDP
commands and telemetry before publishing JointState, policy state, and TF.

## Deliberate separation

ROS description, the ROS bridge, released-policy playback, and new-policy
training remain separate layers. The bridge controls simulation only, and a
training checkpoint does not automatically become a hardware policy. Each
claim remains independently testable.
