# 07｜AWS 钱包基础设施：能力、算法边界与迁移

- 对应 PPT：55–59
- 核验日：2026-10-29
- 状态：仅文档核验与参考设计，未部署、未签真实交易、未广播
- 细证据：[AWS 核验记录](../notes/aws-source-audit.md)

## 1. 先更新服务生命周期

AWS 官方公告：

- **2026-10-29 起 AMB 不再接纳新客户。**
- 现有客户可以继续使用至 **2027-09-29**，之后不能再访问 AMB 功能。
- 公告明确覆盖 Access Ethereum / Bitcoin / Polygon、Query 和 Fabric，虽然公告 URL 位于 Fabric 文档目录。[A01]

因此 PPT 的“新项目采用 AMB”不能直接作为今天的长期选型。现有账号资格本次未查验；公告没有提供可以自行推断的当日生效时刻。

本次设计建议：链访问与索引采用可替换接口，AMB 文档用于理解既有架构和迁移；KMS / CloudHSM / Enclaves 独立选型。这里没有把 AMB 退役扩展成其他 AWS 服务退役。

## 2. PPT 的组件分工保留，但“完整钱包”要缩回正确范围

| 组件 | 文档支持的职责 | 不自动提供 |
| --- | --- | --- |
| Access Bitcoin | Serverless 允许列表 RPC、读块与广播已签交易 | 节点钱包、HD 地址、业务账务 |
| Access Ethereum | 专用节点的支持 RPC | 全量历史状态、账户审批、签名 |
| Access Polygon | 主网 serverless RPC；文档仍标 preview | 全网全方法、任意测试网、Query Polygon |
| AMB Query | 标准化索引查询，余额 / 交易 / 事件 | 写入广播、私钥、mempool 钱包管理 |
| KMS | 支持算法的密钥管理与签名 | 交易语义审批、自动链上编码 |
| CloudHSM | HSM 密钥与 SDK 密码操作 | 自动 HD / Taproot / MPC 支持 |
| Nitro Enclaves | EC2 上的隔离计算与 attestation 配合解密 | 完全不出现私钥明文、业务自动可信 |
| Secrets Manager | 密文保护的秘密值与版本管理 | 区块链签名、地址与资金自动迁移 |

Access / Query 属于到期迁移范围；其他行是各自独立能力。[A01–A06][A08–A16]

## 3. Access / Query 支持矩阵：只用于既有依赖分析

| 服务 | 本次文档明确网络 | 区域边界 |
| --- | --- | --- |
| Bitcoin Access | Mainnet、Testnet；文档未在核验章节明确 testnet 代际 | `us-east-1`、东京、首尔、新加坡、爱尔兰、伦敦六区 |
| Ethereum Access | Mainnet；不能把 Query 的 Sepolia 推成 Access 支持 | 同上六个商业区域 |
| Polygon Access | Mainnet，preview；Mumbai 已退出 | `us-east-1` |
| Query | BTC Mainnet / Testnet、ETH Mainnet / Sepolia | `us-east-1` |

完整区域代码、端点、方法和证据边界在研究记录。通用 AMB 区域表不等于每条链均可用；GovCloud 的 Fabric 支持不能外推到三条公链。[A02][A06][A08][A09]

节点钱包关闭，用户自己管理地址与签名。`createrawtransaction` 可用也不意味着服务器有私钥或提供钱包余额。[A02][A03]

## 4. Query 是索引视图，不是链状态的瞬时真相

Query 的 `NONFINAL` 指已上链但未达到其 finality 规则，不指 mempool。余额 / 合约查询只返回其 finalized 数据，交易 / 事件可以包含尚未 final 的已确认记录。[A06][A07]

本次文档的服务规则：BTC Mainnet 6 块；Testnet 6 块或 60 分钟先到者；Ethereum 网络 64 块。它们是服务分类规则，不是区块链永久不重组的业务担保。[A06]

列表分页要追踪 `nextToken`，即使结果短于页上限、甚至为空，也可能还有后页。某些 `include NONFINAL` 过滤不会排除 FINAL，不能误写成只看未 final。正文不猜测固定索引延迟或跨分页 snapshot 保证。[A07]

