#!/usr/bin/env python3
"""Compare matched MicroDuck MuJoCo and Isaac policy-rollout evidence."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MUJOCO = (
    PROJECT_ROOT / "artifacts/baseline/mujoco_walk_vx_0_3_scale_0_9.json"
)
DEFAULT_ISAAC = (
    PROJECT_ROOT / "artifacts/isaac/policy_walk_vx_0_3_scale_0_9.json"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/parity/walk_vx_0_3_comparison.json"


def close_list(left: list[float], right: list[float], tolerance: float = 1e-6) -> bool:
    return len(left) == len(right) and all(
        math.isclose(a, b, abs_tol=tolerance) for a, b in zip(left, right, strict=True)
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mujoco", type=Path, default=DEFAULT_MUJOCO)
    parser.add_argument("--isaac", type=Path, default=DEFAULT_ISAAC)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    mujoco = json.loads(args.mujoco.read_text(encoding="utf-8"))["summary"]
    isaac = json.loads(args.isaac.read_text(encoding="utf-8"))["summary"]
    mujoco_xyz = mujoco["final_root_xyz_m"]
    isaac_xyz = isaac["final_root_xyz_m"]
    x_difference = isaac_xyz[0] - mujoco_xyz[0]
    x_relative_difference = x_difference / mujoco_xyz[0]
    checks = {
        "both_finite": bool(mujoco["finite"] and isaac["finite"]),
        "both_upright_at_end": bool(
            mujoco["upright_at_end"] and isaac["upright_at_end"]
        ),
        "commands_match": close_list(mujoco["command"], isaac["command"]),
        "action_scales_match": math.isclose(
            mujoco["action_scale"], isaac["action_scale"], abs_tol=1e-9
        ),
        "physics_timestep_matches": math.isclose(
            mujoco["simulation_timestep_s"],
            isaac["physics_timestep_s"],
            abs_tol=1e-12,
        ),
        "control_rate_matches": math.isclose(
            mujoco["control_hz"], isaac["control_hz"], abs_tol=1e-12
        ),
        "final_height_within_1cm": abs(isaac_xyz[2] - mujoco_xyz[2]) < 0.01,
        "max_tilt_within_0_02rad": abs(
            isaac["max_tilt_rad"] - mujoco["max_tilt_rad"]
        )
        < 0.02,
    }
    report = {
        "scenario": {
            "duration_s": isaac["duration_s"],
            "vx_m_s": isaac["command"][0],
            "action_scale": isaac["action_scale"],
        },
        "mujoco": {
            "final_root_xyz_m": mujoco_xyz,
            "max_tilt_rad": mujoco["max_tilt_rad"],
            "min_root_z_m": mujoco["min_root_z_m"],
        },
        "isaac": {
            "final_root_xyz_m": isaac_xyz,
            "max_tilt_rad": isaac["max_tilt_rad"],
            "min_root_z_m": isaac["min_root_z_m"],
        },
        "differences": {
            "final_xyz_isaac_minus_mujoco_m": [
                isaac_value - mujoco_value
                for isaac_value, mujoco_value in zip(isaac_xyz, mujoco_xyz, strict=True)
            ],
            "forward_displacement_relative_difference": x_relative_difference,
            "max_tilt_isaac_minus_mujoco_rad": (
                isaac["max_tilt_rad"] - mujoco["max_tilt_rad"]
            ),
        },
        "checks": checks,
        "behavioral_smoke_parity": all(checks.values()),
        "interpretation": (
            "Both engines execute the same policy contract and remain upright. "
            "Trajectory equality is not claimed: PhysX uses a simplified implicit-PD "
            "actuator and different contact dynamics from the upstream MuJoCo model."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["behavioral_smoke_parity"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
