# 多项式消失漂移的停止时间相图

更新日期：2026-07-17  
对应登记：T15  
状态：A（内部工作稿证明闭合，待独立概率论复核）

## 1. 问题与证明合同

固定参与者数 \(k\ge2\)、非零常数 \(\eta\) 和指数 \(\alpha\ge0\)，令

\[
p_N=1+\eta N^{-\alpha}.
\]

只考虑充分大的正整数 \(N\)，使 \(p_N\in[0,2]\)。当 \(\alpha=0\)
时还需 \(\eta\in[-1,1]\setminus\{0\}\)。初始余额均分：

\[
X_i^{(N)}(0)=N,\qquad 0\le i\le k-1.
\]

每步均匀选择一个无序节点对；外围—外围方向公平；中心—外围对中，中心
收款的条件概率为 \(p_N/2\)。停止时间为

\[
\tau_N=\inf\{n\ge0:\min_iX_i^{(N)}(n)=0\}.
\]

本证明包统一此前两个分开的结果：

- 07：\(p_N-1=\eta/N\) 的弱漂移扩散退出；
- 10：固定 \(p\ne1\) 的强漂移指数集中。

它不处理增长的 \(k\)、非均分初值、一般流量矩阵、状态依赖交易概率、
随机支付金额或相关多超边网络。

## 2. 控制参数

一步漂移为

\[
d_{0,N}=\frac{2\eta}{kN^\alpha},\qquad
d_{r,N}=-\frac{2\eta}{k(k-1)N^\alpha},
\quad 1\le r\le k-1.
\]

距离边界为 \(N\)，扩散时间尺度为 \(N^2\)。因此决定漂移与扩散竞争的
无量纲参数为

\[
\mathrm{Pe}_N=N|p_N-1|
=|\eta|N^{1-\alpha}.
\]

于是：

\[
\begin{array}{c|c|c}
\alpha<1 & \mathrm{Pe}_N\to\infty & \text{漂移主导}\\
\alpha=1 & \mathrm{Pe}_N=|\eta| & \text{临界对流—扩散}\\
\alpha>1 & \mathrm{Pe}_N\to0 & \text{扩散主导}
\end{array}
\]

这不是由经验拟合得到的分类，而是以下三个严格极限的共同参数化。

## 3. 主定理

### 定理 PD

在第 1 节假设下：

### A. 漂移主导区 \(0\le\alpha<1\)

定义负漂移速度

\[
v_N=
\begin{cases}
\dfrac{2|\eta|}{kN^\alpha},&\eta<0,\\[6pt]
\dfrac{2\eta}{k(k-1)N^\alpha},&\eta>0,
\end{cases}
\]

以及

\[
t_{N,\alpha}^*=\frac{N}{v_N}
=
\begin{cases}
\dfrac{k}{2|\eta|}N^{1+\alpha},&\eta<0,\\[6pt]
\dfrac{k(k-1)}{2\eta}N^{1+\alpha},&\eta>0.
\end{cases}
\]

对任意固定 \(\varepsilon\in(0,1)\)，存在
\(c=c(k,\eta,\alpha,\varepsilon)>0\) 与 \(N_0\)，使

\[
\Pr\!\left(
\left|\frac{\tau_N}{t_{N,\alpha}^*}-1\right|>\varepsilon
\right)
\le(k+1)\exp\{-cN^{1-\alpha}\},
\qquad N\ge N_0.
\]

此外存在 \(\lambda_0>0\)，使

\[
\sup_{N\ge N_0}
\mathbb E\exp\!\left(
\lambda_0\frac{\tau_N}{t_{N,\alpha}^*}
\right)<\infty.
\]

因此对每个固定 \(q>0\)，

\[
\mathbb E\left(
\frac{\tau_N}{t_{N,\alpha}^*}
\right)^q\longrightarrow1.
\]

### B. 临界区 \(\alpha=1\)

令 \(\mathbf Z_\eta\) 为 07 中从均分点出发、漂移
\(\boldsymbol\beta_\eta\)、切向协方差 \(A_0\) 的 Brownian 运动，
并令 \(T_\eta\) 为其首次离开开单纯形的时间。则

\[
\frac{\tau_N}{N^2}\Rightarrow T_\eta,
\qquad
\mathbb E\left(\frac{\tau_N}{N^2}\right)^q
\longrightarrow\mathbb ET_\eta^q
\quad(q>0).
\]

