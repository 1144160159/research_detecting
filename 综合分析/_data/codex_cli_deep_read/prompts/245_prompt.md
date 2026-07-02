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
# [245] Integrating Entity Attributes for Error-Aware Knowledge Graph Embedding
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
编号：245
题名：Integrating Entity Attributes for Error-Aware Knowledge Graph Embedding
年份：2023
DOI：10.1109/tkde.2023.3310149
来源：IEEE Transactions on Knowledge and Data Engineering
PDF：paper/10.1109_TKDE.2023.3310149.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：无
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\245.txt
- 原始字符数：88052
- 本次发送字符数：88052
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 4, APRIL 2024

1667

Integrating Entity Attributes for Error-Aware
Knowledge Graph Embedding
Qinggang Zhang , Junnan Dong , Qiaoyu Tan , and Xiao Huang

Abstract—Knowledge graphs (KGs) can structurally organize
large-scale information in the form of triples and significantly
support many real-world applications. While most KG embedding
algorithms hold the assumption that all triples are correct, considerable errors were inevitably injected during the construction process. It is urgent to develop effective error-aware KG embedding,
since errors in KGs would lead to significant performance degradation in downstream applications. To this end, we propose a novel
framework named Attributed Error-aware Knowledge Embedding
(AEKE). It leverages the semantics contained in entity attributes
to guide the KG embedding model learning against the impact of
erroneous triples. We design two triple-level hypergraphs to model
the topological structures of the KG and its attributes, respectively.
The confidence score of each triple is jointly calculated based
on self-contradictory within the triple, consistency between local
and global structures, and homogeneity between structures and
attributes. We leverage confidence scores to adaptively update the
weighted aggregation in the multi-view graph learning framework
and margin loss in KG embedding, such that potential errors will
contribute little to KG learning. Experiments on three real-world
KGs demonstrate that AEKE outperforms state-of-the-art KG
embedding and error detection algorithms.
Index Terms—Knowledge graph, graph neural network,
anomaly detection, node representation learning.

I. INTRODUCTION
NOWLEDGE graphs (KGs) can aggregate millions of
relational facts in the form of triples [1], i.e, (head entity,
relation, tail entity). Examples include general-purpose KGs,
e.g., YAGO [2] and DBpedia [3], and domain-specific KGs,
e.g., biomedical KGs [4] and agricultural KGs [5]. KGs are
essential supporters for many knowledge-driven artificial intelligent systems, such as KG-enhanced recommender systems [6]
and KG-based conversational agents [7]. Meanwhile, KG embedding has been intensively studied, which can improve the
generalization and adaptability of KGs in downstream tasks. By
representing entities as continuous vectors and each relationship
as an operation in the same space, such as translation and
projection, we can perform KG inference in continuous spaces
with simple numerical computations.

K

Manuscript received 6 June 2022; revised 31 July 2023; accepted 26 August
2023. Date of publication 5 September 2023; date of current version 8 March
2024. This work was supported by the Research Grants Council of the Hong
Kong Special Administrative Region, China under Grant PolyU 25208322. Recommended for acceptance by X. Chen. (Corresponding author: Xiao Huang.)
The authors are with the Department of Computing, Hong Kong Polytechnic University, Hong Kong (e-mail: qinggangg.zhang@connect.polyu.hk;
hanson.dong@connect.polyu.hk; qiaoytan@polyu.edu.hk; xiaohuang@comp.
polyu.edu.hk).
Digital Object Identifier 10.1109/TKDE.2023.3310149

While many KG embedding algorithms have been explored [8], [9], [10], the impact of erroneous triples has often
been ignored. Manual construction is impractical due to the massive scale of KGs. Most real-world KGs are extracted from web
corpora using heuristic algorithms [3], [11], [12]. A considerable
number of noisy triples were inevitably introduced into KGs due
to the noises in the original sources and the imperfect extraction
algorithms [13]. For example, NELL [14] is a frequently used
KG with 2.4 million triples, with an accuracy of 74%, corresponding to roughly 0.6 million erroneous triples [15]. Errors
in KGs would lead to significant performance degradation in
downstream applications. Thus, it is urgent to develop effective
error-aware KG embedding.
It is nontrivial to enable error-aware learning in KGs, given
that the patterns of KG errors are unknown and diverse [16], [17],
[18]. Recently, a few studies explore guiding the KG embedding
model learning against the impact of erroneous triples [19], [20],
[21]. Particularly, Vault [22] is the first work that performs graph
representation learning while considering erroneous triples during the learning phase. It estimates a probability score of reliability to determine the quality of a triple via several prior models
fitted with existing KGs. The similar concept of judgments for
each triple is also applied in CKRL [23] and NoiGAN [24]. The
former model generates confidence scores for triples via internal
structure information and utilizes them in representation learning to produce robust representations, while the latter improves it
in the aspect of sample selection. The key idea of these methods
is to guide the embedding model to focus on more convincing
triples by exploiting the internal graph structures. However,
merely KG topological structures are often not effective to
support the detection of nontrivial errors [25]. For instance,
given a triple {London, is_larger_than, W ashington} with
sparse graph structure, it is hard to know which London it refers
to, since there are many cities called London. Thus, efforts
have been devoted to employing extra information sources,
such as related webpages [26], external knowledge bases [25]
and annotation information from crowdsourcing websites [27].
But these supplemental sources are often prohibitive to acquire
which impedes its success in practice.
KGs are often associated with fertile and valuable attribute
data, describing the property of entities. Fig. 1 illustrates a
toy KG with six entities. Each entity contains a set of attributes, e.g., the entity M adameCurie has an attribute list
of {birth_date, gender, nationality, language} which indicates its role as a human being, while {latitude, longitude,
population, area} shows M ariaSalomea’s role as a location.

1041-4347 © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

1668

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 4, APRIL 2024

Fig. 1. Running examples of complex errors in real-world KGs. (a) Presents
a KG error with mismatched head/tail entities and relations. This error can be
detected by reasoning over neighboring triples. But, real-world KGs are often
incomplete and noisy. (b) Demonstrates a further difficult case with some key
links missing. In this case, the rich semantics in entity attribute types can facilitate
the detection of errors.

Considering that most entities in KGs are not typed or are very
loosely typed, being able to learn about the semantic portrait of
the entity from the attribute set is valuable.
Modeling and measuring the correlation between entity attributes and KG structure can guide the KG embedding model
learning against the impact of erroneous triples. In real-world
KGs, entity attributes often show high dependency with the
graph structure, i.e., entities with relevant semantic meanings
are usually linked by specific relations. For example, entities with attribute set {latitude, longitude, population, area}
are generally connected to live_in or born_in while entities with {pen_name, writing_style} are more likely connected to author_of . It means that triples whose entities
have inconsistent attributes with its neighboring relations
are more likely to contain noisy facts. Taking the triple
{M adameCurie, spouse_of, M ariaSalomea} in Fig. 1(b)
as example, analyzing the attribute list of M adameCurie and
M ariaSalomea and comparing the learned semantics with the
corresponding relation, it can be easily deduced that this triple is
erroneous since it is impossible to has the relation of spouse_of
between a person and a location. Hence, we propose to enrich the
entity semantics with its attribute list, and measure the degree of
consistency between attributes and graph structure as anomaly
signal to guide the learning process of KGs to enable effective
error-aware KG embeddings.
However, it is still a challenging task to integrate entity attributes into error-aware KG embedding, with two major key challenges. (i) The heterogeneity of entity attribute
makes it hard to utilize. In general, attributes are not uniformly distributed over all entities. As shown in Fig. 1(b),
different entities usually have distinct types or numbers of
attributes. Furthermore, the same entity can represent different roles in different triples. When an entity describes its different roles, it tends to associate with different attribute sets
to represent the certain semantics. For example, an entity of
both scientist and amateur writer prefers an attribute list of
{research_area, citation, h_index} when describes its role
as scientist and {pen_name, writing_style, notable_book}
when it means the status of writer. Therefore, a tailored and
uniform encoder is desired to fuse such heterogeneous attribute

information to depict the various levels of semantics for entities.
(ii) It is hard to leverage the semantics learned from attributes to
help the KG embedding model learn error-aware embeddings.
Entity attributes can be used to implicitly portray the semantics
of entities, but it is hard to integrate different KG components,
i.e., entities, relations and attributes into a suitable vector space
since they always exhibit rather distinct characteristics. Some
existing KG embedding models attempt to integrate attributes
into the learning framework by directly fusing the learned attribute semantics into the entity embedding [28], [29], [30],
[31]. However, in this fusing way, it is hard to measure the
complex correlation and dependency between entity attributes
and knowledge graph structure, which is crucial to guide the
embedding model to filter out noisy information from hidden
erroneous triples.
Through this article, we aim to answer the following research
questions. ❶ How to jointly embed different kinds of KG components, i.e, entities, relations and attributes, into suitable vector
spaces? ❷ How to construct an effective detector that calculates the confidence score for each triple based on the learned
features? ❸ How to make the best of confidence information
learned from the detection module to get the error-aware KG
embeddings? To solve these problems, in this article, we propose
a novel framework named Attributed Error-aware Knowledge
Embedding, i.e, AEKE, that leverages the semantics contained
in entity attributes to guide the KG embedding model learning
against the impact of erroneous triples. The key idea is to guide
the embedding model to focus on more convincing triples by
exploiting the correlation between knowledge graph structures
and entity attributes. Concretely, we designed two triple-level
hypergraphs, i.e, relational hypergraph, and attribute hypergraph, to model the topological structure of the original KG
and its attributes, respectively. A contrastive learning framework
is then used to learn the representation of each instance from
these two different views. Analyzing and mining the unique
structure of KGs and the correlation between graph structure and
attributes, the confidence score of each triple can be calculated
by considering three anomaly signals, i.e., self-contradictory
within the triple, global acknowledgment across triples, and
conformity between attribute and graph structure. We leverage
confidence scores to adaptively update the weighted aggregation
in contrastive learning and margin loss in KG embedding, such
that potential errors would contribute little to KG learning. The
main contributions of this work are concluded as follows:
r In this research, we propose a novel knowledge graph
embedding framework, i.e., AEKE, which leverages the
semantics contained in entity attributes to guide the KG
embedding model learning against the impact of erroneous
triples.
r We design a tailored multi-view contrastive learning framework to use attribute information as a congruent view to
guide the learning process of KGs.
r Based on the KG structure characteristics and the previously learned multi-view features, we propose to measure
the confidence score of each triple by considering anomaly
signals of three levels.

