# T19：离散零漂移二元通道到高斯块生存序的严格桥接

更新日期：2026-07-24  
文档性质：**内部证明工作稿；证明链闭合，尚未取得独立概率论签核**  
发布状态：**not publication-ready**

## 1. 结论与边界

对固定有限二元通道网络、平衡初始余额、外生 i.i.d. 单位增量和严格零漂移，相关原子路由模型与保持每条通道完整边际增量的独立代理都在 \(N^2\) 时钟下收敛到各自的中心 Gaussian 退出时间。两族归一化停止时间具有统一正指数矩，因此均值可以通过极限。中心 Gaussian 相关不等式随后给出

\[
T_{\rm corr}\ge_{\rm st}T_{\rm ind},
\qquad
\lim_{N\to\infty}
\frac{\mathbb E\tau_N^{\rm corr}-\mathbb E\tau_N^{\rm ind}}{N^2}
=\mathbb ET_{\rm corr}-\mathbb ET_{\rm ind}\ge0.
\]

这不是有限 \(N\) 的逐点符号定理，也不覆盖非平衡初态、非零漂移、状态依赖路由、增长网络或三元以上超边。

## 2. 精确模型

固定通道数 \(m<\infty\)。第 \(e\) 条二元通道的两侧初始余额均为 \(N\)，以有符号位移表示为

\[
(N+S_e(n),\,N-S_e(n)).
\]

令 \(\xi_1,\xi_2,\ldots\) 为 i.i.d. 向量，取值于 \(\{-1,0,1\}^m\)，满足

\[
\mathbb E\xi_1=0,
\qquad
\Sigma=\operatorname{Cov}(\xi_1),
\qquad
\Sigma_{ee}>0\quad(1\le e\le m).
\]

相关过程为 \(S^{\rm corr}(n)=\sum_{r\le n}\xi_r\)。独立边际代理的一步增量 \(\eta_r\) 满足：各坐标 \(\eta_{r,e}\) 相互独立，且 \(\eta_{r,e}\overset d=\xi_{r,e}\)。因此

\[
\operatorname{Cov}(\eta_r)=D:=\operatorname{diag}(\Sigma_{11},\ldots,\Sigma_{mm}),
\]

同时每条通道的完整一步边际律均被保持。定义

\[
\tau_N^{a}=\inf\{n\ge0:\max_e|S_e^{a}(n)|=N\},
\qquad a\in\{\mathrm{corr},\mathrm{ind}\}.
\]

单位增量保证路径不会越过 \(\pm N\) 而未先命中边界。

均匀有序 OD 的最短路由核满足上述精确零漂移：每条路径与反向路径具有相同的最短路由重数和相同概率，而两者增量互为相反数。浮点实现中约 \(10^{-17}\) 的残差只属于求和表示误差，不改变以反向路由对定义的数学概率律。

## 3. 定理 T19

在第 2 节条件下，令 \(B_\Sigma\) 和 \(B_D\) 分别为协方差率 \(\Sigma\) 与 \(D\) 的中心 Brownian 运动，并定义

\[
T_{\rm corr}=\inf\{t\ge0:\max_e|B_{\Sigma,e}(t)|\ge1\},
\qquad
T_{\rm ind}=\inf\{t\ge0:\max_e|B_{D,e}(t)|\ge1\}.
\]

则：

1. 对 \(a\in\{\mathrm{corr},\mathrm{ind}\}\)，
   \[
   \tau_N^a/N^2\Rightarrow T_a.
   \]
2. 存在 \(\lambda>0\)，使两模型共同满足
   \[
   \sup_{N\ge1}\mathbb E\exp(\lambda\tau_N^a/N^2)<\infty.
   \]
3. 对每个固定 \(q>0\)，
   \[
   \mathbb E(\tau_N^a/N^2)^q\to\mathbb ET_a^q.
   \]
