# [088] Open-CyKG: An Open Cyber Threat Intelligence Knowledge Graph

## 1. 基本信息
- 题名：Open-CyKG: An Open Cyber Threat Intelligence Knowledge Graph  
- 中文题名：Open-CyKG：开放式网络威胁情报知识图谱  
- 作者：Injy Sarhan, Marco Spruit  
- 年份与来源：2021，Knowledge-Based Systems，DOI：10.1016/j.knosys.2021.107524  
- 关键词：Cyber Threat Intelligence, Knowledge Graph, Named Entity Recognition, Open Information Extraction, Attention network  
- 代码：已下载，[source/Open-CyKG](<F:\泉城实验室\二期\论文\异常检测\source\Open-CyKG>)  
- 正文包：本次正文包未截断。  
- 相关性判断：对“异常检测”主线是弱相关，更偏威胁情报结构化、APT 报告知识抽取、知识图谱构建，适合放在“安全文本智能与知识图谱辅助分析”综述背景中。

## 2. 中文翻译与核心摘要
这篇论文要解决的不是传统流量异常检测或主机行为检测，而是“安全报告太多、太散、难查询”的问题。作者提出 Open-CyKG，用开放信息抽取从非结构化 APT 报告中抽取三元组，再用网络安全 NER 给实体打标签，最后通过词向量聚类做实体融合，构建可在 Neo4j 中查询的 CTI 知识图谱。

核心思路可以概括为：不用预定义关系集合，也不强依赖已有本体，而是先让 OIE 从句子中抽出 `<实体1, 关系, 实体2>`，再用 NER 判断哪些词是 malware、application、hash、OS、vendor、relevant term 等安全实体，最后把表达不同但语义接近的实体合并，减少图谱中的冗余与歧义。

## 3. 论文解决的具体问题
论文针对三个很具体的痛点：

1. APT 报告和安全公告主要是非结构化文本，安全分析师难以快速检索“某类恶意软件做了什么”“攻击者如何使用某技术”等事实。
2. 既有网络安全关系抽取常要求预定义关系或本体，例如只抽 vulnerability-product-vendor 这类关系，容易漏掉开放场景下的新关系、新行为和新攻击描述。
3. 直接把抽取结果放进知识图谱会出现大量重复、歧义和低质量事实，例如同一实体有多种写法，或者 OIE 抽出了语法上完整但安全意义较弱的三元组。

## 4. 创新点深度提炼
- 首次把 OIE 作为网络安全 CTI 知识图谱的核心抽取器，目标是摆脱固定关系集合限制。
- 将 OIE、NER、KG canonicalization 串成一条完整流水线，而不是只做一个文本分类或实体识别组件。
- OIE 模型把词、POS、谓词三路输入拼接，用序列标注方式抽取重叠三元组，并加入 attention 让模型更关注对关系抽取有贡献的词。
- NER 不只是独立任务，而是服务于 KG 构建：用于给节点加属性、过滤无安全实体标签的低价值三元组。
- 用上下文化词向量和层次凝聚聚类做实体融合，尝试缓解开放抽取知识图谱常见的实体重复和语义漂移问题。
- 论文不仅报告 OIE/NER 指标，还用 Cypher 查询示例说明知识图谱能返回面向分析师的问题答案。

## 5. 科学问题与研究假设
论文背后的科学问题是：开放式信息抽取能否在安全领域生成足够可靠的结构化威胁情报，并进一步组织成可查询的知识图谱？

主要研究假设包括：

- APT 报告中的安全行为可以被表示为开放三元组，不必预先枚举所有关系类型。
- attention 能提升神经 OIE 对谓词、实体边界和关键动作词的捕捉能力。
- Bi-GRU 在小规模、长句、安全文本场景下能以较少参数获得比 Bi-LSTM 更好的效果。
- 网络安全 NER 标签能帮助 KG 过滤无意义三元组，并为查询提供类型约束。
- 上下文化 embedding 加 HAC 聚类能够把语义相同或相近的实体归并，从而改善图谱查询召回。

## 6. 科学方法与技术路线
技术路线是三阶段：

1. OIE：把 MalwareDB/APT 报告句子转成 BIO 序列标注任务。输入为词向量、POS 向量、谓词向量拼接，经过双向循环网络、attention、TimeDistributed Dense 和 SoftMax，输出 Entity、Action、Modifier 等标签，再恢复为三元组。
2. NER：使用微软安全公告数据集和 CTI 报告数据集训练安全实体识别模型。网络为 Embedding + Bi-GRU + TimeDistributed Dense + CRF，输出安全实体类别。
3. KG 构建与融合：把 OIE 三元组映射为图中头节点、边、尾节点；把 NER 标签作为节点属性；去除无安全实体标签的低价值三元组；用上下文化词向量平均表示实体，再用 cosine distance + complete-linkage HAC 聚类；每个簇选代表实体，形成 canonicalized KG。

