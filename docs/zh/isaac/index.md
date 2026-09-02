# 把 MicroDuck 放进 Isaac Sim

仓库已经带了转换好的 MicroDuck USD。第一次来不用先折腾转换脚本，也不用先配置策略，直接把
鸭子请进场景就行。

## 1. 找到 USD

从仓库根目录开始，主文件是：

```text
assets/isaac/robot_allcollisions/robot_allcollisions.usda
```

请保留整个 `robot_allcollisions` 目录。主文件还会读取相邻 `payloads/` 目录里的几何和材质。

<figure class="md-doc-figure md-usd-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-usd-preview.webp" alt="仓库自带 MicroDuck USD 的三分之四视角渲染预览" width="1200" height="800" loading="lazy"></div>
  <figcaption><strong>这张不是概念图。</strong>它由仓库当前的 USD 直接渲染，方便你打开 Isaac Sim 前先认一下模型。进入 Isaac Sim 后可以自由转镜头。</figcaption>
</figure>

## 2. 把鸭子请进场景

1. 启动 Isaac Sim。
2. 点击 **File → Open**。
3. 选择 `robot_allcollisions.usda`。
4. 等待 stage 和材质加载完成。
5. 如果想检查 articulation 是否稳定，可以点击 **Play**。

## 鸭子顺利落地时应该看到什么

- MicroDuck 作为一台完整机器人出现，而不是散开的网格；
- Stage 树中能看到机器人身体和关节；
- 头部、身体、腿和脚都能看到；
- 点击 **Play** 后机器人不会立刻消失或散架。

只查看模型或截图，做到这里就够了。下一步可以先[运行一张行走策略](./policy-playback)，再去
[多动作游乐场](./playground)一次玩完整套动作，或者从[原生 Isaac Lab 训练](./training)开始自己教。

## 鸭子没有出现在 Stage 里？

- 确认打开的是最外层 `.usda`，不是 `payloads/` 里的文件；
- 不要改变仓库里的目录结构；
- 查看 Isaac Sim Console 是否提示相对路径资源缺失；
- 视口里什么都没有时，选中机器人并按 <kbd>F</kbd> 聚焦。

::: details 给维护者：从上游 MJCF 重新生成 USD
教程已经带了可用 USD。只有修改源模型或转换代码时才需要重新生成：

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/convert_mjcf_to_usd.sh
```

脚本会转换模型、应用项目的碰撞调整，并更新 `assets/isaac/` 下的资产。
:::
