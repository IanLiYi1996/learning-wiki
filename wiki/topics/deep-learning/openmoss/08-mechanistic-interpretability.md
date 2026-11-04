# 模型可解释性：解释特征，还是解释计算？

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

模型答对一道算术题，行为测试却未必能告诉我们它是识别了模板，还是采用了能推广的算法。研究者还想知道：哪些信息被读出、怎样传递，改变这条路径后答案是否按预期变化。

激活是高维向量，可读概念未必对应单个神经元。稀疏自编码器（SAE）将激活拆成少量字典方向，试图得到更细的特征；但这些特征容易描述、能重建数值，与能够解释干预结果，仍是不同要求。[^S]

Llama Scope（下文 S）提供稀疏特征资源；维度坍缩论文（A）的 ASI 改善字典初始化；Lorsa（L）近似 attention 的内容传递；CRM（C）组合 attention 与 MLP 替换模块，扩展归因路径。注意力尤其难处理：它既搬运内容，也决定从哪里读取。[^S][^A][^L][^C]

## 1. 稀疏特征能说明什么？

设字典 $D=[d_1,\ldots,d_m]$，编码 $a=\operatorname{ReLU}(W_E x+b_E)$，重建 $\hat x=Dz+b_D$。普通 ReLU SAE 取 $z=a$，优化

$$
\mathcal L_{\mathrm{L1}}=\mathbb E\big[\|x-\hat x\|_2^2+\lambda\|z\|_1\big].
$$

TopK 把稀疏预算放进门控，而非另加 L1 惩罚。Scope 的改法是

$$
M_i=\mathbf1\{i\in\operatorname{TopKIndices}(a_j\|d_j\|_2,K)\},
\quad z_i=M_i a_i,\quad
\mathcal L_{\mathrm{TopK}}=\mathbb E\|x-Dz-b_D\|_2^2.
$$

按“激活×decoder 范数”排序，使入选依据对应输出贡献尺度。Scope 不用复活死特征的辅助损失；训练前 10% 步数把 K 从输入维数退火到目标值。以上是 S §2.2–2.4、§3.3.2 的训练设计，不是因果验证。[^S]

JumpReLU 则为 $z_i=a_i\mathbf1[a_i>\theta_i]$，不是 $\max(0,a_i-\theta_i)$。原始 JumpReLU 训练用重建加 L0 惩罚，借直通估计器处理不连续门控；但 Scope 是先训 TopK，再标定阈值使平均 L0 约为 K，不能把二者写成同一种训练损失。阈值门控允许每个样本使用不同数量的特征，也消除了逐样本 TopK 的直接名额竞争。（S §2.4、§3.3.4；JumpReLU §2–3）[^S][^J]

$$
\mathcal L_{\mathrm{JumpReLU}}
=\mathbb E\big[\|x-Dz-b_D\|_2^2+\lambda\|z\|_0\big].
$$

三目标分别问“用了几个方向”“数值还原得怎样”“改变某个方向后，原模型是否按解释预测变化”。小 MSE 不约束下游敏感方向，也不保证替换模块的 Jacobian 相同；低 L0 更不保证方向语义唯一。Scope 的 ΔLM loss 测试替换对语言模型损失的影响，仍非特征反事实正确率。作者在 S §4 明确把更细的因果评价留给后续工作。[^S]

对 ReLU／贡献尺度 TopK，把 $d_i$ 放大 $c>1$ 倍、对应编码缩小 c 倍，重建及 L0 不变，未经范数修正的 L1 却会减小。因此 decoder 范数不是无关的实现细节。Scope 的贡献尺度门控处理了这种参数化自由度；但固定尺度并未证明字典概念唯一，也没有把重建损失变成干预损失。应另检验同一扰动在原模型与替换模型中的下游变化是否一致。

大字典也不会自动提供更多有效概念。固定 K、扩大 m，会减少均匀使用假设下每单元的平均入选机会 $K/m$；长期未过门控的单元缺少重建梯度，弱方向容易被强方向持续挤出。这是竞争机制，不是“m 大就必然死亡”的定理。A 还发现低秩几何与 Adam 陈旧动量的问题；其“死特征”定义是连续 1000 万 token 不激活。Scope 所称“死亡少见”不能无条件外推到所有位置、字典尺度及检查窗口。（A §3.2、§5.1、§5.3）[^A]

## 2. 字典很大，为什么许多特征没有被用到？

