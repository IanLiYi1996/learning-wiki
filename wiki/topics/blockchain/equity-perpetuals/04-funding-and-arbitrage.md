# 04 资金费、基差与套利：为什么价格会靠近，也为什么会脱开

研究日期：2026-11-04。[上一章](03-prices-and-anchoring.md) · [返回专题](README.md) · [下一章：保证金与清算](05-margin-and-liquidation.md)

## 永续少了一个到期日，就需要持续激励

有到期日的衍生品可以依靠到期结算规则形成收敛约束。永续通常没有这样的自然终点，所以资金费用于持续改变多空持仓的经济成本。Hyperliquid 的资金费是多空间的转移，不是平台对这笔转移另收一份交易费；平台交易费应分开计算。[Funding](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding)

直觉是：合约持续偏贵，机制通常提高多头相对成本，吸引卖出力量；持续偏便宜，则激励往往相反。但这不是“最后成交价比股票高，下一小时一定多付空”的简单判断。费率使用 premium 相关输入、时间统计、利息和部署参数；XYZ 还有自己的公式更新说明。[XYZ funding updates](https://docs.trade.xyz/perpetuals/changelog/funding-rate-formula-updates)

## 算金额时用名义仓位，不是保证金

采用有符号数量 $q$：正数为多头，负数为空头。已知某个结算周期的费率 $r$ 和当时 Oracle $O$，账户资金费现金流可写为：

$$
\mathrm{FundingCashflow}=-qOr.
$$

$r>0$ 时多头支付、空头收取；$r<0$ 时反过来。这只算支付金额，不从价格差推导费率。Hyperliquid 按小时转移资金费；请核对界面展示的是小时、8 小时还是年化口径。[支付口径](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding)

教学例：$q=100$、$O=100$，名义仓位 10,000；假定每小时费率为 **0.001%=0.00001**：

- 多头每小时支付 0.1 USDC。
- 假定仓位、Oracle 和费率整天不变，24 小时支付 2.4。
- 同样假定持续 365 天，支付 876，即名义仓位的 8.76% 简单年化。
- 如果只用了 1,000 保证金，这笔 876 是初始保证金的 87.6%，不是 8.76%。

这些是恒定假设的算术，不是市场当前费率或未来收益。不要把小时费率、资金费年化、复利 APY、保证金回报率混用。[离线实验 B](lab.md#lab-b)

## 想再深一层：价格差怎样变成费率

HIP-3 的 premium 输入不是最后成交价差，而是：

$$
P_t=\frac{P_{\mathrm{impactBid},t}+P_{\mathrm{impactAsk},t}}{2O_t}-1.
$$

协议通用的八小时基准表达是：

$$
F_{8,\mathrm{base}}=\bar P+\operatorname{clamp}(I-\bar P,-c,c).
$$

其中 $\bar P$ 是周期内采样后平均的 premium；$I$ 是利息项；clamp 把括号内值限制在上下界。部署方可以配置 multiplier、利息与 clamp；实际支付还要转换成小时口径并应用相关控制。这里没有把未核实的配置与封顶顺序拼成一个“当前 XYZ 全市场完整公式”。[协议公式](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding) [参数与版本差异](sources.md#version-and-unknowns)

一个**纯假设**：$I=0.01\%$、$c=0.05\%$，平均 premium 为 $-0.02\%$，则基准八小时率为：

$$
-0.02\%+\operatorname{clamp}(0.03\%,-0.05\%,0.05\%)=+0.01\%.
$$

这解释为什么“轻微折价”不必然意味着空头付多头，也说明即时报价、平均 premium 和最终费率不能互相替代。此处是教学参数，不是对真实市场费率的计算。[S12](sources.md#s12) [S13](sources.md#s13)

## 基差与套利的完整算例

定义本章的美元基差：

$$
b=P_{\mathrm{perp}}-P_{\mathrm{stock}}.
$$

假设每单位合约参考一股，股票 100，合约 102。买 10 股股票、做空 10 单位合约。之后股票和合约都到 105：

| 项目 | 计算 | 毛盈亏 |
| --- | --- | --- |
| 股票多头 | $10(105-100)$ | +50 |
| 永续空头 | $-10(105-102)$ | -30 |
| 合计 | 两条腿之和 | +20 |

一般地，忽略分红、费用、资金费和汇率变化：

$$
\mathrm{CombinedPnL}=q(b_{\mathrm{entry}}-b_{\mathrm{exit}}).
$$

所以盈利来自基差 2 缩到 0，不要求股票下跌。买股票、卖偏贵的合约形成纠偏力量。这是机制推导，不是已执行的套利，也不保证存在可用借券、订单深度或最终收敛。[实验 D](lab.md#lab-d) [价格偏离风险](https://docs.trade.xyz/legal-and-disclaimers/perpetuals-risks-and-disclaimers)

## 为什么“中性”仍可能大亏

如果之后股票仍为 100，合约却涨到 110，两条腿合计亏 80。即使很久以后价差归零，空头账户也可能已经追加不了保证金并被清算。

还要考虑：

- **两条腿不同时成交**：先成交的一边会短暂暴露方向风险。
- **证券融资 / 借券**：反向套利需要做空股票时，可能借不到、成本高或被召回。
- **费用与流动性**：毛价差覆盖不了手续费、点差、滑点和资金成本。
- **休市**：合约可交易时，真实股票或可访问的证券渠道未必能成交。
- **跨账户资金**：股票浮盈不能自动补链上保证金，提现与转账也未必及时。
- **资金费变号、分红与 USDC 汇率**：都可能改变持有期结果。

证券做空、借券、利息与股息责任见 [Investor.gov](https://www.investor.gov/introduction-investing/investing-basics/how-stock-markets-work/stock-purchases-and-sales-long-and)；合约成本与风险见 [XYZ 披露](https://docs.trade.xyz/legal-and-disclaimers/perpetuals-risks-and-disclaimers)。以上清单是把官方机制拼接后的风险推导，不是在评价某一个可交易策略。

来源组：[S12 通用资金费](sources.md#s12)、[S13 XYZ 参数边界](sources.md#s13)、[S14 交易成本](sources.md#s14)、[S18 股息差异](sources.md#s18)。

## 自测与答案

1. 资金费按 1,000 保证金还是 10,000 名义仓位算？——按该时点数量与 Oracle 对应的名义价值。
2. 资金费年化 8.76% 是否意味着可以稳定赚 8.76%？——否，符号、费率、仓位价值和其他成本都可能变。
3. 基差套利是不是两边涨跌抵消后就无风险？——否，剩余基差、执行、融资与清算风险。
