## 04 感知与估计：标定、贝叶斯、EKF 与 SLAM

### 从像素到空间：投影先丢失了什么

真实状态 $s$ 可包含位姿、速度、偏置和地图；观测 $o$ 是像素、深度、编码器或惯性测量，不能直接当作 s。相机 C 采用 x 向图像右、y 向图像下、z 向前的右手系。为避免与控制输入 u 混淆，像素列、行记为 $(\xi,\eta)$。忽略畸变、使用针孔模型：

$$
\xi=f_x\frac{X_C}{Z_C}+c_x,\qquad
\eta=f_y\frac{Y_C}{Z_C}+c_y,\qquad
K=
\begin{bmatrix}f_x&0&c_x\\0&f_y&c_y\\0&0&1\end{bmatrix}.
$$

$p_C=(X_C,Y_C,Z_C)\in\mathbb R^3$ 为相机坐标；$f_x,f_y$ 是像素单位的焦距，$c_x,c_y$ 为主点，K 为 $(3,3)$ 内参。直觉是相似三角形：同一射线上的点投到同一像素，二维图像本身不含该点的距离。要求 $Z_C>0$；接近零时除法及导数都会病态。[OpenCV 官方：针孔模型与内外参](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)

若深度图 D 给出沿光轴的 Z，而不是到相机的欧氏距离，可反投影：

$$
p_C=D[\eta,\xi]\,K^{-1}
\begin{bmatrix}\xi\\\eta\\1\end{bmatrix}
=
\begin{bmatrix}
(\xi-c_x)D/f_x\\
(\eta-c_y)D/f_y\\
D
\end{bmatrix},\qquad
p_W=R_{WC}p_C+t_{WC}.
$$

