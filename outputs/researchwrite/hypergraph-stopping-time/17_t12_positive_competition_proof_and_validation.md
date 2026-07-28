# T12 正漂移竞争二阶极限：证明与有限网格验证

更新日期：2026-07-18  
证明状态：A — 内部工作稿闭合，外部概率论签核未完成

## 1. 证明合同、记号与主张边界

固定任意整数 \(k\ge3\) 和任意实数 \(p\in(1,2]\)。以下所有极限均只让
整数 \(N\to\infty\)，不让 \(k\) 或 \(p\) 随 \(N\) 改变。记

\[
\delta=p-1,\qquad m=k-1,\qquad
v=\frac{2\delta}{k(k-1)},\qquad
t_N^*=\frac{N}{v}.
\]

参与者 0 是中心，参与者 \(1,\ldots,m\) 是外围。每一步均匀选择一个
无序节点对。若选择 \(\{0,r\}\)，则以条件概率 \(p/2\) 从 \(r\) 向
0 转移一个单位，以条件概率 \((2-p)/2\) 从 0 向 \(r\) 转移一个单位；
外围—外围对的两个方向各以条件概率 \(1/2\) 发生。初始余额均为
\(N\)，停止时间为

\[
\tau_N=\inf\{n\in\mathbb Z_{\ge0}:\min_{0\le i\le m}X_i(n)=0\}.
\]

令 \(\xi(n)=(\xi_0(n),\ldots,\xi_m(n))\) 是不因吸收而改变的一列
i.i.d. 自由增量，并令

\[
Z_i(n)=N+\sum_{\ell=1}^n\xi_i(\ell),\qquad n\in\mathbb Z_{\ge0}.
\]

每个坐标的一步变化属于 \(\{-1,0,1\}\)，所以自由过程不能从正整数
越过 0 而不命中 0。原吸收过程与自由过程使用同一列增量时，逐路径有

\[
\tau_N=\min_{0\le i\le m}T_{N,i},\qquad
T_{N,i}=\inf\{n\ge0:Z_i(n)=0\}.
\]

本文件证明固定 \((k,p)\) 下的 \(\sqrt N\) 二阶极限和全部固定正阶绝对
矩收敛。它不证明 \(p=p_N\to1\)、\(k=k_N\to\infty\)、多超边网络、
余额依赖路由或一般相关路由下的同一公式。第 9 节的模拟只检查实现和
有限网格对齐，不参与第 3–8 节的定理证明。

## 2. 一步增量、漂移与协方差

一个给定无序对被选中的概率为 \(2/[k(k-1)]\)。对任意外围坐标
\(r\in\{1,\ldots,m\}\)，中心—外围事件给出

\[
\mathbb E\xi_r(1)
=\frac{2}{k(k-1)}\left(-\frac p2+\frac{2-p}{2}\right)
=-\frac{2(p-1)}{k(k-1)}=-v.
\]

外围—外围事件的两个方向抵消其均值。坐标 \(r\) 在且仅在所选对含
\(r\) 时具有非零增量，因此

\[
\mathbb E\xi_r(1)^2=(k-1)\frac{2}{k(k-1)}=\frac2k.
\]

若 \(r\ne s\)，乘积 \(\xi_r(1)\xi_s(1)\) 只在选择外围对
\(\{r,s\}\) 时非零，并且两个转移方向下都等于 \(-1\)。所以

\[
\mathbb E[\xi_r(1)\xi_s(1)]= -\frac{2}{k(k-1)}.
\]

令外围中心化增量和为

\[
M_r(n)=\sum_{\ell=1}^n(\xi_r(\ell)+v),\qquad
Z_r(n)=N-vn+M_r(n),qquad 1\le r\le m.
\]

一步协方差矩阵 \(B=\operatorname{Cov}(\xi_1(1),\ldots,\xi_m(1))\)
因而满足

\[
B_{rr}=\gamma=\frac2k-v^2,
\qquad
B_{rs}=c=-\frac{2}{k(k-1)}-v^2\quad(r\ne s),
\]

以及

\[
\gamma-c=\frac{2}{k-1}.
\]

中心漂移为

