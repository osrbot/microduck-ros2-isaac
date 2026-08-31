#!/usr/bin/env python3
"""Inventory the pinned MicroDuck MJCF and ONNX policy contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import mujoco
import numpy as np
import onnxruntime as ort


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_ROOT = PROJECT_ROOT / "reference"
DEFAULT_MODEL = (
    REFERENCE_ROOT
    / "microduck_rl/src/mjlab_microduck/robot/microduck/robot_allcollisions.xml"
)
DEFAULT_POLICY_DIR = REFERENCE_ROOT / "microduck/policies"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/baseline/upstream_inventory.json"


def sha256(path: Path) -> str:
    """Return the SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_head(path: Path) -> str:
    """Return the checked-out Git commit for a reference repository."""
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def mj_name(model: mujoco.MjModel, obj_type: mujoco.mjtObj, index: int) -> str:
    """Return a stable name for one MuJoCo object."""
    return mujoco.mj_id2name(model, obj_type, index) or f"unnamed_{index}"


def joint_type_name(value: int) -> str:
    """Translate a MuJoCo joint type value into a readable label."""
    names = {
        int(mujoco.mjtJoint.mjJNT_FREE): "free",
        int(mujoco.mjtJoint.mjJNT_BALL): "ball",
        int(mujoco.mjtJoint.mjJNT_SLIDE): "slide",
        int(mujoco.mjtJoint.mjJNT_HINGE): "hinge",
    }
    return names.get(int(value), f"unknown_{int(value)}")


def model_inventory(path: Path) -> dict[str, Any]:
    """Load a MJCF model and return its structural and physical inventory."""
    model = mujoco.MjModel.from_xml_path(str(path))
    joints = []
    for index in range(model.njnt):
        limited = bool(model.jnt_limited[index])
        joints.append(
            {
                "index": index,
                "name": mj_name(model, mujoco.mjtObj.mjOBJ_JOINT, index),
                "type": joint_type_name(model.jnt_type[index]),
                "axis": model.jnt_axis[index].tolist(),
                "limited": limited,
                "range": model.jnt_range[index].tolist() if limited else None,
                "qpos_address": int(model.jnt_qposadr[index]),
                "dof_address": int(model.jnt_dofadr[index]),
            }
        )

    actuators = []
    for index in range(model.nu):
        joint_id = int(model.actuator_trnid[index, 0])
        actuators.append(
            {
                "index": index,
                "name": mj_name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, index),
                "joint": mj_name(model, mujoco.mjtObj.mjOBJ_JOINT, joint_id),
                "control_range": model.actuator_ctrlrange[index].tolist(),
                "force_range": model.actuator_forcerange[index].tolist(),
            }
        )

    sensors = []
    for index in range(model.nsensor):
        sensors.append(
            {
                "index": index,
                "name": mj_name(model, mujoco.mjtObj.mjOBJ_SENSOR, index),
                "dimension": int(model.sensor_dim[index]),
                "data_address": int(model.sensor_adr[index]),
            }
        )

    bodies = []
    for index in range(1, model.nbody):
        bodies.append(
            {
                "index": index,
                "name": mj_name(model, mujoco.mjtObj.mjOBJ_BODY, index),
                "parent_index": int(model.body_parentid[index]),
                "mass_kg": float(model.body_mass[index]),
                "inertia_kg_m2": model.body_inertia[index].tolist(),
            }
        )

    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "sha256": sha256(path),
        "model_name": path.stem,
        "timestep_s": float(model.opt.timestep),
        "gravity_m_s2": model.opt.gravity.tolist(),
        "counts": {
            "qpos": int(model.nq),
            "dof": int(model.nv),
            "bodies": int(model.nbody),
            "joints": int(model.njnt),
            "actuators": int(model.nu),
            "geometries": int(model.ngeom),
            "sensors": int(model.nsensor),
        },
        "total_body_mass_kg": float(np.sum(model.body_mass)),
        "joints": joints,
        "actuators": actuators,
        "sensors": sensors,
        "bodies": bodies,
    }


def policy_inventory(path: Path) -> dict[str, Any]:
    """Return the declared ONNX input and output contract."""
    session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    inputs = [
        {"name": item.name, "shape": item.shape, "type": item.type}
        for item in session.get_inputs()
    ]
    outputs = [
        {"name": item.name, "shape": item.shape, "type": item.type}
        for item in session.get_outputs()
    ]
    return {
        "path": str(path.relative_to(PROJECT_ROOT)),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "inputs": inputs,
        "outputs": outputs,
        "contract_ok": len(inputs) == 1
        and len(outputs) == 1
        and inputs[0]["shape"][-1] == 61
        and outputs[0]["shape"][-1] == 14,
    }


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--policy-dir", type=Path, default=DEFAULT_POLICY_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    """Write the reproducible upstream inventory."""
    args = parse_args()
    policy_paths = sorted(args.policy_dir.glob("*.onnx"))
    if not policy_paths:
        raise FileNotFoundError(f"No ONNX policies found in {args.policy_dir}")

    report = {
        "upstream": {
            "microduck_rl": git_head(REFERENCE_ROOT / "microduck_rl"),
            "microduck_runtime": git_head(REFERENCE_ROOT / "microduck"),
        },
        "model": model_inventory(args.model.resolve()),
        "policies": [policy_inventory(path.resolve()) for path in policy_paths],
    }
    report["all_policy_contracts_ok"] = all(
        policy["contract_ok"] for policy in report["policies"]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(
        "Model: "
        f"{report['model']['counts']['bodies']} bodies, "
        f"{report['model']['counts']['joints']} joints, "
        f"{report['model']['counts']['actuators']} actuators, "
        f"{report['model']['total_body_mass_kg']:.6f} kg"
    )
    print(
        f"Policies: {len(report['policies'])}; "
        f"61 -> 14 contracts: {report['all_policy_contracts_ok']}"
    )
    return 0 if report["all_policy_contracts_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
