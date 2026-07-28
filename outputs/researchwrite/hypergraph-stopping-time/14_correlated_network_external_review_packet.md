# T16–T18 相关网络证明独立评审签核包

更新日期：2026-07-18  
材料状态：**unsigned / 全部未签署**  
Publication readiness: **false**

本签核包供未参与当前推导的概率论研究者独立复算。每一节必须单独选择 `Yes / No`、填写 reviewer，并签名及注明日期；任何空白均不等于通过。只有全部 14 节均选择 `Yes` 且分别签署后，证明包才可以进入下一轮稿件提升；签署本包也不替代更广的文献新颖性检索或期刊同行评审。

## 评审者资格与执行协议

### 资格

评审者应满足：未参与 T16–T18 的原始推导、formal fix、证明包撰写、实验代码实现或当前 QA。若评审者曾对其中某一部分提供实质推导意见，应在签名旁披露，并由另一名独立评审者复核相应条目。

### 必读材料

1. [模型与定理合同](12_correlated_hypergraph_network_model_and_theorem_contract.md)；
2. [T16–T18 完整证明包](13_correlated_network_proof_package.md)；
3. [关键证明与 T18 准确性报告](16_key_proof_and_t18_validation_2026-07-18.md)；
4. [T18 实现](../../../t18_cross_topology_validation.py)与[回归测试](../../../test_t18_cross_topology.py)；
5. [三拓扑精确锚点](../../../results/t18-exact-anchors/t18-exact-anchors.csv)、[正式 T18 主效应](../../../results/t18-cross-topology/t18-primary-effects.csv)和[最弱单元敏感性](../../../results/t18-weakest-sensitivity/t18-weakest-cell-sensitivity.csv)。

### 复算原则

- 证明条目必须独立重建关键不等式或极限定理条件；只运行测试不能替代数学复算。
- 数值条目应至少重算 CSV、manifest、区间端点和一个精确锚点；仅检查屏幕截图不算通过。
- `Yes` 表示该条目在明确假设下成立且主张未越界；`No` 必须写明失败的最小步骤、反例或缺失条件。
- 若结论仅需增加条件即可成立，应先选 `No`，记录建议条件，待证明包修订后重新签署。
- 评审者不需要评价期刊选择、录用概率或“全球首次”；这些不属于本包范围。

### 最小复现命令

```powershell
python -m unittest -v
python t18_cross_topology_validation.py --output results/t18-cross-topology-independent-check
python t18_cross_topology_validation.py --output results/t18-exact-anchors-independent-check --exact-anchors --anchor-scale 2 --anchor-repetitions 100000
python t18_cross_topology_validation.py --output results/t18-weakest-sensitivity-independent-check --weakest-only --sensitivity-repetitions 100000 --sensitivity-blocks 100
```

第一条命令是最低代码门禁；后三条会重新生成大量随机实验，评审者可先核查已冻结 CSV 与哈希，再在计算资源允许时完整复跑。独立复跑应写入新目录，不能覆盖权威结果。

### 当前权威校验值

| 文件 | SHA-256 |
|---|---|
| `t18_cross_topology_validation.py` | `2d9cf6ebeb80819ab11f843a48d27ddd5d9a596b7da520be3ad47f9445c90765` |
| `test_t18_cross_topology.py` | `69ad388a263c28f326702d682014cf8dfa184bd658d05878fe279557c271e049` |
| `t18-primary-effects.csv` | `d9436daa71457d3f6c58cf02767b0204a178177a9f8d4367eec94a57d6ecd234` |
| `t18-kernel-diagnostics.csv` | `38779a494c53b824410894c7f5d8c11beca79be74001154fe82cbfa03d160808` |
| `t18-weakest-cell-sensitivity.csv` | `0b3009f557758bc392ef5a097234c3cd68bc08420d53bea15f800bb16b5abf79` |
| `t18-exact-anchors.csv` | `b9ada3e30ca5ea82e1d5bc4683f0370570c22a610868f2bfc36b8879bf54734d` |

## R01 — Model semantics / 模型语义

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §§1.1–1.2；`12_correlated_hypergraph_network_model_and_theorem_contract.md`, §§3–5；`network_model.py::route_increment`。
- **Review test:** 单位简单路由是否在每个被使用超边内恰减一、加一，并且网络首次余额耗尽时间是否始终只表示首个余额坐标等于零。
- **Failure action:** 选择 `No` 时，冻结 T16–T18 的全部稿件提升；先修正状态、路由或停止量定义，再从 R01 重新评审。

