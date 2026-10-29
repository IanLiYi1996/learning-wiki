# 稳定币与多链生态：PPT p28–42 一手来源审计

- 研究及检索日期：2026-10-29（UTC）。
- 目的：为 PPT 的机制、术语与产品生命周期纠错，不提供股票价格、投资分析或法律建议。
- 方法：由后台研究代理检索并打开官方文档、官方公告及项目维护者代码仓库；以下保留 18 条核心来源，不采用媒体转述作为证据。
- 范围：USDT、USDC、DAI/USDS、USDe、Polygon、Polkadot、Cosmos/IBC、Solana，以及 Ethereum/Solana 对比的证据边界；不遍历跨链产品，不加入桥事故案例。
- 执行边界：后台代理只写本文件，不修改 PPT 或其他文件，不提交或 push。主线程整合时已另外读取完整附件并补充二次核验，终稿与来源漂移说明以专题正文及复核记录为准。
- 页码限制：本次未取得可核对的用户 PPT 原文。下面的 p28–42 是**暂定审阅槽位，不是已验证的原稿页码映射**；实际改稿时须按主题定位。不得声称已经逐页检查了原 PPT。

## 一、先改哪些内容

以下是建议替换口径，不是对未见原稿的逐字引述。来源编号对应第二节。

| 暂定页码 | 主题 | 应删除或限定的说法 | 建议替换口径 | 来源 |
| --- | --- | --- | --- | --- |
| p28 | 稳定币定义 | “稳定币价格/净值永远等于 1 美元” | 区分目标锚定、资产支持、发行方直接赎回条件与二级市场价格；这些不是同一个承诺。 | S03、S04、S07 |
| p29 | USDT 多链 | “各链的 USDT 都是 Tether 原生发行；BSC、Polygon 默认原生” | 逐一核对链、资产种类和官方合约。Tether 名单中的 BNB Smart Chain 小节只列 XAU₮，不是 USD₮；该名单未列 Polygon USD₮。两者不能凭名称认定为发行方原生 USD₮，也不能不查合约就把所有版本统一判为同一种桥接资产。 | S01 |
| p30 | USDC | “月度鉴证就是完整财审；任何持有人都可直接找 Circle 赎回” | 月度鉴证针对储备与流通量，Circle 公司财务审计另行披露。直接赎回须符合适用条款及 Circle Mint 账户资格；持币本身不等于直接赎回资格。 | S03、S04 |
| p31 | DAI / USDS | “只用 ETH 抵押；完全没有机构或链下依赖” | 已证实机制包括 USDC–DAI 的 LitePSM、USDS 包装接口，以及 Maker/Sky 的 RWA 借贷、回款和链下执行模块；不能用“纯 ETH、无机构”概括。当前抵押组合及比例须另取同期证据。 | S05、S06 |
| p32 | USDe | “对冲后净值恒为 1；托管和负资金费率没有风险” | 通过资产与衍生品对冲寻求相对稳定；资产由 OES 服务商托管，仍有托管、交易所对手方、流动性与市场风险。持续负资金费率可能产生支出，储备基金是缓冲设计，不是无限担保。 | S07 |
| p33 | 跨链与资产身份 | “同名代币/支持跨链消息就代表相同资产与安全性” | 将发行方认可资产、包装/桥接表示、消息语义、传输与执行分开审查；名称及网络支持不能代替具体合约和资产来源核验。 | S01、S04、S12 |
| p34 | Ethereum / Solana 对比 | 无日期的固定 TPS、固定费用、“从未宕机”或“永久更便宜” | 本次未取得同期同口径的两链性能/费用样本，不填数值、不作永久排名。Solana 有官方停机复盘；finality 目标不是 TPS。 | S15、S18；比较方法见第三节 |
| p35 | Polygon PoS | “Polygon PoS 是 rollup L2” | Polygon 官方将 PoS 定义为 Ethereum 的 EVM 兼容 PoS sidechain；不能将它与 zkEVM rollup 混为一谈。 | S08、S09 |
| p36 | Polygon zkEVM | “当前仍是持续运营、可新增部署的主网方案” | 2025-06-11 公告退役；官方现状页记载 2026-07-03 sequencer 停止、网络不再出块。按历史 rollup 产品及退役状态介绍，不把 PoS 或其他 Polygon 产品一并判为退役。 | S09、S10 |
| p37 | Polkadot 资源分配 | “当前仍靠长期插槽拍卖才能接入” | 长期 slot auction 是历史机制；当前按 Agile Coretime 的 bulk / on-demand 资源分配解释。不要进一步写成“已完全没有任何竞价机制”。 | S11 |
| p38 | XCM | “XCM 就是跨链传输协议/桥” | XCM 是跨共识消息格式与语言；传输渠道另有 XCMP、HRMP、VMP 等，格式本身不负责把消息送达。 | S12 |
| p39 | Cosmos SDK | “SDK 只能建设 Cosmos Hub 的子链，且必然共享 Hub 安全” | SDK 是模块化的应用专用链/账本开发框架；链可有自己的执行与安全配置，不能从采用 SDK 推导其受 Hub 验证者保护。 | S13 |
| p40 | IBC / 共享安全 | “IBC 只能用于 Cosmos 域；接入即自动共享安全” | IBC 可跨 SDK 之外的账本和虚拟机；通信与共享安全是不同能力，共享安全须另行选择、配置并核验，不是接入 IBC 的自动结果。 | S13、S14 |
| p41 | Solana 共识 / 账户 | “PoH 是独立共识；程序就是自带全部状态的单一账户” | 不将 PoH 单独等同共识；按升级日期说明 TowerBFT 历史与 Alpenglow 当前状态。程序账户与状态数据账户要区分；PDA 是由 program ID 和 seeds 确定性派生、无私钥的地址。 | S15、S16 |
| p42 | Solana Token / USDT | “每种 Token 都要部署独立 Token Program；ATA 就是钱包地址” | 区分 Token Program、Mint、Token Account、ATA。SPL USDT 的资产标识应取 Tether 公布的 Solana mint，不凭 symbol 或名称识别。 | S01、S17 |

