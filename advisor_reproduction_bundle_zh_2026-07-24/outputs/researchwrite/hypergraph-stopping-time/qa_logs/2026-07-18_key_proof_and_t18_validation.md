# 关键证明与 T18 正式验证 QA 日志

**日期**：2026-07-18  
**范围**：T16–T18 证明桥接、T18-A 36 单元正式实验、完整复跑、最弱单元敏感性、三拓扑精确锚点、项目状态同步。  
**结论**：本轮内部证明与计算 QA 全部通过；外部概率论签核仍未完成，`publication_readiness=false`。

## 1. 证明核查

1. T16 的吸收、谱半径和 Poisson 唯一性继续显式依赖有限状态耗尽可达性，没有从渐近协方差非退化倒推有限 $N$ 吸收。
2. T17A 的早尾、晚尾和统一指数矩分别核查了初态/漂移收敛余项、floor 误差和长尾块常数。
3. T17B/C 的过程极限、退出映射连续性、逐面立即穿越、全状态 $O(N^2)$ 均值界和几何块指数矩继续保持独立步骤。
4. T18a 只在联合 Gaussian 极限中使用零交叉协方差推出块独立。
5. 新增临界互逆路由扰动引理：
   \[
   N d_N^{(s)}=2sa\zeta,
   \qquad
   \Gamma_N^{(s)}=\Gamma_0-d_N^{(s)}d_N^{(s)\mathsf T}.
   \]
   该结论由互逆增量外积相同直接推出。
6. 证明包仍标记 `internal, unsigned`；R01–R14 没有外部签名。

## 2. 测试驱动实现记录

所有新生产接口都先写测试并观察预期失败，再实现最小功能：

| 功能 | RED 证据 | GREEN 证据 |
|---|---|---|
| T18 场景构造 | `ModuleNotFoundError: t18_cross_topology_validation` | 3 个初始场景测试通过 |
| 核恒等式诊断 | `cannot import name kernel_diagnostics` | 36 单元确定性门禁测试通过 |
| 配对统计与产物 | `cannot import name run_t18_validation` | 快速运行写出完整 manifest |
| 活跃并集模拟器 | `cannot import name simulate_paired_proxy_active` | 可重复性、$N=1$ 和跳过吸收行测试通过 |
| 敏感性统计 | `cannot import name summarize_sensitivity` | normal/path-$t$/block-$t$ 算术测试通过 |
| 常数差边界 | 捕获到 SciPy precision-loss warnings | 常数差无 warning，约定偏度/峰度为 0 |
| 最弱单元 runner | `cannot import name run_weakest_sensitivity` | 快速产物测试通过 |
| 精确锚点 runner | `cannot import name run_exact_anchors` | $N=1$ 恒等锚点通过 |
| 拓扑非同构 | 旧随机种子得到 $[1,1,2,2]\ne[1,1,1,3]$ 的断言失败 | 种子 7 得到链/星/分支三种不同度序列 |

旧 `network_phase_validation.py::simulate_paired_proxy` 未被修改，因此 Task 6 冻结证据的生成语义不受影响。T18 使用新 `simulate_paired_proxy_active`；它只对仍在任一模型中活跃的轨迹并集生成共同随机数。正式元数据中的随机行比例为朴素方案的 17.5%–26.4%。

## 3. 拓扑设计缺陷与纠正

原计划中的 `random_connected_triads(4, seed=20260718)` 具有超边交叠图度序列 $[1,1,2,2]$，与 chain 同构。该问题在第一次两轮正式运行后的精确锚点检查中被发现。

处置：

1. 新增永久结构回归测试；
2. 改用 seed 7，其度序列为 $[1,1,1,3]$；
3. 原两次正式运行和原精确锚点移入三个 `rejected-seed20260718` 审计目录，不进入论文证据；
4. 用 seed 7 从头完整运行两次 36 单元实验，并重新求解三拓扑精确锚点；
5. 未复制或合并旧 CSV 行。

这项修正改变了随机拓扑结果：旧链同构拓扑均值差约为 0.0961–0.1104；修正后的分支拓扑为 0.0790–0.0903。

## 4. 正式 T18-A 设计与结果

- 三拓扑：chain、common-hub star、seed-7 random branch；交叠度序列分别为 $[1,1,2,2]$、$[3,3,3,3]$、$[1,1,1,3]$。
- 三漂移：balanced、$+0.01/N$、$-0.01/N$。
- 四尺度：$N=10,20,40,80$。
- 每单元 30,000 对独立轨迹；合计 1,080,000 对主实验轨迹。
- 主端点：$(\tau_{\rm corr}-\tau_{\rm proxy})/N^2$。
- 36 重比较 Bonferroni normal 临界值：3.1969502291312546。
- 预定最大半宽：0.02。

结果：

| 项目 | 核验值 |
|---|---:|
| 主效应行 | 36 |
| 核诊断行 | 36 |
| 同时区间严格为正 | 36/36 |
| 最大半宽 | 0.0142735571 |
| 最小下界 | 0.0015783859 (`star-balanced-N80`) |
| CI 独立重算最大误差 | $6.94\times10^{-18}$ |
| 缩放漂移最大误差 | $6.68\times10^{-15}$ |
| 二阶矩/协方差恒等式最大误差 | $1.05\times10^{-15}$ |
| 代理边际均值最大误差 | $3.82\times10^{-16}$ |
| 代理边际协方差最大误差 | $1.17\times10^{-15}$ |

正式运行用时 959.264 秒；完整复跑用时 963.649 秒。两个目录的主效应 CSV 和核诊断 CSV 分别逐字节相同，config SHA 和 input SHA 一致，两份 manifest 均通过重算。

