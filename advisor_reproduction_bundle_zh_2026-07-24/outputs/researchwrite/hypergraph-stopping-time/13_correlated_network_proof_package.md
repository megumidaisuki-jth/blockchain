# 相关超图网络首次余额耗尽：T16–T18 证明包

更新日期：2026-07-17  
文档性质：**internal proof draft / 内部证明工作稿；证明链内部闭合，但尚未取得独立概率论签核**  
发布状态：**not publication-ready**

## 0. 一句话论证与状态

在固定有限超图和外生 i.i.d. 有界路由增量下，本文先用有限状态耗尽可达性严格闭合吸收与 Poisson 方程，再按多项式漂移尺度证明确定性集中或相关 Brownian 乘积单纯形退出极限，并把高斯块独立的充分条件与冻结相关核的独立边代理诊断分开陈述。

主要读者是核查信任链和主张边界的外部概率论研究者。下表中的“证明成立”只表示本工作稿给出了完整推导，不表示已经通过独立评审。

| 标签 | 本包状态 | 精确边界 |
|---|---|---|
| T16 | **PROVED — internal, unsigned** | 对每个具有非空内部状态空间且满足有限状态耗尽可达性的固定 $N$ 成立 |
| T17A | **PROVED — internal, unsigned** | $0\le\alpha<1$、$\boldsymbol\beta\ne0$；给出集中、统一指数矩和全部固定正阶矩 |
| T17B | **PROVED — internal, unsigned** | $\alpha=1$；过程、退出时间及全部固定正阶矩收敛 |
| T17C | **PROVED — internal, unsigned** | $\alpha>1$；零漂移过程、退出时间及全部固定正阶矩收敛 |
| T18a | **PROVED — internal, unsigned** | 只针对联合高斯极限；跨超边协方差块为零是块独立的充分条件 |
| T18-A 临界扰动桥接引理 | **PROVED — internal, unsigned** | 对平衡基准中的互逆路由对施加 \(\pm a/N\) 概率扰动；给出精确漂移与协方差恒等式 |
| T18b | **MIXED — formal grid complete** | 冻结增量律的非因子化是严格结论；三类非同构拓扑、三类临界漂移和四个尺度的配对停止时间差已完成正式实验，但仍不是统一符号定理 |

## 1. 术语、模型和共同假设

### 1.1 锁定术语

| 规范术语 | 本包中的唯一含义 |
|---|---|
| network first-depletion time / 网络首次余额耗尽时间 | 首个余额坐标等于零的时刻 $\tau_N^{\mathrm{net}}$ |
| route alphabet / 路由字母表 | 固定有限的简单单位支付路径集合 $\mathcal A$ |
| product simplex / 乘积单纯形 | 每条超边各有一个守恒单纯形的笛卡尔积 |
| finite-state depletion reachability / 有限状态耗尽可达性 | 从每个内部状态存在一个正概率路由词到达边界的显式假设 |
| independent-edge proxy / 独立边代理 | 只保留逐边边际增量并把边块独立抽样的诊断；它不是路由流量 |
| internal proof draft / 内部证明工作稿 | 可以内部闭合，但在独立评审签字前仍是未签署材料 |

本文的停止量不改称路由失败、通道关闭或网络断连；后三者需要另外的拒绝、删除和重路由语义。

### 1.2 状态空间与自由延拓

坐标集为

\[
\mathcal I=\{(e,v):e\in E,\ v\in e\},\qquad
D=|\mathcal I|,
\]

第 $e$ 条超边有 $k_e=|e|$ 个参与者和总余额 $Nc_e$。记

\[
\mathcal S_N^\circ
=\prod_{e\in E}\left\{
\mathbf x_e\in\mathbb Z_{>0}^{k_e}:
\sum_{v\in e}x_{e,v}=Nc_e
\right\}.
\]

只考虑 $\mathcal S_N^\circ\ne\varnothing$ 的 admissible $N$。初态满足

\[
\frac{\mathbf x_N}{N}\longrightarrow\mathbf z\in\mathcal D,
\quad
\mathcal D=\prod_{e\in E}\left\{
\mathbf y_e>0:\sum_{v\in e}y_{e,v}=c_e
\right\}.
\]

对第 $N$ 个系统，令 $\boldsymbol\xi_{N,1},\boldsymbol\xi_{N,2},\ldots$
为由路由字母表诱导的 i.i.d. 增量，且

\[
\|\boldsymbol\xi_{N,r}\|_\infty\le1,
\quad
\mathbf d_N=\mathbb E\boldsymbol\xi_{N,1},
\quad
\Gamma_N=\operatorname{Cov}(\boldsymbol\xi_{N,1}).
\]

每个增量逐超边守恒。因而它们位于乘积切空间

\[
H=\left\{\mathbf y\in\mathbb R^D:
\sum_{v\in e}y_{e,v}=0\ \text{for every }e\right\}.
\]

在边界之后继续使用同一独立增量序列，定义自由过程

\[
\widetilde{\mathbf X}_N(n)
=\mathbf x_N+\sum_{r=1}^n\boldsymbol\xi_{N,r}.
\]

单位支付和简单路由保证每个坐标单步至多减少一，故从正整数出发不会越过零而不命中零；因此

\[
\tau_N^{\mathrm{net}}
=\inf\{n\ge0:\min_{i\in\mathcal I}\widetilde X_{N,i}(n)=0\}.
\]

自由延拓只服务于固定时刻鞅不等式和函数极限定理，不改变停止前的支付语义。

渐近模块还假设

\[
N^\alpha\mathbf d_N\to\boldsymbol\beta,
\qquad
\Gamma_N\to\Gamma,
\qquad
\Gamma_{ii}>0\quad(i\in\mathcal I).
\]

