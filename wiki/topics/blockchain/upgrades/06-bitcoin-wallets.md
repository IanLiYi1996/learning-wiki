# 06｜Bitcoin 新版工程：MuSig2、PSBT、cluster mempool 与 Testnet4

- 查阅日：2026-10-29（北京时间）
- 旧内容定位：PPT 15–22、43–44、55–59；[基础篇 02](../chapters/02-bitcoin.md)
- 目标：区分主网共识、客户端策略、交换格式与测试网络的更新
- 状态：原始规范 / 官方发布说明核验；没有升级节点、操作密钥或建立通道

## 1. Bitcoin 没有因软件升级整体换一套共识

UTXO、最多累计工作量、主网难度调整与脚本花费规则不能因客户端发布新版本而随意改写。这里补的是钱包与节点的当前接口 / 策略演进，而不是把所有新功能说成一次主网硬分叉。

截至查阅日，官方 release 列表已有 **Core 32.1**。其说明特别写明 32.0 虽 tagged，却未完整正式发布；本专题此前固定 Core v30.0 是可复查的代码审计基线，不是今天的安装推荐。[32.1 发布说明](https://bitcoincore.org/en/releases/32.1/)

## 2. MuSig2：把“签名可相加”还原成完整协作协议

### 旧简化为什么不够

两个各自完成的 Schnorr 签名不能直接相加成一份目标签名。BIP327 的 MuSig2 是 n-of-n 协同签名，参与者共同确定密钥、nonce、消息与聚合过程；它不是任意 t-of-n 门限方案。[BIP327](https://github.com/bitcoin/bips/blob/master/bip-0327.mediawiki)

### 新流程包含哪些对象

```text
参与者公钥列表与顺序
  → KeyAgg：聚合密钥上下文
  → 可选派生 / Taproot tweak
  → 每方NonceGen：私有nonce材料 + 公共nonce
  → 汇集公共nonce，形成同一会话
  → 每方核对交易、消息、密钥和会话
  → Sign：partial signature
  → 聚合 / 验证部分贡献
  → 一份BIP340兼容签名
```

这是 BIP327 各算法职责的学习摘要，不是可以直接用于密码实现的伪代码。

为什么有 key aggregation coefficients：将公钥列表纳入聚合规则，避免应用把恶意选择的公钥当成简单求和。为什么每方使用双 nonce：nonce 与会话组合属于安全协议设计的一部分，不是“大家发一个随机数就行”。具体标签哈希、特殊系数、奇偶归一化和 tweak 由规范决定。[KeyAgg / General Signing Flow](https://github.com/bitcoin/bips/blob/master/bip-0327.mediawiki)

### 接到 Taproot 时的三种密钥

```text
各人的长期公钥
  → MuSig2聚合internal key
  → Taproot tweak后的output key
```

不能拿第一层或第二层的签名预期代替最后的输出花费规则。script path 是独立备用条件；用 MuSig2 并不自动为未来丢失参与方提供恢复。[BIP341](https://github.com/bitcoin/bips/blob/master/bip-0341.mediawiki)

### 教学场景

Alice 和 Bob 共同控制一个 key-path 输出。正常花费必须两方完成同一会话；Bob 离线时，Alice 不能因为自己的签名合法就单独完成 MuSig2。若需要单方在超时后恢复，应提前在脚本策略中设计并保存恢复材料，而不是事后改变 n-of-n 性质。

这是控制路径示例，不是某个钱包已经实现的恢复功能。

### 2026 年的规范更新要读哪里

查阅日 BIP327 版本为 **1.0.4**，changelog 记载 2026-08-19 修正 PartialSigAgg 的两个规范问题。算法实现、测试向量和参考代码要匹配，不应只说“支持 MuSig2”而不记录版本。[BIP327 Changelog](https://github.com/bitcoin/bips/blob/master/bip-0327.mediawiki)

设计建议：secret nonce 只能消费一次，签名超时 / 崩溃恢复不能导致重用；未验证的 partial signature 不当作独立付款批准凭据。生产实现使用经审计且目标链兼容的库。

## 3. Descriptor：备份的不只是几个私钥

Descriptor 描述输出脚本集合、key origin、派生路径及策略。维护者文档覆盖 `wpkh`、`wsh`、`tr`、多签及 MuSig2 聚合等语义；脚本支持不代表所有 GUI、硬件与 RPC 都实现了相同能力。[Core descriptors](https://github.com/bitcoin/bitcoin/blob/master/doc/descriptors.md)

教学抽象：

```text
keys + derivation + script policy + range
  → 这套钱包应识别和控制的输出
```

两人多签不是“各留一段助记词”就能保证恢复，可能还需要另一方 xpub、公钥顺序、路径、脚本、Taproot 承诺和扫描范围。前缀 `bc1p` 不能还原这些信息。

32.1 的 `exportwatchonlywallet` 可导出 descriptor wallet 的公开描述符与相关钱包信息，但不带私钥，供在线观察端使用；`addhdkey` 加入扩展 key 不会自动生成输出脚本，仍需明确描述符。[32.1 Wallet 变更](https://bitcoincore.org/en/releases/32.1/)

工程建议：恢复演练验证“找得到旧输出且能按旧策略花费”，不只验证能从 seed 派生一个新地址。

## 4. PSBT v0 → v2：升级的是协作格式

PSBT 将 Creator / Updater / Signer / Finalizer 等角色分开，让离线签名器获得交易及必要 prevout / 策略材料。它不是私钥备份或自动安全批准。[BIP174](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)

| 属性 | PSBT v0 | PSBT v2 |
| --- | --- | --- |
| unsigned tx 的组织 | global 中整体 unsigned transaction | 分散到global / input / output字段 |
| 输入输出的增补 | 全局结构固定带来协作限制 | 显式字段与modifiable规则支持构造阶段增补 |
| 版本表达 | 缺version字段时按v0解释 | 明确version=2，排除v0 global unsigned tx字段 |

BIP370 解决协作构造与字段定位问题，但不授权 coordinator 在签名者不知情时更改已经承诺的输出。是否还能修改，受 PSBT flags、现有签名与 sighash 规则共同约束。[BIP370](https://github.com/bitcoin/bips/blob/master/bip-0370.mediawiki)

### Taproot 不是把 PSBT v2 标签打上就支持

BIP371 为 **PSBT v0 与 v2** 增加 Taproot signature、script、control block、key derivation 等字段。容器版本和花费路径是不同维度。[BIP371](https://github.com/bitcoin/bips/blob/master/bip-0371.mediawiki)

验收矩阵至少交叉：

```text
PSBT version：v0 / v2
input：legacy / segwit-v0 / taproot
signer：软件 / 硬件 / 远程 / 协作
sighash与找零策略
finalizer与extractor版本
```

“支持 PSBT”“支持 Taproot”“能最终化脚本路径”不能合并为一个勾选项。

### 在线观察 + 离线签名的完整职责

```text
在线watch-only：收款扫描、选币、构造PSBT
  → 离线：核对收款、找零、prevout金额、fee、策略，签名
  → 在线：最终化、验签、持久化、广播和观察
```

官方离线教程已采用 watch-only 文件导出路径。本次只解释该架构，未执行其示例命令；教程正文仍提 v32.0，选二进制时不能覆盖32.1发布说明的正式状态。[维护者离线教程](https://github.com/bitcoin/bitcoin/blob/master/doc/offline-signing-tutorial.md)

## 5. cluster mempool：费用判断不再只盯一笔交易

Core 31 引入 cluster mempool：按未确认交易的父子依赖，把相连交易划成 connected components；在 cluster 内形成用于共同选择的 chunks。用于出块选择、驱逐、中继和 RBF 的成本判断因此可以覆盖相关交易，而不是只按某笔 fee 排序。[31.0 Mempool 变更](https://bitcoincore.org/en/releases/31.0/)

```text
父交易P：低fee
  ├─ 子交易C1：高fee，花P的输出
  └─ 子交易C2：依赖P，可能又有自己的后继

交易图 → cluster → chunks / 有效fee排序
```

### 教学例：CPFP 改善的是依赖组合

假设普通交易、未受额外 sigops 策略限制：

```text
P：200 vB，fee=200 sat
C：100 vB，fee=700 sat

组合：900 / 300 = 3 sat/vB
```

例子解释共同包含时的费用视图，不保证任意网络都接受这个包，更不保证固定时间入块。

当前替换策略还需要满足绝对 fee、增量中继成本和 feerate diagram 改善等条件。“替换单笔的费率更高”不能推出复杂依赖图必可替换。[维护者 RBF policy](https://github.com/bitcoin/bitcoin/blob/master/doc/policy/mempool-replacements.md)

### 新限制与钱包要改变的验收

31 的默认 cluster count / size 限制替代旧 ancestor / descendant 限制，旧 CPFP carveout 被移除。相关 RPC 可查看 cluster、chunks 与 fee diagram；部署参数和供应商支持必须单独检查。[31.0 发布说明](https://bitcoincore.org/en/releases/31.0/)

设计建议：

- 构造依赖链、扇出、替换与高低费组合的测试，不只发送孤立交易。
- 不以旧祖先 / 后继固定数字推断今天中继结果。
- 与硬件无关，节点 policy 变化也可能影响已签交易能否进入所用 mempool。
- `testmempoolaccept` 是某节点此刻的判断，不是全网未来承诺。

主网共识与 mempool policy 分开：策略拒绝的交易不必然是无效区块交易；不同实现 / 版本 / 节点参数可能有不同中继结果。

## 6. 费用字段还有一个容易漏掉的“新视角”

BIP141 的 `ceil(weight/4)` 是学习交易大小的基础，但 Core 的 policy / RPC `vsize` 还可能取该大小与 sigops size 的较大值。mempool中的 modified fee 也可包含本地优先级调整，不一定等于输入减输出的原始 fee。[mempool terminology](https://github.com/bitcoin/bitcoin/blob/master/doc/policy/mempool-terminology.md)

纯单位教学例：

```text
BIP141权重大小 → 125 vB
sigops size    → 200
policy vsize   → 200
```

因此“按字节计费，简单”在钱包入门有用，但在复杂脚本、包、替换和节点策略中仍要区分不同单位及范围。原离线练习只验证 BIP141 理想化大小模型。

## 7. Testnet3 → Testnet4：新的测试链，不是旧链继续加块

BIP94 定义新的 Testnet4；Core 28.0 已加入支持。它不是 Testnet3 的余额原地升级，更不是主网改规则。不同 genesis 和链状态要作为独立 network identity。[BIP94](https://github.com/bitcoin/bips/blob/master/bip-0094.mediawiki)、[28.0 上线支持说明](https://bitcoincore.org/en/releases/28.0/)

为什么改：旧测试链的最小难度例外可能与周期末取基准难度组合出 block storm。Testnet4 保留测试用20分钟例外，并调整周期难度基准、限制周期首块的时间回退行为。[BIP94 规则](https://github.com/bitcoin/bips/blob/master/bip-0094.mediawiki)

具体区别：

1. 超过20分钟的测试最小难度例外不用于周期首块。
2. 周期重定向的基础难度取上一周期**首块**，而非可能已降至最小难度的末块。
3. 周期首块时间戳不能比上一块早超过600秒，仍满足MTP条件。

这解释为什么不能用测试网的某次目标变化来反驳基础篇的主网公式。

工程建议：即使地址格式相似，也记录 genesis、网络参数、节点 chain 字段、配置和服务端实际返回，不把字符串 `Testnet` 当充分身份。AMB旧文档没有明确代际，不能自行假定它已切换Testnet4。

## 8. Lightning Taproot channels：实现能力不等于全网自动迁移

当前 LND API 的 channel commitment type 明确列 production `TAPROOT`，使用 MuSig2 funding 与 tapscript 特性；`SIMPLE_TAPROOT_FINAL` 是保留的旧别名。其他通道类型与旧通道不会因该枚举存在自动变成 Taproot。[LND ListChannels](https://lightning.engineering/api-docs/api/lnd/lightning/list-channels/)

```text
双方协商支持的通道类型
  → 用对应funding / commitment格式开新通道
  → 对应签名、fee与链上关闭路径
  → 生命周期、恢复和watchtower能力验收
```

Taproot Assets 的专门文档进一步说明 tapd、lnd、litd 的职责与集成模式，资产通道可以有额外协议 / 软件要求。它不是“启用 Taproot 后 Bitcoin 所有账户自然拥有 ERC-20”。[Taproot Assets Channels](https://docs.lightning.engineering/lightning-network-tools/taproot-assets/taproot-assets-channels)

本节只说明当前一方实现的明确能力。没有声称所有 Lightning 实现、对等方或 watchtower 已支持，也没有把 PTLC、通道工厂或其他未来研究当成现行默认。

## 9. 迁移验收与自测

| 改动 | 最小验收 |
| --- | --- |
| MuSig2实现更新 | 固定BIP327版本、向量、nonce消费和崩溃恢复、tweak |
| Descriptor / watch-only | 旧输出可发现、公钥和脚本一致、没有导出私钥 |
| PSBT v2 / Taproot字段 | parser-signer-finalizer交叉测试，错误找零 / 字段缺失拒绝 |
| cluster mempool / RBF | 依赖图、限额、chunks、替换fee与目标节点policy |
| 新RPC / 字段 | 运行版本 / schema、optional字段、旧bip125字段不作为唯一判断 |
| Testnet4 | genesis识别、余额独立、难度例外、旧服务network映射 |
| Taproot通道 | 双方feature协商、正常关闭、异常关闭、恢复和tower覆盖 |

自测：

- 为什么软件升级可以改变中继，却不能随意改变有效链规则？
- 为什么 `v2 PSBT` 不等于 `Taproot PSBT`？
- 为什么MuSig2正常路径失去一方后，不能临时降低签名门槛？
- 为什么Testnet4的难度算法细节不能复制成主网算法？

所有来源按2026-10-29核验，未来实施须绑定实际客户端、库、设备与RPC版本。本次仅文档研究，未把旧Core审计基线替换成一次未执行的软件升级。
