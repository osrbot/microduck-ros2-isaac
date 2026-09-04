# 测试过的环境

记录日期：2026-08-31（Asia/Shanghai）。这是已知可工作的测试矩阵，不代表其他版本一定不可用。

## 主机与软件

- Ubuntu 24.04.4 LTS，x86_64
- NVIDIA GeForce RTX 4080 SUPER，16 GB VRAM
- NVIDIA driver 595.91.07
- 30 GB 系统内存
- ROS 2 Jazzy，Python 3.12.3
- Isaac Sim 6.0.1 standalone
- Isaac Lab 3.0.0 beta 2，提交 `2e44ddb2e19536579140496023b5ccb060bc4152`
- ONNX Runtime 1.24.4，CPU execution provider

## Python 边界

主机交互 `PATH` 中用户 Python 3.11 位于 Ubuntu Python 3.12 之前。ROS 验证包装脚本会把 `/usr/bin` 放在前面并显式调用 `/usr/bin/python3`，避免把无关用户环境误判成 ROS 故障。

Isaac 使用的 ONNX Runtime 安装在 `work/isaac_python_pkgs`。项目把外部 Isaac Lab checkout 当作只读运行时。

## 显示与 GPU

RViz 在 Xorg 桌面和 OpenGL 4.6 下验证。主机通过 `/usr/share/.../nvidia_icd.json` 与 `/etc/.../nvidia_icd.json` 重复暴露同一 GPU，原始 Isaac Kit 运行复现了 `ERROR_DEVICE_LOST`。选择单一 ICD 并关闭多 GPU 渲染后，60 秒仿真正常退出。

包装脚本不会删除或修改系统驱动文件。不同 GPU、驱动、Wayland/Xorg 或 Isaac 版本都应视为新的验证矩阵。

## 连续翻滚案例补充

2026-09-04 的[连续翻滚实验](../isaac/continuous-roll)沿用上述 Isaac 环境；训练记录中的 RSL-RL 为 5.0.1。
Actor 热启动需要 Isaac Python 中的 `onnx`，原 ONNX 直接回放需要项目内的 `onnxruntime`。
先执行专题的依赖预检，再跑 64 环境、5 次更新的短测试；训练与回放使用同一套 Python、模型和动作接口。
