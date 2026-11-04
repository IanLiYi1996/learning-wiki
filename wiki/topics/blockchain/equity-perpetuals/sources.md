# 一手来源台账：股票永续、真实股票与有资产支持的股票代币

核验日期：2026-11-04。本文件只记录公开一手资料与由其支持的教学边界，不提供交易、法律或产品推荐。S01–S20 是稳定来源组编号；章节引用可使用 `sources.md#s01`。同组可能包含协议、部署者或监管机构的多个相关页面。

Hyperliquid 与 trade[XYZ] 文档通过当日在线 Markdown 路由读取；入口为 [Hyperliquid 文档索引][hl-index]、[XYZ 文档索引][xyz-index]。监管、托管保护与发行方页面通过当日在线网页核验。阅读日期不是发布日期，也不是冻结版本；本次未核验节点源码、链上实时配置、发行方实际储备或任何个人账户。

## 如何使用这些证据

事实摘录均为中文概括，不是原文全文转载。协议资料解释 HyperCore；XYZ 资料解释 `xyz` 部署，不能外推为所有 HIP-3 市场。SEC／FINRA 的投资者教育资料说明一般权利与账户结构，不替具体产品作法律定性。发行方材料只能证明其公开描述的结构，不能视为独立储备审计。遇到现行说明、历史更新与 API 默认值不一致，应保留差异，参见[版本与未知项](#version-and-unknowns)。

## 来源组

<a id="s01"></a>

### S01｜真实股票：所有权与股东权利

- 股票是公司所有权的一种证券；普通股通常涉及表决、公司宣布分配后的股息及剩余资产权益。不同类别的股份权利不同，不是每股都有相同投票权，也不是公司保证定期派息。普通股在破产清算中可能一无所获。[Investor.gov 股票说明][stocks]、[SEC 术语表][sec-glossary]
- “跟踪一股价格”与“持有一股的所有权”不是同一命题；比较产品应先看发行人、股份类别和法律权利，再看报价符号。这是基于上述权利定义的教学推论。[股票说明][stocks]
- ETF 份额代表基金组合及其收入的一部分权益，而不是直接分别持有每家成分公司的股份；基金市场价可能偏离净资产值，产品结构、组合与费用需另读基金文件。[ETF 说明][etfs]

权威与限制：SEC 官方投资者教育；说明一般结构，不替任何具体公司的章程、股类条款或登记记录。建议对应 `01-products-and-rights.md`、`glossary.md`。

<a id="s02"></a>

### S02｜现金账户与证券融资账户

- 现金账户购买证券须全额付款，不能向该券商借款完成账户内购买；融资账户可以用账户内证券作担保向券商借钱购股。两者都能持有真实证券，“融资”并不把股票变成价格合约。[SEC 账户类型][account-types]、[FINRA 券商账户][finra-accounts]
- 融资购股产生借款利息、追加保证金与强制卖出风险，损失可能超过最初投入，券商不一定须事先通知。完全付款股票仍有市场损失；只是不能把衍生品的保证金清算机制直接套到无借款的现金购股。[SEC 融资账户公告][margin-bulletin]
- 股票做空通常通过借入证券交付，伴随保证金、借券等费用；借入股票派息时，做空者需向出借方支付相关股息。这与在永续里开空是不同流程。[SEC 股票多空说明][stock-short]

权威与限制：SEC／FINRA 官方教育资料；不提供某券商的保证金合同或当地适用规则。本主题不复用旧资料中的 T+2／旧日内交易门槛。建议对应 `01-products-and-rights.md`、`05-margin-and-liquidation.md`。

<a id="s03"></a>

### S03｜证券持有、客户资产托管与 SIPC 边界

- 券商“street name”持有通常由中介或其名义持有人登记，而券商账簿记录客户为实益所有人；直接登记则在发行人／过户代理账簿登记客户。前者不等于客户只是买了一个价格赌注。[SEC／FINRA 联合持有证券公告][holding]
- FINRA 区分全额付款证券的占有／控制义务与融资账户证券使用；客户另行参与全额证券借贷计划时，相关保护和使用条件会变化。不能笼统说“券商永远不能出借任何客户股票”。[FINRA 券商账户][finra-accounts]
- SIPC 的对象是陷入财务困境的会员券商所托管的合资格客户现金／证券；限额 50 万美元，其中现金上限 25 万美元。它不是股价、投资建议或收益保险。**不能因链上合约引用美股、使用 USDC 或自称非托管，就推定有 SIPC 保护。** 后一句是依据适用条件的推论，不是对 XYZ 作法律裁决。[SIPC 官方保护范围][sipc]

权威与限制：SEC／FINRA 对证券持有的解释及 SIPC 自身对保护范围的说明；实际保护须核会员、客户关系、资产资格及程序。建议对应 `01-products-and-rights.md`、`07-risk-and-protection.md`。

<a id="s04"></a>

### S04｜有资产支持的股票代币：结构示例，不是推荐

- SEC 区分发行人直接代币化、托管证券权益与第三方合成关联证券；有些代币能承载股票权利，有些只是另一发行人的债务／衍生权益。不能仅凭“在链上”或“1:1”断言持有人是不是股东。[Investor.gov 代币化证券][tokenized]
- 作为一种结构例子，发行方将 xStocks 描述为 Jersey 特设发行公司的 tracker certificate／不记名债务工具，以对应证券作 1:1 支持，不授予标的公司股东表决权；托管分隔、担保代理与违约处置均受产品文件约束。[发行方法律概览][issuer-legal]
- 一级发行／赎回需发行方 KYC、AML 与钱包白名单；二级转账或成交不自动赋予无条件赎回能力。现行文档另有需发行方和券商双方开户核验的实物股票兑换流程，因此也不能断言“所有这类代币都只能换现金”。[发行与赎回][issuer-redemption]、[实物兑换流程][issuer-in-kind]
- 该示例把标的股息税后再投资，通过 rebase／显示倍率传递经济效果；这与直接享有标的公司的股息请求权不同。其他产品可能采用不同安排。[发行方 FAQ][issuer-faq]

权威与限制：发行方解释其自身产品；未独立审计储备、托管或担保可执行性。实际权益以有效招股书、补充文件与具体 Final Terms 为准；[发行方文件入口][issuer-documents]列有 2026-05-08 基础招股书及后续补充，本次未全文审阅这些 PDF。只用于结构对照，不推荐该发行方／渠道。建议对应 `01-products-and-rights.md`、`06-hours-and-corporate-actions.md`、`07-risk-and-protection.md`。

<a id="s05"></a>

### S05｜HIP-3：谁定义市场，质押究竟保护什么

- HIP-3 部署者定义合约、预言机与市场运行参数；使用 HyperCore 订单簿及保证金引擎，不等于 Hyperliquid 协议层为每个标的买入股票。[HIP-3][hip3]
- 文档主网质押要求为 500,000 HYPE，并存在持续／退出等待条件；这是运行者质押，不是按未平仓名义金额购买标的股票的全额储备。[HIP-3][hip3]
- 罚没由验证者投票，重在协议正确性、运行与性能，不是对所有经济损失或主观争议的保证。罚没的 HYPE **销毁而非分配给受影响用户**，不能称为赔付基金。[HIP-3][hip3]
- 部署者可用 `haltTrading` 终止交易、取消订单并按当时 mark 结算仓位，也可恢复市场。“无固定到期日”不等于永远不能终止。[HIP-3 结算章节][hip3]

权威与限制：协议官方规范；质押数、权限及经济参数可变，不能由规范推定现实市场无异常或用户必获补偿。建议对应 `01-products-and-rights.md`、`07-risk-and-protection.md`、`08-reading-a-contract.md`。

<a id="s06"></a>

### S06｜XYZ 永续与协议／前端／部署者的分工

- `xyz` 永续是无固定到期的线性合约，以 USDC 保证金及结算；美元报价与 USDC 结算间不自动进行 USDC/USD 转换，经济上存在 quanto／结算币偏离风险。[XYZ Perpetuals][xyz-perps]
- XYZ 决定市场、数据源和可配置参数；其维护的分布式 relayer 约每三秒发布价格输入。HyperCore 处理下单、撮合、仓位、保证金、资金费、清算与结算。[XYZ 架构][xyz-architecture]
- trade.xyz 是非托管交互界面，既不替代 HyperCore，也不是该部署的唯一访问界面；这项架构声明不消除预言机、网络、钱包和参数风险。[与 Hyperliquid 的关系][xyz-relationship]

权威与限制：XYZ 对自身部署与界面的描述；不能把它等同证券券商、传统中央对手方或所有 HIP-3 产品。建议对应 `README.md`、`01-products-and-rights.md`、`02-market-and-positions.md`。

<a id="s07"></a>

### S07｜成交、仓位与盈亏：订单簿不是按预言机报价兑换

- HyperCore 订单簿按价格—时间优先撮合，受 tick／lot 约束。市场参与者的订单与深度决定可成交价格；oracle／mark 是计算输入，不是保证可按该价买卖的报价。[Hyperliquid 订单簿][order-book]、[XYZ 风险说明][xyz-risks]
- 线性仓位的未实现盈亏可写为 `方向 × (mark − 入场均价) × 数量`；开仓增仓影响加权入场价，减仓不重算剩余入场价。最终应以成交、费用、资金费及保证金账本核算，不能用一个屏幕上的价格差代替完整现金流。[Entry price and PnL][pnl]
- 原生 Crypto Perps 的合约规格用于理解线性机制；其中 USDT 计价、impact notional 等参数**不是 XYZ 美股的通用规格**。[原生合约规格][contract-specs]、[XYZ 产品说明][xyz-perps]

权威与限制：协议文档和部署者风险披露；PnL 页面强调部分 entry／closed PnL 为界面方便展示，不能当作独立托管证券记录。建议对应 `02-market-and-positions.md`、`lab.md`。

<a id="s08"></a>

### S08｜XYZ Oracle Price：外部输入与内部价格发现

- oracle 是资金费参考价，并进入 mark 计算；外部市场可用时，relayer 从场所与机构数据形成外部价格。当外部输入不可用时，内部机制从最后外部价起步，根据订单簿 impact bid／ask 与 oracle 的差异推进。[Oracle Price][oracle]
- 内部 oracle 用连续时间 EMA，当前说明时间常数为 30 分钟；impact 价格对应给定名义金额在买／卖盘口的平均执行价，缺乏足够深度的一侧贡献归零。恢复外部输入后，下一次更新重新使用外部定价。[Oracle Price][oracle]
- 时间常数曾由 8 小时变 1 小时，再于 2026-04-30 改为 30 分钟；这些历史数值不能混用。内部 oracle 可动，因此“外部市场关闭”不等于“oracle 冻结”。[时间常数更新][oracle-changelog]

权威与限制：XYZ 自身算法说明；不是外部真实股票成交记录，不保证数据正确或操纵不可能。未核实实时 impact notional。建议对应 `03-prices-and-anchoring.md`、`06-hours-and-corporate-actions.md`、`lab.md`。

<a id="s09"></a>

### S09｜External Price 与美股外部交易时段

- External Price 是单独的 relayer 输入：外部市场开启时与 externally-derived oracle 对应；外部关闭时停在最后外部收市参考，而内部 oracle 仍可继续变化。[External Price][external]
- 美股说明的外部覆盖包括盘前 04:00–09:30、正常 09:30–16:00、盘后 16:00–20:00，以及 Blue Ocean ATS 提供的夜盘 20:05–04:00，均为 ET；所述周覆盖从周日 20:05 至周五 20:00。[美股市场页][us-hours]
- 2026-08-13 更新把周末内部时段终点从周日 20:00 改成 20:05；节假日及具体合约仍需单独核对。规格中也存在外部时段不同的品种，不能写成“全部股票每天夜里都冻结”或“每个美股永续都具有完全相同的夜盘输入”。[内部时段更新][hours-changelog]、[规格表][spec-index]

权威与限制：XYZ 对其输入覆盖的声明，不是所有券商或证券交易所的可成交保证。ET 不应全年固定换算成一个 UTC 时差。建议对应 `03-prices-and-anchoring.md`、`06-hours-and-corporate-actions.md`。

<a id="s10"></a>

### S10｜Mark Price：风险估值，不是成交承诺

- XYZ mark 是三项的中位数：oracle；oracle 加永续 mid 与 oracle 差值的 150 秒 EMA；本地最佳买、最佳卖、最后成交的中位数。前两项由 relayer 输入，第三项由协议计算。[XYZ Mark Price][mark]
- mark 用于未实现盈亏、保证金、清算与条件单触发；可以不同于 oracle、last、盘口可执行价。两个组件共享 oracle，故“取三个数中位数”不意味着有三个独立来源，也不保证错误 oracle 无法影响清算。[Mark Price][mark]、[XYZ 风险说明][xyz-risks]
- XYZ 说明对 relayer 更新采用 ±50 bps 的单次限制；协议 API 另有一般 `markPx` 单次限制。单次限幅不等于累计涨跌限制。原生 crypto mark 的外部 CEX perp 组件也不能直接套到 XYZ。[HIP-3 API][hip3-api]、[原生稳健价格][robust-prices]

权威与限制：部署者方法及协议输入规范；算法稳健性是控制目标，不是无清算风险保证。建议对应 `03-prices-and-anchoring.md`、`05-margin-and-liquidation.md`。

<a id="s11"></a>

### S11｜Discovery Bounds v2：会移动的窗口

- 现行说明对 mark 施加参考价周围的瞬时界限，并允许内部 oracle 接近触发阈值时重锚：参考移到该方向边界，再建立新窗口。上下方向分别计数；用尽配置次数后才成为该方向硬上限，外部定价恢复会重置。[Discovery Bounds][bounds]
- 不能把一个瞬时 `±1/max leverage` 窗口当成整个周末恒定区间。实际范围、reset 次数与适用参数应核品种规格；表中有例外／取整，不能只由杠杆倒数覆盖规格。[Bounds][bounds]、[规格表][spec-index]
- 强平价在**当时有效**界限外，只在该界限仍有效的条件下不能因 mark 越过该价而触发；重锚、外部重开、保证金与资金费变化都会改变前提。[Bounds][bounds]、[风险披露][xyz-risks]

权威与限制：XYZ 市场结构规则；2026-03-13 的 [v2 更新页][bounds-changelog]下半部明确是 v1 归档，不应当作现行固定区间模型。建议对应 `03-prices-and-anchoring.md`、`05-margin-and-liquidation.md`、`lab.md`。

<a id="s12"></a>

### S12｜Hyperliquid Funding：公式、采样与实际支付

- 资金费在多空之间转移，协议不就该转移收取资金费手续费；正费率通常多付空，负费率空付多。通用文档每五秒采 premium、按小时平均，以八小时口径公式计算，再每小时支付其八分之一。[Funding][funding]
- 通用表达为 `F8 = P + clamp(I − P, −c, c)`；HIP-3 premium 使用 impact bid／ask 的平均值相对 oracle，而非“最新成交价减股价”。支付名义金额使用 `数量 × oracle`，不是 `数量 × mark`。[Funding][funding]
- 所以即时最后成交溢价不保证本小时资金费必为正，也不能把资金费率直接等同溢价。利率项、平均 premium、clamp 与部署者倍率须同时解释；通用协议文档写上限为 0.5%／小时，但 XYZ 的倍率与封顶组合仍见 S13 及未知项。[Funding][funding]、[HIP-3 参数 API][hip3-api]

权威与限制：协议一般公式；通用页的 crypto 叙述、数值例子与 HIP-3 专项定义须分开，不保证套利收敛的时间或幅度。建议对应 `04-funding-and-arbitrage.md`、`lab.md`。

<a id="s13"></a>

### S13｜XYZ Funding 参数与“套利锚定”的边界

- XYZ 2025-12-19 更新公开展示对 Hyperliquid 公式乘 0.5，并保留 `±0.0005` clamp；基线约 5.5% 简单年化是该历史公式及假设的说明，不是保证回报。当前规格表所读取的美股样例倍率仍为 0.5。[XYZ funding 更新][funding-changelog]、[规格表][spec-index]
- 现行 HIP-3 API 支持分别设置 multiplier、八小时 interest rate 与 funding clamp，并在 clamp 接口写默认 `0.0003`。这不直接证明 XYZ 已改成该默认值，也不能据旧更新断言全市场永远为 `0.0005`。[HIP-3 API][hip3-api]
- 资金费与可对冲交易能形成价格靠拢的激励；但订单簿、外部休市、融资／借券、资金费变动、费用与清算约束使“立刻且精确收敛”“无风险搬砖”都不成立。这是基于机制和风险条款的教学推论，不是实证套利收益。[XYZ 产品][xyz-perps]、[风险说明][xyz-risks]

权威与限制：有日期的历史变更、当前规格与协议可配置范围三种证据；未读链上每品种实际 interest／clamp，也未观察真实 funding 历史。建议对应 `04-funding-and-arbitrage.md`、`08-reading-a-contract.md`、`lab.md`。

<a id="s14"></a>

### S14｜交易费用不是资金费；Growth Mode 不是统一常数

- XYZ 标准表的基础档示例为 taker 0.090%、maker 0.030%；Growth Mode 表示例为 0.0090%、0.0030%。这些是该页条件下的每笔交易费，不是保证每个资产、账户或未来时点都收同样费用。[XYZ Fees][xyz-fees]
- 费档取决于滚动 14 天加权成交量，并可能受 staking、referral、部署者 fee scale、collateral 与 Growth Mode 等影响。协议允许 HIP-3 部署者配置费用，不应泛称“全部 HIP-3 恒定为原生费率两倍”。[Hyperliquid Fees][hl-fees]、[HIP-3 API][hip3-api]
- 比较合约持有成本应分别列交易费、资金费、买卖价差和滑点；传统对冲腿另有借款／借券与执行成本，而不是只比较屏幕上一个费率。[Funding][funding]、[SEC 融资账户][margin-bulletin]、[XYZ 流动性风险][xyz-risks]

权威与限制：官方公开费用规则，不是任何账户的有效费率报价；未核单品种实时 Growth Mode。建议对应 `04-funding-and-arbitrage.md`、`08-reading-a-contract.md`。

<a id="s15"></a>

### S15｜保证金、账户模式与 1× 误区

- 初始保证金取决于名义仓位、mark 与所选杠杆；维持要求取决于该市场／档位的最大杠杆，而不只是用户把滑块设成多少。逐仓隔离本仓位保证金，strict isolated 另有限制移除保证金的规则。[XYZ Margin Modes][xyz-margin]、[协议 Margining][hl-margin]、[Margin tiers][margin-tiers]
- **当前不能统一说“HIP-3 各 DEX 的保证金永远分开”**：standard 模式按 DEX 分开；unified／portfolio 对同抵押资产的跨 DEX cross 仓位可以共享保证金。必须先核账户抽象模式。[Account abstraction modes][account-modes]、[Margining][hl-margin]
- 1× 只说明某时点所选名义金额／保证金关系，不增加股票所有权、兑股或股息权，也不免除资金费、费用、ADL 与运行风险。不能说所有 1× 多仓都容易清算，也不能保证所有 1× 仓位永不清算；方向、资金流、其他共享仓位与参数必须明确。[Margining][hl-margin]、[XYZ 风险说明][xyz-risks]

权威与限制：协议规则和 XYZ 模式说明；非个人强平价计算。仓位档位和账户模式可变，XYZ 某些概述仍使用旧杠杆范围，具体以规格及元数据核对。建议对应 `02-market-and-positions.md`、`05-margin-and-liquidation.md`、`08-reading-a-contract.md`。

<a id="s16"></a>

### S16｜Clearinghouse、普通清算与 backstop

- HyperCore clearinghouse 管理地址的保证金余额与仓位状态；名字不代表传统证券清算会员体系、证券托管或对用户收益作担保。[Clearinghouse][clearinghouse]
- 权益不足维持保证金时先尝试向订单簿清算，可能部分成交；进一步恶化时 backstop 可接管仓位与保证金。强平使用 mark，不是最后成交价，界面预估强平价会随资金费及 cross 其他仓位变化。[协议 Liquidations][hl-liquidations]、[XYZ Liquidation Mechanics][xyz-liquidations]
- 当前 XYZ 对已启用 cross 的资产有独立链上 backstop liquidator，不能套用“每个 XYZ 品种都由原生 HLP 兜底”。它降低对 ADL 的依赖，不保证能吸收所有损失，也不创造全额股票储备。[HIP-3 Backstop][hip3]、[XYZ 清算说明][xyz-liquidations]

权威与限制：协议记账／清算规范与部署者状态声明；原生 HLP 路径和 HIP-3 独立 backstop 要分开，未审计其当前资金量。建议对应 `05-margin-and-liquidation.md`、`07-risk-and-protection.md`。

<a id="s17"></a>

### S17｜ADL：保持系统偿付能力，不保证盈利仓位完整保留

- 账户或逐仓价值变负且常规处置不足时，ADL 可从反方向盈利仓位中按收益与杠杆相关指标选择，按前一 mark 强制减仓／平仓。方向判断正确也不保证仓位能持有到预定时点。[协议 ADL][hl-adl]、[XYZ ADL][xyz-adl]
- 文档的“系统保持偿付能力／无坏账”描述的是清算与记账机制目标及约束，不是每个用户无损、盈利永不被截断或没有技术风险。协议也说明无未平仓仓位用户不会承担此类仓位损失社会化；不能外推为存款在一切故障中绝对安全。[协议 ADL][hl-adl]、[XYZ 风险说明][xyz-risks]

权威与限制：官方机制描述；不是 ADL 发生概率、历史频率或赔偿保证。建议对应 `05-margin-and-liquidation.md`、`07-risk-and-protection.md`。

<a id="s18"></a>

### S18｜公司行动：股息不是固定资金费，拆股可能结束旧仓位

- XYZ 股票永续不直接收股息；文档认为股息经济效果可经定价、资金费和与股票的套利反映，但资金费依市场条件变化，**不是固定股息支付，也不保证完全复制股东税后结果**。[Corporate Actions][corporate-actions]、[公司行动风险][xyz-risks]
- 当前拆股／反向拆股安排是结算原仓位、取消订单，再按新股票单位重开；恢复敞口需重新开仓、重新提交订单。并购等事件逐项判断，可能继续、调整、结算或永久关闭。[Corporate Actions][corporate-actions]
- 2026-09-28 Kioxia 通知具体安排为旧仓位 USDC 结算、包括 TP／SL 的订单取消，新参考价除以三；通知明确重开参考价初始化 oracle，**实际成交仍取决于订单簿**。这是日本股票实例，只用来说明 XYZ 操作路径，不当作全部美股事件的统一日程。[Kioxia 拆股通知][kioxia]

权威与限制：部署者一般政策与公开事件通知；本次未核验该事件实际链上执行，不能把“预计重开”写成已实证完成。建议对应 `06-hours-and-corporate-actions.md`、`08-reading-a-contract.md`。

<a id="s19"></a>

### S19｜权益缺失、数据／USDC／法律与技术风险

- 永续提供合成价格敞口，持有人没有标的的所有权、表决、股息／分配、赎回、转换、交割等权利；不存在“拿保证金换成对应股票”的合约权利。有人自行购股对冲，也不会由此赋予永续持有人股票请求权。[Perpetuals Risks][xyz-risks]
- 数据可能真实发布却不具代表性，例如夜盘薄成交、停牌、异常拍卖或错误公司行动映射；oracle 可影响多个 mark 组件，即使 XYZ 订单簿没有该价成交，也可能触发资金费、条件单或清算。[Perpetuals Risks][xyz-risks]
- USDC 与美元不是同一资产；网络、钱包、bridge、relayer 或 API 故障可能阻止管理仓位而风险继续累积。报价、限幅、stop 与 24/7 可访问性都不是准确价格、成交或无损保证。[Perpetuals Risks][xyz-risks]
- 一般免责声明明确存在包括美国人士及美国境内的访问限制；本读本不提供绕过限制的方法，也不把开放协议访问能力解释为所有地区都获准交易。[General Disclaimer][xyz-disclaimer]

权威与限制：XYZ 自身风险与访问声明；不是独立审计、全球法律意见或完整免责条款分析。建议对应 `01-products-and-rights.md`、`07-risk-and-protection.md`、`README.md`。

<a id="s20"></a>

### S20｜读具体合约：规格、时段、OI 与变更记录

- 规格表逐项列 underlying／单位、最大杠杆、discovery bounds、reset 次数、margin mode、外部／内部时段与 funding multiplier；还说明 OI 上限可能阻止新开仓，只许减仓／平仓。[Specification Index][spec-index]
- 当日文档样例：TSLA／NVDA 为 20×、±5%、2 resets、cross、0.5 funding multiplier；AAPL 同为 20×／±5% 但只列 1 reset。它们是**有日期的规格例子，不是现行推荐或不可变常量**。URNM／ICE 的时段行与上述 24/5 美股样例不同。[Specification Index][spec-index]
- 股市、夜盘股市及其他资产的节假日表分开；不能把现货交易所休市、ATS 夜盘休市与永续停止撮合混为一谈。历史市场参数页进一步说明模式、时段、reset 和上限确实会更新。[Holiday Closures][holidays]、[10/25 参数更新][parameters-1025]、[6/24 参数更新][parameters-0624]

权威与限制：XYZ 当前可变规格／历史台账；表未给足全部实时参数，部分历史页只有月日无年份，不能擅自补年。建议对应 `06-hours-and-corporate-actions.md`、`08-reading-a-contract.md`、`lab.md`。

## 章节到来源组的建议映射

| 文件 | 优先来源组 | 引用重点 |
| --- | --- | --- |
| `README.md` | S01、S05、S06、S19 | 产品边界、研究日期、非推荐 |
| `01-products-and-rights.md` | S01–S06、S19 | 股票权利、托管、支持资产代币、合成敞口 |
| `02-market-and-positions.md` | S06、S07、S15 | 合约数量、订单簿、多空、保证金账本 |
| `03-prices-and-anchoring.md` | S08–S11、S19 | external／oracle／mark／execution 分离 |
| `04-funding-and-arbitrage.md` | S12–S14、S18、S19 | 采样／基线／clamp、费用、对冲限制、股息 |
| `05-margin-and-liquidation.md` | S02、S10、S11、S15–S17 | 初始／维持、账户模式、清算、backstop、ADL |
| `06-hours-and-corporate-actions.md` | S04、S09、S18、S20 | ATS 夜盘、内部时段、假日、公司行动 |
| `07-risk-and-protection.md` | S03–S05、S16、S17、S19 | 资产权利、质押非赔付、托管与系统风险 |
| `08-reading-a-contract.md` | S05、S06、S13–S15、S18、S20 | 逐项规格及必须复核的参数 |
| `learning-roadmap.md` | S01、S06–S08、S12、S15、S19 | 权利→交易→价格→资金费→风险的学习顺序 |
| `glossary.md` | S01–S03、S05–S17 | 术语定义按协议／部署者分别标注 |
| `lab.md` | S07–S15、S17、S18、S20 | 原创简化模型、离线算术及反例 |

此表是教学组织建议，不是一项外部事实。练习必须注明假设及未包含的机制，不把原创模拟输出称为真实市场测试。

<a id="version-and-unknowns"></a>

## 版本差异、未知项与下次核验

以下记录截至 2026-11-04，不用一句“以官网为准”抹平实际差异。

1. **Funding clamp 未确定。** [协议 Funding][funding]和 [XYZ 2025-12-19 更新][funding-changelog]展示 `±0.0005`；[当前 HIP-3 API][hip3-api]的 `setFundingClamps` 写默认 `0.0003`，且允许部署者修改。未查询每品种链上配置，故只能把数值放进明确标为“假设”的例子。也未由源码核验倍率与小时封顶的精确组合顺序。
2. **原生与 HIP-3 premium 不同。** [Funding][funding]技术段给 HIP-3 impact bid／ask 平均价格式，不能套用原生单边 IPD 式。这里“当前某笔成交有溢价却资金费不为正”并不声称：在正利率、非负倍率等特定条件下，已经平均的正 premium 还能任意产生负值；反例应说明成交价、impact 价格、平均时段或参数的差别。
3. **旧 discovery bands 不是现行 v2。** [v2 历史页][bounds-changelog]明确保留 v1 文本，且其导引仍指向 External Price；当前规则集中在 [Discovery Bounds][bounds]，并须联读 [规格表][spec-index]。reset／threshold 不全部展示在规格中；不能把 WTIOIL 的阈值例子当作所有股票阈值。旧 [oracle 更新][oracle-changelog]中的收益保留比例与静态 band 表述不作为当前收益保证。
4. **mark 输入与限幅有层次。** [XYZ Mark][mark]写 relayer ±50 bps；[协议 API][hip3-api]写一般 mark 单次 1% 等约束，这是不同层，不直接视为互斥。Oracle 页附注的 EMA basis 符号与 Mark 页表述有方向差异，本文按专门 Mark 页解释经济含义，不直接拼接两页公式；本次未以源码消除该表达差异。
5. **跨 DEX margin 不能照旧概述。** [HIP-3][hip3]的独立 DEX 描述和 [Clearinghouse][clearinghouse]的简短默认说明，须结合 [Margining][hl-margin]与 [账户模式][account-modes]。独立市场状态不意味着 unified／portfolio 用户的所有抵押风险必然分离。未获取任何用户真实模式。
6. **夜盘覆盖不是每个标的时时都有深度。** [美股页][us-hours]给 BOATS 夜盘；[规格表][spec-index]仍列不同时段的例外。20:00 到 20:05 的接续、节假日提前收市、停牌和个别无有效输入时的切换须核实际可用数据，不从“24/5”推定没有间隙。周末外部价冻结也不代表内部 oracle／mark 冻结。
7. **费率范围存在页面不同步。** [HIP-3 主规范][hip3]及 [费用页][hl-fees]概述段写 Growth Mode fee share 0–100%；同一费用页详细段与 [API][hip3-api]另允许 growth fee scale 到 10 以下。本文只使用条件化费用表与“需核具体配置”，不构造一个未经核验的全球统一上下限。XYZ “标准两倍”是其当前说明，不是所有部署者的协议常数。
8. **发行方示例不冻结在旧版。** [发行方当前赎回说明][issuer-redemption]和 [实物流程][issuer-in-kind]新增了有准入条件的兑股路线；“有储备”“是债务凭证”“可申请兑股”“持有期间拥有标的公司股东权利”是四个不同问题。未审查完整法律 PDF、储备或开户资格，不向读者推荐该路线。
9. **公司行动通知不是执行证明。** [Kioxia 通知][kioxia]是已过去日期的安排，包含预计时间；没有查链上日志，就不能说已按时完成。其他美股事件的结算价、停牌、订单取消与重开处理须读当次公告。
10. **未执行事项。** 未登录券商、接钱包、申请开户／赎回、下单、转账、改参数、运行付费数据查询、提交或推送代码。只阅读公开资料并新增此来源台账。不可从文档推定最新流动性、当前 oracle 状态、真实套利收益、backstop 资金充足度、发行方偿付或司法可追偿结果。

下次更新应先查单品种规格、参数变更与账户模式，再复核 oracle／mark／funding 的专门技术说明，最后读当次公司行动、费用及地区限制。保留核验日期与差异记录，不仅更换页面日期。

## 官方链接

[hl-index]: https://hyperliquid.gitbook.io/hyperliquid-docs/llms.txt
[xyz-index]: https://docs.trade.xyz/llms.txt
[stocks]: https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks
[etfs]: https://www.investor.gov/introduction-investing/investing-basics/investment-products/mutual-funds-and-exchange-traded-2
[stock-short]: https://www.investor.gov/introduction-investing/investing-basics/how-stock-markets-work/stock-purchases-and-sales-long-and
[sec-glossary]: https://www.sec.gov/resources-small-businesses/glossary
[account-types]: https://www.investor.gov/introduction-investing/investing-basics/how-stock-markets-work/types-brokerage-accounts
[margin-bulletin]: https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-29
[finra-accounts]: https://www.finra.org/investors/investing/investment-accounts/brokerage-accounts
[holding]: https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-97
[sipc]: https://www.sipc.org/for-investors/what-sipc-protects
[tokenized]: https://www.investor.gov/introduction-investing/investing-basics/investment-products/tokenized-securities
[issuer-legal]: https://docs.xstocks.fi/docs/product-legal-overview
[issuer-redemption]: https://docs.xstocks.fi/docs/issuance-and-redemption
[issuer-in-kind]: https://docs.xstocks.fi/docs/issuance-and-redemption/in-kind-flow-xport
[issuer-faq]: https://docs.xstocks.fi/docs/frequently-asked-questions
[issuer-documents]: https://assets.backed.fi/legal-documentation
[hip3]: https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals.md
[hip3-api]: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/hip-3-deployer-actions.md
[xyz-perps]: https://docs.trade.xyz/perpetuals.md
[xyz-architecture]: https://docs.trade.xyz/architecture.md
[xyz-relationship]: https://docs.trade.xyz/overview/relationship-to-hyperliquid.md
[order-book]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/order-book.md
[contract-specs]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications.md
[pnl]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/entry-price-and-pnl.md
[oracle]: https://docs.trade.xyz/perpetuals/mechanics/oracle-price.md
[oracle-changelog]: https://docs.trade.xyz/perpetuals/changelog/oracle-time-constant-updates.md
[external]: https://docs.trade.xyz/perpetuals/mechanics/external-price.md
[us-hours]: https://docs.trade.xyz/perpetuals/markets/stocks/us.md
[hours-changelog]: https://docs.trade.xyz/perpetuals/changelog/equities-internal-session-hours.md
[mark]: https://docs.trade.xyz/perpetuals/mechanics/mark-price.md
[robust-prices]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/robust-price-indices.md
[bounds]: https://docs.trade.xyz/perpetuals/mechanics/discovery-bounds.md
[bounds-changelog]: https://docs.trade.xyz/perpetuals/changelog/discovery-bounds-v2.md
[funding]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding.md
[funding-changelog]: https://docs.trade.xyz/perpetuals/changelog/funding-rate-formula-updates.md
[xyz-fees]: https://docs.trade.xyz/perpetuals/mechanics/fees.md
[hl-fees]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees.md
[xyz-margin]: https://docs.trade.xyz/perpetuals/risk-and-margining/margin-modes.md
[hl-margin]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margining.md
[margin-tiers]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/margin-tiers.md
[account-modes]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/account-abstraction-modes.md
[clearinghouse]: https://hyperliquid.gitbook.io/hyperliquid-docs/hypercore/clearinghouse.md
[hl-liquidations]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/liquidations.md
[xyz-liquidations]: https://docs.trade.xyz/perpetuals/risk-and-margining/liquidation-mechanics.md
[hl-adl]: https://hyperliquid.gitbook.io/hyperliquid-docs/trading/auto-deleveraging.md
[xyz-adl]: https://docs.trade.xyz/perpetuals/risk-and-margining/auto-deleveraging.md
[corporate-actions]: https://docs.trade.xyz/perpetuals/corporate-actions.md
[kioxia]: https://docs.trade.xyz/perpetuals/corporate-actions/2026-09-28-kioxia-stock-split.md
[xyz-risks]: https://docs.trade.xyz/legal-and-disclaimers/perpetuals-risks-and-disclaimers.md
[xyz-disclaimer]: https://docs.trade.xyz/legal-and-disclaimers/general-disclaimer.md
[spec-index]: https://docs.trade.xyz/perpetuals/specifications-and-schedules/specification-index.md
[holidays]: https://docs.trade.xyz/perpetuals/specifications-and-schedules/holiday-closures.md
[parameters-1025]: https://docs.trade.xyz/perpetuals/changelog/market-parameters/10-25.md
[parameters-0624]: https://docs.trade.xyz/perpetuals/changelog/market-parameters/6-24.md
