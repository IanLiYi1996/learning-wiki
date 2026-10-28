# GTC Berlin 2026：机器人软件栈交付边界

核查截止：2026-10-26。仅讨论机器人与人形机器人，不展开 Cosmos。引用编号对应文末完整标题、日期、canonical URL 和 web 来源 ID。状态依据新闻原文、公开仓库、模型卡及发布页分别判断；未安装软件、下载完整权重或执行机器人测试。

## 一、版本名称不能直接变成交付结论

10月21日有效主新闻稿写的是 **Isaac GR00T 1.7**，并将 Isaac OS 和开放数据列入机器人开发栈；它没有写“Isaac OS 0.8”。新闻所称可用性不能代替版本包核验。[S1] GR00T 官方仓库和模型卡则具体命名 **GR00T N1.7 / GR00T-N1.7-3B**。两者可关联，但引用新闻时应保留新闻自己的名称。[S2–S3]

尤其存在资料不同步：仓库 README 称 N1.7 GA，模型卡仍称 Early Access；模型文件索引可见两份 safetensors 权重分片，却不是本研究实际下载成功的证明。[S2–S4] 因此可写“宣布/仓库标记可用，存在公开权重入口”，不可写“已实测下载和部署”。开发者博客也已描述 N1.7，但页面标注7月7日、结构化修改日期8月6日，与大会更新时间关系不明，不能据此认定整个型号于大会首次发布。[S5]

## 二、GR00T：机制、许可证与硬件限制

模型卡将其定义为约30亿参数的开放权重视觉—语言—动作模型：视觉语言骨干结合动作生成头，输入相机图像、机器人状态与语言指令，输出动作序列；EgoScale 用人体第一视角数据帮助跨机器人形态泛化。这不等于开箱即用的通用人形控制系统，具体机器人仍需要数据适配、后训练与控制接口。[S3,S5]

官方仓库给出推理至少16GB GPU显存、微调至少40GB显存的要求；只能用于这些示例工作流的硬件边界，不能推广为所有机器人任务的最低配置。[S2] 许可证也不宜合并：代码为 Apache 2.0，权重模型卡明确列 NVIDIA Open Model License；应以目标代码或权重自身许可证为准，不能把代码许可覆盖到模型权重。这是分层许可，不应称为已证实的许可证资料不同步。[S2–S3] 模型卡没有提供可据此断言整机功能安全认证或量产任务可靠性的材料。[S3]

## 三、Capture：有公开产物，不能杜撰独立 GA 版本

官方 keynote 页面把 Isaac Capture 列为人类示范采集组件；开发页介绍消费级设备、VR头显和智能眼镜等采集方式。[S6,S16] 官方开发页与源码库确有公开入口；源码支持设备抽象、遥操作、动作重定向、MCAP记录/回放、第一视角手部重建，以及向 LeRobot 工作流输出数据。因此不能仅称“概念宣布”。[S6–S7]

但公开仓库沿用 Isaac Teleop 的发布脉络：可见10月14日 **v1.5.175** 发布，早于大会。该日期只能证明相应 Teleop 产物存在，不证明某个独立编号的 Capture GA 已交付。[S8] 根 LICENSE.md 是 Apache 2.0；README 另将手部重建等模型产物列为 OpenMDW-1.1，不能把后一许可写成整个源码库的许可。[S9,S17] 对设备支持还应区分已实现适配器与新闻举例；未验证任意智能眼镜均可直接接入。

## 四、Lab 与 OS：宣布状态和公开版本分开写

主新闻稿把 **Isaac Lab 3.0** 写为 GA，并强调可由智能体辅助构建环境、训练和评估策略。[S1] 但检查公开 GitHub releases 时，仍见 **v3.0.0-EA**；GitHub API 给出其 UTC 发布时间为9月16日，找不到同等明确的最终 GA 标签。[S10,S18] 应标“新闻称 GA，公开发行资料未同步”，不要将早期访问包包装成已核实最终版。Lab 延续已有机器人仿真学习框架，本次不是从零推出 Isaac Lab；仓库许可为 BSD-3-Clause。[S10–S11]