ZHANG et al.: INTEGRATING ENTITY ATTRIBUTES FOR ERROR-AWARE KNOWLEDGE GRAPH EMBEDDING

r We leverage confidence scores to adaptively update
weighted aggregation in the multi-view graph learning
framework and margin loss in KG embedding, such that
potential errors will contribute little to KG modeling.
A preliminary version of this paper was published in the
proceedings of the 31st ACM International Conference on Information & Knowledge Management (CIKM 2022) [32]. In
the conference version, we introduced a contrastive graph learning framework for Knowledge Graph Error Detection, named
CAGED. The key idea of CAGED is to detect the potential
errors from noisy KG by exploiting the internal graph structures.
Despite its superiority over existing error detection models, we
found that there are still two significant limitations that need
to be addressed before its successful application in real-world
scenarios. 1) CAGED performs error detection merely relying on
KG topological structures. However, real-world KGs are often
incomplete and sparse. Simply relying on KG topological structures is often not effective to support the detection of nontrivial
errors with sparse graph structure. 2) Given the detected errors,
it is still hard to get effective KG embeddings for downstream
tasks. A straightforward solution is to retrain the KG by filtering
out all the possible noisy triples. However, we found that it is
infeasible in practice since in real-world KGs, it is difficult to directly conclude whether a triple is true or not without being tested
in practice or strictly and mathematically proven. As shown in
previous study [32], even the SOTA error detection method could
only achieve 60% accuracy. Consequently, directly filtering out
all the possible erroneous triples will lead to severe information
loss, especially for these long-tail entities which only have few
links in the original KG.
In this article, instead of performing KG modeling via a
two-step way, i.e., i) conduct error detection first, and then ii)
retrain the KG by filtering out all the possible noisy triples,
we propose an end-to-end graph learning framework, named
AEKE. While CAGED serves as a KG error detection model
seeking anomaly labels for each triple, our newly proposed
AEKE focuses on error-aware KG embedding learning that
aims to encode entities and relations into a low-dimensional
vector space while considering erroneous triples during the
learning phase. In particular, we extend the preliminary work
as follows: 1) We formally define the task of error-aware KG
embedding and highlight its difference with error detection. 2)
Rather than relying solely on internal topological structures,
we leverage additional information, i.e., entity attributes, to
guide AEKE learning against the impact of nontrivial errors.
3) We introduce a novel training objective function, where the
confidence score is learnable and dynamically updated during
the representation learning phase so that the noisy information
from erroneous triples can be minimized while the valuable
information from correct triple will be mostly preserved during
the training process. 4) More experiments are conducted to
verify the effectiveness of our proposed model on both detection
performance and downstream task of KG completion.
II. PROBLEM STATEMENT
Given a knowledge graph G, we define G = (E, R), indicating
an aggregation of an entity set E and a relation set R. We use
(h, r, t) ∈ T to represent a triple fact inside one KG, where there

1669

TABLE I
NOTATIONS SUMMARY

is a relation r ∈ R linking a head entity h and a tail entity t.
Learning from the KG representation, we use uppercase bold
letters to denote matrices (e.g., W), lowercase bold letters to
represent vectors (e.g., z). We list the major symbols in this
paper in Table 1.
When taking entity attributes into consideration, we use A
to denote the attribute set and define the attributes of entity h in the form of {ah,1 , ah,2 , . . . , ah,|Ah | } where ah,i ∈
A is the ith attribute type and |Ah | is the total number
of attribute types with regard to the entity h. Here, we
only utilize attribute types to quantitatively depict the entity semantics without considering accurate values due to its
low quality. For example, given the entity M ariaSalomea
in Fig. 1, we reconstruct its semantics with the attribute
set {longitude, latitude, population} instead of {longitude :
53.74 W, latitude : 20.77 N, population : 1.5M }. We adopt
E and R to represent the feature matrices of entity and relation, respectively. Similarly, we adopt A to denote the learned
attribute matrix of entities in G, where i-th row of A ∈ RD×FA
represents the feature indicators to the attributes ah,i ∈ A of
entity h ∈ E. D is the max value across the attribute number of
each entity. In our model, these embeddings will be used in two
ways: (i) for representation learning, and (ii) for confidence
learning.
Definition 1. Errors in Knowledge Graph. Given a triple
in a KG, denoted as (h, r, t), if there is a mismatch among
its head entity h, relation r, and tail entity t, then this triple
(h, r, t) is an error. There are two types of mismatching.
First, relevant entities might be connected by wrong relations.
E.g., {ElonM usk, f ounder_of, T esla}, where ElonM usk
is connected with T esla indeed, but he is the CEO, not the
founder. Second, irrelevant entities might be connected. E.g.,
{BruceLee, place_of _birth, England}, in which BruceLee
was born in Los Angeles.
In a KG, it is difficult to directly conclude whether a triple
is true or not without being tested in practice or mathematically
proven. Thus, following previous studies [15], [19], [23], [32],
[33], we introduce the concept of triple confidence and try to
validate the whole KG from the perspective of triples, where the
confidence value indicates the degree of a triple being true.
Definition 2. Triple Confidence. In this article, we introduce
the concept of confidence to measure the correctness of each
triple. Its value is set to be in the range [0, 1]. The closer the
value gets to 0, the more likely the triple is incorrect.

1670

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 4, APRIL 2024

Fig. 2. We perform a relation-induced construction process to build the relational hypergraph, and construct the attribute hypergraph based on entity attributes.
These two hypergraphs can be regarded as congruent views of the target KG. A contrastive learning framework is used to learn the representation of each instance
from these two different views. Meanwhile, a triple confidence estimation module is designed to calculate the confidence score of each triple by considering:
self-contradictory within the triple; local-global consistency in graph structure; and structure-attribute homogeneity. Under the joint adaptive training scheme, we
leverage confidence scores to adaptively update the weighted aggregation in contrastive learning and margin loss in KG embedding, such that potential errors would
contribute little to KG learning.

Definition 3. Error-Aware KG Embedding. Given a KG G,
with noisy triples, we aim to learn low-dimensional representations for all entities E and relations R, i.e., a mapping
{G} → {E, R}, such that all information in correct triples can
be preserved, while the impact of false triples on the embedding
is minimized. The performance of error-aware embedding is
evaluated by applying E and R to downstream tasks.
III. METHODOLOGY
We propose AEKE to learn error-aware KG embedding by
integrating entity attributes. As shown in Fig. 2, AEKE consists
of three key components. ❶ KG representation learning model.
It incorporates a confidence score C(h, r, t) into the traditional
KG embedding model to isolate the impact of noise over embedding vectors. ❷ Triple confidence learning module. It aims
to learn a confidence score C(h, r, t) to measure the correctness
and significance of each triple with the favor of both internal
structural information and external heterogeneous attribute information. ❸ Joint adaptive training scheme. A tailored adaptive
mechanism is applied to optimize the KG representation learning
and confidence learning model under an end-to-end framework.
A. Knowledge Graph Representation Learning
Knowledge graphs can effectively store and handle structured
information of real-world entities and facts, and have been
widely utilized in various knowledge-driven applications. In
fact, real-world KGs always suffer from serious quality problem
since amounts of errors were introduced into KGs in construction phase due to the original noises in sources and the imperfect
extraction methods. However, most existing knowledge graph
embedding methods assume that all triple facts hold true to the
knowledge graph. Therefore, the noisy information is overfitted

into KG embeddings, which leads to significant performance
degradation in downstream tasks.
To eliminate the impact of noisy triples over embedding
vectors, following a previous study [23], [33], we introduce
the concept of confidence to describe whether a triple fact is
noisy or not. Its value is set to be in the range [0, 1]. The closer
the value gets to 0, the more likely the triple is incorrect. With
the introduction of confidence, we can define the new erroraware objective function to eliminate the noisy data from the
learning process of KG embedding model.


max(0, γ + C(h, r, t) · E(h, r, t)
Lemb =
(h,r,t)∈G (h ,r  ,t )∈G 

− E(h , r , t )),

(1)

where E(h, r, t) = eh + er − et 2 is the traditional energy
score for translational embedding models following translation assumption. γ > 0 is the hyperparameter of margin, and
G represents the sampled positive triple set. Here, the triple
confidence C(h, r, t) forces our model to pay more attention
to those more convincing facts. For pair-wise training, since
there are no explicit negative triples in KGs, we sample negative
triples complying with the following rules:
G  = {(h , r, t) | h ∈ E} ∪ {(h, r, t ) | t ∈ E}
∪ {(h, r , t) | r ∈ R} , (h, r, t) ∈ G.

(2)

It means that one entity or relation in a positive triple is randomly
replaced by another entity or relation in the overall set. Note that
different from TransE, we also add relation replacements for
better performances. The corruption of entity (relation) might
lead to false negative samples. To this end, we discard all triples
already in G from G  to make sure our generated negative triples
are truly negative.

ZHANG et al.: INTEGRATING ENTITY ATTRIBUTES FOR ERROR-AWARE KNOWLEDGE GRAPH EMBEDDING

1671

