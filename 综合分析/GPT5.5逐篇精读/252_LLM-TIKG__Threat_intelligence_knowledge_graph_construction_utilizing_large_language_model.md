# [252] LLM-TIKG: Threat intelligence knowledge graph construction utilizing large language model

## 1. 基本信息
- 题名：LLM-TIKG: Threat intelligence knowledge graph construction utilizing large language model
- 中文题名：LLM-TIKG：利用大语言模型构建威胁情报知识图谱
- 年份 / 来源：2024，Computers & Security
- DOI：10.1016/j.cose.2024.103999
- 作者机构：上海交通大学、国网浙江电科院
- 主题归类：威胁情报、知识图谱、大语言模型、TTP 分类
- 相关性判断：对“异常检测”不是直接建模论文，但对告警解释、威胁狩猎、攻击归因和异常事件语义增强有参考价值。

## 2. 中文翻译与核心摘要
这篇论文的核心目标是把非结构化开源威胁情报报告转成可查询、可关联的威胁情报知识图谱。作者认为传统 IoC 收集只得到 IP、域名、哈希等低层碎片，难以表达攻击者、恶意软件、工具、漏洞、攻击行为和 TTP 之间的关系。

LLM-TIKG 的做法是：先用 GPT-3.5 的 few-shot 能力生成实体关系标注和数据增强样本，再用 LoRA 指令微调 Llama2-7B，让较小模型完成主题分类、实体关系抽取、TTP 分类，最后把抽取结果融合进 Neo4j 图谱。论文最有价值的地方不是“用了大模型”，而是把攻击行为句子映射到 MITRE ATT&CK TTP，使知识图谱从 IoC 关联上升到攻击过程和技术意图层面。

## 3. 论文解决的具体问题
论文针对的是 OSCTI 报告难以直接用于检测与防御的问题。安全厂商博客、CISA 公告、研究报告通常是长文本，里面混合了攻击者、恶意软件、工具、文件、哈希、域名、漏洞、攻击链描述和背景叙事。

作者指出三类具体困难：一是威胁实体边界模糊，例如工具、攻击类型、攻击者别名容易混淆；二是高质量标注数据缺乏，传统 NER/RE 训练成本高；三是已有知识图谱工作偏向实体和关系，忽略“side-load DLL”“inject shellcode”等攻击行为描述，导致 TTP 这种高层语义丢失。

## 4. 创新点深度提炼
- 用 GPT 生成和扩增训练数据：把 GPT-3.5 当作标注辅助者，而不是直接部署为抽取系统，降低人工标注成本。
- 用小模型本地化执行：通过 LoRA 微调 Llama2-7B，在隐私、成本和可部署性上比直接调用闭源大模型更现实。
- 把 TTP 纳入知识图谱：从攻击行为句子中抽取 MITRE ATT&CK Technique / Sub-technique，使图谱不只连接 IoC，还连接攻击战术语义。
- 引入报告主对象：将报告的 main object 作为实体属性或关系补强依据，缓解 PowerShell、C2 server 等通用节点导致的关系混淆。
- 重视数据质量而非单纯规模：1600 条人工修正数据微调出的 NER 精度优于 15000 条粗标数据，说明大模型微调对噪声标签非常敏感。
- 将提示词设计作为实验变量：论文展示了更严格的实体类型说明、排除“其他类型”、单独定义 threat type 后，GPT 标注质量明显改善。

## 5. 科学问题与研究假设
核心科学问题是：大语言模型能否减少威胁情报知识图谱构建对人工标注和规则工程的依赖，同时保留足够准确的安全领域语义？

论文隐含了几条研究假设：GPT 的 few-shot 能力可以生成可用的威胁情报标注；少量高质量标注比大量噪声标注更适合指令微调；Llama2-7B 经过 LoRA 后能学习威胁实体、关系和 TTP 的领域边界；TTP 分类可以把难以实体化的攻击行为转化为标准化图谱节点；知识图谱中的共享工具、技术、哈希和攻击链可服务威胁狩猎与归因。

## 6. 科学方法与技术路线
技术路线分三段。

