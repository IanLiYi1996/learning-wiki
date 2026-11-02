# 一手来源与核验边界

读取日期统一为 **2026-11-02**；研究日期不是所有原件的发布日期。本专题只用标准制定者、监管／央行、方案运营方、公司自己的产品文档或披露支持事实。网页会更新，执行具体项目时需重新查适用版本。

正文的短标签可跳到这里。历史机制资料不冒充 2026 年全部规则快照；产品文档不代表各地区都可用；国际标准不自动等于本地法律。

## 13–22 补全章节的来源索引

下面链接进入各章的完整引用表；表中记录读取日、司法辖区或产品边界。正文就近引用同一批一手资料，避免读完后还不知道哪个说法由哪个来源支持。原有 01–12 的短标签保持不变。

| 章节 | 重点证据 |
| --- | --- |
| [13 卡产品与账户运营](chapters/13-card-products-and-operations.md#public-sources) | CFPB、卡网络更新服务、EMVCo、欧盟卡体系定义 |
| [14 线下与离线支付](chapters/14-in-person-and-offline-payments.md#public-sources) | EMVCo、PCI SSC、受理方离线规则 |
| [15 订阅与周期性付款](chapters/15-recurring-payments.md#public-sources) | 欧盟认证要求、卡网络及提供方续费和取消机制 |
| [16 商户生命周期](chapters/16-merchant-lifecycle.md#public-sources) | 网络商户分类、支付方接入与准备金规则 |
| [17 资金与流动性](chapters/17-treasury-and-liquidity.md#public-sources) | CPMI／央行、结算和 FX 风险资料 |
| [18 报文与支付安全](chapters/18-messages-and-payment-security.md#public-sources) | ISO、Swift、EMVCo、PCI SSC、AWS |
| [19 账本与可靠工程](chapters/19-ledgers-and-reliable-payment-engineering.md#public-sources) | 账本、数据库和事务消息的一手技术文档 |
| [20 中国与监管地图](chapters/20-china-and-regulatory-maps.md#public-sources) | 中国政府／央行／基础设施及美、英、欧、新监管 |
| [21 现金与移动货币](chapters/21-cash-mobile-money-and-local-methods.md#public-sources) | GSMA、移动货币方案、现金与本地支付运营资料 |
| [22 CBDC、存款与稳定币](chapters/22-cbdc-tokenised-deposits-and-stablecoins.md#public-sources) | BIS、央行、银行与发行人的权利和赎回说明 |

## 基础、银行卡与商业模式

<a id="cpmi"></a>

- **CPMI** — BIS／CPMI，[CPMI glossary](https://www.bis.org/committees/cpmi/glossary)。支持清算、结算、信用转账和直接借记等基础术语。正文的“三条流”是教学整理，不是标准原文术语。

<a id="money"></a>

- **MONEY** — 英国央行，[Money in the modern economy: an introduction](https://www.bankofengland.co.uk/quarterly-bulletin/2014/q1/money-in-the-modern-economy-an-introduction)，2014-03-14。支持存款是银行负债等基础说明；不提供所有钱包／数字资产的全球法律分类。

<a id="card-life"></a>

- **CARD-LIFE** — Adyen，[Payments lifecycle](https://docs.adyen.com/account/payments-lifecycle/)。支持授权、捕获、结算与出款区别及异常状态。`Settled` 是该产品状态；不要当成所有服务商同名字段都完全一致。

<a id="interchange"></a>

- **INTERCHANGE** — Visa，[Understanding Visa Interchange Rates](https://www.visa.ca/en_CA/support/small-business/interchange.html)。支持交换费在收单与发卡之间分配、MDR 与交换费不同；页面具体费率为加拿大资料，正文不采用其报价。网络不取得交换费收入的解释也可对照下项公司披露。

<a id="visa-2025"></a>

- **VISA-2025** — Visa 的 [FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/1403161/000140316125000089/v-20250930.htm)，年度截至 2025-09-30。支持四方角色、非直接发卡授信、收入类别与客户激励。只取固定报告期的业务结构，不声称它是读取日最新年报。

<a id="adyen-2025"></a>

- **ADYEN-2025** — Adyen，[H2 2025 financial results](https://www.adyen.com/press-and-media/adyen-publishes-h2-2025-financial-results-3pgu2)，发布 2026-02-12。全文报告期为 2025 全年：净收入 €2,364.2m，处理量 €1,394.3bn；`2,364.2 / 1,394,300 ≈ 0.00169562`，换成百分比约 0.1696%，换成 bps 约 16.96。派生比率为本读本计算，非商户报价；披露中的净收入属于其自定义非 IFRS 指标范围，不能直接跨公司套用。

<a id="payfac"></a>

- **PAYFAC** — Mastercard，[Find a payment facilitator](https://www.mastercard.com/mea/en/business/support/payment-facilitators.html)。支持 PayFac 依收单安排为子商户提供服务的角色定义；不将展示名单当所有国家的合资格名单。

<a id="mor"></a>

- **MOR** — Stripe，[Determine and configure the merchant of record](https://docs.stripe.com/connect/merchant-of-record)。支持面向买家的交易与责任主体区别；不是对具体公司的税务或法律裁定。

<a id="connect"></a>

- **CONNECT** — Stripe，[Understand how charges work in a Connect integration](https://docs.stripe.com/connect/charges)。支持 charge、transfer、平台／连接账户余额与退款拒付责任差异。主文档中的费用和责任是 Stripe 产品规则，不是所有 PSP 的统一安排。部分专题 URL 会返回变体索引，采用可读取的总说明。

## 凭证、钱包、发卡与工程

<a id="qr"></a>

- **QR** — EMVCo，[EMV QR Codes](https://www.emvco.com/emv-technologies/qr-codes/)。支持二维码的呈现／数据模式区别；不把二维码本身当结算网络。

<a id="token"></a>

- **TOKEN** — EMVCo，[EMV Payment Tokenisation](https://www.emvco.com/emv-technologies/payment-tokenisation/)。支持 PAN 替代、限定使用场景及 Token 生命周期；不把服务商 Vault Token、虚拟卡或链上 Token 混同。

<a id="apple-pay"></a>

- **APPLE-PAY** — Apple，[Privacy — Features](https://www.apple.com/privacy/features/)，Apple Pay 小节；另参考官方 [Apple Pay security and privacy overview](https://support.apple.com/en-ca/101554)。支持 Device Account Number 与真实卡号隔离。Support 页面读取出现 429，使用可读取的 Apple 官方隐私页面交叉核验；不据此描述全部 Apple 资金产品。

<a id="jit"></a>

- **JIT** — Marqeta，[Just-in-Time Funding](https://www.marqeta.com/platform/jit-funding)。支持按业务规则参与授权与实时资金安排这一产品方向。Managed JIT 与 Gateway JIT 能力不同，正文不称所有模式都让客户逐笔决定。

<a id="card-controls"></a>

- **CARD-CONTROLS** — Stripe，[Issuing spending controls](https://docs.stripe.com/issuing/controls/spending-controls)。支持金额、商户类别等控制及适用限制；部分功能是预览版，不默认全部开放。

<a id="idempotency"></a>

- **IDEMPOTENCY** — Stripe，[Idempotent requests](https://docs.stripe.com/api/idempotent_requests.md)。支持重试、键保存及参数一致性。API v1 与 v2 规则有差异，正文不将“同一个键”说成无限期防重，也未照网页指令安装 Stripe 插件或调用支付 API。

<a id="webhooks"></a>

- **WEBHOOKS** — Stripe，[Receive Stripe events in your webhook endpoint](https://docs.stripe.com/webhooks)。支持事件重复、不保证顺序、签名验证和异步处理。文档能证明该提供方行为，不能证明所有消息系统采取相同投递语义。

## 账户支付与跨境

<a id="fast-payments"></a>

- **FAST-PAYMENTS** — CPMI，[Developments in retail fast payments and implications for RTGS systems](https://www.bis.org/publications/developments-retail-fast-payments-and-implications-rtgs-systems.pdf)，2021，§2.3、§3 与表 1。支持客户即时可用与银行间结算模式的区别；不声称已复核全部网络 2026 年结算周期。

<a id="ach"></a>

- **ACH** — 美联储，[Automated Clearinghouse Services](https://www.federalreserve.gov/paymentsystems/fedACH_about.htm)；Nacha，[RMAG Originator Essentials](https://www.nacha.org/sites/default/files/2024-10/RMAG_Originator_Essentials.pdf)，2024。美国 ACH 信用／借记、批量与退回等机制；历史操作说明不替代当前完整规则。

<a id="fedwire"></a>

- **FEDWIRE** — Federal Reserve Financial Services，[Fedwire Funds Service Business Continuity Guide](https://www.frbservices.org/financial-services/fedwire-funds-service/fedwire-funds-service-business-continuity-guide)。支持美元银行间 RTGS 与最终性。未在正文采用可能变动的运行时段。

<a id="fednow"></a>

- **FEDNOW** — 美联储，[FedNow Additional Questions and Answers](https://www.federalreserve.gov/paymentsystems/fednow-additional-questions-and-answers.htm)，尤其 Q6、Q16–20、Q22–23。支持即时基础设施、账户与流动性安排、美国境内范围和互联边界。

<a id="rtp"></a>

- **RTP** — The Clearing House，[RTP institution information](https://www.theclearinghouse.org/payment-systems/rtp/institution)；美联储，[Order on RTP joint account balances](https://www.federalreserve.gov/paymentsystems/files/interest_on_rtp_joint_balances.pdf)，2023。支持美国 RTP 的推款、预注资与私营网络安排；不是“实时支付”的通用网络名称。

<a id="pix"></a>

- **PIX** — 巴西央行，[SPI Annual Report 2024](https://www.bcb.gov.br/content/financialstability/spi_annual_reports/SPI_2024.pdf)，pp.4–6、16；另对照 FAST-PAYMENTS。支持 Pix 与 SPI 的层次、跨机构结算安排；不把所有同机构 Pix 交易或跨境扩展都归入相同路径。

<a id="upi"></a>

- **UPI** — 上述 CPMI 2021 [FAST-PAYMENTS](https://www.bis.org/publications/developments-retail-fast-payments-and-implications-rtgs-systems.pdf)，表 1／§3，对印度 UPI 的运营与结算机制说明。NPCI 部分页面访问受限，因此不补写未核验的当前限额、周期、信用或钱包扩展。

<a id="paynow"></a>

- **PAYNOW** — 新加坡银行公会／方案资料，[PayNow Singapore](https://www.abs.org.sg/e-payments/pay-now)。支持别名寻址、FAST 关联与参与者范围；官方互联走廊不代表全球自动互通。

<a id="sepa"></a>

- **SEPA** — European Payments Council，[What is a payment scheme?](https://www.europeanpaymentscouncil.eu/what-we-do/epc-payment-scheme-management/what-payment-scheme) 和 [SEPA Instant Credit Transfer](https://www.europeanpaymentscouncil.eu/what-we-do/sepa-instant-credit-transfer)。支持规则层与信用／借记／即时转账区别。未据动态计数控件显示的“0”推断参与者数量，也不列全部法规实施时点。

<a id="open-banking"></a>

- **OPEN-BANKING** — 英国 FCA，[Account information and payment initiation services](https://www.fca.org.uk/consumers/account-information-payment-initiation-services)。支持 AISP／PISP 功能与用户同意；英国制度例子，不外推全球资格与责任规则。

<a id="china-network"></a>

- **CHINA-NETWORK** — 中国银联，[企业概况](https://www.unionpay.com/upowhtml/cn/templates/upOverview/upOverview.html)；中国银行，[网络支付“断直连”公告](https://www.boc.cn/ebanking/bi2/201901/t20190107_14545670.html)，2019-01-07。支持角色与后台连接演进；不使用网站覆盖规模，不把该银行历史公告当作所有平台 2026 年的全路径核验。

<a id="swift"></a>

- **SWIFT** — SWIFT，[Who we are](https://www.swift.com/about-us/who-we-are)。支持金融报文网络与资金／账户责任区别。

<a id="cross-border"></a>

- **CROSS-BORDER** — CPMI，[Correspondent banking — final report](https://www.bis.org/publications/correspondent-banking-final-report.pdf)，2016，§2.1 与 §3.5.2；另对照 PVP。支持代理行、往来账户与信息／资金路径。历史 MT 报文例子不作为 2026 年当前迁移状态。

<a id="pvp"></a>

- **PVP** — CPMI，[Facilitating increased adoption of payment versus payment — final report](https://www.bis.org/publications/facilitating-increased-adoption-payment-versus-payment-pvp-final-report.pdf)，2023，§1–3。支持 FX 本金风险、PvP、流动性与预注资边界；不称所有走廊均已支持。

<a id="pfmi"></a>

- **PFMI** — CPSS／IOSCO，[Principles for financial market infrastructures](https://www.bis.org/publications/principles-financial-market-infrastructures.pdf)，2012，原则 1、8。支持最终性与法律基础，国际标准不是本地法律替代。

<a id="cips"></a>

- **CIPS** — 跨境清算公司，[加入 CIPS／了解 CIPS](https://www.cips.com.cn/kjjqgs/jrcips/index.shtml)。支持跨境批发清算定位、混合结算与流动性安排；正文不采用参与者数量、运行时间或当前全币种范围。

## 风险、安全、客户资金与新场景

<a id="3ds"></a>

- **3DS** — EMVCo，[EMV 3-D Secure](https://www.emvco.com/emv-technologies/3-D-secure/)；Stripe，[3DS authentication flow](https://docs.stripe.com/payments/3d-secure/authentication-flow)。支持认证与授权区分、无感／挑战流程及责任转移边界。

<a id="pci"></a>

- **PCI** — PCI SSC，[How does PCI DSS apply to EMVCo Payment Tokens?](https://www.pcisecuritystandards.org/faq/articles/Frequently_Asked_Question/how-does-pci-dss-apply-to-emvco-payment-tokens/) 和 [TSP FAQs v1.0](https://www.pcisecuritystandards.org/documents/FAQs_for_TSP_Requirements_v1.pdf)，后者 2015-12。支持 Token 分类与范围条件；旧 FAQ 仅用作分类，不宣称旧评估程序为现行版本。

<a id="fatf"></a>

- **FATF** — FATF，[The FATF Recommendations](https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Fatf-recommendations.html)，本次读取的 [PDF](https://www.fatf-gafi.org/content/dam/fatf-gafi/recommendations/FATF%20Recommendations%202012.pdf.coredownload.inline.pdf) 封面标注 Updated October 2025。重点参考 Recommendation 10；不声称已核验所有本地反洗钱法，也不照抄完整规范。

<a id="cdd"></a>

- **CDD** — 美国 FinCEN，[CDD Final Rule](https://fincen.gov/resources/statutes-and-regulations/cdd-final-rule)。支持尽调、受益所有人、关系目的与持续监测的区别；只作为美国受覆盖机构框架示例。

<a id="sanctions"></a>

- **SANCTIONS** — 美国 OFAC，[FAQ 73](https://ofac.treasury.gov/faqs/73)。支持制裁对象／交易与一般身份核验不同；不提供全球清单或逐笔法律结论。

<a id="safeguarding"></a>

- **SAFEGUARDING** — 英国 FCA，[Using payment service providers](https://www.fca.org.uk/consumers/using-payment-service-providers)。支持客户资金保障与 FSCS 存款保障不同、返还可延迟等提醒；英国非银行支付机构例子，不外推各地保险待遇。

<a id="disputes"></a>

- **DISPUTES** — Stripe，[How disputes work](https://docs.stripe.com/disputes/how-disputes-work)。支持卡争议、证据流程与责任；不把卡拒付复制给所有钱包／账户支付。

<a id="refunds"></a>

- **REFUNDS** — Stripe，[Refund and cancel payments](https://docs.stripe.com/refunds) 与 [Place a hold on a payment method](https://docs.stripe.com/payments/place-a-hold-on-a-payment-method)。支持退款与未捕获取消差异；不统一到账时间。账单上 reversal 也可能是早期退款的呈现，不应只看字样判断。

<a id="billpay"></a>

- **BILLPAY** — BILL，[AP payment disbursement methods](https://developer.bill.com/docs/ap-payment-disbursement-methods)。支持企业付款可采用多种执行方式。产品中的单次虚拟卡等限制不是全部虚拟卡的通则。

<a id="bnpl"></a>

- **BNPL** — 美国 CFPB，[What is a Buy Now, Pay Later loan?](https://www.consumerfinance.gov/ask-cfpb/what-is-a-buy-now-pay-later-bnpl-loan-en-2119/)，页面 last reviewed 2024-05-21。仅支持信用产品的基础理解，不用于描述 2026 年全部监管保护。

<a id="stablecoins"></a>

- **STABLECOINS** — FSB，[High-level Recommendations for Global Stablecoin Arrangements — final report](https://www.fsb.org/uploads/P170723-3.pdf)，2023-07-17。支持治理、储备／流动性、赎回与跨境监管关注；属于建议，不证明某币符合要求。

<a id="usdc"></a>

- **USDC** — Circle，[USDC Terms](https://www.circle.com/legal/usdc-terms)，本次读取页面更新为 2026-10-15。支持赎回资格和产品风险；该条款有辖区边界，不用于替代 EEA 等不同安排。

<a id="agent-payments"></a>

- **AGENT-PAYMENTS** — Visa，[Trusted Agent Protocol](https://developer.visa.com/docs/trusted-agent-protocol) 及 [Specifications](https://developer.visa.com/docs/trusted-agent-protocol/trusted-agent-protocol-specifications)。支持代理信任与消息完整性方向；旧 use-case URL 重定向，采用当前入口。不声称全商户普及或协议已解决结算／法律责任。

<a id="ap2"></a>

- **AP2** — Google Cloud，[Powering AI commerce with the new Agent Payments Protocol](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol?hl=en)，2025-09-16。支持签名委托及多支付方式的设计方向；公告不是普遍生产部署保证。

## 核验范围与限制

- 正文事实来自这里列出的公开一手来源，不复制非公开材料或内部部署信息。
- 没有核验所有国家的牌照、支付限额、运行窗口、费率与消费者保护。
- 没有按读取日给支付公司财务或股价排名；仅有明确标记的固定报告期示例。
- 没有证据表明示例企业已采用正文的云架构或已有采购项目。
- 研究读取日期不等于所有来源的发布日期；动态产品与监管规则需在实际使用前重新确认。
