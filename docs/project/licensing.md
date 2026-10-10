# Licensing and publication boundary

This is a mixed-license repository. Do not describe the bundled project as
Apache-only.

## Original compatibility work

Scripts, ROS packaging, launch files, validators, and documentation written for
this project are licensed under Apache-2.0. The root `LICENSE` applies to those
original contributions.

## Upstream-derived robot assets

The October 2026 pinned upstream [LICENSE-MODELS.md](https://github.com/pollen-robotics/microduck_rl/blob/ceca01706143d729305baa94cbd8ab990979e325/LICENSE-MODELS.md)
explicitly separates STL meshes (**CC BY-NC-SA 4.0**) from MJCF XML, export
configuration and `.part` metadata (**Apache-2.0**). This replaces the earlier
version-unspecified notice; it is not a license version chosen by this project.

The generated Xacro description is Apache-2.0, but its referenced STL meshes
remain CC BY-NC-SA 4.0. USD contains converted mesh geometry and must retain
those mesh terms. The historical bundled USD also retains its original source
identity; the update does not claim it was regenerated.

For publication:

- preserve Pollen Robotics attribution and `NOTICE-MICRODUCK.md`;
- retain [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
  notices and identify changes to mesh adaptations;
- do not claim that every file is OSI-approved open-source;
- request written clarification before commercial, sponsored, or monetized use
  where the non-commercial restriction may matter.

Released ONNX policies are fetched to ignored `reference/policies/v7/` and are
not bundled. The model card at the locked Hub revision declares Apache-2.0;
the downloader retains that card and checks its SHA-256 along with the weights.
The separately retained historical sit/stand weight comes from the Apache-2.0
[runtime revision](https://github.com/pollen-robotics/microduck/blob/590b986bd8c0d50ae02cb3ea2f59c463b6828168/LICENSE)
recorded in `upstream.lock`; it is also downloaded to ignored `reference/`, not bundled.

This is a conservative engineering publication boundary, not legal advice.
