# 扩散语言模型：并行生成为什么难，缓存又能省下什么

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

自回归语言模型按顺序生成下一个 token。离散扩散语言模型可以先留下多个遮盖位置，再反复预测、选择并提交其中一些位置。它允许在一次前向中处理多个待生成 token，但也带来一个问题：本轮补上的内容，会改变其他位置下一轮看到的上下文。更多并行输出不一定意味着更少计算，也不保证相同答案质量。[Sparse-dLLM，§1–3][P4]

OpenMOSS 在这一方向的工作主要是分析和改进已有扩散基座：LongLLaDA 研究长度外推，Sparse-dLLM 研究推理计算复用，DiRL 研究后训练。LLaDA、Dream 和 SDAR 等基座不应计为团队从头预训练的成果。这里重点讲生成机制和缓存；长度分析见[长上下文专题](07-long-context-and-diffusion-optimization.md)，DiPO 的训练概率见[后训练专题](14-post-training-and-rl.md)。[LongLLaDA][P3]、[DiRL][P5]

## 1. 生成顺序变了，概率条件也变了

自回归模型把一句话的概率分解为

$$
p_\theta(y\mid Q)=\prod_{j=1}^{L}p_\theta(y_j\mid Q,y_{<j}).
$$

遮盖式生成则在状态 $s_t$ 中保留已知 token 和 mask，让模型预测尚未提交的位置，再由采样器决定本步提交的集合 $S_t$。同一步生成的两个 token，预测时未必知道对方的具体取值。因此，把它们任意排成一个自回归顺序，会改变条件事件。[DiRL，§2–3][P5]

可以把一次生成理解为“遮盖状态 → 候选预测 → 选择位置 → 更新状态”，重复到填完。生成结果取决于模型，也取决于块长度、置信度阈值、重遮盖策略和采样温度。只报告每步提交了多少 token，不能直接推算端到端加速：每步是否还扫描完整序列、是否需要重建缓存，同样重要。[Sparse-dLLM，算法 1–2][P4]

这里的“扩散”也不能与音画扩散混为一谈。本文讨论离散 token 的遮盖和提交；[MOVA／OmniVAE 专题](03-audiovisual-latents-and-joint-denoising.md)讨论连续潜变量及其噪声过程。共同名称不意味着噪声、训练目标或采样器可以互换。

## 2. 为什么旧 token 没改，旧 KV 仍可能过期？

自回归缓存成立，依赖因果注意力：过去位置不能读取未来新内容。全双向模型不同。即使某个 prefix token 的 ID 不变，它的下一层 hidden state 仍会读取当前块的新内容；因此，更深层的 $K^{\ell+1},V^{\ell+1}$ 可能改变。[Sparse-dLLM，Method][P4]、[attention 实现][C4a]

用简化的层更新表示：

$$
h_i^{\ell+1}=h_i^\ell+
\sum_j a_{ij}^\ell V_j^\ell.
$$

如果新解码位置 $j$ 对旧位置 $i$ 可见，更新 $h_j^\ell$ 就可能更新 $h_i^{\ell+1}$。token 身份固定，没有推出内部状态固定。双向模型照搬 AR 缓存，实际上是在引入近似。

按块生成也不自动解决这个问题。Sparse-dLLM 将全双向模型按块生成，并未把跨块注意力改成严格因果；DiRL 的 SDAR 则采用块间因果、块内双向。两者都出现“块”，但缓存成立的条件不同。[Sparse-dLLM][P4]、[DiRL，§2][P5]

## 3. Sparse-dLLM 实际复用了什么？

它的出发点是：重复去噪时，许多块外状态变化较小，当前块主要依赖的历史位置也有一定稳定性。与其每步重算全部序列，不如先建立块外缓存，再保留其中较重要的部分。[Sparse-dLLM，§3][P4]

论文算法和固定版本源码对应的过程是：

1. 块内第 0 步做全序列前向，暂不缓存。
2. 第 1 步再次全前向，建立块外 prefix 和 suffix 的 K/V 缓存。
3. 用当前块 query 的均值与块外 K 的乘积评分，跨 head 平均，再做邻域 max-pool 和 top-k 筛选。
4. 第 2 步起，只重算当前块，拼接保留的旧块外缓存；换块后重新建立缓存。

