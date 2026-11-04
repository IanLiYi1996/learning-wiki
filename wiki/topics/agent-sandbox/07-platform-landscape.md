# 07 平台版图：同叫 Sandbox，交付的边界和责任并不相同

研究日期：2026-11-04。仅使用实时查阅的厂商官方文档、官方发布记录与官方代码仓库；没有部署这些产品，也没有运行逃逸测试或跨平台性能测试。本章比较执行边界、状态语义和责任分工，不做营销排名，不引用缺少同等测试条件的价格或启动速度比较。

## 1. 先确定比较的是哪一种产品、哪一种版本

“给 agent 一个计算机”和“托管 agent 服务”不是完全相同的需求：前者可能要运行陌生仓库的测试、安装系统包、启动浏览器；后者可能只运行你审核过的编排代码，再调用独立工具。选型应记录四个对象：控制 agent 的可信服务、不可信代码的执行环境、允许访问的数据与凭据、保存产物的存储。下文把产品事实与由事实推导的工程判断分开；“未知”表示本次材料不能证明，不表示产品一定没有该能力。

截至研究日，至少有五个容易沿用旧印象的变化：

- Modal 文档已经提供 `gvisor` 与 `vm` 两种运行时；不是只有 gVisor，也不能据此写成每个 Sandbox 都同时经过“gVisor + microVM”两层。[Modal 运行时][modal-sandboxes] [安全模型][modal-network]
- Daytona 当前稳定文档标为 v0.227，Linux sandbox 有 Container 和 Linux VM 两类，默认 Container 共享 runner 的内核；另一个 v2 文档入口明确写 Linux Firecracker microVM，但稳定版页面把该入口标为 Alpha。版本不同，结论不能串用。[稳定版 Linux][daytona-linux] [v2 入口][daytona-v2]
- Cloudflare 当前 Sandboxes 文档区分 Container 与 Dynamic Worker，并保留 Sandbox SDK 0.x 文档。Linux Container 路径在 Firecracker microVM 内运行；Dynamic Worker 是 Workers/V8 路径，不是同一个虚拟机边界。[环境选择][cf-environments]
- Vercel Sandbox 当前默认保存文件系统，停止后可恢复新会话；不能继续笼统描述成“停止即永久丢失所有数据的临时沙盒”。[持久化正式发布][vercel-persistence-release]
- AWS 当前既有 AgentCore Runtime 的 microVM 与 Instances 两种计算类型，也有独立的 Lambda MicroVMs 产品；不能把 AgentCore、Lambda Event Functions、Lambda MicroVMs 和 Fargate 当成同一种 API 的不同名称。[AgentCore Instances][aws-instances] [Lambda MicroVMs][lambda-microvms]

下表只说明公开证据支持的边界。独立 guest 内核并不自动证明没有实现漏洞、侧信道或配置错误；公开架构也不是某次实际部署正确的证据。

| 平台／明确运行类型 | 官方材料支持的执行边界 | 不能从产品名推导什么 |
| --- | --- | --- |
| E2B Cloud／Runtime | 每个 sandbox 为 Firecracker microVM；Runtime 同时实现控制面、节点编排器、VM 内 agent 与流量路由。[官方仓库][e2b-runtime] | 开源 Runtime 不等于所有自托管套餐自动拥有 Cloud 的全部集成 |
| Modal `runtime="gvisor"` | 用户态 Linux 系统调用接口由 gVisor 处理。[安全模型][modal-network] | 不能证明该路径必然还套一层 microVM |
| Modal `runtime="vm"` | 独立 Linux kernel 的 VM，以 Linux KVM／CPU 硬件虚拟化隔离。[安全模型][modal-network] | 所读页面未说明具体 VMM 是 Firecracker，也未证明 VM 内再使用 gVisor |
| Daytona 稳定版 Container | namespaces 与资源限制；Linux 文档明确共享 host kernel，是默认 class。[Linux][daytona-linux] [隔离][daytona-isolation] | 不能标为“每个 sandbox 独立 microVM” |
| Daytona 稳定版 Linux VM | 独立 Linux kernel、硬件虚拟化边界；snapshot 决定 class。[Linux][daytona-linux] | 所读稳定版 class 页面不足以认定所有 Linux VM 使用某个特定 VMM |
| Daytona v2 文档的 Linux | v2 入口明确写 Firecracker microVM；稳定版导航标该入口 Alpha。[v2][daytona-v2] [版本导航][daytona-linux] | 不能把 v2 宣传／架构反推到稳定版默认 Container |
| Cloudflare Linux Container sandbox | Linux image 作为 container 在独立 Firecracker microVM 内运行。[环境选择][cf-environments] | Container 字样不等于共享其他客户的宿主内核 |
| Cloudflare Dynamic Worker／Workers 中的 Wasm | Dynamic Worker 使用 V8 沙箱及 Workers 的进程级防护；Wasm 是 Workers 支持的另一种代码形式。[环境选择][cf-environments] [Workers 安全][cf-workers-security] [Wasm][cf-wasm] | 每个 Worker／Wasm module 不等于一台具有独立 Linux kernel 的 VM |
| Vercel Sandbox | 每个 sandbox 为 Firecracker microVM，独立文件系统和网络。[概览][vercel-overview] | 不等于 Vercel Functions 的执行模型；VM 内不同进程不自动成为不同客户的边界 |
| Fly.io Machines | 平台应用运行在 Firecracker microVM，以 Machines API 管理。[架构][fly-architecture] [Machines][fly-machines] | VM 隔离不意味着同 organization 的私网或 app secrets 也按 Machine 隔离 |
| AgentCore Runtime，microVM 类型 | 每个 Runtime session 专属 microVM；同会话中的 agent 与 shell 共享环境。[会话][aws-runtime-sessions] | 每次工具调用或每次 `exec` 不会自动再分配独立 VM |
| AgentCore Runtime，Instances 类型 | AWS 在客户账户中管理 EC2 instances，支持同实例内协作 agent。[Instances][aws-instances] | 不沿用默认 microVM 类型的“一会话一 microVM”结论 |
| AgentCore Code Interpreter／Browser | 各工具自己的 session 使用专属 microVM。[解释器会话][aws-ci-sessions] [浏览器会话][aws-browser-sessions] | Runtime session ID 不是这两个工具的会话边界；页面未明确 VMM 名称 |
| AWS Lambda Event Functions／Lambda MicroVMs | AWS 明确 Lambda MicroVMs 基于 Firecracker；传统函数的执行环境也使用 Firecracker，但两者生命周期 API 不同。[MicroVMs][lambda-microvms] [Lambda FAQ][lambda-faq] | 传统函数每次 invocation 不保证新的、可由用户暂停恢复的 VM |
| ECS on Fargate | 安全边界为 task，不同 task 不共享底层 kernel、CPU／memory 资源或 ENI。[Fargate][fargate-overview] | 同 task 的多个容器不是多个互不信任租户的硬边界；不由此断言所有平台版本都使用 Firecracker |
| Docker Sandboxes，本地模式 | agent 在 microVM 内；宿主工作目录、代理和 MCP 是显式跨边界入口。[安全模型][docker-security] | 不等于普通 `docker run`；所读材料不足以认定具体 hypervisor，也不能把本地存储语义套到 cloud 模式 |