Isaac OS 是本次新宣布的开放机器人运行时框架，基于 Holoscan，把感知、运动控制和推理等软件组件接入实时机器人执行链。[S1] 新闻并未给出版本号、GA声明、完整下载入口或逐板卡支持矩阵；因此不写0.8、不认定它是替换 Linux 的通用操作系统，也不把“开放框架”自动等同所有依赖均开源。Jetson Thor 在相关新闻中的作用主要是参考人形机器人计算平台，而非已核实的 OS 唯一支持硬件。[S1,S13]

## 五、开放数据必须注明访问层级

新闻推出人类及机器人数据、物理对象模型与合成数据，并明确 **完整 Human 1M Dataset 仅向 Cosmos Coalition partners 开放**，不是 Physical AI Open Dataset Coalition。原文定位片段为：“with the full Human 1M Dataset accessible to Cosmos Coalition partners.”[S1] “开放 Physical AI 数据”不等于公众可无条件下载完整 Human1M。本轮未获得可独立验证的 Human1M 完整数据卡、许可、文件列表和采集规模，不能把名称推成100万小时、100万人或100万条轨迹。

相对可核验的另一产物是10月21日发布的 **SimReady Central**：聚合面向机器人及AI工厂的物理仿真资产，使用 OpenUSD 等格式，包含质量、材料、碰撞等仿真属性。这是仿真资产库，不是人类示范数据集；不同资产许可仍应逐项核对。[S12] 已有 PhysicalAI collection 与本次新增资产也不能混为同一天首次开放的单一数据集。

## 六、机器人和伙伴：演示不是部署

Agile 官方将 **Agile ONE SN** 定位为参考人形平台，结合 Jetson Thor 和 NVIDIA 机器人软件；处于早期访问，计划 **2027年初交付**。本次发布不等于10月已向普通客户批量交付，亦不能据此替其他人形机器人承诺可迁移性。[S13] Microduck 开发博客展示智能体辅助在 Isaac Lab 中构建并训练行走任务，验证的是开发流程/仿真演示，不能写成生产现场自主运行的证明。[S14]

伙伴应按证据强弱表述：Agility 在新闻中对应 Halos 安全集成，KUKA 对应通过 Visual Components 的 FactoryLens 使用工业数字孪生；均不证明部署本次全部栈。[S1] Figure 在 keynote 页面出现，但同样不能从标识推成软件版本部署证据。[S16] NEURA 的 Neuron AI 公告日期为10月14日，是大会前的伙伴模型发布，不能改写成大会首发或统一切换至 GR00T。[S15] Schneider 的本次机器人技术部署尚未取得可用一手出处，不作具体工厂规模上线推断。最可证实的进展是开发、数据和运行时链路的连接，量产部署及可靠性仍需独立证据。

## 来源表

无明确发布日期的动态页面统一标“页面未标日期；查阅2026-10-26”，不将查阅日当发布日。来源 ID 保留供主代理引用；URL 以实际成功读取的官方页面为准。

