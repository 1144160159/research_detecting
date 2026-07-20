# GPU 恶意流量候选数据集审计与 strict-v4 冻结决策

审计日期：2026-07-17

## 审计范围

在 GPU 服务器上只读盘点 9 套候选数据。原始清单记录文件数、容量、CSV 表头签名、标签列候选、小样本标签分布、PCAP 数量和压缩包成员；样本标签计数不冒充全量计数。清单 SHA-256 为 `62297574add6c7d1af57ba0be714b465c9342ce339faabda23e1cc6bdeb5d921`。

| 候选 | 盘点容量 | 表格文件 | PCAP | 判断 |
|---|---:|---:|---:|---|
| CIC-ToN-IoT | 3.31 GiB | 2 | 0 | 第一优先，已有 535 万行全量标签审计 |
| CIC-BoT-IoT | 8.49 GiB | 2 | 0 | 4 个粗类，作为跨域补充 |
| CICDarknet2020 | 0.07 GiB | 1 | 0 | 主表排除：两个同名 Label，且为应用流量类别 |
| CICIoT2023 | 564.73 GiB | 372 | 309 | 第一优先，33 个攻击目录加正常类 |
| LSNM2024 | 2.36 GiB | 21 | 2 | 需统一 4 种表头并删除直接标识字段 |
| Mal_TLS2023 | 0.08 GiB | 1 | 0 | 严格泄漏复审后升级，适合加密恶意软件域 |
| CTU-13 | 74.27 GiB | 13 | 13 | 需先冻结 13 个 capture 到 botnet 家族的映射 |
| CICDDoS2019 | 24.35 GiB | 0 | 0 | 7 个压缩包，适合 DDoS 敏感性补充 |
| CICAPT-IIoT2024 | 11.40 GiB | 2 | 0 | 先全量审计 subLabelCat，再决定是否接入 |

## 冻结扩展方向

strict-v4 第一批固定接入 CIC-ToN-IoT 和 CICIoT2023。现有 5 数据集、61 场景将扩为 7 数据集、103 场景，其中新增 9 个 ToN-IoT 攻击类和 33 个 CICIoT2023 攻击类。

CICIoT2023 必须只读取 309 个原始捕获对应 CSV，排除 63 份 `MERGED_CSV`，避免重复样本。其标签来自父目录，39 个公共特征不含 IP；仍需生成基于源捕获和连续块的分组列，使 train/validation/test group overlap 为 0。

代表 pilot 在结果产生前冻结为 6 个未知类：ToN-IoT 的 xss、scanning、ransomware，以及 CICIoT2023 的 DDoS-ICMP_Flood、Mirai-udpplain、CommandInjection。每个场景运行 CAEOS、MLP、Open-Detect、RoNeTC，seed 7 共 24 个方法运行。全部通过数据哈希、无标识特征、无分组重叠、无跨标签指纹、有限指标和零失败门后，才扩展到五种子和全部 42 个新增场景。

## 对全面 SOTA 的作用

新增数据集不用于稀释或替换 strict-v2 结果。strict-v2 的 20/24 基线终审继续独立完成；strict-v4 用于证明跨物联网采集环境、攻击族和捕获来源的泛化。主文应分别报告 strict-v2 的严密同协议排名与 strict-v4 的扩展泛化，不把异构协议结果混成一个显著性家族。
