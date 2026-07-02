# DA-FDIDS补充论文并入记录

生成日期：2026-06-25  
并入范围：`DA-FDIDS需补充论文方向与清单.md` 中“最优先补的 12 篇”  
本地位置：`paper/`

## 1. 并入结论

12 篇 DA-FDIDS 优先补充论文已在本地 `paper/` 目录中完成补充，并已纳入 DA-FDIDS 相关工作证据链。它们分别补强以下模块：

- GRL / DomainDiscriminator：DI-NIDS。
- 动态图与流交互建模：E-GraphSAGE、EULER。
- 漂移检测与在线适配：CADE。
- 异构域适应：Heterogeneous Domain Adaptation for IoT Intrusion Detection。
- TrafficEncoder / 流量基础表征：Universal Embedding、FlowSem-MAE、TrafficLLM、IHUD-BERT。
- MFL / RBF / 原型度量学习：Learning in Multiple Spaces。
- 少样本类增量攻击检测：Few-Shot Class-Incremental Learning for NIDS。
- 鲁棒性与部署安全：Membership Inference and Adversarial Attack Defense Framework。

## 2. 已补充论文清单

| 序号 | 论文 | 本地文件 | 主要补强方向 | 与 DA-FDIDS 的关系 |
|---:|---|---|---|---|
| 1 | DI-NIDS: Domain invariant network intrusion detection system | `paper/10.1016_j.knosys.2023.110626.pdf` | 域对抗、跨域泛化 | 直接支撑 GRL + 域判别器的设计动机 |
| 2 | E-GraphSAGE: A Graph Neural Network based Intrusion Detection System for IoT | `paper/10.1109_NOMS54207.2022.9789878.pdf` | 边特征图、IoT NIDS | 支撑流量边特征图建模和图 NIDS 背景 |
| 3 | EULER: Detecting Network Lateral Movement via Scalable Temporal Link Prediction | `paper/10.14722_ndss.2022.24107.pdf` | 动态图、横向移动、时序链路预测 | 支撑动态图安全检测和时序交互建模 |
| 4 | CADE: Detecting and Explaining Concept Drift Samples for Security Applications | `paper/CADE.pdf` | 概念漂移、漂移解释 | 支撑 LoRA 在线适配与 Stable-LoRA 稳定约束的必要性 |
| 5 | Heterogeneous Domain Adaptation for IoT Intrusion Detection | `paper/10.1109_JIOT.2023.3239872.pdf` | 异构域适应、图几何对齐 | 补强 DA-FDIDS 跨域迁移在异构场景下的讨论 |
| 6 | Universal Embedding Function for Traffic Classification via QUIC Domain Recognition Pretraining | `paper/10.1109_tnsm.2025.3642984_dup.pdf` | 通用流量 embedding、迁移学习 | 支撑 TrafficEncoder 可替换为预训练通用流量表征 |
| 7 | FlowSem-MAE: Protocol-Native Tabular Pre-training for Encrypted Traffic Classification | `paper/10.48550_arXiv.2603.10051.pdf` | 协议原生表格预训练、MAE | 补强流量基础模型和协议语义建模 |
| 8 | TrafficLLM: Enhancing Large Language Models for Network Traffic Analysis with Generic Traffic Representation | `paper/10.48550_arXiv.2504.04222.pdf` | 流量大模型、通用表征、泛化 | 支撑 TrafficEncoder/LLM 化基础表征趋势 |
| 9 | IHUD-BERT: A Large-Scale Network Traffic Classification Method Based on Pre-Training Transformers and Knowledge Distillation | `paper/10.1109_tccn.2026.3695843_dup.pdf` | 预训练 Transformer、知识蒸馏、inter-flow 评测 | 支撑严谨划分、抗泄漏评测和轻量部署 |
| 10 | Learning in Multiple Spaces: Prototypical Few-Shot Learning With Metric Fusion for Next-Generation Network Security | `paper/10.1109_tnsm.2026.3665647_dup.pdf` | few-shot、原型学习、度量融合 | 支撑 MFL、RBF 相似性和多度量类别判别 |
| 11 | A Few-Shot Class-Incremental Learning Method for Network Intrusion Detection | `paper/10.1109_tnsm.2023.3332284_dup.pdf` | 少样本类增量、未知新类 | 支撑新攻击类别持续纳入和少样本增量检测 |
| 12 | A Membership Inference and Adversarial Attack Defense Framework for Network Traffic Classifiers | `paper/10.1109_tai.2024.3357791_dup.pdf` | 对抗鲁棒性、成员推理防御 | 补强 DA-FDIDS 部署风险与鲁棒评测部分 |

