# Evidence-OpenEMTD：证据冲突感知的可信开放集多模态加密恶意流量检测方法

> 论文初稿 v0.2  
> 基于当前目录下综合报告、逐篇详报与全文证据材料撰写。实验数值、作者信息、正式参考文献格式需在复现实验和原文核对后补齐。

## 摘要

随着 TLS、QUIC、VPN 与匿名通信技术的广泛使用，恶意流量检测逐渐从明文载荷分析转向基于包长、方向、时序、协议元数据、字节结构和流间关系的侧信道建模。现有加密恶意流量检测方法在闭集分类场景中已取得较高准确率，但真实园区网络中持续出现未知攻击族、低质量标签、业务漂移和高带宽在线部署约束，导致仅依赖单一模态或闭集判别边界的模型难以可靠落地。为此，本文提出 Evidence-OpenEMTD，一种证据冲突感知的可信开放集多模态加密恶意流量检测框架。该框架从流统计、包序列、TLS/QUIC 元数据、字节或频域表示以及主机-会话流间关系图中提取互补证据，使每个模态输出 Dirichlet evidence、belief 和 uncertainty，并通过证据冲突感知融合估计多模态判断是否充分、是否一致、是否可信。在开放集拒识阶段，本文联合融合不确定性、模态冲突度、类原型距离、能量分数和置信度校准构建未知攻击风险空间，避免未知攻击被高置信误判为已知类别。进一步地，本文引入自监督对比预训练、噪声鲁棒损失、伪标签清洗和未知候选记忆，以提升低标注、噪声标签和跨场景迁移下的稳定性。实验设计将在 USTC-TFC2016、CICIDS2017/CSE-CIC-IDS2018、UNSW-NB15、QUIC、ISCXVPN2016 及园区真实流量上开展闭集识别、攻击族留出开放集、跨数据集迁移、低标注比例、混合噪声标签、模态缺失/污染和在线部署评估。预期结果表明，该框架能够在保持已知类检测性能的同时提高未知攻击召回率，降低误报率并输出可审计的多模态风险证据。

**关键词**：加密恶意流量检测；可信开放集识别；证据深度学习；多模态融合；未知攻击检测；图神经网络；不确定性校准；自监督学习

## 1. 引言

加密通信已成为互联网和园区网络的默认形态。攻击者同样利用 TLS、QUIC、VPN、DoH 等协议隐藏命令控制、恶意下载、扫描探测和数据外传行为，使传统依赖深度包检测或明文特征匹配的安全系统面临明显失效风险。近年来，研究者开始从可观测的侧信道信息中识别加密恶意流量，包括流级统计、包长序列、方向时序、握手元数据、原始字节截断片段、频域特征以及跨流交互关系等。当前资料中 55 篇重点论文显示，该方向已形成多模态融合、开放集未知类检测、图关系建模、半监督或自监督学习、噪声鲁棒训练、环境漂移适应和轻量化部署等技术脉络。

然而，已有工作仍存在三类关键不足。第一，多数方法仍以闭集分类为主，即训练和测试阶段默认类别集合一致。一旦出现未知攻击族或新型加密恶意样本，模型往往会将其强制归入某个已知类别，造成漏报或错误处置。第二，多模态融合多停留在特征拼接、双分支融合或固定权重聚合，缺少对模态可靠性、模态缺失、采样噪声和跨域漂移的显式建模。第三，公开数据集上的高准确率尚不能充分说明真实部署价值，开放集指标、校准指标、吞吐、时延、内存、特征预算和证据解释仍需进入统一实验协议。

围绕上述问题，本文将研究对象定义为“多模态开放集加密恶意流量检测”：给定仅包含部分已知恶意家族和正常流量的训练集，模型需要在测试阶段同时完成已知类识别和未知恶意流量拒识，并在低标注、噪声标签、业务漂移和在线部署约束下保持可用。本文的核心思想是：加密载荷不可见并不意味着证据缺失，包、流、协议、字节和关系图提供了不同粒度的行为线索；但这些证据并非总是可靠，因此检测框架必须同时学习“如何表征流量”“何时相信某个模态”以及“何时拒绝已知类别边界”。

本文拟作出如下贡献：

