# [117] A framework for threat intelligence extraction and fusion

## 1. 基本信息

- 论文：A framework for threat intelligence extraction and fusion
- 作者：Yongyan Guo, Zhengyu Liu, Cheng Huang 等
- 来源：Computers & Security, 2023
- DOI：10.1016/j.cose.2023.103371
- 主题：威胁情报抽取、网络安全知识图谱、实体关系联合抽取、知识融合
- 本地 PDF：`paper/10.1016_j.cose.2023.103371.pdf`
- 正文包完整性：本次正文包未截断。
- 代码状态：未发现该论文对应的本地开源代码。

## 2. 中文翻译与核心摘要

这篇论文提出了一个面向威胁情报抽取与融合的框架，目标是从结构化和非结构化数据中抽取网络安全实体-关系三元组，并进一步融合为初步的网络安全知识图谱 CKG。

论文的核心不是单纯做 IOC 抽取，而是把威胁情报文本中的“实体是什么”和“实体之间有什么关系”一起建模。例如从漏洞描述、APT 报告、安全公告中抽取类似：

`软件 - hasVulnerability - CVE`
`威胁组织 - uses - 攻击模式`
`攻击活动 - attributedTo - 威胁组织`

作者认为传统流水线方法先做实体识别、再做关系分类，会带来两个问题：实体识别错误会传递到关系抽取；实体和关系两个任务之间的依赖被割裂。为此，论文把实体关系联合抽取转化为“多序列标注”问题：每一种关系类型对应一条 BIO 标注序列，序列中同时标出实体边界、实体类型以及该实体在关系中是 subject 还是 object。

模型结构是 BERT + BiGRU + relation-specific attention + BiGRU-CRF。知识融合部分则采用改进 Levenshtein 距离，对数字字符赋予更高编辑惩罚，以避免把 `APT28` 和 `APT29` 这类名称错误合并。

## 3. 论文解决的具体问题

论文解决的是网络安全知识图谱构建中的两个前置问题。

第一，从非结构化威胁情报文本中抽取高质量三元组。威胁情报大量存在于 CVE 描述、APT 报告、安全博客、安全公告、黑客论坛中，这些文本术语密集、实体形态特殊，并且同一句话常同时出现多个实体和多种关系。

第二，把来自不同来源的威胁情报实体进行初步融合。结构化数据如 ATT&CK、MISP、Unit 42、WatcherLab 本身已有实体和关系；非结构化文本中抽取出的实体则可能存在别名、拼写差异、命名变体。若不融合，知识图谱会出现重复节点和碎片化关系。

论文聚焦的不是攻击检测模型本身，而是为攻击溯源、威胁狩猎和安全态势感知提供结构化知识基础。

## 4. 创新点深度提炼

1. 将网络安全实体关系抽取建模为多关系序列标注  
   每个关系类型生成一条独立标签序列，使同一实体可以同时参与多种关系，缓解 overlapping relation 问题。

2. 标签同时编码实体边界和关系角色  
   BIO 标签不仅标出实体跨度，还区分 subject/object。这样模型输出的不是孤立实体，而是可直接还原为三元组的结构。

3. 引入关系感知注意力  
   同一句威胁情报文本中，不同关系关注的词不同。`hasVulnerability` 更关注软件和 CVE，`uses` 更关注攻击者和攻击技术。relation-specific attention 让模型按关系类型重新加权上下文。

4. 针对安全实体形态设计预处理  
   对 IP、MAC、Hash、URL、Email、域名、文件路径等特殊实体进行规则识别和替换，降低表面形式差异对语义学习的干扰。

5. 轻量级知识融合策略  
   作者没有直接使用 embedding-based entity alignment，而是针对初始 CKG 场景采用改进 Levenshtein 距离，尤其修正数字字符带来的误合并问题。

## 5. 科学问题与研究假设

核心科学问题是：在网络安全文本中，能否通过联合建模显著提升实体-关系三元组抽取质量，并在知识图谱初建阶段以低成本方式完成实体融合？

论文隐含了几个研究假设：

- 实体识别和关系抽取在网络安全文本中强相关，联合模型优于流水线模型。
- 同一句安全文本中可能存在多关系、多实体重叠，因此按关系类型拆分标注序列比单一序列更适合。
- 网络安全实体的特殊表面形式会干扰通用 NLP 表示，规则化替换有助于模型学习。
- 在初步 CKG 阶段，实体属性和关系不完整，基于名称相似度的轻量融合比复杂图嵌入方法更现实。
- 数字在安全实体命名中通常具有强区分性，因此编辑距离中数字修改应承担更高惩罚。

