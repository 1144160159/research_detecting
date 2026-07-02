# [014] Machine learning based encrypted traffic classification: Identifying SSH and Skype

## 1. 基本信息

- 论文题名：Machine learning based encrypted traffic classification: Identifying SSH and Skype
- 作者：Riyad Alshammari, A. Nur Zincir-Heywood
- 年份：2009
- 会议：IEEE Symposium on Computational Intelligence for Security and Defense Applications
- DOI：10.1109/cisda.2009.5356534
- 主题定位：加密流量分类、应用识别、跨网络泛化、流级统计特征
- 任务对象：SSH vs non-SSH；Skype vs non-Skype
- 核心限制：不使用 IP 地址、端口号、payload 内容
- 代码状态：未发现该论文对应的本地开源代码

## 2. 中文翻译与核心摘要

这篇论文研究的是：在不能看明文 payload、不能依赖端口号、也不使用 IP 地址的情况下，机器学习是否仍能识别加密应用流量，并且模型是否能从一个网络泛化到另一个完全不同的网络。

作者选择 SSH 和 Skype 作为代表。SSH 代表典型加密远程登录、隧道和文件传输场景；Skype 代表专有、P2P、VoIP、可穿越 NAT/防火墙的复杂加密应用。论文不是只追求同一数据集上的高准确率，而是强调 robustness：用 Dalhousie 校园网数据训练，再在 AMP、MAWI、DARPA99 等不同来源的完整流量上测试。

方法上，论文使用 NetMate 将原始流量转换为双向 flow，并提取包数、字节数、持续时间、正反向 inter-arrival time、包长统计等流级特征。分类器包括 AdaBoost、SVM、Naive Bayes、RIPPER 和 C4.5。实验结果显示，C4.5 在真实网络数据上的 SSH 和 Skype 识别整体最稳定，说明即使不依赖 payload 和端口，加密应用仍会在流级统计行为中留下可学习模式。

## 3. 论文解决的具体问题

论文要解决的不是普通“流量分类”问题，而是三个约束叠加后的应用识别问题：

1. 加密导致 payload 不可见  
   SSH、Skype 等应用隐藏了内容层语义，传统 DPI 或 payload signature 方法失效。

2. 端口号不可靠  
   应用可以使用非标准端口、动态端口，甚至复用常见端口逃避检测，因此基于 IANA 端口的识别容易失效。

3. 训练网络与测试网络不同  
   许多流量分类论文在同源数据上训练和测试，容易高估性能。本文强调法证分析和实际部署场景：模型往往在一个网络训练，却要用于另一个网络。

因此，具体问题可以表述为：

> 仅凭流级统计特征，机器学习模型能否在跨网络条件下可靠地区分 SSH/Skype 与非 SSH/非 Skype 流量？

## 4. 创新点深度提炼

1. 把“跨网络鲁棒性”作为核心评价对象  
   论文最有价值的地方不是提出新模型，而是把训练集和测试集放在不同网络上。Dalhousie、AMP、MAWI、DARPA99 的 TCP/UDP 比例、流量规模和采集环境差异很大，这比同源交叉验证更接近真实部署。

2. 主动排除高偏置特征  
   IP、端口、payload 都被排除。这样做牺牲了短期准确率，但提高了结论的泛化意义。尤其端口号在公开数据标注中被用作弱标签，但不进入模型特征，这是本文设计上的关键区分。

3. 将 SSH 与 Skype 同时纳入加密流量研究  
   SSH 相对规整，Skype 则具有 P2P、VoIP、NAT 穿越、UDP/TCP 混合等复杂行为。两者共同出现，使论文不只是“SSH 检测”实验，而是尝试验证流级统计方法对不同加密应用的适用性。

4. 强调可解释模型的部署价值  
   C4.5 和 RIPPER 不只是效果较好，还能形成决策树或规则。论文提到 C4.5 生成 13 条 SSH 规则、使用 14 个特征；RIPPER 生成 11 条 SSH 规则、使用 15 个特征。这对网络管理员部署和审计很重要。

5. 用 DR/FPR 而非总准确率作为主指标  
   作者明确指出，在类别不平衡场景下 overall accuracy 可能误导。例如 SSH 只占 10% 时，全判为 non-SSH 也能有 90% accuracy。因此本文关注 Detection Rate 和 False Positive Rate，更符合安全检测任务的评价习惯。

