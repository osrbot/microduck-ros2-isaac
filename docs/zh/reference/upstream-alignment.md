# 上游对齐 — 2026 年 10 月

源码锁定、官方策略下载器和 ROS 描述已更新，本地 MuJoCo 与结构检查通过。
**新版 Isaac 转换及 ROS/RViz 运行时尚未复测。** 仓库自带的 Isaac USD、原生训练模型和历史结果
继续单独保留；马戏团内容不变。

::: tip 2026-10-20 补充：了解 v8，不切换默认
上游已发布改善起身与转向的 VelStand v8。
新加的[选读教程](../guide/velstand-v8)解释训练改动、参数依据、两阶段续训和评估前提。
本页的版本表与 10 月 10 日检查记录保持原意，`upstream.lock` 和默认策略不变；
上游公布的 v8 成绩没有计入本项目验收。
:::

## 1. 现在选的是哪个版本？ {#versions}

| 输入 | 不可变版本 | 位置 |
| --- | --- | --- |
| MicroDuck RL | [`ceca01706143`](https://github.com/pollen-robotics/microduck_rl/commit/ceca01706143d729305baa94cbd8ab990979e325) | `reference/microduck_rl/` |
| MicroDuck runtime | [`dec725c67ffb`](https://github.com/pollen-robotics/microduck/commit/dec725c67ffbbdde7f1de30f8c936b1bf9c1d70e) | `reference/microduck_runtime/` |
| 官方策略集 v7 | [`6677ec007142`](https://huggingface.co/pollen-robotics/microduck-policies/commit/6677ec007142bbaf05123a468f6ae58d13808786) | `reference/policies/v7/` |
| 游乐场历史坐起策略 | [`590b986bd8c0`](https://github.com/pollen-robotics/microduck/commit/590b986bd8c0d50ae02cb3ea2f59c463b6828168) | `reference/policies/isaac-legacy/` |
| 仓库自带历史 Isaac USD | [`d424a0c899f6`](https://github.com/pollen-robotics/microduck_rl/commit/d424a0c899f6b33cbd3daeb279913134349c0b63) | `assets/isaac/robot_allcollisions/` |

表中为提交号缩写；`upstream.lock` 记录完整版本和每个下载文件的 SHA-256。下载器遇到有改动的源码 checkout 或哈希
不一致的已有策略时会停止；先保留自己的修改，不要为了通过检查而删除它们。
已有的 `reference/microduck/` 历史快照不动。

```bash
./scripts/fetch_upstream.sh
```

下载脚本使用 Python 3.11+，获取 v7 的 10 个 ONNX、清单和模型卡，以及游乐场使用的历史坐起权重，
共 13 个文件均检查哈希。runtime checkout 只是源码参考，
这一步**不会**安装实体机器人 daemon、刷固件或升级 Isaac Lab。

## 2. 先从 ROS 描述开始 {#ros-description}

仓库内的 Xacro 和 38 个 STL 已来自所选的 10 月模型。按 [ROS 2 教程](../ros2/)构建和启动即可，
这条路线不需要额外下载上游。14 关节接口不变。Humble 继续不加 `rviz_fullscreen:=true`，手动最大化 RViz。

维护者需要重新生成描述时：

```bash
python3 scripts/generate_ros_description.py
python3 scripts/validate_ros_mjcf_pose_parity.py
```

转换源现在是 **`robot_groundcontact.xml`**。它承接旧版选择性碰撞的 `robot_allcollisions.xml`。
新版上游中同名的 `robot_allcollisions.xml` 已是全碰撞几何模型，不能按文件名直接互换。
两者仍是 14 动作模型；下载新版 runtime 不会自动给本项目 ROS/ONNX 接口增加可控嘴部关节。

## 3. 不开 Isaac，也能先检查策略 {#policy-probe}

隔离环境使用 Python 3.12、MuJoCo 3.10.0、ONNX Runtime 1.24.4、NumPy 2.4.1。
`setup_mujoco_env.sh` 优先用 `uv`，未安装时改用本地 `python3.12 -m venv` 与 pip，不替换系统 Python。

```bash
./scripts/setup_mujoco_env.sh
MICRODUCK_BASELINE_DIR="$PWD/artifacts/upstream-alignment/20261010" \
  ./scripts/run_official_baseline.sh
work/mujoco_env/bin/python scripts/run_mujoco_baseline.py \
  --policy reference/policies/v7/velstand.onnx \
  --duration 10 --vx 0.3 --action-scale 0.9 \
  --output artifacts/upstream-alignment/20261010/velstand_groundcontact_probe.json
```

最后一条是在简化接地模型中的**平地兼容性探测**，不是复现 v7 的 Rough + Backlash 训练环境。
它不测试跌倒、起身、身体倾斜或实体机器人。上游说明了站立 roll/pitch 控制，同时仍列出身体高度
和低速转向限制，见 [VelStand 说明](https://github.com/pollen-robotics/microduck_rl/blob/ceca01706143d729305baa94cbd8ab990979e325/docs/velstand_policy.md)。

## 4. Isaac 教程里哪些变了？ {#isaac-path}

- 默认行走/站立仍是 `alpha_walking`/`alpha_stand`。v7 文件与历史基线哈希一致，只换了下载位置。
- 游乐场默认保留历史 `alpha_sitstand`，下载器从原始不可变版本单独获取，放在
  `reference/policies/isaac-legacy/`。这样默认使用的七个动作网络均与历史哈希一致。
  更新的 v7 坐起策略仍需重新检查 Isaac 中的动作和切换。
- `velstand` 已下载，但不会悄悄替换游乐场的双策略控制器。控制器保留历史切换和缩放逻辑，
  换文件名不等于完整移植新版 runtime。
- `roulade.onnx` 与历史案例输入逐字节一致。教程路径已更新，原翻滚结果和 USD 不变。

有可用且已确认身份的 Linux/Isaac 主机时，下一步转换检查为：

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/convert_mjcf_to_usd.sh
./scripts/run_isaac_policy.sh \
  --usd assets/isaac/robot_groundcontact/robot_groundcontact.usda \
  --policy reference/policies/v7/alpha_stand.onnx \
  --duration 5 --action-scale 1.0 \
  --output artifacts/isaac/groundcontact/stand.json
```

候选模型通过站立和行走检查后，维护者才单独试用新版坐起。这是**尚未验收的试验命令**，
不是新手的默认启动命令：

```bash
./scripts/run_isaac_playground.sh \
  --usd assets/isaac/robot_groundcontact/robot_groundcontact.usda \
  --sitstand-policy reference/policies/v7/alpha_sitstand.onnx \
  --follow-camera --viz kit
```

转换器生成独立的 `robot_groundcontact/` 候选目录；目录已存在时拒绝覆盖，也不会替换历史 USD。
完成转换和结构检查，还不能自动将候选提升为原生训练模型，也不代表新版坐起及动作衔接已经验证。

## 5. 2026-10-10 的检查记录 {#evidence}

| 检查项 | 本地结果 |
| --- | --- |
| 不可变源码版本与 12 个下载哈希 | 已核对 |
| 历史坐起下载与默认七个动作网络哈希 | 与历史基线一致 |
| 10 个 ONNX 网络 | 声明的输入均为 61 维，输出均为 14 维 |
| 生成的 ROS 描述 | 15 个物理 link + 无质量根节点，14 个可动关节；网格路径完整 |
| MJCF→ROS 变换 | 比较 109 处，最大矩阵误差 `4.90e-12` |
| `alpha_stand`，5 秒 | 有限值，结束时直立 |
| `alpha_walking`，10 秒，vx 0.3 | 有限值，结束时直立；最终 xy 约 `[1.156, -0.214]` m |
| `velstand`，10 秒，vx 0.3 | 有限值，结束时直立；最终 xy 约 `[1.189, -0.101]` m |
| 历史 USD | 结构检查仍通过，文件内容未改动 |
| 新版 USD / PhysX 回放 / ROS GUI | 本轮未运行 |

报告在 `artifacts/upstream-alignment/20261010/`。这些确定性的短探测不是鲁棒性评分，也不是速度
跟踪已达标的证明。[旧测试记录](./results)保留自己的日期和源版本。
网格与 XML/代码的许可划分见[许可说明](../project/licensing)。发布本说明不代表待测运行时已验收，
也不代表完成了新训练。
