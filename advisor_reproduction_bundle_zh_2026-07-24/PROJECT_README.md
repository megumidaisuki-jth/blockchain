# Correlated hypergraph payment-channel first-depletion study

本目录研究固定超图支付通道网络在外生随机多超边路由下的“首次余额耗尽时间”。内容包括严格随机过程模型、有限状态 Markov 精确解、相关扩散与漂移相图内部证明工作稿，以及可复现的独立 Monte Carlo 诊断。T12 已在固定整数 $k\ge3$、固定 $p\in(1,2]$ 的参数域内完成正漂移外围竞争的 $\sqrt N$ 极限、全固定正阶矩收敛和期望二阶修正的内部证明；T16 仅在显式有限状态耗尽可达性下内部闭合；T17A/B/C 在 formal fix 1 后内部闭合；T18a 仅在联合 Gaussian 扩散极限且跨超边协方差块为零时内部闭合。以上结论的外部概率论评审均未签署。T12 的 36 单元主实验、独立异种子复跑、Welch 同时区间与 9 个精确锚点均通过；这些有限网格结果只验证实现与有限样本一致性，不构成渐近定理的证明。T18-A 也已完成三类非同构拓扑、三种临界漂移、四个尺度的 36 单元正式实验、完整复跑、最弱单元 100,000 对区间敏感性和三拓扑精确锚点。真实 Lightning 映射的第一阶段已经取得并校验 336 快照公开数据集，冻结三个日期和六个 31 节点子图，生成 12 个真实拓扑/透明合成需求路由核；尚未运行停止时间正式实验，也不声称掌握真实支付流量或余额。Publication readiness 仍为 false；尚余外部概率审查、MathSciNet/zbMATH/Scopus/WoS/CNKI 机构检索、真实拓扑停止时间实验、稿件组装和目标期刊格式化等门禁。

独立通道/超边生存函数乘积是 Podiatchev–Orda–Rottenstreich (2024) 直接覆盖的基线；本项目只复现并用作相关网络对照。

Shabgahi 等（2022）已基于网络拓扑研究支付通道有效寿命，Podiatchev–Orda–Rottenstreich（2024）已定义 PCN stopping time 和网络首通道失败，Kotzer 等（2025）等工作已提出超图/多方支付通道。因此本项目不得声称“首次研究支付通道寿命/停止时间”或“首次提出超图支付通道”；候选贡献被收窄为“原子多超边路由诱导的相关性 + 网络首余额耗尽 + 多项式消失漂移相变 + 有界独立代理诊断”。

主要文件：

