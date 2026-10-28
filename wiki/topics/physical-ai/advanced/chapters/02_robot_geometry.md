## 02 机构与几何：SE(3)、FK、IK 与雅可比

### 坐标不是物体：先固定变换方向

机器人计算首先要回答“这个数在哪个坐标系里”。全文采用列向量、右手坐标系、弧度制；$T_{AB}$ 表示 B 系相对于 A 系的位姿，并把 B 坐标变成 A 坐标。世界系记 W，基座系记 B，末端系记 E，不用字母 s 指代坐标系，以免与真实状态 $s$ 混淆。转动关节正方向按右手定则，移动关节正方向沿所定义轴。

$$
SO(3)=\{R\in\mathbb R^{3\times3}\mid R^\top R=I_3,\ \det R=1\},\qquad
T_{AB}=
\begin{bmatrix}R_{AB}&p_{AB}\\0_{1\times3}&1\end{bmatrix}\in SE(3).
$$

这里 $R_{AB}$ 的三列是 B 的三个单位轴在 A 中的坐标；$p_{AB}\in\mathbb R^3$ 是 B 原点在 A 中的位置，$I_3$ 是单位矩阵。正交条件保持长度和夹角，行列式条件排除镜像。位姿虽存为 $(4,4)$ 数组，只有六个自由度，不是十六个独立参数。[Modern Robotics §3.2.1：旋转矩阵](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-1-rotation-matrices-part-1-of-2/)

$$
\begin{bmatrix}p_A\\1\end{bmatrix}
=T_{AB}\begin{bmatrix}p_B\\1\end{bmatrix},\qquad
T_{AC}=T_{AB}T_{BC},\qquad
T_{BA}=T_{AB}^{-1}=
\begin{bmatrix}R_{AB}^\top&-R_{AB}^\top p_{AB}\\0&1\end{bmatrix}.
$$

$p_A,p_B$ 是同一点的两个 $(3,)$ 坐标数组；$T_{BC}$ 将 C 变成 B，因而组合中间的 B 可以“消去”。逆变换先撤销平移，再撤销旋转，所以逆平移不是简单的 $-p_{AB}$。方向向量的齐次末项为零，不应受到平移。矩阵乘法通常不可交换；“向世界轴平移”和“沿工具轴平移”也不是同一操作。[Modern Robotics §3.3.1：齐次变换](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-3-1-homogeneous-transformation-matrices/)

一个自创检查例：B 相对 A 绕 z 轴转正九十度，B 原点在 A 的 $(1,0,0)$，则 B 中点 $(1,0,0)$ 在 A 中为 $(1,1,0)$。实现测试应同时验证这一结果、变换与其逆的乘积，以及旋转行列式。不要只检查矩阵尺寸。

### 从机构到 FK：配置与速度是不同对象

固定基座、含 n 个独立单自由度关节的串联机构中，$q\in\mathbb R^n$ 是配置，$\dot q\in\mathbb R^n$ 是配置随时间的变化率。二者可以分别存为 $(n,)$ 数组；转动分量分别用弧度、弧度每秒，移动分量分别用米、米每秒。$\dot q$ 不是相邻编码器读数直接相减，还必须除以采样周期 $dt$，并处理角度跨越周期边界。自由基座使用单位四元数时，配置维度 $n_q$ 和广义速度维度 $n_v$ 可以不同，不能默认数组逐项求导就是速度。

正运动学 FK 的输入是机构参数与 $q$，输出末端 $T_{WE}(q)$，以及按需输出各连杆位姿。指数积表达把每个关节看成沿固定螺旋轴生成的运动：

$$
T_{WE}(q)=e^{[S_1]q_1}e^{[S_2]q_2}\cdots e^{[S_n]q_n}T_0,\qquad
[S_i]=
\begin{bmatrix}[\omega_i]_\times&v_i\\0&0\end{bmatrix}.
$$

