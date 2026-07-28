# T12 正漂移竞争二阶定理与正式验证最终 QA

**日期**：2026-07-18（Asia/Hong_Kong）  
**范围**：固定整数 $k\ge3$、固定 $p\in(1,2]$ 的正漂移外围竞争二阶定理，耦合模拟、精确 Markov 锚点、36 单元正式主运行、独立异种子复跑、同时区间、证据完整性与项目状态同步。  
**结论**：内部数学、实现、精确锚点、精度、复跑、manifest、全量回归和保护证据门禁全部通过。T12 可标记为 **A—内部闭合、外部评审未签署**；`publication_readiness=false`。有限网格诊断不构成渐近定理的证明。

## 1. 证明闭合边界

[T12 证明与验证文档](../17_t12_positive_competition_proof_and_validation.md)在固定 $k,p$、仅令整数 $N\to\infty$ 的合同内证明：

1. 外围增量协方差满足 $\gamma-c=2/(k-1)$；
2. 确定性时刻的多元 CLT、紧致窗口最大不等式、严格同时穿越和中心坐标指数排除共同给出
   \[
   \frac{\tau_N-t_N^*}{\sqrt N}\Rightarrow H;
   \]
3. 两段尾界给出每个固定实数 $q>0$ 的绝对矩收敛；
4. Gaussian 投影计算给出
   \[
   \mathbb E\tau_N=t_N^*-
   \frac{\kappa_{k-1}}{v}\sqrt{\frac{k}{p-1}}\sqrt N+o(\sqrt N).
   \]

独立内部审阅逐模块重算量词、一步矩、CLT、窗口噪声、首次穿越、中心去除、两段尾界、统一可积性、Gaussian 投影和均值展开，未发现剩余内部数学缺口。当前标签不表示同行评审通过；外部概率论研究者未签署，若外审否定任一证明模块，T12 必须降回 C，二阶式只能作为理论引导的经验修正。

## 2. RED→GREEN 实现历史

所有生产接口均先出现与目标接口对应的失败，再实现并回归。完整逐项记录见 [Task 1](../../../../.superpowers/sdd/t12-task-1-report.md)、[Task 2](../../../../.superpowers/sdd/t12-task-2-report.md)、[Task 3](../../../../.superpowers/sdd/t12-task-3-report.md)和 [Task 4](../../../../.superpowers/sdd/t12-task-4-report.md)。

| 模块 | RED 证据 | GREEN 证据 |
|---|---|---|
| 外围增量律与常数 | 缺少 `t12_positive_competition_validation`，导入失败 | 理论测试 3/3；既有漂移测试 3/3 |
| 共享自由延拓/首次耗尽模拟 | 缺少 `simulate_coupled_competition` | 模拟测试 3/3；T12 当时全套 6/6 |
| 分块统计与 Gaussian 诊断 | 缺少 `bonferroni_t_critical`；随后捕获 cell-ID 与零方差临界值缺陷 | 统计测试 6/6；`-W error` 无 precision-loss warning |
| 产物管线 | 缺少 `run_exact_anchors` | 首轮产物测试 5/5，T12 17/17 |
| 评审修复：比较输入完整性 | 截断为一行的两个 CSV 被错误接受 | 强制完整 schema、规范 36 单元、每轮 36 唯一种子且跨轮不交叠 |
| 评审修复：CLI 显式零 | 显式 `0` 被 truthy 默认值替换 | 用 `is not None` 转发，真实 CLI 验证器拒绝零值 |

评审修复后的 T12 专项结果为 19/19；当时全项目回归为 76/76。最终 fresh 回归见第 7 节。

## 3. 模拟语义与性能检查点

- 每条轨迹在 $n_\star=\lfloor N/v\rfloor$ 前都沿同一自由增量流推进，即使已经首次耗尽；$n_\star$ 后只推进尚未耗尽者。
- 首次耗尽时间和终止余额只记录一次；无时间上限、删失、事后排除或失败单元替换。
- 20,000 路径边际交叉核验在 $(k,N,p)=(4,8,1.5)$ 得到：耦合模拟均值 `37.98100000`，旧独立实现均值 `37.89795000`，差 `0.08305000`，小于 `3.5×` 合并标准误 `0.56437013`。
- 非正式最慢格性能检查 `simulate_coupled_competition(5,320,1.25,2000,12003)` 用时 `2.3477935 s`。

## 4. 精确锚点与正式运行

正式运行命令、运行时、逐项算术与哈希详见 [Task 5 报告](../../../../.superpowers/sdd/t12-task-5-report.md)。四个权威结果入口为 [精确锚点](../../../../results/t12-positive-competition-exact-anchors)、[主运行](../../../../results/t12-positive-competition)、[独立复跑](../../../../results/t12-positive-competition-replication)和[复跑比较](../../../../results/t12-positive-competition-replication-comparison)。

