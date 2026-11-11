# Agent Memory：一手来源与证据边界

观察日期：2026-11-11（Asia/Shanghai）。本页记录原始来源与证据边界，不是产品验收或独立复现实验。可变文档和 GitHub `main` 均指本次访问所见，不代表 Anthropic 实验使用的固定版本。

本次阅读公开原始网页、论文、README 与示例 prompt，没有调用模型服务、业务 API、付费服务或在线演示，也没有运行来源中的 notebook、benchmark 或下载权重。不把搜索摘要、公开示例或一次抓取失败当作内部实验的复现证据。

## 证据等级与使用规则

| 标签 | 含义 | 不能据此声称 |
| --- | --- | --- |
| 厂商自报 | Anthropic 对自家模型、内部语料和选定任务的实验叙述 | 独立复现、全套 benchmark 排名、普遍因果规律 |
| 原始研究 | 论文作者对指定协议的实验结果 | 任意产品、模型或价格体系同样成立 |
| 官方机制 | 产品文档与第一方公开代码／prompt | 所有部署已实现、prompt 等于强制安全策略 |
| 一般背景 | 解释预计算、跨任务学习或记忆攻击的相关工作 | 就是原文实验的实现或评测结果 |
| 教学建议／推论 | 从证据提出的检查项目，明确标为建议 | 厂商保证、论文已经完成的实验 |

下列十项为核心来源；论文的作者仓库、benchmark 配套文档和同项目 prompt 是核验入口，不另扩展成产品或论文大全。

<a id="primary-sources"></a>

## 十项核心一手来源

