# 06 Higgs 案例：把公开设计与证据缺口一起读

核查日期：2026-11-09。原文：Boson AI Team，[Higgs Realtime Duplex: Face to Face, Working in the Background](https://www.boson.ai/blog/higgs-realtime-duplex)，发布于 2026-11-05。[专题导读](README.md) · [来源记录](sources.md)。

## 1. 哪些是文章明确报告的？

| Boson 报告 | 读法与边界 |
| --- | --- |
| 45B MoE 前台模型 | 总参数口径；未公布单步激活参数，不能据此精确计算 FLOPs |
| 从文本模型继续训练约 2T 多模态 tokens | 是继续训练描述，不是声称从零总训练量或独立样本量 |
| 输入与输出按 160 ms 块推进 | 是时间粒度，不是端到端 TTFA 或打断停止延迟实测 |
| 前台自己推理、调工具，按需委派 | 是架构与能力描述；任务路由、失效和授权细节未完整公开 |
| 参考音频／图像进入输出解码器 | 声线与脸可换条件；不是推理能力变化或身份授权证明 |
| 多教师同策略蒸馏与模拟训练闭环 | 是训练路线描述；完整 loss、数据和训练实现未公开 |

表内事实来自[原文方法与训练章节][approach]；右栏是本 Wiki 的分析。没有据演示描述推断已经公开了可复现的模型权重或训练栈。

## 2. “低 token 率”怎样读？

原文给出每个块输入音频 1 个单位、输出音频 2 个，视频输入每六块一帧且每帧约十二个单位，输出脸部 2 个 latent。按该名义口径验算：[Boson 预算说明][budget]

$$
375+750+750+750=2625\ {\rm units/min}.
$$

这解释了文章约 2.6K／分钟的视听数量级，不是我们测得的 tokenizer 统计。各模态的 token／latent 还不应直接当作相同的文字计费单位。

文章还把压缩中的文字工作计入近期预算，并说明较旧历史另以文字保留。[预算说明][budget] 因此最近窗口不是整个会话的固定上限；不能只拿音频速率估算长会话内存，也不能把“会压缩”理解成永不丢信息。

原创工程建议：分别记录视听表示量、文字／工具量、摘要误差、KV／解码缓存、实际账单和任务表现。通过不同会话长度的实测，判断压缩是否伤害跨时段追问与任务状态。

## 3. 评测结论不该压缩成“全面领先”

原文的比较表包含多个任务、配置与来源；不同行的最好结果并不总属于 Higgs。Boson 声称核验了超过一半的对照成绩，但没有在文章里给出足以逐行审计的完整复现清单。[Boson benchmark 章节][benchmarks]

本 Wiki 不复制排行榜为自己的实测，也不把“不同任务有竞争力”重写成全面领先。读表时应逐行问：

1. 对照模型是哪一版本、什么 thinking 配置？
2. 是自报、引用榜单，还是在同一流水线重测？
3. 任务、用户模拟器、工具和评分器是否一致？
4. 样本量、置信区间、失败与缺测怎样处理？
5. 是否同时测了延迟和成本？

这些是原创审计问题。详见[评测篇](05-evaluation-and-safety.md)，不要从混合来源表推断唯一的系统排名。

## 4. 能力演示与可复现验证分开

原文介绍辅导、多人场景与后台工程任务的演示，但本次只阅读公开页面，未执行这些任务或实测视频时间线。[Boson 能力章节][capabilities]

一段演示可以帮助理解设计目标，仍不能证明打断成功率、旁谈误响应率、长会话稳定性、工具取消语义或身份保护。可复现验证需要可用接口、完整协议、失败案例和允许独立测量的条件。

## 5. 访问与成本：不要混用产品

截至核查日，所读发布页仍将 **Duplex API** 描述为即将推出，并提供 waitlist；页面同时链接已有 **Higgs Realtime** 产品及价格。这两个产品入口不能直接等同。[Boson Try it][try]

“每小时成本不超过人的十分之一”是文章中的设计目标，不是已验证的统一价格；既有人力成本假设的差异，也有后台模型、工具、渲染与传输的变量。[原文目标][targets]

本次没有查询账户开通状态、确认 Duplex 的独立报价或调用 API；发布页的状态也不能证明所有客户的访问状态相同。部署前应重新核验产品名称、能力、接口、报价与授权。

## 6. 值得带走的研究问题

本读本的判断是：真正值得继续学习的，不只是声音和脸，更是**连续时间里的策略与状态**。可以沿着三条可检验路线推进：

- 前台推理与选择性委派，能否在同一任务下改善质量／成本／时延权衡？
- 多教师训练，能否同时改善礼貌交互、任务成功与权限约束，而不是偏向某一个指标？
- 模拟闭环，能否迁移到真实、未见的人类时机和噪声，而不是只熟悉模拟器？

这些是后续问题，不是已经完成的实验结论。

下一步：[四个离线练习](lab.md) · [一手来源](sources.md)。

[approach]: https://www.boson.ai/blog/higgs-realtime-duplex#our-approach
[budget]: https://www.boson.ai/blog/higgs-realtime-duplex#reducing-cost-a-tight-token-budget
[benchmarks]: https://www.boson.ai/blog/higgs-realtime-duplex#benchmarks
[capabilities]: https://www.boson.ai/blog/higgs-realtime-duplex#capabilities
[try]: https://www.boson.ai/blog/higgs-realtime-duplex#try-it
[targets]: https://www.boson.ai/blog/higgs-realtime-duplex#what-a-good-interaction-model-needs
