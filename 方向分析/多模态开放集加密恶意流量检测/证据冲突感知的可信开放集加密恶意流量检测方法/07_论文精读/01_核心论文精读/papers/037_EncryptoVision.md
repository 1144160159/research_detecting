# 037 EncryptoVision：基于双模态融合的加密流量多分类模型

# 第一部分：原文结构化全文缩译

## 0. 原文章节覆盖表

| 原文章节 | 本文对应内容 | 覆盖状态 |
|---|---|---|
| Abstract | 第 2 节 | 已覆盖 |
| 1 Introduction | 第 3 节 | 已覆盖 |
| 2 Related Works | 第 4 节 | 已覆盖 |
| 3 Our Model | 第 5 至 9 节 | 已覆盖 |
| 4 Experiments and Performance Evaluation | 第 10 至 15 节 | 已覆盖 |
| 5 Conclusions and Future Work | 第 16 节 | 已覆盖 |

## 1. 文献身份

- 标题：EncryptoVision: A dual-modal fusion-based multi-classification model for encrypted traffic recognition。
- 中文题名：EncryptoVision：基于双模态融合的加密流量多分类模型。
- 作者：Zhiyuan Li、Yujie Jin。
- 期刊：Computer Networks，Vol. 270，2025，Article 111499。
- DOI：10.1016/j.comnet.2025.111499。
- 收稿/录用/在线：2025-03-04 / 2025-06-22 / 2025-07-07。
- 本地全文：`paper/10.1016_j.comnet.2025.111499.pdf`。
- 原文代码：`https://github.com/Jsu-JYJ/EncryptoVision`。
- 方法定位：同源流量矩阵的空间/时间双视图闭集模型，不是开放集检测方法。

## 2. 摘要缩译

现有 CNN、LSTM 和 Transformer 已能分类加密流量，但很多方法只使用原始包字节，可能忽略动态流量模式和协议变化。论文提出 EncryptoVision：先把流量转换成三通道图像，用 triplet attention 加强通道、宽度和高度之间的交互，再以多头自注意力提取全局空间特征；同时把同一矩阵展平为字节序列，用 Transformer 提取“时间”特征；最后动态融合空间和时间表示完成细粒度多分类。

模型在 USTC-TFC2016、ISCX-VPN2016、CIC-IOT2022 和 CESNET-QUIC22 上评测，原文报告 F1 分别为 0.979、0.988、0.974 和 0.911。

## 3. 引言缩译

加密应用、VPN、Tor 和 QUIC 增加了网络流量可见性难度。作者认为简单拼接字节会让长包覆盖其他包信息，CNN 的局部 receptive field 又可能丢失全局依赖。受 YaTC、ET-BERT、FS-Net、ATVITSC 和时空双分支模型启发，论文把前三个 packet 组织成三通道图像，同时保留展平序列，分别学习 spatial 和 temporal feature。

论文的主要贡献是三通道表示、triplet attention、双 Transformer 分支和动态加权融合。这里的 dual-modal 是空间/序列两种表示视图，不是两个独立数据源。

## 4. 相关工作缩译

相关工作分为传统机器学习、CNN/RNN 深度模型和 Transformer 模型。传统方法依赖端口、协议、统计特征；CNN/RNN 可从原始字节或序列学习；PERT、ET-BERT、YaTC 和 ATVITSC 则加强了上下文预训练、层次矩阵或视觉 Transformer 表示。

EncryptoVision 与 YaTC 的差异是把前三个包直接作为三个 channel，并把相同数据再展平给序列 Transformer；与 ET-BERT 的差异是没有大规模预训练，而是端到端监督学习。

## 5. PCAP 数据预处理缩译

USTC-TFC2016、ISCX-VPN2016 和 CIC-IOT2022 的 PCAP 先用 Wireshark 过滤 ARP、STUN、DNS、ICMP 等控制/辅助协议，再用 SplitCap 按 TCP/UDP 五元组 session 切流。

每条 flow 取前三个 packet；不足 3 个时补固定零数据。每个 packet 截断或补齐至 256 bytes：

- IP header：20 bytes。
- TCP/UDP header：统一占 20 bytes，UDP 后补 12 个零。
- optional headers：40 bytes。
- payload：176 bytes。

