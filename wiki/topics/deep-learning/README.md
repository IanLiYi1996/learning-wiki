# 深度学习专题解读：从论文主张到可检验的机制

研究日期：2026-11-04。这里按“问题 → 数学直觉 → 实验证据 → 实现 → 边界”解读具体研究，不把单篇文章包装成整个深度学习领域的定论。

目录现拆为六个可折叠方向，新增视觉表征与多模态。学习对象不同，验证方式也不同：训练模型看数据、目标和轨迹，视觉表示看接口与检索空间，编辑权重看计算契约和副作用，推理优化看 FLOPs、IO 与实际延迟。分组是本 Wiki 的阅读组织，不是论文宣称的领域分类；原有文章地址不变。

## 从这里开始：先选一个问题

| 想回答的问题 | 入口 | 当前细分内容 |
| --- | --- | --- |
| 如何把 base LLM 训练成能推理、用工具的模型？ | [LLM 训练配方](training/README.md) | Rufus-Air 流水线；Agentic-RL Lab 算法、环境、蒸馏与评测 |
| 如何让图像／视频更符合偏好和任务？ | [扩散与视觉生成](diffusion/README.md) | DPO、去噪链上的 RL、视觉奖励和组合优势 |
| 如何直接表达像素，或学习统一多模态向量？ | [视觉表征与多模态](vision/README.md) | PixelBench／PRT；EmbeddingGemma 2 架构、训练与检索 |
| 如何判断推理成本与“实时”是否可信？ | [GPU 与内存](diffusion/05-gpu-and-memory-roofline.md) | CUDA 层次、Roofline、视频 token、吞吐与时延 |
| 如何让代理改进自己，而不被假指标带跑？ | [AI 自我改进与自动科研](self-improvement/README.md) | RSI、改进器、科学家系统、预算归因；连接已有 Autoresearch |
| 不走普通训练，能否直接读写权重？ | [权重编辑与解释](weight-space-programming.md) | WSP、QK／OV、权重几何、实验权限和回滚 |

### 目录关系

```text
深度学习专题
├─ LLM 训练与后训练
│  ├─ Rufus-Air：总览 → 数据／SFT／RLVR → Agent → 奖励 → 工程／评测 → 实验
│  └─ Agentic-RL Lab：目标 → 工具环境 → 蒸馏 → 信用分配 → 多模态／裁判 → 复现
├─ 扩散与视觉生成：偏好对 → 去噪轨迹 → 奖励设计
├─ 视觉表征与多模态：文本像素／PRT；共享骨干／统一向量／检索
├─ 推理与硬件：GPU／内存 → 视频成本
├─ 自动研究与评测：RSI 对象 → 改进器 → 科研反馈 → oracle／预算 → 保留或回滚
└─ 权重编辑与解释：WSP → 数学机制 → 权限／证据 → 本地实验
```

<a id="category-training"></a>

## 1. LLM 训练与后训练

[Rufus-Air 图文解读](training/rufus-air/README.md)从一份八阶段配方入手，先分清预训练、SFT、带可验证奖励的 RL、Agentic RL 和最终 RLHF。细分四章，另有标准库实验与来源／复现检查表。

配方不是一组能跨模型照抄的学习率：数据版本、输出格式、loss mask、真实采样 token、环境、停止条件都属于输入。相关概念与具体作者报告分别标注。

[Agentic-RL Lab 六章解读](training/agentic-rl-lab/README.md)把 Datawhale 仓库的 16 个入口映射到六类学习问题：优化目标、工具环境、在线蒸馏、长程信用分配、多模态与评分器、评测复现。10 张原创图和标准库实验帮助把公式对应到实际源码；同时说明远程训练成本、代码执行隔离与测量合同。

[Unified Training 九页读本](training/unified-training/README.md)把预训练、midtraining、SFT 和合适的 RL 目标放到共同似然视角。10 张机制图拆解成功条件分布、有限采样、token 分母、异步旧策略和混合调度；[离线验算](training/unified-training/lab.md)与[证据边界](training/unified-training/evidence-and-limits.md)帮助区分数学统一、实现一致和性能优劣。

<a id="category-diffusion"></a>

## 2. 扩散与视觉生成

