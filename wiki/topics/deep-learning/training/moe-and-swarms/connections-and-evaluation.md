# 03 结合 MoE 与 Swarm：两层计算、关键路径与评测合同

研究与来源核验日期：2026-11-09。[专题导读](README.md) · [MoE](moe-training.md) · [Swarm／RLCR](swarm-rlcr.md) · [一手来源](sources.md)。

本章的对照、算例和检查表是 Wiki 的教学综合，不是 Hugging Face 或 General Reasoning 宣称的新算法。背景机制分别来自 [MoE 手册](https://huggingface.co/spaces/huggingface/moe-blogpost#s-1) 与 [Swarm 博客](https://www.gr.inc/blog/how-to-train-a-swarm)。

## 1. 可以结合的是分层，不是把 Expert 改名叫 Agent

这并非仅是假想组合：Avalon-M1 报告 §2.2.4 明确采用 MoE policy，RL 阶段冻结 router 及 load-balancing bias、回放 rollout 的 expert assignments，并不使用负载平衡 loss。它将集体行为的训练与内部路由的一致性约束放在同一 recipe 中。[报告第 14 页](https://gr.inc/avalonm1.pdf#page=14)

将这种系统概念化，有两层决策：

```text
任务与评测环境
  └─ Agent 组织：委派、消息、工具、共享状态
       ├─ Agent A 的上下文 → LLM 生成
       └─ Agent B 的上下文 → LLM 生成
                              └─ 每个 MoE 层：Router → Experts → Combine
```

上层决定谁做什么、何时通信；下层决定一个 token 经过哪些参数。改变上层 Agent 数，并不等于改变下层 top-k；共享 checkpoint，也不等于把每个 Agent 绑定到一个 expert。

RLCR 为组织行为提供学习信号；MoE 是承载 policy 的网络架构。报告说所有 Agent 联合训练，不意味着 policy 的所有参数都更新；router 是明确的冻结子集。冻结矩阵和 bias 本身也不足以保证数值路径完全一致，其他网络权重改变会改变 router 输入；报告的 expert-assignment 回放是另一个明确步骤。

Dense policy 同样可以承载组织训练。MoE 相比 dense 在相同集体训练预算下有什么收益，需另行消融，不能把两篇文章的结果直接相乘。

## 2. 共同问题：分工收益能否覆盖协调成本

两者都让“更多单元”可能成为容量或并行优势，但增加单元本身不是验收标准。

| 共同提问 | 在 MoE 中 | 在 Swarm 中 |
| --- | --- | --- |
| 是否有效分工？ | 路由选择与 expert 表示是否有用 | 子任务是否互补、产物能否合并 |
| 谁成了瓶颈？ | 热 expert、最慢 rank、显存或互连 | 顺序依赖、慢成员、工具或集中协调 |
| 协调花了什么？ | 张量通信、排列、同步和缓冲 | 消息 token、等待、重复工作和冲突 |
| 从什么学？ | 主任务梯度与路由控制 | 集体回报与策略梯度 |
| 如何证实收益？ | 质量与实测吞吐／成本对照 | 质量—延迟—总计算的匹配对照 |

这些是分析问题的共同坐标，不是可互换的实现。MoE 的张量合并有明确网络计算结构；消息协作则涉及环境语义、状态变化和非确定性工具，错误模式不同。

## 3. 延迟看关键路径，成本看总量

下式是教学分解，不是两个源文的 benchmark 公式：

$$
T_{\text{finish}}\approx T_{\text{serial}}+
T_{\text{parallel-critical-path}}+
T_{\text{coord,exposed}}.
$$

并行段只看关键路径；总工作／费用则需要累计所有分支。若分支有交叉依赖，应画实际依赖图，不应简单取所有 Agent 时间的最大值。

用 Amdahl 的简化直觉，如果工作的 20% 必须串行，其余 80% 可均匀并行到 8 份，忽略开销时：

$$
\operatorname{Speedup}(8)=
\frac{1}{0.2+0.8/8}=\frac{10}{3}\approx3.33.
$$

不是 8 倍；再加协调、等待和资源竞争，收益可能更小。这里的 20%、8 份和 3.33 都是原创算例，不是 Avalon-M1 实验。

同理，一个 MoE 推理请求降低 active expert 计算，也可能仍受权重读取、KV cache、batch 调度或互连约束。[硬件与 Roofline 读本](../../diffusion/05-gpu-and-memory-roofline.md)

**更低延迟、更少总 token、更少 GPU 小时、更低账单是四种主张。** Swarm 可在总计算不降甚至上升时降低延迟；MoE 可在降低单 token 计算时仍保有较大的驻留内存。

## 4. 从训练到评测，至少固定三层接口

| 接口 | 应保存什么 | 否则可能误判什么 |
| --- | --- | --- |
| 模型计算 | checkpoint、精度、top-k、router 配置、batch、推理引擎 | 同权重但不同内部计算路径 |
| 行动轨迹 | role／模板、消息可见性、工具结果、时间戳、生成 mask、采样概率 | 训练的行为并非实际采样的行为 |
| 环境与评分 | 初始状态、harness、测试版本、截止点、失败／超时规则 | 环境变了，却把差异归给模型学习 |

MoE rollout 的路由一致性问题由 [R3](https://arxiv.org/abs/2510.11370v2) 专门讨论；集体行动的激励与环境设计由 [RLCR](https://gr.inc/avalonm1.pdf) 讨论。它们分别处理接口的不同部分。

一个消息产生高回报，不代表它一定造成高回报；一次路由一致，也不代表评分器没有漏洞。正确性、因果归因和数值一致性是三个检查项。

## 5. Swarm 最小对照矩阵

以下是复现计划模板，尚未运行真实模型：

| 对照组 | 保持什么 | 想分离的因素 |
| --- | --- | --- |
| 单 Agent，普通预算 | 同 checkpoint、环境与工具 | 基础任务能力 |
| 单 Agent，匹配集体总生成 token | token 记账范围一致 | 多算的贡献与并行的贡献 |
| 多 Agent，独立尝试后选择 | 相同样本数和选择器预算 | 不交流的并行搜索 |
| 多 Agent，无通信但保留可行任务分解 | 相同人数及能力 | 消息机制是否带来收益 |
| 多 Agent，允许通信但未做集体训练 | 相同组织接口和预算 | 预置 Harness 与 RL 学习的贡献 |
| 多 Agent，RLCR 后 | 相同 held-out 任务、预算与停止规则 | 集体训练的增益 |

消融要保持任务可执行。删除通信却不给必要的子任务输入，会把协作消融变成“破坏任务”。对于共享文件等其他隐式沟通渠道，也必须明确保留或关闭什么。

评测应扫过多个 deadline 和多个团队规模，报告均值、波动与失败，而不是挑一个交叉点。Token 匹配需说明是否包括 reasoning、communication、prompt／重复上下文及选择器消耗；matched output tokens 不自动等于 matched 总 FLOPs 或费用。

## 6. MoE 最小对照矩阵

模型侧应另做：

- 架构对照：固定数据与训练 token，明确匹配总参数还是激活计算。
- 路由对照：不同平衡方式同时报告持出损失、MaxVio、drop rate 和任务质量。
- 系统对照：同硬件、同模型和同数据，分别改变 EP 布局、kernel 与 overlap。
- RL 一致性对照：同一输入、权重及采样设置下比较 routing agreement 和 log-probability gap，再比较有／无回放的学习。

强制随机均衡路由可作为系统诊断，但它改变了模型选择，不是训练质量的正式基线。手册将系统表现与学习结果分别观察。[手册 §3.3、§3.7](sources.md)

## 7. 怎么读两个源文里的数字

手册的集群测量首先属于它的硬件、软件和 workload；博客／报告的集体结果首先属于其环境、组织和评测协议。阅读时给每个数字补上五项：

1. 比什么：哪个模型／组织、哪个基线。
2. 固定什么：token、质量、时间还是资源。
3. 怎么计：墙钟实测、derived latency 还是模拟。
4. 做了什么：独立复现、源码核验还是只阅读作者材料。
5. 能推多远：同设置、跨任务还是跨规模。

本专题只完成原文阅读、机制核验、教学算例及文档／构建检查。**Derived latency 不自动等于真实服务中的墙钟等待；作者报告也不等于独立复现。** 数字定位及尚未公开／未执行的部分见[来源页](sources.md)。

## 8. 下一步学习，不直接开启昂贵训练

初学者先验算三件事：参数容量与 active count 的区别；容量和负载的区别；deadline 下的同分但不同完成时间。再阅读原文公式，对上本专题使用的简化记号。

做工程复现则先写训练合同：GPU 和互连、环境时间模型、记账范围、数据持出、评分器权限、checkpoint 恢复及预算上限。共享状态应纳入 [Sandbox 与凭证边界](../../../agent-sandbox/README.md)，长程更新则连接 [Agentic-RL 信用分配](../agentic-rl-lab/credit-assignment.md)。

## 自测

1. “用 MoE 的 Swarm”里，人数翻倍会让每 token 激活 expert 数翻倍吗？
2. 为什么匹配输出 token 的两个系统仍可能成本不同？
3. 怎样判断通信是产生收益的原因，而不是训练过程中同时上升的统计量？

参考：不必，组织规模与网络 top-k 不同层；prompt、读取、工具、硬件和并行闲置成本仍可不同；固定预算和接口做通信消融，验证实际产物，并报告多种截止时间与任务的结果。