## 5. 科学问题与研究假设

科学问题可以拆成几层：

1. 加密应用是否仍具有稳定的流级行为指纹？
2. 这种指纹是否不依赖某个网络的地址、端口或主机结构？
3. 哪类机器学习模型更适合从统计流特征中学习这种指纹？
4. SSH 与 Skype 这两类行为差异很大的加密应用，是否都能被同一类特征体系识别？

论文隐含的研究假设包括：

- H1：加密隐藏的是内容，不会完全抹除通信行为模式。
- H2：包长、方向、持续时间、正反向时延等 flow statistics 能承载足够的分类信息。
- H3：去掉 IP、端口和 payload 后，模型更可能学到跨网络稳定规律。
- H4：决策树和规则模型比部分黑盒或强假设模型更适合该任务。
- H5：Skype 比 SSH 更难稳定识别，因为它的通信模式更复杂，且依赖 P2P/VoIP 行为。

## 6. 科学方法与技术路线

论文技术路线很清晰：

1. 收集多源网络流量  
   包括 Dalhousie 校园网、AMP、MAWI、DARPA99。

2. 构造标签  
   Dalhousie 使用 PacketShaper 深度分类工具标注；AMP、MAWI 使用端口标注；DARPA99 使用端口标注，并用 SSH handshake 验证 SSH 标签。

3. 生成 flow  
   使用 NetMate。flow 是双向的，第一个包方向定义为 forward。TCP flow 通过正常连接关闭或 600 秒 timeout 结束；UDP 通过 timeout 结束。

4. 提取流级统计特征  
   包括协议、flow duration、正反向包数、正反向字节数、正反向 inter-arrival time 的 min/mean/max/std、正反向包长的 min/mean/max/std 等。

5. 构造平衡训练样本  
   SSH 训练样本来自 Dalhousie，共 12,246 条 flow，其中 SSH 和 non-SSH 各 6,123。Skype 训练样本共 60,000 条，Skype 与 non-Skype 平衡。

6. 训练多种分类器  
   使用 Weka 默认参数，模型包括 C4.5、RIPPER、AdaBoost、SVM、Naive Bayes。

7. 跨网络测试  
   训练主要在 Dalhousie 样本上完成，测试在完整 Dalhousie、AMP、MAWI、DARPA99 或 Dalhousie Skype 测试数据上进行。

8. 使用 DR 和 FPR 评价  
   DR 衡量目标应用识别率，FPR 衡量非目标应用被误判为目标应用的比例。

## 7. 实验设计与实验步骤

可复核流程如下。

1. 数据准备  
   - Dalhousie：337,041,778 个包，约 213,562 MB。
   - AMP：332,064,652 个包，约 188,435 MB。
   - MAWI：76,543,335 个包，约 28,718 MB。
   - DARPA99：16,723,835 个包，约 3,638 MB。
   - SSH 完整 flow 数：Dalhousie 19,384；AMP 427,448；MAWI 19,016；DARPA99 72,094。
   - Skype 只在 Dalhousie 表中出现，完整 trace 中 Skype flow 为 8,664,137。

2. 预处理  
   - 用 NetMate 从包级 trace 生成双向 flow。
   - TCP timeout 设为 600 秒。
   - 不保留 IP 地址、源/目的端口、payload。
   - 只保留流级统计特征。
   - Dalhousie 数据已匿名化，payload 被截断到 IP header 末尾。

3. 训练样本构造  
   - SSH：从 FTP、SSH、DNS、HTTP、MSN 中随机采样，构造 6,123 SSH + 6,123 non-SSH。
   - Skype：从 FTP、SSH、MAIL、DNS、HTTP、HTTPS、Random UDP 等类别采样，构造 60,000 条平衡样本。

4. 模型与基线  
   - C4.5：Weka 中通常对应 J48。
   - RIPPER：Weka 中通常对应 JRip。
   - SVM：Weka 中通常对应 SMO。
   - Naive Bayes。
   - AdaBoost，弱分类器为简单决策桩一类方法。

5. 训练  
   - 先在 Dalhousie 训练样本上做 10-fold cross validation。
   - 再用 Dalhousie 训练样本训练模型。
   - 将训练好的模型应用到完整 trace 或独立测试数据。

6. 指标  
   - DR：目标类被正确识别比例。
   - FPR：非目标类被误判为目标类比例。
   - 不以 overall accuracy 为主，因为数据极度不平衡。

