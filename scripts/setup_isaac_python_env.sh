#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
isaaclab_dir=${ISAACLAB_DIR:-"$HOME/rlgpu_ws/IsaacLab"}
isaac_python="$isaaclab_dir/_isaac_sim/kit/python/bin/python3"
isaac_python_launcher="$isaaclab_dir/_isaac_sim/python.sh"
target_dir="$project_dir/work/isaac_python_pkgs"

if [[ ! -x "$isaac_python" || ! -x "$isaac_python_launcher" ]]; then
    echo "Isaac Sim Python was not found below $isaaclab_dir/_isaac_sim" >&2
    exit 1
fi

if PYTHONPATH="$target_dir" "$isaac_python_launcher" -c \
    'import onnxruntime as ort; assert ort.__version__ == "1.24.4"' \
    >/dev/null 2>&1; then
    echo "Project-local ONNX Runtime 1.24.4 is already ready."
    exit 0
fi

mkdir -p "$target_dir"
uv pip install \
    --python "$isaac_python" \
    --target "$target_dir" \
    --no-deps \
    'onnxruntime==1.24.4'

PYTHONPATH="$target_dir" "$isaac_python_launcher" -c \
    'import onnxruntime as ort; print(f"onnxruntime={ort.__version__} providers={ort.get_available_providers()}")'
