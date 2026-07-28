# 概率论先行工作—本项目主张映射

检索日期：2026-07-17

## 已被直接先例覆盖的内容

| 本项目旧表述 | 直接先例 | 结论 |
|---|---|---|
| 三人均匀方向精确式 \(3xyz/(x+y+z)\) 是候选主创新 | Engel 1993；Bruss et al. 2003；Diaconis & Ethier 2022 的回顾 | 改为已知基线和实现校验 |
| 三人零漂移随机游走的 \(N^2\) Brownian 退出极限 | Alabert et al. 2004 | 已有过程/退出时间/期望/PDE 的直接先例 |
| 一般多人首次破产可由吸收 Markov 线性系统精确求解 | Swan & Bruss 2006；Marfil & David 2024 | 属标准框架；本项目价值在具体模型、约简、实现和后续渐近，不在方程形式本身 |
| 四人零漂移大容量 Poisson 近似 | Bruss et al. 2003 | 已有明确先例；不可声称本文首次提出公平 \(k=4\) PDE |
| 公平随机选对、单位转移、首次有人破产的多人模型 | Sobel & Frankowski 2002 的 random-selection 策略 | 模型和差分方程均已有直接先例 |
| 四人公平首次破产的 simplex/Brownian 大容量分析 | O’Connor & Saloff-Coste 2023 | 四人模型、连续单纯形和谱/harmonic-profile 路线均非首次 |
| 三人公平模型的 harmonic measure 与 Brownian 近似速率 | Denisov & Wachtel 2024 | 三人退出位置渐近和 Brownian 近似已有更强直接先例 |
| 有限单纯形 killed-chain/harmonic-measure 一般估计 | Diaconis, Houston-Edwards & Saloff-Coste 2021 | Perron–Frobenius、Doob transform 和 inner-uniform 域工具属于现有理论 |
| pairwise 多人 ruin 或非对称 pairwise 三人变体尚无人研究 | Grigorescu & Yao 2016；Kehagias et al. 2025 | 公平可控选对和非对称策略选对已有邻近先例，需按停止事件和控制机制区分 |
| 非对称一般 \(n\) 人首次破产尚无人研究 | Rocha & Stern 1999/2004；Hashemiparast & Sabzevari 2011；Sabzevari 2018 | 已有系统先例；但其每轮由一名赢家同时向所有对手收款，不是本项目成对单位转账 |
| “证明退出时间全部阶矩”本身可作为新颖性 | Tzioufas 2019；Phetpradap & Sripanitan 2025；Ekhad & Zeilberger 2023 | 不成立：不同几何/更新规则中已有全矩极限、任意阶矩公式或多阶精确矩；只能主张模型特定的组合结果 |
| 多人 ruin 的经验近似尚无先例 | Hussain et al. 2023 | 三人非对称经典规则已有经验近似；v4 必须突出成对转账、一般 \(k\)、结构约束和留出验证 |
| \(1/N\) 弱不对称尺度或“小漂移相变”本身可作为新颖性 | Athreya、Sethuraman 与 Tóth 2010；Wachtel 2009；Schulte-Geers 与 Stadje 2017；Geng 与 Markowsky 2026 | 不成立：区间弱不对称、first-passage transition、小漂移占用时间与区间退出漂移比较均有先例；只能主张中心偏置守恒单纯形中的模型特定统一结果 |
| 支付通道 lifetime、depletion 或 stopping time 尚无人直接建模 | Shabgahi et al. 2022；Dehshali et al. 2022；Podiatchev–Orda–Rottenstreich 2024 | 不成立：有效寿命、拓扑—寿命关系、吞吐上限、单通道停止时间和网络首通道失败均已有直接先例 |
| 超图/多方支付通道或跨超边支付语义尚无人提出 | Kim 2023；Kotzer et al. 2025；Corcoran–Lewis 2025；Nainwal–Kamble–Awathare 2026 | 不成立：必须把新颖性绑定到随机原子路由诱导的相关首耗尽理论，而不是表示法或协议语义 |
| 三角阵 first-passage 方法可作为本项目独立创新 | Denisov–Sakhanenko–Wachtel 2021 | 不成立：三角阵 first-passage 已有方法先例；只能主张特定相关超图几何与漂移相图的组合结果 |