7. 消融/敏感性  
   论文没有严格做现代意义上的 ablation，例如逐个去除包长、时延、方向特征，也没有调参敏感性分析。它的“对照”主要来自：
   - 不同分类器对照；
   - 不同网络测试对照；
   - SSH 与 Skype 两类应用对照；
   - 训练集交叉验证与跨网络测试对照。

8. 结果核查  
   复现实验时应重点核查三件事：
   - 标注来源是否一致，尤其 AMP/MAWI 的端口弱标签会引入噪声。
   - flow timeout、双向 flow 定义是否与论文一致。
   - DR/FPR 是否按目标类单独计算，不能只看 accuracy。

## 8. 关键结果、结论与证据

SSH 识别中，C4.5 在真实网络 trace 上整体最稳。

- Dalhousie 完整 trace：C4.5 对 SSH 的 DR 为 95.9%，FPR 为 2.8%。
- AMP：C4.5 对 SSH 的 DR 为 97.2%，FPR 为 0.8%。
- MAWI：C4.5 对 SSH 的 DR 为 82.9%，FPR 为 0.5%。
- DARPA99：SVM 对 SSH 表现最好，DR 为 99.8%，FPR 为 3.7%；C4.5 在 DARPA99 上为 83.3% DR、1.1% FPR。

这说明 C4.5 并非每个数据集都绝对最优，但在真实网络数据上的综合表现更好。DARPA99 是模拟网络，作者也因此更看重 Dalhousie、AMP、MAWI 上的结果。

Skype 识别中，C4.5 也表现突出：

- Skype Dal Training Sample 的 10-fold CV：C4.5 对 Skype 的 DR 为 97.8%，FPR 为 1.9%。
- 在测试数据上：C4.5 对 Skype 的 DR 为 98.4%，FPR 为 7.7%。

Skype 的检测率很高，但误报率明显高于 SSH。这符合直觉：Skype 的 P2P 和 VoIP 行为可能与其他 UDP、实时通信或交互型应用在流级统计上相似。

总体结论是：

> 不看 payload、不看 IP、不看端口，仅使用流级统计特征，也能对 SSH 和 Skype 加密流量进行有效识别；其中 C4.5 在跨网络真实 trace 上最具实用性和可解释性。

## 9. 局限性与待解决问题

1. 标签质量存在天然风险  
   AMP 和 MAWI 使用端口标注，而论文的核心动机之一正是端口不可靠。这会形成一个矛盾：模型不使用端口作为特征，但测试标签仍部分依赖端口。若真实应用使用非标准端口，标签可能错。

2. Skype 实验的跨网络证据不足  
   SSH 在 Dalhousie、AMP、MAWI、DARPA99 上都有测试；Skype 主要在 Dalhousie 数据上做训练和测试。由于 Skype 行为强依赖网络环境和版本，实现真正跨网络鲁棒性还需要更多 trace。

3. 没有系统特征消融  
   论文没有回答哪些特征最关键。例如包长统计、方向性、IAT、duration 各自贡献多少，仍不清楚。

4. 使用 Weka 默认参数  
   默认参数方便比较，但不能说明每个模型已达到最佳。SVM、AdaBoost 对参数敏感，默认设置可能压低了它们的潜力。

5. 数据年代较早  
   2009 年的 SSH、Skype 和网络应用生态与今天差异很大。尤其 Skype 协议、加密实现、NAT 穿越策略和流媒体行为都可能变化。

6. 对攻击者适应性考虑不足  
   如果应用或攻击者主动做流量混淆、padding、时延扰动、流切分，基于统计特征的分类器可能退化。

7. 图中规则细节需要回到 PDF 复核  
   本次正文包未截断，但正文文本中 Fig. 1 和 Fig. 2 的 C4.5/RIPPER 具体规则内容没有完整呈现。若要复现可解释规则或写规则级分析，需要回到原 PDF 查看图像细节。

## 10. 与本项目的关系

这篇论文与“异常检测”项目的关系很强，但它本身更准确地说是加密流量应用识别，而不是异常检测。

它对项目有三点直接价值：

1. 特征层面可复用  
   flow duration、正反向包数、字节数、包长统计、IAT 统计是异常检测中常见且稳定的基础特征。它们不依赖 payload，适合加密流量场景。

