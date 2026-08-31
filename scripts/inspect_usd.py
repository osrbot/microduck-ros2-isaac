#!/usr/bin/env python3
"""Inspect the converted MicroDuck USD without starting a simulation."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from pxr import Usd, UsdGeom, UsdPhysics


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_USD = (
    PROJECT_ROOT
    / "assets/isaac/robot_allcollisions/robot_allcollisions.usda"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/isaac/usd_inventory.json"
EXPECTED_JOINTS = {
    "left_hip_yaw",
    "left_hip_roll",
    "left_hip_pitch",
    "left_knee",
    "left_ankle",
    "neck_pitch",
    "head_pitch",
    "head_yaw",
    "head_roll",
    "right_hip_yaw",
    "right_hip_roll",
    "right_hip_pitch",
    "right_knee",
    "right_ankle",
}
EXPECTED_MASS_KG = 0.73724314
EXPECTED_MESHES = 81
EXPECTED_ENABLED_COLLISIONS = 10
EXPECTED_DISABLED_COLLISIONS = 71


def parse_args() -> argparse.Namespace:
    """Parse USD inventory options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--usd", type=Path, default=DEFAULT_USD)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def inspect_stage(path: Path) -> dict[str, Any]:
    """Return the composed USD articulation inventory."""
    stage = Usd.Stage.Open(str(path.resolve()), load=Usd.Stage.LoadAll)
    if stage is None:
        raise RuntimeError(f"Unable to open USD stage: {path}")

    default_prim = stage.GetDefaultPrim()
    rigid_bodies = []
    articulation_roots = []
    collisions = []
    enabled_collisions = []
    disabled_collisions = []
    meshes = []
    joints = []
    total_mass = 0.0

    prim_range = Usd.PrimRange.Stage(stage, Usd.TraverseInstanceProxies())
    for prim in prim_range:
        prim_path = str(prim.GetPath())
        if prim.HasAPI(UsdPhysics.ArticulationRootAPI):
            articulation_roots.append(prim_path)
        if prim.HasAPI(UsdPhysics.RigidBodyAPI):
            mass_api = UsdPhysics.MassAPI(prim)
            mass = mass_api.GetMassAttr().Get()
            mass_value = float(mass) if mass is not None else 0.0
            total_mass += mass_value
            rigid_bodies.append({"path": prim_path, "mass_kg": mass_value})
        if prim.HasAPI(UsdPhysics.CollisionAPI):
            collisions.append(prim_path)
            enabled = UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Get()
            if enabled is None or bool(enabled):
                enabled_collisions.append(prim_path)
            else:
                disabled_collisions.append(prim_path)
        if prim.IsA(UsdGeom.Mesh):
            meshes.append(prim_path)
        if prim.IsA(UsdPhysics.RevoluteJoint):
            joint = UsdPhysics.RevoluteJoint(prim)
            joints.append(
                {
                    "name": prim.GetName(),
                    "path": prim_path,
                    "lower_limit_deg": joint.GetLowerLimitAttr().Get(),
                    "upper_limit_deg": joint.GetUpperLimitAttr().Get(),
                    "axis": joint.GetAxisAttr().Get(),
                }
            )

    joint_names = {item["name"] for item in joints}
    host_specific_layer_documentation = sorted(
        layer.identifier
        for layer in stage.GetLayerStack(includeSessionLayers=False)
        if any(marker in layer.documentation for marker in ("/home/", "/tmp/"))
    )
    checks = {
        "default_prim": bool(default_prim and default_prim.IsValid()),
        "meters_per_unit": math.isclose(
            UsdGeom.GetStageMetersPerUnit(stage), 1.0, rel_tol=0.0, abs_tol=1e-12
        ),
        "kilograms_per_unit": math.isclose(
            UsdPhysics.GetStageKilogramsPerUnit(stage),
            1.0,
            rel_tol=0.0,
            abs_tol=1e-12,
        ),
        "up_axis_z": UsdGeom.GetStageUpAxis(stage) == UsdGeom.Tokens.z,
        "one_articulation_root": len(articulation_roots) == 1,
        "joint_names": joint_names == EXPECTED_JOINTS,
        "mass": math.isclose(
            total_mass, EXPECTED_MASS_KG, rel_tol=0.0, abs_tol=2e-6
        ),
        "mesh_count": len(meshes) == EXPECTED_MESHES,
        "collision_api_count": len(collisions) == EXPECTED_MESHES,
        "enabled_collision_count": len(enabled_collisions)
        == EXPECTED_ENABLED_COLLISIONS,
        "disabled_visual_collision_count": len(disabled_collisions)
        == EXPECTED_DISABLED_COLLISIONS,
        "self_collision_only_not_ground_collision": not any(
            "/power_support_1/" in path for path in enabled_collisions
        ),
        "no_host_specific_layer_documentation": (
            not host_specific_layer_documentation
        ),
    }
    return {
        "usd": str(path.resolve().relative_to(PROJECT_ROOT)),
        "default_prim": str(default_prim.GetPath()) if default_prim else None,
        "meters_per_unit": UsdGeom.GetStageMetersPerUnit(stage),
        "kilograms_per_unit": UsdPhysics.GetStageKilogramsPerUnit(stage),
        "up_axis": str(UsdGeom.GetStageUpAxis(stage)),
        "articulation_roots": articulation_roots,
        "total_mass_kg": total_mass,
        "rigid_bodies": rigid_bodies,
        "revolute_joints": sorted(joints, key=lambda item: item["name"]),
        "collision_count": len(collisions),
        "enabled_collision_count": len(enabled_collisions),
        "disabled_collision_count": len(disabled_collisions),
        "enabled_collision_paths": enabled_collisions,
        "mesh_count": len(meshes),
        "host_specific_layer_documentation": host_specific_layer_documentation,
        "checks": checks,
        "all_checks_ok": all(checks.values()),
    }


def main() -> int:
    """Inspect the stage and write retained evidence."""
    args = parse_args()
    report = inspect_stage(args.usd)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: report[key]
                for key in (
                    "total_mass_kg",
                    "collision_count",
                    "enabled_collision_count",
                    "disabled_collision_count",
                    "mesh_count",
                    "checks",
                    "all_checks_ok",
                )
            },
            indent=2,
        )
    )
    print(f"Wrote {args.output}")
    return 0 if report["all_checks_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
