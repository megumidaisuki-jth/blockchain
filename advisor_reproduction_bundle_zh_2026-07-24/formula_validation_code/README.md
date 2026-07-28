# Word公式独立验证

该目录用于复现论文 Markdown 公式到 Word 原生 OMML 的一致性检查，不依赖论文生成器内部状态。

检查范围包括：

- Markdown 显示公式与行内公式是否全部生成可编辑 `m:oMath`；
- 公式表是否使用单栏4580 DXA，且表宽、网格宽与单元格宽均为4080+500 DXA；
- 公式正文与编号单元格的上下左右边距是否均为0 DXA，避免较长编号（14a）换行或截断；
- 编号公式是否保持（1）—（14）、（14a）、（15）—（24）的顺序；
- 是否存在 `U+FFFD` 或残留 LaTeX 控制词；
- 式（3）的自由延拓记号、式（8）的中文字体隔离；
- 式（14）是否误用 `m:sepChr` 表示减号或比较符；
- 式（17）的乘积操作数是否完整；
- 式（23）的矩阵、分式与伸缩括号是否为真实 OMML 结构；
- 式（24）的 `9/8` 是否为真实分式。

在 `E:\newblockchain` 下运行：

```powershell
& 'C:\Users\jiate\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'E:\newblockchain\advisor_reproduction_bundle_zh_2026-07-24\formula_validation_code\audit_word_formulas.py' `
  --md 'E:\newblockchain\outputs\researchwrite\hypergraph-stopping-time\manuscript\相关超图支付通道网络的停止时间_通信学报格式_v0.5.md' `
  --docx 'E:\newblockchain\outputs\researchwrite\hypergraph-stopping-time\manuscript\相关超图支付通道网络的停止时间_通信学报格式_v0.5.docx' `
  --output 'E:\newblockchain\advisor_reproduction_bundle_zh_2026-07-24\formula_validation_code\formula_audit_v0.5.json'
```

退出码为0且报告状态为 `PASS` 才表示通过。该检查验证公式转换和结构语义，不替代数学证明审阅；数学证明另由冻结证明文档和实验复现门验证。
