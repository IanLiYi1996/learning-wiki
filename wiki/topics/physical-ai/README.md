# Physical AI

- 类型：主题
- 状态：已归档，后续可按章节补实验笔记
- 归档日期：2026-10-28
- 资料日期：行业篇、原理篇与概念地图为 2026-10-27；GTC 报告为 2026-10-26

这份专题同时回答两个问题：机器人系统各层怎样工作；业界各阶段已经有哪些产品和交付方案。行业篇与原理篇分开保存，按阶段对读。概念地图用于补术语，会议报告用于查具体发布。

本次是已有资料的整理归档，不是产品状态的重新核验。公开下载、商业交付、客户运行、限定试点、预览和未来计划仍按原文分别记录，不将全部条目统称为成熟量产方案。

## 从哪里开始

1. 读行业篇的 [阶段地图](industry/chapters/01_lifecycle.md) 和 [端到端组合与客户案例](industry/chapters/11_solutions_cases.md)，先知道各项工作交付什么。
2. 按下表查具体产品，同时读对应原理章节。
3. 使用 [学习路线与自测](learning-roadmap.md) 记录掌握情况，再运行离线练习。
4. 新产品或新版本用 [产品与方案笔记模板](templates/product-solution-note.md) 单独补充，不静默改写旧资料的时间口径。

## 四份正文

| 资料 | 内容 | 阅读文件 |
| --- | --- | --- |
| 业界产品与端到端方案 | 12 章；58 条产品、工具及应用方案记录；147 个一手来源入口 | [Markdown](industry/Physical_AI_业界产品与端到端方案.md) · [PDF](industry/Physical_AI_业界产品与端到端方案.pdf) · [Word](industry/Physical_AI_业界产品与端到端方案.docx) |
| 底层原理与实现细节 | 14 章；数学模型、算法、数据字段、运行接口和数值练习；21 篇论文元数据 | [Markdown](advanced/Physical_AI_底层原理与实现细节.md) · [PDF](advanced/Physical_AI_底层原理与实现细节.pdf) · [Word](advanced/Physical_AI_底层原理与实现细节.docx) |
| 知识全景与学习指南 | 基本概念、术语、领域地图与入门练习 | [Markdown](Physical_AI_知识全景与学习指南.md) · [PDF](Physical_AI_知识全景与学习指南.pdf) · [Word](Physical_AI_知识全景与学习指南.docx) |
| GTC Berlin 2026 内容整理 | 会期发布、机器人、工厂、汽车与 Physical AI 技术栈；版本 1.2 | [Markdown](conferences/gtc-berlin-2026/GTC_Berlin_2026_Physical_AI_深度调研报告.md) · [PDF](conferences/gtc-berlin-2026/GTC_Berlin_2026_Physical_AI_深度调研报告.pdf) · [Word](conferences/gtc-berlin-2026/GTC_Berlin_2026_Physical_AI_深度调研报告.docx) |

PDF 保留原交付的固定分页；Word 便于批注，目录与页码需兼容软件更新。GitHub 直接阅读可用 Markdown，公式密集章节也可查 PDF。

## 产品阶段与底层原理对照

