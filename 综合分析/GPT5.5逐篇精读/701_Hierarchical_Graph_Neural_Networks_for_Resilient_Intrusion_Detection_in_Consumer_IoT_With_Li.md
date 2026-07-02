# [701] Hierarchical Graph Neural Networks for Resilient Intrusion Detection in Consumer IoT With Limited Labeled Data

## 1. 基本信息

- 题名：Hierarchical Graph Neural Networks for Resilient Intrusion Detection in Consumer IoT With Limited Labeled Data
- 作者：Guolong Zheng 等
- 来源：IEEE Transactions on Consumer Electronics
- DOI：10.1109/TCE.2025.3604228
- 发表状态：2025 年 8 月 29 日在线发表，正文页眉为 Vol. 72, No. 1, February 2026
- 主题归类：IoT 入侵检测、少标签学习、图神经网络、对抗鲁棒检测
- 代码：`source\HierGNN`，核心实现集中在 `hiergnn.py`

## 2. 中文翻译与核心摘要

这篇论文可以译为：**面向少量标注数据消费级物联网弹性入侵检测的层次化图神经网络**。

论文的核心主张是：消费级 IoT 网络中设备异构、补丁滞后、弱口令和协议不安全等问题使攻击面快速扩大，而真实攻击样本又难以持续标注；同时，深度学习 NIDS 容易被细微扰动绕过。因此，检测模型不能只追求常规准确率，还要在少标签和对抗扰动下保持稳定。

作者提出 HierGNN：先在**包级别**用动态特征过滤和 GAT 抽取细粒度包表示，再在**流级别**用自注意力和双向 GRU 建模时序依赖，最后通过自适应注意力和论文所称的 MAML 泛化模块完成分类。实验声称在 CICIDS2017、ToN-IoT、MedBIoT 上，极少标签下仍能保持较高 F1 和准确率，并在 FGSM、PGD 攻击下比传统 ML 和已有 GNN 基线更稳。

## 3. 论文解决的具体问题

论文瞄准的是 IoT NIDS 的三个叠加难点：

1. **少标签问题**：新型攻击、零日攻击和跨场景 IoT 流量很难获得大量可靠标签，普通监督模型在 0.1%、数百条样本这种条件下容易退化。
2. **对抗规避问题**：攻击者可以对网络特征做小幅扰动，使深度模型误判为正常流量；论文把鲁棒性提升到和准确率同等重要的位置。
3. **单粒度建模不足**：只看包容易丢失长程行为模式，只看流又可能忽略握手、初始交互、标志位组合等细节。作者认为攻击行为天然有“包内特征组合 -> 包序列 -> 流行为”的层次结构。

## 4. 创新点深度提炼

第一，论文把网络流表示成**包图序列**，而不是一个静态流图。每个流最多取前 20 个包；每个包构造成一个 3 节点全连接小图，包的 10 维头部特征复制到节点上，再送入 GAT 得到包图嵌入。

第二，包级模块引入了**硬过滤 + 软门控**。重要性 MLP 产生特征得分，通过分位数阈值保留高分特征；门控 MLP 再对保留特征做连续重加权。这个设计的防御直觉是缩小输入攻击面，让被扰动但不关键的特征难以进入后续时序模型。

第三，流级模块采用**多头自注意力 + BiGRU**。自注意力负责判断哪些包时间步更重要，BiGRU 建模前后文，最后对有效包表示求均值并经 MLP 聚合为流向量。相比全 Transformer，作者强调 GRU 对短包序列更适合边缘部署。

第四，论文试图把**少样本泛化和对抗鲁棒性合并**：泛化模块先用自适应注意力重加权流向量，再通过 MAML 思路学习可快速适配新任务的初始化。不过本地代码中没有看到 MAML 内外循环实现，这一点需要作为复现风险单独看待。

## 5. 科学问题与研究假设

科学问题可以概括为：**能否通过层次化图表示，把有限标签中的包级局部证据和流级时序证据充分利用起来，从而同时提升 IoT 入侵检测的数据效率和对抗鲁棒性？**

论文隐含了几条研究假设：

- 攻击流量的可判别信息集中在少数包头特征及其组合中，动态过滤能去噪并压制对抗扰动。
- 流的前若干个包已经包含足够强的入侵意图信号，因此最多 20 个包能在性能和开销之间取得平衡。
- 层次化抽象比单层 GNN、传统 ML、孤立流特征建模更适合少标签场景。
- 对包级扰动先做过滤，可以防止污染传播到流级时序表示。
- 通过元学习初始化，模型可用少量新场景标签快速适配未知攻击。

## 6. 科学方法与技术路线

技术路线是：`PCAP/CSV -> 双向流切分 -> 包头特征 -> 包图序列 -> Packet-GAT -> Temporal-GRU -> adaptive attention/classifier`。

数据侧，论文只使用包头信息，不做 DPI，也不依赖预计算高级流特征。CSV 主要用于按五元组、时间戳关联标签。流按规范化双向五元组聚合，300 秒无活动超时切分，最多取 20 个包，长流继续拆分。

