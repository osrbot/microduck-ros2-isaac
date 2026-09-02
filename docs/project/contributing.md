# Contributing

This page is for people changing the repository. If you only want to use ROS 2
or Isaac Sim, follow the tutorial instead — you do not need any generator below.

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

The converter updates `assets/isaac/` and applies this project's collision
adjustment. Open the top-level USD and run a policy before you submit the change.

## Tell us what you tested

In a pull request, say what changed, which commands you ran, and what you did not
test. Detailed recorded setups and test data live under
[Contributor notes](/reference/environment); they are not part of the beginner
tutorial.
