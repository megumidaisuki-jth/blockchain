# 真实 Lightning 拓扑映射第一阶段 QA

**日期**：2026-07-22（Asia/Hong_Kong）  
**范围**：公开数据取得、来源与哈希、三个预注册快照、确定性子图、透明合成需求、原子路由核、映射产物和回归验证。  
**结论**：第一阶段通过。已建立真实拓扑到现有 `NetworkKernel` 的可审计映射；尚未运行停止时间正式实验，不能称真实流量验证。

## 1. 数据来源与下载

采用 Valko–Marx Gómez 的公开数据集：

- 数据 DOI：<https://doi.org/10.7910/DVN/2OAVO6>；
- 数据论文 DOI：<https://doi.org/10.1038/s41597-025-06413-7>；
- 上游原始 gossip 记录：<https://doi.org/10.5281/zenodo.4088530>。

先取得 26,135 字节的 `shapes.geo.tab` 和 8,250 字节的上游脚本包。完整
`snapshots.geo.zip` 首次传输在 1,735,076 字节处 EOF；该文件没有被接受，
而是保留为 `.partial` 后使用断点续传与自动重试完成。最终长度
562,027,011 字节，上游 MD5 和本地 SHA-256 分别为：

```text
e6edd6fd7acae460abd0f70f71c9dbec
f380b71796edd86019ddc0b7822938559bfd40a2f650b21ccb66f14ef10e9320
```

MD5 与 Dataverse 元数据完全一致。三个预注册文件的 SHA-256 为：

| 文件 | SHA-256 |
|---|---|
| `20201014.gml.geo` | `900dbdce07298a65bafcc793bb18efbcd4bd43875a412c4195213dda41bce802` |
| `20220531.gml.geo` | `1aee99d82a6f60791f17e4176d76d3cfa20cd5931397f46d627a89b6e646e7a4` |
| `20230716.gml.geo` | `ee1b054a6ba2cb0ea3184f9f68f5cca7d8e70d17ff2d9e44e5e8871be8a8b855` |

实际节点/边计数分别为 5,963/29,940、15,947/79,552 和
15,100/64,212，逐项匹配元数据。

## 2. RED→GREEN 数据解析

最初真实快照冒烟检查被 `htlc_maximum_msat` 类型门拒绝。逐边检查发现，
三个 GML 分别有 8,121、27,590 和 26,587 个大整数因 GML 原生整数范围而
编码为十进制字符串；这不是缺失或负容量。新增失败测试后，适配器只接受
正十进制字符串并规范化为 Python 整数，其他字符串仍拒绝。focused
测试从 1 个错误恢复为 5/5 通过。

## 3. RED→设计修正

原合同曾要求每个 31 节点子图至少有一条长度不小于 3 的最短路。真实
冒烟检查显示 5/6 子图直径为 2；保留该门会系统性排除高度中心化的真实
LN 局部结构。正式停止时间模拟尚未开始，因此按审计程序把门改为研究
相关性所需的最小条件：存在长度不小于 2 的多通道路由。日期、锚点、节点
数和需求未改变。修正后的 6/6 子图通过：每个连通、通道数至少 30，并有
非零跨通道协方差。

## 4. 映射产物

权威入口为 [results/lightning-real-topology-mapping](../../../../results/lightning-real-topology-mapping)。

| 产物 | 行数/对象数 | 说明 |
|---|---:|---|
| `lightning-subgraphs.csv` | 6 | 3 日期 × primary/hub |
| `lightning-subgraph-nodes.csv` | 186 | 每个子图 31 节点 |
| `lightning-subgraph-channels.csv` | 202 | 每个真实 LN 通道映射为二元超边 |
| `lightning-kernels.csv` | 12 | 6 子图 × uniform/hotspot |
| `lightning-routes.csv` | 11,304 | 概率以十六进制浮点序列化 |
| `lightning-mapping-metadata.json` | 1 | 来源、软件、门禁与运行时间 |

映射运行用时 `30.3815348 s`。六个均匀需求核的最大绝对漂移均为
`1.214306433183765e-17`；六个热点核产生预期的非零漂移。所有核都有多
通道路由和非零跨通道协方差。`SHA256SUMS.txt` 的 6/6 条目复算匹配。

## 5. 测试与回归

执行：

```powershell
python -m py_compile lightning_topology_mapping.py lightning_mapping_validation.py test_lightning_topology_mapping.py
python -W error -m unittest -v test_lightning_topology_mapping.py
python -W error -m unittest -v
```

结果：编译静默通过；focused 5/5 通过；全项目 81/81 在 `61.582 s` 内
通过，退出码 0，无 Python warning/error。

## 6. 当前文件哈希

| 文件 | SHA-256 |
|---|---|
| `lightning_topology_mapping.py` | `5a1aed3317951c25d4575e4c1b42afe0598d3f5d87136780f321fa9006c9258a` |
| `lightning_mapping_validation.py` | `c76874ada50a7969bc4c299d7f19ece1724e02fecf91ba3850a403a28a7e7bca` |
| `test_lightning_topology_mapping.py` | `f48cfe23bd27cf45772e114bc18ec9901c47be37e749ec26b6fa366633e165dd` |
| [映射合同](../18_real_lightning_mapping_contract_2026-07-22.md) | `61d9dcadcaf60139b1966fd140459a07368e0137723d966b919e5e5e15190204` |
| 数据来源记录 | `33c1c8492a41faa3654fe373389c33578f32a616e9bfce02f2dd43ced994442f` |
| `lightning-routes.csv` | `24c1447d5b4b8509086f13f62e0122c211df245597acfa798c56074124037cc5` |
| 映射 manifest | `5a28dec23ad5f976a052b840eb8ce72fd52b59de57c466e2ec0a73ed10eadac0` |
| `README.md` | `73dbf9789f1d044c00dca1087f185faeffbbc214034ccb3eac259852e68b430e` |

## 7. 主张边界与下一步

本阶段支持“真实公开拓扑/透明合成需求”。公开 gossip 不包含真实支付流量、
私有余额或失败后重试，因此不能写成真实流量校准，也不能把模型余额首次
到零称为真实支付失败或通道关闭。

下一步是先用每格 2,000 对轨迹完成 48 单元性能与无删失预检，再据运行时
冻结正式样本量、同时区间和独立复跑。完成度仍保持 71.75%，因为停止时间
正式实验尚未执行，`publication_readiness=false`。
