#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"

python3 -m unittest discover -s tests -v
python3 -m compileall -q \
    scripts \
    tests \
    source/microduck_isaac_lab \
    ros2_ws/src/microduck_control_bridge \
    ros2_ws/src/microduck_examples
bash -n \
    scripts/run_isaac_playground.sh \
    scripts/train_isaac_velocity.sh \
    scripts/play_isaac_velocity.sh \
    scripts/validate_ros_bridge_runtime.sh \
    scripts/validate_ros_examples_runtime.sh \
    scripts/validate_ros_isaac_e2e.sh

printf 'Learning, playground, and ROS bridge contracts passed.\n'
