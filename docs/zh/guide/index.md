# 从这里开始：今天怎么遛鸭？

这份教程先分两条入口：在 RViz 里打个招呼，或者直接把鸭子放进 Isaac Sim。Isaac 路线里面再分成
现成动作游乐场和从头训练。挑一条顺眼的走，不用为了看个模型先把整本说明书背下来。

## 路线一：先在 RViz 打个招呼

适合下面这些目标：

- 在 RViz 里看到完整的 MicroDuck；
- 旋转、缩放和平移镜头；
- 用滑块移动机器人的关节；
- 把 description 包用到其他 ROS 2 项目中。

需要 Ubuntu 24.04 和 ROS 2 Jazzy，不需要 Isaac Sim。

**完成后的样子：**MicroDuck 会稳稳站在 RViz 中央。打开 GUI 后，另一个窗口可以控制
14 个关节。

[开始 ROS 2 教程 →](/zh/ros2/)

## 路线二：放进 Isaac Sim 遛两圈

适合下面这些目标：

- 打开仓库自带的 MicroDuck USD；
- 在 Isaac Sim 里查看机器人；
- 运行已经发布的站立或行走策略；
- 切换坐起、低头碰地、踢球和前滚；
- 用原生 Isaac Lab 环境跑一次 PPO 训练；
- 录制一段仿真视频或做直播演示。

需要 Linux、支持的 NVIDIA 显卡、Isaac Sim 和 Isaac Lab。

**完成后的样子：**MicroDuck 会落到 Isaac Sim 的地面上，能用键盘切动作；训练路线还会产出自己的
checkpoint。

[开始 Isaac Sim 教程 →](/zh/isaac/)

## 路线三：ROS 2 和 Isaac 一起开

模型已经分别跑通，想看 ROS 命令怎样真的传进 Isaac，再把姿态同步回 RViz，就走这条三终端路线。
页面里已经配好每一步命令、预期画面、动作示例和一键闭环测试。

[用 ROS 2 遥控 Isaac 里的鸭子 →](/zh/ros2/isaac-control)

## 先别管那些维护工具

仓库里还有模型转换脚本、检查工具和 JSON 测试记录。它们是给修改模型和维护项目时使用的，
不是入门门票。第一次来，直接从已经准备好的 ROS 包或 USD 开始，先把鸭子玩起来。

下一步：[安装当前路线需要的软件](./installation)。
