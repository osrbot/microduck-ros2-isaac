# MicroDuck upstream notice

This community project is based on public work by Pollen Robotics:

- MicroDuck RL: <https://github.com/pollen-robotics/microduck_rl>
- MicroDuck runtime: <https://github.com/pollen-robotics/microduck>
- Product page: <https://pollen-robotics.com/microduck/>

The exact source revisions used by this project are recorded in
`upstream.lock`.

The upstream [LICENSE-MODELS.md](https://github.com/pollen-robotics/microduck_rl/blob/ceca01706143d729305baa94cbd8ab990979e325/LICENSE-MODELS.md)
now explicitly licenses the STL meshes under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
It separately licenses MJCF XML, export configuration and Onshape part metadata
under Apache-2.0. The generated Xacro description and original integration code
are Apache-2.0; the referenced/copied STL meshes retain Pollen Robotics'
CC BY-NC-SA 4.0 terms. Converted mesh geometry also retains the mesh terms.
Do not describe a package containing both as Apache-only.

The new ROS mesh set was copied without geometry edits from the locked source;
SHA-256 values are in `ros2_ws/src/microduck_description/meshes/SHA256SUMS`.
The bundled historical Isaac USD retains its original source commit in
`upstream.lock`; it has not been regenerated or relabeled as the October model.
It contains converted mesh geometry, not just Apache-licensed XML.

Official ONNX weights are downloaded separately from
[pollen-robotics/microduck-policies](https://huggingface.co/pollen-robotics/microduck-policies)
at the immutable revision in `upstream.lock`. That revision's model card declares
Apache-2.0. The weights and source checkouts live in ignored `reference/`, not in
this repository's source distribution.
The playground separately retains the historical sit/stand weight from runtime
commit `590b986bd8c0d50ae02cb3ea2f59c463b6828168`, whose root license is Apache-2.0.
Its source and SHA-256 are pinned in `upstream.lock`; it is downloaded, not bundled.

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
