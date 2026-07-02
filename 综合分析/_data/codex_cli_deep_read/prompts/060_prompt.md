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
# [060] Knowledge graph based methods for record linkage
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
编号：060
题名：Knowledge graph based methods for record linkage
年份：2020
DOI：10.1016/j.patrec.2020.05.025
来源：Pattern Recognition Letters
PDF：paper/10.1016_j.patrec.2020.05.025.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：无
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\060.txt
- 原始字符数：38323
- 本次发送字符数：38323
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Pattern Recognition Letters 136 (2020) 1–7

Contents lists available at ScienceDirect

Pattern Recognition Letters
journal homepage: www.elsevier.com/locate/patrec

Knowledge graph based methods for record linkage
Bhaskar Gautam a, Oriol Ramos Terrades a,∗, Joana Maria Pujadas-Mora b, Miquel Valls b
a
b

Computer Vision Center - Universitat Autònoma de Barcelona, Ediﬁci O Campus UAB, Bellaterra 08193, Spain
Center for Demographic Studies - Universitat Autònoma de Barcelona, Ediﬁci E2 Campus UAB, Bellaterra 08193, Spain

a r t i c l e

i n f o

Article history:
Received 16 July 2019
Revised 23 April 2020
Accepted 7 May 2020
Available online 24 May 2020
Keywords:
Record linkage
Entity alignment
Author disambiguation
Knowledge graph embedding
Historical census data

a b s t r a c t
Nowadays, it is common in Historical Demography the use of individual-level data as a consequence of
a predominant life-course approach for the understanding of the demographic behaviour, family transition, mobility, etc. Advanced record linkage is key since it allows increasing the data complexity and its
volume to be analyzed. However, current methods are constrained to link data from the same kind of
sources. Knowledge graph are ﬂexible semantic representations, which allow to encode data variability
and semantic relations in a structured manner.
In this paper we propose the use of knowledge graph methods to tackle record linkage tasks. The proposed method, named WERL, takes advantage of the main knowledge graph properties and learns embedding vectors to encode census information. These embeddings are properly weighted to maximize
the record linkage performance. We have evaluated this method on benchmark data sets and we have
compared it to related methods with stimulating and satisfactory results.
© 2020 Elsevier B.V. All rights reserved.

1. Introduction
Nowadays, it is common in historical demography the use
of individual-level data as a consequence of a predominant lifecourse approach for the understanding of the demographic behaviour, family transition, mobility, etc. The building of individual
life-courses often involves the link of the birth certiﬁcate (baptism), the death certiﬁcate of the same individual and, for those
who got married, their marriage certiﬁcate. These certiﬁcates were
compiled nominally and manually in the so called Quinque Libri
(parish registers) from the Council of Trento in the 16th century
onwards throughout Europe [33]. Moreover, and as a consequence
of the establishment of the Liberal State in Europe, civil registers
and censuses spread out from the 19th century, although in some
countries spread out even before [8,9,31]. Consequently, individual
life-courses can also be enriched by sequential observations of the
same individual over time and space using census material. Indeed,
record linkage is the task of ﬁnding records in a data set that refer to the same entity across different data sources in which individuals do not have a unique identiﬁer [26]. In addition, other
studies in the discipline apply an inter-generational perspective to
determine the transmission of demographic behaviour, social outcomes or diseases, which is key in genetic studies and necessarily

∗

Corresponding author.
E-mail address: oriolrt@cvc.uab.cat (O. Ramos Terrades).

https://doi.org/10.1016/j.patrec.2020.05.025
0167-8655/© 2020 Elsevier B.V. All rights reserved.

requires the connection across generations [7], which also implies
the linkage between different generations of a same family.
However, poor data quality can turn record linkage into a challenging task. The conservation status of original documents, the
scanning process, the large number of similar values in names,
ages or addresses are just some of the multiple factors that can
affect data quality. More importantly, the relationship between
household members and their head can signiﬁcantly change between two censuses. For example, people were born and died, got
married, changed occupation, or moved home. These changes on
individual’s records make record linkage in the historical census,
i.e. those collected in the 19th and early 20th century and where
only limited information about individuals were available, even
more challenging. As a result, record linkage methods as those
based on string distances are not reliable enough, and many false
or duplicate matches are often generated. This is also a common
problem in other record linkage applications, such as author disambiguation [5].
Knowledge graphs (KG) allow organizing semantics in a structured manner. They represent a collection of interlinked descriptions of real-world objects, events, situations or abstract concepts,
which are called entities, in a formal structure. Popular KG include
Freebase, DBpedia, YAGO, Satori, etc. and they have millions of entities and billions of entity links. Many researchers have developed
various link prediction methods, also known as entity alignment
(EA) methods, using KG embedding techniques since these large
KG are still incomplete with some missing links [2,15,32].

