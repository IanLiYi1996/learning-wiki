# 连续扩散与 Flow 语言模型：从噪声到联合文本生成

整理与核查日期：2026-11-11。入口是 Sophia Tang、Chanhyuk Lee、Floor Eijkelboom、Jinwoo Kim 的 [A Survey on Continuous Diffusion and Flow Language Models](https://www.alphaxiv.org/abs/2611.continuous-diffusion-flow-language-models)。这是 alphaXiv 预印本综述，不是名叫“Continuous”的新模型发布。

原创问题：假设两个位置只有两种合法组合，各占一半。如果分别把每个位置预测得很准，再独立抽样，仍可能拼出不合法组合。文本的词语、代码括号和谜题条件都有依赖；“一口气生成很多位置”不能仅靠各位置的好分数保证整体正确。

连续模型先在向量空间生成，再解码成离散 token。它提供联合变换、可微控制和少步采样的研究接口，但不是天然更准确、更省显存、更安全或更便宜的保证。

## 八章阅读地图

| 问题 | 入口 |
| --- | --- |
| 离散 token 为什么能由连续过程生成？联合与边缘分布差在哪？ | [01 离散文本与连续状态](01-discrete-text-continuous-state.md) |
| One-hot、embedding、latent、simplex、sphere 各有什么代价？ | [02 表示与解码](02-representations-and-decoders.md) |
| 扩散、flow matching、denoiser、score 和 velocity 怎样对应？ | [03 连续动力学与训练](03-diffusion-and-flow-matching.md) |
| 噪声调度、预测目标与 self-conditioning 为什么不能分开照抄？ | [04 训练与反馈](04-training-schedules-and-self-conditioning.md) |
| 采样器、guidance、提交／修订、输出长度和缓存怎样影响结果？ | [05 推理策略](05-sampling-guidance-and-commitment.md) |
| 少步求解、flow map、自蒸馏与直接生成器如何区别？ | [06 少步生成](06-flow-maps-and-few-step-generation.md) |
| 怎样比较训练计算、NFE、时延、gPPL、多样性与任务正确率？ | [07 扩展与评测](07-scaling-and-evaluation.md) |
| 连续状态怎样监测？哪些研究问题仍未解决？ | [08 安全与研究路线](08-safety-and-research-roadmap.md) |

配套：[术语表](glossary.md) · [五个免费离线练习](lab.md) · [来源、版本与综述边界](sources.md)。

## 先认清三个接口

```text
文字 token → 编码／表示 → 连续状态
                              ↓
                   迭代求解／学习到的映射
                              ↓
                  连续输出 → 解码器 → token
```

这条教学路径不规定唯一模型。有人用 one-hot 无需学习 token 编码；有人依赖预训练 encoder；有人将多个 token 压到少量 latents，又由 AR decoder 恢复文字。生成状态的压缩与最终文字的生成顺序，需要分别检查。

## 阅读路线

- **30 分钟**：01 的联合分布反例 → 02 的接口表 → 07 的测量合同。
- **90 分钟**：01～06 顺序阅读，手算 velocity 转换与 flow map 合成。
- **半天练习**：跑五个小数组实验，再用 07／08 填写一个固定数据、质量和总预算的研究方案。这里的半天不包括真实模型训练。

本读本统一采用生成时间 **t=0 是噪声，t=1 是数据**。有的扩散论文用相反时间方向；比公式前先对齐约定。物理响应时间、采样步数、网络函数调用数也不是同一个量。

## 与已有知识连接

[图像／视频扩散后训练](../diffusion/README.md)解释偏好、奖励与工程成本；本读本补上文字的表示和联合解码问题，不把图像的噪声 surrogate 直接换成 token likelihood。

[OpenMOSS 离散扩散与缓存](../openmoss/13-diffusion-language-models.md)解释 mask、提交与近似 KV 复用。离散状态过程也可以采用连续时间；“连续时间”不代表本篇所说的连续状态。

[GPU 与内存](../diffusion/05-gpu-and-memory-roofline.md)帮助区分计算、带宽和容量。[实时交互](../realtime-interaction/README.md)解释“少步”为什么不直接变成对话低时延。

[Agent 记忆系统](../../agent-memory/README.md)保存跨会话经验；这里的 self-conditioning 多指一次生成内部的预测反馈，两者不能因为都复用信息就合并为同一种学习。

## 来源与执行约定

综述 v1 的文献截止日是 2026-11-02，alphaXiv 标示提交日 2026-11-08，作者项目在 2026-11-09 公告。文献目录会继续更新；本读本的追踪日期不代表综述已经覆盖后来全部修订。[来源身份](sources.md#survey)

以下区分论文机制、作者报告、原创推导和待验假设。没有下载模型权重、使用 GPU、运行真实语言模型或重新测排行榜；小数组通过测试不等于实现了 FLM、CFM、ELF 或完整扩散 trainer。

下一篇：[01 离散文本与连续状态](01-discrete-text-continuous-state.md)。
