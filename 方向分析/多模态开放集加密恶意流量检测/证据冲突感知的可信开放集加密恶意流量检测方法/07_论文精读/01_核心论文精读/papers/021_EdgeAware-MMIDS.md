# 021 Edge-Aware MMIDS：面向 CCIIoT 的深度自适应融合入侵检测

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | PDF页 | 本卡 | 状态 |
|---|---:|---|---|
| Abstract / Introduction / Related Work | 1-3 | 第1-3节 | 已覆盖 |
| Data / Preprocessing / Models | 3-6 | 第4-6节 | 已覆盖 |
| Results / Ablation | 6-7 | 第7-8节 | 已覆盖 |
| Limitations / Conclusion | 8 | 第9-10节 | 已覆盖 |

## 1. 身份与摘要缩译

作者为 Nimra Nasir、Amnah Firdous、Syeda Sitara Waseem、Syed Rizwan Hassan、Mansoor Ihsan 和 Isma Farah Siddiqui。论文为 IEEE Transactions on Consumer Electronics 录用作者版，DOI 10.1109/TCE.2026.3674715。

论文声称并行使用 GRU、LSTM、1D Transformer 和 TinyBERT 分别处理 host log、network flow、packet-level traffic 和 phishing email，再以可学习权重融合概率输出。四类输入实际来自 CTAP/CTDAPD、CIC-IDS2018、UNSW-NB15 和独立 phishing email 数据集，并不是同一事件或同一样本的对齐观测。

## 2. 引言与相关工作缩译

作者以 CCIIoT 中网络、主机、包和邮件威胁并存为动机，认为单模型难以覆盖异质数据。相关工作包括 LSTM/GRU 时序 IDS、统计特征融合、少样本、edge-IoMT、bagging GBDT 和轻量模型。论文将 late fusion 视为系统级多模态集成。

## 3. 数据与预处理缩译

四个数据源分别为：CTAP host logs；UNSW-NB15 的 43 个 flow-level 字段；CIC-IDS2018 flows；Kaggle phishing email 文本。统一映射为 Normal/Attack 二分类。数值缺失值用均值/中位数，类别缺失用众数；类别字段 one-hot/ordinal；数值 Min-Max；文本去停用词、小写和分词；序列 padding/truncation。

拆分为 stratified 80/10/10，SMOTE 和下采样仅作用训练集，缩放参数只由训练集拟合；时间序列声称采用 time-aware split。Python/NumPy/TensorFlow seed 均为 42。不同数据集之间没有样本 ID、时间戳或事件级对齐。

## 4. 模型缩译

LSTM 处理 CIC-IDS2018 序列，最终隐藏状态投影为 128 维后做 sigmoid 二分类。GRU 处理 host logs，使用双向 GRU 和注意力。1D Transformer 处理 UNSW-NB15 的数值流特征。TinyBERT 处理 phishing email 文本。

各模型输出攻击概率 pₘ。所谓 adaptive fusion 为对不同模型概率施加可学习权重后再分类，权重由验证表现和置信度驱动。由于一个真实样本并不会同时拥有来自四个不同公开数据集的四个观测，该融合的统计对象和标签对应关系缺乏可部署定义。

## 5. 结果缩译

单模型结果：LSTM Accuracy 97.96%、F1 0.98；GRU Accuracy 82.34%、F1 0.78，且 attack recall 仅 0.04；1D Transformer Accuracy 94.86%、F1 0.95；TinyBERT Accuracy 99.53%、F1 1.00。

自适应融合报告 Accuracy 99.12%、F1 0.991、ROC-AUC 0.997；简单平均为 97.92%、0.979、0.988。去掉 GRU 后反而仍有 Accuracy 98.41%、F1 0.984；去掉 TinyBERT 为 96.87%、0.968。这些数字不能证明同一样本多模态互补，因为输入来源和样本分母不同。

## 6. 讨论、局限与结论缩译

作者承认预采集数据不能代表演化威胁；edge 部署尚未实测；SMOTE 可能生成不真实攻击；解释性只做初步分析。未来工作包括资源受限设备基准、实例级解释和动态模型选择。

# 第二部分：独立技术分析

## A. 任务与模态审计

- 角色：D-多模态反例；状态：`project_mapped`。
- 本地 PDF：`paper/10.1109_TCE.2026.3674715.pdf`。
- 协议：`P3-disjoint-dataset-late-fusion`。
- 多模态判定：作者称多模态，但同一行/事件没有四模态对齐，属于“异任务模型集成”，不是真多源样本级多模态。
- 任务为闭集二分类，无 unknown rejection。

## B. CAEOS 纠偏价值

本论文最重要的价值是反例：不能因为存在四个模型和四种数据就宣称一个样本拥有四模态。CAEOS 的每个流必须能追溯到同一 PCAP/标签事件中的 payload bytes、packet sequence 和 flow statistics；跨主机日志或邮件只有在 event ID/时间窗/实体映射可核时才能作为额外模态。

## C. 95%/5%与采纳

99.12% Accuracy 不可进入 CAEOS 主表；论文未报告良性 FAR、Known Macro-F1、Unknown AUROC/AUPR/FPR95、OSCR 或校准。只采纳 training-only preprocessing、SMOTE 仅在训练集和缺失模态权重的设计提醒；否决其样本级融合证据。

## D. 最终审计

- G0-G1、G3-G9：通过。
- G2：DOI 已核，Zotero 待核。
- G10：未通过；最终状态 `project_mapped`。