[扩散读本](diffusion/README.md)仍保留六篇原文的整套阅读路线；这里把其中[偏好数据](diffusion/01-dpo-and-preference-pairs.md)、[奖励更新](diffusion/02-rl-through-denoising.md)、[评分与多目标](diffusion/03-rewards-judges-and-advantages.md)单列。LLM 的 token likelihood 与扩散的去噪 surrogate 不能因为都叫 DPO 就直接互换。

[扩散标准库实验](diffusion/lab.md)保留原位置，跨越奖励、硬件和视频三类教学问题，旁边的来源表也不移动。

<a id="category-vision"></a>

## 3. 视觉表征与多模态

[视觉表征导读](vision/README.md)把可见的像素表示、可检索的语义向量与生成分布分开。[PixelBench 八页专题](vision/pixelbench/README.md)解释文本调色板／网格、三类任务、检索指标、分辨率失败、两份 PRT 配方与证据边界；[原创离线实验](vision/pixelbench/lab.md)验算分母、相对聚合和官方单位。

[EmbeddingGemma 2 五页专题](vision/embeddinggemma-2/README.md)解释共享双向骨干、模态编码器、渐进蒸馏与对比目标、可截断向量和量化／索引迁移。它输出表示，不是图片或生成答案。两套读本由本 Wiki 的阅读路线连接，不混写模型、训练起点和 benchmark。

<a id="category-inference"></a>

## 4. 推理与硬件

先读[GPU、内存与 Roofline](diffusion/05-gpu-and-memory-roofline.md)，再读[实时视频估算](diffusion/06-realtime-video-estimates.md)。重点是计算吞吐、内存流量、容量与时延的不同含义，不用峰值参数替代指定 workload 的实测。

这些内容与训练工程相连，但“如何让一次前向快”与“如何让一次参数更新正确”仍是不同问题。

<a id="category-research"></a>

## 5. 自动研究与评测

[AI 自我改进与自动科研](self-improvement/README.md)将此前研究重组为八章：先分清答案、系统和改进器，再读智能体演化、参数适应、算法发现、科学家系统与内部研发。六张机制图、术语表、49 组公开引用及三个免费离线练习帮助判断“谁变强了”。

这组材料核验截至 2026-10-17，2026-11-04 整理入 Wiki；没有把入库日期当作全部论文及产品的最新核验日期。[来源与版本边界](self-improvement/sources.md)单独说明作者报告、公司自报与独立复现的区别。

[Autoresearch 与 oracle](diffusion/04-autoresearch-and-oracles.md)讨论搜索程序／配置的外层闭环。[训练配方的评测章](training/rufus-air/infrastructure-and-evaluation.md)讨论模型成绩的测量契约。这里并列的是研究方法，不把自动程序搜索误称为另一种模型损失。

评分器、持出集和预算是共同主题；但训练反馈、候选选择和最终测试应分开。

<a id="category-weights"></a>

## 6. 权重编辑与解释