B. Triple Confidence Learning With Entity Attributes
To enhance the robustness of our error-aware KG embedding
model, we learn a confidence score C(h, r, t) for each triple. As
illustrated in Fig. 2, our key idea is to measure the correctness and
significance of each triple by exploiting the correlation between
knowledge graph structures and entity attributes. In the real
world, KGs are often accompanied by entity attributes, which
have three paradigms as follows.
r In triple level, relations can be interpreted as translations
operating on the low-dimensional embeddings of the entities. So, the more a triple fits the translation assumption,
i.e., h + r ≃ t, the more convincing this triple should be
considered.
r In graph level, the connected triples that share the same
entity are always semantically relevant. Intuitively, a KG
can be regarded as a social group, where each triple is an
individual. The degree of acknowledgements from neighboring triples to the target triple reflects whether the target
triple can be properly integrated into the society.
r Entity attributes often show high dependency with the
graph structure, i.e., entities whose attributes show relevant
semantic meanings are usually linked by specific relations.
It means triples whose entities have inconsistent attributes
with its neighbors are more likely to contain noisy facts.
Based on these observations, we propose a novel confidence
learning model to answer the research problems mentioned at
the beginning of this paper. To model the different components
in KGs, i.e., entity, relation and attribute, into suitable vector
spaces, we proposed a multi-view knowledge graph learning
framework in which a dual-view structure information encoder
and a relation-specific attribute encoder are designed to model
the topological KG structure and entity attributes, respectively.
Specifically, we first design two triple-level hypergraphs, i.e.,
relational hypergraph and attribute hypergraph to model the
topological structure of the original KG and its attribute, respectively. And then we employ a unified contrastive learning
framework to model their dependency. To construct an effective
detector that calculates the confidence score for each triple based
on the learned features, we propose to measure the confidence
score of each triple by considering three anomaly signals, i.e.,
self-contradictory within relational triple structure, global consistency across triples, and attribute-structure dependency.
1) Multi-View Construction: Knowledge graph embedding
projects entities and relations into low dimensional vector space,
which has been successfully applied in KG-based tasks. However, the existing embedding approaches only model entities
and their relations within triples, ignoring the global correlation
among triples in KGs. To model the complex topological graph
structure, in this article, we propose a novel view towards
knowledge graph modeling that augments the target KG into
hyper-views (triple-level), by regarding each relational triple as
nodes. Concretely, we perform a relation-induced construction
process to build the relational hypergraph. In essence, we follow
one strategical criterion: we regard each relational triple as nodes
and link them in the relational hypergraph if they share the same
entity in the original KG. Such triple-level transformation could
filter out low-level information without changing the structure of

Fig. 3.

Triple feature extraction for local relational structure.

possible errors in original KGs since a KG error usually occurs
inside a triple as a mismatch of the head entity, tail entity, and
their corresponding relation.
Definition 4. Relational Hypergraph. Given a knowledge
graph G = {(h, r, t)|h, t ∈ E, r ∈ R}, the corresponding rela A
r , X
r ),
tional hypergraph is the triple-level graph Gr = (V,


where V and Ar are the set of nodes and adjacency metric
r = {Γ(h, r, t) | (h, r, t) ∈ G} represents the
respectively. X
 where Γ(·) is a concatenation function.
feature matrix of V,


Ar (v, u|u, v ∈ V) = 1, if u and v share the same entity in the
original KG, i.e., G.
When taking entity attributes into consideration, we build
another triple-level graph, i.e., attribute hypergraph, to reconstruct the knowledge graph from the perspective of attributes.
Specifically, we treat each triple in the original KGs as an
individual instance and reconstruct its semantics with the feature
learned from the attribute sets of its head and tail entity.
Definition 5. Attribute Hypergraph. Given the same knowledge graph G = {(h, r, t)|h, t ∈ E, r ∈ R}, with entity attribute
set A = {{ah,1 , ah,2 , . . . , ah,|Ah | }|h ∈ E} where ah,i is the ith
attribute type for entity h, the attribute hypergraph can be denoted as Ga = (Va , Aa , Xa ), where Va and Aa are the set of
nodes and adjacency metric respectively, which have the same
structure with Gr . And Xa represent the feature matrices of
each node vi ∈ Va learned from corresponding entity attributes.
These two hypergraphs can be regarded as congruent views of
the target KG. The relational hypergraph models the correlation
between relational triples, while the attribute hypergraph represents the distribution of entity attributes. Considering that entity
attributes always show high dependency with graph structure,
i.e., entity attributes are always linked with certain relevant
relations, for normal triples in KGs, we can easily find enough
relevant attributes in attribute hypergraph to reconstruct its
semantics learned from relational hypergraph. Thus, it helps
us assess the trustworthiness of each triple in the original KG by
measuring the consistency between its representations learned
from these two views.
2) Learning From View I: Relational Hypergraph: Existing
KG embedding approaches only model entities and their relations within triples, ignoring the global correlation among triples
in KGs. In this section, we propose a new graph encoder in a
dual-view which learns both the local structure within relational
triples (local view), and the contextual information buried among
their neighboring community simultaneously (global view), as
shown in Fig. 3.
Local View of Relational Structure Modeling: Constructing
relational hypergraph from the original knowledge graph, in
some way, may lose some local structure information, which
means the translational or sequential structure inside a triple
(head → relation → tail). Since every instance in the relational

1672

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 4, APRIL 2024

hypergraph is transformed from a corresponding triple (h, r, t)
in the original knowledge graph, we first randomly initialize the
embedding of entities and relations in the original knowledge
graph, and then adopt a local information modeling layer, i.e,
a set of BiLSTM units, to to integrate the embedding of head
entity, relation and tail entity (eh , er , et ) into triple-level representation p. Taking the ith triple (h, r, t) as an example, our
local information modeling layer is formulated as follows.
pi = Glocal (h, r, t) = fconcat (fBiLST M (eh , er , et )).

(3)

The output triple embedding pi is supposed to well capture the
local relational structure of the input triple. Thus, we use them
as the initial embedding of each node in relational hypergraph.
Global View of Neighbor Information Aggregation: Except
the local structure inside triples, abundant contextual information among a community of triples are useful in detecting
anonymous triples. To model such global contextual information, an intuitive way is to use graph neural network (GNN) or
its variants. However, existing graph neural networks are not
optimal for KG embedding task since they ignore the existence
of anomalous instance in the graph. In other words, potential
noisy triples may draw relatively equal attention as normal
ones, which leads to a more challenging triple representation
learning. To reduce impacts from potential anomalies, we adopt
an attention-based architecture, i.e., Gglobal , to selectively aggregate messages from the neighboring triples.
Given an anchor triple pi ∈ Rd in relational hypergraph,
we update its embedding by attending over its neighborhoods’
features, e.g., {p1 , p2 , . . . , pm }, pm ∈ Rd through a two-layer
graph attention network. A single graph attentional layers is
given by:
attij = fatt (Wpi , Wpj ) .

(4)

Here, attij is a raw attention coefficient which indicates the
importance of triple j to triple i. W ∈ Rn×d is a learnable
linear transformation matrix to project the initialized triple
representations into the same high-level vector space. fatt is
the attentional function. To make attention coefficients easily
comparable across different triples, We normalize the attention
values by applying a softmax function:
exp (attij )
.
αij = m
k=1 exp (attik )

(5)

Then, the final triple embedding in relational hypergraph can
be calculated with a nonlinearity sigmoid function as follows.
⎞
⎛
m

(6)
αij Wpj ⎠ .
xi = σ ⎝
j=1

3) Learning From View II: Attribute Hypergraph: Most of
the current knowledge graph embedding frameworks focus on
learning the inner structure of relational triples. However, entity
attributes contain amounts of accurate and targeted semantic
information that can describe entities quantitatively, which is
equally valuable to enable effective KG embedding. To facilitate information transfer between entity attributes and the
target KG for error-aware embedding, we propose a tailored

Fig. 4. Attribute triple Embedding initialization by capturing attribute information.

a relation-specific encoder, i.e., gattr learn the attribute-based
triple representation from attribute hypergraph, as shown in
Fig. 4.
Attribute Hypergraph Embedding: Attributes are not uniformly distributed over all entities. In general, different entities
always have different types or numbers of attributes, even the
same entity may represent different roles in different triples.
When an entity describes its different roles in different triples,
it tends to associate with different attribute sets to represent
the certain semantics. Thus, it is necessary to choose which
attribute corresponds to the semantics the current entity represents when we want to reconstruct triple-level semantics based
on the attributes of its head/tail entities. To capture which level
of information the current entity mainly focuses on, we therefore
adopt the relation-specific mechanism, which uses the relation
type as an indicator to lead the selection of entity attributes in
different triples.
Given a triple (h, r, t), in order to extract the rich semantics
information from more valuable attributes of entity h and t, we
first splice the embeddings of attribute type into an embedding
matrix, denoted by Mh = {ah,1 , ah,2 , . . . , ah,|Ah | } and Mt =
{at,1 , at,2 , . . . , at,|At | }, then feed them to an attention module
with relation embedding er to get the integrated representation
êh and êt for target entity h and t. Take entity h as an example:
atth,i = fatt (femb (er ), femb (ah,i )),

(7)

exp (atth,i )
,
αh,i = |A |
h
j=1 exp (atth,j )

(8)

where femb and fatt are all single-layer feed-forward neural
networks. The αh,i is the normalized attention weight of attribute ah,i . Now, we can compute the aggregated attribute-based
representation êh of Ah , which is the weighted sum of all the
transformed representation of attributes in it:
êt =

|At |


αt,i ∗ femb (at,i ) .

(9)

i=1

Then given a triple (h, r, t) in attribute hypergraph, we can get
the attribute-based entity representations, i.e., êh and êt , by using
this attribute encoder. The final attribute-based triple embedding
qi can be calculated as:
qi = fconcat (êh ; er ; êt ).

(10)

Aggregating Neighbor Attribute Information: Homogeneously,
given an anchor triple qi ∈ Rd in attribute hypergraph, we
follow the global view of relational hypergraph to update the
embedding by attending over neighbors’ features of qi , e.g.,
{q1 , q2 , . . . , qm }, qm ∈ Rd through the same two-layer graph

ZHANG et al.: INTEGRATING ENTITY ATTRIBUTES FOR ERROR-AWARE KNOWLEDGE GRAPH EMBEDDING

attention network:

⎛
zi = σ ⎝

m


⎞
αij Wqj ⎠ .

(11)

j=1

