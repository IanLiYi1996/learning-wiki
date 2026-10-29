# 来源与版本记录

核验日期：2026-10-29。正文在相应章节逐节标明来源，不把这份目录当成所有陈述的统一免责脚注。

## 版本基线

| 对象 | 本次核验结果 | 证据与限制 |
| --- | --- | --- |
| Three.js npm `latest` | `0.186.1` | [发布元数据](https://registry.npmjs.org/three/0.186.1)；不是无限期的最新版本声明 |
| Three.js 对应 `gitHead` | `9b4a2ac29c63ccb43fd51c5661f2f873ac2c39b8` | 源码链接尽量固定到此提交 |
| WebGPU 发布文档 | 2026-09-15 CRD | [固定版本](https://www.w3.org/TR/2026/CRD-webgpu-20260915/) |
| WGSL 发布文档 | 2026-10-26 CRD | [固定版本](https://www.w3.org/TR/2026/CRD-WGSL-20261026/) |
| WebGL 主线 | WebGL 2 / GLSL ES 3.00 | 功能、扩展和设备 limits 分别检测 |
| 数值练习运行时 | Node.js `v22.22.0` | 只使用标准库，不依赖 Three.js 或 GPU |

CRD 指 Candidate Recommendation Draft。标准文档日期不等于浏览器完整支持日期，npm 版本也不等于 Three.js 所有新特性均已脱离实验阶段。

## 来源层级

1. 规范：Khronos WebGL / OpenGL ES / GLSL ES；W3C WebGPU / WGSL。
2. 框架官方源码与指南：Three.js、Babylon.js、PixiJS、React Three Fiber、regl 等。
3. 开发者技术说明：MDN API 文档、Google Filament PBR 文档。
4. 教学组织：本专题中的学习路径、比较框架、数学例子和实验设计。

第四层是整理和推导，不标成某公司的官方架构图或某个设备的实测结论。

## 常用入口

- [Khronos WebGL 官方仓库](https://github.com/KhronosGroup/WebGL)
- [Khronos OpenGL ES 注册库](https://github.com/KhronosGroup/OpenGL-Registry)
- [MDN WebGL API](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API)
- [MDN WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)
- [Three.js 固定源码](https://github.com/mrdoob/three.js/tree/9b4a2ac29c63ccb43fd51c5661f2f873ac2c39b8)
- [glTF 2.0 材质与资产规范原稿](https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc)
- [Google Filament PBR](https://google.github.io/filament/main/filament.html)
- [Spector.js](https://spector.babylonjs.com/)

部分 Khronos registry 页面在当前抓取环境返回访问挑战，改用规范维护者的官方 GitHub 原稿；不把访问失败标成已读。

Three.js 的旧 `manual/en/*.html` 及部分旧文档路径在本次核验时返回 404 / Redirecting。正文优先引用固定源码中的 `manual/pages/`、`docs/pages/` 与实际实现文件，不以猜测 URL 代替核验。

## 本次验证范围

- 在线阅读一手文档与源码，核对版本基线。
- 检查 Markdown 本地文件链接、来源标记与章节衔接。
- 运行纯数学、色彩和理论纹理大小的 Node.js 测试。
- 没有搭建完整浏览器渲染应用，没有实际 GPU 计时或显存测量。
- 文档中的 GLSL/WGSL/Three.js 片段需在各自环境中验证；不冒称已经通过全部目标设备编译与画面验证。

本次实际执行：20 项 Node.js 数值测试全部通过，数学示例正常输出；10 份专题 Markdown 的本地文件链接未发现缺失。检查不覆盖外部链接未来可达性、标题锚点或完整 CommonMark 语法。