模型侧，包级 GAT 之前先做动态特征过滤；GAT 两层后做全局均值池化得到每个包图的 embedding。流级模块对包 embedding 序列做 padding mask、自注意力、packed BiGRU 和聚合。最终分类模块先生成 softmax 注意力掩码，对流向量做逐维重权，再输出二分类概率。

解释性方面，论文认为包级 importance score 能解释关键特征，流级 attention 能指出关键包时间步。但代码没有把这些权重作为可分析结果输出。

## 7. 实验设计与实验步骤

可复核流程如下：

1. **数据**：CICIDS2017、MedBIoT、ToN-IoT。三者分别覆盖通用企业/校园攻击流量、IoT botnet、中等规模 IoT/工业 4.0 测试床。
2. **预处理**：从 PCAP 取包头特征；CSV 只用于标签和流归属；双向五元组聚流；300 秒 inactivity timeout；每段流最多 20 包；每包 10 维特征；训练集上拟合 StandardScaler，再应用到验证/测试。
3. **模型/基线**：HierGNN 对比 DT、RF、SVM、KNN、XGBoost，以及 E-GraphSAGE、Anomal-E。FeCoGraph 因作者未找到公开代码而未比较。
4. **训练设置**：Python 3.8.8、PyTorch 1.13.0、PyG 2.3.0、DGL 1.2，硬件为 Xeon Silver 4310 和 2 张 RTX 4090。
5. **少标签比例实验**：按 0.1%、0.5%、1%、10% 等比例采样训练，剩余作为测试，用 Accuracy、Precision、Recall、F1 衡量。
6. **极端少样本实验**：固定采样 300、500、700、1000 条记录训练，检验类别不均衡和样本不足下的稳定性。
7. **对抗鲁棒实验**：在 1000 条标签训练条件下，对模型施加 FGSM 和 PGD 白盒规避攻击，比较攻击前后性能下降。
8. **消融/敏感性**：去掉 Packet-GAT，用均值聚合替代；去掉 Flow-TGN，用简单 MLP 替代；分别在正常和 PGD 条件下比较。
9. **结果核查**：重点核查 F1 而不仅是 Accuracy，因为 CICIDS2017 等数据存在明显类别不均衡；同时核查对抗攻击后性能下降幅度，而不是只看干净测试集。

## 8. 关键结果、结论与证据

论文最强结论是：HierGNN 在少标签、极少标签和对抗攻击下都显著优于基线。

在百分比采样实验中，MedBIoT 上 0.1% 训练数据时 HierGNN 准确率为 98.15%，10% 时为 99.15%；ToN-IoT 上 0.1% 时准确率 95.40%，10% 时 96.10%；CICIDS2017 上 0.1% 时准确率 95.25%，10% 时 98.25%。这说明其优势不是只在单一数据集出现。

在固定样本实验中，300 条样本下 HierGNN 仍能在 MedBIoT 上取得约 97.27% F1，在 ToN-IoT 上约 94.10% F1，在 CICIDS2017 上约 94.05% F1；而 KNN、E-GraphSAGE 等在 CICIDS2017 上退化明显。

对抗实验更能支撑作者的鲁棒性叙事：MedBIoT 上 XGBoost 的 F1 从 92.45% 掉到 FGSM 下 71.15%、PGD 下 67.15%；HierGNN 从 97.92% 只降到 97.17% 和 96.36%。CICIDS2017 上 HierGNN 的 F1 从 95.00% 降到 FGSM 94.20%、PGD 93.40%，降幅远小于基线。

消融表明 Packet-GAT 是鲁棒性的关键来源。MedBIoT 1000 条样本下，去掉 Packet-GAT 后 PGD 下 F1 只有 73.44%，比完整模型低 22.92 个百分点；去掉 Flow-TGN 也会下降，但作者认为其主要影响是长程时序上下文，而非第一道抗扰动过滤。

## 9. 局限性与待解决问题

第一，论文使用的是静态公开数据集，虽然覆盖面较广，但没有真正验证生产 IoT 网络中的 concept drift、设备新增、协议变化和攻击策略迁移。

第二，正文对 10 维包头特征的具体字段没有完整展开，复现时必须明确特征列表、方向归一化、端口/IP 编码、时间间隔处理和标准化保存方式。

第三，论文声称使用 MAML，但本地代码没有实现 MAML 的 support/query 内外循环；如果代码就是公开仓库主实现，则论文方法和代码之间存在重要缺口。

第四，3 节点包图把同一个包特征复制到多个节点，这个设计的图语义并不充分。若节点初始特征完全相同，全连接 GAT 的“关系学习”可能退化为一种带注意力的非线性变换，而不是真正的包内特征交互图。

第五，FGSM/PGD 是常见白盒攻击，但网络流量特征有离散性和协议约束。扰动后的样本是否仍对应合法可发送流量，正文没有充分讨论。

第六，摘要与部分结果表述略有张力：摘要称 0.1% 标签下 accuracy 0.96+，但正文对 ToN-IoT 和 CICIDS2017 的 0.1% 准确率描述分别为 95.40% 和 95.25%。综述引用时应以表格具体数值为准。

