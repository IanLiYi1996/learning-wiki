# 13 microVM 工具链：从 Firecracker 到社区管理层

资料核验：2026-11-04。本文是官方文档、仓库与许可证的静态源码阅读，不是已部署、压测或通过攻击验证的报告。第 [04 章](04-microvm-and-kata.md)讲隔离边界，第 [06 章](06-lifecycle-and-orchestration.md)讲生命周期；本章补充“谁调用谁、源码从哪里读、接入后还缺什么”。分支链接会变化，实际选型须固定 release、commit、guest 镜像与依赖版本。

## 先给项目分层，不把名字当替代关系

| 层次 | 本章代表 | 提供什么 | 不自动提供什么 |
| --- | --- | --- | --- |
| VMM | Firecracker、Cloud Hypervisor、QEMU、crosvm | vCPU、内存、设备与 VM 运行 | 租户授权、任务执行 API、集群调度 |
| VMM 库／公共积木 | libkrun、rust-vmm | 嵌入式接口或可组合的虚拟化组件 | 完整托管沙箱服务 |
| SDK／启动 CLI | firecracker-go-sdk、firectl | 调用 VMM API、构造启动配置 | guest 软件、业务身份与平台状态机 |
| OCI／containerd 适配 | firecracker-containerd、krunvm | 把镜像／容器使用方式接到 VM | 所有容器编排器兼容性与多租户保证 |
| VM 生命周期管理 | Ignite、Flintlock、Capsule | 镜像准备、网络、创建与回收等管理 | 同一范围的跨主机调度与安全政策 |
| guest 管理 | containerd agent、capsule-guest、kata-agent | VM 内执行与容器管理协议 | 宿主 VMM 权限管理 |

这是按接口责任做的原创归类，具体依据见下文官方来源。同一个项目可跨层，但不能因此抹去层间责任：OCI 镜像不是 guest kernel；SDK 不是 VMM；guest agent 不是模型 Agent；“支持 vsock”也不是自带租户认证。

## Firecracker：理解一个进程内的三个角色

