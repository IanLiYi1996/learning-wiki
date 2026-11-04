# 后训练与强化学习：按什么轨迹、奖励和概率更新

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

后训练遇到的困难不只是奖励够不够好。扩散模型同时生成多个位置，交互规划模型则在动作之间接收环境观察。
两者都需要回答：训练时重建的条件状态，是否真是采样时模型看到的状态？代码计算的概率，是否对应实际提交的输出？
DiRL／DiPO处理扩散轨迹重放；BandPO调整概率更新区间；Planner-R1让任务规划器从环境完成反馈中学习。[P5]、[P6]、[P7]

这里讨论数学解题和任务规划的能力训练，不把RL与安全对齐混为一谈。完成奖励、参考模型KL或数学正确率，都不能直接作为拒答、诚实或物理安全的证据。
外部基座也须单列：DiRL从SDAR-8B-Chat继续训练，Planner-R1使用Qwen2.5-7B-Instruct；BandPO实验的Qwen及DeepSeek蒸馏权重也来自外部。团队贡献是这里的算法、训练框架及后训练结果。[DR]、[ER]、[P6] §6.1

| 工作 | 训练信号和更新对象 | 阅读时需要分开的量 |
|---|---|---|
| DiRL／DiPO | 数学任务反馈；真实生成状态下的模型概率 | 状态logits、采样概率、最终文本概率 |
| BandPO | 数学RLVR；旧概率相关的ratio边界 | 标量边界的理论性质、完整策略更新效果 |
| Embodied-Planner-R1 | 环境完成反馈；多轮Thought／Action轨迹 | 训练二值奖励、评测分数、真实机器人能力 |

遮盖生成和推理缓存见[扩散语言模型专题][T13]，任务执行、世界反馈及ETA的经验验证见[世界建模与具身规划专题][T05]。运行时契约与候选经验验收，和这里改变模型参数的RL不是同一过程。

## 1．DiRL：先把生成状态重建正确

### 1.1 为什么随机mask不能替代真实rollout？

SDAR采用块间因果、块内双向的生成结构。当前块内可以并行预测，之前完成的块提供历史条件。
SFT以随机mask构造训练样本；RL却要计算实际rollout中选中token的概率。任意重新遮盖最终答案，会改变可见信息，不能保证得到原决策状态的logits。[P5] §2–3、[DR]

例如，两个位置在同一步提交。它们预测时看到的是同一个部分遮盖状态，彼此都还不是已知答案。
把第二个位置当成AR token，条件改成“已经看到第一个位置的答案”，会改变概率。即使最终文本完全相同，训练事件也不同。

DiRL记录每个token首次提交的 `step_map`。对每个块，重放某一步时遮盖该步及未来步的位置，只对该步新提交的token计loss。
`generate_training_samples_for_one` 用最小正step构造 `p_mask`，用大于等于该step的条件构造 `masked_indices`；二者分别对应本步目标与本步未知位置。[C5a]

随后 `prepare_for_bd_training` 组织noisy／clean副本，并用FlexAttention的块mask并行处理不同块。
这让训练能重建条件状态，也减少逐块前向的开销；它没有把双向块内生成改写成从左到右的teacher forcing。[C5b]、[P5] §4.1

### 1.2 SFT与RL分别做什么？

论文SFT使用从GLM-4.6蒸馏的OpenR1-Math轨迹，最长8K；8×H200、全局batch 512、学习率 $10^{-5}$，训练100步。
RL阶段使用Big-Math，在SDAR后训练权重上继续更新；论文报告128×H200、128道题／batch、每题32条轨迹、学习率 $10^{-6}$，训练40步。[P5] §3

工程循环如下。它描述数据和参数怎样流动，不是无偏性的证明。

1. LMDeploy用当前行为策略生成答案，并返回真实step map。
2. 计算奖励及组内advantage；DAPO式动态采样排除全对或全错的组。
3. 重建各生成步的状态，计算目标token概率及可选参考模型KL。
4. 根据clipped surrogate更新参数，在线同步推理服务器，开始下一轮rollout。[P5] §3–4、[C5g]

公开 `rl.yaml` 不等于论文实验清单：它设置每题8条轨迹、block size=4、动态阈值0.9、top-k=50。
这些值可用来理解发布代码，不能反填为正文每题32条轨迹的设置；两者与论文检查点的逐项对应尚未确认。[C5e]

