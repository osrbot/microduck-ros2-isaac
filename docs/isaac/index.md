# Open MicroDuck in Isaac Sim

The repository includes a converted MicroDuck USD. You can open it before
setting up policy playback. No conversion is required.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Time</span><strong>8–15 minutes</strong></div>
  <div role="listitem"><span>Environment</span><strong>Isaac Sim</strong></div>
  <div role="listitem"><span>Policies</span><strong>Not required</strong></div>
  <div role="listitem"><span>Result</span><strong>USD loads and survives Play</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>This page checks only the model layer</strong>
  <ul>
    <li>locate the included top-level USD;</li>
    <li>open the complete stage in Isaac Sim;</li>
    <li>inspect appearance, articulation, and Play stability.</li>
  </ul>
</div>

<div class="md-command-steps">
  <strong>Check the file in Terminal before opening Isaac Sim</strong>
  <p>Press <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd> for terminal A and <code>cd</code> to the repository root. This catches a missing USD or payload before the GUI starts.</p>
</div>

<div class="md-step-kicker"><span>STEP 1</span><strong>Terminal A · repository root</strong></div>

## 1. Find the USD

From the repository root, the main stage is:

```text
assets/isaac/robot_allcollisions/robot_allcollisions.usda
```

Keep the whole `robot_allcollisions` directory together. The main file loads
geometry and materials from the neighboring `payloads/` directory.

```bash
test -f assets/isaac/robot_allcollisions/robot_allcollisions.usda \
  && test -d assets/isaac/robot_allcollisions/payloads \
  && echo "MicroDuck USD: OK"
```

Press <kbd>Enter</kbd>. The command should immediately print
`MicroDuck USD: OK` and return to the prompt. No output means at least one path
is missing, often because the terminal is not at the repository root.

<div class="md-result-label">USD RENDER PREVIEW · CHECK THE APPEARANCE</div>

<figure class="md-doc-figure md-usd-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-usd-preview.webp" alt="Three-quarter rendered preview of the MicroDuck USD included in this repository" width="1200" height="800" loading="lazy"></div>
  <figcaption><strong>Rendered from the included USD.</strong> Use this preview to identify the model before opening Isaac Sim.</figcaption>
</figure>

<div class="md-step-kicker"><span>STEP 2</span><strong>Isaac Sim window</strong></div>

## Open the USD

1. Start Isaac Sim.
2. Choose **File → Open**.
3. Select `robot_allcollisions.usda`.
4. Wait for the stage and materials to finish loading.
5. Press **Play** if you want to check that the articulation stays in the scene.

For a standalone install, open Isaac Sim from its application entry or launcher.
Launch commands differ between releases, so this step does not ask you to guess
an install path. In the file picker, use <kbd>Ctrl</kbd>+<kbd>L</kbd> to enter a
full path or browse from the repository folder.

## Expected result

- MicroDuck appears as one complete robot rather than loose mesh files.
- The Stage tree contains the robot body and its joints.
- The head, body, legs, and feet are visible.
- Pressing **Play** does not immediately remove or explode the robot.

Wait until the loading indicator finishes. A temporarily gray material is normal
while assets load; a red asset error, detached body, or disappearance after
**Play** is not.

<div class="md-result-label">REAL UI REFERENCE · VIEWPORT AND STAGE</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="MicroDuck, the viewport, and the Stage tree in a real Isaac Lab run" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>Use the center viewport and the Stage tree on the right.</strong>This real screenshot comes from this repository's multi-skill playground, not the no-policy open step above, but the panels and checks are the same. After opening the top-level USD, confirm the complete duck in the viewport and a clean robot hierarchy in Stage.</figcaption>
</figure>

<div class="md-checkpoint">
  <strong>Model-layer check passed</strong>
  <p>The stage hierarchy, appearance, and articulation are intact after <strong>Play</strong>. No policy or training has run yet.</p>
</div>

Opening the stage is enough for viewing and screenshots. Next, run
[one walking policy](./policy-playback), open the
[multi-skill playground](./playground), or start
[native Isaac Lab training](./training).

## The model does not appear

- Make sure you opened the top-level `.usda`, not a file inside `payloads/`.
- Keep the repository directory structure unchanged.
- Check the Isaac Sim console for a missing relative asset path.
- If the viewport is blank, frame the selected robot with <kbd>F</kbd>.

::: details For contributors: rebuild the USD from the upstream MJCF
The included USD is ready for the tutorial. Rebuild it only when changing the
source model or conversion code:

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/convert_mjcf_to_usd.sh
```

The script converts the model, applies the project collision adjustment, and
updates the asset under `assets/isaac/`.
:::

<div class="md-page-complete">
  <strong>The USD is stable.</strong>
  <p>Run one walking policy next for the easiest runtime check, or open the playground if your policy environment already works.</p>
</div>

<div class="md-next-grid">
  <a class="md-next-card" href="/microduck-ros2-isaac/isaac/policy-playback"><span>RECOMMENDED NEXT</span><strong>Replay one walking policy →</strong><p>Check ONNX, physics, progress output, and the follow camera.</p></a>
  <a class="md-next-card" href="/microduck-ros2-isaac/isaac/playground"><span>ALREADY FAMILIAR</span><strong>Open the multi-skill playground →</strong><p>Walk, sit, kick, ground-pick, and roll.</p></a>
</div>
