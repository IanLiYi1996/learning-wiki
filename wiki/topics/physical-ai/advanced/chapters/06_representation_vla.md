## 06 表示与网络：从像素和语言到机器人动作

### 06.1 输入不是状态：先建立张量接口

沿用第 01 章：$s_t$ 是真实状态，$o_t$ 是传感器观测，$a_t$ 是策略动作，$u_t$ 是控制器送入执行机构的输入，$q_t$ 是关节变量。本章讨论如何实现从观测到动作的网络，不把视觉特征当作完整真实状态，也不把关节位置目标等同于电机力矩。以下维度是教学接口；具体模型是否接收某种模态，必须另外核实。

设一批 RGB 图像为 $I\in\mathbb R^{B\times H_I\times W_I\times3}$。把图像切成边长 $P$ 的不重叠 patch，展平后得到 $X_{\rm patch}\in\mathbb R^{B\times N_v\times3P^2}$，再作投影：

$$
N_v=\frac{H_IW_I}{P^2},\qquad
E_v=X_{\rm patch}W_v+b_v+E_{\rm pos}+E_{\rm camera}+E_{\rm time}.
$$

这里 $B$ 是批大小，$H_I,W_I$ 是图像高宽，假设均能被 $P$ 整除；$N_v$ 是每张图的 patch 数，$d$ 是统一特征宽度；$W_v\in\mathbb R^{3P^2\times d}$、$b_v\in\mathbb R^d$ 是可学习投影，结果 $E_v\in\mathbb R^{B\times N_v\times d}$。其余三项是广播到同一形状的位置、相机身份和观测时间编码，单图可省略后两项。patch 投影及位置编码来自 [ViT §3.1](https://arxiv.org/pdf/2010.11929v2)；相机、时间项是本书的多模态接口设计，不声称原始 ViT 使用了它们。

自创维度例：$224\times224$ 图像、$P=16$，得到 196 个视觉 token，每个原始 patch 有 768 个数；两台相机、三帧历史合计 1176 个视觉 token。它们仍是图像局部的编码，并不是 1176 个有物理坐标的物体。若图像先经过视觉骨干，应将骨干输出的特征宽度投影到 $d$，而非重复对原像素投影；裁剪与缩放的几何含义也须保留。

本体感知可拼成 $p_t=[q_t,\dot q_t,g_t]\in\mathbb R^{d_p}$，包含关节位置、速度及夹爪读数，归一化后通过 MLP 映射成一个或多个 $d$ 维 token；$d_p$ 是本体向量宽度，$g_t$ 是夹爪读数。不能把“缺失传感器”填零后当作真实零读数，应附有效性标记。语言先分词为整数数组 $\ell\in\{0,\ldots,|\mathcal V|-1\}^{B\times N_l}$，查表 $E_l=E_{\rm vocab}[\ell]$ 得到 $B\times N_l\times d$；$\mathcal V$ 是词表，$N_l$ 是文本长度，$E_{\rm vocab}\in\mathbb R^{|\mathcal V|\times d}$ 是嵌入矩阵。查表与视觉投影统一的是宽度，不是模态含义。[Transformer §3.4](https://arxiv.org/pdf/1706.03762v7)给出 token embedding；[openpi 的 prefix／suffix 实现](https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/models/pi0.py)则可具体检查图像、语言、本体 token 如何接入。

### 06.2 Q、K、V 究竟算了什么

把可用模态拼成 $X\in\mathbb R^{B\times N\times d}$，其中 $N$ 是总 token 数。单个注意力头执行：

$$
Q=XW_Q,\quad K=XW_K,\quad V=XW_V,\qquad
Y=\operatorname{softmax}_{j}\!\left(\frac{QK^\top}{\sqrt{d_h}}+M\right)V.
$$

这里 $d$ 是模型特征宽度，$d_h$ 是本例单头宽度，取查询、键、值宽度相同；$W_Q,W_K,W_V\in\mathbb R^{d\times d_h}$，所以 $Q,K,V$ 均为 $B\times N\times d_h$。转置只作用于最后两轴，分数及加性 mask $M$ 为 $B\times N\times N$，可按批广播。softmax 沿被查询位置 $j$ 归一化，输出 $Y$ 为 $B\times N\times d_h$。本式 $Q$ 是查询矩阵，不是第 08 章的动作价值函数。多个头的输出拼接后投影回 $d$，再接残差、归一化与逐 token MLP。[注意力原论文 §3.2](https://arxiv.org/pdf/1706.03762v7)给出这套运算。

缩放的直觉可自行推导：假设查询与键各分量相互独立、均值为零、方差为一，点积是 $d_h$ 个乘积之和，方差为 $d_h$；除以 $\sqrt{d_h}$ 后量级才不随宽度增长。实际训练特征未必满足独立假设，因此这是初始化量级解释，不是模型全过程的统计保证。注意力只是加权混合信息，没有内置刚体运动学或碰撞约束。

mask 决定训练时有没有偷看答案。允许连接令 $M_{ij}=0$，禁止连接令其为 $-\infty$；padding token 也要屏蔽。自回归动作 token 使用因果 mask，并将输入标签右移，当前位置只能看到已知前缀。连续生成头可让同一条带噪动作段内的 token 双向注意，但观测不能包含未来真实图像，干净动作也不能作为未说明的输入。注意力 mask、动作损失 mask、动作归一化 mask 是三种不同对象，不能共用一个布尔数组；实现中还应防止有效查询的整行全被屏蔽。[因果解码说明](https://arxiv.org/pdf/1706.03762v7)与 [openpi 的 make_attn_mask](https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/models/pi0.py)提供两种具体检查入口。

### 06.3 动作空间、坐标和旋转是模型契约

动作可表示关节目标、末端绝对位姿或末端增量。比如在机器人基座坐标系中表达的平移增量，不能直接当作相机坐标增量；“每步位移”也不能当作“每秒速度”。同一个数值动作在采样周期改变后有不同物理含义。归一化只改变数值尺度，不会自动转换坐标系、弥补标定误差或改变控制器接口。

对选定的连续动作维度，可以用训练集的上下界统计作仿射映射：

$$
\widetilde a_j=\operatorname{clip}\!\left(2\frac{a_j-l_j}{h_j-l_j}-1,-1,1\right),\qquad
a_j=l_j+\frac{\widetilde a_j+1}{2}(h_j-l_j).
$$

这里 $j$ 是动作维度，$l_j,h_j$ 是该维度的训练统计，假设 $h_j>l_j$；$\widetilde a_j$ 是无量纲值，反变换恢复原单位。若正向发生裁剪，反变换不能恢复被截断部分。常量维度需单独处理，夹爪离散开关也未必适用同一变换。原始 OpenVLA 使用第 1／99 百分位及按维度选择的 mask；实际恢复应选对数据集的 `unnorm_key`，见 [OpenVLA predict_action](https://github.com/openvla/openvla/blob/main/prismatic/models/vlas/openvla.py)。

旋转表示也需写明。这里采用 rot6d：网络输出两个三维列向量，再正交化：

$$
b_1=\frac{r_1}{\|r_1\|_2},\qquad
w=r_2-(b_1^\top r_2)b_1,\qquad
b_2=\frac{w}{\|w\|_2},\qquad
R=[\,b_1\ \ b_2\ \ b_1\times b_2\,].
$$

这里 $r_1,r_2,w,b_1,b_2\in\mathbb R^3$，$R\in SO(3)$；假设 $r_1$ 非零、两输入不共线，否则归一化退化，需检测或带阈值处理，不能宣称任意六个数都稳定。约定 $R=R_{B\leftarrow E}$，把末端坐标向量变到基座坐标；若预测的是增量旋转，右乘 $R_{\rm new}=R_{\rm old}\Delta R$ 表示末端局部增量，左乘表示基座侧增量，两者不可混用。六维重建的依据是 [旋转表示原论文 §4.2](https://openaccess.thecvf.com/content_CVPR_2019/papers/Zhou_On_the_Continuity_of_Rotation_Representations_in_Neural_Networks_CVPR_2019_paper.pdf)。

若改用四元数，本书记作 $\rho=(w,x,y,z)$，不占用关节符号 $q$；单位化后 $\rho$ 与 $-\rho$ 表示同一旋转。训练需处理符号等价，不能简单平均两者后再单位化。rot6d 中“六维”是旋转编码长度，不是机器人六个关节；更换编码也会改变动作头输出宽度，旧 checkpoint 不能不经适配直接解码。

### 06.4 离散 token 与连续动作头

离散化的一般实现是将每个归一化标量划成 $K_a$ 个等宽区间：

$$
b_j=\min\!\left(K_a-1,\left\lfloor\frac{K_a(\widetilde a_j+1)}2\right\rfloor\right),\qquad
\widehat{\widetilde a}_j=-1+\frac{2(b_j+1/2)}{K_a}.
$$

这里假设 $\widetilde a_j\in[-1,1]$，$b_j\in\{0,\ldots,K_a-1\}$ 是区间编号，帽号表示用区间中心恢复。未裁剪时，归一化量化误差不超过 $1/K_a$。这是本书的理想等宽分箱，不是 OpenVLA 代码的逐行转录：其 `linspace` 生成 256 个边界、255 个中心，再用 `digitize` 和末端裁剪；复现 checkpoint 必须保留这项边界细节，见 [ActionTokenizer](https://github.com/openvla/openvla/blob/main/prismatic/vla/action_tokenizer.py)。

离散头输出词表 logits，训练监督是示范动作转换成的整数 token；交叉熵仅在动作目标位置计算，图像和输入指令不能误算成待预测标签。连续头则把动作查询的隐藏表示 $B\times H_a\times d$ 投影为 $B\times H_a\times d_a$，直接回归动作、噪声或生成速度；$H_a$ 是预测步数，$d_a$ 是每步动作宽度，三种回归目标在第 07 章区分。若扩展仍采用每步七维动作，chunk 是 $H_a\times7$，增加的是时间轴，不是新的物理自由度。回归头并不会天然满足旋转、速度或碰撞约束。

原始 [OpenVLA v3 §3、§6](https://arxiv.org/pdf/2406.09246v3)接收单张 RGB 与指令，预测单步七维动作：三维平移、三维旋转相关分量和一个夹爪分量；七维不是七个关节，也不是七步 chunk。其视觉骨干融合两路特征，经投影进入语言骨干，再逐动作 token 解码。后续 OFT 的连续输出、多图输入等属于另一套扩展配方，官方 [README 版本说明](https://github.com/openvla/openvla/blob/main/README.md)已明确区分；不能用后续代码接口倒填原始论文。

从 VLM 迁移到 VLA，真正增加的是“观测／指令到动作”的机器人监督。冻结视觉编码器时，动作损失只更新未冻结的投影、骨干或头；解冻后才会把该损失梯度传回视觉层。验收时应分别核对观测预处理、token 排列、mask、动作单位与反归一化，不能只比较网络参数量或文本生成能力。

### 本章实际阅读的一手来源

- [ViT v2](https://arxiv.org/pdf/2010.11929v2)：§3.1，patch 投影与位置编码。
- [Attention Is All You Need v7](https://arxiv.org/pdf/1706.03762v7)：§3.1–3.4，QKV、因果 mask 与 embedding。
- [旋转表示 CVPR 原文](https://openaccess.thecvf.com/content_CVPR_2019/papers/Zhou_On_the_Continuity_of_Rotation_Representations_in_Neural_Networks_CVPR_2019_paper.pdf)：§4.1–4.2，四元数等价及六维正交化。
- [OpenVLA v3](https://arxiv.org/pdf/2406.09246v3)：§3、§6，原始输入输出与监督。
- [OpenVLA 动作 tokenizer](https://github.com/openvla/openvla/blob/main/prismatic/vla/action_tokenizer.py)、[动作恢复代码](https://github.com/openvla/openvla/blob/main/prismatic/models/vlas/openvla.py)、[README](https://github.com/openvla/openvla/blob/main/README.md)：分箱端点、统计键及后续扩展边界。
- [openpi pi0.py](https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/models/pi0.py)：prefix／suffix、本体投影与块注意力；所读为访问日 main，含后续分支，不作为原始论文逐行实现的承诺。