\[
u=\mathbb E\xi_0(1)=\frac{2(p-1)}k=(k-1)v>0.
\]

所有中心化坐标增量的绝对值都小于 2；下文统一用上界 2。

## 3. 主定理

### 定理 T12

对每一个固定整数 \(k\ge3\) 和每一个固定实数 \(p\in(1,2]\)，令
\(v,t_N^*,B\) 如第 1–2 节所定义。令

\[
G=(G_1,\ldots,G_m)\sim\mathcal N(0,B/v),
\qquad
H=\frac1v\min_{1\le r\le m}G_r.
\]

则当整数 \(N\to\infty\) 时，

\[
\frac{\tau_N-t_N^*}{\sqrt N}\Rightarrow H.
\]

而且，对每一个固定实数 \(q>0\)，

\[
\mathbb E\left|\frac{\tau_N-t_N^*}{\sqrt N}\right|^q
\longrightarrow \mathbb E|H|^q.
\]

若 \(Z_1^{\circ},\ldots,Z_m^{\circ}\) 是独立标准正态变量，并记

\[
\kappa_m=\mathbb E\max_{1\le r\le m}Z_r^{\circ},
\]

则

\[
\mathbb EH=-\frac{\kappa_m}{v}\sqrt{\frac{k}{p-1}}.
\]

因此有两个等价的均值展开：

\[
\boxed{
\mathbb E\tau_N
=t_N^*-\frac{\kappa_{k-1}}{v}
\sqrt{\frac{k}{p-1}}\sqrt N+o(\sqrt N)
}
\]

和

\[
\boxed{
\frac{\mathbb E\tau_N}{t_N^*}
=1-\kappa_{k-1}\sqrt{\frac{k}{(p-1)N}}+o(N^{-1/2}).
}
\]

## 4. 确定时刻 CLT 与紧集局部过程极限

### 4.1 确定时刻多元 CLT 和所有取整项

令

\[
n_N=\lfloor t_N^*\rfloor.
\]

因为 \(n_N=N/v+O(1)\)，所以

\[
\frac{n_N}{N}=\frac1v+O(N^{-1}).
\]

对任意固定向量 \(a\in\mathbb R^m\)，一维 i.i.d. CLT 给出

\[
\frac{a^\top M(n_N)}{\sqrt N}
=\sqrt{\frac{n_N}{N}}
\frac{a^\top M(n_N)}{\sqrt{n_N}}
\Rightarrow
\mathcal N\left(0,\frac{a^\top Ba}{v}\right).
\]

对所有固定 \(a\) 应用 Cramér–Wold 定理，得到确定时刻的固定维多元
CLT：

\[
\frac{M(n_N)}{\sqrt N}\Rightarrow G,
\qquad G\sim\mathcal N(0,B/v).
\]

这里没有使用随 \(N\) 增长的维数，也没有使用强近似。

### 4.2 长度 \(O(\sqrt N)\) 的局部鞅增量

固定任意实数 \(0\le C<\infty\) 和 \(\varepsilon>0\)，并令

\[
L_N=\lceil C\sqrt N\rceil+2.
\]

下文局部位移 \(j\) 始终取整数，即 \(j\in\mathbb Z\)。因为
\(L_N=O(\sqrt N)\) 而 \(n_N=N/v+O(1)\)，对每个固定 \(C\)，充分大的
\(N\) 都满足 \(L_N\le n_N\)，所以所有向后时刻 \(n_N+j\) 均非负。

对一个外围坐标，向前的中心化增量和是增量绝对值至多 2 的鞅。
最大型 Azuma–Hoeffding 不等式及其对负鞅的应用给出

\[
\Pr\left(\max_{\substack{j\in\mathbb Z\\0\le j\le L_N}}
|M_r(n_N+j)-M_r(n_N)|>\varepsilon\sqrt N\right)
\le2\exp\left(-\frac{\varepsilon^2N}{8L_N}\right).
\]

向后差值是把 \(n_N-L_N+1,\ldots,n_N\) 的独立中心化增量反向排列
后的部分和；对该反向过滤再次应用同一最大不等式。对两个方向和全部
\(m\) 个外围坐标作并集界，得到