## 二、18 条官方来源与证据边界

证据质量仅评价“是否能支持该条结论”，不是项目安全评级：

- **A：**正式官方技术文档、条款或项目代码直接说明机制。
- **A／历史：**有日期的第一方公告或工程复盘，适合证明该事件，不自动代表今天全部状态。
- **B／现状声明：**官方持续更新的产品/状态说明；可引用其截至检索日的声明，但不是独立审计、运行验证或同期性能测量。
- 页面没有显示发布时间/更新时间的，明确标记“未标注”；检索日期不能冒充发布日期。本文未归档网页快照或锁定 Git commit，后续引用须复查。

### S01 — Tether 支持协议与官方资产标识

- URL：<https://tether.to/en/supported-protocols/>
- 支持结论：页面按资产列出 USD₮ 的 Ethereum、Avalanche、Kava、Celo、Kaia、Tron、Liquid、Solana、Polkadot AssetHub、Tezos、Near、TON、Aptos 标识；BNB Smart Chain 小节列的是 XAU₮，未给 USD₮；Polygon 不在这里的 USD₮ 名单中。不能把“支持某条链的某种 Tether 资产”偷换为“这条链有官方原生 USDT”。
- 可直接用于 p42 的标识：Solana USD₮ mint 为 `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB`；Ethereum USD₮ 合约为 `0xdac17f958d2ee523a2206206994597c13d831ec7`。两者是不同网络上的资产标识，不是 Token Program 地址。
- 证据质量／日期：A，发行方集成文档；未标注更新时间，2026-10-29 检索。支持清单是动态的；这不是对所有链上同名资产的完整审计。
- 应改 PPT：p29、p33、p42（暂定）。

### S02 — Tether 旧链过渡方案的后续修订

- URL：<https://tether.io/news/tether-provides-update-on-transition-plan-for-legacy-blockchains/>
- 支持结论：Omni Layer、Bitcoin Cash SLP、Kusama、EOS、Algorand 的 USD₮ 停止直接发行与赎回，不再与受支持版本同等受官方支持；2025-08-29 更新明确撤回冻结这些网络合约的计划，钱包之间仍可转移。
- 证据质量／日期：A／历史，发行方公告，发布于 2025-08-29；S01 当前页面也将这些链列为 deprecated。不能沿用旧计划写成“全部已经冻结”，也不能将“可转移”写成“仍可直接赎回”。
- 应改 PPT：p29、p33（暂定）。

### S03 — Circle 储备透明度、月度鉴证与公司审计

