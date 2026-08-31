#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"

for required in \
    reference/microduck_rl/.git \
    reference/microduck/.git \
    work/mujoco_env/bin/python \
    work/isaac_python_pkgs/onnxruntime; do
    if [[ ! -e "$project_dir/$required" ]]; then
        printf 'Missing %s; follow README.md setup first.\n' "$required" >&2
        exit 1
    fi
done

printf '[1/8] Environment and pinned-source checks\n'
./scripts/check_environment.sh

printf '[2/8] MuJoCo inventory, stand, and walking baselines\n'
./scripts/run_official_baseline.sh

printf '[3/8] Isaac conversion, collision post-process, and USD inventory\n'
./scripts/convert_mjcf_to_usd.sh

printf '[4/8] Isaac stand policy\n'
./scripts/run_isaac_policy.sh \
    --policy reference/microduck/policies/alpha_stand.onnx \
    --duration 5 --action-scale 1.0 \
    --output artifacts/isaac/policy_stand_zero_command_scale_1_0.json

printf '[5/8] Isaac walking policy\n'
./scripts/run_isaac_policy.sh \
    --policy reference/microduck/policies/alpha_walking.onnx \
    --duration 10 --vx 0.3 --action-scale 0.9 \
    --output artifacts/isaac/policy_walk_vx_0_3_scale_0_9.json

printf '[6/8] Cross-engine behavioral smoke comparison\n'
"$project_dir/work/mujoco_env/bin/python" scripts/compare_rollouts.py

printf '[7/8] ROS description generation and package validation\n'
"$project_dir/work/mujoco_env/bin/python" scripts/generate_ros_description.py
"$project_dir/work/mujoco_env/bin/python" scripts/validate_ros_mjcf_pose_parity.py
./scripts/validate_ros2_package.sh

printf '[8/8] ROS runtime nodes, JointState, robot_description, and TF\n'
./scripts/validate_ros2_runtime.sh

printf 'All headless validation stages passed. GUI and hardware remain separate gates.\n'
