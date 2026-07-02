# [560] TIMFuser: A multi-granular fusion framework for cyber threat intelligence

## 1. 基本信息

- 论文：TIMFuser: A multi-granular fusion framework for cyber threat intelligence
- 作者：Chunyan Ma 等
- 来源：Computers & Security, 148, 104141
- DOI：10.1016/j.cose.2024.104141
- 时间：元数据年份为 2024；论文在线发表时间为 2024-10-04，期刊卷期标注为 2025
- 主题：网络威胁情报、TTP、攻击行为抽取、多源情报融合、攻击技术识别
- 本地代码状态：未发现该论文对应开源代码包

## 2. 中文翻译与核心摘要

这篇论文提出 TIMFuser，一个面向网络威胁情报的多粒度融合框架。它要解决的不是单篇 CTI 报告里的 IOC 抽取，而是从大量非结构化 CTI 报告中抽取攻击行为、识别 ATT&CK 攻击技术，并在“攻击行为粒度”和“攻击技术粒度”上融合来自多源报告的碎片化信息。

论文的核心判断是：APT 攻击活动通常被多个安全厂商、组织或博客在不同时间、不同视角下披露。单个报告只能看到局部 TTP，导致威胁狩猎或攻击图构建时信息不完整，进而带来较高误报。TIMFuser 试图把同一攻击活动下多份报告中的攻击行为和攻击技术聚合起来，形成更完整的攻击视图。

整体流程包括六步：多源数据采集、文本预处理、相关信息识别、攻击图抽取、攻击技术识别、攻击技术融合。方法上，论文最重要的部分是两个融合：一是攻击行为融合，引入结构、语义和侧信息做实体规范化；二是攻击技术融合，用集合关系和相似性分析合并不同来源披露的 TTP 及其 usage。

## 3. 论文解决的具体问题

论文瞄准的是多源非结构化 CTI 的自动化融合问题，具体包括：

1. 单源 CTI 视角碎片化  
   现有系统常从单篇报告抽取 TTP 或攻击行为，但同一攻击活动的信息分散在多个来源中。SolarWinds 示例中，不同厂商分别披露 PowerShell、浏览器凭据窃取、任务创建、数据外传等不同侧面，单看任何一个来源都不完整。

2. 低层 IOC 难以表达攻击语义  
   哈希、IP、域名等 IOC 时效短、易变化，无法稳定描述攻击者的行为模式。论文强调 TTP 和攻击行为比 IOC 更适合支撑 APT 检测与威胁狩猎。

3. 非结构化 CTI 报告噪声大、文本长  
   报告中有广告、团队介绍、背景描述等无关内容，并且很多报告超过 BERT/RoBERTa 常见的 512 token 输入限制。因此需要先识别安全相关长文本，再识别与攻击行为直接相关的句子。

4. 攻击行为抽取存在实体歧义和重复  
   例如 APT29、UNC2452、Cozy Bear 指向同一攻击者；Sibot backdoor 和 Sibot 可能指同一实体。仅用编辑距离容易把 CVE-2021-44228 和 CVE-2021-44227 误合并，也可能把 APT28 和 APT29 错合并。

5. 缺少公开的多源攻击活动融合数据集  
   作者因此构建并标注了长文本分类、相关句识别、实体簇、SolarWinds 攻击活动报告等数据，用于验证各子任务。

## 4. 创新点深度提炼

1. 多粒度融合视角  
   论文不是只抽取 IOC，也不是只做 ATT&CK 技术分类，而是同时在攻击行为层和攻击技术层做融合。攻击行为层解决实体、动作、依赖关系的规范化；攻击技术层解决多来源 TTP 集合的合并与 usage 聚合。

2. 面向 CTI 报告的完整流水线  
   TIMFuser 覆盖从爬取、清洗、长文本分类、相关句识别、SRL 抽取、攻击图构建、Graph2vec 技术识别到技术集合融合的端到端流程。虽然仍是 pipeline，但比只做单点抽取的工作更贴近实际分析流程。

