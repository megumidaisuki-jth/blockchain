# 定理与证明缺口登记表

更新日期：2026-07-24

## 1. 审计结论

文献审计确认：有限状态吸收 Markov/Poisson 框架、(k=3) 乘积闭式和
三人零漂移扩散退出极限均有直接先例，不能列为原创主定理。在当前固定额
中心偏置模型中，吸收性、零漂移势函数界、漂移/协方差、含漂移路径界、
固定非零漂移的相对指数集中与全矩极限，以及固定 (k) 的弱漂移退出时间
全矩极限，现已具备闭合证明工作稿。进一步以
\(p_N=1+\eta N^{-\alpha}\) 统一得到 \(\alpha<1\) 漂移集中、
\(\alpha=1\) 带漂移扩散和 \(\alpha>1\) 公平扩散的三分区相图。
弱漂移包已完成一次内部对抗性复核并修正 PDE
函数空间，但仍须按 09 评审包完成外部独立概率论复核。文献审计进一步
确认“非对称一般 \(n\) 人”和“全矩”均不能单独作为新颖性；Barnett
（1964）全文是 T9 低维先例判断的 P0 闸门。正漂移 \(N^{-1/2}\) 竞争修正
现已用确定时刻多元 CLT、紧集局部鞅界、严格穿越退出映射、中心指数
小概率界、两段尾界与 Gaussian 差分投影完成内部证明闭合；其有限网格
验证与解析证明分开记录。按作者决定，人类专家签核不再作为项目硬门；旧评审包仅保留为可选导师审阅清单。

Task 7 formal fix 1 后，相关网络证明包 13 又在显式有限状态耗尽可达性下内部闭合 T16，在合同 12 第 6 节条件下内部闭合 T17A/B/C，并在联合 Gaussian 极限的零跨超边协方差块条件下内部闭合 T18a。T18b 保持 E / mixed：冻结增量律非因子化是严格结论，冻结设计的配对停止时间差是数值观察，没有普遍符号定理。上述 T16、T17 与 T18a 的人类专家签核已由作者取消为硬门；评审包 14 仅作为可选审阅清单保留，publication readiness 仍因机构检索、现实映射和中文稿件未完成而为 false。Task 9 已以运行最小值容差验证清除精确生存函数序列化债务，42/42 测试、264 行冻结证据和 6/6 manifest 通过，五个数学 CSV 哈希未改变。Task 10 又完成开放来源八项同构审计；机构数据库确认仍是未通过门禁。

## 2. 证明状态词典

| 状态 | 含义 | 论文处理 |
|---|---|---|
| A | 当前工作稿中已有闭合证明；仍需合作者或同行独立核查 | 可写为 theorem/proposition |
| B | 核心论证成立，但还缺一个短引理、边界条件或正式化步骤 | 修补后才能写为 theorem |
| C | 形式推导或数值支持，关键概率收敛/误差阶未证明 | 写为 conjecture、formal approximation 或 numerical observation |
| E | 离散网格上的经验结果 | 只写 empirical surrogate/validation |
| X | 与当前合法模型冲突或证据不足 | 从论文主张中删除 |

“精确”只表示给定模型下没有近似误差；“已证明”还要求假设、有限性、
边界和可选停止条件全部写明。

## 3. 候选定理逐条登记

