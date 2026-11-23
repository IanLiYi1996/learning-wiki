# 社区扩展来源台账：仓库、许可、归档与开放范围

核验日期：2026-11-04。范围：新增第 11–14 章的社区项目研究。原十章的机制与平台来源仍在[基础来源页](sources.md)；本页不把研究日期升级为生产验证日期，也不宣称穷举了全部社区。

## 三层来源，避免重复一大份链接清单

1. 本页保存社区目录的公共来源、54 个仓库的 GitHub API 证据，以及分层的核验边界。
2. [开源平台章](12-open-platform-projects.md)、[microVM 工具链章](13-microvm-toolchain.md)、[嵌入式与 Wasm 章](14-embedded-and-wasm-projects.md)的章末小账本重列各章用到的全部精确 URL，包含源码、LICENSE、接口与限制。它们是本页链接到的子账本，不只是一句“来源 GitHub”。
3. [机器可读表](community-repositories.json)保存明确仓库节点、阅读分层、API `archived` 与 `license_detected` 的快照；它没有保存 star 排名，也不替代上述正文证据。

文档测试会合并基础来源、本页和明确标记的三个子账本，检查正文外部引用均有记录；不会把任意正文 URL 当成已经完成来源核验的账本。

## 官方 API 快照：看见了什么，不是什么保证

研究时读取官方 Repository API。表中的许可栏是 GitHub 的 SPDX 检测结果：空值与 `NOASSERTION` 不表示没有许可证。Cloud Hypervisor 的 AND、rust-vmm crate 的 OR、QEMU 组件与 crun 程序／库应继续阅读实际许可文本；不得从该字段直接给出法律或商业使用结论。

“未归档”只描述字段值，不说明生产就绪、有人响应 issue、所有当前功能都受支持或未来 SLA。Daytona、Ignite、Hocus、vmm-reference 与 RunD artifact 的归档状态有明确证据；AgentScope Runtime 的 README 则提示迁移，即使 API 当时未归档，也不据此推荐继续沿旧库开发。

