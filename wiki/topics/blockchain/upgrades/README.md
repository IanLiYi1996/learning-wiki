# 时效更新与升级后的完整机制

- 查阅日：2026-10-29（北京时间）
- 目的：接着 PPT 学新机制，而不止看到一条“已过期”提醒
- 结构：6 篇升级教程，与原来的 7 章基础篇对读
- 证据：官方规范、维护者代码、发布说明与状态页；所有部署 / 链上验收仍未执行

## 从这里读

| 阅读篇 | 完整解释的问题 | 旧 PPT |
| --- | --- | --- |
| [01 Ethereum](01-ethereum.md) | 7702 委托与 4337 组合流程；path archive 与历史 proof；binary-tree 研究路线；PeerDAS / BPO | 23–27、45、47 |
| [02 Solana](02-solana.md) | Alpenglow 两轮证书；slot / bank / block；bank-aware 消费；v1 大交易、200ms slot 与有效高度 | 36–37、49–50 |
| [03 多链](03-multichain.md) | Polygon 退役后各产品的边界；Agile Coretime 资源流程；IBC v2 与共享安全 | 38–42 |
| [04 稳定币](04-stablecoins.md) | USDS / sUSDS、LitePSM、SKY治理；USDe支持组合；CCTP跨链与故障恢复；旧Tether版本 | 28–35、41、46、51 |
| [05 AWS](05-aws-infrastructure.md) | AMB后的自管/托管访问、Query索引替代、双读迁移；HSM新硬件与SDK；Ed25519签名 | 55–59 |
| [06 Bitcoin 工程](06-bitcoin-wallets.md) | MuSig2完整协作；descriptor / PSBT；cluster mempool / RBF；Testnet4与Taproot通道 | 15–22、43–44、55–59 |

每篇包含升级动机、核心对象、流程、教学例、收益与剩余边界、自测和迁移验收。不同篇中的序号是阅读次序，不表示发生顺序或版本优劣。

## 旧内容 → 新机制 → 当前状态

下面的状态按各篇所引一手资料表述。“官方称已上线”不等于本次独立运行测量，“标准已定义”也不等于所有客户端支持。