- URL：<https://www.circle.com/transparency>
- 支持结论：Circle 描述按 AICPA 鉴证标准提供月度第三方 assurance，内容是 USDC 储备价值与流通量关系；同页另行说明 Deloitte 自 2022 财年起审计 Circle 财务。储备包括现金与现金等价物；不能概括为全部美元纸币或单一银行现金。
- 证据质量／日期：A，发行方披露口径；动态储备栏目标记截至 2026-10-26，2026-10-29 检索。本文只确认披露及鉴证范围，未逐份打开最新会计师报告，也不把网站营销承诺当作审计意见。
- 应改 PPT：p28、p30（暂定）；纠错应为“月度储备鉴证不是完整财报审计”，而非“Circle 从未做财务审计”。

### S04 — Circle USDC Terms：直接赎回与市场价格

- URL：<https://www.circle.com/legal/usdc-terms>
- 支持结论：§2、§4 与 §13 将直接赎回与合资格、正常状态的 Circle Mint 账户及相关条件联系起来；无 Mint 账户的 Type B 持有人不能仅凭持币直接向 Circle 赎回。§13 不保证第三方平台价格始终为 1 美元；§8 区分 Circle 支持的 USDC 与第三方 copies / wrappers。
- 证据质量／日期：A，正式条款，页面 Last Updated 为 2026-10-15。页面说明该组条款针对 EEA 之外持有人，EEA 有另行文件；不能将这里的资格表述无差别外推全球，也不能替具体用户判定开户资格。
- 应改 PPT：p28、p30、p33（暂定）。仅用于忠实说明产品规则，不构成法律建议。

### S05 — Spark 官方集成文档：Sky LitePSM

- URL：<https://docs.spark.fi/dev/integration-guides/litepsm/>
- 支持结论：核心 DssLitePsm 交换 USDC 与 DAI，UsdsPsmWrapper 提供 USDC–USDS 接口；USDC 在单独的 pocket 中持有。文档提示费用、暂停状态、容量与外部 Token 依赖，不能把固定比率报价理解为无限流动性或永久零费用。
- 证据质量／日期：A，生态维护者的合约集成文档，列出 Ethereum mainnet 合约地址；未标注更新时间，2026-10-29 检索。足以证明 USDC 机制依赖，不足以证明 USDC 当前占全部抵押的比例。
- 应改 PPT：p31（暂定）。Sky LitePSM 与 Spark 多链 PSM3 是不同合约，不在本次展开其他跨链产品。

### S06 — Maker/Sky 官方 RWA Toolkit

- URL：<https://github.com/sky-ecosystem/rwa-toolkit>
- 支持结论：维护者将仓库定义为链下资产支持借贷工具；RwaToken 表示 RWA 抵押，RwaUrn 支持借出 DAI，conduits 处理放款与还款，RwaLiquidationOracle 为链下执行者提供清算信号。机制不只是 ETH 抵押自动清算，包含权限化及链下执行环节。
- 证据质量／日期：A／机制代码，Maker/Sky 项目维护者仓库；README 未标注统一发布日期，2026-10-29 检索，未锁定 commit。仓库存在及部署脚本不等于所有模块当前均有敞口或已部署。
- 应改 PPT：p31（暂定）。可写“Maker/Sky 机制体系包含 RWA 路径”；当前 USDS/DAI 的逐项 RWA 资产、机构名单、余额和比例本次未完成同期核验，不填数值、不将历史模块一律写成当前活跃资产。

### S07 — Ethena USDe Overview

- URL：<https://docs.ethena.fi/solution-overview>
- 支持结论：USDe 使用与支持资产匹配的衍生品空头对冲；文档涉及流动稳定资产、质押 ETH 收益，以及资金费率/期现基差。资产由 Off Exchange Settlement 服务商托管，并用于交易所保证金安排；OES 降低风险，不消除托管或交易所对手方风险。
- 负资金费率：若持续深度为负且资产收益不能覆盖成本，设计由 reserve fund 承担成本；页面没有无限补足承诺。其措辞是多数市场条件下相对稳定，不是所有情景中价格、储备净值或每枚可兑价值恒为 1。
- 证据质量／日期：A，协议机制及风险自披露；未标注更新时间，2026-10-29 检索。不是独立托管审计或当前持仓快照；不由示例推断今天全部支持资产只含 ETH，也不填 BTC、ETH、稳定币的当前比例。
- 应改 PPT：p28、p32（暂定）。USDe 与有收益累积机制的 sUSDe 分开，不把 sUSDe 收益写成 USDe 本身保证收益。

### S08 — Polygon PoS 官方定义

