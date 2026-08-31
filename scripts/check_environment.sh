#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
isaaclab_dir=${ISAACLAB_DIR:-"$HOME/rlgpu_ws/IsaacLab"}

. /etc/os-release
printf 'project=%s\n' "$project_dir"
printf 'os=%s\n' "$PRETTY_NAME"
printf 'architecture=%s\n' "$(uname -m)"
printf 'kernel=%s\n' "$(uname -r)"
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
printf 'ros_distro=%s\n' "${ROS_DISTRO:-not-sourced}"
ros2 --version 2>/dev/null || true
docker --version
python3 --version
uv --version

if [[ ! -x "$isaaclab_dir/isaaclab.sh" ]]; then
    printf 'Isaac Lab launcher not found: %s\n' "$isaaclab_dir/isaaclab.sh" >&2
    exit 1
fi

printf 'isaaclab_dir=%s\n' "$isaaclab_dir"
printf 'isaaclab_version=%s\n' "$(<"$isaaclab_dir/VERSION")"
printf 'isaaclab_commit=%s\n' "$(git -C "$isaaclab_dir" rev-parse HEAD)"
"$isaaclab_dir/isaaclab.sh" -p -c \
    "import isaaclab, isaacsim; print('isaac_python_imports=ok')"
