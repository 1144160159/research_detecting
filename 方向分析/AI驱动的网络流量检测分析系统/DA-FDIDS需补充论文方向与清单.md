# DA-FDIDS需补充论文方向与清单

生成日期：2026-06-24  
方向归属：AI驱动的网络流量检测分析系统  
模型定位：域自适应基础表征增强的少样本动态网络入侵检测模型

更新日期：2026-06-25  
更新状态：最优先补充的 12 篇论文已补齐，均已放入本地 `paper/` 目录；整理结果见 `AI驱动的网络流量检测分析系统/DA-FDIDS补充论文并入记录.md`。

## 1. 总体判断

DA-FDIDS 的相关论文不应按传统 IDS、加密流量分类或通用异常检测泛泛补充，而应围绕模型中的关键模块补齐证据链：

- DIDS-MFL 基线：动态图、解耦表示、少样本 episode 检测。
- TrafficEncoder：流量基础表征、预训练流量模型、通用 embedding。
- LoRA / Stable-LoRA：参数高效适配、小样本在线更新、稳定性约束。
- GRL / MMD：域对抗、分布对齐、跨域泛化。
- Cache / RBF / MHA：检索增强、原型/度量学习、局部相似性建模。
- 实验可信性：跨数据集、跨主机、跨时间、概念漂移、开放集与 OOD。

因此建议按“必须补、建议补、可选补”三层补论文。

## 2. A 类：必须补充方向

### A1. 动态图少样本网络入侵检测

**为什么必须补**：DA-FDIDS 的骨架来自 DIDS-MFL，模型中 TGNMemory、动态图扩散、SelfExpr/MFL、episode 训练都需要这一方向支撑。

**应补论文类型**：

1. 动态图 NIDS / temporal graph intrusion detection。
2. 图神经网络流量检测，尤其是 edge-feature graph、flow interaction graph。
3. few-shot NIDS / meta-learning NIDS。
4. 动态图横向移动、攻击链检测。

**代表论文清单**：

| 优先级 | 论文 | 状态 | 用途 |
|---|---|---|---|
| 必引 | Disentangled Dynamic Intrusion Detection / DIDS-MFL | 本地已有：`paper/10.1109_TPAMI.2025.3595671.pdf` | DA-FDIDS 直接基线 |
| 必补 | E-GraphSAGE: A Graph Neural Network based Intrusion Detection System for IoT | 已补：`paper/10.1109_NOMS54207.2022.9789878.pdf` | 图 NIDS 基础工作，支撑边特征图建模 |
| 必补 | Euler: Detecting Network Lateral Movement via Scalable Temporal Link Prediction | 已补：`paper/10.14722_ndss.2022.24107.pdf` | 动态图安全检测，支撑时序交互建模 |
| 建议 | FIR-GNN: Flow Interaction Relationships for Intrusion Detection | 本地元数据出现 | 流交互关系图，支撑 flow interaction graph |
| 建议 | Hierarchical GNN for Resilient Intrusion Detection With Limited Labeled Data | 本地元数据出现 | 有限标签 + 图 NIDS |
| 建议 | FeCoGraph: Label-Aware Federated Graph Contrastive Learning for Few-Shot NIDS | 本地已有 | few-shot + graph + federated 支撑 |

### A2. 域适应与跨域泛化 NIDS

**为什么必须补**：DA-FDIDS 名称中的 DA 以及 GRL、DomainDiscriminator、MMD 都需要跨域域适应论文支撑。这是 DA-FDIDS 相对 DIDS-MFL 的核心增量。

**应补论文类型**：

1. 域对抗 NIDS：GRL、domain discriminator、domain-invariant representation。
2. 统计分布对齐：MMD、CORAL、特征函数、moment matching。
3. 多域表示学习：multi-domain transformation、cross-dataset NIDS。
4. 异构域适应：不同数据集特征空间不一致时的迁移。

**代表论文清单**：

| 优先级 | 论文 | 状态 | 用途 |
|---|---|---|---|
| 必补 | DI-NIDS: Domain invariant network intrusion detection system | 已补：`paper/10.1016_j.knosys.2023.110626.pdf` | 直接支撑 GRL/domain-adversarial 设计 |
| 必引 | A Domain Adaptive IoT IDS Based on AEC-GAT and Joint Domain Adversary | 本地已有：`paper/10.1109_TII.2025.3631964.pdf` | 图结构 + 域对抗 |
| 必引 | MTRF: Multidomain Transformation Representation for Network Flows in NIDS | 本地已有：`paper/10.1109_TDSC.2025.3649110.pdf` | 多域表示迁移 |
| 必引 | Encrypted Traffic Classification Through Deep Domain Adaptation Network With Smooth Characteristic Function | 本地已有：`paper/10.1109_TNSM.2025.3534791.pdf` | 统计分布对齐，支撑 MMD/SCF |
| 必补 | Heterogeneous Domain Adaptation for IoT Intrusion Detection | 已补：`paper/10.1109_JIOT.2023.3239872.pdf` | 异构域适应，补足跨特征空间迁移 |
| 建议 | Unsupervised Cross-Domain Attack Traffic Classifier for Intelligent Connected Vehicle | 本地元数据出现 | 无监督跨域攻击流量分类 |