## 3. 逐篇并入要点

### 3.1 DI-NIDS

DI-NIDS 证明 NIDS 在跨数据集或跨网络环境部署时会因特征分布差异显著退化，并提出利用对抗域适应从多个网络域中提取域不变特征，再结合 One-Class SVM 做异常识别。它最适合放在 DA-FDIDS 的“域适应与跨域泛化”部分，用来支撑 GRL、DomainDiscriminator 和域不变表示学习。

对 DA-FDIDS 的写作意义：DI-NIDS 解决的是静态跨域泛化，而 DA-FDIDS 进一步把域对抗放入动态图少样本 episode 中，因此可以强调“从域不变 NIDS 到动态少样本域适应 NIDS”的扩展。

### 3.2 E-GraphSAGE

E-GraphSAGE 将流量端点映射为图节点，将网络流映射为带边特征的图边，并用 GNN 同时捕获边属性和拓扑关系。它说明流级记录天然适合图表示，尤其对 IoT 场景中分布式扫描、DDoS、Botnet 等多实体协同行为有价值。

对 DA-FDIDS 的写作意义：E-GraphSAGE 可作为图 NIDS 基础引用，支撑 DA-FDIDS 中动态图记忆和流交互建模的必要性。

### 3.3 EULER

EULER 将横向移动检测建模为动态图链路预测问题，通过 GNN 编码离散时间快照中的拓扑关系，再用序列编码器刻画时序演化。它强调 APT 横向移动不是孤立流异常，而是网络实体关系随时间变化后的异常边。

对 DA-FDIDS 的写作意义：EULER 可支撑“动态交互关系”和“攻击链行为随时间演化”的论述，尤其适合放在动态图 NIDS 部分。

### 3.4 CADE

CADE 面向安全应用中的概念漂移，提出检测漂移样本并解释漂移原因的方法。它利用对比学习把样本映射到低维空间，并通过距离解释说明漂移样本为什么偏离已有类别。

对 DA-FDIDS 的写作意义：CADE 支撑模型在线部署时必须考虑概念漂移，也能解释为什么 LoRA 在线适配需要 Stable-LoRA 约束，避免把少量漂移样本或噪声样本错误吸收到基础表征中。

### 3.5 Heterogeneous Domain Adaptation for IoT Intrusion Detection

该论文提出图几何对齐方法 GGA，将每个入侵域建模为由攻击类别及类别关系构成的图，通过图级形状保持、中心点匹配、旋转避免和伪标签选择实现异构域知识迁移。

对 DA-FDIDS 的写作意义：它补足了 DA-FDIDS 当前同构特征空间跨域设置之外的异构域适应讨论，可作为未来工作或更严格跨域实验的支撑。

### 3.6 Universal Embedding Function

该论文以 QUIC 域名识别作为预训练任务，学习可迁移的 packet sequence embedding，并迁移到多个下游流量分类数据集。其关键价值是证明流量分类可以借鉴计算机视觉中的“先预训练通用嵌入，再迁移到下游任务”范式。

对 DA-FDIDS 的写作意义：它为 TrafficEncoder 提供直接背景。DA-FDIDS 若当前仅使用 MLP 编码器，应表述为“框架兼容预训练流量 embedding”，而不是过度声称已具备真正 foundation encoder。

### 3.7 FlowSem-MAE

FlowSem-MAE 认为直接把协议字段展平成字节序列会破坏协议语义，并提出协议原生的 Flow Semantic Units 与表格式 masked autoencoder 预训练。它强调字段可预测性、字段边界和流级元数据对加密流量分类的重要性。

对 DA-FDIDS 的写作意义：它可以补强 TrafficEncoder 的设计方向，即未来编码器不应只处理通用 `msg` 特征，而应显式利用协议字段结构和可迁移语义。

