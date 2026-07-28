# 弱漂移退出时间极限：定理工作稿与证明包

更新日期：2026-07-17

## 1. 结论与边界

本文件闭合中心偏置模型在

\[
p_N=1+\frac{\eta}{N},\qquad k\ \text{固定},\qquad N\to\infty
\]

下从过程弱收敛到停止时间全矩收敛的四个环节：三角阵列不变原理、
单纯形首次出界时间收敛、统一指数矩和 Dirichlet–Poisson 识别。
这是当前项目的**定理工作稿**，状态为“证明链已闭合，待独立概率论
核查”；它不构成已经通过同行评审的发表结果，也不支持任意流量矩阵、
增长的 \(k\) 或相关多超边网络。

三人零漂移情形及其 Brownian 三角形退出极限已有直接先例；本项目不得
将其作为原创贡献。最接近的文献边界见第 8 节。

本包是 \(p_N=1+\eta N^{-\alpha}\) 统一结果在 \(\alpha=1\) 的临界模块；
三分区拼接、\(\alpha<1\) 与 \(\alpha>1\) 的独立证明见
[11 相图证明包](11_polynomial_drift_phase_diagram_proof_package.md)。

## 2. 模型与记号

固定整数 \(k\ge2\)。第 \(N\) 个系统的总整数余额为 \(kN\)，初态
\(\mathbf x^{(N)}\) 满足

\[
\frac{\mathbf x^{(N)}}N\longrightarrow \mathbf z\in
\mathcal S_k^\circ
:=\left\{\mathbf z\in(0,\infty)^k:\mathbf1^\top\mathbf z=k\right\}.
\]

每一步均匀选择一个无序节点对。外围—外围对两个方向等概率；包含中心
节点 0 的节点对中，中心收款的条件概率为 \(p_N/2\)，中心付款的条件
概率为 \((2-p_N)/2\)。对固定 \(\eta\)，当 \(N\) 足够大时
\(p_N\in[0,2]\)。

令 \(\boldsymbol\xi_r^{(N)}\) 为第 \(r\) 步整数余额增量。为使用不变原理，
在首次出界后仍以同一独立增量序列延拓无约束随机游走；该延拓不改变
首次出界前的过程或停止时间。定义

\[
\mathbf Z_N(s)
=\frac1N\left(\mathbf x^{(N)}+
\sum_{r=1}^{\lfloor N^2s\rfloor}\boldsymbol\xi_r^{(N)}\right),
\]

以及

\[
T_N=\frac{\tau_N}{N^2},\qquad
\tau_N=\inf\{m\ge0:\min_iX_i^{(N)}(m)=0\}.
\]

在切向子空间 \(H=\{\mathbf y:\mathbf1^\top\mathbf y=0\}\) 上记

\[
P_H=I-\frac1k\mathbf1\mathbf1^\top,qquad
A_0=\frac{2}{k-1}P_H,
\]

并定义

\[
\boldsymbol\beta_\eta
=\left(
\frac{2\eta}{k},
-\frac{2\eta}{k(k-1)},\ldots,
-\frac{2\eta}{k(k-1)}
\right).
\]

## 3. 主定理

**定理（固定维数中心偏置弱漂移极限，工作稿）。** 在第 2 节假设下，
令

\[
\mathbf Z(s)=\mathbf z+\boldsymbol\beta_\eta s+A_0^{1/2}\mathbf W_H(s),
\]

其中 \(\mathbf W_H\) 是切向子空间上的标准 Brownian 运动，并令

\[
T=\inf\{s\ge0:\mathbf Z(s)\notin\mathcal S_k^\circ\}.
\]

则：

1. \(\mathbf Z_N\Rightarrow\mathbf Z\) 于 \(D([0,\infty),H+\mathbf z)\)；
2. \(T_N\Rightarrow T\)；
3. 存在 \(N_0=N_0(\eta)\) 与 \(c=c(k,\eta)>0\)，使
   \(\sup_{N\ge N_0}\mathbb E\exp(cT_N)<\infty\)；
