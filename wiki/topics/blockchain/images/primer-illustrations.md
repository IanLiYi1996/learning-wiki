# 图解扫盲配图说明

- 配套正文：[区块链图解扫盲](../beginner-guide.md)。
- 编写日：2026-10-29（北京时间）。
- 内容：30 张原创教学图，SVG 为可编辑源文件，2 倍分辨率 PNG 用于 Markdown、GitHub 与离线阅读；其中行业分工图也用于行业篇。
- 来源：根据正文问题、算例和一手规范自行组织，不转载互联网图片，不使用原始 PPT 截图，没有上传正文到图像生成 API。

## 为什么这样画

图主要帮助看清三类关系：钱、控制材料和记录分开；某个过程还有哪些步骤；数字变化为什么产生不同结果。

UTXO 的费用是差额，不画成一个普通收款输出。挖矿的四位数是缩小范围的教学数据，不伪装成真实哈希。订单簿条形组织报价，不用宽度冒充实时深度。金库、基金和代币数量不会仅凭图标就合并成同一种权利。

图片中的金额、报价、收益和风险阈值都回到正文假设。图示不是实测拓扑、上线证据、性能报告或收益承诺。

每张图都有标题、说明和可放大的本地资源。网页使用 SVG 渐进增强，无法使用时回退 PNG。图位由内容清单明确指定，不按任意标题机械生成装饰图。

## 重建这一组，不改其他专题

仓库内的清单是 `scripts/figures/blockchain-primer.json`，生成器是 `scripts/render_figures.py`。它们入 Git，但不作为网页构建中的下载资源。

Python 3.9+，Cairo、中文字体 `Noto Sans CJK SC`，以及 `cairosvg`/`Pillow`：

```bash
python scripts/render_figures.py --id-prefix primer- --embed
python scripts/render_figures.py --check
python wiki/topics/blockchain/examples/primer_math.py
```

第一条只生成及更新 `primer-` 图组和它的正文插图，不改写其他专题资产及 Physical AI 清单。第二条检查整个仓库已有的图位及资源。

SVG 采用本地字体回退、中文标签和无障碍 title/desc，无远程图片、外部字体、脚本或热链。场景图检查元素边界及箭头穿框；渲染后仍需看图，代码检查不能代替视觉和机制复核。

## 以前的资料

原始附件和两张 PPT 原图继续放在本地忽略目录，不上传。首版入门笔记保留在 [机制速查](../beginner-reference.md)，不是本次图解正文的旧版图片来源。
