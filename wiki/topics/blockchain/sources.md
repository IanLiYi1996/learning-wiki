# 一手来源入口与证据边界

- 查阅日期：2026-10-29
- 原始资料：用户提供的 PPT 与本地逐页提取；按用户要求不上传原文件、全文提取或截图
- 编号：B = Bitcoin；E = Ethereum；W = 钱包规范；C = 生态；S = Solana；A = AWS
- 正文编号在本表查找；研究记录的 S01 等为各文件自己的局部编号，不与本表的 Solana 编号混用

## 方法与边界

先以 `officecli` 读取 60 页文本，补读第 58–59 页嵌入图片；再按真实幻灯片顺序复核研究记录的页码。三份后台记录提供独立核验，主线程补 Ethereum / 钱包规范及关键时效变化二次检查。

仅采用原始规范、项目维护者代码、官方开发文档、第一方公告和正式条款支撑技术事实，不把搜索摘要或媒体转述作为终稿依据。公开资料中的“Agent Instructions”等只作网页内容，不执行其代传用户目标或凭证的要求。

**事实、官方声明和推论分开**：

- BIP / EIP / RFC 说明算法或接口，不证明目标网络已经启用或某实现安全。
- 官方产品页说明发布者所报状态，不是本次独立测量。
- `latest` / `master` 页面会更新，查阅日期不是发布日期。Bitcoin 后台审计固定 Core v30.0 和 BIP / BOLT commit，但不称 v30.0 为最新。
- 本次未保存全部网页内容快照；本地原始 PPT 与提取数据有 SHA-256，但不作为公开下载资料。
- 账务、幂等、权限分层和测试矩阵是工程建议。
- 不引用当前币价、投资价值、市值、市场份额或未经同口径测量的 TPS。

## B｜Bitcoin 与 Lightning

