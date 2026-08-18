# 035 融合流内与流间特征：多样特征驱动的多模态加密流量分类模型 / MeDF

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | 本文对应内容 | 覆盖状态 |
|---|---|---|
| Abstract | 第 2 节 | 已覆盖 |
| 1 Introduction | 第 3 节 | 已覆盖 |
| 2 Background and Related Work | 第 4 节 | 已覆盖 |
| 3 Description of MeDF | 第 5 至 9 节 | 已覆盖 |
| 4 Experiment | 第 10 至 15 节 | 已覆盖 |
| 5 Conclusion | 第 16 节 | 已覆盖 |

## 1. 文献身份

- 标题：Combine intra- and inter-flow: A multimodal encrypted traffic classification model driven by diverse features。
- 中文题名：融合流内与流间特征：多样特征驱动的多模态加密流量分类模型。
- 作者：Xiangbin Wang、Qingjun Yuan、Yongjuan Wang、Gaopeng Gou、Chunxiang Gu、Gang Yu、Gang Xiong。
- 期刊：Computer Networks，Vol. 245，2024，Article 110403。
- DOI：10.1016/j.comnet.2024.110403。
- 收稿/录用/在线：2024-01-15 / 2024-04-06 / 2024-04-08。
- 本地全文：`paper/10.1016_j.comnet.2024.110403.pdf`。
- 方法简称：MeDF。
- 任务定位：闭集加密流量分类；包含恶意 TLS 家族分类与普通应用分类，不包含未知拒识。

## 2. 摘要缩译

加密隐藏 payload 内容，不同加密协议与规避策略进一步增加分类难度。现有多模态方法通常只融合单条流内部的多类特征，忽略不同流之间的关联。论文提出 MeDF，同时利用流内和流间信息：把流的原始字节变换为时频谱图，并提取统计特征作为流内表示；再依据流之间的 IP 与协议关联构建流关系图，用 GCN 提取流间表示；最后融合三条分支完成分类。

作者在两个真实数据集上得到 98.57% 和 94.73% Accuracy，认为提升来自流内欧氏空间特征与流间非欧氏图特征的互补。

## 3. 引言缩译

论文把常用流量特征分为统计特征、时序特征、原始流量和图特征。统计与字节/时序特征描述单条流内部行为，图特征描述多条流共享端点或协议产生的关系。现有方法通常只选择其中一侧，无法同时利用局部内容和跨流上下文。

MeDF 将特征分为两级：流内侧包含原始字节时频谱图与统计向量，流间侧包含流关系图。三个专用模型分别学习谱图、统计和图表示，再级联拼接。作者将其称为多模态，因为不同表示具有互补性，并分别位于欧氏空间和非欧氏图空间。

## 4. 背景与相关工作缩译

加密流量分类是在不解密的条件下判断应用、用途或流量类别，可在 packet、flow 或 session 层级完成。flow 由源/目的 IP、源/目的端口和协议五元组定义，session 通常指两个节点间的双向流。

流内方法包括包长、到达间隔、原始 payload、Markov 特征和多分支神经网络；流间方法则利用共享 IP、端口、协议或访问关系建立图。AppNet、MIMETIC 等已有多模态模型主要融合单流内的 payload、协议字段或包序列。MeDF 的区别是额外显式建模多条流之间的关系。

## 5. 总体框架缩译

MeDF 包含四个部分：PCAP 预处理、流内特征提取、流间特征提取和多模态分类。

对每条流，模型提取原始字节序列并生成谱图，同时生成统计向量；CNN 与 MLP 分别编码两者并拼接为流内表示。对整个流集合建立关系图，GCN 输出每个流节点的流间表示。最后把同一流的流内与流间向量拼接，输入全连接层和 softmax 分类。

## 6. PCAP 预处理缩译

PCAP 按五元组切分为流。作者删除三类背景流：

- TCP 握手失败或没有业务 payload 的流。
- 全部数据包均为 DNS 查询的独立 DNS 流。
- LLMNR 名称解析流。

作者认为这些流在多种业务类别中频繁出现、区分性弱。但论文没有报告三类删除的数量、比例、标签分布，也没有验证恶意 DNS 或恶意 LLMNR 是否会被误删。对 CAEOS 而言，这些规则只能作为特定应用分类预处理，不能直接用于恶意流量统一数据集。

