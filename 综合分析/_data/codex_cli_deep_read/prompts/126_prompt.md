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
# [126] Cybersecurity knowledge graphs construction and quality assessment
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
编号：126
题名：Cybersecurity knowledge graphs construction and quality assessment
年份：2023
DOI：10.1007/s40747-023-01205-1
来源：Complex & Intelligent Systems
PDF：paper/10.1007_s40747-023-01205-1.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：无
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\126.txt
- 原始字符数：68142
- 本次发送字符数：68142
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Complex & Intelligent Systems (2024) 10:1201–1217
https://doi.org/10.1007/s40747-023-01205-1

ORIGINAL ARTICLE

Cybersecurity knowledge graphs construction and quality assessment
Hongyi Li1,2 · Ze Shi2 · Chengwei Pan3,4

· Di Zhao1,2 · Nan Sun2

Received: 28 January 2023 / Accepted: 4 August 2023 / Published online: 24 August 2023
© The Author(s) 2023

Abstract
Cyber-attack activities are complex and ever-changing, posing severe challenges to cybersecurity personnel. Introducing
knowledge graphs into the field of cybersecurity helps depict the intricate cybersecurity landscape and provides technical
support for threat identification and situational awareness. However, during the process of constructing knowledge graphs,
inevitable noise and conflicts may be introduced, leading to misleading inferences and decisions. This paper aims to address
the issues of constructing and assessing the quality of cybersecurity knowledge graphs. We manually constructed a dataset
of cybersecurity knowledge graphs (CS13K) and expanded the existing cybersecurity ontology, building a more versatile
ontology applicable to existing data features. Building upon this, we utilized Neo4j to construct the cybersecurity knowledge
graph. Furthermore, we propose an AttTucker model, based on Transformer, for assessing the quality of knowledge graphs.
By employing numerous self-attention heads, this model captures latent information among entities and relations. While
reducing the dimensionality of knowledge embeddings, the model achieves evaluation results comparable to high-dimensional
embeddings. Finally, we incorporate the path-level information between entities in the knowledge graph into the evaluation
of knowledge graph quality based on the AttTucker model. Experimental analysis on both generic datasets and cybersecurity
datasets demonstrates that our model significantly improves F1 value and accuracy in knowledge graph quality assessment
tasks, outperforming other models.
Keywords Cybersecurity · Knowledge graph · Quality assessment · Ontology construction · Attention mechanism

Introduction
In recent years, a vast amount of valuable cybersecurity
information is scattered across the internet in a fragmented
Hongyi Li and Ze Shi are co-first authors of the article.

B Chengwei Pan

pancw@buaa.edu.cn

B Di Zhao

zdhyl2010@163.com
Hongyi Li
lihongyi@buaa.edu.cn
Ze Shi
zb2039107@buaa.edu.cn

1

School of Mathematical Sciences, Beihang University,
Beijing 100191, China

2

School of Cyber Science and Technology, Beihang
University, Beijing 100191, China

3

Institute of Artificial Intelligence, Beihang University,
Beijing 100191, China

4

Zhongguancun Laboratory, Beijing, China

manner, such as vulnerability platforms, security information
platforms, and security forums. However, these cybersecurity
knowledge fragments have not been effectively integrated
and utilized, limiting their unique advantages of big data
knowledge. Additionally, with the rapid evolution of the
cybersecurity landscape and the continuous innovation of
attack methods, passive and static defense measures are
no longer sufficient to meet the existing cybersecurity
needs. Therefore, proactive analysis of cybersecurity-related
information has become a necessary approach to address
cybersecurity challenges. In light of the abundant and dispersed data and the diverse and highly complex malicious
attacks confronted in the field of cybersecurity, knowledge
graph technology is regarded as an effective solution. As
an efficient knowledge management and reasoning tool,
knowledge graphs can automatically discover potential associations between threat entities, provide valuable correlated
information for cybersecurity situational awareness and risk
assessment, associate intrusion alerts with attack paths, and
propose optimal mitigation measures. Moreover, in the process of cyber-attack forensics, knowledge graphs can display

123

1202

vulnerable attack paths that require special attention. Analyzing this associative information, cybersecurity professionals
can gain a better understanding of vulnerabilities and attack
methods that adversaries may exploit, allowing them to
strengthen defense measures and enhance overall cybersecurity protection. Therefore, constructing a comprehensive
and accurate cybersecurity knowledge graph has become a
necessary means to address cybersecurity challenges.
The construction of an ontology forms the foundation of
building a cybersecurity knowledge graph. Acting as the
knowledge system of the cybersecurity knowledge graph,
cybersecurity ontology encapsulates the abstracted knowledge concepts of vulnerabilities, attackers, attack patterns,
attack consequences, and defensive strategies in the security
domain model. It can be utilized to represent, integrate, and
share relevant cybersecurity knowledge, and can offer a formalized and unified terminology in the information security
field along with the interrelationships among these terms.
Simultaneously, it also has ontology reasoning and querying
capabilities. Although several general-purpose ontologies in
the cybersecurity field have been constructed to date, their
complete applicability to a broader range of data sources
is hampered due to differing focuses on cybersecurity elements. To address this issue, in this paper, we construct a new
cybersecurity ontology, based on the analysis of CS13K data
characteristics and the reuse of existing cybersecurity ontologies. This new ontology provides support for the construction
of a comprehensive and accurate cybersecurity knowledge
graph.
Knowledge graphs have played a crucial role in multiple
domains, and an increasing number of software and applications are built upon them. However, when using knowledge
graphs, it is often assumed that the content within these
graphs is entirely error-free. If the content of the graph
itself is flawed, it can significantly undermine the effectiveness of higher-level applications, leading to misleading
reasoning and decision-making. However, noise and conflicts
are inevitably introduced during the construction of knowledge graphs. With the widespread adoption of knowledge
graphs, there is a growing demand for verifying the knowledge contained within them. In the early stages of knowledge
graph development, the scale requirements were relatively
low, allowing for manual inspection to determine the correctness of the triples in the graph. Nowadays, real-world
applications rely on large-scale and extensive knowledge
repositories, making manual fact-checking impractical. The
quality assessment of knowledge graphs plays a vital role in
enhancing their effectiveness and reliability in various application domains. Based on this, we propose a novel method
for evaluating the quality of knowledge graphs, specifically
focusing on assessing the quality of cybersecurity knowledge
graphs.

123

Complex & Intelligent Systems (2024) 10:1201–1217

In this paper, we manually constructed a cybersecurity knowledge graph dataset called CS13K, which exhibits
high knowledge quality. Building upon a subset of existing cybersecurity ontologies, we developed a more versatile
cybersecurity domain ontology that served as the foundation
for constructing the cybersecurity knowledge graph. Inspired
by the significant success of attention mechanisms in certain
deep learning tasks [1, 2], we propose a Transformer-based
model for evaluating the quality of knowledge graphs, named
AttTucker. This model utilizes numerous self-attention heads
to capture latent information between entities and relations.
Furthermore, we incorporate the path-level information to
assess the quality of the constructed cybersecurity knowledge graph. In summary, the key contributions of this paper
are as follows:
(1). We manually constructed a dataset of cybersecurity
knowledge graphs, named CS13K, which comprises 4494
entities, 12 relations, and 13,027 triples. CS13K represents
the first fully manually constructed knowledge graph dataset
in the field of cybersecurity.
(2). We expanded the UCO ontology from 8 categories to
16 categories and developed a new cybersecurity ontology
suitable for the CS13K dataset. Leveraging this ontology, we
constructed a cybersecurity knowledge graph that integrates
diverse and heterogeneous cybersecurity data sources into
semantically interpretable knowledge.
(3). We proposed a Transformer-based model for evaluating the quality of knowledge graphs. Under the condition
of low-dimensional embeddings, this model achieves evaluation results comparable to high-dimensional embeddings,
thereby addressing scalability issues in large-scale datasets.
The remaining sections of this paper are organized as follows: In Section “Related works”, we discuss the related
works. In Section “Methods”, we introduce the cybersecurity
knowledge graph dataset proposed in this study. We elaborate on the methodology used to construct the cybersecurity
knowledge graph and provide an overview of our model.
In Section “Results and discussion”, we present the experimental results and provide a detailed evaluation and analysis
of our model. Finally, we summarize the paper and discuss
future research directions.