## R02 — Reachability / 有限状态耗尽可达性

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** [证明包 §2](13_correlated_network_proof_package.md)的“内部转移可执行”“正概率路径”和 §2.1；`network_exact.py::build_transient_matrix`；[旧两超边精确结果](../../../results/network/network-exact.csv)；[三类四超边 $N=2$ 精确锚点](../../../results/t18-exact-anchors/t18-exact-anchors.csv)。
- **Review test:** 正概率路由词是否从每个内部状态给出实际可执行的边界路径，反向搜索是否只被表述为给定有限输入的证书，以及三个 10,000 状态锚点的 `all_states_reach_boundary=True` 是否没有被错误推广为所有 $N$/所有拓扑自动可达。
- **Failure action:** 选择 `No` 时，将 T16 降为已枚举实例的计算结论，并禁止从协方差非退化推断有限状态吸收。

## R03 — Spectral argument / 谱论证

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §2 的“排除闭合内部类并得到定量收缩”及“吸收、Poisson 方程和唯一性”。
- **Review test:** $Q_N^{L_N}\mathbf1\le(1-\delta_N)\mathbf1$ 是否推出 $Q_N^m\to0$、$\rho(Q_N)<1$、Neumann 逆、Poisson 方程和唯一性。
- **Failure action:** 选择 `No` 时，撤回 T16 的谱半径、Neumann 级数和一般 Poisson 唯一性陈述，只保留经残差核验的有限线性求解结果。

## R04 — Early tail / 早尾

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §3.1。
- **Review test:** $g_\varepsilon>0$ 的定义是否同时覆盖正、零、负极限漂移坐标；初态与漂移收敛余项是否都进入大 $N$ 余量；最大型 Azuma 的常数和有限坐标并集是否正确。
- **Failure action:** 选择 `No` 时，把 T17A 降为 concentration conjecture，并删除早尾指数率及其矩推论。

## R05 — Late tail / 晚尾

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §§3.2–3.3。
- **Review test:** 达到 $\theta_*$ 的固定负漂移坐标是否给出晚时确定性负余量，以及 $m_r=\lfloor rt_{N,*}\rfloor$ 上的尾界常数是否对所有充分大 $N$ 一致。
- **Failure action:** 选择 `No` 时，把 T17A 降为 concentration conjecture；不得用有限时间窗模拟替代长尾证明。

## R06 — Exponential moments / 指数矩

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §§3.3、5.3。
- **Review test:** 漂移主导区的归一化整数块尾和，以及扩散尺度的强 Markov 几何块，是否分别给出 $N$ 一致的正指数矩；由此到任意固定正阶矩的一致可积性是否成立。
- **Failure action:** 选择 `No` 时，保留已经单独通过的概率或分布收敛，但删除全部未经一致可积性支持的矩收敛陈述。

## R07 — FCLT / 函数型中心极限定理

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §4.1。
- **Review test:** 三角阵列中心化、有界增量 Lindeberg 条件、协方差和、紧性及 $N\mathbf d_N$ 确定性项是否在 $N^2$ 时钟上正确处理。
- **Failure action:** 选择 `No` 时，撤回 T17B/C 的过程极限、退出极限和矩极限，直到 FCLT 被重新证明。

## R08 — Tangent-space covariance / 切空间协方差

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §§1.2、4.1、5.2；`network_model.py::build_kernel` 和 `validate_phase_kernel`。
- **Review test:** 逐超边守恒是否把过程限制在乘积切空间；$\Gamma$ 在环境空间奇异是否被正确允许；逐面 $\Gamma_{ii}>0$ 是否足以支持后续法向论证和 $\operatorname{tr}\Gamma>0$。
- **Failure action:** 选择 `No` 时，撤回所有依赖该协方差条件的退出映射和势函数结论，并明确列出所需的更强非退化假设。

## R09 — Single-face crossing / 单面穿越

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §§4.2–4.3。
- **Review test:** 在任一选定 active face 上，强 Markov 后的一维正方差 Brownian 法向是否从零在任意短区间内取负值，并使退出泛函满足上半连续所需的穿越条件。
- **Failure action:** 选择 `No` 时，只保留第 4.1 节的过程收敛；T17B/C 的退出时间收敛标为 unresolved。