| 编号 | 来源与公开入口 | 可支持的内容与边界 |
| --- | --- | --- |
| S1 | Anthropic：[The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory) | 原文四层结构、定义及全部文中实验；属于厂商自报，不是完整可复现论文。 |
| S2 | Lin 等：[Sleep-time Compute: Beyond Inference Scaling at Test-time，v1](https://arxiv.org/html/2504.13171v1)；[元数据](https://arxiv.org/abs/2504.13171)；[作者代码](https://github.com/letta-ai/sleep-time-compute) | 原文直接引用的预计算背景；数学任务和成本模型不是 Anthropic 的数据库／wiki 实验。 |
| S3 | CL-Bench 作者：[Database Exploration 官方任务说明](https://raw.githubusercontent.com/pgasawa/continual-learning-bench/main/src/tasks/database_exploration/README.md)；[项目](https://continual-learning-bench.com/)；[作者仓库](https://github.com/pgasawa/continual-learning-bench)；[论文 v1](https://arxiv.org/html/2606.05661v1) | 任务变体、reward 与 gain；公开默认协议不能无条件套到 S1 的 30 题实验。 |
| S4 | Harvey：[LAB Evaluation Methodology](https://github.com/harveyai/harvey-labs/blob/main/docs/eval-strategies.md)；[原始文本](https://raw.githubusercontent.com/harveyai/harvey-labs/main/docs/eval-strategies.md)；[项目](https://github.com/harveyai/harvey-labs)；[分数变更记录](https://raw.githubusercontent.com/harveyai/harvey-labs/main/CHANGELOG.md) | 官方 rubric、all-pass、双 judge 与版本差异；不证明 S1 使用当前默认 grader。 |
| S5 | Anthropic：[Using agent memory](https://platform.claude.com/docs/en/managed-agents/memory) | 持久文本 store、访问权限、乐观并发、版本和删改边界；官方产品机制，未实际部署验证。 |
| S6 | Anthropic：[Dreams](https://platform.claude.com/docs/en/managed-agents/dreams) | research preview 的异步产品接口；输入 store 不修改，产出另一 store；不是所有 dreaming 实现的定义。 |
| S7 | Anthropic：[Knowledge wiki quickstart](https://github.com/anthropics/claude-quickstarts/blob/main/managed-agents/knowledge-wiki/README.md)；[原始 README](https://raw.githubusercontent.com/anthropics/claude-quickstarts/main/managed-agents/knowledge-wiki/README.md) | 公开示例的来源标注、冲突保留、workflow 和成本说明；不是 S1 全部内部实验的公开 harness。 |
| S8 | Anthropic：[How Claude remembers your project](https://code.claude.com/docs/en/memory) | Claude Code 的 auto memory、注入阈值、机器本地存储及留存；不可推广为 Managed Agents 的同一合同。 |
| S9 | Dong 等：[MINJA 论文 v5](https://arxiv.org/html/2503.03704v5)；[元数据](https://arxiv.org/abs/2503.03704)；[NeurIPS 2025 官方论文页](https://proceedings.neurips.cc/paper_files/paper/2025/hash/42a97bbd9844d2bf68596730af80bcdf-Abstract-Conference.html)；[作者代码](https://github.com/dsh3n77/MINJA) | 仅查询交互也可能污染经验库的原始研究；额外安全背景，不是 S1 的引用或对 Claude 产品的漏洞证明。 |
| S10 | Anthropic：[Dreaming with a dynamic workflow](https://platform.claude.com/cookbook/managed-agents-cma-dreaming-with-a-dynamic-workflow) | S1 所链接的公开 cookbook；动态 workflow、估价／预算和记录清理。与 S6 的专用 Dreams API 要分开。 |

### 论文身份与访问情况

引用数未查询；不以引用量筛选或编造引用数。下列 arXiv 标识均来自实际打开的官方页面；预印本 DOI 不冒充会议出版 DOI。

| 论文 | 作者 | 日期／出版身份 | 固定版本与公开全文 |
| --- | --- | --- | --- |
| Sleep-time Compute: Beyond Inference Scaling at Test-time | Kevin Lin、Charlie Snell、Yu Wang、Charles Packer、Sarah Wooders、Ion Stoica、Joseph E. Gonzalez | 2025-04-17；本次按 arXiv 预印本引用 | `2504.13171v1`；HTML 已读；[PDF](https://arxiv.org/pdf/2504.13171v1) 为官方全文入口 |
| Continual Learning Bench: Evaluating Frontier AI Systems in Real-World Stateful Environments | Parth Asawa、Christopher M. Glaze、Gabriel Orlanski、Ramya Ramakrishnan、Benji Xu、Asim Biswal、Vincent Sunn Chen、Frederic Sala、Matei Zaharia、Joseph E. Gonzalez | 2026-06-04；本次按 arXiv 预印本引用 | `2606.05661v1`；HTML、[公开 PDF](https://arxiv.org/pdf/2606.05661) 已读 |
| Memory Injection Attacks on LLM Agents via Query-Only Interaction | Shen Dong、Shaochen Xu、Pengfei He、Yige Li、Jiliang Tang、Tianming Liu、Hui Liu、Zhen Xiang（会议页作 Zhen J. Xiang） | 初稿 2025-03-05；本次 arXiv v5 修订 2026-02-12；会议身份为 NeurIPS 2025 | `2503.03704v5`；HTML 已读；[会议 PDF](https://papers.neurips.cc/paper_files/paper/2025/file/42a97bbd9844d2bf68596730af80bcdf-Paper-Conference.pdf) 为官方全文入口 |

S9 早期搜索结果可能保留旧标题 *A Practical Memory Injection Attack against LLM Agents*；本页采用当前 arXiv 和会议标题，不当作两篇论文。三篇论文的作者／日期分别以 [S2 元数据](https://arxiv.org/abs/2504.13171)、[S3 元数据](https://arxiv.org/abs/2606.05661)、[S9 元数据](https://arxiv.org/abs/2503.03704) 为准。

<a id="anthropic"></a>

## 原文身份、定义与准确组件名称

S1 页首标示 **2026-11-06**，Team 为 **Engineering**；文末明确由 **Lance Martin** 撰写。编辑指导、讨论贡献者及图件作者属于 acknowledgements，不应一并写成论文共同作者。页面仅给出版日期，不据此推定发布时间或时区。[来源：S1](https://www.anthropic.com/research/components-of-agent-memory)

其局部定义是：从交互／任务经验获得、跨 session 保留、以后能作为 context 读取的知识。它明确排除权重更新、单次对话内的 in-context learning，以及为续接上下文窗口而做的 compaction；这是**本文的术语边界**，不是整个领域必须采用的唯一分类。[来源：S1，Memory notes](https://www.anthropic.com/research/components-of-agent-memory)

<a id="architecture"></a>

| 原文 Figure 1，自下而上 | 中文对照 | 职责 |
| --- | --- | --- |
| **transcripts** | 原始会话／事件记录 | 可搜索的经验记录 |
| **memory notes** | 记忆笔记 | agent 主动保存的重要信息 |
| **memory representations** | 记忆表示 | 如 wiki，用结构与链接组织信息 |
| **injected context** | 注入上下文 | session 开始时由 harness 预装 |

**dreaming** 是跨层检查、整理、构建表示与提升信息的过程，不是第五层。`write / manage / read` 可作为教学的操作视角，但不要称为 S1 的原始四组件名称；也不要把原文改写成“短期／长期／工作记忆”三层。神经科学睡眠类比是动机，不是 agent 使用相同生物机制的实验结论。[来源：S1，Figure 1、6、9、13](https://www.anthropic.com/research/components-of-agent-memory)

### 持久化状态不等于权重学习

S5 的 memory store 是 workspace 范围的文本集合，挂到 session 后用文件工具读写，写入可跨 session 保留。S8 的 auto memory 则是机器本地 Markdown。二者均说明一种**外部状态→未来上下文**路径；不能据此声称模型参数、KV cache、进程内存或全部工具环境被跨 session 保存。[来源：S5 Overview](https://platform.claude.com/docs/en/managed-agents/memory)、[S8 Configure auto memory](https://code.claude.com/docs/en/memory)

检索出的内容在推理时仍进入 context，因此“采用持久记忆”和“推理时利用 in-context learning”并不矛盾；这是机制解释，不是声称 S1 做了权重训练。S2 也是先重表示已知 context、之后把产物提供给问答，而非用“离线”一词证明发生了梯度更新。[来源：S2 §3](https://arxiv.org/html/2504.13171v1)

<a id="evaluation"></a>

## 原文报告了哪些任务，协议能确认到哪里

### 1. CL-Bench 1.0：数据库任务，不是全套总分

S1 报告使用 Managed Agents：每题新 session，跨题仅保留可读取的 memory directory，答后得到正确解法。Figure 3 是 **30 题**的运行均值，纵轴为 **mean reward**，不能改称准确率。[来源：S1，Figure 3](https://www.anthropic.com/research/components-of-agent-memory)

| 模型，保留原文拼写 | Stateless baseline | Memory store |
| --- | ---: | ---: |
| Claude Opus 5.5 | 0.655 | 0.838 |
| Claude Sonnet 5.5 | 0.644 | 0.833 |
| Claude Opus 5 | 0.564 | 0.828 |
| Claude Opus 4.7 | 0.383 | 0.700 |
| Claude Sonnet 5 | 0.306 | 0.610 |
| Claude Sonnet 4.6 | 0.330 | 0.364 |

这是 S1 图中的数据库单项数值，不是产品可用性声明，也不是 CL-Bench 聚合 leaderboard。[来源：S1，Figure 3](https://www.anthropic.com/research/components-of-agent-memory)

S3 当前公开任务名为 **Database Exploration**，代码目录为 `database_exploration`。官方 README 区分：

- `multi_group`：原始数据库上的 **30 题**。
- `schema_drift`：**40 题**，20 题后迁移数据库；`default` 采用这个协议。
- 正确答案的 reward 为 `1 - exploratory_queries / max_queries_per_question`；错误、超时或超预算的 reward 为零。最终 `ANSWER` 动作不算探索 query。

公开论文 Appendix A.4 使用 40 题、每题 15 次探索 SQL 的默认说明。**S1 没有明确标注 variant、commit 或全部预算；30 题与 `multi_group` 长度一致，但一致不等于已确认同版。**不能给 S1 擅加“第 20 题发生漂移”或“预算必为 15”。

任务定义见 [S3 README](https://raw.githubusercontent.com/pgasawa/continual-learning-bench/main/src/tasks/database_exploration/README.md)，论文说明见 [S3 Appendix A.4](https://arxiv.org/html/2606.05661v1)。官方 gain 是同系统有状态 reward 与 stateless baseline 的差；聚合 reward／gain 还有跨任务归一化，不能混作单题 reward。[来源：S3 项目 Metrics at a glance](https://continual-learning-bench.com/)

### 2. Pokémon Red：长程交互案例

S1 比较 Sonnet 3.7 与 **Claude Fable 5** 各一次运行、约 10,000 steps 时的记忆与进度：413 个文件／225 个目录／一枚 badge，对比两个目录中的九个文件加 `global.md`／四枚 badge。Figure 4 中后者总数为 **10 个文件**，不是九个。Opus 5.5 通关是另一个叙述，不是这组同点对比。[来源：S1，Figure 4](https://www.anthropic.com/research/components-of-agent-memory)

Mt. Moon 案例对比错误原始笔记、dreaming 修正后的笔记与无记忆；Figure 8 的修正分支在 action 1,935 到达 Cerulean。steps 与 actions 不自动等价；单案例、不同模型的展示不能隔离模型能力、策略、随机性与记忆结构的影响。[来源：S1，Figure 7–8](https://www.anthropic.com/research/components-of-agent-memory)

### 3. Stainless 内部语料：作者自建问答集

S1 的规模为约 350,000 文件／420M tokens，问答集 **25 题**。使用 Opus 5，通过 2→128 sessions 建 wiki；图的预处理横轴为 2M→128M dreaming tokens。问答报告的是满足 **graded criteria** 的比例：

| 条件 | 原文报告 |
| --- | --- |
| Wiki only | 13%→48% |
| Wiki + search | 54%→61% |
| Search only | 53% |
| 在线 token 变化 | Wiki + search 每题约少用 20,000 tokens |

文件集是内部资料；不宣称已取得其语料、25 题、完整 rubric 或运行轨迹。数字不是“正确回答题数”的百分比，也不是构建成本已回收的证明。[来源：S1，Figure 10](https://www.anthropic.com/research/components-of-agent-memory)

### 4. Merger 文档问答与 Harvey LAB：要分开

S1 并列使用 merger 文档问答和 **Harvey Legal Agent Benchmark（LAB）**。Merger 有 **24 题**；87% 对 73% 指其中需要跨文档整合／判断或算术的项目，不应改成整套 LAB 分数。LAB 展示选定任务：单文档文本查找型标准没有明确 wiki 收益；另一个 wiki 为原文文本大小的 1.77 倍。[来源：S1，Figure 11–12](https://www.anthropic.com/research/components-of-agent-memory)

合同案例中，改写构建指令后，由共享汇总表改为每份合同单独页面、单 agent 负责并保留条款原文，报告覆盖从 **41/57（72%）到 57/57（100%）**。这不证明全部 LAB 任务满分，也不单独识别“逐字引用”“写入所有权”“提示优化”各自贡献。[来源：S1，Figure 14](https://www.anthropic.com/research/components-of-agent-memory)

**LAB 官方计分尤其不能混用：**S4 当前每个 criterion 由 LLM judge 判断 pass/fail；单 judge 的任务 score 只有全部通过才是 1，否则为 0。默认双 judge 是 `claude-sonnet-4-6` 与 `gpt-5.5`，两者 all-pass 值取均值，所以单次 dual headline 可为 0、0.5 或 1；严格双方全通过另列。criterion pass rate 是诊断量，macro 与 pooled 也不同。S1 未说明其完整 judge 配置，因此不能把 72%→100%自动换成当前官方 all-pass headline。[来源：S4 Evaluation Methodology](https://raw.githubusercontent.com/harveyai/harvey-labs/main/docs/eval-strategies.md)

官方 README 要求写清 release／commit；CHANGELOG 记录 rubric judge、工具与文档解析改变。例如 2026-08-26 默认改为双 judge；2026-11-05 改了含修订／批注的 DOCX 读取行为。后来的主分支不等于 S1 运行协议。[来源：S4 README](https://github.com/harveyai/harvey-labs)、[S4 CHANGELOG](https://raw.githubusercontent.com/harveyai/harvey-labs/main/CHANGELOG.md)

## 消融和对照：已测、未测及混杂因素

| 干预／对照 | 可核实证据 | 解释边界 |
| --- | --- | --- |
| Memory vs stateless | 数据库同项任务、有／无跨题目录；见上表 | 不是所有任务或所有记忆架构的因果结论 |
| 写入策略提示 | Sonnet 4.6 refined instruction：0.364→0.641；只记录失败使 Opus 5／4.7 的 memory gain 分别减少 0.234／0.150 | 提示效应依模型和任务，不是“永远不要规范 memory” |
| 校验／纠错 | Mt. Moon 修正前、修正后、无 memory 分支 | 局部案例，不是总体可靠性估计 |
| 表示＋检索 | Stainless 的 wiki only、search only、二者组合；随构建计算量变化 | 提升同时增加预处理预算，非等总成本比较 |
| 目标化构建 | 合同页拆分、单写者与精确条款共同调整 | 多项干预捆绑，不能拆出单因素贡献 |
| 二次维护 | LAB 示例中补页面、修正悬空链接 | 结构维护观察，不等于新的普适分数增益 |

本表依据 [S1 Figure 5、8、10、14–15](https://www.anthropic.com/research/components-of-agent-memory)。S1 未给出完整实验发布包、各图统一重复次数／随机种子／置信区间、全部 prompts 或全因子组件消融。不可补写“统计显著”，也不能声称实测了 dense retrieval、知识图谱、向量数据库、LoCoMo 或 LongMemEval；原文未报告这些对照。

独立背景 S3 论文在其自己的系统与协议下报告 naive ICL 优于专用 memory systems；这提示需要比较具体系统，不与 S1 的选定数据库结果混成一句“memory 必然更好／更差”。[来源：S3 Abstract、实验](https://arxiv.org/html/2606.05661v1)

<a id="cost"></a>

## 计算与成本控制：不要只记在线省下多少

S2 将先已知的 context 与后到的 query 分离，在 Stateful GSM-Symbolic、Stateful AIME 上研究预计算；另有 Multi-Query GSM-Symbolic 和 SWE-Features case study。论文的约 5× 是同准确率下的 **test-time compute** 降低，不是总体账单降低五倍。§5.3 的最高 2.5× 平均成本收益采用每 context 十个 queries，并假设在线生成 token 单位成本是 sleep-time 的 **10 倍**；是成本模型结果，不是当前任意 API 的真实费率。[来源：S2 §4–6](https://arxiv.org/html/2504.13171v1)

S6 的 Dreams 按所选模型标准 token 费率计费，资源 `usage` 报告用量；应先小批量检查整理质量。S10 cookbook 有运行前估价和预算上限；预算是 ceiling，不是预期花费。其例子与 S1 Stainless 实验不是同一个工作负载。[来源：S6 Billing](https://platform.claude.com/docs/en/managed-agents/dreams)、[S10 Cost、配置单元](https://platform.claude.com/cookbook/managed-agents-cma-dreaming-with-a-dynamic-workflow)

S7 当前 README 报告的 build 成本、回本查询数和 per-answer 倍数只属于其示例／benchmark 自报；不移植为专题通用 ROI。它明确只有 `core` tier 的运行被记录，其他语料与当前价格会改变结果。[来源：S7 Cost and tier expectations](https://raw.githubusercontent.com/anthropics/claude-quickstarts/main/managed-agents/knowledge-wiki/README.md)

**教学验收建议，非已有实验结果：**比较时固定模型、任务顺序、访问权限和预算；同时记录原始查询成本、预处理／dreaming、在线读写、重建／更新、存储与缓存、失败重试和延迟。全生命周期每题成本可按 `(构建 + 更新 + 全部在线开销) / 实际查询数` 计算；不要只展示“每题少 20,000 tokens”。漂移、无记忆、原始检索、表示＋检索、禁止写入和有限预算都应有对照，并隔离评测题／答案对构建指令优化的泄漏。

<a id="provenance"></a>

## 来源、更新与冲突：公开代码支持到哪里

- **事实 provenance 与修改 provenance 不同。**S5 的版本和 session 归属回答“谁何时改了什么”，不证明内容是真的。S7 analyzer 的来源、日期、验证方法和不确定性记录回答“这条内容凭什么成立”。[S5 Audit memory changes](https://platform.claude.com/docs/en/managed-agents/memory)、[S7 analyzer prompt](https://raw.githubusercontent.com/anthropics/claude-quickstarts/main/managed-agents/knowledge-wiki/prompts/analyzer_system.md)
- **保留争议，而不是自动编出一致答案。**S7 organizer 规定可确定的新修正保留日期化旧值；无法裁决的冲突保留双方、来源与日期，并区分人的决策和 agent 推断。它还提醒高影响事实在依赖前重新检查。[S7 organizer prompt](https://raw.githubusercontent.com/anthropics/claude-quickstarts/main/managed-agents/knowledge-wiki/prompts/organizer_system.md)
- **transcript 是证据，不是绝对现实。**S1 的纠错案例以原始 transcript 校验笔记；S7 prompt 优先工具观察而非 agent 自述。但日志中的工具结果仍可能错误、缺失或被注入；“日志存在”不等于“已验证事实”。前句是来源规定，后句是信任边界推论。[S1](https://www.anthropic.com/research/components-of-agent-memory)、[S7 analyzer prompt](https://raw.githubusercontent.com/anthropics/claude-quickstarts/main/managed-agents/knowledge-wiki/prompts/analyzer_system.md)
- **乐观并发不是语义裁决。**S5 支持 `content_sha256` 写入前提条件，hash 不匹配需重新读取再尝试；它能发现读写冲突，不自动决定两个业务事实谁对。S7 analyzer 则采用定点编辑、写后读回、重试合并及必要时分文件，organizer 等其他 writer 完成后单独运行。[S5 Safe content edits](https://platform.claude.com/docs/en/managed-agents/memory)、[S7 analyzer](https://raw.githubusercontent.com/anthropics/claude-quickstarts/main/managed-agents/knowledge-wiki/prompts/analyzer_system.md)、[S7 organizer](https://raw.githubusercontent.com/anthropics/claude-quickstarts/main/managed-agents/knowledge-wiki/prompts/organizer_system.md)
- **仍有已承认的丢写。**S7 README 说明共享页可能互相覆盖，最忙 entity page 约 5% 已写行会丢失；不要把 prompt 中的读回／合并要求说成已经提供事务性、串行化或零丢失保证。[S7 Shared pages](https://raw.githubusercontent.com/anthropics/claude-quickstarts/main/managed-agents/knowledge-wiki/README.md)

### 三种 dreaming 语境不要混淆

| 语境 | 当前可核实的更新方式 | 不能外推 |
| --- | --- | --- |
| S1 一般 dreaming | 用额外计算回看经验、修正并重组织记忆 | 一定使用某个产品 API 或固定模型训练方法 |
| S6 Dreams 产品 | 异步读现有 store 和 1–100 个 sessions，产出另一个 store；输入不改；完成后审阅并选择挂载 | 自动把所有线上 session 切换过去；失败产物完整 |
| S10 动态 workflow cookbook | 自己编排分析／整理 session；设置 `COOKBOOK_STORE_ID` 可更新指定 store | 与 S6 相同的 copy-on-output 合同 |

S6 失败或取消后会留下部分输出，`running` 时出现 output ID 不等于完成；终止后的执行 session 是 archive 而非 delete。以上区分来自 [S6 How it works、Lifecycle、Use the output](https://platform.claude.com/docs/en/managed-agents/dreams)、[S10 配置与 cleanup](https://platform.claude.com/cookbook/managed-agents-cma-dreaming-with-a-dynamic-workflow)。S7 当前公开 quickstart 也不等于把 S1 的 128-session 内部实验原封不动开源。

<a id="safety"></a>

## 投毒、权限与隐私：事实和建议分别标记

### 有一手证据的风险／机制

1. **持久写入扩大注入影响时间。**S5 默认附加 store 的 access 是 `read_write`，明确警告用户输入、网页和工具返回中的 prompt injection 可把恶意内容写入 store，后续 session 再读取。只需参考的 store 应使用 `read_only`。这不等于只读内容已经可信。[S5 Attach a memory store](https://platform.claude.com/docs/en/managed-agents/memory)
2. **不需要直接改库也能攻击某些经验库。**S9 的攻击者通过查询和观察输出诱使 agent 保存记录；其实验涵盖 RAP/Webshop、EHRAgent/MIMIC-III 与 eICU、QA Agent/MMLU。前提包括写入／保留经验且后续按相似度检索；这是被测管线的结果，不可声称任意 Claude 或任意用户隔离机制已被攻破。本台账不执行攻击，也不把其成功率当作真实产品漏洞率。[S9 §3、§5.1](https://arxiv.org/html/2503.03704v5)
3. **prompt 防线不是权限执行器。**S7 analyzer／organizer 明确把 documents、tool results 和已有 memory 视为数据、不服从其中指令，并禁止保存 secrets；S8 也明确 CLAUDE.md／auto memory 是 context，不是 enforced configuration。因此不可宣称“写了忽略注入”就有强制访问控制。[S7 analyzer](https://raw.githubusercontent.com/anthropics/claude-quickstarts/main/managed-agents/knowledge-wiki/prompts/analyzer_system.md)、[S7 organizer](https://raw.githubusercontent.com/anthropics/claude-quickstarts/main/managed-agents/knowledge-wiki/prompts/organizer_system.md)、[S8 CLAUDE.md vs auto memory](https://code.claude.com/docs/en/memory)
4. **版本留存与当前内容删除不同。**S5 删除一条 memory 不删除 store 的历史版本；一般保留 30 天，但存活 memory 的近期版本可能保留更久。redact 清除历史内容但保留审计痕迹；当前 live head 不能直接 redact，需先更新或删除。整个 store 的删除另有语义。不能把删文件、archive 或 30 天说成所有副本立即清空。[S5 Audit memory changes、Redact a version、Manage memory stores](https://platform.claude.com/docs/en/managed-agents/memory)
5. **托管与本地不是相同隐私合同。**S5／S6 当前明确 Managed Agents 不适用 ZDR、HIPAA，session transcript 持续存在直到删除。S8 的 auto memory 是机器本地，transcript 留存清理不顺带删记忆文件。本地存储不等于读取后永不进入推理 context；这是数据流解释，不是合规认证。[S5 Data handling](https://platform.claude.com/docs/en/managed-agents/memory)、[S6 Data handling](https://platform.claude.com/docs/en/managed-agents/dreams)、[S8 Storage location、How it works](https://code.claude.com/docs/en/memory)
6. **注入窗口有明确且产品特定的限额。**S8 是 `MEMORY.md` 前 **200 行或 25KB，先触及者为准**，topic files 按需读取；不是全目录自动注入，也不是全部 CLAUDE.md 的同一硬限制。注入内容可能成为每次会话的持续错误来源，长度限制本身不验证真实性。[S8 How it works](https://code.claude.com/docs/en/memory)

### 教学与治理建议，不能包装为来源已经实现

按用户／租户／项目隔离 store；记录事实的原始引用、观察时间、有效范围、验证状态和取代关系；不让低信任内容经总结后升级为系统指令；把写入候选与审批后记忆分开。高影响事实需要重新验证，冲突需要保留证据和裁决者。

设计删除流程时同时检查原始 transcripts、当前 notes、wiki 衍生页、注入索引、历史版本、导出和备份；只读挂载不能解决读取越权或敏感内容外泄。dreaming 的输入权限、产出审阅、切换及回滚需另行设计。上述是基于 S5–S9 的治理建议，**没有证据证明 S1 的实验已经完整落实，也没有完成产品安全审计或删除验证**。

## 尚未证实，保持 unknown

- S1 每项实验的精确模型配置、harness commit、完整 prompt、随机性设置、重复次数与统计不确定性。
- Anthropic 30 题数据库实验是否使用 S3 当前 `multi_group` 的原样数据、预算与 reward 实现。
- S1 Stainless 原始 corpus／问答集／rubric 的公开可得性，以及其建库过程是否完全隔离待评测问题。
- S1 对 LAB 所用 task ID、release、judge 数量、judge 模型与聚合方法；不依据图中文字猜任务路径。
- 整套内部实验代码／完整 trajectories 是否公开。本次只取得公开论文、文档与示例；不把未找到写成“确定从未发布”。
- S1 的全生命周期美元成本、失败／漂移时的更新成本，以及系统级投毒、租户隔离、隐私删除的独立审计结果。

所有数值为注明来源的公开报告或公式说明，不是本轮测量。返回[专题导读](README.md)或[原创离线练习](lab.md)。
