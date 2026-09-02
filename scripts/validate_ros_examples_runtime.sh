#!/usr/bin/env bash
set -eo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
workspace_dir="$project_dir/ros2_ws"
validation_dir="$project_dir/work/ros_example_validation"
launch_log="$validation_dir/rviz_motion_demo.log"

export PATH="/usr/bin:/bin:$PATH"
source /opt/ros/jazzy/setup.bash
source "$workspace_dir/install/setup.bash"
set -u

mkdir -p "$validation_dir"
setsid ros2 launch microduck_examples rviz_motion_demo.launch.py \
    use_rviz:=false >"$launch_log" 2>&1 &
launch_pid=$!

cleanup() {
    if kill -0 "$launch_pid" 2>/dev/null; then
        launch_pgid=$(ps -o pgid= -p "$launch_pid" | tr -d ' ')
        if [[ "$launch_pgid" == "$launch_pid" ]]; then
            kill -TERM -- "-$launch_pgid"
        else
            kill -TERM "$launch_pid"
        fi
        wait "$launch_pid" || true
        for _ in $(seq 1 50); do
            if ! pgrep -g "$launch_pgid" >/dev/null 2>&1; then
                return
            fi
            sleep 0.1
        done
        printf 'ROS example process group did not stop after 5 seconds.\n' >&2
        kill -KILL -- "-$launch_pgid" 2>/dev/null || true
    fi
}
trap cleanup EXIT

ready=0
for _ in $(seq 1 30); do
    if ros2 topic list 2>/dev/null | grep -qx /joint_states; then
        ready=1
        break
    fi
    sleep 0.2
done
if [[ "$ready" -ne 1 ]]; then
    printf 'RViz motion example did not publish /joint_states.\n' >&2
    exit 1
fi

timeout 10s ros2 topic echo --once /joint_states --field position \
    >"$validation_dir/pose_a.txt"
sleep 1.2
timeout 10s ros2 topic echo --once /joint_states --field position \
    >"$validation_dir/pose_b.txt"
ros2 node list | sort >"$validation_dir/nodes.txt"

if cmp -s "$validation_dir/pose_a.txt" "$validation_dir/pose_b.txt"; then
    printf 'RViz example published an unchanged pose.\n' >&2
    exit 1
fi
grep -qx /microduck_rviz_motion_demo "$validation_dir/nodes.txt"
grep -q 'RViz demo:' "$launch_log"

ros2 launch microduck_examples isaac_showcase.launch.py --show-args \
    >"$validation_dir/isaac_showcase_args.txt"
grep -q "'sequence'" "$validation_dir/isaac_showcase_args.txt"
grep -q "'telemetry_timeout_s'" "$validation_dir/isaac_showcase_args.txt"

printf 'ROS example runtime and launch contracts passed.\n'