逐超边守恒给出 $\boldsymbol\beta\in H$ 和 $\Gamma\mathbf1_e=0$。最后一个条件是每个边界面的正法向方差条件；不要求 $\Gamma$ 在整个 $\mathbb R^D$ 上可逆。

## 2. T16：有限状态吸收与 Poisson 方程

### 命题 T16

固定 admissible $N$。若从 $\mathcal S_N^\circ$ 的每个状态都存在一个由正概率路由组成的有限路由词，使单位支付过程在该词执行期间到达乘积单纯形边界，则：

1. 内部状态数为
   \[
   |\mathcal S_N^\circ|
   =\prod_{e\in E}\binom{Nc_e-1}{k_e-1};
   \]
2. 网络首次余额耗尽时间几乎处处有限且具有有限均值；
3. 若 $Q_N$ 是内部—内部次随机转移矩阵，则
   \[
   Q_N^m\to0,\qquad
   \rho(Q_N)<1,
   \qquad
   (I-Q_N)^{-1}=\sum_{m=0}^\infty Q_N^m;
   \]
4. 均值向量是 Poisson 方程
   \[
   (I-Q_N)\mathbf u_N=\mathbf1
   \]
   的唯一解，并且 $u_N(\mathbf x)=\mathbb E_{\mathbf x}\tau_N^{\mathrm{net}}$。

### 证明

**状态计数。** 对固定超边 $e$，把 $Nc_e$ 写成 $k_e$ 个有序正整数之和，隔板法给出 $\binom{Nc_e-1}{k_e-1}$ 个正组合。不同超边的守恒约束彼此分块，完整内部状态是这些正组合的笛卡尔积，故状态数是上述乘积。

**内部转移可执行。** 在任一内部状态，每个付款坐标至少为一。简单路由在同一超边内只出现一次，所以一次单位路由对每个被使用超边恰有一个坐标减一、一个坐标加一；所有减法都合法，且逐超边总余额保持不变。若某付款坐标原值为一，支付完成后该坐标成为零并到达边界；否则下一状态仍在 $\mathcal S_N^\circ$。因此 $Q_N$ 中保留的每条内部转移都对应一笔可执行的单位路由，而不是形式上的不可行跳转。

**正概率路径。** 对每个 $x\in\mathcal S_N^\circ$，可达性假设给出路由词

\[
w_x=(a_{x,1},\ldots,a_{x,\ell_x}),
\qquad
p_x=\prod_{r=1}^{\ell_x}\pi_N(a_{x,r})>0,
\]

其执行路径在第 $\ell_x$ 步之前留在内部，并在不晚于第 $\ell_x$ 步到达边界。上一段保证这个词的每个边界前步骤都实际可执行。

**排除闭合内部类并得到定量收缩。** 状态空间有限，令

\[
L_N=\max_x\ell_x<\infty,
\qquad
\delta_N=\min_xp_x>0.
\]

从任一内部状态出发，在 $L_N$ 步内被吸收的概率至少为 $\delta_N$。于是

\[
Q_N^{L_N}\mathbf1\le(1-\delta_N)\mathbf1,
\]

并由次随机矩阵的单调性迭代为

\[
\|Q_N^{rL_N}\|_\infty\le(1-\delta_N)^r.
\]

若存在闭合内部沟通类，从该类出发永远不能到达边界，这与正概率路由词矛盾。上式进一步给出 $Q_N^m\to0$，并由谱半径公式得到

\[
\rho(Q_N)^{L_N}\le1-\delta_N<1.
\]

因此 Neumann 级数在算子范数下收敛，并确为 $I-Q_N$ 的逆。

**吸收、Poisson 方程和唯一性。** 对内部初态 $x$，

\[
\Pr_x(\tau_N^{\mathrm{net}}>m)=(Q_N^m\mathbf1)(x).
\]

上面的块几何界同时给出 $\Pr_x(\tau_N^{\mathrm{net}}=\infty)=0$ 和

\[
\mathbb E_x\tau_N^{\mathrm{net}}
=\sum_{m=0}^\infty\Pr_x(\tau_N^{\mathrm{net}}>m)
=\left(\sum_{m=0}^\infty Q_N^m\mathbf1\right)(x)<\infty.
\]

第一步分解给出 $\mathbf u_N=\mathbf1+Q_N\mathbf u_N$。因为 $I-Q_N$ 可逆，该解唯一，且

\[
\mathbf u_N=(I-Q_N)^{-1}\mathbf1.
\]

证毕。

### 2.1 反向可达实现的证书边界

`network_exact.py::build_transient_matrix` 枚举每条超边的正组合及其笛卡尔积，标记一步到达零坐标的内部状态为 `leaks`，再沿内部转移图的反向邻接表搜索。返回的 `all_states_reach_boundary=True` 精确表示：**对给定的有限 $N$、给定浮点概率向量的正支持以及给定路由增量表，枚举图中的每个内部状态都能沿正支持边到达某个 leak。**

它不证明以下命题：所有 $N$ 自动可达；任意未输入的拓扑或路由分布可达；渐近法向方差可推出有限状态吸收；程序实现本身无误；或者稀疏线性求解的数值误差为零。因此主定理仍把有限状态耗尽可达性列为数学假设，代码只核查特定有限实例。

冻结两三元超边实例的证书如下；全部数值来自 `results/network/network-exact.csv`，文件哈希见 `results/network/SHA256SUMS.txt`。

| scale $N$ | 内部状态数 | 精确均值 | 最大绝对残差 | 全状态可达边界 |
|---:|---:|---:|---:|:---:|
| 1 | 1 | 1.000000000000000 | 0 | Yes |
| 2 | 100 | 3.845405988723624 | $2.4424906541753444\times10^{-15}$ | Yes |
| 3 | 784 | 8.654869502436274 | $6.8833827526759706\times10^{-15}$ | Yes |