## 7. 实验设计与实验步骤
可复核流程如下：

1. 数据：OIE 使用 MalwareDB，源自 39 篇 APT 报告，原有 6819 句，作者筛出 1910 个信息性句子；NER 使用 Microsoft Security Bulletins 5072 句和 CTI malware 报告 3450 句。
2. 预处理：去掉只有 O 标签、没有关系标签或只有单实体的句子；OIE 按 BIO 标注 Entity/Action/Modifier；提取 POS 和 predicate；NER 按句子分组并 padding。
3. 模型/基线：OIE 对比 Sarhan 早期 Bi-GRU、Stanovsky Bi-LSTM、Bi-LSTM+Attention、Bi-GRU+Attention；NER 对比 Bridges 手工启发式、Kim/Simran 的 Bi-LSTM-CRF/BOC/CNN 结构。
4. 训练：OIE 实验 GloVe、BERT、XLNet、XLM-RoBERTa；最终表中最佳 OIE 为 Bi-GRU+Attention+XLM-RoBERTa。NER 使用 80/20 划分、训练集 0.1 验证、五折交叉验证。
5. 指标：OIE 和 NER 用 recall、precision、F-measure；canonicalization 用 macro、micro、pairwise precision/recall/F1。
6. 消融/敏感性：OIE 去掉 attention 后 F1 从 59.4% 降到 56.8%；作者还指出模型对 epoch、batch size 敏感，并用 grid search 调参。
7. 结果核查：最终不仅看抽取指标，还在 Neo4j 中执行两类查询：围绕 malware 的泛查询，以及 attackers 与 watering hole attacks 的限定查询，检查 canonicalization 是否带来更多有效返回。

## 8. 关键结果、结论与证据
- OIE 最佳结果：Open-CyKG Bi-GRU+Attention 使用 XLM-RoBERTa，Recall 57.2%，Precision 61.8%，F1 59.4%。相比无 attention 的 Bi-GRU F1 提升 2.6 个百分点。
- NER 在 Microsoft Security Bulletins 上很强：Bi-GRU+CRF F1 98.9%，明显高于手工启发式 77.8%。
- NER 在 CTI 报告上更现实：Bi-GRU+CRF F1 79.8%，高于 Simran BOC 的 75.1% 和 CNN 版本的 75.0%。
- 对 MalwareDB 抽样人工标注验证时，NER 在 MSB 训练模型上 F1 86.6%，在 CTI 训练模型上 F1 82.9%，说明跨数据集迁移可用但不完美。
- canonicalization 的 macro F1 为 82.6%、micro F1 为 81.7%，但 pairwise precision 只有 54.7%、pairwise F1 64.8%，说明聚类能提高召回和覆盖，但仍会把部分不应合并的实体合并。
- 论文最重要的结论不是“模型指标绝对很高”，而是证明开放抽取 + 安全 NER + 实体融合可以形成一个可查询的 CTI KG 原型。

## 9. 局限性与待解决问题
- OIE 训练数据很小，1910 个信息性句子不足以支撑复杂安全语义抽取，F1 59.4% 说明三元组质量仍是瓶颈。
- 论文没有端到端评估 KG 对真实安全分析任务的帮助，例如分析师检索准确率、调查耗时下降、事件响应收益等。
- canonicalization 的 pairwise precision 偏低，实体融合存在过度合并风险；这在安全场景中可能引入错误事实链。
- NER 与 OIE 使用的数据源不同，跨语料迁移存在标签体系和文本风格不一致问题。
- 查询示例偏少，只展示两个 Cypher 查询，尚不能证明图谱在复杂攻击链推理、TTP 关联、漏洞-样本-组织映射中的可靠性。
- 代码包更像研究 notebook，不是一键复现实验工程；依赖旧版 Keras、keras_contrib、Colab/Drive 路径，工程可复现性有限。
- 正文包未截断，但图 5、图 6、图 10 的视觉细节仍建议回到 PDF 复核，特别是 Neo4j 查询返回样例。

## 10. 与本项目的关系
如果本项目主线是异常检测，这篇论文的直接相关性不强，因为它不建模异常分数、检测边界或时序行为。但它可作为异常检测系统的知识增强模块：把安全报告中的 malware、attack technique、tool、vulnerability、indicator 结构化，辅助解释异常告警、补全威胁上下文、生成调查查询。

更适合借鉴的是“告警/报告文本到知识图谱”的方法，而不是模型指标本身。例如，可以把异常检测输出的 IP、hash、进程名、漏洞编号作为 KG 查询入口，关联 APT 报告中的攻击行为和缓解线索。