### A3. 概念漂移、图漂移与在线适配

**为什么必须补**：DA-FDIDS 使用 LoRA online adaptation、Stable-LoRA、cache fusion、RBF/MHA，这些模块的合理性来自真实网络环境的概念漂移、图漂移和在线适应需求。

**应补论文类型**：

1. self-supervised concept drift adaptation for NIDS。
2. graph drift / temporal drift in malicious traffic detection。
3. test-time adaptation / online adaptation。
4. drift detection and explanation。

**代表论文清单**：

| 优先级 | 论文 | 状态 | 用途 |
|---|---|---|---|
| 必引 | Self-Supervised Adaptation Method to Concept Drift for NIDS / ReCDA | 本地已有：`paper/10.1109_TDSC.2025.3599321.pdf` | 概念漂移与持续适应 |
| 必补 | CADE: Detecting and Explaining Concept Drift Samples for Security Applications | 已补：`paper/CADE.pdf` | 漂移检测与解释，支撑在线适配背景 |
| 必引 | MalMoE: Mixture-of-Experts Enhanced Encrypted Malicious Traffic Detection Under Graph Drift | 本地已有 | 图漂移 + MoE，支撑 drift-aware 检测 |
| 必引 | FG-SAT: Efficient Flow Graph for Encrypted Traffic Classification Under Environment Shifts | 本地已有 | 环境偏移下的流图鲁棒性 |
| 建议 | MTG-GAN: Masked Temporal Graph GAN for Cross-Domain System Log Anomaly Detection | 本地元数据出现 | 跨域时序图异常检测，可作邻域支撑 |

### A4. 流量基础模型、预训练与通用表征

**为什么必须补**：DA-FDIDS 中 TrafficEncoder 被写作 Foundation Encoder，但当前代码若只是 MLP，则必须用这一方向论文支撑“可替换为预训练流量编码器”的设计，并避免过度声称。

**应补论文类型**：

1. traffic foundation model / traffic pre-training。
2. encrypted traffic representation learning。
3. universal traffic embedding。
4. contrastive pretraining / masked autoencoder / transformer for traffic。

**代表论文清单**：

| 优先级 | 论文 | 状态 | 用途 |
|---|---|---|---|
| 必引 | Learning Flow Semantics for Encrypted Traffic Analysis: A Contrastive Pre-training Approach | 本地已有：`paper/10.1109_TDSC.2026.3677663.pdf` | TrafficEncoder / 预训练表征支撑 |
| 必引 | When Pre-Training Meets Contrast Learning: Few-Shot Encrypted Traffic Classification With Novelty Detection | 本地已有：`paper/10.1109_TON.2026.3674624.pdf` | 预训练 + few-shot + novelty |
| 必引 | Robustness Matters: Pre-Training Can Enhance the Performance of Encrypted Traffic Analysis | 本地已有：`paper/10.1109_TIFS.2025.3613970.pdf` | 预训练提升鲁棒性 |
| 必补 | Universal Embedding Function for Traffic Classification via QUIC Domain Recognition Pretraining | 已补：`paper/10.1109_tnsm.2025.3642984_dup.pdf` | 通用流量 embedding |
| 必补 | FlowSem-MAE: Protocol-Native Tabular Pre-training for Encrypted Traffic Classification | 已补：`paper/10.48550_arXiv.2603.10051.pdf` | MAE 式流量预训练 |
| 建议 | TrafficLLM / LLM for Network Traffic Analysis | 已补：`paper/10.48550_arXiv.2504.04222.pdf` | 流量大模型背景 |
| 建议 | IHUD-BERT: Large-Scale Network Traffic Classification Based on Pre-Training Transformers and Knowledge Distillation | 已补：`paper/10.1109_tccn.2026.3695843_dup.pdf` | transformer 预训练流量分类 |

### A5. LoRA、PEFT 与小样本在线微调

