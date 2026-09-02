# 项目架构

本项目是围绕 Pollen Robotics 固定版本输入构建的独立兼容与教学层。生成的 ROS/Isaac 文件是派生输出，不是新的权威机器人规格。

```text
固定版本 microduck_rl MJCF
        |-- MuJoCo 清单与参考 rollout
        |-- Xacro + 网格 --> ROS 2 / TF / RViz
        `-- Isaac MJCF 导入 --> 碰撞修正 --> 已验证 USD

固定版本 microduck 策略
        |-- MuJoCo 61 -> 14 回放
        `-- Isaac 多策略游乐场 <--> 本机 UDP <--> ROS 2 / RViz

已验证 MicroDuck USD
        `-- 原生 Isaac Lab 环境 --> RSL-RL PPO --> 新 checkpoint
```

## 可复现源输入层

`upstream.lock` 记录不可变提交。`fetch_upstream.sh` 把它们放入被忽略的 `reference/`，避免上游分支移动后悄悄改变演示输入。

## ROS 描述层

生成器保留 15 个 MJCF 物理 body、惯性、14 个 hinge 和引用几何。`trunk_base` 上增加一个无质量 `base_link`，用于解决 KDL 根节点惯性限制，并不移动或删除真实 trunk 惯性。四元数通过旋转矩阵转换，也覆盖精确 ±90° pitch 奇异点。

## Isaac 层

Isaac Lab MJCF 导入器生成 stage。项目只修改恢复一处源碰撞过滤意图所需的状态，然后按固定结构契约检查完整 stage。

## 策略适配层

两套运行器使用相同的 61 维观测顺序、14 维动作顺序、home pose、命令布局、200 Hz 物理频率和 50 Hz 策略频率；接触和执行器物理仍由各引擎决定。

## 训练与 ROS 互动层

原生 Isaac Lab task 复用相同 USD 和 61→14 契约，增加多环境、奖励、重置、随机化、curriculum 和
RSL-RL PPO。ROS bridge 不进入 Isaac 的 Python 环境，而是用 localhost UDP 传命令和遥测，再发布
`JointState`、策略状态与 TF。

## 有意保持的边界

ROS description、ROS bridge、公开策略回放和新策略训练仍然是独立层。bridge 只连接仿真，训练
checkpoint 也不会自动变成真机策略；每一层都要单独测试和陈述。
