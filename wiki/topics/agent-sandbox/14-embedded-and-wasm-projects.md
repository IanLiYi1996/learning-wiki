# 14 嵌入式、解释器与 Wasm 项目：不一定先建一座沙箱云

核验日期：2026-11-04。本章补充可嵌入应用、桌面或工具服务器的社区项目。源码公开、平台宣传、阅读推导与实际部署验证分开；本轮没有安装运行时、创建 VM、测试逃逸或复测厂商性能。

## 先确定需要给程序一台机器，还是几项能力

需要 shell、系统包、原生二进制与浏览器，和只需要遍历一份 JSON、调用几个经过授权的函数，是两类需求。前者可以评估嵌入式 microVM；后者可以评估受限解释器、Wasm runtime 或插件框架。API 都写着 `run`／`exec`，不说明它们具有相同环境和边界。

| 路线 | 本章项目 | 实际交付层 | 不能直接代入 |
| --- | --- | --- | --- |
| 嵌入式机器 | BoxLite、microsandbox | VM 生命周期、OCI 环境、执行与文件接口 | 不等于自动拥有租户管理与安全运营 |
| OS 级进程约束 | Anthropic sandbox-runtime | 文件、进程与代理网络政策的运行包装 | 不等于 guest kernel |
| 受限解释器 | Pydantic Monty | 语言解释、能力中介与资源预算 | 不等于完整 CPython＋任意 native wheels |
| Wasm runtime | Wasmtime、Wasmer、WasmEdge | 模块／组件执行与宿主接口 | 不等于无需适配的完整 Linux |
| 插件与工具服务 | Extism、Spin、Wassette | 插件接口、应用框架或 MCP 到 Wasm 的桥 | 不替代宿主函数的业务授权 |

定位依据见各节项目的一手来源。表中对“不能代入”的判断是本专题根据机制做的工程推导，不是已完成的跨项目安全评级。

## BoxLite：把一套机器执行能力嵌入应用

