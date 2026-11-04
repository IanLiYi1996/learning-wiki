# MOSS-Image：从设计要求到文字和布局

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

活动海报即使精美，只要日期写错、标题漏字或正文溢出，就无法直接使用。信息图还要求文案和空间层级清楚，约束比一般场景图严格得多。

短提示往往没有写明这些细节。系统需要先决定内容与布局，再忠实画出这份规格。扩写 prompt 可以补充选择，却不能保证生成器准确执行；提高渲染能力，也不会自动补全用户没提供的事实。[技术报告 §1–2](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

MOSS-Image 将文字转写、换行和矩形位置标注（bbox）纳入训练条件，并让 Agent 把简短请求转成文案与布局规格。DiT 负责去噪生成图片。理解这项工作，需要看清规划器做了哪些选择，以及生成器能执行到什么程度。[报告 §2–4](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

## 1. 精确文字和位置怎样进入监督？

### 1.1 将设计选择和像素执行分开

报告使用短／中／长 caption，并保留文字转写、换行和 bbox。自然语言与布局 JSON 都经过同一文字条件接口输入。[报告 §2、§3.2、附录 C](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

令目标图为 `X`，一般描述为 `C`，新增规格为 `L`。

```text
H(X | C,L) ≤ H(X | C)
```

新增条件在统计上减少合法图的歧义，但不保证有限模型训练效果单调变好：规格可能错、文字可能截断、布局可能不合理。它更不能证明“已经理解设计”；可能是把目标选择从生成器转移给提供 `L` 的规划器。

### 1.2 换行为何不只是排版装饰？

例如： 相同字符串“甲乙丙丁”可以是四字一行、两行各两字、四行竖排。内容相同但局部 glyph 位置和分行不同。只写总字符串，生成器要额外猜测行结构；明确 `甲乙\n丙丁` 与 bbox，就让词序、行边界和空间位置的训练监督一致。

报告为长 caption 转写可见文字而不翻译，并保留换行、读序、位置、字形与间距；但关于换行收益的材料主要是定性 case study，不能称为已独立隔离的全规模因果消融。[报告 §3.2、§6、附录 C.1／J](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

## 2. 为什么保留并标注有瑕疵的图片？

### 2.1 保留覆盖，用条件区分质量

报告先去重和移除 AI 图像，保留来源原有过滤；后续不再统一丢掉有水印、模糊或压缩瑕疵的真实图，而在 caption 中标记这些属性。它不是完全取消 NSFW 等安全过滤。[报告 §3.1、附录 B](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

把质量／瑕疵记为 `Q`，过滤相当于主要学习 `p(X|C,Q=good)`，标注则试图学到更宽的 `p(X|C,Q)`。在真实图片中，水印和密集文字、信息图、网络截图可能相关；过滤 watermark／naturalness 也可能误伤目标任务。

但条件化只有在标签足够准确、干净样本足够多、模型能分辨 `Q` 时才可靠。漏标的水印仍是无条件污染，标签错误可能把质量状态混合；稀有领域也不因一句“blurred”自动变得有用。

### 2.2 作者实验支持什么？

附录 B.2 用早期 24 层 multi-stream、Qwen3.5-0.8B、256×256 配置比较同为 1.6M steps 的两组训练。额外规则保留 43.35% 数据；OneIG 总分从 0.4363 降至 0.3482，其中 text 分数从 0.5243 降至 0.1180；DPG-Bench 几乎不变。**这不是最终 5B single-stream 的全部配方消融。**[报告附录 B.2、表 9–10](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

同训练步数控制了部分计算，但过滤同时改变样本覆盖、重复频率和领域分布。结论应是“这套额外规则损伤该早期实验的文字覆盖与部分质量”，不能扩成“所有质量筛选都无益”。FDR6 的真实参考分布还与未过滤数据有关，报告自己也提醒跨数据分布比较的局限。

## 3. 文字和图像怎样在 DiT 中交互？

### 3.1 文字是条件，图像是生成目标

冻结 Qwen3.5-9B 文本编码器给出条件特征；两层 text-only Transformer 做进一步投影，随后与图像 latent tokens 一起进入 42 层、隐藏 3072 的 joint self-attention。图像 VAE 是冻结的 FLUX.2 组件；5B 指 DiT，不包括整个系统所有模块。[报告 §3／架构图、附录 A](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)、[模型代码](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/comfyui/moss-image/model.py#L137)

抽象数据流为：

```text
caption／layout → 冻结文字 encoder → text-only projection → T
noised image latent → projection → I
[I;T] → joint DiT blocks → 只取 image 部分 → image latent velocity／prediction
```

文字随 joint block 更新，有助于与空间状态交互，但系统不是在此训练一个 next-token 文案回答器；文字的正确文案主要由条件提供。报告的文字监督集中在条件数据，不能擅自写成专门的逐字符 OCR 交叉熵训练。[报告 §3.2–3.3](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

### 3.2 四个坐标各代表什么？

固定 `_RoPE.forward` 第 118–134 行使用 `(r,f,h,w)`，其中 image tokens 的 `r=0,f=text_length`，空间位置居中；text tokens 的 `r=0,f=token_index,h=w=0`。[RoPE 代码](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/comfyui/moss-image/model.py#L118)

例如： text 长度 5、image 网格 2×3：

```text
text0=(0,0,0,0)，text4=(0,4,0,0)
image左上=(0,5,-0.5,-1)，image右下=(0,5,0.5,1)
```

`f` 区分文字序列和图像平面，并非真实视频时间；diffusion timestep 另经调制进入 block。`r=0` 使 reference 子空间的旋转为恒等，当前并未因预留该轴而拥有参考图编辑能力。`video_embedder` 等变量名也不能证明此 checkpoint 支持视频。[源码与报告 §3.3、§8](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

### 3.3 SiTU-GLU 的数值作用

源码 `_situ` 第 8–9 行为：

```text
[4 tanh(g/4) sigmoid(g)] × [25 tanh(u/25)]
```

小幅度时约为 `g sigmoid(g) u`，即 SwiGLU 风格；幅度大时，两项软饱和，其逐通道乘积绝对值不超过 100。这个界限仅在下投影之前成立，不能据此保证整个 block 激活或梯度都有限。它是训练稳定性选择，不是足以解释密集文字能力的单一机制。[实现](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/comfyui/moss-image/model.py#L8)

报告 Muon–AdamW 的 1B loss 收敛比较同样支持优化配方，不代表 final 5B 图片质量收益已完全被隔离。应把文字／布局数据的监督贡献与数值稳定性贡献分开。

## 4. 布局编译器能保证什么？

### 4.1 检查规格，转换坐标

外部 GPT-6 规划器选择任务指导、检索知识／参考、写出文案与布局。模型真正收到的是序列化文字条件；当前 DiT 不直接接受参考图。公开 `compile_prompt.py` 则检查 canvas 是正数且为 16 的倍数、元素有合法类型／literal text、bbox 有正面积且不越界。[报告 §4、§8](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)、[编译器第 58–108 行](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/skills/moss-image-prompt-enhancer/scripts/compile_prompt.py#L58)

其坐标转换不是照抄 bbox：

```text
输入：absolute xyxy = [x1,y1,x2,y2]
输出：centered yxyx =
[floor(y1)-H/2, floor(x1)-W/2, ceil(y2)-H/2, ceil(x2)-W/2]
```

例如： canvas=1024×768，bbox `[100.2,50.8,900.1,200.2]` 编为 `[-334,-412,-183,389]`。代码按边缘包围取整、交换 x/y、移到画布中心；复制未经转换的坐标会改变解释。[第 34–55 行](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/skills/moss-image-prompt-enhancer/scripts/compile_prompt.py#L34)

输出 JSON 不保留根级 `width/height`，因此调用方还要保证实际生成 canvas 与编译时一致。编译器约束的是**规格的结构合法性**，不是最终生成像素：没有一个硬几何求解器保证物体一定落在指定 bbox，文字一定不会溢出。这是学习式 soft control。

### 4.2 三类正确性必须分别检查

```text
知识／文案正确性 → 规划规格正确性 → 渲染执行正确性
```

例如： Agent 写错一个知识事实，bbox 却合法，DiT 逐字完美渲染；图像依然错误。反过来，文案正确但编译 canvas 用错，空间执行会偏。成功渲染不能替代检索核验，JSON schema 正确也不能替代设计审查。

所谓 zero-shot modification 当前是修改 layout 后重新生成，不是编辑已存在图片并保持其余像素不变；这意味着可比较设计，未必提供精确版本化编辑。[报告 §6、§8](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

## 5. 文字、位置和设计偏好怎样评价？

### 5.1 OCR coverage 会漏掉哪些错误？

LLTB 用 OCR 后的单位 multiset：英文按规范化词，中文按字符，忽略部分标点：

```text
matched_i = Σ_u min(count_GT(u),count_OCR(u))
recall_i  = matched_i / |GT|
```

组内按目标单位数加权，最后中英×三长度组等权得到 Mean-6。作者 96.3 是该 coverage，不是完整字符串正确率。[报告附录 G.1、式与表 4](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

例如： GT 为“上海”，OCR 为“海上”，multiset coverage=100%，语义却变了。GT 为 `cat dog cat`，OCR 为 `dog cat cat wrong`，coverage 仍 100%；词序和额外错词未直接受罚。

因此需额外测 sequence edit distance、标点／换行、位置、文字事实和无关插入；不能从 coverage 直接解释为海报可直接出版。报告其实也承认不检查顺序、不直接罚额外单位。240 tasks 源于 80 个 source entries 的三种 prefix 长度，统计重采样还应保留同源样本依赖。

### 5.2 mIoUdet 的分母为何重要？

7Bench 主表的 `mIoUdet=0.8786` 只在有正 overlap 的已检测目标上平均；all-target `mIoU=0.6788`，445/576 个目标有正 overlap，检测率 77.26%。它们对应定位质量和覆盖率两个问题，不宜只报道前者。[报告附录 G.4、表 19](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

其他模型的 safety refusal／缺失检测计零，会影响端到端可用性；若研究的是纯渲染能力，应同时报告条件成功子集与完整请求分布，不无声排除失败样本。

### 5.3 Elo 是相对偏好，不是跨实验质量单位

RLA 的短请求端到端、prompt ablation、共享增强 prompt 下 backbone 比较分别拟合 Bradley–Terry。相同“1800 Elo”在独立组中没有可直接相减的绝对意义。[报告 §5、附录 G.2–G.3](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)

若使用通常 Elo scale，同一组 `P(i beats j)=1/(1+10^((E_j-E_i)/400))`，相差 100 对应约 64%，不是“质量高 100 点”。不同组需共同 anchor 或直接交叉比较。

置信区间重叠不等价于排名一定不显著：模型估计共享任务和对手，差值的方差依赖协方差。应检验 paired preference 或按任务 cluster bootstrap；61 个任务上的大量投票不能当作同数量独立设计任务。对海报／信息图／UI 各自也应报告，而非只用平均掩盖类型差异。

这些结果支持模型执行密集文字和布局条件，但文案事实、文字顺序和原图编辑能力仍需分别判断。尤其要分清外部规划器与 DiT 的贡献。

## 参考资料

本文依据 MOSI.AI 的 [MOSS-Image Technical Report](https://github.com/OpenMOSS/MOSS-Image/blob/c1355e6b1986dfe8fba3c0455783a05899212342/paper/MOSS_Image_Technical_Report.pdf)，代码固定于 `c1355e6b1986`。材料核查于 2026-10-17，实验数字来自作者，计算例为本文推导；未生成测试图片。
