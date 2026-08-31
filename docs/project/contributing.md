# Contributing

Contributions should make one evidence level stronger without blurring the
boundaries between source, conversion, simulation, GUI, and hardware.

## Before opening a change

1. Read [architecture](/concepts/architecture), [validation](/reference/validation),
   and [licensing](./licensing).
2. Keep upstream revisions pinned. Update `upstream.lock` only in a focused,
   reviewed compatibility change.
3. Do not add downloaded policies, local environments, logs, credentials, or
   machine-specific paths.
4. Preserve attribution for derived model assets.

## Validate proportionally

- Documentation: `npm ci && npm run docs:build`.
- ROS generation: generator, pose parity, package build, and runtime test.
- Isaac asset: conversion, post-process, and USD inventory.
- Policy adapter: standing/walking JSON plus cross-engine smoke comparison.
- GUI claim: record host versions and a bounded, repeatable interaction test.
- Hardware claim: keep it separate from simulation evidence and document the
  physical setup and safety boundary.

Run the complete headless suite when a change crosses layers:

```bash
./scripts/validate_all.sh
```

## Report results honestly

A pull request should state what changed, what ran, where evidence was written,
and what remains untested. “It opens” is not a substitute for structure; “it
walks once” is not training, trajectory, or hardware parity.
