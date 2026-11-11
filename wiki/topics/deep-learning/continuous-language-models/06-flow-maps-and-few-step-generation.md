# 06 少步生成：学习大步映射，不只是把 Euler 步长放大

核查日期：2026-11-11。[专题导读](README.md) · [FLM 与 CFM](sources.md#maps)。

## 1. 三种“一步”先分开

| 方法 | 一次调用想计算什么 | 主要误差／额外代价 |
| --- | --- | --- |
| 大步数值求解 | 用当前 velocity 近似长区间变化 | 可能有很大积分误差 |
| Learned flow map | 直接近似同一 flow 的有限时间变换 | 训练／蒸馏误差；目标是否一致 |
| Direct pushforward／endpoint generator | 将噪声直接变成样本 | 分布学习与 decoder；不必对应两时间 map |

分类是教学接口对照，不将某个 one-step 数字当作所有模型的共同结构。少步求解器与训练过的少步模型也不能混写。

## 2. 精确 map 具有合成关系

对 ODE 的解算子 $X_{s,t}$，有：

$$
X_{u,t}\circ X_{s,u}=X_{s,t},
\qquad X_{s,s}=\mathrm{id}.
$$

它表示“先走 s→u，再走 u→t”与“直接走 s→t”落到同一轨迹点。训练可以用短跳监督长跳。

但 semigroup 与 identity **还不够**确定目标 flow：恒等映射也满足它们，却完全没有移动。还需要相应的切向／对角约束，例如 $\partial_t X_{s,t}|_{t=s}=b_s$，或匹配对角 denoiser。[FLM §3.3 与附录 B](https://arxiv.org/html/2602.16813v3)

这个反例有[离线测试](lab.md)，不用于证明真实神经网络已经恢复数据分布。

## 3. 两时间 denoiser 怎样连接 categorical 目标？

对本读本的直线路径，可将 map 写为：

$$
X_{s,t}(x)=\frac{1-t}{1-s}x+
          \frac{t-s}{1-s}\delta_{s,t}(x),
\qquad \delta_{s,s}=D_s.
$$

普通 Euler 使用瞬时 $D_s$，这里的 $\delta_{s,t}$ 描述跨区间的平均 clean estimate，不是把输入再加一个 t 标签就自动得到。

在相关 one-hot 理论下，沿轨迹的 clean estimates 的适当凸组合仍处于 simplex，所以 categorical CE／KL 可成为学习接口。FLM 与 CFM 采用不同的一致性／蒸馏目标，不把两者统称成一个 loss。[FLM](https://arxiv.org/html/2602.16813v3) · [CFM](https://arxiv.org/abs/2602.12233v1)

## 4. Teacher 与 self-distillation 各有什么条件？

预训练 teacher 提供较稳定的目标，但增加一个训练阶段。Self-distillation 可边学对角、边用自身短跳提供长跳目标，却面对会变化的 teacher target。

原创建议检查：目标来自谁、是否 stop-gradient、对角与非对角怎样混合、是否直接训练完整跳跃、词表／表示是否兼容，以及指导与反馈是否在目标中。

“不需要独立 teacher”不等于“无需训练数据”或“零训练成本”。既有 teacher 的能力也不能直接当作蒸馏后保留的能力。

## 5. 反馈、guidance 与排序必须进入 map 的合同

若多步 teacher 依赖预测反馈 z、tokenwise 时间或有指导的速度场，student 必须处理这些状态或逼近相应的闭合动力学。

否则压缩掉的可能不只是积分步数，还有必要条件和质量收益。比较时应把多步 teacher、少步 student 和同等总预算替代方案分别记录，检查任务、分布覆盖与非目标能力。

## 6. “一步”仍是一个完整系统

最终可能还要 decode、检查长度、保留置信位置、对其他位置重新加噪和生成，或让 AR verifier 验证草稿。网络一步、采样一轮、完整服务一次，是不同单位。

不报告 decoder、guidance、refinement、verification 和硬件条件，就不能从论文 NFE 推出产品响应时延。下一篇：[07 扩展与评测](07-scaling-and-evaluation.md)。
