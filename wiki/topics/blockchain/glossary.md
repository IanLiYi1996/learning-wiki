# 术语表：优先分清容易混淆的对象

以下是便于阅读的定义摘要；协议细节见相应正文及 [一手来源表](sources.md)，不替代规范。

| 术语 | 简要含义 | 不是什么 | 阅读 / 来源 |
| --- | --- | --- | --- |
| UTXO | 未花费交易输出 | 账户中的可修改余额 | [02](chapters/02-bitcoin.md)，B01 |
| Outpoint | txid + 输出索引 vout | 地址 | 02，B01 |
| Address | 按特定网络规则编码的接收提示 | 完整资产身份、保证本人控制 | 02 / [05](chapters/05-wallet-engineering.md)，B09 |
| scriptPubKey | 输出的花费规则 / 锁定脚本 | 接收方私钥 | 02，B03 |
| scriptSig | 输入的传统解锁脚本字段 | SegWit 后已完全删除的字段 | 02，B03 |
| Witness | 输入见证材料 | 全区块末尾集中区、链外未验证数据 | 02，B03 |
| txid | 传统序列化双 SHA-256 | 要签的 sighash | 02，B03 |
| wtxid | 含 witness 序列化的标识 | 只对签名做哈希 | 02，B03 |
| sighash | 依输入与类型生成的签名消息摘要 | 统一等于 txid | 02，B04 / B06 |
| target / difficulty | PoW 阈值 / 其反比难度 | 同方向变化的两个量 | 02，B01 |
| chainwork | 逐有效块累计的规则工作量 | 节点票数、实际已计数哈希次数 | 02，B01 |
| stale / orphan | 未入活动链有效块 / 本节点父块未知块 | 所有交易永远不存在 | 02，B14 |
| Confirmation | 相对当前链的包含深度 | 无条件零风险 | [01](chapters/01-system-model.md)，B02 |
| Finality | 特定协议 / 服务下的最终性语义 | RPC返回hash、所有链通用的同一块数 | 01 / [07](chapters/07-aws.md)，A06 / C16 |
| Mempool | 节点观察的待打包候选集 | 全网唯一数据库、最终账本 | 02，B01 |
| weight / vsize | 加权大小 / 向上取整的虚拟字节 | 直接等于网络字节数 | 02，B03 |
| Taproot | P2TR承诺与花费机制 | 旧ECDSA输出自动迁移、匿名币 | 02，B05 / B06 |
| MuSig2 | n-of-n协同Schnorr签名协议 | 任意独立完整签名相加、自动t-of-n | 02 / [06](chapters/06-security.md)，B08 |
| HTLC | 哈希条件与时间锁组合 | 到点自动执行的定时银行转账 | 02，B10–B12 |
| Watchtower | 特定通道作弊监控 / 预授权惩罚 | 一般离线收款代理 | 02，B13 |
| nonce | 依账户 / 类型定义的顺序状态 | 网络无关全局计数 | [03](chapters/03-ethereum.md)，E04 / E11 |
| gas / gasLimit | 执行资源单位 / 预算上限 | 实际费用本身 | 03，E02 |
| receipt | 链上交易执行摘要 / 日志 | 指定资产一定到账的充分证据 | 03 / 05，E08 / E09 |
| slot / trie path | Solidity存储位置 / 哈希树查找路径 | 所有层都同一个key | 03，E01 / E07 |
| stateRoot / storageRoot | 全局账户承诺 / 特定账户存储承诺 | 发行方银行余额证明 | 03，E01 / E03 |
| Proxy | 委托到实现逻辑的合约结构 | 字节码固定所以行为固定 | 03，E06 |
| approve / permit | 链上直接 / 签名授权修改allowance | 授权本身已完成转账 | 06，E09 / E14 |
| UserOperation | ERC-4337账户操作请求 | 普通EOA交易 | 06，E11 |
| EIP-7702 | EOA代码委托机制 | 与4337完全同一流程、只存一次性无状态授权 | 03 / 06，E04 |
| Safe module | 已启用的额外执行 / 控制路径 | 必须始终通过owner阈值 | 06，E16 |
| DKG / TSS | 分布式密钥生成 / 门限签名协议 | Shamir恢复后在一台机器签名 | 06，W08 |
| seed / xprv / xpub | 派生起点 / 扩展私钥 / 扩展公钥 | 同一泄露范围 | 06，W06 / W07 |
| PSBT | 构造、签名、最终化的交换格式 | 含私钥的加密备份 | 05，W02–W04 |
| Mint / Token Account / ATA | Solana资产标识 / 某mint余额账户 / 常用派生账户 | EVM合约地址 / 通用钱包地址同一个对象 | [04](chapters/04-ecosystem.md)，S03 |
| PDA | 无私钥的program派生地址 | 程序持有私钥、地址已存在就有资金 | 04，S05 |
| Sidechain / Rollup | 独立共识 / L1承诺验证的扩容类别 | 一个品牌下全部产品必同安全模型 | 04，C10 / C18 / C19 |
| XCM / 传输通道 | 消息格式 / 运送机制 | 一个同义协议 | 04，C13 |
| IBC / 共享安全 | 通信标准 / 独立安全机制安排 | 接入前者自动获得后者 | 04，C14 / C15 |
| Reserve attestation | 特定范围储备鉴证 | 整家公司全财务审计与安全担保 | 04，C03 |
| Delta-neutral | 尽量抵消方向性价格风险的组合 | 费用、托管、流动性风险为零 | 04，C07 / C08 |
| DER / r||s / yParity | 不同签名输出编码与恢复信息 | 可直接互换的链上整笔交易 | 07，A05 / A19 / E02 |
| KMS DIGEST | 对指定ECDSA配置签已给摘要 | 又算一次SHA256的RAW模式 | 07，A05 |
| Attestation | 对飞地测量与来源等的证明 | 代码无漏洞、业务已批准 | 07，A14 / A15 |
| Rotation | 秘密 / 版本 / key管理流程 | 自动迁走链上旧地址资金 | 07，A16 |