3. 攻击行为融合引入侧信息和嵌入学习  
   它借鉴 CESI 思路，不只看字符串相似度，而是结合形态归一化、实体链接、WordNet 词义消歧、IDF token overlap、动作关联规则等侧信息，再通过嵌入学习和 HAC 聚类完成 canonicalization。

4. 将攻击技术识别建模为子图匹配  
   作者先从 CTI 中构建攻击图，再用 Graph2vec 表示报告攻击图和 ATT&CK 技术图，通过图嵌入距离判断某个技术图是否匹配到攻击活动图中。这使技术识别同时利用语义和结构信息。

5. 攻击技术融合使用集合关系区分互补、包含和重复  
   对不同来源披露的技术集合，论文用 Jaccard 和 contained similarity 区分无交集、部分重叠、包含、完全相同四类情况，并同步合并对应攻击行为 usage，减少重复同时保留关键细节。

## 5. 科学问题与研究假设

核心科学问题可以概括为：

- 如何从噪声大、篇幅长、表达不规范的非结构化 CTI 报告中抽取可靠攻击行为？
- 如何判断不同报告中的实体、动作或攻击行为是否指向同一真实语义对象？
- 如何把多源报告中的局部 TTP 合并成一个更完整的攻击活动视图？
- 这种融合后的攻击视图是否比单源或字符级融合方法更准确、更有利于下游威胁狩猎？

论文隐含的研究假设包括：

1. 多源 CTI 之间存在互补关系，同一攻击活动的完整 TTP 视图无法由单一来源充分覆盖。
2. 攻击行为的完整性是攻击技术识别质量的前提。
3. 仅使用字符相似度不足以完成 CTI 实体融合，必须结合结构、语义和安全领域侧信息。
4. 攻击技术可以被看成攻击行为图中的模式，图嵌入匹配比单纯文本分类更适合识别结构化 TTP。
5. 技术集合的融合可以降低重复信息，同时保留多来源披露的 usage 证据。

## 6. 科学方法与技术路线

TIMFuser 的技术路线是一个六阶段 pipeline：

1. 多源异构数据采集  
   一路从 MITRE ATT&CK 抓取 procedure examples 和外部引用；另一路从互联网 CTI 来源中基于种子 URL 和 BFS 抓取报告。论文使用 Selenium 渲染网页、BeautifulSoup 解析内容，并用 pdfplumber、html2text 等工具转换文本。

2. 数据预处理  
   包括特殊字符移除、攻击指标还原、被动句转主动句、句子和词分割、主语省略补全、显式/隐式共指消解。隐式共指依赖安全领域词典，例如 C2/C&C/Command and Control 归一，动词 download/read/gather 等映射到系统动作。

3. 相关信息识别  
   长文本层面用 Longformer 判断报告是否与攻击活动相关；句子层面用 RoBERTa-large + BiLSTM + multi-head self-attention 判断句子是否包含攻击行为细节。

4. 攻击图抽取  
   使用 SRL 识别“谁对谁做了什么”，再通过规则保留系统实体和系统动作，最后根据系统调用方向推断信息流方向，形成 subject-action-object 攻击行为三元组和攻击图。

5. 攻击行为融合  
   对 subject、object、action 引入侧信息，学习嵌入，使用 HAC 聚类，将等价实体和动作合并为代表项，再合并多源子图。

6. 攻击技术识别与融合  
   用 Graph2vec 表示攻击图，将技术识别看作技术图与报告攻击图的子图匹配；随后用集合论和相似度度量融合不同来源的 ATT&CK 技术集合及其 usage。

## 7. 实验设计与实验步骤

可复核流程如下：

