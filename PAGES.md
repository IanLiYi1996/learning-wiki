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