4. 对任意固定 \(q>0\)，
   \(\mathbb E T_N^q\to\mathbb ET^q\)；特别地
   \(\mathbb E T_N\to\mathbb ET=:a_{k,\eta}(\mathbf z)\)；
5. \(a_{k,\eta}\in H_0^1(\mathcal S_k^\circ)\cap C(\mathcal S_k)\)
   且 \(a_{k,\eta}\in C^\infty(\mathcal S_k^\circ)\)，是
   有界单纯形上

\[
\boldsymbol\beta_\eta^\top\nabla a
+\frac1{k-1}\Delta_{\mathrm{tan}}a=-1,
\qquad a|_{\partial\mathcal S_k}=0
\]

的唯一 \(H_0^1\) 变分弱解；同一函数也是连续 Dirichlet 数据下的
唯一连续黏性解。

特别地，从均分点 \(\mathbf z=\mathbf1\) 出发，

\[
\boxed{
\mathbb E\tau_N
=N^2a_k(\eta)+o(N^2),
\qquad a_k(\eta):=a_{k,\eta}(\mathbf1).
}
\]

## 4. 引理一：三角阵列函数型中心极限定理

一步均值和协方差为

\[
\mathbf d_N:=\mathbb E\boldsymbol\xi_1^{(N)}
=\frac{\boldsymbol\beta_\eta}{N},
\]

\[
\operatorname{Cov}(\boldsymbol\xi_1^{(N)})
=A_0-\mathbf d_N\mathbf d_N^\top
\longrightarrow A_0.
\]

因此

\[
\mathbf Z_N(s)
=\frac{\mathbf x^{(N)}}N
+\frac1N\sum_{r\le N^2s}
(\boldsymbol\xi_r^{(N)}-\mathbf d_N)
+\frac{\lfloor N^2s\rfloor}{N}\mathbf d_N.
\]

确定性项一致收敛到 \(\boldsymbol\beta_\eta s\)。中心化增量的范数至多
\(2/N\)，故 Lindeberg 条件自动成立；其可预测二次变差在紧时间区间上
收敛到 \(sA_0\)。三角阵列鞅/独立增量不变原理遂给出
\(\mathbf Z_N\Rightarrow\mathbf Z\)。因极限路径连续，Skorokhod
\(J_1\) 收敛可在表示下升级为紧区间上的一致收敛。

## 5. 引理二：首次出界时间的分布收敛

固定 \(t>0\)，令坐标运行最小值泛函

\[
m_i(f,t)=\min_{0\le s\le t}f_i(s).
\]

对连续路径，一致拓扑下 \(m_i\) 连续。事件 \(\{T>t\}\) 等于所有
\(m_i(\mathbf Z,t)>0\)；其边界包含于

\[
\bigcup_{i=0}^{k-1}\{m_i(\mathbf Z,t)=0\}.
\]

每个坐标 \(Z_i\) 是具有非零方差

\[
(A_0)_{ii}=\frac2k
\]

的一维 Brownian 运动加常漂移。它在有限时间区间上的运行最小值分布
连续，故上述有限并集概率为零。由连续映射/连续集定理，

\[
\Pr(T_N>t)\longrightarrow\Pr(T>t).
\]

对每个 \(t\) 都成立，因而 \(T_N\Rightarrow T\)。这一论证把三角形
三条边的直接证明推广到固定有限个单纯形面。

## 6. 引理三：统一均值界、几何尾与一致可积性

核心不是从过程收敛猜测尾部，而是先对第 \(N\) 个离散链的**所有内部
初态**建立统一 \(O(N^2)\) 均值界。

### 6.1 \(\eta=0\)

令

\[
V(\mathbf x)=\sum_i(x_i-N)^2.
\]

公平模型每步满足 \(\mathbb E(\Delta V\mid\mathcal F_t)=2\)。由有限状态
吸收引理和可选停止，

