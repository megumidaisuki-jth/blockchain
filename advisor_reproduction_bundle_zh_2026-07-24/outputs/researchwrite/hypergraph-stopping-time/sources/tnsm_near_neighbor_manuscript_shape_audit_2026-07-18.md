# TNSM 直接近邻论文形态审计

**审计日期**：2026-07-18  
**用途**：判断本项目投向 IEEE Transactions on Network and Service Management（TNSM）时，主文页数、理论—实验配比和网络管理贡献是否与直接先例匹配。  
**边界**：这是目标期刊近邻稿件审计，不是新的全球新颖性检索，也不替代机构数据库检索。
**项目状态**：`publication_readiness = false`；本审计不改变外部证明、T18、机构检索或完整稿件门禁。

## 1. 执行结论

按 DOI 去重并把同题会议版/预印本合并到期刊正式版后，当前找到两篇与本项目最直接的 TNSM 论文：

1. Podiatchev–Orda–Rottenstreich（2024），*Survivable Payment Channel Networks*，15 页；
2. Kotzer–Ladóczki–Tapolcai–Rottenstreich（2025），*Addressing Scalability Issues of Blockchains With Hypergraph Payment Networks*，14 页。

这两篇论文共同显示：

- TNSM 已直接接收支付通道 stopping time 和超图支付网络，因此这两个主题本身不能作为本项目的新颖性；
- 两篇正式版均明显超过 10 页免费额度，并同时提供模型/理论、可执行网络管理动作和实验；
- 两篇都使用真实 Lightning Network（LN）拓扑或快照，而不是只给小型合成拓扑；
- 本项目当前理论深度足够进入该对话，但缺少“真实需求映射 + 可执行容量/路由/再平衡判断规则”的稿件级闭合。

因此，此前 11–12 页的主文建议偏紧。当前更合理的暂定路线是 **12–14 个 IEEE 双栏页**，完整长证明作为随稿评审的补充材料；按 2026-07-18 TNSM 政策，预计超过 10 页部分的页费为 440–880 美元。若作者要求零页费，必须另行设计 10 页压缩版，不能假装两者信息容量相同。

## 2. 检索与核验协议

### 2.1 问题定义

本轮只回答三个问题：

1. 最直接 TNSM 先例的正式页数是多少？
2. 它们怎样组合理论、算法/设计和实验？
3. 这些先例对本项目的投稿结构提出什么最低要求？

### 2.2 来源路线

