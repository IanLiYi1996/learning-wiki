# OpenMOSS：研究路线与技术机制

资料核查：2026-10-17。Wiki 整理：2026-11-04。[深度学习总入口](../README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)。

这组读本以 OpenMOSS 的项目和论文为案例，学习多模态模型怎样表示信息、怎样训练，以及怎样把生成接到互动和行动。读完应能分清：统一接口与统一架构、预测后果与选择动作、测试得分与实际任务完成。

材料按 11 条研究方向组织，保留 14 篇技术深解。每篇先交代背景和出发点，再分析方法、实现与证据。这里不是团队的官方组织图，也不是模型排行榜；研究分类与具体项目保持两层。

## 1. 按研究问题选择章节

| 研究方向 | 背景与出发点 | 深入阅读 |
| --- | --- | --- |
| 基础语言模型与统一多模态 | 预训练能力怎样变成对话、工具使用与跨模态输入输出？ | [MOSS 与 AnyGPT：对话监督、插件协议和离散接口](09-foundation-and-omni-models.md) |
| 语音生成与交互 | 内容、声线和说话人需要不同信息；质量与延迟怎样取舍？ | [语音表示、MOSS-Speech、CAT、TTS 与 TTSD](01-audio-representation-and-generation.md) |
| 音频理解与结构化转写 | 转写文字为什么不能代替声音、音乐和说话人理解？ | [MOSS-Audio、MTD 与 MOSS-Music](10-audio-understanding-and-transcription.md) |
| 视觉与视频理解 | 离线感知怎样扩展到持续输入，模型何时应该发言？ | [MOSS-Video-Preview 与 MOSS-VL](02-streaming-video-time-and-cache.md) |
| 多模态生成 | 语义相关不保证音画同步，设计要求也不保证像素中的文字和布局正确。 | [OmniVAE／MOVA：表示对齐与联合去噪](03-audiovisual-latents-and-joint-denoising.md)；[MOSS-Image：文字、布局和规格执行](04-image-layout-supervision-and-specification.md) |
| 具身智能 | 理解意图、生成动作、预测后果和确认结果，各需要什么？ | [RoboOmni／FRoM-W1：策略与全身控制](11-robotics-policy-and-control.md)；[D2PO／WAP／EasyWAM／ETA：建模、规划和验证](05-world-action-and-embodied-agent.md) |
| 工具使用与数字 Agent | 会写调用、会用历史经验，与完成工作之间还差什么？ | [工具训练、记忆、执行评价与实验决策](06-agent-memory-and-executable-evaluation.md) |
| 模型架构与生成范式 | 能放入长输入不等于能用好证据，并行生成也不自动省计算。 | [ReAttention／RoPE++／LongLLaDA：长度、位置和检索](07-long-context-and-diffusion-optimization.md)；[Sparse-dLLM：遮盖生成与缓存近似](13-diffusion-language-models.md) |
| 后训练与强化学习 | 任务反馈怎样更新模型，训练概率是否对应生成过程？ | [DiRL／DiPO、BandPO 与 Planner-R1](14-post-training-and-rl.md) |
| 诚实性与安全对齐 | 事实错误、不知道答案和不应回答，为什么需要分别研究？ | [HalluQA、Idk 与 LongSafety](12-honesty-and-long-context-safety.md) |
| 机制可解释性 | 能解释一个特征，是否已经解释了模型怎样计算？ | [Llama Scope、Lorsa 与 CRM](08-mechanistic-interpretability.md) |

先修知识和按问题组合的阅读顺序见[学习路线](learning-roadmap.md)。不需要先把十四篇全部读完，再开始某一个方向。

## 2. 怎样理解“OpenMOSS 路线”

早期 MOSS 将语言能力接到对话和工具协议，AnyGPT 用离散序列连接多种模态。后来的视频、音频和生成工作则分别处理持续输入、声学细节、物理时间和连续潜表示。共同问题有延续，具体骨干和权重不必延续。[MOSS／AnyGPT](09-foundation-and-omni-models.md) · [视频理解](02-streaming-video-time-and-cache.md) · [音频理解](10-audio-understanding-and-transcription.md)。

因此，不将这一组项目归纳成“所有模态都塞进同一个 LLM”，也不把同一组织下的模型视为已经集成的系统。MOSS-Image 是生成方向的案例，CoLLiE 是训练基础设施，VLABench 等是评价支撑；它们不与整个研究方向并列。

D2PO 和 World-Aware-Planning 虽在组织外的仓库，但由[团队公开研究总览](https://github.com/sii-research/OpenMOSS/blob/14d3cf31265a5d3de9dea89a1d0857ea3d976579/README.md)列入，因此纳入分析。其余共同作者的工作不自动扩大为团队成果。

## 3. 和已有 Wiki 对读

| 本专题的问题 | 先补或继续读 | 对读时注意 |
| --- | --- | --- |
| SFT、概率比、组内优势和奖励 | [训练配方](../training/README.md)、[Agentic-RL 优化目标](../training/agentic-rl-lab/policy-objectives.md) | DiPO 的生成步和 Agent 的环境交互步不是同一种步 |
| 连续潜变量和去噪训练 | [扩散与视觉生成](../diffusion/README.md) | 音画连续扩散与遮盖式语言生成不能互换采样器 |
| 表示、输入接口和语义对齐 | [视觉表征与多模态](../vision/README.md) | 检索向量、可重建音频码和生成条件承担不同职责 |
| 缓存、内存与实时成本 | [GPU／内存](../diffusion/05-gpu-and-memory-roofline.md)、[视频成本估算](../diffusion/06-realtime-video-estimates.md) | 每秒 token、首响应和端到端提醒延迟分别计算 |
| 世界模型、动作和控制 | [Physical AI 原理](../../physical-ai/advanced/README.md)、[Pollen 数据与策略](../../physical-ai/pollen-robotics/data-and-policy-learning.md) | 模型输出、执行接口和物体实际状态需要分别验收 |
| 解释权重与验证机制 | [权重空间编程](../weight-space-programming.md) | 可读的解释、计算替换和因果干预是不同证据 |

## 4. 阅读与更新约定

论文成绩归属于作者；文中的代数推导、计算例和反例属于分析，不是独立模型实验。2026-11-04 完成的是 Wiki 迁移、链接和阅读结构整理，没有把原资料重新核验到这一天。

本专题保留原论文版本和固定源码链接。后续补充应记录新的核查日期，说明改了哪篇论文、配置或结论，不静默覆盖原来的测量口径。具体出处、快照登记和未执行项见[来源页](sources.md)。
