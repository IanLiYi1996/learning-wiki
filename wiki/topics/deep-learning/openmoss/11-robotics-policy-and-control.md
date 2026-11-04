# RoboOmni 与 FRoM-W1：从理解人的意图到执行机器人动作

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

机器人听到“我有点渴”，面对的还不是一条完整控制指令。它需要判断谁在说话、对方偏好什么、附近有哪些物体，以及是否应该先问一句。
另一类机器人已经知道要“模仿大象”，却仍得解决双脚站稳、关节可达和运动跟踪的问题。
RoboOmni 与 FRoM-W1 分别从这两个缺口出发：前者研究情境中的操作意图，后者把语言生成的人体运动落到人形控制器。[RoboOmni §1][R-paper]、[FRoM-W1 §1–2][F-paper]

把两者放在一起读，重点不在“语言模型也能输出动作”，而在动作究竟是什么。RoboOmni 输出机械臂的末端增量控制；H-GPT 输出人体运动表示，后面还有重定向和跟踪策略。
这两种输出都需要执行系统解释，不能仅凭生成 token 就判断物理任务完成。

本文讨论策略与控制，世界建模和规划另见[世界建模与具身规划专题](05-world-action-and-embodied-agent.md)。“生成未来身体运动”与“预测给定动作之后的未来环境”不是同一个问题；对话确认也不等于宿主强制执行的权限检查。

## 1. RoboOmni：先弄清要做什么，再把确认后的意图转成动作

### 1.1 omni-context 为什么比语音转文字更难？

这里的 RoboOmni 是 *Proactive Robot Manipulation in Omni-modal Context*，读取版本为 `2510.23763v3`。它不是同名的 *Actions Are Just Another Modality for Vision-Language Models*；两篇工作不能混用实验成绩。
论文研究的 cross-modal contextual instruction，要求从视觉、说话内容、语调和环境声音中推断隐含请求。[R-paper]

OmniAction 将情境分成情绪线索、重叠说话、非语言声音、说话人身份、双人对话和三人对话。比如门铃本身不是“放鱼丸”的指令，只有前面的约定说明了这个声音意味着什么。
身份线索则要求把偏好归给正确的人，而不是只识别一句话里出现了哪种食物。[RoboOmni §3.1、图1][R-paper]

普通 ASR 转录可以保留词语，却未必保留否定语气、声音事件和说话人关系。这是输入的信息差异，不应全部归为下游策略“推理较弱”。
本文的判断是：公平比较至少要分开“输入已经丢失线索”和“线索齐全但模型判断错误”。

### 1.2 Perceiver、Thinker、Talker、Executor 各自做什么？

Perceiver 沿用 Qwen2.5-Omni 的多模态编码方式，把当前图像、音频与文本历史送入 Thinker。Thinker 在扩展词表中自回归生成回复或动作符号；Talker 将回复及语义表示转换成语音；
Executor 把离散动作符号还原为连续控制。论文的骨干配置是 Qwen2.5-Omni-3B。[RoboOmni §4、§5.1][R-paper]

按论文的任务设计，可把交互读成下面的顺序；它是行为组织方式，不是已经验证的安全状态机：

```text
当前画面＋语音／环境音＋对话历史
    → 推断对象、动作和请求者
    → 生成澄清问题，接收确认
    → 动作 token → 连续动作块 → 机器人执行
```

训练目标把回复与专家动作统一成 next-token 最大似然。对话样本监督文字回复，操作样本监督动作 token，两类 batch 交替进入训练。
正文 §4.3 的目标没有未来环境观测预测项，也没有通过真实任务回报训练的在线探索环节。[R-paper]

因此，这里的“端到端”描述多模态理解与动作生成的学习连接。它不意味着词表、动作解码、夹爪约定和底层控制器都消失了，也不意味着整个系统具有世界模型。
与世界建模的区别就在输出目标：这里先问“该回复什么、该发什么动作”，后者继续追问“这个动作会造成什么后果”。

