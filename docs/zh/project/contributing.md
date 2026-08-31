# 参与贡献

贡献应让某一证据层更可靠，而不是混淆源输入、转换、仿真、GUI 和硬件之间的边界。

## 修改前

1. 阅读[架构](/zh/concepts/architecture)、[验证体系](/zh/reference/validation)和[许可](./licensing)。
2. 固定上游提交；只有专门的兼容更新才能修改 `upstream.lock`。
3. 不提交下载的策略、本地环境、日志、凭据或机器绝对路径。
4. 对模型派生资产保留署名。

## 按影响范围验证

- 文档：`npm ci && npm run docs:build`。
- ROS 生成：generator、pose parity、package build 与 runtime test。
- Isaac 资产：conversion、post-process 与 USD inventory。
- 策略适配：站立/行走 JSON 与跨引擎 smoke comparison。
- GUI 声明：记录主机版本并提供有界、可重复交互测试。
- 硬件声明：与仿真证据分开，记录实体配置和安全边界。

跨层修改运行：

```bash
./scripts/validate_all.sh
```

变更说明应写清改了什么、运行了什么、证据在哪里、什么仍未测试。“能打开”不能代替结构检查，“走过一次”不能代表训练、轨迹或硬件一致。
