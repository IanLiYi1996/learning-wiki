# Shader 与 Web 渲染技术

研究日期：2026-10-29。以 WebGL 2 / GLSL ES 3.00 为底层教学主线，Three.js 版本基线为 `0.186.1`。

目标不是背框架 API，而是能解释：一份几何数据怎样变成屏幕上的图像；为什么同一个 Shader 在不同设置下会变暗、出错或变慢；框架替你管理了哪些工作。

## 先建立分层

```text
应用逻辑 / React / 编辑器 / 资产加载
                    |
场景与框架：Three.js、Babylon.js、PixiJS；R3F 管理 React 场景生命周期
                    |
渲染组织：可见性、排序、材质变体、光照、阴影、后处理
                    |
图形 API：WebGL 2 或 WebGPU
                    |
GPU 程序：GLSL ES 或 WGSL；TSL 是生成这些程序的节点表达层
                    |
浏览器实现 / 驱动 / GPU 硬件
```

这是知识组织模型，不是每个引擎都具有相同实现的承诺。API、Shader 语言、场景框架、React 绑定不是同一层的替代品。

## 章节与阅读顺序

| 顺序 | 章节 | 学完应能解释 |
| --- | --- | --- |
| 01 | [GPU 管线与 Shader](01-gpu-pipeline-and-shaders.md) | 顶点、图元、片元、深度和混合之间的关系 |
| 02 | [坐标、投影、插值与采样](02-coordinates-and-sampling.md) | `P * V * M`、`w`、法线矩阵、mipmap |
| 03 | [WebGL 2 API 与资源模型](03-webgl2-api-and-resource-model.md) | Buffer、VAO、Program、Texture、FBO 怎样配合 |
| 04 | [Three.js 与框架分层](04-threejs-and-frameworks.md) | 一次 `renderer.render()` 如何组织底层绘制 |
| 05 | [光照、PBR、颜色与后处理](05-lighting-color-and-postprocessing.md) | 材质为何响应光线，为什么颜色与 pass 顺序重要 |
| 06 | [性能、调试与资源生命周期](06-performance-and-debugging.md) | 怎样用证据区分 CPU、GPU、带宽与同步瓶颈 |
| 07 | [WebGPU、WGSL 与 TSL](07-webgpu-wgsl-and-tsl.md) | 新 API 改变了什么，旧 GLSL 项目怎样迁移 |

另见[学习路线与实验](learning-roadmap.md)、[来源与版本记录](sources-and-versions.md)。

## 两条实践路线

先用一条路线走通，不要把两套 Shader 系统混搭。

| 路线 | 程序表达 | 适合本专题中的学习目标 |
| --- | --- | --- |
| `WebGLRenderer` | 内置材质、`ShaderMaterial`、`RawShaderMaterial`、GLSL | 理解传统 WebGL 管线、接入旧项目、读 ShaderChunk |
| `WebGPURenderer` | NodeMaterial、TSL；按后端生成 WGSL 或 GLSL | 理解现代绑定模型、节点着色与迁移边界 |

第二条路线可以使用 WebGL 2 后端，不表示第一条路线的任意 GLSL 材质会自动迁移。细节与一手依据见[第 07 章](07-webgpu-wgsl-and-tsl.md)。
核验版本还存在为旧 `WebGLRenderer` 接入有限节点材质的兼容入口；这里按教学主线分成两条路线，不宣称它们绝对互斥。

## 数值验证

在仓库根目录运行，使用 Node.js 标准库，无安装依赖：

```bash
node --test wiki/topics/rendering/examples/pipeline-math.test.mjs
node wiki/topics/rendering/examples/pipeline-math.mjs
```

程序验证数学关系和理论存储估算，不访问 GPU，不证明 GLSL 编译成功、浏览器兼容、实际帧率或显存占用。浏览器实验另按学习路线执行和记录。

## 笔记中的证据边界

- 规范事实：以 Khronos、W3C 的定义为准。
- 框架事实：以核验的版本、官方文档和源码为准。
- 教学推导：公式和数值例子用于解释机制，不代替完整引擎实现。
- 性能判断：先给假设和测量方法，不编造某设备的性能结果。
- 浏览器支持：按目标环境检测 feature、extension 和 limits，不用一句“都支持”概括。

Physical AI 里的数字孪生与可视化可以应用这些知识，但渲染图像、物理仿真和机器人控制属于不同职责，不能彼此替代。
