# AWS 托管钱包：官方来源核验与工程边界

- 核验 / snapshot 日期：2026-10-29（UTC）。
- 类型：PPT p55–59 的来源审计；状态：文档核验完成，部署与交易验收未执行。
- 方法：完整读取 research skill；通过 `web.run` 核验 AWS 官方文档与第一方说明，并只读获取官方 Markdown / 协议原始文本交叉检查。部分 GitHub / 规范长页的浏览抓取受限时，用同一权威发布者的原始文本补核，不引用第三方解释。按本仓库笔记惯例归为 15 组一手来源，组内列出实际核验章节。当前未提供后台子代理工具，因此本次由主代理完成。
- 范围：只读公共资料与本地 PPT 提取文本 / p58–59 图片；未调用真实 AWS 资源，未创建密钥、节点、集群或交易，未执行广播。没有成本报价或法律判断。
- 快照含义：记录本日读到的文档结论，不是运行态测量，也不是网页全文归档。AWS `latest`、GitHub `master` 是可变入口；本次未取得不可变的文档 revision / source commit，不能把访问日伪装为产品发布日期。

## 先给结论

AWS 的密钥保管、签名、隔离计算与链访问组件可以组成钱包基础设施，但不是开箱即用的完整托管钱包。PPT 的节点接入 / 外部签名职责分离基本正确；完整钱包仍须实现交易构造、审批、UTXO / nonce 并发、重组回滚、账务与恢复。[S02–S15]

最重要的时效修订：AWS 已公告 AMB 自 **2026-10-29 起不再接受新客户**；现有客户可继续使用至 **2027-09-29**，之后不能访问 AMB 功能。公告明确覆盖 Access Ethereum / Bitcoin / Polygon、Query 与 Fabric。因而不能在今天把“新客户采用 AMB”写成可持续的新建方案；现有客户也必须规划迁移。[S01]

PPT p55“本项目 BTC 即走此路”、p56“实际调用验证结果 / 已云上跑通”，以及 p58–59 的流程图，只是原作者陈述。本审计没有该项目的账号、部署记录、请求响应、交易 ID、CloudTrail 或测试报告，**不承认其为我们的实测，更不据此声明安全验收通过**。

## p55–56：当前 network / Region 支持矩阵

以下均为本日官方文档支持范围，且受 S01 生命周期限制；“服务存在端点”不等于账号已获服务资格或具体链可创建。

| 服务 | 模式 / 当前明确列出的网络 | Region | 核验结论 |
| --- | --- | --- | --- |
| AMB Access Bitcoin | Serverless；Mainnet、Testnet | `us-east-1`、`ap-northeast-1`、`ap-northeast-2`、`ap-southeast-1`、`eu-west-1`、`eu-west-2` | Core 全节点钱包功能关闭；不支持私链、挖矿。AWS 文档只称 Testnet，未在所核章节说明 testnet3 / testnet4，不能自行升级命名。[S02] |
| AMB Access Ethereum | 创建专用托管节点；当前支持列表只有 Mainnet | 同上 6 个商业 Region，依据 Ethereum 专属 GA 公告与当前区域端点表交叉核对 | Ropsten、Rinkeby、Goerli 已停止支持；文档建议使用 Sepolia / Holesky 做测试，不构成 AMB Access 支持这些网络的证据。Sepolia 是 Query 的明确支持项。[S05–S06] |
| AMB Access Polygon | Serverless，文档仍标 **preview**；只明确列 Mainnet | 仅 `us-east-1` | Mumbai 支持已于 2024-04-15 结束；建议 Amoy 不是已列出 Amoy 服务端点。没有 Polygon zkEVM / 私链 / validator staking 支持。[S04] |
| AMB Query | BTC Mainnet / Testnet；ETH Mainnet / Sepolia | 仅 `us-east-1` | API 枚举：`BITCOIN_MAINNET`、`BITCOIN_TESTNET`、`ETHEREUM_MAINNET`、`ETHEREUM_SEPOLIA_TESTNET`；没有 Polygon。[S06–S07] |

Region 证据边界：通用 AMB 区域表还列 `us-gov-west-1`，但 GovCloud 官方文档明确该区域只支持 Fabric，不能据此添加 Ethereum / BTC / Polygon。Ethereum 专属 Region 公告发布日期为 2021-03-02；其网络示例已过时，因此本表仅用它确认链专属 Region，再用当前概念文档确认网络，不沿用旧测试网。[S05]

端点形态（仅标识配置，不是本次调用记录）：

```text
BTC：mainnet.bitcoin.managedblockchain.<Region>.amazonaws.com
     testnet.bitcoin.managedblockchain.<Region>.amazonaws.com
Polygon：mainnet.polygon.managedblockchain.us-east-1.amazonaws.com
Query：managedblockchain-query.us-east-1.amazonaws.com
Ethereum：每个节点分别提供 HTTP / WebSocket 端点
```

