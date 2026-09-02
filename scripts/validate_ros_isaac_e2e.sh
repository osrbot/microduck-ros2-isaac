#!/usr/bin/env bash
set -eo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
workspace_dir="$project_dir/ros2_ws"
artifact_dir=${MICRODUCK_E2E_ARTIFACT_DIR:-"$project_dir/artifacts/isaac"}
work_dir="$project_dir/work/ros_isaac_e2e"
command_port=${MICRODUCK_E2E_COMMAND_PORT:-15155}
telemetry_port=${MICRODUCK_E2E_TELEMETRY_PORT:-15156}
playground_duration=${MICRODUCK_E2E_DURATION:-30}
wall_timeout=${MICRODUCK_E2E_TIMEOUT:-120}
playground_report=${MICRODUCK_E2E_PLAYGROUND_REPORT:-"$artifact_dir/ros_isaac_e2e_playground.json"}
probe_report=${MICRODUCK_E2E_PROBE_REPORT:-"$artifact_dir/ros_isaac_e2e.json"}
launch_log=${MICRODUCK_E2E_ROS_LOG:-"$work_dir/ros_launch.log"}
playground_log=${MICRODUCK_E2E_ISAAC_LOG:-"$work_dir/isaac_playground.log"}
probe_log=${MICRODUCK_E2E_PROBE_LOG:-"$work_dir/ros_probe.log"}

export PATH="/usr/bin:/bin:$PATH"
source /opt/ros/jazzy/setup.bash
source "$workspace_dir/install/setup.bash"
set -u

mkdir -p "$artifact_dir" "$work_dir" "$(dirname "$playground_report")" \
    "$(dirname "$probe_report")" "$(dirname "$launch_log")" \
    "$(dirname "$playground_log")" "$(dirname "$probe_log")"

launch_pid=
playground_pid=
probe_pid=

stop_process_group() {
    local pid=$1
    if [[ -z "$pid" ]] || ! kill -0 "$pid" 2>/dev/null; then
        return
    fi
    local pgid
    pgid=$(ps -o pgid= -p "$pid" | tr -d ' ')
    if [[ -n "$pgid" && "$pgid" == "$pid" ]]; then
        kill -TERM -- "-$pgid" 2>/dev/null || true
    else
        kill -TERM "$pid" 2>/dev/null || true
    fi
    wait "$pid" 2>/dev/null || true
}

cleanup() {
    stop_process_group "$probe_pid"
    stop_process_group "$playground_pid"
    stop_process_group "$launch_pid"
}
trap cleanup EXIT

setsid ros2 launch microduck_control_bridge isaac_playground.launch.py \
    use_rviz:=false command_port:="$command_port" telemetry_port:="$telemetry_port" \
    >"$launch_log" 2>&1 &
launch_pid=$!

sleep 2
setsid /usr/bin/python3 "$project_dir/scripts/validate_ros_isaac_e2e.py" \
    --playground-report "$playground_report" \
    --output "$probe_report" \
    --timeout "$wall_timeout" \
    >"$probe_log" 2>&1 &
probe_pid=$!

sleep 1
setsid timeout --signal=INT --kill-after=10s "$wall_timeout" \
    "$project_dir/scripts/run_isaac_playground.sh" \
    --headless --no-keyboard --duration "$playground_duration" \
    --ros-command-port "$command_port" --ros-telemetry-port "$telemetry_port" \
    --output "$playground_report" \
    >"$playground_log" 2>&1 &
playground_pid=$!

set +e
wait "$playground_pid"
playground_status=$?
playground_pid=
wait "$probe_pid"
probe_status=$?
probe_pid=
set -e

if [[ "$playground_status" -ne 0 ]]; then
    tail -120 "$playground_log" >&2
    exit "$playground_status"
fi
if [[ "$probe_status" -ne 0 ]]; then
    tail -120 "$probe_log" >&2
    exit "$probe_status"
fi
if [[ ! -s "$playground_report" || ! -s "$probe_report" ]]; then
    echo "ROS-Isaac end-to-end evidence was not created." >&2
    exit 1
fi

cat "$probe_log"