4) Model Learning: To learn discriminative features from
both relational hypergraph and attribute hypergraph, we adopt
a tailored contrastive loss to optimize the proposed multi-view
knowledge graph neural network.
Contrasting Between Structure and Attribute Views: The
relational hypergraph models the global correlation between
relational triples, while the attribute hypergraph represent the
distribution of entity attributes. These two hypergraphs can be
regarded as congruent views of the original KG since entity
attributes always show high dependency with graph structure.
In this paper, we adopt the normalized temperature-scaled cross
entropy loss as our contrastive objective and train the encoders by
maximizing the mutual information between triple embeddings,
i.e., xi and zi , learned from these two views.
exp (sim (xi , zi ) /τ )
,
j∈{1,2,...,N }\{i} exp (sim (xi , zj ) /τ )
(12)
where τ denotes the temperature parameter. sim(xi , zi ) denotes
the cosine similarity of triple embedding xi from relational
hypergraph and zi learned from attribute hypergraph.
Contrasting Between Local and Global Views: As mentioned
at the beginning of Section III-B, the connected triples that share
the same entity are always semantically relevant, and thus the
degree of acknowledgements from neighboring triples to the target triple reflects whether the target triple can properly integrate
into the community. To model such paradigm between individual
triple and its community, we propose another contrastive training
objective by maximizing the mutual information between pi
and xi . Here, pi is the embedding of ith triple learned from
local relational structure (3), while xi is the embedding of the
same triple that learned by aggregating information from its
neighboring community (6).
Lsa (xi , zi ) = − log 

exp (sim (pi , xi ) /τ )
.
j∈{1,2,...,N }\{i} exp (sim (pi , xj ) /τ )
(13)
Finally, by combining the above two losses, we have our final
contrastive objective function, i.e Lcon defined below:
Llg (pi , xi ) = − log 

1 
(Lsa (xi , zi ) + Llg (pi , xi )) .
2 N i=1
N

Lcon =

(14)

5) Triple Confidence Estimation: Based on the KG
paradigms and the previously learned multi-view features,
we propose to measure the triple confidence by considering
three anomaly signals: self-contradictory within local relational
structure, global consistency across triples, and attributestructure dependency.
Self-Contradictory Measurement: In triple level, relations can
be interpreted as translations operating on the low-dimensional
embeddings of the entities. So, the more a triple fits the translation assumption, i.e., h + r ≃ t, the more convincing this triple
should be considered. Existing KG embedding algorithms have

1673

developed various energy functions to model the translational
structure for better learning embeddings. In this paper, we take a
simple squared euclidean distance to measure the unconformity
of each triple with translation assumption, and define the local
triple confidence LT (h, r, t) as follows.
LT (h, r, t) =

1
1 + e−eh +er −et 2

.

(15)

Global Acknowledgement Estimation: The connected triples that
share the same entity are always semantically relevant, and thus
the degree of acknowledgements from neighboring triples to
the target triple reflects whether the target triple can properly
integrate into the KG. Inspired by social identity theory [34],
[35], the KG can be regarded as a social group, where each
triple is an individual. The degree of acknowledgements from
other individuals to the targeted individual (target triple) reflects
whether the targeted individual can properly integrate into the
society, i.e., the KG. We believe that only a true triple can achieve
popular recognition from its neighboring triples. In other words,
if a triple is well accepted, we tend to believe that it is trustworthy.
Hence, we define another confidence function to measure the
global acknowledgement of target triple (h, r, t).
GT (h, r, t) = sim(pi , xi ),

(16)

where pi = Glocal (h, r, t) is the local embedding of triple
(h, r, t), and xi = Gglobal (h, r, t) represent the feature learned
from its global context.
Structure-Attribute Dependency Estimation: The relational
hypergraph models the correlation between relations, while
the attribute hypergraph represent the distribution of entity
attributes. Considering that entity attributes always show high
dependency with graph structure, i.e., entity attributes are always linked with certain relevant relations, for normal triples in
KGs, we can easily find enough relevant attributes in attribute
hypergraph to reconstruct its semantics learned from relational
hypergraph. So, the consistency between its representations
learned from these two views can be regarded as an effective
anomaly signal to assess the trustworthiness of each triple in the
original KG.
AT (h, r, t) = sim(xi , zi ),

(17)

where xi = Glocal (h, r, t), zi = gattri (h, r, t) are the representations of triple (h, r, t), learned from relational hypergraph and
attribute hypergraph, respectively.
Triple Confidence: Finally, we measure the confidence score
of each triple based on the previously learned features and define
final score functions for detecting potential errors as follows:
C(h, r, t) = σ(LT (h, r, t) + λ1 · GT (h, r, t)
+ λ2 · AT (h, r, t)),

(18)

where LT (h, r, t) reflects the degree of self-conformity within
the local relational triple, GT (h, r, t) denotes the consistency
between local-global structure, AT (h, r, t) measures the similarity of the same sample between relational hypergraph and
attribute hypergraph. When the confidence value is larger, the
triple (h, r, t) is more likely to be a normal one.

1674

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 4, APRIL 2024

r Q5 (Section IV-F): Is our proposed AEKE an efficient

Algorithm 1: Error-Aware KG Embedding Learning.

method compared to baselines?

r Q6 (Section IV-G): How does our proposed AEKE perform
error-aware embedding in real-world scenarios?
A. Datasets

C. Joint Adaptive Training Scheme
In this section, we introduce the details of the training scheme
to answer the third research question mentioned at the beginning
of this paper, i.e., how to make the best of confidence information
learned from the detection module to get the error-aware KG
embeddings. Concretely, we define a comprehensive objective
function to tightly integrates the KG embedding model and confidence learning model that work jointly to get the error-aware
embeddings. The learning process of AEKE is summarized in
Algorithm 1.
L = Lcon + βLemb .

(19)

Under this scheme, KG representation learning and confidence
learning mechanism could be mutually beneficial for each other
in each iteration that the former provides a promising embedding in latent space for the latter, while the latter singles out
less credible triples to improve the performance of the former.
Through iteratively joint estimation of triple confidence, we aim
at reducing impacts from potential anomalies and learn optimal
representation of the target KG.
IV. EXPERIMENTS
In this section, we conduct comprehensive experiments on
a variety of real-world KGs to verify the effectiveness of the
proposed framework AEKE. Specifically, we aim to answer the
following questions.
r Q1 (Section IV-B): Is our proposed AEKE valid and effective for distinguishing noisy triples?
r Q2 (Section IV-C): How effective is the KG embeddings
learned by AEKE in comparison with the state-of-the-art
KG embedding models?
r Q3 (Section IV-D): How does each component of AEKE
contribute to its prominent performance?
r Q4 (Section IV-E): How do the hyperparameters influence
the performance of AEKE?

We evaluate our proposed AEKE on three real-world benchmark datasets, including FB15K-237, YAGO15 K, and DB15 K.
Due to the human curation, these benchmark datasets contain highly reliable facts. Following prior work [23], [24],
we amplify each of three datasets by incorporating 5%
and 15% noisy triples to imitate real-world errors, respectively. Since most errors in real-world KGs derive from
the misunderstanding between similar entities, e.g., the error
(N ewton, N ationality, England) is more likely to occur in
real-world KGs than (N ewton, N ationality, Google), in this
paper, the noisy triples are appropriately generated in the following way. Given a positive triple (h, r, t), the head or tail
entity is replaced to form a harder and more confusing negative
triple (h , r, t) or (h, r, t ), where h (or t ) should have appeared
in the head (or tail) position with the same relation in the
dataset.
FB15K-237 [36] stands as the widely-applied subset with 114
relations and 10054 entities under Freebase, which is known as
the huge knowledge base with over 1 billion triples. FB15K237 proves to be better than FB15K-237 by getting over the
challenges FB15K-237 faced for inverse relations and keeping
symmetrical, asymmetrical and combinatorial relationships, as
well as the attributes.
DB15K [37] is a subset of Wikidata, making up for the
weakness of Wikipedia. To avoid test leakage, it also excludes
inverse relations using the same procedure as the derivation of
FB15K-237.
YAGO15K [38] augmented WordNet with over one million
entities, transforming WordNet from the plane data to a knowledge graph. YAGO15 K gets formed based on YAGO aligned
with the entities in Freebase.
B. Capability of AEKE in Distinguishing KG Errors (Q1)
In this section, we conduct experiment on KGs in terms of
KG error detection task to verify the capability of AEKE in
distinguishing errors. Specifically, we rank all the triples in the
target KG according to their confidence scores in ascending
order. The top ranked triples are treated as potential errors. The
experiments are conducted on three benchmark datasets, including FB15K-237, DB15 K and YAGO15 K with noisy triples to be
different ratios of 5% and 15% of KGs. In the following part, we
elaborate the experiment settings and prerequisites of baseline
models and evaluation metrics.
1) Baselines: From three aspects we single out models as
the baseline to evaluate the error detection performance, among
which CKRL [23] and NoiGAN [24] represent the error-aware
embedding methods; TTMF [15], CAGED [32], and CrossVal [25] represent the state-of-the-art error detection alternatives; TransE [39], DistMult [40], ComplEx [41], SimplE [42]

ZHANG et al.: INTEGRATING ENTITY ATTRIBUTES FOR ERROR-AWARE KNOWLEDGE GRAPH EMBEDDING

