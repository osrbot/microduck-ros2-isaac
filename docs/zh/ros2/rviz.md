# 转转镜头，活动一下关节

## 先围着鸭子转一圈

仓库自带的 RViz 配置默认选择 **Move Camera**：

- 左键拖动：绕机器人旋转；
- 鼠标滚轮：缩放；
- 中键拖动：平移。

如果远程桌面不能把 RViz 最大化，可以直接全屏启动：

```bash
ros2 launch microduck_description view_microduck.launch.py \
  rviz_fullscreen:=true
```

直接拖机器人不会改变关节，关节要用滑块控制。

## 再让它动起来

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

可以逐个移动滑块，也可以点击 **Randomize** 快速演示。当前公开仿真模型包含 14 个可动关节。

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

## 滑块动了，鸭子却没动？

打开另一个终端，source workspace，然后检查关节消息：

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 topic echo /joint_states --once
```

如果没有消息，重新使用 `use_gui:=true` 启动，并查看 Joint State Publisher 终端的错误。

## 可选：显示碰撞几何

```bash
ros2 launch microduck_description view_microduck.launch.py \
  with_collision_meshes:=true
```

随后在 RobotModel 中打开 **Collision Enabled**。正常查看时建议关闭，否则 RViz 会更卡。

如果仍然卡顿或网格路径持续报错，继续看[故障排查](/zh/troubleshooting)。
