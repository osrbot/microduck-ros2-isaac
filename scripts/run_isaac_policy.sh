#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
isaaclab_dir=${ISAACLAB_DIR:-"$HOME/rlgpu_ws/IsaacLab"}
isaac_python_packages="$project_dir/work/isaac_python_pkgs"
isaac_device=${MICRODUCK_ISAAC_DEVICE:-cuda:0}

# Isaac Sim is unstable when the Vulkan loader discovers the same NVIDIA GPU
# through two ICD manifests. Prefer the standalone-driver manifest when both
# distro and standalone manifests are installed, while preserving an explicit
# caller override for other hosts.
if [[ -n "${MICRODUCK_VULKAN_ICD:-}" ]]; then
    vulkan_icd=$MICRODUCK_VULKAN_ICD
elif [[ -f /etc/vulkan/icd.d/nvidia_icd.json ]]; then
    vulkan_icd=/etc/vulkan/icd.d/nvidia_icd.json
elif [[ -f /usr/share/vulkan/icd.d/nvidia_icd.json ]]; then
    vulkan_icd=/usr/share/vulkan/icd.d/nvidia_icd.json
else
    vulkan_icd=
fi

if [[ -n "$vulkan_icd" && -z "${VK_DRIVER_FILES:-}" && -z "${VK_ICD_FILENAMES:-}" ]]; then
    export VK_DRIVER_FILES=$vulkan_icd
    export VK_ICD_FILENAMES=$vulkan_icd
fi

if [[ "$isaac_device" =~ ^cuda:([0-9]+)$ ]]; then
    default_active_gpu=${BASH_REMATCH[1]}
else
    default_active_gpu=0
fi
isaac_active_gpu=${MICRODUCK_ISAAC_ACTIVE_GPU:-$default_active_gpu}
isaac_kit_args=${MICRODUCK_ISAAC_KIT_ARGS:-"--/renderer/multiGpu/autoEnable=0 --/renderer/multiGpu/enabled=0 --/renderer/activeGpu=$isaac_active_gpu"}

if [[ ! -d "$isaac_python_packages/onnxruntime" ]]; then
    echo "Missing project-local ONNX Runtime. Run scripts/setup_isaac_python_env.sh first." >&2
    exit 1
fi

export PYTHONPATH="$isaac_python_packages${PYTHONPATH:+:$PYTHONPATH}"
printf 'Isaac Vulkan ICD: %s\n' "${VK_DRIVER_FILES:-${VK_ICD_FILENAMES:-system default}}"
printf 'Isaac Kit GPU settings: %s\n' "$isaac_kit_args"
"$isaaclab_dir/isaaclab.sh" -p "$project_dir/scripts/run_isaac_policy.py" \
    --device "$isaac_device" \
    --kit_args "$isaac_kit_args" \
    "$@"