| 仓库／公开范围入口 | `archived` | API 许可检测 | 官方状态来源 |
| --- | --- | --- | --- |
| [E2B SDK](https://github.com/e2b-dev/E2B) | false | Apache-2.0 | [API](https://api.github.com/repos/e2b-dev/E2B) |
| [E2B runtime](https://github.com/e2b-dev/runtime) | false | Apache-2.0 | [API](https://api.github.com/repos/e2b-dev/runtime) |
| [Daytona 历史仓库](https://github.com/daytonaio/daytona) | true | 未识别 | [API](https://api.github.com/repos/daytonaio/daytona) |
| [OpenSandbox](https://github.com/opensandbox-group/OpenSandbox) | false | Apache-2.0 | [API](https://api.github.com/repos/opensandbox-group/OpenSandbox) |
| [CubeSandbox](https://github.com/TencentCloud/CubeSandbox) | false | NOASSERTION | [API](https://api.github.com/repos/TencentCloud/CubeSandbox) |
| [SandboxFusion](https://github.com/bytedance/SandboxFusion) | false | Apache-2.0 | [API](https://api.github.com/repos/bytedance/SandboxFusion) |
| [Kubernetes Agent Sandbox](https://github.com/kubernetes-sigs/agent-sandbox) | false | Apache-2.0 | [API](https://api.github.com/repos/kubernetes-sigs/agent-sandbox) |
| [OpenShell](https://github.com/NVIDIA/OpenShell) | false | Apache-2.0 | [API](https://api.github.com/repos/NVIDIA/OpenShell) |
| [BoxLite](https://github.com/boxlite-ai/boxlite) | false | Apache-2.0 | [API](https://api.github.com/repos/boxlite-ai/boxlite) |
| [microsandbox](https://github.com/superradcompany/microsandbox) | false | Apache-2.0 | [API](https://api.github.com/repos/superradcompany/microsandbox) |
| [Firecracker](https://github.com/firecracker-microvm/firecracker) | false | Apache-2.0 | [API](https://api.github.com/repos/firecracker-microvm/firecracker) |
| [firecracker-go-sdk](https://github.com/firecracker-microvm/firecracker-go-sdk) | false | Apache-2.0 | [API](https://api.github.com/repos/firecracker-microvm/firecracker-go-sdk) |
| [firecracker-containerd](https://github.com/firecracker-microvm/firecracker-containerd) | false | Apache-2.0 | [API](https://api.github.com/repos/firecracker-microvm/firecracker-containerd) |
| [firectl](https://github.com/firecracker-microvm/firectl) | false | Apache-2.0 | [API](https://api.github.com/repos/firecracker-microvm/firectl) |
| [Ignite](https://github.com/weaveworks/ignite) | true | Apache-2.0 | [API](https://api.github.com/repos/weaveworks/ignite) |
| [Flintlock](https://github.com/liquidmetal-dev/flintlock) | false | MPL-2.0 | [API](https://api.github.com/repos/liquidmetal-dev/flintlock) |
| [Cloud Hypervisor](https://github.com/cloud-hypervisor/cloud-hypervisor) | false | 未识别 | [API](https://api.github.com/repos/cloud-hypervisor/cloud-hypervisor) |
| [QEMU 官方镜像](https://github.com/qemu/qemu) | false | NOASSERTION | [API](https://api.github.com/repos/qemu/qemu) |
| [crosvm 官方镜像](https://github.com/google/crosvm) | false | BSD-3-Clause | [API](https://api.github.com/repos/google/crosvm) |
| [libkrun](https://github.com/libkrun/libkrun) | false | Apache-2.0 | [API](https://api.github.com/repos/libkrun/libkrun) |
| [krunvm](https://github.com/libkrun/krunvm) | false | Apache-2.0 | [API](https://api.github.com/repos/libkrun/krunvm) |
| [vmm-reference](https://github.com/rust-vmm/vmm-reference) | true | Apache-2.0 | [API](https://api.github.com/repos/rust-vmm/vmm-reference) |
| [Kata](https://github.com/kata-containers/kata-containers) | false | Apache-2.0 | [API](https://api.github.com/repos/kata-containers/kata-containers) |
| [gVisor](https://github.com/google/gvisor) | false | Apache-2.0 | [API](https://api.github.com/repos/google/gvisor) |
| [runc](https://github.com/opencontainers/runc) | false | Apache-2.0 | [API](https://api.github.com/repos/opencontainers/runc) |
| [crun](https://github.com/containers/crun) | false | GPL-2.0 | [API](https://api.github.com/repos/containers/crun) |
| [youki](https://github.com/youki-dev/youki) | false | Apache-2.0 | [API](https://api.github.com/repos/youki-dev/youki) |
| [nsjail](https://github.com/google/nsjail) | false | Apache-2.0 | [API](https://api.github.com/repos/google/nsjail) |
| [bubblewrap](https://github.com/containers/bubblewrap) | false | NOASSERTION | [API](https://api.github.com/repos/containers/bubblewrap) |
| [Minijail](https://github.com/google/minijail) | false | BSD-3-Clause | [API](https://api.github.com/repos/google/minijail) |
| [sandbox-runtime](https://github.com/anthropics/sandbox-runtime) | false | Apache-2.0 | [API](https://api.github.com/repos/anthropics/sandbox-runtime) |
| [Wasmtime](https://github.com/bytecodealliance/wasmtime) | false | Apache-2.0 | [API](https://api.github.com/repos/bytecodealliance/wasmtime) |
| [Wasmer](https://github.com/wasmerio/wasmer) | false | MIT | [API](https://api.github.com/repos/wasmerio/wasmer) |
| [WasmEdge](https://github.com/WasmEdge/WasmEdge) | false | Apache-2.0 | [API](https://api.github.com/repos/WasmEdge/WasmEdge) |
| [Extism](https://github.com/extism/extism) | false | BSD-3-Clause | [API](https://api.github.com/repos/extism/extism) |
| [Spin](https://github.com/spinframework/spin) | false | Apache-2.0 | [API](https://api.github.com/repos/spinframework/spin) |
| [Wassette](https://github.com/microsoft/wassette) | false | MIT | [API](https://api.github.com/repos/microsoft/wassette) |
| [Monty](https://github.com/pydantic/monty) | false | MIT | [API](https://api.github.com/repos/pydantic/monty) |
| [OpenHands SDK](https://github.com/OpenHands/software-agent-sdk) | false | MIT | [API](https://api.github.com/repos/OpenHands/software-agent-sdk) |
| [SWE-ReX](https://github.com/SWE-agent/SWE-ReX) | false | MIT | [API](https://api.github.com/repos/SWE-agent/SWE-ReX) |
| [Harbor](https://github.com/harbor-framework/harbor) | false | Apache-2.0 | [API](https://api.github.com/repos/harbor-framework/harbor) |
| [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) | false | MIT | [API](https://api.github.com/repos/UKGovernmentBEIS/inspect_ai) |
| [Inspect K8s](https://github.com/UKGovernmentBEIS/inspect_k8s_sandbox) | false | MIT | [API](https://api.github.com/repos/UKGovernmentBEIS/inspect_k8s_sandbox) |
| [containerd](https://github.com/containerd/containerd) | false | Apache-2.0 | [API](https://api.github.com/repos/containerd/containerd) |
| [Podman 当前 owner](https://github.com/podman-container-tools/podman) | false | Apache-2.0 | [API](https://api.github.com/repos/podman-container-tools/podman) |
| [Incus](https://github.com/lxc/incus) | false | Apache-2.0 | [API](https://api.github.com/repos/lxc/incus) |
| [AgentScope Runtime](https://github.com/agentscope-ai/agentscope-runtime) | false | Apache-2.0 | [API](https://api.github.com/repos/agentscope-ai/agentscope-runtime) |
| [AIO Sandbox](https://github.com/agent-infra/sandbox) | false | Apache-2.0 | [API](https://api.github.com/repos/agent-infra/sandbox) |
| [Hocus](https://github.com/hocus-dev/hocus) | true | MIT | [API](https://api.github.com/repos/hocus-dev/hocus) |
| [Project-Capsule](https://github.com/Project-Capsule/capsule) | false | Apache-2.0 | [API](https://api.github.com/repos/Project-Capsule/capsule) |
| [RunD 作者 artifact](https://github.com/chengjiagan/RunD_ATC22) | true | Apache-2.0 | [API](https://api.github.com/repos/chengjiagan/RunD_ATC22) |
| [rust-vmm community](https://github.com/rust-vmm/community) | false | 未识别 | [API](https://api.github.com/repos/rust-vmm/community) |
| [Wasmer SDK](https://github.com/wasmerio/wasmer-sdk) | false | NOASSERTION | [API](https://api.github.com/repos/wasmerio/wasmer-sdk) |
| [AgentScope 迁移目标](https://github.com/agentscope-ai/agentscope) | false | Apache-2.0 | [API](https://api.github.com/repos/agentscope-ai/agentscope) |

## 社区总目录的补充主源

这些来源补充第 11 章的 OCI、集成和迁移角色说明；项目许可／归档依据仍要读上表与各章账本，不能由同一 README 推出全部安全性质。

| 来源 | 本轮核对内容 |
| --- | --- |
| [runc README](https://raw.githubusercontent.com/opencontainers/runc/main/README.md) | Linux OCI runtime、项目定位 |
| [crun README](https://raw.githubusercontent.com/containers/crun/main/README.md) | OCI runtime／C 与库接口；不采用性能排名 |
| [youki README](https://github.com/youki-dev/youki) | Rust OCI runtime，不从实现语言推导完整沙箱政策 |
| [containerd README](https://raw.githubusercontent.com/containerd/containerd/main/README.md) | daemon、完整容器生命周期与嵌入上层系统 |
| [Podman README](https://raw.githubusercontent.com/podman-container-tools/podman/main/README.md) | container／pod 管理、非 Linux 宿主的 machine 路线 |
| [Incus README](https://raw.githubusercontent.com/lxc/incus/main/README.md) | 系统 container 与 VM 管理器 |
| [AIO README](https://raw.githubusercontent.com/agent-infra/sandbox/main/README.md) | 工具环境、鉴权默认和 quickstart 的 seccomp／端口范围 |
| [OpenHands Agent Server](https://docs.openhands.dev/sdk/guides/agent-server/overview) | local、Docker 与远端 workspace 的不同后端 |
| [SWE-ReX README](https://raw.githubusercontent.com/SWE-agent/SWE-ReX/main/README.md) | 统一 shell session 接口，不等于统一隔离强度 |
| [Harbor README](https://raw.githubusercontent.com/harbor-framework/harbor/main/README.md) | 本地／云 environment 与评测／rollout |
| [Inspect sandboxing](https://inspect.aisi.org.uk/sandboxing.html) | provider、资源、每样本环境与清理 |
| [AgentScope Runtime 迁移公告](https://raw.githubusercontent.com/agentscope-ai/agentscope-runtime/main/README.md) | 合并到 2.0、旧库准备归档，而非继续推荐旧实现 |

## 未核实项与不覆盖项

- 名称相近的项目不合并：AIO 工具环境、腾讯 CubeSandbox、Kubernetes Agent Sandbox、OpenSandbox、OpenShell 各有不同所有者与实现。腾讯对应的规范仓库已核实为 `TencentCloud/CubeSandbox`；未经确认的其他名称不补猜，也不计入 54 个核心快照。
- 公开 SDK、参考 artifact、只读镜像、旧开发环境与完整自建平台都列有学习价值，但不是同一开放范围。
- 尚未对所有项目固定源码 commit，未审计整个依赖图、发行制品或供应链。表里的 API 元数据不是完整许可扫描或法律意见。
- 没有重跑这些项目的 benchmark、启动数字、部署脚本、浏览器、GPU、native OS 与多租户安全测试。
- 当前扩展只完成资料补充与本地文档／构建检查；不把 API 读取和 Markdown 测试写成生产验收。

## 怎样更新

先看官方迁移／弃用声明，再读 API 和 release／兼容性。保留“更新较慢”“归档”“待归档／迁移”“实验／beta”“成熟度未知”之间的区别。更新一个版本或 owner，通常还需要重新检查 package 许可、后端、平台、快照与默认政策，而不是只改 GitHub 链接。

新增引用应落在本页或对应章末明确标记的账本；新增核心仓库则同步机器表、总目录、数量与回归测试。不要通过扩大 source-test 的扫描范围，把未归档的正文引用自动变成“已核对”的来源。

[专题导读](README.md) · [社区总地图](11-community-project-map.md) · [基础来源](sources.md) · [开源平台](12-open-platform-projects.md) · [microVM 工具链](13-microvm-toolchain.md) · [嵌入式与 Wasm](14-embedded-and-wasm-projects.md)
