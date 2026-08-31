# 许可与发布边界

这是一个混合许可仓库，不能把整个仓库描述成 Apache-only。

## 原创兼容代码

本项目原创的脚本、ROS packaging、launch、validator 和文档采用 Apache-2.0，根目录 `LICENSE` 适用于这些贡献。

## 上游模型派生资产

STL、生成的 Xacro 和生成的 USD 来自 Pollen Robotics MicroDuck 3D 模型。上游 `microduck_rl` README 将这些文件称为“Creative Commons BY-SA-NC”，但没有注明版本。本项目保留原文，不替作者猜测具体版本。

公开发布时：

- 保留 Pollen Robotics 署名与 `NOTICE-MICRODUCK.md`；
- 在版本未明确前，按非商业和相同方式共享处理模型派生物；
- 不声称仓库中每个文件都是 OSI 认可的开源许可；
- 涉及商业、赞助或变现时，先向 Pollen Robotics 获取书面澄清。

已发布 ONNX 策略只会下载到被忽略的 `reference/`，不打包进仓库，使用者仍需遵守上游条款。

本页是保守的工程发布边界，不构成法律意见。
