# Rufus-Air：一手来源、版本与复现边界

研究日期：2026-11-03。[配方总览](README.md)。

本页记录实际读到的证据，不将预印本、公开框架和团队产物混成一个“下载即复现”的包。正文分别标注作者报告、背景机制、教学推导与工程建议。

<a id="paper-metadata"></a>

## 1. 精确论文与访问状态

用户链接末尾带中文逗号，本次以 arXiv ID **2609.29421** 定位，未将标点当成 ID 的一部分。官方 API 返回最新版为 v2，与官方摘要页一致。

| 字段 | 核验内容 |
| --- | --- |
| 标题 | Rufus-Air: An Open LLM Post-Training Recipe |
| 作者简记 | Chia-Yuan Chang、Renyuan Cheng、Rui Feng 等 22 位；完整列表见官方页，同名 Zixuan Zhang 两位为不同作者 |
| 年份／类型／venue | 2026；arXiv 预印本；本次未确认正式会议／期刊发表 |
| arXiv | [2609.29421v2](https://arxiv.org/abs/2609.29421v2) |
| 首次公开／本次版本 | 2026-09-24／2026-09-25 |
| DOI | 10.48550/arXiv.2609.29421，为 arXiv-issued DOI，不自动证明同行评审 |
| 全文状态 | 公开 [PDF](https://arxiv.org/pdf/2609.29421v2) 与 [HTML](https://arxiv.org/html/2609.29421v2) 可访问；API 标注 48 页 |
| 引用数 | 未查询，不用未核引用数排名 |
| 来源平台与读取日期 | arXiv 官方摘要、Atom API、公开全文；2026-11-03 |
| 许可记录 | 摘要页显示 arXiv perpetual non-exclusive license；本 Wiki 不转载全文、原曲线或截图 |

## 2. 分章实际读取范围

| 本 Wiki 的章节 | 论文重点 | 补充证据 |
| --- | --- | --- |
| 总览 | §2、§6；八阶段、起点与顺序边界 | GLM-4.5-Air-Base 模型卡 |
| 数据／SFT／RLVR | §3.1–3.3、附录 C／D | 数据卡、Math-Verify、Reasoning Gym、LiveCodeBench 文档 |
| Agentic 环境 | §3.5–3.7、§4.2、附录 F | Slime 与 SGLang 的 token／mask 接口、Strands 事件 |
| 奖励与稳定性 | §3.4、§3.8、§4.1、§6 | Slime R3／checkpoint 代码、Tülu 3、奖励过优化论文 |
| 工程与评测 | §4、§5、§6；附录 C／E／F／G 的相关部分 | Slime、SGLang、Firecracker 官方说明 |

不是每条参考文献都已精读，也未逐项审计作者全部 benchmark。分章的固定源码 URL 是机制核验快照，不冒称它们都等于作者训练时的完整构建。

## 3. 上游组件与模型入口

| 一手来源 | 阅读用途 | 本次未做 |
| --- | --- | --- |
| [GLM-4.5-Air-Base 模型卡](https://huggingface.co/zai-org/GLM-4.5-Air-Base) | base／chat 区别，总／激活参数 | 不下载权重、运行 inference |
| [模型配置](https://huggingface.co/zai-org/GLM-4.5-Air-Base/blob/main/config.json)／[张量索引](https://huggingface.co/zai-org/GLM-4.5-Air-Base/blob/main/model.safetensors.index.json) | 当日元数据：额外预测层与约 220.94 GB 的 `total_size` | 只读小型 JSON，不下载张量；不是实际运行显存 |
| [THUDM Slime](https://github.com/THUDM/slime) | 训练、rollout、数据接口；分章另固定部分源码 | 不安装或运行，不推断专用补丁全部存在于 main |
| [SGLang](https://github.com/sgl-project/sglang) | serving 与 token 请求／返回接口 | 不运行服务，不核验整个 binary stack |
| [Strands Agents](https://strandsagents.com/) | 代理循环与 hook 机制 | 不部署 Rufus-Gym，不混用版本 API 名称 |
| [Firecracker](https://firecracker-microvm.github.io/) | KVM microVM 与隔离模型 | 不部署、安全测试或实测启动时间 |
| [E2B 官方开源运行时](https://github.com/e2b-dev/infra) | 论文指向的上游入口 | 只记录链接，未审计完整仓库 |

最后一行仅作入口记录，不作本课独立证明的依据。数据卡的字段、来源与限制详见 [01 来源](data-sft-and-rlvr.md#public-sources)；本文不提供法律许可结论。

<a id="reproduction-boundaries"></a>

## 4. 三个复现等级与缺口

**已完成的第一级：教学机制。** 验证小规模计数、mask、采样 token 合同、失败分类和协议比较；这些没有模型权重、GPU 或外部服务依赖。

**未完成的第二级：局部模型阶段。** 还需要选定小模型、数据处理、参考策略、实际 reward、环境及资源预算；不能把修改学习率后启动框架称为复现 Rufus-Air 的阶段。

**未完成的第三级：完整作者流水线。** 需逐项补齐：

- 各阶段起始与选定 checkpoint、数据版本、去污染与筛选输出。
- 容器、上游 commit、build-time patches、精度与并行配置。
- Rufus-Slime／Rufus-Gym 的适配与环境模板、tool schema、token 记录和中止规则。
- 权重、optimizer／scheduler／RNG／采样进度的交接策略。
- 训练 reward、开发选点、最终测试各自的 judge、题集、预算与聚合。
- 工具错误如何计分／重试，Search 的评测日期窗口、locale、泄题域名过滤及实时网页错误处理；同名 harness 也未必是参考实现。
- 长轨迹沙箱、搜索、评分服务的授权、成本与停止条件。

本次在官方论文链接及所读上游入口中，**没有核验到一个涵盖所有这些产物的专用 Rufus-Air 仓库或最终权重发布包**。这不是宣称它们永远不存在，而是不能把未核验状态写成已确认公开。作者“open recipe”的主张与我们的实际产物核验范围分开。

## 5. 怎样阅读作者配置与成绩

附录 C 表 15／16 为软件与超参数入口，本课只摘取少量用于讲单位和机制的事实，不复制整张配置表。节点、每题候选、更新次数、单轮与整轨迹长度是不同维度。

headline、相邻阶段、开发监控和外部报告列也属于不同测量。原文明确一部分阶段表协议不同，以及没有统一 benchmark 全阶段跟踪；不要凭图表位置相邻就作差、归因或制作统一排名。

论文里工具／服务价格是作者报告时的案例，不是本次实时价格调研；本课没有报价、采购或支付。

<a id="public-sources"></a>

## 6. 本 Wiki 的原创与未执行项

配图均为本地机制重画；教学数组、候选数、角色 mask 和协议冲突案例为原创。示例代码只用 Python 标准库，测试范围不包含真实 tokenizer、梯度、MoE 网络或并行运行。

未下载论文图件、数据集和权重，未安装训练栈，未训练／重跑 benchmark，未部署沙箱，未调用付费模型或检索服务。每个“作者报告”都不能据此升级为本 Wiki 的独立实验结论。
