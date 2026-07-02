# [118] A graph empowered insider threat detection framework based on daily activities

## 1. 基本信息

编号：118  
题名：A graph empowered insider threat detection framework based on daily activities  
中文题名：基于日常活动的图增强内部威胁检测框架  
年份：2023  
来源：ISA Transactions 141: 84-92  
DOI：10.1016/j.isatra.2023.06.030  
主题归类：图学习、知识图谱与威胁情报  
关联方向：恶意流量、暗网与攻击检测，但本文更偏“用户行为/内部威胁/实体异常检测”，与网络流量检测是弱相关。  
代码：论文声明开源于 [Wayne-on-the-road/ResHybnet](https://github.com/Wayne-on-the-road/ResHybnet)。虽然元数据写“未发现本地代码”，但工作区实际存在 `source\ResHybnet`，本解析已读取该目录。

## 2. 中文翻译与核心摘要

这篇论文的核心不是检测单条恶意日志，而是把内部威胁检测重构为“发现恶意用户-日期节点”。作者认为员工行为往往按自然日呈现规律，内部人员也可能只在某些日期表现异常，因此日粒度风险识别更贴近安全运营。

方法上，论文把每天的用户行为拆成两类信号：一类是人工挑选的独立行为特征，例如首次登录时间、最后登出时间、首次/最后 USB 活动时间、非工作时间 USB 活动次数；另一类是当天活动序列，例如登录、登出、USB、文件、邮件等按时间排序后的序列。后者通过 LSTM auto-encoder 自动压缩成隐含特征。

分类阶段，作者构造“用户-日期”为节点的组织图，边来自上下级关系、同主管关系、同一用户不同日期关系。然后提出 ResHybnet：先用 GNN 聚合组织图邻域信息，再通过残差连接把原始节点属性加回去，最后用 CNN 捕捉非拓扑特征模式。论文的主要论点是：GNN 能利用组织关系，但会削弱个体节点属性；残差连接可以补偿这种属性损失，CNN 则继续挖掘节点特征内部模式。

## 3. 论文解决的具体问题

论文解决的是内部威胁检测中三个相互缠绕的问题。

第一，内部人员具有合法访问权限，传统访问控制或外围防护难以直接阻断，因此检测必须依赖行为偏离。问题不在于“有没有访问”，而在于“访问行为在时间、对象、频率、上下文上是否异常”。

第二，已有特征工程通常偏向单点统计特征，例如登录时间、USB 次数、文件类型数量。这些特征能体现行为强度或时间偏移，但难以表达“一天内活动发生的顺序结构”。例如同样都有 USB 行为，先非工作时间登录、再连接 USB、再打开压缩包，与正常上班期间打开文档的风险含义完全不同。

第三，单纯 CNN/ANN 把每个用户样本当作孤立向量，忽视组织关系；单纯 GNN 又可能因邻域传播过强而冲淡节点自身特征。本文实际要解决的是：如何同时保留个体日行为特征、日内序列模式和组织关系结构。

## 4. 创新点深度提炼

1. **把检测对象定义为 user-day**：不是“用户长期是否恶意”，也不是“单条日志是否恶意”，而是判断某个用户在某一天是否存在恶意行为。这一粒度更适合日报、告警排查和风险评分。

2. **人工特征与自动序列特征融合**：手工特征负责表达专家可解释的行为偏移，LSTM auto-encoder 负责从日内行为序列中提取不易手工刻画的隐模式。

3. **把组织关系转化为用户-日期图**：同一员工不同日期相连，上下级用户-日期相连，同主管用户-日期相连，使模型能利用“组织中相似角色或管理关系下的行为相似性”。

4. **ResHybnet 的关键不是简单堆叠 GNN 和 CNN，而是残差补偿**：实验显示去掉残差后性能大幅下降，说明 GNN 聚合本身可能破坏节点属性，残差连接才是模型有效的关键结构。

5. **专门分析 LSTM 输入序列长度**：作者没有只给一个最大长度设置，而是比较均值、标准差附近和最大长度，说明序列截断/填充会影响特征质量。

## 5. 科学问题与研究假设

核心科学问题可以概括为：内部人员的恶意行为是否能在“日粒度行为序列 + 组织关系图”中形成可学习的异常模式？

对应研究假设包括：

1. 员工日常工作负载具有日周期规律，因此按自然日组织行为比跨年整体建模更贴合检测任务。

2. 恶意用户-日期不仅会在独立统计特征上异常，也会在日内活动顺序上表现出隐含差异。

3. 组织关系图中相连节点存在行为相似性，GNN 可以利用这种相似性增强检测。

4. 单纯 GNN 会弱化节点原始属性，残差连接能恢复个体行为特征，从而提升分类性能。

5. LSTM auto-encoder 的输入序列越完整，越可能保留有用模式，但超过一定长度后边际收益趋缓。

## 6. 科学方法与技术路线

技术路线是“日志到日节点，日节点到图，图上分类”。

首先，CERT 4.2 原始日志被聚合为用户-日期样本。每个样本有两组属性：人工特征矩阵 `Xm` 和自动特征矩阵 `Xa`。人工特征来自 logon 和 device，自动特征来自 logon、device、file、email 的日内序列。

其次，活动序列被编码为 24 类：12 种活动乘以工作时间/非工作时间两种上下文，再加一个 `none` 填充值。序列经 one-hot 后输入 LSTM auto-encoder，编码端输出 5 维隐特征。最终行为特征为 `Xb = concatenate(Xm, Xa)`。

再次，构造组织图 `G(V,A)`，每个节点是一个 user-day。边连接上级与下属、同主管员工、同一员工不同日期。ResHybnet 先用 GNN 得到图增强表示 `Hc`，再用残差 `X = Hc + Xb` 保留原始属性，最后交给 CNN 和全连接层输出二分类结果。

## 7. 实验设计与实验步骤

可复核流程如下：

1. **数据**：使用 CERT 4.2，原始数据包含 LDAP、device、email、file、http、logon、psychometric 等文件；论文实际主要使用 device、logon、file、email，LDAP 用于组织关系。

2. **采样**：从 1000 名员工、70 名恶意内部人员中构造平衡样本，共 1908 个 user-day 节点，训练/测试约 70%/30%。

3. **预处理**：人工特征为 5 个：首次登录时间、最后登出时间、首次设备活动时间、最后设备活动时间、非工作时间设备活动次数；时间映射到 `[0,1]`。

4. **序列编码**：将每天的 logon/device/file/email 活动按时间排序，编码为 24 类活动；短序列尾部填充 `none`，最长序列为 74，因此主实验使用长度 74，one-hot 维度为 25。

5. **自动特征训练**：LSTM auto-encoder 以重构误差为目标训练，编码输出维度设为 5，再与 5 维人工特征拼接，形成 10 维节点属性。

6. **模型/基线**：比较 ResHybnet、SVM、CNN、GNB、RF、LR、GCN；另比较 GCN/GAT 作为 GNN 组件时是否启用残差。

7. **训练策略与指标**：PyTorch、PyTorch Geometric、scikit-learn；早停 patience 为 30，delta 为 0.0001；每组实验 10 轮，报告 Accuracy、Precision、Recall、F1。

8. **消融/敏感性**：一组验证残差连接；一组比较 manual、automatic、manual+automatic；一组比较序列长度 5、16、27、38、49、60、74。

9. **结果核查**：本地 `source\ResHybnet\detection_result` 中保存的 10 轮 `manual+lstm_seq74` 结果均值与论文表 4 的 F1 约 92.19% 一致。

## 8. 关键结果、结论与证据

ResHybnet(GCN+CNN) 达到 Accuracy 92.62%、Precision 91.52%、Recall 92.87%、F1 92.19%，整体优于 SVM 的 F1 90.22%、CNN 的 90.15%、LR 的 88.81%。单独 GCN 的 F1 只有 75.53%，虽然 Recall 很高，但 Precision 明显偏低，说明图传播带来大量误报。

残差连接是最强证据：GCN+CNN 有残差时 F1 为 92.19%，无残差时降到 73.73%；GAT+CNN 有残差时 F1 为 90.47%，无残差时为 72.16%。这说明模型提升并不是来自“GNN+CNN 堆叠”，而是来自图信息与原始节点属性之间的平衡。

特征融合也有实证支持：manual 特征 F1 为 91.63%，automatic 特征单独只有 85.56%，融合后 F1 为 92.19%。这表明序列隐特征不是主导信号，但能补充手工特征，带来 0.56 个百分点的 F1 提升。

序列长度实验显示，长度 5 和 16 的 F1 低于只用人工特征；长度 27 后进入较高区间，最大长度 74 得到最高 F1 92.19%，但 27、49、60 等长度已接近最优，说明长序列有帮助，但收益并非线性增长。

## 9. 局限性与待解决问题

首先，CERT 4.2 是合成数据，且论文使用下采样构造平衡样本；真实内部威胁是极端类别不平衡问题，恶意样本比例远低于实验设置，Precision 和 Recall 在真实部署中可能明显变化。

其次，论文只使用了部分日志。http、psychometric 等信息没有充分进入特征工程，邮件内容也只简化为内外部地址类型，行为语义利用仍然粗。

第三，代码中的评估流程存在可商榷点。本地实现 `detection_with_ResHybnet.py` 用测试集 loss 做早停监控，这会让测试集参与模型选择；同时 `hybrid_models.py` 输出 `softmax` 后又用 `F.nll_loss`，严格来说应改为 `log_softmax + nll_loss` 或直接用 `CrossEntropyLoss`。

第四，图学习实验是偏 transductive 的设置，训练时图中包含全部节点和边，只通过 mask 区分训练/测试。对真实在线场景中新日期、新员工、新组织结构的泛化能力，论文没有充分验证。

第五，隐私与合规只是结论中提到，没有给出机制。内部威胁检测天然涉及员工监控，如何在隐私保护、可解释审计和检测有效性之间权衡，仍是开放问题。

## 10. 与本项目的关系

按你已有分类，“图学习、知识图谱与威胁情报”是合理的，但本文不是典型威胁情报知识图谱，也不是网络恶意流量检测。它更适合作为“多源日志融合 + 图异常检测 + 用户/资产行为建模”的参考文献。

对恶意流量、暗网、攻击检测项目的可迁移价值在于三点：一是把检测粒度从单条事件提升到实体-时间窗口，例如 user-day、host-hour、asset-day；二是把手工统计特征和序列自编码特征融合；三是用图关系补充孤立样本分类，例如用户-设备、主机-进程、IP-域名、账号-权限组等关系图。

但如果本项目核心是加密流量分类或暗网流量识别，本文相关性确实偏弱。它提供的是行为建模框架，而不是流量字节、包序列、会话统计或协议侧特征。

## 11. 代码对照分析

本地代码目录为 [source\ResHybnet](F:/泉城实验室/二期/论文/异常检测/source/ResHybnet)。主要对应关系如下：

- [README.md](F:/泉城实验室/二期/论文/异常检测/source/ResHybnet/README.md)：说明三阶段流程：序列预处理、LSTM auto-encoder 特征抽取、ResHybnet 检测。
- [code_for_sequence_process\1-to_sequence_for_all_user_multiprocessing.py](F:/泉城实验室/二期/论文/异常检测/source/ResHybnet/code_for_sequence_process/1-to_sequence_for_all_user_multiprocessing.py)：对应论文的日内活动序列构造。代码读取 logon、device、file、email，把工作时间定义为 8:00-18:00，并实现 24 类活动编码。
- [code_for_sequence_process\2-selectout_sample_data_for_LSTM_train.py](F:/泉城实验室/二期/论文/异常检测/source/ResHybnet/code_for_sequence_process/2-selectout_sample_data_for_LSTM_train.py)：从 1908 个样本中抽取对应 user-day 的序列，生成 `1-data-test-combine-sequence.csv`。
- [lstm_feature_extraction.py](F:/泉城实验室/二期/论文/异常检测/source/ResHybnet/lstm_feature_extraction.py)：对应 LSTM auto-encoder。`seq_len_list=[74]`，`n_feat=5`，输入 one-hot 维度 25，输出 5 维自动特征，并拼接人工特征。
- [tool_and_model\hybrid_models.py](F:/泉城实验室/二期/论文/异常检测/source/ResHybnet/tool_and_model/hybrid_models.py)：对应 ResHybnet。支持 `GCN/GAT/SAGE`，CNN 为两层 Conv1d，`x_dual = x + x_g` 就是论文残差连接。
- [detection_with_ResHybnet.py](F:/泉城实验室/二期/论文/异常检测/source/ResHybnet/detection_with_ResHybnet.py)：对应训练与评估。读取节点特征、`1-data-test-undirected_edge.csv`，构造 PyG `Data`，用 mask 划分训练/测试，输出 acc/pre/rec/f1。
- [sample_data](F:/泉城实验室/二期/论文/异常检测/source/ResHybnet/sample_data)：包含人工特征、序列、不同序列长度的融合特征和边文件。需要注意，代码包中没有完整提供从 LDAP 生成组织图边、从原始 logon/device 生成 5 个手工特征的全部脚本，更多是以预制 CSV 形式给出。
- 运行线索：在 `source\ResHybnet` 下先运行 `python lstm_feature_extraction.py`，再运行 `python detection_with_ResHybnet.py`；若要重做序列预处理，需要把 CERT 4.2 的 `logon.csv/device.csv/file.csv/email.csv` 放到 `code_for_sequence_process\cert4.2_data`。

## 12. 本篇精华

1. 本文最有价值的建模选择是把内部威胁定义为“恶意 user-day”，兼顾安全运营可解释性和机器学习样本构造。

2. 手工特征仍然是主信号，LSTM auto-encoder 序列特征是补充信号；融合提升不大但稳定，说明专家知识没有被深度模型替代。

3. GNN 在内部威胁检测中并非天然有效，单独 GCN F1 很低；组织图有用，但必须防止邻域传播稀释节点属性。

4. ResHybnet 的核心贡献是残差连接，而不是 GNN 与 CNN 的普通组合；无残差时性能接近崩溃。

5. 组织关系图的边设计很朴素，但实用：上下级、同主管、同用户跨日期，三类关系足以把孤立行为样本变成图学习问题。

6. 序列长度实验提醒：截断太短会损害自动特征，达到均值以上一个标准差后收益趋缓，最大长度不一定总是性价比最高。

7. 真实落地还缺少不平衡评估、在线学习、隐私保护、跨组织泛化和严格测试集隔离。

## 13. 建议精读路线

先读 Section 3，抓住 user-day 定义、人工/自动特征融合、ResHybnet 三个核心设计。然后读 Section 4，把 CERT 4.2 文件、5 个手工特征、24 类活动编码和组织图三条建边规则整理成自己的流程图。

接着重点看 Tables 4-7：表 4 看模型对比，表 5 看残差连接，表 6 看特征消融，表 7 看序列长度敏感性。最后对照本地代码读 `lstm_feature_extraction.py`、`hybrid_models.py`、`detection_with_ResHybnet.py`，同时记录代码与论文不完全一致或不够严谨的地方，尤其是早停使用测试集、损失函数写法、预制 CSV 缺少完整生成链路。

<!-- codex-cli-deep-read: complete -->