| 旧内容 | 应接着学习什么 | 状态 / 重要边界 | 详细说明 |
| --- | --- | --- | --- |
| EOA 没有代码、单次签名就是支付 | EIP-7702 外层交易、authority 授权、持久委托与撤销 | Pectra 已启用；原始私钥仍存在，委托不是一次性支付授权 | [Ethereum](01-ethereum.md) |
| AA 只是一句 UserOperation | EntryPoint、Bundler、Paymaster、keyed nonce 与 7702 组合 | 上层设施有版本；v0.8/v0.9 支持不能外推任意服务 | [Ethereum](01-ethereum.md) |
| 归档 = 所有旧哈希树、固定容量 | path archive 反向历史、索引、trie-node retention | 客户端能力；值查询与历史证明分开，不能补回已丢历史 | [Ethereum](01-ethereum.md) |
| Verkle 是唯一“下一代树” | unified binary tree 与 witness / 无状态验证 | 当前研究 / Draft；不能说主网已换树或已全面抗量子 | [Ethereum](01-ethereum.md) |
| 扩容只是提高 TPS / 每节点下载全部 blob | PeerDAS 纠删码、列、KZG、custody / sampling、BPO | Fusaka已启用；后续参数分阶段；不保证所有L2费率下降 | [Ethereum](01-ethereum.md) |
| Solana 固定 PoH + TowerBFT / 400ms | Votor certificates、快慢路径、独立 slot 缩短 | 官方称Alpenglow已启用；Rotor未排期，slot已为200ms | [Solana](02-solana.md) |
| 一个 slot 就是一个观察桶 | bank-scoped 数据、UpdateParent、事件幂等与重连 | 特定接口 / 版本能力；bank_id不是跨供应商全局身份 | [Solana](02-solana.md) |
| 固定1232字节、按旧ComputeBudget解析 | v1 message config、4096字节、读取版本与签名适配 | v1官方称已上线；legacy/v0限制不随之全部放宽 | [Solana](02-solana.md) |
| Polygon = zkEVM运行中的单一L2方案 | PoS、CDK模式、Agglayer证明、产品编排 | zkEVM Mainnet Beta退役；其他方案不是无条件同安全替代品 | [多链](03-multichain.md) |
| 长期slot拍卖、固定资源租期 | bulk / on-demand Coretime、region、拆分、更新、共享安全 | Agile Coretime现行机制；JAM等另标计划，资源不等于安全所有权 | [多链](03-multichain.md) |
| IBC只连Cosmos、通信即安全共享 | IBC版本化对象、router / client / payload、ack / timeout与ICS | 跨生态通信与共享安全分开，具体路线仍逐项核查 | [多链](03-multichain.md) |
| Cosmos Hub旧ICS教程可作今天provider入口 | provider/consumer安全机制与Gaia现行模块分开 | 官方当前Hub资料与v28发布说明已移除provider，旧流程仅作历史/通用机制 | [多链](03-multichain.md) |
| DAI / USDS都是Vault借出的同一种币 | Converter、LitePSM、sUSDS份额与SKY新治理 | 已有接口 / 官方迁移声明；不同路径有不同参数与控制权 | [稳定币](04-stablecoins.md) |
| USDe永远stETH + ETH空单 | 动态支持组合、风险限额、OES、reserve buffer | 文档类别不等于本次实时敞口；对冲不消除托管 / funding风险 | [稳定币](04-stablecoins.md) |
| 跨链USDC一定锁住再铸包装币 | CCTP原生burn-and-mint、attestation、Fast/Standard、hooks恢复 | 当前产品能力，路线版本须匹配；不是原子无风险搬钱 | [稳定币](04-stablecoins.md) |
| 旧USDT链只是同名另一入口 | 网络 / 资产支持状态与清退模式 | 停止直接发行 / 赎回不等于所有链上转账被禁 | [稳定币](04-stablecoins.md) |
| AMB是新建钱包默认基建 | 可替换RPC + 自管或托管索引、双读切流、单一业务付款 | 2026-10-29停新客户，2027-09-29终止；无唯一官方“新版AMB” | [AWS](05-aws-infrastructure.md) |
| HSM统一旧世代、KMS仅记secp256k1 | hsm2m与SDK5迁移；KMS Ed25519 RAW语义 | 官方支持；算法 / 硬件 / 接口 / 认证分开验收 | [AWS](05-aws-infrastructure.md) |
| 多签就是相加、PSBT一个格式、fee只看一笔 | BIP327协作、PSBT v2/371、cluster/chunks、现代RBF | 标准和客户端分别演进；不能泛指任意设备或节点 | [Bitcoin](06-bitcoin-wallets.md) |
| Testnet是统一测试链 | Testnet4 genesis与BIP94例外 | 新测试网络，不自动迁移旧余额，不替代主网规则 | [Bitcoin](06-bitcoin-wallets.md) |

## “升级”其实有四种操作

这是本次整理的理解框架：

```text
协议启用：链上有效性 / 执行规则变化
客户端更新：数据库、RPC、mempool、消息解码能力变化
产品迁移：某服务退役、某资产或治理接口被替换
研究方向：目标与提案变化，尚不能执行成现行规则
```

不加区分会导致常见错误：

- path 数据库上线，被误写成主网承诺树已经更换；
- 供应商提供新 RPC，被误写成所有用户必须搬资产；
- 某份硬件认证，被误写成所有链签名算法都获支持；
- 规范写了阈值，被误写成现网固定延迟保证；
- EIP / SIMD 状态与网络实际启用不一致时，只看状态栏下结论。

## 学习顺序

先读与自己任务相关的一篇，再回到基础篇核对不变的原理：

1. 钱包签名 / 托管：Ethereum → AWS → Bitcoin。
2. 充值监听 / 索引：Solana → Ethereum历史状态 → AWS索引替代。
3. 稳定币支付 / 跨链：稳定币 → 多链 → 各链钱包适配。
4. 公链 / 扩容系统：Ethereum PeerDAS → 多链 → Solana共识。

每篇的教学数值只验证机制，不代表当前费率、容量、资产比例或执行成功。下一步实验使用 [实验模板](../templates/experiment-note.md)，先离线与本地链，真实资产 / AWS资源另需明确授权。

## 时效的维护方法

- 保留旧资料，追加替代入口和适用版本，不静默改写附件。
- 给每个升级记“日期 + 对象 + 状态证据 + 不适用范围”。
- 对源码 / 文档矛盾选择更具体证据，并保留矛盾说明；不拼成虚假的统一现状。
- 新机制没有直接替代物时，写清“新架构的选择与迁移职责”，不硬造一个后继产品。
- 性能、吞吐、费用和资产配置没有同期测量时不补伪精确数字。

返回 [专题首页](../README.md)、[纠错表](../corrections.md)、[来源导航](../sources.md)。