三个 packet 分别作为三个 channel，得到 3 × 16 × 16 矩阵。该表示保留了前三包边界，但把 channel 直接等同于 packet 序号，不能把三 channel 解释为三个模态。

## 6. CESNET-QUIC22 的异构预处理缩译

CESNET-QUIC22 只有 CSV 聚合字段，论文没有恢复原始 packet bytes，而是选择 24 个字段分配到三个 channel：

- Channel 1：源/目的 IP、目的 ASN、源/目的端口、协议、双向包长直方图。
- Channel 2：双向包间隔直方图和 variable-length PPI。
- Channel 3：QUIC version、QUIC SNI、duration、双向 bytes/packets、PPI length/duration/roundtrips、flow end reason 等。

数值归一到 0–255，每个 channel 补齐或截断至 256 values。`QUIC_SNI` 是字符串，论文对它执行 MD5，再压缩为 0–255 的整数。

这与前三个数据集的三 packet raw-byte channel 在语义上完全不同。更严重的是，SNI、IP、ASN 和端口可直接标识应用或采集环境；对 SNI 哈希只改变编码形式，没有消除标签捷径，还会产生碰撞。

## 7. 图像与序列转换缩译

三维矩阵 M 转成 0–255 像素，并执行 min-max 归一化：

> T = (M − min(M)) ÷ (max(M) − min(M))。

同一矩阵再展平成长度 768 的序列：

> B = [b₁, b₂, …, b₇₆₈]。

论文没有说明 max(M) = min(M) 时如何处理。对 CESNET 而言，展平顺序由人工字段分配和大量 zero padding 决定，并非真实 packet 时间序列，因此“temporal modality”的物理含义较弱。

## 8. 空间特征分支缩译

### 8.1 Triplet Attention

输入 T 同时沿 channel、height 和 width 三个方向旋转。每个方向用 max pooling 与 average pooling 拼接：

> ZPool(T) = [MaxPool(T), AvgPool(T)]。

随后通过二维卷积和 sigmoid 生成注意力权重，三个方向输出求平均得到重建图像 T′。该模块增加跨维交互，但不创建新数据模态。

### 8.2 Patch Embedding 与 Transformer

T′ 被切分为 S × S patches，patch 数为：

> z = H × W ÷ S²。

patch 线性映射到 D 维，拼接 class token 并加入 position embedding。多头注意力为：

> headᵢ = softmax(QᵢKᵢᵀ ÷ √dₖ)Vᵢ。

> MSA(Q, K, V) = Concat(head₁, …, headₕ)W(O)。

经过 6 层 Transformer 后提取 class embedding 作为 spatial feature f空间。

## 9. 序列特征与融合缩译

### 9.1 Gaussian Noise

展平序列加入根据序列均值 μ、标准差 σ 生成的 Gaussian noise：

> g(r) = [1 ÷ √(2πσ²)] exp[−(r − μ)² ÷ (2σ²)]。

> B噪声 = B + G。

论文称噪声可模拟传输扰动并降低过拟合，但未给出 noise scale、截断和随机种子，也没有证明这种数值噪声对应真实 packet loss 或 transmission error。

### 9.2 Temporal Transformer

B噪声 加入 class/position embedding 后输入另一套 Transformer，输出 temporal feature f时间。由于输入是相同矩阵的展平副本，它更准确的名称是 sequence-view feature，而不是独立时间观测。

### 9.3 Dynamic Fusion

f空间 与 f时间 先映射到统一的 512-dimensional hidden space，再通过 additive attention 计算权重并加权融合为 f。最终分类为：

> Y = softmax(Wf + β)。

交叉熵为：

> L = −(1 ÷ k) ΣᵢΣⱼ yᵢⱼ log Yⱼ(xᵢ)。

融合权重是分类损失驱动的 attention score，不是模态可靠度、校准置信度或证据冲突量。

## 10. 数据集与任务缩译

| 数据集 | Flow 数 | Packet 数 | 标签数 | 输入来源 |
|---|---:|---:|---:|---|
| USTC-TFC2016 | 9.85K | 97.11K | 20 | PCAP 前三包 |
| ISCX-VPN2016 | 3.12K | 41.11K | 7 | PCAP 前三包 |
| CIC-IOT2022 | 5.40K | 320.71K | 10 | PCAP 前三包 |
| CESNET-QUIC22 | 3.03M | 未给出 | 18 | CSV 24 字段 |

