# Licensing and publication boundary

This is a mixed-license repository. Do not describe the bundled project as
Apache-only.

## Original compatibility work

Scripts, ROS packaging, launch files, validators, and documentation written for
this project are licensed under Apache-2.0. The root `LICENSE` applies to those
original contributions.

## Upstream-derived robot assets

STL meshes, generated Xacro, and generated USD derive from Pollen Robotics'
MicroDuck 3D model. The upstream `microduck_rl` README calls those files
“Creative Commons BY-SA-NC” but does not identify a version. This project
preserves that wording instead of selecting a license version on the author's
behalf.

For publication:

- preserve Pollen Robotics attribution and `NOTICE-MICRODUCK.md`;
- treat model derivatives as non-commercial and share-alike while the exact
  license remains unclear;
- do not claim that every file is OSI-approved open-source;
- request written clarification before commercial, sponsored, or monetized use
  where the non-commercial restriction may matter.

Released ONNX policies are fetched to ignored `reference/` directories and are
not bundled. Users remain responsible for upstream terms.

This is a conservative engineering publication boundary, not legal advice.
