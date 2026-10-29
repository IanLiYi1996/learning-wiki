# WebGL2 API 与资源模型：从三角形到多通道渲染

- 所属层次：浏览器渲染 / GPU 编程；前置：JavaScript、向量与矩阵、三角形光栅化。
- 核验日期：2026-10-29；状态：机制与官方文档已核验，浏览器 / GPU 实验待执行。
- 学习目标：能说明一次 draw 读取哪些资源、依赖哪些状态，以及为何“对象存在”不等于“可以绘制”。
- 阅读顺序：前置 [01 GPU 管线与着色器](01-gpu-pipeline-and-shaders.md)、[02 坐标与采样](02-coordinates-and-sampling.md)；下一章 [04 Three.js 与框架](04-threejs-and-frameworks.md)。
- 来源约定：正文编号对应末尾官方链接；Khronos 规定语义，MDN 解释浏览器 API，Three.js 官方资料用于迁移。
- 版本边界：Khronos `latest` WebGL1/2 页面当前标为 2026-06-30 Editor's Draft，是工作草案而非新版已普遍落地的承诺；本文不依赖草案新增入口。[1][2]

## 1. 先建立模型：WebGL 不是“把 JavaScript 放到 GPU”

CPU 用 JavaScript 创建资源、上传字节、设置状态并提交命令；GPU 按 program、顶点输入与当前 framebuffer 执行。TypedArray 是 CPU 数据，WebGLBuffer 是 context 所有的资源句柄；二者不是共享数组。修改上传后的 TypedArray 不会自动更新 buffer。[2][8]
最小路径是：顶点输入 → vertex shader 写 `gl_Position` → 图元装配与裁剪 → 透视除法、viewport、光栅化与插值 → fragment shader → 深度 / 模板测试与混合 → attachment。这里是概念顺序，不保证硬件逐项串行；深度测试可能提前执行。[2][3]
`gl_Position` 是齐次裁剪坐标，不是像素坐标；除以 w 后，WebGL 的 NDC 三轴范围为 [-1,1]，默认深度映射到 [0,1]。插值默认是透视校正的，整数跨阶段数据须用 `flat`。[3][9]

| 对照 | WebGL1 | WebGL2 |
| --- | --- | --- |
| 基础 API / shader | 接近 OpenGL ES 2.0 / GLSL ES 1.00 | 接近 ES 3.0；接受 ES 1.00 与 ES 3.00 shader，另有 WebGL 限制 |
| 顶点组织 | VAO、instancing、32 位索引通常通过对应扩展 | VAO、instancing、`UNSIGNED_INT` 索引为核心 |
| 纹理与目标 | NPOT 纹理有 wrap / mipmap 限制；MRT 等需扩展 | NPOT 无这组特殊限制；3D / array texture、MRT、sized format 等为核心 |
| 数据组织 | 普通 uniforms；无核心 UBO / transform feedback | UBO、transform feedback、query、sync、像素 buffer 等 |

表中“核心”不代表资源限额无限；扩展和设备能力仍须查询。WebGL2 也不完全向后兼容，不能只把 `getContext("webgl")` 换成 `"webgl2"`；例如固定索引 primitive restart 总是开启，各索引类型最大值成为 restart 标记。[1]
尤其不要把 desktop GL 或 ES 3.1+ 的 geometry shader、tessellation shader、compute shader、SSBO、image load/store 当作 WebGL2 功能；WebGL2 没有这些核心入口。[1][3]

### GLSL ES 1.00 → 3.00：迁移的是接口契约

- 1.00 顶点输入 `attribute` → 3.00 顶点 `in`；顶点 `varying` → `out`，片元 `varying` → `in`。
- 1.00 `gl_FragColor` → 自定义片元 `out vec4`，可用 `layout(location=0)`；`texture2D` / `textureCube` → `texture`。
- 两个阶段使用一致版本；原生 WebGL 的 ES 3.00 源码固定以 `#version 300 es` 开始，放在字符串第一行，后接换行，不能先拼接 precision 或宏。
- 片元 float 没有默认精度，显式写 `precision highp float;`；精度限定不是“所有设备数值逐位一致”的承诺。高动态范围纹理还应显式声明 sampler 精度。

为什么：link 不只是连接两段源码，还要验证阶段接口、uniform 定义和资源限额；同名输入输出的类型等接口条件不满足会失败。ES 1.00 源码不能凭 WebGL2 context 自动获得 ES 3.00 语法。[1][3]

## 2. Context、编译、链接与三种错误通道

`canvas.getContext("webgl2", options)` 返回 context 或 `null`；同一 canvas 同一模式再次调用返回同一个 context，不能先创建 2D context 再在该 canvas 创建 WebGL2。创建选项首次生效；实际参数用 `getContextAttributes()` 读取。`null` 还可能来自资源或策略限制，不应直接写成某浏览器品牌“不支持”。[1][4]
program 建立过程：`createShader → shaderSource → compileShader → attachShader → linkProgram → useProgram`。编译检查 `COMPILE_STATUS` 与 shader log；链接检查 `LINK_STATUS` 与 program log；成功编译不保证成功链接，成功链接也不保证当前 draw 状态合法。[5]
教学时可逐个同步检查方便定位；大量 shader 的生产初始化应批量提交并检测 `KHR_parallel_shader_compile`，之后跨帧查询 `COMPLETION_STATUS_KHR`，完成后再读链接状态。扩展不保证总编译时长更短。[23]

