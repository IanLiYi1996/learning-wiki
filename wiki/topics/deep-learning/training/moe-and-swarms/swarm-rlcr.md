# 02 Swarm 与 RLCR：怎样让协作成为有回报的行为

研究与来源核验日期：2026-11-09。[专题导读](README.md) · [上一章：MoE](moe-training.md) · [下一章：联系与评测](connections-and-evaluation.md) · [来源](sources.md)。

Swarm 的学习对象不是“把一个 token 分给几个 FFN”，而是多个 Agent 在环境里怎样分工、交流和完成任务。本章以 General Reasoning 的 [How to Train a Swarm](https://www.gr.inc/blog/how-to-train-a-swarm) 和 [Avalon-M1 技术报告](https://gr.inc/avalonm1.pdf) 为例，不代表所有组织式 Agent 训练。

## 1. 三种用更多推理计算的办法

| 方式 | 计算怎样增加 | 哪类问题值得比较 |
| --- | --- | --- |
| 单 Agent 更长推理 | 一条轨迹继续思考、检查或调用工具 | 有较强顺序依赖的任务 |
| 独立多次尝试后选择 | 并行生成候选，再投票或验证 | 候选基本可独立求解的任务 |
| 通信式集体协作 | 拆分工作、共享中间结果、合并产物 | 子任务互补且存在依赖的长程任务 |

通信不一定优于独立尝试。任务已经可以完全独立并行时，沟通可能只是额外开销；只有它改善了结果或关键路径才有价值。博客以这三种组织方式讨论“怎样让并行工作有回报”，不是要求所有任务都组建 Swarm。[博客：Making parallel work pay](https://www.gr.inc/blog/how-to-train-a-swarm)

## 2. 共享策略、共享回报，不等于共享上下文

Avalon-M1 的核心是共享 policy：不同角色调用同一组模型权重，但拥有自己的观察和行动历史；组织的集体回报产生一个 flat collective advantage，并用于所有成员的学习。它与“只训练调度器、冻结 worker”的设置不同。[报告：Training](https://gr.inc/avalonm1.pdf)

用教学记号表达，Agent $a$ 的行动来自 $\pi_\theta(u^a_t\mid h^a_t)$。共享 $\theta$ 不要求 $h^a_t$ 相同，也不要求动作相同。角色提示、可见消息和环境状态会影响它各自的输入。

还要分清两个“共享”：同一个组织内可以有共享工作空间；同一题采样的多个 rollout 是不同组织轨迹，并不能因奖励比较而互相读取彼此的答案。博客明确把当前 recipe 的不同 rollout 隔离，与未来跨 episode 公共知识贡献区别开。[博客：Outstanding problems](https://www.gr.inc/blog/how-to-train-a-swarm)

## 3. 集体优势怎样推动参数更新

以下公式只展示 policy gradient 的方向，**不是技术报告训练 loss 的完整复刻**：

$$
A(\tau)=R(\tau)-b(q),\qquad
\nabla_\theta J\ \propto\
\mathbb E_\tau\!\left[
A(\tau)\sum_a\sum_{t\in\text{agent actions}}
\nabla_\theta\log\pi_\theta(u^a_t\mid h^a_t)
\right].
$$

$\tau$ 是整个组织的轨迹，$R$ 是环境回报，$b(q)$ 是针对任务的比较基线。这个表达暂时省略概率比、mask、归约和采样校正；报告中的具体 baseline 与更新规则见[核验记录](sources.md)。

报告的大多数环境使用 CISPO，将重要性概率比上限设为 5；组内采样数 $K=16$ 指 rollout 组，不是 16 个 Agent。报告没有逐项公开完整 loss 的归约与数值处理，不能将 MiniMax 的 CISPO 原式不加说明地写成已验证的 Avalon 实现。[报告 §2.2.1，第 11 页](https://gr.inc/avalonm1.pdf#page=11)

只给策略主动生成的有效 token 承担 loss，prompt、工具观察和收到的同伴消息不再次作为生成动作更新。组织回报也不只是终局正确率，还包含工具格式／执行错误及不足招募的惩罚。因此“用任务回报学出协作”不等于 recipe 没有额外的行为先验。[报告 §2.2.2，第 12 页](https://gr.inc/avalonm1.pdf#page=12)

直觉是：当一个组织比比较基线表现更好，更新提高其行为的倾向；较差则向相反方向更新。**Flat 指优势共享，不是给每个人发同额工资，更不是认定每一个 token 都有同样的因果贡献。** 自己的梯度、产生多少有效动作、mask 和归约规则仍会影响更新。

这种信号很便宜，却很粗：帮助同伴的消息可能直到很久以后才影响得分；重复工作甚至无关发言也可能获得同方向的优势。共享回报让合作有机会被强化，但没有自动完成精细的多 Agent 信用分配。博客将“长 episode、多人共享优势、多环境学习”列为后续困难。[RLCR 的学习问题](https://www.gr.inc/blog/how-to-train-a-swarm)

## 4. 为什么必须设计延迟压力

若奖励只看最终正确性，那么 10 分钟完成和 100 分钟完成的两个成功组织可能得到同样回报。仅增加 Agent 数不会自动使“更快”成为优化目标。

博客讨论两类激励：显式延迟惩罚，以及截止时间。Avalon-M1 采用后者作为延迟压力来源，不应把博客里的示例惩罚公式写成它的实际 reward。[博客：Latency penalties／Time limits](https://www.gr.inc/blog/how-to-train-a-swarm)

教学表达可以写为：

$$
R_{T_{\max}}(\tau)=
\operatorname{Score}\!\left(s_\tau(\min(T_{\text{end}},T_{\max}))\right).
$$

即到截止点读取当前状态的得分。它说明机制，不规定每一种环境必须使用这个具体 scoring function。

**截止时间不是连续的提速奖励。** 两条轨迹都在截止前达到相同回报，不因其中一条更早完成就自动得到更高分。它主要让“来不及达到目标”的慢轨迹吃亏。

## 5. Anytime-return 环境：随时停止也能衡量进展

只有终局“成功／失败”的任务，过早截断后可能全是零分。Avalon-M1 因而使用能评估中间进展的长程环境：例如软件任务中的测试通过情况。训练中逐步放宽最大墙钟时间，让组织有机会收回初期协调成本。[博客：Time limits](https://www.gr.inc/blog/how-to-train-a-swarm)

原创教学算例，非作者实验：截止时间 20 分钟，评分器是固定 10 个持出测试的通过数。

- 单 Agent 在 20 分钟时通过 6 个测试，回报 6。
- 协作组织在 20 分钟时通过 8 个，回报 8。
- 两个组织分别在第 10 和第 18 分钟通过全部 10 个，若截止前得分保持为 10，它们回报相同。

要预先定义部分奖励、失败计数及是否允许回滚；固定评分器，不让 Agent 删测试、修改 judge 或只刷容易项。Anytime-return 是有用的环境接口，不是环境天然正确的保证。

## 6. 通信与组织结构：给原语，不把脚本当学习成果

Avalon-M1 的组织有 CEO 和至多 8 名 specialist；CEO 可招募和解雇成员，成员可通过 direct message、channel 和 archive 交流。角色结构存在，但不同成员都参加共享策略的训练。[博客：Communication primitives；报告环境说明](https://www.gr.inc/blog/how-to-train-a-swarm)

要区分两层证据：

- Harness 已提供了什么：角色、权限、工具、招募接口及共享空间。
- 策略学会了什么：什么时候委派、发什么消息、怎样避开冲突、怎样合并互补产物。

如果任务分解和沟通脚本已被程序完全规定，观察到团队成功不能单独证明模型学会了新的组织行为。这是本 Wiki 的归因提醒，不是否定结构化 Harness 的实用价值。

## 7. 怎么知道真正学会了协作

至少分别衡量环境回报、时间、总计算和沟通。更多消息可能只是更啰嗦，更多 token 也可能是重复劳动；博客中的“有用工作”以操作环境的 turn 的 reasoning／output token 为 proxy，不能等同于经过独立验证的产出。[博客：Signs of life](https://www.gr.inc/blog/how-to-train-a-swarm)

作者报告：在 matched-output-token 对照下，单 Agent extended-thinking 基线花费约 4 倍时间。这是 derived latency：用新增 prompt／output token 的固定参考速率，加工具耗时和消息依赖，重放出关键路径。它去除了服务排队等影响，**不是已经在本地实测的 4 倍加速，也不是所有任务均有此收益**。[报告 §3.2.2 与附录 C.2](https://gr.inc/avalonm1.pdf#page=22)

EdgeBench 交叉点还存在源文差异：博客写约 **2.4 小时**，当前报告图 8 写观测 **1.7 小时**、拟合 **1.8 小时**的 derived latency。未找到解释两份材料差异的作者说明，因此不把其中一个数写成统一结论。[差异核验记录](sources.md)

S8 是同一混合集体训练模型的单 Agent 推理模式，强制匹配 B8 的 output-token 预算，并非单独训练的纯单 Agent 对照。组织在同 token 下也不是普遍更准确；报告表 3 的 SWE-Bench Pro V2 (Hard) 上，S8 为 37.3%，B8 为 23.5%。作者还明确缺少相同训练 compute 的纯单 Agent 训练消融。[报告表 3，第 20 页；§7.1.1，第 40 页](https://gr.inc/avalonm1.pdf#page=20)

还需要无通信、独立尝试、相同 token 预算单 Agent 等对照，才能把多算、并行、通信和训练的收益拆开。详细模板见[综合章](connections-and-evaluation.md)。

## 8. 已知边界

博客称其初期训练组织至多 9 个 Agent。小团队训练到大 Swarm 部署的泛化、长程共享奖励的信用分配，以及当前 episode 未受益但未来可能受益的公共知识贡献，仍是开放问题。[博客：Outstanding problems](https://www.gr.inc/blog/how-to-train-a-swarm)

权限也不能由集体奖励兜底。共享文件、消息和工具可能扩大错误或越权影响；训练和部署都应明确隔离、凭证、持久状态、评分器和人工介入边界。[已有 Sandbox 专题](../../../agent-sandbox/README.md)

## 自测

1. 共享策略为什么仍能产生角色差异？
2. 两个组织都在截止前完成且回报相同，早完成的是否自动多得奖励？
3. Reward、环境操作 token 和消息量都提高，是否足以证明通信造成了性能提升？

参考：输入、历史与权限不同；单靠截止时间不会；不够，还需预算匹配、通信消融、独立产出检查和固定评测协议。共享优势提供方向，但不等于精确归因。
