# 06 时段与公司行动：周末价格、分红与拆股如何影响仓位

研究日期：2026-11-04。[上一章](05-margin-and-liquidation.md) · [返回专题](README.md) · [下一章：风险与保护](07-risk-and-protection.md)

## “24/7”要拆开四个时钟

| 时钟 | 要检查什么 |
| --- | --- |
| 合约时钟 | 可否挂单、开仓、减仓，有无维护或暂停 |
| 外部行情时钟 | 正常交易、盘前、盘后、隔夜、节假日分别提供什么数据 |
| 对冲渠道时钟 | 自己或做市商实际能否交易真实股票，不只看有没有行情 |
| 风险时钟 | 资金费、Mark、保证金、触发单与清算是否继续运行 |

因此“我周末能点买入”不证明“有一个同样深、同样可对冲的股票市场”。合约连续交易与底层证券有连续可执行的外部价格是两件事。[时段与流动性风险](https://docs.trade.xyz/legal-and-disclaimers/perpetuals-risks-and-disclaimers)

## 当前 XYZ 的美股外部时段

截至查阅日，XYZ 的 US 页面描述从周日 **20:05 ET 到周五 20:00 ET** 的 24/5 外部覆盖，组合了：

- 盘前：04:00–09:30 ET。
- 正常交易：09:30–16:00 ET。
- 盘后：16:00–20:00 ET。
- 隔夜：20:05–04:00 ET，文档列出 Blue Ocean ATS。

这是部署方的外部行情说明，不是所有股票、所有交易者都能在这些时段获得相同深度或可执行权限。具体标的还要读规格表、节假日、停牌和更新公告。[US 股票页面](https://docs.trade.xyz/perpetuals/markets/stocks/us) [规格表](https://docs.trade.xyz/perpetuals/specifications-and-schedules/specification-index) [节假日](https://docs.trade.xyz/perpetuals/specifications-and-schedules/holiday-closures)

时间使用来源的 ET，而不是固定 UTC 偏移：美国东部时间有夏令时；换算北京时间时应按交易日期确认。不要把整年的 09:30 ET 固定当作同一个北京时间。

## 周末是怎样的一种市场

虚构场景：周五外部股票最后参考 100；周六有公司新闻，合约买卖愿意在 108 附近交易。

XYZ 外部输入不可用时会以内部盘口信息推进 Oracle，而不只是冻结 100。具体 Mark、资金费与可发现范围仍受规则控制；外部市场恢复后，Oracle 再回到外部定价。[内部 Oracle](https://docs.trade.xyz/perpetuals/mechanics/oracle-price) [价格边界](https://docs.trade.xyz/perpetuals/mechanics/discovery-bounds)

这意味着“外部股票尚未重新成交”期间也可能有清算。价差套利者未必能同时交易证券那一腿，所以纠偏力度可能下降。后者是对两类交易时钟的机制推导，不是对某个周末成交质量的测量。

## 分红：股价收益不等于总回报

假想股票从 100 除息到 98，公司每股派现金 2。忽略税、其他价格变化与费用：

| 持有对象 | 股价盈亏 | 现金分红 | 教学合计 |
| --- | --- | --- | --- |
| 10 股真实股票 | -20 | +20 | 0 |
| 10 单位未做分红调整的价格永续 | -20 | 没有股东股息权 | -20，尚未计资金费 |

这个表**不是在宣称 XYZ 对每次分红都这样结算**。它只说明：如果产品追踪未调整的股票价格而无额外调整，总回报会与持股不同。XYZ 当前政策说现金分红通常不暂停交易，持有人不直接收到股息，经济影响可经定价、资金费与股票套利体现；但资金费不是固定股息支付，也不能保证完全复制持股税后结果。其他合约须单独看公告和规格。[股票与股息](https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks) [公司行动](https://docs.trade.xyz/perpetuals/corporate-actions) [合约披露](https://docs.trade.xyz/legal-and-disclaimers/perpetuals-risks-and-disclaimers)

## 拆股：数量和价格都要一起处理

假想 2:1 拆股：原来 10 股、每股 100，在不考虑其他价格变化时成为 20 股、每股 50，总市值仍是 1,000。

如果合约机械地把参考价从 100 改成 50，而数量仍按原来 10 单位解释，就会制造本不该有的经济损益。因此需要有公司行动处理机制，不能自行假设一定沿用券商处理方式。

**XYZ 当前的一般拆股 / 反向拆股政策是：结算已有仓位、实现盈亏、取消未成交订单，再按拆股后单位重开。** 想恢复敞口，需要重新开仓、重新提交订单；不是自动保留旧仓位并按比例增加单位。具体时点和结算价仍看当次事件公告；其他部署方可能采用不同方式。[XYZ corporate actions](https://docs.trade.xyz/perpetuals/corporate-actions)

同理，合并、分拆、收购、退市、停牌、代码变化与 ADR 比例都可能改变参考对象。应追问：**仓位、挂单、参考证券和结算价格分别怎样处理**，而不仅看图表是否变得连续。

## 限价、止损与 reduce-only 在事件里

事件暂停可能取消订单；恢复时可能跳价；达到持仓上限或进入 reduce-only 可能限制新增风险，但不保证原仓位退出时有足够对手。历史有效的止损价或限价，在拆股后也不能不加核对地继续使用。[规格与持仓上限](https://docs.trade.xyz/perpetuals/specifications-and-schedules/specification-index) [流动性与规格风险](https://docs.trade.xyz/legal-and-disclaimers/perpetuals-risks-and-disclaimers)

来源组：[S09 时段](sources.md#s09)、[S18 公司行动](sources.md#s18)、[S20 逐标的规格](sources.md#s20)。

## 自测与答案

1. 正常证券交易所收盘后是否一定没有外部价格？——否，还可能有盘后、隔夜等所选来源。
2. 周末合约上涨是否证明真实股票已在相同价格成交？——否，可能是内部市场定价。
3. 拆股后单股价格减半是否说明投资者资产损失一半？——不应如此，真实股票数量同时变化；合约须看自己的调整规则。
