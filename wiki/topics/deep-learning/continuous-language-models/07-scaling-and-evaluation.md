# 07 扩展与评测：训练计算、生成质量和响应时间分开

核查日期：2026-11-11。[专题导读](README.md) · [作者报告与版本](sources.md#evaluation)。

## 1. “缩小计算差距”不是“生成快了二十倍”

RePlaid 报告，在其匹配架构／训练设置的比较中，相对 AR 的 training-compute gap 约为 **20×**，并研究 likelihood、噪声调度和表示。这是达到指定 likelihood 的训练计算口径，不是推理快二十倍。[RePlaid v3](https://arxiv.org/abs/2605.18530v3)

比较规模还需区分从头训练与继承 AR 预训练。只列最终参数量、再忽略继承的模型与数据，不能完成训练资源归因。本文不复制综述的规模表为本地成绩。

## 2. 连续密度，不是离散文本概率

若连续 generator 输出 x，decoder 给出文字 w，离散概率需通过 decoder 汇集概率质量：

$$
p_\theta(w)=\int p_{\rm dec}(w\mid x)p_{\rm cont}(x)\,dx.
$$

在 embedding 处的一个 density 值，不是这句话的 probability。Likelihood bound、ELBO、生成样本的 reference gPPL 又是不同东西。[Plaid](https://arxiv.org/abs/2305.18619v1) · [RePlaid](https://arxiv.org/abs/2605.18530v3)

所以 AR 的廉价 token likelihood ratio 不能未经推导就用于任何连续生成器的 RL。路径转移、最终 marginal 与可微奖励是不同更新接口。

## 3. Generative perplexity 测谁认为文字可预测？

gPPL 常用固定参考 AR 模型给生成样本打分。它不是生成器自身的精确 likelihood，也不直接是事实正确率。

原创二符号 reference：下一符号重复的概率为 0.9，变化为 0.1。全 A 样本的条件 gPPL 为 **1/0.9≈1.111**，样本 unigram entropy 为 **0**；平衡交替样本的 gPPL 为 **10**，entropy 为 **ln 2**。

这个 toy 不是自然语言质量实验，只说明更可预测与更多样可以冲突。真实评测应同时报告采样配置、多样性、重复、分布距离和任务表现，而不是只取最小 gPPL 的一点。[FLM 的 collapse 与实验检查](https://arxiv.org/html/2602.16813v3)

## 4. 单个 entropy 点也不足以证明分布正确

两个方法可以有相似 unigram entropy，却在句子组合、重复模板或跨样本覆盖上完全不同。

建议扫温度、随机性、NFE 与 guidance，比较 quality–diversity frontier；加入适当的分布比较指标和人／程序评价。Feature space、有限样本和 reference 模型也有自己的偏差，不能由某一距离小推出所有文本性质相同。

## 5. 任务正确性需要对应的验证器

| 任务 | 更直接的验收 | 仍然缺什么 |
| --- | --- | --- |
| 程序／可计算答案 | 隔离环境下验证输出与必要约束 | 测试完整性、资源与安全 |
| Sudoku／逻辑谜题 | 行列等约束与完整合法性 | 开放语言和真实任务泛化 |
| 多解任务 | 正确率加有效解覆盖 | 不能只奖励大量重复解 |
| 开放文本 | 内容、分布、多样性和人工标准 | 单指标难覆盖全部要求 |
| 生物序列等应用 | 有效性与任务预测，必要实验验证 | 预测器高分不等于真实功能 |

这些是验收建议。本文不生成或验证生物／医疗候选，不提供实验或临床建议；也不将 puzzle 成绩称为普遍推理能力证明。

## 6. 一个公平的效率合同

固定模型与初始化、数据／词表、长度／块、目标质量、有效输出计数、所有 NFE、guidance／decoder／verifier、硬件／精度／并发、缓存、失败与停止。

分别报告训练总计算、运行显存、每次前向成本、首输出／整段时延、吞吐及质量。尽量比较同质量的 Pareto 前沿，不将更低质量换来的提速描述为无损。

下一篇：[08 安全与研究路线](08-safety-and-research-roadmap.md)。