### 1.3 FAST+ 压缩的是连续动作块，不是物体或技能名称

RoboOmni 采用上游 FAST+，向 Thinker 词表加入 2,048 个动作符号。七维控制包含末端平移、旋转和夹爪分量；实验配置使用六步 action chunk。
2,048 是词表大小，既不是每一步固定生成 2,048 个 token，也不是 2,048 种预定义机器人技能。[RoboOmni §4.1–4.2、§5.1][R-paper]

FAST 原文 §V 的过程是：归一化动作，沿时间轴分别做离散余弦变换，量化频域系数，
再把系数展开，用 BPE 压缩为离散序列。FAST+ 提供在多种机器人数据上训练的通用词表。
时间上平滑、相邻步重复的信息因此不必逐维逐步写成很长的 token 序列。[FAST §V、图4][FAST]

解码需要逆向还原系数和动作，再用匹配数据集的统计量反归一化。BPE 压缩与系数量化是两个环节；前者不等于后者的重建无损。
这也解释了为什么同一个语言模型换掉动作单位、chunk 长度或夹爪符号后，仍可能在执行端失败。

固定源码 `train_omni.py` 的 `process_example` L176 调用 FAST processor，
`map_fast_token_to_vlm_action` L170 把结果写成 `<robot_action_i>`。
推理侧 `RoboOmni.inference` L368–410 提取动作 token、减去词表偏移、FAST decode，再执行反归一化。[R-train]、[R-util]

本文推导：FAST+ 降低表达连续动作的序列成本，但不替模型判断抓哪一个物体。错误意图可以被编码成一段平滑、格式正确的动作；正确意图也可能因控制接口不匹配而执行失败。
应分别记录意图正确率、动作解码误差和闭环任务成功，不能用其中一项替代另外两项。

### 1.4 OmniAction 怎样把机器人轨迹变成多模态情境？

OmniAction 的作者自报规模为 141,162 个 episodes；基本样本是对话、视觉序列和动作轨迹的组合。用户轮次以音频表示，机器人回复以文字表示，`[ACT]` 标记进入操作的时刻。
其中动作来自已有机器人示范，情境对话不是同等数量的现场人机互动记录。[RoboOmni §3.1–3.2][R-paper]

构建先从 Open-X Embodiment 的任务与轨迹出发，用 GPT-4o 改写为含隐含意图的家庭对话，
加入后续人机确认，再检查改写意图是否仍对应原任务。
这一设计保住了动作监督，但也意味着轨迹与新对话的匹配依赖脚本构造和质量检查。[RoboOmni §3.2][R-paper]

音频由 MOSS-TTSD、CosyVoice、Gemini-TTS 等生成，随后加入多人重叠、声音事件和背景声。不同角色可使用一致音色，同一脚本可以改变声学条件。
作者还进行了抽样人工核验；这支持被检查样本的意图可恢复性，不能视为真实家庭语境覆盖率。[RoboOmni §3.2、附录 A][R-paper]

本文认为最需要检查的是脚本捷径：某个音色、固定问句或声音事件是否总对应同一目标。若模型靠这些关联选动作，换成新的说话人关系或相同词语的相反语气时就可能失效。
这是评测建议，不是本文已经发现的数据泄漏。

### 1.5 合成语音仿真、真人语音仿真与真机实验必须分开

| 证据层 | 输入与执行世界 | 作者报告 | 可以据此判断什么 |
|---|---|---|---|
| OmniAction-LIBERO-TTS | 合成情境音频；LIBERO 仿真执行 | Table 1 总体成功率 85.6% | 在所构造情境任务上的操作能力 |
| OmniAction-LIBERO-Real | 真人录制的直接语音指令；仍在 LIBERO 执行 | Table 2 总体 76.6%，ASR＋π0 为 73.8% | 真实语音条件下的仿真操作能力 |
| WidowX 250S | 经过本地示范微调；真实机械臂执行 | §5.4、图5及附录 B 的成功案例 | 意图确认到物理执行的示例可行性 |
| 主动帮助评估 | 判断用户意图与比较澄清回复 | §5.5、图6 的意图识别与对话分析 | 不能直接当机械臂成功率 |