A §4.1 用中心化激活矩阵的奇异值定义

$$
p_i=\sigma_i/\sum_j\sigma_j,\qquad
\operatorname{erank}=\exp(-\sum_i p_i\log p_i).
$$

attention 输出的有效秩比例约 60%，MLP 输出和 residual 约 90%（图 2）。这是谱集中程度，不是“40% 维度严格为零”，也不等于“60% 维度解释 99% 方差”。图 3 的另一指标是 attention 保留 39.1% 主方向可恢复超过 99% 的零消融损失；阈值、度量和分母必须分开。[^A]

作者将 $O=ZW_O$ 沿方向 $e$ 的方差拆成

$$
\operatorname{Var}(Oe)
=\operatorname{Var}(Z\hat v)\|W_Oe\|_2^2,\qquad
\hat v=W_Oe/\|W_Oe\|_2.
$$

§4.4、图 4 支持输出投影 $W_O$ 对谱的进一步压缩。多头输出子空间重叠是作者的机制解释；不能仅凭这项观察断言 softmax 必然使任何 transformer 输出低秩。[^A]

若数据主要落在 r 维子空间 S，均匀随机单位方向 w 的投影能量满足 $\mathbb E\|P_Sw\|^2=r/d$。以 $\Sigma$ 表示协方差，线性编码响应的方差为 $w^\top\Sigma w$：落入低方差方向的初始化更难赢得 TopK，随后更新不足。这个几何模型解释了“容量存在、方向不对”的浪费，但不能从 $r/d$ 单独算出 87% 死亡率。

ASI 用校准激活的 SVD 找到主子空间，将初始 decoder 放进去，再用其转置初始化 encoder。按源码的行存储记号 $B=D^\top\in\mathbb R^{m\times d}$，论文 §5.2／附录 K 写为 $B_0\leftarrow B_0P_S$；固定源码实际用低维随机系数乘主方向，即 $B_0=GV_r^\top$，其中 $G\in\mathbb R^{m\times r}$。二者都实现子空间对齐，但不是逐元素相同的初始化。它不是训练全程强制权重留在子空间，更不是 PCA 截断后的固定模型。[^A][^code-sae]

排除“只是改了初始化规模”的关键证据是附录 J.1／图 12：**相同初始化子空间维数下，随机子空间劣于 SVD 活跃子空间**。附录 E.3 另做初始化范数搜索，报告合理范围内范数影响较小；J.2／图 13 在近满秩 residual 上收益有限。这组结果支持方向对齐，而非仅缩小维数或调整范数；但不是穷尽所有混杂因素的同范数全因子实验。[^A]

主设置表 4 中，32,768 特征、L0=50 的死特征均值从 16,144.33 降到 4，归一化 MSE 从 0.33367 降到 0.31680。1M 字典“87% 降至不足 1%”则是 **ASI＋SparseAdam** 的图 8 结果。附录 I 表 6–7 仍有 ASI 残留死亡，附录 E.4 还指出长期高 L0 会使方向漂离子空间。证据支持可扩展训练改良，不支持“ASI 一步解决全部死特征或解释忠实度”。[^A]

表 6 还有一项相反结果：Llama 第 7 层 AuxK 只有 98 个死特征，ASI 却有 5308 个；但 ASI 的归一化 MSE 为 0.28882，优于 AuxK 的 0.29800。特征死亡更少，并不总能带来更好重建。[^A]

## 3. Lorsa 怎样分开内容和寻址？

按论文输出方向单位范数的参数化，省略偏置与位置变换，令 $g(h)$ 为 head h 所属的共享 QK 组：

$$
A_g=\operatorname{softmax}_{\rm causal}
\left((XW_{Q,g})(XW_{K,g})^\top/\sqrt{d_h}\right),
\quad z_h=A_{g(h)}Xw_{V,h},
$$

$$
\hat Y_i=\sum_{h\in S_i}z_{h,i}w_{O,h},\qquad
S_i=\operatorname{TopKIndices}_h(z_{h,i}).
$$

每个 $w_{V,h}w_{O,h}$ 是 rank-1 OV；QK 仍保留原 head 的维数，并在一组稀疏 heads 间共享。Lorsa 从 attention **输入预测输出**，不像 SAE 从输出重建同一个输出。（L §3.1、算法 1）[^L]

