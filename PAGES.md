# GitHub Pages

- 网站：https://ianliyi1996.github.io/learning-wiki/
- 发布源：`main` 分支根目录。
- 构建：GitHub Pages 原生 Jekyll，使用 Primer 主题。
- Markdown：原文保持不变，构建时生成 HTML 并转换本地 Markdown 链接。
- 首页：根目录及专题目录的 README 自动生成索引页。
- 公式：MathJax；PDF、Word 和其他资料保留原有下载路径。

## 本地预览

需要 Ruby、Bundler，以及用于安装原生依赖的 Ruby 开发头文件和编译工具。

```bash
bundle install
bundle exec jekyll serve
```

默认访问 `http://127.0.0.1:4000/learning-wiki/`。
本地 Jekyll 会读取工作目录中的文件；需要核对线上发布范围时，应在干净的 Git 检出目录构建。
线上只发布已提交到 `main` 的内容。

## 图文阅读

专题 Markdown 引用本地 PNG，网站渐进增强为 SVG 并提供点击放大／原尺寸阅读。
图片不依赖外站热链；禁用 JavaScript 时仍能阅读 PNG。
Physical AI 的四份旧独立 HTML 从网站构建中排除，避免覆盖同名 Markdown 页面；原件仍保留在仓库，PDF／Word 下载不变。

## Physical AI 完整阅读

专题总入口在页内提供知识全景、行业篇、原理篇和 GTC 四份完整正文，切换读本不重新加载页面。
行业、原理和 GTC 的原目录 URL 也直接显示正文；下载和构建记录放在可展开的资料说明中。
章节 ID 按读本加前缀，图片和站内链接按原文件位置重新定位。公式只排版当前读本，减少初次加载工作。
阅读片段使用现有 Kramdown／Nokogiri 依赖生成，不需要 GitHub Pages 自定义插件；原 Markdown 是唯一内容源。

修改正文或批量补图后，从仓库根目录执行：

```bash
bundle exec ruby scripts/build_physical_reader.rb
bundle exec ruby scripts/build_physical_reader.rb --check
bundle exec ruby tests/physical_reader_test.rb
bundle exec jekyll build
PHYSICAL_READER_SITE=_site python -m unittest discover -s tests -p test_physical_reader.py
```

`--check` 会拒绝陈旧片段。检查涵盖四份全文、末章与附录、站内资源、唯一锚点和归档来源校验和。
