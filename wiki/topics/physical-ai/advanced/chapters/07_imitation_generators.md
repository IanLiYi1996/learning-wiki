## 07 模仿与生成策略：BC、动作分块、扩散与 Flow Matching

### 07.1 BC 学的是示范分布，不是任务奖励

行为克隆把示范数据中的观测条件 $c_t$ 与动作配对。这里 $c_t=(o_{t-L+1:t},\ell)$，包含长度为 $L$ 的观测窗及可选指令 $\ell$；观测可同时含图像和本体读数，但不能含未来真实观测。单步连续回归与概率策略的基本目标分别是：

$$
\mathcal L_{\rm MSE}=\mathbb E_{\mathcal D}\!\left[\frac1{d_a}\|f_\theta(c_t)-a_t\|_2^2\right],\qquad
\mathcal L_{\rm NLL}=-\mathbb E_{\mathcal D}\log\pi_\theta(a_t\mid c_t).
$$

这里 $\mathcal D$ 是示范分布，$a_t,f_\theta(c_t)\in\mathbb R^{d_a}$，$\theta$ 是策略参数；监督是示范者的动作，而非奖励或策略自己生成的动作。若 $\pi_\theta$ 是均值为 $f_\theta(c_t)$、协方差为固定 $\sigma^2I$ 的高斯，NLL 等于平方误差乘 $1/(2\sigma^2)$ 再加常数；学习方差后还包含对数方差项，不能再说与 MSE 完全相同。动作 token 的 NLL 则是目标整数的交叉熵。两式是本书从监督概率模型写出的基本形式；序列模仿的分布问题见 [DAgger 原文 §2](https://proceedings.mlr.press/v15/ross11a/ross11a.pdf)。

自创反例：同一观测下，示范者以相同概率向左移 $-2$ 或向右移 $+2$，中央区间 $[-0.5,0.5]$ 不可通行。标量预测 $x$ 的期望平方误差为：

$$
\tfrac12(x+2)^2+\tfrac12(x-2)^2=x^2+4.
$$

这里 $x$ 是确定性动作输出，两个示范模式单位相同。最小值在 $x=0$，恰好穿过障碍；预测 $+2$ 的误差更大，却是一条可行路线。这是“低回归损失”和“可执行行为”不一致的构造，不是论文实验。单峰高斯加可学习方差仍可能以零为均值；多峰模型必须采样或选模式，若再对生成样本取均值，会重新制造失败动作。

### 07.2 误差改变下一次输入：covariate shift 与 DAgger

训练集观察来自专家策略诱导的分布 $d_{\pi_E}$，部署却来自学习策略诱导的 $d_{\pi_\theta}$。第一次稍偏的抓取会改变物体位置，下一次图像不再像专家数据；“随机切分示范帧的验证误差很小”没有验证这条反馈链。自创最坏情形：每步在尚未偏离时以概率 $\varepsilon$ 进入一个未见过且无法恢复的区域，之后每步都付单位代价。第 $t$ 步处于偏离区的概率至多为 $t\varepsilon$，求和得到代价上界 $\varepsilon T(T+1)/2$，另受 $T$ 截断。这里 $T$ 是任务步数；这只是说明二次累积的可能性，并非所有 BC 都必然如此。

[DAgger §3、Algorithm 3.1](https://proceedings.mlr.press/v15/ross11a/ross11a.pdf)通过数据聚合改变训练分布。流程是：先用专家示范训练初始策略；每轮在学习策略或专家／学习混合策略下收集访问到的观测；让专家为这些观测标注应采取的动作，把新标签并入全部历史数据，再训练下一轮策略。专家提供的标签不必就是当时执行的动作。若使用混合策略，可逐轮减小专家介入比例，最后在目标部署条件下选取策略。

DAgger 并不是给旧示范多加一个随机增强，也不能保证未覆盖的危险状态安全可访问。专家在偏离状态上是否能给一致标签、是否存在恢复动作、交互代价是否允许，都影响可实施性。本章仅描述算法，任何实际数据收集仍须单独的仿真、安全约束与授权。

### 07.3 chunk：预测窗、执行窗和时延不是一个参数

令策略预测 $A_t=[a_t,\ldots,a_{t+H_a-1}]\in\mathbb R^{H_a\times d_a}$。批训练张量为 $B\times H_a\times d_a$；观测窗长 $L$ 描述过去，$H_a$ 描述未来，执行前缀长度 $H_e\le H_a$ 决定多久重新观察。若输出数组从最早观测时刻对齐，还必须先跳过历史索引，当前动作不一定是数组第零项。[Diffusion Policy §III](https://arxiv.org/pdf/2303.04137v4)区分观察、预测与执行 horizon；其 [图像策略代码](https://github.com/real-stanford/diffusion_policy/blob/main/diffusion_policy/policy/diffusion_unet_image_policy.py)从 `n_obs_steps-1` 取执行段。

chunk 让模型联合学习动作间关联，也把若干决策合并成一次推理，但更长的执行前缀会延迟反馈。自创时序例：控制周期 20 ms，推理耗时 80 ms，$H_a=16$ 覆盖 320 ms，$H_e=4$ 执行 80 ms。即使网络只执行前四步，最后一条指令结束时距用于预测的观测也已约 160 ms；若异步推理，观测到达时还可能有四个旧动作正在执行。队列必须记录时间戳、已执行前缀和新输出应从哪一项接续，不能靠“chunk 很长”自动消除过期。

ACT 是分块策略的一种具体训练法，不是 chunk 的定义。[ACT 原文 §IV、附录 C](https://arxiv.org/pdf/2304.13705v1)训练时用示范动作段和本体观测推断潜变量，再由图像、本体与潜变量预测动作段，以重建损失及到高斯先验的 KL 正则联合训练；推理移除该推断编码器，并取先验均值零。需注意原文 Algorithm 1 写 MSE，§IV-C 与 [作者 policy.py](https://github.com/tonyzhaozh/act/blob/main/policy.py)实际采用 L1 重建，不能把教学 MSE 当作其精确实现。

ACT 的 temporal ensemble 合并的是“不同预测时刻对同一个执行时刻”的动作，不是相邻时刻动作的移动平均。它增加查询频率，可能平滑切换，却也可能把不同模式平均成不可行动作。长度、重预测频率、融合权重和实际时延需要分别验证。

### 07.4 DDPM：先定义噪声过程，再定义学习目标

把归一化的示范动作段展平为 $x^{(0)}\in\mathbb R^{D}$，其中 $D=H_a d_a$。扩散步记作 $k$，不与环境时间 $t$ 混用。DDPM 的前向过程为：

$$
p_{\rm fwd}(x^{(k)}\mid x^{(k-1)})=
\mathcal N\!\left(\sqrt{\alpha_k}x^{(k-1)},\beta_k I\right),\quad
\alpha_k=1-\beta_k,\quad
\bar\alpha_k=\prod_{i=1}^k\alpha_i,
$$

$$
x^{(k)}=\sqrt{\bar\alpha_k}\,x^{(0)}
+\sqrt{1-\bar\alpha_k}\,\epsilon,\qquad
\epsilon\sim\mathcal N(0,I).
$$

这里 $\beta_k\in(0,1)$ 是固定噪声日程，$\alpha_k,\bar\alpha_k$ 是信号保留系数，$I$ 是 $D\times D$ 单位矩阵，$\epsilon$ 是同宽高斯噪声。第二式可由第一式递推：信号系数逐步相乘，独立噪声方差累积为 $1-\bar\alpha_k$，因此训练时无需真的运行前面所有加噪步。[DDPM §2、式 2–4](https://arxiv.org/pdf/2006.11239v2)给出这两个分布；将数据从图像换成动作段，不改变该代数关系。

网络接收带噪段、扩散步嵌入和观测条件，预测加入的噪声：

$$
\mathcal L_\epsilon=
\mathbb E_{\mathcal D,k,\epsilon}
\left[
\frac{\sum_{b,h,j}m_{bhj}
\big(\epsilon_{bhj}-\epsilon_\theta(x^{(k)},k,c)_{bhj}\big)^2}
{\sum_{b,h,j}m_{bhj}}
\right].
$$

这里批张量 $x^{(k)},\epsilon,\epsilon_\theta$ 均为 $B\times H_a\times d_a$；$k$ 通常为每样本随机采样的噪声步，$c$ 含观测窗、有效相机及可选语言；$m\in\{0,1\}^{B\times H_a\times d_a}$ 标记有效动作坐标，假设分母非零。轨迹末端 padding、不同机器人补齐的动作维度不应进入本书此损失。监督 $\epsilon$ 是人工采样并已知的噪声，不是示范中的“动作误差”。[DDPM §3.4、Algorithm 1](https://arxiv.org/pdf/2006.11239v2)说明简化噪声 MSE；它不等同于任意生成模型的精确 NLL。

图像可先编码成特征，与本体历史拼成全局条件，供 U-Net 的条件层使用；也可以作为 Transformer 的条件 token。上述 $m$ 是本书为多形态／可变长度补充的有效性 mask，不声称原始 Diffusion Policy 文件支持它：所读代码直接断言批数据没有 `valid_mask`。该实现另有 `condition_mask` 用于 inpainting，并以其补集计损失；“已知量锁定”与“无效量忽略”必须分开。[官方 compute_loss](https://github.com/real-stanford/diffusion_policy/blob/main/diffusion_policy/policy/diffusion_unet_image_policy.py)可核对条件、目标类型及 reduction。

采样从 $x^{(K)}\sim\mathcal N(0,I)$ 开始，典型固定方差 DDPM 更新为：

$$
x^{(k-1)}=
\frac1{\sqrt{\alpha_k}}
\left(x^{(k)}-\frac{\beta_k}{\sqrt{1-\bar\alpha_k}}
\epsilon_\theta(x^{(k)},k,c)\right)+\sigma_k z_k.
$$

这里 $K$ 是扩散总步数，$z_k\sim\mathcal N(0,I)$ 是每轮新采的噪声，最后一步取零；$\sigma_k^2$ 是选定反向方差，例如前向后验方差 $\beta_k(1-\bar\alpha_{k-1})/(1-\bar\alpha_k)$。它不同于训练用的 $\epsilon$，也不是把观测重新加噪。该更新依据 [DDPM §3.2、Algorithm 2](https://arxiv.org/pdf/2006.11239v2)，近似质量取决于网络与日程。

DDIM 不是“把 DDPM 循环随意少跑几次”。确定性 DDIM 可先由噪声预测估计干净动作，再跳到所选较小噪声索引 $l<k$：

$$
\widehat x^{(0)}=\frac{x^{(k)}-\sqrt{1-\bar\alpha_k}\,\widehat\epsilon}{\sqrt{\bar\alpha_k}},
\qquad
x^{(l)}=\sqrt{\bar\alpha_l}\,\widehat x^{(0)}
+\sqrt{1-\bar\alpha_l}\,\widehat\epsilon.
$$

这里 $\widehat\epsilon=\epsilon_\theta(x^{(k)},k,c)$，其余系数沿用同一训练日程；本式对应随机性参数 $\eta=0$，给定初始噪声后确定性更新。非零 $\eta$ 会引入不同的随机项。DDIM 允许复用相关训练目标，却改变采样路径；推理步数与训练噪声步数不是同一个配置。[DDIM §4.1](https://arxiv.org/pdf/2010.02502v4)说明该区别。

### 07.5 Flow Matching：监督的是生成路径速度

选择最简单的噪声到数据插值，令生成时间 $\tau$ 从零走到一：

$$
x_\tau=(1-\tau)z+\tau x_{\rm data},\qquad
v^\star=x_{\rm data}-z,\qquad
\mathcal L_{\rm FM}=\mathbb E\left[
\frac{\sum m\,(v_\theta(x_\tau,\tau,c)-v^\star)^2}{\sum m}
\right].
$$

这里 $z$ 是与动作段同形状的标准高斯噪声，$x_{\rm data}$ 是归一化示范段，$\tau\in(0,1)$ 随机采样，$v^\star$ 是该插值对 $\tau$ 的导数，$m,c$ 沿用前节，平方和逐坐标计算。给定 $x_{\rm data}$，插值的噪声协方差为 $(1-\tau)^2I$，应从显式采样式计算，不能把噪声标准差当方差。$v^\star$ 的单位是“归一化动作／生成时间”，不是末端物理速度，更不是控制输入 $u_t$。这是 [Flow Matching §3–4](https://arxiv.org/pdf/2210.02747v2)概率路径思想下的简单条件路径；其他插值的速度目标必须重新求导。

推理不再知道 $x_{\rm data}$，而是求解：

$$
\frac{dx_\tau}{d\tau}=v_\theta(x_\tau,\tau,c),\qquad
x_0=z,\qquad
x_{\tau+\Delta\tau}\approx x_\tau+\Delta\tau\,v_\theta(x_\tau,\tau,c).
$$

这里 $x_0$ 是生成起点而不是 DDPM 的干净样本索引，最后一式是显式 Euler 积分，$\Delta\tau>0$。训练只回归随机插值点上的速度，无需对整段 ODE 求解反传；推理才多次求解速度场。平方损失学到的是给定 $(x_\tau,\tau,c)$ 的条件平均速度，不是直接对全部最终动作求均值，因此可输运多峰分布；有限步长仍会引入积分误差。

[π₀ §IV](https://arxiv.org/pdf/2410.24164v4)将视觉语言条件、本体状态和动作专家连接到连续段生成；所读 [openpi compute_loss／sample_actions](https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/models/pi0.py)采用反方向时间：$\tau_{\rm code}=1-\tau$，插值为 $\tau_{\rm code}z+(1-\tau_{\rm code})x_{\rm data}$，目标为 $z-x_{\rm data}$，并以负步长从一积分到零。该关系是变量换元，不是模型预测了相反动作。代码还含后续配置分支，不能把访问日 main 的所有行为归入原始 π₀。

### 07.6 可检查的训练与推理伪代码

下列是本书原创、无硬件调用的算法骨架。`valid_mean` 按有效坐标数平均；无效坐标在输入和输出固定为零。`action_attention_mask` 为 $B\times H_a\times H_a$：有效动作 token 可互相注意，无效 key 屏蔽；动作 token 可读有效观测，观测 prefix 不回读动作。此处采用双向动作段，是示例设计及 π₀ 的配置，不是原始 Diffusion Policy Transformer 的因果配置。已知执行前缀若作为条件，应单独输入 $c$ 并采用匹配训练，不能临时覆盖部分噪声后假定仍是同一算法。

```text
# 训练：batch 动作 [B, Ha, da]；c 只编码过去／当前观测
obs, demo, m = sample_demonstration_windows()
c = encode_obs(obs, observation_valid_mask)
x_data = normalize_and_zero_padding(demo, m)
z = normal_like(x_data) * m
if generator == "DDPM":
    k = random_noise_index_per_sample()
    x = sqrt(abar[k])*x_data + sqrt(1-abar[k])*z
    pred = noise_net(x, embed(k), c, action_attention_mask)
    loss = valid_mean((pred-z)**2, m)
else:  # 噪声到数据的 FM
    tau = random_generation_time_per_sample()
    x = (1-tau)*z + tau*x_data
    pred = velocity_net(x, embed(tau), c, action_attention_mask)
    loss = valid_mean((pred-(x_data-z))**2, m)
backprop_and_update(loss)  # encoder 若未冻结，也接收梯度

# 推理：观测条件在一次生成循环中固定
c = encode_obs(current_history, observation_valid_mask)
x = normal([B, Ha, da]) * m
if generator == "DDPM":
    for k in K, ..., 1:
        eps = noise_net(x, embed(k), c, action_attention_mask)
        x = ddpm_update(x, eps, k, fresh_noise_if_needed()) * m
else:
    for tau in increasing_grid_from_zero_to_one():
        x = (x + delta_tau*velocity_net(x, embed(tau), c,
                                      action_attention_mask)) * m
actions = inverse_normalize(x)
return aligned_execution_prefix(actions, He, timestamps)
```

监督数据、噪声步与环境步必须分别记录。推理返回动作还不是执行命令，应由第 01 章约定的动作适配与控制接口解释。复现应首先做无硬件的形状、mask、单位及时间对齐测试，再讨论闭环表现。

### 本章实际阅读的一手来源

- [DAgger 原文](https://proceedings.mlr.press/v15/ross11a/ross11a.pdf)：§2–3，分布偏移、专家查询与聚合流程。
- [ACT v1](https://arxiv.org/pdf/2304.13705v1)、[作者 policy.py](https://github.com/tonyzhaozh/act/blob/main/policy.py)：§IV、附录 C，CVAE、推理潜变量、L1／MSE 表述差异及 ensemble。
- [Diffusion Policy v4](https://arxiv.org/pdf/2303.04137v4)、[图像 U-Net 策略实现](https://github.com/real-stanford/diffusion_policy/blob/main/diffusion_policy/policy/diffusion_unet_image_policy.py)：§III，条件编码、动作窗口、mask 和噪声目标。
- [DDPM v2](https://arxiv.org/pdf/2006.11239v2)：§2–3、Algorithms 1–2，前向闭式、噪声监督与反向采样。
- [DDIM v4](https://arxiv.org/pdf/2010.02502v4)：§3–4，非马尔可夫构造与确定性跳步采样。
- [Flow Matching v2](https://arxiv.org/pdf/2210.02747v2)：§2–4，条件路径、速度回归及 ODE。
- [π₀ v4](https://arxiv.org/pdf/2410.24164v4)、[openpi pi0.py](https://github.com/Physical-Intelligence/openpi/blob/main/src/openpi/models/pi0.py)：§IV，观测条件、动作专家及代码时间方向；仓库按访问日 main 阅读。
