# Livestream guide

Follow the order “watch the motion → control it → inspect the data → start training.”
The outline below takes about 25 minutes. While training starts, explain its parameters
and logs, then replay a checkpoint prepared before the session.

## Before going live

1. Complete the installation, RViz, and Isaac chapters, then rehearse each in the desktop session you will record.
2. Download the models and prepare a training checkpoint you have already replayed.
3. Place terminals on the left and RViz or Isaac on the right. Keep text readable and desktop folders outside the capture.
4. Rehearse the outline below and note startup delays. Check [licensing](./licensing) for the models and media you use.

## A 25-minute demonstration

| Time | Action | What to explain |
| --- | --- | --- |
| 0–2 min | Show a walking clip or the [continuous-roll video](../isaac/continuous-roll) | What viewers will learn to do |
| 2–7 min | Open RViz, move the camera, and adjust joints | How the model, joints, and TF relate |
| 7–12 min | Run standing and walking in Isaac, then try keyboard actions | How velocity commands change motion |
| 12–17 min | [Send ROS 2 commands](../ros2/isaac-control) and inspect the pose in RViz | Where commands go and how states return |
| 17–22 min | [Start a short training run](../isaac/training), show saved files, and replay a checkpoint | Rewards, updates, saving, and loading |
| 22–25 min | Recap the steps and suggest one parameter change | How viewers can repeat the exercise |

## RViz: inspect the model and move its joints

Open a new terminal at the project root and run:

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

On Humble, replace `jazzy` with `humble` and keep the default windowed launch.
Rotate and zoom first, then move individual joint sliders. Click **Center** to
restore the default pose. Show collision geometry when explaining that topic.

## Isaac: stand, walk, and use the keyboard

Open another terminal at the project root. Start with standing:

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/policies/v7/alpha_stand.onnx \
  --duration 30 --action-scale 1.0 --follow-camera --viz kit
```

After it exits, run the walking policy:

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/policies/v7/alpha_walking.onnx \
  --duration 60 --vx 0.3 --action-scale 0.9 --follow-camera --viz kit
```

Explain that `vx=0.3` is the forward-velocity command while viewers watch the motion.
Then use the [playground](../isaac/playground) to show turning, kicking, floor touches,
and sitting. Let each result remain visible for a few seconds before changing actions.

Simulation speed depends on the GPU and window. The recorded host took about three
minutes for 60 simulated seconds; rehearse on your machine and adjust the pace.
If progress stops and the window is unresponsive, exit with `Ctrl+C` and use
[troubleshooting](../troubleshooting).

## Training: explain each step as you run it

Follow [chapter 10](../isaac/training) for five updates. Point out the training stage,
save location, and configuration files. Then load your prepared checkpoint to show
“change settings → train → save → replay.” For continuous rolling, use the
[three-round tuning record](../isaac/roll-debugging) to explain the observed problem,
the change made, and the resulting behavior.

Complete downloads, installation, and repeated loading before the session. Keep
each demonstration focused on one operation and one visible result.
