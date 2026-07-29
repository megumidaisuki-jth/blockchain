# 超图支付通道网络首次耗尽时间研究

本仓库保存中文期刊论文《原子路由下超图支付通道网络的首次耗尽时间》的稿件、实验源码、公开拓扑输入、数值结果和复现记录。

## 当前版本

- 稿件：`outputs/researchwrite/hypergraph-stopping-time/manuscript/原子路由下超图支付通道网络的首次耗尽时间_通信学报格式_v0.7.1.docx`
- 发布标签：`manuscript-v0.7.1`
- 实验源码：`experiment/`
- 压缩稿：12 页，保留 5 个定理、24 个编号公式、4 幅 PNG 图和 30 条参考文献。

作者、单位、通信作者、基金、中图分类号和 DOI 仍为待填写项。

## 目录

- `experiment/`：论文当前版本直接使用的实验源码、依赖版本、文件清单和回归测试；这是实验代码的唯一活动入口。
- `data/raw/`：历史 Lightning 快照、2026 年过滤投影及来源说明。
- `results/`：实验的 NPZ/CSV/JSON 结果、运行元数据和 SHA-256 清单。
- `outputs/researchwrite/hypergraph-stopping-time/figures/`：论文使用的 PNG 图及输入审计。
- `outputs/researchwrite/hypergraph-stopping-time/manuscript/`：Markdown 源稿、Word 稿和质量检查记录。
- `advisor_reproduction_bundle_zh_2026-07-24/`：早期完整复现归档，仅作历史快照，不是当前实验代码入口。

## 实验回归

从仓库根目录执行：

```powershell
D:\miniconda\python.exe experiment\run_tests.py
```

实验环境与源码—论文对应关系见 `experiment/README.md`；精确文件清单见 `experiment/inventory.json`。

## 结论边界

严格数学结论限于稿件定义的固定拓扑、原子路由、单位增量和相应渐近条件。高阶跨拓扑与 Lightning 结果属于预设有限设计和公开拓扑上的计算证据，不外推为任意超图的统一生存序，也不用于估计现实 Lightning 支付成功率。
