# Generated model assets

`isaac/robot_allcollisions/` is generated from the pinned Pollen Robotics
`microduck_rl` MJCF by `scripts/convert_mjcf_to_usd.sh` with Isaac Sim 6.0.1 and
Isaac Lab 3.0.0 beta 2.

The conversion script uses a temporary directory, publishes only a validated
asset, disables the one source `self_collision_only` geometry that cannot be
represented faithfully by the importer's dropped MJCF masks, and removes
host-specific temporary paths from generated USD comments.

The asset is not hand-authored source of truth. Recreate it from the pinned
upstream model and verify it with `scripts/inspect_usd.py` after changing the
toolchain or source revision.

These files are derivatives of Pollen Robotics' 3D model. The upstream README
describes model files as "Creative Commons BY-SA-NC" without specifying a
version. See `NOTICE-MICRODUCK.md`; do not assume that the repository's
Apache-2.0 license overrides the model terms.
