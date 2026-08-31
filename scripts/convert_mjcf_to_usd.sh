#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
isaaclab_dir=${ISAACLAB_DIR:-"$HOME/rlgpu_ws/IsaacLab"}
input="$project_dir/reference/microduck_rl/src/mjlab_microduck/robot/microduck/robot_allcollisions.xml"
canonical_dir="$project_dir/assets/isaac/robot_allcollisions"
inventory="$project_dir/artifacts/isaac/usd_inventory.json"

if [[ ! -x "$isaaclab_dir/isaaclab.sh" ]]; then
    printf 'Isaac Lab launcher not found: %s\n' "$isaaclab_dir/isaaclab.sh" >&2
    exit 1
fi

mkdir -p "$project_dir/assets/isaac" "$project_dir/work"
conversion_dir=$(mktemp -d "$project_dir/work/isaac_conversion.XXXXXX")
backup_dir="$project_dir/work/isaac_previous_asset.$$"
generated_dir="$conversion_dir/robot_allcollisions"
requested_output="$conversion_dir/robot_allcollisions.usd"
asset_published=false

cleanup() {
    status=$?
    if [[ "$status" -ne 0 ]]; then
        if [[ "$asset_published" == true ]]; then
            rm -rf -- "$canonical_dir"
        fi
        if [[ -d "$backup_dir" ]]; then
            mv -- "$backup_dir" "$canonical_dir"
        fi
    elif [[ "$status" -eq 0 && -d "$backup_dir" ]]; then
        rm -rf -- "$backup_dir"
    fi
    rm -rf -- "$conversion_dir"
}
trap cleanup EXIT

# Isaac Sim 6's importer creates a suffixed sibling when its chosen output
# directory already exists. Convert into a fresh temporary directory so every
# run produces exactly one deterministic canonical asset instead.
"$isaaclab_dir/isaaclab.sh" -p \
    "$isaaclab_dir/scripts/tools/convert_mjcf.py" \
    "$input" "$requested_output" \
    2>&1 | tee "$project_dir/work/isaac_mjcf_conversion.log"

if [[ ! -f "$generated_dir/robot_allcollisions.usda" ]]; then
    printf 'Isaac converter did not create the expected asset: %s\n' "$generated_dir" >&2
    exit 1
fi
if [[ -e "$backup_dir" ]]; then
    printf 'Refusing to overwrite unexpected backup path: %s\n' "$backup_dir" >&2
    exit 1
fi
if [[ -d "$canonical_dir" ]]; then
    mv -- "$canonical_dir" "$backup_dir"
fi
mv -- "$generated_dir" "$canonical_dir"
asset_published=true

"$isaaclab_dir/isaaclab.sh" -p "$project_dir/scripts/postprocess_isaac_usd.py" \
    --instances "$canonical_dir/payloads/instances.usda"

"$isaaclab_dir/isaaclab.sh" -p "$project_dir/scripts/inspect_usd.py" \
    --usd "$canonical_dir/robot_allcollisions.usda" \
    --output "$inventory"