TuckER [43] and EARL [44] are picked for being representative knowledge graph embedding methods. The details of the
baseline methods are elaborated as follows:
TransE [39] assumes that entities and relations are embedded
in the same space, allowing for the approximation of the tail
entity related to a given head entity and relation after training.
As a result, the original triples are transformed into word vectors
using either L1 or L2 norm.
DistMult [40] is a bi-linear model that calculates the confidence of potential semantics for entities and relations in the
vector space. It simplifies the RESCAL model by representing
the relational matrix as a diagonal matrix, removing the limitation. However, DistMult can only handle symmetric relations in
a knowledge graph.
ComplEx [41] is another notable bi-linear model that builds
upon DistMult. It improves upon DistMult by introducing complex numbers and expanding the model into the complex number
space. This enhancement enables ComplEx to handle both symmetric and asymmetric relations in a knowledge graph.
SimplE [42] SimplE embeddings offer interpretability and
allow the integration of specific background knowledge by
employing weight tying. It provides evidence of its complete
expressiveness and establishes a bound on the size of its embeddings to ensure full expressivity.
TuckER [43] is a linear model that offers a relatively simple
approach to link prediction in knowledge graphs. It leverages
the Tucker decomposition of a binary tensor containing known
facts.
EARL [44] focuses on learning embeddings for a specific
group of entities referred to as reserved entities. To obtain
embeddings for the entire set of entities, it encodes their
unique characteristics by considering their connected relations,
k-nearest reserved entities, and multi-hop neighbors.
TTMF [15] utilizes semantic information to calculate the
trustworthiness of triples in order to distinguish between normal
instances and anomalies. This differentiation is achieved through
corresponding confidence values.
CAGED [32] By joint training with KG embedding and
contrastive learning loss, CAGED assesses the trustworthiness
of each triple based on two learning signals, i.e., the consistency of triple representations across multi-views and the
self-consistency within the triple.
NoiGAN [24] aims to learn noise-aware knowledge graph embeddings. It combines error detection and completion tasks using
a unified Generative Adversarial Networks (GAN) framework.
CKRL [23] is an advanced confidence-aware knowledge representation learning method. It aims to overcome the assumption
made in conventional KRL, where all triples in the original graph
are considered correct. CKRL focuses more on triples with lower
confidence, as they may indicate potential noise.
CrossVal [25] suggests using an external human-curated
knowledge graph as an auxiliary information source to aid in
error detection within a target knowledge graph. The external
knowledge graph is constructed based on human-curated knowledge repositories and tends to have high precision.
2) Evaluation Protocol: The implementation of both the
baselines and our proposed framework is carried out using PyTorch. For the baseline methods, we utilize the publicly available

1675

codes for conducting our experiments. Training of our proposed
framework and the baselines is performed on a Nvidia 3090 GPU
server. Specifically, we employ the Adam optimizer with a fixed
batch size of 256 to optimize all models. The model parameters
are initialized using the default Xavier initializer, and the initial
learning rate is set to 0.01. Additionally, we maintain a fixed
embedding size of 100 for all models.
In order to assess the performance of the baseline approaches,
we utilize ranking measures. These measures involve calculating
ranks based on the scores assigned by the models to the triples
in the knowledge graph (KG). A lower score indicates a lower
likelihood of a triple being correct. The triples in the target KG
are ranked in ascending order according to their scores, where the
top-ranked triples have a higher probability of being incorrect.
To provide a fair assessment of KG validation performance, we
employ the following two evaluation measures.
Precision@K assesses the percentage of real anomalies found
in the first K queries.
| Errors Discovered in Top K Ranking |
.
K
(20)
Recall@K measures reflects the percentage of real anomalies
found in the overall number of ground truth anomalies.
Precision@K =

Recall@K =

| Errors Discovered in Top K Ranking |
. (21)
| Total number of Errors in the KG |

3) Experimental Results: We now answer the first question,
i.e., Q1 evaluating the effectiveness of AEKE. The experimental
results are summarized in Table II. We have three observations
as follows.
Obs. 1. AEKE demonstrates superior performance compared
to both embedding methods and state-of-the-art error detection baselines. Our proposed model, AEKE, outperforms all
baselines in terms of recall and precision evaluation metrics.
Specifically, at a 5% anomaly ratio and k value of 5%, AEKE
achieves a 1.8% improvement over the second-best method.
Obs. 2. Knowledge graph embedding baselines, such as
TransE, ComplEx, and DistMult, generally yield satisfactory
results. However, when compared to tailored error detection
and error-aware methods, these knowledge graph representation
baselines exhibit inferior performance. The reason behind this is
that KG embedding frameworks do not account for errors in the
KG, resulting in the inability to learn discriminative representations for normal and noisy triples. This outcome emphasizes
the need for an error-aware representation learning framework
to achieve robust KG embeddings.
Obs. 3. The inclusion of auxiliary human-curated information
proves to be useful in detecting errors in KGs. For instance,
CrossVal, which utilizes an external human-curated KG as auxiliary information, demonstrates better detection performance
than other baselines. However, our model surpasses it due to
its ability to leverage the relational structure within triples, the
global contextual structure across triples, and the rich semantics
derived from entity attributes. This comprehensive approach
allows our model to excel in error detection.

1676

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 4, APRIL 2024

TABLE II
ERROR DETECTION RESULTS OF PRECISION@K AND RECALL@K BASED ON THE THREE DATASETS WITH ANOMALY RATIO = 5%

C. Quality of KG Embeddings Leaned by AEKE (Q2)
The goal of our model is to learn effective knowledge graph
embeddings that could facilitate various applications. To verify
the quality and effectiveness of learned embeddings, we evaluate
AEKE in terms of KG completion task. Knowledge graph completion is a traditional evaluation task that aims to complete the
incomplete triples that lack a head entity, tail entity or relation.
In the following part, we elaborate the experiment settings and
prerequisites of baseline models and evaluation measurements.
1) Baseline Methods: To validate the quality of KG embeddings leaned by our proposed AEKE, we compare it with the
strongest baselines according to our best knowledge. Following
the taxonomy aforementioned in Section V, we divide all baselines into three categories: (i) embedding-based: TransE [39],
SimplE [42], EARL [44]; (ii) state-of-art completion models:
RGCN [45] and RGHAT [46]; (iii) Error-aware embedding
method: NoiGAN [24] and CKRL [23].
2) Evaluation Protocol: In this research paper, our primary
focus revolves around entity prediction. To provide a more
precise description, we establish the KG completion as a task
that involves predicting either the head entity in a given query
(?, r, t) or the tail entity in a given query (h, r, ?). To be specific,
we mask the head or tail entity of each triple in the test dataset and
require each method to predict the missing entities. To maintain
consistency with the previous study [23], [24], we utilize two
evaluation metrics: 1) Mean Rank of correct entities, denoted as
MRR, and 2) Hits@K, which denotes the proportion of correct
answers ranked within the top K positions.
3) Experiment Results: We conduct the experiments on
three benchmark datasets, including FB15K-237, DB15 K and
YAGO15 K with noisy triples to be different ratios of 5% and
15% of KGs. Evaluation results are shown in Table III. In
general, we have the following observations.

Obs. 1. AEKE consistently outperforms the embedding-based
models and other tailored KG completion competitors over
different anomaly ratios, which verifies the quality and effectiveness of KG embeddings learned by AEKE.
Obs. 2. Error-aware embedding methods, including NoiGAN,
CKRL and our proposed AEKE, always show better performance than other models. And the embedding-based methods,
i.e., TransE, SimplE, and EARL, are always surpassed by both
KG completion models, i.e., RGCN and RGHAT. It is because
embedding-based methods that are trained in a pair-wise mode
and only model the local relational structure of triples, are more
likely to over-fit noisy information.
Obs. 3. As the anomaly rate increases, the performance gap
between the baseline models and our AEKE become more
significant. Specifically, comparing with second-best method,
our AEKE just gets the improvements of 0.3%, 0.6% and 0.5%
on FB15k-237, DB15 K and YAGO15 K respectively. As the
anomaly rate increases to 15%, our AEKE gets more significant
improvements of 0.8%, 1.2% and 1.6% on FB15k-237, DB15 K
and YAGO15 K, respectively. It indicates that our proposed
framework is more robust, especially for KGs with larger scale
of noises.
D. Ablation Study (Q3)
We now investigate the third question. In this part, four pairs
of variants of AEKE are used for this ablation study.
1) The Role of Attribute Hypergraph Encoder: Entity attributes can be used to implicitly portray the semantics of
entities, but it is hard to integrate different KG components,
i.e., entities, relations and entity attributes into a suitable vector
space since they always exhibit rather distinct characteristics. To
leverage the semantics contained in entity attributes to guide the
KG embedding model learning against the impact of erroneous

ZHANG et al.: INTEGRATING ENTITY ATTRIBUTES FOR ERROR-AWARE KNOWLEDGE GRAPH EMBEDDING

1677

TABLE III
RESULTS OF KNOWLEDGE GRAPH COMPLETION

triples, in this article, we first build an attribute-based hypergraph
and then propose a novel attribute encoder to model the attribute
information with heterogeneous structure. To test the effect of
our proposed attribute encoder, we remove the attribute view
from AEKE, and denote the variant as AEKE(none). In this
part, we compare our model and its variant with three KG
embedding models in terms of the capability in distinguishing
KG errors. Specifically, we use TransE, ComplEx and DistMult
to model the KGs without attribute information and denote
them as TransE(none), ComplEx(none) and DistMult(none),
respectively. In the same time, we directly integrate attributes
into KG embedding frameworks by initializing the entity feature
with the concatenated attribute semantics, and denote them as
TransE(attr), ComplEx(attr) and DistMult(attr).
As shown in Table IV, after introducing the attributes, all
baselines as well as our model, present better performance,
which verifies the value and importance of attribute information
in KG representation learning. But the improvement of the
baselines is quite marginal compared to our model. Particularly,
there is only an increase of 0.99%, 0.65%, 1.75% for TranE,
ComplEx and DistMult, respectively. And our model shows a
significant improvement of 3.97% at K equals 1%. It is because
these baseline models attempt to integrate attributes into KG
embedding framework by directly initializing the entity feature
with the learned attribute semantics and train the model in pairwise mode. However, in this fusing way, it is hard to measure the
complex correlation and dependency between entity attributes
and knowledge graph structure, which is crucial to guide the
embedding model to filter out noisy information from hidden
erroneous triples.

TABLE IV
RESULTS OF PRECISION@K% AND RECALL@K% BASED ON FB15K-237
WITH ANOMALY RATIO = 5%

2) The Role of Relational Hypergraph Encoder: To assess
the effectiveness of capturing translational structure within each
triple using a local information modeling layer, we introduce two
variations: AEKE_LSTM and AEKE_Concat. AEKE_LSTM

1678

Fig. 5.

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 4, APRIL 2024

