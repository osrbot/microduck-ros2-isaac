# 把 MicroDuck 请进 ROS 2 和 RViz

这是仓库里最短的一条完整路线：构建 description 包、打开 RViz、确认模型没有缺件，再用滑块活动 14 个
关节。全程只用 ROS 2，不需要 Isaac Sim，也不需要真机。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>预计时间</span><strong>10–15 分钟</strong></div>
  <div role="listitem"><span>需要环境</span><strong>Ubuntu 24.04 + Jazzy</strong></div>
  <div role="listitem"><span>窗口数量</span><strong>1 个终端 + 2 个 GUI</strong></div>
  <div role="listitem"><span>完成结果</span><strong>完整模型与 14 关节可动</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>这页会完成四件事</strong>
  <ul>
    <li>只构建入门所需的 <code>microduck_description</code>；</li>
    <li>在 RViz 中看到头、身体、双腿和双脚；</li>
    <li>用 Joint State Publisher GUI 拖动关节；</li>
    <li>从终端确认 <code>/joint_states</code> 真的在发布数据。</li>
  </ul>
</div>

::: tip 先确认当前目录
下面第一条命令假设你位于仓库根目录，也就是能看到 `README.md` 和 `ros2_ws/` 的位置。
:::

<div class="md-command-steps">
  <strong>先开终端 A</strong>
  <p>按 <kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>T</kbd>。如果终端默认打开在主目录，先执行 <code>cd /你的路径/microduck-ros2-isaac</code> 进入仓库；代码里的“你的路径”要换成真实路径。</p>
</div>

<div class="md-step-kicker"><span>步骤 1</span><strong>终端 A · 按 Ctrl + Alt + T 打开</strong></div>

