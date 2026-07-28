# T12 正漂移竞争二阶极限：证明与验证设计

日期：2026-07-18  
状态：已完成方案选择，待用户审阅本规格后实施  
范围：固定参与者数、固定正中心偏置的单超边首次余额耗尽；不涉及论文正文组装或投稿。

## 1. 目标与成功标准

当前 T11 已证明固定正漂移下退出时间的一阶指数集中和全部固定正阶矩的一阶收敛，但 T12 的多个外围节点竞争导致的 $\sqrt N$ 级修正仍标为 C。目标是将 T12 提升为内部闭合的 A 类工作稿，并用独立、可复现、无删失的计算实验验证离散模型、局部近似和统计实现。

成功必须同时满足：

1. 从一步增量律重新推导外围漂移与协方差，不能把经验公式当作证明前提；
2. 证明退出时间的 $\sqrt N$ 级分布极限；
3. 证明缩放退出时间族一致可积，从而严格交换期望并得到二阶均值展开；
4. 解释高斯极值常数为何只依赖外围差分协方差，而不要求外围首次到达时间独立；
5. 通过精确 Markov 锚点、正式 Monte Carlo、独立种子复跑、区间和哈希 QA；
6. 所有有限网格结果保持“数值诊断”标签，不作为渐近定理的证明。

## 2. 数学合同

固定 $k\ge3$、$p\in(1,2]$，记

\[
\delta=p-1,\qquad m=k-1,\qquad
v=\frac{2\delta}{k(k-1)},\qquad
t_N^*=\frac{N}{v}.
\]

参与者 0 为中心，外围参与者为 $1,\ldots,m$。每步均匀选择一个无序节点对；中心—外围对以 $p/2$ 的条件概率向中心转移一个单位，以 $(2-p)/2$ 的条件概率反向转移；外围—外围对方向公平。初态为 $(N,\ldots,N)$，停止时间为首个余额坐标到达 0 的时刻 $\tau_N$。

自由延拓外围坐标写为

\[
Z_r(n)=N-vn+M_r(n),\qquad 1\le r\le m,
\]

其中 $M$ 是中心化增量和。一步外围协方差矩阵 $B$ 必须满足

\[
B_{rr}=\gamma=\frac2k-v^2,
\qquad
B_{rs}=c=-\frac{2}{k(k-1)}-v^2\quad(r\ne s),
\]

因而

\[
\gamma-c=\frac{2}{k-1}.
\]

## 3. 目标定理

令 $G\sim\mathcal N(0,B/v)$，并令

\[
H=\frac1v\min_{1\le r\le m}G_r.
\]

需要证明：

\[
\frac{\tau_N-t_N^*}{\sqrt N}\Rightarrow H.
\]

进一步，对每个固定 $q>0$，证明

\[
\mathbb E\left|
\frac{\tau_N-t_N^*}{\sqrt N}
\right|^q
\longrightarrow \mathbb E|H|^q.
\]

令 $Z_1,\ldots,Z_m$ 为独立标准正态变量，

\[
\kappa_m=\mathbb E\max_{1\le r\le m}Z_r.
\]

交换对称高斯向量的差分投影给出

\[
\mathbb E\min_r G_r
=-\kappa_m\sqrt{\frac{\gamma-c}{v}}
=-\kappa_m\sqrt{\frac{k}{\delta}}.
\]

因此目标二阶展开为

\[
\boxed{
\mathbb E\tau_N
=t_N^*
-\frac{\kappa_{k-1}}{v}\sqrt{\frac{k}{p-1}}\sqrt N
+o(\sqrt N)
}
\]

或等价地

\[
\boxed{
\frac{\mathbb E\tau_N}{t_N^*}
=1-\kappa_{k-1}\sqrt{\frac{k}{(p-1)N}}
+o(N^{-1/2}).
}
\]

该定理只覆盖固定 $k,p$。它不覆盖 $p=p_N\to1$、$k=k_N\to\infty$、多超边相关网络或余额依赖路由。

## 4. 证明模块

### 4.1 一步矩与确定时刻 CLT

直接枚举无序对和方向，得到外围均值 $-v\mathbf1$ 与协方差 $B$。令 $n_N=\lfloor t_N^*\rfloor$，由固定维 i.i.d. 多元 CLT，

\[
\frac{M(n_N)}{\sqrt N}\Rightarrow G,
\qquad G\sim\mathcal N(0,B/v).
\]

