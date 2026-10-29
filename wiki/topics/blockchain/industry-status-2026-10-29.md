# 区块链行业现状：技术、产品与风险地图

- 截点与核验日：2026-10-29（北京时间，UTC+8）。
- 前置：[零基础扫盲](beginner-guide.md)。本篇解释“现在发展到哪里”，不重复全部基础定义。
- 范围：一手规范、维护者文档、产品条款、具名商业公告和监管发布；不提供投资排名、当前行情或个体合规结论。
- 状态：资料核验，未运行节点、实测支付、访问用户钱包或核查链上 feature gate。
- 更新方式：保留本篇日期；后续变化另记截点，不把过去的官方目标改成已实现事实。

## 1. 先给出判断：它已经不只是发行币，但也没有消除中间机构

下面是根据本篇具名证据得到的**归纳**，不是全行业规模测量：

1. 基础协议仍在演进，关注点包括账户可编程、数据可用性、执行吞吐和最终性。Ethereum、Solana 的当前升级证据分别见第 3、4 节。
2. 稳定币已有部分商户收款、机构结算和预充值产品；具体覆盖并不等于所有国家、所有支付环节都已上线。见第 6 节。
3. 代币化基金已有产品证据，但基金管理、登记、资格、底层资产和兑付仍存在链外机构。见第 7 节。
4. 钱包、跨链和服务生命周期仍是重要边界；资产上链不使权限、数据或退出风险消失。见第 5、8 节。
5. 监管框架在部分法域更加明确，但成法、发布规则、生效、许可和全球可用是不同状态。见第 10 节。

最有用的问题因此不是“区块链有没有用”，而是：**在哪个环节有可核验的收益，增加了哪些责任，失败时怎样恢复或退出。**

## 2. 按职责看行业，不按币价排座次

| 层次 | 提供什么 | 初学者重点检查 | 本篇证据入口 |
| --- | --- | --- | --- |
| 基础网络 | 记账、共识、执行、结算 | 规则、验证者/矿工、状态及运行版本 | Bitcoin、Ethereum、Solana，第 3–4 节及下文 |
| 扩容与连接 | 批处理、数据、跨链消息/资产 | 证明对象、数据、排序器、升级/退出权限 | 第 5 节 |
| 基础设施 | RPC、索引、预言机、签名服务 | 数据完整性、版本、供应商故障与生命周期 | 第 5、8 节 |
| 账户与控制 | 钱包、自托管、托管、AA | 谁能签、谁能升级、恢复与撤销 | 第 8 节 |
| 金融与支付 | 交换、借贷、稳定币、结算 | 收益来源、兑付、流动性与资格 | 第 6–7 节 |
| 新应用 | 身份、游戏、隐私、机器支付等 | 真实需求、实现范围、非链上依赖 | 第 9 节 |
| 治理和监管 | 协议协调、机构责任、许可 | 权限、生效时间、适用主体和地域 | 第 10 节 |

这是一张分析地图，不是声称各赛道都拥有相同规模或商业成熟度的统计表。

### Bitcoin：协议、软件与金融敞口要分开