\[
\Pr\left(
\max_{\substack{j\in\mathbb Z\\|j|\le L_N}}
\|M(n_N+j)-M(n_N)\|_\infty>\varepsilon\sqrt N
\right)
\le4m\exp\left(-\frac{\varepsilon^2N}{8L_N}\right).
\]

由于 \(L_N\le(C+2)\sqrt N\)，对每个固定 \((C,\varepsilon,k)\)，存在
\(N_0(C,\varepsilon,k)<\infty\)，使所有 \(N\ge N_0\) 满足

\[
\Pr\left(
\max_{\substack{j\in\mathbb Z\\|j|\le C\sqrt N+2}}
\|M(n_N+j)-M(n_N)\|_\infty>\varepsilon\sqrt N
\right)
\le2k\exp\left[-\frac{\varepsilon^2}{16(C+2)}\sqrt N\right].
\]

这就是局部新增噪声在 \(\sqrt N\) 尺度下消失的定量界。

### 4.3 紧集上一致局部线性化

固定任意实数 \(0\le C<\infty\)。对 \(s\in[-C,C]\) 定义

\[
\ell_N(s)=\lfloor t_N^*+s\sqrt N\rfloor,
\qquad
Y_{N,r}(s)=\frac{Z_r(\ell_N(s))}{\sqrt N}.
\]

对充分大的 \(N\)，所有 \(\ell_N(s)\) 都非负。取整满足

\[
\ell_N(s)-n_N=s\sqrt N+O(1)
\]

且该 \(O(1)\) 在 \([-C,C]\) 上一致；更具体地，其绝对误差小于 2。
确定性余额项满足

\[
\frac{N-v\ell_N(s)}{\sqrt N}
=-vs+\rho_N(s),
\qquad
0\le\rho_N(s)<\frac v{\sqrt N}.
\]

所以第 4.2 节的最大界推出

\[
\sup_{|s|\le C}
\left\|Y_N(s)-\frac{M(n_N)}{\sqrt N}+vs\mathbf1\right\|_\infty
\xrightarrow{\mathbb P}0.
\]

把格点间余额作线性插值得到连续过程 \(\widetilde Y_N\)。一步坐标变化
至多 1，因此 \(Y_N\) 与 \(\widetilde Y_N\) 的紧集一致距离至多
\(1/\sqrt N\)。结合确定时刻多元 CLT 和 Slutsky 定理，对每个固定
实数 \(0\le C<\infty\)，

\[
\widetilde Y_N(\cdot)\Rightarrow G-v(\cdot)\mathbf1
\quad\text{于 }C([-C,C],\mathbb R^m).
\]

该结论是“确定时刻 CLT 加局部鞅最大界”，不是路径强耦合或强近似。

## 5. 退出映射、竞争者同时穿越与中心坐标

### 5.1 外围退出时间的 \(\sqrt N\) 紧性

令

\[
T_{N,\mathrm P}=\min_{1\le r\le m}T_{N,r},
\qquad
S_{N,\mathrm P}=\frac{T_{N,\mathrm P}-t_N^*}{\sqrt N}.
\]

固定任意实数 \(1\le C<\infty\)。若某外围坐标在
\(n_- =\lfloor t_N^*-C\sqrt N\rfloor\ge0\) 前到达 0，则在某个
\(s\le n_-\) 有

\[
M_r(s)=-N+vs\le-vC\sqrt N.
\]

最大型 Azuma–Hoeffding 与 \(n_-\le N/v\) 给出

\[
\Pr(S_{N,\mathrm P}<-C)
\le m\exp\left(-\frac{v^3C^2}{8}\right).
\]

若 \(n_-<0\)，左侧事件为空。对晚尾，令
\(n_+=\lfloor t_N^*+C\sqrt N\rfloor\)。事件
\(S_{N,\mathrm P}>C\) 蕴含任意指定外围坐标在 \(n_+\) 时仍为正，故

\[
M_r(n_+)>vn_+-N\ge vC\sqrt N-v.
\]

