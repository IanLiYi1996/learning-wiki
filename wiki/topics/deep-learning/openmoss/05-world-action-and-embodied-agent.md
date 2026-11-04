# OpenMOSS 的世界建模与具身规划：预判后果，执行后求证

资料核查：2026-10-17。[专题首页](README.md) · [学习路线](learning-roadmap.md) · [来源与版本](sources.md)

机器人把杯子放到托盘，既要选择动作，也要确认杯子是否抓住、是否放稳。命令执行完，并不总表示物体已经到位；下一步需要依据新观测。[ETA §1–4][P]

这里的“动作”有不同尺度。D2PO 和 World-Aware-Planning（下文简称 WAP）选择 `open microwave` 等符号操作，具体运动交给环境控制器；EasyWAM 生成连续动作块并学习未来观测；ETA 管理工具授权、观测更新和任务验收。若不区分这些接口，把语言规划成功率与机器人控制成功率放在一起，就无法判断收益发生在哪一层。[D2PO §3、附录 A.1–2][DP]、[WAP 附录 A][WP]、[EasyWAM][M]、[ETA §3–4][P]

本文按“如何学习任务规划、如何生成动作与未来、如何验证真实执行”组织。下表是方法定位，不表示四个项目已经组成同一系统。

| 工作 | 训练或运行时学／维护什么 | 推理时是否显式比较预测后果 |
|---|---|---|
| D2PO | 联合优化动作偏好与下一状态描述偏好 | 论文推理直接选下一动作；树搜索用于收集训练数据 |
| WAP | 场景相关指令、逐步理由和课程训练 | 读取视觉历史后选符号动作；没有物理 rollout 搜索 |
| EasyWAM | 视频与动作的联合、单向或级联建模 | 当前所查接口没有多候选后果重排 |
| ETA | 授权、执行回执、新观测及经验晋级证据 | 可以重规划；是否完成由环境证据验证 |

各行分别依据 [D2PO §3][DP]、[WAP §3][WP]、[EasyWAM 推理源码][U]和 [ETA §3–4][P]。动作表示、策略解码、运动重定向与机器人控制另见[机器人策略与控制专题](11-robotics-policy-and-control.md)。

D2PO 与 WAP 的纳入依据是 `sii-research/OpenMOSS` 官方总览的 “Selected Research → Embodied-AI”：总览明确列出两项工作，并链接 `sinwang20/D2PO` 和 `sii-research/World-Aware-Planning`。因此研究范围按官方收录确定，不限于 `OpenMOSS` GitHub org 内的仓库；收录本身不证明这些项目共享训练流水线或已完成系统集成。[固定版本总览 L127–128][OM]

## 1. 预测后果、生成策略与逆动力学

令 $c=(o_{\le t},l,s_t)$ 为部署时可得的观测历史、指令和本体状态，$A$ 为未来动作块，$F$ 为未来观测或潜变量。WAM 综述 §2、§4 的定义提供联合分布与级联分类；以下补上信息边界，而非复述项目命名。[综述][W]

$$
\underbrace{p(F\mid c,A)}_{\text{action-conditioned world prediction}},\qquad
\underbrace{p(A,F\mid c)}_{\text{joint policy/world modeling}}
=p(A\mid c)p(F\mid c,A)
=p(F\mid c)p(A\mid c,F).
$$

第一项回答“指定动作之后会怎样”，不负责选择动作；联合模型可同时采样动作和未来，但未必有候选动作比较、价值函数或搜索。后一分解中的 $p(A\mid c,F)$ 是 IDM：训练可从真实起终状态反推动作；部署必须另外提供目标状态或生成的未来，不能偷用真实 $F$。最终策略实际是 $\int p(A\mid c,F)p(F\mid c)\,dF$，不是训练时已知未来的条件预测。等式是概率链式法则；架构是否实现相应条件接口仍需读码。