TTS 设置从四套共 40 个 LIBERO 操作任务产生六类情境，共 240 个评测任务变体。“240”不是论文明确报告的全部独立机器人试验次数。
Table 1 中 Long 的 79.5% 也低于 Spatial 的 93.0%，总体平均掩盖了任务结构的差异。[RoboOmni §3.3、§5.2][R-paper]

真人语音设置的 “Real” 修饰语音来源，不修饰执行平台；§5.3 又明确研究直接语音指令。
它和 TTS 的六类隐含情境不完全同分布，不能把 85.6% 减去 76.6% 解释为纯粹的合成到真实语音性能损失。
真实机械臂证据应单列：论文展示了确认后抓取放置，但未提供本文可据以审计总体成功率的完整试验账本。[RoboOmni §5.3–5.4、附录 B][R-paper]

文字基线接收的是转录文本，不必然是已经消歧的正确操作命令。因此，较低得分可能混合了线索损失、意图理解和控制问题。
§5.6 另有 omni 模型作为 Planner 的级联比较，也仍需核对训练、接口和预算，不能推成所有模块化控制都更差。[R-paper]

### 1.6 对话中的确认，是否真的约束了动作模式？

公开工具类维护 `history` 与 `action_mode`，先生成回复，随后看到 `[ACT]` 才切换动作生成。
但 `inference` L416–420 还有 `len(self.history) >= len(task_item)` 的强制切换分支。
这里的 `task_item` 是 dict，比较的是映射键数，不是独立确认状态。[R-util]

这段代码不能被解释成用户拒绝时动作一定被禁止。论文案例中的礼貌询问、模型训练中学到的确认行为，与宿主独立验证“允许执行”是不同保障。
ETA 的执行契约讨论后者；本篇只确认这条启发式分支存在，未运行拒绝场景测试。

训练入口 `load_model_and_processor` L321 加载 Thinker，并在 L338 冻结 `audio_tower`；
`collate_fn` L263 对输入和 padding 作监督屏蔽，保留最后一个 assistant 输出的训练信号。
这说明开放了可核验的多模态训练路径，不证明 Talker 同时完成同范围联训。[R-train]

复现还需处理具体入口：LIBERO 脚本 L33 导入 `roboomni_utils_chatmode`，
而既有目录核查未找到该模块；默认十次 rollout、seed 7 也只是仓库默认。
脚本 L95 又把 FAST horizon 设为 6，不能把工具类构造器中的默认 1 步当作论文配置。[R-eval]

真实机械臂入口 `run_widowx.py` L82–87 加载 Nora，而不是同名 RoboOmni；
公开 Nora 工具类使用 Qwen2.5-VL。它不能充当完整语音确认栈的复现证明。
本文没有修补这些代码，也没有把静态依赖缺口解释成论文实验没有发生。[R-real]、[R-nora]

## 2. FRoM-W1：人体运动是中间表示，机器人还需要一个稳定的跟踪器

FRoM-W1 的读取版本为 `2601.12799v1`。它研究语言到人形全身运动，不以机械臂物体操作为主任务。人体动作数据远多于语言标注的机器人全身数据；先学人体运动，再适配机器人，可利用这部分数据。
代价是生成、重定向、控制和真实部署各有一层误差，必须分别验收。[FRoM-W1 §1–2][F-paper]

### 2.1 H-GPT 输出什么？CoT 起什么作用？

H-GPT 先用 VQ-VAE 编码人体全身运动，再将离散码加入语言模型词表。连续表示包括位置、速度、旋转和手部特征；当前 H-GPT 文档描述的是 623 维 SMPL-X 运动特征。
它不是直接给 H1 或 G1 发关节力矩。[FRoM-W1 §2.2][F-paper]、[H-GPT 文档][F-hgpt]

