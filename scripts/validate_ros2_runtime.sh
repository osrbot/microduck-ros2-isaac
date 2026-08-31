#!/usr/bin/env bash
set -eo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
workspace_dir="$project_dir/ros2_ws"
log_file="$project_dir/work/ros_runtime_launch.log"

export PATH="/usr/bin:/bin:$PATH"
source /opt/ros/jazzy/setup.bash
source "$workspace_dir/install/setup.bash"
set -u

mkdir -p "$(dirname "$log_file")"
setsid ros2 launch microduck_description view_microduck.launch.py \
    use_rviz:=false use_gui:=false >"$log_file" 2>&1 &
launch_pid=$!

cleanup() {
    if kill -0 "$launch_pid" 2>/dev/null; then
        # Run launch in its own session and terminate the entire process group;
        # otherwise killing only ros2 launch leaves its three child nodes orphaned.
        launch_pgid=$(ps -o pgid= -p "$launch_pid" | tr -d ' ')
        if [[ "$launch_pgid" == "$launch_pid" ]]; then
            kill -TERM -- "-$launch_pgid"
        else
            kill -TERM "$launch_pid"
        fi
        wait "$launch_pid" || true
        for _ in $(seq 1 50); do
            if ! pgrep -g "$launch_pgid" >/dev/null 2>&1; then
                break
            fi
            sleep 0.1
        done
    fi
}
trap cleanup EXIT

sleep 3
/usr/bin/python3 "$project_dir/scripts/validate_ros_runtime.py"
