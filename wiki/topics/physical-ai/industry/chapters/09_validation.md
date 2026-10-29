## 09 验证、回放与系统测试方案

核验日：2026-10-27。本阶段接收第 08 章冻结的模型、运行栈与配置，产出“在什么输入、接口、版本和判据下通过”的证据。下面将汽车控制器的在环测试与真实机器人日志回放分开介绍；汽车测试产品可以提供方法与接口参考，但其道路场景模型和传感器注入适配不能直接证明仓储机器人、机械臂或人形机器人有效。

### Applied Intuition：汽车软件验证与在环集成方案

Applied Intuition 的车辆工具方案把场景/真实日志、传感器模型与被测软件接入仿真和评估流程，输出测试结果与可追踪的场景证据。当前官网提供 SDK 化工作流和云、本地、隔离环境等部署入口；具体 HIL 数据注入、时间同步和硬件端点仍要按被测控制器集成，不能臆造一个通用于所有机器人控制器的 ROS API。[当前产品入口](https://www.appliedintuition.com/products)

获取方式是商业产品与工程集成。供应商和 NI 的联合公告明确区分 Applied 的对象/传感器仿真与 NI 的 HIL 测试硬件；不是安装一个仿真应用就获得完整硬件台架。Porsche 合作公告涉及 SIL、HIL 与车辆测试，记为“供应商具名汽车合作披露”，不证明指定车型的全部测试都用某个单品完成。[HIL 集成范围](https://www.appliedintuition.com/press-releases/national-instruments)、[Porsche 合作](https://www.appliedintuition.com/press-releases/porsche)

本卡仅覆盖汽车 ADAS/AD/车辆软件分支。道路传感器、交通参与者和 ECU 时序需匹配实际对象；公开合作不等于全套接口规格公开，也不能用仿真覆盖率取代真实系统的未知故障分析。

### dSPACE SCALEXIO：汽车 ECU 的闭环硬件在环

SCALEXIO 以实时模型、I/O 配置及被测 ECU 为输入，模拟 ECU 所看到的车辆/环境信号，读取其控制输出并形成闭环。输出包括响应轨迹、捕获数据、故障注入结果与自动测试判据。它与 RCP 的职责不同：HIL 中 ECU 仍是真实被测对象，RCP 才可能由实时系统替代 ECU 的控制功能。[官方职责](https://www.dspace.com/en/pub/home/products/hw/simulator_hardware/scalexio.cfm)

产品是按项目配置的商业硬件与软件组合，公开接缝包括总线/网络、模拟与数字 I/O、FMI 模型集成，以及适用组件的 ASAM XIL 自动化接口；故障插入与信号调理需要具体硬件，而非所有机箱自动具备。[接口及正式产品扩展](https://www.dspace.com/en/pub/home/news/dspace_pressroom/press/scalexio-fsx-extension.cfm)

供应商客户页中 Geely 的具名评价明确涉及 SCALEXIO 与 ASM 的混动控制器开发测试，证据范围就是该汽车用途。本章也仅采用汽车 ECU 分支：没有工位接触、机器人传动和网络模型的对应验证，不能把汽车 HIL 台架直接称为通用机器人验证方案。[具名用途证据](https://www.dspace.com/en/pub/home/company/customers.cfm)

### Foxglove + rosbag2：真实机器人事件的记录、检查和输入回放

rosbag2 接收 ROS 2 消息并记录，也可按选定话题回放为 ROS 消息；Foxglove 接收本地/远端记录或 WebSocket 流，提供时间轴检查与可视化。输出是可重看、可定位的事件证据，配合被测软件才形成回归测试，不能把“看起来轨迹一致”当作机器自动判定通过。[rosbag2 官方代码与接口](https://github.com/ros2/rosbag2)、[Foxglove 回放语义](https://docs.foxglove.dev/docs/visualization/playback)

rosbag2 为开源工具链，Foxglove 当前应用/服务按商业席位或许可获取；本地文件访问、云存储和桥接组件的获取条件应分别记录。官方文档支持 MCAP、ROS bag 等格式，同时提醒旧 `.db3` 缺少消息定义，不宜假设自定义消息天然可回放。[当前格式与访问条件](https://docs.foxglove.dev/docs/visualization/connecting/local-data)

Dexory 的公开播放器由 Foxglove 官方介绍，可同时驱动可视化和向 ROS 2 栈重发 MCAP；这是具名真实机器人开发集成证据，不是整机闭环复现保证。应记录消息定义、时钟、TF、初始状态与 QoS；存储格式和数据管理细节交叉参见数据章，不重列平台全功能。[Dexory 播放器集成](https://foxglove.dev/blog/connect-foxglove-to-your-local-player-with-playback-control)

### 怎样衔接成系统测试

以下是本手册建议的交付组织，不是上述平台自动具备的统一能力。每项测试至少记录被测版本、输入集、初始状态、运行环境、输出判据与失败证据，并区分：

- 日志检查：解释已经发生的事件，检查时间顺序、状态转换和故障上下文。
- 开环回归：将相同记录输入新软件，比较感知、估计或规划输出；软件产生的新动作没有改变原记录中的环境。
- 闭环验证：模型或真实被测对象根据新输出产生后续输入。汽车 HIL 的 ECU—仿真环境闭环属于这一类，但模型误差仍存在。

日志播放可能向 ROS 图重新发布指令话题，因此回归环境应与设备执行域隔离，只将明确选定的观测输入交给被测程序；测试脚本不应自动连到真实机器人执行端。本次工作未执行任何设备、安装命令或实机参数配置。[回放会重新发布消息的依据](https://github.com/ros2/rosbag2)

交给第 10 章的不是一个“测试通过”标签，而是与发布清单绑定的回归结果、已知限制、遥测项、现场告警规则与回滚条件。网络中断、时钟错位、软件重启、命令重发、算力竞争和地图/标定变化，都应有明确的失败分类及证据入口，避免现场故障只能靠口头描述。

### 实际读取来源

- [Applied Intuition 当前产品](https://www.appliedintuition.com/products)、[NI 在环合作范围](https://www.appliedintuition.com/press-releases/national-instruments)、[Porsche 汽车合作披露](https://www.appliedintuition.com/press-releases/porsche)：不将早期合作公告改写为具体在售 SKU 的全部规格。
- [dSPACE SCALEXIO](https://www.dspace.com/en/pub/home/products/hw/simulator_hardware/scalexio.cfm)、[FSX 与 ASAM XIL 接口](https://www.dspace.com/en/pub/home/news/dspace_pressroom/press/scalexio-fsx-extension.cfm)、[客户具名评价](https://www.dspace.com/en/pub/home/company/customers.cfm)。
- [rosbag2 官方代码与 README](https://github.com/ros2/rosbag2)：ROS 文档站访问受限，改读官方仓库。
- [Foxglove Playback](https://docs.foxglove.dev/docs/visualization/playback)、[本地格式与许可](https://docs.foxglove.dev/docs/visualization/connecting/local-data)、[Dexory PlaybackControl 集成](https://foxglove.dev/blog/connect-foxglove-to-your-local-player-with-playback-control)。
