# Unified Training：一手来源、固定快照与未执行项

研究日期：2026-11-04。只记录公开材料。原文是 *Training Foundation Models with a Single Algorithm*，不是整个基础模型领域已经完成统一的公告。

## 1. 论文与作者材料

| 材料 | 核验内容 | 边界 |
| --- | --- | --- |
| [arXiv 摘要](https://arxiv.org/abs/2610.40564) | v1，2026-10-29，作者与 67 页报告元数据 | 不宣称会议录用或以后修订 |
| [论文 v1 HTML](https://arxiv.org/html/2610.40564v1) | 目标分布、有限 N、token 归约、实验、计算与附录 | 结果归属于作者，不是本 Wiki 实测 |
| [项目页](https://yudasong.github.io/unified-training/) | 研究定位、图解、代码与模型入口 | 不复制整页插图或整张排行榜 |
| [作者 GitHub](https://github.com/yudasong/unified-training) | 默认分支为 `release`，实现与运行入口 | 有代码不等于依赖、语料和运行条件已复现 |
| [模型发布](https://huggingface.co/sfanm/unified-training) | 受控／real-world 产物入口 | 未下载、未运行、未验证性能 |
| [数据发布](https://huggingface.co/datasets/sfanm/unified-training) | 作者发布的数据入口 | 未获取全库、未审计许可与污染 |

## 2. 本次读取的公共实现

以下 URL 固定到本次检查的提交，不把可变分支当作永久证据。

- [README](https://github.com/yudasong/unified-training/blob/5b3eaa0f3ce39f695beb5d27a0bb0f92368b3118/README.md)：分离的训练、评测、NeMo-RL 环境，运行脚本、checkpoint 与数据入口。
- [配置合同](https://github.com/yudasong/unified-training/blob/5b3eaa0f3ce39f695beb5d27a0bb0f92368b3118/docs/configuration.md)：loss norm、响应保留、调度、policy age 与默认值／论文值差异。
- [`rollout_common.py`](https://github.com/yudasong/unified-training/blob/5b3eaa0f3ce39f695beb5d27a0bb0f92368b3118/src/unified_training/rollout_common.py)：`weight_groups`、零权重、过滤、有限样本 pass@k 与响应保存。
- [`hf_trainer.py`](https://github.com/yudasong/unified-training/blob/5b3eaa0f3ce39f695beb5d27a0bb0f92368b3118/src/unified_training/hf_trainer.py)：`loss_denominator`、`weighted_ce_sums`、采样支持、全局归一化与 separate loss。
- [policy shard 加载](https://github.com/yudasong/unified-training/blob/5b3eaa0f3ce39f695beb5d27a0bb0f92368b3118/src/unified_training/policy_weights.py)：已发布权重的 CPU 读取方式，不是奖励权重的计算模块。
- [freshness guard](https://github.com/yudasong/unified-training/blob/5b3eaa0f3ce39f695beb5d27a0bb0f92368b3118/src/unified_training/rollout_freshness.py)：完成批次、生成器 rank、策略版本与进度检查；已读这些入口，不等于审计全部 buffer 行为。
- [受控配置](https://github.com/yudasong/unified-training/blob/5b3eaa0f3ce39f695beb5d27a0bb0f92368b3118/experiments/controlled/configs/common.env)：论文响应 token 分母、零权重保留、无基线与严格年龄设置。
- [real-world 配置](https://github.com/yudasong/unified-training/blob/5b3eaa0f3ce39f695beb5d27a0bb0f92368b3118/experiments/realworld/configs/common.env)：16 回答、512 RL rows、12,000 updates、发布与混合设置。
- [real-world 复现说明](https://github.com/yudasong/unified-training/blob/5b3eaa0f3ce39f695beb5d27a0bb0f92368b3118/experiments/realworld/README.md)：硬件变化会改变速度和策略年龄；基础 midtraining 语料不全部包含在发布中。

`episodes.py`、`dataset.py`、`corpus_mix.py` 在正文作为进一步阅读入口，不能因列出名字就宣称已做完整代码审计。读代码的指定函数也不等于运行过测试或安装过上游包。

## 3. 本 Wiki 的原创部分

机制图由本地清单生成，提供 SVG 与 2× PNG；没有重画论文数值曲线冒称新结果。条件分布 `(0.75,0,0.25)`、四回答权重、3.2／8／2 分母、80%／20% 抽样、四条调度面积和 1,020,000 FLOPs 均为原创教学例。

标准库程序只计算小概率、计数与有限数组，不实现语言模型、autograd、DDP、buffer 服务、tokenizer、真实 verifier、GPU trainer 或 TailRL。测试通过仅说明这些教学约定和反例正确。

## 4. 尚未执行或验证

未下载模型权重或训练全库，未启动真实训练、调用模型／judge API、执行模型生成代码、重跑 benchmark、重算论文保存结果或采购算力。没有审计全量去污染、第三方许可适用性、硬件速度或任意规模迁移。

论文的成功条件分布是目标构造，固定目标与 stale generator 仍需区分；有限样本有偏差，真实 token／算力比例要测量。理论、公开实现与结果应分别核验，不彼此替代。

网页已整理与模型已复现是两个状态。返回[导读](README.md)；读[证据与局限](evidence-and-limits.md)、[离线实验](lab.md)。
