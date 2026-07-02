# [274] One Train for Two Tasks: An Encrypted Traffic Classification Framework Using Supervised Contrastive Learning

## 1. 基本信息

- 题名：One Train for Two Tasks: An Encrypted Traffic Classification Framework Using Supervised Contrastive Learning
- 中文理解：一次训练同时完成包级与流级加密流量分类的监督对比学习框架
- 年份：2024
- 来源：arXiv preprint
- DOI：10.48550/arXiv.2402.07501
- 主题归类：加密流量分类、应用识别、跨粒度表征学习
- 方法名称：CLE-TFE，Contrastive Learning Enhanced Temporal Fusion Encoder
- 代码目录：`source\CLE-TFE`
- 正文包状态：标记为未截断，本文理解基于完整正文包与本地代码包阅读。

## 2. 中文翻译与核心摘要

这篇论文的核心意思是：现有加密流量分类方法往往把“单包分类”和“流分类”当成两个彼此独立的任务来训练，但流本来就是由包组成的，包级表示会直接影响流级表示；同时，很多方法只从单个样本自身学习 raw bytes 或统计特征，没有显式利用同类别样本之间的共同不变特征。作者提出 CLE-TFE，在 TFE-GNN 的字节级流量图编码器基础上加入监督对比学习，并把包级分类、流级分类、包级对比、流级对比统一在一次训练中完成。

论文最重要的判断是：包级任务不是流级任务的附属结果，而是优化流级表示的有效中间监督。实验证明，包级分类与包级对比能让每个 packet embedding 更可分，进而让 LSTM 聚合得到的 flow embedding 更稳健。反过来，流级任务对包级表示的帮助并不明显，甚至会有轻微负影响。这一点比“又加了一个对比损失所以效果更好”的表述更有研究价值。

## 3. 论文解决的具体问题

论文针对两个具体痛点：

第一，表征学习层面的问题。加密流量中不能依赖明文内容，raw bytes、长度序列、统计特征都容易学到数据集特定模式。既有深度模型通常直接拟合分类目标，没有显式约束同类样本在嵌入空间中靠近、异类样本分开，因此对“同类流量共享的语义不变性”利用不足。

第二，任务组织层面的问题。包级分类和流级分类常被分别训练。这样既重复消耗计算资源，也浪费了包级表示对流级表示的天然支撑关系。作者的问题不是简单做多任务学习，而是要证明：在加密流量分类中，跨层级监督是否能让一个模型同时服务 packet-level 与 flow-level 两个粒度，并提升总体性能。

## 4. 创新点深度提炼

1. 双层监督对比学习  
   CLE-TFE 在包级和流级都做监督对比学习。包级对比不是直接扰动原始字节序列，而是在 TFE-GNN 构建的字节图上做 node dropping 和 edge dropping；流级对比则对包序列做 packet dropping。

2. 把图增强放在字节语义图上  
   TFE-GNN 的图节点是 byte value，边表示滑动窗口内字节共现的 PMI 关系。对节点和边做扰动，相当于迫使模型在局部字节缺失或字节相关性被削弱时仍学到稳定表示，这比随机裁剪原始 byte sequence 更贴近其图建模假设。

3. 一次训练覆盖两个分类任务  
   论文提出 cross-level multi-task learning：同一个 TFE-GNN packet encoder、同一个 LSTM flow encoder，在一个目标函数内同时优化包分类、流分类、包级监督对比、流级监督对比。

4. 明确揭示跨层级方向性  
   消融和 t-SNE 结果显示，包级任务明显帮助流级任务，但流级任务对包级表示帮助有限。这说明流量分类中“底层包表示质量”是流表示的瓶颈之一。

5. 计算开销优势  
   相比 ET-BERT 这类预训练 Transformer，CLE-TFE 不依赖大规模预训练，FLOPs 约为 ET-BERT 的 1/14；相比 TFE-GNN 参数仅小幅增加，主要来自新增 packet classification head。

