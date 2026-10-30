# 常见问题

这里整理了安装、模型、训练和使用许可的常见问题。运行报错请看[故障排查](/zh/troubleshooting)。

## 这个项目现在能做什么？

- 在 RViz 里打开完整 MicroDuck，活动 14 个关节；
- 跑现成的 ROS 2 点头、踏步和鞠躬例程；
- 在 Isaac Sim 里直接打开仓库自带 USD；
- 回放公开行走策略，在键盘游乐场切换多种动作；
- 用 Isaac Lab 训练平地行走，并按[连续翻滚案例](/zh/isaac/continuous-roll)练习调参；
- 在 MuJoCo 中试运行起身与转向模型，或[下载模型继续训练](/zh/guide/training-checkpoints)；
- 从 ROS 2 给本机 Isaac 游乐场发命令，再把姿态显示到 RViz。

## 现在还不能做什么？

- **不能直接控制实体 MicroDuck。** 仓库没有 `ros2_control`、舵机驱动、标定和真机安全配置。
- **Isaac checkpoint 不能直接下发真机。** sim2real 还需要执行器建模、部署和实体测试。
- **Isaac 和 MuJoCo 不会走出完全相同的轨迹。** 两边的接触和执行器模型不同。
- **没有嘴部动作。** 公开仿真模型和策略定义了 14 个关节，不包含嘴部执行器。

## ROS 2 和 Isaac Sim 必须一起装吗？

不用。只想看模型、动关节、跑 ROS 2 例程，就先装 ROS 2。想玩物理、策略、游乐场或训练时，再装
Isaac Sim。ROS 2 连接 Isaac 是后面的可选玩法。

## 仓库已经有 URDF、USD 和 ROS 2 包了吗？

有。`microduck_description` 提供 ROS 机器人描述、网格、惯性、TF/RViz launch、home pose 和关节
滑块；Isaac USD 也已经生成好。第一次使用不需要自己转换模型。

## Isaac Sim 可以直接打开吗？

可以。先打开仓库提供的最外层 USD 看模型；想动起来，再用现成 runner 回放单策略或打开键盘游乐场。
自己训练新 checkpoint 是另一条 Isaac Lab 路线。

## 为什么是 14 个关节，不是 15 个执行器？

公开 MJCF 和策略只有 14 个可动关节。实体运行时提到过嘴部执行器，但公开仿真模型没有它的几何、
极限和策略动作。

## 质量和惯性参数来自哪里？

参数来自上游 MJCF。转换检查会比较质量、惯性和位姿，确认 ROS 与 Isaac 模型保留了源数据。
这些数值尚未由本项目在实体机器人上重新测量。

## 可以商业使用这些资产吗？

模型网格采用 **CC BY-NC-SA 4.0**，包含非商业使用限制；MJCF 描述和本项目原创代码采用 **Apache-2.0**。
具体文件范围见[许可说明](/zh/project/licensing)。商业、赞助或变现用途涉及模型网格时，先向 Pollen Robotics 确认授权。

## 运行失败，先去哪里？

打开[故障排查](/zh/troubleshooting)，按 RViz 缺件、关节不动、Isaac 崩溃或策略加载失败等现象查找。
