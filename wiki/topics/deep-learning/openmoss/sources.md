# OpenMOSS 来源、版本与核验边界

资料核查：2026-10-17。Wiki 整理：2026-11-04。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [机器可读来源登记](sources.json)。

本专题由既有项目／论文调研改编为学习读本。正文保留原来的论文版本、固定源码、作者实验和分析性反例；本轮只整理阅读结构与站内链接，没有重新检索团队在原核查日之后的全部工作。

## 1. 研究范围

范围依据 [OpenMOSS 组织目录](https://github.com/OpenMOSS)和[团队研究总览的固定版本](https://github.com/sii-research/OpenMOSS/blob/14d3cf31265a5d3de9dea89a1d0857ea3d976579/README.md)。覆盖公开主线及代表工作，不逐篇穷尽全部论文，也不从共同作者、相似名称或组织内的适配仓库推定原创归属。

D2PO、World-Aware-Planning 与音乐数据管线使用作者或团队链接的组织外仓库。LLaDA、Dream、SDAR、Qwen 和底层视听组件的外部来源保持原归属，不能算成 OpenMOSS 从头训练的所有基座。

## 2. 主要论文入口

同一行中的论文分别承担不同任务，不能将一个 paper ID 套给整个模型家族。精确章节、表格、代码路径和行号留在正文，不在本页重复实验分数。

| 学习问题 | 主要一手来源 | 对应解读 |
| --- | --- | --- |
| 基础模型与多模态接口 | [MOSS，MIR 2024](https://link.springer.com/article/10.1007/s11633-024-1502-8)；[AnyGPT，ACL 2024](https://aclanthology.org/2024.acl-long.521/)；[CoLLiE](https://arxiv.org/abs/2312.00407) | [基础模型篇](09-foundation-and-omni-models.md) |
| 语音交互 | [SpeechGPT](https://arxiv.org/abs/2305.11000)；[SpeechTokenizer](https://arxiv.org/abs/2308.16692)；[MOSS-Speech](https://arxiv.org/abs/2510.00499) | [语音篇](01-audio-representation-and-generation.md) |
| 音频表示与生成 | [MOSS-Audio-Tokenizer](https://arxiv.org/abs/2602.10934)；[MOSS-TTS](https://arxiv.org/abs/2603.18090)；[MOSS-TTSD](https://arxiv.org/abs/2603.19739) | [语音篇的表示与生成分析](01-audio-representation-and-generation.md) |
| 音频理解与转写 | [MOSS-Audio v3](https://arxiv.org/pdf/2606.01802v3)；[MTD v7](https://arxiv.org/pdf/2601.01554v7)；[MOSS-Music 固定说明](https://github.com/OpenMOSS/MOSS-Music/blob/ad107c7ddaa06de168a0dfbc18d3e1e6a40c0e5e/README.md) | [音频理解篇](10-audio-understanding-and-transcription.md) |
| 视频与实时互动 | [MOSS-Video-Preview](https://arxiv.org/abs/2606.07639)；[MOSS-VL v1](https://arxiv.org/html/2608.15045v1) | [视频篇](02-streaming-video-time-and-cache.md) |
| 音画生成与潜表示 | [OmniVAE](https://arxiv.org/abs/2607.23855)；[MOVA](https://arxiv.org/abs/2602.08794) | [视听生成篇](03-audiovisual-latents-and-joint-denoising.md) |
| 文字与布局生成 | [MOSS-Image 固定技术报告](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf) | [图像篇](04-image-layout-supervision-and-specification.md) |
| 机器人策略与控制 | [RoboOmni v3](https://arxiv.org/html/2510.23763v3)；[FRoM-W1 v1](https://arxiv.org/html/2601.12799v1)；[VLABench，ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/papers/Zhang_VLABench_A_Large-Scale_Benchmark_for_Language-Conditioned_Robotics_Manipulation_with_Long-Horizon_ICCV_2025_paper.pdf) | [机器人篇](11-robotics-policy-and-control.md) |
| 世界建模、规划和执行 | [D2PO v1](https://arxiv.org/html/2503.10480v1)；[WAP v1](https://arxiv.org/html/2506.21230v1)；[ETA v1](https://arxiv.org/html/2608.03924v1)；[EasyWAM 固定架构说明](https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/docs/blogs/blog01_arch_zh.md) | [具身规划篇](05-world-action-and-embodied-agent.md) |
| 记忆与实际工作评价 | [ContextWeave](https://arxiv.org/abs/2608.04830)；[ABC](https://arxiv.org/abs/2601.11077)；[SWE-bench Science](https://arxiv.org/abs/2608.19799)；[AgentHPOBench](https://arxiv.org/abs/2607.29626) | [数字 Agent 篇](06-agent-memory-and-executable-evaluation.md) |
| 长上下文与架构 | [ReAttention v3](https://arxiv.org/pdf/2407.15176v3)；[RoPE++ v1](https://arxiv.org/pdf/2512.07525v1)；[LongLLaDA v3](https://arxiv.org/pdf/2506.14429v3) | [长上下文篇](07-long-context-and-diffusion-optimization.md) |
| 扩散推理与后训练 | [Sparse-dLLM v2](https://arxiv.org/pdf/2508.02558v2)；[DiRL v2](https://arxiv.org/pdf/2512.22234v2)；[BandPO v1](https://arxiv.org/pdf/2603.04918v1)；[Planner-R1 v1](https://arxiv.org/html/2506.23127v1) | [扩散语言篇](13-diffusion-language-models.md)、[后训练篇](14-post-training-and-rl.md) |
| 事实、拒答与长输入安全 | [HalluQA v4](https://arxiv.org/pdf/2310.03368v4)；[Idk，ICML 2024](https://proceedings.mlr.press/v235/cheng24i.html)；[LongSafety，LLMSEC 2025](https://aclanthology.org/2025.llmsec-1.4/) | [诚实性与安全篇](12-honesty-and-long-context-safety.md) |
| 内部机制 | [Llamascopium 固定入口](https://github.com/OpenMOSS/Llamascopium/tree/544b2f93290a60cc5dbafb535565592b79a05141)；[CRM 作者报告](https://interp.open-moss.com/posts/complete-replacement) | [可解释性篇](08-mechanistic-interpretability.md) |

<a id="audio"></a>

## 3. 家族论文与来源空缺

MOSS-Music 没有在原核查范围内确认独立论文；其功能、数据管线和作者评测以固定仓库说明为依据。不将 MOSS-Audio 的预训练量或 RL 配置照搬给 Music。

EasyWAM 的分析主要依据软件、配置、源码与作者博客。WAM 综述提供分类背景，不是 EasyWAM 的方法论文。UnifiedToolHub 是工具数据与评测底座，原核查没有确认它的专属模型论文。CRM 的网页报告也不补写为不存在的 arXiv 文献。

语音家族中的 TTS、直接语音回答、转写和音乐理解具有不同输入输出；共享名称、帧率或组织归属不证明权重与表示相同。

## 4. 怎样回查源码版本

[来源登记](sources.json)保存 14 篇正文中使用的公开 GitHub／Hugging Face 快照入口及相关章节。正文保留具体文件链接；行号只适用于链接中的固定提交。独立出现的提交号采用短写，完整版本仍在公开来源链接里。

快照是材料的版本，不是独立复现证明。论文实验、发布配置与所读源码不能逐项对应时，正文已保留差异；不把今天的默认值反填为原论文的训练设置。实时服务、工具执行、训练代码和模型权重也分别评价。

## 5. 本轮做了什么，没做什么

本轮迁移技术文章、增加导读与交叉链接、适配公式和站内地址，并检查 Wiki 文档与构建。没有训练或运行这些模型，没有下载权重或训练数据，没有复跑模型排行榜、连接机器人或调用付费模型服务。

来源页登记的是原研究依据，不宣称全部来源在 2026-11-04 重新核验。将来更新一个结果，应同时记录论文版本、代码快照、指标、分母和预算；只替换一个排行榜数字不构成完整更新。