**为什么必须补**：DA-FDIDS 的 B2/B6 是 LoRA online adaptation 和 Stable-LoRA，这是论文创新点之一。必须补充“为什么不用全参数微调、为什么 LoRA 适合流量检测”的文献。

**应补论文类型**：

1. LoRA / PEFT for encrypted traffic analytics。
2. mixture of LoRA experts / SVD-LoRA。
3. online adaptation / test-time adaptation with parameter-efficient tuning。
4. stable adaptation / anti-forgetting / regularized PEFT。

**代表论文清单**：

| 优先级 | 论文 | 状态 | 用途 |
|---|---|---|---|
| 必引 | Adapting Large Language Models for Encrypted Traffic Analysis Services: Mixture of LoRA Experts | 本地已有：`paper/10.1109_TSC.2026.3671484.pdf` | 直接支撑 LoRA/PEFT 用于流量分析 |
| 必补 | TrafficLLM 相关论文 | 已补：`paper/10.48550_arXiv.2504.04222.pdf` | 流量 LLM + PEFT 背景 |
| 建议 | Mixture-of-LoRA / SVD-LoRA / PEFT surveys | 需联网补 | 用于解释 Stable-LoRA 的参数高效稳定适配 |
| 可选 | General LoRA / PEFT 原始方法论文 | 需补 | 如果方法部分要系统解释 LoRA，可补基础引用 |

## 3. B 类：建议补充方向

### B1. 检索增强、原型学习与度量学习

**为什么建议补**：DA-FDIDS 的 cache fusion、RBF similarity matrix、MHA feature weighting，本质上是少样本检索增强和度量判别。当前综述里这条线还可以更清楚。

**代表论文清单**：

| 优先级 | 论文 | 状态 | 用途 |
|---|---|---|---|
| 建议 | Learning in Multiple Spaces: Prototypical Few-Shot Learning With Metric Fusion for Next-Generation Network Security | 已补：`paper/10.1109_tnsm.2026.3665647_dup.pdf` | 支撑 MFL/metric fusion |
| 建议 | ICT-META: In-Context Aware Few-Shot Learner for Encrypted Traffic Classification | 本地已有 | in-context few-shot，支撑 episode 检测 |
| 建议 | Space Decoupled Prototype Learning for Few-Shot Attack Detection in CPS | 本地元数据出现 | 原型学习 + few-shot 攻击检测 |
| 建议 | Few-Shot Class-Incremental Learning Method for NIDS | 已补：`paper/10.1109_tnsm.2023.3332284_dup.pdf` | 类增量少样本检测 |
| 可选 | Efficient Intrusion Detection for Edge Network via Multi-Stage Few-Shot Class-Incremental Learning | 本地元数据出现 | 边缘网络类增量 few-shot |

### B2. 开放集、未知攻击与 zero-day 检测

**为什么建议补**：DA-FDIDS 当前不是严格开放集方法，但论文如果要强调 unknown/few-shot/新型攻击，必须有开放集文献作为边界说明和未来扩展支撑。

**代表论文清单**：

| 优先级 | 论文 | 状态 | 用途 |
|---|---|---|---|
| 建议 | Multi-Dimensional Cross-Granularity Open-Set Network Intrusion Detection | 本地已有：`paper/10.1109_TNSM.2026.3693141.pdf` | NIDS 开放集代表 |
| 建议 | End-to-End Open-Set Semi-Supervised Learning for Fine-Grained Encrypted Traffic Classification | 本地已有：`paper/10.1109_TIFS.2026.3653575.pdf` | 开放集 + 半监督 |
| 建议 | Detection of Unknown Attacks Through Encrypted Traffic: Gaussian Prototype-Aided VAE | 本地已有：`paper/10.1109_TIFS.2025.3612141.pdf` | 未知攻击检测 |
| 建议 | Zero-X: Blockchain-Enabled Open-Set Federated Learning for Zero-Day Attack Detection in IoV | 本地元数据出现 | zero-day + federated + open-set |
| 可选 | Autoencoder + Double Random Forest IDS for Unknown Attack Defense | 本地元数据出现 | 传统未知攻击防御对比 |

### B3. 图关系增强、多粒度流量建模与加密恶意流量检测

**为什么建议补**：DA-FDIDS 虽然不是加密流量模型，但 DIDS-MFL 和本地课题都与加密恶意流量检测相邻。补这类论文可支撑“图关系、多粒度、鲁棒流量表征”。

**代表论文清单**：

