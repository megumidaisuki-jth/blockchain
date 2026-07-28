# 固定强漂移退出时间证明包

更新日期：2026-07-18  
对应登记：T10–T11  
状态：A（内部工作稿证明闭合，待独立概率论复核）

## 1. 证明合同

本文件只处理固定参与者数 \(k\ge2\)、固定中心偏置
\(p\in[0,2]\setminus\{1\}\) 和正整数均分初值
\(X_i(0)=N\in\mathbb N\) 的中心偏置模型。
停止时间为

\[
\tau_N=\inf\{n\ge0:\min_{0\le i\le k-1}X_i(n)=0\}.
\]

每步均匀选择一个无序节点对；若选中中心—外围对 \(\{0,r\}\)，则以
\(p/2\) 的条件概率把一个单位从 \(r\) 转给 \(0\)，以
\((2-p)/2\) 的条件概率反向转移；外围—外围对的两个方向等概率。

本证明包的目标比原有“均值一阶等价”更强：

1. 给出相对误差偏离的一致指数概率界；
2. 给出 \(\tau_N/N\) 的统一指数矩；
3. 推出任意固定正阶矩收敛，包括均值一阶式与相对方差消失。

正漂移侧的 \(N^{-1/2}\) 竞争修正仍不在本 T10–T11 一阶证明合同内；
它已在
[17 T12 证明包](17_t12_positive_competition_proof_and_validation.md)
用局部 CLT、最大不等式、严格穿越、两段尾一致可积性和 Gaussian 投影
另行内部闭合，状态为 A — internally closed, external review unsigned。

## 2. 漂移、主导坐标与时间尺度

一步坐标漂移为

\[
d_0=\frac{2(p-1)}{k},\qquad
d_r=-\frac{2(p-1)}{k(k-1)},\quad 1\le r\le k-1.
\]

令 \(D\) 为具有负漂移的坐标集合，并令 \(v\) 为这些坐标共同的负漂移
绝对值：

\[
(D,v)=
\begin{cases}
(\{0\},\,2(1-p)/k), & 0\le p<1,\\[3pt]
(\{1,\ldots,k-1\},\,2(p-1)/[k(k-1)]), & 1<p\le2.
\end{cases}
\]

主时间尺度为

\[
t_N^*=\frac{N}{v}
=
\begin{cases}
\dfrac{kN}{2(1-p)}, & p<1,\\[6pt]
\dfrac{k(k-1)N}{2(p-1)}, & p>1.
\end{cases}
\]

负漂移侧只有中心节点竞争；正漂移侧有 \(k-1\) 个外围节点竞争。二者
一阶尺度不同，但下面的集中论证可以统一处理。

## 3. 自由延拓耦合

令 \(\xi(1),\xi(2),\ldots\) 为由上述选对—定向机制产生的独立同分布
增量，不因余额是否到达边界而改变。定义整个整数格上的自由随机游走

\[
Z_i(n)=N+\sum_{\ell=1}^{n}\xi_i(\ell).
\]

原吸收过程与自由过程使用同一串增量，直至首次有坐标到达零。由于每步
坐标变化只可能为 \(-1,0,1\)，不会跨越零而不命中零。因此若

\[
T_i=\inf\{n\ge0:Z_i(n)=0\},
\]

则逐路径有

\[
\tau_N=\min_{0\le i\le k-1}T_i.
\]

自由延拓只用于在确定时间上应用鞅不等式，不改变停止时间的分布。

对每个坐标定义

\[
M_i(n)=Z_i(n)-N-d_i n.
\]

这是关于自然过滤的鞅，并且

\[
|\Delta M_i(n)|=|\xi_i(n)-d_i|\le2.
\]

因此一侧最大型 Azuma–Hoeffding 不等式给出

\[
\Pr\!\left(\min_{0\le s\le n}M_i(s)\le-a\right)
\le \exp\!\left(-\frac{a^2}{8n}\right),
\]

固定时刻的上尾同样满足

\[
\Pr(M_i(n)\ge a)\le \exp\!\left(-\frac{a^2}{8n}\right).
\]

这里采用的常数并非最优，但对指数阶和所有后续推论充分。

## 4. 主定理

### 定理 SD

固定 \(k\ge2\) 和 \(p\in[0,2]\setminus\{1\}\)。对任意
\(\varepsilon\in(0,1)\)，存在只依赖于 \(k,p,\varepsilon\) 的
\(c>0\) 与 \(N_0<\infty\)，使得对所有 \(N\ge N_0\)，

\[
\Pr\!\left(\left|\frac{\tau_N}{t_N^*}-1\right|>\varepsilon\right)
\le (k+1)e^{-cN}.
\]

此外存在 \(\lambda_0=\lambda_0(k,p)>0\)，使

