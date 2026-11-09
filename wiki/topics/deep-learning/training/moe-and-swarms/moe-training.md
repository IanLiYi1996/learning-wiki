# 01 MoE：从 Top-k 路由到真正可用的训练吞吐

研究与来源核验日期：2026-11-09。[专题导读](README.md) · [下一章：Swarm 与 RLCR](swarm-rlcr.md) · [来源](sources.md)。

MoE 的主要承诺不是“几个模型投票”，而是让一个网络拥有较大的参数容量，同时让每个 token 只经过部分 expert。实现这种稀疏计算以后，仍要解决梯度、负载与硬件效率。[Switch Transformers](https://arxiv.org/abs/2101.03961v3)

## 1. 一个 token 怎样走过 MoE

下面是常见 token-choice MoE 的教学表达，不覆盖所有 router 变体：

$$
s_i(h)=\operatorname{score}(W_rh)_i,\qquad
S(h)=\operatorname{TopK}_i s_i(h)
$$

$$
y(h)=\sum_{i\in S(h)}g_i(h)E_i(h).
$$

$h$ 是某层的隐藏向量，$W_r$ 是 router 参数，$E_i$ 是 expert 网络，$g_i$ 是用于合并结果的权重。选择 expert 和计算合并权重是两个步骤，不能默认为同一数值。存在 shared expert 时，还会加入相应的常开计算分支。[DeepSeekMoE](https://arxiv.org/abs/2401.06066v1)

若对所选 softmax 分数重新归一化，则 $g_i=s_i/\sum_{j\in S}s_j$。这是一个明确的约定，不是所有实现的统一形式。手册 §3.1 特别区分选取前／后 softmax、sigmoid、归一化和输出缩放；改变其中一项就可能改变输出幅度。[手册章节定位](sources.md)

**教学反例**：如果只选一个 logit 再对它做 softmax，结果恒为 1，该门控系数不能通过这条路径向 router 提供梯度。Top-1 不是不能学习，而是需要使用仍依赖原始分数的门控方式；Switch 使用完整 softmax 得到被选 expert 的门控概率。[Switch §2.1](https://arxiv.org/html/2101.03961v3)

## 2. 总参数、激活参数和运行成本是三个数

假设有 $L$ 个 MoE 层，每层 $N$ 个 routed expert、每个 $P_e$ 个参数，每个 token 选 $k$ 个。把其余常用参数统记为 $P_{\text{common}}$，则教学近似为：

$$
P_{\text{total}}\approx P_{\text{common}}+LNP_e,\qquad
P_{\text{active/token}}\approx P_{\text{common}}+LkP_e.
$$

这忽略了参数共享、不同层宽度和额外模块，只用来理解计数。**不是完整 FLOPs 公式，也不是显存公式。** 未激活的 expert 仍需存放；训练还包含梯度、优化器状态、反向激活与通信缓冲。[Megatron MoE 指南](https://docs.nvidia.com/megatron-core/developer-guide/0.15.0/api-guide/moe.html)

原创算例：$P_{\text{common}}=1$ B，$L=10$，$N=8$，$P_e=0.1$ B，$k=2$。总参数为 9 B，每 token 激活参数约 3 B。不能从这里推出显存只有三分之一或延迟恰好是三分之一。甚至一个 batch 可能覆盖所有 expert。

要比较 dense 与 MoE，至少说明固定的是总参数、激活计算、训练 token、质量还是墙钟预算；不同固定项回答不同问题。

## 3. Expert 分工：粒度和共享分支

DeepSeekMoE 把较大的 expert 切成更多、更小的 expert，并相应增加所选数量，以扩大组合空间；另设 shared expert 学习共用成分，减少 routed expert 的冗余。[DeepSeekMoE 原论文](https://arxiv.org/abs/2401.06066v1)

“细粒度”不等于无条件更快：总 active width 相近时，小矩阵、更多调度和通信仍可能降低硬件利用率。Shared expert 也不是免费的知识库；它增加实际计算，若要公平比较，应将其纳入激活预算。这两项首先是架构选择，其次才是 kernel／部署选择。

不能凭 expert 编号就认定它是“数学专家”或“代码专家”。语义专门化需要查看路由统计及干预效果；expert 是网络模块，不是有独立对话和工具的角色。

## 4. 负载平衡：不让少数 expert 拖住全部 GPU

设统计窗口内各 expert 获得的 token-expert assignments 为 $n_i$。本章采用：

$$
\bar n=\frac{1}{N}\sum_i n_i,\qquad
\operatorname{MaxVio}=\frac{\max_i n_i-\bar n}{\bar n}.
$$

这是最大负载超出均值的比例；不是“最大／最小负载”，也不是直接的 GPU 利用率。[Loss-Free Balancing §4.1](https://arxiv.org/html/2408.15664v1)

原创算例：4 个 expert 的计数为 $[8,4,2,2]$，均值 4，MaxVio 为 1，最热 expert 的负载是均值的两倍。若计数发生在不同层、不同 batch 或不同 token mask 上，不应直接混比。

两类平衡方法要分开：

| 方法 | 改变什么 | 需要警惕什么 |
| --- | --- | --- |
| 辅助负载损失 | 给训练目标增加鼓励均衡的项 | 系数过强可能与语言建模目标竞争 |
| 动态 expert bias | 根据近期负载改变选择倾向 | 平衡窗口、更新步长、状态恢复及过度纠偏 |

这组区分及其比较来自 [Auxiliary-Loss-Free Load Balancing](https://arxiv.org/abs/2408.15664v1)。

以 Switch 的 top-1 为例，辅助项可写为 $\alpha N\sum_i f_iP_i$：$f_i$ 是实际选择比例，$P_i$ 是全 softmax 分数的平均值。不要把这个 top-1 定义直接贴到 top-k 实现而不检查计数归一化。[Switch 式 (4)–(6)](https://arxiv.org/html/2101.03961v3)

DeepSeek-V3 的动态 bias 只影响选择，合并权重仍由原始 affinity score 产生；而且它保留了很小的 sequence-wise 辅助项。**Auxiliary-loss-free 指一种主要平衡机制，不代表整个模型绝无任何辅助损失。**[DeepSeek-V3 §2.1.2](https://arxiv.org/html/2412.19437v2)

## 5. 容量、丢弃和 dropless

对于某个明确统计域内的 $T$ 个 token，top-$k$ 共提出 $Tk$ 次 expert assignment。教学容量表达为：

$$
C=\left\lceil c\,\frac{Tk}{N}\right\rceil,
$$

$c$ 是 capacity factor。实际实现须查清 $T$ 按 rank、batch 还是其他域计数，以及取整规则。[Megatron 容量机制](https://docs.nvidia.com/megatron-core/developer-guide/0.15.0/api-guide/moe.html)

当 expert 超过容量时，dropping 会取消部分分配；这不是删除整段输入，也不保证取消整个 token 的所有 expert 路径。Padding 则为不足容量的 expert 补形状，两者不能混称。Dropless 不丢分配，但并没有让失衡、缓冲或动态形状问题消失。[MegaBlocks](https://arxiv.org/abs/2211.15841v1)

原创算例：$T=16,k=1,N=4,c=1$，得到 $C=4$。路由计数为 $[8,4,2,2]$，容量约束使最热 expert 的 4 次分配被丢弃，assignment dropping rate 为 $4/16=25\%$。这只是算例，不是推荐配置或实际训练结果。

验收时应同时记录丢弃率、持出损失与任务质量；“更快”若来自跳过计算，就不是与 dropless 完全等价的优化。

## 6. Router 数值稳定，不等于负载平衡

ST-MoE 引入 router z-loss，惩罚 logits 的 logsumexp：

$$
\mathcal L_z=\frac{\beta}{T}\sum_t
\left(\log\sum_i e^{z_{t,i}}\right)^2.
$$

它限制 logits 的尺度，不直接要求各 expert 接收同样多的 token。[ST-MoE §3.3–3.4](https://arxiv.org/html/2202.08906v2)

因此 z-loss、负载辅助项、MaxVio 和 expert 激活范数各测不同对象。较低精度还可能把接近的分数变成并列，影响离散 Top-k；把敏感 router 计算保留在更高精度是稳定性策略，不意味着整个网络都用 FP32。手册 §3.1、§3.6 将数值问题和负载问题分别观察。[手册](sources.md)

## 7. Expert Parallelism：搬 token，不是复制数据并行

EP 将不同 expert 放到不同 GPU。典型 all-to-all dispatcher 的前向路径是：

```text
隐藏状态 → Router → 排列 token
                    ↓
              dispatch 到目标 GPU
                    ↓
                expert 计算
                    ↓
              combine 返回原位置 → 加权合并
```

DP 主要复制模型处理不同样本；TP 切分张量计算；PP 切分模型层；EP 切分 expert。它们可以组合，但通信范围和内存分布不同。[Megatron 并行指南](https://docs.nvidia.com/megatron-core/developer-guide/0.15.0/api-guide/moe.html)

分配均衡后，仍要检查跨节点互连、小 GEMM 效率、排列开销和未被计算遮住的通信。一个通信 kernel 占用时间很长，也可能含等待最慢 rank 的时间，不全是链路正在传字节。手册 §2.1、§3.7 的实践重点是：先测实际使用的 collective，再看 profiler，不能只凭 all-reduce 成绩推断 all-to-all。[手册章节](sources.md)

建议的排查顺序是本 Wiki 的工程检查表：

1. 固定数据、tokenizer、精度和模型计算预算，建立 dense／MoE 对照。
2. 看每层 token 计数和每个 rank 汇总负载，再解释通信等待。
3. 分析 kernel、互连和显存，逐项比较 grouped GEMM、融合、EP 布局及 overlap。
4. 每次优化同时检查质量与成本，不把改变路由规则的实验当作纯系统优化。

## 8. Serving 与 RL：不要只检查 checkpoint 相同

Serving 中的 prefill、decode、batch 大小和 expert 热点都可能与预训练不同。降低 serving top-k 会改变选择集合及合并权重，并不自动降低所有 expert 的驻留内存；必须重新测质量。手册第 4 章专门讨论这种“训练配置不等于服务配置”的差异。[手册](sources.md)

RL 更要检查 rollout engine 与 trainer：不同 kernel、精度、batch 或旧权重可使同一序列选择不同 expert，并产生 log-probability 差异。R3 记录并回放 rollout 路由，针对的是这一内部计算一致性；它不解决环境奖励是否正确的问题。[R3 原论文 §3–4](https://arxiv.org/html/2510.11370v2)

GSPO 从序列级概率比与裁剪处理稳定性，是不同层面的办法；R3 与 GSPO 都有作者在特定设定下的结果，不能由一篇文章推出所有 MoE RL 必须使用同一方案。[GSPO](https://arxiv.org/abs/2507.18071v2)

## 自测

1. 激活参数只有总参数的三分之一，为什么不能推出显存和时间都只有三分之一？
2. $[8,4,2,2]$ 的 MaxVio 和 top-1、容量 4 时的 assignment 丢弃率各是多少？
3. z-loss、平衡损失和动态 expert bias 是否解决同一问题？

参考：分别要考虑驻留、优化器／激活、通信和 kernel；两个数为 1、25%；三种机制分别涉及数值尺度、梯度上的负载目标及选择倾向。下一章把“分工单元”换成能够行动的 Agent，但不会把这些损失原样搬过去。
