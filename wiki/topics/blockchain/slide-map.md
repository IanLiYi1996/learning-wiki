# PPT 60 页内容索引

- 编号按实际幻灯片顺序，不按原页眉中跳号的章节编号
- 原始 PPT、逐页提取和截图仅保留在本地，不随此索引公开
- 下面是主题摘要，不是原文转录；核验 / 修订见 [纠错表](corrections.md)

章节简称：01 系统模型；02 Bitcoin；03 Ethereum；04 生态；05 工程；06 安全；07 AWS。

| 页码 | 原稿主题 | 正文落点 / 重点 |
| --- | --- | --- |
| 1 | 穿透区块链封面 | [专题入口](README.md) |
| 2 | 六大主题总览 | [学习路线](learning-roadmap.md) |
| 3 | 双花问题 | [01](chapters/01-system-model.md)、[02](chapters/02-bitcoin.md)：签名不决定排序 |
| 4 | 四重防线 | [02](chapters/02-bitcoin.md)：有效链与最大累计 work |
| 5 | 双花攻击过程 | [02](chapters/02-bitcoin.md)：确认概率与攻击前提 |
| 6 | 孤块与 PoW 叔块 | [02](chapters/02-bitcoin.md)：stale / orphan；叔块是历史机制 |
| 7 | 出块速度与难度调节 | [02](chapters/02-bitcoin.md)：纠正 difficulty 比例 |
| 8 | SegWit 的目标 | [02](chapters/02-bitcoin.md)：承诺范围与兼容性 |
| 9 | txid 延展性 | [02](chapters/02-bitcoin.md)：双 SHA-256 与有效性条件 |
| 10 | Legacy / SegWit 交易结构 | [02](chapters/02-bitcoin.md)：witness 在 locktime 前 |
| 11 | txid 与 wtxid | [02](chapters/02-bitcoin.md)：标识与 sighash 区分 |
| 12 | 新旧区块结构 | [02](chapters/02-bitcoin.md)：逐交易 witness，不是全块尾区 |
| 13 | 见证位置与权重 | [02](chapters/02-bitcoin.md)：weight / vsize |
| 14 | witness commitment | [02](chapters/02-bitcoin.md)：root + reserved value |
| 15 | Taproot 三块拼图 | [02](chapters/02-bitcoin.md)：新增路径与旧规则并存 |
| 16 | Schnorr 聚合 | [02](chapters/02-bitcoin.md)、[06](chapters/06-security.md)：MuSig2 非裸相加 |
| 17 | Taproot key / script path | [02](chapters/02-bitcoin.md)：tweak 与分支隐私 |
| 18 | Tapscript | [02](chapters/02-bitcoin.md)：脚本阈值与门限签名区分 |
| 19 | Taproot 收益与新地址 | [02](chapters/02-bitcoin.md)：Bech32m、隐私边界 |
| 20 | 闪电支付通道与惩罚 | [02](chapters/02-bitcoin.md)：旧状态仍可能上链 |
| 21 | HTLC 多跳路由 | [02](chapters/02-bitcoin.md)：期限梯度与主动退款 |
| 22 | 闪电网络痛点 | [02](chapters/02-bitcoin.md)：流动性与在线责任 |
| 23 | 智能合约字节码与账户 | [03](chapters/03-ethereum.md)：代理与 EIP-7702 |
| 24 | 合约 storage trie | [03](chapters/03-ethereum.md)：slot / trie 路径 |
| 25 | 全局 state trie | [03](chapters/03-ethereum.md)：四字段与状态根证明 |
| 26 | 结构共享 | [03](chapters/03-ethereum.md)：逻辑承诺与实际数据库分开 |
| 27 | 规模与节点配置 | [03](chapters/03-ethereum.md)：客户端 / 版本 / 模式条件 |
| 28 | USDT 不是公链 | [04](chapters/04-ecosystem.md)：资产与网络 |
| 29 | USDT 起源与多链 | [04](chapters/04-ecosystem.md)：官方支持 / 包装 / 旧链 |
| 30 | 四类稳定币与市场规模 | [04](chapters/04-ecosystem.md)：只保留机制，不搬市场数值 |
| 31 | USDT / USDC 法币储备 | [04](chapters/04-ecosystem.md)：储备鉴证与赎回条件 |
| 32 | DAI / USDS Vault | [04](chapters/04-ecosystem.md)：ETH 示例不是完整抵押模型 |
| 33 | DAI 清算与依赖 | [04](chapters/04-ecosystem.md)：PSM / RWA，不搬未复核损失金额 |
| 34 | USDe / UST | [04](chapters/04-ecosystem.md)：对冲边界与历史铸销 |
| 35 | 稳定币机制对照 | [04](chapters/04-ecosystem.md)：机制可混合，链外依赖另标 |
| 36 | Ethereum / Solana 对比 | [04](chapters/04-ecosystem.md)：测量口径及 Alpenglow 更新 |
| 37 | Solana 程序与数据账户 | [04](chapters/04-ecosystem.md)、[05](chapters/05-wallet-engineering.md)：PDA / token accounts |
| 38 | Polygon 扩容 | [04](chapters/04-ecosystem.md)：PoS 侧链、zkEVM 退役 |
| 39 | Polkadot / Cosmos 哲学 | [04](chapters/04-ecosystem.md)：框架、安全、通信分别说 |
| 40 | 多链体系对照与价值捕获 | [04](chapters/04-ecosystem.md)：Coretime / XCM；不作币价评价 |
| 41 | lock-and-mint 桥 | [04](chapters/04-ecosystem.md)：一种模式，不是全部跨链 |
| 42 | 桥事故与安全 | [04](chapters/04-ecosystem.md)：分层威胁模型，不搬损失统计 |
| 43 | Bitcoin 地址四类锁 | [02](chapters/02-bitcoin.md)、[05](chapters/05-wallet-engineering.md)：补 P2WSH |
| 44 | 收、发、花兼容责任 | [05](chapters/05-wallet-engineering.md)：历史脚本与恢复 |
| 45 | Ethereum nonce / gas | [03](chapters/03-ethereum.md)、[05](chapters/05-wallet-engineering.md)：并发与执行结果 |
| 46 | ERC-20 余额与事件 | [03](chapters/03-ethereum.md)、[05](chapters/05-wallet-engineering.md)：接口 / 精度 / 实际到账 |
| 47 | 授权、盲签、AA | [06](chapters/06-security.md)：permit、4337、7702 |
| 48 | 多网络与钱包对比 | [05](chapters/05-wallet-engineering.md)：完整资产标识 |
| 49 | EVM 迁移复用 | [05](chapters/05-wallet-engineering.md)：兼容不等于零验收 |
| 50 | 交易所接链职责 | [05](chapters/05-wallet-engineering.md)：扫描、提现、账务、重组 |
| 51 | USDT 充值网络匹配 | [05](chapters/05-wallet-engineering.md)：防错链与恢复条件 |
| 52 | 冷热、多签、MPC | [06](chapters/06-security.md)：不同控制维度 |
| 53 | DKG / TSS | [06](chapters/06-security.md)：协议与恢复安全 |
| 54 | Safe 与 EOA | [06](chapters/06-security.md)：owner 阈值之外的模块路径 |
| 55 | AMB Access / Query / Fabric | [07](chapters/07-aws.md)：生命周期与职责 |
| 56 | AMB 支持矩阵 / 项目声明 | [07](chapters/07-aws.md)：网络 / 区域；作者声明非本次实测 |
| 57 | KMS / CloudHSM / Nitro | [07](chapters/07-aws.md)：算法、HD、签名授权边界 |
| 58 | KMS BTC 提币图 | [07](chapters/07-aws.md)、[图阅读记录](notes/follow-up-verification.md)：DER、低-S、故障分支 |
| 59 | CloudHSM BTC 提币图 | [07](chapters/07-aws.md)、[图阅读记录](notes/follow-up-verification.md)：r||s、CKM_ECDSA、硬件世代 |
| 60 | 总结 | [专题入口](README.md)：沿状态与信任边界复盘 |

## 原始资料与发布范围

原文件与逐页提取未修改，只保存在本地忽略目录；公开版本不包含附件、原文转录、图片或提取数据。此表是学习主题摘要与页码映射，第 58–59 页图片已人工阅读，解读保存在研究笔记。

提取脚本：[extract_pptx.py](scripts/extract_pptx.py)。它不执行宏、外链、嵌入对象或附件中的操作要求。
