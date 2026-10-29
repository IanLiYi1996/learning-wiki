# GTC Berlin 2026：自动驾驶与车载边缘计算

核查截止：2026-10-26；大会窗口：2026-10-20—22。仅用完整的一手新闻稿、开发者资料、官方代码及伙伴声明；“宣布”“可下载”“量产”“商业运营”分别处理。来源编号对应文末原始 URL。

## 本次更新与技术机制

核心变化不是发布新的整车自动驾驶等级，而是把推理模型、数据生产和安全验证连接到欧洲合作项目。10月21日 NVIDIA 宣布 Alpamayo 2 Edge、Halos SAFE、Cosmos 3 Nano 新变体及 Alpamayo Agentic Factory。[S1]

Alpamayo 2 Edge 是基于 Cosmos 的20亿参数推理 VLA，针对 DRIVE AGX Thor 优化，设计运行频率为10Hz，用于车内场景理解与运动规划。开发者页解释其用自适应推理生成轨迹和因果说明，但仍标注 Coming Soon。同期博客明确：GitHub/Hugging Face 下载计划在“本月晚些时候”开放。因此本次是宣布，不是现场已可下载；本次核查也未证实权重已经开放。[S1][S2][S3]

机制上，既有 Alpamayo 开源栈将视觉、语言推理和动作预测联系起来，输出轨迹及因果推理链；官方 recipes 提供微调、强化学习和量化路径。AlpaSim/AlpaGym 的闭环让动作改变后续观测，暴露日志重放容易漏掉的累积错误。它们是开发工具，不是开源模型直接获得道路驾驶资格的证明。[S4]

本次 AlpaJudge 对驾驶解释评分，过滤薄弱标注；Foundation4D 无需 lidar 输入即可标注多摄像头视频，供感知训练及 NuRec 重建使用。Cosmos 3 Nano 新变体同步生成多视角相机与 lidar 数据，扩充天气、交通等长尾场景；NuRec 把真实记录重建为可交互仿真。Cosmos Data Factory 将视频和车辆信号变为可检索、标注的数据集；Agentic Factory 编排数据准备、后训练和仿真评估，预计2027年初开放，不是现成量产系统。[S1][S3]

## 硬件、命名与安全边界

不要把 Thor、DRIVE AGX、Hyperion 和 DRIVE AV 当成同一产品：Thor 是车规计算芯片，DRIVE AGX 是开发计算平台，Hyperion 是计算与传感器参考架构，DRIVE AV 是驾驶软件。2026年9月官方说明 DRIVE Hyperion 已更名为 NVIDIA Hyperion；9月背景文章明确写 Hyperion 10 与双 Thor，没有证实本次存在 Hyperion 11。[S3][S6][S9]

可确认的背景规格：单 Thor 官方规格表列最高1000 INT8 TOPS、64GB LPDDR5X、273GB/s；2025年开发者正文另列2000 FP4 TFLOPS。必须保留精度和“最高”口径，不能视为整车持续有效算力，也不据双芯片自行外推本次新系统性能；这些不是 Berlin 新发布的芯片规格。[S5][S5a]

安全需分层。DRIVE AV 的端到端 AI 与经典安全栈并行，提供冗余；Halos 跨硬件、系统软件、算法及验证。[S9] 本次新增 Halos SAFE 将需求转成场景、测试和可追溯指标证据，连接仿真、SIL/HIL、实车测试及车队监控。官方技术说明以运行设计域为安全论证起点，区分 L2 主动安全与 L4，不能以一个模型解释或仿真分数替代整车安全论证。[S7]

技术判断：推理链提升可检查性，生成数据扩充覆盖，但两者都不自动保证驾驶动作正确。SAFE 本身也讨论仿真保真度、过拟合和串联工具的误差；安全证据必须覆盖目标运行环境、残余风险和上线后的监控。应把芯片/操作系统功能安全、开发过程审核、具体车辆验证与运营许可分开，不能由前两者直接推导后两者。[S7][S9]

