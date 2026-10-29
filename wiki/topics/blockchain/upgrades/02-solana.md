# Solana 新版学习章：从 PoH / TowerBFT 到 Alpenglow

- 核验日：**2026-10-29，北京时间（UTC+8）**。
- 前置阅读：[生态章](../chapters/04-ecosystem.md)、[钱包工程章](../chapters/05-wallet-engineering.md)、[二次复核](../notes/follow-up-verification.md)。
- 范围：英文官方工程文档、规范与发布源码的文档研究；没有连接钱包、调用链上 RPC、查询 feature gate、启动节点或测试真实资源。
- 读完应能区分执行与共识，解释 certificate，设计不会因候选分支、乱序通知或过期重试而重复付款的消费者。

## 1. 先锁定现状，再学习旧模型

当前[英文 Alpenglow 页](https://solana.com/upgrades/alpenglow)标记 **Updated October 2026**，明确声明主网已上线：epoch **1064** 于 **2026-10-21 约 13:36 UTC，即北京时间约 21:36** 开始；Votor 随 Agave 4.3 启用，Rotor 尚未排期。这是官方状态声明，不是本章独立验证主网运行的结果。

旧模型可拆成三件事：

1. **PoH 提供顺序与节奏。** 顺序哈希及 tick 帮助表达交易历史和 slot 边界；它不是“执行成功即最终确认”的证明。
2. **TowerBFT 决定分支与最终性。** 验证者用链上 vote transactions 投票，通过 lockout 累积形成确认；旧 `confirmed` 是乐观超多数确认，旧 `finalized` 还要有后续确认块。
3. **SVM 执行程序、改变账户状态。** 执行结果与网络是否最终接受这个分支，是两个问题。旧 commitment 表具体列出 `finalized` 所需的 **31+ 个后续 confirmed blocks**，不要把“约 32 slots / 12.8 秒”当成永恒时间常数。[旧 PoH 说明，仅用于历史模型](https://solana.com/developers/cookbook/transactions/confirmation)；[Anza 分时期 commitment 表](https://docs.anza.xyz/consensus/commitments)。

为什么换？[SIMD-0326](https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0326-alpenglow.md)指出旧设计最终性慢、共识通信及链上验签开销大，并提出可证明安全性与活性的替代设计。改动是把“为共识投票”从普通交易执行路径移出，而不是废除 PoS 权重，也不是换掉程序运行时。该规范页仍标 `Review`，其中经济参数也有旧描述；它用于解释设计，**不能单凭其状态栏判断今天是否上线**。

## 2. 新组件与 stake 阈值：不是“60% 节点举手”

**Votor**负责投票、出块相关决策与最终性；验证者直接发送共识消息。Votor 替换 TowerBFT，PoH 不再承担旧式出块 tick / pacing；共识投票也不再作为普通链上 vote transactions，原来包含 votes 的总 TPS 因而不能跨升级直接比较。[当前替换范围](https://solana.com/upgrades/alpenglow)；[Triton TPS 迁移口径](https://blog.triton.one/alpenglow-migration-avoid-the-misinformation/)。

**Pool**管理看到的 votes / certificates；**Blokstor**承担协议数据存储职责。Certificate 是按 stake 权重形成的投票证据，可用 **BLS 聚合签名与签名者 bitmap**表达；应核验消息类型、目标及对应验证者密钥，不能只信任 leader 发来一个百分比。[设计术语与投票规则](https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0326-alpenglow.md)；[Agave 4.3.2 certificate 定义](https://docs.rs/agave-votor-messages/4.3.2/src/agave_votor_messages/certificate.rs.html)。

第一轮对及时收到、满足父块证据条件的有效候选投 **Notarization**，否则按本地超时规则投 **Skip**；第二轮根据已有证据投 **Final**，或在协议的 safe-to-notar / safe-to-skip 条件下投 fallback。第二轮不是随意重新选一票，也不是客户端再等一个固定时长。[SIMD 两轮规则](https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0326-alpenglow.md)。

以下是[新版英文页的阈值说明](https://solana.com/upgrades/alpenglow)，并与[4.3.2 的 `CertificateType::threshold()`](https://docs.rs/agave-votor-messages/4.3.2/src/agave_votor_messages/certificate.rs.html)中的 **60 / 80** 常量交叉核对：

| 证书 | stake 权重口径 | 意义 |
| --- | --- | --- |
| Fast finalization | 第一轮 notarize ≥80% | 一轮直接最终确认 |
| Notarization | notarize ≥60%；未到 80% 时走慢路径 | 公证，不单独等于最终确认 |
| Finalization | 第二轮 finalize ≥60% | 与该候选的 notarization certificate 一起构成慢路径最终性 |
| Notarization fallback | notarize / notarize-fallback 合计 ≥60% | fallback 证据，不自动等于 finalized |
| Skip | skip / skip-fallback 合计 ≥60% | 决定跳过，不是付款成功证据 |

表中 `≥`沿用官网概览；常量定义本身不提供完整整数边界算法。本章不实现共识验证器，教学例也避开恰好 60% / 80% 的边界。实现级验收必须进一步核对所用版本的 stake 比较与签名验证，不能用浮点四舍五入；Agave 的[精确 Fraction 类型及精度测试](https://docs.rs/agave-votor-messages/4.3.2/src/agave_votor_messages/fraction.rs.html)专门处理这个问题。

“**20% 恶意 + 20% 离线**”区分拜占庭行为与不响应，不是允许 40% 恶意。直观上，一轮路径需要更强的投票覆盖；两轮则用额外的证据与投票约束，在更多节点不可达时推进。安全性依赖故障假设和诚实投票规则，活性还依赖部分同步条件。[规范的安全取舍](https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0326-alpenglow.md)。

保留一个解释边界：英文升级页把两个 60% 候选不可能同时成功简写为“需要 120% stake”。**不能把这句算术当完整安全证明**：投票集合可能重叠，真正的论证还涉及不重复投票、恶意权重与协议规则。本章不冒充已复现白皮书证明；Anza 白皮书入口本次未能取到正文。

**Rotor 仍属未来阶段。** 它计划把 Turbine 的树状传播改为单层 relay，保留纠删码和 stake 调整带宽的思路；当前不能把 Rotor 的预期传播收益算成已上线收益。SVM、程序与账户执行不因 Votor 被替换；v1 格式等是另一个升级轴。[Votor / Rotor 当前分期](https://solana.com/upgrades/alpenglow)。

## 3. Slot、block、bank：索引身份为何必须重建

| 名词 | 本章中的含义 | 不能作的等同 |
| --- | --- | --- |
| slot | 预定 leader 的网络时间窗口 | 不保证有成功区块 |
| block | 该窗口中的候选交易集合及协议数据 | 不等于全局唯一 slot |
| bank | 节点为候选执行维护的具体状态实例 | `bank_id` 不等于 blockhash 或 bank hash |

同 slot 多候选在旧模型也可能出现。新版页区分：**Agave 4.3** 中可由 leader equivocation 产生；**4.4 的 fast leader handoff 尚属后续功能**，允许预期父节点被 skip 后重启候选。不能因为 4.3 已有 `bank_id` / marker 类型，就声称 4.4 的生产行为已激活。[候选与版本边界](https://solana.com/upgrades/alpenglow)。

Geyser 是节点回调接口；Yellowstone gRPC 是将这些数据提供给消费者的服务。4.3.2 提供 `update_account_for_bank`、`notify_transaction_for_bank`、`notify_entry_for_bank`、`notify_block_metadata_for_bank` 和 `update_bank_status`。自己拼块时应按 **连接会话 + slot + bank_id** 分桶，而非仅 slot。[固定版本 Geyser 接口](https://docs.rs/agave-geyser-plugin-interface/4.3.2/src/agave_geyser_plugin_interface/geyser_plugin_interface.rs.html)。

`bank_id` 是每个节点自己的计数身份：同一块在供应商 A 和 B 上可分别是 7、12；重连不能假定仍是同一命名空间。跨供应商核对使用 blockhash，保留各自缓冲区。快照账户 `is_startup=true`、尚无 bank 的 slot 通知、deshred 数据不可强行补一个 bank ID；deshred 表示执行前观察，不是收款成功。[Triton bank_id 表与跨供应商规则](https://blog.triton.one/alpenglow-and-your-triton-stack-what-to-update-before-mainnet/)。

### UpdateParent 与事件顺序

`UpdateParentV1`携带新的 parent slot / block ID。Geyser 的 `notify_entry_update_parent`报告 **cleared_bank_id**；替代 bank 的 ID 由后续 `CreatedBank`另报。工程上应撤销旧 bank 的暂存视图，并按替代 bank 重建，而不是原地改 parent 后保留旧付款事件。[Agave marker 原始定义](https://docs.rs/solana-entry/4.3.2/src/solana_entry/block_component.rs.html)；[4.3.2 回调契约](https://docs.rs/agave-geyser-plugin-interface/4.3.2/src/agave_geyser_plugin_interface/geyser_plugin_interface.rs.html)。

消费者至少处理以下顺序边界：

- 同 bank 内交易按 **transaction index**排序；账户多次写入按 **write_version**处理，不能拿到达先后当执行顺序。
- Anza 说明从 Agave 3.0 起 transaction 通知在 `Processed`前发送，但 `Confirmed`和 `Processed`仍可任意先后；这是节点回调关系，不是跨连接全局有序保证。[回调时序文档](https://docs.anza.xyz/validator/geyser)。
- `UpdateParent`回调可与 entry 通知竞争，必须用 cleared bank ID 对账；deshred 的 UpdateParent 通知只保证先于其 FEC 边界起始数据集的交易通知。Footer 也只承诺相对 entry 的顺序。[4.3.2 明确契约](https://docs.rs/agave-geyser-plugin-interface/4.3.2/src/agave_geyser_plugin_interface/geyser_plugin_interface.rs.html)。
- `FirstShredReceived`、`Completed`和 `Dead`属于非 bank-scoped 回调；不要把 `Completed`误当 finalized。[接口中的状态分类](https://docs.rs/agave-geyser-plugin-interface/4.3.2/src/agave_geyser_plugin_interface/geyser_plugin_interface.rs.html)。

Footer 需显式启用，certificate 字段可为空；其中 `block_final_cert`有**自己的 slot / block_id**，可能证明较早的块，而非承载 footer 的块。空证书不是未最终确认的充分证据，拿错证明对象也不能结算。[footer 结构与 fast / slow 证书转换](https://docs.rs/solana-entry/4.3.2/src/solana_entry/block_component.rs.html)。

## 4. JSON-RPC：接口可继续用，含义不能照旧猜

Alpenglow 本身不要求重写普通 `sendTransaction`、账户读取、程序交互、priority fee / tip 路径；Triton 明确普通 RPC polling / WebSocket 在切换日不新增必要字段，`getAccountInfo`、`getProgramAccounts`、DAS 响应不因共识替换而改。但这**不等于所有方法永不新增字段**：vote account 的解析数据新增可空 `blsPubkeyCompressed`，还有用于识别迁移的新 `getAgGenesisCert`。[Triton 按产品说明](https://blog.triton.one/alpenglow-and-your-triton-stack-what-to-update-before-mainnet/)。

当前 Alpenglow 下：

- `processed`：只证明交易在某个 bank 执行过。
- `confirmed`与 `finalized`：语义等价，表示进入永久账本；**notarization 的 60% 不是新的 RPC commitment**。
- 语义等价不承诺通知同时送达，也不保证订阅了两种标签就只收到一份。账务应按事件幂等，而非标签各入一次账。[Anza 新表](https://docs.anza.xyz/consensus/commitments)；[Triton 双标签突发提示](https://blog.triton.one/alpenglow-and-your-triton-stack-what-to-update-before-mainnet/)。

迁移验收可按官方文档设计 `getAgGenesisCert`能力检查：`null`、返回证书、`Method not found`分别表示尚未迁移、已迁移、节点不认识该接口；**最后一种不能当作“没迁移”**。本章没有执行这项检查，也不凭日期推断每个供应商端点。[迁移指南](https://blog.triton.one/alpenglow-migration-avoid-the-misinformation/)。

约 **150ms 是目标 finality，不是付款 SLA，也不是 slot 时长**。未获准直接参与 Votor 的 RPC 节点，可能经后续 block footer 才知道最终性；跳块、传播、索引、网络和业务处理都会增加用户可见延迟。[Anza 共识信息三种接收路径](https://docs.anza.xyz/consensus/alpenglow)。

## 5. 钱包需要一起验收的独立升级

**Slot 已缩短到 200ms。** 官方专页称四阶段完成，最后一步在 **2026-10-09、epoch 1053**生效；这独立于 Alpenglow。旧 `slot × 400ms`倒计时失效，Clock 也不是高精度墙钟：Alpenglow 后 `unix_timestamp`近似父块结束时刻，仍是整秒分辨率。[Reduced Slot Times](https://solana.com/upgrades/reduced-slot-times)；[Anza Clock 语义](https://docs.anza.xyz/consensus/alpenglow)。

**v1 已上线，但不要把所有旧交易都放宽到 4096 字节。** 官方称 `txv1`于 **2026-09-15、epoch 1035**启用；legacy / v0 继续可用，仍为 **1232 字节**，v1 为 **4096 字节、64 个 inline accounts、无 ALT**。v1 首字节 `0x81`、签名在末尾，不能当 v0 换个版本号。[上线证据](https://solana.com/upgrades/larger-transaction-sizes)；[格式比较](https://solana.com/docs/core/transactions/versioned-transactions)。

钱包和 scanner 必须能读 v1，即使自己仍发送 v0：支持后在 `getBlock` / `getTransaction`传整数 `maxSupportedTransactionVersion: 1`，大交易采用 base64；不支持时明确失败，不能当空块。v1 的 CU limit、loaded accounts data size limit 要显式设置；ComputeBudget 指令不再配置它们。优先费在 message config 中是 **lamports 总额**，不是 micro-lamports/CU。[v1 构造与读取迁移](https://solana.com/docs/core/transactions/versioned-transactions)。

费用模型仍分基础费与优先费；当前基础费为每个计费签名 **5000 lamports**，已被执行的失败交易仍收手续费。legacy / v0 优先费为 `ceil(CU_price × CU_limit / 1,000,000)`；v1 直接配置总额。`getFeeForMessage`页面目前只明示 legacy / v0，不能据此保证某端点支持 v1 估费。[费用公式](https://solana.com/docs/core/fees/fee-structure)；[估费接口支持范围](https://solana.com/docs/rpc/http/getfeeformessage)。

**过期按高度，不按硬编码 150 slots 或 30 秒。** 保存 `getLatestBlockhash`返回的 blockhash 与 **lastValidBlockHeight**，比较相同 commitment 下的 `getBlockHeight`；超过最后有效高度后停止重播。Slot 可以被跳过，slot 编号、block height 与时间不是同一个轴。200ms 页面写约 30 秒只是时序估计，还要扣除取到 hash 时已消耗的窗口。[blockhash 接口](https://solana.com/docs/rpc/http/getlatestblockhash)；[height 接口](https://solana.com/docs/rpc/http/getblockheight)；[官方“超过最后有效高度”判断](https://solana.com/developers/cookbook/transactions/confirmation)。

## 6. 完整付款与事件消费流程

以下是基于接口契约的**工程建议**，不是本次完成的生产验收。以普通 recent-blockhash 转账为例：

1. **创建业务请求。** 保存 network、收款对象、最小单位整数金额、requestId；预留余额。一次业务请求可以有多次尝试，但不能各付款一次。
2. **构造消息。** 选已获 SDK / 签名器支持的格式，取 fresh blockhash 和 lastValidBlockHeight，配置费用 / 资源，完成模拟及用户授权。模拟成功不保证随后执行成功。
3. **保存签名后再广播。** 持久化 attemptId、原始字节、第一签名及有效高度。`sendTransaction`返回第一签名只表示 RPC 接收，不证明包含或最终成功。[广播契约](https://solana.com/docs/rpc/http/sendtransaction)。
4. **处理广播不确定。** 超时进入 `BROADCAST_UNKNOWN`；有效期内可重播同一字节并查旧签名，不能马上改 blockhash 签第二笔。
5. **接收执行观察。** Geyser / Yellowstone 分连接、分 bank 暂存 transaction、account、meta 与状态；deshred 不触发入账。遇 UpdateParent 清理旧观察；账户快照只用于恢复，不生成新充值。
6. **匹配最终候选与完整数据。** 即使 finality 通知先到，也等待该 bank 的执行数据足够完整；全量拼块可用 metadata 的执行交易数，过滤流不能要求“收到全部交易”。不混合不同 bank 的账户差额。
7. **核对实际效果后结算。** 用 finalized 状态及 `getTransaction`中的 `meta.err`、实际费用、目标账户 / 资产变化交叉核验。最终确认的失败交易是“失败结果已确定”，不是付款成功。[状态查询](https://solana.com/docs/rpc/http/getsignaturestatuses)；[执行结果](https://solana.com/docs/rpc/http/gettransaction)。
8. **恢复和对账。** 断流补扫、重叠去重；状态返回 `null`可能只是近期缓存未覆盖，必要时验收历史查询。确认旧尝试未成功且已过期后，才为同一 request 创建新 attempt；改变消息必须重新授权签名。[状态缓存范围](https://solana.com/docs/rpc/http/getsignaturestatuses)。

建议把“观察身份”和“账务身份”分开：

```text
观察桶：(network, connectionSession, slot, bank_id)
事件身份：(network, signature, instructionPath, asset, recipient)
结算条件：最终候选 + 执行成功 + 效果匹配 + 事件尚未入账
```

`instructionPath`是业务定义的顶层 / 内层指令定位，不是新 RPC 字段。跨供应商重播、confirmed / finalized 双通知、进程重启，都只推进同一结算记录。

## 7. 定量教学例：全部是假设，不是真实观测

- **投票例：** 假设总有效 stake 为 1000 权重单位。810 单位第一轮 notarize 可走一轮快路径；650 单位 notarize 不足以快确认，若第二轮再形成 610 单位 finalize 证据，与 notarization certificate 配合走慢路径。只有 590 单位则不能称已达到 60% 证书阈值；510 个小节点也不等于 51% stake。
- **乱序例：** slot 900 中 bank 7 被清理、bank 8 成为替代候选；bank 7 的迟到交易通知不得混入 bank 8。bank 8 的 `Confirmed`先于 `Processed`到达时可先标记最终性，但在执行数据及效果核验前不入账。另一供应商 bank 12 只有匹配 blockhash 后才能对应 bank 8。
- **有效期例：** 返回 lastValidBlockHeight=10150；height=10150 尚未因“超过高度”判过期，10151 才超过。无论当前 slot 编号是多少，都不算 `slot+150`。假设还剩 120 个有效出块高度且连续按 200ms 出块，约为 24 秒；这是预算估计，不是倒计时保证。
- **费用例：** 一项普通计费签名、legacy / v0 请求 200000 CU，价格 10000 micro-lamports/CU，则优先费 2000、合计 7000 lamports。改用 v1 时应直接配置优先费 2000，不能继续把 10000 当总额。上述公式来源见[费用文档](https://solana.com/docs/core/fees/fee-structure)。
- **TPS 例：** 假设旧样本 1200 笔中 800 是 votes，新样本同样 400 笔用户交易却没有 votes；“总交易数下降”不能推出用户活动下降。报表须标明总量 / non-vote、成功 / 失败、时间区间及升级边界。[Triton 计数口径提示](https://blog.triton.one/alpenglow-migration-avoid-the-misinformation/)。

## 8. 迁移测试矩阵与客户端边界

以下都是**待执行的离线 / 授权测试用例**，本章未运行：

| 输入或故障 | 必须验收的结果 |
| --- | --- |
| 同 slot 两候选，最终性先于执行通知 | 分 bank 暂存；只结算最终候选且数据完整的成功效果 |
| UpdateParent 与旧 entry / transaction 竞争 | cleared bank 隔离；CreatedBank 替代身份不继承旧付款观察 |
| 跨供应商 bank_id 不同；断连重放 | 分会话缓冲、按 blockhash 核对；账务只记一次 |
| startup account、无 bank_id、deshred | 不伪造 bank ID，不把快照 / 执行前数据当充值 |
| confirmed / finalized 重复；footer 无证书或指向旧块 | 幂等；不因空证书否定状态，不用错证明对象 |
| 旧 scanner 遇 v1；未知 config；只读 ComputeBudget | 显式拒绝不支持格式或正确解析；不静默空块 / 零费用 |
| 广播超时、签名长耗时、height 超限 | 先核查旧尝试；有效期内重播同字节，过期后受控重建 |
| finalized 但 meta.err 非空；账户效果不符 | 失败 / 异常分支与费用单独记账，不完成付款 |
| TPS 去掉 votes；200ms 增加摄入频率 | 重设统计基线与背压容量，不能靠旧总量报警 |

**Firedancer / Frankendancer 的限制单列：** 英文官方页明确它们**未受支持参与这次迁移**，迁移要求使用 Agave-based **v4.3.2**（列出 Agave、Jito-Solana、Harmonic Salsa）。这是特定升级窗口的客户端兼容要求，**不是永远不能支持 Alpenglow**，也不证明相关生态服务全部不可用；未来恢复须另查正式兼容声明。[本次迁移要求](https://solana.com/upgrades/alpenglow)。

## 9. 收益、限制与自测

收益主要是缩短协议最终性、减少链上投票执行与流数据负担，让钱包不必照搬旧 32-slot 等待。限制是：共识升级不能保证业务成功、交易纳入时延、RPC 新鲜度或消费完整性；Rotor 尚未上线，150ms 不可签成固定 SLA，stake 分布和网络拓扑也影响快 / 慢路径。[最终性目标与执行边界](https://solana.com/upgrades/alpenglow)；[RPC 信息接收延迟](https://docs.anza.xyz/consensus/alpenglow)。

自测（括号内是答题检查点）：

1. 为什么 650/1000 notarize 还不能入账？（公证不是最终证书，且仍要执行效果。）
2. 为什么 20+20 不是 40% 恶意容忍？（故障类型、诚实规则及活性假设不同。）
3. 同 slot 两个 bank 如何避免重复充值？（候选隔离、最终选择、业务事件幂等。）
4. 为什么 footer 有证书也不能直接认定当前块最终？（核对证书自己的 slot / block_id。）
5. 为什么 200ms、150ms、约 30 秒是三种不同指标？（slot 节奏、协议最终性目标、hash 时间预算。）
6. 自己只发 v0，为什么仍要升级 scanner？（别人可发 v1；旧读取器可能整体失败。）
7. 为什么 height 超限还要查旧签名？（阻止未来纳入不等于否定过去已经成功。）

## 10. 来源、版本、状态证据与保留差异

本章只使用 Solana Foundation、Anza / Agave、Triton 的原始文档或发布源码；docs.rs 链接是 **Agave 所属 crate 的固定 4.3.2 原始源码发布视图**，不是第三方解说。没有用旧译本补新版英文正文。

| 本章局部编号 | 来源 / 版本 | 支撑范围及状态 |
| --- | --- | --- |
| SOL-U1 | [Alpenglow 英文页](https://solana.com/upgrades/alpenglow)，Updated October 2026 | epoch 1064 上线声明、Votor 已启用 / Rotor 未排期、4.3 / 4.4 边界、迁移客户端 |
| SOL-U2 | [SIMD-0326](https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0326-alpenglow.md)，当前页面仍标 Review | 动机、两轮规则、慢路径需配对证书、安全模型；不作上线或当前经济参数证据 |
| SOL-U3 | [certificate.rs](https://docs.rs/agave-votor-messages/4.3.2/src/agave_votor_messages/certificate.rs.html)、[fraction.rs](https://docs.rs/agave-votor-messages/4.3.2/src/agave_votor_messages/fraction.rs.html)，4.3.2 | 60 / 80 常量、签名与 bitmap、精确权重类型；未完成整个比较器审计 |
| SOL-U4 | [Anza Commitments](https://docs.anza.xyz/consensus/commitments) | 分开列出 TowerBFT 历史与 Alpenglow 当前语义 |
| SOL-U5 | [Geyser 接口源码](https://docs.rs/agave-geyser-plugin-interface/4.3.2/src/agave_geyser_plugin_interface/geyser_plugin_interface.rs.html)，4.3.2 | bank-scoped 回调、UpdateParent、footer 顺序；源码存在不等于 feature 已激活 |
| SOL-U6 | [block_component.rs](https://docs.rs/solana-entry/4.3.2/src/solana_entry/block_component.rs.html)，4.3.2 | marker / footer / 证书对象与 fast / slow 解码 |
| SOL-U7 | [Triton stack 指南](https://blog.triton.one/alpenglow-and-your-triton-stack-what-to-update-before-mainnet/)，Updated 20 Oct 2026 | Yellowstone 字段、跨供应商身份、普通 RPC 边界；保留部分预上线文字 |
| SOL-U8 | [Anza Geyser 文档](https://docs.anza.xyz/validator/geyser) | 回调时序；示例仍含旧 slot-only 接口，不能据此忽略新版 bank_id |
| SOL-U9 | [Anza Alpenglow](https://docs.anza.xyz/consensus/alpenglow) | RPC 接收共识信息路径、Clock、footer；开头仍写 upcoming |
| SOL-U10 | [Reduced Slot Times](https://solana.com/upgrades/reduced-slot-times)，Updated October 2026 | 200ms、epoch 1053 最后阶段、时间预算；非本次测量 |
| SOL-U11 | [Larger Transaction Sizes](https://solana.com/upgrades/larger-transaction-sizes)，Updated September 2026 | txv1 于 epoch 1035 启用；4096 仅适用于 v1 |
| SOL-U12 | [Versioned Transactions](https://solana.com/docs/core/transactions/versioned-transactions) | 格式、64 账户、config、读写兼容；96 账户不作为已生效结论 |
| SOL-U13 | [Fee Structure](https://solana.com/docs/core/fees/fee-structure) | 费用与 v1 总额单位，失败费用 |
| SOL-U14 | [getLatestBlockhash](https://solana.com/docs/rpc/http/getlatestblockhash)、[getBlockHeight](https://solana.com/docs/rpc/http/getblockheight) | 有效高度与 commitment 接口 |
| SOL-U15 | [sendTransaction](https://solana.com/docs/rpc/http/sendtransaction)、[getSignatureStatuses](https://solana.com/docs/rpc/http/getsignaturestatuses)、[getTransaction](https://solana.com/docs/rpc/http/gettransaction) | 接收 / 缓存 / 执行结果；不证明本次任何付款 |
| SOL-U16 | [Confirmation & Expiration](https://solana.com/developers/cookbook/transactions/confirmation) | 仅采用高度判过期及历史模型；旧 PoH / 400ms / 32-slot 当前建议不沿用 |
| SOL-U17 | [Transactions 总览](https://solana.com/docs/core/transactions) | 保留“150 slots”和“96 for v1”与细节页的冲突 |
| SOL-U18 | [getFeeForMessage](https://solana.com/docs/rpc/http/getfeeformessage) | 当前页面只明确 legacy / v0，未确认 v1 支持 |
| SOL-U19 | [Triton migration 指南](https://blog.triton.one/alpenglow-migration-avoid-the-misinformation/)，Updated 20 Oct 2026 | 迁移识别与 TPS；是预演 / 预期，不是事后实测日志 |

需主线程保留、而非悄悄拼接的差异：

1. **上线与时点：** SOL-U1 已写 live，SOL-U9 开头仍 upcoming；SOL-U19 的 epoch 开始时间约 13:20 UTC，与 SOL-U1 的约 13:36 UTC 不同，且还描述激活后的倒计时。采用新版官方页的上线声明，不断言上述时刻就是首个 Votor 块的独立实测时间。
2. **Slot：** SOL-U7 FAQ 仍写 250ms、200ms 待推出；SOL-U10 已明确最后阶段完成。本文现状用 200ms，保留旧指南差异。
3. **过期：** SOL-U17 写 150 slots，SOL-U10 写 150 blocks；SOL-U16 还保留旧时间与 PoH 解释。钱包以 RPC 返回的 lastValidBlockHeight 为准，不拼成固定 30 秒保证。
4. **账户数：** SOL-U17 总览列“96 for v1 with SIMD-0596”，SOL-U11 / SOL-U12 仍以 64 为现行、96 为 draft。本章不认定 96 已生效，需进一步查正式激活证据。
5. **JSON-RPC 兼容：** Alpenglow 保持常用交易 / 账户接口，不消除独立 v1 升级的解码、版本参数和估费兼容要求；也不能把 `confirmed`未来可能移除的供应商建议写成今日已删除。

主线程后续可在生态章补“Votor 已启用、Rotor 未排期、slot 缩短是独立升级”，在钱包章补“bank-aware 消费、v1 读取、按有效高度过期”；本次严格只新增本文件，未改动那些章节。