1. 提出 Evidence-OpenEMTD 多模态可信开放集检测框架，将流统计、包序列、协议元数据、字节/频域表示和流间关系图纳入统一证据建模管线。
2. 设计模态证据意见生成与冲突感知融合机制，使不同模态输出 belief、uncertainty 和 conflict，缓解模态噪声、缺失模态和跨场景漂移造成的错误融合。
3. 构建可信开放集未知攻击拒识模块，联合不确定性、模态冲突度、类原型距离、能量分数和校准风险得到未知风险分数，支持拒识、风险排序和人工复核。
4. 引入自监督对比预训练、伪标签清洗、噪声鲁棒损失、未知候选记忆和漂移监测，使模型适配低质量标签与真实园区网络变化。
5. 建立面向论文复现和工程落地的实验协议，同时报告 Known-F1、Unknown Recall、AUROC、OSCR、FPR@95、ECE、Brier Score、Latency、Throughput、Memory 等指标。

## 2. 相关工作

### 2.1 加密恶意流量检测

加密流量检测早期主要依赖流统计、五元组、包长分布、方向序列和持续时间等手工特征。随着深度学习发展，CNN、RNN、Transformer、ViT、Mamba 等模型被用于从包序列、截断字节和图像化表示中学习高维行为模式。当前资料显示，USTC-TFC2016、CICIDS2017、CSE-CIC-IDS2018、UNSW-NB15、QUIC、ISCXVPN2016、IoT-23、Bot-IoT、ToN-IoT 等数据集被频繁用于该领域评估。已有方法证明了侧信道特征对加密流量识别的有效性，但在未知攻击、标签噪声和跨域迁移下仍需进一步验证。

### 2.2 多模态与多视图融合

多模态融合方法尝试把包级、流级、协议级、字节级和关系级信息组合起来，解决单一特征表达不足的问题。例如，基于 intra-flow 与 inter-flow 的融合模型强调流内序列和流间关系的互补性；EncryptoVision、BPF-DAG、ATVITSC 等工作说明视觉表示、动态属性图、包-流多粒度特征均可提升加密流量分类效果。当前不足在于，多数融合策略假设各模态始终可用且可靠，缺少样本级可信度估计，也很少系统测试缺失模态和模态污染场景。

### 2.3 开放集与未知攻击检测

开放集检测关注训练集中未出现类别在测试阶段的识别和拒绝。OpenMax 早期指出闭集 softmax 会把未知样本强制归入已知类，后续 OOD 方法进一步使用 Mahalanobis 距离、能量分数、置信度校准和风险覆盖曲线衡量模型是否过度自信。当前资料中的 Open set identification、HyperEye、Fine-Grained Detection、End-to-End Open-Set Semi-Supervised Learning、Gaussian Prototype-Aided VAE、ECNet、RoNeTC、TrustWI、FOSS、M3S-UPD 和 New Class Detection 等论文均与未知加密恶意流量检测直接相关。这类工作提示，未知类不应被建模为普通闭集类别，而应通过原型距离、重构误差、能量分数、置信度校准或不确定性估计在已知类边界之外构建风险空间。最新可信开放集工作进一步说明，模型不只要输出“是否 unknown”，还应解释证据是否充分、不同视图是否冲突、风险分数是否校准。问题在于，各论文的数据集划分、未知类设置、开放集指标和真实部署解释仍不统一，模态冲突与低质量标签下的可信拒识仍有进一步研究空间。

### 2.4 鲁棒学习、图关系与部署约束

真实网络中的训练标签通常来自告警、规则、沙箱或弱标注系统，不可避免存在噪声、污染和类别混合。Fine-Grained Detection from Mixed Noisy Labels、MTDecipher、FG-SAT、Robust Detection via Contrastive Learning、GETRF 等工作显示，对比学习、图结构约束、低质量标签鲁棒损失和漂移适应是近年热点。同时，HyperEye、AutoML4ETC、SRViT、TrafficAudio 和硬件感知搜索相关工作提醒，安全模型不能只报告准确率，还需评估吞吐、时延、内存、参数量和特征提取开销。本文将这些线索整合到统一的研究方案中。

## 3. 问题定义

设训练集为

$$
\mathcal{D}_{train} = \{(x_i, y_i)\}_{i=1}^{N}, \quad y_i \in \mathcal{Y}_K
$$

其中 \(\mathcal{Y}_K\) 表示训练阶段可见的已知类别集合，包括正常流量和若干已知恶意家族。测试集包含已知类样本和未知类样本：