| 通道 | 典型问题 | 检查方式 |
| --- | --- | --- |
| JavaScript / DOM 异常 | 参数对象不合法、跨源图像上传不满足 origin / CORS 规则 | `try/catch` 与浏览器 Console |
| shader / program 失败 | 语法、版本、接口不匹配 | 状态查询 + info log；不是只看 `getError()` |
| GL error flag | enum、数值、状态、FBO、内存问题 | 开发阶段在小命令组后读取 `getError()` 至 `NO_ERROR` |

GL 错误通常不抛 JS 异常，错误命令被忽略；所以“没有异常”不等于画对了。`CONTEXT_LOST_WEBGL` 在丢失后首次 `getError()` 返回，此后可返回 `NO_ERROR`，仍需 `isContextLost()` / 事件判断。不要每个生产 draw 都同步读错误状态。[2][6][22]

## 3. Buffer、attribute、VAO、index、uniform 与 texture unit

`bufferData(target, typedArray, usage)` 分配存储并复制数据；`bufferSubData` 更新既有区间而不扩容。`STATIC_DRAW` / `DYNAMIC_DRAW` 是使用提示，不是只读 / 可变权限。只按字节数分配的 WebGL 存储也要初始化，不能读取到别人的未初始化显存。[2][8]
attribute 是 shader 输入槽位，不是 buffer 对象。`vertexAttribPointer(location,size,type,normalized,stride,offset)` 把调用当时 `ARRAY_BUFFER` 的对象与解码规则记录下来；stride / offset 单位都是字节。槽位还要 `enableVertexAttribArray`；整数 shader 输入 `ivec/uvec` 应走 `vertexAttribIPointer` 并匹配符号类型。[1][8]

| 状态归属 | 保存什么 | 不保存什么 |
| --- | --- | --- |
| VAO | attribute enable、格式、stride、offset、各槽位关联的 buffer、divisor；`ELEMENT_ARRAY_BUFFER` 绑定 | program、uniform、texture、FBO；当前全局 `ARRAY_BUFFER` 绑定 |
| program | 链接后的接口与普通 uniform 值 / uniform-block 绑定关系 | VAO 与 texture unit 上实际绑定的 texture |
| context / 绑定对象 | 当前 program / VAO / FBO、各 texture unit 绑定、深度与混合等状态 | 不会自动从其他 context 导入资源 |

VAO 保存 buffer 引用与解释规则，不复制 buffer 内容；相同 buffer 更新后，多个 VAO 会看到新数据。设置 pointer 后 `bindBuffer(ARRAY_BUFFER,null)` 不会取消该 attribute；但在 VAO 仍绑定时清空 `ELEMENT_ARRAY_BUFFER` 会取消该 VAO 的索引绑定。被禁用槽位的常量 attribute 值不是 VAO 状态。[1][7]
`drawElements(mode,count,type,offset)` 的 count 是索引数，offset 是索引 buffer 内字节偏移；`Uint16Array` 配 `UNSIGNED_SHORT`，`Uint32Array` 配 `UNSIGNED_INT`。索引选择一整套 attribute，因此同位置但 UV / 法线不同的顶点通常要拆开；索引 buffer 也不能与其他数据 buffer 随意混用。[1][2]
`getAttribLocation` 可能是 -1；`getUniformLocation` 可能是 `null`，原因包括未声明、未激活 / 被优化掉、名称错误。必需接口应断言，可选接口允许缺失；`uniform*(null,...)` 静默无操作。location 属于特定 program 的链接结果，重链接 / 恢复后重新查询；矩阵上传 `transpose` 必须为 false。[1][10]
sampler uniform 保存的是 unit 整数，不是 texture 或 `TEXTURE0` enum：`activeTexture(TEXTURE0+i) → bindTexture(TEXTURE_2D,tex) → uniform1i(location,i)`。分别查询 vertex / fragment / combined texture-unit 限额；不同 sampler 类型不能错误地指向不匹配的纹理。[1][11]
纹理还依赖 internalFormat / format / type、mipmap 完整性、过滤与 wrap；只上传 level 0 时要确保 min filter 不要求缺失的 mip。WebGL2 的 sampler object 可覆盖绑定 unit 的采样参数，排查时不能只检查 texture 参数。[1][22]

## 4. CSS 尺寸、drawing buffer、viewport 与 DPR