- [投稿就绪度与目标期刊策略（2026-07-18 权威进度基线）](outputs/researchwrite/hypergraph-stopping-time/15_submission_readiness_and_venue_strategy_2026-07-18.md)：更新后的研究基础 8.2/10 与投稿任务 71.75% 的计算依据，给出 TNSM 暂定路线、稿件蓝图和七项硬门禁；百分比不是录用概率。
- [T12 正漂移竞争二阶定理与验证](outputs/researchwrite/hypergraph-stopping-time/17_t12_positive_competition_proof_and_validation.md)：给出固定 $k,p$ 参数域内的严格证明链、全矩与期望展开，以及与证明分离的有限网格诊断；当前为内部闭合、外部评审未签署。
- [T12 最终 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-18_t12_positive_competition.md)：记录 RED→GREEN、全量回归、精确锚点、两轮正式运行、独立算术重算、manifest、保护哈希与尚未通过的门禁。
- [T12 精确锚点](results/t12-positive-competition-exact-anchors)、[正式主运行](results/t12-positive-competition)、[独立异种子复跑](results/t12-positive-competition-replication)与[复跑比较](results/t12-positive-competition-replication-comparison)：当前 T12 权威数值目录；36 单元有限网格和 9 个精确锚点只作实现与有限样本验证，不承担渐近证明。
- [真实 Lightning 拓扑映射合同](outputs/researchwrite/hypergraph-stopping-time/18_real_lightning_mapping_contract_2026-07-22.md)：冻结公开数据源、三个日期、两类确定性子图、透明需求、路由核和现实语义边界；明确真实拓扑不等于真实流量。
- [真实拓扑映射产物](results/lightning-real-topology-mapping)：包含 6 个子图、12 个核、186 个节点映射、202 个通道映射、11,304 条路由、metadata 和 SHA-256 manifest；尚未包含停止时间正式模拟。
- [真实 Lightning 映射第一阶段 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-22_real_lightning_mapping_stage1.md)：记录数据下载与断点续传、GML 大整数规范化、子图门禁修正、映射核、manifest 和 81 项回归。
- [关键证明与 T18 跨拓扑实验准确性报告](outputs/researchwrite/hypergraph-stopping-time/16_key_proof_and_t18_validation_2026-07-18.md)：临界互逆路由扰动引理、36 单元正式结果、两次逐字节复跑、最弱单元敏感性、三拓扑精确锚点以及可写/不可写边界。
- [关键证明与 T18 正式验证 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-18_key_proof_and_t18_validation.md)：记录测试驱动过程、旧随机种子同构缺陷、完整重跑、区间/哈希重算、57 项回归和未通过门禁。
- [T18 正式主效应](results/t18-cross-topology/t18-primary-effects.csv)、[核诊断](results/t18-cross-topology/t18-kernel-diagnostics.csv)、[完整复跑](results/t18-cross-topology-replication)、[最弱单元敏感性](results/t18-weakest-sensitivity/t18-weakest-cell-sensitivity.csv)与[精确锚点](results/t18-exact-anchors/t18-exact-anchors.csv)：当前 T18 权威数值入口；带 `rejected-seed20260718` 后缀的目录因随机拓扑与链形同构而只作纠错审计。
- [投稿就绪度与目标期刊策略 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-18_submission_readiness_and_venue_strategy.md)：记录评分算术、JSON/UTF-8、本地链接、官方期刊入口、冻结哈希和 42 项回归测试。
- [项目进展审计（2026-07-17）](outputs/researchwrite/hypergraph-stopping-time/exports/项目进展审计_超图支付通道停止时间_2026-07-17.md)：模型、证明、数值和先行工作纠偏的完整历史审计；对应 HTML 仍待用户视觉确认。
- [弱漂移证明包](outputs/researchwrite/hypergraph-stopping-time/07_weak_drift_proof_package.md)：固定 \(k\)、\(p_N=1+\eta/N\) 的过程、退出时间与全矩收敛定理工作稿；待外部独立概率论核查。
- [弱漂移内部对抗性审计](outputs/researchwrite/hypergraph-stopping-time/08_weak_drift_adversarial_audit.md)：逐环节重算 FCLT、退出映射、指数矩和 PDE 函数空间，并收窄先行工作边界。
- [弱漂移外部概率论评审包](outputs/researchwrite/hypergraph-stopping-time/09_weak_drift_external_review_packet.md)：R1–R12 签核表、反例压力测试和失败降级规则；尚未完成外部评审。
- [强漂移证明包](outputs/researchwrite/hypergraph-stopping-time/10_strong_drift_proof_package.md)：固定 \(p\ne1\) 下相对指数集中、统一指数矩与全部固定正阶矩收敛的工作稿；待独立概率论核查。
- [多项式消失漂移相图证明包](outputs/researchwrite/hypergraph-stopping-time/11_polynomial_drift_phase_diagram_proof_package.md)：统一 \(\alpha<1\) 漂移集中、\(\alpha=1\) 带漂移扩散和 \(\alpha>1\) 公平扩散；待独立概率论核查。
- [相关网络模型与定理合同](outputs/researchwrite/hypergraph-stopping-time/12_correlated_hypergraph_network_model_and_theorem_contract.md)：固定超图、外生 i.i.d. 路由和网络首次余额耗尽事件的模型边界。
- [T16–T18 相关网络证明包](outputs/researchwrite/hypergraph-stopping-time/13_correlated_network_proof_package.md)：T16、T17A/B/C 与 T18a 的内部闭合证明，以及 T18b 的严格/数值混合边界；外部评审未签署。
- [T16–T18 外部评审签核包](outputs/researchwrite/hypergraph-stopping-time/14_correlated_network_external_review_packet.md)：已更新为包含评审者资格、复算协议、T18 复现命令、权威哈希和逐项失败降级规则的当前交接入口；R01–R14 仍为 0/14、全部未签署，publication readiness 保持 false。
- [T16–T18 外部评审交接 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-18_external_probability_review_handoff.md)：记录 14 项空白状态、链接、哈希、受保护证据与状态字段检查；该内部 QA 不构成外部证明签核。
- [网络精确结果](results/network/network-exact.csv)、[相图诊断](results/network/network-phase-scaling.csv)、[相关模型—独立代理配对诊断](results/network/network-correlated-vs-proxy.csv)、[生存曲线](results/network/network-survival-curves.csv)、[运行元数据](results/network/network-run-metadata.json) 与 [SHA-256 清单](results/network/SHA256SUMS.txt)：Task 6 冻结证据入口；其中 `alpha=0.5` 有限网格不作为收敛验证。
- [近临界/非对称文献审计](outputs/researchwrite/hypergraph-stopping-time/sources/near_critical_asymmetric_search_audit_2026-07-17.md)：按四项模型同构判据比较 Barnett、Rocha–Stern、Tzioufas 等先例；Barnett 1964 全文仍是 P0 闸门。
- [Barnett 访问与引用链审计](outputs/researchwrite/hypergraph-stopping-time/sources/barnett_1964_access_and_citation_chain_audit_2026-07-17.md)：记录合法可用性、1963 方法前篇、双向引用链和当前不可判定边界；本轮未下载全文。
- [多项式漂移相图文献审计](outputs/researchwrite/hypergraph-stopping-time/sources/polynomial_drift_phase_search_audit_2026-07-17.md)：核查一维弱不对称、小漂移 first-passage transition 和区间退出先例，约束相图的新颖性措辞。
- [相关网络先行工作补充审计](outputs/researchwrite/hypergraph-stopping-time/sources/correlated_network_prior_art_update_2026-07-18.md)：记录开放来源检索覆盖/失败、八项同构判据、15 项去重比较表和收窄后的投稿贡献合同；机构数据库闸门仍未通过。
- [TNSM 直接近邻稿件形态审计](outputs/researchwrite/hypergraph-stopping-time/sources/tnsm_near_neighbor_manuscript_shape_audit_2026-07-18.md)：核验两篇直接先例的 14–15 页正式形态、理论—管理—真实 LN 数据组合，并把暂定主文预算修订为 12–14 页。
- [TNSM 直接近邻稿件形态审计 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-18_tnsm_near_neighbor_manuscript_shape_audit.md)：记录来源降级、版本去重、页数/费用算术、BibTeX 补全、边界检查、冻结哈希和完整回归。
- [相关网络先行工作补充审计 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-18_correlated_network_prior_art_update.md)：记录 UTF-8、BibTeX/DOI 去重、同构表、本地链接、42 项回归测试和冻结证据哈希。
- [本轮弱漂移 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-17_weak_drift_adversarial_audit.md)：记录 11 项测试、一步矩枚举、引文边界和文档一致性检查。
- [外部评审包与文献审计 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-17_external_review_packet_and_literature_audit.md)：记录本轮来源核验、24 条 BibTeX、11 项测试和 HTML/链接检查。
- [强漂移与 Barnett 访问 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-17_strong_drift_and_barnett_access_audit.md)：记录逐式数学核验、27 条 BibTeX、11 项测试、链接/渲染检查和未通过闸门。
- [多项式漂移相图 QA](outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-17_polynomial_drift_phase_diagram_qa.md)：记录三分区证明复算、精确 \(k=2\) 尺度校验、小漂移先例边界、31 条 BibTeX、测试与渲染检查。
- [k3至50漂移公式_最终验证报告.md](k3至50漂移公式_最终验证报告.md)：冻结 v4 公式、适用域、2112 场景最终验收和误差解释。
- [含漂移超边停止时间_严格推导.md](含漂移超边停止时间_严格推导.md)：一般流量矩阵、中心偏置模型、扩散 PDE 与强弱漂移渐近推导。
- [drift_formula_final.py](drift_formula_final.py)：最终可执行预测器；`k=3` 使用已知三人 gambler's-ruin 模型的精确 Markov 解，`k>=4` 使用冻结近似。
- [independent_blind_validation.py](independent_blind_validation.py)：不调用生产仿真器的独立盲测实现。
- [results/drift-final-acceptance-results.csv](results/drift-final-acceptance-results.csv)：最终保守口径下全部 2112 个验证场景。
- [results/drift-final-acceptance-summary.json](results/drift-final-acceptance-summary.json)：最终验收汇总与审计哈希。
- [figures/fig7-k3-50-blind-validation.png](figures/fig7-k3-50-blind-validation.png)：最终误差图。

