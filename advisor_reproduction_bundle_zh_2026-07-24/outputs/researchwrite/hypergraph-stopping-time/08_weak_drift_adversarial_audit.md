# 中心偏置弱漂移定理：内部对抗性证明审计

更新日期：2026-07-17

## 1. 审计结论

本轮从模型定义、实现代码和候选定理重新推导，而不是沿用
07 证明包的结论。结论为：

1. 弱漂移过程极限、首次出界时间分布收敛和统一可积性的核心论证成立；
2. 强 Markov 分块尾实际上给出统一指数矩，从而可把“均值收敛”加强为
   任意固定正阶矩收敛；
3. 原 PDE 表述“唯一有界弱解/黏性解”混合了两个解概念，必须分别写成
   \(H_0^1\) 变分弱解和 \(C(\overline D)\) 黏性解；
4. 定理的数学正确性可维持工作稿 A 级，但其方法是标准扩散逼近，
   新颖性不能仅由“未找到完全同构论文”推出；
5. 本文件是内部对抗性复核，不代替未参与推导的概率论研究者或正式同行评审。

## 2. 定理合同

固定 \(k\ge2\) 和 \(\eta\in\mathbb R\)。令 \(N\) 取足够大的整数，使

\[
p_N=1+\frac{\eta}{N}\in[0,2].
\]

总余额为 \(kN\)，初态 \(\mathbf x^{(N)}\) 为正整数组合且
\(\mathbf x^{(N)}/N\to\mathbf z\in D\)，其中

\[
D=\left\{\mathbf z\in(0,\infty)^k:\mathbf1^\top\mathbf z=k\right\}.
\]

每一步均匀选择一个无序对；外围—外围方向公平；中心—外围对中，中心
收款概率为 \(p_N/2\)。停止时间为第一个坐标到达零的时刻

\[
\tau_N=\inf\{m\ge0:\min_iX_i^{(N)}(m)=0\}.
\]

该合同不覆盖增长的 \(k\)、任意流量矩阵、状态依赖方向概率、随机金额、
支付拒绝、再平衡或相关多超边网络。

## 3. 模型与代码一致性

代码 drift_experiments.py 先均匀抽取两个不同节点。若节点对含中心 0，
令转移朝中心的概率为 theta = p_bias/2；否则保留抽取顺序所给出的
公平定向。由于有序抽取对每个无序对产生两个等概率顺序，这与第 2 节
的无序选对模型等价。

对每个中心—外围对 \(r\)，条件方向差为
\(p_N/2-(1-p_N/2)=\eta/N\)。无序对概率为
\(2/[k(k-1)]\)，因此一步均值为

\[
\mathbf d_N
=\left(
\frac{2\eta}{kN},
-\frac{2\eta}{k(k-1)N},\ldots,
-\frac{2\eta}{k(k-1)N}
\right)
=\frac{\boldsymbol\beta_\eta}{N}.
\]

方向偏置不改变 \(\boldsymbol\xi\boldsymbol\xi^\top\)，故

\[
\mathbb E(\boldsymbol\xi\boldsymbol\xi^\top)
=A_0=\frac{2}{k-1}P_H,\qquad
\operatorname{Cov}(\boldsymbol\xi)
=A_0-\mathbf d_N\mathbf d_N^\top.
\]

这与代码的 transition probabilities、精确 Markov 求解器和模拟器一致。

## 4. 逐环节证明审计

### 4.1 三角阵列 FCLT：通过

定义

\[
M_N(t)=\frac1N\sum_{r\le\lfloor N^2t\rfloor}
(\boldsymbol\xi_r^{(N)}-\mathbf d_N).
\]

其跳跃范数至多 \(2/N\)，故对任意 \(\varepsilon>0\)，当 \(N\) 足够
大时条件 Lindeberg 和最大跳跃条件均恒为零。可预测二次变差为

\[
\langle M_N\rangle(t)
=\frac{\lfloor N^2t\rfloor}{N^2}
\left(A_0-\mathbf d_N\mathbf d_N^\top\right)
\longrightarrow tA_0
\]

且在紧时间区间上一致收敛。Rebolledo 型鞅 FCLT 遂给出
\(M_N\Rightarrow A_0^{1/2}W_H\)。同时

\[
\frac{\lfloor N^2t\rfloor}{N}\mathbf d_N
=\frac{\lfloor N^2t\rfloor}{N^2}\boldsymbol\beta_\eta
\longrightarrow t\boldsymbol\beta_\eta.
\]

