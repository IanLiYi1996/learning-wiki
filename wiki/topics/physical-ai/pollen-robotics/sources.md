# Pollen Robotics：来源、版本、开放范围与复现等级

研究日期：2026-11-03。[生态导读](README.md)。

## 1. 本次查了什么

本读本从 [官方组织](https://github.com/pollen-robotics)、[官网](https://pollen-robotics.com/)与 [Reachy 2 官方文档](https://docs.pollen-robotics.com/)进入，按职责选择项目。只读固定源码、README、配置及相关测试；没有将组织中的全部项目、fork、CAD、电路、系统镜像和模型都审计一遍。

[机器可读快照清单](sources.json)保存 **22 个仓库、23 份快照**，其中 AmazingHand main 与 Enhanced 分支分开。日期表示本次读取时间，不表示项目首次发布或所有构建时间。正文结论链接到固定 blob；不能用浮动 main 后来的修改来支持旧结论。

Microduck 章还对照两项固定的上游依赖：[mjlab 的相关环境／观测／动作定义](https://github.com/mujocolab/mjlab/tree/19d6c06c17572dafcb31ad5110a902006b58d944)、[BAM 的 mjlab 适配](https://github.com/Rhoban/bam/blob/62bd8ce12154340be97e06f7f41a0ca8f116d967/bam/mjlab.py)。它们另列在清单中，不计为 Pollen 原创仓库，也不声称审计了完整依赖栈。

GitHub 的 fork／默认分支元数据另外记录；不拿最后 pushed 时间代替当前默认分支的源码版本，也不拿 star 数排项目成熟度。仓库可以存在而官方文档仍未完成，源码和文档需要分别读。

## 2. 分章实际读取范围

| 章节 | 主要对象 | 核验目的 |
| --- | --- | --- |
| 01 本体／SDK | reachy2-sdk、core、SDK server／API、reachy_mini | 目标、状态、单位、代际、后端与交接 |
| 02 遥操作／日志 | Reachy2Teleoperation、旧 ReachyTeleoperation、HDF5 recorder、Rerun adapter | 人类控制、反馈通道、记录数据与学习样本差别 |
| 03 感知／仿真 | pollen-vision、两个 MuJoCo server 路径、reachy2_qpik | 深度尺度、外参、时序、接口差异与控制异常 |
| 04 数据／策略 | grabette、grabette-slam、grabette-policy | 录制、重建、chunk-relative 表示、训练与 OpenArm 适配 |
| 05 Microduck／RL | microduck、microduck_rl | 仿真状态、观测、奖励、执行器、PPO 与 runtime 合同 |
| 06 手／执行器 | AmazingHand 两版本、PincOpen、Orbita2D／3D | 机构、标定、单位、耦合运动学、使能与反馈 |

具体读取文件在各段的主来源链接旁列出。未审计每个依赖、所有测试、全部编译目标或整套模型参数；阅读了源码不等于已通过上游测试。

## 3. 核心快照入口

| 链路 | 固定源码入口 |
| --- | --- |
| Reachy 2 | [SDK](https://github.com/pollen-robotics/reachy2-sdk/tree/eb42d1f08cf32244443dc46930ff2e17cf5852da)、[core](https://github.com/pollen-robotics/reachy2_core/tree/b7000c1255f322826f4d0ad1f1e54d424e55c051)、[server](https://github.com/pollen-robotics/reachy2_sdk_server/tree/2bb56b676f235a8d6774474cf053ef4bd8585476)、[API](https://github.com/pollen-robotics/reachy2-sdk-api/tree/6a7cbdd463200fef3a20c2742255ee5089d89561) |
| 遥操作与记录 | [Reachy2Teleoperation](https://github.com/pollen-robotics/Reachy2Teleoperation/tree/1612347e3b1b06a612f5dd79c333090c1d0bd335)、[旧代入口](https://github.com/pollen-robotics/ReachyTeleoperation/tree/9934da67628c0b41398d0a2fd33316494ada39db)、[HDF5](https://github.com/pollen-robotics/reachy2_hdf5_recorder/tree/feead2b81acdc92ab632f9dc53badf7a450ba19e)、[Rerun](https://github.com/pollen-robotics/reachy2-sdk-rerun/tree/538b296209cc91d114b8e923c43df9912f5d0559) |
| Mini | [SDK 与 daemon](https://github.com/pollen-robotics/reachy_mini/tree/e26c6c30e723d80b1ecdaa3ace80f7e84f4d15f2) |
| 数据与学习 | [Grabette](https://github.com/pollen-robotics/grabette/tree/e82d31b772c99efbf35f16e8634844ab22e73c1b)、[SLAM](https://github.com/pollen-robotics/grabette-slam/tree/39116d865065a7b8db946f6845ecf6c07042df5f)、[policy](https://github.com/pollen-robotics/grabette-policy/tree/c0e997b15b7b50a485577fa6d059875cfc62e849) |
| 小型双足 | [Microduck runtime](https://github.com/pollen-robotics/microduck/tree/997808c1d71056d31bd6f05fc5fde848c849d2bc)、[RL 环境](https://github.com/pollen-robotics/microduck_rl/tree/bae39f5900b318f7e87fc485c30a31213cfa14eb) |
| 感知与仿真 | [vision](https://github.com/pollen-robotics/pollen-vision/tree/2d7cfab7c0c1090741e43ba5e3aab5acefb110f7)、[fake SDK](https://github.com/pollen-robotics/reachy2_mujoco/tree/f6d8284e812d3b96b557e2e844d55bd09d6e3ee6)、[WebSocket bridge](https://github.com/pollen-robotics/reachy2_mujoco_server/tree/a304471a9685d6a30e45f8bdb552d8db0c91ac32)、[QP IK](https://github.com/pollen-robotics/reachy2_qpik/tree/149948db13b108b9f4a940a5bb94f50422eadd27) |
| 操作部件 | [AmazingHand](https://github.com/pollen-robotics/AmazingHand/tree/3e8241074df3436a3044ced4881e3bb2133aa725)、[Enhanced](https://github.com/pollen-robotics/AmazingHand/tree/31bfc548270a306829c7a3acdad19f643f53f618)、[PincOpen](https://github.com/pollen-robotics/PincOpen/tree/1b5a3dc83cb4eae042d535bda3765b9e12a9b8a7)、[Orbita3D](https://github.com/pollen-robotics/orbita3d_control/tree/9e547d616af8487c52c5aff68792a74fbc023d79)、[Orbita2D](https://github.com/pollen-robotics/orbita2d_control/tree/dc54f7ee24b54407d584ebee15bdb35894c206d0) |

这些版本是本 Wiki 的阅读快照，**不是经过联合兼容测试的一套发布 BOM**。各系统对上游分支、镜像、依赖、固件和硬件的要求仍须分别确认。

## 4. 许可与证据分别检查

仓库 LICENSE、机械设计、第三方模型、数据、硬件采购和在线服务分别记录。AmazingHand 的机械许可与软件许可不同；PincOpen 与多数控制软件的声明也不同。Microduck RL 另有模型许可文件。这里不把组织首页的 Apache 标语推广到全部材料，不给法律合规结论。[Microduck 模型许可入口](https://github.com/pollen-robotics/microduck_rl/blob/bae39f5900b318f7e87fc485c30a31213cfa14eb/LICENSE-MODELS.md)

产品官网、README 的指标、演示与训练耗时属于作者／供应商披露。本文不重绘这些曲线，不转述为独立性能结果，不提供实时价格、库存或客户部署承诺。一个下载入口不能证明获得了许可、全部依赖和完整复现条件。

实物风险请继续读 [官方 Reachy 2 安全说明](https://docs.pollen-robotics.com/getting-started/safety-first/safety-guidelines/)；本文只做接口和证据审计，不是认证、安全测试或操作培训的替代品。

## 5. 三个等级：本次只做到机制与静态核验

**第一级，已执行：**本 Wiki 的标准库小计算和文档／网页检查。验证单位、反投影、空间变换、运动学、时间与动作合同；不包含真实相机、网络、物理引擎、神经网络或驱动。

**第二级，未执行：**指定版本的依赖安装、仿真、感知、数据导出、训练或策略回放。还要确认资源、模型／数据使用条件、参数和基准协议。

**第三级，未执行：**真机部署与任务验收。需要具体型号、标定／固件、使能和停止流程、通信与权限、操作人员、任务空间、负载、失败恢复与独立证据；仿真“会动”不能跳过这些。

没有连接机器人、使能电机、刷固件、采购、GPU 训练、模型下载、数据下载或付费 API 调用。读取源代码与自己做教学计算分别标记，避免把“原创例子”混成上游实测。

## 6. 与旧归档的关系

本研究是 2026-11-03 新增的独立集合。旧 Physical AI 四份归档的正文、校验和、PDF／Word、产品卡和日期不因此被静默改写。原有原理章节可交叉对读；新增页面、配图、实验和快照在自己的目录／清单中验证。
