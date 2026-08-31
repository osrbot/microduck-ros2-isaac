#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
lock_file="$project_dir/upstream.lock"
reference_dir="$project_dir/reference"

read_lock_value() {
    local section=$1
    local key=$2
    python3 - "$lock_file" "$section" "$key" <<'PY'
import sys
import tomllib

with open(sys.argv[1], "rb") as stream:
    data = tomllib.load(stream)
print(data[sys.argv[2]][sys.argv[3]])
PY
}

sync_repo() {
    local directory_name=$1
    local section=$2
    local url
    local commit
    local destination="$reference_dir/$directory_name"
    url=$(read_lock_value "$section" url)
    commit=$(read_lock_value "$section" commit)

    if [[ -e "$destination" && ! -d "$destination/.git" ]]; then
        printf 'Refusing to replace non-Git path: %s\n' "$destination" >&2
        return 1
    fi

    if [[ ! -d "$destination/.git" ]]; then
        git clone --no-checkout "$url" "$destination"
    elif [[ -n $(git -C "$destination" status --porcelain) ]]; then
        printf 'Refusing to change dirty reference checkout: %s\n' "$destination" >&2
        return 1
    fi

    git -C "$destination" fetch --depth 1 origin "$commit"
    git -C "$destination" checkout --detach "$commit"
    test "$(git -C "$destination" rev-parse HEAD)" = "$commit"
    printf '%s=%s\n' "$section" "$commit"
}

mkdir -p "$reference_dir"
sync_repo microduck_rl microduck_rl
sync_repo microduck microduck_runtime