4. 对所有 \(t\ge0\)，
   \[
   \Pr(T_{\rm corr}>t)\ge\Pr(T_{\rm ind}>t),
   \]
   因而前述归一化均值差极限非负。更一般地，对任意递增可测函数 \(g\)，只要两侧期望均存在且有限，就有 \(\mathbb Eg(T_{\rm corr})\ge\mathbb Eg(T_{\rm ind})\)。

## 4. 证明

### 4.1 两个函数型中心极限定理

有界 i.i.d. 增量满足多元 Donsker 定理：

\[
N^{-1}S^{\rm corr}(\lfloor N^2\,\cdot\rfloor)
\Rightarrow B_\Sigma,
\qquad
N^{-1}S^{\rm ind}(\lfloor N^2\,\cdot\rfloor)
\Rightarrow B_D
\]

于 \(D([0,\infty),\mathbb R^m)\)。该步骤允许 \(\Sigma\) 退化；只要求每个法向坐标的方差严格为正。

### 4.2 退出映射的几乎处处连续性

对连续路径定义

\[
\Phi(f)=\inf\{t\ge0:\max_e|f_e(t)|\ge1\}.
\]

每个极限过程在首次接触前于任意紧子区间严格位于开立方体内部。若在有限停止时 \(T\) 接触面 \(f_e=1\) 或 \(f_e=-1\)，强 Markov 性给出接触后的法向增量为具有正方差的一维 Brownian 运动。Brownian 运动从零出发在任意右邻域内立即取正、负两种符号；多个面同时接触时只需对有限 active set 取概率一事件的有限交。因此极限路径在接触后立即穿越某个支撑超平面，\(\Phi\) 在该路径处关于紧区间一致拓扑连续。

任一正方差坐标几乎处处在有限时间命中 \(\pm1\)，故 \(T_a<\infty\) 几乎处处。连续映射定理得到结论 1。这个论证正是现有 T17C 第 4 节在二元通道坐标中的专门化，并显式覆盖同时触及多个面的情形。

### 4.3 统一尾界和一致可积性

令 \(V(s)=\sum_{e=1}^m s_e^2\)。对相关模型和独立代理都有

\[
\mathbb E[V(s+\zeta)-V(s)\mid s]
=\operatorname{tr}\Sigma=:v_*>0,
\]

因为两模型均值为零且代理保持所有边际方差。在 \(\tau_N^a\wedge k\) 前后，每个坐标绝对值不超过 \(N\)，所以有界可选停止给出

\[
v_*\,\mathbb E_s(\tau_N^a\wedge k)
=\mathbb EV(S^a(\tau_N^a\wedge k))-V(s)
\le mN^2.
\]

令 \(k\to\infty\)，对所有内部初态一致得到

\[
\sup_s\mathbb E_s\tau_N^a\le A N^2,
\qquad A=m/v_*.
\]

取 \(L_N=\lceil2AN^2\rceil\)。Markov 不等式和每个块端点的强 Markov 性递推得到

\[
\sup_s\Pr_s(\tau_N^a>rL_N)\le2^{-r}.
\]

于是对充分小且与 \(N\) 无关的 \(\lambda>0\)，

\[
\sup_{N,s,a}\mathbb E_s\exp(\lambda\tau_N^a/N^2)<\infty.
\]

所有固定正阶幂因此一致可积，结合分布收敛得到结论 2–3。这一步不需要独立代理对应一条物理路由；它只使用 i.i.d.、有界、逐通道守恒、零均值和正总方差。

### 4.4 Gaussian 块生存序

固定 \(t\) 并取逐渐加密的有限时间网格。第 \(e\) 条通道在所有网格时刻留在 \([-1,1]\) 的事件是有限维中心 Gaussian 空间中的中心对称凸集。Gaussian 相关不等式及归纳给出

\[
\Pr\!\left(\bigcap_{e=1}^m A_{e,r}\right)
\ge\prod_{e=1}^m\Pr(A_{e,r}).
\]

