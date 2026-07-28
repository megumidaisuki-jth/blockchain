# 2026-07-18 TNSM 直接近邻稿件形态审计 QA

## 结论

状态：**PASS（目标期刊近邻稿件形态审计范围）**。

本状态表示两篇直接 TNSM 先例的身份、正式卷期页码、版本族、稿件结构和本项目差距已得到多源核验，相关 BibTeX 与投稿进度基线同步通过。它不表示 TNSM 已由作者最终确认、页费已获批准、T18 已运行、机构数据库已检索、外部证明已签核或稿件已经可以投稿。`publication_readiness = false`。

## 产物与同步文件

- 主审计：[TNSM 直接近邻论文形态审计](../sources/tnsm_near_neighbor_manuscript_shape_audit_2026-07-18.md)
- 投稿基线：[投稿就绪度与目标期刊策略](../15_submission_readiness_and_venue_strategy_2026-07-18.md)
- 书目库：[references.bib](../sources/references.bib)
- 机器状态：[state.json](../state.json)
- 索引与进度：根目录 `README.md`、`.superpowers/sdd/progress.md`

## 来源路线

核验日期：2026-07-18。

1. academic-search MCP 当前未挂载，已明确记录工具不可用；
2. 按 `nature-academic-search` 的 T1→T2→T3 规则，使用技能自带 OpenAlex 公共 API 脚本作发现检索；
3. 用 Crossref DOI API 核验题名、作者、期刊、卷、期和页码；
4. 用 [TNSM 官方范围/索引入口](https://www.comsoc.org/publications/journals/ieee-transactions-network-and-service-management)、[TNSM searchable index](https://www.tnsm-overview.org/search) 和 [TNSM 投稿政策](https://www.comsoc.org/publications/journals/ieee-tnsm/policies-guidelines)核验期刊身份和页数政策；
5. 用 [Podiatchev 作者版本全文](https://eprint.iacr.org/2024/1393.pdf)、[Kotzer ePrint 元数据页](https://eprint.iacr.org/2025/205)和 [Technion 机构记录](https://cris.technion.ac.il/en/publications/survivable-payment-channel-networks-2/)核验摘要、结构、真实 LN 数据和版本关系。

## 查询与结果

在 `year >= 2022` 下运行四个查询：

1. `payment channel networks network service management`
2. `hypergraph payment channel networks`
3. `survivable payment channel networks`
4. `blockchain network service management payment channel`

查询 1、4 噪声较大；查询 2、3 命中直接工作。按 DOI 和“标准化题名 + 第一作者”去重后，正式 TNSM 核心集合为 2 篇：

| 工作 | 正式元数据 | 页数 |
|---|---|---:|
| Podiatchev–Orda–Rottenstreich, *Survivable Payment Channel Networks* | 21(6):6218–6232；[DOI](https://doi.org/10.1109/TNSM.2024.3456229) | 15 |
| Kotzer–Ladóczki–Tapolcai–Rottenstreich, *Addressing Scalability Issues of Blockchains With Hypergraph Payment Networks* | 22(3):2427–2440；[DOI](https://doi.org/10.1109/TNSM.2025.3542960) | 14 |

Podiatchev 的 COMSNETS 会议版和 Kotzer 的 IACR ePrint 版属于版本族，不重复计为独立 TNSM 论文。正式期刊记录优先。

## 来源失败与处理

- 第一次 OpenAlex 降级命令的 PowerShell 引号被拆分；改用单变量传参后解决。
- 一次结果输出因 Windows GBK 不能表示作者名字符而中止；设置 `PYTHONUTF8=1` 后四个查询均成功。
- IACR 2025/205 PDF 的一次直接打开受 robots 限制；未用不明镜像替代，而是以搜索索引中的 PDF 文本、ePrint 元数据、Crossref 正式元数据和 TNSM 卷期页交叉核验。
- 两个宽查询精度低，因此审计只声称“两篇最直接先例”，不声称穷尽所有 TNSM 区块链论文。

## 结构与结论核验

| 检查 | 结果 |
|---|---|
| Podiatchev 正式页数 | `6232 - 6218 + 1 = 15`，PASS |
| Kotzer 正式页数 | `2440 - 2427 + 1 = 14`，PASS |
| Podiatchev 稿件结构 | 全文核验 Introduction、停止时间、通道集合、容量优化、分布式优化、特定拓扑、Related Work、Conclusion/Discussion |
| Kotzer 稿件结构 | 引言核验背景/related work、成本、拓扑设计、真实 LN 评价、结论组织 |
| 现实数据 | 两篇均含 LN 拓扑/快照证据 |
| 管理动作 | 容量再分配；超图拓扑构造 |
| 本项目主要缺口 | 真实需求映射和可执行容量/路由/代理选择规则 |
| 适用边界 | 不把两篇推广为所有 TNSM 论文的最低页数 |

## 页费算术

按 TNSM 当前“10 页免费，超出每页 220 美元，最多 16 页”的政策：

| 总页数 | 超页数 | 强制页费 |
|---:|---:|---:|
| 12 | 2 | 440 美元 |
| 13 | 3 | 660 美元 |
| 14 | 4 | 880 美元 |
| 15 | 5 | 1,100 美元 |
| 16 | 6 | 1,320 美元 |

全部满足 `(总页数 - 10) × 220`。这些金额不含可选 OA，且政策必须在真正投稿前复核。

## 书目核验

- BibTeX 条目：45；唯一键：45；
- DOI：40；唯一 DOI：40；
- 全局花括号平衡：0；
- `KotzerEtAl2025Hypergraph` 已补齐：`volume = 22`、`number = 3`、`pages = 2427--2440`；
- 字段来自 Crossref DOI `10.1109/TNSM.2025.3542960`，与 TNSM 2025 年第 3 期目录一致。

## 投稿进度算术

- “目标期刊与投稿合规”模块从 35% 提高到 45%；
- 该模块权重为 5%，加权贡献从 1.75% 提高到 2.25%；
- 总完成度从 59.50% 提高到 `60.00%`；
- `state.json` 继续以整数 `60` 展示；
- 主文明确说明 60.0% 不是论文质量或录用概率。

## 结构化 QA

| 检查 | 结果 |
|---|---|
| 严格 UTF-8 | 6/6 本轮核心文件通过 |
| `state.json` | 解析通过，`publication_readiness = false` |
| 投稿加权表 | 8/8 行逐行算术通过，总计 60.00% |
| 本地 Markdown 链接 | 0 个失效链接 |
| 页数与页费 | 2 个正式页数、5 个费用点全部通过 |
| 范围边界 | 同时保留“不是全球新颖性检索”“不支持一般化”“机构库待检索” |
| 冻结保护对象 | HTML + 五个数学 CSV，6/6 哈希通过 |

## 回归测试

命令：

```powershell
python -m unittest discover -v
```

最终索引变更后的复验结果：`Ran 42 tests in 18.640s`，`OK`，即 42/42 通过。

## 本轮文件哈希

| 文件 | 行数 | SHA-256 |
|---|---:|---|
| `README.md` | 71 | `ee8e61723b3cfcf32941d5ed7eb1ecc439919308a4d61995150ec557c8df3cc7` |
| `.superpowers/sdd/progress.md` | 51 | `0c755ca90fa2a193af8bead478b4508268d6d72317885932cd2012e1b6748d09` |
| `15_submission_readiness_and_venue_strategy_2026-07-18.md` | 212 | `7dfad0ff7b7c3038261ce83fd23fe123c948274dd49b130a252a9dade111e279` |
| `state.json` | 41 | `abaaacdf25b441c36ce8659a98dc44d907b50dde30b91951359be35151fcf78f` |
| `sources/references.bib` | 487 | `7df97beac6f0b304104a0fa089910dc6e3b378d39ffd23519875d7d3e05312b1` |
| `sources/tnsm_near_neighbor_manuscript_shape_audit_2026-07-18.md` | 171 | `ef7cbbf2bdcbfc029ffbfa719af5f4846a39b1d816afdf97f2c3d5fd314efd43` |

## 保护对象哈希

- `项目进展审计_超图支付通道停止时间_2026-07-17.html`：`babf45d3ee1ae1455dfbf8d6c6d78d05fb296b87fdec6aca2902dc4a9b4f88cb`
- `network-correlated-vs-proxy.csv`：`08f7a5df559b9eee613fabff1f29375e9c40d50537e39668d19bbe370ff25dda`
- `network-exact.csv`：`4a95eb7d31b4cfb6f397c721d5d7258520d468ed789b01b880e360c24d5984db`
- `network-mc-exact-check.csv`：`bf1053d1f838d82eee15735a57041f2e01010eb10c904e8f6e42924f3e2b6aa4`
- `network-phase-scaling.csv`：`774b47efb90a4de16503ca3bb6684c582375449534817e639e528c053db23b43`
- `network-survival-curves.csv`：`6b4d12ecb3d90ff2e631b65ddcb50e6e9db8fa9beb58108d1e865370a27b680a`

## 仍未闭合的门禁

1. 作者尚未批准 R1/R2/R3 页数—费用路线；
2. T18 A/B/C 正式设计尚未获批和运行；
3. R01–R14 外部概率论签核未完成；
4. MathSciNet/zbMATH/Scopus/WoS/CNKI 机构检索未完成；
5. 真实 LN 需求映射和网络管理判断规则未形成；
6. 完整英文稿件、作者 ORCID/元数据和投稿包不存在；
7. 冻结 HTML 仍待用户视觉确认。

因此，本轮只证明“目标期刊形态判断更可靠、页数建议需要上调”，不证明项目已经可以投稿。
