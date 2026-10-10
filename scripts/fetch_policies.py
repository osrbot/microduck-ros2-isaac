#!/usr/bin/env python3
"""Download the immutable official policy set, checking every file before install."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import tempfile
import tomllib
import urllib.request

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def checked_filename(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", name):
        raise ValueError(f"Unsafe policy filename: {name!r}")
    return name


def file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def fetch_file(url: str, destination: Path, expected: str) -> bool:
    """Never replace an existing mismatched file or install a partial download."""
    if not re.fullmatch(r"[a-f0-9]{64}", expected):
        raise ValueError("Expected a SHA-256 from the project lock")
    if destination.exists():
        if destination.is_symlink() or file_sha256(destination) != expected:
            raise ValueError(f"Existing file differs from lock; preserve it before retrying: {destination}")
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".download-", delete=False) as stream:
            temporary = Path(stream.name)
            request = urllib.request.Request(url, headers={"User-Agent": "microduck-ros2-isaac"})
            with urllib.request.urlopen(request, timeout=60) as response:
                while chunk := response.read(1024 * 1024):
                    stream.write(chunk)
        actual = file_sha256(temporary)
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch for {destination.name}: {actual} != {expected}")
        # link is exclusive: a concurrent creator must never be overwritten.
        temporary.chmod(0o644)
        destination.hardlink_to(temporary)
        return True
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, default=PROJECT_ROOT / "upstream.lock")
    args = parser.parse_args()
    with args.lock.open("rb") as stream:
        lock = tomllib.load(stream)
    config = lock["policies"]
    revision = config["revision"]
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("Policy revision must be an immutable 40-character commit")
    repo = config["repo"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("Invalid Hub repository")
    destination = PROJECT_ROOT / "reference/policies" / checked_filename(config["version"])
    for name, expected in config["files"].items():
        checked_filename(name)
        changed = fetch_file(
            f"https://huggingface.co/{repo}/resolve/{revision}/{name}",
            destination / name, expected,
        )
        print(f"{'downloaded' if changed else 'verified'} {name} {expected}")
    print(f"policies={repo}@{revision} ({config['version']})")
    legacy = lock["playground_sitstand"]
    if not re.fullmatch(r"[a-f0-9]{40}", legacy["revision"]):
        raise ValueError("Legacy policy revision must be an immutable 40-character commit")
    if not re.fullmatch(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+", legacy["repo"]):
        raise ValueError("Invalid legacy policy repository")
    legacy_path = PROJECT_ROOT / "reference/policies/isaac-legacy/alpha_sitstand.onnx"
    changed = fetch_file(
        f"https://raw.githubusercontent.com/{legacy['repo']}/{legacy['revision']}/policies/alpha_sitstand.onnx",
        legacy_path, legacy["sha256"],
    )
    print(f"{'downloaded' if changed else 'verified'} isaac-legacy/alpha_sitstand.onnx {legacy['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