\[
\mathbb E_{\mathbf x}\tau_N
=\frac{\mathbb E_{\mathbf x}V(\mathbf X(\tau_N))-V(\mathbf x)}2
\le\frac{k(k-1)}2N^2.
\]

### 6.2 \(\eta>0\)

任取外围坐标 \(r\)。其每步漂移为

\[
d_r=-\frac{2\eta}{k(k-1)N}.
\]

由于任意内部初态都有 \(x_r\le kN\)，坐标鞅可选停止给出

\[
\sup_{\mathbf x}\mathbb E_{\mathbf x}\tau_N
\le\frac{k^2(k-1)}{2\eta}N^2.
\]

### 6.3 \(\eta<0\)

中心坐标漂移为

\[
d_0=-\frac{2|\eta|}{kN},
\]

从而

\[
\sup_{\mathbf x}\mathbb E_{\mathbf x}\tau_N
\le\frac{k^2}{2|\eta|}N^2.
\]

综上，对固定 \((k,\eta)\) 存在有限常数 \(A=A(k,\eta)\)，使

\[
\sup_{N\ge N_0}\sup_{\mathbf x}
\mathbb E_{\mathbf x}\tau_N\le AN^2.
\]

取整数块长 \(L_N=\lceil2AN^2\rceil\)。Markov 不等式和强 Markov
性质给出

\[
\sup_{\mathbf x}\Pr_{\mathbf x}(\tau_N>L_N)\le\frac12,
\]

继而迭代得到

\[
\boxed{
\sup_{\mathbf x}\Pr_{\mathbf x}(\tau_N>mL_N)\le2^{-m},
\qquad m=0,1,2,\ldots
}
\]

由于 \(L_N/N^2\le2A+1\)，对任意
\(0<c<\log2/(2A+1)\) 还有

\[
\sup_{N\ge N_0}\mathbb E\exp(cT_N)<\infty.
\]

因此 \(\{T_N^q\}\) 对每个固定实数 \(q>0\) 都一致可积。结合第 5 节
的分布收敛，

\[
\mathbb ET_N^q\longrightarrow\mathbb ET^q,\qquad q>0.
\]

这一步闭合了原工作稿最关键的期望收敛缺口，并把结论加强到全正阶矩。

## 7. 引理四：PDE 识别

在切向子空间 \(H\) 上，\(P_H\) 是恒等算子，因此极限扩散生成元为

\[
\mathcal A_\eta
=\boldsymbol\beta_\eta^\top\nabla
+\frac12A_0:\nabla^2
=\boldsymbol\beta_\eta^\top\nabla
+\frac1{k-1}\Delta_{\mathrm{tan}}.
\]

它在 \((k-1)\) 维切向空间上一致椭圆。单纯形有界并满足外锥条件；由
Dynkin/Feynman–Kac 表示，\(a_{k,\eta}(\mathbf z)=\mathbb E_{\mathbf z}T\)
连续延拓到闭单纯形、在边界为零，并满足相应 Dirichlet–Poisson 问题。
准确的弱形式为：对每个
\(\varphi\in H_0^1(\mathcal S_k^\circ)\)，

\[
\frac1{k-1}\int\nabla a\cdot\nabla\varphi
-\int(\boldsymbol\beta_\eta\cdot\nabla a)\varphi
=\int\varphi.
\]

Lax–Milgram 与常漂移项的反对称性给出唯一 \(H_0^1\) 变分弱解；
比较原理另给出唯一连续黏性解；椭圆正则性给出内部光滑性。单纯形角点
可能限制直至边界的经典正则性，因此不声称
\(a\in C^2(\overline{\mathcal S_k})\)。

## 8. 与先行工作的关系

