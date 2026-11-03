# 权重空间编程：一手来源与实验边界

核验日期：2026-11-03。本文核验的是公开证据，不是重新运行模型所得的实验报告。

最重要的区别是：**没有梯度训练，不等于没有数据、计算或反馈。** 作者的实验覆盖无工具读权重、无前向的矩阵分析、一次性写权重，以及依赖练习题、激活和验证反馈的迭代编辑，不能统一称为“只看权重就提升大模型能力”。各自权限见下表，依据是作者公开的提示、实验 README 和评分文件。

## 1. 来源索引

### 阅读范围与版本约定

本次完整阅读了原博客正文、日志仓库总 README、实验 1–8 的全部 README、Gemma 数学对照 README，以及公开实验汇总。另读取小型评分文件、编辑清单、Qwen 首轮提示与首个前向返回、评测协议代码；没有逐条审计全部对话，没有执行发布者代码、下载模型权重或调用原文实验的模型推理 API。对评分 JSON 的加总属于公开记录的算术核对，不属于模型实验复现。

以下每项均于 **2026-11-03 实际读取**；发布日期、提交日期与读取日分别记录。日志统一固定在提交 `4d09ba6d6a7e891dd8063974dfe81b3d78e3494f`，GitHub 记录提交日期为 2026-10-29；这不是博客的发布日期。未另外标注版本的实验资料，均指这个提交。

<a id="blog"></a>

### 原博客

