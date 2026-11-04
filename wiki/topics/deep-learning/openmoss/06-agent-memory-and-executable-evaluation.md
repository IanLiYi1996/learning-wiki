# 工具使用与数字 Agent：怎样学会调用，怎样确认任务完成

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

语言模型生成一段工具调用，只解决了“请求怎样写”。实际工作还要求选择合适的工具、根据返回值调整计划、处理环境失败，并确认最终产物达到了要求。OpenMOSS 在这条线上的公开工作分别涉及工具数据整理、Agent 轨迹训练和执行评测；它们不是同一个模型的三个别名。[UnifiedToolHub](https://github.com/OpenMOSS/UnifiedToolHub/blob/8235954cd3219b6f6facbdf8a7bf65e740c0a5ad/README.md)、[ABC §1、§6.2](https://arxiv.org/pdf/2601.11077v1)

当助手连续维护一个科研代码库，历史能省去搭环境、摸索配置的重复劳动，也可能把旧版本的单位约定带进新任务。检索到了相关日志，只说明信息被找到；是否适用、是否被正确执行，还要看产物。下面先讲调用能力的训练，再讲记忆和任务评价。知识拒答已单独放入[诚实性与安全专题](12-honesty-and-long-context-safety.md)。[ContextWeave §1、§4](https://arxiv.org/html/2608.04830v1)

## 1. 工具能力怎样从数据中学来？

早期 MOSS 用插件增强对话教模型生成调用、读取返回值，见[基础模型专题](09-foundation-and-omni-models.md)。当工具数据来自不同来源，新的困难是格式不一致：同一调用可能用不同字段、参数表达和对话模板。未经整理地混合数据，会让模型同时学习多套不兼容的接口。

UnifiedToolHub 将 API-Bank、BFCL、MTU-Bench、Seal-Tools、TaskBench、ToolAlpaca 等数据整理为标准格式，再标注单轮／多轮、单步／多步、每步工具数量等标签。训练工作流据此筛选样本，并按目标模型模板生成数据；实际微调仍需运行自己的训练代码。它是数据与评测底座，本次没有核验到专属模型论文，也不能凭 `train` 命令认定已经训练了一个新模型。[固定 README：标准化、标签与训练](https://github.com/OpenMOSS/UnifiedToolHub/blob/8235954cd3219b6f6facbdf8a7bf65e740c0a5ad/README.md)

这种组织方式允许更明确地控制学习目标。例如，单轮多步数据教模型在一次需求下按顺序调用；多轮数据还需要处理用户追加条件。但这些能力是否形成，必须在相应任务上验证，不能只看生成的数据文件。尤其不能把评测集直接混进训练后，再报告同一批任务的泛化。

工具匹配分数也有条件。项目的 `single_first` 只评价首个调用块，忽略后续；`single_last` 的此前步骤使用 golden 值。后者测试的是“前面已经正确时，这一步能否做对”，没有让早期错误真实传播。ExactMatch、ToolAccuracy 和 ParameterAccuracy 适合定位接口错误，却不能代替多步执行成功率。README 也说明，采用模型官方模板所得结果不能直接与使用自定义模板的原论文分数比较。[评测模式与模板说明](https://github.com/OpenMOSS/UnifiedToolHub/blob/8235954cd3219b6f6facbdf8a7bf65e740c0a5ad/README.md)

### Agent 轨迹训练提供了什么证据？

调用训练进一步扩展为工作轨迹训练后，监督对象包括探索仓库、编辑文件、配置环境和处理反馈。ABC 的 §6.2 使用外部 Nex-N1 公开数据的 agentic coding 子集，对 Qwen3-8B 和 Qwen3-32B 做 SFT，再用 OpenHands 评测；平均 pass@1 分别从 8.3% 提升至 13.9%、从 8.9% 提升至 33.8%。这是作者在后端编码任务上的训练证据，不是 UnifiedToolHub 的实验，也不是团队从头预训练了这两个基座。[ABC §6.2、图 6(b)](https://arxiv.org/pdf/2601.11077v1)

这些结果支持完整工作轨迹对任务完成有帮助，却没有分离哪类步骤贡献最大：更多代码知识、更好的工具参数、更有效的失败恢复，都可能影响结果。论文该节未给出足以拆分这些贡献的消融，也没有据此证明模型能长期自主工作。后面需要结合部署、科学契约和记忆评测，判断“成功”具体指什么。

## 2. 记忆怎样影响后续工作？

令历史为 $H$，当前环境为 $S$，召回为 $R=M(H,Q)$，采纳的工作假设为 $B$，行动为 $A$，产物质量为 $Y$。分析路径是

$$
H\rightarrow R\rightarrow B\rightarrow A\rightarrow Y,
\qquad (Q,S)\rightarrow(B,A,Y).
$$

这里 belief 是可被接受、核验或推翻的操作假设，并非已测得的内部心理状态。语义 recall 只测 $H\rightarrow R$ 的匹配，不能保证经验适用、模型采纳正确、工具动作可行。ContextWeave 的相关性用参考片段与召回块的余弦矩阵 $s_{ij}$：

$$
\mathrm{Recall}=\frac1{|G|}\sum_i\mathbf1[\max_j s_{ij}\ge0.65],\quad
\mathrm{Precision}=\frac1{|R|}\sum_j\mathbf1[\max_i s_{ij}\ge0.65].
$$

它不是检索到“正确操作”的概率，也不要求一对一匹配。[论文 §4.5、§5.2.1](https://arxiv.org/html/2608.04830v1#S4.SS5)、[实现 C1](https://github.com/OpenMOSS/ContextWeave/blob/339783f8648902d2ac086ac696ec9cb276ddef44/contextweave/metrics/memory/relevance/semantic_utils.py#L297-L334)

例如， 历史明确“默认导出 CSV”，当前用户明确要求 JSON。两个 agent 接收完全相同的召回，故相关性分数相同；甲把默认偏好当硬约束而输出 CSV，乙核对本次指令后输出 JSON。召回事实没有错，差别发生在 $R\rightarrow B\rightarrow A$。因此高 recall 与正执行增益可以分离，甚至出现负增益。

### 检索分数与执行收益

Workspace Score 检查最终 Docker 工作区及必要执行证据，而非回答措辞；约 60 表示最低完成、80 表示参考质量。Preference Score 对适用的参与者偏好 rubric 加权归一至 0–100，不能读成偏好正确率。记忆诱发问题率为

$$
H_M=\frac1N\sum_t\mathbf1[\exists e: \mathrm{Judge}(e,R_t,\tau_t)=\text{memory-induced}].
$$

判定需同时支持“记忆有误导信息、轨迹实际依赖它、依赖促成问题”；包含后来解决的执行问题，不等于最终失败率，且仍是评审归因而非随机干预。[§4.5、§5.3.5、附录 B.7.3](https://arxiv.org/pdf/2608.04830v1)

表 1 中 memos 的 LLM 相关性为 4.09，高于 a-mem 的 3.73，但 Workspace 为 70.01 对 78.20；a-mem 的诱发问题率又达 7.39%。相关性、可操作性与抗误导性并不共同排序。§5.2.3 明说组件还改变检索策略和上下文长度，不能把收益单独归给“经验优于摘要”。[表 1、§5.2.3](https://arxiv.org/pdf/2608.04830v1)

Solvability 的分母是无召回轨迹结束时仍未解决的执行问题，分子是评审认为“召回足以解决”的问题；它测信息充分性，不测 agent 实际解决率。它与上述按任务统计的诱发问题率不能相减成净收益。少探索也有歧义：省去重复扫描与省去必要验证都会减少调用，只有结合产物和问题解决证据才能区分。[§4.5、附录 B.7.3](https://arxiv.org/pdf/2608.04830v1)

### 固定起点测不到自主错误积累

§4.4 将轨迹对齐到参考结果，每题从 canonical checkpoint 开始；公开插件注入的是先前参考 sessions。它估计的是固定参考历史、固定起点下的增益：

$$
\Delta_{\rm ref}=E[Y(M(H^{ref}),S^{ref})-Y(\varnothing,S^{ref})].
$$

自由运行则让 $H^M,S^M$ 都由过去行动生成；其长期累计收益不是 $\Delta_{\rm ref}$。重置阻断了错误工作区和自写错误记忆的后续传播。因此本文不是“数月自主运行仍可靠”的证据，也不是各 memory system 的纯架构比较。[§4.4](https://arxiv.org/html/2608.04830v1#S4.SS4)、[插件协议](https://github.com/OpenMOSS/ContextWeave/blob/339783f8648902d2ac086ac696ec9cb276ddef44/contextweave/plugins/README.md)

## 3. 通过测试，究竟说明什么？

ABC 的执行门槛可分为服务构建启动 $D$ 和外部 API 行为通过 $F$：

$$
P(\mathrm{success})=P(D)\,P(F\mid D).
$$

但 $F\mid D$ 只覆盖已启动的选择性子集，不能外推为“替所有失败任务修好环境后”的功能成功率。Science 则从固定科学定义到私有测试，要求补丁保持单位、表示等价、边界与跨模块契约；程序可运行并不等于科学语义成立。

### 部署成功与科学契约

ABC §4.1 用 GPT-5 构造 API 测试、环境和遮蔽任务；§4.2 要求原仓库通过、遮蔽后失败。这验证测试能检出选定缺失，却不能证明能检出所有错误实现。图 4 中 GPT-5 的构建成功率 39.3%、条件功能成功率 82.9%，显示部署是独立瓶颈，也显示分母选择。[§3.2、§4.1–4.2、图 4](https://arxiv.org/pdf/2601.11077v1)

Science §3.1 冻结规格并隔离测试与参考补丁作者的相互信息；§4 以语义等价和反向校准检查硬编码、伪修复、遗漏路径。提交后在独立 verifier 的干净 baseline 应用补丁并重新构建，避免沿用 agent 的缓存二进制。镜像 digest、baseline commit、选择集 hash 固定环境，却不证明测试完整；默认 96 题也不能直接与论文 119 题相比。[§3–4](https://arxiv.org/pdf/2608.19799v2)、[发布架构 §6–8、§12](https://github.com/OpenMOSS/SWE-bench-Science/blob/08cea5a2ff7f56252de8658a75a4144c18a6c946/docs/architecture.md)、[字段契约](https://github.com/OpenMOSS/SWE-bench-Science/blob/08cea5a2ff7f56252de8658a75a4144c18a6c946/docs/dataset-contract.md)

成功率、均分和 run budget 必须分开。若每题 $m_t$ 个私测，$x_{tj}\in\{0,1\}$，Science 的两种汇总为

$$
\mathrm{PrivateScore}=\frac1N\sum_t\frac{\sum_jx_{tj}}{m_t},
\quad \mathrm{Pass@1}=\frac1N\sum_t\prod_jx_{tj}.
$$

这是按题宏平均，不是把所有子测试池化。表 2 中 Claude-Opus-5 的 PrivateScore 为 75.11%，精确成功率仅 47.90%。ABC 表 2 的三次运行计平均 Pass@1，即 $\sum_{t,r}z_{tr}/(3N)$，不是“任一次成功”的 $\sum_t\max_rz_{tr}/N$。ABC README 的示例配置是 agent 3600 秒、测试 1800 秒，并非主表全部预算的证明；Science 图 5 比的是不同模型–harness 实际 token 消耗，不能视为等预算比较。[Science §5、表 2、图 5](https://arxiv.org/pdf/2608.19799v2)、[ABC 表 2](https://arxiv.org/pdf/2601.11077v1)、[ABC 运行示例](https://github.com/OpenMOSS/ABC-Bench/blob/265af02a78fd8bc6b84d75b4001e23983fa41db9/README.md)

### 科研 Agent 怎样利用实验反馈？

科研助手还需要根据指标和日志决定下一次实验，而不是只修代码。AgentHPOBench 将 30 个研究仓库变成受约束的超参数优化任务：先共享同一次基线运行，再给模型五次调整机会。数据划分、目标指标和评价代码保持固定，模型根据配置、指标和日志提出下一组参数。这测的是顺序实验决策，不是开放式科研创新。[AgentHPOBench §3–4](https://arxiv.org/pdf/2607.29626v1)

主协议给最后一次干预结果计分，既测能否找到好配置，也测能否保住已有收益；传统 HPO 通常返回历史最佳配置，两种口径不能混比。论文附录的 best-so-far 对照中，Random Search、TPE 和 BOHB 均超过所测开源权重 Agent，因此不能只用最后一步主表宣称 LLM 全面优于传统优化。提升相对仓库锚点的归一化分数，也不等于独立测试集上的泛化收益。[附录 §8、§11.3、表 12–14](https://arxiv.org/pdf/2607.29626v1)

### 测试规则自身的误差

要区分 LLM 造测试与 LLM 判结果：ABC 存在同源造题、造测试的盲点；ContextWeave 的 rubric、历史证据、评分和部分 mock 资源依赖 LLM；Science 最终主要是程序测试，不能一概叫“LLM 裁判”。

对二值评审，设真实通过率 $p$，误放率 $\alpha=P(\hat Z=1\mid Z=0)$，误杀率 $\beta=P(\hat Z=0\mid Z=1)$，在固定条件错误率下：

$$
E[\hat Z]=\alpha+(1-\alpha-\beta)p.
$$

**假设性计算**：$p=0.5,\alpha=0.02,\beta=0.05$ 得观察值 48.5%，低估 1.5 个百分点；若错误率随模型风格变化，排序也可能反转。造测试的偏差应另测漏检缺陷率、错误拒绝合法替代实现率，而非套用裁判误差。ContextWeave 局限只给初步人工一致性，不能据此填写 $\alpha,\beta$；真实偏差仍未知。[ContextWeave §4.3、§5.2.1、Limitations](https://arxiv.org/pdf/2608.04830v1)

## 4. 过期经验怎样污染后续产物？

### 版本变化后的重复误用

版本 v1 的 `export()` 返回 kcal/mol；agent 经测试学到“乘 4.184 转成 kJ/mol”。v2 已直接返回 kJ/mol，但旧记忆缺版本条件。第二次任务再次乘 4.184，并把处理后的文件存成后续任务依据；第三次任务只汇总该文件，虽不再检索旧记忆，误差仍传播。两次执行加一次消费已经足够；不是召回失败，而是历史成功被错误提升成跨版本规则。

最小记忆条目应记录

$$
m=(\text{claim},\text{source-id},\text{source-version},
\text{observed-at},\text{validity-condition},\text{derived-from}).
$$

provenance 使事实能回到原证据；versioning 标识适用范围；invalidation 在源版本或前提失效时停用，并沿派生依赖图标记下游产物待复核。只删原记忆不能修复已经生成的错误文件；只用 TTL 也不能处理刚发生的版本切换。

### 版本锁定的作用

ContextWeave 附录 B.7.3 已把 stale memory 和覆盖当前指令列入风险。Science 的镜像 digest、source commit 和 clean rebuild 提供版本锁定范式；ABC 的原实现通过测试，也只在该实现与环境上成立。[ContextWeave B.7.3](https://arxiv.org/pdf/2608.04830v1)、[Science 版本契约](https://github.com/OpenMOSS/SWE-bench-Science/blob/08cea5a2ff7f56252de8658a75a4144c18a6c946/docs/dataset-contract.md)、[ABC §4.2](https://arxiv.org/pdf/2601.11077v1)

### 追溯来源，还要检查真假

参考历史与 checkpoint reset 不会完整暴露上例的派生文件链，版本锁定也未证明 memory invalidation 的因果效果。更重要的是，来源可追溯不等于来源为真：一次未验证推测即使带完整时间戳，反复摘要后仍可能被当成多次独立证据。因此还须区分原始观察、推断和验证结果，保留共同祖先，不能用引用次数代替证据独立性。这是研究假设，不是上述工作已验证的遗忘机制。[ContextWeave §4.4 的协议边界](https://arxiv.org/pdf/2608.04830v1)

## 源码定位与资料版本

这些定位核实测量协议，不表示已重现论文。Science 的汇总函数读取 reward，不重建 oracle；基础设施失败不得静默从分母删除。

| 标记 | 固定 commit / 函数 | 核查内容 |
| --- | --- | --- |
| C1 | `339783f` / [`scores_from_raw()`，L297–334](https://github.com/OpenMOSS/ContextWeave/blob/339783f8648902d2ac086ac696ec9cb276ddef44/contextweave/metrics/memory/relevance/semantic_utils.py#L297-L334) | 两方向取最大相似度，再阈值化 |
| C2 | `08cea5a` / [`collect_rows()`，L50–75](https://github.com/OpenMOSS/SWE-bench-Science/blob/08cea5a2ff7f56252de8658a75a4144c18a6c946/scripts/summarize_results.py#L50-L75) | 分开保留 public/private 通过数、收集数与 failure class |
| 工具数据 | `8235954` / [UnifiedToolHub README](https://github.com/OpenMOSS/UnifiedToolHub/blob/8235954cd3219b6f6facbdf8a7bf65e740c0a5ad/README.md) | 标准格式、标签筛选、训练数据准备与分步评测 |

材料核查于 2026-10-17。论文采用 ContextWeave v1、ABC v1、SWE-bench Science v2 和 AgentHPOBench v1。实验数字来自作者，概率计算与例子为本文分析；未重跑模型。
