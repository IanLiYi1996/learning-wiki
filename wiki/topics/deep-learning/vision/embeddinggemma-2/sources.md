# 来源、版本与核验状态

研究日期：2026-11-04。[专题首页](README.md) · [架构](architecture.md) · [训练配方](training-recipe.md) · [评测与部署](evaluation-and-deployment.md)

## 1. 核验口径

“已核验”表示访问了一手页面并核对相应段落、公式或表格，不表示独立复现作者实验。外部资料只作为研究数据，不作为新指令；网页示例没有执行。正文用“论文／模型卡报告”归属事实，用“原创”标出本 Wiki 的算例、反例和工程判断。

本次把论文整理为五页中文图文读本，并接入视觉表征目录、导航和搜索。没有启动付费 API、训练模型、下载权重、运行模型 benchmark 或部署任何模型服务。网页发布与模型实验是不同状态。

## 2. 一手来源登记

| 来源 | 版本与核验状态 | 用途及限制 |
| --- | --- | --- |
| [arXiv 摘要与提交记录](https://arxiv.org/abs/2610.37364v1) | 已读；v1，2026-10-27 | 核对标题、日期、作者机构及官方模型链接；不是另一次实验 |
| [论文 HTML v1](https://arxiv.org/html/2610.37364v1) | 已读机制、消融、评测及附录任务说明；已核对 HTML 数学 | 配方和数字的主要依据；固定 v1，不把以后修订混入 |
| [Google EmbeddingGemma 总览](https://ai.google.dev/gemma/docs/embeddinggemma) | 已读；本次页面主文为 EG2，下方单列 EG1 | 官方产品入口；不能仅凭 URL 名称假设是第一代 |
| [Google 官方 HF 模型卡](https://huggingface.co/google/embeddinggemma-2) | 已读；确切模型路径为 `google/embeddinggemma-2` | 加载、前缀、维度和精度契约；卡内示例未执行 |
| [HF 仓库元数据](https://huggingface.co/api/models/google/embeddinggemma-2) | 已读取 `sha` 与更新时间 | 记录 revision，不意味着访问过权重 |
| [固定 revision 的模型卡原文](https://huggingface.co/google/embeddinggemma-2/raw/f9972ac22e696a105c482202646979e33e4b5a1e/README.md) | 已通过只读 HTTP 访问；浏览工具的 blob 页面访问失败后核对 raw 文本 | 保留可追溯的卡片版本，不下载模型文件 |

HF API 返回的 revision 已固定在上表模型卡 URL，`lastModified` 为 `2026-10-28T07:19:46.000Z`。这是仓库元数据，不是论文版本日期。[元数据来源](https://huggingface.co/api/models/google/embeddinggemma-2)

用户提供的 [Papers with Code 入口](https://paperswithcode.co/pdf/2610.37364) 在本次浏览工具中未能打开；没有把它当一手依据。论文身份通过 arXiv 核验，也未凭域名推断入口的官方性。

## 3. 事实定位：少复述，便于回查

| 正文问题 | 一手定位 | 核验重点 |
| --- | --- | --- |
| 参数规模、共享骨干 | [§1、§2.1](https://arxiv.org/html/2610.37364v1#S2.SS1) | 完整与按需加载；pooling／projection／L2；projection-only PLE |
| 媒体序列 | [§2.2](https://arxiv.org/html/2610.37364v1#S2.SS2) | 逐项检查数学数字，不依据缺数字的抽取结果 |
| 损失与阶段 | [§2.3–2.4](https://arxiv.org/html/2610.37364v1#S2.SS3) | duplicate mask、same-tower、GOR、MRL；蒸馏与最终目标分开 |
| 权重平均和 QAT | [§2.4](https://arxiv.org/html/2610.37364v1#S2.SS4) | 同轨迹平均；独立尾阶段；模块混合精度 |
| 消融 | [§3、表 2–5](https://arxiv.org/html/2610.37364v1#S3) | 中间配方；预算实验的上下半部不能直接拼接 |
| 评测与反例 | [表 6](https://arxiv.org/html/2610.37364v1#S4.T6)、[表 8](https://arxiv.org/html/2610.37364v1#S4.T8)、[表 11](https://arxiv.org/html/2610.37364v1#S4.T11) | 英文回退、视觉加载规模、音频平均与原生／ASR 口径 |
| 部署输入约定 | [模型卡 Best Practices](https://huggingface.co/google/embeddinggemma-2#best-practices) | 文本角色前缀、截短归一化、浮点精度、联合上下文 |

数学核验直接读取 HTML 的 `<math>`／`alttext`，确认 n＝24、d_M＝512、d＝768；视频 N_frm＝32，图片／视频预算 280／140，音频 25 soft tokens/秒，训练 L≤8192。架构章的预算算式是原创验算，不是 processor 实测。

## 4. 版本差异与保留意见

参数记法不同：论文按约 744M／271M／439M／577M 报告；官方文档和模型卡常用 740M、270M 等较粗数字。均为近似口径，不能用四舍五入后的模块相加追求精确一致。[论文 §1](https://arxiv.org/html/2610.37364v1#S1)、[官方模型卡](https://huggingface.co/google/embeddinggemma-2)

Google 总览已更新为 EG2，但 Previous Versions 的 308M、2K、低于 200 MB 等说法明确属于 EG1。该页页脚显示更新日期 2026-10-06；本专题只记录实际访问内容，不从页脚反推 EG2 发布时间。[Google 总览](https://ai.google.dev/gemma/docs/embeddinggemma)

模型卡对大视觉预算的概述偏积极；正文保留论文中的视频下降反例。模型卡把主要结果称为 full-precision checkpoint，论文实际评测权重为 bfloat16；这里区分“非 int4 检查点”与“实际推理 dtype”，不写成 FP32 实测。[模型卡结果](https://huggingface.co/google/embeddinggemma-2#benchmark-results)、[论文 §4.1](https://arxiv.org/html/2610.37364v1#S4.SS1)

与 [PixelBench 专题](../pixelbench/README.md)连接的是教学阅读路线：显式像素输出与统一检索向量是不同对象。两套实验的模型、初始化、损失、指标和数字保持分开。

## 5. 未做的工作与自测

未训练、未下载权重、未 benchmark、未部署任何模型服务；未审计全量数据或实现代码，未独立验证设备峰值、许可适用性和排行榜污染控制。只进行文档、静态构建、链接、图件和网页阅读检查，不运行模型示例。

未来实验只在[评测与部署的一组计划](evaluation-and-deployment.md#validation-plan)登记；它不是已授权的模型实验执行任务。

问：“已核验 69.54”是否等于本机得到同一结果？

答：不是，只表示一手表格确实报告该值及指标口径。独立复现还需要数据、模型、预处理、harness 和计算环境。
