## 03 场景建模、数字孪生与物理仿真

### 阶段工作与交付物

场景工程把 CAD、机器人描述、现场测量、设备配置及流程要求变成可执行的虚拟试验环境。交付物不只是三维画面，还包括机器人和工装模型、碰撞与传感器配置、控制接口、版本化测试场景，以及离线程序、验证报告或训练用环境。数字孪生还需绑定具体真实对象、参数来源和更新记录，不能仅凭模型外观宣布已与实物一致。

本章区分三种工作：工业单元的离线编程与虚拟调试、机器人软件／学习环境的闭环测试、汽车虚拟试驾。它们可以交换部分资产，却不是同一个交付物。以下“获取、支持、客户案例、研究”的描述均按 **2026-10-27** 可读的一手资料标注；有文档和开源发行的组件不被自动归为“不成熟”，商业客户案例也不被外推成通用 AI 或安全认证。

### ABB RobotStudio：围绕 ABB 控制器的离线工程环境

RobotStudio 用于机器人单元布局、运动验证、程序编写和现场调试前的离线检查。输入是机器人配置、工装／几何、目标路径及程序，输出是可复用的工作站模型、ABB 机器人程序和运动、节拍等检查结果。其关键接口是 ABB Virtual Controller：使用真实控制软件对应的程序与配置进行虚拟执行，而不是只播放手绘动画。随后由工程流程将验证后的程序与配置接到实际控制器。[Desktop 职责](https://www.abb.com/global/en/areas/robotics/products/software/robotstudio-suite/robotstudio-desktop)

获取形式包括 PC 桌面软件和商业许可；Suite 官网还列出云协作、路径规划和程序辅助，许可页说明浮动许可及离线借用。各模块的适用条件应按具体许可核对，不能把“云许可”理解成所有计算都在浏览器中完成。[Suite](https://www.abb.com/global/en/areas/robotics/products/software/robotstudio-suite)、[许可形式](https://www.abb.com/global/en/areas/robotics/products/software/robotstudio-suite/robotstudio-license)

ABB 历史 Evolut 案例披露了布局、夹具检查、节拍验证和离线程序编制，构成工业工程使用证据，但不是 2026 年部署规模统计。[Evolut 案例](https://library.e.abb.com/public/646aec8533a54008887d8b4146bb1d1a/rs_casestudy_evolut_en_web.pdf) 产品中的 AI Assistant 或自动路径规划不把它变成通用机器人智能；现场标定、工艺验收和安全措施仍在软件接口之外。

### Siemens Tecnomatix Process Simulate：产线过程与虚拟调试

Process Simulate 面向制造过程的三维验证，输入是设备和产品几何、布局、机器人动作、工艺顺序及控制逻辑；输出是制造研究模型、离线程序、节拍／碰撞检查和虚拟调试结果。接入通常围绕生产单元建模，再连接真实或仿真的 PLC 逻辑；它覆盖机器人、人工操作与产线事件，不等同于统计生产物流的 Plant Simulation，也不是一套通用强化学习环境。[当前产品目录](https://www.siemens.com/en-us/products/tecnomatix/offerings/)

官方提供商业产品和 Process Simulate X 订阅形态，X 的发布说明涉及云协作、授权和部署管理。当前目录与历史发布中的模块命名已有差别，不能根据旧文章把模块组合当成当前固定报价。Tecnomatix Connector 可向 Omniverse 传递几何及仿真内容，接口目的主要是资产衔接和可视化协作，不表示两个求解器自动产生一致物理结果。[X 与连接器说明](https://blogs.sw.siemens.com/tecnomatix/introducing-process-simulate-x-digital-manufacturing-powered-by-cloud-technologies/)

Siemens 的 Ingemat 案例披露该工程公司将 Process Simulate 用于机器人仿真和虚拟调试，任务涉及汽车自动化工程；这是供应商客户案例，不能泛化成所有工厂的产量提升。[Ingemat](https://blogs.sw.siemens.com/tecnomatix/ingemat-a-virtual-commissioning-success-story/) 仿真交付仍依赖模型、控制代码和接口映射，不能代替真实设备的工艺及安全验收。

### Isaac Sim：机器人场景、传感器与软件闭环的平台

Isaac Sim 将机器人与环境资产、物理运行、传感器输出和外部机器人软件连接在同一场景中。输入可来自 URDF、MJCF、CAD 或 USD，输出包括仿真状态、相机／其他传感器数据、合成数据及测试记录。工程接入可使用 Python、Kit 扩展和 ROS 2；学习任务通常进一步接 Isaac Lab，而不是把 Isaac Sim 本体称作已训练策略。[固定 6.0.0 文档](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/)、[官方代码](https://github.com/isaac-sim/IsaacSim)

公开源码、发行与文档入口均可访问，官方说明涵盖工作站、容器和 Python 工作流。本文固定文档版本用于复查接口，不宣称其为最新版本；源码、Kit、第三方依赖和资产的授权须分别核对，不能把“代码开放”解读为所有内容无条件再分发。

NVIDIA 的 AWS 早期采用公告将 Amazon Robotics 的 Proteus 传感器仿真列为使用方向，是供应商披露的开发应用，不证明真实机群的策略均经该平台训练或已通过安全认证。[采用披露](https://blogs.nvidia.com/blog/gpu-aws-omniverse-isaac-sim-robots/) USD 是场景表示，物理与传感器计算由所配置后端完成；模型外观、碰撞代理与控制时序需单独核验，跨版本也不能默认兼容。

### MuJoCo：可嵌入程序的动力学与接触仿真器

MuJoCo 的交付中心是动力学计算，而非工厂数据管理或 PLC 工程。输入是 MJCF、受支持的 URDF、执行器与环境参数以及每步控制输入，输出是状态、接触、力和传感器结果。接入方式是在 C／C++ 或 Python 程序中装载模型并运行仿真，再把读写接口封装给控制、优化或训练代码；MJX 等计算路径需要按自身支持范围检查，不能仅替换名称便认为结果与性能完全相同。[官方仓库](https://github.com/google-deepmind/mujoco)

项目提供开源代码、版本化二进制和 Python 接口，属于正式公开可取得、有文档的基础软件，不因没有云销售页面而被归为演示产品。具体模型、任务库、数据记录和实验调度由上层负责；模型库也不能代替对真实机器人的参数标定。

Google DeepMind 的 MuJoCo Playground 提供运动控制、操作和 sim-to-real 研究环境，是官方可执行代码及研究示范的证据；本次没有将其当作具名客户的量产报告。[Playground](https://github.com/google-deepmind/mujoco_playground) 接口边界尤其在执行器和接触假设：相同几何模型并不保证相同真实执行效果，仿真步进接口也不是工业机器人可直接加载的生产程序。

### Gazebo：面向机器人软件集成的模块化仿真栈

Gazebo 接收机器人和世界描述、插件、传感器配置及控制消息，输出仿真状态、传感器流和测试记录。项目以版本化库组合提供物理、渲染、传感器和 transport 能力；SDF world 组织场景，机器人模型和插件定义行为。接 ROS 2 时，经 `ros_gz` bridge 映射消息类型与方向，而不是所有 Gazebo topic 自动成为 ROS topic。[ROS 2 集成文档](https://gazebosim.org/docs/harmonic/ros2_integration/)

获取形式是公开源码和发行包，可在本地用 GUI 查看，也可由测试程序驱动服务端。官方支持表列有 Harmonic、Jetty 等 LTS，须按 ROS 发行与插件兼容性确定组合；Gazebo Classic 已在 2025 年结束生命周期，不能把它与当前 Gazebo 的支持状态混写。[发行及支持表](https://gazebosim.org/docs/latest/releases/)、[Classic 状态](https://classic.gazebosim.org/)

Open Robotics 披露 Gazebo 用于 DARPA SubT 虚拟赛道，证明复杂多机器人场景与测试基础设施的实际使用，证据类型是研究竞赛，不是商业机群量产。[SubT 披露](https://www.openrobotics.org/blog/2021/9/27/darpa-subt-final-competition) 传感器、物理引擎和插件各有支持边界；ROS 消息连接成功，也不意味着时钟、坐标、控制动态和实机表现都已一致。工程交付还应固定场景、插件与桥接配置，让回归任务能够重复运行，而不只是交付运行截图。

### 汽车分支：CARLA 与 IPG CarMaker

**CARLA** 的核心是自动驾驶研究场景：道路、交通参与者、天气和传感器配置进入仿真服务端，Python／C++ 客户端控制场景并接收图像、雷达等数据。它提供公开代码与资产，采用客户端／服务端架构，适合构建研究、训练和测试用场景；本次依据官方介绍确认可访问性与接口，没有据社区普及度宣称任何整车项目已完成量产验证。[CARLA](https://carla.org/)、[架构说明](https://carla.readthedocs.io/en/latest/start_introduction/)

**IPG CarMaker** 围绕车辆虚拟试驾和控制软件测试，输入包括车辆模型、道路、驾驶／交通及测试定义，输出是试验运行和评估结果。官方商业产品明确覆盖 MIL、SIL、HIL、VIL，即模型、软件、硬件和整车在环；产品形态涉及 PC、无界面运行、云及台架集成。本次核验了正式产品与接口说明，未核验特定客户当前生产规模。[CarMaker](https://www.ipg-automotive.com/solutions/product-portfolio/carmaker) 它不是机械臂离线编程工具，也不能凭在环接口宣称整个自动驾驶功能已获安全批准。

### 同类别对照与交付衔接

| 产品 | 主要验证对象 | 核心接入与输出 | 本次证据层级 | 不能默认替代 |
| --- | --- | --- | --- | --- |
| RobotStudio | ABB 机器人单元及程序 | Virtual Controller → 工作站与机器人程序 | 商业入口、文档、历史供应商客户案例 | 通用 AI、现场标定与安全验收 |
| Process Simulate | 制造过程及控制逻辑 | 三维研究／PLC 连接 → 离线程序与虚拟调试 | 商业目录、X 发布、Ingemat 案例 | 物流仿真或通用策略训练 |
| Isaac Sim | 场景、传感器及机器人软件栈 | USD／Python／ROS 2 → 观测、状态、数据 | 官方源码／文档、早期采用披露 | 已训练策略和实机保证 |
| MuJoCo | 动力学、接触与控制／学习环境 | 模型／代码调用 → 状态、力、传感器 | 正式开源发行、官方研究环境 | PLC 工程与产线管理 |
| Gazebo | 机器人软件及插件集成 | SDF／插件／ROS bridge → 多种传感器流 | 支持表、文档、研究竞赛 | 自动完成时序及参数校准 |
| CARLA | 道路交通与自动驾驶研究 | 客户端 API → 场景和传感器结果 | 公开平台、代码和文档 | 车辆量产或法规合规结论 |
| CarMaker | 车辆与控制系统在环测试 | 虚拟试驾／台架接口 → 试验评估 | 正式商业产品及接口说明 | 通用机器人场景工程 |

本章原创衔接原则是：先确认最终交付是工业程序、测试报告还是训练环境，再建立资产与接口版本清单；模型转移后逐项核对几何、控制和传感器语义。可交换 CAD、USD 或日志，不等于可以直接互换控制器、物理求解器和验收结论。

### 实际读取的一手来源

- [ABB RobotStudio Desktop](https://www.abb.com/global/en/areas/robotics/products/software/robotstudio-suite/robotstudio-desktop)、[Suite](https://www.abb.com/global/en/areas/robotics/products/software/robotstudio-suite)、[License](https://www.abb.com/global/en/areas/robotics/products/software/robotstudio-suite/robotstudio-license)：虚拟控制器、产品职责与许可形式。检索工具读取成功，随后直连复测超时，未反复重试；软件及账户未实测。
- [ABB／Evolut PDF](https://library.e.abb.com/public/646aec8533a54008887d8b4146bb1d1a/rs_casestudy_evolut_en_web.pdf)：实际读取两页；2004 年历史供应商案例，只用于离线工程任务范围，不表示当前部署统计。
- [Siemens 当前产品目录](https://www.siemens.com/en-us/products/tecnomatix/offerings/)、[Process Simulate X 发布](https://blogs.sw.siemens.com/tecnomatix/introducing-process-simulate-x-digital-manufacturing-powered-by-cloud-technologies/)：产品模块、获取形态和 Omniverse 连接器；模块命名须以当前目录为准。
- [Siemens／Ingemat](https://blogs.sw.siemens.com/tecnomatix/ingemat-a-virtual-commissioning-success-story/)：机器人仿真与虚拟调试案例。
- [Isaac Sim 6.0.0](https://docs.isaacsim.omniverse.nvidia.com/6.0.0/)、[官方仓库](https://github.com/isaac-sim/IsaacSim)：资产、机器人栈、公开代码和部署入口。
- [NVIDIA Isaac Sim／AWS 公告](https://blogs.nvidia.com/blog/gpu-aws-omniverse-isaac-sim-robots/)：早期采用披露，限定 Amazon Robotics 传感器仿真方向，不外推机群规模。
- [MuJoCo](https://github.com/google-deepmind/mujoco)、[MuJoCo Playground](https://github.com/google-deepmind/mujoco_playground)：发行、程序接口和官方研究环境。
- [Gazebo ROS 2](https://gazebosim.org/docs/harmonic/ros2_integration/)、[Releases](https://gazebosim.org/docs/latest/releases/)、[Classic](https://classic.gazebosim.org/)、[Open Robotics SubT](https://www.openrobotics.org/blog/2021/9/27/darpa-subt-final-competition)：桥接、版本支持及虚拟竞赛使用。
- [CARLA 首页](https://carla.org/)、[Introduction](https://carla.readthedocs.io/en/latest/start_introduction/)：道路场景与客户端／服务端接口。
- [IPG CarMaker](https://www.ipg-automotive.com/solutions/product-portfolio/carmaker)：虚拟试驾、在环层次与部署形态。以上均于 2026-10-27 核验；无法读取的入口未作为正文证据。
