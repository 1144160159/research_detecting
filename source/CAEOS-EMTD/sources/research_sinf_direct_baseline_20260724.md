# SINFlow direct-baseline audit

更新时间：2026-07-24

## 论文身份

- 题名：Unknown DDoS Attack Detection with Sliced Iterative Normalizing Flows Technique
- 作者：Chin-Shiuh Shieh、Thanh-Lam Nguyen、Thanh-Tuan Nguyen、Mong-Fong Horng
- 期刊：Computers, Materials & Continua 82(3), 4881-4912 (2025)
- DOI：`10.32604/cmc.2025.061001`
- 出版日期：2025-03-06
- 官方全文：
  - `sources/shieh2025_sinf.pdf`
  - 1,511,090 字节
  - SHA256 `c52d670907ddf3b21a10a9ca92a1165b6050a7dc447ac6db5530bb5a8aa4ef7e`
- 抽取文本：
  - `sources/shieh2025_sinf.txt`
  - 108,733 字节
  - SHA256 `e20dc94dd3a15cef9f054527fbef4cf2b49e418dff693a16f975bfbd3da26c83`

## 可验证方法契约

论文管线由三部分组成：

1. Autoencoder 对流级表格特征降维；
2. DNN 在编码表征上做 benign/malicious 二分类；
3. Gaussianizing Iterative Slicing（GIS）对编码训练分布做密度估计，以 log-density 作为未知风险。

论文给出的训练参数为：

- Adam；
- learning rate `0.005`；
- weight decay `0.003`；
- batch size `512`；
- random 70:30 train/test；
- 16 个种子：`0, 19, 58, 101, 205, 333, 487, 691, 827, 902, 1103, 1229, 1453, 1721, 27449, 920987`。

正文还分别写了“10次训练”“16个种子”“训练20次”，三种次数描述不一致。论文没有给出AE层宽、潜维度、激活函数、dropout概率、DNN层结构、训练epoch、GIS迭代数、切片数、KDE/whitening/停止条件。

## 预处理与阈值

论文描述的预处理为：

- 含缺失或NaN的行删除；
- INF替换为 `1e10`；
- 负值替换为0；
- `X <- log10(X + 1) / 10`；
- 再缩放到 `[0,1]`；
- 二分类one-hot标签；
- 不做outlier removal或data augmentation。

论文没有说明 `[0,1]` 缩放统计量只在训练集拟合还是在完整数据上拟合。

GIS阈值定义为训练样本log-density的第1百分位，论文报告阈值 `-23.30`。这一公式在原则上可以只消费known-training，但正文同时说明阈值可按数据集经验调整，且未发布选择trace。因此可保留为known-only候选规则，不能把“零未知暴露已验证”写成事实。

## 静态未知检测与增量学习边界

静态未知模块只报告Outlier Detection Rate。CICIDS2017-Friday为1.42%，CICDDoS2019各攻击集约11.24%-86.69%。这不是AUROC、AUPR、FPR95、OSCR或ECE，也不能证明被标记样本全部是真未知。

摘要中的最高F1 `0.9999`来自网络专家标注被标记样本、再将已确认未知样本用于增量学习之后。该结果必须归入增量/监督更新阶段，禁止作为静态zero-shot未知检测成绩。

## 代码检索

GitHub repository查询结果：

- 完整题名：0
- DOI：0
- `SINF CICIDS2017 CICDDoS2019`：0
- `Autoencoder SINF DDoS`：0

截至审计未验证2025 IDS论文的作者实现。负检索不证明代码不存在。

论文引用的2021 SINF底层方法有官方仓库：

- `biweidai/SINF`
- commit `450ee7bf3d3357c0108cf575c5bbf1a1be030a58`
- commit date `2022-12-06T14:41:01-08:00`
- 提供通用GIS/SIG引擎；
- 不含CICIDS2017/CICDDoS2019、AE、DNN、论文预处理或增量学习管线；
- 仓库根未发现LICENSE文件。

因此该仓库只能证明底层SINF引擎可得，不能冒充2025 SINFlow IDS作者实现。

## GPU数据审计

原始源候选覆盖 `2/2`：

- CICIDS2017：
  `/opt/data/private/wangwt/ParkAttackKE/datasets/cic/cic_cicids2017/raw`
- CICDDoS2019：
  `/opt/data/private/wangwt/ParkAttackKE/datasets/cic/CICDDoS2019`

冻结文件：

- `MachineLearningCSV.zip`：235,102,953字节
- CICIDS2017 Wednesday PCAP：13,420,789,612字节
- CICIDS2017 Friday PCAP：8,839,309,056字节
- `CSV-01-12.zip`：2,330,434,641字节
- `CSV-03-11.zip`：918,815,761字节

直接读取ZIP表头发现：

- CICIDS2017 Wednesday CSV为79列（含Label）；
- CICDDoS2019 `DrDoS_DNS.csv` 为88列（含Label）；
- 去除首尾空格后共享78个列名；
- CICDDoS2019另有10列；
- 两者表头不相同。

论文声称使用CICIDS2017全部80个特征，却未发布跨数据集特征映射、列顺序或processed manifest。原始数据齐全不等于论文输入可重建。

## 机器准入结论

机器证据位于 `results/strict_v4_sinf_direct_baseline_audit/`：

- evidence canonical SHA：
  `783454e4bb2c887bdf693f3de937c025da4db3dc3946a79a0cde3eacc5b5f82f`
- audit canonical SHA：
  `698f398ba7e9ab4968d68c3652e276ef127ccaf0a2526f64f9a0e6632e9af892`
- auditor SHA：
  `f1f4c45e0bdc2385b72d338aac7ed6e8cfa885a9de7a4f81eb01f53b9bb97ed5`
- test SHA：
  `d1990b7b67410df9624c89cda03abcc26fd5d1bcfe17f50ef15bf8c69c5b1fd8`

最终状态：

- `direct_domain_related_work_admitted=true`
- `native_external_protocol_candidate=true`
- `native_external_protocol_data_ready=true`
- `strict_adapter_candidate_after_specification=true`
- `native_execution_admitted=false`
- `strict_v4_main_table_admitted=false`
- `headline_incremental_f1_counted_as_zero_shot_unknown=false`
- `model_metrics_generated=false`
- `baseline_count_increment=0`

本地直接单测与GPU目标环境pytest均为 `10/10 PASS`；审计脚本、测试、evidence、audit、PDF、抽取文本和两份研究记录共8个同步工件逐SHA一致。

重新准入至少需要：2025 IDS作者代码或精确AE/DNN结构、完整GIS参数、不可变跨数据集特征映射、training-only缩放证据、known-only阈值选择trace、group-disjoint拆分与strict-v4六指标。
