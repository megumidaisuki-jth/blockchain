# Evidence table

| Claim | Evidence/source | Strength | Usable section | Risk | Status |
|---|---|---|---|---|---|
| (k=2) 均分无漂移时 \(\mathbb E\tau=N^2\) | 赌徒破产递推；2024 PCN 文献；Markov 测试 | 强 | Background / baseline | 非原创 | evidence-backed |
| (k=3) 均匀流量下 \(\mathbb E_{x,y,z}\tau=3xyz/(x+y+z)\) | Engel 1993；Bruss et al. 2003；Alabert et al. 2004；本项目复推、Markov 与 MC | 强 | Background / validation baseline | 明确非原创 | evidence-backed |
| 任意给定 \(\Pi\) 下 \(\tau\) 有几何尾且 \((I-Q)u=\mathbf1\) 有唯一有限解 | Swan & Bruss 2006；Marfil & David 2024；本项目吸收引理、残差 | 强 | Methods / implementation | Markov 形式非原创；本项目几何界很松但充分 | evidence-backed |
| 公平随机选对、单位转移的多人首次破产模型 | Sobel & Frankowski 2002；O’Connor & Saloff-Coste 2023 | 强 | Background / model provenance | 模型、四人案例和 simplex/Brownian 路线均非原创 | evidence-backed |
| 非对称一般 \(n\) 人首次破产与其矩已有先例 | Rocha & Stern 1999/2004；Hashemiparast & Sabzevari 2011；Sabzevari 2018；Phetpradap & Sripanitan 2025 | 强 | Related work / novelty boundary | 这些文献采用一名赢家从所有对手收款的规则，不可误写成与本项目成对转账同构 | evidence-backed |
| 多维退出时间的所有 \(p\)-阶矩极限已有先例 | Tzioufas 2019；另见 Kmet & Petkovšek 2002 | 强 | Related work / method provenance | 几何为 \(L_\infty\) 球/多货币高维游走，不是守恒单纯形；排除“全矩方法本身新颖” | evidence-backed |
| Barnett 1964 是否覆盖三人成对非对称特例 | Cambridge/JSTOR 书目页、OpenAlex OA 状态、Barnett 1963 方法前篇与双向引用链；访问审计文件 | 弱 | Novelty gate | 未发现 OA 副本；受控全文入口未测试；公开材料无完整转移核，必须全文人工核验 | manual-needed |
| 零漂移平方势函数恒等式与严格界 | 生成元直接计算；单元测试与 MC | 强 | Main theorem | 可能是标准技巧，创新有限 | evidence-backed |
| 中心偏置的正负漂移结构不对称 | 合法联合概率模型直接计算 | 强 | Model / Results | 依赖中心偏置模型 | evidence-backed |
| 固定 \(k\)、\(p_N=1+\eta/N\) 下 \(\tau_N/N^2\) 收敛且全部固定正阶矩收敛 | 三角阵列 FCLT；运行最小值连续集；全状态均值界 + 强 Markov 几何尾与统一指数矩；变分 PDE；07 证明包、08 内部对抗性审计与 09 可选评审合同 | 强（内部工作稿证明） | Asymptotics theorem | 全矩现象在不同模型已有先例；本项目只可主张模型特定组合，且须保留 Barnett 全文闸门；人类专家签核已取消为硬门 | evidence-backed-internal |
| 固定负漂移下 \(\tau_N/t_-^*\) 指数集中于 1，且全部固定正阶矩收敛 | 自由延拓；最大型 Azuma–Hoeffding 早尾界；单负漂移坐标晚尾界；统一指数矩；10 证明包；MC | 强（内部工作稿证明） | Asymptotics theorem | 待独立概率论核查；集中方法本身是标准工具 | evidence-backed-internal |
| 固定正漂移下 \(\tau_N/t_+^*\) 指数集中于 1，且全部固定正阶矩收敛 | 自由延拓；坐标并集早尾界；任一外围负漂移坐标晚尾界；统一指数矩；10 证明包；MC | 强（内部工作稿证明） | Asymptotics theorem | 一阶定理不含 \(N^{-1/2}\) 竞争修正；待独立概率论核查 | evidence-backed-internal |
| \(p_N=1+\eta N^{-\alpha}\) 的三分区相图：\(\alpha<1\) 确定性集中、\(\alpha=1\) 带漂移扩散、\(\alpha>1\) 公平扩散，且各区全矩收敛 | 07、10 与 11 证明包；\(\alpha>1\) 小漂移势函数统一界；\(k=2\) 精确 Markov 尺度校验 | 强（内部工作稿证明） | Main asymptotic theorem | \(1/N\) 弱不对称、小漂移 transition、FCLT 和全矩现象均有先例；只可主张模型特定统一组合，待独立复核 | evidence-backed-internal |
| 固定 \(k\ge3\)、固定 \(p\in(1,2]\) 时，正漂移存在 \(N^{-1/2}\) 的 \((k-1)\) 节点竞争分布极限、全部固定正阶绝对矩收敛和二阶均值修正 | [17 T12 证明包](17_t12_positive_competition_proof_and_validation.md)：一步协方差、确定时刻多元 CLT、正反向局部最大界、缩放退出时间紧性、严格穿越、中心指数小概率界、两段尾 UI、Gaussian 差分投影；Task 5 精确锚点、正式第一轮和独立复跑只作有限网格诊断 | 强（内部工作稿证明） | Asymptotics theorem | 只覆盖固定 \(k,p\)；有限网格不证明渐近定理；人类专家签核不再是硬门 | evidence-backed-internal |
| 冻结 v4 在声明离散网格上误差小于预设点误差阈值 | 2,112 场景、独立验证器、哈希、复算 | 强（离散网格经验） | Numerical method | 不是连续域误差定理 | evidence-backed |
| 全部同时误差上界低于 5% | Bonferroni-normal 计算 | 中 | Supplement | 对区间方法敏感；t 敏感性未全通过 | evidence-backed |
| v4 的历史训练来源和损失可逐位复原冻结系数 | 2,518 个历史点的只读重拟合；30 个系数逐位一致 | 中强 | Methods / provenance | 独立脚本、清单和外部时间戳仍缺 | plausible-inference |
| 独立通道/超边生存函数乘积是 Podiatchev–Orda–Rottenstreich (2024) 直接覆盖的基线；本项目只复现并用作相关网络对照。 | Podiatchev–Orda–Rottenstreich 2024；尾和恒等式 | 强 | Background / correlated-network control | 不得列为项目贡献，也不得推广到相关路由 | evidence-backed-prior-baseline |
| 支付通道有效寿命、拓扑—寿命关系、通道 stopping time 与网络首通道失败均已有直接先例 | Shabgahi et al. 2022；Dehshali et al. 2022；Podiatchev–Orda–Rottenstreich 2024 | 强 | Related work / novelty boundary | 不得声称首次研究 PCN lifetime、depletion 或 stopping time | evidence-backed-prior-baseline |
| 超图/多方支付通道、超图余额路径规划和跨超边原子协议语义均已有先例 | Kim 2023；Kotzer et al. 2025；Corcoran–Lewis 2025；Nainwal–Kamble–Awathare 2026 | 强 | Related work / novelty boundary | 不得声称首次提出超图 PCN、多方通道或跨超边支付 | evidence-backed-prior-baseline |
| Podiatchev et al. 的独立通道网络模型明确承认多跳支付会同时影响多个通道，故通道不相关假设不合理 | Podiatchev–Orda–Rottenstreich 2024 全文第 III 节、独立网络计算后的限制说明 | 强 | Introduction / problem gap | 只证明相关性问题有直接文献动机，不自动证明本项目新颖 | evidence-backed-gap |
| 已核验开放来源中未发现同时满足固定超图、原子多超边 i.i.d. 路由、相关首耗尽、三尺度漂移、乘积单纯形退出和全矩/代理诊断的直接同构工作 | `sources/correlated_network_prior_art_update_2026-07-18.md` 的八项判据与 15 项去重表 | 中强（受来源覆盖限制） | Introduction / contributions | MathSciNet/zbMATH/Scopus/WoS/CNKI 未完成；只能写“已检索范围内未发现”，不能写“全球首次” | bounded-negative-search |
| T16：相关网络有限状态吸收与 Poisson 方程 | 13 证明包；Task 6 精确残差与全状态可达性门 | 强（内部闭合） | Network exact theory | 显式假设有限状态耗尽可达性；不得称已同行评审 | A — internally closed and code-reproducible |
| T17：相关网络多项式漂移三分区及全部固定正阶矩 | 合同 12 第 6 节；13 证明包；formal fix 1 | 强（内部闭合） | Network asymptotics | 数值相图仅为诊断；`alpha=0.5` 有限网格不稳定，不能作为收敛验证 | A — all proof modules internally closed after fix 1 |
| T18a：零跨超边协方差块下的扩散级独立聚合 | 13 证明包的联合 Gaussian 块独立证明 | 强（内部闭合） | Network diffusion baseline | 只适用于联合 Gaussian 极限；一般非 Gaussian 零协方差不足 | A — internally closed and code-reproducible |
| T18b：冻结相关核非因子化与独立代理误差诊断 | 冻结跨块协方差；Task 6 配对 MC、精确基线与哈希 | 混合：精确 + 离散数值 | Network diagnostics | 正配对差只属于冻结拓扑/需求/代理；无普遍符号定理 | E — no universal sign theorem |
| T19：零漂移平衡二元通道的离散相关模型与独立边际代理收敛到各自 Gaussian 退出时间，具有全矩收敛，且极限相关停止时间随机不短于独立代理 | 27 证明包的双 FCLT、退出映射、统一指数尾和 Gaussian 相关不等式；三节点路径确定性 Poisson 解与独立 Brownian 谱级数；28/28a 独立子Agent验收 | 强（内部闭合） | Network asymptotics / sign mechanism | 只保证极限非负序；\(N=1\) 有明确负差反例；非平衡、非零漂移和高阶超边不覆盖 | A — internally closed, independent subagent ACCEPT |
| T32：冻结真实拓扑上需求不平衡轴解释有限尺度混合符号 | 两阶段80单元、3,200分块、80唯一种子；五重/八重/四重同时区间；正式与独立复跑输入清单；`results/lightning-sign-mechanism-closure/` | 中强（后验机制综合） | Real-topology mechanism results | 只有4个日期；概率插值同时改变漂移、协方差和高阶矩；不是普遍符号定理或仅漂移因果识别 | evidence-backed-bounded-mechanism |
| T34：模型首次触边与真实支付失败严格非等价；理想单位合同中的触边支付仍被接受，余额拒绝若发生严格更晚，但协议/策略可更早失败，替代路径或反向流可使成功延后 | 定义性证明；BOLT #2/#4/#7；Pickhardt et al. 2021、Tikhomirov et al. 2020；139,968 条小状态序列穷举零索引违例及三类反例 | 强（语义/索引合同） | Model / limitations | 不是交易级真实失败校准；公开拓扑缺余额、尝试、失败码和重试日志 | evidence-backed-semantic-boundary |
| Task 6 网络证据包可复现 | `results/network` 五个 CSV、metadata 与 SHA-256 清单；Task 6 独立只读复算 | 强（冻结证据） | Methods / validation | 精确生存序列化有机器精度归一化债务，最终 QA 必须清除 | evidence-backed |
| v6 对称闭式、非均匀推广和 \(\mathcal O(k^{-1/2})\) 定理成立 | 旧技术文档 | 弱/冲突 | 不可用 | 模型与新推导矛盾 | unsupported |

写作启动门禁为 `PASS_WITH_PARALLEL_GATES`，publication readiness 仍为 false：人类专家签核已由作者取消为硬门；T34 已关闭现实停止事件语义映射，仍需机构数据库新颖性审计、Barnett（1964）全文边界、完整中文稿件和目标期刊格式化。T32已闭合冻结真实拓扑上的有限网格符号机制，但不提供普遍符号定理。
