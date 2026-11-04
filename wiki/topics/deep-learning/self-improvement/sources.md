# 自我改进：来源与证据边界

证据截止：2026-10-17。Wiki 整理：2026-11-04。

[专题首页](README.md) · [概念与基础](concepts-and-foundations.md) · [智能体演化](agent-evolution.md) · [学习与权重](learning-and-weights.md) · [算法与基础设施](algorithms-and-infrastructure.md) · [科学家智能体](ai-scientists.md) · [产业与自动实验](industry-and-autoresearch.md) · [评测与安全](evaluation-and-safety.md) · [研究路线](research-roadmap.md) · [术语表](glossary.md) · [实验练习](lab.md)

本页整理既有研究材料及其 49 组公开引用，不补入截止日之后的进展。整理日期只表示编排时间：本轮没有重新访问论文、核验产品现状或运行实验。下列成绩和开放性记录沿用原材料，不是独立复现结果。来源编号保留原有对应关系；一组可能含多篇论文，不能把 49 组理解为 49 项成功实验。

## 怎样使用这些来源

正式发表、预印本和公司自报回答的是不同问题。会议或期刊论文接受过相应的研究审查；预印本是作者公开的方法与实验，接收状态需另有依据；公司发布、系统卡和官方仓库是第一方记录，可以说明研发参与或公开流程，却不能充当独立性能认证。arXiv 链接也不意味着工作必然未发表，目录只列原材料确认的状态。

同行评审不等于无关联团队完整复现。代码公开、权重公开、训练数据公开和核心服务可离线运行，也不是同一回事。论文内部的多种子重复、合作实验室验证与独立复现，应分别记录。尤其是科学家系统，公开分析脚本未必包含核心引擎；服务依赖和许可差异会限制可复现范围。

阅读时先确定它改了什么：答案、提示词、工具程序、权重，还是产生下一次修改的方法。任务分数上升可以支持局部优化，但不能单凭这一点确认改进器变强，更不能确认持续自加速。理论文献提供条件论证；算法发现提供可执行验证；产业记录提供应用线索。把它们放在一起有助于提出研究问题，不宜合成一个“RSI 已实现”的总分。

## 转述结果前要保留的限定

这些限定与后面的编号共同使用，具体实验解读见相应章节。