2

B. Gautam, O. Ramos Terrades and J.M. Pujadas-Mora et al. / Pattern Recognition Letters 136 (2020) 1–7

Therefore, there is the need of record linkage methods able to
deal with heterogeneous data sources. Existing methods are tailored to a particular set of attributes and this makes more diﬃcult
record linkage across heterogeneous sources. Furthermore, these
methods must be able to cope with data variability, due to individual life-course changes and robust to acquisition errors and unveriﬁed transcriptions as well. KGs provide a conceptual framework in
which record linkage prediction and cross-linkage, between different sources, are naturally deﬁned. Indeed, the proposed method,
named WERL, is a step forward in record linkage methods since
it overcomes some of the main diﬃculties discussed earlier. The
main contributions of this paper are:
Evolution knowledge graph. We use KGs for census data and
we enrich them to take into account changes on attribute values of linked records.
• A two step learning process. Thereby, we separately learn attribute embeddings and their weight in record linkage tasks.
This allows higher ﬂexibility on embeddings learning and faster
training.
•

In summary, we propose an EA method able to deal with heterogeneous data and that can be applied to other types of KGs in
which entities are described in terms of attributes.
2. Related work
In this section we brieﬂy review the main methods related to
the record linkage task. First, we summarize the main methods
which are devoted to this task. Then, we review those KG based
methods which are closely related to the proposed method.
2.1. Record linkage methods
The record linkage task has been explored by a number of disciplines, including databases, statistics and artiﬁcial intelligence being key for disciplines like historical demography. Each discipline
has formulated the problem slightly different and consequently
different techniques have been proposed [24].
Early development in computing devices like the Hollerith Tabulator was a result of increasing census data size in the late 17th
century and the lack of resources to tabulate and to analyze this
information [11]. Since then, and mostly from the 19th century onwards, many states gathered population censuses with the purpose
of rationalizing the state population and wealth [20,23,35,36]. State
statistics institutionalisation was a response to the wish of quantiﬁable material within an epistemological development framework
of scientiﬁc objectiveness and an impersonal knowledge of issues
and phenomena [20]. It is worth noting how research centers from
different countries have made their historical census data publicly
available (see IPUMS NAPP1 and Mosaic project2 ).
In the database community, this task is also known as deduplication. Deduplication aims at eliminating repeated data or multiple
copies and thus compressing the database. To this end, it has been
proposed various string edit-distance based methods for record
matching like a general-purpose scheme [16] or a knowledgeintensive approach [22]. In statistics, a long line of research has
been conducted in probabilistic record linkage, largely based on
the seminal paper by [6] formulated entity matching as a classiﬁcation problem, where the basic goal is to classify entity pairs
as matching or non-matching. They proposed using unsupervised
methods, based on a feature-based representation of pairs which
are manually designed and are, to some extent, problem-speciﬁc.
1
2

https://www.nappdata.org/napp/.
https://censusmosaic.demog.berkeley.edu/.

