# 2026-07-18 投稿就绪度与目标期刊策略 QA

## 结论

状态：**PASS（项目进度与期刊策略基线范围）**。

本状态只表示进度量化、基础文件同步、期刊入口核验和项目内回归通过。它不表示论文已经完成、定理已经外部评审、机构数据库已经检索、T18 已经运行、目标期刊已经由作者最终确认或论文具有任何特定录用概率。`publication_readiness` 保持 `false`。

## 本轮产物

- 主产物：[投稿就绪度与目标期刊策略](../15_submission_readiness_and_venue_strategy_2026-07-18.md)
- 同步文件：[范围](../00_scope.md)、[论证图](../03_argument_map.md)、[章节合同](../04_section_contracts.md)、[定理缺口登记](../06_theorem_proof_gap_register.md)、[机器状态](../state.json)、根目录 `README.md`、`.superpowers/sdd/progress.md`
- 保护对象：未修改 2026-07-17 HTML 和五个冻结数学 CSV；未启动 T18 正式实验；未下载 Barnett（1964）全文或补充材料。

## 指标算术核验

### 研究基础成熟度

八项基础文件评分为：`8.5, 8.3, 8.4, 8.0, 7.4, 7.0, 9.2, 7.2`。

- 合计：`64.0`
- 算术平均：`64.0 / 8 = 8.0`
- 与 `state.json -> scores.overall`：一致
- 适用范围：foundation files only；当前没有完整 manuscript draft

### 投稿任务完成度

逐模块加权贡献为：

`15.00 + 17.00 + 13.50 + 9.75 + 2.00 + 0.00 + 0.50 + 1.75 = 59.50`。

- 公开表格逐行满足 `权重 × 模块完成率 = 加权贡献`
- 权重合计：`100%`
- 精确合计：`59.50%`
- `state.json` 的整数展示：`60%`，与四舍五入一致
- 语义门：主文明确说明该值不是论文质量分数或录用概率

### 期刊启发式评分

按 `30% / 25% / 20% / 15% / 10%` 权重重算四个候选：

| 期刊 | 文档展示 | 重算结果 | 状态 |
|---|---:|---:|---|
| IEEE Transactions on Network and Service Management | 4.44 | 4.435 → 4.44 | PASS |
| IEEE Transactions on Networking | 3.94 | 3.935 → 3.94 | PASS |
| AAP/JAP | 3.74 | 3.740 → 3.74 | PASS |
| Queueing Systems | 3.60 | 3.595 → 3.60 | PASS |

这些分数只对当前稿件形态做决策支持，不是对期刊质量、声望或录用难度的排名。

## 官方期刊入口核验

核验日期：2026-07-18。