Related works
In this section, we reviewed the previous work in areas, such
as cybersecurity datasets, ontology construction, knowledge
graph construction, and knowledge graph quality assessment.
We provided a comprehensive overview of research in these
tasks within the field of cybersecurity.

Complex & Intelligent Systems (2024) 10:1201–1217

1203

Table 1 Information extraction and knowledge graph datasets in cybersecurity domain
Dataset

Purpose
NER

Ravendar [3]
Robert [4]
Kim [5]
Wang [6]
Guo [7]
Rastogi [8]
Ours (CS13K)

√
√
√
√
√

Dataset size
RE

Remarks

KG

–

–

46,300 tokens

2013

High-quality, manually annotated

–

–

15,192 sentences

2014

Low-quality, automatically annotated

–

–

498,000 tokens

2020

High-quality, large-scale

–
√

–

175,220 tokens

2020

High-quality, manually annotated

–
√

13,262 sentences

2021

High-quality, manually annotated

–

–

–

–
√

–

Year

√
√

40K triples

2021

Low-quality, automatically annotated

3K triples

2021

High-quality, small-scale

13,027 triples

2022

High-quality, moderately large-scale

Cybersecurity datasets
Due to the high sensitivity and specialized nature of data
in the field of cybersecurity, as well as the lack of largescale specialized corpora, there has been limited research on
cybersecurity knowledge graph datasets. As shown in Table
1, Robert et al. [4] constructed a cybersecurity entity recognition dataset using an automatic annotation method. They
collected data from 15,192 cybersecurity sentences and used
the “BIO” labeling scheme for data annotation. Kim et al.
[5] manually annotated an entity recognition dataset in the
cybersecurity domain, where domain experts labeled entities
in CTI reports. This dataset contains a total of 498,000 words
and was used for entity recognition research in the cybersecurity field using Bi-LSTM-CRF, achieving an F1 score of
75.05%. Wang et al. [6] manually annotated a dataset called
DNRTI for named entity recognition research in the threat
intelligence domain. The dataset was collected from over 300
threat intelligence reports, and entities from 13 categories
were annotated. It contains a total of 175,220 words. Rastogi
et al. [8] employed an automated extraction method to collect data from 1100 threat intelligence reports, constructing a
malware knowledge graph dataset MT40K. This dataset contains 27,354 entities and 34 types of relations, comprising a
total of 40,000 triples. As the extraction was automated, the
accuracy of the triples in the dataset was not high. Based on
the MT40K dataset, the authors constructed another dataset,
MT3K, using manual filtering and expert review. The MT3K
malware knowledge graph dataset contains 3000 triples, and
while it boasts high triple accuracy, its smaller scale makes it
less suitable for data-driven deep learning models. Guo et al.
[7] manually constructed a cybersecurity information extraction dataset called OSINT by collecting information from
various sources, such as vulnerability databases, security
advisories, APT reports, security blogs, and hacker forums.
They used this dataset for joint extraction of entities and
relations in the cybersecurity domain, achieving an F1 score

of 80.98%. However, due to extensive internal annotation
work, the dataset has not been made publicly available.
The use of natural language processing and deep learning
methods for addressing cybersecurity issues is a relatively
emerging research area. The lack of large-scale datasets in
the cybersecurity field, coupled with the limited quality of
existing publicly available datasets, has become one of the
main obstacles restricting deep learning-based research in
the cybersecurity domain.

Cybersecurity ontology
The construction of ontology serves as the basis for building
a cybersecurity knowledge graph. Existing ontologies in the
field of cybersecurity can be difficult to apply comprehensively to the integration of broader data sources due to their
varying focuses during the construction process [9]. The earliest cybersecurity ontology was proposed by Undercoffer
et al., with the aim of constructing an intrusion detection
system for threat identification [10]. Since then, numerous
ontologies have been proposed in the field of cybersecurity.
Iannacone et al. [11] constructed a cybersecurity ontology
encompassing 15 types of entities and 115 attributes. Later,
Syed et al. [12] expanded this ontology, creating a more universal cybersecurity ontology, UCO, which can be mapped
to the STIX format. The UCO ontology links a large number of cybersecurity standards and ontologies, such as CVE,
CCE, CVSS, CAPEC, and more. It mainly includes eight
types of entities, such as Attacker, Attack-Pattern, Consequences, and Indicator. In addition to mapping to STIX,
UCO extends several related cybersecurity standards and
ontologies, like CVE, CCE, CVSS, etc. Vorobiev et al. [13]
built a Security Asset Vulnerability Ontology (SAVO) for
modeling concepts, attributes, and interrelationships among
network threats, risks, and vulnerabilities. Pingle et al. [14]
enhanced the UCO cybersecurity ontology by adding crucial
classes, such as Campaign, Tool, Course-of-Action, and also

123

1204

expanded the relations, thereby completing the extension of
the UCO ontology.
The construction of ontology can avoid the generation of
redundant triples and accelerate the triple generation process
in the knowledge graph. Therefore, building a comprehensive, appropriately granular, and semantically rich ontology
is crucial for constructing a cybersecurity knowledge graph.

Knowledge graphs
In 2012, Google introduced the concept of a knowledge graph
based on the Semantic Web. Essentially, a knowledge graph
is a large-scale semantic network that encompasses various
entities, concepts, and the semantic relations between entities. Currently, knowledge graphs have become a research
focus in areas, such as semantic search, question answering systems, and recommendation systems [15, 16]. In this
section, we first discuss the typical applications of knowledge
graphs and then provide an overview of their applications in
the field of cybersecurity.
Typical applications of knowledge graphs
From an application perspective, knowledge graphs can be
categorized into general knowledge graphs and domainspecific knowledge graphs. General knowledge graphs focus
on the breadth of knowledge and are widely used in intelligent
search and recommendation scenarios. Typical examples of
general knowledge repositories include Freebase, DBpedia,
YAGO, and Wikidata. On the other hand, domain-specific
knowledge graphs prioritize the depth of knowledge and
serve specific query and analysis requirements within a
particular knowledge domain. They have been extensively
applied in domains, such as finance, healthcare, e-commerce,
and academia.
Cybersecurity knowledge graphs
Cybersecurity issues are complex and intertwined, and multiple scholars have discussed security vulnerabilities [17,
18], attack patterns [19], and their corresponding solutions
in various scenarios [20, 21]. Some scholars have also
utilized federated learning techniques to address various
cyber-attacks [22]. By introducing knowledge graphs into the
field of cybersecurity, multiple heterogeneous and massive
cybersecurity data sources can be integrated into semantically interpretable knowledge. Researchers can gain intuitive
understanding of cybersecurity entities and their relations,
such as the exploitation relation between hacker organizations and vulnerabilities, the affiliation relation between
attackers and hacker organizations, and the inclusion relation between software and vulnerabilities. This integration
can play a role in target profiling, APT detection, attack

123

Complex & Intelligent Systems (2024) 10:1201–1217

