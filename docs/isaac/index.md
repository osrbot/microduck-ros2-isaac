# Create and inspect the Isaac USD

The Isaac workflow converts the pinned upstream MJCF with Isaac Lab's official
converter, applies one documented collision correction, and validates the
resulting stage before policy playback.

## Convert the model

```bash
export ISAACLAB_DIR=/path/to/IsaacLab  # omit when using the documented default
./scripts/setup_isaac_python_env.sh
./scripts/convert_mjcf_to_usd.sh
```

The canonical stage is written to:

```text
assets/isaac/robot_allcollisions/robot_allcollisions.usda
```

Conversion occurs in a temporary project work directory. A successful run
replaces the canonical generated asset atomically; a failed run restores the
previous asset and removes temporary conversion files.

## Why there is a post-process

The MJCF importer does not preserve the source `contype`/`conaffinity` filtering
semantics. Without correction, the `self_collision_only` power-support sensor
mesh can collide with the ground. `postprocess_isaac_usd.py` disables general
collision for that one source geometry and records the change.

## Inspect the contract

The conversion script runs `inspect_usd.py` automatically. The retained report
is `artifacts/isaac/usd_inventory.json` and enforces:

- stage units and axis convention;
- 15 rigid bodies and 14 revolute joints;
- articulation root, joint names, and limits;
- approximately 0.737243 kg total physical mass;
- 81 mesh instances, of which 10 collision meshes remain enabled;
- the documented collision correction.

You can repeat the inspection directly through the Isaac launcher:

```bash
"$ISAACLAB_DIR/isaaclab.sh" -p scripts/inspect_usd.py
```

## Open the stage

Open the canonical `.usda` in Isaac Sim for material and camera inspection. A
stage opening successfully is only a GUI check; use the structural report above
before claiming that body, joint, mass, or collision contracts are correct.

Continue with [ONNX policy playback](./policy-playback).