| ID | 候选结果 | 必要假设 | 当前证据 | 状态 | 投稿前动作 |
|---|---|---|---|---|---|
| T0 | \(\tau\) 几乎必然有限，且 \((I-Q)^{-1}\) 存在 | 有限整数单纯形；至少一个 \(\pi_{ij}>0\)；首次到零吸收 | 重复一个正概率方向给出几何尾界 | A | 独立核查几何尾界与谱半径表述 |
| T1 | 任意合法 \(\Pi\) 下 \((I-Q)u=\mathbf1\) 唯一确定 \(\mathbb E\tau\) | T0；固定交易额；整数余额 | Swan–Bruss 2006、Marfil–David 2024；一步条件化；T0；稀疏残差 | A | 作为标准方法基线；只把项目特定实现/吸收证明列为方法贡献 |
| T2 | \(k=2\) 无漂移/有漂移赌徒破产公式 | 真正的 Bernoulli 方向概率；吸收边界 | 二阶差分方程；单元测试 | A | 作为已知基线，不作新颖性主张 |
| T3 | \(k=3\) 均匀流量下 \(\mathbb E_{x,y,z}\tau=3xyz/(x+y+z)\) | 正整数余额；六个有序方向等概率 | Engel 1993；Bruss et al. 2003；Alabert et al. 2004；本项目复推与求解器 | A | 明确标为已知基线，不进入原创贡献列表 |
| T4 | 零漂移平方势函数占用恒等式 | 固定交易额；\(\boldsymbol\mu=0\) | 生成元恒等式；有界停止；T0 | A | 明确初值不必均分，界才使用均分 |
| T5 | 均分零漂移下的严格上下界 | T4；均分初值 | 边界势函数极值 | A | 可补充整数边界的更紧上界作为附录 |
| T6 | 中心偏置模型的漂移和协方差公式 | 无序节点对均匀；\(p\in[0,2]\) | 合法联合概率直接计算 | A | 统一中心/外围下标与 \(p\) 定义 |
| T7 | 路径下界 \(\tau\ge N\) 与负漂移坐标上界 | 均分初值；固定单位交易；T0 | 路径计数；坐标鞅可选停止 | A | 在定理中明确对每个 \(d_i<0\) 都成立 |
| T8 | 公平均匀选对模型下 \(\mathbb E\tau/N^2\to a_k\) | 固定 \(k\)；\(N\to\infty\)；无序对均匀且方向公平 | T9 取 \(\eta=0\)；势函数统一均值界；Alabert 2004 给出 (k=3) 先例 | A | 独立复核；明确 (k=3) 非原创并继续检索一般 (k) 先例 |
| T9 | 中心偏置弱漂移 \(p_N=1+\eta/N\) 下 \(\tau_N/N^2\Rightarrow T\)，且 \(\mathbb E(\tau_N/N^2)^q\to\mathbb ET^q\) 对每个 \(q>0\) 成立 | 固定 \(k,\eta\)；\(N\to\infty\)；第 2 节中心偏置机制 | 三角阵列 FCLT；运行最小值连续集；全状态 \(O(N^2)\) 均值界；强 Markov 几何尾与统一指数矩；变分 PDE；内部对抗性审计 | A | 按 09 的 R1–R12 外部签核；全文核查 Barnett 1964；补精确定理编号。不能把标准扩散逼近或“全矩”本身作重大创新 |
| T10 | 固定 \(p<1\) 时 \(\tau_N/t_-^*\) 相对指数集中于 1，且 \(\mathbb E(\tau_N/t_-^*)^q\to1\) 对每个 \(q>0\) 成立 | 固定 \(k\) 和 \(p\in[0,1)\)；\(N\to\infty\) | 自由延拓；最大型 Azuma 早尾；单中心坐标晚尾；统一指数矩；10 证明包 | A | 按 10 的 12 项清单独立检查过程延拓、最大不等式、尾和与整数取整 |
| T11 | 固定 \(p>1\) 时 \(\tau_N/t_+^*\) 相对指数集中于 1，且 \(\mathbb E(\tau_N/t_+^*)^q\to1\) 对每个 \(q>0\) 成立 | 固定 \(k\) 和 \(p\in(1,2]\)；\(N\to\infty\) | 自由延拓；全坐标早尾并集；任一外围负漂移坐标晚尾；统一指数矩；10 证明包 | A | 独立检查中心异常早停、外围竞争与一阶定理/二阶修正的边界 |
| T12 | 固定 \(k\ge3\)、固定 \(p\in(1,2]\) 的正漂移 \(N^{-1/2}\) 竞争修正：分布极限、全部固定正阶绝对矩和二阶均值展开 | T11 的自由延拓与远晚尾；固定 \(k,p\)；单位整数转移 | 17 证明包：一步协方差、确定时刻多元 CLT、含 floor 的紧集局部鞅界、退出时间紧性、相关多竞争者严格穿越、中心指数小概率界、两段尾与 UI、Gaussian 差分投影；Task 5 有限网格只作诊断 | A — internally closed and code-reproducible | 17 第10节仅作可选导师审阅；不得把有限网格 QA 写成定理证据，不得推广到 \(p_N\to1\)、\(k_N\to\infty\) 或网络模型 |
| T13 | 独立通道/超边生存函数乘积是 Podiatchev–Orda–Rottenstreich (2024) 直接覆盖的基线；本项目只复现并用作相关网络对照。 | 非负整数停止时间；跨超边独立 | Podiatchev–Orda–Rottenstreich 2024；尾和恒等式 | A（先行工作基线） | 不列为项目贡献，不推广至共享路由 |
| T14 | 冻结 v4 在声明网格上具有低经验误差 | 中心偏置模型；声明域；冻结系数 | 2,112 点、独立模拟器、哈希复算 | E | 补齐可执行拟合链；不得写成连续域误差定理 |
| T15 | \(p_N=1+\eta N^{-\alpha}\) 下：\(\alpha<1\) 时 \(\tau_N/N^{1+\alpha}\) 指数集中于正负不对称常数；\(\alpha=1\) 时为带漂移 Brownian 单纯形退出；\(\alpha>1\) 时为公平 Brownian 单纯形退出；三者均有全部固定正阶矩收敛 | 固定 \(k,\eta\ne0,\alpha\ge0\)；均分初值；充分大 \(N\)；\(\alpha=0\) 时 \(|\eta|\le1\) | 07、10、11；\(\alpha>1\) 势函数统一增量下界；\(k=2\) 精确 Markov 尺度校验 | A | 按 11 的 12 项清单独立复核；不得声称首次发现 \(1/N\) 临界尺度或小漂移相变 |
| T16 | 相关网络有限状态吸收与 Poisson 方程 | 有限状态耗尽可达性 | 13 证明包；Task 6 精确残差/全状态可达性门 | A — internally closed and code-reproducible | 14的R01–R03仅作可选审阅；有限网格证书不替代一般假设 |
| T17 | 相关网络多项式漂移三分区及全部固定正阶矩 | 合同 12 第 6 节 | 13 证明包；数值仅作诊断 | A — all proof modules internally closed after fix 1 | 14的R04–R12仅作可选审阅；`alpha=0.5` 有限网格不得作为收敛验证 |
| T18a | 零跨块协方差下的扩散级独立聚合 | 联合 Gaussian 极限 | 13 证明包的块独立证明 | A — internally closed and code-reproducible | 14的R13仅作可选审阅；不得推广到一般非 Gaussian 零协方差增量 |
| T18b | 显式冻结非因子化与误差诊断 | 冻结拓扑/需求/代理 | Task 6 配对 MC + 精确基线 | E — no universal sign theorem | 保留“严格增量律结论 + 冻结数值观察”的混合标签；做跨拓扑稳健性审计 |
| T19 | 零漂移平衡二元通道相关模型到 Gaussian 块生存序的离散桥接：退出时间、统一指数矩、全矩收敛及极限均值差非负 | 固定有限二元网络；外生 i.i.d. 单位增量；严格零漂移；平衡初态；各通道正方差；独立代理保持完整通道边际 | 27 证明包；三节点路径 \(N=1\)–256 确定性 Poisson 验证；28/28a独立子Agent验收 | A — internally closed, independent subagent ACCEPT | 人类专家签核不再是硬门；不得推广为有限 \(N\) 符号定理、非中心域或三元以上超边定理 |
| T32 | 冻结真实拓扑需求插值的有限尺度符号机制 | 4日期×2锚点；λ∈{0,.25,.5,.75,1}；N=40；正式与独立复跑 | 80单元、3,200分块、80唯一种子；五重/八重/四重同时区间；中文PNG和6项哈希 | E+ — bounded mechanism evidence | 只有4日期；后验综合；概率插值同时改变漂移、协方差和高阶矩；不得升级为普遍符号或仅漂移因果定理 |

