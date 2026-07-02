# [539] Self-Supervised and Interpretable Anomaly Detection Using Network Transformers

## 1. 基本信息

- 题名：Self-Supervised and Interpretable Anomaly Detection Using Network Transformers
- 中文题名：基于网络 Transformer 的自监督可解释异常检测
- 作者：Daniel L. Marino、Chathurika S. Wickramasinghe、Craig Rieger、Milos Manic
- 来源：IEEE Transactions on Industrial Informatics, Vol. 21, No. 5, May 2025
- DOI：10.1109/TII.2025.3534443
- 研究对象：工业控制系统网络流量异常检测
- 方法关键词：Network Transformer, self-supervised learning, graph packet dissection, hierarchical graph features, interpretable anomaly detection
- 数据：Idaho National Laboratory 提供的真实 ICS 测试床 PCAP，共 6,036,046 个数据包
- 代码状态：本地未发现该论文对应开源代码包

## 2. 中文翻译与核心摘要

这篇论文的核心问题不是“能不能检测网络异常”，而是“检测到异常后，能不能说清楚异常来自哪里、影响了哪些设备、涉及哪些连接”。作者认为传统深度模型和常见无监督异常检测器虽然可以给出异常分数，但输出过于黑盒，工程人员很难据此定位攻击源、受害设备和异常通信路径。

论文提出 Network Transformer，简称 NeT。它先把网络通信表示成图：IP 地址是节点，源地址到目的地址之间的数据包序列是边。然后用 Transformer 对每条边上的包序列进行自监督建模，通过“根据过去包预测未来包”的方式学习正常通信模式。训练完成后，Transformer 编码器输出包级嵌入，进一步聚合成三层特征：全局网络特征、设备节点特征、连接边特征。

最终异常检测并不只发生在一个黑盒向量上，而是可以沿着“全网-设备-连接”逐层下钻。实验表明，NeT 在真实 ICS 场景中可以检测 flood、scan、failed authentication、setting change 等异常，并能指出攻击发起设备、目标继电器以及异常连接。

## 3. 论文解决的具体问题

论文解决的是工业控制网络中的可解释异常检测问题，具体包含三层痛点。

第一，工业网络异常检测缺少高质量标注。攻击样本稀少，异常类型不完备，人工标注依赖领域专家，因此作者选择只用正常流量训练模型，把异常数据留到测试阶段。

第二，已有模型输出粒度太粗。很多方法只能给出某个时间窗口“异常/正常”的判断，不能说明异常由哪台设备、哪条连接、哪类通信变化触发。对 ICS 现场处置来说，这种结果不够用。

第三，网络通信天然是图结构，但许多 ML 方法把流量压平成统计特征，丢掉了源、目的、连接关系。作者希望把网络拓扑和通信关系直接嵌入模型设计，让模型表征与人类专家理解网络的方式一致。

## 4. 创新点深度提炼

1. **把可解释性前置到表示学习阶段**  
   论文没有主要依赖 LIME、SHAP 这类事后解释工具，而是把通信网络建模成图，使模型内部特征天然对应全网、设备和连接。这种解释不是“给黑盒补解释”，而是“让特征结构本身可追踪”。

2. **Graph Packet Dissection 形成层次化网络特征**  
   数据包按源 IP 和目的 IP 分组，形成边上的包序列；节点代表设备，边代表通信连接。之后通过求和聚合得到 edge、node、global 三类特征，使异常定位可以从全局检测下钻到设备和连接。

3. **用 Transformer 学习边上的包序列行为**  
   作者把一条连接上的连续数据包类比为一句话中的词序列，用 Transformer 编码包序列，捕获通信中的时序和上下文依赖。这比单纯统计包数量、端口数量、payload 长度等更有表达力。

4. **自监督训练避免异常标签依赖**  
   NeT 训练目标是用过去 k 个包预测未来 n 个包。正常 PCAP 可以自动切成输入-输出序列，不需要人工标注攻击类型。这一点非常契合工业现场“正常数据多、异常标签少”的现实。

