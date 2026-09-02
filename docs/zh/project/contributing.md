# 参与贡献

这一页只给要改仓库代码的人。只是想玩 ROS 2 或 Isaac Sim，不需要运行下面任何生成器，跟着教程走就行。

## 改代码前

1. 先看[架构](/zh/concepts/architecture)和[许可](./licensing)。
2. 保持上游提交固定；只有专门做兼容更新时才改 `upstream.lock`。
3. 不要提交下载的策略、本地环境、日志、凭据或机器绝对路径。
4. 模型派生资产要保留原始署名。

## 改到哪里，就测到哪里

- 文档：`npm ci && npm run docs:build`。
- ROS 生成：重新生成 description，再构建并打开 RViz。
- Isaac 资产：重新生成 USD，检查 Stage，再跑一张策略。
- 策略适配：跑站立与行走检查。
- 真机相关：单独说明硬件、操作过程和安全边界，不和仿真混在一起。

一次改到多个部分时，运行完整无界面检查：

```bash
./scripts/validate_all.sh
```

## 重新生成 ROS 2 description

只有修改上游模型或 ROS 生成器以后才运行：

```bash
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
./scripts/generate_ros_description.py
./scripts/validate_ros2_package.sh
```

然后重新构建 `microduck_description`，再打开 RViz 看一遍。

## 重新生成 Isaac USD

只有修改源模型或转换代码以后才运行：

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/convert_mjcf_to_usd.sh
```

转换器会更新 `assets/isaac/`，并应用本项目的碰撞调整。提交前要打开最外层 USD，再跑一张策略。

## 提交时写清楚

Pull request 里说明改了什么、跑了哪些命令、还有什么没测。测试机器和历史数据放在
[维护者资料](/zh/reference/environment)里，不塞进普通新手教程。