第一段是数据构建。作者从 Symantec、Fortinet、TrendMicro、CISA、Sophos、TheHackerNews、KrebsonSecurity 等来源爬取威胁情报报告，保留标题、链接、正文和段落结构。随后用 GPT-3.5 按“instruction + examples + input”提示词生成主题分类、实体关系抽取数据；TTP 分类数据来自 MITRE ATT&CK malware examples 和 TRAM，并用回译与 GPT 改写扩增。

第二段是模型微调。作者使用 Llama2-7B，采用 LoRA 指令微调。训练格式是 instruction、input、output。实体关系抽取任务中，提示词还包含实体类型示例，以减少幻觉和类型漂移。

第三段是图谱构建。流程是先判断报告是否属于威胁情报，再输出主对象；报告末尾 IoC 列表用正则补抽；正文按 section 抽取实体关系；当主对象是 malware 或 attacker 时，对句子做 TTP 分类并连接到主对象；最后对实体和关系做规则合并与基于词向量、HAC 聚类的融合。

## 7. 实验设计与实验步骤
可复核流程如下：

1. 数据：收集约 1.25 万篇开源安全内容，论文中 4.1 写 12,545，4.4 写 12,542，数量存在小不一致。
2. 预处理：清理广告、侧栏和空行，保留段落 / 小节结构；标题和首段用于主题判断；长 section 按输入长度切分；报告末尾 IoC 用正则处理。
3. 数据集：主题分类 2000 条；实体关系抽取 15000 条粗标和 1600 条人工修正；TTP 分类 38,946 条。
4. 模型 / 基线：NER 对比 BERT-CRF、GPT-3.5、GPT-4、不同数据规模微调的 Llama2-7B；TTP 对比 TTPDrill、TRAM、LLaMA Technique、LLaMA Sub-technique。
5. 训练：Python 3.9，2 × RTX 3090，最大学习率 1e-4，最多 10 epochs；实体关系抽取最大长度 1024 tokens，其余任务 512 tokens。
6. 指标：NER 用 Precision、Recall、F1；TTP 因含负样本，增加 Accuracy。
7. 消融 / 敏感性：比较粗标 15000 与人工修正 1600；比较提示词改进前后；比较不同 epoch；比较 Technique 与 Sub-technique 粒度。
8. 结果核查：在全量真实报告上构建 Neo4j 图谱，并用 Shuckworm、PivNoxy、BlackSuit / Royal Ransomware 案例检验图谱是否能表达攻击链和相似性。

## 8. 关键结果、结论与证据
NER 结果中，LLaMA-1600 的 Precision 达 87.88%，Recall 83.99%，F1 85.89。它的精度高于 BERT-CRF、GPT-3.5、GPT-4 和 LLaMA-15000，但 F1 并非所有设置下最高：改进提示词后的 GPT-4 在表 5 中 F1 达 89.98。这说明论文最强证据是“高质量微调提升精度和可部署性”，而不是绝对 F1 全面领先。

TTP 分类结果更强。LLaMA-Tec Accuracy 97.47%，Precision 96.53%，Recall 99.95%，F1 98.21；Sub-technique 粒度下降到 Accuracy 83.60%、F1 87.50，说明细粒度 ATT&CK 标签仍然更难。TTPDrill 和 TRAM 在大类别覆盖下表现较弱，反映规则或传统分类器面对大量 Technique 时扩展性不足。

真实数据实验中，模型把 9681 篇文章判为威胁情报报告，最终抽取 50,745 个实体和 64,948 条关系。案例图显示，Shuckworm 可关联到恶意软件、工具和 IoC；PivNoxy 的文档诱导、文件加载、自注入等攻击过程可被图谱表达；BlackSuit 与 Royal Ransomware 通过共同技术、哈希和 Conti 关系体现相似性。

## 9. 局限性与待解决问题
正文包标注为未截断，因此本次理解不受正文缺失影响。

