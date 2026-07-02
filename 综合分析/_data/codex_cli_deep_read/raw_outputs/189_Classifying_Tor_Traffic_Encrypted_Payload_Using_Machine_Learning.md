# [189] Classifying Tor Traffic Encrypted Payload Using Machine Learning

## 1. 基本信息

- 编号：189
- 题名：Classifying Tor Traffic Encrypted Payload Using Machine Learning
- 年份：2024
- 来源：IEEE Access
- DOI：10.1109/access.2024.3356073
- 主题归类：加密流量分类与应用识别
- 二级关联：其他 AI 安全与跨域异常检测
- 数据集：UNB-CIC / ISCXTor2016
- 代码状态：未发现该论文对应的本地开源代码
- 正文包状态：本次提供正文未截断

## 2. 中文翻译与核心摘要

这篇论文研究的是：**不依赖流级统计特征，也不解密内容，仅凭单个加密负载包的十六进制字符分布，区分 Tor 与 nonTor 流量**。

传统 Tor 流量检测常用流级特征，例如持续时间、包间隔、上下行统计、突发模式等。这类方法效果高，但有两个明显问题：第一，需要观察多个包甚至完整流，实时性较差；第二，在非对称路由、采样缺失、流重组困难时，特征可靠性下降。本文试图避开这些问题，把分析对象压缩到**单个 packet 的 encrypted payload**。

论文的核心直觉是：理论上，良好的加密输出应接近随机，Tor 与普通 TLS/SSH/proprietary 加密负载不应暴露可区分信息。但 Tor 的通信机制并不只是“多加密一次”这么简单，它涉及固定 cell、分层加密、不同协议栈处理、应用流量经 Tor 网关重新封装等因素。作者因此假设：这些工程机制可能在密文十六进制字符分布上留下可统计识别的痕迹。

论文分两步验证：

1. 用 Mann-Whitney U 检验比较 Tor 与 nonTor 加密负载的 hex 字符频率/比例分布，发现 256 个应用-特征组合中有 242 个存在显著差异，差异率为 94.53%。
2. 用 J48、Random Forest、IBk 对 8 类应用分别做 Tor/nonTor 二分类。最终更重视与包长弱相关的比例特征 Set 2，并报告 J48 平均准确率 95.65%；保留 5% 平衡数据作为 unseen prediction 时，最终模型平均准确率 98.06%。

这篇论文的价值不在于提出复杂模型，而在于把 Tor 检测问题从“流级行为建模”转向“单包密文统计指纹”，并试图解释为什么密文仍然可能表现出可区分的工程特征。

## 3. 论文解决的具体问题

论文解决的是一个非常具体的二分类问题：

> 给定一个已提取出的加密负载 payload，不使用 IP、端口、流持续时间、包间隔、上下行包数等流级特征，也不解密内容，仅基于 payload 十六进制字符分布，判断其来自 Tor 还是 nonTor 网络。

它针对的是现有 Tor 流量分类方法的几个痛点：

- **流级特征依赖多个包**：需要等待足够多 packet 后才能计算特征，不适合低延迟检测。
- **时间特征受网络环境影响**：延迟、抖动、拥塞、非对称路由都会改变包间隔和流级统计。
- **固定 cell 检测可能脆弱**：如果 Tor 配置或实现细节变化，仅依赖 cell 尺寸等显性特征可能失效。
- **深度学习 header/raw packet 方法可解释性较弱**：准确率高，但很难说明模型到底学到了什么。

本文要证明的是：**即便只看加密 payload 的字符统计，也能在相当高精度下检测 Tor**。

## 4. 创新点深度提炼

第一，论文把分类依据从 flow-based features 压缩到 **single encrypted payload packet**。这意味着检测器理论上可以对任意位置的单包进行判断，不要求观察完整连接，也不要求 packet 顺序完整。

第二，它使用的是非常轻量的人工特征：16 个十六进制字符的频数 `F_0` 到 `F_f`，以及对应比例 `R_0` 到 `R_f`。这类特征计算便宜、可解释，并且可直接追踪每个 hex 字符在 Tor/nonTor 中的统计差异。

第三，论文把“统计显著性分析”和“机器学习分类”连在一起。Mann-Whitney U 检验回答“密文分布是否真的不同”，机器学习分类回答“这种差异是否足以用于自动检测”。这个设计比直接堆模型更有说服力。

第四，作者意识到频数特征 Set 1 虽然准确率更高，但会受到 packet size 影响，因此最终更强调比例特征 Set 2。这是一个重要判断：如果直接使用频数，模型可能部分学到的是包长差异，而不是密文字符分布差异。

