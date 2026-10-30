# 2026-10-30 币安安全事件：一手证据与技术解读边界

- 查询日期：2026-10-30；本文时间统一使用北京时间 UTC+8。
- 阅读与核对窗口：北京时间约 13:00–13:30，不是实时监控。
- 金额快照：TRM 为 08:30；Aave 主回应为 09:00；币安公告未明确网页显示时间的时区，不擅自换算。
- 发布范围：公开研究笔记；不包含附件 PPT、原文提取或截图。
- 方法：直接阅读官方公告、协议规范和风险服务商公告；关键交易浏览器页返回 403，未读取其完整内容，未运行节点重放、逐笔验签或攻击复现。

## 1. 可以确认的事件身份

币安官方公告承认安全事件，估计影响约 63 亿美元、已冻结约 30 亿美元。初步调查怀疑 DevOps 工程师电脑被入侵后，攻击者进入服务容器并提交未经授权的提现。公告称尚未发现钱包私钥泄漏证据，并承诺后续技术报告。[S1]

“没有发现泄漏证据”不等于已经证明私钥绝无泄漏；初步入口解释不等于完整取证结论。不能据此填入恶意软件名称、CVE、IAM 策略、容器平台或具体签名供应商。[S1]

本案不是 2019 年 7,000 BTC 热钱包事件，也不是 2022 年 BSC Token Hub 跨链证明验证事件。白话正文见[事件解读](../binance-security-incident-2026-10-30.md)，历史一手材料及金额口径见[历史消歧笔记](binance-incident-disambiguation-2026-10-30.md)。

## 2. 时间线与证据分层

| 北京时间 | 事件 | 证据层级 |
| --- | --- | --- |
| 10-30 04:05 起 | TRM 观察到跨十条链的资金流出，主要集中在约二十分钟内 | 调查机构链上归集，不是本次独立复算。[S2] |
| 04:20 左右 | TRM 描述以太坊钱包的 7702 委托及包含五十项预签授权的交易 | 机构调查；本次未取得并逐项验签该授权交易。[S2] |
| 04:24 左右 | Aave 回应所链接的交易 `0x53bd…e2f3`，据其报告转出约 167,464 ETH 与 63 种代币 | 风险服务商报告及公开交易链接；浏览器页受访问限制，未独立复核执行轨迹。[S4] |
| 04:58–05:01 | LlamaRisk 报告攻击地址在 Aave 抵押 6,000 万 USDT，借出 19,762 WETH | 协议风险服务商的一手回应。[S4] |
| 05:42–07:04 | Aave guardian 执行多网络 reserve freeze | 协议风险服务商一手回应。[S4] |
| 08:08 | Arbitrum 安全委员会执行紧急资产转移 | 官方应急公告；本次读取公告及其交易链接，未独立重放升级动作。[S5] |
| 午间媒体更新 | Cointelegraph 转述币安称充值正常，提现预计四十八小时内恢复 | 二手运营状态；不是已经恢复提现的证明。[S6] |

币安首份公告中的“暂停充值与提现”应描述为初始措施，不能拿它否定后续状态更新。[S1]、[S6]

## 3. 金额怎么读

TRM 按转出时的币价估算约 63.6 亿美元，覆盖十条链；币安称“估计影响”约 63 亿美元。机构对地址的归属判断、统计范围、价格时间和冻结进度可能不同。[S1]、[S2]

必须分开四个口径：

1. 原始未经授权转出资产及其估值；
2. 此刻受限制或被冻结的资产；
3. 已实际归还受害方的资产；
4. 完成对账、追偿、赔付后的净损失。

这是本文的会计口径分析，不是币安已经公布的最终对账。不能把攻击地址当前余额当成原始盗款，更不能把借来的 WETH 再算一遍交易所原始损失。

Arbitrum 原公告使用 **8,425 ETH、74,559,805.2 ARB**；TRM 使用 8,426 ETH，两者有小幅差异，本文未独立核销。引用本次应急处置数量优先使用处置方原公告，不将差异擅自归因为舍入。[S2]、[S5]

## 4. 攻击路径：哪些成立，哪些仍然缺证据

公开材料支持以下拼接，但两个环节之间的内部过程仍未公开：

```text
币安初步披露：
工程师电脑受侵 → 进入内部服务容器 → 提交未经授权提现
                                      │
                         内部审批/签名如何被滥用：待取证
                                      │
TRM 的链上判断：
多链有效签名与资金转移 ────────────────┘
以太坊另使用 7702 委托 → 调用被委托钱包 → 资产流出
```