## 2．DiPO：条件概率和“无偏”指向哪个对象？

### 2.1 从AR token改为生成步状态

记 $s_{it}$ 为第 $i$ 条轨迹在第 $t$ 步之前的完整遮盖状态，$S_{it}$ 为本步提交位置，$T_i$ 为步数。
AR GRPO使用 $p_\theta(y_k\mid Q,y_{<k})$；DiPO重放所计算的是 $p_\theta(y_j\mid s_{it})$。状态中仍保留尚未提交的位置。[P5] 式(4)–(8)、[C5a]

仅在外生固定step map、给定状态下独立采样的简化模型中，轨迹log-likelihood可写成：

$$
\log\pi_\theta(\tau\mid Q,S)=\sum_t\sum_{j\in S_t}\log p_\theta(y_j\mid s_t).
$$

这个式子不是论文对所有置信度解码器给出的无偏定理。真实提交位置依赖模型及候选token，条件于选中集合后的分布未必仍是原独立采样分布。
最终文本概率还需要处理多条生成轨迹通向同一文本的情况；DiRL正文没有给出该边缘化计算。[P5] §3.2

### 2.2 正文式(6)、(7)、(8)与源码的差别

正文式(6)在每条轨迹内，按生成步遍历本步token，计算新旧条件概率ratio，再逐token clipping，并加参考模型KL。
式(7)换成全组步数归一化，并用当前概率的stop-gradient作为分母。压缩写为：

$$
J_7=\mathbb E_{Q,\tau_{1:G}\sim\pi_{\rm old}}
\left[\frac{\sum_{i,t}\sum_{j\in S_{it}}
C_\epsilon\!\left(p_\theta(y_j\mid s_{it})/
\operatorname{sg}[p_\theta(y_j\mid s_{it})],A_i\right)}
{\sum_iT_i}-\beta\,{\rm KL}\right],
\quad C_\epsilon(r,A)=\min(rA,\operatorname{clip}(r,1-\epsilon,1+\epsilon)A).
$$

式(6)的逐轨迹归一化与式(7)的全组归一化，也不能在轨迹长度不同的情况下视作同一权重。
正文式(8)又去掉内层token求和和KL，ratio写成：

$$
\frac{\pi_\theta(\tau_i(t)\mid\tau_i(<t))}
{\operatorname{sg}[\pi_\theta(\tau_i(t)\mid\tau_i(<t))]}.
$$

按 $\tau_i(t)$ 为本步提交token集合的定义，这是step对象的概率写法。正文没有交代它与逐token clipping的等价条件。
固定提交的 `SDARForCausalLM.forward` 则明确逐token gather全词表log-softmax、逐tokenexp／clip，再求和，未先合成step联合ratio。[P5] 式(6)–(8)、[C5]

一个小例子就能区分：advantage=1，两个token ratio均为1.15，按正文的对称上界1.2计算，逐token平均surrogate为1.15；联合ratio为1.3225，裁剪后为1.2。
该反例说明离策略更新时不能交换“联合概率”与“逐token裁剪”；它不是实现默认参数的实测。实现上界是 $1+\epsilon+0.08$，配置 $\epsilon=0.20$ 时为1.28。[C5]、[C5e]

detach分母让前向ratio等于1，梯度仍沿分子回传log-prob梯度，并非零。
它适合行为策略与重放前策略同步的在线一阶更新；多轮或小批更新时，代码另算旧log-prob，而不是始终用当前值detach。[C5c]

### 2.3 top-k=50：精确logits还不是精确采样概率

默认配置的top-k=50实际传给了服务器。采样器先过滤top-k，再softmax；训练端却对全词表logits做log-softmax。[C5e]、[C5i]、[C5d]、[C5]
固定候选集合 $K$ 时，服务中的采样概率是：

$$
p_{\rm sample}(y\mid s)
=\frac{p_\theta(y\mid s)}{Z_K(s)},\quad
Z_K(s)=\sum_{v\in K}p_\theta(v\mid s),\quad y\in K.
$$