| 工程阶段 | 产品与方案章节 | 对应原理章节 |
| --- | --- | --- |
| 系统职责与接口 | [01 阶段地图](industry/chapters/01_lifecycle.md)、[12 产品交接](industry/chapters/12_interfaces_reading.md) | [01 状态、观测、动作与反馈](advanced/chapters/01_system_model.md) |
| 真实数据采集与管理 | [02 Foxglove、MCAP、Rerun、数据服务](industry/chapters/02_real_data.md) | [10 时间对齐、动作语义与样本](advanced/chapters/10_data_pipeline.md) |
| 场景、数字孪生与仿真 | [03 RobotStudio、Process Simulate、Isaac Sim、MuJoCo、Gazebo 及汽车分支](industry/chapters/03_scene_sim.md) | [03 动力学与接触](advanced/chapters/03_dynamics_contact.md)、[11 仿真求解](advanced/chapters/11_simulation.md) |
| 合成数据与示范扩增 | [04 Replicator、Mimic 与 Cosmos 分支](industry/chapters/04_synthetic.md) | [07 模仿与生成策略](advanced/chapters/07_imitation_generators.md)、[09 世界模型](advanced/chapters/09_world_models.md)、[10 数据工程](advanced/chapters/10_data_pipeline.md) |
| 训练、微调与模型 | [05 训练与实验管理](industry/chapters/05_training.md)、[06 模型与商业智能平台](industry/chapters/06_model_platforms.md) | [06 表示与 VLA](advanced/chapters/06_representation_vla.md)、[07 BC、扩散与 Flow](advanced/chapters/07_imitation_generators.md)、[08 强化学习](advanced/chapters/08_rl.md)、[09 世界模型](advanced/chapters/09_world_models.md) |
| 感知、规划与控制 | [07 Isaac ROS、MoveIt、cuRobo、Nav2、ros2_control 与工业控制接口](industry/chapters/07_perception_control.md) | [02 几何与运动学](advanced/chapters/02_robot_geometry.md)、[03 动力学](advanced/chapters/03_dynamics_contact.md)、[04 感知与估计](advanced/chapters/04_estimation_slam.md)、[05 规划与控制](advanced/chapters/05_planning_control.md) |
| 边缘推理与工业宿主 | [08 Jetson、TensorRT、IGX、ONNX Runtime、OpenVINO、Industrial Edge](industry/chapters/08_edge_deploy.md) | [12 通信、调度、GPU 推理与故障](advanced/chapters/12_runtime.md) |
| 验证、回放与测试 | [09 Applied Intuition、SCALEXIO、日志与回放](industry/chapters/09_validation.md) | [13 指标、统计与诊断](advanced/chapters/13_evaluation.md)、[14 数值练习](advanced/chapters/14_workbook.md) |
| 多机调度与业务交接 | [10 MiRFleet、InOrbit、Open-RMF、Formant](industry/chapters/10_fleet_operations.md)、[11 客户案例](industry/chapters/11_solutions_cases.md) | [01 系统职责](advanced/chapters/01_system_model.md)、[12 运行接口](advanced/chapters/12_runtime.md) |

这些是阅读定位，不代表表中产品功能等同或互相替代。产品获取、部署方式、接口和现场证据见各章卡片及 [CSV](industry/products.csv)／[JSON](industry/products.json)。

## 代码与练习

以下命令从本专题目录执行，只使用 Python 标准库，不联网、不连接硬件：

```bash
python examples/feedback_demo.py
python advanced/examples/numerical_workbook.py
python scripts/check_archive.py
python -m unittest discover -s scripts/tests -v
```

反馈程序演示扰动与反馈；数值练习包含 11 组断言。教学参数不能用于真实设备。归档检查只验证文件、链接和记录一致性，不测试产品性能或模型效果。

- [反馈教学程序](examples/feedback_demo.py)
- [原理篇数值练习](advanced/examples/numerical_workbook.py)
- [评测协议工作表](templates/evaluation_protocol.md)
- [产品与方案笔记模板](templates/product-solution-note.md)

## 来源、构建与归档

- [行业篇说明](industry/README.md)、[来源表](industry/sources.json)、[检查摘要](industry/qa/review.md)
- [原理篇说明](advanced/README.md)、[论文元数据](advanced/papers.json)、[来源表](advanced/sources.json)、[检查摘要](advanced/qa/review.md)
- [概念地图构建说明](concept-map.md)、[论文元数据](papers.json)
- [GTC 报告说明](conferences/gtc-berlin-2026/README.md)
- [归档记录](archive-notes.md)：文件保留范围、日期口径与校验方式

`chapters/` 保留两册分章稿，`notes/` 保留研究记录；构建脚本和依赖锁文件随资料归档。依赖包、历史导出版和重复检查截图不入库，原工作目录及成品没有被移动或删除。