## 仍可能形成贡献、但需继续审计的内容

| 候选差异点 | 当前证据 | 仍需排查 |
|---|---|---|
| 固定任意 \(k\) 的中心偏置弱漂移 \(p_N=1+\eta/N\) 退出时间全矩极限 | 本项目 07 证明包、08 内部对抗性审计、09 外部评审包；按四项同构判据尚未见完全同构结果 | **P0：全文核查 Barnett 1964**；MathSciNet/zbMATH/Scopus/WoS 引用追踪；标准扩散逼近和全矩现象本身创新有限 |
| 中心偏置下正负强漂移不对称的一阶极限、相对指数集中与全部固定正阶矩收敛 | 本项目 10 强漂移证明包：自由延拓、Azuma 早晚尾界、统一指数矩 | 集中工具是标准方法；一般非对称多人 ruin 与选边机制文献；需独立概率论复核 |
| \(p_N=1+\eta N^{-\alpha}\) 的三分区统一相图 | 本项目 11 证明包：\(\alpha<1\) 为 \(N^{1+\alpha}\) 漂移集中，\(\alpha=1\) 为带漂移扩散，\(\alpha>1\) 为公平扩散，并给出各区全矩极限 | 相变机制和 \(1/N\) 临界尺度已有上述先例；需按七项同构判据继续检索，并由独立概率论研究者复核全部三段证明 |
| 结构约束的 \(k=4,\ldots,50\) 快速经验代理和严格留出验证 | 冻结 v4 + 2,112 场景 | 多人 ruin 数值近似、机器学习/回归代理、独立复现实验 |
| 首次余额耗尽理论与多方支付通道协议语义的映射 | PCN/H-MPC 文献 + 本项目模型边界 | 真实流量、余额不足拒绝、随机金额、再平衡和物理时间 |
| 原子多超边路由诱导的相关网络首耗尽、三尺度漂移相图及全矩/独立代理边界的统一组合 | 本项目 12–14 合同/证明/评审包；Podiatchev et al. 2024 明确指出独立通道假设受多跳路由限制；2026-07-18 八项同构表在开放来源中未见完全同构结果 | MathSciNet/zbMATH/Scopus/WoS/CNKI 机构检索；独立概率论签核；T18 跨拓扑稳健性；真实流量映射 |

## 检索边界

本轮使用了作者/期刊页面、DOI 页面、arXiv 和引用链，重点覆盖关键词：
multi-player/N-player gambler's ruin、three/four tower、simplex random walk、
exit time、weak drift、diffusion limit、absorbing Markov chain、
random-selection pairwise game、harmonic measure、four-player ruin、
asymmetric play、convergence of moments，以及 small-drift/weak-asymmetry
phase transition。弱漂移结果的完全同构要求同时满足“成对单位转账、固定
一般 \(k\)、\(p_N=1+\eta/N\)、首次任一余额归零及矩极限”；相图检索还要求
覆盖同一中心偏置核、均分初值和 \(\alpha<1,=1,>1\) 三区。当前纳入来源尚未
找到这些条件全满足者，但 Barnett (1964) 的公开摘要不足以确认其转移核，
已列为 manual-needed。尚未完成
MathSciNet、zbMATH、Scopus/WoS 的穷尽式引用追踪，因此所有“未找到直接
先例”只能写为检索结论，不能写为全球首次声明。

逐篇模型比较、查询族与核验状态见
[近临界与非对称多人破产文献审计](near_critical_asymmetric_search_audit_2026-07-17.md)。
相图专门检索与逐篇七项判据比较见
[多项式漂移相图文献审计](polynomial_drift_phase_search_audit_2026-07-17.md)。

2026-07-18 的 PCN/超图/相关网络补充检索、来源失败记录和八项同构比较见
[相关超图网络先行工作补充审计](correlated_network_prior_art_update_2026-07-18.md)。