Although this can be a major problem when linking data from different sources, these proposals have been, by and large, adopted by
subsequent researchers, often with elaborations of the underlying
statistical model. The Jaro-Winkler distance has been used commonly for record linkage purposes [34,1].
The AI community has focused on applying supervised learning to the record-linkage task for parameter learning of stringedit distance metrics [25] and combining the results of different
distance functions [29]. Unsupervised methods include similaritybased ones [19], probabilistic ones [27], hierarchical graph modelbased ones [24] and self-learning and embedding based entity
alignment [10].
2.2. Knowledge-based representations
The most basic knowledge representation is the entity-relation
(ER) graph, whose nodes are entities and the adjacency matrix
represents the entity relations. The Translations in the embedding
space (TransE) method generates knowledge graph embeddings of
entities and relations, so that two related entities must have close
entity embeddings in the embedding space [2]. A major drawback
of this model is the poor accuracy while modelling one-to-many
and many-to-many relations.
In order to overcome this problem, Wang et al. [32] proposed
the Translating on hyperplanes (TransH) method. In that work, an
entity is ﬁrst projected onto a hyperplane given for each relation. Thus, the method projects the entity according to the relation it is involved in. This allows the method to perform well even
with one-to-many and many-to-many relations. Moreover, Lin et al.
[15] observed that the optimal dimension used to embed entities
and relations could be different since they are completely different
objects. In order to address this issue they proposed the TransR
method, which learns a matrix to project embedded entities into
the relation embedding space. This method performs well with
one-to-many and many-to-many relations since it uses a different
projection matrix for each relation.
RESCAL is a compositional method, which generates relational
embeddings using tensor factorization [18]. Each embedding dimension represents a single entity feature, thus if two entities
have the same feature value, both should have similar values in
the same embedding dimension. Similarly, the Holographic Embedding (HOLE) method combines the expressive power of the tensor
product with the eﬃciency and simplicity of TransE by using the
circular correlation of vectors to represent pairs of entities [17].
In addition, Path-based TransE (PTransE) is an extension of the
TransE method, which considers multi-step relation paths along
with direct links [13]. Finally, the Bootstrapping Entity Alignment
(BootEA) method aims to update entity embedding using bootstrap
process which adds likely alignments to the knowledge graph [28].
In recent times, there have been an abundance of temporal knowledge graphs which have a timestamp attached to each triplet. Such
graphs are useful to represent dynamic data where order of events
matter[30]. attempted to predict future events by evolving entity
embedding with time[12]. presented Event-Evolutionary principles
for recognising order of various events.
The KR-EAR method relies on a entity-attribute-relation (EAR)
knowledge representation [14]. In that work, the authors identiﬁed
two kinds of elements in their knowledge graph: entities, which
are related between them by means of relations, and attributes,
which are a sort of entity features. Consequently, they deﬁned the
EA task as a product of two posterior probabilities. One modeling entities and relations and the other modeling attributes and
entities. Moreover, self-learning and active learning techniques are
used for embedding learning when not enough annotated data is
available. The Self-Learning and Embedding based entity alignment
(SEEA) method is an extension of the KR-EAR method [10]. There,

B. Gautam, O. Ramos Terrades and J.M. Pujadas-Mora et al. / Pattern Recognition Letters 136 (2020) 1–7

3

Fig. 1. WERL overview. Document image analysis techniques and information extraction methods are ﬁrst applied. Then, a KG representation with evolution triples is built.
Learning is a two step process: ﬁrst, attribute and attribute values are learned. Second, consist of attribute weights learning.

the authors applied reinforcement learning techniques to improve
the performance of their method.
3. The WERL method
The Weighted embedding based record linkage (WERL)
method relies on an extension of the EAR graph and its parameters are learned in a two step process. The full training process is
depicted in Fig. 1. First of all, there are the usual document image
analysis processes consisting of layout analysis, text line detection
and text recognition. Then, the extracted text has to be processed,
cleaned, standardized and harmonized before building the KG. All
these processes are by themselves complex enough and far from
being error free therefore the historical data used in this paper has
been checked and validated by social science experts to avoid being conditioned by those transcription errors in our experiments.
The next step is to build the KG. We modiﬁed the EAR representation by adding relations between attribute values, we named it
Evolution knowledge graph (EKG). These relations have been used
to learn attribute embeddings and attribute value embeddings in
a ﬁrst step and no other embeddings have been learned. Finally,
we have learned the attribute weights to be used later during the
record linkage process.
At record linkage time, we have considered pairs of candidate
records, which can be from different census years, as for instance
entities h and t in Fig. 1. For all the attributes in common between
these two records, we have compared their values by using the
same EA method used in training. Then, the values have been aggregated and weighted accordingly to provide a score between 0
and 1 that gives the matching probability.
In what follows, we provide the details of the WERL method.
We start by introducing the notation used to describe all the different steps to be done for training and records linkage prediction.
3.1. Evolution knowledge graph (EKG)
Let G = (E, V, R, A, B ) a KG. E and V are the graph nodes while
R, A and B are the graph edges, see the top left matrix in Fig. 2.
E is the entity set and R the set of edges between entities. Given
two entities h and t, respectively called head and tail, a relational
triple (RT) is the triple: (h, t, r).

Fig. 2. Example of the proposed Evolution KG representation: RT is the set of relational triples: (e1 , h, r2 ), (e1 , e2 , same) and (e2 , t, r1 ). V is the set of attribute values:
{v0 , . . . , v7 }. Triples: (e1 , v3 , ai ), (e1 , v2 , aj ), (e2 , v5 , ai ), (e2 , v4 , aj ) and gray dashed
triples belong to the AT set and ET = { (v2 , v4 , ai ), (v3 , v5 , a j )} the set of evolution
triples. In this representation will be a missing value between h and t (dashed line).
Top left: KG adjacency matrix.