$D[\eta,\xi]$ 为该像素的有效光轴深度，$R_{WC},t_{WC}$ 来自把 C 坐标变为 W 的 $T_{WC}$。像素索引按“行、列”，坐标按“列、行”，不要交换。深度输入为 $(H_{\mathrm{img}},W_{\mathrm{img}})$，有效点输出可为 $(N,3)$；N 不一定等于像素总数。若传感器给的是射线距离 r，应使用单位化射线乘 r，不能直接代入 D。[MIT：深度图与点云](https://manipulation.csail.mit.edu/pose.html)

自创离线例：$f_x=f_y=400$、主点 $(320,240)$，像素 $(360,220)$ 的光轴深度为 2 米，得到 $p_C=(0.2,-0.1,2)$ 米。负 y 表示主点上方。这个计算同时检查坐标方向、焦距像素单位和深度尺度，不涉及设备操作。

### 标定与时间：把观测模型写对

径向畸变的一种简化形式为：

$$
x'=X_C/Z_C,\qquad y'=Y_C/Z_C,\qquad
r^2=x'^2+y'^2,\qquad
\begin{bmatrix}x_d\\y_d\end{bmatrix}
=\left(1+k_1r^2+k_2r^4\right)
\begin{bmatrix}x'\\y'\end{bmatrix}.
$$

$x',y'$ 是无量纲归一化坐标，$x_d,y_d$ 是畸变后坐标，$k_1,k_2$ 为径向系数。镜头改变的不是每个三维点的位置，而是投影后的射线方向。完整模型还可含切向等项；本文只展示两项径向模型，不声称可描述所有镜头。反投影应先去畸变，或者使用与已校正图像对应的新内参。[OpenCV：畸变模型](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)

标定是用已知三维点和多幅像素对应关系估计参数，不是“量一次焦距”。其最小二乘原型为：

$$
\min_{\theta,\{T_{CB_j}\}}
\sum_{j,i}
\left\|o_{ji}-\pi_\theta\!\left(T_{CB_j}\bar p_i\right)\right\|_2^2.
$$

$p_i$ 是标定板 B 上的 $(3,)$ 已知点，$\bar p_i$ 是补一后的 $(4,)$ 向量；$o_{ji}\in\mathbb R^2$ 是第 j 幅图的像素，$\theta$ 收集内参与畸变，$\pi_\theta$ 输出 $(2,)$ 投影；$T_{CB_j}$ 为该视角下板到相机的变换。直觉是让所有已知点的预测像素同时贴近实际像素。每轮线性化投影，解参数增量，更新位姿，再检查重投影误差。

输入可按视图组织为多个 $(N_j,3)$ 对象点数组和 $(N_j,2)$ 图像点数组，输出 K、畸变向量及每图外参。视角或图像覆盖变化不足会导致参数耦合；应在未用于拟合的对应点上检查残差结构，不能只看一个训练 RMS。OpenCV 位姿求解的旋转、平移把对象坐标变成相机坐标，通常对应 $T_{CW}$，相机世界位姿则是其逆。[OpenCV：标定与位姿求解接口](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)

空间正确而时间错配，仍会形成错误点云。手眼外参描述固定装配关系，随时间变化的是载体位姿。融合应使用测量产生时刻，而非软件收到消息的时刻：

$$
t_{\mathrm{ref}}=\gamma t_{\mathrm{sensor}}+\delta.
$$

$\delta$ 为时钟偏移，$\gamma$ 为相对时钟尺度或漂移系数；短区间可采用 $\gamma=1$ 的简化。相机与 IMU 的联合标定同时涉及空间变换与时间偏移，数据还须核查时间戳抖动。[ETH Kalibr 官方：Camera–IMU Calibration](https://github.com/ethz-asl/kalibr/wiki/camera-imu-calibration)

对运动序列，应将位姿或预测状态对齐到该时刻；迟到数据需要回溯更新并重传播，或者明确采用有界延迟近似。滚动快门使不同行的曝光时刻不同，单一帧时间是额外假设。毫米和米混用、裁剪缩放后未更新 K、RGB 与深度像素未配准，都会造成系统性偏差；增大噪声协方差不能使错误观测模型变正确。

### 贝叶斯滤波：保留一个状态分布

给定实际控制输入历史与观测历史，记状态信念为 b。以下下标 t 表示环境中的离散控制/观测步，$dt$ 为一步的采样周期；它不是扩散步骤，k 留给扩散章。在一阶 Markov 动力学、当前观测条件独立的模型下：

$$
b_t^-(s_t)=\int p(s_t\mid s_{t-1},u_{t-1})b_{t-1}^+(s_{t-1})\,ds_{t-1},\qquad
b_t^+(s_t)=\frac{p(o_t\mid s_t)b_t^-(s_t)}
{\int p(o_t\mid s_t)b_t^-(s_t)\,ds_t}.
$$

$b^-$ 为看本次观测前的预测分布，$b^+$ 为更新后的后验；$u_{t-1}$ 是上一周期真实使用的输入，$o_t$ 是当前观测。预测把上次的不确定性沿动力学推前，更新按“该状态解释这次观测的可能性”重新加权，分母只负责归一化。策略动作 a 若尚未经低层转换，不能直接冒充动力学中的 u。EKF 用均值和协方差近似这一分布，因子图则可保留多个时刻的联合分布。[GTSAM 作者官方教程：概率模型与因子图](https://gtsam.org/tutorials/intro.html)

### EKF：每一轮究竟更新哪些数组

先采用欧氏 d 维状态、m 维观测、独立零均值加性高斯噪声：

$$
s_t=\mathcal F(s_{t-1},u_{t-1},dt)+w_{t-1},\qquad
o_t=\mathcal H(s_t)+\nu_t,\qquad
w_{t-1}\sim\mathcal N(0,Q_{t-1}),\quad
\nu_t\sim\mathcal N(0,R_t).
$$

$\mathcal F$ 是离散状态转移，$\mathcal H$ 是观测预测；$s,w\in\mathbb R^d$、$o,\nu\in\mathbb R^m$，Q 为 $(d,d)$ 过程噪声协方差，R 为 $(m,m)$ 测量噪声协方差。这里的 Q 是一个时间步的噪声，不是可不加转换地使用的连续时间噪声密度。EKF 在当前估计附近重新线性化，但均值预测仍用非线性模型。[MIT 2.160：EKF 讲义](https://ocw.mit.edu/courses/2-160-identification-estimation-and-learning-spring-2006/d9cba810f893379e8fc6c0ecb582766f_lecture_7_2.pdf)

预测步骤：

$$
\hat s_t^-=\mathcal F(\hat s_{t-1}^+,u_{t-1},dt),\qquad
F_t=\left.\frac{\partial\mathcal F}{\partial s}\right|_{\hat s_{t-1}^+},\qquad
P_t^-=F_tP_{t-1}^+F_t^\top+Q_{t-1}.
$$

$\hat s$ 为 $(d,)$ 状态均值，P 为 $(d,d)$ 估计误差协方差，F 为 $(d,d)$ 状态转移雅可比。F 把旧误差映射到新误差，Q 再补上本步未知扰动。若噪声经 G 注入低维子空间，则加项应为 $GQG^\top$，且 Q 的尺寸随噪声维度变化。[MIT 2.160：线性化与协方差传播](https://ocw.mit.edu/courses/2-160-identification-estimation-and-learning-spring-2006/d9cba810f893379e8fc6c0ecb582766f_lecture_7_2.pdf)

收到观测后计算创新与增益：

$$
\hat o_t=\mathcal H(\hat s_t^-),\qquad
H_t=\left.\frac{\partial\mathcal H}{\partial s}\right|_{\hat s_t^-},\qquad
r_t=o_t-\hat o_t,\qquad
S_t=H_tP_t^-H_t^\top+R_t,\qquad
K_t=P_t^-H_t^\top S_t^{-1}.
$$

$\hat o,r$ 为 $(m,)$，H 为 $(m,d)$，S 为 $(m,m)$ 创新协方差，K 为 $(d,m)$ Kalman 增益。r 问“观测与预测差多少”，S 问“模型原本允许它差多少”，K 决定这次差异如何修正各个状态分量。角度残差必须归一到一致的角度分支；S 的逆仍应通过线性求解实现。

更新步骤采用 Joseph 形式：

$$
\hat s_t^+=\hat s_t^-+K_tr_t,\qquad
A_t=I_d-K_tH_t,\qquad
P_t^+=A_tP_t^-A_t^\top+K_tR_tK_t^\top.
$$

$I_d$ 为 $(d,d)$ 单位矩阵，A 是更新后的误差传播矩阵。第一项保留未被观测消除的先验误差，第二项计入本次观测噪声；这由更新误差的协方差直接展开得到，比直接相减两个接近矩阵更适合有限精度计算。此形式仍假设先验误差与测量噪声不相关，不会替错误的数据关联兜底。

自创标量例：预测位置为 2、预测方差为 4；观测为 3、测量方差为 1，H 为 1。于是 r 为 1、S 为 5、K 为 0.8，后验位置为 2.8、方差为 0.8。融合更信任方差较小的测量，但没有把结果硬设成测量值。

实现每轮应输出 $\hat s_t^+,P_t^+$ 及 r、S、时间戳、观测是否接受。可用 $r^\top S^{-1}r$ 检查归一化创新，但异常不一定意味着传感器坏了，还可能是错配、时钟问题或模型失配。禁止将缺测填零后正常更新；缺测应跳过或只更新有效子观测。重复使用同一证据并当作独立观测会虚假缩小 P；协方差非对角项也不能随意抹掉。[MIT 2.160：可观测性与数值失败](https://ocw.mit.edu/courses/2-160-identification-estimation-and-learning-spring-2006/d9cba810f893379e8fc6c0ecb582766f_lecture_7_2.pdf)

位姿属于流形，以上加法仅适用于局部误差坐标。姿态误差可用三维切空间增量，回注入旋转后还要按新线性化点变换误差协方差。不能把四元数四个分量视为四个独立旋转自由度，再只靠归一化解决协方差问题。

### SLAM：把轨迹和地图共同解释为测量

令 $T_i=T_{WC_i}$ 为第 i 个相机位姿，$\ell_j\in\mathbb R^3$ 为地标。里程计或回环测量 $Z_{ij}$ 给出相对位姿，图像测量 $o_{ij}$ 给出地标像素：

$$
r_{ij}^{\mathrm{pose}}
=\operatorname{Log}(Z_{ij}^{-1}T_i^{-1}T_j)^\vee,\qquad
r_{ij}^{\mathrm{img}}
=o_{ij}-\pi_K\!\left(R_i^\top(\ell_j-t_i)\right).
$$

$T_i$ 的旋转和平移为 $R_i,t_i$；pose 残差为 $(6,)$，image 残差为 $(2,)$，$\pi_K$ 为前文针孔投影。第一式比较预测相对变换与测量，第二式先把世界地标变到相机再投影。pose 协方差必须定义在所选局部残差坐标中，不是 $(4,4)$ 位姿矩阵元素的协方差。[GTSAM 官方：BetweenFactor 残差与坐标](https://borglab.github.io/gtsam/betweenfactor/)

假设给定未知量后，各因子噪声独立，最大后验可化成：

$$
\min_{\Theta}\ 
\frac12\sum_f\rho_f\!\left(r_f(\Theta)^\top\Sigma_f^{-1}r_f(\Theta)\right)
+E_{\mathrm{prior}}(\Theta),\qquad
\Theta=\{T_i,\ell_j\}.
$$

f 遍历测量因子，$\Sigma_f$ 是该残差协方差，$\rho_f$ 为可选鲁棒损失，无鲁棒处理时取恒等函数；$E_{\mathrm{prior}}$ 是先验代价。每个因子只连接它涉及的位姿、地标，因此雅可比是块稀疏的。图是误差函数，当前参数值另行存放，不能把“已建图”当作“已求解”。[GTSAM 作者官方教程：图与 Values](https://gtsam.org/tutorials/intro.html)

具体迭代先以预测轨迹和三角化地标初始化，计算并白化残差，组装稀疏雅可比，再求增量：

$$
(\mathcal J^\top\mathcal J+\lambda D_{\mathrm{scale}})\Delta
=-\mathcal J^\top r,\qquad
T_i\leftarrow T_i\operatorname{Exp}([\Delta_i]),\qquad
\ell_j\leftarrow\ell_j+\Delta_{\ell_j}.
$$

$\mathcal J$ 为 $(N_r,D_{\mathrm{var}})$ 白化残差雅可比，r 为 $(N_r,)$，$\Delta$ 为 $(D_{\mathrm{var}},)$；$\lambda$ 是 LM 阻尼，$D_{\mathrm{scale}}$ 是尺度矩阵；每个位姿增量为六维，每个地标增量为三维。局部更新后重算真实目标，改善时接受并调整阻尼，否则拒绝并重试。可用稀疏 QR 避免正规方程平方放大条件数，停止时检查目标变化、梯度和步长，而非仅看迭代数。[GTSAM：非线性优化](https://gtsam.org/tutorials/intro.html)

最后必须处理 gauge：若只有相对测量，将全部位姿与地标同时做同一个全局刚体变换，残差不变，三维问题至少存在六个未定方向。纯单目、无尺度先验时还可共同缩放平移和地标，增加尺度自由度。固定首个位姿只是选坐标系，不是测得了绝对真值；纯单目还需独立固定或引入尺度。无 gauge 约束的 Hessian 可能奇异，添加任意大对角数只会掩盖问题。[GTSAM 官方：不定线性系统与 gauge](https://borglab.github.io/gtsam/indeterminatesystemexception/)

回环增加跨时刻约束，但错误匹配会把远处轨迹拉到一起；鲁棒核只缓解部分离群点，仍须先验证数据关联。初始化差、地标仅见一次、纯旋转缺少三角化视差，都可能导致退化。输出不应只有一张地图，还应包含轨迹、坐标系与尺度约定、残差、可观测性说明和计算协方差所采用的锚定条件。

### 实际读取来源

- [OpenCV：Camera Calibration and 3D Reconstruction](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)：读取针孔、畸变、标定参数与对象到相机的外参说明；未依赖特定程序版本。
- [MIT Robotic Manipulation：Geometric Pose Estimation](https://manipulation.csail.mit.edu/pose.html)：读取深度、点云及内外参相关部分。
- [ETH Kalibr 官方 Wiki：Camera–IMU Calibration](https://github.com/ethz-asl/kalibr/wiki/camera-imu-calibration)：读取时间校准及时间戳检查部分，不采用其硬件采集参数。
- [MIT 2.160：Lecture Notes No. 7，EKF 与 Implementation Issues](https://ocw.mit.edu/courses/2-160-identification-estimation-and-learning-spring-2006/d9cba810f893379e8fc6c0ecb582766f_lecture_7_2.pdf)：读取讲义；本文离散更新与标量算例为独立推导，非转录讲义的连续时间公式。
- [GTSAM 官方在线教程：Factor Graphs and GTSAM](https://gtsam.org/tutorials/intro.html)：读取概率模型、图与 Values、非线性优化、PoseSLAM 和地标 SLAM 部分；引用在线文档，不引用其链接的论文。
- [GTSAM 官方：BetweenFactor](https://borglab.github.io/gtsam/betweenfactor/)：读取相对位姿残差及局部噪声坐标。
- [GTSAM 官方：Debugging an Indeterminate Linear System](https://borglab.github.io/gtsam/indeterminatesystemexception/)：核验 gauge、秩亏及数值病态的区别。
