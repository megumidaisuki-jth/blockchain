# 论文实验源码

本目录只收录《原子路由下超图支付通道网络的首次耗尽时间》当前稿件直接使用的实验代码和回归测试。历史探索脚本、被替代的试验方案、投稿文档生成工具和公式推导工具不属于本目录。

所有命令均应从仓库根目录 `E:\newblockchain` 执行。原始公开拓扑仍保存在 `data/raw/`，已归档数值结果仍保存在 `results/`，论文 PNG 图保存在 `outputs/researchwrite/hypergraph-stopping-time/figures/`；本目录集中管理源码，不复制大体积输入和结果。

## 实验与源码对应关系

| 论文实验 | 主要入口 | 共享实现/后处理 | 论文位置 |
|---|---|---|---|
| 有限状态 Poisson 方程 | `network_phase_validation.py` | `network_exact.py`、`network_model.py`、`network_topologies.py` | 表1、6.1节 |
| 漂移三分区 | `network_phase_scaling_closure.py` | `network_simulation.py`、`plot_phase_scaling_closure_figure.py` | 图1、5.4节、6.2节 |
| 高阶跨拓扑效应 | `higher_order_cross_topology.py` | `plot_higher_order_cross_topology.py` | 图2、5.3节、6.3节 |
| 离散—高斯桥接 | `gaussian_discrete_bridge_validation.py` | 脚本内含精确链、谱级数和绘图 | 图3、6.4节 |
| Lightning 历史/2026横截面 | `lightning_real_topology_formal.py`、`lightning_current_2026_formal.py` | `lightning_topology_mapping.py`、`lightning_mapping_simulation.py`、阶段比较与合并脚本 | 5.5节、5.6节、6.5节 |
| 需求集中度与符号反转 | `lightning_drift_interpolation_formal.py` | `lightning_drift_interpolation_comparison.py`、`lightning_sign_mechanism_closure.py` | 图4、6.6节 |
| 停止事件时间索引 | `stopping_event_mapping_validation.py` | 穷举核查 | 6.7节 |

`lightning_*_preflight.py` 保留了正式运行前的样本量和精度门设计；`lightning_*_comparison.py` 与 `lightning_pooled_sensitivity.py` 负责独立阶段比较及门限判断后的合并敏感性分析。`network_phase_validation.py` 同时提供多个实验复用的区块统计和独立代理函数。

## 环境

本次归档验证使用 Python 3.12，并采用 `requirements.txt` 中记录的科学计算库版本。安装示例：

```powershell
python -m pip install -r experiment\requirements.txt
```

## 一键回归

```powershell
D:\miniconda\python.exe experiment\run_tests.py
```

该命令首先核对 `inventory.json`，确保目录中没有未登记的实验源码，然后发现并运行 `experiment/tests/` 下的全部测试。发布结果的原始大样本计算耗时较长；回归测试只执行确定性检查、小规模精确锚点和已发布结果哈希核验。

## 输入与结果

- 历史 Lightning 输入：`data/raw/ln-geolocated-2019-2023/selected_snapshots/`
- 2026 Lightning 输入：`data/raw/mempool-lightning-2026-07-22/channels-geo.json`
- 数值结果：`results/network-phase-closure/`、`results/t18-*`、`results/discrete-gaussian-bridge/`、`results/lightning-*`、`results/stopping-event-mapping-validation/`
- 论文图：`outputs/researchwrite/hypergraph-stopping-time/figures/` 以及相应 `results/` 子目录中的 PNG

精确文件清单和对应论文用途见 `inventory.json`。
