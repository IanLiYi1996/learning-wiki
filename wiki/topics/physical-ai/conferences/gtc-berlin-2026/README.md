---
permalink: /wiki/topics/physical-ai/conferences/gtc-berlin-2026/
physical_ai_reader: gtc
---
# GTC Berlin 2026 Physical AI 内容整理

资料整理日期：2026-10-26。会议时间为 2026-10-20–22，地点为德国柏林。当前版本为 1.2。

2026-10-29：本页可直接阅读完整图文报告；PDF、Word 与仓库中的独立 HTML 保留原导出版。见[网页修订记录](../../archive-notes.md)。

## 阅读与编辑

- [PDF 阅读版](GTC_Berlin_2026_Physical_AI_深度调研报告.pdf)：含可点击目录、40 个书签及来源链接；最终页数见 `qa/layout-check.json`。
- [Word 编辑版](GTC_Berlin_2026_Physical_AI_深度调研报告.docx)：含标题层级、表格、动态目录与页码字段；已通过 OpenXML 校验。目录与页码由 Word 等兼容软件打开后计算；若未自动更新，可全选后按 F9。Word 的页数不必与 PDF 相同。
- [Markdown 正文](GTC_Berlin_2026_Physical_AI_深度调研报告.md)：保留正文与数字引用。
- [独立正文页面](GTC_Berlin_2026_Physical_AI_深度调研报告.html)：当前显示图文网页；原独立 HTML 导出及 `print.css` 保留在仓库。

正文约 6,900 汉字，包括内容概览、8 章和 3 个附录。48 条来源记录对应 46 个不同的来源 URL。内容按 Cosmos、机器人、工厂和自动驾驶归类，另有技术栈、设备与性能数据、发布信息和 10 个会议场次。

## 版本记录

1.1：改为事实说明文，删除战略解读、采购判断、平台化机会、90 天试点和自行扩展的风险建议。术语在首次出现时解释，版本差异、开放时间和供货计划集中放在第七章。会议场次不再标注推荐优先级。

1.2：扩展第六章 Physical AI 技术栈，增加分层职责、输入输出、训练／编排／推理分工、ROS 2 与硬件控制，以及机器人、自动驾驶和工厂三类应用的连接方式。新增 12 项技术栈资料，按查阅日记录，不统称为 GTC 新发布。

原有会期案例、版本记录和性能数字继续保留。各版 Markdown、Word、PDF、HTML 及排版脚本在原工作目录的 `archive/v1.0/`、`archive/v1.1/` 备份；学习仓库只归档当前 1.2 成品。

文件名保留不变，方便继续使用已有链接；文内标题已改为“Physical AI 内容整理”。

## 研究底稿与质量检查

`notes/` 保留此前的机器人、工业、汽车核查笔记及论文元数据，新增 `physical-ai-stack.md` 记录任务编排、推理、通信与执行组件的官方说明。

学习仓库保留本版 `qa/layout-check.json`、Word 引用及域检查、来源访问检查等 JSON 摘要；原工作目录中的缩略图、预览与文本转储不入库。Word 浏览器预览与实际 Word 的分页可能不同；归档没有重新执行来源访问或视觉检查。

## 重建文件

需要 Pandoc、officecli，以及 Python 的 markdown、weasyprint、pymupdf。中文字体使用 Noto Sans CJK SC。

```bash
uv run --with markdown --with weasyprint --with pymupdf python build_report.py
pandoc GTC_Berlin_2026_Physical_AI_深度调研报告.md \
  --from markdown --to docx --standalone \
  --lua-filter docx_filter.lua --metadata lang=zh-CN \
  --output GTC_Berlin_2026_Physical_AI_深度调研报告.docx
python style_docx.py
```

重建 Word 前应先关闭当前 officecli resident，避免旧的内存版本覆盖生成物。排版程序仅生成本目录交付物，不安装或部署 NVIDIA 软件，不修改外部系统。