Regarding KG attributes, V is the set of the attribute values
while A, which is called attribute set, is the edge set linking entities
and attribute values. We denote by AT the set of attribute triples:
(h, v, a) and by Va the attribute value subset, which is the domain
of an attribute a. Similarly, Ve is the attribute value set corresponding to entity e. In other words and in the context of census records,
Ve corresponds to the actual contents of a record e. Although the
elements of Ve are functions of entity attributes a: v = v(a ), we
will omit them when it be clear. Moreover, Ae is the attributes set

4

B. Gautam, O. Ramos Terrades and J.M. Pujadas-Mora et al. / Pattern Recognition Letters 136 (2020) 1–7

of e and Ah,t = Ah ∩ At the set of attributes shared by both entities
h and t.
Finally and as being one of our contributions, we add the
dependencies between attribute values in our KG representation.
These dependencies model the possible changes on people records
through time. To illustrate it, let us consider a kid born in 1867. In
ﬁrst records, he will appear as the son of the head of the household and, probably, his civil status, if reported, single. Later, some
years later he would appear as being the head of his own household and probably married. Once he gets married, he would never
became single again but could be widow and married. The rationale of adding these attribute values dependencies is to model
these semantic dependencies.
Given 2 attribute values vi , vj ∈ Va , that are related because they
appear in two linked records, we deﬁne the evolution triple (ET)
by the triple: (vi , vj , a). These triples add arrows between attribute
values into the KG, see Fig. 2 for graphical representation of our
KG.
3.2. Record linkage prediction
As we have explained at the beginning of this section, we perform record linkage by comparing the attribute values of two candidate records. Given two entities, h and t, we take their attribute
value embedding vectors, θ h,a and θ t,a for all attributes a ∈ Ah,t and
we compare them by means of the EA method used to learn them.
Then, we compute the weighted average given by g:

g(h, t; , W ) =



wa S(v, u )EA(v, u, a; )

(1)

set while T − is composed of all the possible linked records that are
not in T + .
The loss function is the hinge loss evaluated on the predicted
record linkage probability given by Eq. (2). This loss is evaluated in
both positive and negative tuples as shown below:

LRL (W ) =



max {0, λRL + P (y = 1|h, t; , W )}

(h,t )∈T +

+



max {0, λRL − P (y = 1|h, t; , W )}

(4)

(h,t )∈T −

4. Experiments
We carried out two experiments in order to evaluate the WERL
method. In order to properly evaluate the contributions of this paper, we slightly modiﬁed the WERL method. We named MERL the
modiﬁed method and it consists of not considering weights when
predicting record linkage.
The ﬁrst experiment consists of comparing the WERL performance with some state of the art EA methods, described in
Section 2.2, over three benchmark data sets detailed in the next
section, namely BALL, Febrl and Cora data sets. The second experiment aims at evaluating WERL, and MERL, robustness to data
changes. To this end, we used a model trained on a census coming from one town, and we applied to census from neighbouring
villages.

a∈Ah,t

where v ∈ Vh and u ∈ Vt , W = (wa )a is a weight vector associated
to attributes a, S(u,v) is set to 0 if v equals u and 1, otherwise, and
 are the embedding vectors learned. To convert the score return
by g to a value to be probability interpreted, we apply the sigmoid
function, σ :

P (y = 1|h, t; , W ) =

1
1 + exp{−g(h, t; , W )}

(2)

3.3. First step: embedding learning
The ﬁrst step consists of learning the embeddings used to predict record links. To learn them, we can use any of the methods
reviewed in Section 2.2 but applied only to the ET set. We do not
need to learn embeddings to RT and AT sets since they are not
used for record linkage.
Consequently, negative sampling must be done for ET sets. To
do so, we generate them as it is done in similar approaches [13,14].
For each attribute value vi ∈ Va , we sample attribute values from
Va \ Evi , where Evi = {v j ∈ Va | (vi , v j , a ) ∈ E T }. We denote by E +
and E − the positive and negative evolution triple samples, respectively.
We use the same loss function for attribute and attribute values embeddings as the original KG-based embedding method. If
we named that loss function LKG , the actual loss function used to
train the embedding is:

LEA () =



LKG (v, u, a; ) +

(v,u,a )∈E +



LKG (v, u, a; )

(3)

(v,u,a )∈E −

3.4. Second step: weight learning
Once we have learned the embeddings, we must learn the attribute weights, which provide the impact of each attribute to
record linkage prediction. Positive and negative RT, named respectively T + and T − , come from the candidate pair set. Similarly to
the ET set, T + is composed of all the linked records in the training