## 2. E2B：Firecracker 执行环境，以及不同部署模式的责任边界

E2B 的核心不是在可信 agent 进程中增加一个 `eval`，而是让 SDK 操作另一台隔离 Linux 机器。官方 Runtime 仓库给出了完整组成：控制面 API 决定放置，节点 orchestrator 管理 Firecracker、网络与块设备，VM 内 `envd` 提供进程、PTY、文件和端口相关接口。因此，可以把模型与编排逻辑留在可信后端，把仓库、测试、生成代码放入 sandbox。[Runtime 架构说明][e2b-runtime]

状态要区分三件事。Template 是创建环境的起点；默认 pause 保存文件系统与内存，可恢复进程和变量；`mode="filesystem"` 则只保存文件系统，恢复时重新启动，不能期待进程继续。当前文档说明 paused sandbox 不自动过期，只有显式 kill 才删除。工程含义是：暂停不是销毁，回收器必须同时管理暂停状态及其存储，不能只数正在运行的 VM。[持久化与两种 pause][e2b-persistence]

网络默认允许出站 Internet，可用开关或 IP／CIDR／域名 allow／deny 控制。凭据方面，E2B Secrets 的 HTTPS header 注入发生在 sandbox 外；2026-11-03 发布的 Workload Identity 也把签名身份 token 加到匹配的出站请求中，而不是放入 guest 的环境变量。接收服务仍须验证签名、audience、期限及身份，并决定允许何种业务操作；“有 JWT”不是数据授权已经完成。[网络][e2b-network] [Secrets][e2b-secrets] [Workload Identity][e2b-identity]

自托管不能只看 Compose 文件能否启动。当前 Embed Compose README 要求 Linux、KVM、相关设备与宿主内核能力；嵌套虚拟化是 VM 内部署的前提。Compose 启动的是包含真实 Firecracker orchestrator 的单机栈，不是把 microVM 改成普通 Docker 容器。镜像架构、宿主设备、模板构建和快照磁盘容量都属于操作者的责任。[Embed Compose 要求][e2b-compose]

还要注意证据的时间和适用范围：2026-09-30 的 Embed 发布说明明确表示，当时 Embed 不含 secrets、volumes、workload identity 和 BYO proxy；当前 Runtime 总览则列出了这些能力。两份材料证明“代码栈有能力”和“某部署发行包实际支持”不能混为一谈。本次没有逐项审计 Embed 发布制品与功能开关，所以不将这些 Cloud 功能声明为当前 Embed 已全部可用，也不把旧发布说明当成永不变化的限制。[Embed 发布范围][e2b-embed-release] [当前 Runtime][e2b-runtime]

## 3. Modal Sandboxes：先选运行时，再讨论兼容性

Modal 当前用参数选择 gVisor 或 VM；未指定时由平台选择。VM 路径面向 Docker-in-Docker、FUSE、嵌套 cgroups 等完整 Linux 需求；GPU sandbox 当前只支持 gVisor。这里的“兼容性”是具体系统能力是否满足，不是哪个产品整体更优。对要求明确边界的生产系统，应显式记录所选 runtime，不能依赖默认选择永远不变。[运行时与兼容性][modal-sandboxes]

生命周期上，目录／文件系统 snapshot 与 memory snapshot 是不同对象；当前 memory snapshot 标为 Alpha，支持两种 runtime。保留期也不同：文件系统和目录 snapshot 默认 30 天，可以配置；memory snapshot 为 7 天，当前不能延长。不能从“有 snapshot”推出永久保存，也不能从文件系统恢复推出内存中的 agent loop 会继续。[Snapshot 类型、成熟度与保留期][modal-snapshots]

Modal 默认不开放入站，也不授予 Sandbox 对 workspace 其他资源的默认访问能力；但默认可以向公共 IP 出站。网络页提供全禁、CIDR 和 Beta 域名限制，并明确除全禁外 DNS 仍不受限制。因此，“没有默认 Modal 权限”和“没有外部网络”是两种结论。当前 Beta Secret Injection 可在 sandbox 外向匹配 HTTPS 请求替换 header；普通 `Secret` 环境变量注入则把值交给了 sandbox 内代码。[网络与默认授权][modal-network] [Secret Injection Beta][modal-secret-injection] [环境变量方式][modal-sandboxes]

本次文档证明的是两种可选隔离路径，没有证明每个 gVisor Sandbox 都在 microVM 里，也没有证明 VM 路径使用 Firecracker。架构图应保留这个未知，而不是按行业常见组合补齐。托管计算不消除镜像维护、出站策略、快照清理和租户映射等应用责任。[安全模型][modal-network]

