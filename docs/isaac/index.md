# Open MicroDuck in Isaac Sim

The ready-to-open MicroDuck USD is already here. You can open it before setting
up any policy. You do not need to convert anything.

Want a look at what comes later? The [continuous-roll case study](./continuous-roll) starts with the full motion video, then covers setup, training, parameters, and debugging. If you are new to Isaac, open the model with this page first.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Time</span><strong>8–15 minutes</strong></div>
  <div role="listitem"><span>Environment</span><strong>Isaac Sim</strong></div>
  <div role="listitem"><span>Policies</span><strong>Not required</strong></div>
  <div role="listitem"><span>Result</span><strong>USD opens and stays put when you press Play</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>You will check the model</strong>
  <ul>
    <li>locate the included top-level USD;</li>
    <li>open the complete stage in Isaac Sim;</li>
    <li>inspect appearance, articulation, and Play stability.</li>
  </ul>
</div>

<div class="md-command-steps">
  <strong>Check the file first</strong>
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

<div class="md-result-label">QUICK LOOK · THIS IS THE DUCK</div>

<figure class="md-doc-figure md-usd-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-usd-preview.webp" alt="Three-quarter rendered preview of the MicroDuck USD included in this repository" width="1200" height="800" loading="lazy"></div>
  <figcaption><strong>This picture comes from the included USD.</strong>Use it to check that you opened the right model.</figcaption>
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

## What you should see

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
  <figcaption><strong>Look at the center view and the Stage tree on the right.</strong>This real picture comes from the skill playground, but the panels are the same. You should see one full duck and no broken links in the Stage tree.</figcaption>
</figure>

<div class="md-checkpoint">
  <strong>The model looks good!</strong>
  <p>The stage hierarchy, appearance, and articulation are intact after <strong>Play</strong>. No policy or training has run yet.</p>
</div>

Opening the stage is enough for viewing and screenshots. Follow the next page
to run one walking policy before you open the multi-skill playground.

## The model does not appear

- Make sure you opened the top-level `.usda`, not a file inside `payloads/`.
- Keep the repository directory structure unchanged.
- Check the Isaac Sim console for a missing relative asset path.
- If the viewport is blank, frame the selected robot with <kbd>F</kbd>.

<div class="md-page-complete">
  <strong>The duck is standing. Now make it move!</strong>
  <p>The next page runs one walking policy. It is the quickest way to check that Isaac, ONNX Runtime, and the model work together.</p>
</div>