tracing, and provide new technical means for cybersecurity
situational awareness, threat identification, and prediction.
Currently, research on knowledge graphs in the field of
cybersecurity is still in its early stages, with limited studies on the overall technical framework for constructing and
evaluating cybersecurity knowledge graphs. Yan et al. [23]
utilized machine learning methods to extract entities in the
field of cybersecurity and proposed a knowledge graph construction method applicable to the cybersecurity domain.
Based on the constructed ontology, they completed the
construction of a cybersecurity knowledge base. A cybersecurity situational analysis graph named Cygraph, launched
by MITRE, constructs a knowledge graph from four dimensions: network infrastructure, security posture, cyber threats,
and mission readiness. It is utilized to support tasks, such
as attack surface identification and attack situational understanding, for the protection of critical assets [24]. Kiesling
et al. [25] constructed a cybersecurity knowledge graph that
integrates critical information from various public sources
regarding vulnerabilities, weaknesses, and attack patterns.
Their instance data is derived from designated standards and
databases, such as CWE and CVE, by MITRE.

Knowledge graphs quality assessment
Knowledge graph quality assessment aims to quantitatively
evaluate the quality of knowledge within a knowledge graph.
Common methods for evaluating knowledge graph quality
can be classified into two categories: detection methods using
external data sources and detection methods based on internal
data within the knowledge graph.
Detection methods using external data typically rely on
external ontologies or network knowledge data to identify
entity or relationship errors within the knowledge graph. For
example, DeFacto et al. [26] used the DBpedia knowledge
base as their research object, transformed the knowledge data
into natural language statements, searched these statements
in a browser, and determined the confidence values of the
knowledge data based on the number of retrieved pages.
On the other hand, detection methods based on internal
data of the knowledge graph typically model the knowledge graph as a graph and record paths between two entities
through techniques such as random walks. If there are multiple paths between two entities in the knowledge graph,
it suggests a high likelihood of a relations between them.
Some scholars have also used knowledge representation
learning methods to discover erroneous entities and relations. Konstantinos et al. [27] compared the effectiveness
of graph embedding algorithms and path ranking algorithms
and achieved good results by combining these algorithms
in the task of knowledge graph error detection. Xie et al.
[28] utilized the structural information within the knowledge
graph for error detection. They introduced confidence scores

Complex & Intelligent Systems (2024) 10:1201–1217

of triples into the knowledge representation learning process
and proposed a confidence-aware knowledge representation
learning method. Experimental results demonstrated that this
method effectively captures the local and global structural
information of the knowledge graph for triple confidence
evaluation. Mendes et al. [29] proposed a knowledge quality
assessment method based on the LDIF framework, allowing users to define quality assessment functions based on
their specific business requirements or determine the final
score through comprehensive consideration of multiple evaluation methods. Jia et al. [30] constructed a knowledge graph
triple confidence evaluation model, assessing the confidence
of triples from three dimensions: the entity level, the relation
level, and the global level. They achieved good evaluation
results on the FB15K dataset. Zhang et al. [31] employed
automated machine learning technology (AutoML) to automatically design scoring functions (SFs) suitable for the triple
classification problem in the knowledge graph. By establishing a unified SF representation and a search space, and using
a greedy algorithm for efficient search, they achieved commendable results in the triple classification task.

Methods
Figure 1 presents the framework for constructing and evaluating the cybersecurity knowledge graph in this paper.
It primarily involves four components: dataset construction, ontology construction, cybersecurity knowledge graph
construction, and quality assessment of the cybersecurity
knowledge graph.

Dataset
Cybersecurity threat reports present the technical and social
aspects of cyber-attack events in the form of unstructured
text. The construction of a cybersecurity knowledge graph
first involves extracting key information from these reports,
which is not a straightforward task. The existing open-source
knowledge graph datasets in the field of cybersecurity are
obtained through automatic extraction, and the accuracy of
triples is not high, which is insufficient to reflect the actual
situation of cybersecurity. The only known cybersecurity
knowledge graph dataset with a higher accuracy rate, MT3K,
is manually selected from MT40K. However, the scale of
triples in this dataset is only 3000, which is not suitable
for data-driven deep learning models. To truly reflect the
status of cybersecurity, we have collected data from more
than 440 public security reports and manually constructed a
cybersecurity knowledge graph dataset. Each security report
is issued by world-renowned security companies or government agencies and is analyzed, extracted, and annotated by
several doctoral students from the Institute of Cyberspace

1205
Table 2 Relation types in the CS13K dataset and their statistical characteristics
Relation

Size

Proportion (%)

BelongTo

989

7.59

Cause

924

7.09

Exploits

792

6.08

HasAttack Location

2068

15.88

HasAttackTime

688

5.28

HasCharacteristics

951

7.30

HasVulnerability

1010

7.75

Indicates

443

3.40

Mitigates

750

5.76

Targets

2259

17.34

Use

1489

11.43

Associate
Total

664

5.10

13,027

100.00

Security who have good domain knowledge in cybersecurity. We named this dataset CS13K (Cybersecurity 13K). We
will continue to update CS13K to expand its scale and scope,
and reflect the true form of cybersecurity.
The CS13K dataset includes a total of 4,494 entities
and 12 types of relations. These 12 types of relations
are: belongTo, cause, exploits, hasAttackLocation, hasAttackTime, hasCharacteristics, hasVulnerability, indicates,
mitigates, targets, use, and associate. The dataset contains
a total of 13,027 triples, each with corresponding documents
and sentences, which provides a data source for future work in
areas, such as entity recognition and relation extraction. The
statistical characteristics of the relation types in the dataset
are shown in Table 2.
For example, the relation between ThreatActor and HackerGroup, Malware and MalwareFamily, malicious software
and its type, and vulnerabilities and their type is denoted
as “belongTo”. The relation between vulnerabilities and the
aftermath of an attack is represented as “cause”. The relation between threat actors and vulnerabilities or weaknesses
is represented as “exploits”. The relation between hacker
groups and their attack locations, attack activities and their
attack locations, and malicious software and their attack locations is represented as “hasAttackLocation”. The relation
between hacker groups and their attack times, attack activities and their attack times, and malicious software and its
attack time is represented as “hasAttackTime”. The relation
between malicious software and its features or functions,
hacker groups and their features or functions, and the features or functions of attack tools used by hacker groups is
represented as “hasCharacteristics”. The relation between
hardware, operating systems, and software and their own

123

1206

Complex & Intelligent Systems (2024) 10:1201–1217

Fig. 1 Framework for cybersecurity knowledge graph construction and quality assessment

security vulnerabilities is represented as “hasVulnerability”. The relation between hacker groups and their aliases
is represented as “indicates”. The relation between behaviors mitigating malicious software or vulnerabilities and
the malicious software or vulnerabilities is represented as
“mitigates”. The relation between hacker groups, malicious
software, or vulnerabilities and their targets is represented as
“targets”. The relation between attackers, attack activities,
and the attack methods or tools they use are represented as
“use”. Furthermore, when two entities have a relation but
do not fit the previous eleven categories, the label is set as
“associate”.

Construction of cybersecurity ontology
Based on the UCO ontology, we initially classify the knowledge related to cybersecurity to express the cybersecurity
knowledge completely. We expand the classes related to
cybersecurity attacks and preventive measures within the
UCO ontology to 16, the descriptions of which are presented
in Table 3. Subsequently, we define and constrain the rela-

123

tions between these classes. The relations and hierarchical
structure among the classes constructed in this paper are illustrated in Fig. 2.
By integrating and instantiating the associations depicted
in Fig. 2a–f, we obtained the schematic diagram of the network security ontology, as shown in Fig. 3. In Fig. 3, it can
be observed that Hacker groups use Malware during attack
activities, and the Malware may exploit various vulnerabilities present in operating systems or software, which can lead
to a series of consequences. Typical consequences include
denial of service, destruction of backups, memory corruption,
and privilege escalation. The cybersecurity domain ontology serves as the foundation for constructing the knowledge
graph, making it crucial to build a more comprehensive and
versatile ontology suitable for existing data sources.

