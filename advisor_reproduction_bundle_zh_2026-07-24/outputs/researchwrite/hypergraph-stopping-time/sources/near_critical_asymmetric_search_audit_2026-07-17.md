# 近临界与非对称多人破产文献审计

检索日期：2026-07-17  
用途：界定中心偏置弱漂移定理 T9 的最近先例，而不是证明“全球首次”。

补充访问审计：Cambridge/JSTOR/OpenAlex 核验未发现 Barnett（1964）的
OA 副本；JSTOR 存在受控下载/XML 入口，但补充材料选择尚未确认，故本轮
未测试全文权限且没有下载文件。Barnett（1963）方法前篇的公开摘要、元数据
和引用关系已核验，但完整转移核仍须全文。详见
[Barnett 访问与引用链审计](barnett_1964_access_and_citation_chain_audit_2026-07-17.md)。

## 1. 被审计的主张

本轮不检索宽泛的“多人赌徒破产是否有人研究”，而检索下列组合是否已有
完全同构先例：固定一般参与者数 (k)，每步只在一对参与者之间转移一个
单位，方向概率采用中心偏置 (p_N=1+\eta/N)，在首次任一余额归零时停止，
并证明 (N^2) 尺度退出时间的分布与矩极限。

只有以下四项同时成立才标为“完全同构”：

1. **转账规则**：每步仅有一名付款方与一名收款方，余额增量为
   (e_j-e_i)；
2. **维数范围**：结论适用于固定一般 (k)，而不只是 (k=2) 或 (k=3)；
3. **偏置尺度**：存在与 (p_N=1+\eta/N) 等价的近临界中心偏置；
4. **停止量**：研究首次任一坐标到零，并给出退出时间的分布/矩渐近。

“讨论了多人”“讨论了非对称”“证明了所有矩”中的任意一项，均不足以
构成完全同构。

## 2. 检索方法与证据等级

### 2.1 查询族

- `multiplayer OR n-player gambler's ruin` + `asymmetric OR biased`；
- `pairwise transfer` + `first ruin OR exit time`；
- `weak drift OR near-critical OR small drift` + `simplex OR lattice exit`；
- `moments OR convergence of moments` + `multidimensional gambler's ruin`；
- 从 Barnett 1964、Rocha–Stern 1999/2004、Sobel–Frankowski 2002、
  Tzioufas 2019 和近年多人矩论文追踪引用链。

### 2.2 来源优先级

1. 出版商文章页、期刊页、arXiv 原始记录和可访问全文；
2. Crossref/DOI 元数据；
3. 仅用于发现候选的搜索索引或二次引用，不单独支撑模型同构判断。

本轮 OpenAlex 公共接口的部分查询在 Windows GBK 输出环节失败，且相关性
排序不稳定，因此只把它作为候选发现工具；所有纳入结论的条目均回到 DOI、
出版商或 arXiv 页面核验。尚未完成 MathSciNet、zbMATH、Scopus 和 Web of
Science 的全引用追踪。

## 3. 候选逐项比较

| 文献 | 每步规则 | (k) | 偏置 | 停止事件与结果 | 与 T9 的关系 | 核验状态 |
|---|---|---:|---|---|---|---|
| Barnett (1964), *A three-player extension of the gambler's ruin problem* | 摘要未给出完整转移核；论文建立在作者 1963 年非对称二维随机游走之上 | 3 | 非对称，但尺度未知 | 三人扩展；公开摘要不足以确认停止量和矩结论 | **最高优先级潜在近邻**；可能在 (k=3) 与成对非对称转账上接近 | `manual_needed`：必须读全文，不能凭摘要判为覆盖或不覆盖 |
| Rocha & Stern (1999) | 每轮选一名赢家；其余 (n-1) 人各付 1，赢家净增 (n-1) | 一般 (n) | 固定赢家概率 (p_i) | 首次破产；有限初始财富下的期望和破产概率 | 非对称、一般 (n)，但**不是成对单位转账**，也不是 (1/N) 弱偏置极限 | 已由出版商摘要/规则核验 |
| Rocha & Stern (2004) | 同一“所有输家向赢家付款”规则 | 一般 (n) | 固定 (p_i) | 等初始财富下的期望、概率与渐近 | 规则和渐近参数均不同 | 已由 DOI/出版商摘要核验 |
| Hashemiparast & Sabzevari (2011)；Sabzevari (2018) | 同上，另允许平局 | 一般 (n) | 固定 (p_i) 与平局概率 | 期望、概率及方差 | 说明非对称多人 ruin 的矩已有系统研究，但更新规则不同 | 由 2025 开放全文的模型和引用链核验 |
| Phetpradap & Sripanitan (2025) | 赢家从每个对手各收 1，可平局 | 一般 (n) | 固定 (p_i) | 等资本 (d=n,n+1) 的任意正整数阶矩公式 | **排除“全矩本身即新颖”**；不覆盖成对转账、(N\to\infty) 弱漂移扩散极限 | 已由开放全文核验 |
| Hussain et al. (2023) | 三人经典“单一赢家从两名输家收款”规则 | 3 | 非对称 | 破产时间经验近似公式 | 是 v4 数值代理的邻近先例，不是 T9 的同构模型 | 已由出版商摘要/DOI 核验 |
| Kmet & Petkovšek (2002) | 两名玩家、多个货币坐标的高维随机游走 | 维数一般，但不是多人单纯形 | 公平 | 多维退出时间的期望渐近 | 是高维退出方法先例，不是多人余额守恒单纯形 | 已由原论文入口核验 |
| Tzioufas (2019) | (\mathbb Z^d) 简单随机游走，从 (L_\infty) 球退出 | 一般 (d) | 公平 | 适当缩放下所有 (p)-阶退出时间矩极限 | **排除“由不变原理得到全矩收敛即新颖”**；几何和转移规则不同 | 已由期刊摘要/arXiv 核验 |
| Ekhad & Zeilberger (2023) | 公平三人 gambler's ruin | 3 | 公平 | 用符号计算给出许多持续时间矩 | 三人公平矩的直接先例；不覆盖一般 (k) 或弱漂移 | 已由 arXiv 核验 |
| Grigorescu & Yao (2016) | 可控制的公平成对转账 | 一般多人 | 选择策略 | 完全淘汰时间/方差目标 | 与成对规则接近，但停止量和控制问题不同 | 已由 DOI/原文元数据核验 |
| Kehagias et al. (2025) | 激活玩家选择对手，随后成对单位转账 | 3 | 非对称策略 | 完全淘汰博弈 | 排除“非对称 pairwise 多人 ruin 无先例”；不覆盖首次为零弱漂移 | 已由 Springer 原文页核验 |