示范数据学到的 $p(F\mid c,A)$ 也未自动等于 $p(F\mid c,\mathrm{do}(A))$。隐藏接触状态可能同时影响专家动作和未来；条件相关性不能替代干预预测。判断一个模型是否支持规划，还要检查它能否固定候选动作、预测相应后果，以及决策程序是否真的利用这些预测。联合生成视频与动作不自动包含这套程序。

## 2. D2PO：把动作后果学进规划模型

D2PO 的问题是：只模仿成功动作，模型容易学会表面顺序，却不理解“先打开容器才能放入物体”等前置条件。它把同一个 LVLM 用于动作选择和状态预测，后者输出物体属性、空间关系与持有状态的自然语言描述，而不是下一帧图像或连续物理状态。[论文 §1、§3.3][DP]

训练数据来自模拟器中的逐步树搜索。论文配方为每个状态采样 5 个动作，最多搜索 25 步；GPT-4o 给出 0–5 的目标进度评分，环境可执行性取 0／1 后放大到 0／5，两项等权平均，按阈值筛选分支。达到目标后回溯成功路径：路径上的理由—动作作为 chosen，同一节点的其他候选作为 rejected。源码也先恢复场景、重放既有动作，再实际执行候选；这些训练后果来自模拟器试错，不是模型自行想象出的标签。[§3.2、附录 B.1][DP]、[树搜索 L345–449][DPC1]、[混合评分 L641–645][DPC2]

状态偏好对有一个容易漏掉的细节：固定当前图像与 chosen 动作，把其执行后的描述作为正例，把兄弟动作造成的其他状态作为负例。GPT-4o 根据图像和环境 metadata 生成描述，输出还先复述当前状态，再预测下一状态。比如输入 `open microwave`，正例是微波炉打开，负例却描述冰箱变得可见。它检验动作与结果的辨别能力，但不是对同一动作全部可能结果的概率校准。训练标签使用环境 metadata，与部署模型能否直接读取 metadata 也须分开说明。[§3.2–3.3、附录 B.2][DP]

用统一记号写 DPO 的单对损失：

$$
\ell(q,y^+,y^-)
=-\log\sigma\!\left[
\beta\left(
\log\frac{\pi_\theta(y^+\mid q)}{\pi_{\rm ref}(y^+\mid q)}
-\log\frac{\pi_\theta(y^-\mid q)}{\pi_{\rm ref}(y^-\mid q)}
\right)\right],
\qquad
\mathcal L=\mathcal L_{\rm action}+\lambda\mathcal L_{\rm state}.
$$

动作任务的上下文是目标、观测与动作历史，输出是理由—动作；状态任务的实现以图像和动作作输入、当前／下一状态描述作输出。论文先全参数 SFT 3 epochs，再做 1 epoch 双偏好训练，取 $\lambda=1$；公开数据列出约 4.5k SFT、15k 动作偏好和 8.7k 状态偏好样本。普通 DPO 仅保留动作目标，是主要消融。[§3.3、§4.1.4][DP]、[数据发布清单][DPR]

推理不用再生成候选未来或调用树搜索：模型根据当前画面、历史动作及执行反馈，输出下一步理由、动作和对象，再等待环境返回新观测。[`evaluate2.py`][DPC4] 接入普通 evaluator，[`evaluate3.py`][DPC5] 才接入采集用 tree evaluator。这一分工支持“世界预测作为训练辅助任务改善策略”，不支持“推理时靠模拟未来搜索取得收益”。[§1、附录 A.1][DP]、[普通评测 L175–242][DPC3]

VoTa-Bench 基于 AI2-THOR／ALFRED／LoTa-Bench：549 个 seen、646 个 unseen 样本，六类家务任务。SR 检查环境最终目标条件；PL 在成功基础上按专家与模型的动作序列长度加权，不能读成每步延迟或机器人能耗。Qwen2-VL-7B 的作者结果如下，单位为 %。[§4.1、表 1–2][DP]