| 运行 | 设计 | 墙钟时间 | 关键门禁 |
|---|---|---:|---|
| 精确锚点 | 9 个 $(k,p)$，$N=6$，每格 100,000 路径，100 块 | 6.501 s | 9/9 精确均值在同时区间内；最大 Poisson 残差 `3.197442310920451e-14`；零删失 |
| 正式主运行 | 36 单元，每格 20,000 路径，40 个不重叠 500 路径块 | 82.539 s | 最大确定性矩误差 `2.220446049250313e-16`；最大同时半宽 `0.025877691320792203≤0.03`；零删失 |
| 独立复跑 | 相同 36 单元，36 个新种子且与主运行全不相交 | 82.868 s | 最大同时半宽 `0.023650625361005862`；零删失 |
| Welch 比较 | 两轮 40 块修正比，36 重比较 | 1.442 s | 36/36 同时 95% 区间包含零；失败单元为 0 |

独立算术重算的最大误差：主运行分块 SE `4.336808689942018e-18`、修正比恒等式 `2.220446049250313e-16`、区间端点 `1.387778780781446e-17`；复跑对应为 `5.204170427930421e-18`、`2.220446049250313e-16`、`1.734723475976807e-17`；Welch 差值 `0`、SE `1.734723475976807e-18`、自由度 `4.263256414560601e-14`、区间端点 `1.387778780781446e-17`。

## 5. 条件敏感性决策

未运行敏感性。预注册触发条件是主运行任一同时半宽超过 `0.03`，或任一主运行—复跑 Welch 同时区间排除零。本次最大半宽为 `0.025877691320792203`，36/36 Welch 区间包含零，因此触发集合为空，`results/t12-positive-competition-sensitivity` 按设计保持不存在。没有事后选择单元。

## 6. T12 权威数值哈希与 manifest

四份 `SHA256SUMS.txt` 均按清单逐项重算，合计 11 个被列文件，错配 0；manifest 不列自身。

| 产物 | SHA-256 |
|---|---|
| 精确锚点 CSV | `5375af593085e963bdb61823c9bd4cef2c12f4c0c5f96a7a2923694a9f6bca83` |
| 精确锚点 metadata | `4cb734924c715f1e97e6444634e42b5cffe91383d7c42f2ca509038c81310a9c` |
| 主运行 CSV | `a00cab8a779415508f5022b899f28e9968f31787488b988ed1c4ae2e37793527` |
| 主运行矩诊断 CSV | `fd2c727660a4044e43508d61d8d53cf8d9350564918077dca1e7b5609407b7bc` |
| 主运行 metadata | `a22634f479be122c3ba5d4ed48c0c95b75c01199bc31b2fa7f8cd48c6ac6ef7e` |
| 复跑 CSV | `ec61ed161615ddcf2069d36077a0732d7a2e624a044b9a1cea9c30e302495410` |
| 复跑矩诊断 CSV | `fd2c727660a4044e43508d61d8d53cf8d9350564918077dca1e7b5609407b7bc` |
| 复跑 metadata | `aa1aaaf076077803c77fa4cd1179b761c94c17304f71fccd83e3a94d5a4be8d4` |
| 比较 CSV | `2b4a1065b99cb62fd671cd9b9fd142b2d259d74511d38c4ac04cbbf65bf270e8` |
| 比较 metadata | `cc651b824340ceb5fcdfef89d569248ee48620e090c757a44bf9f52d147ca035` |
| 比较失败单元文件（空文件） | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## 7. 最终技术与文档验证

最终 fresh 命令：

```powershell
python -m py_compile t12_positive_competition_validation.py test_t12_positive_competition.py
python -W error -m unittest -v
```

结果：编译静默成功；全项目 **76/76** 测试在 `56.108 s` 内通过，退出码 0。PowerShell 启动时因本机执行策略不能加载用户 profile 的环境提示不属于 Python warning；测试本身在 `-W error` 下无 warning/error。

最终只读证据脚本还验证：

- UTF-8 JSON 可解析，T12 四个 metadata 的汇总 gate 均为 true；
- 主运行/复跑各 36 行，精确锚点 9 行，比较 36 行，零删失，失败单元 0；
- README、文档 06/17/15 和本 QA 的所有本地 Markdown 链接存在；
- README、01、02、06、10、15、17、本 QA 和 `state.json` 无禁止控制字符；
- live 文档中不存在把 T12 继续标为 C、未闭合或“需要强近似”的旧句；
- `[机器状态](../state.json)` 为 `submission_completion_percent=71.75`、`publication_readiness=false`，且不含 `positive_drift_competition_error_not_bounded`；
- 外部评审签名仍为 0，未把内部 QA 当作外部签核。

## 8. 既有保护证据

下列 11 个既有结果文件和冻结 HTML 均逐字节保持既有哈希；T12 工作未修改或重渲染它们。

