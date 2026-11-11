# Agent 记忆系统：保存什么，怎样维护，何时相信

整理与核查日期：2026-11-11。以 Anthropic 的 [The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory) 为入口，学习跨会话状态、读写与整理、检索、实验归因和信任边界。原文是工程研究分享，不是记忆系统的统一标准，也不是每一种架构的独立评测。

原创场景：一个采购助手记住“去年默认选供应商 A”。今年换了合同，用户又明确要求比较 B。历史记录可以省去重复调查，也可能把过期偏好变成错误指令。问题不是“记住得够不够多”，而是保存的信息是否适用、能否追溯、会不会覆盖当前需求。

## 六章阅读地图

| 想回答的问题 | 入口 |
| --- | --- |
| 记忆、上下文、压缩、数据库和权重更新怎样区别？ | [01 记忆与状态](01-memory-and-state.md) |
| 在线写笔记与事后 dreaming 分别负责什么？并发写入怎样不丢内容？ | [02 写入、维护与读取](02-write-manage-read.md) |
| 日志、笔记、wiki、索引与检索怎样搭配？ | [03 表示与检索](03-representations-and-retrieval.md) |
| “有记忆更好”的实验怎样做？如何计算全部成本？ | [04 评测与消融](04-evaluation-and-ablation.md) |
| 怎样处理过期经验、投毒、权限、删除和回滚？ | [05 安全与治理](05-safety-and-governance.md) |
| Anthropic 的四层结构和公开案例支持哪些结论？ | [06 原文案例与证据边界](06-anthropic-components.md) |

配套：[术语表](glossary.md) · [四个免费离线练习](lab.md) · [一手来源与版本](sources.md)。

## 先看一条完整路径

```text
经历／工具观察 → 可追溯记录 → 候选笔记 → 核验与整理 → 检索／预加载
                                                            ↓
更新与失效 ← 新证据与任务反馈 ← 执行结果 ← 当前任务中的采纳判断
```

这是本 Wiki 的教学路径，不是 Anthropic 的原始组件图。原文 Figure 1 的四层是 transcripts、memory notes、memory representations、injected context；dreaming 是跨层维护过程。[原文定义与图件核验](sources.md#architecture)

后文分清四个容易混淆的事实：写成功不代表内容正确；检索相关不代表当前适用；加入上下文不代表模型遵从；任务变好不代表模型参数更新。

## 三条学习路线

- **30 分钟**：读 01 的状态对照、03 的索引与原证据、06 的实验边界。
- **90 分钟**：顺序读六章，再跑四个小练习；重点检查来源、适用条件和版本。
- **工程验收**：先填写 04 的实验合同，再用 05 检查读写权限、污染、删除与回滚。真实用户资料和付费服务需要另行授权。

## 与已有专题连接

[OpenMOSS 的记忆与执行评测](../deep-learning/openmoss/06-agent-memory-and-executable-evaluation.md)深入解释“召回 → 采纳 → 行动 → 产物”的区别，及参考历史、固定起点的局限。

[实时助手的任务状态](../deep-learning/realtime-interaction/03-background-reasoning-and-tools.md)讨论用户改口后旧结果如何失效；持续记忆把类似问题延长到多次会话。

[AI 自我改进](../deep-learning/self-improvement/concepts-and-foundations.md)区分系统状态改善与改进器自身变强。保存经验并不自动构成严格 RSI。[Agent Sandbox](../agent-sandbox/README.md)和[AI／Agent 安全](../security/security-101/09-ai-and-agent-security.md)提供执行隔离与权限背景。

与[连续扩散／Flow 语言模型](../deep-learning/continuous-language-models/README.md)也要分开：它的 self-conditioning 通常是在一次生成过程中反馈上次预测，不是跨会话记忆服务。

## 执行与证据边界

本读本引用公开论文、官方文档与第一方示例；厂商自报、背景机制和原创建议分别标注。没有运行 Claude、内部语料实验、Managed Agents、真实数据库、在线攻击或付费模型。离线练习只操作合成记录和数字，不能证明某个产品的安全、任务收益或合规性。

下一篇：[01 记忆与状态](01-memory-and-state.md)。