- URL：<https://docs.polygon.technology/pos/>
- 支持结论：标题明确将 PoS 定义为 Ethereum 的 EVM-compatible Proof-of-Stake sidechain，并引向 Heimdall、Bor、checkpoints 与 state sync 架构。依据该定义，不能把 Polygon PoS 标成 rollup L2。
- 证据质量／日期：A，官方开发者文档；未标注更新时间，2026-10-29 检索。与 Ethereum 有联系不等于具有 rollup 同一套安全机制；本文不从简短首页推导完整安全保证。
- 应改 PPT：p35（暂定）。

### S09 — Polygon zkEVM Mainnet Beta 退役原始公告

- URL：<https://forum.polygon.technology/t/sunsetting-polygon-zkevm-mainnet-beta-in-2026/21020>
- 支持结论：首帖宣布次年退役 zkEVM Mainnet Beta，描述当时的约十二个月 sequencer 过渡安排及降低支持；同时说明 zkEVM 的历史 rollup 定位，并把加强 PoS 列为另一方向。
- 证据质量／日期：A／历史，官方论坛管理层公告；**首帖发布于 2025-06-11 13:09，页面未给时区**。只采用首帖，不把普通社区回复当作官方承诺。
- 应改 PPT：p35、p36（暂定）。这是假定规划的发布日期，不是最后停机日期；关于退出能力必须结合 S10 更新。

### S10 — Polygon zkEVM 官方现状页

- URL：<https://polygon.technology/polygon-zkevm>
- 支持结论：官方状态为 Sunset Complete；**2026-07-03** sequencer 已退役、网络不再出块，Agglayer Bridge 不再处理 zkEVM 提款。EOA 资产回收有专门 Claims 路径，不能将此能力外推到锁在智能合约中的资产。
- 证据质量／日期：B／现状声明，官方产品页；明确给出事件日期，未标注页面最后更新时间，2026-10-29 检索。该状态更新优先于旧公告中笼统的“随时退出”表述；本次未连接钱包或测试 Claims。
- 应改 PPT：p36（暂定）。改成历史产品与退役说明，不继续作为当前可用链推荐；退役对象限定为 zkEVM Mainnet Beta。

### S11 — Polkadot Agile Coretime

- URL：<https://wiki.polkadot.com/learn/learn-agile-coretime/>
- 支持结论：官方 Wiki 将旧长期租赁 slot auction 与 bulk / on-demand coretime 分开，并在“最后一次拍卖”问答记载 **2024-09-19** runtime upgrade 启用 Agile Coretime，进行中拍卖取消、已有活跃租约迁移。
- 证据质量／日期：A，官方机制文档及历史迁移说明；未标注页面最后更新时间，2026-10-29 检索。部分 FAQ 仍有旧的“开发中”内容，不据此判定其他功能的当前上线状态。
- 应改 PPT：p37（暂定）。现行 coretime 定价仍可包含 Dutch auction / bidding；“替代长期插槽拍卖”不等于“完全没有拍卖或竞价”，也不支持固定 core 数、实时价格或容量。

### S12 — Polkadot XCM：格式，而非传输

- URL：<https://wiki.polkadot.com/learn/learn-xcm/>
- 支持结论：XCM 是 Cross-Consensus Message Format，定义消息及指令，不定义送达方式；文档另列 XCMP、HRMP、VMP 传输路径。其适用概念也不限于 Polkadot 平行链。
- 证据质量／日期：A，官方术语/机制文档；未标注更新时间，2026-10-29 检索。格式设计原则不能外推为任意桥、路由、执行环境必然成功或没有风险。
- 应改 PPT：p33、p38（暂定）。不把 XCM、具体通道、桥实现和资产赎回机制写成一个东西。

### S13 — Cosmos SDK 官方概述

- URL：<https://docs.cosmos.network/sdk/latest/learn/intro/overview>
- 支持结论：SDK 是应用专用链和账本的模块化框架，可建 public、private permissioned、consortium 网络；业务逻辑、共识等组件有分工，链可保持自己的执行与安全。SDK 本身不是 Cosmos Hub，也不是只允许在 Hub 之下运行的执行环境。
- 证据质量／日期：A，官方框架文档；未标注更新时间，2026-10-29 检索。页面性能及采用数量不作为两链对比证据。
- 应改 PPT：p39、p40（暂定）。由“安全可自行配置”与 S14 的独立共享安全功能可推导：接入 SDK/IBC 不自动使链获得 Hub 共享安全；此处不声称任何具体链今天采用哪种安全方案。

### S14 — IBC 维护方：范围及跨链验证能力