## 6. 科学方法与技术路线

整体框架分为四步：

1. 数据收集  
   收集结构化威胁情报和非结构化威胁情报。结构化来源包括 ATT&CK、MISP、Unit 42、WatcherLab 等；非结构化来源包括 CVE 描述、安全公告和 APT 报告。

2. 结构化数据处理  
   对 STIX 等格式数据做本体匹配，映射到 UCO 2.0 / STIX 2.0 参考的实体和关系体系，然后写入 Neo4j。

3. 非结构化数据联合抽取  
   文本先经过清洗、特殊实体替换、句子切分和 WordPiece 分词；随后进入 BERT-BiGRU-Attention-BiGRU-CRF 模型。模型对每一种关系分别生成标签序列，再由标签序列还原三元组。

4. 知识融合与入库  
   对不同来源实体计算改进 Levenshtein 距离。若距离低于阈值，则添加 `sameAs` 关系，形成初步 CKG。

采用的主要实体类型包括 Indicator、Threat Actor、Attack Pattern、Malware、Tool、Campaign、Course of Action、Vulnerability、Software。主要关系包括 hasProduct、hasVulnerability、uses、attributedTo、mitigates、indicates。

## 7. 实验设计与实验步骤

1. 数据  
   非结构化数据来自 CVE 漏洞描述、安全公告和 APT 报告。作者人工标注 12,680 个句子，共 67,918 个网络安全三元组。知识融合实验使用 698 个 Threat Actor 实体，并人工标注 560 条 `sameAs` 关系。

2. 预处理  
   清洗非 ASCII 字符和句首句尾空白；恢复被安全写法改写的 IP、URL、Email；用正则识别 IP、MAC、Hash、URL、Email、域名、文件名、路径等，并替换为 `sub type` 形式；使用 NLTK 分句、WordPiece 分词。

3. 模型/基线  
   主模型为 BERT + BiGRU + relation-specific attention + BiGRU-CRF。流水线基线为 RelExt。联合抽取基线包括 NovelTag、GraphRel、MultiHead。

4. 训练  
   采用 5 折交叉验证。BERT 向量维度 768，BiGRU 隐层和关系 embedding 均为 300。优化器 RMSprop，学习率 0.0001，batch size 64，dropout 0.5。

5. 指标  
   使用 Precision、Recall、F1。只有当关系类型和两个实体都完全匹配时，一个三元组才算抽取正确。

6. 消融/敏感性  
   比较不做特殊实体替换的 Model-NoSub；用 Word2Vec 替代 BERT 的 Model-W2V；用 LSTM 替代 GRU 的 Model-LSTM；去除注意力机制的 Model-NoAtt；还测试 80/20、75/25、66/34、50/50 不同训练测试划分。

7. 结果核查  
   重点核查三类结果：联合模型是否优于流水线；预处理、BERT、GRU、attention 各组件是否贡献性能；改进 Levenshtein 是否优于传统编辑距离，尤其是否减少数字型实体误合并。

## 8. 关键结果、结论与证据

联合抽取模型相较流水线模型有明显提升。RelExt 的 Precision、Recall、F1 分别为 57.04%、67.80%、61.69%；论文模型达到 82.28%、80.48%、81.37%。这说明在该数据集上，联合建模确实缓解了流水线方法的错误传播。

与其他联合抽取模型相比，论文模型也更强：NovelTag F1 为 56.05%，GraphRel 为 61.59%，MultiHead 为 70.89%，论文模型为 81.37%。作者将优势归因于针对安全语料的预处理、BERT 表示、关系特定注意力和适配重叠关系的标注方案。

消融实验显示，特殊实体替换有实质贡献：完整模型 F1 81.37%，不替换特殊实体后降到 78.86%。BERT 明显优于 Word2Vec，后者 F1 为 75.37%。GRU 略优于 LSTM，attention 带来小幅提升。

数据划分实验中，即使训练集比例降到 50%，F1 仍有 79.90%。这说明安全语料中的描述模式、术语和句法存在较强重复性，模型在较小训练集上仍能维持一定泛化。

知识融合实验中，改进 Levenshtein 优于传统 Levenshtein。关键原因是数字字符被赋予更大编辑代价，可以避免把 `APT28` / `APT29` 或仅一位不同的 IP 错误合并。

## 9. 局限性与待解决问题

论文的 CKG 仍处于“初步构建”阶段，重点在抽取和简单融合，尚未深入处理知识推理、复杂实体消歧、图嵌入和下游安全任务验证。

