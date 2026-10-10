#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
isaaclab_dir=${ISAACLAB_DIR:-"$HOME/rlgpu_ws/IsaacLab"}
input="$project_dir/reference/microduck_rl/src/mjlab_microduck/robot/microduck/robot_groundcontact.xml"
# Keep the historical robot_allcollisions USD intact: native training and
# recorded experiments still use that separately pinned asset.
canonical_dir="$project_dir/assets/isaac/robot_groundcontact"
evidence_dir="$project_dir/artifacts/isaac/groundcontact"

if [[ -e "$canonical_dir" ]]; then
    printf 'Preserve or archive the existing candidate before reconverting: %s\n' "$canonical_dir" >&2
    exit 1
fi
if [[ ! -f "$input" ]]; then
    printf 'Run scripts/fetch_upstream.sh first; missing %s\n' "$input" >&2
    exit 1
fi

if [[ ! -x "$isaaclab_dir/isaaclab.sh" ]]; then
    printf 'Isaac Lab launcher not found: %s\n' "$isaaclab_dir/isaaclab.sh" >&2
    exit 1
fi

mkdir -p "$project_dir/assets/isaac" "$project_dir/work" "$evidence_dir"
conversion_dir=$(mktemp -d "$project_dir/work/isaac_conversion.XXXXXX")
generated_dir="$conversion_dir/robot_groundcontact"
requested_output="$conversion_dir/robot_groundcontact.usd"

cleanup() {
    # This is only the fresh generated scratch directory, never a prior asset.
    rm -rf -- "$conversion_dir"
}
trap cleanup EXIT

# Isaac Sim 6's importer creates a suffixed sibling when its chosen output
# directory already exists. Convert into a fresh temporary directory so every
# run produces exactly one deterministic canonical asset instead.
"$isaaclab_dir/isaaclab.sh" -p \
    "$isaaclab_dir/scripts/tools/convert_mjcf.py" \
    "$input" "$requested_output" \
    2>&1 | tee "$evidence_dir/conversion.log"

if [[ ! -f "$generated_dir/robot_groundcontact.usda" ]]; then
    printf 'Isaac converter did not create the expected asset: %s\n' "$generated_dir" >&2
    exit 1
fi
"$isaaclab_dir/isaaclab.sh" -p "$project_dir/scripts/postprocess_isaac_usd.py" \
    --instances "$generated_dir/payloads/instances.usda" \
    --output "$evidence_dir/usd_postprocess.json"

"$isaaclab_dir/isaaclab.sh" -p "$project_dir/scripts/inspect_usd.py" \
    --usd "$generated_dir/robot_groundcontact.usda" \
    --output "$evidence_dir/usd_inventory_candidate.json"

mv -- "$generated_dir" "$canonical_dir"
"$isaaclab_dir/isaaclab.sh" -p "$project_dir/scripts/inspect_usd.py" \
    --usd "$canonical_dir/robot_groundcontact.usda" \
    --output "$evidence_dir/usd_inventory.json"
printf 'Converted candidate: %s (runtime playback is a separate gate)\n' "$canonical_dir"
