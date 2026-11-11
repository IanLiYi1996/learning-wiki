# 连续语言模型：原始来源、版本与证据边界

核查日期：2026-11-11。以下区分作者综述、原始研究、动态目录与本 Wiki 的原创推导。没有运行来源中的模型或 benchmark，没有下载权重；不将平台 AI overview 当原论文。

<a id="survey"></a>

## 1. 用户提供的论文是什么？

**A Survey on Continuous Diffusion and Flow Language Models**，作者 Sophia Tang、Chanhyuk Lee、Floor Eijkelboom、Jinwoo Kim。平台将该版本标为 **alphaXiv Exclusive、v1、2026-11-08 提交**；作者项目与论文目录于 **2026-11-09** 公告。PDF 共 37 页，文献截止日为 **2026-11-02**。[论文页](https://www.alphaxiv.org/abs/2611.continuous-diffusion-flow-language-models) · [实际 PDF](https://www.alphaxiv.org/abs/2611.continuous-diffusion-flow-language-models.pdf) · [作者项目](https://continuous-lm.github.io/) · [作者主页](https://sophtang.github.io/)

`2611.continuous-diffusion-flow-language-models` 是该平台的标识，不是已经确认的标准 arXiv 编号。本次页面 scholar 元数据的 `arxivId` 为 null，作者 BibTeX 也采用 alphaXiv；不从泛化的 JSON-LD publisher 字段推定它已在 arXiv 发布。也未确认正式会议／期刊出版身份。

本读本主要使用 PDF §2～§8：机制定义、表示、训练、推理、少步、扩展、评测与开放问题；公式重点核对 §2.4、§5.1～§5.2。作者目录用于定位原始工作，不表示独立验证全部收录模型。

## 2. 十项核心来源

| 编号 | 原始来源与本次版本 | 主要用途 |
| --- | --- | --- |
| S1 | 上述综述的 alphaXiv v1 | 阅读地图与领域问题，不是一篇新模型实验报告 |
| S2 | [作者论文集合，固定 README](https://github.com/sophtang/Awesome-Continuous-Language-Models/blob/bbe5f932364c8f9097516979ddc0e69bb2a99709/README.md) | 定位模型、原始论文与八类目录；不是统一运行的排行榜 |
| S3 | Li 等：[Diffusion-LM，2205.14217v1](https://arxiv.org/abs/2205.14217v1) | 连续词向量、去噪与梯度可控生成的早期实例 |
| S4 | Dieleman 等：[CDCD，2211.15089v3](https://arxiv.org/abs/2211.15089v3) | Categorical 数据的连续 diffusion、CE 接口与 time warping |
| S5 | Lipman 等：[Flow Matching，2210.02747v2](https://arxiv.org/abs/2210.02747v2) | 条件概率路径与 simulation-free velocity 回归的基础 |
| S6 | Lee 等：[FLM／FMLM，2602.16813v3](https://arxiv.org/abs/2602.16813v3)；[已读 HTML](https://arxiv.org/html/2602.16813v3) | One-hot flow、联合生成、两时间 denoiser、蒸馏与实验接口 |
| S7 | Roos 等：[Categorical Flow Maps，2602.12233v1](https://arxiv.org/abs/2602.12233v1) | Categorical flow map 与 endpoint consistency 的另一条原始方法 |
| S8 | Gulrajani、Hashimoto：[Plaid，2305.18619v1](https://arxiv.org/abs/2305.18619v1) | Likelihood、decoder 与连续生成的缩放背景 |
| S9 | Yang 等：[RePlaid，2605.18530v3](https://arxiv.org/abs/2605.18530v3) | 匹配架构／训练条件的 likelihood 与 training-compute 比较 |
| S10 | Hu 等：[ELF，2605.10938v3](https://arxiv.org/abs/2605.10938v3) | Contextual embedding、共享解码与连续 flow 接口 |

S2 快照提交时间为 2026-11-10 UTC；这里固定已核验 revision，不把之后的目录更新混入。S10 的 v3 修订于 2026-11-05，晚于 S1 文献截止日；它是本读本在核查日继续追踪的原始版本，不声称 S1 已采用该版全部新结果。

<a id="representations"></a>

## 3. 表示：哪些事实与哪些判断？

S3、S4、S6、S7、S10 支持表示和目标接口的不同实例：embedding、one-hot 或 contextual features，不应该只凭都叫 diffusion／flow 就合并实现。

L×V、L×d 与 M×d 的账本、两个 token embedding 相同的反例，以及小数组状态预算是本 Wiki 的教学分析。它们只比较声明的稠密表示，不重建实际训练显存、decoder 代价或真实模型质量。

<a id="dynamics"></a>

## 4. 动力学：需要保留的假设

S5 提供 Flow Matching 的条件路径学习框架；S6 §3 给出 one-hot 数据的 flow 和 denoiser 关系。本文以噪声 t=0、数据 t=1 为统一约定；不同论文有相反时间方向，参数化不能直接照搬。

条件均值、velocity、score 的转换依路径与噪声分布；精确联合分布讨论还需正确学习、精确积分和能辨识 token 的表示。不能写成“任何连续网络自动保留所有依赖”。ODE `dx/dt=x` 和二符号联合反例由本 Wiki 构造。

<a id="maps"></a>

## 5. 少步：不是一个通用 loss

S6 的 FLM／FMLM 和 S7 的 CFM 是不同原始工作。两时间 map、对角监督、semigroup／其他一致性目标要按原文解释；不能因为都能 one-step 就推定 teacher、feedback、guidance 和目标完全相同。

恒等映射满足 semigroup 却不等于所需 flow，是本 Wiki 的基本反例。它说明“只测组合一致”不是完整验收，不是重新测得某个模型 collapse。额外 readout／guidance／decoder 的 NFE 算例也是原创。

<a id="evaluation"></a>

## 6. 规模与评测：不转录成无条件速度结论

S8 与 S9 比较 likelihood 与训练计算；S9 报告的约 20× 是匹配设置中相对 AR 的 training-compute gap，不能写成生成提速或总体账单收益。不同初始化、数据、训练阶段和继承的 AR 权重须分别记录。

S6 的实验含 gPPL、entropy、collapse 检查与任务评价；单次最好分数不等于统一质量–多样性排名。二符号 reference 的 gPPL／entropy 是教学玩具，不是 GPT-2、OpenWebText 或 MAUVE 的本地复现。

正文的研究清单与安全建议来自对接口的分析，没有完成真实语言模型训练、GPU profiling、用户任务或连续轨迹的安全审计。本文保留这些限制，不将作者自报改写成独立认证。
