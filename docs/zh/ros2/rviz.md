# 使用 RViz

## 移动相机

仓库配置默认选择 **Move Camera**。左键拖动旋转 Orbit 视图，滚轮缩放，中键拖动平移。如果远程桌面无法最大化窗口：

```bash
ros2 launch microduck_description view_microduck.launch.py \
  rviz_fullscreen:=true
```

RViz 不是网格编辑器，直接拖机器人不会改变关节。

## 操作关节

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

使用 Joint State Publisher 滑块或 **Randomize**，数据链路应为：

```text
joint_state_publisher_gui -> /joint_states -> robot_state_publisher -> /tf -> RViz
```

官方仿真与策略契约只有 14 个可动关节。实体机器人的嘴部执行器不在这份描述中，项目不会虚构第 15 个仿真关节。

## RViz 看起来缺件时

先区分相机遮挡和描述资源错误：

1. 在 Views 面板使用 **Reset**，再绕机器人旋转一周。
2. 在 **RobotModel** 确认 `Visual Enabled` 已启用且 `Alpha` 为 `1`。
3. 展开 `Links`；缺失网格会在对应 link 报错，记录第一个 link 名称和资源错误。
4. 查看 launch 终端是否存在 `package://microduck_description/meshes/...` 加载失败。
5. 重新生成并检查：

   ```bash
   ./scripts/generate_ros_description.py
   ./scripts/validate_ros2_package.sh
   ```

6. 重新 source 当前 workspace 后再启动：

   ```bash
   cd ros2_ws
   source /opt/ros/jazzy/setup.bash
   source install/setup.bash
   ```

不要用 collision 网格“填补”缺失 visual。碰撞网格本来就更简化，是独立的诊断层。

## 检查碰撞几何

```bash
ros2 launch microduck_description view_microduck.launch.py \
  with_collision_meshes:=true
```

随后在 RobotModel 启用 **Collision Enabled**。常规演示时请关闭；它会在约 79.7 万 visual 三角形之外额外增加约 17.1 万三角形。

| 现象 | 优先检查 |
| --- | --- |
| 相机不能旋转/缩放 | 是否加载仓库 RViz 配置及 Tools 块 |
| 颈部或腿部分离 | 重新生成，并运行 MJCF/URDF 位姿对比 |
| 整个 link 消失 | RobotModel link 错误和网格 URI |
| 灰色模型存在但细节看不清 | 光照、相机角度和 visual Alpha |
| 滑块变化但模型不动 | `/joint_states`、`/tf` 和当前 overlay |

更多命令见[故障排查](/zh/troubleshooting)。