正文包标记为未截断，因此本次理解不需要额外假设缺页；但复现相关细节仍建议回到 PDF 表格和代码 commit 核查。

## 10. 与本项目的关系

这篇论文与“异常检测/入侵检测”项目强相关，尤其适合放在**少标签 IoT/边缘网络异常检测**和**图学习鲁棒检测**两条综述线中。

可直接借鉴的是三层思路：包头级动态过滤、流级时序聚合、少标签评估协议。对于工业互联网、车联网或边缘网关场景，这种结构可以作为强基线：前端避免 DPI，较符合隐私和部署约束；后端通过包序列捕捉慢速扫描、botnet 控制、DDoS 初始行为等模式。

但若用于本项目复现或扩展，不能只跑仓库默认脚本。必须先补齐 PCAP 到 `.pt` 的预处理，明确特征字段，并补实现 ToN-IoT、MAML、对抗攻击和消融开关，才能支撑论文级比较。

## 11. 代码对照分析

代码包很小，顶层只有 `README.md`、`hiergnn.py`、`requirements.txt`。README 明确说明模型期望读取预处理好的 `.pt` 文件，而不是直接处理 PCAP；每个样本应包含 `packet_graphs`、`flow_features`、`labels`、`flow_metadata`。

源码对应关系如下：

- 数据读取：`PreprocessedIoTDataset` 读取 `.pt`，要求四个 key；`collate_fn_for_hier_gnn` 把一个 batch 内所有 packet graph 合并为 PyG `Batch`。
- 数据路径：`load_and_combine_data` 支持 `data/cicids2017/pt` 和 `data/medbiot/pt`；命令行 choices 只有 `cicids17`、`medbiot`，没有 ToN-IoT。
- 包级模型：`DynamicFeatureFilter` 对应论文中的 importance score、quantile mask 和 gate；`PacketLevelGAT` 对应两层 GATConv 和 mean pooling。
- 流级模型：`TemporalGNN` 对应 MultiheadAttention、BiGRU、temporal fusion 和 flow aggregation。
- 分类模块：`GeneralizationModule` 实现了 adaptive attention 和 MLP classifier，但没有 MAML。
- 训练评估：`HierGNNTrainer` 实现训练、验证、weighted precision/recall/F1、AUC、混淆矩阵；主函数默认 batch size 128、hidden dim 128、GAT heads 8、GRU layers 3、dropout 0.2、epoch 20、lr 0.0005。

运行线索是：

```bash
cd source\HierGNN
pip install -r requirements.txt
python hiergnn.py --dataset cicids17 --sample_ratio 0.1 --gpu_id 0
python hiergnn.py --dataset cicids17 --sample_ratio 0.1 --gpu_id 0 --pre_sample
```

需要注意几个复现缺口：仓库没有 PCAP/CSV 到 `.pt` 的预处理脚本；没有 StandardScaler 保存/加载逻辑；没有 FGSM/PGD 攻击代码；没有论文消融实验开关；没有 MAML；`flow_info` 被传入模型但未被使用；`PacketLevelGAT` 中计算了 node attention weights 但没有用于 pooling 或返回解释结果；`sample_ratio=1.0` 时 `test_dataset` 可能保持为 `None`，默认运行路径需要小心。

## 12. 本篇精华

- HierGNN 的核心不是“用了 GNN”，而是把 NIDS 拆成包级去噪和流级时序建模两个尺度。
- 动态过滤模块是论文鲁棒性的主要来源：硬 mask 减少可攻击特征，软 gate 做样本自适应重权。
- 少标签实验设计较完整，同时覆盖比例采样和固定样本数采样，比只报 10%/20% 训练集更有说服力。
- 对抗实验显示，传统强基线如 XGBoost 在 FGSM/PGD 下掉点很大，而 HierGNN 掉点很小，这是论文最有辨识度的结果。
- 消融结果支持“包级模块抗扰动、流级模块补上下文”的功能分工。
- 代码可作为模型骨架参考，但不是完整论文复现包；预处理、ToN-IoT、MAML、对抗评估都需要补。
- 对综述写作来说，这篇可归入“hierarchical GNN + few-shot NIDS + adversarial resilience”，但引用 MAML 贡献时要谨慎。

## 13. 建议精读路线

先读 Introduction 和 Related Work，抓住作者设定的三重矛盾：IoT 异构、标签稀缺、对抗扰动。然后精读 Methodology 的 A-D 小节，重点画出从 PCAP 到包图序列、再到流向量的张量流。

第二遍读实验时，不要只看最高 accuracy，优先看 0.1%、300 samples、PGD 三组结果，因为它们最能验证论文标题里的 “limited labeled data” 和 “resilient”。

最后对照代码读 `hiergnn.py`：先看 `DynamicFeatureFilter`、`PacketLevelGAT`、`TemporalGNN`、`GeneralizationModule`，再看数据加载和主函数。读代码时重点标记论文有但代码没有的部分，这会直接决定后续复现计划和可信度评估。

<!-- codex-cli-deep-read: complete -->