训练时，运动经过编码器、最近码本量化和解码器重建；语言生成器学习指令、CoT、运动 token 的序列。
推理时不需要真实目标运动，先生成 CoT，再生成运动码，由 VQ-VAE decoder 还原连续运动。
当前源码 `VQVae.encode/decode` L92/L108 和 `HumanoidGPT` 的语言、运动训练分支对应这层划分。[F-vq]、[F-model]

论文的 CoT 是将抽象描述拆成身体动作的语义中介，可写为：

$$
p(M_h,C\mid I)=p(C\mid I)\,p(M_h\mid I,C).
$$

这里 $I$ 是指令，$C$ 是动作描述，$M_h$ 是人体运动。它解释“象鼻式挥臂”怎样转为身体部位和动作先后，不负责证明机器人质量、重心和接触力可行。
CoT 也不是对预测环境后果进行搜索的规划器。[FRoM-W1 §2.2.1–2.2.3][F-paper]

生成器使用 Llama-3.1-8B 与 LoRA；HumanML3D-X 扩展原有身体运动以包含手部，
Motion-X 提供更多人体片段，另由 GPT-4o 增广动作描述。
这些来源不能写成机器人在线探索数据；Motion-X 和人体参数模型还各有授权要求。[F-paper]、[F-hgpt]

### 2.2 重定向解决形态差异，但不保证动力学稳定

人体手腕、腿长、关节自由度与机器人不同，运动不能直接逐关节复制。§2.3.1 先从三维关键点重建 SMPL-X 姿态，再优化机器人关节，使对应身体点的位置和方向接近人体参考；
正则项处理关节限位等约束，手部另对齐指尖位置。[F-paper]

论文图4还说明了身体姿态、手腕朝向和手指优化的分工。重定向后的产物是机器人参考轨迹，仍需跟踪策略决定在重力和控制误差下怎样执行。
一个逐帧可达的姿势序列，也可能因变化太快、支撑不足或自碰撞而无法连续完成。

后一句是控制层面的解释，不是本文新增测试。需要分别看运动重建误差、重定向误差与实际跟踪误差；只看生成动画的流畅程度，不能判断最后一项。
H-ACT 文档把重建、retarget、policy training 与部署明确分为不同步骤。[F-hact]

### 2.3 PPO 教师与 DAgger 学生：哪些信息允许在真机使用？

默认 H-ACT 在 IsaacGym 中训练 privileged teacher，用 PPO 优化跟踪和稳定性回报。回报约束参考运动误差、摔倒和不合理的控制变化；AMASS 重定向运动用于通用预训练。
学生随后以 DAgger 方式模仿教师，用较受限、可部署的观测和运动目标产生动作。[FRoM-W1 §2.3.2、§3.2][F-paper]

| 阶段 | 可使用的信息 | 输出或监督 |
|---|---|---|
| PPO 教师训练 | 仿真完整状态与丰富的参考运动，包括未来参考 | 控制动作，由跟踪、稳定性等回报优化 |
| DAgger 学生训练 | 部署兼容的本体观测与简化运动目标 | 模仿教师动作，补足学生访问状态上的误差 |
| 真机学生执行 | 机载观测与已给定的运动命令 | 输出交给低层控制器，实际身体状态反馈继续参与 |

为避免论文紧凑记号掩盖观测差别，可把蒸馏理解为最小化
`||πS(o_onboard, r_small) − πT(o_privileged, r_rich)||²`。
这只是本文对 §2.3.2 式(6)的信息边界解释，不是另一套已实现训练目标。
DAgger 的目的也不只是复制固定教师轨迹，而是缓解学生动作导致访问状态变化后的误差积累。

教师知道的“未来参考”是已经提供的目标运动，不是真机未来会怎样运动的真实观测。学生还需要运动命令；“不使用特权状态”不意味着不给任何目标。
默认学生简化目标含头部与双手等关键点，不能把教师的完整状态要求直接搬到机载推理。[F-paper]

