# 01 扩散模型的 DPO 与偏好数据

读取日：2026-11-03 · [专题](README.md) · [来源与边界](#public-sources)

<a id="diffusion-01"></a>

本章从 Andrei Filatov 的[实践博客](https://anvilarth.github.io/preference-optimization.html)出发，回到论文和作者代码，回答三个问题：DPO 比较什么，扩散模型怎样实现这种比较，什么数据值得比较。公式中的简化数字均为原创教学例子；没有下载权重、训练、调用付费推理或复现性能。博客的经验建议不视为普遍定律。

## 01 偏好标签只说“这次更喜欢谁”

假设提示词是“红杯旁有两枚方糖”。胜者画对数量但纹理普通，败者质感漂亮却多画一枚：选择胜者，可能是在奖励计数，不是在奖励画风。若另一批标注员只看美感，合并标签就可能混合不同目标。偏好数据首先需要共同提示词、明确评判维度，以及可追溯的胜负方向。

Bradley–Terry（BT）假设潜在效用为 $r(c,x)$，选择概率是：

$$
P(x^w\succ x^l\mid c)=\sigma(r(c,x^w)-r(c,x^l)),
\qquad \sigma(u)=\frac1{1+e^{-u}}.
$$

效用相等时概率为一半；差为 $\log3$ 时为四分之三。它允许同一对被不同人选出不同结果，但仍假定用单一效用差解释比较；审美分群、偏好循环未必适合这一模型。标签本身不能证明 BT 成立，更没有给出胜者的绝对质量。[DPO §3](https://arxiv.org/html/2305.18290v3)

## 02 Reference log-ratio：奖励的是相对基线的变化

DPO 从“最大化期望奖励，减去 $\beta D_{\mathrm{KL}}(p\Vert p_{\mathrm{ref}})$”出发。在理想分布空间、$\beta>0$ 及必要支持条件下，最优分布为：

$$
p^*(x\mid c)=\frac{p_{\mathrm{ref}}(x\mid c)e^{r(c,x)/\beta}}{Z(c)}.
$$

取对数，得到 $r=\beta\log(p^*/p_{\mathrm{ref}})+\beta\log Z(c)$。同一提示词的两幅图相减，未知的 $Z(c)$ 消去。于是直接训练：

$$
z=\beta\left[
\log\frac{p_\theta(x^w\mid c)}{p_{\mathrm{ref}}(x^w\mid c)}
-\log\frac{p_\theta(x^l\mid c)}{p_{\mathrm{ref}}(x^l\mid c)}
\right],
\qquad L=-\mathbb E\log\sigma(z).
$$

连续图像空间中的 $p$ 指密度。核心不是“当前模型认为哪幅更常见”，而是“相对 reference，哪幅得到更多提升”。初始化与 reference 相同时，每对 $z=0$，损失为 $\log2$，即使 reference 本来就偏爱某幅图。[DPO §4、附录 A.1–A.2](https://arxiv.org/html/2305.18290v3)

Reference 是冻结的基线，不是审美裁判；$\beta$ 是尺度及正则强度，不是第二个 reference。固定奖励时，大 $\beta$ 的理论最优解更贴近基线；实际优化中，单对导数为 $\partial[-\log\sigma(z)]/\partial(z/\beta)=-\beta\sigma(-z)$，它还影响梯度和饱和。大 $\beta$ 会让正确分开的对更快饱和，却未必减弱错分对的梯度。作者代码将两模型的胜负 log-ratio 相减后才乘 $\beta$；把 $\beta$ 设为零只会消除学习信号，不等于“去掉 reference”。[作者实现 `preference_loss`](https://github.com/eric-mitchell/direct-preference-optimization/blob/f8b8c0f49dc92a430bae41585f9d467d3618fe2f/trainers.py#L70)

冻结只意味着 reference 不更新；它仍通过 $z$ 改变每对的梯度权重。代码的 `reference_free` 是将参考胜负 log-ratio 置零，让参考对两者的基准比值为一，不能与减小 $\beta$ 混用解释。[同一实现 L73–85](https://github.com/eric-mitchell/direct-preference-optimization/blob/f8b8c0f49dc92a430bae41585f9d467d3618fe2f/trainers.py#L73)

## 03 扩散模型为什么转向去噪误差 surrogate

语言模型可累加给定序列的 token 对数概率；扩散图像的边缘密度要积分掉通向它的全部隐含去噪路径，不能直接廉价求出。Diffusion-DPO 将问题扩展到路径分布，利用变分界、Jensen 不等式，并用前向加噪过程近似相关后验；高斯反向转移最终给出可微的平方误差目标。它是 surrogate，不是精确图像似然，也不是“两个 ELBO 下界相减仍自动构成下界”。[Diffusion-DPO §4、补充 S2](https://arxiv.org/html/2311.12908v1)

在噪声预测参数化下，对 $s\in\{w,l\}$：

$$
x_t^s=\alpha_tx_0^s+\sigma_t\epsilon,\qquad
E_\theta^s=\|\epsilon-\epsilon_\theta(x_t^s,t,c)\|_2^2.
$$

每对共享时间步 $t$ 和高斯噪声 $\epsilon$，可训练模型与 reference 又读取同一份 $x_t^s$。这是作者伪代码与发布实现的实际约定：把随机污染条件配齐，避免额外难度差扰乱比较。用共同随机数降低差值方差的直觉依赖正协方差，并非每对必然降方差；而且损失非线性，不能随意互换共享与独立采样后声称估计目标完全相同。[补充 S9](https://arxiv.org/html/2311.12908v1) [训练代码 L1031–1145](https://github.com/SalesforceAIResearch/DiffusionDPO/blob/9bc5f3d5f0f3aa09f384238b73196826e24508eb/train.py#L1031)

论文包含 $T$、时间权重和误差求和；发布代码采用张量平均 MSE，并使用 $-\tfrac12\texttt{beta\_dpo}$ 作系数。因此 $\beta$ 必须连同归一化、时间采样和学习率理解，不能跨实现照搬。该代码还明确断言预测目标为 `epsilon`，不是任意 flow／velocity 模型的即插即用证明。[同一源码 L1105、L1125–1145](https://github.com/SalesforceAIResearch/DiffusionDPO/blob/9bc5f3d5f0f3aa09f384238b73196826e24508eb/train.py#L1105)

## 04 四项误差：相对改善不等于质量改善

<!-- illustration: dif-dpo-four-errors-3ab489409d -->
![四项误差：先对 reference，再比较胜负。噪声预测的简化记号；时间权重、MSE 归一化须与实际实现一起核验。](../images/dif-dpo-four-errors.png)

*图：四项误差：先对 reference，再比较胜负。噪声预测的简化记号；时间权重、MSE 归一化须与实际实现一起核验。*
<!-- /illustration: dif-dpo-four-errors-3ab489409d -->

记 $\delta_s=E_\theta^s-E_{\mathrm{ref}}^s$，把正尺度写作 $b_t=\beta T\omega_t$，则：

$$
z_t=-b_t(\delta_w-\delta_l),\qquad
L_{\mathrm{diff}}=-\mathbb E_{t,\epsilon,\mathrm{pairs}}\log\sigma(z_t).
$$

负号不可省：误差越小越好，而 log-probability 越大越好。胜者相对误差下降，或败者相对误差上升，都能让 $z_t$ 增大。[Diffusion-DPO 式 14](https://arxiv.org/html/2311.12908v1)

原创反例：reference 两项误差都是 $1$，当前变成 $(1.2,1.5)$。取 $b_t=1$，则 $z_t=0.3$，单对损失从 $0.693$ 降到约 $0.554$，但胜者误差也上升了。四项相减不是惩罚模型与 reference 的预测向量距离；它只比较误差变化。共享参数还会使两支梯度互相影响。Diffusion-SDPO 讨论并报告了这种相对目标与绝对误差脱节，不能据此断言所有 DPO 都会崩溃。[Diffusion-SDPO §3](https://arxiv.org/html/2511.03317v2)

## 05 FiFA：pair gap、置信度和多样性不能混为一谈

FiFA 是数据过滤方法，不是新的生成器损失。论文用代理奖励模型计算：

$$
m_i=|r_\phi(c_i,x_i^w)-r_\phi(c_i,x_i^l)|,\qquad
\tilde f_i=m_i+\alpha Q(c_i)+\gamma\log d_k(c_i),
$$

其中 $Q$ 是 LLM 提示词质量分，$d_k$ 是嵌入空间到第 $k$ 个邻居的欧氏距离。完整目标含所选集合的熵；为高效选取，论文改用全体提示词上的固定邻距，排序取前 $K$，不是精确求解集合熵最大化。[FiFA §3、式 4–8](https://arxiv.org/html/2410.10166v2)

Margin 衡量代理评估器的分离程度，不是已校准的人类投票置信度，更不是胜者质量。假设同一评分尺度上，两对分数为 $(3,0)$ 与 $(9,8)$：前者差大，却未必是更好的学习目标。绝对值还隐藏方向：代理与人类强烈意见相反，也能产生大 margin。应单独核查方向冲突，而不是把“大差距”直接译成“标签可信”。代码可选 `use_new_label_0` 按奖励重标方向；那是另一个数据决策。[FiFA 训练预处理](https://github.com/YangYongJin/FiFA-Official-Repo/blob/1249c845e4502ceca3efcb49d2135d533a449b20/train.py#L874)

小 gap 可以来自标注噪声，也可以是两个好样本间有价值的细微偏好。FiFA 的高 margin 策略有其数据与任务依据；其理论解释假设线性奖励及特定噪声，不能推出“小 gap 一律没用”。附录 G 另讨论奖励软标签加权，不要把过滤与置信度加权当成同一操作。[FiFA §3.3、附录 G](https://arxiv.org/html/2410.10166v2)

还要分清数据与训练两种 gap：$m_i$ 来自代理奖励，$z_t$ 来自当前模型相对 reference 的误差变化。初始化时所有 $z_t$ 都为零，并不表示所有数据对都模糊。代码的 `implicit_acc` 只统计 $z_t>0$ 的比例，不是人类偏好胜率；把它当成质量证明，会把优化目标当成了独立验证。[Diffusion-DPO 源码 L1144](https://github.com/SalesforceAIResearch/DiffusionDPO/blob/9bc5f3d5f0f3aa09f384238b73196826e24508eb/train.py#L1144)

质量评分考虑清晰度、可理解性、难度与有害内容，不等于提示词越长越好。邻距项则希望避免大 margin 对全挤在人像等少数主题；但文字多样性不保证图像多样性。发布代码还有重要差异：用平均余弦邻距代替对数欧氏邻距，读取预先归一化的 margin／LLM 分数，并限制同一 caption 的入选数量。代码参数 `beta` 对应论文的 $\gamma$，不是 DPO 的 $\beta$。[FiFA §3.2、附录 C](https://arxiv.org/html/2410.10166v2) [选择源码 L175–283](https://github.com/YangYongJin/FiFA-Official-Repo/blob/1249c845e4502ceca3efcb49d2135d533a449b20/select_data.py#L175)

## 06 Off-policy 可以复用旧对，不等于无视支持与漂移

DPO 可读取预先收集的偏好对，不要求每步由当前 checkpoint 生成；Diffusion-DPO 也给出 off-policy 推导。但“不需要在线 rollout”只说明训练流程，并不保证任何外部图像都同样有效。[DPO §4](https://arxiv.org/html/2305.18290v3) [Diffusion-DPO 补充 S3](https://arxiv.org/html/2311.12908v1)

从理论最优解可直接看出支持边界：有限奖励下，reference 不分配概率质量的区域，$p^*$ 也不会凭重加权分配非零概率质量。连续扩散分布常无这样明显的硬零，但极低密度、有限模型容量仍使外部样本难学。低密度不等于数学上的零支持，也不能因 surrogate 可算就忽略分布漂移。[DPO 附录 A.1](https://arxiv.org/html/2305.18290v3)

工程判断：拿强模型作胜者、弱模型作败者，可能同时传递配色、构图、水印等来源特征。若来源与标签绑定，模型可能学到来源捷径；极端败者也可能与实际错误脱节。应记录生成器、采样设置、标签标准，检查目标域和当前模型常见错误的覆盖。冻结 reference 不能修复缺失数据；原 DPO 在参考生成器不可得时先拟合胜者来缓解漂移，也不是无条件保证。[DPO §4 的数据复用说明](https://arxiv.org/html/2305.18290v3)

## 07 保质量是另一个目标：三道自测

若胜者本身足够好，可以考虑：

$$
L_{\mathrm{joint}}=L_{\mathrm{diff}}+
\lambda\,\mathbb E E_\theta^w,\qquad \lambda>0.
$$

这给出胜者重建的独立压力，但只是软约束：共享梯度、有限步长仍可能让胜者误差上升；重建误差也不等于感知质量。坏胜者会被进一步强化，窄域胜者可能压缩覆盖。博客推荐联合 SFT 可作为实验假设，不能改写成“必能保住生成质量”。[博客第 5 章](https://anvilarth.github.io/preference-optimization.html)

Diffusion-SDPO 进一步按两支梯度关系缩放败者项；其非增保证是一阶近似，输出空间替代又引入估计误差，强曲率和有限步长会削弱保证。[论文 §4.1、§6、附录 A](https://arxiv.org/html/2511.03317v2) 因此评估建议是同时看胜负误差、留出域的人类偏好、对象正确性和多样性，不只看训练 loss 或筛选时同一代理模型的分数。本次未执行这些评测。

1. Reference 已更偏爱胜者，当前模型与它完全相同，$z$ 是否为正？答：不是，两个 log-ratio 都为零；DPO 衡量相对变化，不奖励既有偏爱。
2. 若 $\delta_w=-0.2,\delta_l=0.1,b_t=2$，$z_t$ 是多少？改成 $\delta_w=0.2,\delta_l=0.5$ 呢？答：都是 $0.6$，损失都约 $0.437$；第二组胜者变差，证明同一偏好损失不能区分绝对质量走向。
3. 应只保留最大 gap 的一千个人像对吗？答：不能仅凭 gap 决定；还要查方向一致性、胜者质量、评估器校准和域覆盖。若直接运行 FiFA 选择脚本，还须提供预计算分数，并理解其 `beta` 是多样性权重。

<a id="public-sources"></a>

## 08 来源、版本与实际读取范围

下表 URL 指向实际核验资料；论文读取的是公开 HTML，不声称逐页读完 PDF。代码固定到 commit；仓库建立日不等于正式版本发布日期。没有独立验证论文 benchmark，也不将所报告的节省比例推广到其他模型。

| 标题／作者 | URL | 读取日 | 原发布日期／读取版本 | 实际读到的范围 | 适用边界 |
| --- | --- | --- | --- | --- | --- |
| Direct Preference Optimization (DPO) for Diffusion Models／Filatov | [博客](https://anvilarth.github.io/preference-optimization.html) | 2026-11-03 | 2026-10-11；当日页面 | 六章文字与 Sources 链接；未逐图复核 | 实践意见及引用入口，不是通用定理 |
| Direct Preference Optimization: Your Language Model is Secretly a Reward Model／Rafailov 等 | [arXiv HTML](https://arxiv.org/html/2305.18290v3) | 2026-11-03 | v1：2023-05-29；读 v3：2024-07-29 | §3–4，附录 A.1–A.2 | BT、支持与理想分布假设下的推导 |
| DPO 作者参考实现／Eric Mitchell | [trainers.py](https://github.com/eric-mitchell/direct-preference-optimization/blob/f8b8c0f49dc92a430bae41585f9d467d3618fe2f/trainers.py) | 2026-11-03 | 建立：2023-06-22；`f8b8c0f`：2023-12-14 | README、损失与 log-probability 计算，L45–115 | 语言模型实现；未运行训练 |
| Diffusion Model Alignment Using Direct Preference Optimization／Wallace 等 | [arXiv HTML](https://arxiv.org/html/2311.12908v1) | 2026-11-03 | v1：2023-11-21 | 背景式 3–8、§4、S2、S3 相关推导、S9 | 路径界与近似目标；非精确边缘似然 |
| Diffusion-DPO 作者实现／Salesforce AI Research | [train.py](https://github.com/SalesforceAIResearch/DiffusionDPO/blob/9bc5f3d5f0f3aa09f384238b73196826e24508eb/train.py) | 2026-11-03 | 建立：2023-12-27；`9bc5f3d`：2026-06-02 | README；冻结 L583–601；加噪、损失 L1031–1145 | 默认 epsilon 路径；未审计全部实验及可选扰动 |
| Automated Filtering of Human Feedback Data for Aligning Text-to-Image Diffusion Models／Yang 等（FiFA） | [arXiv HTML](https://arxiv.org/html/2410.10166v2) | 2026-11-03 | v1：2024-10-14；读 v2：2025-04-02 | §3、§4.1、附录 A、C 说明、G | 过滤策略与限定理论；未转录模板图或复现实验 |
| FiFA 作者实现／Yongjin Yang | [select_data.py](https://github.com/YangYongJin/FiFA-Official-Repo/blob/1249c845e4502ceca3efcb49d2135d533a449b20/select_data.py)、[train.py](https://github.com/YangYongJin/FiFA-Official-Repo/blob/1249c845e4502ceca3efcb49d2135d533a449b20/train.py) | 2026-11-03 | 建立：2025-04-02；`1249c84`：2025-06-25 | README、选择脚本全文；训练的重标与软标签相关片段 | 与论文距离公式有差异；依赖预计算分数；未执行 |
| Diffusion-SDPO: Safeguarded Direct Preference Optimization for Diffusion Models／Fu 等 | [arXiv HTML](https://arxiv.org/html/2511.03317v2) | 2026-11-03 | v1：2025-11-05；读 v2：2025-12-02 | §3 局限、§4.1、§6、附录 A 二阶讨论 | 保证仅到一阶；未核验其性能复现 |

访问限制：FiFA 论文及 README 指向的[项目页](https://sprain02.github.io/FiFA/)当日直接请求返回 HTTP 404，未作为内容依据。博客其他引用未作本章论证依据。