USTC-TFC 含 10 类 benign 应用和 10 类 malware。ISCX-VPN 使用 7 类 VPN traffic。论文把 CIC-IOT2022 描述为含 DDoS、malware 和 data leak 的 10 类 IoT 流量，但该标签语义必须依据官方数据说明重新核对，不能仅凭本文转述认定为 10 个攻击家族。

CESNET-QUIC22 原数据来自一个月的 QUIC backbone traffic。论文只选择 2022-11-27 单日数据，并把 102 个应用和 3 类 background 汇总为 18 类。单日随机验证不能证明 cross-day 泛化。

## 11. 指标、环境和协议缩译

论文报告 Accuracy、Precision、Recall 和 F1：

> Accuracy = (TP + TN) ÷ (TP + TN + FP + FN)。

> Precision = TP ÷ (TP + FP)。

> Recall = TP ÷ (TP + FN)。

> F1 = 2 × Precision × Recall ÷ (Precision + Recall)。

原文称为每个 target class 定义，但没有明确最终 F1 的 macro、micro 或 weighted averaging。

实验环境为 Windows 11、Intel i5-13400、32 GB RAM、RTX 4070、Python 3.9.19 和 PyTorch。模型 input image 3 × 16 × 16，sequence length 768，triplet convolution kernel 7 × 7，hidden fusion dimension 512，Transformer depth 6、16 heads、dropout 0.1。learning rate 0.001，batch size 32，在 accuracy curve 收敛时停止。

论文使用 10-fold cross-validation，但没有说明 fold 是否按 flow fingerprint、capture、device、day 或 application instance 分组，也没有给出 seeds、fold-wise variance 或 confidence interval。

## 12. 超参数实验缩译

patch size S 比较 2、4、8，embedding dimension D 比较 64、128、256。总体选择 S = 4、D = 256。

| 数据集 | 最终 Accuracy | 最终 F1 |
|---|---:|---:|
| USTC-TFC2016 | 98.1% | 0.979 |
| ISCX-VPN2016 | 99.4% | 0.988 |
| CIC-IOT2022 | 99.2% | 0.974 |
| CESNET-QUIC22 | 91.7% | 0.911 |

超参数结果直接写成 test results，论文没有证明 S 和 D 只在 inner validation folds 选择。若先查看全部 10-fold test performance 再固定超参数，会产生 model-selection bias。

## 13. 动态权重分析缩译

USTC-TFC 的 spatial/temporal 权重最终约为 0.50418/0.49582，CESNET 约为 0.499/0.501，均接近等权。ISCX-VPN 和 CIC-IOT2022 的 spatial weight 更高，作者归因于空间特征更重要和 class imbalance。

这些权重只能说明分类器在训练分布上的相对使用程度。权重接近 0.5 不证明两种视图互补，权重偏向某分支也不等同于该分支在 unknown 样本上更可靠。

## 14. 消融实验缩译

| 变体 | USTC F1 | ISCX F1 | CIC-IOT F1 | CESNET F1 |
|---|---:|---:|---:|---:|
| Max-Pool | 0.974 | 0.795 | 0.895 | 0.912 |
| Avg-Pool | 0.977 | 0.957 | 0.932 | 0.868 |
| 去 Gaussian Noise | 0.907 | 0.805 | 0.736 | 0.770 |
| 去 Triplet Attention | 0.848 | 0.470 | 0.729 | 0.886 |
| 去 Temporal Feature Module | 0.763 | 0.930 | 0.884 | 0.748 |
| 去 Spatial Feature Module | 0.963 | 0.408 | 0.761 | 0.871 |
| Full Model | 0.979 | 0.988 | 0.974 | 0.911 |

ISCX 和 CIC-IOT 对 spatial branch/TA 极敏感，USTC 对 temporal branch 更敏感。CESNET full model F1 0.911 还略低于 Max-Pool 的 0.912，说明并非每个组件在所有数据集都稳定增益。

Gaussian noise 带来异常大的提升，但论文没有 noise magnitude 和多 seed 结果，这是复现时必须优先核查的组件。

## 15. 基线对比缩译

