# 来源台账与核验边界

研究日期：2026-11-03。资料只来自公开一手来源，正文把官方事实、AWS 建议和原创教学／方案假设分开。链接指向可变化的网页，不是冻结版本；日期是阅读时点，不能当作每个文档的发布日期。

## 1. 最新公告优先，冲突不抹平

最重要的状态校正：[2026-06-17 发布公告][launch]是 code vulnerabilities gated preview 的历史基线；[2026-10-22 GA 公告][ga]明确该项正式可用，并列 US East（N. Virginia）和 US West（Oregon）。[产品概览][overview]读取时仍带 gated preview 标记。本读本以有日期的新公告更新该项，不把单项 GA 外推到所有功能、地区或 AWS 分区。

GA 公告将代码漏洞修复的人审批放在当前能力中，把自主执行描述为未来。产品概览的渐进自治措辞不是“现在默认自动合并部署”的合同。code scanning、threat modeling 的 preview 标签与[文档历史][history]、[预览计费表][billing]对照阅读。

其他不一致：

- [how-it-works][how]和[full code review 页][code]仍偏 GitHub 表述，[what-is][agent]与[threat modeling][threat]列更多仓库提供商。不要合并成任意能力都支持的全集。
- [resilience][resilience]与[安全最佳实践][best]的 Region 列表不同；后者主要是处理路线，不是统一可用性表。
- [安全 FAQ][guidance]里无 API／调度／CI/CD 的说法，与[CI/CD 专页][cicd]、[调度说明][schedule]和较新的文档历史不同步。
- FAQ 的 confidence 表述与[Pentest finding][findings]、[code finding][code-findings]默认只显示 High 的过滤行为不同。评估空列表前先查过滤。
- [新 Continuum 数据保护][data]明确不覆盖原 Security Agent pentest；[agent 数据保护][agent-data]与[逐功能跨区表][best]必须单独阅读。

处理规则：保留来源和日期；优先按能力的详细文档与有日期发布说明；指出冲突，不虚构统一默认值；重要前提在真实 PoC 前复核当前控制台、文档或正式支持答复。本次没有访问控制台。

## 2. 产品与成本一手资料

| 来源 | 本次读取用途 |
| --- | --- |
| [产品概览][overview]／[功能页][features] | 整体定位、frontier agent 与四项能力区别，标记不同步 |
| [GA 公告][ga]／[历史公告][launch] | 发布时点、code vulnerabilities 两个 Region、人工批准 |
| [Continuum 指南][cv]／[开始前][start] | integrations、environments、GitHub／S3 与 collector 上下文 |
| [触发 scan][trigger]／[查看 issues][issues]／[patches][patches] | 首次副作用、不可取消、加载与生成状态、证据等级和交付区别 |
| [公开定价][pricing]／[计费口径][billing]／[配额][quotas] | task-hours、试用、复测、LOC／CIU、preview 及容量非预算 |
| [威胁建模][threat]／[code review][code]／[pentest][pentest] | 输入、结果、模拟验证、网络、预算和清理边界 |
| [CI/CD][cicd] | 部署后门禁、OIDC、三类失败、fail-open、baseline、取消清理 |

金额只在小型原创算术中使用，不复制官网成本曲线或声称客户实际运行。免费或试用说明不扩展到目标环境与人工。可机器读取的重点台账见 [sources.json](sources.json)。

## 3. 权限、数据与修复资料

- [资源层级][hierarchy]、[角色][roles]、[账户隔离][isolation]、[Collector 服务关联角色][collector]：区分客户账户、Space、操作者、服务与测试身份。
- [安全要求 packs][requirements]：可复用组织要求，但不能据此声称完成合规评估或保证通过审计。
- [凭据][credentials]、[域名验证][domain]、[AWS pentest 政策][policy]：技术证明不替代授权；第三方依赖、运行风险和禁止活动分开核对。
- [新数据保护][data]、[agent 数据保护][agent-data]、[KMS][kms]、[安全最佳实践][best]：分别解释驻留、推理路由、内容用途、访问和加密。
- [Pentest findings][findings]、[code findings][code-findings]、[threat findings][threat-findings]：结果类型、过滤、置信度、成立前提和验证状态。
- [修复许可][enable-repair]、[pentest 修复][repair]、[code 修复][code-repair]、[单项 revalidation][revalidate]：许可与触发分开；生成、交付、合并、部署、复测不能合成一个“已修复”。

