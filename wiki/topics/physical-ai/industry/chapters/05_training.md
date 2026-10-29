## 05 训练、微调与实验管理产品

本章以 2026-10-27 的公开文档为核验口径。训练框架、机器人工作流和实验管理是不同责任层：框架计算梯度，机器人工作流组织数据或环境，实验平台保存过程与产物。下面按交付职责分类，不按品牌排序。`main`、`latest` 指访问日可查文档，不意味着任意旧发布包都具有相同接口。

### 本阶段应交付什么

进入模型适配前，团队应交付可追溯的数据或环境版本、观测／动作字段、单位与频率，以及不混入训练集的验证划分。完成训练后应交付 checkpoint、归一化统计、模型和优化器配置、依赖版本、随机种子、训练日志、闭环评估记录及恢复／回滚说明。这是本手册定义的交接包，不是任一产品自动提供的生产验收证书。

实验系统里至少把“数据版本—训练 run—模型版本—评估条件”关联起来。只保存最低 loss 的文件名，无法说明它对应哪台机器人、哪个相机位置或哪种动作定义；同样，登记成“production”也不代表已经完成硬件、安全和现场验收。

### PyTorch：训练基础组件，不是机器人方案

PyTorch 提供张量运算、自动求导、模型模块、优化器和数据加载组件。前端接收经过项目预处理的图像、本体状态、动作标签或交互样本，后端产出更新后的模型参数与训练统计；任务损失、数据语义、机器人接口仍由上层代码定义。官方基础教程按数据、模型、求导、优化、保存加载组织流程，不能把这一通用能力写成预装的抓取、运动或产线方案。[PyTorch 基础组件](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)