### C. 扩散主导区 \(\alpha>1\)

令 \(T_0\) 为同一切向 Brownian 运动在零漂移下的首次单纯形退出时间。
则

\[
\frac{\tau_N}{N^2}\Rightarrow T_0,
\qquad
\mathbb E\left(\frac{\tau_N}{N^2}\right)^q
\longrightarrow\mathbb ET_0^q
\quad(q>0).
\]

若 \(\eta=0\)，则 \(p_N\equiv1\)，对任意 \(\alpha\) 都直接落入 C 的
公平扩散结论。

## 4. 漂移主导区证明

### 4.1 自由延拓与坐标鞅

与 10 相同，在首次退出后继续使用同一串独立增量，定义自由过程

\[
Z_i^{(N)}(n)
=N+\sum_{\ell=1}^{n}\xi_i^{(N)}(\ell)
\]

和

\[
M_i^{(N)}(n)
=Z_i^{(N)}(n)-N-d_{i,N}n.
\]

单位步长保证

\[
\tau_N=\min_i\inf\{n:Z_i^{(N)}(n)=0\}.
\]

每个 \(M_i^{(N)}\) 是鞅且

\[
|\Delta M_i^{(N)}|\le2.
\]

### 4.2 过早退出

令

\[
n_-=\left\lfloor(1-\varepsilon)t_{N,\alpha}^*\right\rfloor.
\]

所有负漂移坐标在 \(s\le n_-\) 时的确定性均值至少为
\(\varepsilon N\)，所有正漂移坐标的确定性均值至少为 \(N\)。若
\(\tau_N\le n_-\)，某个坐标鞅必在 \(n_-\) 前向下偏离至少
\(\varepsilon N\)。最大型 Azuma–Hoeffding 与并集界给出

\[
\Pr(\tau_N\le n_-)
\le k\exp\!\left(-\frac{\varepsilon^2N^2}{8n_-}\right)
\le k\exp\!\left(
-\frac{\varepsilon^2v_NN}{8(1-\varepsilon)}
\right).
\]

写 \(v_N=a_\eta N^{-\alpha}\)，其中

\[
a_\eta=
\begin{cases}
2|\eta|/k,&\eta<0,\\
2\eta/[k(k-1)],&\eta>0,
\end{cases}
\]

便得到 \(e^{-cN^{1-\alpha}}\) 早尾。

### 4.3 过晚退出

令

\[
n_+=\left\lceil(1+\varepsilon)t_{N,\alpha}^*\right\rceil
\]

并固定任一负漂移坐标 \(j\)。若 \(\tau_N>n_+\)，则

\[
M_j^{(N)}(n_+)>v_Nn_+-N\ge\varepsilon N.
\]

因此

\[
\Pr(\tau_N>n_+)
\le\exp\!\left(-\frac{\varepsilon^2N^2}{8n_+}\right)
\le\exp\!\left(
-\frac{\varepsilon^2v_NN}{16(1+\varepsilon)}
\right)
\]

对充分大 \(N\) 成立。早尾和晚尾联合即得 A 中的相对集中，且可以取

\[
c=\frac{\varepsilon^2a_\eta}{16(1+\varepsilon)}.
\]

### 4.4 统一指数矩

对同一负漂移坐标，当

\[
n\ge\left\lceil\frac{2N}{v_N}\right\rceil
\]

时，

\[
\Pr(\tau_N>n)
\le\exp\!\left(-\frac{v_N^2n}{32}\right).
\]

取任意固定 \(\lambda_0>0\)，并令

\[
z_N=\exp\!\left(\frac{\lambda_0}{t_{N,\alpha}^*}\right)
=\exp\!\left(\frac{\lambda_0v_N}{N}\right).
\]

因为

\[
Nv_N=a_\eta N^{1-\alpha}\longrightarrow\infty,
\]

可以选 \(N_0\) 使

\[
\frac{\lambda_0v_N}{N}\le\frac{v_N^2}{64}.
\]

对整数值停止时间使用

\[
\mathbb Ez_N^{\tau_N}
=1+(z_N-1)\sum_{n\ge0}z_N^n\Pr(\tau_N>n).
\]

