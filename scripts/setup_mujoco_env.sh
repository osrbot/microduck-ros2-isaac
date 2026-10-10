#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
python_exe="$project_dir/work/mujoco_env/bin/python"

if [[ ! -x "$python_exe" ]]; then
    mkdir -p "$project_dir/work"
    if command -v uv >/dev/null 2>&1; then
        uv venv "$project_dir/work/mujoco_env" --python 3.12
    else
        "${MICRODUCK_BOOTSTRAP_PYTHON:-python3.12}" -m venv "$project_dir/work/mujoco_env"
    fi
fi

if command -v uv >/dev/null 2>&1; then
    installer=(uv pip install --python "$python_exe")
else
    installer=("$python_exe" -m pip install)
fi
"${installer[@]}" \
    'mujoco==3.10.0' \
    'onnxruntime==1.24.4' \
    'numpy==2.4.1'

"$python_exe" -c \
    "import mujoco, onnxruntime, numpy; print('mujoco', mujoco.__version__); print('onnxruntime', onnxruntime.__version__); print('numpy', numpy.__version__)"
