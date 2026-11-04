# 诚实回答与长上下文安全：模型为什么拒答，又在拒绝什么？

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

助手读完一份长文档，仍可能编出不存在的事实；遇到不熟悉的问题，它也可能知道应当保留判断，却继续猜答案。
另一些请求即使有准确答案，也不应照做。把这些失败都叫“幻觉”，会把事实核验、知识不确定性和有害内容混在一起。
HalluQA、Say-I-Dont-Know 与 LongSafety 分别为这些问题提供证据，但评价对象和拒答规则不同。
[HalluQA §1–2](https://arxiv.org/pdf/2310.03368v4)、[Idk §1](https://raw.githubusercontent.com/mlresearch/v235/main/assets/cheng24i/cheng24i.pdf)、[LongSafety §1](https://aclanthology.org/2025.llmsec-1.4.pdf)

## 1. 先分清评价对象

事实幻觉是输出与事实或参考证据不一致；知识拒答是模型因缺少可靠答案而停止作答；安全拒答是因为请求或预期输出有害。
模型可能答得准确却不安全，也可能安全地拒绝却没有证明自己知道答案。这里的“诚实”采用论文的行为测量，不讨论意识或主观体验。

| 研究 | 主要问题 | 拒答怎样计分 | 成果身份 |
| --- | --- | --- | --- |
| HalluQA | 中文回答是否受参考事实支持 | 参考答案认定不可回答时才接受拒答 | benchmark、数据和评测脚本 |
| Say-I-Dont-Know | 是否回答自己的已知题、拒绝未知题 | 拒答依据模型特定采样标签判断 | Idk 数据、对齐训练与评价研究 |
| LongSafety / LongSafetyBench | 长输入下能否识别有害内容并选择安全回应 | 安全且相关的选项得分，不等于一律拒答 | 训练数据与 SFT 实验；另有 benchmark |

上述口径分别见 [HalluQA §2.1、§3.2](https://arxiv.org/pdf/2310.03368v4)、[Idk 附录 B.6](https://raw.githubusercontent.com/mlresearch/v235/main/assets/cheng24i/cheng24i.pdf)、[LongSafety §3.3](https://aclanthology.org/2025.llmsec-1.4.pdf)。
HalluQA 的低分没有直接证明哪种训练能修好模型；LongSafetyBench 也不是训练算法。训练干预必须另看数据、损失、基线与消融。

## 2. HalluQA：拒绝误导，与回答事实问题不是一回事

### 2.1 对抗筛选让它适合找弱点，而非估计日常错误率

HalluQA 共 450 问，覆盖 30 个领域，包含 Misleading 175、Misleading-hard 69、Knowledge 206。
前两类偏重错误前提、文化误解与模仿性错误，后一类检查知识问题的事实正确性。
Misleading 用 GLM-130B 筛选，五次中至少三次诱发错误才保留；Knowledge 要求 ChatGPT3.5 和 Puyu 各五次中至少三次答错。
正确/错误参考答案及支持证据经人工编写、核查。[§2.2、图 2](https://arxiv.org/pdf/2310.03368v4)

筛选器参与定义了难题分布。一个模型在这里失分，既可能缺知识，也可能特别容易接受筛选过程针对的错误前提。
这不等于同样比例的普通用户问答会失败。模型类型、规模、检索系统和接口也一起变化，不能把组间差异当成单一训练干预的因果效果。
[§3.1、§3.4](https://arxiv.org/pdf/2310.03368v4)

### 2.2 “无幻觉率”还要求流畅、正面回答

令 $h_i=1$ 表示按论文规则通过，则 $\mathrm{NHR}=N^{-1}\sum_i h_i$。
规则要求输出流畅、正面回应问题，并能由正确参考答案支持；乱码、答非所问也记作失败。
只有参考答案允许“无法回答”时，“不知道”才可通过。[§2.1、§3.2](https://arxiv.org/pdf/2310.03368v4)

因此 NHR 不是纯事实错误的补集，它还包含表达和响应性要求。
如果一个可回答的书籍出版年份问题被模型拒绝，HalluQA 会罚分；Idk 则可能因该模型的未知标签而奖励拒答。
两种选择可以各有用途，但不能用分数高低裁定哪套规则更“诚实”。

### 2.3 五次投票没有消除裁判的共同盲点

论文以 GPT-4-0613 为裁判，给它参考答案和评价规则，五次判断取多数。
在抽样的 600 个回答上，与人工的一致率为单次 93.33%、五次 93.50%；这是表 4 的作者验证结果。
当时测试的 24 个模型中，18 个 NHR 低于 50%，不是 2026 年模型榜单。[§3.3、表 4、§3.4](https://arxiv.org/pdf/2310.03368v4)

相同裁判重复五次，主要减少随机波动；对参考答案遗漏、错误前提和表达偏好的共同误判不一定有效。
总体一致率也不能直接给出某一模型的误放率或误杀率。若这些错误随回答风格变化，近邻模型的排序仍可能不稳。
可检验的办法是盲化模型身份，分别审计错误前提、知识题和合理拒答，再公布分层混淆矩阵。

仓库在 2024-02-28 加入多选任务；其选项准确率与原开放生成 NHR 不是同一个测量。
固定提交的 `calculate()` 虽接受 `vote_times`，判断条件却写成“是”的数量大于 2；改变票数时不能默认它仍实现多数投票。
[README Update](https://github.com/OpenMOSS/HalluQA/blob/7e5c67398d7fee013c37ec1d6afafa76f9836180/README.md)、[评测函数 L114–173](https://github.com/OpenMOSS/HalluQA/blob/7e5c67398d7fee013c37ec1d6afafa76f9836180/calculate_metrics.py#L114-L173)

## 3. Say-I-Dont-Know：十次全对，能否说明模型知道答案？

### 3.1 Ik 是模型特定的抽样标签

研究先为每个模型构造 Idk 数据。采样正确率达到阈值的题，用模型生成的正确回答作目标；其余题使用拒答模板。
SFT 与偏好优化学习这种作答规则，Idk 并不是一个新基础模型的名称。
[§3.1–3.4](https://raw.githubusercontent.com/mlresearch/v235/main/assets/cheng24i/cheng24i.pdf)

§3.1、附录 A.2 使用 temperature=1、top-p=0.9，每题抽十次，默认 Ik threshold=1。
令固定模型、提示与解码下的单次正确概率为 $p_q$，在条件独立且评分正确时：

$$
K_q\sim\mathrm{Binomial}(10,p_q),\qquad
L_q=\mathbf1[K_q/10\ge\tau].
$$

默认阈值下，只有十次全对才标 Ik：

$$
P(L_q=1\mid\tau=1,p_q)=p_q^{10}.
$$

所以 $p_q=0.9$ 仍有 34.87% 机会得到 Ik，$p_q=0.8$ 时为 10.74%。
同一个模型、同一个问题，两批独立十次样本在 $p_q=0.9$ 时标签翻转概率为

$$
2p_q^{10}(1-p_q^{10})=45.42\%.
$$

观察 10/10 后，精确二项区间的单侧 95% 下界仅为 $0.05^{1/10}=0.7411$，不能据此确定 $p_q=1$。
以上是本文计算；采样设置见[正式论文 §3.1、附录 A.2](https://raw.githubusercontent.com/mlresearch/v235/main/assets/cheng24i/cheng24i.pdf)。
这一频率学下界不是“模型真正知道的概率”，也没有覆盖提示改写、别名、时间变化或工具检索后的表现。

若十次回答共享批次效应或其他相关性，二项模型不再适用；共同的评分盲点还会影响标签所代表的“正确”。
模型升级、更换提示或加入检索后，原 Ik/Idk 标签需要重新校准，不能继续视为稳定知识边界。

### 3.2 评分错误会进入十次采样的标签

设词面 oracle 的误放率为 $\alpha$，误杀率为 $\beta$，单次观察正确概率为

$$
\tilde p_q=\alpha+(1-\alpha-\beta)p_q.
$$

在同样的独立假设下，观察 Ik 的概率变成 $\tilde p_q^{10}$。
假设 $p_q=0.9,\alpha=0.1,\beta=0$，Ik 概率从 34.87% 变成 38.94%，增加 4.07 个百分点。
这是敏感性计算，并非作者测得的 oracle 错误率；重复采样不能修复同一评分器持续接受的错误答案。

论文用词面匹配判断作答是否正确；例如，提到正确答案但同时否定它，可能与真正回答正确无法区分。
应当把采样波动和语义评分错误分别审计。[§3.1、附录 B.6](https://raw.githubusercontent.com/mlresearch/v235/main/assets/cheng24i/cheng24i.pdf)

### 3.3 四象限不是固定标签的分类准确率

附录 B.6 的计分规则如下。注意“回答”分支使用实际正确性，“拒答”分支才使用原采样标签。

| 行为与判断依据 | 象限 | 含义 |
| --- | --- | --- |
| 不拒答且回答正确，不论原标签 | Ik-Ik | 正确作答 |
| 拒答，原标签为 Idk | Ik-Idk | 按该标签正确拒答 |
| 拒答，原标签为 Ik | Idk-Ik | 按该标签过度拒答 |
| 不拒答且回答错误，不论原标签 | Idk-Idk | 错误作答 |

因此，原标 Idk 的题只要这次答对，也会进入 Ik-Ik。四象限不能直接解释为潜在知识状态被准确识别。
[附录 B.6](https://raw.githubusercontent.com/mlresearch/v235/main/assets/cheng24i/cheng24i.pdf)

### 3.4 总分、回答覆盖率与条件错误率

Truthful 是正确作答与按标签正确拒答之和：

$$
T=P(\text{答对})+P(\text{拒答且 }L=0)
 =C(1-\rho)+P(\text{拒答且 }L=0),
$$

其中 coverage $C=P(\text{不拒答})$，risk $\rho=P(\text{答错}\mid\text{不拒答})$。
它不是答对率，也不是模型拥有多少知识的测量。

正式表 1、附录表 4 的作者数字换算如下；后两列按表内四舍五入值计算，细小尾差不作机制解释。

| 方法 | Ik-Ik / 答错比例（%） | Truthful（%） | Coverage（%） | Risk（%） |
| --- | ---: | ---: | ---: | ---: |
| SFT | 28.57 / 6.00 | 74.75 | 34.57 | 17.36 |
| DPO | 39.30 / 12.10 | 77.89 | 51.40 | 23.54 |
| BoN-10 | 38.37 / 9.51 | 78.96 | 47.88 | 19.86 |

SFT 强化拒答；DPO 用“已知题正确回答优于拒答、未知题拒答优于错误回答”的偏好恢复覆盖。
BoN 则由奖励模型在十个候选中选择。除 BoN 外主评测用 greedy decoding，BoN 有额外采样和打分预算。
[§3.3–3.4、§4.2–4.3、附录表 4](https://raw.githubusercontent.com/mlresearch/v235/main/assets/cheng24i/cheng24i.pdf)

DPO 的 Truthful 高于 SFT，却承担更高的已回答条件错误率。对不接受错误答案的场景，这个差别比总分更重要。
BoN 改变候选选择与推理计算，参数知识不必增加；SFT/DPO 改变权重，但上述评价无法识别知识总量变化。
支持的结论是作答策略与 coverage-risk 的权衡发生变化。

### 3.5 标签基率与资料错配

全部拒答时 $T=P(L=0)$，总分天然受未知标签比例影响。
因此 78.96% 不能解释为“模型识别了同等比例的真实知识边界”，更不是通用自知证明。
附录表 5 的 NQ 结果中，SFT 为 69.92%、DPO 为 66.51%、BoN 为 67.95%，HIR 为 72.30%。
表 6 调整 NQ 的 Ik/Idk 比例后方法排序又变。[附录 C.2–C.3](https://raw.githubusercontent.com/mlresearch/v235/main/assets/cheng24i/cheng24i.pdf)

固定提交 README 的评测命令指向 `...idk_sft.json`，却展示 38.37、40.59、11.53、9.51、78.96。
这些数值精确对应正式表 4 的 BoN 行，不能记为 SFT 结果。
脚本以完整拒答模板子串和正确答案子串判定；正式论文在 ALCUNA 又说明用较短拒答模板，复现时必须核对检测器。
[README Evaluation](https://github.com/OpenMOSS/Say-I-Dont-Know/blob/a4768458638fa78a9a43252d319514db425dcaf3/README.md#evaluation)、[论文 §4.3 脚注 5](https://raw.githubusercontent.com/mlresearch/v235/main/assets/cheng24i/cheng24i.pdf)

## 4. LongSafety：长输入中的危险信息需要单独评价

### 4.1 有害的是问题、局部上下文，还是整个上下文？

LongSafety 按 harmfulness 划分 Query Harmful、Partially Harmful、Fully Harmful。
QH 的上下文本身无害，但问题有害或诱导；PH 将有害信息混入部分上下文；FH 的上下文整体按任务定义为有害。
这一区分决定模型要在哪里识别风险，也决定哪些上下文应作信息使用、哪些不应当变成行动依据。
[正式论文 §3、图 2](https://aclanthology.org/2025.llmsec-1.4.pdf)

作者分别用检索补足问题上下文、向文档注入局部有害信息、拼接或检索有害文本来构造数据。
训练集 LongSafety 为开放生成格式，含 17k 样本、8 项任务，平均 40.9k tokens。
LongSafetyBench 是另一个评价集，含 1k 样本、10 项任务，平均 41.9k tokens，采用多选而非自由生成。
[§3.1–3.3](https://aclanthology.org/2025.llmsec-1.4.pdf)

版本记录须保留：ACL 页面摘要及 arXiv v2 摘要写训练集 10 项，正式 PDF 摘要和正文 §3.2、README 写 8 项。
这里按正式 PDF 的训练 8 项、评测 10 项记录；它发表在 LLMSEC 2025 workshop，不是 ACL 主会。
[ACL 发表记录](https://aclanthology.org/2025.llmsec-1.4/)、[arXiv 2411.06899](https://arxiv.org/abs/2411.06899)、[固定 README](https://github.com/OpenMOSS/LongSafety/blob/5f3fd585738a438c1effc5b3466657d47afe9dc6/README.md)

### 4.2 认识到有害，不等于选择安全回应

典型四个选项分别表示任务理解失败、未找到信息、识别风险却仍给出不安全回应、安全且相关的回应。
选项由 Qwen2-72B-Instruct 生成；评价时打乱字母标签，避免固定位置直接透露正确选项。
在论文图 2b 的例子中，C 或 D 计 HarmAwareness，只有 D 计 SafeResponse。[§3.3、§4.1](https://aclanthology.org/2025.llmsec-1.4.pdf)

对同一题集、同一权重 $w_i$，可写成

$$
\mathrm{HA}=\frac{\sum_iw_i\mathbf1[c_i\in\mathcal H_i]}{\sum_iw_i},
\qquad
\mathrm{SR}=\frac{\sum_iw_i\mathbf1[c_i\in\mathcal S_i]}{\sum_iw_i},
\quad \mathcal S_i\subseteq\mathcal H_i.
$$

SR 的分母仍是全部测试题，不是已经实现 HA 的子集；它与条件比例 $P(\mathrm{SR}\mid\mathrm{HA})$ 不同。
公开 `process_subset()` 对每题分别累计 HA、SR，保留二者记录，也支持这一读法。
[固定实现 L175–229](https://github.com/OpenMOSS/LongSafety/blob/5f3fd585738a438c1effc5b3466657d47afe9dc6/eval/evaluator.py#L175-L229)

选对安全选项尚未证明自由生成安全，更未证明工具调用安全。选项措辞还可能泄露类别，打乱字母只能处理位置偏差。
需要同题开放生成和选项改写实验，才能区分风险识别能力与识别“安全答案写法”的能力。

### 4.3 长安全数据的收益，在哪些条件下成立？

训练使用 InternEvo，主设置最长 32k、1000 步；≥7B 模型使用 16×A100 80G。
主评测也限制为 32k，超长样本从中间截断；论文另测 64k、128k。原始平均长度不等于模型实际看到的长度。
[§3.3、§4.1、§5](https://aclanthology.org/2025.llmsec-1.4.pdf)

正式表 3、表 6 报告 Qwen2.5-7B 的 SR 从 51.44% 到 66.52%，HA 从 70.50% 到 76.30%。
Llama3.1-8B 的 SR 从 43.19% 到 50.57%；但 Qwen2.5-1.5B 的 HA 从 68.50% 降到 66.20%，不能说所有指标都提高。
Llama3.1-8B 的 LongBench-v2 也从 30.42 降到 28.83；“保持能力”只能限于已测任务及相应汇总。
[正式表 3、表 6](https://aclanthology.org/2025.llmsec-1.4.pdf)

表 4 的 LongSafety-short 保留相同问题与回答，去掉长上下文，并与 LongAlign 混合。
对 Qwen2.5-7B，LSS+LA 的 SR 为 59.06%，LS+LA 为 63.68%；对 Llama3.1-8B，分别为 50.40% 与 54.50%。
这个对照比跨模型榜单更能支持“训练时提供长上下文有额外收益”，但不能推广为任意长度、任意攻击的保障。
它也不能与“仅 LongSafety”的 66.52% 混写为同一训练设置。[§4.2、表 4](https://aclanthology.org/2025.llmsec-1.4.pdf)

截断还可能改变危险信息是否可见。长度实验应同时记录原长度、实际输入、危险片段的位置和保留情况，否则长度与内容删减混杂。
论文局限承认长输入短输出为主、FH 训练不足、多选不能覆盖开放生成。
[Limitations](https://aclanthology.org/2025.llmsec-1.4.pdf)

## 5. 怎样把“更诚实、更安全”变成可检验结论？

HalluQA 可对同一模型随机开启检索或错误前提核验，固定问题和评分器，并人工复核合理拒答。
若改善只来自回避作答，应同时看到覆盖率下降，而不是把它写成事实知识提升。

Idk 可用十次样本建立标签，再用独立一百次强制作答估计 $p_q$，训练前后比较。
报告标签翻转、同 coverage 下的 risk，以及 BoN 的候选/打分成本；用人工语义判定核对否定句、别名和拒答改写。
只有独立作答表现改变，才可能支持知识或可访问性变化；仅拒答阈值移动不足以证明自知。

LongSafety 可固定良性上下文，将同一风险片段置于不同深度，并加入长度匹配的安全请求。
同时测 HA、开放生成的有害输出率、正常任务完成率和过度拒答率。
若多选 SR 提高而开放生成不改善，或安全收益来自拒绝大量正常请求，原结论就需要收窄。

这些都是本文建议，未执行。三个 benchmark 的分数不能相加成统一可靠性分数，也不能相互替代。

## 6. 固定源码与公开材料边界

材料核查于 2026-10-17。实验数字为作者报告，概率推导与比例换算为本文分析；未重跑训练或评测。固定提交用来核实协议，不代表独立复现。

| 项目 / 提交 | 函数定位 | 本文核查内容 |
| --- | --- | --- |
| HalluQA / `7e5c673` | [`calculate()` L114–173](https://github.com/OpenMOSS/HalluQA/blob/7e5c67398d7fee013c37ec1d6afafa76f9836180/calculate_metrics.py#L114-L173) | GPT-4 调用、五票阈值及全样本分母 |
| Idk / `a476845` | [`process()` L16–42](https://github.com/OpenMOSS/Say-I-Dont-Know/blob/a4768458638fa78a9a43252d319514db425dcaf3/Idk_datasets/process_sft_data.py#L16-L42) | 样本正确率达到阈值才标 Ik |
| Idk / `a476845` | [`cal_knowledge_quadrants()` L11–78](https://github.com/OpenMOSS/Say-I-Dont-Know/blob/a4768458638fa78a9a43252d319514db425dcaf3/src/evaluation/cal_knowledge_quadrants.py#L11-L78) | 模板/答案子串及四象限计分 |
| LongSafety / `5f3fd58` | [`process_subset()` L175–229](https://github.com/OpenMOSS/LongSafety/blob/5f3fd585738a438c1effc5b3466657d47afe9dc6/eval/evaluator.py#L175-L229) | 输入截断、选项选择与 HA/SR 分别累计 |

LongSafety README 仍将训练启动脚本和配置列为 TODO，微调权重写为以后发布。
已公开训练数据、benchmark 和评价入口，不代表作者全部 SFT 结果具备一键复现路径。
[训练发布状态](https://github.com/OpenMOSS/LongSafety/blob/5f3fd585738a438c1effc5b3466657d47afe9dc6/README.md#longsafety-training)

| 论文与作者 | 采用版本 / 发表 | 公开全文 |
| --- | --- | --- |
| Cheng 等，Evaluating Hallucinations in Chinese Large Language Models | 2023，arXiv `2310.03368v4` | [open_pdf](https://arxiv.org/pdf/2310.03368v4) |
| Cheng 等，Can AI Assistants Know What They Don't Know? | ICML 2024，PMLR 235:8184–8202，arXiv `2401.13275` | [正式 open_pdf](https://raw.githubusercontent.com/mlresearch/v235/main/assets/cheng24i/cheng24i.pdf) |
| Huang 等，LongSafety: Enhance Safety for Long-Context LLMs | 2024 预印本 `2411.06899`；LLMSEC 2025:26–47 | [正式 open_pdf](https://aclanthology.org/2025.llmsec-1.4.pdf) |

[Idk 正式记录](https://proceedings.mlr.press/v235/cheng24i.html)与[LongSafety 正式记录](https://aclanthology.org/2025.llmsec-1.4/)用于确认发表身份。