KG completion results of AEKE variants based on the three datasets with anomaly ratio = 5%.

replaces the Bi-LSTM units in our local information modeling
layer with LSTM, while AEKE_Concat removes the Bi-LSTM
units and directly concatenates randomly initialized embeddings
of the head entity, relation, and tail entity to form the local
representation of each triple. Our results indicate a significant
drop in performance for both variants, with AEKE_LSTM outperforming AEKE_Concat. This outcome is expected because
a simple concatenation approach can lead to the loss of local
structural information.
Next, to validate the error-aware functionality of our
global encoder, we substitute our tailored graph encoder
with RGCN [45] and RGHAT [46], creating AEKE_GCN
and AEKE_GAT, respectively. As observed from Fig. 5,
AEKE_GAT outperforms AEKE_GCN, but there remains a
noticeable gap compared to our model. This gap arises due to
RGCN assuming that all observed triples in the KG are correct,
which can result in overfitting on noisy facts and the failure to
detect errors. On the other hand, RGHAT employs an attention
mechanism to learn KG representations, which has the potential
to filter out some noisy information. However, AEKE_GAT still
does not exhibit excellent performance in the error detection
task. This can be attributed to the fact that RGHAT applies
the attention mechanism from the perspective of entities and
relations, whereas KG errors often occur at the triple level, where
mismatches between the head entity, tail entity, and the corresponding relation are common. In contrast, our graph encoder
incorporates a customized error-aware attention layer that takes
triple-level embeddings as input. This tailored approach enables
us to effectively filter out noisy facts.
3) The Role of Joint Adaptive Training Scheme: To evaluate
the effectiveness of our joint optimization approach, we conduct
experiments using different training losses, resulting in three
variants: AEKE_SA, AEKE_LG, and AEKE_KGE. From the
results depicted in Fig. 5, it is evident that all three variants are
inferior to our proposed model. Notably, AEKE_KGE performs
particularly poorly, even when compared to straightforward

Fig. 6. Margin parameter and trade-off parameters analysis on the three
datasets.

baseline methods. This discrepancy arises due to the fact that
the negative sampling employed in the KG embedding framework primarily assists our model in learning rich structural
and semantic information within triples. However, such local
features alone are insufficient to enable effective error detection
across the entire KG. Contrastive learning, on the other hand,
complements the negative samples by facilitating the learning
of distinguishable across-view representations. With the distinguishable across-view representations, denoising noisy triples
on KGs will be much more effective.
E. Parameter Analysis (Q4)
In this section, we investigate the impact of three key parameters in AEKE and report the results in Fig. 6(a) and (b).
1) Trade-Off Parameters in Confidence Score Function: As
shown in (18), λ1 and λ2 are trade-off coefficients that balance
the contribution of three learning signals for error detection,
i.e., the self-contradictory within the triple embedding, global
alignment among triples, and the conformity between attributes
and the graph structure. The larger λ1 and λ2 indicate that
effective error detection relies more on the signals of global
acknowledgement and cross-view conformity, respectively. To
search for suitable trade-off parameters, we vary them from

ZHANG et al.: INTEGRATING ENTITY ATTRIBUTES FOR ERROR-AWARE KNOWLEDGE GRAPH EMBEDDING

1679

TABLE V
COMPLEXITY ANALYSIS (SPACE COMPLEXITY, TIME COMPLEXITY, THE
OVERALL TRAINING TIME Ttotal AND THE AVERAGE TRAINING TIME IN EACH
EPOCH Tepoch )

10−3 to 103 . We perform completion on FB15K-237 and the
performance in terms of MRR is shown in Fig. 6(b). From
the results, we observe that the completion performance is
much better when the value of λ1 and λ2 is larger than 1,
with an optimal result at λ1 = 10 and λ2 = 100. We omit
the results on the other two datasets since they show similar
trends.
2) Margin Parameter: The translation-based KG embedding
loss function utilizes γ as a margin to regulate the distance
between the representations of positive and negative pairs, as
indicated in (1). In order to examine the influence of γ, we
vary its value from 0 to 1.0 and present the results in Fig. 6(a).
The DB15 K dataset achieves optimal outcomes when λ1 is
approximately 0.1. From a global perspective, the variations in
the parameter λ do not appear to have a significant impact, as
its value remains stable within a specific range, as observed in
YAGO15 K. However, for FB15K-237, the performance notably
improves when λ is set below 0.5, with the best result obtained at
0.2. The overall performance changes exhibit a stable trend with
minimal fluctuation as γ varies. This is primarily attributed to
the joint training approach employed, which prevents the model
from becoming suboptimal.

Fig. 7. Case study on FB15K-237. (a) presents a 2-hop subgraph extracted
from FB15K-237 centering at the target entity /m/0f b1q. While (b) demonstrates the corresponding subgraph with attribute information attached to each
entity.

TABLE VI
CONFIDENCE SCORE OF EACH TRIPLE IN THE SUGRAPH

models. 3) Although both our proposed AEKE and CrossVal use
extra data sources for KG modeling, our proposed AEKE shows
better efficiency than CrossVal. It is because entity attributes
used in AEKE are naturally attached to entities, which can be
directly leveraged for KG learning, while CrossVal need extra
time to align the knowledge from the original KG and external
KG since a entity may have different IDs or names in different
KGs.

F. Complexity Analysis (Q5)
In this section, we conduct a comprehensive complexity
analysis to investigate the efficiency of our proposed AEKE.
N _e, N _r and N _t denote the number of entities, relations
and triples, respectively. m, n and t are the dimensions of
entity, relation and triple embeddings. N _k is the number of
entities in external KG used in CrassVal, and d is the dimension
of entity embedding in external KG. N _a is the number of
attributes in AEKE. As shown in Table V, we have the following
observations: 1) Embedding-based methods including TransE,
SimplE, and EARL are time and space efficient and run faster
than error detection and error-aware methods in general since
they only need to calculate the mean square losses. In the same
time, EARL costs more time than TransE and SimplE since it
introduces multi-layer convolution network in knowledge graph
embedding. 2) In terms of computation time per epoch, NoiGAN
and CAGED outperform AEKE and CrossVal. This is attributed
to NoiGAN and CAGED leveraging fewer data sources for KG
modeling. Nonetheless, the overall training time of NoiGAN
is considerably larger than CAGED due to the challenges in
convergence that are commonly encountered with GAN-based

G. Case Study on Interpretability (Q6)
We conduct a case study to investigate how AEKE can perform error-aware learning in real-world scenarios. We select the
entity /m/0f b1q as the target entity and visualize its 2-hop
subgraph and the corresponding attribute information in Fig. 7.
There are nine triples in the subgraph, five of which are normal
ones and the other four are erroneous (in red). To verify the
ability of AEKE in distinguishing noisy triples, we show the
confidence score of each triple in Table VI. To make the effect
measurable and comparable, apart from the ground truth labels,
we also include the confidence score that are learned from
the SOTA error-aware embedding method, i.e., NoiGAN, as
counterparts.
Based on the results shown in Table VI, we have the
following observations: (i) compared to NoiGAN, our proposed AEKE shows its superiority in distinguishing erroneous triples. To be clear, NoiGAN learn a confidence set of
{0.6836, 0.2673, 0.7864, 0.6781} for the four real-world errors, which means three erroneous triples have escaped the
detection with the help of the conflicting and complicated

1680

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 4, APRIL 2024

structure. Our method, in contrast, assigns a confidence set
of {0.1684, 0.1086, 0.4309, 0.1146} to four triples, which indicates that it accurately identifies three errors, i.e., only one
erroneous triple is oddly assigned a slightly higher score of
0.4309. (ii) When measuring the correctness of normal triples,
AEKE shows better stability and robustness than NoiGAN in
most cases. Specifically, the normal triples get a confidence
set of {0.8921, 0.8427, 0.9254, 0.8710, 0.8549} using AEKE,
which are generally closer to 1 (the ground truth value), compared with the confidence set {0.7553, 0.7017, 0.8257, 0.7682,
0.7944} learned from NoiGAN. Interestingly, the triple with
more erroneous neighbors tends to have a lower confidence
score in NoiGAN, while this phenomenon is not that obvious in
our proposed AEKE. It is mainly because AEKE measures the
triple confidence by considering three different anomaly signals,
i.e, self-contradictory within relational triple structure, global
consistency across triples, and attribute-structure dependency,
while NoiGAN only relies on pure graph structure to estimate
triple confidence, which makes it more vulnerable to neighboring erroneous instances.
V. RELATED WORK
A. Knowledge Graph Embedding
A lot of efforts have been laid on the KG embedding to learn
the representation of triples within KGs after establishment,
contributing an essential base for downstream tasks [47], [48],
[49], [50], [51]. Translational distance models represented by
TransE [39] seize greater attention than before, more applications prove its reliability for embedding based on the design
to embed entities and relations into a continuous vector space
as the projection of the original triples. As to three methods
which sharing roots with each other, Rescal [46] represents the
bi-relational data into three-dimensional tensors, in the form of
an entity matrix and a relation matrix. DistMult [40] simplifies
Rescal with a bi-linear formulation, taking entities as low dimensional vectors and relations from a bi-linear mapping function.However, this kind of simplification brings the restriction
of a symmetry problem, ComplEx [41] improved DistMult and
fixed the problem by introducing complex value which enables
the model to handle both symmetric and asymmetric problems.
KG Embedding Methods With External Information: While
the traditional ones are showing their advantages, more and more
researches start to focus on attaching importance to external
information of the original KG aiming to support better embedding methods. DKRL [52] introduces entitiy description into the
KG embedding for better semantic understanding. It trains the
energy function with mutual promotion of structural embedding
and description embedding. KDCoE [53], similarly, also takes
the advantage of abundant semantics as a semi-supervised algorithm, which embeds multilingual entity descriptions through a
co-learning method for knowledge alignment across languages.
B. Knowledge Graph Error Detection
Error detection, being one of the most challenging problems,
has been the subject of extensive research for many years. Initially, studies on error detection primarily focused on traditional

