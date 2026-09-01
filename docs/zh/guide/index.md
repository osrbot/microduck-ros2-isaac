# 从这里开始：今天怎么遛鸭？

这份教程有两条路线：先在 RViz 里打个招呼，或者直接把鸭子放进 Isaac Sim。挑一条顺眼的走，
不用为了看个模型先把整本说明书背下来。

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
- 录制一段仿真视频或做直播演示。

需要 Linux、支持的 NVIDIA 显卡、Isaac Sim 和 Isaac Lab。

**完成后的样子：**MicroDuck 会落到 Isaac Sim 的地面上，并在跟随镜头下迈开小短腿。

[开始 Isaac Sim 教程 →](/zh/isaac/)

## 先别管那些维护工具

仓库里还有模型转换脚本、检查工具和 JSON 测试记录。它们是给修改模型和维护项目时使用的，
不是入门门票。第一次来，直接从已经准备好的 ROS 包或 USD 开始，先把鸭子玩起来。

下一步：[安装当前路线需要的软件](./installation)。