| 训练方式 | Seen SR | Seen PL | Unseen SR | Unseen PL |
|---|---:|---:|---:|---:|
| SFT | 44.63 | 40.33 | 50.77 | 46.70 |
| 动作 DPO | 53.92 | 49.37 | 57.59 | 53.65 |
| D2PO | 58.11 | 53.33 | 61.46 | 57.16 |

本文按表计算，双目标相对动作 DPO 的 SR 增量为 seen 4.19、unseen 3.87 个百分点。LLaVA-1.6-7B 和 Llama-3.2-11B 也有收益，但仍是同类模拟环境中的符号规划结果。§5.3／图 4 还报告 action-conditioned 训练在 seen 较好，goal-directed 状态想象在 unseen 较好；不能据总成功率断言显式动作条件在所有泛化任务上都更优。[DP]

论文 “Limitations” 承认模拟到真实环境的差距和 GPT-4o 采集成本。本文还区分两项证据：策略收益不能单独证明状态描述忠实于接触动力学；状态偏好增加的监督也需要与等量额外训练数据作对照。当前固定源码的分支筛选是 top-2 分数至少 3.2，加上所有分数至少 4.5 的项，与附录 B.1 的单阈值 3.75 不同；不把今天的采集脚本当成论文实验的完整复现配置。[DP]、[当前筛选 L584–608][DPC1]

## 3. World-Aware-Planning：改善指令与场景的对应关系

WAP 处理另一类困难：模型知道“把刀放进容器”，却未必能把“用来切东西的工具”“椅子旁的容器”等说法对应到当前画面。它保留 ALFRED 专家动作轨迹，用教师模型扩写指令并补写逐步理由，再训练 LVLM 在视觉历史上选择符号动作。论文没有把理由当成物理模拟器，也没有训练 $p(F\mid c,A)$ 的视频后果接口。[§3.1–3.3][WP]

数据增强覆盖外观、空间、功能和指代句法。例如用颜色与形状标识对象，用邻近地标指定位置，用“切东西的工具”代替刀的名称，或加入代词和背景叙述。教师生成指令时可看轨迹终帧；语义核验可看原指令和整段观测，五次核验至少四次通过，否则重新生成。它们属于训练数据构建条件，不能据此说部署学生也获得未来帧。[§3.2 式 2–3][WP]、[指令生成 L29–59][WPC1]

逐步理由尤其不能误读为已验证的内部推理。`generate_reasoning()` 把已知的 `original_action` 交给教师，让它解释为什么下一步动作合适；`process_single_entry()` 再把新理由与原动作拼回样本。这样的后写理由可以形成有用监督，但文字合理性不是因果忠实度证据，也不保证模型在未知接触状态下正确预测后果。[§3.2.3][WP]、[理由生成／写回 L29、L86–115][WPC2]

论文使用 Qwen2.5-VL-72B-Instruct 作教师，主实验学生为 Qwen2.5-VL-7B 和 InternVL3-8B，报告 80,875 组增强指令—轨迹。课程先学原始任务，再学外观／空间增强，最后学功能／句法增强；式 5 是动作预测的交叉熵目标，训练数据包含前述理由标注。推理按 $a_t=f_\theta(I,o_{1:t})$ 反复读取历史视觉观测并决策，不给动作成功文本或任务进度信号。当前 `process_prompt()` 直接返回指令，旧的反馈拼接代码被注释掉；视觉与模型输出历史由对话接口维护。[§3.1、§3.3、§4.1][WP]、[当前 planner L50–175][WPC3]

主要结果来自 EB-ALFRED。表 1 的 harder closed-loop、无动作反馈设置中，Qwen2.5-VL-7B 如下；这些是同一设置内的逐级比较。[表 1][WP]

| 方式 | 平均 SR | Common | Long |
|---|---:|---:|---:|
| 未训练模型 | 2.0 | 2 | 0 |
| Basic Reasoning | 47.0 | 22 | 54 |
| Full Augmentation | 58.0 | 62 | 64 |
| Curriculum Learning | 62.7 | 62 | 70 |