对固定 \(C\)，当 \(N\) 足够大时，右侧至少为
\(vC\sqrt N/2\)，且 \(n_+\le2N/v\)。固定时刻 Azuma–Hoeffding
于是给出一个只依赖 \(v\) 的常数 \(b>0\)，使

\[
\limsup_{N\to\infty}\Pr(S_{N,\mathrm P}>C)\le e^{-bC^2}.
\]

先令 \(N\to\infty\)，再令 \(C\to\infty\)，两侧界证明
\(\{S_{N,\mathrm P}\}\) 紧。

### 5.2 严格穿越连续性不要求竞争者独立

对任意确定向量 \(a\in\mathbb R^m\)，令

\[
g_r^a(s)=a_r-vs,
\qquad
\theta(a)=\frac1v\min_r a_r.
\]

每条坐标路径 \(g_r^a\) 都在唯一时刻 \(a_r/v\) 严格向下穿越 0。
更重要的是，控制首次外围退出的标量下包络为

\[
\min_r g_r^a(s)=\min_r a_r-vs.
\]

对每个 \(\epsilon>0\)，它满足

\[
\min_r g_r^a(\theta(a)-\epsilon)=v\epsilon>0,
\qquad
\min_r g_r^a(\theta(a)+\epsilon)=-v\epsilon<0.
\]

取 \(C>|\theta(a)|+\epsilon\)。在整个
\([-C,\theta(a)-\epsilon]\) 上，极限下包络至少为 \(v\epsilon\)；在
\(\theta(a)+\epsilon\) 处则等于 \(-v\epsilon\)。因此，只要扰动路径
在 \([-C,C]\) 上的一致误差小于 \(v\epsilon/2\)，且其全局首次退出
没有发生在左端点 \(-C\) 之前，它在
\([-C,\theta(a)-\epsilon]\) 上保持正值，并在
\(\theta(a)+\epsilon\) 前发生穿越。其首次穿越遂位于
\((\theta(a)-\epsilon,\theta(a)+\epsilon)\)。这一左端点条件不可省略，
因为自由延拓坐标命中 0 后可能重新进入正半轴；第 5.1 节的紧性正是用来
把这类窗口前首次退出的概率送到 0。

若多个坐标的 \(a_r\) 相同，它们可以同时到达 0，但下包络仍以上述斜率
\(-v\) 严格穿越；退出映射连续性不使用坐标独立性，也不需要先排除
并列竞争者。把这一确定性 \(\epsilon\)-夹逼应用于第 4.3 节的每个紧窗，
并用第 5.1 节的紧性排除左右窗口外首次穿越，得到

\[
S_{N,\mathrm P}\Rightarrow
\frac1v\min_{1\le r\le m}G_r=H.
\]

线性插值不会改变首次到零时刻：整数余额的一步下降至多 1，因而首次
达到非正值的格点就是首次达到 0 的格点。

### 5.3 中心坐标在局部窗口内指数可忽略

令

\[
M_0(n)=Z_0(n)-N-un,
\qquad u=(k-1)v>0.
\]

固定任意实数 \(0\le C<\infty\)，并令
\(n_C=\lceil t_N^*+C\sqrt N\rceil\)。若中心在 \(n_C\) 前耗尽，
则某个 \(s\le n_C\) 满足

\[
M_0(s)=-N-us\le-N.
\]

对充分大的 \(N\)，\(n_C\le2N/v\)。最大型 Azuma–Hoeffding 因而给出

\[
\Pr(T_{N,0}\le t_N^*+C\sqrt N)
\le\exp\left(-\frac{N^2}{8n_C}\right)
\le\exp\left(-\frac{vN}{16}\right).
\]

加入有限多个小 \(N\) 后，可写成存在
\(C_1=C_1(k,p,C)<\infty\) 和 \(c_1=c_1(k,p,C)>0\)，使

\[
\Pr(T_{N,0}\le t_N^*+C\sqrt N)\le C_1e^{-c_1N}
\quad\text{对所有 }N\ge1.
\]

中心的确定性余额在整个窗口内至少为 \(N\)，即保持 \(N\) 量级。

### 5.4 完整停止时间的分布极限