\[
\sup_{N\ge1}\mathbb E
\exp\!\left(\lambda_0\frac{\tau_N}{N}\right)<\infty.
\]

因而对每个固定 \(q>0\)，

\[
\mathbb E\left(\frac{\tau_N}{t_N^*}\right)^q\longrightarrow1.
\]

特别地，

\[
\mathbb E\tau_N\sim t_N^*,\qquad
\frac{\operatorname{Var}(\tau_N)}{(t_N^*)^2}\longrightarrow0.
\]

### 4.1 过早退出概率

令

\[
n_-=\left\lfloor(1-\varepsilon)t_N^*\right\rfloor.
\]

对负漂移坐标 \(i\in D\) 和任意 \(s\le n_-\)，有

\[
N+d_i s=N-vs\ge\varepsilon N.
\]

对正漂移坐标，确定性均值不小于 \(N\)。若 \(\tau_N\le n_-\)，则某个
坐标 \(i\) 在某个 \(s\le n_-\) 到达零，故

\[
M_i(s)=-N-d_i s\le-\varepsilon N.
\]

对全部 \(k\) 个坐标作并集界并应用最大型不等式，

\[
\Pr(\tau_N\le n_-)
\le k\exp\!\left(-\frac{\varepsilon^2N^2}{8n_-}\right)
\le k\exp\!\left(-\frac{\varepsilon^2v}{8(1-\varepsilon)}N\right).
\]

整数取整只会使第一步指数更大；当 \(n_-=0\) 时，初始余额均为正，
事件 \(\{\tau_N\le0\}\) 为空。

### 4.2 过晚退出概率

令

\[
n_+=\left\lceil(1+\varepsilon)t_N^*\right\rceil
\]

并固定任意一个负漂移坐标 \(j\in D\)。若 \(\tau_N>n_+\)，则该坐标在
\(n_+\) 时仍为正，因此

\[
M_j(n_+)=Z_j(n_+)-N+vn_+>vn_+-N\ge\varepsilon N.
\]

固定时刻 Azuma–Hoeffding 给出

\[
\Pr(\tau_N>n_+)
\le\exp\!\left(-\frac{\varepsilon^2N^2}{8n_+}\right).
\]

对充分大的 \(N\)，
\(n_+\le2(1+\varepsilon)N/v\)，从而

\[
\Pr(\tau_N>n_+)
\le\exp\!\left(-\frac{\varepsilon^2v}{16(1+\varepsilon)}N\right).
\]

联合早尾和晚尾即得定理中的相对指数集中。可取一个保守的共同常数

\[
c=\frac{\varepsilon^2v}{16(1+\varepsilon)}
\]

并把有限个小 \(N\) 吸收到 \(N_0\) 中。

## 5. 统一指数矩

仍固定一个负漂移坐标 \(j\in D\)。当

\[
n\ge\left\lceil\frac{2N}{v}\right\rceil
\]

时，事件 \(\{\tau_N>n\}\) 蕴含 \(Z_j(n)>0\)，于是

\[
M_j(n)>vn-N\ge\frac{vn}{2}.
\]

故

\[
\Pr(\tau_N>n)
\le\exp\!\left(-\frac{v^2n}{32}\right).
\]

对整数值非负随机变量和 \(z>1\)，尾和恒等式为

\[
\mathbb E z^{\tau_N}
=1+(z-1)\sum_{n\ge0}z^n\Pr(\tau_N>n).
\]

取

\[
\lambda_0=\frac{v^2}{64},\qquad z_N=e^{\lambda_0/N}.
\]

把尾和在 \(\lceil2N/v\rceil\) 处分开。前半段被
\(z_N^{\,2N/v+2}\) 一致控制；后半段中

\[
z_N^n\Pr(\tau_N>n)
\le\exp\!\left[-\left(\frac{v^2}{32}
-\frac{\lambda_0}{N}\right)n\right]
\le e^{-v^2n/64}.
\]

后者是与 \(N\) 无关的几何级数。因此

\[
\sup_{N\ge1}\mathbb E
\exp\!\left(\lambda_0\frac{\tau_N}{N}\right)<\infty.
\]

这一步同时排除了只凭概率收敛却无法交换期望的缺口。

## 6. 全部固定正阶矩

指数矩一致有界蕴含对任意固定 \(q>0\)，随机变量族

\[
\left\{\left(\frac{\tau_N}{N}\right)^q:N\ge1\right\}
\]

一致可积。第 4 节已经证明
\(\tau_N/t_N^*\to1\) 依概率，而 \(t_N^*/N=1/v\) 为常数，故

\[
\mathbb E\left(\frac{\tau_N}{t_N^*}\right)^q\to1.
\]

