# 深度学习专题解读：从论文主张到可检验的机制

研究日期：2026-11-03。这里按“问题 → 数学直觉 → 实验证据 → 实现 → 边界”解读具体研究，不把单篇文章包装成整个深度学习领域的定论。

目录现拆为五个可折叠方向。学习对象不同，验证方式也不同：训练模型看数据、目标和轨迹，编辑权重看计算契约和副作用，推理优化看 FLOPs、IO 与实际延迟。分组是本 Wiki 的阅读组织，不是论文宣称的领域分类；原有文章地址不变。

## 从这里开始：先选一个问题

| 想回答的问题 | 入口 | 当前细分内容 |
| --- | --- | --- |
| 如何把 base LLM 训练成能推理、用工具的模型？ | [LLM 训练配方](training/README.md) | Rufus-Air：SFT、RLVR、Agentic RL、RLHF、基础设施 |
| 如何让图像／视频更符合偏好和任务？ | [扩散与视觉生成](diffusion/README.md) | DPO、去噪链上的 RL、视觉奖励和组合优势 |
| 如何判断推理成本与“实时”是否可信？ | [GPU 与内存](diffusion/05-gpu-and-memory-roofline.md) | CUDA 层次、Roofline、视频 token、吞吐与时延 |
| 如何让代理自动试验，而不被假指标带跑？ | [自动研究与评测](diffusion/04-autoresearch-and-oracles.md) | 实验契约、oracle、正确性准入、持出集 |
| 不走普通训练，能否直接读写权重？ | [权重编辑与解释](weight-space-programming.md) | WSP、QK／OV、权重几何、实验权限和回滚 |

### 目录关系

```text
深度学习专题
├─ LLM 训练与后训练
│  └─ Rufus-Air：总览 → 数据／SFT／RLVR → Agent → 奖励 → 工程／评测 → 实验
├─ 扩散与视觉生成：偏好对 → 去噪轨迹 → 奖励设计
├─ 推理与硬件：GPU／内存 → 视频成本
├─ 自动研究与评测：候选程序 → oracle → 保留或回滚
└─ 权重编辑与解释：WSP → 数学机制 → 权限／证据 → 本地实验
```

<a id="category-training"></a>

## 1. LLM 训练与后训练

[Rufus-Air 图文解读](training/rufus-air/README.md)从一份八阶段配方入手，先分清预训练、SFT、带可验证奖励的 RL、Agentic RL 和最终 RLHF。细分四章，另有标准库实验与来源／复现检查表。

配方不是一组能跨模型照抄的学习率：数据版本、输出格式、loss mask、真实采样 token、环境、停止条件都属于输入。相关概念与具体作者报告分别标注。

<a id="category-diffusion"></a>

## 2. 扩散与视觉生成

[扩散读本](diffusion/README.md)仍保留六篇原文的整套阅读路线；这里把其中[偏好数据](diffusion/01-dpo-and-preference-pairs.md)、[奖励更新](diffusion/02-rl-through-denoising.md)、[评分与多目标](diffusion/03-rewards-judges-and-advantages.md)单列。LLM 的 token likelihood 与扩散的去噪 surrogate 不能因为都叫 DPO 就直接互换。

[扩散标准库实验](diffusion/lab.md)保留原位置，跨越奖励、硬件和视频三类教学问题，旁边的来源表也不移动。

<a id="category-inference"></a>

## 3. 推理与硬件

先读[GPU、内存与 Roofline](diffusion/05-gpu-and-memory-roofline.md)，再读[实时视频估算](diffusion/06-realtime-video-estimates.md)。重点是计算吞吐、内存流量、容量与时延的不同含义，不用峰值参数替代指定 workload 的实测。

这些内容与训练工程相连，但“如何让一次前向快”与“如何让一次参数更新正确”仍是不同问题。

<a id="category-research"></a>

## 4. 自动研究与评测

[Autoresearch 与 oracle](diffusion/04-autoresearch-and-oracles.md)讨论搜索程序／配置的外层闭环。[训练配方的评测章](training/rufus-air/infrastructure-and-evaluation.md)讨论模型成绩的测量契约。这里并列的是研究方法，不把自动程序搜索误称为另一种模型损失。

评分器、持出集和预算是共同主题；但训练反馈、候选选择和最终测试应分开。

<a id="category-weights"></a>

## 5. 权重编辑与解释

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

## 建议阅读路线

**想读训练 recipe**：先读 [Rufus-Air 总览](training/rufus-air/README.md)，按四章顺序阅读；用实验页核对 batch 单位和 mask，而不是立即启动大模型训练。

想学图像／视频生成的后训练与工程，先走[扩散专题的阅读路线](diffusion/README.md)。它独立于下面的权重空间编程路线，无需先读完 WSP。

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