$$
y_j \in \mathcal{Y}_K \cup \mathcal{Y}_U, \quad \mathcal{Y}_K \cap \mathcal{Y}_U = \emptyset
$$

开放集加密恶意流量检测目标是学习一个函数 \(f(x)\)，使其在输入加密流量样本 \(x\) 时输出：

1. 已知类预测 \(\hat{y} \in \mathcal{Y}_K\)；
2. 未知风险分数 \(s_{unk}(x)\)；
3. 若 \(s_{unk}(x) > \tau\)，则拒识为未知攻击或未知流量；
4. 可解释证据 \(e(x)\)，包括关键模态贡献、相似原型、邻域关系或异常原因。

本文关注如下研究问题：

**RQ1：** 多粒度侧信道模态能否比单一模态更稳定地刻画加密恶意流量行为？

**RQ2：** 样本级模态可靠性门控能否降低模态噪声、缺失和漂移带来的错误融合？

**RQ3：** 原型距离、能量分数和不确定性校准的联合风险分数能否提升未知攻击召回率并控制误报？

**RQ4：** 自监督、噪声鲁棒和漂移监测机制能否在低标注与跨场景条件下保持检测性能？

**RQ5：** 二阶段轻量部署能否在高带宽园区网络中兼顾检测效果和在线时延？

## 4. 方法

### 4.1 框架总览

Evidence-OpenEMTD 由六个模块组成：

1. 多模态流量解析模块：从 pcap 或流记录中生成包序列、统计特征、协议元数据、字节/频域特征和关系图。
2. 模态编码模块：为不同模态配置轻量编码器，并输出模态表征。
3. 模态证据意见生成模块：为每个模态输出 evidence、belief 和 uncertainty。
4. 证据冲突感知融合模块：估计模态间冲突，生成融合意见和融合表征。
5. 可信开放集拒识模块：基于不确定性、冲突度、类原型、能量分数和校准风险输出未知风险。
6. 鲁棒训练与在线部署模块：通过自监督预训练、噪声鲁棒学习、未知候选记忆、漂移监测和二阶段推理提升真实场景可用性。

### 4.2 多模态输入构造

对每条会话或流量样本 \(x\)，构造如下模态：

**流统计模态 \(x^{stat}\)：** 包括持续时间、上下行包数、字节数、包长统计量、到达间隔统计量、方向切换次数、突发长度等。

**包序列模态 \(x^{seq}\)：** 取前 \(L\) 个包的长度、方向、时间间隔和 TCP/UDP 标志位，形成长度受限的时序输入。该模态适合早期检测。

**协议元数据模态 \(x^{proto}\)：** 包括 TLS/QUIC 握手字段、版本、扩展数量、SNI 可用性、JA3/JA4 类指纹、证书统计、QUIC 传输参数等。涉及隐私字段时仅保留不可逆摘要或统计量。

**字节/频域模态 \(x^{byte}\)：** 对加密载荷不可解密的前提下，仅使用截断字节分布、方向化字节片段、包长序列频域变换或流量图像表示，不还原用户内容。

**关系图模态 \(G=(V,E)\)：** 在滑动时间窗口内构建主机、会话、域名指纹、端口、协议或流节点。边可表示同源主机、同目的端、相似包序列、时间邻近、共享证书或通信模式相似性。图模态用于捕获隐蔽恶意流量的群体行为。

### 4.3 模态编码器

每个模态由独立编码器映射到统一维度：

$$
h_m = E_m(x^{m}), \quad m \in \{stat, seq, proto, byte, graph\}
$$

流统计和协议元数据可采用 MLP 或 TabTransformer；包序列可采用 1D-CNN、GRU 或轻量 Transformer；字节/频域模态可采用 CNN 或 ViT-lite；关系图模态可采用 GraphSAGE、GAT 或动态图编码器。为控制部署成本，在线阶段优先启用 \(stat\)、\(seq\)、\(proto\) 三类低成本模态，离线深度分析或高风险样本再启用 \(byte\) 与 \(graph\) 模态。

### 4.4 模态证据意见生成与冲突感知融合

对每个模态，先估计其可靠性分数：

$$
r_m = \sigma(W_r [h_m; q_m; c_m])
$$

其中 \(q_m\) 表示模态质量特征，例如缺失率、包数是否不足、握手字段是否完整、图邻居数量是否过少；\(c_m\) 表示模态置信特征，例如预测熵、重构误差或与训练分布的距离。融合权重为：

