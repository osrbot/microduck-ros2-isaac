# 让 MicroDuck 在 Isaac Sim 里走起来

这部分假设电脑里已经安装 Isaac Sim 和 Isaac Lab。USD 已经在仓库里；下面只需要下载公开策略，
并在项目目录准备 ONNX Runtime。环境准备好以后，就可以正式放鸭开跑。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>预计时间</span><strong>15–25 分钟</strong></div>
  <div role="listitem"><span>执行位置</span><strong>仓库根目录</strong></div>
  <div role="listitem"><span>需要窗口</span><strong>终端 + Isaac Sim</strong></div>
  <div role="listitem"><span>完成结果</span><strong>公开策略持续运行并有报告</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>这页会完成</strong>
  <ul>
    <li>准备公开策略和项目本地 ONNX Runtime；</li>
    <li>运行 60 秒行走策略，并识别正常进度输出；</li>
    <li>再跑一次 10 秒 headless 自检，留下 JSON 结果。</li>
  </ul>
</div>

<div class="md-command-steps">
  <strong>这页只需要终端 A</strong>
  <p>按 <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd> 打开终端，<code>cd</code> 到仓库根目录。GUI 回放、站立策略和 headless 自检要依次运行；前一个结束或按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 停止后，才能启动下一个。</p>
</div>

<div class="md-step-kicker"><span>步骤 1</span><strong>终端 A · 仓库根目录</strong></div>

## 1. 准备策略运行环境

在仓库根目录运行：

```bash
./scripts/fetch_upstream.sh
export ISAACLAB_DIR=/path/to/IsaacLab
./scripts/setup_isaac_python_env.sh
```

如果 Isaac Lab 正好在默认的 `~/rlgpu_ws/IsaacLab`，可以省略 `ISAACLAB_DIR`。

<div class="md-checkpoint">
  <strong>依赖准备完成</strong>
  <p><code>reference/microduck/</code> 中已有公开策略，<code>work/isaac_python_pkgs/onnxruntime</code> 目录存在。后面再玩不用重复下载。</p>
</div>

<div class="md-step-kicker"><span>步骤 2</span><strong>终端保持运行 · GUI 回放</strong></div>

## 2. 放鸭开跑

在带图形桌面的 Linux 中运行：

```bash
./scripts/run_isaac_policy.sh \
  --duration 60 \
  --vx 0.3 \
  --action-scale 0.9 \
  --follow-camera \
  --viz kit
```

按 <kbd>Enter</kbd> 后终端会持续打印日志，提示符不会马上回来。第一次加载 Kit 扩展可能需要几分钟，
不要因为窗口还没出现就重复执行同一条命令。

Isaac Sim 会打开，把 MicroDuck 放到地面上，然后运行行走策略，镜头会跟随机器人。仿真速度可能
比真实时间慢，终端每五个仿真秒会输出一次进度。

进度行类似 `Rollout progress: sim=5.0/60.0s`。它表示仿真控制循环确实向前走，不要求 wall time 与
sim time 完全一致。窗口打开后先看四件事：机器人落在地面、关节持续运动、镜头跟随、终端无 traceback。

<div class="md-result-label">真实运行截图 · 行走策略开始后</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-action-walk.webp" alt="MicroDuck 在 Isaac Sim 中实际回放公开行走策略" width="1200" height="750" loading="lazy"></div>
  <figcaption><strong>策略开始接管。</strong>这张实测图来自行走回放过程。鸭子会迈步不等于一定笔直向前；先看仿真是否持续、关节是否正常运动、终端有没有报错。</figcaption>
</figure>

<div class="md-checkpoint">
  <strong>行走回放通过</strong>
  <p>进度能走到 60 秒，关节持续更新，进程正常退出并写入报告。鸭子迈步但轨迹不够直，不等于加载失败；先把“能运行”和“行为质量”分开判断。</p>
</div>

## 可选：让它先乖乖站好

先等 60 秒行走回放正常结束；想提前结束，就在终端 A 按 <kbd>Ctrl</kbd>+<kbd>C</kbd>，等提示符回来再运行：

```bash
./scripts/run_isaac_policy.sh \
  --policy reference/microduck/policies/alpha_stand.onnx \
  --duration 30 \
  --action-scale 1.0 \
  --follow-camera \
  --viz kit
```

<div class="md-step-kicker"><span>步骤 3</span><strong>终端 · Headless 自检</strong></div>

## 不看画面，跑一小圈

先确认 GUI 回放已经退出，下面的命令适合快速检查环境：

```bash
./scripts/run_isaac_policy.sh \
  --duration 10 \
  --vx 0.3 \
  --action-scale 0.9 \
  --headless
```

运行结束后会把简单结果写到 `artifacts/isaac/policy_rollout.json`。普通教程不需要阅读这个文件，
只有排查问题时才用得上。

检查文件已经生成：

```bash
test -s artifacts/isaac/policy_rollout.json \
  && echo "Policy rollout report: OK"
```

最后一行打印 `Policy rollout report: OK`，才说明本次报告确实写出来了；没有输出时先检查上一条 headless
命令是否完整结束，而不是反复执行 `test`。

## 鸭子走着走着，Isaac Sim 崩了？

- 通过 `run_isaac_policy.sh` 启动，不要直接运行 Python 文件。包装脚本会在需要时只选择一个
  NVIDIA Vulkan 设备。
- 开始新任务前先关闭其他 Isaac Sim 窗口。
- 先用空场景确认 NVIDIA 驱动、Vulkan 和 Isaac Sim 本身可以稳定运行。
- 尝试无界面命令。如果 headless 正常而 GUI 崩溃，问题更可能在渲染或桌面会话。
- GPU 环境变量和进一步检查见[故障排查](/zh/troubleshooting)。

::: details 高级设置
包装脚本默认使用 `cuda:0`。多 GPU 主机确实需要时可以覆盖：

```bash
export MICRODUCK_ISAAC_DEVICE=cuda:0
export MICRODUCK_VULKAN_ICD=/etc/vulkan/icd.d/nvidia_icd.json
export MICRODUCK_ISAAC_ACTIVE_GPU=0
```

公开策略读取 61 个数值，控制仿真模型里的 14 个关节。物理频率为 200 Hz，策略推理频率为
50 Hz。这些信息在修改运行器时有用，第一次回放时不用先理解。
:::

<div class="md-page-complete">
  <strong>鸭子已经会走了。</strong>
  <p>窗口运行和无界面运行都试过了。下一页把公开的几种动作都交给键盘。</p>
</div>