取 \(q=1\) 得均值一阶等价；取 \(q=1,2\) 并使用
\(\operatorname{Var}(Y)=\mathbb EY^2-(\mathbb EY)^2\)，得到相对方差
趋于零。

## 7. 有限容量上界交叉核查

对任意负漂移坐标 \(j\in D\)，停止鞅满足

\[
\mathbb E X_j(m\wedge\tau_N)
=N-v\,\mathbb E(m\wedge\tau_N).
\]

左侧非负，因此

\[
\mathbb E(m\wedge\tau_N)\le\frac{N}{v}.
\]

令 \(m\to\infty\) 并用单调收敛，

\[
\mathbb E\tau_N\le\frac{N}{v}=t_N^*.
\]

该有限 \(N\) 上界与渐近结论相容，但不是矩收敛证明的替代；第 5 节的
统一指数矩才负责闭合期望与高阶矩交换。

## 8. 数值一致性与有限样本解释

现有每点 10,000 次模拟给出下列 \(\mathbb E\tau_N/t_N^*\) 比值：

| \(k\) | \(p\) | \(N=20\) | \(40\) | \(80\) | \(160\) | \(320\) |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 0.5 | 0.998 | 0.999 | 1.000 | 0.999 | 1.000 |
| 5 | 0.5 | 1.003 | 1.003 | 1.001 | 1.000 | 1.000 |
| 3 | 1.5 | 0.710 | 0.790 | 0.847 | 0.890 | 0.923 |
| 5 | 1.5 | 0.453 | 0.574 | 0.677 | 0.764 | 0.829 |

负漂移侧只有一个主导坐标，有限样本很快接近一阶式；正漂移侧取
\(k-1\) 个相关外围首次到达时间的最小值，出现明显的负二阶修正，且
\(k\) 越大收敛越慢。这不反驳一阶定理：表中比值随 \(N\) 增大向 1
移动。该表只描述有限样本现象，不证明二阶极限。严格的固定
\(k\ge3,p\in(1,2]\) 二阶定理及其期望余项现已在
[17 T12 证明包](17_t12_positive_competition_proof_and_validation.md)
通过局部 CLT、最大界和统一可积性闭合；其外部概率论签核仍未完成。

原始数据：
[drift-strong-asymptotic.csv](../../../results/drift-strong-asymptotic.csv)。

## 9. 方法来源、新颖性边界与适用边界

- 鞅有界差分集中方法应引用 Azuma（1967），不能作为本项目新方法。
- 本包的可投稿内容是该方法对中心偏置成对转账核的完整实例化、正负漂移
  不对称尺度，以及与弱漂移 \(N^2\) 区间共同形成的模型特定相图。
- 结论要求 \(k\) 与 \(p\ne1\) 固定。它不覆盖 \(p\to1\) 的联合极限；
  \(p_N=1+\eta/N\) 应使用 07 弱漂移证明包；多项式消失漂移的联合极限
  见 [11 相图证明包](11_polynomial_drift_phase_diagram_proof_package.md)。
- \(p=0,2\) 的退化方向概率仍被证明覆盖；只需存在上面明确的负漂移
  坐标。\(k=2\) 退化为标准有偏赌徒破产的一阶结论。
- 停止量仍是单个多方通道的首次余额到零，不自动等于永久关闭、首次
  路由失败或整个超图网络失效。

Azuma 原始来源：
[Weighted Sums of Certain Dependent Random Variables](https://doi.org/10.2748/tmj/1178243286)。

## 10. 外部复核清单

独立复核者应逐项签核：

1. 自由延拓与原吸收过程直至 \(\tau_N\) 的逐路径一致性；
2. \(\tau_N=\min_iT_i\) 是否依赖单位步长且无越界；
3. \(|\Delta M_i|\le2\) 与最大型 Azuma 常数；
4. 过早退出并集界是否覆盖正漂移坐标的异常早停；
5. 过晚退出只选一个负漂移坐标是否充分；
6. 整数取整对 \(n_-\)、\(n_+\) 的处理；
7. 尾和恒等式及统一指数矩的几何级数常数；
8. 从依概率收敛和指数矩到任意实数 \(q>0\) 矩收敛的统一可积性；
9. 可选停止上界使用截断停止而非未经验证的无界停止；
10. \(k=2\)、\(p=0\)、\(p=2\) 和 \(p\to1\) 的边界说明；
11. 定理没有误含 \(k=k_N\) 或 \(p=p_N\) 的额外联合极限；
12. T12 二阶定理与本 T10–T11 一阶证明合同保持分离，并核对 17 证明包的
    A-internal / external-unsigned 状态没有被误写成外部确认。

任一关键项未通过时，T10–T11 应降为 B 或 C；在独立签核前，论文只能称
其为“内部闭合工作稿”，不能称为经同行评审定理。
