#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
microduck_rl_dir="$project_dir/reference/microduck_rl"
python_exe=${MICRODUCK_PYTHON:-"$project_dir/work/mujoco_env/bin/python"}

if [[ ! -d "$microduck_rl_dir/.git" ]]; then
    printf 'Run scripts/fetch_upstream.sh first.\n' >&2
    exit 1
fi

if [[ ! -x "$python_exe" ]]; then
    printf 'Run scripts/setup_mujoco_env.sh first.\n' >&2
    exit 1
fi

cd "$microduck_rl_dir"
"$python_exe" "$project_dir/scripts/inspect_upstream.py"
"$python_exe" "$project_dir/scripts/run_mujoco_baseline.py" \
    --policy "$project_dir/reference/microduck/policies/alpha_stand.onnx" \
    --duration "${MICRODUCK_STAND_DURATION:-5.0}" \
    --action-scale 1.0 \
    --output "$project_dir/artifacts/baseline/mujoco_stand_zero_command_scale_1_0.json"
"$python_exe" "$project_dir/scripts/run_mujoco_baseline.py" \
    --policy "$project_dir/reference/microduck/policies/alpha_walking.onnx" \
    --duration "${MICRODUCK_WALK_DURATION:-10.0}" \
    --vx "${MICRODUCK_WALK_VX:-0.3}" \
    --vy "${MICRODUCK_WALK_VY:-0.0}" \
    --yaw-rate "${MICRODUCK_WALK_YAW_RATE:-0.0}" \
    --action-scale 0.9 \
    --output "$project_dir/artifacts/baseline/mujoco_walk_vx_0_3_scale_0_9.json"
