# 学习笔记配图

各 JSON 是经过正文内容梳理的图解清单，记录内容、图型与精确插入标题。
不按标题自动拼装泛用封面，不新增来源事实，也不将图示称为实际部署证据。

## 覆盖原则

- 多阶段流程、闭环、状态／失败边界、系统职责、概念对比需要图。
- 长笔记按机制拆图；分章与汇总稿复用图解，不只在顶部放装饰封面。
- 目录、来源／核验记录、术语表、空模板、归档说明和短清单不强制配图。
- 每张图提供中文标签、说明、SVG 无障碍标题和 PNG 后备。所有资源在仓库本地，无热链、外部字体或生成 API。
- 图解遵循 document-illustrator 的内容归纳与 fireworks-tech-graph 的矢量布局／校验方式；按技术内容选择流程、职责对照、分层、几何和数值图。

## 重建

Python 3.9+，系统 Cairo、中文字体 `Noto Sans CJK SC`，Python 包 `cairosvg`：

```bash
python scripts/render_figures.py --embed
python scripts/render_figures.py --check
bundle exec ruby scripts/build_physical_reader.rb
bundle exec jekyll build
PHYSICAL_READER_SITE=_site python -m unittest discover -s tests -p 'test_*.py'
```

第一条命令重新生成 SVG／2× PNG，并按清单进行幂等机械插入。
脚本在写文件前检查所有插入标题是否唯一。`--check` 只读，不生成或修改文件。
SVG 与 PNG 位于各专题的 `images/`；Markdown 用相对 PNG 路径便于 GitHub、导出与离线阅读。
网站渐进增强选择 SVG，失败时回退 PNG；点击可放大、切换原尺寸或下载 PNG。
补图后重建 Physical AI 阅读片段，确保页内阅读器与 Markdown 的图片和正文一致。

区块链零基础图组在 `blockchain-primer.json`，覆盖白话读本的控制/记录、UTXO、PoW、订单簿、AMM、清算、跨链等问题。新增 `scene` 类型显式指定元素与箭头，检查边界及穿框；用 `--id-prefix primer-` 只重建该组，不改其他专题及 Physical AI 清单。详细假设见 [配图说明](../../wiki/topics/blockchain/images/primer-illustrations.md)。

支付主干图组在 `payments.json`（14 图）；领域补全分在 `payments-foundations.json`、`payments-operations.json`、`payments-engineering-regions.json`、`payments-digital-money.json`（18 图）。用 `--id-prefix payment-` 重建支付专题全部 32 图，或用 `--id-prefix payment-ext-` 只重建 13–22 课的补全图。内容覆盖产品、终端、订阅、商户运营、资金、密码与账本、中国体系、现金与数字货币；费用与架构均为教学示例，不代表公司生产数据或部署。发布范围只含公开一手资料的扩展读本，不含内部会议附件或录屏。

深度学习图组在 `deep-learning.json`，当前围绕权重空间编程，包括计算契约、方法对照、手写控制器、QK／OV、实验权限、修补与能力、投影、置换平均和验证回滚。用 `--id-prefix wsp-` 单独重建；图中数字例为可测试的原创教学，不冒充原文真实模型评测。

扩散与推理工程图组在 `diffusion.json`（13 图），覆盖后训练地图、DPO 四项误差、奖励微调路线、SDE 密度、评估证据、奖励标准化、自动研究、正确性验收、CUDA 层次、Roofline、视频延迟、token 与计算成本。用 `--id-prefix dif-` 单独重建，资源仍位于 `deep-learning/images/`，分章用 `../images/` 引用。小数组和假想硬件是原创教学例，不冒称性能复现。

## Physical AI 原件与图文版

2026-10-29 的修订只给 Markdown 正文与分章补图，不改变原文研究日期、引用、产品状态或结论。
原 PDF、Word 与独立 HTML 导出版保留原字节，不冒称已经重建。
`archive-manifest.json` 保留图文 Markdown 的当前校验和及归档原件校验和；配图资源在新增修订清单中校验。
若以后重建导出版，需按分册说明运行并重新核验排版、引用、图片和归档清单。