$$
\alpha_m = \frac{\exp(r_m / T)}{\sum_{k}\exp(r_k / T)}
$$

最终融合表征为：

$$
z = \sum_m \alpha_m W_m h_m
$$

该机制使模型能够在 QUIC 元数据缺失、短流样本包数不足、图邻居稀疏或字节模态受噪声影响时降低对应模态权重。训练时随机进行模态 dropout，增强缺失模态鲁棒性。

进一步地，本文将每个模态的分类输出从 softmax 概率升级为 Dirichlet evidence。对模态 \(m\)，模型输出非负证据：

$$
e_m = \mathrm{softplus}(W_e h_m), \quad \alpha_m = e_m + 1
$$

设类别数为 \(K\)，Dirichlet strength 为 \(S_m=\sum_k \alpha_{m,k}\)，则该模态对类别 \(k\) 的信念质量和整体不确定性为：

$$
b_{m,k} = \frac{e_{m,k}}{S_m}, \quad u_m = \frac{K}{S_m}
$$

当某个模态缺少有效证据时，\(S_m\) 较小，\(u_m\) 较高；当不同模态支持不同类别时，模型不应简单平均，而应显式计算模态冲突。本文定义两模态冲突为：

$$
C_{i,j} = \sum_{p \neq q} b_{i,p} b_{j,q}
$$

综合冲突度为全部模态对冲突均值：

$$
C(x) = \frac{2}{M(M-1)}\sum_{i<j} C_{i,j}
$$

最终融合可采用 Dempster-Shafer 证据融合或其简化形式，得到融合 belief、融合 uncertainty 和融合表征。这样，模型不仅知道“哪个类别概率最高”，还知道“证据是否充分”和“模态之间是否互相矛盾”。

### 4.5 开放集未知攻击拒识

对每个已知类别 \(k\)，维护类原型：

$$
\mu_k = \frac{1}{|\mathcal{D}_k|}\sum_{i:y_i=k} z_i
$$

样本到最近已知类原型的距离为：

$$
d_{proto}(x)=\min_k ||z-\mu_k||_2
$$

分类头输出 logits \(g(x)\)，能量分数定义为：

$$
E(x) = -T \log \sum_k \exp(g_k(x)/T)
$$

不确定性可由预测熵、深度集成、MC Dropout 或证据学习得到：

$$
u(x) = -\sum_k p_k(x)\log p_k(x)
$$

综合未知风险分数为：

$$
s_{unk}(x)=\lambda_1 \tilde{d}_{proto}(x) + \lambda_2 \tilde{E}(x) + \lambda_3 \tilde{u}(x) + \lambda_4 \tilde{C}(x)
$$

其中 \(\tilde{\cdot}\) 表示在验证集上归一化。阈值 \(\tau\) 根据验证集控制 FPR@95 或目标误报率进行选择。若 \(s_{unk}(x)>\tau\)，模型输出 Unknown；否则输出已知类别 \(\arg\max_k p_k(x)\)。

### 4.6 鲁棒训练目标

总损失由五部分组成：

$$
\mathcal{L} = \mathcal{L}_{ce} + \beta_1 \mathcal{L}_{con} + \beta_2 \mathcal{L}_{proto}
+ \beta_3 \mathcal{L}_{cal} + \beta_4 \mathcal{L}_{noise}
$$

其中 \(\mathcal{L}_{ce}\) 为已知类监督分类损失；\(\mathcal{L}_{con}\) 为跨增强视图或跨模态对比损失；\(\mathcal{L}_{proto}\) 拉近同类样本与类原型距离并推开异类原型；\(\mathcal{L}_{cal}\) 用于温度缩放或置信度校准；\(\mathcal{L}_{noise}\) 可采用广义交叉熵、对称交叉熵或样本重加权，以降低噪声标签影响。

半监督场景下，未标注样本先经过弱增强和强增强一致性训练。对高置信且低未知风险样本生成伪标签，对高未知风险、高不确定性或高模态冲突样本进入候选未知池，不直接并入已知类别训练。漂移监测模块跟踪原型移动距离、模态可靠性分布、证据不确定性分布和特征分布偏移，当漂移超过阈值时触发阈值重校准或增量复核。

### 4.7 二阶段在线部署

为适配园区高带宽场景，本文采用二阶段检测：

