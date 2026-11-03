# 云与应用安全

研究核验：2026-11-03。本专题先建立安全体系，再进入 AWS Continuum 与客户方案设计。它是公开资料整理和原创教学，不是客户环境评估、合规认证或已执行的渗透测试。

## 从哪里开始

[云与应用安全体系 101 → L200](security-101/README.md) 是基础读本：十章、14 页、16 张机制图。覆盖风险治理、身份与组织、网络与零信任、数据密钥与隐私、应用 API、DevSecOps 与供应链、工作负载与容器、检测响应、AI／Agent、韧性恢复，附[学习路线](security-101/learning-roadmap.md)与[离线实验](security-101/lab.md)。

[AWS Continuum 与安全方案 L200](aws-continuum/README.md) 保留原来的 9 页、10 张图，从产品能力到验证修复与客户方案。101／L200 都是本 Wiki 定义的学习目标，不是 AWS 官方认证，也不声称存在对应官方课程。

第一次学习建议从体系读本的[风险治理](security-101/01-risk-and-governance.md)和[身份](security-101/02-identity-and-organization.md)开始。已经了解基础、准备讨论产品时，可直接读 Continuum 的[能力与成本](aws-continuum/continuum-l200.md)。面向客户沟通时，重点看[权限与数据](aws-continuum/permissions-and-data.md)、[验证与修复](aws-continuum/validation-and-remediation.md)和[四种候选方案](aws-continuum/customer-solutions.md)。

## 按问题选入口

| 你想搞清楚什么 | 从这里读 |
| --- | --- |
| 登录、租户与工具为什么还要授权？ | [身份](security-101/02-identity-and-organization.md)、[API](security-101/05-app-and-api-security.md)、[Agent](security-101/09-ai-and-agent-security.md) |
| 内网、加密和容器为什么不足以证明隔离？ | [网络](security-101/03-network-and-zero-trust.md)、[数据](security-101/04-data-keys-and-privacy.md)、[工作负载](security-101/07-workload-and-container-security.md) |
| 扫描、SBOM、签名、PR 各能证明什么？ | [供应链](security-101/06-devsecops-and-supply-chain.md)、[Continuum 修复](aws-continuum/validation-and-remediation.md) |
| 告警之后怎样做，备份怎样验收？ | [检测响应](security-101/08-detection-and-incident-response.md)、[恢复](security-101/10-resilience-and-recovery.md) |
| 怎样准备客户方案或分享？ | [体系学习路线](security-101/learning-roadmap.md)、[workshop 问题卡](aws-continuum/learning-roadmap.md) |

## 与其他专题连接

- [支付行业的风险与合规](../payments/payment-industry-101.md#lesson-08)：资金、身份、欺诈和系统安全有交集，但不是同一学科。
- [Agentic RL 的工具与环境](../deep-learning/training/agentic-rl-lab/tools-and-environments.md)：工具权限、未可信输入和代理副作用，应与安全证据一起理解。
- [Physical AI 的系统与执行边界](../physical-ai/pollen-robotics/README.md)：软件检查通过不代表物理系统安全；执行与恢复需要另行验收。
- [区块链安全事件解读](../blockchain/binance-security-incident-2026-10-30.md)：学习区分已确认事实、推断、处置措施和尚未核实的说法。

## 阅读边界

本专题不教授攻击载荷，不创建 AWS 资源，不请求产品准入，不接触真实凭据。所有练习使用虚构记录与本地标准库；真正的账户集成、评估、部署和客户推荐都需要单独确认适用性与授权。标准与产品可能变化；分别查[体系来源](security-101/sources.md)和[Continuum 来源](aws-continuum/sources.md)，不要把框架、教学例或产品说明当成真实安全证明。