论文 RL 实验使用 19-DOF H1、21-DOF G1 的身体配置，不把手指关节全部加入 RL。手部运动主要直接重定向，身体策略负责稳定跟踪。
这里的 DOF 数是所用训练配置，不是这两类机器人所有硬件版本的总自由度，更不证明灵巧接触操作已经解决。[FRoM-W1 §3.2][F-paper]

### 2.4 仿真 RFT 是目标运动适配，不是持续实机学习

推理阶段先取得一条生成并重定向的目标运动，再用预训练策略初始化，
在仿真中针对这条参考继续训练教师，重新蒸馏学生，最后部署适配后的策略。
这里的更新对象主要是跟踪器，不是 H-GPT 语言模型或预测环境的世界模型。[FRoM-W1 §2.3.2][F-paper]

因此，论文的“inference-time RFT”允许生成后增加优化预算，不能理解成一次语言模型前向就完成全部控制，也不能理解成机器人边做真实任务边自动积累通用技能。
若要证明持续学习，还需检验多任务保留、遗忘、安全性和真实反馈更新，目前这组实验没有给出这样的证据。

§3.2 的 RFT 比较随机选取 30 条 AMASS 运动，比较从零训练、仅预训练和再微调。
图10–11 报告微调后的跟踪改善；作者说约 500 个微调 step 已可观察到改善。
它不是 500 个真实机器人动作，也没有直接给出所有新指令都能在固定实时预算内适配的保证。[F-paper]

### 2.5 运动生成好、跟踪好、任务完成好，是不同分数

| HumanML3D-X，作者 Table 1 | FID，越低越好 | 文本检索 R Top-1，越高越好 |
|---|---:|---:|
| T2M-GPT | 0.677 | 0.357 |
| H-GPT，无 CoT | 0.229 | 0.333 |
| H-GPT，有 CoT | 0.255 | 0.332 |

这组结果支持 H-GPT 的运动分布更接近测试数据，却不支持所有语义指标都领先。CoT 在分布内 FID 略差；Table 2 的改写和文字噪声测试则改善，
对应 FID 分别由 0.455 到 0.355、由 0.830 到 0.602。[FRoM-W1 §3.1、Table 1–2][F-paper]

作者还发现扩大到 Motion-X 后，并非所有标准测试都优于只用 HumanML3D-X。其关于自动标注与姿态估计质量的解释是作者推测，不能当作已被消融确定的原因。
数据更多、语言鲁棒、身体稳定之间没有一个总分可以直接换算。[FRoM-W1 §3.1，Motion-X 扩训分析][F-paper]

H-ACT 的 MPJPE、速度/加速度误差和 SR 衡量运动跟踪，H-GPT 的 FID 和文本检索衡量生成。两者都不是物体是否真正被拿起、是否完成环境交互的成功率。
对需要接触物体的应用，还必须增加对象状态、接触结果和执行安全的独立验收；这是本文依据这些指标定义提出的评测要求。[FRoM-W1 §3.1–3.2][F-paper]

### 2.6 H1/G1 实机展示了什么，哪里仍会失败？

§3.3 的部署把 H-GPT 放在边缘 4090 工作站，运动重定向后传给机器人，
H-ACT 控制策略运行在机载计算板；RoboJuDo 适配不同控制策略的命令格式与设备通信。
这是一条有物理执行证据的分层管线，而不是所有推理都在机器人上完成。[F-paper]、[F-hact]

图13展示 H1/G1 模仿大象、拉琴式动作，以及先走动再模拟接电话。其中动作表达不应升级为真实演奏或完整物体操作；图14另示不同控制器的部署兼容性。
正文定量跟踪实验与这些实机展示的分母不同，不能把仿真 SR 填成真实机器人成功率。[FRoM-W1 §3.2–3.3、图13–14][F-paper]

失败证据也应保留：图15有 G1 极端下蹲失稳及快速向前运动跟踪失败。作者讨论了生成动作与指令不匹配、自碰撞和 sim-to-real gap。
所以“可以在 H1/G1 上演示”支持部署可行性，不支持任意指令、任意速度或长期无人值守控制。[F-paper]

