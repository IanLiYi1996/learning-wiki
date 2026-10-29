## 02 真实数据采集、标注与管理

<!-- illustration: robot-data-assets-3ca04c29d1 -->
![机器人日志怎样变成训练资产。记录容器、查看器、标注服务与训练清单承担不同职责。](../../images/robot-data-assets.png)

*图：机器人日志怎样变成训练资产。记录容器、查看器、标注服务与训练清单承担不同职责。*
<!-- /illustration: robot-data-assets-3ca04c29d1 -->

### 阶段工作与交付物

这一阶段把现场运行、遥操作示范和测试记录变成可查找、可复核、可交给训练与评测的资产。交付物应包括原始日志、相机与机器人标定版本、设备及软件版本、任务与事件标签、轨迹边界、数据权限，以及可重复生成的数据集清单。命令、实测状态和人工解释必须分开保存；日志浏览器能显示动作曲线，不意味着数据已经具有合格的机器人动作监督。

本章用五类证据描述公开状态：正式获取入口、官方文档或代码、客户自己的披露、供应商发布的客户案例、预览或研究示例。不同证据不能互换。“可商业访问”只表示官网明确提供商业入口，不表示本次已经签约或实测全部服务。以下状态统一核验至 **2026-10-27**；原始采集、审核标注、目录管理与训练样本整理的衔接是本章原创参考流程，不冒称某个客户的内部架构。

### Foxglove：多模态记录的查看、组织与协作平台

