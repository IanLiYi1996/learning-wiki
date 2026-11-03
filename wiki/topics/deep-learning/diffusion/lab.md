# 扩散后训练与推理工程：标准库手算实验

<a id="diffusion-lab"></a>

研究日期：2026-11-03。[返回专题](README.md)。这个实验只操作小数组与公式，不运行图像生成模型，不使用 GPU，不下载权重，不调用模型 API。它核验的是本 Wiki 的教学数字，不是任何论文的实验成绩。

源码：[scripts/diffusion_lab.py](https://github.com/IanLiYi1996/learning-wiki/blob/main/scripts/diffusion_lab.py)；测试：[tests/test_diffusion_lab.py](https://github.com/IanLiYi1996/learning-wiki/blob/main/tests/test_diffusion_lab.py)。

Python 3.9+，零第三方依赖，在仓库根目录运行：

```bash
python -B scripts/diffusion_lab.py
python -B -m unittest discover -s tests -p 'test_diffusion_lab.py' -v
```

## A. DPO 的符号：偏好差距增大，损失应该下降

输入是两种候选的**假想 log 概率差**，并非扩散模型的图像 likelihood。定义 $z=\beta(\Delta_\theta-\Delta_{\rm ref})$，输出 $\sigma(z)$ 与 $-\log\sigma(z)$。

调用 `dpo_pair(0)` 得到概率 0.5、损失约 0.693147；调用 `dpo_pair(2)` 得到约 0.880797、0.126928。测试检查方向、reference 差距、beta 和 ±1000 的数值稳定性。若把赢家和输家倒过来，差距符号也必须改变。

请不要把这里的 gap 直接替换成未经符号推导的 denoising error。扩散 DPO 如何用误差代理，见[第 01 章](01-dpo-and-preference-pairs.md)。

## B. 多奖励：先混合还是先归一化

三个候选的评分分别为 A=`[0,100,200]`、B=`[2,1,0]`。原始相加后为 `[2,101,200]`，A 的大尺度主导排序。若各自归一化，两项基本抵消，说明冲突，并不说明三个候选真实质量相同。

教学约定为总体标准差：

$$
\mu=\frac{1}{n}\sum_i r_i,\qquad
\sigma=\sqrt{\frac{1}{n}\sum_i(r_i-\mu)^2},
\qquad a_i=\frac{r_i-\mu}{\sigma+10^{-8}}.
$$

`normalized([7,7,7])` 输出零向量，没有 NaN。实现先识别全等组，并在尺度变换后稳定计算标准差，测试还覆盖很大非整数的常量组和极小差值，避免浮点误差制造假优势。零优势意味着组内这个信号无法区分候选，而不是“所有候选都好”。正尺度变化在 epsilon 可忽略时保持归一化结果；极小尺度时不能声称严格不变。

`combined_advantages(..., per_channel=True)` 是**教学组合**，不完整复刻 GDPO、GD²PO 或 DAPO。权重非负，不自动判断哪个奖励重要。`gates=[True,True,False]` 只把最后一个信号置零，不进行二次归一化，所以输出均值可能不为零。这不是有意保持无偏的 policy-gradient 实现。

`conflicting([1,0],[-1,0])` 展示共享参数坐标中的负点积；它不是仅凭两个奖励分数就能推知真实梯度冲突的算法。更多边界见[第 03 章](03-rewards-judges-and-advantages.md)。

## C. Roofline：增加峰值不总能救吞吐

`roofline` 的输入单位依次是 FLOPs、bytes、FLOP/s、bytes/s。假想任务 A：10 TFLOPs、1 TB，硬件为 100 TFLOP/s 与 1 TB/s。

输出计算下界 0.1 秒、搬运下界 1 秒，最终下界 1 秒。峰值计算翻倍，下界还是 1 秒；搬运量减半，变成 0.5 秒。任务 B 把流量改为 0.01 TB，则计算成为限制，下界为 0.1 秒。

没有测量实际内核，不能把此处下界直接标成“预测运行时间”。启动、通信、频率与其他串行部分不在模型里。概念解释见[第 05 章](05-gpu-and-memory-roofline.md)。

## D. 视频 token：裁剪、padding、时间覆盖

`video_tokens(1280,720,16)` 返回 `(40,22,4,3520)`，使用作者计算器的 floor 口径。

空间采用 `spatial_policy="ceil"`，返回 `(40,23,4,3680)`；再指定 `time_policy="ceil"`，返回 `(40,23,5,4600)`。这些差异说明输入协议是成本模型的一部分，不代表真实 VAE 接受任意帧数且恰好输出这些形状。

一帧的特例也有测试。floor 产生空空间格、输入非整数或策略名称错误时拒绝计算，避免生成貌似合理的零成本。

## E. 稀疏注意力：不要连投影一起除掉

`attention_flops(100,10,4)` 返回 **180000**；密集版本为 **480000**，直接除以四则是 **120000**。本课只对连接项使用四倍稀疏假设，投影工作保留。

`dit_flops` 另加两层线性 FFN、可显式传入 cross-attention 成本，再乘层数、步数与 CFG 分支数。这是粗略 FLOPs 模型，不包含 softmax、VAE 和 wall-clock 内核行为。

`weight_memory(14_000_000_000)` 返回原始 BF16 权重 **28 GB／约 26.077 GiB**；不是运行或训练的总显存。作者计算器的说明／代码差异及性能边界见[第 06 章](06-realtime-video-estimates.md)。

## F. Oracle：错误结果再快也不进入排名

`oracle_accepts([.2,.4],[.2,NaN])` 返回 `False`。错长度、Inf、超容差也会被拒绝；`[.2,.4000001]` 在默认容差内通过。

这里比较扁平有限数值序列，容差以参考输出为基准，并使用共同尺度避免差值和容差同时溢出后发生 `inf <= inf` 的假通过。计算容量或组合优势若超出浮点范围则拒绝；公式选择器必须是真正的布尔值，字符串 `"False"` 不可充当 `False`。它不验证复杂张量布局、模型梯度、采样分布或最终质量。运行时间故意不作为输入：先验正确性，再谈提速，见[第 04 章](04-autoresearch-and-oracles.md)。

## 练习：修改一个变量，先预测，再运行

1. 把 DPO gap 从 2 改为 -2，概率和损失向哪里变化？
2. 所有奖励都相同，优势为什么没有更新信息？
3. B 奖励反映计数正确性，能否因为 A 尺度大就忽略 B？
4. 把任务 A 的峰值翻倍、流量不变，为什么下界不变？
5. 把空间尺寸都翻倍，固定其他变量，token 大约怎样变化，密集二次项呢？
6. 把步数从 8 改为 4，是否证明用户端延迟减半？

参考答案：①概率下降、损失上升。②组内相对分数为零；要检查采样是否没有差异、奖励是否失效。③不能，量纲不是任务优先级，需设计归一化、权重或硬约束。④带宽仍限制。⑤忽略取整时 token 为四倍、二次项十六倍，投影和 FFN 不是十六倍。⑥只证明这个简化算术模型的去噪工作减少，端到端仍有其他成本与质量问题。

<a id="public-sources"></a>

## 实验来源与边界

逻辑背景来自各章的一手来源；具体数组、假想硬件、180000／120000 对照和 oracle fixture 为本 Wiki 原创。它们没有引用或声称复现论文的图像分数、GPU 速度、统计显著性或模型质量。