5. **TCP 特征与 raw bytes 两种输入路径并行验证**  
   NeT 使用 TCP 字段特征，NeTB 使用原始字节特征。实验中二者对不同攻击的敏感性不同：flood/scan 更容易被 NeT/NeTB 捕捉，setting change 中 raw bytes 因为包含 payload 信息而更有优势。

6. **将深度表征与传统异常检测器组合**  
   论文没有把 Transformer 直接做成端到端分类器，而是把它作为特征编码器，再接 LOF、OCSVM、Autoencoder。这样既保留无监督异常检测框架，又提升输入特征的结构化表达能力。

## 5. 科学问题与研究假设

核心科学问题可以概括为：如果把网络通信的图结构作为模型的归纳偏置，是否能在保持异常检测性能的同时提升定位和解释能力？

论文隐含了几个关键假设。

第一，正常工业网络通信具有稳定的图结构和时序模式。设备之间的通信对象、协议行为、包序列规律在正常状态下相对可学习。

第二，攻击会破坏这种正常通信模式。flood 和 scan 会改变通信量与连接形态；failed authentication 和 setting change 虽更隐蔽，但会引入 SSH、Telnet、DNP3 告警等异常通信迹象。

第三，Transformer 通过未来包预测学到的嵌入能够表达正常通信语义。异常流量在这个嵌入空间中会偏离正常分布，因此可被 AE、LOF、OCSVM 等检测器识别。

第四，边、节点、全局的求和聚合不会完全抹掉异常定位信息。也就是说，某条异常连接的嵌入变化会传递到相关节点，再传递到全局特征。

## 6. 科学方法与技术路线

论文方法可以拆成五步。

第一步是 PCAP 窗口化。作者使用 30 秒滚动窗口，把连续网络包切成可分析片段。

第二步是图化分解。每个窗口内，按源 IP 和目的 IP 将包分组。IP 地址是节点，源-目的通信关系是边，边上挂载该连接中的包序列。

第三步是包特征构造。论文考虑两类输入：一类是 TCP/UDP 解剖后的协议字段特征，另一类是原始字节特征，其中 raw bytes 方案使用 512 字节 payload/包内容表示。

第四步是 Transformer 自监督学习。编码器-解码器结构根据过去包预测未来包。数值字段用平方损失，二值和类别字段用交叉熵损失。训练完成后只取编码器作为包嵌入提取器。

第五步是层次聚合与异常检测。包嵌入先聚合成边特征，连接到同一设备的边特征再聚合成节点特征，全图所有边再聚合成全局特征。随后在不同层级上训练异常检测模型，用全局特征判断是否异常，用节点和边特征定位异常来源。

## 7. 实验设计与实验步骤

可复核流程如下。

1. **数据**  
   使用 INL 的真实 ICS 网络测试床。网络包含两台攻击机、两个保护继电器、一个电能质量表、一个 RTAC、一个卫星同步网络时钟、一台 SCADA PC 和两个交换机。流量通过 SPAN 端口镜像到 sniffer，保存为 PCAP。总计 6,036,046 个包。

2. **场景划分**  
   包含五类场景：正常运行、flood attack、scan attack、failed authentication、setting change。PC1 发起 flood 和 scan，目标是 Relay 1/2；PC2 发起 failed authentication 和 setting change，同样针对 Relay 1/2。

3. **预处理**  
   对 PCAP 做 30 秒滚动窗口；按源-目的 IP 分组；执行 TCP/UDP dissection；抽取 TCP 特征或 raw bytes 特征；按连接打包成张量；用 TensorFlow-Datasets 缓存预处理结果。

4. **模型训练**  
   只用正常场景训练。正常数据按 80% 训练、20% 测试划分，并做 5-fold cross-validation。Transformer 用自监督目标训练：输入过去 k 个包，预测未来 n 个包；优化器使用 ADAM。

5. **特征提取**  
   训练完成后，用 Transformer 编码器生成包嵌入。边特征为该连接包嵌入求和；节点特征为相关边特征求和；全局特征为窗口内全部边特征求和。

6. **模型与基线**  
   NeT/NeTB 特征分别接 LOF、OCSVM、AE。基线使用文献中的手工统计特征，同样接 LOF、OCSVM、AE。AE 使用重构误差判断异常。