Foxglove 面向机器人日志的日常使用：接入相机、点云、位姿、曲线和文本记录，输出可共享的回放视图、事件和可检索录制集合。输入可以是 MCAP、受支持的 ROS 日志或实时数据；已有 ROS 系统可经 Foxglove Bridge 接入，自定义程序可使用 C++、Python、Rust SDK，把流写入 MCAP 或传到查看器。团队再通过 API、CLI、webhook 将录制与内部处理任务衔接。[平台文档](https://docs.foxglove.dev/docs)、[SDK](https://docs.foxglove.dev/docs/sdk)

获取形式包括桌面与浏览器应用；Data Platform 文档列出供应商托管、自有存储配合托管，以及客户自管数据平面，后一形式默认仍有供应商认证协调，不能直接称完全离线。[部署说明](https://docs.foxglove.dev/docs/data) 公开证据不仅有界面演示：Foxglove 披露 Dexory 的 MCAP 播放器集成，保留独立播放进程，同时向 Foxglove 与 ROS 2 输出数据。这个例子证明回放接口可接入既有软件栈，不证明整个仓库机器人生产系统由 Foxglove 管理。[Dexory 集成说明](https://foxglove.dev/blog/connect-foxglove-to-your-local-player-with-playback-control)

接口边界是记录、观察与数据组织。任务标签和导出结果仍需项目定义语义；不能把可视化、事件标记或在线连接当作自动校准、完整标注服务、控制安全认证或策略训练系统。

### MCAP：可独立采用的日志容器，不是云产品

MCAP 是保存带时间戳发布／订阅消息的开放容器格式，可承载不同序列化编码。其输入是消息、schema、channel 和辅助附件，输出是 `.mcap` 文件；索引、分块与压缩让读者按时间和主题定位记录，标定文件等上下文也可随附件保存。它与 Foxglove 有紧密生态关系，但使用 MCAP 不要求购买或接入 Foxglove Data Platform。[MCAP 规范](https://mcap.dev/spec)

接入方式是在采集程序或日志系统的写入层采用 MCAP 库，再由支持该格式的播放器、分析工具或转换器读取。项目必须保留消息定义和编码，分别解释记录时间、发布时间与消息内部采集时间；文件扩展名相同，不代表动作单位、坐标系和时钟已经一致。MCAP 项目提供公开规范和开源实现，是可直接取得的基础组件，而非只能通过销售演示访问的服务。[MCAP 项目](https://mcap.dev/)

公开使用证据可见 Dexory 的播放器集成：MCAP 被用来载入、回放并向 ROS 2 重发记录。这支持“已有机器人软件集成”的判断，不支持把 MCAP 说成自带数据审核、账号权限、机群分析或标注产能的管理平台。[集成范围](https://foxglove.dev/blog/connect-foxglove-to-your-local-player-with-playback-control) 格式保证的是如何装载消息，消息是否完整、可信、可用于训练仍由采集与审核流程负责。

### Rerun：代码优先的时空数据层与查看器

Rerun SDK 将多频率、多模态数据记录为带时间与实体路径的表示，输入包括图像、3D 几何、机器人状态和已有日志，输出包括 `.rrd` 记录、查看器视图、查询结果及派生数据层。Python、Rust、C++ 日志接口可嵌入算法；当前官方 SDK 页面还列出 MCAP／ROS 2 转换、SQL／dataframe 查询、目录服务和 PyTorch dataloader。接入并不要求机器人整体迁移：可先在现有处理程序中记录少量关键观测和结果，再建立共享 schema。[SDK 职责](https://rerun.io/sdk)

开源 SDK 与本地目录服务公开可取，查看器支持桌面、浏览器和 notebook。[公开代码](https://github.com/rerun-io/rerun) 商业 Rerun Hub 是对象存储之上的目录、索引与流式访问后端，当前产品页提供客户存储及商务接洽入口，具体部署与准入需确认；相关公告明确使用 private preview，本次未找到能够确认全面开放 GA 的声明，故不将 SDK 与 Hub 合并判断成熟度。[Hub](https://rerun.io/hub)、[发布公告](https://rerun.io/blog/data-layer-for-robot-learning)

官网列出 LeRobot 使用 Rerun 检查机器人数据与训练运行，属于公开开源集成证据，并不是客户量产披露。SDK 中新增处理、审核和训练接口也应按具体版本检查实验性标记。它帮助检查标签与组织派生层，但不会自动产生真实机器人命令，亦不替代人工审核制度。[公开集成](https://rerun.io/sdk)

### Scale Physical AI：数据采集与标注服务

Scale 的 Physical AI Data Engine 属于服务型数据供给：输入是机器人形态、任务、物体、环境和质量要求，也可涉及已有记录的丰富与标注；交付是定制采集的示范、多模态 grounding 注释及约定的数据集。官方介绍同时列出定制采集、标注和已有数据供给，不是仅售卖一个本地标注编辑器。[Physical AI 产品](https://scale.com/physical-ai)、[服务说明](https://scale.com/blog/physical-ai)

接入首先是与其工程、采集及运营团队确定数据规格、传感器配置、审核规则和交付验收，再进入本方目录与训练流程。官网提供联系入口，属于可商业接洽的服务；本次未核验到统一公开的机器人 episode SDK 或跨项目固定交付 schema，不能替供应商编造直接可调用的动作数据 API。托管、处理地域、权利范围与文件形式应以具体项目披露为准。

供应商公告列出 Physical Intelligence、Generalist AI 与 Cobot，并附有客户负责人对合作的表述。它能证明存在公开披露的数据合作及供应商采集业务，不能独立证明任一客户的部署规模、所有机器人任务的生产表现，亦不能把供应商公布的数据量当成跨产品性能排名。[公开合作范围](https://scale.com/blog/physical-ai) 尤其是人类示范和语义注释，不会自动成为某台机器人的可执行动作；命令层、重定向、时钟和机器人接口仍须在交付规格中明确。

### Roboto AI：日志检索、分析自动化与数据整理

Roboto 的职责是把机器人记录变成可查询的数据集、事件、统计结果和训练／评测候选片段。它读取 ROS、MCAP、PX4、Parquet 等受支持格式；输入经上传或自有存储桶接入，Python SDK、CLI 和 API 再连接分析代码。Actions 执行用户定义的后处理，Triggers 在条件满足时启动处理，Collections 组织筛选出的数据；这与简单打开单条日志的查看器不是同一交付层。[Roboto 文档](https://www.roboto.ai/docs)、[支持格式](https://www.roboto.ai/docs/learn/formats)

商业访问有明确证据：官网同时提供免费注册入口、付费方案，以及托管和客户 AWS 环境内 self-managed 形式。本次只核验公开入口，没有创建账户，也不保证任意地区或权限条件都能开通。无需凭融资或品牌印象推断它是“仅研究原型”，同样不能据官网扩展性表述认定其已经普遍大规模生产。[获取与部署](https://www.roboto.ai/pricing)

供应商的 BRINC 案例披露了飞行日志接入、自有 S3、Python 分析和出厂 QA 检查，属于明确任务范围内的客户应用证据；文中的效率数字属于该案例陈述，不外推到其他机器人。[BRINC 案例](https://www.roboto.ai/customers/brinc) 分析报告、AI 摘要和通过／失败标签不是独立安全结论；整理出的片段也需另行审核动作监督与数据使用权。

### 同类对照与交付衔接

下表整理本章已核验的职责，不比较性能或推荐采购。

| 产品／组件 | 主要交付层 | 获取或部署形式 | 交给下一阶段什么 | 不应混淆的边界 |
| --- | --- | --- | --- | --- |
| MCAP | 消息文件容器 | 开放规范、开源实现 | 原始记录、schema、附件与索引 | 没有自带云目录和标注产能 |
| Foxglove | 查看、协作与录制目录 | 桌面／浏览器，托管或自托管数据平台 | 回放视图、事件、筛选后的记录 | 查看与标记不等于完成动作标注 |
| Rerun SDK／Hub | 时空表示、查询及数据访问 | SDK 本地开源；Hub 联系获取 | `.rrd`、查询、派生层及数据读取接口 | SDK 可访问性不证明 Hub 已全面 GA |
| Scale Physical AI | 采集与标注供给 | 商业项目服务 | 约定规格的数据集与注释 | 项目交付接口不能假定统一 |
| Roboto AI | 日志分析、筛选和自动化 | 公开注册，付费托管／AWS 自管 | 事件、统计、Collections 和数据片段 | 案例中的 QA 使用不等于安全认证 |

一个可执行的组织方式是：先约定日志 schema 与权限，再选用记录容器；把事件审核与派生标签回写到目录，最后生成版本化训练清单。Foxglove、Rerun、Roboto 的接口可以衔接文件与处理脚本，但本章不宣称三者默认开箱互通。

### 实际读取的一手来源

- [Foxglove Documentation](https://docs.foxglove.dev/docs)、[Data Platform](https://docs.foxglove.dev/docs/data)：平台组件、录制、索引、协作与数据平面部署形式。
- [Foxglove SDK](https://docs.foxglove.dev/docs/sdk)：语言接口、实时流与 MCAP 写入。
- [Foxglove／Dexory PlaybackControl](https://foxglove.dev/blog/connect-foxglove-to-your-local-player-with-playback-control)：供应商披露的实际播放集成，仅用于该接口范围。
- [MCAP Specification](https://mcap.dev/spec)、[项目首页](https://mcap.dev/)：容器、schema、消息时间、索引和公开实现入口。
- [Rerun SDK](https://rerun.io/sdk)、[官方仓库](https://github.com/rerun-io/rerun)、[Hub](https://rerun.io/hub)、[Data Layer 发布说明](https://rerun.io/blog/data-layer-for-robot-learning)：分别核对公开 SDK、商业后端及预览／实验性标记；SDK 网页由直接 HTTP 读取，未执行代码。
- [Scale Physical AI](https://scale.com/physical-ai)、[服务发布说明](https://scale.com/blog/physical-ai)：采集与标注范围、联系入口及供应商披露的合作。
- [Roboto Documentation](https://www.roboto.ai/docs)、[Formats](https://www.roboto.ai/docs/learn/formats)、[获取与部署](https://www.roboto.ai/pricing)：注册、SDK、处理对象及商业部署形式；首页一次超时后改用文档与方案页。
- [Roboto／BRINC](https://www.roboto.ai/customers/brinc)：供应商客户案例，限定为飞行日志、诊断与 QA。以上均于 2026-10-27 核验。
