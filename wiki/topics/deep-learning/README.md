# 深度学习专题解读：从论文主张到可检验的机制

研究日期：2026-11-03。这里按“问题 → 数学直觉 → 实验证据 → 实现 → 边界”解读具体研究，不把单篇文章包装成整个深度学习领域的定论。

本专题的第一篇是 **Weight-Space Programming／权重空间编程**。原文发表于 2026-11-02，由研究者报告一组让通用大模型读取、修改或构造其他网络权重的实验。我们保留它的兴奋点，也把实验权限、失败案例和未经验证的展望分开。[原文与核验记录](weight-space-programming-sources.md#blog)

## 从这里开始

- [图文解读：权重空间编程，10 节](weight-space-programming.md)：9 张机制图，先看懂为什么“权重也可以是一种程序”。
- [本地实验与 12 道自测](weight-space-programming-lab.md)：只用 Python 标准库，手写控制器、验证神经元置换、观察平均失败与局部投影。
- [术语速查](glossary.md)：权重、激活、梯度、Logit、残差流、低秩与因果干预。
- [一手来源与实验权限](weight-space-programming-sources.md)：原文、日志、模型发布与相关工作；哪些已读，哪些尚未独立复现。

## 10 节目录

| 节 | 先回答一个问题 |
| --- | --- |
| [01 三种对象](weight-space-programming.md#wsp-01) | 权重、架构、输入含义，为什么缺一不可？ |
| [02 新在哪里](weight-space-programming.md#wsp-02) | 与训练、Hypernetwork、编译器和模型编辑如何区别？ |
| [03 手写一个网络](weight-space-programming.md#wsp-03) | 15 个参数能怎样实现一个小控制程序？ |
| [04 怎样读权重](weight-space-programming.md#wsp-04) | QK 与 OV 矩阵分别解释“看哪里”和“搬什么”？ |
| [05 八个实验](weight-space-programming.md#wsp-05) | 哪些只读静态权重，哪些使用运行反馈？ |
| [06 Qwen 案例](weight-space-programming.md#wsp-06) | 修复循环和获得新的数学能力，是同一件事吗？ |
| [07 权重几何](weight-space-programming.md#wsp-07) | 为什么只改一点也可能影响很大，平均还会出错？ |
| [08 证据强弱](weight-space-programming.md#wsp-08) | 一段合理解释如何升级成因果证据？ |
| [09 工程实现](weight-space-programming.md#wsp-09) | 如何把权限、评测、成本和回滚放进 Harness？ |
| [10 学习与判断](weight-space-programming.md#wsp-10) | 哪些结论可以带走，哪些暂时不能？ |

## 建议阅读路线

**30 分钟直觉路线**：01 → 03 → 05 → 06 → 10。把“无梯度”和“无反馈”先分开，再理解局部修复。

**90 分钟机制路线**：顺序阅读，拿纸验算 03、04、07 的公式，最后完成自测。

**半天实践路线**：跑本地实验与测试，读作者发布的实验协议和评测代码，再写一页复现计划。半天不包括下载或重评真实语言模型。

推荐先具备矩阵乘法、ReLU、前向计算的基本概念。Transformer 不熟悉也可以读，04 节只引入本题所需的最小记号；它不是完整 Transformer 课程。

## 阅读约定与边界

- **作者报告**：归属于原文和作者发布的材料，不自动成为独立验证。
- **背景机制**：来自论文、研究者说明和框架文档，不宣称本篇发明了全部机制。
- **原创教学推导**：15 参数控制器、置换反例和投影数字由本 Wiki 构造，并有本地测试。
- **研究判断**：可能的解释和复现建议明确标为判断，不冒充作者的实验结果。

本次没有运行原文的模型编辑实验、下载真实模型权重或重跑 MATH-500；教学实验不调用模型服务。原文提到的自我改进、跨架构移植等展望，不能按已实现的工程能力采购或部署。

配图按机制拆解，使用仓库本地 SVG 与 2× PNG；网页可放大，Markdown 可直接阅读。重建此组：

```bash
python scripts/render_figures.py --embed --id-prefix wsp-
python scripts/render_figures.py --check --id-prefix wsp-
```

相关阅读：[Physical AI 的学习与控制](../physical-ai/README.md)。手写静态策略、通过强化学习训练策略，以及在线规划，是不同机制。