dSPACE 10月21日一手声明确认展示了 SAFE＋NuRec 的 SIL/HIL 集成，并支持自动执行 Euro NCAP 测试；这证明协议相关验证工作流，不证明 Euro NCAP 与 NVIDIA 新签合作或授予 L4 认证。[S8] CLA 的“2025最佳表现车型”是 Euro NCAP 在2026年1月公布的历史安全评价，不是本次新增合作。[S10] 未找到名为“Alpamayo Safety Toolkit”的可核验一手发布；应使用已证实的 Halos SAFE 名称。

## 伙伴、车型与部署成熟度

Mercedes-Benz：扩大 Hyperion、Alpamayo Stack、Halos 合作已于10月16日宣布，包含未来 L4 研发。[S11] 10月21日德国城市点到点 MB.DRIVE ASSIST PRO 明确为 SAE L2，驾驶员仍负责；订购计划为2027年上半年，具体车型和价格待公布，不能写成德国已无人驾驶。[S12] S-Class＋DRIVE AV 的 L4-ready/Uber 项目早在1月29日介绍，措辞是未来 robotaxi，非本次商业落地证明。[S13]

奔驰另计划2026年底向斯图加特和慕尼黑部分合资格客户提供 OTA 早期体验，不等于已经全德国开放。该 L2 原稿列27个传感器和最高254 TOPS，但没有点名 Thor；不能把双 Thor 的参考架构规格套给这套辅助驾驶系统，也不能由传感器数量判定它是 L4。[S12]

Bolt/Lucid：本次选择 Alpamayo Stack，目标支撑至少25,000辆 L4-ready 未来 Lucid 车辆；2027年马德里先采集道路数据，须监管批准。本次声明没有给出具体车型或无人商业载客启动日；软件选择、硬件准备与已部署 L4 车队不能划等号。Bolt 自有页面标10月22日但正文未完整呈现，关键事实取其署名发布的10月21日 Cision 原稿。[S14][S14a]

Uber：本次原稿确认共同开发 Cosmos 数据工厂，未新增可核验的车型或运营日期。双方数据工厂方向在2025年10月28日 Uber 原稿已出现，不能整体算作 Berlin 首次宣布。[S1][S15]

Bosch/Continental：未找到本次汽车合作的一手新声明；不能按提示补入新增名单。Bosch 的 Hyperion ECU 属2026年1月 CES 生态背景；Continental、Aurora、NVIDIA 的 Thor/DriveOS L4 卡车合作属2025年1月，原计划2027年量产，不能以该计划证明如今已量产该版本。[S16][S17] 本次原稿另列 Volvo Cars、Volkswagen Commercial Vehicles、Einride，以及 Aptiv、Valeo、Schaeffler；其具体成熟度需按各项目核查，不统一称“已经 L4 商用”。[S1]

结论：可信进展是更小的车载推理模型、生成数据/闭环仿真与可审计安全证据链，以及欧洲项目的软硬件适配。未核实项包括 Hyperion 11、Alpamayo Safety Toolkit、Euro NCAP 本次直接新合作、Bosch/Continental 本次新增汽车合作及各计划的全面无人商业运营。“未找到”不等于断言不存在。

## 一手源表

无发布日期的滚动文档按2026-10-26访问状态记录；历史稿不得当作本次发布。

