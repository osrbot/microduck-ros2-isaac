# Contributing

Use this page when changing repository code. For a first run, start with the
[tutorial](/guide/). Run the commands below from the project root.

## Before you change code

1. Read [architecture](/concepts/architecture) and [licensing](./licensing).
2. Keep upstream revisions pinned. Change `upstream.lock` only in a focused
   compatibility update.
3. Do not commit downloaded policies, local environments, logs, credentials, or
   machine-specific paths.
4. Keep attribution with every derived model asset.

## Run the checks that match your change

- Documentation: `npm ci && npm run docs:build`.
- ROS generation: regenerate the description, then build and open it in RViz.
- Isaac asset: regenerate the USD, inspect the stage, then run one policy.
- Policy adapter: run the standing and walking checks.
- Hardware work: document it separately from simulation results.

When a change crosses several areas, run the complete headless suite:

```bash
./scripts/validate_all.sh
```

## Regenerate the ROS 2 description

Run this only after changing the upstream model or ROS generator:

```bash
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
./scripts/generate_ros_description.py
./scripts/validate_ros2_package.sh
```

Then rebuild `microduck_description` and reopen RViz.

## Regenerate the Isaac USD

Run this only after changing the source model or conversion code:

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/convert_mjcf_to_usd.sh
```

The converter writes the candidate to `assets/isaac/robot_groundcontact/` and
applies the collision adjustment. It stops if that directory already exists;
archive an existing candidate before regenerating it. Open the top-level USD
and replay a policy before submitting the change.

## Tell us what you tested

In a pull request, list the changes, commands, and test results, including any
untested parts. Record software versions so others can compare their setup with
the [tested environment](/reference/environment).