7. **指标**  
   全局层面使用 FPR 和 ADR。FPR 衡量正常测试窗口被误报为异常的比例；ADR 衡量攻击场景窗口被检测为异常的比例。ADR 分总体和各攻击场景报告。

8. **消融与敏感性**  
   论文主要比较了三类检测器、两类 NeT 输入特征和手工基线。它没有充分展开窗口长度、Transformer 维度、预测步长、聚合函数、阈值选择等超参数敏感性实验。

9. **结果核查**  
   全局层面看是否检测到攻击；节点层面看 PC1/PC2 和 Relay 1/2 是否异常；边层面看 PC1-Relay、PC2-Relay 连接是否被标出。RTAC 在 failed authentication 和 setting change 中也异常，原因是继电器会通过 DNP3 向 RTAC 发送告警。

## 8. 关键结果、结论与证据

全局特征的 t-SNE 可视化显示，flood 和 scan 与正常流量分离明显；failed authentication 和 setting change 与正常流量差异更细微。这符合直觉：flood/scan 会显著改变通信量和连接模式，而认证失败和配置变更更多体现在局部协议行为和告警通信上。

Table III 的文字分析表明，NeT 和 NeTB 在总体上达到与手工基线相当或更好的检测表现，尤其在 flood 和 scan 上 ADR 更高。AE 在三个检测器中表现最好，因此作者后续节点和边分析主要使用 AE。

节点层面的结果更能体现论文价值。Flood 和 scan 中，PC1 的异常计数最高，符合攻击源设定；failed authentication 和 setting change 中，PC2 被识别为异常源。Relay 1 和 Relay 2 也出现高异常比例，说明模型能识别受攻击设备。

边层面的结果进一步定位到连接。Flood/scan 中异常连接集中在 PC1 与两个继电器之间；failed authentication/setting change 中异常连接集中在 PC2 与两个继电器之间。这说明 NeT 不只是检测“有攻击”，还能给出工程处置更需要的连接级证据。

论文最重要的结论是：图结构带来的可解释性并没有明显牺牲检测性能。相反，NeT 在保持或提升检测表现的同时，提供了传统统计特征基线不具备的层次化定位能力。

## 9. 局限性与待解决问题

本次正文包标注为未截断，因此整体理解不受正文缺失影响。不过纯文本中的表格数值和图像细节没有完整呈现，若要精确引用 Table III 的具体 FPR/ADR 数字，仍建议回到 PDF 复核。

论文实验只覆盖一个 ICS 测试床，设备数量、协议组合和攻击类型都较有限。NeT 是否能泛化到更大规模企业网、多网段 ICS、动态 IP、NAT、加密流量或复杂横向移动场景，仍未验证。

节点和边层面的评估主要用异常计数和图示说明，没有给出严格的连接级 precision、recall、F1 或定位准确率。也就是说，论文证明了“能给出有意义的定位线索”，但还没有充分量化定位质量。

聚合方式较简单。边特征、节点特征、全局特征都采用求和，这会让高流量攻击更容易显现，但也可能让低频隐蔽攻击被淹没。求和还可能弱化方向性、时间顺序和协议状态机信息。

自监督目标是未来包预测，但异常检测目标是分布偏离识别，两者并不完全一致。未来工作可以比较对比学习、掩码包建模、图自编码、时序图预测等目标。

可解释性目前主要停留在设备和连接级。作者在结论中也提到，未来希望结合 LIME/SHAP 做包级甚至字节级解释。这说明 NeT 的解释能力还没有深入到“哪个字段、哪个 payload 片段导致异常”。

## 10. 与本项目的关系

这篇论文与“入侵检测与网络异常检测”方向直接相关，尤其适合放在“工业控制网络中的自监督与可解释异常检测”小节中。它的相关性不是因为模型名字用了 Transformer，而是因为它把网络异常检测从单点分数推进到结构化定位。

对本项目最有借鉴价值的是三点：第一，把网络流量建成通信图，而不是只做窗口统计；第二，用正常数据自监督预训练，降低异常标签依赖；第三，把异常检测输出设计成全局、设备、连接三级证据链。

