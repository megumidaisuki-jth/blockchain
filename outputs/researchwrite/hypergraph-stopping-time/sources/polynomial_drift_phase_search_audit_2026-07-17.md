# 多项式消失漂移相图文献审计

检索日期：2026-07-17  
用途：界定 \(p_N=1+\eta N^{-\alpha}\) 三分区相图 T15 的先行工作边界。

## 1. 检索对象

被审计的完整组合为：

1. 固定一般参与者数 \(k\)；
2. 每步只在一对参与者之间转移一个单位；
3. 总余额守恒、状态空间为离散单纯形；
4. 中心偏置随容量按 \(N^{-\alpha}\) 消失；
5. 首次任一余额为零；
6. 同时刻画 \(\alpha<1,\alpha=1,\alpha>1\)；
7. 给出分布极限、指数集中或全部固定正阶矩极限。

只有七项同时满足才记为完全同构。小漂移、弱不对称、区间退出或矩增长中
任一单项均只构成方法/现象先例。

## 2. 检索过程

查询族：

- gambler's ruin + vanishing drift + exit time；
- gambler's ruin + near-critical / weak drift；
- weakly asymmetric random walk + interval exit；
- simplex / polytope random walk + small drift + exit time；
- ladder epoch + small negative drift + moments；
- drifted Brownian/random walk + bounded-domain exit。

首选 Crossref、arXiv 和出版社原文页。nature-academic-search 的 OpenAlex
备用脚本在四个并发查询时返回 HTTP 429，故未把该轮结果纳入证据；随后
使用普通检索发现候选，再逐项回到 arXiv 或 Cambridge Core 原始页面。
本轮未使用 Google Scholar、ResearchGate 或百科页面支撑结论。

## 3. 最近候选

| 文献 | 模型与结果 | 与 T15 的关系 | 裁决 |
|---|---|---|---|
| Athreya, Sethuraman & Tóth (2010), arXiv:1009.3999 | 一维区间 \(\{0,\ldots,N\}\) 上最近邻随机游走；明确区分公平、\(q_N=1/2-c/N\) 弱不对称和固定不对称；研究退出时 range、local times、periodicity | 直接确认 \(1/N\) 弱不对称和三类区间已有先例，但主要停止时统计不是退出时间全矩，几何也不是守恒单纯形 | 邻近尺度先例，非完全同构 |
| Wachtel (2009), DOI 10.1239/aap/1261669592 | 一维小负漂移随机游走的首次下降阶梯时刻；研究尾转变和矩增长率 | “小漂移导致 first-passage transition” 已有系统理论；无有限单纯形、中心偏置或正负多人竞争 | 强方法/现象先例 |
| Schulte-Geers & Stadje (2017), DOI 10.1017/jpr.2016.95 | 小正漂移随机游走在负半轴的占用时间；用 FCLT 得到漂移 Brownian 极限 | 说明 small-drift + FCLT + Brownian drift 组合并非新方法；停止量不同 | 方法先例 |
| Geng & Markowsky (2026), DOI 10.1080/15326349.2025.2515964 | 一维有偏随机游走与带漂移 Brownian 在对称区间的退出时间关于漂移随机单调 | 直接涉及 bounded exit time 与 drift，但不研究 \(N^{-\alpha}\) 三分区或多人单纯形 | 退出时间邻近先例 |
| Alabert, Farré & Roy (2004) | 三人公平三角格退出到 Brownian 三角形；含统一可积性和 Poisson 方程 | 覆盖 \(k=3,\eta=0\) 的扩散端点 | 直接低维端点先例 |
| Tzioufas (2019) | 不同多维几何下退出时间全部 \(p\)-阶矩极限 | 排除“全矩相图本身即新颖” | 全矩方法/现象先例 |

## 4. 可辩护结论

本轮核验确认：

1. \(1/N\) 弱不对称不是本项目首次提出的尺度；
2. 小漂移 first-passage transition、FCLT 到漂移 Brownian、区间退出时间
   的漂移比较和全矩极限均有直接或邻近先例；
3. 当前纳入来源尚未发现七项判据同时成立的完整结果。

第 3 点是有边界的检索结论，不是全球不存在证明。尤其 Barnett（1964）
全文、MathSciNet/zbMATH/Scopus/WoS 引用追踪仍未完成。

因此论文不得写“首次发现 \(1/N\) 临界漂移”或“首次建立小漂移相变”。
可审计的候选表述是：

> 在中心偏置的多方支付通道成对转账核下，统一证明首次余额耗尽时间从
> \(N^{1+\alpha}\) 确定性集中，经 \(\alpha=1\) 带漂移单纯形扩散，
> 过渡到 \(\alpha>1\) 公平单纯形扩散，并闭合全部固定正阶矩。

该表述仍须独立概率论复核和完整数据库检索后才能进入投稿摘要。

## 5. 原始入口

- [Athreya、Sethuraman 与 Tóth，arXiv:1009.3999](https://arxiv.org/abs/1009.3999)
- [Wachtel，Cambridge Core](https://www.cambridge.org/core/journals/advances-in-applied-probability/article/transition-phenomena-for-ladder-epochs-of-random-walks-with-small-negative-drift/A7877E070D2F2CFB13D27BC9742A1C00)
- [Schulte-Geers 与 Stadje，Cambridge Core](https://www.cambridge.org/core/journals/journal-of-applied-probability/article/abs/small-drift-limit-theorems-for-random-walks/6339CC37548CD42F8BB0CE23989BD270)
- [Geng 与 Markowsky，arXiv:2408.00277](https://arxiv.org/abs/2408.00277)