右端正是独立边际 Brownian 代理的网格生存概率。对可能退化的 \(\Sigma\)，可先给协方差加入 \(\varepsilon I\)，应用不等式后令 \(\varepsilon\downarrow0\)。连续路径和稠密网格把闭网格事件降到连续时间闭生存事件；每个正方差 Brownian 坐标的绝对最大值分布无原子，所以闭、开生存约定给出同一概率。由此得到结论 4。

最后使用第 4.3 节的均值收敛：

\[
\begin{aligned}
\lim_{N\to\infty}
\frac{\mathbb E\tau_N^{\rm corr}-\mathbb E\tau_N^{\rm ind}}{N^2}
&=\mathbb ET_{\rm corr}-\mathbb ET_{\rm ind}\\
&=\int_0^\infty
[\Pr(T_{\rm corr}>t)-\Pr(T_{\rm ind}>t)]\,dt\ge0.
\end{aligned}
\]

证毕。

## 5. 确定性数值验证

采用三节点路径和均匀有序 OD。相关一步增量为

\[
(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1)
\]

各以 \(1/6\) 发生，因此

\[
\Sigma=\begin{pmatrix}2/3&1/3\\1/3&2/3\end{pmatrix},
\qquad
D=\operatorname{diag}(2/3,2/3).
\]

对 \(N=1,2,4,\ldots,256\) 的被杀二维游走以双精度稀疏线性求解器确定性求解 Poisson 方程 \((I-Q_N)u_N=\mathbf1\)，没有 Monte Carlo 抽样误差；这里“确定性数值解”不等于解析精确值或区间算术证书。最大线性残差为 \(1.06\times10^{-10}\)，该残差只验证方程一致性，不单独构成前向误差界。独立 Brownian 极限另由一维区间生存谱的平方积分得到

\[
\mathbb ET_{\rm ind}=0.884056239375,
\]

2000 与 4000 项计算差 \(2.12\times10^{-11}\)；离散外推值与该解析级数相差 \(2.37\times10^{-12}\)。相关极限在不同窗口和拟合次数下约落在 \(0.93323207\)–\(0.933236114\)，主规格诊断值为 \(0.9332361050\)；该末位没有严格误差条，正文应报告为约 \(0.933236\)。从而

\[
\mathbb ET_{\rm corr}-\mathbb ET_{\rm ind}\approx0.04918.
\]

所有门禁通过。值得保留的反例是

\[
\Delta_1=1-9/8=-0.125,
\]

而本设计在全部 \(N\ge2\) 网格点上为正。这同时验证渐近方向并否定把 T19 错写成有限 \(N\) 普遍符号定理。

## 6. 证据与降级规则

- 数值源数据：`results/discrete-gaussian-bridge/discrete-gaussian-bridge-exact.csv`。
- 元数据与门禁：`results/discrete-gaussian-bridge/metadata.json`。
- PNG：`results/discrete-gaussian-bridge/discrete-gaussian-bridge.png`。
- 可复现程序：`gaussian_discrete_bridge_validation.py`；专项测试：`test_gaussian_discrete_bridge.py`。
- 若外部复核否定退出映射，则只保留两个 FCLT；若否定统一尾界，则只保留分布极限与 Gaussian 极限序；若 Gaussian 相关不等式的路径离散化步骤失败，则撤回随机序和均值差符号。确定性网格不得替代任何证明步骤。

## 7. 仍未闭合的范围

1. T19 尚待未参与推导的概率论研究者独立签核。
2. 非中心初态或非零漂移下的安全域不再关于零中心对称，本定理不给出符号。
3. 三元以上超边的余额单纯形通常不是中心对称集合，Gaussian 相关不等式不能按本证明直接使用。
4. 严格正序没有在一般非零跨通道协方差下证明；正文只能陈述非负序，受控路径上的严格正差属于实例结果。