| 优先级 | 论文 | 状态 | 用途 |
|---|---|---|---|
| 建议 | BPF-DAG: Byte-Packet-Flow Features Fusion via Dynamic Attributed Graph | 本地已有 | 动态属性图 + 多粒度特征 |
| 建议 | BPF-GNN: Multi-Granularity Feature Extraction Using GNN for Encrypted Traffic Classification | 本地已有 | 多粒度 GNN |
| 建议 | MTDecipher: Robust Encrypted Malicious Traffic Detection via Multi-Task GNN | 本地已有 | 多任务 GNN + 鲁棒检测 |
| 建议 | MTSecurity: Privacy-Preserving Malicious Traffic Classification Using GNN and Transformer | 本地元数据出现 | GNN + Transformer |
| 可选 | HINHJ: Heterogeneous Graph Neural Network for DNS Hijacking Detection | 本地元数据出现 | 异构图安全检测案例 |

### B4. 鲁棒性、OOD、对抗攻击与数据泄漏风险

**为什么建议补**：远程 sanity check 已指出主机、端口、拓扑或 `msg` 特征捷径风险。论文中需要补“严谨评测和鲁棒性”方向，说明为什么采用 host-disjoint/cross-domain/time-disjoint。

**代表论文清单**：

| 优先级 | 论文 | 状态 | 用途 |
|---|---|---|---|
| 建议 | Robustness Matters: Pre-Training Can Enhance Encrypted Traffic Analysis | 本地已有 | 鲁棒性与预训练 |
| 建议 | Membership Inference and Adversarial Attack Defense Framework for Network Traffic Classifiers | 已补：`paper/10.1109_tai.2024.3357791_dup.pdf` | 安全评测与防御 |
| 建议 | ProGen: Projection-Based Adversarial Attack Generation Against NIDS | 本地元数据出现 | 对抗攻击 |
| 建议 | Constraining Adversarial Attacks on NIDS: Transferability and Defense Analysis | 本地元数据出现 | 对抗迁移与防御 |
| 建议 | Mixed label noise / open-set noise robust NIDS papers | 本地有相关证据 | 标签噪声、开放集噪声 |

## 4. C 类：可选补充方向

### C1. 联邦、隐私与跨组织协同检测

**何时补**：如果 DA-FDIDS 后续要写成跨机构、多域协同检测，可补。若当前只做单机跨数据集实验，可少写。

**代表论文**：

- FeCoGraph: Label-Aware Federated Graph Contrastive Learning for Few-Shot NIDS。
- Privacy-Preserving Few-Shot Traffic Detection Against APTs via Federated Meta Learning。
- Privacy-Preserving GNN for NIDS。
- Zero-X: Open-Set Federated Learning for Zero-Day Attack Detection in IoV。

### C2. 多模态/多源异构安全数据融合

**何时补**：如果论文想从“AI驱动网络流量检测系统”扩展到资产、日志、行为、告警或知识图谱融合，可补。若 DA-FDIDS 只使用流量数据，则不建议作为主线。

**代表论文**：

- XG-NID: heterogeneous GNN + LLM for NIDS。
- Multimodal fusion based few-shot NIDS。
- Knowledge graph-enhanced multi-view IDS。
- Semi-supervised encrypted malicious traffic detection based on multimodal traffic characteristics。

### C3. 应用场景扩展：IoT、IoV、工业控制、边缘网络

**何时补**：如果实验数据集包含 ToN-IoT、BoT-IoT、Edge-IIoT、IoV 或 ICS，可在实验背景中补少量场景论文。

**代表论文**：

- Domain adaptive IoT IDS / AEC-GAT。
- Unsupervised cross-domain attack traffic classifier for intelligent connected vehicle。
- Industrial open-set / unknown attack detection。
- Efficient edge network few-shot class-incremental IDS。

## 5. 最终建议清单

### 5.1 最优先补的 12 篇（已完成）

1. DI-NIDS: Domain invariant network intrusion detection system。已补：`paper/10.1016_j.knosys.2023.110626.pdf`
2. E-GraphSAGE: A Graph Neural Network based Intrusion Detection System for IoT。已补：`paper/10.1109_NOMS54207.2022.9789878.pdf`
3. Euler: Detecting Network Lateral Movement via Scalable Temporal Link Prediction。已补：`paper/10.14722_ndss.2022.24107.pdf`
4. CADE: Detecting and Explaining Concept Drift Samples for Security Applications。已补：`paper/CADE.pdf`
5. Heterogeneous Domain Adaptation for IoT Intrusion Detection。已补：`paper/10.1109_JIOT.2023.3239872.pdf`
6. Universal Embedding Function for Traffic Classification via QUIC Domain Recognition Pretraining。已补：`paper/10.1109_tnsm.2025.3642984_dup.pdf`
7. FlowSem-MAE: Protocol-Native Tabular Pre-training for Encrypted Traffic Classification。已补：`paper/10.48550_arXiv.2603.10051.pdf`
8. TrafficLLM / Large Language Model for Network Traffic Analysis。已补：`paper/10.48550_arXiv.2504.04222.pdf`
9. IHUD-BERT: Network Traffic Classification Based on Pre-Training Transformers and Knowledge Distillation。已补：`paper/10.1109_tccn.2026.3695843_dup.pdf`
10. Learning in Multiple Spaces: Prototypical Few-Shot Learning With Metric Fusion for Network Security。已补：`paper/10.1109_tnsm.2026.3665647_dup.pdf`
11. Few-Shot Class-Incremental Learning Method for Network Intrusion Detection。已补：`paper/10.1109_tnsm.2023.3332284_dup.pdf`
12. Membership Inference and Adversarial Attack Defense Framework for Network Traffic Classifiers。已补：`paper/10.1109_tai.2024.3357791_dup.pdf`

