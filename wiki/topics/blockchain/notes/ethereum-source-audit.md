# Ethereum 与钱包规范核验

- 查阅日：2026-10-29
- 方法：直接阅读 ethereum.org、EIP/ERC、Solidity 与 Geth 一手资料
- 证据限制：文档核验，不是节点或合约实测；`latest` 文档可能含开发版本

| 编号 | 一手资料 / 定位 | 支持的结论 | PPT |
| --- | --- | --- | --- |
| E01 | [Merkle Patricia Trie](https://ethereum.org/en/developers/docs/data-structures-and-encoding/patricia-merkle-trie/)，State / Storage Trie | 账户四字段、secure trie 路径、状态承诺与逻辑更新；不能把槽位计算和 trie 路径混为一谈 | 23–26 |
| E02 | [EIP-1559](https://eips.ethereum.org/EIPS/eip-1559)，Specification | 类型 2 交易、费用上限与实际单价、Keccak 签名消息 | 45 |
| E03 | [EIP-1186](https://eips.ethereum.org/EIPS/eip-1186)，Specification / Proofs for non existent values | 账户和存储证明需要可信根；接口名称沿用 eth_getProof，规范状态不代表每家 RPC 都支持 | 24–25 |
| E04 | [EIP-7702](https://eips.ethereum.org/EIPS/eip-7702)，Behavior / Security Considerations | EOA 代码委托持久；处理授权增加 nonce；后续执行失败不回滚委托；实现拥有广泛控制能力 | 23、45、47 |
| E05 | [Pectra](https://ethereum.org/en/roadmap/pectra/)，上线与 EOA account code | 主网 2025-05-07 启用，包括 EIP-7702；不是仅提案 | 23、47 |
| E06 | [ERC-1967](https://eips.ethereum.org/EIPS/eip-1967)，Abstract / Specification；[Solidity address calls](https://docs.soliditylang.org/en/latest/types.html#members-of-addresses) | 代理的 storage 与实现逻辑区分；实现/管理员变更可影响行为；内部调用可携带 ETH value | 23、46–47 |
| E07 | [Solidity Storage Layout](https://docs.soliditylang.org/en/latest/internals/layout_in_storage.html)，Mappings / JSON Output | slot、packing、mapping 键补齐；latest 查阅时显示 0.8.39-develop，不把它指定成生产编译器版本 | 24 |
| E08 | [Ethereum JSON-RPC](https://ethereum.org/en/developers/docs/apis/json-rpc/)，balance / transaction count / receipt / logs | 标签与网络查询；receipt 状态及日志 removed；索引必须保存 blockHash | 45–46、50 |
| E09 | [ERC-20](https://eips.ethereum.org/EIPS/eip-20)，Methods / Events | decimals 可选，transfer 返回 false 必须处理；规范不强制内部 mapping 布局 | 46 |
| E10 | [Geth Archive](https://geth.ethereum.org/docs/fundamentals/archive)，Path-Based / Historical Trie Node Retention | hash/path 模式容量不同；v1.16.x/v1.17.x 历史 proof 能力有条件；网页日期 2026-02-24 | 26–27 |
| E11 | [ERC-4337](https://eips.ethereum.org/EIPS/eip-4337)，Definitions / nonce / handleOps | UserOperation、EntryPoint、Bundler、Paymaster 与 keyed nonce；版本/API必须一致 | 47、54 |
| E12 | [Solidity ABI](https://docs.soliditylang.org/en/latest/abi-spec.html)，Function Selector / Events | 函数 selector 与日志主题用 Keccak；有 schema 才能正确解码 | 46–47 |
| E13 | [EIP-712](https://eips.ethereum.org/EIPS/eip-712)，domainSeparator / Replay attacks | 类型化可读不等于安全授权；标准本身不提供完整防重放 | 47 |
| E14 | [ERC-2612](https://eips.ethereum.org/EIPS/eip-2612)，Specification / Backwards Compatibility | permit 修改 allowance，有 nonce/deadline；DAI 早期 permit 接口不同 | 47 |
| E15 | [ERC-1271](https://eips.ethereum.org/EIPS/eip-1271)，Specification | 合约签名验证需要 isValidSignature，不可只恢复 EOA | 54 |
| E16 | [Safe Concepts](https://docs.safe.global/advanced/smart-account-concepts)，Module Transaction | owners/threshold 路径与模块路径不同，模块可绕过常规 owner 签名验证 | 54 |

## 核验结论的使用

来源支持“协议/接口如何定义”，不是“部署一定安全”。钱包的幂等、回滚、业务审批、冷热调拨、外部签名服务输入检查属于本次设计建议，应通过故障测试验证。

没有沿用 PPT 的链高、TPS、盘占用、市值和主观产品评价。Geth 的容量示例只用来反驳统一配置假设，不冒充本环境测量。
