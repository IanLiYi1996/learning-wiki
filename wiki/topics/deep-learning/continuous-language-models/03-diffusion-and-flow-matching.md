# 03 连续动力学：训练的是预测器，生成还要经过求解

核查日期：2026-11-11。[专题导读](README.md) · [原始 FM 与 FLM 来源](sources.md#dynamics)。

## 1. 本篇的时间约定

令 $x_0$ 是噪声，$x_1$ 是干净连续表示，生成时间从 0 到 1。一个简单路径是：

$$
I_t=(1-t)x_0+t x_1.
$$

训练可独立采数据、噪声和一个 t，构造中间状态；不必先运行整个生成轨迹。Conditional Flow Matching 用可计算的条件路径监督速度场，这种训练接口不等于所有模型都走完全相同的轨迹。[Flow Matching 原论文](https://arxiv.org/abs/2210.02747v2)

“单个条件插值是直线”也不意味着边缘概率 flow 的每条轨迹都是直线。网络要在同一状态下综合可能的数据与噪声配对，条件平均会随状态改变。

## 2. Velocity 与 denoiser 的转换

对上述直线插值，记最优 denoiser 为 $D_t(x)=\mathbb{E}(x_1\mid I_t=x)$。在 $t<1$ 时：

$$
b_t(x)=E[x_1-x_0\mid I_t=x]
       =\frac{D_t(x)-x}{1-t}.
$$

最后一式可由 $x=(1-t)x_0+t x_1$ 取条件期望得到。网络可直接预测 velocity，也可预测干净表示并转换为 velocity。

转换依赖路径、时间方向和参数化。终点分母为零时，不能把这段表达式直接当成数值调用；需要端点 readout 或适当极限／停止规则。[FLM §3.2](https://arxiv.org/html/2602.16813v3)

## 3. 训练预测目标和 loss 也要分开

原创阅读账本：

| 网络输出 | Loss 比较对象 | 需要额外说明 |
| --- | --- | --- |
| 干净表示 | 表示 MSE | 表示、时间权重、decoder |
| 干净 token 概率 | Categorical CE | 概率与条件均值的关系 |
| 干净表示 | 转换后的 velocity MSE | 转换系数改变时间权重 |
| Velocity／score | 对应路径目标 | 噪声分布、几何与边界 |

对 one-hot 数据，token 概率就是干净向量的条件均值，可以用 CE 学习 denoiser。对 contextual latents，一般不能直接用单位置 token 概率的加权 embedding 替代整段条件均值。[FLM](https://arxiv.org/html/2602.16813v3) · [CDCD](https://arxiv.org/abs/2211.15089v3) · [ELF](https://arxiv.org/abs/2605.10938v3)

## 4. 学到速度后，ODE 才生成样本

确定性生成沿

$$
\frac{dx_t}{dt}=b_\theta(x_t,t)
$$

从噪声开始积分。Euler 的一步是 $x_{t+h}=x_t+h b_\theta(x_t,t)$。Heun 先做一次 proposal，再用第二次 velocity 评估修正。

有两个独立误差：网络没有学准目标速度，以及数值求解没有准确跟随已学到的场。多步求解可以降低部分积分误差，不一定修复错误的模型；直接减少步骤也不会让这两种误差消失。

原创 ODE `dx/dt=x, x(0)=1` 的真值在 t=1 是 e。一步 Euler 得 **2**；两步得 **2.25**。模型场完全准确时，求解仍会有误差。这里没有语言模型。

## 5. 带随机性，也要改对应漂移

某些方法使用 SDE 随机轨迹，而不只 ODE。若希望保持指定边缘分布，加入噪声还需相应 score／漂移修正；不能把任意高斯扰动追加到已训练 sampler 后宣称分布不变。

模型参数、几何、时间网格和随机性共同定义采样结果。本文不实现通用 SDE solver，也不将连续时间与系统响应毫秒对应。求解时间 t 是生成坐标，不是用户等到回答的墙钟时间。

下一篇：[04 训练与反馈](04-training-schedules-and-self-conditioning.md)。动手：[Euler／Heun 验算](lab.md)。
