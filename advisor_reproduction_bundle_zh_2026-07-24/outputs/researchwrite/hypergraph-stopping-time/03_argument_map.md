# Argument map

## Scientific tension

- What is known: 双边支付通道的余额耗尽可由一维赌徒破产描述；公平多人
  随机选对首次破产、三人闭式、四人 Poisson/谱渐近、有限域
  harmonic measure、非对称一般 \(n\) 人首次破产、不同几何/更新规则下
  的全矩结果和一般吸收 Markov 计算已有概率论先例；支付通道有效寿命、
  网络首通道 stopping time、超图 PCN、多方通道和跨超边协议语义也已有
  直接先例。
- What is unknown: Podiatchev–Orda–Rottenstreich 已明确指出多跳支付同时影响多个通道，使其独立通道网络假设不合理；在该公开缺口下，固定超图原子路由相关过程的首耗尽相图能否通过未参与推导者的独立概率论复核，T18 的相关误差是否跨拓扑/漂移稳健，以及真实路由流量和状态依赖机制如何改变结论，仍未解决。
- Why the gap matters: 独立通道模型无法量化同一多跳支付对多个余额块的联合风险；如果相关性显著改变首耗尽分布，容量配置、路由与再平衡决策就不能只依赖逐通道边际寿命。

## Central research question

在给定固定超图、外生多超边路由分布、容量和初始余额下，网络首次余额耗尽时间的期望与分布如何精确表述、渐近刻画，并如何诊断独立边代理的相关性误差？

## Central thesis

固定超图支付通道网络的首次余额耗尽是相关有界路由增量在乘积单纯形上的首次出界问题；本项目以先行工作的独立聚合作为对照，在显式有限状态耗尽可达性下内部闭合 T16，并在合同 12 的固定维外生路由条件下内部闭合 T17A/B/C 与 T18a。T18b 只把冻结增量律非因子化写为严格结论，把配对停止时间差写为数值观察；证明均属于内部工作稿且未经过同行评审，人类专家签核已由作者取消为硬门。

## Supporting arguments

独立通道/超边生存函数乘积是 Podiatchev–Orda–Rottenstreich (2024) 直接覆盖的基线；本项目只复现并用作相关网络对照。

### Argument 1 — literature-anchored exact baseline
- Claim: 给定合法流量矩阵，期望停止时间由标准有限状态吸收 Markov/
  Poisson 方程唯一确定；本项目将其严格实例化为支付通道基准。
- Evidence: Swan–Bruss 与 Marfil–David 先例；一步条件化、稀疏线性系统、
  机器精度残差、与 Monte Carlo 一致。
- Limitation: 方程形式非原创，且状态空间随 (k,N) 组合爆炸。

### Argument 2 — known low-dimensional checks and finite-capacity bounds
- Claim: 已知 (k=2,3) 闭式提供解析校验；任意固定 (k) 的势函数与
  负漂移坐标给出有限容量界和后续尾控制。
- Evidence: Engel、Bruss et al.、Alabert et al.、Sobel–Frankowski、
  O’Connor–Saloff-Coste；本项目平方势函数、确定性测试与可选停止推导。
- Limitation: 低维闭式、公平选对模型和四人 simplex 路线均非原创；
  零漂移界不能直接移植到一般含漂移模型。

### Argument 3 — drift creates asymmetric regimes
- Claim: 对 \(p_N=1+\eta N^{-\alpha}\)，中心偏置模型由
  \(\mathrm{Pe}_N=|\eta|N^{1-\alpha}\) 控制：\(\alpha<1\) 是正负
  不对称的确定性集中区，\(\alpha=1\) 是带漂移单纯形扩散区，
  \(\alpha>1\) 回到公平扩散区；三个区间均闭合全部固定正阶矩。
- Evidence: 弱漂移四引理证明包与内部对抗性审计；漂移/协方差直接计算；漂移上界；
  强漂移自由延拓、早晚尾界与统一指数矩；\(\alpha>1\) 的小漂移势函数
  统一界；\(k=2\) 精确 Markov 尺度校验。
- Limitation: \(1/N\) 弱不对称、小漂移 transition、FCLT 和全矩现象均有
  一维或不同几何先例；07、10、11 均待外部独立复核。Barnett 1964 未发现
  OA 副本且受控全文尚未核验；正漂移二阶误差和现实流量校准未完成。

### Argument 4 — fast empirical surrogate
- Claim: 结构约束下的冻结 v4 近似可在声明离散参数网格内以低误差预测期望停止时间。
- Evidence: 无重合主盲测网格、独立模拟器、2,112 场景复算。
- Limitation: 公式拟合生成链缺失；统计阈值依赖 normal 近似；连续域与域外没有保证。

### Argument 5 — correlated-network exact closure

- Claim: 在显式有限状态耗尽可达性下，相关网络内部状态没有闭合非吸收类，且 \((I-Q_N)u_N=\mathbf1\) 唯一确定网络首次余额耗尽均值。
- Evidence: 13 证明包 T16；Task 6 在 \(N=1,2,3\) 的精确残差与全状态可达性门。
- Status/limitation: A — internally closed and code-reproducible；有限网格证书不替代所有 \(N\) 的可达性假设，人类专家签核不再是项目硬门。