全词表概率少了这个归一化因子。动态unmask又根据候选token的概率选择提交位置，`low_confidence_dynamic` 还强制每块至少提交最高分候选。[C5f]
因此，重放出模型原始logits，并不自动等于重建完整sampler的提交事件概率。论文实验是否另行关闭这些变换，未知。

`shrink!=1` 分支会把块内全部正step合并成最小正值，也会改变重放条件；默认值1避开该变换。[C5h]、[C5e]
核验时应固定同一文本与参数，分别比较真实map、打乱map和合并map的可见状态；采样端还需单独比较截断前后的归一化概率。

### 2.4 “无偏”具体针对什么？

最稳妥的解释是：给定真实轨迹状态，重放得到该状态下的模型logits，不再以随机mask／去噪时间采样去近似另一种似然。
这里的logits是确定值，“无偏”首先指避免条件状态错配，不是对最终文本概率完成了精确积分。[P5] Introduction、§3.2

对任务 $Q$ 和旧策略轨迹的抽样，可以估计一个明确指定的clipped surrogate期望。
若要声称最终文本期望奖励梯度无偏，还必须处理提交集合、top-k归一化、clip、组内标准化、长度权重及过滤后的抽样测度。正文没有覆盖这些步骤的无偏梯度定理。
这一限制不否定框架的速度或数学分数收益；它限定了论文术语能支持到哪里。

## 3．DiRL实验：训练速度、解码速度和质量分别看

| 设置与出处 | 作者报告 | 读数边界 |
|---|---|---|
| DiRL／TraceRL训练循环；8×H200、batch 4、输入1024、输出8192 [P5] §4.3 | FlexAttention训练阶段约6×加速；总循环吞吐约2.5× | 不是128卡RL任务的统一加速倍数，也不是采样无偏证明 |
| SDAR-8B-Chat→DiRL静态；表1 [P5] | 五任务均分42.2→54.0；平均输出长度890.4→3556.4 | SFT／RL贡献未拆分，输出明显变长，缺少等生成长度的比较 |
| DiRL静态→动态0.9；表1 [P5] | 均分54.0→52.8；平均每步token 1→1.8 | 每步并行度不是墙钟TPS |
| 同一动态对照，MATH500 [P5] | 准确率85.1→83.1；每步token 1→2.0 | 加快提交伴随质量下降 |
| 同一动态对照，AIME2025 [P5] | 准确率22.9→20.8；每步token 1→1.7 | 不能写成无损并行解码 |

表1的静态／动态结果应分行保存。README的83.05、20.63、20.83等摘要数字接近动态设置，不能与正文静态行拼成一组“最佳模型成绩”。[DR]、[P5] 表1
动态阈值扫描提示速度与质量可调，但现有结果没有分离SFT、RL与实际生成长度变化的贡献。生成得更长，也不等于实验调整了推理长度上限。

## 4．BandPO：低概率token为什么容易过早被裁剪？

正advantage的token，旧概率为 $p$。固定ratio上界 $1+\epsilon$ 对应的绝对概率增量只有 $\epsilon p$。
当 $p$ 很小时，这个增量也很小。BandPO把旧策略周围的f-divergence trust region投影为依赖该token旧概率的ratio区间。[P6] §4–5

设目标token的新旧概率比为 $r$，其余token在极值解中同比例缩放。论文的标量化函数是：

$$
c=\frac{1-rp}{1-p},\qquad g_f(p,r)=p f(r)+(1-p)f(c).
$$

在相应凸性、支持集条件下，求解 $g_f(p,r)\le\delta$ 得到目标token可行ratio上下界；KL实例数值求解，TV及Pearson $\chi^2$ 有闭式形式。
这里的全局最优是边界投影问题的性质，不是整个神经网络RL训练的全局最优保证。[P6] 式(10)–(15)

TV对应的区间为：

$$
r_{\min}=\max(0,1-\delta/p),\qquad
r_{\max}=\min(1/p,1+\delta/p).
$$

例如 $p=0.01,\epsilon=0.2$，固定clip允许增加0.002；TV半径 $\delta=0.05$ 的核心上界为6，允许增加0.05。
这只是标量映射的计算例，不是该token在训练中一定增加多少的预测。对应源码为 `_solve_bandtv_analytical`。[C6]