CSS 尺寸决定页面布局，`canvas.width/height` 请求像素存储尺寸，`gl.drawingBufferWidth/Height` 才是实际尺寸。WebGL 不自动按 DPR 扩大存储；`viewport` 把 NDC 映射到目标像素，不会随 canvas resize 自动更新。[2][9]
常用近似：无 border / padding 的 canvas 内容宽高 × DPR，取整数再设置 width / height；只在尺寸真的变化时赋值。下面示例把 DPR 上限设为 2，这是质量 / 成本策略，不是规范规定。[2][22]
非整数 DPR、缩放与跨屏可产生像素对齐误差；检测并优先使用 `ResizeObserver` 的 `device-pixel-content-box`，不支持时退回内容尺寸 × DPR。不要把带 CSS transform 的外框尺寸无条件当作内容像素尺寸。[22]
resize 会清空 / 重建默认 drawing buffer 内容，但不自动重建应用自己的 FBO，也不销毁所有 GPU 对象；viewport、相机 aspect、离屏目标尺寸分别维护。切换 FBO 后，同样显式设置它的 viewport。[1][2][9]

## 5. 原创最小例：一对 GLSL ES 3.00 shader + 完整 JavaScript

把以下单段粘贴到有 `document.body` 的浏览器页面 Console 即可；它自行创建 canvas，无外部资源、HTML 工程或部署要求。预期是深色背景上的彩色三角形；不是本次已执行的实测结果。示例用独占 context，包含 resize、恢复重建与释放；同步编译检查仅用于教学。[4][5][8][10][21]

```js
function mountWebGL2Triangle(canvas) {
  const gl = canvas.getContext("webgl2");
  if (!gl) throw new Error("WebGL2 context 创建失败，请检查环境与 Console");
  // 成对 GLSL：#version 紧接模板字符串开头，没有前导空行。
  const vertexSource = `#version 300 es
precision highp float;
layout(location=0) in vec2 aPosition;
layout(location=1) in vec3 aColor;
uniform vec2 uScale;
out vec3 vColor;
void main() {
  gl_Position = vec4(aPosition * uScale, 0.0, 1.0);
  vColor = aColor;
}`;
  const fragmentSource = `#version 300 es
precision highp float;
in vec3 vColor;
layout(location=0) out vec4 outColor;
void main() {
  outColor = vec4(vColor, 1.0);
}`;
  const vertices = new Float32Array([
    -0.75, -0.6, 1.0, 0.25, 0.15,
     0.75, -0.6, 0.15, 0.85, 0.35,
     0.0,   0.75, 0.2, 0.45, 1.0
  ]);
  const indices = new Uint16Array([0, 1, 2]);
  let gpu = null, raf = 0, disposed = false;
  function build() {
    const owned = [];
    const release = () => {
      for (const [kind, object] of [...owned].reverse())
        gl[`delete${kind}`](object);
      owned.length = 0;
    };
    function make(kind, ...args) {
      const object = gl[`create${kind}`](...args);
      if (!object) throw new Error(`${kind} 创建失败或 context 已丢失`);
      owned.push([kind, object]);
      return object;
    }
    function compile(type, source) {
      const shader = make("Shader", type);
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS))
        throw new Error(gl.getShaderInfoLog(shader) || "shader 编译失败");
      return shader;
    }
    try {
      const vs = compile(gl.VERTEX_SHADER, vertexSource);
      const fs = compile(gl.FRAGMENT_SHADER, fragmentSource);
      const program = make("Program");
      gl.attachShader(program, vs); gl.attachShader(program, fs);
      gl.linkProgram(program);
      if (!gl.getProgramParameter(program, gl.LINK_STATUS))
        throw new Error(gl.getProgramInfoLog(program) || "program 链接失败");
      gl.detachShader(program, vs); gl.detachShader(program, fs);
      gl.deleteShader(vs); gl.deleteShader(fs);
      owned.splice(0, 2); // 后续只释放仍拥有的 program / VAO / buffers。
      const vao = make("VertexArray"), vbo = make("Buffer"), ibo = make("Buffer");
      gl.bindVertexArray(vao);
      gl.bindBuffer(gl.ARRAY_BUFFER, vbo);
      gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);
      gl.enableVertexAttribArray(0); gl.enableVertexAttribArray(1);
      gl.vertexAttribPointer(0, 2, gl.FLOAT, false, 20, 0);
      gl.vertexAttribPointer(1, 3, gl.FLOAT, false, 20, 8);
      gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ibo);
      gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, indices, gl.STATIC_DRAW);
      gl.bindVertexArray(null); gl.bindBuffer(gl.ARRAY_BUFFER, null);
      gl.bindFramebuffer(gl.FRAMEBUFFER, null);
      for (const cap of [gl.BLEND, gl.DEPTH_TEST, gl.CULL_FACE, gl.SCISSOR_TEST])
        gl.disable(cap);
      gl.colorMask(true, true, true, true); gl.depthMask(true);
      gl.clearColor(0.04, 0.07, 0.11, 1.0);
      return { program, vao, scale: gl.getUniformLocation(program, "uScale"), release };
    } catch (error) { release(); throw error; }
  }
  function frame() {
    if (disposed || !gpu || gl.isContextLost()) return;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(1, Math.round(canvas.clientWidth * dpr));
    const h = Math.max(1, Math.round(canvas.clientHeight * dpr));
    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w; canvas.height = h;
    }
    const dw = gl.drawingBufferWidth, dh = gl.drawingBufferHeight;
    gl.viewport(0, 0, dw, dh); gl.clear(gl.COLOR_BUFFER_BIT);
    gl.useProgram(gpu.program); gl.bindVertexArray(gpu.vao);
    if (gpu.scale !== null)
      gl.uniform2f(gpu.scale, Math.min(1, dh / dw), Math.min(1, dw / dh));
    gl.drawElements(gl.TRIANGLES, indices.length, gl.UNSIGNED_SHORT, 0);
    raf = requestAnimationFrame(frame);
  }
  function lost(event) {
    event.preventDefault(); cancelAnimationFrame(raf);
    gpu = null; // 旧句柄全部无效；保留 CPU arrays / shader 源码。
  }
  function restored() {
    if (disposed) return;
    try { gpu = build(); raf = requestAnimationFrame(frame); }
    catch (error) { console.error("恢复重建失败", error); }
  }
  gpu = build();
  canvas.addEventListener("webglcontextlost", lost);
  canvas.addEventListener("webglcontextrestored", restored);
  raf = requestAnimationFrame(frame);
  return { gl, dispose() {
    disposed = true; cancelAnimationFrame(raf);
    canvas.removeEventListener("webglcontextlost", lost);
    canvas.removeEventListener("webglcontextrestored", restored);
    if (gpu && !gl.isContextLost()) gpu.release();
    gpu = null;
  }};
}
const triangleCanvas = document.createElement("canvas");
triangleCanvas.style.cssText = "width:420px;height:260px;max-width:100%;display:block";
document.body.appendChild(triangleCanvas);
const triangleDemo = mountWebGL2Triangle(triangleCanvas);
```

