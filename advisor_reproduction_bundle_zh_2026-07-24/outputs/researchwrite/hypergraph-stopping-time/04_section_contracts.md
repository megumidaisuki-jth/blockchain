# Section contracts

## Project-wide authority ceiling

独立通道/超边生存函数乘积是 Podiatchev–Orda–Rottenstreich (2024) 直接覆盖的基线；本项目只复现并用作相关网络对照。

- T16：A — internally closed and code-reproducible under explicit finite-state depletion reachability; Task 6 exact residual/reachability gates pass。
- T17A/B/C：A — all proof modules internally closed after formal fix 1; numerical phase grids are diagnostic only, and the `alpha=0.5` finite grid is not convergence validation。
- T18a：A — internally closed and code-reproducible only for the joint Gaussian diffusion limit with zero cross-hyperedge covariance blocks。
- T18b：E / mixed — frozen increment-law non-factorization is exact; paired stopping-time differences are frozen-design numerical observations; no universal sign theorem。
- Task 9：精确生存序列化容差归一化和冻结证据最终 QA 已通过；该债务已清除，2026-07-17 HTML 只待用户视觉确认。
- Task 10：开放来源多源审计和八项同构表已通过 QA；MathSciNet/zbMATH/Scopus/WoS/CNKI 机构检索仍未完成。
- T19：平衡零漂移二元通道的离散—高斯生存序桥接已内部闭合，独立子 agent 验收为 ACCEPT、0 阻断且 5 项非阻断补救全部关闭；人类专家签核不再是项目门，不得改写为有限 \(N\) 符号定理。
- T32：真实拓扑需求插值给出有限网格机制证据；λ=0、0.5、1的同时区间分离，八锚点平均斜率为负；四日期聚类和后验分析边界必须并列报告。
- T34：现实语义已闭合为“触边与支付失败严格非等价”；139,968 条小状态序列索引核查零违例。写作启动门禁通过，但 publication readiness 仍为 false：机构数据库确认、Barnett（1964）全文边界、完整中文稿件和中文目标期刊格式化未完成。

## Introduction / Related work

- Purpose: 建立从双边 channel depletion 到多方通道单纯形退出问题的缺口。
- Inputs: Shabgahi et al. 2022 通道有效寿命、Dehshali et al. 2022 吞吐上限、
  2024 survivable PCN、Kim 2023 多方通道、Kotzer et al. 2025 超图 PCN、
  2025 H-MPC/Horcrux、Sankagiri–Hajek 2025/2026、2026 PCN 几何理论、
  depletion/路由文献、Denisov–Sakhanenko–Wachtel 2021 三角阵 first-passage、
  Engel 1993、Bruss et al. 2003、Alabert et al.
  2004、Sobel & Frankowski 2002、Swan & Bruss 2006、Grigorescu & Yao
  2016、Diaconis, Houston-Edwards & Saloff-Coste 2021、Diaconis & Ethier
  2022、O'Connor & Saloff-Coste 2023、Marfil & David 2024、Denisov &
  Wachtel 2024、Kehagias et al. 2025、Barnett 1964、Rocha & Stern
  1999/2004、Kmet & Petkovšek 2002、Tzioufas 2019、Ekhad & Zeilberger
  2023、Hussain et al. 2023、Phetpradap & Sripanitan 2025。
- Allowed claims: 支付通道有效寿命、拓扑—寿命关系、单通道 stopping time
  和网络首通道失败已有直接先例；多方/超图通道与跨超边协议语义已出现；
  Podiatchev et al. 明确指出多跳路由使通道独立假设不合理；在已核验开放
  来源中未发现八项完全同构结果，但机构数据库仍待确认。公平多人首次破产
  的低维闭式、扩散和 Markov 计算已有直接先例；非对称一般 \(n\) 人和
  不同模型的全矩结果也已有先例。
- Forbidden claims: “首次研究支付通道寿命/stopping time”“首次研究拓扑—寿命关系”
  “首次超图建模”“首次提出多方/跨超边支付”“此前无人研究多维赌徒破产”“公平随机
  选对多人模型由本文提出”“四人单纯形/Brownian 路线由本文首次提出”
  “首次研究非对称一般 \(n\) 人 ruin”“三角阵 first-passage 由本文提出”
  “全矩本身即原创”或任何“全球首次”。
- Required evidence: 可核 DOI/预印本、完整文献检索日志、逐条新颖性对比。
- Validation checklist: 每个新颖性句子都能指向检索范围和对照文献。

## Model and stopping event

- Purpose: 定义状态、时间、交易机制和停止事件。
- Inputs: \(k,C,\sigma,N,\Pi,p,\tau\)。
- Allowed claims: 这是多方通道内首次方向性余额耗尽模型；触边支付在单位理想合同中仍被接受，首次拒绝是另一执行前时钟；二者在现实协议中无普适等式或先后序。
- Forbidden claims: 直接等同协议永久关闭、网络断连或支付失败。
- Required evidence: 状态更新概率非负且归一；时间单位明确；T34 双时钟定义、BOLT 事实来源与索引核查。
- Validation checklist: 全文同一符号同一含义；中心偏置与一般 \(\Pi\) 分开；不得把执行后触边时间 \(\tau\) 与执行前拒绝时间 \(\rho\) 混用。

