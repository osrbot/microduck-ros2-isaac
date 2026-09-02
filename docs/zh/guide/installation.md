# 先看环境，再装软件

这一页只做准备工作：把仓库放好，并确认你选中的那条路线能找到对应工具。ROS 2 和 Isaac 是两套独立
环境，只玩其中一条，就做对应一半。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>预计时间</span><strong>ROS 2：10–20 分钟</strong></div>
  <div role="listitem"><span>Isaac 准备</span><strong>已有安装后约 10 分钟</strong></div>
  <div role="listitem"><span>执行位置</span><strong>Linux 终端</strong></div>
  <div role="listitem"><span>完成标志</span><strong>检查命令全部通过</strong></div>
</div>

## 两条路线要准备什么

<div class="md-requirement-grid">
  <div class="md-requirement-card md-route-orange"><span>ROS 2 路线</span><strong>Ubuntu 24.04 + ROS 2 Jazzy</strong><p>不需要 NVIDIA 显卡，也不需要 Isaac Sim。第一次建议先走这条。</p></div>
  <div class="md-requirement-card md-route-aqua"><span>Isaac 路线</span><strong>Ubuntu 24.04 + NVIDIA GPU</strong><p>完整测试组合是 Isaac Sim 6.0.1 standalone 和 Isaac Lab 3.0.0 beta 2。</p></div>
</div>

今天想玩哪条，就准备哪一套。不确定时先装 ROS 2，后面再补 Isaac。

<div class="md-tutorial-goals">
  <strong>走完这一页，你会完成</strong>
  <ul>
    <li>克隆仓库并确认当前目录正确；</li>
    <li>为 ROS 2 路线准备 Jazzy 和 colcon，或为 Isaac 路线确认 Isaac Lab；</li>
    <li>下载公开策略并建立项目本地 Python 依赖；</li>
    <li>在启动图形程序前，先用几条小检查排除环境问题。</li>
  </ul>
</div>

## 第一次开终端？先学这 1 分钟

下面所有命令都在 **Ubuntu 桌面**的终端里运行。终端就是那个可以输入命令的黑色或深色窗口，不是
Isaac Sim 里的 Console，也不是浏览器地址栏。

<div class="md-terminal-school">
  <strong>Ubuntu 常用终端快捷键</strong>
  <p>先记住“打开、再开一个、粘贴、停止”四件事，后面就够用了。</p>
  <div class="md-shortcut-grid" role="list" aria-label="Ubuntu 终端快捷键">
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>T</kbd></strong><p>打开第一个终端窗口。</p></div>
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>N</kbd></strong><p>再开一个终端窗口，适合教程里的终端 B、C。</p></div>
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>T</kbd></strong><p>在同一窗口新建标签页；屏幕小时可以这样用。</p></div>
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd></strong><p>把复制好的命令粘贴进终端。</p></div>
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>C</kbd></strong><p>停止正在运行的程序。注意：在终端里它不是复制。</p></div>
    <div role="listitem"><strong><kbd>Ctrl</kbd> + <kbd>L</kbd></strong><p>清空当前画面；不会删除文件，也不会停止程序。</p></div>
  </div>
</div>

::: tip 快捷键没反应也别慌
远程桌面有时会把快捷键截走。点 Ubuntu 左上角 **Activities / 活动**，搜索 **Terminal / 终端**；
想再开一个时，也可以在终端菜单里选 **File → New Window**。教程里的“终端 A、B、C”只是窗口标签，
一台电脑就够了。
:::

<div class="md-command-steps">
  <strong>每个命令块都按这个节奏来</strong>
  <p>点代码块右上角的复制按钮 → 回到终端按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>V</kbd> → 按 <kbd>Enter</kbd>。短命令要等 <code>用户名@电脑名:目录$</code> 这样的提示符重新出现；启动 RViz 或 Isaac 的长命令不会立刻返回提示符，要保持这个终端开着。</p>
</div>

<div class="md-step-kicker"><span>步骤 1</span><strong>终端 A · 按 Ctrl + Alt + T 打开</strong></div>

## 克隆仓库

```bash
git clone https://github.com/osrbot/microduck-ros2-isaac.git
cd microduck-ros2-isaac
```

第一条下载仓库，第二条进入仓库目录。两行一起粘贴也可以；等提示符重新出现后再做下一项检查。

确认没有走错门：

```bash
test -f README.md && test -d ros2_ws && test -d assets/isaac \
  && echo "MicroDuck repository: OK"
```

<div class="md-checkpoint">
  <strong>看到这些就继续</strong>
  <p>终端打印 <code>MicroDuck repository: OK</code>。ROS 2 包和 Isaac USD 已经随仓库提供，第一次运行不用重新生成模型。</p>