公开实现也分层开放：`H-GPT/hGPT/models` 有生成、编码和评测组件，
H-ACT 的 retarget、human2humanoid、RoboJuDo 通过子模块接入，需保留各自版本与外部依赖。
仓库 README 仍列 teacher 权重 TBD、AMASS-G1 链接待发布；H-GPT 文档说明实际训练 launcher 要自行组织 Lightning Trainer。[F-model]、[F-sub]、[F-repo]、[F-hgpt]

## 3. VLABench：用来拆开语义与执行，不替任何策略背书

VLABench 对应 `2412.18194`，最初公开于 2024 年，后发表于 ICCV 2025。它提供 MuJoCo/dm_control 任务、资产和示范流水线，覆盖对象辨认、常识、复杂指令与长程组合。
本文用它说明怎样评价策略，不声称 RoboOmni 或 FRoM-W1 已完成这里的统一对照实验。[V-paper]、[V-final]

正式版分别报告 IS、PS、SR：接近正确操作对象、完成子任务比例、严格任务成功。这适合定位“理解了对象但没有做成”和“只完成前几个步骤”的差别。
VLM 的技能/参数/DAG 匹配分数属于另一种评测，不能直接当真实动作完成率。[VLABench ICCV §3.3–4.1][V-final]

固定代码 `ConditionSet.is_met` L309 要求子条件同时满足，`met_progress` L316 计算满足比例。`PourCondition` L178 以倾斜几何关系做代理，没有在该条件中模拟液体流动。
因此“通过某任务条件”需要连同判定实现解释，不能自动升级为真实倒液体等价验证。[V-cond]

版本尤其不能混用：arXiv v1 的 progress 定义、ICCV 正式版的长程 composite Track 6，
与当前 README 的 `track_6_unseen_texture` 不是同一协议。
正式版五任务、每任务 200 示范的设置，也不能与当前十任务、每任务 500 样本直接并入一个结果表。[V-paper]、[V-final]、[V-repo]

补充材料 §10.2 的真实 Select Mahjong 小实验，作者报告仅真实数据为 `3/20`，
加入仿真数据后为 `5/20`。这是一项有限的数据利用证据，不是整个基准的实机验证。
本文没有据此推断稳定的泛化收益。[V-supp]

若用于 RoboOmni，需新增并冻结语音、说话人、确认/拒绝与原任务意图的对应关系，分别测消歧和执行。
若用于 FRoM-W1 的环境交互，需先定义适合人形的控制接口和物体状态验收，不能照搬机械臂 task SR。
这是拟议评测设计；VLABench 本身不会替模型补上这些能力。

## 4. 策略、控制与世界建模怎样衔接？

RoboOmni 的主要问题是多模态情境怎样改变意图与动作；FRoM-W1 的主要问题是人体参考怎样变成稳定控制。[世界建模与规划专题](05-world-action-and-embodied-agent.md)研究未来环境与动作的信息耦合，以及执行证据由谁认可。
它们可以讨论组合，但没有证据支持这些项目已经共享同一骨干、训练闭环或已评测部署栈。

对 RoboOmni，最有区分力的测试是保留相同转录词语，只改变语调、请求者或环境声音，
再加入明确拒绝与中途撤回。固定模型、动作接口和预算，记录错误执行是否真的被阻止。
`[ACT]` 触发、对话准确率和独立执行权限应分别检查，不用一个成功案例替代整个拒绝测试。

对 FRoM-W1，应冻结生成参考，分别测试重定向、未经 RFT 的学生、等预算 RFT 学生和真实执行。
把生成失败、跟踪失败、硬件安全停止分开统计，同时测原有运动是否因适配而回退。
这些是本文建议；未经复跑，不能写成项目已经完成的消融或安全保障。

## 资料、版本与复现口径

