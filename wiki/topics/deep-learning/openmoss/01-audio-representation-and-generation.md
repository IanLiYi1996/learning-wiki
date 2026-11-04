# 语音模型怎样保留内容、声线和说话人

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

本篇讨论语音表示、生成和直接语音交互。听觉问答、音乐分析及带说话人的转写，见[音频理解与转写专题](10-audio-understanding-and-transcription.md)。

同一句“好”，可以是赞同、犹豫，也可以是反讽。把语音转成文字后再交给 LLM，容易复用文字知识，却可能丢掉这些声学信息；让模型直接处理声音，又会增加序列长度和生成成本。[MOSS-Speech §1–2](https://proceedings.iclr.cc/paper_files/paper/2026/file/20cf299b663a37b5b936de2cb5713cf5-Paper-Conference.pdf)

问题首先落在音频表示上。编解码器（codec）把波形压缩成较短的表示，再从中还原声音。压得越短，语言模型的负担通常越小，但下游也越难追回被丢掉的信息。RVQ 用多层码逐步补充残差，试图在压缩率和声学细节之间取得平衡。[SpeechTokenizer §1、§3](https://arxiv.org/pdf/2308.16692v2)

OpenMOSS 的这些工作分别处理这条链的不同环节：SpeechTokenizer 和 CAT 学习表示；MOSS-TTS 调整音频码的生成顺序；MOSS-Speech 将文字模型适配为直接语音回答；TTSD 在给定剧本中保持多个角色的声线。理解它们，需要区分“听懂后回答”和“朗读剧本”，再看各自如何保留信息、控制成本。[MOSS-TTS §1](https://arxiv.org/pdf/2603.18090v2)、[CAT §1–3](https://arxiv.org/pdf/2602.10934v2)、[TTSD §1–2](https://arxiv.org/pdf/2603.19739v1)

## 1. 音频压缩后，还剩下什么？

### 语义表示是否足够？

“先提语义，再补声学”隐藏着一个强假设。令 $C$ 为上游条件，$S$ 为语义表示，$V$ 为声线参考，$X$ 为输出波形。若生成器只能经过 $S,V$ 接收条件，则其建模近似为：

$$
p(X\mid C,V)\approx\sum_Sp(S\mid C,V)p(X\mid S,V),
\qquad X\perp C\mid(S,V).
\tag{推导1}
$$

这是接口施加的条件独立假设，不是“语义 token 天然充分”的定理。若语气、强调或犹豫未进入 $S,V$，后级只能猜测，不能恢复原条件中的选择。SpeechTokenizer 的真实 USLM 更谨慎：§3.4 的残差模型仍接收音素 $u$ 和参考码 $\widehat Q$，因此不能把它写成 $Q_{2:K}\perp u\mid Q_1$。其论文机制等价于：

$$
p(Q\mid u,\widehat Q)=p_{\rm AR}(Q_1\mid u)
\prod_{k=2}^{8}p_{\rm NAR}(Q_k\mid Q_{<k},u,\widehat Q).
\tag{论文机制换记}
$$

第一层是内容优先接口，而非纯语义充分统计量；后级存在文本旁路。[SpeechTokenizer §3.2–3.4，PDF pp.4–6](https://arxiv.org/pdf/2308.16692v2#page=4)。

RVQ 的“残差”首先是潜空间运算。令 $z=E(X)$，$e_k$ 为映射回公共潜空间的第 $k$ 层码向量：

$$
r_0=z,\quad q_k=\arg\min_i d_k(r_{k-1},i),\quad
r_k=r_{k-1}-e_k(q_k),\quad \widehat z_K=\sum_{k=1}^{K}e_k(q_k).
\tag{实现的数学换记}
$$

距离 $d_k$ 可以在投影、归一化后的空间计算；这不保证波形失真随每次残差扣除严格下降，更不保证后层只含音色。CAT 的 `MossAudioTokenizerResidualLFQ.forward` 明确逐层累加量化向量、扣除残差；其归一化最近邻见 `MossAudioTokenizerLFQ.decode_latents`。[固定源码：L1076–1092、L1238–1274](https://github.com/OpenMOSS/MOSS-Audio-Tokenizer/blob/8c50ac4c5d7287d2ed6ea20a08c90ca439887d23/modeling_moss_audio_tokenizer.py#L1238)。

### SpeechTokenizer、CAT 与连续特征的区别

SpeechTokenizer 用 HuBERT 连续特征约束第一 RVQ 层，同时用重建／GAN 训练完整 codec；推理时 teacher 消失，AR 预测第一层，NAR 补残差，decoder 合成。CAT 则直接从波形联合优化 encoder、量化器、decoder 与训练期文字头，不预指定“哪一层必须是纯语义”。其 §3.2 式(1)、(5)为：

$$
\mathcal L_{\rm sem}=-\sum_i\log p(y_i\mid\mathcal T,\widehat z,y_{<i}),\quad
\mathcal L_G=\lambda_{\rm sem}\mathcal L_{\rm sem}
+\lambda_{\rm rec}\mathcal L_{\rm rec}
+\lambda_{\rm cmt}\mathcal L_{\rm cmt}
+\lambda_{\rm code}\mathcal L_{\rm code}
+\lambda_{\rm adv}\mathcal L_{\rm adv}
+\lambda_{\rm feat}\mathcal L_{\rm feat}.
\tag{论文}
$$

ASR、多人 ASR 和 caption 的梯度监督的是量化后的向量序列，不是对整数 ID 直接求导。对 encoder 参数 $\phi$，梯度可写为 $\nabla_\phi\mathcal L_{\rm sem}=J_E^\top\widetilde J_Q^\top\nabla_{\widehat z}\mathcal L_{\rm sem}$，其中 $\widetilde J_Q$ 是量化的反向代理。若采用 $\widehat z_{\rm ST}=z+\operatorname{sg}(\widehat z-z)$，则该代理近似恒等：这是条件推导；SpeechTokenizer 附录D明确采用 straight-through，但不据此断言 CAT 训练代码完全相同。所查 CAT 发布量化 `forward` 有 `@torch.no_grad()`，只能核准推理残差，不能复现完整训练梯度。[SpeechTokenizer 附录D](https://arxiv.org/pdf/2308.16692v2#page=16)、[CAT §3.2／附录A](https://arxiv.org/pdf/2602.10934v2#page=5)、[CAT 推理函数 L1238](https://github.com/OpenMOSS/MOSS-Audio-Tokenizer/blob/8c50ac4c5d7287d2ed6ea20a08c90ca439887d23/modeling_moss_audio_tokenizer.py#L1238)。

率失真取舍可用工程目标 $\min\mathbb E[d(X,D(Q))]+\beta R+\gamma\mathcal L_{\rm sem}$ 理解，但这不是论文给出的 Shannon 最优界。固定长索引的名义码率为 $R=f\sum_k\log_2V_k$：CAT 的 $f=12.5,V_k=1024$ 给出 $R=125K$ bps。增加深度买到的是表示容量，未必同比增加任务相关信息；音色、背景和词义会竞争该容量。[CAT §3.1、§5.2／图5、附录A.1](https://arxiv.org/pdf/2602.10934v2#page=11)。

MOSS-Speech 另走单码本、encoder 只用 ASR 目标的路线，声学由条件 flow decoder 补全；连续音频理解接口又是另一端：`MossAudioModel.forward` 把连续特征经 adapter 填入文字骨干，并注入 DeepStack，最终输出文字。它绕开离散量化误差，但没有因此获得可逆波形接口，也不能直接使用上述 RVQ 码率。[MOSS-Speech §2.2](https://proceedings.iclr.cc/paper_files/paper/2026/file/20cf299b663a37b5b936de2cb5713cf5-Paper-Conference.pdf#page=4)、[连续接口：`forward` L469–520](https://github.com/OpenMOSS/MOSS-Audio/blob/66326e6e0db34f036c86a76ba005efa4830c69dd/src/modeling_moss_audio.py#L469)。

### 实验支持到哪一步？

SpeechTokenizer 表3／§5.1比较 teacher，附录B表6比较 LSTM/BiLSTM；它们支持“语义目标和可见上下文影响接口质量”，不证明解耦独立。CAT 图4显示全联合训练优于冻结 encoder／量化器后只优化 decoder，但不是去掉辅助 ASR 的单变量实验；附录E表4的 CAT-ASR 还经过约200万小时配对训练，不能归因于 tokenizer 单独的语义充分性。[SpeechTokenizer 表3、表6](https://arxiv.org/pdf/2308.16692v2#page=8)、[CAT §5.1／图4、附录E](https://arxiv.org/pdf/2602.10934v2#page=10)。

这些结果说明表示需要适配下游任务。第一层是否已经保留了生成所需的内容，仍要看去掉残差模型的文本旁路后是否损伤韵律；现有消融尚未证明这一点。

## 2. Delay 与 Global-local 怎样生成多层音频码？

### 两种生成顺序

令 $q[t,k]$ 表示物理帧 $t$、RVQ 层 $k$，$C$ 包含文本和参考，$b_t$ 为 text/pad 控制通道，$H_t^{GL}=(Q_{<t,:},B_{<t})$。Global-local 在每帧内部按深度展开：

$$
p_{\rm GL}(Q,B\mid C)=\prod_{t=1}^{T}
\left[p(b_t\mid C,H_t^{GL})\prod_{k=1}^{K}
p(q[t,k]\mid C,H_t^{GL},b_t,q[t,<k])\right].
\tag{论文§4.2式15换记}
$$

实际 local 还先预测 text/pad 控制通道，因此每帧循环为 $K+1$ 步。Delay 则设调度步 $s=t+k-1$，$\widetilde q[s,k]=q[s-k+1,k]$，仅对 $1\le s-k+1\le T$ 的位置计损失。忽略特殊控制标记，公开多头实现对应：

$$
p_{\rm D}(Q\mid C)=
\prod_{s=1}^{T+K-1}\prod_{k: \,\mathrm{valid}}
p(\widetilde q[s,k]\mid C,H_s),\quad
H_s=\{q[u,j]:u+j-1<s\}.
\tag{源码因子分解推导}
$$

同一步音频头在给定历史／骨干状态后分别预测，采样结果不在该步互相回馈。这是不同调度步的条件分解，不能换写成完整的 $Q_{<t,:}$ 历史。[MOSS-TTS §4.1式10–12、§4.2式14–15](https://arxiv.org/pdf/2603.18090v2#page=8)、[`MossTTSDelayModel.forward` L279–301](https://github.com/OpenMOSS/MOSS-TTS/blob/934d6826b084c46a0d033402174d5f8ac4ed2519/moss_tts_delay/modeling_moss_tts.py#L279)。

以下是推导示例，$T=3,K=3$，不是性能实验：

| 调度步 $s$ | head 1 | head 2 | head 3 | 此步后完整可解码帧 |
|---|---|---|---|---|
| 1 | $q[1,1]$ | pad | pad | 无 |
| 2 | $q[2,1]$ | $q[1,2]$ | pad | 无 |
| 3 | $q[3,1]$ | $q[2,2]$ | $q[1,3]$ | 帧1 |
| 4 | pad | $q[3,2]$ | $q[2,3]$ | 帧2 |
| 5 | pad | pad | $q[3,3]$ | 帧3 |

处理器 `apply_delay_pattern` 将零起始第 $i$ 列放到行 $i:i+T$，`apply_de_delay_pattern` 反向取出，直接核准此错位索引。一个容易漏掉的结果是：$q[1,3]$ 能看到已生成的 $q[2,1]$，却看不到同一步 $q[2,2]$。这是生成顺序中的“较晚帧粗码”，不是读取未来真实录音；相应地，较早物理帧的部分深层码也可能尚未进入历史。[固定源码：两函数 L536–557](https://github.com/OpenMOSS/MOSS-TTS/blob/934d6826b084c46a0d033402174d5f8ac4ed2519/moss_tts_delay/processing_moss_tts.py#L536)。

### 首音和持续生成的成本

训练时两者均 teacher-force：Delay 做错位、多头掩码交叉熵；Local 将帧内真值前缀加在 global latent 后，用因果 local 一次批量计算。推理时 Delay 每个骨干步投影所有头；Local 先取 global 状态，再逐层采样并回馈 embedding。故“深度自回归”不等于训练也必须串行跑 $K$ 次。[Local `forward` L814–846、`CustomMixin._sample` L390–423](https://github.com/OpenMOSS/MOSS-TTS/blob/934d6826b084c46a0d033402174d5f8ac4ed2519/moss_tts_local/modeling_moss_tts.py#L814)。

以下为成本推导，不是实测：令 $P_D,P_G$ 为 prefill 到第一个预测状态的时间，$g_D,g_G$ 为缓存骨干一步成本，$h$ 为一次全部 Delay heads 的成本，$\ell(j)$ 为第 $j$ 个 local 步成本，$d_c$ 为 codec／缓冲成本。省略开始结束标记、取一次解码一帧时：

$$
\begin{aligned}
\mathrm{TTFA}_D&\approx P_D+(K-1)g_D+Kh+d_c,\\
\mathrm{TTFA}_{GL}&\approx P_G+\sum_{j=1}^{K+1}\ell(j)+d_c,\\
\mathrm{steady}_D&\approx g_D+h,\qquad
\mathrm{steady}_{GL}\approx g_G+\sum_{j=1}^{K+1}\ell(j).
\end{aligned}
$$

Delay 共需 $T+K-1$ 个调度输出，Local 约 $T$ 个 global 输出。文本 prefill 不因 RVQ 深度而展开；但处理器中长度 $L$ 的参考音频块变为 $L+K-1$ 步，Local 仍为 $L$ 步。短请求尤其受 prefill 和填管影响。$K-1$ 是计算步数，不应乘80 ms便宣称真实 TTFA：模型生成速度与播放时钟不同，codec 分块和设备缓冲还会增加成本。[Delay `_replace_audio_placeholders` L473–481、`_get_unified_codes` L627–636](https://github.com/OpenMOSS/MOSS-TTS/blob/934d6826b084c46a0d033402174d5f8ac4ed2519/moss_tts_delay/processing_moss_tts.py#L473)。

还有实现混杂：所查 Local `MossTTSLocalTransformer.forward` 强制 `use_cache=False`，`_sample` 每次将增长的帧内前缀重算，故不能简单把 $\ell(j)$ 当常数。普通注意力下，该实现局部 FFN 重算量随 $K$ 为二次、attention 为三次量级；这是操作数分析，不是实测延迟，也不是 Global-local 架构不可优化的下界。[固定源码：L187–206、L393–406](https://github.com/OpenMOSS/MOSS-TTS/blob/934d6826b084c46a0d033402174d5f8ac4ed2519/moss_tts_local/modeling_moss_tts.py#L187)。

### 质量比较中的容量差异

论文表3的 continuation 英文 SIM 为 Delay 70.86、Local 73.28，但骨干规模不同，不是同容量拓扑消融。CAT §4.3图3比较 Progressive Sequence Dropout 的概率，支持可变深度训练，不证明 Local 必然更快或更优。[MOSS-TTS §6.2／表3](https://arxiv.org/pdf/2603.18090v2#page=19)、[CAT §4.3／图3](https://arxiv.org/pdf/2602.10934v2#page=8)。

Delay 用错位调度换取多头并行；Local 保留完整的过去帧和帧内依赖，但需要逐层生成。比较速度时，还应分开首音、持续吞吐和 Local 实现中的前缀重算成本。

## 3. MOSS-Speech 怎样直接生成语音回答？

### 共享骨干与末端分叉

MOSS-Speech 回答时不必先生成文字答案，但这不意味着没有文字监督或不继承文本知识。论文§2.1在36层中共享前32层，随后分成4层 text 和4层 speech；HF 固定配置与 `MossSpeechModel.__init__`、`forward` 也分别构建共享块／分支，再从同一共享状态路由。生成目标为 $\prod_t p(a_t\mid a_{<t},U)$，其中 $U$ 为输入语音 token；它省掉显式答案文字序列，不证明隐状态中没有文字化表征。[正式论文 §2.1／图3](https://proceedings.iclr.cc/paper_files/paper/2026/file/20cf299b663a37b5b936de2cb5713cf5-Paper-Conference.pdf#page=3)、[固定模型源码：L487–499、L657–688](https://huggingface.co/fnlp/MOSS-Speech/blob/cff025bb41d8459d59abac0b5e44aba7f659ec9e/modeling_moss_speech.py#L657)、[固定配置](https://huggingface.co/fnlp/MOSS-Speech/blob/cff025bb41d8459d59abac0b5e44aba7f659ec9e/config.json)。

分叉的动机来自 preview 中层对齐、顶层分化的相似度观察。余弦／DTW 图可提示在哪里专门化，不能证明存在一个可分离的“共享知识模块”；从28层 preview 的观察迁移到36层并选择末4层分叉，也仍是设计判断。[正式论文 §2.1／图2](https://proceedings.iclr.cc/paper_files/paper/2026/file/20cf299b663a37b5b936de2cb5713cf5-Paper-Conference.pdf#page=3)。

### 训练用文字，回答时省去文字中介

训练先以 ASR-only encoder 产生单码本表示，再冻结原文字骨干、训练语音 embedding／分支／head；第二阶段解冻并混入纯文本；SFT 使用同内容的四种文字／语音输入输出组合。训练资产还包括3–6秒转写／语音交错、文本合成语音和由文字 QA 改写得到的语音 QA。推理才是“输入语音→共享骨干→speech 分支→条件 flow／vocoder”，不需要先走 text 分支输出完整答案。[正式论文 §2.2、§3.1–3.2](https://proceedings.iclr.cc/paper_files/paper/2026/file/20cf299b663a37b5b936de2cb5713cf5-Paper-Conference.pdf#page=4)。

因果约束要按模块写：encoder 目标是 $a_t=E(X_{\le t\Delta})$，但仍有取帧／前端等待；decoder 不应自动写成零 lookahead。固定 codec 配置给出5 token chunk、3 token pre-lookahead；`CausalMaskedDiffWithXvec.inference` 在非 finalize 时明确切出尾部 lookahead。公开 HF 包装的 `token2wav` 又传入 `streaming=False`，`decode` 默认 `finalize=True`。这些证据说明流式组件设计与默认公开调用不同，不能由“fully causal encoder”推出整栈零等待或完整对话 TTFA。[固定 codec 配置 L13–30](https://huggingface.co/fnlp/MOSS-Speech-Codec/blob/eeec733e4e1dea7da444d332d8e1621ef257414c/flow/config.yaml#L13)、[flow `inference` L238–279](https://github.com/OpenMOSS/MOSS-Speech/blob/3a1001ae37b731ae49a98311139fb54c49230fd9/cosyvoice/flow/flow.py#L238)、[包装调用 L133–143、`decode` L405–414](https://huggingface.co/fnlp/MOSS-Speech-Codec/blob/eeec733e4e1dea7da444d332d8e1621ef257414c/modeling_moss_speech_codec.py#L133)。

### 语音适配为什么会损伤文字能力？

一个可检验的解释是：新增随机音频 embedding 早期把共享骨干推向不熟悉的输入分布，语音 next-token 梯度与原文字目标冲突。若 $g_s,g_t$ 为共享参数上的语音／文字梯度，则语音更新对文字损失的一阶影响为：

$$
\Delta\mathcal L_t\approx-\eta\,g_t^\top g_s.
\tag{推导}
$$

负内积会使文字损失上升；冻结令共享更新为零，先让新接口适应旧表示。但第二阶段共享层一旦漂移，即使 text head 冻住，其输入分布也会改变。这解释为何分叉和冻结能缓解、却不能自动消除遗忘；论文没有直接测上述梯度冲突，所以它是机制假说，不是确证。[正式论文 §3.1.2、§5](https://proceedings.iclr.cc/paper_files/paper/2026/file/20cf299b663a37b5b936de2cb5713cf5-Paper-Conference.pdf#page=5)。

表6中同为4层分叉，NF 的 MMLU 为62.11，FP–Full 为66.50，FP–Layerwise 为68.82，原骨干为76.60。NF–NoSplit 为60.97，支持分叉有益但幅度较小。它能证明该配方下训练日程影响能力保持，不能证明“知识无损迁移”，也不能把分叉收益与新增参数容量完全分离。冻结／解冻改变有效更新历史；“约两 epoch”也不是逐项计算预算严格匹配。[正式论文 §5／表6，PDF p.9](https://proceedings.iclr.cc/paper_files/paper/2026/file/20cf299b663a37b5b936de2cb5713cf5-Paper-Conference.pdf#page=9)。

“原生语音回答”描述的是输出路径。文字知识保留了多少，仍需看适配后的测试结果；分叉和冻结都没有消除表 6 中的能力下降。

## 4. 多人对话怎样记住每个角色的声音？

### 标签要与参考声线长期绑定

把剧本加上 `[S1]`、`[S2]` 不会自动获得稳定多角色生成。每个标记必须绑定参考声线，并跨长上下文保持。可用分析状态 $I_t=\{b_j,v_j,\rho_j\}_{j=1}^{N}$ 描述标签绑定、声线记忆与最近激活位置；令剧本位置为 $a_t$、当前说话人为 $s_t$，则：

$$
p(q[t,k]\mid C,H_t)
\approx p(q[t,k]\mid \mathrm{text}_{a_t},s_t,I_t,H_t),
\quad I_{t+1}=F(I_t,s_t,q[t,:]).
\tag{机制假说}
$$

这不是声称源码有显式 identity-state 张量，而是对 KV／隐状态需要保存什么的可检验描述。TTSD 附录A表2确实把每人参考音频与 `[Sj]` 配对，且默认联合 reference cloning 和 assistant-prefix continuation。[MOSS-TTSD §4.3／图2、附录A表2](https://arxiv.org/pdf/2603.19739v1#page=13)。

### 说话人标签怎样进入训练？

训练数据若把同一人错误拆成两个标签，或把参考槽绑定错，模型学到的就是冲突监督。论文§2描述从碎片 ASR 与 diarization 协调，到 MTD 一次转写并给标签；§3.2再从同源录音抽非重叠单人片段，绑定参考槽。3–5人数据因标注困难只保留少量高质量真实片段，再交错拼接单人片段补充长程身份学习。拼接能训练轮换，不能代替自然重叠／抢话数据。[MOSS-TTSD §2–3.2](https://arxiv.org/pdf/2603.19739v1#page=2)。

课程从单人 TTS 中间检查点开始，先学单／双人及参考绑定，再提高质量、减少单人比例，最后加入真实／合成多人；推理先 prefill 标签化完整剧本和参考／continuation 前缀，再生成连续 codec 流。这里最危险的混杂是 speaker identity 与节目背景、录音设备绑定：即使换人听感稳定，也可能部分靠背景捷径。[MOSS-TTSD §4.2–4.3](https://arxiv.org/pdf/2603.19739v1#page=5)。

### TTSD-eval 源码：两人边界与 ACC 的含义

评测以给定剧本做 MMS forced alignment，按标点／标签切段，再用声纹 embedding 比较参考。`MultiLingualAligner.align_waveform` 接收的是参考 transcript；`split._build_segments` 从标签更新 `current_speaker`，它没有独立辨认生成音频中谁在说话。[固定评测 SHA：`align_waveform` L108–145](https://github.com/OpenMOSS/TTSD-eval/blob/dea13b98529dc16dcfb5fe45779ad63ac9238337/tools/align.py#L108)、[`_build_segments` L97–143](https://github.com/OpenMOSS/TTSD-eval/blob/dea13b98529dc16dcfb5fe45779ad63ac9238337/tools/split.py#L97)。

公开 `run_similarity` 只读 `prompt_audio_speaker1/2`；`_process_segment_batch` 的预测为 `"[S1]" if sim1 >= sim2 else "[S2]"`，且任何非S1的真标签相似度都取 sim2。因此即使对齐器能解析 `[S3]`，整个评分器也不是任意 $N$ 人评测。其指标实质为 $\mathrm{ACC}=M^{-1}\sum_m1[\arg\max_{j\in\{1,2\}}\cos(e_m,r_j)=s_m]$，只度量“两候选参考中是否更像指定人”。[固定源码：`run_similarity` L271–277、`_process_segment_batch` L189–207](https://github.com/OpenMOSS/TTSD-eval/blob/dea13b98529dc16dcfb5fe45779ad63ac9238337/tools/run_similarity.py#L189)。

ACC 不能证明内容正确：错读一整句仍可能具有正确声纹；漏读会使强制对齐错配。它也不证明 overlap 自然，因为单段只赋一个标签、混合声纹只取一个胜者。源码还有具体偏差：相似度失败返回0，两边失败时平局选S1；默认把短音频重复到超过2秒、长音频截前30秒；最终分别输出 case 平均和 segment 平均，不是时长加权。[`_compute_similarity_safe` L176–186、`_normalize_pcm_seconds` L47–74、聚合 L423–426](https://github.com/OpenMOSS/TTSD-eval/blob/dea13b98529dc16dcfb5fe45779ad63ac9238337/tools/run_similarity.py#L47)。这些是当前公开评分实现的边界，不断言论文全部实验逐字使用同一代码版本。

### 声纹更接近，内容未必更准确

附录C表5联合模式的英文 SIM 从 clone-only 0.7228 升至0.7326，但 ACC 从0.9680降至0.9626，WER从9.39%升至9.88%；它支持参考与 continuation 联合更利于声纹，不支持所有指标全面改善。额外前缀还同时增加声学暴露和上下文，未隔离显式槽绑定机制。论文§5.1测试最长720秒，也不独立证明五人、60分钟稳定。[MOSS-TTSD 附录C表5、§5.1](https://arxiv.org/pdf/2603.19739v1#page=14)。

目前最缺的是相近声线、角色长时间离场后重返，以及重叠说话的评价。双人声纹分类分数无法覆盖这些情况，也不能代替内容准确度。

## 参考资料

材料核查于 2026-10-17。表内列出所用论文版本，相关公开入口见[来源索引](sources.md#audio)。

| 核心论文 | 作者简记／首发年 | 本文冻结版本／venue | 一手全文 |
|---|---|---|---|
| SpeechTokenizer: Unified Speech Tokenizer for Speech Language Models | Xin Zhang 等／2023 | 2308.16692v2；ICLR 2024 | [PDF](https://arxiv.org/pdf/2308.16692v2) |
| MOSS-Audio-Tokenizer: Scaling Audio Tokenizers for Future Audio Foundation Models | Yitian Gong 等／2026 | 2602.10934v2；arXiv report | [PDF](https://arxiv.org/pdf/2602.10934v2) |
| Towards True Speech-to-Speech Models Without Text Guidance | Xingjian Zhao 等／2025 | 2510.00499关联；ICLR 2026正式版 | [正式 PDF](https://proceedings.iclr.cc/paper_files/paper/2026/file/20cf299b663a37b5b936de2cb5713cf5-Paper-Conference.pdf) |
| MOSS-TTS Technical Report | Yitian Gong 等／2026 | 2603.18090v2；arXiv report | [PDF](https://arxiv.org/pdf/2603.18090v2) |
| MOSS-TTSD: Text to Spoken Dialogue Generation | Yuqian Zhang 等／2026 | 2603.19739v1；arXiv preprint | [PDF](https://arxiv.org/pdf/2603.19739v1) |

实验数字来自论文，计算示例为本文推导；未运行训练或性能复现。CAT 发布的是推理量化代码，不能据此核实完整训练梯度。
