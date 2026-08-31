#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
python_exe="$project_dir/work/mujoco_env/bin/python"

if [[ ! -x "$python_exe" ]]; then
    mkdir -p "$project_dir/work"
    uv venv "$project_dir/work/mujoco_env" --python 3.12
fi

uv pip install --python "$python_exe" \
    'mujoco==3.10.0' \
    'onnxruntime==1.24.4' \
    'numpy==2.4.1'

"$python_exe" -c \
    "import mujoco, onnxruntime, numpy; print('mujoco', mujoco.__version__); print('onnxruntime', onnxruntime.__version__); print('numpy', numpy.__version__)"
