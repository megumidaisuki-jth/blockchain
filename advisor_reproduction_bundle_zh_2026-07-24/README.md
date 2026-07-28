# 超图支付通道网络停止时间：导师复现包

本目录保存论文关键公式、定理证明文档、验证程序、实际输入数据、权威实验结果及 SHA-256 完整性清单。目标是让导师在不依赖原开发工作区、也不依赖人类专家签核的条件下，复查数学实现与计算证据。

## 一、最快复现方式

推荐使用 Python 3.10，并在本目录打开 PowerShell：

```powershell
python -m pip install -r requirements.txt
python run_reproduction.py --mode quick
python run_reproduction.py --mode full
```

也可直接运行 `RUN_QUICK_VALIDATION.ps1` 或 `RUN_FULL_VALIDATION.ps1`。快速验证检查基础漂移公式、最终公式、超边状态转移和离散高斯桥；完整验证自动发现全部测试，预期为 **113 项全部通过**。其中原始重放测试会从80个正式/复跑NPZ重新构造3,200个分块，核对发布CSV；T34 的 5 项测试另行核对触边—拒绝时间索引、策略提前失败和反向流恢复。每次运行的文本日志和 JSON 摘要写入 `reproduction_logs/`；测试可能生成的 `.tmp/`、缓存及日志不纳入静态清单，不会改变已封存结果。

只检查文件是否被改动：

```powershell
python verify_bundle_integrity.py
```

预期结尾为 `INTEGRITY PASS`。包级清单见 `BUNDLE_SHA256SUMS.txt`；各权威结果目录另有独立 `SHA256SUMS` 或 `SHA256SUMS.txt`。

## 二、公式—代码—证据索引

| 研究环节 | 主要代码 | 自动测试 | 证明/验收材料 |
|---|---|---|---|
| 单超边漂移、停止时间与边界公式 | `drift_experiments.py`、`drift_formula_final.py`、`run_experiments.py` | `test_drift.py`、`test_final_formula.py`、`test_hyperedge.py` | `outputs/researchwrite/hypergraph-stopping-time/07_weak_drift_proof_package.md`、`10_strong_drift_proof_package.md` |
| 相关超图网络状态转移与精确锚点 | `network_model.py`、`network_exact.py`、`network_simulation.py`、`network_phase_validation.py` | `test_network_model.py` | `13_correlated_network_proof_package.md`、`results/network/` |
| T12 正竞争定理 | `t12_positive_competition_validation.py` | `test_t12_positive_competition.py` | `17_t12_positive_competition_proof_and_validation.md`、`results/t12-positive-competition*/` |
| T18 跨拓扑结论 | `t18_cross_topology_validation.py` | `test_t18_cross_topology.py` | `16_key_proof_and_t18_validation_2026-07-18.md`、`results/t18-*/` |
| T19 离散高斯生存桥与符号机制 | `gaussian_discrete_bridge_validation.py` | `test_gaussian_discrete_bridge.py` | `21_gaussian_block_survival_theorem_and_sign_mechanism.md`、`27_discrete_gaussian_survival_bridge_theorem_2026-07-24.md`、`28a_t19_subagent_remediation_recheck_2026-07-24.md` |
| Lightning 历史/2026 真实拓扑映射 | `lightning_topology_mapping.py`、`lightning_real_topology_formal.py`、`lightning_current_2026_formal.py` | `test_lightning_topology_mapping.py` 等 | `18a_real_lightning_formal_results_2026-07-23.md`、`19a_current_2026_formal_results_2026-07-23.md` |
| 漂移插值与结构符号检验 | `lightning_drift_interpolation_*.py`、`lightning_structural_sign_analysis.py` | 对应 `test_lightning_*.py` | `26_drift_interpolation_formal_results_2026-07-24.md`、`results/lightning-drift-interpolation-*/` |
| T32真实拓扑符号机制闭合 | `lightning_sign_mechanism_closure.py` | `test_lightning_sign_mechanism_closure.py` | `32_sign_mechanism_closure_contract_2026-07-24.md`、`results/lightning-sign-mechanism-closure/` |
| T34停止事件—支付失败语义边界 | `stopping_event_mapping_validation.py` | `test_stopping_event_mapping_validation.py` | `34_stopping_event_real_payment_mapping_contract_2026-07-24.md`、`results/stopping-event-mapping-validation/` |

上述 Markdown 文件均位于 `outputs/researchwrite/hypergraph-stopping-time/`。总体证据索引见该目录的 `23_manuscript_ready_evidence_map_2026-07-23.md`，中文论文结构见 `29_chinese_manuscript_scope_and_structure_2026-07-24.md`。

## 三、输入数据

`data/` 保留了实际参与论文实验的输入：

- Lightning 历史快照：2020-10-14、2022-05-31、2023-07-16；
- Lightning 当前快照：2026 年 `channels-geo.json`；
- 原始数据说明和统计文件。

未收录未被正式验证调用的 562 MB 原始压缩归档，以避免复现包无意义膨胀。正式代码调用的解压后快照均已保留。所有论文图只保留 PNG，符合本项目的单一图片格式约定。

## 四、重新生成实验结果

封存的 `results/` 用于逐哈希核对。若要重新计算，请把输出写到 `reproduced_results/`，避免覆盖封存证据。例如：

```powershell
python gaussian_discrete_bridge_validation.py --output-dir reproduced_results/discrete-gaussian-bridge
python network_phase_validation.py --output-dir reproduced_results/network
```

各正式 Lightning 和 T12/T18 程序的参数可用 `python <脚本名> --help` 查看。正式蒙特卡洛计算耗时取决于 CPU；建议先运行完整单元测试，再按论文拟引用的结果目录逐项复算。独立种子复现实验与主实验结果已分别保留，便于比较。

## 五、正确理解验证结论

本包能证明的是：代码与封存证据一致；确定性公式、精确小规模锚点、性质测试和独立随机种子复算满足当前定理合同；截至封包时全套自动测试通过。它不把数值实验误表述为纯数学证明，也不替代导师对论文创新性、表述范围及投稿定位的学术判断。

复现环境记录见 `ENVIRONMENT.json`，原项目说明保存在 `PROJECT_README.md`。如包内任何静态文件被修改，应重新运行 `generate_bundle_manifest.py` 生成新清单，并记录修改原因与日期。
