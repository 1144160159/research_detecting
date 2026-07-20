# 第一批 Zotero 接管种子文献

来源：根目录 `文献.md`。目标是先建立异常检测核心证据链，不做全量导入。

## 加密流量与网络入侵检测

| 编号 | 题名 | 建议集合 | 标签 |
|---|---|---|---|
| [69] | A Survey of Encrypted Malicious Traffic Detection | `02_Methods_方法谱系/EncryptedTraffic_加密恶意流量检测` | `ad/role/survey`, `ad/domain/encrypted-traffic` |
| [101] | Deep Learning for Encrypted Traffic Classification and Unknown Data Detection | `02_Methods_方法谱系/OpenSet_OOD_开放集与未知攻击检测` | `ad/domain/encrypted-traffic`, `ad/domain/open-set` |
| [102] | E-GraphSAGE: A Graph Neural Network based Intrusion Detection System for IoT | `02_Methods_方法谱系/Graph_图异常检测` | `ad/domain/graph`, `ad/domain/network-ids` |
| [104] | Encrypted Malware Traffic Detection via Graph-based Network Analysis | `02_Methods_方法谱系/EncryptedTraffic_加密恶意流量检测` | `ad/domain/encrypted-traffic`, `ad/domain/graph` |
| [115] | 3D-IDS: Doubly Disentangled Dynamic Intrusion Detection | `02_Methods_方法谱系/IDS_NIDS_网络入侵检测` | `ad/domain/network-ids`, `ad/role/method` |
| [132] | DI-NIDS: Domain invariant network intrusion detection system | `01_Core_核心证据/DA-FDIDS_AI驱动网络流量检测` | `ad/domain/network-ids`, `ad/evidence/support` |
| [138] | Graph based encrypted malicious traffic detection with hybrid analysis of multi-view features | `01_Core_核心证据/Evidence-OpenEMTD_可信开放集加密恶意流量检测` | `ad/domain/encrypted-traffic`, `ad/domain/multimodal`, `ad/domain/graph` |
| [147] | Point Cloud Analysis for ML-Based Malicious Traffic Detection | `01_Core_核心证据/Evidence-OpenEMTD_可信开放集加密恶意流量检测` | `ad/domain/encrypted-traffic`, `ad/role/method` |
| [173] | An Autoencoder-Based Hybrid Detection Model for Intrusion Detection With Small-Sample Problem | `02_Methods_方法谱系/IDS_NIDS_网络入侵检测` | `ad/risk/small-sample`, `ad/domain/network-ids` |
| [175] | Anomaly Detection for In-Vehicle Network Using Self-Supervised Learning With Vehicle-Cloud Collaboration Update | `02_Methods_方法谱系/IDS_NIDS_网络入侵检测` | `ad/domain/network-ids`, `ad/role/method` |
| [180] | Auto-Updating Intrusion Detection System for Vehicular Network: A Deep Learning Approach Based on Cloud-Edge-Vehicle Collaboration | `01_Core_核心证据/DA-FDIDS_AI驱动网络流量检测` | `ad/domain/network-ids`, `ad/role/method` |

## 图异常与时序异常

| 编号 | 题名 | 建议集合 | 标签 |
|---|---|---|---|
| [149] | Robust Anomaly-Based Insider Threat Detection Using Graph Neural Network | `02_Methods_方法谱系/Graph_图异常检测` | `ad/domain/graph`, `ad/role/method` |
| [156] | A Discrepancy Aware Framework for Robust Anomaly Detection | `02_Methods_方法谱系/MTS_多变量时序异常检测` | `ad/domain/time-series`, `ad/role/method` |
| [159] | A Multihead Attention Self-Supervised Representation Model for Industrial Sensors Anomaly Detection | `02_Methods_方法谱系/MTS_多变量时序异常检测` | `ad/domain/time-series`, `ad/role/method` |
| [162] | A Survey of Graph-Based Deep Learning for Anomaly Detection in Distributed Systems | `02_Methods_方法谱系/Graph_图异常检测` | `ad/role/survey`, `ad/domain/graph` |
| [163] | A Survey on Graph Neural Networks for Time Series: Forecasting, Classification, Imputation, and Anomaly Detection | `02_Methods_方法谱系/MTS_多变量时序异常检测` | `ad/role/survey`, `ad/domain/time-series`, `ad/domain/graph` |
| [166] | Abnormal Logical Representation Learning for Intrusion Detection in Industrial Control Systems | `02_Methods_方法谱系/IDS_NIDS_网络入侵检测` | `ad/domain/network-ids`, `ad/role/method` |
| [168] | Adaptive Working Condition Recognition With Clustering-Based Contrastive Learning for Unsupervised Anomaly Detection | `02_Methods_方法谱系/MTS_多变量时序异常检测` | `ad/domain/time-series`, `ad/role/method` |
| [170] | Adversarial Graph Neural Network for Multivariate Time Series Anomaly Detection | `02_Methods_方法谱系/MTS_多变量时序异常检测` | `ad/domain/time-series`, `ad/domain/graph` |
| [176] | ARISE: Graph Anomaly Detection on Attributed Networks via Substructure Awareness | `02_Methods_方法谱系/Graph_图异常检测` | `ad/domain/graph`, `ad/role/method` |
| [178] | Asymptotic Consistent Graph Structure Learning for Multivariate Time-Series Anomaly Detection | `02_Methods_方法谱系/MTS_多变量时序异常检测` | `ad/domain/time-series`, `ad/domain/graph` |

## 第一批输出目标

1. 以上论文进入 Zotero 后，全部加 `ad/status/inbox`。
2. 标题/摘要筛选完成后，生成 `zotero-workflow/screening/YYYYMMDD_screening_batch01.csv`。
3. 至少 10 篇完成 `zotero-workflow/evidence-cards/` 证据卡。
4. 生成第一版研究简报：`zotero-workflow/briefs/YYYYMMDD_research-brief_异常检测.md`。