- URL：<https://ibcprotocol.dev/about>
- 支持结论：维护方将 IBC 定义为开放互操作标准；当前页面列出 Besu、Ethereum、Solana、Cosmos，并说明规范可在其他账本/VM 实现；历史部分将支持共享经济安全的 cross-chain validation 单独列为 2023 年新增能力。因此 IBC 不限于 Cosmos SDK 链，通信不能与共享安全混同。
- 证据质量／日期：A／规范范围，B／当前覆盖声明；页面未标注最后更新时间，2026-10-29 检索。列出某生态，不证明该生态所有网络、所有资产、所有版本和所有方向均已互通。
- 应改 PPT：p40（暂定）。共享安全应作为另外选择的能力审查；不采用页面累计规模、连接数量或“无 exploit”营销口径作安全担保。

### S15 — Solana Alpenglow 官方升级状态

- URL：<https://solana.com/upgrades/alpenglow>
- 支持结论：2026 年 10 月更新的正文记载 **Alpenglow 于 2026-10-21、epoch 1064 在主网启用**，第一阶段 Votor 替代 TowerBFT 投票机制；Rotor 是后续阶段，尚未排期。页面明确 PoH 不再用于原来的出块节奏控制。
- 证据质量／日期：B／现状声明，Solana Foundation 官方升级说明；页面显示初始月份为 2026-06、更新月份为 2026-10。本文未自行查 feature gate 或重放链上运行证据，部署状态按官方正文归属引用。
- 应改 PPT：p34、p41（暂定）。不仅删掉“PoH 是独立共识”，还要避免把历史 TowerBFT/PoH 架构当成 2026-10-29 的完整现状。页面 finality 数字是目标/预期且明确不是常数，不写成 TPS 或交易 SLA；该升级不改变 SVM 执行和手续费机制。

### S16 — Solana Account Structure / PDA

- URL：<https://solana.com/docs/core/accounts/account-structure>
- 支持结论：账户有 lamports、data、owner、executable、rent_epoch 字段；程序账户与数据账户用途不同，状态数据由 owner program 管理。PDA 由 program ID 与 seeds 确定性派生，没有对应私钥。
- 证据质量／日期：A，官方技术文档；未标注更新时间，2026-10-29 检索。这里的 owner 是程序所有者概念，不能与 Token Account 数据中的持有人 authority 混为一谈。
- 应改 PPT：p41（暂定）。不能将 PDA 讲成“程序保管私钥的钱包”；地址派生也不能自动证明地址上已有账户或资产。

### S17 — Solana Token Programs / Mint / Token Account / ATA

- URL：<https://solana.com/docs/core/tokens>
- 支持结论：Token Program 提供指令逻辑，Mint 标识资产并记录供应与权限，Token Account 记录某 mint 的持有余额与权限；ATA 是采用可推导地址的 Token Account，不是另一种资产，也不是钱包地址。钱包可为同一 mint 持有多个 Token Accounts。
- 证据质量／日期：A，官方技术文档；未标注更新时间，2026-10-29 检索。文档区分原 Token Program 与 Token-2022，不能不查账户就认定任意代币使用哪个程序或扩展。
- 应改 PPT：p42（暂定）。结合 S01 可讲“SPL USDT”；mint 名称和 symbol 不是发行方身份验证。不要将 Solana 上每个 token 都解释成独立部署的一套 ERC-20 式合约。

### S18 — Solana 2024-02-06 官方停机复盘

- URL：<https://solana.com/news/02-06-24-solana-mainnet-beta-outage-report>
- 支持结论：报告记载 2024-02-06 09:53 UTC 主网区块 finalization 停止，14:55 UTC 恢复共识进展，约五小时；原因涉及 legacy loader 触发的 JIT 缓存无限重编译循环。
- 证据质量／日期：A／历史，Solana 官网刊载、注明原由 Anza 发布的工程复盘；事件日期明确为 2024-02-06，正文未显示独立发布日期，2026-10-29 检索。
- 应改 PPT：p34、p41（暂定）。足以否定“Solana 从未宕机”；不能从这一次事件推算 2026 年故障率，不能替换成“总是宕机”或未经调查的两链可靠性排名。

## 三、改稿时的关键边界

### 1. 原生发行与桥接：审查对象必须落到资产

本次能确认的是 S01 中发行方认可的具体 USD₮ 标识及旧链状态，不是所有网络上所有“USDT”的来源。

