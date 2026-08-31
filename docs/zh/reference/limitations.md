# 已知限制

## Isaac 回放不等于训练环境

当前 USD 和运行器支持检查、扩展与策略回放，但没有实现上游 reward、训练噪声、reset、curriculum、多环境复制或原生 Isaac Lab task API。

运行器采用简化 implicit-PD：刚度 0.55 N·m/rad、阻尼 0.053 N·m·s/rad、effort limit 0.96 N·m；上游更详细地建模 BAM XL330 的电气、摩擦、饱和、电池和延迟。

## 行为 smoke parity 不是轨迹一致

两个引擎在已记录场景都保持直立，但位移和横向漂移差异明显。不能把当前 Isaac 的轨迹或 reward 当作上游 MuJoCo 的数值替代。

## ROS 目前以描述为主

包内提供几何、运动学、惯性、TF、RViz 与 home pose，不提供 `ros2_control`、Dynamixel 通信、ROS 到 Isaac bridge、标定或硬件验收。

Xacro 默认速度上限 6.0 rad/s 是仿真/规划占位值，不是权威硬件安全极限。

## 嘴部执行器不在模型中

选定 MJCF 和策略只有 14 个可动关节。上游实体运行时还提到一个嘴部执行器，但仿真模型没有给出其几何、惯性、极限和策略行为，本项目不会猜测。

## 碰撞过滤仍是简化实现

Isaac 导入器丢失 MJCF collision bitmask，因此当前把一处 `self_collision_only` 传感器网格从一般碰撞中禁用。精确选择性自碰撞仍需经过验证的 PhysX collision groups。

## GUI 证据依赖主机

包装脚本只对项目启动隔离重复 NVIDIA ICD，不等于修复系统驱动。绕过脚本启动 Isaac 仍可能崩溃。ROS visual 约 79.7 万三角形，4K 远程桌面还可能受编码和网络限制。

## 模型再分发许可需上游澄清

Pollen Robotics 把 3D 文件描述为“Creative Commons BY-SA-NC”，但没有提供版本。在获得确切说明前，派生资产应按非商业、署名、相同方式共享处理。详见[许可边界](/zh/project/licensing)。
