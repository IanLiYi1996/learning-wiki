# Palantir FDE 与 AI FDE：前线部署工程方法

- 调研日期：2026-09-04
- 主题位置：企业软件交付 / 数据与 AI 工程 / 平台产品化 / Agent 工程
- 核心术语：FDE、FDSE、Deployment Strategist、AI FDE
- 相关主题：[Palantir Ontology](palantir-ontology.md)

## 结论先行

FDE 是 **Forward Deployed Engineer**，通常译为前线部署工程师。

它不是“驻场程序员”的新名称，也不是传统咨询顾问加一点代码。
健康的 FDE 模式把四种责任放在同一个闭环中：

```text
理解客户真实问题
  + 亲自构建生产系统
  + 对采用和业务结果负责
  + 把现场经验沉淀回产品
```

Palantir 当前还使用同一个名称提供 **AI FDE**：
一个能通过自然语言操作 Foundry、修改数据管道和 Ontology、运行测试并提交评审的 Agent。

这两个概念必须分开：

```text
人类 FDE
  负责：问题、判断、关系、交付和结果

AI FDE
  负责：加速 Foundry 内的探索、实现、测试和变更操作
```

AI FDE 更像人类 FDE 的工程杠杆，而不是完整替代者。

## 两个 FDE

### 人类 FDE / FDSE

