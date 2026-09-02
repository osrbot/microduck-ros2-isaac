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

printf '[1/13] Environment and pinned-source checks\n'
./scripts/check_environment.sh

printf '[2/13] Playground, training-task, and bridge contract checks\n'
./scripts/validate_learning_stack.sh

printf '[3/13] MuJoCo inventory, stand, and walking baselines\n'
./scripts/run_official_baseline.sh

printf '[4/13] Isaac conversion, collision post-process, and USD inventory\n'
./scripts/convert_mjcf_to_usd.sh

printf '[5/13] Isaac stand policy\n'
./scripts/run_isaac_policy.sh \
    --policy reference/microduck/policies/alpha_stand.onnx \
    --duration 5 --action-scale 1.0 \
    --output artifacts/isaac/policy_stand_zero_command_scale_1_0.json

printf '[6/13] Isaac walking policy\n'
./scripts/run_isaac_policy.sh \
    --policy reference/microduck/policies/alpha_walking.onnx \
    --duration 10 --vx 0.3 --action-scale 0.9 \
    --output artifacts/isaac/policy_walk_vx_0_3_scale_0_9.json

printf '[7/13] Interactive multi-policy playground smoke\n'
./scripts/run_isaac_playground.sh --duration 2 --no-keyboard --headless

printf '[8/13] Native Isaac Lab training-task smoke\n'
MICRODUCK_TRAIN_ENVS=16 MICRODUCK_TRAIN_ITERATIONS=1 \
    ./scripts/train_isaac_velocity.sh

printf '[9/13] Cross-engine behavioral smoke comparison\n'
"$project_dir/work/mujoco_env/bin/python" scripts/compare_rollouts.py

printf '[10/13] ROS description generation and package validation\n'
"$project_dir/work/mujoco_env/bin/python" scripts/generate_ros_description.py
"$project_dir/work/mujoco_env/bin/python" scripts/validate_ros_mjcf_pose_parity.py
./scripts/validate_ros2_package.sh

printf '[11/13] ROS description and runnable-example runtime\n'
./scripts/validate_ros2_runtime.sh
./scripts/validate_ros_examples_runtime.sh

printf '[12/13] ROS-to-Isaac bridge command and telemetry runtime\n'
./scripts/validate_ros_bridge_runtime.sh

printf '[13/13] Live ROS-to-Isaac playground round trip\n'
./scripts/validate_ros_isaac_e2e.sh

printf 'All headless validation stages passed. GUI and hardware remain separate gates.\n'
