# LLM 训练与后训练：配方不是一串超参数

研究日期：2026-11-03。[深度学习五方向目录](../README.md#category-training)。

这一分组讨论“怎样让参数更新可解释、可验证、可复现”。先分清预训练、SFT、偏好优化、可验证奖励 RL 和 Agentic RL，再看数据、环境、计算与评测怎样共同构成 recipe。可从 [Rufus-Air 八阶段配方](rufus-air/README.md)看整条流水线，从 [Agentic-RL Lab](agentic-rl-lab/README.md)看算法到源码；这里不是完整预训练教科书。

## 当前读本与细分入口

| 细分问题 | 读哪一页 | 看完应该能检查什么 |
| --- | --- | --- |
| 一条后训练流水线怎样接力？ | [Rufus-Air 总览](rufus-air/README.md) | 起始模型、阶段顺序、继承状态与证据边界 |
| 数据怎样变成监督信号？ | [01 数据、SFT 与 RLVR](rufus-air/data-sft-and-rlvr.md) | 模板、loss mask、可学习性、验证器与查漏 |
| 会写代码，怎样变成会操作环境？ | [02 Agentic RL](rufus-air/agentic-environments.md) | 工具权限、持久状态、token 轨迹与失败分类 |
| 奖励上升为什么可能更糟？ | [03 奖励与稳定性](rufus-air/reward-and-stability.md) | judge、RLHF、相对优势、MoE 回放和回退 |
| 怎样读 batch、资源和模型成绩？ | [04 基础设施与评测](rufus-air/infrastructure-and-evaluation.md) | 单位、真实成本、同协议比较与归因 |
| 不用大 GPU 可以验证什么？ | [标准库实验与检查表](rufus-air/lab.md) | 计数、mask、token 合同、失败分类和测量合同 |
| 什么已公开、什么仍需补齐？ | [来源与复现边界](rufus-air/sources.md) | 固定论文／组件版本，区别上游能力与专用适配 |

## Agentic-RL Lab：六类问题拆到代码

| 细分方向 | 入口 | 不应混淆的对象 |
| --- | --- | --- |
| 优化目标 | [GRPO／DAPO／GSPO](agentic-rl-lab/policy-objectives.md) | 奖励、优势、概率比、裁剪、归约 |
| 工具与环境 | [Search-R1／ReTool／ALFWorld](agentic-rl-lab/tools-and-environments.md) | 动作与观察；工具成功与任务成功 |
| 在线蒸馏 | [OPD／OPSD](agentic-rl-lab/on-policy-distillation.md) | student 采样、teacher 评分、训练特权与 DPO |
| 长程信用分配 | [AgentOPSD／TEMPO](agentic-rl-lab/credit-assignment.md) | 终局方向、turn 重分配、macro-step bootstrap |
| 多模态与评分器 | [视觉／Spec-o3／Jev／Tournament](agentic-rl-lab/multimodal-and-judges.md) | 图像条件、SFT、RL、校准与相对排序 |
| 评测复现 | [代码合同与检查表](agentic-rl-lab/evaluation-and-reproduction.md) | 题目身份、harness、预算、失败和真实成本 |

[导读与 16 个上游入口映射](agentic-rl-lab/README.md) · [标准库实验](agentic-rl-lab/lab.md) · [固定来源与核验范围](agentic-rl-lab/sources.md)。新增读本不移动 Rufus-Air 页面，也不声称小规模示例已经复现大型 MoE recipe。

## 一份训练合同至少有六部分

以下是本 Wiki 的教学模板，不是新增的训练算法：

1. **起点与目标**：哪个 base／instruction checkpoint；希望改变什么，不希望损害什么。
2. **数据与格式**：来源版本、使用条件、去污染、模板、角色、标签与 loss mask。
3. **更新规则**：实际消费示范、偏好对还是新 rollout；优化器、batch 单位、更新次数与正则。
4. **反馈与环境**：验证器、评分器、工具、沙箱、预算、超时及中止策略。
5. **计算与状态**：精度、并行、权重同步、旧概率、随机状态、checkpoint 与停止条件。
6. **证据与验收**：开发集和最终测试分开；固定 harness，检查非目标能力和成本。

只复制学习率会遗漏这些接口。只保留最终权重也不能说明训练数据、采样轨迹和奖励怎样产生。只对同一个奖励模型换一批问题，不自动得到独立质量证据。

## 与其他细分方向怎样衔接

这里的 LLM 例子以 token 动作为基础；[扩散模型 RL](../diffusion/02-rl-through-denoising.md)还涉及连续去噪路径和不同的 likelihood／匹配目标，不能直接互换实现。

[推理硬件](../diffusion/05-gpu-and-memory-roofline.md)帮助理解吞吐与内存，而训练合同还要考虑反向、状态与 rollout。[自动研究](../diffusion/04-autoresearch-and-oracles.md)可以搜索候选配方，却仍需固定正确性验收。[权重编辑](../weight-space-programming.md)则需要另一套权限与副作用检查。

## 建议路线与执行边界

30 分钟先读 Rufus-Air 总览和每章自测；90 分钟按四章顺序阅读；半天完成标准库实验，并填写一页复现合同。这里的“半天”不是训练大型 MoE 所需时间。

本次不运行真实模型训练，不下载权重，不采购算力，不调用付费评分器。公开框架、公开数据和论文配方分别核验；不把“开放”解释为所有专用补丁、环境和模型产物已完整公开。
