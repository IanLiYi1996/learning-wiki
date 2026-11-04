# 视觉与视频理解：从离线感知到 MOSS-VL 的持续互动

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

视觉模型首先需要读懂已经给定的证据：图中的文字、物体位置、多个画面的关系，以及视频事件发生的先后。实时互动在这些能力上增加了时间约束：证据尚未全部到达，用户却已经提问；模型正在回答，画面又可能改变。离线理解与实时互动因此应放在同一条研究线中，但分别评价。[MOSS-VL §1、§3–4](https://arxiv.org/html/2608.15045v1)

助手讲解屏幕操作时，用户可能随时提问，窗口也可能在回答中途变化。它需要继续接收画面、修正旧判断，并在该等待时保持沉默。离线视频问答通常只需处理已经给定的片段，流式互动则要维护不断变化的证据。[MOSS-VL §1、§4.2](https://arxiv.org/html/2608.15045v1)

定期把全部历史重新交给模型，会重复处理旧内容；只保留文字摘要，又可能丢掉后续需要的视觉细节。训练数据也要改变：除了正确答案，还得教模型等待、触发提醒和处理中断。

MOSS-VL 将视觉表示与文字生成分开，让新帧追加到视觉注意力缓存；再用位置编码、时间戳和可见性约束表达“当时看到了什么”，通过 Realtime-SFT 学习发言时机。它的设计价值在这些环节的配合。[论文 §2、§4](https://arxiv.org/html/2608.15045v1)

## 离线能力从哪里来？

MOSS-VL 的视觉理解并非只靠最后一轮实时对话数据。预训练先冻结视觉和语言骨干，对齐 projection 与 cross-attention；随后全参数训练，加入图像／视频 caption、OCR、空间和时间 grounding、图文交错文档及推理数据。后期再增加高质量与长上下文样本，得到 Base；常规 SFT 得到 Instruct，Realtime-SFT 才继续教发言、沉默和修正。论文这两轮后训练均为监督学习，没有使用 RL 或 thinking mode。[§3–4、表 3–4](https://arxiv.org/html/2608.15045v1)

这个训练顺序解释了研究动机：先建立对场景和事件的理解，再把已有感知能力接入不断变化的互动。OCR 教识别文字，grounding 教证据位于哪里，时间标注教事件发生于何时；实时数据则教当前时刻是否已经有足够证据开口。单靠实时开关 token，不能替代这些感知基础。

较早的 MOSS-Video-Preview 已在 Llama-3.2-Vision 上探索视觉／语言解耦和实时模式。MOSS-VL 报告将其视为前期探索，同时明确重设计了模型栈；不能据此把两套层数、骨干或检查点当成相同模型。当前 Preview 仓库也已链接独立报告 `2606.07639`，不应沿用“只有演示、没有论文”的旧判断。[Preview 固定 README](https://github.com/OpenMOSS/MOSS-Video-Preview/blob/e3837691f47af7f9d183e10bf43d2f2522db157c/README.md)、[Preview 报告](https://arxiv.org/abs/2606.07639)、[MOSS-VL §1](https://arxiv.org/html/2608.15045v1)

## 1. 新帧怎样进入正在生成的回答？

### 1.1 视觉缓存与文字状态分开

设文字状态为 `H_t∈R^(T×d)`，视觉表示为 `H_v∈R^(N×d)`。拼接型架构在语言层对 `[H_t;H_v]`做自注意力；新视觉 token 会参与同一序列的位置和可见性结构。MOSS-VL 让文字自己维持因果序列，视觉只提供跨注意力 K/V。48 层里 36 层是原语言层，12 层为新增跨注意力，位置为 2、6、…、46。[论文 §2.1–2.2](https://arxiv.org/html/2608.15045v1#S2.SS1)、[发布配置](https://huggingface.co/OpenMOSS-Team/MOSS-VL-Realtime/blob/d1f71a588deaf2b9b9cea7c6fff66cb10847cc86/config.json)

简化地写一次交互：

```text
Q = RMSNorm(H_t W_q)
K = RMSNorm(H_v W_k)
V = H_v W_v
A = softmax(R_Q(Q) R_K(K)^T / sqrt(d_head) + M) V
H'_t = H_t + tanh(g_a)·W_o A
H''_t = H'_t + tanh(g_f)·FFN(LN(H'_t))
```

两个 `g` 都是标量，初值为零；Q 用 32 heads，K/V 用 8 heads。源码 `MossVLTextCrossAttention` 第 619–665 行实现投影和位置旋转，`MossVLCrossAttentionDecoderLayer` 第 792–841 行实现门控。[固定实现](https://huggingface.co/OpenMOSS-Team/MOSS-VL-Realtime/blob/d1f71a588deaf2b9b9cea7c6fff66cb10847cc86/modeling_moss_vl.py#L604)

### 1.2 零门控到底保留了什么？

对 `h'=h+tanh(g)f_θ(h,v)`，在 `g=0` 时：

```text
h' = h
∂h'/∂θ = 0
∂h'/∂g = f_θ(h,v)
```

这使新增模块初始是恒等残差路径：第一步主要先让 gate 获得打开方向，新分支参数的梯度要随 gate 打开才进入。它有助于避免随机视觉连接立刻扰乱语言网络，但**只保证初始化时的函数连续性，不保证后续全参数训练没有遗忘**。论文第 1 阶段冻结视觉／语言骨干，只训练 projection 和 cross-attention；之后的阶段全参数训练，因此最终文本能力必须再测，不能从零 gate 直接推定。[论文 §3、表 4](https://arxiv.org/html/2608.15045v1#S3)


### 1.3 追加缓存仍有成本

新帧只产生新的视觉表示，并在每个跨注意力层计算新 K/V 后追加；没有新帧时读取旧缓存。源码第 661–678 行明确：新 key 只旋转一次，已缓存的 key 已带 RoPE；每个新 query 则必须重新旋转。不要对缓存 key 重复施加位置旋转。[固定实现](https://huggingface.co/OpenMOSS-Team/MOSS-VL-Realtime/blob/d1f71a588deaf2b9b9cea7c6fff66cb10847cc86/modeling_moss_vl.py#L647)

按配置估算， 只算 12 层视觉 K/V、8 个 KV heads、head_dim=128、BF16：

```text
M_visual_KV = 12 × 2(K,V) × N × 8 × 128 × 2 bytes
            = 49,152 N bytes
```

假设 `N=100,000`，仅这部分约 4.92GB（十进制），尚未计模型、视觉表示、文字 KV、工作区和分配开销。GQA 节约了缓存；它没有取消缓存随帧数增长的事实。

一次 query 跨注意力仍要读取可见历史 K/V，因此每步成本随可见 `N` 增长。相对拼接型语言栈，可近似比较：

```text
拼接：L·O((T+N)^2)
解耦：L_self·O(T^2) + L_cross·O(TN) + 视觉编码器成本
```

这是忽略常数、前馈和缓存实现的量级比较。它解释“减缓增长”，不证明“无限视频、固定内存、固定延迟”。[论文 §2.5、Figure 4](https://arxiv.org/html/2608.15045v1#S2.SS5)

## 2. 位置、秒数和可见证据分别怎样表示？

### 2.1 三种机制的分工

| 机制 | 实际回答的问题 | 不负责的事情 |
|---|---|---|
| XRoPE | 文字与视觉 patch 在共同逻辑序列／空间坐标中的关系 | 现实世界过去了多少秒 |
| 时间戳 token | 此帧来自录像／流的哪个秒数 | 阻止模型访问未来帧 |
| Cross-attention mask | 此文字 query 当时有权看到哪些视觉证据 | 告诉模型事件具体时长 |

论文明确说 XRoPE 的 `t` 是相对序列坐标，不是 wall-clock time；真实时间通过 `<|time_start|>X.X seconds<|time_end|>`进入文字。[论文 §2.3–2.5](https://arxiv.org/html/2608.15045v1#S2.SS3)

### 2.2 XRoPE 坐标与真实时间

论文用：

```text
文字 token：p_text=(x,x,x)
帧内 patch：p_(a,b)=(t,t+a,t+b)
帧结束／占位：x=max(t+h',t+w')
下一文字：x+1
```

例如： 前文结束后，某帧 anchor `t=10`，合并后网格 `h'=2,w'=3`：

| 单元 | XRoPE 坐标 |
|---|---|
| 左上 patch | (10,10,10) |
| 右上 patch | (10,10,12) |
| 右下 patch | (10,11,12) |
| separator／文字占位 | (13,13,13) |
| 下一文字 | (14,14,14) |

若这帧来自 0.2 秒，或者来自 8 秒，上表本身可以一样。改变抽帧间隔、丢帧或原生分辨率，也会改变“逻辑位置差”与“真实秒数差”的对应。**所以不能从相邻 RoPE 坐标直接推出相邻真实时刻。** 时间戳不是装饰字段，而是非均匀抽帧中的必要补充。[论文式 (1)、§2.4](https://arxiv.org/html/2608.15045v1#S2.SS3)

### 2.3 mask 限制未来证据

令第 `i` 个文字 query 可以看到的视觉前缀长度为 `b_i`：

```text
M[i,j] = 0      if j < b_i
         -∞    otherwise
```

回答“事件现在出现了吗”的训练必须按发言时刻决定 `b_i`。如果整段视频都可见，即使文字标着 2 秒，模型也可能根据 10 秒的画面提前回答；仅修改位置编码不能修复这种未来泄漏。

特殊 FA3 后端把稠密 `T×N` mask 压缩成每个 query 一个 int32 前缀边界，不可见 tiles 不计算；这是利用“所有有效证据构成前缀”的结构，不是适用于任何任意稀疏 mask 的通用压缩。[后端说明及 mask contract](https://github.com/OpenMOSS/MOSS-VL/blob/a3feb74da1a5184bfc10be59b58a33874231f51e/third_party/flash-attention-src/README.md)

**实现审计：** 当前 HF 参考实现的 `_expand_cross_attention_mask` 第 1546–1553 行仍创建稠密张量；cross-attention 第 687–689 行在 FA2／FA3 标记下走 SDPA interface。论文特殊训练 kernel、HF 参考推理、SGLang serving 是不同路径。下载 HF 模型并填一个 FA 参数，不能自动宣称复现了论文的特殊 mask 性能。[HF mask 实现](https://huggingface.co/OpenMOSS-Team/MOSS-VL-Realtime/blob/d1f71a588deaf2b9b9cea7c6fff66cb10847cc86/modeling_moss_vl.py#L1489)、[注意力调用](https://huggingface.co/OpenMOSS-Team/MOSS-VL-Realtime/blob/d1f71a588deaf2b9b9cea7c6fff66cb10847cc86/modeling_moss_vl.py#L685)

## 3. 模型怎样学会发言和等待？

### 3.1 不另加决策头，意味着什么？

Realtime 数据把帧到达后的输出分成 silence、response＋文字、文字结束＋silence。发言／等待仍由语言模型 next-token prediction 决定，只增加两个状态 token，不是再训练一个独立 detector。一个回复可分布在连续帧的多个槽位中。[论文 §4.2](https://arxiv.org/html/2608.15045v1#S4.SS2)

这个表示把“观察”“选择发言”“发言内容”纳入一条自回归轨迹。但 ordinary QA 的目标只有答对，流式目标还包括正确等待、及时触发、避免重复触发，以及新事件打断旧答案时修正。

论文对 assistant token 计算：

```text
L = Σ_i m_i w_i CE_i / Σ_i m_i
状态 token：w_i=α_(y_i)(1-p_i)^γ，γ=2
普通回答文字：w_i=1
α_k=(n_s+n_r)/(2 n_k)
```

`n_s,n_r` 是全局 batch 中 silence／response 的计数，不是各 GPU 单独估计。其作用是让稀有的发言监督不会被大量等待槽淹没。[论文 §4.3、式 (2)](https://arxiv.org/html/2608.15045v1#S4.SS3)

### 3.2 为什么这不保证发言概率已经校准？

先忽略 focal 项、只考虑二状态条件分布。若真实发言概率为 `p`，两类权重为 `w_R,w_S`，加权 CE 的点态最优预测为：

```text
q_R = w_R p / [w_R p + w_S(1-p)]
```

当真实先验极不平衡、权重近似逆频率时，`q_R` 不再等于真实发言概率。focal loss 和完整词表会进一步改变这一简式，不能把该式冒充论文算法的完整解；但它说明 **“学会稀有响应”与“输出概率可直接作为事件置信度”不同**。

例如： 真实事件频率 1%，逆频率权重约使该频率下的二类预测移向 50%。这不等于模型突然发现了一半时刻都有事件，而是代价敏感训练改变了决策分布。部署若需要低误报，应另测 precision–recall、每分钟误报、触发延迟和阈值敏感性，不能只看 response 数量。

### 3.3 EOS masking 的消融应该怎样读？

论文不监督 assistant 回合末尾 end token：流式中用户插话结束当前消息，却不代表世界和会话结束。控制变量比较报告 emission frequency +39%、mean reply length +68%，为作者自报。[论文 §4.3](https://arxiv.org/html/2608.15045v1#S4.SS3)

这支持“回合边界监督会压制后续发言”的解释，但**发言更多／更长不等于更准／更及时**。正确的后续消融应该在相同事件上测新增发言有多少必要、有多少重复或错误，而不是把产量提升本身视为全面互动改进。

## 4. 帧处理得快，还可能提醒得晚

HF 的 `MossVLRealtimeSession.push_frame` 第 2375–2420 行要求时间戳不递减；队列满且 `drop_oldest=True` 时丢掉旧的待处理帧，插入新帧。默认未显式给时间戳时按 `time.monotonic()`补入。[固定源码](https://huggingface.co/OpenMOSS-Team/MOSS-VL-Realtime/blob/d1f71a588deaf2b9b9cea7c6fff66cb10847cc86/modeling_moss_vl.py#L2375)

例如， 一个告警目标只出现 100ms，摄像头确实拍到了它，但服务积压将对应帧丢掉。模型最终对其沉默，不证明模型不会识别该事件；它根本没得到证据。

反过来， 为避免丢帧而保留所有帧，服务在积压几秒后才发出正确提醒。离线判为正确，现实时间上却失去用途。

因此，完整实验需要同时记录：

```text
capture_timestamp → enqueue → encode → decode decision → output → user playback
```

分开报告采样遗漏、queue drop、数据年龄、TTFT、持续 token 速率及端到端 trigger latency。模型编码可追加，是实现实时性的一部分；backpressure 与调度还会改变其实际观测分布。

## 5. 实验测到了哪些互动能力？

论文把可互动能力分成层级，量化评价覆盖 L2–L4；L5 即生成期间持续感知，主要由演示和代码支持，专门量化 benchmark 仍缺。离线对比也非全胜，例如 MMMU 的差距不能由流式指标掩盖；而不同采帧预算又限制了跨模型因果比较。[论文表 1、表 5、§6–7](https://arxiv.org/html/2608.15045v1#S6)

这些结果支持模型处理持续输入和选择发言时机。长期运行中的遗漏、误报与队列积压仍需任务级测试，尤其不能把演示直接当作风险告警可靠性。

### 相关评测回答了什么不同问题？

GAOKAO-MM 以中文多模态考题测知识与图文推理，不是实时视频模型；FutureOmni 根据视听前缀预测后续事件，测的是未来推断，不含候选动作干预。它们可以补充对视觉推理与时序理解的认识，却不能证明模型已学会实时发言或物理规划。不能把一次未来事件预测成功，直接解释成可供机器人反事实规划的世界模型。[GAOKAO-MM 仓库](https://github.com/OpenMOSS/GAOKAO-MM)、[FutureOmni 论文](https://arxiv.org/abs/2601.13836)

## 资料与代码版本

论文为 Pengyu Wang 等的 [MOSS-VL Technical Report](https://arxiv.org/html/2608.15045v1)，相关论文与项目入口见[来源索引](sources.md)。材料核查于 2026-10-17，实验分数来自作者，计算示例为本文推导；未运行 GPU 基准。

源码依据 GitHub `a3feb74da1a5`、Realtime HF `d1f71a588dea`。文中行号对应该版本的 `modeling_moss_vl.py`。