完整实现还做极端概率处理、高概率区间松弛及最大ratio兜底；这些启发式应与核心trust-region公式分开。[C6a]
逐坐标可行区间也不等于完整新分布满足同一散度约束。TV例中，$P=(.25,.25,.25,.25)$、$Q=(.30,.30,.20,.20)$ 的每项均在半径0.05对应的坐标区间内，但整体TV为0.10。
这个反例提醒我们：投影区间给的是单坐标约束，clipped surrogate不是完整策略的硬投影。BandPO也不修复DiPO的状态或sampler概率错配。

### 数学RLVR的收益与反效果

| 冻结比较／[P6] 表1 | mean@32／pass@32或指定单项 |
|---|---|
| Qwen2.5-3B，800步；GRPO | 三任务平均17.57／32.60 |
| 同基座同预算；Clip-Higher | 20.47／40.60 |
| 同基座同预算；BandKL，δ=0.05 | 22.00／42.01 |
| DeepSeek-R1-Distill-Qwen-7B，500步；GRPO→BandKL 0.05 | 平均49.04／66.78→51.44／67.12 |
| 同一7B，AIME2025，BandKL δ=0.03→0.05 | pass@32 61.46→57.21；放宽半径并非单项全赢 |

这些实验用8×H200、三个重复，训练数据为DAPO与MATH Levels 3–5的组合。[P6] §6.1
mean@32与pass@32分别涉及32次采样的平均正确和至少一次命中，不能当作单次确定性正确率。
论文的数值求解加速属于边界计算工程；本文没有独立测量其吞吐，也不把数学分数推广为工具行为或安全收益。

## 5．Embodied-Planner-R1：让规划器从动作后果中学习

### 5.1 动机与任务定义

在部分可观测环境中，指令本身不能决定完整动作序列：找不到物体、动作无效或状态变化后，规划器需要用新观察修正下一步。
ReAct提供Thought／Action／Observation的交互格式；Planner-R1进一步利用在线任务结果更新策略，减少只模仿固定专家轨迹的依赖。[P7] §1–3

环境通过状态转移 $\Psi$ 执行动作，再返回观察 $o_{t+1}$。模型每轮输出 $m_t=(\phi_t,a_t)$，只有解析出的动作 $a_t$ 送入环境。
同一个任务—环境对复制多份，用冻结的行为策略探索到完成、主动done或步数上限，再收集完整轨迹。[P7] §2–3、附录A

基座是外部Qwen2.5-7B-Instruct，训练框架基于verl，评测框架改自MINT。不能把任务规划后的权重称为团队从头预训练的基础模型。[ER]
“不依赖专家示范作为核心奖励信号”也不等于没有人为先验：指令模型、系统prompt、动作API和目标判定都已预先定义。

### 5.2 二值完成奖励与IPO

正文采用完成驱动奖励，不另加格式奖励、长度惩罚或逐步手工shaping：

$$
r_i=\begin{cases}
1,&\text{环境任务完成},\\
0,&\text{任务未完成}.
\end{cases}
\qquad
\hat A_{i,t}=\frac{r_i-\mu_r}{\sigma_r}.
$$

同组轨迹提供相对基线，同一条轨迹的终局advantage分配给各交互步。它降低了对过程标注的需求，却没有识别每一步的独立因果贡献。
全失败组仍没有正向完成信号；格式必须可解析、动作必须被环境接受，才能到达成功状态。[P7] §3.4–3.5

论文式(6)的交互步ratio为：

$$
Pr_t(\theta)=
\frac{\pi_\theta(\phi_t,a_t\mid\tau_{i,<t})}
{\pi_{\theta_{\rm old}}(\phi_t,a_t\mid\tau_{i,<t})}.
$$

IPO式(7)对轨迹内各步作clipped surrogate平均，并加参考模型KL；模型生成Thought和Action，外部Observation只提供条件。[P7]
这与DiPO的“生成步”含义不同：这里一步是一次环境动作和随后反馈，那里一步是一个块内去噪提交。

实现仍沿用 `grpo` 配置和函数名。`compute_grpo_outcome_advantage` 用终局分数计算组均值、标准差，分母加 $10^{-6}$，再广播到有效生成token。[C7a]
多轮actor用 `input_mask` 计loss，rollout对环境观察置0、模型输出置1；外部观察不是要模仿生成的目标。[C7b]、[C7c]
`compute_policy_loss` 实际逐token计算ratio与clipping，不能仅凭IPO的交互步公式断言实现先构造整轮联合概率。[C7d]

