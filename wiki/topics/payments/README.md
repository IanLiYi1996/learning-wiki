# 支付行业 101：从一杯咖啡到全球资金网络

整理日期：2026-11-02。基于支付网络、中央银行、标准组织、监管与服务商的公开一手资料，按“业务直觉 → 原理 → 商业 → 风险 → 工程”组织。

从一笔买咖啡的支付开始，理解谁批准付款、谁承担资金责任、钱如何到账，以及支付公司怎样赚钱。全专题共 22 课、32 张中文机制图：01–12 是连续主干读本，13–22 是补全产品、运营、工程和地区视角的独立章节。术语在首次出现时解释，计算与架构示例明确标为教学假设。

## 开始阅读

- [主干图文读本：01–12 课](payment-industry-101.md)：适合顺序阅读，不需要先背缩写。
- [领域补全：13–22 课](#extension-map)：卡产品、线下与订阅、商户运营、资金管理、报文安全、可靠账本、中国监管、现金和数字货币。
- [术语速查](glossary.md)：中文解释、英文缩写与常见误区。
- [学习路线与自测](learning-roadmap.md)：45 分钟主干速读、两周学习、岗位选读、纸上实验与答案。
- [一手来源与核验边界](sources.md)：结论出处、适用地区与报告期。

## 01–12：先建立主干

| 课 | 你会搞懂什么 |
| --- | --- |
| [01 支付是什么](payment-industry-101.md#lesson-01) | 钱、账户、凭证、网络与三条流 |
| [02 银行卡的一生](payment-industry-101.md#lesson-02) | 授权、请款、清算、结算、对账和异常 |
| [03 商户受理生态](payment-industry-101.md#lesson-03) | Acquirer、Processor、Gateway、PSP、PayFac、MoR |
| [04 费用与商业模式](payment-industry-101.md#lesson-04) | MDR、Interchange、TPV、Take Rate、利润与现金 |
| [05 钱包与发卡](payment-industry-101.md#lesson-05) | 余额、凭证、Token、虚拟卡和消费控制 |
| [06 账户与实时支付](payment-industry-101.md#lesson-06) | A2A、ACH、RTGS、区域方案、开放银行与中国生态 |
| [07 跨境与企业支付](payment-industry-101.md#lesson-07) | SWIFT、往来账户、FX、预注资、PvP、CIPS、AP/AR |
| [08 风险与合规](payment-industry-101.md#lesson-08) | 认证、欺诈、AML、制裁、PCI、客户资金与争议 |
| [09 账本与支付工程](payment-industry-101.md#lesson-09) | 状态机、幂等、Webhook、复式记账和对账 |
| [10 研究一家支付公司](payment-industry-101.md#lesson-10) | 责任链、财务口径与技术需求证据 |
| [11 稳定币与代理](payment-industry-101.md#lesson-11) | 嵌入式支付、信用产品、新 Rail 与代理权限 |
| [12 完整平台案例](payment-industry-101.md#lesson-12) | 把产品、资金、风险、账务和工程拼起来 |

<a id="extension-map"></a>

## 13–22：把缺少的十个视角补上

每章都有机制图、具体例子、易错点、三道自测及答案，来源直接放在章节末尾。可以按顺序读，也可以从工作中遇到的问题进入。

| 课 | 新补的领域 | 你会回答的问题 |
| --- | --- | --- |
| [13 卡产品与账户运营](chapters/13-card-products-and-operations.md) | 信用／借记／预付、账单与额度、三方／四方、换卡 | 刷的是谁的钱？换卡后订阅为什么还在？ |
| [14 线下、终端与离线支付](chapters/14-in-person-and-offline-payments.md) | EMV、NFC、SoftPOS、L1–L3、断网受理 | 手机能收款就不用认证？离线成功由谁承担风险？ |
| [15 订阅与周期性付款](chapters/15-recurring-payments.md) | CIT／MIT、同意、SCA、更新、重试与取消 | 首次支付成功后，为什么不能随意反复扣款？ |
| [16 商户生命周期](chapters/16-merchant-lifecycle.md) | KYB、承保、MCC、监控、准备金与退出 | 接入商户之后，退款和风险由谁继续管？ |
| [17 资金与流动性管理](chapters/17-treasury-and-liquidity.md) | 预注资、净额、币种账户、FX、压力情景 | 公司有钱，为什么某个国家此刻仍付不出去？ |
| [18 报文、密码与支付安全](chapters/18-messages-and-payment-security.md) | ISO 8583／20022、HSM、PIN、密钥生命周期 | 格式兼容和加密正确，为什么还不够安全？ |
| [19 账本与可靠支付工程](chapters/19-ledgers-and-reliable-payment-engineering.md) | 可用／冻结、并发、Outbox／Inbox、补偿与恢复 | 如何避免双花、重复出款和恢复后丢账？ |
| [20 中国支付与监管地图](chapters/20-china-and-regulatory-maps.md) | 银行、银联、网联、备付金、CIPS、司法辖区 | 中国支付链路怎样拆？出海需要核对哪些法律主体？ |
| [21 现金、移动货币与本地方法](chapters/21-cash-mobile-money-and-local-methods.md) | Cash-in／out、代理现金与电子余额、ATM、支票、代金券 | 没有银行卡或智能手机的人怎样完成支付？ |
| [22 CBDC、代币化存款与稳定币](chapters/22-cbdc-tokenised-deposits-and-stablecoins.md) | 央行货币、银行负债、发行人、赎回和最终性 | 同样叫“数字货币”，持有人究竟对谁有权利？ |

这是一张学习覆盖地图，不是宣称全球所有支付产品、规则和例外都已穷尽。先读主干，再用补全章节把具体问题放回角色、资金与责任链。

## 阅读约定

- **外部核验**：正文附近链接到公开一手来源。
- **教学示例**：交易、费率、账务与架构用于说明机制，不是生产测量。
- **待验证假设**：技术或商业机会需要合同、牌照、财报与项目证据。

主要目标是建立可迁移的行业理解，不是全球牌照或法规大全。证券结算、完整信贷风控与各国税务不在展开范围；监管段落不是法律意见，财务段落不是投资建议。

## 配图与关联阅读

图解提供本地 SVG 源图与 2× PNG，无图片热链。网页可点击放大，Markdown 和离线导出使用 PNG 后备。图示不代表任何公司的实际部署。

重建本专题配图，不改其他主题：

```bash
python scripts/render_figures.py --embed --id-prefix payment-
python scripts/render_figures.py --check --id-prefix payment-
```

继续阅读：[区块链与钱包工程](../blockchain/README.md)，对照传统支付与链上资金轨道。两者的凭证、最终性、资金权利与消费者保护不能机械互换。
