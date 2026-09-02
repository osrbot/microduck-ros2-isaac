#!/usr/bin/env bash
set -eo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
workspace_dir="$project_dir/ros2_ws"
log_file="$project_dir/work/ros_bridge_runtime_launch.log"

export PATH="/usr/bin:/bin:$PATH"
source /opt/ros/jazzy/setup.bash
source "$workspace_dir/install/setup.bash"
set -u

mkdir -p "$(dirname "$log_file")"
setsid ros2 launch microduck_control_bridge isaac_playground.launch.py \
    use_rviz:=false command_port:=15055 telemetry_port:=15056 \
    >"$log_file" 2>&1 &
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
    fi
}
trap cleanup EXIT

sleep 3
/usr/bin/python3 "$project_dir/scripts/validate_ros_bridge_runtime.py"
