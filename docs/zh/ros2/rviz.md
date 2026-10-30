# 调整 RViz 视角和关节

本页教你旋转、缩放和平移视角，操作关节滑块，并检查模型缺件或关节不动的问题。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>预计时间</span><strong>8–12 分钟</strong></div>
  <div role="listitem"><span>前置结果</span><strong>RViz 已能启动</strong></div>
  <div role="listitem"><span>需要窗口</span><strong>RViz + 1 个终端</strong></div>
  <div role="listitem"><span>完成结果</span><strong>镜头、关节和网格都可检查</strong></div>
</div>

<div class="md-step-kicker"><strong>RViz 窗口</strong></div>

## 1. 先围着鸭子转一圈 {#先围着鸭子转一圈}

仓库自带的 RViz 配置默认选择 **Move Camera**：

- 左键拖动：绕机器人旋转；
- 鼠标滚轮：缩放；
- 中键拖动：平移。

<div class="md-result-label">真实运行截图 · 镜头旋转并拉近后</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-camera.webp" alt="RViz Orbit 镜头旋转、缩放后的 MicroDuck 近景" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>拖动鼠标可以改变观察角度。</strong>左侧 Distance、Yaw 和 Pitch 会随缩放和旋转变化。</figcaption>
</figure>

::: warning ROS 2 Humble：不要添加全屏参数
在 Humble 中，不要添加 `rviz_fullscreen:=true`：它会向 RViz 传入不受支持的
`--fullscreen` 选项，导致程序在窗口打开前退出。请使用下面的命令，需要大窗口时手动最大化：

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

下文环境命令以 Jazzy 为准。在 Humble 中测试时，用
`source /opt/ros/humble/setup.bash` 替换 `source /opt/ros/jazzy/setup.bash`。
:::

在 Jazzy 中，如果远程桌面不能把 RViz 最大化，可以直接全屏启动：

```bash
ros2 launch microduck_description view_microduck.launch.py \
  rviz_fullscreen:=true
```

直接拖机器人不会改变关节，关节要用滑块控制。

<div class="md-checkpoint">
  <strong>镜头操作正常</strong>
  <p>左键能绕机器人旋转，滚轮能拉近拉远，中键能平移。若拖动没有反应，先确认顶部工具栏选中的是 <strong>Move Camera</strong>。</p>
</div>

<div class="md-step-kicker"><strong>终端 · ros2_ws 已 source</strong></div>

## 2. 再让它动起来 {#再让它动起来}

如果原来的 launch 还在运行，先回到那个终端按 <kbd>Ctrl</kbd>+<kbd>C</kbd>，等日志停止，再执行：

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

可以逐个移动滑块，也可以点击 **Randomize** 快速演示。当前公开仿真模型包含 14 个可动关节。

<div class="md-checkpoint">
  <strong>关节操作正常</strong>
  <p>拖动一个滑块时，只有对应关节链发生变化；把滑块归零后，姿态能回到容易辨认的默认位置。</p>
</div>

<div class="md-step-kicker"><strong>只在画面异常时执行</strong></div>

## 鸭子看起来少了块零件？ {#鸭子看起来少了块零件}

<figure class="md-doc-figure md-bug-figure">
  <img src="/images/rviz-missing-parts.png" alt="RViz 中 MicroDuck 头部与身体分离、部分零件缺失的错误示例" width="646" height="674" loading="lazy">
  <figcaption><strong>模型缺件示例。</strong>头部飘在上面、身体中间断开或左右零件明显不齐，都应该按下面的顺序检查。</figcaption>
</figure>

1. 先绕机器人旋转一圈，有些零件只是被身体挡住了。
2. 在 **Views** 面板点击 **Reset**。
3. 在 **RobotModel** 中确认 **Visual Enabled** 已打开，**Alpha** 为 `1`。
4. 展开 **Links**，加载失败的网格会在对应 link 旁边显示错误。
5. 查看 launch 终端中是否有失败的 `package://microduck_description/meshes/...` 路径。
6. 重新 source workspace 后再启动：

   ```bash
   cd ros2_ws
   source /opt/ros/jazzy/setup.bash
   source install/setup.bash
   ros2 launch microduck_description view_microduck.launch.py use_gui:=true
   ```

显示缺件时检查 visual 网格路径。Collision 网格用于碰撞计算，几何通常更简化。

<div class="md-step-kicker"><strong>新终端 · 检查 ROS 消息</strong></div>

## 滑块动了，鸭子却没动？ {#滑块动了-鸭子却没动}

保持 RViz 和滑块窗口运行。在原终端按 <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>N</kbd> 打开另一个窗口，
source workspace，然后检查关节消息：

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic echo /joint_states --once
```

命令会在收到一帧数据后自动结束。看到 `name:` 与 `position:` 就说明消息已经到达；它一直等着不返回时，
才需要检查 Joint State Publisher 是否仍在运行。

如果没有消息，重新使用 `use_gui:=true` 启动，并查看 Joint State Publisher 终端的错误。

## 可选：显示碰撞几何

```bash
ros2 launch microduck_description view_microduck.launch.py \
  with_collision_meshes:=true
```

随后在 RobotModel 中打开 **Collision Enabled**。正常查看时建议关闭，否则 RViz 会更卡。

<div class="md-page-complete">
  <strong>视角和关节操作完成</strong>
  <p>镜头能转、零件齐全、14 个关节也能读。下一页让它自己点头、踏步和鞠躬。</p>
</div>
