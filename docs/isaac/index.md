# Open MicroDuck in Isaac Sim

The repository includes a converted MicroDuck USD. You can open it before
setting up policy playback. No conversion is required.

## 1. Find the USD

From the repository root, the main stage is:

```text
assets/isaac/robot_allcollisions/robot_allcollisions.usda
```

Keep the whole `robot_allcollisions` directory together. The main file loads
geometry and materials from the neighboring `payloads/` directory.

<figure class="md-doc-figure md-usd-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-usd-preview.webp" alt="Three-quarter rendered preview of the MicroDuck USD included in this repository" width="1200" height="800" loading="lazy"></div>
  <figcaption><strong>Rendered from the included USD.</strong> Use this preview to identify the model before opening Isaac Sim.</figcaption>
</figure>

## 2. Open the USD

1. Start Isaac Sim.
2. Choose **File → Open**.
3. Select `robot_allcollisions.usda`.
4. Wait for the stage and materials to finish loading.
5. Press **Play** if you want to check that the articulation stays in the scene.

## Expected result

- MicroDuck appears as one complete robot rather than loose mesh files.
- The Stage tree contains the robot body and its joints.
- The head, body, legs, and feet are visible.
- Pressing **Play** does not immediately remove or explode the robot.

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
