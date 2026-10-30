# 修改一个训练任务

本章把现有行走任务改为**只练低速前进**。你会修改速度命令，运行短训练，再加载模型检查动作。
最后介绍增加坡面、起身或踢球任务时，需要改哪些配置。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>本次目标</span><strong>低速直行</strong></div>
  <div role="listitem"><span>执行位置</span><strong>Linux 仓库根目录</strong></div>
  <div role="listitem"><span>前置步骤</span><strong>完成第 10 章</strong></div>
  <div role="listitem"><span>完成结果</span><strong>配置、模型和报告</strong></div>
</div>

> 本页修改示例已按项目源码检查；新增设置尚未在 GPU 上运行验证。先执行下方短训练，确认配置生效。

## 1. 保存当前配置 {#backup}

先关闭正在使用这个任务的训练或回放。在 Ubuntu 终端进入仓库根目录，执行：

```bash
custom_id=$(date +%Y%m%d-%H%M%S)
custom_run="$PWD/work/custom-velocity/$custom_id"
custom_evidence="$PWD/artifacts/custom-velocity/$custom_id"
custom_backup="$PWD/backups/custom-velocity/$custom_id"
cfg="$PWD/source/microduck_isaac_lab/microduck_isaac_lab/tasks/velocity/velocity_env_cfg.py"
test -f "$cfg" || exit 1
mkdir -p "$custom_run" "$custom_evidence" "$custom_backup"
cp "$cfg" "$custom_backup/velocity_env_cfg.py"
```

命令会建立本次实验的日志、回放和备份目录，并保存修改前的配置。后面的命令在同一个终端执行，继续使用这些变量。

## 2. 把速度命令改为低速直行 {#configure}

用文本编辑器打开 `source/microduck_isaac_lab/microduck_isaac_lab/tasks/velocity/velocity_env_cfg.py`。
找到 **`MicroDuckVelocityFlatEnvCfg` 类中的 `__post_init__()`**，保留原有设置，在末尾加入下面的六行速度和课程设置。
修改后的函数如下；文件末尾还有一个 `_PLAY` 类，本步修改前面的基础类。

```python
    def __post_init__(self) -> None:
        self.decimation = 4
        self.episode_length_s = 20.0
        self.sim.dt = 0.005
        self.sim.render_interval = self.decimation
        self.sim.physics_material = self.scene.terrain.physics_material
        self.scene.left_foot_contact.update_period = self.sim.dt
        self.scene.right_foot_contact.update_period = self.sim.dt

        self.commands.base_velocity.ranges.lin_vel_x = (0.1, 0.2)
        self.commands.base_velocity.ranges.lin_vel_y = (0.0, 0.0)
        self.commands.base_velocity.ranges.ang_vel_z = (0.0, 0.0)
        self.commands.base_velocity.rel_standing_envs = 0.0
        self.commands.base_velocity.rel_turn_in_place_envs = 0.0
        self.curriculum.standing_fraction = None
```

| 设置 | 为什么这样改 |
| --- | --- |
| 前进速度 `0.1～0.2 m/s` | 先练较小范围的前进速度；这是练习用的目标范围 |
| 横向速度和转向速度均为 `0` | 本次只要求沿自身前方行走 |
| 站立、原地转向比例均为 `0` | 每个环境都收到前进命令 |
| `standing_fraction = None` | 关闭会逐步增加站立样本的课程，保持上面的设置 |

模型、关节顺序、观测、奖励和 PPO 参数沿用原任务。`_PLAY` 类继承基础类，因此回放也使用这些速度设置。
“向前”以机器人当前朝向为准；它仍会从不同朝向出生。

## 3. 检查修改 {#check}

回到刚才的终端执行：

```bash
python3 - "$cfg" <<'PY'
import ast
from pathlib import Path
import sys
ast.parse(Path(sys.argv[1]).read_text())
print("Configuration syntax: OK")
PY
git diff -- "$cfg"
```

应看到 `Configuration syntax: OK`。再看 `git diff`，确认本次只增加了上述六行。
如果文件原来就有自己的修改，以第 1 步的备份为对照，保留原有内容。

## 4. 跑一次短训练 {#train}

使用[第 10 章](./training)准备好的 Isaac Lab 环境，在同一终端运行：

```bash
set -o pipefail
MICRODUCK_TRAIN_ENVS=64 MICRODUCK_TRAIN_ITERATIONS=5 \
  ./scripts/train_isaac_velocity.sh --headless \
  --log-root "$custom_run/logs" 2>&1 | tee "$custom_run/train.log"
```

终端应依次进入创建环境、学习和保存阶段，最后打印 `MICRODUCK_TRAIN_STAGE=complete`。
本次模型位于 `work/custom-velocity/<实验时间>/logs/<运行时间>/`。

打开该目录的 `params/env.yaml`，检查 `base_velocity` 下的三个速度范围，以及站立、原地转向比例；
再确认 `curriculum.standing_fraction` 已关闭。目录中还应有 `model_final.pt` 和 `training_summary.json`。
五次更新用于检查配置与保存流程，稳定步态需要继续训练和回放比较。

## 5. 回放这个模型 {#replay}

训练退出后，把第一行换成本次 `model_final.pt` 的实际绝对路径：

```bash
checkpoint=/absolute/path/to/your/run/model_final.pt
test -f "$checkpoint" || exit 1
MICRODUCK_PLAY_STEPS=1000 \
MICRODUCK_PLAY_OUTPUT="$custom_evidence/playback.json" \
MICRODUCK_PLAY_SCREENSHOT="$custom_evidence/playback.png" \
  ./scripts/play_isaac_velocity.sh --checkpoint "$checkpoint"
```

这次回放运行 1000 个控制步，约 20 秒仿真时间。检查：

- 模型能加载，终端没有 NaN 或维度错误；
- 鸭子是否尝试向自身前方迈步，有没有持续侧移、转圈或摔倒；
- `playback.json` 和 `playback.png` 是否生成。

先保持这六项设置和奖励不变，按第 10 章逐步增加训练轮数。每次用相同回放设置比较动作，再决定是否调奖励。

## 6. 结束实验或继续扩展 {#extend}

记录修改原因、训练轮数、模型路径和回放表现。想恢复实验前的配置时，先停止相关进程。
如果文件只有本次六行修改，可以在同一终端执行下面的恢复命令；如果还做过其他修改，先比较备份与当前文件，只撤回本次六行。

```bash
cp "$custom_backup/velocity_env_cfg.py" "$cfg"
```


下一步可以增加坡面、起身姿态或小球。需要改动的位置如下：

| 想增加什么 | 先修改哪里 | 怎么检查 |
| --- | --- | --- |
| 坡面或障碍 | `MicroDuckSceneCfg` | reset 后机器人位于地面上，接触正常 |
| 起身任务 | `EventsCfg`、`RewardsCfg`、`TerminationsCfg` | 从倒地开始，记录站起用时和再次摔倒次数 |
| 踢球任务 | 场景中的球、球位置观测、踢球奖励和终止条件 | 记录球沿目标方向的位移，同时检查鸭子是否站稳 |

游乐场已有 70 mm、15 g 小球，可参考它的物理设置。训练环境仍需新增球的位置观测、重置与奖励。
加入新观测后，输入维度会变化，要同步调整网络；旧的 61 维策略不能直接读取额外的球位置。

<div class="md-page-complete">
  <strong>下一步：学习起身和转向的训练方法</strong>
  <p>你已经知道如何修改配置、确认生效并回放模型。第 16 章进一步解释教师模型、初始姿态和奖励的调整。</p>
</div>