这三行是有限 $N$ 计算证书，不替代 T16 的一般证明。

## 3. T17A：$0\le\alpha<1$ 的漂移主导区

假设 $\boldsymbol\beta\ne0$。因每个超边块的坐标和为零，至少一个坐标具有负漂移。定义

\[
\theta_*
=\min_{i:\beta_i<0}\frac{z_i}{-\beta_i},
\qquad
t_{N,*}=\theta_*N^{1+\alpha}.
\]

### 定理 T17A

对每个固定 $\varepsilon\in(0,1)$，存在 $c_\varepsilon>0$ 和 $N_\varepsilon<\infty$，使所有 $N\ge N_\varepsilon$ 满足

\[
\Pr\left(
\left|\frac{\tau_N^{\mathrm{net}}}{t_{N,*}}-1\right|>\varepsilon
\right)
\le(D+1)e^{-c_\varepsilon N^{1-\alpha}}.
\]

还存在 $\lambda_0>0$，使

\[
\sup_{N\ge N_0}\mathbb E
\exp\left(\lambda_0\frac{\tau_N^{\mathrm{net}}}{t_{N,*}}\right)<\infty.
\]

因此对任意固定 $q>0$，

\[
\mathbb E\left(
\frac{\tau_N^{\mathrm{net}}}{t_{N,*}}
\right)^q\longrightarrow1.
\]

### 3.1 早尾：所有坐标的确定性余量

写 $\mathbf b_N=N^\alpha\mathbf d_N$。令

\[
g_\varepsilon
=\min_i\left\{
z_i+(1-\varepsilon)\theta_*\min(\beta_i,0)
\right\}.
\]

若 $\beta_i<0$，由 $\theta_*\le z_i/(-\beta_i)$ 得括号内至少为 $\varepsilon z_i$；若 $\beta_i\ge0$，括号内等于 $z_i$。所以 $g_\varepsilon>0$。由 $\mathbf x_N/N\to\mathbf z$ 和 $\mathbf b_N\to\boldsymbol\beta$，对充分大 $N$，

\[
\left\|\frac{\mathbf x_N}{N}-\mathbf z\right\|_\infty
\le\frac{g_\varepsilon}{4},
\qquad
(1-\varepsilon)\theta_*
\|\mathbf b_N-\boldsymbol\beta\|_\infty
\le\frac{g_\varepsilon}{4}.
\]

令 $n_-=\lfloor(1-\varepsilon)t_{N,*}\rfloor$。对 $0\le s\le n_-$ 和每个坐标 $i$，

\[
\frac{x_{N,i}+s d_{N,i}}N
=\frac{x_{N,i}}N+\frac{s}{N^{1+\alpha}}b_{N,i}
\ge\frac{g_\varepsilon}{2}.
\]

定义坐标鞅

\[
M_{N,i}(s)=\sum_{r=1}^s(\xi_{N,r,i}-d_{N,i}),
\qquad |\Delta M_{N,i}|\le2.
\]

若 $\tau_N^{\mathrm{net}}\le n_-$，某个坐标在某个 $s\le n_-$ 命中零，因而该坐标鞅在此前向下偏离至少 $g_\varepsilon N/2$。最大型 Azuma 和有限坐标并集给出

\[
\Pr(\tau_N^{\mathrm{net}}\le n_-)
\le D\exp\left{-
\frac{g_\varepsilon^2}{32(1-\varepsilon)\theta_*}
N^{1-\alpha}\right\}.
\]

这一步同时使用了初态收敛与漂移收敛；没有把 $o(N^{-\alpha})$ 余项略去。

### 3.2 晚尾：一个达到 $\theta_*$ 的负漂移坐标

固定 $j$ 使

\[
\beta_j<0,
\qquad
\theta_*=\frac{z_j}{-\beta_j}.
\]

令

\[
a_N=(1+\varepsilon)t_{N,*},
\qquad
m_+=\lfloor a_N\rfloor.
\]

因为 $\tau_N^{\mathrm{net}}$ 取整数值，

\[
\left\{
\frac{\tau_N^{\mathrm{net}}}{t_{N,*}}>1+\varepsilon
\right\}
=\{\tau_N^{\mathrm{net}}>a_N\}
=\{\tau_N^{\mathrm{net}}>m_+\}.
\]

写 $\mathbf b_N=N^\alpha\mathbf d_N$。由 $0\le a_N-m_+<1$，

\[
\frac{x_{N,j}+m_+d_{N,j}}N
=\frac{x_{N,j}}N
+(1+\varepsilon)\theta_*b_{N,j}
-\frac{(a_N-m_+)b_{N,j}}{N^{1+\alpha}}
\longrightarrow
z_j+(1+\varepsilon)\theta_*\beta_j
=-\varepsilon z_j.
\]

最后一项正是 floor 带来的至多一步误差；$\mathbf b_N$ 有界使它为
$O(N^{-1-\alpha})$。因此对充分大 $N$，

\[
x_{N,j}+m_+d_{N,j}
\le-\frac{\varepsilon z_j}{2}N,
\qquad
m_+\le2(1+\varepsilon)\theta_*N^{1+\alpha}.
\]

在上述等价事件上，自由过程的第 $j$ 坐标在 $m_+$ 时仍为正，因此

\[
M_{N,j}(m_+)>
\frac{\varepsilon z_j}{2}N.
\]

固定时刻 Azuma 给出

\[
\Pr\left(
\frac{\tau_N^{\mathrm{net}}}{t_{N,*}}>1+\varepsilon
\right)
=\Pr(\tau_N^{\mathrm{net}}>m_+)
\le\exp\left\{-
\frac{\varepsilon^2z_j^2}{64(1+\varepsilon)\theta_*}
N^{1-\alpha}\right\}.
\]