这不是“十条区块链同时被破解”的证据。TRM 据多链签名交易判断签名基础设施可能遭滥用；币安尚未公开完整根因。[S1]、[S2]

HSM/KMS 保存私钥和批准业务是两件事。AWS 文档用作通用例子：私钥不以明文离开 KMS，但有权限的调用者可以请求对消息或摘要签名。若业务策略在签名前没有独立验证意图，“钥匙没被拿走”仍可能发生“盖章服务被冒用”。**不据此断言币安使用 AWS KMS 或某个特定 HSM。**[S7]、[S8]

## 5. 7702 的关键机制

EIP-7702 引入类型 `0x04` 的 set-code 交易。钱包签署授权元组，节点将账户代码设为委托指示器，执行时在该账户上下文运行目标代码。委托持续存在，可用新的有效授权替换或清除；交易执行部分回滚不会撤销已经处理的委托。[S9]

授权包含 `chain_id`、代码地址、`nonce` 和签名。无效元组跳过；有效授权会递增授权账户的 nonce；同一账户最后有效的委托生效。连续 nonce 授权并不保证“恰好只有一项有效”，也不保证账户 nonce 已越过整个覆盖区间后仍能匹配。[S9]

TRM 报告五十项预签授权。在教学中可解释为对繁忙钱包不断变化的序号做覆盖，不是爆破密码；五十项不是五十个独立审批人。[S2]、[S9]

TRM 报告先设置委托，之后调用被委托账户转出资产。[S2] 因此应区分“先获得委托授权”和“后调用已委托账户”。

通用机制举例：一笔外层 `Value = 0 ETH`、由其他地址发起的调用，也可能通过被委托账户的内部执行转出该账户资产；调用阶段不需要每次重新设置委托。这是基于规范的教学示例，**不写成本次已独立确认的交易字段**。只看外层 ETH 数额、只监控由交易所钱包发起的交易，都不足以覆盖此类执行效果。[S9]

EIP-7702 的用途包括批处理、代付 gas 和更细的权限实现。它不是天然盗币漏洞；风险在于签到错误委托代码或签名/审批路径失守。规范本身已警告不安全的委托实现可导致账户被近乎完全控制。[S9]

## 6. 冻结不是回滚，借贷也不是原始盗窃

USDC 的发行方 Circle 明确保留链上 blocklisting 能力。该能力限制特定代币的未来转移，并不抹去历史交易，也不代表地址里的 ETH 一并被冻结。[S10]

Arbitrum 的应急机制不同：安全委员会原子升级 Ethereum 上的 Inbox，加入发送者覆盖能力，注入两笔代表攻击者地址的跨链交易，将资金转至 `0x0000000000000000000000000000000000000DA0`，再恢复 Inbox。公告称后续移动须 ArbitrumDAO 治理投票。不能把这写成普通矿工可以强行移动任何以太坊主网资产。[S5]

Aave 借出的实际是 WETH。它是超额抵押借款，不是本次已经证明的 Aave 合约盗窃。LlamaRisk 当时认为该仓位有足额抵押且按正常规则可清算；这是时点判断，不是永久无风险保证。[S4]

冻结 Aave reserve 与拉黑 USDT 地址也不是同一件事：前者阻止新供给和新借款，仍保留偿还、提现和清算。提现仍受池内流动性等正常条件限制。[S4]

止损有副作用：LlamaRisk 的第二份说明称，退出和禁止新供给提高了部分池子利用率，借款利率上升，并建议临时调整 Slope2。文件摘要与部分具体参数表并不完全一致，本文不重复其“所有池子满利用率统一为 10%”概括，更不声称建议已执行。[S11]

## 7. 归因、赔付与待公开证据

TRM 高置信度归因为 TraderTraitor，但未在文章里公开全部链上和链下情报。本笔记写“TRM 的归因”，不写执法机构已最终确认。[S2]

币安承诺动用 SAFU 与公司资金覆盖损失，整改后更新储备证明。这个承诺既不等于盗款已追回，也不是本次已经完成偿付能力审计。[S1]

需要等待的关键材料：

- 初始入侵方式、恶意软件及凭据/会话影响范围；
- 服务容器与签名服务之间的认证、授权、审批边界；
- 五十项授权的原始交易、请求日志及实际生效范围；
- 多链签名器的隔离方式与是否存在共同控制入口；
- 资产完整清单、冻结重叠、追回进度与赔付对账；
- 清除委托之外，关联 executor/module 权限是否全面处置；
- 执法归因和恢复服务后的验证结果。