## 升级篇新增对象

| 对象 | 先这样理解 | 不能混同 |
| --- | --- | --- |
| authority / outer sender | 7702被委托账户 / 外层交易发起者 | 业务签名者、委托地址与收款地址 |
| Path archive | 按路径与历史增量组织状态的客户端数据库 | 主网承诺树已经升级 |
| PeerDAS / BPO | 数据可用性抽样 / 只调blob参数的分阶段升级 | 执行正确性证明 / 固定L2费用 |
| Votor / Rotor | 新最终性投票机制 / 后续传播阶段 | 两者都已上线 |
| bank_id | 某节点的执行候选实例身份 | 跨供应商统一blockhash |
| transactionConfig | Solana v1消息的资源/fee配置 | 旧格式ComputeBudget指令解析 |
| Coretime region / task | 验证资源时间权利 / 已分配调度对象 | 买下一台CPU / 已自动启动链 |
| Pessimistic proof | 跨链桥资产会计约束的证明 | 整条链合约执行与DA均已证明 |
| IBC classic / v2 | 共存但对象、报文与配置不同的协议 | 库升级后所有旧channel自动转新协议 |
| sUSDS shares | vault份额 | 原样等于USDS或美元数量 |
| CCTP attestation | 对跨链消息的发行方证明 | 源链物理finality提前、目标付款已完成 |
| Cluster / chunk | mempool依赖组件 / 共同费用选择的分组 | 共识上的新账户或全网统一队列 |
| PureEd25519 / Ed25519ph | 原消息签名 / 特定预哈希模式 | 可任意互换的RAW与DIGEST |

详细定义、当前状态和一手依据见 [升级篇总索引](upgrades/README.md)，不从名称本身推断部署支持。