4.1. Data sets
The Baix Llobregat (BALL) Demographic Database provided the
census records for Sant Feliu town of Barcelona collected in 16
different censuses from 1828 to 1940[21]. We note that the population of the town doubled two decades (1920–1940). The data
set contains around 60K records of individuals with 30 attributes.
Available attributes include individual’s full name, year of birth,
civil status, occupation and relationship with the head of the family.
The Freely Extensible Bio-medical Record Linkage (Febrl) is a
synthetic data set about bio-medical records of patients [3]. Each
record provides information like full name, address, postal code
and birth date. It contains 10K records split across two data sets of
5K records each. For each record, there is a duplicate record in the
other data set. We attempt to link these duplicate records across
these two data sets.
Cora data set contains bibliographical information about scientiﬁc papers in XML format [4]. It contains 1879 records of scientiﬁc citations with details like title, author(s), publisher, journal
and date. The citations refer to 191 unique papers. We attempt to
link all citations referring to the same scientiﬁc paper.
We split data into training, validation and test sets. We further
partition each set in two data sets A and B to build candidate pairs
(a, b). For FEBRL and CORA dataset, we split train-test sets randomly,
while for the BALL dataset we create candidate pairs from two consecutive years. Consider CY as the set of records for a census year Y
from the BALL dataset. For training we use two pairs of dataset (A,
B) as (C1889 , C1906 ) and (C1930 , C1936 ). For validation we use (C1906 ,
C1910 ) and (C1936 , C1940 ). For testing we selected (C1910 , C1924 ) and
(C1924 , C1930 ). To reduce the number of candidate pairs in the BALL
data set we ﬁlter those pairs having the same second surname, see
Table 1 for the counts of each of these sets. Then, we built the
corresponding EKG for each of these data sets, see Table 2 for the
complete counts.

B. Gautam, O. Ramos Terrades and J.M. Pujadas-Mora et al. / Pattern Recognition Letters 136 (2020) 1–7

5

Table 1
Data Partition into train, test and validation sets.
Data set

BALL

Febrl

# Train

# Val.

# Test

# Train

# Val.

# Test

# Train

# Val.

# Test

Dataset A
Dataset B
Candidate Pairs
True Pairs

9510
10,629
238,854
6748

9384
10,722
240,954
9049

10,629
10,536
244,696
8412

3000
3000
29,066
1952

1500
1500
7674
995

500
500
959
340

470
470
220,900
7961

314
313
98,282
3601

156
156
24,336
883

Table 2
Training set sizes of Evolution KG.

BALL
FEBRL
Cora

#E

#A

#R

#V

#AT

#RT

#ET

16,883
6000
940

6
5
15

51
1
1

3492
7497
1764

82,500
30,000
7550

13,750
0
0

10,643
1112
26123

4.2. Methods and parameters
We implemented various translation based algorithms for generating knowledge graph embedding. We used tensorﬂow3 library
to generate and optimize embedding for the KG structures deﬁned
above. We referred an open-source collection of graph embedding
methods called OpenKE4 , to implement the following KG embedding based methods for entity alignment:
•
•

TransE and TransH for ER KG
KR-EAR and SEEA for Evolution KG

To properly evaluate the contribution of each of the elements
introduced in the WERL method we have implemented a one more
method called: MERL. For MERL, we explicitly consider weights as
1 i.e. we consider the mean distance instead of weighted distance.
Moreover, we applied these two methods on two KGs: a basic ER
knowledge graph, in which attributes are also considered as being entities, and to the EKG introduced in Section 3.1. Finally, we
applied grid-search on each of the considered methods to ﬁnd the
optimal hyper-parameters, see Section 1 of the Supplementary Material, for fair comparison.
4.3. 1st experiment. record linkage evaluation.
Overall, EA methods fail when they are applied to record linkage tasks while record linkage methods achieve signiﬁcantly better
performance in all data sets in terms of Precision, Recall and Fscore metrics, see Table 3. However, in terms of accuracy it seems
that all methods obtain relatively good results although WERL and
MERL based methods still achieve the best results. It should be
said that these accuracy values can be misleading since we are in a
two highly unbalanced classiﬁcation problem, see Table 3. We note
that the major concern is false positives, since incorrect linking can
have a chain effect and have negative impact on the concerned research. Since the proportion of true pairs is very low (3% census,
7% febrl, 4% cora) compared to candidate pairs, it is hard to avoid
false positives without increasing false negatives.
Regarding the BALL data set, the WERL (EKG) method provides
the best F-Score of 0.93. Among the compared EA methods, TransE
has the highest F-Score of 0.21 only. TransH and KR-EAR have FScores of 0.17 and 0.18. We note that we get better results when
training over evolution triples. Concerning the Febrl data set, the
MERL EKG provides the best F-score of 0.98. Among EA methods, TransH has the highest F-Score of 0.60, while TransE has a FScore of 0.58. Applying self-learning to KR-EAR i.e. using the SEEA
3
4