摘要的 +60.7 是 2.0→62.7 的绝对百分点增量，不是相对提升，也不是另一有反馈基线 4.7→62.7 的差值。同设置下 InternVL3-8B 从 6.0 提至 61.0；GPT-4o 为 26.0，Claude-3.5-Sonnet 为 57.3。Claude 的 Long 为 74，仍高于 WAP 的 70，不能写成每类任务都超越商用模型。[表 1][WP]

消融也限定了收益来源：仅增强外观／空间为 46.7，未超过 Basic Reasoning 的 47.0；完整理由替换为 58.0，再加课程为 62.7。表 2 的自选增强课程为 56.7，低于显式课程。六类 SR 的 STD 衡量类别间均衡性，并非重复实验的标准误或置信区间。因此结果支持这组叙事监督与课程配置，不是“文字越丰富，规划一定越好”。[§4.1、表 2–3][WP]

作者附录 A 明确限定为符号动作，未建模连续控制参数；工业、室外动态障碍泛化未验证，中途纠错能力仍有限。附录 B.2 又将 Qwen 学生写成 72B，与 §4.1／表 1 的 7B 不一致，复现实验须核对实际配置。本文据此将 WAP 定位为场景理解和动作前置条件的训练方法，不将其称为可校准的物理世界模拟器。[WP]

## 4. EasyWAM：五种结构怎样使用未来信息？

`build_inputs` 将 RGB `[B,3,Tv,H,W]` 编成 latent `[B,C,Tz,Hz,Wz]`；动作为 `[B,Ha,Da]`，只取首时刻本体状态，文本为 `[B,L,D]`。数据指南的 33 个 action/state 步与 9 个视频时间戳不是同一时间分辨率；MoT 还检查 `Ha % (Tv-1)==0`。[输入构建 L594–705][M]、[数据指南][D]

以 Wan scheduler 为例，训练输入是 $x_\sigma=(1-\sigma)x+\sigma\epsilon$，监督是速度 $\epsilon-x$，不是未来 RGB 的直接重建。初帧 latent 保持干净，未来与动作加噪；总损失为 `λv·Lv+λa·La`。动作 padding 按有效步归一化；视频 padding 经 VAE 时间压缩分组，整组均为 pad 才排除。loss mask、attention mask、加噪选择 mask 不能混为一谈。[scheduler L46–58][S]、[Unified L537–626][U]

下表采用默认 Wan `first_frame_causal`，`V0` 表示初帧、`Vσ` 表示由真实未来加噪所得 token。所有变体训练都有真实未来监督；“看未来”专指动作前向的信息可达性。

| 变体 | 训练动作分支看到什么 | 部署时怎样生成 |
|---|---|---|
| Unified [U] | `Aσ` 读取 `V0,Vσ,Aσ`；视频与动作双向通信 | 共同去噪；`decode_video=False` 只取消 RGB 解码 |
| MoT [M] | 动作只读 `V0,Aσ`；视频不读动作，但视频损失仍训练视觉专家 | 默认缓存初帧后只生成动作；`bidirectional` 配置走联合路径 |
| MoT-Joint [J] | 动作可读全部 `Vσ`，视频仍不读动作 | 同时更新两个流，依赖关系仍是单向 |
| MoT-IDM [I] | 动作读条件视频；条件默认以 0.5 概率加噪，其余为干净真实未来 | 先生成视频，再以视频为条件生成动作 |
| Hidden [H] | 动作读视频中间层；默认 detach，动作梯度不回传视频专家 | 动作始终读首步缓存；联合路径随后的视频更新不改变这份条件 |

这张表里，三处实现值得仔细看。

其一，MoT-IDM 的未来条件不是部署特权。训练的 `cond_noise_mask[B]` 经 `[B,1,1,1,1]` 广播选择干净/加噪未来，两个视频分支互不读取；仅 noisy 分支计算视频 loss。部署 L376–452 先完成视频采样，再完成动作采样。因此其风险是“真实未来条件→模型未来条件”的分布差异；加噪教师条件不等于训练时已经见过模型生成错误。[I]