## 5. 科学问题与研究假设

科学问题可以概括为三层：

- 同类别加密流量样本是否存在可通过监督对比学习捕获的共同不变特征？
- 字节级流量图上的结构扰动，是否能比直接分类训练更好地学习稳健 packet representation？
- 包级任务与流级任务之间是否存在可利用的跨层级监督关系？

论文的主要研究假设是：

- 同一应用/行为类别的 packet 或 flow 在嵌入空间中应具有可聚合的类内共性；
- 适度删除图节点、图边和流内包不会改变类别语义，因此可作为语义保持增强；
- 优化 packet embedding 会改善后续 LSTM 聚合出的 flow embedding；
- 将包级和流级任务统一训练，比两次独立训练更高效，并能达到更好的综合性能。

## 6. 科学方法与技术路线

技术路线是“字节图编码 + 双层增强 + 双层监督对比 + 跨层级多任务分类”。

数据先从 pcap 中抽取 header 和 payload 字节，删除 IP 地址和端口等敏感或易泄漏字段，然后分别构造 header graph 与 payload graph。图节点是字节值，边由滑动窗口内字节共现的正 PMI 关系形成。

模型延续 TFE-GNN：每个包的 header graph 和 payload graph 分别经过 GNN 编码，再通过 cross-gated filter 融合为 packet representation；一个 flow 中的 packet representations 输入 LSTM 得到 flow representation。

训练时有四个目标：

- 包级分类损失：packet representation 接 MLP 分类头；
- 流级分类损失：flow representation 接 MLP/linear 分类头；
- 包级监督对比损失：原始包图与增强包图作为两视图，同类包互为正样本；
- 流级监督对比损失：原始包序列与 packet dropping 后的增强序列作为两视图，同类流互为正样本。

总损失为：包分类 + 流分类 + α 包级对比 + β 流级对比。论文中的 α、β 在代码里分别对应 `coe_graph` 与 `coe` 的角色。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   使用 ISCX VPN-nonVPN 与 ISCX Tor-nonTor，拆成四个独立数据集：ISCX-VPN、ISCX-NonVPN、ISCX-Tor、ISCX-NonTor。类别数分别为 6、6、8、8。论文报告的 flow/packet 数量为：VPN 1674/19282，NonVPN 3928/33838，Tor 1697/22888，NonTor 7979/68024。

2. 预处理  
   用 SplitCap 得到双向流；代码 README 明确只使用 TCP pcap。Tor 数据因流数量有限，会按 60 秒非重叠窗口切分。过滤无 payload 或长度超过 10000 的异常流；去除 Ethernet header、IP 地址和端口；每条流最多保留前 15 个包。代码中 `config.py` 仍保留 `FLOW_PAD_TRUNC_LENGTH=50`，但训练通过 `--point 15 --K 15` 实际只取前 15 个包参与模型。

3. 图构造  
   对 header 与 payload 分别构造 byte-level traffic graph。payload 每包截断/填充到 150 字节，header 到 50 字节；PMI 窗口大小为 5。代码中 `utils.construct_graph()` 实现正 PMI 边构造。

4. 模型与基线  
   流级基线包括 AppScanner、K-FP、FlowPrint、CUMUL、FS-Net、DF、ET-BERT、TFE-GNN 等；包级基线包括 Securitas、2D-CNN、3D-CNN、DeepPacket、BLJAN、EBSNN 等。CLE-TFE 使用 TFE-GNN 风格 GNN 编码器、LSTM、双分类头和监督对比损失。

5. 训练  
   采用 PyTorch + DGL，RTX 3080，结果取 5 次运行均值。关键超参：edge dropping 0.05，node dropping 0.1，packet dropping 0.6，temperature 0.07。不同数据集的 α、β 不同，例如 VPN 中 β=0.5、α=1.0。

6. 指标  
   报告 Overall Accuracy、Precision、Recall、Macro F1。Macro F1 对多类不平衡更重要，论文主要以它支撑结论。