与早尾联合后可取

\[
c_\varepsilon=
\min\left\{
\frac{g_\varepsilon^2}{32(1-\varepsilon)\theta_*},
\frac{\varepsilon^2z_j^2}{64(1+\varepsilon)\theta_*}
\right\}.
\]

### 3.3 长尾块与统一指数矩

写 $h=-\beta_j>0$，故 $z_j=h\theta_*$。对充分大 $N$，

\[
x_{N,j}\le2z_jN,
\qquad
-d_{N,j}\ge\frac{h}{2N^\alpha},
\qquad
t_{N,*}\ge1.
\]

对整数 $r\ge9$ 置 $m_r=\lfloor r t_{N,*}\rfloor$。于是

\[
m_r\ge(r-1)t_{N,*}\ge8t_{N,*},
\]

从而 $(-d_{N,j})m_r\ge2x_{N,j}$，并有

\[
x_{N,j}+m_rd_{N,j}
\le-\frac{(-d_{N,j})m_r}{2}.
\]

事件 $\{\tau_N^{\mathrm{net}}>m_r\}$ 蕴含

\[
M_{N,j}(m_r)>\frac{(-d_{N,j})m_r}{2}.
\]

再用固定时刻 Azuma，得到对所有充分大 $N$ 和 $r\ge9$ 一致成立的块尾界

\[
\Pr\left(\frac{\tau_N^{\mathrm{net}}}{t_{N,*}}>r\right)
\le
\exp\{-a(r-1)N^{1-\alpha}\}
\le e^{-a(r-1)},
\qquad
a=\frac{h^2\theta_*}{128}>0.
\]

取 $\lambda_0=a/2$，按区间 $r<\tau_N^{\mathrm{net}}/t_{N,*}\le r+1$ 分块，

\[
\begin{aligned}
\mathbb E e^{\lambda_0\tau_N^{\mathrm{net}}/t_{N,*}}
&\le e^{9\lambda_0}
+\sum_{r=9}^\infty
e^{\lambda_0(r+1)}
\Pr\left(\frac{\tau_N^{\mathrm{net}}}{t_{N,*}}>r\right)\\
&\le e^{9\lambda_0}
+e^{\lambda_0+a}\sum_{r=9}^\infty
e^{-(a-\lambda_0)r}<\infty,
\end{aligned}
\]

且右端与 $N$ 无关。这闭合了长尾常数。相对集中给出依概率收敛，统一指数矩使任意固定 $q>0$ 的 $q$ 次幂一致可积，故 T17A 的全部正阶矩结论成立。

## 4. T17B/C：函数极限与退出映射

### 4.1 三角阵列函数型中心极限定理

定义自由缩放过程

\[
\mathbf Z_N(t)
=\frac{\mathbf x_N}{N}
+\frac1N\sum_{r=1}^{\lfloor N^2t\rfloor}\boldsymbol\xi_{N,r}.
\]

中心化后

\[
\mathbf Z_N(t)
=\frac{\mathbf x_N}{N}
+\frac1N\sum_{r=1}^{\lfloor N^2t\rfloor}
(\boldsymbol\xi_{N,r}-\mathbf d_N)
+\frac{\lfloor N^2t\rfloor}{N}\mathbf d_N.
\]

中心化缩放增量的欧氏范数至多 $2\sqrt D/N$，所以每个固定 Lindeberg 截断阈值在充分大 $N$ 后没有贡献。其协方差和在时间 $t$ 收敛到 $t\Gamma$：

\[
\frac{\lfloor N^2t\rfloor}{N^2}\Gamma_N\longrightarrow t\Gamma.
\]

由于每个增量属于 $H$，协方差收敛和紧性都在固定维乘积切空间 $H$ 内进行。三角阵列 Donsker 定理于是给出

\[
\frac1N\sum_{r=1}^{\lfloor N^2\,\cdot\rfloor}
(\boldsymbol\xi_{N,r}-\mathbf d_N)
\Rightarrow\Gamma^{1/2}\mathbf W_H(\cdot)
\]

于 $D([0,\infty),H)$。确定性项在紧时间区间上一致满足

\[
\frac{\lfloor N^2t\rfloor}{N}\mathbf d_N
=t(N\mathbf d_N)+o(1).
\]

因此

\[
\mathbf Z_N\Rightarrow\mathbf Z_b,
\qquad
\mathbf Z_b(t)=\mathbf z+\mathbf b t+\Gamma^{1/2}\mathbf W_H(t),
\]

其中

\[
\mathbf b=
\begin{cases}
\boldsymbol\beta,&\alpha=1,\\
\mathbf0,&\alpha>1.
\end{cases}
\]

这同时给出了 $N^2$ 时钟上 $N\mathbf d_N$ 确定性项的精确去向。

### 4.2 退出映射连续性引理

对连续路径
$f:[0,\infty)\to\prod_e\{\mathbf x_e:\sum_vx_{e,v}=c_e\}$，定义

\[
\Phi(f)=\inf\{t\ge0:\min_i f_i(t)\le0\}.
\]

**引理。** 若 $T=\Phi(f)<\infty$，且

1. 对每个 $\delta\in(0,T)$，路径在 $[0,T-\delta]$ 严格位于内部；
2. 对每个 $\delta>0$，存在 $s\in(T,T+\delta)$ 使某个坐标 $f_i(s)<0$；

则 $\Phi$ 在 $f$ 处关于紧区间一致收敛连续。

**证明。** 固定 $\delta\in(0,T)$。连续性、坐标有限性和紧致性给出

\[
\min_{0\le s\le T-\delta}\min_i f_i(s)>0.
\]

故充分接近 $f$ 的路径在 $T-\delta$ 前仍未退出，给出

