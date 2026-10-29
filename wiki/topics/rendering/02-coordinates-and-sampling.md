# 02 坐标、投影、插值与采样

研究日期：2026-10-29。前置：[GPU 管线](01-gpu-pipeline-and-shaders.md)。本文公式采用列向量，WebGL 深度约定采用未启用 clip-control 改写的常规管线。

## 1. 先确定坐标约定，再写矩阵

一条顶点变换链：

```text
模型局部坐标 --M--> 世界坐标 --V--> 相机坐标 --P--> 齐次裁剪坐标
   --裁剪、除以w--> NDC --viewport--> framebuffer 坐标
```

用列向量表示：

$$p_c = P V M \begin{bmatrix}x\\y\\z\\1\end{bmatrix}.$$

最右边的变换先作用。矩阵的存储顺序、向量放左边还是右边、坐标系左右手性是三个不同问题，不能统称“矩阵是反着乘的”。Three.js 的数学代码、WebGL 上传布局和别的教程可能选择不同表达约定。[C1][C2]

需要明确的五项契约：

| 契约 | 本文约定 | 混用的症状 |
| --- | --- | --- |
| 向量 | 列向量 | 变换顺序错误 |
| 相机前方 | 常规 Three.js 相机局部 `-Z` | 物体在相机背后 |
| 矩阵上传 | column-major 数组，`transpose=false` | 平移、投影失效 |
| 深度范围 | WebGL NDC `[-1,1]`；WebGPU `[0,1]` | 裁剪或深度比较不一致 |
| 屏幕坐标 | 不默认等同 DOM 坐标 | 拾取 Y 方向或缩放错误 |

`M` 是模型到世界的变换；`V` 通常是相机世界变换的逆，不是把相机位置直接填入平移矩阵。修改 Three.js 相机 FOV、aspect、near 或 far 后，需要更新投影矩阵。[C1][C3]

## 2. 齐次坐标不是给 3D 增加一个空间维度

在仿射变换中，位置使用 `w=1`，方向使用 `w=0`。平移列因此会影响位置，但不会影响方向。

投影之后的 `w` 不再只是这个初始值。标准透视矩阵可得到 `w_c=-z_view`，从而：

$$x_{\mathrm{ndc}}=x_c/w_c,\quad y_{\mathrm{ndc}}=y_c/w_c,\quad z_{\mathrm{ndc}}=z_c/w_c.$$

同样的横向位移，远处较大的 `w` 会把屏幕位移缩小。这是“远小近大”对应的计算，不是 Shader 自动识别物体距离。[C1]

裁剪发生在透视除法之前。常规 WebGL 可见体满足：

$$-w_c \le x_c,y_c,z_c \le w_c.$$

WebGPU 的 Z 条件则是 `0 <= z_c <= w_c`。跨过 near plane 的三角形需要裁剪；不能先把 `w` 丢掉再用一个三维立方体简单判断所有图元。[C1][C4]

`gl_Position = vec4(projected.xyz / projected.w, 1.0)` 不是标准透视顶点输出方式：它改变了裁剪和后续属性插值使用的信息。一般应输出完整的 `projected`。

## 3. 透视矩阵与深度精度

令 `n=near>0`、`f=far>n`、`s=1/tan(fovY/2)`、`a=aspect`。常规 WebGL 透视矩阵为：

$$
P =
\begin{bmatrix}
s/a & 0 & 0 & 0\\
0 & s & 0 & 0\\
0 & 0 & -(f+n)/(f-n) & -2fn/(f-n)\\
0 & 0 & -1 & 0
\end{bmatrix}.
$$

它把相机空间的 `z=-n` 映射为 NDC `-1`，`z=-f` 映射为 NDC `1`。Three.js 源码针对 WebGL、WebGPU 和 reversed depth 分支采用不同系数，不能复制一份投影矩阵用于全部后端。[C3]

若用正距离 `d=-z_view`，默认 depth range `[0,1]` 下：

$$z_{\mathrm{depth}}=\frac{f}{f-n}-\frac{fn}{(f-n)d}.$$

由此自行求导：

$$\frac{dz_{\mathrm{depth}}}{dd}=\frac{fn}{(f-n)d^2}.$$

这是教学推导：距离越远，相同世界距离对应的深度变化越小；固定精度深度缓冲更容易在那里混淆两个表面。`near` 极小又 `far` 极大常导致 z-fighting。

排查顺序：

1. 确认是否真有重叠、共面几何。
2. 根据业务范围合理设置 near/far，而不是习惯性设置 `0.0001` 和 `1000000`。
3. 需要覆盖极大尺度时，再研究 reversed-Z、深度格式、浮动原点等方案。
4. 改用 reversed-Z 时连同清除值、比较方向、投影约定一起核对。

这里的数学不等于某设备的量化误差测量；浮点和定点 depth 格式的误差分布不同。

## 4. 为什么 UV 不能简单屏幕线性插值

设三角形三个顶点的属性是 `a_i`，裁剪坐标的第四分量是 `w_i`，片元处的屏幕重心坐标为 `lambda_i`。

默认平滑属性的透视校正关系：

