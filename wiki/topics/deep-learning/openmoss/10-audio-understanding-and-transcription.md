# 音频理解与转写：连续特征怎样变成可核对的文字

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

## 1. 背景：转写正确，不等于听懂了音频

一段会议录音里，文字只是部分信息。同一句“好啊”可能是赞同，也可能带着讽刺；远处的提示音、
谁打断了谁、某个人隔了十分钟再次发言，都可能改变理解。音乐中的歌词也不能代替伴奏、和声与段落变化。
MOSS-Audio 的动机是让同一音频前端保留这些线索，再由语言模型按任务输出转写、描述或答案。
MTD 则集中解决会议中的“谁在什么时间说了什么”。[Audio §1–2](https://arxiv.org/pdf/2606.01802v3#page=2)、[MTD §1](https://arxiv.org/pdf/2601.01554v7#page=2)。

这篇专题讨论的模型都以音频为输入、文字为输出。它们与需要还原波形的 CAT／TTS 系统不同：
理解前端不必把每一处声学细节压进可解码的离散码本，可以直接向语言模型传递连续向量。
代价是，这些向量并不因此成为可逆的音频表示。[Audio §2.1](https://arxiv.org/pdf/2606.01802v3#page=4)、[MTD 公开模型源码 L26–42](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/blob/e3bdd93f8ad58418e04659818efd5fd87a0bc486/moss_transcribe_diarize/modeling_moss_transcribe_diarize.py#L26)。

| 系统 | 主要输出 | 应当单独检验的错误 |
|---|---|---|
| MOSS-Audio | 转写、音频描述、时间相关问答、推理答案 | 听觉证据是否支持答案，文字是否正确，时间是否对齐 |
| MOSS-Transcribe-Diarize，简称 MTD | 带说话人和起止时间的转写 | 内容错字、跨段身份混淆、时间边界偏移 |
| MOSS-Music | 歌词与音乐分析文字 | 歌词、和弦或结构是否准确，描述是否编造 |

上述任务范围分别见 [Audio §1](https://arxiv.org/pdf/2606.01802v3#page=3)、[MTD §2](https://arxiv.org/pdf/2601.01554v7#page=3)
和 [Music 固定 README L23–34](https://github.com/OpenMOSS/MOSS-Music/blob/ad107c7ddaa06de168a0dfbc18d3e1e6a40c0e5e/README.md#L23)。

## 2. MOSS-Audio：给文字模型保留多层声学证据

### 连续 encoder 先解决输入长度

论文§2.2的前端从128通道 log-mel 出发，经三层 stride-2 卷积，将时间轴压缩八倍，
再用32层 Transformer 提取连续特征。输出帧率为12.5 Hz，即每秒约12.5个向量，不是12.5个离散声学码。
按帧率计算，十分钟约有7,500个音频位置；时间标记和文字指令还会占用额外上下文。
这是长度推算，不是吞吐实测。[Audio §2.2](https://arxiv.org/pdf/2606.01802v3#page=4)、[固定8B配置](https://huggingface.co/OpenMOSS-Team/MOSS-Audio-8B-Instruct/blob/d4dc5a6d8cd79b43dcd82884c75e303b1ecd016d/config.json)。

最终 encoder 特征经过一个带门控的投影网络，映射到文字模型的 hidden space。
`MossAudioModel.forward` 用 `masked_scatter_` 把它们填进音频占位符，随后文字 decoder 生成答案。
音频没有先被转成转写文本；但模型输出仍是文字，不包含语音或音乐波形解码器。
[固定源码：`forward` L469–520](https://github.com/OpenMOSS/MOSS-Audio/blob/66326e6e0db34f036c86a76ba005efa4830c69dd/src/modeling_moss_audio.py#L469)。

长录音还要求控制 encoder 的注意力范围。论文称窗口限制为100个输出帧、约8秒，将长程推理交给语言模型。
不过，所查实现按音频块批量编码；`_encode_chunk_batch` 构造的是 padding mask，没有在这里建立逐帧因果 mask。
因此，“局部注意力”和“支持缓存”的设计叙述，不足以证明公开路径已实现持续接收语音的在线理解。
复现时应分别核对论文窗口、实际分块参数和推理调用，而不是由 encoder 名字推断实时性。
[Audio §2.2](https://arxiv.org/pdf/2606.01802v3#page=4)、[`MossAudioEncoder.forward` L206–254](https://github.com/OpenMOSS/MOSS-Audio/blob/66326e6e0db34f036c86a76ba005efa4830c69dd/src/modeling_moss_audio.py#L206)、[`_encode_chunk_batch` L135–150](https://github.com/OpenMOSS/MOSS-Audio/blob/66326e6e0db34f036c86a76ba005efa4830c69dd/src/modeling_moss_audio.py#L135)。

### DeepStack 不是再跑一套音频模型

只取 encoder 最后一层，意味着所有任务都依赖同一个高层表示。作者担心它偏向词义，
丢掉情绪、瞬态声响和局部音色。因此除了最终特征，DeepStack 还把中间层特征投影后送进文字 decoder 的早期层。
所查8B配置选择 encoder 索引8、16、24，并注入前三个 decoder 层；这里是代码索引，不混写成从1起数的层号。
[Audio §2.3](https://arxiv.org/pdf/2606.01802v3#page=5)、[固定配置](https://huggingface.co/OpenMOSS-Team/MOSS-Audio-8B-Instruct/blob/d4dc5a6d8cd79b43dcd82884c75e303b1ecd016d/config.json)。

源码核准了注入方式：`_apply_deepstack_to_hidden_states` 只在音频槽位做加法，
`_register_llm_deepstack_hooks` 将对应特征加到早期层输出。可用下式描述该实现：

$$
\widetilde h_j[m_t]=h_j[m_t]+A_j(z_{\ell_j,t}),
\qquad m_t\text{ 为第 }t\text{ 个音频槽位。}
$$

这是源码的数学换记，不是论文给出的因果解释。文字槽位和插入的时间数字不在该音频 mask 内；
也没有把三路中间特征展开成三倍长度的输入序列。
[固定源码：两个注入函数 L386–435](https://github.com/OpenMOSS/MOSS-Audio/blob/66326e6e0db34f036c86a76ba005efa4830c69dd/src/modeling_moss_audio.py#L386)。

我的理解是，这种设计给 decoder 多次接触声学证据的机会，而不是要求主 adapter 一次完成所有压缩。
但最终 benchmark 的提升不能全部归给 DeepStack：训练数据、encoder 和后训练同时改变了。
若要确认它主要保留情绪或瞬态信息，需要同预算对照最终层单路输入，并按任务拆分收益。
论文§2.3给出动机和结构，评测§6没有提供足以隔离这些因素的同预算消融。[Audio §2.3、§6](https://arxiv.org/pdf/2606.01802v3#page=5)。

### 时间标记提供参照，不直接预测边界

论文在每25个音频向量后插入经过秒数“2”“4”“6”等数字。时间数字使用文字 token，
不是把某个音频向量替换成时间，也不是每个词已有正确时间标签。
处理器的 `_build_audio_tokens_with_time_markers` 明确按25个位置分段插数字。
[Audio §2.4](https://arxiv.org/pdf/2606.01802v3#page=5)、[固定处理器 L225–256](https://github.com/OpenMOSS/MOSS-Audio/blob/66326e6e0db34f036c86a76ba005efa4830c69dd/src/processing_moss_audio.py#L225)。

两秒是输入锚点的间隔，不能当成预测精度下界；同样，80 ms 的特征间隔也不保证80 ms的边界误差。
模型仍需根据块内声学变化和 timestamp 监督生成时间。一个复现细节是：
所查 `from_pretrained` 默认 `enable_time_marker=False`，官方 `infer.py` 显式传入 `True`。
只检查类构造函数的默认值，会漏掉这个差别。
[固定处理器 L140–151](https://github.com/OpenMOSS/MOSS-Audio/blob/66326e6e0db34f036c86a76ba005efa4830c69dd/src/processing_moss_audio.py#L140)、[官方示例 L30–34](https://github.com/OpenMOSS/MOSS-Audio/blob/66326e6e0db34f036c86a76ba005efa4830c69dd/infer.py#L30)。

作者在 AISHELL-1／LibriSpeech 上用 AAS 测时间偏移，即匹配时间槽位的平均绝对误差：

$$
\mathrm{AAS}=\frac1N\sum_{i=1}^{N}|\widehat t_i-t_i|.
$$

§6.4／表4自报8B Instruct 的 AAS 为35.77／131.61 ms。参考边界由 CTC forced alignment 生成，
不是人工逐词绝对真值；结果支持“在这一对齐协议上误差更小”，不能外推到复杂会议的所有说话人或事件边界。
误识别词如何匹配、缺失时间槽如何计入，也应随评测实现核对。[Audio §6.4／表4](https://arxiv.org/pdf/2606.01802v3#page=14)。

## 3. 训练与后训练：Instruct 和 Thinking 的分工

### 从零训练 encoder，仍依赖外部标注

Audio 数据先按声事件边界切分，尽量保留完整发言或声音事件，再按内容送入语音、音乐及一般声音分支。
ASR 分支比较多套转写结果，用一致性筛选，再做 forced alignment；其他分支补说话方式、事件和音乐描述。
最后将各分支证据合并成自然语言训练目标。“encoder 从零训练”说的是模型参数初始化，
不意味着标签由原始音频自行产生，也不意味着没有其他模型参与。[Audio §3.1–3.6](https://arxiv.org/pdf/2606.01802v3#page=6)。

我更关心这一步的误差如何传播。多套 ASR 一致能排除部分错误，但若它们共同听错，也会得到高置信标签；
把分支结果写成流畅 caption 后，来源之间的分歧还可能被隐藏。这是标注机制的风险分析，
不是声称作者训练集已被证明存在某个错误率。[Audio §3.2、§3.6](https://arxiv.org/pdf/2606.01802v3#page=6)。

预训练先稳定音频前缀接口，训练重点是主 adapter 和 DeepStack；第二阶段全模型联合更新。
作者报告总量约1.2T training tokens，第二阶段默认 ASR相关／caption／纯文本比例为30%／40%／30%，
组内按数据量平方根采样。纯文本用于保留语言能力，第一阶段默认不混入。
§4使用“主体保持相对稳定”的表述，未据此补造逐参数冻结清单。[Audio §4](https://arxiv.org/pdf/2606.01802v3#page=9)。

### Instruct 先学会按要求交付

任务 SFT 把预训练能力转为用户指令接口：按要求转写、描述、回答问题或给时间戳，
并学习对应输出格式。问答由各类 caption 构造，另混入身份说明等样本；这一阶段产生 Instruct。
它适合需要直接结果的任务，不能因输出较短就认为它没有在使用上下文。
[Audio §5.1](https://arxiv.org/pdf/2606.01802v3#page=9)。

Thinking 在此基础上加入音频与纯文字 reasoning cold start，再做 DAPO 强化学习。
文字推理样本帮助迁移分析方式，音频样本要求把答案与听觉线索联系起来。
所以两者区别主要在后训练目标，而不是 Thinking 换了一种可还原波形的 encoder。
[Audio §5.2–5.3](https://arxiv.org/pdf/2606.01802v3#page=10)。

### 强化学习能优化答案，仍需检验听觉依据

DAPO 为同一 prompt 采样16个回答，按任务正确性、质量和格式等奖励更新策略。
同组奖励方差接近零时，组内比较几乎没有学习信号，作者将其过滤并补采样。
图4显示补采样次数随训练增长，说明优化成本还包括被筛掉的回答，不能只数最后用于更新的样本。
[Audio §5.3／图4](https://arxiv.org/pdf/2606.01802v3#page=10)。

奖励提高并不单独证明模型更依赖音频。对同一道题替换音频、遮掉有关片段，或让文字先验与音频冲突，
才能检查推理是否真的随声学证据改变。这是建议的验证方式；报告的奖励／长度曲线没有完成该因果检验。
我也不会把显示出来的推理文字直接当成内部感知过程的忠实记录。[Audio §5.3／图5](https://arxiv.org/pdf/2606.01802v3#page=11)。

作者表1中8B Thinking 在四项音频理解任务的平均分为71.08，高于配对 Instruct 的66.32，
但低于该表 Gemini-3.1-Pro 的79.89。表3的 Instruct 汇总 CER 为11.30；
多说话人、远近场等子项并非最优。结果支持按任务选择版本，不支持“Thinking 全面更强”。
[Audio §6.1／表1、§6.3／表3](https://arxiv.org/pdf/2606.01802v3#page=14)。

Speech captioning 则用作者自建2,000条音频及人工描述，再让文字 judge 比较输出与参考。
这里 judge 并非直接听音频；分数更高表示描述更符合该参考协议，
不能把“人格”等文字属性评分当成已客观测量的人的属性。[Audio §6.2／表2](https://arxiv.org/pdf/2606.01802v3#page=13)。

## 4. MTD：把内容、说话人和时间放进同一输出序列

### 联合输出解决什么问题

独立 ASR 和 diarization 的结果需要对齐：一句话跨过两个声纹段，或两人同时说话时，
系统必须决定文字归谁。MTD 直接生成 `[开始时间][Sxx]文字[结束时间]`，让这些决策共享上下文。
它的标签首先是录音内的说话人身份，不应自动解释为真实姓名或跨录音永久声纹 ID。
[MTD §1–2](https://arxiv.org/pdf/2601.01554v7#page=2)、[固定输出格式 L60–69](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/blob/e3bdd93f8ad58418e04659818efd5fd87a0bc486/README.md#L60)。

下面只是格式示意，不是作者测试样本；第二段起点早于第一段终点，可以表达重叠：

```text
[0.48][S01]我先说明一下。[2.10][1.80][S02]等一下，这里有个问题。[3.60]
```

联合序列仍是自回归文字生成。“单次转写”指同一全局上下文下生成一个结果，
不是一次 GPU forward 就输出整个会议，也不保证所有字段始终相互一致。
因此还需要检查起止时间是否合法、同一标签是否漂移、漏掉的重叠发言在哪里。
[公开 `forward` 及生成接口 L291–359](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/blob/e3bdd93f8ad58418e04659818efd5fd87a0bc486/moss_transcribe_diarize/modeling_moss_transcribe_diarize.py#L291)。

### 块 encoder 与全局 decoder 并不矛盾

公开0.9B模型用 Whisper-Medium 风格 encoder；四倍时间合并后，经 MLP 投影送入 Qwen3-0.6B 风格 decoder。
`VQAdaptor` 虽带“VQ”名字，实现只有线性层、SiLU 和 LayerNorm，没有码本查找或 RVQ。
这里仍是连续音频特征注入，不是把 CAT 离散索引送去转写。
[固定模型源码 L26–42、L85–145](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/blob/e3bdd93f8ad58418e04659818efd5fd87a0bc486/moss_transcribe_diarize/modeling_moss_transcribe_diarize.py#L26)、[固定模型配置](https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize/blob/704aa4a9c304e8520be88901e0d1960158ef5b15/config.json)。

处理器把16 kHz录音按30秒切成前端块。`get_audio_features` 根据 `audio_chunk_mapping`
将同一录音的块特征按顺序拼回，再合并、投影，填入统一文字序列。
所以论文“最长90分钟不分块”应读成不拼接多个独立短段转写，而不是 encoder 从不切音频。
全局 decoder 可以让隔得很远的发言共同参与身份判断；已经在局部编码中丢失的细节，则不能靠全局文字模型保证恢复。
[固定处理器 `_chunk_audio` L56–69](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/blob/e3bdd93f8ad58418e04659818efd5fd87a0bc486/moss_transcribe_diarize/processing_moss_transcribe_diarize.py#L56)、[`get_audio_features` L119–145](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/blob/e3bdd93f8ad58418e04659818efd5fd87a0bc486/moss_transcribe_diarize/modeling_moss_transcribe_diarize.py#L119)、[固定前端配置](https://huggingface.co/OpenMOSS-Team/MOSS-Transcribe-Diarize/blob/704aa4a9c304e8520be88901e0d1960158ef5b15/preprocessor_config.json)。

128k是上下文预算，不是自动完成任意90分钟录音的保证。按12.5 Hz推算，90分钟音频约占67,500个位置，
还需容纳数字时间锚、提示和输出文字；输出 token 上限过小也会截断结果。
公开 README 明确要求长录音提高 `max_new_tokens`。这些是长度约束，不是模型准确率结论。
[MTD §1](https://arxiv.org/pdf/2601.01554v7#page=3)、[固定 README L299–316](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/blob/e3bdd93f8ad58418e04659818efd5fd87a0bc486/README.md#L299)。

### 数据能教重叠，但论文没有披露完整训练配方

§3的模拟数据抽取2–12名说话人，控制轮换和间隔，允许重叠达到较短片段的80%，再加噪声及混响。
这给联合模型提供可控的多人监督；真实节目与会议则补充自然录音差异。
报告未完整披露公开0.9B每阶段训练量、步数和初始化细节，不能由这套总体数据叙述推定训练已完全可复现。
[MTD §3](https://arxiv.org/pdf/2601.01554v7#page=4)。

### CER、cpCER 与时间精度必须分开读

CER去掉身份信息后比较全文；cpCER先将每个说话人的文字拼接，再寻找预测标签到参考标签的最佳置换。
用 $R_i,H_j$ 表示逐说话人拼接文字，必要时补空说话人，可将其定义写为：

$$
\mathrm{cpCER}=\frac{\min_\pi\sum_i d_{\rm edit}(R_i,H_{\pi(i)})}{\sum_i|R_i|}.
$$

这是指标定义的数学换记。置换让 `[S01]` 和 `[S02]` 对调命名不受惩罚，却会惩罚把两个人的话混进同一流。
它仍受到识别错误影响，而且没有把时间边界纳入距离。[MTD §4.1.2](https://arxiv.org/pdf/2601.01554v7#page=5)。

| 指标 | 测什么 | 不直接测什么 |
|---|---|---|
| CER | 全文字符编辑错误 | 身份归属、时间戳 |
| cpCER | 最佳标签置换后的逐人文字错误 | 毫秒边界误差、无文字声音的归属 |
| Δcp＝cpCER－CER | 两种文字评分的差值 | 可独立相加的“纯说话人错误” |
| AAS／时间边界误差 | 与参考时间的偏移 | 内容或身份一定正确 |

前三项定义来自 [MTD §4.1.2](https://arxiv.org/pdf/2601.01554v7#page=5)；AAS见 [Audio §6.4](https://arxiv.org/pdf/2606.01802v3#page=14)。
表中“不直接测什么”是由定义得到的分析，不声称 MTD 已报告 AAS。

论文将 Δcp 解释为说话人归属带来的额外退化，但表2 Alimeeting 的 CER＝24.86%、cpCER＝22.17%，
Δcp＝−2.69。这个作者自报反例说明差值不是普适非负分解：按人重排会改变字符比较顺序。
一个简化例子是参考全文“甲乙”、预测顺序“乙甲”，但各人文字均正确；全文编辑距离非零，逐人距离可以为零。
[MTD 表2](https://arxiv.org/pdf/2601.01554v7#page=5)。

也可以保持文字及标签不变，把所有时间整体平移一秒：CER、cpCER均不变，检索和字幕却会出错。
因此，AISHELL-4自报14.84%／15.83%说明该协议下内容和归属表现，不能单独证明时间精准。
论文结尾仍把更细的 timestamp 评测及 streaming SATS 列为后续工作。
低离线 RTF 也只说明整段处理速度，不能当成边听边出的延迟。[MTD 表2、§5](https://arxiv.org/pdf/2601.01554v7#page=5)、[固定服务计时表](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/blob/e3bdd93f8ad58418e04659818efd5fd87a0bc486/README.md#L331)。

## 5. MOSS-Music：音乐理解的难点在标签怎样获得

### 模型输出文字，训练管线也在生产文字标签

Music 沿用 Audio 的连续 encoder、DeepStack 和时间标记，再做音乐持续预训练、指令微调，
Thinking 另有 reasoning tuning。它接收歌曲并输出歌词、描述或分析文字；
这些功能不构成 text-to-music 生成，也没有证据表明该路径输出新音乐波形。
[Music 固定 README L85–135](https://github.com/OpenMOSS/MOSS-Music/blob/ad107c7ddaa06de168a0dfbc18d3e1e6a40c0e5e/README.md#L85)。

官方链接的数据管线将原曲送入几条支路：音频语言模型写整体描述，MIR工具估计节拍、调性和和弦，
结构模型给段落边界；随后按段切音频，做歌词识别和局部调性分析，再合并为 caption 和问答。
这里列出工具角色比堆名字更有用：结构边界决定在哪切，歌词填充演唱内容，MIR补充可定位的音乐属性。
[作者数据管线固定执行图](https://github.com/wx9songs/MOSS-Music-Data-Pipeline/blob/58ee296c4be830514773fb93b9b5a1f503c11cd2/README.md#L64)。

### 标签写得流畅，不代表所有分析都正确

`caption_generate.py` 的 prompt 要求综合结构化 metadata，并在来源矛盾时优先信任已有整体描述；
缺失歌词不被当成纯器乐的证据。后者能避免一个常见误判，前者也可能覆盖更可靠的局部工具结果。
源码还允许从文件路径识别曲名和艺人，再写入 caption。
[固定脚本 `PROMPT_TEMPLATE` L38–74](https://github.com/wx9songs/MOSS-Music-Data-Pipeline/blob/58ee296c4be830514773fb93b9b5a1f503c11cd2/scripts/caption_generate.py#L38)。

我的分析是，监督中同时存在声学证据与音乐常识线索。若问答由这类 caption 构造，
模型可能在确实听到结构变化之前，就靠曲目身份和常见编曲模式答对。
验证方式应包括去掉路径身份信息、未见曲目测试，以及移动副歌位置后检查答案时间是否随音频改变。
这不是断言训练集已发生泄漏，而是管线给出的具体待检验风险。

公开脚本可帮助复核标注过程，但跑通它还要原始曲目、结构模型权重和外部推理服务。
数据管线开放不等于全量训练数据开放，也不能代替专属预训练配方。
[管线固定 README L132–146](https://github.com/wx9songs/MOSS-Music-Data-Pipeline/blob/58ee296c4be830514773fb93b9b5a1f503c11cd2/README.md#L132)。

### 实验口径与独立论文边界

作者 README 自报 Instruct 音乐QA平均80.38、Thinking 74.26，但平均只取八项，
排除了三项 NSynth 孤立音符识别。歌词15.88%则是 MUSDB18 的WER29.19%、
MIR-1K的CER15.84%、Opencpop的CER2.60%的无权平均，不能叫一个统一测试集的WER。
这也再次说明 Thinking 不是所有任务都占优。[固定QA表及平均定义](https://github.com/OpenMOSS/MOSS-Music/blob/ad107c7ddaa06de168a0dfbc18d3e1e6a40c0e5e/README.md#L190)、[固定歌词表](https://github.com/OpenMOSS/MOSS-Music/blob/ad107c7ddaa06de168a0dfbc18d3e1e6a40c0e5e/README.md#L261)。

Caption 的领先来自初步文字模型 judge；时间戳歌词及和弦的详细 benchmark 仍写待发布。
本次核查的固定 README 仍有 arXiv Coming Soon，BibTeX 的 `howpublished` 指向仓库、
`note` 为 GitHub repository。没有核验到 Music 独立全文，就不能把 Audio 的1.2T规模或DAPO配置照搬给它；
`2606.01802` 是骨干论文，不是 Music 专属训练报告。这里记录“未核验”，不声称证明论文不存在。
[固定评测说明 L170–183](https://github.com/OpenMOSS/MOSS-Music/blob/ad107c7ddaa06de168a0dfbc18d3e1e6a40c0e5e/README.md#L170)、[固定引用声明 L400–409](https://github.com/OpenMOSS/MOSS-Music/blob/ad107c7ddaa06de168a0dfbc18d3e1e6a40c0e5e/README.md#L400)。

## 6. 读这些结果时，哪些结论可以留下

连续特征、多层注入与时间数字提供了具体的感知接口；答案是否真正依赖音频，
仍需通过替换、遮挡和时间移动实验验证。Audio 的问答、caption 和时间对齐成绩，应分别解释。
MTD 的联合输出减少模块间协调步骤，但内容、身份和时间仍是三个不同错误来源。
Music 的数据工程能提供细分音乐监督；工具标签、常识和实际声学贡献需要分开验证。

MTD 的公开0.9B与在线 Pro 在 README 中分列，不能把 Pro 分数归给开源检查点；
Podcast／Movies 的数据发布状态未独立确认，论文“将公开”不改写为“已取得”。
[固定版本说明与评分行](https://github.com/OpenMOSS/MOSS-Transcribe-Diarize/blob/e3bdd93f8ad58418e04659818efd5fd87a0bc486/README.md#L154)、[MTD §4.1.1](https://arxiv.org/pdf/2601.01554v7#page=4)。

## 资料与版本

材料核查于 2026-10-17。实验数字为作者报告，机制解释、反例和长度计算为本文分析；未运行模型或审计全量数据。

| 工作 | 作者／年份 | 采用资料 |
|---|---|---|
| MOSS-Audio Technical Report | Chen Yang 等／2026 | [2606.01802v3](https://arxiv.org/abs/2606.01802v3) |
| MOSS Transcribe Diarize Technical Report | MOSI.AI团队，Donghua Yu等／2026 | [2601.01554v7](https://arxiv.org/abs/2601.01554v7) |
| MOSS-Music | OpenMOSS Team／2026 | 官方仓库和数据管线，未核验独立论文 |

GitHub固定提交：Audio `66326e6e0db3`；
MTD `e3bdd93f8ad5`；Music `ad107c7ddaa0`；
作者音乐管线 `58ee296c4be8`。正文均直接链接对应文件及已核准行号。
Hugging Face配置分别固定于 Audio `d4dc5a6d8cd7`、
MTD `704aa4a9c304`；配置核验不等于下载、运行了该权重。
