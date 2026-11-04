# 一手来源、版本与研究边界

研究与整理日期：2026-11-04。本页是来源台账，不是部署认证、最新漏洞情报或采购结论。正文事实链接到其所有者；原创例子、算术与架构另作标记。

## 研究怎么做的

从问题树出发，分别核对执行原语、运行时、编排、托管产品、网络／身份和生产验收。采用多轮在线检索、官方页面阅读、第一方代码说明与两个后台研究任务；主任务交叉核对了关键机制、平台版本差异和新旧文档冲突。

没有可调用的独立 Deep Research 产品入口，因此不声称已经运行该产品或获得其报告。没有以二手比较文章作技术事实依据，没有以搜索摘要替代所有关键机制的原文，也没有对全部项目做源码安全审计。

证据分四类：

| 类型 | 可以支持 | 不能支持 |
| --- | --- | --- |
| 官方机制／API 文档 | 项目定义、接口、公开边界、明确限制 | 某部署实际正确、无漏洞 |
| 第一方源码说明／固定代码 | 对应版本的实现结构或静态分支 | 完整协议正确、测试已经执行 |
| 官方发布记录 | 特定日期的能力与交付范围 | 其他版本／套餐同样适用 |
| 原创教学推导 | 决策问题、设计方向、算术与自测 | 厂商保证、实际容量与安全评级 |

## 执行原语与运行时来源

链接访问日期均为 2026-11-04；可变文档和主分支不冒充固定发行版。

