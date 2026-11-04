# Agent Sandbox 中英术语：接口、边界与状态

整理日期：2026-11-04。这是阅读辅助，不是行业统一定义或标准认证。机制定义见相应正文及[一手来源](sources.md)。

| 术语 | 本专题含义 | 常见混淆 |
| --- | --- | --- |
| Sandbox／沙箱 | 受政策约束的执行环境 | 不是一个固定运行时名称 |
| Execution boundary／执行边界 | 不可信程序到宿主／其他工作负载的限制面 | 不等于业务授权 |
| Agent runtime | Agent 控制循环的运行环境 | 不一定是陌生代码的隔离环境 |
| Control plane／控制面 | 管理生命周期、身份、政策与调度的可信组件 | 不应交给 guest 修改 |
| Data plane／数据面 | 实际执行、I/O 与请求路径 | 不代表所有内容可信 |
| OCI image | 软件与文件系统的打包／分发对象 | 不能从 image 判断最终隔离 |
| OCI runtime | 容器启动与执行规范的一层实现 | 不等于沙箱服务平台 |
| CRI | Kubernetes 与容器执行服务的接口 | 不等于 OCI 或 VMM |
| Namespace | Linux 资源视图／名称空间 | Kubernetes namespace 不是独立 kernel |
| cgroup | 进程层级与资源控制 | 不负责全部目录和 API 授权 |
| Capability | Linux root 权能的拆分项；另有泛义的被授予能力 | 同名概念需看上下文 |
| seccomp | 系统调用过滤约束 | 不分析完整业务语义 |
| LSM | Linux Security Module 框架 | 策略存在不等于已强制执行 |
| Landlock | 可叠加的进程自我约束机制 | 不等于任意旧内核均支持新 ABI |
| Rootless | daemon／容器按非 root 用户体系运行 | 不等于 VM |
| Sentry | gVisor 的应用内核 | 不是普通 Linux guest kernel |
| Gofer | gVisor 文件资源访问的组件 | 配置模式可能变化 |
| runsc | gVisor 的 OCI runtime 入口 | 不自带租户业务授权 |
| systrap | gVisor 借助 seccomp trap 的 platform | 不是独立沙箱服务 |
| KVM | Linux 的硬件虚拟化接口 | 不等于具体 VMM |
| VMM | 管理 vCPU、内存与设备等的组件 | 不等于 guest OS |
| Guest kernel | 虚拟环境内部的 kernel | 自身也需要 patch 与配置 |
| microVM | 精简的虚拟机路径 | 不是没有设备／内核／运维 |
| jailer | Firecracker 的宿主约束辅助程序 | 不是 guest 任务执行 agent |
| TAP | 宿主上的虚拟以太网接口 | 本身不是出站防火墙 |
| virtio | 虚拟化 I/O 的接口家族 | 各设备与后端安全范围不同 |
| vsock | guest／host 通信通路 | 不替代任务与业务授权 |
| MMDS／IMDS | microVM／实例元数据服务 | 不是同一个服务或权限政策 |
| RuntimeClass | Kubernetes runtime handler 选择与相关配置 | 不会自动安装节点 runtime |
| Pod Overhead | 运行时额外资源的调度核算 | 仍需要正确测量与申报 |
| Warm pool | 请求前准备的空闲实例池 | 不应包含前一个用户的身份 |
| Snapshot | 某层状态快照，必须注明文件／内存／设备 | 不等于应用事务提交 |
| Checkpoint | 可恢复的执行／应用状态 | 不保证外部副作用只执行一次 |
| Pause／Suspend | 暂停执行，保存范围按平台定义 | 不等于销毁或删除数据 |
| Clone uniqueness | 克隆恢复后唯一性重新建立 | 内核熵刷新不覆盖应用全部缓存 |
| VMGenID | guest 可感知 VM 世代变化的一种机制 | 不自动刷新所有应用 token |
| Generation | 实例代次，辅助拒绝旧句柄 | 客户端自报不成为可信身份 |
| Wasm | WebAssembly 模块／执行模型 | 不等于完整 Linux 环境 |
| WASI | Wasm 的系统接口体系 | 不同版本并不完全等价 |
| Isolate | 在进程／运行时中隔离执行上下文的模型 | 不等于每个上下文一台 VM |
| TEE | 可信执行环境，能力随硬件与模型不同 | 不保证应用无恶意或永远可用 |
| Attestation | 对环境／测量的证明与验证 | 不等于业务动作审批 |
| Credential broker | 在受控边界签发／代用业务能力 | 短 token 仍需精确范围 |
| Secret injection | 在特定请求路径附加真实秘密 | 环境变量注入是不同可见性 |
| Egress | 出站网络流量 | 允许域名不等于允许一切动作 |
| Ingress／Preview | 外部连接到任务服务的路径 | 随机 URL 不代替身份授权 |
| DNS rebinding | 目标解析变化导致校验与连接不一致的风险 | 域名 allowlist 不独立完成地址检查 |
| SSRF | 利用服务请求能力访问不应访问的目标 | 需要目标、解析和权限约束 |
| MCP | 工具／上下文交互协议 | 连接成功不证明参数或输出可信 |
| Artifact | 明确导出的产物 | 文件哈希不证明内容安全 |
| Fail-closed | 无法满足约束时拒绝 | 不等于自动换弱 runtime 跑通 |
| Cold／Warm／Restore | 冷启动／预热／恢复的不同起点 | 不能混合启动时间口径 |
| p95／p99 | 测量分布的分位数 | 不是最大值或默认 SLA |

## 读资料时的三个问法

遇到“sandbox”，问它是哪种 runtime 和谁配置政策；遇到“snapshot”，问保存了哪些对象、秘密和连接；遇到“secure”，问不可信主体、信任基础、覆盖项与实际证据。

同一个名字在不同版本或产品里可能对应不同语义。尤其 Linux Container／VM class、文件系统持久化／内存恢复、runtime session／tool session，应回到[平台章](07-platform-landscape.md)的明确范围。

[专题导读](README.md) · [学习路线](learning-roadmap.md)
