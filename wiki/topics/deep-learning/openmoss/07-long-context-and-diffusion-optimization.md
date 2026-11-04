# 长上下文与注意力架构：长度、位置和检索为什么是不同问题

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

长文档和代码库带来两个问题：模型能否利用远处信息，以及处理这些信息要花多少计算。支持更长输入，只解决了容量问题；找到了答案字样，也未必理解了它与其他内容的关系。

ReAttention 从历史中选择片段，NTK 类方法调整位置编码频率，RoPE++ 改变注意力的读出结构。LongLLaDA 则研究扩散模型在长度外推时的表现。它们解决的环节不同，检索、问答与预测损失也可能给出不同结论。[ReAttention][P1]、[RoPE++][P2]、[LongLLaDA][P3]

这里关注“输入更多信息后，模型能否用对它”。扩散生成的缓存复用见[扩散语言模型专题](13-diffusion-language-models.md)，生成轨迹与概率更新见[后训练专题](14-post-training-and-rl.md)。它们影响计算和训练，不应混作位置外推方法。

## 1. 位置重编码与频率外推

NTK 保留完整序列并调整旋转频率；ReAttention 先选择历史片段，再对选后的序列编码位置。两者改变了不同的距离关系。下面先统一 RoPE 的符号，再看这种区别。

采用源码的二维旋转 $R(\phi)=\begin{pmatrix}\cos\phi&-\sin\phi\\\sin\phi&\cos\phi\end{pmatrix}$。第 $n$ 对维度记 $\tilde q=q_0+iq_1,\tilde k=k_0+ik_1$，令

$$
a=q_0k_0+q_1k_1,\quad b=q_0k_1-q_1k_0,\quad
\phi_n=\theta_n(t-s).
$$

有 $\tilde q\overline{\tilde k}=a-ib$。为了同时匹配 RoPE++ 的向量式与代码，定义

$$
C_n=\overline{\tilde q}\tilde k e^{-i\phi_n}
=(a+ib)e^{-i\phi_n},\qquad
S_R=\sum_n(a\cos\phi_n+b\sin\phi_n),\quad
S_I=\sum_n(a\sin\phi_n-b\cos\phi_n).
$$

于是 $S_R=\sum\operatorname{Re}C_n,\ S_I=-\sum\operatorname{Im}C_n$。每对的相位是 $\arg\tilde k-\arg\tilde q-\phi_n$，模长满足 $|C_n|=\|q\|\|k\|$；多频率求和后不能把它们替换成一个统一相位。以上是自洽的简化推导，省略注意力的 $1/\sqrt d$。[P2] 附录 B、[C2]

**原文存在可验证的不一致。** RoPE++ 式(1)、(2)、(4)写的是 $\tilde q\overline{\tilde k}e^{-i\phi_n}$，却展开成上面的 $S_R,S_I$。按附录的 $+i$ 定义，这不成立：取 $t=s,q=(1,0),k=(0,1)$，原文复数式的负虚部是 $+1$，式(3)和代码却是 $-1$。交换共轭即可得到上述自洽表达，但作者究竟意图修改哪项，未知；这里不把修正写成作者公式。[P2] 式(1)–(4)、[C2]

ReAttention 的推理步骤是：①缓存本层未旋转的历史 K/V，用未旋转 QK 做 top-k；②合并各查询／头命中的邻近 span，去重并按原时间顺序排序，保留全局和局部片段；③对选后序列重新施加 RoPE，再做普通注意力。默认预算为 $32+4096+127\times32=8192$。这里“不带 position”只指本层检索未直接乘 RoPE，不代表隐藏状态完全无位置信息，也不是重新前向计算全部历史 hidden states。[P1] §2–3、[C1]

设选后索引映射为 $g$，最后使用 $\theta_n[g(t)-g(s)]$。NTK 则保留完整序列、改变频率 $\theta_n$，不删 token、不把原距离改成选后秩差。内容相关且不连续的 $g$ 不能等同于统一频率缩放；实现里可选带 PE 的检索或原始位置，也不意味着默认方法就是 NTK。全历史缓存仍线性增长，扫描检索也仍依赖历史长度。[C1]

例如，检索保留了答案，却删掉唯一承载关系的 KV，本层仍无法利用这条关系。论文表 4 的 16K MultiKey3 中，ReAttention 为 15，Dynamic NTK 为 95；这类失败不能只用位置外推解释。文中的 t-SNE 图提示自然文本与混乱文本有所不同，但没有证明检索总能选对。[P1] §4、附录 E

## 2. RoPE++ 怎样复用实部和虚部？