## 4. Daytona：Container、Linux VM 和 v2 不能写成一行

Daytona 稳定 Linux 文档对 class 的定义比概览中的“完整隔离”更精确：Container 共享 host kernel；Linux VM 自己有 kernel，由硬件虚拟化形成边界；snapshot 决定 sandbox class。两者使用相同 SDK／CLI／API，不意味着两者安全模型相同。看到“兼容 Docker image”也不能判断底层是容器还是 VM，因为 image 可以只是启动文件系统的来源。[Linux class 定义][daytona-linux]

当前稳定隔离页进一步明确，Container 使用独立 namespaces 与资源上限，VM class 才有 pause／resume、fork、hot snapshots 等 VM 能力。Daytona 持久化默认保留身份和文件系统，stop／start 与保存内存的 pause／resume 不同；跨 sandbox 的共享卷又是另一层。创建同一个模板并不能证明没有把上一用户的文件带给下一用户。[隔离机制][daytona-isolation] [持久化层次][daytona-persistence]

网络也不宜写成单一默认值：稳定文档按账户 tier 区分 Internet 出站，Tier 1／2 受限，Tier 3 及以上开放；另可配置 block-all、CIDR 或域名名单。sandbox 间网络默认不共享，显式 linked sandboxes 是例外。preview 默认认证，`public` 可退出该认证。部署审查应读取实际 tier、sandbox 网络设置与 preview 策略，不从“私有 sandbox”推导所有方向都不可达。[网络隔离与 tier][daytona-isolation]

v2 文档入口已经将 Linux 写为 Firecracker microVM；然而稳定文档导航仍将 v2 标为 Alpha。本章把它单列为另一套版本证据，不对稳定版 Container 做架构升级推断。稳定 Linux VM 的具体 VMM、不同 class 在所有托管区域与自有 compute 部署中的实现一致性，本次未获得足够证明。[v2 文档][daytona-v2] [稳定版版本导航与 class][daytona-linux]

## 5. Cloudflare：Linux Sandbox 与 Workers／Wasm 是两种边界

### 5.1 Linux 路径：Worker 控制容器，但 Worker 不是容器本身

Cloudflare 当前文档直接说明：Container 的 image 作为 Linux container 在 Firecracker microVM 内运行，microVM 有独立 kernel 和 network。Linux sandbox 的控制对象是 Durable Object，Worker 通过名字访问它，Durable Object 启动或停止实例。应区分可信控制代码、Durable Object 的状态与运行 Linux 的 VM，不把三者画成同一个进程。[环境与隔离][cf-environments] [生命周期][cf-lifetime]

Durable Object 同名路由与存储可以持续，但运行实例结束时，进程和实例磁盘内容随之结束；下一次 start 是新实例。保存 workspace／snapshot 是另一项应用操作，而且当前文档中的部分自动保存能力标为 Beta。尤其容易遗漏的是：容器内部忙着跑测试，不算 Durable Object 活动；若控制对象不活跃，实例仍可能达到 inactivity timeout 而停止。[实例与对象生命周期][cf-lifetime]

安全文档还明确，部署 sandbox 中的 Linux 进程有 root 等价 capabilities，单纯换一个 Linux user 不能形成不可信用户之间的文件边界。同一个 sandbox 就是同一信任单元。当前 Container 默认 `enableInternet: false`，只有 Worker 出站 handler 截获的请求能够离开；handler 可在 sandbox 外附加 HTTPS 凭据。控制 Worker 必须限制目标与操作，并从认证身份推导 sandbox 名称，不能把用户提供的名字当成授权。[共享信任域、网络与凭据][cf-security]

### 5.2 Dynamic Worker／Wasm 路径：能力受限的代码环境，不是完整 Linux

Dynamic Worker 适用于生成代码只需调用一组已知方法的情况，例如筛选通过 scoped binding 返回的数据。其边界由 V8 沙箱与 Workers 进程级防护实现，不提供 Linux VM 的通用 shell、系统包与完整 kernel 接口。Workers 也支持 WebAssembly，但“Wasm 能执行代码”不能推出“能原样运行任意 Linux 仓库”。[环境选择][cf-environments] [Workers 安全模型][cf-workers-security] [Workers Wasm][cf-wasm]

也不能把 Dynamic Worker 默认当成无网络：当前安全页说明其继承 Worker 网络能力，加载时设置 `globalOutbound: null` 才使直接 `fetch()`／`connect()` 失败。binding 方法与允许的出站仍是权限入口。因此可以把两条路径组合起来：受限方法处理检索和组织数据，Linux Container 运行需要真实工具链的测试；这是一种基于公开能力的设计思路，不是所有应用都必须采用的产品推荐。[网络与 capability 入口][cf-security] [官方组合示例][cf-environments]

## 6. Vercel Sandbox：microVM 已明确，临时性却不是固定默认

官方概览明确每个 Sandbox 为 Firecracker microVM，并支持 Linux image、系统级工具及 SDK／CLI。控制 Sandbox API 的 OIDC／access token 是平台鉴权；guest 为外部 API 使用的 credential 是另一件事。不要因为应用部署在 Vercel，就假定 guest 应该拿到项目全部环境变量。[架构、镜像与鉴权][vercel-overview]

当前持久化在停止时保存文件系统，再从最近 snapshot 开始新会话；默认开启，可选 `persistent: false`。这保持的是持久名称和文件，不是证明原有进程、TCP 连接或内存会继续。旧 SDK 的 ephemeral 教程与当前 named／persistent 模型应按版本阅读。存储保留、删除与 fork 也需要自己的数据生命周期策略。[2026-05-26 持久化正式发布][vercel-persistence-release]

网络默认 `allow-all`，`deny-all` 明确包括 DNS；自定义策略默认拒绝，按域名／地址范围允许，也可运行中更新。官方还明确，firewall 位于 microVM 外的 host，凭据可在外部网络边界注入。这里不是“保存到 secret store 就不可读”，而是请求路径根本不把凭据值交给 guest。[Firewall 策略与限制][vercel-firewall] [边界实现说明][vercel-network-boundary]