\(
\liminf_n\Phi(f_n)\ge T-\delta
\)。另一方面，条件 2 给出 $s<T+\delta$ 和 $i$ 使 $f_i(s)<0$；充分接近时 $f_{n,i}(s)<0$，故

\(
\limsup_n\Phi(f_n)\le T+\delta
\)。令 $\delta\downarrow0$ 即得结论。证毕。

### 4.3 单面与多面首次接触

令

\[
T_b=\Phi(\mathbf Z_b),
\qquad
A(T_b)=\{i:Z_{b,i}(T_b)=0\}.
\]

先证 $T_b<\infty$ 几乎处处成立。固定任一超边：若该块漂移非零，块和为零保证存在 $b_i<0$，相应坐标是一维负漂移 Brownian 运动且法向方差 $\Gamma_{ii}>0$，所以它几乎处处命中零；若该块漂移全为零，任选坐标得到零漂移、正方差的一维 Brownian 运动，也几乎处处命中零。网络退出时间不大于这个坐标命中时间。

在 $T_b$ 前的严格内部性来自首次接触的定义和连续路径在紧区间上的正余量。还需证明接触后的立即穿越。向量过程是可能退化但具有平稳独立增量的 Gaussian 过程，因此在有限停止时 $T_b$ 处满足强 Markov 性。条件于 $\mathcal F_{T_b}$，对每个选定的 active face $i\in A(T_b)$，其接触后法向增量为

\[
b_i s+\sqrt{\Gamma_{ii}}B_i(s),\qquad s\ge0.
\]

对任意 $h>0$，标准 Brownian 运动从零出发在 $[0,h]$ 全程非负的概率为零；加入常漂移后，Cameron–Martin 绝对连续性保持该零概率结论。因此对每个 $n\ge1$，上述法向增量在 $(0,1/n)$ 内取负值的条件概率为一，进而在接触后任意短区间内穿过该支撑超平面。

若多个面同时首次命中，$A(T_b)$ 仍是至多含 $D$ 个元素的有限集合。对其每个元素应用上一段，再对有限个概率一事件取交，得到每个被选中的 active face 都各自在任意短的接触后区间内发生法向穿越。该论证不要求不同法向独立；强 Markov 性和逐面正法向方差已经足够。于是退出映射引理的条件 2 几乎处处成立。

极限连续使 Skorokhod $J_1$ 表示上的收敛升级为紧区间一致收敛。单位步长又给出路径恒等式

\[
\Phi(\mathbf Z_N)=\frac{\tau_N^{\mathrm{net}}}{N^2}.
\]

连续映射定理因此得到

\[
\frac{\tau_N^{\mathrm{net}}}{N^2}\Rightarrow T_b.
\]

这一步覆盖单面首次接触以及任意有限个面的同时首次接触。

## 5. 统一 $O(N^2)$ 均值、指数尾和全矩

### 5.1 临界非零漂移：负坐标与截断可选停止

设 $\alpha=1$ 且 $\boldsymbol\beta\ne0$。选择 $j$ 使 $\beta_j<0$，写 $h=-\beta_j$。对充分大 $N$，

\[
d_{N,j}\le-\frac{h}{2N}.
\]

对任意内部初态和有界停止时 $\sigma_m=m\wedge\tau_N^{\mathrm{net}}$，停止坐标分解给出

\[
\mathbb E_xX_{N,j}(\sigma_m)
=x_j+d_{N,j}\mathbb E_x\sigma_m.
\]

这里 $\sigma_m\le m$，增量有界，所以可选停止不需要预设 $\tau_N^{\mathrm{net}}$ 的可积性。单位支付在零处停止，退出坐标的 overshoot 为零；即使首先耗尽的是另一坐标，第 $j$ 坐标在停止时仍非负。因此

\[
\mathbb E_x\sigma_m
\le\frac{x_j}{-d_{N,j}}
\le\frac{2c_{e(j)}}hN^2.
\]

令 $m\to\infty$ 并用单调收敛，得到全状态 $O(N^2)$ 均值界。这个论证不使用下一节的势函数。

### 5.2 临界零漂移与消失漂移：乘积势函数

本节处理 $\alpha=1,\boldsymbol\beta=0$ 以及 $\alpha>1$。定义逐边重心

\[
b_{N,e,v}=\frac{Nc_e}{k_e}
\]

和势函数

\[
V_N(x)=\sum_{e,v}(x_{e,v}-b_{N,e,v})^2.
\]

在第 $e$ 个闭单纯形上，凸函数的最大值在顶点取得，故

\[
0\le V_N(x)\le C_VN^2,
\qquad
C_V=\sum_{e\in E}c_e^2\left(1-\frac1{k_e}\right).
\]

还可取

\[
\|x-\mathbf b_N\|_1\le LN,
\qquad
L=2\sum_{e\in E}c_e\left(1-\frac1{k_e}\right).
\]

内部一步的精确增量为

\[
\mathbb E[\Delta V_N\mid X_N=x]
=\mathbb E\|\boldsymbol\xi_{N,1}\|^2
+2\langle x-\mathbf b_N,\mathbf d_N\rangle.
\]

令 $\sigma^2=\operatorname{tr}\Gamma>0$。正性来自逐面条件 $\Gamma_{ii}>0$。由协方差收敛，充分大 $N$ 时

\[
\mathbb E\|\boldsymbol\xi_{N,1}\|^2
=\operatorname{tr}\Gamma_N+\|\mathbf d_N\|^2
\ge\frac{\sigma^2}{2}.
\]

在本节两个区间中都有 $N\|\mathbf d_N\|_\infty\to0$，所以漂移扰动对全部状态一致满足

\[
\left|2\langle x-\mathbf b_N,\mathbf d_N\rangle\right|
\le2LN\|\mathbf d_N\|_\infty
\le\frac{\sigma^2}{4}
\]