奖励路径也需要核对。rollout根据环境返回状态设置completed，并由宿主追加SUCCESS；`AlfRewardManager`读取成功结束标记，给最终有效位置0/1奖励。[C7c]、[C7e]
模型自行输出done主要表示终止探索，不自动等于任务完成。代码中失败结束分支、completed分支与评分字段，都是奖励验证的一部分。
这种设计减少了过程奖励定义，但正文关于降低reward hacking的动机不是“不可能骗奖”的证明。

### 5.3 验证设置与成绩

论文训练设置为8×A100 80GB、上下文4096、每步128个任务、每任务5条轨迹，最多30次交互。
公开ScienceWorld easy脚本却设 `train_batch_size=64`，仍为每任务5条；复现不能把两者当成同一冻结配方。[P7] §4.1、[C7f]

| 作者自实现对照；[P7] 表1 | ALFWorld Seen／Unseen／Avg. | ScienceWorld Seen／Unseen／Avg. |
|---|---|---|
| Qwen2.5-7B-Instruct＋ReAct | 30.00／32.09／31.05 | 28.01／16.09／22.05 |
| 同基座＋SFT | 80.71／79.10／79.91 | 68.81／55.70／62.26 |
| 同基座＋ETO | 84.29／79.85／82.07 | 55.08／57.32／56.20 |
| 同基座＋Planner-R1 | 99.29／96.27／97.78 | 83.66／76.18／79.92 |

表中保存作者报告口径，未混入论文标为“Not Directly Comparable”的外部成绩。每任务评测一次、最多30步；单次轨迹结果不提供采样方差估计。[P7] §4.1
ScienceWorld主实验开启全部五项simplification，包括瞬移、预开容器和自动浇水等，考察偏高层规划的文字交互。
“Normal”模式保留更多操作机制，图6中达到约0.6训练奖励需约100训练步，Easy约50步；这是环境难度对学习速度的影响，不是服务器TPS。[P7] §4.3、附录B

训练曲线还报告ScienceWorld响应长度约900→500 token，总动作数约20→12.5，无效动作到约50训练步后接近零。
这些量可解释规划效率，但响应更短、无效动作更少与终局任务分数仍需分别看；它们不能替代未见环境评测。[P7] 图5及§4.3

ScienceWorld指标还有一处实现限制：评测wrapper将 `info['raw_score']` 的最大值保留为reward，另设success字段；训练端则是二值成功标记。[C7g]
因此本文把79.92保留为作者表列分数，不直接改称“79.92%的任务完全成功”。完整聚合脚本与论文原始日志的对应仍未核定。
摘要的泛化下降值与正文表2的平均差也不同：摘要写−3.66，表2写−3.33；不选择其中一个当作跨环境通用指标。[P7] Abstract、表2

### 5.4 为什么这仍是纯文字任务规划RL？

ALFWorld和ScienceWorld通过文本观察及离散指令交互。论文没有训练视觉定位、接触控制、连续运动或实机闭环，并在Limitations明确把视觉扩展留待以后。[P7] 附录F
仿真内部有状态与物理规则，不等于模型学到了可调用的显式动力学世界模型；成功Thought文本也不证明内部因果机制已经被辨认。
与[世界建模与具身规划专题][T05]的世界—动作耦合和宿主执行验证相比，这里的明确证据是：外部文字环境给反馈，参数经交互RL更新，作者报告了冻结基座下的规划分数提升。

## 6．复现时先核对什么？

DiPO先核对真实step状态、采样归一化及token／step损失；BandPO核对核心边界与后处理开关；Planner-R1核对环境完成条件、简化设置与评分聚合。
这些检查分别对应条件事件、更新幅度和奖励来源，不能用“RL有效”一项总分覆盖。
## 固定提交与官方资料

材料核查于 2026-10-17。实验数字为作者报告，概率推导与反例为本文分析；未运行 GPU 训练。发布源码与论文检查点的逐项对应尚未确认，Planner-R1 的结果也不包含实机验证。