| 方法 | USTC F1 | ISCX F1 | CIC-IOT F1 | CESNET F1 |
|---|---:|---:|---:|---:|
| AppScanner | 0.595 | 0.756 | 0.785 | 0.871 |
| 1D-CNN | 0.922 | 0.815 | 0.874 | 0.618 |
| CNN-LSTM | 0.924 | 0.841 | 0.867 | 0.642 |
| FS-Net | 0.864 | 0.873 | 0.839 | 0.809 |
| L2-BiTCN-CNN | 0.929 | 0.820 | 0.876 | 0.745 |
| YaTC | 0.977 | 0.971 | 0.913 | 未报告 |
| ET-BERT | 0.973 | 0.987 | 0.945 | 0.875 |
| ATVITSC | 0.959 | 0.938 | 0.936 | 0.861 |
| EncryptoVision | 0.979 | 0.988 | 0.974 | 0.911 |

相对最强基线，USTC 和 ISCX 只提升 0.002 和 0.001，远小于协议和随机波动可能造成的差异。没有 fold variance 和 paired significance 时，不能宣称这些小差异具有统计意义。

CESNET 输入含 SNI/IP/port，而不同基线是否使用完全相同字段并不清楚，因此 0.911 不能直接证明双模态结构优于其他编码器。

## 16. 结论与未来工作缩译

论文总结三通道图像、triplet attention、sequence Transformer 和动态融合可以改善四个固定数据集的闭集分类。作者承认只测试四个数据集，真实流量类别数量并不预先确定，未来需要提高跨数据集 generalization 和 robustness；同时计划用 reservoir network 与简化 Transformer 降低 48 million 参数和训练成本。

“类别并不预先确定”只在局限中提出，正文没有开放集建模、unknown split 或拒识评价。

# 第二部分：独立技术分析

## A. 一句话结论

EncryptoVision 是可复现的同源双视图融合候选，但不是独立双模态证据模型；其随机 10-fold、身份字段捷径、异构输入语义和未说明 averaging 使论文高分只能作为组件候选，不能进入 CAEOS strict-v4 主表。

## B. 协议审计

- 任务：四个固定标签闭集多分类。
- unknown：无。
- split：10-fold CV，但没有 grouped/capture/day 规则。
- CESNET：只选单日，未做 cross-day；保留 SNI/IP/ASN/port。
- PCAP：前三 packet view，未说明重复 flow 或 capture fingerprint 隔离。
- hyperparameter selection：以 test results 选择 S/D 的风险不明。
- metric averaging：未定义。
- seeds/statistics：缺失。
- protocol grade：`P3-random-CV-identity-shortcut-and-model-selection-unclear`。
- comparability：`C1-组件可比`。

## C. 是否属于真正双模态

只能称为同源双视图。Spatial branch 与 temporal branch 都来自同一个 3 × 16 × 16 矩阵；sequence 是 image flatten 的确定性变换。二者可能使用不同 inductive bias，但没有新增观测信息，也没有独立采集噪声。

CESNET 更接近 heterogeneous feature groups，但把人工字段排列成图像再展平并不会产生视觉/时间两个物理模态。CAEOS 可以采纳双 encoder 和 dynamic fusion，不应把它作为“多模态独立证据”论据。

## D. 身份捷径审计

- `QUIC_SNI` 直接接近应用标签；MD5 后压成单字节仍可被模型记忆。
- IP、ASN、port 与采集环境和应用类别高度相关。
- 单日 10-fold 会让同 host/application fingerprint 同时出现在 train/test。
- 前三包 header 未清除 IP/port，PCAP 数据也可能保留端点捷径。

正式复现必须至少提供 full、no-SNI、no-IP/port/ASN、histogram-only 和 cross-day 五组对照。strict-v4 主结果只允许无身份字段版本。

## E. 数据集标签纠偏

USTC-TFC 是 benign application + malware family 的混合闭集任务；ISCX 是 VPN application；CESNET 是 QUIC application/background；CIC-IOT2022 的标签需回到官方 mapping 核对。四者不能统一解释为“已知恶意攻击家族分类”。

因此论文四个 F1 不能直接填入 CAEOS Known Macro-F1 一列。只有在统一 coarse/fine malicious labels 和相同 benign 定义后，才能构造可比任务。

## F. 三层指标映射

| 层级 | 原文 | CAEOS 要求 | 判定 |
|---|---|---|---|
| 已知识别 | Accuracy、未注明 averaging 的 F1 | Known Macro-F1、BA、per-class Recall、Benign FAR | 部分覆盖 |
| 未知检测 | 无 | AUROC、AUPR-Out、FPR@95TPR、Unknown-F1 | 缺失 |
| 联合开放集 | 无 | OSCR、OpenAUC、Known Acceptance、Unknown Rejection | 缺失 |
| 校准 | 无 | ECE、Brier、NLL | 缺失 |

