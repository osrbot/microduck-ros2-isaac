# Tested setup

Recorded on 2026-08-31 (Asia/Shanghai). This is a known working matrix, not a
claim that other versions cannot work.

## Host

- Ubuntu 24.04.4 LTS, x86_64
- NVIDIA GeForce RTX 4080 SUPER, 16 GB VRAM
- NVIDIA driver 595.91.07
- 30 GB system memory
- ROS 2 Jazzy and Python 3.12.3
- Isaac Sim 6.0.1 standalone
- Isaac Lab 3.0.0 beta 2 at `2e44ddb2e19536579140496023b5ccb060bc4152`
- ONNX Runtime 1.24.4, CPU execution provider

## Python boundary

The host had a user Python 3.11 ahead of Ubuntu's Python 3.12. ROS validation
wrappers deliberately put `/usr/bin` first and invoke `/usr/bin/python3` so an
unrelated user environment is not mistaken for a ROS failure.

The project installs ONNX Runtime for Isaac into `work/isaac_python_pkgs`. It
treats the external Isaac Lab checkout as read-only.

## Display and GPU notes

RViz was exercised through an active Xorg desktop and OpenGL 4.6. The host
exposed the same GPU through both `/usr/share/vulkan/icd.d/nvidia_icd.json` and
`/etc/vulkan/icd.d/nvidia_icd.json`. The original Isaac Kit run reproduced
`ERROR_DEVICE_LOST`; selecting one ICD and disabling multi-GPU rendering allowed
the 60-second simulation run to exit normally.

The wrapper does not delete or modify system driver files. Treat a different
driver, GPU, Wayland/Xorg setup, or Isaac release as a new validation matrix.
