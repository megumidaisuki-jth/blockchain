# 2026-07-18 相关网络先行工作补充审计 QA

## 结论

状态：**PASS（开放来源审计范围）**。

本状态表示：本轮开放来源检索、去重同构表、参考文献同步、文档一致性和代码回归均通过。它不表示 MathSciNet、zbMATH、Scopus、Web of Science、CNKI 已完成，也不表示论文具有“全球首次”新颖性或 publication-ready。

## 范围

- 主审计：`sources/correlated_network_prior_art_update_2026-07-18.md`
- 同步文件：`01_research_canon.md`、`02_evidence_table.md`、`sources/literature_claim_map_2026-07-17.md`、`sources/correlated_network_prior_art_audit_2026-07-17.md`、`sources/references.bib`、根目录 `README.md`
- 保护对象：未改动 `项目进展审计_超图支付通道停止时间_2026-07-17.html`，其视觉确认仍独立等待用户完成。

## 来源覆盖

通过作者/出版方页面或论文全文核验了以下直接边界：

- Shabgahi et al.：支付通道有效寿命和拓扑预测；
- Dehshali et al.：失衡前交易数与链下吞吐上限；
- Podiatchev–Orda–Rottenstreich：通道 stopping time、网络首通道失败及独立通道限制；
- Bai–Xu–Wang：交易等待时间的 first-passage，而非 depletion；
- Kim、Kotzer et al.、Corcoran–Lewis、Nainwal–Kamble–Awathare、Pickhardt：多方/超图支付通道及路径/协议/多面体边界；
- van Engelshoven–Roos、Horcrux、Sankagiri–Hajek：depletion 防护和长期控制边界；
- Denisov–Sakhanenko–Wachtel、Tzioufas、Patel–Carron–Bullo：三角阵 first-passage、全矩与乘积链方法边界。

失败/未覆盖来源已显式登记：Crossref 批量请求 `429`；Semantic Scholar API `429`；zbMATH API 有条款接受门；MathSciNet、Scopus、Web of Science、CNKI 无当前机构入口。未下载 Barnett（1964）全文，未接受 zbMATH API 条款。

## 结构化检查

执行日期：2026-07-18。

| 检查 | 结果 |
|---|---|
| 严格 UTF-8 读取 | 7/7 文件通过 |
| BibTeX 条目 | 45 条、45 个唯一键 |
| DOI | 40 个、40 个唯一 DOI |
| BibTeX 全局花括号平衡 | 0 |
| 本轮新增 BibTeX 键 | 9/9 存在 |
| 同构比较表 | 15 行；每行 10 列；C1–C8 仅含 `Y/P/N` |
| 本地 Markdown 链接 | 0 个失效链接 |
| 有界新颖性合同 | 通过：同时保留“已检索范围”“不支持全球首次”“机构库待核验” |
| 总门 | PASS |

## 回归测试

命令：

```powershell
python -m unittest discover -v
```

结果：`Ran 42 tests in 18.026s`，`OK`，即 42/42 通过。

## 文件哈希

| 文件 | 行数 | SHA-256 |
|---|---:|---|
| `README.md` | 67 | `31c33c3f6759928f368ae241b5ed5548a6aef17ea42cac49aa55e5ab54b993d4` |
| `01_research_canon.md` | 198 | `cb21613f6e87aba36b78c1037314a512a4665bc5babc3589aa386b8fe04b3d6e` |
| `02_evidence_table.md` | 34 | `747d2c0701805fba9139b5422fcff18d65f304a56055e89693d9515c59ff270b` |
| `sources/correlated_network_prior_art_audit_2026-07-17.md` | 79 | `3d957c59102d2c2be81a5085c4f84156e4e4a9d4ff0d68751d53252466d842e4` |
| `sources/correlated_network_prior_art_update_2026-07-18.md` | 139 | `38c01e1cb84f894975aec111b7ef34389d05bf2518781642d1595a858cf38bc6` |
| `sources/literature_claim_map_2026-07-17.md` | 58 | `6e58c2e946631120c979bade0daf2f30243f3da07718906d8824187f8e61ddef` |
| `sources/references.bib` | 484 | `f2e11c4d096fd418e816008680a68a8dab7eb0be34fc0fbfb4b076975a596131` |

## 保护对象与冻结数学证据

- 等待用户视觉确认的 HTML SHA-256 仍为 `babf45d3ee1ae1455dfbf8d6c6d78d05fb296b87fdec6aca2902dc4a9b4f88cb`。
- 五个冻结数学 CSV 的 SHA-256 保持为：
  - `network-correlated-vs-proxy.csv`: `08f7a5df559b9eee613fabff1f29375e9c40d50537e39668d19bbe370ff25dda`
  - `network-exact.csv`: `4a95eb7d31b4cfb6f397c721d5d7258520d468ed789b01b880e360c24d5984db`
  - `network-mc-exact-check.csv`: `bf1053d1f838d82eee15735a57041f2e01010eb10c904e8f6e42924f3e2b6aa4`
  - `network-phase-scaling.csv`: `774b47efb90a4de16503ca3bb6684c582375449534817e639e528c053db23b43`
  - `network-survival-curves.csv`: `6b4d12ecb3d90ff2e631b65ddcb50e6e9db8fa9beb58108d1e865370a27b680a`

因此本轮文献同步没有改变 Task 9 的视觉目标或冻结数学结果。

## 剩余门禁

1. MathSciNet/zbMATH/Scopus/WoS/CNKI 机构检索；
2. T16、T17A/B/C、T18a 独立概率论签核；
3. T18 重叠链、重叠星、随机连通超图稳健性；
4. 真实交易流量到外生、状态无关 i.i.d. 路由核的映射；
5. 稿件组装、目标期刊选择和格式化。
