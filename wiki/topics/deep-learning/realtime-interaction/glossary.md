# 实时交互术语速查

整理日期：2026-11-09。[专题导读](README.md) · [来源与证据](sources.md)。以下是本读本采用的简化解释，不替代每篇论文的精确定义。

| 术语 | 本读本里的含义 | 不要混成什么 |
| --- | --- | --- |
| Full duplex／全双工 | 输入与输出可并行持续处理 | 不只是流式 TTS |
| Streaming／流式 | 逐段处理或输出，不等完整序列 | 不保证双工或低端到端延迟 |
| Turn-taking／轮次控制 | 判断谁继续、谁接话、何时让步 | 不只是检测静音 |
| VAD | 检测语音活动的信号或模块 | 不等于意图／说话对象识别 |
| Backchannel | “嗯”等不夺走话语权的倾听反馈 | 不一定是在抢答 |
| Barge-in | 用户在系统输出时介入 | 不自动代表取消后台任务 |
| Addressee／说话对象 | 一段发言面向谁 | 发言者身份不等于对象 |
| Neural codec | 将波形与较低速率表示相互转换 | 不等于 ASR 转写 |
| Codebook／码本 | 量化时可选的表示集合 | 不等于语言模型词表 |
| Latent | 编码器产生的隐表示 | 不保证与 token 等计费 |
| Causal／因果 | 不依赖未到达的未来输入 | 不等于零等待 |
| Lookahead | 前端／解码需要的额外未来片段 | 不等于模型思考预算 |
| TTFA | 从明确起点到第一段音频的时间 | 不一定是第一段有用答案 |
| Flow matching | 学习连续路径的速度场来生成数据 | 不等于一层即可生成 |
| DiT | 用 Transformer 建模扩散生成 | 去噪时间不是会话物理时间 |
| MoE | 按路由使用专家的模型结构 | 总参数不等于每步激活参数 |
| Delegation／委派 | 将子任务交给其他执行者／模型 | 不等于每轮必须委派 |
| Provisional result | 尚未最终核验的中间结果 | 不应直接当任务完成 |
| Intent version | 当前用户需求的版本标记 | 不是结果到达顺序 |
| On-policy distillation | 在学生访问的轨迹上接受教师反馈 | 不是 DPO 或教师采样示范的同义词 |
| GRPO | 同题采样组中利用相对奖励优化策略 | 不保证每个步骤正确 |
| MOPD | 多教师同策略蒸馏的描述性名称 | 名称不公开教师混合或 loss |
| RSI | 研究递归自我改进的概念 | 循环训练不充分证明改进器变强 |
| Pass@1 | 单次尝试的成功度量，依具体协议 | 不是多次择优后的最高表现 |
| p95 latency | 约 95% 观测不超过的时延分位数 | 不等于平均值或固定块长度 |

通用交互／codec 入口：[01](01-duplex-and-turn-taking.md)、[02](02-streaming-codecs-and-rendering.md)。任务状态：[03](03-background-reasoning-and-tools.md)。训练：[04](04-training-and-distillation.md)。测量：[05](05-evaluation-and-safety.md)。Higgs 专属事实见[06](06-higgs-realtime-duplex.md)，来源逐项见[证据页](sources.md)。