| 文件 | SHA-256 |
|---|---|
| `network-correlated-vs-proxy.csv` | `08f7a5df559b9eee613fabff1f29375e9c40d50537e39668d19bbe370ff25dda` |
| `network-exact.csv` | `4a95eb7d31b4cfb6f397c721d5d7258520d468ed789b01b880e360c24d5984db` |
| `network-mc-exact-check.csv` | `bf1053d1f838d82eee15735a57041f2e01010eb10c904e8f6e42924f3e2b6aa4` |
| `network-phase-scaling.csv` | `774b47efb90a4de16503ca3bb6684c582375449534817e639e528c053db23b43` |
| `network-survival-curves.csv` | `6b4d12ecb3d90ff2e631b65ddcb50e6e9db8fa9beb58108d1e865370a27b680a` |
| T18 主运行 `t18-primary-effects.csv` | `d9436daa71457d3f6c58cf02767b0204a178177a9f8d4367eec94a57d6ecd234` |
| T18 主运行 `t18-kernel-diagnostics.csv` | `38779a494c53b824410894c7f5d8c11beca79be74001154fe82cbfa03d160808` |
| T18 最弱单元敏感性 CSV | `0b3009f557758bc392ef5a097234c3cd68bc08420d53bea15f800bb16b5abf79` |
| T18 精确锚点 CSV | `b9ada3e30ca5ea82e1d5bc4683f0370570c22a610868f2bfc36b8879bf54734d` |
| T18 完整复跑 `t18-primary-effects.csv` | `d9436daa71457d3f6c58cf02767b0204a178177a9f8d4367eec94a57d6ecd234` |
| T18 完整复跑 `t18-kernel-diagnostics.csv` | `38779a494c53b824410894c7f5d8c11beca79be74001154fe82cbfa03d160808` |
| 根目录冻结 HTML | `babf45d3ee1ae1455dfbf8d6c6d78d05fb296b87fdec6aca2902dc4a9b4f88cb` |

## 9. 完成度算术与当前文件哈希

[权威完成度清单](../15_submission_readiness_and_venue_strategy_2026-07-18.md)沿用原有八模块权重。本轮只把“内部证明闭合”从 85% 提升到 100%，其 20% 权重贡献从 17.00% 增至 20.00%，因此

```text
15.00 + 20.00 + 14.25 + 9.75 + 10.00 + 0.00 + 0.50 + 2.25 = 71.75
```

完成度为 **71.75%（约 72%）**，不是录用概率。外部独立评审仍为 0%，所以没有增加该模块贡献。

| 文件 | SHA-256 |
|---|---|
| `t12_positive_competition_validation.py` | `2545ea8378468e844cef15e86847d8bbce4aadd29a0952548573e707e69909eb` |
| `test_t12_positive_competition.py` | `8df80cb5a03a2169fd60a179eb6447b51bae77be9e08617131b8ed1958dbe182` |
| `17_t12_positive_competition_proof_and_validation.md` | `7bcfa5325812a50adddc8610459c1358b92e92661b9729cfd9bd824b1e267f5b` |
| `06_theorem_proof_gap_register.md` | `8ec3ba71805552c2e2dddc52f8818ae89ae284695e7939ed011a7792d3596681` |
| Task 5 报告 | `9fc5edfbe8172d5b6e9b7dd4abc79d3459a3419cc8174d96ff2bbbec4e9923c0` |
| Task 6 报告 | `6e0721a4abb7fd07d9ca5aee0622c3ca2edfe9e47da401dbf035e6ebbae1a64d` |
| `README.md` | `fd4af318bacc0cb5ad50d05fef41780c2091db22503cca0d7846299ad26e3265` |
| `15_submission_readiness_and_venue_strategy_2026-07-18.md` | `25a5f2f7ce05f70b41f76f71963961588831fb40668e86e64b9db6748e14e8b9` |
| `state.json` | `4037a0e2f504ee13edc6dc45dacb571e2f939b2461ec5b5f929342a1d3066faf` |

本 QA 不嵌入自身哈希，避免自引用改变摘要。

## 10. 仍未通过的门禁

1. 弱漂移、强漂移、多项式漂移相图、T12 与相关网络定理的外部独立概率论签核；
2. MathSciNet、zbMATH、Scopus、Web of Science、CNKI 的机构检索，以及 Barnett 1964 全文模型核验；
3. 旧 v4 拟合生成链；
4. 公开 Lightning/透明需求到原子超边路由核的可审计映射；
5. 首次余额耗尽与真实支付失败、再平衡、通道关闭的语义校准；
6. 完整英文论文、逐句证据审计、目标期刊模板和投稿前反方预审。

因此本任务只关闭 T12 的内部证明与验证阶段，不启动论文写作，不把项目标记为可投稿，也不代表最终发表目标已经完成。