在 \(\lceil2N/v_N\rceil\) 前，尾和被
\(\exp(3\lambda_0)\) 一致控制；在其后，

\[
z_N^n\Pr(\tau_N>n)
\le\exp\!\left(-\frac{v_N^2n}{64}\right).
\]

又因 \(z_N-1=O(v_N/N)\) 且
\((1-e^{-v_N^2/64})^{-1}=O(v_N^{-2})\)，尾部贡献为

\[
O\!\left(\frac1{Nv_N}\right)=O(N^{\alpha-1}),
\]

从而一致有界。这证明 A 的统一指数矩。相对集中给出依概率收敛，指数矩
给出所有固定正阶矩的一致可积性，故 A 证明完毕。

## 5. 临界区证明

当 \(\alpha=1\) 时，

\[
\mathbb E\xi_1^{(N)}
=\frac{\boldsymbol\beta_\eta}{N}.
\]

在 \(N^2\) 时间和 \(N\) 空间缩放下，累计漂移收敛到
\(\boldsymbol\beta_\eta t\)，中心化鞅部分收敛到协方差 \(A_0\) 的
切向 Brownian 运动。首次出界连续集、全状态 \(O(N^2)\) 均值界、
强 Markov 几何尾、统一指数矩和 PDE 识别已经在 07–09 中逐项写明。
因此 B 是 07 主定理从均分初值出发的直接引用，不重复证明。

## 6. 扩散主导区证明

### 6.1 零漂移函数极限

当 \(\alpha>1\) 时，

\[
\mathbb E\xi_1^{(N)}
=\frac{\boldsymbol\beta_\eta}{N^\alpha}.
\]

对缩放过程

\[
\mathbf Z_N(t)
=\frac1N\left(
N\mathbf1+\sum_{r\le\lfloor N^2t\rfloor}\xi_r^{(N)}
\right),
\]

其确定性漂移为

\[
\frac{\lfloor N^2t\rfloor}{N}
\frac{\boldsymbol\beta_\eta}{N^\alpha}
\longrightarrow0
\]

且在紧时间区间上一致收敛。协方差仍收敛到 \(A_0\)，有界增量自动满足
Lindeberg 条件。因此

\[
\mathbf Z_N\Rightarrow
\mathbf1+A_0^{1/2}\mathbf W_H.
\]

07 的运行最小值连续集论证不依赖非零漂移，故

\[
\tau_N/N^2\Rightarrow T_0.
\]

### 6.2 小漂移下的统一 \(O(N^2)\) 均值界

令

\[
V(\mathbf x)=\sum_{i=0}^{k-1}(x_i-N)^2.
\]

对任一内部状态，

\[
\mathbb E(\Delta V\mid\mathbf X=\mathbf x)
=2+2(\mathbf x-N\mathbf1)^\top\mathbf d_N,
\qquad
\mathbf d_N=\frac{\boldsymbol\beta_\eta}{N^\alpha}.
\]

在总余额为 \(kN\) 的单纯形上，

\[
\|\mathbf x-N\mathbf1\|_1\le2(k-1)N,
\qquad
\|\mathbf d_N\|_\infty
=\frac{2|\eta|}{kN^\alpha}.
\]

所以

\[
\left|
2(\mathbf x-N\mathbf1)^\top\mathbf d_N
\right|
\le\frac{8(k-1)|\eta|}{k}N^{1-\alpha}.
\]

因 \(\alpha>1\)，可选 \(N_0\) 使右侧不超过 1，进而对所有内部状态

\[
\mathbb E(\Delta V\mid\mathcal F_n)\ge1.
\]

同时整个闭单纯形上

\[
0\le V(\mathbf x)\le k(k-1)N^2.
\]

对 \(\tau_N\wedge m\) 停止并取期望，

\[
\mathbb E(\tau_N\wedge m)
\le
\mathbb EV(\mathbf X(\tau_N\wedge m))-V(\mathbf X(0))
\le k(k-1)N^2.
\]

令 \(m\to\infty\)，得到对所有内部初态同样成立的统一界

\[
\sup_{\mathbf x}
\mathbb E_{\mathbf x}\tau_N
\le k(k-1)N^2.
\]

### 6.3 统一指数矩与全矩

令

\[
L_N=\left\lceil2k(k-1)N^2\right\rceil.
\]