其二，Hidden 联合接口 L1086 的 `if cached_hidden is None` 只在首步赋值；动作循环持续读取 `cached_hidden`。动作接口更以 `return_prediction=False` 在捕获层提前停止，根本没有未来 latent 的迭代更新。官方架构博客将 Hidden 标为“测试时预测视频”，但该概括不足以描述当前动作接口；评测 `_predict_action_chunk` L375–404 又按 `visualize_future_video` 切换 joint/action。没有历史 run manifest，不能断言博客成绩使用了当前哪条路径。[H]、[评测分派][E]、[博客 RQ2][B]

其三，传入 `action=` 不代表固定动作预测。Unified L662 直接 `del action`；MoT 将其传成 `gt_action`，但 `_predict_joint_noise` L1088–1162 没有使用；IDM 也删除该参数。 这些接口不能仅靠提供候选动作就用作 `p(F|c,A*)` rollout。[U]、[M]、[I]

另有 mask 的间接路径：Unified 的默认配置为 `state_position: sequence`，初帧可读 state，state 又可读全部 future/action；故两层之间存在 `future→state→V0`，不能把“初帧不直接读未来”说成其表示始终没有未来信息。[mask L181–216][U]、[配置][UC]

本文在内存中抽取原源码 mask 函数、以每组一个 token 检查可达性，得到：MoT 的 `A←F`、`F←A` 均关闭；Joint 只开放前者；IDM 的动作只读取 cond；Unified 开放上述 state 中转路径。检查未加载权重，不是性能实验。mask 的 `True` 是允许读取，见 `StructuredAttentionMask.dense` L105–110。[mask 实现][AM]

## 5. 联合训练的收益来自哪里？

`Lv` 下降可来自视觉预训练、表征正则化、更多参数或容易预测的背景；`La` 是示范分布上的局部速度误差，不是闭环成功，也不是碰撞损失。当前推理主要采样一个动作块；上述调用中没有“多候选动作→预测各自未来→按价值重排”的决策程序。因此策略提升、在线想象提升、显式规划提升需要三套不同消融。

作者博客 RQ1/RQ2 自报如下；不是本文实验。[B]

| 设置 | Unified | Hidden | MoT |
|---|---:|---:|---:|
| Wan，全参数，LIBERO | 98.6% | 98.8% | 96.7% |
| Wan，全参数，Plus | 79.0% | 77.6% | 71.7% |
| Wan，LoRA，LIBERO | 87.0% | 93.5% | 95.9% |
| Cosmos，全参数，LIBERO | 96.8% | 96.8% | 97.6% |
| Cosmos，全参数，Plus | 78.2% | 77.8% | 77.7% |

反转至少三层：Wan 的 Hidden 分布内略高，Plus 却由 Unified 领先；LoRA 改为 MoT 领先；Cosmos 中 MoT 在 LIBERO 领先，Plus 三者接近。Cosmos-MoT 的 Camera 75.1% 高于 Unified 63.7%，Robot 58.5% 却低于 Unified 79.2%。 均分改变可由扰动类别的收益/损失抵消，不足以归因为“想象质量”或“对齐税”。默认 LIBERO 每任务 50 trials，Plus 是 10,030 个扰动任务各一次；后者不等于同一任务的独立大量重复。公开汇总也未给这些架构差异的配对不确定性。[B]、[LIBERO 协议][LE]、[Plus 协议][LP]

camera/tool/benchmark 混杂同样阻止 EasyWAM 与 ETA 横比：EasyWAM 拼接 agent/wrist 图像；ETA Codex 论文 §5.1.2、附录 B.2 可请求正交视角、像素射线定位和夹爪预览，并用 5,000 仿真步、5,400 秒尝试预算。Full ETA Table 2 的 `56/400` 与 Codex 的 `117/130 Pass@5` 既不是相同工具能力，也不是相同统计单位；更不能与 EasyWAM 成功率相减来证明哪种范式优越。[D]、[ETA §5、B.1–2][P]