$$
a =
\frac{\sum_i \lambda_i a_i/w_i}
{\sum_i \lambda_i/w_i}.
$$

`lambda_i` 的和为 1，但不能因此去掉分母。三个 `w` 相等时才退化成普通线性插值。顶点到片元的插值语义由着色语言与光栅化规则定义，`flat` 又是另一种契约。[C5]

教学例子：`lambda=[0.5,0.25,0.25]`、`a=[0,1,0]`、`w=[1,2,4]`。

```text
屏幕线性结果 = 0.25
透视校正结果 = 0.125 / 0.6875 = 0.181818...
```

把一块倾斜平面画成棋盘格，可以直观看到错误线性 UV 的扭曲。不要把这个“普通属性”公式再次套到已经定义好的屏幕深度插值上；NDC 深度和相机空间线性距离也不是同一数值。

## 5. 法线为什么用逆转置矩阵

位置与切向量服从几何变换，但法线的职责是继续垂直于变换后的表面。

若原切向量 `t` 和法线 `n` 满足 `n^T t=0`，线性变换为 `A`，则：

$$n'=(A^{-1})^T n,\qquad {n'}^T At=n^Tt=0.$$

这是一段教学推导。对于非均匀缩放，直接使用 `A*n` 一般不保留垂直关系。Three.js 的 `normalMatrix` 由 model-view 的左上 `3x3` 部分取逆转置得到。[C2]

具体例子：

```text
t = [1,-1,0], n = [1,1,0], A = diag(2,1,1)
A*t = [2,-1,0]
错误法线 A*n = [2,1,0]，点积为3
正确法线 inverse-transpose(A)*n = [0.5,1,0]，点积为0
```

后续再 normalize；在片元阶段重新 normalize 插值后的法线。奇异变换，例如一个缩放轴为零，无法按普通逆矩阵关系处理。

法线、光方向、视线方向必须处于同一坐标空间。切线空间法线贴图还要通过 TBN 基转换；它不等于把贴图 RGB 当世界法线。

## 6. Texture 是采样信号，不只是图片

需要分开记录：

- 存储：像素格式、数据类型、颜色编码、各 mip level。
- 定位：UV、寻址模式、翻转、纹理矩阵。
- 重建：nearest、linear、mipmap、各向异性过滤。
- 使用：颜色、法线、粗糙度、深度、其他数据。

缩小时一个片元可能覆盖很多 texel。单次基础层采样容易产生闪烁和走样；mipmap 预先准备不同尺度的信号。常规隐式 LOD 选择与纹理坐标的屏幕导数相关，不只是“相机离得远就换小图”。[C6]

对一张大的正方形贴图，完整 mip 链 texel 数约为：

$$WH(1+1/4+1/16+\cdots)\approx \tfrac43 WH.$$

`4096x4096` RGBA8 基础层约 `64 MiB`，完整 mip 链约 `85.33 MiB`。这只是理论纹理存储，不含 CPU 解码副本、驱动开销、对齐与其他资源。

矩形和极窄纹理不要机械套用 `4/3`；应逐层按 `max(1,floor(width/2))`、`max(1,floor(height/2))` 求和。

GPU 压缩纹理与 PNG/JPEG 传输压缩不是一回事。法线、粗糙度等数据也不应因为来自 PNG 就被当 sRGB 解码。[C6][C7]

## 7. 自测

1. 相机向右移动时，为什么视图变换通常使场景向左？
2. `w=0` 为何能表示方向，但不能拿所有投影结果的 `w` 强制改成零？
3. 透视除法与裁剪为什么要按正确次序执行？
4. 非均匀缩放后，为什么旋转矩阵式的法线处理不够？
5. 为什么 mipmap 不能解决所有纹理倾斜视角走样？
6. 为什么 CSS 中 `800x600` 的画布不一定只有 48 万个 GPU 像素？

数值例子可运行[数学实验](examples/pipeline-math.mjs)和[测试](examples/pipeline-math.test.mjs)。下一章：[WebGL 2 资源模型](03-webgl2-api-and-resource-model.md)。

## 一手来源

所有入口于 2026-10-29 核验；Three.js 链接冻结到 `0.186.1` 对应源码。

[C1]: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_model_view_projection "MDN: WebGL model view projection"
[C2]: https://github.com/mrdoob/three.js/blob/9b4a2ac29c63ccb43fd51c5661f2f873ac2c39b8/src/math/Matrix3.js "Three.js: Matrix3.getNormalMatrix"
[C3]: https://github.com/mrdoob/three.js/blob/9b4a2ac29c63ccb43fd51c5661f2f873ac2c39b8/src/math/Matrix4.js "Three.js: projection matrices"
[C4]: https://www.w3.org/TR/2026/CRD-webgpu-20260915/#coordinate-systems "W3C WebGPU: coordinate systems"
[C5]: https://www.w3.org/TR/2026/CRD-webgpu-20260915/#rasterization "W3C WebGPU: rasterization and interpolation"
[C6]: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices "MDN: texture and mipmap practices"
[C7]: https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc "Khronos: glTF texture semantics"