停止时执行 `triangleDemo.dispose()`，再自行 `triangleCanvas.remove()`；释放资源不等于删除 DOM。位置与颜色分别占 2 / 3 个 float，所以 stride 为 20 字节、颜色 offset 为 8 字节；uniform scale 用实际 drawing-buffer aspect 保持等比例。[8][9]
边界：示例不是资源管理框架；未实现创建失败后的 UI 回退、最大尺寸预算、热替换 program、共享 context 状态隔离。恢复可能永不发生，应允许用户重试或展示替代内容。[1][4][21]

## 6. FBO、attachments、completeness 与 MRT

FBO 是 attachment 组织与路由对象，不是“另一张 canvas”。texture / renderbuffer 提供存储；`framebufferTexture2D` 连接纹理特定 mip image，`framebufferTextureLayer` 连接 layer。renderbuffer 不能直接被 shader 采样，适合不需采样的深度 / 多重采样存储。[1][2]
创建顺序：分配目标存储 → 绑定 FBO → 接上 color 与可选 depth/stencil → 设置 draw buffers → `checkFramebufferStatus`。本节示例应优先从 RGBA8 + 同尺寸深度附件开始，便于隔离格式问题。[1][12]

- 非零、已定义、attachment-renderable 的 image 才能组成目标；WebGL2 仍要求附件尺寸匹配，不能套用 native ES3 对不同尺寸附件的宽松规则。
- depth 与 stencil 若同时存在，须使用同一 image；同一 image 不能重复接到多个 color attachment。
- 多重采样 renderbuffer 的 samples 要匹配，不能把非零 samples renderbuffer 与单采样 texture 任意混装。
- `FRAMEBUFFER_COMPLETE` 只说明附件组合完整，不检查本次 shader / sampler / blend 状态，也不表示已经画出了正确内容。

上述 WebGL 专属规则见 [1]，状态枚举见 [12]；在初始化、resize 或重接附件后检查，不必每帧同步检查稳定 FBO。
MRT：片元写 `layout(location=0/1) out ...`，分别接 `COLOR_ATTACHMENT0/1` 并 `drawBuffers([gl.COLOR_ATTACHMENT0,gl.COLOR_ATTACHMENT1])`。数组位置 i 对应输出位置 i，不能任意把位置 0 路由到附件 1；查询 `MAX_DRAW_BUFFERS` 与 `MAX_COLOR_ATTACHMENTS`。[1][13]
float / normalized attachment 对应浮点输出，整数 attachment 对应 `ivec/uvec`；整数目标用 `clearBufferiv/uiv`，不能直接以普通 `clear(COLOR_BUFFER_BIT)` 清除。MRT 不等于各 attachment 独立 blend：核心混合状态共享，独立配置另检测扩展。[1][13]
绑定 `FRAMEBUFFER` 会设置读 / 写绑定，`DRAW_FRAMEBUFFER` 与 `READ_FRAMEBUFFER` 可分开设置；读回 MRT 时用 `readBuffer(COLOR_ATTACHMENTi)`。默认目标使用 `BACK`；`bindFramebuffer(...,null)` 回到默认目标仍需恢复 viewport。[1][13]
离屏 MSAA 通常先绘到多采样 renderbuffer，再用 `blitFramebuffer` resolve 到可采样的单采样目标；按 internal format 查询支持的 samples，不能只拿全局 `MAX_SAMPLES` 当所有格式都支持的值。[1]