Cora

Set

https://www.tensorﬂow.org/install.
https://github.com/thunlp/OpenKE.

method improves the performance signiﬁcantly. We note that the
MERL (EKG) method perform better than WERL (EKG). Finally, as
it regards the CORA data set, TransE provides the best F-Score of
0.54. SEEA was able to improve the results slightly from KR-EAR.
Among our proposed methods, WERL (EKG) provides the highest
F-Score of 0.46. We further note that WERL methods do not perform well on sparse dataset.
In summary, WERL (EKG) and MERL (EKG) methods provide satisfactory and stimulating results since with these methods we are
able to learn proper embedding vectors for KGs.

4.4. 2nd experiment. Method robustness.
Additionally, we tested the WERL (EKG) and the MERL (EKG)
methods on one more census dataset from Santa Coloma de Cervello
and Castellvi de Rosanes towns of Barcelona. The dataset have 8631
records with similar attributes as were provided for Sant Feliu
town.
We partition the dataset as Dataset A and B with 4815 and 3816
records. We considered records from census years 1866, 1924, 1936
and 1945 as dataset A. For the a dataset B, we selected the records
from census years 1901, 1930, 1940 and 1950. We apply blocking
indexing on the second surname ﬁeld to yield 83,264 candidate
pairs, out of which only 6407 are true links. The results are provided in Table 4. MERL (EKG) provides the best F-score of 0.66.

4.5. Discussion
Overall, the proposed method achieves satisfactory performance
compared to similar methods in record linkage tasks. If we analyse
results on benchmark data sets, we notice that sparse data, as in
the Cora data set, makes vector embedding learning harder since
evolution triples need paired attributes in candidate records and
thus the low F-score for these methods. For the febrl data set the
most duplicates had surname and lastname swapped. For such errors, WERL suffers from over-ﬁtting and MERL performs better.
Regarding the BALL data set, we notice that the WERL(EKG)
method is able to learn transcription errors, which occurred during the digitisation process. Indeed, this method performs better
when attribute values evolve in particular order than when they
evolve randomly, since it suffers from over-ﬁtting as well.
Moreover in these experiments the WERL (EKG) method generates 1243 false negatives and 96 false positives in the BALL data
set. In what follows, we provide the different rea-sons for their incorrect classiﬁcation:
Full name: Over 90% of false positives have different full names
while over 60% false negatives have the same full names.
Year of Birth: Over 98% false negatives have the same years of
births. All 96 false positives also have the same years of birth. Additionally, we had 45 false positives where year of birth is missing
for both records.
Civil Status: Over 80% false negatives have the same civil status.
We had 38 false positives with the same civil status i.e. about 58%
false positives have different civil status.

6

B. Gautam, O. Ramos Terrades and J.M. Pujadas-Mora et al. / Pattern Recognition Letters 136 (2020) 1–7
Table 3
Record Linkage Results for three data sets, presents Accuracy, Precision, Recall and F-score.
Data set

BALL

Febrl

Acc.

P

R

F-Score

Acc.

P

R

F-Score

Acc.

P

R

F-Score

TransE (ER)
TransH (ER)
KR-EAR (EAR)
SEEA (EAR)
MERL (ER)
WERL (ER)
MERL (EKG)
WERL (EKG)

0.87
0.81
0.79
0.91
0.98
0.99
0.99
0.99

0.19
0.12
0.13
0.07
0.90
0.99
0.76
0.98

0.25
0.26
0.30
0.10
0.68
0.67
0.88
0.89

0.21
0.17
0.18
0.08
0.77
0.80
0.82
0.93

0.95
0.95
0.42
0.91
0.96
0.95
0.99
0.97

0.70
0.72
0.07
0.44
0.79
0.90
0.99
0.99

0.49
0.52
0.65
0.57
0.92
0.71
0.97
0.76

0.58
0.60
0.13
0.49
0.85
0.79
0.98
0.86

0.99
0.95
0.88
0.97
0.91
0.91
0.95
0.97

0.62
0.39
0.20
0.79
0.23
0.23
0.32
0.61

0.48
0.51
0.81
0.21
0.58
0.58
0.39
0.36

0.54
0.44
0.32
0.33
0.33
0.33
0.35
0.46

Table 4
Additional Results for Santa Coloma and Castellvi towns.

WERL (EKG)
MERL (EKG)

Cora

Method

Accuracy

Precision

Recall

F-Score

0.96
0.94

0.87
0.58

0.51
0.77

0.64
0.66

Supplementary material
Supplementary material associated with this article can be
found, in the online version, at doi:10.1016/j.patrec.2020.05.025.
References