7. 消融/敏感性  
   消融包括去掉流分类、流对比、包分类、包对比、header graph augmentation、payload graph augmentation，以及把监督对比替换成无监督对比。敏感性分析考察 α、β、edge dropping ratio、node dropping ratio。

8. 结果核查  
   重点核查两点：CLE-TFE 是否在两个任务总体最优；包级任务是否确实促进流级任务。论文通过表 1/2 的主结果、表 3-6 的消融、t-SNE 可视化和 FLOPs/参数对比共同支撑。

## 8. 关键结果、结论与证据

流级任务上，CLE-TFE 在四个数据集均取得最好结果。Macro F1 分别为：

- ISCX-VPN：0.9761，TFE-GNN 为 0.9536；
- ISCX-NonVPN：0.9389，TFE-GNN 为 0.9240；
- ISCX-Tor：1.0000，TFE-GNN 为 0.9855；
- ISCX-NonTor：0.8994，TFE-GNN 为 0.8507。

包级任务上，CLE-TFE 在 NonVPN、Tor、NonTor 最优；在 VPN 上略低于 EBSNN-LSTM。作者解释为：EBSNN 单独优化包级任务，而 CLE-TFE 要同时兼顾流级与包级，存在任务权衡。

消融结果最有信息量：去掉包级分类与对比后，VPN 流级 F1 从 0.9761 降到 0.9354，说明包级监督对流级表征非常关键；而去掉流级任务时，包级结果反而没有明显变差，说明跨层级帮助主要是自下而上。监督对比显著优于无监督对比，VPN 平均 F1 从 0.8920 提升到 0.9597，说明标签指导下的正样本扩充是核心收益来源。

计算成本方面，CLE-TFE 只比 TFE-GNN 增加少量参数，但由于使用更短流长度，FLOPs 低于 TFE-GNN，并远低于 ET-BERT。

## 9. 局限性与待解决问题

第一，图增强是固定随机策略。node dropping、edge dropping、packet dropping 都靠人工设定比例，不能根据样本难度、类别特征或图结构自适应调整。论文未来工作也明确提到 learnable graph augmentation。

第二，监督对比虽然增加了正样本，但没有充分处理 hard negative。加密流量中相近应用类别很容易共享长度、时序或 TLS 行为模式，困难负样本挖掘可能比普通负样本数量更重要。

第三，数据集仍是 ISCX 系列，且划分方式并非行业统一标准。README 也提示数据划分会导致复现差异。模型是否能泛化到更新协议、QUIC/HTTP3、大规模真实企业流量、跨采集环境，论文没有充分证明。

第四，包标签直接继承流标签，这在应用分类中通常可接受，但在更细粒度异常检测或多行为混合流中可能过强。一个 flow 内不同 packet 未必都承载相同判别信息。

第五，ISCX-Tor 接近满分需要谨慎看待。满分可能说明任务本身在该预处理和划分下较容易，也可能存在数据集偏差。真正部署前应做跨时间、跨环境、跨数据源验证。

## 10. 与本项目的关系

这篇论文与“异常检测”项目的关系较强，但它本身不是异常检测论文，而是加密流量多类分类框架。可迁移价值主要在三点：

- 可把“正常/异常”或“攻击类型”视为监督标签，用监督对比学习拉近同类行为、拉远不同攻击/应用行为；
- 它提供了从 packet representation 到 flow representation 的跨粒度建模范式，适合网络安全中“单事件-会话-主机行为”这类层次结构；
- 字节图增强与 packet dropping 对抗了局部字段缺失、包丢失和采集不完整问题，这与真实异常检测场景中的噪声很接近。

但如果用于异常检测，需要补充开放集/未知类能力。CLE-TFE 的设定是闭集多分类，默认测试类别已在训练中出现；而异常检测常要求发现未见过的异常模式。

## 11. 代码对照分析