### Argument 6 — correlated-network phase limits

- Claim: T17A/B/C 在 formal fix 1 后内部闭合漂移主导集中、临界相关扩散退出、零漂移扩散退出及全部固定正阶矩。
- Evidence: 合同 12 第 6 节；13 证明包的早晚尾、FCLT、单面/多面穿越和统一指数矩模块。
- Status/limitation: A — all proof modules internally closed after fix 1；Task 6 相图数值只作描述性诊断，`alpha=0.5` 有限网格不足以验证收敛。

### Argument 7 — independence boundary and dependence diagnostic

- Claim: 联合 Gaussian 极限中，零跨超边协方差块足以推出块独立；冻结两三元超边核则给出精确非因子化实例。
- Evidence: 13 证明包 T18a；Task 6 冻结跨块协方差、配对 MC 与精确基线。
- Status/limitation: T18a 为 A — internally closed and code-reproducible；T18b 为 E / mixed，冻结配对差没有普遍符号。

### Argument 8 — bounded novelty position

- Claim: 截至 2026-07-18 已核验的开放来源中，尚未发现同时覆盖固定超图、原子多超边外生 i.i.d. 路由、跨块相关性、网络首耗尽、三尺度漂移相变、乘积单纯形退出及全矩/代理诊断的直接同构论文。
- Evidence: `sources/correlated_network_prior_art_update_2026-07-18.md` 的八项同构判据、15 项去重表和来源失败记录。
- Status/limitation: 只属于有界阴性检索；MathSciNet、zbMATH、Scopus、Web of Science 与 CNKI 机构检索未完成，不支持“全球首次”。

### Argument 9 — centered Gaussian survival order and discrete bridge

- Claim: 对平衡零漂移固定二元通道网络，相关原子路由模型和独立通道边际代理分别收敛到保持边际协方差的高斯退出时间；退出映射连续性和统一指数矩允许均值通过极限，高斯相关不等式给出极限相关停止时间的非负随机序。
- Evidence: 21 的中心高斯块生存序；27 的 T19 双 FCLT、逐面立即穿越、平方势函数和强 Markov 几何尾；三节点路径 \(N=1\)–256 确定性 Poisson 解及独立 Brownian 谱级数。
- Status/limitation: A — internally closed, independent subagent ACCEPT；0 个阻断问题，5 项非阻断补救后 5/5 关闭；人类专家签核不再是项目门；只保证极限非负序，\(N=1\) 存在精确负差反例，非中心初态、非零漂移和三元以上超边不覆盖。

### Argument 10 — bounded real-topology sign mechanism

- Claim: 在八个冻结 Lightning 拓扑锚点、固定路由集合和固定增量支持下，从均匀需求向热点需求移动会系统性压低相关模型相对独立边际代理的标准化停止时间效应，并解释有限网格中的均匀正号—热点负号分离。
- Evidence: T32合同；正式与独立复跑共80单元、3,200分块、80个不相交阶段种子；λ=0五重同时区间为正，λ=0.5和λ=1为负；八锚点固定平均斜率区间严格为负；中文PNG及6项哈希产物。
- Status/limitation: evidence-backed bounded mechanism；这是已知正式/复跑结果的后验机制综合。四日期精确符号翻转 `p=0.125`，不得写成一般时间总体显著性；概率插值也改变协方差和高阶矩，不是“仅漂移”因果识别。

## Counterarguments / alternative explanations

- 这些结果可能只是标准吸收 Markov 链理论的直接应用，数学新颖性不足。
- 弱漂移定理虽正确，但 FCLT、连续映射、统一尾界和 Feynman–Kac 的
  组合可能被审稿人视为标准扩散逼近，而非独立数学突破。
- Tzioufas 2019 与 Phetpradap–Sripanitan 2025 表明“全矩”本身不足以构成
  创新；Barnett 1964 若包含同构三人转移核，还会进一步压缩低维差异。
- “超图”仍可能被视为表示语言；当前工作虽已引入一次路由同时更新多边的跨块协方差并闭合冻结真实拓扑的需求插值机制，但机构数据库检索和审稿中的新颖性判断仍决定其是否构成足够强的网络贡献。
- 中心偏置是人为设定，不能代表真实路由流量。
- 经验公式的高精度可能来自密集训练/相邻插值，而非理论泛化。
- 首次余额为零不一定对应实际支付失败或通道寿命。

## Final move

把第一篇中文论文定位为“固定相关支付通道网络的首次余额耗尽”：已知通道寿命、独立聚合、超图支付通道和标准吸收链只作基线；T16、T17A/B/C、T18a 与 T19 作为内部闭合且代码可复现的证明工作稿，T18b 作为有边界的依赖诊断，T32作为冻结真实拓扑的有限网格机制证据，T34负责触边与真实支付失败的严格非等价边界。人类专家签核已由作者取消为硬门；可以开始期刊中立中文初稿，publication readiness 仍需机构数据库确认、Barnett（1964）全文边界、完整中文稿件和期刊格式化。