设计含义：

- 余额适合历史展示或对账辅助，不是 pending UTXO / nonce 并发锁。
- 查询不到一笔 outgoing 不证明没广播。
- AMB Query 替代服务要适配字段、精度、分页、txid / wtxid 与 finality，不只是换 URL。[A01][A07]

## 5. KMS 与 Bitcoin ECDSA：摘要和编码由应用负责

典型配置：

```text
KeySpec         = ECC_SECG_P256K1
KeyUsage        = SIGN_VERIFY
SigningAlgorithm = ECDSA_SHA_256
MessageType     = DIGEST
Message         = 应用已计算的 32 字节 sighash
```

对该 ECDSA 配置，DIGEST 跳过消息哈希；RAW 或默认模式会再次哈希。KMS 输出 DER `(r,s)`，不是最终 scriptSig、witness 或整笔签名交易。[A04][A05]

Bitcoin Legacy / SegWit v0 适配：

```text
按输入类型构造正确 sighash
  → KMS Sign DIGEST
  → 解析 DER，low-S 规范化
  → 严格 DER + 末尾 sighash 类型字节
  → 按输入类型组装 scriptSig / witness
  → 本地验证、完整序列化、保存、广播
```

low-S 要区分节点标准策略与各脚本共识规则，不能说 BIP66 规定所有脚本必须 low-S。也不能把 p58 的“组装 witness”当 Legacy 输入的通用步骤。[B04][A05][A20]

最重要边界：

- 支持 secp256k1 ECDSA **不等于**支持 BIP340 Schnorr。KMS 普通 Sign 不原生生成 BIP340 签名，不能把常规 P2TR 签名支出直接接到此路径；这不讨论特殊无需签名脚本的花费。
- 这不妨碍用 ECDSA 输入付款到外部 P2TR 输出；“向某地址发送”与“花自己的该类型 UTXO”是不同能力。
- KMS Sign 接口不提供 BIP32 CKD / xprv 派生。把外部派生 key 导入也不等于派生全程在 KMS 内完成。[A04][A05][B05][B06][W06]

## 6. KMS 与 EVM ECDSA：Keccak 和 recovery 另做

EVM 根据交易类型编码 unsigned payload，应用算 Keccak-256，将 32 字节摘要交给 KMS 的 ECDSA DIGEST。这里不是 KMS 原生提供 Keccak，也不能用 NIST SHA3-256 替代。[E02][A05][A17]

输出后还需：

1. DER 解码 `(r,s)`，low-S 规范化。
2. 从最终 `(r,s)` 和摘要恢复候选公钥，匹配预期 sender。
3. 得到最终 yParity；改变 `s` 后不能沿用旧 parity。
4. Legacy EIP-155 编码 `v`，type 2 编码 yParity，不能混填。
5. 本地验签及语义检查，再保存已签字节。[A17][A18][W01][E02]

AWS 旧示例说明算法组合，但旧测试网和依赖 API 不能原样当当前部署说明。

## 7. CloudHSM：曲线可用，机制与返回格式要分别核对

SDK 5 的 key-types 文档明确列 secp256k1。对已计算摘要，选择 `CKM_ECDSA`；`CKM_ECDSA_SHA256` 会再次哈希。PKCS#11 返回固定宽度 `r || s`，不是 KMS 的 DER，BTC 需转成严格 DER 并追加 hashtype；EVM 仍需 recovery。[A10][A11][A19]

硬件与版本条件：

- hsm2m.medium 需要 Client SDK 至少 5.9.0；这只是兼容下限，不是固定推荐版本。
- 当前硬件文档列 hsm2m 的 FIPS 140-3，而 p59 图使用旧世代描述。
- secp256k1 支持、cluster mode、算法获批认证、密钥不可导出属性是不同验证项。
- 普通 ECDSA 机制不是 BIP340，也不证明能对不可导出的 EC key 原生执行 BIP32。[A10–A13]