1. [TNSM 官方范围](https://www.comsoc.org/publications/journals/ieee-transactions-network-and-service-management)：理论和应用网络/服务管理贡献；可靠性、性能、可扩展性和优化属于明确相关方向。
2. [TNSM 政策与指南](https://www.comsoc.org/publications/journals/ieee-tnsm/policies-guidelines)：要求 related work/novelty；10 页以内免页费、超过 10 页每页 220 美元、最多 16 页；2026 可选 OA 列示 2,800 美元。
3. [IEEE Transactions on Networking 政策与指南](https://www.comsoc.org/publications/journals/ieee-tnet/policies-guidelines)：当前官方刊名和典型 16 页上限得到核验。
4. [AAP/JAP 作者说明](https://www.cambridge.org/core/journals/advances-in-applied-probability/information/author-instructions)：提交在 JAP/AAP 间统筹；JAP 研究论文通常不超过 25 个印刷页，AAP 可接收更长应用概率研究。
5. [Queueing Systems 官方范围](https://link.springer.com/journal/11134/aims-and-scope)：概率论、网络资源共享、稀缺资源竞争、极端事件和仿真方法属于范围。

网页政策可能变化；真正投稿前必须再次读取官方页面，不能仅依赖本 QA 的 2026-07-18 快照。

## 结构化检查

| 检查 | 结果 |
|---|---|
| 严格 UTF-8 | 7/7 本轮核心文件通过 |
| `state.json` | 解析通过 |
| 基础评分算术 | 8.0，一致 |
| 投稿完成度算术 | 59.50%，状态展示 60%，一致 |
| 期刊加权评分 | 4/4 通过 |
| 官方期刊 URL | 5/5 存在于主产物 |
| 本地 Markdown 链接 | 0 个失效链接 |
| 旧 Task 9 序列化债务措辞 | 权威文件中 0 处 |
| 状态边界 | 保留 `publication_readiness = false` 与“不是录用概率” |
| 保护哈希 | HTML + 五个 CSV，6/6 通过 |

说明：首轮内联检查中的中文文字门使用 PowerShell 管道时发生字符传输歧义；校验器改用 Unicode 转义后通过。该问题属于检查脚本文字编码，不是项目文件编码错误；项目文件严格 UTF-8 检查始终通过。

## 回归测试

命令：

```powershell
python -m unittest discover -v
```

最终变更后的复验结果：`Ran 42 tests in 18.139s`，`OK`，即 42/42 通过。

## 本轮文件哈希

| 文件 | 行数 | SHA-256 |
|---|---:|---|
| `README.md` | 69 | `3e900f847ce6d266353588f98c3f5498764226fdabe2432f8c8015dc962b0093` |
| `.superpowers/sdd/progress.md` | 40 | `d294bb960862c66b912821e1d0d52e22c498b64155635c7376f9faec4b1f9601` |
| `00_scope.md` | 39 | `6fdd6304bdb2db759084bfd0bb4879460bde3d171c56d41fdefa4b4e7556db92` |
| `03_argument_map.md` | 96 | `946e3aaa292f7bb8f144619a8bb66c1a6250001d5b0d1815631e981317d08576` |
| `04_section_contracts.md` | 102 | `a4195ffb092a545bf7daf65e90d3aac0b61d9c86e397877efb157383e024e521` |
| `06_theorem_proof_gap_register.md` | 210 | `fa65dbabd321d1dec02d6fc87923c0891c386ef111379373f6d485d0518cc9bf` |
| `state.json` | 41 | `18ecf77cae929dd65995799c0f4bd66b4ff42eeb9367ae91deeba6e80451dd5f` |
| `15_submission_readiness_and_venue_strategy_2026-07-18.md` | 210 | `56c3c384fcce24979e60a457222dcaa2a7d8efd086283972df1c32a3b2954908` |

## 保护对象哈希

- `项目进展审计_超图支付通道停止时间_2026-07-17.html`：`babf45d3ee1ae1455dfbf8d6c6d78d05fb296b87fdec6aca2902dc4a9b4f88cb`
- `network-correlated-vs-proxy.csv`：`08f7a5df559b9eee613fabff1f29375e9c40d50537e39668d19bbe370ff25dda`
- `network-exact.csv`：`4a95eb7d31b4cfb6f397c721d5d7258520d468ed789b01b880e360c24d5984db`
- `network-mc-exact-check.csv`：`bf1053d1f838d82eee15735a57041f2e01010eb10c904e8f6e42924f3e2b6aa4`
- `network-phase-scaling.csv`：`774b47efb90a4de16503ca3bb6684c582375449534817e639e528c053db23b43`
- `network-survival-curves.csv`：`6b4d12ecb3d90ff2e631b65ddcb50e6e9db8fa9beb58108d1e865370a27b680a`

## 仍未通过的投稿门禁

1. T18 A/B/C 正式设计尚未获用户批准，实验未运行；
2. R01–R14 外部概率论评审均未签署；
3. MathSciNet/zbMATH/Scopus/WoS/CNKI 机构检索未完成；
4. 真实交易需求到路由核的映射未完成；
5. 完整英文论文、目标期刊模板和投稿包尚未形成；
6. 2026-07-17 HTML 仍待用户视觉确认。

因此，本轮可以确认“项目可继续推进且进度基线可靠”，不能确认“已经可以投稿”。
