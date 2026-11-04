# 01 产品与权利：同一个股票代码，可能不是同一种资产

研究日期：2026-11-04。[返回专题](README.md) · [下一章：市场与仓位](02-market-and-positions.md)

## 先问“拥有什么”，再问“会不会涨”

想象三个界面都显示某股票价格 100。第一个卖真实股份，第二个卖发行人提供的代币，第三个卖股价永续合约。价格图看起来相似，不代表法律权利、现金流和退出方式相同。

真实普通股是公司的所有权份额。经券商以 street name 持有时，登记链和实际投资者之间有中介，但不能因此把股份说成“只是券商的价格模拟”。分红取决于公司是否派发，投票权取决于股份类别与持有安排；并非每只股票都付股息或拥有相同投票权。[股票基础](https://www.investor.gov/introduction-investing/investing-basics/investment-products/stocks)

XYZ 永续则明确不赋予底层资产的所有权、分红、投票、赎回、兑换或交付权。盈利是一笔合约现金结算结果，不是公司把营业利润直接转给合约多头。[永续权利披露](https://docs.trade.xyz/legal-and-disclaimers/perpetuals-risks-and-disclaimers)

## 一张不依赖品牌的分类表

| 产品 | 实际对象 | 价格接近股票的原因 | 核心追问 |
| --- | --- | --- | --- |
| 券商中的真实股票 | 公司股份 | 直接交易股票本身 | 股份类别、托管、交易与公司行动 |
| 股票 ETF | 基金份额，不是每家成分公司的直接股东身份 | 基金资产、组合及申赎机制 | 跟踪什么、费用、份额与底层资产 |
| 有证券储备的股票代币 | 由具体发行结构定义的权利 | 储备、申购赎回和市场交易，视规则而定 | 谁持有储备、谁能赎回、破产时有什么权利 |
| CFD / 差价合约 | 与对手方按差价结算的合同 | 报价及合同结算规则 | 对手方、资金隔离、费用和清算 |
| 有到期日的期货 | 标准化或协议定义的衍生品 | 套利及到期结算 / 交付约定 | 到期日、乘数、现金还是实物结算 |
| 股票永续 | 没有通常到期日的股价衍生品仓位 | 参考行情、资金费与套利激励 | 预言机、保证金、费率、休市与异常结算 |

这张表是机制分类，不声称每个平台都提供所有产品。ETF 不是股票代币，股票代币也可能采取不同结构，不能一律归为“直接股份”。ETF 的正式解释见 [Investor.gov](https://www.investor.gov/introduction-investing/investing-basics/investment-products/mutual-funds-and-exchange-traded-2)；Hyperliquid 永续与部署方规则见[合约规格](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/contract-specifications)和 [HIP-3](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals)。原生 Crypto Perps 的计价等细节不是美股永续的统一规格。

## “有储备”还要拆成四个问题

对于声称有证券储备的代币，至少分开判断：

1. **资产**：是否有足够证券，证券由谁、在哪个账户持有？
2. **权利**：代币持有人是直接或间接权益持有人，还是对发行人的合同请求权？
3. **兑换**：自己是否满足申购 / 赎回资格，拿回证券还是现金，有哪些最低金额和时间限制？
4. **失败场景**：发行人、托管人或渠道中断时，储备与投资者的法律关系是什么？

这是读合同的方法，不是替任何产品确认储备。公开余额或储备报告也不独自回答后面三个问题。股价永续更不能因为行情来自真实股票，就被推断为具有这样的储备或赎回通道。

## 全款、融资、产品类型是不同维度

“股票安全、合约危险”太粗糙。全款股票仍有公司经营、价格和中介风险；融资买真实股票又增加了利息、保证金与强平。反过来，把永续杠杆设成 1 倍，仍不产生股东权利，也不消除资金费与跟踪偏差。[证券账户](https://www.finra.org/investors/investing/investment-accounts/brokerage-accounts) [融资账户](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-29)

正确的比较至少有四个轴：**资产 / 合同、是否融资、如何托管、怎样退出**。不应仅比较两个界面的杠杆按钮。

## 自测与答案

1. 合约名叫某公司的代码，是否就拥有该公司股份？——否，要读对象与权利定义。
2. 1 倍美股永续是否就是“稳定币支付的股票”？——否，支付或保证金币种不改变权利对象。
3. 股票代币声称 1:1 储备，是否足以证明自己可以换回股票？——否，需核对自身资格、发行合同与赎回流程。

下一章把“你拥有什么”接到“系统如何记录和结算它”。来源组：[S01 股票权利](sources.md#s01)、[S02 账户](sources.md#s02)、[S03 持有与保护](sources.md#s03)、[S04 股票代币结构](sources.md#s04)、[S19 合约权利](sources.md#s19)。