## 4. 可辩护结论

截至本轮纳入并核验的来源，**尚未发现同时满足四项同构判据的结果**。这只
是有边界的检索结论，不能改写为“首次证明”或“文献中不存在”。尤其是
Barnett (1964) 的全文尚未核验，它是当前新颖性判断的 P0 闸门。

本轮已经能确定两项负面结论：

1. “非对称一般 (n) 人首次破产”不是新主题；Rocha–Stern 系列早已研究，
   但采用一名赢家同时从所有对手收款的不同更新规则。
2. “退出时间全部阶矩”本身不是新现象；Tzioufas (2019) 在不同几何中证明
   所有 (p)-阶矩的极限，Phetpradap–Sripanitan (2025) 在不同多人规则中
   给出任意整数阶矩公式。

因此 T9 只能定位为：**特定中心偏置、守恒单纯形、成对单位转账和首次耗尽
语义下的近临界退出定理候选**。论文贡献必须把它与强漂移不对称相图、支付
通道语义和可计算代理组合呈现，不能把标准 FCLT、连续映射或全矩收敛单独
包装为重大创新。

## 5. 下一轮检索闸门

1. 通过图书馆/JSTOR/作者存档合法取得 Barnett (1964) 全文，逐条填写四项
   同构判据；1963 方法前篇的公开摘要、元数据和引用关系已核验，完整
   转移核仍需全文。
2. 用 MathSciNet/zbMATH 做 Barnett、Rocha–Stern、Sobel–Frankowski 的
   “被引/引用”双向追踪。
3. 用 Scopus/WoS 复核 `weak drift`, `small drift`, `near-critical`,
   `simplex exit`, `triangular array` 的组合查询。
4. 外部概率论审阅者必须独立确认“最近先例—差异—新增内容”三列表；若
   找到完全同构或包含 T9 的一般定理，T9 降为应用推论并重写贡献结构。

## 6. 原始入口

- [Barnett 1964，Cambridge Core](https://www.cambridge.org/core/journals/journal-of-applied-probability/article/abs/threeplayer-extension-of-the-gamblers-ruin-problem/A9E0448F0ADA4517511C789A387CF1FE)
- [Barnett 1964 访问与引用链审计](barnett_1964_access_and_citation_chain_audit_2026-07-17.md)
- [Rocha & Stern 1999，ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0167715298002958)
- [Rocha & Stern 2004，DOI](https://doi.org/10.1016/j.aam.2003.07.005)
- [Phetpradap & Sripanitan 2025，Springer 开放全文](https://link.springer.com/article/10.1007/s40840-024-01790-5)
- [Tzioufas 2019，期刊页](https://math-mprf.org/journal/articles/id1530/)
- [Ekhad & Zeilberger 2023，arXiv](https://arxiv.org/abs/2309.08762)
- [Kmet & Petkovšek 2002，作者存档 PDF](https://sites.math.rutgers.edu/~zeilberg/akherim/Kmet.pdf)
- [Hussain et al. 2023，DOI](https://doi.org/10.1080/03610918.2021.1888996)
