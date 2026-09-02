# 常见问题

## 仓库中已经有 URDF 和 USD 吗？

有。仓库包含生成的 ROS Xacro/网格和 Isaac USD，它们都派生自固定版本上游 MJCF，并继续受上游模型条款约束。

## 已经有 ROS 2 包吗？

有，包名是 `microduck_description`，提供机器人描述、网格、惯性、TF/RViz launch、官方 home pose publisher 和可选关节滑块。

## Isaac Sim 可以直接用吗？

可以。包含的 USD 和 runner 支持单策略回放与多动作游乐场；仓库还提供原生 Isaac Lab 平地速度
训练任务。回放公开 ONNX 和训练新 checkpoint 是两条不同路线。

## ROS 能控制 Isaac 或实体机器人吗？

ROS 2 可以通过 `microduck_control_bridge` 遥控本机 Isaac 游乐场并接收关节、策略状态和 TF。它不能
控制实体机器人；项目仍没有 `ros2_control`、硬件驱动或舵机标定。

## Isaac 训练出来的策略能直接上真机吗？

不能直接这样判断。当前任务是 implicit-PD 教学/实验环境，没有复刻上游 BAM 执行器和完整
sim2real 配方，真机部署仍需要单独验证。

## 为什么只有 14 个关节，不是 15 个执行器？

已发布 MJCF 和策略定义 14 个可动关节。实体运行时提到的嘴部执行器不在该仿真/策略契约中，因此不猜测其行为。

## 惯性和模型位姿验证过吗？

15 个物理惯性矩阵都正定，总质量在源/ROS/Isaac 一致；109 个源到 ROS 位姿矩阵通过容差。这证明转换一致性，不等于独立测量过量产硬件。

## 为什么 MuJoCo 和 Isaac 走得不一样？

两个引擎的接触和执行器模型不同。已记录运行都保持 finite/upright，但项目明确不声明轨迹一致。

## 可以商业使用这些资产吗？

不要默认可以。上游将 3D 文件称为“Creative Commons BY-SA-NC”但未给版本。涉及商业、赞助或变现时请阅读[许可说明](/zh/project/licensing)，并向 Pollen Robotics 澄清。