**第一阶段：轻量在线筛选。** 使用流统计、包序列前缀和协议元数据快速输出已知类概率与未知风险。该阶段关注低时延和高吞吐。

**第二阶段：深度多模态复核。** 对第一阶段判为高风险、低置信或疑似未知的样本，补充字节/频域和关系图模态，进行更精细的开放集检测与证据生成。

大模型或规则化解释模块不直接替代检测器，仅用于对高风险事件生成证据链，例如关键模态贡献、相似历史样本、相关主机群、协议异常点和处置建议。

## 5. 实验设计

### 5.1 数据集

拟采用如下数据集和场景：

| 数据集/场景 | 用途 | 备注 |
|---|---|---|
| USTC-TFC2016 / USTC | 恶意家族识别、开放集留出 | 当前资料中高频出现 |
| CICIDS2017 / CSE-CIC-IDS2018 | 入侵检测、跨数据集迁移 | 可构造攻击族留出 |
| UNSW-NB15 | 泛化与噪声鲁棒评估 | 可用于跨域验证 |
| QUIC | 现代加密协议检测 | 适合协议元数据与轻量部署评估 |
| ISCXVPN2016 / VPN-nonVPN | 加密应用和 VPN 流量表征 | 可作为预训练或闭集 baseline |
| 园区真实流量 | 真实部署验证 | 需脱敏、弱标注与人工抽样复核 |

### 5.2 开放集协议

本文设计三类开放集划分：

1. **攻击族留出：** 每次从恶意家族中留出若干类作为未知类，其余类别作为已知类训练。
2. **跨数据集未知：** 在一个数据集训练，在另一个数据集的恶意类型上测试未知拒识能力。
3. **时间漂移未知：** 按时间划分训练和测试，将后期出现的新业务或新攻击作为未知分布。

为保证可复现，每组实验记录随机种子、已知/未知类别列表、训练/验证/测试比例、标签比例和阈值选择策略。

### 5.3 对比方法

对比方法分为五组：

1. 闭集分类基线：Random Forest、MLP、CNN、RNN、Transformer。
2. 单模态基线：仅流统计、仅包序列、仅协议元数据、仅字节/频域、仅关系图。
3. 多模态融合基线：简单拼接、注意力融合、双分支融合、固定权重融合。
4. 开放集基线：最大 softmax 置信度、OpenMax、Mahalanobis 距离、能量分数、原型距离、重构误差类方法。
5. 可信开放集与新类检测基线：RoNeTC、TrustWI、FOSS、M3S-UPD、New Class Detection、校准 softmax、evidential classifier。
6. 近期加密恶意流量相关工作复现：Open set identification、HyperEye、Fine-Grained Detection、Gaussian Prototype-Aided VAE、ECNet、BPF-DAG、MTDecipher、FG-SAT 等。

### 5.4 评价指标

闭集识别指标包括 Accuracy、Precision、Recall、Macro-F1、Known-F1。开放集指标包括 Unknown Recall、AUROC、AUPR、OSCR、FPR@95TPR、Detection Rate、False Alarm Rate。校准指标包括 ECE、Brier Score、NLL、可靠性曲线和 risk-coverage 曲线。可信性指标包括模态缺失/污染下 uncertainty 增幅、模态冲突度变化、unknown risk 排序质量和证据包可追溯性。鲁棒性指标包括不同标签噪声比例、不同标注比例、不同漂移强度下的性能退化曲线。部署指标包括 Latency、Throughput、Memory、参数量、FLOPs 和特征提取时间。

### 5.5 消融实验

拟开展如下消融：

1. 去除某一模态，评估模态贡献。
2. 固定融合权重替代证据冲突感知融合，验证 evidence / uncertainty / conflict 的作用。
3. 去除原型距离、能量分数、不确定性或冲突度分量，验证开放集风险分数组成。
4. 去除自监督预训练、伪标签清洗或噪声鲁棒损失，评估低标注和噪声条件贡献。
5. 比较无图、静态图、动态图和不同边定义，评估关系图对未知攻击和漂移场景的贡献。
6. 比较单阶段推理与二阶段推理，评估检测效果与时延开销。

## 6. 预期结果与分析模板

实验完成后，建议按以下表格组织结果。

### 6.1 主结果