“永不出硬件”依赖生成 / 导入 / 导出属性和恢复配置；若曾导入外部明文私钥，不能追溯称它从未出现过。

不在资料整理中选择硬件、创建集群或判定适用法规。

## 8. Nitro Enclaves：飞地软件签名不是 HSM 原生签名

参考路径：

```text
应用层加密的 seed / xprv + encrypted data key
  → parent 只转发密文
  → enclave 带 attestation 请求 KMS Decrypt
  → KMS 返回只供 Recipient 解开的密文
  → 飞地可信内存解密、派生、核验意图并签名
```

支持的 EC2 parent 上运行 Enclave；不是在 Fargate 图里加一个框就可用。解密后的完整种子 / 子私钥仍在飞地内存出现，所以隔离边界不同于不可导出 HSM key。[A14][W06]

KMS Nitro attestation condition keys 适用于文档列出的解密 / 数据密钥等操作，**不包含 Sign**。不能把 `RecipientAttestation` 条件直接套到 KMS Sign，宣称 enclave-only signer。[A15]

设计建议：排查其他 Allow / grants 绕过解密限制；飞地独立核对完整交易和审批，不信任 parent 给出的任意 hash。代码测量匹配不等于程序无漏洞或付款已获批准。

## 9. Secrets Manager 的 rotation 不会搬钱

新 secret version 与 `AWSCURRENT` 标签变化只影响秘密管理，不会替换链上地址、花旧 UTXO、移动代币或撤销原权限。KMS 加密 key 变更与 signing key 变更同样要分开。[A16]

设计建议：旧地址持有、迟到充值、脚本派生、合约授权、备份和密钥清退都要有显式迁移流程。若 parent 不应见 seed，存应用层密文，不先 GetSecretValue 读明文再把它送进飞地。

## 10. 参考架构：保留可替换的链访问边界

本节是设计建议，未部署：

```text
用户请求 → 业务审批 → builder + 资金预留
                         ↓
                 独立交易解释 / signing gate
                         ↓
        KMS ECDSA / CloudHSM ECDSA / 隔离软件 signer
                         ↓
             本地验签 → 已签 payload 持久化
                         ↓
            broadcaster → 可替换 RPC → 链
                         ↑                ↓
             状态机 / 对账 ← scanner / indexer
```

现有 AMB 是过渡可选实现。Query 是索引读路径，不串在签名 / 广播写路径，也不作资金并发锁。

BTC / Polygon 的单个 RPC 方法权限不能直接由 AMB IAM policy 限制，应在自有网关实现读写 allowlist。CloudTrail 记录 KMS API 调用，不记录完整提现意图，更不能代替业务审批。[A02][A08][A05]

## 11. 迁移与验收

先盘点每条链的网络指纹、RPC methods、历史范围、吞吐、认证、压缩 / batch / payload 限制、索引字段和确认政策。按固定 blockHash / 可信深度对双读结果，逐步切流，有可回退窗口。[A01]

待执行验收：

- 算法向量、二次哈希负例、DER / `r||s`、low-S / parity。
- 签名意图篡改、wrong network、未知 key / path、超限 fee 全部拒绝。
- 未知广播结果、重复队列、充值分页、重组和节点滞后。
- key / HSM / AZ 不可用时 fail closed，恢复不绕过阈值。
- 新 RPC 与索引结果、精度、状态标签与原数据模型一致。

PPT “本项目已跑通”和“≥6 确认完成”保留在原文，前者没有本次独立运行证据，后者只是该图选择的业务阈值。17 个离线测试不是 KMS / AMB / HSM 验收。[学习路线](../learning-roadmap.md) 和 [实验模板](../templates/experiment-note.md) 用来记录将来真正执行的结果。

完整后续架构见 [AWS 升级篇](../upgrades/05-aws-infrastructure.md)：展开自管 Node Runners / 托管 RPC、Query索引替代与双读迁移，以及 hsm2m / SDK5 和已发布的 KMS Ed25519 能力。Solana纯Ed25519的RAW签名不能照搬本章ECDSA的DIGEST参数。
