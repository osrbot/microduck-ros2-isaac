# Build another training task

“Train every action” rarely means placing every button inside one reward. Start
with a clear success condition for each skill, train and evaluate it separately,
then decide whether to use one conditional policy or runtime policy switching.

The best next task is a **ball-kick duck**. The repository already has the
ball size, mass, and left/right placement baseline, and the result is much
easier to judge on stream than a reward curve. Train one side first, mirror it
to the other, and avoid making walking, recovery, kicking, and rolling fight
inside one reward on day one.

## Suggested order

| Task | Add to the scene | Primary success metric |
| --- | --- | --- |
| Rough locomotion | Height fields, steps, and slopes | Track velocity without falling |
| Stand up | Random prone and supine starts | Reach a stable stand in time |
| Ball kick | A 70 mm, 15 g ball and target direction | Move the ball while remaining upright |
| Ground pick | A mouth-tip contact target | Touch the floor and recover to stand |
| Sit / rise | A binary posture command | Complete both transitions smoothly |

## What to copy from the current task

The native task lives under
`source/microduck_isaac_lab/microduck_isaac_lab/tasks/velocity/`. Keep the shared
asset and 61-value contract, then replace the task-specific pieces:

1. `SceneCfg` for a ball, obstacle, terrain, or target;
2. `EventsCfg` for spawn states, object placement, pushes, and randomization;
3. `RewardsCfg` for one main task objective and a small set of safety/smoothing terms;
4. `TerminationsCfg` for success, falls, and timeout;
5. `CurriculumCfg` to discover the skill before increasing difficulty or action taxes;
6. `agents/`, normally reusing the PPO baseline until the environment itself works.

## Do not call a five-iteration smoke run training success

Each new task needs three different checks:

- contract: 61 observations, 14 actions, and unchanged joint order;
- short training: resets work, rewards stay finite, and PPO updates/checkpoints;
- behavior: view the checkpoint and confirm the skill, not just a rising reward.

After one skill is stable, consider a shared actor, skill IDs, distillation, or
runtime policy switching. The [skill playground](./playground) already
demonstrates the last option.