| 编号 | 标题 | 发布日期／性质 | 原始 URL |
| --- | --- | --- | --- |
| S1 | European Mobility Leaders Build Safe Vehicles and Robotaxi Fleets on NVIDIA Hyperion | 2026-10-21／本次 | https://nvidianews.nvidia.com/news/european-mobility-leaders-build-safe-vehicles-and-robotaxi-fleets-on-nvidia-hyperion |
| S2 | NVIDIA Open Models Advance Europe’s Sovereign Intelligence Across Industries | 2026-10-21／本次、开放时间 | https://blogs.nvidia.com/blog/open-models-europe-industry/ |
| S3 | Autonomous AI Solutions | 无发布日期／开发者滚动页，访问2026-10-26 | https://developer.nvidia.com/drive |
| S4 | NVIDIA Alpamayo Developer Hub | 无发布日期／官方代码 README，访问2026-10-26 | https://github.com/NVlabs/alpamayo-recipes |
| S5 | DRIVE AGX Developer Kits | 无发布日期／规格，访问2026-10-26 | https://developer.nvidia.com/drive/agx |
| S5a | Accelerate Autonomous Vehicle Development with the NVIDIA DRIVE AGX Thor Developer Kit | 2025-09-03／背景，正文规格表 | https://developer.nvidia.com/blog/accelerate-autonomous-vehicle-development-with-the-nvidia-drive-agx-thor-developer-kit/ |
| S6 | Physical AI Takes the Wheel: How the World’s Robotaxi Leaders Are Building With NVIDIA Technologies | 2026-09-10／背景 | https://blogs.nvidia.com/blog/robotaxi-leaders-full-stack-open-platform/ |
| S7 | Our Architecture — NVIDIA Halos Safety Assurance Framework for Evaluation | 无发布日期／安全技术说明，访问2026-10-26 | https://docs.nvidia.com/halos-safe/technical-brief/our-architecture |
| S8 | From Sensor Data to Simulation | 2026-10-21／dSPACE本次声明 | https://www.dspace.com/en/pub/home/news/dspace_pressroom/press/from-sensor-data-to-simulation.cfm |
| S9 | NVIDIA DRIVE AV Raises the Bar for Vehicle Safety as Mercedes-Benz CLA Earns Top Euro NCAP Award | 2026-01-22／背景；含9月更名编者注 | https://blogs.nvidia.com/blog/drive-av-mercedes-benz-cla-euro-ncap-safety-award/ |
| S10 | Euro NCAP names Best-in-Class cars tested in 2025 | 2026-01-14／Euro NCAP背景 | https://www.euroncap.com/press-media/euro-ncap-names-best-in-class-cars-tested-in-2025/ |
| S11 | Mercedes-Benz and NVIDIA expand strategic partnership to advance safe highly automated driving in the next decade | 2026-10-16／会前伙伴声明 | https://group.mercedes-benz.com/company/news/mb-and-nvidia-expand-strategic-partnership.html |
| S12 | Mercedes-Benz first to bring point-to-point driving to Germany | 2026-10-21／同期伙伴声明 | https://group.mercedes-benz.com/technology/autonomous-driving/driving/point-to-point-navigation.html |
| S13 | Mercedes-Benz Unveils New S-Class Built on NVIDIA DRIVE AV, Which Enables an L4-Ready Architecture | 2026-01-29／背景 | https://blogs.nvidia.com/blog/mercedes-benz-l4-s-class-drive-av-platform/ |
| S14 | Bolt picks NVIDIA Alpamayo Stack to drive its autonomous vehicles across Europe | 2026-10-21／Bolt署名原始发布 | https://news.cision.com/bolt/r/bolt-picks-nvidia-alpamayo-stack-to-drive-its-autonomous-vehicles-across-europe,c4412935 |
| S14a | Bolt picks NVIDIA Alpamayo Stack to drive its autonomous vehicles across Europe | 2026-10-22／Bolt自有页，正文提取不完整 | https://bolt.eu/en/blog/alpamayo/ |
| S15 | Uber to Deploy One of the World’s Largest Networks of Autonomous Vehicles, Powered by NVIDIA AI Architecture | 2025-10-28／伙伴背景声明 | https://investor.uber.com/news-events/news/press-release-details/2025/Uber-to-Deploy-One-of-the-Worlds-Largest-Networks-of-Autonomous-Vehicles-Powered-by-NVIDIA-AI-Architecture/default.aspx |
| S16 | NVIDIA Expands Global Hyperion Ecosystem to Accelerate the Road to Full Autonomy | 2026-01-05／CES背景 | https://blogs.nvidia.com/blog/global-drive-hyperion-ecosystem-full-autonomy/ |
| S17 | Aurora, Continental, and NVIDIA Partner to Deploy Driverless Trucks at Scale | 2025-01-06／CES背景，日期可由原稿Business Wire链接核对 | https://ir.aurora.tech/news-events/press-releases/detail/112/aurora-continental-and-nvidia-partner-to-deploy-driverless-trucks-at-scale |
