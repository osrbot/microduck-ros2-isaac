# Make a new training task

The [continuous-roll case study](./continuous-roll) covered training, tuning, and evaluation. Now apply the same process to a new motion:
define the scene, success criteria, rewards, termination rules, and replay checks before implementing the task.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>Planning</span><strong>20–30 minutes</strong></div>
  <div role="listitem"><span>Implementation</span><strong>Depends on the task</strong></div>
  <div role="listitem"><span>Prerequisite</span><strong>Velocity smoke run passes</strong></div>
  <div role="listitem"><span>Result</span><strong>A task you can test</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>Explain your task in four lines</strong>
  <ul>
    <li>what enters the scene;</li>
    <li>what command the robot receives;</li>
    <li>what counts as success and failure;</li>
    <li>what replayed behavior must be visible before you call it learned.</li>
  </ul>
</div>

## A good first task: kick a ball

The repository already has a tested 70 mm, 15 g ball and left/right placement baseline. The result is easier to judge
than a scalar reward. Train one side first, then mirror it. Do not combine walking, recovery, kicking, and rolling in one
reward on day one.

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="MicroDuck and the yellow ball in the real Isaac skill playground" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>Start with a scene that already works.</strong>The playground already checks the ball size, mass, and position. Reuse those facts, but do not call a ready-made policy your own training result.</figcaption>
</figure>

## Suggested task order

| Task | Add to the scene | Primary success metric | Leave out of version one |
| --- | --- | --- | --- |
| Rough locomotion | Height fields, steps, slopes | Track velocity without falling | Ball skills |
| Stand up | Random prone and supine starts | Reach a stable stand in time | Style objectives |
| Ball kick | Ball, target direction, active foot | Move the ball while staying upright | Continuous dribbling |
| Ground pick | Mouth-tip contact target | Touch the floor and recover | Object grasping |
| Sit / rise | Binary posture command | Complete both transitions smoothly | Forward roll |

<div class="md-step-kicker"><span>STEP 1</span><strong>Write down what “good” means</strong></div>

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

<div class="md-step-kicker"><span>STEP 3</span><strong>Pass five checks</strong></div>

## Five checks before you train

| Gate | Required check | Inspect first after failure |
| --- | --- | --- |
| Contract | 61 observations, 14 actions, unchanged joint order | Observation terms and joint map |
| Environment | Parallel reset, contacts, randomization, finite values | Scene, sensors, and events |
| Short training | PPO updates and saves a checkpoint | Reward, termination, VRAM, runner |
| Behavior | Continuous replay completes the intended skill | Reward exploits, commands, curriculum |
| Robustness | Multiple seeds and spawn positions still work | Overfitting to one initial state |

A rising reward only proves that the policy found a way to score. The final two gates test whether it learned the action
you intended.

<div class="md-step-kicker"><span>STEP 4</span><strong>Get one move working before you mix moves</strong></div>

## Pick how the moves work together later

After one skill works across varied starts, compare:

- one policy per skill with safe runtime switching;
- a shared actor with an explicit skill ID;
- distillation from several expert policies.

The [skill playground](./playground) already demonstrates the first option, which is the easiest to inspect and debug.

<div class="md-page-complete">
  <strong>You made it through the whole route!</strong>
  <p>You can now pick one move, describe the scene and controls, and decide what success should look like before you write code.</p>
</div>