## Exact theory

- Purpose: 复述并复推 \(k=2,3\) 已知基线，给出一般 \(\Pi\) 的标准 Poisson
  实现、项目吸收性证明和可用于后续渐近的有限容量界。
- Inputs: 生成元、势函数、边界、可选停止条件。
- Allowed claims: 完成证明的命题和定理；T16 可写为显式有限状态耗尽可达性下“内部证明闭合、代码可复现”的相关网络吸收与 Poisson 方程；不得写成已同行评审。
- Forbidden claims: 将标准 Markov 方程宣传为普适初等闭式。
- Required evidence: 几何尾吸收引理、完整证明、独立符号核查、精确求解残差。
- Validation checklist: 每个定理的假设、结论、证明和边界案例齐全。

## Drift asymptotics

- Purpose: 解释弱漂移、强负漂移和强正漂移的不同尺度。
- Inputs: 漂移向量、协方差、Péclet 数、PDE、竞争极值。
- Allowed claims: 固定非零漂移的一阶极限和固定 \(k\) 中心偏置弱漂移
  退出极限可作为“内部证明链已闭合、可执行核查通过”的定理工作稿；弱漂移
  的统一指数矩推出所有固定正阶矩收敛；固定非零强漂移还可主张相对指数
  集中、统一指数矩与全部固定正阶矩收敛；正漂移二阶项仍标为命题/猜想并
  给数值证据。可把二者统一为 \(p_N=1+\eta N^{-\alpha}\) 的三分区
  相图工作稿，但必须并列说明内部工作稿状态和小漂移先例。
  在网络合同 12 的固定维外生路由条件下，T17A/B/C 可写为 formal fix 1 后“全部证明模块内部闭合”；Task 6 相图网格只作诊断，`alpha=0.5` 有限网格不得承担收敛验证。
- Forbidden claims: 以 Taylor 展开代替弱收敛证明；把拟合误差包络称为理论界；
  把 FCLT、连续映射和 Feynman--Kac 的标准组合本身称为主要数学创新；把
  内部对抗式审计称为独立同行核查；在 Barnett 1964 全文未核验时声称
  三人非对称特例无先例。
- Required evidence: 不变原理、退出时间连续映射、统一指数矩/一致可积性、
  集中性或误差阶证明；PDE 的变分弱解与连续黏性解分别表述；09、14评审表
  仅作为可选导师审阅清单保留，不再要求人类签名；代码、精确锚点和子Agent审计必须可复现。
- Validation checklist: 渐近参数明确（固定 \(k\)、\(N\to\infty\)、\(p\) 如何缩放）；
  每个“已证明”标签都与内部工作稿、适用范围和可复现证据状态并列。

## Numerical validation

- Purpose: 验证精确求解器、渐近式和经验代理，显示失效区域。
- Inputs: exact Markov、独立 MC、训练/开发/盲测划分、原始或可重建轨迹。
- Allowed claims: 离散网格上的误差统计和明确的区间方法。
- Forbidden claims: 连续域一致保证、所有 2,112 点均未见、以 PASS 比例替代误差分布。
- Required evidence: v4 拟合脚本、冻结记录、环境、随机种子、稳健区间敏感性。
- Validation checklist: 独立单位是轨迹；场景级 (n) 明确；多重比较策略和图例完整。

网络证据还必须逐项指向 `results/network` 的精确残差/可达性、Monte Carlo、相图、配对代理、生存曲线、metadata 和 SHA-256 清单。Task 9 已通过运行最小值容差验证清除精确生存序列化债务；后续重生成证据时必须重新通过同一门禁。

## Network extension / Discussion

- Purpose: 区分直接先行工作覆盖的独立聚合、内部闭合的固定相关网络工作稿和仍未完成的跨拓扑/现实路由外推。
- Inputs: 合同 12、证明包 13、评审包 14、Task 6 冻结网络证据。
- Allowed claims: T16 在有限状态耗尽可达性下内部闭合；T17A/B/C 在 formal fix 1 后内部闭合；T18a 只在联合 Gaussian 极限零跨块条件下内部闭合；T18b 只给冻结非因子化严格结论与冻结数值误差诊断。
- Forbidden claims: 把独立聚合当成一般网络定理。
- Required evidence: 依赖结构定义、13 证明包、Task 6 网络级精确/模拟/哈希证据、T19子Agent验收、T32正式/复跑机制产物；14只作可选审阅清单。
- Validation checklist: 讨论明确回应“本文研究固定相关 network，但证明仍是内部工作稿、非同行评审”；不得把停止事件改称支付失败、路由失败、通道关闭或网络断连；不得给相关误差赋予普遍符号。