在事件
\(\{|T_{N,\mathrm P}-t_N^*|\le C\sqrt N\}\) 上，完整停止时间与外围
停止时间不相同只可能因为中心不迟于 \(t_N^*+C\sqrt N\) 耗尽。因此

\[
\Pr(\tau_N\ne T_{N,\mathrm P})
\le
\Pr(|S_{N,\mathrm P}|>C)
+\Pr(T_{N,0}\le t_N^*+C\sqrt N).
\]

先取 \(N\to\infty\)，再取 \(C\to\infty\)，第 5.1 和 5.3 节使右侧
趋于 0。故

\[
\frac{\tau_N-t_N^*}{\sqrt N}\Rightarrow H.
\]

## 6. 两段尾界与每个固定正阶的一致可积性

记

\[
W_N=\frac{\tau_N-t_N^*}{\sqrt N}.
\]

本节给出独立于 \(N\) 的可积尾包络；这一步负责从分布收敛交换期望和
任意固定正阶绝对矩。

### 6.1 Gaussian 窗口：\(1\le x\le2\sqrt N/v\)

先看早尾。若 \(t_N^*-x\sqrt N>0\)，外围坐标过早耗尽的第 5.1 节
计算逐字给出

\[
\Pr(T_{N,\mathrm P}<t_N^*-x\sqrt N)
\le m e^{-v^3x^2/8}.
\]

中心在该时刻前耗尽要求大小至少为 \(N\) 的负鞅偏差，故

\[
\Pr(T_{N,0}<t_N^*-x\sqrt N)\le e^{-vN/8}.
\]

早尾事件非空时 \(x<\sqrt N/v\)，所以
\(N>v^2x^2\)，上式至多为 \(e^{-v^3x^2/8}\)。当
\(x\ge\sqrt N/v\) 时，\(W_N<-x\) 因 \(\tau_N\ge0\) 而不可能发生。

再看晚尾。令 \(n_x=\lfloor t_N^*+x\sqrt N\rfloor\)。事件
\(W_N>x\) 蕴含任意指定外围坐标在 \(n_x\) 时为正，并且

\[
M_r(n_x)>vn_x-N\ge vx\sqrt N-v.
\]

当 \(N\ge4\) 且 \(x\ge1\) 时，右侧至少为 \(vx\sqrt N/2\)。在
\(x\le2\sqrt N/v\) 时又有 \(n_x\le3N/v\)，所以固定时刻
Azuma–Hoeffding 给出

\[
\Pr(W_N>x)\le e^{-v^3x^2/96}.
\]

合并早晚两侧，并令 \(b=v^3/96\)，对所有 \(N\ge4\) 和
\(1\le x\le2\sqrt N/v\) 有

\[
\Pr(|W_N|>x)\le(m+2)e^{-bx^2}.
\]

### 6.2 远晚尾：\(x\ge2\sqrt N/v\)

该范围的早尾为空。此时

\[
n_x=\lfloor t_N^*+x\sqrt N\rfloor
\ge\left\lceil\frac{2N}{v}\right\rceil,
\qquad n_x\ge x\sqrt N,
\]

其中使用了 \(v\le1/3\)，故 \(N/v\ge3\)。T11 已证明的几何晚尾为

\[
\Pr(\tau_N>n)\le e^{-v^2n/32}
\quad\text{对所有 }n\ge\lceil2N/v\rceil.
\]

于是

\[
\Pr(|W_N|>x)=\Pr(W_N>x)
\le e^{-v^2x\sqrt N/32}
\le e^{-v^2x/32}.
\]

这一步只调用 T11 的几何尾，不调用强近似。

### 6.3 尾积分、统一可积性和矩收敛

第 6.1–6.2 节说明存在只依赖固定 \((k,p)\) 的
\(A<\infty,b_0>0\)，使对全部 \(N\ge4\) 和 \(x\ge1\)，

\[
\Pr(|W_N|>x)\le Ae^{-b_0x}.
\]

有限集合 \(N=1,2,3\) 中，每个停止时间也由 T11 几何尾具有全部正阶
矩；减小 \(b_0\) 并增大 \(A\) 后，同一形式可覆盖所有 \(N\ge1\)。

对任意固定 \(q>0\)，非负随机变量的尾积分恒等式给出