methods such as rule-based approaches [54], classificationbased methods [16], clustering-based methods [55], [56],
distance-based methods [57], distribution-based methods [58],
and others [59], [60]. Among these approaches, several notable
methods have been developed specifically for error detection in
knowledge graphs (KGs). One such method is KGClean [61], a
classification-based framework that employs a novel approach
called AL-detect to determine the truthfulness of triples and
subsequently detect and repair erroneous data. Another method,
SDValidate [58], utilizes statistical distributions to identify error
relations in noisy KGs, without relying on any external knowledge. Inspired by SDValidate and PRA [62], PaTyBRED [16]
incorporates type and path features into local relation classifiers
to detect relation assertion errors in KGs. However, in many
cases, it is challenging to acquire a sufficiently labeled dataset
with explicit error labels, which limits the broader application
of unsupervised learning methods in error detection tasks.
The advancement of graph embedding techniques, such as
TransE [39], KBGAN [63], ConvE [64], and DistMult [34], has
led to a significant focus on embedding-based error detection
methods. Numerous models have been developed, demonstrating the effectiveness of embedding approaches on benchmark
datasets. One notable model is TransT [65], which is a translating embedding model based on TransE [39] and incorporates
triple trustworthiness to handle noisy knowledge graphs. TransT
introduces two sub-models that consider entity types and entity
descriptions, respectively, in order to calculate triple trustworthiness values. In the Correction Tower framework proposed by
Abedini et al. [17], three distinct embedding-based solutions are
introduced to address different types of errors, including outliers,
inconsistent triples, and erroneous relations. These solutions are
then combined to form a filter-like structure that detects and
corrects errors within the knowledge graph.
C. Error-Aware Knowledge Graph Embedding
Different from KG error detection that aims to get the anomaly
labels of each triple, error-aware KG embedding is an end-to-end
KG representation learning framework that encodes entities and
relations into low-dimensional vector space with the consideration of erroneous triples during the learning phase. Vault [22]
is the first work that aims to detect possible errors in KGs while
learning knowledge representations. It estimates a probability
score of reliability to determine the quality of a triple via several
prior models fitted with existing KGs. A similar concept of
judgments for each triple is also applied in CKRL [23] and
NoiGAN [24]. The former model generates confidence scores
for triples via internal structure information and utilizes them in
representation learning to produce robust representations, while
the latter improves it in the aspect of sample selection.
VI. CONCLUSIONS AND FUTURE WORK
Learning effective and robust embeddings of entities and
relations in KGs can facilitate various downstream applications.
Most existing efforts take advantage of the internal structure
within KGs to help train a discriminative detector. But, they
are confronted with the bottleneck that the internal topological
information implied in pure KGs is far from abundant to support

ZHANG et al.: INTEGRATING ENTITY ATTRIBUTES FOR ERROR-AWARE KNOWLEDGE GRAPH EMBEDDING

the validation task in real-world scenarios. In this article, we
propose a novel KG representation learning framework, i.e.,
AEKE, to incorporate the semantic information contained in
entity attributes to automatically validate triples in KGs. We
treat the original KG without attributes information as relational
hypergraph, and build an attribute hypergraph based on these
side-information and treat it as a congruent view of target KG.
The confidence score of each triple is calculated by considering:
self-contradictory within the triple; local-global consistency in
graph structure; and structure-attribute homogeneity between
triple-level views. Experiment results demonstrate that AEKE
outperforms state-of-the-art KG error detection algorithms.
Since real-world KGs are always evolving and introducing new
knowledge, extending our method to temporal KG representation learning will be a very valuable and promising future
work. Besides, in the future, we will also explore using the
error-aware knowledge graph representation learning method in
AEKE for downstream applications such as question answering
and recommender systems.
REFERENCES
[1] Q. Wang, Z. Mao, B. Wang, and L. Guo, “Knowledge graph embedding:
A survey of approaches and applications,” IEEE Trans. Knowl. Data Eng.,
vol. 29, no. 12, pp. 2724–2743, Dec. 2017.
[2] F. Mahdisoltani, J. Biega, and F. M. Suchanek, “YAGO3: A knowledge
base from multilingual Wikipedias,” in Proc. Conf. Innov. Data Syst. Res.,
2015.
[3] J. Lehmann et al., “DBpedia – A large-scale, multilingual knowledge base
extracted from Wikipedia,” Semantic Web J., vol. 6, no. 2, pp. 167–195,
2015.
[4] P. Ernst, A. Siu, and G. Weikum, “KnowLife: A versatile approach for
constructing a large knowledge graph for biomedical sciences,” BMC
Bioinf., vol. 16, May 2015, Art. no. 157.
[5] Y. Chen, J. Kuang, D. Cheng, J. Zheng, M. Gao, and A. Zhou, “AgriKG:
An agricultural knowledge graph and its applications,” in Proc. Int. Conf.
Database Syst. Adv. Appl., Springer, 2019, pp. 533–537.
[6] H. Wang, M. Zhao, X. Xie, W. Li, and M. Guo, “Knowledge graph
convolutional networks for recommender systems,” in Proc. World Wide
Web Conf., 2019, pp. 3307–3313.
[7] X. Huang, J. Zhang, D. Li, and P. Li, “Knowledge graph embedding
based question answering,” in Proc. 12th ACM Int. Conf. Web Search Data
Mining, 2019, pp. 105–113.
[8] S. Guo, Q. Wang, L. Wang, B. Wang, and L. Guo, “Jointly embedding
knowledge graphs and logical rules,” in Proc. Conf. Empirical Methods
Natural Lang. Process., 2016, pp. 192–202.
[9] J. Feng, M. Huang, M. Wang, M. Zhou, Y. Hao, and X. Zhu, “Knowledge
graph embedding by flexible translation,” in Proc. 15th Int. Conf. Princ.
Knowl. Representation Reasoning, 2016, pp. 557–560.
[10] S. Guo, Q. Wang, L. Wang, B. Wang, and L. Guo, “Knowledge graph
embedding with iterative guidance from soft rules,” in Proc. AAAI Conf.
Artif. Intell., 2018, pp. 4816–4823.
[11] K. Bollacker, R. Cook, and P. Tufts, “Freebase: A shared database of
structured general human knowledge,” in Proc. AAAI Conf. Artif. Intell.,
2007, pp. 1962–1963.
[12] S. Heindorf, M. Potthast, B. Stein, and G. Engels, “Vandalism detection
in Wikidata,” in Proc. 25th ACM Int. Conf. Inf. Knowl. Manage., 2016,
pp. 327–336.
[13] R. Fasoulis, K. Bougiatiotis, F. Aisopos, A. Nentidis, and G. Paliouras,
“Error detection in knowledge graphs: Path ranking, embeddings or both,”
2020, arXiv:2002.08762.
[14] T. Mitchell et al., “Never-ending learning,” Commun. ACM, vol. 61, no. 5,
pp. 103–115, 2018.
[15] S. Jia, Y. Xiang, X. Chen, and K. Wang, “Triple trustworthiness measurement for knowledge graph,” in Proc. World Wide Web Conf., 2019,
pp. 2865–2871.
[16] A. Melo and H. Paulheim, “Detection of relation assertion errors in
knowledge graphs,” in Proc. Knowl. Capture Conf., 2017, pp. 1–8.

1681