附带读取 [PrivateLink][privatelink]与[连接 VPC][vpc]：服务 API 私有接入和代理访问私网目标是不同问题；本读本不提供网络部署模板，也没有假设 PrivateLink 会自动打通目标。

## 4. 基础职责与风险判断

[01 安全基础](security-foundations.md)逐项列 AWS IAM、SCP、Access Analyzer、Config、Security Hub／CSPM、GuardDuty、Inspector、CloudTrail／CloudWatch、KMS、Secrets Manager、WAF 和 Backup 的一手来源。职责比较不是“开齐服务就安全”的选型单。

方法资料：[OWASP 安全测试][owasp-test]、[Threat Modeling Cheat Sheet][owasp-threat]、[WSTG][wstg]；风险与事件响应：[NIST SP 800-30r1][nist-risk]、[SP 800-61r3][nist-ir]；严重性：[FIRST CVSS 4.0][cvss]。这些资料不等于任何客户已经满足合规或完成评估。

官方图标依据 [AWS Architecture Icons][icons]。客户侧治理图是原创逻辑参考，**不是 Continuum 内部部署，也不是内建自动集成**；SVG 含 draw.io 可编辑模型。概念图由本仓库清单和渲染器生成，可离线放大；图中案例、数字、学习顺序和方案合同都是教学设计。

## 5. 四级证据与未执行项

| 层级 | 本次做到什么 |
| --- | --- |
| 官方资料 | 阅读公开产品、操作、价格、发布及方法文档，标记不同步 |
| 原创教学 | 白话解释、重画图、虚构订单服务、客户方案候选和学习评分 |
| 本地验证 | 检查页面与来源链接、图片、导航、搜索、公式；运行标准库练习及测试 |
| 真实客户评估 | **未执行**：不等同前三层，不报告任何真实安全结果 |

未登录 AWS、调用账户 API、创建 environment／Space／角色／密钥／调度、申请服务、扫描代码或目标、运行 pentest、执行生成脚本、部署、安全响应、发送客户推荐或付费。没有收录内部讨论的姓名、时刻、相对排期或附件。Workshop 问题卡和 2–4 周示例计划只是准备材料与原创假设。

客户方案 A–D 的范围、验收与 no-go 来自对能力边界的设计推导，不是 AWS 正式套餐、定价、SLA 或采购建议。真实推进要另行确认适用性、授权、数据许可、预算与负责人。

## 6. 更新这本读本的检查表

先更新 GA／preview 和具体分区、Region，再查权限、数据与集成变化；不要仅换产品名。再核首次扫描、自动调度、门禁失败、任务停止与修复审批默认值。最后核价、额度、计量口径以及客户替代路线。

每次变更应同步正文、图解、sources 台账与实验假设，保留原始不同步记录；测试通过只说明本地内容与合同一致，不证明官方事实永久不变。

