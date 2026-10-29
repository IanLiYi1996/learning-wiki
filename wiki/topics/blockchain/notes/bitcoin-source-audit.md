# Bitcoin 协议一手来源审计：PPT p4–22

研究日期：2026-10-29。用途：为私有 learning-wiki 主文提供可复核的协议纠偏与工程验收点。

本 sidecar 按主线程给定的页码和疑点核验，未独立读取《穿透区块链-原理生态与钱包工程-v3.pptx》，因此“应改如何写”是建议替换文本，不冒充 PPT 原句。最终逐页归属由主线程对照原文件确认。本文件采用 research 技能要求的一手证据追溯方式：读取规范与源码，再记录结论，不大量摘抄原文。

范围与版本：难度调整默认指 Bitcoin 主网；交易规则指相应软分叉激活后的规则；Lightning 指所引 BOLT 的 HTLC／惩罚式通道，不泛化到所有研究中通道设计。Bitcoin Core 选择 v30.0 作为可复现的实现审计基线，不声称它是研究日最新版本。BIP 与 BOLT 使用研究时解析出的固定提交：

- Core v30.0：`d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3`。
- bitcoin/bips：`5aadddb511a5dcfe4599531bd8ae5e5b96d0f793`。
- lightning/bolts：`191462825ae341f0a27098765c075f01ca9bc6c2`。

规范决定协议语义；源码验证实现细节；开发者指南补充术语；Lightning Labs 文档只用于其 watchtower 功能边界。下文的“工程推论”与测试设计不是声称已经执行的实验结果。

## 1. 难度与目标值：p7 的比例写反了

事实：工作量证明要求区块头哈希数值不大于目标值 `T`。`nBits` 编码的是 target，不是 difficulty。设固定难度一目标为 `T₁`，则 `D = T₁ / T`；target 越小，difficulty 越大。主网重定向可概括为：

```text
E = 2016 × 600 = 1,209,600 秒
A = t[h − 1] − t[h − 2016]       # h 是新周期第一块的高度
A* = clamp(A, E/4, 4E)
Tnew = min(powLimit, floor(Told × A* / E))
Dnew ≈ Dold × E / A*            # 忽略整数截断、compact 舍入和 powLimit 截顶
```

这里选择的是上一周期 2016 个区块的首尾时间戳，首尾之间只有 2015 个间隔；分母仍是 `2016 × 600`，不可“修正”为 `2015 × 600`。按区块高度每 2016 块调整，不是墙钟恰好过两周就调整。时间跨度限幅为 3.5–56 天；再施加 `powLimit`，最后编码为 compact。Testnet 的最小难度例外、Testnet4 的 BIP94 分支及 regtest 的免重定向参数不能混作主网规则。

PPT 页码：p7。

应改如何写：新 target = 旧 target × 实际跨度／预期跨度；新 difficulty 近似 = 旧 difficulty × 预期跨度／实际跨度，并注明限幅与整数编码。若上一周期只用 7 天，target 约减半、difficulty 约翻倍。注明“2016 块，首尾 2015 个时间间隔”。