原证明结论正确；投稿版应写出上述 bracket，而不只写“收敛到
\(tA_0\)”。

### 4.2 首次出界时间：通过

将离散链在吸收后以同一独立增量序列延拓，定义阶梯过程
\(\mathbf Z_N(t)\)。对该过程，首次离开 \(D\) 的时间恰为
\(\tau_N/N^2\)，不存在越过边界而未命中的问题，因为每步只改变
\(\pm1\)。

对固定 \(t>0\) 和坐标 \(i\)，运行最小值

\[
m_i(f,t)=\min_{0\le s\le t}f_i(s)
\]

在连续路径的一致拓扑下连续。极限的每个坐标是从正值出发、方差率
\((A_0)_{ii}=2/k>0\) 的一维带漂移 Brownian 运动。其在固定有限区间
上的运行最小值在零处无原子。因此

\[
\Pr(T_N>t)\to\Pr(T>t)
\]

对每个 \(t>0\) 成立，并推出 \(T_N\Rightarrow T\)。这一论证比直接
引用“首次通过时间泛函连续”更透明，同时满足 Whitt（1980）所强调的
连续映射边界条件。

### 4.3 全状态均值界：通过

公平情形使用

\[
V(\mathbf x)=\sum_i(x_i-N)^2
\]

并有 \(\mathbb E[\Delta V\mid\mathcal F_t]=2\)。有限状态吸收性先保证
\(\mathbb E\tau_N<\infty\)，之后可选停止给出

\[
\sup_{\mathbf x}\mathbb E_{\mathbf x}\tau_N
\le\frac{k(k-1)}2N^2.
\]

当 \(\eta>0\) 时，任一外围坐标漂移为
\(-2\eta/[k(k-1)N]\)；当 \(\eta<0\) 时，中心坐标漂移为
\(-2|\eta|/(kN)\)。对 \(\tau_N\wedge n\) 使用坐标鞅，再令
\(n\to\infty\)，得到

\[
\sup_{\mathbf x}\mathbb E_{\mathbf x}\tau_N
\le
\begin{cases}
k^2(k-1)N^2/(2\eta),&\eta>0,\\
k^2N^2/(2|\eta|),&\eta<0.
\end{cases}
\]

三种界都对同一 \(N\) 的全部内部状态成立，这是后续强 Markov 分块
能够迭代的关键。

### 4.4 指数尾和全矩收敛：通过并加强

若 \(\sup_{\mathbf x}\mathbb E_{\mathbf x}\tau_N\le AN^2\)，令
\(L_N=\lceil2AN^2\rceil\)。Markov 不等式与强 Markov 性给出

\[
\sup_{\mathbf x}\Pr_{\mathbf x}(\tau_N>mL_N)\le2^{-m}.
\]

由于 \(L_N/N^2\le2A+1\)，存在

\[
0<c<\frac{\log2}{2A+1}
\]

使

\[
\sup_{N\ge N_0}\mathbb E\exp(cT_N)<\infty.
\]

因此，不仅 \(\{T_N\}\) 一致可积，而且对每个固定 \(q>0\)，
\(\{T_N^q\}\) 一致可积。结合 \(T_N\Rightarrow T\)，得到

\[
\boxed{\mathbb E T_N^q\longrightarrow\mathbb E T^q,
\qquad q>0.}
\]

均值收敛是 \(q=1\) 的特例。投稿版应采用这一更强且直接由现有尾界
推出的结果。

### 4.5 PDE 识别：修改后通过

在切向空间 \(H\) 上取正交坐标，将 \(D\) 视为
\((k-1)\) 维有界开单纯形。生成元为

\[
\mathcal A_\eta
=\boldsymbol\beta_\eta^\top\nabla
+\frac1{k-1}\Delta_H.
\]

正确且可审查的表述是：

- \(a(\mathbf z)=\mathbb E_{\mathbf z}T\) 连续延拓到
  \(\overline D\)，并在 \(\partial D\) 为零；
- \(a\in H_0^1(D)\cap C(\overline D)\cap C^\infty(D)\)；
- \(a\) 是以下变分问题的唯一 \(H_0^1(D)\) 解：

\[
\frac1{k-1}\int_D\nabla a\cdot\nabla\varphi
-\int_D(\boldsymbol\beta_\eta\cdot\nabla a)\varphi
=\int_D\varphi,\qquad \varphi\in H_0^1(D);
\]

- 同一函数也是连续 Dirichlet 数据下的唯一连续黏性解。