| 方法 | Known-F1 | Unknown Recall | AUROC | OSCR | FPR@95 | ECE | Latency |
|---|---:|---:|---:|---:|---:|---:|---:|
| 闭集 Transformer | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 |
| 简单多模态拼接 | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 |
| 开放集单模态基线 | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 |
| MM-OpenEMTD | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 | 待填 |

预期分析重点不是单纯强调准确率提升，而是回答：未知类召回是否提高，误报是否可控，置信度是否更可靠，部署时延是否满足在线约束。

### 6.2 模态消融

| 模态组合 | Known-F1 | Unknown Recall | AUROC | ECE | 说明 |
|---|---:|---:|---:|---:|---|
| 统计 | 待填 | 待填 | 待填 | 待填 | 低成本基础模态 |
| 统计 + 序列 | 待填 | 待填 | 待填 | 待填 | 验证早期时序贡献 |
| 统计 + 序列 + 协议 | 待填 | 待填 | 待填 | 待填 | 在线主链路 |
| 全模态无门控 | 待填 | 待填 | 待填 | 待填 | 融合基线 |
| 全模态 + 可靠性门控 | 待填 | 待填 | 待填 | 待填 | 本文方法 |

### 6.3 鲁棒性与漂移实验

| 场景 | 方法 | Known-F1 | Unknown Recall | FPR@95 | 性能下降 |
|---|---|---:|---:|---:|---:|
| 20% 标签噪声 | 基线 | 待填 | 待填 | 待填 | 待填 |
| 20% 标签噪声 | MM-OpenEMTD | 待填 | 待填 | 待填 | 待填 |
| 跨数据集迁移 | 基线 | 待填 | 待填 | 待填 | 待填 |
| 跨数据集迁移 | MM-OpenEMTD | 待填 | 待填 | 待填 | 待填 |

## 7. 讨论

本文方案的核心价值在于将“开放集拒识”从附加评估项提升为模型设计目标。对加密恶意流量而言，未知攻击并非少数异常情况，而是长期存在的真实威胁。若模型不能表达“我不知道”，高闭集准确率反而可能掩盖严重风险。

多模态建模的收益也不应被简单理解为特征越多越好。不同模态在不同场景下可靠性差异明显：短流样本中包序列不足，QUIC 场景中部分握手信息不可见，真实园区图关系受 NAT、代理和采样策略影响，字节/图像模态又可能带来较高计算开销。因此，样本级模态可靠性建模是多模态方法面向真实部署的关键环节。

此外，本文将大模型定位为证据解释和运维辅助，而不是直接分类器。原因是高带宽检测主链路需要稳定、可控、低时延和可审计，小模型更适合承担实时检测；大模型适合在高风险事件上汇总多模态证据、生成分析报告和辅助处置。

## 8. 局限性

本初稿仍有三点需要后续工作补齐。第一，当前方法公式和模块设计来自现有资料归纳，尚需结合具体数据格式完成工程实现。第二，园区真实流量需要脱敏、合规审批和人工抽样复核，弱标注质量会影响开放集评估。第三，参考文献仍需回到 PDF 核对作者、发表 venue、卷期页码、DOI 和具体实验细节，避免仅凭二级分析材料引用。

## 9. 结论

本文提出 Evidence-OpenEMTD，一种面向多模态开放集加密恶意流量检测的研究方案与论文初稿。该方法围绕加密载荷不可见、未知攻击持续出现、多模态证据可靠性不一致、低质量标签和在线部署约束等核心问题，构建多粒度侧信道表示、模态证据意见生成、证据冲突感知融合、原型/能量/不确定性/冲突度联合拒识以及鲁棒训练机制。后续工作将完成统一数据处理管线、复现关键 baseline、开展开放集与鲁棒性实验，并在园区真实流量上验证在线检测能力。

## 附录 A：研究工作开展路线

### A.1 第一阶段：统一数据管线与复现闭环

1. 整理 USTC、CICIDS2017/CICIDS2018、UNSW-NB15、QUIC、ISCXVPN2016 等数据集，统一 pcap 到 flow/session 的解析格式。
2. 实现五类候选模态：统计、序列、协议、字节/频域、关系图。
3. 复现最小 baseline：统计特征 MLP、包序列 CNN/Transformer、简单多模态拼接。
4. 建立统一评价脚本，支持闭集和攻击族留出开放集评估。

### A.2 第二阶段：开放集主模型实现

