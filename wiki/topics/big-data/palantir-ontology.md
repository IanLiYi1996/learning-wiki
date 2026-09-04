# Palantir Ontology：企业业务语义与操作层

- 调研日期：2026-09-04
- 主题位置：大数据平台 / 企业语义层 / 数据应用 / AI Agent
- 产品范围：Palantir Foundry、AIP 与 Ontology
- 说明：本文将“plantier”按 **Palantir** 理解
- 相关主题：[Palantir FDE 与 AI FDE](palantir-fde.md)

## 结论先行

Palantir Ontology 不是把数据库表换成业务名称，也不是传统知识图谱的简单产品化。
它更接近一个建立在企业数据资产之上的**业务语义与操作运行时**：

```text
业务对象与关系
  + 决策逻辑与模型
  + 受控业务动作
  + 权限、审计和版本治理
  = 面向人类应用和 AI Agent 的操作层
```

[Palantir 官方文档](https://www.palantir.com/docs/foundry/ontology/overview/)
将 Ontology 定义为组织的 operational layer。它位于数据集、虚拟表和模型等数字资产之上，
使用 objects、properties 和 links 表达业务语义，使用 actions、functions 和 dynamic security
表达可执行行为。

理解它的关键不是“本体”这个词，而是下面这个问题：

> 如何让数据、模型和分析结果进入真实业务操作，同时保持权限、校验、审批和审计？

如果系统只需要查询和报表，Ontology 可能过重；如果系统需要让人或 Agent
在复杂业务环境中安全地采取行动，它的设计才体现出价值。

## 为什么现在受到关注

Ontology 并不是因生成式 AI 才出现，但企业 AI Agent 放大了一个长期存在的问题：
LLM 能生成答案，却通常不知道企业中的对象是什么、可以调用什么逻辑、允许执行哪些动作，
也不知道执行后如何写回系统并接受审计。

Palantir 的解法是让 Ontology 同时提供：

- **上下文**：订单、设备、客户、航班、患者等对象及其关系。
- **确定性工具**：业务规则、预测模型、优化器和 Functions。
- **可执行动作**：带参数、权限、校验、审批和写回的 Actions。
- **治理边界**：对象级、属性级、应用级和 Agent scope 权限。
- **反馈数据**：谁在什么上下文中做了什么决策，以及产生了什么结果。

[AIP 官方概览](https://www.palantir.com/docs/foundry/aip/overview/)
说明 AIP 的工作流、Agent 和 Functions 建立在 Ontology 与开发工具链之上。
Palantir 在向 SEC 提交的
[2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
中也把 Ontology 描述为其平台核心，并称 AIP 可把组织的 actions 和 processes
转化为人类与 LLM Agent 能使用的工具。

因此，“Ontology 最近火热”更准确的解释是：

> Agentic AI 让企业重新重视业务语义、工具调用、权限和执行闭环，而 Palantir
> 已经把这些能力集成为一个产品化运行层。

这是基于产品架构的判断，不代表 Palantir 已被独立证明为所有企业的最优方案。

## 它在大数据架构中的位置

```text
数据源与业务系统
ERP | CRM | MES | WMS | 数据库 | IoT | 文档 | API
                         |
                         v
数据平台
采集 | 湖仓 | 数仓 | 流处理 | 查询引擎 | ML 平台
                         |
                         v
Palantir Ontology
对象 | 属性 | 关系 | 接口 | 逻辑 | 动作 | 安全
                         |
                         v
应用与操作
分析应用 | 业务工作台 | 自定义应用 | 自动化 | AI Agent
                         |
                         v
业务结果与反馈
写回 | 通知 | 外部系统调用 | 决策记录 | 效果数据
```

Ontology 不替代对象存储、湖仓表格式、流处理或查询引擎。
它消费这些系统产生的数据和模型，把它们组织成可被业务应用使用的操作模型。

## 四个核心层次

Palantir 在
[Why create an Ontology?](https://www.palantir.com/docs/foundry/ontology/why-ontology/)
中把一个企业决策拆为 Data、Logic、Action 和 Security。这个框架比按产品组件记忆更重要。

### 1. Data：业务世界是什么

#### Object type

Object type 是现实实体或事件的类型，例如：

- `Customer`
- `PurchaseOrder`
- `Aircraft`
- `MaintenanceEvent`
- `HospitalBed`
- `Shipment`

[Object type 文档](https://www.palantir.com/docs/foundry/object-link-types/object-types-overview/)
将 object type 类比为数据集 schema，将 object 类比为一行实例，将 object set
类比为一组经过过滤的行。但这种类比只用于帮助理解，Ontology object
还会参与关系、权限、动作和应用工作流。

#### Property

Property 描述对象特征，例如订单金额、设备状态、预计到达时间。
它不仅包含数据类型，还可以包含显示信息、业务含义和安全配置。

参见 [Properties](https://www.palantir.com/docs/foundry/object-link-types/properties-overview/)。

#### Link type

Link type 定义对象之间的关系，例如：

```text
PurchaseOrder -> Supplier
Shipment -> PurchaseOrder
Aircraft -> MaintenanceEvent
Patient -> HospitalBed
```

[Link type 文档](https://www.palantir.com/docs/foundry/object-link-types/link-types-overview/)
说明 link type 是两个 object types 之间关系的 schema，link 是具体关系实例。

Links 让应用按业务关系导航，而不必在每个应用中重新实现 join。

#### Interface

Interface 是抽象能力契约，类似编程语言中的接口。

例如定义一个 `Facility` interface：

```text
Facility
  - name
  - location
  - capacity
  - shutdown()
```

`Factory`、`Warehouse` 和 `MaintenanceHangar` 都可以实现这个 interface，
同一个工作流便能处理所有设施类型。

[Interfaces 文档](https://www.palantir.com/docs/foundry/interfaces/interface-overview/)
明确区分了具体 object type 与抽象 interface。当前 interface 在不同应用和 SDK
语言中的支持程度并不完全一致。

### 2. Logic：如何评估决策

Functions 用于封装可以在操作场景中快速执行的服务器端逻辑。

常见用途包括：

- 查询和筛选对象集合。
- 遍历对象关系。
- 计算派生指标。
- 调用预测模型或优化器。
- 查询外部系统。
- 生成复杂 Ontology edits。
- 为 LLM 返回流式结果。

[Functions 概览](https://www.palantir.com/docs/foundry/functions/overview/)
显示当前 Functions 主要支持 TypeScript 和 Python，并运行在服务器端隔离环境中。

Functions 的设计意义是把业务逻辑从单个报表、脚本或 Prompt 中提取出来，
成为人类应用和 Agent 都能复用的正式能力。

### 3. Action：如何安全地改变现实

Action type 定义一个业务动作，而不是裸字段更新。例如：

```text
ApprovePurchaseOrder
ReallocateInventory
AssignMaintenanceCrew
DischargePatient
BlockSuspiciousTransaction
```

一个 Action 可以包含：

- 参数。
- 对对象和关系的修改规则。
- 提交条件与权限。
- 业务校验。
- Function-backed logic。
- 通知。
- Webhook 或外部系统调用。
- Action log。

[Actions 概览](https://www.palantir.com/docs/foundry/action-types/overview/)
将 Action 描述为一次修改一个或多个对象、属性和关系的事务。
[Action rules](https://www.palantir.com/docs/foundry/action-types/rules/)
可创建、修改或删除对象和 links，也可以把复杂变更交给 Function。

Action 的重要性在于，它把“可以做什么”从 UI 按钮提升为可复用的业务能力。
Workshop、自定义应用、API 和 Agent 可以调用同一个 Action，从而复用相同校验和权限。

#### Side effects

当真实 source of truth 位于 ERP、CRM 或其他外部系统时，Action 可以通过通知和 webhook
进行 decision orchestration。

参见 [Action side effects](https://www.palantir.com/docs/foundry/action-types/side-effects-overview/)。

需要注意：Ontology 内部修改可以有明确事务边界，但外部 webhook 或 ERP 写入
不会自动与 Ontology 形成跨系统原子事务。设计时仍需考虑幂等、重试、补偿和对账。

### 4. Security：谁能看、谁能做

Ontology 的安全不是单一 ACL，而是多层控制的组合：

```text
Ontology schema/resource permissions
  + object/property data policies
  + markings / CBAC / organization boundaries
  + application restrictions
  + Action submission criteria
  + user or service-account permissions
  + OAuth scopes
```

[Object security policies](https://www.palantir.com/docs/foundry/object-permissioning/object-security-policies/)
分别使用 object policy 和 property policy 实现行级与列级控制；两者组合可形成单元格级控制。

[Action permissions](https://www.palantir.com/docs/foundry/action-types/permissions/)
还要求执行者满足对象可见性、Action submission criteria、读写授权和目标对象权限。

一个容易忽略的边界是：

- 对象和属性策略主要在读取时过滤。
- 数据一旦进入导出文件、响应载荷或下游系统，这些策略不会自动继续生效。
- 需要结合 markings、Classification-based Access Control 或下游控制保护数据传播。

因此，Agent“使用了 scoped token”不等于系统已经自动实现业务最小权限。

## 数据是如何进入 Ontology 的

### Backing datasource

Object type 会映射到实际数据源，Ontology 并不是脱离数据的抽象模型。
数据源可以来自批处理、流处理、虚拟表或其他 Foundry 资产。

### Indexing

[Object indexing 文档](https://www.palantir.com/docs/foundry/object-indexing/overview/)
说明 Object Storage v2 使用 Funnel 管理 batch 或 streaming indexing pipeline，
把表格或其他数据转化为适合对象检索的视图。

### Direct datasource

[Direct datasource](https://www.palantir.com/docs/foundry/object-indexing/direct-datasources/)
为低延迟写入提供能力，适合数据和 edits 都要求较低延迟的工作流。
截至调研日期，该能力仍标记为 beta，并需要在吞吐、排序和重放语义之间做权衡。

### Writeback

用户或 Agent 通过 Actions 产生的修改会写入 Ontology 的编辑层或 writeback dataset，
并在不同应用中呈现最新对象状态。

设计时必须明确：

- 原始业务系统是否仍是 source of truth？
- Ontology 是操作主系统还是决策编排层？
- 写回失败后由谁重试和对账？
- 上游重放是否会覆盖用户 edits？
- 同一对象的批处理数据、流数据和人工修改如何合并？

## 决策和审计数据

Palantir 把“业务决策本身”也作为数据处理。

### Action log

[Action log](https://www.palantir.com/docs/foundry/action-types/action-log/)
把成功的 Action submission 建模为对象，可记录决策者、时间、参数、相关对象和当时上下文。

它适合回答：

```text
谁在什么时候，基于什么输入，做出了什么决定？
```

### Edit history

[Object edit history](https://www.palantir.com/docs/foundry/object-edits/user-edit-history/)
记录对象的全部编辑历史，无论修改是否来自某个 Action。

它适合回答：

```text
这个对象从过去到现在发生了哪些变化？
```

两者不能互相替代：

- Action log 关注决策上下文，但只记录成功 Action。
- Edit history 关注所有状态变更，但不一定知道业务决策原因。

### Observability

[Ontology and AIP observability](https://www.palantir.com/docs/foundry/aip-observability/overview/)
提供 metrics、execution history、distributed tracing、logs 和 performance monitoring，
用于观察 Functions、Actions、Automations、模型和 AIP Logic 的执行。

## Ontology 与 AI Agent

### 1. Ontology 作为业务上下文

传统 RAG 常从文档中检索文本片段，Ontology 则可以向 Agent 提供结构化对象、关系、
当前状态、业务定义和权限过滤后的上下文。

[Ontology-Augmented Generation](https://www.palantir.com/docs/foundry/ontology/ontology-augmented-generation/)
展示了把文档切分为 objects，再通过关键词、向量或混合搜索向模型提供内容的方法。

这并不意味着 Ontology 自动解决检索质量问题。官方也强调不存在适用于所有任务的单一最佳检索方案。

### 2. OSDK 作为应用接口

[Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/overview/)
会根据应用选择的 Ontology 资源生成类型安全 SDK，使应用能够：

- 查询 objects 和 object sets。
- 遍历 links。
- 调用 Functions。
- 提交 Actions。
- 写回 Ontology。

OSDK 的 TypeScript 实现和部分 Maker API 已公开在
[Palantir osdk-ts](https://github.com/palantir/osdk-ts)，
但生成的类型、权限和运行目标仍与具体 Foundry enrollment 绑定。

### 3. Ontology MCP 作为 Agent 工具层

[Ontology MCP](https://www.palantir.com/docs/foundry/ontology-mcp/overview/)
可以将 object types、query functions 和 Actions 暴露为模型可发现和调用的工具。

概念上可以理解为：

```text
Object types -> Agent 可以理解和查询的业务资源
Query functions -> Agent 可以调用的确定性读取工具
Actions -> Agent 可以调用的受控写入工具
```

### 4. Agent 的授权模型

[Agent scoped permissions](https://www.palantir.com/docs/foundry/agents/scoped-permissions/)
和
[Ontology MCP authentication](https://www.palantir.com/docs/foundry/ontology-mcp/authentication-and-authorization/)
说明 Agent 的权限会受到 Ontology binding、应用限制、OAuth scope
以及用户或服务账号权限的共同约束。

交互式 Agent 通常代表当前用户执行；后台 Agent 则可能使用服务账号。
两者需要不同的审批、审计和权限设计。

### 5. 安全的写入模式

推荐路径：

```text
Agent 读取对象
  -> 调用确定性 Function/模型
  -> 生成建议
  -> 人工或策略审批
  -> 调用预定义 Action
  -> 写回并生成审计记录
```

不推荐路径：

```text
Agent 自由生成 SQL/HTTP 请求
  -> 直接修改底层系统
  -> 缺乏统一校验、权限和审计
```

[Staged writes](https://www.palantir.com/docs/foundry/logic/staged-writes/)
允许 AIP Logic 在一次执行中暂存嵌套 Function 或 Action 产生的 edits，
再统一提交。截至调研日期，这项能力仍标记为 beta。

## 与相邻技术的区别

| 技术 | 主要解决的问题 | 与 Palantir Ontology 的关键差异 |
| --- | --- | --- |
| OWL/RDF 本体 | 开放知识表示、形式语义、推理与交换 | Palantir 更关注企业数据绑定、工作流、动作、权限和运行时 |
| 知识图谱 | 实体、关系、图查询和知识发现 | Ontology 增加 Functions、Actions、写回、应用和安全控制 |
| BI Semantic Layer | 统一指标、维度和 join | Ontology 不只回答问题，还能修改业务状态 |
| Data Catalog | 发现、描述、血缘和治理数据资产 | Ontology 将数据资产映射为可运行的业务对象与能力 |
| MDM | 匹配、去重、主记录和数据质量 | Ontology 可消费主数据，并在其上建立行为和决策 |
| Lakehouse | 开放存储、表事务、计算与查询 | Ontology 位于湖仓之上，不替代表格式和计算引擎 |
| Digital Twin | 物理或业务系统的动态数字表示 | Ontology 可承载孪生模型，但不自动提供工程仿真或 3D 能力 |

### 与 OWL/RDF 的区别

[W3C OWL 2](https://www.w3.org/TR/owl2-overview/)
拥有形式化语义，可支持一致性、包含关系和实例检索等推理。
[RDF](https://www.w3.org/TR/rdf11-primer/)
强调基于 IRI 和三元组的开放图表示。

Palantir 公开文档没有把 OWL、RDF、SHACL 或 SPARQL 描述为 Ontology 的核心兼容层。
因此不要因为名称相同，就假设 Palantir Ontology 能与标准语义网本体无损互换。

更准确的说法是：

```text
W3C ontology = formal knowledge representation
Palantir Ontology = operational enterprise domain model and runtime
```

### 与 Semantic Layer 的区别

[dbt Semantic Layer](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)
主要集中定义 metrics，自动处理 joins，并向下游工具提供一致指标。

如果需求只是“所有报表使用同一个收入指标”，Semantic Layer 更直接。
如果需求是“识别风险订单，计算替代方案，审批并重新分配库存”，则需要
Ontology 所强调的对象、逻辑和动作闭环。

### 与 Catalog 的区别

[Databricks Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/)
是数据与 AI 资产治理层，重点包括权限、发现、血缘、审计和共享。

Ontology 可以使用这些治理后的资产，但它还需要回答：

- 数据对应哪些业务对象？
- 对象之间是什么关系？
- 可以执行哪些业务动作？
- 谁可以在什么条件下执行？
- 动作结果如何写回和追踪？

两者可以互补，代价是要管理资产元数据与业务本体之间的一致性。

## 一个供应链例子

### 对象模型

```text
Supplier
Part
PurchaseOrder
Shipment
InventoryLot
Factory
CustomerOrder
```

### 关系

```text
Supplier -> supplies -> Part
PurchaseOrder -> orderedFrom -> Supplier
Shipment -> fulfills -> PurchaseOrder
InventoryLot -> storedAt -> Factory
CustomerOrder -> requires -> Part
```

### Functions

```text
predictShipmentDelay(shipment)
calculateShortageRisk(part, factory)
optimizeInventoryAllocation(shortages)
findApprovedSubstitute(part)
```

### Actions

```text
ExpediteShipment
ReallocateInventory
ApproveSubstitutePart
ChangeSupplier
NotifyCustomer
```

### Agent 工作流

```text
1. Agent 查询未来七天可能缺料的订单。
2. Function 计算延误概率和库存影响。
3. 优化器生成库存重分配建议。
4. Agent 解释方案及其成本。
5. 高金额变更进入人工审批。
6. 审批后调用 ReallocateInventory Action。
7. Action 写回 Ontology，并通过 webhook 更新 ERP。
8. Action log 保存决策上下文。
9. 后续实际交付结果用于评估建议质量。
```

这个例子体现了 Ontology 与普通知识图谱的根本区别：
图谱可以描述供应商、订单和零件之间的关系；操作本体还定义了如何计算、如何行动、
谁能行动以及行动后发生什么。

## 推荐实施方法

### 1. 从决策开始

不要先建“企业全部对象”，先选择一个高价值决策：

- 谁做决策？
- 需要哪些输入？
- 使用什么逻辑？
- 可以采取什么行动？
- 行动后修改哪些系统？
- 如何判断结果好坏？

### 2. 建立最小业务模型

只建支撑该决策所需的对象、属性和关系，避免照搬所有源系统表结构。

### 3. 明确数据所有权

为每个对象定义：

- 主键和身份解析规则。
- source of truth。
- 数据所有者。
- 更新频率。
- 质量规则。
- 批、流和人工 edits 的合并策略。

### 4. 把逻辑产品化

将稳定逻辑放入 Functions、模型或优化器，不要把重要规则埋在 Dashboard、
Prompt 或单个应用前端中。

### 5. 把写操作包装为 Action

Action 至少应定义：

- 输入参数。
- 前置条件。
- 权限和 submission criteria。
- 幂等键或重复提交策略。
- 业务校验。
- 写回和外部 side effects。
- 失败与补偿方案。
- 审批条件。
- Action log。

### 6. 先支持人，再支持 Agent

先确保人类用户可以通过同一 Action 稳定完成流程，再让 Agent 调用。
这样 Agent 继承的是已验证的业务能力，而不是直接获得底层系统权限。

### 7. 建立持续治理

Ontology 是长期产品，不是一次性数据模型。需要明确：

- Domain owner。
- Ontology owner。
- Data steward。
- Action owner。
- 安全负责人。
- 版本和兼容策略。
- 废弃流程。
- 变更评审与测试。

[Ontology Manager](https://www.palantir.com/docs/foundry/ontology-manager/overview/)
提供 UI 管理面；[SuperRepo](https://www.palantir.com/docs/foundry/superrepo/overview/)
和 Ontology-as-code 则提供代码化、测试和发布路径。SuperRepo 截至调研日期仍为 beta。

## 常见错误

### 1. 把数据库表一比一变成 object types

结果只是换名后的数据目录，没有形成稳定业务语义。

### 2. 一开始追求全企业统一模型

范围过大，价值反馈过慢，最终容易变成长期建模项目。

### 3. 只有对象，没有 Actions

如果 Ontology 只能查询而不能支撑业务变更，它与普通语义层的差异会明显缩小。

### 4. 让 Agent 绕过 Action

直接写数据库或调用任意 API，会失去统一校验、权限、审批和审计。

### 5. 混淆 Action log 与 edit history

前者记录决策上下文，后者记录全部状态变化。

### 6. 忽略外部系统一致性

Webhook 成功与 Ontology edit 成功不是同一个事务，需要补偿和对账。

### 7. 认为读取权限会自动传播

对象策略对下游导出和应用载荷有明确边界，必须单独设计传播控制。

### 8. 没有业务负责人

本体并不是数据团队独自维护的 schema；没有领域负责人时，语义和动作会快速失真。

## 局限与风险

### 平台依赖

虽然 OSDK 的 TypeScript 客户端及部分 Maker API 开源，但 Ontology 的语义模型、
Actions、Functions、应用、权限和写回仍依赖 Foundry 运行时。

[Ontology export/import](https://www.palantir.com/docs/foundry/ontology-manager/export-import/)
支持 JSON 迁移，但官方提醒不能依赖该 JSON schema 保持稳定，部分配置也不能跨 Ontology 完整导入。

更现实的锁定风险不是“原始数据拿不出来”，而是多年积累的业务逻辑、
操作工作流和应用很难低成本迁移。

### 实施与组织成本

Palantir 的
[2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
披露：

- 大型客户的数据环境和实施过程复杂。
- 销售周期通常为六到九个月，部分客户超过一年。
- 专业服务可能包含培训、界面配置，以及持续的 Ontology 和数据建模支持。

这些披露说明 Bootcamp 在数日内做出第一个流程，并不等于完成生产级集成、
治理和组织推广。

### 能力成熟度不一致

截至调研日期，以下能力存在 beta、部分支持或按语言不同的情况：

- Direct datasource。
- SuperRepo 和 Ontology-as-code 的部分流程。
- Pro-code Agents。
- AIP Logic staged writes。
- Interfaces 在 Java、Python、Actions 和对象服务中的部分能力。

选型时必须以目标 enrollment 的实际功能为准。

### 独立验证有限

公开案例大多由 Palantir 或客户联合发布。它们能证明场景和可行性，
但通常没有完整披露基线、对照组、实施成本和归因方法。

## 公开案例如何看

### Airbus / Skywise

[Airbus and Skywise](https://www.palantir.com/impact/airbus/)
适合说明飞机、部件、航班、维护和供应链对象如何组成跨组织运营模型。
页面公布了交付速度、机队连接和停场减少等指标，但属于联合案例材料，
不能把全部效果独立归因于 Ontology。

### Tampa General Hospital

[Tampa General Hospital](https://www.palantir.com/impact/tampa-general-hospital/)
展示了患者流、床位、排班和运营决策场景。公开改善指标有参考价值，
但缺少完整实验周期、样本和成本披露。

### NHS Federated Data Platform

英国卫生与社会保障部的
[Accounting Officer Assessment](https://www.gov.uk/government/publications/department-of-health-and-social-care-accounting-officer-assessments/federated-data-platform-programme-accounting-officer-assessment)
给出了七年预期收益，同时披露 Gateway Review 为 amber，并承认不同产品采用率会影响收益模型。

这个案例更适合说明：

```text
试点价值 != 大规模采用价值
技术可行 != 组织推广成功
预期收益 != 已实现收益
```

## 学习顺序

### 第一阶段：理解概念

1. Object、Property、Link、Interface。
2. Function 与 Action 的区别。
3. Read path、write path 和 source of truth。
4. Action log、edit history 和 lineage。
5. 对象权限、属性权限和 markings。

### 第二阶段：画出完整执行链

选择一个场景，画出：

```text
源数据
  -> Object indexing
  -> Object/Link model
  -> Function/model
  -> Application/Agent
  -> Action
  -> Writeback/external system
  -> Audit and feedback
```

### 第三阶段：做技术比较

分别回答：

- 为什么不用普通数据仓库？
- 为什么不用 dbt Semantic Layer？
- 为什么不用知识图谱？
- 为什么不用 Catalog + 自研微服务？
- 为什么不用业务系统自身的 API？

如果不能清楚回答，说明还没有找到 Ontology 的增量价值。

### 第四阶段：研究 Agent 治理

重点学习：

- OSDK 和 Ontology MCP。
- 用户代理与服务代理的授权区别。
- Human-in-the-loop。
- Action approval。
- Staged writes。
- Evals、tracing 和审计。
- 外部模型和外部系统的数据边界。

## 选型检查表

| 问题 | 是 | 否 |
| --- | --- | --- |
| 是否存在高价值、重复发生的业务决策？ | 继续评估 | Ontology 价值有限 |
| 是否需要跨多个数据源和业务系统？ | 适合统一对象模型 | 简单应用可能足够 |
| 是否需要把分析结果转化为受控写操作？ | Actions 有价值 | Semantic Layer 可能足够 |
| 业务对象、关系和动作能否被多个应用复用？ | 平台收益较高 | 单应用建模可能更便宜 |
| 是否需要 AI Agent 安全调用真实业务能力？ | Ontology/Action 模式有价值 | 普通 RAG 可能足够 |
| 是否有领域负责人长期治理模型？ | 可以推进 | 应先解决组织责任 |
| 是否能承担平台和迁移依赖？ | 进入商业评估 | 优先开放组合式架构 |

## 最终判断

Palantir Ontology 最值得学习的不是某个产品界面，而是一个架构思想：

```text
数据平台负责提供可信数据和计算，
业务本体负责表达现实世界和决策语义，
操作层负责把决策变成受控动作，
安全与审计贯穿人和 Agent 的完整执行链。
```

它对大数据技术体系的补充，是在“数据能够被查询”之后继续追问：

> 数据如何变成可复用的业务能力，并由人和 AI 安全地作用于现实？

## 核心资料

- [Palantir Ontology overview](https://www.palantir.com/docs/foundry/ontology/overview/)
- [Why create an Ontology?](https://www.palantir.com/docs/foundry/ontology/why-ontology/)
- [Ontology core concepts](https://www.palantir.com/docs/foundry/ontology/core-concepts/)
- [Action types](https://www.palantir.com/docs/foundry/action-types/overview/)
- [Functions](https://www.palantir.com/docs/foundry/functions/overview/)
- [Ontology SDK](https://www.palantir.com/docs/foundry/ontology-sdk/overview/)
- [Ontology MCP](https://www.palantir.com/docs/foundry/ontology-mcp/overview/)
- [AIP overview](https://www.palantir.com/docs/foundry/aip/overview/)
- [Ontology and AIP observability](https://www.palantir.com/docs/foundry/aip-observability/overview/)
- [Palantir 2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000011/pltr-20251231.htm)
- [W3C OWL 2 overview](https://www.w3.org/TR/owl2-overview/)
- [dbt Semantic Layer](https://docs.getdbt.com/docs/use-dbt-semantic-layer/dbt-sl)
- [Databricks Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/)

## 研究边界

- Palantir 官方文档多数未标注独立发布日期，本文统一记录访问日期 2026-09-04。
- 产品能力可能因 enrollment、部署环境和版本不同。
- 案例效果数字主要来自 Palantir 或客户联合材料。
- 公开资料缺少同规模、同场景的长期 TCO、迁移成本和跨平台性能基准。
- 本文中的架构比较是基于公开功能边界的分析，不是对未公开内部实现的断言。
