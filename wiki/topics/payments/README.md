# 支付行业 101：从一杯咖啡到全球资金网络

整理日期：2026-11-02。基于支付网络、中央银行、标准组织、监管与服务商的公开一手资料，按“业务直觉 → 原理 → 商业 → 风险 → 工程”组织。

从一笔买咖啡的支付开始，理解谁批准付款、谁承担资金责任、钱如何到账，以及支付公司怎样赚钱。12 课配有 14 张中文机制图，术语在首次出现时解释，计算与架构示例明确标为教学假设。

## 开始阅读

- [完整图文读本：12 课](payment-industry-101.md)：适合顺序阅读，不需要先背缩写。
- [术语速查](glossary.md)：中文解释、英文缩写与常见误区。
- [学习路线与自测](learning-roadmap.md)：45 分钟快速通读、七天学习、纸上实验与答案。
- [一手来源与核验边界](sources.md)：结论出处、适用地区与报告期。

## 12 课目录

| 课 | 你会搞懂什么 |
| --- | --- |
| [01 支付是什么](payment-industry-101.md#lesson-01) | 钱、账户、凭证、网络与三条流 |
| [02 银行卡的一生](payment-industry-101.md#lesson-02) | 授权、请款、清算、结算、对账和异常 |
| [03 商户受理生态](payment-industry-101.md#lesson-03) | Acquirer、Processor、Gateway、PSP、PayFac、MoR |
| [04 费用与商业模式](payment-industry-101.md#lesson-04) | MDR、Interchange、TPV、Take Rate、利润与现金 |
| [05 钱包与发卡](payment-industry-101.md#lesson-05) | 余额、凭证、Token、虚拟卡和消费控制 |
| [06 账户与实时支付](payment-industry-101.md#lesson-06) | A2A、ACH、RTGS、区域方案、开放银行与中国生态 |
| [07 跨境与企业支付](payment-industry-101.md#lesson-07) | SWIFT、往来账户、FX、预注资、PvP、CIPS、AP/AR |
| [08 风险与合规](payment-industry-101.md#lesson-08) | 认证、欺诈、AML、制裁、PCI、客户资金与争议 |
| [09 账本与支付工程](payment-industry-101.md#lesson-09) | 状态机、幂等、Webhook、复式记账和对账 |
| [10 研究一家支付公司](payment-industry-101.md#lesson-10) | 责任链、财务口径与技术需求证据 |
| [11 稳定币与代理](payment-industry-101.md#lesson-11) | 嵌入式支付、信用产品、新 Rail 与代理权限 |
| [12 完整平台案例](payment-industry-101.md#lesson-12) | 把产品、资金、风险、账务和工程拼起来 |

## 阅读约定

- **外部核验**：正文附近链接到公开一手来源。
- **教学示例**：交易、费率、账务与架构用于说明机制，不是生产测量。
- **待验证假设**：技术或商业机会需要合同、牌照、财报与项目证据。

主要目标是建立可迁移的行业理解，不是全球牌照或法规大全。证券结算、完整信贷风控与各国税务不在展开范围；监管段落不是法律意见，财务段落不是投资建议。

## 配图与关联阅读

图解提供本地 SVG 源图与 2× PNG，无图片热链。网页可点击放大，Markdown 和离线导出使用 PNG 后备。图示不代表任何公司的实际部署。

重建本专题配图，不改其他主题：

```bash
python scripts/render_figures.py --embed --id-prefix payment-
python scripts/render_figures.py --check --id-prefix payment-
```

继续阅读：[区块链与钱包工程](../blockchain/README.md)，对照传统支付与链上资金轨道。两者的凭证、最终性、资金权利与消费者保护不能机械互换。