如果本项目关注的是跨域异常检测，NeT 也有启发：不同系统可以抽象出不同图结构，例如设备-传感器图、服务调用图、主机-进程图，再沿图结构做层次化异常定位。不过本文实验仍偏 ICS 网络，迁移到其他异常检测域需要重新定义节点、边和事件序列。

## 11. 代码对照分析

本地未发现该论文对应的开源代码，因此不能给出真实源码文件对应关系。若复现该方法，代码目录大概率应包含以下模块。

- `pcap_preprocess/` 或 `data_pipeline/`：读取 PCAP，做 30 秒滚动窗口，调用 TCP/UDP 解析器，按源-目的 IP 分组。
- `packet_features.py`：实现 TCP 字段特征与 raw bytes 特征；raw bytes 路径需要处理固定长度 512 字节、padding、截断和类别/数值字段编码。
- `graph_dissector.py`：构造窗口内通信图，维护 node/IP、edge/source-destination、edge packet sequence 的映射。
- `datasets.py`：把分组后的包序列转为 TensorFlow 张量，并接入 TensorFlow-Datasets 缓存。
- `models/network_transformer.py`：实现 encoder-decoder Transformer、多头注意力、位置编码、右移目标序列的可训练 `W0`、混合损失函数。
- `train_net.py`：只用正常流量训练 Transformer，自监督预测未来包，优化器为 ADAM。
- `feature_aggregation.py`：用编码器输出生成 edge、node、global 三层特征，核心操作是包嵌入求和与边特征求和。
- `detectors.py`：实现 LOF、OCSVM、AE 三类异常检测器；AE 需要重构误差和阈值逻辑。
- `experiments/global_eval.py`：实现 5-fold、80/20 正常数据划分、攻击场景测试、FPR/ADR 计算。
- `experiments/node_edge_analysis.py`：统计每台设备、每条连接的异常计数，生成类似 Fig. 8 和 Fig. 9 的结果。
- `visualization.py`：t-SNE 可视化全局特征，绘制不同攻击场景与正常流量的分布差异。

运行线索上，论文明确提到 Python multiprocessing、TensorFlow、TensorFlow-Datasets 和 ADAM。PCAP 解析层可能需要 Scapy、PyShark 或 tshark 之类工具，但正文没有指定具体库。

## 12. 本篇精华

1. NeT 的核心不是“Transformer 检测异常”，而是“用 Transformer 学习连接上的包序列，再用图结构把异常解释回设备和连接”。

2. 论文把网络异常检测的输出从单一异常分数扩展为全局、节点、边三级证据，适合工业现场排障和攻击溯源。

3. 自监督未来包预测让模型只依赖正常流量训练，符合 ICS 中异常样本稀缺、标注昂贵的现实。

4. Flood 和 scan 这类高流量攻击在 NeT/NeTB 特征中更容易分离；failed authentication 和 setting change 更隐蔽，需要协议字段和 payload 信息共同支撑。

5. AE 在该实验中优于 LOF 和 OCSVM，说明深度表征之后仍需要合适的无监督异常评分器。

6. RTAC 在部分攻击中被标为异常并非误判，而是攻击触发继电器告警后通过 DNP3 影响到 RTAC，体现了模型捕获间接影响的能力。

7. 论文的可解释性主要来自结构设计，不是事后解释算法；但它还没有达到字段级、包级因果解释。

## 13. 建议精读路线

先读 Introduction 和贡献列表，抓住作者真正要解决的是“异常定位与解释”，不是单纯刷检测指标。

然后重点读 Section III-A 到 III-C，对照 Fig. 2、Fig. 3、Fig. 4 理解三件事：包如何变成图，Transformer 如何训练，edge/node/global 特征如何聚合。

接着读 Section IV-A，弄清 ICS 测试床、五类场景、PC1/PC2/Relay/RTAC 的关系。后续所有解释性结果都依赖这个实验拓扑。

再读 Table III 和作者对它的分析，关注 NeT、NeTB、baseline 在不同攻击上的差异，而不是只看总体平均。

最后精读 Fig. 8 和 Fig. 9。这两幅图是论文贡献的关键证据：它们说明模型能从“检测到异常”进一步走到“哪台设备异常、哪条连接异常”。