| 先行工作 | 已有内容 | 对本项目的约束/差异 |
|---|---|---|
| Engel（1993）；Bruss、Louchard 与 Turner（2003） | 同一公平三塔/三人模型的 \(3xyz/(x+y+z)\) 精确均值 | 三人闭式是已知基线，不是本文贡献 |
| Alabert、Farré 与 Roy（2004） | 三角格随机游走到 Brownian 三角形的退出时间收敛、统一可积性和 Poisson 解 | \(k=3,\eta=0\) 的扩散结论亦已有直接先例 |
| Swan 与 Bruss（2006）；Marfil 与 David（2024） | 一般多人首次破产的吸收 Markov/线性系统计算 | \((I-Q)u=\mathbf1\) 是标准精确框架，不可包装为新数学定理 |
| Bruss、Louchard 与 Turner（2003） | 四塔大容量均值的 Poisson 渐近表达 | 公平 \(k=4\) PDE 近似已有明确先例 |
| Sobel 与 Frankowski（2002） | 公平 random-selection：随机选对、单位转移、首次有人破产 | 公平多人选对模型及差分方程并非本项目提出 |
| Diaconis、Houston-Edwards 与 Saloff-Coste（2021） | 有限 inner-uniform 域上的 gambler's-ruin/harmonic-measure 估计 | killed-chain 与 Perron–Frobenius 工具属于现有一般理论 |
| O’Connor 与 Saloff-Coste（2023） | 同一公平四人首次破产模型及连续单纯形谱/harmonic profile | 四人模型和 Brownian/simplex 近似均有直接先例 |
| Denisov 与 Wachtel（2024） | 三人模型 harmonic measure、Brownian 近似及收敛速率 | 三人退出位置渐近和 Brownian 近似已有更强先例 |
| Grigorescu 与 Yao（2016）；Kehagias et al.（2025） | 公平可控 pairwise 完全淘汰；三人非对称策略 pairwise 完全淘汰 | pairwise 多人 ruin 和非对称三人变体已有邻近研究 |
| Barnett（1964） | 三人 gambler's ruin 的非对称扩展；公开摘要未给完整转移核 | P0 全文闸门：未阅读全文前不能判断是否覆盖三人成对特例 |
| Rocha 与 Stern（1999、2004）及后续 | 一名赢家同时从其他所有玩家收款的非对称一般 \(n\) 人首次破产和矩 | 非对称一般 \(n\) 人并非新主题，但更新规则不是成对单位转账 |
| Kmet 与 Petkovšek（2002）；Tzioufas（2019） | 不同高维几何中的退出时间渐近；后者证明所有 \(p\)-阶矩极限 | 高维退出和全矩收敛的方法/现象均有先例，不能单独作创新 |
| Ekhad 与 Zeilberger（2023）；Phetpradap 与 Sripanitan（2025） | 公平三人多阶矩；不同非对称多人规则的任意整数阶矩公式 | “多人破产时间的全部阶矩”本身不能作为原创表述 |
| Rebolledo（1980）；Whitt（1980） | 局部鞅中心极限定理；首次通过时间等泛函的连续性条件 | 为第 4–5 节提供一般函数极限定理背景 |

截至 2026-07-17 的定向检索尚未找到与“固定任意 \(k\)、中心偏置
\(p_N=1+\eta/N\)、成对单位转账、首次任一坐标为零、且证明全矩收敛”
四项同时成立的结果；这只说明它是**模型特定的候选差异点**，不等于
已经证明全球首次。Barnett（1964）全文尚未核验，故连 \(k=3\) 非对称
特例也不能作排除式声明。FCLT、连续映射、Feynman–Kac 和“全矩”现象
均有一般或邻近先例，不能脱离强漂移相图、支付通道语义和可计算方法
单独包装成重大数学创新。逐篇比较见
[文献审计](sources/near_critical_asymmetric_search_audit_2026-07-17.md)。

## 9. 投稿前核查清单

- 逐行复核中心偏置增量均值、协方差与时间缩放。
- 给出所采用三角阵列不变原理的精确定理编号和拓扑。
- 将运行最小值连续集论证写成正式引理，并处理整数取整。
- 把三类统一均值界的可选停止条件与有限吸收引理交叉引用。
- 在主文固定 \(H_0^1\) 变分弱解或连续黏性解框架，不再混用概念。
- 明确写出统一指数矩，并据此陈述全部固定正阶矩收敛。
- 合法取得并全文核查 Barnett 1964，再完成一般非对称多人、近临界随机
  游走和多面体 killed diffusion 的引用追踪。
