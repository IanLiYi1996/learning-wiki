# 学习路线与实验

研究日期：2026-10-29。以“能解释、能改动、能验证”为进阶标准，不按刷完多少教程判断。

## 阶段 0：补齐最少的数学

学习向量、点积、叉积、归一化、矩阵乘法、三角函数、颜色通道和采样。先能手算二维旋转与一次矩阵变换，不必先学完整微分几何。

读[第 02 章](02-coordinates-and-sampling.md)，运行：

```bash
node --test wiki/topics/rendering/examples/pipeline-math.test.mjs
node wiki/topics/rendering/examples/pipeline-math.mjs
```

验收：解释位置与方向的 `w` 差别、矩阵次序、WebGL/WebGPU near/far 映射、错误法线变换与错误颜色混合。

## 阶段 1：让一个三角形出现

读[第 01 章](01-gpu-pipeline-and-shaders.md)与[第 03 章](03-webgl2-api-and-resource-model.md)。

实验：用 WebGL 2 建立 context、compile/link 一对 GLSL ES 3.00、上传三个顶点、设置 VAO、调用 draw。

每次只改一个条件：attribute offset、stride、输出颜色、顶点的 `w`、viewport。观察并记录预期与实际。

验收：不依赖框架，能够说清楚每个对象的职责；人为制造编译、布局与裁剪错误后能定位。

## 阶段 2：做出有深度的场景

实验：加入 MVP、索引立方体、深度测试、背面剔除、棋盘格纹理和 canvas resize。分别从不同距离观察倾斜平面，比较有/无 mipmap。

验收：区分模型、世界、视图、裁剪、NDC 与窗口空间；知道 camera aspect 与 viewport 不是同一设置。

此阶段不要同时引入复杂 PBR、骨骼动画和多光源，避免多个错误相互遮盖。

## 阶段 3：把同一场景迁入 Three.js

读[第 04 章](04-threejs-and-frameworks.md)。

实验：用 `BufferGeometry + Mesh + Camera + WebGLRenderer` 重建同一对象；再比较内置材质与 `ShaderMaterial`。

验收：说明框架管理的缓存、上传、状态与 draw；解释修改 uniform 与改变材质程序结构时更新方式为什么不同。

读源码时沿着一帧的数据流走，不按目录随机浏览：

```text
render -> 可见对象与列表 -> 材质程序 -> uniform/attribute -> 状态 -> draw
```

## 阶段 4：理解表面为什么这样亮

读[第 05 章](05-lighting-color-and-postprocessing.md)。

实验：方向光、不同 roughness/metalness、法线贴图、阴影；先固定曝光和环境，再一次改一个参数。验证颜色贴图与数据贴图的编码。

验收：解释 Fresnel、roughness 与高光、metallic 与漫反射的关系；发现颜色错误时不只通过增大光强补偿。

## 阶段 5：建立两到三个 pass

实验：主场景到 render target、一个 blur 或边缘效果、最终显示转换。画出资源读写图，记录每个 target 的格式、尺寸、采样数、清除与生命周期。

验收：无 read/write feedback loop；resize 后所有相关目标尺寸正确；知道多一次全屏 pass 消耗什么。

## 阶段 6：做一次真实 profiling

读[第 06 章](06-performance-and-debugging.md)。

实验：固定场景，分别改 DPR、draw 数、材质复杂度、阴影和后处理。能用 timer query 时记录 GPU 时间与 disjoint；不能用时明确工具限制，不把 CPU 计时伪装成 GPU 结果。

验收：提出瓶颈假设，给出对照结果；连续进入/退出场景检查资源 ownership 与释放。

## 阶段 7：再进入 WebGPU 与节点材质

读[第 07 章](07-webgpu-wgsl-and-tsl.md)。

实验：将一个简单自定义材质重写为 TSL，分别核对 WebGPU 与强制 WebGL 2 后端；若学习 compute，再另做一个有边界检查的独立实验。

验收：理解 pipeline、bind group、buffer layout 与队列提交；清楚哪些旧 GLSL 和后处理代码不能原样搬迁。

## 进一步深入

完成前面的实验后再选择一条研究支线，而不是一次把所有名词堆在第一份项目中：

- 材质与光照：BRDF 推导、IBL 预积分、能量补偿、透明与 transmission。
- 渲染组织：deferred、clustered lighting、render graph、资源复用。
- 动态几何：骨骼、morph、instancing、GPU 粒子和数据更新。
- 屏幕空间与时间：SSAO、SSR、TAA、motion vectors、历史拒绝。
- 大规模场景：LOD、空间结构、流式加载、资产压缩与移动 GPU。

这些是后续学习方向，本次笔记不声称已经完整实现或测量。

## 实验笔记模板

```text
问题与假设：
库版本 / 浏览器 / GPU / 后端：
输入资产与数据：
坐标 / 颜色 / resource layout 契约：
baseline：
本次唯一改动：
输出图像、CPU/GPU指标和测量限制：
符合或不符合假设：
可能的混杂因素：
代码与来源：
下一步：
```