\[
\mathbb E|W_N|^q
=q\int_0^\infty x^{q-1}\Pr(|W_N|>x)\,dx.
\]

更具体地，对任意 \(K\ge1\)，

\[
\begin{aligned}
\mathbb E\bigl[|W_N|^q;|W_N|>K\bigr]
&=K^q\Pr(|W_N|>K)
+q\int_K^\infty x^{q-1}\Pr(|W_N|>x)\,dx\\
&\le A K^qe^{-b_0K}
+qA\int_K^\infty x^{q-1}e^{-b_0x}\,dx.
\end{aligned}
\]

右侧与 \(N\) 无关并在 \(K\to\infty\) 时趋于 0。因此，对每一个固定
\(q>0\)，族 \(\{|W_N|^q:N\ge1\}\) 一致可积。结合第 5.4 节的分布
收敛和连续函数 \(x\mapsto|x|^q\)，得到

\[
\mathbb E|W_N|^q\longrightarrow\mathbb E|H|^q.
\]

特别地，\(\{W_N\}\) 一致可积，所以
\(\mathbb EW_N\to\mathbb EH\)。

## 7. 不假设外围独立的 Gaussian 极值投影

令 \(\mathbf1\in\mathbb R^m\) 为全 1 向量，并令

\[
P=I_m-\frac1m\mathbf1\mathbf1^\top,
\qquad
\bar G=\frac1m\mathbf1^\top G.
\]

交换对称矩阵可写成

\[
B=(\gamma-c)I_m+c\mathbf1\mathbf1^\top.
\]

因为 \(P\mathbf1=0\)，

\[
\operatorname{Cov}(PG)
=P\frac BvP
=\frac{\gamma-c}{v}P.
\]

若 \(Z^\circ=(Z_1^\circ,\ldots,Z_m^\circ)\sim\mathcal N(0,I_m)\)，则
\(PZ^\circ=Z^\circ-\bar Z^\circ\mathbf1\) 的协方差为 \(P\)。中心
Gaussian 向量由均值和协方差唯一确定，因此

\[
G-\bar G\mathbf1=PG
\overset d=
\sqrt{\frac{\gamma-c}{v}}
\left(Z^\circ-\bar Z^\circ\mathbf1\right).
\]

这个等式只描述差分子空间中的 Gaussian 投影；它不声称
\(G_1,\ldots,G_m\) 独立。逐样本有

\[
\min_rG_r=\bar G+\min_r(G_r-\bar G).
\]

因为 \(G\) 居中，\(\mathbb E\bar G=0\)。又因为
\(\mathbb E\bar Z^\circ=0\) 且独立标准正态向量关于取负对称，

\[
\mathbb E\min_rZ_r^\circ=-\mathbb E\max_rZ_r^\circ=-\kappa_m.
\]

所以

\[
\mathbb E\min_rG_r
=-\kappa_m\sqrt{\frac{\gamma-c}{v}}.
\]

最后代入

\[
\gamma-c=\frac2{k-1},
\qquad
v=\frac{2(p-1)}{k(k-1)},
\]

得到

\[
\frac{\gamma-c}{v}=\frac{k}{p-1},
\qquad
\mathbb EH
=-\frac{\kappa_{k-1}}v\sqrt{\frac{k}{p-1}}.
\]

该推导解释了系数只依赖外围差分协方差，而不要求各外围首次到达时间
独立。

## 8. 从矩收敛到两个均值展开

由 \(W_N=(\tau_N-t_N^*)/\sqrt N\) 和第 6.3 节，

\[
\mathbb E\tau_N=t_N^*+\sqrt N\,\mathbb EW_N
=t_N^*+\sqrt N\,\mathbb EH+o(\sqrt N).
\]

代入第 7 节的 \(\mathbb EH\) 得到定理中的绝对均值展开。再除以
\(t_N^*=N/v\)，得到相对展开。期望交换由第 6 节的统一可积性负责，
不是由有限网格模拟、仅有的分布收敛或未经证明的余项假设负责。

## 9. 有限网格数值诊断（不属于证明）