Markov 不等式和强 Markov 性给出

\[
\sup_{\mathbf x}
\Pr_{\mathbf x}(\tau_N>mL_N)\le2^{-m}.
\]

因此存在 \(c=c(k)>0\)，使

\[
\sup_{N\ge N_0}
\mathbb E\exp\!\left(c\frac{\tau_N}{N^2}\right)<\infty.
\]

这使所有固定正阶矩一致可积。结合分布收敛即得 C。

## 7. 统一解释

| 区间 | 一步漂移 | 停止时间尺度 | 极限性质 | 正负不对称 |
|---|---:|---:|---|---|
| \(0\le\alpha<1\) | \(N^{-\alpha}\) | \(N^{1+\alpha}\) | 相对指数集中于确定性常数；全矩收敛 | 负侧 1 个中心坐标；正侧 \(k-1\) 个外围坐标 |
| \(\alpha=1\) | \(N^{-1}\) | \(N^2\) | 带常漂移 Brownian 单纯形退出；全矩收敛 | 进入极限漂移向量 \(\boldsymbol\beta_\eta\) |
| \(\alpha>1\) | \(o(N^{-1})\) | \(N^2\) | 零漂移 Brownian 单纯形退出；全矩收敛 | 首阶极限中消失 |

相图说明 \(1/N\) 不是任意选择，而是中心偏置在 \(N^2\) 扩散时间内
累计到 \(O(N)\) 边界距离的唯一临界多项式尺度。

## 8. 文献与新颖性边界

小漂移和弱不对称随机游走已有直接先例，故“发现临界尺度 \(1/N\)”本身
不能作为原创主张：

- Athreya、Sethuraman 与 Tóth（2010）在长度 \(N\) 的一维区间上明确
  比较对称、\(1/N\) 弱不对称和固定不对称随机游走，并研究退出时的
  range、local times 与 periodicity；
- Wachtel（2009）研究小负漂移随机游走下降阶梯时刻的转变现象和矩增长；
- Schulte-Geers 与 Stadje（2017）研究小正漂移下占用时间的极限定理；
- Geng 与 Markowsky（2026）研究有偏随机游走和漂移 Brownian 运动在
  对称区间内退出时间关于漂移的随机单调性。

它们为尺度转变和证明工具提供先例，但当前核验材料没有给出本项目
“固定一般 \(k\)、守恒单纯形、中心偏置成对转账、首次任一余额为零、
\(\alpha\) 三分区且全部固定正阶矩收敛”的完整组合。

因此 T15 只能定位为模型特定的统一相图候选。它的论文价值来自把弱漂移、
强漂移、正负不对称和支付通道容量尺度组织成同一可检验定理，而不是来自
小漂移、FCLT、Azuma 或全矩现象本身。完整检索边界见
[多项式漂移相图文献审计](sources/polynomial_drift_phase_search_audit_2026-07-17.md)。

## 9. 外部复核清单

独立概率论复核者应逐项签核：

1. \(p_N\) 的合法范围与 \(\alpha=0\) 对 \(\eta\) 的额外约束；
2. \(d_{0,N}\)、\(d_{r,N}\) 和 \(\mathrm{Pe}_N\) 的常数；
3. \(\alpha<1\) 时自由延拓和最大型 Azuma 的使用；
4. 早尾与晚尾指数确为 \(N^{1-\alpha}\)；
5. \(\alpha<1\) 统一指数矩中
   \(O((Nv_N)^{-1})\) 尾部估计；
6. 从统一指数矩到任意实数 \(q>0\) 的一致可积性；
7. \(\alpha=1\) 是否完全满足 07–09 的定理合同；
8. \(\alpha>1\) FCLT 中累计漂移
   \(N^{1-\alpha}\boldsymbol\beta_\eta\to0\)；
9. 势函数增量公式中的因子 2 与
   \(\|\mathbf x-N\mathbf1\|_1\) 上界；
10. 小漂移势函数下界是否对全部内部状态统一；
11. 强 Markov 分块是否给出 \(\tau_N/N^2\) 的统一指数矩；
12. 定理没有误含增长 \(k\)、非均分初值或 T12 二阶竞争修正。

任一关键项失败时，T15 应降为 B 或拆回 T9–T11；在独立签核前，只能称
其为内部闭合工作稿。
