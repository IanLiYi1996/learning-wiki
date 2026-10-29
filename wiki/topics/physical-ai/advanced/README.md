---
permalink: /wiki/topics/physical-ai/advanced/
physical_ai_reader: advanced
---
# Physical AI：底层原理与实现细节

2026-10-27，深化版 2.0。前版是知识地图，本册补到数学模型、算法过程和实现接口。前版文件保持不变。

2026-10-29：本页可直接阅读完整图文正文与公式；PDF、Word 与仓库中的独立 HTML 保留原导出版。见[网页修订记录](../archive-notes.md)。

最终 PDF 为 55 页，正文及附录约 3.3 万汉字，109 组独立显示公式，109 个一手资料入口。21 篇论文元数据另存，未知字段没有补估计值。

## 正文

- [PDF](Physical_AI_底层原理与实现细节.pdf)
- [Word](Physical_AI_底层原理与实现细节.docx)
- [Markdown](Physical_AI_底层原理与实现细节.md)
- [HTML](Physical_AI_底层原理与实现细节.html)

14 章按运行系统的依赖关系展开。每章给出变量与尺寸、公式与假设、算法过程、字段或伪代码、数值问题和失败条件。

具体内容包括 SE(3)、FK／IK、雅可比和奇异值；惯性矩阵、执行器／传动与接触；相机模型、时钟、EKF、SLAM 因子图；路径搜索、轨迹优化与控制；QKV、动作编码、行为克隆、chunk、DDPM／DDIM、Flow Matching；Bellman、GAE、PPO、SAC；RSSM、KL balancing 与想象训练；因果数据对齐、物理约束求解、GPU 异步运行与量化；统计区间和逐层误差诊断。

研究以原论文、作者教材和官方代码为依据。research／academic-search 用于核验；humanizer-zh 用于把公式旁的解释写成直接、自然的中文，不加入产品排名或战略判断。

## 阅读方式

先读 01 章的状态与接口定义，再按 02—05 学几何、动力学、估计、规划与控制。06—09 把学习模型接到同一套符号上；10—13 追到数据、仿真、部署与评测。14 章把若干公式变成可以复现的计算。

查公式时一起看假设和单位。局部线性化不是全局保证，代码返回成功不等于任务完成。各章的教学接口不冒充原模型的精确配置；涉及论文或软件时注明版本。

## 离线数值练习

```bash
python examples/numerical_workbook.py --output qa/numerical-results.json
```

只用 Python 标准库，11 组检查覆盖 FK／IK、雅可比差分、阻尼、标量反馈、Kalman、MSE 多峰、噪声采样、线性 flow、Wilson 区间和因果对齐。没有训练模型、操作硬件或运行完整机器人仿真，不能把教学参数用于实机。

## 构建与数学排版

依赖：Python、uv、Pandoc、officecli、Node.js，以及 Noto Sans CJK SC 字体。

```bash
npm ci --ignore-scripts --no-audit --no-fund
python build.py --format assemble
uv run --with markdown --with weasyprint --with pymupdf python build.py --format pdf
python build.py --format docx
```

MathJax 固定为 3.2.2，仅用于构建，不作为“当前最新版本”的声明。PDF 将 TeX 转为自带字形的矢量 SVG，避免用普通正文显示 LaTeX；Word 通过 Pandoc 保留原生 OMML。Word 目录、PAGE／NUMPAGES 由兼容的域引擎更新，固定分页以 PDF 为准。

构建将旧式 `\rm` 写法标准化为 `\mathrm`。当前转换器的矩阵列属性顺序、普通文本与数学字体属性冲突按 OpenXML 结构修正，不改变数学内容；修正后重新验证。975 处数学表达（含行内变量）在源文件、PDF 和 Word 中数量一致，无公式转换回退。

`chapters/` 是正文分章源，`frontmatter.md` 和 `appendices.md` 是前言与附录源。`build.py` 合并正文、按首次引用生成 S 编号，避免把代码 `a[0]` 误解为来源编号。章节末研究用来源清单在合稿时删除，统一来源表在附录 C。

`sources.json` 保存来源入口。`papers.json` 合并前版及本轮核验论文，未知字段保持 null。`qa/` 保存引用对应、公式渲染、OpenXML、数值与视觉检查；Word 的 Linux 预览不等于实际 Word 分页。

PDF 已查看全页缩略图并抽查矩阵、积分、控制、扩散和 JSON 页面。Word 已做全内容结构与公式检查，以及默认预览和第 8 页抽样；不宣称默认预览完整展示了所有 Word 页面，也不把 Linux 预览的页数当作实际 Word 页数。

## 资料边界

本册覆盖上述算法的基础计算与工程接口，不声称逐字复刻某一仓库或穷尽机器人、控制、视觉和学习的全部学科。没有产品采购、发布会战略结论、实机调参或安全认证方案。下一步复现需固定目标任务、软件版本、数据与验证环境。
