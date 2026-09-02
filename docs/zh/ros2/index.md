# 把 MicroDuck 请进 ROS 2 和 RViz

这是仓库里最短的一条路线。description、网格、launch 和 RViz 配置都准备好了，不用先考古模型，
几条命令就能让鸭子露个脸。

## 1. 构建功能包

在仓库根目录运行：

```bash
cd ros2_ws
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
```

如果提示找不到 ROS 2 或 `colcon`，先回到[安装说明](/zh/guide/installation)。

## 2. 让鸭子露个脸

```bash
ros2 launch microduck_description view_microduck.launch.py
```

RViz 应该会打开，并显示保持默认姿态的 MicroDuck。

## 3. 让它活动一下关节

按 <kbd>Ctrl</kbd>+<kbd>C</kbd> 停止上一次 launch，然后运行：

```bash
ros2 launch microduck_description view_microduck.launch.py use_gui:=true
```

这时会多出一个 Joint State Publisher 窗口。拖动滑块，RViz 中对应的关节应该一起移动。

## 鸭子正常到场时应该看到什么

- RViz 能打开，RobotModel 没有红色错误；
- 头部、身体、两条腿和脚都能看到；
- 左键拖动可旋转，滚轮缩放，中键拖动可平移；
- 拖动滑块时机器人姿态会变化。

下一步可以查看[移动镜头和关节](./rviz)，或者直接跑
[ROS 2 自动例程](./examples)，让鸭子自己点头、踏步和指挥 Isaac 表演。

## 常用启动参数

| 参数 | 用途 |
| --- | --- |
| `use_gui:=true` | 打开关节滑块 |
| `rviz_fullscreen:=true` | 桌面不能最大化时直接全屏 |
| `use_rviz:=false` | 只运行 description 和 TF，不打开 RViz |
| `with_collision_meshes:=true` | 调试时显示碰撞几何 |

::: details 给维护者：重新生成 description
只有修改上游模型或生成器时才需要运行：

```bash
cd ..
./scripts/fetch_upstream.sh
./scripts/setup_mujoco_env.sh
./scripts/generate_ros_description.py
./scripts/validate_ros2_package.sh
```

重新生成后，再构建 ROS workspace 并重启 launch。
:::
