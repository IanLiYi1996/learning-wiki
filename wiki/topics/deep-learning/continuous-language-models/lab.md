# 五个离线生成练习：联合分布、求解、映射与测量

整理日期：2026-11-11。[专题导读](README.md)。本页只用合成分布和一个标量 ODE，不运行 diffusion LM、FLM、CFM、teacher 或 decoder。

Python 3.9+ 标准库；无网络、GPU、权重和付费服务。共用脚本：[memory_and_flow_lab.py](https://github.com/IanLiYi1996/learning-wiki/blob/main/scripts/memory_and_flow_lab.py)；测试：[test_memory_and_flow_studies.py](https://github.com/IanLiYi1996/learning-wiki/blob/main/tests/test_memory_and_flow_studies.py)。新文件未发布时，源码网页链接可能尚不存在。

```bash
python -B scripts/memory_and_flow_lab.py --group flow
python -B -m unittest discover -s tests -p 'test_memory_and_flow_studies.py' -v
```

## A. 两个正确 marginals，仍可能错一半

`factorization_error(((.5,0),(0,.5)))` 的两个 marginals 均为 `(0.5,0.5)`；其乘积把质量均匀分到四个组合。真实 joint 为零的格子得到 **0.5** 质量，TV 距离也是 **0.5**。

这不是一个训练得到的语言模型。矩阵须矩形、非空、非负、规范化；“非法格子”按输入 joint 的严格零定义，不把很小概率擅自归零。

## B. 准确 velocity，也会被 Euler 近似

对 `dx/dt=x, x(0)=1, duration=1`，真值为 e：

| 方法 | 步数 | NFE | 结果 |
| --- | ---: | ---: | ---: |
| Euler | 1 | 1 | 2 |
| Euler | 2 | 2 | 2.25 |
| Euler | 4 | 4 | 2.44140625 |
| Heun | 1 | 2 | 2.5 |

Heun 一步需要两次 velocity 评估；比较表面步数会误判预算。教学 solver 的步数上限为 10,000，非法方法、类型、非有限值和结果溢出拒绝。

这只展示数值误差，不证明 Heun 在任何语言模型上都是最佳 sampler。

## C. Semigroup 不能单独识别目标 flow

`map_contract(0,.5,1,1)` 比较三种明确写出的 map：

- 真解 `exp(t-s)×x`：合成误差近零。
- 大步 Euler `(1+t-s)×x`：合成误差 **0.25**。
- 恒等 map：合成误差 **0**，但对目标 `dx/dt=x` 的 velocity 误差 **1**。

所以只测“短跳等于长跳”，会漏掉完全不动的错误解。这里没有神经网络、自蒸馏训练、分布学习或真实模型 collapse。

## D. Probability guidance 可以离开 simplex

`guidance_targets((.9,.1),(.4,.6),2)` 返回约 **(-0.1,1.1)**，`valid_probability_target=False`。两端都合法，外推却不保证合法。

函数不裁剪、不重规范化，也不实现 logits guidance。若实验改了修正方法，它是另一条推理／目标合同，需要独立检验。

## E. 指标与资源各自记账

二符号 Markov reference 假设重复概率 0.9、变化概率 0.1，排除第一个 token 的评分：

| 样本 | Conditional gPPL | Unigram entropy |
| --- | ---: | ---: |
| `AAAAAA` | 约 1.111 | 0 |
| `ABABAB` | 约 10 | ln 2 |

不是 GPT-2、真实英语评分或分布评测实现，只说明可预测性与样本 entropy 不相同。相似 entropy 也不证明句子组合分布相同。

另外，`evaluation_count(8,2,1)` 为 **17** 次评估。`dense_state_budget(128,50000,64)` 给出 one-hot ambient state **25,600,000 bytes**、embedding **32,768 bytes**；bit 编码有 **16** 个坐标，以 float32 表示为 **8,192 bytes**。

这些只是声明的稠密状态，不包含参数、logits、KV、梯度、optimizer、readout 或 decoder；没有实际分配张量。小词表的编码维数也要重新算，不能把 16 当固定常量。

## 五道自测

1. 边缘概率准就能独立抽整段吗？**不保证，A 展示依赖损失。**
2. Heun 一步与 Euler 一步是同预算吗？**本例不是，前者 NFE=2。**
3. Semigroup error=0 就学到了目标吗？**不是，恒等 map 是反例。**
4. Guided 概率和为一就合法吗？**还需所有坐标非负且不超过一。**
5. 状态 bytes 小或 gPPL 小，足以宣称真实模型更好更快吗？**不够，还要模型、解码、质量与总资源合同。**

所有输出可序列化为有限 JSON。代码测试不替代真实 sampler、loss／gradient 一致性、扩展实验或安全验证。
