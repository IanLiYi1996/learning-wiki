# 11 社区公开项目地图：从 E2B、Firecracker 找到整个工具链

核验日期：2026-11-04。本章把原来分散在机制与商用平台中的项目，改为可直接查找的社区目录。它同时收录平台、执行引擎、适配器、SDK、开发工具与历史参考，**不是把所有条目都叫作端到端沙箱产品**。

原第 04 章讲过 Firecracker，第 07 章讲过 E2B；这里只按名字查找还不够。需要解释它们分别提供什么、与哪些社区组件配合，以及哪一部分可自建。新增 [12 开源平台](12-open-platform-projects.md)、[13 microVM 工具链](13-microvm-toolchain.md)、[14 嵌入式与 Wasm](14-embedded-and-wasm-projects.md)深入展开；许可证与维护证据见[社区来源台账](community-sources.md)。

## 你点名的两个项目，先放在正确的位置

<a id="community-e2b"></a>

### E2B：平台接口，不只是某个云服务名

[E2B SDK](https://github.com/e2b-dev/E2B)给 Agent 提供环境创建、命令、文件和连接接口；[E2B runtime](https://github.com/e2b-dev/runtime)则公开控制面、节点侧编排、guest agent 和路由等实现。SDK 调用与运营整套执行基础设施是两件事。SDK 开源不独立证明后台全部可自托管；这里正因为 runtime 有公开实现，才沿其明确边界讨论自建。[官方 runtime](https://github.com/e2b-dev/runtime)。

阅读顺序：先理解任务 API，再看创建请求如何被放置、宿主如何管理 VM、guest 的执行代理做什么，最后核对网络、凭证与暂停数据。不要以“三行 SDK 能运行代码”估算自托管工作量。具体源码入口和开放范围见[第 12 章](12-open-platform-projects.md)。

<a id="community-firecracker"></a>

### Firecracker：VMM，不是 E2B 的同层替代品

[Firecracker](https://github.com/firecracker-microvm/firecracker)提供精简虚拟设备与 KVM microVM 的执行机制；[Go SDK](https://github.com/firecracker-microvm/firecracker-go-sdk)包装管理调用，[firecracker-containerd](https://github.com/firecracker-microvm/firecracker-containerd)接入容器生命周期，[firectl](https://github.com/firecracker-microvm/firectl)提供 VM 启动工具。它们各补不同一层，不等于每个都实现完整的租户平台。

因此，“用 E2B 还是用 Firecracker”往往应拆成“使用现成平台接口，还是自己运营 VMM、调度与政策”。也可能在同一系统里同时使用它们。guest、jailer、TAP、磁盘、快照与执行代理的关系见[第 13 章](13-microvm-toolchain.md)，隔离原理见[第 04 章](04-microvm-and-kata.md)。

## 六层目录：先选需要替换的那一层

下表是原创阅读分类，不是所有项目必须遵循的部署拓扑。

| 层 | 主要问题 | 代表项目 | 不包含的默认承诺 |
| --- | --- | --- | --- |
| 平台／控制与政策 | 创建、连接、授权、回收工作空间 | E2B runtime、OpenSandbox、OpenShell | 不从 API 名称推出特定 kernel 边界 |
| 编排／执行服务 | 节点放置、环境接口、代码服务与工作空间 | Agent Sandbox、SandboxFusion、AIO、Incus | 不把 controller、tool image 当作 VMM |
| VM／OCI 运行机制 | guest、设备、Linux ABI 与进程边界 | Firecracker、Kata、gVisor、QEMU、libkrun | 不负责所有业务权限与数据出口 |
| SDK／适配器／管理工具 | 接某运行时到现有流程 | Go SDK、containerd adapter、krunvm、Flintlock | 不自动得到完整 Agent SaaS |
| 嵌入式／语言工具 | 给应用内部代码窄能力或一台本地机器 | BoxLite、microsandbox、Monty、Wasm 项目 | 不把语言接口等同通用 Linux |
| Agent／评测集成 | 工具协议、episode、执行、评分与轨迹 | OpenHands SDK、SWE-ReX、Harbor、Inspect | provider 能力仍需向底层追溯 |

## A. 公开平台、编排与执行服务

本组条目的功能依据在相应官方仓库；当前归档／许可检测单列在[来源台账](community-sources.md)，不以项目品牌替代证据。

| 项目／仓库 | 交付角色与学习重点 | 必须区分的范围 |
| --- | --- | --- |
| [E2B SDK](https://github.com/e2b-dev/E2B) | Agent 到远端执行环境的客户端接口 | SDK 与实际运行后端 |
| [E2B runtime](https://github.com/e2b-dev/runtime) | 控制面、节点编排、执行代理和路由 | runtime 代码、Embed 制品与托管 Cloud |
| [OpenSandbox](https://github.com/opensandbox-group/OpenSandbox) | 沙箱协议、服务与运行后端的统一接口 | Docker／Kubernetes／VM 后端及已实现 vs 扩展计划 |
| [CubeSandbox](https://github.com/TencentCloud/CubeSandbox) | RustVMM／KVM 平台与 E2B-compatible 接口 | API 兼容不等于同一 VMM，也不自动覆盖所有 SDK 功能 |
| [Kubernetes Agent Sandbox](https://github.com/kubernetes-sigs/agent-sandbox) | CRD、controller、template、claim、warm pool | 编排对象与实际 RuntimeClass |
| [NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell) | 执行政策、可信 supervisor、网络与凭证能力 | 不同驱动、L7 模式与 guest 授权 |
| [SandboxFusion](https://github.com/bytedance/SandboxFusion) | 代码执行与评测服务 | 实际进程／jail／容器配置，不默认当作 microVM |
| [AIO Sandbox](https://github.com/agent-infra/sandbox) | browser、terminal、file、editor、notebook、MCP 工具环境 | 工具箱 image 与隔离基础设施 |
| [Daytona 历史仓库](https://github.com/daytonaio/daytona) | 理解旧实现与项目迁移 | 仓库已归档；不能作为当前托管服务完全开源的证明 |
| [Incus](https://github.com/lxc/incus) | 系统容器与 VM 的统一管理／REST 路线 | container 与 VM 实例类型；不是特定 Agent 协议 |

Incus 的官方定位是系统容器与 VM 管理器，可从单机到集群。把它列入是为了补足通用基础设施路线，不是声称它默认具有 E2B 的 Agent 工具 API。[README](https://raw.githubusercontent.com/lxc/incus/main/README.md)。

特别注意 AIO 的公开 quickstart：README 会为兼容性使用放宽 seccomp 的选项，并说明不设置 API key 时相关服务保持开放；示例绑定 loopback。不能把工具齐全的演示 image 不经分析部署到公网，或者把“browser 在一个叫 sandbox 的容器内”升级为 VM 级边界。[AIO README](https://raw.githubusercontent.com/agent-infra/sandbox/main/README.md)。

## B. microVM、VMM 与 VM 工具链

| 项目／仓库 | 交付角色 | 应沿着什么阅读 |
| --- | --- | --- |
| [Firecracker](https://github.com/firecracker-microvm/firecracker) | KVM microVM VMM | API、设备、jailer、guest 与 snapshot |
| [firecracker-go-sdk](https://github.com/firecracker-microvm/firecracker-go-sdk) | Go 管理接口 | SDK 能包装什么，仍需谁配置宿主 |
| [firecracker-containerd](https://github.com/firecracker-microvm/firecracker-containerd) | OCI／containerd 接 microVM | shim、guest agent、容器与 VM 粒度 |
| [firectl](https://github.com/firecracker-microvm/firectl) | 启动／控制 CLI | guest artifacts、Firecracker 版本与宿主约束 |
| [Flintlock](https://github.com/liquidmetal-dev/flintlock) | microVM 管理与基础设施 API | 管理面、网络、存储与底层依赖 |
| [Ignite](https://github.com/weaveworks/ignite) | 历史容器式 VM 工作流 | 已归档，保留设计参考，不默认推荐新部署 |
| [Hocus](https://github.com/hocus-dev/hocus) | 历史开发环境与预构建工作流 | 已归档；初期与最后使用的 VMM 不应混写 |
| [Project-Capsule](https://github.com/Project-Capsule/capsule) | 单机 Linux 系统／容器／microVM 管理集成 | 实验边界及加固待办，不能推成生产承诺 |
| [Cloud Hypervisor](https://github.com/cloud-hypervisor/cloud-hypervisor) | 云工作负载 VMM | 设备、共享文件、存储、迁移与后端 |
| [QEMU](https://github.com/qemu/qemu) | 通用虚拟化／模拟器 | accelerator、machine type、backend 安全合同 |
| [crosvm](https://github.com/google/crosvm) | 隔离设备进程的 VMM | minijail、设备 policy、平台抽象 |
| [libkrun](https://github.com/libkrun/libkrun) | 可嵌入 VMM 的库接口 | OS backend、共享资源、稳定分支 |
| [krunvm](https://github.com/libkrun/krunvm) | libkrun 上层 VM 管理 CLI | image 与生命周期，不当成另一套 hypervisor |
| [rust-vmm vmm-reference](https://github.com/rust-vmm/vmm-reference) | 历史参考实现 | 已归档；组织下各 crate 有各自状态 |
| [rust-vmm community](https://github.com/rust-vmm/community) | 公共 VMM 组件生态入口 | 各 crate 的版本、许可与测试分别核对 |
| [RunD 作者 artifact](https://github.com/chengjiagan/RunD_ATC22) | 历史实验脚本与数据 | 已归档，不等于完整公开的 RunD 运行时 |

具体开源许可、归档证据与源码路径在[第 13 章](13-microvm-toolchain.md)。rust-vmm 是组件生态，单个参考仓库归档不能外推为全部 rust-vmm 项目停止，也不应反过来用整个生态活跃证明参考实现仍受维护。

## C. Linux／OCI 与进程约束项目

| 项目／仓库 | 角色 | 不要混成同一机制 |
| --- | --- | --- |
| [Kata Containers](https://github.com/kata-containers/kata-containers) | OCI／CRI 工作流中的 VM runtime | Pod VM 与 guest 内多个 container |
| [gVisor](https://github.com/google/gvisor) | Sentry 应用内核、runsc | 应用内核与网络库，不是一个用途 |
| [runc](https://github.com/opencontainers/runc) | Go 实现的 Linux OCI runtime | 普通 OCI 执行不自动获得 guest kernel |
| [crun](https://github.com/containers/crun) | C 实现的 OCI runtime／库路线 | 实现语言、性能与隔离合同不同问题 |
| [youki](https://github.com/youki-dev/youki) | Rust 实现的 OCI runtime | 内存安全语言不代替 namespace／policy 配置 |
| [containerd](https://github.com/containerd/containerd) | image 与容器生命周期服务 | daemon、shim、选用 runtime 三层 |
| [Podman](https://github.com/podman-container-tools/podman) | OCI container／pod／image 管理 | rootless、Podman machine 与每任务隔离 |
| [nsjail](https://github.com/google/nsjail) | namespace、资源与 syscall 约束工具 | 调用方决定政策，不是沙箱云 |
| [bubblewrap](https://github.com/containers/bubblewrap) | 低层环境构造／namespace 包装 | 调用参数定义边界，不自带完整租户政策 |
| [Minijail](https://github.com/google/minijail) | 进程降权与 sandbox 辅助库／工具 | 宿主进程约束，不是 guest OS |
| [Anthropic sandbox-runtime](https://github.com/anthropics/sandbox-runtime) | OS primitives 与出口代理的政策包装 | 研究预览、平台条件与兼容例外 |

角色依据：[runc](https://raw.githubusercontent.com/opencontainers/runc/main/README.md)、[crun](https://raw.githubusercontent.com/containers/crun/main/README.md)、[containerd](https://raw.githubusercontent.com/containerd/containerd/main/README.md)、[Podman](https://raw.githubusercontent.com/podman-container-tools/podman/main/README.md)及项目 README。Kata／gVisor 的边界见原[第 03](03-gvisor.md)、[第 04](04-microvm-and-kata.md)章；轻量工具见[第 02](02-linux-and-containers.md)与[第 14](14-embedded-and-wasm-projects.md)章。

Podman 在 macOS／Windows 上可以通过它管理的 Linux VM 运行容器，但这不表示该 VM 内每个容器都成为独立 microVM。containerd 自身也不决定你最终选择 runc、Kata 或其他 runtime。**工程建议**：从管理 API 一直追到实际执行 handler，不只停在产品名称。

## D. 嵌入式 VM、解释器与 Wasm 生态

| 项目／仓库 | 角色 | 优先检查 |
| --- | --- | --- |
| [BoxLite](https://github.com/boxlite-ai/boxlite) | 可嵌入的 microVM／机器执行库与相关服务接口 | 平台、KVM／HVF、有效 security／network 配置 |
| [microsandbox](https://github.com/superradcompany/microsandbox) | 本地、可程序化 microVM 工作流 | beta、OS backend、image、fork／snapshot 与回收 |
| [Pydantic Monty](https://github.com/pydantic/monty) | 受限 Python 解释器与宿主能力接口 | 语言限制、host callbacks、worker 与商业服务范围 |
| [Wasmtime](https://github.com/bytecodealliance/wasmtime) | Wasm／component 执行与嵌入 | imports、WASI、预算与编译产物信任 |
| [Wasmer](https://github.com/wasmerio/wasmer) | Wasm runtime 与相关 package／SDK 生态 | runtime、SDK、语言包和托管服务分开 |
| [Wasmer SDK](https://github.com/wasmerio/wasmer-sdk) | 应用到语言包／沙箱接口 | 实际发行方式、平台与授予的宿主能力 |
| [WasmEdge](https://github.com/WasmEdge/WasmEdge) | 可扩展 Wasm runtime | native plugins、模型／设备与能力授予 |
| [Extism](https://github.com/extism/extism) | Wasm 插件框架、PDK 与 Host SDK | 插件反调宿主函数的权限 |
| [Spin](https://github.com/spinframework/spin) | Wasm 应用／微服务框架 | triggers、组件、网络与存储 |
| [Wassette](https://github.com/microsoft/wassette) | Wasm Components 到 MCP tools 的运行层 | 早期开发、组件加载与政策 |

逐个项目的源码阅读与技术取舍见[第 14 章](14-embedded-and-wasm-projects.md)。该组不是“microVM 的九个替代实现”：其中只有部分提供完整机器环境，其他项目处理语言执行、插件与服务接口。

## E. Agent 与评测的执行接口：谁在消费 sandbox

| 项目／仓库 | 与沙箱的连接点 | 不能误写为 |
| --- | --- | --- |
| [OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk) | workspace／Agent Server／远端 API | SDK 的远端接口自带某个固定 VMM |
| [SWE-ReX](https://github.com/SWE-agent/SWE-ReX) | shell session 与执行后端的统一接口 | 所有 backend 具有相同隔离等级 |
| [Harbor](https://github.com/harbor-framework/harbor) | benchmark、environment、Agent 与 rollout 管理 | 新造了一套 hypervisor |
| [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) | sandbox provider、exec、文件与 per-sample 生命周期 | 评分器与候选代码天然没有共享风险 |
| [Inspect K8s Sandbox](https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox) | Inspect 的 Kubernetes provider | 集群 Pod 默认就是独立 VM |
| [AgentScope Runtime（迁移中）](https://github.com/agentscope-ai/agentscope-runtime) | 历史 sandbox／Agent-as-a-Service 集成 | `archived=false` 就表示仍推荐沿旧库开发 |
| [AgentScope（迁移目标）](https://github.com/agentscope-ai/agentscope) | 原 Runtime 公告指向的 AgentScope 2.0 项目 | 当前安装版本与实际 sandbox backend 仍须查新文档 |

OpenHands 官方区分 local workspace、Docker Agent Server 与 API-based remote workspace；SWE-ReX 把本地／远端 shell backend 抽象出来；Harbor 本地 Docker 和云 provider 是环境选择；Inspect 支持 provider 扩展、每样本设置与清理。[OpenHands](https://docs.openhands.dev/sdk/guides/agent-server/overview)、[SWE-ReX](https://raw.githubusercontent.com/SWE-agent/SWE-ReX/main/README.md)、[Harbor](https://raw.githubusercontent.com/harbor-framework/harbor/main/README.md)、[Inspect](https://inspect.aisi.org.uk/sandboxing.html)。

**原创评测检查建议**：记录究竟哪个 backend 执行了 episode、谁能访问测试与答案、评分器是否独立、并行样本是否共享目录／身份、失败时是否清理。框架把 provider 包装成统一接口，是可迁移性收益，不是统一安全证明。

AgentScope Runtime README 已明确提示能力并入 AgentScope 2.0，并要求迁移；研究日 GitHub API 的 `archived` 字段仍是 false。两项证据共同说明：维护判断不能只有一个布尔字段。[迁移声明](https://raw.githubusercontent.com/agentscope-ai/agentscope-runtime/main/README.md)。

## 不把“公开仓库”统一翻译成“全部开源”

至少分五种范围：

1. **完整自托管核心**：能找到控制／执行实现，仍须查部署制品与外部依赖。
2. **底层引擎**：执行机制公开，上层租户平台需要另做。
3. **SDK／协议与 image**：客户端或工具环境公开，后台可能仍是服务。
4. **实验／示例集成**：证明有一种连接办法，不证明一般性生产支持。
5. **历史代码**：已归档、迁移或参考实现，保留学习价值，不自动构成维护承诺。

这些分类是阅读框架，具体项目必须逐仓库判断。既有 Modal、Cloudflare、Vercel、Fly 和 AWS 对照继续留在[第 07 章](07-platform-landscape.md)；本章不因为某家发布 SDK 就宣称其内部控制面全部开源。

## 维护与许可快照：哪些字段能说到哪一步

[机器可读仓库表](community-repositories.json)保存研究日 54 个明确仓库节点的 GitHub API `archived` 与 SPDX 检测结果；一组产品可能包含多个节点，这不是“54 个互相竞争的沙箱云”。[来源台账](community-sources.md)列出这些 API 与实际文档的核验范围。

- `archived=true` 是归档证据；`false` 不是生产就绪、持续响应或 SLA 的证据。
- `license_detected` 是 GitHub 的检测值；`null`／`NOASSERTION` 不表示没有许可。多个组件、库／程序、例外条款要查各自 LICENSE／COPYING。
- 不使用 star 排名、一次 `pushed_at` 或 README 的 fastest／secure 字样推定质量。
- 未找到的项目、歧义名称和不可访问仓库不补猜 owner 或默认实现；在来源页明确留作未核实项。

## 三条可执行的阅读路线

**想自建 Agent 沙箱平台**：12 的 E2B／OpenSandbox → 06 的生命周期 → 09 的网络身份 → 10 的生产验收。先确认自己是要平台 API，还是要自己维护全套节点工程。

**想研究 Firecracker 社区工具链**：13 → 04 的边界 → 06 的快照。比较 SDK、OCI adapter 与管理器各补哪一层，再查维护与 host requirements。

**想给本地 Agent／工具加隔离**：14 的 BoxLite／microsandbox／srt／Monty／Wasm → 08 的硬门槛 → 09 的宿主能力。不需要 Linux 的工具，未必应先建设 microVM 集群。

## 自测与答案

1. E2B SDK、Firecracker、Harbor 能组成同一个部署吗？**可以讨论这样的分层组合，但须核对实际接口／backend。** 它们不是同层的竞争品。
2. 社区 image 包含 terminal／browser，是否证明 guest kernel 独立？**不证明。** 要继续追到运行时。
3. 仓库未归档，能否省略 README 中的迁移声明？**不能。** 维护状态应结合公告与版本。

[专题导读](README.md) · [下一章：开源平台](12-open-platform-projects.md) · [microVM 工具链](13-microvm-toolchain.md) · [嵌入式与 Wasm](14-embedded-and-wasm-projects.md) · [社区来源台账](community-sources.md)