rank-1 OV 使“读什么方向、写什么方向”可以组合：固定路由后，输出方向与后续 encoder 的内积给出通道连接，$A_{ij}v_j$ 给出 z-pattern 的来源贡献。然而语义标签只描述这些方向的统计行为，不是独立程序变量。共享 $A_g$ 的多个内容通道共同使用同一多维地址计算；softmax 又耦合所有候选位置，故“词可组合”不等于“每词有可独立拆开的路由”。

尤其要区分 z-pattern 与裸 attention pattern：前者是 $A_{ij}v_{j,h}$，后者只有 $A_{ij}$。共享同一 A 的两单元，因为 values 不同，仍可显示不同的高亮来源；不同 z 图不能充当独立 QK 的证据。CRM “Lorsa Feature Families” 中的首字母、第二字母、末字母通道，就是复用寻址而专化内容的作者案例。[^L][^C]

L 附录 B.1／图 8 在固定参数预算、K=64、Pythia 两种上下文长度下，降低 QK 维数到原 64 以下显著损害重建，支持保留多维路由的工程选择。附录 B.3／表 3 中，固定原 QK 的 FVU=12.4%，原 QK 初始化后可训练为 11.2%，随机初始化为 11.3%；因此路由并非只复制原 attention 图，但也不能据此证明恢复了唯一“真实路由”。§8 明确承认 shared QK 可能使归因误落到同组其他通道。[^L]

表 1 的 Llama 设置为每层 32K 稀疏 heads、每 token 128 个活跃、512M 参数，原 MHSA 为 64M。它用更多参数换取更细的解释，活跃单元虽少，仍需存储权重和计算 QK。[^L]

## 4. 固定注意力图会漏掉什么？

CRM 为 attention 配 Lorsa、为 MLP 配 transcoder，补上原本隐藏于跨 token 边中的中间节点。其“complete”首先是这两类模块的路径覆盖。局部归因仍冻结 attention pattern、layernorm 分母，并加入 $\epsilon=y_{\rm original}-y_{\rm replacement}$ 误差节点对齐基准 logits。**基准输出精确相等有误差补偿保障，不等于稀疏模块自身零误差。**（C “Complete (Local) Replacement Models”）[^C]

attention 输出 $y_i=\sum_jA_{ij}(X)v_j(X)$ 的变化分两项：

$$
dy_i=\underbrace{\sum_jA_{ij}\,dv_j}_{\text{内容变化}}
+\underbrace{\sum_jv_j\,dA_{ij}}_{\text{路由变化}}.
$$

固定 attention 图只保留第一项。它能解释既定地址上的搬运，不能据此回答“上游特征变了以后为什么换地址”。

冻结图求得的是这些条件固定后的导数。原模型还会改变 attention、layernorm 尺度和 TopK 入选集合，较大干预不能只靠当前图的局部线性关系预测。

**两 token 构造反例，非作者实验：**用一个标量 QK/V head、因果 attention，设

$$
x_1=(0,t,1),\quad x_2=(1,0,0);
\quad W_Q=(1,0,0)^\top,\ W_K=(0,1,0)^\top,\ W_V=(0,0,1)^\top.
$$

第二个 token 有 $q_2=1$、keys 为 $(t,0)$、values 为 $(1,0)$，故

$$
y_2(t)=\frac{e^t}{e^t+1},\quad
y_2(0)=1/2,\quad y_2'(0)=1/4.
$$

只干预 token 1 的 key 坐标，values 不变。冻结 t=0 的 attention 图会预测 $dy_2/dt=0$；真实导数却为 1/4。有限干预 $t=\log9$ 时，真实输出变为 0.9，冻结图仍为 0.5。遗漏的是“改变检索地址”的作用，不是“改变被搬运内容”的作用；即使基准重建完全准确，也可能漏掉这种反事实。

不能因此说 CRM 完全不解释 QK。官网另做 attention score 的双线性 QK tracing，也明确承认单位置分数不能解释 softmax 的相对竞争；只贡献 QK 的特征不显示在主图中。固定 SHA 的 `attribute()` 默认 `enable_qk_tracing=False`，`collect_cache()` detach pattern；独立 QK tracing 不是主图已包含完整 $dA/dX$ 的证明。[^C][^code-attr]

还需保留版本边界：网页称 QK tab 选择 z-pattern 贡献最大位置，当前 `_retrieve_qk_vector_targets()` 实际取 attention **score** 的 argmax。有不同 values 时二者不必一致。报告中的主图、辅助追踪和重新前向运行的 CRM，不能作为同一种对象评价。[^C][^code-attr]

