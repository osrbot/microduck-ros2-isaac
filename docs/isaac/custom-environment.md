# Modify a training task

Start with one small change: make the existing walking task **practice slow forward motion only**. Find the configuration, change the velocity commands, run a short training check, and replay the result.
The final section shows where to extend the task with terrain, recovery poses, or a ball.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Goal</span><strong>Slow forward walking</strong></div>
  <div role="listitem"><span>Run from</span><strong>Linux repository root</strong></div>
  <div role="listitem"><span>Prerequisite</span><strong>Chapter 10 complete</strong></div>
  <div role="listitem"><span>Result</span><strong>Settings, model, replay report</strong></div>
</div>

> This example has been checked against the project source. The new settings still need GPU testing. Start with the short run below and check the saved configuration.

## 1. Back up the current configuration {#backup}

Stop any training or replay that uses this task. Open an Ubuntu terminal at the repository root and run:

```bash
custom_id=$(date +%Y%m%d-%H%M%S)
custom_run="$PWD/work/custom-velocity/$custom_id"
custom_evidence="$PWD/artifacts/custom-velocity/$custom_id"
custom_backup="$PWD/backups/custom-velocity/$custom_id"
cfg="$PWD/source/microduck_isaac_lab/microduck_isaac_lab/tasks/velocity/velocity_env_cfg.py"
test -f "$cfg" || exit 1
mkdir -p "$custom_run" "$custom_evidence" "$custom_backup"
cp "$cfg" "$custom_backup/velocity_env_cfg.py"
```

This creates directories for logs, replay output, and the original configuration. Keep using this terminal; the later commands reuse these variables.

## 2. Set slow forward velocity commands {#configure}

Open `source/microduck_isaac_lab/microduck_isaac_lab/tasks/velocity/velocity_env_cfg.py` in a text editor.
Find **`__post_init__()` in `MicroDuckVelocityFlatEnvCfg`**. Keep its existing settings and append the six command and curriculum assignments shown below.
The complete function should look like this. Edit the base class, above the `_PLAY` class at the end of the file.

```python
    def __post_init__(self) -> None:
        self.decimation = 4
        self.episode_length_s = 20.0
        self.sim.dt = 0.005
        self.sim.render_interval = self.decimation
        self.sim.physics_material = self.scene.terrain.physics_material
        self.scene.left_foot_contact.update_period = self.sim.dt
        self.scene.right_foot_contact.update_period = self.sim.dt

        self.commands.base_velocity.ranges.lin_vel_x = (0.1, 0.2)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (0.0, 0.0)
        self.commands.base_velocity.rel_standing_envs = 0.0
        self.commands.base_velocity.rel_turn_in_place_envs = 0.0
        self.curriculum.standing_fraction = None
```

| Setting | Why it changes |
| --- | --- |
| Forward speed `0.1–0.2 m/s` | Practice a narrow, low-speed range first; this range is chosen for the exercise |
| Lateral and turning speeds `0` | Request motion along the robot's forward direction |
| Standing and turn-in-place fractions `0` | Give every environment a forward command |
| `standing_fraction = None` | Disable the curriculum that would gradually add standing samples |

Keep the model, joint order, observations, rewards, and PPO settings. The `_PLAY` class inherits the base configuration, so replay uses the same velocity settings.
Forward is relative to the robot's current heading; initial headings are still randomized.

## 3. Check the edit {#check}

In the same terminal, run:

```bash
python3 - "$cfg" <<'PY'
import ast
from pathlib import Path
import sys
ast.parse(Path(sys.argv[1]).read_text())
print("Configuration syntax: OK")
PY
git diff -- "$cfg"
```

Look for `Configuration syntax: OK`. Inspect `git diff` and confirm that this exercise added only those six lines.
If the file already contained your own changes, compare with the backup from step 1 and preserve them.

## 4. Run a short training check {#train}

Use the Isaac Lab environment prepared in [chapter 10](./training). In the same terminal, run:

```bash
set -o pipefail
MICRODUCK_TRAIN_ENVS=64 MICRODUCK_TRAIN_ITERATIONS=5 \
  ./scripts/train_isaac_velocity.sh --headless \
  --log-root "$custom_run/logs" 2>&1 | tee "$custom_run/train.log"
```

The terminal should progress through environment creation, learning, and saving, then print `MICRODUCK_TRAIN_STAGE=complete`.
The model goes under `work/custom-velocity/<experiment time>/logs/<run time>/`.

Open that run's `params/env.yaml`. Check all three velocity ranges and the standing and turn-in-place fractions under `base_velocity`,
and confirm that `curriculum.standing_fraction` is disabled. The run should also contain `model_final.pt` and `training_summary.json`.
Five updates check configuration and saving. A stable gait requires further training and replay comparisons.

## 5. Replay this model {#replay}

After training exits, replace the first line with the actual absolute path to this run's `model_final.pt`:

```bash
checkpoint=/absolute/path/to/your/run/model_final.pt
test -f "$checkpoint" || exit 1
MICRODUCK_PLAY_STEPS=1000 \
MICRODUCK_PLAY_OUTPUT="$custom_evidence/playback.json" \
MICRODUCK_PLAY_SCREENSHOT="$custom_evidence/playback.png" \
  ./scripts/play_isaac_velocity.sh --checkpoint "$checkpoint"
```

Replay runs for 1000 control steps, about 20 simulated seconds. Check that:

- the model loads without NaN or shape errors;
- the duck attempts to step forward, and note persistent sidestepping, circling, or falls;
- `playback.json` and `playback.png` are written.

Keep the six settings and existing rewards fixed at first. Increase training iterations gradually as described in chapter 10.
Compare replays under the same conditions before deciding whether to change rewards.

## 6. Finish or extend the experiment {#extend}

Record why you changed the settings, the iteration count, checkpoint path, and replay behavior.
To restore the configuration, first stop the related processes. If these six assignments are your only changes,
run the command below in the same terminal. If you made other edits, compare the backup with the current file
and remove only these six assignments instead.

```bash
cp "$custom_backup/velocity_env_cfg.py" "$cfg"
```


You can next add terrain, recovery poses, or a ball:

| Addition | Start here | What to check |
| --- | --- | --- |
| Slopes or obstacles | `MicroDuckSceneCfg` | The robot resets above the ground and contacts behave correctly |
| Recovery task | `EventsCfg`, `RewardsCfg`, `TerminationsCfg` | Time to stand from a fallen pose and the number of subsequent falls |
| Ball kick | Ball asset, ball-position observations, kick rewards, termination rules | Ball displacement along the target direction and whether the duck stays upright |

The playground already has a 70 mm, 15 g ball whose physical settings you can reuse.
The training environment still needs ball-position observations, resets, and rewards.
Adding observations changes the input size, so update the network too; the old 61-input policy cannot directly consume extra ball-position values.

<div class="md-page-complete">
  <strong>Next: recovery and turning methods</strong>
  <p>You can now edit a configuration, check that it takes effect, and replay the model. Chapter 16 explains changes to teachers, starting poses, and rewards.</p>
</div>
