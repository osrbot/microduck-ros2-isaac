#!/usr/bin/env bash
set -euo pipefail

project_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
lock_file="$project_dir/upstream.lock"
reference_dir="$project_dir/reference"

python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "fetch_upstream.sh needs Python 3.11+ (tomllib); use a suitable local environment")'

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
        git init "$destination"
        git -C "$destination" remote add origin "$url"
    elif [[ -n $(git -C "$destination" status --porcelain) ]]; then
        printf 'Refusing to change dirty reference checkout: %s\n' "$destination" >&2
        return 1
    fi

    if [[ $(git -C "$destination" remote get-url origin) != "$url" ]]; then
        printf 'Reference origin differs from lock: %s\n' "$destination" >&2
        return 1
    fi
    git -C "$destination" fetch --depth 1 origin "$commit"
    git -C "$destination" checkout --detach "$commit"
    test "$(git -C "$destination" rev-parse HEAD)" = "$commit"
    printf '%s=%s\n' "$section" "$commit"
}

mkdir -p "$reference_dir"
sync_repo microduck_rl microduck_rl
# Keep the old reference/microduck snapshot and its circus policy inputs intact.
sync_repo microduck_runtime microduck_runtime
python3 "$project_dir/scripts/fetch_policies.py"
