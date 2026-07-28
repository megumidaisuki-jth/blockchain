# 相关超图网络先行工作补充审计（2026-07-18）

## 1. 审计结论

截至 2026-07-18，在本轮能够访问并核验的开放来源中，未发现同时满足下文八项同构判据的直接论文；这一结果只支持“在已检索范围内未发现直接同构结果”，不支持“全球首次”。本轮检索同时排除了三类过宽的新颖性主张：

1. 不能声称首次研究支付通道的寿命、耗尽时间或 stopping time；
2. 不能声称首次以超图或多方通道表示支付通道网络；
3. 不能把三角阵 first-passage、乘积链或全矩收敛方法本身写成原创。

当前最可辩护的候选贡献，是把 Podiatchev–Orda–Rottenstreich（2024）明确指出但未解决的“多跳支付同时影响多个通道、通道并不独立”缺口，落实为固定超图上的原子多超边路由增量，并研究相关余额过程的首次耗尽、漂移相变与独立代理误差。该贡献仍须通过机构数据库检索和独立概率论评审，publication readiness 继续为 `false`。

## 2. 检索范围、查询族与可用性

检索日为 2026-07-18。检索采用 DOI 优先、其次为规范化标题加第一作者的去重规则；技术判断优先使用作者预印本、出版方页面和论文全文。

### 2.1 查询族

- `payment channel` AND (`stopping time` OR `first passage` OR `lifetime` OR `lifespan` OR `depletion`)
- (`hypergraph` OR `multi-party payment channel`) AND (`balance` OR `depletion` OR `stochastic`)
- (`multi-hop payment` OR `route`) AND (`correlated channels` OR `joint balance` OR `simultaneous update`)
- (`triangular array` OR `small drift`) AND (`first-passage` OR `exit time` OR `moment convergence`)
- 对 Podiatchev、Shabgahi、Kotzer、Corcoran、Nainwal、Pickhardt、Denisov 等精确题名及其前后向引用链进行补充核验。

### 2.2 来源覆盖与失败记录

| 层级 | 来源 | 本轮状态 | 可据此声称的覆盖 |
|---|---|---|---|
| T1 | arXiv、IACR ePrint、Springer、IEEE DOI/出版记录、NDSS、MDPI | 通过；逐篇核验题名、作者、摘要或全文 | 直接 PCN、超图 PCN、协议/控制及概率论方法先例 |
| T1 | Crossref REST | 预检可达，但批量请求返回 `429` | 不把 Crossref 计为本轮完整覆盖；改用出版方/作者页面核验 |
| T2 | OpenAlex | 可用；用于精确题名和书目交叉核验 | 补充发现与书目核对，不替代全文判断 |
| T2 | Semantic Scholar API | 返回 `429` | 本轮未完成该源的系统覆盖 |
| T3 | zbMATH Open | 公开页面确认 Denisov–Sakhanenko–Wachtel 条目 `Zbl 1496.60041`；REST API 有条款接受门 | 只记录公开可见条目；未代替 MathSciNet/zbMATH 系统检索 |
| T3 | MathSciNet、Scopus、Web of Science、CNKI | 当前环境无机构检索入口 | `manual-needed`，投稿前必须补做 |

PubMed 与本主题的计算机网络/概率论核心文献域不匹配，未把“接口可达”误写成有效主题覆盖。本轮未下载 Barnett（1964）全文或补充材料，也未接受 zbMATH API 的法律条款。

## 3. 八项同构判据

为避免只凭关键词判断“相似”，本审计固定以下判据：

| 代号 | 判据 |
|---|---|
| C1 | 直接研究支付通道网络（PCN） |
| C2 | 固定多方/超图结构，并显式跟踪超边—参与者余额 |
| C3 | 一次外生、状态无关、i.i.d.、有界路由事件作为跨多个超边的原子增量 |
| C4 | 显式研究该原子路由诱导的跨超边相关性 |
| C5 | 停止事件是网络中首个余额坐标到零/首个通道耗尽 |
| C6 | 漂移按 (p_N=1+\eta N^{-\alpha}) 消失，并区分 \(\alpha<1,=1,>1\) |
| C7 | 得到固定维乘积单纯形上的联合扩散退出极限 |
| C8 | 证明全部固定正阶矩收敛，并提供相关模型—独立代理的精确/配对 MC 诊断 |

表中 `Y` 表示直接满足，`P` 表示只覆盖邻近概念，`N` 表示不满足。`P` 不能用于宣称同构。