Cybersecurity knowledge graph
The knowledge graph can be defined as K G  (h, r , t),
where h and t denote the head and tail entity, respectively,
and r represents the relation between h and t. In this study, the

Complex & Intelligent Systems (2024) 10:1201–1217

Fig. 2 Depiction of the schematic of relations among cybersecurity
objects. Specifically, a represents the relations between Campaign and
the other relevant classes; b presents the relations between CourseOfAction and the other related classes; c indicates the relations between

1207

HackerGroup and the other related classes; d expresses the relations
between Malware and the other correlated classes; e displays the relations between ThreatActor and the other related classes; f shows the
relations between Vulnerability and the other related classes

Fig. 3 Diagram of cybersecurity ontology

graph database Neo4j is selected as the software for storing
cybersecurity knowledge data. Neo4j is currently the most
widely used and popular graph database software, organizing and storing data in the form of nodes and edges. By
incorporating vulnerabilities, attacks, defense mechanisms,
etc., into the knowledge graph, it becomes possible to associate intrusion alerts with attack paths, visually presenting
attack methods, indicators, and consequences in the form of

a graph, and proposing the best mitigation measures. During the process of investigating cyber-attacks, it is possible
to identify the paths that are vulnerable and require focused
attention and create an overall picture of the attack activities,
facilitating analysis, detection, classification, and attribution
of various cyber threats. Figure 4 is a partial diagram of the
cybersecurity knowledge graph built using Neo4j.
The knowledge graph offers a fresh perspective for understanding and addressing cybersecurity threats. For example,

123

1208

Complex & Intelligent Systems (2024) 10:1201–1217

Fig. 4 Diagram of cybersecurity
knowledge graph

in the case of a common malware cyber-attack, the knowledge graph can classify it into multiple subclasses (such as
Trojan, worm, spyware) and link it to specific attack strategies
(such as ransomware, user data theft). Furthermore, it can
be associated with specific systems and applications at risk
(such as operating systems, web servers) and relevant defense
measures (such as firewall configurations, encryption, and
intrusion detection systems). Analyzing the information in
the knowledge graph, cybersecurity experts can make more
accurate predictions and prevent various cyber-attacks.
Moreover, taking automated threat detection and response
as an example, the knowledge graph contains extensive
information about past cyber-attacks, such as attack types,
methods, affected systems, attack timestamps, and impact
of the attacks. Based on this information and the success
achieved by intelligent computing [32], optimization algorithms [33, 34], and machine learning algorithms in various
scenarios and tasks [35, 36], we can train a machine learning
model based on this information. When new cyber activities (such as log entries, cyber traffic) are inputted into the
model, it can identify threats that match the attack patterns in
the knowledge graph. This enables us to provide early warning and response before the attacks pose a real threat to the
system.

graphs under the condition of low-dimensional embedding.
Existing knowledge representation models have achieved
good results in many downstream tasks using highdimensional embeddings, whereas the performance with
low-dimensional embeddings needs to be improved. This
has led to the scalability issue of existing models in largescale datasets. Therefore, we propose a Transformer-based
knowledge graph quality assessment model (AttTucker) that
utilizes a large number of self-attention heads to capture
latent information between entities and relations. Furthermore, we integrate path-level information into the AttTucker
model to evaluate the confidence of triples in the cybersecurity knowledge graph.
Based on the earliest research on attention mechanisms
[1], during the encoding phase, for each triple (h, r , t), we
set the dimension of the head entity as dh , the dimension
of the tail entity as dt , and the dimension of the relation
as dr . To ensure the validity of tensor calculations in the
model, we consider setting dh  dt  dr  k. We define the
embeddings of the head entity h and the relation r as eh ∈ R k
and er ∈ R k , respectively. The concatenated vector (eh ; er )
is then constructed as the query Q∈ R 2k , value V ∈ R 2k , and
key K ∈ R 2k . Based on the head entity h and the relation r ,
we can obtain the output matrix H ∈ R 2k as follows:

Quality assessment of cybersecurity knowledge
graphs
To the best of our knowledge, no model has attempted to
address the problem of quality assessment of knowledge

123


QK T
V,
H  Ahr V  softmax √
dk


(1)

Complex & Intelligent Systems (2024) 10:1201–1217

1209

Table 3 Classes related to cybersecurity and their descriptions
Class

Description

AttackVectors

A means or method through which hackers
can gain access to a computer or network
server

Backdoor

A method of logging in to the system, which
can bypass the existing security settings of
the system

Campaign

A series of malicious activities targeted at a
specific objective or launched within a
certain period of time

Characteristics

eh ×2
er ×3 et ,
ϕ(h, r , t)  W ×1

Characteristics of hacker organizations,
attack activities, malware, etc

Consequence

Consequences resulting from the exploitation
of vulnerabilities

CourseOfAction

Measures employed to prevent or respond to
attacks

HackerGroup

A group or organization engaged in
malicious operations

Location

The location where the cyber-attack takes
place

Malware

Utilized to compromise the confidentiality,
integrity, or availability of the victim’s data
or systems

MalwareFamily

Family of Malware

OperatingSystem

Operating system

Organization

The target of an attack, such as an
organization or company

Software

Software

ThreatActor

Individuals who conduct malicious
operations

Tool

Tools utilized by HackerGroup, Campaign,
ThreatActor, etc., for carrying out attacks

Vulnerability

A bug in the software that can be directly
exploited by hackers to gain access to a
system or network

(5)

where th r is the threshold that partitions triples into positive
and negative examples, which is a relation-specific parameter. In the CS13K dataset, we have 12 different th r values.
When p≥ 0.5, the triple is judged as positive, and when p <
0.5, the triple is classified as negative.
We use Binary Cross-Entropy (BCE) loss to train the
model, minimizing the following loss function.
L−

1 
(yi log pi + (1 − yi )log(1 − pi )),
V

(6)

i∈V

where V is the set of all entities, pi is the predicted probabilities of triples, and yi is the binary label.
In addition, based on the work in the literature [30], we
incorporate the path-level information into the AttTucker
model (referred to as AttTuc-Path model). As shown in Fig. 5,
we denote the triple confidence obtained from the AttTucker
model as pAttTucker , and the triple confidence obtained using
path-level information as pPath . We concatenate pAttTucker
and pPath to form a vector V , which is then fed into a
multi-layer perceptron to obtain the final probability value
p indicating the confidence of a triple being true.

(2)