1. 数据  
   - 长文本分类数据：516 篇攻击活动相关报告，223 篇无关报告。
   - 相关句识别数据：14204 个句子，其中 10748 个相关、5179 个无关。这里论文数字加和超过 14204，疑似表述或排版存在不一致，复核原 PDF 时应关注。
   - 攻击行为融合：人工标注 1221 个实体 gold clusters。
   - 真实攻击活动案例：SolarWinds 相关 11 篇 CTI 报告，来自 FireEye、Volexity、CrowdStrike、MSTIC、SecureWorks、Mandiant、NCSC、CheckPoint 等来源。

2. 预处理  
   - 清洗 HTML、图片和特殊字符。
   - 还原 hxxp、[.] 等被改写 IOC。
   - 被动句转主动句。
   - NLTK 分句和分词。
   - 省略主语补全。
   - NeuralCoref 做显式共指。
   - 安全领域词典做实体和动词隐式归一。

3. 模型与基线  
   - 长文本相关性：Longformer 对比 BERT 截断、BERT+TextRank、BERT+Random、ToBERT。
   - 句子相关性：RoBERTa-large + BiLSTM + attention 对比 SVM、MLP、fastText、TextCNN、BiLSTM。
   - 攻击行为融合：对比 Sarhan and Spruit、AttacKG、Guo et al. 的方法。
   - 攻击图抽取：对比 EXTRACTOR、AttacKG。
   - 攻击技术识别：对比 AttacKG。
   - 攻击技术融合：对比 T1 直接合并、T2 去重、TIMFuser 融合。

4. 训练  
   - 长文本分类：mini-batch size 4，50 epochs，Cross Entropy，Adam，学习率 3e-5。
   - 句子分类：序列长度 150，Adam，学习率 5e-5，RoBERTa-large 作为编码器。
   - 攻击行为融合：GloVe 初始化嵌入，训练 pairwise ranking loss，加入侧信息约束和 L2 正则，再 HAC 聚类。

5. 指标  
   - 分类任务：Precision、Recall、F1。
   - 实体/行为融合：macro、micro、pairwise 的 Precision、Recall、F1。
   - 攻击图抽取和技术识别：报告级 F1。
   - 技术融合：融合后技术数量、行为数量，以及代表性技术的时间跨度和关联行为分析。

6. 消融与敏感性  
   - 句子识别中，attention 相比 BiLSTM 提升 F1 约 2.31%。
   - 攻击行为融合中移除任一侧信息都会降低 macro/micro/pairwise F1；IDF token overlap 影响最大，micro F1 降低约 3.72%。
   - 训练 epoch 增加后 F1 上升并稳定。
   - HAC 阈值在 0.1 到 0.6 范围内测试，阈值 0.1 最优。

7. 结果核查  
   - 需要重点核查表 8、表 9、表 10、表 11。
   - 表 10 显示 TIMFuser 在实体、依赖、技术识别上均明显高于基线。
   - 表 11 显示直接合并 80 个技术，去重后 61 个，TIMFuser 仍为 61 个技术，但攻击行为 usage 从 421 降到 263，说明它不只是去重技术名，还压缩和关联了行为证据。

## 8. 关键结果、结论与证据

1. 相关长文本识别  
   Longformer 在长 CTI 报告分类中优于截断或分段 BERT 方法，F1 提升约 6.31%。这支持作者关于“长报告不能简单截断”的判断。

2. 相关句识别  
   TIMFuser 的句子识别模型达到 Precision 98.88%、Recall 99.66%、F1 99.27%，高于 SVM、MLP、fastText、TextCNN、BiLSTM。这里的性能非常高，说明数据标注边界可能较清晰，也需要关注是否存在来源分布泄漏或测试集难度不足。

3. 攻击行为融合  
   TIMFuser 在 macro F1、micro F1、pairwise F1 上分别达到 93.36%、94.66%、71.36%，相比基线分别提升 1.9%、2.74%、5.49%。pairwise F1 明显低于 macro/micro，说明细粒度 mention pair 级别仍存在误聚类或漏聚类。

