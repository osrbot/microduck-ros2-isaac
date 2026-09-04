#!/usr/bin/env python3
"""Run one experiment with both a per-stage and absolute wall-clock limit."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--deadline", required=True)
    parser.add_argument("--max-seconds", type=float, required=True)
    parser.add_argument("--status", type=Path, required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    deadline = datetime.fromisoformat(args.deadline).timestamp()
    allowance = min(args.max_seconds, deadline - time.time() - 20)
    args.status.parent.mkdir(parents=True, exist_ok=True)
    status = {"started_utc": datetime.now(timezone.utc).isoformat(), "deadline": args.deadline, "allowance_s": allowance, "command": command}
    if allowance <= 0 or not command:
        raise SystemExit("No attempt time remains, or command is empty")
    started = time.monotonic()
    process = subprocess.Popen(command, start_new_session=True)
    status["pid"] = process.pid
    args.status.write_text(json.dumps(status, indent=2) + "\n")
    timed_out = False
    try:
        exit_code = process.wait(timeout=allowance)
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        timed_out = True
        os.killpg(process.pid, signal.SIGINT)
        try:
            exit_code = process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            exit_code = process.wait(timeout=5)
    finally:
        # A launcher may return while leaving its child alive: always clean
        # this stage's process group, never unrelated GPU/user processes.
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    status.update(exit_code=exit_code, timed_out=timed_out, elapsed_s=time.monotonic() - started, finished_utc=datetime.now(timezone.utc).isoformat())
    args.status.write_text(json.dumps(status, indent=2) + "\n")
    return 124 if timed_out else exit_code


if __name__ == "__main__":
    raise SystemExit(main())