可以构造一个简单反例：视频分支预测物体被正确放进篮子，动作分支却因坐标符号错误向反方向移动。如果视频不读动作，漂亮的预测也未必描述实际动作的后果。要证明规划收益，还需看候选动作的后果预测是否帮助选择了更好的动作。

## 6. ETA 怎样维护执行后的证据？

论文 §3.1、§4.2、附录 F 区分 Planner 的意图、Interface 的授权与 World 的证据。下面是本文据契约归纳的状态机，**不是宣称宿主硬编码 pick/place 顺序**。[P]、[动作管线][AP]

```text
FreshEvidence → ProposedCall → ContractGate
  ├─拒绝：保存理由与未满足义务，Planner 自选修复
  └─授权：至多一次 mutating call → OutcomeReceipt
          ├─fresh snapshot：更新证据后重新决策
          └─缺 snapshot／执行结果未知：ObservationDebt
               → host observe → FreshEvidence
               → 连续三次刷新失败：安全终止
FreshEvidence → SemanticVerification → 继续／重规划／求助／完成
```

`ActionPipeline._compile_tool_batch` L1353–1395 按 effect 阻止 mutation 批执行；`_compile_skill_call` L1096–1109 只返回 guidance，不暗中展开动作。`ToolCallingPlanner.plan` L198–211 在调用模型前处理宿主义务；`_invariant_obligation_decision` L386–438 自动补 `observe`。所以“Planner 每步自主”不意味着模型能跳过刷新，宿主只接管证据与传输不变量，不接管任务策略。[pipeline][APC]、[planner][PL]

semantic verification 至少分三层：工具调用完成、对象状态关系成立、任务官方成功。`_semantic_result_projection` L718 将 attachment proxy 的 tentative 转为需确认，而非抓取成功。`_record_world_mutation` L6475 又明确：失败运动若部分执行，机器人状态证据仍可能过期；命令确认不能证明物体移动。释放 gate L3255 仅在已有 attachment PASS 且最近运输失败等特定条件下阻止开夹爪，不能外推为所有放置语义都已被穷尽验证。[registry][TR]、[memory][ME]

权限上，host 注册工具与 handler authority；`_stamp_tool_result_provenance` L1074 删除 handler 自带 provenance，非 environment authority 的 receipt 被移除。模型文本、world prediction、普通 `state_delta` 不能铸造官方 reward。这个 World 是模拟器/机器人外部环境；神经预测若未来接入，仍应是 proposal，不能偿还 fresh-observation debt。[TR]、[ETA §4.3、F.2][P]

边界也不是绝对沙箱：文档 L403–416 允许逐次显式批准的 `outside_sandbox` Python 获得宿主 imports、文件和网络权限。因此“不能直接触碰 World”须限定受限运行配置；该授权是扩大信任面，不等于已证明远端服务不可绕过，也不是本文发现的现成漏洞。[AP]

## 7. 一次成功怎样成为可复用经验？

ETA §6.2、Table 5 的晋级规则是 `D∧Q∧R∧H`：确定性契约检查、隔离评阅、同任务 replay、配对 held-out 收益且不新增安全/契约回退。禁止存历史坐标、复用旧 pose 或改写原子权限。[P]

但机制必须分层核查：`SelfImprovementConfig` L44 默认不自动应用；`BackendReviewedSkillAutoApplier.apply` L123–160 经 author/reviewer 后写入 **session-local** skill。`PromotedMemoryStore.promote` L36–86 是附来源/reviewer 的追加持久化，函数自身没有 replay/held-out 检验。不能用这些 writer 的存在证明每次写入均通过论文 Table 5，也不能仅据 writer 缺检查断言上游所有调用都绕过门槛。[self-improvement][SI]、[promoted-memory][PM]