## 7. 流间关系图缩译

每条流是一个无向图节点，节点属性用于构图的部分为源 IP、目的 IP 和协议。若两条流的源/目的 IP 集合存在共同值且协议相同，则连接无向边。图不保留流方向，意图是表示共享通信端点带来的关联。

构图算法遍历所有流对，因此朴素时间复杂度为：

> 1 + 2 + … + (V − 1) = V(V − 1) ÷ 2。

> T构图 = O(V²)。

用稀疏邻接表保存时，空间复杂度为：

> S构图 = O(E)。

论文明确写成“build the relation graph of all flows”，但没有说明训练、验证和测试是否先隔离后分别构图。这给后续 GCN 带来关键的传导式泄漏风险。

## 8. 流内特征缩译

### 8.1 原始字节时频谱图

作者把流字节序列视为离散时间序列，使用短时傅里叶变换同时表示局部时间与频率信息。一般形式为：

> STFT{x[t]}(m, ω) = Σ x[t]w[t − mH]e⁻ʲωᵗ。

谱图取复数变换的幅值平方：

> Spectrogram{x[t]}(m, ω) = |X(m, ω)|²。

实际实验截取每条流前 500 个原始字节，不足补零；IP 地址被 mask。STFT window length 为 100，overlap rate 为 67%，window function 为 Hanning。谱图交给轻量化 VGG 风格 CNN，部分普通卷积替换为深度可分离卷积。

作者还用样本熵讨论时频图的信息量，并提出：

> SampEn(seq) < tfEn(seq) ≤ 2 × SampEn(seq)。

这一不等式更多是作者的理论解释。STFT 是原字节的确定性变换，不会凭空增加 Shannon 信息；二维展开可能提高神经网络可利用性，但“信息熵增加”不能直接当作新模态独立信息的证明。

### 8.2 统计特征

统计分支包括：

- 包长分布：均值、中位数、众数、标准差、分位数、峰度、偏度。
- 包间到达时间：均值、方差、最大值等。
- payload 长度：正向/反向字节数与包数，以及最大、最小、均值、方差和标准差。
- 字节发送率：总速率、正向速率、反向速率。
- 加密算法套件与协议类型。

统计向量由三隐藏层 MLP 编码。论文没有给出完整特征字段表、缺失值处理和标准化参数，因此工程复现仍需回到源码或补充材料核对。

## 9. 三分支学习与融合缩译

图分支使用 3 个图卷积层和 1 个全连接层，其中并行图卷积分别采用 sum 与 max 聚合。其节点分类交叉熵记为：

> L流间 = −Σ p图(i) log q图(i)。

谱图 CNN 和统计 MLP 分别优化：

> L谱图 = −Σ p谱(i) log q谱(i)。

> L统计 = −Σ p统计(i) log q统计(i)。

流内损失为：

> L流内 = L谱图 + L统计。

三条分支向量级联后，由最终分类头产生多模态损失 L融合。总损失为：

> L总 = L流内 + L流间 + L融合。

作者为流内和流间损失设置相同权重，以避免其中一侧被忽略。该做法是等权多任务监督，不是证据理论中的可靠度校准，也没有显式衡量分支冲突。

## 10. 数据集缩译

### 10.1 Malicious_TLS

原数据包含 2018–2021 年的 22 个恶意代码家族和 benign TLS。论文只选取 6 类和 benign：

| 类别 | 流数 |
|---|---:|
| Arachni | 2,000 |
| Awvs | 2,000 |
| Burpsuite | 2,000 |
| Shifu | 2,000 |
| Tiggre | 2,000 |
| Tor | 2,000 |
| Benign | 4,000 |

标签语义并不完全同质：Arachni、AWVS、BurpSuite 是扫描/测试工具，Tor 是匿名网络类别，不能无条件等同为六个恶意软件家族。CAEOS 引用该结果前必须回查数据集标签说明。

### 10.2 ISCX VPN-nonVPN 2016

