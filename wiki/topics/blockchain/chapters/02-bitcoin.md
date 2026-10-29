# 02｜Bitcoin：UTXO、共识、SegWit、Taproot 与支付通道

- 对应 PPT：3–22、43–44
- 目标：能解释交易有效性、分叉选择和每种花费路径
- 细节证据与固定源码版本见 [Bitcoin 核验记录](../notes/bitcoin-source-audit.md)

## 1. UTXO 是输出，不是账户余额

一个 outpoint 由 `(txid, vout)` 指定。输出记录金额与 scriptPubKey；输入引用它并提供满足花费条件的材料。钱包“余额”是根据自己能控制的输出计算出来的视图，不是 Bitcoin 链上一个地址账户的 balance 字段。[B01][B14]

```text
旧交易的输出（UTXO）
  → 新交易输入引用
  → 验证脚本与金额守恒
  → 删除被花费输出，新增收款 / 找零输出
```

两笔交易都能有合法签名，却不能在同一有效历史中花同一输出两次。先收到的交易可能只是某个节点的 mempool 选择；最终排序取决于有效区块历史。[B01][B02]

## 2. 最多累计工作量与确认

节点先拒绝无效区块，再选择累计工作量最大的有效链。“最长链”是历史简称，不宜简单比较块数。Core 的单块工作量可表示为 `floor(2^256 / (target + 1))`，再逐块累加，不是记录矿工实际计算次数。[B01]

多数算力可以干扰排序、重组自己的付款或持续审查，但不能只靠算力伪造他人签名、任意花费 UTXO 或让正常节点接受超额发行。少数算力也不意味着双花概率为零；白皮书的追赶模型有算力比例、持续时间等前提。[B01][B02]

严格用词：父块未知是 orphan；有效竞争分支未进入活动链通常称 stale。交易是否再次进入链要重新判断，不能写“stale 区块从未存在，所以其全部交易永久消失”。[B14]

工程含义：确认阈值是接受风险的业务策略，需要金额、链状态和故障处理配合。

## 3. PPT 第 7 页：difficulty 与 target 的比例反了

主网概念公式：

```text
E = 2016 × 600 秒
A = 上一周期末块时间戳 − 上一周期首块时间戳
A* = clamp(A, E/4, 4E)

Tnew = min(powLimit, floor(Told × A* / E))
Dnew ≈ Dold × E / A*
```

`target` 越小越难；difficulty 与 target 反比。上一周期 7 天完成，则 target 约减半、difficulty 约翻倍。PPT 将 target 的比例误写成 difficulty 的比例。[B01]

准确边界：每 2016 块按高度调整；首尾时间戳实际横跨 2015 个间隔，分母仍是 `2016 × 600`。还涉及 compact 编码舍入与 powLimit。Testnet 和 regtest 的例外不能作为主网规则。[B01]

## 4. 三种哈希必须分开

| 对象 | 用途 | 不应混淆 |
| --- | --- | --- |
| txid | 传统交易序列化的双 SHA-256；供输入引用输出 | 不是签名摘要 |
| wtxid | 含 witness 的交易序列化双 SHA-256 | 不是“所有见证直接拼接的哈希” |
| sighash | 依输入类型和 sighash flag 构造的签名消息摘要 | 不必等于 txid，也不必对整笔交易按同一种规则计算 |

没有 witness 时 `wtxid = txid`。计算输入是二进制序列化，不是 JSON 或 hex 文本；显示字节序与内部字节序也要区分。[B03][B04][B06]

## 5. SegWit 改的是承诺范围，见证仍在各交易内

含 witness 的序列化顺序是：

```text
version | marker | flag | vin | vout | 每输入 witness stack | locktime
```

计算 txid 时用传统格式，不含 marker、flag 和 witness；wtxid 包括扩展格式。区块依序保存交易，不是在所有交易末尾另放一个全区块集中签名区。[B03]

scriptSig 字段没有删除：

- 原生 witness 输入要求为空；
- P2SH 包裹的 witness 输入保留对应 redeemScript 的 push；
- Legacy 输入仍保留其解锁数据。

所以混合 Legacy / witness 输入的整笔交易不能无条件称为不可延展；还需看全部输入和签名条件。SegWit 解决对应条件下 txid 的非自愿延展性，不保证 wtxid 或签名者主动构造的所有变体不变。[B03]

## 6. witness commitment 如何进入区块承诺

设 `H₂` 是双 SHA-256：

```text
W = MerkleRoot(coinbase 的零叶值, 其余交易的 wtxid)
C = H₂(W || witness_reserved_value)

coinbase 某个输出的 scriptPubKey：
OP_RETURN + 0x24 + 0xaa21a9ed + C [+ 可选后续字节]
```

reserved value 为 coinbase 输入 witness 中的 32 字节值，不要求必须全零。coinbase 只在这棵 witness 树中使用零叶，不代表它自己的真实 txid / wtxid 为零。[B03]

```text
witness 数据
  → wtxid Merkle root + reserved value
  → coinbase 输出承诺
  → coinbase txid
  → 区块头原有 txid Merkle root
  → PoW
```

这解释了区块头结构不变却仍承诺 witness。witness root 本身不等于 commitment；多个匹配输出取最高索引，具体条件按 BIP141。[B03]