Occupation: Over 50% false negatives had the same occupation
across years. We had 24 false positives with the same occupation
i.e. over 70% false positives have different occupations.
Relation: About 65% false negatives have the same relationship
with head. We had 5 false positives with the same relationship i.e.
about 95% false positives have different relationships across years.
To sum up, we note that WERL EKG linked the record pairs having valid evolution of attribute values while rejecting the record
pairs having invalid evolution, even though they had some common attribute values. Next improvements must overcome these
problems.
5. Conclusions and future work
In this paper we have proposed a KG based method for record
linkage tasks, named WERL. We have enriched knowledge representation by introducing evolution relations. These new edges in
the knowledge graph encode valid variations (evolution) on individual data. Thanks to this knowledge representation the WERL
method is able to learn embedding vectors which better encode
census data. Then in the second step, attribute weights are optimized for the record linkage task. This allows us to identify which
attributes are more discriminant for record linkage tasks. Thereby,
we have taken advantage of knowledge graph representation and
the associated entity alignment methods and, at the same time,
we have trained a specialized method for record linkage tasks.
We have evaluated the proposed method on benchmark data
sets and we have compared it to related methods. The achieved
results are satisfactory and stimulating since there is still room
for improvement. The proposed method must be applied to larger
and more heterogeneous census data sets to evaluate both how it
scales when data sizes increase and its robustness to data variability. We are quite conﬁdent that knowledge graph methods will behave better than existing approaches.
Declaration of Competing Interest
None.
Acknowledgments
This work is partially funded by RTI2018-095645-B-C21and
RTI2018-095533-B-100, Generalitat de Catalunya, 2017 SGR 1783
and the Recercaixa project Xarxes. The Titan V used for this research was donated by the NVIDIA Corporation.

[1] M.A. Jaro, Probabilistic linkage of large public health data ﬁles, Stat. Med. 14
(1995) 491–498, doi:10.1002/sim.4780140510.
[2] A. Bordes, N. Usunier, A. Garcia-Duran, J. Weston, O. Yakhnenko, Translating
embeddings for modeling multi-relational data, in: C.J.C. Burges, L. Bottou,
M. Welling, Z. Ghahramani, K.Q. Weinberger (Eds.), Advances in Neural Information Processing Systems 26, 2013, pp. 2787–2795.
[3] P. Christen, Febrl - an open source data cleaning, deduplication and record
linkage system with a graphical user interface, in: KDD, 2008, pp. 1065–1068,
doi:10.1145/1401890.1402020.
[4] U. Draisbach, F. Naumann, DuDe: the duplicate detection toolkit, ACM - VLDB,
2010.
[5] A.K. Elmagarmid, P.G. Ipeirotis, V.S. Verykios, Duplicate record detection: a survey, IEEE Trans. Knowl. Data Eng. 19 (2007) 1–16, doi:10.1109/TKDE.2007.9.
[6] I.P. Fellegi, A.B. Sunter, A theory for record linkage, J. Am. Stat. Assoc. 64 (1969)
1183–1210, doi:10.1080/01621459.1969.10501049.
[7] Z. Fu, P. Christen, J. Zhou, A graph matching method for historical census
household linkage, Advances in Knowledge Discovery and Data Mining., 2014.
xx–xx
[8] M.S. García Pérez, Tratamiento y resolucián de las descripciones deﬁnidas y su
aplicacin en sistemas de extraccin de informacin, Hispania Nova, 2007.
[9] M. García Ruipérez, El empadronamiento municipal en España: evolución legislativa y tipología documental, Documenta & Instrumenta, 2012, pp. 45–86.
[10] S. Guan, X. Jin, Y. Jia, Y. Wang, H. Shen, X. Cheng, Self-learning and embedding
based entity alignment, in: 2017 IEEE International Conference on Big Knowledge (ICBK), 2017, pp. 33–40, doi:10.1109/ICBK.2017.15.
[11] F. Kistermann, Hollerith punched card system development (1905-1913), Annals of the History of Computing, 27 (2005) 56–66, doi:10.1109/MAHC.2005.8.
IEEE
[12] Z. Li, S. Zhao, X. Ding, T. Liu, in: EEG: Knowledge base for event evolutionary
principles and patterns„ 2017, pp. 40–52, doi:10.1007/978- 981- 10- 6805- 8_4.
[13] Y. Lin, Z. Liu, H. Luan, M. Sun, S. Rao, S. Liu, Modeling relation paths for representation learning of knowledge bases, in: Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing, 2015, pp. 705–714,
doi:10.18653/v1/D15-1082.
[14] Y. Lin, Z. Liu, M. Sun, Knowledge representation learning with entities, attributes and relations, in: Proceedings of the Twenty-Fifth International Joint
Conference on Artiﬁcial Intelligence, 2016, pp. 2866–2872.
[15] Y. Lin, Z. Liu, M. Sun, Y. Liu, X. Zhu, Learning entity and relation embeddings
for knowledge graph completion, in: Proceedings of the Twenty-Ninth AAAI
Conference on Artiﬁcial Intelligence, 2015, pp. 2181–2187.
[16] A. Monge, C. Elkan, An eﬃcient domain-independent algorithm for detecting
approximately duplicate database records, 1997, (????).
[17] M. Nickel, L. Rosasco, T. Poggio, Holographic embeddings of knowledge graphs,
in: 30th Conference on Artiﬁcial Intelligence, 2016, pp. 1955–1961.
[18] M. Nickel, V. Tresp, H.P. Kriegel, A three-way model for collective learning on
multi-relational data, in: 28th International Conference on International Conference on Machine Learning, 2011, pp. 809–816.
[19] A. Nikolov, M. d’Aquin, E. Motta, Unsupervised learning of link discovery conﬁguration, in: 9th International Conference on The Semantic Web: Research
and Applications, 2012, pp. 119–133, doi:10.1007/978- 3- 642- 30284- 8_15.
[20] T. Porter, Trust in Numbers. the Pursuit of Objectivity in Science and Public
Life, Princeton University Press, 1995.
[21] J. Pujadas-Mora, A. Fornes, J. Llados, G. Brea-Martínez, M. Valls-Figols, The
Baix Llobregat (BALL) Demographic Database, between Historical Demography and Computer Vision (nineteenth-twentieth centuries), 2019, pp. 29–61.
10.15826/B978-5-7996-2656-3
[22] V. Raman, J. Hellerstein, Potter’s Wheel: an Interactive Data Cleaning System,
VLDB J. 2 (2001) 381–390.
[23] L. Raphael, Ley y orden. dominación mediante la administración en el siglo
XIX, Siglo XXI, 2008.