## 11. 代码对照分析
代码仓库主要文件如下：

- [README.md](<F:\泉城实验室\二期\论文\异常检测\source\Open-CyKG\README.md>)：说明模型、数据来源、依赖和引用；明确代码在 Google Colab GPU 上实现，数据需按论文引用自行准备。
- [Open_CyKG_OIE_Model.ipynb](<F:\泉城实验室\二期\论文\异常检测\source\Open-CyKG\Open_CyKG_OIE_Model.ipynb>)：对应论文 OIE 模块。包含 `load_dataset`、`load_dataset_encodeinputs`、predicate/POS/word 三路输入、Flair embedding、attention、TimeDistributed Dense、SoftMax 评估代码。需要注意：notebook 中模型单元同时出现 `stack_latent_layers` 的 GRU 写法和实际 `Bidirectional(LSTM(...))` 调用，和论文最佳 Bi-GRU+Attention 描述不完全一致，复现实验时要手动校正。
- [Open_Cy_KG_NER.ipynb](<F:\泉城实验室\二期\论文\异常检测\source\Open-CyKG\Open_Cy_KG_NER.ipynb>)：对应 NER 模块。代码结构是句子聚合、词/标签索引、padding、Embedding、Bi-GRU、TDD、CRF、训练和五折验证；另有 Bi-LSTM 对照实验。
- [Open_CyKG__Knowledge_Graph_Canonicalization.ipynb](<F:\泉城实验室\二期\论文\异常检测\source\Open-CyKG\Open_CyKG__Knowledge_Graph_Canonicalization.ipynb>)：对应 KG 构建、三元组整理、embedding 生成、HAC 聚类和 macro/micro/pairwise 评估。代码中保留了 Colab 路径和占位注释，需要用户补数据路径、标签列表和 Neo4j 导入环节。
- [KG_goldStandard](<F:\泉城实验室\二期\论文\异常检测\source\Open-CyKG\KG_goldStandard>)：包含 `KG_phase_1.csv` 与 `KG_phase_2.csv`，是 token 级 KG 构建/评估中间数据，字段包括 `finalSentID, FinalWord, finalNER, finalPOS, finalTrueLabel`。
- [NER_CS/NER_Eval_data.csv](<F:\泉城实验室\二期\论文\异常检测\source\Open-CyKG\NER_CS\NER_Eval_data.csv>)：包含 NER 评估/合并结果，字段有 `finalNER, NERpredicted1, NERpredicted2`，能看出两个 NER 数据源预测被合并到最终标签。

总体看，源码对应论文方法是清楚的，但不是生产级仓库：没有完整 requirements、没有原始数据、没有统一入口脚本，复现需要在 notebook 中补路径、补标签列表、选择 embedding 并修正模型结构。

## 12. 本篇精华
- Open-CyKG 的核心价值在于“开放关系抽取”，它避免把安全知识限制在少数预定义关系中。
- 论文把 NER 从单独实体识别任务变成 KG 质量控制工具，用于节点标注、三元组过滤和查询约束。
- OIE 的 precision 比 recall 更重要，因为错误事实进入 KG 后会污染查询结果和后续推理。
- attention 带来实证增益，但 OIE F1 仍只有 59.4%，说明开放式安全三元组抽取远未解决。
- canonicalization 能提升查询覆盖，但 pairwise precision 低，实体融合仍是开放 KG 的高风险环节。
- 这篇更适合作为“威胁情报知识图谱构建”论文，而不是异常检测算法论文。
- 代码证明作者释放了实验线索，但复现门槛不低，尤其是 Colab 路径、旧 Keras/CRF 依赖和 notebook 内部结构不一致。
- 对综述写作来说，它可以作为“从非结构化 CTI 到可查询图谱”的代表性开放抽取方案。

## 13. 建议精读路线
1. 先读 Introduction 和 Related Work，抓住它和传统 RE/ontology-based KG 的差异：它强调开放抽取。
2. 再读 Section 3，重点画出 OIE、NER、KG canonicalization 三段流水线，尤其是 OIE 输入特征和 KG 融合逻辑。
3. 精读 Table 2、Table 4、Table 5、Table 7：这些表决定论文证据强弱，尤其要注意 OIE 分数并不高。
4. 对照代码读三个 notebook：先 OIE，再 NER，最后 canonicalization；不要直接运行，先修正路径、依赖和 Bi-GRU/Bi-LSTM 不一致问题。
5. 最后看 Fig. 10 查询示例，把它理解为“可检索 CTI 原型展示”，不要过度解读为完整安全推理系统。

<!-- codex-cli-deep-read: complete -->