代码与论文主线基本一致，关键文件如下：

- `README.md`：给出环境、数据下载、SplitCap、pcap 转 npz、图构造、训练和评估命令。训练命令中的 `--coe` 对应流级对比权重 β，`--coe_graph` 对应包/图级对比权重 α。
- `pcap2npy.py`：pcap 读取入口。`process()` 从包中拆出 header/payload，并保存 payload length、packet length、IP、端口、时间、协议、TCP flag、MSS 等字段。
- `utils.py`：核心预处理工具。`remove()` 删除 header 中 IP 地址和端口相关字段；`split_flow_ISCX()` 处理普通 ISCX 流；`split_flow_Tor_nonoverlapping()` 实现 Tor 的 60 秒非重叠切分；`construct_graph()` 用 PMI 构造字节图。
- `preprocess.py`：数据集构建入口。先按类别读取 `.npz`，做约 9:1 train/test 划分，再分别保存 payload/header 的 `.npz` 与 DGL 图文件。
- `dataloader.py`：DGL 数据集。`MixTrafficFlowDataset4DGL` 同时加载 header graph 与 payload graph，并维护 mask 以过滤空图。
- `model_new_aug.py`：模型主体。`GCN` 实际使用 DGL `SAGEConv`；`SupConLoss` 是监督对比损失；`MixTemporalGNN` 实现 header/payload 图增强、包级对比、包分类头、LSTM 流编码、流级对比和流分类。
- `train_new.py`：训练入口。总损失为 `flow CE + coe * flow contrastive + coe_graph * graph contrastive + packet CE`。
- `test_new.py`：评估入口。加载同一模型后同时打印 flow-level 和 packet-level 的 `classification_report`。

一个实现细节值得注意：论文中包级增强表述为先 node dropping 再 edge dropping，但代码里是 `drop_node_trans(drop_edge_trans(graph))`，即先 DropEdge 后 DropNode。两者在随机图扰动语义上相近，但严格复现实验时应以代码为准。

另一个细节是，代码同时对 header graph 和 payload graph 做包级监督对比，然后用 `hp_ratio` 加权融合二者的 contrastive loss。这比正文主干叙述更具体，也解释了消融中“header augmentation”和“payload augmentation”可以分开比较。

## 12. 本篇精华

- CLE-TFE 的核心不是单纯“加对比学习”，而是把包级和流级两个粒度的分类与对比目标统一到一次训练中。
- 包级监督是流级性能提升的关键来源；消融显示去掉包级分类与对比会显著伤害流级 F1。
- 字节图增强比原始字节序列增强更贴合 TFE-GNN，因为图边本身表达 byte co-occurrence 的语义相关性。
- 监督对比远强于无监督对比，说明同类样本之间的多正样本关系对加密流量表征非常有价值。
- 流级任务对包级任务帮助有限，跨层级收益主要是 packet 到 flow 的自下而上传递。
- CLE-TFE 在 ISCX 四个数据集上取得很强综合性能，尤其流级任务全部最优。
- 相比 ET-BERT，CLE-TFE 不依赖大规模预训练，计算成本低得多，更适合资源受限的安全分析场景。
- 用于异常检测时，需要额外解决未知类、跨域泛化和混合行为流标签问题。

## 13. 建议精读路线

建议按以下顺序读：

1. 先读 Introduction，抓住两个问题：同类共性未利用、包级/流级重复训练。
2. 再读 Section 3.2，重点理解为什么在 byte-level traffic graph 上做 node/edge dropping。
3. 接着读 Section 3.3 和损失函数，明确四个训练目标如何组成一次训练。
4. 精读 Table 3-6 的消融，比主结果更能说明方法是否真的有效。
5. 最后读代码 `model_new_aug.py` 和 `train_new.py`，把论文公式对应到实际实现，尤其是 `graph_cl_loss`、`cl_loss`、`packet_head` 和总损失。

<!-- codex-cli-deep-read: complete -->
