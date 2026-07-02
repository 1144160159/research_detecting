你是使用 GPT-5.5 的资深网络安全与异常检测论文精读助手。请真正阅读下面提供的论文正文包和代码包，理解后输出一篇中文深度解析 Markdown。

重要要求：
1. 不要用模板化空话，不要说“程序自动抽取显示”。你需要像研究员读完论文后写读书笔记一样表达。
2. 必须围绕正文内容提炼：具体问题、创新点、科学问题、研究假设、科学方法、实验步骤、关键结论、局限与待解决问题。
3. 如果代码包存在，请把论文方法与代码目录、关键文件、运行线索对应起来，指出哪些源码文件可能对应数据预处理、模型、训练和评估。
4. 如果正文包被截断，必须在“局限性与待解决问题”中说明：本次理解基于提供的正文包，仍需回到 PDF 复核被截断部分。
5. 不要长篇复制英文原文。可以短引极少量关键词，但主体必须是中文理解和分析。
6. 输出必须是完整 Markdown，且必须包含下面 13 个二级标题，标题文字不得改名。
7. “实验设计与实验步骤”要写成可复核流程：数据、预处理、模型/基线、训练、指标、消融/敏感性、结果核查。
8. “本篇精华”要给出 5-8 条高密度要点，能直接服务综述或科研汇报。

必须使用的文档结构：
# [248] KnowCTI: Knowledge-based cyber threat intelligence entity and relation extraction
## 1. 基本信息
## 2. 中文翻译与核心摘要
## 3. 论文解决的具体问题
## 4. 创新点深度提炼
## 5. 科学问题与研究假设
## 6. 科学方法与技术路线
## 7. 实验设计与实验步骤
## 8. 关键结果、结论与证据
## 9. 局限性与待解决问题
## 10. 与本项目的关系
## 11. 代码对照分析
## 12. 本篇精华
## 13. 建议精读路线

元数据：
编号：248
题名：KnowCTI: Knowledge-based cyber threat intelligence entity and relation extraction
年份：2024
DOI：10.1016/j.cose.2024.103824
来源：Computers & Security
PDF：paper/10.1016_j.cose.2024.103824.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：无
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\248.txt
- 原始字符数：70931
- 本次发送字符数：70931
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Computers & Security 141 (2024) 103824

Contents lists available at ScienceDirect

Computers & Security
journal homepage: www.elsevier.com/locate/cose

KnowCTI: Knowledge-based cyber threat intelligence entity and relation
extraction
Gaosheng Wang a,b , Peipei Liu a,b , Jintao Huang a,b , Haoyu Bin a,b , Xi Wang a,b,∗ , Hongsong Zhu a,b
a Institute of Information Engineering, Chinese Academy of Sciences, Beijing, China
b School of Cyber Security, University of Chinese Academy of Sciences, Beijing, China

A R T I C L E

I N F O

Keywords:
Cyber threat intelligence
Entity and relation extraction
Knowledge graph
Attention mechanism
Graph attention network

A B S T R A C T
Structured cyber threat intelligence enables security researchers to know the occurrence of cyber threats in
time, thereby improving the eﬃciency of security defense and analysis. Previous works usually use general
deep learning and NLP techniques to extract intelligence. Such methods suﬀer from insuﬃcient semantic
understanding in the ﬁeld of security. To address these issues, we propose a novel method called Knowledgebased Cyber Threat Intelligence Entity and Relation Extraction (KnowCTI), which incorporates cybersecurity
knowledge into the model to enhance the understanding of the realm of cybersecurity and has a full picture of
threats with the threat intelligence graph generation. Speciﬁcally, we ﬁrst build a cybersecurity knowledge base
and train cybersecurity-aware knowledge embeddings based on the base. Secondly, we reﬁne the most related
knowledge triples by attention mechanism and gate mechanism, and then construct a sentence tree through these
triples. Next, we employ graph attention networks to incorporate knowledge information into the sentence by
considering the sentence tree as a graph. Finally, we consider entity extraction as a sequence labeling problem
and relation extraction as a classiﬁcation problem to decode the entities and relation triples according to the
threat intelligence ontology we designed. Experimental results demonstrate the superior performance with the
F1 score exceeding 90.16 and 81.83 on entity and relation extraction separately.

1. Introduction
The number of disclosed security vulnerabilities has been steadily increasing recently. Within the multitude of security vulnerabilities, the
proportion of high-risk vulnerabilities has been consistently rising (h3c,
2023). This trend exacerbates the severity of various novel forms of
vulnerability exploitation and attack methods, such as Advanced Persistent Threat (APT) attacks, posing a more pronounced impact on
the cybersecurity environment (secrss, 2023). Consequently, it imposes
higher demands on threat detection and defense. Traditional protection methods primarily employ defensive mechanisms like ﬁrewalls and
intrusion detection systems, strategically positioned at boundaries or
critical nodes. However, these methods are ineﬀective against complex
attacks and new vulnerabilities since they deeply rely on prior features, rules, and knowledge (Mitchell and Chen, 2014; Thimma et al.,
2015). Researchers must consistently identify emerging vulnerabilities
and threats to update their conﬁgurations. To address the limitations
of current defense measures, security experts have proposed the adoption of Cyber Threat Intelligence (CTI), encompassing comprehensive
threat information and Indicator of Compromise (IoC) (Samtani et al.,
2020). By leveraging CTI, researchers can attain a thorough comprehension of threats and transition from conventional passive defense to
active defense strategies (Zhao et al., 2020).
A substantial volume of open-source threat intelligence is available on the Internet, manifesting in diverse forms across public media
such as technology blogs, community forums, and social media. These
sources disseminate threat-related information with extensive coverage
and notable timeliness, signiﬁcantly contributing to threat warning and
defense eﬀorts. Consequently, security organizations are progressively
extracting CTIs from security-related text available on the Internet. This
allows them to comprehensively understand existing or imminent cyber
threats and develop precise defense capabilities to augment the capabilities of existing security protection equipment (Li et al., 2022), which
has sparked the interest of security experts in delving deeper into research on CTI extraction.

* Corresponding author at: Institute of Information Engineering, Chinese Academy of Sciences, Beijing, China.
E-mail addresses: wanggaosheng@iie.ac.cn (G. Wang), liupeipei@iie.ac.cn (P. Liu), huangjintao@iie.ac.cn (J. Huang), binhaoyu@iie.ac.cn (H. Bin),
wangxi@iie.ac.cn (X. Wang), zhuhongsong@iie.ac.cn (H. Zhu).
https://doi.org/10.1016/j.cose.2024.103824
Received 29 January 2024; Received in revised form 5 March 2024; Accepted 23 March 2024
Available online 28 March 2024
0167-4048/© 2024 Elsevier Ltd. All rights reserved.

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.

In recent years, numerous studies have focused on CTI extraction.
The trajectory of research on CTI extraction has evolved from extracting simple intelligence to more intricate forms. Existing research can
be broadly categorized into rule-based and learning-based approaches.
Initial eﬀorts primarily concentrated on rule-based methods. These
methods extract IoC with regular formalities through the application
of predeﬁned rules (Burger et al., 2014; Liao et al., 2016). Nevertheless, these methods are limited to extracting basic threat intelligence,
such as IP addresses and hashes, and are incapable of identifying unregulated complex entities, such as attacker names and attack methods.
Additionally, certain studies employ entity dictionaries in conjunction
with grammatical rules to identify complex and previously unseen security entities. These approaches heavily rely on dictionaries and lack
generalizability. With the advancements in deep learning and Natural
Language Processing (NLP) techniques, researchers endeavored to treat
CTI extraction as an information extraction task (Long et al., 2019; Liu
et al., 2022; Wang et al., 2020), aiming to extract more intricate intelligence entities such as attackers, tools, compromised organizations, etc.
In addition to extracting intelligence entities, few researchers are focusing on attack graphs to achieve a global understanding of attacks (Guo
et al., 2021; Li et al., 2022). The utilization of deep learning models
has progressed from the initial Word2Vec+BiLSTM-based model to the
current pre-trained large language model, exempliﬁed by BERT. However, existing approaches encounter two limitations. First, whether it is
Word2Vec or a pre-trained language model, they lack an understanding
of the cybersecurity domain semantics. Second, current research mainly
focuses on extracting intelligence entities but seldom extracts relations
between entities which could provide a comprehensive overview of security intelligence.
In response to these limitations, the paper introduces KnowCTI, a
knowledge-based Cyber Threat Intelligence Entity and Relation Extraction method that incorporates relevant cybersecurity knowledge into
the text to enhance the comprehension of security-related content and
extracts intelligence entities and relations that could be used to construct threat intelligence graphs and have a full picture of threats. In order to fuse cybersecurity knowledge, we collect structured cybersecurity
data published on the Internet and extract knowledge triples to build
the cybersecurity knowledge base ﬁrst. Then we train cybersecurityaware knowledge embeddings on the cybersecurity knowledge base
by introducing cybersecurity semantic information. For entity and relation extraction, we design a CTI ontology that deﬁnes the concepts
used in threat knowledge graphs and their relationships, providing a
framework for modeling entities and relationships. Secondly, we select
related knowledge triples from the cybersecurity knowledge base according to the given sentence and construct the sentence tree. Next,
we consider the sentence tree as a graph and fuse the knowledge information based on graph attention networks (GAT). Leveraging the
integrated knowledge information, KnowCTI extracts intelligence entities and the relation triples, which could be used to construct a threat
intelligence graph to provide a comprehensive representation of security intelligence. The contributions can be summarized as follows:

Fig. 1. An example of expert reading process.

full picture of the threat. Also, we collect a large amount of reports
and explored the attack trends and attack organization proﬁling.
2. Background
2.1. Motivation
In the process of human reading, ordinary individuals can only
comprehend words based on their context, whereas experts can make
inferences with pertinent cybersecurity knowledge while reading text
from the cybersecurity domain. Inspired by this, we propose the insertion of knowledge triples into security text, incorporating knowledge
information to enhance the representations whose goal is to leverage domain-speciﬁc knowledge and integrate it into the text, thereby
improving the understanding of cybersecurity text and ultimately empowering CTI extraction capabilities.
Experts understand which products the CVE vulnerability may aﬀect
and the attack methods attackers may employ, but models lack such an
ability. For instance, in the text “POWRUNER was delivered using a malicious RTF ﬁle that exploited CVE-2017-0199”, it is describing how an
attack tool named POWRUNER, utilizing the vulnerability, was transmitted to a target system through a speciﬁc ﬁle. As illustrated in Fig. 1,
experts reading this text will incorporate relevant knowledge to better comprehend the text and infer that POWRUNER is an attack tool.
While a cybersecurity expert ﬁnds it easy to understand such text, machines struggle as they lack knowledge about CVE and RTF. Hence, the
incorporation of security knowledge into the model will signiﬁcantly
enhance performance. Achieving KnowCTI entails addressing the following challenges.
2.1.1. Cybersecurity-aware knowledge embedding representations
Current methods train knowledge embeddings on knowledge bases
through translation-based or neural network methods (Ji et al., 2021).
However, these methods are task-independent and domain-irrelevant.
In other words, the embeddings generated by these methods lack
cybersecurity-speciﬁc semantic information. To address this, we introduce cybersecurity-aware knowledge embedding representations for the
security domain.
To incorporate security domain semantic information into knowledge embeddings, it is essential to capture the text context in which the
knowledge entity is situated. For each knowledge entity, we initially
conduct a search for cybersecurity reports related to it using a search
engine. Subsequently, we ﬁlter sentences containing the knowledge
entity. To grasp the security context, we employ an additional cybersecurity text binary classiﬁcation task, training a classiﬁcation model to
discern whether the text is related to cybersecurity. So that we could
obtain initial knowledge entity embeddings by the classiﬁcation model,
which would be used for training knowledge embeddings based on the
translation-based method. Consequently, we could train cybersecurityaware knowledge embeddings using cybersecurity-related reports. The
detailed introduction will be provided in Section 4.2.

• We design a knowledge ontology about cyber threat intelligence
that could help operators have a full picture of cyber threats. Based
on the ontology, we could construct the threat intelligence graph
by extracting these entities and relations.
• We propose to incorporate external cybersecurity knowledge into
the model to augment the understanding of cybersecurity text. We
propose the cybersecurity-aware knowledge embedding method to
introduce cybersecurity semantics to knowledge embedding. To
tackle the knowledge noise issue, we propose the knowledge denoising mechanism.
• Experimental results demonstrate that our method achieves great
performance. KnowCTI could achieve a 90.16 F1 score on entity
extraction and an 81.83 F1 score on relation extraction. Given a
report, we could generate the threat intelligence graph to give a
2

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.

Fig. 2. Knowledge insertion and sentence tree construction.

2.1.2. Knowledge fusion into cybersecurity text
Eﬀective utilization of knowledge positively impacts the model’s
performance. Conversely, improper use of knowledge can lead to counterproductive outcomes (Liu et al., 2020). The introduction of knowledge has the potential to bring knowledge noise comprising irrelevant
triples or erroneous information, which may deviate from the original
intended meaning of the text. An entity in the security knowledge base
may possess multiple knowledge triples; however, not all of them contribute to text understanding. It is crucial for the model to select the
most relevant knowledge triples to enhance text understanding.
The attention mechanism (Vaswani et al., 2017), inspired by human cognitive processes, enables models to dynamically concentrate
on speciﬁc elements within input sequences, providing them with the
capability to comprehend complex dependencies and generate contextually relevant and coherent language. The attention mechanism has
played a pivotal role in catalyzing a paradigm shift in NLP and deep
learning, particularly in the context of the Transformer architecture.
For this reason, we employ attention mechanisms to denoise knowledge and fuse knowledge. Since knowledge is typically represented by
triples while text is sequential, knowledge embeddings and word embeddings have distinct embedding spaces leading to the heterogeneous
embedding space problem, where we solve this problem by employing
linear transformation to convert them into the same space.
We ﬁrst select related knowledge triples to construct the sentence
tree as shown in Fig. 2 where we consider it as a graph intuitively.
Then we employ the GAT (Ren et al., 2023) to incorporate the knowledge node information into the cybersecurity text. The GAT introduced
a learnable attention mechanism that allocates weights between each
source and target node, allowing nodes to decide which neighboring
node is more important when aggregating messages from local neighbors, rather than aggregating information from all neighbors with the
same weight. It can essentially choose important information fusion.
The detailed introduction will be provided in Section 4.3.

Fig. 3. Threat intelligence knowledge ontology.

UCO (Syed et al., 2016) in the ﬁeld of cyber threat intelligence. These
standards are crucial for cybersecurity as they enable security teams to
understand and respond to threats more quickly. While constructing the
ontology, we fully consider these speciﬁcations. The ontology is shown
in Fig. 3.
Each threat entity contains the entity type and its deﬁnition. The
knowledge ontology proposed in this study is limited within CTI. In this
work, we design 13 entity types: Threat-Actor, Security-Team, Campaign, Attack-Method, Attack-Purpose, Vulnerability, Tool, Asset, Indicator, Location, Identity, Feature, Time, and the detailed explanation of
each entity is shown in Table 1. Each entity type may contain several
sub-classes as needed. For example, “Identity” could contain “Individuals”, “Organizations”, “Groups” and “Industry”.
In a knowledge graph, each entity is a node and the relations between entities construct the edge. Data pertaining to knowledge graphs
are expressed as (subject, relation, object) triples, denoted as (𝑠, 𝑟, 𝑜),
signifying the existence of a relation denoted by the label 𝑟 between the
subject 𝑠 and object 𝑜 within the graph. Semantic relationships between
entities play a crucial role which could provide a comprehensive understanding of a threat while isolated entities could not. Table 2 illustrates
the relations we design between entities. We design 11 relation types:
“locate-at”, “discover”, “launch”, “target”, “attack-purpose”, “suﬀer”,
“use”, “has”, “aﬀect”, “indicate”, “and active-time”. Each relation type
may contain several sub-classes as needed, for example, “attack-target”
could contain “target-identity”, and “target-location”.

2.2. Preliminaries
A singular threat indicator cannot provide a comprehensive understanding of the threat. The knowledge graph could oﬀer a comprehensive perspective on the threat landscape, enabling operators to observe
the interconnections among various entities, including threat actors, indicators, vulnerabilities, and incidents. This heightened visibility assists
researchers in identifying patterns and comprehending the broader context of threats. At the core of this knowledge graph lies the ontology
(Ren et al., 2022), serving as the foundational element for the structured representation and analysis of threat-related data.
The ontology is meticulously crafted to reﬂect the intricacies of the
cyber threat intelligence domain. Entities and relations are designed to
oﬀer a structured framework for capturing, interpreting, and utilizing
threat-related data. The selection of these elements draws from both
industry standards and the practical needs of cyber threat intelligence
professionals.
In the realm of cybersecurity, there are many standard speciﬁcations such as Common Attack Pattern Enumerations and Classiﬁcations (CAPEC) (CAPEC, 2023), Common Weakness Enumeration (CWE)
(CWE, 2023), Common Vulnerabilities and Exposures (CVE) (CVE,
2023), etc. The representative speciﬁcations are STIX (STIX, 2023), and

3. Overview
KnowCTI consists of 4 major modules as shown in Fig. 4: Construct Cybersecurity Knowledge Base, Cybersecurity-aware Knowledge
Embedding, Knowledge Fusion, and Decoder.
To implement KnowCTI, the initial step is to construct a cybersecurity knowledge base. Fortunately, there is a wealth of structured cybersecurity data on the Internet, including sources like opencve (OpenCVE,
2023), malvuln (Malvuln, 2023), ATT&CK (ATT&CK, 2023), etc. We
collect a large amount of data and extract triples to establish an initial
cybersecurity knowledge base.
To ensure cybersecurity semantics for entity embedding, we introduce a cybersecurity-aware knowledge embedding training method.
Initially, we obtain entity embedding representations from open cybersecurity text data containing the entity. Subsequently, we train the
embedding representations on the knowledge base using translationbased methods.
In the knowledge fusion stage, we ﬁrst match related knowledge
triples in the knowledge base and select the knowledge triples with
3

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.

