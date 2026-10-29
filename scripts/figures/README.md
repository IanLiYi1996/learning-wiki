# 学习笔记配图

四个 JSON 是经过正文内容梳理的图解清单，记录内容、图型与精确插入标题。
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

## Physical AI 原件与图文版

2026-10-29 的修订只给 Markdown 正文与分章补图，不改变原文研究日期、引用、产品状态或结论。
原 PDF、Word 与独立 HTML 导出版保留原字节，不冒称已经重建。
`archive-manifest.json` 保留图文 Markdown 的当前校验和及归档原件校验和；配图资源在新增修订清单中校验。
若以后重建导出版，需按分册说明运行并重新核验排版、引用、图片和归档清单。
