# 三分区有限尺度实验门禁报告

- 实验：`network-phase-closure-20260728`
- 总体：PASS
- 生成时间（UTC）：2026-07-28T03:20:11Z

| 门禁 | 结果 | 观测值 | 判据 |
|---|---|---|---|
| `deterministic_implementation` | PASS | `0` | all deterministic cell gates pass |
| `zero_censoring_nan_exclusion` | PASS | `{"censored":0,"excluded":0,"nan":0}` | all three counts equal zero |
| `precision_primary` | PASS | `0.02738425467061486` | maximum 20-cell simultaneous normalized half-width <= 0.03 |
| `precision_replication` | PASS | `0.024211119483128266` | maximum 20-cell simultaneous normalized half-width <= 0.03 |
| `independent_stage_agreement` | PASS | `0` | all 20 Bonferroni-Welch intervals contain zero |
| `final_slope_primary_zero` | PASS | `{"half_width":0.016227062795044822,"point":2.0101271435682158}` | point in [1.9,2.1] and simultaneous half-width <= 0.10 |
| `final_slope_primary_drift` | PASS | `{"half_width":0.004183676230201994,"point":1.5159621847142257}` | point in [1.4,1.65] and simultaneous half-width <= 0.10 |
| `final_slope_primary_critical` | PASS | `{"half_width":0.014117863210068249,"point":2.0053604642017455}` | point in [1.9,2.1] and simultaneous half-width <= 0.10 |
| `final_slope_primary_fair` | PASS | `{"half_width":0.017540193812413674,"point":2.008202008728244}` | point in [1.9,2.1] and simultaneous half-width <= 0.10 |
| `final_slope_replication_zero` | PASS | `{"half_width":0.01619616669008983,"point":1.9938031370834115}` | point in [1.9,2.1] and simultaneous half-width <= 0.10 |
| `final_slope_replication_drift` | PASS | `{"half_width":0.0035514110455151515,"point":1.5185768475312573}` | point in [1.4,1.65] and simultaneous half-width <= 0.10 |
| `final_slope_replication_critical` | PASS | `{"half_width":0.012711643543186657,"point":1.9879985122830568}` | point in [1.9,2.1] and simultaneous half-width <= 0.10 |
| `final_slope_replication_fair` | PASS | `{"half_width":0.015635159337629267,"point":2.0010035596219726}` | point in [1.9,2.1] and simultaneous half-width <= 0.10 |
| `plateau_ratio_primary_zero` | PASS | `1.0236666700651607` | last-three normalized maximum/minimum <= 1.1 |
| `plateau_ratio_primary_drift` | PASS | `1.0223749331238816` | last-three normalized maximum/minimum <= 1.2 |
| `plateau_ratio_primary_critical` | PASS | `1.0087031764419865` | last-three normalized maximum/minimum <= 1.1 |
| `plateau_ratio_primary_fair` | PASS | `1.0192123439790084` | last-three normalized maximum/minimum <= 1.1 |
| `drift_center_primary` | PASS | `0.945227146875` | N=1600 normalized drift mean in [0.80,1.05] |
| `drift_concentration_primary` | PASS | `0.006875` | N=1600 probability of >30% relative deviation <= 0.25 |
| `fair_to_zero_primary` | PASS | `0.005226520312500038` | absolute normalized mean difference at N=400 <= 0.03 |
| `plateau_ratio_replication_zero` | PASS | `1.0127246523562448` | last-three normalized maximum/minimum <= 1.1 |
| `plateau_ratio_replication_drift` | PASS | `1.0260874519962166` | last-three normalized maximum/minimum <= 1.2 |
| `plateau_ratio_replication_critical` | PASS | `1.016776770304057` | last-three normalized maximum/minimum <= 1.1 |
| `plateau_ratio_replication_fair` | PASS | `1.0023266407774127` | last-three normalized maximum/minimum <= 1.1 |
| `drift_center_replication` | PASS | `0.9486553015625001` | N=1600 normalized drift mean in [0.80,1.05] |
| `drift_concentration_replication` | PASS | `0.007` | N=1600 probability of >30% relative deviation <= 0.25 |
| `fair_to_zero_replication` | PASS | `0.0048580765625000355` | absolute normalized mean difference at N=400 <= 0.03 |

失败门禁不等同于数学定理失败；它只限制该有限网格可支持的数值表述。