Q
Wi K )
)(V Wi V ). Wi Q ∈ R k×dk ,
where Hi  softmax( (QWi √)(K
dk
Wi K ∈ R k×dk , Wi V ∈ R k×dv , and W O ∈ R hdv ×k are projection matrices, and h is the number of heads.
Furthermore, we use a token-wise feed-forward to generate the final output representation Houtput for each triple of
the knowledge graphs:
Houtput  F F N (MultiH (Q, K , V )),

(4)

where W ∈ R k×k×k is the core tensor, for each score
ϕ(h, r , t), We apply the logistic sigmoid function to each
score ϕ(h, r , t) to obtain the predicted probability p of a
triple being true:
p  sigmod(ϕ(h, r , t) − th r ),

where Ahr ∈ R 2k×2k are the attention matrices. When using
multiple attention heads, the multi-head attention can be represented as:


MultiH (Q, K , V )  H1 , . . . , H j W O ,

where F F N (x)  max(0, x W1 + b1 )W2 + b2 , and
W1 ∈ R k×dh , b1 ∈ R dh ,W2 ∈ R dh ×k , b2 ∈ R k are learnable
parameters.
During the decoding phase, based on the simplicity and
efficiency of the Tucker model [37], we construct the knowledge graph quality assessment model on the basis of the
eh ; 
er ), where
eh and
er are the
Tucker model. Let Houtput  (
output representations of the head h and the relation r . The
scoring function for the triple (h, r , t) can be represented as:

(3)

V  [ pAttTucker ; pPath ],

(7)


h n  σ W h n V + bh n ,

(8)

p  α(Wo h n + bo ),

(9)

Here, h n represents the n-th hidden layer, Wh n and bh n
denote the learnable parameters in the n-th hidden layer. Wo
and bo are the learnable parameters of the output layer.

123

1210

Complex & Intelligent Systems (2024) 10:1201–1217

Fig. 5 The AttTuc-Path model
for knowledge graph quality
assessment

Table 4 The parameter numbers and time complexity
Models

Numbers of parameters

Time complexity

TransE

Ek + Rk

O(k)

TransH

Ek + 2Rk

O(k)

TransD

2Ek + 2Rk

O(k)

TransR

Ek + Rk(k + 1)

O(k 2 )

Tucker

Ek + Rk + k 3

O(k 3 )

AttTucker

Ek + Rk + 3k 2 +k 3

O(k 3 )

Params T ucker  Ek + Rk + k 3 .

Time complexity and parameter numbers analysis
We conducted an analysis of the model complexity and
parameter numbers. Table 4 presents the parameter numbers
and time complexity of the Tucker and AttTucker models developed in this study, as well as the baseline models
TransE, TransH, TransD, and TransR. In the table, E represents the number of entities in the knowledge graph, R
represents the number of relation types, and k represents the
embedding dimension. From Table 4, it can be observed that
the parameter numbers of the baseline models exhibits a certain correlation with the number of entities, the number of
relations, or the embedding dimension.
In the task of knowledge graph quality assessment, we
represent the triples in the knowledge graph in the form of a
third-order Tucker decomposition:

X  G×1 A×2 B×3 C,

123

Here, X is a third-order tensor, G is a core tensor, and A,
B, and C are factor matrices. A and C have dimensions (E,
k), B has dimensions (R, k), and G has dimensions (k, k,
k). This means that A and C represent entity embeddings,
B represents relation embeddings, and G captures the interaction between these embeddings. Therefore, the parameter
count of the Tucker decomposition is:

(10)

(11)

The main cost here is the core tensor G, which has a size
of k 3 , and can become computationally expensive when k is
large. The costs of A and C are proportional to the number
of entities E, and the cost of B is proportional to the number
of relations R.
In the multi-head self-attention mechanism, for each attention head, we have three weight matrices: query (Q), key (K ),
and value (V ). Assuming we have h heads, a model embedding dimension of k, and each head has a dimension of dk ,
then for each attention head, the sizes of the Q, K , and V
matrices are all (dk , k).
Therefore, the parameter numbers of a single selfattention head is 3 ∗ d k ∗ k, and since there are h heads,
the total parameter count for self-attention is:
Params attention  3 ∗ d k ∗ k ∗ h

 3k 2 .

(12)

Complex & Intelligent Systems (2024) 10:1201–1217

1211

Therefore, the total parameter numbers of the AttTucker
model, including both the Tucker decomposition and multihead self-attention parameters, can be represented as:
ParamsAttTucker  ParamsTucker + Paramsattention

(13)

 Ek + Rk + 3k 2 +k 3 .
As a result, the time complexity of the Tucker and AttTucker models developed in this study is O(k 3 ). The time
complexity of TransE, TransH, and TransD is O(k), and the
time complexity of TransR is O(k 2 ). It can be observed
that, under the assumption of fixed embedding dimensions for entities and relations, our model contains more
parameters. However, in the case of low-dimensional embeddings, our model can achieve evaluation results comparable
to those with high-dimensional embeddings. Furthermore,
when dealing with large-scale datasets, the parameter count
introduced by the embedding dimension is negligible compared to the number of entities and relations. Therefore, our
model addresses the scalability issue to some extent in largescale datasets.

Results and discussion
In this section, we evaluate the quality assessment performance of the Tucker, AttTucker, and AttTuc-Path models
on the general-domain knowledge graph dataset FB15K. We
also verify the performance of our model on the cybersecurity
dataset CS13K.

Experimental settings and evaluating metrics
The FB15K dataset is a widely used general-domain knowledge graph dataset, consisting of 14,951 entities and 1345
relations. Since the FB15K dataset does not contain negative
triples, we adopt the method proposed in reference [38] to
construct negative triples by replacing either the head or tail
entity, simulating the construction of real-world knowledge
graphs. To investigate the impact of noise ratios in the knowledge graph on model performance, we construct datasets with
noise ratios of 10%, 20%, 30%, 40%, and 50%, denoted as
FB15K-N10, FB15K-N20, FB15K-N30, FB15K-N40, and
FB15K-N50, respectively. Similarly, for the cybersecurity
dataset CS13K, we also construct datasets with noise ratios
of 10%, 20%, 30%, 40%, and 50%, denoted as CS13K-N10,
CS13K-N20, CS13K-N30, CS13K-N40, and CS13K-N50,
respectively. For all datasets, we divide them into training
and testing sets in a 4:1 ratio. Accuracy and F1 score are
used as evaluation metrics. For a given triple, it is classified
as a positive sample if the predicted probability p ≥ 0.5,

Table 5 Main parameter settings for the AttTucker model
Batch size

2000

Learning rate

0.015

Epochs

3000

Number of heads

128

Encoder dropout

0.7

Position feed-forward dropout

0.7

Multi-heads attention dropout

0.1

Dimension embeddings

100

otherwise it is classified as a negative sample. During the
prediction process, there are four possible scenarios:
1. When the actual label is negative and the prediction is also
negative, it is a true negative (T N ).
2. When the actual label is negative but the prediction is
positive, it is a false positive (F P).
3. When the actual label is positive but the prediction is negative, it is a false negative (F N ).
4. When the actual label is positive and the prediction is also
positive, it is a true positive (T P).
Therefore,
Accuracy 

TP +TN
,
T P + T N + FP + FN

(14)

Precision 

TP
,
T P + FP

(15)

TP
,
T P + FN

(16)

2Precision ∗ Recall
.
Precision + Recall

(17)

Recall 
F1 

We use Accuracy and F1 score as evaluation metrics, and
analyze the Precision and Recall values to better reflect the
model’s ability to distinguish between positive and negative samples. The main parameter settings for the AttTucker
model are shown in Table 5.

Experimental results and evaluation
Performance on general knowledge graph dataset
On the FB15K dataset, we compared our model with other
baseline models, including NTN, CKRL, TransT, DistMult,
Analogy, ComplEx, SimplE, TransE, TransR, and others.
The results are shown in Table 6. It can be observed that
both the Tucker and AttTucker models outperform all the
baseline models in terms of accuracy and F1 value. Notably,

123

1212

Complex & Intelligent Systems (2024) 10:1201–1217
Table 7 Impact of noise ratio on model performance in the FB15K
dataset

Table 6 Results of different models on FB15K
Models

Accuracy

F1 value

NTN [38]

0.665

–

CKRL(LT) [28]

0.818

–

Models

Datasets

Accuracy

F1 value

Tucker

FB15K-N10

0.971

0.973

0.968

0.970

CKRL(LT + PP) [28]

0.819

–

FB15K-N20

CKRL(LT + PP + AP) [28]

0.817

–

FB15K-N30

0.962

0.964

TransT (TT) [39]

0.822

–

FB15K-N40

0.954

0.955

FB15K-N50

0.945

0.948

TransT (TT + DT) [39]

0.824

–

DistMult [31]

0.808

–

AttTucker

FB15K-N10

0.979

0.980

0.974

0.975

Analogy [31]

0.821

–

FB15K-N20

ComplEx [31]

0.818

–

FB15K-N30

0.969

0.971

SimplE [31]

0.815

–

FB15K-N40

0.961

0.963

FB15K-N50

0.955

0.956

AutoSF [31]

0.827

–

TransE [30]

0.868

0.876

TransH [30]

0.912

0.913

TransD [30]

0.913

0.913

TransR [30]

0.902

0.904

Tucker

0.945

0.948

AttTucker

0.955

0.956

the TransE model does not achieve high evaluation results
due to its limitations in handling 1-to-N, N-to-1, and N-toN relations. By introducing more complex relation-specific
parameters, models, such as TransH, TransR, and TransD,
have achieved better evaluation results than the TransE
model. The AttTucker model achieves an F1 value of 0.956
on the FB15K dataset, which is 5.2% higher than the F1 value
of the TransR model. This indicates that modeling the knowledge graph as a core tensor and three factor matrices, along
with the introduction of multi-head attention mechanism,
enables the model to better capture the complex relations
in the knowledge graph and improve its accuracy.
Furthermore, we analyzed the impact of the proportion of
noisy triples in the knowledge graph on the model’s performance, and the results are shown in Table 7. From Table 7, it
can be observed that as the proportion of noisy triples in the
knowledge graph increases from 10 to 50%, both the Tucker
and AttTucker models show a decrease in evaluation performance. The reason for this could be that as the proportion
of noise increases, the triples in the knowledge graph may
become more inconsistent. For example, there may be noisy
triples that contradict other correct triples. This inconsistency
can confuse the model during inference and prediction, leading to a decrease in its performance. It is evident from Table
7 that although the model’s performance decreases with the
increase in the proportion of noise, the evaluation results
remain at a good level. This indicates that while the presence
of noise does have some impact on the model’s performance,

123

our model is still able to maintain relatively stable performance, demonstrating its robustness to noisy triples.
To validate the effectiveness of the AttTucker model in
the knowledge graph quality assessment task, we conducted
a visual analysis of the evaluation results of the AttTucker
model on the FB15K-N50 testing sets, as shown in Fig. 6.
Similar results can also be obtained when using the Tucker
model. Figure 6a illustrates the confidence evaluation results
for negative triples, while Fig. 6b shows the confidence evaluation results for positive triples. By observing Fig. 6a, we
can see that negative triples generally have low confidence
values, and these values are mostly below 0.5. Conversely,
Fig. 6b demonstrates that positive triples generally have
high confidence values, and these values are mostly above
0.5. Such visual analysis helps us intuitively understand the
model’s predictive ability for triple confidence in the knowledge graph, further confirming the superiority and reliability
of the AttTucker model in the task of knowledge graph quality assessment.

Performance on the cybersecurity dataset
In addition, we evaluated the performance of Tucker and AttTucker models on the cybersecurity knowledge graph dataset
CS13K. The results are shown in Table 8. From Table 8, it
can be observed that for the TransE model, as the noise ratio
increases, the accuracy and F1 value gradually decrease. The
noise ratio affects the performance of the TransE model on
the cybersecurity dataset, resulting in lower accuracy and F1
value. The Tucker model demonstrates higher accuracy and
F1 value on the CS13K dataset at different noise ratios. In
contrast, the AttTucker model exhibits better performance
on the CS13K dataset at different noise ratios. Although the
accuracy and F1 score of the AttTucker model decrease with

Complex & Intelligent Systems (2024) 10:1201–1217

1213

Fig. 6 Confidence distribution of
positive and negative triples of
FB15K-N50

Table 8 Impact of noise ratio on model performance in the CS13K
dataset

Relations

Precision

Recall

F1 value

BelongTo

0.868

0.883

0.875

Cause

0.916

0.931

0.923

Exploits

0.882

0.836

0.858

0.866

HasAttackLocation

0.893

0.898

0.895

0.859

0.860

HasAttackTime

0.953

0.946

0.949

0.854

0.855

HasCharacteristics

0.913

0.906

0.909

CS13K-N10

0.951

0.952

HasVulnerability

0.911

0.906

0.908

CS13K-N20

0.935

0.938

Indicates

0.902

0.913

0.907

CS13K-N30

0.922

0.923

Mitigates

0.893

0.907

0.900

CS13K-N40

0.911

0.913

Targets

0.956

0.948

0.952

CS13K-N50

0.893

0.894

Use

0.917

0.899

0.908

CS13K-N10

0.965

0.968

Associate

0.909

0.926

0.917

CS13K-N20

0.950

0.951

Average

0.909

0.908

0.909

CS13K-N30

0.938

0.940

CS13K-N40

0.925

0.926

CS13K-N50

0.908

0.909

Models

Datasets

Accuracy

F1 value

TransE

CS13K-N10

0.881

0.882

CS13K-N20

0.870

0.872

CS13K-N30

0.864

CS13K-N40
CS13K-N50
Tucker

AttTucker

Table 9 The quality evaluation results for different relation types

increasing noise ratio, it maintains stronger robustness compared to the TransE model, enabling it to maintain higher
performance in noisy environments.
We also reported the precision, recall, and F1 value of the
AttTucker model for each specific relation type. We used the
CS13K-N50 dataset, which has a higher noise ratio, for the
quality evaluation. The results are shown in Table 9. By analyzing the precision, recall, and F1 value for each relation
type, we can gain deeper insights into the model’s quality assessment performance across different relation types.
We found that the model exhibits varying precision and
recall across different relation types. For example, relation
types, such as “hasAttackTime” and “targets”, have relatively higher precision and recall, while relation types like

“belongsTo” and “exploits” have relatively lower precision
and recall. This indicates that the model’s quality assessment
capability varies for different relation types, possibly due to
variations in sample features among different relations in the
dataset.
Similarly, we visualized the confidence evaluation results
of the AttTucker model on the CS13K-N50 testing sets, as
shown in Fig. 7. Figure 7a illustrates the confidence evaluation results for negative triples, while Fig. 7b shows the
confidence evaluation results for positive triples. From Fig. 7,
we observed similar results as in the general dataset: the confidence values for negative triples are generally low, with
most values below 0.5. In contrast, the confidence values for
positive triples are generally high, with most values above
0.5. This indicates that the model performs well in quality
assessment of cybersecurity knowledge graphs.

123

1214

Complex & Intelligent Systems (2024) 10:1201–1217

Fig. 7 Confidence distribution of
positive and negative triples of
CS13K-N50

Fig. 8 a Precision and recall values for different thresholds. b The Recall–Precision curves

Moreover, we utilized precision and recall curves to represent the model’s evaluation performance of triple confidence
scores. The threshold used for triple confidence discrimination is adjustable, where triples with confidence scores
higher than the threshold are classified as positive, and those
below it are classified as negative. As depicted in Fig. 8a, as
the threshold increases, precision continually improves while
recall decreases. At lower thresholds, recall is higher, but as
the threshold increases, recall decreases. When the threshold
surpasses 0.5, recall starts to decline significantly, and the
closer the threshold is to 1, the more rapid the decline. This
indicates that the confidence scores of positive samples in
the CS13K-N50 dataset are generally above 0.5, and when
the threshold is higher than 0.5, precision remains at a high
level, indicating that the model has good capability to identify negative samples in the CS13K dataset. Further analysis
of this phenomenon suggests that the higher precision and
lower recall results may stem from stricter discrimination
requirements for negative samples. With higher thresholds,
the model tends to classify triples with lower confidence

123

scores as negative, thereby improving precision. However,
this also leads to some positive triples being mistakenly classified as negative, resulting in lower recall.
On the other hand, the Recall–Precision curve in Fig. 8b
shows that when the recall is less than 0.8, as the recall
increases, precision remains almost constant and maintains
a high value. This may be due to the model’s cautious selection of positive triples at lower recall rates to ensure higher
precision. However, as the recall increases, the model begins
to classify more triples as positive, including some triples
with lower confidence scores, leading to a rapid decrease in
precision. The balancing point of the curve is approximately
around a recall of 0.90, indicating that at this point, the model
achieves high precision while maintaining a good recall rate.
The use of attention mechanisms to capture interactions
and dependencies between entities and relations in the knowledge graph is a key aspect of the AttTucker model. Therefore,
we investigated the impact of multi-head attention on the
model’s performance. As shown in Fig. 9, within a certain
range, increasing the number of attention heads enhances the

Complex & Intelligent Systems (2024) 10:1201–1217

Fig. 9 The impact of the number of heads on the model’s accuracy

accuracy of the model for knowledge graph quality assessment. However, we also observed that as the number of heads
continues to increase, the performance improvement of the
model gradually diminishes until reaching a saturation state.
This phenomenon may be attributed to the working principle
of the multi-head attention mechanism. A smaller number of
heads may not fully capture the complex interaction relationships in the knowledge graph, limiting the expressive power
of the model. Increasing the number of attention heads can
enhance the model’s modeling capability for different entities and relations, thus improving the accuracy. However,
based on the results in Fig. 9, we observed that after the
number of heads reaches 128, further increasing the number
of heads does not lead to significant performance improvements. This suggests that the effective range of the multi-head
attention mechanism has been reached, and additional heads
do not provide additional information gain. These findings
provide guidance for further optimization and design of attention mechanisms to achieve better knowledge graph quality
assessment performance.
Additionally, we also verified the effectiveness of the
model under low-dimensional embeddings to demonstrate
its scalability when evaluating large-scale knowledge graphs.
Table 10 displays the evaluation results of the Tucker model
and the AttTucker model on the CS13K-N50 dataset at different embedding dimensions. It can be observed that as the
embedding dimension increases, the evaluation accuracy of
the model gradually improves. When the dimension is below
100, increasing the embedding dimension further enhances
the model’s accuracy. Moreover, the comparative results also
show that, at the same embedding dimension, the AttTucker
model outperforms the Tucker model in terms of evaluation
accuracy. This indicates that the attention mechanism can
indeed better capture the interaction information between
entities and relations, thereby improving the evaluation accuracy of the model under low-dimensional embeddings. It is
worth noting that at the dimension of 75, the AttTucker model
achieves a accuracy level comparable to that of the Tucker

1215

model at the dimension of 100. This suggests that the addition
of the attention mechanism can compensate for some information loss under low dimensions and significantly enhance
the model’s performance. Furthermore, we observed that at
the dimension of 64, the evaluation accuracy of the AttTucker
model surpasses that of the Tucker model at the dimension
of 75. This further validates the effectiveness of the attention
mechanism in improving the model’s performance under low
dimensions.
Besides, we also tested the impact of path-level information between entities in the knowledge graph on the
performance of the knowledge graph quality assessment
model. In this experiment, we again selected the CS13KN50 dataset with a higher noise ratio for evaluation and
used the accuracy as the evaluation metric. We specifically
focused on examining the performance of path-level information in knowledge graph quality assessment. The evaluation
results are presented in Table 11, where “Path” represents the
evaluation accuracy considering only the path-level information from the CS13K-N50 dataset, and “AttTuc-Path”
represents the final knowledge graph quality assessment
accuracy obtained by integrating the AttTucker model with
the path-level information.
From Table 11, it can be observed that combining pathlevel information with the AttTucker model significantly
improves the model’s predictive performance. By incorporating path-level information, the model is able to comprehensively consider the semantic associations between entities
within the knowledge graph, thereby enhancing the model’s
predictive and assessment capabilities for triple confidence
scores in the knowledge graph. The introduction of pathlevel information enriches the model’s modeling capability
for complex associations between entities in the knowledge
graph, aiding in more accurate judgment of triple confidence.
Although the detailed investigation of path-level information is not the primary focus of this study, this approach does
provide an effective means to enhance the accuracy of knowledge graph quality assessment.

Conclusions and future works
During the construction process of knowledge graphs, it
is inevitable to introduce noise and conflicts. In response
to the quality assessment problem of cybersecurity knowledge graphs, we manually built a cybersecurity knowledge
graph dataset called CS13K. Subsequently, we extended the
UCO ontology and created a new ontology specifically for
the cybersecurity domain. Using this extended ontology,
we leveraged Neo4j to construct the cybersecurity knowledge graph, providing support for cybersecurity situational
awareness, threat identification, and prediction. Lastly, we
proposed a Transformer-based model for knowledge graph

123

1216
Table 10 The impact of
embedding dimensions on the
model’s performance

Table 11 The evaluation results
of each model

Complex & Intelligent Systems (2024) 10:1201–1217

Model

Dimension k
32

64

75

100

150

Tucker

0.671

0.837

0.860

0.894

0.893

AttTucker

0.720

0.877

0.899

0.908

0.908

Dataset

Metrics

AttTucker

Path

AttTuc-Path

CS13K-N50

Accuracy

0.908

0.889

0.947

quality assessment, which demonstrated good evaluation performance under low-dimensional embeddings, showcasing
the scalability of our model in large-scale knowledge graph
datasets. Additionally, experimental results revealed that
incorporating path-level information significantly enhanced
the effectiveness of knowledge graph quality assessment.
Specifically, on the CS13K-N50 dataset, our model achieved
an accuracy of 0.947. In future, we will further expand
our cybersecurity knowledge graph to encompass a broader
range of cyber-attacks and threats. Moreover, we will explore
methods for better integration of other types of data and information, such as cyber traffic data and intrusion detection
system reports, to enhance the utility and comprehensiveness of our knowledge graph. We will also investigate more
efficient knowledge representation algorithms to improve
the performance of our knowledge graph quality assessment
model.
Acknowledgements The authors would like to thank all the anonymous
reviewers for their contribution in improving this manuscript.
Funding This work was supported by the National Natural Science
Foundation of China (Grant no. 61771001).
Data availability For the FB15K dataset used in the paper, it can be
accessed through the following link: https://github.com/zqhead/TransE/
tree/master/FB15k. Additionally, the CS13K dataset is available from
the corresponding author upon reasonable request.

Declarations
Conflict of interest The authors declare that they have no conflict of
interest.
Open Access This article is licensed under a Creative Commons
Attribution 4.0 International License, which permits use, sharing, adaptation, distribution and reproduction in any medium or format, as
long as you give appropriate credit to the original author(s) and the
source, provide a link to the Creative Commons licence, and indicate if changes were made. The images or other third party material
in this article are included in the article’s Creative Commons licence,
unless indicated otherwise in a credit line to the material. If material
is not included in the article’s Creative Commons licence and your
intended use is not permitted by statutory regulation or exceeds the

123

permitted use, you will need to obtain permission directly from the copyright holder. To view a copy of this licence, visit http://creativecomm
ons.org/licenses/by/4.0/.

References
1. Vaswani A, Shazeer N, Parmar N, Uszkoreit J, Jones L, Gomez A
(2017) Attention is all you need. NIPS. https://doi.org/10.48550/
arXiv.1706.03762
2. Wang J, Li X, An X (2022) Modeling multiple latent information
graph structures via graph convolutional network for aspect-based
sentiment analysis. Complex Intell Syst. https://doi.org/10.1007/
s40747-022-00940-1
3. Lal R (2013) Information extraction of security related entities and
concepts from unstructured text. Dissertations & Theses - Gradworks
4. Bridges RA, Jones CL, Iannacone MD, Testa KM, Goodall JR
(2013) Automatic labeling for entity extraction in cyber security.
Comput Sci. https://doi.org/10.48550/arXiv.1308.4941
5. Kim G, Lee C, Jo J, Lim H (2020) Automatic extraction of named
entities of cyber threats using a deep Bi-LSTM-CRF network. Int
J Mach Learn Cybern 11(10):2341–2355. https://doi.org/10.1007/
s13042-020-01122-6
6. Wang X, Liu X, Ao S, Li N, Zhang X (2020) DNRTI: a largescale dataset for named entity recognition in threat intelligence.
TrustCom. https://doi.org/10.1109/TrustCom50675.2020.00252
7. Guo, Y, Liu, Z, Huang, C, Liu, J, Jing, W, Wang, Z, Wang Y
(2021) CyberRel: joint entity and relation extraction for cybersecurity concepts. In: International Conference on Information and
Communications Security (pp. 447–463). https://doi.org/10.1007/
978-3-030-86890-1_25
8. Rastogi N, Dutta S, Christian R, Gridley J, Zaki M, Gittens A
(2021) Predicting malware threat intelligence using KGs. https://
doi.org/10.13140/RG.2.2.12526.54083, arXiv:2102.05571
9. Smith, B, (2012) Ontology. In: The furniture of the world. Brill.
p. 47–68
10. Undercofer J, Joshi A, Finin T, Pinkston J (2003) A target-centric
ontology for intrusion detection. In: Workshop on ontologies in
distributed systems.
11. Iannacone M, Bohn S, Nakamura G, Gerth J, Goodall J (2015)
Developing an ontology for cyber security knowledge graphs. The
10th Annual Cyber and Information Security Research Conference.
https://doi.org/10.1145/2746266.2746278
12. Syed Z, Padia A, Finin T, Mathews L, Joshi A (2016) UCO: A
unified cybersecurity ontology. In: Workshops at the thirtieth AAAI
conference on artificial intelligence

Complex & Intelligent Systems (2024) 10:1201–1217
13. Vorobiev A, Bekmamedova N (2007) An ontological approach
applied to information security and trust. ACIS 2007 Proceedings,
114
14. Pingle A, Piplai A, Mittal S, Joshi A, Holt J, Zak R (2019) Relext:
relation extraction using deep learning approaches for cybersecurity knowledge graph improvement. In: Proceedings of the 2019
IEEE/ACM International Conference on Advances in Social Networks Analysis and Mining. https://doi.org/10.48550/arXiv.1905.
02497
15. Xie L, Hu Z, Cai X, Zhang W, Chen J (2021) Explainable
recommendation based on knowledge graph and multi-objective
optimization. Complex Intell Syst 7(3):1241–1252. https://doi.org/
10.1007/s40747-021-00315-y
16. Verma S, Bhatia R, Harit S, Batish S (2022) Scholarly knowledge
graphs through structuring scholarly communication: a review.
Complex Intell Syst. https://doi.org/10.1007/s40747-022-00806-6
17. Andola N, Prakash S, Gahlot R (2022) An enhanced smart card and
dynamic ID based remote multi-server user authentication scheme.
Clust Comput 25(5):3699–3717. https://doi.org/10.1007/s10586022-03585-4
18. Andola N, Gogoi M, Venkatesan S (2019) Vulnerabilities on hyperledger fabric. Pervasive Mobile Comput 59:101050. https://doi.org/
10.1016/j.pmcj.2019.101050
19. Andola N, Raghav YVK (2021) SpyChain: a lightweight
blockchain for authentication and anonymous authorization in IoD.
Wireless Pers Commun 119:343–362. https://doi.org/10.1007/s1
1277-021-08214-8
20. Zhang Z, Song X, Sun X (2023) Hybrid-driven-based fuzzy secure
filtering for nonlinear parabolic partial differential equation systems with cyber attacks. Int J Adapt Control Signal Process
37(2):380–398. https://doi.org/10.1002/acs.3529
21. Wang W, Han Z, Alazab M (2022) Ultra super fast authentication
protocol for electric vehicle charging using extended chaotic maps.
IEEE Trans Ind Appl 58(5):5616–5623. https://doi.org/10.1109/
TIA.2022.3184668
22. Alazab M, RM SP, Parimala M (2021) Federated learning for
cybersecurity: concepts, challenges, and future directions. IEEE
Transact Industrial Inform 18(5):3501–3509. https://doi.org/10.
1109/TII.2021.3119038
23. Jia Y, Qi Y, Shang H, Jiang R, Li A (2018) A practical approach
to constructing a knowledge graph for cybersecurity. Engineering
4(1):53–60. https://doi.org/10.1016/j.eng.2018.01.004
24. Harley E, Purdy S, Limiero M, Lu T, Mathews W (2018) CyGraph:
big-data graph analysis for cybersecurity and mission resilience.
MITRE CORP MCLEAN VA
25. Kiesling E, Ekelhart A, Kurniawan K, Ekaputra F (2019) The
SEPSES knowledge graph: an integrated resource for cybersecurity. In: International Semantic Web Conference 198–214. https://
doi.org/10.1007/978-3-030-30796-7_13
26. Lehmann J, Bühmann L (2010) ORE-a tool for repairing and
enriching knowledge bases. In: International Semantic Web Conference 177–193. https://doi.org/10.1007/978-3-642-17749-1_12
27. Bougiatiotis K, Fasoulis R, Aisopos F, Nentidis A, Paliouras G
(2020) Guiding Graph Embeddings using Path-Ranking Methods
for Error Detection innoisy Knowledge Graphs. https://doi.org/10.
48550/arXiv.2002.08762

1217
28. Xie R, Liu Z, Lin F, Lin L (2018) Does william shakespeare really
write hamlet? Knowledge representation learning with confidence.
Proc AAAI Conf Artif Intell 32(1). https://doi.org/10.48550/arXiv.
1705.03202
29. Mendes PN, Mühleisen H, Bizer C (2012) Sieve: linked data
quality assessment and fusion. In: Proceedings of the 2012 joint
EDBT/ICDT workshops116–123
30. Jia S, Xiang Y, Chen X, Wang K (2019) Triple trustworthiness
measurement for knowledge graph. In: The World Wide Web Conference 2865–2871. https://doi.org/10.48550/arXiv.1809.09414
31. Zhang Y, Yao Q, Dai W (2020) AutoSF: searching scoring functions
for knowledge graph embedding. 2020 IEEE 36th International
Conference on Data Engineering (ICDE). IEEE, 433–444. https://
doi.org/10.1109/ICDE48307.2020.00044
32. Dash S, Chakraborty C, Giri SK (2021) Intelligent computing on
time-series data analysis and prediction of COVID-19 pandemics.
Pattern Recogn Lett 151:69–75. https://doi.org/10.1016/j.patrec.
2021.07.027
33. Sarkar A, Khan MZ, Singh MM (2021) Artificial neural synchronization using nature inspired whale optimization. IEEE Access
9:16435–16447. https://doi.org/10.1109/ACCESS.2021.3052884
34. Tao H, Cheng L, Qiu J (2022) Few shot cross equipment fault diagnosis method based on parameter optimization and feature mertic.
Measurement Sci Technol 33(11):115005. https://doi.org/10.1088/
1361-6501/ac8368
35. Aziz RM, Hussain A, Sharma P (2022) Machine learning-based
soft computing regression analysis approach for crime data prediction. Karbala Int J Modern Sci 8(1):1–19. https://doi.org/10.33
640/2405-609X.3197
36. Aziz RM, Baluch MF, Patel S (2022) A machine learning based
approach to detect the Ethereum fraud transactions with limited
attributes. Karbala Int J Modern Sci 8(2):139–151
37. Balažević I, Allen C, Hospedales T M (2019) Tucker: Tensor factorization for knowledge graph completion. arXiv preprint arXiv:
1901.09590. https://doi.org/10.18653/v1/D19-1522
38. Wang Z, Zhang J, Feng J, Chen Z (2014) Knowledge graph embedding by translating on hyperplanes. In: Proceedings of the AAAI
conference on artificial intelligence
39. Zhao, Y. Feng H, Gallinari PJE (2019) Embedding learning with
triple trustiness on noisy knowledge graph 21(11):1083

Publisher’s Note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

123
PAPER_TEXT