|编号|完整标题／日期|canonical URL|web 来源 ID|
|---|---|---|---|
|S1|NVIDIA Advances Isaac Platform for General-Purpose Robotics With New Reference Humanoid, Frameworks, Simulation Pipelines and Data／2026-10-21|https://nvidianews.nvidia.com/news/nvidia-advances-isaac-platform-for-general-purpose-robotics-with-new-reference-humanoid-frameworks-simulation-pipelines-and-data|turn1view0|
|S2|NVIDIA/Isaac-GR00T — README／页面未标日期；查阅2026-10-26|https://github.com/NVIDIA/Isaac-GR00T|turn1view1|
|S3|nvidia/GR00T-N1.7-3B — Model Card／页面未标日期；查阅2026-10-26|https://huggingface.co/nvidia/GR00T-N1.7-3B|turn1view2|
|S4|nvidia/GR00T-N1.7-3B — Files and versions／页面未标日期；查阅2026-10-26|https://huggingface.co/nvidia/GR00T-N1.7-3B/tree/main|turn1view3|
|S5|Develop Humanoid Robot Policies End-to-End with NVIDIA Isaac GR00T／页面标2026-07-07；HTML结构化修改日期2026-08-06|https://developer.nvidia.com/blog/develop-humanoid-robot-policies-end-to-end-with-nvidia-isaac-gr00t/|turn1view4|
|S6|Isaac Capture／页面未标日期；查阅2026-10-26|https://developer.nvidia.com/isaac/capture|turn2view0|
|S7|NVIDIA/IsaacCapture — README／页面未标日期；查阅2026-10-26|https://github.com/NVIDIA/IsaacCapture|turn2view1|
|S8|Release v1.5.175 — NVIDIA/IsaacCapture／2026-10-14|https://github.com/NVIDIA/IsaacCapture/releases/tag/v1.5.175|turn2view2|
|S9|NVIDIA/IsaacCapture — LICENSE.md／页面未标日期；查阅2026-10-26|https://raw.githubusercontent.com/NVIDIA/IsaacCapture/main/LICENSE.md|turn4view0|
|S10|Release v3.0.0-EA — isaac-sim/IsaacLab／API日期2026-09-16 UTC；网页摘要显示9月15日|https://github.com/isaac-sim/IsaacLab/releases/tag/v3.0.0-EA|turn2view4|
|S11|isaac-sim/IsaacLab — LICENSE／页面未标日期；查阅2026-10-26|https://github.com/isaac-sim/IsaacLab/blob/main/LICENSE|turn2view5|
|S12|Announcing SimReady Central: An Open Library of Simulation-Ready 3D Assets for Robotics and AI Factories／2026-10-21|https://huggingface.co/blog/nvidia/simready-central-assets-robotics-ai-factories|turn3view0|
|S13|Agile Robots launches Agile ONE SN／2026-10-21|https://www.agile-robots.com/en/news/detail/agile-robots-launches-agile-one-sn/|turn3view1|
|S14|Using AI Agents to Teach Robots Like Microduck to Walk in Simulation／2026-10-23|https://developer.nvidia.com/blog/using-ai-agents-to-teach-robots-like-microduck-to-walk-in-simulation/|turn0view0|
|S15|NEURA Robotics introduces Neuron AI／2026-10-14|https://neura-robotics.com/neura-robotics-introduces-neuron-ai/|turn0view1|
|S16|GTC Berlin Keynote／页面未标发布日期；活动日期2026-10-21|https://www.nvidia.com/gtc/keynote/|turn4view3|
|S17|NVIDIA/IsaacCapture — README.md 原始文件／页面未标日期；查阅2026-10-26|https://raw.githubusercontent.com/NVIDIA/IsaacCapture/main/README.md|turn4view1|
|S18|GitHub API — IsaacLab v3.0.0-EA release／published_at：2026-09-16T22:34:03Z；用curl复核|https://api.github.com/repos/isaac-sim/IsaacLab/releases/tags/v3.0.0-EA|本轮终端读取，无web ID|

### 未核实与排除

未核实：最终 Lab 3.0 GA 包、独立 Capture GA 编号、Isaac OS 版本/下载/许可和硬件矩阵、Human1M 完整模型卡与许可、伙伴本次栈的量产部署。以上“未核实”不等于确认不存在。主代理提及的 Cosmos framework README 集成 N1.7，可作为后续交叉线索；本轮对其 GitHub URL 的读取失败，未把这一转述当独立证据。错误入口 `https://nvidianews.nvidia.com/news/nvidia-unveils-full-stack-robotics-platform-at-gtc-berlin` 已排除，不引用其摘要。