仍需逐项验证协议、TLS、请求匹配和受允许 API 的操作范围：允许某域名，只限制能够去哪里，不必然限制能够在那里做什么。网络文档专门说明 hostname 与实际 virtual host 的区别。能够读取私有数据的代码仍可能把数据放进被允许的请求、日志或产物里；这些出口需要业务层约束，不是更换 microVM 品牌即可解决。[域名和请求规则][vercel-firewall]

## 7. Fly.io Machines：通用 VM 原语，不是自动完成的多租户沙盒系统

Fly.io 的官方架构明确采用 Firecracker；Machines API 让应用控制 VM 的资源、区域和生命周期。它适合构建自己的执行池或按任务创建 VM，但 API 的存在不等于已经提供租户队列、任务授权、产物审查或失败后的自动回收。后半部分是从低层 API 的职责推导出的应用工程责任。[平台架构][fly-architecture] [Machines 概览][fly-machines]

停止与 suspend 也不同：suspend 保存包含 memory／CPU 状态的 Firecracker snapshot，再启动可从该状态恢复；远端是否继续保持网络连接仍有条件。普通 root filesystem 被官方称为 ephemeral，不应用它作为持久数据契约。Fly Volume 是绑定特定服务器的本地存储，不是自动复制的分布式盘，官方明确要求应用负责复制并另做备份。[Suspend／resume][fly-suspend] [Volume 限制][fly-volumes]

网络和凭据往往比 VM 名称更决定安全边界。默认同 organization 的 apps 加入同一 6PN 私网，能互相通信；app secrets 在启动时作为环境变量进入该 app 的每台 Machine。因此，把多个不互信用户的 Machines 放在同一 organization／app，并给 app 放一个大权限 secret，不能称为“每台 microVM 互不相干”。应另行隔离私网和身份，或让凭据只通过可信中介用于受限操作。[6PN][fly-network] [App secrets][fly-secrets]

本次没有证明 Machines 自带一个适用于任意恶意 guest 的、默认 deny-all 的 L7 出站凭据代理。若需要这一安全属性，应查明网络隔离和代理的实际执行位置，不能用 VM 内可被代码修改的规则替代外部边界。

## 8. AWS Bedrock AgentCore：Runtime、Code Interpreter、Browser 分开读

### 8.1 Runtime 托管 agent，不会自动隔离同会话的 shell

默认 microVM 计算类型按 Runtime session 隔离，session ID 用于路由同一环境。`InvokeAgentRuntimeCommand` 与 agent invocation 操作同一会话、容器、文件系统与环境；因此“agent 是可信代码，但它在本 Runtime 里执行陌生脚本”没有自动新增一道工具 VM 边界。官方安全页还指出：AgentCore 不代应用强制 user-to-session 映射；持久文件系统中 permissions 被保存，但该会话内访问检查不按通常多用户权限方式强制执行。[会话与命令共用环境][aws-runtime-sessions] [安全注意事项][aws-runtime-security]

默认 compute 状态只在当前生命周期内存在；配置 Session storage 可跨停止保存指定目录，但当前仍为 Preview，存在 idle expiry 和版本更新重置语义。EFS／S3 Files 等 BYO 文件系统又可能跨多个会话共享。microVM 每会话隔离与共享存储的授权不是同一个问题，挂载同一数据源时仍需按业务身份限制数据访问。[Runtime 存储类型与边界][aws-runtime-storage]

Instances 类型则由 AWS 在客户账户中管理 EC2，可支持更长会话和多个 agent 共享实例。microVM 文档中的时限和边界不能直接套过去；所读 Instances 页面不足以证明每个协作 agent 都拥有独立 microVM。选型时必须把 compute type 写进配置和风险记录。[Instances 工作方式][aws-instances]

### 8.2 Code Interpreter 和 Browser 有各自的工具会话

Code Interpreter session 提供自己的计算环境和状态，Browser session 提供自己的浏览器环境；两者的会话文档都明确专属 microVM。它们各有 start／stop API、session ID 和工具资源，不是 Runtime 中的一段普通子进程。把陌生代码送给单独创建的 Code Interpreter，和直接在 Runtime shell 执行，是两种不同的信任拓扑。[解释器 session][aws-ci-sessions] [Browser session][aws-browser-sessions]

Code Interpreter 可选 `SANDBOX`、`PUBLIC`、`VPC`；其中 SANDBOX 文档仍明确允许 S3 访问，因此不是物理意义的无网络环境。Browser 基础页仍只列 public，但更新的共用 VPC 文档明确包括 Browser、Code Interpreter 与 Runtime。这里优先按完整 VPC 指南及 API 配置核验，而不复述旧概览的“只能 public”。是否完全禁止 DNS、互联网或其他 AWS 服务访问，不能只凭 mode 名字证明。[解释器模式][aws-ci-network] [三项服务 VPC 支持][aws-vpc]

会话内状态与数据留存也不能混为一谈：解释器文档同时说 session 结束后清理数据，又列 30 天的 session data TTL；Browser 页面也有 30 天 retention 与单独的 S3 recording。所读页面没有充分解释这些 retention 所覆盖的全部数据对象，本章不将其解读成“用户文件结束瞬间从所有备份和记录永久擦除”，也不解读成“可重新连接已结束会话”。[解释器留存描述][aws-ci-sessions] [Browser 录制与留存][aws-browser-sessions]

### 8.3 microVM 不替你隐藏执行角色凭据

AWS 官方凭据文档说明，配置 execution role 时，Runtime、Code Interpreter 和 Browser 的 VM 通过 MMDS 获得临时 AWS 凭据；任何能在 VM 内运行的代码或 actor 都可读取它们，而且该行为独立于网络 mode。Runtime 安全页再次明确了这个边界。因此，临时凭据不等于对 guest 不可见，独立 VM 也不等于角色可以拥有管理员权限。[凭据管理][aws-credentials] [Runtime 安全][aws-runtime-security]

