# 实时全双工交互：一边听看，一边说话与做事

整理与核查日期：2026-11-09。以 Boson AI 在 2026-11-05 发布的 [Higgs Realtime Duplex 原文](https://www.boson.ai/blog/higgs-realtime-duplex)为入口，学习实时语音、多模态流、交互控制和后台任务的共同原理。这不是原文翻译，也不是模型部署手册。

想象一个仓库助手：你一边走动，一边问库存；它看到货架，开始查询；你临时改了型号，它停止旧回答；查询尚未结束，你又向同事说话，它不插嘴。这个原创场景里，答案文字正确只是其中一个要求。什么时候听、什么时候说、旧任务还要不要继续，同样决定系统是否可用。

## 先选一个问题

| 你想理解什么 | 阅读入口 |
| --- | --- |
| “流式”与“全双工”到底差在哪里？怎样区分打断和附和？ | [01 全双工、轮次与说话对象](01-duplex-and-turn-taking.md) |
| 声音怎样变成 token？为什么流分块不能代替响应延迟？ | [02 编解码、因果生成与流式预算](02-streaming-codecs-and-rendering.md) |
| 模型说话时如何查资料？用户改口后，旧结果怎么办？ | [03 后台推理、工具与任务状态](03-background-reasoning-and-tools.md) |
| 教师如何教会学生“何时行动”？OPD、GRPO 和 RSI 如何区别？ | [04 训练、蒸馏与改进闭环](04-training-and-distillation.md) |
| 高 QA 分数为什么不等于好的交互？哪些隐私与权限需要验收？ | [05 评测与安全](05-evaluation-and-safety.md) |
| Higgs 具体公开了什么？哪些结论仍缺少证据？ | [06 Higgs 案例与证据边界](06-higgs-realtime-duplex.md) |

辅助页：[术语速查](glossary.md) · [四个免费离线练习](lab.md) · [一手来源与核验记录](sources.md)。

## 三条学习路线

**30 分钟直觉路线**：读 01，接着读 03 的订单改口场景，最后看 06 的证据表。先把“有声音”“能边生成边播放”“能同时听说”“能正确管理并发任务”分开。

**90 分钟机制路线**：按 01 → 02 → 03 → 04 → 05 阅读，再做离线练习。重点是物理时间、生成步数和任务状态三个不同坐标，不需要先下载语音模型。

**工程评估路线**：从 05 的验收合同倒推：要记录哪些时间戳、版本、权限、失败和成本？再回到 02 与 03 找需要实现的接口。06 的厂商自报不直接充当自己服务的验收数据。

## 与已有专题连接

- [OpenMOSS 语音表示与生成](../openmoss/01-audio-representation-and-generation.md)：更深入地解释语义／声学表示、残差量化与语音生成；本专题补上连续交互与任务控制。
- [OpenMOSS 视频时间与缓存](../openmoss/02-streaming-video-time-and-cache.md)：理解视频采样、物理时间和历史状态；低帧率不自动等于足够的动作理解。
- [Agentic-RL Lab 的 OPD／OPSD](../training/agentic-rl-lab/on-policy-distillation.md)：对照真实实现中的采样者、teacher 和概率反馈。它不是 Boson 的训练代码。
- [GPU 与内存 Roofline](../diffusion/05-gpu-and-memory-roofline.md)：把 token 预算与计算、带宽、容量和时延分开。
- [AI 自我改进的概念与理论](../self-improvement/concepts-and-foundations.md)：区别改善模型与改善“改进器”；模拟失败闭环不是严格 RSI 的充分证据。
- [Agent Sandbox 与权限边界](../../agent-sandbox/README.md)：实时对话可以提议操作，执行写入仍需要隔离与授权。

## 本读本的证据约定

“Boson 报告”只表示公开文章的陈述；“背景机制”由对应一手论文或文档支持；“原创教学”是本 Wiki 的推导、场景、验收建议和小数组实验。具体引用与缺口见[来源页](sources.md)。

本次没有运行 Higgs 模型、观看并实测演示视频、调用产品 API、下载权重或重跑 benchmark。离线代码不使用麦克风、摄像头、网络、GPU 或付费服务；通过它的测试，只证明教学算例和文档合同一致。

下一篇：[01 全双工、轮次与说话对象](01-duplex-and-turn-taking.md)。
