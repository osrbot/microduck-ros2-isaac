# Retained validation evidence

The JSON files in this directory are outputs of the documented headless run on
2026-08-31. They are retained to make public claims auditable, not to replace a
fresh validation on another machine.

- `baseline/`: pinned upstream inventory and final MuJoCo stand/walk rollouts.
- `isaac/`: USD inventory/post-process evidence, final Isaac stand/walk policy
  rollouts, and the compact 60-second Kit GPU-stability result.
- `parity/`: matched MuJoCo/Isaac behavioral smoke comparison.
- `ros/`: generated-description inventory, 109-pose MJCF/URDF matrix parity,
  expanded-URDF checks, and live ROS graph/JointState/TF smoke result plus RViz
  camera/joint interaction evidence.

Early tuning runs, fixed-home-pose experiments, full GUI logs/traces, ROS launch
logs, and build directories are deliberately excluded. Rebuildable logs belong
in ignored `work/`; only the small machine-readable GUI stability summary is
retained. Visual acceptance and physical hardware remain separate gates.