## 7. 浮点纹理：存储是前提，渲染 / 过滤 / 读回是不同问题

不要用“支持 float texture”一个布尔值描述整条链；以下仅讨论 WebGL2 常见 RGBA 格式，mipmap 与 sampler 类型也要合法。[1][14][15][16]

| 格式 | 存储 / 采样 | 作为 color attachment 渲染 | 线性过滤 | 浮点读回 |
| --- | --- | --- | --- | --- |
| RGBA16F | 核心格式 | 检测 `EXT_color_buffer_float` 或 `EXT_color_buffer_half_float` | 核心支持 half-float linear，非 32F 的规则 | 启用对应 render 扩展、FBO 完整后用 RGBA / FLOAT |
| RGBA32F | 核心格式 | 检测 `EXT_color_buffer_float` | 检测 `OES_texture_float_linear`；缺失时采用合法 NEAREST 路径 | 同左述完整浮点 FBO，RGBA / FLOAT |

`EXT_color_buffer_float` 的可渲染清单是 R16F、RG16F、RGBA16F、R32F、RG32F、RGBA32F、R11F_G11F_B10F，不包含 RGB16F / RGB32F。不能凭 RGB32F 能上传就判定其可以作 render target。[14]
已获得 render 扩展后，RGBA / FLOAT 是浮点 color buffer 的有效读回组合，目标用 `Float32Array`；RGBA / UNSIGNED_BYTE 不能当作通用浮点读回。其他组合需在选定读 FBO / attachment 后查询 `IMPLEMENTATION_COLOR_READ_FORMAT/TYPE` 并符合规范，不是任意格式转换器。[14][15][18]
额外独立能力：32F blending 要检测 `EXT_float_blend`；支持时可被 color-buffer 扩展隐式启用，但不能假定一定有。16F blending 不要求这个 32F 扩展，前提仍是该 16F attachment 合法可渲染。[17][22]
验证应逐项记录：启用扩展 → 分配 sized format → attachment 检查 → 写入已知 float 色值并读回 → 用独立目标检查过滤结果；FBO complete 不能证明 linear 正确。`readPixels` 原点在左下；TypedArray 类型、长度和 `PACK_ALIGNMENT` / pack 状态都要匹配。[12][14][16][18]

## 8. Depth、blending、透明度与反馈循环

深度测试、深度写入是不同开关：`enable(DEPTH_TEST)` 控制比较，`depthMask(true/false)` 控制写；目标还得有 depth attachment。禁用深度测试时，普通 draw 不写深度；`depthMask(true)` 本身不会启用测试。[2]
`clear` 不受 viewport 限制，却受 scissor 与写入 mask 影响；`depthMask(false)` 会让 `clear(DEPTH_BUFFER_BIT)` 无效。开始新帧前恢复 depthMask / colorMask / stencilMask 和适当 scissor，别让透明 pass 的状态泄漏到下一帧。[2][19]
常见透明 pass：先不透明物体（depth test + write），再透明物体大致由远到近（depth test 保留、`depthMask(false)`、`enable(BLEND)`），结束恢复写入。排序不是相交透明几何的通解，WebGL 不自动替你排序。[2][25]
straight-alpha 常见组合为 `blendFuncSeparate(SRC_ALPHA,ONE_MINUS_SRC_ALPHA,ONE,ONE_MINUS_SRC_ALPHA)`；RGB 得到 `Cs·As + Cd·(1-As)`，alpha 为 `As + Ad·(1-As)`。若输出 RGB 已预乘 alpha，RGB 源因子用 ONE，不能再乘一次 alpha。[2]
canvas 的 `premultipliedAlpha` 描述浏览器页面合成预期，不会自动启用 BLEND 或自动给所有 shader RGB 预乘；纹理上传的预乘状态又是独立环节。三处表示须一致，黑边 / 光晕常是它们不一致。[2][4]
禁止在同次 draw 中采样当前写入的 attachment image，WebGL 对反馈循环产生 `INVALID_OPERATION`；换 FBO 名称但仍接同一纹理不是解决方案。实践上用两张独立纹理防止误踩 mip / layer 可达范围规则。[2]
ping-pong 的机制是：pass A 读纹理 A、写 FBO(B)；下一 pass 读 B、写 FBO(A)，交换角色。每个 pass 明确输入、输出、viewport、mask 与 blend；同一 context 中正常按序的 GPU pass 不需逐 pass `finish()`。[2]

## 9. Instancing、UBO、transform feedback：有限的数据并行

