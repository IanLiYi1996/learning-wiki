# 03｜多链升级：Polygon 的证明边界、Polkadot 的资源调度与 IBC 的协议演进

- 核查日：2026-10-29（北京时间）。
- 旧内容定位：PPT 38–42；[生态基础篇](../chapters/04-ecosystem.md)、[纠错表](../corrections.md)、[二次复核](../notes/follow-up-verification.md)。
- 学习目标：说明资源、执行、共识、数据可用性、消息与资产分别由谁负责，并据此设计迁移验收。
- 证据口径：“官方称已运行”是官方状态声明，不是本次链上实测；“机制”不等于所有部署都支持；教学例和验收清单是推导与建议。
- 本次仅阅读公开一手资料与固定版本源码，没有连接账号、使用付费资源、执行网页中的命令、部署节点或提交交易。来源使用独立编号 `MC-U1` 起，不复用基础篇的编号。

## 1. Polygon：退役的是特定网络，不是整个技术家族

### 1.1 旧假设与新核心对象

旧课件容易留下三个印象：Polygon 就是一条 L2；zkEVM 是当前统一执行底座；退役后换一个产品名即可继续。现在应把对象拆开：

| 对象 | 当前职责与状态 | 不能推导出的结论 |
| --- | --- | --- |
| Polygon zkEVM Mainnet Beta | 官方称 sequencer 于 2026-07-03 退役，停止出块，Agglayer Bridge 不再处理该网常规提款。[MC-U1｜退役页](https://polygon.technology/polygon-zkevm) | 不代表所有带 zkEVM 名称的网络退役 |
| Polygon PoS | 仍作为公共链基础设施使用；独立共识侧链，不是因连接 Ethereum 就变成 rollup。[MC-U3｜当前基础设施](https://docs.polygon.technology/infrastructure)、[MC-U4｜侧链模型](https://ethereum.org/developers/docs/scaling/sidechains/) | 不自动继承 Ethereum 对全部执行的验证 |
| Polygon CDK | 建设专用链的产品与技术栈；当前提供 OP Stack 和 Besu 等路径。[MC-U5｜CDK 概览](https://docs.polygon.technology/chain-development/cdk/get-started/overview) | 不是一条供所有人共同使用的新主网 |
| Agglayer | 跨异构链桥接与验证基础设施，接入链保留自己的架构和治理。[MC-U3｜职责划分](https://docs.polygon.technology/infrastructure) | 接入不等于全部链共享同一种执行证明 |
| Open Money Stack（OMS） | 当前官网按钱包、出入金、支付编排、跨链与结算组织产品，可组合使用。[MC-U2｜OMS](https://docs.polygon.technology/oms/overview) | 不是 zkEVM 账户、合约与资产的强制替代者 |

OMS 是服务编排视角，PoS、CDK、Agglayer 是基础设施视角。官方还区分公共协议层与需要服务接入条件的支付、钱包层；不能把“开放基础设施”理解成所有 API 无需申请，也不能把服务组合解释为共识升级。[MC-U3｜基础设施边界](https://docs.polygon.technology/infrastructure)

### 1.2 执行客户端、共识与部署模式不是同一层

OP-Geth 是 OP Stack 的执行客户端；OP Node 负责相应的链派生、同步和出块相关协调。Besu 是另一条执行客户端路径，当前 CDK Besu 使用 QBFT，即已知验证者集合运行的拜占庭容错 PoA 共识。QBFT 的投票不是 zkEVM 执行证明。[MC-U6｜组件表](https://docs.polygon.technology/chain-development/cdk/cdk-opgeth/architecture)、[MC-U7｜Besu 安全模型](https://docs.polygon.technology/chain-development/cdk/cdk-besu/overview)

zkEVM 既出现在历史网络名称中，也描述将 EVM 执行关系纳入有效性证明的技术方向。旧 `zkevm-node` 仓库描述 executor、prover、批次和 L1 验证，但有归档通知；当前 CDK 的客户端列表不能从这份历史 README 推导。当前仍有其他接入链被官方名单标为 zkEVM，这也不等于 Polygon zkEVM Mainnet Beta 恢复运行。[MC-U14｜历史节点](https://raw.githubusercontent.com/0xPolygonHermez/zkevm-node/develop/README.md)、[MC-U5｜当前客户端](https://docs.polygon.technology/chain-development/cdk/get-started/overview)、[MC-U13｜接入链分类](https://docs.polygon.technology/interoperability/agglayer/supported-chains)

部署模式解决的是另外两个问题：如何验证执行，数据存在哪里。

| CDK 模式 | 执行与桥验证 | 数据可用性（DA） | 本次查到的产品状态 |
| --- | --- | --- | --- |
| sovereign | 不要求本链执行 prover；Agglayer 仍生成 pessimistic proof，接入认证依配置而定 | 不能一概说离链：OP-Geth 组件参考列 L1 batcher；Besu 路径不向 L1 发布交易数据 | 概览标 Live、默认模式；Besu 目前仅此模式 |
| validium | 执行有效性证明与桥约束验证 | 离链／替代 DA；当前具体实现包括 OP Succinct AltDA | 概览标 Live |
| zkrollup | 执行有效性证明 | 所需交易数据发布到 Ethereum | 概览仍标 In development |

表格依据：[MC-U5｜模式状态](https://docs.polygon.technology/chain-development/cdk/get-started/overview)、[MC-U6｜模式组件](https://docs.polygon.technology/chain-development/cdk/cdk-opgeth/architecture)、[MC-U7｜Besu](https://docs.polygon.technology/chain-development/cdk/cdk-besu/overview)、[MC-U8｜AltDA 实现](https://docs.polygon.technology/chain-development/cdk/privacy)。模式组件页的 validium DA 链接仍带 TBD，详细隐私页却已有具体实现，属于文档粒度与更新漂移；不能据一个占位符否定整个模式，也不能据架构图宣称 zkrollup 已正式可交付。

因此，本文不把这些部署全部标成安全含义相同的“Ethereum L2”。营销上的 L2 总称不能替代“谁验证状态、数据能否取回、怎样退出”的逐项描述。“无需 prover”也只是本链无需执行 prover，不是整条 Agglayer 路径没有密码学证明。

### 1.3 Pessimistic proof 究竟证明什么

它首先是桥资产会计的隔离机制，不是对每笔本链智能合约执行的完整复算。它跟踪的是受桥接规则约束的跨链资产余额、出口与已导入出口，而不是钱包里的所有账户 storage。[MC-U9｜证明架构](https://docs.polygon.technology/interoperability/agglayer/core-concepts/pessimistic-proof/architecture)

简化验证流程：

1. 链提交 certificate，描述旧状态、待导入的桥出口、待导出的桥出口及新承诺。
2. 检查导入证明；按资产来源网络与来源合约定位资产，更新 Local Balance Tree。
3. 用 Nullifier Tree 记录已导入出口，拒绝重复消费；更新 Local Exit Tree，并检查余额不能透支。
4. 先运行原生验证，再用 zkVM 证明相同计算，验证证明并结算对应承诺。

这些对象和流程来自 [MC-U44｜证明生成](https://docs.polygon.technology/interoperability/agglayer/core-concepts/pessimistic-proof/proof-generation)、[MC-U10｜数据结构](https://docs.polygon.technology/interoperability/agglayer/core-concepts/pessimistic-proof/data-structures)。桥的目标链 claim 还要核验出口的 Merkle 路径并记录已领取状态，不能仅凭源链事件截图到账。[MC-U12｜资产桥接](https://docs.polygon.technology/interoperability/agglayer/core-concepts/unified-bridge/asset-bridging)

教学例：某链对一项受会计约束的外来资产已导入 100 单位、已导出 30 单位，剩余预算是 70。没有新增合法导入时，再申请导出 80 应被拒绝。这个例子说明跨链透支约束；不证明剩余 70 在本链被公平分给谁，也不保证本链合约没有漏洞。

再看三种不同问题：

| 问题 | 需要的证据 | 不能由它代替的证据 |
| --- | --- | --- |
| 合约执行是否符合状态转换规则 | 执行有效性证明，或具体链的共识／验证机制 | 桥预算守恒本身不证明内部执行正确 |
| 跨链资产是否重复消费或超额导出 | 桥承诺、导入证明、余额与 nullifier 约束 | 不保证数据可获取、用户请求不被审查 |
| 重建状态所需数据能否持续取得 | DA 发布、保存、取回与故障恢复机制 | 一个有效 proof 或一个数据哈希都不提供原始数据 |

Aggchain 的认证路径可以是 ECDSA 授权，也可以是 generic validity proof；前者依赖配置中的授权者，不能讲成后者。Besu 文档明确其 pessimistic proof 不证明内部状态转换；validium 的详细实现则把原始批次留在运营方 DA，仅在 Ethereum 锚定承诺和有效性证明。[MC-U11｜认证与证明类型](https://docs.polygon.technology/interoperability/agglayer/core-concepts/state-transition-proof/aggchain-proof)、[MC-U7｜Besu 边界](https://docs.polygon.technology/chain-development/cdk/cdk-besu/overview)、[MC-U8｜DA 边界](https://docs.polygon.technology/chain-development/cdk/privacy)

### 1.4 退役后的具体步骤与迁移验收

官方 Claims 针对退役时自托管 EOA 持有的资产，在 Ethereum 上领取，独立于已退役 sequencer。DeFi 合约、多签合约和第三方桥合约内资产不能通过该界面恢复，应联系相应协议／合约运营方。界面当前声明提供至 2027-12-31；本文没有核验任何具体地址资格。[MC-U1｜恢复范围](https://polygon.technology/polygon-zkevm)

建议钱包与链团队依次处理：

1. 停用旧网充值、普通交易和常规提款入口，历史查询与恢复提示分别保留。
2. 按最后可核对区块盘点 EOA 余额、合约余额、仓位凭证、未完成桥消息及管理员权限，不把“控制签名钥匙”等同“直接持有合约内资产”。
3. 先确认原网恢复路径，再独立选择目标：使用现有 PoS 公共链，或建设具体模式的 CDK 链；OMS 接入也是独立选择。
4. 在目标链重新部署或按经过审核的方案导入状态；逐项迁移代理权限、oracle、索引、资产表示与未完成业务。
5. 按源资产处置、目标到账和业务负债三方对账，不能只证明目标合约部署成功。

这是工程建议，不是官方保证的一键迁移。Agglayer 的跨链组合能力不能扩大为“原子搬走所有历史合约、storage 和资产”。通用 Exit Certificate Tool 也有 PP 模式、委员会阈值、停机与已结算出口等前提，且把合约锁定价值单独归集处理；不能用它的能力说明覆盖特定 zkEVM Claims 的 EOA 限制。[MC-U41｜退出工具](https://docs.polygon.technology/interoperability/agglayer/integrations/exit-certificate-tool)、[MC-U1｜特定网络规则](https://polygon.technology/polygon-zkevm)

验收重点：网络身份和资产来源一致；普通到账、证明结算、领取完成分别建状态；覆盖重复 claim、数据不可取、授权者停机与升级暂停。收益是可以按需求组合执行、隐私和互操作；边界是安全模型并未统一，代码可复用也不意味着状态与资产自动迁移。

## 2. Polkadot：从长期插槽转为可分配的验证资源

### 2.1 旧假设与当前状态

旧模型是“长期 slot auction → 固定租期 → 一条平行链占一个 core”。官方 Wiki 记载，Polkadot 在 2024-09-19 runtime 升级启用 Agile Coretime，取消当时进行中的旧拍卖，并把已激活租约迁为对应资源安排。现行核心是 bulk 与 on-demand，而不是要求每条新链先赢长期插槽拍卖。[MC-U15｜迁移记录](https://wiki.polkadot.com/learn/learn-agile-coretime/)

这不等于取消全部市场定价：bulk 销售仍有优先续租、Dutch auction 价格发现及固定价格阶段。2026-06-29 更新的官方开发文档把 bulk 周期列为 28 天；这是当时配置，不是协议永远固定的常数。[MC-U17｜销售与续租](https://docs.polkadot.com/parachains/runtime-maintenance/coretime-renewal/)、[MC-U16｜当前资源说明](https://docs.polkadot.com/reference/polkadot-hub/consensus-and-security/agile-coretime/)

### 2.2 新核心对象：core、time、region 与 task

core 是 relay chain 验证资源的虚拟抽象，不是购买一台专属 CPU。coretime 是使用它的时间；timeslice 是调度粒度；region 是 bulk 资源权利的表示，涉及特定 core、时间区间及占用份额；task 对应待调度工作，在本文流程中通常是已注册的 ParaID。[MC-U15｜术语](https://wiki.polkadot.com/learn/learn-agile-coretime/)

| 操作 | 改变什么 | 教学上应避免的误解 |
| --- | --- | --- |
| bulk | 取得一段连续资源，可分配、拆分等 | 买到资源不等于已经注册或启动链 |
| on-demand | 为待验证 parablock 下单，进入按需调度 | 不是给所有钱包交易承诺即时打包 |
| split | 沿时间轴拆成前后相接的 region | 不是把同一时刻算力复制两份 |
| interlace | 同一时间区间内按调度份额轮流服务不同 task | 不是多个 task 同时独占一个 core |
| renew | 为符合条件的分配延续下一期资源 | 并非所有拆分后的 region 都保留限价续租资格 |
| elastic scaling | 为同一个 task 使用多个 core | 不等于 interlace，也不等于每条链已自动扩容 |

依据：[MC-U16｜bulk、split、interlace、on-demand](https://docs.polkadot.com/reference/polkadot-hub/consensus-and-security/agile-coretime/)、[MC-U17｜renew](https://docs.polkadot.com/parachains/runtime-maintenance/coretime-renewal/)。完整 bulk 分配给单条链可有 price-capped renewal；拆分、交错或保持闲置会改变资格。续租权不是永不调价、永不失效，也不是业务收益保证。

### 2.3 购买、注册与共享安全的具体流程

把三个动作分别验收：

```text
注册链：ParaID + runtime Wasm + genesis head，等待 onboarding
准备出块：collator + 本链状态 + relay chain 同步
取得调度：bulk region 分配到 task，或提交 on-demand 订单
进入验证：collator 提交候选块 / PoV → relay validators 验证与包含
```

注册和资源流程依据 [MC-U18｜部署指南](https://docs.polkadot.com/parachains/launch-a-parachain/deploy-to-polkadot/)；该指南示范网络为 Paseo，不将其参数直接当 Polkadot 主网配置。验证流程依据 [MC-U19｜平行链共识](https://docs.polkadot.com/reference/parachains/consensus/)。

资源 NFT 的持有者可以先持有资源，尚未分配给链；只有注册、onboarding、调度和节点条件匹配，才会产生进入共享安全流程的候选块。bulk 的 Broker pallet 在 Coretime 系统链，部署指南把 on-demand 下单列在相应 relay chain 的 OnDemand pallet。实际入口要按目标网络 metadata 核对。[MC-U18｜资源入口](https://docs.polkadot.com/parachains/launch-a-parachain/deploy-to-polkadot/)

“共享安全”来自 relay validators 使用已注册状态转换逻辑验证候选块，以及包含、可用性、批准／争议等过程，不来自资源交易付款截图。它也不保证应用业务规则正确、用户永远能及时提交交易或外部桥零风险。[MC-U19｜验证责任](https://docs.polkadot.com/reference/parachains/consensus/)

教学例：A 链需要持续出块，B 链只偶尔活跃。A 可申请完整 bulk；B 可选择按需或合适的 interlaced 分配。若把某 region 拆为前后两段，是 split；在相同区间轮流服务两链，是 interlace；让 A 同时使用两个 core，才是 elastic scaling。三者都不能让已有历史状态凭空分叉后自动合并。

### 2.4 Elastic scaling 与 JAM：状态必须分层

elastic scaling 的核心是同一链在多个 core 上提交更多候选块，验证阶段可并行，但包含时仍需检查状态根衔接；collator、runtime 和调度必须支持相应生产率。不是把有先后依赖的状态转换随意并发。[MC-U21｜实现说明](https://docs.polkadot.com/reference/parachains/consensus/elastic-scaling/)

本次可确认的证据层次：

- 官方 Wiki 记录 2024-12 在 Kusama 进行过 live 测试，并描述 Kusama 多核能力；这不能写成“从未实现”。[MC-U20｜测试与机制](https://wiki.polkadot.com/learn/learn-elastic-scaling/)
- Agile Coretime Wiki 与 2026-06-29 开发页仍写 elastic scaling 在开发中，专门的 elastic 文档则描述多核工作机制。不能强行拼成“Polkadot 主网所有链已自动弹性伸缩”。[MC-U15｜状态措辞](https://wiki.polkadot.com/learn/learn-agile-coretime/)、[MC-U16｜更新页](https://docs.polkadot.com/reference/polkadot-hub/consensus-and-security/agile-coretime/)、[MC-U21｜机制页](https://docs.polkadot.com/reference/parachains/consensus/elastic-scaling/)
- 截至核查日，具体 Polkadot 主网 runtime 的启用条件、哪些链实际采用多核及自动扩缩策略，本次未完成独立验证，标为**未证实**；不沿用测试吞吐或目标延迟作为 SLA。

JAM 官方 Wiki 使用“prospective design to succeed the relay chain”的路线图措辞。可以学习其 service、Refine／Accumulate 等设计，但本教程仍以 relay chain 当前注册、调度与验证流程为基础；没有证据就不能宣布 JAM 已替代它。[MC-U24｜JAM 状态](https://wiki.polkadot.com/learn/learn-jam-chain/)

### 2.5 XCM 与传输，以及团队迁移验收

XCM 是跨共识消息的格式与指令语言，不负责选择传输。HRMP 经 relay 路由，XCMP 有不同传输设计，VMP 用于 relay 与平行链之间；当前 Wiki 仍注明 XCMP 在开发中，多数消息走 HRMP。代码或 pallet 名含 XCMP 不足以证明已启用直接传输。[MC-U22｜XCM 格式](https://wiki.polkadot.com/learn/learn-xcm/)、[MC-U23｜传输状态](https://wiki.polkadot.com/learn/learn-xcm-transport/)

建议旧插槽团队核对迁移后的 lease／region、core、task、到期与续租资格；把续租变成运维任务。当前文档已有 auto-renewal，但要求 HRMP 通道、Coretime 链上的 sovereign account 资金及明确配置，并有 `AutoRenewalFailed` 事件；“已启用自动续租”不等于付款永远成功。[MC-U17｜续租运维](https://docs.polkadot.com/parachains/runtime-maintenance/coretime-renewal/)

钱包验收应分别确认源交易、消息投递与目标执行；核对 XCM 版本、Location、资产来源、执行费用、weight、目标 barrier 和错误恢复。共享安全不自动允许所有指令，发送成功不等于目标资产到账。这是基于格式与异步执行分层的工程建议，不是本次运行结果。

收益是资源周期更灵活、闲置资源可重分配；边界是资源不足、未续租、节点落后或目标消息配置不匹配仍可影响业务连续性。

## 3. Cosmos / IBC：跨生态通信升级，不是自动共享安全

### 3.1 旧假设与新对象

“Cosmos SDK 是造链框架，IBC 是通信协议”仍有用；“IBC 只在 Cosmos 域内”“接入 IBC 就由 Cosmos Hub 保护”都不成立。官方现在声明支持 Cosmos、Ethereum、Solana、Besu 等环境，但这里的 Besu 是客户端／执行环境类别，不是一条同名公共主网。[MC-U30｜官方支持声明](https://ibcprotocol.dev/about)

ibc-go 从 v10 开始在同一发布线中包含 classic 与 v2；两套协议分开，一条连接使用其中一套。升级库不等于把旧 channel 自动变成 v2 client pair。[MC-U25｜协议并存](https://docs.cosmos.network/ibc/latest/intro)

### 3.2 Classic 与 v2 的实际差别

| 维度 | IBC classic | IBC v2 |
| --- | --- | --- |
| 连接对象 | client、connection、port、channel | client pair、router、application |
| 建立路径 | 两侧 client，再完成 connection 与 channel 握手 | 配置 client 与 counterparty 绑定，不沿用两套握手 |
| 应用路由 | port/channel 及应用绑定 | router 按 port 定位应用；packet 标识源／目标 client |
| 应用数据 | packet data；版本主要在 channel 建立／升级时协调 | payload 显式带 source/destination port、version、encoding、value |
| 超时 | timeout height 和／或 timestamp；字段单位依实现 | packet 使用 Unix 秒级 timestamp；proof height 仍存在 |
| 安全验证 | client 验证对端共识状态与 commitment proof | 保留 client 验证；可使用不同验证模型 |

架构与握手依据 [MC-U26｜classic 对象](https://docs.cosmos.network/ibc/latest/ibc/overview)、[MC-U25｜v2 对象](https://docs.cosmos.network/ibc/latest/intro)；字段依据 [MC-U27｜v10.7.0 classic packet](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/types/packet.go)、[MC-U28｜同版 v2 packet](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/v2/types/packet.go)。v2 去掉的是 timeout height 语义，不是去掉验证证明时使用的高度。

client 不是“相信 relayer 说发生了什么”。它按对应实现验证对端的共识更新与承诺；可信初始状态、验证者变化、有效期、错误行为处理和证明格式仍需检查。v2 的 client 层也允许多签、ZK verifier 或 conditional 等模型，不能把所有路线都说成同一种轻客户端信任假设。[MC-U26｜client 与 proof](https://docs.cosmos.network/ibc/latest/ibc/overview)、[MC-U25｜验证模型](https://docs.cosmos.network/ibc/latest/intro)

**版本陷阱：**latest 文档描述 packet 可带多个 payload，并讨论一次目的端执行的原子回滚；但官方 Hub 版本页列 ibc-go **v10.7.0**，该 tag 的 `Packet.ValidateBasic` 要求 payload 数量恰好为 1。因此，Hub 当前能力不能从 latest 的多 payload 描述直接推导，更不能扩展成所有跨链调用全局原子提交。[MC-U25｜latest 描述](https://docs.cosmos.network/ibc/latest/intro)、[MC-U34｜Hub 版本](https://docs.cosmos.network/hub/latest/start/versions)、[MC-U28｜固定版限制](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/v2/types/packet.go)

### 3.3 Commitment、relayer、ack 与 timeout 的完整路径

下面按 v10.7.0 的 v2 实现解释；classic 同样有发送、接收、确认、超时生命周期，但标识、排序和存储路径不同，不能复用未经适配的报文字节。[MC-U27｜classic 格式](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/types/packet.go)、[MC-U29｜v2 实现](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/v2/keeper/packet.go)

1. **准备：**两侧安装兼容 client 与应用，绑定 counterparty，登记 router 的 port、版本和编码。
2. **Send：**源链应用执行发送逻辑，分配 sequence，将 packet commitment 写入状态；应用可在此锁定或销毁相应资产。
3. **Relay / Receive：**relayer 搬运 packet、证明与 proof height。目标链验证 client 配对、未超时、源 commitment 的 membership；写 receipt 防重复，再由应用处理 payload。
4. **Acknowledgement：**目的端写 ack 承诺；relayer 把 ack 与证明送回。源链验证后清除原发送承诺，应用根据成功或错误结果完成业务处理。
5. **Timeout：**在对端共识状态的时间达到截止后，提交目标 receipt 不存在的证明。源链验证未接收与原承诺后清除承诺，再由应用执行超时处理。

绑定与 router 依据 [MC-U25｜v2 概览](https://docs.cosmos.network/ibc/latest/intro)；收据、ack、membership／non-membership 与承诺清除依据 [MC-U29｜v10.7.0 keeper](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/v2/keeper/packet.go)。上述资产处置取决于具体应用，核心协议不自动铸币，也不为任意应用保证退款。

Commitment 不是 relayer 的声明或事件截图：v10.7.0 的 v2 实现把目标 client、timeout 和 payload 字段纳入哈希，再在规定的源 client／sequence 路径验证。证明还必须锚定到 client 已接受的共识状态。[MC-U43｜承诺构造](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/v2/types/commitment.go)、[MC-U26｜路径与验证](https://docs.cosmos.network/ibc/latest/ibc/overview)

重放防护不是一句“sequence 唯一”：它还需要 client／channel 作用域、目标 receipt、源 commitment 比较与已完成状态。修改 payload、换目标 client 或重复 ack，不能因为 relayer 再提交一次就再次入账。classic 另有 ordered/unordered channel 语义；不要默认为所有消息都按同一全局顺序执行。[MC-U29｜重放检查](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/v2/keeper/packet.go)、[MC-U43｜字段承诺](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/v2/types/commitment.go)、[MC-U26｜排序边界](https://docs.cosmos.network/ibc/latest/ibc/overview)

ack 可以表示应用错误，不是“收到即成功”。timeout 也不是钱包本地计时结束自动退款：对端证明、源链处理和应用恢复都不可少。目标已经写 receipt、但 ack 尚未返回时，不能凭“我没看到 ack”伪造未接收证明。这里的“端到端”仅指两端 client 验证、packet 生命周期与应用语义闭环，不承诺任意多跳路线具有一个统一的端到端证明。

### 3.4 当前哪些路线有官方依据

| 证据范围 | 本次能写的状态 | 仍需单独核验 |
| --- | --- | --- |
| Cosmos Hub 的 classic 与 v2 | 当前 Hub 文档声明两者在 `cosmoshub-4` 均 live | 某个 client／channel 是否 active、资产与方向是否可用 |
| Hub ↔ Ethereum Eureka | 官方有 mainnet 部署资料、技术说明；两端使用轻客户端，Ethereum 一侧使用 SP1 降低验证开销 | 具体部署地址、升级权限、client 状态与应用限制 |
| Solana、Besu 等环境 | IBC 官网当前声明支持；不能继续写“绝不能跨生态” | 具体链、主网／测试网、classic／v2、client 类型与路线 |
| Base、Arbitrum 等特定方向 | Eureka 概览仍有“soon”措辞 | 本次未取得足够的逐路线当前证据，标未证实 |

依据：[MC-U35｜Hub 当前 relaying](https://docs.cosmos.network/hub/latest/infrastructure/relaying)、[MC-U31｜Eureka 范围](https://docs.cosmos.network/skip-go/eureka/eureka-overview)、[MC-U32｜技术路径](https://docs.cosmos.network/skip-go/eureka/eureka-tech-overview)、[MC-U30｜协议级支持](https://ibcprotocol.dev/about)。不把官网支持类别、产品路线图和可用的具体资产路径混成一张“全部互通”地图。

协议默认开放 relaying 与特定部署的开放性也不同：当前 Hub 文档明确 v2 client 可限制 `allowed_relayers`；Eureka 技术页描述初期 permissioned relay，安全页另列升级、暂停与 client 管理权限。使用轻客户端不意味着无管理员风险，也不意味着任何 relayer 当前都能提交。[MC-U35｜当前 allowlist](https://docs.cosmos.network/hub/latest/infrastructure/relaying)、[MC-U32｜relay 条件](https://docs.cosmos.network/skip-go/eureka/eureka-tech-overview)、[MC-U33｜管理权限](https://docs.cosmos.network/skip-go/eureka/security-properties)

### 3.5 Interchain Security：独立机制，而且 Hub 现状已改变

先给出当前结论：**官方 Hub 文档称 Gaia v28.0.0 已移除 ICS provider 模块，Hub 不再运行 consumer chains。**固定 tag 的 v28.0.0 发布说明也明确此项删除；当前版本页列主网 v28.3.1。因此，不能把仍在线的旧 ICS／Next 教程写成“今天可以按原流程向 Cosmos Hub 申请共享安全”。[MC-U39｜当前 Hub 说明](https://docs.cosmos.network/hub/latest/getting-started/what-is-gaia)、[MC-U40｜v28.0.0 发布说明](https://github.com/cosmos/gaia/releases/tag/v28.0.0)、[MC-U34｜当前版本](https://docs.cosmos.network/hub/latest/start/versions)

这不影响理解 provider/consumer 的机制，也不等于 IBC 随之停止。ICS 是建立在 IBC 上的专门应用：provider 的验证者另外运行 consumer 节点，consumer 通过专用通信接收验证者集合更新；它不是普通 token transfer 自动附带的功能。[MC-U36｜ICS 机制](https://cosmos.github.io/interchain-security/introduction/overview)

旧／通用机制的流程是：创建 consumer 身份与初始化参数 → 确认 provider 参与集合及 consumer key → 生成匹配的启动状态 → 到启动时间运行 consumer → 维护验证者更新、处罚与相应通信。权限化程度也不相同：Opt-in 不强迫验证者参与，可以免治理创建；Top-N 要求按 provider 投票权阈值选出的验证者参与，因此需治理。[MC-U37｜身份与阶段](https://cosmos.github.io/interchain-security/features/permissionless)、[MC-U38｜参与集合](https://cosmos.github.io/interchain-security/features/partial-set-security)

Top-N 不是“人数前 N 个”，而是按 provider 投票权累计阈值选择；历史 ADR 明确这个定义。ADR 中早期“全部通过治理”的接入流程已被后续 Permissionless ICS 演进，不照搬为当前机制；allow／deny list 等 power-shaping 配置还会影响最终 consumer 集合。[MC-U42｜Top-N 定义与设计沿革](https://cosmos.github.io/interchain-security/adrs/adr-015-partial-set-security)、[MC-U37｜后续权限模型](https://cosmos.github.io/interchain-security/features/permissionless)、[MC-U45｜集合塑形](https://cosmos.github.io/interchain-security/features/power-shaping)

这些机制文档标为 **Next**，本文用于解释安全对象，不作为当前 Hub 服务入口。Hub 移除 provider 不等于通用 ICS 机制从此不存在；其他部署是否可用需要独立证据。历史 consumer 的独立运行、安全迁移和现行 provider 状态要读各链正式公告；本次没有逐链验证名单，不猜哪些链仍继承 Hub 安全。

### 3.6 教学例、迁移步骤与验收

假设 A 链发起 10 单位资产转移到 B。A 有发送承诺，B 校验后执行应用并写 receipt；B 的应用若拒绝资产，应返回相应错误 ack，A 再按应用规则处理。若 B 未接收且满足超时证明条件，A 执行 timeout。两链仍可以有不同验证者集合；这些过程只证明通信及应用处置关系，不能证明 B 的验证者由 A 或 Hub 提供。

假设另一路线是 `A —classic→ Hub —v2→ Ethereum`。Hub 是中间应用与协议转换／转发点，不是透明电缆；应逐段核对承诺、资产表示与错误恢复。官方 Eureka 的技术路径确实允许已有 classic 链通过 Hub 接入，但不能因此把 A 标成已经升级为 v2，或获得 Hub 的共享安全。[MC-U32｜接入路径](https://docs.cosmos.network/skip-go/eureka/eureka-tech-overview)

建议链团队迁移时：

1. 固定本链 SDK／ibc-go、对端实现、client 类型与应用版本，区分库支持和启用部署。
2. 盘点 classic 的 channel、连接、未完成 packets、client 到期与资产路径；新增 v2 配对，不静默改写旧历史。
3. 按 router 与 payload 适配编码、应用回调、超时单位、允许 relayer 和权限；先验证所用版本是否仅单 payload。
4. 逐笔收敛旧承诺或明确保留旧协议服务，核对目标资产来源与供应守恒；不要只按 symbol 合并余额。
5. 将收到、应用成功、ack 返回、timeout 完成和人工处理分别建账，并保留证据高度、路径与原始 packet。

钱包验收至少包含：重复 packet、错误编码／版本、过期或冻结 client、错误 proof height、重复 ack、已收到但 ack 延迟、relayer 停机／不在 allowlist、目标应用失败与超时恢复。切换通信协议不应自动更改安全来源；历史依赖 ICS 的链还需独立验收现行验证者集合和安全迁移。

收益是更容易支持异构执行环境、降低握手与应用版本协调负担；边界是 client 安全模型、两端共识、应用代码、管理员和通信活性仍需分别审查。证明消息来自对端，不代表对端可信，更不代表链间自动共享安全。

## 4. 自测：能否指出“新能力”的前提

1. Polygon zkEVM 退役为什么不能推出 PoS、CDK 与 Agglayer 都停止？——对象与生命周期不同。
2. sovereign “无 prover”为什么仍能有 ZK proof？——本链执行 prover 与 Agglayer 桥证明不是同一职责。
3. validium 执行证明有效、DA 无法取回，是否等于可正常退出？——不能；还需数据与退出条件。
4. 买到 region 后为何链可能不出块？——尚未注册／onboard、未分配 task 或节点条件未满足。
5. split、interlace、多核 elastic 各沿哪个维度变化？——时间区间、时间内份额、同 task 的 core 数。
6. 已开 auto-renewal 是否可以不监控？——不能，还要资金、资格、执行与失败事件。
7. XCM 发送成功能否代替目标执行验收？——不能；格式、投递、执行与到账分开。
8. 没收到 ack 可否直接退款？——不能；需要区分已接收、未接收证明与应用规则。
9. latest 说多 payload，Hub 是否就支持？——不能；v10.7.0 固定源码只允许一个。
10. Hub 的 IBC v2 live 能否证明它仍提供 ICS？——不能；当前官方资料明确 provider 已移除。

## 5. 一手来源、版本与状态表

下表均于 2026-10-29 查阅。没有发布版本的页面记为“滚动文档”，不把搜索抓取日当发布日；源码 tag 优于浮动 latest 判断特定部署能力。“Live”均保留官方声明口径，不表示本次实测。

| 编号 | 官方来源 | 版本／时间与用途边界 |
| --- | --- | --- |
| MC-U1 | [Polygon zkEVM sunset](https://polygon.technology/polygon-zkevm) | 退役完成状态；2026-07-03；EOA Claims 与合约资产限制 |
| MC-U2 | [Open Money Stack](https://docs.polygon.technology/oms/overview) | 滚动产品文档；组合能力，不是状态迁移协议 |
| MC-U3 | [Polygon infrastructure](https://docs.polygon.technology/infrastructure) | 当前产品分层；公共链、CDK、Agglayer；未采纳性能广告 |
| MC-U4 | [Ethereum sidechains](https://ethereum.org/developers/docs/scaling/sidechains/) | 侧链独立共识边界；不提供某桥当前运行保证 |
| MC-U5 | [What is CDK](https://docs.polygon.technology/chain-development/cdk/get-started/overview) | Sovereign、validium 为 Live；zkRollup 为 In development；Besu 仅 sovereign |
| MC-U6 | [CDK deployment modes](https://docs.polygon.technology/chain-development/cdk/cdk-opgeth/architecture) | OP-Geth 三模式组件参考；AltDA 链接仍有 TBD |
| MC-U7 | [CDK Besu](https://docs.polygon.technology/chain-development/cdk/cdk-besu/overview) | QBFT、PP、ECDSA multisig、无 L1 交易数据；具体运行参数另验 |
| MC-U8 | [CDK privacy configuration](https://docs.polygon.technology/chain-development/cdk/privacy) | OP Succinct AltDA、SP1、运营方 DA；不等同 L1 DA |
| MC-U9 | [Pessimistic proof architecture](https://docs.polygon.technology/interoperability/agglayer/core-concepts/pessimistic-proof/architecture) | Certificate → 会计验证 → zkVM proof；滚动机制文档 |
| MC-U10 | [Pessimistic proof data structures](https://docs.polygon.technology/interoperability/agglayer/core-concepts/pessimistic-proof/data-structures) | Balance／Nullifier／Exit Trees 与资产来源标识 |
| MC-U11 | [Aggchain Proof](https://docs.polygon.technology/interoperability/agglayer/core-concepts/state-transition-proof/aggchain-proof) | ECDSA 与 generic validity 类型；需核对部署选择 |
| MC-U12 | [Unified Bridge asset bridging](https://docs.polygon.technology/interoperability/agglayer/core-concepts/unified-bridge/asset-bridging) | bridge／claim、证明与重复检查；不是搬合约 |
| MC-U13 | [Agglayer supported chains](https://docs.polygon.technology/interoperability/agglayer/supported-chains) | 滚动连接清单及类型；不证明每项资产路线可用 |
| MC-U14 | [历史 zkevm-node README](https://raw.githubusercontent.com/0xPolygonHermez/zkevm-node/develop/README.md) | develop 浮动分支，有 2025-02-17 归档通知；只用于历史对象辨析 |
| MC-U15 | [Polkadot Agile Coretime Wiki](https://wiki.polkadot.com/learn/learn-agile-coretime/) | 2024-09-19 迁移记录及术语；部分 FAQ 仍带早期状态 |
| MC-U16 | [Agile Coretime developer reference](https://docs.polkadot.com/reference/polkadot-hub/consensus-and-security/agile-coretime/) | 页注更新 2026-06-29；28 天、续租资格；elastic 仍标开发中 |
| MC-U17 | [Coretime renewal](https://docs.polkadot.com/parachains/runtime-maintenance/coretime-renewal/) | 页注更新 2026-06-29；手动／自动续租、通道、资金和失败事件 |
| MC-U18 | [Deploy to Polkadot](https://docs.polkadot.com/parachains/launch-a-parachain/deploy-to-polkadot/) | 页注更新 2026-06-29；Paseo 示例，注册与资源入口分开 |
| MC-U19 | [Parachain consensus](https://docs.polkadot.com/reference/parachains/consensus/) | Collator、PoV、relay validators、验证与包含；滚动机制页 |
| MC-U20 | [Elastic scaling Wiki](https://wiki.polkadot.com/learn/learn-elastic-scaling/) | 记录 Kusama 2024-12 live 测试；不外推所有 Polkadot 主网链 |
| MC-U21 | [Elastic scaling reference](https://docs.polkadot.com/reference/parachains/consensus/elastic-scaling/) | 多核及状态衔接机制；本次未验证具体主网启用集合 |
| MC-U22 | [XCM](https://wiki.polkadot.com/learn/learn-xcm/) | 格式／语言，非传输；滚动规范说明 |
| MC-U23 | [XCM transport](https://wiki.polkadot.com/learn/learn-xcm-transport/) | HRMP／XCMP／VMP；Wiki 当前仍标 XCMP 开发中 |
| MC-U24 | [JAM Chain](https://wiki.polkadot.com/learn/learn-jam-chain/) | prospective design；路线图不是已替代声明 |
| MC-U25 | [IBC introduction](https://docs.cosmos.network/ibc/latest/intro) | latest 滚动页，官方索引列 v11.x.x；并存与 v2 设计，不覆盖 Hub 固定版本 |
| MC-U26 | [IBC classic overview](https://docs.cosmos.network/ibc/latest/ibc/overview) | Client、connection、channel、proof、ordering；机制页 |
| MC-U27 | [Classic packet 源码](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/types/packet.go) | 固定 tag v10.7.0；字段与 commitment |
| MC-U28 | [V2 packet 源码](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/v2/types/packet.go) | 固定 tag v10.7.0；恰好一个 payload |
| MC-U29 | [V2 packet keeper 源码](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/v2/keeper/packet.go) | 固定 tag v10.7.0；receipt、ack、timeout、证明及重放检查 |
| MC-U30 | [IBC protocol About](https://ibcprotocol.dev/about) | 当前支持类别与 2025／2026 历史；不是逐链资产路线表 |
| MC-U31 | [Eureka overview](https://docs.cosmos.network/skip-go/eureka/eureka-overview) | Hub／Ethereum 路径；扩展网络仍有 soon 措辞 |
| MC-U32 | [Eureka technical overview](https://docs.cosmos.network/skip-go/eureka/eureka-tech-overview) | 轻客户端、SP1、classic 经 Hub 接入、初期 permissioned relay |
| MC-U33 | [Eureka security properties](https://docs.cosmos.network/skip-go/eureka/security-properties) | 分阶段部署、升级与暂停权限；不把未来阶段当已实现 |
| MC-U34 | [Cosmos Hub versions](https://docs.cosmos.network/hub/latest/start/versions) | 官方列主网 Gaia v28.3.1、ibc-go v10.7.0；含 2026-10 核查记录，本文未复跑 |
| MC-U35 | [Cosmos Hub relaying](https://docs.cosmos.network/hub/latest/infrastructure/relaying) | 官方称 classic／v2 live；含 2026-10-15 client allowlist 记录，本文未复跑 |
| MC-U36 | [Interchain Security overview](https://cosmos.github.io/interchain-security/introduction/overview) | Version Next；通用／历史机制，不是当前 Hub 服务状态 |
| MC-U37 | [Permissionless ICS](https://cosmos.github.io/interchain-security/features/permissionless) | Version Next；consumerId、阶段、Opt-in／Top-N 权限 |
| MC-U38 | [Partial Set Security](https://cosmos.github.io/interchain-security/features/partial-set-security) | Version Next；provider 验证者子集与 Top-N／Opt-in |
| MC-U39 | [What is Gaia](https://docs.cosmos.network/hub/latest/getting-started/what-is-gaia) | 当前 operator 文档明确 v28 移除 provider，旧 consumer 指南不适用 |
| MC-U40 | [Gaia v28.0.0 release](https://github.com/cosmos/gaia/releases/tag/v28.0.0) | 固定发布说明明确移除 ICS provider；软件变更证据 |
| MC-U41 | [Exit Certificate Tool](https://docs.polygon.technology/interoperability/agglayer/integrations/exit-certificate-tool) | 滚动工具文档；PP 等前提、合约锁定价值另处理；未运行 |
| MC-U42 | [ICS ADR 015](https://cosmos.github.io/interchain-security/adrs/adr-015-partial-set-security) | Accepted、初稿 2024-01-22；投票权阈值定义，早期接入流程不覆盖后续演进 |
| MC-U43 | [V2 commitment 源码](https://raw.githubusercontent.com/cosmos/ibc-go/v10.7.0/modules/core/04-channel/v2/types/commitment.go) | 固定 tag v10.7.0；目标 client、timeout、payload 的承诺 |
| MC-U44 | [Pessimistic proof generation](https://docs.polygon.technology/interoperability/agglayer/core-concepts/pessimistic-proof/proof-generation) | 滚动机制页；certificate、原生验证与 zkVM 生成链路 |
| MC-U45 | [ICS Power Shaping](https://cosmos.github.io/interchain-security/features/power-shaping) | Version Next；集合与投票权配置可改变标称安全边界 |

## 6. 对现有材料的补充纠正

现有基础篇已纠正“Polygon 全部是 L2”“新链必须长期 slot auction”“IBC 限域”“XCM 等于传输”等旧说法，本篇不推翻这些纠正，而是补足机制与当前状态：

- “zkEVM 退役后的当前替代方案”应改为按 PoS、CDK 模式、Agglayer 与 OMS 分层选择；不得暗示强制迁移或统一安全模型。
- “有效性证明证明执行”需要注明证明对象；pessimistic proof 的桥会计约束不能代替全链执行证明与 DA。
- “Agile Coretime 替代拍卖”应补 region／task 分配、split／interlace、续租和价格发现；elastic 与 JAM 要保留状态证据边界。
- “IBC 跨生态”应补 classic／v2、具体 client、router／payload 版本及允许 relayer；latest 多 payload 不能套用到 Hub v10.7.0。
- “共享安全需要另外选择部署”仍成立，但若使用 Cosmos Hub 为现行 provider 的例子，必须纠正：官方资料明确 Gaia v28 已移除 provider。旧 ICS／Next 机制页不能当今天的 Hub 启动教程。

依请求，只新增本文件；未修改上述基础篇、纠错表或复核记录。