上述形态来自对应服务文档；不要把控制面 `managedblockchain.<Region>` 当作各链数据面 RPC，也不要把 Query 的 `us-east-1` 端点改 Region 后推定可用。[S02、S04–S06]

## 15 组官方 / 原始来源审计

下列 S01–S15 均在 2026-10-29 核验。每组的链接、结论、版本条件与 PPT 页码一起保留；跨页推导在正文明确说明。AWS 文档负责证明产品能力，BIP / EIP / OASIS 负责证明协议要求，二者不能互相替代。

### S01 — AMB 生命周期：改变新建可行性

- 链接：[AWS AMB end of support](https://docs.aws.amazon.com/managed-blockchain/latest/hyperledger-fabric-dev/managed-blockchain-end-of-support.html)。
- 核验结论：停止接纳新客户日为 2026-10-29；现有客户的服务截止日为 2027-09-29。官方给出自管节点 / 第三方 RPC 与索引服务的迁移方向，Query 迁移不是仅替换端点，须转换数据模型与分页。
- 版本 / 条件：当前官方服务级公告；不是 Fabric 独有的退役公告，虽 URL 位于 Fabric 文档目录。账号是否属于现有客户本次未检查；公告未给可自行推定的当日具体时刻。
- PPT：p55–56、p58–59 均须加生命周期脚注。**设计建议**：新客户以替代 RPC / 自管索引为候选；现有客户把 AMB 作为过渡依赖。

### S02 — BTC Access：Serverless，但不是节点钱包

- 链接：[Bitcoin key concepts](https://docs.aws.amazon.com/managed-blockchain/latest/ambbtc-dg/key-concepts.html)。
- 核验结论：支持 Mainnet / Testnet、6 个 Region；钱包功能关闭，地址与资金内容由客户管理。提供 HTTPS / SigV4；文档明确 **不能用 IAM 限制单个 Bitcoin JSON-RPC 方法**。无私链、挖矿支持。
- 版本 / 条件：AMB Access Bitcoin `latest`；不能从文档推定底层 Core 精确版本、testnet 代际或所有 Core 方法均开放。Serverless 只免节点 provisioning，不免钱包逻辑。
- PPT：p55–56、p58–59。**设计建议**：scanner 与 broadcaster 在自有 RPC 网关分别设方法白名单，不能只靠同一 AMB IAM 权限完成读写分离。

### S03 — BTC supported methods 与广播边界

- 链接：[Supported Bitcoin JSON-RPCs](https://docs.aws.amazon.com/managed-blockchain/latest/ambbtc-dg/bitcoin-api.html)。
- 核验结论：列表覆盖区块 / 链状态、mempool、原始交易、工具方法。钱包相关可用例：`getblockhash`、`getblock`、`gettxout`、`getrawtransaction`、`estimatesmartfee`、`testmempoolaccept`、`sendrawtransaction`。`createrawtransaction` 也在列表，表示构造未签名交易，不表示节点持有私钥。
- 版本 / 条件：只能依该 allowlist；不能承诺 `getbalance`、`listunspent`、`importprivkey`、`walletpassphrase`、`signrawtransactionwithwallet` 等节点钱包能力。`getrawmempool(verbose=true)` 不支持；HTTP 响应超过 10 MB 须按文档使用 gzip；默认每网络 / Region 100 RPS，不应写成无限吞吐。
- PPT：p55–56、p58–59。“扫块”可由区块 RPC 实现；RPC 提交返回不是入块或终局证明。**设计建议**：持久化已签原始交易，重试同一 payload；记录拒绝 / 超时 / 已提交状态，再独立观察上链，不把 `testmempoolaccept` 当作保留 UTXO 或确认承诺。

### S04 — Polygon：preview / 主网与方法限制

- 链接：[Polygon key concepts](https://docs.aws.amazon.com/managed-blockchain/latest/ambp-dg/key-concepts.html)；[Polygon supported RPCs](https://docs.aws.amazon.com/managed-blockchain/latest/ambp-dg/polygon-api.html)。
- 核验结论：Serverless 主网，仅 `us-east-1`，仍为 preview；只广播外部已签 raw transaction，方法名按列表为 `eth_sendRawTransaction`。未列方法不支持，不能假定有 `eth_sendTransaction`、`eth_sign` 或 `personal_*`。
- 版本 / 条件：preview 不支持 JSON-RPC batch；`eth_getLogs` 有合约地址时默认最多 1K 区块，高活跃合约可能更小，无合约地址仅 8 区块；方法级配额不同，广播默认 10 RPS。可用 SigV4 或 Accessor billing token，不能混用；IAM 不能限制单个 Polygon RPC。Mumbai 已退出，不据 Amoy 建议虚构支持项。
- PPT：p55–56。支持 `eth_getBlockByNumber`、receipt / logs 等，不等于免费获得钱包索引、HD 密钥或 AMB Query Polygon 数据。

### S05 — Ethereum：专用节点、Mainnet 与历史数据限制

- 链接：[Ethereum key concepts](https://docs.aws.amazon.com/managed-blockchain/latest/ethereum-dev/ethereum-concepts.html)；[Ethereum supported RPCs](https://docs.aws.amazon.com/managed-blockchain/latest/ethereum-dev/supported-json-rpc.html)；[Ethereum GA / Region 公告，2021-03-02](https://aws.amazon.com/about-aws/whats-new/2021/03/announcing-general-availability-of-ethereum-on-amazon-managed-blockchain/)；[当前 AMB endpoints](https://docs.aws.amazon.com/general/latest/gr/managedblockchain.html)；[GovCloud AMB 限制](https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/govcloud-amb.html)。
- 核验结论：创建节点接入当前明确支持的 Mainnet；6 个商业 Region，GovCloud 仅 Fabric。raw transaction 在外部签名后通过 `eth_sendRawTransaction` 提交，不是以太坊钱包或 staking validator。
- 版本 / 条件：不支持 batch；WebSocket payload 512 KB；大于 5.9 MB 的 HTTP 响应须用文档指定压缩头。历史状态类调用（如 balance / call / code / storage）及若干 trace 方法只覆盖最近 128 blocks；不要把它解释为全部区块读取均只有 128 块，也不要宣称全量 archive node。过滤器可能随节点替换消失；订阅与连接绑定。
- PPT：p55–56。Query 的标准化历史数据并不等于任意历史 EVM storage、call 或 trace 的 archive RPC 替代品。确切 Geth / 共识客户端运行版本、本账号节点状态均未实测。

### S06 — Query：network / finality / 只读职责

- 链接：[Query key concepts](https://docs.aws.amazon.com/managed-blockchain/latest/ambq-dg/key-concepts.html)。
- 核验结论：4 个网络，仅 `us-east-1`；SigV4 的标准化历史 / 余额 / 事件查询，不提供交易构造、私钥签名或 outgoing 广播。所谓“不能扫块”应解释为不提供 Access 式逐块 JSON-RPC；仍能分页查询索引历史，不是不能分析链数据。
- 版本 / 条件：Query 自身规则为 BTC Mainnet 6 blocks；BTC Testnet 6 blocks **或 60 分钟，先到者**；ETH 支持网络 64 blocks。余额 / 合约 API 只返回达到 finality 的数据，交易 / 事件 API 可返回已上链但尚未 final 的数据。这是服务判定规则，不是可替代业务风控的永久不重组保证。
- PPT：p55–56、p58–59。所核章节没有提供数值化索引延迟 SLA；不能把“实时查询”写成 0 延迟、固定几秒可见或等同链头。访问日期不是链数据索引截止日期。

### S07 — Query：NONFINAL、pagination、outgoing 与 UTXO 边界

- 链接：[ListTransactions](https://docs.aws.amazon.com/managed-blockchain/latest/AMBQ-APIReference/API_ListTransactions.html)；[ConfirmationStatusFilter](https://docs.aws.amazon.com/managed-blockchain/latest/AMBQ-APIReference/API_ConfirmationStatusFilter.html)；[GetTransaction](https://docs.aws.amazon.com/managed-blockchain/latest/AMBQ-APIReference/API_GetTransaction.html)；[ListTransactionEvents](https://docs.aws.amazon.com/managed-blockchain/latest/AMBQ-APIReference/API_ListTransactionEvents.html)；[ListFilteredTransactionEvents](https://docs.aws.amazon.com/managed-blockchain/latest/AMBQ-APIReference/API_ListFilteredTransactionEvents.html)；[GetTokenBalance](https://docs.aws.amazon.com/managed-blockchain/latest/AMBQ-APIReference/API_GetTokenBalance.html)。
- 核验结论：NONFINAL 是 **链上已确认、尚未达 Query finality**，不是 mempool。List 的 `confirmationStatusFilter.include` 可加入 NONFINAL，但 FINAL 仍包含，不能当作“只取 NONFINAL”。GetTransaction / ListTransactionEvents 可直接返回未 final 的已确认交易。
- 版本 / 条件：上述列表 API 默认 `maxResults=100`、范围 1–250；少于上限乃至空数组都可能仍有下一页。必须追随 `nextToken`，直到无下一 token，不能按数组长度停止。时间过滤与排序不自动证明数据库式一致性 snapshot；本次未找到跨分页链状态冻结承诺。
- PPT：p55–56、p58–59。Query 可以追踪 **已上链 outgoing 交易**，但不能创建 / 广播它，也不能证明未索引交易没发出。BTC filtered events API 仅支持 Bitcoin，提供 `transactionEventToAddress`、`voutSpent` 等输出筛选；**推论**：它不是钱包 input 选择、mempool 冲突锁或完整 outgoing ledger。需自有 UTXO / 提币状态机，不能把“某地址有未花输出”当作马上可支用。
- 补充：BTC API 的 `transactionId` 是不含 witness 的 txid，`transactionHash` 是含 witness 的 wtxid；二者须分别保存。余额响应中的 `atBlockchainInstant` / `lastUpdatedTime` 不应自行解释为全链索引 watermark。[S06]

### S08 — KMS secp256k1 / Sign：digest 不再哈希、输出 DER

- 链接：[KMS Key spec reference](https://docs.aws.amazon.com/kms/latest/developerguide/asymmetric-key-specs.html)；[KMS Sign API](https://docs.aws.amazon.com/kms/latest/APIReference/API_Sign.html)。
- 核验结论：`ECC_SECG_P256K1` 对应 secp256k1；签名配置为 `SIGN_VERIFY` + `ECDSA_SHA_256`。对于该 ECDSA 算法，`MessageType=DIGEST` 跳过哈希，输入为 32 字节摘要；用 RAW 或遗漏 MessageType 会再次哈希，导致链上摘要不匹配。HTTP JSON 使用 Base64 blob，SDK binary 不应重复 Base64。
- 版本 / 条件：Sign 的 ECDSA 输出是 ASN.1 DER `(r,s)`，不是 Bitcoin 最终 witness，也不是 EVM `r,s,yParity`。私钥不以明文离开 KMS；不等于任意导入密钥从未曾出现在外部。不同算法的 DIGEST 行为不能一概类推，当前文档的 Ed25519ph 特例不适用于此 ECDSA 配置。
- PPT：p57–58；EVM 是扩展核验。KMS 的公开 Sign / key-spec 接口未提供 BIP340 Schnorr 或 BIP32 CKD / xprv 派生；ECDH 也不是 BIP32，且 secp256k1 不属于其 key-agreement 支持项。先在外部派生再导入子密钥不等于“私钥在 KMS 内完成 HD 派生”，并改变密钥暴露边界。[S09]

### S09 — Bitcoin 原始规范：sighash、DER / hashtype / low-S、Taproot、HD

- 链接：[BIP66](https://github.com/bitcoin/bips/blob/master/bip-0066.mediawiki)；[BIP143](https://github.com/bitcoin/bips/blob/master/bip-0143.mediawiki)；[BIP340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki)；[BIP341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki)；[BIP32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)。
- 核验结论：legacy 与 SegWit v0 按各自输入 / script / hashtype 计算摘要，不是拿整笔 raw transaction 的 txid 当 sighash。BIP143 是双 SHA256，覆盖待花输出金额；ECDSA 验签项为严格 DER 加末尾 1-byte hashtype，该字节不在 DER 内。low-S 使用 `s' = min(s, n-s)`；BIP340 对既有 Bitcoin ECDSA low-S 的说明是网络 policy，不能误写成 BIP66 新增的所有脚本共识规则。
- 版本 / 条件：BIP143 只适用于 witness v0；p58 画的“组装 witness”不是所有 BTC input 类型的通用步骤。Taproot 按 BIP340 / 341 用 Schnorr、x-only keys、tagged hash 和 tweak；签名通常 64 字节，非默认 hashtype 时 65 字节，不能将 ECDSA DER 转码成 Schnorr。
- PPT：p57–59。支持 secp256k1 ≠ 支持 Taproot 签名。**边界**：KMS / 当前 CloudHSM ECDSA 可服务 legacy / SegWit v0 spending，不原生生成 BIP340 签名；但可以花 ECDSA inputs、创建付款给外部 P2TR 地址的输出，不能误写成“完全不能向 Taproot 地址付款”。BIP32 私钥派生需要 chain code、HMAC-SHA512 与私钥标量运算，普通 Sign oracle 无法替代。

### S10 — EVM 原始规范与 AWS 示例：Keccak / low-S / recovery

- 链接：[EIP-2](https://eips.ethereum.org/EIPS/eip-2)；[EIP-155](https://eips.ethereum.org/EIPS/eip-155)；[EIP-1559](https://eips.ethereum.org/EIPS/eip-1559)；[AWS KMS EIP-1559 示例说明，2022-02-10](https://aws.amazon.com/blogs/database/how-to-sign-ethereum-eip-1559-transactions-using-aws-kms/)。
- 核验结论：交易按其类型构造待签 payload，再用 **Keccak-256（不是 NIST SHA3-256）** 得到摘要；ECDSA 参数由 DER 提取，须 low-S。KMS 不返回 recovery / yParity，须用摘要与 `(r,s)` 恢复候选公钥并与预期 key / 地址比对；low-S 翻转后须重新确定 parity，不能沿用未规范化签名的值。
- 版本 / 条件：legacy EIP-155 的 `v = 35 + 2×chainId + parity`；EIP-1559 type 2 序列化的是 yParity，不是把该 v 原样填入。AWS 老示例用已退出的 Rinkeby 与旧库 API，仅证明算法组合，不证明当前网络 / SDK 代码原样可部署。
- PPT：p57 的密钥能力延伸、p56 Ethereum 条目。**推论 / 待验收**：ECDSA DIGEST 跳过 KMS 哈希，因而可签外部构造的 32 字节 Keccak 摘要；这不是 KMS 提供 Keccak 算法。批准 chainId、nonce、to、value、calldata、fee bounds 后才可签，不能做任意摘要签名端点。

### S11 — CloudHSM：确实支持 secp256k1，但硬件代际须更新

- 链接：[Client SDK 5 PKCS#11 key types](https://docs.aws.amazon.com/cloudhsm/latest/userguide/pkcs11-key-types.html)；[HSM types](https://docs.aws.amazon.com/cloudhsm/latest/userguide/hsm-types.html)；[Deprecation notifications](https://docs.aws.amazon.com/cloudhsm/latest/userguide/compliance-dep-notif.html)。
- 核验结论：当前 SDK 5 的 EC key 表明确列 `secp256k1 (Blockchain)`，不是据“支持 EC”猜测。`hsm2m.medium` 要求 SDK ≥ 5.9.0，支持 FIPS / non-FIPS cluster modes；hsm1 已于 2026-03-31 到达 end of support。
- 版本 / 条件：p59 的 FIPS 140-2 世代描述不能当作当前新建硬件说明；hsm2m 文档列 FIPS 140-3。曲线支持、集群工作模式、硬件模块认证、某算法是否为获批服务是不同问题。key-types 页未提供完整的 secp256k1 × mode × firmware 矩阵，本次不声称所有组合均已验证，也不声称 secp256k1 为 FIPS-approved。
- PPT：p57、p59。**设计建议**：生成 EC key 时显式选 secp256k1 与不可导出 / sensitive 属性，并验收属性与离线签名；“私钥永不出硬件”是配置、来源和恢复设计条件，不是所有导入 / 导出选项的无条件结论。

### S12 — CloudHSM：CKM_ECDSA、编码、二次哈希与 Schnorr 区别

- 链接：[SDK 5 PKCS#11 mechanisms](https://docs.aws.amazon.com/cloudhsm/latest/userguide/pkcs11-mechanisms.html)；[OASIS PKCS#11 v2.40，§2.3.1 / §2.3.6](https://docs.oasis-open.org/pkcs11/pkcs11-curr/v2.40/os/pkcs11-curr-v2.40-os.html)。
- 核验结论：SDK 5 支持 single-part `CKM_ECDSA` 与 ECDSA-with-hash 系列。已计算 Bitcoin sighash / EVM Keccak 摘要，应选 **CKM_ECDSA**；`CKM_ECDSA_SHA256` 会再 SHA256，且 SDK 5 的 RSA / ECDSA hashing 在客户端软件完成。算法名称相似不代表摘要语义相同。
- 版本 / 条件：PKCS#11 的 ECDSA 签名是固定宽度 `r || s`，secp256k1 为 64 bytes；不是 KMS DER。BTC 须先提取并规范化 low-S，再编码 DER、追加 hashtype；EVM 须得到正确 parity。SDK 5 不支持 SignRecover / VerifyRecover，不意味着应用不能自行做 EVM public-key recovery。
- PPT：p57、p59。当前列出的 ECDSA / EdDSA / ML-DSA 不是 BIP340 Schnorr；机制表没有 BIP340 或 BIP32 CKD。提供 HMAC / ECDH KDF 不足以证明完整 HD 派生能在不可导出的 EC key 内完成。不能通过换 DER 格式“支持 Schnorr”。

### S13 — CloudHSM：SDK snapshot / Region / VPC 条件

- 链接：[Latest Client SDK release](https://docs.aws.amazon.com/cloudhsm/latest/userguide/latest-releases.html)；[CloudHSM endpoints and quotas](https://docs.aws.amazon.com/general/latest/gr/cloudhsm.html)。
- 核验结论：本日 latest release 页列 **5.18.0**；≥5.9.0 是 hsm2m 兼容下限，不是建议永远用 5.9。自 5.17 起页面给出最多前 3 个 minor 版本 / 发布后一年支持规则。须核对 OS、CPU 架构及 PKCS#11 / JCE / OpenSSL 对应组件，不能把 AWS API SDK 与 CloudHSM Client SDK 混为同一版本。
- 版本 / 条件：hsm2m 按 S11 可用于 CloudHSM 支持的 Region；本日区域表含上面 6 个 BTC Access 商业 Region，所以这些组合在**区域文档层面**相容，Query 共区只在 `us-east-1`。其他地区的 HSM 可用性不能扩展 AMB 网络可用性；不据 GovCloud / 中国分区名称推定商业 AMB 可用。
- PPT：p57、p59。图中的 VPC / client / Crypto User 是签名数据面的职责；CloudHSM 管理 API 的 IAM 权限不是 `C_Sign` 的逐次业务审批。**设计建议**：私有 VPC 内独立 signer、至少 2 个 HSM 的跨 AZ 可用性与恢复测试；该拓扑未部署，Region 端点表也不是实际容量 / 账号资格证明。

### S14 — IAM / CloudTrail / Nitro：授权与隔离，不是业务审批

- 链接：[KMS Sign CloudTrail example](https://docs.aws.amazon.com/kms/latest/developerguide/ct-sign.html)；[Nitro Enclaves 概念与 requirements](https://docs.aws.amazon.com/enclaves/latest/user/nitro-enclave.html)；[Enclave KMS attestation](https://docs.aws.amazon.com/enclaves/latest/user/kms.html)；[KMS Nitro condition keys](https://docs.aws.amazon.com/kms/latest/developerguide/conditions-nitro-enclave.html)；[KMS Decrypt / Recipient](https://docs.aws.amazon.com/kms/latest/APIReference/API_Decrypt.html)。
- 核验结论：Sign 需要 key policy / IAM 授权，CloudTrail 记录 API 事件；示例没有业务提币字段或签名 payload，不能代替批准金额 / 目的地址的业务日志。签名 API 接受摘要而不解释交易，故**推论**：“私钥不可导出”不消除被滥用为 signing oracle 的风险。[S08、S10]
- 版本 / 条件：Enclave 是支持的 EC2 parent 上隔离 CPU / 内存的 VM；无持久存储、外部网络或交互访问，只通过 parent socket 通信。文档列所有 AWS Regions，但仍受实例类型限制，不支持 Outposts / Local / Wavelength Zones；不是 Fargate 中自动存在的功能。
- 核验结论：`Recipient` 携 attestation，KMS Decrypt 返回 `CiphertextForRecipient`，不是 parent 可读 plaintext。policy 可绑定 `kms:RecipientAttestation:ImageSha384` / `PCR0/1/2/3/4/8`；**必须检查其他 Allow / grants 不绕过此限制**。这些 condition 的已列操作是 Decrypt、DeriveSharedSecret、GenerateDataKey、GenerateDataKeyPair、GenerateRandom，**不包括 Sign**；不能宣称给 KMS Sign 加同样条件就形成 enclave-only signer。
- PPT：p57–59。**设计建议**：xprv 用应用层信封加密；飞地经 attested Decrypt 解密数据密钥，再在可信内存中解开 seed / xprv、执行 BIP32 和软件签名。[S09] 私钥完整值仍在飞地内存出现，不能称“从未以明文出现”或“始终是不可导出的 HSM key”。attestation 证明代码测量匹配，不证明业务审批、运行代码无漏洞或 parent 提供的交易无恶意。

### S15 — Secrets Manager：version / rotation 不会移动链上资金

- 链接：[What's in a secret / versions](https://docs.aws.amazon.com/secretsmanager/latest/userguide/whats-in-a-secret.html)；[Rotate secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)。
- 核验结论：secret 的 string / binary 值被 KMS 加密，变更 / rotation 会产生新版本；`AWSCURRENT`、`AWSPREVIOUS`、`AWSPENDING` 是版本标签。Secrets Manager 是存储 / 访问与轮换能力，不是 BTC / EVM 私钥签名服务。
- 版本 / 条件：普通 seed / xprv 没有文档承诺的链上钱包 managed-rotation；自定义 Lambda 可以实现外部流程，但不会因标签切换自动替换地址、转移旧 UTXO / token 或完成资金归集。存储层换加密 key 与更换链上 signing key 也不是同一件事。
- PPT：p57。**设计建议**：旧钥匙必须保留到旧地址余额、迟到入金及相关合约权限处理完毕，另做恢复与清退。若要求 parent 不见 seed，不可把普通 `GetSecretValue` 返回的 seed 明文再送入 enclave；存应用层密文，用 S14 attested unwrap，在飞地内解密。

## 对 p57–59 的签名流程修订

以下是依据 S08–S12 的实现要求整理，不是本项目运行记录：

| 步骤 | BTC ECDSA（legacy / SegWit v0） | EVM ECDSA（以 type 2 为例） |
| --- | --- | --- |
| 构造 / 计算 | 为每个 input 选择相应 script / sighash 规则；v0 覆盖 prevout amount，双 SHA256 | 按 EIP-1559 构造 unsigned payload，Keccak-256；绑定 chainId / nonce 等 |
| KMS | `ECC_SECG_P256K1`、`SIGN_VERIFY`、`ECDSA_SHA_256`、`DIGEST` | 相同 ECDSA / DIGEST 配置；Keccak 在应用端计算 |
| CloudHSM | secp256k1 + `CKM_ECDSA`，不要选再次 hashing 的 mechanism | 同理，不把 Keccak digest 再喂给 SHA256 signing mechanism |
| 适配输出 | KMS DER / PKCS#11 `r||s` → low-S → 严格 DER → 1-byte hashtype；按 input 类型填 scriptSig 或 witness | 提取 `(r,s)` → low-S → 恢复并校验 sender / yParity → 按 tx type 序列化 |
| 结果判定 | 先离线验证，再广播并跟踪 mempool / 入块 / 重组 / 深度；txid 与 wtxid 分离 | 先离线验证 sender，再广播，检查 receipt / execution status 与确认规则 |

p58 的“每次调用经 CloudTrail”不能替代 business authorization；p59 的“私钥永不离开硬件”需显式生成 / 导入与不可导出属性条件。两图的广播箭头不保证“进入全网 mempool→矿工打包”必然发生；“≥6 确认”也不是所有网络 / 业务的统一完成条件。[S03、S06、S08、S11、S14]

## 未能仅靠官方资料确证的事项

- 本账号是否为 AMB 现有客户、实际 endpoint 连通性与 Region 资格：未检查。
- AWS 所称 BTC Testnet 的具体代际、运行节点 client 精确版本：所核支持章节未明确；部署验收须核对 network identity，不能把名字相同当作链一致。[S02]
- Query 从首次入块 / 达 finality 到可查的 P50 / P95 / P99、异常期间延迟、跨分页冻结 snapshot：所核文档没有数值 SLA / 一致性承诺；不能编造。[S06–S07]
- CloudHSM secp256k1 在特定 cluster mode / firmware / SDK binary 上的可执行结果与算法认证范围：有曲线支持证据，无该组合的本次实测。[S11–S13]
- KMS 的低-S 分布、性能、业务策略防绕过；Enclave parent 被攻陷时能否抵挡伪造交易；恢复 / migration 是否成功：未测试。
- PPT “本项目已云上跑通”：仅原作者声称，没有我们的独立证据。AWS 示例也只证明第一方提供过相应方法，不能替代当前项目与当前网络验收。

## AWS wallet 参考部署与数据 / 控制流

**本节全部为设计建议，不是已验证项目，不是 AWS 已代建的钱包产品；未实施任何资源操作。** 组件能力与限制依据 S01–S15，组合、权限划分、状态机和测试阈值由此处提出。

### 参考部署条件

- 以 `us-east-1` 作为候选共区配置，便于现有 AMB Query / Polygon 与 BTC Access 相交；这不是必须的全球部署地，也不保证账号可用。新 AMB 客户采用可替换 RPC / 自管节点和索引器，不假定可新增 AMB；现有客户同时建设 2027-09-29 前迁出路径。[S01–S06]
- API / policy / builder / broadcaster / scanner 分角色部署于 ECS 或 EC2，账务与 UTXO / nonce 状态存放受事务 / 条件写约束的数据库；队列只作为调度，不作为批准凭证。公网请求端、普通 builder 不持有 signing 权限。
- 签名分三条可选路径：KMS 单钥 ECDSA；CloudHSM SDK 5.18.0 + hsm2m EC ECDSA；支持的 EC2 parent + Nitro Enclave 软件 HD / BIP340 signer。前两者不承诺 Taproot spending；第三条把 private-key plaintext 边界收缩到 enclave 内存。
- 对 CloudHSM 逐项锁定 OS / 架构、binary checksum、curve、mechanism、mode、密钥不可导出属性；对 Enclave 锁定 EIF 测量 / PCR / 受信代码发布过程，不用 Fargate 图代替 EC2 parent。

### 一条交易的数据流

```text
地址 / 公钥目录 ──────→ scanner / 历史索引 ─→ 链观察库 ─→ 内部账务 / 对账
                              ↑
                              │ blocks / receipts / indexed events
用户意图 → API → 业务审批 → builder + UTXO/nonce预留 → signing gate
                                                      │
                           ┌──────────────────────────┼─────────────────────────┐
                           ↓                          ↓                         ↓
                    KMS ECDSA DIGEST             CloudHSM ECDSA         attested Enclave
                    返回 DER                    返回 r||s              解密 xprv / 派生 / 签名
                           └──────────────────────────┼─────────────────────────┘
                                                      ↓
                                     协议适配 + 离线验签 + 已签payload持久化
                                                      ↓
                           broadcaster → 可替换 RPC → 链 → scanner → 状态与账务
```

Query 在图中只是可选历史 / 对账读路径，不串在“签名→广播”写路径中；其 final-only balance 不能充当 pending 状态的可用余额或 UTXO 锁。[S06–S07]

### 与数据流分开的控制流：防 signing oracle

1. 审批凭证绑定完整、规范化意图：wallet / network / chainId、目的地址、金额、资产合约、calldata、费用上限、输入 / nonce、key ID / derivation path、策略版本、有效期与唯一 request ID。
2. signer 独立校验审批凭证、白名单 / 限额和交易解释，再由完整 payload 重新计算链协议摘要；不能对来自 builder 的任意 32 bytes 直接无条件签名。审批人与签名角色权限分离。
3. KMS 最小化到指定 key ARN / signing algorithm，业务网关只允许既定 DIGEST 流程；CloudHSM 最小化 CU / key 权限；广播角色不持签名 / seed 解密权限。不要设计不存在的“AMB IAM 单 RPC 限制”或“Nitro 条件约束 KMS Sign”。[S02、S04、S08、S14]
4. 防重放由 signer 的授权消费记录与数据库原子状态转换保证；请求重试应复用已签 payload。审批后改变找零、destination、fee bounds、nonce 或输入集合，须按策略重新审批。Enclave parent 是转发者，不是信任来源。
5. 分别保留业务审计（意图、审批、摘要、key / public-key fingerprint、txid / wtxid、状态）与 AWS API / HSM 事件证据，建立关联 ID；不在日志写 seed / xprv / CU secret。attestation 失败或策略不匹配须 fail closed。[S14–S15]

建议状态机：

```text
requested → approved → reserved → signed → submitted → included → policy-confirmed
                                          │              │
                                          └→ rejected    └→ reorged → 重新观察 / 对账
```

提交超时应有 `submission-unknown` 与查链 / 重试分支，不当作未提交；included 不等于 EVM execution success，不等于 Query FINAL，也不等于业务可最终入账。[S03、S06–S07、S10]

### 验收点（全部待执行，本次无“通过”项）

| 验收面 | 应取得的证据 / 必须验证的负例 |
| --- | --- |
| 生命周期与网络 | 账号服务资格；精确 network / chainId / genesis、Region、endpoint、client / SDK / firmware 版本；现有 AMB 客户的替代路径与截止日前迁移记录。 |
| RPC allowlist | 所用区块、UTXO、fee、broadcast 方法与参数成功 / 失败样本；节点钱包方法拒绝；gzip、batch、payload、限流与退避行为；自有网关读角色不能调用广播。 |
| BTC KMS / HSM | 使用公开 BIP143 / DER 测试向量离线验证；逐 input 正确 sighash / amount / hashtype；DER 与 PKCS#11 `r||s` 双向适配、低-S、scriptSig / witness、txid / wtxid；RAW / hashing-mechanism 二次哈希负例必须失败。 |
| EVM | EIP-155 / type 2 向量、Keccak 与 SHA3 混用负例、low-S 前后 parity、恢复 sender、chainId / nonce 绑定；wrong sender / network 拒签，receipt revert 不记为付款成功。 |
| Taproot / HD | KMS / ECDSA 路径拒绝 P2TR spending；若启用 enclave，运行 BIP32 hardened / leading-zero 向量与 BIP340 / 341 tweak / sighash 向量，验收输出类型，而非只测“有一个签名”。 |
| Query 延迟与分页 | 分开测首次入块可见、finality 到 balance 可见的延迟分位数；FINAL / NONFINAL 边界、空页带 token、250 上限、全页遍历；固定历史区间重复对账，模拟索引滞后，不从缺失结果推断 outgoing 未广播。 |
| 并发与重组 | 多任务重复提币 / UTXO 双选 / nonce 冲突、队列重投、提交超时、替换 / 失效交易、短链回滚与跨供应商观察不一致；不能重复扣账或重复记完成。 |
| 审批 / oracle | 绕过 API 直接尝试签名、任意 digest、改 destination / calldata / fee、过期或重放审批、错误 key / path、策略撤销与 signer 被调用过多的负例。IAM 成功或存在 CloudTrail 不能视为该项通过。 |
| Enclave | 无 Recipient、错误测量、未受信 EIF / 调试配置、替代 Allow / grant、parent 直接 Decrypt 必须不获 plaintext；parent 只看到密文 / 非敏感输出；真实 seed / child key 不出 enclave，升级与恢复仍可用。 |
| CloudHSM / 恢复 | 指定 SDK / mode / curve 的生成与签名记录、不可导出属性、CU 最小权限、节点 / AZ 故障与恢复演练；认证范围与算法可执行结果分开记录。 |
| Rotation / 迁移 | Secrets Manager 版本切换不被当作资产迁移；旧地址迟到入金 / 未花余额 / 合约权限处理、密钥恢复；RPC 双读按固定 block hash / 高度与确认深度对比，Query 替代模型含分页与 txid / wtxid 映射。 |

验收证据以后须在获得额外执行授权后采集；本次只给出待测清单。最终对 PPT 可写的措辞是：“官方文档支持按上述边界组合相关能力；原作者声称曾云上跑通，本次未独立复现；2026-10-29 起 AMB 新客户受限，须更新参考架构与迁移计划。”
