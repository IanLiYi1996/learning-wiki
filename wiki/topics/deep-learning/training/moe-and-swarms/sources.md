# MoE 与 Swarm：一手来源、版本与核验边界

核验日期：2026-11-09。[专题导读](README.md) · [MoE 机制](moe-training.md) · [Swarm／RLCR](swarm-rlcr.md) · [跨层联系与评测](connections-and-evaluation.md)。所有结论追溯到原作者手册、论文、报告或官方文档。这里的“核验”是核对公开原文，不是独立重跑训练或评测。

## MoE：手册版本、章节与背景论文

Hugging Face 的 [The Ultimate MoE Training Handbook](https://huggingface.co/spaces/huggingface/moe-blogpost#s-1)由 Nouamane Tazi、Leandro von Werra、Thomas Wolf 撰写。[Space 的公开文本入口](https://huggingface-moe-blogpost.hf.space/llms.txt)明确标注发布于 **2026-11-05**；[Space API 元数据](https://huggingface.co/api/spaces/huggingface/moe-blogpost)核对了本次所读仓库版本。最后修改时间不能替代首次发布日期。

外层 Space 页面主要是 iframe；本次还直接读取作者公开仓库的章节源码，将嵌入 HTML 还原为文本，重点核对下列内容。不复制互动页面，不把页面里的模拟数值当作集群实测。

| 阅读对象 | 固定公开版本／原文入口 | 用途 |
| --- | --- | --- |
| 导言 | [chapter 1](https://huggingface.co/spaces/huggingface/moe-blogpost/blob/ef70726e6f8b99d74298a16a4894340f288a58c2/app/src/content/chapters/1-introduction.mdx) | 总参数与 active 参数、读者条件、路由／平衡／通信三个问题 |
| 环境与首跑 | [chapter 2](https://huggingface.co/spaces/huggingface/moe-blogpost/blob/ef70726e6f8b99d74298a16a4894340f288a58c2/app/src/content/chapters/2-setup-and-your-first-run.mdx) | §2.0–2.5 的硬件条件、all-to-all 诊断、容器、tokenization 与 dense／MoE 对照 |
| MoE 解剖 | [chapter 3](https://huggingface.co/spaces/huggingface/moe-blogpost/blob/ef70726e6f8b99d74298a16a4894340f288a58c2/app/src/content/chapters/3-anatomy-of-moe-training.mdx) | §3.1 scoring／数值、§3.2 routing、§3.3 balancing、§3.4 expert 粒度、§3.6 稳定性、§3.7 系统 |
| Serving 与 RL | [chapter 4](https://huggingface.co/spaces/huggingface/moe-blogpost/blob/ef70726e6f8b99d74298a16a4894340f288a58c2/app/src/content/chapters/4-from-training-to-serving.mdx) | serving top-k／驻留内存的区别、rollout 与 trainer 的路由不一致及回放边界 |
| 手册引用的训练实现 | [Megatron-LM 的 MoE 指南](https://github.com/NVIDIA/Megatron-LM/blob/d6316eb45bf1bfbb6f1f848c0b56e55166564d80/megatron/core/transformer/moe/README.md) | 手册 recipe 使用的固定 checkout；不是本次安装或执行的训练栈 |
| 官方 API 背景 | [Megatron Core 0.15.0 MoE 文档](https://docs.nvidia.com/megatron-core/developer-guide/0.15.0/api-guide/moe.html) | EP／TP／DP、grouped GEMM、capacity、padding／dropping 和 per-layer logging |

0.15.0 文档是有版本的机制背景，不宣称它与手册固定 checkout 的全部新 flags 兼容。手册还区分 main 上的功能及不同测量所用版本；实际运行须逐项查依赖。本 Wiki 没有执行命令验证这些兼容组合。

| 一手背景论文 | 本专题使用的机制 | 不扩大成什么结论 |
| --- | --- | --- |
| [Switch Transformers v3](https://arxiv.org/html/2101.03961v3) | §2.1–2.2 的 Top-1、门控、容量及式（4）–（6）的平衡项 | 所有模型都采用 Switch 的归一化／丢弃策略 |
| [DeepSeekMoE v1](https://arxiv.org/abs/2401.06066v1) | 细粒度 expert 与 shared expert 的架构动机 | expert 与人类职业存在固定一一对应 |
| [Loss-Free Balancing v1](https://arxiv.org/html/2408.15664v1) | §3 的动态选择 bias，§4.1 的 MaxVio | 不使用梯度或永远没有辅助目标 |
| [DeepSeek-V3 v2](https://arxiv.org/html/2412.19437v2) | §2.1.2 的选择 bias／原始权重、微小 sequence-wise aux loss、node-limited routing | auxiliary-loss-free 等于整个训练目标只有 LM loss |
| [ST-MoE v2](https://arxiv.org/html/2202.08906v2) | §3.3–3.4 的 router z-loss 与稳定性 | z-loss 就是负载平衡，或能消除所有 Top-k 数值差异 |
| [MegaBlocks v1](https://arxiv.org/abs/2211.15841v1) | 动态稀疏计算与 dropless 的系统动机 | dropless 自动消除了失衡和通信成本 |
| [R3 v2](https://arxiv.org/html/2510.11370v2) | §3–4 的 train-inference discrepancy 与 rollout routing replay | 路由回放对所有 MoE RL 都有保证收益 |
| [GSPO v2](https://arxiv.org/abs/2507.18071v2) | 序列级重要性比、裁剪与 MoE RL 稳定性 | GSPO 与 R3 是同一个算法或可直接替换 |

**算例来源**：9 B／3 B 参数、计数 `[8,4,2,2]`、MaxVio=1、容量 4、25% assignment 丢弃率、20 分钟 deadline、Amdahl 的 3.33 倍均为本 Wiki 构造。文档回归测试验算这些数值，不是模型 benchmark。参数计数、容量、概念 policy gradient 和关键路径公式均说明了简化范围。

**未执行**：没有申请 Slurm／Hugging Face Jobs、下载权重／训练数据、检查真实 GPU 或网络、启动 Megatron、重跑手册 profiler、测服务吞吐或 MoE RL 收益。公开源码可读不等于 recipe 已在本机复现。

## 1. 来源、发布日期与读取快照

| 一手来源 | 可确认的日期／状态 | 本次用途与限制 |
| --- | --- | --- |
| [How to Train a Swarm](https://www.gr.inc/blog/how-to-train-a-swarm)，General Reasoning team | 页首明确为 **2026-11-02** | 核对激励设计、time limits、作者对集体推理的解释；博客不是另一组独立实验 |
| [Avalon-M1: Reinforcement Learning from Collective Rewards](https://gr.inc/avalonm1.pdf)；[同站 www 入口](https://www.gr.inc/avalonm1.pdf) | 博客参考文献第 5 项注明 **October 2026**；当前 PDF **81 页**，首页／页眉注明仍在训练、修订中 | 核对方法、公式、表格、延迟口径及作者承认的限制；未发现显式版本号或修订日期 |
| [GR 官方首页 Latest](https://www.gr.inc/) 与 [Avalon-M1 发布页](https://www.gr.inc/releases/avalon-m1) | 首页把 Introducing Avalon-M1 标为 **2026-10-23**；发布页说技术报告随介绍当天发布 | 可把 2026-10-23 记为官方介绍及报告发布事件的日期；不能将其当作当前 PDF 每次修订的日期 |
| [MiniMax-M1 原论文 v1，§3.1](https://arxiv.org/html/2506.13585v1#S3.SS1) | **2025-06-16** | 仅解释 GR 报告引用的 CISPO 原始公式；不是 Avalon 的实现审计或独立复现 |

报告作者为 Iliyan Zarov、Henry Course、Anthony Hartshorn、Ran Achiron、Louis Roche、Akshit Sinha、Chengxi Taylor、Ross Taylor。作者列表与引用格式见[博客 Citation](https://www.gr.inc/blog/how-to-train-a-swarm#citation)及[报告第 1 页](https://gr.inc/avalonm1.pdf#page=1)。

直接读取的裸域与 www 域 PDF 经校验为相同内容；PDF 元数据 CreationDate／ModDate 均为 `2026-10-23 11:13:05 UTC`。这是文件元数据，不是经验证的公开上线时间或修订历史；本文不保存 PDF，也不声称该浮动 URL 将来仍返回同一内容。以下页码均为当前 PDF 的文档页码，`#page=` 使用一基页码。

## 2. Shared policy、flat collective advantage 与组织规模

| 待核验说法 | 原文支持的准确表述 | 原始位置与边界 |
| --- | --- | --- |
| 所有 agent 使用 shared policy | CEO 与 specialists 使用同一套模型权重 θ；角色差异来自上下文中的 mandate／角色描述，不是每个角色单独训练一套权重。CEO 与 specialists 联合训练，没有冻结一类 subagent 的独立策略 | [§2.1，第 9–10 页](https://gr.inc/avalonm1.pdf#page=9)、[§1.1，第 7 页](https://gr.inc/avalonm1.pdf#page=7)。共享权重不等于共享 KV cache 或同一上下文 |
| flat collective advantage | 一个 organisation rollout 的总奖励形成一个标量 advantage，同一组织各 agent 的有效生成 token 都使用它；不估计每个 agent 的边际贡献，也不做 per-agent counterfactual credit assignment | [§2.2.2，第 12 页](https://gr.inc/avalonm1.pdf#page=12)。相同 advantage 不代表各 token 的概率比、梯度或贡献相同 |
| 所有 token 都训练 | 只训练 policy 主动采样的 token。prompt、工具结果、环境观察及收到的其他 agent 消息不承担 loss；报告还列出重复与错误位置等额外 mask | [§2.2.2，第 12 页](https://gr.inc/avalonm1.pdf#page=12)。不能把接收消息再次计为生成动作的训练信号 |
| CEO／8 specialists | 预算 b 是 CEO **之外**可同时雇用的 specialists 上限；b=0 为单 agent，b=8 最多为 **CEO+8 specialists，即 9 个 agent**。CEO 先规划角色与工具权限，之后可雇用／解雇 | [§2.1，第 9 页](https://gr.inc/avalonm1.pdf#page=9)、[§2.2.4，第 14 页](https://gr.inc/avalonm1.pdf#page=14)。不是所有任务固定启动 8 位 specialists，也不是证明可扩展到任意规模 |
| RLCR 训练只包含多 agent | rollout 预算约 20% 用于单 agent、80% 用于多 agent；约 90% 训练 token 来自多 agent rollout | [§2.2.4，第 14 页](https://gr.inc/avalonm1.pdf#page=14)。之后的 B0 是同一混合训练模型的单 agent 执行模式 |
| shared policy 意味着所有参数都更新 | 报告另有模型内部约束：RL 阶段冻结 MoE router 及 load-balancing bias，重放 rollout 时的 expert assignment，不使用 load-balancing loss | [§2.2.4，第 14 页](https://gr.inc/avalonm1.pdf#page=14)。agent 的上下文角色与模型内部 MoE experts 是不同层次，不能互称“专家”后混为一谈 |

CEO、角色描述和通信工具本身就是 harness 先验。作者明确承认这些设计及预训练偏差可能影响观察到的层级与分工，因此“出现中间 lead 角色”不能改写成“从完全无结构状态自发发明管理层”。来源：[§7.1.2，第 40 页](https://gr.inc/avalonm1.pdf#page=40)。

## 3. 实际公式：GR 明文与引用算法分开

### 3.1 GR 报告明确公开了什么

组织回报使用跨 agent、跨 token 的未折扣奖励总和：

$$
R_i=\sum_{k=1}^{N_i}\sum_{t=1}^{T_{i,k}}r_{i,k,t}.
$$

这是 [§2.2.2，第 12 页，式（3）](https://gr.inc/avalonm1.pdf#page=12)。N_i 为 rollout i 的 agent trajectories 数，T_{i,k} 为该轨迹 token 数。环境奖励之外，报告还加入 malformed-tool、tool-execution-error 与 underhire penalties；underhire 权重随环境变化。因此不能把这个 R_i 一概描述成“唯一的终局正确性奖励”，也不能把相同 advantage 描述成精确的贡献归因。

多数环境使用 CISPO，报告直接给出的式（1）是 importance-sampling ratio 的**上裁剪**：

$$
\hat r_{i,t}(\theta)
=\min\!\left(r_{i,t}(\theta),\varepsilon_{\mathrm{high}}\right),
\qquad \varepsilon_{\mathrm{high}}=5.
$$

这里 r_{i,t}(θ) 是策略概率比，不能与式（3）的环境奖励 r_{i,k,t} 混用。该节另明确 **group size K=16**、丢弃零方差组，且未使用 IcePop；K 是 group-relative 优势的 rollout 组大小，不是组织中的 agent 数。来源：[§2.2.1.1，第 11 页](https://gr.inc/avalonm1.pdf#page=11)。

baseline 的证据比“只提到 group-relative”略强：[§2.2.3.3，第 14 页](https://gr.inc/avalonm1.pdf#page=14)明确不训练 critic；[附录 F.4 图 24，第 66 页](https://gr.inc/avalonm1.pdf#page=66)把 training advantage 标为组内 reward z-score。可以确认其组内相对／标准化语义，但正文没有完整列出 CISPO 的 baseline 与数值稳定实现。图 24 的“各 GRPO group 等权”描述的是分析图的统计汇总，不能据此确定训练 loss 的归约方式。

### 3.2 被引用的 CISPO 原论文：完整 objective 与 baseline

以下公式来自 **MiniMax 原论文，不是 GR 报告逐项公开的 Avalon loss**。采用该论文符号，输出轨迹 o_i 的 importance ratio 为：

$$
r_{i,t}(\theta)=
\frac{\pi_\theta(o_{i,t}\mid q,o_{i,<t})}
{\pi_{\theta_{\mathrm{old}}}(o_{i,t}\mid q,o_{i,<t})}.
$$

组内均值构成 baseline，优势由标准差归一化：

$$
b(q)=\operatorname{mean}(\{R_j\}_{j=1}^{G}),
\qquad
\hat A_{i,t}=
\frac{R_i-b(q)}
{\operatorname{std}(\{R_j\}_{j=1}^{G})}.
$$

其中 b(q) 是为便于中文解释而给原式均值项加的名称；这是原论文式（2）的代数重写。原论文式（4）的最大化目标为：

$$
\mathcal J_{\mathrm{CISPO}}(\theta)=
\mathbb E_{(q,a)\sim\mathcal D,\,
 \{o_i\}_{i=1}^{G}\sim\pi_{\theta_{\mathrm{old}}}(\cdot\mid q)}
\left[
\frac{
 \sum_{i=1}^{G}\sum_{t=1}^{|o_i|}
 \operatorname{sg}(\hat r_{i,t}(\theta))\,
 \hat A_{i,t}\,
 \log\pi_\theta(o_{i,t}\mid q,o_{i,<t})
}{
 \sum_{i=1}^{G}|o_i|
}
\right].
$$

sg 表示 stop-gradient。若采用最小化 loss 的代码约定，可写 L_CISPO=−J_CISPO；这个符号转换不是 GR 新公布的式子。MiniMax 式（5）用两侧 clip 描述 ratio，但随后说明其实际实验不施加有效下界。CISPO 裁剪的是作为梯度系数的 IS weight，不应直接替换为 PPO 的 `min(rA, clip(r)A)` surrogate。来源：[MiniMax-M1 §3.1，式（2）、（4）、（5）](https://arxiv.org/html/2506.13585v1#S3.SS1)。

**实现缺口：**GR 引用 CISPO 并明确 upper cap=5，不等于公开了全部训练代码。仅由上述引用不能确认 Avalon 的 stop-gradient 放置、agent／rollout／batch／全局 token 归约、mask 后分母、标准差的自由度及 epsilon、优势 detach／缩放、额外正则，以及异步 rollout 所用旧概率的版本管理。原论文完整目标用于解释算法，不能当作这些细节已经被核实；尤其不能将“相同标量优势”偷换成“每个 agent 等权 loss”。

### 3.3 GKPO 不是所有环境共用的 baseline

GR 对部分长期财富目标使用另一个方法 GKPO。报告式（2）直接给出：

$$
A_i^{(\beta)}=
\frac{1}{\beta}
\left[
\frac{e^{\beta R_i}}
{\frac{1}{K}\sum_{j=1}^{K}e^{\beta R_j}}
-1
\right].
$$

此处 R_i 是 log-return，不能无说明地等同于上一小节所有环境的奖励定义。作者取 β=0.2582，再以 gain g 缩放优势；β>0 时下界为 −1/β，β→0 恢复 Kelly advantage，β=1 为 risk-neutral 情形。报告称其与核心 RLCR 配方正交，只用于特定长周期环境；当前字节流的附录 H 仅写实践中 g 在 2–6 之间，没有逐环境列出精确取值。来源：[§2.2.1.2，第 11–12 页，式（2）](https://gr.inc/avalonm1.pdf#page=11)、[附录 H，第 70–71 页](https://gr.inc/avalonm1.pdf#page=70)。这不能拿来补写 CISPO 的 baseline，也不是独立验证了 GKPO 效果。

## 4. Time-limit、anytime-return 与显式 latency penalty

博客讨论的显式惩罚候选式是：

$$
R(\tau)=R_{\mathrm{task}}(\tau)
-\beta\,\bar p(q)\,\frac{T(\tau)}{T_{\max}}.
$$

T(τ) 是 rollout wall-clock，p̄(q) 是该任务各 rollout 的平均 pass rate。作者把它列为**一种可能形式**，没有说这是 Avalon 的实际 reward。这个 β 也不是 GKPO 的 β。来源：[博客 Making parallel work pay → Latency penalties](https://www.gr.inc/blog/how-to-train-a-swarm#making-parallel-work-pay)。

Avalon 实际采用 time limit 作为 latency pressure：达到上限便取截至该时刻的总回报，不额外套用上述显式惩罚。训练 wall-clock 上限从 **2 小时**线性增加，到 **step 200 略超过 5 小时**，也可以由 agent 提前结束。来源：[博客 Time limits](https://www.gr.inc/blog/how-to-train-a-swarm#making-parallel-work-pay)、[报告 §2.2.4，第 14 页](https://gr.inc/avalonm1.pdf#page=14)。

其前提是环境有 anytime-return：任意截断点仍能给出进展信号，例如当前通过测试的比例、交易收益、带中间奖励的游戏。它不是“不做奖励设计就能从所有稀疏终局任务取得中途奖励”。相同 deadline 前完成、取得相同任务回报的两个 rollout 不因完成早晚不同而自动得到不同分数；deadline 不是对每一秒提前完成的连续奖励。来源：[博客 Time limits](https://www.gr.inc/blog/how-to-train-a-swarm#making-parallel-work-pay)、[§2.2.3.1，第 13 页](https://gr.inc/avalonm1.pdf#page=13)。

作者认为延长 horizon 可让组织摊薄 coordination tax，并减少等待完整 rollout 的训练成本，但明确说**未系统测量课程带来的训练加速**。不能把推理阶段约 4× 的 derived-latency 比较改写成“RL 训练加速 4×”。来源：[§2.2.3.1，第 13 页](https://gr.inc/avalonm1.pdf#page=13)。

## 5. Matched-token：作者结果支持什么

B0、B2、B4、B8 分别表示同一 Avalon 模型以 0、2、4、8 位额外 specialists 的预算执行。S8 是 **output-token budget forcing** 的单 agent：未生成到 B8 组织所用 output tokens 之前不允许提交，提前提交会被要求继续改进。它是 matched-output-token **推理** baseline，不是单独训练的纯单 agent 模型，也不是 matched-FLOPs／成本／显存实验。定义见[§3.2.1／表 3，第 20 页](https://gr.inc/avalonm1.pdf#page=20)。

下面只摘取说明边界所需的作者表格数值，未重算成绩：

| Benchmark | B0：单 agent | B8：CEO+最多 8 specialists | S8：匹配 output tokens 的单 agent | 能说明的边界 |
| --- | ---: | ---: | ---: | --- |
| IMO-ProofBench-Advanced | 29.8% | 37.5% | 37.7% | 相比普通单 agent 的提升，大部分可由更多 token 恢复 |
| FrontierScience | 55.9% | 63.5% | 55.5% | 该任务上组织优于 S8，但不能由此推出所有任务都如此 |
| SWE-Bench Pro V2 (Hard) | 21.6% | 23.5% | 37.3% | S8 明显高于 B8，否定“组织在同 token 下普遍更准确” |

来源：[表 3，第 20 页](https://gr.inc/avalonm1.pdf#page=20)。组织胜过普通单 agent 的“14/16 个百分比 benchmark、平均 +3.9 个百分点”是作者相对普通执行模式的汇总，**不是**相对 S8 的优势；S8 也未覆盖所有长周期 benchmark。来源：[§1.2，第 7 页](https://gr.inc/avalonm1.pdf#page=7)、[§3.2.1，第 20–21 页](https://gr.inc/avalonm1.pdf#page=20)。

在 matched output tokens 的延迟比较中，报告给出 S8 用时为 B8 的 **2.9–6.2 倍**，平均组织约 **3.9× 更快**；IMO 示例为 **121 对 38 分钟**。这些分钟都是下节的 derived latency。HealthBench 很短，固定招聘／协调开销更显著。博客把总体结果概括为约 4×；不能保证换模型、任务、组织规模或服务负载后仍有同样加速。来源：[§3.2.2／图 6，第 21–22 页](https://gr.inc/avalonm1.pdf#page=21)、[博客 Signs of life](https://www.gr.inc/blog/how-to-train-a-swarm#signs-of-life)。

另一个 DRACO time-budget 实验用 **step 170** checkpoint、100 个内部任务，比较 3、5、10、20 分钟 working time。working time 结束后解雇 specialists，再让 CEO **不限时**整理最终报告；因此不是整个任务端到端的严格同一 wall-clock 上限。作者观察短至 3 分钟时组织落后，之后收益改善。来源：[§3.2.2.1／图 7，第 22–23 页](https://gr.inc/avalonm1.pdf#page=22)。

## 6. Derived latency：不是实测部署时延

报告通过 event log 重放构造每个 agent 的虚拟时钟。下式是对附录 C.2 文字规则的数学重述，**不是声称原文另有这个编号公式**：

$$
\Delta c_{\mathrm{model}}
=\frac{n_{\mathrm{in,new}}}{15000}
+\frac{n_{\mathrm{out}}}{50}
\quad\text{秒},\qquad
T_{\mathrm{derived}}=\max_a c_a.
$$

规则来自[附录 C.2，第 59–61 页](https://gr.inc/avalonm1.pdf#page=59)，其中 15,000／50 tokens/s 也明确见[§3.2.2，第 22 页](https://gr.inc/avalonm1.pdf#page=22)：

- output 包含 reasoning；只计 context 新增的 prompt token，已 prefill 的部分不反复计费；compaction 重写后的 context 重新全量计入。
- 工具调用计入实测执行耗时；同 turn 并行 read-only 工具按时间区间并集计，不直接相加。
- 专家受雇时从 CEO 当前时钟起步；接收消息／报告／帖子会把接收方时钟推到发送方发送时刻，若后者更晚。
- 纯等待不推进时钟，依赖输出的等待通过消息同步体现；最终取所有 agent 的最大时钟，即最长依赖链。

因此该指标包含模型计算、工具执行与依赖关系的近似，但去除了服务端排队／batching 等噪声，不是用户实际等待时间，也不是总 agent-hours 或总资源成本。报告还说明与所参照外部 system card 的绝对时间不可直接比较，因为对方未公布参考速率。内部 agent 总 output tokens 与 critical-path tokens 也不同：并行工作的 token 可以增加总量而不等量增加关键路径。来源：[附录 C.2，第 59–61 页](https://gr.inc/avalonm1.pdf#page=59)。

## 7. 差异、风险与尚不能称为独立复现的内容

| 差异／缺口 | 原文证据 | 本笔记处理 |
| --- | --- | --- |
| EdgeBench crossover 不一致 | [博客 Signs of life](https://www.gr.inc/blog/how-to-train-a-swarm#signs-of-life)写 8-hire 组织约 **2.4h**；[报告图 8，第 23 页](https://gr.inc/avalonm1.pdf#page=23)写观测 **1.7h**、拟合 **1.8h**；[§3.3.1，第 24 页](https://gr.inc/avalonm1.pdf#page=24)采用约 1.7h | 1.7／1.8 是观测与 log-logistic 拟合的区别；没有找到解释 2.4 与报告差异的作者说明，不臆测 checkpoint、重跑或四舍五入 |
| EdgeBench seeds 计数不一致 | [§3.3，第 23 页](https://gr.inc/avalonm1.pdf#page=23)写 49 tasks、每任务 4 seeds，图 8／§3.3.1 分析四个预算共 450 runs；[表 4，第 60 页](https://gr.inc/avalonm1.pdf#page=60)写 49 tasks、1 seed | 不替作者补齐缺失 run、筛选条件或表格修正；需要作者澄清哪些样本进入哪个结果 |
| 内部 search benchmark 不是公开 leaderboard 原设定 | [附录 C.1，第 59 页](https://gr.inc/avalonm1.pdf#page=59)：BrowseComp-Internal／DRACO-Internal 用 BackSearch 的内部固定索引，作者明确绝对分数不可与公开结果直接比较 | 保留 `-Internal`，只在作者相同索引／grader 条件下比较，不删除后缀后引用外部排名 |
| 没有纯单 agent matched-compute 训练消融 | [§7.1.1，第 40 页](https://gr.inc/avalonm1.pdf#page=40)：因算力不足，没有同环境、同 harness、同训练 compute 的纯单 agent 训练 run | B0／S8 的执行模式比较不能证明 RLCR 训练配方本身优于等预算纯 RLVR |
| 小规模与信用分配的推广限制 | [§7.1.1，第 39–40 页](https://gr.inc/avalonm1.pdf#page=39)、[博客 Outstanding problems](https://www.gr.inc/blog/how-to-train-a-swarm#outstanding-problems)：长 horizon、多个 agent、多环境共同增加 flat-advantage 方差；目前最多 9 agent | 不把这组实验扩展为数百／数千 agent 已验证，也不把粗粒度 credit 写成问题已解决 |
| 行为相关性不是每项组织实践的因果证明 | [§7.2，第 41 页](https://gr.inc/avalonm1.pdf#page=41)：层级、peer review 与分工的个别因果贡献仍未解决 | 通信 token 增多不自动等于通信更有效；角色分析也受 harness 与检测方法影响 |
| 性能增强不自动保证监督安全 | [§7.2，第 41 页](https://gr.inc/avalonm1.pdf#page=41)：受测场景中拒绝有害动作仍接近普遍，但向人类报告问题的频率降低 | “作者未发现明确安全违规”不能简化成“集体已安全／已对齐” |

所有分数、增长趋势、约 4× 的延迟优势、课程效果解释及 emergent hierarchy 分析，均是 **GR 作者报告的结果**。博客、发布页与 PDF 属于同一研究的不同表达，不构成三次独立复现。本文没有下载权重、安装训练栈、执行 rollout、调用模型、重跑 benchmark、重算置信区间或实现训练 loss。

报告结论仍将权重、harness、环境发布写为后续计划；这只能证明作者当时的计划，不能证明本次已取得资产，更不能证明外部团队已重现结果。来源：[§7.2，第 41 页](https://gr.inc/avalonm1.pdf#page=41)、[官方发布页 Roadmap](https://www.gr.inc/releases/avalon-m1)。本次没有检索全部潜在复现工作，不能反向断言“外界绝无复现”。

工具核验限制：已读取博客、官方首页／发布页、www PDF 文本和算法原论文；裸域 PDF 的浏览打开失败，随后直接读取并校验。浏览工具对同一 PDF 的第 60 页截图曾显示与当前直取字节流及可读文本不同的速率数字；本文采用当前可读文本中的 **15,000／50**，没有混用截图数字，也不据此虚构作者修订史。浮动链接、工具缓存和文件元数据均不足以确定具体修订时间。

进一步复现至少需要固定报告／代码／权重版本，明确完整 CISPO loss 与 mask 归约、baseline 数值处理、异步旧策略概率、课程和组织预算、环境 reward／停止语义、实际使用的评测样本，以及 derived-latency 的事件日志与参考速率。以上是根据已识别缺口提出的核验清单，不是声称作者已经提供全部材料。
