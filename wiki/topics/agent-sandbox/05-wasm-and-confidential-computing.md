# 05 Wasm 与机密计算：限制程序的能力，或限制宿主的可见性

资料核验：2026-11-04。这是两条不同技术轴：Wasm 缩窄工作负载的接口，机密计算改变宿主信任。它们不是容器到 microVM 之间的两个“等级”。

## Wasm 不是一台缩小的 Linux

WebAssembly 模块通过显式 imports 与外部交互，不天然拥有原始系统调用或任意 I/O。线性内存、类型化控制流、越界检查和外部接口由运行时实现。[Wasmtime 安全说明](https://docs.wasmtime.dev/security.html)。

原创例子：一个工具只需要接收字符串、提取日期并返回结构化记录。若编译为 Wasm，宿主可以不提供网络、磁盘或业务身份，只提供输入／输出函数。它的“环境”未必需要 shell、包管理器和完整文件系统。

另一个工具必须启动 Chrome、安装系统包和运行本机二进制：这不是把 OCI image 改个扩展名就能变成 Wasm。应评估重编译、语言运行时、原生扩展和接口适配成本，而不是只看启动宣传。

## 受控导入可以把边界做得很窄

教学模型：

| 给模块的接口 | 可以完成什么 | 宿主仍要检查 |
| --- | --- | --- |
| `read_input`／`write_result` | 纯计算工具 | 输入大小、输出结构和总量 |
| 指定目录的文件能力 | 处理任务文件 | 目录范围、链接、文件对象与配额 |
| 精确 HTTP 能力 | 联系少数服务 | 目标解析、重定向、数据分类和凭证 |
| 企业业务函数 | 读取或改变业务对象 | 租户、资源、动作、审批和幂等 |

WASI 文件系统采用能力式安全模型，访问限定在授予的文件和目录。这个模型的价值依赖宿主不把过宽的能力授予模块。[Wasmtime](https://docs.wasmtime.dev/security.html)。

**工程推论**：模块不能自己调用原始 syscall，不代表宿主导入的 `run_any_command` 函数安全。给它一条能执行任意宿主命令的 bridge，会把窄接口的价值重新扩宽。host functions、运行时／编译器、业务服务与参数检查都属于需要审查的链路。

## WASI 版本是兼容性合同，不要写“支持 WASI”就结束

官方仓库区分 Preview 1（witx）、WASI 0.2／Preview 2（WIT 与模块化 API）和当前预览 WASI 0.3／Preview 3（组件模型的原生异步）。它们不是完全相同的一套系统接口。[WASI 官方仓库](https://github.com/WebAssembly/WASI/blob/main/README.md)。

**工程建议**：记录目标版本、component／core module 形式、编译器、语言适配器、运行时版本和实际导入列表。不把“能跑一个 hello world”当成 Python native wheels、线程、socket 和浏览器的兼容性证明，也不把 preview 自动视为所有平台都已提供稳定支持。

JavaScript isolate 也不是 Wasm 的同义词。平台可在 isolate 中运行 JavaScript 并支持 Wasm，但其安全边界、API 和运行方式仍由平台实现决定；Cloudflare Workers 与 Cloudflare 的容器 Sandbox SDK 要分开读，见[平台章](07-platform-landscape.md)。

## 无限循环、内存与输出仍要预算

语言级内存隔离不等于对资源耗尽免疫。Wasmtime 的执行控制提供 fuel／epoch 等配置入口，需要宿主启用并协调；它们不能自动替所有 host I/O、网络等待和日志设置预算。[Wasmtime Config API](https://docs.wasmtime.dev/api/wasmtime/struct.Config.html)。

教学建议：

- 限制线性内存、table、实例数和最大栈；
- 为 guest 计算设燃料或中断预算，为整体任务设 wall-clock timeout；
- 为 host functions 设自己的超时、并发和取消协议；
- 限制 stdout／结果大小，检查输出格式后再进入后续工具；
- 不把原始终端输出或 HTML 直接当可信 UI。

Wasmtime 安全说明专门讨论终端控制序列；可见“代码未逃出语言 sandbox”与“输出不能影响操作者”不是同一个命题。[终端输出与安全](https://docs.wasmtime.dev/security.html)。

## 机密计算把信任方向反过来

普通 sandbox 的主要问题是“让 guest 少伤害 host／邻居”；机密计算还问“让不可信 host 少看到或改变 guest 内敏感内容”。Confidential Containers 主要采用 VM enclaves，把宿主内核、kubelet、CRI runtime、Kata shim 以及 Kubernetes 控制面放在不可信域之外。[信任模型](https://confidentialcontainers.org/docs/architecture/trust-model/trust-model/)。

具体 TEE 能力与完整性保障随硬件平台和代际变化，不应把 SEV、SEV-ES、SEV-SNP、TDX 等名字混成等价保证。平台支持、测量对象与密钥策略必须分别查。

## Attestation 与密钥释放的教学链路

典型的原创分解：

1. guest 启动时形成硬件支持的环境测量与证明。
2. 外部可信验证者检查证明、新鲜度、平台状态和获准测量。
3. 策略判断是否为这份软件、任务与身份释放特定秘密。
4. 秘密经保护通路送入被批准的环境。
5. 应用仍按业务授权限制使用，输出仍经过数据政策。

Confidential Containers 文档说明受测量的四类 guest 构件是固件、kernel、kernel command line 与 rootfs；工作负载容器通常由以第一阶段信任为根的第二阶段测量／OCI 签名等覆盖，而不是每一层都由硬件直接测量。它依赖外部可信实体（通常是 Trustee）验证 guest。[信任模型](https://confidentialcontainers.org/docs/architecture/trust-model/trust-model/)。

**工程推论**：“证明来自某个 TEE”不自动证明镜像属于正确租户，也不自动证明程序没有恶意。验证政策若允许错误测量，仍会把秘密交错；应用若把秘密发给获准出口，内存加密也不替它做业务判断。

## 它没有保证可用性与任意接口安全

Confidential Containers 的信任模型明确把硬件侧信道和拒绝服务列为不覆盖项；不可信宿主可以不调度 guest。通过跨边界 API 附加设备、挂载磁盘或向应用发请求，也仍需检查和 guest 内政策。[官方模型](https://confidentialcontainers.org/docs/architecture/trust-model/trust-model/)。

因此，本专题不把机密计算列为“最安全、所以什么场景都选它”。它增加的是特定信任假设下的能力与工程要求：支持硬件、证明服务、软件测量、密钥发布、故障诊断和升级策略。

## 两条路线怎样与容器／VM 组合

| 架构组合 | 可讨论的价值 | 不能据此省略 |
| --- | --- | --- |
| Wasm + 受控 host API | 固定工具、插件、短计算任务的窄能力边界 | host functions 授权与资源预算 |
| Wasm + 进程／容器隔离 | 运行时之外增加 OS 层防护 | 跨层配置、取消与输出验收 |
| microVM + 受控网络／broker | 一般 Linux 工作负载与独立 guest 边界 | 镜像、凭证、控制面与清理 |
| confidential VM + broker | 宿主不可信时保护特定 guest 数据 | 证明政策、guest 应用与业务授权 |

表中是原创设计方向，不是已部署方案，也不说明某厂商支持每种组合。

## 自测与答案

1. Wasm 能否仅靠显式导入就执行所有现成 Linux 二进制？**不能这样推断。** 二进制和接口适配不同。
2. fuel 是否给任意阻塞 host function 设置了完整超时？**不能这样推断。** guest 计算与 host I/O 要分别限制。
3. attestation 是否证明代码处理用户数据的目的正当？**不证明。** 环境测量、软件信任和业务授权是不同判断。

[专题导读](README.md) · [上一章：microVM 与 Kata](04-microvm-and-kata.md) · [下一章：生命周期与编排](06-lifecycle-and-orchestration.md)