## 4. 已闭合内部工作稿与尚未闭合证明包

### 4.1 扩散退出时间证明包（T8–T9，工作稿已闭合）

完整证明见 [弱漂移退出时间极限证明包](07_weak_drift_proof_package.md)。
闭合顺序如下：

1. 有界三角阵列增量给出切向子空间 FCLT，极限均值
   \(\boldsymbol\beta_\eta t\)、协方差 \(tA_0\)。
2. 每个面法向投影是一维非退化带漂移 Brownian 运动；其运行最小值
   无原子，有限个面遂给出首次出界连续集。
3. \(\eta=0\) 用平方势函数，\(\eta\ne0\) 用负漂移坐标，对所有内部状态
   得到统一 \(AN^2\) 均值界；强 Markov 分块进一步给出
   \(\Pr(\tau_N>m\lceil2AN^2\rceil)\le2^{-m}\)，闭合一致可积性。
   该尾界还给出统一指数矩及所有固定正阶矩收敛。
4. 极限生成元在切向空间一致椭圆；Dynkin/Feynman–Kac 识别
   \(H_0^1\) 变分弱解；比较原理另给出唯一连续黏性解，内部为经典解。

当前状态 A 的含义仍是“本项目工作稿闭合、完成内部对抗性审计但待外部
独立核查”，不是已发表定理。投稿前必须补精确定理编号、整数取整细节、
目标期刊 PDE 解框架，并完成 [09 外部评审包](09_weak_drift_external_review_packet.md)
的 R1–R12 签核。

