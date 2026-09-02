# 把 MicroDuck 放进 Isaac Sim

仓库已经带了转换好的 MicroDuck USD。第一次来不用先折腾转换脚本，也不用先配置策略，直接把
鸭子请进场景就行。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>预计时间</span><strong>8–15 分钟</strong></div>
  <div role="listitem"><span>需要环境</span><strong>Isaac Sim</strong></div>
  <div role="listitem"><span>需要策略</span><strong>不需要</strong></div>
  <div role="listitem"><span>完成结果</span><strong>USD 完整加载并可 Play</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>这一页只验证模型层</strong>
  <ul>
    <li>找到仓库提供的主 USD；</li>
    <li>在 Isaac Sim 中打开完整 stage；</li>
    <li>检查外观、关节层级与 Play 后的稳定性。</li>
  </ul>
</div>

<div class="md-command-steps">
  <strong>先用终端确认文件，再打开 Isaac Sim</strong>
  <p>按 <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd> 打开终端 A，<code>cd</code> 到仓库根目录。这里先检查 USD 和它的 payload 是否齐全，避免进 Isaac 以后才发现路径不对。</p>
</div>

<div class="md-step-kicker"><span>步骤 1</span><strong>终端 A · 仓库根目录</strong></div>

## 1. 找到 USD

从仓库根目录开始，主文件是：

```text
assets/isaac/robot_allcollisions/robot_allcollisions.usda
```

请保留整个 `robot_allcollisions` 目录。主文件还会读取相邻 `payloads/` 目录里的几何和材质。

从终端确认文件与 payload 目录都在：

```bash
test -f assets/isaac/robot_allcollisions/robot_allcollisions.usda \
  && test -d assets/isaac/robot_allcollisions/payloads \
  && echo "MicroDuck USD: OK"
```

按 <kbd>Enter</kbd> 后应立即看到 `MicroDuck USD: OK` 并回到提示符。没有输出就表示至少有一个路径不存在，
先确认自己是否真的在仓库根目录。

<div class="md-result-label">仓库 USD 渲染预览 · 用来核对外观</div>

<figure class="md-doc-figure md-usd-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-usd-preview.webp" alt="仓库自带 MicroDuck USD 的三分之四视角渲染预览" width="1200" height="800" loading="lazy"></div>
  <figcaption><strong>这张不是概念图。</strong>它由仓库当前的 USD 直接渲染，方便你打开 Isaac Sim 前先认一下模型。进入 Isaac Sim 后可以自由转镜头。</figcaption>
</figure>

<div class="md-step-kicker"><span>步骤 2</span><strong>Isaac Sim 窗口</strong></div>

## 把鸭子请进场景

1. 启动 Isaac Sim。
2. 点击 **File → Open**。
3. 选择 `robot_allcollisions.usda`。
4. 等待 stage 和材质加载完成。
5. 如果想检查 articulation 是否稳定，可以点击 **Play**。

如果你安装的是 standalone 版，就从应用菜单或安装目录的启动器打开；不同 Isaac 版本的启动命令不同，
这里不让第一次玩的同学盲猜路径。打开文件选择器后，可以按 <kbd>Ctrl</kbd>+<kbd>L</kbd> 输入完整路径，
也可以从仓库目录逐级点进去。

## 鸭子顺利落地时应该看到什么

- MicroDuck 作为一台完整机器人出现，而不是散开的网格；
- Stage 树中能看到机器人身体和关节；
- 头部、身体、腿和脚都能看到；
- 点击 **Play** 后机器人不会立刻消失或散架。

等待右下角加载提示结束再判断。材质还在加载时，短暂出现灰色模型不等于文件坏了；Stage 树里出现红色
资源错误、头身散开或按 Play 后立即消失，才需要回到下面的排查步骤。

<div class="md-result-label">真实界面参考 · 先认 Stage 和视口</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="Isaac Lab 实际运行窗口中的 MicroDuck、Stage 树和视口" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>先认两个地方：中间是视口，右侧是 Stage 树。</strong>这张来自本仓库多动作游乐场的真实运行，不是本步骤的无策略打开画面；但窗口区域和检查方法相同。你打开主 USD 后，也要在这两个位置确认鸭子完整到场、层级没有报红。</figcaption>
</figure>

<div class="md-checkpoint">
  <strong>模型层验证通过</strong>
  <p>Stage 树、外观和 articulation 都正常，点击 <strong>Play</strong> 后机器人仍在场。到这里还没有运行策略，也没有开始训练。</p>
</div>

只查看模型或截图，做到这里就够了。下一页先跑一张行走策略，再去多动作游乐场玩完整套动作。

## 鸭子没有出现在 Stage 里？

- 确认打开的是最外层 `.usda`，不是 `payloads/` 里的文件；
- 不要改变仓库里的目录结构；
- 查看 Isaac Sim Console 是否提示相对路径资源缺失；
- 视口里什么都没有时，选中机器人并按 <kbd>F</kbd> 聚焦。

<div class="md-page-complete">
  <strong>USD 已经站稳。</strong>
  <p>下一页先跑一张行走策略。这是检查 Isaac、ONNX Runtime 和模型能不能一起工作的最快方法。</p>
</div>
