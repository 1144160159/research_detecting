# 029 Flow-Payload NIDS：利用流统计与协议载荷的多视图入侵检测

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | PDF页 | 本卡 | 状态 |
|---|---:|---|---|
| Abstract / Introduction / Related Work | 1-3 | 第1-3节 | 已覆盖 |
| Proposed Method / Alignment | 3-6 | 第4-5节 | 已覆盖 |
| Evaluation / Results | 6-11 | 第6-8节 | 已覆盖 |
| Conclusion | 10-11 | 第9节 | 已覆盖 |

## 1. 身份与摘要缩译

作者为 A. Kiflay、A. Tsokanos、M. Fazlali 和 R. Kirner，发表于 Array 22（2024）100349，DOI 10.1016/j.array.2024.100349。

论文从 UNSW-NB15 的 PCAP 和标签中对齐六个 flow features 与每个协议的前 32 payload bytes。两个 Random Forest 分别输出类别概率，再以 soft voting 平均。摘要报告 Accuracy、Recall、Precision 和 F1 多在 98%-99%。

## 2. 引言与相关工作缩译

作者指出，flow-based NIDS 高效但无法观察用户内容，且不同环境下特征分布变化明显；payload-based NIDS 能看应用攻击，但计算开销大、对加密流量受限。相关工作涵盖 flow statistics、n-gram payload、1D-CNN、BERT 和 feature-level fusion。论文目标是离线检测，不声称即时阻断。

## 3. 数据对齐与预处理缩译

流由五元组和时间窗聚合，六个特征包括双向 packet/byte counts、flow start 和 duration 等标准字段。作者从 PCAP 提取 payload，并用官方 flow label 对齐；算法弥补公开数据通常只有 flow CSV、没有已标注 payload 的缺口。

协议 payload 仅保留前 32 bytes。数据按 80%/20% 划分训练测试，约 1,495,071 TCP 样本和其他协议样本按原比例进入。全文未证明 split 按 capture、flow fingerprint 或时间隔离，可能发生近重复泄漏。

## 4. 模型与融合缩译

流分支和 payload 分支均为 Random Forest。对测试样本 x，类别 j 的最终概率为：

Pⱼ(x) = 0.5 × [Pⱼ(x,h₁) + Pⱼ(x,h₂)]

选择最大 Pⱼ 的类别。论文还将 late soft voting 与 feature-level early fusion 比较。soft voting 保留两分支可解释性，而 early fusion 的输出难以归因到具体视图。

## 5. 实验结果缩译

二元与多类实验总测试样本约 371,778。多数攻击 ROC 曲线靠近左上角，Backdoor 和 Worms 表现较低。总体 Accuracy、Precision、Recall、F1 多在 98% 以上，部分接近 99%；使用的输入仅为六个流特征和 32 bytes payload。

payload-size 实验比较更大预算后选择 32 bytes，意在平衡性能和成本。SHAP 分析显示 payload 常占主导，但 flow features 对 payload 较短或不可区分的攻击仍必要。论文未研究加密后 payload 是否仍有同等语义。

## 6. 局限与结论缩译

研究只在 UNSW-NB15 单一数据集、离线闭集条件评估；没有 unknown attack 留出、跨时间、跨网络或缺失 payload。作者把在线部署和其他环境验证留作未来工作。

# 第二部分：独立技术分析

## A. 协议、模态与状态

- 角色：B-传统双视图基线；状态：`project_mapped`。
- 本地 PDF：`paper/10.1016_j.array.2024.100349.pdf`。
- 协议：`P3-random-flow-split-closed-set`。
- 多模态：同一 flow 的 statistics＋payload bytes，样本级对齐，属于同源双视图。
- 任务：闭集二元/多类；无 unknown rejection。

## B. CAEOS 采纳

该论文适合作为最低复杂度双视图基线：两个 RF 加 soft voting。它能检验 CAEOS 的深度融合是否真正优于简单概率平均。对于加密流量，32 bytes payload 可能主要包含头部、握手或加密随机字节，必须逐数据集记录 payload 可见性，不可直接复制其高分。

`E-FLOWPAYLOAD-01`：统一 strict-v4 split 上训练 flow-RF、payload-RF、soft-voting RF、early-fusion RF 和 CAEOS；阈值仅 known validation；5 seeds。若 CAEOS 不能显著超过 soft voting 的 OSCR 且校准更差，应削减融合复杂度。

## C. 95%/5%与最终审计

98%-99% 闭集结果不能证明良性 FAR≤5% 或 unknown FPR95≤5%；无 OSCR、ECE、Brier、NLL。G0-G1、G3-G9 通过；G2 核至 DOI、Zotero 待核；G10 未通过。最终状态 `project_mapped`。
