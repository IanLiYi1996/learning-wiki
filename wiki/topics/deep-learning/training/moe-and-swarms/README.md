# MoE 与 Swarm：模型内稀疏计算，模型外集体协作

研究与来源核验日期：2026-11-09。[返回训练专题](../README.md) · [深度学习目录](../../README.md)。

本专题结合 Hugging Face 的 [The Ultimate MoE Training Handbook](https://huggingface.co/spaces/huggingface/moe-blogpost#s-1) 与 General Reasoning 的 [How to Train a Swarm](https://www.gr.inc/blog/how-to-train-a-swarm)，回答一个共同问题：把计算分给多个单元，怎样才能得到有效收益？

先保留最重要的区别：**MoE 是一个模型内部选择参数的架构；Swarm 是多个智能体围绕共享任务行动的系统。** Expert 不等于 Agent，模型架构也不等于强化学习算法。下面的联系是本 Wiki 的学习组织，不是两篇文章提出了一种统一算法。

## 先选一个问题

| 想弄清什么 | 阅读入口 | 看完应能解释什么 |
| --- | --- | --- |
| 参数很多，为什么一次前向只用一部分？ | [01 MoE 架构、负载与训练工程](moe-training.md) | Top-k、总参数／激活参数、平衡、容量、EP 与通信 |
| 多开几个智能体，为什么不自动形成协作？ | [02 Swarm 与 RLCR](swarm-rlcr.md) | 共享策略、集体奖励、截止时间、通信和信用分配 |
| 两篇材料可以怎样结合，又不能怎样类比？ | [03 跨层联系、成本与评测](connections-and-evaluation.md) | 模型内外两层计算、关键路径、预算对照与证据边界 |
| 数字、公式和版本来自哪里？ | [一手来源与核验记录](sources.md) | 原文定位、论文背景、作者报告与尚未复现的内容 |

## 两层分工，不是同一种“专家系统”

| 对照项 | MoE | Swarm／Agent collective |
| --- | --- | --- |
| 分工单元 | 神经网络里的 expert，常见为 FFN | 含上下文、工具接口与行动轨迹的 Agent |
| 输入 | 每一层的 token 隐藏状态 | 子任务、环境观察、同伴消息 |
| 分配机制 | Router 选择 expert | 调度器、组织协议或学到的委派行为 |
| 交换什么 | 激活张量与计算结果 | 自然语言消息、文件、工具结果和环境状态 |
| 学习信号 | 主任务损失，可能加路由正则 | 环境回报及集体策略更新 |
| 典型规模约束 | 显存、expert 粒度、互连与负载 | 延迟、通信、状态冲突、长程信用分配 |

MoE 的基础可对照 [Switch Transformers](https://arxiv.org/abs/2101.03961v3) 和 [DeepSeekMoE](https://arxiv.org/abs/2401.06066v1)；本专题的 Swarm 案例限定为 [Avalon-M1／RLCR 技术报告](https://gr.inc/avalonm1.pdf)，不将所有多智能体系统都归入同一训练方式。

一个 Swarm 可以调用 dense LLM，也可以调用 MoE LLM。如果使用后者，每个 Agent 的一次生成内部还要执行路由与 expert 计算；Agent 之间则在另一层分配工作。Avalon-M1 报告 §2.2.4 就采用 MoE policy，并在 RL 阶段冻结 router、回放 expert assignments。这是两篇材料的具体技术连接，不是已经验证了收益可相乘。[报告第 14 页](https://gr.inc/avalonm1.pdf#page=14)

## 两篇材料分别怎样读

Hugging Face 手册发布于 2026-11-05。它从集群准备和 dense 对照出发，拆解 MoE，再延伸到 serving 与 RL；阅读机制不要求立即租用集群。[Space 元数据与章节来源](sources.md)

General Reasoning 博客发布于 2026-11-02。它围绕集体推理的激励设计，解释为何需要让并行工作产生回报，并引用 Avalon-M1 的早期实验。报告及博客中的性能结果属于作者报告，不是本 Wiki 的重新测量。[Swarm 来源核验](sources.md)

建议阅读顺序：

1. 先用本页的对照表分清两层对象。
2. 读 MoE 章，验算参数、容量和负载的例子。
3. 读 RLCR 章，分清共享回报、共享权重和共享环境。
4. 用综合章的对照实验模板检查“更快、更强、更便宜”分别指什么。

30 分钟路线读两章开头和综合章；90 分钟路线顺序阅读并完成自测。时间是阅读预算，不是训练大型模型或复现长程任务的预算。

## 与已有知识的连接

- [Rufus-Air 奖励与稳定性](../rufus-air/reward-and-stability.md)：将 MoE 路由一致性放回实际后训练流水线。
- [Agentic-RL 的优化目标](../agentic-rl-lab/policy-objectives.md)：区分奖励、优势、概率比与归约。
- [长程信用分配](../agentic-rl-lab/credit-assignment.md)：集体优势为什么不是精确的个体贡献。
- [GPU、内存与 Roofline](../../diffusion/05-gpu-and-memory-roofline.md)：激活参数、访存、容量与实际时延不同。
- [Agent Sandbox](../../../agent-sandbox/README.md)：共享工作空间不意味着共享无限权限。
- [自我改进的评测与安全](../../self-improvement/evaluation-and-safety.md)：训练反馈、开发选择与最终验收分开。

## 阅读边界

本专题提供机制解读、原创教学算例与评测模板，不是两个源文的全文翻译。不下载模型权重，不启动 GPU 作业，不调用付费模型，也不声称已复现 MoE 训练或 Avalon-M1。手册的集群配置、作者的 benchmark 数字、Wiki 的简化公式分别标注；未来扩大集群或组织规模时，必须重新验证。