[overview]: https://aws.amazon.com/continuum/
[features]: https://aws.amazon.com/continuum/features/
[launch]: https://aws.amazon.com/about-aws/whats-new/2026/06/aws-continuum/
[ga]: https://aws.amazon.com/blogs/aws/aws-continuum-for-code-vulnerabilities-is-now-generally-available/
[cv]: https://docs.aws.amazon.com/continuum/latest/userguide/code-vulnerabilities.html
[start]: https://docs.aws.amazon.com/continuum/latest/userguide/cv-getting-started.html
[trigger]: https://docs.aws.amazon.com/continuum/latest/userguide/cv-triggering-scan.html
[issues]: https://docs.aws.amazon.com/continuum/latest/userguide/cv-viewing-issues.html
[patches]: https://docs.aws.amazon.com/continuum/latest/userguide/cv-viewing-patches.html
[pricing]: https://aws.amazon.com/continuum/pricing/
[billing]: https://docs.aws.amazon.com/securityagent/latest/userguide/pricing.html
[quotas]: https://docs.aws.amazon.com/securityagent/latest/userguide/quotas.html
[agent]: https://docs.aws.amazon.com/securityagent/latest/userguide/what-is.html
[how]: https://docs.aws.amazon.com/securityagent/latest/userguide/how-it-works.html
[history]: https://docs.aws.amazon.com/securityagent/latest/userguide/doc-history.html
[code]: https://docs.aws.amazon.com/securityagent/latest/userguide/perform-code-review-scan.html
[threat]: https://docs.aws.amazon.com/securityagent/latest/userguide/perform-threat-model.html
[pentest]: https://docs.aws.amazon.com/securityagent/latest/userguide/perform-penetration-test.html
[cicd]: https://docs.aws.amazon.com/securityagent/latest/userguide/cicd-pentest.html
[schedule]: https://docs.aws.amazon.com/securityagent/latest/userguide/schedule-penetration-test.html
[hierarchy]: https://docs.aws.amazon.com/securityagent/latest/userguide/understand-lifecycle.html
[roles]: https://docs.aws.amazon.com/securityagent/latest/userguide/create-iam-role.html
[isolation]: https://docs.aws.amazon.com/securityagent/latest/userguide/infrastructure-security.html
[collector]: https://docs.aws.amazon.com/continuum/latest/userguide/using-service-linked-roles.html
[credentials]: https://docs.aws.amazon.com/securityagent/latest/userguide/provide-testing-credentials.html
[domain]: https://docs.aws.amazon.com/securityagent/latest/userguide/enable-test-domain.html
[policy]: https://aws.amazon.com/security/penetration-testing/
[data]: https://docs.aws.amazon.com/continuum/latest/userguide/data-protection.html
[agent-data]: https://docs.aws.amazon.com/securityagent/latest/userguide/data-protection.html
[kms]: https://docs.aws.amazon.com/securityagent/latest/userguide/customer-managed-keys.html
[best]: https://docs.aws.amazon.com/securityagent/latest/userguide/security-best-practices.html
[guidance]: https://docs.aws.amazon.com/securityagent/latest/userguide/security-guidance.html
[resilience]: https://docs.aws.amazon.com/securityagent/latest/userguide/resilience.html
[findings]: https://docs.aws.amazon.com/securityagent/latest/userguide/review-penetration-findings.html
[code-findings]: https://docs.aws.amazon.com/securityagent/latest/userguide/review-code-scan-findings.html
[threat-findings]: https://docs.aws.amazon.com/securityagent/latest/userguide/review-threat-model-findings.html
[enable-repair]: https://docs.aws.amazon.com/securityagent/latest/userguide/enable-remediate-findings.html
[repair]: https://docs.aws.amazon.com/securityagent/latest/userguide/remediate-finding.html
[code-repair]: https://docs.aws.amazon.com/securityagent/latest/userguide/remediate-code-scan-findings.html
[revalidate]: https://docs.aws.amazon.com/securityagent/latest/userguide/revalidate-findings.html
[privatelink]: https://docs.aws.amazon.com/securityagent/latest/userguide/vpc-interface-endpoints.html
[vpc]: https://docs.aws.amazon.com/securityagent/latest/userguide/connect-agent-vpc.html
[owasp-test]: https://owasp.org/www-project-security-culture/v11/7-Security_Testing/
[owasp-threat]: https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html
[wstg]: https://owasp.org/www-project-web-security-testing-guide/v42/2-Introduction/
[nist-risk]: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-30r1.pdf
[nist-ir]: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf
[cvss]: https://www.first.org/cvss/v4.0/user-guide
[icons]: https://aws.amazon.com/architecture/icons/
[requirements]: https://docs.aws.amazon.com/securityagent/latest/userguide/security-requirements.html