| 主源 | 使用范围 | 不据此声称 |
| --- | --- | --- |
| [Linux seccomp BPF](https://docs.kernel.org/userspace-api/seccomp_filter.html) | 系统调用过滤、参数边界、不是完整 sandbox | 业务授权或全部信息流已解决 |
| [cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html) | 层级、资源控制、清理状态 | 所有文件／网络预算自动覆盖 |
| [Landlock](https://docs.kernel.org/userspace-api/landlock.html) | 进程自我限制、可叠加 LSM、内核／ABI 条件 | 老内核已有现行全部能力 |
| [Docker Engine 安全](https://docs.docker.com/engine/security/) | namespaces、daemon、capabilities、硬化 | 普通容器自带 guest kernel |
| [Docker rootless](https://docs.docker.com/engine/security/rootless/)、[默认 seccomp](https://docs.docker.com/engine/security/seccomp/) | 权限模型与过滤起点 | non-root、rootless 与 VM 同义 |
| [bubblewrap](https://github.com/containers/bubblewrap)、[nsjail](https://github.com/google/nsjail) | 轻量工具的积木与调用参数 | 自动提供租户编排与完善默认政策 |
| [gVisor 概述](https://gvisor.dev/docs/)、[架构介绍](https://gvisor.dev/docs/architecture_guide/intro/)、[安全模型](https://gvisor.dev/docs/architecture_guide/security/) | 应用内核、系统接口与信任范围 | 所有硬件攻击、网络与资源耗尽已消除 |
| [gVisor platforms](https://gvisor.dev/docs/architecture_guide/platforms/) | systrap 默认、ptrace 状态、KVM 进程模型 | 使用 KVM 就是普通 Linux microVM |
| [gVisor 兼容性](https://gvisor.dev/docs/user_guide/compatibility/)、[文件系统](https://gvisor.dev/docs/user_guide/filesystem/) | ABI 限制、设备例外、Gofer／directfs／LISAFS | 所有任务通用兼容或所有模式同一合同 |
| [Firecracker 设计](https://github.com/firecracker-microvm/firecracker/blob/main/docs/design.md)、[起步](https://github.com/firecracker-microvm/firecracker/blob/main/docs/getting-started.md) | KVM、VMM、guest、设备与宿主要求 | 自带完整 SaaS、任意宿主可用 |
| [Firecracker 生产宿主](https://raw.githubusercontent.com/firecracker-microvm/firecracker/main/docs/prod-host-setup.md) | jailer／seccomp、patch、网络与日志责任 | Firecracker 自己过滤全部网络 |
| [Firecracker snapshot 原文](https://raw.githubusercontent.com/firecracker-microvm/firecracker/main/docs/snapshotting/snapshot-support.md)、[仓库阅读入口](https://github.com/firecracker-microvm/firecracker/blob/main/docs/snapshotting/snapshot-support.md) | 状态集合、磁盘责任、唯一性、VMGenID、连接与兼容性 | CRC 是真实性证明、恢复保证 exactly-once |
| [Kata 虚拟化设计](https://github.com/kata-containers/kata-containers/blob/main/docs/design/virtualization.md) | CRI 到 VM、Pod 粒度、后端差异 | 每个 container 独立 VM |
| [QEMU 安全](https://www.qemu.org/docs/master/system/security.html) | 特权 monitor、支持的 accelerator／machine、后端边界 | 任意 TCG／machine 都提供同样安全保证 |
| [Cloud Hypervisor](https://www.cloudhypervisor.org/docs/prologue/introduction/) | 云工作负载 VMM 的公开定位 | 所有设备／迁移能力均适配本任务 |
| [crosvm 架构](https://doc.crosvm.dev/book/architecture/overview.html) | device 进程与 minijail 结构 | 一个现成 Agent SaaS |
| [libkrun README](https://github.com/containers/libkrun/blob/main/README.md) | 嵌入式虚拟化、平台范围与主分支注意事项 | 主分支等于稳定发行版 |
| [Wasmtime 安全](https://docs.wasmtime.dev/security.html)、[Config API](https://docs.wasmtime.dev/api/wasmtime/struct.Config.html) | Wasm imports、能力、fuel／epoch 和 host I/O | 任意 host function 安全或所有 I/O 自动超时 |
| [WASI](https://github.com/WebAssembly/WASI/blob/main/README.md) | Preview 1、WASI 0.2、当前 0.3 preview 的区分 | 所有 runtime 已稳定支持全部版本 |
| [Confidential Containers 信任模型](https://confidentialcontainers.org/docs/architecture/trust-model/trust-model/) | 宿主信任、测量、外部验证者、DoS／侧信道范围 | 应用目的正当、完全可用或一般性无侧信道 |

阅读 Wasmtime Config 时页面为 `51.0.0-dev` API 文档；这里只用其机制说明，不宣称该开发版是建议部署版本。libkrun README 的组织地址当前会重定向，主分支仍是可变入口；正文保留稳定分支选择提醒。crosvm 的旧 `google.github.io` 页面无法在本次浏览中访问，已改用当前官方 `doc.crosvm.dev` 架构入口。

## 编排、网络与身份来源

| 主源 | 使用范围 | 不据此声称 |
| --- | --- | --- |
| [Kubernetes Agent Sandbox](https://github.com/kubernetes-sigs/agent-sandbox) | CRD／controller、Template／Claim／WarmPool 与 runtime 委托 | CRD 本身实现内核隔离；roadmap 全部已交付 |
| [RuntimeClass](https://kubernetes.io/docs/concepts/containers/runtime-class/) | handler、调度、overhead、默认／失败行为 | YAML 会自动安装运行时 |
| [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) | 容器配置基线、sandboxed workloads 的适用边界 | 统一最优配置或已执行合规评估 |
| [NetworkPolicy](https://kubernetes.io/docs/concepts/services-networking/network-policies/) | CNI 依赖、L3／L4、叠加、节点与旧连接行为 | 域名、TLS、全部 L7 或标准日志能力 |
| [AWS IMDS options](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-options.html) | 双栈元数据、IMDSv2、hop limit | 其他云端点相同；IMDSv2 即任务授权 |
| [OWASP LLM01](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) | 外部内容、提示注入、最小权限和审批 | 所有提示注入可被 sandbox 消除 |
| [OpenShell 架构](https://docs.nvidia.com/openshell/about/architecture)、[安全建议](https://docs.nvidia.com/openshell/security/best-practices) | supervisor／gateway、各驱动围栏、L7／TLS 与例外 | 所有驱动都是 microVM 或相同强度 |
| [OpenShell inference](https://docs.nvidia.com/openshell/how-it-works/inference)、[policy schema](https://docs.nvidia.com/openshell/how-it-works/policies/schema) | 原生端点、profile／attachment、文件与 MCP 范围 | 旧全局路由仍适用；工具参数与返回值已全部检查 |
| [OpenShell proxy.rs 固定提交](https://raw.githubusercontent.com/NVIDIA/OpenShell/5d25211b25a8fc887e8d5c606d57d6ab22f1d76c/crates/openshell-supervisor-network/src/proxy.rs) | 目的地校验、凭证改写与不匹配拒绝的静态分支 | 已运行网络测试或完整源码审计 |

OpenShell 文档阅读基线为 `v0.1.7`；固定提交与动态页面分开记录。详细网络设计的双栈、重定向、broker、browser context、MCP、产物与日志要求多为**教学验收建议**，不把它们写成平台已经实现的完整能力。

## 托管与本地平台来源：按产品／版本分组

[平台章的来源小表](07-platform-landscape.md)列有 51 个官方链接的使用范围与引用定义。这里列出研究入口和最易跨范围误用的证据：

| 产品 | 第一方入口 | 版本／能力界限 |
| --- | --- | --- |
| E2B | [Runtime](https://github.com/e2b-dev/runtime)、[Embed Compose](https://github.com/e2b-dev/runtime/blob/main/embed/compose/README.md)、[Embed 发布](https://e2b.dev/resources/introducing-e2b-embed) | 当前源码能力与某 Embed 制品功能矩阵不同 |
| E2B 状态／身份 | [persistence](https://docs.e2b.dev/sandbox/persistence)、[network](https://docs.e2b.dev/network/internet-access)、[Secrets](https://e2b.dev/resources/introducing-e2b-secrets)、[Workload Identity](https://e2b.dev/resources/introducing-e2b-workload-identity) | pause 保存范围、默认联网、2026-11-03 身份发布；服务端仍需业务授权 |
| Modal | [Sandboxes](https://modal.com/docs/guide/sandboxes)、[security／network](https://modal.com/docs/guide/sandbox-networking)、[snapshots](https://modal.com/docs/guide/sandbox-snapshots)、[secret injection](https://modal.com/docs/guide/sandbox-secret-injection) | gVisor／VM 两条路径；memory Alpha 与凭证 Beta 不提升为全产品保证 |
| Daytona | [Linux](https://www.daytona.io/docs/en/linux-sandboxes/)、[isolation](https://www.daytona.io/docs/en/isolation/)、[persistence](https://www.daytona.io/docs/en/persistence/)、[v2](https://www.daytona.com/docs) | 稳定 `v0.227` Container／VM 与 `v2.0 Alpha` 分开 |
| Cloudflare | [环境](https://developers.cloudflare.com/sandbox/concepts/)、[lifetime](https://developers.cloudflare.com/sandbox/concepts/lifetime/)、[security](https://developers.cloudflare.com/sandbox/concepts/security/)、[Workers security](https://developers.cloudflare.com/workers/reference/security-model/)、[Wasm](https://developers.cloudflare.com/workers/runtime-apis/webassembly/) | Linux Container／Firecracker 与 Dynamic Worker／V8；1.0 与旧 0.x 语义另分 |
| Vercel | [Sandbox](https://vercel.com/docs/sandbox)、[持久化 GA 发布](https://vercel.com/changelog/sandbox-persistence-is-now-ga)、[firewall](https://vercel.com/docs/sandbox/concepts/firewall)、[网络边界](https://vercel.com/blog/a-sandbox-without-a-network-boundary-is-only-half-a-sandbox) | 默认持久化文件系统，不等于保存内存／进程 |
| Fly | [architecture](https://docs.fly.io/reference/architecture)、[Machines](https://docs.fly.io/machines/overview)、[suspend](https://docs.fly.io/reference/suspend-resume)、[volumes](https://docs.fly.io/volumes/overview)、[6PN](https://docs.fly.io/networking/private-networking)、[secrets](https://docs.fly.io/apps/secrets) | 私网、app-wide secrets、本地 Volume 与每 VM 边界不同 |
| AgentCore Runtime | [sessions](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-sessions.html)、[security](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-security-best-practices.html)、[storage](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-filesystem-configurations.html)、[Instances](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-instances-how-it-works.html) | microVM／Instances compute type；session storage Preview 与 BYO 挂载另分 |
| AgentCore 工具／凭证 | [Code Interpreter session](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-session-characteristics.html)、[Browser session](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-resource-session-management.html)、[CI network](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/code-interpreter-resource-management.html)、[VPC](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-vpc.html)、[credentials](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/security-credentials-management.html) | 分开的工具会话、网络模式与 MMDS；清理、TTL 与 recording 不等价 |
| Lambda Event Functions | [FAQ](https://aws.amazon.com/lambda/faqs/)、[lifecycle](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtime-environment.html)、[timeout](https://docs.aws.amazon.com/lambda/latest/dg/configuration-timeout.html)、[VPC](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html) | 传统 handler／invocation，不能推广到 Durable／Managed Instances |
| Lambda MicroVMs | [MicroVMs](https://docs.aws.amazon.com/lambda/latest/dg/lambda-microvms-guide.html)、[network](https://docs.aws.amazon.com/lambda/latest/dg/microvms-networking.html)、[security](https://docs.aws.amazon.com/lambda/latest/dg/microvms-security.html) | 独立生命周期 API、memory／disk 恢复、connector 和 token；不混成传统函数 |
| Fargate | [task 边界](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)、[task 配置](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-tasks-services.html)、[task roles](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html) | task 粒度、配置限制、任务与 execution roles，不指定未公开 VMM |
| Docker Sandboxes | [本地架构](https://docs.docker.com/ai/sandboxes/architecture/)、[安全](https://docs.docker.com/ai/sandboxes/security/) | 本地 microVM、workspace／clone、host-side MCP，不外推 cloud |

## 冲突、未知与版本漂移怎么处理

1. **Modal 叠层未知**：公开两种 runtime，不据此填入“每个实例都 gVisor＋microVM”。
2. **Daytona 版本不同**：稳定默认 Container 和 v2 Firecracker 单列，不跨版本代入。
3. **E2B Embed 交付范围**：旧发布限制与当前源码列表冲突时，不假装已审计当前制品。
4. **AgentCore 具体 VMM 未证实**：microVM 有证据，不能从 AWS 品牌推出某个 VMM。
5. **Browser 网络页面范围差异**：基础 session 页与共用 VPC 指南分开说明，部署再核 API／区域。
6. **清理／留存描述不完整**：计算结束、session data TTL、S3 recording、log 和备份另列，不推定物理擦除。
7. **旧 OpenShell 推理教程**：当前原生端点模型有迁移说明；升级需重新验收，不沿用旧路由结论。
8. **WASI／Landlock／主分支变化**：能力和内核／runtime 版本绑定，不自动外推到实际环境。

这些未知不是对产品的负面事实，而是本轮证据的边界。需求若依赖它们，应取得版本化第一方说明、合同、独立审计或实际 PoC。

## 本轮执行与未执行清单

已做：公开资料研究、章节写作、来源交叉核验、四张原创 SVG／PNG 机制图、三个本地标准库教学模型、文档／链接／导航／构建测试。

未做：独立 Deep Research 产品调用、购买服务、云账户访问、资源部署、容器／VM 启动、恶意代码运行、逃逸复现、硬件侧信道测试、GPU 验收、产品 SDK 账户级实验、真实身份或浏览器测试、数据删除验证、全源码审计及同条件跨平台 benchmark。

平台性能数字未组成排名；容量、时延候选与状态机为原创教学数据，不冒充论文／厂商／生产测量。附带代码不是安全组件；本地测试通过不等于执行边界已通过生产验收。

## 如何维护

产品更新后先记录原来与新基线的区别，再改正文、来源和测试。更新运行时不能只改一个版本号：platform、网络、文件系统、设备、快照与身份都可能变化。保持 unknown 与未测试清单，不因为方案需要完整表格就补猜答案。

图件沿用 Wiki 现有生成器，不访问绘图 API：

```bash
uv run --no-project --with cairosvg --with pillow python scripts/render_figures.py --embed --id-prefix agbox-
python3 scripts/render_figures.py --check --id-prefix agbox-
```

第一条仅用于重建图件，需要系统 Cairo 与中文字体；离线实验不依赖这些包。图是职责、状态和准入的原创示意，不是产品内部部署图或安全测试证据。

[专题导读](README.md) · [平台原始引用](07-platform-landscape.md) · [网络身份原始引用](09-network-identity-and-data.md) · [离线实验](lab.md)
