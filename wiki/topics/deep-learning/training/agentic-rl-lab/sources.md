# Agentic-RL Lab：源码快照、研究证据与未执行项

研究日期：2026-11-03。[读本导读](README.md)。

## 1. 核验对象与公开许可

本次对象是 **datawhalechina/agentic-rl-lab**，不是同名第三方 fork。以[固定源码树](https://github.com/datawhalechina/agentic-rl-lab/tree/8493321013c02eef6cf79ca2594811f53c6fdac1)为准；本次读取时默认分支为 main，该版本提交日期为 2026-11-02。正文的源码链接均固定到此版本，不把未来 main 的变化归入本次核验。

仓库声明 [Apache-2.0](https://github.com/datawhalechina/agentic-rl-lab/blob/8493321013c02eef6cf79ca2594811f53c6fdac1/LICENSE)。这是仓库许可证记录，不代表远程服务、模型、全部数据、第三方 prompt 与派生结果自动共享同一许可。执行前分别检查使用条件；本文不作法律结论。

[实验目录](https://github.com/datawhalechina/agentic-rl-lab/blob/8493321013c02eef6cf79ca2594811f53c6fdac1/experiments/README.md)列出 16 个入口；README 的宣传、资源消耗和曲线是作者材料。本读本没有独立重跑它们，也没有用 star 数、宣传语或一张曲线作为算法优越性的证明。

## 2. 分章实际检查的代码

| 本章 | 固定源码目录／文件 | 核验目的与限制 |
| --- | --- | --- |
| 导读／复现 | README、`pyproject.toml`、实验 `start.md` | 目录、版本、远程训练与依赖；未安装训练栈 |
| 01 优化 | `grpo/03-grpo.py`、`02-demo-async.py`；`dapo/{train,rollout,reward}.py`；`gspo/{train,rollout,loss}.py` | 优势、clip、detach、归约、动态采样；未核验远端梯度内核 |
| 02 环境 | `search-r1`、`retool`、`alfworld` 的 protocol／rollout／environment／reward | 行动、观察、解析、mask、工具与状态；未调用外部服务或运行生成代码 |
| 03 蒸馏 | `general-opd`、`medical-opd`、`opsd`、`agentopsd` | teacher、采样、反馈与 student 更新；未实测模型能力 |
| 04 credit | `alfworld/advantages.py`；`agentopsd/{advantages,teacher,loss}.py`；`tempo/{states,critic,tempo}.py` | trajectory／turn／macro-step 信号；未重跑环境或 critic |
| 05 应用 | `vision-grpo`、`spec-o3`、`pytrio-jev`、`tournament-grpo` 的训练／评测模块 | 模态、SFT／RL、校准、比赛奖励；不构成领域部署验收 |
| 06 评测 | 各目录 eval／data／start 及环境配置 | 分离模型、harness、预算与失败策略；不是完整安全审计 |

具体结论的支持文件直接链接在各章旁边。本次不是逐行审计所有依赖、所有脚本和整个锁文件，也不是模型服务的兼容性验收。Python 源码可读、安装解析成功、模型 API 运行成功、论文成绩复现是四个不同里程碑。

## 3. 背景论文：原算法与教程实现分开

以下三项以 arXiv 官方记录核对标题、首位作者、年份、版本，并阅读相关 HTML 章节；引用数未查询，不据此排名。均按预印本来源记录，不额外宣称已核验正式 venue。

| 标题／作者简记 | 版本与年份 | 本次读取范围 | 全文入口 |
| --- | --- | --- | --- |
| DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models；Zhihong Shao 等 | [2402.03300v3](https://arxiv.org/abs/2402.03300v3)，2024 | §4 GRPO 与结果级奖励 | [HTML](https://arxiv.org/html/2402.03300v3)；官方页提供 PDF |
| DAPO: An Open-Source LLM Reinforcement Learning System at Scale；Qiying Yu 等 | [2503.14476v2](https://arxiv.org/abs/2503.14476v2)，2025 | §2–3，原始目标与四项改进 | [HTML](https://arxiv.org/html/2503.14476v2)；官方页提供 PDF |
| Group Sequence Policy Optimization；Chujie Zheng 等 | [2507.18071v2](https://arxiv.org/abs/2507.18071v2)，2025 | §2–4，token／sequence ratio 与目标 | [HTML](https://arxiv.org/html/2507.18071v2)；官方页提供 PDF |

完整作者列表与版本历史以官方摘要页为准。这里没有下载或转载论文图件、整张配置表；所列 HTML 可以公开访问，但没有把“页面存在”写成完整论文实验已复核。

Search-R1、ReTool、TEMPO、AgentOPSD 等更多原论文入口由上游教程提供。**本读本对这些部分的主要独立核验对象是 Lab 教程及源码**，不是宣称已精读并复现所有原论文。若需要做正式研究，应再对照原论文、官方实现和消融；Lab 的模型、数据、服务与预算不能默认等于论文设置。

## 4. 本 Wiki 的原创与真实执行范围

六章组织、机制配图、示例数字、检查表和标准库实验由本 Wiki 编写。配图不复制原论文或上游曲线，不用假数据重画成模型训练成绩。

机制实验测试了 sample-standardized advantage、PPO／CISPO 标量梯度、回答／token 归约、GSPO 几何平均、零目标分母、补采预算和长度 shaping。这里的“梯度”是可验算的标量导数与有限差分，不是模型反向图、SDK custom loss 或真实大网络梯度。

文档测试另检查本地链接、来源版本、搜索、图件、隐私与导航；网页测试检查公式、配图、桌面／手机排版。它们提高教材的正确性，不证明上游训练成功。

## 5. 未执行项与仍需补齐的复现合同

本次没有安装 PyTRIO／ALFWorld 训练环境，没有下载模型权重或训练数据，没有运行模型采样／训练／benchmark，没有调用付费搜索、裁判、teacher 或训练服务。没有把上游的账单截图当成实时价格或给出采购承诺。

进一步局部复现至少需要明确：固定 commit 与服务端版本；模型及 tokenizer；数据 split、处理产物与污染检查；prompt／模态格式；旧概率和 mask；奖励与停止规则；optimizer、权重同步和恢复状态；独立评测与总预算；密钥保护、日志上传和环境隔离。详见 [06 检查表](evaluation-and-reproduction.md)。

服务可用性、套餐、版本兼容、数据下载速度和执行安全性均未实测。若上游以后修订，我们应新建核验日期、说明变更，再更新结论，不静默把旧来源链接替换成浮动 main。