原数据包含 VPN/非 VPN 的 14 类，约 28 GB。论文只使用 6 个普通业务标签：Chat 31,334、Mail 24,719、File Transfer 67,790、Streaming 36,128、Torrent 169,309、VoIP 53,040。

该设置是应用类型闭集分类，不是恶意检测。论文没有报告抽样原因、train/validation/test 比例、capture 分组或类别内 VPN/非 VPN 的具体合并方式。

## 11. 实验设置与指标缩译

环境为 Intel i7-9700K、NVIDIA RTX 3080、32 GB RAM、Windows、Python 3.7.13 和 PyTorch 1.11.0。

论文报告 Accuracy、Recall、FPR 和 Precision：

> Accuracy = (TP + TN) ÷ (TP + TN + FP + FN)。

> Recall = TP ÷ (TP + FN)。

> FPR = FP ÷ (FP + TN)。

> Precision = TP ÷ (TP + FP)。

但两个任务均为多分类，论文没有说明 one-vs-rest 的 averaging 方式，也没有说明哪个类别是 positive。表中的 FPR 因此不是 CAEOS 的 benign FAR，更不是 FPR@95TPR。

基线包括 1D-CNN、XGBoost、ACID、ProGraph、AppNet 和 MIMETIC。论文没有报告训练轮次、batch size、optimizer、learning rate、seed、重复次数或验证集。

## 12. 主结果缩译

### 12.1 Malicious_TLS

| 方法 | Accuracy | Recall | FPR | Precision |
|---|---:|---:|---:|---:|
| 1D-CNN | 92.37 | 91.76 | 0.31 | 90.78 |
| XGBoost | 90.29 | 90.17 | 0.37 | 90.21 |
| ACID | 96.13 | 95.87 | 0.22 | 95.98 |
| ProGraph | 91.55 | 91.34 | 0.33 | 91.39 |
| AppNet | 95.52 | 95.30 | 0.27 | 95.52 |
| MIMETIC | 96.73 | 96.32 | 0.26 | 96.29 |
| MeDF | 98.57 | 98.62 | 0.22 | 98.14 |

### 12.2 ISCX VPN-nonVPN 2016

| 方法 | Accuracy | Recall | FPR | Precision |
|---|---:|---:|---:|---:|
| 1D-CNN | 89.68 | 89.25 | 0.42 | 89.17 |
| XGBoost | 88.32 | 88.27 | 0.41 | 89.06 |
| ACID | 92.73 | 92.48 | 0.30 | 91.63 |
| ProGraph | 94.35 | 94.54 | 0.30 | 93.89 |
| AppNet | 90.17 | 90.34 | 0.34 | 90.28 |
| MIMETIC | 91.56 | 91.45 | 0.32 | 90.89 |
| MeDF | 94.73 | 94.56 | 0.28 | 93.86 |

所有数值按原表的百分比口径抄录。MeDF 在 Malicious_TLS 上领先，但在 ISCX 上 Accuracy 仅比 ProGraph 高 0.38 个百分点，Precision 还略低于 ProGraph。论文没有显著性检验，不能断言该小差异稳定。

## 13. 混淆矩阵与谱图讨论缩译

作者观察到 Malicious_TLS 各类识别接近 1，而 ISCX 多数类别低于 95%。论文把差异归因于 ISCX 结构更复杂、流间关联更弱，导致图模态贡献降低。

谱图展示不同应用/恶意类别的时频纹理差异。该可视化说明 STFT 为 CNN 提供了结构化输入，但没有证明这些纹理跨 capture、跨工具版本或跨网络环境保持稳定。

## 14. 消融实验缩译

消融只在 Malicious_TLS 上进行：

| 模型 | Accuracy | Recall | FPR | Precision |
|---|---:|---:|---:|---:|
| MeDF | 98.57 | 98.62 | 0.22 | 98.14 |
| intra-MeDF | 96.82 | 92.76 | 0.31 | 95.79 |
| inter-MeDF | 90.25 | 89.92 | 0.97 | 90.27 |

原文结论称相对仅流内模型提升 1.75 个百分点，相对仅流间模型提升 8.32 个百分点。流内特征本身比流间图更强，图分支主要起补充作用。

