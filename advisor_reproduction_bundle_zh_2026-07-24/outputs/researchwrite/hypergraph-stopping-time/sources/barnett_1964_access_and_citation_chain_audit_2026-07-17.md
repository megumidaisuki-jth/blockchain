# Barnett（1964）访问与引用链审计

审计日期：2026-07-17  
目的：核验 T9 的三人非对称低维先例，不以访问受限或检索未命中替代
模型同构判断。

## 1. 书目信息

已由 Cambridge Core 期刊页核验：

- V. D. Barnett；
- A Three-Player Extension of the Gambler's Ruin Problem；
- Journal of Applied Probability，1(2)，321–334，1964 年 12 月；
- 规范 DOI：10.2307/3211863；
- Cambridge 内容标识中另出现 S0021900200108435，对应的 DOI 形式为
  10.1017/S0021900200108435。项目参考文献以期刊页显示的
  10.2307/3211863 为主标识，并保留另一个标识用于检索去重。

官方入口：

- [Cambridge Core 文章页](https://www.cambridge.org/core/journals/journal-of-applied-probability/article/abs/threeplayer-extension-of-the-gamblers-ruin-problem/A9E0448F0ADA4517511C789A387CF1FE)
- [JSTOR 稳定记录](https://www.jstor.org/stable/3211863)
- [该卷期 JSTOR 目录](https://www.jstor.org/stable/i361241)

## 2. 合法可用性核验

| 路径 | 核验结果 | 可支持的结论 |
|---|---|---|
| Cambridge Core | 公开页显示书目信息与简短 extract，并提示 Get access | 可确认身份；不能恢复完整转移核 |
| JSTOR | 卷期页存在 article、Download 与 XML 入口 | 说明存在受平台控制的全文入口；本轮未测试访问权限 |
| OpenAlex | 记录为 closed，未给出开放仓储全文，has_fulltext=false | 未发现开放获取副本；不等于证明互联网绝无合法副本 |
| 普通公开检索 | 未发现作者主页、机构仓储或开放期刊副本 | 当前状态记为 oa_not_found |

本轮没有下载 PDF、XML、网页全文或补充附件。原因是全文下载流程要求先
确定是否同时获取 Supporting Information，而该选择尚待用户确认。这个
暂停只影响文件获取，不影响书目元数据与引用链核验。

当前访问状态：

\[
\texttt{oa\_not\_found + controlled\_platform\_entry\_untested}.
\]

不得把该状态改写为“无权访问”“全文不存在”或“Barnett 不覆盖本模型”。

## 3. 1963 年方法前篇

Barnett（1963）的文章已由 Cambridge Core 核验：

- Some Explicit Results for an Asymmetric Two-Dimensional Random Walk；
- Mathematical Proceedings of the Cambridge Philosophical Society，
  59(2)，451–462；
- DOI：10.1017/S0305004100037063。

公开摘要明确说明论文研究一个特定的非对称二维随机游走，并讨论无界过程
的返回/到达问题以及矩形吸收边界下的到达与吸收概率。Barnett（1964）的
引用图谱包含这篇前作，因此它是追查 1964 模型构造的首要方法来源。

但公开材料仍不足以推出以下任何事项：

1. 1964 年三人模型是否每步只在一对玩家间转移一个单位；
2. 其不对称是否等价于本项目中心偏置参数 \(p\)；
3. 是否研究 \(p_N=1+\eta/N\) 的近临界序列；
4. 是否证明首次任一余额为零的分布或矩极限。

官方入口：
[Barnett 1963，Cambridge Core](https://www.cambridge.org/core/journals/mathematical-proceedings-of-the-cambridge-philosophical-society/article/abs/some-explicit-results-for-an-asymmetric-twodimensional-random-walk/E345875EF794D3B32EFF2B9770D931B7)。

## 4. 双向引用链

OpenAlex 公共引用图谱把 Barnett（1963）和 Kingman（1961）
The Ergodic Behaviour of Random Walks 列为 1964 论文的两条参考文献
记录，并报告四条直接施引记录：

1. Discrete Parameter Stochastic Processes（1973），
   DOI 10.1007/978-3-642-80750-3_1；
2. P.-C. G. Vassiliou（1980），On Certain Aspects of a Simple Random
   Walk with One Random and One Non-Random Absorbing Barrier，
   DOI 10.1080/03461238.1980.10408651；
3. Erik Zierke（1998），Absorption Probabilities of a Brownian Motion
   in a Triangular Domain，DOI 10.1007/978-1-4612-2234-7_14；
4. Sobel 与 Frankowski（2002），
   DOI 10.1016/S0378-3758(01)00191-4。

其中 Zierke 的 Springer 章节页和马格德堡大学预印本目录可以确认标题、
作者与三角域 Brownian 吸收主题：

- [Springer 图书/章节入口](https://link.springer.com/book/10.1007/978-1-4612-2234-7)
- [OVGU 预印本目录](https://math.ovgu.de/Forschung/Ver%C3%B6ffentlichungen/Preprints_%2BTechnical%2BReports%2B%28alte%2BVersion%29/Preprints/1996-p-2734.html)

这条引用链证明 Barnett（1964）处在“非对称二维随机游走—三人破产—
三角域吸收”方法谱系中，但不能凭被引关系恢复其精确一步转移规则。
OpenAlex 的四条记录也不是 MathSciNet、zbMATH、Scopus 或 Web of
Science 的完整性替代。

## 5. 对四项同构判据的当前裁决

| 判据 | 当前公开证据 | 裁决 |
|---|---|---|
| 每步成对单位转账 | 标题与 extract 不给完整核 | 未决 |
| 固定一般 \(k\) | 标题明确是三人扩展 | 不满足一般 \(k\)，但可能覆盖 \(k=3\) 特例 |
| 中心偏置 \(p_N=1+\eta/N\) | 公开页无该尺度 | 未决，不能据此判为不存在 |
| 首次到零的分布与矩极限 | 公开页无完整定理 | 未决 |

因此 Barnett（1964）在证据表中的状态仍应为 manual-needed。现在能够
排除的只有“它给出了固定一般 \(k\) 的结论”；不能排除它与本项目
\(k=3\)、固定不对称特例部分重合。

## 6. 下一步合法获取协议

在用户确认补充材料选择后：

1. 先检查 JSTOR/Cambridge 当前登录会话是否有机构访问，不绕过平台控制；
2. 若允许正文但页面无 Supporting Information，则下载正文并记录
   实际入口、文件哈希和获取日期；
3. 若存在补充材料，严格按用户选择一并获取或明确跳过；
4. 若机构路径不可用，检查作者/机构仓储和馆际文献传递，不使用非授权源；
5. 全文取得后逐页摘录模型状态、一步转移核、停止事件、主要定理和渐近
   参数，并更新四项同构表；
6. 再用 MathSciNet/zbMATH/Scopus/WoS 做正式双向引用追踪。

在上述步骤完成前，论文可以写“Barnett（1964）是待全文核验的最近三人
先例”，不得写“Barnett（1964）与本文模型不同”。
