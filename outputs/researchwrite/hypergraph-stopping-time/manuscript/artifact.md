# 模板执行合同

## Reference

- 原始模板：`E:\newblockchain\outputs\researchwrite\hypergraph-stopping-time\manuscript\《通信学报》官方正文模板_2026-04-20.doc`
- 原始模板 SHA-256：`DD866F0C567CB01B7B18A0A56EE7E19F96C1F1253D311A335DC421D9E50221DB`
- 转换参考：`E:\newblockchain\outputs\researchwrite\hypergraph-stopping-time\manuscript\《通信学报》官方正文模板_2026-04-20.docx`
- 转换参考 SHA-256：`1ECCCD5E654A241F81B77BE12621AF3F4DB3986D5DFE1FE5E8ACCC12B5FA554E`
- 页数：9；分节数：4；段落数（Word COM）：199；表格数：2。
- 结构证据：`.qa/template-style-evidence.json` 与本目录官方格式合同。
- 视觉证据说明：参考模板的 88 个旧式嵌入对象导致 Word/PDF 批量导出阻塞；原件不修改。最终稿不继承这些对象，必须对最终 DOCX 的全部页面逐页渲染检查。

## Page system

- A4 近似尺寸 8.27 in × 11.22 in，纵向。
- 左右边距 0.79 in；上下边距 0.95 in；页眉距边界约 49.6 pt；页脚距边界约 38.25 pt。
- 四个连续分节的栏数依次为 1、2、1、2；双栏间距 426 twip。
- 第一页与后续页页眉规则不同；正文页眉为“作者等：中文题名”。

## Typography and roles

- 中文题名：`Heading 1`；作者：`人名`；单位：`地名`。
- 中英文摘要、关键词、中图分类号、文献标志码和 DOI：`摘要`。
- 一级、二级、三级标题：`Heading 2`、`Heading 3` 及其派生层级。
- 正文：`Normal`；公式：`公式`；图题：`图注`；表题：`表题`；参考文献标题：`文献`；条目：`文献文`。
- 中文正文采用宋体五号；英文与数字采用 Times New Roman；公式采用 Cambria Math 或 Word 公式对象。

## Components and flow

1. 中文题名、作者、单位。
2. 中文摘要、关键词、中图分类号、文献标志码、DOI。
3. 英文题名、作者、单位、Abstract、Keywords。
4. 双栏正文，章节从“0 引言”开始。
5. 宽图表可置于连续单栏分节，随后恢复双栏。
6. 参考文献、作者简介与基金信息。

## Slot map

- 题名、摘要、关键词和正文全部重写。
- 作者、单位、基金、通信作者与作者简介保留显式占位符，不使用示例作者信息。
- DOI 留空；文献标志码固定为 A；中图分类号待核。
- 示例论文正文、图表、参考文献与嵌入对象全部移除。

## Fidelity gates

- 参考原件和转换参考的 SHA-256 必须保持不变。
- 最终文档必须保留 A4 页面、首节单栏、正文双栏和模板样式名称。
- 标题不超过 20 个汉字，中文摘要不超过 200 个汉字，关键词不少于 4 个。
- 所有图仅使用 PNG；图不能仅靠颜色区分；表格使用三线表。
- 最终稿逐页渲染为 PNG，检查遮挡、裁切、跨栏、表格和公式编号。
