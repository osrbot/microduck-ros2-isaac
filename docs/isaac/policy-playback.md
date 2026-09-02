# Make MicroDuck walk in Isaac Sim

This page requires Isaac Sim and Isaac Lab. The setup below downloads the
released policy files and installs ONNX Runtime inside the project.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Time</span><strong>15–25 minutes</strong></div>
  <div role="listitem"><span>Run from</span><strong>Repository root</strong></div>
  <div role="listitem"><span>Windows</span><strong>Terminal + Isaac Sim</strong></div>
  <div role="listitem"><span>Result</span><strong>Released policy and JSON report</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>This page will</strong>
  <ul>
    <li>prepare released policies and project-local ONNX Runtime;</li>
    <li>run the walking policy for 60 simulated seconds;</li>
    <li>finish with a 10-second headless check and saved report.</li>
  </ul>
</div>

<div class="md-command-steps">
  <strong>This page needs terminal A</strong>
  <p>Press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd> and <code>cd</code> to the repository root. Run GUI playback, the standing policy, and the headless check one after another. Wait for the current command to finish or stop it with <kbd>Ctrl</kbd>+<kbd>C</kbd> first.</p>
</div>

<div class="md-step-kicker"><span>STEP 1</span><strong>Terminal A · repository root</strong></div>

## 1. Prepare the policy runner

From the repository root:

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

You can omit `ISAACLAB_DIR` when Isaac Lab is at the default
`~/rlgpu_ws/IsaacLab` path.

<div class="md-checkpoint">
  <strong>Dependencies are ready</strong>
  <p>Released policies exist under <code>reference/microduck/</code>, and <code>work/isaac_python_pkgs/onnxruntime</code> exists. This setup is required only once.</p>
</div>

<div class="md-step-kicker"><span>STEP 2</span><strong>Keep the terminal open · GUI replay</strong></div>

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

After <kbd>Enter</kbd>, logs continue and the prompt does not return immediately.
The first Kit extension load may take several minutes. Do not start the same
command again while the first process is warming up.

Isaac Sim should open, place MicroDuck on the ground, and run the walking policy
while the camera follows the robot. The simulation may run slower than real
time; the terminal prints progress every five simulated seconds.

A line such as `Rollout progress: sim=5.0/60.0s` confirms that the control loop is advancing. Check that the robot is on
the ground, joints continue moving, the camera follows, and no traceback appears.

<div class="md-result-label">REAL RUN · WALKING POLICY ACTIVE</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-action-walk.webp" alt="MicroDuck replaying the released walking policy in Isaac Sim" width="1200" height="750" loading="lazy"></div>
  <figcaption><strong>The policy is in control.</strong> This is a real walking-policy playback. A stepping duck is not necessarily tracking a perfectly straight line; first confirm that simulation continues, the joints move normally, and the terminal stays free of errors.</figcaption>
</figure>

<div class="md-checkpoint">
  <strong>Walking replay passed</strong>
  <p>Progress reaches 60 simulated seconds and the process exits cleanly with a report. Stepping without perfectly straight tracking is a behavior-quality issue, not a loading failure.</p>
</div>

## Optional: run the standing policy

Wait for the 60-second run to finish. To stop early, press
<kbd>Ctrl</kbd>+<kbd>C</kbd> in terminal A and wait for the prompt before running:

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_stand.onnx \
  --duration 30 \
  --action-scale 1.0 \
  --follow-camera \
  --viz kit
```

<div class="md-step-kicker"><span>STEP 3</span><strong>Terminal · headless check</strong></div>

## Run a headless test

Make sure the GUI playback has exited, then use this quick terminal check:

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

```bash
test -s artifacts/isaac/policy_rollout.json \
  && echo "Policy rollout report: OK"
```

The final line must print `Policy rollout report: OK`. No output usually means
the previous headless run did not finish or did not write the file.

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

<div class="md-page-complete">
  <strong>Single-policy playback is complete.</strong>
  <p>You checked the released ONNX contract, Isaac physics loop, GUI playback, and a headless report. Continue with interactive skills or your own training task.</p>
</div>

<div class="md-next-grid">
  <a class="md-next-card" href="/microduck-ros2-isaac/isaac/playground"><span>KEEP PLAYING</span><strong>Open the multi-skill playground →</strong><p>Switch sit, ground pick, kick, and roll from the keyboard.</p></a>
  <a class="md-next-card" href="/microduck-ros2-isaac/isaac/training"><span>TRAIN NEXT</span><strong>Run the native Isaac Lab task →</strong><p>Go from five-iteration smoke to checkpoint replay.</p></a>
</div>