官网的 global weights 定义为数据分布上的期望局部归因，结合静态 virtual weight 与共激活／attention 统计。它不是去掉全部输入条件后的通用算法；作者也承认当前全局图常更像特征聚类，而非端到端算法。“global”不消除上述路由导数边界。（C “Global Weights as Expected Local Attributions”）[^C]

## 5. 三类评价的差别

| 协议 | 实际检验 | 不能替代什么 |
|---|---|---|
| 解释文本 | 用自然语言预测激活／z-pattern，在另一些上下文检验预测 | 原模型反事实机制 |
| reconstruction | 固定字典规模、L0、位置与数据，测误差及替换后的 LM loss | 语义单一性、路由导数 |
| intervention | 在原模型与替换模型做匹配扰动，检验预测变化及传播 | 未测试分布上的完整解释 |

各工作的评价方式如下。

**文本解释。**L §5.3、图 5／附录 I 使用 GPT-4o：8 个高激活上下文生成说明，再预测 4 个高激活与 4 个随机上下文。每分布抽 100 heads/features；同规模 Pythia-160M 模块、12 层的激活和来源模式形成 24 个比较：[^L]

| 显著性口径 | Lorsa 胜 SAE | Lorsa 负 SAE | 未检出显著差异 |
|---|---:|---:|---:|
| t-test，α=0.05 | 6 | 3 | 15 |

作者结论是解释性相当。“15 平”只表示未检出显著差异，不是统计等效性证明；这不是 Llama 所有层的结果，也没有修改任何模型激活。[^L]

**重建。**Scope §4.1 在 5000 万 held-out tokens 上测 L0、EV、ΔLM loss；其式 6 的 EV 分母是 $\|x\|^2$，不应无说明换成中心化总方差。Lorsa §4／图 2–3 比较 FVU，但其预测计算任务比 SAE 的自重建更难。CRM 的 replacement score 衡量误差节点到 logits 的影响，completeness score 衡量重要节点上由可解释来源解释的份额：同预算下前者降低、后者可提高，说明更广路径覆盖仍可能带来更多残余误差。[^S][^L][^C]

**具体干预。**L 附录 D.4 的 `75 ÷ 3 =` 本来输出 25，概率 0.73；把 `Lorsa.15.2668` 的激活置零，将其强度转到 `Lorsa.15.3099`，输出转为 15，概率 0.66。两 head 共享 QK，所以这是 OV 内容通道的因果案例，不是独立路由分解的验证。论文 §6 的 path patching 还限定影响经 residual／MLP 传播，不经其他 attention heads；结果须按这一路径限制解读。[^L]

CRM 的归因图评价限于 8× expansion。用 100 prompts 的逐特征消融，把 logits KL 变化与归因影响排名比较；另取每图最重要 512 特征，检验消融后三层内下游变化。K=64／128／256 的 Pearson 为 0.690／0.691／0.628，transcoder-only 为 0.560／0.587／0.649，因而并非每个设置都胜出。[^C]

其残差扰动还比较 encoder 方向、随机旋转方向及上游特征方向；冻结基准误差节点后重新前向，用下游变化的 cosine／归一化 MSE 检验，encoder／上游激活扰动尺度为 0.1。这比重建更接近因果忠实度，但不能推出任意大干预仍忠实。作者还报告缩写特征互换须放大才能得到 AG→GA，强放大时会出现 G；这说明自我纠正与未覆盖的位置机制仍影响反事实。（C “Mechanistic Faithfulness”“Causal Validation: Reversing Word Order”）[^C]

## 资料与源码定位

源码核查于 2026-10-17，官方 `dev` 固定为 `544b2f93290a`。实验数字来自论文或作者报告，计算反例为本文推导；未运行训练和性能复现。

