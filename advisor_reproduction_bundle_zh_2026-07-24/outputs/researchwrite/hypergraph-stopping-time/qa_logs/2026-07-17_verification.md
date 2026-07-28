# 2026-07-17 交付核验记录

## 代码测试

- 命令：`python -m unittest -v`
- 结果：11 项测试全部通过，0 failure，运行时间 9.177 s。

## 研究文档完整性

- 8 个基础研究文件和 4 个核心输入文件均存在。
- `state.json` 可解析；当前模式为 `hybrid`，阶段为 `foundation_audit`。
- 主审计报告的 8 个必需一级内容板块均存在。
- 主报告中的 10 个本地链接全部解析到存在的文件。
- 项目交付目录的 Markdown/JSON 控制字符命中数为 0。
- 两处已修复的公式损坏模式（换页控制符、`a_0\(`）残留数均为 0。

## 验证结果复算

从 `results/drift-final-acceptance-results.csv` 重新读取 2,112 个场景并独立计算：

- 平均绝对相对误差：0.00680031347236104；
- 中位绝对相对误差：0.00511709126252033；
- 90% / 95% 分位绝对相对误差：0.0157553085571278 / 0.0190579838521729；
- 最大绝对相对误差：0.0383953811369129；
- RMS 相对误差：0.00917811448761293；
- 平均有符号相对误差：-0.00218906699542701；
- 点误差不超过 4% 的比例：1；
- Bonferroni-normal 不确定性上界不超过 5% 的比例：1；最大上界为 0.0499945556064577。

上述数值与 `drift-final-acceptance-summary.json` 逐项一致。

## SHA-256 指纹

- `drift_formula_final.py`: `fc6ed5692c5e33a9fffe770a3a11e12d0b94dbf5a1eec4c0ae7c81aee87c07d7`
- `independent_blind_validation.py`: `669071cdc8ac5972ca7bdb542e6360273f80287b3bca1b1b87de68c64eb6cb8c`
- `independent_precision_validation.py`: `49bc43e6fa248fed55e06405acd9658e21b28e031b0e09c93610c8b1fe1f514f`
- `independent_boundary_validation.py`: `7bd17439943bee509526fbdfe1d93ff9932f73ad9df6491b8f1f8ec4403671a0`
- `drift-final-blind2-results.csv`: `aeebc03cb1db7d38ad76a14aea3bf9ce1eac9085b67b69b341a6b11d7ba2db9c`
- `drift-final-precision-results.csv`: `0898691f63f8c6edc55ecc5e4a566593531721d91fdaabcd36f3beedde73850b`
- `drift-final-boundary-results.csv`: `18597e60ef546bac3e4a9a2dce76b1ec9d9ad2217fe29ba1a593a6cddb840619`
- `drift-final-acceptance-results.csv`: `3cdced29f35c5ee8c8fdcccca1c8f61d3e59d83049eaa29984632e3c2131d04e`

## 限定说明

本记录证明现有代码测试、交付文件与已保存统计汇总在当前工作区内一致；它不消除主报告中已登记的证明缺口、v4 拟合来源缺口或外部新颖性风险。