4. 攻击图抽取  
   在 11 篇 SolarWinds 报告上，TIMFuser 实体识别平均 F1 为 80.39%，依赖识别平均 F1 为 95.44%，显著高于 EXTRACTOR 和 AttacKG。论文认为原因是 EXTRACTOR 会把同类非 IOC 实体过度聚合，而 AttacKG 基于字符特征容易误合并。

5. 攻击技术识别  
   TIMFuser 平均 F1 为 82.46%，高于 AttacKG 的 64.79%。证据来自表 10，作者将优势归因于图结构信息和攻击行为上下文。

6. 攻击技术融合  
   在 SolarWinds 案例中，直接合并得到 80 个技术，去重后 61 个，TIMFuser 融合后仍为 61 个技术，但 usage 数量压缩为 263。这个结果说明 TIMFuser 的价值不在增加技术数量，而在把重复或相关行为证据规范化，使每个技术背后的攻击行为更清晰。

## 9. 局限性与待解决问题

1. Pipeline 误差传播  
   TIMFuser 由多个模块串联，长文本分类、句子识别、SRL、实体规范化、图匹配任一环节出错都会影响后续结果。论文也承认实时性和端到端能力不足。

2. 真实攻击场景覆盖有限  
   深入评估主要围绕 SolarWinds 11 篇报告。SolarWinds 是典型供应链 APT 案例，但不足以证明框架对勒索软件、ICS 攻击、云攻击、移动攻击等场景同样稳定。

3. 标注数据和复现资源有限  
   论文称数据可按请求提供，本地也未发现开源代码。缺少公开代码和完整数据会影响复现，尤其是侧信息词典、爬虫种子、规则后处理、HAC 阈值等细节。

4. 句子分类结果过高，需要谨慎解读  
   相关句识别 F1 达 99.27%，在真实 CTI 语境中偏高。可能是标注任务边界较明确，也可能与数据划分方式、来源重复、模板化报告有关，复现时应做跨来源测试。

5. Graph2vec 子图匹配的解释性有限  
   图嵌入相似度能给出匹配结果，但很难直接解释是哪条攻击行为触发了某个 ATT&CK 技术判断。对安全分析师而言，可解释证据链仍然重要。

6. 大规模多源数据的时效性权衡  
   收集窗口太短会导致信息不足，窗口太长又降低 CTI 的实时价值。论文提出用种子 URL 和 BFS 平衡，但仍依赖人工维护种子和来源质量控制。

7. 正文包未截断  
   本次提供的正文包标注为未截断，因此以上理解基于完整正文包；仍建议回到 PDF 复核图表、公式排版和表格数字，尤其是相关句数据量处存在疑似不一致。

## 10. 与本项目的关系

根据已有分类，本论文属于“图学习、知识图谱与威胁情报”，与异常检测项目是弱相关但有方法借鉴价值。

它不直接提出异常检测模型，也不处理网络流量、主机日志或时序异常评分。因此如果本项目核心是流量异常检测、日志异常检测或无监督异常检测，它不是直接 baseline。

但它可以在三个方向提供支撑：

1. 威胁知识增强  
   TIMFuser 生成的融合 TTP 和攻击行为图可作为异常检测系统的先验知识或规则模板，帮助解释异常事件属于哪类 ATT&CK 技术。

2. 威胁狩猎查询图构建  
   论文明确提到，融合后的完整攻击图可与系统审计日志构建的 query graph/provenance graph 匹配，从而降低威胁狩猎误报。

3. 异常检测结果语义化  
   如果本项目检测到异常进程、文件、注册表、网络连接等事件，可以借鉴其 subject-action-object 表示，把异常事件映射到攻击行为，再进一步映射到 TTP。

## 11. 代码对照分析

本地未发现该论文对应的代码包，因此不能给出真实源码文件级对应关系。结合论文方法，如果后续找到官方或第三方实现，建议重点查找以下目录或文件类型：