[Firecracker 仓库](https://github.com/firecracker-microvm/firecracker)是 VMM 本体，根 [LICENSE](https://github.com/firecracker-microvm/firecracker/blob/main/LICENSE)为 Apache-2.0。本次官方仓库 API 显示未归档。官方[设计文档](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)规定每个 Firecracker 进程只封装一个 microVM，其内部主要分为：

- API 线程：接收宿主控制请求，不在 guest I/O 的快速路径中。
- VMM 线程：组织机器、设备与事件循环，处理转交的管理请求。
- vCPU 线程：每个 guest CPU 对应一个线程，通过 KVM 执行，并参与设备 I/O 处理。

不要把这三个角色画成三台服务，也不要把 HTTP API 当作 guest 的 shell。代码入口可按 [main.rs](https://github.com/firecracker-microvm/firecracker/blob/main/src/firecracker/src/main.rs) → `api_server`／`api_server_adapter` → [builder.rs](https://github.com/firecracker-microvm/firecracker/blob/main/src/vmm/src/builder.rs)追踪，再深入 `src/vmm/src/devices`。阅读目标是找到配置在哪个阶段生效、失败后谁负责退出，而不是只看启动参数。

### 宿主与最小 guest：二进制之外的合同

官方[起步文档](https://github.com/firecracker-microvm/firecracker/blob/main/docs/getting-started.md)要求 Linux、x86_64 或 aarch64，以及对 `/dev/kvm` 的读写权限。可以运行 Docker、可以编译 Rust、可以在云 VM 中打开串口，都不能证明目标机型提供可用硬件虚拟化；嵌套环境须单独验收。

最小可启动 guest 至少要有匹配架构的 Linux kernel，以及能够到达 PID 1 的 rootfs 或 initrd。若要跑真实 Agent 工具，还要补 shell／解释器、CA、DNS、时钟、应用依赖与执行代理。“最小内核”不是删除所有驱动，而是保留所选设备和启动路径需要的配置。官方[内核政策](https://github.com/firecracker-microvm/firecracker/blob/main/docs/kernel-policy.md)列出 virtio-block、net、vsock、随机数及 PCI 等配置，并提醒 CI 使用的 microVM 内核可能含回移补丁。

核验日该政策的 host／guest 表列有 5.10、6.1、6.18 系列和对应 Firecracker 最低版本；不能把它压缩成“任何 Linux 4.x 以上都支持”。当前 main 的起步文档已有可选 `--enable-pci`，内核政策也有 PCI 启动章节，但同页仍残留较早的“不支持 PCI”说明。因此不要照搬早期文章写成“Firecracker 永远只有 MMIO”，也不要把 main 的接口当作所有历史 release 的能力。应以所选版本的代码、guest 配置与测试共同确认。

### API、vsock、MMDS 是三个不同接口

| 接口 | 调用方向与用途 | 平台审查重点 |
| --- | --- | --- |
| API Unix socket | 可信宿主控制面配置 VM | socket 权限、文件路径、设备参数与实例归属 |
| virtio-vsock | 宿主与 guest 程序通信 | 应用认证、请求大小、超时、重连及执行权限 |
| MMDS | 宿主写入元数据，guest 读取 | 数据最小化、接口启用范围、恢复后重新注入 |

[API 定义](https://github.com/firecracker-microvm/firecracker/blob/main/src/firecracker/swagger/firecracker.yaml)包含 `/boot-source`、`/machine-config`、`/drives/{drive_id}`、网络、`/vsock`、`/actions` 与快照等资源。冷启动通常先设置机器与设备，再提交 `InstanceStart`；恢复则走另外的加载路径。不能把未授权用户提供的宿主磁盘路径原样传给管理 API。

官方 [vsock 文档](https://github.com/firecracker-microvm/firecracker/blob/main/docs/vsock.md)说明宿主端 AF_UNIX 与 guest 端 AF_VSOCK 的转换。宿主主动连接时还要发送 `CONNECT <port>` 握手；guest 主动连接则映射到宿主相应端口的 Unix socket。它不是必须经过 TAP 的 IP 连接，但也没有自动实现“这个请求属于哪个用户”。原创建议：guest 服务只暴露固定协议，限制输出与并发，并让受信任 broker 检查任务代次和权限。

官方 [MMDS 指南](https://github.com/firecracker-microvm/firecracker/blob/main/docs/mmds/mmds-user-guide.md)区分已弃用 V1 与会话 token 型 V2；guest 默认不可达，须配置允许的网络接口。V2 token 不能被解释成任意 guest 进程之间的业务授权。指南还说明元数据存储内容不随 VM 快照保存，而 MMDS 版本和网络配置会保存。运营者应在恢复后重新注入新实例数据，不能因此忽略 guest 内存里已经缓存的旧秘密。

### jailer 约束宿主，snapshot 保存运行状态

官方 [jailer 文档](https://github.com/firecracker-microvm/firecracker/blob/main/docs/jailer.md)将其限定为 Firecracker 的专用隔离程序，并要求匹配版本的静态链接二进制。它准备 chroot、cgroup、namespace、资源限制，随后降权执行 VMM；不是可以给任意程序套上的通用 guest 代理。`--netns` 是加入预先安排的网络环境，不等于生成完整防火墙。

[生产宿主指南](https://github.com/firecracker-microvm/firecracker/blob/main/docs/prod-host-setup.md)要求 jailer 或同等／更严格约束，强调 jailer 输入路径可信、每实例身份隔离，以及 Firecracker 不替运营者过滤网络流量。原创验收问题是：“最后运行中的进程究竟是什么 UID、在哪个 namespace、受哪组 cgroup 上限约束？”配置里写了 jailer 不等于约束已生效；磁盘、日志与快照配额也不能只靠 guest RAM 数量推导。

[快照文档](https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md)把设备／VM 状态、guest memory 与外部管理的磁盘集合分开。CRC 只能辅助发现偶然损坏，不代替真实性保护；恢复有软硬件匹配条件，vsock 旧连接会关闭。Full／Diff 快照还涉及基线、脏页跟踪和文件一致性，不能将差分文件独立当作完整 VM 模板。

第 06 章已解释 clone uniqueness；这里补一个工具链责任：快照 API 不替你冻结外部数据库，也不替你保管磁盘基线、重建 TAP 或轮换业务凭证。VMGenID 等通知有助于 guest 感知恢复，但应用缓存的 token、随机值与身份仍须处理。所谓“恢复成功”至少应拆成 VMM 加载、guest 健康、执行代理重连、身份重新绑定四个验收点。

官方 [SPECIFICATION](https://github.com/firecracker-microvm/firecracker/blob/main/SPECIFICATION.md)中的启动和内存开销数字绑定特定机器、guest 与测量终点；不是“下载镜像到工具可用”的总延迟。本章不据此宣布它比所有 VMM 最快或最安全。

## 两条 Firecracker 链：直接管理 VM 与容器适配

以下为基于官方组件关系的原创简图，不是本轮部署记录：

```text
直接 VM 链
用户 -> 受信任 broker -> 自建管理程序 / Go SDK / firectl
                            -> jailer -> Firecracker -> KVM
                                  API ^        |
                                      |        +-> guest kernel -> PID 1 / 执行代理
                                      +--------+   vsock 或受控网络执行协议

containerd 链
客户端 -> 专用 containerd + control plugin -> 宿主 shim/runtime
                                             |-> Firecracker -> KVM
                                             +-> vsock -> guest agent -> runc -> 容器进程
```

直接链中，管理程序拥有 VM 对象：选择 kernel／rootfs、安排宿主资源、创建或恢复，guest 内怎么执行任务由你定义。容器链中，VM 与容器任务是不同对象：VM 已启动，不代表容器已创建；删除一个容器，也不必然删除那台容纳多个容器的 VM。这一区别应进入清理状态机，而不是藏在 CLI 的退出码里。

### firecracker-go-sdk 与 firectl：封装不等于平台

[firecracker-go-sdk](https://github.com/firecracker-microvm/firecracker-go-sdk)属于 Firecracker 官方组织，许可证为 [Apache-2.0](https://github.com/firecracker-microvm/firecracker-go-sdk/blob/main/LICENSE)。它在 OpenAPI 生成客户端之上封装 Go 接口；阅读顺序是仓库 README → [machine.go](https://github.com/firecracker-microvm/firecracker-go-sdk/blob/main/machine.go) → [jailer.go](https://github.com/firecracker-microvm/firecracker-go-sdk/blob/main/jailer.go) → `client`。检查创建、Start、退出处理、jailer 配置和网络资源归属。

README 明确有尚未覆盖的 Firecracker 功能。网络既可连接预建 TAP，也可调用 CNI；后者涉及宿主网络权限，且文档列出多网卡、DNS 等限制。因此 SDK 升级不能代替底层版本兼容测试，CNI 示例不能代替出站政策，`Start` 成功不能代替 guest ready。

[firectl](https://github.com/firecracker-microvm/firectl)是同组织的启动 CLI 和 SDK 示例客户端，亦为 [Apache-2.0](https://github.com/firecracker-microvm/firectl/blob/main/LICENSE)。需要另行提供 Firecracker、kernel 与 rootfs，可设置磁盘、TAP、vsock、日志等；从 [main.go](https://github.com/firecracker-microvm/firectl/blob/main/main.go)读参数如何进入 SDK。它适合学习单 VM 启动关系，不提供多租户任务服务或集群调度。

核验日两者均未归档，最近 push 分别为 2026-02-10、2026-01-16。它们是“近月更新较少但未归档”，不是“已停止维护”，也不是“最新 Firecracker 接口已全部支持”。尤其 firectl README 仍有旧 Firecracker 下载示例，不能直接当作 2026 年生产安装清单。

### firecracker-containerd：OCI 进入 guest 的完整中间层

[firecracker-containerd](https://github.com/firecracker-microvm/firecracker-containerd)亦在官方组织，许可证为 [Apache-2.0](https://github.com/firecracker-microvm/firecracker-containerd/blob/main/LICENSE)，本次未归档，最近 push 为 2026-10-21。官方[架构文档](https://github.com/firecracker-microvm/firecracker-containerd/blob/main/docs/architecture.md)划分 control plugin、宿主 runtime/shim、guest agent 和 rootfs image builder：

1. plugin 为 microVM 生命周期添加控制接口，并编入专用 containerd。
2. 宿主 shim 对接 containerd runtime v2，向 VMM 发 VM 操作，向 guest 发容器操作。
3. guest agent 代理容器控制、事件与标准输入输出，通过 guest 内 runc 创建 Linux 容器。
4. image builder 构造包含 agent／runc 等组件的 VM rootfs；用户 OCI 工作负载不等于这份系统 rootfs。

源码阅读顺序：`proto/firecracker.proto` → `firecracker-control` → `runtime` → `agent` → `tools/image-builder`；先读架构再追数据路径。containerd runtime v2 是 containerd 接口，不能因项目用了 OCI image 就宣称它是任意 OCI runtime 的即插即用替代品。

其[起步文档](https://github.com/firecracker-microvm/firecracker-containerd/blob/main/docs/getting-started.md)涉及 devmapper thin pool、专用 daemon 与配置，且仍保留较早的 Intel x86_64／AMD 和 Arm 路线图描述；示例还禁用了 CRI plugin。README 对 Kubernetes／CRI 有路线图措辞，并提示多租户用例由用户自担风险。因此“Firecracker 支持 aarch64”“仓库最近有 push”都不足以证明所选 adapter 版本在 Arm／Kubernetes 上已获得完整验证。

原创审查重点：锁定 containerd、SDK、VMM、kernel 和 agent 组合；区分宿主存储 snapshotter 与 VM memory snapshot；明确一 VM 内能否混放不互信容器；查有效 jailer 配置，不能用 README 的旧路线图推断代码从未实现某项能力。镜像来源、CNI、磁盘回收、daemon socket 和租户准入仍归平台负责。

## 社区管理项目：看能力，也看生命周期

### Ignite：有价值的历史设计，不是当前维护方案

[weaveworks/ignite](https://github.com/weaveworks/ignite)是规范仓库，许可证为 [Apache-2.0](https://github.com/weaveworks/ignite/blob/main/LICENSE)。README 明确 Deprecated／不再维护；官方 API 显示已归档，最后 push 为 2023-12-07。它把 OCI rootfs／kernel 镜像接到 Firecracker，提供类似容器的 VM 管理体验、CNI 与声明式 GitOps。

它值得回答“如何把 OCI 分发与独立 guest 系统组合”，不宜回答“今天装什么就有人持续修安全问题”。阅读入口是 README 的 Scope、镜像／kernel 说明与 `docs/installation.md`、`pkg`。历史 root 权限、alpha 警告、内核及下载示例需一起阅读；维护 fork、替换依赖和补齐宿主约束均由接手者承担。

### Flintlock：单宿主 VM 服务，不等于全局调度器

[liquidmetal-dev/flintlock](https://github.com/liquidmetal-dev/flintlock)是当前规范仓库，许可证为 [MPL-2.0](https://github.com/liquidmetal-dev/flintlock/blob/main/LICENSE)，未归档，最近 push 为 2026-11-02。README 明确支持 Firecracker 与 Cloud Hypervisor，通过 gRPC／HTTP 创建、查询、删除 microVM，并用 OCI 镜像分发卷、kernel 与 initrd；可提供初始化数据和 vsock guest-agent 通信。

它最初服务于把 microVM 作为 Kubernetes 集群节点的场景；这与“每个 Pod 由 Kata 启动一台 VM”不是同一对象模型。README 将跨主机编排和预热池列为其他组件的职责，所以不要把宿主 API 当成已经完成整个 fleet 的调度和租户分配。

阅读入口：README compatibility 表 → `api`／`core` → [Firecracker 创建代码](https://github.com/liquidmetal-dev/flintlock/blob/main/infrastructure/microvm/firecracker/create.go)及另一 provider。当前文档区分 TAP 与 Cloud Hypervisor 专有的 macvtap／virtiofs 支持，并明确不再支持早期 Weaveworks macvtap Firecracker fork。Linux/KVM 能力、后端版本、镜像初始化、宿主网络及资源残留需分别验收；不是换一个 provider 名字就可复制所有设备配置。

### Hocus 与 Capsule：必须先消除名称和时代混淆

[hocus-dev/hocus](https://github.com/hocus-dev/hocus)是开发环境产品源码，不是新 VMM。当前 [LICENSE.md](https://github.com/hocus-dev/hocus/blob/main/LICENSE.md)为 MIT；README 明确于 2024-09-28 归档并停止维护。官方 [Hocus 博客](https://hocus.dev/blog/)记录其初期使用 Firecracker、2023 年改用 QEMU。因此旧目录或宣传中的 Firecracker 标签不能代表最后的实现，更不能把当年的设备限制照搬为今天的 Firecracker 事实。

可从仓库 `app/agent` 与开发环境工作流读 VM、预构建、连接和清理的结合方式。它适合作为长寿命开发环境的历史工程案例；若复用代码，依赖修复、guest／host 更新和新平台兼容性没有原团队维护保证。本轮不确认其历史安装方案在当前机器上可直接运行。

确有相关官方源码的同名项目是 [Project-Capsule/capsule](https://github.com/Project-Capsule/capsule)，许可证为 [Apache-2.0](https://github.com/Project-Capsule/capsule/blob/main/LICENSE)，本次未归档。它是单主机不可变 Linux 系统与管理服务：`capsuled` 为宿主 PID 1，统一管理普通容器与 Firecracker VM；不是 Hocus 的继任仓库，也不是分布式集群平台。

其[架构文档](https://github.com/Project-Capsule/capsule/blob/main/docs/architecture.md)说明共享 guest rootfs、每 VM OCI payload 磁盘、`capsule-guest` 的 vsock 服务与 guest 内 runc。阅读顺序：架构 → `runtime/microvm/firecracker` → `cmd/capsule-guest` → reconciler。其[起步文档](https://github.com/Project-Capsule/capsule/blob/main/docs/getting-started.md)构建产物固定为 linux/amd64，要求 UEFI；macOS 可以是构建／操作端，不表示 macOS 原生提供 Firecracker KVM。

更重要的是 [PLAN](https://github.com/Project-Capsule/capsule/blob/main/PLAN.md)明确把 jailer 加固和 microVM 资源限制列为待办；本轮读取的 [driver.go](https://github.com/Project-Capsule/capsule/blob/main/runtime/microvm/firecracker/driver.go)也直接构造 Firecracker 进程。故只能将其作为可学习的单机集成，不能把文档中的工作清单写成已满足敌对多租户的生产承诺。运营者仍须处理特权管理面、VMM 降权、配额和网络策略。

## 支撑景观：不同 VMM、库与 Kata 后端

### Cloud Hypervisor：云 VM 能力与版本条件一起看

[Cloud Hypervisor](https://github.com/cloud-hypervisor/cloud-hypervisor)是基于 Rust 的 VMM，README 描述 KVM／MSHV、现代云 guest、virtio、热插拔与迁移；主要架构为 x86_64、aarch64，riscv64 标为实验性，核验日 main 的最低宿主内核要求为 6.8。能力不能跨架构、hypervisor 和发行版无条件外推。

其当前 [package 声明](https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/cloud-hypervisor/Cargo.toml)是 `Apache-2.0 AND BSD-3-Clause`，对应 [Apache 文本](https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/LICENSES/Apache-2.0.txt)与 [BSD 文本](https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/LICENSES/BSD-3-Clause.txt)；[文档另有 CC-BY-4.0](https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/LICENSES/CC-BY-4.0.txt)。GitHub 自动识别为空不等于没有许可证，更不能把 AND 写成任选其一的 OR。

源码入口按 README → `cloud-hypervisor/src` → `vmm` → `hypervisor`／设备后端读。README 明确跨版本 snapshot／restore 与 live migration 不保证支持。virtiofs、透传与迁移需要相应后端、宿主权限和测试；更丰富的设备合同不是“默认沙箱权限更小”。

### QEMU：先选安全用例，再选机器和设备

[QEMU 上游仓库](https://gitlab.com/qemu-project/qemu)在 GitLab；本轮同时读其[官方 GitHub 镜像 README](https://github.com/qemu/qemu/blob/master/README.rst)。它支持系统模拟、硬件加速虚拟化与用户态模拟，不能把三者当同一隔离机制。

[LICENSE](https://github.com/qemu/qemu/blob/master/LICENSE)说明整体模拟器为 GPL-2.0，部分代码另有兼容许可证，固件是单独程序；还应查看 [COPYING](https://github.com/qemu/qemu/blob/master/COPYING)、[COPYING.LIB](https://github.com/qemu/qemu/blob/master/COPYING.LIB)及具体文件。API 的 NOASSERTION 不是“无许可证”，也不是所有捆绑物都只有同一种许可证。

阅读入口：官方[安全合同](https://www.qemu.org/docs/master/system/security.html) → 所选 machine／accelerator → 源码 `hw`、`accel`、`qapi`。官方合同要求硬件虚拟化 accelerator 和列出的 machine type；TCG 等非虚拟化用例不能依赖同样的 guest 隔离保证。QEMU 自身也有 `microvm` machine，不等于 Firecracker。monitor 属于特权控制面；磁盘解析、共享目录、vhost-user 后端与设备暴露仍需最小权限、配额和逐项审查。

### crosvm：设备进程隔离也有平台条件

[crosvm 规范源码](https://chromium.googlesource.com/crosvm/crosvm/)在 Chromium Git，Google 的 [GitHub 仓库](https://github.com/google/crosvm)是只读镜像，而非“项目已归档”。其根 [LICENSE](https://github.com/google/crosvm/blob/main/LICENSE)为 BSD-3-Clause。README 列出多个架构／hypervisor 和图形、音频等设备，但这不是所有组合可互换的支持矩阵。

从 README → `ARCHITECTURE.md` → `devices`／`hypervisor` 和所选构建 feature 阅读。Linux 设备进程可借助 Minijail、namespace 与 seccomp 隔离；不能把 Linux 的进程约束原样声称为所有其他宿主的实现。运营者仍需核对构建选项、设备后端、图形共享与控制通道，不能用“Rust＋设备沙箱”替代自己的威胁模型。

### rust-vmm：组件集合与参考 VMM 要分开

[rust-vmm/community](https://github.com/rust-vmm/community)是公共虚拟化组件的说明入口，包括 KVM 调用、guest memory、加载器和 virtio 等；不是一项可以直接启动租户会话的服务。源码阅读应选实际消费的 crate，从公开接口、unsafe 边界、依赖和测试往下追，而不是把组织名当一个发行包。

许可证必须逐 crate 看。示例 [kvm-ioctls Cargo.toml](https://github.com/rust-vmm/kvm-ioctls/blob/main/kvm-ioctls/Cargo.toml)当前声明 `Apache-2.0 OR MIT`，并有 [Apache](https://github.com/rust-vmm/kvm-ioctls/blob/main/kvm-ioctls/LICENSE-APACHE)与 [MIT](https://github.com/rust-vmm/kvm-ioctls/blob/main/kvm-ioctls/LICENSE-MIT)文本；community 的许可建议不等于每个 crate 的实际许可。

[vmm-reference](https://github.com/rust-vmm/vmm-reference)才是将组件拼起来的参考 VMM：已归档，最后 push 为 2024-09-09，README 明确实验用途、不用于生产。它的 [Cargo.toml](https://github.com/rust-vmm/vmm-reference/blob/main/Cargo.toml)及 [Apache](https://github.com/rust-vmm/vmm-reference/blob/main/LICENSE-APACHE)／[BSD](https://github.com/rust-vmm/vmm-reference/blob/main/LICENSE-BSD-3-CLAUSE)文本表明 `Apache-2.0 OR BSD-3-Clause`，比 API 单一标签更完整。它可教组件如何组装，不能证明整个 rust-vmm 组织停止维护，也不能把历史示例默认参数当作新的生产基线。

### libkrun 与 krunvm：库和 OCI CLI 不要重复计成两种 VMM

[libkrun/libkrun](https://github.com/libkrun/libkrun)与 [libkrun/krunvm](https://github.com/libkrun/krunvm)是当前规范仓库；旧 containers 地址会重定向。二者根许可证分别为 [Apache-2.0](https://github.com/libkrun/libkrun/blob/main/LICENSE)、[Apache-2.0](https://github.com/libkrun/krunvm/blob/main/LICENSE)，本次均未归档。

libkrun 将 VMM 封装为动态库，以 Rust／C API 接入程序。README 区分 Linux KVM、macOS ARM64 HVF，并把 Windows WHP 标为 upcoming；main 现为仍可能变化的 2.0 API／ABI，生产源码构建应选最新 stable 分支。krunvm 是利用 libkrun 与 buildah 从 OCI 镜像创建 microVM 的 CLI，README 列出 Linux x86_64／aarch64 与 macOS ARM64。不能由库的未来后端推出 CLI 已支持该平台。

阅读入口：libkrun README → `include` 接口 → [Security Model](https://github.com/libkrun/libkrun/blob/main/docs/security-model.md)；krunvm README → `src` 的镜像与卷处理。安全文档特别提醒 virtiofs 暴露路径、资源耗尽及 TSI 代理使用 VMM 的宿主网络上下文，包括配置允许的 Unix socket 访问。所谓“零网络配置”是使用体验，不是默认没有出站能力；挂载宿主目录也不因存在 VM 边界就自动安全。

### Dragonball 与 RunD：归入 Kata 的关系，不多算独立平台

[Kata 仓库](https://github.com/kata-containers/kata-containers)中的 [Dragonball README](https://github.com/kata-containers/kata-containers/blob/main/src/dragonball/README.md)确认它是面向容器的 Linux/KVM VMM，并列出 x86-64、aarch64。其 [crate 声明](https://github.com/kata-containers/kata-containers/blob/main/src/dragonball/Cargo.toml)及 [Kata LICENSE](https://github.com/kata-containers/kata-containers/blob/main/LICENSE)为 Apache-2.0。当前 [runtime-rs](https://github.com/kata-containers/kata-containers/blob/main/src/runtime-rs/README.md)将它作为内建后端，并列出外部 QEMU／Cloud Hypervisor／Firecracker。

阅读路径是 runtime-rs → `crates/hypervisor` → `src/dragonball` 及其 device／vCPU／API 文档。源码支持架构不等于每种发行包都包含相同后端；还要检查 shim 构建、配置、guest agent 和节点硬件。它是 Kata 的实现后端，不应与 Kata 重复计成两套独立 Agent 沙箱平台。

[RunD_ATC22](https://github.com/chengjiagan/RunD_ATC22)则是论文作者公开的实验脚本和原始数据仓库，根 [LICENSE](https://github.com/chengjiagan/RunD_ATC22/blob/main/LICENSE)为 Apache-2.0，本次已归档。README 说明部分二进制与内部系统紧耦合，并将开源演进关联到 Kata runtime-rs。因此可以研究其实验合同与历史设计，不应将该 artifact 说成可自行完整部署的 RunD 运行时，也不能由脚本许可证推断未公开实现的许可证。本轮未核实独立、完整、持续维护的 RunD 发行仓库。

## 给选型与源码阅读一个落点

“已归档”是仓库只读状态；“更新较慢”是观察到的时间间隔；“未归档、最近有 push”也只是当前事实，不是安全补丁时限、未来维护承诺或某个功能成熟度。Ignite、Hocus、vmm-reference、RunD artifact 的历史价值可以保留，但不能和其他项目一起无区别地列成当前维护推荐。

原创实践顺序：先确定需要直接 VM、容器适配还是开发环境；再固定宿主架构／虚拟化后端／guest 设备；随后沿“API → 资源准备 → 启动 → guest ready → 执行 → 清理”追一次完整调用。最后填一张责任清单：谁认证用户，谁限制设备与宿主路径，谁过滤网络，谁保存磁盘和快照，谁处理崩溃残留，谁更新 guest／host／VMM。

本轮尚未证明的事项包括：任何项目在指定机器上的部署成功、延迟与密度、多租户安全验收、containerd adapter 的当前 Arm／CRI 完整兼容性、历史 Hocus 安装可用性，以及 RunD 独立实现的完整公开范围。源码阅读是缩小这些未知项的起点，不是已经完成验收。

## 自测与答案

1. 安装 Go SDK 后，是否已经有带鉴权的 guest shell 服务？**没有。** SDK 面向宿主 VMM API；guest 执行协议和用户授权需另行实现。
2. containerd 中删除一个容器，是否必然删除 microVM 和全部磁盘？**不必然。** 容器任务、VM 对象与存储生命周期须分别追踪，尤其一 VM 可运行多个容器。
3. GitHub 显示未归档或许可证标签为空，分别证明长期维护或没有许可证吗？**都不证明。** 前者须和更新时间、路线图、版本支持分开；后者须读 LICENSE、package 声明与具体组件。

<!-- community-sources:start -->
## 本章来源小账本

以下均为官方仓库、官方镜像、项目文档或作者 artifact；核验日期统一为 **2026-11-04**。正文使用的外部来源在此重列，供合并全局账本；许可证结论只覆盖明确列出的项目／组件，不覆盖整个依赖与镜像供应链。

| 项目／证据组 | 精确官方来源 |
| --- | --- |
| Firecracker 本体与源码 | [仓库](https://github.com/firecracker-microvm/firecracker)；[LICENSE](https://github.com/firecracker-microvm/firecracker/blob/main/LICENSE)；[设计](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)；[main.rs](https://github.com/firecracker-microvm/firecracker/blob/main/src/firecracker/src/main.rs)；[builder.rs](https://github.com/firecracker-microvm/firecracker/blob/main/src/vmm/src/builder.rs) |
| Firecracker 主机／guest／接口 | [Getting started](https://github.com/firecracker-microvm/firecracker/blob/main/docs/getting-started.md)；[Kernel policy](https://github.com/firecracker-microvm/firecracker/blob/main/docs/kernel-policy.md)；[API schema](https://github.com/firecracker-microvm/firecracker/blob/main/src/firecracker/swagger/firecracker.yaml)；[vsock](https://github.com/firecracker-microvm/firecracker/blob/main/docs/vsock.md)；[MMDS](https://github.com/firecracker-microvm/firecracker/blob/main/docs/mmds/mmds-user-guide.md) |
| Firecracker 宿主约束与状态 | [jailer](https://github.com/firecracker-microvm/firecracker/blob/main/docs/jailer.md)；[生产宿主](https://github.com/firecracker-microvm/firecracker/blob/main/docs/prod-host-setup.md)；[Snapshot support](https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md)；[SPECIFICATION](https://github.com/firecracker-microvm/firecracker/blob/main/SPECIFICATION.md) |
| firecracker-go-sdk | [仓库／README](https://github.com/firecracker-microvm/firecracker-go-sdk)；[LICENSE](https://github.com/firecracker-microvm/firecracker-go-sdk/blob/main/LICENSE)；[machine.go](https://github.com/firecracker-microvm/firecracker-go-sdk/blob/main/machine.go)；[jailer.go](https://github.com/firecracker-microvm/firecracker-go-sdk/blob/main/jailer.go) |
| firectl | [仓库／README](https://github.com/firecracker-microvm/firectl)；[LICENSE](https://github.com/firecracker-microvm/firectl/blob/main/LICENSE)；[main.go](https://github.com/firecracker-microvm/firectl/blob/main/main.go) |
| firecracker-containerd | [仓库／README](https://github.com/firecracker-microvm/firecracker-containerd)；[LICENSE](https://github.com/firecracker-microvm/firecracker-containerd/blob/main/LICENSE)；[Architecture](https://github.com/firecracker-microvm/firecracker-containerd/blob/main/docs/architecture.md)；[Getting started](https://github.com/firecracker-microvm/firecracker-containerd/blob/main/docs/getting-started.md) |
| Ignite | [归档仓库／弃用声明](https://github.com/weaveworks/ignite)；[LICENSE](https://github.com/weaveworks/ignite/blob/main/LICENSE) |
| Flintlock | [规范仓库／兼容性表](https://github.com/liquidmetal-dev/flintlock)；[LICENSE](https://github.com/liquidmetal-dev/flintlock/blob/main/LICENSE)；[Firecracker create.go](https://github.com/liquidmetal-dev/flintlock/blob/main/infrastructure/microvm/firecracker/create.go) |
| Hocus | [归档仓库／停止维护声明](https://github.com/hocus-dev/hocus)；[LICENSE.md](https://github.com/hocus-dev/hocus/blob/main/LICENSE.md)；[官方博客／更换 QEMU 的历史记录](https://hocus.dev/blog/) |
| Capsule（Project-Capsule） | [仓库](https://github.com/Project-Capsule/capsule)；[LICENSE](https://github.com/Project-Capsule/capsule/blob/main/LICENSE)；[Architecture](https://github.com/Project-Capsule/capsule/blob/main/docs/architecture.md)；[Getting started](https://github.com/Project-Capsule/capsule/blob/main/docs/getting-started.md)；[PLAN](https://github.com/Project-Capsule/capsule/blob/main/PLAN.md)；[driver.go](https://github.com/Project-Capsule/capsule/blob/main/runtime/microvm/firecracker/driver.go) |
| Cloud Hypervisor | [仓库／README](https://github.com/cloud-hypervisor/cloud-hypervisor)；[Package license](https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/cloud-hypervisor/Cargo.toml)；[Apache](https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/LICENSES/Apache-2.0.txt)；[BSD](https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/LICENSES/BSD-3-Clause.txt)；[文档 CC-BY-4.0](https://github.com/cloud-hypervisor/cloud-hypervisor/blob/main/LICENSES/CC-BY-4.0.txt) |
| QEMU | [规范上游](https://gitlab.com/qemu-project/qemu)；[官方镜像 README](https://github.com/qemu/qemu/blob/master/README.rst)；[LICENSE](https://github.com/qemu/qemu/blob/master/LICENSE)；[COPYING](https://github.com/qemu/qemu/blob/master/COPYING)；[COPYING.LIB](https://github.com/qemu/qemu/blob/master/COPYING.LIB)；[官方安全合同](https://www.qemu.org/docs/master/system/security.html) |
| crosvm | [规范源码](https://chromium.googlesource.com/crosvm/crosvm/)；[GitHub 镜像／README](https://github.com/google/crosvm)；[LICENSE](https://github.com/google/crosvm/blob/main/LICENSE) |
| rust-vmm 与 crate 示例 | [Community](https://github.com/rust-vmm/community)；[kvm-ioctls package](https://github.com/rust-vmm/kvm-ioctls/blob/main/kvm-ioctls/Cargo.toml)；[Apache](https://github.com/rust-vmm/kvm-ioctls/blob/main/kvm-ioctls/LICENSE-APACHE)；[MIT](https://github.com/rust-vmm/kvm-ioctls/blob/main/kvm-ioctls/LICENSE-MIT) |
| vmm-reference（归档参考实现） | [仓库／生产使用警告](https://github.com/rust-vmm/vmm-reference)；[Cargo.toml](https://github.com/rust-vmm/vmm-reference/blob/main/Cargo.toml)；[LICENSE-APACHE](https://github.com/rust-vmm/vmm-reference/blob/main/LICENSE-APACHE)；[LICENSE-BSD-3-CLAUSE](https://github.com/rust-vmm/vmm-reference/blob/main/LICENSE-BSD-3-CLAUSE) |
| libkrun／krunvm | [libkrun 规范仓库](https://github.com/libkrun/libkrun)；[libkrun LICENSE](https://github.com/libkrun/libkrun/blob/main/LICENSE)；[Security model](https://github.com/libkrun/libkrun/blob/main/docs/security-model.md)；[krunvm 规范仓库](https://github.com/libkrun/krunvm)；[krunvm LICENSE](https://github.com/libkrun/krunvm/blob/main/LICENSE) |
| Kata／Dragonball | [Kata 仓库](https://github.com/kata-containers/kata-containers)；[Kata LICENSE](https://github.com/kata-containers/kata-containers/blob/main/LICENSE)；[Dragonball README](https://github.com/kata-containers/kata-containers/blob/main/src/dragonball/README.md)；[Dragonball Cargo.toml](https://github.com/kata-containers/kata-containers/blob/main/src/dragonball/Cargo.toml)；[runtime-rs README](https://github.com/kata-containers/kata-containers/blob/main/src/runtime-rs/README.md) |
| RunD 作者 artifact | [仓库／公开范围说明](https://github.com/chengjiagan/RunD_ATC22)；[LICENSE](https://github.com/chengjiagan/RunD_ATC22/blob/main/LICENSE) |
| 本轮官方 GitHub API 状态证据（一） | [Firecracker](https://api.github.com/repos/firecracker-microvm/firecracker)；[Go SDK](https://api.github.com/repos/firecracker-microvm/firecracker-go-sdk)；[firectl](https://api.github.com/repos/firecracker-microvm/firectl)；[containerd adapter](https://api.github.com/repos/firecracker-microvm/firecracker-containerd)；[Ignite](https://api.github.com/repos/weaveworks/ignite)；[Flintlock](https://api.github.com/repos/liquidmetal-dev/flintlock) |
| 本轮官方 GitHub API 状态证据（二） | [Hocus](https://api.github.com/repos/hocus-dev/hocus)；[Capsule](https://api.github.com/repos/Project-Capsule/capsule)；[Cloud Hypervisor](https://api.github.com/repos/cloud-hypervisor/cloud-hypervisor)；[QEMU 镜像](https://api.github.com/repos/qemu/qemu)；[crosvm 镜像](https://api.github.com/repos/google/crosvm)；[rust-vmm community](https://api.github.com/repos/rust-vmm/community)；[libkrun](https://api.github.com/repos/libkrun/libkrun)；[krunvm](https://api.github.com/repos/libkrun/krunvm)；[Kata](https://api.github.com/repos/kata-containers/kata-containers)；[RunD artifact](https://api.github.com/repos/chengjiagan/RunD_ATC22)；[vmm-reference 中央快照](https://api.github.com/repos/rust-vmm/vmm-reference) |

<!-- community-sources:end -->

[专题导读](README.md) · [社区项目总地图](11-community-project-map.md) · [上一章：开源平台](12-open-platform-projects.md) · [下一章：嵌入式与Wasm项目](14-embedded-and-wasm-projects.md)
