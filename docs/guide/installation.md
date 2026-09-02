# Check your computer, then install what you need

Set up only the route you want. ROS 2 and Isaac Sim work on their own, so you do
not need both.

<div class="md-tutorial-meta" role="list" aria-label="Page overview">
  <div role="listitem"><span>ROS 2 setup</span><strong>10–20 minutes</strong></div>
  <div role="listitem"><span>Isaac setup</span><strong>About 10 minutes after install</strong></div>
  <div role="listitem"><span>Run in</span><strong>A Linux terminal</strong></div>
  <div role="listitem"><span>Ready when</span><strong>All checks print OK</strong></div>
</div>

## The two setups at a glance

<div class="md-requirement-grid">
  <div class="md-requirement-card md-route-orange"><span>ROS 2 route</span><strong>Ubuntu 24.04 + ROS 2 Jazzy</strong><p>No NVIDIA GPU and no Isaac Sim. This is the best first route.</p></div>
  <div class="md-requirement-card md-route-aqua"><span>Isaac route</span><strong>Ubuntu 24.04 + NVIDIA GPU</strong><p>Fully tested with Isaac Sim 6.0.1 standalone and Isaac Lab 3.0.0 beta 2.</p></div>
</div>

Set up only the route you want today. If you are unsure, prepare ROS 2 first.

<div class="md-tutorial-goals">
  <strong>You will</strong>
  <ul>
    <li>clone the project and check the folder;</li>
    <li>get ROS 2 and colcon ready, or find your Isaac Lab launcher;</li>
    <li>get the ready-made policies and ONNX Runtime when you need them;</li>
    <li>find setup problems before a window opens.</li>
  </ul>
</div>

## New to the terminal? Try these keys first

Run the commands on an **Ubuntu desktop** in the Terminal app. This is not the
Isaac Sim Console and not the browser address bar.

<div class="md-terminal-school">
  <strong>Ubuntu terminal shortcuts</strong>
  <p>Open, duplicate, paste, and stop are enough for the whole tutorial.</p>
  <div class="md-shortcut-grid" role="list" aria-label="Ubuntu terminal shortcuts">
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>T</kbd></strong><p>Open the first terminal window.</p></div>
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>N</kbd></strong><p>Open another window for terminal B or C.</p></div>
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>T</kbd></strong><p>Open a tab in the current window.</p></div>
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd></strong><p>Paste a copied command into the terminal.</p></div>
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>C</kbd></strong><p>Stop the running program. It does not copy in a terminal.</p></div>
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>L</kbd></strong><p>Clear the visible text without stopping the program.</p></div>
  </div>
</div>

::: tip If the shortcut is captured by Remote Desktop
Open **Activities**, search for **Terminal**, and launch it there. Use
**File → New Window** when you need another one. “Terminal A, B, and C” are only
labels; one computer is enough.
:::

<div class="md-command-steps">
  <strong>Run each command like this</strong>
  <p>Use the copy button → return to Terminal → press <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>V</kbd> → press <kbd>Enter</kbd>. A short command is finished when the <code>user@computer:folder$</code> prompt returns. A command that opens RViz or Isaac keeps running, so leave that terminal open.</p>
</div>

<div class="md-step-kicker"><span>STEP 1</span><strong>Terminal A · Ctrl + Alt + T</strong></div>

## Clone the repository

```bash
git clone https://github.com/osrbot/microduck-ros2-isaac.git
cd microduck-ros2-isaac
```

The first line downloads the repository and the second enters it. Wait for the
prompt to return before running the check below.

Verify the directory:

```bash
test -f README.md && test -d ros2_ws && test -d assets/isaac \
  && echo "MicroDuck repository: OK"
```

<div class="md-checkpoint">
  <strong>See OK? Keep going.</strong>
  <p>The terminal prints <code>MicroDuck repository: OK</code>. The ROS package and Isaac USD are already included; first-time users do not regenerate them.</p>
</div>

<div class="md-step-kicker"><span>STEP 2A</span><strong>ROS 2 route only</strong></div>

## Prepare ROS 2 Jazzy

These commands target Ubuntu 24.04 with the official ROS apt source already configured:

```bash
sudo apt update
sudo apt install \
  ros-jazzy-desktop \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-xacro \
  python3-colcon-common-extensions
```

When `sudo` asks for your password, the terminal shows no dots or asterisks.
Type it and press <kbd>Enter</kbd>. Continue after the prompt returns without an
error starting with `E:`.

Load and check the tools:

```bash
source /opt/ros/jazzy/setup.bash
echo "ROS_DISTRO=$ROS_DISTRO"
command -v ros2
command -v colcon
```

A successful `source` command normally prints nothing; the next three lines are
the checks that should produce output.

<div class="md-checkpoint">
  <strong>ROS 2 is ready!</strong>
  <p>The first line says <code>ROS_DISTRO=jazzy</code>; the next two lines print paths for <code>ros2</code> and <code>colcon</code>.</p>
</div>

::: tip Source each new terminal
`source /opt/ros/jazzy/setup.bash` affects only the current shell. The tutorials repeat every required source command.
:::

<div class="md-step-kicker"><span>STEP 2B</span><strong>Isaac route only</strong></div>

## Check Isaac Sim and Isaac Lab

The fully tested setup is Ubuntu 24.04, Isaac Sim 6.0.1 standalone, Isaac Lab 3.0.0 beta 2, and an NVIDIA GPU with
working drivers and Vulkan.

If Isaac Lab is not at `~/rlgpu_ws/IsaacLab`, set its path:

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
```

Replace `/path/to/IsaacLab` with the real directory on your computer, for
example `/home/duck/rlgpu_ws/IsaacLab`. Do not paste the placeholder unchanged.

Check the GPU and launcher:

```bash
nvidia-smi
test -x "${ISAACLAB_DIR:-$HOME/rlgpu_ws/IsaacLab}/isaaclab.sh" \
  && echo "Isaac Lab launcher: OK"
```

Fix the path if the second command does not print `OK`. Reopening Isaac will not repair a missing launcher.

## Fetch policies and local dependencies

From the repository root:

```bash
./scripts/fetch_upstream.sh
./scripts/setup_isaac_python_env.sh
```

The scripts create ignored `reference/` and `work/` directories inside this project. They do not modify Isaac Lab.

```bash
test -d reference/microduck && echo "Upstream assets: OK"
test -d work/isaac_python_pkgs/onnxruntime && echo "ONNX Runtime: OK"
```

<div class="md-checkpoint">
  <strong>Isaac is ready!</strong>
  <p>Both checks print <code>OK</code>. You may skip this section when you only want to open the included USD.</p>
</div>

## Fast troubleshooting

| Symptom | Check first |
| --- | --- |
| `ros2: command not found` | Source `/opt/ros/jazzy/setup.bash` in this terminal |
| `colcon: command not found` | Install `python3-colcon-common-extensions` |
| Isaac Lab launcher missing | Point `ISAACLAB_DIR` at the directory containing `isaaclab.sh` |
| `nvidia-smi` fails | Repair the NVIDIA driver or host GPU access |
| Released policy missing | Rerun `fetch_upstream.sh` and check the download |
| ONNX Runtime missing | Run `setup_isaac_python_env.sh` from the repository root |

<div class="md-page-complete">
  <strong>You’re ready!</strong>
  <p>The next page starts with the lighter ROS 2 route. If you only want Isaac Sim, use the left sidebar and jump to step 6.</p>
</div>