### 4.2 局部过程退化为随机截距直线

对固定 $C<\infty$ 和 $s\in[-C,C]$，定义

\[
Y_{N,r}(s)=\frac{Z_r(\lfloor t_N^*+s\sqrt N\rfloor)}{\sqrt N}.
\]

用有界增量最大不等式证明长度 $O(\sqrt N)$ 的局部时间窗内新增鞅噪声为 $o_{\mathbb P}(\sqrt N)$，并处理取整余项，从而在紧集上一致得到

\[
Y_N(\cdot)\Rightarrow G-v(\cdot)\mathbf1.
\]

极限路径逐坐标严格向下穿越 0，因此首次到达映射在极限路径处连续。

### 4.3 中心坐标与远离窗口的退出

中心坐标具有正漂移。在 $t_N^*+O(\sqrt N)$ 时间窗内，中心余额的确定性均值仍为正的 $N$ 量级。最大型 Hoeffding/Azuma 界给出中心异常先耗尽概率指数小，因此它不影响 $\sqrt N$ 极限或矩极限。

外围退出的早尾和晚尾在 $x\sqrt N$ 偏移下分别由最大型和固定时刻有界增量不等式控制。对 $x=O(\sqrt N)$ 得到 $e^{-c x^2}$ 型界；更远的晚尾沿用 T11 的几何尾。由此证明

\[
\left\{\left|\frac{\tau_N-t_N^*}{\sqrt N}\right|^q:N\ge1\right\}
\]

对每个固定 $q>0$ 一致可积。

### 4.4 高斯极值常数

不假设外围块独立。对交换对称 $G$，令 $\bar G=m^{-1}\sum_rG_r$。因为 $\mathbb E\bar G=0$，

\[
\mathbb E\min_rG_r
=\mathbb E\min_r(G_r-\bar G).
\]

差分投影满足

\[
G-\bar G\mathbf1
\overset d=
\sqrt{\frac{\gamma-c}{v}}
\left(Z-\bar Z\mathbf1\right),
\]

故期望最小值等于独立标准正态最大值期望的负值乘以上述尺度。这一步解释现有经验公式中的 $\kappa_{k-1}$ 和 $\sqrt{k/(p-1)}$。

## 5. 计算实现边界

新增文件：

- `t12_positive_competition_validation.py`：一步矩、理论常数、耦合模拟、精确锚点、正式运行和 manifest；
- `test_t12_positive_competition.py`：全部新生产接口的测试；
- `outputs/researchwrite/hypergraph-stopping-time/17_t12_positive_competition_proof_and_validation.md`：证明及结果报告；
- `outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-18_t12_positive_competition.md`：RED/GREEN、正式运行和完整 QA。

不得修改已有冻结结果。正式输出使用新目录：

- `results/t12-positive-competition/`；
- `results/t12-positive-competition-replication/`；
- `results/t12-positive-competition-exact-anchors/`；
- 必要时的 `results/t12-positive-competition-sensitivity/`。

## 6. 正式实验设计

### 6.1 参数网格与独立单位

- $k\in\{3,4,5\}$；
- $p\in\{1.25,1.50,2.00\}$；
- $N\in\{40,80,160,320\}$；
- 共 36 个主单元；
- 每单元第一轮 20,000 条独立轨迹；
- 独立复跑每单元另取 20,000 条、使用不相交种子；
- 每轮每单元按生成顺序划分为 40 个不重叠批次，每批 500 条。

独立实验单位是单条完整轨迹；批次只用于稳健标准误和 Student-$t$ 区间。不得把同一轨迹的多个时间点当作独立重复。

### 6.2 同轨迹局部近似

每条自由增量流同时记录真实退出时间 $\tau_N$ 和确定时刻 $n_N=\lfloor t_N^*\rfloor$ 的外围鞅向量 $M(n_N)$。若轨迹先于 $n_N$ 退出，仍以同一 i.i.d. 自由增量律补足到 $n_N$；若在 $n_N$ 后退出，则继续到真实首次耗尽。不得在余额为零后改变自由增量律。

局部代理定义为

\[
\widehat\tau_{N,\mathrm{loc}}
=t_N^*+\frac1v\min_rM_r(n_N).
\]

记录

\[
\frac{\tau_N-t_N^*}{\sqrt N},\qquad
\frac{\widehat\tau_{N,\mathrm{loc}}-t_N^*}{\sqrt N},\qquad
\frac{|\tau_N-\widehat\tau_{N,\mathrm{loc}}|}{\sqrt N}.
\]