- [DGM（12）](#source-12)：采用 v3。SWE-bench 的 20.0%→50.0% 来自分阶段评价、最高扩展到 200 题，不能当成完整 500 题成绩。演化诊断含私有测试补丁信息，成本也不同；应分开解释演化内收益和未参与演化的迁移结果。
- [SEAL（13）](#source-13)：采用 v2。ARC 的 72.5% 对 20% 是 8 道筛选题、每题 5 个 self-edit、共 40 次配置试验的成功比例，不是完整 ARC 题目通过率。一次适应成功还需与多轮遗忘结果一起读。
- [Hyperagents（20）](#source-20)：迁移同时带入 task agent 与 meta agent，且初始数学评分程序有格式和解析问题。收益不能全归于改进器或数学能力；继续演化后的差异不显著，也不支持优势必然复合。
- [AIDE²（21）](#source-21)：研究效率与 ignition test 是两项证据。后者每组仅三次独立运行，作者未得到确定的自加速优势；不能写成已经“点火”。
- [Sakana（43）](#source-43)：三篇人工筛选稿件中，一篇达到 workshop 首轮门槛，随后按协议撤回，没有最终 meta-review。Nature 正式论文是人类作者对系统的研究，不是 AI 自撰稿件发表于 Nature。
- [Co-Scientist（44）](#source-44)与 [Robin（45）](#source-45)：人设定目标、筛选候选并承担湿实验。Robin 还需人把实验概要转成协议，完成培养、测序和部分预处理。内部排名或体外验证不能外推临床疗效，也不能称无人实验室。
- [Kosmos（46）](#source-46)：主系统证据按预印本处理。Nature 内容授权不是技术论文发表；79.4% 的单位是抽查陈述，“六个月研究”是合作科学家的时间估计。
- [M2.7（48）](#source-48)：内部性能“提高 30%”不能改写成提高 30 个百分点。指标、基线和不确定性披露不足；两篇同公司同文页面不是两份独立验证。

评测还有几种常见误读：[MLE-bench（17）](#source-17) 的 pass@8 是多次尝试的统计，不是八轮递归学习；[RE-Bench（18）](#source-18) 的归一化分数不是通用智能倍数；[GEA（24）](#source-24) 的 Polyglot 高分对应 medium 子集；[MetaShare（25）](#source-25) 更早出现最佳版本，不等于更快达到同一目标，部分任务总 token 反而增加。[奖励过度优化（34）](#source-34) 中的 gold reward 仍有模型误差；[模型崩溃研究（33）](#source-33) 也不能脱离数据替换、累积方式推导所有合成数据循环必然失败。

## 分组来源目录

每行保留一组来源编号。带版本号的链接沿用所读版本；无版本号的网页、论文入口和仓库可能变化，不代表已冻结完整快照。以下六组是阅读分类，不是证据强弱排行榜。

### 学术基础与学习机制

对应[概念与基础](concepts-and-foundations.md)、[学习与权重](learning-and-weights.md)。

| 编号 | 公开一手来源 | 状态或使用范围 |
| --- | --- | --- |
| <a id="source-2"></a>2 | Good，[Speculations Concerning the First Ultraintelligent Machine](https://vtechworks.lib.vt.edu/server/api/core/bitstreams/a5e423ee-54e0-4eec-aeca-32b73f851af5/content) | 原始重印节选，仅第 31–33 页；采用 1965，索引有年份差异 |
| <a id="source-3"></a>3 | Schmidhuber，[Gödel Machines](https://arxiv.org/abs/cs/0309048) | 2003 首发、2006 修订；形式保证依赖公理及证明搜索 |
| <a id="source-4"></a>4 | Leike、Hutter，[On the Computability of AIXI](https://arxiv.org/abs/1510.05572)；[Bad Universal Priors and Notions of Optimality](https://arxiv.org/abs/1510.04931) | 2015；计算性、先验与最优性边界，不是现实 RSI 的统一上限 |
| <a id="source-5"></a>5 | [Learning to learn by gradient descent by gradient descent](https://arxiv.org/abs/1606.04474)；[Self-Referential Weight Matrix](https://arxiv.org/abs/2202.05780)；[Self-Referential Meta Learning](https://arxiv.org/abs/2212.14392) | 2016／2022 作者稿入口；更新规则、快速权重与自指学习 |
| <a id="source-8"></a>8 | Zelikman 等，[STaR](https://arxiv.org/abs/2203.14465) | 2022；正确答案参与推理材料筛选 |
| <a id="source-13"></a>13 | Zweiger 等，[Self-Adapting Language Models（SEAL）](https://arxiv.org/html/2506.10943v2) | 2025，v2；学习材料与适应配置的内外循环 |
| <a id="source-14"></a>14 | Zhao 等，[Absolute Zero（AZR）](https://arxiv.org/abs/2505.03335) | 2025；零人工训练示例不等于没有预训练和执行器反馈 |
| <a id="source-15"></a>15 | Yuan 等，[Self-Rewarding Language Models](https://arxiv.org/abs/2401.10020) | ICML 2024；有限迭代，仍有外部数据和评价锚点 |
| <a id="source-28"></a>28 | Peng 等，[VisionHOPE](https://arxiv.org/html/2609.33325v1) | 2026 预印本，v1；图像内局部自修改，计算量比较不等算力 |
| <a id="source-37"></a>37 | Finn、Abbeel、Levine，[MAML](https://proceedings.mlr.press/v70/finn17a.html) | ICML 2017；学习适合少步适应的初始参数 |
| <a id="source-38"></a>38 | Duan 等，[RL²](https://arxiv.org/abs/1611.02779) | 2016 预印本入口；不补写未确认的接收状态 |
| <a id="source-39"></a>39 | Guo 等，[DeepSeek-R1，Nature 正式论文](https://www.nature.com/articles/s41586-025-09422-z)；[首次预印本](https://arxiv.org/abs/2501.12948)；[官方模型入口](https://github.com/deepseek-ai/DeepSeek-R1) | 2025；权重公开不等于完整训练代码与全部数据公开 |

### 智能体演化与元改进

对应[智能体演化](agent-evolution.md)、[研究路线](research-roadmap.md)。

| 编号 | 公开一手来源 | 状态或使用范围 |
| --- | --- | --- |
| <a id="source-1"></a>1 | Madaan 等，[Self-Refine](https://arxiv.org/abs/2303.17651)；Shinn 等，[Reflexion](https://arxiv.org/abs/2303.11366) | 2023 作者稿入口；输出细化、语言反思与记忆 |
| <a id="source-6"></a>6 | Fernando 等，[Promptbreeder](https://arxiv.org/abs/2309.16797) | 2023 首发／ICML 2024；任务提示与变异提示共同演化 |
| <a id="source-7"></a>7 | Zelikman 等，[Self-Taught Optimizer（STOP）](https://arxiv.org/abs/2310.02304) | 2023 首发／COLM 2024；代码改进器自修改 |
| <a id="source-9"></a>9 | Hu 等，[Automated Design of Agentic Systems（ADAS）](https://arxiv.org/abs/2408.08435)；[正式会议记录](https://iclr.cc/virtual/2025/poster/28073) | 2024 预印本／ICLR 2025；固定元搜索设计 agent |
| <a id="source-10"></a>10 | Robeyns、Szummer、Aitchison，[A Self-Improving Coding Agent（SICA）](https://arxiv.org/html/2504.15228) | 2025；SWE-bench 为 50 题子集，模型来源与成本随设置变化 |
| <a id="source-11"></a>11 | Yin 等，[Gödel Agent](https://aclanthology.org/2025.acl-long.1354/) | ACL 2025；不受约束设置部分收益来自更强模型 |
| <a id="source-12"></a>12 | Zhang 等，[Darwin Gödel Machine（DGM）](https://arxiv.org/html/2505.22954v3) | 2025 首发，采用 v3；档案搜索与分阶段评价 |
| <a id="source-20"></a>20 | Zhang 等，[Hyperagents](https://arxiv.org/pdf/2603.19461v1) | 2026 预印本，v1 PDF；保留 HTML／PDF 日期呈现差异 |
| <a id="source-21"></a>21 | Srikanth 等，[Recursive self-improvement of AI research agents（AIDE²）](https://arxiv.org/html/2609.26457v1) | 2026 预印本，v1；研究效率改善与自加速未定分别记录 |
| <a id="source-22"></a>22 | Liu 等，[EvoX](https://arxiv.org/html/2602.23413v2) | 2026 预印本，v2；解搜索与策略搜索分层 |
| <a id="source-23"></a>23 | Zheng 等，[Dream-RSI](https://arxiv.org/html/2609.14858v2) | 2026 预印本，v2；回放历史优化探索，发布计划不等于实现已公开 |
| <a id="source-24"></a>24 | Weng 等，[Group-Evolving Agents（GEA）](https://arxiv.org/html/2602.04837v1) | 2026 预印本，v1；跨分支共享经验，基准子集需保留 |
| <a id="source-25"></a>25 | Bhutani 等，[MetaShare](https://arxiv.org/html/2610.21887v1) | 2026 预印本，v1；workshop 接收为作者自报，非主会认证 |
| <a id="source-26"></a>26 | Lee 等，[Meta-Harness](https://arxiv.org/html/2603.28052v1) | 2026 预印本，v1；外层 proposer 固定，部分评测未独立留出 |
| <a id="source-27"></a>27 | Lu 等，[AREX](https://arxiv.org/html/2607.21461v3) | 2026 预印本，v3；答案与研究状态循环，不是训练算法自改写 |
| <a id="source-29"></a>29 | Hambardzumyan 等，[AIRA₂](https://arxiv.org/html/2603.26499v2) | 2026 预印本，v2；稳定评价与多 worker，资源比较需分开 |
| <a id="source-30"></a>30 | Hou 等，[Learn Like Humans（MARS）](https://aclanthology.org/2026.acl-long.1329/) | ACL 2026；主要是一轮离线增强 |
| <a id="source-31"></a>31 | Kakade 等，[POLARIS](https://aclanthology.org/2026.findings-acl.1969/) | Findings of ACL 2026；成功曲线不代表全部运行 |

### 算法发现与基础设施应用

对应[算法与基础设施](algorithms-and-infrastructure.md)。正式方法论文与官方部署数字分列在同一来源组内，应用数字仍是作者或开发方报告。

| 编号 | 公开一手来源 | 状态或使用范围 |
| --- | --- | --- |
| <a id="source-16"></a>16 | Novikov 等，[AlphaEvolve 技术报告](https://arxiv.org/abs/2506.13131)；[DeepMind 应用说明](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) | 2025；预印本＋第一方应用记录，内核与端到端收益不同 |
| <a id="source-40"></a>40 | Fawzi 等，[AlphaTensor 正式论文](https://www.nature.com/articles/s41586-022-05172-4)；[官方方法说明](https://deepmind.google/blog/discovering-novel-algorithms-with-alphatensor/) | Nature 2022；特定矩阵尺寸与计算设置 |
| <a id="source-41"></a>41 | Mankowitz 等，[AlphaDev 正式论文](https://www.nature.com/articles/s41586-023-06004-9)；[LLVM libc++ 应用说明](https://deepmind.google/blog/alphadev-discovers-faster-sorting-algorithms/) | Nature 2023；排序内核收益受长度、硬件和测量条件限制 |
| <a id="source-42"></a>42 | Romera-Paredes 等，[FunSearch 正式论文](https://www.nature.com/articles/s41586-023-06924-6)；[官方问题说明](https://deepmind.google/blog/funsearch-making-new-discoveries-in-mathematical-sciences-using-large-language-models/) | 2023 在线／Nature 2024 卷；程序提案与可执行评价 |

### 科学家智能体

对应[科学家智能体](ai-scientists.md)。正式版、早期稿、产品说明和执行扩展不互相替代。

| 编号 | 公开一手来源 | 状态或使用范围 |
| --- | --- | --- |
| <a id="source-43"></a>43 | Lu 等，[Towards end-to-end automation of AI research](https://www.nature.com/articles/s41586-026-10265-5)；[AI Scientist v1](https://arxiv.org/abs/2408.06292)；[v2](https://arxiv.org/abs/2504.08066)；[Sakana 评审与撤稿说明](https://sakana.ai/ai-scientist-first-publication/) | Nature 2026-03-25；两种系统设置与早期预印本，撤稿是另一条记录 |
| <a id="source-44"></a>44 | Gottweis 等，[Co-Scientist 正式论文](https://www.nature.com/articles/s41586-026-10644-y)；[2025 初稿](https://arxiv.org/abs/2502.18864v1)；[Hypothesis Generation 产品说明](https://www.research.google/blog/a-new-era-of-innovation-google-research-at-io-2026/)；[2026 实验执行扩展](https://arxiv.org/abs/2608.26701) | Nature 首次在线 2026-05-19；产品发布和另篇扩展预印本不等于同一论文升级 |
| <a id="source-45"></a>45 | Ghareeb 等，[Robin 正式论文](https://www.nature.com/articles/s41586-026-10652-y)；[2025 预印本](https://arxiv.org/abs/2505.13400)；[FutureHouse 流程说明](https://www.futurehouse.org/research/demonstrating-end-to-end-scientific-discovery-with-robin-a-multi-agent-system) | Nature 首次在线 2026-05-19；介绍页更新日不是项目首发日 |
| <a id="source-46"></a>46 | Mitchener 等，[Kosmos 技术报告](https://arxiv.org/html/2511.02824v2)；[Edison 上线说明](https://edisonscientific.com/news/announcing-kosmos)；[Springer Nature 授权公告](https://edisonscientific.com/news/bringing-trusted-research-into-kosmos-our-agreement-with-springer-nature) | 2025 预印本 v2＋公司记录；2026 内容授权不改变论文证据类别 |

### 实验室自报与公开研发流程

对应[产业与自动实验](industry-and-autoresearch.md)、[实验练习](lab.md)。研发参与、局部框架优化与固定预算搜索不是同一种递归证据。

| 编号 | 公开一手来源 | 状态或使用范围 |
| --- | --- | --- |
| <a id="source-47"></a>47 | OpenAI，[GPT-5.3-Codex 发布稿](https://openai.com/index/introducing-gpt-5-3-codex/)；[AI self-improvement 系统卡](https://deploymentsafety.openai.com/gpt-5-3-codex/ai-self-improvement)；[内部部署风险记录](https://deploymentsafety.openai.com/gpt-5-3-codex/misalignment-risks-and-internal-deployment) | 2026-02-05 公司第一方记录；团队使用早期模型参与后续研发，High 门槛不是 RSI 判据 |
| <a id="source-48"></a>48 | MiniMax，[M2.7 原始发布稿](https://www.minimax.io/news/minimax-m27-en)；[同文 Research 页面](https://www.minimax.io/blog/minimax-m27) | 2026-03-18 公司自报；百轮 scaffold 迭代不等于自主权重升级 |
| <a id="source-49"></a>49 | Karpathy，[autoresearch 官方仓库与 README](https://github.com/karpathy/autoresearch) | 2026 公开流程；五分钟训练预算不包括所有开销，未运行训练 |

### 评测、风险与综述

对应[评测与安全](evaluation-and-safety.md)、[术语表](glossary.md)。综述用于定位原研究，不承担全部实验结论。

| 编号 | 公开一手来源 | 状态或使用范围 |
| --- | --- | --- |
| <a id="source-17"></a>17 | Chan 等，[MLE-bench](https://arxiv.org/abs/2410.07095) | 2024 首发／ICLR 2025；采用原论文批次，不是当前排名 |
| <a id="source-18"></a>18 | Wijk 等，[RE-Bench](https://arxiv.org/abs/2411.15114) | 2024 首发；专家预算、best-of-k 与违规审计需一起读 |
| <a id="source-19"></a>19 | Rank 等，[PostTrainBench](https://arxiv.org/html/2603.08640v2) | 2026 预印本，v2；自动训练产物不等于训练者自身演化 |
| <a id="source-32"></a>32 | Huang 等，[Large Language Models Cannot Self-Correct Reasoning Yet](https://arxiv.org/abs/2310.01798)；Kumar 等，[SCoRe，v2](https://arxiv.org/html/2409.12917v2)；[SCoRe 正式会议记录](https://iclr.cc/virtual/2025/poster/30501) | 前者 2023 首发／ICLR 2024；后者 2024 首发／ICLR 2025，训练奖励与测试反馈不同 |
| <a id="source-33"></a>33 | Shumailov 等，[AI models collapse when trained on recursively generated data](https://www.nature.com/articles/s41586-024-07566-y)；Gerstgrasser 等，[Is Model Collapse Inevitable?](https://arxiv.org/abs/2404.01413) | Nature 2024＋2024 作者稿；替换与累积数据的条件不同 |
| <a id="source-34"></a>34 | Gao 等，[Scaling Laws for Reward Model Overoptimization](https://arxiv.org/abs/2210.10760) | 2022；代理奖励与较独立评价可能背离 |
| <a id="source-35"></a>35 | Everitt 等，[Self-Modification of Policy and Utility Function in Rational Agents](https://arxiv.org/abs/1605.03142) | 2016 理论研究；保存初始目标不等于现实安全认证 |
| <a id="source-36"></a>36 | Chen 等，[Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops](https://arxiv.org/html/2607.07663v2) | 2026 综述预印本，v2；1,250 是检索语料规模，不是成功实验数 |

## 尚未解决的来源问题

原材料记录了 Good 重印与索引年份的差异，Hyperagents 的 HTML／PDF 日期差异，以及 MetaShare 正文和附录财务样本口径未协调。Sakana 正式论文与公开仓库的许可描述也有差异，因此这里只称“公开代码”，不统一宣称宽松开源。未确认的正式发表、完整实现或引用数，不补成否定结论，也不填成零。

后续更新应同时补上所读版本、指标分母、反馈可见范围和总预算；新结果若改变了这些条件，需要另列，不能直接覆盖旧数字。
