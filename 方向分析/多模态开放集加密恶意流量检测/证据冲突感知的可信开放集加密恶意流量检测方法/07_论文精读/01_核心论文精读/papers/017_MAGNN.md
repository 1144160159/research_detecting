# 017 MAGNN：面向恶意流量检测的多尺度自适应图对比学习

# 第一部分：原文结构化全文缩译

## 0. 章节覆盖

| 原文 | PDF页 | 本卡 | 状态 |
|---|---:|---|---|
| Abstract / Introduction / Related Work | 1-3 | 第1-3节 | 已覆盖 |
| Graph Construction / Augmentation / Contrastive Learning | 3-7 | 第4-6节 | 已覆盖 |
| Experiments / Results | 7-13 | 第7-8节 | 已覆盖 |
| Scalability / Ablation / Conclusion | 13-14 | 第8-10节 | 已覆盖 |

## 1. 文献身份与摘要缩译

作者为 Mukhtar Ahmed、Jinfu Chen、Ernest Akpaku 和 Ali Bux，发表于 Journal of Parallel and Distributed Computing，211（2026）105240，DOI 为 10.1016/j.jpdc.2026.105240。

论文认为传统流量 GNN 偏重节点特征，忽略通信边的包/流属性和时间演化。MAGNN 把主机或设备建为节点，把通信流建为边，通过 temporal-node contrast、edge-level contrast 和 multi-head hierarchical contrast 同时学习局部、边级和全局表征，并以边修改和随机游走生成增强视图。实验覆盖 CTU-13、ISCXVPN2016、CICIDS2017 和 CIRA-CIC-DoHBrw2020。

## 2. 引言与相关工作缩译

作者将图流量检测的缺口归纳为：节点聚合可能稀释关键攻击信号；单尺度图难以表达局部突发与全局结构；静态图难以适应演化流量；大量监督标签不现实。相关工作包括 Anomal-E、NEGAT、E-GraphSAGE、TCGNN、DE-GNN、CoLA、AAGNN、RoSA、RWR 和 GRADATE。MAGNN 在这些工作上增加时间节点、边级和多头层次三个对比目标。

## 3. 问题定义与图构建缩译

网络被表示为 G = (V,E)，节点是 IP/设备，边是网络包、会话或通信流。节点特征含流量体量、包统计或行为；边特征表示连接属性。论文还比较 flow-centric 和 feature-centric 两种图构建，最终认为 host-centric 图更好。动态图按 300、600 和 900 秒快照组织。

## 4. 图增强缩译

第一种增强随机增加或删除比例 P 的边，以模拟拓扑扰动。第二种增强采用随机游走重启：

pₜ = (1 − α)Apₜ₋₁ + αeᵢ

其中 eᵢ 表示从目标节点重启，稳定概率用于选择结构和语义上接近的子图。增强同时保留主要结构并制造足够差异，供对比目标学习不变表征。

## 5. 多尺度对比模块缩译

Temporal-node contrast 比较相邻时间快照中的节点行为；edge-level contrast 显式对齐通信边表示；multi-head hierarchical contrast 通过多头注意力组合节点、子图和全图级表示。总损失为三项对比目标的加权组合。论文称预训练可在无标签图上进行，部署时可用少量标签微调或评分，但最终分类头和监督使用范围没有被完整、可复核地分开说明。

## 6. 数据与训练设置缩译

四个数据集覆盖 botnet、VPN/非VPN、通用入侵和 DoH 恶意流量。实现使用 Python 3.9、PyTorch 2.0、PyTorch Geometric 2.3.1、NumPy 1.24 和 Pandas 1.5。学习率 0.001，Adam，weight decay 0.00001，batch 64，训练 100 epochs，验证损失 10 epochs 无提升时衰减学习率并用于 early stopping。邻居采样大小为 30。

论文未明确给出 capture-grouped train/validation/test split、随机种子数和 unknown leave-out；因此这些都是闭集或异常评分结果，不能按开放集未知检测解释。

## 7. 主结果缩译

在 100 steps 附近，MAGNN 报告 Accuracy：CTU-13 约 97.80%、ISCXVPN2016 98.60%、CICIDS2017 99.13%、DoHBrw2020 99.30%；对应 F1 约 98.94%、99.36%、98.97% 和 99.10%。这些高分是数据集内结果，没有 unknown rejection operating point。

计算时间表显示 MAGNN 在不同数据集上的训练/推理时间优于部分 GNN 基线；CTU-13 文字给出单 epoch 约 18.5 秒，而表格抽取位置存在 21.4 秒项，需回看排版确认具体配置。四 GPU 相对单 GPU 的训练时间最多下降约 59.83%，三张或更多 GPU 的 speedup 多超过 50%。

## 8. 消融与扩展结果缩译

表6中完整模型 Accuracy 98.45%、F1 97.58%、MSE 0.06、RMSE 0.20、MAE 0.31、MAPE 1.08。去掉多头层次对比后 F1 96.85%；去掉边级对比为 96.45%；去掉时间节点对比为 96.00%；去掉图增强为 95.75%；去掉综合损失为 96.20%。

host-centric 图在 DoHBrw2020 上 Accuracy 98.91%，flow-centric 为 94.61%，feature-centric 为 90.70%。论文据此认为端点关系是最强结构，但该结果也提示 IP/设备身份捷径风险。

## 9. 讨论与局限缩译

作者承认模型未显式处理 APT 长期依赖，尚需在线学习、记忆结构、持续对比学习、更大真实流量和解释机制。论文将图增强带来的泛化潜力延伸到 zero-day，但没有实际留出攻击家族实验，因此这一点仍是推测。

## 10. 结论缩译

MAGNN 是多尺度图表征和分布式训练基线，不是开放集检测器。其价值在于边级/时间/层次对比组件和图构建消融，而不是 95% 以上闭集 F1 本身。

# 第二部分：独立技术分析

## A. 任务、协议与模态

- 角色：C-图表征强基线；状态：`project_mapped`。
- 本地 PDF：`paper/10.1016_j.jpdc.2026.105240.pdf`。
- 协议：`P3-closed-set-split-and-label-use-unclear`；无 unknown 构造、阈值或 OSCR。
- 模态：同一流量派生的节点、边和时间尺度，属于图多尺度单模态/多视图，不是真多源多模态。
- 端点作为节点可能编码数据集环境身份；跨数据集必须重建图并移除或匿名化 IP 捷径。

## B. 95%/5% 与采纳判断

闭集 Accuracy/F1 超过 95% 不能证明 unknown 检测或良性 FAR 达标。论文没有 Macro-F1 定义、FPR95、OSCR、ECE、Brier 或 NLL。

采纳边级对比和时间节点对比作为候选表征消融；不采纳“自监督即可检测 zero-day”的外推。`E-MAGNN-01` 在 strict-v4 上比较统计编码器、host-centric MAGNN、去 IP 图和 CAEOS 图分支，5 seeds；若去身份字段后或跨数据集时收益消失，则否决图主干。

## C. 最终审计

- G0-G1、G3-G9：通过。
- G2：DOI 已核，Zotero 待核。
- G10：未通过。
- 最终状态：`project_mapped`。