- Instancing：一次 `draw*Instanced` 复用几何；divisor=0 按顶点前进，divisor=1 按实例前进，d>1 每 d 个实例前进一次；shader 可用 `gl_InstanceID`。减少 CPU draw 开销，不消除实例自身的顶点 / 片元成本。
- 实例矩阵 `mat4` 占四个 attribute 槽，四列均设置 pointer、enable 和 divisor；把“每实例矩阵”误设成每顶点，是图形爆炸的常见原因。
- UBO：`layout(std140) uniform Camera { mat4 vp; vec4 eye; };`；获取 block index → `uniformBlockBinding(program,index,binding)` → `bindBufferBase(UNIFORM_BUFFER,binding,buffer)`。
- WebGL2 的 uniform block 只支持 std140，不支持 shared / packed；block index 是 program 内编号，binding 是 context 绑定槽，buffer 是字节存储，三者不要混淆。
- std140 不是 JS 紧密数组布局：数组 stride、矩阵列 stride、vec3 对齐会留空隙；可查询 `UNIFORM_OFFSET/ARRAY_STRIDE/MATRIX_STRIDE` 和 block size，按查询结果 / std140 规则打包。
- `bindBufferRange` 的起点需满足 `UNIFORM_BUFFER_OFFSET_ALIGNMENT`；检测 block-size 与 binding 数量限额。UBO 供 shader 读取，shader 不能把计算结果写回 UBO。

依据：[1][3][20]。可验证 UBO 布局：放入不同已知值，用片元颜色展示，再故意按紧密 float-array 写入，比较错位；“减少 API 更新数”不代表任何工作负载都会更快。
Transform feedback 捕获 vertex shader 输出到 buffer，发生在裁剪前；先 `transformFeedbackVaryings(program,names,mode)` 再 link，绑定 TF 对象与输出 buffer，再 begin → draw → end。仅更新数据时启用 `RASTERIZER_DISCARD`，结束后必须禁用，否则后续画面消失。[1][20]
用不同 buffer 做输入 / 输出，避免 TF 输出 buffer 同时处在其他冲突绑定点；交换时也要解绑旧 indexed TF 输出或切换对象，不是只交换 JS 变量。`beginTransformFeedback` 的图元类别要与 draw 兼容，输出容量也须覆盖捕获数据。[1]
它可做粒子状态更新等逐记录运算；fragment + FBO 可做逐 texel 运算。二者都不是 compute shader：没有 workgroup 共享内存 / barrier、任意存储写入与通用 dispatch，算法必须适配图形管线；不要因 Three 的 WebGPU 页面出现 compute 就认作 WebGL2 能力。[1][24]

## 10. Context loss / restoration 与资源生命周期

丢失可能来自 GPU 重置、系统切换或资源压力，并非只在出错程序发生。监听 canvas 的 `webglcontextlost`，`preventDefault()` 允许尝试恢复，停 RAF / 提交；用 CPU 资源描述保留重建材料，而不是把旧 WebGL handle 当资产。[2][21]
收到 `webglcontextrestored` 后，重建全部应用 GPU 对象：buffers、textures、samplers、shaders/programs、VAOs、FBOs/renderbuffers、TF/query/sync；重新上传内容、取 locations、查询能力并启用扩展、设置 viewport 与所有自定义状态。旧对象仍可能是 JS 非 null 引用，但已无效。[1][2][21]
异步加载回调还要检查“当前 context 世代”，避免旧请求把结果上传到新状态；失去 TF / ping-pong 累积状态后，要从 CPU 快照或确定初值重启，不能假装模拟连续。[2]
显式 `deleteBuffer/Texture/Program/VertexArray/...`，不用等 GC；删除句柄不保证显存当场释放，尚被使用 / 引用的资源可延后回收。移除 canvas 或清空 JS 数组也不是显式 GPU 清理。[2][22]
预算估算：RGBA8 每像素 4 字节、RGBA16F 8、RGBA32F 16；完整二维 mip 链约乘 4/3 只适用于大尺寸、近似正方形纹理。矩形尤其极窄纹理应逐层按 `max(1,floor(width/2))`、`max(1,floor(height/2))` 计算 texel 数并求和；还要算双缓冲、depth、MSAA 与驱动额外存储。DPR 翻倍导致面积约四倍；没有可移植的“剩余显存查询”可替代预算和上限。[22]

## 11. 调试与性能：找出同步点，不凭 draw 的 JS 耗时猜 GPU