对充分大 $N$ 成立。因此

\[
\mathbb E[\Delta V_N\mid X_N=x]\ge
\delta:=\frac{\sigma^2}{4}>0
\]

在所有内部状态上一致成立。对 $m\wedge\tau_N^{\mathrm{net}}$ 使用有界停止和补偿和式，

\[
\delta\,\mathbb E_x(m\wedge\tau_N^{\mathrm{net}})
\le
\mathbb E_xV_N(X_N(m\wedge\tau_N^{\mathrm{net}}))-V_N(x)
\le C_VN^2.
\]

令 $m\to\infty$ 得

\[
\sup_{x\in\mathcal S_N^\circ}
\mathbb E_x\tau_N^{\mathrm{net}}
\le\frac{C_V}{\delta}N^2.
\]

### 5.3 强 Markov 几何块、指数矩和极限传递

把 5.1 或 5.2 的常数统一写成 $A$，使所有充分大 $N$ 满足

\[
\sup_x\mathbb E_x\tau_N^{\mathrm{net}}\le AN^2.
\]

置 $L_N=\lceil2AN^2\rceil$。Markov 不等式给出任意内部初态下

\[
\Pr_x(\tau_N^{\mathrm{net}}>L_N)\le\frac12.
\]

在每个块端点条件于尚未耗尽时，过程处于某个内部状态；强 Markov 性和全状态界可再次应用。归纳得到

\[
\sup_x\Pr_x(\tau_N^{\mathrm{net}}>mL_N)\le2^{-m},
\qquad m=0,1,2,\ldots.
\]

令 $B=2A+1$，则 $L_N/N^2\le B$。对任意 $0<\lambda<\log2/B$，按上述块分解给出

\[
\sup_{N\ge N_0}\sup_x
\mathbb E_x\exp\left(\lambda\frac{\tau_N^{\mathrm{net}}}{N^2}\right)
\le
\sum_{m=0}^\infty
e^{\lambda B(m+1)}2^{-m}<\infty.
\]

因此 $\{(\tau_N^{\mathrm{net}}/N^2)^q\}$ 对每个固定 $q>0$ 一致可积。结合第 4 节的分布收敛，得到

\[
\mathbb E\left(\frac{\tau_N^{\mathrm{net}}}{N^2}\right)^q
\longrightarrow\mathbb E T_b^q.
\]

同一个指数界通过 Portmanteau 截断也给出极限 $T_b$ 的正指数矩，故右侧全部正阶矩有限。至此 T17B 和 T17C 的分布及全矩结论均闭合。

## 6. T18a：高斯块独立的充分条件

### 定理 T18a

把 $H$、$\mathbf z$、$\mathbf b$ 和 $\Gamma$ 按超边分块。若

\[
\Gamma_{ef}=0\qquad(e\ne f),
\]

则极限 Gaussian 过程的不同超边块相互独立。若 $T_e$ 是第 $e$ 个块首次离开其开单纯形的时间，则

\[
T_b=\min_{e\in E}T_e,
\qquad
\Pr(T_b>t)=\prod_{e\in E}\Pr(T_e>t).
\]

### 证明

对不同超边 $e\ne f$ 和任意 $s,t\ge0$，中心化极限块满足

\[
\operatorname{Cov}(Z_e(s),Z_f(t))
=\min(s,t)\Gamma_{ef}=0.
\]

任意有限组选定时间的块向量联合高斯；联合高斯向量的零交叉协方差蕴含独立。由有限维柱集生成路径 $\sigma$-代数，不同超边的整个连续路径块相互独立。确定性初态和漂移不改变独立性。乘积域的首次退出发生于至少一个块首次退出，故 $T_b=\min_eT_e$；各 $T_e$ 是各自路径块的可测泛函，所以

\[
\Pr(T_b>t)
=\Pr(T_e>t\ \text{for every }e)
=\prod_e\Pr(T_e>t).
\]

证毕。该结论依赖联合高斯性；一般非高斯有限步增量仅有零协方差并不足以推出块独立。

### 6.1 T18-A 临界互逆路由扰动桥接引理

设平衡基准路由律为 \(\pi_0\)，其均值为零，协方差为 \(\Gamma_0\)。取一对互为反向的路由 \(r,\bar r\)，并记其增量为

\[
\zeta=\xi(r),\qquad \xi(\bar r)=-\zeta,
\]

且基准概率满足 \(\pi_0(r)=\pi_0(\bar r)\)。固定 \(a>0\)。对 \(s\in\{-1,0,1\}\) 和使全部概率保持为正的整数 \(N\)，定义

\[
\pi_N^{(s)}
=\pi_0+\frac{sa}{N}\bigl(\mathbf e_r-\mathbf e_{\bar r}\bigr).
\]

记相应单步均值和协方差为 \(d_N^{(s)}\) 与 \(\Gamma_N^{(s)}\)。则有以下精确恒等式：

\[
d_N^{(s)}=\frac{2sa}{N}\zeta,
\qquad
N d_N^{(s)}=2sa\zeta,
\]

以及

\[
\mathbb E_{pi_N^{(s)}}[\xi\xi^{\mathsf T}]
=\mathbb E_{pi_0}[\xi\xi^{\mathsf T}],
\qquad
\Gamma_N^{(s)}
=\Gamma_0-d_N^{(s)}d_N^{(s)\mathsf T}.
\]

特别地，\(\Gamma_N^{(s)}\to\Gamma_0\)，且

\[
\|\Gamma_N^{(s)}-\Gamma_0\|
=O(N^{-2}).
\]

因此，\(s=0\) 对应 T17B 的临界零漂移极限，而 \(s=\pm1\) 对应具有相反极限漂移

