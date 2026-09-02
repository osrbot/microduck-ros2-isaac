#!/usr/bin/env bash
set -eo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
workspace_dir="$project_dir/ros2_ws"
validation_dir="$project_dir/work/ros_validation"
package_dir="$workspace_dir/src/microduck_description"

export PATH="/usr/bin:/bin:$PATH"
source /opt/ros/jazzy/setup.bash
set -u
mkdir -p "$validation_dir"

xacro "$package_dir/urdf/microduck.urdf.xacro" \
    >"$validation_dir/microduck.urdf"
check_urdf "$validation_dir/microduck.urdf"
python3 "$project_dir/scripts/validate_ros_description.py" \
    --urdf "$validation_dir/microduck.urdf" \
    --package-dir "$package_dir"

cd "$workspace_dir"
colcon build \
    --symlink-install \
    --packages-select \
        microduck_description \
        microduck_control_bridge \
        microduck_examples \
    --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3 \
    --event-handlers console_direct+

colcon test \
    --packages-select \
        microduck_description \
        microduck_control_bridge \
        microduck_examples \
    --event-handlers console_direct+
colcon test-result --verbose
