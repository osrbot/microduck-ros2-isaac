#!/usr/bin/env python3
"""Verify that generated URDF poses preserve the pinned MJCF pose matrices."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from generate_ros_description import (
    numbers,
    rotation_matrix_from_quaternion,
    rotation_matrix_from_rpy,
    upstream_sha,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_DIR = (
    PROJECT_ROOT / "reference/microduck_rl/src/mjlab_microduck/robot/microduck"
)
DEFAULT_XACRO = (
    PROJECT_ROOT
    / "ros2_ws/src/microduck_description/urdf/microduck.urdf.xacro"
)
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/ros/mjcf_urdf_pose_parity.json"
TRANSLATION_TOLERANCE_M = 1e-10
ROTATION_MATRIX_TOLERANCE = 1e-9


def relative_path(path: Path) -> str:
    """Return a project-relative path where possible for public evidence."""
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mjcf", type=Path, default=DEFAULT_MODEL_DIR / "robot_allcollisions.xml"
    )
    parser.add_argument("--xacro", type=Path, default=DEFAULT_XACRO)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def pose_errors(source: ET.Element, generated_origin: ET.Element) -> tuple[float, float]:
    """Return translation and rotation-matrix errors for one source/output pose."""
    source_xyz = numbers(source.get("pos"), (0.0, 0.0, 0.0))
    generated_xyz = numbers(generated_origin.get("xyz"), (0.0, 0.0, 0.0))
    if len(source_xyz) != 3 or len(generated_xyz) != 3:
        raise ValueError("Pose translation must have three values")
    translation_error = max(
        abs(source_value - generated_value)
        for source_value, generated_value in zip(
            source_xyz, generated_xyz, strict=True
        )
    )

    source_quaternion = numbers(source.get("quat"), (1.0, 0.0, 0.0, 0.0))
    if len(source_quaternion) != 4:
        raise ValueError("Source quaternion must have four values")
    quaternion_norm = sum(value * value for value in source_quaternion) ** 0.5
    if quaternion_norm <= 0.0:
        raise ValueError("Source quaternion has zero length")
    source_matrix = rotation_matrix_from_quaternion(
        tuple(value / quaternion_norm for value in source_quaternion)
    )

    generated_rpy = numbers(generated_origin.get("rpy"), (0.0, 0.0, 0.0))
    if len(generated_rpy) != 3:
        raise ValueError("Generated RPY must have three values")
    generated_matrix = rotation_matrix_from_rpy(generated_rpy)
    rotation_error = max(
        abs(source_matrix[row][column] - generated_matrix[row][column])
        for row in range(3)
        for column in range(3)
    )
    return translation_error, rotation_error


def main() -> int:
    args = parse_args()
    if not args.mjcf.is_file():
        raise FileNotFoundError(args.mjcf)
    if not args.xacro.is_file():
        raise FileNotFoundError(args.xacro)

    source_root = ET.parse(args.mjcf).getroot()
    generated_root = ET.parse(args.xacro).getroot()
    source_world_body = source_root.find("worldbody/body")
    if source_world_body is None:
        raise ValueError("MJCF has no root body")

    generated_links = {
        link.get("name", ""): link for link in generated_root.findall("link")
    }
    generated_joints = {}
    for joint in generated_root.findall("joint"):
        child = joint.find("child")
        if child is not None:
            generated_joints[child.get("link", "")] = joint

    mesh_files = {}
    for mesh in source_root.findall("asset/mesh"):
        filename = mesh.get("file")
        if not filename:
            raise ValueError("MJCF mesh asset has no file")
        mesh_files[mesh.get("name") or Path(filename).stem] = Path(filename).name

    counts = {
        "body_joint_poses": 0,
        "inertial_poses": 0,
        "visual_poses": 0,
        "collision_poses": 0,
    }
    skipped_self_collision_geometries = 0
    max_translation_error = 0.0
    max_rotation_error = 0.0

    def compare(source: ET.Element, generated: ET.Element | None, label: str) -> None:
        nonlocal max_translation_error, max_rotation_error
        if generated is None:
            raise ValueError(f"Generated pose is missing for {label}")
        translation_error, rotation_error = pose_errors(source, generated)
        max_translation_error = max(max_translation_error, translation_error)
        max_rotation_error = max(max_rotation_error, rotation_error)
        if translation_error > TRANSLATION_TOLERANCE_M:
            raise ValueError(
                f"Translation mismatch for {label}: {translation_error} m"
            )
        if rotation_error > ROTATION_MATRIX_TOLERANCE:
            raise ValueError(
                f"Rotation mismatch for {label}: matrix error {rotation_error}"
            )

    def check_body(body: ET.Element, is_root: bool = False) -> None:
        nonlocal skipped_self_collision_geometries
        name = body.get("name")
        if not name or name not in generated_links:
            raise ValueError(f"Generated link is missing for MJCF body {name!r}")
        link = generated_links[name]

        source_inertial = body.find("inertial")
        if source_inertial is None:
            raise ValueError(f"MJCF body {name} has no inertial pose")
        compare(source_inertial, link.find("inertial/origin"), f"{name} inertial")
        counts["inertial_poses"] += 1

        if not is_root:
            joint = generated_joints.get(name)
            compare(
                body,
                joint.find("origin") if joint is not None else None,
                f"{name} joint",
            )
            counts["body_joint_poses"] += 1

        for kind, source_class, count_key in (
            ("visual", "visual", "visual_poses"),
            ("collision", "collision", "collision_poses"),
        ):
            source_geometries = [
                geom for geom in body.findall("geom") if geom.get("class") == source_class
            ]
            generated_geometries = link.findall(f".//{kind}")
            if len(source_geometries) != len(generated_geometries):
                raise ValueError(
                    f"{name} {kind} count differs: "
                    f"{len(source_geometries)} != {len(generated_geometries)}"
                )
            for index, (source_geom, generated_geom) in enumerate(
                zip(source_geometries, generated_geometries, strict=True)
            ):
                mesh_name = source_geom.get("mesh")
                generated_mesh = generated_geom.find("geometry/mesh")
                generated_filename = (
                    Path(generated_mesh.get("filename", "")).name
                    if generated_mesh is not None
                    else ""
                )
                if not mesh_name or mesh_files.get(mesh_name) != generated_filename:
                    raise ValueError(
                        f"Mesh mapping differs for {name} {kind} {index}: "
                        f"{mesh_name!r} -> {generated_filename!r}"
                    )
                compare(
                    source_geom,
                    generated_geom.find("origin"),
                    f"{name} {kind} {index}",
                )
                counts[count_key] += 1

        skipped_self_collision_geometries += sum(
            geom.get("class") == "self_collision_only" for geom in body.findall("geom")
        )
        for child in body.findall("body"):
            check_body(child)

    check_body(source_world_body, is_root=True)
    poses_checked = sum(counts.values())
    checks = {
        "physical_links_match": len(generated_links) == 16,
        "body_joint_pose_count_14": counts["body_joint_poses"] == 14,
        "inertial_pose_count_15": counts["inertial_poses"] == 15,
        "visual_pose_count_70": counts["visual_poses"] == 70,
        "collision_pose_count_10": counts["collision_poses"] == 10,
        "self_collision_geometry_deliberately_skipped": (
            skipped_self_collision_geometries == 1
        ),
        "all_translations_match": (
            max_translation_error <= TRANSLATION_TOLERANCE_M
        ),
        "all_rotation_matrices_match": (
            max_rotation_error <= ROTATION_MATRIX_TOLERANCE
        ),
    }
    report = {
        "source_mjcf": relative_path(args.mjcf),
        "source_revision": upstream_sha(args.mjcf),
        "generated_xacro": relative_path(args.xacro),
        "poses_checked": poses_checked,
        **counts,
        "skipped_self_collision_geometries": skipped_self_collision_geometries,
        "translation_tolerance_m": TRANSLATION_TOLERANCE_M,
        "rotation_matrix_tolerance": ROTATION_MATRIX_TOLERANCE,
        "max_translation_error_m": max_translation_error,
        "max_rotation_matrix_error": max_rotation_error,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