## 4. 去重后的同构比较表

| 工作 | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | 对本项目的约束 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| Bai–Xu–Wang (2021) | Y | N | N | N | N | N | N | N | first-passage 已用于交易等待时间，但事件不是通道耗尽 |
| van Engelshoven–Roos (2020) | Y | N | N | N | P | N | N | N | depletion 规避与费率激励已有直接先例 |
| Shabgahi et al. (2022) | Y | N | N | N | P | N | N | N | 已基于拓扑建立单通道有效寿命模型 |
| Dehshali et al. (2022) | Y | N | N | N | P | N | N | N | 已把有限可路由交易数与网络吞吐上限联系起来 |
| Podiatchev–Orda–Rottenstreich (2024) | Y | N | N | N | Y | N | N | N | 已定义通道 stopping time 和网络首通道失败；网络精确式假设通道独立 |
| Tian et al. (Horcrux, 2025) | Y | N | P | P | P | N | N | N | 多跳支付、相邻通道联合调节和 depletion 防护已有协议/实验先例 |
| Sankagiri–Hajek (2025/2026) | Y | N | N | P | N | N | N | N | 长期净流不可持续及联合路由/流控已有控制论先例 |
| Kim (2023) | Y | Y | N | N | N | N | N | N | 多方支付通道设计和联盟形成已有先例 |
| Kotzer et al. (2025) | Y | Y | N | N | N | N | N | N | 超边支付网络及拓扑性能比较已有直接先例 |
| Corcoran–Lewis (2025) | Y | Y | P | N | N | N | N | N | 超图余额映射与跨超边路径规划已有直接先例 |
| Nainwal–Kamble–Awathare (2026) | Y | Y | P | P | N | N | N | N | 跨超边原子结算语义已有协议先例，但不是随机停止理论 |
| Pickhardt (2026) | Y | Y | N | N | P | N | P | N | 可行财富多面体、cut 与多方资本效率已有理论先例 |
| Denisov–Sakhanenko–Wachtel (2021) | N | N | N | N | P | N | N | N | 三角阵 first-passage 是方法先例，不能作为应用创新 |
| Tzioufas (2019) | N | N | N | N | P | N | P | P | 多维退出时间全 \(p\)-阶矩渐近已有先例，但几何为 \(L_\infty\) 球 |
| Patel–Carron–Bullo (2016) | N | N | N | N | P | N | P | N | 多随机游走联合命中和乘积链是标准工具 |

本表共 15 项规范化工作；未发现八项全为 `Y` 的条目。这个阴性结果受第 2.2 节来源缺口约束，不能外推为穷尽性证明。

## 5. 关键直接先例的严格边界

### 5.1 支付通道寿命与停止时间不是空白