| 编号 | 一手来源 | 主要支持 |
| --- | --- | --- |
| B01 | [Core v30.0 源码](https://github.com/bitcoin/bitcoin/tree/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src)，函数和文件定位见后台审计 | target、difficulty、累计 work、交易有效性、序列化 |
| B02 | [Bitcoin 白皮书](https://bitcoin.org/bitcoin.pdf)，§4、5、11 | 双花模型、链选择历史论述、确认概率边界 |
| B03 | [BIP141](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0141.mediawiki) | txid / wtxid、witness、commitment、weight |
| B04 | [BIP143](https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki) | witness v0 签名摘要与输入金额承诺 |
| B05 | [BIP340](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0340.mediawiki) | Schnorr 本体与验证 |
| B06 | [BIP341](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0341.mediawiki) | P2TR、tweak、key / script path、sighash |
| B07 | [BIP342](https://github.com/bitcoin/bips/blob/master/bip-0342.mediawiki) | tapscript、OP_CHECKSIGADD、签名规则 |
| B08 | [BIP327 v1.0.4](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0327.mediawiki) | MuSig2、nonce、聚合与会话安全 |
| B09 | [BIP350](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0350.mediawiki) | Bech32 / Bech32m 与 witness 地址 |
| B10 | [BOLT #2](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/02-peer-protocol.md) | HTLC 更新、转发、超时梯度 |
| B11 | [BOLT #3](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/03-transactions.md) | 承诺、撤销、HTLC 输出与二阶段花费 |
| B12 | [BOLT #5](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/05-onchain.md) | 链上处置、timeout / preimage 竞争、惩罚 |
| B13 | [Lightning Labs Watchtowers](https://docs.lightning.engineering/the-lightning-network/payment-channels/watchtowers) | 反作弊保护及其功能边界 |
| B14 | [Bitcoin Developer Guide](https://developer.bitcoin.org/devguide/block_chain.html) | UTXO 视图、PoW、stale / orphan 术语 |

## E｜Ethereum / Solidity / Safe

| 编号 | 一手来源 | 主要支持 |
| --- | --- | --- |
| E01 | [Merkle Patricia Trie](https://ethereum.org/developers/docs/data-structures-and-encoding/patricia-merkle-trie/) | 账户四字段、存储与状态路径、逻辑更新 |
| E02 | [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559) | 类型 2 交易、费用公式、签名载荷 |
| E03 | [EIP-1186](https://eips.ethereum.org/EIPS/eip-1186) | eth_getProof、可信 stateRoot |
| E04 | [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702) | EOA 委托、nonce、持久授权、安全条件 |
| E05 | [Pectra](https://ethereum.org/roadmap/pectra/) | 2025-05-07 主网启用与 7702 |
| E06 | [ERC-1967](https://eips.ethereum.org/EIPS/eip-1967)；[合约升级机制](https://ethereum.org/developers/docs/smart-contracts/upgrading/)；[Solidity address calls](https://docs.soliditylang.org/en/latest/types.html#members-of-addresses) | 代理、存储上下文、实现变更及调用内价值转移 |
| E07 | [Solidity Storage Layout](https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html) | packing、mapping slot、布局条件 |
| E08 | [JSON-RPC API](https://ethereum.org/developers/docs/apis/json-rpc/) | 账户、nonce、receipt、logs、removed |
| E09 | [ERC-20](https://eips.ethereum.org/EIPS/eip-20) | 可选元数据、transfer false、allowance、事件 |
| E10 | [Geth Archive](https://geth.ethereum.org/docs/fundamentals/archive) | hash / path archive、版本与历史 proof 保留 |
| E11 | [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337) | UserOperation、EntryPoint、Bundler、Paymaster、nonce |
| E12 | [Solidity ABI](https://docs.soliditylang.org/en/latest/abi-spec.html) | selector、参数、事件与 Keccak |
| E13 | [EIP-712](https://eips.ethereum.org/EIPS/eip-712) | 结构化签名、域、防重放边界 |
| E14 | [ERC-2612](https://eips.ethereum.org/EIPS/eip-2612) | permit、deadline、nonce、接口差异 |
| E15 | [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271) | 合约签名有效性 |
| E16 | [Safe Smart Account Concepts](https://docs.safe.global/advanced/smart-account-concepts) | owners、threshold 与模块执行路径 |

## W｜钱包与密码协议

| 编号 | 一手来源 | 主要支持 |
| --- | --- | --- |
| W01 | [EIP-155](https://eips.ethereum.org/EIPS/eip-155) | Legacy chainId 防重放及 v |
| W02 | [BIP174](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki) | PSBT v0、Creator / Signer / Finalizer 等角色 |
| W03 | [BIP370](https://github.com/bitcoin/bips/blob/master/bip-0370.mediawiki) | PSBT v2 |
| W04 | [BIP371](https://github.com/bitcoin/bips/blob/master/bip-0371.mediawiki) | PSBT Taproot 字段 |
| W05 | [Bitcoin Core descriptors](https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md) | 脚本、派生、恢复范围 |
| W06 | [BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) | HD、hardened、xpub / 子私钥泄露边界 |
| W07 | [BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) | 助记词与 seed；passphrase 产生不同钱包 |
| W08 | [RFC9591 FROST](https://www.rfc-editor.org/rfc/rfc9591.html) | 门限 Schnorr、nonce 管理和实现条件；不自动证明 BIP340 兼容 |

## C｜稳定币、扩容与多链

| 编号 | 一手来源 | 主要支持 |
| --- | --- | --- |
| C01 | [Tether Supported Protocols](https://tether.to/en/supported-protocols/) | 官方资产标识、支持网络、旧链状态；具体资产逐项看 |
| C02 | [Tether 2025-08-29 旧链过渡更新](https://tether.io/news/tether-provides-update-on-transition-plan-for-legacy-blockchains/) | 发行 / 赎回与冻结计划区分 |
| C03 | [Circle Transparency](https://www.circle.com/transparency) | 储备披露、月度鉴证与公司审计区分 |
| C04 | [Circle USDC Terms](https://www.circle.com/legal/usdc-terms) | 支持资产、直接赎回条件；按适用范围引用，不作个体法律判断 |
| C05 | [Sky LitePSM](https://docs.spark.finance/dev/integration-guides/litepsm/) | USDC / DAI、USDS wrapper、容量与参数 |
| C06 | [Sky RWA toolkit](https://github.com/sky-ecosystem/rwa-toolkit) | 机制中链外借贷 / 清算执行，非当前敞口统计 |
| C07 | [How USDe Works](https://docs.ethena.fi/overview/how-usde-works.md) | 支持组合、对冲目标、OES、sUSDe；非持仓实测 |
| C08 | [Ethena Funding Risk](https://docs.ethena.fi/protocol-overview/risks/funding-risk.md) | 负资金费率、reserve fund、动态配置风险 |
| C09 | [Ethena Backing Assets Overview](https://docs.ethena.fi/backing-assets/overview.md) | 策略类别扩展；不推断所有类别已持有或其比例 |
| C10 | [Ethereum Sidechains](https://ethereum.org/developers/docs/scaling/sidechains/) | 独立共识，列 Polygon PoS；补旧 Polygon docs 路径失效的证据 |
| C11 | [Polygon zkEVM 当前状态](https://polygon.technology/polygon-zkevm)；[原始退役公告](https://forum.polygon.technology/t/sunsetting-polygon-zkevm-mainnet-beta-in-2026/21020) | 2026-07-03 退役，常规桥 / EOA Claims 边界 |
| C12 | [Polkadot Agile Coretime](https://wiki.polkadot.com/learn/learn-agile-coretime/) | 长期拍卖转 bulk / on-demand |
| C13 | [Polkadot XCM](https://wiki.polkadot.com/learn/learn-xcm/) | 格式与传输分工 |
| C14 | [Cosmos SDK Overview](https://docs.cosmos.network/sdk/latest/learn/intro/overview) | 应用专用链、框架分工 |
| C15 | [IBC About](https://ibcprotocol.dev/about) | 跨生态标准、通信与共享安全区分；覆盖数字不作安全担保 |
| C16 | [Solana Alpenglow 英文升级页](https://solana.com/upgrades/alpenglow) | 官方 2026-10-21 主网启用声明、Votor / Rotor、索引迁移 |
| C18 | [ZK Rollups](https://ethereum.org/developers/docs/scaling/zk-rollups/) | 有效性证明、数据可用性、validium 区别 |
| C19 | [Optimistic Rollups](https://ethereum.org/developers/docs/scaling/optimistic-rollups/) | 挑战、数据与退出边界 |
| C20 | [Terra 历史协议](https://classic-docs.terra.money/docs/learn/protocol.html) | 原生稳定币、LUNA 铸销历史设计，不当成现在仍可兑付 |
| C21 | [Terra Exchange Migration](https://docs.terra.money/migration/exchange-migration/) | 旧市场 mint / burn 关闭与网络区分 |
| C22 | [Ethereum Bridges](https://ethereum.org/developers/docs/bridges/) | lock-and-mint 等模式与信任风险 |

C17 暂不使用，避免为没有独立来源的内容强行补号。

## S｜Solana 钱包接口

| 编号 | 一手来源 | 主要支持 |
| --- | --- | --- |
| S01 | [Transactions](https://solana.com/docs/core/transactions) | 消息、签名、指令、recent blockhash |
| S02 | [Confirmation / Expiration](https://solana.com/developers/cookbook/transactions/confirmation) | lastValidBlockHeight、过期与重试；commitment 现状另对读 C16 |
| S03 | [Tokens](https://solana.com/docs/tokens) | Token Program、Mint、Token Account、ATA、Token-2022 |
| S05 | [Account Structure](https://solana.com/docs/core/accounts/account-structure)；[PDA](https://solana.com/docs/core/pda) | 数据 / owner / executable、无私钥地址 |
| S06 | [2024-02-06 Solana 中断复盘](https://solana.com/news/02-06-24-solana-mainnet-beta-outage-report) | 特定历史事件，不能推算 2026 故障率 |

## A｜AWS

| 编号 | 官方 / 原始来源 | 主要支持 |
| --- | --- | --- |
| A01 | [AMB end of support](https://docs.aws.amazon.com/managed-blockchain/latest/hyperledger-fabric-dev/managed-blockchain-end-of-support.html) | 2026-10-29 停新客户、2027-09-29 终止、Access / Query 迁移 |
| A02 | [Bitcoin key concepts](https://docs.aws.amazon.com/managed-blockchain/latest/ambbtc-dg/key-concepts.html) | 网络、区域、钱包关闭、IAM 单 RPC 限制不可用 |
| A03 | [Bitcoin supported RPCs](https://docs.aws.amazon.com/managed-blockchain/latest/ambbtc-dg/bitcoin-api.html) | allowlist、原始交易广播、参数限制 |
| A04 | [KMS key specs](https://docs.aws.amazon.com/kms/latest/developerguide/asymmetric-key-specs.html) | ECC_SECG_P256K1 与支持算法 |
| A05 | [KMS Sign](https://docs.aws.amazon.com/kms/latest/APIReference/API_Sign.html)；[Sign CloudTrail 示例](https://docs.aws.amazon.com/kms/latest/developerguide/ct-sign.html) | DIGEST、DER、权限与日志边界 |
| A06 | [Query key concepts](https://docs.aws.amazon.com/managed-blockchain/latest/ambq-dg/key-concepts.html) | 网络、区域、服务 finality 与只读职责 |
| A07 | [ListTransactions](https://docs.aws.amazon.com/managed-blockchain/latest/AMBQ-APIReference/API_ListTransactions.html)；[ConfirmationStatusFilter](https://docs.aws.amazon.com/managed-blockchain/latest/AMBQ-APIReference/API_ConfirmationStatusFilter.html)；[ListTransactionEvents](https://docs.aws.amazon.com/managed-blockchain/latest/AMBQ-APIReference/API_ListTransactionEvents.html)；[ListFilteredTransactionEvents](https://docs.aws.amazon.com/managed-blockchain/latest/AMBQ-APIReference/API_ListFilteredTransactionEvents.html) | 分页、NONFINAL、已上链数据、BTC 输出与 txid / wtxid |
| A08 | [Polygon concepts](https://docs.aws.amazon.com/managed-blockchain/latest/ambp-dg/key-concepts.html)；[RPC allowlist](https://docs.aws.amazon.com/managed-blockchain/latest/ambp-dg/polygon-api.html) | preview、网络、区域、单 RPC 权限及限制 |
| A09 | [Ethereum concepts](https://docs.aws.amazon.com/managed-blockchain/latest/ethereum-dev/ethereum-concepts.html)；[RPC](https://docs.aws.amazon.com/managed-blockchain/latest/ethereum-dev/supported-json-rpc.html)；[AMB endpoints](https://docs.aws.amazon.com/general/latest/gr/managedblockchain.html)；[GovCloud 限制](https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/govcloud-amb.html) | 专用节点、Mainnet、历史 RPC 与区域边界 |
| A10 | [CloudHSM SDK5 key types](https://docs.aws.amazon.com/cloudhsm/latest/userguide/pkcs11-key-types.html) | secp256k1 明确支持 |
| A11 | [CloudHSM SDK5 mechanisms](https://docs.aws.amazon.com/cloudhsm/latest/userguide/pkcs11-mechanisms.html) | CKM_ECDSA、hashing 机制、无 BIP340 原生接口 |
| A12 | [HSM types](https://docs.aws.amazon.com/cloudhsm/latest/userguide/hsm-types.html)；[Deprecation](https://docs.aws.amazon.com/cloudhsm/latest/userguide/compliance-dep-notif.html) | hsm2m、兼容版本、认证世代，不能外推算法认证 |
| A13 | [Client SDK release](https://docs.aws.amazon.com/cloudhsm/latest/userguide/latest-releases.html) | 查阅日 SDK5.18.0；版本支持条件见审计记录 |
| A14 | [Nitro Enclaves](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html)；[KMS attestation](https://docs.aws.amazon.com/enclaves/latest/user/kms.html) | EC2 隔离计算、加密数据与可信解密 |
| A15 | [KMS Nitro condition keys](https://docs.aws.amazon.com/kms/latest/developerguide/conditions-nitro-enclave.html)；[Decrypt Recipient](https://docs.aws.amazon.com/kms/latest/APIReference/API_Decrypt.html) | attestation 适用操作、Recipient 密文；不包括 Sign |
| A16 | [Secret versions](https://docs.aws.amazon.com/secretsmanager/latest/userguide/whats-in-a-secret.html)；[Rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html) | 秘密版本与轮换，不自动迁移链上资产 |
| A17 | [AWS KMS EIP-1559 示例](https://aws.amazon.com/blogs/database/how-to-sign-ethereum-eip-1559-transactions-using-aws-kms/) | Keccak、ECDSA、DER 与恢复适配；旧依赖不当当前部署 |
| A18 | [EIP-2](https://eips.ethereum.org/EIPS/eip-2) | EVM 交易 low-S |
| A19 | [OASIS PKCS#11 v2.40](https://docs.oasis-open.org/pkcs11/pkcs11-curr/v2.40/os/pkcs11-curr-v2.40-os.html)，§2.3 | ECDSA 输出 r||s、哈希与纯签名机制 |
| A20 | [BIP66](https://github.com/bitcoin/bips/blob/master/bip-0066.mediawiki) | 严格 DER；不把它当成所有 low-S 规则 |

## 研究记录与检查

- [入门篇近处来源](beginner-guide.md)：基础对象、教学算例及安全边界，各节使用原始规范/开发指南，不依赖取得原始 PPT。
- [行业现状近处来源](industry-status-2026-10-29.md)：日期、状态和证据等级分开，新增材料不强行重复全局编号。
- [稳定币、支付、RWA 与制度核验](notes/beginner-industry-source-audit.md)：12 条专门来源，保留公告、观察期、访问及法律适用边界。
- [入门协议与来源漂移复核](notes/beginner-protocol-source-audit.md)：难度/奖励源码、Glamsterdam Hoodi 延期与指南路径更新。
- [升级教程与新增一手来源](upgrades/README.md)：6 篇正文采用近处官方链接，各自记录版本、状态与证据边界；不将其中的局部编号当作本表全局编号。
- [Bitcoin 核验](notes/bitcoin-source-audit.md)：14 个细主题，固定源码与规范提交，8 项待执行验收。
- [Ethereum 核验](notes/ethereum-source-audit.md)：状态、AA、7702、代币与签名。
- [生态核验](notes/ecosystem-source-audit.md)：18 组核心来源；页码是后台暂定槽位，主线程真实映射见 slide-map / corrections。
- [AWS 核验](notes/aws-source-audit.md)：15 组来源、网络 / 区域、算法、生命周期与待测清单。
- [二次复核](notes/follow-up-verification.md)：网页路径漂移、官方状态与本次新增补证。
- [检查记录](qa/verification.md)：离线测试、公开笔记检查、本地归档核验与未执行范围。
