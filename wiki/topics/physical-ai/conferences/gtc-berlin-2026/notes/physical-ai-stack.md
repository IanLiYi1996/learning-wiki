# Physical AI 技术栈：任务编排、推理、通信与执行

核查截止、访问日：2026-10-26。以下只说明组件用途与输入输出，不判断采购价值，也不将这些组件统称为本次大会新发布。共采用五页实际通过 web.run 打开的官方一手资料。

## 核查笔记

**OSMO 管任务，不是训练算法。** 官方仓库将其定义为工作流编排工具。输入是 YAML 工作流，包括任务的容器镜像、算力需求和上下游依赖；它安排训练、仿真或测试程序在相应计算资源上运行，并把任务产物传给后续任务或保存到对象存储。模型训练由任务内的程序完成，模型权重等产物不能写成由 OSMO 自身算法生成。[S1]

**TensorRT 管已训练模型的推理运行，不是 VLA 模型。** 构建阶段通常输入导出的 ONNX 模型，输出针对目标 GPU 编译的序列化引擎；运行阶段加载引擎，输入新数据，输出模型预测。VLA 指视觉—语言—动作模型的任务类型，不能与推理工具互换名称。具体模型能否转换，还取决于算子支持或自定义插件，不能推定任意模型都能直接运行。[S2]

**Isaac ROS 是 NVIDIA 加速的 ROS 2 软件包集合，不等于 Isaac OS。** 按软件包定义与 ROS 2 节点机制合并理解，在感知链路中，它承担节点处理工作：接收输入数据，将处理结果交给其他节点。这个输入输出关系是接口层面的归纳；各包的算法、传感器输入和消息格式要逐包核对，首页没有给出统一规格。[S3,S4]

**ROS 2 管节点之间的数据与请求交换。** 节点可以在同一进程、不同进程或不同机器上通信；topic 用于发布和订阅数据，service 用于请求另一节点完成操作，action 用于较长时间的任务。因此，通信层传递的是消息和请求，不是训练算法，也不自动把感知结果变成电机命令。[S4]

**ros2_control 连接控制器与硬件接口。** 输入包括目标参考值和硬件测量状态；控制器据此计算命令。控制循环读取硬件状态、更新控制器输出，再把命令写到硬件组件。硬件插件负责实际设备通信；状态接口与命令接口分开，配置和驱动必须对应具体机器人。[S5]

这些关系并不是固定串联的一条流水线：OSMO 编排开发任务；TensorRT 执行网络；Isaac ROS 提供机器人处理节点；ROS 2 传消息；ros2_control 把控制结果接到设备。这里的分工是依据上述文档归纳，不表示安装这些组件后就能直接闭环运行机器人。[S1–S5]

## 来源表

五页均未提供本笔记可确认的统一发布日期，故只标访问日；访问日不是发布日。标题保留原文，URL 为实际成功打开的页面。

| 编号 | 标题 | 日期或访问日 | URL |
|---|---|---|---|
| S1 | NVIDIA/OSMO — README：Welcome to OSMO / Workflow Orchestration Purpose-built for Physical AI | 访问：2026-10-26 | https://github.com/NVIDIA/OSMO |
| S2 | Quick Start Guide — NVIDIA TensorRT | 访问：2026-10-26 | https://docs.nvidia.com/deeplearning/tensorrt/latest/getting-started/quick-start-guide.html |
| S3 | NVIDIA Isaac ROS — Isaac ROS | 访问：2026-10-26 | https://nvidia-isaac-ros.github.io/ |
| S4 | Nodes — ROS 2 Documentation: Jazzy | 访问：2026-10-26 | https://docs.ros.org/en/jazzy/Concepts/Basic/About-Nodes.html |
| S5 | Getting Started — ROS2_Control: Jazzy Oct 2026 documentation | 访问：2026-10-26 | https://control.ros.org/jazzy/doc/getting_started/getting_started.html |

## 核查与访问边界

- OSMO 用户指南入口 `https://nvidia.github.io/OSMO/user_guide/index.html` 本轮返回 NOT_AVAILABLE，改用 NVIDIA 官方仓库 README；这不证明用户指南不存在。
- Isaac ROS 首页只直接确认软件包集合的定位；本轮未逐包打开感知节点接口文档，因此不列具体消息类型，也不声称全部软件包均使用 TensorRT。
- 文档为访问时读取的动态页面，不是截止日的归档快照；不据此认定首发日期、历史版本状态、特定 VLA 转换支持或特定机器人部署结果。
- 未执行安装命令、机器人或 agent 软件；不展开 OpenUSD、Isaac Sim、物理仿真机制或总体层次表。
