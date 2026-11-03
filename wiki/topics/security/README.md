# 云与应用安全

研究核验：2026-11-03。本专题从安全基础进入 AWS Continuum，再连接客户方案设计。它是公开资料整理和原创教学，不是客户环境评估、合规认证或已执行的渗透测试。

## 从哪里开始

[AWS Continuum 与安全方案 L200](aws-continuum/README.md) 是目前的主读本：9 页、10 张图，从“需要保护什么”讲到“怎样判断一次验证和修复真的完成”。L200 是本 Wiki 定义的中级学习目标，不是 AWS 官方认证，也不声称存在一门对应的官方课程。

建议先读[安全基础](aws-continuum/security-foundations.md)，再读[能力与成本](aws-continuum/continuum-l200.md)。面向客户沟通时，重点看[权限与数据](aws-continuum/permissions-and-data.md)、[验证与修复](aws-continuum/validation-and-remediation.md)和[四种候选方案](aws-continuum/customer-solutions.md)。准备分享或 workshop，可用[学习路线与问题卡](aws-continuum/learning-roadmap.md)。

## 与其他专题连接

- [支付行业的风险与合规](../payments/payment-industry-101.md#lesson-08)：资金、身份、欺诈和系统安全有交集，但不是同一学科。
- [Agentic RL 的工具与环境](../deep-learning/training/agentic-rl-lab/tools-and-environments.md)：工具权限、未可信输入和代理副作用，应与安全证据一起理解。
- [Physical AI 的系统与执行边界](../physical-ai/pollen-robotics/README.md)：软件检查通过不代表物理系统安全；执行与恢复需要另行验收。
- [区块链安全事件解读](../blockchain/binance-security-incident-2026-10-30.md)：学习区分已确认事实、推断、处置措施和尚未核实的说法。

## 阅读边界

本专题不教授攻击载荷，不创建 AWS 资源，不请求产品准入，不接触真实凭据。所有练习使用虚构记录与本地标准库；真正的账户集成、评估、部署和客户推荐都需要单独确认适用性与授权。产品状态、价格、区域、数据处理规则和集成提供商可能变化；以[来源台账](aws-continuum/sources.md)中的能力级核验方法为准。
