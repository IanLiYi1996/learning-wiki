# 02 表示与解码：小向量、好重构和好生成不是同一目标

核查日期：2026-11-11。[专题导读](README.md) · [表示来源](sources.md#representations)。

## 1. 先问“状态在哪里”，再问模型名称

| 表示 | 简化形状 | 主要问题 |
| --- | --- | --- |
| One-hot | L×V | 易对应 token，但大词表带来高维状态／投影 |
| Binary code | L×ceil(log2 V) | 紧凑；距离依编码，不自动反映语言相似性 |
| Vocabulary embedding | L×d | 可学习／复用几何；需防缩放、坍缩和解码不稳 |
| Contextual embedding | L×d | 每个位置含上下文；需恢复文字和处理生成误差 |
| Compressed latent | M×d，M 可小于 L | 减少重复处理；恢复细节由 decoder 承担 |
| Simplex／sphere | 依构造决定 | 采样器和目标须尊重相应几何 |

L 是 token 数，V 是词表大小，d 是表示维数。表格是教学压缩；不同模型会组合多种设计。原始背景可读 Diffusion-LM、CDCD、ELF 与 Categorical Flow Maps，不能仅从名称判断网络或 sampler 相同。[一手来源](sources.md#representations)

## 2. One-hot 的 denoiser 在 simplex，噪声状态未必在

One-hot 向量是词表的一个顶点。其条件期望是 token 概率的加权和：

$$
D_t(x)^\ell=\sum_{k=1}^{V}p(w_\ell=k\mid x_t=x)e_k.
$$

所以 denoiser 的输出可在概率 simplex 上，由 softmax 参数化。但若状态通过高斯噪声和 one-hot 数据插值，它在周围的欧氏空间演化，不要求每一步都非负且和为一。

不要混淆“输出可解释为概率”与“当前噪声向量就是概率”。直接把 ambient state 每步裁剪为概率向量，会改变过程；需要相应模型和理论支持。[FLM §3.1–3.2](https://arxiv.org/html/2602.16813v3)

## 3. 词向量可以省维度，也会藏捷径

原创反例：两个不同 token 的 embedding 被训练成同一个向量。回归这个向量可以很准，却无法从它分辨两个 token。另一种捷径是把向量范数无限放大，使固定噪声显得很小。

因此要联合检查 token 可恢复性、表示几何、噪声尺度和生成质量。冻结预训练编码器避免一种漂移，但它的空间可能不适合生成；联合训练可适应任务，却需要约束和独立评价。[Diffusion-LM 与 CDCD](sources.md#representations)

编码器对真实文字重构很好，也不保证 decoder 对生成出的、带残留误差的表示稳定。应测试扰动后的重构，以及真正生成状态的解码，而不只测试干净输入。

## 4. Latent 缩短的是哪段序列？

若 512 个 token 压成 32 个 latent，flow 的每次更新可能处理更短的序列。但最后 decoder 可以是自回归，也可以并行；生成长度、词汇细节与推理成本都取决于这个接口。

原创成本框架：

$$
C_{\rm total}=C_{\rm encoding}
 +N_{\rm evaluations}C_{\rm latent\ step}+C_{\rm decoding}.
$$

这是一张费用／计算分解，不是 FLOPs 精确公式。压缩率不能直接当端到端加速倍数；encoder 是否推理必需、decoder 是否 AR、是否有额外 refinement，都要单列。

ELF 主要在连续 contextual embedding 中演化，并使用共享网络的解码模式映射 token；这与“任意压缩 latent 后用另一个 AR decoder”不同。[ELF v3](https://arxiv.org/abs/2605.10938v3)

## 5. Simplex 与 sphere 为什么需要各自的 sampler？

概率 simplex 要非负且和为一。球面要保持单位范数。普通欧氏更新不一定保持这些约束；softmax 后的概率、球面投影和几何感知转移，也不是无代价的同一个操作。

原创建议：先列状态空间、端点、预测空间、更新规则和最终 readout；不要看见概率值就假定对应同一个概率路径。CFM 的两时间 denoiser 为 categorical 目标提供一个接口，但它不要求所有模型采用同一表示。[CFM](https://arxiv.org/abs/2602.12233v1)

## 6. 一个仅算稠密状态的预算

假想 L=128、V=50,000、d=64、每坐标 4 bytes。稠密 one-hot ambient state 为 **25,600,000 bytes**，embedding state 为 **32,768 bytes**。这不是实际模型峰值显存：还未计 logits、投影、attention、梯度、optimizer 或 decoder。

更小表示的名义状态可明显更短，但其 encoder／decoder 和质量代价须另测。动手见[状态预算实验](lab.md)。

下一篇：[03 连续动力学与训练](03-diffusion-and-flow-matching.md)。
