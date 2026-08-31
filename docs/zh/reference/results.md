# 已记录验证结果

验证日期：2026-08-31（Asia/Shanghai）。`artifacts/` 下 JSON 是机器可读证据，本页是人工摘要。

## 输入与结构

- `microduck_rl`：`d424a0c899f6b33cbd3daeb279913134349c0b63`
- `microduck`：`590b986bd8c0d50ae02cb3ea2f59c463b6828168`
- 9 个已发布策略：输入宽度 61，输出宽度 14。
- 物理模型总质量约 0.737243 kg。
- 15 个物理刚体，14 个可动关节。

## 策略 rollout

| 引擎与场景 | 时长 | 最终根坐标 xyz（m） | 最大倾角 | 结果 |
| --- | ---: | --- | ---: | --- |
| MuJoCo 行走，`vx=0.3`，scale 0.9 | 10 s | `[1.151052, -0.217529, 0.117609]` | 0.063937 rad | finite、upright |
| Isaac 站立，scale 1.0 | 5 s | `[0.001080, -0.000970, 0.116149]` | 0.022275 rad | finite、upright |
| Isaac 行走，`vx=0.3`，scale 0.9 | 10 s | `[1.481570, 0.412802, 0.118544]` | 0.068429 rad | finite、upright |
| Isaac Kit 行走，同一命令 | 60 s | `[-0.086344, 6.222491, 0.120011]` | 0.068429 rad | finite、upright、正常退出 |

配对的 10 秒行走在相同命令、scale 和时序下都保持有限值和直立，最终高度相差 0.000935 m，最大倾角相差 0.004493 rad。

但前向位移相差约 28.7%，横向漂移的大小和方向也不同，因此明确不能称为轨迹一致。Isaac 使用 PhysX 接触和简化 implicit-PD；上游训练使用 MuJoCo 与更详细的 BAM XL330 模型。

## USD 结构

- 15 个刚体、14 个旋转关节。
- 81 个带 collision API 的网格实例。
- 10 个碰撞网格启用。
- 70 个 visual 加一处源传感器网格的碰撞禁用。
- 单位、坐标轴、极限、articulation root、质量和名称均通过检查。

## ROS 2 描述

- 无质量 `base_link`、15 个物理 link、1 个固定根关节、14 个旋转关节。
- 70 个 visual、10 个 collision、38 个唯一网格文件。
- visual 约 796,792 个三角形；可选 collision 额外约 171,146 个。
- 15 个物理惯性矩阵均为正定。
- 比较 109 个位姿矩阵：平移误差 0 m，最大旋转矩阵误差 `4.90e-12`，容差为 `1e-9`。
- Xacro、`check_urdf`、colcon build、5/5 ament tests 均通过。
- 运行时收到所需节点、描述、home JointState 和 `world -> ankle_left` TF。

## GUI 证据

RViz 在已验证主机全屏运行 75 秒，自动输入确认默认 Orbit 旋转与缩放；关节 GUI 改变 14 个关节后，TF 和画面都变化。导致颈部和腿部看似分离的四元数奇异点问题已修复，并由 109 位姿对比防回归。

首次 60 秒 Isaac Kit 运行复现了重复 Vulkan ICD 引起的 GPU crash。包装脚本选择单一 ICD 并关闭多 GPU 后，同一仿真正常完成、退出码为 0，且没有新 GPU dump。

这些结果不证明原生训练一致、实体硬件行为或最终直播画面已经验收。