正式计算覆盖 \(k\in\{3,4,5\}\)、\(p\in\{1.25,1.5,2\}\) 和
\(N\in\{40,80,160,320\}\)。下列结果来自 Task 5 冻结产物：

| 诊断 | 有限网格结果 |
|---|---|
| 一步矩 | 第一轮和复跑各 9 个 \((k,p)\) 单元；最大闭式—枚举误差均为 \(2.220446049250313\times10^{-16}<10^{-12}\) |
| 精确锚点 | \(N=6\) 的 9 个单元，每单元 100,000 条轨迹；最大 Poisson 方程残差 \(3.197442310920451\times10^{-14}<10^{-10}\)，9 个精确均值全部落入同时 95% 区间，删失为 0 |
| 正式第一轮 | 36 个单元，每单元 20,000 条轨迹、40 个不重叠批次；删失为 0；修正比同时区间最大半宽为 0.025877691320792203，低于 0.03 门槛 |
| 独立复跑 | 36 个单元使用与第一轮完全不相交的 36 个种子；删失为 0；全部 36 个同时 Welch 区间包含 0；最紧的零侧余量为 0.0010919013086878454 |
| 敏感性 | 精度门和复跑门均通过，预声明失败单元集合为空，因此未启动 100,000 轨迹敏感性运行 |

同轨迹局部代理也保留了有限 \(N\) 偏差，而不是把它隐藏为“已收敛”。最难
单元 \((k,p)=(5,1.25)\) 的缩放绝对误差 90% 分位数在
\(N=40,80,160,320\) 时依次为
\(162.8573,144.7966,131.3136,116.8905\)；五个目标分位数中的最大绝对
差在同一组 \(N\) 上依次为 \(130.1092,98.0840,70.5951,50.7856\)。
这些量在声明网格上下降，但仍很大，只能说明弱偏置大 \(k\) 单元的有限
样本逼近较慢。它们既不证明单调收敛，也不提供渐近误差率。

冻结证据入口：

- [精确锚点](../../../results/t12-positive-competition-exact-anchors/t12-exact-anchors.csv)
- [正式第一轮](../../../results/t12-positive-competition/t12-primary.csv)
- [独立复跑](../../../results/t12-positive-competition-replication/t12-primary.csv)
- [复跑比较](../../../results/t12-positive-competition-replication-comparison/t12-replication-comparison.csv)
- [Task 5 正式执行报告](../../../.superpowers/sdd/t12-task-5-report.md)

数值实验的角色限于：检查离散增量枚举、模拟器、有限状态精确求解器、
区间算术、种子独立性和有限网格与理论方向的一致性。渐近定理由第 2–8
节的解析论证建立。

## 10. 严格性状态与外部复核边界

本文件完成了以下内部证明链：

1. 从一步事件律推出外围漂移、原始二阶矩、协方差和
   \(\gamma-c\)；
2. 用固定维 i.i.d. CLT 和显式取整余项得到确定时刻 Gaussian 截距；
3. 用正向/反向最大型 Azuma 界得到紧集上一致局部线性化；
4. 用退出时间紧性和严格下穿连续性处理相关的多竞争者，不作独立性假设；
5. 用 \(C_1e^{-c_1N}\) 界移除中心坐标；
6. 用 Gaussian 窗口和 T11 远晚尾得到每个固定 \(q>0\) 的一致可积性；
7. 用均值零差分投影推导 Gaussian 极值系数和均值展开。

因此 T12 在当前项目词典下可标为“A — 内部工作稿闭合，外部概率论签核
未完成”。这不是同行评审、独立确认或发表状态。当前没有外部概率论研究者
对本证明签字；Task 5 的执行复核和有限网格 QA 也不构成该签核。

外部复核者至少应逐项检查：自由延拓的逐路径等价；正反向局部最大不等式；
所有 floor/ceil 事件包含关系；紧性与局部退出映射的组合；同时竞争者下的
严格穿越；中心异常退出界；第 6 节两段尾的覆盖与尾积分；以及第 7 节只在
差分子空间使用独立标准正态表示的边界。任一关键项未通过时，T12 应回退
为 C，均值二阶式应改写为 theory-informed empirical correction。