先画纯色、关复杂状态，再逐一恢复 attribute、texture、FBO、depth、blend；记录每个 pass 的资源与状态，保存带行号的 shader log。开发期在分配 / 重绑定后读错误和 FBO 状态，生产热循环避免大量 `get*` 往返。[5][6][12][22]
`readPixels` 直接到 TypedArray 与 `getBufferSubData` 都可能等待 GPU；`performance.now()` 包住 `drawElements` 多半是在量 CPU 提交，不是 GPU 完成时间。`flush` 推送命令而不等待完成，`finish` 等待完成，会破坏流水并行。[1][2][22]
较少阻塞的读回：`PIXEL_PACK_BUFFER` 分配容量 → `readPixels(...,byteOffset)` → fence → 必要时 flush → 后续帧以 timeout=0 的 `clientWaitSync` 检查 → ready 后 `getBufferSubData` → 删除 fence / buffer。CPU 复制仍有成本；必须让出事件循环，禁止同步忙轮询。[1][22]
GPU 时间检测 `EXT_disjoint_timer_query_webgl2`：begin / end elapsed query，后续检查 available，且 `GPU_DISJOINT_EXT` 为 false 才采用结果；缺失时不编造 GPU 时间。编译状态的同步查询又是另一类卡顿，见第 2 节。[23]
优化候选：缓存不变 VAO/FBO，批量 draw / instancing，集中纹理上传，限制离屏尺寸，复用资源；移动 tile GPU 的不再使用附件可尝试 `invalidateFramebuffer`。分别测 CPU 提交、GPU pass、上传 / 读回和内存，实验前后同场景对比。[22]

## 12. 迁移到 Three.js：抽象升高，契约仍在

| 原生机制 | Three.js 对应概念 | 仍需自己判断 |
| --- | --- | --- |
| buffers / attributes / indices / VAO | `BufferGeometry`、`BufferAttribute`、`setIndex`；底层绑定由 renderer 管理 | 更新数据后标 `needsUpdate`，共享顶点语义与容量 |
| program / GLSL / uniforms | `ShaderMaterial` / `RawShaderMaterial`、`uniforms[name].value`、`glslVersion` | 接口、精度、版本及框架注入的声明 |
| texture / FBO / ping-pong | `Texture`、`WebGLRenderTarget`、`setRenderTarget` | 格式能力、输入输出不别名、resize、读回成本 |
| instancing / UBO | `InstancedMesh`、自定义实例属性、`ShaderMaterial.uniformsGroups` | 实例属性标更新，block 布局与资源限额 |
| viewport / 状态 / 生命周期 | `setSize`、`setPixelRatio`、material 状态、`.dispose()` | 相机 aspect、透明排序、所有权、资源恢复与缓存边界 |

这些是概念对应，不是公开一一暴露的 VAO 句柄；具体 API 以项目锁定版本为准。官方当前 `WebGLRenderer` 文档说明 r163 起不支持 WebGL1，但这不是所有浏览器的能力结论。[24][25]
移植本文 shader 可优先用 `RawShaderMaterial` 保留自己声明的接口；使用 `glslVersion: THREE.GLSL3` 时按该版本的源码前缀机制管理 `#version`，避免正文与自动前缀重复。`ShaderMaterial` 会提供框架的 built-in 定义，不宜机械复制所有声明。[24]
纹理 uniform 值交给 Three 设置，不手工传 unit；不随意改 renderer 内部 GL 绑定。必须共享 context 做原生绘制时，建立清楚的状态边界并使用公开 `resetState()`；它不是完整业务状态快照恢复。[25]
移除 mesh 不会自动释放其共享 geometry / material / texture；按所有权逐项 dispose，render target 也要释放。`renderer.info` 提供对象 / draw 统计而非精确显存字节；Three 仍不能替你把 GPU 独有的累积模拟状态恢复成丢失前数据。[2][25][26]

## 13. 可验证实验、自测与错误排查

以下全部是待执行实验，不是测量报告；每次记录浏览器版本、OS / GPU（允许时）、DPR、context 参数、扩展列表、错误 / log 和预期对照。[4][6][22]

1. VAO：先 pointer 指向 A，再绑定 ARRAY_BUFFER=B 但不重设 pointer；应仍读 A。绑定 VAO 时清空 ELEMENT_ARRAY_BUFFER，indexed draw 应失败。[7][8]
2. Resize：只改 CSS，再改 width/height 但不设 viewport，最后补 viewport；比较清晰度和映射范围。检查实际 drawing-buffer 尺寸，不仅看 DOM 宽高。[2][9]
3. 深度：FBO 有深度时先绘近物体，再 depthMask(false)、clear depth、绘远物体；比较恢复 depthMask(true) 后 clear 的结果。[19]
4. 浮点：逐个记录 16F / 32F render、linear、FLOAT readback、32F blend 能力；扩展缺失时记录降级，不偷偷依赖本机结果。[14][15][16][17][18]
5. 反馈：让 shader 采样当前输出 texture 应产生错误；换成两纹理 ping-pong 后应消除反馈错误。[2]
6. 丢失：检测 `WEBGL_lose_context` 后调用 lose；等待 lost 事件已处理，再在后续任务 restore；确认三角形重现，旧 location / buffer 不再使用。不要依赖立即恢复或固定耗时。[21]
7. 同步：同场景比较无读回、同步 readPixels、PBO+fence；记录帧时间分布，不把 API 提交耗时当 GPU 时间。无计时扩展时明确缺测。[22][23]

