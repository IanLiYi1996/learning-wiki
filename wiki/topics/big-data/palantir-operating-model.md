# Palantir Operating Model：业务分层、产品架构与 FDE 组织设计

- 调研日期：2026-09-04
- 主题位置：企业软件 / 数据与 AI 平台 / FDE / 组织设计
- 相关主题：[Palantir Ontology](palantir-ontology.md)、[Palantir FDE 与 AI FDE](palantir-fde.md)

## 研究边界

**Palantir 没有公开完整的内部组织架构图、汇报线、账户编制规则或正式 RACI。**

本文不是泄露版 org chart，而是基于以下公开资料重构的 operating model：

- [Palantir 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
- [Palantir Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm)
- 2026-09-04 可访问的 [Palantir Lever 招聘 API](https://api.lever.co/v0/postings/palantir?mode=json)及岗位页
- Palantir 官方角色文章
- Foundry、AIP、Ontology、Apollo 官方文档

全文使用三种证据标签：

- **公开事实**：官方文件或岗位资料直接说明。
- **重构**：多个公开事实组合后得到的 operating model。
- **建议模型**：为了帮助理解而设计的接口、RACI 或检查清单，不代表 Palantir 内部正式名称。

招聘信息描述公司希望角色承担的责任，不等于每个员工的实际时间分配。不同国家、政府与商业客户、
安全等级和项目阶段也会形成不同团队配置。

## 结论先行

Palantir 不是简单的“软件公司加驻场工程师”，其工作模式更接近三个相互咬合的系统：

```text
业务经营系统
政府 / 商业分部 -> 账户级投资与贡献率 -> 获取、采用和扩张

客户交付系统
Sales / BD -> Echo -> Delta + Design -> 专业保障角色 -> 客户自助与扩展

产品研发系统
现场问题 -> 通用原语 -> Foundry / Gotham / AIP / Apollo / Ontology
         -> 再进入更多客户现场
```

最重要的组织设计不是岗位名称，而是三种责任边界：

```text
谁负责找到值得解决的问题？        Echo / Sales / 客户业务负责人
谁负责让生产系统真正工作？        Delta / Design / 专业保障角色
谁负责把重复需求变成通用产品？    Dev / Product Engineering
```

**重构结论：** Palantir 同时使用三种不同的管理粒度，不能把它们混为一张树状组织图：

1. **财务粒度是业务分部**：Government 与 Commercial。
2. **经营粒度是客户账户**：按账户决定前期投入、交付成本和扩张机会。
3. **研发粒度是产品能力**：小型产品团队长期拥有可复用的平台能力。

FDE 模式把账户现场和产品能力连接起来。一个健康的部署不是“替客户长期写定制软件”，而是：

```text
用通用平台快速解决一个高价值问题
  -> 在现场发现产品缺口
  -> 只对客户特殊部分做有限扩展
  -> 将重复模式沉淀为平台能力
  -> 让后续部署更快、更稳定、更少依赖人力
```

## 一张总图

以下是本文对 Palantir operating model 的公开资料重构：

```text
                                Palantir 公司
                                      |
                 +--------------------+--------------------+
                 |                                         |
         Government segment                         Commercial segment
       政府采购、任务与合规                         企业采购、运营与 ROI
                 |                                         |
                 +--------------------+--------------------+
                                      |
                           Account portfolio management
                    按客户账户评估长期价值、投入和扩张机会
                                      |
               +----------------------+----------------------+
               |                                             |
       Sales / BD / Deal Team                         Account mission team
  机会、关系、采购、定价、合同               围绕具体任务动态组装，不是固定部门
                                                             |
                          +-------------+-------------+-------+--------+
                          |             |             |                |
                     Echo / DS      Delta / FDE     Design      FD specialists
                    问题与采用       技术与交付      用户体验     AI/Infra/SRE/
                                                                Security/Enablement
                          \             |             /                /
                           +------------+-------------+---------------+
                                             |
                                  Customer production workflow
                                             |
                     +-----------------------+-----------------------+
                     |                                               |
              Adoption / expansion                         Field feedback / gaps
                     |                                               |
                     +-----------------------+-----------------------+
                                             |
                                  Dev / Product Engineering
                         通用原语、平台能力、可靠性、产品路线图
                                             |
              +----------------+-------------+-------------+----------------+
              |                |                           |                |
           Gotham           Foundry                       AIP             Apollo
         任务操作系统     数据与运营平台              AI/Agent 层       软件交付层
              \                |                           /                /
               +---------------+----------+---------------+----------------+
                                          |
                                      Ontology
                          数据 + 逻辑 + 动作 + 安全的操作语义层
```

这里的 `Account mission team` 是**重构概念**。公开岗位反复说明 FDE、Deployment Strategist、
Product Designer 和其他工程师组成小团队解决客户问题，但 Palantir 没有公开宣布一个统一名为
“account pod”的正式全球组织单元。

## 一、业务分层：分部管理，账户经营

### 1. 两个业务分部

**公开事实：** [Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm)
披露 Palantir 有两个 operating segments：

| 分部 | 主要客户 | 典型差异 |
| --- | --- | --- |
| Government | 美国及非美国政府机构 | 采购周期、预算、合同退出权、安全许可、ATO 和任务环境 |
| Commercial | 非政府行业客户 | 企业预算、ROI、采用速度、业务扩张和行业竞争 |

这两个分部由 CEO 作为 chief operating decision maker 用于资源配置和绩效评估。
分部的划分依据包括客户类型、组织结构和管理报告结构。

截至 2026 年第二季度：

- 2026 上半年收入中，Government 占 52%，Commercial 占 48%。
- Q2 Government 收入约 9.90 亿美元，Commercial 收入约 9.45 亿美元。
- Q2 Government contribution margin 为 71%，Commercial 为 78%。
- 2026 上半年 Government contribution margin 为 72%，Commercial 为 75%。

Palantir 的 contribution margin 是收入减去与账户相关的 cost of revenue 和 sales and marketing
成本后再除以收入，并排除股权激励。它还不包含统一管理的 R&D 和 G&A，因此不能直接等同于
完整客户利润。

### 2. 分部不是完整的日常组织图

**重构：** Government / Commercial 更像顶层经营和财务切分，而不是所有人的唯一汇报线。

公开招聘中同一个客户任务可能同时需要：

- Echo 团队的 Deployment Strategist。
- Delta 团队的 FDE 或 Forward Deployed Infrastructure Engineer。
- Design 团队的 Product Designer。
- Product Development 的 Reliability Engineer。
- Business Development 分类下的 Security Engineer。
- Dev 团队的产品工程师。

因此，真实工作更像矩阵：

```text
客户/市场轴：Government <-------------> Commercial
产品能力轴：Gotham / Foundry / AIP / Apollo / Ontology
角色专业轴：Sales / Echo / Delta / Design / Dev / Specialists
任务阶段轴：Pilot -> Production -> Adoption -> Expansion
```

一个人可能属于某个职能团队，但在一个时期内围绕特定客户和任务协作。

### 3. 账户是核心经营单元

**公开事实：** [2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
和 [Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm)
都明确表示，Palantir 按 **account level** 管理客户，而不是按行业或 sector 管理每个客户关系，
以便针对每个账户的增长机会优化投入。

账户级管理体现在：

- 收入直接分配到客户账户。
- 部署、运行、获客和扩张成本按账户分配。
- 与现有客户合作的软件工程师可能同时负责平台运行和发现新用途。
- 管理层根据软件可为该客户产生的长期价值，改变是否继续投入的判断。

这解释了 FDE 为什么同时具有工程、交付和扩张属性：其成本和成果都落在账户经济中，而不是只落在
产品研发成本中心。

### 4. 账户经济不是标准低接触 SaaS

截至 2026-06-30，Palantir 披露有 1,049 个客户；过去十二个月前 20 大客户的平均收入为
1.24 亿美元，同比增加 67%。这些数字来自
[Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm)。

**重构：** 这是一种“高账户价值支撑高接触交付”的经济结构：

```text
高价值、复杂账户
  -> 值得投入跨职能小队和前期试点
  -> 先解决最关键任务建立信任
  -> 横向扩展到更多部门和用例
  -> 纵向扩展到更多用户和操作层级
  -> 单账户收入增长吸收前期投入
```

[2025 Form 10-K 的 Account Growth 部分](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
将增长路径描述为：

- 向客户的合作伙伴和供应商生态延伸。
- 销售更多产品化、跨行业能力。
- 针对具体 use case 部署战略性软件实现。
- 在同一机构内横向扩展到更多部门和职能。
- 纵向扩展到更多用户和用户组。

它与“每个席位按月收费、低成本在线获客”的 SaaS 模型明显不同。

### 5. 前期投资与不确定性

**公开事实：** Palantir 会自费或低价运行 pilots 和 AIP Bootcamps，而且不能保证它们转化为长期收入。
[2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
称 Bootcamp 可以在真实客户数据上于数日内交付真实工作流，同时在风险披露中说明这些初始部署
可能只产生很少收入，甚至没有后续收入。

这使账户选择成为重要决策：

```text
问题价值是否足够大？
客户是否有真实数据和决策权？
首个工作流能否进入生产而不只停在 demo？
平台是否能扩展到更多部门和用户？
本次定制是否可能沉淀为通用能力？
```

## 二、产品分层：不是五个独立产品，而是一个操作系统组合

### 1. 官方产品关系

**公开事实：** [2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
列出四个 principal software platforms：Gotham、Foundry、Apollo 和 AIP。

同一文件说明：

- Gotham 与 Foundry 都是客户的 central operating system，但面向的任务和具体功能不同。
- AIP 为 Gotham 与 Foundry 提供集成的 AI 架构。
- Apollo 支撑平台在多种环境中的持续交付和运行。
- Ontology 位于平台核心，将数据、逻辑和动作组织成决策架构。

[Foundry 平台概览](https://www.palantir.com/docs/foundry/platform-overview/overview/)
进一步把架构描述为：

```text
顶部：预构建和自定义 AI 产品
中部：AIP + Foundry，包括 Ontology、核心服务、安全与治理
底部：Apollo 软件交付层
```

因此，Ontology 不是与四个平台并列的第五个 SKU，而是横跨 Foundry、AIP 及相关操作流程的核心抽象。

### 2. 分层视图

| 层 | 产品或能力 | 主要职责 | 组织含义 |
| --- | --- | --- | --- |
| 任务与行业应用层 | Gotham、行业应用、AIP Now、自定义应用 | 让具体用户执行任务 | Echo、FDE、Design 最接近此层 |
| AI 与自动化层 | AIP | 模型连接、Agent、Logic、Evals、人机协作 | FD AI 与 AIP 产品团队连接现场和平台 |
| 运营数据层 | Foundry | 数据集成、转换、分析、模型和应用开发 | FDE 构建客户工作流，Dev 构建通用原语 |
| 语义与动作层 | Ontology | 对象、关系、逻辑、Action、权限和审计 | 把业务语言变成应用与 Agent 的正式接口 |
| 软件交付层 | Apollo | 跨云、on-prem、edge 的发布、升级和配置 | Infra、SRE、Reliability 保障生产运行 |
| 横切治理层 | Security、permissions、branching、audit | 控制谁能看、改、发布和执行 | Security、客户控制人和平台治理共同负责 |

### 3. Gotham

[2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
将 Gotham 描述为面向国防、情报和其他政府任务的操作系统，整合多域数据与传感器，支持从分析、
态势感知到行动计划和执行的交接。

组织上，Gotham 场景通常提高以下角色的重要性：

- 具备安全许可的 FDE、DS 和基础设施工程师。
- Forward Deployed Security Engineer。
- Tactical edge、断网环境和特殊硬件工程能力。
- 政府采购、审计和授权人员。

### 4. Foundry

[Foundry 官方概览](https://www.palantir.com/platforms/foundry/)和
[Foundry 平台文档](https://www.palantir.com/docs/foundry/platform-overview/overview/)
将 Foundry 定位为数据 operations platform：连接数据、逻辑、分析和业务工作流。

它是大多数 FDE 客户交付的通用工程底座：

- 接入和转换数据。
- 训练或接入模型。
- 构建 Ontology。
- 开发应用与工作流。
- 配置权限、审计与发布流程。

### 5. AIP

[AIP 官方文档](https://www.palantir.com/docs/foundry/aip/overview/)
说明 AIP 将 AI 连接到组织的数据和 operations，并在 Ontology 和开发工具链上提供 Logic、
Agent、Evals 和 AI 应用能力。

组织上，AIP 不消除 FDE，反而新增了接口责任：

- 业务问题是否适合模型或 Agent。
- 模型输出如何进入受控 Action。
- 哪些步骤需要人工审批。
- 如何做评估、回归测试、监控和成本控制。
- 谁承担错误决策和外部副作用的责任。

[Forward Deployed AI Engineer](https://jobs.lever.co/palantir/636fc05c-d348-4a06-be51-597cb9e07488)
负责与客户共同拥有 GenAI 战略和实现，构建端到端工作流、推进生产，并将现场经验反馈给 AIP 产品。

### 6. Apollo

[2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
和 [Apollo 官方页面](https://www.palantir.com/platforms/apollo/)
将 Apollo 定位为跨云、on-prem 和 rugged edge 环境的软件交付与控制层，负责持续发布、
安全更新和配置管理。

Apollo 在 operating model 中承担“产品复用能够抵达复杂环境”的关键作用：

```text
Dev 构建通用平台版本
  -> Apollo 管理多环境发布与升级
  -> Infra / Reliability 处理环境差异和生产信号
  -> 现场不必永久维护一套脱离主干的客户分叉
```

### 7. Ontology

[Ontology 官方概览](https://www.palantir.com/docs/foundry/ontology/overview/)
把 Ontology 定义为数据、模型和其他数字资产之上的 operational layer，包括对象、属性、关系，
以及 Actions、Functions 和动态安全。

Ontology 同时也是客户团队和 Palantir 团队之间的“业务接口契约”：

```text
客户领域语言
订单、供应商、设备、任务、患者
               |
               v
Ontology
对象、关系、状态、规则、权限、可执行动作
               |
      +--------+--------+
      |                 |
人类应用与工作流      AI Agent 与自动化
```

它降低了每个应用重复解释数据库表和业务规则的成本，但会把领域建模质量变成整个部署的关键约束。

## 三、FDE 概念下的组织结构分层

Palantir 的公开角色更适合用“责任层”理解，而不是传统上下级层级。

### 1. 商业与账户层：Sales / BD / Deal Team

[Sales 岗位](https://jobs.lever.co/palantir/24060586-7ba8-47c0-bfc1-f1dd5b82d8bd)
负责新客户和扩张机会，从初次沟通、机会评估、采购流程推进到企业合同关闭，并承担明确销售指标。

[Deal Team - Business Affairs](https://jobs.lever.co/palantir/16a1b500-13fe-4c22-ad89-372093b462da)
负责与 Sales、Legal、Finance 和 Engineering 合作设计定价、商务条款、合同结构、续约和 upsell。

该层的核心责任是：

- 选择和进入账户。
- 建立采购和高层关系。
- 让价值主张、范围、价格和合同一致。
- 防止前线团队在没有商业边界时无限扩张。

它不应单方面决定生产架构、业务规则或产品路线图。

### 2. 问题与采用层：Deployment Strategist / Echo

[Deployment Strategist 岗位](https://jobs.lever.co/palantir/e0ab8226-b928-4e3a-bf87-08fe7b1ea595)
属于公开招聘中的 Echo 团队，职责包括：

- 进入客户现场理解关键问题和用户痛点。
- 确定相关数据集。
- 与 FDE 建立稳定、可扩展的数据管道。
- 为新用户群构建工作流。
- 培训用户并推动真实采用。
- 向分析师和 C-level 汇报结果和后续方案。
- 将现场观察带回 Software Engineering 和 Product Design。

官方员工文章
[A day in the life of a Deployment Strategist](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-deployment-strategist-951cb59a5a96)
也显示 DS 的技术深度差异很大，有的人偏工作流、组织和采用，有的人会大量编码。

**重构：** Echo 的 primary ownership 更接近“问题是否值得解决，以及结果是否真的被使用”，而不是
“某段代码是否按规格完成”。

### 3. 技术交付层：FDE / FDSE / Delta

[Forward Deployed Software Engineer 岗位](https://jobs.lever.co/palantir/5168e8fd-fec1-4fea-b7a1-81bdaea65850)
属于 Delta，明确将 FDE 描述为直接嵌入客户、以小型高信任团队端到端拥有高风险项目：

- 与工程师共同做架构和设计决策。
- 处理超出原有假设的数据规模。
- 构建定制应用、LLM 工作流和生产方案。
- 管理从一线用户到高管的关系。
- 从第一次客户对话负责到改变客户实际操作的软件上线。

[A day in the life of an FDSE](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1)
展示了管道、数据模型、权限、代码评审、生产监控、故障调查和客户协作的混合工作。

**重构：** Delta 的 primary ownership 是“解决方案能否在真实约束下进入并留在生产”。

### 4. 用户与工作流层：Product Design

[Product Designer 岗位](https://jobs.lever.co/palantir/2d8b7eaa-5c08-44ef-a0f0-5a96cee2794d)
说明 Design 负责软件的人类使用体验，覆盖早期概念、用户研究、交互、原型和视觉设计，并与产品工程师和
forward deployed engineers 共同实现工作流。

Design 在 mission team 中不只是“美化界面”，而是负责：

- 操作流程是否符合用户现实。
- 复杂决策是否能被正确理解。
- 权限、异常、审批和不确定性如何呈现。
- 一个现场工作流能否抽象成可复用交互模式。

### 5. 平台产品层：Dev / Product Engineering

[Backend Software Engineer - Application Development](https://jobs.lever.co/palantir/ab7e3425-81d5-4705-a7b5-cd60c8a45cdb)
说明 Product Development 由小型软件工程团队组成，每个团队聚焦产品的一个方面，构建跨职能能力、
通用工作流、API 和可靠的系统原语。

[Dev versus Delta](https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87)
提供了最有用的经典边界：

```text
Dev
围绕一个产品能力服务许多客户，长期拥有通用平台。

Delta
围绕一个客户结果组合许多产品能力，并在现场扩展边界。
```

该边界并非完全封闭。当前产品工程岗位还描述了 Frontline 短期嵌入机制，让产品工程师进入客户现场，
再把观察带回产品开发。

### 6. AI 专业层：Forward Deployed AI

[Forward Deployed AI Engineer](https://jobs.lever.co/palantir/636fc05c-d348-4a06-be51-597cb9e07488)
同时承担 AI strategy、端到端实现、生产化和 AIP 产品反馈。

与普通 FDE 相比，其专业责任更集中在：

- LLM / Agent 任务分解。
- RAG、工具调用和 Ontology 接入。
- 模型评估与回归。
- 人机交接和风险控制。
- AI 成本、延迟、准确率和可解释性。

它仍然是 mission team 的工程角色，不是脱离客户结果的模型研究岗。

### 7. 基础设施层：Forward Deployed Infrastructure

[Forward Deployed Infrastructure Engineer](https://jobs.lever.co/palantir/0fccbe95-2520-4df3-8600-7897656c06a2)
负责：

- 部署和升级 Palantir 产品。
- 监控、告警、配置和迁移。
- 生产故障排查。
- 自动化 runbook 和手工操作。
- 使用 Foundry 与 Apollo 解决基础设施问题。

其接口位置是：

```text
客户环境约束 <-> Apollo / 平台发布能力 <-> 应用和数据工作流
```

### 8. 可靠性层：Forward Deployed Reliability

[Forward Deployed Reliability Engineer](https://jobs.lever.co/palantir/5a99fe16-1bda-4313-ace2-a11ea6e58f0c)
负责 mission-critical workflow 的稳定性，通过 on-call 获取现场信号，先恢复服务，再推动产品、工具和流程改进。

这个角色体现了 field-to-product 的另一个通道：

```text
生产事故
  -> 根因和重复模式
  -> 自动化、文档和最佳实践
  -> 平台或工作流改进
  -> 更多账户共享可靠性收益
```

### 9. 安全与授权层：Forward Deployed Security

[Forward Deployed Security Engineer](https://jobs.lever.co/palantir/22053072-4c22-49c4-8299-28e107ceeb98)
同时理解网络安全和美国政府政策，直接拥有 ATO 流程，将 NIST 等监管语言转化为工程要求、证据和安全架构。

安全角色的责任不是“最后上线前签字”，而是尽早约束：

- 系统边界和数据流。
- 身份、访问、加密和审计。
- CI/CD 合规控制。
- 证据生成和评估。
- 客户与 Palantir 各自承担的风险。

### 10. 客户成功与规模化层：Forward Deployed Enablement

[Forward Deployed Enablement Engineer](https://jobs.lever.co/palantir/00c2c97b-8514-4617-9883-e53e486b6dcd)
嵌入集中式 Customer Success，帮助商业客户开发团队在 Foundry 和 AIP 上独立构建、优化和排障，
同时开发支持工具，把一对一帮助转化为可规模化 enablement。

它是从“高接触部署”走向“客户自助”的重要组织接口：

```text
FDE 交付首个高价值工作流
  -> Enablement 帮助客户团队掌握平台
  -> 重复问题变成工具、指南和产品改进
  -> FDE 不需要永久驻场
```

## 四、典型 account pod / mission team

### 1. 这是动态矩阵，不是固定编制

**重构：** 一个典型客户任务团队可以画成：

```text
                           Customer executive sponsor
                        预算、优先级、组织变更与风险接受
                                      |
                              Joint mission lead
                     Palantir DS/FDE + 客户业务/技术负责人
                                      |
      +---------------+---------------+---------------+----------------+
      |               |               |               |                |
  Sales / BD       Echo / DS       Delta / FDE      Design      Customer SMEs
 商业边界与采购   问题、采用、价值   架构、代码、生产  用户工作流    规则、数据、操作
      |               |               |               |                |
      +---------------+-------+-------+---------------+----------------+
                              |
           +------------------+------------------+------------------+
           |                  |                  |                  |
       FD AI / ML        FD Infra / SRE      FD Security       Enablement
       AI 与评估         环境与可靠性         授权与合规        客户自助
           |                  |                  |                  |
           +------------------+---------+--------+------------------+
                                        |
                               Dev / Product teams
                     平台缺口、通用原语、版本和长期产品质量
```

团队不会在所有阶段保持同样配置：

| 阶段 | 核心角色 | 按需加入 |
| --- | --- | --- |
| 机会识别 | Sales、DS、客户 sponsor | FDE、Deal Team |
| Bootcamp / pilot | DS、FDE、客户用户与数据人员 | Design、FD AI |
| Production | FDE、客户工程、Infra/Reliability | Security、产品工程 |
| Adoption | DS、Design、客户业务负责人 | Enablement、FDE |
| Expansion | Sales、DS、客户 sponsor | FDE、Deal Team、产品负责人 |
| 稳态运行 | 客户 owner、Enablement、Reliability | FDE、Product Engineering |

### 2. 团队接口比人数更重要

一个 mission team 至少需要回答七个接口问题：

1. **账户接口**：谁有权承诺范围、价格和时间？
2. **业务接口**：谁定义问题、成功指标和操作规则？
3. **数据接口**：谁拥有数据质量、语义和访问授权？
4. **技术接口**：谁对架构、代码和生产质量负责？
5. **产品接口**：什么进入客户配置，什么升级为通用平台？
6. **运行接口**：谁值班、谁处理事故、谁接受剩余风险？
7. **采用接口**：谁负责用户培训、流程改变和业务结果？

如果这些接口不明确，“端到端 ownership”会退化为所有人都以为别人负责。

## 五、生命周期：从 Bootcamp 到产品反馈

### 1. Bootcamp / pilot：证明真实工作流

[2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
称 AIP Bootcamp 在真实客户数据上于数日内交付真实工作流。

典型目标不是完成企业级平台，而是验证：

- 问题是否真实且重要。
- 数据是否可获得。
- Ontology 是否能表达核心对象和动作。
- 用户是否愿意用新工作流。
- 平台是否具备进入生产的技术路径。

该阶段最危险的误判是把 demo 流畅度当成生产价值。

### 2. Production：从可演示到可承担责任

生产化需要补齐：

- 稳定数据管道和数据质量控制。
- 权限、审计和职责分离。
- branch、proposal、code review 和发布策略。
- 性能、容量和成本。
- 监控、告警、on-call、恢复与回滚。
- 模型评估、人工审批和失败模式。
- 外部系统写回的幂等、重试和对账。

[Foundry 开发生命周期文档](https://www.palantir.com/docs/foundry/platform-overview/development-lifecycle/)
与 [Global Branching 文档](https://www.palantir.com/docs/foundry/global-branching/overview/)
展示了通过分支、评审和 proposal 管理跨资源变更的产品机制。

### 3. Adoption：系统被使用才开始产生价值

Deployment Strategist 岗位把培训、广泛使用和 concrete impact 直接列为责任。

采用不是登录人数，而应观察：

- 关键决策是否迁移到新工作流。
- 一线用户是否信任数据和建议。
- 例外情况是否仍绕回 Excel、邮件或口头协调。
- 决策周期、错误率、产能或服务水平是否改变。
- 客户是否形成自己的产品 owner 和工程 owner。

### 4. Expansion：从单一用例到账户平台

[2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
说明 Palantir 通过更多部门、功能、用户组、供应商生态和产品化能力扩展账户。

扩张的健康顺序通常是：

```text
首个关键工作流成功
  -> 相邻流程复用同一数据和 Ontology
  -> 更多用户进入共同操作模型
  -> 新模块的边际交付成本下降
  -> 账户价值和平台粘性增长
```

危险顺序则是：

```text
首个 demo 尚未进入生产
  -> 销售提前承诺多个新用例
  -> FDE 同时维护多个半成品
  -> 客户定制迅速碎片化
```

### 5. Product feedback：现场学习回到平台

**公开事实：** [2025 Form 10-K 的 R&D 部分](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
称 Palantir 通过嵌入用户理解问题，利用跨行业数以万计的 front-line hours 发现研发机会，
改进平台功能、兼容性、可靠性、易用性和性能。

一个完整生命周期是：

```text
Bootcamp / pilot
      |
      v
Production hardening
      |
      v
User adoption and operational result
      |
      v
Account expansion
      |
      v
Recurring pattern extraction
      |
      v
Product primitive / template / platform improvement
      |
      +----------------------> Faster next deployment
```

## 六、field-to-product 飞轮

### 1. 飞轮的两个方向

```text
产品到现场
Dev 构建通用能力
  -> Apollo 分发
  -> FDE 组合
  -> Design 适配用户
  -> DS 推动采用
  -> 客户产生结果

现场到产品
用户阻塞 / 事故 / 重复需求
  -> DS、FDE、Reliability 收集证据
  -> 与 Product Engineering 定义通用问题
  -> Dev 构建原语
  -> 更多账户复用
```

### 2. 哪些内容应该回到产品

适合进入通用产品：

- 多个客户重复遇到的问题。
- 可形成稳定 API、数据类型或操作原语的能力。
- 影响可靠性、安全、升级或开发效率的系统性缺口。
- 能显著减少后续 FDE 工时的工具。
- 可配置而不需要每个客户重写的行业模式。

适合留在账户层：

- 客户独有的流程命名和组织结构。
- 特定数据源映射。
- 客户自有算法和知识产权。
- 临时迁移逻辑。
- 无法证明跨客户需求的特殊 UI 或脚本。

### 3. 产品化的判定

**建议模型：** 对每个现场扩展记录：

| 问题 | 判断 |
| --- | --- |
| 重复性 | 是否至少在多个任务或账户出现？ |
| 抽象稳定性 | 能否定义不泄露客户细节的通用接口？ |
| 运维成本 | 留在客户分支会产生多少升级和支持成本？ |
| 平台位置 | 属于 Foundry、AIP、Ontology、Apollo 还是行业产品？ |
| 迁移路径 | 客户现有实现如何迁移到通用能力？ |
| Owner | 哪个产品团队长期拥有？ |

如果只有“把代码扔给产品团队”，没有产品 owner、迁移计划和采用指标，飞轮不会自动发生。

## 七、决策权、责任与接口

### 1. 公开资料可推导的责任边界

| 决策 | Primary owner | 关键协作者 |
| --- | --- | --- |
| 是否追求账户机会 | Sales / 业务领导 | DS、FDE、管理层 |
| 商务条款与采购 | Sales / Deal Team | Legal、Finance、Engineering |
| 首个任务和成功标准 | DS + 客户 sponsor | FDE、Sales、用户 |
| 技术架构和实现 | FDE | 客户工程、Product Engineering、Infra |
| 用户工作流和交互 | Design + DS | FDE、一线用户 |
| 数据含义与业务规则 | 客户领域 owner | DS、FDE |
| 通用平台原语 | Dev / Product Engineering | FDE、DS、Design |
| 生产发布与环境 | FDE / Infra | Apollo 产品团队、客户运维 |
| 安全授权和风险接受 | 客户授权人 | FD Security、FDE、客户安全 |
| 采用和组织变化 | 客户业务 owner + DS | Design、Enablement、FDE |
| 账户扩张 | Sales + DS + 客户 sponsor | FDE、Deal Team |
| 事故恢复 | Reliability / Infra / 服务 owner | FDE、Product Engineering、客户运维 |

这是**公开资料重构**，不是 Palantir 发布的正式授权矩阵。

### 2. RACI 示例

符号：

- `A`：最终 accountable。
- `R`：直接 responsible。
- `C`：必须咨询。
- `I`：需要知会。

| 活动 | Sales/BD | DS/Echo | FDE/Delta | Design | FD 专家 | Dev/Product | 客户 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 账户资格判断 | A/R | C | C | I | I | I | C |
| Mission charter | C | R | R | C | C | I | A |
| 成功指标 | C | R | C | C | I | I | A/R |
| 数据访问与语义 | I | R | R | I | C | I | A |
| 解决方案架构 | I | C | A/R | C | C | C | C |
| Ontology 模型 | I | C | R | C | C | C | A/C |
| 用户工作流 | I | R | C | A/R | I | C | C |
| 生产就绪 | I | C | R | C | A/R | C | A |
| 安全授权 | I | C | R | I | R | C | A |
| 用户采用 | C | R | C | R | C | I | A |
| 商业扩张 | A/R | R | C | I | I | I | C |
| 产品化决策 | I | C | R | C | C | A | I |
| 生产事故 | I | I | R | I | A/R | C | C |

RACI 必须按账户和阶段调整。例如政府任务中，客户安全授权人和 FD Security 的权重会显著上升；
AI 自动化中，FD AI、模型治理和业务风险 owner 会成为强制参与者。

### 3. 建议性的接口产物

Palantir 没有公开说明所有团队都使用以下文档名称。它们是从公开责任边界推导出的**建议模型**：

| 接口产物 | 解决的问题 |
| --- | --- |
| Account thesis | 为什么值得投入，该账户如何形成长期平台价值？ |
| Mission charter | 首个问题、用户、数据、动作、成功指标和退出标准是什么？ |
| Ontology contract | 对象、关系、状态、规则、权限和 source of truth 如何定义？ |
| Production readiness review | 安全、可靠性、成本、监控、回滚和运维责任是否清楚？ |
| Adoption review | 用户行为和业务结果是否改变？ |
| Expansion memo | 扩展是否复用现有平台，而不是制造新孤岛？ |
| Product gap RFC | 现场缺口为何应该成为通用产品，谁长期拥有？ |

## 八、供应链案例

以下为**说明性案例**，不是某个公开 Palantir 客户的事实复述。

### 场景

一家制造企业经常因关键零件短缺导致订单延期。数据分散在 ERP、供应商门户、物流系统、库存系统和
工厂排产表中。计划员依赖 Excel 和邮件协调。

### 1. Bootcamp

```text
Sales / DS
确定高价值问题：未来 14 天哪些订单可能因缺件延期？

客户领域人员
解释 BOM、供应商承诺、替代料、优先级和排产规则。

FDE
接入订单、库存、采购、运输和生产数据。

Design
与计划员原型化“风险订单 -> 缺件 -> 可选行动”工作流。

FD AI
仅在适合时加入供应商邮件提取或异常解释，不替代确定性库存计算。
```

### 2. Ontology

```text
CustomerOrder
  -> requires -> Part
  -> scheduledAt -> Factory

Part
  -> suppliedBy -> Supplier
  -> heldAs -> InventoryPosition
  -> inboundAs -> Shipment

Actions
  ReallocateInventory
  ExpediteShipment
  SelectAlternatePart
  ChangeProductionSequence
```

Ontology 让应用和 Agent 使用同一组对象、关系、规则和受控动作。

### 3. Production

| 工作 | Owner |
| --- | --- |
| 数据管道、对象模型和应用 | FDE |
| 用户流程与异常状态 | Design + DS |
| 发布环境和升级 | FD Infra + Apollo |
| Action 权限与审计 | FDE + 客户安全 |
| 预测或优化模型评估 | FD AI / 数据科学 + 客户 owner |
| on-call 和故障恢复 | Reliability + 服务 owner |
| 用户培训和流程迁移 | DS + 客户业务负责人 |

### 4. Adoption

不只检查模型准确率，还检查：

- 计划员是否每天在系统中处理风险订单。
- 建议是否转化为受控 Action。
- 操作后是否回写 ERP 或物流系统。
- 订单延期率、加急成本和库存占用是否改变。
- 用户绕开系统时是什么原因。

### 5. Expansion

健康扩张：

```text
订单缺件
  -> 供应商风险
  -> 运输异常
  -> 工厂产能
  -> 客户承诺
```

这些流程复用同一组订单、零件、供应商、工厂和 Shipment 对象。

不健康扩张：

```text
每增加一个部门
  -> 新建独立数据模型
  -> 新写一套权限
  -> 新复制一个应用
  -> 新增长期 FDE 维护负担
```

### 6. 现场反馈回产品

如果多个制造客户都需要“带约束的库存重分配”，现场团队可以把共同需求反馈给产品团队：

- 通用的 supply allocation interface。
- 批量 Action 和审批。
- 冲突检测与 simulation。
- 可解释的优化结果。
- 标准化审计和撤销。

客户特有的 BOM 规则留在账户层，通用动作和交互进入产品层。

## 九、为什么这种模式能工作

### 1. 缩短问题到生产的反馈距离

DS、FDE 和 Design 直接面对用户，不需要经过多层需求转译。错误假设可以在数据、工作流和现场行为中
快速暴露。

### 2. 同一团队看到完整因果链

```text
业务问题
  -> 数据
  -> 模型和规则
  -> 用户决策
  -> 系统动作
  -> 业务结果
```

传统组织经常把这些步骤分散在顾问、数据团队、应用团队、运维和业务部门之间。
FDE 小队至少在早期阶段压缩了这些交接。

### 3. 高价值账户能承担高接触投入

前 20 大客户平均收入和账户扩张数据表明，Palantir 的经济模型可以为重要账户投入更多前线资源。
但这依赖成功扩张，不代表所有 pilot 都有正回报。

### 4. 平台提供共同原语

Foundry、AIP、Ontology 和 Apollo 把数据、语义、应用、AI、治理与交付放在同一产品体系中。
FDE 不必从数据库、权限系统、发布平台和审计系统全部从零搭建。

### 5. 生产责任产生高质量反馈

Reliability、Infra 和 FDE 不只完成上线，还接触升级、事故、性能和安全问题。
这些信号比只做售前 demo 更能指导产品研发。

### 6. 角色允许在模糊环境中快速决策

公开岗位反复强调 autonomy、agency、小团队和 end-to-end ownership。这适合需求无法预先完整定义的复杂任务。

### 7. 当前经济指标与软件复用相容

[Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm)
披露 Q2 gross margin 为 85%，整体 contribution margin 为 74%。

这与“强平台吸收交付成本”的软件经济相容，但不能证明每个账户都已经标准化，也不能忽略 R&D、G&A、
股权激励和失败 pilot。

## 十、何时退化为服务公司

Palantir 在 [2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
中明确区分 product-based model 与 labor-based model。其平台一般以产品化方式提供，而不是为每个客户
编写由客户拥有、持续依赖额外劳务合同的独立软件。

FDE 模式退化的信号包括：

### 1. 人力与收入线性绑定

```text
每增加一个客户
  -> 永久增加一组工程师
  -> 没有共享产品收益
```

如果 FDE 利用率成为主要增长约束，组织更接近专业服务。

### 2. 客户分叉无法升级

- 每个客户维护独立代码分支。
- 平台升级需要大量手工修复。
- Apollo 不能实现统一交付。
- 客户特性长期无法回到主产品。

### 3. 销售承诺压过产品边界

- 为成交承诺缺乏复用价值的功能。
- FDE 被迫完成不可维护的截止日期。
- 产品团队只接收紧急升级，没有长期路线图。

### 4. Demo 多，生产少

- Bootcamp 很快。
- 生产权限、数据质量、可靠性和组织采用长期未完成。
- pilot 数量被误当成客户价值。

### 5. 客户无法自助

- 客户没有内部 owner。
- 所有变更必须由 Palantir 完成。
- Enablement 和知识转移不足。
- FDE 离场后工作流停止演进。

### 6. 现场知识没有产品化

- 同类问题在多个客户重复手工解决。
- 没有产品 gap 记录、owner 和优先级。
- Reliability 事故只做恢复，不做系统改进。
- Design 模式没有进入复用组件。

### 7. 账户利润掩盖平台债务

单个大账户可能支付大量收入，使长期定制看起来合理；但如果其代码、Ontology 和运维方式无法被其他账户复用，
公司仍可能累积高维护债务。

## 十一、与传统 SaaS、咨询和 SI 对比

| 维度 | 传统横向 SaaS | 管理/技术咨询 | System Integrator | Palantir FDE 模式 |
| --- | --- | --- | --- | --- |
| 核心销售物 | 标准订阅产品 | 建议、方案、项目人力 | 集成项目和定制系统 | 产品平台 + 任务结果 |
| 客户接触 | Sales/SE，交付后 CSM | 顾问团队深度进入 | 项目团队深度进入 | DS/FDE/Design 深度嵌入 |
| 需求处理 | 尽量标准化配置 | 分析并给出建议 | 按范围实现 | 在现场发现问题并迭代实现 |
| 工程责任 | 产品团队为主 | 可无生产代码责任 | 项目代码和集成责任 | FDE 直接构建并进入生产 |
| 生产运行 | 客户或标准支持 | 通常不是主要责任 | 依合同交接或托管 | Infra/Reliability/Enablement 持续参与 |
| 产品反馈 | CSM、工单、产品研究 | 知识管理 | 项目复盘 | 现场工程师直接反馈 Dev |
| 定制 | 低到中 | 方法和建议定制 | 高 | 目标是账户适配建于通用平台之上 |
| 收入扩张 | 席位、模块、用量 | 更多项目和顾问 | 新项目、维护合同 | 更多任务、部门、用户和平台能力 |
| 规模化机制 | 多租户和自助 | 方法论与人员杠杆 | 模板、交付中心和人力 | 通用平台、Ontology、Apollo、产品化 |
| 主要风险 | 产品不匹配复杂现场 | 建议无法落地 | 人力线性、技术债 | FDE 定制过多而退化为 SI |

### 关键差异

Palantir 与咨询和 SI 都有深度客户嵌入，但声称并努力保持 product-based model。
它与传统 SaaS 都依赖产品复用，但接受比典型 SaaS 更高的前期部署成本和更模糊的客户问题。

因此最准确的描述不是“纯 SaaS”或“咨询公司”，而是：

> 以产品平台为资本基础、以账户任务团队为价值发现与交付机制、以现场反馈推动产品研发的高接触企业软件模式。

## 十二、对组织设计的启示

### 1. 不要复制岗位名称，要复制闭环

只招聘 FDE 而没有强平台、产品 owner、可靠性能力和产品化通道，会得到昂贵的定制工程团队。

### 2. 分清三个 owner

```text
Account owner：客户关系和账户经济
Mission owner：具体业务结果和生产交付
Product owner：可复用能力和长期平台质量
```

三者可以在小公司由同一人承担，但责任不能消失。

### 3. 给现场团队自由，也要给产品边界

FDE 需要越过现有产品边界解决问题，但每次越界都应回答：

- 这是临时 workaround 还是新产品能力？
- 谁维护？
- 如何升级？
- 是否跨客户复用？
- 什么时间移除客户特例？

### 4. 采用率应是交付指标

项目不能在“代码已上线”时结束。业务 owner、DS 和 Design 应共同对实际操作变化负责。

### 5. 让可靠性和安全进入早期设计

Infra、Reliability 和 Security 不是上线门卫，而是架构参与者。越晚加入，pilot 与 production
之间的成本差距越大。

### 6. 客户自助是规模化指标

健康的 FDE 不是永远不可替代，而是让客户内部团队可以在平台上继续构建，同时让 Palantir 专注更高价值问题。

## 十三、用于判断一个 FDE 组织是否健康的问题

### 账户层

- 是否按长期账户价值分配 FDE，而不是平均分配？
- pilot 的转化率、生产率和回收期是多少？
- 新收入有多少来自现有客户采用扩张？
- 账户 contribution 是否包含真实部署和扩张成本？

### 交付层

- 每个任务是否有客户 accountable owner？
- 是否在 Bootcamp 结束前定义生产路径？
- 是否同时衡量上线、采用和业务结果？
- FDE 是否有清晰退出或降配条件？

### 产品层

- 现场扩展中有多少进入通用产品？
- 同类客户的交付时间是否持续下降？
- 客户分支和特殊代码量是否增长？
- 产品团队是否定期参与现场问题评审？

### 组织层

- Sales、DS、FDE 和 Dev 的冲突由谁裁决？
- 谁能拒绝不健康的客户定制？
- Reliability 和 Security 是否有独立升级权？
- Design 是否有权改变工作流，而不是只接受需求？

### 客户能力层

- 客户是否拥有数据、Ontology 和业务规则的负责人？
- 客户工程师能否独立构建和排障？
- 客户是否理解平台行为、权限和审计？
- Palantir 离场后系统能否持续运行和演进？

## 最终判断

Palantir 的 operating model 可以压缩为：

```text
按分部配置资本
按账户投资和衡量经济性
按任务组建跨职能小队
按平台能力组织长期研发
用 FDE 把现场问题与产品演进连接起来
```

它的组织创新不是简单取消产品、销售、咨询和工程的边界，而是重新设计它们的接口：

- Sales 对机会和商业闭环负责。
- Echo 对问题、用户和采用负责。
- Delta 对技术交付和生产结果负责。
- Design 对人类工作流负责。
- 专业 forward-deployed 角色对 AI、环境、可靠性、安全和规模化负责。
- Dev / Product Engineering 对通用平台和长期复用负责。
- 客户必须对领域规则、组织变化和风险接受负责。

这种模式能够工作的前提是：

```text
高价值复杂问题
  + 强通用平台
  + 小团队端到端责任
  + 高质量现场反馈
  + 严格的产品化纪律
  + 客户最终形成自助能力
```

缺少“强平台、产品化纪律、客户自助”中的任何一项，FDE 都可能从产品飞轮变成高成本人力交付。

## 核心官方资料

### 公司与账户经济

- [Palantir 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
- [Palantir Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm)
- [Palantir 当前 Lever 招聘 API](https://api.lever.co/v0/postings/palantir?mode=json)

### 角色与组织接口

- [Sales](https://jobs.lever.co/palantir/24060586-7ba8-47c0-bfc1-f1dd5b82d8bd)
- [Deal Team - Business Affairs](https://jobs.lever.co/palantir/16a1b500-13fe-4c22-ad89-372093b462da)
- [Deployment Strategist](https://jobs.lever.co/palantir/e0ab8226-b928-4e3a-bf87-08fe7b1ea595)
- [Forward Deployed Software Engineer](https://jobs.lever.co/palantir/5168e8fd-fec1-4fea-b7a1-81bdaea65850)
- [Forward Deployed AI Engineer](https://jobs.lever.co/palantir/636fc05c-d348-4a06-be51-597cb9e07488)
- [Product Designer](https://jobs.lever.co/palantir/2d8b7eaa-5c08-44ef-a0f0-5a96cee2794d)
- [Backend Software Engineer - Application Development](https://jobs.lever.co/palantir/ab7e3425-81d5-4705-a7b5-cd60c8a45cdb)
- [Forward Deployed Infrastructure Engineer](https://jobs.lever.co/palantir/0fccbe95-2520-4df3-8600-7897656c06a2)
- [Forward Deployed Reliability Engineer](https://jobs.lever.co/palantir/5a99fe16-1bda-4313-ace2-a11ea6e58f0c)
- [Forward Deployed Security Engineer](https://jobs.lever.co/palantir/22053072-4c22-49c4-8299-28e107ceeb98)
- [Forward Deployed Enablement Engineer](https://jobs.lever.co/palantir/00c2c97b-8514-4617-9883-e53e486b6dcd)
- [Dev versus Delta](https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87)
- [A day in the life of a Deployment Strategist](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-deployment-strategist-951cb59a5a96)
- [A day in the life of an FDSE](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1)

### 产品与治理

- [Foundry platform overview](https://www.palantir.com/docs/foundry/platform-overview/overview/)
- [Foundry product](https://www.palantir.com/platforms/foundry/)
- [Gotham product](https://www.palantir.com/platforms/gotham/)
- [AIP overview](https://www.palantir.com/docs/foundry/aip/overview/)
- [Apollo product](https://www.palantir.com/platforms/apollo/)
- [Ontology overview](https://www.palantir.com/docs/foundry/ontology/overview/)
- [Action types](https://www.palantir.com/docs/foundry/action-types/overview/)
- [Development lifecycle](https://www.palantir.com/docs/foundry/platform-overview/development-lifecycle/)
- [Global Branching](https://www.palantir.com/docs/foundry/global-branching/overview/)
- [AI FDE overview](https://www.palantir.com/docs/foundry/ai-fde/overview/)
- [AI FDE security and governance](https://www.palantir.com/docs/foundry/ai-fde/security-and-governance/)
