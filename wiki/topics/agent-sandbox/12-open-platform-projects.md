# 12 开源平台与执行服务：E2B、OpenSandbox、CubeSandbox 及上下游

核验日期：2026-11-04。本文按公开实现、接口和部署责任梳理社区项目，而非重新排列托管产品榜单。引用来自官方仓库、文档与许可文件；没有安装项目、执行示例、创建沙箱、复测性能或完成生产安全审计。

## 先确认开源的是哪一部分

| 项目 | 已公开的核心对象 | 要继续核验的范围 |
| --- | --- | --- |
| E2B | SDK／CLI、runtime、guest agent、模板及 Embed 部署材料 | 具体发行制品、部署模式、全部功能与外部服务 |
| OpenSandbox | 生命周期／执行协议、SDK、server、components、Kubernetes 集成 | 实际 runtime、资源与出口配置、协议扩展成熟度 |
| CubeSandbox | 控制面、节点、shim／hypervisor、网络与存储等实现 | 具体 SDK 兼容性、宿主前提、各模式有效政策 |
| Kubernetes Agent Sandbox | CRD、controller、模板、claim 与 warm pool | 节点安装的 RuntimeClass 和集群政策 |
| AIO Sandbox | 多工具环境、image、API／SDK 与示例 | 所用容器／VM 边界、公开端口、认证与浏览器状态 |
| SandboxFusion | 代码执行、语言 runner、测试／评测服务 | 实际执行方式、资源／文件约束、candidate 与 judge 边界 |
| Daytona 历史仓库 | 旧核心源码与历史版本 | 已停止维护；现行核心是否公开不能沿旧标签推断 |
| OpenShell | supervisor／gateway／政策与 provider 运行层 | 所选驱动、实际 enforcement、权限与数据范围 |

具体依据见各节及章末来源。**SDK／工具 image／控制面／运行时**不是同义词；开放其中一部分，不证明其他部分可按相同方式自建。

## E2B：客户端、控制面、节点与 guest 一起读