B. Gautam, O. Ramos Terrades and J.M. Pujadas-Mora et al. / Pattern Recognition Letters 136 (2020) 1–7
[24] P. Ravikumar, W.W. Cohen, A hierarchical graphical model for record linkage,
in: Proceedings of the 20th Conference on Uncertainty in Artiﬁcial Intelligence,
AUAI Press, 2004, pp. 454–461.
[25] E.S. Ristad, P.N. Yianilos, Learning string-edit distance, IEEE Trans. Pattern Anal.
Mach. Intell. 20 (1998) 522–532, doi:10.1109/34.682181.
[26] S. Ruggles, C. Fitch, E. Roberts, Historical Census Record Linkage, Technical Report, 2017-3, University of Minnesota, 2017.
[27] F.
Suchanek,
S.
Abiteboul,
P.
Senellart,
PARIS:
probabilistic
alignment of relations, instances, and schema, CoRR (2011).
1111.7164
[28] Z. Sun, W. Hu, Q. Zhang, Y. Qu, Bootstrapping entity alignment with knowledge
graph embedding, in: 27th International Joint Conference on Artiﬁcial Intelligence, 2018, pp. 4396–4402.
[29] S. Tejada, C.A. Knoblock, S. Minton, Learning object identiﬁcation rules for information integration, Inf. Syst. 26 (2001) 607–633.

7

[30] R. Trivedi, H. Dai, Y. Wang, L. Song, Know-evolve: Deep temporal reasoning for
dynamic knowledge graphs, arXiv:1705.05742 (2017).
[31] J.R. Valero Escandell, La implantación del registro civil en españa (problemas de utilización en estudios demográﬁcos), Historia ContemporÃ!‘nea (1986)
87–99.
[32] Z. Wang, J. Zhang, J. Feng, Z. Chen, Knowledge graph embedding by translating
on hyperplanes, in: AAAI, 2014, pp. 1112–1119.
[33] J.D. Willigan, K.A. Lynch, Sources and Methods of Historical Demography: Studies in Social Discontinuity, Elsevier, 2013.
[34] W. Winkler, The state of record linkage and current research problems, Stat.
Med. 14 (1999).
[35] S. Woolf, Statistics and the modern state, Comp. Stud. Soc. Hist. 31 (1989) 588–
604, doi:10.1017/S001041750 0 016054.
[36] G.U. Yule, M.G. Kendall, An Introduction to the Theory of Statistics, Charles
Griﬃn and Company, 1919.
PAPER_TEXT
