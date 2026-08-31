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
        `-- Isaac 61 -> 14 playback
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

## Deliberate separation

ROS currently describes and visualizes the robot. Isaac directly replays the
policy. There is no hidden ROS bridge between them, and neither path is a
physical robot driver. This separation keeps every claimed layer independently
testable.
