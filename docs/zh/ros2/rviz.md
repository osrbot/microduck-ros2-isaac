# 转转镜头，活动一下关节

这一页专门解决两件事：怎么把 RViz 镜头拖听话，以及模型看起来缺件时应该按什么顺序查。先确认画面，
再确认关节消息，不靠重启碰运气。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>预计时间</span><strong>8–12 分钟</strong></div>
  <div role="listitem"><span>前置结果</span><strong>RViz 已能启动</strong></div>
  <div role="listitem"><span>需要窗口</span><strong>RViz + 1 个终端</strong></div>
  <div role="listitem"><span>完成结果</span><strong>镜头、关节和网格都可检查</strong></div>
</div>

<div class="md-step-kicker"><span>步骤 1</span><strong>RViz 窗口</strong></div>

## 先围着鸭子转一圈

仓库自带的 RViz 配置默认选择 **Move Camera**：

- 左键拖动：绕机器人旋转；
- 鼠标滚轮：缩放；
- 中键拖动：平移。

<div class="md-result-label">真实运行截图 · 镜头旋转并拉近后</div>

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/ros-isaac-rviz-camera.webp" alt="RViz Orbit 镜头旋转、缩放后的 MicroDuck 近景" width="1400" height="900" loading="lazy"></div>
  <figcaption><strong>镜头操作成功时，机器人不会散架，只是观察角度在变。</strong>这张来自联调时的实际 RViz 画面；左侧 Distance、Yaw 和 Pitch 都已经随着拖动发生变化。</figcaption>
</figure>

如果远程桌面不能把 RViz 最大化，可以直接全屏启动：

```bash
ros2 launch microduck_description view_microduck.launch.py \
  rviz_fullscreen:=true
```

直接拖机器人不会改变关节，关节要用滑块控制。

<div class="md-checkpoint">
  <strong>镜头操作正常</strong>
  <p>左键能绕机器人旋转，滚轮能拉近拉远，中键能平移。若拖动没有反应，先确认顶部工具栏选中的是 <strong>Move Camera</strong>。</p>
</div>

<div class="md-step-kicker"><span>步骤 2</span><strong>终端 · ros2_ws 已 source</strong></div>

## 再让它动起来

如果原来的 launch 还在运行，先回到那个终端按 <kbd>Ctrl</kbd>+<kbd>C</kbd>，等日志停止，再执行：

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

可以逐个移动滑块，也可以点击 **Randomize** 快速演示。当前公开仿真模型包含 14 个可动关节。

<div class="md-checkpoint">
  <strong>关节操作正常</strong>
  <p>拖动一个滑块时，只有对应关节链发生变化；把滑块归零后，姿态能回到容易辨认的默认位置。</p>
</div>

<div class="md-step-kicker"><span>步骤 3</span><strong>只在画面异常时执行</strong></div>

## 鸭子看起来少了块零件？

<figure class="md-doc-figure md-bug-figure">
  <img src="/images/rviz-missing-parts.png" alt="RViz 中 MicroDuck 头部与身体分离、部分零件缺失的错误示例" width="646" height="674" loading="lazy">
  <figcaption><strong>像这样就不算正常到场。</strong>头部飘在上面、身体中间断开或左右零件明显不齐，都应该按下面的顺序检查。</figcaption>
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

不要用 collision 网格去“补”缺失的 visual。碰撞网格本来就是更简单的调试模型。

<div class="md-step-kicker"><span>步骤 4</span><strong>新终端 · 检查 ROS 消息</strong></div>

## 滑块动了，鸭子却没动？

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
  <strong>RViz 里已经是一只完整鸭了。</strong>
  <p>镜头能转、零件齐全、14 个关节也能读。下一页让它自己点头、踏步和鞠躬。</p>
</div>
