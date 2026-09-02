# 下一关：自己再造一个训练任务

这一页是开发路线图，不是假装“一条命令自动造环境”。目标是把一个动作拆成场景、成功条件、reward、
终止与回放验收，避免训练几小时后才发现问题定义本身就含糊。

<div class="md-tutorial-meta" role="list" aria-label="本页概览">
  <div role="listitem"><span>规划时间</span><strong>20–30 分钟</strong></div>
  <div role="listitem"><span>开发时间</span><strong>按任务另算</strong></div>
  <div role="listitem"><span>前置结果</span><strong>平地训练 smoke 已通过</strong></div>
  <div role="listitem"><span>本页产物</span><strong>可实现、可验收的任务定义</strong></div>
</div>

<div class="md-tutorial-goals">
  <strong>先把新任务写成四句话</strong>
  <ul>
    <li>场景里新增什么；</li>
    <li>机器人收到什么命令；</li>
    <li>怎样算成功，怎样算失败；</li>
    <li>回放时必须看到什么动作，才允许说“学会了”。</li>
  </ul>
</div>

## 第一项推荐：踢球鸭

仓库已经有 70 mm、15 g 小球和左右脚摆放基线，成功指标也直观，直播时比奖励曲线更容易看懂。先做
单侧踢球，再镜像到另一侧；不要第一天就把走路、起身、踢球和前滚塞进同一张网里互相抢 reward。

<figure class="md-doc-figure">
  <div class="md-doc-image-stage"><img src="/images/isaac-playground-live.webp" alt="MicroDuck 与黄色小球在 Isaac 多动作游乐场中的真实运行画面" width="1400" height="876" loading="lazy"></div>
  <figcaption><strong>先从已经验证过的场景基线出发。</strong>球的尺寸、质量和初始摆位已经在游乐场里实际运行；新训练任务可以复用场景事实，但不能把公开踢球策略的回放当成自己的训练结果。</figcaption>
</figure>

## 任务优先级怎么排

| 任务 | 场景里新增什么 | 最重要的成功指标 | 第一版先不做什么 |
| --- | --- | --- | --- |
| 粗糙地形行走 | height-field、台阶、坡面 | 不摔倒且跟得上速度 | 不同时训练踢球 |
| 起身 | 仰躺/趴倒随机出生 | 限时回到稳定站姿 | 不追求花式动作 |
| 踢球 | 球、脚侧、目标方向 | 球向目标移动且鸭子不倒 | 不先做双脚连续盘带 |
| 低头碰地 | 嘴尖 contact/site 目标 | 碰地后能重新站稳 | 不与捡取物体混做 |
| 坐下/起身 | 二值姿态命令 | 两个方向都温和完成 | 不先合并前滚 |

<div class="md-step-kicker"><span>步骤 1</span><strong>先写验收条件</strong></div>

## 以踢球任务为例，先定“成功”

第一版可以把一次 episode 写成：

1. 鸭子以稳定站姿出生，球随机放在左脚前方的小范围内；
2. 命令给出目标方向；
3. 脚接触球后，球在限定时间内沿目标方向移动至少一个阈值；
4. 机器人根部高度与倾角保持在安全范围；
5. 超时、摔倒或球跑出场地就结束 episode。

阈值先来自可视化与现有场景测量，再通过短实验调整。不要为了让 reward 好看，把“脚蹭到球”偷偷改成
“踢球成功”。

<div class="md-step-kicker"><span>步骤 2</span><strong>复制最少的任务骨架</strong></div>

## 从现有任务复用哪些部分

原生任务位于：

```text
source/microduck_isaac_lab/microduck_isaac_lab/tasks/velocity/
```

新增任务时保留公共模型和 61 维接口契约，只替换真正与任务相关的配置：

1. `SceneCfg`：加入球、障碍、地形或目标；
2. `CommandsCfg`：定义策略究竟要跟踪什么命令；
3. `EventsCfg`：随机出生姿态、物体位置、扰动、质量和摩擦；
4. `RewardsCfg`：一个主任务 reward，加少量安全与平滑约束；
5. `TerminationsCfg`：成功、摔倒、越界和超时；
6. `CurriculumCfg`：先让任务可学，再逐步扩大随机化和动作要求；
7. `agents/`：先复用现有 PPO 配置，确认不是环境问题后再调网络。

::: tip 一次只改一层
先让环境 reset、观测和 reward 都 finite，再开始短训练；先让短训练保存 checkpoint，再开始调 reward；
先让单侧踢球稳定，再镜像到另一侧。这样失败时知道该回哪一步。
:::

<div class="md-step-kicker"><span>步骤 3</span><strong>按三个门槛验证</strong></div>

## 新任务的最小验收表

| 门槛 | 必须检查 | 不通过时先查什么 |
| --- | --- | --- |
| 契约检查 | 观测 61 维、动作 14 维、关节顺序不变 | observation term 与关节映射 |
| 环境检查 | 多环境 reset、接触与随机化正常，数值 finite | scene、sensor、event 配置 |
| 短训练检查 | PPO 能更新，checkpoint 能保存 | reward、termination、显存与 runner |
| 行为检查 | 回放连续动作，任务真的完成 | reward 漏洞、命令分布、课程难度 |
| 稳定性检查 | 多 seed、多初始位置仍能完成 | 是否只记住单一出生状态 |

最重要的是最后两行。总 reward 上升只能说明策略找到了某种得分方法，不保证它学到的是你脑子里的动作。

<div class="md-step-kicker"><span>步骤 4</span><strong>单任务稳定后再组合</strong></div>

## 什么时候才做多技能

单个任务在多种初始条件下稳定后，再比较三种组合方式：

- 每个动作一张网，由运行时状态机安全切换；
- 共享 actor，并给观测加入明确的 skill id；
- 用多个专家策略做蒸馏。

现有[多动作游乐场](./playground)已经演示第一种，也是最容易解释和调试的起点。不要因为“统一大模型”
听起来厉害，就提前放弃可验收性。

<div class="md-page-complete">
  <strong>整条教程路线走完了。</strong>
  <p>现在你可以挑一个新动作，写清场景、控制方式和成功画面，再开始动手实现。</p>
</div>
