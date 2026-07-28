# T16–T18 外部概率论评审交接 QA

**日期**：2026-07-18  
**范围**：`14_correlated_network_external_review_packet.md` 的评审资格、复算入口、权威哈希、R01–R14 逐项门禁和未签署状态。  
**结论**：交接包已具备供独立概率论研究者复算的材料与失败规则；当前仍是 **0/14**，没有 reviewer、signature 或 date，`publication_readiness=false`。本日志是内部材料完整性检查，不是外部数学签核。

## 1. 交接包增补内容

1. 明确评审者必须未参与 T16–T18 原始推导、formal fix、证明包写作、实验代码和当前 QA；存在实质参与时须披露并另行复核。
2. 把模型合同、完整证明包、关键准确性报告、T18 实现/测试及三类权威 CSV 列为必读材料。
3. 给出完整回归、36 单元正式实验、三拓扑精确锚点和最弱单元敏感性的独立复现命令；要求写入新目录，禁止覆盖权威证据。
4. R02 增补三个四超边拓扑的 $N=2$ 精确锚点，但明确有限枚举结果不能自动推广至所有 $N$ 和所有拓扑。
5. R13 增补临界互逆路由扰动恒等式、36 单元有限网格和最弱单元敏感性复核要求。
6. R14 增补旧随机种子与链形同构的纠错审计，以及“不把有限网格全正升级为统一符号定理”的主张边界。

## 2. 结构与未签署状态检查

| 检查 | 结果 |
|---|---:|
| R01–R14 二级标题 | 14 |
| `☐ Yes` 空框 | 14 |
| `☐ No` 空框 | 14 |
| reviewer 空白栏 | 14 |
| signature/date 空白栏 | 14 |
| 控制字符 | 0 |
| Final gate 明示 | `0/14` |
| Publication readiness | `false` |

没有任何方框被选择，也没有姓名、签名或日期被填写。因此不能把“材料已交接”写成“证明已获独立确认”。

## 3. 链接与权威哈希检查

- 交接包内本地 Markdown 链接：10 个；缺失：0 个。
- 下列 6 个交接包权威哈希均以磁盘文件重新计算，错配：0 个。

| 文件 | SHA-256 |
|---|---|
| `t18_cross_topology_validation.py` | `2d9cf6ebeb80819ab11f843a48d27ddd5d9a596b7da520be3ad47f9445c90765` |
| `test_t18_cross_topology.py` | `69ad388a263c28f326702d682014cf8dfa184bd658d05878fe279557c271e049` |
| `t18-primary-effects.csv` | `d9436daa71457d3f6c58cf02767b0204a178177a9f8d4367eec94a57d6ecd234` |
| `t18-kernel-diagnostics.csv` | `38779a494c53b824410894c7f5d8c11beca79be74001154fe82cbfa03d160808` |
| `t18-weakest-cell-sensitivity.csv` | `0b3009f557758bc392ef5a097234c3cd68bc08420d53bea15f800bb16b5abf79` |
| `t18-exact-anchors.csv` | `b9ada3e30ca5ea82e1d5bc4683f0370570c22a610868f2bfc36b8879bf54734d` |

## 4. 已沿用的计算证据

本次只修改评审交接文档、索引和状态字段，没有改动证明、代码或结果。最近一次正式技术 QA 已记录：

```text
python -m unittest -v
Ran 57 tests in 42.827s
OK
```

同一 QA 还记录了两轮 36 单元正式实验逐字节一致、最弱单元 100,000 对敏感性、三个 10,000 状态精确锚点、区间端点独立重算和四份 manifest 校验。本轮不重复运行约 16 分钟的正式模拟，也不把已有内部计算证据替代为外部数学复算。

## 5. 受保护材料与状态边界

- Task 6 的 5 个冻结 CSV 哈希应继续与 `2026-07-18_key_proof_and_t18_validation.md` 中记录值一致。
- 冻结 HTML 的 SHA-256 应继续为 `babf45d3ee1ae1455dfbf8d6c6d78d05fb296b87fdec6aca2902dc4a9b4f88cb`；本轮不修改、不重渲染。
- `state.json` 保持 `submission_completion_percent=68.75` 和 `publication_readiness=false`。交接包 QA 不增加完成度，因为真正的 R01–R14 外部签核尚未发生。

## 6. 下一门禁

由一名真正独立、具备概率论/随机过程能力的研究者按 R01–R14 逐条复算、填写 reviewer、选择 Yes/No 并签署日期。在 14 项全部通过前，不开始把内部证明工作稿包装成可投稿定理正文。

## 7. 当前交接文档哈希

| 文件 | SHA-256 |
|---|---|
| `14_correlated_network_external_review_packet.md` | `5c88f5ccd6c95de208f5576348e74d54205b671ab82c3ed2f52f9890f47a0cbb` |
| `README.md` | `4e1fcba26a4eb2369ef509ebd69200054ac50e6a88e813e0ec3472927b582e16` |
| `state.json` | `1449af3087eb4bea6635fdff872c13773cc540cd56b4cb6a7efd06cf5f8ee9d0` |

本表不包含本 QA 文件自身哈希。