## 构建 description 包

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-select microduck_description
source install/setup.bash
```

构建成功时，末尾应出现类似：

```text
Summary: 1 package finished
```

再确认 ROS 2 能找到刚构建的包：

```bash
ros2 pkg prefix microduck_description
```

输出路径应落在当前仓库的 `ros2_ws/install/microduck_description`。如果提示找不到包，通常是最后一条
`source install/setup.bash` 漏了；如果连 `colcon` 都找不到，先回到[安装与环境检查](/zh/guide/installation)。

<div class="md-checkpoint">
  <strong>构建这一关通过</strong>
  <p><code>colcon</code> 没有失败包，<code>ros2 pkg prefix</code> 能返回当前 workspace 的安装路径。现在再开 RViz，出错时就不会把构建问题和显示问题混在一起。</p>
</div>

<div class="md-step-kicker"><span>步骤 2</span><strong>终端 A · ros2_ws 目录</strong></div>

## 先用默认姿态打开 RViz

```bash
ros2 launch microduck_description view_microduck.launch.py
```

这是一条持续运行的命令：提示符不会马上回来，终端里继续出现日志是正常的。**终端 A 保持运行，
不要关。**稍等几秒，RViz 会打开，MicroDuck 应站在网格中央。先别急着拖视角，按下面顺序检查：

1. 左侧 `RobotModel` 没有红色错误；
2. 头部和身体连在一起；
3. 左右两条腿、两只脚都能看到；
4. `Fixed Frame` 使用 `base_link`，网格稳定不乱跳。

<div class="md-result-label">真实运行截图 · RViz 打开后</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros2-rviz-motion-demo.webp" alt="ROS 2 自动关节例程在 RViz 中完整显示 MicroDuck" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>鸭子完整到场时，零件关系应该像这样。</strong>图片来自自动动作例程，所以它正在抬腿；本步骤启动后会保持默认站姿。先看头、身体、双腿和双脚有没有落队。</figcaption>
</figure>

<div class="md-checkpoint">
  <strong>画面这一关通过</strong>
  <p>RViz 中是一只完整的 MicroDuck，RobotModel 没有网格路径错误。若头身分离或零件消失，先去看<a href="/microduck-ros2-isaac/zh/ros2/rviz">缺件检查步骤</a>，不要继续用滑块把问题搅得更花。</p>
</div>

<div class="md-step-kicker"><span>步骤 3</span><strong>终端 A · 重新启动</strong></div>

## 打开关节滑块

回到终端 A，按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 停止上一次 launch。看到进程退出后再运行：

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

这次会出现两个窗口：RViz 和 **Joint State Publisher**。在滑块窗口中做一个最小测试：

1. 先轻轻拖动 `head_yaw`，确认头部左右转动；
2. 把它拖回接近 `0`；
3. 再轻轻拖动一个膝关节，确认对应腿部弯曲；
4. 点击 **Center** 或把滑块归零，让鸭子回到容易辨认的姿态。

滑块会限制在 URDF 关节上下限内，但它只是可视化关节状态，不包含重力和接触。鸭子在 RViz 中摆出
高难度姿势，不代表物理世界里也站得住。

<div class="md-result-label">官方界面参考 · Joint State Publisher</div>

<figure class="md-doc-figure md-jsp-figure">
  <div class="md-doc-image-stage md-jsp-stage"><img src="/images/joint-state-publisher-gui-official.png" alt="ROS 2 Joint State Publisher 官方滑块窗口截图" width="272" height="194" loading="lazy"></div>
  <figcaption><strong>滑块窗口大致就是这个样子。</strong>这张是 ROS 官方包的界面参考，所以只写了 <code>joint_A</code>、<code>joint_B</code>、<code>joint_C</code>；MicroDuck 实际窗口会列出 14 个真实关节名。拖动后要回 RViz 看对应部位有没有一起动。<a href="https://github.com/ros/joint_state_publisher/tree/ros2/joint_state_publisher_gui">图片来源：ROS joint_state_publisher_gui ↗</a></figcaption>
</figure>

<div class="md-step-kicker"><span>步骤 4</span><strong>终端 B · 新开终端</strong></div>

## 确认关节消息真的在流动

保持终端 A、RViz 和滑块窗口运行。把鼠标放到终端 A 上，按
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> 新开窗口 B；屏幕小也可以按
<kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>T</kbd> 新开标签页。

```bash
cd /path/to/microduck-ros2-isaac/ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic echo /joint_states --once
```

把第一行的 `/path/to/microduck-ros2-isaac` 换成仓库真实路径。执行后会打印一条 YAML 消息并自动结束，
结构类似：

```yaml
name: [left_hip_yaw, ..., right_ankle]
position: [0.0, ..., 0.0]
```

输出里应有 `name` 和 `position`。`name` 列表包含 14 个关节；拖动滑块后再次按终端的
<kbd>↑</kbd> 调出上一条命令并按 <kbd>Enter</kbd>，相关 `position`
数值应该变化。

<div class="md-checkpoint">
  <strong>ROS 数据这一关通过</strong>
  <p><code>/joint_states</code> 能返回 14 个关节，并且滑块变化会进入消息。到这里，“模型显示”和“ROS 状态发布”两条链都已打通。</p>
</div>

## 常用启动参数

| 参数 | 什么时候用 |
| --- | --- |
| `use_gui:=true` | 打开关节滑块，手动检查 14 个关节 |
| `rviz_fullscreen:=true` | 远程桌面无法最大化窗口时，直接全屏启动 |
| `use_rviz:=false` | 只运行 description 和 TF，不打开 RViz |
| `with_collision_meshes:=true` | 调试碰撞几何；普通浏览建议关闭 |

例如，远程桌面下同时打开滑块和全屏 RViz：

```bash
ros2 launch microduck_description view_microduck.launch.py \
  use_gui:=true rviz_fullscreen:=true
```

::: details 给维护者：什么时候才需要重新生成 description
普通使用者不需要运行生成器。只有修改上游模型或生成代码时，才从仓库根目录运行：

```bash
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
./scripts/generate_ros_description.py
./scripts/validate_ros2_package.sh
```

生成后重新执行本页步骤 1，再启动 RViz 验证。
:::

<div class="md-page-complete">
  <strong>第一圈遛完了。</strong>
  <p>你已经构建了 ROS 2 包、看到了完整模型、拖动了真实关节消息。想继续手动看模型就去相机与缺件页；想让鸭子自己表演，就直接跑自动例程。</p>
</div>

<div class="md-next-grid">
  <a class="md-next-card" href="/microduck-ros2-isaac/zh/ros2/rviz"><span>模型检查</span><strong>学会拖镜头与排查缺件 →</strong><p>视角、全屏、RobotModel、网格路径和 joint_states 都逐项检查。</p></a>
  <a class="md-next-card" href="/microduck-ros2-isaac/zh/ros2/examples"><span>更好玩</span><strong>让鸭子自动点头和踏步 →</strong><p>不需要 Isaac，直接运行 RViz-only 动作例程。</p></a>
</div>