## R10 — Multi-face crossing / 多面同时触边

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §4.3 的有限 active set 论证。
- **Review test:** 同时首次命中多个面时，是否可以在不假设法向独立的情况下，对有限 active set 的每个坐标使用强 Markov 和概率一穿越事件，并满足退出映射连续性。
- **Failure action:** 选择 `No` 时，只保留过程收敛；所有退出时间和退出时间矩收敛均标为 unresolved。

## R11 — Critical mean bound / 临界非零漂移均值界

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §5.1。
- **Review test:** $\alpha=1,\boldsymbol\beta\ne0$ 时是否选到负坐标；对 $m\wedge\tau_N^{\mathrm{net}}$ 的可选停止是否有界且可积；零 overshoot 和坐标非负性是否给出全状态 $O(N^2)$ 界。
- **Failure action:** 选择 `No` 时，保留临界过程及退出分布结论，但删除非零临界漂移下的指数矩和全部矩收敛。

## R12 — Vanishing-drift potential / 零或消失漂移势函数

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** `13_correlated_network_proof_package.md`, §5.2。
- **Review test:** 逐边重心、$C_VN^2$ 最大值、$L N$ 的一范数界、$\mathbb E\|\xi\|^2$ 的统一正下界及 $N\|d_N\|_\infty=o(1)$ 扰动是否全部对状态一致。
- **Failure action:** 选择 `No` 时，删除 $\alpha=1,\boldsymbol\beta=0$ 与 $\alpha>1$ 的统一均值、指数矩及矩收敛，只保留已经通过的过程/分布层结论。

## R13 — T18 Gaussian independence / T18 高斯独立性

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** [证明包 §§6–7.1](13_correlated_network_proof_package.md)；`test_network_model.py` 的冻结两超边核检查；[T18 核诊断](../../../results/t18-cross-topology/t18-kernel-diagnostics.csv)、[正式主效应](../../../results/t18-cross-topology/t18-primary-effects.csv)和[敏感性结果](../../../results/t18-weakest-sensitivity/t18-weakest-cell-sensitivity.csv)。
- **Review test:** （i）跨超边零协方差块加联合 Gaussian 性是否推出路径块独立及生存函数乘积；（ii）互逆路由 $\pm a/N$ 扰动是否精确满足 $Nd_N^{(s)}=2sa\zeta$ 及 $\Gamma_N^{(s)}=\Gamma_0-d_N^{(s)}d_N^{(s)\mathsf T}$；（iii）非零跨块是否只证明增量律非因子化；（iv）36/36 正区间是否始终保持“冻结有限网格上的数值结论”，没有被改写成任意拓扑的统一符号定理。
- **Failure action:** 选择 `No` 时，按失败子项撤回 T18a 因子化、临界扰动桥接引理或 T18b 相应数值陈述；不得把非零协方差或 36 个全正单元改写成统一误差符号。

## R14 — Claim/literature boundary / 主张与文献边界

- **Yes / No:** ☐ Yes　☐ No
- **Reviewer:** ______________________________
- **Signature / date:** ______________________________
- **Evidence location:** [证明包 §§0、7–9](13_correlated_network_proof_package.md)；[关键准确性报告](16_key_proof_and_t18_validation_2026-07-18.md)；`sources/correlated_network_prior_art_audit_2026-07-17.md`；正式 T18 metadata/manifest；三个带 `rejected-seed20260718` 后缀的纠错审计目录。
- **Review test:** 标准吸收链、FCLT、Azuma 和 Gaussian 独立是否未被包装为方法创新；独立通道、超图 PCN 和原子结算先行工作是否被承认；独立代理是否未被称为真实路由流量；36 单元结果是否未被称为普遍排序定理；原随机种子与链形同构的问题是否被公开记录并从权威证据排除；Barnett 正文是否未被假装核验。
- **Failure action:** 选择 `No` 时，阻止论文提升，收缩或删除越界主张，并在完成合法全文核查和更广检索后重新签署本节。

---

**Final gate:** 本文件在 2026-07-18 更新后仍没有任何 reviewer、signature 或 date。上方所有方框均为空；这表示 **0/14 通过**，而不是“默认通过”。只要任一节未选择 `Yes`、未填写 reviewer 或未签署日期，`publication_readiness` 就保持 **false**，证明材料继续保持 internal proof draft 状态。