## 5. 最弱单元敏感性

`star-balanced-N80` 使用新种子和 100,000 对轨迹重新估计：

- 均值差：0.0226528891；
- Bonferroni normal 下界：0.0148823925；
- path-level Student-$t$ 下界：0.0148821745；
- 100 个不重叠批次均值 Student-$t$ 下界：0.0147959703；
- 三种区间均为正；
- 偏度 0.0786621，超额峰度 1.5477318；
- 无删失、无排除、无固定步数截断。

因此已移除 `bonferroni_normal_claim_needs_robust_interval_sensitivity` 技术债。

## 6. 精确—Monte Carlo 锚点

三类四超边拓扑在 $N=2$ 均有 10,000 个内部状态：

| 拓扑 | 精确均值 | MC 均值 | $z$ | 最大残差 | 全状态可达 |
|---|---:|---:|---:|---:|:---:|
| chain | 3.6912343407 | 3.68928 | -0.34837 | $2.71\times10^{-14}$ | Yes |
| star | 4.0273888655 | 4.02829 | 0.14526 | $3.19\times10^{-14}$ | Yes |
| random branch | 3.7271237112 | 3.73504 | 1.38440 | $2.78\times10^{-14}$ | Yes |

全部满足 $|z|<3.29$、残差 $<10^{-10}$ 和可达性门禁。

## 7. 回归、格式与链接 QA

Fresh full regression：

```text
python -m unittest -v
Ran 57 tests in 42.827s
OK
```

另通过：

- `python -m py_compile t18_cross_topology_validation.py test_t18_cross_topology.py`；
- 5 个 JSON 文件 UTF-8 解析；
- 4 份 manifest 重算；
- 4 个修改后的权威 Markdown 文档控制字符检查；
- 所有本地 Markdown 链接解析；
- 36 行区间端点和半宽独立重算；
- `state.json` 完成度、技术债和 `publication_readiness=false` 一致性检查。

## 8. 受保护旧证据

以下 SHA-256 均与此前 QA 记录相同：

| 文件 | SHA-256 |
|---|---|
| `network-correlated-vs-proxy.csv` | `08f7a5df559b9eee613fabff1f29375e9c40d50537e39668d19bbe370ff25dda` |
| `network-exact.csv` | `4a95eb7d31b4cfb6f397c721d5d7258520d468ed789b01b880e360c24d5984db` |
| `network-mc-exact-check.csv` | `bf1053d1f838d82eee15735a57041f2e01010eb10c904e8f6e42924f3e2b6aa4` |
| `network-phase-scaling.csv` | `774b47efb90a4de16503ca3bb6684c582375449534817e639e528c053db23b43` |
| `network-survival-curves.csv` | `6b4d12ecb3d90ff2e631b65ddcb50e6e9db8fa9beb58108d1e865370a27b680a` |

冻结 HTML 的既有哈希 `babf45d3ee1ae1455dfbf8d6c6d78d05fb296b87fdec6aca2902dc4a9b4f88cb` 仍能在根目录匹配到唯一文件；本轮未修改或重渲染该 HTML。

## 9. 当前权威哈希

| 文件 | SHA-256 |
|---|---|
| `t18_cross_topology_validation.py` | `2d9cf6ebeb80819ab11f843a48d27ddd5d9a596b7da520be3ad47f9445c90765` |
| `test_t18_cross_topology.py` | `69ad388a263c28f326702d682014cf8dfa184bd658d05878fe279557c271e049` |
| `t18-primary-effects.csv` | `d9436daa71457d3f6c58cf02767b0204a178177a9f8d4367eec94a57d6ecd234` |
| `t18-kernel-diagnostics.csv` | `38779a494c53b824410894c7f5d8c11beca79be74001154fe82cbfa03d160808` |
| `t18-weakest-cell-sensitivity.csv` | `0b3009f557758bc392ef5a097234c3cd68bc08420d53bea15f800bb16b5abf79` |
| `t18-exact-anchors.csv` | `b9ada3e30ca5ea82e1d5bc4683f0370570c22a610868f2bfc36b8879bf54734d` |
| `README.md` | `65bf128463d561f641256050fb7d1c2405c17c6d81ec37e00c5758cb44eb4681` |
| `13_correlated_network_proof_package.md` | `f1d2979f6d67ba26243ffc66154f0521b65a6a81ad21be3298764fd383025cde` |
| `15_submission_readiness_and_venue_strategy_2026-07-18.md` | `15aacc55c5e4b2f362ca8dee5ff282422e84b21a186438f6130237af47f4af6a` |
| `16_key_proof_and_t18_validation_2026-07-18.md` | `fbe3ab13059fcf51288964ff4629c15abb74eda088363c94efedf0394c8306f1` |
| `state.json` | `ba178c34948485ecddd059960ff6f585ab14d8abc46d5a7e6852f9525d3654ae` |

本 QA 文件写入后，引用它的文件若再修改，须重新计算相应哈希；本表不包含本 QA 文件自身哈希。

## 10. 仍未通过的门禁

1. T16–T18 的 R01–R14 外部概率论签核；
2. MathSciNet、zbMATH、Scopus、Web of Science、CNKI 机构检索；
3. 真实 Lightning 拓扑/透明需求到路由核的映射；
4. 首次余额耗尽与真实支付失败、再平衡、通道关闭的语义校准；
5. 完整英文论文及其逐句证据审计。

T18-A 已从技术债和硬门禁中移除，但其有限网格全正结论不得升级为统一符号定理。