主要局限在于：第一，实体关系抽取仍受 GPT 标注噪声影响，安全组织被误识别为攻击者、泛称词被抽成实体等问题需要规则和人工修正。第二，长文本、表格、IoC 列表对 Llama2-7B 仍不友好，论文也承认 hash 和 domain 容易漏抽。第三，TTP 分类是闭集分类，未覆盖或样本稀缺的 Technique 会受到训练集分布影响。第四，知识图谱融合仍依赖启发式规则和 HAC 聚类，别名合并、关系规范化和通用工具节点消歧没有彻底解决。第五，案例研究偏展示型，缺少对威胁狩猎、攻击归因下游任务的定量提升评估。第六，论文没有给出主题分类性能，也没有充分说明 NER 测试集规模、跨来源划分和潜在数据泄漏控制。

## 10. 与本项目的关系
如果本项目主线是网络异常检测，这篇论文不是直接的异常检测模型论文：它不处理流量时间序列、系统日志异常评分或在线检测阈值。

它的价值在于异常检测之后的语义增强。异常检测系统发现可疑 IP、进程、文件、域名或行为后，可以借助类似 LLM-TIKG 的图谱把底层告警关联到 malware、attacker、tool、vulnerability、TTP，从而支持告警解释、攻击链重建、威胁狩猎优先级排序和归因线索生成。对综述写作而言，它适合放在“知识图谱与威胁情报辅助异常检测”或“LLM for cyber threat intelligence”小节。

## 11. 代码对照分析
本地元数据给的目录 `source\LLM-TIKGdataset` 不存在，但实际可读目录是 `source\LLM-TIKG-dataset`。该目录不是完整代码仓库，而是数据集发布包。

可见文件包括：`README.md`、`entity&relationship.json`、`fig/prompt.png`、`fig/dataStructure.png`。核心文件 `entity&relationship.json` 约 1.88 MB，共 1762 行，每行是一个 JSON 样本，字段为 `instruction`、`input`、`output`；其中 `input` 为 null，`instruction` 实际放的是报告句子或段落，`output` 包含 `Named Entities` 和 `Relationships`。

它对应论文中的“实体与关系抽取数据集”，尤其接近作者手工修正的那部分数据。它不包含爬虫、主题分类数据、TTP 分类数据、LoRA 微调脚本、BERT-CRF 基线、TRAM/TTPDrill 复现实验、Neo4j 导入、实体融合或 HAC 聚类代码。因此不能把它当成可一键复现 LLM-TIKG 的源码，只能作为实体关系抽取微调样本使用。若要复现论文，需要自行补齐：NDJSON 读取、指令模板包装、Llama2-7B LoRA 训练、输出解析、IoC 正则抽取、图数据库写入和评估脚本。

## 12. 本篇精华
- LLM-TIKG 的真正贡献是把 OSCTI 从“文本和 IoC 列表”推进到“实体-关系-TTP 图谱”。
- GPT 在论文中主要承担标注和增强角色，最终部署目标是本地微调的 Llama2-7B。
- TTP 分类是本文相对威胁情报图谱旧工作的关键增强，因为它保留了攻击行为语义。
- 数据质量比数据规模更关键：1600 条人工修正样本优于 15000 条粗标样本。
- LLaMA-Tec 在 Technique 分类上表现很强，但 Sub-technique 粒度仍明显下降。
- NER 结果要谨慎解读：LLaMA-1600 精度最高，但改进提示词后的 GPT-4 F1 更高。
- 代码包实际是数据集包，不是完整复现实验工程。
- 对异常检测项目而言，它最适合作为告警知识增强和攻击链解释模块，而不是检测器本身。

## 13. 建议精读路线
先读 Introduction 和 Fig. 1，抓住作者为什么认为 IoC 不够、为什么 TTP 必须进图谱。然后读 3.2 到 3.4，重点画出“GPT 标注 → LoRA 微调 → 分段抽取 → TTP 分类 → 图谱融合”的流程。接着精读 Tables 2-5，尤其注意数据质量实验和 Technique / Sub-technique 的差异。最后读 Case Study，把 PivNoxy 和 BlackSuit/Royal 的图谱用法转化成你自己项目里的“异常告警如何被解释和关联”的思路。代码包只需重点看 `entity&relationship.json` 的样本格式，它能帮助理解论文的实体关系输出长什么样。

<!-- codex-cli-deep-read: complete -->
