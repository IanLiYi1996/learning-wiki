# AWS Context：一手来源与证据边界

核查日期：2026-11-24（Asia/Shanghai）。来源沿用同日公开资料调研；本次 Wiki 整理不宣称重新测试服务，也不把图件当作部署证据。

## 证据分级

- **官方描述：** 产品定位和设计承诺，不代替正式接口、安全合同或实测结果。
- **公开状态核查：** 已读取页面中的发布阶段；检索未命中不能证明不存在。
- **原创分析：** 职责对照、教学场景、选型建议与 PoC 设计。
- **未执行：** 账号接入、控制台检查、模型调用、部署、付费云资源或生产安全验证。

## S1

[AWS Machine Learning Blog：Context intelligence for your data and AI agents at scale](https://aws.amazon.com/blogs/machine-learning/context-intelligence-for-your-data-and-ai-agents-at-scale/)

- 发布日期：2026-06-17，与 S2 交叉核对。
- 支持：Coming soon 标注、业务上下文图、API/MCP 接入方向、人工治理、使用反馈、Iceberg/S3 和权限设计。
- 不支持：完整接口清单、底层图引擎、性能验证或正式开放状态。

## S2

[AWS Machine Learning Blog：Mailan Lee 作者索引](https://aws.amazon.com/blogs/machine-learning/author/mailan/)

- 支持：S1 的发布日期交叉核对。
- 不作为服务开放状态或功能规格证据。

## S3

[AWS News Blog：Top announcements of the AWS Summit in New York 2026](https://aws.amazon.com/blogs/aws/top-announcements-of-the-aws-summit-in-new-york-2026/)

- 发布日期：2026-06-17。
- 支持：与 S1 同期的 Coming soon 标注、数据关系与知识图谱、运行时 agentic search 的定位。

## S4

[AWS What's New：Context Ontology Accelerator 发布公告](https://aws.amazon.com/about-aws/whats-new/2026/07/aws-context--ontology-accelarator-generally-available/)

- 发布日期：2026-07-31。链接中的双连字符与拼写按实际页面保留。
- 支持：COA 开源可获取；自定义 ontology 的 Context 原生全托管能力在该公告中仍为未来事项。
- **不支持 Context 托管服务自身 GA。** 也不能用 7 月公告直接证明 11 月的全部状态。

## S5

[AWS CloudTrail：Logging network activity events](https://docs.aws.amazon.com/en_us/awscloudtrail/latest/userguide/logging-network-events-with-cloudtrail.html)

- 支持：AWS Context 的 `context.amazonaws.com`、`context-mcp.amazonaws.com` 事件源记录。
- 本次页面未显示该服务条目的加入日期。
- 不据此推导可调用 endpoint、IAM prefix、区域、API 工具或 GA。

## S6

[AWS IAM：Service Authorization Reference](https://docs.aws.amazon.com/service-authorization/latest/reference/reference.html)

- 用途：IAM 文档检索入口。
- 本次检查不是完整逐服务枚举，不据此证明 Context IAM 文档不存在。

## S7

[AWS CLI：命令参考目录](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/index.html)

- 本次呈现目录未出现 Context 命令。
- 不据此排除受限接口或全部 SDK 支持。

## S8

[Boto3：服务参考目录](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/index.html)

- 本次正文提取只显示部分内容，未完成服务枚举。
- 专用 Context client 未确认，但不能写成“不存在”。

## S9

[Amazon Bedrock：Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)

- 支持：知识检索、图与结构化数据源接入，以及当前 Managed Knowledge Base 的多步检索与推理。
- 不支持 Context 的完整集成合同，也不能简化成“RAG 只做向量检索”。

## S10

[Amazon Bedrock AgentCore：Memory](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory.html)

- 支持：短期交互事件和长期记忆的定位。
- 不支持 Context 内部实现，也不代表正式政策可从会话中自动推断。

## S11

[AWS Glue：Getting started with business context](https://docs.aws.amazon.com/glue/latest/dg/catalog-business-context-getting-started.html)

- 支持：Data Catalog 的业务术语、资产元数据、语义搜索、Agent skill，以及本次页面的 preview 标注。
- 不据此确认其与 Context 的数据模型和定义权威来源。

## S12

[AWS 官方 COA 文档](https://aws.github.io/context-ontology-accelerator/)

- 支持：自管理方案、语义建模、复核与 Agent 使用流程。
- 不将示例组件或性能外推到 Context 托管服务。

## S13

[AWS 官方 COA GitHub 仓库](https://github.com/aws/context-ontology-accelerator)

- 支持：源码入口与部署到用户 AWS 账户的自管理方式。
- 不支持 Context 托管服务的价格、安全、性能或 SLA。

## 检索与可用性边界

原调研检查 AWS 官网、What's New、官方文档、AWS GitHub、CLI 与 Boto3 目录。未采用社区文章、搜索摘要或第三方 Marketplace 内容作为产品承诺。

候选产品路径 `https://aws.amazon.com/context/` 与 `https://aws.amazon.com/aws-context/` 在本次工具访问中未取得正文；这不是已验证 HTTP 404，不能排除其他路径或受邀开放。

本轮未确认独立定价、区域、配额、完整 API/MCP 清单或账号级接入。公开资料可更新；有新公告时应复核来源日期和状态，而不是把旧页的 Coming soon 当作永久结论。
