# 零基础与行业篇：协议、来源漂移和教学边界复核

- 核验日：2026-10-29（北京时间，UTC+8）。
- 对象：[入门篇](../beginner-guide.md)、[行业现状](../industry-status-2026-10-29.md)。
- 方法：直接读取官方开发指南、规范、维护者源码及后续公告；与既有来源表和升级教程对读。
- 边界：没有执行钱包、节点、合约、支付或链上迁移；没有把读网页写成主网测量。

## 1. Bitcoin：从通俗解释追到独立验证

再次直接读取 Core v30.0 的 `pow.cpp`、`src/kernel/chainparams.cpp`、`validation.cpp`：

- `CheckProofOfWorkImpl`：哈希数值不大于目标。
- `ContextualCheckBlockHeader`：声明的 nBits 必须等于 `GetNextWorkRequired` 的结果，不能只检查自己声明的宽松目标。
- 主网 600 秒目标间隔、14 天目标跨度、210000 块减半；目标调整使用历史时间并限幅。
- `GetBlockSubsidy` 与 `bad-cb-amount`：新增补贴和已有手续费分别计算，超额奖励仍被拒绝。

来源：[pow.cpp](https://github.com/bitcoin/bitcoin/blob/v30.0/src/pow.cpp)、[主网参数](https://github.com/bitcoin/bitcoin/blob/v30.0/src/kernel/chainparams.cpp)、[validation.cpp](https://github.com/bitcoin/bitcoin/blob/v30.0/src/validation.cpp)。基线版本用于复查，不当成最新推荐。

另读 [Core 32.1 正式发布](https://bitcoincore.org/en/releases/32.1/)与 [v32.1 pow.cpp](https://github.com/bitcoin/bitcoin/blob/v32.1/src/pow.cpp)，确认不能把“32.0 tag 存在”写成正式已发布；新版本的目标检查与调整仍须按实际源码解释。

教学交叉资料：[交易](https://developer.bitcoin.org/devguide/transactions.html)、[区块](https://developer.bitcoin.org/devguide/block_chain.html)、[挖矿](https://developer.bitcoin.org/devguide/mining.html)、[钱包](https://developer.bitcoin.org/devguide/wallets.html)、[支付](https://developer.bitcoin.org/devguide/payment_processing.html)、[P2P](https://developer.bitcoin.org/devguide/p2p_network.html)、[白皮书](https://bitcoin.org/bitcoin.pdf)。

不复制旧开发指南中的即时补贴、容量或费用数字作为当前值；0.10 BTC 付款和四位哈希均明确为人为教学例。

## 2. Ethereum：基础指南存在旧式简化，后续规范优先

[账户指南](https://ethereum.org/developers/docs/accounts/)适合理解公私钥、账户和钱包，但不能用“EOA 没有代码”的旧模型排除 7702 的现行委托行为。另以 [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702)、[Pectra](https://ethereum.org/roadmap/pectra/)及 [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337)核对持续授权和账户角色。

基础费例子参考 [Gas](https://ethereum.org/developers/docs/gas/)及 [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559)，但限定 21000 gas 示例为无代码、未委托账户的简单支付；合约/额外数据/7702 与 blob 不沿用该成本。算例的 8+1 gwei 不是当前费率。

代币与应用新对象分别核对 [ERC-20](https://eips.ethereum.org/EIPS/eip-20)、[ERC-721](https://eips.ethereum.org/EIPS/eip-721)、[ERC-4626](https://eips.ethereum.org/EIPS/eip-4626)、[预言机](https://ethereum.org/developers/docs/oracles/)、[MEV](https://ethereum.org/developers/docs/mev/)；接口标准不自动授予版权、公司股权或收益保证。

## 3. Glamsterdam：不能从到期日反推上线

来源链：

1. [路线图](https://ethereum.org/roadmap/glamsterdam/)仍有开发网测试、Q4 预期及 Hoodi 日期，页面更新时间和公告不同。
2. [2026-10-16 Hoodi 公告](https://blog.ethereum.org/2026/10/16/glamsterdam-hoodi-announcement)正文原计划 10-26 激活，并说明 Sepolia 10-06 已激活；其顶部追加延期通知。
3. [2026-10-22 延期公告](https://blog.ethereum.org/2026/10/22/glamsterdam-hoodi-delay)明确取消 Hoodi 原排期与 200M 配套调整，新日期未设。

采用第 3 项较新、专门的状态公告，保留第 2 项用于 ePBS/BAL/状态定价设计解释。不声称 Hoodi 已上线、不声称 Ethereum 主网已上线、不把撤销未来配置写成回滚现有历史。没有查到替代日期或完成的独立网络测量，保留未知。

[Fusaka](https://ethereum.org/roadmap/fusaka/)则明确记载 2025-12-03 已上线。其介绍中的 BPO2 示例与既有配置核验有口径差异，本次行业概览不填即时 target/max；实现时按对应配置和网络重新确认。

## 4. Solana、多链与生命周期

- [Alpenglow 英文当前页](https://solana.com/upgrades/alpenglow)：官方启用声明、Votor 与未来 Rotor 分开；约 150ms 只标目标。
- [大交易升级](https://solana.com/upgrades/larger-transaction-sizes)：v1 与 legacy/v0 限制分开，不把所有交易放宽。
- [Coretime](https://docs.polkadot.com/reference/polkadot-hub/consensus-and-security/agile-coretime/)：资源调度与共享安全分开，elastic 具体部署不靠介绍页推定。
- [当前 Gaia 文档](https://docs.cosmos.network/hub/latest/getting-started/what-is-gaia)：明确 ICS provider 移除；通信功能不是旧 provider 仍提供的证据。
- [Polygon zkEVM](https://polygon.technology/polygon-zkevm)：退役与 EOA Claims 限制，不扩展至合约锁定资产。
- [AMB 公告](https://docs.aws.amazon.com/managed-blockchain/latest/hyperledger-fabric-dev/managed-blockchain-end-of-support.html)：结束接纳新客户与终止支持是不同日期。

以上都是官方资料状态核验，不是执行 feature gate、Claims 或供应商迁移的验收。

## 5. DeFi 教学模型不当最新部署承诺

[Uniswap 旧路径](https://docs.uniswap.org/contracts/v2/concepts/protocol-overview/how-uniswap-works)已重定向至 [当前概念页](https://developers.uniswap.org/docs/get-started/concepts/how-uniswap-works)；旧 v2 收益页迁到 [新域名](https://developers.uniswap.org/docs/protocols/v2/concepts/understanding-returns)。入门篇使用新路径，将恒定乘积标为最简单教学模型，不推断全部版本。

[Aave 清算](https://aave.com/help/borrowing/liquidations)支撑健康因子解释；数值由本教程另设。原尝试的 flash-loans smart-contracts 路径未取到正文，改为 [当前指南](https://aave.com/docs/aave-v3/guides/flash-loans)。Aave 文档允许部分 `flashLoan` 路径在满足条件时开债务头寸，不能把“全部调用无条件立即还款”写成统一实现规则。

再质押只作概念风险分类，不提供某个产品的实时惩罚参数或收益。支付、基金和制度的 12 条专门来源及访问限制另见 [后台研究记录](beginner-industry-source-audit.md)。