Table 1
Entity type and explanation.
Entity Type

Explanation

Threat-Actor
Security-Team
Campaign
Attack-Method
Attack-Purpose
Vulnerability
Tool
Asset
Indicator
Location
Identity
Feature
Time

Attacker, maybe individuals, groups, or organizations.
Security team, organization or institution.
The attack incident launched by threat actor.
Attack methods or ways that adversaries attempt to comprise targets.
The purpose of the attack or campaign the threat actor launched.
Vulnerability that could be used by hackers to comprise the system.
Tools used by attackers.
Assets, products or software that would be compromised.
Indicators of comprise, such as IP, domain, hash, etc.
Geographic location, which may indicate the location of the attacker or the target location of the attack.
Target individuals, organizations, groups, or industry.
The features of vulnerability, or attack method.
Timestamps.

Table 2
Relationship between entities and explanation.
Subject

Relationship

Object

Explanation

Security-Team

discover

Campaign, Threat-Actor

Campaign
Threat-Actor
Threat-Actor
Threat-Actor
Threat-Actor

active-time
active-time
locate-at
target
use

Threat-Actor
Threat-Actor
Vulnerability

launch
attack-purpose
has

Time
Time
Location
Identity, Location
Tool, Vulnerability,
Attack-Method
Campaign
Attack-Purpose
Feature

Vulnerability
Indicator

aﬀect
indicate

Identity
Asset
Attack-method
Tool

locate-at
suﬀer
has
use

Asset
Threat-Actor, Tool,
Attack-method
location
Attack-Method
Feature
Attack-Method, Vulnerability

Vulnerability

suﬀer

Attack-Method

The security team discovers an attack campaign or a threat actor
carrying out an attack behavior.
Activity time of the campaign.
Activity time of threat actor.
The threat actor is located at the related Location.
The threat actor targets the type of victims and the related location.
The related attack method, vulnerability, or tool are used by the
threat actor in a campaign.
Threat actor launch the attack campaign.
The attack purpose of the threat actor in the campaign.
The characteristics of this vulnerability that would be used by
threat actors.
Assets aﬀected by the vulnerability.
The indicator of compromise could detect evidence Threat-Actor,
Attack-Pattern, malicious Tools.
The identity is located at the related location.
The attack method that fragile assets may suﬀer.
The characteristics of the attack method.
Threat actors use tools to exploit vulnerability or attack method in a
campaign.
The vulnerability may be subject to some attack method.

similar semantics. Then we construct the sentence tree with object entities in triples as leaf nodes. Then we utilize the matrix to represent the
sentence tree and use GAT to fuse knowledge information.
In the decoder stage, we employ the sequence labeling method to
extract CTI entities, treating relation extraction as a classiﬁcation task.
In the end, we generate a threat knowledge graph according to the
extracted entities and relations, facilitating a holistic view of the cybersecurity landscape.

reliable information about vulnerabilities, threat actors, attack techniques, and other cybersecurity concepts. The data sources could be
divided into three types: 1) open-source database, such as OpenCVE
(OpenCVE, 2023), ATT&CK (ATT&CK, 2023), CAPEC (CAPEC, 2023),
etc; 2) structured data on websites, such as Malvuln (Malvuln, 2023),
Threat Actor Map (aptmap, 2023, etc; 3) structured data on the open
source platform github. Each data source has a speciﬁc data collection
mechanism, given that we gather data from various sources.
After collecting the data, it is necessary to analyze each data format
because diﬀerent data sources have various data presentations. Next,
we parse the collected data, extracting cybersecurity entities and their
relations to generate knowledge triples. Additionally, we unify relationships from diﬀerent sources that convey the same meaning. Fig. 5 shows
how we extract triples from structured data of Malvuln (Malvuln, 2023)
which introduces a threat AtomSilo including threat type, vulnerability
type, ﬁle type, etc. We consider the AtomSilo as the subject entity, and
the type content as the object entity and obtain the relations according
to the type. Lastly, we identify and eliminate duplicate triples, considering that knowledge data collected from diﬀerent sources may contain
the same knowledge triple with varying descriptions.

4. Methodology
In this section, we will provide a detailed introduction to the major modules of our approach. First, we provide an introduction to the
construction of the initial knowledge base from open-source structural
data. Subsequently, we oﬀer a detailed introduction to the training of
cybersecurity-aware knowledge embeddings. Following that, we will
describe the CTI extraction module, with a focus on knowledge fusion
technology.
4.1. Construct knowledge base

4.2. Cybersecurity-aware knowledge embeddings

Security teams frequently post summarized structural cybersecurityrelated information online which represents knowledge in essence. Consequently, we can construct an initial cybersecurity knowledge base
using open-source structured cybersecurity data.
The ﬁrst step in constructing the cybersecurity knowledge base is to
collect structured data from various sources, which provide rich and

Training knowledge embedding representation is crucial for knowledge representation. An eﬀective embedding representation signiﬁcantly improves model performance. To incorporate cybersecurity semantics into embedding representations, we introduce an additional
4

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.

Fig. 4. The overview of KnowCTI consists of 4 modules. (1) Construct the cybersecurity knowledge base from open-source structure data. (2) Training cybersecurityaware knowledge embeddings on the cybersecurity knowledge base by introducing cybersecurity semantics. (3) Construct the sentence tree according to knowledge
triples and fuse knowledge information. (4) The decoder module which extracts entities and relation triples that could be used for knowledge graph construction.

for each knowledge entity. Finally, we utilize the mean-pooling of 𝑒𝑒𝑚𝑏𝑖
to compute the ﬁnal knowledge entity embeddings 𝑒𝑒𝑚𝑏 :

𝑒𝑒𝑚𝑏 = 𝑓𝑚𝑒𝑎𝑛 (𝑒𝑒𝑚𝑏0 , ..., 𝑒𝑒𝑚𝑏𝑛 )

(3)

We make the 𝑒𝑒𝑚𝑏 as the knowledge initial representation.
Then we employ translation-based methods (Bordes et al., 2013;
Wang et al., 2014; Ji et al., 2015) to train the knowledge embedding
using the 𝑒𝑒𝑚𝑏 as the initial embeddings. Translation-based methods
have been inﬂuential in the ﬁeld of knowledge graph embedding which
is simple but eﬀective. This type of translation distance-based model
usually considers the rationality of facts as the distance between two
entities after translating the relationship. It uses margin loss as the object:
Fig. 5. Extract triples from open structured data.

𝑙𝑜𝑠𝑠𝑘𝑒 =

(1)

𝑜 = 𝜎(𝑊 𝑡0 + 𝑏)

(2)

∑

[𝛾 + 𝑑(𝑠 + 𝑟, 𝑜) − 𝑑(𝑠′ + 𝑟, 𝑜′ )]+

(4)

(𝑠,𝑟,𝑜)∈𝐾 (𝑠′ ,𝑟,𝑜′ )∈𝐾 ′

(𝑠,𝑟,𝑜)

cybersecurity text identiﬁcation task to train the knowledge embeddings based on cybersecurity-related reports.
For a given knowledge entity 𝑒, the initial step is to search for entityrelated documents 𝑃 in the browser. We retain the top 10 documents
assuming these are the most relevant. In most cases, sentences where
the entity is located are security-related. This is because most securityrelated entities are unique to the realm of cybersecurity. Subsequently,
we ﬁlter at most 10 sentences containing the entity as 𝑆𝑒 to enrich the
semantic information.
We train a classiﬁcation model by ﬁne-tuning BERT (Devlin et al.,
2018) model consistent with the rest to determine whether the text is
related to cybersecurity or not. Therefore, We could obtain entity embeddings from the ﬁnetuned model, if the text is cybersecurity-related.
For each sentence, we use it as the input for the ﬁnetuned BERT model.
Initially, we encode each sentence 𝑠𝑖 and acquire the embeddings of
each token. Next, we utilize the [CLS] embedding for binary classiﬁcation to determine the security relevance of the sentence.

𝑡0 , 𝑡1 , ..., 𝑡𝑛 = 𝐵𝐸𝑅𝑇 (𝑠𝑖 )

∑

where [𝑥]+ represents the positive part of 𝑥, (𝑠, 𝑟, 𝑜) is the triple in
knowledge base 𝐾 , 𝛾 > 0 is a margin hyperparameter. The corrupted
triples are constructed by:
′
𝐾(𝑠,𝑟,𝑜)
= {(𝑠′ , 𝑟, 𝑜)|𝑠′ ∈ 𝐾} ∪ {(𝑠, 𝑟, 𝑜′ )|𝑜′ ∈ 𝐾}