## 运行

依赖 Python 3.10+、NumPy、SciPy、matplotlib。

```powershell
$env:TEMP='E:\newblockchain\.tmp'
$env:TMP='E:\newblockchain\.tmp'
python test_final_formula.py
python independent_blind_validation.py
python plot_final_validation.py
```

相关网络证明与证据包的复现命令：

```powershell
python -m unittest test_network_model -v
python network_phase_validation.py --quick --output results/network-quick
python network_phase_validation.py --output results/network
node render_research_html.mjs "outputs/researchwrite/hypergraph-stopping-time/exports/项目进展审计_超图支付通道停止时间_2026-07-17.md" "项目进展审计_超图支付通道停止时间_2026-07-17.html" "超图支付通道停止时间研究：项目进展审计与论文推进路线"
```

公式的声明参数域为

\[
3\leq k\leq50,\qquad
10\leq N=C/(k\sigma)\leq128,\qquad
0.30\leq p_{\mathrm{bias}}\leq1.90.
\]

这里的旧冻结 v4 停止时间按单超边内成功发生的单位交易次数计数；变量支付额、非中心偏置和初始余额不均匀不在该公式的已验证范围内。相关网络结果另以一次多超边路由为一个原子网络步，停止事件始终是首个超边—参与者余额坐标到零，不等同于支付失败、通道关闭或网络断连。
