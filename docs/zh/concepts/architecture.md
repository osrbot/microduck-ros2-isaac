# 项目架构

本项目把 Pollen Robotics 的 MicroDuck 模型转换成 ROS 2 和 Isaac 可用的文件，
并提供策略回放、训练和 ROS 通信工具。各部分的关系如下：

```text
固定版本 microduck_rl MJCF
        |-- MuJoCo 清单与参考 rollout
        |-- Xacro + 网格 --> ROS 2 / TF / RViz
        `-- Isaac MJCF 导入 --> 碰撞修正 --> 已验证 USD

固定版本 Hugging Face microduck-policies 策略
        |-- MuJoCo 61 -> 14 回放
        `-- Isaac 多策略游乐场 <--> 本机 UDP <--> ROS 2 / RViz

已验证 MicroDuck USD
        `-- 原生 Isaac Lab 环境 --> RSL-RL PPO --> 新 checkpoint
```

## 模型和策略从哪里来

`upstream.lock` 记录使用的提交。`scripts/fetch_upstream.sh` 按这些提交下载到 `reference/`，
因此重复运行教程会得到同一份输入。
runtime 源码与策略权重是不同输入：当前 runtime 在 `reference/microduck_runtime/`，默认权重在
`reference/policies/v7/`，逐文件检查 SHA-256。新转换使用接地模型 `robot_groundcontact.xml`。
仓库自带 USD 和原生训练继续使用已测过的模型；替换它们前需要重新验证运行结果。具体提交见[模型与源码版本](../reference/upstream-alignment)。

## ROS 2：显示模型和关节

生成器保留 15 个 MJCF 物理 body、惯性、14 个 hinge 和引用几何。`trunk_base` 上增加一个无质量 `base_link`，用于解决 KDL 根节点惯性限制，并不移动或删除真实 trunk 惯性。四元数通过旋转矩阵转换，也覆盖精确 ±90° pitch 奇异点。

## Isaac：运行物理仿真

Isaac Lab 的 MJCF 导入器生成 USD。转换脚本修正一处导入后多出的传感器网格碰撞，
再检查单位、关节、质量和碰撞设置。

## 策略回放：把观测送进模型

两套运行器使用相同的 61 维观测顺序、14 维动作顺序、home pose、命令布局、200 Hz 物理频率和 50 Hz 策略频率；接触和执行器物理仍由各引擎决定。

## 训练和 ROS 通信

原生 Isaac Lab task 复用相同 USD 和 61 维输入、14 维输出接口，增加多环境、奖励、重置、随机化、curriculum 和
RSL-RL PPO。ROS bridge 不进入 Isaac 的 Python 环境，而是用 localhost UDP 传命令和遥测，再发布
`JointState`、策略状态与 TF。

## 各部分分别检查

模型转换后检查关节和惯性，策略回放后检查动作，训练后检查保存的模型，ROS 通信则检查命令和状态是否往返。
这些工具目前连接仿真；实体机器人还需要舵机驱动、标定和硬件测试。