令 $J=R(-\pi/2)$，则

$$
S_I=(R_{\Theta,t}Jq)^\top R_{\Theta,s}k
=(Jq)^\top R_{\Theta,s-t}k.
$$

这是线性代数恒等式：负虚部 head 共享原 Q/K 投影，只额外旋转 query；源码使用 `q*sin-rotate_half(q)*cos`，再把实／虚 query 交错排列。两组分数分别 softmax、分别读取同一 V，所以不是把虚部加进一个实部 score。它也不等于两套独立可训练 $W_Q,W_K$：第二套受 $J$ 约束。[C2]

EH 保持输出 head 数，将投影 Q/K/V head 数减半，KV cache 减半；EC 保持投影与 cache，输出 head 数翻倍，`o_proj` 输入宽度随之翻倍。EH 没有把整个模型参数减半，EC 也不是等 FLOPs／等训练时间。公平比较至少固定 head dimension、KV head 数／GQA、精度、长度、训练 token 和优化器，另报输出投影参数、吞吐和峰值内存。主表只能回答对应的资源约束，不能据“同 cache”推出同计算成本。[P2] §3.3、[C2]

训练上，它需架构预训练，不是普通模型的推理插件：正文采用 DCLM、4K/50B token，再增大 rotary base 做32K继续训练。继续训练量正文写10B，表2、6标题写5B；无法据此核定每个发布 checkpoint 的实际预算。表11的776M/32K训练吞吐为 RoPE 29019.6、EH 29399.3、EC 22631.1 tokens/GPU/s，直接说明 EC 的 cache 优势不等于速度优势。[P2] §4.1、表11

表6另有统计口径缺口：BABILong 的 RoPE／EH／EC 表列 Avg 为29.5／32.9／22.9，六长度分数的算术均值却为24.98／27.00／19.38。本次复算确认不相等，但无法确定是排版还是加权定义问题；下表改用32K单点，不自行替作者改平均分。[P2] 表6

实／虚读出保留不同双线性项，但长依赖收益仍取决于学得的 QK。附录用随机向量建立的平均曲线不能代表任意模型；单频 $d=2$ 时 $c_I(\Delta)=\sin\Delta$，在 $\Delta=3\pi/2$ 为负，也说明不能把平均性质推广为无限距离上的普遍正性。[P2] §3.2、附录 B、D

## 3. LongLLaDA 的稳定 PPL 说明了什么？

长度 $L$ 下，双向注意力确实覆盖 $\Delta=t-s\in[-(L-1),L-1]$，因果注意力只覆盖非负一侧；这是 mask 几何的证明，不是模型能力证明。双向覆盖增加了相位的符号样本，却没把最大绝对距离 $L-1$ 加倍。[P3] §3

作者用正负位置覆盖解释 OOD 下相对稳定的 QK／PPL，又用 cosine 偶性解释局部检索。但完整 RoPE score 同时含 $b\sin\phi$，不是只有偶函数：取 $a=0,b=1$，正负距离的分数就反号。因此，“双向→稳定 PPL”的因果关系仍是机制假说；不同基座、训练数据和 base 的比较及二维 t-SNE，不能单独排除其他原因。[P3] 图3–5；第 1 节的简化反例

现有比较同时涉及基座、数据和 rotary base 的差异，尚不能分开估计双向性与这些因素的贡献。

测量本身也不同：`get_ppl` 随机遮盖后续 64-token 答案，未遮盖部分可以从右侧提供信息；AR 脚本只使用左前缀。因此稳定 PPL 说明遮盖预测任务没有崩溃，不能单独证明远处证据被利用。[C3]

LongLLaDA 的推理修改是加载时令 $\beta'=\lambda\beta_0$，保留原索引，并继续分块、置信度选 token 的去噪。[C3] 附录式(4)–(6)给出的周期启发式为

$$
d_{\rm extra}=2\left\lceil\frac d2\log_{\beta_0}\frac{T_{\rm train}}{2\pi}\right\rceil,\qquad
\lambda(t)=\beta_0^{-1}\left(\frac t{2\pi}\right)^{d/d_{\rm extra}}.
$$

对 $\beta_0=500000,d=128,T_{\rm train}=4096$，$d_{\rm extra}=64$，8K所需系数约3.40，向上取4。正文式(1)却保留 $10^{-4}$，代入会得到约170，而非4；此处采用附录，不静默抄正文。这个周期条件不是检索成功率定理：图6–7中 $\lambda=31$ 已出现中间遗失，55不能继续有效外推。[P3] §4、附录 A

