#!/usr/bin/env python3
"""Validate the expanded MicroDuck URDF contract and write a compact inventory."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URDF = PROJECT_ROOT / "work/ros_validation/microduck.urdf"
DEFAULT_PACKAGE_DIR = PROJECT_ROOT / "ros2_ws/src/microduck_description"
DEFAULT_OUTPUT = PROJECT_ROOT / "artifacts/ros/urdf_inventory.json"

POLICY_JOINTS = (
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
)


def relative_path(path: Path) -> str:
    """Return a project-relative path where possible for public evidence."""
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--urdf", type=Path, default=DEFAULT_URDF)
    parser.add_argument("--package-dir", type=Path, default=DEFAULT_PACKAGE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def positive_definite_inertia(inertia: ET.Element) -> bool:
    """Check positive definiteness of the symmetric 3x3 inertia tensor."""
    ixx = float(inertia.get("ixx", "nan"))
    iyy = float(inertia.get("iyy", "nan"))
    izz = float(inertia.get("izz", "nan"))
    ixy = float(inertia.get("ixy", "nan"))
    ixz = float(inertia.get("ixz", "nan"))
    iyz = float(inertia.get("iyz", "nan"))
    det2 = ixx * iyy - ixy * ixy
    det3 = (
        ixx * (iyy * izz - iyz * iyz)
        - ixy * (ixy * izz - iyz * ixz)
        + ixz * (ixy * iyz - iyy * ixz)
    )
    return all(math.isfinite(value) for value in (ixx, iyy, izz, det2, det3)) and (
        ixx > 0.0 and det2 > 0.0 and det3 > 0.0
    )


def main() -> int:
    args = parse_args()
    if not args.urdf.is_file():
        raise FileNotFoundError(args.urdf)
    root = ET.parse(args.urdf).getroot()
    if root.tag != "robot" or root.get("name") != "microduck":
        raise ValueError("Expanded description is not robot 'microduck'")

    links = root.findall("link")
    joints = root.findall("joint")
    revolute_joints = [joint for joint in joints if joint.get("type") == "revolute"]
    joint_names = tuple(joint.get("name", "") for joint in revolute_joints)
    link_names = {link.get("name", "") for link in links}
    child_links = {
        child.get("link", "") for joint in joints if (child := joint.find("child")) is not None
    }
    root_links = sorted(link_names - child_links)

    masses = []
    positive_inertias = True
    for link in links:
        inertial = link.find("inertial")
        if link.get("name") == "base_link" and inertial is None:
            continue
        if inertial is None:
            raise ValueError(f"Link {link.get('name')} lacks inertia")
        mass = inertial.find("mass")
        inertia = inertial.find("inertia")
        if mass is None or inertia is None:
            raise ValueError(f"Link {link.get('name')} has incomplete inertia")
        masses.append(float(mass.get("value", "nan")))
        positive_inertias = positive_inertias and positive_definite_inertia(inertia)

    mesh_elements = root.findall(".//mesh")
    missing_meshes = []
    mesh_filenames = []
    prefix = "package://microduck_description/meshes/"
    for mesh in mesh_elements:
        filename = mesh.get("filename", "")
        if not filename.startswith(prefix):
            missing_meshes.append(filename)
            continue
        mesh_name = filename.removeprefix(prefix)
        mesh_filenames.append(mesh_name)
        if not (args.package_dir / "meshes" / mesh_name).is_file():
            missing_meshes.append(filename)

    limits_valid = True
    velocities = set()
    efforts = set()
    for joint in revolute_joints:
        limit = joint.find("limit")
        if limit is None:
            limits_valid = False
            continue
        lower = float(limit.get("lower", "nan"))
        upper = float(limit.get("upper", "nan"))
        effort = float(limit.get("effort", "nan"))
        velocity = float(limit.get("velocity", "nan"))
        limits_valid = limits_valid and all(
            math.isfinite(value) for value in (lower, upper, effort, velocity)
        )
        limits_valid = limits_valid and lower < upper and effort > 0.0 and velocity > 0.0
        velocities.add(velocity)
        efforts.add(effort)

    checks = {
        "physical_link_count_15_plus_base_link": len(links) == 16,
        "joint_count_14_revolute_plus_1_fixed": len(joints) == 15,
        "revolute_joint_count_14": len(revolute_joints) == 14,
        "joint_contract_matches": joint_names == POLICY_JOINTS,
        "root_is_massless_base_link": root_links == ["base_link"],
        "total_mass_matches_mjcf": math.isclose(sum(masses), 0.737243, abs_tol=1e-6),
        "all_inertias_positive_definite": positive_inertias,
        "all_joint_limits_valid": limits_valid,
        "all_meshes_resolve": not missing_meshes,
        "mouth_joint_absent": "mouth" not in joint_names,
    }
    report = {
        "urdf": relative_path(args.urdf),
        "links": len(links),
        "physical_links": len(links) - 1,
        "joints": len(joints),
        "fixed_joints": len([joint for joint in joints if joint.get("type") == "fixed"]),
        "revolute_joints": len(revolute_joints),
        "root_links": root_links,
        "joint_names": list(joint_names),
        "total_mass_kg": sum(masses),
        "visual_mesh_instances": len(root.findall(".//visual/geometry/mesh")),
        "collision_mesh_instances": len(root.findall(".//collision/geometry/mesh")),
        "unique_mesh_files": len(set(mesh_filenames)),
        "joint_velocity_limits_rad_s": sorted(velocities),
        "joint_effort_limits_nm": sorted(efforts),
        "missing_meshes": missing_meshes,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
