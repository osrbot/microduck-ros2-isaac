# MicroDuck upstream notice

This community project is based on public work by Pollen Robotics:

- MicroDuck RL: <https://github.com/pollen-robotics/microduck_rl>
- MicroDuck runtime: <https://github.com/pollen-robotics/microduck>
- Product page: <https://pollen-robotics.com/microduck/>

The exact source revisions used by this project are recorded in
`upstream.lock`.

The upstream `microduck_rl` README states that its code is licensed under the
Apache License 2.0 and that its 3D model files are licensed under
"Creative Commons BY-SA-NC". The upstream notice does not identify a Creative
Commons license version, so this project preserves that wording and does not
claim a version on Pollen Robotics' behalf.

Derived URDF, USD, mesh packages, and other robot-description data remain
identified as derivatives of the upstream MicroDuck 3D model. Original code
written for this compatibility project is licensed separately under the
Apache License 2.0.

Changes made by this project include format conversion, ROS 2 packaging,
Isaac Sim articulation configuration, validation metadata, and documentation.
No affiliation with or endorsement by Pollen Robotics is implied.

## Documentation images

- `docs/public/media/continuous-roll/` contains project-recorded Isaac simulation
  video and a frame extracted from that video. The robot is rendered from the
  upstream-derived MicroDuck USD. The model attribution and terms above remain
  applicable. `README.md` in that media directory records the source session,
  editing scope, and original-video checksum; no trained weights are distributed
  in that directory.

- `docs/public/images/microduck-lineup.webp` is an unmodified copy of the image
  linked from the official Pollen Robotics `microduck` README. Its source is
  <https://github.com/user-attachments/assets/c2f7c245-8217-46a1-8d1e-e0ba967cd969>.
- `docs/public/images/microduck-waddle-lab.webp` is an original project
  illustration generated with the official lineup image as a subject reference.
  It is decorative artwork, not a screenshot or simulation result.
- `docs/public/images/play-duck-sticker.webp` is an original project
  illustration generated from a user-supplied meme only as a mood and gesture
  reference. The source bitmap is not included. The sticker itself is static;
  its optional movement on the website is implemented with CSS.
- `docs/public/images/hero-microduck-meme.webp` is an original project
  illustration generated from the same user-supplied meme as a mood and gesture
  reference and the official MicroDuck lineup as a hardware identity reference.
  It is a decorative hybrid mascot, not a hardware or simulation screenshot.
- `docs/public/images/isaac-usd-preview.webp` is rendered from the USD bundled in
  this repository.
- `docs/public/images/rviz-missing-parts.png` is a user-supplied runtime
  screenshot included as a troubleshooting example.
- `docs/public/images/joint-state-publisher-gui-official.png` is an unmodified
  copy of the screenshot shipped with the ROS `joint_state_publisher_gui`
  package. Its source is
  <https://github.com/ros/joint_state_publisher/blob/ros2/joint_state_publisher_gui/screenshot.png>.
  The package is distributed under the BSD license recorded alongside the
  screenshot in the upstream repository; the complete notice is preserved in
  `docs/public/images/joint-state-publisher-gui-official.LICENSE.txt`.