论文 Table 6、附录 E.1–E.5 的负结果需按实验单位读：online 两组序列分别 `0→1→0/10`、`0→0→3/10`，不是稳定增长；task-local 配对两臂均 `0/30`；exact-task playbook 从 `4/30` 到 `1/30`，baseline-only/candidate-only 为 4/1，作者给 exact McNemar `p=0.375`。因此不能称“显著退化”，但候选没有证明客观收益，仍未达晋级要求；v1/v2 replay 不复现成功，未进入 held-out。[P]

exact-task 的 held-out 是同三任务的新 seed，不是新任务泛化；五组研究依次按前组诊断设计，也不是五次独立确认。既有 manifest 未统一冻结主 Planner 身份，隔离上下文也不等于独立模型评阅。`0/30` 不证明等效；stage reachability 更不是严格嵌套转移概率。统计结论应止于“本组候选无一晋级”，不是“文本经验永远无效”。[ETA B.3、E.4–5][P]

后续 RoboDojo RSI 不能补作论文确认实验：10-16 文档自报 `23/42→27/42→28/42`，跨 v108/v109/v111/v112；含人工诊断批准、任务措辞补充、历史经验及额外特权 completion checker。seed 全为 0、每尝试最多 200 calls、无整回合时间/native-action 上限，还有六任务未填满预算。[RSI L13–45][RSI]

“前 k 次任一次成功”的累计覆盖即使系统不改也只会上升。学习收益需要比较相同尝试与权限预算下，更新经验是否提高了未见条件的成功率；单看经验库增长或累计覆盖不够。

## 参考资料

Siyin Wang 等，*World Modeling Makes a Better Planner: Dual Preference Optimization for Embodied Task Planning*，ACL 2025，采用 `2503.10480v1`；Junhao Shi、Zhaoye Fei 等，*World-aware Planning Narratives Enhance Large Vision-Language Model Planner*，2025，采用预印本 `2506.21230v1`。[D2PO][DP]、[WAP][WP]

ETA：Yitong Chen 等，*ETA: A New Agentic Paradigm for Embodied Tasks*，2026，采用 `2608.03924v1`。概率分类参照 Siyin Wang 等的综述 `2605.12090v1`，该综述不是 EasyWAM 方法论文；EasyWAM 以软件、配置、源码和作者博客为依据。论文历史实验与当前源码分开解释，不用今天的实现回填过去的评测。

源码核查于 2026-10-17，EasyWAM 固定为 `dd5b06153abd`，OpenETA 为 `b02260228e8c`。实验数字来自作者，计算与反例为本文分析；未运行模型或实机实验。

D2PO 固定为 `5474c30d13db`，WAP 为 `103ad7612655`；官方总览为 `14d3cf31265a`。主要入口如下。

| 固定源码 | 位置与核对事项 |
|---|---|
| D2PO [`AlfredEvaluator.evaluate_task`][DPC1]，L242／L345／L429／L584 | 候选采样、恢复模拟器后试执行、当前分支筛选 |
| D2PO [`TaskPlanner.evaluate_score_gpt`][DPC2]，L541／L641 | GPT 目标评分与环境可执行性等权合并 |
| D2PO [`AlfredEvaluator.evaluate_task`][DPC3]，L145／L175–242 | 普通闭环评测、下一动作生成及成功／失败反馈 |
| WAP [`enhance_instruction`][WPC1]，L29 | 训练指令增强读取末帧；本文件示范的是句法增强 |
| WAP [`generate_reasoning`／`process_single_entry`][WPC2]，L29／L86 | 给定专家动作生成理由，再保留原动作写回 |
| WAP [`VLMPlanner.process_prompt`／`get_message`][WPC3]，L50／L97 | 当前反馈拼接停用，维护视觉与输出历史 |

