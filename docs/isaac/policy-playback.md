# Replay ONNX policies

The runner reconstructs the released policy interface directly in Isaac Sim.
It is a policy-playback adapter, not a native Isaac Lab training environment.

## Headless standing smoke test

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_stand.onnx \
  --duration 5 \
  --action-scale 1.0 \
  --headless \
  --output artifacts/isaac/policy_stand_local.json
```

## Headless walking smoke test

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_walking.onnx \
  --duration 10 \
  --vx 0.3 \
  --action-scale 0.9 \
  --headless \
  --output artifacts/isaac/policy_walk_local.json
```

## Visual playback

Run this inside a graphical desktop session with `DISPLAY` available:

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_walking.onnx \
  --duration 60 \
  --vx 0.3 \
  --action-scale 0.9 \
  --follow-camera --viz kit
```

The wrapper selects one NVIDIA Vulkan ICD when duplicate manifests are present,
disables Kit multi-GPU rendering, and aligns the renderer GPU with the compute
device. Override only when your host requires it:

```bash
export MICRODUCK_ISAAC_DEVICE=cuda:0
export MICRODUCK_VULKAN_ICD=/etc/vulkan/icd.d/nvidia_icd.json
export MICRODUCK_ISAAC_ACTIVE_GPU=0
```

Kit GUI playback can be much slower than simulation time. Progress is printed
every five simulated seconds during long visual runs.

## Policy contract

| Observation block | Width |
| --- | ---: |
| Base angular velocity | 3 |
| Projected gravity | 3 |
| Joint position relative to home | 14 |
| Joint velocity | 14 |
| Previous raw action | 14 |
| Twist, head pose, and body-pose command | 13 |
| **Total** | **61** |

The 14-value output is mapped from policy joint order to Isaac joint order, then
applied as:

```text
target = official home pose + action scale * raw policy action
```

Physics runs at 200 Hz and inference at 50 Hz. The current Isaac actuator is a
simplified implicit-PD approximation, so the project claims finite/upright
behavioral smoke parity—not trajectory equality with MuJoCo.

## Interpret the output

Each run writes a JSON report with source paths, policy dimensions, command,
timing, root pose, maximum tilt, inference time, and finite/upright status. Keep
that file as evidence for the exact run; a video alone is not equivalent.