[17] F. Abedini, M. R. Keyvanpour, and M. B. Menhaj, “Correction tower:
A general embedding method of the error recognition for the knowledge
graph correction,” Int. J. Pattern Recognit. Artif. Intell., vol. 34, no. 10,
2020, Art. no. 2059034.
[18] Z. Zhang et al., “Towards robust knowledge graph embedding via multitask reinforcement learning,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 4,
pp. 4321–4334, Apr. 2023.
[19] Y. Shan, C. Bu, X. Liu, S. Ji, and L. Li, “Confidence-aware negative
sampling method for noisy knowledge graph embedding,” in Proc. IEEE
Int. Conf. Big Knowl., 2018, pp. 33–40.
[20] J. Pujara, E. Augustine, and L. Getoor, “Sparsity and noise: Where knowledge graph embeddings fall short,” in Proc. Conf. Empirical Methods
Natural Lang. Process., 2017, pp. 1751–1756.
[21] M. Nayyeri, S. Vahdati, E. Sallinger, M. M. Alam, H. S. Yazdi, and J.
Lehmann, “Pattern-aware and noise-resilient embedding models,” in Proc.
Eur. Conf. Inf. Retrieval, Springer, 2021, pp. 483–496.
[22] X. Dong et al., “Knowledge vault: A web-scale approach to probabilistic
knowledge fusion,” in Proc. 20th ACM SIGKDD Int. Conf. Knowl. Discov.
Data Mining, 2014, pp. 601–610.
[23] R. Xie, Z. Liu, F. Lin, and L. Lin, “Does William Shakespeare REALLY
write Hamlet? Knowledge representation learning with confidence,” in
Proc. AAAI Conf. Artif. Intell., 2018, pp. 4954–4961.
[24] K. Cheng, Y. Zhu, M. Zhang, and Y. Sun, “NoiGAN: Noise aware knowledge graph embedding with GAN,” 2019.
[25] Y. Wang, F. Ma, and J. Gao, “Efficient knowledge graph validation via
cross-graph representation learning,” in Proc. 29th ACM Int. Conf. Inf.
Knowl. Manage., 2020, pp. 1595–1604.
[26] J. Lehmann, D. Gerber, M. Morsey, and A.-C. Ngonga Ngomo, “DeFactodeep fact validation,” in Proc. Int. Semantic Web Conf., Springer, 2012,
pp. 312–327.
[27] M. N. Jeyaraj, S. Perera, M. Jayasinghe, and N. Jihan, “Probabilistic error
detection model for knowledge graph refinement,” in Proc. Int. Conf.
Comput. Linguistics Intell. Text Process., vol. 26, no. 3, pp. 1243–1257,
2019.
[28] M. Li, N. Gao, C. Tu, J. Peng, and M. Li, “Incorporating attributes
semantics into knowledge graph embeddings,” in Proc. IEEE 24th Int.
Conf. Comput. Supported Cooperative Work Des., 2021, pp. 620–625.
[29] Z. Liu, Y. Cao, L. Pan, J. Li, and T.-S. Chua, “Exploring and
evaluating attributes, values, and structures for entity alignment,”
2020, arXiv:2010.03249.
[30] B. D. Trisedya, J. Qi, and R. Zhang, “Entity alignment between knowledge
graphs using attribute embeddings,” in Proc. AAAI Conf. Artif. Intell., 2019,
pp. 297–304.
[31] Y. Lin, Z. Liu, and M. Sun, “Knowledge representation learning with
entities, attributes and relations,” Ethnicity, vol. 1, pp. 41–52, 2016.
[32] Q. Zhang, J. Dong, K. Duan, X. Huang, Y. Liu, and L. Xu, “Contrastive
knowledge graph error detection,” in Proc. 31st ACM Int. Conf. Inf. Knowl.
Manage., 2022, pp. 2590–2599.
[33] S. Wang, X. Huang, C. Chen, L. Wu, and J. Li, “REFORM: Error-aware
few-shot knowledge graph completion,” in Proc. 30th ACM Int. Conf. Inf.
Knowl. Manage., 2021, pp. 1979–1988.
[34] T. Trouillon, C. R. Dance, J. Welbl, S. Riedel, É. Gaussier, and G.
Bouchard, “Knowledge graph completion via complex tensor factorization,” 2017, arXiv:1702.06879.
[35] J. C. Turner and P. J. Oakes, “The significance of the social identity concept
for social psychology with reference to individualism, interactionism and
social influence,” Brit. J. Social Psychol., vol. 25, pp. 237–252, 1986.
[36] K. Toutanova, D. Chen, P. Pantel, H. Poon, P. Choudhury, and M. Gamon,
“Representing text for joint embedding of text and knowledge bases,” in
Proc. Conf. Empirical Methods Natural Lang. Process., 2015, pp. 1499–
1509.
[37] Y. Liu, H. Li, A. Garcia-Duran, M. Niepert, D. Onoro-Rubio, and D. S.
Rosenblum, “MMKG: Multi-modal knowledge graphs,” in Proc. 16th Int.
Conf. Semantic Web, Springer, 2019, pp. 459–474.
[38] F. Mahdisoltani, J. Biega, and F. Suchanek, “YAGO3: A knowledge base
from multilingual Wikipedias,” in Proc. 7th Biennial Conf. Innov. Data
Syst. Res., 2014.
[39] A. Bordes, N. Usunier, A. Garcia-Duran, J. Weston, and O. Yakhnenko,
“Translating embeddings for modeling multi-relational data,” in Proc. Int.
Conf. Neural Inf. Process. Syst., 2013, pp. 2787–2795.
[40] B. Yang, W. T. Yih, X. He, J. Gao, and L. Deng, “Embedding entities and
relations for learning and inference in knowledge bases,” 2015.
[41] T. Trouillon, J. Welbl, S. Riedel, É. Gaussier, and G. Bouchard, “Complex
embeddings for simple link prediction,” in Proc. Int. Conf. Mach. Learn.,
2016, pp. 2071–2080.

1682

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 4, APRIL 2024

[42] S. M. Kazemi and D. Poole, “Simple embedding for link prediction in
knowledge graphs,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2018,
pp. 4289–4300.
[43] I. Balažević, C. Allen, and T. M. Hospedales, “TuckER: Tensor factorization for knowledge graph completion,” 2019, arXiv:1901.09590.
[44] M. Chen et al., “Entity-agnostic representation learning for parameterefficient knowledge graph embedding,” 2023, arXiv:2302.01849.
[45] M. Schlichtkrull, T. N. Kipf, P. Bloem, R. V. D. Berg, I. Titov, and M.
Welling, “Modeling relational data with graph convolutional networks,”
in Proc. Eur. Semantic Web Conf., Springer, 2018, pp. 593–607.
[46] D. Nathani, J. Chauhan, C. Sharma, and M. Kaul, “Learning attentionbased embeddings for relation prediction in knowledge graphs,”
2019, arXiv:1906.01195.
[47] J. Ashish, B. A. Ramesh, Z. M. Zaki, B. Debapriya, and M. Fillia, “A survey
on contrastive self-supervised learning,” Technologies, vol. 9, no. 2, 2021,
Art. no. 2.
[48] R. Hadsell, S. Chopra, and Y. LeCun, “Dimensionality reduction by
learning an invariant mapping,” in Proc. IEEE Comput. Soc. Conf. Comput.
Vis. Pattern Recognit., 2006, pp. 1735–1742.
[49] O. Henaff, “Data-efficient image recognition with contrastive predictive
coding,” in Proc. Int. Conf. Mach. Learn., 2020, pp. 4182–4192.
[50] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum contrast for
unsupervised visual representation learning,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2020, pp. 9729–9738.
[51] S. Monka, L. Halilaj, S. Schmid, and A. Rettinger, “ConTraKG:
Contrastive-based transfer learning for visual object recognition using
knowledge graphs,” CoRR, 2021.
[52] R. Xie, Z. Liu, J. Jia, H. Luan, and M. Sun, “Representation learning of
knowledge graphs with entity descriptions,” in Proc. AAAI Conf. Artif.
Intell., 2016, pp. 2659–2665.
[53] M. Chen, Y. Tian, K.-W. Chang, S. Skiena, and C. Zaniolo, “Co-training
embeddings of knowledge graphs and entity descriptions for cross-lingual
entity alignment,” 2018, arXiv:1806.06478.
[54] Y. Ma, H. Gao, T. Wu, and G. Qi, “Learning disjointness axioms with
association rule mining and its application to inconsistency detection of
linked data,” in Proc. Chin. Semantic Web Web Sci. Conf., Springer, 2014,
pp. 29–41.
[55] H. Paulheim and A. Gangemi, “Serving DBpedia with DOLCE–More than
just adding a cherry on top,” in Proc. Int. Semantic Web Conf., Springer,
2015, pp. 180–196.
[56] X. Wang, X. L. Wang, and D. M. Wilkes, “A minimum spanning treeinspired clustering-based outlier detection technique,” in Proc. Ind. Conf.
Data Mining, Springer, 2012, pp. 209–223.
[57] J. Debattista, C. Lange, and S. Auer, “A preliminary investigation towards
improving linked data quality using distance-based outlier detection,” in
Proc. Joint Int. Semantic Technol. Conf., Springer, 2016, pp. 116–124.
[58] H. Paulheim and C. Bizer, “Improving the quality of linked data using
statistical distributions,” Int. J. Semantic Web Inf. Syst., vol. 10, no. 2,
pp. 63–86, 2014.
[59] J. Lehmann, D. Gerber, M. Morsey, and A.-C. N. Ngomo, “Defacto-deep
fact validation,” in Proc. Int. Semantic Web Conf., Springer, 2012, pp. 312–
327.
[60] B. Shi and T. Weninger, “Discriminative predicate path mining for fact
checking in knowledge graphs,” Knowl.-Based Syst., vol. 104, pp. 123–
133, 2016.
[61] C. Ge, Y. Gao, H. Weng, C. Zhang, X. Miao, and B. Zheng, “KGClean: An embedding powered knowledge graph cleaning framework,”
2020, arXiv:2004.14478.
[62] N. Lao and W. W. Cohen, “Relational retrieval using a combination of
path-constrained random walks,” Mach. Learn., vol. 81, no. 1, pp. 53–67,
2010.
[63] Z. Wang, J. Zhang, J. Feng, and Z. Chen, “Knowledge graph embedding
by translating on hyperplanes,” in Proc. AAAI Conf. Artif. Intell., 2014,
pp. 1112–1119.
[64] Y. Lin, Z. Liu, M. Sun, Y. Liu, and X. Zhu, “Learning entity and relation
embeddings for knowledge graph completion,” in Proc. 29th AAAI Conf.
Artif. Intell., 2015, pp. 2181–2187.
[65] Y. Zhao, H. Feng, and P. Gallinari, “Embedding learning with triple
trustiness on noisy knowledge graph,” Entropy, vol. 21, no. 11, 2019,
Art. no. 1083.

Qinggang Zhang received the bachelor’s degree of
engineering in computer science from the Northwestern Polytechnical University, China. He is currently
working toward the PhD degree with the Department
of Computing, Hong Kong Polytechnic University,
Hong Kong SAR. He is currently a group member
in DEEP Lab supervised by Dr. Xiao Huang with
the Hong Kong Polytechnic University. His research
interests include graph neural networks, knowledge
graphs, and network anomaly detection.

Junnan Dong received the MS degree from the Hong
Kong Polytechnic University, supervised by Dr. Xiao
Huang. He is currently working toward the PhD
degree with DEEP Lab, Department of Computing,
Hong Kong Polytechnic University. His research interests mainly include graph neural networks and
knowledge-enhanced reasoning. He has published
papers on WSDM and WWW related to learning with
knowledge graphs.

Qiaoyu Tan received the BEng degree from the College of Computer Science and Technology, Southwest
University, China, in 2017. He is currently working
toward the PhD degree with the Department of Computer Science and Engineering, Texas A&M University, College Station, Texas. His research interests include graph neural networks, knowledge graphs, network anomaly detection, and recommendation systems. He has published more than 20 peer-reviewed
research papers and serves as a reviewer and PC
member for several premier conferences and journals.

Xiao Huang received the BS degree in engineering
from Shanghai Jiao Tong University, in 2012, the MS
degree in electrical engineering from the Illinois Institute of Technology, in 2015, and the PhD degree in
computer engineering from Texas A&M University,
in 2020. He is an assistant professor with the Department of Computing, Hong Kong Polytechnic University. He is a program committee member of AAAI
2021–2023, ICLR 2022–2023, NeurIPS 2021–2022,
KDD 2019–2022, TheWebConf 2022–2023, ICML
2021–2022, IJCAI 2020–2022, CIKM 2019–2022,
WSDM 2021–2023, SDM 2022, ICKG 2020–2021.
PAPER_TEXT
