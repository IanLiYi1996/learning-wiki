## 07 感知、运动规划与机器人控制产品

本章核验日为 2026-10-27。“成熟”在这里不是统一评分：可获取的开源代码、正式商业产品、供应商生产案例、具名客户披露、试点和研究原型是不同证据。案例只说明其公开范围，不能把品牌合作、下载数量或控制接口的存在推成整机量产。以下按“感知结果—运动请求—控制器执行”介绍产品，不将它们视为可以直接互换的整套系统。

### Isaac ROS：ROS 2 加速感知、定位与地图组件

Isaac ROS 是 NVIDIA 的加速 ROS 2 组件工具链，本卡覆盖感知、定位与地图分支。各组件接入图像、标定信息、深度或 IMU，输出检测/分割结果、位姿/里程计或地图；Visual SLAM 估计运动，nvblox 将深度与位姿转换为三维重建及导航代价地图，输入输出应按包区分。[组件目录](https://nvidia-isaac-ros.github.io/)、[地图组件](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_nvblox/index.html)

公开接缝包括 ROS 2 节点、话题、服务和 launch 配置，可接入已有机器人数据流。官方文档与仓库提供组件和环境获取入口，部署要匹配支持的 GPU、ROS 分支及传感器配置；本卡只标“公开工具链”，不补写客户生产证据，也不将所有依赖视为同一种许可。[官方仓库](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common)、[定位包接口](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_visual_slam/index.html)

它不同于提供系统/计算依赖的 JetPack，也不同于构建和执行模型的 TensorRT；这里交付的是机器人算法组件及其连接关系。传感器标定、时钟和坐标仍由集成方核验，GPU 加速不等于整条链路硬实时。[职责与集成范围](https://nvidia-isaac-ros.github.io/)

### MoveIt：开源机械臂规划与执行框架

MoveIt 2 把机器人模型、当前关节状态、坐标变换、障碍物和目标位姿接成运动规划请求，输出关节轨迹及执行反馈。`move_group` 提供 ROS actions/services，C++ 接口和 RViz 插件可发请求，轨迹通过 `FollowJointTrajectory` 交给下游控制器；它自己不提供机器人侧的该 action server。[架构与接口](https://moveit.picknik.ai/main/doc/concepts/move_group.html)

代码以 BSD-3-Clause 发布，可按匹配的 ROS 2 分支使用二进制包或源码，部署在机器人计算机或规划主机；URDF、SRDF、运动学插件和规划配置属于实际交付物，而不是下载后自动获得的适配。证据等级是可查的开源工具链与官方代码，不用仓库活跃度代替客户量产证明。[官方代码](https://github.com/moveit/moveit2)

它解决几何规划与轨迹衔接，不等于视觉识别器、伺服驱动器或安全控制器。碰撞结果依赖模型、标定和场景更新；商业支持、部署维护和客户应用证据应与下面的 MoveIt Pro 分开记录。[职责边界](https://moveit.picknik.ai/main/doc/concepts/move_group.html)

### MoveIt Pro：商业开发平台与机器人运行时

MoveIt Pro 是 PickNik 的商业操作应用平台，不是给开源 MoveIt 换一个名字。输入包含机器人模型、传感器数据和行为树任务，运行时完成行为执行、规划与控制接口衔接；Desktop App 用于编辑、调试和监视，Runtime 部署到机器人，二者可以分机。公开文档说明 ROS 2 Control 接口与自定义组件扩展，并区分低层 Core 库。[产品与接口规格](https://docs.picknik.ai/technical_specifications/)

获取走商业许可与供应商安装渠道，主版本有公开支持周期；应冻结应用、容器/软件包、ROS 分支和机器人配置的对应关系，不把开发分支当生产支持承诺。[发布与支持政策](https://docs.picknik.ai/software_installation/major_releases/)

供应商披露 BMW 使用行为树、视觉与规划做抓取重定位，但同页明确首个应用仍准备从实验室试点转生产。因此此例标为“供应商具名试点”，不写成全面量产，也不据其生产级措辞推断整机安全认证。[BMW 案例及阶段](https://picknik.ai/case-study-automotive/)

### cuRobo：GPU 运动生成算法库

cuRobo 将机器人模型与碰撞几何、障碍场景、当前关节状态和目标末端位姿作为输入，利用 GPU 并行逆运动学、碰撞检查与轨迹优化，返回规划状态、优化轨迹及插值轨迹。输出是可交给执行层的关节运动序列，不是机器人已完成运动的反馈。[输入输出与流程](https://nvlabs.github.io/curobo/latest/getting-started/motion_planning.html)

公开 Python API 提供模型/状态/场景表示，以及逆运动学、轨迹优化和运动规划模块；官方仓库按 Apache-2.0 公开，可在匹配的 CUDA 计算环境中嵌入应用。本卡证据等级是“公开工具链”，未另核客户生产部署，不将文档演示或基准结果转成应用性能承诺。[公开 API](https://nvlabs.github.io/curobo/latest/reference/api_overview.html)、[官方仓库](https://github.com/NVlabs/curobo)

它是运动生成库，不是 MoveIt 的整套 ROS 场景/任务/执行框架，也不是伺服控制器。ROS/MoveIt 接入、轨迹下发和实际执行确认仍需集成层；碰撞几何近似、状态与障碍更新，以及关节顺序、单位和执行约束都须保持一致，规划成功不能替代这些条件。[模型与算法职责](https://curobo.org/)

### Nav2：移动机器人的导航应用框架

Nav2 面向移动与地面机器人：输入地图或环境表征、定位/里程计、传感器观测、机器人运动约束和导航目标，输出路径、底盘运动命令及任务状态。行为树通过 ROS action/service 编排规划、控制和恢复等服务器，算法以插件替换；这与机械臂的抓取轨迹规划是不同职责。[官方架构](https://docs.nav2.org/rolling/)

项目提供开源代码及按 ROS 发行版组织的工具链，Open Navigation 提供专业服务。部署时需要机器人侧驱动、坐标关系、传感器和底盘接口；实际交付应包含导航配置、地图版本、行为树与故障处理，而不是只有一个目标坐标。官方“被企业采用”的表述属于维护方披露，本卡不将其换算成某客户的生产规模。[代码与获取](https://github.com/ros-navigation/navigation2)

Nav2 不承担混合厂商车队的全局资源仲裁，也不替代底盘的制动与伺服闭环。单机能成功导航，不代表多机共享窄通道、门和电梯不会冲突；该衔接交给第 10 章的调度层。[模块边界](https://docs.nav2.org/rolling/)

### ros2_control：控制器与硬件之间的标准接缝

ros2_control 的核心不是另一套路径搜索器，而是 Controller Manager、控制器插件与硬件组件。输入为参考指令、机器人描述和硬件读回的状态；控制循环执行 read、update、write，输出位置、速度或力/力矩等硬件命令接口。ROS services 管理组件生命周期与接口占用，避免多个控制器同时争用同一资源。[官方架构](https://control.ros.org/jazzy/doc/getting_started/getting_started.html)

它是按 ROS 发行版发布的开源框架，可源码适配驱动或使用对应包；此处读取 Jazzy 文档说明接口，不称 Jazzy 为最新版本。UR 官方 driver 的兼容声明是可查集成证据，但不是任意自制硬件的实时性能证明。[UR 集成说明](https://docs.universal-robots.com/Universal_Robots_ROS_Documentation/rolling/doc/ros2_controller_vs_driver.html)

真实边界在驱动阻塞、内存操作、操作系统调度及设备链路。Controller Manager 文档提供循环与诊断机制；“用了 ROS 2”不保证硬实时，周期上限和异常恢复必须按目标运行环境核验，并保留异常原因。[循环与诊断](https://control.ros.org/jazzy/doc/ros2_control/controller_manager/doc/userdoc.html)

### Mech-Vision / Mech-Viz：工业三维视觉与视觉引导运动

Mech-Vision 将相机图像/点云及项目配置变成工件位姿、标签或抓取路径；Mech-Viz 接收视觉结果、机器人与场景模型，组织可视化流程并规划取放运动。新版文档也说明 Mech-Vision 可提供部分路径规划，不能按旧版名称把两者功能硬切成永不重叠的两层。[当前产品职责](https://docs.mech-mind.net/en/suite-tutorial/latest/vision-system-introduction.html)

软件在 IPC 上运行，通过供应商渠道获取与相机、机器人匹配的版本。标准接口模式可用 TCP socket 请求并返回位姿/路径，由机器人或 PLC 保留动作决策；Master-Control 模式则由视觉侧发送运动或 I/O 命令，集成责任明显不同。[通信模式](https://docs.mech-mind.net/en/suite-tutorial/latest/vision-system-introduction.html)

官方点焊上料案例描述了现场工件识别、选取和路径规划，但客户未具名，记为“供应商匿名生产应用案例”，不据此替任何具体工件承诺精度或节拍。其边界还包括曝光、手眼标定、夹具和抓手几何，以及接口返回失败时的工位逻辑。[案例范围](https://www.mech-mind.com/cases/picking-of-automotive-components-for-spot-welding.html)

### UR PolyScope 与官方 ROS 2 driver：控制器和外部应用不能混为一层

PolyScope 是 UR 机器人控制器上的编程、运动执行和集成软件；外部 ROS 2 driver 则把应用侧轨迹、I/O 请求与机器人状态连接到控制器。可查接口包括 URScript、RTDE、ROS topics/services/actions 与 ros2_control，输出是控制器实际执行的运动及状态，不是绕过控制器直接驱动电机。[PolyScope 接口](https://www.universal-robots.com/products/software/integration/)

PolyScope 随适用机器人系统提供，官方 driver 开源并由 UR 明确支持，运行在外部 Linux 主机。控制器内置 ROS 2 功能和外部 driver 是两条不同路径；内置功能与控制器自带 ROS 发行版绑定，不能从“支持 ROS 2”推成任意版本互通。[两条集成路径](https://docs.universal-robots.com/Universal_Robots_ROS_Documentation/rolling/doc/ros2_controller_vs_driver.html)、[官方代码](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver)

产品状态证据是正式控制器软件及厂商维护驱动；官网工厂案例不能自动证明使用了该 ROS driver。配置还需区分 PolyScope X、PolyScope 5 与旧 CB3，保留速度缩放、暂停/故障与上层轨迹执行之间的状态映射，始终以控制器实际版本为准。[官方支持范围](https://www.universal-robots.com/developer/communication-protocol/ros-and-ros2-driver/)

### ABB EGM：外部运动引导接口的控制器例子

Externally Guided Motion 是 RobotWare 的可选控制器功能，不是通用 ROS 2 驱动。Position Stream 向外部发送运动状态；Position Guidance 接收外部生成的关节或笛卡尔目标；Path Correction 用外部测量修正已编程路径。所核验的官方手册将传感器通道定义为 UDP 与 Protobuf，并给出 `egm.proto` 和 RAPID 侧组件。[ABB 官方手册，接口与消息定义](https://library.e.abb.com/public/f63dc4031d194a58be058eb657441180/3HAC073319%20AM%20Externally%20Guided%20Motion%20RW6-en.pdf?x-sign=BWbSjBUhUwt70d44B8HVhOH3uYGGWVQuy72oK8Yu4Vq6yiBCtA5eQE%2B8jjTH7Ypt)

此证据明确属于 IRC5 / RobotWare 6.14、手册修订 F，是存量控制器接口例，不能标成最新 OmniCore / RobotWare 的规格。部署需要对应 EGM 选件、外部通信端点及控制器程序；文档中的上料和焊缝跟踪是应用例示，不是具名客户生产证明。[版本与选件范围](https://library.e.abb.com/public/f63dc4031d194a58be058eb657441180/3HAC073319%20AM%20Externally%20Guided%20Motion%20RW6-en.pdf?x-sign=BWbSjBUhUwt70d44B8HVhOH3uYGGWVQuy72oK8Yu4Vq6yiBCtA5eQE%2B8jjTH7Ypt)

工程交付必须固定消息坐标、单位、控制模式和失联处理，验证外部目标与控制器滤波/限幅后的执行差异，并保存配置。周期通信接口既不是任意力矩控制权限，也不是外部网络到机器人运动的硬实时保证。

### 本阶段交付物与下一阶段接口

本阶段应形成可部署的机器人配置、标定结果与坐标字典、视觉结果 schema、运动请求/执行反馈契约、控制器兼容矩阵和故障状态映射。这里的交付要求是本手册的工程组织建议，不是每个产品都自动生成的功能清单。交给第 08 章的对象包括模型、算法包、依赖与许可、硬件驱动和预期资源需求；运行时交给第 09 章验证的则是可观测状态及可重放输入。

### 实际读取来源

- [Isaac ROS 官方目录](https://nvidia-isaac-ros.github.io/)、[Common 官方仓库](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common)、[Visual SLAM 文档](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_visual_slam/index.html)、[nvblox 文档](https://nvidia-isaac-ros.github.io/repositories_and_packages/isaac_ros_nvblox/index.html)：仅核验组件职责、接口与公开获取。
- [MoveIt 架构](https://moveit.picknik.ai/main/doc/concepts/move_group.html)、[MoveIt 2 官方代码](https://github.com/moveit/moveit2)。
- [MoveIt Pro 规格](https://docs.picknik.ai/technical_specifications/)、[发布支持政策](https://docs.picknik.ai/software_installation/major_releases/)、[BMW 试点案例](https://picknik.ai/case-study-automotive/)。
- [cuRobo 官方文档](https://curobo.org/)、[运动规划输入输出](https://nvlabs.github.io/curobo/latest/getting-started/motion_planning.html)、[公开 Python API](https://nvlabs.github.io/curobo/latest/reference/api_overview.html)、[官方仓库](https://github.com/NVlabs/curobo)：未引用论文、扩查客户或列版本大全。
- [Nav2 官方文档](https://docs.nav2.org/rolling/)、[官方代码](https://github.com/ros-navigation/navigation2)。
- [ros2_control 架构](https://control.ros.org/jazzy/doc/getting_started/getting_started.html)、[Controller Manager](https://control.ros.org/jazzy/doc/ros2_control/controller_manager/doc/userdoc.html)。
- [Mech-Mind 软件与通信](https://docs.mech-mind.net/en/suite-tutorial/latest/vision-system-introduction.html)、[匿名点焊上料案例](https://www.mech-mind.com/cases/picking-of-automotive-components-for-spot-welding.html)。
- [UR PolyScope 集成](https://www.universal-robots.com/products/software/integration/)、[ROS 2 集成路径](https://docs.universal-robots.com/Universal_Robots_ROS_Documentation/rolling/doc/ros2_controller_vs_driver.html)、[driver 官方代码](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver)、[官方支持入口](https://www.universal-robots.com/developer/communication-protocol/ros-and-ros2-driver/)。
- [ABB EGM 官方手册，RobotWare 6.14，修订 F](https://library.e.abb.com/public/f63dc4031d194a58be058eb657441180/3HAC073319%20AM%20Externally%20Guided%20Motion%20RW6-en.pdf?x-sign=BWbSjBUhUwt70d44B8HVhOH3uYGGWVQuy72oK8Yu4Vq6yiBCtA5eQE%2B8jjTH7Ypt)：读取版本、选件、职责、通信和代码示例说明；公开下载地址含服务器签名，失效时按文档编号在 ABB Library 查找。
