# 弱漂移证明与先行工作纠偏 QA

日期：2026-07-17

## 1. 本轮改变

1. 确认公平三人/三塔公式 \(3xyz/(x+y+z)\) 至少已有 Engel（1993）和
   Bruss、Louchard、Turner（2003）直接先例；项目文件已统一改为
   “已知解析基线”。
2. 确认 Alabert、Farré、Roy（2004）已覆盖同一三人随机游走的 Brownian
   三角形退出、退出时间与期望收敛以及 Poisson 解；三人零漂移扩散不再
   作为候选创新。
3. 确认 Swan、Bruss（2006）及 Marfil、David（2024）已用吸收 Markov/
   线性系统求一般多人首次破产；项目不再把 \((I-Q)u=\mathbf1\) 的形式
   本身作为原创主张。
4. 新建 07_weak_drift_proof_package.md，闭合固定 \(k\) 中心偏置弱漂移的
   FCLT、退出时间连续集、统一可积性和 PDE 识别。

## 2. 关键证明核查

| 检查项 | 核查结果 |
|---|---|
| 一步弱漂移均值 | \(\mathbf d_N=\boldsymbol\beta_\eta/N\) |
| 中心化协方差 | \(A_0-\mathbf d_N\mathbf d_N^\top\to A_0\) |
| 切向生成元 | \(\boldsymbol\beta_\eta^\top\nabla+(k-1)^{-1}\Delta_{\rm tan}\) |
| 面法向非退化性 | 每个坐标方差 \((A_0)_{ii}=2/k>0\) |
| \(\eta=0\) 全状态均值界 | \(\sup_xE_x\tau_N\le k(k-1)N^2/2\) |
| \(\eta>0\) 全状态均值界 | \(\sup_xE_x\tau_N\le k^2(k-1)N^2/(2\eta)\) |
| \(\eta<0\) 全状态均值界 | \(\sup_xE_x\tau_N\le k^2N^2/(2|\eta|)\) |
| 强 Markov 分块尾 | 块长 \(\lceil2AN^2\rceil\) 下尾概率至多 \(2^{-m}\) |
| 期望收敛 | 分布收敛 + 统一几何尾推出一致可积与均值收敛 |
| PDE 边界正则性 | 只称唯一有界弱/黏性解和内部经典解，不声称角点到边界 \(C^2\) |

## 3. 声明等级

- 弱漂移：A（当前工作稿证明闭合；待独立概率论核查）。
- 三人闭式和三人零漂移扩散：A（正确），但明确非原创。
- 一般吸收 Markov 方程：A（正确），但属于标准方法基线。
- 正漂移二阶竞争修正：C，未升级。
- v4：E，仍是离散网格经验代理。

## 4. 尚未解除的质量门

- 未完成 MathSciNet/zbMATH/Scopus/WoS 的穷尽引用追踪。
- 弱漂移证明尚未由独立概率论研究者逐行复核。
- 尚未为 FCLT、连续映射和 PDE 唯一性固定目标期刊版本的精确定理编号。
- v4 一键拟合复原脚本仍待用户批准后实施。

## 5. 证据文件

- ../07_weak_drift_proof_package.md
- ../sources/literature_claim_map_2026-07-17.md
- ../sources/references.bib
- ../06_theorem_proof_gap_register.md

## 6. 可复现核验结果

- 回归测试：在 `E:\newblockchain` 运行 `python -m unittest -v`，共 11 项，
  全部通过（本次复核运行 9.056 s）。
- 增量恒等式枚举：对 $k\in\{2,3,4,7,10\}$ 及多组 $N,\eta$ 逐方向
  枚举；一步均值最大绝对误差为 $1.145\times10^{-16}$，协方差最大绝对
  误差为 $2.220\times10^{-16}$。
- 文档链接：核验 17 份 Markdown 中的 60 个本地链接，断链为 0。
- HTML 同步：4 份根目录报告的数学占位符均为 0；共 8 个 `img` 标签，
  其中 6 个本地图像引用全部存在，其余为内嵌/外部资源。
- 参考文献：`references.bib` 含 8 条记录，重复键为 0，花括号平衡。
- 陈旧主张扫描：关于“首次提出三人公式”或“首次提出一般多人 Markov/
  Poisson 方程”的命中均出现在禁止性或纠偏性语境；未发现仍把它们列作
  当前原创贡献的有效文本。