该消融没有分开谱图与统计分支，也没有 random-edge、degree-preserving 或移除 IP 的图捷径对照，因此不能确认图增益来自真正跨流行为，而不是 capture 内 IP 标签同质性。

## 15. 复杂度缩译

谱图计算在原序列长度 N、窗口长度 M 下的时间复杂度写为 O(NM log M)，空间复杂度为 O(NM)。朴素流关系构图为 O(V²)，稀疏存储为 O(E)。

MeDF 有 2.54 million 参数，每 epoch 运行时间 47.5 s；MIMETIC 为 1.78 million 参数和 39.4 s。作者认为性能提升足以抵消额外开销。但这些数字不包含 PCAP 解析、STFT 缓存和全图 O(V²) 构建成本，不能用于端到端吞吐结论。

## 16. 结论缩译

论文认为同时使用谱图、统计与流关系图，可以比只用流内或流间特征获得更完整的加密流量表示。MeDF 的贡献是把欧氏的单流特征与非欧氏的跨流关系放入同一闭集分类框架；开放集拒识、校准和真实未知攻击不在研究范围内。

# 第二部分：独立技术分析

## A. 一句话结论

MeDF 是当前文献集中最接近“字节/统计/关系图三分支”的多模态闭集基线，但其全流构图、IP 关联、拆分缺失和多分类 FPR 口径使结果存在显著泄漏与误读风险；CAEOS 应采纳其三分支结构，必须重写协议后才能进入正式对照。

## B. 协议审计

- 任务：固定类别闭集分类。
- unknown：没有 leave-family-out 或拒识任务。
- split：没有 train/validation/test 比例与 grouped 规则。
- 构图：算法描述对 all flows 先建图，未证明训练/测试子图隔离。
- 标签传播风险：GCN 可能让测试节点通过边接收训练节点信息。
- 环境捷径：边直接使用源/目的 IP 和协议，可能编码 capture、设备和标签分组。
- 模型选择：无独立 validation 说明。
- 统计：无 seeds、方差、置信区间和显著性检验。
- 指标：多分类 FPR averaging 未定义。
- 协议等级：`P3-transductive-graph-and-split-unclear`。
- 可比性：`C1-组件可比`，不能进入 strict-v4 主表。

## C. 是否属于真正多模态

MeDF 比 YaTC 更接近多模态：它有三个显式编码分支，分别处理字节谱图、统计向量和跨流图；图分支还引入单条流之外的上下文。因此从工程多视图定义看，可以称为“同源 PCAP 的三分支多模态”。

但三者并非独立传感器：谱图是原字节的确定性变换，统计量也由相同流计算，图由同一批流的五元组关系构造。它们的错误可能高度相关。CAEOS 可以借鉴分支结构，但不能预设三分支证据条件独立，必须实测分支冲突、冗余和互补性。

## D. 对 CAEOS 三模态定义的纠偏

推荐把项目三模态固定为：

1. 原始字节模态：header/payload 或包字节编码器。
2. 流统计/时序模态：包长、方向、IAT、持续时间、速率等。
3. 关系上下文模态：同 capture 内、严格时间可用的 host/flow 图。

若当前第三模态是另一种对相同 payload 的图像变换，它只能叫同源视图，不能宣称独立模态。MeDF 可作为关系图模态的直接出处，但 strict-v4 中每个样本只能使用预测时刻之前可观测的邻居。

## E. 标签与预处理风险

- DNS/LLMNR 一律删除不适合恶意检测，因为这些协议本身可能承载攻击或恶意基础设施行为。
- TCP 握手失败流可能包含扫描和 DoS，不能按“无业务 payload”直接删除。
- Malicious_TLS 只选 6/22 类，不能称为全数据集结果。
- Tor、扫描工具和恶意软件标签语义混合，需要重新映射 attack coarse/fine labels。
- 前 500 字节和统计特征属于实验视图，不应覆盖统一基础数据的完整字节与包序列。

## F. 三层指标映射

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | Accuracy、Recall、Precision、多分类 FPR | Macro-F1、BA、per-class Recall、Benign FAR | 部分覆盖 |
| 未知检测 | 无 | AUROC、AUPR-Out、FPR@95TPR、Unknown-F1 | 缺失 |
| 联合开放集 | 无 | OSCR、OpenAUC、Known Acceptance、Unknown Rejection | 缺失 |
| 校准 | 无 | ECE、Brier、NLL | 缺失 |