1. 实现模态编码器、证据意见生成和冲突感知融合。
2. 实现类原型、能量分数、不确定性分数、冲突度和阈值选择。
3. 加入模态 dropout 和温度缩放校准。
4. 完成主结果、开放集指标和校准曲线。

### A.3 第三阶段：鲁棒性与真实部署增强

1. 加入自监督对比预训练和低标注比例实验。
2. 注入标签噪声和样本污染，评估噪声鲁棒损失。
3. 构建跨数据集和跨时间漂移实验，测试漂移监测与重校准。
4. 设计二阶段在线推理，报告吞吐、时延、内存和特征预算。

### A.4 第四阶段：论文完善

1. 回到 PDF 核对关键公式、实验设置和参考文献信息。
2. 将实验结果填入第 6 节表格，补充显著性检验和误差条。
3. 绘制方法框架图、开放集协议图、可靠性门控可视化和 ROC/OSCR 曲线。
4. 完成摘要、贡献、相关工作和讨论的压缩润色，形成投稿版本。

## 参考文献初表

> 以下条目基于当前资料中的论文题名和年份整理，正式投稿前需补齐作者、期刊/会议、卷期页码与 DOI。

[1] Semi-Supervised Encrypted Malicious Traffic Detection Based on Multimodal Traffic Characteristics, 2024.

[2] Combine intra- and inter-flow: A multimodal encrypted traffic classification model driven by diverse features, 2024.

[3] Open set identification of malicious encrypted traffic based on multi-feature fusion, 2024.

[4] EncryptoVision: A dual-modal fusion-based multi-classification model for encrypted traffic, 2025.

[5] HyperEye: A Lightweight Features Fusion Model for Unknown Encrypted Malware Traffic Detection, 2025.

[6] Fine-Grained Detection and Analysis of Unknown Encrypted Malicious Traffic From Mixed Noisy Labels, 2026.

[7] End-to-End Open-Set Semi-Supervised Learning for Fine-Grained Encrypted Traffic Classification, 2026.

[8] Detection of Unknown Attacks Through Encrypted Traffic: A Gaussian Prototype-Aided Variational Autoencoder Framework, 2025.

[9] ECNet: Robust Malicious Network Traffic Detection With Multi-View Feature and Confidence Mechanism, 2024.

[10] BPF-DAG: Byte-Packet-Flow Features Fusion via Dynamic Attributed Graph for Reliable Encrypted Traffic Classification, 2026.

[11] MT-DEGCL: Multi-Task Encrypted Traffic Classification With Dual Embedding and Graph Contrastive Learning, 2026.

[12] MTDecipher: robust encrypted malicious traffic detection via multi-task graph neural networks, 2026.

[13] FG-SAT: Efficient Flow Graph for Encrypted Traffic Classification Under Environment Shifts, 2025.

[14] Robust Detection of Malicious Encrypted Traffic via Contrastive Learning, 2026.

[15] Learning Flow Semantics for Encrypted Traffic Analysis: A Contrastive Pre-training Approach, 2026.

[16] GETRF: A General Framework for Encrypted Traffic Identification With Robust Representation Based on Datagram Structure, 2024.

[17] CL-ViME: Contrastive Learning and Vision Mixture of Experts for Encrypted Traffic Classification, 2026.

[18] Adapting Large Language Models for Encrypted Traffic Analysis Services: An Efficient Realization With Mixture of LoRA Experts, 2026.

[19] Reliable Open-Set Network Traffic Classification, 2025.

[20] Shattering Weak Facades: Trustworthy Detection of Encrypted Malicious Traffic via Uncertainty-Aware Fusion, 2026.

[21] Towards Open Set Deep Networks, 2016.

[22] On Calibration of Modern Neural Networks, 2017.

[23] Evidential Deep Learning to Quantify Classification Uncertainty, 2018.

[24] A Simple Unified Framework for Detecting Out-of-Distribution Samples and Adversarial Attacks, 2018.

[25] Energy-Based Out-of-Distribution Detection, 2020.

[26] FOSS: Towards Fine-Grained Unknown Class Detection Against the Open-Set Attack Spectrum With Variable Legitimate Traffic, 2024.

[27] M3S-UPD: Efficient Multi-Stage Self-Supervised Learning for Fine-Grained Encrypted Traffic Classification With Unknown Pattern Discovery, 2025.

[28] New Class Detection in Network Traffic Classification Using Confidence Information Embedded Cascade Structure, 2025.