- 来源：[Sparks of Weight-Space Programming: LLMs can natively read & write neural network weights](https://rikiyat.github.io/blog/weight-space-programming/)，Rikiya Takehi、Jayden Teoh、Alex Zhang、Omar Khattab。
- 发布：2026-11-02；读取：2026-11-03，正文全文，含追加 Gemma 实验、相关工作和日志说明。
- 支持：研究问题、八个实验的报告范围、作者对循环修复的解释，以及公开 checkpoint 的出处。
- 边界：这是作者博客报告，不以其自述替代原始评分；“未来可以增加能力、审计后门、避免遗忘”等属于展望，不是这些实验已经验证的结论。

<a id="logs"></a>

### 作者公开日志

- 来源：[总 README 与固定提交](https://github.com/RikiyaT/lm_understand-logs/tree/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f)；[提交元数据](https://api.github.com/repos/RikiyaT/lm_understand-logs/commits/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f)。
- 版本：上述 2026-10-29 提交；读取：2026-11-03，总 README 全文及下列资料。
- 支持：提示、答复、计算返回、评分与最终权重之间的对应关系。
- 边界：发布包只覆盖正文所报告的运行，不含全部早期提示试跑。作者报告所有 1,125 个回合均通过内置工具审计，本次未重新审计这 1,125 个事件流。部分训练 checkpoint、中间激活及运行服务代码未发布。

下表每行是本次实际读取的来源组，版本和读取日沿用上面的共同约定；README 全文已读，评分范围按行列明，不意味着该实验的所有日志都已读。

| 实验来源 | 支持结论与实际核对文件 | 核验边界 |
| --- | --- | --- |
| [1：游戏识别](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp1_which_game/README.md) | [评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp1_which_game/eval/scores.json)：四个命名结果均计为正确 | Freeway 的回答是 Frogger，评分按交通穿越游戏接受；每个游戏选训练的最佳种子，不是对任意策略抽样 |
| [2：扩散模型识别](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp2_diffusion/README.md) | [评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp2_diffusion/eval/scores.json)：三种形状名称正确 | 生成对象是实心形状，回答却都画成轮廓；“识别正确”不等于准确还原生成分布 |
| [3：字符语言模型](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp3_language/README.md) | [答案评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp3_language/eval/scores.json)、[头部测量](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp3_language/eval/heads.json)：六次语料判断正确 | 正文按 induction 分数 >0.2 定义复制头，评分文件的 `true_copy_heads` 却用 >0.3；必须注明阈值，不能直接把该字段当作正文真值 |
| [4：车辆修复](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp4_fix_car/README.md) | [编辑与测试评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp4_fix_car/eval/oneshot_result.json)：6,073/171,664 项变化；独立测试流 1,024 回合全部成功 | 编辑前已提供 256 回合失败统计和一条轨迹；成功限于这个关卡与测试流，不是一般物理控制能力 |
| [5：MinAtar 从零写权重](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp5_write_from_scratch/README.md) | [评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp5_write_from_scratch/eval/minatar_eval.json)：三个游戏均超过所列 100M 步 PPO 基线 | 每项 1,000 回合；对 500M 步基线只有 Breakout 更强。提供完整游戏源码，且 PPO checkpoint 未发布 |
| [6：围棋从零写权重](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp6_go_from_scratch/README.md) | [零反馈评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp6_go_from_scratch/eval/budget_0/eval_submission.json)、[50 次反馈评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp6_go_from_scratch/eval/budget_50/eval_submission.json)、[同规模对战](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp6_go_from_scratch/eval/ppo_same_size/ppo_big_eval/h2h_lr_scan.json) | 零反馈版仅胜过较小 PPO；胜过调参后的同规模 PPO 是 50 次反馈版。每个预算一条运行，不是学习曲线的多次重复 |
| [7：奉承识别](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp7_sycophancy/README.md) | 已读纯权重轮 [1](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp7_sycophancy/eval/weights_only_1/summary.md)、[2](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp7_sycophancy/eval/weights_only_2/summary.md)、[3](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp7_sycophancy/eval/weights_only_3/summary.md) 和 [attention 轮汇总](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp7_sycophancy/eval/attention_tool/summary.md) | 前三轮的 1/3 是概率 0.5 的强制平局选择；第四轮部分被提前停止。成功轮的组件排名仍是候选证据，不是全部经过因果干预确认的机制 |
| [8：Qwen 数学编辑](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/README.md) | 已读四版合并评分的关键字段、关键分片、编辑清单与 [实验汇总](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/eval/RESULTS_excerpt.md)，详见第 3 节 | 汇总自标最终版本为 2026-10-27 15:06；其旧实验编号与博客不同，应按模型、预算和公开运行对应，不按旧编号推断 |
| [Gemma 数学对照](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/gemma_followup/README.md) | 已读基线及四个编辑版的合并评分、25 次预算的评分分片 | 正文采用宽松答案抽取，不是仅接受 boxed 答案；与 Qwen 的模型规模、采样和输出上限也不同 |

<a id="qwen"></a>

### Qwen 官方模型卡

- 来源：[Qwen/Qwen3.5-0.8B 模型卡固定版本](https://huggingface.co/Qwen/Qwen3.5-0.8B/blob/2fc06364715b967f1860aea9cf38778875588b17/README.md)，Qwen Team。
- 版本：`2fc06364715b967f1860aea9cf38778875588b17`；[公开 API](https://huggingface.co/api/models/Qwen/Qwen3.5-0.8B) 记录仓库创建于 2026-02-28、该版本最后修改于 2026-03-02，不据此冒称正式发布日。读取：2026-11-03。
- 支持：0.8B、24 层、宽度 1,024；默认 non-thinking；thinking 模式更容易循环的官方警告。
- 阅读边界：已读架构、thinking 用法、采样建议和循环警告相关段落，未逐项核验模型卡全部榜单。文本 thinking 推荐温度为 1.0；博客使用的 0.6 应称为作者固定协议，不能笼统称“默认设置”。

<a id="model-release"></a>

### 编辑者身份与配置的证据边界

- 来源：[作者日志说明](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/README.md)和各实验原始请求；版本与读取日沿用日志约定。
- 支持：作者材料记录编辑者的模型标识及推理配置，可与被编辑的目标模型分开识别。
- 边界：本专题不评估编辑者产品规格、价格或可用性；模型标识不自动固定未来服务端实现，更不是这些实验的官方认证。复现还需记录当时的完整请求与可用服务版本。

<a id="checkpoint-release"></a>

### 编辑后 checkpoint 与外部重评

- 来源：[RikiyaT/Qwen3.5-0.8B-weight-space-programming 模型卡](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming/blob/d1671a178705bcab7644806d23c535517f35723b/README.md)，及 [编辑版评分](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming/blob/d1671a178705bcab7644806d23c535517f35723b/eval/scores_edited_math500.json)、[基线评分](https://huggingface.co/RikiyaT/Qwen3.5-0.8B-weight-space-programming/blob/d1671a178705bcab7644806d23c535517f35723b/eval/scores_base_math500.json)。
- 发布/重建：模型卡署明 2026-11-02；固定版本 `d1671a178705bcab7644806d23c535517f35723b`。读取：2026-11-03，模型卡全文及评分 JSON。
- 支持：卡片记载 akhaliq 用公开 diff 重建、核对哈希并重评；逐题记录可加总为编辑版 1,020/2,000＝51.0%，基线 5/100＝5.0%。
- 边界：完整评测只有编辑版 500 题×4 次；基线仅 25 题×4 次。它验证已有编辑 checkpoint 的重建和部分效果，不是重新发现编辑，也不是全部八个实验的独立复现。本次未对模型二进制亲自验哈希。

<a id="gemma"></a>

### Gemma 官方身份资料

- 来源：[google/gemma-3-270m-it 官方模型卡](https://huggingface.co/google/gemma-3-270m-it) 与 [公开版本元数据](https://huggingface.co/api/models/google/gemma-3-270m-it)。
- 版本：作者使用 `ac82b4e820549b854eebf28ce6dedaf9fdfa17b3`；API 记录创建于 2025-07-30、最后修改于 2025-08-14，非本次确认的发布日。读取：2026-11-03，公开身份和模型说明段落。
- 支持：对照使用的是 Gemma 3 270M 指令模型，而非与 Qwen 相同规模的模型。
- 边界：固定版本 raw 模型卡读取返回 401，未登录或绕过访问限制；公开页面已读，但未找到能独立确认温度 1.0、top-k 64、top-p 0.95 为“模型卡推荐”的段落。该采样组合可由作者评测记录确认，推荐出处仍待补核。

### 概念对照资料

下列五项是相关方法的一手入口，不是本文八个实验的复现证据。读取日均为 2026-11-03；没有查询引用数，也不以引用量评价结论。

<a id="transformer-circuits"></a>

#### Transformer Circuits：注意力计算框架

- 来源：[A Mathematical Framework for Transformer Circuits](https://transformer-circuits.pub/2021/framework/index.html)，Nelson Elhage 等，Anthropic，在线研究文章。
- 发布：2021-12-22；读取：2026-11-03，摘要式总览、QK/OV 分解、induction heads 和相关勘误章节，非全文。
- 支持：权重矩阵乘积可帮助分析注意力路由与写入；复制头的分析存在早于本博客的方法来源。
- 边界：该文重点是简化的 attention-only 模型；不能将其数学分解直接当作完整 Qwen 或 Gemma 的行为证明。文章自身还保留了一处组合图的勘误。

<a id="tracr"></a>

#### Tracr：程序到权重的编译

- 来源：[Tracr: Compiled Transformers as a Laboratory for Interpretability](https://arxiv.org/abs/2301.05062v5)，David Lindner、János Kramár、Sebastian Farquhar、Matthew Rahtz、Thomas McGrath、Vladimir Mikulik；[作者代码入口](https://github.com/google-deepmind/tracr)。
- 发布：arXiv v1 为 2023-01-12，所读 v5 为 2023-11-03；页面注明 NeurIPS 2023 Spotlight。读取：2026-11-03，元数据与摘要，未读论文全文。
- 支持：可把人类可读程序编译为具有已知结构的 decoder-only Transformer，提供解释方法的真值。
- 边界：形式程序编译不同于通用 LLM 根据自然语言直接设计权重；本次没有运行编译器。arXiv 页面提供开放 PDF 入口，未下载。

<a id="hypernetworks"></a>

#### HyperNetworks：专门的权重生成器

- 来源：[HyperNetworks](https://arxiv.org/abs/1609.09106v4)，David Ha、Andrew Dai、Quoc V. Le，arXiv 预印本入口。
- 发布：v1 为 2016-09-27，所读 v4 为 2016-12-01。读取：2026-11-03，元数据与摘要，未读全文或核查正式会议版本、代码。
- 支持：用一个网络生成另一个网络的权重；摘要明确其方法以反向传播端到端训练。
- 边界：生成权重本身不是本博客首创；需要区分专门训练的权重生成器与直接使用现成通用 LLM。开放 PDF 入口存在，未下载。

<a id="rome"></a>

#### ROME：定位与事实编辑

- 来源：[Locating and Editing Factual Associations in GPT](https://arxiv.org/abs/2202.05262v5)，Kevin Meng、David Bau、Alex Andonian、Yonatan Belinkov；[作者项目页](https://rome.baulab.info/)。
- 发布：v1 为 2022-02-10，所读 v5 为 2023-01-13；页面注明 NeurIPS 2022。读取：2026-11-03，元数据、摘要及项目概览，未读全文。
- 支持：以因果干预定位与事实预测相关的激活，再直接编辑前馈权重；是局部权重编辑的先例。
- 边界：事实关联编辑不等于循环修复或从零写游戏策略；摘要不能支持“所有局部编辑都有效且无副作用”。开放 PDF 入口存在，未下载。

<a id="refusal-direction"></a>

#### 单一拒绝方向

- 来源：[Refusal in Language Models Is Mediated by a Single Direction](https://arxiv.org/abs/2406.11717v3)，Andy Arditi、Oscar Obeso、Aaquib Syed、Daniel Paleka、Nina Panickssery、Wes Gurnee、Neel Nanda，arXiv 入口。
- 发布：v1 为 2024-06-17，所读 v3 为 2024-10-30。读取：2026-11-03，元数据与摘要，未读全文或验证代码。
- 支持：论文在所研究模型中发现与拒绝相关的一维残差子空间，并通过激活干预改变拒绝行为。
- 边界：这是低维行为方向的概念对照，不证明 Qwen 的循环方向与拒绝方向相同，更不证明任意能力都能用单方向增删。开放 PDF 入口存在，未下载。

### 仿射层与 ReLU 定义

- 来源：[PyTorch 2.15 Linear](https://docs.pytorch.org/docs/2.15/generated/torch.nn.Linear.html) 与 [ReLU](https://docs.pytorch.org/docs/2.15/generated/torch.nn.ReLU.html) 官方 API 文档。读取：2026-11-03，定义、权重形状和输入输出形状。
- 支持：`Linear` 保存输出维×输入维矩阵、偏置，以及 ReLU 的逐元素最大值定义。
- 边界：`stable` 入口在读取日重定向到 2.15；本专题固定该文档链接，不声称教学代码安装或依赖此版本。教学脚本使用 Python 标准库，列向量记号与 API 的批量行向量写法分别注明。

<a id="experiments"></a>

## 2. 实验权限矩阵与边界

这里的“纯权重判断”指判断时不读取目标网络的运行结果或激活，**不是不给架构、输入布局或任务语义**。以下所有实验都提供了架构说明；数值规模指被读写的目标网络，不是编辑者自身规模。依据为[各实验原始来源](#logs)。

| 实验 | 目标规模、架构与语义提示 | Python 权限 | 目标前向/反馈预算 | 可支持的结论 |
| --- | --- | --- | --- | --- |
| 1 游戏识别 | 17,253 参数；500→32→32→5；给网格通道与动作，不给游戏选项 | 无 | 单次答复，无运行反馈 | 纯权重加布局的开放命名；4 个案例 |
| 2 扩散识别 | 23,824 参数；160→64→64→144；给 DDPM、像素和时间步含义 | 无 | 明确禁止任何前向或采样模拟 | 纯权重识别三种形状，但实心/轮廓判断失败 |
| 3 语言识别 | 全模型约 7.16M，实际给中间块 7,084,032 数值；4 层×6 头；给前向代码及三种候选语料，移除输入/输出层 | 最多 100 次；实际每次对话 6–11 次 | 禁止网络及任一层在任何输入上前向；允许权重线性代数 | 无激活的权重分析；三模型各两次对话，不是六个独立训练模型 |
| 4 车辆修复 | 171,664 参数；679→128→五个 128 层→16；给场景、观测语义、失败统计和轨迹 | 无 | 一次编辑，无编辑后的反馈 | 无工具的一次性修复，**不是无行为证据的纯权重诊断** |
| 5 MinAtar 编程 | 20,486 参数；600→32→32→6；零初始化；给规则、完整源码、通道及评分方式 | 无 | 每游戏一次答复，提交前不运行 | 无环境反馈的策略构造；依赖明确任务语义，不是从匿名权重猜用途 |
| 6 围棋编程 | 1,480,274 参数；243→512×6→82；给 9×9 规则、棋盘布局和合法动作掩码 | 最多 120 次；各预算实际 1/17/30/39 次 | 0/10/25/50 次；每次最多 128 局，或 256 局面并可返回隐藏激活 | 只有零预算版无目标运行反馈；更强结果来自迭代验证 |
| 7 奉承识别 | 三对 Gemma 270M；18 层、宽 640；前三轮无嵌入/tokenizer，第四轮补全 | 纯权重轮最多 60 次；attention 轮最多 20 次 | 纯权重轮零前向；成功轮每次最多 16 段、每段 128 token，返回 attention，不返回输出/隐藏状态 | 纯权重识别未成功；3/3 成功依赖输入相关的 attention，组件因果地位仍有限 |
| 8 Qwen 编辑 | 文本部分约 0.8B；24 层、宽 1,024；给 tokenizer、练习题答案及参考解 | 最多 300 次；三预算实际 59/45/80 次 | 10/25/50 次；每次至多 512 次生成，或 teacher-forced 读取至多 1,024 段 | 依赖生成、评分、log-prob、隐藏状态和 MLP 激活的无梯度编辑，不是纯权重或零数据结果 |
| Gemma 数学对照 | 270M；18 层、宽 640；同类练习题，预设 DEV/HOLDOUT 选择流程 | 最多 300 次；实际 13/20/44/63 次 | 5/10/25/50 次；每次至多 2,048 次生成，或 1,024 段 teacher-forced 文本 | 同类无梯度编辑未建立明显数学提升；不能推出任何模型均无法新增能力 |

矩阵中的“pass”是作者定义的一次服务请求，不是一个样本或一次 token 级计算。Qwen 配对比较时每个模型最多 256 次生成，总计 512；其首轮就返回 96 个答案及隐藏状态、MLP 激活，其中 85 个到达 token 上限，见[原提示](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/turns/t001/prompt.txt)和[首轮返回](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/requests/fwd_1.done.json)。因此“50 次前向”不能直接换算成很低的总计算成本。

Qwen 初始提示还明确提供 GSM8K train 7,469 题、MATH train 7,275 题及 1983–2023 年 AIME 714 题；前两者带参考解，AIME 只带答案。禁止的是梯度与拟合式训练，不是查看这些数据或利用评分选择编辑，见上述原提示。

作者日志中的 `tool_free` 指没有使用 Codex 内置工具。实验 3、6、7、8 仍通过实验服务运行 Python 或前向请求。[总 README](#logs)明确说明了这一区别。最终由实验者打分也不意味着该分数在提交前给编辑者看过。

## 3. Qwen 与 Gemma 的关键数字

<a id="qwen-results"></a>

### Qwen：主结论可以对上记录，但要保留协议

直接读取的[基线合并评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/eval/unedited/merged.json)与[50 次预算合并评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/eval/p50c/merged.json)分别给出 MATH-500 准确率 0.079、0.481。本次另外读取双方全部十个 MATH-500 评分分片并加总：各 500 题、2,000 次生成，正确数 **158→962**；到达上限数 **1,860→661**，即 93.0%→33.05%，正文显示为 33.1%。这是记录内部一致性的核验，不是重新生成答案。

两版分片记录的采样一致：thinking 开启，temperature 0.6、top-p 0.95、top-k 20、presence penalty 1.5、seed 0，最多 **32,768 个新 token**，包含思考与最终答案；数学题取最后一个 boxed 答案评分。协议可核对[基线分片](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/eval/unedited/parts/math500_s0of10/scores.json)、[编辑版分片](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/eval/p50c/parts/math500_s0of10/scores.json)和[作者协议定义](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/code/profiles.py)。

按作者 README、合并评分与协议记录，各评测样本规模如下。这里是**所有采样答案的平均准确率，不是 pass@k**；同一题多次生成也不能视为同等数量的独立题目。

| 评测 | 题数 | 每题生成数 | 总生成数 |
| --- | --- | --- | --- |
| MATH-500 | 500 | 4 | 2,000 |
| GSM8K | 1,319 | 2 | 2,638 |
| AMC23 | 40 | 16 | 640 |
| Minerva Math | 272 | 4 | 1,088 |
| OlympiadBench | 674 | 4 | 2,696 |
| MMLU-Pro 固定子集 | 1,000 | 1 | 1,000 |
| GPQA Diamond | 198 | 4 | 792 |
| IFEval | 541 | 2 | 1,082 |
| AIME24 / AIME25，各自 | 30 | 16 | 480 |

GSM8K 的 13.8%→67.1%、IFEval 的 21.0%→62.3% 均能在上述合并评分中找到。IFEval 使用思考结束后的答案及 strict prompt-level 检查，并非数学题的 boxed 评分。公开汇总还列出 AIME24/25：50 次预算版仅为约 0.6%/2.3%；不能把部分基准的大幅改善写成数学能力全面恢复。GPQA 基线图曾用 149/198 题的临时结果 24.5%，完整公开评分为 22.7%，[实验 README](#logs)已明确说明。

权重数也有两个口径：[冻结编辑清单](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/work_notes/frozen_weights_manifest.json)记录第 15、19 层各改 64 个输出列，每列 1,024 项，覆盖 **131,072 项**；以约 0.8B 为分母是约 0.0164%，正文简写 0.016%。但[最终 bf16 diff 清单](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/runs/p50c/edit/manifest.json)给出实际位模式变化数 **65,260＋64,928＝130,188**，其余项舍入后与基线相同。不要把覆盖数当成精确的 bf16 变化数，也不要把参数占比当成计算节省比例。

解释者推论：更稳妥的描述是“在指定 thinking 与评分协议下，编辑缓解了妨碍完成答案的故障，提升可测表现”。截断比例是可核验指标，但不证明每条截断答案都在循环；这些结果也没有单独证明新数学算法被写入模型。这个限定与作者自己的 [Gemma 追加讨论](#blog)相容。

### Gemma：失败对照不能省略评分差异

作者公开的[基线评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/gemma_followup/eval/unedited/merged.json)和[25 次预算评分](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/gemma_followup/eval/g25b/merged.json)支持宽松 MATH-500 分数 6.8%→7.7%；四个编辑版的宽松分数依次约 7.0%、7.6%、7.7%、7.0%，均未建立明显提升。它是对该模型、该编辑流程的负结果，不是数学能力无法通过权重编辑增加的普遍证明。

Gemma 同样为 500 题×4 次，但不开 thinking，最多 **8,192 新 token**，temperature 1.0、top-k 64、top-p 0.95。正文采用宽松抽取：优先最后一个 boxed 答案，否则取明确的最终答案，再否则取最后一个数；严格 boxed-only 基线其实是 2.75%，25 次预算版是 3.75%。这些规则与数值可核对[对照 README](#logs)和[评分分片](https://github.com/RikiyaT/lm_understand-logs/blob/4d09ba6d6a7e891dd8063974dfe81b3d78e3494f/exp8_math/gemma_followup/eval/g25b/parts/math500_s0of3/scores.json)。

Gemma 基线 8.5% 截断与 Qwen 基线 93.0% 截断来自不同长度、模式与模型，适合作为各自运行故障的描述，不是严格匹配的“有循环/无循环”唯一变量对照。

## 4. 复现证据层次与待查项目

### 目前证据到哪一层

| 层次 | 本次能够确认的内容 | 不能据此宣称 |
| --- | --- | --- |
| 作者报告 | 博客、各实验权限和结果说明已读 | 同一结果已获独立实验验证 |
| 作者发布的可核对记录 | 小评分、逐题结果、提示、diff、协议可对应；关键计数已加总 | 发布包包含全部探索过程，或所有规则已被本次重新审计 |
| 发布者重建材料 | 提供固定基线版本、diff、重建脚本与张量哈希 | 本次已执行脚本并验证模型二进制 |
| 外部执行者的 checkpoint 重建与重评 | 模型卡署名 akhaliq，公开逐题评分支持编辑版 51.0%；属于可查的外部重评 | 已独立复现 Astra 的发现过程、全部基线和八个实验；作者名下的发布页本身也不是完全独立的研究报告 |
| 端到端独立复现 | 本次未执行，也未以以上资料确认 | 这些能力对别的编辑者、训练种子、架构或任务同样稳定 |

外部重评使用完整多模态 checkpoint，原实验使用文本导出；卡片说明语言张量相同，并列出 vLLM 0.33.0、transformers 5.20.2、math-verify 0.9.0。其 51.0% 不能取代原实验的 48.1%，也不能把只有 25 题的外部基线拼成完整的同环境前后对照。来源见[发布模型卡及评分](#checkpoint-release)。

### 发布时应保留的风险与后续核验

- **完整性与运行规则。** [作者 README](#logs)明确遗漏早期试跑；实验 8 的编辑服务、前向服务与部分评分依赖也未完整发布。后续应逐条审计允许的计算、失败请求重试、提示修订和跨会话交接，而不是仅依据 `tool_free` 字段推断无反馈。
- **统计稳定性。** 围棋和数学的每个预算对应一次设计/编辑轨迹；多题、多局评分不替代重复编辑运行。应重复编辑者种子与训练种子，报告按题聚类的不确定性，不能仅由这几条轨迹断言“多给预算必然更好”。
- **基线与成本公平性。** 应补同预算的随机局部编辑、传统无梯度搜索、较强训练方案，以及 Qwen 的 non-thinking、推荐温度和其他解码对照。总成本应含编辑者 token、全部生成与激活计算；当前“pass”口径不能证明比训练更省算力。
- **机制与副作用。** 正确答案增加、attention 转移与组件排名各是不同层级的证据。应补因果干预、跨任务与安全回归；修改很少的参数不自动保证无遗忘、无安全退化或无分布外副作用。此项是解释者提出的验证需求，不是已观察到副作用。
- **数据与复建范围。** 实验 3 的 Python 语料清单只恢复约 81.5% 的字符，不能称训练数据已完整复建；实验 7 未发布所用微调 checkpoint，重训又不保证逐位一致；实验 5 的 PPO checkpoint 也缺失。上述限制均在[对应 README](#logs)说明。
- **测试隔离与预训练。** 作者称测试集未交给编辑者，这说明实验过程的访问安排，不等于排除了编辑者或基座预训练中的数据重叠。本次没有做预训练污染审计；不能将“提交前未见测试题”改写为“所有模型从未见过这些题”。
- **来源待补。** Gemma 采样“官方推荐”的具体出处仍未独立核到；五项相关工作目前只核到摘要或指定章节。若正文进一步讨论其优化步骤、公式假设、实验细节或局部编辑安全性，应补读相应论文全文再引用。

这些边界不否认公开结果的价值，而是把“记录可核对”“已有编辑可重建”“效果被外部重测”和“发现过程可独立复现”分开，避免将早期案例扩写为已经成熟的通用工程能力。