第五，论文从隐私角度强调：方法不解密、不读取明文语义，只统计密文十六进制字符。它属于 DPI，但不是内容审查式 DPI，而是密文表征统计。

## 5. 科学问题与研究假设

论文有两个明确研究问题。

**RQ1：能否基于 encrypted payload 区分 Tor 与 nonTor 加密流量？**

背后的理论冲突是：密码学理想要求密文不泄露明文信息，且应难以与随机串区分；但实际网络系统中，密文负载受到协议栈、分段、封装、cell 结构、加密层数、应用协议差异等因素共同影响。因此作者假设：Tor 和 nonTor 的 encrypted payload 在 hex 字符统计上可能存在可检验差异。

**RQ2：能否以数据高效方式，仅用单个 encrypted payload 区分 Tor 流量？**

这里的“数据高效”不是指训练数据少，而是指推理时不需要多包流特征。作者假设：如果单包 hex 字符比例已包含足够信号，那么轻量监督学习模型就能完成分类。

可进一步拆成三个子假设：

- H1：Tor 与 nonTor 加密负载的 hex 字符分布并非完全同分布。
- H2：这种差异不只是个别应用偶然现象，而是在 Audio、Browsing、Chat、Email、FTP、P2P、VDO、VoIP 多类应用中普遍存在。
- H3：比例特征比原始频数更能排除包长混杂，因此更适合作为最终方法的核心特征。

## 6. 科学方法与技术路线

论文技术路线如下：

1. 从 UNB-CIC / ISCXTor2016 数据集中读取 Tor 与 nonTor PCAP。
2. 按 8 类应用分别组织二分类数据集。
3. 清洗 packet，只保留包含加密 payload 的 TLS、SSH、TCP/proprietary 协议数据。
4. 对每个 encrypted payload 转为十六进制字符序列。
5. 提取两组特征：
   - Set 1：每个 hex 字符的频数，16 维。
   - Set 2：每个 hex 字符频数占 payload 总字符数的比例，16 维。
6. 使用 Pearson correlation 检查特征与 packet size 的关系。
7. 对 Tor/nonTor 特征分布做 Mann-Whitney U 检验，判断统计差异。
8. 使用 Weka 3.8.3 中的 J48、Random Forest、IBk 进行二分类。
9. 根据数据规模选择 10-fold cross validation 或 70/30 percentage split。
10. 额外保留平衡数据的一部分作为 unseen data，测试最终模型泛化。

整体上，论文方法非常像“密文字符统计指纹 + 可解释传统机器学习”。

## 7. 实验设计与实验步骤

**数据**

使用 UNB-CIC / ISCXTor2016 数据集。数据来自 Whonix 环境：workstation 侧采集 regular nonTor traffic，gateway 侧采集 Tor traffic。数据覆盖 8 类应用：Audio、Browsing、Chat、Email、FTP、P2P、VDO、VoIP。

**预处理**

按应用类型分组，构造 8 个 Tor/nonTor 二分类任务。对每个 PCAP packet，检查最高层协议：

- TLS：提取 `tls.app_data`
- SSH：提取 `ssh.encrypted_packet`
- TCP 或 proprietary protocol：提取 `tcp.data`

空 payload、连接建立/控制阶段无关包被过滤。由于 Tor 与 nonTor 样本不均衡，作者使用 undersampling 平衡类别。

**特征提取**

对每条 encrypted payload 统计 16 个 hex 字符 `0-9, a-f`：

- `F_i`：字符 `i` 的出现次数。
- `R_i`：字符 `i` 出现次数除以 payload 总字符数。

最终得到 32 个候选特征。后续更重视 Set 2，因为 Set 1 与 packet size 明显相关。

**模型/基线**

机器学习模型为：

- J48：C4.5 决策树的 Weka 实现。
- Random Forest：100 棵树，默认参数。
- IBk：kNN，默认 `k=1`，欧氏距离。

论文对比的不是复杂深度模型，而是可解释、传统、低成本分类器。

**训练**

作者使用 Weka 3.8.3 默认超参数。数据切分策略根据样本规模选择：

- 约 10000 实例以内：10-fold cross validation。
- 更大数据集：70% 训练、30% 测试。

平衡后的数据还额外划出一部分作为 unseen prediction 阶段。

**指标**

主要指标包括：

- Accuracy
- Precision
- Recall
- F1-score

统计分析阶段使用 Mann-Whitney U test，以 `p < 0.05` 判断 Tor 与 nonTor 特征分布显著不同。