</div>

<div class="md-step-kicker"><span>步骤 2A</span><strong>只走 ROS 2 路线时执行</strong></div>

## 准备 ROS 2 Jazzy

下面命令适用于 Ubuntu 24.04，并假设你已经按 ROS 官方方式配置好 apt 软件源：

```bash
sudo apt update
sudo apt install \
  ros-jazzy-desktop \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-xacro \
  python3-colcon-common-extensions
```

`sudo` 询问密码时，键盘输入不会显示圆点或星号，这是正常的；输入完直接按 <kbd>Enter</kbd>。安装过程
回到提示符且没有 `E:` 开头的错误，才继续下面的检查。

加载 ROS 环境并检查关键命令：

```bash
source /opt/ros/jazzy/setup.bash
echo "ROS_DISTRO=$ROS_DISTRO"
command -v ros2
command -v colcon
```

`source` 成功时通常一声不吭；后面三行有输出才是检查结果。

<div class="md-checkpoint">
  <strong>ROS 2 准备完成</strong>
  <p>第一行显示 <code>ROS_DISTRO=jazzy</code>，后两行分别打印 <code>ros2</code> 和 <code>colcon</code> 的路径。若有一行没有输出，先不要进入 RViz 页面。</p>
</div>

::: tip 每个新终端都要 source
`source /opt/ros/jazzy/setup.bash` 只对当前终端生效。后面的教程会把需要的 source 命令完整写出，
第一次玩鸭不用背。
:::

<div class="md-step-kicker"><span>步骤 2B</span><strong>只走 Isaac 路线时执行</strong></div>

## 确认 Isaac Sim 与 Isaac Lab

本项目完整测试过的组合是 Ubuntu 24.04、Isaac Sim 6.0.1 standalone、Isaac Lab 3.0.0 beta 2，
以及能正常使用驱动和 Vulkan 的 NVIDIA 显卡。其他版本可能可以运行，但先从最小检查开始。

如果 Isaac Lab 不在默认的 `~/rlgpu_ws/IsaacLab`，先告诉当前终端它在哪里：

```bash
export ISAACLAB_DIR=/path/to/IsaacLab
```

这里的 `/path/to/IsaacLab` 是占位符，必须换成你电脑里的真实目录，例如
`/home/duck/rlgpu_ws/IsaacLab`；不要把 `path` 四个字母原样照抄。

检查显卡和启动器：

```bash
nvidia-smi
test -x "${ISAACLAB_DIR:-$HOME/rlgpu_ws/IsaacLab}/isaaclab.sh" \
  && echo "Isaac Lab launcher: OK"
```

`nvidia-smi` 应显示你的 NVIDIA GPU；第二条应打印 `Isaac Lab launcher: OK`。如果 Isaac Lab 路径检查
失败，先修正 `ISAACLAB_DIR`，不要靠反复启动 Isaac 碰运气。

## 准备公开策略与项目依赖

仍在仓库根目录运行：

```bash
./scripts/fetch_upstream.sh
./scripts/setup_isaac_python_env.sh
```

第一条下载 MicroDuck 公开模型和策略，第二条把 ONNX Runtime 放进项目自己的 `work/` 目录。它们不会
修改你的 Isaac Lab checkout。

检查准备结果：

```bash
test -d reference/microduck && echo "Upstream assets: OK"
test -d work/isaac_python_pkgs/onnxruntime && echo "ONNX Runtime: OK"
```

<div class="md-checkpoint">
  <strong>Isaac 策略环境准备完成</strong>
  <p>两行都显示 <code>OK</code>。只打开仓库自带 USD 时可以跳过这一步；运行公开 ONNX 策略和多动作游乐场时需要它。</p>
</div>

## 常见卡点，先在这里处理

| 现象 | 最先检查 |
| --- | --- |
| `ros2: command not found` | 当前终端是否执行了 `source /opt/ros/jazzy/setup.bash` |
| `colcon: command not found` | 是否安装 `python3-colcon-common-extensions` |
| `Isaac Lab launcher not found` | `ISAACLAB_DIR` 是否指向含 `isaaclab.sh` 的目录 |
| `nvidia-smi` 失败 | NVIDIA 驱动与宿主机 GPU 是否正常 |
| 策略文件缺失 | `fetch_upstream.sh` 是否完整执行，网络下载是否中断 |
| ONNX Runtime 缺失 | 是否从仓库根目录执行 `setup_isaac_python_env.sh` |

<div class="md-page-complete">
  <strong>准备好了，下一站先玩 ROS 2。</strong>
  <p>下一页会构建最小 ROS 2 包并打开 RViz。只想玩 Isaac，也可以在左侧直接点第 6 步。</p>
</div>