\[
\beta^{(s)}=2sa\zeta
\]

但具有同一极限扩散协方差 \(\Gamma_0\) 的两个临界非零漂移实验。该构造把 T18-A 的正、零、负三种实验情形严格接到 T17B，而不是仅按有限样本点估计结果事后命名漂移。

**证明。** 概率扰动的总质量为零，故仍位于概率单纯形；充分大的 \(N\) 保证正性。利用基准均值为零以及两条互逆路由的增量分别为 \(\zeta\) 和 \(-\zeta\)，

\[
d_N^{(s)}
=\frac{sa}{N}\{\zeta-(-\zeta)\}
=\frac{2sa}{N}\zeta.
\]

另一方面，互逆增量的外积相同：

\[
\zeta\zeta^{\mathsf T}
=(-\zeta)(-\zeta)^{\mathsf T}.
\]

所以概率质量在该路由对之间移动并不改变未中心化二阶矩。由

\[
\operatorname{Cov}(\xi)
=\mathbb E[\xi\xi^{\mathsf T}]
-\mathbb E[\xi]\mathbb E[\xi]^{\mathsf T}
\]

立即得到协方差恒等式及 \(O(N^{-2})\) 收敛。证毕。

**适用边界。** 该引理不声称有限 \(N\) 的停止时间差关于 \(s\) 单调，也不声称不同拓扑具有相同误差符号。它只证明三种实验核具有声明的漂移—协方差渐近关系。

## 7. T18b：冻结两三元超边核与独立边代理诊断

冻结拓扑为 $e_1=\{0,1,2\}$、$e_2=\{2,3,4\}$，20 个有序源—宿路由等概率。核定义见 `network_model.py::two_overlapping_triads_uniform`；冻结回归断言见 `test_network_model.py:54-65`。按坐标顺序

\[
((e_1,0),(e_1,1),(e_1,2));
((e_2,2),(e_2,3),(e_2,4)),
\]

跨超边协方差块为

\[
\Gamma_{12}
=\frac1{10}
\begin{pmatrix}
2&-1&-1\\
2&-1&-1\\
-4&2&2
\end{pmatrix},
\qquad
\|\Gamma_{12}\|_{\mathrm F}=0.6.
\]

该非零块严格排除了有限增量律按两个超边块的乘积分解：若两个边块独立，其交叉协方差必须为零。因此这里得到的是一个明确的路由增量律非因子化实例。它没有给出停止时间差的统一符号。

独立边代理保留两个边块各自的边际增量律，却独立抽样两个块；它不是任何跨超边路由字母表的流量模型。冻结的 50,000 对共同随机数诊断如下。归一化均值和差均除以 $N^2$，差定义为“相关模型减独立边代理”；所有表值及 95% 配对区间来自 `results/network/network-correlated-vs-proxy.csv`，运行配置和种子来自 `results/network/network-run-metadata.json`。

| $N$ | 相关均值/$N^2$ | 代理均值/$N^2$ | 配对差 | 配对 SE | 95% CI |
|---:|---:|---:|---:|---:|---:|
| 10 | 0.9629726 | 0.9218184 | 0.0411542 | 0.00338301 | [0.0345236, 0.0477848] |
| 20 | 0.9642676 | 0.9173049 | 0.0469627 | 0.00337971 | [0.0403385, 0.0535868] |
| 40 | 0.9692817 | 0.9210577 | 0.0482240 | 0.00338347 | [0.0415925, 0.0548555] |

同一 CSV 中的 $q_{0.1}/q_{0.5}/q_{0.9}$ 归一化差分别为：$N=10$ 时 $0/0.0300000/0.0900000$，$N=20$ 时 $0.0075000/0.0400000/0.0925000$，$N=40$ 时 $0.0087500/0.0437500/0.0956250$。冻结生存曲线的 243 个网格值位于 `results/network/network-survival-curves.csv`。

这些冻结样本中的均值差均为正，只能表述为该拓扑、该需求族、该容量网格和该独立边代理下测得的正差。非零相关、不同拓扑或不同漂移都不能单独推出同一符号。

`results/network/network-phase-scaling.csv` 是有限网格描述性诊断，不进入 T17 的证明。尤其 $\alpha=0.5$ 的 $N^{1.5}$ 归一化均值在 $N=10,20,40,80$ 上为 3.06930、4.28285、6.07820、8.48087，尚未显示平台；该序列不能被当作 T17A 的数值收敛证书。这里使用 amplitude 0.01 的非零概率扰动，构造位置见 `network_phase_validation.py:392-409`。

### 7.1 T18-A 正式跨拓扑验证

正式设计使用四个三元超边构成的三类非同构拓扑：

1. overlap chain，超边交叠图度序列为 $[1,1,2,2]$；
2. common-hub star，度序列为 $[3,3,3,3]$；
3. `random_connected_triads(4, seed=7)`，度序列为 $[1,1,1,3]$。

最初试用的随机拓扑种子 `20260718` 产生度序列 $[1,1,2,2]$，与链形同构。精确锚点审计发现该问题后，旧运行被移入带 `rejected-seed20260718` 后缀的目录，并新增结构回归测试；它们不进入下述结论。

每个拓扑使用平衡、$+0.01/N$ 和 $-0.01/N$ 互逆路由概率扰动，并在 $N\in\{10,20,40,80\}$ 上比较相关路由过程与保持逐超边增量边际的独立代理。每个单元含 30,000 对独立轨迹，主估计量为

\[
\Delta_N
=\mathbb E\left[\frac{\tau_{N,\mathrm{corr}}-\tau_{N,\mathrm{proxy}}}{N^2}\right].
\]