知识融合实验范围偏窄，只以 Threat Actor 为例，没有系统验证 Malware、Tool、Software、Vulnerability、Indicator 等实体类型上的效果。不同实体类型的命名规律差异很大，单一编辑距离策略未必通用。

改进 Levenshtein 主要解决拼写差异和数字误合并，对别名、缩写、跨语言命名、组织更名、同一工具不同家族名等复杂安全实体对齐问题能力有限。

实验没有给出按关系类型的详细性能。`hasVulnerability` 这类模式化关系可能较容易，而 `uses`、`attributedTo`、`indicates` 更依赖语境和安全知识，整体 F1 可能掩盖关系间差异。

数据集虽有 12,680 句和 67,918 个三元组，但论文没有公开完整标注数据和源码，本地也未发现代码包，复现实验需要重新实现模型和数据处理流程。

## 10. 与本项目的关系

从“异常检测”项目角度看，这篇论文属于弱相关但有可借鉴价值。

它不直接做流量异常检测、主机行为检测或日志异常检测；它解决的是威胁情报结构化问题。其价值在于为异常检测系统提供外部知识增强：例如把检测到的 IOC、CVE、软件、攻击技术、威胁组织映射到 CKG 中，辅助解释告警、关联攻击链、补充攻击上下文。

如果本项目涉及图学习或知识图谱增强异常检测，可以借鉴两点：一是用安全本体组织实体和关系，二是把非结构化安全文本转为三元组后作为图数据来源。但若项目核心是端到端异常检测算法，这篇论文只能作为威胁情报背景和知识增强模块参考。

## 11. 代码对照分析

本地未发现该论文对应开源代码，因此不能做真实源码级逐文件对照。

若按论文方法复现，合理的代码结构大致应包括：

- 数据预处理：负责 PDF/HTML/JSON 文本解析、去混淆 URL/IP/Email、特殊实体正则替换、NLTK 分句、WordPiece 分词。
- 标注转换：把 BRAT 标注转换为每个关系一条 BIO + subject/object 标签序列。
- 模型定义：实现 BERT embedding、BiGRU encoder、relation embedding、relation-specific attention、BiGRU decoder 和 CRF。
- 训练脚本：实现 5 折交叉验证、RMSprop、dropout、batch 构造和多关系遍历。
- 评估脚本：从预测标签还原三元组，并按“实体和关系全匹配”计算 Precision、Recall、F1。
- 知识融合：实现改进 Levenshtein 距离，设置 `wnum=10`、`wother=1` 和不同阈值。
- 图谱入库：将结构化 STIX 数据和抽取三元组映射到 UCO/STIX 本体后写入 Neo4j。

论文中明确出现的运行线索包括 BERT cased L-12 H768 A-12、Word2Vec GoogleNews vectors negative300、batch size 64、learning rate 0.0001、dropout 0.5、BiGRU hidden size 300、relation embedding size 300。

## 12. 本篇精华

- 论文真正解决的是 CKG 构建前端的“抽取 + 融合”，不是异常检测模型。
- 最大贡献是把安全实体关系抽取改成多关系序列标注，每个关系单独出标签序列，适合处理实体重叠。
- 标签设计很关键：BIO 负责实体边界，subject/object 标记负责三元组方向。
- 安全文本中的 IP、Hash、URL、路径等特殊实体不能直接按普通文本处理，规则替换显著提升效果。
- BERT 相比 Word2Vec 的收益来自上下文表征，适合处理 Software/Tool 等依上下文变化的实体类型。
- 改进 Levenshtein 的核心洞见是：安全实体里的数字通常是强身份信息，不能像普通字符一样低成本编辑。
- 实验结果显示联合模型 F1 81.37%，显著优于流水线 RelExt 的 61.69%。
- 论文的融合方法轻量但有限，适合初建图谱，不足以解决复杂别名和实体消歧。

## 13. 建议精读路线

1. 先读 Section 3 的框架图和实体/关系定义，明确它构建的 CKG schema。
2. 再精读 Section 3.2.2 的 tagging scheme，这是全文方法的核心。
3. 接着读 Section 3.2.3，重点理解 relation-specific attention 如何让同一句话按不同关系重新聚焦。
4. 然后读 Section 3.3，注意作者为什么不用图嵌入做融合，而选择改进编辑距离。
5. 最后读 Section 4 的实验表格，重点比较 Table 1、Table 2、Table 3 和 Fig. 4，判断每个模块是否真的贡献性能。