## G. 95%/5% 安全验收

Malicious_TLS 的 Accuracy/Recall/Precision 均超过 95%，但标签语义、拆分和 averaging 不清楚，不能直接认定 Known Macro-F1 ≥ 95%。表中 FPR 0.22% 是未定义 averaging 的多分类 FPR，不是 benign 被判恶意的 FAR，也不是 FPR@95TPR。

ISCX Accuracy 94.73%、Recall 94.56%、Precision 93.86%，即使按原口径也没有达到 95%。两个实验都没有 unknown 指标与 OSCR，因此均不能通过 CAEOS 95%/5% 安全表。

## H. CAEOS 采纳与否决

### 采纳

- 采纳字节、统计、关系图三个专用编码分支。
- 采纳流内/流间两级消融和分支级损失。
- 采纳 STFT 谱图作为字节模态的可选视图基线。
- 采纳跨流关系对单流分类可能提供补充信息的研究假设。

### 有条件采纳

- 图只能在每个 split/capture 内独立构建，validation/test 不得与 training 消息传递。
- 在线实验只能连接决策时刻之前存在的邻居，禁止未来流信息。
- IP、协议、度数与 connected component 必须做捷径消融。
- 多模态融合必须增加 conflict/reliability head，而不是只做等权拼接。

### 不采纳

- 不先全量构图再随机划分节点。
- 不把多分类平均 FPR 写成 benign FAR 或 FPR95。
- 不删除所有 DNS、LLMNR、无 payload TCP 流作为统一规则。
- 不把 6/22 类子集结果称为全量恶意 TLS 结论。
- 不把 STFT 的二维展开解释为创造了额外信息。

## I. CAEOS 可执行实验

1. `E-MEDF-01`：严格复现三分支 closed-set baseline，图按 capture-grouped split 隔离。
2. `E-MEDF-02`：bytes-only、stats-only、graph-only、bytes+stats、bytes+graph、stats+graph、三分支全组合。
3. `E-MEDF-03`：concat、gated fusion、attention fusion、evidential conflict fusion 同协议比较。
4. `E-MEDF-04`：random edges、shuffle IP、remove protocol、degree-only、component-only 捷径审计。
5. `E-MEDF-05`：inductive unseen-node 与 transductive closed-graph 分开报告。
6. `E-MEDF-06`：leave-family-out 下分别报告三分支 risk AUROC 与联合 OSCR。
7. `E-MEDF-07`：DNS/LLMNR/握手失败流保留与删除对恶意 Recall、Benign FAR 的影响。
8. `E-MEDF-08`：5 seeds、scenario-block bootstrap 和 95%/5% 安全表。

## J. 可引用与不可引用主张

### 可引用

- MeDF 同时编码原始字节谱图、流统计和流关系图。
- 在论文固定协议下，MeDF 在 Malicious_TLS 获得 98.57% Accuracy。
- 相对仅流内分支，加入流间图使 Accuracy 提升 1.75 个百分点。
- 图分支单独性能弱于流内分支，说明其更适合作为补充上下文。

### 不可引用

- MeDF 已证明开放集恶意检测有效。
- MeDF 的 FPR 0.22% 等于 benign FAR 或 FPR@95TPR。
- MeDF 已在全部 22 个 Malicious_TLS 家族上验证。
- MeDF 的全流构图协议不存在训练测试泄漏。
- MeDF 三个分支提供统计独立证据。
- MeDF 已满足 CAEOS 95%/5% 验收。

## K. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过，本地正式 Computer Networks PDF 与全文抽取存在
- G2 身份门：通过至 DOI、卷号、文章号和日期，Zotero 待办
- G3 任务门：通过，明确为闭集分类
- G4 协议门：通过，`P3-transductive-graph-and-split-unclear`
- G5 方法门：通过
- G6 结果门：通过，表 2 至表 8 与图 5 至图 7 已核读
- G7 对比门：通过，但仅组件级可比
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
