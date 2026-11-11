# Agent 记忆术语速查

整理日期：2026-11-11。[专题导读](README.md) · [一手来源](sources.md)。下列解释服务于本读本，不是统一标准。

| 术语 | 本读本中的含义 | 不应混成什么 |
| --- | --- | --- |
| Persistent memory | 跨会话保留、以后可读的外部经验 | 权重必定更新 |
| Context | 一次推理当前能看到的信息 | 全部长期状态 |
| Compaction | 压缩轨迹以续接有限窗口 | 保留全部原始证据 |
| Transcript | 当时对话与观察的记录 | 世界真相的绝对保证 |
| Memory note | 从经验中选择保存的笔记 | 不确定推断自动变事实 |
| Representation | Wiki、实体页、索引等组织方式 | 一个数据库产品名称 |
| Injected context | 开始时预装的内容 | 高权限系统配置的同义词 |
| Dreaming | 用额外计算整理、核验与构建表示 | 第五层或必然训练权重 |
| Salience | 信息对未来任务可能重要的程度 | 每条都必须保存 |
| Provenance | 来源与派生关系 | 引用次数或编辑者身份等于真值 |
| Observed at | 证据对应的观察时间 | 文件最后修改时间 |
| Validity condition | 一条经验的适用条件 | 单一 TTL 能表达全部条件 |
| Invalidation | 证据／条件变化后的停用与复核 | 只删根笔记就修复下游 |
| CAS | 比较版本后再接受更新 | 自动裁决语义冲突 |
| Read-only | 禁止某一类写入 | 读取许可和内容可信都已保证 |
| Retrieval recall | 参考信息被找到的比例 | 真实执行成功率 |
| Criteria coverage | 满足多少评分细项 | 全部必要条件同时通过 |
| All-pass | 一题全部必要条件通过 | 与细项平均完全相同 |
| Amortization | 将构建／维护成本摊到查询 | 在线省 token 就必定回本 |
| Memory poisoning | 低信任内容污染持久经验的风险 | 任意特定产品已被证明可攻破 |
| Self-conditioning | 生成时反馈先前预测等状态 | 默认是跨会话 agent memory |

机制见 [01](01-memory-and-state.md)、[02](02-write-manage-read.md)、[03](03-representations-and-retrieval.md)；测量与安全见 [04](04-evaluation-and-ablation.md)、[05](05-safety-and-governance.md)。Dreaming 名称相同的产品、cookbook 与一般过程，仍需检查各自接口合同。