## 7. 权重与费用

```text
weight = stripped_size × 3 + total_size
       = 非 witness 字节 × 4 + witness 字节 × 1
vsize  = ceil(weight / 4)
```

区块上限为 4,000,000 weight units。PPT 的“约 2–4 MB”只能作依交易组合变化的直观解释，不是每块都能放固定数量的交易。手续费报价应明确 `sat/vB`；签名材料、输入输出类型决定交易大小。[B03]

这里的 vsize 公式是 BIP141 基础大小模型。Core 的 mempool policy / RPC 还可能按 sigops size 调整其 vsize；新版 cluster mempool、CPFP / RBF 与相关费用口径见 [升级篇 Bitcoin 工程](../upgrades/06-bitcoin-wallets.md)，不要把基础公式当成所有客户端字段的完整定义。

## 8. Taproot：增加新路径，旧 ECDSA 不会自动消失

- BIP340：Schnorr 签名规范。
- BIP341：P2TR 输出、tweak 与 key / script path。
- BIP342：当前 tapscript 叶的执行规则。[B05][B06][B07]

旧 Legacy 和 SegWit v0 路径继续使用相应 ECDSA 规则。BIP340 签名本体为 64 字节；交易中的非默认 sighash 编码可额外有一字节类型，不能用旧 DER ECDSA 编码替代。[B05][B06]

Taproot 概念：

```text
internal key P + 脚本树根的 tagged-hash tweak → output key Q

key path：对 Q 给出有效 Schnorr 签名
script path：揭示选中的脚本 + control block / Merkle 路径
```

key path 隐藏是否存在备用脚本；script path 隐藏未使用分支。它改善策略隐私，不保证匿名或消除金额、交易图等信息泄露。[B06]

## 9. MuSig2 与 tapscript 多签不是同一种做法

MuSig2 是协同产生一份 Schnorr 签名的 n-of-n 协议，需要安全公钥聚合、nonce 交互、会话绑定和 partial signatures，不是把既有完整签名相加。BIP327 v1.0.4 在 2026-08-19 还有修正记录，实现应绑定参考代码和向量。[B08]

当前 tapscript 可通过 `OP_CHECKSIGADD` 组织阈值脚本；每条执行路径仍按脚本验证贡献。`t-of-n` 门限签名协议、MuSig2 聚合签名和链上 k-of-n 脚本要分别命名。[B07][B08]

工程含义：签名 nonce 重用、错误 tweak、错误公钥奇偶处理都可能使钱包不可用或泄露密钥，不能为学习方便手写生产实现。

## 10. 地址表补上漏掉的 P2WSH

以下前缀只适用于主网常见编码；必须实际解码、检查校验与网络：

| 地址提示 | 典型输出 | 需要判断的内容 |
| --- | --- | --- |
| `1...` | P2PKH | 公钥哈希，Base58Check |
| `3...` | P2SH | 脚本哈希，不代表一定是多签 |
| `bc1q...` | P2WPKH / P2WSH | v0，分别 20 / 32 字节 program，Bech32 |
| `bc1p...` | P2TR | v1 / 32 字节，Bech32m，key / script path |

“支持接收”“支持发送到某种锁”“能花自己的历史输出”是三项能力。地址前缀不能推出签名者数量。主推一种接收类型也不应丢弃原有恢复资料。[B03][B06][B09][W05]

## 11. Lightning：支付通道与及时处置

典型通道先在链上锁定资金，随后协作更新余额，关闭时结算。PPT 的“开关共两笔”是正常简化路径；争议、HTLC 和其他通道操作可增加链上交易。[B10][B11][B12]

惩罚式通道的旧承诺不是被 Bitcoin 自动判为无效。公布被撤销状态时，对手需要及时用撤销材料触发惩罚；是否有在线监控、费用及恢复能力很重要。[B11][B12]

多跳 HTLC 用同一 payment hash / preimage 关联，超时沿付款方向递减，为中间人上链追索留安全窗口。到期使 timeout 路径可用，但不会自动向钱包打款；仍需协议处理或主动广播相关花费。[B10][B11][B12]

Watchtower 可代为监控被撤销状态并执行预授权惩罚，不是正常离线收款代理，也不默认承担所有诚实关闭和 HTLC 处置。[B13]

教学例：

```text
Alice → Bob：较晚到期
Bob   → Carol：较早到期
Carol 揭示 R → Bob 可凭 R 领取上游资金
失败 / 超时 → 按协议撤销或主动执行超时路径
```

需要另行评估通道方向性流动性、路由、在线责任和备份。PPT 的市场热度、应用普及程度与国家法币政策不作为本专题技术结论。

## 自测

1. 100 vB 的交易与 100 字节的交易为何不是同一计费概念？
2. 为何 txid 没承诺 witness，区块仍能检测 witness 被更改？
3. 某输入来自 P2TR，KMS 给出 DER ECDSA 签名，是否可以直接花费？
4. Watchtower 能做哪些事，又不能替你完成哪些付款交互？

答案线索分别见第 7、6、8、11 节；工程验收点见后台记录，离线模型见 [练习](../examples/offline_workbook.py)。