## G. 95%/5% 安全验收

USTC、ISCX 和 CIC-IOT 的闭集 F1 高于 95%，CESNET 只有 91.1%。但前三项受到任务语义、身份字段、random CV 和指标 averaging 影响，不能直接判定 Known Macro-F1 通过。

论文没有 benign FAR、unknown TPR、FPR@95TPR 或 OSCR，所以 5% 误报和未知拒识均未评估。正确标记是“closed-set candidate only”。

## H. CAEOS 采纳与否决

### 采纳

- 采纳前三包三 channel 作为一种固定字节视图。
- 采纳 spatial/sequence 双 encoder 作为同源多视图基线。
- 采纳 triplet attention、Gaussian noise 和 dynamic fusion 为待验证组件。
- 采纳分数据集展示 fusion weight 的分析形式。

### 有条件采纳

- 输入字段与 masking policy 必须跨数据集统一。
- CV 必须按 flow fingerprint、capture、device 或 day grouped。
- Gaussian noise 必须报告 scale、seed 和真实扰动对照。
- fusion weight 需增加 calibration/conflict supervision 才能解释为可靠度。

### 不采纳

- 不使用 SNI/IP/ASN/port 进入正式主表。
- 不把 RGB channel 当作三个模态。
- 不把 flatten sequence 称为独立 temporal sensor。
- 不过滤所有 DNS/ICMP/STUN 作为恶意检测统一规则。
- 不用没有方差的 0.1–0.2 个百分点优势宣称稳定 SOTA。

## I. CAEOS 可执行实验

1. `E-ENVISION-01`：官方双分支在 strict-v4 grouped split 上重跑。
2. `E-ENVISION-02`：spatial-only、sequence-only、concat、dynamic attention、conflict-aware fusion。
3. `E-ENVISION-03`：identity shortcut 五组消融与 CESNET cross-day 测试。
4. `E-ENVISION-04`：原始前三包、YaTC MFR、ET-BERT BURST 三种字节视图同预算比较。
5. `E-ENVISION-05`：Gaussian noise scale × seeds 稳定性和 packet loss/jitter 真实扰动对照。
6. `E-ENVISION-06`：leave-family-out 下检查两分支 risk AUROC、冲突分布和 OSCR。
7. `E-ENVISION-07`：双分支加入独立统计模态，形成真正 bytes/sequence-statistics 三分支。
8. `E-ENVISION-08`：报告 5 seeds、三层指标、ECE/Brier 和 95%/5% 安全表。

## J. 可引用与不可引用主张

### 可引用

- EncryptoVision 把前三个 packet 构成 3 × 16 × 16 三通道矩阵。
- 模型使用 triplet attention、spatial Transformer、sequence Transformer 和 dynamic fusion。
- 原文固定协议下四数据集 F1 为 0.979、0.988、0.974 和 0.911。
- 消融显示不同数据集对 spatial/sequence branch 的依赖不同。
- 作者承认真实环境类别不预先确定，但没有在本文解决。

### 不可引用

- EncryptoVision 已实现开放集加密恶意流量检测。
- 三个 image channels 是三个独立模态。
- spatial 与 sequence branch 提供独立证据。
- CESNET 的 SNI 哈希已经消除身份泄漏。
- 0.988 相对 0.987 已证明统计显著 SOTA。
- EncryptoVision 已满足 95%/5% 安全门。

## K. 最终审计

- G0 全文缩译门：通过
- G1 全文门：通过，本地正式 Computer Networks PDF 与全文抽取存在
- G2 身份门：通过至 DOI、卷号、文章号和日期，Zotero 待办
- G3 任务门：通过，明确为闭集多分类
- G4 协议门：通过，`P3-random-CV-identity-shortcut-and-model-selection-unclear`
- G5 方法门：通过
- G6 结果门：通过，表 1 至表 6、图 7 至图 10 已核读
- G7 对比门：通过，但仅组件级可比
- G8 局限门：通过
- G9 项目门：通过
- G10 引用门：未通过
- 当前状态：`project_mapped`，不能标记为 complete