自测：① 为何改 CPU array 后图形不变？② 为什么 bind VAO 不会恢复 ARRAY_BUFFER？③ FBO complete 能证明 float linear 吗？④ depthMask(false) 后 clear depth 会怎样？⑤ TF 能否任意写邻居记录 / 使用 compute barrier？⑥ 恢复后除了重新上传顶点还缺哪些状态？
参考答案：① 上传是复制；② 保存的是槽位来源与索引绑定；③ 不能；④ 不清除；⑤ 不能据此获得 compute 能力；⑥ 所有 GPU 对象、接口位置、扩展与自定义状态都重建。回到对应章节解释“为什么”，不要只背 API。[1][7][8][19][21]

| 症状 | 首先核对 |
| --- | --- |
| 全黑但 clear 可见 | shader/link log、当前 program、VAO enable、pointer stride/offset、draw count、clip 坐标、RASTERIZER_DISCARD |
| `INVALID_OPERATION` | sampler / attachment 类型、反馈循环、整数 attribute、错 program location、UBO 容量、TF 冲突绑定 |
| `INVALID_FRAMEBUFFER_OPERATION` | 实际绑定读 / 写 FBO、附件尺寸 / 格式 / samples、目标扩展、完整性状态 |
| 缩放后模糊或只画一角 | CSS / 存储尺寸、实际 drawing buffer、viewport、离屏尺寸、相机 aspect |
| 透明遮挡 / 黑边 / 下一帧消失 | 排序、depth write、clear mask、scissor、straight / premultiplied alpha、blend 因子 |
| 读回失败 / 结果错位 | readBuffer、format/type/TypedArray、pack 状态与长度、原点方向、默认 buffer 的呈现后清除 |

排查表按前述机制组织，不能由某一症状直接判定唯一根因；先缩到最小 pass，再逐项验证。[1][2][5][6][12][18][19]

## 官方参考（核验日期统一为 2026-10-29）

[1]: https://registry.khronos.org/webgl/specs/latest/2.0/
[2]: https://registry.khronos.org/webgl/specs/latest/1.0/
[3]: https://www.khronos.org/registry/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf
[4]: https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/getContext
[5]: https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/linkProgram
[6]: https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/getError
[7]: https://registry.khronos.org/OpenGL/extensions/OES/OES_vertex_array_object.txt
[8]: https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/vertexAttribPointer
[9]: https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/viewport
[10]: https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/getUniformLocation
[11]: https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/activeTexture
[12]: https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/checkFramebufferStatus
[13]: https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext/drawBuffers
[14]: https://registry.khronos.org/webgl/extensions/EXT_color_buffer_float/
[15]: https://registry.khronos.org/webgl/extensions/EXT_color_buffer_half_float/
[16]: https://registry.khronos.org/webgl/extensions/OES_texture_float_linear/
[17]: https://registry.khronos.org/webgl/extensions/EXT_float_blend/
[18]: https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/readPixels
[19]: https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/clear
[20]: https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext/transformFeedbackVaryings
[21]: https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/webglcontextrestored_event
[22]: https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices
[23]: https://registry.khronos.org/webgl/extensions/EXT_disjoint_timer_query_webgl2/
[24]: https://threejs.org/docs/pages/ShaderMaterial.html
[25]: https://threejs.org/docs/pages/WebGLRenderer.html
[26]: https://threejs.org/docs/pages/BufferGeometry.html

- [1] WebGL2：核心功能、兼容差异、std140、FBO / TF / sync / readback；[2] WebGL1：共享状态、viewport、安全、反馈与 context 生命周期。
- [3] [GLSL ES 3.00.6][3] §§3.4、4.3、4.5、8；对照 [GLSL ES 1.00 revision 17](https://registry.khronos.org/OpenGL/specs/es/2.0/GLSL_ES_Specification_1.00.pdf)。原生 VAO 状态表 [7] 只用于解释状态归属，WebGL 限制仍以 [1][2] 为准。
- [4]–[13] MDN：context、[编译](https://developer.mozilla.org/en-US/docs/Web/API/WebGLRenderingContext/compileShader)、link、errors、顶点输入、uniform、texture units、viewport、FBO 与 MRT。
- [14]–[19] Khronos 扩展与 MDN：浮点 rendering / filtering / blending / readback 分界及 clear 的 mask 规则。
- [20] TF；UBO 另见 [uniformBlockBinding](https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext/uniformBlockBinding)、[getActiveUniforms](https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext/getActiveUniforms)；instancing 另见 [vertexAttribDivisor](https://developer.mozilla.org/en-US/docs/Web/API/WebGL2RenderingContext/vertexAttribDivisor)。
- [21]–[23] context 恢复、实践性能与 GPU timer；编译异步查询另见 [KHR_parallel_shader_compile](https://developer.mozilla.org/en-US/docs/Web/API/KHR_parallel_shader_compile)。
- [24]–[26] Three 官方：材质、renderer、geometry；另见 [RawShaderMaterial](https://threejs.org/docs/pages/RawShaderMaterial.html)、[InstancedMesh](https://threejs.org/docs/pages/InstancedMesh.html)、[WebGLRenderTarget](https://threejs.org/docs/pages/WebGLRenderTarget.html)。动态页面和草案可能改变，迁移时重新核对项目版本。