合理的设计是：可信后端持有控制权限，不可信工具 session 只拿必要数据和最小执行角色；外部资源的写操作另做授权。AgentCore 在 VPC 中的 ENI、security group 与路由能够控制可达性，但“在 VPC 内”不保证出站已阻断；官方指南也说明访问 Internet 需要适当 NAT 配置。角色权限、网络和数据对象的范围要一起验收。[VPC 配置与网络方向][aws-vpc]

本次所读会话文档证明 microVM，但未指明这三项服务所有计算路径使用的具体 VMM。不要因名称 MMDS 或 AWS 与 Firecracker 的关联而补写“AgentCore 所有服务都一定是 Firecracker”。

## 9. Lambda 与 Fargate：编排宿主、任务执行器和 MicroVMs 是三个位置

### 9.1 Lambda Event Functions：事件调用，不是任意用户会话的 VM 控制台

传统 Lambda Event Function 按 handler／invocation 执行，由服务管理 execution environment 的初始化、冻结、复用与关闭；普通配置的单次调用上限为 15 分钟。函数 runtime 与 extensions 共用权限、凭据和资源。即使底层有 Firecracker，也不能认定每条用户消息都得到全新 VM，更不能让多个不互信用户默认共享一个带广泛权限的函数来执行任意脚本。[生命周期][lambda-lifecycle] [Event Function timeout][lambda-timeout] [底层执行环境][lambda-faq]

从任务拓扑看，Event Function 更适合做经过审核的短时协调步骤、鉴权或投递工作，再调用专用执行环境。这是架构推论，不是宣称 Lambda 没有能力执行代码。VPC 连接和 IAM 权限仍要配置；其中为网络配置赋给函数角色的权限，也可能由函数代码使用。[VPC 与权限][lambda-vpc]

也不把“15 分钟”推广到 Lambda 的所有功能：当前文档区分 Durable Functions 和 Managed Instances。Durable workflow 的长期存续不是同一台 guest 长期不间断运行的证明；Managed Instances 的并发与生命周期又不同。本章的上述定位限定为传统 Event Functions。[生命周期适用范围][lambda-lifecycle] [timeout 例外][lambda-timeout]

### 9.2 Lambda MicroVMs：当前已是独立的沙盒原语

截至研究日，官方已有 Lambda MicroVMs：以 Firecracker 提供 VM 边界，从预初始化 image 启动，可显式 suspend／resume／terminate，暂停保存 memory 与 disk；客户端通过专用 HTTPS endpoint 访问。这与 Event Function API 的 handler 调用和服务内部冻结不是一回事，应单独纳入平台清单。[Lambda MicroVMs 工作方式][lambda-microvms]

MicroVMs 默认出站可达 public Internet，可以用 VPC egress Network Connector；connector 在 run 时关联，运行中不能更换。入口 token 绑定具体 microVM、端口及有效期，shell 又有单独 token 和 connector。Build role 与 execution role 分开，execution role 可不配置。应用仍负责 image、授权、执行角色范围、暂停后的连接恢复及最终终止，不应把端口 token 当成应用操作的全部授权。[网络连接器][lambda-microvm-network] [角色与入口 token][lambda-microvm-security]

### 9.3 ECS on Fargate：以 task 为边界的托管容器执行

Fargate 文档明确，每个 task 具有独立边界，不与另一个 task 共享 kernel 或相关计算／网络资源。它可以承载自己实现的代码执行服务或一次性工作任务，但 agent 会话、产物传输、暂停恢复策略需要在 ECS／应用层设计；不要假定 Fargate task 自动实现 E2B SDK 那样的交互生命周期。[Fargate task 边界][fargate-overview]

兼容性不是“Dockerfile 能构建，所以一定能运行”：Fargate 不支持 `privileged` 等 task definition 参数，网络必须使用 `awsvpc`，Linux capabilities 也受限制。需要 Docker daemon、某些设备、挂载或内核控制的任务应先做兼容性验证。平台有版本维护／task retirement，长任务还要考虑中断和重试。[配置差异][fargate-config] [平台维护][fargate-overview]

IAM 还需区分给应用访问 AWS 的 task role 与用于拉镜像等平台工作的 task execution role；官方说明 task role 凭据会提供给 task 中的容器。把大权限 role 配给“隔离良好的 task”仍会放大 guest 内恶意代码的授权范围。Fargate 的公开 task 边界也不需要被未经来源支持地改写成“所有版本一定使用某一 VMM”。[Task role 与凭据][fargate-roles]

## 10. 补充：Docker Sandboxes 是具体产品，不是普通 Docker 的别名

当前 Docker Sandboxes 官方本地文档明确 microVM 信任边界，agent 在内部可 sudo，拥有独立 Docker daemon；workspace 可以不挂载、直接挂载，或使用 clone 模式。直接 mount 是宿主真实目录的读写通道，agent 改动立即影响宿主工作树；clone 模式把源仓库只读挂载，工作发生在 VM 内私有 clone。内部安装包、镜像和文件保留到删除 sandbox，不代表只要用了 VM 就不能修改宿主项目。[本地架构与持久化][docker-architecture] [安全边界][docker-security]

本地代理在 VM 外处理匹配请求的 authentication headers，MCP gateway 则是另一个跨边界入口。官方说明本地 stdio MCP servers 在 host 上执行，而非 sandbox VM 内。因此，配置一个能够操作宿主文件或调用云 API 的 MCP server，是显式增加 agent 能力，不能将其安全性归因给 microVM。[凭据与 MCP 集成][docker-security]

这两份页面明确限定本地模式，本章不将其存储、workspace 与凭据行为套到 Docker-managed cloud 模式，也不据此指定 hypervisor 品牌、所有 OS 的实现细节或成熟度。

## 11. 横向比较：状态与运营负担比“都是 VM”更有区分度

### 11.1 状态语义表

