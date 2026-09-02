# Design another training task

This page is a development recipe, not a one-command task generator. Define the scene, success condition, reward,
termination, and replay gate before spending hours on PPO.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Planning</span><strong>20–30 minutes</strong></div>
  <div role="listitem"><span>Implementation</span><strong>Depends on the task</strong></div>
  <div role="listitem"><span>Prerequisite</span><strong>Velocity smoke run passes</strong></div>
  <div role="listitem"><span>Output</span><strong>A testable task definition</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>Describe the new task in four statements</strong>
  <ul>
    <li>what enters the scene;</li>
    <li>what command the robot receives;</li>
    <li>what counts as success and failure;</li>
    <li>what replayed behavior must be visible before you call it learned.</li>
  </ul>
</div>

## Recommended first task: kick a ball

The repository already has a tested 70 mm, 15 g ball and left/right placement baseline. The result is easier to judge
than a scalar reward. Train one side first, then mirror it. Do not combine walking, recovery, kicking, and rolling in one
reward on day one.

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="MicroDuck and the yellow ball in the real Isaac skill playground" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>Start from a scene baseline that already runs.</strong>The ball dimensions, mass, and placement are exercised by the playground. Reuse those facts, but do not present released-policy playback as your training result.</figcaption>
</figure>

## Suggested task order

| Task | Add to the scene | Primary success metric | Leave out of version one |
| --- | --- | --- | --- |
| Rough locomotion | Height fields, steps, slopes | Track velocity without falling | Ball skills |
| Stand up | Random prone and supine starts | Reach a stable stand in time | Style objectives |
| Ball kick | Ball, target direction, active foot | Move the ball while staying upright | Continuous dribbling |
| Ground pick | Mouth-tip contact target | Touch the floor and recover | Object grasping |
| Sit / rise | Binary posture command | Complete both transitions smoothly | Forward roll |

<div class="md-step-kicker"><span>STEP 1</span><strong>Write acceptance criteria first</strong></div>

## Example: define one kick episode

1. Spawn the duck in a stable pose and randomize the ball within a small area beside the left foot.
2. Supply a target direction.
3. Require the ball to travel a minimum distance along that direction before timeout.
4. Keep root height and tilt inside an upright range.
5. End the episode on success, fall, timeout, or out-of-bounds ball motion.

Choose thresholds from scene measurements and short runs. Do not quietly redefine “kick” as “the foot touched the ball”
just because that produces a better graph.

<div class="md-step-kicker"><span>STEP 2</span><strong>Copy the smallest task skeleton</strong></div>

## Reuse only the common pieces

The current native task is under:

```text
source/microduck_isaac_lab/microduck_isaac_lab/tasks/velocity/
```

Keep the shared robot and 61-value interface, then replace task-specific configuration:

1. `SceneCfg`: ball, obstacle, terrain, or target;
2. `CommandsCfg`: the quantity the policy must track;
3. `EventsCfg`: spawn states, placement, pushes, mass, and friction;
4. `RewardsCfg`: one primary objective plus a small safety and smoothness set;
5. `TerminationsCfg`: success, fall, bounds, and timeout;
6. `CurriculumCfg`: begin with a learnable task, then widen randomization;
7. `agents/`: reuse the PPO baseline until the environment itself works.

::: tip Change one layer at a time
First make reset, observations, and rewards finite. Then make a short run save a checkpoint. Tune the reward only after
those gates pass. Mirror the second kick side only after one side is stable.
:::

<div class="md-step-kicker"><span>STEP 3</span><strong>Pass five gates</strong></div>

## Minimum acceptance matrix

| Gate | Required check | Inspect first after failure |
| --- | --- | --- |
| Contract | 61 observations, 14 actions, unchanged joint order | Observation terms and joint map |
| Environment | Parallel reset, contacts, randomization, finite values | Scene, sensors, and events |
| Short training | PPO updates and saves a checkpoint | Reward, termination, VRAM, runner |
| Behavior | Continuous replay completes the intended skill | Reward exploits, commands, curriculum |
| Robustness | Multiple seeds and spawn positions still work | Overfitting to one initial state |

A rising reward only proves that the policy found a way to score. The final two gates test whether it learned the action
you intended.

<div class="md-step-kicker"><span>STEP 4</span><strong>Combine skills only after one is stable</strong></div>

## Choose a multi-skill architecture later

After one skill works across varied starts, compare:

- one policy per skill with safe runtime switching;
- a shared actor with an explicit skill ID;
- distillation from several expert policies.

The [skill playground](./playground) already demonstrates the first option, which is the easiest to inspect and debug.

<div class="md-page-complete">
  <strong>Creating a folder is not the completion condition.</strong>
  <p>You should leave this page with one selected skill, explicit scene and command inputs, success and failure rules, and a replay acceptance gate.</p>
</div>

<div class="md-next-grid">
  <a class="md-next-card" href="/microduck-ros2-isaac/isaac/training"><span>RETURN TO BASELINE</span><strong>Recheck the existing training loop →</strong><p>Make sure smoke, TensorBoard, and replay work before copying the task.</p></a>
  <a class="md-next-card" href="/microduck-ros2-isaac/isaac/playground"><span>STUDY BEHAVIOR</span><strong>Inspect released skills again →</strong><p>Use continuous motion and state changes to define acceptance criteria.</p></a>
</div>