默认保留率 $r=0.5$，pool kernel 为 3。评分不是把完整 attention probability 累加，而是先平均 query，再对未 softmax 的分数排序。平均操作省了评分成本，也可能丢掉 query 间的差异。[算法 1–2][P4]、[filter_cache][C4]、[generate][C4b]

这种缓存包含两个独立假设：重要 token 的身份跨 step 稳定；被保留 KV 的数值在复用期也足够稳定。论文图 2 的注意力图和图 4 的相邻步 L2 变化提供了经验观察，不能保证所有输入、层和采样器都满足这两个条件。[P4]

两个简化例子可以分清误差来源。若 attention 始终均匀，但某个 V 从 0 变为 1，其他位置的输出仍会变化：排名没有变，缓存值却过期了。若当前块两个 query 分别为 $q,-q$，均值变成 0，某个 query 特别需要的 key 又可能被筛掉。前者是状态复用误差，后者是重要性筛选误差。

固定 attention 权重时，复用 V 的误差可写为

$$
\Delta o_i=\sum_{j\in C}a_{ij}
\left(V_j^{\rm fresh}-V_j^{\rm cached}\right).
$$

这是局部分析，不是整网误差上界。真实网络还会改变 Q/K、softmax 权重及后续层；缓存筛选本身也会改变归一化。论文没有给出覆盖这些因素的统一误差保证，热图相似因此仍是近似的经验依据。

## 4. 加速的证据要和质量一起读

作者在 LLaDA-Instruct 的 MATH 设置中报告，吞吐由 8.52 提升至 31.72 tokens/s，准确率由 36.02 降至 34.42。这个结果支持缓存和稀疏计算能提高特定工作负载的吞吐，不能解释为无损重现原生成分布。[论文表 1][P4]

延迟建立缓存也是质量与速度的折中。ARC-C 中，缓存延迟从 1 步增加到 3 步，准确率由 88.47 升至 89.49，吞吐由 36.85 降至 35.38。它说明更充分的状态更新可能换来质量，而不是“延迟 1 步已经精度最优”。Dream 的双向与仅 prefix 稀疏方案平均分都为 69.04，各任务有得有失，也不支持双向方案全面占优。[论文表 3–4][P4]

因此，这条路线的研究问题可以落到具体位置：哪些层、哪些时刻、哪些块外状态适合复用；近似省掉的计算是否值得任务准确率的变化。不能只看每秒 token，也不能把缓存误差与后训练中的概率误差合并成一个问题。后者涉及怎样对生成轨迹求梯度，由[DiPO／BandPO 专题](14-post-training-and-rl.md)单独讨论。

## 资料与源码定位

材料核查于 2026-10-17。实验数字来自作者，局部误差式和反例为本文分析；未运行 GPU 实验。

Sparse-dLLM 源码固定于 `3fd8986bee4d`：[CustomCache.filter_cache，542–580][C4]、[attention，765–800][C4a]、[generate，74–126][C4b]。论文采用 v2；长度外推和强化学习论文仅用于机制比较。

[P3]: https://arxiv.org/pdf/2506.14429v3 "LongLLaDA"
[P4]: https://arxiv.org/pdf/2508.02558v2 "Sparse-dLLM"
[P5]: https://arxiv.org/pdf/2512.22234v2 "DiRL"
[C4]: https://github.com/OpenMOSS/Sparse-dLLM/blob/3fd8986bee4ddd68e70ee8041da3a8c9de44f405/opencompass/models/sparse_dllm/modeling_llada.py#L542-L580
[C4a]: https://github.com/OpenMOSS/Sparse-dLLM/blob/3fd8986bee4ddd68e70ee8041da3a8c9de44f405/opencompass/models/sparse_dllm/modeling_llada.py#L765-L800
[C4b]: https://github.com/OpenMOSS/Sparse-dLLM/blob/3fd8986bee4ddd68e70ee8041da3a8c9de44f405/opencompass/models/sparse_dllm/llada_generate.py#L74-L126
