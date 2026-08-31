#!/usr/bin/env python3
"""Normalize MJCF collision masks that the Isaac importer cannot preserve."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pxr import Sdf, Usd, UsdPhysics


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INSTANCES = (
    PROJECT_ROOT
    / "assets/isaac/robot_allcollisions/payloads/instances.usda"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/isaac/usd_postprocess.json"

# In the source MJCF this duplicate power-support mesh uses contype=2 and
# conaffinity=2: it exists only for the self-collision sensor and must not hit
# the ground. The Isaac importer retains mjc:group but drops those bitmasks.
SELF_COLLISION_ONLY_PRIMS = (
    "/Instances/power_support_1/power_support",
)

STABLE_LAYER_DOCUMENTATION = (
    "Generated from the pinned Pollen Robotics MicroDuck MJCF with Isaac Sim "
    "6.0.1; validated and post-processed by microduck_ros_isaac."
)


def normalize_layer_documentation(asset_root: Path) -> list[str]:
    """Replace importer temporary paths in both text and binary USD layers."""
    changed = []
    layer_paths = sorted(asset_root.rglob("*.usd")) + sorted(
        asset_root.rglob("*.usda")
    )
    for path in layer_paths:
        layer = Sdf.Layer.FindOrOpen(str(path.resolve()))
        if layer is None:
            raise ValueError(f"Unable to open generated USD layer: {path}")
        if layer.documentation != STABLE_LAYER_DOCUMENTATION:
            layer.documentation = STABLE_LAYER_DOCUMENTATION
            layer.Save()
            changed.append(str(path.relative_to(asset_root)))
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instances", type=Path, default=DEFAULT_INSTANCES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not args.instances.is_file():
        raise FileNotFoundError(args.instances)

    stage = Usd.Stage.Open(str(args.instances.resolve()), load=Usd.Stage.LoadAll)
    if stage is None:
        raise RuntimeError(f"Unable to open {args.instances}")
    changes = []
    for path in SELF_COLLISION_ONLY_PRIMS:
        prim = stage.GetPrimAtPath(path)
        if not prim or not prim.IsValid() or not prim.HasAPI(UsdPhysics.CollisionAPI):
            raise ValueError(f"Expected source self-collision prim is missing: {path}")
        collision_api = UsdPhysics.CollisionAPI(prim)
        before = collision_api.GetCollisionEnabledAttr().Get()
        collision_api.CreateCollisionEnabledAttr(False).Set(False)
        after = collision_api.GetCollisionEnabledAttr().Get()
        changes.append(
            {
                "prim": path,
                "source_mjcf_class": "self_collision_only",
                "source_contype": 2,
                "source_conaffinity": 2,
                "collision_enabled_before": True if before is None else bool(before),
                "collision_enabled_after": bool(after),
                "reason": (
                    "Isaac runtime profile disables articulation self-collision; "
                    "do not turn this source-only sensor mesh into ground collision."
                ),
            }
        )
    stage.GetRootLayer().Save()

    asset_root = args.instances.resolve().parents[1]
    normalized_layers = normalize_layer_documentation(asset_root)
    host_specific_documentation_remaining = []
    layer_paths = sorted(asset_root.rglob("*.usd")) + sorted(
        asset_root.rglob("*.usda")
    )
    for path in layer_paths:
        layer = Sdf.Layer.FindOrOpen(str(path.resolve()))
        documentation = layer.documentation if layer is not None else ""
        if layer is None or any(
            marker in documentation for marker in ("/home/", "/tmp/")
        ):
            host_specific_documentation_remaining.append(
                str(path.relative_to(asset_root))
            )

    report = {
        "instances_layer": str(args.instances.resolve().relative_to(PROJECT_ROOT)),
        "changes": changes,
        "normalized_layer_documentation": normalized_layers,
        "host_specific_layer_documentation_remaining": (
            host_specific_documentation_remaining
        ),
        "all_self_collision_only_disabled": all(
            not item["collision_enabled_after"] for item in changes
        ),
    }
    report["all_checks_pass"] = bool(
        report["all_self_collision_only_disabled"]
        and not report["host_specific_layer_documentation_remaining"]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
