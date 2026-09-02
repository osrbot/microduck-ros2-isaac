# Make MicroDuck walk in Isaac Sim

This page requires Isaac Sim and Isaac Lab. The setup below downloads the
released policy files and installs ONNX Runtime inside the project.

## 1. Prepare the policy runner

From the repository root:

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

You can omit `ISAACLAB_DIR` when Isaac Lab is at the default
`~/rlgpu_ws/IsaacLab` path.

## 2. Run the walking policy

Run this from a graphical Linux desktop:

```bash
./scripts/run_isaac_policy.sh \
  --duration 60 \
  --vx 0.3 \
  --action-scale 0.9 \
  --follow-camera \
  --viz kit
```

Isaac Sim should open, place MicroDuck on the ground, and run the walking policy
while the camera follows the robot. The simulation may run slower than real
time; the terminal prints progress every five simulated seconds.

## Run the standing policy

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_stand.onnx \
  --duration 30 \
  --action-scale 1.0 \
  --follow-camera \
  --viz kit
```

## Run a headless test

Use this for a quick terminal check:

```bash
./scripts/run_isaac_policy.sh \
  --duration 10 \
  --vx 0.3 \
  --action-scale 0.9 \
  --headless
```

The run writes a small JSON summary to `artifacts/isaac/policy_rollout.json`.
You do not need to read that file for the tutorial unless you are debugging a
problem.

## Isaac Sim crashes during playback

- Start the policy through `run_isaac_policy.sh`, not by calling the Python file
  directly. The wrapper selects a single NVIDIA Vulkan device when needed.
- Close other Isaac Sim windows before starting another run.
- Check that the NVIDIA driver, Vulkan, and Isaac Sim itself work with a simple
  empty stage.
- Try the headless command. If headless works but the GUI fails, the problem is
  likely in the rendering or desktop session rather than the policy.
- See [troubleshooting](/troubleshooting) for the GPU environment overrides.

::: details Advanced options
The wrapper normally uses `cuda:0`. Multi-GPU hosts can override the selected
devices when required:

```bash
export MICRODUCK_ISAAC_DEVICE=cuda:0
export MICRODUCK_VULKAN_ICD=/etc/vulkan/icd.d/nvidia_icd.json
export MICRODUCK_ISAAC_ACTIVE_GPU=0
```

The released policy reads 61 values and controls the 14 joints in the public
simulation model. Physics runs at 200 Hz and policy inference at 50 Hz. These
details matter when modifying the runner, but not for the first playback.
:::

Once one duck walks cleanly, open the [multi-skill playground](./playground) for
sitting, ground pick, kicks, and a roll. To create a new checkpoint instead of
replaying one, continue with [Isaac Lab training](./training).