- academic-search MCP：当前会话未挂载，记录为工具不可用；
- T1 发现：技能自带 OpenAlex 公共 API 降级脚本；
- T1 元数据核验：Crossref DOI API；
- 出版/期刊核验：[TNSM 官方范围与索引入口](https://www.comsoc.org/publications/journals/ieee-transactions-network-and-service-management)、[TNSM 官方投稿政策](https://www.comsoc.org/publications/journals/ieee-tnsm/policies-guidelines)、[TNSM searchable index](https://www.tnsm-overview.org/search)；
- 全文/作者版本：[Podiatchev et al. PDF](https://eprint.iacr.org/2024/1393.pdf)、[Kotzer et al. ePrint 页面](https://eprint.iacr.org/2025/205)；
- 辅助出版核验：[Technion 的 Podiatchev 机构记录](https://cris.technion.ac.il/en/publications/survivable-payment-channel-networks-2/)。

### 2.3 查询

OpenAlex 降级脚本在 `year >= 2022` 下运行以下查询：

1. `payment channel networks network service management`
2. `hypergraph payment channel networks`
3. `survivable payment channel networks`
4. `blockchain network service management payment channel`

第一和第四个查询精度较低，返回大量消费支付、供应链和一般区块链工作；它们不进入最终近邻表。第二、第三个查询分别命中 Kotzer 和 Podiatchev 的期刊版本及其预印本/会议版。

### 2.4 去重

- DOI 相同：合并；
- DOI 不同但题名标准化后相同且第一作者相同：视为同一工作版本族；
- 同一版本族优先保留具有正式卷、期、页码的 TNSM 期刊版本；
- Podiatchev 的 COMSNETS 会议版本和 Kotzer 的 IACR ePrint 版本只用于全文/版本追踪，不重复计为独立 TNSM 论文。

## 3. 两篇直接近邻

| 维度 | Podiatchev et al. (2024) | Kotzer et al. (2025) |
|---|---|---|
| 正式题名 | *Survivable Payment Channel Networks* | *Addressing Scalability Issues of Blockchains With Hypergraph Payment Networks* |
| DOI | [10.1109/TNSM.2024.3456229](https://doi.org/10.1109/TNSM.2024.3456229) | [10.1109/TNSM.2025.3542960](https://doi.org/10.1109/TNSM.2025.3542960) |
| 正式卷期页 | 21(6):6218–6232 | 22(3):2427–2440 |
| 正式页数 | 15 | 14 |
| 与本项目最直接的重合 | 通道 stopping time、网络首通道失败、漂移/平衡、特定拓扑 | 超图支付网络、多方超边拓扑、LN 对照 |
| 理论/模型 | 单通道随机游走、均值/下界、通道集合、容量分配 | 超图支付网络框架、成本模型、拓扑构造与聚类算法 |
| 网络管理动作 | 全局与分布式容量再分配，目标是提高最小 stopping time | 把 LN/PCN 转换为 NCH/FHS 等超图拓扑并比较成本/成功率 |
| 合成实验 | 链、随机树、链/环等特定拓扑 | 合成流量和多种超图规模/结构 |
| 现实数据 | 2022 年 LN 快照 | LN 经验拓扑/数据，与 LN 及其他方案比较 |
| 可复现性表述 | 本审计未确认正式公开代码入口 | 引言明确声明开源实现、输入和合成流量数据 |

## 4. Podiatchev et al. 的稿件结构

作者版本为 15 页，正文结构可直接从全文核验：

1. **Introduction**：背景与贡献；
2. **The Stopping Time of a Payment Channel**：定义、平衡通道、固定支付额含漂移通道；
3. **Stopping Time of a Set of Channels**：通道集合的首失效计算；
4. **Capacity Distribution Optimization**：把 stopping-time 下界转化为容量配置目标，并在合成拓扑和 LN 快照上验证；
5. **Distributed Optimization**：把全局方案转化为更现实的局部方案；
6. **Stopping Time of a Channel in Particular Topologies**：链、环等拓扑下界；
7. **Related Work**；
8. **Conclusions and Discussion**。

全文在第 10 页附近仍报告 LN 与随机树实验，在第 12 页进入 Related Work，第 13 页进入 Conclusions and Discussion，余下篇幅用于结论延伸和参考文献。它的形态不是“先给公式、再附一个小实验”，而是 stopping time → 容量配置 → 全局/分布式方案 → 合成与真实网络验证的完整管理链。

## 5. Kotzer et al. 的稿件结构

正式版为 14 页。作者版本的引言明确列出以下组织：

- Section II：Layer-2、两方/多方支付通道、超图和 related work；
- Section III-A：多方通道成本；
- Section IV：多方/超图拓扑设计，是论文主贡献；
- Section V：使用真实 LN 数据评估 HPN；
- Section VII：结论与未来方向。

引言把贡献概括为三类：通用 HPN 框架、从现实 LN 拓扑生成超图的聚类算法、使用经验数据的仿真，并声明开源实现、输入和合成流量。这说明单纯“使用超图表示 PCN”远低于该刊已发表基线；超图必须连接到具体构造、性能指标和可复现评价。

## 6. 与本项目的逐项差距

| 稿件要素 | Podiatchev 2024 | Kotzer 2025 | 本项目当前状态 | 投稿前要求 |
|---|---|---|---|---|
| PCN stopping time | 已覆盖 | 非主线 | 已扩展到相关超图首耗尽 | 不声称首次；明确超越独立假设的部分 |
| 超图 PCN | 否 | 已覆盖 | 固定超图原子路由模型 | 不把“超图”本身当贡献 |
| 跨超边相关增量 | 独立聚合并明确指出限制 | 非停止时间模型 | T16–T18 候选核心 | 外部证明签核 + T18 跨拓扑证据 |
| 漂移相图/全矩 | 未覆盖本项目组合 | 未覆盖 | 内部证明工作稿 | 证明条件、先例与外部签核并列 |
| 可执行管理动作 | 容量优化 | 拓扑构造 | 尚以诊断为主 | 形成容量/路由/代理选择规则 |
| 合成拓扑 | 有 | 有 | 冻结实例有，T18 正式网格未运行 | 链、星、固定种子随机连通超图 |
| 真实 LN 映射 | 有 | 有 | 无 | 至少一个公开快照或透明需求映射 |
| 正式公开代码/数据 | 本轮未确认 | 作者声明有 | 本地可复现，尚未归档公开 | 建立 DOI 仓库、环境与运行说明 |
| 稿件 | 15 页已发表 | 14 页已发表 | 无完整英文稿 | 12–14 页主文 + 评审补充材料 |

## 7. 对投稿设计的约束

### 7.1 页数

推荐把经济与完整性平衡点调整为 **12–14 页**：

- 12 页：接受后按当前政策预计 440 美元页费；
- 13 页：预计 660 美元；
- 14 页：预计 880 美元；
- 15 页：与 Podiatchev 相同长度，预计 1,100 美元；
- 16 页：政策上限，预计 1,320 美元。

这些金额只计算超过 10 页的强制页费，不包括可选 OA；正式投稿前必须再次读取官方政策。

### 7.2 主文必须保留的内容

即使把完整证明放到补充材料，主文也至少需要：

1. 相关模型为何不同于独立通道聚合；
2. T16/T17 主定理的准确条件和证明路线；
3. T18 的零相关边界与有限容量误差；
4. 跨拓扑稳健性实验；
5. 一个真实 LN/透明需求映射；
6. 面向容量、路由、再平衡或代理选择的管理含义；
7. 明确限制和可复现入口。

### 7.3 不应照搬先例的地方

- Podiatchev 把 Related Work 放在靠后位置；本项目的新颖性边界更脆弱，宜在前部单列并明确与两篇直接先例的差异。
- Kotzer 的核心是拓扑构造；本项目核心是相关首耗尽理论，不能用大量协议背景挤压定理条件与相关性机制。
- 两篇先例都不能替代本项目的外部概率论评审；“TNSM 已发表类似主题”只证明范围匹配，不证明定理正确或新颖。

## 8. 修订后的路线选择

- **R1（推荐）**：12–14 页证据优先版，预计页费 440–880 美元；主文自洽，完整长证明、扩展表和代码说明进补充材料。
- **R2（零页费）**：严格 10 页；需要砍掉次要单超边 v4、T12 二阶修正和大量背景，只保留相关网络主线，存在解释不足风险。
- **R3（定理完整版）**：15–16 页，预计页费 1,100–1,320 美元；只有外部证明全部签核且作者接受成本时才采用。

本审计只把 R1 作为证据支持的建议，不代表作者已经批准页费或最终页数。

## 9. 检索失败与范围边界

- academic-search MCP 未挂载，已按技能规则使用 OpenAlex 公共 API 降级；
- 四个宽查询中两个噪声较大，因此本轮不宣称穷尽了 TNSM 所有区块链论文；
- IACR 2025/205 PDF 在一次网页直接打开中受 robots 限制，但搜索索引、ePrint 元数据、Crossref 和正式卷期页相互一致；
- Scopus、Web of Science、MathSciNet、zbMATH 和 CNKI 仍未完成，继续属于全项目的新颖性门禁；
- 当前结论只支持“两个最直接 TNSM 先例均为 14–15 页、理论/设计/真实数据结合”，不支持一般化为“所有 TNSM 论文都必须 14 页以上”。

## 10. 对主张的最终影响

本项目面向 TNSM 的可辩护差异应写成：

> 相比已有的独立通道 stopping-time 聚合和超图拓扑构造，本项目研究一次原子多超边路由所诱导的余额相关性，以及该相关性对固定超图网络首次耗尽、漂移相图和独立代理可靠性的影响。

这仍是候选贡献合同，不是已获同行确认的新颖性结论。