| 对象 | 本次确认的保存方式 | 使用时要另行管理 |
| --- | --- | --- |
| E2B | 默认 pause 保留 memory＋filesystem；可选 filesystem-only；当前 paused 状态不自动过期。[持久化][e2b-persistence] | 暂停数据回收、凭据失效、跨租户 template／snapshot 内容 |
| Modal | 文件／目录 snapshot 与 Alpha memory snapshot 分开，TTL 不同。[Snapshots][modal-snapshots] | snapshot 类型、保留期与 Alpha 接口依赖 |
| Daytona 稳定版 | stop／start 保存 filesystem；memory 操作按 VM class 支持。[Persistence][daytona-persistence] [class][daytona-isolation] | class、auto-delete／ephemeral 设置与共享卷 |
| Cloudflare Linux | Durable Object 身份／存储与 Container 实例寿命不同；实例结束丢失其进程与临时盘。[Lifetime][cf-lifetime] | workspace 保存、恢复及控制对象活动；不能用“同名”保证原实例 |
| Vercel | 默认停止保存 filesystem，再启动新 session；可显式不持久化。[正式发布][vercel-persistence-release] | 名称授权、snapshot 删除，不能当成 memory checkpoint |
| Fly Machines | suspend 有 VM 状态 snapshot；rootfs 不作为持久契约，Volume 为本地持久盘。[Suspend][fly-suspend] [Volumes][fly-volumes] | 复制、备份、节点绑定与冷启动回退 |
| AgentCore Runtime microVM | compute 默认临时；Preview session storage 或 BYO file system 单独保存文件。[Storage][aws-runtime-storage] | idle expiry、版本重置与共享挂载授权 |
| AgentCore Code Interpreter／Browser | 各自会话内有状态；结束 compute；recording／retention 是不同数据对象。[解释器][aws-ci-sessions] [Browser][aws-browser-sessions] | 会话停止、产物导出、日志／录制的留存范围 |
| Lambda Event Functions | 服务可冻结／复用环境；workflow 状态功能不等于用户可控 guest checkpoint。[Lifecycle][lambda-lifecycle] | 外部任务状态、幂等与调用重试 |
| Lambda MicroVMs | 用户可控 suspend／resume 保存 memory＋disk。[MicroVMs][lambda-microvms] | connector、image、入口 token 与终止回收 |
| Fargate task | 平台是 task／service 执行模型，不在本章认定其提供交互式 VM checkpoint。[Fargate][fargate-overview] | 会话服务、自行选配持久存储、任务重试与退休处理 |
| Docker Sandboxes 本地 | VM 内状态保存到删除；直接 mount 文件留在 host。[Architecture][docker-architecture] | 宿主工作树修改、磁盘增长与显式删除 |

### 11.2 责任分工表

以下是根据上文能力和接口推导的工程工作清单，不是厂商 SLA，也不表示其他产品没有某项能力。

| 交付层次 | 代表路径 | 平台承担的部分 | 项目必须完成的部分 |
| --- | --- | --- | --- |
| 托管交互执行环境 | E2B Cloud、Modal、Daytona Cloud、Vercel | 提供环境创建、执行及相关状态 API；具体功能按版本核验 | 身份与 sandbox 映射、镜像、出站和凭据规则、产物审查、配额／回收 |
| Worker＋受控执行环境 | Cloudflare Container／Dynamic Worker | 提供 Linux VM 或 Workers 隔离环境及控制接口 | Durable Object 生命周期、bindings 能力设计、网络 handler、workspace 保存与 preview 鉴权 |
| 通用 VM 原语 | Fly Machines、Lambda MicroVMs | 提供 VM 与网络／生命周期接口 | 多租户调度、可信执行代理、任务协议、资源授权与独立数据备份 |
| agent runtime＋独立工具 | AgentCore Runtime／Code Interpreter／Browser | 分别托管编排与工具会话；计算类型另分 | 不可信代码放置、三套会话关联、execution role、VPC、共享文件授权与记录留存 |
| 事件／容器任务计算 | Lambda Event Functions、ECS on Fargate | 托管 invocation 或 task 执行 | 拼装任务系统、交互 API、持久状态、重试和任务终止 |
| 自托管／本地 | E2B Embed、Docker Sandboxes 本地 | 提供软件栈和隔离接口 | 宿主／虚拟化能力、升级、磁盘与备份；本地还要控制 workspace 和 host-side MCP 能力 |

横向性能与成本比较应另立实验：固定 image、区域、CPU／memory、网络、初始缓存、是否恢复 memory、任务输入与并发，再分开计量“API 返回”“guest 可执行”“任务完成”和存储留存。没有这些条件，不引用某平台的单个启动数字作为排行榜。

## 12. 文档没有证明什么：保留为待核验项

| 未决项／错误推断 | 本章可证明到哪里 | 下一步应取得什么证据 |
| --- | --- | --- |
| Modal 的 gVisor＋microVM 叠层 | 当前明确是两种 runtime；未证明每条路径叠层。[Security model][modal-network] | 指定 runtime／backend 的第一方架构或供应商确认 |
| Daytona 所有版本都为 microVM | 稳定 Container 共享 kernel；稳定 Linux VM 与 v2 Firecracker 分开。[Linux][daytona-linux] [v2][daytona-v2] | SDK／API 版本、snapshot class、区域和实际部署类型 |
| E2B Embed 等于 Cloud 功能全集 | 最新 Runtime 有相关能力；Embed 发布说明的支持范围较窄。[Runtime][e2b-runtime] [Embed][e2b-embed-release] | 当前 Embed 制品、功能开关、外部依赖和支持矩阵 |
| AgentCore 各工具一定是 Firecracker | 各工具 microVM 有证据，具体 VMM 名称未由本次页面证明。[解释器][aws-ci-sessions] [Browser][aws-browser-sessions] | 明确到计算类型和版本的第一方底层架构 |
| Fargate 所有版本一定是 Firecracker | task 边界有证据，VMM 名称不在所读契约内。[Fargate][fargate-overview] | 指定 OS／platform version 的官方实现说明 |
| Code Interpreter `SANDBOX` 等于零网络 | 文档明确允许 S3；mode 名称不能证明 DNS 和全部路径阻断。[Network settings][aws-ci-network] | 当前完整协议／DNS 契约，以及实际 VPC 策略验证 |
| AgentCore Browser 只支持 public | 基础页与 VPC 指南存在范围差异；共用指南明确支持 Browser VPC。[基础页][aws-browser-sessions] [VPC][aws-vpc] | 目标区域、实际 Browser 配置及当前 API 支持 |
| AgentCore session 完结等于一切数据立即物理删除 | compute 结束、数据清理、30 天 TTL、S3 recording 是不同描述。[解释器][aws-ci-sessions] [Browser][aws-browser-sessions] | 各数据类别、备份、日志、录制及删除时限的明确定义 |
| Docker Sandboxes 本地架构可代表所有部署 | 所读两页明确限定本地；仅证明 microVM，不指定 VMM。[Security][docker-security] | cloud 对照文档及具体宿主平台实现 |
| 独立 VM 便已实现租户数据隔离 | Fly 私网／secrets、AgentCore MMDS、共享挂载都有额外边界。[Fly][fly-network] [凭据][aws-credentials] [Storage][aws-runtime-storage] | 租户级授权测试、共享资源清单、凭据／网络／日志验收 |