一手来源：S01 的 [`GetNextWorkRequired`／`CalculateNextWorkRequired`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/pow.cpp#L14-L85)；[`CMainParams` 的时间及网络参数](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/kernel/chainparams.cpp#L100-L105)。

## 2. 链选择：最大累计工作量，不是节点投票或单纯最多块

事实：在满足共识有效性条件的链之间，节点按累计工作量选择活动链。Core 对单块记账的工作量是 `floor(2^256 / (T + 1))`，累计值是父块累计值加单块工作量；它不是记录矿工实际试了多少次哈希。块数／高度只是同难度条件下的近似代理。相同工作量时，Core 还有本地接收顺序等平局处理，不能理解成全网立即达成唯一结果。

PPT 页码：p4–6。

应改如何写：节点先验证，再在有效候选链中选择最大累计工作量链；“最长链”仅作历史简称，须注明并非简单比较区块数量，也非一节点一票。

一手来源：S01 的 [`GetBlockProof`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/chain.cpp#L126-L139)、[`CBlockIndexWorkComparator`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/node/blockstorage.cpp#L158-L175)、[`nChainWork` 累加](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/node/blockstorage.cpp#L223-L230)及 [`FindMostWorkChain`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/validation.cpp#L3213-L3274)。

## 3. stale 与 orphan：不要把竞争失败与缺少父块混成一件事

事实：stale block 通常指父块已知、原本有效，但所属分支未成为当前活动链的区块。严格意义的 orphan block 指本节点尚不知道父块的区块；这首先是节点知识／接收顺序状态，不等于竞争失败。历史材料常把 stale 也叫 orphan，应明确本笔记的用词。stale 的身份可以随重组变化；交易可能重新入链，不能说“块变 stale，里面交易便永久无效”。

PPT 页码：p4–6。

应改如何写：同高度竞争中未进入活动链者称 stale；父块未知者称 orphan。分叉后重新确定活动链，并重新评估交易确认状态，不把两类统称“孤块”。

一手来源：S02 的 [Block Height And Forking](https://developer.bitcoin.org/devguide/block_chain.html#block-height-and-forking)，正文含 stale 与 true orphan 的专门辨析；S01 的 [`AcceptBlockHeader`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/validation.cpp#L4311-L4324)区分 `prev-blk-not-found` 与 `bad-prevblk`。

## 4. 51% 能力边界：可重组／双花／审查，不能绕过签名和发行规则

事实：持续算力优势有利于攻击者建立工作量更高的有效分支，重组交易历史、撤回自己已支付的交易后作冲突支付，或通过持续排除与重组实现审查。它不使有限时间内任意深度重组必然成功；低于 50% 也不是双花概率为零。攻击者不能仅凭算力伪造他人授权、任意转走他人 UTXO、超额发行或让遵守原规则的全节点接受非法区块。

PPT 页码：p4–6。

应改如何写：多数算力攻击主要影响有效交易的排序、确认稳定性与可用性，不自动改变签名、UTXO 和发行共识规则。确认是概率性保证；攻击能力还受持续时间、成本与网络条件影响。

一手来源：S03 的 [白皮书 §11 Calculations](https://bitcoin.org/bitcoin.pdf)给出追赶概率模型并限制攻击范围；S01 的 [`ConnectBlock` 中发行及脚本检查](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/validation.cpp#L2676-L2689)拒绝 `bad-cb-amount` 和脚本验证失败。审查的持续性描述是结合最大工作量链选择作出的工程推论。

## 5. txid／wtxid：双 SHA-256 的输入是二进制序列化

事实：`txid = SHA256(SHA256(base_serialization))`；有 witness 时，`wtxid` 对含 witness 的扩展序列化做相同双哈希。base 序列化仍含每个输入的 scriptSig；它排除 marker、flag 和 witness。没有 witness 的交易使用传统序列化，`wtxid = txid`。不能对 JSON、文本十六进制字符串或“签名前交易”直接计算 txid。RPC 显示的哈希十六进制与内部哈希字节顺序也不能混用。

PPT 页码：p9–14。

应改如何写：TXID 是传统二进制交易序列化的双 SHA-256；WTXID 是含 witness 序列化的双 SHA-256。明确“交易标识符”与签名所用的 sighash 不同。

一手来源：S04 [Transaction ID](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0141.mediawiki#transaction-id)；S01 的 [`ComputeHash`／`ComputeWitnessHash`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/primitives/transaction.cpp#L81-L93)、[`HashWriter::GetHash`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/hash.h#L111-L120)。S02 分叉段落另说明区块哈希的展示字节序惯例。

## 6. SegWit 保留 scriptSig；混合输入不自动获得完整 txid 稳定性

事实：所有输入仍有 scriptSig 字段。原生 witness 输入要求 scriptSig 为空；P2SH 包裹的 witness 输入要求它精确 push 对应 redeemScript；legacy 输入仍沿用原有解锁数据。一笔交易可以混合 legacy 与 witness 输入，因此只要 legacy 的非 witness 部分仍可变，整笔 txid 仍可能受影响。

“不可延展”应限定为 txid 的非自愿可延展性及相应签名条件，不能泛指任意脚本、wtxid 或签名者主动重签均不可变化。legacy 的某些等价 scriptSig 变体会被标准中继策略拒绝，但不能据此宣称共识层不存在它们。

PPT 页码：p9–14。

应改如何写：SegWit 将 witness 输入的签名／解锁材料移出 txid 所覆盖的数据，保留 scriptSig 字段。讨论 txid 稳定性时检查全部输入类型与签名条件；不要写成“SegWit 交易删除了 scriptSig，所有可延展性都消失”。

一手来源：S04 的 [Witness program](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0141.mediawiki#witness-program)与 Motivation；S01 的 [`CTxIn` 及其序列化](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/primitives/transaction.h#L66-L72)、[`SerializeTransaction`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/primitives/transaction.h#L255-L283)、`VerifyScript` 的策略／共识标志。混合输入结论是上述序列化规则的直接推论。

## 7. witness 在各交易内部，不是整个区块末尾的集中签名区

事实：扩展格式的一笔交易依次编码 version、marker、flag、vin、vout、按输入顺序的 witness stacks、locktime。每个输入对应一个 stack；在含 witness 的混合交易中，非 witness 输入也占一个空 stack 编码。区块逐笔序列化交易，不是在全部交易后追加一个全区块 witness 区。

PPT 页码：p9–14。

应改如何写：区块由连续的交易构成，各 SegWit 交易在自身输出字段之后、locktime 之前编码各输入的 witness。图示必须画在交易层级；“从 txid 承诺中分离”不等于物理移至区块末尾。

一手来源：S04 Transaction ID；S01 [`SerializeTransaction`／`UnserializeTransaction`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/primitives/transaction.h#L195-L283)的 witness 循环位于输出与 locktime 之间。

## 8. witness commitment：准确公式、coinbase 零叶与承诺位置

事实：设 `H₂ = SHA256 ∘ SHA256`，`r` 是 coinbase 输入 witness 的单个 32 字节 reserved value：

```text
W = MerkleRoot(0x00…00[32 bytes], wtxid(tx₁), …, wtxid(txₙ))
C = H₂(W || r)                  # 原始字节拼接，不拼接显示 hex 文本
coinbase_output.scriptPubKey = 0x6a24aa21a9ed || C || optional_bytes
```

树内节点对左右子节点原始 32 字节值拼接做双 SHA-256；奇数层末项按 Bitcoin Merkle 规则复制。这里 coinbase 的叶值人为设为零，避免把承诺自身绕回树中；不是说 coinbase 实际计算的 wtxid／txid 是零。`r` 也不被规定必须为零。匹配输出至少 38 字节；存在多个匹配者时取最高输出索引。有 witness 数据必须有承诺；完全没有 witness 数据时承诺可省略。

PPT 页码：p9–14。

应改如何写：Coinbase 的 OP_RETURN 输出承诺“双 SHA-256(witness Merkle root ∥ 32 字节 reserved value)”。区块头仍是 txid Merkle root；通过 coinbase txid 间接承诺 witness，不是把 witness root 直接写进区块头。

一手来源：S04 [Commitment structure](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0141.mediawiki#commitment-structure)；S01 的 [`BlockWitnessMerkleRoot`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/consensus/merkle.cpp#L76-L85)、`ComputeMerkleRoot` 及 [`CheckWitnessMalleation`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/validation.cpp#L3960-L4007)。

## 9. Schnorr：新增于 Taproot，未全局替代 ECDSA

事实：BIP340 定义 Schnorr 签名；BIP341 引入 witness v1 的 Taproot 花费规则。Legacy 与 SegWit v0 的相应签名操作仍验证 ECDSA，不能因为协议支持 Taproot 就把已有输出改用 Schnorr。BIP340 签名本体为 64 字节；Taproot 交易中的非默认 sighash 签名可为 65 字节，最后一个字节是 sighash 类型。

PPT 页码：p15–19。

应改如何写：Taproot 为 Bitcoin 新增 BIP340 Schnorr 验证路径，与已有 ECDSA 路径并存。区分“64 字节签名本体”与“64／65 字节交易签名编码”，不要写“升级后全网签名统一改为 Schnorr”。

一手来源：S05 的 BIP340 Description／Specification；S06 的 [Taproot key path spending signature validation](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0341.mediawiki#taproot-key-path-spending-signature-validation)；S01 的 [`EvalChecksigPreTapscript`／`EvalChecksigTapscript`](https://github.com/bitcoin/bitcoin/blob/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src/script/interpreter.cpp#L320-L404)明确分流 ECDSA 与 Schnorr。

## 10. MuSig2：协同签名协议，不是把独立签名相加

事实：BIP327 的 MuSig2 是 n-of-n 协同签名，不是任意 t-of-n 门限协议。它使用公钥列表相关的聚合系数、每个参与者的双 nonce、统一会话与挑战值，再组合 partial signatures，产出可按 BIP340 验证的一份签名；不能将已经独立生成的任意完整签名直接相加。Taproot tweak 与公钥奇偶归一化也需按规范处理。密钥列表顺序是协议输入；默认不替应用排序。

同一 secret nonce 不得用于两次 Sign，重试／崩溃恢复也不能复用；泄漏风险涉及长期私钥。Partial signature 不是可独立当作付款授权证明的普通签名。BIP327 是客户端协议规范，不是全节点新增一个“MuSig2 验证 opcode”。

PPT 页码：p15–19。

应改如何写：Schnorr 的线性结构使安全的多方签名协议成为可能；MuSig2 经过密钥聚合、nonce 交换和部分签名协作生成一份签名。强调 n-of-n、会话绑定与 nonce 单次使用，不把“聚合”解释成裸公钥／现成签名相加。

一手来源：S07 的 [Motivation、General Signing Flow、Public Key Aggregation](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0327.mediawiki)、KeyAgg、Sign、PartialSigAgg、Tweaking。所核验版本为 **1.0.4**；Changelog 记载 2026-08-19 对 PartialSigAgg 的修正，实现应绑定匹配的参考代码／测试向量。

## 11. P2TR：key path 与 script path；只揭示使用的脚本分支

事实：P2TR 输出是 witness v1、32 字节程序，编码 tweak 后的 x-only 输出公钥。概念上 `Q = P + tagged_hash("TapTweak", P || merkle_root) × G`；无脚本树时有相应的无树 tweak 形式，不把它等同于未经 tweak 的裸内部公钥。

移除可选 annex 后，一个 witness 元素走 key path，按输出公钥验证签名；两个及以上元素走 script path，末两项为 script 与 control block，验证所选叶子的 Merkle 承诺。Script path 揭示被花费的脚本与证明，不揭示整棵策略树；key path 不揭示是否存在脚本备选。多方密钥路径聚合也不意味着 script path 的所有签名自动被聚合。

PPT 页码：p15–19。

应改如何写：P2TR 可通过 tweak 后输出公钥的 key path 花费，也可揭示被承诺的某个 script path。标清 internal key、output key、叶脚本、control block；隐私改善是隐藏未使用策略，不是无条件匿名。

一手来源：S06 的 [Script validation rules](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0341.mediawiki#script-validation-rules)、Constructing and spending Taproot outputs 及 Spending using one of the scripts。

## 12. bc1q：既可能是 P2WPKH，也可能是 P2WSH

事实：地址前缀只是识别线索，必须解码并检查版本、程序长度、网络和校验编码。有效主网 v0 地址使用 Bech32，可表示 20 字节 P2WPKH 或 32 字节 P2WSH；两者均可呈现 `bc1q…`。P2TR 是 v1、32 字节程序，使用 Bech32m，通常呈现 `bc1p…`；v1 前缀本身不能代替程序长度与校验验证。

PPT 页码：p15–19。

应改如何写：

| 解码后的类型 | witness 版本／程序长度 | 主网编码 |
| --- | --- | --- |
| P2WPKH | v0／20 字节 | Bech32，`bc1q…` |
| P2WSH | v0／32 字节 | Bech32，`bc1q…` |
| P2TR | v1／32 字节 | Bech32m，`bc1p…` |

不要把“bc1q = 单签地址”“bc1p = 多签地址”写成协议事实；地址类型也不直接表达签名者数量。

一手来源：S04 Witness program；S08 的 [Addresses for segregated witness outputs](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0350.mediawiki#addresses-for-segregated-witness-outputs)及 Test vectors；S06 的 P2TR 程序识别条件。

## 13. Lightning HTLC：哈希条件与时限梯度，不是“时间到自动退款”

事实：常规 HTLC 以 `payment_hash = SHA256(payment_preimage)` 关联多跳付款。转发节点的入站到期高度必须晚于出站，差值至少满足相应 outgoing channel 的 `cltv_expiry_delta`，为观察原像、上链和处理重组留余量。HTLC 绝对到期高度／CLTV 与承诺输出的 `to_self_delay`／CSV 是不同的时间约束。

通道正常在线时通过签名的状态更新移除／兑现 HTLC；争议时依相应 commitment 的 offered／received 输出，使用预签二阶段 HTLC-timeout／HTLC-success 或直接花费路径。不能把各路径都简化成同一段 if/else 脚本。到期让 timeout 路径具备可用条件，不触发 Bitcoin 自动执行；在相应输出尚未被竞争花费前，原像路径可能仍能成功。

PPT 页码：p20–22。

应改如何写：接收方凭原像兑现；付款／转发节点在失败或超时后按协议撤销链下 HTLC，必要时主动关闭通道并广播 timeout 花费，等待确认及适用的 CSV 延迟。多跳超时沿付款方向递减，不写“超过截止时间合约自动退回钱包”。

一手来源：S09 的 [Forwarding HTLCs](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/02-peer-protocol.md#forwarding-htlcs)、cltv_expiry_delta Selection、Removing an HTLC；S10 的 [Offered／Received HTLC Outputs 与二阶段交易](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/03-transactions.md#offered-htlc-outputs)；S11 的 [Local Commitment, Local Offers](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/05-onchain.md#htlc-output-handling-local-commitment-local-offers)。BOLT #5 的 timeout 判定／交易确认边界应结合 Core 最终性规则验收，避免把到期高度与可进入哪一候选块混淆。

## 14. watchtower：反作弊监控，不是离线正常收款代理

事实：惩罚式通道中，“已撤销”旧 commitment 不是被 Bitcoin 共识自动判为无效；对手可能将它上链，需要及时以撤销材料花费惩罚路径。Watchtower 接收预先授权的保护数据，监控已撤销状态上链并提交相应惩罚交易。Lightning Labs 所述服务不接管正常 HTLC 收款的通道签名交互，也不保证代办所有诚实关闭／HTLC 到期处理。

工程推论：配置 tower 不等于用户节点具备离线收款能力；若某钱包提供此体验，应另行说明托管、常在线签名节点、LSP、异步接收等具体机制，不能归功于 tower。保护还取决于状态成功上传、覆盖范围、在线性、费用与确认及时性。

PPT 页码：p20–22。

应改如何写：Watchtower 可代为监测已撤销通道状态的上链作弊，并执行预授权惩罚；正常收款仍需相应通道端点或明确授权的收款服务完成协议交互。退款／sweep 与监控的责任须明确，不承诺“装了 tower 就能永久离线收款”。

一手来源：S10 的 [Key Derivation](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/03-transactions.md#key-derivation)描述可外包 watcher 的材料；S11 的 [Revoked Transaction Close Handling](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/05-onchain.md#revoked-transaction-close-handling)；S12 的 [Watchtowers／Channel breaches](https://docs.lightning.engineering/the-lightning-network/payment-channels/watchtowers)区分 breach 与普通 force close；S09 定义正常付款所需的 HTLC／承诺更新交互。

## 一手来源索引：12 个重点来源

按规范或项目归组；S01 为同一固定版本的 Core 源码证据组，其具体文件和函数均在对应主题内链接，不把不同文件的职责混为一谈。

| 编号 | 来源链接 | 阅读段落／章节／函数 | 支持的结论与使用边界 |
| --- | --- | --- | --- |
| S01 | [Bitcoin Core v30.0 源码](https://github.com/bitcoin/bitcoin/tree/d0f6d9953a15d7c7111d46dcb76ab2bb18e5dee3/src) | `pow.cpp` 的 GetNextWorkRequired／CalculateNextWorkRequired；`chain.cpp` 的 GetBlockProof；`node/blockstorage.cpp` 的比较器／累计值；`validation.cpp` 的 FindMostWorkChain、ConnectBlock、CheckWitnessMalleation；`primitives/transaction.{h,cpp}` 的序列化／哈希；`hash.h` 的双哈希；`consensus/merkle.cpp` 的树；`script/interpreter.cpp` 的签名分流；`kernel/chainparams.cpp` 的主网参数 | 难度方向、2015 个间隔、限幅、工作量链选择、有效性约束，以及交易／承诺的字节级实现；不是“最新 Core”声明。 |
| S02 | [Bitcoin Developer Guide: Block Chain](https://developer.bitcoin.org/devguide/block_chain.html) | Introduction；Proof Of Work；Block Height And Forking | stale／true orphan 用词、每节点独立验证和分叉后的确认变化；教学解释不是替代源码的最终共识规范。 |
| S03 | [Satoshi Nakamoto: Bitcoin 白皮书](https://bitcoin.org/bitcoin.pdf) | §4 Proof-of-Work；§5 Network；§11 Calculations | 累积 PoW 的历史论述、追赶概率与算力攻击不能任意增发／夺币的边界；不把其中“longest”当现代实现的块数比较。 |
| S04 | [BIP141](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0141.mediawiki) | Motivation；Transaction ID；Commitment structure；Witness program | txid／wtxid、scriptSig 保留及输入约束、逐交易 witness 与 commitment 公式；v1 后续规则须结合 BIP341。 |
| S05 | [BIP340](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0340.mediawiki) | Motivation；Description；Specification；Applications；Test Vectors and Reference Code | Schnorr 本体、x-only 公钥与 64 字节签名；该签名规范本身不把全部旧输出迁移为 Schnorr。 |
| S06 | [BIP341](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0341.mediawiki) | Script validation rules；Key path signature validation；Constructing and spending Taproot outputs；Test vectors | P2TR 输出、key／script path、control block、tweak、annex 与 64／65 字节规则；叶版本 0xc0 的脚本执行细则另属 BIP342。 |
| S07 | [BIP327，v1.0.4](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0327.mediawiki) | Motivation；General Signing Flow；KeyAgg；Nonce Generation；Sign；PartialSigAgg；Tweaking；Changelog | MuSig2 的 n-of-n、两轮交互、聚合系数、nonce 单次性与安全会话；不是任意独立签名相加，也不是自动门限签名。 |
| S08 | [BIP350](https://github.com/bitcoin/bips/blob/5aadddb511a5dcfe4599531bd8ae5e5b96d0f793/bip-0350.mediawiki) | Addresses for segregated witness outputs；Test vectors for v0–v16 native segregated witness addresses | v0 用 Bech32，v1–v16 用 Bech32m；校验和必须匹配 witness 版本，bc1q 不唯一指向 P2WPKH。 |
| S09 | [BOLT #2](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/02-peer-protocol.md) | Forwarding HTLCs；cltv_expiry_delta Selection；Removing an HTLC；Commitment updates | 多跳期限安全余量、原像的单 SHA256 条件、链下付款需端点交互、不能提前错误回退上游 HTLC。 |
| S10 | [BOLT #3](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/03-transactions.md) | to_local；Offered／Received HTLC Outputs；HTLC-Timeout and HTLC-Success Transactions；Key Derivation；Appendices C／F／H | CLTV 与 CSV 分工、二阶段路径、惩罚脚本、可外包 watcher 的授权材料；须按协商通道类型选对应格式。 |
| S11 | [BOLT #5](https://github.com/lightning/bolts/blob/191462825ae341f0a27098765c075f01ca9bc6c2/05-onchain.md) | Local／Remote Commitment HTLC handling；Revoked Transaction Close Handling；Generation of HTLC Transactions；General Requirements | 到期后主动花费、原像／timeout 竞争、确认深度与 CSV、费用供给及惩罚反应；协议保证以正确及时处置为条件。 |
| S12 | [Lightning Labs: Watchtowers](https://docs.lightning.engineering/the-lightning-network/payment-channels/watchtowers) | Channel breaches；Watchtowers；Timelocks | tower 监控 breach 并广播预授权惩罚，区别于正常 force close 和正常收款；属于一方实现说明，不是全球通用 tower 功能保证。 |

## 8 个工程测试点

以下是待执行的验收设计，不是已跑通的结果。使用离线测试向量、Core 单元测试或隔离 regtest／本地 Lightning 测试网；不涉及真实资金、主网广播或外部服务修改。

1. **重定向边界与限幅**：用主网参数构造 2016 个区块索引，断言周期第一块取上一周期首尾的 2015 个间隔、分母仍为 1,209,600。覆盖 A=E/2、A=2E、A<E/4、A>4E、非边界高度、powLimit 与 compact 舍入。regtest 默认免重定向，不能用“挖 2016 块未调整”反证主网算法。依据 S01。

2. **工作量、stale／orphan 与非法高工作量候选**：在索引／链选择测试中构造不同 target 的分支，验证比较累计 work 而非高度；未知父块、父块非法、有效非活动分支应分别分类。构造超额 coinbase／无效授权的区块，断言高工作量也不使其被接受。UTXO 及确认状态随合法重组重算。不同难度分支需按规则构造，不靠随意修改 nBits 的无效 regtest 区块。依据 S01–S03。

3. **txid、wtxid 与混合输入序列化**：以固定有效交易核对二进制双 SHA-256、内部字节序和展示值。只改 witness 时 txid 不变、wtxid 变化，但另行检查修改后的脚本是否有效；无 witness 时两者相等。解析 legacy＋witness 混合输入，核对空 witness 占位、保留 scriptSig、witness 位于该交易 locktime 前；用同义 legacy scriptSig 变体检查 txid 改变，并区分共识接受与标准中继拒绝。不得把两个冲突花费同时存在误判成共识可延展性测试成功。依据 S01、S04。

4. **witness commitment 字节级校验**：强制 coinbase 树叶为 32 字节零，选择非零 reserved value；本地重算 W 和 C。覆盖错误 root、reserved value 长度／stack 数量、最高匹配输出索引、合法附加数据、缺承诺却有 witness。验证“全无 witness、无承诺”可成立；不要把 coinbase 实际 wtxid 当树叶或把显示 hex 拼接后哈希。依据 S01、S04。

5. **地址判型与编码拒绝**：运行 BIP350 向量及三类有效地址：v0/20、v0/32、v1/32。验证两个 bc1q 都可合法但类型不同；v0+Bech32m、v1+Bech32、错误程序长度、混合大小写、网络不符须拒绝。结果返回解码后的版本／程序，不用前缀硬编码签名者数。依据 S04、S06、S08。

6. **ECDSA／Schnorr 分流与 P2TR 双路径**：按输入所花费的输出类型选择验证语义，而非按整笔交易设置单一算法。核对 BIP340 及 BIP341 向量；验证 key path 签名使用 tweak 后输出 key，script path 校验选中叶、Merkle 分支、control block 奇偶位与可选 annex。覆盖错误 tweak、错误承诺和 65 字节签名末字节 `0x00` 的拒绝；不要将未来叶版本的升级语义统统写成当前 tapscript。依据 S01、S05、S06。

7. **MuSig2 会话与 nonce 生命周期**：绑定 BIP327 v1.0.4 参考代码和向量，完成 KeyAgg→NonceGen／NonceAgg→Sign→PartialSigAgg，验证最终 BIP340 签名。测试公钥顺序、tweak、消息不一致、错误部分贡献、聚合器扰动及崩溃恢复。拒绝已消费 nonce 的再次 Sign；partial signatures 不作为独立授权证据；两个独立完整 Schnorr 签名的裸相加不是有效替代。依据 S07。

8. **Lightning 超时主动处置与 tower 边界**：隔离运行 A→B→C 通道，检查入站／出站 expiry 梯度、不可撤销承诺状态与 preimage 验证。断开端点，推进区块高度，验证 timeout 需主动广播、费用足够才能确认，适用时还需 CSV 后 sweep；观察已到期但未花费 HTLC 的竞争原像路径。另测试旧状态上链时 tower 惩罚、普通关闭时的责任、状态未上传的覆盖缺口。端点离线且只启用 tower 时不得标记正常收款成功；到期高度与下一候选块的 locktime 最终性须逐块断言。依据 S01、S09–S12。