常漂移项在 \(H_0^1\) 上不破坏 coercivity；单纯形满足外锥条件，
边界点对一致椭圆扩散均为正则。只声明内部光滑，不声明角点处
\(C^2\) 正则性。

## 5. 先行工作带来的新颖性纠偏

本轮新增核查的直接相关文献如下。

| 文献 | 与本项目的关系 | 不能再声称的内容 |
|---|---|---|
| Sobel & Frankowski (2002) | 明确包含公平随机选对、单位转移和首次有人破产的 random-selection 策略 | 公平选对多人模型或其差分方程由本文提出 |
| O’Connor & Saloff-Coste (2023) | 同一公平四人首次破产模型；研究大容量 harmonic profile 与连续单纯形谱问题 | 四人模型或 Brownian/simplex 近似是本文首次 |
| Diaconis, Houston-Edwards & Saloff-Coste (2021) | 有限 inner-uniform 域的 gambler's-ruin/harmonic-measure 一般估计 | 在有限单纯形上使用 killed-chain/Perron–Frobenius 方法本身新颖 |
| Denisov & Wachtel (2024) | 三人模型的 harmonic measure、Brownian 近似及收敛速率 | 三人 Brownian 近似或退出位置渐近新颖 |
| Grigorescu & Yao (2016) | 公平单位 pairwise transfer，但研究可控选对和完全淘汰时间 | pairwise-transfer 多人 ruin 尚无人研究 |
| Kehagias et al. (2025) | 三人 pairwise transfer、固定非对称胜率和策略选对，直至完全淘汰 | 非对称 pairwise 三人模型是空白 |
| Barnett (1964) | 三人 gambler's ruin 的非对称扩展；公开摘要不足以确认转移核 | 在全文未核验时声称三人成对非对称特例无先例 |
| Rocha & Stern (1999, 2004) 及后续 | 一名赢家从所有对手收款的非对称一般 \(n\) 人首次破产、期望和矩 | 非对称一般 \(n\) 人首次破产是本文首次 |
| Tzioufas (2019) | 不同高维几何中所有 \(p\)-阶退出时间矩的缩放极限 | 退出时间全矩收敛的现象或不变原理路线本身新颖 |
| Ekhad & Zeilberger (2023)；Phetpradap & Sripanitan (2025) | 公平三人多阶精确矩；不同非对称多人规则的任意整数阶矩 | 多人破产时间“全矩”本身是本文创新 |

Rocha–Stern 一系的“非对称 \(n\) 人 ruin”每轮由一个赢家同时向其余
\(n-1\) 人收款，和本项目每轮只转移一个单位的 pairwise 模型不同，
只能作为邻近文献，不能当作完全同构先例。与此同时，Tzioufas 和
Phetpradap–Sripanitan 已足以否定“全矩本身新颖”；可辩护差异必须是
成对单位转账、中心 \(1/N\) 偏置、固定一般 \(k\) 与首次为零的组合。

## 6. 当前可辩护的贡献边界

弱漂移定理在正确性上可以保留，但不能把标准 FCLT + 连续映射 +
Feynman–Kac 的组合包装成孤立的数学突破。较稳妥的贡献组合是：

1. 一个合法、可解释的中心偏置 pairwise 流量族；
2. 同一模型下弱漂移 \(N^2\) 尺度与正负强漂移 \(N\) 尺度之间的相图；
3. 该中心偏置成对转账模型下，弱漂移首次耗尽时间的全矩收敛及明确的
   对流—扩散 Dirichlet 问题；
4. 正负强漂移因“一个中心”与“多个外围竞争”产生的不对称；
5. 与支付通道停止语义和经验证快速代理的组合。

若缺少现实流量映射、强漂移严格定理或相关网络扩展，单独依靠第 3 点
未必足以支撑高水平概率论论文。

## 7. 投稿前剩余质量门

1. 由未参与当前推导的概率论研究者按
   [09 外部评审包](09_weak_drift_external_review_packet.md) 逐行复核并
   完成 R1–R12 签核。
2. 在目标期刊允许的引用体系中固定 Rebolledo/Whitt 或等价现代定理的
   精确编号。
3. 决定主文采用变分弱解还是黏性解框架；不要在一句话中混用。
4. 合法取得 Barnett 1964 全文并核验转移核；继续追踪
   Sobel–Frankowski、Rocha–Stern、O’Connor–Saloff-Coste 和
   Diaconis–Houston-Edwards–Saloff-Coste 的引用链。
5. 若要把“全矩收敛”列作贡献，正文必须明确给出统一指数矩推导。