Bitcoin 的资产/UTXO、PoW、累计工作量链选择仍是理解它的基础；本文用固定源码学习，不把旧审计版本当安装建议。官方发布页在核验日列 **Bitcoin Core 32.1**，其发布说明特别指出 32.0 虽打 tag，但未完成正式发布。软件版本升级，不等于发行规则自动改成另一套。[Core 32.1 发布说明](https://bitcoincore.org/en/releases/32.1/)；[当前目标检查源码](https://github.com/bitcoin/bitcoin/blob/v32.1/src/pow.cpp)。

钱包工程的关注点包括描述符、PSBT、Taproot/MuSig2 协作签名、中继/替换策略及测试网身份；Lightning 通过支付通道扩展付款能力，但引入通道资金、路由、流动性和链上争议处置边界。它们不能都理解为“换一种地址格式”。完整对象和故障路径见 [Bitcoin 新版教程](upgrades/06-bitcoin-wallets.md)，一手规范入口见 [Bitcoin/Lightning 来源](sources.md)。

金融机构产品、平台余额和直接自托管 BTC 又是不同控制关系。本文不因存在机构产品就推断 BTC 获得价格保证，也没有核查 ETF 份额、机构持仓或当前挖矿收益。

## 3. Ethereum：已上线的变化与下一次升级必须分开

### 已上线：Pectra 与可编程账户

官方记载 **Pectra 于 2025-05-07 主网上线**。EIP-7702 允许外部控制账户设置代码委托，从而支持可编程钱包能力。它不是把旧账户简单换成新币，也不表示每个钱包自动拥有相同恢复与费用代付方案。[Pectra](https://ethereum.org/roadmap/pectra/)；[EIP-7702](https://eips.ethereum.org/EIPS/eip-7702)。

对用户重要的新边界是**持续授权**：委托可跨交易存在，执行失败不自动撤销已经处理的委托。4337 的 UserOperation、Bundler、EntryPoint 和 Paymaster 则是另一套应用层机制；“免 gas”通常有人代付，并非网络处理不需要成本。[7702 规范](https://eips.ethereum.org/EIPS/eip-7702)；[ERC-4337](https://eips.ethereum.org/EIPS/eip-4337)。

### 已上线：Fusaka 与 PeerDAS

官方记载 **Fusaka 于 2025-12-03 上线**，核心变化之一是 PeerDAS，即对 blob 数据可用性进行分布式采样/保管。它旨在支持更多扩容数据，而不是让每个节点无限制地下载、保存全部数据。[Fusaka](https://ethereum.org/roadmap/fusaka/)；[EIP-7594](https://eips.ethereum.org/EIPS/eip-7594)。

**Blob**是为这类数据发布设计的数据对象，不是“把智能合约放进一个更大文件就自动执行”。数据可用性、执行证明、基础链最终性和历史数据留存仍是不同问题。PeerDAS 的设计能力不等于所有 L2 已经实现同样低的费用或端到端到账时间。

本篇不引用即时 blob target/max 或网络 gas 上限：官方介绍中的示例、升级配置和实时区块参数可能有不同口径。需要实现级数值时，应核对对应版本配置及链上状态；[完整升级教程](upgrades/01-ethereum.md)已解释这些区分。

### 尚未核实主网上线：Glamsterdam，Hoodi 已延期

这是本次重新查阅的重要纠偏。路线图仍显示开发网测试、Q4 2026 主网预期与一个 Hoodi 日期；但 **2026-10-22 的 Ethereum Foundation 延期公告**明确取消原定 **2026-10-26** 的 Hoodi 激活及配套 200M gas 调整，尚未设定替代日期。不能因为原计划日期已过，就宣称 Hoodi 或主网完成升级。[路线图](https://ethereum.org/roadmap/glamsterdam/)；[延期公告，优先于旧排期](https://blog.ethereum.org/2026/10/22/glamsterdam-hoodi-delay)。

设计内容可以完整认识，但状态要单列：

- **ePBS，协议内提议者/构建者分离**：提议者选择执行载荷承诺，构建者交付内容，协议处理相关付款及及时性证据。目的是调整职责和信任边界，不是取消区块内容验证。
- **BAL，区块级访问列表**：记录执行涉及的账户/存储访问及相关状态变化，帮助客户端并行读取、验证和计算状态。
- **状态创建/访问重新计费**：更明确地计入长期存储和访问成本，避免吞吐增长把节点负担隐蔽地转嫁出去。

这些是升级设计，不是本篇对主网新增性能的实测。[官方机制介绍](https://blog.ethereum.org/2026/10/16/glamsterdam-hoodi-announcement)。该旧公告顶部也追加了延期说明，并称主网日期未定；延期撤销的是未来激活配置，不是回滚 Hoodi 已有历史。

## 4. Solana：执行、共识、交易格式是三条升级轴

当前英文官方页称 **Alpenglow 在 2026-10-21、epoch 1064 启用**。Votor 替换旧 TowerBFT 共识路径，以直接投票和证书处理最终性；SVM 程序执行没有被替换。Rotor 的传播改动仍为后续阶段，不能计入已上线能力。[Alpenglow 当前页](https://solana.com/upgrades/alpenglow)。

对普通读者，重点不是记住所有证书名字，而是理解：

- “执行过”与“全网最终接受这个执行结果”是不同证据。
- 官方约 150ms 是目标最终性，不是你每笔付款必达的服务承诺。
- 当前官方迁移说明中 `confirmed`与`finalized`语义等价，但不保证两个通知同时到达，更不能重复入账。

这些是官方状态/接口说明，本次没有测量主网延迟或核验每家 RPC。[官方升级与集成说明](https://solana.com/upgrades/alpenglow)；[Anza commitment 定义](https://docs.anza.xyz/consensus/commitments)。

另一个独立变化是 **v1 交易格式**：官方记载 2026-09-15 启用，v1 可到 4096 字节；旧 legacy/v0 继续可用，不能把其原有限制也放宽。发送旧格式与读取链上所有新格式，是两项不同兼容任务。[大交易上线页](https://solana.com/upgrades/larger-transaction-sizes)；[格式对照](https://solana.com/docs/core/transactions/versioned-transactions)。

重试也要用真实有效高度等规则，而不是把旧 slot 时长乘成固定秒数。交易被最终确认，也仍可能是执行失败的结果。完整解析、候选身份及故障流程见 [Solana 新版教程](upgrades/02-solana.md)。

## 5. 多链现状：互联不等于共享安全，产品也会退役

理解多链，要分别问“计算资源从哪来”“谁提供安全”“谁提供数据”“谁证明消息”“谁控制退出”。以下变化是有出处的代表性案例，不是所有网络清单：

| 对象 | 核验日可写的状态 | 应升级的旧认知 |
| --- | --- | --- |
| Polkadot Coretime | 当前文档描述 bulk 与 on-demand 资源调度；多 core 的 elastic scaling 仍须按具体部署确认。[官方文档](https://docs.polkadot.com/reference/polkadot-hub/consensus-and-security/agile-coretime/) | 不再只靠长期插槽拍卖解释资源取得；资源购买、共享安全和消息格式分开。 |
| Cosmos Hub | 当前文档明确 Gaia v28 移除 ICS provider，旧 consumer 操作指南不再适用；IBC 路由仍是另一项功能。[当前 Hub 说明](https://docs.cosmos.network/hub/latest/getting-started/what-is-gaia) | 不能凭仍在线的 ICS 文档就认定今天仍可按旧流程接入 Hub 共享安全。 |
| Polygon zkEVM Mainnet Beta | 官方记载 2026-07-03 sequencer 退役；专门 Claims 针对 EOA-held 资产，不能覆盖合约锁定资产。[官方退役/回收说明](https://polygon.technology/polygon-zkevm) | 不把旧部署推荐当现行服务，也不把专门回收路径当所有资产保证。 |
| AMB | AWS 记载 2026-10-29 起不接纳新客户，2027-09-29 结束支持。[AWS 生命周期公告](https://docs.aws.amazon.com/managed-blockchain/latest/hyperledger-fabric-dev/managed-blockchain-end-of-support.html) | 原有“用 AMB 接入”的架构需要迁移计划；签名服务与节点/索引服务是不同设施。 |

还有一些长期成立的边界：EVM 兼容不自动等于相同费用、权限或最终性；rollup/validium/侧链不能按品牌互换；跨链消息可验证不保证接收应用逻辑正确；原生币与桥接凭证不自动拥有同样退出路径。[Ethereum 扩容](https://ethereum.org/developers/docs/scaling/)、[桥风险](https://ethereum.org/developers/docs/bridges/)。

迁移应该保留“构造、签名、广播、扫描、对账”各自的能力契约，不是假装存在一个全功能无差别替代产品。具体机制和验收见 [多链新版教程](upgrades/03-multichain.md)、[AWS 迁移教程](upgrades/05-aws-infrastructure.md)。

## 6. 稳定币支付：哪些已有实际产品证据

先区分支付链上的不同环节：消费者支付、商户收款、机构清偿债务、预先为跨境付款备资、最终收款人兑现。链上某个环节上线，不证明整个链路都由同一稳定币完成。

| 案例 | 证据与阶段 | 不应扩大成的结论 |
| --- | --- | --- |
| Stripe 稳定币收款 | 当前文档提供启用和集成流程；客户付稳定币，完成付款结算到商户 Stripe 余额中的本地货币。[接入文档](https://docs.stripe.com/payments/stablecoin-payments) | 所有地区商户都能启用；商户一定持有稳定币；资金提现已由本次实测。 |
| Visa 美国 USDC 结算 | 2025-12-16 公告称 Cross River Bank、Lead Bank 已开始使用；扩大覆盖是当时计划。[历史公告](https://corporate.visa.com/en/sites/visa-perspectives/newsroom/visa-launches-stablecoin-settlement-in-the-united-states.html) | 所有 Visa 刷卡都上链；2026 扩大计划必然已完成。 |
| Visa Direct/Inyo | 2026-10-15 公告明确稳定币预充值进入商业生产，面向符合条件的客户/合作方。[商业上线公告](https://investor.visa.com/news/news-details/2026/Visa-Direct-Launches-Stablecoin-Powered-Money-Movement-as-Pilots-Move-to-Production/default.aspx) | 全部稳定币 payout 功能、全部地区都上线；最终收款者一定收到 USDC。 |

本次归纳是：**部分支付/机构资金环节已经有生产或产品证据，但仍与传统账户、合规和兑换设施组合使用。**这不是“稳定币取代银行”的证据，也没有证明当前零售支付占比。

用户需要继续检查的是原生/包装资产身份、兑付资格、手续费、退款与争议机制、银行端到账、冻结以及业务主体。USDC 和 USDT 的条款不能互相套用；直接赎回与在市场卖出不同。[USDC 条款](https://www.circle.com/legal/usdc-terms)；[Tether 条款](https://tether.to/en/legal/)。

这里没有把 Visa 旧公告中的年化速度数字改成年份更新后的“当前交易额”。历史数字、观察日期及报告范围详见 [来源审计](notes/beginner-industry-source-audit.md)。

## 7. RWA：代币化基金已经存在，但权利并不凭技术自动成立

**RWA**泛指用链上系统表达与现实资产有关的记录或权益。本篇实际核验的是基金份额案例，不替房地产、私人信贷等所有类别作成熟度保证。

两项具名证据：

- **BUIDL/Tempo**：2026-07-30 参与方公告声明基金在 Tempo 可用，面向合资格投资者，配合 Securitize 转让代理等设施。披露明确这是基金份额，不是稳定币，也不是对组合中某项资产的直接所有权。[部署公告及披露](https://investors.securitize.io/news/news-details/2026/Tempo-expands-onchain-yield-offering-with-BlackRocks-BUIDL-fund/default.aspx)。
- **FOBXX/BENJI**：Franklin Templeton 当前页面说明 BENJI 与基金份额的关系，官方持有人记录仍由转让代理的区块链集成系统维护。基金的 1 美元目标份额净值不构成保本或存款保险。[产品及风险说明](https://www.franklintempleton.com/about-us/digital-assets/digital-assets-technology)。

为了不混淆，记住四种身份：

| 身份 | 实际关系 | 需要另外查的事 |
| --- | --- | --- |
| 支付稳定币 | 针对参照货币的发行/赎回机制 | 发行主体、储备、兑付资格 |
| 代币化银行存款 | 银行存款的数字化记录或表达 | 账户关系、适用保护、访问规则 |
| 代币化基金份额 | 对基金的权益 | 资格、资产管理、官方登记和赎回 |
| DeFi 金库 shares | 对策略资产的份额 | 换算率、损失、合约及退出条件 |

以上是对象区分，不对任一具体账户的法律保护作判断；基金和金库证据见上方产品文件及 [ERC-4626](https://eips.ethereum.org/EIPS/eip-4626)，美国法律中的对象区分见第 10 节。

链上可转移和链外可赎回不是同一服务时钟。发行许可、白名单、托管、权利文件、估值和违约处置不会因为上链而消失。本篇不填写当前基金规模、收益率或实时赎回速度。

## 8. 钱包与 DeFi：功能更可编程，风险也更可组合

当前官方接口已经覆盖合约账户、4337 操作、7702 委托、代币授权和金库份额。用户体验可以包含批量操作、代付与恢复，但一个账户能否安全使用这些功能，要看实际实现、模块、权限和费用承担者，而不能只看“智能钱包”标签。[ERC-4337](https://eips.ethereum.org/EIPS/eip-4337)、[EIP-7702](https://eips.ethereum.org/EIPS/eip-7702)、[Safe 权限模型](https://docs.safe.global/advanced/smart-account-concepts)。

DeFi 的基础对象可以先按真实接口学习：

- **交换/做市**：Uniswap 当前文档区分多个版本，AMM、集中流动性、hooks 等不是同一个模型。旧 v2 恒定乘积例子适合扫盲，不足以描述所有新池子的权限和执行规则。[当前机制入口](https://developers.uniswap.org/docs/get-started/concepts/how-uniswap-works)。
- **抵押借贷**：Aave 的健康因子和清算文档说明抵押、债务和阈值关系；参数、市场及功能需按部署核验。不能用一张教程的阈值充当所有资产的当前参数。[健康因子](https://aave.com/help/borrowing/liquidations)。
- **份额型收益产品**：ERC-4626 定义 shares/assets 接口；损失、费用、限额与舍入可能影响兑换，不意味着底层资产或收益有担保。[ERC-4626](https://eips.ethereum.org/EIPS/eip-4626)。

我的风险归纳是：可组合性增加效率，也增加依赖路径。如果一个金库持有另一协议的凭证，而那个协议依赖预言机、桥或托管方，最外层“合约正常”不证明全部底层可兑现。这是根据上述对象关系推导的分析，不是对某个协议安全的实测。

本篇不使用未核验的 TVL 排名、实时 APY、协议收入或漏洞损失总额，也没有把 v4 文档存在视为所有网络部署都完成。

## 9. 隐私、身份、游戏、机器支付：用证据分级看新应用

新应用不应只按“AI+链”“游戏+链”等标签评估。至少把四种状态区分开：

```text
设计/标准
  → 开发者接口或可用产品
  → 具名客户的生产部署
  → 同口径、可复核的持续使用和经济结果
```

前一层不自动证明后一层。本篇有支付生产公告，但没有做游戏、身份、存储/DePIN 等全部赛道的规模调查，因而不把它们统一称为“已经大规模落地”。

**机器/Agent 支付**有具体开发接口例子：Coinbase 当前 x402 文档描述，在请求流程里展示价格、验证和结算付款后提供数字服务，买方可以是人或机器。它证明存在这种集成方式，不证明自主 Agent 商业模式已普遍成立，也不使 Agent 获得无限付款权限。[x402 文档](https://docs.cdp.coinbase.com/x402/welcome)。

对这类产品应追加预算、可调用目标、资产/网络、授权范围、重复请求、退款和审计限制。这里是安全设计建议，没有连接 AI 钱包或执行 x402 付款。

**隐私**也应独立判断：链上公开数据、身份信息存储、证明泄露什么、谁有查看/冻结权限，各自需要证据。“ZK rollup”主要说明有效性证明路线，不能单凭名称宣称交易内容对外保密。[ZK rollup 数据与证明模型](https://ethereum.org/developers/docs/scaling/zk-rollups/)。

## 10. 监管：成法、发布、生效、许可是四个不同动作

这里只介绍公开制度状态，不判断读者或某个产品依法可用。法域、经营主体、资产类别和具体业务必须另外核验；面向中文写作不代表中国内地、香港或其他地区拥有同一规则。

### 欧盟：MiCA 已有适用规则，但不是全部资产的统一许可证

EUR-Lex 的官方摘要记载，ART/EMT 相关规则自 **2024-06-30** 适用，一般规则自 **2024-12-30** 适用。EMT 针对单一官方货币的稳定价值表达，ART 涉及其他资产/资产篮子；受既有金融服务法规范的金融工具等，不因“上链”自动全部归入 MiCA。[官方摘要](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=legissum:4626998)。

本次该站直接访问出现挑战页，后台研究取得官方摘要；没有把摘要当作对全部最新技术标准、许可名册或其他支付法规的逐条审计。

### 美国：GENIUS 已成法，OCC 最终规则尚未生效

GENIUS Act 是 **2025-07-18** 批准的 Public Law 119-27，不是仍未通过的提案。其支付稳定币制度涉及许可、储备、赎回及披露，并区分支付稳定币、存款与所列证券类别；不构成政府价格担保或存款保险。[成文法版本](https://www.congress.gov/bill/119th-congress/senate-bill/1582/text/pl?format=txt)；[详细来源定位](notes/beginner-industry-source-audit.md)。

更近期的变化是 **OCC 2026-10-21 已发布实施最终规则说明，生效日为 2027-01-18**。因此截至本文截点，应写“已发布、尚未生效”，不是“还只有草案”，也不是“今天已全面执行”。公告限定其管辖主体，并将 BSA/反洗钱/制裁相关规则列为另行协调制定的事项。[OCC Bulletin 2026-50](https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-50.html)。

不能把这一机关的规则、法律一般生效机制、其他条款的过渡期和发行人实际获许可混成同一天。本文没有核验全部机关附件或具体发行人的许可状况。

### 跨境：仍需逐地、逐主体核验

FSB 2026-10 的公开说明强调全球稳定币安排的跨行业、跨境依赖和数据局限。它是金融稳定监测研究，不是向全球用户发放统一业务许可。[FSB 发布页](https://www.fsb.org/2026/10/global-stablecoin-arrangements-cross-border-vulnerabilities-and-financial-stability-monitoring/)。

本文没有完整调查中国内地、香港和其他各地制度，不给出开户、交易、经营或税务可行性结论。要开展具体业务，需要补查相应监管文件、许可和专业意见，不能从“技术可调用”推出“当地可合法提供”。

## 11. 怎么读行业数字，避免把宣传当测量

以下是研究方法约束，不是本次提交的行业统计：

| 看到的指标 | 先追问什么 | 常见误读 |
| --- | --- | --- |
| TPS | 统计窗口、交易类别、是否计投票、失败及测试流量 | 把不同网络/升级前后的不同计数方式直接排名 |
| 最终性时间 | 协议目标还是实测分布，观察节点及业务链路是什么 | 把目标 150ms 当用户付款 SLA |
| 活跃地址 | 地址去重、合约/机器人、多地址与身份关系 | 直接当独立真实用户数 |
| TVL | 资产范围、价格口径、借贷循环与跨协议重复计算 | 直接当收入、保险金或净新增需求 |
| 转账额/交易量 | 付款还是交易所、内部调拨、清算及套利 | 直接当真实商品支付需求 |
| 年化交易速度 | 来自哪个月，是否按短期速度外推 | 当作全年已实现交易额或今天现状 |
| 收益率 | 观察期、复利、奖励币与本金损失/退出条件 | 把页面 APR/APY 当固定利息承诺 |
| 源码/审计报告 | 版本、覆盖、整改与部署是否对应 | 当作整个产品永远安全的证书 |

具体口径冲突有一手例子：Solana 共识投票路径变化，使旧投票交易计数不能直接与新模型比较；Visa 历史公告的年化速度不能当当前全年已实现额。[Alpenglow](https://solana.com/upgrades/alpenglow)；[Visa 历史公告](https://corporate.visa.com/en/sites/visa-perspectives/newsroom/visa-launches-stablecoin-settlement-in-the-united-states.html)。本篇没有另取数据重算上述指标。

因此本篇有意不填“2026 全球市值、稳定币支付占比、链性能榜、即时挖矿收益”。缺少一致观测日期和方法时，写未知比制造精确数字更有用。

## 12. 接下来学什么，怎样保持不过期

把学习目标分开，不必先选一个币投资：

- **理解世界**：完成 [入门篇的 20 道自测](beginner-guide.md)，能区别资产、控制、执行、最终性与兑付。
- **理解协议**：分别走完 BTC UTXO/PoW 和 EVM nonce/gas/合约路径，再比较其他网络。
- **理解产品**：为一个稳定币、一个 DeFi 产品、一个跨链方案写控制与退出卡，未知项不猜。
- **进入工程**：按照 [学习路线](learning-roadmap.md)，先离线，再在单独授权环境做本地链实验。
- **跟踪升级**：读 [完整新版机制](upgrades/README.md)，核对规范、客户端、实际网络状态和供应商接口，不只看发布标题。

维护本专题时，每项时效结论保留：查阅日、事实发生日、主网/测试网、来源、公告/部署/测量的证据等级，以及哪些没有独立验证。

本次新增行业研究细节见 [支付、稳定币与 RWA 来源审计](notes/beginner-industry-source-audit.md)和 [协议与来源漂移复核](notes/beginner-protocol-source-audit.md)。原始 PPT、全文提取和原图继续只在本地保存；本篇是公开笔记，不提供附件下载。
