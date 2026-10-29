# Physical AI 学习路线与自测

归档日期：2026-10-28。以下是已有教材的阅读和练习安排，不增加新的产品状态结论。

使用方法：每阶段分别记录“能解释”“能算或验证”“能描述产品交接”。读完一章不自动等于掌握；没有做过的实验保持未完成，不把教学程序结果当实机验证。

## 1. 先把系统画清楚

阅读：[行业篇 01](industry/chapters/01_lifecycle.md)、[原理篇 01](advanced/chapters/01_system_model.md)、[行业篇 12](industry/chapters/12_interfaces_reading.md)。

- [ ] 以拿杯子或送料为例，写出任务、状态、观测、动作、反馈及完成判据。
- [ ] 分清任务编排、策略模型、运动规划、控制器、驱动和安全保护的职责。
- [ ] 写出一条动作接口：关节顺序、单位、坐标、绝对或增量、时间戳和有效期。
- [ ] 解释模型输出数组为什么不能不经适配直接发给任意机器人。

产物：一张系统职责表和一份输入输出约定。可使用 [产品方案模板](templates/product-solution-note.md) 的接口部分。

## 2. 学几何、动力学和真实控制

阅读：[原理篇 02](advanced/chapters/02_robot_geometry.md)、[03](advanced/chapters/03_dynamics_contact.md)、[05](advanced/chapters/05_planning_control.md)，对读 [行业篇 07](industry/chapters/07_perception_control.md)。

- [ ] 说明 SE(3)、坐标变换、FK、IK 和雅可比各自的输入输出。
- [ ] 算两连杆 FK，检查两种 IK 解到达同一点。
- [ ] 用差分验证雅可比，解释奇异位形下普通逆和阻尼更新的差别。
- [ ] 区分力、力矩、冲量、接触约束以及执行器和传动的限制。
- [ ] 说明路径、带时标轨迹、位置控制、力矩控制和任务完成的区别。
- [ ] 从 MoveIt、cuRobo、ros2_control、UR 或 ABB 接口卡片中，指出谁生成运动、谁执行、谁拥有实际驱动。

练习：[数值工作簿](advanced/examples/numerical_workbook.py) 的 FK／IK、雅可比、阻尼及反馈检查。这里只验证教学计算，没有机械臂执行记录。

## 3. 学感知、状态估计和数据采集

阅读：[原理篇 04](advanced/chapters/04_estimation_slam.md)、[10](advanced/chapters/10_data_pipeline.md)，对读 [行业篇 02](industry/chapters/02_real_data.md)。

- [ ] 说明相机内参、外参、畸变、深度、标定误差和坐标之间的关系。
- [ ] 写出 Kalman／EKF 的预测与更新，区分状态不确定性和传感器噪声。
- [ ] 区分 SLAM 的局部定位、地图与回环约束。
- [ ] 为图像、机器人状态和命令定义采集时间、到达时间、episode 和标定版本。
- [ ] 解释因果对齐，指出使用动作发生后的图像作当前输入会造成什么问题。
- [ ] 分清 MCAP 容器、查看平台、分析管理平台和人工数据服务交付的内容。

产物：一份 episode 字段表和数据划分规则。运行工作簿的标量 Kalman 与因果对齐检查。

## 4. 学仿真和合成数据

阅读：[原理篇 03](advanced/chapters/03_dynamics_contact.md)、[09](advanced/chapters/09_world_models.md)、[11](advanced/chapters/11_simulation.md)，对读 [行业篇 03](industry/chapters/03_scene_sim.md)、[04](industry/chapters/04_synthetic.md)。

- [ ] 列出仿真机器人除外观几何外需要的关节、惯量、碰撞、接触、执行器和传感器参数。
- [ ] 解释积分步长、碰撞检测、接触约束与求解误差怎样影响结果。
- [ ] 区分控制器虚拟调试、机器人软件集成、动力学仿真和视频世界模型。
- [ ] 分清渲染感知标签、示范轨迹扩增、视频预测及外观迁移的监督内容。
- [ ] 说明域随机化能覆盖哪些差异、哪些差异仍需要实测。
- [ ] 给 RobotStudio、Process Simulate、Isaac Sim、MuJoCo／Gazebo 以及 Cosmos 分支分别写一句职责，不用“通用平台”代替接口说明。