## 4. 实验怎样区分容量、检索和推理？

| 控制设置／来源 | 观测变化 | 不能推出的结论 |
|---|---|---|
| ReAttention，LLaMA3-8B，16K，表4 [P1] | NTK→ReAttention：Single3 91→94；MultiKey3 95→15 | 查针成功即多键关联成功 |
| RoPE++ 776M，RoPE→EH，表2 [P2] | RULER均值27.4→28.6；BABILong 22.8→19.4 | 半 cache 无质量代价 |
| RoPE++ 1.5B，RoPE→EC，表6 [P2] | RULER均值35.1→37.5；BABILong/32K 18.5→12.6 | 双 head 全任务提升 |
| LongLLaDA Base，16K，λ14→31，表2 [P3] | NIAH 85.4→97.2；QA 54→41 | 最佳检索 scaling 也是最佳 QA scaling |

这些工作不能用一个“支持多少 K”的数字排序。ReAttention 需要同时检查检索预算与关系证据是否被删；RoPE++ 要交代共享投影、缓存和输出计算的变化；LongLLaDA 则要区分遮盖预测损失、查针和真实问答。能装下的长度、能找到的证据与能完成的推理，分别对应不同实验。

## 资料与源码定位

材料核查于 2026-10-17，源码链接固定到下列提交。实验数字来自作者，代数例子为本文计算；未运行 GPU 实验。文中公式差异尚无作者勘误，源码版本与论文训练检查点的逐项对应也未确认。

| 仓库／完整 SHA | 已核对函数和行号 |
|---|---|
| ReAttention `a62514f169d8` | [DynamicCache.update，539–655][C1]；[recall_operation_for_full，531–537][C1a]；[LlamaAttention.forward，361–367][C1b] |
| rope_pp `91ba3357c49b` | [LlamaAttention.__init__，195–239][C2a]；[apply_rotary_pos_emb，241–277][C2]；[forward，290–327][C2b] |
| LongLLaDA `7244e0991597` | [_load_model，179–195][C3a]；[get_ppl，66–96][C3]、[main，115–129][C3b]；[AR main，29–35][C3c]；[generate，71–107][C3d] |

[P1]: https://arxiv.org/pdf/2407.15176v3 "ReAttention，正文与附录"
[P2]: https://arxiv.org/pdf/2512.07525v1 "RoPE++，正文与附录"
[P3]: https://arxiv.org/pdf/2506.14429v3 "LongLLaDA，正文与附录"
[C1]: https://github.com/OpenMOSS/ReAttention/blob/a62514f169d821fadf962e51aad24c4e5a1643db/re_attention/cache_utils_v0921.py#L539-L655
[C1a]: https://github.com/OpenMOSS/ReAttention/blob/a62514f169d821fadf962e51aad24c4e5a1643db/re_attention/cache_utils_v0921.py#L531-L537
[C1b]: https://github.com/OpenMOSS/ReAttention/blob/a62514f169d821fadf962e51aad24c4e5a1643db/re_attention/re_attention_llama3_1.py#L361-L367
[C2]: https://github.com/OpenMOSS/rope_pp/blob/91ba3357c49beb22e132ed096557baee503f3486/rope_pp/modeling_llama_rope_pp.py#L241-L277
[C2a]: https://github.com/OpenMOSS/rope_pp/blob/91ba3357c49beb22e132ed096557baee503f3486/rope_pp/modeling_llama_rope_pp.py#L195-L239
[C2b]: https://github.com/OpenMOSS/rope_pp/blob/91ba3357c49beb22e132ed096557baee503f3486/rope_pp/modeling_llama_rope_pp.py#L290-L327
[C3]: https://github.com/OpenMOSS/LongLLaDA/blob/7244e09915972ed3d8e92c713889a53e82147caf/ppl/get_ppl_llada.py#L66-L96
[C3a]: https://github.com/OpenMOSS/LongLLaDA/blob/7244e09915972ed3d8e92c713889a53e82147caf/llada/llada_wrapper.py#L179-L195
[C3b]: https://github.com/OpenMOSS/LongLLaDA/blob/7244e09915972ed3d8e92c713889a53e82147caf/ppl/get_ppl_llada.py#L115-L129
[C3c]: https://github.com/OpenMOSS/LongLLaDA/blob/7244e09915972ed3d8e92c713889a53e82147caf/ppl/get_ppl_llama.py#L29-L35
[C3d]: https://github.com/OpenMOSS/LongLLaDA/blob/7244e09915972ed3d8e92c713889a53e82147caf/llada/llada_generate.py#L71-L107
