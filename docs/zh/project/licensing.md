# 许可与发布边界

这是一个混合许可仓库，不能把整个仓库描述成 Apache-only。

## 原创兼容代码

本项目原创的脚本、ROS packaging、launch、validator 和文档采用 Apache-2.0，根目录 `LICENSE` 适用于这些贡献。

## 上游模型派生资产

2026 年 10 月锁定版本的上游 [LICENSE-MODELS.md](https://github.com/pollen-robotics/microduck_rl/blob/ceca01706143d729305baa94cbd8ab990979e325/LICENSE-MODELS.md)
已明确区分：STL 网格采用 **CC BY-NC-SA 4.0**；MJCF XML、导出配置与 `.part` 元数据采用 **Apache-2.0**。
这取代了旧版“未注明版本”的说明，不是本项目自行选择许可版本。

生成的 Xacro 描述采用 Apache-2.0，但它引用的 STL 网格仍采用 CC BY-NC-SA 4.0。
USD 含有转换后的网格几何，需继续保留网格许可。仓库内的历史 USD 也保留原始来源身份，本次更新不声称已重新生成它。

公开发布时：

- 保留 Pollen Robotics 署名与 `NOTICE-MICRODUCK.md`；
- 保留 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 声明，并注明对网格派生物的修改；
- 不声称仓库中每个文件都是 OSI 认可的开源许可；
- 涉及商业、赞助或变现时，先向 Pollen Robotics 获取书面澄清。

已发布 ONNX 策略只会下载到被忽略的 `reference/policies/v7/`，不打包进仓库。
锁定 Hub 版本的模型卡声明 Apache-2.0；下载器保留模型卡，并像检查权重一样检查它的 SHA-256。
单独保留的历史坐起权重来自 `upstream.lock` 所记录、采用 Apache-2.0 的
[runtime 版本](https://github.com/pollen-robotics/microduck/blob/590b986bd8c0d50ae02cb3ea2f59c463b6828168/LICENSE)，
同样只下载到被忽略的 `reference/`，不打包进仓库。

本页是保守的工程发布边界，不构成法律意见。
