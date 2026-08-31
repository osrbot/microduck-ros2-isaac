#!/usr/bin/env python3
"""Generate a self-contained ROS 2 Xacro description from the pinned MicroDuck MJCF."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_DIR = (
    PROJECT_ROOT / "reference/microduck_rl/src/mjlab_microduck/robot/microduck"
)
DEFAULT_PACKAGE_DIR = PROJECT_ROOT / "ros2_ws/src/microduck_description"
DEFAULT_REPORT = PROJECT_ROOT / "artifacts/ros/generated_description.json"


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
    parser.add_argument("--mesh-dir", type=Path, default=DEFAULT_MODEL_DIR / "assets")
    parser.add_argument("--package-dir", type=Path, default=DEFAULT_PACKAGE_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--default-velocity-limit",
        type=float,
        default=6.0,
        help=(
            "Simulation/planning fallback in rad/s. The upstream MJCF does not "
            "declare per-joint velocity limits; this value remains a Xacro override."
        ),
    )
    return parser.parse_args()


def numbers(value: str | None, default: tuple[float, ...]) -> tuple[float, ...]:
    """Parse a whitespace-separated MJCF numeric attribute."""
    if value is None:
        return default
    return tuple(float(item) for item in value.split())


def format_numbers(values: tuple[float, ...] | list[float]) -> str:
    """Serialize numbers deterministically while avoiding negative zero."""
    return " ".join(f"{0.0 if abs(value) < 1e-15 else value:.12g}" for value in values)


def rotation_matrix_from_quaternion(
    quaternion: tuple[float, float, float, float],
) -> tuple[tuple[float, float, float], ...]:
    """Return the rotation matrix for an MJCF ``(w, x, y, z)`` quaternion."""
    w, x, y, z = quaternion
    return (
        (
            1.0 - 2.0 * (y * y + z * z),
            2.0 * (x * y - w * z),
            2.0 * (x * z + w * y),
        ),
        (
            2.0 * (x * y + w * z),
            1.0 - 2.0 * (x * x + z * z),
            2.0 * (y * z - w * x),
        ),
        (
            2.0 * (x * z - w * y),
            2.0 * (y * z + w * x),
            1.0 - 2.0 * (x * x + y * y),
        ),
    )


def rotation_matrix_from_rpy(
    rpy: tuple[float, float, float],
) -> tuple[tuple[float, float, float], ...]:
    """Return the URDF fixed-axis ``Rz(yaw) * Ry(pitch) * Rx(roll)`` matrix."""
    roll, pitch, yaw = rpy
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    return (
        (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
        (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
        (-sp, cp * sr, cp * cr),
    )


def quaternion_wxyz_to_rpy(quaternion: tuple[float, ...]) -> tuple[float, float, float]:
    """Convert an MJCF quaternion to an equivalent fixed-axis URDF RPY.

    The usual independent ``atan2`` formulas lose the coupled roll/yaw angle
    at exactly +/-90 degrees of pitch.  Many MicroDuck CAD mesh frames sit on
    that singularity, so preserve the remaining angle explicitly instead of
    silently rotating those meshes to a different orientation.
    """
    if len(quaternion) != 4:
        raise ValueError(f"Quaternion must have four values: {quaternion}")
    w, x, y, z = quaternion
    norm = math.sqrt(w * w + x * x + y * y + z * z)
    if norm <= 0.0:
        raise ValueError("Zero-length quaternion")
    normalized = tuple(item / norm for item in (w, x, y, z))
    matrix = rotation_matrix_from_quaternion(normalized)
    sin_pitch = max(-1.0, min(1.0, -matrix[2][0]))

    if math.isclose(abs(sin_pitch), 1.0, abs_tol=1e-10):
        pitch = math.copysign(math.pi / 2.0, sin_pitch)
        yaw = 0.0
        if sin_pitch > 0.0:
            roll = math.atan2(matrix[0][1], matrix[0][2])
        else:
            roll = math.atan2(-matrix[0][1], -matrix[0][2])
    else:
        pitch = math.asin(sin_pitch)
        roll = math.atan2(matrix[2][1], matrix[2][2])
        yaw = math.atan2(matrix[1][0], matrix[0][0])

    rpy = (roll, pitch, yaw)
    reconstructed = rotation_matrix_from_rpy(rpy)
    max_error = max(
        abs(matrix[row][column] - reconstructed[row][column])
        for row in range(3)
        for column in range(3)
    )
    if max_error > 1e-9:
        raise ValueError(
            "Quaternion cannot be represented by the generated URDF RPY "
            f"within tolerance: {quaternion}, max matrix error {max_error}"
        )
    return rpy


def add_origin(parent: ET.Element, source: ET.Element) -> None:
    """Copy MJCF local pose attributes to a URDF origin."""
    xyz = numbers(source.get("pos"), (0.0, 0.0, 0.0))
    rpy = quaternion_wxyz_to_rpy(numbers(source.get("quat"), (1.0, 0.0, 0.0, 0.0)))
    ET.SubElement(
        parent,
        "origin",
        {"xyz": format_numbers(xyz), "rpy": format_numbers(rpy)},
    )


def upstream_sha(mjcf: Path) -> str:
    """Resolve the pinned source revision from the containing reference clone."""
    current = mjcf.resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=candidate,
                text=True,
                check=True,
                capture_output=True,
            )
            return result.stdout.strip()
    return "unknown"


def actuator_properties(root: ET.Element) -> dict[str, float]:
    """Read the selected MJCF actuator class instead of duplicating its constants."""
    chosen = root.find(".//default[@class='chosen_actuator']")
    if chosen is None:
        raise ValueError("MJCF has no chosen_actuator default class")
    joint = chosen.find("joint")
    position = chosen.find("position")
    if joint is None or position is None:
        raise ValueError("chosen_actuator lacks joint or position properties")
    force_range = numbers(position.get("forcerange"), ())
    if len(force_range) != 2:
        raise ValueError("chosen_actuator has no two-sided forcerange")
    return {
        "effort_limit": max(abs(force_range[0]), abs(force_range[1])),
        "damping": float(joint.get("damping", "0")),
        "friction": float(joint.get("frictionloss", "0")),
        "armature": float(joint.get("armature", "0")),
    }


def generate(args: argparse.Namespace) -> dict[str, object]:
    """Generate Xacro and copy only meshes that the source model actually uses."""
    if args.default_velocity_limit <= 0.0:
        raise ValueError("--default-velocity-limit must be positive")
    if not args.mjcf.is_file():
        raise FileNotFoundError(args.mjcf)
    if not args.mesh_dir.is_dir():
        raise FileNotFoundError(args.mesh_dir)

    source_root = ET.parse(args.mjcf).getroot()
    world_body = source_root.find("worldbody/body")
    if world_body is None:
        raise ValueError("MJCF has no root body")

    mesh_files: dict[str, str] = {}
    for mesh in source_root.findall("asset/mesh"):
        filename = mesh.get("file")
        if not filename:
            raise ValueError("MJCF mesh asset has no file")
        name = mesh.get("name") or Path(filename).stem
        mesh_files[name] = filename

    materials: dict[str, tuple[float, ...]] = {}
    for material in source_root.findall("asset/material"):
        name = material.get("name")
        if name:
            rgba = numbers(material.get("rgba"), (0.7, 0.7, 0.7, 1.0))
            if len(rgba) != 4:
                raise ValueError(f"Material {name} does not have RGBA")
            materials[name] = rgba

    properties = actuator_properties(source_root)
    revision = upstream_sha(args.mjcf)
    robot = ET.Element(
        "robot", {"name": "microduck", "xmlns:xacro": "http://www.ros.org/wiki/xacro"}
    )
    robot.append(
        ET.Comment(
            " Generated from Pollen Robotics microduck_rl "
            f"robot_allcollisions.xml at {revision}. Do not hand-edit generated geometry. "
        )
    )
    ET.SubElement(robot, "xacro:arg", {"name": "with_visual_meshes", "default": "true"})
    ET.SubElement(robot, "xacro:arg", {"name": "with_collision_meshes", "default": "true"})
    ET.SubElement(
        robot,
        "xacro:arg",
        {
            "name": "joint_velocity_limit",
            "default": format_numbers([args.default_velocity_limit]),
        },
    )
    robot.append(
        ET.Comment(
            " joint_velocity_limit is a documented simulation/planning fallback; "
            "the upstream MJCF does not provide authoritative per-joint velocity limits. "
        )
    )

    used_materials = {
        geom.get("material")
        for geom in source_root.findall(".//worldbody//geom")
        if geom.get("class") == "visual" and geom.get("material")
    }
    if any(
        geom.get("class") == "visual" and not geom.get("material")
        for geom in source_root.findall(".//worldbody//geom")
    ):
        used_materials.add("microduck_default_gray")
    for name in sorted(used_materials):
        material_element = ET.SubElement(robot, "material", {"name": name})
        ET.SubElement(
            material_element,
            "color",
            {"rgba": format_numbers(materials.get(name, (0.7, 0.7, 0.7, 1.0)))},
        )

    # KDL cannot represent inertia on the root link. Keep the 15 physical MJCF
    # bodies unchanged and add one massless ROS frame above trunk_base.
    ET.SubElement(robot, "link", {"name": "base_link"})

    used_meshes: set[str] = set()
    counts = {"links": 0, "revolute_joints": 0, "visuals": 0, "collisions": 0}
    skipped_self_collision_geometries = 0
    total_mass = 0.0

    def add_geometry(
        container: ET.Element,
        link_name: str,
        geom: ET.Element,
        kind: str,
        index: int,
    ) -> None:
        mesh_name = geom.get("mesh")
        if geom.get("type") != "mesh" or not mesh_name:
            raise ValueError("Only named mesh geometries are supported by this source model")
        filename = mesh_files.get(mesh_name)
        if not filename:
            raise ValueError(f"Geometry references unknown mesh {mesh_name}")
        used_meshes.add(filename)
        element = ET.SubElement(
            container, kind, {"name": f"{link_name}_{kind}_{index}"}
        )
        add_origin(element, geom)
        geometry = ET.SubElement(element, "geometry")
        ET.SubElement(
            geometry,
            "mesh",
            {"filename": f"package://microduck_description/meshes/{Path(filename).name}"},
        )
        if kind == "visual":
            ET.SubElement(
                element,
                "material",
                {"name": geom.get("material", "microduck_default_gray")},
            )

    def add_body(body: ET.Element, parent_name: str | None) -> None:
        nonlocal skipped_self_collision_geometries, total_mass
        name = body.get("name")
        if not name:
            raise ValueError("MJCF body has no name")
        link = ET.SubElement(robot, "link", {"name": name})
        counts["links"] += 1

        inertial_source = body.find("inertial")
        if inertial_source is None:
            raise ValueError(f"Body {name} has no explicit inertial")
        mass = float(inertial_source.get("mass", "nan"))
        inertia = numbers(inertial_source.get("fullinertia"), ())
        if not math.isfinite(mass) or mass <= 0.0 or len(inertia) != 6:
            raise ValueError(f"Body {name} has invalid mass/fullinertia")
        total_mass += mass
        inertial = ET.SubElement(link, "inertial")
        add_origin(inertial, inertial_source)
        ET.SubElement(inertial, "mass", {"value": format_numbers([mass])})
        ET.SubElement(
            inertial,
            "inertia",
            {
                "ixx": format_numbers([inertia[0]]),
                "iyy": format_numbers([inertia[1]]),
                "izz": format_numbers([inertia[2]]),
                "ixy": format_numbers([inertia[3]]),
                "ixz": format_numbers([inertia[4]]),
                "iyz": format_numbers([inertia[5]]),
            },
        )

        visual_geometries = [
            geom for geom in body.findall("geom") if geom.get("class") == "visual"
        ]
        if visual_geometries:
            visual_if = ET.SubElement(
                link, "xacro:if", {"value": "$(arg with_visual_meshes)"}
            )
            for index, geom in enumerate(visual_geometries):
                add_geometry(visual_if, name, geom, "visual", index)
                counts["visuals"] += 1

        collision_geometries = [
            geom for geom in body.findall("geom") if geom.get("class") == "collision"
        ]
        if collision_geometries:
            collision_if = ET.SubElement(
                link, "xacro:if", {"value": "$(arg with_collision_meshes)"}
            )
            for index, geom in enumerate(collision_geometries):
                add_geometry(collision_if, name, geom, "collision", index)
                counts["collisions"] += 1
        skipped_self_collision_geometries += sum(
            geom.get("class") == "self_collision_only" for geom in body.findall("geom")
        )

        if parent_name is not None:
            joints = body.findall("joint")
            if len(joints) != 1:
                raise ValueError(f"Body {name} must contain exactly one joint, got {len(joints)}")
            source_joint = joints[0]
            if source_joint.get("type", "hinge") != "hinge":
                raise ValueError(f"Joint {source_joint.get('name')} is not a hinge")
            joint_name = source_joint.get("name")
            limits = numbers(source_joint.get("range"), ())
            if not joint_name or len(limits) != 2:
                raise ValueError(f"Body {name} has an invalid joint")
            joint = ET.SubElement(robot, "joint", {"name": joint_name, "type": "revolute"})
            ET.SubElement(joint, "parent", {"link": parent_name})
            ET.SubElement(joint, "child", {"link": name})
            add_origin(joint, body)
            ET.SubElement(
                joint,
                "axis",
                {"xyz": format_numbers(numbers(source_joint.get("axis"), (0.0, 0.0, 1.0)))},
            )
            ET.SubElement(
                joint,
                "limit",
                {
                    "lower": format_numbers([limits[0]]),
                    "upper": format_numbers([limits[1]]),
                    "effort": format_numbers([properties["effort_limit"]]),
                    "velocity": "$(arg joint_velocity_limit)",
                },
            )
            ET.SubElement(
                joint,
                "dynamics",
                {
                    "damping": format_numbers([properties["damping"]]),
                    "friction": format_numbers([properties["friction"]]),
                },
            )
            counts["revolute_joints"] += 1

        for child in body.findall("body"):
            add_body(child, name)

    add_body(world_body, None)
    root_joint = ET.SubElement(
        robot, "joint", {"name": "base_link_to_trunk_base", "type": "fixed"}
    )
    ET.SubElement(root_joint, "parent", {"link": "base_link"})
    ET.SubElement(root_joint, "child", {"link": world_body.get("name", "trunk_base")})
    ET.SubElement(root_joint, "origin", {"xyz": "0 0 0", "rpy": "0 0 0"})

    package_dir = args.package_dir.resolve()
    xacro_path = package_dir / "urdf/microduck.urdf.xacro"
    mesh_output_dir = package_dir / "meshes"
    xacro_path.parent.mkdir(parents=True, exist_ok=True)
    mesh_output_dir.mkdir(parents=True, exist_ok=True)
    ET.indent(ET.ElementTree(robot), space="  ")
    ET.ElementTree(robot).write(
        xacro_path, encoding="utf-8", xml_declaration=True, short_empty_elements=True
    )

    hashes: list[tuple[str, str]] = []
    for filename in sorted(used_meshes):
        source = args.mesh_dir / filename
        if not source.is_file():
            raise FileNotFoundError(source)
        destination = mesh_output_dir / Path(filename).name
        shutil.copy2(source, destination)
        digest = hashlib.sha256(destination.read_bytes()).hexdigest()
        hashes.append((digest, destination.name))
    (mesh_output_dir / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for digest, name in hashes), encoding="utf-8"
    )

    report = {
        "source_mjcf": relative_path(args.mjcf),
        "source_revision": revision,
        "source_spawn_height_m": float(world_body.get("pos", "0 0 0").split()[2]),
        "xacro": relative_path(xacro_path),
        **counts,
        "ros_frame_links": 1,
        "ros_total_links": counts["links"] + 1,
        "fixed_joints": 1,
        "total_mass_kg": total_mass,
        "unique_meshes": len(used_meshes),
        "skipped_self_collision_geometries": skipped_self_collision_geometries,
        "actuator_from_mjcf": properties,
        "joint_velocity_limit_rad_s": {
            "value": args.default_velocity_limit,
            "provenance": "simulation fallback; not an authoritative hardware limit",
            "xacro_override": "joint_velocity_limit:=<rad_s>",
        },
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def main() -> int:
    report = generate(parse_args())
    return 0 if report["links"] == 15 and report["revolute_joints"] == 14 else 1


if __name__ == "__main__":
    raise SystemExit(main())