| 模块／函数 | 核对事项 |
|---|---|
| [SparseDictionary.activation_function_factory / compute_loss](https://github.com/OpenMOSS/Llamascopium/blob/544b2f93290a60cc5dbafb535565592b79a05141/src/llamascopium/models/sparse_dictionary.py#L713)（L713／L841） | TopK 门控；重建、可选稀疏及 AuxK 项。当前通用训练器的可选项不能冒充 Scope 原训练配置 |
| [SparseAutoEncoder.encode / init_W_D_with_active_subspace](https://github.com/OpenMOSS/Llamascopium/blob/544b2f93290a60cc5dbafb535565592b79a05141/src/llamascopium/models/sae.py#L453)（L288／L453） | decoder 范数门控；中心化后 SVD、低维系数乘主方向 |
| [STEFunction.forward / JumpReLU](https://github.com/OpenMOSS/Llamascopium/blob/544b2f93290a60cc5dbafb535565592b79a05141/src/llamascopium/activation_functions.py#L21)（L21／L67） | 执行的是保幅阈值门控；`sparse_dictionary.py:L111` 配置注释误写成 shifted ReLU，以执行代码为准 |
| [Initializer.initialize_sae_from_config](https://github.com/OpenMOSS/Llamascopium/blob/544b2f93290a60cc5dbafb535565592b79a05141/src/llamascopium/initializer.py#L241) | 启用子空间初始化后，另做 initialization_search；方向与范数步骤分开 |
| [LowRankSparseAttention](https://github.com/OpenMOSS/Llamascopium/blob/544b2f93290a60cc5dbafb535565592b79a05141/src/llamascopium/models/lorsa.py#L112)（L462／L743／L811） | OV 活跃子空间初始化、共享 QK 编码、稀疏解码 |
| [collect_cache / attribute / _retrieve_qk_vector_targets / compute_qk_tracing](https://github.com/OpenMOSS/Llamascopium/blob/544b2f93290a60cc5dbafb535565592b79a05141/src/llamascopium/circuits/attribution.py#L456)（L456／L537／L803／L1044） | 冻结 pattern 与尺度；可选 QK 双线性归因；score-argmax 位置选择 |
| [apply_saes / detach_at](https://github.com/OpenMOSS/Llamascopium/blob/544b2f93290a60cc5dbafb535565592b79a05141/src/llamascopium/circuits/hooks.py#L21)（L21／L73） | 重建加 error 保持前向；detach 切断指定梯度路径 |

[^S]: Zhengfu He 等，*Llama Scope: Extracting Millions of Features from Llama-3.1-8B with Sparse Autoencoders*，2024，arXiv `2410.20526v1`。[开放全文](https://arxiv.org/html/2410.20526v1)。定位：§2.2–2.4、§3.3、§4.1–4.3。
[^L]: Zhengfu He、Junxuan Wang 等，*Towards Understanding the Nature of Attention with Low-Rank Sparse Decomposition*，ICLR 2026；arXiv `2504.20938`。[正式开放 PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/7e57d4c3bb2bd2396a551e7aeea19aed-Paper-Conference.pdf)。本文章节／表号按正式版：§3–6、§8；表 1／3，图 5／8，附录 B／D／I。
[^A]: Junxuan Wang 等，*Dimensional Collapse in Transformer Attention Outputs: A Challenge for Sparse Dictionary Learning*，arXiv `2508.16929v4`，2026-02-11。[开放全文](https://arxiv.org/html/2508.16929v4)；[ICML 2026 正式记录](https://proceedings.mlr.press/v306/wang26bh.html)。本文数字按 v4：§4–5，图 2–4／8／12–13，附录 E／I／J／K，表 4／6–7。
[^C]: Wentao Shu、Xuyang Ge 等，*Bridging the Attention Gap: Complete Replacement Models for Complete Circuit Tracing*，2026，OpenMOSS 作者官网报告。[全文](https://interp.open-moss.com/posts/complete-replacement)。按页面章节标题定位；不是此处已确认的独立 arXiv／会议论文。
[^J]: Senthooran Rajamanoharan 等，*Jumping Ahead: Improving Reconstruction Fidelity with JumpReLU Sparse Autoencoders*，2024，arXiv `2407.14435v1`。[原始方法全文](https://arxiv.org/html/2407.14435v1)。仅用于核对 JumpReLU 定义、L0 目标与梯度估计。
[^code-sae]: [固定 SHA 的 SAE 子空间初始化](https://github.com/OpenMOSS/Llamascopium/blob/544b2f93290a60cc5dbafb535565592b79a05141/src/llamascopium/models/sae.py#L453)。
[^code-attr]: [固定 SHA 的 attribution 实现](https://github.com/OpenMOSS/Llamascopium/blob/544b2f93290a60cc5dbafb535565592b79a05141/src/llamascopium/circuits/attribution.py#L456)。