- 改稿记录至少写清：网络、合约/mint、发行或包装主体、源资产、铸造与销毁/锁定路径、赎回对象和暂停权限。
- BSC 的特定 Binance-Peg 版本、Polygon 的特定桥接版本，若要肯定写出“由谁托管、桥接自哪条链”，须补该版本的一手机制与地址证据。本文不猜具体合约，也不将发行方名单的缺项当成对所有历史版本的完整否定证明。
- “跨链转移”与“同一发行方在多链分别发行”分开说明；消息互通不自动保证包装资产可获发行方直接赎回。[S01、S02、S04、S12]

### 2. Maker / Sky：只写已证实路径

可确认的路径是 USDC ↔ DAI LitePSM、USDS-facing wrapper，以及 RWA 模块中借出/收回 DAI 和链下执行者的角色。由此已可否定“纯 ETH、零链下依赖”。但本文未完成当前抵押资产库存核验，不能声称 RWA 比例、所有机构角色、全系统风险参数或每一个历史模块的现行启用状态。[S05、S06]

不将 DAI、USDS、sUSDS 和治理代币混为同一资产；不凭改名推导所有旧机制不变，也不加入未经部署/治理证据确认的冻结权限、储蓄率、迁移比例或“永远不可冻结”结论。

### 3. USDe：“风险对冲”不是“价格、净值、兑付恒等”

建议把支持资产、衍生品损益/成本、OES 托管与交易所保证金安排分别介绍。资产价格变化的对冲不能由逻辑上消除执行偏差、托管、对手方或流动性风险。储备基金承担负资金费率成本的设计，不等于所有压力下均可足额补偿；须区分储备净值、每枚赎回价值和二级市场价格。[S07]

### 4. 两链 TPS 与费用比较：先补可比测量，再下结论

本次 18 条来源不包含 Ethereum/Solana 同期、同负载的性能及费用样本，因此**不提供 TPS 或费用数值排名**。S15 的目标 finality 不是实测 TPS，旧架构下包含投票交易的统计也不能未经说明与升级后的交易口径拼接；S18 只证明一次有明确范围的历史中断。[S15、S18]

若原 PPT 有数值，改稿前要求其同时交代：

1. 网络范围：Ethereum mainnet、某个 rollup 或生态合计不能混用；Solana 必须注明集群与客户端/升级时期。
2. 统计口径：成功用户交易、所有上链交易、投票、失败交易与链内指令是否计入；理论上限、峰值和持续吞吐分开。
3. 样本条件：观测窗口、负载和交易类型、数据入口与计算方法；不可比较两个日期或两个压力条件下随意挑出的数字。
4. 费用项目：网络费、优先费、账户创建/存储资金、应用收费分开；原生币金额、美元换算时间及中位数/分位数注明。
5. 可用性口径：出块停止、finalization 中断、部分 RPC 不可用与拥堵不能统称同一种“宕机”；未检索到事件不等于从未发生。

## 四、末尾红线：不得使用的未经验证数字与主观结论

- 不使用无日期、无网络、无方法的 TPS、费用、finality、验证者数、core 数、利用率、TVL、市场份额或“宕机次数”。官方目标、测试结果与营销文案也不自动成为主网持续性能。
- 不填未经同期一手核验的 USDT/USDC 储备金额、DAI/USDS 的 ETH/USDC/RWA 比例、USDe 资产配置、对冲敞口、储备基金余额、资金费率或 sUSDe 收益率。
- 不使用“净值恒为 1”“所有人随时直接赎回”“所有链都原生”“无限流动性”“绝无机构”“永不冻结”“从未宕机”“绝对安全”等无条件表述。
- 不从官方鉴证、审计、托管安排或历史无事故记录推导“无风险”；不把未来 roadmap、后续阶段或旧公告写成截至 2026-10-29 已全面部署。
- 不给出“最好/最值得投资的稳定币或链”“必然升值”“某链将取代另一链”“买入/卖出/收益保证”等主观投资结论；机制差异不直接等于投资优劣。
- 本文不判断特定用户的法律资格、监管适用或资产追索权。条款只按适用范围引用，个体法律问题不在本次研究范围。
- 尚待补证但不妨碍上述机制纠错：用户 PPT 原文与精确页码；BSC/Polygon 特定 USDT 表示的来源与合约；当前 Maker/Sky 抵押库存；USDe 当前持仓；Ethereum/Solana 同期性能/费用数据。未取得前保留限定语，不编造数字或完成状态。