| 论文 | 作者 | 采用版本与发表信息 |
|---|---|---|
| RoboOmni: Proactive Robot Manipulation in Omni-modal Context | Siyin Wang 等 | `2510.23763v3`；ICLR 2026 |
| FRoM-W1: Towards General Humanoid Whole-Body Control with Language Instructions | Peng Li 等 | `2601.12799v1`；2026 技术报告 |
| VLABench: A Large-Scale Benchmark for Language-Conditioned Robotics Manipulation with Long-Horizon Reasoning Tasks | Shiduo Zhang 等 | `2412.18194v1` 与 ICCV 2025 正式版分开使用 |

材料核查于 2026-10-17。实验成绩和数据规模为作者报告，解释性推导与评测建议为本文分析；未运行模型或操作真实机器人。
RoboOmni 固定 SHA 为 `935b3d7fa5d1`，
FRoM-W1 为 `457d84d44e63`，VLABench 为 `cf588fe60c0c`。
当前源码与论文历史实验环境的逐项对应尚未确认。

[R-paper]: https://arxiv.org/html/2510.23763v3
[FAST]: https://arxiv.org/pdf/2501.09747v1
[R-train]: https://github.com/OpenMOSS/RoboOmni/blob/935b3d7fa5d1fcd55d6ab32ba8d4fa1285961895/training/train_omni.py#L170
[R-util]: https://github.com/OpenMOSS/RoboOmni/blob/935b3d7fa5d1fcd55d6ab32ba8d4fa1285961895/experiments/libero/roboomni_utils.py#L238
[R-eval]: https://github.com/OpenMOSS/RoboOmni/blob/935b3d7fa5d1fcd55d6ab32ba8d4fa1285961895/experiments/libero/run_libero_eval.py#L33
[R-real]: https://github.com/OpenMOSS/RoboOmni/blob/935b3d7fa5d1fcd55d6ab32ba8d4fa1285961895/experiments/bridge/run_widowx.py#L82
[R-nora]: https://github.com/OpenMOSS/RoboOmni/blob/935b3d7fa5d1fcd55d6ab32ba8d4fa1285961895/experiments/bridge/nora_utils.py#L4
[F-paper]: https://arxiv.org/html/2601.12799v1
[F-hgpt]: https://github.com/OpenMOSS/FRoM-W1/blob/457d84d44e638c1070473dd48cedde19752cad09/H-GPT/README.md
[F-vq]: https://github.com/OpenMOSS/FRoM-W1/blob/457d84d44e638c1070473dd48cedde19752cad09/H-GPT/hGPT/models/archs/hgpt_vq.py#L92
[F-model]: https://github.com/OpenMOSS/FRoM-W1/blob/457d84d44e638c1070473dd48cedde19752cad09/H-GPT/hGPT/models/hgpt.py#L14
[F-hact]: https://github.com/OpenMOSS/FRoM-W1/blob/457d84d44e638c1070473dd48cedde19752cad09/H-ACT/README.md
[F-sub]: https://github.com/OpenMOSS/FRoM-W1/blob/457d84d44e638c1070473dd48cedde19752cad09/.gitmodules
[F-repo]: https://github.com/OpenMOSS/FRoM-W1/blob/457d84d44e638c1070473dd48cedde19752cad09/README.md
[V-paper]: https://arxiv.org/html/2412.18194v1
[V-final]: https://openaccess.thecvf.com/content/ICCV2025/papers/Zhang_VLABench_A_Large-Scale_Benchmark_for_Language-Conditioned_Robotics_Manipulation_with_Long-Horizon_ICCV_2025_paper.pdf
[V-supp]: https://openaccess.thecvf.com/content/ICCV2025/supplemental/Zhang_VLABench_A_Large-Scale_ICCV_2025_supplemental.pdf
[V-repo]: https://github.com/OpenMOSS/VLABench/blob/cf588fe60c0c7282174fe979f5913170cfe69017/README.md
[V-cond]: https://github.com/OpenMOSS/VLABench/blob/cf588fe60c0c7282174fe979f5913170cfe69017/VLABench/tasks/condition.py#L178