### 4.2 固定强漂移证明包（T10–T11，工作稿已闭合）

完整证明见 [固定强漂移退出时间证明包](10_strong_drift_proof_package.md)。
闭合顺序如下：

1. 在整个整数格上以同一串独立增量自由延拓，逐路径证明原停止时间等于
   各自由坐标首次到零时间的最小值。
2. 对 \(M_i(n)=Z_i(n)-N-d_in\) 应用最大型 Azuma–Hoeffding；在
   \((1-\varepsilon)t_N^*\) 前，任一坐标到零都要求至少
   \(\varepsilon N\) 的负偏离，得到 \(ke^{-cN}\) 早尾。
3. 在 \((1+\varepsilon)t_N^*\) 后，只需选择任一负漂移坐标；尚未退出
   要求至少 \(\varepsilon N\) 的正偏离，得到 \(e^{-cN}\) 晚尾。
4. 对 \(n\ge2N/v\)，同一负漂移坐标给出
   \(\Pr(\tau_N>n)\le e^{-v^2n/32}\)；尾和恒等式遂给出
   \(\tau_N/N\) 的统一指数矩和任意固定正阶矩收敛。
5. 截断可选停止独立给出有限容量上界
   \(\mathbb E\tau_N\le t_N^*=N/v\)，作为交叉核查。

该结果覆盖 \(k=2\) 与 \(p=0,2\)，但要求 \(k,p\ne1\) 固定，不覆盖
\(p=p_N\to1\) 或 \(k=k_N\)。状态 A 仍表示内部工作稿闭合而非外部审阅
通过；投稿前必须完成证明包末尾 12 项独立签核。

### 4.3 多项式消失漂移相图（T15，工作稿已闭合）

完整证明见
[多项式消失漂移相图证明包](11_polynomial_drift_phase_diagram_proof_package.md)。
闭合顺序如下：

1. 识别控制参数
   \(\mathrm{Pe}_N=N|p_N-1|=|\eta|N^{1-\alpha}\)；
2. \(\alpha<1\) 时把 10 的自由延拓/Azuma 论证推广到随 \(N\) 消失的
   负漂移，得到 \(e^{-cN^{1-\alpha}}\) 相对偏离界；
3. 利用 \(Nv_N\to\infty\) 闭合
   \(\tau_N/t_{N,\alpha}^*\) 的统一指数矩和全矩收敛；
4. \(\alpha=1\) 直接调用 07–09 的带漂移扩散退出定理；
5. \(\alpha>1\) 时累计漂移 \(N^{1-\alpha}\boldsymbol\beta_\eta\to0\)；
   对平方势函数证明全状态一步期望增量最终至少为 1，从而给出统一
   \(k(k-1)N^2\) 均值界、几何尾、指数矩和公平扩散全矩极限。

该相图把 T9–T11 放入同一尺度框架，是当前更适合作为论文主理论的候选。
但 Athreya–Sethuraman–Tóth、Wachtel、Schulte-Geers–Stadje 等已经证明
一维弱不对称或小漂移转变现象，故只能主张中心偏置守恒单纯形成对转账核
下的模型特定统一组合。

### 4.4 正漂移二阶修正证明包（T12）

完整证明见
[正漂移竞争二阶极限证明与有限网格验证](17_t12_positive_competition_proof_and_validation.md)。
闭合顺序如下：

1. 从一步转移事件直接得到外围均值 \(-v\mathbf1\)、协方差 \(B\) 和
   \(\gamma-c=2/(k-1)\)，并在
   \(n_N=\lfloor t_N^*\rfloor\) 应用固定维 i.i.d. 多元 CLT。
