# 05 Microduck 与强化学习：训练策略如何成为机器人控制

研究日期：2026-11-03。[生态导读](README.md) · [固定源码与范围](sources.md)。本章以行走任务 `Mjlab-Velocity-Flat-MicroDuck` 为基线，静态阅读固定版本源码；恢复、轮滑等任务须另查对应 envcfg。未执行仓库代码、下载权重或训练数据、训练、连接硬件、采购资源或安装依赖；没有真实重跑结果。

## 直觉：学会平衡，不是学会聊天

这里的 RL 学习“看到身体状态和运动命令，下一刻关节该指向哪里”。它不是 LLM Agent 的工具选择、文本奖励或对话训练。`microduck_rl` 负责 MuJoCo/mjlab 环境与策略训练，`microduck` 负责机器人运行时。`robotd` 独立控制线程读取关节与 IMU，经命令门控、策略调度、推理生成目标，再交给 safety 写电机；游戏手柄、蓝牙及媒体服务是外围入口，不能替代这个反馈环。参见[运行环实现](https://github.com/pollen-robotics/microduck/blob/997808c1d71056d31bd6f05fc5fde848c849d2bc/robotd/src/main.rs)。

可以把策略想成不断改正姿势的身体反射，而把远端程序想成提出意图的人。前者要在身体已经倾斜、脚即将落地时及时更新，后者可以较慢地请求前进或转头。即使给远端接上语言模型，也只是多一个命令来源，不能因此把本地运动策略的训练目标、动作空间和反馈频率解释成语言智能体的训练。这是两种职责，不是同一模型的两种名字。

## 观测、历史与动作合同

<!-- illustration: pollen-microduck-contract-0c8d86077c -->
![Microduck 的 61→14，是形状与语义共同的合同。固定行走任务与前馈部署示例；非所有任务共用的通用 schema。](../images/pollen-microduck-contract.png)

*图：Microduck 的 61→14，是形状与语义共同的合同。固定行走任务与前馈部署示例；非所有任务共用的通用 schema。*
<!-- /illustration: pollen-microduck-contract-0c8d86077c -->

前馈部署图接收 float32 `[1,61]`，输出 `[1,14]`。位置与速度使用同一关节顺序：左腿五轴、颈头四轴、右腿五轴；嘴部关节跳过。下表是零起始、右端不包含的索引，维度相同但字段错位仍可能产生“看似正常”的错误动作。[观测组装源码](https://github.com/pollen-robotics/microduck/blob/997808c1d71056d31bd6f05fc5fde848c849d2bc/duck-control/src/obs.rs)固定了这些边界。

| 索引 | 字段 |
| --- | --- |
| 0–3 | 躯干角速度，rad/s |
| 3–6 | 躯干坐标系投影重力，单位向量 |
| 6–20 | 14 轴角度减 HOME，rad |
| 20–34 | 14 轴角速度，rad/s |
| 34–48 | 上一帧原始策略动作 |
| 48–51 | 前进、侧移速度与偏航角速度 |
| 51–55 | 四轴颈头目标相对 HOME 的偏移 |
| 55–61 | 身体 x、y、z、roll、pitch、yaw 偏移 |

运行时身体 x、y、yaw 槽固定为零。头部命令进入观测，不能再叠加一次到输出。动作不是力矩，也不是相对当前角度的增量；名义位置目标为 `q目标 = qHOME + s·a`。训练的 `s=1.0`；运行时行走默认 `0.9`、站立 `1.0`，P 增益默认 200，站立乘 0.8；头部/腿部另有 0.5/0.7 低通。历史反馈仍保存滤波、缩放前的动作。这里必须核对具体模型的配套调参，不能声称默认训练与部署完全一致。[目标与技能调度](https://github.com/pollen-robotics/microduck/blob/997808c1d71056d31bd6f05fc5fde848c849d2bc/robotd/src/control.rs)。

## 训练：时钟、奖励、终止与课程

锁定的 mjlab 1.3.0 默认物理步长为 0.005 s，decimation 为 4，所以仿真积分 200 Hz、策略更新 50 Hz，每步策略跨 20 ms；不能把两者互换。行走继承 20 s episode、倾斜超过 70°终止；超时与越出地形边界标为 time-out，与跌倒失败不同。[继承的基础配置](https://github.com/mujocolab/mjlab/blob/19d6c06c17572dafcb31ad5110a902006b58d944/src/mjlab/tasks/velocity/velocity_env_cfg.py)。

行走 actor 去掉真实线速度和地形扫描，critic 保留线速度、足部高度及接触等特权信息；部署只带 actor。默认不堆叠观测历史，上一动作不等于多帧状态；IMU 延迟 0–1 个控制步，关节速度固定延迟一步。actor/critic 是 512、256、128 隐藏层的 ELU 网络，带观测归一化；PPO 每次每环境采 24 步，clip=0.2、gamma=0.99、lambda=0.95。

奖励同时塑形速度跟踪、直立、颈头跟踪、足部腾空、抬脚及动作平滑；线/角速度跟踪权重各 2，腾空 3，滑移 -0.1。身体姿态跟踪在行走中权重为零，字段存在不代表能力已学会。课程把动作变化惩罚从 -0.1 提至 -1，静止命令比例从 2% 提至 25%，逐步扩大头部目标和质心扰动；速度范围反而固定：x ±0.4、y ±0.3 m/s，yaw ±1 rad/s。粗糙地形保留地形难度课程。行走启用质心、质量/惯量、摩擦、转子惯量、编码器偏置、IMU 安装误差和速度推扰，P/D 增益随机化目前关闭；不是所有扰动都在每次 reset 重采样。摩擦走 BAM 的 friction_scale，不能把修改 MuJoCo frictionloss 当成等效随机化。新增非有限状态终止及 critic 传感项清洗是数值防护，不是物理安全证明。[行走 envcfg](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/src/mjlab_microduck/tasks/microduck_velocity_env_cfg.py)。

理解奖励时，可以先问“如果我原地不动，这一项还会支付吗”，再问“这项惩罚会不会让完成任务反而更亏”。课程也不是部署时逐步放宽安全限制，而是训练分布及目标随计数变化。评价时应另外记录命令跟踪误差、跌倒及恢复、碰撞和失效条件，不能把不同课程阶段的总奖励直接解释成性能提升。本章只解析配方，不替作者重新验证注释中的训练经验。

## Sim-to-real：代码已经提供什么

执行器不是理想 PD 黑盒：训练使用 BAM M6 XL330 电压控制与摩擦模型，固件 P 增益设为 200，电压随机范围 6.5–8.2 V，并模拟负载压降，最低 6 V，命令 delay 参数为 3–6。Backlash 变体把每轴 ±1°齿隙纳入模型，保持策略维数不变；不能把被动铰链或滚轮也计入十四轴输出。[机器人与执行器配置](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/src/mjlab_microduck/robot/microduck_constants.py)。

随机化直觉是让策略面对一组略有差异的身体，而不是保证真实身体一定落在这组分布里。电压、摩擦和安装误差的范围都带假设；换硬件、地面或电池后，不能只保持网络文件不变。模型选择也影响接触：行走模型、地面接触模型、全碰撞模型及轮滑模型不可凭相同观测维数互换。

## Checkpoint 如何跨过部署边界

checkpoint 是可续训资产，含 actor、critic、归一化器、优化器、迭代与 common_step_counter；ONNX 不是这种资产。resume 延续课程；跨任务 warm-start 使用 `MICRODUCK_WARM_START=1` 重置计数，但保留权重、归一化器和优化器。必须同时保留任务、解析后的配置、代码版本及未提交差异，不能只交换一个权重文件。[训练 bundle 合同](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/docs/training_checkpoints.md)。

导出必须经过 runner 的 ONNX 路径，将观测归一化烘焙进图。手工转换可能在仿真 play 中正常，却在接收原始观测的机器人上失效；导出还记录 task、checkpoint 与来源元数据。[导出实现](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/src/mjlab_microduck/export.py)。

部署合同因此不止两个张量形状，还包括关节名称与顺序、HOME、坐标系、单位、命令含义、动作尺度、反馈历史、归一化和控制时钟。排障应先查这些不变量，再讨论奖励或调增益；否则一个字段错位、一个缺失的归一化器，可能被误诊成机器人需要更强的策略。

运行时加载检查类型、名字和形状，并预热；除前馈图，也支持显式 `h_in/c_in → h_out/c_out` 的 LSTM。记忆属于各策略槽，切换、reset 或推理失败时清零，不能当成共享身体状态。不过通用发布器当前只接单输入/单输出，model_api 为 1，不能由“运行时支持 LSTM”推断发布链已支持。[推理与记忆生命周期](https://github.com/pollen-robotics/microduck/blob/997808c1d71056d31bd6f05fc5fde848c849d2bc/duck-control/src/policy.rs)。

schema 2 manifest 还声明维度、kind、时长与命令编码。发布器的形状/非有限值/常量输出检查只是图级 smoke check；phase 与 posture_flag 需要 daemon 的专用调度，不可冒充普通恒定命令技能。这些检查没有证明动作完成、无碰撞或稳妥退回站姿。[发布门槛](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/src/mjlab_microduck/publish/manifest.py)。

## 不要把展示或设计当作验收

`duck-body` 已提供真实 daemon 对接 MuJoCo 身体的实现，但当前使用 XML 执行器，并固定报告电压、温度，不能冒充完整 BAM 训练环境或真实电池/热模型。架构设计页的愿景、README 视频及作者训练记录，也不能补足未读代码、未测配置的证据。[仿真身体实现](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/src/mjlab_microduck/sim/body_server.py)。

运行时 safety 拒绝非有限目标、默认 500 ms deadman 清速度命令，但只限幅到舵机 ±π 行程，不是逐关节机械限位；跌倒判定本身不禁止策略驱动，响应由上层决定。奖励、课程、烟测或漂亮视频均不是安全验收；本章不保证真实物理摆动、接触或人员安全。[安全层的实际边界](https://github.com/pollen-robotics/microduck/blob/997808c1d71056d31bd6f05fc5fde848c849d2bc/duck-control/src/safety.rs)。

读代码顺序：任务注册 → 行走 envcfg → mjlab 基础配置/位置动作 → constants 与 BAM → mdp → checkpoint/export → manifest → obs/policy/control/safety → body_server。理论对照：[PPO 与价值学习](../advanced/chapters/08_rl.md)、[仿真与执行器误差](../advanced/chapters/11_simulation.md)、[运行时合同](../advanced/chapters/12_runtime.md)。

自测：为什么嘴部偏移会错配右腿？5 ms×4 为何不是 200 Hz 策略？上一动作应存滤波前还是滤波后？resume 与 warm-start 如何影响课程？61→14 图检查通过为何仍不能授权真机运动？答案分别对应关节顺序、双时钟、历史合同、计数恢复与安全证据边界。