| 仓库／完整SHA | 主要定位 |
|---|---|
| DiRL `a9e28f708f06` | [状态样本645–705][C5a]；[训练准备1059–1130][C5b]；[loss 1230–1264][C5]；[旧概率1290–1305][C5c] |
| 同一DiRL提交 | [采样241–269][C5d]；[配置29–67][C5e]；[动态提交53–69][C5f]；[组过滤522–536][C5g]；[shrink 729–753][C5h] |
| BandPO `0de49cd919b4` | [TV映射50–58][C6]；[band后处理128–154][C6a] |
| Embodied-Planner-R1 `50cb93cfc027` | [advantage 111–156][C7a]；[actor 568–574][C7b]；[rollout 342–385][C7c]；[policy loss 274–305][C7d] |
| 同一Planner-R1提交 | [奖励20–27][C7e]；[easy脚本6–37][C7f]；[ScienceWorld评测64–100][C7g] |

[P5]: https://arxiv.org/pdf/2512.22234v2 "DiRL正文与附录"
[P6]: https://arxiv.org/pdf/2603.04918v1 "BandPO正文与附录"
[P7]: https://arxiv.org/html/2506.23127v1 "Planner-R1官方全文；本次核验版本"
[DR]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/README.md
[ER]: https://github.com/OpenMOSS/Embodied-Planner-R1/blob/50cb93cfc02725a1864edc39c0a2170ab233ba61/README.md
[C5]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/models/sdar/modeling_sdar.py#L1230-L1264
[C5a]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/train/dapo.py#L645-L705
[C5b]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/models/sdar/modeling_sdar.py#L1059-L1130
[C5c]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/train/dapo.py#L1290-L1305
[C5d]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/lmdeploy/pytorch/engine/logits_process.py#L241-L269
[C5e]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/configs/rl.yaml#L29-L67
[C5f]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/lmdeploy/pytorch/strategies/dllm/unmasking.py#L53-L69
[C5g]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/train/rollout_dapo_server.py#L522-L536
[C5h]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/train/dapo.py#L729-L753
[C5i]: https://github.com/OpenMOSS/DiRL/blob/a9e28f708f06f4fc0d98b23d57fa152e9ad99447/train/rollout_dapo_server.py#L151-L158
[C6]: https://github.com/OpenMOSS/BandPO/blob/0de49cd919b4ddf3e161fbdf69abcf0527c79ac2/RLtraining/verl/verl/bandpo/band/band.py#L50-L58
[C6a]: https://github.com/OpenMOSS/BandPO/blob/0de49cd919b4ddf3e161fbdf69abcf0527c79ac2/RLtraining/verl/verl/bandpo/band/band.py#L128-L154
[C7a]: https://github.com/OpenMOSS/Embodied-Planner-R1/blob/50cb93cfc02725a1864edc39c0a2170ab233ba61/verl/trainer/ppo/core_algos.py#L111-L156
[C7b]: https://github.com/OpenMOSS/Embodied-Planner-R1/blob/50cb93cfc02725a1864edc39c0a2170ab233ba61/verl/workers/actor/dp_actor.py#L568-L574
[C7c]: https://github.com/OpenMOSS/Embodied-Planner-R1/blob/50cb93cfc02725a1864edc39c0a2170ab233ba61/verl/workers/rollout/vllm_rollout/sci_rollout.py#L342-L385
[C7d]: https://github.com/OpenMOSS/Embodied-Planner-R1/blob/50cb93cfc02725a1864edc39c0a2170ab233ba61/verl/trainer/ppo/core_algos.py#L274-L305
[C7e]: https://github.com/OpenMOSS/Embodied-Planner-R1/blob/50cb93cfc02725a1864edc39c0a2170ab233ba61/verl/workers/reward_manager/alf.py#L20-L27
[C7f]: https://github.com/OpenMOSS/Embodied-Planner-R1/blob/50cb93cfc02725a1864edc39c0a2170ab233ba61/examples/grpo_trainer/sci_easy.sh#L6-L37
[C7g]: https://github.com/OpenMOSS/Embodied-Planner-R1/blob/50cb93cfc02725a1864edc39c0a2170ab233ba61/verl/eval_agent/envs/sciworld_env.py#L64-L100
[T05]: 05-world-action-and-embodied-agent.md
[T13]: 13-diffusion-language-models.md