### 3.8 TrafficLLM

TrafficLLM 提出面向网络流量分析的大语言模型适配框架，通过流量域 tokenization 和双阶段微调学习通用流量表征，并在多任务和未见流量场景中验证泛化能力。

对 DA-FDIDS 的写作意义：它支撑“流量基础模型”趋势，也说明 TrafficEncoder 后续可以从轻量 MLP 扩展为 LLM/PLM 风格的通用流量表征模块。

### 3.9 IHUD-BERT

IHUD-BERT 使用 IP Header Unit 作为输入单位，并结合预训练 Transformer 与知识蒸馏实现高效流量分类。该论文特别强调 payload-based 模型在 inter-flow 划分下性能会崩塌，说明不严谨划分会造成会话工件泄漏和虚高结果。

对 DA-FDIDS 的写作意义：它非常适合支撑 DA-FDIDS 实验设计中的 host-disjoint、flow-disjoint、time-disjoint 和 cross-domain 划分要求，也支撑轻量化部署。

### 3.10 Learning in Multiple Spaces

该论文提出 Multi-Space Prototypical Learning，在 few-shot 入侵检测中融合 Euclidean、Cosine、Chebyshev 和 Wasserstein 等多种度量空间，并使用 Polyak 平均原型与 balanced episodic training 提高稳定性。

对 DA-FDIDS 的写作意义：它与 DA-FDIDS 的 MFL、RBF similarity、MHA feature weighting 高度相关，可作为少样本原型/度量学习的直接支撑文献。

### 3.11 Few-Shot Class-Incremental Learning for NIDS

该论文提出 BFS-NID，通过自监督 ViT 特征提取和分支分类器融合，使 NIDS 能够在少量样本条件下持续学习新攻击类别，并缓解灾难性遗忘。

对 DA-FDIDS 的写作意义：它支撑“新攻击类别少样本到达后持续纳入”的问题背景。DA-FDIDS 当前以 episode 少样本分类为主，后续可向类增量检测扩展。

### 3.12 Membership Inference and Adversarial Attack Defense Framework

该论文分析 ML-NIDS 面临的成员推理和对抗样本逃逸风险，并提出 HierarchicalDP 防御框架，根据网络流量特征安全等级施加差异化噪声，在降低攻击成功率的同时尽量保持分类准确率。

对 DA-FDIDS 的写作意义：它可用于补充模型部署风险与鲁棒性评测，说明 DA-FDIDS 不应只报告闭集分类性能，还应关注对抗扰动、隐私泄漏和部署安全。

## 4. 并入后的综述结构建议

DA-FDIDS 的相关工作可按如下顺序组织：

1. 动态图与流交互 NIDS：DIDS-MFL、E-GraphSAGE、EULER。
2. 域适应与跨域泛化：DI-NIDS、AEC-GAT、MTRF、SCF、Heterogeneous DA。
3. 概念漂移与在线适配：ReCDA、CADE、FG-SAT、MalMoE。
4. 流量基础表征与预训练：Learning Flow Semantics、Universal Embedding、FlowSem-MAE、TrafficLLM、IHUD-BERT。
5. 少样本度量学习与增量检测：Learning in Multiple Spaces、ICT-META、Few-Shot Class-Incremental Learning、FeCoGraph。
6. 鲁棒性与安全评测：Robustness Matters、Membership Defense、对抗攻击/数据泄漏相关工作。

## 5. 后续处理建议

1. 为 12 篇论文生成逐篇中文精读报告，建议放入 `AI驱动的网络流量检测分析系统/DA-FDIDS补充论文逐篇分析/`。
2. 从 12 篇论文中提取 BibTeX，统一写入 DA-FDIDS 论文参考文献库。
3. 在 DA-FDIDS 实验部分新增“严格划分与泄漏风险控制”小节，重点引用 IHUD-BERT 和 DI-NIDS。
4. 如果继续声称 TrafficEncoder 是 foundation encoder，应至少补充 Universal Embedding、FlowSem-MAE、TrafficLLM 或 IHUD-BERT 中一种预训练编码器的替换实验。