实践中不需要先把所有“未知”填成产品优劣。可以先提出必须满足的安全属性，例如“陌生测试代码不能读编排角色凭据”“只允许指定包源和受限工具 API”“文件可保存但每次运行都重建进程”；再要求对应的配置、版本与验收证据。下一章沿这些约束讨论选型与参考架构。

## 13. 来源小表：URL 与证据范围

所有链接在研究日实时查阅；可变文档和 `main` 分支可能继续更新。表中链接文字保留关键 URL 路径，完整地址也在文末引用定义中，便于合并专题来源账本。发布文章只用于其明确日期、实现描述和发布范围，不采用营销比较结论。

| 官方来源 URL | 本章使用的证据范围 |
| --- | --- |
| [github.com/e2b-dev/runtime][e2b-runtime]；[embed/compose/README.md][e2b-compose] | Firecracker、控制／数据面、单机自托管、KVM 和宿主前提；不是发行包功能全集证明 |
| [e2b.dev/resources/introducing-e2b-embed][e2b-embed-release] | 2026-09-30 Embed 的交付及当时不包含功能 |
| [docs.e2b.dev/sandbox/persistence][e2b-persistence]；[network/internet-access][e2b-network] | pause 的 memory／filesystem 区别、留存、默认出站与网络配置 |
| [e2b.dev/resources/introducing-e2b-secrets][e2b-secrets]；[introducing-e2b-workload-identity][e2b-identity] | guest 外 HTTPS 凭据／身份注入；Identity 发布日期为 2026-11-03 |
| [modal.com/docs/guide/sandboxes][modal-sandboxes]；[sandbox-networking][modal-network] | 两种 runtime、Linux 兼容性、GPU 限制、网络与默认授权；不证明叠层 |
| [modal.com/docs/guide/sandbox-snapshots][modal-snapshots]；[sandbox-secret-injection][modal-secret-injection] | snapshot 成熟度与 TTL；外部凭据注入 Beta |
| [daytona.io/docs/en/linux-sandboxes/][daytona-linux]；[isolation/][daytona-isolation]；[persistence/][daytona-persistence] | 稳定版 class、共享／独立 kernel、namespace、tier 网络与状态层次 |
| [daytona.com/docs][daytona-v2] | v2 Linux Firecracker 声明；Alpha 标签另由稳定版导航核验 |
| [developers.cloudflare.com/sandbox/concepts/][cf-environments]；[concepts/lifetime/][cf-lifetime] | Container Firecracker 与 Dynamic Worker 区别；控制对象和实例寿命 |
| [developers.cloudflare.com/sandbox/concepts/security/][cf-security] | 同 sandbox 信任域、root 等价能力、默认网络、外部凭据注入、名称授权 |
| [developers.cloudflare.com/workers/reference/security-model/][cf-workers-security]；[runtime-apis/webassembly/][cf-wasm] | Workers 安全模型及 Wasm 运行形式；不证明独立 guest kernel |
| [vercel.com/docs/sandbox][vercel-overview]；[changelog/sandbox-persistence-is-now-ga][vercel-persistence-release] | Firecracker、镜像、鉴权与默认文件系统持久化 |
| [vercel.com/docs/sandbox/concepts/firewall][vercel-firewall]；[blog/a-sandbox-without-a-network-boundary-is-only-half-a-sandbox][vercel-network-boundary] | 网络默认、DNS、请求规则、host 外部防火墙与凭据边界 |
| [docs.fly.io/reference/architecture][fly-architecture]；[machines/overview][fly-machines] | Firecracker 与 VM API 的职责 |
| [docs.fly.io/reference/suspend-resume][fly-suspend]；[volumes/overview][fly-volumes] | memory snapshot、rootfs 临时性、本地卷、复制和备份责任 |
| [docs.fly.io/networking/private-networking][fly-network]；[apps/secrets][fly-secrets] | 默认 organization 私网及 app-wide guest 环境变量凭据 |
| [AWS AgentCore runtime-sessions.html][aws-runtime-sessions]；[runtime-security-best-practices.html][aws-runtime-security] | 会话 VM、shell 同环境、用户映射责任、文件权限与凭据风险 |
| [AWS AgentCore runtime-filesystem-configurations.html][aws-runtime-storage]；[runtime-instances-how-it-works.html][aws-instances] | Preview session storage、共享 BYO 存储及 Instances 独立计算类型 |
| [AWS AgentCore code-interpreter-session-characteristics.html][aws-ci-sessions]；[browser-resource-session-management.html][aws-browser-sessions] | 各工具自己的 microVM session、状态、录制和不完全清楚的 retention |
| [AWS AgentCore code-interpreter-resource-management.html][aws-ci-network]；[agentcore-vpc.html][aws-vpc]；[security-credentials-management.html][aws-credentials] | 网络模式／VPC 与 MMDS 凭据可见性；网络不等于 IAM 授权 |
| [AWS Lambda FAQ][lambda-faq]；[lambda-runtime-environment.html][lambda-lifecycle]；[configuration-timeout.html][lambda-timeout]；[configuration-vpc.html][lambda-vpc] | Event Function 环境、复用／权限、调用限制及新计算模式例外 |
| [AWS Lambda lambda-microvms-guide.html][lambda-microvms]；[microvms-networking.html][lambda-microvm-network]；[microvms-security.html][lambda-microvm-security] | 独立 MicroVMs 产品、Firecracker、暂停／恢复、connector 与端口 token |
| [AWS ECS AWS_Fargate.html][fargate-overview]；[fargate-tasks-services.html][fargate-config]；[task-iam-roles.html][fargate-roles] | task 边界、配置兼容性、维护、应用和平台两类角色 |
| [docs.docker.com/ai/sandboxes/architecture/][docker-architecture]；[security/][docker-security] | 本地 microVM、workspace／clone、状态、代理及 host-side MCP；不代表 cloud |

