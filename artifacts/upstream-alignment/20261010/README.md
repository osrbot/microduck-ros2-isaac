# October 2026 local alignment evidence

These reports were produced on 2026-10-10. They cover pinned-source identity,
ONNX contracts, MJCF-to-ROS structure/poses, and short MuJoCo CPU probes.
They do not establish new-source Isaac/PhysX playback, ROS/RViz runtime,
robustness, real-robot operation, or newly trained skills.

- `upstream_inventory.json`: current source identities, v7 download hashes,
  model structure and ten ONNX contracts.
- `generated_description_installed.json`, `urdf_inventory_installed.json`,
  `mjcf_urdf_pose_parity_installed.json`, `microduck.urdf`: the installed ROS
  description, 38 mesh references, 14 movable joints and 109 pose comparisons.
- `mujoco_stand_zero_command_scale_1_0.json`: five-second standing probe.
- `mujoco_walk_vx_0_3_scale_0_9.json`: ten-second walking probe.
- `velstand_groundcontact_probe.json`: ten-second flat-ground compatibility
  probe only; not the Rough + Backlash environment or recovery validation.
- `legacy_usd_inventory.json`: structural check of the unchanged historical USD.

The final tutorial default keeps all seven historical playground weight hashes.
The v7 sitting policy in the inventory is **not** the default sitting weight.
`upstream.lock` separately pins the original runtime's sit/stand weight as
`playground_sitstand`; `tests/test_upstream_alignment.py` checks that boundary.
The downloader checks all 13 files, including that historical weight.

See the bilingual `docs/reference/upstream-alignment.md` and
`docs/zh/reference/upstream-alignment.md` for commands and limitations.
