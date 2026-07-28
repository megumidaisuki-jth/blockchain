# v4 系数来源只读复原记录

更新日期：2026-07-17

## 结论

冻结 v4 的 30 个系数可以从以下历史数据精确复原：

| 数据 | 场景数 | 用途 | SHA-256 |
|---|---:|---|---|
| `drift-calibration-data.csv` | 520 | 原校准集 | `decfef97a0fca4ec08414a25842d3abaf77a08db9d100cc0f217ca3ea429815b` |
| `drift-development-data.csv` | 270 | v2 后转入拟合 | `8559e1a247e464a98e24c2340bcc4117614c6633ab62f37aa634a7000f9f2962` |
| `drift-final-blind-results.csv` | 1,728 | v3 失败后转入开发 | `6a7d372d1f6a1ea112331a0a6d424c6b49033ad73b6fac7331819c2e2f2dd9fc` |

合计 2,518 个历史训练场景。使用 `drift_formula_search.py` 中现有的
`fit_neutral` 与 `fit_crossover_corrections`，以三份数据的并集重新拟合：

- `NEUTRAL` 最大绝对系数差：0；
- `NEGATIVE` 最大绝对系数差：0；
- `POSITIVE` 最大绝对系数差：0。

作为对照，只使用校准集与开发集会得到 v3 系数，不能复原 v4；加入第一轮
失败盲测后才逐位一致。这与“v3 未通过后转为开发数据、随后冻结 v4”的
叙述一致。

## 证据隔离

第二轮盲测 `drift-final-blind2-results.csv` 的 SHA-256 为
`aeebc03cb1db7d38ad76a14aea3bf9ce1eac9085b67b69b341a6b11d7ba2db9c`。
本次复原没有读取它作为拟合输入；第二轮盲测参数网格与上述三份历史训练
数据的参数点交集为 0。

## 代码指纹

- 历史搜索脚本：`abf607174519238600e3463a8c6f4e819f2a27acb2d0decaf9512d9395dc14c7`
- 冻结 v4 预测器：`fc6ed5692c5e33a9fffe770a3a11e12d0b94dbf5a1eec4c0ae7c81aee87c07d7`

## 限定

这是一次只读法证复原，不等同于已经完成可发布的一键训练链。仍需独立
脚本固定输入清单、模式校验、软件版本、输出参数与失败条件；在该脚本完成
前，方法可复现性只能标为“来源已定位、工程链未闭合”。

