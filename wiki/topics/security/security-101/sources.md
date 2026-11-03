# 一手来源、版本与核验边界

研究日期：2026-11-03。本读本只整理公开一手资料：规范发布机构、官方云文档、项目维护者及官方方法指南。每章在结论附近链接来源，并列实读范围；不搬运完整文档、攻击脚本或第三方评测曲线。

## 1. 先区分固定基线与滚动文档

| 选定基线 | 本书的用途 | 不应推出什么 |
| --- | --- | --- |
| [NIST CSF 2.0（2024）][csf] | Govern 到 Recover 的风险结果与组织沟通 | 一份规定全部实现的配置清单 |
| [SP 800-61r3（2025）][ir] | 把响应融入风险管理 | 旧版事件生命周期图就是当前唯一顺序 |
| [FIPS 199（2004）][cia] | 保密、完整、可用与影响概念 | 所有商店都承担相同联邦分类义务 |
| [Privacy Framework 1.0（2020）][privacy] | 数据处理生命周期与隐私风险概念 | 最新版本或完整法律义务清单 |
| [NIST SSDF 1.1（2022）][ssdf] | 安全开发、交付与漏洞响应实践 | 本书声称它一定是最新标准 |
| [SLSA v1.2][slsa]／[provenance/v1][provenance] | 构建来源与验证者信任合同 | SBOM、签名或来源证明单独保证安全 |
| [OWASP API Security 2023][api] | 对象、功能、属性授权与资源风险分类 | 2026 年的真实风险排名 |
| [NIST SP 800-63B-4（2025）][auth] | 认证与会话概念 | 令牌存在就代表业务访问获准 |
| [OWASP LLM 2025 风险资料][llm]／[NIST AI 600-1][ai] | 模型输入、输出、数据与执行风险 | 完全防御提示注入或 Agent 有权执行 |

这些是明确选定的教学基线，不统一声称“最新版”。AWS、GitHub、Kubernetes 和持续维护的 cheat sheets 则按阅读日核验；URL 不构成内容冻结。本次没有固定所有网页快照或产品版本。

## 2. 按章找到来源与研究范围

| 章 | 来源承担的角色 |
| --- | --- |
| [01 治理](01-risk-and-governance.md) | NIST 风险与安全目标、CSF／RMF；AWS 共同责任与 SRA；FIRST CVSS |
| [02 身份](02-identity-and-organization.md) | IAM 评估及边界、SCP、根恢复、MFA、Control Tower；RFC／OIDC 规范 |
| [03 网络](03-network-and-zero-trust.md) | AWS VPC、端点、TLS、WAF、IMDS；NIST SP 800-207 |
| [04 数据](04-data-keys-and-privacy.md) | KMS 授权、secret 轮换、S3 链接和入口；NIST 隐私与 OWASP 生命周期 |
| [05 应用](05-app-and-api-security.md) | OWASP API 与应用控制；NIST 认证会话；AWS 幂等请求机制 |
| [06 供应链](06-devsecops-and-supply-chain.md) | SSDF、SLSA、Sigstore、GitHub、ECR 与 OWASP |
| [07 工作负载](07-workload-and-container-security.md) | EKS／ECS 责任和身份、Kubernetes 约束、Inspector、Runtime Monitoring |
| [08 检测响应](08-detection-and-incident-response.md) | NIST 61r3、AWS 响应指导、CloudTrail／CloudWatch／GuardDuty／Security Hub／SRA |
| [09 Agent](09-ai-and-agent-security.md) | OWASP LLM、NIST AI、Bedrock filtering 与 AgentCore 身份 |
| [10 恢复](10-resilience-and-recovery.md) | AWS DR 目标、四类策略、Vault Lock、restore testing 与额外验证 |

机读重点台账见 [sources.json](sources.json)，完整引用在各章正文末尾。重点台账不是声称穷尽全部资料，也不是一套已通过客户审计的证据库。

## 3. 特别容易过时或拼错的边界

**治理与账号名称。** AWS SRA 是需要适配客户环境的参考；Control Tower 的账户职责、名称和集成会随登陆区版本变化。不要将 SRA 图中的 Log Archive／Security Tooling 名称直接当成每个 Control Tower 版本的默认配置。[SRA 适配说明][sra] [Control Tower 账户][accounts]

**IAM 策略规则。** “策略一律求交集”省略同账户资源策略对用户、角色或角色会话的不同授权路径；SCP 也不覆盖管理账户主体、服务关联角色和全部外部访问。RCP 作用于受支持资源的权限上限，含自己的例外，不是万能补丁。阅读时保留适用范围，不从一句口诀产生生产策略。[权限边界][boundaries] [SCP][scp] [RCP][rcp]

**Kubernetes 旧资料。** EKS Pod Security 指南仍有 PSP 迁移时期表述；目前 Kubernetes 正式资料区分 PSS 与 PSA，enforce 与 audit／warn 不同。本书不照搬旧 PSP 配置，也不声称 namespace 或专属 IAM role 是完整硬隔离。[EKS 指南][podsec] [PSA][psa]