- [Shabgahi et al., *Modeling Effective Lifespan of Payment Channels*](https://arxiv.org/abs/2301.01240) 把一侧余额不足定义为有效寿命结束，并基于网络拓扑预测单通道期望寿命。因此不能写“首次数学建模支付通道寿命”或“首次研究拓扑对通道寿命的影响”。
- [Dehshali et al., *Throughput Limitation of the Off-chain Payment Networks*](https://eprint.iacr.org/2022/1614) 明确把通道在失衡前可路由的有限交易数与链下网络吞吐上限联系起来。
- [Podiatchev et al., *Survivable Payment Channel Networks*](https://eprint.iacr.org/2024/1393) 明确定义通道 stopping time，并研究单通道、通道集合、特定拓扑和容量优化。其网络可生存性采用首个通道失败语义，与本项目停止事件高度接近。
- [Bai et al. (2021)](https://arxiv.org/abs/2104.02936) 已把 first-passage 用于单通道交易等待时间；其边界事件是交易金额重新变得可路由，不是通道余额首次耗尽。

### 5.2 “相关通道”是有文献依据的缺口，但不是自动成立的新颖性

Podiatchev et al. 的全文在给出独立通道网络计算后，明确指出该独立假设并不合理，因为多跳交易会同时影响若干通道。这个陈述为本项目研究原子路由诱导相关性提供了直接问题来源。它只说明问题重要且先例未处理该处限制；要形成论文贡献，仍需证明我们的相关模型、T17 相图或 T18 判据没有被其他文献覆盖。

### 5.3 超图/多方支付通道不是空白

- [Kotzer et al. (2025)](https://eprint.iacr.org/2025/205) 已提出超边支付网络与超图拓扑，并比较成功率和成本。
- Corcoran–Lewis (2025) 已研究带多方通道的 PCN 路径规划和超图余额语义。
- [Kim (2023)](https://www.mdpi.com/1424-8220/23/9/4524) 已研究多方支付通道及联盟形成。
- [Nainwal–Kamble–Awathare (2026)](https://arxiv.org/abs/2512.11775) 已给出跨超边多方支付的原子协议语义。
- [Pickhardt (2026)](https://arxiv.org/abs/2601.04835) 已从可行财富多面体和 cut 角度讨论多方超边；其公开全文未给出本项目的随机 stopping-time/FCLT 结论。

因此不能写“首次提出超图支付通道”“首次允许一笔支付跨多个超边”或“首次研究 PCN depletion”。

### 5.4 depletion 防护与长期控制是相邻而非同构工作

- [The Merchant](https://arxiv.org/abs/2012.10280) 以动态费率激励平衡使用；
- [Horcrux](https://eprint.iacr.org/2024/1338) 以 flow neutrality 和多方虚拟通道减少 depletion；
- [Sankagiri–Hajek](https://arxiv.org/abs/2502.20203) 研究联合路由/流控与稳态需求下的收敛。

这些工作说明 depletion 的工程动机和控制问题已有丰富先例，但它们没有给出固定超图上相关余额过程的三分区首次退出定理。

### 5.5 概率论方法边界

- [Denisov–Sakhanenko–Wachtel](https://arxiv.org/abs/2005.00240) 已研究三角阵独立增量的 first-passage；
- Tzioufas (2019) 已给出另一类多维游走退出时间的全部 \(p\)-阶矩渐近；
- Patel–Carron–Bullo (2016) 已用乘积链处理多个随机游走的联合命中时间。

因此论文必须把方法贡献绑定到“原子路由诱导的相关协方差结构 + 固定维乘积单纯形 + 多项式消失漂移 + 网络首耗尽”这一具体组合，不能单独把 FCLT、Poisson 方程、三角阵或全矩收敛列为新方法。

## 6. 收窄后的投稿贡献合同

若外部评审最终签署，建议把主张限定为以下四层，而不是笼统宣称“首篇超图 PCN 停止时间论文”：

1. **相关网络模型**：在固定有限超图上，把一次跨多超边支付建模为保持各超边守恒约束的单个原子增量，从而显式产生跨超边相关性；路由分布必须保持外生、i.i.d.、状态无关和有界。
2. **严格首耗尽理论**：在显式耗尽可达条件下给出有限状态精确表示；在固定维、大容量极限中给出 \(\alpha<1\)、\(\alpha=1\)、\(\alpha>1\) 三分区及全部固定正阶矩收敛。
3. **独立近似的适用边界**：只在联合 Gaussian 极限且跨超边协方差块为零时推出块独立；不把零协方差推广到一般非 Gaussian 情形。
4. **可复现误差诊断**：用精确小网络与配对 Monte Carlo 比较相关模型和保留边际的独立代理；只报告冻结设计下的误差，不声称跨拓扑普遍符号。

推荐的有界新颖性句式是：

> 在截至 2026-07-18 已核验的开放来源中，我们未发现同时研究固定超图上的原子多超边路由相关性、网络首余额耗尽、三尺度漂移相变和全部固定正阶矩的直接同构结果；该判断仍待 MathSciNet、zbMATH、Scopus、Web of Science 与 CNKI 的机构检索确认。

## 7. 下一步门禁

| 优先级 | 工作 | 通过条件 |
|---|---|---|
| P0 | 机构数据库新颖性复核 | MathSciNet/zbMATH/Scopus/WoS/CNKI 完成精确题名、主题词和引用链检索；记录检索式、日期、命中与去重日志 |
| P0 | 独立概率论评审 | T16、T17A/B/C、T18a 的外部签核表全部通过，或按失败降级规则收窄主张 |
| P1 | T18 跨拓扑稳健性 | 至少覆盖不重叠基线、重叠链、重叠星、随机连通超图；报告标准化效应量、置信区间与符号变化 |
| P1 | 应用映射 | 给出真实 PCN/H-MPC 交易到外生 i.i.d. 路由核的可识别映射，并明确不满足状态无关假设时的失效边界 |
| P2 | 稿件组装与选刊 | 以“相关首耗尽理论”为标题核心，完成 related work、定理主线、实验和可复现性附录；再按目标期刊格式化 |

在上述 P0 门禁通过前，项目可以继续做实验和稿件骨架，但不得标记为 publication-ready。