**消融/敏感性**

论文实际做了一个重要对照：Set 1 频数特征 vs Set 2 比例特征。结果显示 Set 1 在 RF 上平均准确率最高，但因受 packet size 影响，作者最终偏向 Set 2。严格来说，这不是完整消融实验，但已经触及关键混杂因素：包长。

**结果核查**

可复核时应重点检查：

- 提取 payload 时是否误把未加密 TCP data 纳入。
- Tor/nonTor 是否来自同一应用类型下的可比数据。
- undersampling 是否在 train/test 切分前完成，是否引入重复或泄漏。
- unseen data 是否真正未参与模型选择。
- Set 1 的高准确率是否主要来自包长差异。
- Set 2 的分类结果是否在不同应用、不同协议、不同时间采集数据上仍稳定。

## 8. 关键结果、结论与证据

统计分析最关键结果是：8 类应用、两组特征共 256 个比较中，242 个特征在 Tor 与 nonTor 之间存在显著差异，差异率为 94.53%。这说明加密 payload 的 hex 分布并非完全不可区分。

不同应用差异强弱不一。Chat 的相似特征较多，有 10 个 ratio 特征未达到显著差异；Audio 有 3 个；P2P 只有 1 个。这暗示应用协议、样本结构和流量生成方式会影响密文统计差异。

分类方面：

- Set 1 + RF 平均准确率最高：96.53%。
- Set 1 + J48：94.71%。
- Set 1 + IBk：96.42%。
- Set 2 + J48：95.65%。
- Set 2 + RF：92.62%。
- Set 2 + IBk：73.77%。

作者最终选择更强调 Set 2 + J48，不是因为它绝对最高，而是因为它较少受 packet size 影响，更符合“基于密文字符比例而非包长”的研究主张。

J48 使用 Set 2 时，平均 precision、recall、F1-score 均约为 0.93。VoIP 表现最好，接近 100%；Audio 和 Chat 相对更困难。

unseen prediction 阶段平均准确率为 98.06%，最低 Email 为 93.36%，最高 VoIP 为 99.80%。不过这个结果需要谨慎看待，因为 unseen 数据仍来自同一平衡数据池，并不是跨数据集、跨时间、跨网络环境的真正外部验证。

论文最终结论是：单包 encrypted payload 的 hex 字符比例足以形成有效 Tor/nonTor 分类器，并且相比流级方法具有实时性、位置无关性和可解释性优势。

## 9. 局限性与待解决问题

第一，论文使用的是 UNB-CIC / ISCXTor2016。该数据集虽然经典，但采集环境、Tor 版本、应用版本、协议栈行为都可能具有年代和环境特异性。2024 年论文继续使用该数据集，外部泛化仍需新数据验证。

第二，unseen prediction 并不等同于真正独立测试集。它是从平衡数据中划出的 5% 或少量保留数据，仍可能共享同一采集环境和应用分布。模型是否能泛化到不同国家、不同 Tor 版本、不同客户端、不同出口节点、不同 TLS 实现，还没有被充分证明。

第三，Set 1 与 packet size 相关的问题被作者发现，但 Set 2 是否完全消除了长度、分段、MSS、Tor cell 重组等结构性信号，仍需更细粒度分析。比例特征降低了长度影响，但不代表只剩“加密算法差异”。

第四，论文没有充分验证因果解释。作者提出固定 512-byte cell、多层加密、加密算法参数、Tor 流量同质性等可能成功因素，但这些仍是合理猜测，不是通过控制实验逐一验证的因果结论。

第五，按应用类型分别做二分类，在工程部署中可能存在前置条件问题：真实流量中检测器未必先知道该 packet 属于 Audio、Chat 还是 FTP。如果要落地，需要测试跨应用混合场景下的统一 Tor/nonTor 分类模型。

第六，方法面对对抗性规避的鲁棒性未知。攻击者或 Tor 实现如果进行 padding、包长扰动、payload shaping、混合填充或协议混淆，hex 比例特征可能显著变化。

第七，正文包未截断，因此本次理解不受正文缺页影响。但仍建议回到 PDF 复核表格中的具体样本数量、各应用逐项指标和图示，因为正文抽取可能丢失表格排版细节。

## 10. 与本项目的关系

这篇论文与“加密流量分类与应用识别”高度相关，也可服务“AI 安全与跨域异常检测”的方法储备。

