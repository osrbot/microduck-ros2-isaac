#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
isaaclab_dir=${ISAACLAB_DIR:-"$HOME/rlgpu_ws/IsaacLab"}
isaac_device=${MICRODUCK_ISAAC_DEVICE:-cuda:0}
training_dir="$project_dir/work/isaac_training"
num_envs=${MICRODUCK_PLAY_ENVS:-1}
play_steps=${MICRODUCK_PLAY_STEPS:-200}
play_timeout=${MICRODUCK_PLAY_TIMEOUT:-180}
play_output=${MICRODUCK_PLAY_OUTPUT:-"$project_dir/artifacts/isaac/velocity_playback.json"}
play_screenshot=${MICRODUCK_PLAY_SCREENSHOT:-"$project_dir/artifacts/isaac/velocity_playback.png"}

if [[ "$isaac_device" =~ ^cuda:([0-9]+)$ ]]; then
    default_active_gpu=${BASH_REMATCH[1]}
else
    default_active_gpu=0
fi
isaac_active_gpu=${MICRODUCK_ISAAC_ACTIVE_GPU:-$default_active_gpu}
isaac_kit_args=${MICRODUCK_ISAAC_KIT_ARGS:-"--/renderer/multiGpu/autoEnable=0 --/renderer/multiGpu/enabled=0 --/renderer/activeGpu=$isaac_active_gpu --/crashreporter/skipOldDumpUpload=1 --/crashreporter/preserveDump=1"}

if [[ ! -x "$isaaclab_dir/isaaclab.sh" ]]; then
    printf 'Isaac Lab launcher not found: %s\n' "$isaaclab_dir/isaaclab.sh" >&2
    exit 1
fi

if [[ -n "${MICRODUCK_VULKAN_ICD:-}" ]]; then
    export VK_DRIVER_FILES=$MICRODUCK_VULKAN_ICD
    export VK_ICD_FILENAMES=$MICRODUCK_VULKAN_ICD
elif [[ -f /etc/vulkan/icd.d/nvidia_icd.json ]]; then
    export VK_DRIVER_FILES=/etc/vulkan/icd.d/nvidia_icd.json
    export VK_ICD_FILENAMES=/etc/vulkan/icd.d/nvidia_icd.json
fi

export MICRODUCK_PROJECT_DIR=$project_dir
export PYTHONPATH="$project_dir/source/microduck_isaac_lab${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p "$training_dir"

playback_completion_file=$(mktemp "${TMPDIR:-/tmp}/microduck-playback-complete.XXXXXX")
cleanup_playback_completion() {
    rm -f -- "$playback_completion_file"
}
trap cleanup_playback_completion EXIT

set +e
timeout --signal=INT --kill-after=10s "$play_timeout" \
    "$isaaclab_dir/isaaclab.sh" -p "$project_dir/scripts/play_isaac_velocity.py" \
    --device "$isaac_device" \
    --kit_args "$isaac_kit_args" \
    --num-envs "$num_envs" \
    --steps "$play_steps" \
    --output "$play_output" \
    --screenshot "$play_screenshot" \
    --enable_cameras \
    "$@" \
    --completion-file "$playback_completion_file"
launcher_exit=$?
set -e

if [[ "$launcher_exit" -ne 0 ]]; then
    if [[ "$launcher_exit" -eq 124 ]]; then
        printf 'Playback exceeded %s seconds and was stopped.\n' "$play_timeout" >&2
    fi
    exit "$launcher_exit"
fi
completion_state=$(<"$playback_completion_file")
if [[ "$completion_state" != "complete" ]]; then
    echo "Playback stopped before report and screenshot completion." >&2
    exit 1
fi