- 由未参与当前推导的概率论研究者按
  [09 外部评审包](09_weak_drift_external_review_packet.md) 的 R1–R12 独立签核。
- 对照 [内部对抗性审计](08_weak_drift_adversarial_audit.md) 逐条关闭问题。

## 10. 原始文献入口

- A. Engel, The Computer Solves the Three Tower Problem (1993): https://www.jstor.org/stable/2324818
- F. T. Bruss, G. Louchard and J. W. Turner, On the N-Tower Problem and Related Problems (2003): https://doi.org/10.1239/aap/1046366109
- A. Alabert, M. Farré and R. Roy, Exit Times from Equilateral Triangles (2004): https://doi.org/10.1007/s00245-003-0779-1
- Y. C. Swan and F. T. Bruss, A Matrix-Analytic Approach to the N-Player Ruin Problem (2006): https://doi.org/10.1239/jap/1158784944
- P. Diaconis and S. N. Ethier, Gambler's Ruin and the ICM (2022): https://doi.org/10.1214/21-STS826
- R. I. D. Marfil and G. David, Solution to the N-Player Gambler's Ruin Using Recursions Based on Multigraphs (2024): https://doi.org/10.1080/03610918.2023.2233173
- W. Whitt, Some Useful Functions for Functional Limit Theorems (1980): https://doi.org/10.1287/moor.5.1.67
- R. Rebolledo, Central Limit Theorems for Local Martingales (1980): https://doi.org/10.1007/BF00587353
- M. Sobel and K. Frankowski, Extensions of Gambler's Ruin with Even Odds (2002): https://doi.org/10.1016/S0378-3758(01)00191-4
- P. Diaconis, K. Houston-Edwards and L. Saloff-Coste, Gambler's Ruin Estimates on Finite Inner Uniform Domains (2021): https://doi.org/10.1214/20-AAP1607
- K. O'Connor and L. Saloff-Coste, The 4-Player Gambler's Ruin Problem (2023): https://doi.org/10.1007/978-3-031-37800-3_5
- D. Denisov and V. Wachtel, Harmonic Measure in a Multidimensional Gambler's Problem (2024): https://doi.org/10.1214/24-AAP2069
- I. Grigorescu and Y.-C. Yao, Maximizing the Variance of the Time to Ruin in a Multiplayer Game with Selection (2016): https://doi.org/10.1017/apr.2016.17
- A. Kehagias et al., Three-Gambler Ruin Game: A Game Theoretic Analysis (2025): https://doi.org/10.1007/s13235-025-00641-7
- V. D. Barnett, A Three-Player Extension of the Gambler's Ruin Problem (1964): https://doi.org/10.2307/3211863
- A. L. Rocha and F. Stern, The Gambler's Ruin Problem with n Players and Asymmetric Play (1999): https://doi.org/10.1016/S0167-7152(98)00295-8
- A. L. Rocha and F. Stern, The Asymmetric n-Player Gambler's Ruin Problem with Equal Initial Fortunes (2004): https://doi.org/10.1016/j.aam.2003.07.005
- A. Kmet and M. Petkovšek, Gambler's Ruin Problem in Several Dimensions (2002): https://doi.org/10.1006/aama.2001.0769
- A. Tzioufas, The Several Dimensional Gambler's Ruin Problem (2019): https://math-mprf.org/journal/articles/id1530/
- S. B. Ekhad and D. Zeilberger, Explicit Expressions for Moments of the Duration of a 3-Player Gambler's Ruin (2023): https://arxiv.org/abs/2309.08762
- P. Phetpradap and N. Sripanitan, On the Moments of the Asymmetric n-Player Gambler's Ruin Problem (2025): https://doi.org/10.1007/s40840-024-01790-5