对本项目最有价值的点是：它提供了一种非常轻量的 encrypted traffic representation。相比深度学习直接吃 raw bytes，hex 字符比例特征更容易解释、部署和审计。对于异常检测项目，可以把这类特征作为基础统计视角，与 flow features、TLS handshake metadata、packet size sequence、方向序列等组合。

它尤其适合以下场景：

- 边界网关快速筛查 Tor-like encrypted payload。
- 在不保存明文、不做解密的隐私约束下进行流量侧检测。
- 对流重组不可靠、只拿到单包或采样包的监测环境。
- 作为深度模型之外的可解释 baseline。
- 用于研究“加密实现/封装机制是否泄露统计指纹”。

但若用于真实安全系统，不应单独依赖该方法。更稳妥的做法是将其作为多模态流量检测中的一组轻量特征。

## 11. 代码对照分析

本地元数据说明未发现该论文对应的开源代码包，因此无法逐文件映射到作者源码。根据论文方法，如果复现，代码目录大概率应拆成以下模块：

- 数据读取与 PCAP 解析：对应论文 Algorithm 1。功能是遍历 packet，识别 TLS/SSH/TCP/proprietary 层，提取 `tls.app_data`、`ssh.encrypted_packet`、`tcp.data`。
- 数据清洗与标签构造：按 8 个 application type 组织 Tor/nonTor 样本，过滤空 payload 和连接控制包。
- 类别平衡：对 Tor/nonTor 做 undersampling，并保留一部分 balanced data 作为 unseen prediction。
- 特征提取：对应 Algorithm 2。对 payload hex string 计算 `F_0-F_f` 和 `R_0-R_f`。
- 统计检验：对每个应用、每个特征执行 Mann-Whitney U test，输出 `p > 0.05` 的非显著特征和总差异率。
- 相关性分析：计算 Set 1/Set 2 与 packet size 的 Pearson correlation。
- 模型训练：生成 Weka 可读的 ARFF/CSV，分别训练 J48、Random Forest、IBk。
- 评估脚本：输出 accuracy、precision、recall、F1，并单独对 unseen data 做最终预测。

如果在本项目中实现复现，建议优先写成 Python pipeline：`pyshark/scapy` 解析 PCAP，`pandas` 组织特征，`scipy.stats.mannwhitneyu` 做统计检验，`scikit-learn` 复现 J48 近似模型可用 `DecisionTreeClassifier`，RF/kNN 则直接对应。若需要与论文严格一致，应导出 ARFF 后用 Weka 3.8.3 跑 J48、RF、IBk 默认参数。

## 12. 本篇精华

- 论文提出了一个单包级 Tor 检测思路：只看 encrypted payload 的 hex 字符统计，不依赖完整 flow。
- 方法的核心不是复杂模型，而是发现 Tor 与 nonTor 密文负载在字符比例上存在稳定统计差异。
- 统计检验显示 256 个特征比较中 242 个显著不同，差异率 94.53%，支撑了“密文仍有工程指纹”的判断。
- Set 1 频数特征准确率更高，但受 packet size 影响；Set 2 比例特征更适合作为论文主张的核心证据。
- J48 + Set 2 平均准确率 95.65%，说明可解释传统模型已经足够有效。
- 论文真正挑战的是“加密流量不可区分”的工程现实，而不是破解加密内容。
- 最大不足是外部泛化和因果解释不足：结果主要建立在 ISCXTor2016，同源 unseen 数据不能替代跨环境验证。
- 对异常检测项目而言，这类 hex-ratio 特征适合作为轻量、可解释、隐私友好的补充特征。

## 13. 建议精读路线

建议先读 Introduction，抓住两个研究问题 RQ1 和 RQ2，因为整篇论文都是围绕“能否区分”和“能否单包高效区分”展开。

第二步读 Dataset、Data Cleansing 和 Feature Extraction。重点看作者如何定义 encrypted payload，尤其是 TLS、SSH、TCP/proprietary 三类 payload 的提取逻辑。这里决定了实验是否干净。

第三步读 Statistical Analysis。重点不是 Mann-Whitney U 的公式，而是哪些应用和哪些 hex ratio 特征没有显著差异，这能帮助判断方法在不同应用上的稳定性。

第四步读 Machine Learning Results。建议特别比较 Set 1 和 Set 2，而不是只看最高准确率。Set 1 的高分可能混入包长信号，Set 2 才更接近论文真正想证明的“密文比例指纹”。

最后读 Discussion。这里作者给出了成功原因解释，但要带着怀疑读：固定 cell、多层加密、协议参数、Tor 流量同质性都合理，但还不是被完全验证的因果机制。