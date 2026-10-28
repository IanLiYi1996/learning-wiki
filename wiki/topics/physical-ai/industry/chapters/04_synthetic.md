## 04 合成数据与示范扩增

### 阶段工作与交付物

这个阶段补充稀缺任务、场景与外观条件，交付物可以是带几何真值的感知数据、仿真执行过的机器人示范，也可以是待审核的生成视频及文本标签。三者必须分别登记来源、生成配置、版本、质量检查和使用权限。图像、分割标签、动作命令与“任务成功”判断不是同一种监督；不能把生成得自然的视频直接写进动作字段。

下面按 **2026-10-27** 一手页面的实际状态介绍产品。Replicator 属于场景驱动的数据生成组件，Mimic 属于示范轨迹扩增流程，Cosmos 属于模型与工具家族。当前 Cosmos 已转向 Cosmos 3；Predict2.5、Transfer2.5、Reason2 的代码仍可查，但官方均标明有限维护。这里分别介绍其接口用途，不把旧分支称为当前主线，也不根据演示视频宣布客户量产。[当前 Cosmos 入口](https://github.com/NVIDIA/cosmos)、[旧分支状态](https://github.com/nvidia-cosmos/cosmos-transfer2.5)

### Omniverse Replicator：场景与标签驱动的感知数据生成

Replicator 用于定制合成数据流水线，输入是 USD 场景、物体语义、相机、材质和随机化规则，输出是渲染图像及启用的深度、分割、检测框等注释。接入方式是在 Kit／Isaac Sim 中使用扩展和 Python API，定义生成触发、annotator 和 writer，再把输出接入已有训练目录；writer 决定实际文件和元数据形式，不存在一个对所有任务适用的默认数据集。[Replicator 职责](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator.html)、[Python API](https://docs.omniverse.nvidia.com/kit/docs/omni_replicator/latest/source/extensions/omni.replicator.core/docs/API.html)

官方公开文档、API 和脚本示例，说明它不是只有宣传视频的概念；获取通常随所使用的 Omniverse／Isaac Sim 运行环境，而非一个与环境无关的独立云标注账号。交付应同时保留语义映射和生成配置，便于复核与重建。环境、依赖、资产和再分发授权需要分开核对，本次不执行下载安装。

Isaac Sim 的固定版本教程列出物体、场景、AMR 导航和 UR10 码垛随机化工作流，是可查的官方应用示例，不是某个客户的生产效果披露。[6.0.0 工作流](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/replicator_tutorials/index.html) 注释正确性依赖场景语义与配置；渲染几何真值不自动变成现实准确标签，感知输出也不自动带机器人动作监督。

### Isaac Lab Mimic：从机器人示范扩增可执行轨迹

Mimic 接收少量机器人示范、对象位姿、子任务边界和兼容环境配置，生成经过环境执行与成功判定筛选的新示范。它以对象相关的子任务变换和轨迹拼接扩展示范，交付包含观测与动作的 HDF5 记录；与仅改变图像外观不同，动作来自明确的机器人控制接口。[固定 v2.2.0 文档](https://isaac-sim.github.io/IsaacLab/v2.2.0/source/overview/teleop_imitation.html)

接入已有 Isaac Lab 环境时，需要实现末端位姿读取、目标位姿到动作、动作到目标位姿、夹爪动作、对象位姿及子任务信号等 helpers。这里的函数约定决定轨迹能否执行，不能把任意人的手部视频直接塞入生成器。获取形式是 Isaac Lab 开源工作流及脚本，运行在相容的仿真与计算环境中；本章固定版本用于核验，不称其为最新发行。

官方堆叠和倒料教程提供采集、标注、生成及训练示例，证据类型是可执行开发／研究示范，未被当作某个客户的量产案例。文档也明确提醒非确定性回放：生成时通过不代表每次重播均通过。成功判据、子任务切分和对象变化决定覆盖范围，扩增数据还需与源示范共同分组划分，不能跨训练与测试泄漏。[生成与限制](https://isaac-sim.github.io/IsaacLab/v2.2.0/source/overview/teleop_imitation.html#common-pitfalls-when-generating-data)

### Cosmos 3：当前统一家族，按任务选择生成或推理接口

当前 Cosmos 官网与主仓库将 Cosmos 3 作为统一多模态家族。Reasoner 的接口以文本与视觉为输入、文本为输出；Generator 可使用文本、视觉、音频和动作条件，并按任务输出视觉、音频或动作。接入要选择相应 checkpoint 与 recipe，再将生成结果或推理回答送入审核、数据处理或指定策略工作流；不能因为家族支持动作就认为任意视频模型会输出关节命令。[当前主仓库](https://github.com/NVIDIA/cosmos)

官方提供模型集合、推理／后训练配方和浏览器试用入口，属于公开可访问的模型与代码生态；某些依赖仍要求接受访问条件，不能将“公开入口”写成无条件商用授权。部署形式包括 GPU 推理、后训练及服务化，具体模型的输入、输出和资源要求按对应说明核对。[产品入口](https://www.nvidia.com/en-us/ai/cosmos/)

仓库展示场景转换、动作条件预测和机器人操作演示，证明存在参考模型与接口示例，不是具名客户的规模生产证据。本次不采用产品页排名或“物理一致”的营销表述作为验收结论。输出动作需要机器人形态、动作空间、数据和控制适配；普通生成视频仍只有生成画面，不能冒充实测状态和执行命令。

### Cosmos Predict2.5：视频世界预测分支与专用动作条件配方

Predict2.5 的常见用途是依据文本或视觉条件预测／生成后续视频，输入通过推理配置进入模型，输出为视频片段，可用于候选场景扩充和视觉训练素材。接入现有数据流程时应保留输入片段、条件、生成版本和审核结果，再与真实数据分开管理。它不是给仿真器提供精确接触力的动力学库，也不直接替代 USD 场景。[Predict2.5 仓库](https://github.com/nvidia-cosmos/cosmos-predict2.5)

公开代码仍列有推理、后训练及模型获取入口，但仓库顶部已标注不再积极开发、仅有限维护，当前主线转向 Cosmos 3。获取形式是代码、模型和 GPU 工作流，而非随手下载即可兼容任意机器人的成品控制系统。

本分支还提供动作条件视频预测及专用 policy 配方。动作条件文档明确需要配对机器人状态与动作作为输入条件：它是“已有动作预测画面”，不是从普通画面自动发现真实命令。[动作条件接口](https://github.com/nvidia-cosmos/cosmos-predict2.5/blob/main/docs/post-training_video2world_action.md) 官方研究配方与模型发布可证明这些特定能力可查，不能证明任一客户量产；不同任务 checkpoint 的输出也不可混称为同一动作接口。

### Cosmos Transfer2.5：以空间条件控制视频外观

Transfer2.5 面向条件控制的世界视频生成：输入可以包括已有视频、提示词和深度、边缘、分割、模糊图等空间控制，输出是按条件生成的视觉片段。接入时可由仿真导出控制视频，再在参数文件中指定各控制通道、权重和输出目录；官方示例也提供从输入画面计算部分控制的路径。它增加外观变化，不负责替物理引擎计算机器人轨迹。[推理输入与配置](https://github.com/nvidia-cosmos/cosmos-transfer2.5/blob/main/docs/inference.md)

获取是公开仓库、模型入口和 GPU 推理／后训练流程；当前该版本已转入有限维护，不能把它写成仍在持续扩展的独立主线产品。示例中的 robot depth、edge、segmentation 和 multi-control 参数文件构成可检查的参考应用，不等于客户自动驾驶或操作任务已量产。[状态与示例](https://github.com/nvidia-cosmos/cosmos-transfer2.5)

接口边界在标签继承：条件画面与输出相似，不保证所有对象轮廓、遮挡和细节严格保留。若生成器移动、增添或删除了物体，原检测框和分割标签须重新核验；原动作也只有在时间、几何及控制语义保持时才可作为关联信息，不能因为视觉“更真实”而自动视为新动作真值。

### Cosmos Reason2：审核与解释辅助，不是视频生成器

Reason2 是可定制的视觉语言推理模型，输入是图像／视频和提示，输出是文本回答及任务所约定的描述。它可嵌入候选片段审核、事件描述或标签建议流程：应用构建提示及结果 schema，接本地批处理或模型服务，再把回答与原视频、时间范围关联保存。它既不同于 Transfer 的条件视频生成，也不同于 Mimic 的机器人示范执行。[Reason2 接口](https://github.com/nvidia-cosmos/cosmos-reason2)

仓库公开模型入口、Transformers 推理及在线／离线部署说明，但当前顶部同样标注有限维护、后续主线转到 Cosmos 3。本次把这些可访问代码和样例记录为模型／研究生态证据，没有据宣传中的“理解物理”宣称输出可替代真实接触测试或人工质量审核。

具体接入时应把建议标签与人工确认标签分列，明确是否允许回答不确定、如何回溯证据、哪些样本需要复核。自然语言“拿起物体”不是关节、末端或力矩命令；文本判断的任务成功也不是机器人执行确认。即使服务返回可解析 JSON，字段完整仍不证明语义正确，模型回答不能自动成为原始数据真值。

### 同类对照与数据衔接

| 工具／分支 | 输入核心 | 输出核心 | 能否直接交付动作监督 | 本次证据状态 |
| --- | --- | --- | --- | --- |
| Replicator | 场景、语义、传感器与随机化 | 感知数据和选定注释 | 单靠图像生成不能；需另有控制记录 | 官方 API、运行环境及工作流 |
| Mimic | 机器人示范、对象、子任务与环境 | 执行及筛选后的示范 | 可在明确动作接口中生成，仍须审核 | 开源脚本、固定版本研究示例 |
| Cosmos 3 | 任务对应的多模态条件 | 文本或生成模态，含专用动作路径 | 取决于任务模型与机器人适配；视频本身不能 | 当前主线入口、模型及参考演示 |
| Predict2.5 | 文本／视觉，专用配方可加动作 | 视频；专用 policy 另行核对 | 普通视频不能，动作条件也不是新命令标签 | 公开旧分支，有限维护 |
| Transfer2.5 | 视频及空间控制 | 条件生成视频 | 不自动产生；继承标签须检查一致性 | 公开旧分支、输入参数示例 |
| Reason2 | 视频／图像及提示 | 文本与建议标签 | 不能直接输出已执行机器人动作记录 | 公开旧分支、推理与部署说明 |

本章原创衔接流程是：先确定要补的是感知标签、动作示范还是视觉条件，再生成；保留源数据到生成数据的关联，执行任务专属审核，最后发布独立版本的数据清单。若将仿真渲染送入 Transfer，或用 Reason 辅助筛选 Mimic 片段，必须把额外质量门作为项目实现，不能称为客户已经采用的默认组合。

### 实际读取的一手来源

- [Omniverse Replicator](https://docs.omniverse.nvidia.com/extensions/latest/ext_replicator.html)、[Python API](https://docs.omniverse.nvidia.com/kit/docs/omni_replicator/latest/source/extensions/omni.replicator.core/docs/API.html)：扩展、annotator、writer 与程序化生成。旧 API 链接发生跳转，本文使用实际读取的规范入口。
- [Isaac Sim 6.0.0 Perception Data Generation](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/replicator_tutorials/index.html)：官方场景、物体与随机化教程，不充当客户案例。
- [Isaac Lab Mimic v2.2.0](https://isaac-sim.github.io/IsaacLab/v2.2.0/source/overview/teleop_imitation.html)：示范、动作转换 helpers、成功筛选、HDF5 与非确定性回放。
- [NVIDIA Cosmos 官网](https://www.nvidia.com/en-us/ai/cosmos/)、[Cosmos 当前主仓库](https://github.com/NVIDIA/cosmos)：当前 Cosmos 3 定位、输入输出、模型入口及参考演示；未引用排名，也未读取或引用链接中的论文。
- [Predict2.5 README](https://github.com/nvidia-cosmos/cosmos-predict2.5)、[动作条件说明](https://github.com/nvidia-cosmos/cosmos-predict2.5/blob/main/docs/post-training_video2world_action.md)：有限维护与已有动作条件的区别。
- [Transfer2.5 README](https://github.com/nvidia-cosmos/cosmos-transfer2.5)、[inference](https://github.com/nvidia-cosmos/cosmos-transfer2.5/blob/main/docs/inference.md)：有限维护、输入模态与 JSON 参数。
- [Reason2 README](https://github.com/nvidia-cosmos/cosmos-reason2)：文本推理、在线／离线部署和有限维护标记。以上均于 2026-10-27 核验；没有下载模型、生成视频或执行平台安装。