1. 数据采集  
   可能对应 `crawler/`、`mitre_crawler.py`、`web_crawler.py`、`scrape_attack.py`。应包含 Selenium、BeautifulSoup、pdfplumber、html2text 相关逻辑。

2. 数据预处理  
   可能对应 `preprocess/`、`normalization.py`、`coreference.py`、`indicator_restore.py`、`dictionary.py`。重点看 IOC 还原、被动转主动、实体/动词映射词典、省略主语补全。

3. 相关信息识别  
   可能对应 `models/relevance_longformer.py`、`sentence_classifier.py`、`train_relevance.py`。应能看到 Longformer、RoBERTa-large、BiLSTM、multi-head attention、CrossEntropy、Adam 等配置。

4. 攻击行为抽取  
   可能对应 `srl/`、`attack_graph_extraction.py`、`postprocess_srl.py`。重点看 SRL 输出如何转成 `(subject, action, object)`，以及系统实体过滤和信息流方向推断规则。

5. 攻击行为融合  
   可能对应 `fusion/behavior_fusion.py`、`cesi.py`、`canonicalization.py`、`hac_cluster.py`。核心应包括侧信息构建、负采样、pairwise ranking loss、HAC 聚类、代表实体选择。

6. 攻击技术识别与融合  
   可能对应 `technique_recognition.py`、`graph2vec_match.py`、`technique_fusion.py`。重点看 ATT&CK procedure graph 如何构造、Graph2vec 如何训练、Jaccard 和 contained similarity 如何实现。

7. 评估  
   可能对应 `evaluate.py`、`metrics.py`、`ablation.py`。应包含 precision/recall/F1，以及 macro/micro/pairwise cluster evaluation。

## 12. 本篇精华

1. TIMFuser 的核心价值是把 CTI 分析从“单篇报告抽取”推进到“同一攻击活动多源报告融合”。

2. 论文强调攻击行为是 TTP 融合的基础：技术名可以重复或遗漏，但行为 usage 能提供更细粒度证据。

3. 攻击行为融合不能只靠编辑距离；APT29/UNC2452/Cozy Bear 这类别名需要实体链接、上下文嵌入和安全领域侧信息共同处理。

4. Longformer 用于报告级相关性识别，RoBERTa-large + BiLSTM + attention 用于句子级攻击行为识别，分别解决长文本和细粒度语义问题。

5. 技术识别被建模为攻击图与 ATT&CK 技术图之间的子图匹配，这是本文与普通文本分类式 TTP 识别的重要差异。

6. SolarWinds 案例表明，多源 CTI 报告之间既有重复也有互补，融合后更适合构建完整攻击图和威胁狩猎查询。

7. 论文最大短板是代码和数据开放不足、评估攻击场景偏窄、pipeline 误差传播明显。

## 13. 建议精读路线

1. 先读 Introduction 和 Motivating example  
   把握论文为什么强调多源 CTI，以及 SolarWinds 示例中“单源不完整”的实际含义。

2. 再读 Methodology 总框架图  
   重点理解六个模块之间的数据流：报告文本到相关句，再到攻击行为、攻击图、攻击技术、融合技术视图。

3. 精读 3.4 Attack graph extraction  
   这是论文技术密度最高的部分，尤其是 SRL 后处理、攻击行为融合、侧信息、CESI 目标函数和 HAC 聚类。

4. 精读 3.5 和 3.6  
   理解作者如何从攻击图走向 ATT&CK 技术识别，以及如何用集合关系合并不同来源的技术列表和 usage。

5. 对照读 Evaluation 的 Q1-Q5  
   每个问题对应一个模块的验证。建议重点看表 9、表 10、表 11，判断每个模块的证据是否支撑作者结论。

6. 最后读 Discussion  
   关注实时性、攻击场景泛化、大规模数据处理三类限制，这些也是后续复现或改进最容易切入的方向。