局部代理可为非整数或负数，只作为渐近线性化变量，不能称为真实停止时间。

### 6.3 主统计量

理论均值修正系数为

\[
A(k,p)=\frac{\kappa_{k-1}}v\sqrt{\frac{k}{p-1}}.
\]

每个单元报告：

1. 真实退出时间均值、标准差和无删失轨迹数；
2. 缩放修正 $\widehat A_N=(t_N^*-\bar\tau_N)/\sqrt N$；
3. 归一化修正比 $R_N=\widehat A_N/A(k,p)$；
4. 基于 40 个批次均值的 Bonferroni 同时 95% Student-$t$ 区间；
5. 局部代理缩放绝对误差的均值、中位数和 90% 分位数；
6. 真实缩放退出时间与目标高斯极值分布的 0.1、0.25、0.5、0.75、0.9 分位数差；
7. 第一轮与独立复跑的 $R_N$ 差异，以及基于两组各 40 个批次值的 Welch 区间。

实验不把“置信区间包含 1”作为渐近定理证明，也不要求有限 $N$ 下单调收敛。

### 6.4 精确锚点

对 $k\in\{3,4,5\}$、$p\in\{1.25,1.50,2.00\}$、$N=6$ 求解对称压缩的精确有限状态 Poisson 方程，并各用 100,000 条新轨迹复核，共 9 个锚点。每个锚点按生成顺序划分为 100 个不重叠批次，每批 1,000 条，并以批次均值构造 Student-$t$ 区间。

门槛：

- 最大线性方程残差 $<10^{-10}$；
- 精确均值落入按 9 重比较校正的同时 95% Monte Carlo 区间；
- 无时间截断、无删失、无事后排除。

### 6.5 预声明准确性门槛

1. 一步均值、原始二阶矩和协方差枚举最大绝对误差 $<10^{-12}$；
2. 所有正式单元均达到计划轨迹数，删失数为 0；
3. 36 个 $R_N$ 同时区间的最大半宽不超过 0.03；
4. 9 个精确锚点全部通过残差和同时区间门槛；
5. 第一轮与独立复跑的 36 个 $R_N$ 差异，其按 36 重比较校正的同时 95% Welch 区间全部包含 0；
6. 所有 CSV、metadata 和 manifest 可重算，正式代码、测试和结果写入 SHA-256 清单。

若第 3 或第 5 项失败，使用新种子对最弱或冲突单元追加 100,000 条轨迹和 100 个不重叠批次；不得删除原结果。敏感性结果只用于区分 Monte Carlo 不确定性与稳定偏差，不能追逐显著性。

## 7. 测试驱动顺序

1. 先测试理论漂移、协方差和 $\gamma-c$ 恒等式，观察缺失接口失败；
2. 再测试 $\kappa_m$、$A(k,p)$ 和 $k=3$ 可手算特例；
3. 测试耦合模拟的守恒、可重复性、自由延拓、无删失和小参数路径；
4. 测试批次区间、Bonferroni 临界值、分位数和复制差异算术；
5. 测试精确锚点、CSV schema、metadata、manifest 和拒绝覆盖非空目录；
6. 每个生产接口均须先出现与缺失功能一致的 RED，再写最小实现至 GREEN；
7. 最后运行新测试、完整回归、语法编译和独立产物重算。

## 8. 失败处理与主张边界

- 若局部过程证明无法给出严格穿越连续性，则 T12 保持 C，不用模拟替代该步骤；
- 若一致可积性失败，只保留分布极限，不写二阶期望展开；
- 若高斯极值投影推导失败，撤回现有 $\kappa_{k-1}$ 理论系数；
- 若精确锚点失败，先诊断模拟器或状态压缩，禁止正式大规模运行；
- 若独立复跑冲突且敏感性仍不能解释，报告冲突并保持数值结论未通过；
- 即使全部内部门槛通过，T12 仍须外部概率论研究者签核后才能称为独立确认；
- 不声称该二阶极值修正是一般 PCN、任意超图或任意相关路由的统一定理。

## 9. 交付判据

完成时应有：可逐式审计的 T12 证明、测试先行记录、两轮独立正式模拟、9 个精确锚点、必要的最弱单元敏感性、全部 manifest/哈希以及更新后的证明登记表和项目状态。项目完成度只有在这些证据全部通过后才能重新计算；论文正文仍不在本任务范围内。
