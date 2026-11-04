# OmniVAE 与 MOVA：怎样让画面和声音对上

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

生成钢琴演奏时，手指画面和音色可以各自逼真，但声音晚半秒，结果仍会让人出戏。多人说话还要求声线、台词和嘴形对应。音画生成因此要同时处理单模态质量与跨模态关系。[MOVA §1–2](https://arxiv.org/html/2602.08794v2)

先生成视频再配音，容易复用现成模型，却让配音阶段受已经确定的画面约束。联合生成允许两边相互修正，但需要学习不同信号之间的语义和时间对应。它们经过 VAE 压缩后的潜变量，也未必天然适合共同建模：能还原原信号，与容易被生成器学习，是两种要求。[OmniVAE §1–3](https://arxiv.org/pdf/2607.23855v2)

OmniVAE 在表示层加入语义和片段对齐监督；MOVA 则在联合去噪时通过 Bridge 交换信息。前者减少下游读取关系的困难，后者控制生成过程中的相互约束。两项工作可以互相启发，但已发布的 MOVA 尚不能视为换用了 OmniVAE。[OmniVAE §3](https://arxiv.org/pdf/2607.23855v2)、[MOVA §2、§4–5](https://arxiv.org/html/2602.08794v2)

## 1. OmniVAE 对齐了什么？

OmniVAE 保留：

```text
视频 x_v → E_v → z_v → D_v → 重建视频
音频 x_a → E_a → z_a → D_a → 重建音频
```

`z_v` 是时空张量，`z_a` 是一维时间序列，维度、采样网格和 decoder 不同。训练中的空间／时间聚合和 projector 得到：

```text
u_v[i,s] = normalize(P_v(Aggregate_v(z_v[i], s)))
u_a[i,s] = normalize(P_a(Aggregate_a(z_a[i], s)))
```

片段 `s` 的两种投影才通过余弦相似性学习对应关系。部署时聚合和蒸馏头被移除，VAE 仍各自运行。[论文 §3.1–3.3](https://arxiv.org/pdf/2607.23855v2)、[投影／归一化代码第 1491–1538 行](https://github.com/OpenMOSS/OmniVAE/blob/2749b39c24659e775fcc22bdcf3b3913313adeea/vae/omnivae/models/audio_video_vae/contrastive.py#L1491)

### 1.1 投影相近，潜变量仍可不同

即使 `P_v(z_v)≈P_a(z_a)`，也不推出 `z_v≈z_a`。例如 `z_v=A s+n_v`、`z_a=B s+n_a`，projector 分别学会取出语义 `s`，其余噪声／重建细节仍可能完全不同。对齐保留的是可读取的共有结构，不是两个完整潜分布恒等。

因而论文的合理主张是“下游容易读出对应关系”，不是“下游已经无需学习任何跨模态映射”。这也解释了为什么仍需要联合 DiT 和跨模态 bridge。

### 1.2 首帧为什么不能像其他帧一样切？

因果视频 VAE 的首个 latent 对应一张输入帧，后续 latent 覆盖多帧时间块。若把它们当等时长单元均匀切段，开头的音视频会错位。当前 `contrastive.py` 的 `_align_causal_first_frame` 第 1443–1473 行去掉首视频 latent，并按对应原始时长比例去掉音频 latent。蒸馏路径则把首帧和 image teacher 特征对齐。[论文 §3.2–3.3](https://arxiv.org/pdf/2607.23855v2)、[首帧校正实现](https://github.com/OpenMOSS/OmniVAE/blob/2749b39c24659e775fcc22bdcf3b3913313adeea/vae/omnivae/models/audio_video_vae/contrastive.py#L1443)

这一步避免了“标注时间正确，latent 的时间覆盖却错位”的训练错误。

## 2. 负样本怎样逼模型区分时间？

论文把 8 秒 clip 切成 48 个约 1/6 秒片段。正样本为同一 clip、同一 segment 的音视频；默认负例来自三个层级：47 个同 clip 其他 segment、48 个同源长视频的另一个 clip、24 个其他源视频的 segment。[论文 §3.2、式 (1)](https://arxiv.org/pdf/2607.23855v2)

目标为：

```text
L_v→a = -(1/BS) Σ_(i,s) log[
  exp(u_v[i,s]·u_a[i,s]/τ)
  / Σ_(j,t)∈positive∪negatives exp(u_v[i,s]·u_a[j,t]/τ)
]
L_align = (L_v→a + L_a→v)/2
```

| 负样本层级 | 主要防止的捷径 | 潜在代价 |
|---|---|---|
| 同 clip 不同时刻 | 只识别这个视频属于什么主题，不识别事件时刻 | 重复／静止内容可能成为语义近似的负样本 |
| 同源视频不同 clip | 利用拍摄者、场景、人物身份区分不同视频 | 连续素材中的类似事件并不一定真的语义不同 |
| 不同源视频 | 缺少跨主题区分能力 | 任务可能太容易，只学习类别差异 |

“防止捷径”是本文对目标的分析；三类采样机制由论文与源码支持。当前 `sample_negatives_for_loss` 第 1289–1374 行构造正样本列、候选负例、valid mask，计算两方向 logits；无效 padding 不进入 softmax。[固定实现](https://github.com/OpenMOSS/OmniVAE/blob/2749b39c24659e775fcc22bdcf3b3913313adeea/vae/omnivae/models/audio_video_vae/contrastive.py#L1289)

### 2.1 最小反例：主题对了，声音晚了两秒

假设 甲视频全程是钢琴，乙视频全程是汽车。若只有跨视频负例，编码器仅输出“钢琴／汽车”就能轻松区分；甲的声音错移两秒，clip identity 仍正确。加入甲视频内不同时刻负例后，模型才必须捕捉敲键与声学 onset 的具体对应。

但这种监督仍不是“因果物理世界模型”：片段对应与动作导致后果是不同对象。闪电后延迟出现雷声在物理上合理，强迫零延迟反而错误。应同时测试自然传播延迟、声音来自画外和背景音乐，避免把训练的同步先验当成全部音画关系。

### 2.2 粒度不是越细越好

片段太细，聚合后的信噪比会降低；太粗，则容易漏掉片段内部的漂移。48 段／8 秒约 167ms，只说明监督怎样切分，没有证明生成后的音素对齐误差小于这个值。

## 3. 语义对齐为什么会牺牲部分重建质量？

OmniVAE 同时优化：

```text
L_v = λ_vr L_video_recon + λ_vd L_video_distill + λ_av L_align
L_a = λ_ar L_audio_recon + λ_ad L_audio_distill + λ_av L_align
```

共享 `L_align` 联合优化时只算一次，不应因在两个分支的书面公式出现两次就重复加权。视频重建含 L1／LPIPS／KL，音频含波形／多分辨率 mel／KL；语义蒸馏使用冻结 Qwen3-Omni teacher 的特征，简式为 `-mean log sigmoid(cos(project(z), teacher(x)))`。[论文 §3.3–3.4](https://arxiv.org/pdf/2607.23855v2)

### 3.1 蒸馏在保留什么，可能损失什么？

重建要求保留包括细纹理、音色、背景噪声的具体信号；语义表示通常允许同义、视角或细节变化。因此目标之间并不天然一致。论文表 2 就显示了真实取舍，例如 UCF-101 PSNR：Recon 36.93，完整 OmniVAE 36.27；音频 AudioSet／MUSDB18 的 ViSQOL 也从 Recon 的 4.55／4.60 降至完整模型的 4.08／4.31。[论文表 2](https://arxiv.org/pdf/2607.23855v2)

对齐监督牺牲了部分重建精度，是否值得要看下游生成收益。四个内部配置使用相同骨干，比训练条件不同的外部 VAE 更适合判断这项取舍。

### 3.2 损失配平与梯度配平

论文使用 loss-magnitude weighting；公开 recipe 还包含 adaptive ratio 参数。[论文 §3.4、§4.5.2](https://arxiv.org/pdf/2607.23855v2)、[stage3 recipe](https://github.com/OpenMOSS/OmniVAE/blob/2749b39c24659e775fcc22bdcf3b3913313adeea/vae/scripts/recipes/stage3_av_align.sh)

表 6 比较了损失值配平、以 encoder 末层为代理的 GradNorm，以及 uncertainty weighting：[论文表 6](https://arxiv.org/pdf/2607.23855v2)

| 平衡方式 | Intra A@48↑ | Overall A@64↑ | Video PSNR↑ |
|---|---:|---:|---:|
| Loss magnitude | 0.51 | 0.24 | 34.1 |
| GradNorm（末层 proxy） | 0.44 | 0.17 | 35.4 |
| Uncertainty adaptive | 0.29 | 0.13 | 33.4 |

该实验支持 loss-magnitude 在此配方中取得更好的检索／重建取舍；GradNorm 更高的 PSNR 不等于更强的对应关系。末层 proxy 又不测完整 encoder 的梯度冲突，因此不能从这一表推广“任何梯度平衡都劣于 loss 数值平衡”。

从数学上看，`λ_1 E[L_1]≈λ_2 E[L_2]` 不保证 `||λ_1∇L_1||≈||λ_2∇L_2||`，也不保证梯度同向。损失值很大，梯度仍可能很小；所以表中的经验结果不能推广为两种配平方式等价。

### 3.3 为什么后期只训练 audio decoder？

语义／对比阶段为了节约长 clip 和负例的内存，移除了判别器／feature matching，作者观察到轻微电子音。之后冻结 audio encoder，只微调 decoder 的对抗与 feature-matching 目标，就能改善波形外观而不改变已有 latent 坐标。[论文 §3.4](https://arxiv.org/pdf/2607.23855v2)

这是明确的优化分工：`E_a` 的语义／同步结构固定，`D_a` 的信号还原改善。但它不能追回 encoder 已丢弃的信息；如果身份线索根本没进 latent，再好的 decoder 也不能凭空还原。

## 4. MOVA 的两个“时间”：物理时间不等于扩散时间

### 4.1 Aligned RoPE 对齐的是事件的物理时刻

视频和音频经过 VAE 后的帧率不同。如果都直接用整数 `0,1,2,...`，同一个 index 可能代表不同秒数。MOVA 将视频时间位置缩放到音频时间单位：

```text
position_audio(j) = j
position_video(i) = i·r_audio/r_video
```

同一视频 latent frame 内不同空间 patch 可以共享该时间位置；空间信息仍由视频骨干的编码负责。当前 `DualTowerConditionalBridge.build_aligned_freqs` 第 420–475 行实现该关系，并可考虑因果 VAE 的首帧时间偏置。[论文 §2.2](https://arxiv.org/html/2602.08794v2#S2.SS2)、[Bridge 实现](https://github.com/OpenMOSS/MOVA/blob/1591b2557b42030a3421442c998dd6f5602ed9bd/mova/diffusion/models/interactionv2.py#L420)

例如： 视频 latent 6Hz、音频 latent 50Hz，视频 index 6 与音频 index 50 都是一秒附近；整数 index 6 与 6 却不在同一时刻。这种坐标换算解决索引错配，不能自己生成正确的发声／口形关系，后者仍需要数据学习。

### 4.2 noise time 对齐的是信息确定程度

Flow matching 的简化表示：

```text
z_m(t_m) = (1-σ_m(t_m)) z_m(0) + σ_m(t_m) ε_m
target_velocity_m = ε_m - z_m(0)
```

物理上同一时刻的音视频，可以处在不同去噪阶段。`t_video≠t_audio` 不意味着音频在故事里比视频晚几秒，而是两种模态当前被噪声破坏的程度不同。[论文 §2.1、§4.4](https://arxiv.org/html/2602.08794v2#S4.SS4)

上式的 `ε-z(0)` 是以 `σ` 为路径参数的 velocity。若对原始 `t` 求导，链式法则给出 `dz/dt=σ'(t)(ε-z(0))`，不能漏掉导数因子。公开 scheduler 用 `Δσ` 更新样本，其训练目标仍是 `ε-clean`；噪声标签、ODE 参数和实际 step 单位须一起核对。[scheduler 第 80–113 行](https://github.com/OpenMOSS/MOVA/blob/1591b2557b42030a3421442c998dd6f5602ed9bd/mova/diffusion/schedulers/flow_match.py#L80)

论文为大规模训练独立抽样两个时间，并在不同阶段调整 sigma shift。本文的解释是：相对更确定的模态可以为另一模态提供更可靠的条件；固定 schedule 因此也是一种隐式信息流先验，未必适合所有物理事件。[论文 §7.1](https://arxiv.org/html/2602.08794v2#S7.SS1)

### 4.3 论文公式与 scheduler 的差异

v2 PDF 与 HTML 的 §4.4 都显示：

```text
σ_paper(t;s) = s·t / [s+t(1-s)]
```

公开 `FlowMatchScheduler.set_timesteps` 第 57 行则是：

```text
σ_code(t;s) = s·t / [1+(s-1)t]
```

当 `s=5`：

| t | 论文展示的式子 | 公开代码式子 |
|---|---:|---:|
| 0 | 0 | 0 |
| 0.25 | 0.3125 | 0.625 |
| 0.5 | 0.8333 | 0.8333 |
| 1 | 5 | 1 |

前者的 `σ(1)=5` 与以 `[0,1]` 为凸混合系数的描述不一致，不能直接照抄重写 scheduler。**本次没有找到作者对这一差异的说明；可能是公式排版／笔误，不能据此推定实际训练用了错误 scheduler。** 复现应明确采用哪个实现，而不是悄悄改掉论文式子。[论文 §4.4／式 (4) 后的定义](https://arxiv.org/html/2602.08794v2#S4.SS4)、[固定代码第 57 行](https://github.com/OpenMOSS/MOVA/blob/1591b2557b42030a3421442c998dd6f5602ed9bd/mova/diffusion/schedulers/flow_match.py#L57)

## 5. Dual CFG 分别加强了哪种条件？

把三个预测简记为：

```text
v00 = vθ(z_t, 无文字, 无Bridge)
v01 = vθ(z_t, 无文字, 有Bridge)
v11 = vθ(z_t, 有文字, 有Bridge)

v_guided = v00 + s_B(v01-v00) + s_T(v11-v01)
```

论文式 (6) 的两个旋钮，控制的是跨模态条件和在跨模态条件之上的文字条件。一般情况要三次模型计算；`s_B=1` 时化为标准 text CFG；`s_B=s_T=s` 时化为 `v00+s(v11-v00)`，同样只需两次。[论文 §5.1、§7.2](https://arxiv.org/html/2602.08794v2#S5.SS1)

### 5.1 为什么同步增强会牺牲“谁说了什么”？

论文表 5 的部分作者结果：

| s_B | DeSync↓ | LSE-C↑ | cpCER↓ | DNSMOS↑ |
|---|---:|---:|---:|---:|
| 1.0 | 0.475 | 6.278 | 0.177 | 3.797 |
| 3.5 | 0.351 | 7.800 | 0.247 | 3.674 |
| 4.0 | 0.365 | 7.891 | 0.264 | 3.631 |

提高引导强度改善了部分同步指标，却损伤音质和内容／说话人正确性。DeSync 从 3.5 到 4.0 还出现反向变化，收益并非单调。[论文表 5](https://arxiv.org/html/2602.08794v2#S6.T5)

从概率模型看， Bayes 因子分解提供了一个可解释的引导方向；它并不自动证明三种网络运行模式是校准的概率 score。Bridge 条件来自另一个正在变化的模态，不是永远固定的外部观测；网络预测和 flow velocity 的近似还需要经验验证。因此应把 dual CFG 看成有结构的控制机制，不称为“保证正确联合后验的无偏采样”。

### 5.2 默认公开入口不是论文所有推理模式

固定版本 `pipeline_mova.py` 的 `MOVA.__call__` 第 347 行将 `cfg_mode="text"`设为局部变量；默认 CLI `scripts/inference_single.py`只公开 `--cfg_scale`。这个调用路径的普通 CFG 不应被描述为已启用独立 `s_B,s_T` 的三分支方案。[pipeline](https://github.com/OpenMOSS/MOVA/blob/1591b2557b42030a3421442c998dd6f5602ed9bd/mova/diffusion/pipelines/pipeline_mova.py#L322)、[CLI](https://github.com/OpenMOSS/MOVA/blob/1591b2557b42030a3421442c998dd6f5602ed9bd/scripts/inference_single.py)

同样，公开 fine-tuning `sample_timestep_pair` 读取一条 paired schedule 的同一行，`training_step` 的默认配置写 `independent_timesteps=False`；这不是论文原始大规模训练“独立抽两个 uniform times”的同一协议。此结论只针对已核查默认入口，不否认其他服务、训练代码或内部实验可能实现不同路径。[训练源码第 1018–1036、1380–1397 行](https://github.com/OpenMOSS/MOVA/blob/1591b2557b42030a3421442c998dd6f5602ed9bd/mova/diffusion/pipelines/mova_train.py#L1018)

## 6. 同步测试与生成测试测的是不同能力

OmniVAE 的 sync probe 分类 -2 到 +2 秒、每 0.2 秒一类，共 21 类偏移。冻结表示时，Recon 的 A@1 为 6.4%，完整模型为 20.2%；它支持更容易读取时间对应关系，不代表“生成只有 20.2% 能同步”。A@1tol 又允许 ±1 类，不应混成一个精度指标。[论文表 3](https://arxiv.org/pdf/2607.23855v2)

下游四组相同 VAE 骨干与目标组合比对，比外部不同 VAE 的榜单更能支撑目标贡献。但该研究的 Verse-Bench TED prompts 为适配 256×256 人脸检测，改写成近景／中近景；四组用同一改写，内部比较较合理，不能直接对照原始 prompt 下 MOVA 或其他论文的唇形分数。[论文 §4.4](https://arxiv.org/pdf/2607.23855v2)

发布 recipe 与论文还须分开：论文 teacher 视觉层为 27；当前 stage3 shell 默认 `--distill_vision_layer 18`，并将独立蒸馏与 joint alignment 分成更多操作阶段。阶段命名不同不一定是错误，但运行该默认 recipe 也不能宣称精确重现论文所有检查点。[论文 §4.1](https://arxiv.org/pdf/2607.23855v2)、[recipe 第 38–54 行](https://github.com/OpenMOSS/OmniVAE/blob/2749b39c24659e775fcc22bdcf3b3913313adeea/vae/scripts/recipes/stage3_av_align.sh#L38)

## 资料与代码版本

所用论文为 Jun Zhan 等的 OmniVAE `2607.23855v2`、OpenMOSS Team 的 MOVA `2602.08794v2`，完整信息见[论文目录](sources.md)。实验数字来自作者，计算例为本文推导；未运行模型。

代码核查于 2026-10-17，固定提交为 OmniVAE `2749b39c2465`、MOVA `1591b2557b42`。
