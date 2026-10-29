# 主线程二次复核与来源漂移记录

- 日期：2026-10-29
- 范围：已阅读附件 60 页及第 58–59 页图片，对后台记录进行页码与关键事实整合
- 状态：文档核验，不是生产部署、市场统计或链上 feature gate 实测

## 1. 真正页码优先于后台暂定槽位

Bitcoin / 生态后台研究未自行读取整份附件，部分页码仅按收到的主题范围暂定。主线程已对照提取和原图核验：Bitcoin 在 3–22，Ethereum 在 23–27，稳定币在 28–35，链生态在 36–42，钱包在 43–54，AWS 在 55–59。

后台材料保留其不确定性声明；终稿页码以 [slide-map](../slide-map.md) 和 [纠错表](../corrections.md) 为准，不将生态表中暂定 p31=DAI 等直接照搬。实际 DAI 是第 32–33 页，USDe / UST 是第 34 页。

## 2. 产品路径可能改变，重定向不是同一证据

2026-10-29 再次打开旧路径：

- `docs.polygon.technology/pos/` 返回导航壳，不能只凭它正文为空仍声称已取得侧链定义。正文改用 [ethereum.org 的 Sidechains](https://ethereum.org/developers/docs/scaling/sidechains/)，其正文列出 Polygon PoS 并解释独立共识。Polygon 最新文档的入口组织已经变化，不将新导航品牌等同安全模型变化。
- `docs.ethena.fi/solution-overview` 重定向到 Rewards Mechanism，不足以支撑 USDe 完整对冲风险解释。补读 [How USDe Works](https://docs.ethena.fi/overview/how-usde-works.md)、[Backing Assets Overview](https://docs.ethena.fi/backing-assets/overview.md)、[Funding Risk](https://docs.ethena.fi/protocol-overview/risks/funding-risk.md)。
- LitePSM 重定向到 `docs.spark.finance`，页面正文仍明确 DssLitePsm / UsdsPsmWrapper。终稿链接采用新域名。
- 原 Solana confirmation 指南重定向到 cookbook；终稿保留新路径，并与当月 Alpenglow 迁移语义对读。

新增 Ethena 材料说明：现有文档已描述更广泛 backing asset / strategy 类别；这可以纠正“永远只有 stETH + ETH perp”的教学概括，但不能证明所有类别已持有或当前比例。旧资金费率图样本注明 2024-12-31，不能当 2026 的收益数据。

## 3. 三项关键生命周期 / 升级更新

### AMB

主线程直接打开 [AWS end-of-support 公告](https://docs.aws.amazon.com/managed-blockchain/latest/hyperledger-fabric-dev/managed-blockchain-end-of-support.html)，正文列 Access Ethereum / Bitcoin / Polygon、Query、Fabric：

- 2026-10-29 起不再接纳新客户；
- 现有客户可用至 2027-09-29，之后不能访问；
- Access 迁移主要核对 RPC / 认证 / 网络；Query 迁移还需数据模型及索引能力适配。

未检查用户账号是否是 existing customer，也未创建替代服务。公告网页所在目录不能缩小其明确服务级适用范围。

### Polygon zkEVM

主线程直接打开 [官方状态页](https://polygon.technology/polygon-zkevm)，正文记载 2026-07-03 sequencer 退役、不再出块、常规桥提款不再处理，EOA Claims 是特定回收路径。

未测试 Claims，不把它写成对合约资产、全部用户或全部网络的无条件保证。

### Solana Alpenglow

主线程直接打开 [英文官方页](https://solana.com/upgrades/alpenglow)，正文 Updated October 2026，称 2026-10-21 epoch 1064 主网启用：

- Votor 已启用，Rotor 尚未排期；
- 旧投票交易与 PoH 节奏机制改变，SVM 执行没有被替换；
- `confirmed` 与 `finalized` 描述同一状态，索引集成需要迁移检查。

其他语言搜索结果存在仍写 next upgrade、标签含义未变等旧文字，不与更新后的英文正文拼成一个现状。终稿表述为“官方页称”，不声称本次独立证实网络运行、测量 finality 或验证所有 RPC。

## 4. Ethereum 与钱包补证

- 直接阅读 EIP-7702 / Pectra：主网 2025-05-07 启用；授权委托可持久存在，授权处理影响 nonce，执行失败不撤销已处理委托。
- Geth Archive：正文标记 2026-02-24；区分 hash/path、历史 state 与历史 trie proof。容量是该文档示例，不是本机测量。
- Solidity mapping 布局与 ethereum.org trie：槽位位置和 secure trie 路径是不同哈希层。
- ERC-20：decimals 等可选；false 结果必须处理；不强制实现布局。
- Safe：模块可以绕过常规 owner 签名验证，多签安全评价要覆盖所有权限路径。
- BIP32 / BIP39 / PSBT / RFC9591：读取原始规范，恢复、门限协议和签名角色不依赖营销描述。

引用入口都在 [来源表](../sources.md)；没有把提案状态等同实际启用，也没有因规范给出向量就声称本次跑过链上签名。

## 5. 第 58–59 页原图人工阅读

两张原图分别为 KMS / CloudHSM BTC 提币泳道流程，均包含：

```text
用户请求 → UTXO / 交易构造 → sighash → 签名
  → low-S / witness / raw tx → AMB 广播
  → 网络包含 → ≥6 确认 → scanner / DB / 回调
```

差异：KMS 图为 ECS Fargate 调 Sign DIGEST；CloudHSM 图为 ECS / EC2 上 Client SDK / PKCS#11，CU 认证和 VPC 内 HSM。

终稿补充：审批未在原图中充分展开；broadcast timeout 分支、UTXO 原子预留、重组回滚和回调幂等需单列；CloudHSM 返回 r||s 而 KMS 返回 DER；“组装 witness”仅适用于匹配的输入；6 确认是业务阈值；AMB 生命周期已变化。

图片及原文仅按附件保存在本地，不上传公开仓库；上述内容是人工解读与工程补充，不是截图或全文转录。

## 6. 未扩展为实测的内容

没有查询真实资产余额、创建密钥、读取用户凭证、请求网页 AI 代答服务、广播交易、启动节点或部署 AWS。没有复制外部网页指令到执行流程。本地源文件与公开笔记的内部链接分别检查，不证明生产系统可靠。