2. 对 \(t_N^*+[-C,C]\sqrt N\) 内的正向和反向中心化增量分别应用
   最大型 Azuma–Hoeffding，显式保留全部 \(O(1)/\sqrt N\) floor 余项，
   得到紧集上一致的随机截距直线极限。这里不使用或声称强近似。
3. 先用 \(e^{-cC^2}\) 早晚界证明缩放外围退出时间紧，再利用
   \(\min_r(G_r-vs)=\min_rG_r-vs\) 的严格零穿越证明退出映射连续；
   即使多个相关坐标同时竞争，该论证也不要求独立性。
4. 中心坐标在局部窗口内的确定性余额保持 \(N\) 量级，其异常先耗尽概率
   为 \(C_1e^{-c_1N}\)，故完整停止时间与外围停止时间具有同一极限。
5. 在 \(1\le x\le2\sqrt N/v\) 上得到 \(e^{-cx^2}\) 尾界，在更远晚尾
   调用 T11 的几何界；尾积分遂给出每个固定 \(q>0\) 的一致可积性和
   绝对矩收敛。
6. 在均值零外围差分子空间中证明
   \(PG\overset d=\sqrt{(\gamma-c)/v}\,PZ\)，由
   \(\mathbb E\bar G=0\) 推出 \(\kappa_{k-1}\) 系数和两个二阶均值展开。

Task 5 的精确锚点、第一轮、独立种子复跑和区间门均通过，但这些证据只
检查实现与有限网格对齐。T12 的 A 状态只表示内部证明工作稿闭合；外部
概率论研究者尚未签核。

### 4.5 相关网络 T16–T18 证明包（内部闭合、代码可复现）

完整证明见 [相关网络 T16–T18 证明包](13_correlated_network_proof_package.md)，模型边界见 [合同 12](12_correlated_hypergraph_network_model_and_theorem_contract.md)，独立签核接口见 [评审包 14](14_correlated_network_external_review_packet.md)。

1. T16 在显式有限状态耗尽可达性下，用有限状态正概率路由词排除闭合非吸收类，得到谱半径、Neumann 逆和 Poisson 唯一解；Task 6 的 \(N=1,2,3\) 残差与可达性只作为冻结实例证书。
2. T17A 在 formal fix 1 后用精确的 `floor` 事件等价修复非整数晚尾阈值，并闭合早晚尾、统一指数矩和全部固定正阶矩。
3. T17B/C 用三角阵列 FCLT、有限 active set 的单面/多面立即穿越、两类全状态 \(O(N^2)\) 均值机制和强 Markov 几何块闭合退出时间与全部固定正阶矩。
4. T18a 只在联合 Gaussian 极限中以零跨超边协方差块推出路径块独立；T18b 的冻结跨块非零协方差严格排除增量律因子化，但停止时间差只属于 Task 6 冻结数值观察。

上述证明模块的状态上限分别为 A、A、A、E；A 仍只表示内部证明工作稿闭合。评审包 14 的 R01–R14 当前全部未签署，任何空白都不等于通过。

## 5. 推荐的论文定理结构

1. **Lemma / Methods baseline — Well-posed finite-state exit equation**：
   T0–T1；明确引用多人 ruin 的既有 Markov 方法。
2. **Known analytic baselines**：T2–T3，仅用于校验，不列入原创贡献。
3. **Theorem 2 — Zero-drift potential identity and bounds**：合并 T4–T5。
4. **Proposition 2 — Center-biased drift and covariance**：T6。
5. **Theorem 3 — Finite-capacity drift bounds**：T7。
6. **Theorem 4 — Polynomial-drift phase diagram and moment limits**：
   以 T15 统一 T8–T11；三分区分别引用弱/强漂移证明模块。
7. **Corollaries — Critical diffusion and fixed-drift concentration**：
   单列 T9 与 T10–T11 的 PDE、显式尺度和指数集中形式。
8. **Theorem — Fixed positive-drift competition correction**：T12；只覆盖固定
   \(k\ge3,p\in(1,2]\)，并与有限网格验证及 v4（T14）分开报告。
