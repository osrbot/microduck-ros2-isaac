# Architecture

This project converts Pollen Robotics' MicroDuck model for ROS 2 and Isaac,
then provides policy playback, training, and ROS communication tools. The
diagram shows how those parts connect.

```text
pinned microduck_rl MJCF
        |-- MuJoCo inventory and reference rollouts
        |-- generated Xacro + copied meshes --> ROS 2 / TF / RViz
        `-- Isaac MJCF importer --> collision correction --> validated USD

pinned Hugging Face microduck-policies
        |-- MuJoCo 61 -> 14 playback
        `-- Isaac skill playground <--> localhost UDP <--> ROS 2 / RViz

validated MicroDuck USD
        `-- native Isaac Lab task --> RSL-RL PPO --> new checkpoint
```

## Model and policy sources

`upstream.lock` records the selected commits. `scripts/fetch_upstream.sh`
downloads those revisions into `reference/`, so repeated tutorial runs use the
same inputs.
Runtime source and policy weights are separate inputs. The current runtime is
under `reference/microduck_runtime/`; default weights are under
`reference/policies/v7/` and checked by SHA-256. New conversion uses the ground-contact model
`robot_groundcontact.xml`. The bundled USD and native training keep their tested
model until a replacement passes runtime checks. See [model and source versions](../reference/upstream-alignment) for the exact revisions.

## ROS 2: model and joint display

The generator preserves all 15 physical MJCF bodies, their inertias, 14 hinges,
and referenced geometry. A massless `base_link` is added above `trunk_base` so
KDL can consume the tree without discarding or moving the physical trunk
inertia. Quaternion poses are converted through rotation matrices, including
the source's exact ±90° pitch singularities.

## Isaac: physics simulation

Isaac Lab's MJCF importer produces the USD. The conversion script disables an
extra sensor-mesh collision introduced during import, then checks units, joints,
mass, and collision settings.

## Policy playback: observations and actions

Both runners use the same 61-value observation order, 14-value output order,
home pose, command layout, 200 Hz physics step, and 50 Hz policy cadence. Each
engine still retains its own contact and actuator behavior.

## Training and ROS communication

The native Isaac Lab task reuses the USD and 61-input, 14-output interface, then adds parallel
environments, rewards, resets, randomization, curriculum, and RSL-RL PPO. The
ROS bridge stays outside Isaac's Python environment and exchanges localhost UDP
commands and telemetry before publishing JointState, policy state, and TF.

## Check each part

After conversion, check joints and inertias. After playback, check the motion.
After training, test the saved model. For ROS communication, check that commands
and states travel both ways. These tools currently connect simulation; physical
hardware still needs servo drivers, calibration, and hardware tests.
