# Physical AI 归档记录

归档日期：2026-10-28。目标为私有学习仓库的 `wiki/topics/physical-ai/`，范围仅限本次 Physical AI 资料。

## 日期口径

- 行业篇、原理篇与概念地图：2026-10-27 的资料及检查记录。
- GTC 报告：2026-10-26，版本 1.2；按会议资料保存。
- 本次新增专题入口、阶段对照、学习路线与笔记模板，不将归档日期当成产品状态重新核验日期。

## 保留范围

- 四份正文的 Markdown、PDF、Word 和 HTML 成品。
- 行业篇 12 章、原理篇 14 章的分章稿、前言与附录。
- 产品 CSV／JSON、论文元数据、一手来源入口与研究底稿。
- 两个不连接硬件的标准库教学程序及评测模板。
- 原有构建脚本、样式、Lua 过滤器及 MathJax 依赖锁文件。
- 原检查的 JSON 结果与 Markdown 摘要。

不归档 `node_modules/`、Python 缓存、重复截图、预览和文本转储，也不复制 GTC 的历史导出版。原工作目录仍保留全部原件和旧版，没有移动或删除。

原概念地图的 README 改名为 [concept-map.md](concept-map.md)，主题入口由新的 [README](README.md) 提供。GTC 资料保留文件名，放入 `conferences/gtc-berlin-2026/`。研究记录中的技能路径改为不依赖主机的标识；这不表示技能文件本身被打包进仓库。

成品按字节保留，包括原有 Markdown 数学空格、换行和 CSV 的 CRLF。专题 `.gitattributes` 禁止 Git 对这些归档成品自动转换换行，以免跨平台检出后与 SHA-256 清单不一致。

## 校验与复现

从本专题目录执行：

```bash
python scripts/check_archive.py
python -m unittest discover -s scripts/tests -v
python examples/feedback_demo.py
python advanced/examples/numerical_workbook.py
```

[归档清单](archive-manifest.json) 保存四组既有成品的 SHA-256，以及 116 个配套文件的必备路径清单。检查程序核对成品字节、配套文件是否缺失、JSON 解析、Markdown 本地链接、产品 CSV／JSON 记录及数量，并检查文本资料里的本机绝对路径。依赖包和 Python 缓存不参与校验，也不入库。

数值练习和反馈练习可以重跑；历史 PDF／Word 排版及来源访问记录不冒称归档时重新完成。重建成品需要各册 README 列出的工具、字体及依赖；构建可能改写成品与清单对应的哈希，届时应重新生成归档清单并记录改动。

归档检查器支持本资料使用的 Markdown 链接形式，不是完整 CommonMark 解析器；不检查标题锚点、外部页面可达性或 PDF／Word 内部排版。

## 本次实际检查

- 16 个既有正文成品的 SHA-256 与清单一致，导出版未重新生成。
- 行业篇 12 章、原理篇 14 章、21 篇原理篇论文元数据完整。
- 58 条产品的 CSV／JSON 逐字段一致。
- 41 个 JSON 可解析，132 处专题 Markdown 本地文件链接有效。
- 116 个必备配套文件存在；未被文档链接引用的研究元数据和分册前言也纳入清单。
- 归档检查器的 19 项单元／集成测试通过，包含文件变更、缺失文件、非 UTF-8 系统默认编码、链接写法、数据不一致与 CLI 失败诊断。
- 反馈教学程序及数值工作簿的 11 组断言通过。
- 入库清单没有依赖包、Python 缓存、重复 QA 媒体或高置信度凭据模式。

本次没有产品安装、下载模型、完整仿真、模型训练、实机测试或客户系统接入。