本专题最早的读本是 **Weight-Space Programming／权重空间编程**。研究者报告一组让通用大模型读取、修改或构造其他网络权重的实验；我们把权限、失败案例和展望分开。[原文与核验记录](weight-space-programming-sources.md#blog)

- [图文解读，10 节](weight-space-programming.md)：9 张机制图，先理解权重如何表达计算。
- [本地实验与 12 道自测](weight-space-programming-lab.md)：手写控制器、神经元置换、平均失败与局部投影。
- [术语速查](glossary.md)：权重、激活、梯度、Logit、残差流、低秩与因果干预。
- [一手来源与实验权限](weight-space-programming-sources.md)：哪些已读，哪些尚未独立复现。

### WSP 原有 10 节目录

| 节 | 先回答一个问题 |
| --- | --- |
| [01 三种对象](weight-space-programming.md#wsp-01) | 权重、架构、输入含义，为什么缺一不可？ |
| [02 新在哪里](weight-space-programming.md#wsp-02) | 与训练、Hypernetwork、编译器和模型编辑如何区别？ |
| [03 手写一个网络](weight-space-programming.md#wsp-03) | 15 个参数能怎样实现一个小控制程序？ |
| [04 怎样读权重](weight-space-programming.md#wsp-04) | QK 与 OV 矩阵分别解释“看哪里”和“搬什么”？ |
| [05 八个实验](weight-space-programming.md#wsp-05) | 哪些只读静态权重，哪些使用运行反馈？ |
| [06 Qwen 案例](weight-space-programming.md#wsp-06) | 修复循环和获得新的数学能力，是同一件事吗？ |
| [07 权重几何](weight-space-programming.md#wsp-07) | 为什么只改一点也可能影响很大，平均还会出错？ |
| [08 证据强弱](weight-space-programming.md#wsp-08) | 一段合理解释如何升级成因果证据？ |
| [09 工程实现](weight-space-programming.md#wsp-09) | 如何把权限、评测、成本和回滚放进 Harness？ |
| [10 学习与判断](weight-space-programming.md#wsp-10) | 哪些结论可以带走，哪些暂时不能？ |

## 综合研究案例：OpenMOSS

[OpenMOSS 研究路线与技术机制](openmoss/README.md)保留 11 条研究方向、14 篇技术深解，跨越语音、视觉、生成、具身、Agent、后训练、安全和可解释性。它作为综合案例独立组织，不替代上面的六类基础读本。

先看[按问题选择的学习路线](openmoss/learning-roadmap.md)，再读对应方法与源码。原资料核查于 2026-10-17，2026-11-04 整理入 Wiki；没有将迁移日期当作团队全部新成果的核验日期。[来源与版本](openmoss/sources.md)。

## 建议阅读路线

**想辨认自改进证据**：从 [RSI 导读](self-improvement/README.md)进入 [DGM／Hyperagents／AIDE²](self-improvement/agent-evolution.md)，再做[预算和四格对照](self-improvement/lab.md)。想看行业先读科学家与工业研发两章，不把这些工作全称为严格 RSI。

**想读训练 recipe**：先读 [Rufus-Air 总览](training/rufus-air/README.md)，按四章顺序阅读；用实验页核对 batch 单位和 mask，而不是立即启动大模型训练。

**想读 Agentic RL 代码**：先读 [Lab 导读](training/agentic-rl-lab/README.md)与[优化目标](training/agentic-rl-lab/policy-objectives.md)，再走工具／环境和蒸馏路线。用[免费标准库验算](training/agentic-rl-lab/lab.md)检查学习信号；上游远程模型实验须另行确认预算与安全，不因本地 CPU 可运行就自动启动。

想学图像／视频生成的后训练与工程，先走[扩散专题的阅读路线](diffusion/README.md)。它独立于下面的权重空间编程路线，无需先读完 WSP。

**想学视觉表示**：先读 [PixelBench](vision/pixelbench/README.md)理解“显式输出什么”和评分器的作用，再读 [EmbeddingGemma 2](vision/embeddinggemma-2/README.md)理解“怎样学习评分／检索用的表示空间”。两套源码／配方阅读不等于真实模型复现。

**30 分钟直觉路线**：01 → 03 → 05 → 06 → 10。把“无梯度”和“无反馈”先分开，再理解局部修复。

**90 分钟机制路线**：顺序阅读，拿纸验算 03、04、07 的公式，最后完成自测。

**半天实践路线**：跑本地实验与测试，读作者发布的实验协议和评测代码，再写一页复现计划。半天不包括下载或重评真实语言模型。

推荐先具备矩阵乘法、ReLU、前向计算的基本概念。Transformer 不熟悉也可以读，04 节只引入本题所需的最小记号；它不是完整 Transformer 课程。

## 阅读约定与边界

- **作者报告**：归属于原文和作者发布的材料，不自动成为独立验证。
- **背景机制**：来自论文、研究者说明和框架文档，不宣称本篇发明了全部机制。
- **原创教学推导**：15 参数控制器、置换反例和投影数字由本 Wiki 构造，并有本地测试。
- **研究判断**：可能的解释和复现建议明确标为判断，不冒充作者的实验结果。

这些读本没有运行真实模型训练、模型编辑、下载权重或重跑模型 benchmark；标准库实验不调用模型服务。权重编程的自我改进和跨架构移植，以及训练配方的规模迁移，均不能按已实现的工程保证采购或部署。

配图按机制拆解，使用仓库本地 SVG 与 2× PNG；网页可放大，Markdown 可直接阅读。重建此组：

```bash
python scripts/render_figures.py --embed --id-prefix wsp-
python scripts/render_figures.py --check --id-prefix wsp-
```

相关阅读：[Physical AI 的学习与控制](../physical-ai/README.md)。手写静态策略、通过强化学习训练策略，以及在线规划，是不同机制。