这些是本文提出的核验问题，不暗示上述控制一定不存在。

## 8. 防御性学习结论

以下是基于公开证据提出的设计建议，不是对币安内部实现的事实断言：

- 签名前独立解析链、账户、实际收款人、资产、金额与代码权限变更，不能仅检查摘要格式。
- 提现授权、7702 委托、合约管理与任意消息签名分开处理；不需要的权限默认拒绝。
- 人员终端、部署权限、策略审批和签名能力分离，并覆盖多链共因风险。
- 对钱包全部资产减少、代码变化和合约 executor 权限建立告警，不只看顶层 `From`/`Value`。
- 给高额资产流出设置组合限速、独立复核与冷钱包分层，明确可用性代价。
- 应急方案分别处理基础设施凭据、钱包委托、关联权限、充提路径及冻结伙伴；单独暂停前端按钮未必覆盖已公开授权。

## 9. 来源

- [S1：Binance Security Incident Update](https://www.binance.com/es/support/announcement/detail/c5a8729a97ac486d963784d96c5642d7)——该语言路径展示英文正文；英文路径检索工具访问失败，使用可读取路径。
- [S2：TRM Labs 的本案调查](https://www.trmlabs.com/resources/blog/north-korea-steals-usd-6-36-billion-from-binance-in-the-largest-hack-in-history)
- [S3：Aave 所链接的大额转出交易](https://etherscan.io/tx/0x53bd38b816c23e74134786c29a8c18d792777998a3b9326047b583100e88e2f3)——返回 403，只作待核验链接，不声称已读取。
- [S4：LlamaRisk 在 Aave 论坛的回应](https://governance.aave.com/t/binance-hot-wallet-exploit-aaves-response/25954)
- [S5：Arbitrum 官方应急公告](https://forum.arbitrum.foundation/t/security-council-emergency-action-30-10-2026/31625)
- [S6：Cointelegraph 实时更新](https://cointelegraph.com/news/binance-linked-wallet-faces-possible-exploit-blockchain-researcher-warns)——仅用于后续运营状态的二手转述，不作为技术根因证据。
- [S7：AWS KMS Sign API](https://docs.aws.amazon.com/kms/latest/APIReference/API_Sign.html)
- [S8：AWS KMS 密钥规格说明](https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-choose-key-spec.html)
- [S9：EIP-7702 原始规范](https://eips.ethereum.org/EIPS/eip-7702)
- [S10：Circle USDC 条款](https://www.circle.com/legal/usdc-terms)
- [S11：LlamaRisk 临时利率调整说明](https://governance.aave.com/t/risk-stewards-temporary-slope2-reductions-on-aave-v3-and-aave-v4-2026-10-30/25955)
- [S12：Ethereum 的 7702 集成指南](https://ethereum.org/roadmap/pectra/7702)
- [S13：Ethereum Foundation 的 Pectra 公告](https://blog.ethereum.org/en/2025/04/23/pectra-mainnet)

技术来源与第三方调查的陈述均不视为本次独立逐链验算。新闻检索曾尝试长桥 CLI，但刷新凭据已过期，因此未取得长桥新闻数据；未读取凭据文件、登录、交易、转账或修改任何外部系统。

[S1]: https://www.binance.com/es/support/announcement/detail/c5a8729a97ac486d963784d96c5642d7
[S2]: https://www.trmlabs.com/resources/blog/north-korea-steals-usd-6-36-billion-from-binance-in-the-largest-hack-in-history
[S3]: https://etherscan.io/tx/0x53bd38b816c23e74134786c29a8c18d792777998a3b9326047b583100e88e2f3
[S4]: https://governance.aave.com/t/binance-hot-wallet-exploit-aaves-response/25954
[S5]: https://forum.arbitrum.foundation/t/security-council-emergency-action-30-10-2026/31625
[S6]: https://cointelegraph.com/news/binance-linked-wallet-faces-possible-exploit-blockchain-researcher-warns
[S7]: https://docs.aws.amazon.com/kms/latest/APIReference/API_Sign.html
[S8]: https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-choose-key-spec.html
[S9]: https://eips.ethereum.org/EIPS/eip-7702
[S10]: https://www.circle.com/legal/usdc-terms
[S11]: https://governance.aave.com/t/risk-stewards-temporary-slope2-reductions-on-aave-v3-and-aave-v4-2026-10-30/25955
[S12]: https://ethereum.org/roadmap/pectra/7702
[S13]: https://blog.ethereum.org/en/2025/04/23/pectra-mainnet