(5)

4.3. Knowledge fusion
4.3.1. Knowledge denoise and insertion
To ﬁlter appropriate knowledge entities from a vast array of options,
we employ a simple yet eﬀective method based on security entity features. Security entities frequently possess multiple variants, each with
diﬀerent connectors and suﬃxes but sharing the same backbone string.
Initially, we eliminate special characters and spaces, retain only alphabets and digits, and calculate the maximum common substring to
ascertain if the text contains the target entity. We consider the ratio of
the maximum common substring to the entity length, denoted as 𝛼 . If 𝛼
exceeds 0.8, as determined through experiments, we conclude that the
text contains the target entity. Once the existence of an entity is conﬁrmed, we utilize a string fuzzy match method to identify the closest
triples and determine the insertion position. In this step, we employ an
n-gram approach, where n is determined by the provided knowledge
subject entity, and calculate the match score between knowledge and
the target n-gram. The target entity is determined by the n-gram that
achieves the highest score.
The fuzzy match method may bring incorrect knowledge triples,
leading to noise. After obtaining all candidate knowledge triples, we
encode the knowledge subject embeddings as 𝑘 = [𝑘𝑠0 , 𝑘𝑠1 , ..., 𝑘𝑠𝑚 ]. We

where 𝑡0 is the embedding of the special token [CLS], and 𝜎 is the
sigmoid activation function. If 𝑜 is greater than 0.5, we think the sentence is security-related and reserves the entity embeddings. BERT uses
WordPiece tokenization, which may break a word into a few tokens
and generate diﬀerent embeddings for each token. In this work, we
only adopt the ﬁrst token as the word embeddings. Also, a knowledge
entity may contain multiple words. We use max-pooling to compute
knowledge entity embeddings 𝑒𝑒𝑚𝑏𝑖 in 𝑠𝑖 . We have multiple sentences
5

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.

Fig. 6. Knowledge fusion architecture. We employ the graph attention networks to fuse knowledge information.

As nodes in graph 𝐺 are composed of words in the text and object
entities in the knowledge triples, the node representation is divided into
two parts. We encode the text by ﬁnetuning BERT model which is the
same one used in the knowledge denoise part, and get the representation 𝑡𝑖 of each text node; we obtain the object entity node embedding
𝑒𝑒𝑚𝑏 by cybersecurity-aware knowledge embeddings. The features of
nodes are represented as ℎ = {𝑡1 , 𝑡2 , ..., 𝑡𝑛 , 𝑒𝑒𝑚𝑏1 , 𝑒𝑒𝑚𝑏2 , ..., 𝑒𝑒𝑚𝑏𝑚 }.
To more fully represent the features of nodes and maintain spatial
feature consistency, feature transformations ℎ𝑖 = 𝑊 ℎ𝑖 are performed
using the same weight 𝑊 as in Eq. (6). Then we compute the attention
weights between two nodes:

further select relevant knowledge triples by a selective module employing an attention mechanism. We evaluate the relevance of each
knowledge subject entity for the target context. We encode the text with
ﬁnetuning BERT model and use the special token [𝐶𝐿𝑆] as the context embeddings and compute the relevance. To more fully represent
the features of nodes and maintain spatial feature consistency, feature
transformations are performed.

𝑘 = 𝑘𝑊 ,

𝑐 = 𝑐𝑊

(6)

where 𝑊 is the weight for transformation, 𝑘 is the knowledge subject
embedding, 𝑐 is the [𝐶𝐿𝑆] embedding.
We employ the scaled dot-product attention function to calculate the
attention score 𝑎:

𝑎 = 𝐴𝑡𝑡𝑒𝑛𝑡𝑖𝑜𝑛(𝑄𝑊𝑎 , 𝐾𝑊𝑎 , 𝑉 𝑊𝑎 )

(7)

𝑄𝐾 𝑇
𝐴𝑡𝑡𝑒𝑛𝑡𝑖𝑜𝑛(𝑄, 𝐾, 𝑉 ) = 𝑠𝑜𝑓 𝑡𝑚𝑎𝑥( √ )𝑉
𝑑𝑘

(8)

𝑒𝑖𝑗 = 𝐿𝑒𝑎𝑘𝑦𝑅𝑒𝐿𝑈 (𝑊𝑔 ℎ𝑖 , 𝑊𝑔 ℎ𝑗 )

(10)

𝛼𝑖𝑗 = 𝑠𝑜𝑓 𝑡𝑚𝑎𝑥(𝑒𝑖𝑗 )

(11)

Finally, the normalized attention coeﬃcient is linearly combined
with its corresponding features to serve as the ﬁnal knowledge-aware
representation ℎ̃𝑖 for each node:

where 𝑄 = 𝑘 and 𝐾, 𝑉 = 𝑐 . Then we apply a gating mechanism to select
the relevant knowledge and discard irrelevant knowledge:

∑
ℎ̃𝑖 = 𝜎( (𝛼𝑖𝑗 𝑊𝑔 ℎ̃𝑗 )

𝜇 = 𝜎(𝑎)

4.4. Decoder and graph construction

(9)

In the gating mechanism, we use the sigmoid function to determine
the importance of each triple. The triples with high gating values are
considered relevant, while those with low values are ﬁltered out. Then,
we construct the sentence tree, according to the sentence and the knowledge triples, as shown in Fig. 2.

(12)

We consider CTI entity extraction as a sequence tagging task and
consider relation extraction as a classiﬁcation task and these two tasks
are trained jointly. After obtaining the knowledge-aware representation
of each token embedding, we pass it to a conditional random ﬁeld (CRF)
layer for predicting the label 𝑜𝑖 and the highest score is considered as
the prediction label:

4.3.2. Knowledge fusion
Determining which knowledge triple to use for even the correct
entities is challenging. Ideally, diﬀerent knowledge triples should be
applied under diﬀerent semantics. Therefore, using irrelevant knowledge triples will inevitably introduce noise and reduce the precision of
the threat intelligence extraction. To address this challenge, we employ
Graph Attention Networks (GAT) (Velickovic et al., 2017) to integrate
knowledge into text, leveraging the capability to fuse knowledge based
on relevance weights between nodes.
We convert the sentence tree into a graph 𝐺 , representing words
and knowledge entities as nodes and the relations as edges. For a graph
with 𝑛 nodes, we construct the symmetric adjacency matrix 𝑀 ∈ ℝ𝑛×𝑛
to represent the graph. If there exists an edge between node 𝑖 and node
𝑗 , 𝑀𝑖𝑗 = 1; otherwise, 𝑀𝑖𝑗 = 0. To preserve node information, self-loops
are added to each node, represented as 𝑀𝑖𝑖 = 1.

𝑦̂𝑖 = 𝑎𝑟𝑔𝑚𝑎𝑥(𝑜𝑖 )

(13)

During the training, we optimize the model by minimizing the crossentropy loss in the named entity task and obtain the loss 𝑙𝑜𝑠𝑠1 .
For the identiﬁed entities, we combine them in pairs. For each pair,
we represent it by subtracting the subject entity embedding ℎ𝑒𝑛𝑡1 from
the object entity embedding ℎ𝑒𝑛𝑡2 . As an entity may contain multiple tokens, we apply mean-pooling to the embeddings of tokens as the entity
embedding ℎ𝑒𝑛𝑡 .

ℎ𝑟 = ℎ𝑒𝑛𝑡2 − ℎ𝑒𝑛𝑡1

(14)

Then we classify each pair by softmax activation after the FFNN:

𝑟𝑜𝑖 = 𝑠𝑜𝑓 𝑡𝑚𝑎𝑥(𝐹 𝐹 𝑁𝑁(ℎ𝑟 ))
6

(15)

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.

where 𝑆 is the set of triples, 𝕀 is the indicator function (if the condition
is true, the function value is 1, otherwise 0), and 𝑟𝑎𝑛𝑘𝑖 is the predictive
ranking of the 𝑖𝑡ℎ triple.
In this work, we use hit@10, hit@3, hit@1 as the indicator to evaluate knowledge graph embedding. The larger the hit@n indicator, the
better.
MeanRank is another evaluation method of knowledge graph embedding which represents the average ranking score of correct entities.
A smaller MeanRank value indicates a higher ranking and better entity
vectorization results.

We take the label with the highest probability as the prediction label:

𝑟̂𝑖 = 𝑎𝑟𝑔𝑚𝑎𝑥(𝑟𝑜𝑖 )

(16)

During the training, we also optimize the model with a cross-entropy
loss in the relation classiﬁcation task and obtain the loss 𝑙𝑜𝑠𝑠2 .
Finally, we train the model jointly:

𝑙𝑜𝑠𝑠 = 𝑙𝑜𝑠𝑠1 + 𝜆𝑙𝑜𝑠𝑠2

(17)

where 𝜆 is the weight parameter.

|𝑆|

𝑀𝑅 =

5. Experiments

5.3. Settings
In this work, we use the pretrained BERT model as the backbone
model for ﬁne-tuning. We use grid search to select appropriate hyperparameters. In the knowledge embedding training stage, the embedding
dim is set to 768 the same as BERT, the margin is set to 10. In the CTI
extraction stage, the batch size is 32. In the denoising module, we employ a multi-head attention mechanism and the number of heads is 8,
and the dropout is 0.1. In the GAT module, we also use multi-head attention and set the number of heads to 8. The dropout is set to 0.5
and the 𝛼 in LeakyReLU is set to 0.2. We optimize our model using the
Adam optimizer with a learning rate of 5e-5. Furthermore, we incorporate a learning rate scheduler employing a cosine strategy, and we
apply a weight decay of 0.01.

5.1. Datasets
We collect structural data from multiple sources and construct the
initial knowledge base as introduced in Section 4.1. The total number of triples is 53,713, and the total number of entities is 14,450.
We collected threat data from a set of sources automatically, including
security blogs, forum posts, etc. And ﬁnally, 130,424 security-related
data have been collected. To train and evaluate KnowCTI, we invested
5 cybersecurity graduate students for the annotation of the data. For
security-related text classiﬁcation, we annotated 4,896 instances. For
CTI extraction, we annotated 8,872 instances with 28,347 entities and
13,721 triples, according to the ontology we designed.

5.4. Main results
In order to understand the eﬀectiveness of KnowCTI, we compare
our methods with some classic methods that do not fuse knowledge.
Here we give a brief introduction of them as follows:

5.2. Evaluation metrics
We use Precision(P), Recall(R), and F1 score with macro-average to
evaluate the performance of entity extraction and relation extraction in
KnowCTI. A triple is considered to be correctly extracted if and only
if its relation type and both entities are correctly matched. Equations
show the calculation method of macro-average:

• BiLSTM-CRF (Lample et al., 2016): It is a classic and eﬀective
method for performing NER without considering external knowledge incorporation. The BiLSTM component captures the sequential dependencies among input tokens, while the CRF component
facilitates optimal and cohesive prediction of all labels within the
sentence.
• BERT-CRF (Devlin et al., 2018): BERT eﬀectively extracts implicit
language information from unlabeled text, demonstrating exceptional performance across various NLP tasks, including Named Entity Recognition (NER). In this baseline, we ﬁnetune BERT on CTI
extraction task, and a CRF module is applied as the top layer for
inference.
• BERT-BiLSTM-CRF (Dai et al., 2019): This model combines BERT,
BiLSTM, and CRF. BiLSTM layer follows by BERT, eﬀectively capturing sequential dependencies among input tokens and enhancing
the model’s contextual understanding. This integrated architecture
leverages the complementary strengths of each component.
• NER4CTI (Liu et al., 2022): NER4CTI is the state-of-the-art method
focusing on cybersecurity threat intelligence entity extraction. It
proposed a semantic augmentation approach that integrates various linguistic features to enhance the representations of input
tokens and improve the NER performance.

𝑇𝑃
(18)
𝑇𝑃 + 𝐹𝑃
where 𝑇 𝑃 represents true positive classiﬁcations, 𝐹 𝑃 represents false
𝑃=

positive classiﬁcations. The precision measures the capability of correct
predictions among all positive predictions identiﬁed by the model.

𝑇𝑃
(19)
𝑇𝑃 + 𝐹𝑁
where 𝐹 𝑁 represents false negative classiﬁcations. Recall indicates the
𝑅=

capability of the model to identify positive samples.

2∗𝑃 ∗𝑅
𝑃 +𝑅

(20)

F1 score is the harmonic mean of Precision and Recall, taking into account the results of both. After obtaining the P, R, and F1 of each type,
we average them to get the macro F1 score.
hit@n is commonly used to evaluate the performance of the knowledge graph embedding. It focuses on the top n predictions made by the
model and assesses whether the ultimate correct entity is present within
this set of top n candidates, i.e. the proportion of correct entities ranked
in the top n. It could be calculated by:

Table 3 shows the f1 performance of diﬀerent methods. The results
demonstrate the eﬀectiveness of KnowCTI as it can reach the best performance indicating that the fusion of knowledge could enhance the
models’ understanding of cybersecurity domain text. The results show
that ﬁnetuned BERT model performs better than the BiLSTM model. The
performance of the ﬁnetuned BERT model increases the BiLSTM model

|𝑆|

ℎ𝑖𝑡@𝑛 =

1 ∑
𝕀(𝑟𝑎𝑛𝑘𝑖 ≤ 𝑛)
|𝑆| 𝑖=1

(22)

where the symbolic meaning is the same as above.

In this section, we introduce the datasets and conduct comprehensive experiments to demonstrate the eﬀectiveness of our proposed
model KnowCTI. In addition, we crawled more than 100,000 reports
and analyzed top-k attack method trends over the past two decades.
Also, we presented a case study of attack organization proﬁling and a
case study of threat intelligence graph generation.

𝐹1 =

1 ∑
𝑟𝑎𝑛𝑘𝑖
|𝑆| 𝑖=1

(21)
7

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.

Table 3
Performance of diﬀerent models on CTI extraction.
Models

Entity
P

BiLSTM-CRF
BERT-CRF
BERT-BiLSTM-CRF
NER4CTI
KnowCTI

70.04
78.87
80.55
84.53
92.96

Table 4
The performance of diﬀerent knowledge embedding
methods.

Relation
R
69.98
77.66
80.27
84.23
87.52

F1
70.01
78.26
80.41
84.38
90.16

P
48.35
64.95
68.92
78.43

R
52.68
66.06
67.83
85.54

F1

Methods

MR

hit@10

hit@3

hit@1

50.42
65.50
68.37
81.83

TransE
Cyber-TransE
TransH
Cyber-TransH
TransD
Cyber-TransD

215.41
215.91
221.96
206.03
218.60
170.02

81.00
81.30
81.05
81.25
81.15
81.75

74.25
74.50
74.55
74.65
74.50
74.75

60.80
61.05
60.05
61.50
60.90
62.35

by 8.15. Because BERT is pretrained on a large corpus having better presentation ability and it is also easy to ﬁnetune to the downstream task.
In KnowCTI, we use BERT as the backbone model. Compared to the
BERT-BiLSTM-CRF model, KnowCTI has increased by 9.75 performing
best. Because BERT is pretrained on the general corpus lacking cybersecurity semantics, the introduction of external knowledge could augment
the cybersecurity semantics which could enhance the representations of
cybersecurity text and then improve the model’s performance. We also
compare the entity extraction performance with NER4CTI, and increase
by 5.78. Results show that the performance of relation extraction is
worse than entity extraction generally, perhaps due to error propagation. Because entity extraction errors will inevitably lead to incorrect
relation classiﬁcation.

Table 5
The performance of diﬀerent knowledge embedding methods on CTI
extraction.
Methods
TransE
Cyber-TransE
TransH
Cyber-TransH
TransD
Cyber-TransD

Entity

Relation

P

R

F1

P

R

F1

90.34
91.63
90.68
91.17
90.32
92.96

88.93
87.99
88.32
88.24
88.46
87.52

89.32
89.61
89.48
89.68
89.38
90.16

77.47
76.57
77.80
78.41
79.10
78.43

83.00
86.25
82.41
85.24
83.42
85.54

80.14
81.12
80.04
81.68
81.20
81.83

Table 6
Performance of module deletion.

5.5. Ablation study
Methods

To understand the contribution of diﬀerent modules, we conducted
several ablation studies. In this section, we studied the role of knowledge fusion and the eﬀect of diﬀerent Knowledge representations.

KnowCTI
wo knowledge denoise
wo fuzzy match
BERT

5.5.1. Knowledge embedding evaluation
In this section, we study the performance of diﬀerent translationbased knowledge embedding methods and the eﬀectiveness of cybersecurity-aware knowledge embeddings. We compare the TransE, TransD,
and TransH methods that train on knowledge base only, and the
cybersecurity-aware TransE (Abbreviated as Cyber-TransE), cybersecurity-aware TransD (Abbreviated as Cyber-TransD), cybersecurityaware TransH (Abbreviated as Cyber-TransH) that train on knowledge
base using the cybersecurity entity embeddings. We evaluate the performance of knowledge embedding, and the results are shown in Table 4.
Then for each method, we evaluate the performance of CTI extraction and choose the best of them as the ﬁnal method we use. The
results are shown in Table 5. It should be noted that the F1 score for
security-related classiﬁcation during training the cybersecurity-aware
knowledge embeddings reached 98.68.
As shown in Table 4, we ﬁnd the cybersecurity-aware translationbased methods achieve a little better performance generally. The CyberTransD has the best performance since it introduces more parameters
to map vectors. On the other hand, this method also has the highest
cost. Results in Table 5 show that the Cyber-Trans methods achieve
better performance on CTI extraction than the Trans methods which
demonstrates the eﬀectiveness of the cybersecurity-aware knowledge
embedding. The average improvement of Cyber-Trans methods on CTI
entity extraction is 0.42, and 1.08 on CTI relation extraction. The CyberTrans methods only have a slight improvement over the Trans methods
on CTI entity extraction and the main improvement of Cyber-Trans
methods lies in precision. We have found that the improvement in the
precision of CTI entity extraction will lead to an increase in the recall
rate of relation extraction. Also, the method that has better performance
on knowledge embedding could achieve better performance on CTI extraction. We could see that the Cyber-TransD method gets the highest
score 81.75 on hit@10, 170.02 on MR and it also gets the highest f1
score on CTI extraction 90.16 on entity extraction, and 81.83 on relation extraction.

Entity

Relation

P

R

F1

P

R

F1

92.96
87.80
81.72
78.87

87.52
85.02
77.11
77.66

90.16
86.39
79.35
78.26

78.43
77.73
22.55
64.95

85.54
81.48
24.46
66.06

81.83
79.56
23.47
65.50

5.5.2. Knowledge fusion performance
According to the experiment results in Table 5, we choose CyberTransD method in KnowCTI. In this section, we conduct an ablation
study to understand the eﬀectiveness of each module in knowledge fusion, and the results are shown in Table 6. We remove each of them to
observe their impact on the model.
First, we remove the knowledge denoise module, which reﬁnes the
knowledge triples that are inserted into the text, and the performance
drops by 3.61. The results show that noisy knowledge triples will drop
the performance of the model. Second, we remove the fuzzy search
module and use the strict match search method. This drops a lot and
gets the worst even worse than the base BERT model on relation extraction as shown in the results. It may be because open texts are casual,
the strict knowledge is not often matched in the open text, causing the
knowledge fusion module not to learn well.
5.6. Case study
In this section, we collect 130,424 open reports from 2002-2022
and the number of reports every year are shown in Fig. 8. Then we
employ KnowCTI to extract entities and relation triples from the reports.
Finally, we extract 2,074,149 entities and 912,521 relation triples. From
the extracted entities and relation triples, we could conduct statistical
analysis, explore security knowledge, and generate threat graphs.
5.6.1. Statistical analysis of attack methods
In this part, we analyzed the extracted entities, mainly focusing on
the most commonly used attack methods. Among the extracted entities,
the top-5 attack methods are dos/ddos, phishing, malware, sql injection,
ransomware. Then we statistically analyzed the changes in attack trends
every year, as shown in the Fig. 7. In addition, due to the popularity of
supply chain attacks in recent years, we have also conducted a statistical
analysis of supply chain attack trends.
8

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.

and “vulnerabilities” as Vulnerability type, “Hikvision surveillance cameras” and “Hikvision cameras” as Asset type, “command injection
ﬂaw” as Attack-Method, “Chinese” and “Russian” as Location, “MISSION2025/APT41, APT10” and “threat actor groups” as Threat-Actor.
KnowCTI identiﬁes the relation triples as (‘CVE-2021-36260’, ‘aﬀect’,
‘Hikvision cameras’), (‘Hikvision surveillance cameras’, ‘suﬀer’, ‘command injection ﬂaw’), (‘MISSION2025/APT41, APT10’, ‘locate-at’, ‘Chinese’), (‘MISSION2025/APT41, APT10’, ‘use’, ‘vulnerabilities’), (‘threat
actor groups’, ‘locate-at’, ‘Russian’), (‘threat actor groups’, ‘use’, ‘vulnerabilities’). We could extract the entities and relations eﬀectively.
The “Hikvision surveillance cameras” and “Hikvision cameras” describe
the same entity; “CVE-2021-36260” and “vulnerabilities” both point
to the same entity. We align the entities by rules and construct the
graph according to the relation triples. Another case is shown in Fig. 10.
KnowCTI extracts the Threat-Actor entity “W3LL”. From the graph, we
can see that W3LL has been active since 2017 until now. It mainly uses
phishing kits to launch attacks on Microsoft 365 business email accounts
in region United States, Australia, and Europe, using proxy attacks and
bypassing MFA attack methods. The cases demonstrate that the graph
generated by KnowCTI could give a global picture of threats, and also
demonstrate the eﬀectiveness and generalization of our method.

Fig. 7. Statistics of attack trends. The horizontal axis represents the year, and
the vertical axis represents the reported quantity.

5.6.3. Attack organization portrait
Since we have extracted a large number of relation triples, we can
mine information about attack organizations and proﬁle them. Taking the hack organization “DarkHotel” as an example, for every triple
possessing an identical relation to that of the DarkHotel subject, the
relevant objects are merged into a list. The extracted relation triples related to DarkHotel include attack targets, attack methods, active time,
attack purpose, and tools they used. After deduplication, we summarize
the organization information in Table 7.
We could see that DarkHotel has been active since 2007 and is still
active today. The main attack targets of DarkHotel are senior executives
and luxury hotels where we ﬁnd that there are many related entities
such as “business executives”, “traveling executives”, and “luxury hotels”, etc, in the extracted triples that have target relation. In addition,
since the occurrence of COVID-19, the health organization has also
become the target of Darkhotel. Darkhotel mainly uses spearphishing
attack methods to deliver malicious code. According to the tools they
used, we know that they may inject the hotel wiﬁ networks and deliver malware, spyware, or malicious documents. And the main attack
purpose is to steal information. We compared our proﬁle results with
Wikipedia data entries (Wikipedia, 2023) and found that our proﬁle is
generally correct. This also conﬁrms the eﬀectiveness of our method.

Fig. 8. Total reports per year from 2002 to 2022.

According to statistical data, we found that dos/ddos attacks began
to become popular after 2010 and have continued to this day, while
ransomware attacks began to gradually emerge after 2010 and rose after 2015. SQL injection attacks were quite popular from 2008 to 2012
and the number of sql injection attacks has decreased in recent years.
Malware attacks and phishing attacks are on the rise as a whole, and the
number of attacks will be the highest in 2020-2022, which may also be
related to the COVID-19 epidemic with the increasing demand for online oﬃce work. The number of supply chain attacks is relatively small,
but with the outbreak of the SolarWinds incident in 2021, supply chain
attacks have also become hot, and the number of related attack reports
has reached its peak in 2021.

6. Limitation and future work
6.1. Entity alignment
KnowCTI mainly performs threat intelligence entity and relation
extraction tasks, without entity alignment function. In this work, we
employ simple entity alignment methods when constructing the threat
intelligence graph. However, the ability of this method is relatively limited. We will address this issue in the future. Entity alignment is crucial
for knowledge graph construction. In the ﬁeld of NLP, the goal of entity alignment is to link entities from diﬀerent knowledge graphs or
databases that refer to the same real-world objects or concepts, even
when these entities are expressed in diﬀerent languages or come from
diﬀerent sources. We have extracted a large number of entity and relation triples, and after entity alignment, we can construct a large-scale
intelligence knowledge graph that can be used to comprehensively understand the threat ecosystem and make threat predictions (Rastogi et
al., 2021).

5.6.2. Threat intelligence graph
We randomly take two open reports (Nelson, 2022; scmagazine,
2023) as examples to display the eﬀectiveness of our method. For each
report, we utilize KnowCTI to extract threat entities and relations and
generate a threat intelligence graph. On the other hand, we construct
the graph manually, which is extracted by 5 members of our team
and integrated together. As shown in Fig. 9, the left part is generated by KnowCTI, and the right part is constructed by team members.
In the report (Nelson, 2022), KnowCTI identiﬁes “CVE-2021-36260”
9

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.

Fig. 9. A case in which KnowCTI generates the knowledge graph from the report in which disclosed attackers exploited the CVE-2021-36260 vulnerability to access
Hikvision cameras.

Fig. 10. KnowCTI generates the intelligence graph of the report titled “Microsoft 365 accounts targeted by W3LL threat group”.
Table 7
The portrait information of the DarkHotel attack organization.
DarkHotel
Information

Details

active time
attack purpose
attack method
attack target
tools

2007, 2013, 2014, 2016, March 2018, 2020, 2022
steal information, cyber espionage campaign
uploading malicious code, spearphishing
executives, luxury hotels, telecommunications, Health Organization, agencies
WiFi networks, Konni malware, P2P, malware, oﬃce documents, keylogger, Adobe Flash, zero-day vulnerability

6.2. Deep analysis and targeted defense

2019). We will explore automated intelligence-driven security strategy
generation and development in future work, including access control
conﬁguration, attack detection rules, etc.

