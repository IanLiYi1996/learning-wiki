# 实时多模态交互：来源与证据台账

核验日期：2026-11-09。本页记录公开一手网页、论文原文和官方仓库文档，共 12 项来源。论文版本来自 arXiv 提交历史，仓库采用本次确认的提交快照。未访问私有数据或未公开训练代码，未下载模型权重，未执行演示、推理或付费 API，也未独立复现性能数字。

[专题首页](README.md) · [Higgs 个案](06-higgs-realtime-duplex.md) · [术语表](glossary.md) · [离线实验](lab.md)

## 证据怎样分层

Boson 发布文是模型开发方对架构、训练与成绩的第一方陈述，不是独立性能认证。Full-Duplex-Bench、τ-Voice 和 ProactiveVideoQA 原文提供各自的评测定义；定义来自 Boson 以外的团队，也不意味着这些团队验证了 Higgs 的成绩。公开方法论文可解释训练术语，不能自动填补 Boson 未披露的实现。[S01](#boson) · [S05](#full-duplex-bench) · [S07](#tau-voice) · [S09](#proactive-videoqa) · [S12](#mopd)

“未建立”指本次所读公开材料不足以支持该结论，不等于证明该能力不存在。下面的解释边界与待核问题是整理者的审慎判断，必须与相应原文一起使用。[S01](#boson) · [S02](#boson-realtime-api)

## 来源索引与章节落点

| 编号 / 本页锚点 | 一手来源与用途 | 建议落点 |
| --- | --- | --- |
| [S01 / boson](#boson) | Boson Duplex 发布文：厂商自报与缺失项 | [06 个案](06-higgs-realtime-duplex.md) |
| [S02 / boson-realtime-api](#boson-realtime-api) | 既有 Higgs Realtime API 文档：产品边界 | [06 个案](06-higgs-realtime-duplex.md) |
| [S03 / moshi](#moshi) | Moshi 原论文：双音频流、Mimi、Inner Monologue | [01 双工](01-duplex-and-turn-taking.md)、[02 编解码](02-streaming-codecs-and-rendering.md) |
| [S04 / mimi-code](#mimi-code) | Kyutai 官方仓库：公开推理栈与延迟口径 | [02 编解码](02-streaming-codecs-and-rendering.md) |
| [S05 / full-duplex-bench](#full-duplex-bench) | FDB v1.5 原论文：重叠场景与指标 | [05 评测](05-evaluation-and-safety.md) |
| [S06 / full-duplex-bench-code](#full-duplex-bench-code) | FDB 官方仓库：版本与评测流程 | [05 评测](05-evaluation-and-safety.md) |
| [S07 / tau-voice](#tau-voice) | τ-Voice 原论文：任务结果与交互行为 | [03 工具](03-background-reasoning-and-tools.md)、[05 评测](05-evaluation-and-safety.md) |
| [S08 / tau-voice-code](#tau-voice-code) | Sierra 官方仓库：奖励依据、中文与版本隔离 | [05 评测](05-evaluation-and-safety.md) |
| [S09 / proactive-videoqa](#proactive-videoqa) | ProactiveVideoQA 原论文：主动视频回答与 PAUC | [05 评测](05-evaluation-and-safety.md) |
| [S10 / grpo](#grpo) | DeepSeekMath 原论文：GRPO 定义 | [04 训练](04-training-and-distillation.md) |
| [S11 / on-policy-distillation](#on-policy-distillation) | GKD 原论文：学生分布上的蒸馏 | [04 训练](04-training-and-distillation.md) |
| [S12 / mopd](#mopd) | MOPD 原论文：同源专长教师、按任务路由 | [04 训练](04-training-and-distillation.md) |

## Boson：先保留这些限定

<a id="boson"></a>

### S01 — Higgs Realtime Duplex 发布文

作者 / 发布者：The Boson AI Team / Boson AI。页面日期：2026-11-05。原文：[Higgs Realtime Duplex](https://www.boson.ai/blog/higgs-realtime-duplex)。这是厂商博客，本次没有确认与该文对应的独立技术论文、训练实现或权重快照；不赋予它虚构的 arXiv 标识。[S01 原文](https://www.boson.ai/blog/higgs-realtime-duplex)

| 待转述的内容 | 原文定位 / 能支持什么 | 尚未建立；写作时的边界 |
| --- | --- | --- |
| 160 ms | 按时间切分一节：各流使用 160 ms chunks，静音也占分块。[S01](#boson) | 这是流组织粒度，不是客户端采集到播放的 E2E 延迟实测；文中未提供该延迟的测点、负载、网络或分位数。 |
| 45B MoE | 模型与训练一节：前台模型的参数规模为 45B。[S01](#boson) | 按标称总参数规模记录，不能改写成“每 token 激活 45B”。active parameters、专家数、路由及完整系统参数量未披露。 |
| 约 2T tokens | 训练一节：从文本预训练模型出发，再以文本、音频、视觉数据继续训练约 2 万亿 tokens。[S01](#boson) | 不是仅文本量，也不是包含此前预训练的终身训练总量；模态比例、去重后数据量、tokenizer 和训练预算不足以核算。 |
| 并发工作 | 多线程、推理、工具与委派一节：前台自行推理、异步调用工具或更大后台模型。[S01](#boson) | 能支持设计陈述；不能由展示场景推出所有后台请求都有低延迟、正确取消或事务安全。 |
| MOPD / GRPO | 后训练一节：同一 base 的专长教师经包括 GRPO 的 RL 训练，再蒸馏到单学生。[S01](#boson) | 未给损失、KL 方向、教师混合/路由、任务权重、rollout 更新频率、奖励或消融；[S12](#mopd) 的公式不是 Boson 已确认实现。 |
| RSI | 循环一节：模拟交互、复盘失败、合成针对性数据、训练后重复。[S01](#boson) | 是厂商所用标签与流程描述；没有展示改进器/训练方法本身逐轮变强的独立测量、固定预算对照或自加速证据。 |
| 榜单 / 复现 | 评测一节：比较项部分取自外部报告；Boson 称自己复现了超过一半比较成绩。[S01](#boson) | 厂商复测比较模型不等于外部团队复现 Higgs；本文不能据此认定统一设置、公平预算或显著优势。 |
| API 状态 | 试用一节：Duplex API 即将推出、接受候补；既有 Higgs Realtime 可用。[S01](#boson) | 候补不等于 Duplex 已公开上线；[S02](#boson-realtime-api) 的既有 endpoint 不证明具有新模型、视频/头像或全部后台能力。 |

为了对照指标，保留三项厂商成绩：FDB v1.5 “average” 为 75.5；ProactiveVideoQA 的 PAUC@ω=0.5 为 31.9；τ-Voice 的 task completion（pass@1，%）为 69.8。这些不是本页实测，也不是三个可互换的“正确率”。[S01 评测表](https://www.boson.ai/blog/higgs-realtime-duplex)

复现前仍需确认：FDB average 的组成与归一化，τ-Voice 的版本、语言、Clean/Realistic 条件及任务分母，ProactiveVideoQA 的子集、时窗、评分器，以及各项是否允许后台委派。发布表未给足这些细节，原基准定义不能代替缺失的 Boson 运行配置。[S01](#boson) · [S05](#full-duplex-bench) · [S07](#tau-voice) · [S08](#tau-voice-code) · [S09](#proactive-videoqa)

<a id="boson-realtime-api"></a>

### S02 — 既有 Higgs Realtime API 文档

发布者：Boson AI。网页未显示可靠发布日期；记录为 2026-11-09 访问的可变文档。原文：[Higgs Realtime 概览](https://docs.boson.ai/models/higgs-realtime)。定位：概览、模型名、WebSocket endpoint 与功能清单。[S02 原文](https://docs.boson.ai/models/higgs-realtime)

文档明确列出 `higgs-realtime` 与 `wss://api.boson.ai/v1/realtime`，描述音频/文本双向流、turn detection、barge-in 和工具调用；它也将既有语音 session 称为 full-duplex。因此不能将“旧产品绝不支持双工”当成新旧区别，但该文档也没有建立“这个 endpoint 就是 11 月发布的 Duplex omni 模型”。[S02](https://docs.boson.ai/models/higgs-realtime) · [S01](#boson)

## 全双工与流式 codec 背景

<a id="moshi"></a>

### S03 — Moshi 原始技术报告

作者：Alexandre Défossez、Laurent Mazaré、Manu Orsini、Amélie Royer、Patrick Pérez、Hervé Jégou、Edouard Grave、Neil Zeghidour；机构：Kyutai。arXiv **2410.00037v2**：首次提交 2024-09-17，v2 为 2024-10-02。日期依据提交历史，不从 `2410` 倒推首发日。[元数据](https://arxiv.org/abs/2410.00037v2) · [已读全文](https://arxiv.org/html/2410.00037v2)

定位：§3.3、§3.4.1–3.4.4、§5.3。支持用户与系统音频的并行流、Temporal/Depth Transformer 的分层生成，以及 Mimi 的因果编解码。Mimi 使用 24 kHz 音频、12.5 Hz 帧率、80 ms 帧；论文配置的 split RVQ 是一个语义 VQ 加七层声学 RVQ。12.5 帧/秒不等于只有 12.5 个码本索引/秒：该八码本配置展开后，每条音频流是 100 个索引/秒。[S03 §3](https://arxiv.org/html/2410.00037v2)

定位：§3.4.4、§6。Inner Monologue 是逐帧先预测与输出语音对齐的文本，不是已证实的独立长链后台推理。论文含毒性、复述训练音频、声音一致性及水印研究；§6.4 中 Mimi 编解码会削弱所测 AudioSeal 水印，是特定实验的负结果，不是所有水印必然无效的定理。该报告也不能证明 Boson 使用 Mimi 或继承这些安全结果。[S03 §3.4.4、§6](https://arxiv.org/html/2410.00037v2)

<a id="mimi-code"></a>

### S04 — Kyutai 的 Moshi / Mimi 官方仓库

发布者：kyutai-labs。仓库：[moshi](https://github.com/kyutai-labs/moshi)。本次固定提交 `e6a55d2722a65870ef52a6c9f6ecfc0e90f38362`（提交时间 2026-05-16 UTC；不是项目首发日）。已读范围：README 的架构、Mimi 与客户端说明。[固定 README](https://github.com/kyutai-labs/moshi/blob/e6a55d2722a65870ef52a6c9f6ecfc0e90f38362/README.md) · [提交元数据](https://api.github.com/repos/kyutai-labs/moshi/commits/e6a55d2722a65870ef52a6c9f6ecfc0e90f38362)

README 解释 Moshi 理论 160 ms 是 Mimi 帧 80 ms 加声学延迟 80 ms，并报告 L4 GPU 上整体延迟最低约 200 ms。它还列出 PyTorch、MLX、Rust 推理栈，说明客户端回声消除、积压处理和中继网络可影响体验。这里只核验公开说明，未测量这些数字；尤其不能把 Moshi 的理论 160 ms 与 Boson 的 160 ms chunks 当成同一 E2E 指标。[S04 README](https://github.com/kyutai-labs/moshi/blob/e6a55d2722a65870ef52a6c9f6ecfc0e90f38362/README.md) · [S01](#boson)

## 评测：定义、版本与适用边界

<a id="full-duplex-bench"></a>

### S05 — Full-Duplex-Bench v1.5 原论文

作者：Guan-Ting Lin、Shih-Yun Shan Kuan、Qirui Wang、Jiachen Lian、Tingle Li、Shinji Watanabe、Hung-yi Lee。arXiv **2507.23159v4**：v1 为 2025-07-30，已读 v4 为 2026-04-26；“v1.5”是基准名称，不是论文修订号。arXiv 评论栏注明 ICASSP 2026 接收；此处采用作者稿，不冒充会议出版版。[元数据](https://arxiv.org/abs/2507.23159v4) · [已读全文](https://arxiv.org/html/2507.23159v4)

定位：§2.1–2.3、表 1。四种可控重叠是用户打断、用户附和、与他人交谈、背景语音；行为分类是 Respond/Resume/Uncertain/Unknown。stop latency 从重叠开始到模型停说，response latency 从重叠结束到模型下一次发声。真正打断期望及时让出话轮；附和和非对模型说的话通常期望继续原话。因此“所有 stop latency 都越短越好”与此定义不符。[S05 §2](https://arxiv.org/html/2507.23159v4)

定位：§2.3、§3、表 2–3。行为评分依赖 ASR 转录与模型裁判，时间检测依赖 VAD；原表分列行为分布、时延和韵律，不提供对所有这些异单位指标直接取平均的通用定义。它能支持重叠处理的评测框架，不独立证明 Boson 75.5 的计算口径，也不能把合成的场景控制当成中文真实用户或生产网络的完整验证。[S05](https://arxiv.org/html/2507.23159v4) · [S01](#boson)

<a id="full-duplex-bench-code"></a>

### S06 — Full-Duplex-Bench 官方仓库

发布者：Guan-Ting Lin 等作者，仓库：[DanielLin94144/Full-Duplex-Bench](https://github.com/DanielLin94144/Full-Duplex-Bench)。固定提交 `3e799c45a045256f47d5f1c9cda90157e2d2ec9e`（2026-05-20 UTC）。已读：根 README、`v1_v1.5/README.md`、`v1_v1.5/evaluation/README.md`。[固定根文档](https://github.com/DanielLin94144/Full-Duplex-Bench/blob/3e799c45a045256f47d5f1c9cda90157e2d2ec9e/README.md) · [提交元数据](https://api.github.com/repos/DanielLin94144/Full-Duplex-Bench/commits/3e799c45a045256f47d5f1c9cda90157e2d2ec9e)

根文档区分 v1/v1.5 的预录数据评测、v2 的动态实时评测与 v3 的不流利语音工具任务；v1 原有停顿、附和、顺畅换轮、用户打断四个维度，不能与 v1.5 的四种重叠场景混用。评测文档列出 ASR 对齐、行为分类、pre/post 韵律特征、时延与显著性分析流程；公开脚本不意味着不需外部模型或 API，更不意味着本页已跑通流程。[版本文档](https://github.com/DanielLin94144/Full-Duplex-Bench/blob/3e799c45a045256f47d5f1c9cda90157e2d2ec9e/README.md) · [评测文档](https://github.com/DanielLin94144/Full-Duplex-Bench/blob/3e799c45a045256f47d5f1c9cda90157e2d2ec9e/v1_v1.5/evaluation/README.md)

<a id="tau-voice"></a>

### S07 — τ-Voice 原论文

作者：Soham Ray、Keshav Dhandhania、Victor Barres、Karthik Narasimhan；机构：Sierra.ai、Princeton。arXiv **2603.13686v1**，2026-03-14。这里按预印本记录，不凭模板中的会议关键词宣称正式接收。[元数据](https://arxiv.org/abs/2603.13686v1) · [已读全文](https://arxiv.org/html/2603.13686v1)

定位：§3、§4.1–4.5、附录 E。278 任务由 airline 50、retail 114、telecom 114 组成；pass@1 衡量单次任务完成，数据库结果与必要通信检查共同参与判定，交互质量另列响应、让出话轮、时延、主动打断与选择性。Clean 和 Realistic 是不同声学/互动条件，不能脱离条件比较。[S07 §3–4](https://arxiv.org/html/2603.13686v1)

定位：§3.1、§4.4、§6.1。默认 200 ms 是模拟 tick，模拟时间与墙钟解耦；固定随机种子不消除 LLM 输出差异。原论文只测英语 TTS，模拟器接收智能体转录而非自己做 ASR，工具调用也被简化；因此它不是中文真人体验、真实工具长尾时延或端到端网络延迟认证。带四川普通话口音的英语 persona 仍不是中文任务。[S07 方法与限制](https://arxiv.org/html/2603.13686v1)

<a id="tau-voice-code"></a>

### S08 — Sierra τ-bench 官方仓库与评分文档

发布者：sierra-research。仓库：[tau2-bench](https://github.com/sierra-research/tau2-bench)。固定提交 `033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f`（2026-11-04 UTC）。已读：README 与 `docs/evaluation.md`，不将当前仓库等同于三月论文的冻结实现。[固定 README](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/README.md) · [提交元数据](https://api.github.com/repos/sierra-research/tau2-bench/commits/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f)

README 已列 `voice-v1` 的英语 278 任务与 `voice-v2` / τ-i18n 的六语言×三领域×每格 50 任务，共 900 次单试验通话，语言包含中文。它明确提示 2.0 的任务、提示、裁判与默认设置改变，成绩不能与 1.x 榜单直接比较。因此“τ-Voice 永远只有英语”过时，而“Boson 的 69.8 已验证中文 voice-v2”同样无依据。[S08 README](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/README.md) · [S01](#boson)

评分文档说明最终 reward 是 `reward_basis` 指定分量的乘积，默认 DB 与 COMMUNICATE；`actions` 通常是一条用于生成目标数据库状态的参考轨迹，并非唯一强制调用序列。只有指定 ACTION 分量时才把动作匹配作为奖励门槛。工具“调用正确”、环境“最终正确”、通信“说对”和所有安全要求“满足”不能由一个分数自动互相推出。[S08 评分文档](https://github.com/sierra-research/tau2-bench/blob/033bf082f48e4a3c6a1256208e93cf2ce9c3bb6f/docs/evaluation.md)

<a id="proactive-videoqa"></a>

### S09 — ProactiveVideoQA / PAUC 原论文

作者：Yueqian Wang、Xiaojun Meng、Yifan Wang、Huishuai Zhang、Dongyan Zhao；机构包含北京大学、Huawei Noah’s Ark Lab、北京科技大学。arXiv **2507.09313v2**：v1 为 2025-07-12，v2 为 2025-07-15。[元数据](https://arxiv.org/abs/2507.09313v2) · [已读全文](https://arxiv.org/html/2507.09313v2)

定位：§1、§3–4。任务在视频起始给出问题，模型在播放期间自行选择回答时刻，允许多次自由文本回答；不是无目标的自主行动。PAUC 按标注回答时窗计算累计回答质量随时间变化的归一化曲线面积。ω 调节时效与内容的权衡，论文推荐 0.5；ω=1 退化为忽略回答时间的内容评估。因此 PAUC@ω=0.5 不是普通分类准确率。[S09 定义](https://arxiv.org/html/2507.09313v2)

定位：§3、§6.1–6.2。原实现用 GPT-4.1 对累计回答评分，人类偏好研究也承认一致性有限；人类作答基线还受暂停、输入与翻译流程影响。这支持“回答时机应纳入评测”，不支持通用主动智能、头像生成质量或现实安全认证；Boson 的 31.9 仍需其自己的配置与运行证据。[S09 评测边界](https://arxiv.org/html/2507.09313v2) · [S01](#boson)

## 训练方法：公开定义不能代替私有配方

<a id="grpo"></a>

### S10 — DeepSeekMath：GRPO 原始方法来源

作者：Zhihong Shao、Peiyi Wang、Qihao Zhu、Runxin Xu、Junxiao Song、Xiao Bi、Haowei Zhang、Mingchuan Zhang、Y.K. Li、Y. Wu、Daya Guo；机构：DeepSeek-AI、清华大学、北京大学。arXiv **2402.03300v3**：v1 为 2024-02-05，v3 为 2024-04-27。[元数据](https://arxiv.org/abs/2402.03300v3) · [已读全文](https://arxiv.org/html/2402.03300v3)

定位：§4.1.1–4.1.4、算法 1。GRPO 用同一问题多次采样的组内奖励估计基线，不另训练 PPO 式 value critic；原方法包含策略比率裁剪、参考策略 KL 与结果/过程监督形式。“不用 value critic”不等于不用奖励模型、规则或裁判。原实验是数学文本训练，不能直接证明同一奖励已解决双工时机；Boson 的教师奖励、组大小、超参数仍未知。[S10 §4.1](https://arxiv.org/html/2402.03300v3) · [S01](#boson)

<a id="on-policy-distillation"></a>

### S11 — On-Policy Distillation / GKD 原论文

作者：Rishabh Agarwal、Nino Vieillard、Yongchao Zhou、Piotr Stanczyk、Sabela Ramos、Matthieu Geist、Olivier Bachem；机构包含 Google DeepMind、Mila、University of Toronto。arXiv **2306.13649v3**：v1 为 2023-06-23，v3 为 2024-01-17；arXiv 评论栏注明 ICLR 2024 接收。[元数据](https://arxiv.org/abs/2306.13649v3) · [已读全文](https://arxiv.org/html/2306.13649v3)

定位：§2、§3.1–3.2、算法 1。学生采样自己的序列，教师在这些前缀状态提供 token 分布监督，用来缓解训练/推理分布不匹配；GKD 可以混合固定数据与 on-policy 数据，也允许 forward KL、reverse KL 或 JSD 等不同散度，并可结合 RL。“on-policy”描述轨迹来自谁，不是“把教师答案存下来再做 SFT”的别名，也不规定唯一损失。论文不是 Boson 多模态 MOPD 的实现文档。[S11 方法](https://arxiv.org/html/2306.13649v3) · [S01](#boson)

<a id="mopd"></a>

### S12 — Multi-Teacher On-Policy Distillation 原论文

作者：Wenhan Ma、Jianyu Wei、Liang Zhao、Hailin Zhang、Bangjun Xiao、Lei Li、Qibin Yang、Bofei Gao、Yudong Wang、Rang Li、Jinhao Dong、Zhifang Sui、Fuli Luo；机构包含 Xiaomi LLM Core、北京大学、香港大学、中国人民大学。arXiv **2606.30406v1**，2026-06-29。本次已核验此 v1，未补写其他版本或正式发表状态。[元数据](https://arxiv.org/abs/2606.30406v1) · [已读全文](https://arxiv.org/html/2606.30406v1)

定位：§3.1–3.3、§4.4。公开方案从共同 SFT checkpoint 得到各领域 RL 教师；学生自己 rollout，按提示所属领域路由到对应冻结教师，接受逐 token reverse KL 监督。文中给出 policy-gradient 与带修正的 top-k 两种实现，并分析同源教师稳定性。这是按任务派教师的公开实例，不是“每个 token 都平均所有教师”，也不是权重合并。[S12 方法](https://arxiv.org/html/2606.30406v1)

边界：这篇论文与 Boson 博客的方法名称相同，但博客没有给出引用或足够细节确认采用此配方；论文中的损失、路由和稳定性结果不得移植为 Higgs 已知事实。§4.4.3 的后续一轮教师再训练和学生提升也不证明改进算法自身越来越强或持续自加速；迭代成绩与“改进器的改进”应分别取证。[S12 分析](https://arxiv.org/html/2606.30406v1) · [S01](#boson)

## 留给后续更新的证据缺口

以下是待补证清单，不是已经验证的实验结论：

- Higgs 的 E2E 测点、首音频/停说延迟分位数、并发负载和客户端播放缓存；目前只有分块陈述与其他系统的不同延迟口径。[S01](#boson) · [S04](#mimi-code)
- 激活参数、各模态 tokenizer、训练数据组成、MOPD 损失/教师策略、RSI 逐轮日志及固定预算对照；不要用通用论文补成厂商事实。[S01](#boson) · [S10](#grpo) · [S11](#on-policy-distillation) · [S12](#mopd)
- Higgs 的任务清单、版本、语言、judge、后台委派与预算配置、运行轨迹及外部复现；中文普通话、方言、中英混说与多方说话需要单列覆盖证据。[S01](#boson) · [S05](#full-duplex-bench) · [S07](#tau-voice) · [S08](#tau-voice-code)
- Duplex 的真实上线公告和模型标识，以及异步工具权限、错误撤销、声音/头像授权与数据保存说明。候补页、既有 Realtime 文档和功能展示不能代替这些验证。[S01](#boson) · [S02](#boson-realtime-api) · [S03](#moshi)