9. **Background / Related work / control baseline — T13**：独立通道/超边生存函数乘积是 Podiatchev–Orda–Rottenstreich (2024) 直接覆盖的基线；本项目只复现并用作相关网络对照。
10. **Theorem — Correlated finite-network absorption and Poisson equation**：T16；显式列出有限状态耗尽可达性。
11. **Theorem — Correlated-network polynomial-drift phase diagram**：T17；并列 T17A/B/C，数值相图只作诊断。
12. **Gaussian independence corollary and frozen diagnostic**：T18a/T18b；严格区分联合 Gaussian 充分条件与 E 类冻结数值观察。

这一结构让审稿人能清楚区分“精确离散理论”“已证明渐近”“形式极限”
和“经验代理”，避免一处证明缺口拖累整篇论文的可信度。

## 6. 首批攻关顺序

1. 由另一位概率论研究者独立复核 T0、T7，并按 10 的 12 项清单复核
   T10、T11；这是成本最低、最快可冻结的证明包。
2. 按 11 的 12 项清单重点复核 \(\alpha<1\) 的随 \(N\) 漂移指数矩和
   \(\alpha>1\) 的势函数统一增量下界；通过后以 T15 取代分散的主理论
   叙事。
3. T8–T9 的统一可积性已加强为统一指数矩和全矩收敛；内部对抗性审计
   已修正 PDE 函数空间。下一步由未参与推导者按 09 外部评审包逐项复核，
   并补齐引用与形式化细节；任何关键项未核查都不得视为通过。
4. 由未参与推导的概率论研究者按 17 第 10 节独立复核 T12 的局部 CLT、
   严格穿越、中心退出、两段尾积分和 Gaussian 投影；任何关键项未签核
   都不得写成“外部确认”，若发现实质缺口则回退为 C。
5. T3 已确认非原创；Tzioufas 2019 与 Phetpradap–Sripanitan 2025 又排除
   “全矩本身新颖”。下一步合法取得并阅读全文核验 Barnett 1964，再继续
   一般 (k) 中心偏置弱漂移、强漂移不对称和快速经验代理的组合定位。
6. 由未参与推导的概率论研究者按 14 的 R01–R14 独立签核 T16、T17A/B/C 与 T18a；并在重叠链、重叠星和随机连通超图上审计 T18b 的跨拓扑稳健性。开放来源八项同构审计已经完成；外部签核、MathSciNet/zbMATH/Scopus/WoS/CNKI 机构确认、完整英文稿件和目标期刊格式化完成前，publication readiness 保持 false。

## 7. 证据入口

- [无漂移研究报告](../../../研究报告.md)
- [含漂移严格推导](../../../含漂移超边停止时间_严格推导.md)
- [最终数值验证报告](../../../k3至50漂移公式_最终验证报告.md)
- [研究事实基线](01_research_canon.md)
- [主张—证据矩阵](02_evidence_table.md)
- [弱漂移退出时间极限证明包](07_weak_drift_proof_package.md)
- [弱漂移内部对抗性证明审计](08_weak_drift_adversarial_audit.md)
- [弱漂移外部概率论评审包](09_weak_drift_external_review_packet.md)
- [固定强漂移退出时间证明包](10_strong_drift_proof_package.md)
- [多项式消失漂移相图证明包](11_polynomial_drift_phase_diagram_proof_package.md)
- [正漂移竞争二阶极限证明与有限网格验证](17_t12_positive_competition_proof_and_validation.md)
- [相关网络模型与定理合同](12_correlated_hypergraph_network_model_and_theorem_contract.md)
- [相关网络 T16–T18 证明包](13_correlated_network_proof_package.md)
- [相关网络外部评审签核包](14_correlated_network_external_review_packet.md)
- [网络精确结果](../../../results/network/network-exact.csv)
- [网络相图诊断](../../../results/network/network-phase-scaling.csv)
- [相关模型—独立代理配对诊断](../../../results/network/network-correlated-vs-proxy.csv)
- [网络证据哈希清单](../../../results/network/SHA256SUMS.txt)
- [先行工作—主张映射](sources/literature_claim_map_2026-07-17.md)
- [近临界与非对称多人破产文献审计](sources/near_critical_asymmetric_search_audit_2026-07-17.md)
- [Barnett 1964 访问与引用链审计](sources/barnett_1964_access_and_citation_chain_audit_2026-07-17.md)
- [多项式漂移相图文献审计](sources/polynomial_drift_phase_search_audit_2026-07-17.md)