### 简短续读清单

- E2B：[Runtime 仓库][e2b-runtime] 与 [Embed Compose 要求][e2b-compose]，看自托管真正要运营哪些组件。
- Modal／Daytona：[Modal Security model][modal-network] 与 [Daytona Linux class][daytona-linux]，练习从 SDK 名称追到实际隔离类型。
- Cloudflare：[环境选择][cf-environments] 与 [生命周期][cf-lifetime]，分清 Workers、控制对象和 Linux 实例。
- Vercel／Fly：[Sandbox Firewall][vercel-firewall] 与 [Fly 私网][fly-network]，核对 VM 之外的数据出口。
- AWS：[AgentCore Credentials][aws-credentials]、[Lambda MicroVMs][lambda-microvms]、[Fargate task roles][fargate-roles]，把执行隔离与业务权限分开。
- 本地 agent：[Docker Sandboxes Security][docker-security]，检查 workspace 和 MCP 穿过边界的能力。

[e2b-runtime]: https://github.com/e2b-dev/runtime
[e2b-compose]: https://github.com/e2b-dev/runtime/blob/main/embed/compose/README.md
[e2b-embed-release]: https://e2b.dev/resources/introducing-e2b-embed
[e2b-persistence]: https://docs.e2b.dev/sandbox/persistence
[e2b-network]: https://docs.e2b.dev/network/internet-access
[e2b-secrets]: https://e2b.dev/resources/introducing-e2b-secrets
[e2b-identity]: https://e2b.dev/resources/introducing-e2b-workload-identity
[modal-sandboxes]: https://modal.com/docs/guide/sandboxes
[modal-network]: https://modal.com/docs/guide/sandbox-networking
[modal-snapshots]: https://modal.com/docs/guide/sandbox-snapshots
[modal-secret-injection]: https://modal.com/docs/guide/sandbox-secret-injection
[daytona-linux]: https://www.daytona.io/docs/en/linux-sandboxes/
[daytona-isolation]: https://www.daytona.io/docs/en/isolation/
[daytona-persistence]: https://www.daytona.io/docs/en/persistence/
[daytona-v2]: https://www.daytona.com/docs
[cf-environments]: https://developers.cloudflare.com/sandbox/concepts/
[cf-lifetime]: https://developers.cloudflare.com/sandbox/concepts/lifetime/
[cf-security]: https://developers.cloudflare.com/sandbox/concepts/security/
[cf-workers-security]: https://developers.cloudflare.com/workers/reference/security-model/
[cf-wasm]: https://developers.cloudflare.com/workers/runtime-apis/webassembly/
[vercel-overview]: https://vercel.com/docs/sandbox
[vercel-persistence-release]: https://vercel.com/changelog/sandbox-persistence-is-now-ga
[vercel-firewall]: https://vercel.com/docs/sandbox/concepts/firewall
[vercel-network-boundary]: https://vercel.com/blog/a-sandbox-without-a-network-boundary-is-only-half-a-sandbox
[fly-architecture]: https://docs.fly.io/reference/architecture
[fly-machines]: https://docs.fly.io/machines/overview
[fly-suspend]: https://docs.fly.io/reference/suspend-resume
[fly-volumes]: https://docs.fly.io/volumes/overview
[fly-network]: https://docs.fly.io/networking/private-networking
[fly-secrets]: https://docs.fly.io/apps/secrets
[aws-runtime-sessions]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-sessions.html
[aws-runtime-security]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-security-best-practices.html
[aws-runtime-storage]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-filesystem-configurations.html
[aws-instances]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-instances-how-it-works.html
[aws-ci-sessions]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-session-characteristics.html
[aws-browser-sessions]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-resource-session-management.html
[aws-ci-network]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-resource-management.html
[aws-vpc]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-vpc.html
[aws-credentials]: https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/security-credentials-management.html
[lambda-faq]: https://aws.amazon.com/lambda/faqs/
[lambda-lifecycle]: https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html
[lambda-timeout]: https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html
[lambda-vpc]: https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html
[lambda-microvms]: https://docs.aws.amazon.com/lambda/latest/dg/lambda-microvms-guide.html
[lambda-microvm-network]: https://docs.aws.amazon.com/lambda/latest/dg/microvms-networking.html
[lambda-microvm-security]: https://docs.aws.amazon.com/lambda/latest/dg/microvms-security.html
[fargate-overview]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html
[fargate-config]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-tasks-services.html
[fargate-roles]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html
[docker-architecture]: https://docs.docker.com/ai/sandboxes/architecture/
[docker-security]: https://docs.docker.com/ai/sandboxes/security/

[专题导读](README.md) · [上一章：生命周期与编排](06-lifecycle-and-orchestration.md) · [下一章：选型与参考架构](08-selection-and-architectures.md)
