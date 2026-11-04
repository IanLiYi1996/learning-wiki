# OpenMOSS 学习路线：先选问题，再读方法

资料核查：2026-10-17。Wiki 整理：2026-11-04。[专题首页](README.md) · [来源与版本](sources.md)。

这不是十四篇文章的强制顺序。先确定想理解的接口或训练问题，再读相关章节；不熟悉的基础概念可以回到已有读本，不必在每个项目里重新学一遍。

## 1. 最少需要哪些基础

能读懂概率条件、向量和矩阵维度，以及“编码器产生表示、模型预测输出、损失更新参数”这条关系，就能开始。涉及公式的章节可以先读背景与实验，再回查推导。

| 阅读对象 | 需要的基础 | 可先补的 Wiki 内容 |
| --- | --- | --- |
| 基础模型、音频与视觉 | token、编码器、注意力、监督微调 | [训练配方导读](../training/README.md)、[视觉表征导读](../vision/README.md) |
| 潜表示与生成 | 压缩、重建、噪声、条件生成 | [扩散读本](../diffusion/README.md) |
| 长上下文与实时视频 | RoPE、KV cache、内存与可见性 | [GPU 与内存](../diffusion/05-gpu-and-memory-roofline.md)、[视频成本](../diffusion/06-realtime-video-estimates.md) |
| 强化学习与 Agent | 轨迹、奖励、优势、概率比 | [Agentic-RL 优化目标](../training/agentic-rl-lab/policy-objectives.md) |
| 机器人与世界模型 | 观测、状态、动作、反馈、控制 | [Physical AI 原理入口](../../physical-ai/advanced/README.md) |
| 可解释性 | 激活、权重、低秩与因果干预 | [深度学习术语](../glossary.md)、[权重空间编程](../weight-space-programming.md) |

## 2. 四条按问题组织的路线

### 路线一：模型怎样听、看和生成

从 [MOSS 与 AnyGPT](09-foundation-and-omni-models.md)理解接口统一，再选[语音生成](01-audio-representation-and-generation.md)或[音频理解](10-audio-understanding-and-transcription.md)。之后读[视觉与视频](02-streaming-video-time-and-cache.md)，最后对照[视听生成](03-audiovisual-latents-and-joint-denoising.md)和[文字布局生成](04-image-layout-supervision-and-specification.md)。

读完应能回答：哪些信息由 tokenizer 保留，哪些由后端模型补出？语义一致、波形保真和时间同步为什么不是同一个目标？

### 路线二：长输入、并行生成和训练更新

先读[长上下文与注意力](07-long-context-and-diffusion-optimization.md)，再读[扩散语言模型](13-diffusion-language-models.md)，最后读[DiPO／BandPO 后训练](14-post-training-and-rl.md)。

这里需要分开的三件事是：远处证据是否被使用、旧状态是否适合复用、训练的概率是否对应真实生成事件。找到一个答案 token，不等于理解了关联；重复使用缓存，也不等于重现原分布。

### 路线三：理解意图之后，怎样真正做成任务

先读[RoboOmni 与 FRoM-W1](11-robotics-policy-and-control.md)，弄清动作输出和低层控制；再读[世界建模与具身规划](05-world-action-and-embodied-agent.md)，区分训练辅助预测、候选动作规划与执行反馈。用[数字 Agent](06-agent-memory-and-executable-evaluation.md)对照记忆、部署和最终产物的验收。

读到 Planner-R1 时再查[强化学习篇](14-post-training-and-rl.md)。它的文字环境反馈不能直接代替机器人视觉定位、接触控制或实机验证。

### 路线四：怎样知道模型的答案和解释可信

先读[诚实性与安全](12-honesty-and-long-context-safety.md)，再读[机制可解释性](08-mechanistic-interpretability.md)。前者测回答行为，后者研究内部表示和计算；两者的得分与干预不能互相替代。

试着解释：更高的拒答总分为什么可能伴随更低覆盖率？一个特征有清晰标签，为什么仍不足以证明它是某次回答的原因？

## 3. 阅读时留下哪几项记录

每读一项方法，只记录它的输入、输出、训练信号、推理时可见信息和评价指标。若源码与论文有差异，再补上所用版本与差异位置。这样能比较方法，而不会把整个仓库 README 当作一个共同训练配方。

原稿里已有可手算的例子：视觉 KV 内存、十次采样的标签概率、逐 token 与联合概率比，以及缓存过期的反例。它们用于检查定义，不是模型复现。真正的模型或机器人实验需要另行确定数据、预算、硬件和停止条件。