2. 问题设置具有跨域意义  
   训练网络与测试网络不同，本质上是 domain shift。异常检测项目如果要部署到不同园区、不同链路、不同业务网络，也会遇到同样问题。

3. 评价指标更贴近安全任务  
   论文强调 DR/FPR，而不是 accuracy。这对异常检测尤其重要，因为异常样本少，accuracy 往往没有意义。

需要注意的是，本文是监督式二分类；若本项目关注未知攻击、零日异常或开放集识别，还需要引入无监督、半监督、开放集或 OOD 检测方法。

## 11. 代码对照分析

本论文未发现对应本地开源代码包，因此不能把论文方法映射到真实源码文件。下面是基于论文内容的复现实验代码结构线索，不是现成源码说明。

如果复现，合理的代码目录可以对应为：

- `data/`  
  存放 Dalhousie、AMP、MAWI、DARPA99 原始 trace 或转换后的 flow 文件。

- `preprocess/flow_extract.*`  
  对应论文中的 NetMate 流生成步骤。关键参数是 bidirectional flow、TCP timeout 600 秒、UDP timeout、去除 IP/端口/payload。

- `features/schema.*`  
  对应 Table II 的流级特征定义，包括 protocol、duration、正反向 packets/bytes、IAT 统计、packet length 统计。

- `labels/build_labels.*`  
  对应 Dalhousie 的 PacketShaper 标签、AMP/MAWI 的端口标签、DARPA99 的端口加 SSH handshake 校验。

- `sampling/make_training_samples.*`  
  对应 SSH 的 12,246 条平衡样本和 Skype 的 60,000 条平衡样本。

- `models/train_weka.*`  
  对应 Weka 默认参数训练。C4.5 可用 J48，RIPPER 可用 JRip，SVM 可用 SMO，另有 NaiveBayes 和 AdaBoost。

- `eval/metrics.*`  
  对应 DR/FPR 计算，必须按目标类分别计算，不能只输出 accuracy。

复现时最关键的不是模型代码，而是数据处理一致性：flow 切分、标签来源、特征字段顺序、缺失值处理和训练/测试网络划分。

## 12. 本篇精华

1. 论文最核心贡献是把加密流量分类放到跨网络泛化条件下评估，而不是只在同一数据集内做高准确率实验。

2. 不使用 IP、端口、payload 后，SSH 仍能通过 flow statistics 被较好识别，说明加密隐藏内容但不完全隐藏通信行为。

3. C4.5 在 Dalhousie、AMP、MAWI 等真实网络上表现稳定，SSH 检测可达到约 82.9% 到 97.2% DR，FPR 约 0.5% 到 2.8%。

4. Skype 检测率可达 98.4%，但 FPR 约 7.7%，说明复杂 P2P/VoIP 加密应用比 SSH 更容易与其他流量混淆。

5. 论文反对只用 overall accuracy，因为流量分类高度不平衡，DR/FPR 才更符合安全检测需求。

6. C4.5 和 RIPPER 的价值不仅是性能，还在于能产出网络管理员可理解的规则。

7. 本文的弱点在于标签仍部分依赖端口、缺少特征消融、Skype 跨网络验证不足、且数据年代较早。

8. 对现代异常检测项目而言，这篇论文提供了一个经典基线：payload-free、port-free、flow-based、cross-network evaluation。

## 13. 建议精读路线

1. 先读 Introduction  
   把握作者为什么同时排除 payload、端口和 IP，以及为什么强调 robustness。

2. 再读 Related Work  
   重点看作者如何区分自己与 payload signature、port-based、host-behavior、早期 encrypted traffic classification 的差异。

3. 精读 Methodology 的 Data Collection  
   这里决定实验可信度。尤其要注意不同数据集的标签来源并不完全一致。

4. 精读 Feature Selection  
   建议把 Table II 的特征整理成自己的复现字段表，这是后续实现和综述引用的关键。

5. 精读 Experiments and Result  
   不要只看最高数值，要比较 C4.5、RIPPER、SVM 在不同网络上的稳定性。

6. 回看 Conclusion  
   关注作者对“robust generic solutions”的表述，同时保留批判：Skype 部分仍是 preliminary results。

7. 最后回到 PDF 查看 Fig. 1 和 Fig. 2  
   正文包中图像规则没有完整展开；如果要分析 C4.5/RIPPER 具体判别逻辑，必须复核原图。

<!-- codex-cli-deep-read: complete -->