$T_0$ 是零配置末端位姿；$S_i=[\omega_i^\top,v_i^\top]^\top$ 为零配置下、表达在 W 中的六维关节螺旋轴，$[\omega_i]_\times x=\omega_i\times x$。转动轴取单位 $\omega_i$，若轴经过 $r_i$，则 $v_i=-\omega_i\times r_i$；移动轴取 $\omega_i=0$、$v_i$ 为单位移动方向。直觉是逐关节施加刚体运动，而不是把各个角度直接相加。螺旋轴可存为 $(6,n)$，此处六维量统一采用“角分量在前、线分量在后”。[Modern Robotics §4.1.1：空间指数积](https://modernrobotics.northwestern.edu/nu-gm-book-resource/4-1-1-product-of-exponentials-formula-in-the-space-frame/)

### 雅可比怎样实际算出来

FK 的指数并不要求通用矩阵指数器。转动关节可使用 Rodrigues 形式；小角度时，直接计算“几乎相等的两个数之差”会丢失精度，宜采用相应级数或稳定的基础函数。一次正向遍历还可共享前缀变换，避免每列雅可比重新计算整条机构：

$$
\mathcal T_0=I_4,\qquad
J_{W,i}=\operatorname{Ad}_{\mathcal T_{i-1}}S_i,\qquad
\mathcal T_i=\mathcal T_{i-1}e^{[S_i]q_i},\qquad
\operatorname{Ad}_T=
\begin{bmatrix}R&0\\{[p]_\times R}&R\end{bmatrix}.
$$

$\mathcal T_i$ 为前 i 个关节指数的 $(4,4)$ 前缀乘积，$J_{W,i}\in\mathbb R^6$ 是空间雅可比的第 i 列；T 的块为 R、p，$[p]_\times x=p\times x$，伴随矩阵为 $(6,6)$。它先转动轴方向，再计入换参考原点导致的线速度变化。关节自己的运动尚未写入前缀时生成该列，之后才推进前缀；遍历结束的末端位姿为 $\mathcal T_nT_0$，其中 $T_0$ 仍是前节零配置位姿，不是这里的 $\mathcal T_0$。[Modern Robotics §5.1.1：雅可比列的构造](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-1-1-space-jacobian/)

换成末端表达的 body Jacobian 时，不能仅旋转其中两块：

$$
J_E=\operatorname{Ad}_{T_{WE}^{-1}}J_W,\qquad
J_p=J_W^{v}-[p_{WE}]_\times J_W^{\omega}.
$$

$J_W,J_E$ 均为 $(6,n)$，上标 $\omega$、v 分别选取前三行、后三行，$p_{WE}$ 是末端原点在 W 的位置，$J_p$ 为 $(3,n)$。第一式转换完整 twist，第二式把空间 twist 转成末端点速度；两种任务的雅可比由此有了可实现的明确接口。[Modern Robotics §5.1.2：body 与 space 雅可比关系](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-1-2-body-jacobian/)

机构文件中的关节原点、轴和零角偏置应先归入同一几何模型，再生成这些数组。换工具会改变 $T_0$、末端点速度和 body Jacobian，但不会改变机器人本体的空间螺旋轴定义。数值核验时固定关节索引顺序，分别扰动一个分量，再比较输出位移；扰动过小会被浮点舍入淹没，过大则把非线性误差误判成导数错误。

### 手算 2R：位置、速度与力映射

考虑平面二转动关节臂，连杆长度 $l_1,l_2$，第二角相对于第一杆测量，末端只要求二维位置：

$$
p(q)=
\begin{bmatrix}
l_1\cos q_1+l_2\cos(q_1+q_2)\\
l_1\sin q_1+l_2\sin(q_1+q_2)
\end{bmatrix},\qquad
J_p(q)=\frac{\partial p}{\partial q}=
\begin{bmatrix}
-l_1\sin q_1-l_2\sin(q_1+q_2)&-l_2\sin(q_1+q_2)\\
l_1\cos q_1+l_2\cos(q_1+q_2)&l_2\cos(q_1+q_2)
\end{bmatrix}.
$$

$p$ 为 $(2,)$，$J_p$ 为 $(2,2)$；每列表示仅让对应关节以单位角速度转动时，末端产生的速度。取纯数学例 $l_1=l_2=1$、$q=(0,\pi/2)$，得到 $p=(1,1)$，雅可比两行为 $(-1,-1)$、$(1,0)$。若 $\dot q=(1,-1)$，则末端速度为 $(0,1)$；这是数值代入，不是实机指令。

$$
\dot p=J_p\dot q,\qquad
\tau_{\mathrm{ext}}=J_p^\top f,\qquad
f^\top\dot p=\tau_{\mathrm{ext}}^\top\dot q.
$$

$f\in\mathbb R^2$ 是作用在末端的外力，$\tau_{\mathrm{ext}}\in\mathbb R^2$ 是其广义关节力矩。最后一式表达功率相等，解释了为什么速度映射用 J、力映射用其转置。力与雅可比必须表达在同一坐标系。空间刚体的 twist 雅可比为 $(6,n)$，但空间 twist 的线分量不能不经转换就当作末端原点的 $\dot p$；位置雅可比和 twist 雅可比不是可任意替换的数组。[Modern Robotics §5.1.1：空间雅可比](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-1-1-space-jacobian/)

同一 2R 的解析 IK 可由余弦定理得到：

$$
\begin{aligned}
c_2&=\frac{x_d^2+y_d^2-l_1^2-l_2^2}{2l_1l_2},\\
q_2&=\operatorname{atan2}\!\left(\pm\sqrt{1-c_2^2},c_2\right),\\
q_1&=\operatorname{atan2}(y_d,x_d)-\operatorname{atan2}(l_2\sin q_2,l_1+l_2\cos q_2).
\end{aligned}
$$

$(x_d,y_d)$ 为目标位置，$c_2$ 是第二角的余弦，正负号对应两种肘部构型。目标 $(1,1)$ 有 $(0,\pi/2)$、$(\pi/2,-\pi/2)$ 两个解。若 $|c_2|>1$，目标不可达；仅能对舍入误差造成的微小越界做截断，不能把明显不可达目标强行改成可达。

### 数值 IK：阻尼、迭代与退出条件

对 m 维局部任务误差 $e=x_d-x(q)$，一阶近似把非线性求根化成 $J\Delta q\approx e$。阻尼最小二乘选取：

$$
\Delta q=\arg\min_d\left(\|Jd-e\|_2^2+\lambda^2\|d\|_2^2\right)
=J^\top(JJ^\top+\lambda^2I_m)^{-1}e,\qquad
q^{(i+1)}=q^{(i)}+\alpha\Delta q.
$$

$J\in\mathbb R^{m\times n}$、$e\in\mathbb R^m$、$d,\Delta q\in\mathbb R^n$；$\lambda>0$ 是归一化后的阻尼，$\alpha$ 为步长。直觉是允许少量末端误差，换取不过大的关节改变量。误差和关节增量必须先按特征尺度归一化，避免直接把米、弧度、移动关节和转动关节混进同一范数。公式中的逆用于表达，不应在程序中显式计算；可解 $(m,m)$ 线性系统，或用增广最小二乘的 QR/SVD。[Modern Robotics §6.2：数值 IK 的局部线性化](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-1-of-2/)

每次迭代依次计算 FK、误差和 J，解阻尼子问题，尝试更新；若误差不下降，缩小步长或提高阻尼。触及关节边界时应用带边界的子问题，而非裁剪后宣称求解成功。成功返回 $q$、残差和状态；达到迭代上限、步长过小但误差仍大、无可接受步骤，都应返回失败或停滞。停止标准区分位置与姿态，不能只检查 $\|\Delta q\|$。

完整位姿的局部误差可写为：

$$
e_b=\operatorname{Log}\!\left(T_{WE}(q)^{-1}T_{WE}^{d}\right)^\vee\in\mathbb R^6.
$$

$T_{WE}^{d}$ 为目标位姿，$\operatorname{Log}$ 是 SE(3) 对数，$\vee$ 把李代数矩阵恢复成角在前的六维向量。它描述“从当前末端到目标”的局部刚体位移，应配对同一末端系的 body Jacobian；其后三维不是简单的位置差。局部更新需重新线性化，大转角尤其接近 $\pi$ 时须处理对数分支。[Modern Robotics §6.2：位姿 IK](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-2-of-2/)

### 奇异与冗余：能求数值不等于能完成任务

上述 2R 有 $\det J_p=l_1l_2\sin q_2$：伸直或折叠时秩下降，某方向的一阶速度消失。在 $q=(0,0)$，所有关节只产生末端 y 方向速度；要求纯 x 位移时，局部 IK 可停在零更新，必须换初值或离开该构型。奇异指“比该任务的最大可达秩更低”，并不等于“矩阵不是方阵”。[Modern Robotics §5.3：奇异性](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-3-singularities/)

$$
J=U\Sigma V^\top,\qquad
\Delta q=V\,\operatorname{diag}\!\left(\frac{\sigma_j}{\sigma_j^2+\lambda^2}\right)U^\top e,\qquad
\Delta q=J^\dagger e+(I_n-J^\dagger J)z.
$$

第一式为薄 SVD，$\sigma_j$ 是奇异值；第二式给出阻尼对各方向的增益，小奇异值不会被直接倒数放大。第三式是不加阻尼时的冗余解：$J^\dagger$ 为伪逆，$z\in\mathbb R^n$ 可用于远离关节边界，投影后的项在一阶近似中不改变任务。阻尼逆形成的投影不再是精确零空间投影，次任务可能泄漏到主任务。

数值实现还应检查关节顺序、单位和 FK/J 的一致性，用中心差分核对雅可比列；旋转误差应在切空间比较，不能逐元素差分后把十六项当任务。IK 只回答局部几何可达性：一个收敛解仍可能自碰撞，连接两解的运动也可能穿过障碍，留待规划章处理。

### 实际读取来源

- [Modern Robotics §3.2.1：Rotation Matrices，Part 1](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-2-1-rotation-matrices-part-1-of-2/)：读取作者课程文字转录，核验旋转约束。
- [Modern Robotics §3.3.1：Homogeneous Transformation Matrices](https://modernrobotics.northwestern.edu/nu-gm-book-resource/3-3-1-homogeneous-transformation-matrices/)：核验坐标变换方向、组合与逆。
- [Modern Robotics §4.1.1：Product of Exponentials](https://modernrobotics.northwestern.edu/nu-gm-book-resource/4-1-1-product-of-exponentials-formula-in-the-space-frame/)：核验 FK 的螺旋轴表示。
- [Modern Robotics §5.1.1：Space Jacobian](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-1-1-space-jacobian/)：核验列含义与维度。
- [Modern Robotics §5.1.2：Body Jacobian](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-1-2-body-jacobian/)：核验末端表达与空间表达的伴随变换关系。
- [Modern Robotics §5.3：Singularities](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-3-singularities/)：核验秩下降与任务冗余。
- [Modern Robotics §6.2，Part 1](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-1-of-2/) 与 [Part 2](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-2-of-2/)：核验迭代结构与位姿误差。2R 数值、阻尼推导和检查例为本文自创，不摘录教材算例。