Intelligence is valuable for targeted network defense, so further data
analysis and mining are necessary. Intuitively, according to the attack method trends, security researchers could strengthen defense in a
targeted manner to reduce the risk of attack. Attacks caused by vulnerability exploitation are usually related to speciﬁc products or software.
If there are such products or software in the system, targeted defense
is needed. Otherwise, there is no need to pay attention to this intelligence. Therefore, the extracted asset entities related to vulnerabilities
can be used for targeted defense. Furthermore, the extracted vulnerability features are important for automated targeted defense (Feng et al.,

7. Related work
7.1. Knowledge fusion work
Incorporating knowledge information to enhance word representations (Peters et al., 2019; Liu et al., 2020; Yuan et al., 2021; Faldu et
al., 2021) and augment the performance of downstream tasks (Chawla
et al., 2021; He et al., 2020; Nie et al., 2021; Agarwal et al., 2023)
10

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.

has been a hot research topic in NLP. KnowBert (Peters et al., 2019) is
an extension of BERT aiming to enhance word representations. It proposes to incorporate world knowledge bases into BERT by designing
the knowledge attention and recontextualization component. It uses a
TransformerBlock to fuse knowledge and uses another multi-head attention to recontextualize the word piece representations. K-BERT (Liu
et al., 2020) is an improved BERT that enables injecting knowledge
into models. It injects knowledge triples into the sentence and converts
it into a sequence with a visible matrix preserving structural information and soft-position mechanism so that it could easily use BERT
architecture. KeBioLM (Yuan et al., 2021) is a biomedical knowledgeaware pretrained language model, which incorporates medical knowledge from Uniﬁed Medical Language System. It ﬁrst encodes text only
and then encodes text-entity fusion based on Transformers. KARL-TransNER (Chawla et al., 2021) incorporates world knowledge for NER based
on Transformer Encoder. It uses a self-attention network to encode
entities and relations in the knowledge base. And then generate the
contextualized representations for feature augmentation to improve the
NER performance. KAWR (He et al., 2020) proposes to encode external knowledge into word representations for NER. It proposes a gated
entity-based recurrent unit based on a recurrent neural network unit
to encode entity information into the word and get entity-based word
representations. KaNa (Nie et al., 2021) is a knowledge-aware NER
framework that aims to denoise the type-heterogeneous knowledge in
world knowledge to improve NER performance.

more accurate knowledge triples by an attention mechanism with a
gate. Based on the triples, we construct the sentence tree. Thirdly, we
utilize the graph attention networks to fuse knowledge information. Finally, we extract entities by sequence labeling and extract relations by
entity pair classiﬁcation. Experiments on the dataset demonstrate the
superior performance of KnowCTI. We have extracted CTI entities and
relations from a large number of open texts and studied the activity of
popular attack method trends in the past two decades. Based on the
extracted relation triples, we studied the portrait of attacking organizations and threat intelligence knowledge graph generation demonstrating the eﬀectiveness and generalization of our method.
CRediT authorship contribution statement
Gaosheng Wang: Writing – original draft, Software, Methodology,
Data curation, Conceptualization. Peipei Liu: Writing – review & editing, Supervision, Formal analysis, Conceptualization. Jintao Huang:
Writing – review & editing, Visualization, Investigation, Data curation.
Haoyu Bin: Writing – review & editing, Software, Resources, Data curation. Xi Wang: Writing – review & editing, Project administration.
Hongsong Zhu: Writing – review & editing, Project administration,
Funding acquisition.
Declaration of competing interest
The authors declare the following ﬁnancial interests/personal relationships which may be considered as potential competing interests:
Hongsong Zhu reports ﬁnancial support was provided by National Natural Science Foundation of China. If there are other authors, they declare
that they have no known competing ﬁnancial interests or personal relationships that could have appeared to inﬂuence the work reported in
this paper.

7.2. Cyber threat intelligence extraction
Nowadays, security researchers attempt to extract threat intelligence
entities from open-source reports automatically so that they can keep up
with the rapidly evolving landscape of threats and prepare for network
defense in advance (Mu et al., 2018; Wang et al., 2023; Zhao et al.,
2020). iACE (Liao et al., 2016) is an IOC extraction tool that utilizes
regex and terms to extract IOCs and employs the sentence dependency
graph to mine related tokens and relations between them from open articles. iACE relies on expert knowledge. Long et al. (2019); Zhou et al.
(2018); Liu et al. (2022) apply end-to-end neural-based sequence labeling to IOC identiﬁcation considering it as a named entity recognition
task. The neural-based methods could identify complex entities without human hand-crafted eﬀorts. NER4CTI (Liu et al., 2022) aggregates
multiple features to augment token representations including morphological features, constituent features, and POS features. Moreover, it
utilizes similar words in the cybersecurity domain corpus to augment
domain semantics. Recently, work trends towards constructing graphs.
AttackKG (Li et al., 2022) designs technique templates to extract attack behavior graphs for CTI reports. TTPdrill (Husari et al., 2017)
designs the threat action ontology and extracts TTPs using multiple
NLP techniques from CTI reports. CyberRel (Guo et al., 2021) employs
the BERT-BiGRU model to extract entity and relation jointly for cybersecurity concepts which could be used to construct the cybersecurity
knowledge graph. CSKG4APT (Ren et al., 2022) focuses on the APT attack scenarios and extracts CTI entities and relations to construct the
knowledge graph based on the design ontology.

Data availability
Data will be made available on request.
Acknowledgement
We are grateful to the reviewers for their work and insightful suggestions. This research was supported by the National Natural Science
Foundation of China (Grant No. 61931019).
References
Agarwal, A., Gawade, S., Azad, A.P., Bhattacharyya, P., 2023. Kitlm: domain-speciﬁc
knowledge integration into language models for question answering. arXiv preprint.
arXiv:2308.03638.
aptmap, 2023. https://aptmap.netlify.app/#.
ATT&CK, 2023. https://attack.mitre.org/.
Bordes, A., Usunier, N., Garcia-Duran, A., Weston, J., Yakhnenko, O., 2013. Translating
embeddings for modeling multi-relational data. Adv. Neural Inf. Process. Syst. 26.
Burger, E.W., Goodman, M.D., Kampanakis, P., Zhu, K.A., 2014. Taxonomy model for
cyber threat intelligence information exchange technologies. In: Proceedings of the
2014 ACM Workshop on Information Sharing & Collaborative Security, pp. 51–60.
CAPEC, 2023. http://capec.mitre.org/about/index.html.
Chawla, A., Mulay, N., Bishnoi, V., Dhama, G., 2021. Karl-trans-ner: knowledge aware
representation learning for named entity recognition using transformers. arXiv
preprint. arXiv:2111.15436.
CVE, 2023. https://cve.mitre.org/.
CWE, 2023. https://cwe.mitre.org/.
Dai, Z., Wang, X., Ni, P., Li, Y., Li, G., Bai, X., 2019. Named entity recognition using bert
bilstm crf for Chinese electronic health records. In: 2019 12th International Congress
on Image and Signal Processing, Biomedical Engineering and Informatics (Cisp-Bmei).
IEEE, pp. 1–5.
Devlin, J., Chang, M.-W., Lee, K., Toutanova, K., 2018. Bert: pre-training of deep bidirectional transformers for language understanding. arXiv preprint. arXiv:1810.04805.
Faldu, K., Sheth, A., Kikani, P., Akbari, H., 2021. Ki-bert: infusing knowledge context for
better language and domain understanding. arXiv preprint. arXiv:2104.08145.

8. Conclusion
In this paper, we propose to integrate cybersecurity knowledge into
the CTI extraction model based on pretrained language model to augment the understanding of cybersecurity semantics. Furthermore, we
design a threat ontology for the threat knowledge graph and extract entities and relations, which could be used for threat knowledge graph
construction and give a comprehensive picture of threats. Firstly, we
build the initial knowledge base from open-source structured data. Furthermore, we train the cybersecurity-aware knowledge embeddings,
which introduces the cybersecurity semantics from security texts. Secondly, we propose to fuzzy match related knowledge triples and select
11

Computers & Security 141 (2024) 103824

G. Wang, P. Liu, J. Huang et al.
Feng, X., Liao, X., Wang, X., Wang, H., Li, Q., Yang, K., Zhu, H., Sun, L., 2019. Understanding and securing device vulnerabilities through automated bug report analysis.
In: SEC’19: Proceedings of the 28th USENIX Conference on Security Symposium.
Guo, Y., Liu, Z., Huang, C., Liu, J., Jing, W., Wang, Z., Wang, Y., 2021. Cyberrel: joint
entity and relation extraction for cybersecurity concepts. In: Information and Communications Security: 23rd International Conference, Proceedings, Part I 23. ICICS
2021, Chongqing, China, November 19-21. Springer, pp. 447–463.
h3c. https://www.h3c.com/cn/d_202303/1796824_30003_0.htm.
He, Q., Wu, L., Yin, Y., Cai, H., 2020. Knowledge-graph augmented word representations
for named entity recognition. Proc. AAAI Conf. Artif. Intell. 34 (05), 7919–7926.
Husari, G., Al-Shaer, E., Ahmed, M., Chu, B., Niu, X., 2017. Ttpdrill: automatic and accurate extraction of threat actions from unstructured text of cti sources. In: Proceedings
of the 33rd Annual Computer Security Applications Conference, pp. 103–115.
Ji, G., He, S., Xu, L., Liu, K., Zhao, J., 2015. Knowledge graph embedding via dynamic
mapping matrix. In: Proceedings of the 53rd Annual Meeting of the Association for
Computational Linguistics and the 7th International Joint Conference on Natural Language Processing. In: Long Papers, vol. 1, pp. 687–696.
Ji, S., Pan, S., Cambria, E., Marttinen, P., Philip, S.Y., 2021. A survey on knowledge
graphs: representation, acquisition, and applications. IEEE Trans. Neural Netw. Learn.
Syst. 33 (2), 494–514.
Lample, G., Ballesteros, M., Subramanian, S., Kawakami, K., Dyer, C., 2016. Neural architectures for named entity recognition. In: Knight, K., Nenkova, A., Rambow, O.
(Eds.), Proceedings of the 2016 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies. Association
for Computational Linguistics, San Diego, California, pp. 260–270.
Li, Z., Zeng, J., Chen, Y., Liang, Z., 2022. Attackg: constructing technique knowledge
graph from cyber threat intelligence reports. In: European Symposium on Research
in Computer Security. Springer, pp. 589–609.
Liao, X., Yuan, K., Wang, X., Li, Z., Xing, L., Beyah, R., 2016. Acing the ioc game: toward automatic discovery and analysis of open-source cyber threat intelligence. In:
Proceedings of the 2016 ACM SIGSAC Conference on Computer and Communications
Security, pp. 755–766.
Liu, P., Li, H., Wang, Z., Liu, J., Ren, Y., Zhu, H., 2022. Multi-features based semantic
augmentation networks for named entity recognition in threat intelligence. In: 2022
26th International Conference on Pattern Recognition (ICPR). IEEE, pp. 1557–1563.
Liu, W., Zhou, P., Zhao, Z., Wang, Z., Ju, Q., Deng, H., Wang, P., 2020. K-bert: enabling
language representation with knowledge graph. Proc. AAAI Conf. Artif. Intell. 34
(03), 2901–2908.
Long, Z., Tan, L., Zhou, S., He, C., Liu, X., 2019. Collecting indicators of compromise from
unstructured text of cybersecurity articles using neural-based sequence labelling. In:
2019 International Joint Conference on Neural Networks (IJCNN). IEEE, pp. 1–8.
Malvuln, 2023. https://malvuln.com/.
Mitchell, R., Chen, R., 2014. Behavior rule speciﬁcation-based intrusion detection for
safety critical medical cyber physical systems. IEEE Trans. Dependable Secure Comput. 12 (1), 16–30.
Mu, D., Cuevas, A., Yang, L., Hu, H., Xing, X., Mao, B., Wang, G., 2018. Understanding the
reproducibility of crowd-reported security vulnerabilities. In: 27th USENIX Security
Symposium (USENIX Security 18), pp. 919–936.
Nelson, N., 2022. https://threatpost.com/cybercriminals-are-selling-access-to-chinesesurveillance-cameras/180478/.
Nie, B., Ding, R., Xie, P., Huang, F., Qian, C., Si, L., 2021. Knowledge-aware named entity
recognition with alleviating heterogeneity. Proc. AAAI Conf. Artif. Intell. 35 (15),
13595–13603.
OpenCVE, 2023. https://www.opencve.io/.
Peters, M.E., Neumann, M., Logan IV, R.L., Schwartz, R., Joshi, V., Singh, S., Smith, N.A.,
2019. Knowledge enhanced contextual word representations. arXiv preprint. arXiv:
1909.04164.
Rastogi, N., Dutta, S., Christian, R., Zaki, M., Gittens, A., Aggarwal, C., 2021. Information
prediction using knowledge graphs for contextual malware threat intelligence. arXiv
preprint. arXiv:2102.05571.
Ren, Y., Xiao, Y., Zhou, Y., Zhang, Z., Tian, Z., 2022. Cskg4apt: a cybersecurity knowledge
graph for advanced persistent threat organization attribution. IEEE Trans. Knowl.
Data Eng.
Ren, Y., Li, H., Liu, P., Liu, J., Li, Z., Zhu, H., Sun, L., 2023. Owner name entity recognition
in websites based on heterogeneous and dynamic graph transformer. Knowl. Inf. Syst.,
1–19.
Samtani, S., Abate, M., Benjamin, V., Li, W., 2020. Cybersecurity as an industry: a cyber
threat intelligence perspective. In: The Palgrave Handbook of International Cybercrime and Cyberdeviance, pp. 135–154.

scmagazine, 2023. https://www.scmagazine.com/news/w3ll-groups-phishing-tools-usedto-target-56000-corporate-microsoft-365-accounts.
secrss, 2023. https://www.secrss.com/articles/54098.
STIX, 2023. https://oasis-open.github.io/cti-documentation/stix/intro.
Syed, Z., Padia, A., Finin, T., Mathews, L., Joshi, A., 2016. Uco: a Uniﬁed Cybersecurity
Ontology. UMBC Student Collection.
Thimma, M., Liu, F., Lin, J., Luo, B., 2015. Hyxac: hybrid xml access control integrating
view-based and query-rewriting approaches. IEEE Trans. Knowl. Data Eng. 27 (8),
2190–2202.
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, Ł.,
Polosukhin, I., 2017. Attention is all you need. Adv. Neural Inf. Process. Syst. 30.
Velickovic, P., Cucurull, G., Casanova, A., Romero, A., Lio, P., Bengio, Y., et al., 2017.
Graph attention networks. Stat 1050 (20), 10–48550.
Wang, G., Liu, P., Huang, J., Si, S., Zhu, H., Sun, L., 2023. Csedesc: cybersecurity event
detection with event description. In: International Conference on Artiﬁcial Neural
Networks. Springer, pp. 26–38.
Wang, X., Liu, X., Ao, S., Li, N., Jiang, Z., Xu, Z., Xiong, Z., Xiong, M., Zhang, X., 2020.
Dnrti: a large-scale dataset for named entity recognition in threat intelligence. In:
2020 IEEE 19th International Conference on Trust, Security and Privacy in Computing
and Communications (TrustCom). IEEE, pp. 1842–1848.
Wang, Z., Zhang, J., Feng, J., Chen, Z., 2014. Knowledge graph embedding by translating
on hyperplanes. Proc. AAAI Conf. Artif. Intell. 28 (1).
Wikipedia, 2023. https://en.wikipedia.org/wiki/DarkHotel.
Yuan, Z., Liu, Y., Tan, C., Huang, S., Huang, F., 2021. Improving biomedical pretrained
language models with knowledge. arXiv preprint. arXiv:2104.10344.
Zhao, J., Yan, Q., Li, J., Shao, M., He, Z., Li, B., 2020. Timiner: automatically extracting and analyzing categorized cyber threat intelligence from social data. Comput.
Secur. 95, 101867.
Zhou, S., Long, Z., Tan, L., Guo, H., 2018. Automatic identiﬁcation of indicators of compromise using neural-based sequence labelling. arXiv preprint. arXiv:1810.10156.

Gaosheng Wang received a bachelor’s degree in computer science from Xidian University in 2019. He is currently a student studying in the University of Chinese Academy
of Sciences, pursuing a Ph.D. degree of Cyberspace Security. His work primarily focuses
on cyber threat intelligence and intelligent security defense with deep learning and natural language processing techniques.
Peipei Liu received the B.S. and M.S. degrees in Computer Science and Technology
from Shandong University of Science and Technology, China, in 2019. He is currently
pursuing toward the Ph.D. degree in Cyberspace Security at Institute of Information
Engineering, Chinese Academy of Sciences. His research interests include information
extraction, cyber threat intelligence analysis and multimodal intelligent information processing.
Jintao Huang received a bachelor’s degree in software engineering from Southwest
Jiaotong University in 2019. He is currently a student studying in the University of Chinese Academy of Sciences, pursuing a Ph.D. degree of Cyberspace Security. His work
primarily focuses on program analysis and ﬁrmware analysis.
Haoyu Bin received a bachelor’s degree in 2019 from Sichuan University. Currently
pursuing a Ph.D. degree at the University of Chinese Academy of Sciences, his research
focuses on device ﬁngerprint extraction in internet measurement.
Xi Wang is currently an engineer of Institute of Information Engineering, Chinese
Academy of Sciences. She received her Master’s degree in Institute of Computer Technology,Chinese Academy of Sciences in 2011. Her research interests include cyberspace
security, autonomous cyber defence with deep reinforcement learning and knowledge
graph techniques.
Hongsong Zhu received his PhD in computer architecture from the Institute of Computing Technology, Chinese Academy of Sciences in 2009. He is currently a researcher
at the Institute of Information Engineering, Chinese Academy of Sciences. The research
ﬁeld is cyberspace security. Research interests include: Internet of Things security, network confrontation, intelligent attack and defense, cyberspace security measurement and
threat situation awareness, etc.

12
PAPER_TEXT
