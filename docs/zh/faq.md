# 常见问题

## 仓库中已经有 URDF 和 USD 吗？

有。仓库包含生成的 ROS Xacro/网格和 Isaac USD，它们都派生自固定版本上游 MJCF，并继续受上游模型条款约束。

## 已经有 ROS 2 包吗？

有，包名是 `microduck_description`，提供机器人描述、网格、惯性、TF/RViz launch、官方 home pose publisher 和可选关节滑块。

## Isaac Sim 可以直接用吗？

在已记录主机上，包含的 USD 和 runner 可用于 Isaac Sim 6.0.1 中经过检查的策略回放。这不等于已经有原生 Isaac Lab 训练任务。

## ROS 能控制 Isaac 或实体机器人吗？

不能。当前没有 ROS-to-Isaac bridge、`ros2_control`、硬件驱动或舵机标定。

## 为什么只有 14 个关节，不是 15 个执行器？

已发布 MJCF 和策略定义 14 个可动关节。实体运行时提到的嘴部执行器不在该仿真/策略契约中，因此不猜测其行为。

## 惯性和模型位姿验证过吗？

15 个物理惯性矩阵都正定，总质量在源/ROS/Isaac 一致；109 个源到 ROS 位姿矩阵通过容差。这证明转换一致性，不等于独立测量过量产硬件。

## 为什么 MuJoCo 和 Isaac 走得不一样？

两个引擎的接触和执行器模型不同。已记录运行都保持 finite/upright，但项目明确不声明轨迹一致。

## 可以商业使用这些资产吗？

不要默认可以。上游将 3D 文件称为“Creative Commons BY-SA-NC”但未给版本。涉及商业、赞助或变现时请阅读[许可说明](/zh/project/licensing)，并向 Pollen Robotics 澄清。
