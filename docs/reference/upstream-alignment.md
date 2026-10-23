# Upstream alignment — October 2026

The source lock, official-policy downloader and ROS description have been updated.
Local MuJoCo and structural checks pass. **The new Isaac conversion and ROS/RViz
runtime have not been retested.** The bundled Isaac USD, native training model
and historical results remain separate; circus work is unchanged.

::: tip 2026-10-20 addition: learn about v8 without switching defaults
Upstream has released VelStand v8 with improved recovery and turning.
The new [optional guide](../guide/velstand-v8) covers training changes, parameter rationale,
two-stage resume and evaluation prerequisites. The version table and October 10 evidence below
retain their original meaning; `upstream.lock` and default policies are unchanged.
Upstream v8 results are not included in this project's acceptance record.
:::

## 1. Which versions are selected? {#versions}

| Input | Immutable version | Location |
| --- | --- | --- |
| MicroDuck RL | [`ceca01706143`](https://github.com/pollen-robotics/microduck_rl/commit/ceca01706143d729305baa94cbd8ab990979e325) | `reference/microduck_rl/` |
| MicroDuck runtime | [`dec725c67ffb`](https://github.com/pollen-robotics/microduck/commit/dec725c67ffbbdde7f1de30f8c936b1bf9c1d70e) | `reference/microduck_runtime/` |
| Official policy set v7 | [`6677ec007142`](https://huggingface.co/pollen-robotics/microduck-policies/commit/6677ec007142bbaf05123a468f6ae58d13808786) | `reference/policies/v7/` |
| Playground's historical sit/stand policy | [`590b986bd8c0`](https://github.com/pollen-robotics/microduck/commit/590b986bd8c0d50ae02cb3ea2f59c463b6828168) | `reference/policies/isaac-legacy/` |
| Bundled historical Isaac USD | [`d424a0c899f6`](https://github.com/pollen-robotics/microduck_rl/commit/d424a0c899f6b33cbd3daeb279913134349c0b63) | `assets/isaac/robot_allcollisions/` |

The table abbreviates commit IDs; `upstream.lock` records the full revisions and each downloaded file's SHA-256.
The downloader refuses dirty reference checkouts and mismatched existing policy
files. Keep any local modifications before retrying; do not delete them to make
a check pass. An existing `reference/microduck/` snapshot is left untouched.

```bash
./scripts/fetch_upstream.sh
```

The fetch script uses Python 3.11+ and downloads the ten v7 ONNX files, their manifest
and model card, plus the historical sit/stand weight used by the playground.
All 13 files are hash-checked. The runtime checkout is a source reference: this does **not**
install a physical-robot daemon, flash firmware, or upgrade Isaac Lab.

## 2. Start with the ROS description {#ros-description}

The checked-in Xacro and 38 STL files now come from the selected October model.
Build and launch using the [ROS 2 tutorial](../ros2/); there is no extra upstream
download requirement for that route. The 14-joint interface is unchanged.
On Humble, keep omitting `rviz_fullscreen:=true` and maximize RViz manually.

For maintainers who regenerate the description:

```bash
python3 scripts/generate_ros_description.py
python3 scripts/validate_ros_mjcf_pose_parity.py
```

The conversion source is now **`robot_groundcontact.xml`**. That model succeeds
the old selectively colliding `robot_allcollisions.xml`. The new upstream file
with the old name has full collision geometry and is not an interchangeable
input. Both are still 14-action models; downloading the current runtime does
not add a controlled mouth joint to this ROS/ONNX contract.

## 3. Check policies without Isaac {#policy-probe}

The isolated environment uses Python 3.12, MuJoCo 3.10.0, ONNX Runtime 1.24.4 and
NumPy 2.4.1. `setup_mujoco_env.sh` uses `uv` when available, otherwise a local
`python3.12 -m venv` and pip. It does not replace system Python.

```bash
./scripts/setup_mujoco_env.sh
MICRODUCK_BASELINE_DIR="$PWD/artifacts/upstream-alignment/20261010" \
  ./scripts/run_official_baseline.sh
work/mujoco_env/bin/python scripts/run_mujoco_baseline.py \
  --policy reference/policies/v7/velstand.onnx \
  --duration 10 --vx 0.3 --action-scale 0.9 \
  --output artifacts/upstream-alignment/20261010/velstand_groundcontact_probe.json
```

The last command is a **flat-ground compatibility probe** in the simplified
ground-contact model, not a reproduction of v7's Rough + Backlash training
environment. It does not test falling, getting up, body tilt, or a physical robot.
Upstream documents standing roll/pitch control and still lists body-height and
slow-turn limitations in its [VelStand notes](https://github.com/pollen-robotics/microduck_rl/blob/ceca01706143d729305baa94cbd8ab990979e325/docs/velstand_policy.md).

## 4. What changes in the Isaac tutorial? {#isaac-path}

- Default walking/standing remain `alpha_walking`/`alpha_stand`. Their v7 files
  match the recorded baseline hashes; the download location has changed.
- The playground keeps its historical `alpha_sitstand` under `reference/policies/isaac-legacy/`.
  The downloader fetches this weight separately from its original immutable source.
  All seven default playground weights therefore match the historical hashes.
  The updated v7 sitting policy still needs fresh Isaac motion and transition checks.
- `velstand` is downloaded but is not silently substituted for the playground's
  two-policy controller. That controller retains the historical switching and
  scaling profile; a filename swap is not a full current-runtime port.
- `roulade.onnx` is byte-identical to the historical case-study input. Its
  tutorial path is updated, but the saved rolling results and USD are unchanged.

On an available, verified Linux/Isaac host, the next conversion gate is:

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/convert_mjcf_to_usd.sh
./scripts/run_isaac_policy.sh \
  --usd assets/isaac/robot_groundcontact/robot_groundcontact.usda \
  --policy reference/policies/v7/alpha_stand.onnx \
  --duration 5 --action-scale 1.0 \
  --output artifacts/isaac/groundcontact/stand.json
```

Only after that candidate passes standing and walking checks, maintainers can
explicitly try the updated sitting policy. This is an **unvalidated experiment**,
not the beginner launch command:

```bash
./scripts/run_isaac_playground.sh \
  --usd assets/isaac/robot_groundcontact/robot_groundcontact.usda \
  --sitstand-policy reference/policies/v7/alpha_sitstand.onnx \
  --follow-camera --viz kit
```

The converter writes a separate `robot_groundcontact/` candidate and refuses
to overwrite an existing candidate. It never replaces the historical USD.
Conversion/structure checks alone do not promote the candidate into native
training or validate the updated sitting/standing transitions.

## 5. Evidence from 2026-10-10 {#evidence}

| Check | Local result |
| --- | --- |
| Immutable source pins and 12 download hashes | Verified |
| Historical sit/stand download and seven default playground hashes | Match the historical baseline |
| Ten ONNX networks | All declare 61 inputs and 14 outputs |
| Generated ROS description | 15 physical links + massless root; 14 movable joints; all meshes resolve |
| MJCF-to-ROS transforms | 109 checked; max matrix error `4.90e-12` |
| `alpha_stand`, 5 s | Finite, upright at the end |
| `alpha_walking`, 10 s, vx 0.3 | Finite, upright at the end; final xy about `[1.156, -0.214]` m |
| `velstand`, 10 s, vx 0.3 | Finite, upright at the end; final xy about `[1.189, -0.101]` m |
| Historical USD | Structural checks still pass; file contents unchanged |
| New USD / PhysX playback / ROS GUI | Not run in this update |

Reports are under `artifacts/upstream-alignment/20261010/`. These short,
deterministic probes are not a robustness score or proof of speed tracking.
The [older results](./results) retain their own dates and source revisions.
See [licensing](../project/licensing) for the clarified split between mesh and
XML/code licenses. Publishing these notes does not imply that the pending runtime
checks or any new training have been completed.
