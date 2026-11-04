# PixelBench：一手来源、代码快照与核验边界

研究日期：2026-11-04。仅使用公开论文、项目说明与公开实现。本页为阅读核验台账，不包含用户内部会议附件、客户数据或模型服务凭据。

## 1. 原始研究

| 材料 | 本次核验范围 | 说明 |
| --- | --- | --- |
| [论文摘要与版本](https://arxiv.org/abs/2611.02540) | 标题、作者、v1 提交日期 | 2026-11-02，技术报告 |
| [论文 v1 HTML](https://arxiv.org/html/2611.02540v1) | 三任务、指标、结果、分辨率、PRT、附录 | 不把模板或排版字样当作会议录用 |
| [作者项目页](https://haoquanzhang.github.io/pixelbench/) | 作者解读、论文／代码／模型入口 | 阅读介绍，不复制整页图文 |
| [公开 GitHub 仓库](https://github.com/HaoquanZhang/PixelBench) | 接口、评分、聚合、数据混合与 trainer | 实现能帮助对照论文，存在实现不等于完整独立复现 |
| [作者模型集合](https://huggingface.co/collections/haoquan03/pixel-reconstruction-tuning) | 公开发布入口 | 没有下载权重或验证其运行性能 |

## 2. 固定实现版本

下列链接固定到本次已检查的公共提交。修订号只在对应 GitHub URL 中记录，避免把可变 `main` 当成永久证据。

- [格式验证、RGB 渲染与单色检测](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/pixelbench/format.py)：严格尺寸、不自动修复、颜色预算、布尔索引拒绝。
- [主指标与失败分母](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/pixelbench/evaluate.py)：缺失／非法计零，valid-only MRR。
- [调用与重试流程](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/pixelbench/run.py)：调用失败、截断与完成输出分开。
- [I2P min–max 聚合](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/pixelbench/table.py)：比较集合依赖，常量列报错。
- [八色算法基线](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/pixelbench/baselines.py)：代表性实现，不是全领域穷尽比较。
- [训练数据与预算说明](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/training/README.md)：两套环境、起点、字母网格、GPU 与步数。
- [Pixel 数据构造](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/training/pixels.py)：选择、分辨率、精确评测图排除。
- [教师轨迹](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/training/trajectories.py)：caption／palette 解释与确定性 grid 分工。
- [混合与对照](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/training/prepare.py)：additive 与 fixed 数据账本。
- [Qwen trainer](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/training/qwen.py) 与 [Molmo2 adapter](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/training/molmo2.py)：trainable modules、mask、优化与官方训练入口。
- [下游评测合同](https://github.com/HaoquanZhang/PixelBench/blob/c095bae7434c98e1529dea0754c5ebf61e10534f/EVALUATION.md)：官方 unit、benchmark 权重及组内成功规则。

## 3. 本 Wiki 做了什么

读取公开材料、对照上述实现；将能力测量与辅助训练拆成章节；绘制原创流程／对照图；编写并测试标准库教学代码。4×4 方块、0.375／0.75 分母例、50→25 聚合例、不同平均权重例均为原创构造。

本地代码是最小机制演示，不是上游兼容包，不处理任意模型返回文本，不实现 SigLIP／DINO／PIA／VLM judge，也不读取上游保存的成绩假装是新模型实验。

## 4. 没有执行或证明什么

没有下载论文模型权重、获取完整训练语料、调用闭源模型服务、启动 GPU 训练、运行上游 benchmark、验证第三方托管端点或独立证明成绩。没有对数据近重复进行全库审计；上游排除精确图像匹配也不能自动证明没有语义污染。

没有核实会议录用，不能因项目网页出现 ICLR 模板字段宣称已接收。版本之后可能变化，本文不称“最新完整结论”。

所有训练数字应标为作者报告；所有小数组应标为教学例；所有机制解释应说明是观测还是假说；所有复现计划应说明尚未执行。发布到 Wiki 与独立重跑论文是两个不同状态。

返回[专题导读](README.md)；继续读[证据与局限](evidence-and-limitations.md)、[离线实验](lab.md)。
