# 连续语言模型术语速查

整理日期：2026-11-11。[专题导读](README.md) · [来源与版本](sources.md)。

| 术语 | 本读本中的含义 | 易混淆的对象 |
| --- | --- | --- |
| AR | 依序按前缀生成后续 token | 模型内部也可使用连续向量 |
| Continuous-time | 时间参数连续 | 状态未必连续 |
| Continuous-state | 在向量等连续空间演化 | 最终文字仍可能离散 |
| Marginal | 单个位置的概率分布 | 所有位置的联合分布 |
| Factorization error | 采样时乘积近似丢掉依赖的误差 | 不只是预测器的概率误差 |
| One-hot | 一个 token 对应词表的一个坐标顶点 | 噪声状态不必在 simplex |
| Simplex | 非负、和为一的概率向量空间 | 无约束 logits／Gaussian state |
| Contextual embedding | 含上下文信息的 token 表示 | 单纯词表查表 |
| Compressed latent | 用较少状态承载文字信息 | 不保证 decoder 并行 |
| Denoiser | 从当前状态预测干净目标等量 | 输出目标和 loss 对象可不同 |
| Velocity | 连续状态的变化率 | 不是系统墙钟速度 |
| Score | 指定状态分布的 log-density 梯度 | 不是任务评分器的同义词 |
| Flow matching | 沿条件概率路径学习速度场的接口 | 不规定唯一表示／目标／路径 |
| ODE／SDE | 确定性／随机连续动力学 | 任意加噪不保证边缘分布保持 |
| Noise schedule | 噪声等级与时间的对应等配置 | 训练采样和推理网格仍需区分 |
| Self-conditioning | 反馈先前预测或特征 | 默认不是跨 session Agent memory |
| Guidance | 修改预测／轨迹来加强条件或目标 | 不保证正确性或安全 |
| NFE | 网络函数评估次数，依统计合同 | 不等于 sampler 的表面步数 |
| Flow map | 两个时间之间的有限变换 | 一个放大的 Euler 步不自动等价 |
| Semigroup | 短跳合成等于长跳 | 单独不确定目标 flow |
| Diagonal／tangent | 同时刻边界与瞬时动力学约束 | 不能用 identity 条件替代全部监督 |
| Pushforward generator | 从噪声直接映射到样本 | 不必有任意 s→t 的 map |
| Commitment | 将选中位置固定为上下文 | 不代表永远正确或缓存必然有效 |
| gPPL | 参考 LM 对生成样本的可预测性评分 | 不是生成器精确 likelihood／事实正确率 |
| ELBO／likelihood bound | 一种概率目标或界 | 不是同一张 inference speed 表 |
| Generative frontier | 随配置变化的质量／多样性权衡 | 一个最优点不能代表全部条件 |

记号约定：生成时间 0→1 表示噪声→数据；L 为文字位置数，V 为词表，d 为表示维度。每篇原论文的时间、状态、概率与损失仍需各自核对。
