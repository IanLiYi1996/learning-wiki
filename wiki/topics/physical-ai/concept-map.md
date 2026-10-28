# Physical AI：概念地图与原版构建说明

资料整理日期：2026-10-27。保留原版概念地图及其构建说明；学习仓库归档日期：2026-10-28。

专题入口：[Physical AI](README.md)。对读入口：[按阶段对读行业篇与原理篇](Physical_AI_阅读入口.md)。

## 业界产品与端到端方案

新增 [行业篇](industry/README.md)：逐阶段介绍现成产品、获取与部署、输入输出、接口和落地证据，并给出产品组合与客户案例。它与下方原理教材一起使用，不把软件可下载、模型演示、生产试点和商业运行混为一谈。可检索清单在行业篇的 `products.csv`／`products.json`。

## 底层原理深化版

用户反馈本版过于概括后，新增 [《底层原理与实现细节》](advanced/README.md)，逐层补齐数学模型、算法步骤、张量与数据字段、执行器／接触、数值问题和运行接口。需要深入掌握时，以该册为主；本版保留作为领域地图，不将原文静默覆盖。

## 阅读文件

- [PDF](Physical_AI_知识全景与学习指南.pdf)：固定分页、可点击目录和来源。
- [Word](Physical_AI_知识全景与学习指南.docx)：便于批注和编辑。
- [Markdown](Physical_AI_知识全景与学习指南.md)：正文源文件。
- [HTML](Physical_AI_知识全景与学习指南.html)：浏览器阅读版。
- [论文元数据](papers.json)：10 篇论文，保留版本、作者与来源说明。

## 内容与使用顺序

十五章覆盖概念、系统信息流、机器人基础、感知／定位、规划／控制、模型、学习算法、世界模型、数据、仿真、技术栈、部署、评测、学习路线和练习。附录包含术语、资料边界和一手来源。

先读第 1—2 章建立地图，再按第 14 章的依赖关系学习。第 15 章有不连接硬件的实验、四个练习、十二道自测及答案。论文按机制选取，不是最新型号清单或排行榜。

写作采用 research、academic-search 的一手资料核验方式；humanizer-zh 用于将技术表述改为自然中文。主体用“拿起杯子”解释各层职责，没有采购推荐、战略价值判断或预设学习时长。

## 本轮实际验证

没有下载机器人数据集、训练模型或操作真实设备。运行了：

- Python 标准库一维反馈教学程序，验证扰动、限幅和最终误差。
- PDF 目录、书签、非空页、数字引用目标检查。
- DOCX OpenXML 结构、数字引用目标、动态页码和占位符检查。
- PDF 与 Word 预览的视觉检查。

检查结果在 `qa/`。PDF 使用 WeasyPrint，Word 使用 Pandoc 和 officecli 排版。Word 预览不代表 Microsoft Word 的精确分页；打开 Word 后应更新目录／域，若软件未自动更新，可选中全部并更新域。正式固定页码请以 PDF 为准。

## 离线教学程序

```bash
python examples/feedback_demo.py --output qa/feedback-demo.json
```

它不联网、不连接硬件；模型无真实单位、惯性、接触或执行器。示例参数不能用于真实机器人。第 15 章解释了结果与边界。

另有 [评测工作表](templates/evaluation_protocol.md)，用于预先写明任务、成功判据、输入动作接口、尝试次数和干预条件。

## 重建

需要 Python、uv、Pandoc、officecli，以及 Noto Sans CJK SC 字体。PDF 的 Python 包为 markdown、weasyprint、pymupdf。

```bash
uv run --with markdown --with weasyprint --with pymupdf python build.py --format pdf
python build.py --format docx
```

`build.py` 会合并 notes 中的论文表，按 arXiv ID 去重，保留原始版本信息，生成 `papers.json`。未知字段保持 null，不补估计引用数。

正文的连续数字引用用中文顿号分隔，避免 Markdown 将两个相邻方括号误解为一个完整引用链接。PDF 和 Word 导出还会展开成显式 URL，并逐条验证编号与目标的对应。

## 文件职责

- `notes/`：三条研究线及主编补充核验；不是最终正文。
- `examples/`：不连接硬件的学习实验。
- `templates/`：可填写的评测协议。
- `qa/`：生成、结构与视觉检查材料。
- `build.py`、`print.css`、`docx_filter.lua`：排版和验证代码。

已有会议报告归档到 [GTC Berlin 2026](conferences/gtc-berlin-2026/README.md)。本指南覆盖领域基础与学习结构；会议报告覆盖具体发布和产品实例。

学习仓库仅保留检查摘要，不归档原工作目录里的检查截图、重复预览及文本转储。上述视觉检查是原交付记录，不表示归档时重新做了一遍视觉检查。