[E2B 主仓库](https://github.com/e2b-dev/E2B)提供 JavaScript／Python SDK 与 CLI 入口；[runtime 仓库](https://github.com/e2b-dev/runtime)公开后端。两个根许可文件均为 Apache-2.0，但这只描述明确仓库，不替依赖、镜像或托管服务做完整许可审计。[SDK LICENSE](https://raw.githubusercontent.com/e2b-dev/E2B/main/LICENSE)、[runtime LICENSE](https://raw.githubusercontent.com/e2b-dev/runtime/main/LICENSE)。

### 创建请求与执行流量走不同路径

官方架构把控制面与数据面分开：控制 API 决定 sandbox 放到哪个节点，节点 orchestrator 管理 Firecracker、网络和块设备；guest 内 `envd` 处理进程与文件等接口。模板构建与流量路由也属于 runtime 实现。[架构说明](https://raw.githubusercontent.com/e2b-dev/runtime/main/docs/ARCHITECTURE.md)。

原创阅读简图：

```text
SDK / CLI -> 控制 API -> 节点 orchestrator -> Firecracker -> guest / envd
                 |            |                             |
              状态与元数据   网络、块设备、恢复             用户进程 / 文件

用户流量 -> 路由 / proxy -> 目标节点 -> guest 服务
模板构建 -> kernel / rootfs / snapshot artifacts -> 节点恢复
```

图仅简化责任，不复刻全部内部组件。SDK 调用成功可能只说明控制请求被接受；guest ready、执行代理连接、目标端口、业务授权与结果导出是后续判断。把所有用户流量画成“经过控制 API”，会误解故障和扩容路径。

### 四个源码阅读入口

| 入口 | 阅读问题 |
| --- | --- |
| [E2B README](https://raw.githubusercontent.com/e2b-dev/E2B/main/README.md)与 SDK | 应用怎样创建、连接、执行、处理错误和结束任务？ |
| runtime `docs/ARCHITECTURE.md` → `packages/` | 控制、节点、guest、路由和构建分别由谁负责？ |
| runtime `firecracker/` 与相关宿主代码 | VMM／kernel／rootfs／存储和网络如何组装？ |
| `embed/` | 实际提供哪种单机安装、模板、存储与运维方式？ |

上述目录来自公开仓库，不表示本轮逐行审计所有 package。对每条路径，应继续读其配置、版本和错误处理，而不是只看总体图。

### Embed 的现行声明比旧发布范围更明确

本次读取的 [Embed README](https://raw.githubusercontent.com/e2b-dev/runtime/main/embed/README.md)明确声明在单机提供完整 E2B 栈与全部功能，提供 Docker Compose、多个云的 Terraform 和 Kubernetes 入口，并说明不要求 E2B 账户／license key。它和 2026-09-30 初次发布时较窄的功能描述是不同证据，不能把旧限制永久照搬到现在。

同时，这仍是**项目当前声明**，不是本轮已经审计每种发行制品或跑通全部功能。运营者要核对所选 tag／image、KVM、宿主能力、模板、日志、备份、磁盘与入口政策。即使部署脚本用 Docker，也不是把不可信工作负载改成普通共享 kernel 容器：宿主编排组件与 guest Firecracker 边界是两层。[runtime 定位](https://raw.githubusercontent.com/e2b-dev/runtime/main/README.md)。

原创审查建议：对“数据留在节点”的部署描述，分开检查 runtime 存储、遥测、模型端点、包下载、外部业务 API 与人工导出；它不独立证明 Agent 获准的网络请求不会传出数据。

## OpenSandbox：统一协议与可插拔运行后端

[OpenSandbox](https://github.com/opensandbox-group/OpenSandbox)是当前规范仓库；README 以 AAIF 项目定位，公开多语言 SDK、CLI／MCP、server、执行 components、协议与 Kubernetes 材料。根许可为 Apache-2.0。[README](https://raw.githubusercontent.com/opensandbox-group/OpenSandbox/main/README.md)、[LICENSE](https://raw.githubusercontent.com/opensandbox-group/OpenSandbox/main/LICENSE)。

### 协议层的价值，不是一个固定 kernel 模型

它把创建／销毁／生命周期与命令／文件／代码执行接口组织起来，本地示例用 Docker，集群路径用 Kubernetes。SDK 稳定的调用形状可以减少应用对底层环境的绑定，但**统一 API 不表示不同 runtime 的安全边界一致**。Docker、带应用内核的配置、VM-backed runtime 以及尚未确认的扩展，应分别记录。

源码可按 `specs/` → `sdks/` → `server/` → `components/` → `kubernetes/`阅读：先看公共协议，再追 API 请求如何进入后端及实际运行配置。examples 用于适配 coding、browser、desktop、evaluation 等任务，不是每个示例都已完成恶意多租户验收。[接口与目录](https://raw.githubusercontent.com/opensandbox-group/OpenSandbox/main/README.md)。

### 出站与凭证能力：配置模式需要进入测试合同

官方 Egress 文档描述与 sandbox 共享 network namespace 的 sidecar，区分默认 DNS 过滤与 `dns+nft` 的包层约束，提供域名／地址规则、平台 overlays、凭证注入和启动失败关闭。当前文档同时列出端口政策、DNS lease、连接与协议方面的限制。[Egress](https://raw.githubusercontent.com/opensandbox-group/OpenSandbox/main/docs/architecture/network/egress.md)。

因此，不能把“设置了域名规则”与“所有协议直连都被拦截”画等号。原创验收建议：记录实际 mode、platform floor、DNS 与 IPv6、已有连接、代理异常及凭证匹配；用户能够更改的政策与管理员不可覆盖底线分开。TLS interception 的可见性、信任 CA 和例外也需核验，不能从存在 Credential Vault 推出所有 secret 都不可被代码读取。

### 怎样与 E2B 比较

不要先按品牌判断。先问应用是否依赖某 SDK／协议、是否要自己运营节点、是否需要 Docker／Kubernetes 或 guest VM、是否要持久会话，以及出口／凭证合同是什么。E2B runtime 给出明确 Firecracker 后端；OpenSandbox 的协议与部署适配需要继续追到实际运行类型。二者的接口、状态语义和制作模板方式不应只用“都是 sandbox”概括。

## 腾讯 CubeSandbox：另一个可读的端到端 microVM 平台

规范仓库是 [TencentCloud/CubeSandbox](https://github.com/TencentCloud/CubeSandbox)，而不是未经确认的 `TencentCloud/agent-sandbox`。官方材料明确公开 RustVMM／KVM 后端、单节点与集群部署，以及 E2B-compatible 接口。[README](https://raw.githubusercontent.com/TencentCloud/CubeSandbox/master/README.md)。

其 [LICENSE](https://raw.githubusercontent.com/TencentCloud/CubeSandbox/master/LICENSE)先声明 Cube Sandbox 的 Apache-2.0，再列单独的第三方组件许可；GitHub API 本轮识别为 `NOASSERTION`。这是“检测值不足以概括全文”的例子，不是无许可证，更不能把 root 声明当成全部 kernel、库与 image 的唯一许可。

### 控制面、节点、网络与存储分别是什么

| 模块 | 官方架构中主要职责 | 需要继续验证 |
| --- | --- | --- |
| CubeAPI／CubeMaster | 对外协议、请求转换、调度、生命周期协调 | 用户／租户映射、准入、幂等与故障状态 |
| Cubelet／CubeShim／hypervisor | 节点资源、guest boot／restore 与执行通道 | 宿主前提、降权、设备、配额与回收 |
| CubeProxy | 请求路由与目标实例定位 | 入口认证、端口授权、重连和撤销 |
| CubeVS／CubeEgress | 网络路由／过滤与出站代理 | 协议、模式、实际不可绕过路径与例外 |
| CubeCoW 与相关存储 | rootfs／memory 及 snapshot／clone 的存储组织 | 文件系统条件、基线、完整性和保存范围 |
| Redis | 实例元数据与协调状态 | 高可用、一致性、身份和状态恢复 |

来源：[官方架构](https://raw.githubusercontent.com/TencentCloud/CubeSandbox/master/docs/architecture/overview.md)。本表是责任摘要，不采用其毫秒启动或内存开销作为本轮实测数据。

先沿 CubeAPI → CubeMaster → Cubelet → CubeShim → hypervisor 读创建路径，再从网络、存储与 guest agent 阅读实际执行／恢复。**它使用 RustVMM 组件与 KVM，不因此等同 Firecracker**。同一类底层组件可组成不同设备、控制面与生命周期实现。

官方总体图同时画了透明代理与 SNAT 等网络路径；实际过滤和凭证能力必须继续核对协议、配置与代码，不能仅以“all outbound”总述代替旁路测试。E2B-compatible 也应固定 SDK 版本、模板、错误、文件、端口与 pause／resume 的语义逐项测试，不解读成任何 E2B 功能都无条件 drop-in。

原创选型问题：宿主 KVM／kernel／存储条件是什么？单机与集群有哪些不同组件？控制面故障、暂停状态和跨节点恢复由谁接管？允许的业务身份怎样重新绑定？这些比一次 hello world 更能揭示运营工作量。

## Kubernetes Agent Sandbox：自建集群的编排积木

[SIG Apps 的 Agent Sandbox](https://github.com/kubernetes-sigs/agent-sandbox)是 orchestrator，不是新 VMM。官方 README 明确通过 Pod 的 `RuntimeClass`委托 gVisor／Kata 等 runtime，实现有状态、单实例和稳定身份的工作空间，并提供 template／claim／warm pool 等扩展。[README](https://raw.githubusercontent.com/kubernetes-sigs/agent-sandbox/main/README.md)。

阅读顺序：API／CRD → controller reconcile → examples／extensions → 节点 runtime 配置。学习重点是 desired state、分配、创建、状态反馈、回收与预热；不要把 controller 能管理 Pod，当成 runtime 已在所有节点安装和强制使用。

原创平台建议：用户不能任意选宽 runtime、宿主挂载与身份；RBAC、quota、Pod policy、CNI、storage 与 broker 都要在 controller 之外形成明确合同。与 Inspect 的 K8s provider、Kata 的 Pod VM、Cubelet 的节点 API 也不处在完全相同的对象层。

## AIO Sandbox 与 SandboxFusion：工具环境、执行服务不是 VMM

### AIO：把工具聚合到可操作的环境

[agent-infra/sandbox](https://github.com/agent-infra/sandbox)提供 browser、terminal、file、VSCode、Jupyter、MCP 等工具入口。它适合研究 computer-use、开发环境和统一 I/O，而非据名字推定独立 guest kernel。[README](https://raw.githubusercontent.com/agent-infra/sandbox/main/README.md)。

当前 README 的 Docker quickstart 放宽 seccomp；未配置 API key 时服务保持开放，示例有意绑定 host loopback。原创建议：先确认任务需要哪些工具，再审查其运行方式、浏览器自身约束、公开端口、auth 与 context 清理。若要放进 microVM／Kata，要分别验证该组合，不把工具 image 自带的兼容选项称作整个外层边界的保证。

它可以是沙箱中的“guest 工具环境”，也可以是自己受限部署的容器。前者的外层隔离由其他项目提供；后者接受何种 host／kernel 信任由你决定。不要在一个无法清理的 AIO 实例中混放不同用户的 Cookie、工作区或云身份。

### SandboxFusion：多语言 code runner 与 judge

[SandboxFusion](https://github.com/bytedance/SandboxFusion)公开多个语言 runner、代码运行结果与评测数据集实现，README 提供 Docker 与手工服务安装；服务默认绑定 loopback。当前公开目录包括 `sandbox/runners`、`sandbox/server`、`sandbox/datasets` 与配置。[README](https://raw.githubusercontent.com/bytedance/SandboxFusion/main/README.md)。

它解决的是“怎样安装语言工具、运行代码、提取结果、组织测试／评测”的一层。**不能从沙箱命名或支持 CUDA 就推定使用了 microVM、独立 GPU 边界或所有进程政策已启用**。应继续读具体 runner、配置、进程／文件与设备路径；本轮没有部署服务或证明某种默认 jail 的效果。

原创评测建议：candidate、测试与参考答案按权限分开；限制运行时间、进程、输出、临时文件与安装依赖；区分“编译成功”“运行成功”“测试成功”“评分可信”。评测协议、语言兼容与恶意代码隔离分别验收。

## Daytona：保留历史项目，不把旧源码包装成当前自建栈

[daytonaio/daytona](https://github.com/daytonaio/daytona)的 README 明确说 2026 年 6 月起核心开发移到私有代码库，旧仓库不再更新、修复或发布；保留旧代码以便按其指定历史 LICENSE 使用和 fork。研究日 API 也显示归档。[当前公告](https://raw.githubusercontent.com/daytonaio/daytona/main/README.md)。

README 指向的 `v0.190.0/LICENSE`为 AGPL v3；这只是明确历史版本的许可事实，不是所有 SDK／镜像／现行服务的统一许可，也不是法律或商用判断。[历史许可](https://raw.githubusercontent.com/daytonaio/daytona/v0.190.0/LICENSE)。

原[第 07 章](07-platform-landscape.md)仍用于阅读当前托管产品的 Container／VM class、SDK 版本与状态能力。这里要另外回答“现在公开的代码能否运营同一后台”。公开安装包／API 文档、旧 self-hosting 说明、组织里的 SDK 或示例，均不证明现行私有核心又自动开源。若选择旧 fork，自行承担依赖、补丁、支持与配置核验，不能向用户承诺原维护团队的持续支持。

## OpenShell：政策与可信中介接到执行环境

[NVIDIA OpenShell](https://github.com/NVIDIA/OpenShell)公开政策、gateway／supervisor 与 provider 运行层；README 指向 0.1.x 的新隔离与扩展 API。[README](https://raw.githubusercontent.com/NVIDIA/OpenShell/main/README.md)。

学习顺序是 policy schema → supervisor 的执行／网络边界 → gateway 的生命周期 → provider attachment 与实际驱动。它与单纯 SDK、VMM 或 CRD 不同，关心执行环境怎样使用文件、网络和真实凭证。详细版本、L7 enforce／audit、TLS 与推理路由变化在[第 09 章](09-network-identity-and-data.md)已有固定范围核验，这里不重新声称不同驱动具有同一 microVM 边界。

原创建议：把控制面、工作负载、proxy、credential broker 与业务 API 的权限画清楚；政策获准访问端点，不等于业务上可以执行该端点的一切动作。公开源码也不替你做部署的配置验收。

## 自建平台的最小闭环：项目可以减少多少工作

这是原创责任清单，不是说上述项目均已实现每一项：

1. 创建请求绑定可信用户／租户／任务，限制模板、runtime 和预算。
2. 节点获得适配的宿主、VMM／kernel／image 与存储／网络配置。
3. guest／执行服务 Ready 后，按任务授予窄业务能力。
4. 执行、超时、取消和重试遵循明确协议，外部副作用单独幂等。
5. 产物、日志、preview 和录制按数据政策导出。
6. 终止或暂停时撤销能力；分别管理 compute、snapshot、volume 与保留。
7. 核验版本、兼容、拒绝路径、恢复与成本，而非只保存成功演示。

选平台时逐项填“项目已提供”“需要配置”“团队补齐”“未知”。如果只有 SDK 客户端，控制和数据面仍是你的工作；如果得到公开整套平台，patch、容量、数据与授权也仍是运营责任。

## 自测与答案

1. CubeSandbox 的 E2B-compatible API 能证明使用 Firecracker 吗？**不能。** 公开架构描述的是另一条 RustVMM／KVM 实现。
2. OpenSandbox 或 Agent Sandbox 有统一创建接口，能证明默认独立 guest kernel 吗？**不能。** 必须继续查 backend 与有效 runtime。
3. Daytona 旧仓库仍可下载，能否据此称当前核心仍开源维护？**不能。** 公告、版本与 SDK／核心范围必须分别描述。

<!-- community-sources:start -->
## 本章一手来源小账本

| 项目／证据 | 精确来源与范围 |
| --- | --- |
| E2B SDK | [仓库](https://github.com/e2b-dev/E2B)、[README](https://raw.githubusercontent.com/e2b-dev/E2B/main/README.md)、[LICENSE](https://raw.githubusercontent.com/e2b-dev/E2B/main/LICENSE)：客户端与明确仓库许可 |
| E2B runtime | [仓库](https://github.com/e2b-dev/runtime)、[README](https://raw.githubusercontent.com/e2b-dev/runtime/main/README.md)、[架构](https://raw.githubusercontent.com/e2b-dev/runtime/main/docs/ARCHITECTURE.md)、[LICENSE](https://raw.githubusercontent.com/e2b-dev/runtime/main/LICENSE)：控制／数据／guest／构建与路由 |
| E2B Embed | [当前 README](https://raw.githubusercontent.com/e2b-dev/runtime/main/embed/README.md)：当前全部功能与安装范围声明，非制品审计或运行验证 |
| OpenSandbox | [仓库](https://github.com/opensandbox-group/OpenSandbox)、[README](https://raw.githubusercontent.com/opensandbox-group/OpenSandbox/main/README.md)、[LICENSE](https://raw.githubusercontent.com/opensandbox-group/OpenSandbox/main/LICENSE)、[Egress](https://raw.githubusercontent.com/opensandbox-group/OpenSandbox/main/docs/architecture/network/egress.md)：协议、backend、服务与配置 |
| CubeSandbox | [仓库](https://github.com/TencentCloud/CubeSandbox)、[README](https://raw.githubusercontent.com/TencentCloud/CubeSandbox/master/README.md)、[架构](https://raw.githubusercontent.com/TencentCloud/CubeSandbox/master/docs/architecture/overview.md)、[LICENSE](https://raw.githubusercontent.com/TencentCloud/CubeSandbox/master/LICENSE)：平台层次、SDK 兼容声明与第三方许可范围 |
| Agent Sandbox | [仓库](https://github.com/kubernetes-sigs/agent-sandbox)、[README](https://raw.githubusercontent.com/kubernetes-sigs/agent-sandbox/main/README.md)：orchestrator 与 RuntimeClass 委托 |
| AIO Sandbox | [仓库](https://github.com/agent-infra/sandbox)、[README](https://raw.githubusercontent.com/agent-infra/sandbox/main/README.md)：工具、默认 auth、seccomp 与端口示例 |
| SandboxFusion | [仓库](https://github.com/bytedance/SandboxFusion)、[README](https://raw.githubusercontent.com/bytedance/SandboxFusion/main/README.md)：runner、judge、部署和 loopback |
| Daytona 历史范围 | [仓库](https://github.com/daytonaio/daytona)、[当前弃用公告](https://raw.githubusercontent.com/daytonaio/daytona/main/README.md)、[v0.190.0 LICENSE](https://raw.githubusercontent.com/daytonaio/daytona/v0.190.0/LICENSE)：归档／私有核心公告与明确历史许可 |
| OpenShell | [仓库](https://github.com/NVIDIA/OpenShell)、[README](https://raw.githubusercontent.com/NVIDIA/OpenShell/main/README.md)：0.1.x 政策运行层；细节由第 09 章来源限定 |

<!-- community-sources:end -->

仓库 API 的归档与许可检测在[社区来源页](community-sources.md)，不能代替具体 component／release 的实际 LICENSE。所有简图、审查问题和责任清单为原创教学；本轮没有执行这些系统或承诺某份自建制品与托管服务完全等价。

[专题导读](README.md) · [社区项目总地图](11-community-project-map.md) · [下一章：microVM 工具链](13-microvm-toolchain.md) · [社区来源](community-sources.md)