**监测对象。** GuardDuty Runtime Monitoring 的 ECS on Fargate 与 EKS on Fargate 支持不同；CloudTrail Event history 也不是长期、跨组织、包含所有 data events 的完整审计。先问真实覆盖，不把服务已启用当成所有对象已受控。[运行支持][runtime] [Event history][trail]

**事件响应的资料入口。** 一个旧 AWS whitepaper HTML 入口读取时跳转到 Security Incident Response 产品指南；一般响应方法与订阅产品不是同一件事。本书采用可读取的 Well-Architected 准备／操作页及 NIST 61r3，不沿用跳转地址推导一般方法。[准备][prepare] [操作][operations] [NIST][ir]

**备份与验证。** restore testing 会实际创建并清理支持资源，业务 validation 是额外步骤；Vault Lock 两种模式和宽限期后的不可变规则不同。教学例不执行这些动作，也不把示例时间写成 SLA。[测试][testing] [验证][validation] [锁定][lock]

**生成式 AI。** Bedrock prompt-attack safeguards 有输入标记和接口覆盖范围，尤其需要检查 tool result／tool definition 的限制；过滤、IAM 与下游业务授权各管不同边界。元数据过滤不自动成为可信租户授权。[Prompt attack][guardrail] [AgentCore Identity][identity]

**产品与 API 格式。** Security Hub 与 CSPM 的职责及 finding 格式须按对应功能读取，GitHub Actions 的状态检查、部署审批、OIDC claims 也要按当前提供商和配置核对。文档能描述机制，不证明任何客户已经按机制运行。[Security Hub][hub] [GitHub 安全][github]

## 4. 图与练习提供什么证据

16 张图为本 Wiki 原创机制重画：风险、身份、路径、副本、授权、交付、证据类型、工作负载、覆盖、响应、Agent、恢复及学习。它们不是 AWS 官方部署图、产品 UI 截图或已完成的安全测试。

SVG／2× PNG 由本地清单与渲染器生成，提供中文标签、说明与可放大阅读。新对照图使用独立脚注间距，不改旧图字节；既有 Continuum 内容与原生 AWS 图标参考图保留。

标准库 lab 假设元数据可信，比较虚构 owner／tenant；纸面摘要只是动作绑定，不验证审批者、签名或重放；恢复点是否可用也由案例假设给出。测试通过仅说明这些教学例与合同一致，不证明 IAM、应用、Agent 或备份安全。

## 5. 已做与未做

已做：公开资料研究、原创文案与图、虚构案例、自测、纯标准库验算，以及页面、链接、搜索、图片、排版与归档回归检查。

未做：AWS 账户或 API 访问、CLI／STS 身份核验、创建角色／密钥／资源、真实目标或仓库扫描、攻击、Agent／模型运行、依赖安装用于远程代码执行、申请 preview、部署、不可变锁定、生产故障注入、恢复演练、发送客户建议或付费。

没有内部姓名、会议材料、客户数据、真实凭据和未经核实排期。客户候选卡只是纸面练习，任何真实执行都需另行确认授权、范围、数据、身份、预算、停止和恢复责任。

## 6. 后续怎样更新

先检查标准版本与产品适用范围，再同步正文、图、台账和练习假设；不只替换一个产品名。若官方说明不同步，列出日期与差异，不拼出万能默认值。若没有覆盖或没有实际证据，明确标“未知／未验证”，不靠绿色面板补齐。

[csf]: https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf
[ir]: https://csrc.nist.gov/pubs/sp/800/61/r3/final
[cia]: https://csrc.nist.gov/pubs/fips/199/final
[privacy]: https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.01162020.pdf
[ssdf]: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-218.pdf
[slsa]: https://slsa.dev/spec/v1.2/provenance
[provenance]: https://slsa.dev/spec/v1.2/build-provenance
[api]: https://owasp.org/API-Security/editions/2023/en/0x11-t10/
[auth]: https://pages.nist.gov/800-63-4/sp800-63b.html
[llm]: https://genai.owasp.org/llmrisk/llm062025-excessive-agency/
[ai]: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
[sra]: https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/introduction.html
[accounts]: https://docs.aws.amazon.com/controltower/latest/userguide/special-accounts.html
[boundaries]: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html
[scp]: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html
[podsec]: https://docs.aws.amazon.com/eks/latest/best-practices/pod-security.html
[psa]: https://kubernetes.io/docs/concepts/security/pod-security-admission/
[runtime]: https://docs.aws.amazon.com/guardduty/latest/ug/runtime-monitoring.html
[trail]: https://docs.aws.amazon.com/awscloudtrail/latest/userguide/view-cloudtrail-events.html
[prepare]: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/preparation.html
[operations]: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/operations.html
[testing]: https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing.html
[validation]: https://docs.aws.amazon.com/aws-backup/latest/devguide/restore-testing-validation.html
[lock]: https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html
[guardrail]: https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-prompt-attack.html
[identity]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity-terminology.html
[hub]: https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub-v2.html
[github]: https://docs.github.com/en/actions/reference/security/secure-use
[rcp]: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_rcps.html