[OM]: https://github.com/sii-research/OpenMOSS/blob/14d3cf31265a5d3de9dea89a1d0857ea3d976579/README.md#L127
[DP]: https://arxiv.org/html/2503.10480v1
[WP]: https://arxiv.org/html/2506.21230v1
[DPR]: https://github.com/sinwang20/D2PO/blob/5474c30d13dbe7c4f796375c4c033648d0dcb4b1/README.md
[DPC1]: https://github.com/sinwang20/D2PO/blob/5474c30d13dbe7c4f796375c4c033648d0dcb4b1/src/alfred/alfred_evaluator_tree.py#L242
[DPC2]: https://github.com/sinwang20/D2PO/blob/5474c30d13dbe7c4f796375c4c033648d0dcb4b1/src/task_planner.py#L541
[DPC3]: https://github.com/sinwang20/D2PO/blob/5474c30d13dbe7c4f796375c4c033648d0dcb4b1/src/alfred/alfred_evaluator_former.py#L145
[DPC4]: https://github.com/sinwang20/D2PO/blob/5474c30d13dbe7c4f796375c4c033648d0dcb4b1/src/evaluate2.py#L13
[DPC5]: https://github.com/sinwang20/D2PO/blob/5474c30d13dbe7c4f796375c4c033648d0dcb4b1/src/evaluate3.py#L13
[WPC1]: https://github.com/sii-research/World-Aware-Planning/blob/103ad7612655609983caa4610ab74a5f81d8da5f/data-generation/generate_enhanced_instructions.py#L29
[WPC2]: https://github.com/sii-research/World-Aware-Planning/blob/103ad7612655609983caa4610ab74a5f81d8da5f/data-generation/rewrite_step_reasoning.py#L29
[WPC3]: https://github.com/sii-research/World-Aware-Planning/blob/103ad7612655609983caa4610ab74a5f81d8da5f/EmbodiedBench/embodiedbench/planner/custom_vlm_planner.py#L50
[W]: https://arxiv.org/pdf/2605.12090v1
[P]: https://arxiv.org/html/2608.03924v1
[U]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/src/model/easywam_unified.py#L166
[M]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/src/model/easywam_mot.py#L594
[J]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/src/model/easywam_mot_joint.py#L26
[I]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/src/model/easywam_mot_idm.py#L120
[H]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/src/model/easywam_hidden.py#L921
[S]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/src/model/schedulers/scheduler_continuous.py#L46
[UC]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/configs/model/easywam_unified_wan22.yaml#L9
[AM]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/src/model/component/attention.py#L105
[E]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/experiments/libero/eval_libero_single.py#L375
[B]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/docs/blogs/blog01_arch_zh.md
[D]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/docs/instructions/data/libero.md
[LE]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/docs/instructions/benchmark/libero.md
[LP]: https://github.com/OpenMOSS/EasyWAM/blob/dd5b06153abd1c04eff99a3933dc09baf0906fa2/docs/instructions/benchmark/libero_plus.md
[AP]: https://github.com/OpenMOSS/OpenETA/blob/b02260228e8c90fbc954e4eeb4ce4175249da9ba/docs/agent-action-pipeline.md#L248
[APC]: https://github.com/OpenMOSS/OpenETA/blob/b02260228e8c90fbc954e4eeb4ce4175249da9ba/agent/runtime/pipeline.py#L1223
[PL]: https://github.com/OpenMOSS/OpenETA/blob/b02260228e8c90fbc954e4eeb4ce4175249da9ba/agent/runtime/planner.py#L386
[TR]: https://github.com/OpenMOSS/OpenETA/blob/b02260228e8c90fbc954e4eeb4ce4175249da9ba/agent/tools/registry.py#L718
[ME]: https://github.com/OpenMOSS/OpenETA/blob/b02260228e8c90fbc954e4eeb4ce4175249da9ba/agent/runtime/memory.py#L3255
[SI]: https://github.com/OpenMOSS/OpenETA/blob/b02260228e8c90fbc954e4eeb4ce4175249da9ba/agent/runtime/self_improvement.py#L34
[PM]: https://github.com/OpenMOSS/OpenETA/blob/b02260228e8c90fbc954e4eeb4ce4175249da9ba/agent/runtime/promoted_memory.py#L36
[RSI]: https://github.com/OpenMOSS/OpenETA/blob/b02260228e8c90fbc954e4eeb4ce4175249da9ba/docs/robodojo-rsi-results.md#L13