获取方式是安装匹配设备的软件包或使用项目源码，在本地工作站、服务器或云计算节点执行 Python 训练程序。设备需求取决于网络、批大小及构建支持，不是所有训练必须使用同一种 GPU。多进程训练可接 `torch.distributed` 与 DDP；计算节点、通信后端、驱动和网络配置需匹配，不能因“支持分布式”就假设已有调度、容错和集群运维。[分布式接口](https://docs.pytorch.org/docs/2.14/distributed.html)

它能作为 LeRobot、仿真 RL 库或自有训练程序的计算底座；交接时还要保存数据处理、优化器状态及动作恢复配置。公开文档证明的是组件可取得和接口可实现，不证明目标机器人已有可用策略，也不代替仿真器、示范采集、实验审批、实时控制器和安全联锁。[基础工作流范围](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)

### Isaac Lab：仿真任务与策略训练工作流

Isaac Lab 的职责是组织机器人资产、场景、传感器、动作和任务环境，再与训练算法连接。输入不仅是机器人模型，还包括场景、奖励／终止条件、观测配置和随机化参数；输出是交互轨迹及训练侧生成的策略，而不是由物理后端直接输出“通用机器人权重”。当前公开文档提供共享资产、传感器和场景接口，并把后端选择落实到任务支持的配置。[Isaac Lab 后端范围](https://isaac-sim.github.io/IsaacLab/main/source/concepts/physics_backends.html)

多后端应按当前范围写清：PhysX 通过 Isaac Sim／Omniverse Kit 运行；Newton 是 Warp 原生路径，不要求 Isaac Sim；OvPhysX 可在不带 Kit 的进程里使用 PhysX，并有独立安装项，不能与 Kit 在同一进程混用。Newton 文档列出 MJWarp、Kamino、VBD、MPM 等求解器入口，但某个环境能用哪些 preset，要看该任务的支持列表，不能推断全部功能互通。[后端契约](https://isaac-sim.github.io/IsaacLab/main/source/concepts/physics_backends.html)、[Newton 集成](https://isaac-sim.github.io/IsaacLab/main/source/concepts/physics-backends/newton.html)

这是公开软件与研究／工程开发工作流，设备依赖随后端、渲染和并行规模变化。版本、求解器及任务 preset 应随实验记录保存。项目需另交付 checkpoint、资产转换、关节顺序及目标控制接口，并在切换后端时验证语义和接触行为；公开后端代码不等于实机部署包，不替代现场标定、安全控制和系统集成。[跨后端验证入口](https://isaac-sim.github.io/IsaacLab/main/source/concepts/physics-backends/newton.html)

### LeRobot：示范采集、训练和策略运行的连接层

LeRobot 提供 Python 原生的机器人接口与示范学习工作流。前端通过受支持的机器人、遥操作器和相机采集同步视频、状态与动作，按 LeRobotDataset 组织；中间训练或微调策略，后端将策略接回机器人。官方流程明确区分 Teleoperate、Record、Train、Deploy，示范数据也可从 Hugging Face Hub 获取。没有实机时可处理已有数据或做文档列出的仿真评估，不能据此宣称已完成现场验证。[LeRobot 工作流](https://huggingface.co/docs/lerobot/main/index)

当前 `main` 文档要求从源码安装，并提示常规安装应对应稳定版本；不能把 `main` 的机器人、策略和命令列表全部倒填给旧包。访问日部署文档使用 `lerobot-rollout`，可选同步推理和异步动作 chunk，并可将运行数据记录为新 episode。训练产生的权重仍依赖观测字段、动作维度、归一化和时间对齐，换机器人通常还需要驱动与处理器适配。[版本边界](https://huggingface.co/docs/lerobot/main/index)、[部署接口](https://huggingface.co/docs/lerobot/inference)

实机流程需要硬件组装、校准、相机配置、设备连接，以及适合所选策略的计算资源。交付物是数据集、策略配置／checkpoint 和运行适配配置，而非包含全部机械、电气和安全责任的商品机器人系统；文档中的自主运行或人工接管策略不能代替风险评估、限位与独立停机措施。[运行与人工接管范围](https://huggingface.co/docs/lerobot/inference)

### W&B：实验记录、产物版本和协作管理

W&B 的实验管理层接收训练程序主动记录的配置、loss、任务指标、系统统计和产物，输出 run 页面、对比视图与可查询记录。它不决定机器人动作，也不把录入的“成功率”自动转成统一评估标准；任务定义、测试 episode 和失败分类仍需项目提供。SDK 可嵌入现有训练循环，不要求把训练算法改成某种特定机器人策略。[Experiments 接口](https://docs.wandb.ai/models/track)

Artifacts 将数据、checkpoint、评估表等作为有版本的输入输出，关联产生和使用它们的 run。由此可以追溯某个微调结果使用了哪版数据、哪项评估，但外部文件引用及实际保存内容要由团队约定，不能认为上传一个权重文件就包含全部环境与硬件配置。数据是否允许离开现场、视频和任务日志是否包含敏感信息，也需在上传前明确。[Artifacts 范围](https://docs.wandb.ai/models/artifacts)

当前官方托管文档列出 Forge、Dedicated Cloud 和 Self-Managed：前两种由服务方管理基础设施，后一种由客户维护自己的实例。可通过 SDK 接入服务或企业部署；训练算力仍在训练执行端，平台部署另有存储、网络、权限与维护需求。商用服务的可取得性不等于机器人运行 SLA，W&B 不替代训练环境、策略推理服务器、产线监控或安全系统。[部署方式与责任](https://docs.wandb.ai/platform/hosting/hosting-options/)

### MLflow：可自建的 tracking 与模型登记层

MLflow Tracking 用 API 和 UI 记录参数、代码版本、指标与产物，将训练过程组织为 experiment 和 run；当前模型跟踪还可把 checkpoint 与指定数据集的评估关联。输入是训练程序记录的信息及模型文件，输出是可查询的实验和模型记录。它不负责生成示范、定义奖励，也不会从通用 autologging 自动理解机器人的任务成功条件。[Tracking 文档](https://mlflow.org/docs/latest/ml/tracking/)

部署可从本地记录扩展到独立 HTTP tracking server，后端数据库保存 run 元数据，artifact store 保存较大的权重、图片及数据文件。设备主要是服务端计算、数据库、存储与网络；真正训练所需 GPU 仍由训练程序提供。自建不是零运维：备份、认证、访问控制及大文件路径需要配置，托管服务的治理能力也不能无条件归到所有 OSS 安装上。[服务与存储结构](https://mlflow.org/docs/latest/ml/tracking/)

Model Registry 维护模型版本、来源 run、标签和 alias，可让应用引用某个版本或可移动的发布别名。开放实现和托管版本的权限能力要分别核对。项目交付时应把登记的版本、实际权重和测试条件绑定；切换 alias 只是软件引用的切换，不是现场换模型的安全审批。它不替代机器人驱动、实时动作队列、硬件验收或闭环可执行性检查。[Registry 与 alias](https://mlflow.org/docs/latest/model-registry/)

### 同类别对照：训练执行与实验管理分开比较

| 训练实现／工作流 | 输入责任 | 输出责任 | 公开获取与边界 |
|---|---|---|---|
| PyTorch | 项目提供样本、模型和损失 | 参数更新与序列化模型 | [通用组件](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)；不包含机器人方案 |
| Isaac Lab | 资产、场景、任务与后端配置 | 环境交互和训练接口 | [多后端开发工作流](https://isaac-sim.github.io/IsaacLab/main/source/concepts/physics_backends.html)；任务兼容范围分别核对 |
| LeRobot | 机器人驱动、同步示范及策略配置 | 数据集、训练策略与 rollout | [公开机器人工作流](https://huggingface.co/docs/lerobot/main/index)；稳定包与 main 不混用 |

| 实验管理产品 | 记录／版本对象 | 部署责任 | 不负责的层 |
|---|---|---|---|
| W&B | run、数据和模型 Artifacts | [托管、专用云、自管理](https://docs.wandb.ai/platform/hosting/hosting-options/) | [训练算法与机器人实时控制](https://docs.wandb.ai/models/track)不由实验平台代办 |
| MLflow | run、logged model、Registry version／alias | [本地或 tracking server](https://mlflow.org/docs/latest/ml/tracking/)，托管治理另外核对 | [模型登记](https://mlflow.org/docs/latest/model-registry/)不等于现场认证 |

前一表比较责任位置，不表示三者可直接互换；后一表才是实验管理层的同类对照。两类可组合，不需要为了记录实验替换全部训练代码。

### 算法与物理引擎补充

RSL-RL 是公开的机器人学习算法库，当前主仓库列出 PPO、student-teacher distillation 和多 GPU 支持，额外算法另在 extras 分支；它需要连接环境，不自行提供全部物理资产。[RSL-RL 官方仓库](https://github.com/leggedrobotics/rsl_rl)

Brax 的当前 README 明确自 0.13.0 起仅 `brax/training` 处于积极维护范围，环境与物理模拟指向 MuJoCo Playground、MJX 或 MuJoCo Warp。旧的“四条物理 pipeline”说明仍在页内，不能忽略维护警告，继续把它们统称当前完整支持。[Brax 状态说明](https://github.com/google/brax)

MJX 是通过 JAX／XLA 运行的 MuJoCo 物理实现，提供可批处理的模型与状态，不是动作基础模型，也不是实验管理 SaaS。它与 CPU MuJoCo 的 API 和功能并非完全等价；资产和接触配置应按功能表检查。[MJX 官方范围](https://mujoco.readthedocs.io/en/stable/mjx.html)

### 典型连接流程

下面是本手册的组合方式，不表示厂商提供了整条链的统一支持合同：

```text
示范路线：机器人／相机 → LeRobot 数据与适配 → 策略训练／微调 → checkpoint
仿真路线：资产／任务 → Isaac Lab 指定后端 → RSL-RL 等算法 → checkpoint
共同旁路：训练与评估程序 → W&B 或 MLflow → 数据／run／模型版本关系
交接：checkpoint + 归一化 + 接口配置 + 评估记录 → 模型与部署团队
```

数据流程见 [LeRobot](https://huggingface.co/docs/lerobot/main/index)，环境与算法边界见 [Isaac Lab](https://isaac-sim.github.io/IsaacLab/main/source/concepts/physics_backends.html)、[RSL-RL](https://github.com/leggedrobotics/rsl_rl)，记录对象见 [W&B Artifacts](https://docs.wandb.ai/models/artifacts)、[MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/)。上图不省略交接包，也不把训练完成当作可直接开启实机自主运行的授权。

### 本章一手来源

- [PyTorch 基础教程](https://docs.pytorch.org/tutorials/beginner/basics/intro.html)、[分布式文档](https://docs.pytorch.org/docs/2.14/distributed.html)：组件与执行接口。
- [Isaac Lab 后端文档](https://isaac-sim.github.io/IsaacLab/main/source/concepts/physics_backends.html)、[Newton 文档](https://isaac-sim.github.io/IsaacLab/main/source/concepts/physics-backends/newton.html)：访问日 main 的公开范围。
- [LeRobot main](https://huggingface.co/docs/lerobot/main/index)、[rollout 文档](https://huggingface.co/docs/lerobot/inference)：版本边界、采训部署接口。
- [W&B Experiments](https://docs.wandb.ai/models/track)、[Artifacts](https://docs.wandb.ai/models/artifacts)、[部署选项](https://docs.wandb.ai/platform/hosting/hosting-options/)：官方产品责任。
- [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/)、[Model Registry](https://mlflow.org/docs/latest/model-registry/)：公开接口与部署／治理边界。
- [RSL-RL](https://github.com/leggedrobotics/rsl_rl)、[Brax](https://github.com/google/brax)、[MJX](https://mujoco.readthedocs.io/en/stable/mjx.html)：补充组件及维护／兼容限制。