以上 12 篇的并入说明见 `AI驱动的网络流量检测分析系统/DA-FDIDS补充论文并入记录.md`。

### 5.2 本地已有但必须精读引用的 15 篇

1. `paper/10.1109_TPAMI.2025.3595671.pdf`：DIDS-MFL / Disentangled Dynamic Intrusion Detection。
2. `paper/10.1109_TII.2025.3631964.pdf`：AEC-GAT + Joint Domain Adversary。
3. `paper/10.1109_TDSC.2025.3599321.pdf`：ReCDA / Concept Drift Adaptation。
4. `paper/10.1109_TDSC.2025.3649110.pdf`：MTRF。
5. `paper/10.1109_TNSM.2025.3534791.pdf`：Deep Domain Adaptation With Smooth Characteristic Function。
6. `paper/10.1109_TDSC.2026.3677663.pdf`：Learning Flow Semantics / TACO。
7. `paper/10.1109_TON.2026.3674624.pdf`：When Pre-Training Meets Contrast Learning。
8. `paper/10.1109_TIFS.2025.3613970.pdf`：Robustness Matters。
9. `paper/10.1109_TSC.2026.3671484.pdf`：Mixture of LoRA Experts for Encrypted Traffic Analytics。
10. `paper/10.1109_TIFS.2025.3541890.pdf`：FeCoGraph。
11. `paper/10.1109_TIFS.2025.3571663.pdf`：FG-SAT。
12. `paper/10.48550_arXiv.2602.10157.pdf`：MalMoE。
13. `paper/10.1109_TIFS.2025.3643127.pdf`：BPF-DAG。
14. `paper/10.1109_TNSM.2026.3671203.pdf`：BPF-GNN。
15. `paper/10.1109_TNSM.2026.3693141.pdf`：Multi-Dimensional Cross-Granularity Open-Set NIDS。

## 6. 不建议重点补的方向

1. **传统机器学习 IDS**：如普通 SVM、RF、KNN、CNN-LSTM 分类器，除非作为基础背景，不应占综述主体。
2. **纯协议解析/抓包工程论文**：DA-FDIDS 不做高速采集、流重组、协议解析，不是全流量工程系统。
3. **泛泛的日志异常检测**：除非涉及跨域、时序图或少样本，否则与 DA-FDIDS 主线较远。
4. **单纯多模态安全融合**：资产、日志、行为、知识图谱融合不是 DA-FDIDS 当前模型主体。
5. **与网络流量无关的通用异常检测**：只能作为方法类旁证，不适合作为主要相关工作。

## 7. 参考链接

- DI-NIDS: <https://dl.acm.org/doi/10.1016/j.knosys.2023.110626>
- E-GraphSAGE: <https://arxiv.org/abs/2103.16329>
- Euler / NDSS 2022: <https://www.ndss-symposium.org/ndss-paper/auto-draft-227/>
- CADE / USENIX Security 2021: <https://www.usenix.org/conference/usenixsecurity21/presentation/yang-limin>
- Heterogeneous Domain Adaptation for IoT Intrusion Detection: <https://arxiv.org/abs/2301.09801>
- Universal Embedding Function for Traffic Classification: <https://arxiv.org/abs/2502.12930>
- FlowSem-MAE: <https://arxiv.org/abs/2603.10051>
- TrafficLLM: <https://arxiv.org/html/2504.04222v2>
- Learning Flow Semantics: <https://www.computer.org/csdl/journal/tq/5555/01/11456104/2f9c6hMVVLy>
- Mixture of LoRA Experts for Encrypted Traffic Analytics: <https://www.computer.org/csdl/journal/sc/2026/02/11425822/2eOBlfI7l9m>

