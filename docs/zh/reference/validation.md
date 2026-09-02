# 这个项目怎么测试

项目明确区分证据层级。后一个层级不能反向证明前一个契约，GUI 截图也不能替代结构和运行时检查。

| 层级 | 检查内容 | 已记录状态 |
| --- | --- | --- |
| 源身份 | 固定上游提交 | 通过 |
| MJCF 结构 | 刚体、关节、传感器、执行器、策略形状 | 通过 |
| MuJoCo 运行 | 已发布站立与行走策略 | 通过 |
| USD 结构 | 单位、刚体、关节、质量、碰撞 | 通过 |
| Isaac 运行 | 61→14 适配和 ONNX 执行 | 通过 |
| 多动作游乐场 | 策略加载、切换和有限值回放 | 通过 |
| 原生训练 smoke | task 注册、多环境、PPO 更新、checkpoint | 通过 |
| 行为 smoke parity | 相同命令/时序下 finite、upright | 通过 |
| ROS 包与运行 | 生成、位姿、构建、启动、JointState、TF | 通过 |
| ROS-to-Isaac bridge | 限幅与真实 ROS → Isaac → ROS 策略/状态闭环 | 通过 |
| GUI 交互与稳定性 | RViz 输入和有界 Isaac Kit 运行 | 单台主机通过 |
| 最终公开演示 | 人工画面验收与采集彩排 | 尚未验收 |
| 实体硬件 | 真机与嘴部第 15 执行器 | 未测试 |

## 运行完整无界面验证

```bash
./scripts/validate_all.sh
```

十三个阶段依次验证环境和源、纯 Python 契约、MuJoCo 基准、USD 转换、Isaac 单策略与多动作回放、
原生训练 smoke、跨引擎对比、ROS 包、description 运行时、bridge 协议和真实 ROS-to-Isaac 闭环。

## 固定数值契约

- 物理步长 0.005 s，decimation 4，控制频率 50 Hz。
- 策略输入 `obs[1,61]`，输出 `actions[1,14]`。
- 行走 scale 0.9，站立 scale 1.0。
- MJCF 到 ROS 共比较 109 个变换，旋转容差 `1e-9`。
- 嘴部执行器不在选定 MJCF/ONNX 契约内。

实际数值和证据见[验证结果](./results)。
