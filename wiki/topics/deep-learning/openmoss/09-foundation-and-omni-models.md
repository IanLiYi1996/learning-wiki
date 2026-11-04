# 从 MOSS 到 AnyGPT：先学会对话和用工具，再统一模态接口

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

早期 MOSS 和 AnyGPT 回答了两个不同问题。MOSS 要把语言预训练能力变成可交互、可调用外部工具的助手；AnyGPT 要让同一个语言建模框架接收并生成文字以外的内容。前者的重点在对话数据和执行协议，后者在模态表示与数据对齐。[MOSS 论文][MP]、[AnyGPT，§1–4][AP]

这两项工作是理解 OpenMOSS 路线的起点，但不能把今天的项目理解成同一个 MOSS 基座逐年加模块。MOSS-003 使用自己的语言模型；AnyGPT 从 LLaMA-2-7B 出发；后来的实时视觉、音频理解和连续潜空间生成又采用不同结构。共同研究问题可以延续，模型权重和架构未必延续。[MOSS 仓库][MR]、[AnyGPT，§3.2][AP]、[MOSS-VL 报告](https://arxiv.org/html/2608.15045v1)

## 1. MOSS 的出发点：会续写，不等于会当助手

自监督语言模型擅长根据前文预测后文，但这个目标没有明确告诉它：当前谁在发言、该怎样执行用户指令、什么时候调用计算器、怎样把工具结果变成回答。MOSS 将这些行为组织成多轮对话，再做监督微调。发布的 MOSS-003 系列包括 base、sft 和 sft-plugin，不能把三者的能力混作基座能力。[MR]

仓库披露，16B 基座在约 700B 中英文及代码“单词”上预训练，SFT 使用约 110 万条多轮对话，插件版再加入约 30 万条工具增强对话。“单词”是作者采用的计数单位，不能直接替换成 700B tokenizer tokens，也不应仅凭规模推算精确训练预算。[MR]

数据来源也影响对模型能力的解释。MOSS-003 的 SFT 对话基于约 10 万条内测用户输入和外部模型生成，目的是让合成数据更接近实际用户意图。它得到的是教师回复、真实需求种子和多轮组织方式共同提供的监督，而不是从这些对话中独立发现全部知识。[仓库数据部分][MR]

### 对话模板和 loss mask 具体教了什么？

发布的 `finetune_moss.py` 将 meta instruction、各轮字段及工具结果串成一条因果序列；meta instruction 和工具返回内容的主体不计算 loss，工具结果周围的格式 token 保留监督。源码并没有把所有用户字段一概遮盖，不能将它简单描述成“只训练 assistant 回复”。超过 2048 token 时按轮停止追加，也不意味着每条原始长对话都被完整训练。[MOSS 微调实现][MC]

简化的目标为

$$
\mathcal L=-\sum_{t:m_t=1}
\log p_\theta(x_t\mid x_{<t}),
$$

其中 $m_t$ 由字段类型和模板决定。工具观察值可以作为上下文影响后续输出，而不必成为模型负责预测的内容。mask 划分的是“模型要学会生成什么”，没有凭空增加工具执行能力。

### 工具调用的边界在哪里？

插件版训练涉及搜索、文生图、计算器和解方程。语言模型生成调用请求，外部程序执行，再把结果放回对话。计算器给出了正确数字，不意味着模型权重已经学会相应算法；搜索查到了事实，也不意味着它原先记住了事实。[插件数据说明][MR]

这说明 MOSS 已把外部能力纳入对话协议，但尚不能据此认定它具备长程自主软件开发能力。后者还需要持续操作环境、处理失败并验证产物，见[工具使用与数字 Agent 专题](06-agent-memory-and-executable-evaluation.md)。

仓库还保留偏好模型与最终偏好训练版本“将开源”的条目。不能把路线描述直接当作这些检查点已公开的证据。代码、数据、模型也分别采用 Apache 2.0、CC BY-NC 4.0 和 AGPL 3.0 等条款；“开放”不是单一许可证。[模型清单与协议][MR]

## 2. AnyGPT 的出发点：模态能否像一种新语言接入？

常见多模态助手通过视觉或音频编码器给语言模型输入连续特征，再输出文字。AnyGPT 想同时解决输入与输出：把每种模态变成离散 token，加入词表，让语言模型继续做 next-token prediction。需要调整 embedding 和输出层大小，但不必改造 Transformer 主干。[论文 §3.1–3.2][AP]

它所统一的是语言模型内部的序列接口。前端仍有模态专属 tokenizer，后端仍需专属恢复模块：

| 模态 | 进入语言模型的表示 | 输出恢复方式 |
|---|---|---|
| 图像 | SEED 的 32 个离散语义 token／图 | 语义嵌入连接 unCLIP 扩散解码器 |
| 语音 | SpeechTokenizer 首层语义 token，50 个／秒 | SoundStorm 补其余声学层，再由 SpeechTokenizer 解码 |
| 音乐 | EnCodec 四层码本展平，200 个／秒 | EnCodec decoder 恢复波形 |

这些数值来自论文表 1 和 §3，并非所有后续 OpenMOSS 模型的公共协议。语音的八层 RVQ 不全部由核心 LLM 自回归预测：它只预测第一层，声线等细节另由 SoundStorm 补全。音乐则使用四层，每层 2048 项，展开后合计 8192 个码本词项。[论文 §3.1–3.3][AP]、[发布组件说明][AR]

### 为什么先做对齐，再做交错指令？

同时配对文字、图像、语音和音乐的数据很少。第一阶段先用文字作桥，将“模态→文字”和“文字→模态”的成对数据混合训练，得到 base。第二阶段再用 AnyInstruct 的多轮交错对话训练 chat，让模型学习在一次任务中组合模态，而不只是完成固定转换。[论文 §4][AP]

对应代码也有实质区别：第一阶段扩充模态词项和 embedding，构造转换模板，按完整序列做预测；第二阶段的 `preprocess` 则遮盖用户指令，只对 assistant 输出保留监督。两个训练脚本分别载入对齐数据和交错指令数据。源码示例能说明训练结构，不能替代发布检查点实际训练日志。[stage1][A1]、[stage2][A2]、[阶段 1 配置][AS1]、[阶段 2 配置][AS2]

AnyInstruct 的构造分两步：先由 GPT-4 写含模态占位描述的主题、场景和多轮对话，再用 DALL-E 3、MusicGen 与 Azure TTS 将描述变成对应媒体。过滤后得到 108K 条交错对话，另外还补充了从文本对话转换的语音对话。[论文 §4.2][AP]

这种方式补足了“模型该何时输出什么模态”的监督，但也限定了数据分布。合成图片先服从文字描述，合成语音先服从文本内容；模型较少面对描述错误、背景噪声或跨模态证据相互矛盾的情况。这是由构造流程得到的分析，不是作者已测得的鲁棒性退化。

## 3. 统一 token，留下了哪些难题？

首先是压缩瓶颈。把一张图像压成 32 个语义 token 可以降低语言模型的序列负担，但精细文字、几何和局部细节可能在编码时丢失。若 tokenizer 将两种输入编码为同一个序列，后端语言模型就无法仅凭这段序列区分它们。生成器能补出合理细节，不等于准确保留了原始证据。

其次，各模态付出的序列成本差异很大。按论文码率，10 秒语音的核心语义序列约 500 个 token；10 秒音乐按相同码率外推约 2000 个 token，但论文音乐数据采用 5 秒片段，不能把这个长度计算当作已验证的长音乐生成能力。对一个因果序列使用相同训练接口，没有消除模态长度、采样策略和恢复成本的差别。[论文表 1、§3.1][AP]

还要区分“都能处理”与“都达到专用模型水平”。作者的 base 评测覆盖各模态与文字之间的转换；完整任意模态交错对话主要通过案例展示。LibriSpeech test-clean 的 ASR WER 为 8.5，表中 Whisper Large V2 为 2.7；图像 caption 的 CIDEr 为 107.5，SEED-LLaMA 为 123.6。不同训练数据和零样本条件限制严格归因，但这些结果已足以说明“统一”不代表每项任务都最优。[论文 §5.1–5.2、表 2、4][AP]

最后，文字作桥不会自动建立物理时间同步。“这段音乐与这张图语义相符”和“声响准确发生在画面动作的那一刻”是不同任务。后者需要显式时序表示、对齐监督或联合生成，见[视听潜表示与生成专题](03-audiovisual-latents-and-joint-denoising.md)。

## 4. 怎样理解后续路线？

AnyGPT 证明了离散接口是一条可行的多模态建模路线。后续工作没有因此只沿一种架构发展：语音生成更关注保真度与流式调度；音频理解使用连续编码器；实时视频关注新帧到达时的缓存和可见性；视听生成关注连续潜空间中的同步。各篇专题应围绕这些约束展开，而不能给项目之间画出没有证据的权重继承链。

CoLLiE 属于支撑这一类工作的训练基础设施：组合分布式训练、参数高效微调和评测等功能。它有独立系统论文，但不是新语言模型，也不能据其存在认定今天所有项目都用同一套训练栈。[CoLLiE 论文](https://arxiv.org/abs/2312.00407)、[固定仓库](https://github.com/OpenMOSS/CoLLiE/tree/3826b3ed90da384d70fbe4afde8f91c7b2847a2b)

## 资料与版本

材料核查于 2026-10-17。MOSS 的正式论文是 Tianxiang Sun 等的 *MOSS: An Open Conversational Large Language Model*，发表于 *Machine Intelligence Research*（2024），DOI `10.1007/s11633-024-1502-8`；AnyGPT 是 Jun Zhan 等的 ACL 2024 Long Paper。模型发布年和论文发表年分别记录。实验数字为作者报告，长度计算与瓶颈讨论为本文分析。

[MP]: https://link.springer.com/article/10.1007/s11633-024-1502-8
[MR]: https://github.com/OpenMOSS/MOSS/blob/24bc88737d83fa5561bf3c284b2895b8ac41bff6/README.md
[MC]: https://github.com/OpenMOSS/MOSS/blob/24bc88737d83fa5561bf3c284b2895b8ac41bff6/finetune_moss.py
[AP]: https://aclanthology.org/2024.acl-long.521.pdf
[AR]: https://github.com/OpenMOSS/AnyGPT/blob/fc3bcc4e9dd76edec8a63300b7ae163a9ecec3d4/README.md
[A1]: https://github.com/OpenMOSS/AnyGPT/blob/fc3bcc4e9dd76edec8a63300b7ae163a9ecec3d4/anygpt/src/train/stage1_pretrain.py
[A2]: https://github.com/OpenMOSS/AnyGPT/blob/fc3bcc4e9dd76edec8a63300b7ae163a9ecec3d4/anygpt/src/train/stage2_sft.py
[AS1]: https://github.com/OpenMOSS/AnyGPT/blob/fc3bcc4e9dd76edec8a63300b7ae163a9ecec3d4/scripts/stage1_pretrain.sh
[AS2]: https://github.com/OpenMOSS/AnyGPT/blob/fc3bcc4e9dd76edec8a63300b7ae163a9ecec3d4/scripts/stage2_sft.sh