全部 36 个主比较共用 Bonferroni 正态临界值 $3.1969502291$，形成家族置信水平至少 $95\%$ 的同时区间。正式结果位于 `results/t18-cross-topology/t18-primary-effects.csv`；相同种子完整复跑的主 CSV 和核诊断 CSV 与第一次运行逐字节一致。

| 拓扑 | 12 个单元的 $\widehat\Delta_N$ 范围 | 12 个单元平均值 | 结论边界 |
|---|---:|---:|---|
| chain | $[0.099999,0.109768]$ | $0.105799$ | 12/12 同时区间严格为正 |
| star | $[0.015720,0.030810]$ | $0.024363$ | 12/12 同时区间严格为正；效应最弱 |
| fixed-seed random branch | $[0.078968,0.090287]$ | $0.085798$ | 12/12 同时区间严格为正 |

全网格最大区间半宽为 $0.0142736$，低于预先声明的 $0.02$ 精度阈值。最弱下界出现在 `star-balanced-N80`：

\[
\widehat\Delta_{80}=0.0157195,
\qquad
\mathrm{CI}_{\mathrm{sim}}=[0.0015784,0.0298606].
\]

由于该下界接近零，又使用新种子对该单元额外模拟 100,000 对轨迹。新估计为 $0.0226529$；Bonferroni 正态、路径级 Student-$t$ 和 100 个不重叠批次均值的 Student-$t$ 区间下界分别为 $0.0148824$、$0.0148822$ 和 $0.0147960$，三者均为正。该敏感性证据位于 `results/t18-weakest-sensitivity/`。

为了验证相关过程模拟器而不只检查代码不变量，三类四超边拓扑还在 $N=2$ 的 10,000 状态空间上求得精确吸收链均值，并分别用 100,000 条 Monte Carlo 轨迹交叉验证：

| 拓扑 | 精确均值 | MC 均值 | $z$ 分数 | 最大 Poisson 残差 |
|---|---:|---:|---:|---:|
| chain | 3.69123434 | 3.68928 | -0.34837 | $2.71\times10^{-14}$ |
| star | 4.02738887 | 4.02829 | 0.14526 | $3.19\times10^{-14}$ |
| fixed-seed random branch | 3.72712371 | 3.73504 | 1.38440 | $2.78\times10^{-14}$ |

三个精确锚点均满足全状态可达边界，且 $|z|<3.29$。确定性核诊断的最大误差为：缩放漂移 $6.68\times10^{-15}$、未中心化二阶矩/协方差恒等式 $1.06\times10^{-15}$、代理边际均值 $3.82\times10^{-16}$、代理边际协方差 $1.17\times10^{-15}$。

**可写结论。** 在上述冻结的三类非同构拓扑、三种临界漂移和四个容量尺度内，独立超边代理系统性低估了相关路由过程的首次耗尽均值，且该网格结论通过同时区间、最弱单元高样本敏感性、精确锚点和完整复跑。该陈述不得改写为“任意超图、需求或漂移下独立代理总是低估”；T18b 仍是有限设计上的实验结论。

## 8. 主张—证据映射与失败降级规则

| 主张 | 证据 | 当前状态 | 若独立复核失败 |
|---|---|---|---|
| T16 有限状态吸收、谱半径和 Poisson 唯一解 | 第 2 节证明；`network_exact.py` 仅作有限实例证书 | proved internally | 将 T16 降为有限实例计算命题，停止一般定理推广 |
| T17A 相对集中与全部正阶矩 | 第 3 节的显式早晚余量和长尾块常数 | proved internally | 任一统一常数失效即降为 concentration conjecture |
| T17B/C 过程与退出时间收敛 | 第 4 节 FCLT、强 Markov 法向穿越和有限 active set | proved internally | 若多面穿越不成立，只保留过程收敛，退出时间标为 unresolved |
| T17B/C 全矩收敛 | 第 5 节两个均值机制及几何块指数矩 | proved internally | 若全状态均值界失败，只保留分布收敛 |
| T18a 生存函数因子化 | 第 6 节联合高斯零交叉协方差证明 | proved internally | 删除因子化结论，只保留协方差描述 |
| 冻结增量律非因子化 | 第 7 节非零跨块协方差；`test_network_model.py:54-65` | proved for frozen kernel | 若冻结核复算失败，撤回该实例 |
| T18-A 跨拓扑停止时间差 | `results/t18-cross-topology/` 两次完整运行、同时区间、最弱单元敏感性和 $N=2$ 精确锚点 | formal finite-grid numerical result | 若哈希、区间重算、结构非同构或精确锚点失败，撤回相应数值结论，不影响 T18a |

## 9. 假设、缺失输入与文献边界

- 本包没有发现需要以占位符替代的数学步骤；尚缺的是独立概率论研究者逐项签署 `14_correlated_network_external_review_packet.md`。
- T16 的可达性是显式假设，不由 $\Gamma_{ii}>0$ 推出；冻结代码只认证输入的有限网格。
- T17 要求固定有限超图、固定维数、外生 i.i.d. 路由、单位支付和状态无关概率。余额感知路由、失败后重试、随机金额、费用和增长网络不在结论内。
- T18-A 已完成的全正结果只覆盖冻结的 36 单元；它没有证明任意拓扑、容量、需求或状态依赖路由下的统一符号。
- Podiatchev–Orda–Rottenstreich 已覆盖独立 PCN 通道停止时间基线；Corcoran–Lewis 已给出超图 PCN 和路径语义；COALESCE 已给出跨超边原子结算语义；Patel–Carron–Bullo 的乘积链与有限吸收工具属于标准方法。逐条边界见 `sources/correlated_network_prior_art_audit_2026-07-17.md`。
- Barnett（1964）正文未在本任务下载或据未读正文作排除式判断。
- 在外部评审包全部签字前，本文档只可称内部证明工作稿，publication readiness 为 false。
