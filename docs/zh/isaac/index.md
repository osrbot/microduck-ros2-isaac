# 生成并检查 Isaac USD

Isaac 工作流使用 Isaac Lab 官方转换器读取固定版本 MJCF，应用一个有记录的碰撞修正，再验证 stage 后进入策略回放。

## 转换模型

```bash
export ISAACLAB_DIR=/path/to/IsaacLab  # 使用默认目录时可省略
./scripts/setup_isaac_python_env.sh
./scripts/convert_mjcf_to_usd.sh
```

规范输出位置是：

```text
assets/isaac/robot_allcollisions/robot_allcollisions.usda
```

转换在项目临时 work 目录进行。成功后才替换规范资产；失败时恢复上一份资产并清理临时转换文件。

## 为什么需要后处理

MJCF 导入器不会保留源 `contype`/`conaffinity` 过滤语义。如果不修正，`self_collision_only` power-support 传感器网格会错误地参与地面碰撞。`postprocess_isaac_usd.py` 只禁用这一份源几何的一般碰撞，并记录变更。

## 检查结构契约

转换脚本会自动运行 `inspect_usd.py`，报告保存在 `artifacts/isaac/usd_inventory.json`，检查：

- stage 单位和坐标轴；
- 15 个刚体与 14 个旋转关节；
- articulation root、关节名称与极限；
- 约 0.737243 kg 总物理质量；
- 81 个网格实例，其中 10 个碰撞网格启用；
- 有记录的碰撞修正。

也可直接重复检查：

```bash
"$ISAACLAB_DIR/isaaclab.sh" -p scripts/inspect_usd.py
```

## 打开 stage

在 Isaac Sim 中打开规范 `.usda`，检查材质和镜头。能打开只证明 GUI 能加载文件；对外声明刚体、关节、质量或碰撞正确之前，仍需结构报告。

下一步：[回放 ONNX 策略](./policy-playback)。