产物：场景参数清单，以及“生成数据是什么、怎样验证、用于哪个训练目标”的说明。这里没有预设已安装任何仿真器。

## 5. 学模型和训练机制

阅读：[原理篇 06](advanced/chapters/06_representation_vla.md)、[07](advanced/chapters/07_imitation_generators.md)、[08](advanced/chapters/08_rl.md)、[09](advanced/chapters/09_world_models.md)，对读 [行业篇 05](industry/chapters/05_training.md)、[06](industry/chapters/06_model_platforms.md)。

- [ ] 写出图像 patch、语言 token、QKV、注意力 mask 和动作表示的张量尺寸。
- [ ] 区分行为克隆、动作分块、扩散策略和 Flow Matching 的训练目标与推理过程。
- [ ] 解释多峰动作下 MSE 均值为什么可能不是可用动作。
- [ ] 区分 Bellman 目标、优势估计、PPO 与 SAC 的更新内容及数据来源。
- [ ] 说明世界模型的状态预测、想象训练和真实执行如何分开。
- [ ] 分清训练执行器、仿真训练环境、实验追踪、模型登记、可下载策略及商业工作站交付。
- [ ] 从 GR00T、openpi、OpenVLA／OFT、Gemini Robotics 或商业卡片中抄出已公开输入、动作接口、获取条件和缺失信息，不相互代填。

产物：一份模型接口与训练样本说明。运行工作簿的 MSE、加噪和常量 flow 算例；这些不等于训练过对应模型。

## 6. 学部署和验证

阅读：[原理篇 12](advanced/chapters/12_runtime.md)、[13](advanced/chapters/13_evaluation.md)、[14](advanced/chapters/14_workbook.md)，对读 [行业篇 08](industry/chapters/08_edge_deploy.md)、[09](industry/chapters/09_validation.md)。

- [ ] 写出图像预处理、数据传输、GPU 推理、动作解码和控制下发的时间预算。
- [ ] 解释 stream、事件、输入缓冲生命周期、量化校准及尾延迟。
- [ ] 分清计算模块、系统软件、推理引擎和工业应用宿主。
- [ ] 区分日志回放、软件在环、硬件在环以及真实闭环任务试验。
- [ ] 预先写成功判据、重复次数、人工干预条件、失败分类和适用范围。
- [ ] 对比 9/10 与 90/100 的 Wilson 区间，解释相同成功率为何不是相同证据。

产物：填写 [评测协议](templates/evaluation_protocol.md)，记录你实际做过与没做过的验证。工作簿只提供统计和教学数值结果。

## 7. 学现场方案和多机业务交接

阅读：[行业篇 10](industry/chapters/10_fleet_operations.md)、[11](industry/chapters/11_solutions_cases.md)、[12](industry/chapters/12_interfaces_reading.md)，回看 [原理篇 01](advanced/chapters/01_system_model.md)、[12](advanced/chapters/12_runtime.md)。

- [ ] 区分机器人本地避障、车队派单、共享资源协调、遥测与远程支持。
- [ ] 为送料任务分开记录接受请求、到达、物料交接和业务关闭。
- [ ] 用 DHL／Stretch、FedEx／Dexterity、BMW／Figure、GXO／Digit、MiR／DENSO 中一个案例解释限定任务及公开运行证据。
- [ ] 保留部署时间、实际工序、现有运行、未来扩展及披露方，不把未公开客户架构补成事实。
- [ ] 写清业务系统到机器人接口中的任务 ID、重试、取消、异常和人工接管。

产物：一份端到端方案拆解，分别标记“客户披露”“供应商披露”“学习用参考组合”和“未公开”。

## 最后用一个任务贯通

自行选择拿杯子、分拣或工厂送料之一，把以上产物串成一份项目笔记：

1. 任务与完成判据。
2. 身体、传感器、坐标与动作约定。
3. 真实数据与训练样本。
4. 仿真或合成数据及验证条件。
5. 策略、规划、控制和运行链路。
6. 各阶段产品、部署方式及交接责任。
7. 评测记录、失败诊断与未验证事项。

没有真实设备时，做到接口说明和教学数值验证即可；仿真、训练、部署和现场试验分别留为待完成项。

[返回专题入口](README.md)