Palantir 当前
[Forward Deployed Software Engineer 职位](https://jobs.lever.co/palantir/5168e8fd-fec1-4fea-b7a1-81bdaea65850)
要求工程师直接与客户合作，理解最困难的问题，并端到端负责架构、数据处理、
定制应用、AI 工作流和生产交付。

Palantir 的岗位材料交替使用 FDE 和 FDSE。公开资料没有给出严格的历史名称版本边界，
可以把它们理解为同一角色谱系。

### Palantir AI FDE

[AI FDE 官方概览](https://www.palantir.com/docs/foundry/ai-fde/overview/)
将其定义为 AI-powered Forward Deployed Engineer：
一个通过对话命令直接操作 Foundry 的交互式 Agent。

它可以执行数据转换、代码仓库操作、Ontology 修改、Function 开发、应用构建和治理检查。

## 为什么会出现 FDE

传统企业软件交付经常存在四个断点：

```text
产品团队不了解客户现场
客户知道问题但不会转化为系统设计
销售完成签约但不负责生产结果
顾问给出建议但不长期拥有运行系统
```

FDE 的组织设计是把这些断点压缩到一个小团队中：

```text
客户问题
  -> 现场理解
  -> 数据和工作流建模
  -> 工程实现
  -> 上线和采用
  -> 结果测量
  -> 产品反馈
```

它适合以下问题：

- 业务价值高，失败代价大。
- 数据分散在多个系统中。
- 工作流包含大量隐性知识。
- 需求在实施过程中才会逐渐清晰。
- 需要把分析或 AI 结果接入真实操作。
- 安全、权限、审计和监管要求复杂。

如果问题只是标准 SaaS 配置或低价值自动化，FDE 模式通常太重。

## 人类 FDE 的核心职责

Palantir 当前职位把 FDE 描述为接近 startup CTO 的角色：
在小团队中拥有高风险项目的端到端执行权。

### 问题发现

FDE 面对的通常不是完整需求文档，而是类似问题：

```text
为什么客户正在流失？
哪些订单会延误？
如何更早识别欺诈？
如何优化医院床位和护士配置？
如何让 AI 安全参与现有决策流程？
```

FDE 需要进入用户工作流，区分：

- 用户描述的问题。
- 数据暴露出来的问题。
- 真正限制业务结果的问题。
- 可以通过软件改变的问题。

### 工程实现

公开职位中的典型工作包括：

- 数据集成与清洗。
- 数据模型和 Ontology 建模。
- 分布式数据处理。
- 后端服务和 Functions。
- 前端和自定义应用。
- LLM、RAG、Agent 和评估。
- 权限、安全和合规配置。
- 生产部署与故障排查。

具体技术栈不是固定的。当前职位常列出 Python、Java、C++、
TypeScript/JavaScript、SQL、Spark、云基础设施和前端框架。

### 客户协作

FDE 需要同时与以下人员工作：

- 一线操作用户。
- 客户数据和软件工程师。
- 领域专家。
- 安全、法务和监管团队。
- 项目负责人。
- C-level 决策者。

这意味着技术正确只是必要条件。系统还必须被用户理解、接受并持续使用。

### 生产责任

FDE 不应在 demo 后结束工作。典型责任继续延伸到：

- 生产上线。
- 可靠性和性能。
- 权限与审计。
- 用户培训。
- 采用率。
- 故障处理。
- 业务指标。
- 客户团队交接。

### 产品反馈

FDE 的长期价值来自把现场发现变成可复用产品能力：

```text
一个客户的问题
  -> 找到重复模式
  -> 抽象数据模型、组件或工作流
  -> 反馈给平台和产品团队
  -> 后续客户减少定制成本
```

[Palantir 的 Dev versus Delta](https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87)
将经典边界概括为：

- 产品工程师长期拥有一项通用能力。
- FDE 围绕一个客户结果组合和扩展多项能力。

实际组织中两者可以互相流动，边界不是绝对的。

## Palantir 的前线角色族

Palantir 当前公开招聘显示，forward-deployed 已发展成多个专业方向。

| 角色 | 主要责任 | 典型输出 |
| --- | --- | --- |
| FDSE / FDE | 技术方案端到端实现 | 管道、Ontology、应用、AI 工作流、生产系统 |
| Deployment Strategist | 问题、用户、采用和价值 | 工作流定义、培训、业务案例、高层沟通 |
| Forward Deployed AI Engineer | GenAI 战略与生产实现 | LLM/Agent 工作流、Evals、AI 应用 |
| Infrastructure Engineer | 部署环境和基础设施 | 云/本地部署、升级、配置、自动化 |
| Reliability Engineer | 生产工作流可靠性 | 事故响应、自动化、可观测性、产品改进 |
| Security Engineer | 安全和监管交付 | ATO、控制映射、审计材料、安全架构 |
| Enablement Engineer | 扩大客户自助能力 | 支持、指导、工具、运行手册和知识沉淀 |

这说明“forward deployed”描述的是工作位置和责任方式，
并不限定只能做应用开发。

## FDE 与 Deployment Strategist

[Deployment Strategist 职位](https://jobs.lever.co/palantir/e0ab8226-b928-4e3a-bf87-08fe7b1ea595)
更强调：

- 找到最重要的问题。
- 理解数据含义和用户动机。
- 设计工作流。
- 培训用户。
- 向分析师和高管表达结果。
- 识别下一步扩展机会。

FDSE 更强调：

- 架构和系统设计。
- 数据管道。
- 代码和应用。
- 生产部署。
- 技术可靠性。

二者都可能参与产品、项目管理、战略和客户关系。
实际项目中的边界取决于团队成员能力和项目阶段。

一个可用的简化模型是：

```text
Deployment Strategist
  重点回答：解决什么、为谁解决、如何产生采用和价值

FDE / FDSE
  重点回答：如何把它可靠地构建并运行在生产中
```

## FDE 交付生命周期

### 1. Embed：进入现场

目标不是只听需求，而是理解：

- 用户每天如何工作。
- 哪些步骤依赖人工经验。
- 哪些系统是真正 source of truth。
- 哪些决策由谁承担责任。
- 组织中有哪些权限和政治约束。

当前 Palantir 职位中的出差要求因团队和地区差异明显，
公开范围从约 25% 到 75%。出差比例不是 FDE 的定义，
关键是能否获得足够深的业务上下文。

### 2. Frame：定义问题和结果

FDE 应将模糊目标转化为：

- 用户和决策者。
- 当前流程。
- 期望流程。
- 数据输入。
- 技术和监管约束。
- 可执行动作。
- 成功指标。
- 验收标准。

应避免仅用“模型准确率”定义成功。
生产采用率、处理时间、错误成本和业务结果通常更重要。

### 3. Integrate：建立数据基础

典型任务包括：

- 接入数据库、API、事件和文件。
- 处理身份匹配和主键。
- 建立批流管道。
- 设计数据质量规则。
- 配置权限和 markings。
- 建立可扩展的数据模型。

### 4. Model：构建 Ontology

FDE 将业务现实映射为：

```text
Objects
  + Properties
  + Links
  + Functions
  + Actions
  + Security
```

详见 [Palantir Ontology 深度调研](palantir-ontology.md)。

Ontology 的作用是让数据、逻辑和业务动作被多个应用与 Agent 复用，
而不是为一个 dashboard 临时准备数据。

### 5. Build：构建最短价值链

FDE 通常优先交付一个端到端可运行流程：

```text
真实数据
  -> 分析或模型
  -> 用户界面
  -> 决策
  -> Action
  -> 写回
  -> 结果反馈
```

Palantir 的 AIP Bootcamp 模式强调在实际客户数据上快速构建真实工作流。
但向 SEC 提交的文件也明确提示：试点和 Bootcamp
可能投入大量资源，却不一定转化为长期合同或规模化生产价值。

### 6. Iterate：和用户共同迭代

FDE 需要观察：

- 用户是否理解输出。
- 建议是否在正确时间出现。
- 工作流是否比旧方式更快。
- 哪些异常没有被模型覆盖。
- 哪些操作需要人工审批。
- 哪些设计在真实压力下失败。

### 7. Productionize：生产化

至少需要补齐：

- 自动化测试。
- 数据质量和契约。
- Evals。
- 权限和最小授权。
- 审批与审计。
- 可观测性。
- 容量和成本。
- 故障恢复。
- 版本与发布。
- 支持和 on-call。

### 8. Adopt：推动采用

系统上线不等于产生价值。FDE 或 Deployment Strategist 还需要：

- 培训用户。
- 建立操作手册。
- 修改不合理流程。
- 建立负责人。
- 跟踪使用率。
- 处理组织阻力。

### 9. Measure：测量结果

典型指标：

```text
业务 KPI
采用率
流程时间
异常率
错误成本
模型和系统质量
人工复核率
运行成本
```

Palantir 没有公开统一的 FDE 个人绩效公式。
公开职位反复强调真实运营结果，而不是工单数或代码量。

### 10. Productize：把经验放回平台

交付完成后应问：

- 哪些代码可以删除并改为平台配置？
- 哪些模式可以成为模板？
- 哪些集成可以成为 connector？
- 哪些权限模型可以复用？
- 哪些失败应该推动核心产品修改？
- 客户能否脱离 FDE 独立运行？

这一步决定 FDE 是形成软件复利，还是退化为项目制服务。

## FDE 与相邻角色的区别

| 角色 | 常见结束位置 | 与 FDE 的差异 |
| --- | --- | --- |
| 管理咨询 | 建议、路线图或组织方案 | FDE 通常继续实现并运行生产系统 |
| 系统集成商 | 定制项目交付 | FDE 应依托统一平台并将经验产品化 |
| Solutions Architect | 架构和技术验证 | FDE 通常继续编码、上线和推动采用 |
| Sales Engineer | 售前 demo 和技术评估 | FDE 对生产结果承担更长责任 |
| Customer Success | 使用和续约 | FDE 可以创造新的数据与 AI 工作流 |
| Product Engineer | 通用平台能力 | FDE 围绕特定客户结果组合多项能力 |
| Resident Engineer | 长期驻场支持 | FDE 理想上应形成交接和可复用产品反馈 |

这些是常见模式，不是统一行业标准。不同公司正在重新定义 FDE。

## FDE 能力模型

### 软件工程

- 数据结构和算法。
- 系统设计。
- API 和服务。
- 生产级编码。
- 测试、CI/CD 和代码评审。
- 全栈应用。

### 数据工程

- SQL 和数据建模。
- 批处理与流处理。
- Spark 和分布式计算。
- 数据质量和可观测性。
- 身份解析和主数据。
- 权限与数据治理。

### AI 工程

- 模型选择。
- Prompt 和上下文设计。
- RAG。
- Agent 和工具调用。
- Evals。
- Human-in-the-loop。
- 延迟、成本和可靠性优化。

### 平台与基础设施

- 云和 Kubernetes。
- 网络与身份。
- 安全和合规。
- 日志、指标和追踪。
- 部署、升级和事故处理。

### 产品能力

- 用户访谈和问题发现。
- 工作流设计。
- 成功指标。
- 优先级和范围控制。
- 快速原型。
- 采用与变更管理。

### 交付能力

- 项目拆解。
- 风险管理。
- 依赖协调。
- 书面沟通。
- 高层汇报。
- 培训和交接。

### 行为特征

Palantir 当前职位反复强调：

- Agency。
- 对结果负责。
- 接受模糊性。
- 快速学习。
- 低 ego。
- 在压力下保持判断。
- 能在技术和非技术团队间切换。

## FDE 的一天

Palantir 的
[FDSE 工作日访谈](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1)
展示的工作可能在一天内跨越：

```text
检查生产管道
  -> 调查数据异常
  -> 与用户讨论工作流
  -> 编写或评审代码
  -> 配置权限
  -> 测试应用
  -> 处理部署问题
  -> 向客户展示结果
  -> 向产品团队反馈缺口
```

这是单个员工和特定项目的案例，不代表所有 FDE 的固定时间分配。

## FDE 的商业模型

FDE 同时服务于交付、销售扩张和产品研发。

Palantir
[Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm)
披露，面向现有客户的软件工程师经常同时：

- 管理平台部署与运行。
- 发现平台可以解决的新问题。

这些人员成本会按账户和投入时间进入 contribution margin 计算。

### 为什么它不完全等于咨询

同一 SEC 文件强调 Palantir 采用 product-based model，
而不是为每个客户基于 labor contract 编写完全独立的软件。

理想状态下：

```text
FDE 定制的是配置、Ontology、工作流和应用
核心平台、权限、发布和运行能力保持通用
```

### 为什么它又包含服务属性

Palantir 同时披露：

- 专业服务。
- 用户支持和培训。
- 持续 Ontology 与数据建模支持。
- 试点和 Bootcamp 投入。
- 客户环境中的部署和运维成本。

因此，FDE 是软件与服务之间的混合机制。

## FDE 增长飞轮

```text
1. 进入高价值客户
2. 找到一个关键工作流
3. 快速构建并证明价值
4. 扩展到更多用户和业务域
5. 形成长期平台采用
6. 把重复模式放回产品
7. 降低下一个客户的交付成本
```

这个飞轮只有在第 6、7 步成立时才会形成软件复利。

## 服务陷阱

[a16z 的 Palantirization 分析](https://a16z.com/the-palantirization-of-everything/)
提出一个值得保留的批判：

如果企业只复制“派工程师驻场”，却没有强平台和共同原语，
最终会得到大量无法维护、无法升级、无法复用的独立项目。

### 健康模式

- 单个客户价值足够高。
- 客户工作流具有一定相似性。
- 底层平台强。
- 大部分交付使用通用原语。
- 定制代码会持续回收为平台、模板或配置。
- 客户最终能自助运行。
- FDE 与产品团队共享路线图。

### 危险模式

- 每个客户一套完全不同的代码。
- 收入增长必须同步增加工程师。
- FDE 永久驻场。
- 客户无法独立维护。
- 现场团队只完成销售承诺。
- 产品团队看不到现场学习。
- demo 成功，但生产采用和业务结果不明。

## 职业路径

FDE 可以培养少见的组合能力：

```text
软件工程
  + 数据和 AI
  + 产品判断
  + 领域知识
  + 企业交付
  + 高层沟通
```

Palantir SEC 文件描述其组织相对扁平，
成功的初级员工可能快速承担项目经理、开发负责人或产品经理责任。

这带来两面性：

- 优点：学习密度高，责任增长快，接近创业者体验。
- 风险：正式职级路径和评价标准可能不如传统工程组织清晰。

### 适合的人

- 喜欢真实问题而不是明确工单。
- 愿意跨前后端、数据、云和 AI。
- 能直接面对用户和高管。
- 可以在信息不完整时推进。
- 对上线和业务结果有责任感。
- 能接受出差、上下文切换和压力。

### 不适合的人

- 只想深耕一个稳定技术模块。
- 不愿承担客户沟通和项目节奏。
- 需要高度可预测的需求和工作边界。
- 不愿处理生产、运维或组织变更。
- 对出差或现场工作有严格限制。

## Palantir AI FDE

### 产品时间线

[2025 年 11 月发布说明](https://www.palantir.com/docs/foundry/announcements/2025-11/)
显示 AI FDE 于 2025-11-18 以 beta 推出。

[2026 年 3 月发布说明](https://www.palantir.com/docs/foundry/announcements/2026-03/)
显示 AI FDE 于 2026-03-12 对已启用 AIP 的 enrollment 正式 GA。

后续能力扩展包括：

- 2026-04-14：在 AI FDE 内完成 AIP Evals 编写、运行、诊断和迭代。
- 2026-08-27：在 AI FDE 内配置部分 Automate 业务自动化。
- 2026-08-18：AIP Evolve beta，可协调多个 AI FDE Agent 优化 AI 系统。

### 工作方式

```text
自然语言请求
  -> 分析意图和上下文
  -> 选择 Mode
  -> 启用相关 Capabilities 和 Tools
  -> 生成计划或请求澄清
  -> 调用 Foundry 原生工具
  -> 观察执行结果
  -> 预览、测试或读取 CI
  -> 提交 Proposal / PR
  -> 人工评审和合并
```

[AI FDE 概览](https://www.palantir.com/docs/foundry/ai-fde/overview/)
称其采用 closed-loop operation：
执行操作后读取结果，再决定下一步。

它能够通过以下方式验证修改：

- Transform preview。
- Function preview。
- Dataset build。
- CI checks。
- AIP Evals。

### Modes

[Modes and capabilities](https://www.palantir.com/docs/foundry/ai-fde/modes-and-capabilities/)
列出当前主要模式：

- Data integration。
- Data connection。
- Ontology editing。
- Functions editing。
- Exploration。
- Governance。
- Machine learning。
- OSDK React。
- Platform Q&A。

Mode 的作用不是简单切换提示词，而是控制：

- 加载哪些文档。
- 提供哪些上下文。
- 启用哪些工具。
- Agent 应如何处理问题。

### Capabilities 和 Tools

Capability 是跨 Mode 使用的细粒度能力，并映射到一个或多个工具。

Agent 自管理能力包括：

- 切换 Mode。
- 请求澄清。
- 生成计划。
- 加载文档。
- 管理上下文。
- 动态启停 Capabilities。

领域能力示例：

- 文件系统操作。
- Notepad。
- Solution design。
- 执行 Ontology Action。

### 上下文管理

[AI FDE Navigation](https://www.palantir.com/docs/foundry/ai-fde/navigation/)
说明新会话默认使用最小上下文，不自动获得用户数据。

用户可以主动加入：

- Dataset。
- Function。
- Branch。
- Interface。
- Action type。
- Object type。
- 文档包和媒体。
- 其他 Foundry 资源链接。

这是一种重要的 Agent 设计：

```text
默认无业务数据
  -> 按任务显式增加上下文
  -> 只启用必要工具
```

它同时降低上下文污染和不必要数据暴露。

### 数据和代码能力

AI FDE 可以：

- 编写或修改 Python transforms。
- 构建 Pipeline Builder 管道。
- 管理 Code Repository。
- 运行 build 和 preview。
- 创建或修改数据连接。
- 调试部分 egress policy 和连接问题。

### Ontology 能力

AI FDE 可以创建或修改：

- Object type。
- Link type。
- Action type。
- 部分相关 Ontology 资源。

它还可以在当前权限允许时执行 Ontology Actions。

不是所有资源都具有相同的 branching 和编辑支持，
目标 enrollment 的实际能力需要单独核验。

### Functions 和 Evals

AI FDE 支持：

- AIP Logic。
- TypeScript Functions。
- Python Functions。
- Function preview。
- AIP Evals。

[2026 年 4 月发布说明](https://www.palantir.com/docs/foundry/announcements/2026-04/#evaluate-and-ship-directly-with-aip-evals-in-ai-fde)
说明 AI FDE 可以在测试失败后读取结果、诊断问题、修改 Function 或 suite，
再重新运行。

当时公开限制包括部分 object-set-backed test cases、multi-target suites、
run datasets 和 Marketplace evaluators。

### 应用能力

AI FDE 明确支持：

- OSDK React 应用。
- Custom widgets。

官方总览没有承诺它可以完整构建所有 Workshop、Slate 或其他应用类型。

### Automate

[2026 年 8 月发布说明](https://www.palantir.com/docs/foundry/announcements/2026-08/#configure-business-automation-with-automate-in-ai-fde)
显示 AI FDE 可以在同一会话中创建、检查和修改部分 Automate：

- 时间和对象集条件。
- Action、AIP Logic 和通知 effects。
- 执行模式。
- 重试与 fallback。
- Scope。
- 暂停和恢复。

发布说明同时列出尚不支持的部分条件、effects、运行历史、
手动触发和 telemetry 操作。

## AI FDE 的权限模型

[Security and governance](https://www.palantir.com/docs/foundry/ai-fde/security-and-governance/)
说明 AI FDE：

- 使用当前用户的 Foundry session。
- 不使用单独 service account。
- 不拥有提升后的权限。
- 每个 API 调用都携带当前用户身份。
- 不能执行用户本人无权执行的操作。

概念上：

```text
AI FDE 有效权限
  = 当前用户权限
  ∩ 当前应用和项目范围
  ∩ markings
  ∩ 已启用 tools
  ∩ 用户批准
```

继承用户权限并不自动代表业务权限设计合理。
如果用户本身权限过大，AI FDE 的潜在操作范围也会过大。

## Tool Approval

默认情况下：

- 只读操作通常自动批准。
- Branch 上的部分修改可以按策略批准。
- 默认分支修改需要批准。
- 创建仓库等无法分支的变化需要批准。
- Dataset build 等可能产生 side effect 的工具需要批准。
- 执行 Ontology Action、创建应用、发布或创建 tag 等敏感操作始终需要确认。

用户可以为单次操作批准，也可以对会话中的特定 branch 或 project 进行预授权。

## Branch、Proposal 与 PR

AI FDE 默认使用分支。

```text
Ontology / Logic / Automate 等 Foundry 资源
  -> Global Branch
  -> Proposal
  -> Rebase / Merge checks / Policy approvals
  -> Main

Code Repository
  -> Git branch
  -> Pull Request
  -> CI / Review
  -> Main
```

Global Branch proposal 和代码 PR 是两个相关但不同的评审系统。
不是所有 Foundry 资源都支持 Global Branching。

## 审计和会话

AI FDE 提供两层记录：

### Chat outline

记录活动会话中的：

- Prompt。
- Response。
- Tools。
- Token 使用。

它有助于理解 Agent 的工作过程，但不应自动等同于不可变合规审计记录。

### Foundry audit logs

记录以用户身份执行的：

- API 调用。
- Repository 操作。
- Ontology 修改。
- Dataset build。
- 其他平台操作。

会话只对创建者可见，并继承用户创建会话时的 markings。

## AI FDE 的官方最佳实践

[AI FDE best practices](https://www.palantir.com/docs/foundry/ai-fde/best-practices/)
明确建议：

### 人工验证

- 生产前审查生成代码和资源。
- 检查组织工程标准。
- 使用代表性数据测试。
- 确认工具作用后再批准。

### 最小上下文和工具

只提供任务必需的：

- 数据。
- 文档。
- Foundry 资源。
- Capabilities。
- Tools。

过多上下文会降低准确性，也增加安全暴露。

### 分解复杂问题

先建立基础结构，逐步增加复杂性，每一步完成验证。

### 人工完成生产化

官方建议把 AI FDE 用于快速原型和生成基础，
生产质量实现仍应结合人工开发进行优化。

### 使用 Evals

对 LLM-backed Functions 建立评估套件，
持续比较修改是否改善准确率、安全性、延迟和行为。

### 注意基础设施压力

AI FDE 可以在几秒内连续执行大量操作，
多个会话还可能并行运行。

需要关注：

- 存储读写。
- 计算资源。
- GPU。
- 网络。
- 存储容量。

## AIP Evolve

[AIP Evolve](https://www.palantir.com/docs/foundry/aip-evolve/overview/)
可以协调多个 AI FDE Agent，根据目标和评估策略提出模型、成本、
延迟或工作流优化。

截至调研日期，AIP Evolve 仍是 beta。

它代表一个新的方向：

```text
人类定义目标、约束和验证策略
  -> 多个 AI FDE Agent 并行探索修改
  -> 生成 Proposal
  -> 人类检查证据和 Agent 轨迹
  -> 决定是否合并
```

## 人类 FDE 与 AI FDE 对比

| 维度 | 人类 FDE | AI FDE |
| --- | --- | --- |
| 核心目标 | 对客户结果负责 | 自动化 Foundry 内的实现循环 |
| 问题发现 | 进入组织和用户现场 | 根据显式请求与上下文推理 |
| 领域知识 | 可吸收隐性知识和政治约束 | 受提供上下文限制 |
| 信任与谈判 | 可以建立长期关系 | 无法替代 |
| 工程实现 | 跨系统架构、编码和运行 | 调用 Foundry 原生工具 |
| 用户采用 | 培训、组织变更和责任设计 | 可生成材料，但不能独立完成 |
| 权限 | 通过人员和组织流程控制 | 继承当前用户权限并接受 tool approval |
| 变更评审 | 工程与业务评审 | Branch、Proposal、PR 和人工批准 |
| 速度 | 受人类操作节奏限制 | 可高频、并行执行 |
| 风险 | 判断偏差、交付压力、人员依赖 | 幻觉、错误操作、上下文和资源放大风险 |

最合理的协作分工：

```text
人类 FDE：
  定义问题、判断价值、理解组织、设计责任、接受结果

AI FDE：
  探索平台、生成实现、运行验证、准备变更、减少重复操作
```

## AI 时代为什么重新流行

企业 AI 的主要瓶颈往往不再是“有没有模型”，而是：

- 如何接入客户数据。
- 如何连接业务工具和 API。
- 如何建立权限和审计。
- 如何定义 Evals 和上线标准。
- 如何把模型建议放入现有工作流。
- 如何推动用户采用。
- 如何证明业务 ROI。

FDE 正好填补这条生产最后一公里。

## 行业扩散

### OpenAI

[OpenAI FDE 职位](https://jobs.ashbyhq.com/openai/305a4b22-7ff9-4fa5-9229-c6a22c9aa64f)
要求负责：

- Discovery。
- Technical scoping。
- System design。
- Build。
- Production rollout。
- Adoption。
- Eval-driven product/model feedback。

[OpenAI FDSWE](https://jobs.ashbyhq.com/openai/00207abc-49b7-465c-a219-f7c1140f8047)
更偏全栈定制软件和把客户方案抽象成可复用组件。

OpenAI 还按 Healthcare、Legal、Government 和地区细分 FDE，
说明角色正在垂直行业化。

### Anthropic

[Anthropic FDE](https://job-boards.greenhouse.io/anthropic/jobs/5302966008)
要求在客户系统中构建：

- Claude 生产应用。
- MCP servers。
- Sub-agents。
- Agent skills。
- 评估和规模化部署。

同时要求识别并沉淀可重复交付模式。

### Cohere

[Cohere Agentic Platform FDE](https://jobs.ashbyhq.com/cohere/b0bcef37-1d20-414f-aade-c54942d63df9)
负责从模糊问题到生产 Agent 的完整交付，并强调可靠、可观察、安全和可审计。

Cohere 还设置 Infrastructure Specialist FDE，
负责私有云、本地部署、Kubernetes、安全和企业数据环境。

### Databricks

[Databricks Forward Deployed Engineering](https://www.databricks.com/forward-deployed-engineering)
将 FDE 作为正式专家服务，覆盖 Jumpstart、迁移、LLM、
Center of Excellence 和 Custom SOW。

当前
[Databricks FDE 职位](https://databricks.com/company/careers/open-positions/job?gh_jid=8432827002)
明确写明该角色是 billable，并要求产出生产系统、reference architecture、
accelerator 和最佳实践。

这说明 FDE 在不同公司中可以落在不同商业位置：

```text
Palantir：产品交付、账户扩张与研发反馈混合
OpenAI / Anthropic / Cohere：前沿模型进入生产的最后一公里
Databricks：明确的专业服务和平台采用
```

## FDE 模式的风险

### 人力线性扩张

如果每增加一个客户都要永久增加一组 FDE，
业务会更接近专业服务，而不是软件平台。

### 试点无法转化

Palantir SEC 文件披露，公司会自费投入 pilot 和 Bootcamp，
但这些项目可能不会产生长期合同或显著收入。

### 角色边界模糊

FDE 可能同时承担：

- 工程。
- 售前。
- 项目管理。
- 培训。
- 账户扩张。
- 生产支持。

如果不明确优先级，工程师会同时承受销售期限、客户满意和技术质量压力。

### 客户依赖

永久驻场会阻止客户形成自己的平台能力。

健康交付应包含：

- 客户工程师共同开发。
- 文档。
- 培训。
- Runbook。
- 运维交接。
- 清晰退出标准。

### 知识和保密风险

FDE 会接触客户最核心的：

- 数据。
- 工作流。
- 决策规则。
- 组织弱点。
- 业务知识。

需要明确数据边界、知识产权、访问期限、离场清理和跨客户复用规则。

### 安全和伦理风险

医疗、金融、政府和关键基础设施项目中，
快速交付和账户扩张激励可能与最小权限、人工监督和审慎上线产生冲突。

### AI FDE 放大效应

AI FDE 可以更快执行，也会更快放大：

- 错误假设。
- 过大权限。
- 错误代码。
- 构建和计算成本。
- 并行资源竞争。

因此，审批和分支不能只作为 UI 流程，
还必须有真正的代码、数据、安全和业务评审。

## 公司采用 FDE 的检查表

| 问题 | 健康信号 | 风险信号 |
| --- | --- | --- |
| 客户价值 | 高价值、关键工作流 | 低价值、可标准配置 |
| 客户数量 | 少量高价值客户 | 大量小客户 |
| 工作流相似性 | 可抽象共同原语 | 每个客户完全不同 |
| 产品底座 | 强平台和 API | 主要靠项目代码 |
| 定制趋势 | 随时间下降 | 持续增加 |
| 客户能力 | 逐步自助 | 永久依赖 FDE |
| 产品反馈 | 进入路线图 | 现场团队被隔离 |
| 成功指标 | 采用和业务结果 | Demo 和签约 |
| 工程经济性 | 每次交付更快 | 人力和收入线性增长 |

## FDE 项目启动模板

### 业务目标

- 需要改变什么结果？
- 当前基线是多少？
- 谁对结果负责？
- 为什么现在必须解决？

### 工作流

- 当前流程是什么？
- 哪些步骤是人工判断？
- 哪些动作能够真正改变结果？
- 哪些用户必须参与？

### 数据

- 需要哪些数据？
- Source of truth 在哪里？
- 数据质量和刷新要求是什么？
- 哪些字段敏感？

### 技术

- 需要哪些管道、对象、Functions、Actions 和应用？
- 哪些能力应使用平台原语？
- 哪些能力必须定制？

### AI

- LLM 是否真的必要？
- 确定性逻辑应放在哪里？
- 如何建立 Evals？
- 哪些决策必须人工审批？

### 生产

- SLO 是什么？
- 如何监控？
- 如何恢复？
- 谁 on-call？
- 如何处理外部系统失败？

### 采用

- 用户如何培训？
- 谁是业务 owner？
- 如何测量采用率？
- 何时完成交接？

### 产品化

- 哪些产物可以复用？
- 哪些临时代码必须删除？
- 哪些需求应进入产品路线图？
- 如何降低下一个项目的工程投入？

## 学习路线

### 阶段 1：工程底座

- Python 或 TypeScript。
- SQL 和数据建模。
- API、服务和全栈基础。
- Git、测试和 CI/CD。

### 阶段 2：数据平台

- 批流管道。
- Spark。
- 湖仓与查询。
- 数据质量。
- 权限与治理。

### 阶段 3：业务建模

- Domain modeling。
- Ontology。
- Objects、Links、Functions 和 Actions。
- 工作流和 source of truth。

### 阶段 4：AI 生产化

- RAG。
- Agent。
- Tool calling。
- Evals。
- Human-in-the-loop。
- 安全、延迟和成本。

### 阶段 5：交付和产品

- 用户访谈。
- 问题定义。
- Success metrics。
- Scope 和优先级。
- 采用、培训和变更管理。

### 阶段 6：模拟 FDE 项目

选择一个真实场景，例如供应链异常处理：

```text
接入订单和库存数据
  -> 建立 Ontology
  -> 构建短缺预测
  -> 创建重分配 Action
  -> 构建用户应用
  -> 加入 Agent 建议
  -> 设置审批和审计
  -> 运行 Evals
  -> 定义采用和业务指标
```

## 最终判断

FDE 最值得学习的不是岗位名称，而是一种工程原则：

```text
不要把产品、实施、用户和业务结果分成彼此不负责的团队。
让能够构建系统的人直接面对真实问题，
并要求现场经验最终改善通用产品。
```

人类 FDE 解决的是组织、判断和结果闭环。

AI FDE 解决的是平台操作、实现和验证速度。

二者结合后的理想模式是：

```text
人类定义正确的问题、责任和约束
AI 加速可审查的实现循环
平台沉淀可复用能力
客户最终获得可独立运行的系统
```

## 核心资料

- [Palantir Forward Deployed Software Engineer](https://jobs.lever.co/palantir/5168e8fd-fec1-4fea-b7a1-81bdaea65850)
- [Palantir Deployment Strategist](https://jobs.lever.co/palantir/e0ab8226-b928-4e3a-bf87-08fe7b1ea595)
- [Dev versus Delta](https://blog.palantir.com/dev-versus-delta-demystifying-engineering-roles-at-palantir-ad44c2a6e87)
- [A day in the life of an FDSE](https://blog.palantir.com/a-day-in-the-life-of-a-palantir-forward-deployed-software-engineer-45ef2de257b1)
- [Palantir Q2 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm)
- [Palantir AI FDE overview](https://www.palantir.com/docs/foundry/ai-fde/overview/)
- [AI FDE modes and capabilities](https://www.palantir.com/docs/foundry/ai-fde/modes-and-capabilities/)
- [AI FDE security and governance](https://www.palantir.com/docs/foundry/ai-fde/security-and-governance/)
- [AI FDE best practices](https://www.palantir.com/docs/foundry/ai-fde/best-practices/)
- [OpenAI Forward Deployed Engineer](https://jobs.ashbyhq.com/openai/305a4b22-7ff9-4fa5-9229-c6a22c9aa64f)
- [Anthropic Forward Deployed Engineer](https://job-boards.greenhouse.io/anthropic/jobs/5302966008)
- [Cohere Forward Deployed Engineer](https://jobs.ashbyhq.com/cohere/b0bcef37-1d20-414f-aade-c54942d63df9)
- [Databricks Forward Deployed Engineering](https://www.databricks.com/forward-deployed-engineering)
- [The Palantirization of Everything](https://a16z.com/the-palantirization-of-everything/)

## 研究边界

- 招聘信息反映公司希望角色承担的责任，不等于实际员工时间分配。
- 不同地区、行业和安全环境中的 FDE 工作差异很大。
- 公开资料缺少跨公司的 FDE 利用率、毛利、离职率和客户 ROI 数据。
- 行业“FDE 热潮”包含供应商、招聘机构和投资人的叙事，需要与实际生产结果区分。
- AI FDE 能力正在快速更新，具体可用工具应以目标 Foundry enrollment 为准。