[BoxLite 仓库](https://github.com/boxlite-ai/boxlite)提供 Rust 核心、多个语言 SDK、CLI、可选 REST server，以及自建分布式运行环境的材料。其公开定位是每个 Box 以硬件虚拟化提供独立 kernel 的 microVM，再在 guest 中运行 OCI 环境；不是把模型生成的 Python 直接交给宿主 `eval`。[README](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/README.md)。

### 读源码时沿四条链路走

| 阅读入口 | 先搞清楚什么 | 不要从名字猜 |
| --- | --- | --- |
| `sdks/`、`docs/reference/` | 本地嵌入、REST 与语言绑定的接口 | 所有 SDK 版本与功能完全一致 |
| `docs/concepts/security.md` | shim 的宿主约束及配置 | 使用了 jailer，就与 Firecracker 是同一个 VMM |
| `docs/concepts/networking.md` | guest 到 host proxy 的通路、出口和 secret substitution | 使用 gVisor 网络栈，就用 Sentry 拦截了全部 syscall |
| `docs/concepts/storage.md` | OCI rootfs、QCOW2、host mount 与数据寿命 | 可保存磁盘就等于可恢复所有内存／连接 |

这几条入口都在官方仓库。安全说明中的图将 VM 一层写为 libkrun／KVM；网络说明中默认 gvproxy 使用 gVisor 的网络栈。**使用 gVisor 的网络库不是运行 `runsc` 应用内核**，同样“jailer 受 Firecracker 启发”不能改写为“BoxLite 一定由 Firecracker 运行”。[安全](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/docs/concepts/security.md)、[网络](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/docs/concepts/networking.md)。

### 默认值与平台差异必须另查

安全文档明确说默认配置优先兼容性，并给出启用更严格 `SecurityOptions` 的入口；网络文档默认 gvproxy 提供出站 Internet。不能把“存在网络允许列表”“有安全层”升级成“每种模式默认拒绝所有出站并启用所有宿主约束”。[安全配置](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/docs/concepts/security.md)、[网络配置](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/docs/concepts/networking.md)。

当前 README 分别列 macOS Apple Silicon、Linux x86_64／ARM64、Windows WSL2；macOS Intel 标为后续支持方向。Linux／WSL2 需要可用 KVM，因此“可嵌入”不代表任意笔记本或普通云 guest 都满足底层条件。[平台矩阵](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/README.md)。

磁盘、clone、host 目录与 detached 实例是值得学习的工作空间能力。存储文档区分 QCOW2 与通过 virtiofs 挂载宿主目录；后者是主动打开的数据通路。**工程建议**：为任务指定专属目录、只读输入与受控导出；不能因为有 VM，就把整台电脑的工作目录和秘密一起挂载进去。[存储](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/docs/concepts/storage.md)。

BoxLite 的项目材料可用于理解“库 → 本地机器 → REST 服务 → 自建节点池”的渐进路线。REST 鉴权、租户分配、配额、出口和回收仍要按实际运行模式验收；本轮没有把公开 Cloud 的能力自动视作自建配置的默认行为。

## microsandbox：程序化的本地 microVM 工作流

[microsandbox 当前仓库](https://github.com/superradcompany/microsandbox)提供 CLI 与 TypeScript、Rust、Python、Go SDK，围绕 OCI image、命令、shell、volume、snapshot 和 fork 组织使用方式。README 感谢 libkrun 等底层项目，并明确标为 beta：存在破坏性变化、缺失功能和不完善之处。[官方说明](https://raw.githubusercontent.com/superradcompany/microsandbox/main/README.md)。

本轮阅读到的平台前提是 macOS Apple Silicon、Linux KVM、Windows WHP；**不能把 BoxLite 的 Windows WSL2 条件照抄给 microsandbox，也不能从旧版文档反推当前实现**。这是公开需求矩阵，不是本轮在三种 OS 上做过运行验证。[需求与 beta 提醒](https://raw.githubusercontent.com/superradcompany/microsandbox/main/README.md)。

它和 BoxLite 可以放进同一个候选组，但应该测自己的工作负载：

- 已有 OCI image 能否启动，原生包和浏览器是否兼容？
- 创建、执行、取消、snapshot、fork 和关闭各保存什么状态？
- host mounts、端口、宿主设备与网络的有效政策是什么？
- 软件退出后 VM 是否仍运行，谁负责重连和最终回收？
- 多用户如何分别绑定实例、身份、文件与产物？

这些是原创建议，不是本轮声称已通过的功能矩阵。README 的启动时间脚注明确指某台 M1 上的 guest boot；不能与另一家平台包含排队、网络和工具 Ready 的时延组成排行榜。首次创建的 image pull 与后续 cache 也要分开计量。[计时范围与 cache](https://raw.githubusercontent.com/superradcompany/microsandbox/main/README.md)。

读源码可以先看 CLI／SDK 的生命周期调用，再追到 image、volume、执行与底层虚拟化路径；避免只阅读三个 SDK 调用就断言自己已经理解宿主隔离。示例和 Docker-in-sandbox、browser、warm-worker 教程属于任务适配资料，不是恶意多租户验收证明。

## Anthropic sandbox-runtime：给现有进程加 OS 政策

[sandbox-runtime／srt](https://github.com/anthropics/sandbox-runtime)公开为轻量进程约束工具。README 描述 macOS `sandbox-exec`、Linux bubblewrap 与代理网络过滤，不要求先启动容器；可用于 Agent、local MCP server、shell 等进程。项目同时标为研究预览，政策和 API 可能变化。[README](https://raw.githubusercontent.com/anthropics/sandbox-runtime/main/README.md)。

其学习价值是把“Agent 终端执行”与明确的目录／出口政策连接起来。它不是 Firecracker，不创建普通 Linux guest；保护范围取决于 OS、依赖、政策和兼容开关。

**工程建议**：为桌面 CLI 评估这条路线时，明确哪些宿主目录必需、哪些网络通道可绕过代理、是否能创建新 namespace／运行嵌套容器，以及子进程如何继承约束。当前 README 对若干兼容选项的限制有明确提醒；不要为跑通浏览器或 rootless 工具而放宽设置后，继续沿用原来“写访问被完整禁止”的结论。[限制与选项](https://raw.githubusercontent.com/anthropics/sandbox-runtime/main/README.md)。

这不是给陌生互联网用户提供任意代码服务的自动首选。对不互信租户，应回到[威胁模型](01-system-model-and-threats.md)检查是否接受共享 kernel、宿主用户和目录这一信任基础。

## Pydantic Monty：给 Agent 代码一套受控的语言能力

[Monty](https://github.com/pydantic/monty)是 Rust 实现的 Python sandbox。当前 README 区分 MIT 许可的 OSS package 与商业 Full Monty 服务；不能把开源解释器、独立 worker 和远端服务当成同一个交付物。Python 的具体语法、模块、类、文件与接口支持应查现行限制清单，不用早期“只支持几个表达式”的印象代替当前文档。[README](https://raw.githubusercontent.com/pydantic/monty/main/README.md)、[安全模型](https://pydantic.dev/docs/monty/concepts/security/)。

最重要的概念不是“它比容器快多少”，而是**代码能够向谁请求什么能力**。解释器中的文件、网络和外部函数由宿主映射／中介提供；可调用条目会暂停 sandbox 执行，再让宿主函数以其实际权限运行。因而注册一个“任意请求 URL”或“任意数据库 SQL”函数，会重新扩大能力面。[安全模型](https://pydantic.dev/docs/monty/concepts/security/)。

原创例：允许代码遍历一组订单，并调用 `lookup_order(order_id)`。宿主函数仍须验证当前租户和订单范围，限制次数与结果长度；不能仅因为 Python 在解释器中，就把任意 ID 查询视作已授权。

它适合进入候选组的前提是：任务可以由受支持语言能力与少量授权工具完成。若需要任意 native extensions、系统包、浏览器和复杂编译链，应另做兼容测试或转向完整机器路径。**不把 Monty 直接叫作 Wasm Python**：native package、worker 隔离与 Wasm 构建是要分别查明的运行方式。[项目定位](https://raw.githubusercontent.com/pydantic/monty/main/README.md)。

## Wasm runtime：Wasmtime、Wasmer、WasmEdge 各有自己的上层生态

### Wasmtime：执行引擎与明确的安全合同

[Wasmtime](https://github.com/bytecodealliance/wasmtime)提供 WebAssembly 运行与嵌入能力。Core 模型的外部功能来自链接的 imports；WASI 与宿主配置决定可获得的 I/O。任务只需确定性转换或窄工具接口时，可以研究如何减少授予的能力，而不是先建设 Linux image 池。[安全模型](https://docs.wasmtime.dev/security.html)。

还要分清源码／Wasm 与编译后缓存。序列化的编译产物不能因为扩展名像 Wasm 就当成未可信输入随意反序列化；应按运行时 API 的信任合同、版本与平台要求处理。**工程建议**：模板、编译缓存、模块签名与任务文件各有自己的来源校验，不混成一个“文件上传”入口。[序列化说明](https://docs.wasmtime.dev/examples-serialize.html)。

### Wasmer：runtime 与 Sandbox SDK 分开读

[Wasmer](https://github.com/wasmerio/wasmer)当前材料除 runtime 外，也指向独立 [wasmer-sdk](https://github.com/wasmerio/wasmer-sdk)。它提供在受控环境运行语言包的方式，并以 volume、network 等授权入口连接宿主。软件语言、WASIX／WASI、package 与原生二进制的兼容合同不是一回事。[README](https://raw.githubusercontent.com/wasmerio/wasmer/main/README.md)。

不能因为示例能启动 Python／Bash，就直接得出“任意 Linux OCI image 无改动可执行”。应检查包格式、宿主能力、线程／网络、平台绑定与当前 SDK 的发行方式；runtime 开源也不等于某个托管平台的控制面与 SLA 都开源。

### WasmEdge：可扩展 runtime 不只用于 Agent 代码执行

[WasmEdge](https://github.com/WasmEdge/WasmEdge)支持 Wasm、嵌入接口及扩展生态；README 中 LlamaEdge、模型推理、edge／microservices 属于不同使用方向。运行模型和隔离由模型生成的任意工具代码，是两种不同需求。[README](https://raw.githubusercontent.com/WasmEdge/WasmEdge/master/README.md)。

**工程建议**：评估扩展时，把文件、网络、数据库、GPU／模型推理插件等逐项列为 capability。Wasm 的语言边界不自动证明所有 native host extensions 的接口安全，也不替平台完成 GPU 租户隔离。

## Extism、Spin、Wassette：从执行引擎走到可调用工具

| 项目 | 解决的主要问题 | Agent 场景的审查点 |
| --- | --- | --- |
| [Extism](https://github.com/extism/extism) | Wasm 插件、PDK、Host SDK 与宿主函数 | 哪些函数被注入，能读写哪个业务资源，如何取消和限制输出 |
| [Spin](https://github.com/spinframework/spin) | Wasm 应用／组件、触发器与微服务框架 | HTTP、存储与出站能力是否适合工具服务，而不是整台机器 |
| [Wassette](https://github.com/microsoft/wassette) | 把 Wasm Component exports 转成 MCP tools | 组件加载、权限、供应链、server 身份与工具参数 |

依据：[Extism Host Functions](https://extism.org/docs/concepts/host-functions/)、[Spin README](https://raw.githubusercontent.com/spinframework/spin/main/README.md)、[Wassette concepts](https://raw.githubusercontent.com/microsoft/wassette/main/docs/concepts.md)。

Extism 的 host function 是宿主注入、插件可以回调的能力。宿主函数访问数据库或业务服务时，原来的权限并没有因为经过 Wasm 就消失；参数、资源范围和多线程使用仍需宿主负责。[Host Functions](https://extism.org/docs/concepts/host-functions/)。

Wassette 的公开定位是 MCP 与 Wasm Components 的桥接，建立在 Wasmtime 上；README 明确提醒仍处于早期开发、尚未生产就绪。因此可以作为工具组件路线研究，但不把加载演示或“browser-grade”宣传当作生产认证。旧概念页与当前 release 对协议、prompts／resources 等描述可能不同，按固定版本和当前实现核对，不把一份旧页面变成所有版本的保证。[README](https://raw.githubusercontent.com/microsoft/wassette/main/README.md)、[concepts](https://raw.githubusercontent.com/microsoft/wassette/main/docs/concepts.md)。

## 选型练习：同样叫工具执行，三条路线

以下是原创建议：

1. **数据整理工具**：少量结构化输入、受控查询，先评估 Monty 或 Wasm／Extism。重点是 capability、host callback、输出和超时。
2. **陌生仓库构建**：需要 shell、包管理器、native 工具，评估 BoxLite／microsandbox 或[开源平台](12-open-platform-projects.md)。重点是宿主前提、实际安全模式、出口、挂载和清理。
3. **对外 MCP 工具服务**：若功能可以成为 Wasm Component，研究 Wassette 或其他受控插件服务；需要通用 Linux 时再引入机器执行层。MCP 是入口协议，不是 VM 的同义词。

不存在一条“越嵌入越安全”或“名字含 microVM 就更适合”的规律。为兼容性开放宿主函数、目录、设备或网络，都可能改变最初接受的边界。每条路线先写硬门槛，再测实际任务。

## 自测与答案

1. BoxLite 使用 gvproxy，等于把程序交给 gVisor Sentry 吗？**不等于。** 网络栈与 syscall 应用内核是不同用途。
2. 解释器内的代码调用宿主数据库函数，是否无需租户检查？**仍需检查。** 能力被授予不等于任意参数获准。
3. Wasm runtime、Extism、Wassette 能相互无条件替换吗？**不能。** 执行引擎、插件框架和 MCP 组件服务处在不同层。

<!-- community-sources:start -->
## 本章一手来源与核验范围

| 来源 | 本章使用范围 |
| --- | --- |
| [BoxLite repo](https://github.com/boxlite-ai/boxlite)、[README](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/README.md) | 交付模式、接口、平台条件；不采用性能／安全排名 |
| [BoxLite security](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/docs/concepts/security.md)、[networking](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/docs/concepts/networking.md)、[storage](https://raw.githubusercontent.com/boxlite-ai/boxlite/main/docs/concepts/storage.md) | shim、配置、网络库、挂载与磁盘状态 |
| [microsandbox repo](https://github.com/superradcompany/microsandbox)、[README](https://raw.githubusercontent.com/superradcompany/microsandbox/main/README.md) | 当前 owner、平台与 beta、SDK／CLI／状态能力及计时脚注 |
| [sandbox-runtime repo](https://github.com/anthropics/sandbox-runtime)、[README](https://raw.githubusercontent.com/anthropics/sandbox-runtime/main/README.md) | OS primitives、代理与研究预览／兼容限制 |
| [Monty repo](https://github.com/pydantic/monty)、[README](https://raw.githubusercontent.com/pydantic/monty/main/README.md)、[security](https://pydantic.dev/docs/monty/concepts/security/) | 交付范围、受限语言与宿主能力；不外推历史 benchmark |
| [Wasmtime repo](https://github.com/bytecodealliance/wasmtime)、[security](https://docs.wasmtime.dev/security.html)、[serialization](https://docs.wasmtime.dev/examples-serialize.html) | Wasm 接口与编译缓存合同 |
| [Wasmer repo](https://github.com/wasmerio/wasmer)、[README](https://raw.githubusercontent.com/wasmerio/wasmer/main/README.md)、[SDK repo](https://github.com/wasmerio/wasmer-sdk) | runtime／SDK 分工、语言包和宿主授权 |
| [WasmEdge repo](https://github.com/WasmEdge/WasmEdge)、[README](https://raw.githubusercontent.com/WasmEdge/WasmEdge/master/README.md) | runtime、嵌入及扩展路线 |
| [Extism repo](https://github.com/extism/extism)、[Host Functions](https://extism.org/docs/concepts/host-functions/) | 插件与宿主函数 |
| [Spin repo](https://github.com/spinframework/spin)、[README](https://raw.githubusercontent.com/spinframework/spin/main/README.md) | 应用框架，不是完整 Linux guest |
| [Wassette repo](https://github.com/microsoft/wassette)、[README](https://raw.githubusercontent.com/microsoft/wassette/main/README.md)、[concepts](https://raw.githubusercontent.com/microsoft/wassette/main/docs/concepts.md) | MCP Component 桥接、早期开发与版本边界 |

<!-- community-sources:end -->

许可证／仓库归档状态另见[社区来源台账](community-sources.md)。本章是公开源码与文档阅读；没有执行 SDK 示例、安装上述软件、启用 shell／浏览器、部署云环境或完成跨平台验收。

[专题导读](README.md) · [社区项目总地图](11-community-project-map.md) · [上一章：microVM 工具链](13-microvm-toolchain.md) · [社区来源](community-sources.md)
