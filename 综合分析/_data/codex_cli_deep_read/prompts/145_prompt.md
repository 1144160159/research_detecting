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
# [145] MMIEA: Multi-modal Interaction Entity Alignment model for knowledge graphs
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
编号：145
题名：MMIEA: Multi-modal Interaction Entity Alignment model for knowledge graphs
年份：2023
DOI：10.1016/j.inffus.2023.101935
来源：Information Fusion
PDF：paper/10.1016_j.inffus.2023.101935.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：无
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\145.txt
- 原始字符数：64676
- 本次发送字符数：64676
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Information Fusion 100 (2023) 101935

Contents lists available at ScienceDirect

Information Fusion
journal homepage: www.elsevier.com/locate/inffus

Full length article

MMIEA: Multi-modal Interaction Entity Alignment model for knowledge
graphs
Bin Zhu a,b , Meng Wu c,d , Yunpeng Hong c,d , Yi Chen a,b , Bo Xie a,b , Fei Liu c,d , Chenyang Bu c,d ,∗,
Weiping Ding e ,∗
a State Key Laboratory of Pulsed Power Laser Technology, College of Electronic Engineering, National University of Defense Technology, Hefei, 230037, China
b Key Laboratory of Infrared and Low Temperature Plasma of Anhui Province, College of Electronic Engineering, National University of Defense

Technology, Hefei, 230037, China
c
Key Laboratory of Knowledge Engineering with Big Data (the Ministry of Education of China), Hefei University of Technology, Hefei, 230009, China
d
School of Computer Science and Information Engineering, Hefei University of Technology, Hefei, 230009, China
e
School of Information Science and Technology, Nantong University, Nantong, 226019, China

ARTICLE

INFO

Keywords:
Multi-modal
Knowledge graph
Entity alignment
Interaction
BERT

ABSTRACT
Fusing data from different sources to improve decision making in smart cities has received increasing attention.
Collected data through sensors usually exist in a multi-modal form, such as values, images, and texts. Thus,
designing models that handle multi-modal data has an important role in this field. Meanwhile, security and
privacy issues cannot be ignored, as the leakage of big data may provide opportunities for criminals. To
solve the above challenges, we focus on research on multi-modal entity alignment for knowledge graphs
and proposed the Multi-Modal Interaction Entity Alignment model (MMIEA). The model is proposed from
the perspective of fusing data from different modalities while maintaining privacy. We determined that the
model is privacy-preserving because it does not need to transmit the raw data of each modality (only the
vector representation is transmitted). Specifically, we introduce and improve the BERT-INT model for the
entity alignment task in multi-modal knowledge graphs. Experimental results on two commonly used multimodal datasets show that our method outperforms 17 algorithms, including nine multi-modal entity alignment
methods.

1. Introduction
The concept of a smart city refers to the collection and analysis
of different types of data through various physical devices connected
to the Internet of Things to optimize the city’s operation and service
efficiency [1]. Based on the integration, analysis, and processing of
sensory data in all aspects of urban management, the development
of smart cities is considered conducive to the promotion of scientific
governance and rational layout of cities, and the convenience of urban
life [2], such as smart transportation [3], smart campus [4], and smart
emergency management [5].
An important aspect of smart city construction is the integration
of data (such as remote sensing data) or knowledge from different
sources to obtain a complete image of the city and to conduct data
analysis and mining on this basis for scientific decision-making. Owing
to the different types of sensors, the collected data usually exists in
a multi-modal form, including images, texts, numbers, etc. Moreover,

even with the same sensor, different data can be generated for the same
area owing to different observation angles or observation times (such
as photos taken by satellites from different angles). Moreover, owing
to the need to consider data privacy and security, sensor data from
different units or companies cannot typically be shared directly, which
causes additional difficulties. Therefore, fusing data or knowledge of
different modalities from various sources, that is, the task of entity
alignment (EA), while ensuring privacy is an important issue in the
construction of smart cities.
EA is an important task in the field of knowledge graphs that
aims to determine whether two objects (called entities) from different
sources point to the same object in the real world. The entity alignment
technique helps integrate data from multiple sources into a complete
knowledge graph to obtain a large image of the city; thus, it is useful
for many downstream tasks [6–10]. A knowledge graph refers to a

∗ Corresponding authors.

E-mail addresses: chenyangbu@hfut.edu.cn (C. Bu), dwp9988@163.com (W. Ding).
https://doi.org/10.1016/j.inffus.2023.101935
Received 15 March 2023; Received in revised form 23 June 2023; Accepted 17 July 2023
Available online 31 July 2023
1566-2535/© 2023 Elsevier B.V. All rights reserved.

Information Fusion 100 (2023) 101935

B. Zhu et al.

Fig. 1. Motivation and contribution of this study.

However, owing to the heterogeneity of knowledge graphs, equivalent entities often do not share similar neighbors. For example, in
knowledge graph 𝐾1, Yun Ma may be associated with Alibaba Corporation and the founder of Alibaba, but in another knowledge graph 𝐾2,
Jack Ma may be associated with Softbank Corporation and the director
of Softbank [14]. Without sharing similar neighbors, it is difficult
for the algorithm to correctly determine that ‘‘Yun Ma’’, the founder
of Alibaba, is the same person as ‘‘Jack Ma’’, the former director
of SoftBank Corp. For this case, where the corresponding neighbors
cannot be found in 𝐾1, if a typical graph convolutional networks
(GCN) based approach is adopted, the method of propagating different
neighbors may introduce noise, thereby affecting the accuracy of the
final alignment.
Inspired by BERT-INT [22], instead of aggregating neighbor nodes,
we adopted the idea of computing the interactions between neighbor
nodes to solve the above problem. Because the BERT-INT model does
not specifically deal with multi-modal information, in this study, we
improve the BERT-INT model by including a method for processing
image modalities and image interactions, enabling it to handle multimodal entity alignment tasks. The contributions of this study are as
follows (see Fig. 1):

semantic network that describes objects (i.e., entities) and their relationships in the real world in the form of graphs [11]. Traditional
knowledge graphs typically use only a single modality (i.e., text) to
describe semantic information, whereas multi-modal knowledge graphs
enrich the types of knowledge by introducing information from other
modalities, such as images, into traditional knowledge graphs [12]. The
construction of multi-modal knowledge graphs has been a hotspot in
knowledge graph-related research in recent years [13].
EA models can be grouped into two categories: similarity-based
methods and embedding-based methods [14–17]. Similarity-based
methods are widely used in early research to judge whether two entities
refer to the same object through textual similarity or propagation
methods. Such methods have high accuracy, but the heterogeneity of
knowledge graphs and complexity of multi-modal data have presented
significant challenges. Embedding-based methods refer to training entities and relations into vector representations (called representation
learning) and measuring the similarity between two entities according
to the distance of the vectors. Embedding-based methods can capture
the implicit structural semantics of the KG well. For example, the
success of TransE [18] in the field of KG, particularly link prediction,
EA, and other segment research fields, led to the development of a large
number of related technologies. However, these methods do not pay
sufficient attention to side information (data from different modalities),
which hinders the accuracy of alignment.
To the best of our knowledge, most current research is on homogeneous data fusion (such as the alignment of different remote sensing
images); only a small number of studies have focused on multi-modal
entity alignment, for example, the fusion of images with other types of
data [19]. Liu et al. [20] constructed a multi-modal knowledge graph
MMKG by extracting or adding modal features, such as images, to the
original datasets, and then proposed a multi-modal entity alignment
framework called PoE. Liyi et al. [21] proposed a method MMEA
to model the entity association of multi-modal KG, which consists
of a multi-modal knowledge representation (MMKE) module and a
multi-modal knowledge fusion (MMKF) module.

• Our work focuses on enhancing the BERT-INT model to address
the entity alignment task in multi-modal knowledge graphs.
• We adopt an interactive approach to capture the image information of neighboring entities, leveraging this information for entity
alignment. Moreover, we explore the impact of different fusion
representations, namely concatenation and gating-based fusion
methods, to achieve improved results in view fusion accuracy.
• Experimental results on two commonly used multi-modal datasets
demonstrates that our method outperforms 17 algorithms, including 9 multi-modal EA methods.
The remainder of this paper is organized as follows. Section 2
summarizes related work. Section 3 reviews the preliminary work. In
Section 4, we explain the proposed MMIEA model. Section 5 presents
2

Information Fusion 100 (2023) 101935

B. Zhu et al.

Fig. 2. Illustration of EA [15]. KG1 and KG2 are two different KGs. The goal of EA is to find all potential entity pairs (connected by ‘‘sameAs’’ relations) that can be aligned.
For example, the entity ‘‘Kongzi’’ in Baidu Baike, the entity ‘‘Confucius’’ in Wikipedia and the entity ‘‘Kong Zhongni’’ in Hudong Baike all represent Confucius, the founder of
Confucianism, in the real world.

the experimental results and analysis. Finally, Section 6 concludes the
study.

network to capture entity relationship correlations, while attribute
correlations are fused through a translation machine. Ge et al. introduce
the EASY framework [35], which jointly fuses features derived from
entity names and graph structural information to enhance EA accuracy.
Zeng et al. [36] propose a collective EA framework based on reinforcement learning, utilizing representative features to capture different
aspects of entity similarity in heterogeneous KGs. Sun et al. [37]
propose a robust and adaptive embedding-based EA method, which
improves the performance of traditional embedding methods.
Similarity-based EA are simple and easy to use, but they are limited
in their ability to handle entities with different structures but the
same semantic meaning. Structure-based EA methods, on the other
hand, can address this issue by considering the structural characteristics
of entities, but they often necessitate domain knowledge and strong
reasoning capabilities. In contrast, attribute-enhanced EA techniques
have gained considerable popularity in recent times due to their ability
to enhance the accuracy of EA through the integration of both structural
and contextual information.

2. Related work
Entity Alignment (EA) is a fundamental technology of KG, aiming
to identify entities located in different KGs that refer to the same realworld object (see Fig. 2) [23–26]. In this section, we introduce the
related work regarding EA for Single-modal and Multi-modal KGs.
2.1. Entity alignment for single-modal KGs
The approaches of EA for Single-modal KGs are introduced including the similarity-based, structure-based, and attribute-enhanced
approaches.
Similarity-based Approaches. In the early years, EA was based
on the idea of similarity: the more similar the text of an entity is,
the more similar the entity is. For example, the editing-distance-based
method uses word similarity, the TFIDF-based method [27] obtains
word frequency similarity, and LDA [28] represents the category of
the text model. Most of these methods are unsupervised and easy to
use, and most are used in non-graph knowledge bases. This traditional
similarity-based approach is becoming increasingly inappropriate as the
structure of KG becomes complex and the amount of data increases.
Structure-based Approaches. In recent years, structure-based EA
models have witnessed significant development, focusing on leveraging
the structural information present in knowledge graphs (KGs). For
instance, TransE [18], has led to the development of a large number
of related technologies in KG research, particularly in the fields of link
prediction and EA. MTransE [29] first learns the embedding representation of entities and relations within a single KG and subsequently
learns a transfer matrix to map aligned entities from different KGs into
a unified space. Similarly, IPTransE [30] initially learns the embedding
of a single KG, and then iteratively refines the embedding through
parameter sharing. Furthermore, in [31] a scalable GNN-based entity
alignment approach is proposed to reduce KG size and alignment loss.
Attribute-enhanced Approaches. In addition to structural information, some studies have focused on improving EA using side information. Attribute-enhanced EA models have gained attention due to their
ability to leverage additional edge information [23]. GCN-Align [32]
is a novel method that combines side information, capturing both the
structure and entity attributes of KG based on GCN encoding. Wu
et al. [33] propose joint learning of entity and relation representations
for EA, specifically considering heterogeneous KGs. BERT-INT [22]
achieves remarkable performance in EA experiments by leveraging
side information such as entity names, descriptions, and attributes
through BERT-based pre-training. It surpasses many embedding models
that solely rely on structural information. Additionally, Tam et al.
propose a cross-lingual EA framework [34], which integrates various
information types to maximize the utilization of cross-lingual KG data.
Their framework employs a multi-order graph convolutional neural

2.2. EA for multi-modal KGs
For multi-modal KGs, researchers have gradually started paying
attention to the design of EA. The design of entity alignment (EA) in
multi-modal knowledge graphs (KGs) has garnered increasing attention
among researchers. A crucial approach to tackle multi-modal EA is
through the utilization of a multi-view paradigm [38].
MMEA [21] focuses on learning knowledge representations of relationships, visual images, and numerical images, followed by fusion of
these representations. Liu et al. [39] proposed a method called Visual
Pivoting, which leverages visual semantic representations for unsupervised EA. HMEA [13] embeds the structure and image of an entity into a
hyperbolic space to reduce the distortion. MultiJAF [40] learns the embedding of structure, attributes, and images in the KG and incorporates
a dedicated module to process numerical values. MCLEA [41] employs
contrastive learning to facilitate the embedding of structure, attributes,
and images in the KG. Li et al. [42] propose the use of embeddingbased prompts for video and language pre-training for task-oriented
dialogue systems. Lu et al. [43] present a robust embedding approach
for multi-modal KG representation learning. Dost et al. [44] introduce
a method for aligning and linking entity mentions in images, text,
and knowledge bases. Ma et al. [45] develop UniTranSeR, a unified
transformer semantic representation framework for multi-modal taskoriented dialogue systems. Additionally, Wang et al. [46] investigate
the influence of visual context in multi-modal EA.
These studies highlight the importance of multi-modal EA as a
critical research direction that carries substantial implications for enhancing EA accuracy and robustness. Overall, research on EA in multimodal KGs is still at an early stage, and different methods exhibit
specific limitations and challenges. Future research directions should
delve deeper into exploring the effective utilization and integration of
information from diverse modalities for EA.
3

Information Fusion 100 (2023) 101935

B. Zhu et al.

Fig. 3. Name/description-view in the BERT-INT model [22], including BERT unit. First, obtain the entities’ vector representation with BERT and MLP. Then, calculate the cosine
similarity as result of this view.

1. For each neighbor of entity 𝑒 or 𝑒′ , apply the BERT unit with
name or description to obtain the collection of vector represen{ ( )}| (𝑒)|
{ ( )}| (𝑒′ )|
tation 𝐶 𝑒𝑖 𝑖=1 and 𝐶 𝑒′𝑖 𝑖=1
.

3. Preliminary
Tang et al. [22] proposed a BERT-based interaction model (BERTINT) for single-modal KG. Before introducing our model, the details of
the three views of BERT-INT are described. BERT-INT is a multiview
model. It calculates the side information from the three views of the
name/description (Section III-A), neighbor (Section III-B), and attribute
(Section III-C), and then obtains the similarity between entities.

2. Based on the collection of vector representation, calculate the
neighboring entity similarity matrix 𝑆, where 𝑠𝑖𝑗 makes up 𝑆.
The calculation of 𝑠𝑖𝑗 is presented in Eq. (2) [22].
( )
( )
𝐶 𝑒𝑖 ⋅ 𝐶 𝑒′𝑗
𝑠𝑖𝑗 =
(2)
( )‖ .
‖ ( )‖ ‖
𝐶 𝑒′𝑗 ‖
‖𝐶 𝑒𝑖 ‖ ⋅ ‖
‖
‖ ‖
‖
‖
‖

3.1. Name/description-view

3. For each relation of neighbors, apply the BERT unit with the
}|𝑁(𝑟′ )|
{
}|𝑁(𝑟)|
{
relation’s name to obtain 𝐶(𝑟𝑖 ) 𝑖=1 and 𝐶(𝑟′𝑖 ) 𝑖=1 .

The name/description view is based on the BERT unit. Entity alignment is the downstream objective for fine-tuning a pretrained BERT
model. For each entity e in the dataset, a pre-trained BERT is applied
to accept its name/description as the input. Then, we filter the classification (CLS) embedding of BERT by a multi-layer perceptron (MLP)
layer to obtain the entities’ vector representation 𝐶 (𝑒). The calculation
of 𝐶 (𝑒) is given by Eq. (1) [22].
𝐶(𝑒) = 𝑀𝐿𝑃 (𝐶𝐿𝑆(𝑒)),

4. Based on Step 3, calculate the neighboring relation mask matrix
𝑀. The calculation of each 𝑚𝑖𝑗 ∈ 𝑀 is presented in Eq. (3) [22].
( )
( )
𝐶 𝑟𝑖 ⋅ 𝐶 𝑟′𝑗
𝑚𝑖𝑗 =
(3)
( )‖ .
‖ ( )‖ ‖
𝐶 𝑟′𝑗 ‖
‖ 𝐶 𝑟𝑖 ‖ ⋅ ‖
‖
‖
‖
‖ ‖
‖
Understand the neighboring relation and neighboring entity as a
pair of key values. For two pairs of key values pairs, if the value
is very similar and the key is very similar, it can significantly
increase the similarity of the two pairs of key values pairs.
5. Multiply 𝑀 to 𝑆, i.e., 𝑆𝑖𝑗 = 𝑆𝑖𝑗 ⊗ 𝑀𝑖𝑗 , where ⊗ indicates
elementwise product.
6. 𝑆 is processed using max-pooling and kernel for each row and
column, respectively, to obtain the corresponding similarity vectors. These row similarity vectors and column similarity vectors
are calculated separately, as shown in Eq. (4) [22].
}
𝑛 {
𝑠max
= max 𝑠𝑖0 , … , 𝑠𝑖𝑗 , … , 𝑠𝑖𝑛 ,
𝑖

(1)

where 𝐶𝐿𝑆(𝑒) returns the CLS embedding of the entity 𝑒. 𝑀𝐿𝑃 (𝑥)
returns the output of an MLP when feeding 𝑥.
Based on the BERT unit, the name/description view was first performed. This work is illustrated in Fig. 3. In this view, entities’ descriptions are used as input (use entities’ names when missing), and the
vector representation of entity 𝐶 (𝑒) is obtained after passing through
the BERT unit. Then, the cosine similarity cos(𝐶(𝑒), 𝐶(𝑒′ )) is calculated
as the basis of EA.
3.2. Neighbor-view

𝑗=0

⎡ (𝑠max − 𝜇 )2 ⎤
)
(
𝑙
⎥,
⎢− 𝑖
𝐾𝑙 𝑠max
=
exp
𝑖
2
⎥
⎢
2𝜎
𝑙
⎦
⎣
(
)
[
(
)
(
)
(
)]
max
𝑠
, … , 𝐾𝐿 𝑠max
,
𝐊𝑟 𝐒𝑖 = 𝐾1 𝑠max
,
…
,
𝐾
𝑙
𝑖
𝑖
𝑖

In the neighbor view, we compare and calculate the neighbors  (𝑒)
of the entity 𝑒 with the neighbor  (𝑒′ ) of the entity 𝑒′ to obtain the
(
( ))
similarity vector 𝜙  (𝑒),  𝑒′ of the neighbors of the two entities.
This method is an interactive method. It does not rely on aggregating
neighbors’ name/descriptions to learn a global representation for 𝑒 or
𝑒′ [33,47].
The calculation steps in the neighbor-view are as follows:

(
( ))
𝜙𝑟  (𝑒),  𝑒′ =
4

|
(𝑒)|
∑
( )
1
log𝐊𝑟 𝑐 𝐒𝑖 .
| (𝑒)| 𝑖=1

(4)

Information Fusion 100 (2023) 101935

B. Zhu et al.

7. Combine the two similarity vectors in the row and column.
Obtain similarity vector 𝛷 for measuring the degree of matching
(
( ))
the entities. The calculation of 𝜙  (𝑒),  𝑒′ is presented in
Eq. (5) [22].
(
( ))
(
( ))
(
( ))
𝜙  (𝑒),  𝑒′ = 𝜙𝑟  (𝑒),  𝑒′ ⊕ 𝜙𝑐  (𝑒),  𝑒′ .
(5)

Algorithm 1 Framework of MMIEA
′

1: Input: Entity 𝑒 in 𝐾𝐺 and entity 𝑒′ in 𝐾𝐺
2: Output: Entity alignment result of 𝑒 and 𝑒′
3: if Name/Description information is present then
4:
Conduct work in Name/Description-View
5:
Gain cos(𝐶(𝑒), 𝐶(𝑒′ ))
6: end if
7: if Neighbor-View information is present then
8:
Conduct work in Neighbor-View
(
( ))
9:
Gain 𝜙  (𝑒),  𝑒′
10: end if
11: if Attribute-View information is present then
12:
Conduct work in Attribute-View
(
( ))
13:
Gain 𝜙 (𝑒),  𝑒′
14: end if
15: if Image-View information is present then
16:
Conduct work in Image-View (Algorithm 2)
(
( ))
17:
Gain 𝜙 (𝑒),  𝑒′
18: end if
19: Conduct fusion process and gain entity alignment result

3.3. Attribute-view
The attribute view is similar to the neighbor-view. The only difference is the key–value pair. The name of the attribute is the key, and
the content of the attribute is the value. The remainder is similar to
the neighbor-view. It is worth noting that the attributes of the entity
often have multiple pairs; therefore, we only need to consider several
attributes of the current entity to interact without considering any
neighbor information.
The calculation steps under the attribute view are as follows.
1. For each attribute of entity 𝑒 or 𝑒′ , apply the BERT unit with the
attribute’s value to obtain the collection of vector representation
{ ( )}|(𝑒)|
{ ( )}|(𝑒′ )|
𝐶 𝑎𝑖 𝑖=1 and 𝐶 𝑎′𝑖 𝑖=1 .
2. Based on the collection of vector representation, calculate attributing( entity
similarity matrix 𝑆, where 𝑠𝑖𝑗 makes up 𝑆, 𝑠𝑖𝑗 =
)
𝐶 (𝑎𝑖 )⋅𝐶 𝑎′𝑗
‖ ( )‖ .
‖𝐶 (𝑎𝑖 )‖⋅‖‖𝐶 𝑎′𝑗 ‖‖
‖

on representation learning can effectively eliminate the heterogeneity
between different modal information. Although the representations of
different modalities may be in their own representation spaces, the
structural consistency of the representation is the key to subsequent
multi-modal information.
In multi-modal entity alignment based on embedding, a key issue
is obtaining high-quality representations between various modalities.
For traditional triple information, many high-quality models have been
designed, such as the translation model TransE and its variants. However, current research has not explored the application of entity alignment to other modal information representation models, such as image
information.
BERT-INT [22] is a highly effective EA model. It is based on the
BERT [52] pretrained model to obtain entity embeddings and align
them based on the similarity of the entity embeddings. Additionally,
it uses an MLP for modal fusion, without the need to set weight
hyperparameters.
Inspired by BERT-INT [22], we adopted the idea of computing
the interactions between neighbor nodes to solve the problem that
equivalent entities often do not share similar neighbors. Because the
BERT-INT model does not specifically deal with multi-modal information, we improved the BERT-INT model, including a method for
processing image modalities and image interactions, enabling it to handle multi-modal entity alignment tasks. Specifically, we use interactive
techniques in image modality processing. In each interaction step, we
calculate the image similarity matrix of the neighbor entities for two
entities based on the current entity’s neighbor set and neighbor image
embeddings. Then, we process the rows and columns of the matrix
using max-pooling and kernel functions to obtain the final image view
vector.

‖

3. For each attribute of entities, apply the BERT unit with the
{ ( )}|(𝑟)|
{ ( )}|(𝑟′ )|
attribute’s name to obtain 𝐶 𝑛𝑖 𝑖=1 and 𝐶 𝑛′𝑖 𝑖=1 .
4. Based on Step 3, calculate attributing( name
mask matrix 𝑀,
)
𝐶 (𝑛𝑖 )⋅𝐶 𝑛′𝑗
where 𝑚𝑖𝑗 makes up 𝑀, 𝑚𝑖𝑗 =
‖ ( )‖ .
‖𝐶 (𝑛𝑖 )‖⋅‖‖𝐶 𝑛′𝑗 ‖‖
‖

‖

5. Multiply 𝑀 with 𝑆, i.e., 𝑆𝑖𝑗 = 𝑆𝑖𝑗 ⊗ 𝑀𝑖𝑗 .
6. 𝑆 is processed using max-pooling and kernel for each row and
column, respectively, to obtain the corresponding similarity vectors. These row similarity vectors and column similarity vectors
(
( ))
(
( ))
are calculated separately. 𝜙𝑟 (𝑒),  𝑒′ and 𝜙𝑐 (𝑒),  𝑒′
are obtained, similar to the Eq. (4).
7. Combine the similarity vector in the row and column. Obtain
(
( ))
the similarity vector 𝜙 (𝑒),  𝑒′ for measuring the degree
of matching the entities, similar to the Eq. (5).
4. MMIEA model
In this section, we introduce the MMIEA model in detail. This section contains our motivation and the detailed work on the image view.
Fig. 4 illustrates the framework. The pseudocode for MMIEA is shown
in Algorithm 1. By constructing four views, namely name/description,
neighbor, attribute, and image, MMIEA achieves multi-modal entity
alignment. In particular, MMIEA extends BERT-INT [22] to the multimodal knowledge graph scenario by adding an image-view, providing
richer information for entity alignment.
4.1. Motivation
Knowledge graph (KG) is a popular knowledge modeling technology
in both industrial and academic areas. It is a data structure composed
of nodes and edges to store knowledge data and has constructed
knowledge bases or KGs covering various fields. Representative KGs
include YAGO [48], FreeBase [49], DBpedia [50], and Omega [51].
They are widely used in popular fields such as search engines [6],
question answering [7], recommendation systems [8,9], and natural
language processing [10].
Most of the existing multi-modal entity alignment methods are
embedding-based methods; that is, information of different modalities
is projected into vectors first, and then the resulting vector representation is used for subsequent fusion or alignment. The method based

4.2. Interaction of image-view
The interaction of the image views consists of two cases. If an entity
has multiple images, we can refer to the attribute view for interaction.
However, the current public dataset of multi-modal KG has only one
image per entity, so we developed an alternative method of interaction.
First, we borrow images of entity’s neighbors as the basis and data
for multigraph interactions. Then, the embedding vector of multiple
images related to the entity constitutes the similarity matrix, similar
to Eq. (2) and (3). Finally, use Eqs. (4) and (5) to aggregate and obtain
the similarity under image-view. A diagram of the visual interaction is
shown in Fig. 4(b). The detailed steps are explained in Section 4.3.
5

Information Fusion 100 (2023) 101935

B. Zhu et al.

Fig. 4. Framework of our proposed MMIEA. (a) MMIEA introduces image views that contain rich information. The application of the framework in a remote sensing area can
effectively protect the data privacy because the data of different modalities get embedded and transmitted separately. (b) Diagram of image-view. First, obtain the entities’ vector
representation with image model. Then, obtain the visual image similarity matrix 𝑆 and neighboring relation mask matrix 𝑀. Finally, combine them and calculate similarity vector
𝜙 for measuring the degree of matching the entities under the image-view.

4.3. Image-view

Algorithm 2 Image-View
′

1: Input: Entity 𝑒 in 𝐾𝐺 and entity 𝑒′ in 𝐾𝐺
2: Output: Similarity vector 𝜙 of 𝑒 and 𝑒′
3: for each neighboring image 𝑖 of 𝑒 and 𝑖′ of 𝑒′ do
( )
4:
calculate embedding vectors 𝐶 (𝑖) and 𝐶 𝑖′
5: end for
6: calculate visual image similarity matrix 𝑆
7: for each relation 𝑟 and 𝑟′ of 𝑒 and 𝑒′ do
( )
8:
calculate embedding vectors 𝐶 (𝑟) and 𝐶 𝑟′
9: end for
10: calculate neighboring relation mask matrix 𝑀
11: 𝑆 = 𝑆 ⊗ 𝑀
12: Perform max-pooling and kernel on 𝑆, obtain 𝜙𝑟 and 𝜙𝑐
13: Combine 𝜙𝑟 and 𝜙𝑐 to gain similarity vector 𝜙

We introduced an image modal to determine whether a pair of
entities refers to the same real entity more accurately. For example,
it is difficult to distinguish Apple Inc. from apple the fruit in the text
‘‘apple’’, but it is easy to distinguish it from the images. The visual
features are more intuitive and serve as the icing on the cake for EA.
The image view is described in detail below:
First, we obtained the embedding vector of each image of the
entities. We learn the embedding vectors of images according to the
VGG16 [53] model. The filters in a stack of convolutional layers had
receptive fields of 3 × 3. There are 13 convolutional layers with different depths in the various architectures. The following are the three
fully connected layers. Then, we obtain 4096-dimensional embedding
vectors for all entities’ images.
Given a pair (𝑒𝑖 , 𝑖) ∈ 𝑌 , where 𝑌 is the visual knowledge in KG, we
use a score function to measure the visual features.
( )
‖2
𝑓𝑖𝑚𝑔 𝑒𝑖 , 𝑖 = − ‖
(6)
‖𝑒𝑖 − tanh(𝑣𝑒𝑐(𝑖))‖2 ,

(2) Based on the collection of embedding vectors, calculate visual image
similarity matrix 𝑆, where 𝑠𝑖𝑗 makes up 𝑆, 𝑠𝑖𝑗 =
( )
𝐶 (𝑖𝑖 )⋅𝐶 𝑖′𝑗
‖ ( )‖ .
‖𝐶 (𝑖𝑖 )‖⋅‖‖𝐶 𝑖′𝑗 ‖‖

where 𝑣𝑒𝑐(𝑖) denotes the projection and tanh(⋅) denotes the activation
function. Based on Eq. (6), we minimized the loss function as follows:
∑
(
(
( )))
𝐿𝑖𝑚𝑔 =
log 1 + exp −𝑓𝑖𝑚𝑔 𝑒𝑖 , 𝑖
.
(7)
(𝑒𝑖 ,𝑖)∈𝑌

‖

‖

(3) For each relation of neighbors, apply the BERT unit with the
{ ( )}| (𝑟)|
{ ( )}| (𝑟′ )|
relation’s name to obtain 𝐶 𝑟𝑖 𝑖=1 and 𝐶 𝑟′𝑖 𝑖=1
.
(4) Based on Step 3, calculate neighboring(relation
mask matrix 𝑀,
)
𝐶 (𝑟𝑖 )⋅𝐶 𝑟′𝑗
where 𝑚𝑖𝑗 makes up 𝑀, 𝑚𝑖𝑗 =
‖ ( )‖ .
‖𝐶 (𝑟𝑖 )‖⋅‖‖𝐶 𝑟′𝑗 ‖‖

The pseudocode for the algorithm of the image view is shown in
Algorithm 2.
The calculation steps under the image view are as follows.

‖

‖

(5) Multiply 𝑀 to 𝑆, i.e., 𝑆𝑖𝑗 = 𝑆𝑖𝑗 ⊗ 𝑀𝑖𝑗 .
(6) 𝑆 is processed using max-pooling and kernel for each row and
column,( to obtain
similarity vectors. We ob( ))the corresponding
(
( ))
tain 𝜙𝑟 (𝑒),  𝑒′ and 𝜙𝑐 (𝑒),  𝑒′ according to the Eq. (5)
in this step.

(1) For each entity 𝑒 or 𝑒′ , obtain the collection of embedding
{ ( )}|(𝑒)|
{ ( )}| (𝑒′ )|
vectors 𝐶 𝑖𝑖 𝑖=1 and 𝐶 𝑖′𝑖 𝑖=1
of its neighboring images
𝑖𝑖 , where the subscript 𝑖 from 1 to |(𝑒)| and |(𝑒′ )| respectively.
6

Information Fusion 100 (2023) 101935

B. Zhu et al.

(7) Combine the visual similarity vector in the row and column.
(
( ))
Obtain the similarity vector 𝜙 (𝑒),  𝑒′ for measuring the
degree of matching the entities, similar to the Eq. (5).

5.1. Setup
Datasets. We performed experiments on publicly available multimodal datasets FB15k-DB15K, and FB15K-YAGO15k. Each dataset provides 20%, 50%, and 80% of the reference EA as the training sets. The
basic statistics of the datasets are presented in Table 1.
Evaluation Metrics. Hits@n is the rate of correct entities ranked in
the top n according to the similarity scores. We used Hits@1, Hits@5
and Hits@10 for our experiments. MRR denotes the mean reciprocal
rank of the correct entity. Higher values of Hits@n and MRR explain
the improved performance of the model.
Settings. The dimensions of BERT’s CLS embedding were 768. We
use a 300-dimension MLP in Eq. (1) and an 11 plus 1-dimension MLP
in Eq. (10). The maximal numbers of neighbors and attributes in the
KGs were both set to 50. If more, cut off; if less, add 0. The aggregation
function was an RBF core aggregation function [55]. Image learning
and embedding were consistent with MMEA.
Baselines. The baselines for the comparative experiment are as
follows:

4.4. Vector fusion
We use two approaches to fuse vectors, a direct concatenation
operation and a gating-based fusion operation [54]. The following is
an introduction to these two methods: concatenation fusion and gated
fusion.
4.4.1. Concatenation fusion
we combine the work of the four views, the final fusion vector is
expressed as follows:
(
) [ (
( ))
(
( ))
𝜙 𝑒, 𝑒′ = cos 𝐶(𝑒), 𝐶 𝑒′ ⊕ 𝜙  (𝑒),  𝑒′
(8)
(
( ))
(
( ))]
⊕𝜙 (𝑒),  𝑒′ ⊕ 𝜙 (𝑒),  𝑒′
4.4.2. Gated fusion
We use a gating-based fusion method to fuse the image view with
other views. This model eliminates the need for manual parameter
tuning and instead learns to adjust parameters directly from the training data. Here, 𝑥𝑣 and 𝑥𝑡 represent feature vectors associated with
modalities 𝑣 and 𝑡, respectively. Each feature vector is processed by a
neuron (multiplicative gate) with a hyperbolic tangent (tanh) activation
function to encode an internal representation feature ℎ𝑣 and ℎ𝑡 for the
specific modality. For the input modalities 𝑥𝑣 and 𝑥𝑡 , a gate neuron
employing the Sigmoid function controls the balance of the overall
output derived from the computed features of 𝑥𝑣 and 𝑥𝑡 . The specific
calculation formula is as follows:
h𝑣 = tanh(𝑊𝑣 𝑥𝑣 )
h𝑡 = tanh(𝑊𝑡 𝑥𝑡 )
𝑧 = 𝜎(𝑊𝑧 [𝑥𝑣 ⊕ 𝑥𝑡 ])
𝜙(𝑒, 𝑒′ ) = 𝑧 ∗ ℎ𝑣 + (1 − 𝑧) ∗ ℎ𝑡

• TransE [18] is a typical KG embedding model.
• MTransE [29] learns the embedding representation of entities
and relations in a single KG first, and then learns the transfer
matrix to map the aligned entities from different KGs in the
unified space.
• IPTransE [30] also learns the embedding of a single KG first,
and then obtains the embedding of entities through iteration and
parameter sharing.
• SEA [56] is a semi-supervised method, which uses labeled entities
and abundant unlabeled entity information to align entities.
• GCN-Align [32] is a new way to combine edge information,
which captures the structure and entity attributes of KG based
on GCN coding.
• IMUSE [57] uses an unsupervised approach to generate a large
number of high-quality aligned entities.
• PoE [20] combines multi-modal features and measures the reliability of matching by matching the underlying semantics of
entities and mining the relations contained in the embedded
space.
• HMEA [13] models structure and visual features in the hyperbolic space that can reduce distortion of learned multi-modal
embeddings.
• MMEA [21] first learns the embeddings of multiple modalities
separately and then maps these embeddings with separated spaces
into a common space.
• EVA [58] jointly learns the multi-modal embeddings and combines these embeddings using the weight concatenation fusion
method for final EA.
• MCLEA [41] is a multi-modal contrastive learning based EA
model. It obtains effective joint representations for multi-modal
EA and performs contrastive learning to jointly model intra-modal
and inter-modal interactions.
• MultiJAF [40] model learns the embedding of structure, attributes, image in KG, and designs a special module to process
the numerical value; progress has been made in the experiment
of EA.
• BERT-INT [22] model is a BERT-based interaction model that
performs entity alignment by computing interactions between
neighboring entities.
• DFMKE [59] model uses a dual-fusion multi-modal knowledge
graph embedding framework that combines early fusion and late
fusion.
• MEAformer [60] is a multi-modal entity alignment transformer
approach for meta modality hybrid, which dynamically predicts
the mutual correlation coefficients among modalities for entitylevel feature aggregation.

(9)

(
( ))
(
Among them, 𝑥𝑣 = 𝛷((𝑒), (𝑒′ )), 𝑥𝑡 = cos 𝐶(𝑒), 𝐶 𝑒′ ⊕ 𝜙  (𝑒),
( ′ ))
( ′)
′
 𝑒
⊕ 𝜙 (𝑒) ,  𝑒 , 𝜙(𝑒, 𝑒 ) is the final fusion vector. the parameters in 𝜃 = {𝑊𝑣 , 𝑊𝑡 , 𝑊𝑧 } are learnable, and ⊕ represents the
concatenation operation.
4.5. Loss function
We then obtain the final similarity scores of 𝑒 and 𝑒′ .
( ′)
( (
))
𝑔 𝑒, 𝑒 = MLP 𝜙 𝑒, 𝑒′ .

(10)

The pairwise margin loss function is expressed as follows:
∑
{
(
)
(
)
}
=
max 0, 𝑔 𝑒, 𝑒′− − 𝑔 𝑒, 𝑒′+ + 𝑚 ,

(11)

(𝑒,𝑒′+ ,𝑒′− )∈

{( ′+ ′− )}
where the training data are  =
𝑒, 𝑒 , 𝑒
, and every triplet
( ′+ ′− )
𝑒, 𝑒 , 𝑒
∈  contains a queried entity 𝑒 ∈ 𝐸, rightly aligned
counterpart 𝑒′+ ∈ 𝐸 ′ and negative counterpart 𝑒′− ∈ 𝐸 ′ . 𝑚 is the margin
(
)
between the positive and negative pairs and 𝑔 𝑒, 𝑒′ is instantiated as
( )
𝐿1 distance to measure the similarity between 𝐶 (𝑒) and 𝐶 𝑒′ .
5. Experiments
To illustrate the validity of the proposed model and its modules,
experiments were conducted to answer the following three main questions:
RQ1: Does our model outperform the state-of-the-art models in
multi-modal EA applications?
RQ2: Does the multi-modal method and edge information in our
model make sense in multi-modal EA applications?
RQ3: Does the fusion of multiple views in our model make sense in
our model?
7

Information Fusion 100 (2023) 101935

B. Zhu et al.
Table 1
Basic statistics of the datasets.
Datasets

Entities

Relations

Attributes

Relational triples

Attributes triples

Images

FB15K
DB15K
YAGO15K

14,951
12,842
15,404

1,345
279
32

116
225
7

592,213
89,197
122,886

29,395
48,080
23,532

13,444
12,837
11,194

Fig. 5. Comparison of EA results of different models in the FB15K-DB15K and FB15K-YAGO15K datasets.

• MSNEA [61] designs a multi-modal knowledge embedding module to extract the visual, relational and attribute features of
entities, making full use of multi-modal knowledge.

5.3. Comparison analysis (RQ2)

Multi-modal vs. Single-modal. In general, multi-modal models are
significantly better than single-modal ones. The MMEA increased the
metric of Hits@1 to 26.5%. Subsequently, MCLEA and MultiJAF increased Hits@1 of EA to 44.5% and 48.0%, respectively. The remaining
metrics, including Hits@5, Hits@10, and MRR, showed remarkable
improvements in MMEA, MCLEA, MultiJAF, and our MMIEA.

5.2. Performance analysis (RQ1)
We experimented with the latest multi-modal EA models. We divided these baselines into two categories: single-modal and multimodal. The detailed experimental data are listed in Table 2. In Fig. 5,
the abilities of the different models are clearly displayed in several
pillar diagrams. The results of the comparison models were obtained
from original studies to ensure that the results were realistic and valid.
Our model achieved the best results and was far superior to those
of the other models. The reason for the optimal effect is that our
model is multi-modal and uses a large amount of side information.
Overall, the development of these baselines has progressed from singlemodal to multi-modal, and from simple structure information to multimodal information. Moreover, the accuracy of the models gradually
improved. Experimental results show that our model is the best in
the task of multi-modal EA, with a significant margin compared with
state-of-the-art methods.

Side Information vs. Structural Information. The models with
side information were better than those with only structural information. TransE, which considers only structural information, has a
poor effect. However, embedded models such as MMEA, MCLEA and
MultiJAF have made great progress because of the combination of more
side information, particularly attributes, numerical values, and image
information. Our MMIEA makes significant progress by using the BERT
model to process side information. Therefore, it is better to use side
information in EA.
8

Information Fusion 100 (2023) 101935

B. Zhu et al.
Table 2
Results of comparison on multi-modal EA.
Type

Model

Single-modal

Multi-modal

FB15K-DB15K

FB15K-YAGO15K

Hits@1

Hits@5

Hits@10

MRR

Hits@1

Hits@5

Hits@10

MRR

MTransE [29]
IPTransE [30]
TransE [18]
PoE-l [20]
SEA [56]
GCN-Align [32]
IMUSE [57]
BERT-INT [58]

.003
.039
.078
.079
.169
.043
.176
.775

.014
.122
.179
–
.335
.109
.346
.826

.025
.173
.241
.203
.425
.155
.435
.832

.013
.086
.134
.122
.260
.082
.264
.798

.003
.031
.064
.064
.141
.023
.081
.793

.009
.095
.151
–
.287
.072
.192
.826

.017
.144
.203
.169
.372
.107
.257
.830

.011
.070
.112
.101
.218
.053
.142
.808

PoE-lni [20]
HMEA [13]
MMEA [21]
EVA [58]
MCLEA [41]
MultiJAF [40]
DFMKE [59]
MSNEA [61]
MEAformer [60]
MMIEA (concatenation)
MMIEA (gated)

.120
.127
.265
.213
.445
.480
.338
.652
.578
.776
.778

–
–
.451
.391
–
.576
–
.768
–
.826
.827

.256
.369
.541
.475
.705
.601
.654
.812
.812
.831
.833

.167
–
.357
.301
.534
.523
.55
.708
.661
.798
.799

.109
.105
.234
.171
.388
.463
.367
.442
.444
.793
.793

–
–
.398
.335
–
.658
–
.625
–
.826
.827

.241
.313
.479
.417
.641
.731
.645
.698
.692
.831
.831

.154
–
.317
.260
.474
.554
.51
.529
.529
.808
.808

Table 3
Ablation study on multi-modal EA with different component and training ratios.
Training ratios

0.2

0.5

0.8

Component

FB15K-DB15K

FB15K-YAGO15K

Hits@1

Hits@5

Hits@10

MRR

Hits@1

Hits@5

Hits@10

MRR

BERT unit
name
neighbor
attribute
image
w/o image
MMIEA (concatenation)
MMIEA (gated)

.6778
.6780
.6008
.7066
.0633
.7757
.7762
.7783

.7790
.7797
.7218
.8015
.2142
.8266
.8265
.8269

.8033
.8040
.7564
.8149
.3503
.8321
.8316
.8332

.7233
.7237
.6570
.7495
.1555
.7981
.7979
.7995

.6783
.6783
.5345
.7769
.0808
.7937
.7938
.7937

.7738
.7738
.6679
.8229
.2161
.8263
.8267
.8269

.7972
.7972
.7091
.8274
.3213
.8306
.8307
.8309

.7213
.7212
.5973
.7972
.1631
.8082
.8086
.8080

BERT unit
name
neighbor
attribute
image
w/o image
MMIEA (concatenation)
MMIEA (gated)

.6993
.6995
.6222
.7179
.0711
.7883
.7885
.7797

.7918
.7925
.7323
.8089
.2389
.8302
.8304
.8325

.8069
.8076
.7639
.8192
.3674
.8347
.8350
.8352

.7404
.7408
.6744
.7592
.1674
.8073
.8070
.8082

.7346
.7346
.5749
.8144
.0846
.8319
.8321
.8331

.8110
.8110
.7042
.8535
.2193
.8578
.8580
.8594

.8303
.8303
.7446
.8573
.3366
.8610
.8606
.8607

.7701
.7701
.6366
.8321
.1690
.8348
.8438
.8449

BERT unit
name
neighbor
attribute
image
w/o image
MMIEA (concatenation)
MMIEA (gated)

.7524
.7524
.6644
.7469
.0731
.8330
.8318
.8373

.8232
.8232
.7645
.8088
.2417
.8610
.8614
.8602

.8341
.8341
.7960
.8225
.3752
.8645
.8657
.8649

.7832
.7832
.7121
.7760
.1722
.8461
.8456
.8419

.7606
.7606
.6068
.8240
.0920
.8374
.8383
.8392

.8173
.8173
.7107
.8521
.2362
.8544
.8552
.8557

.8302
.8302
.7507
.8553
.3497
.8570
.8575
.8584

.7877
.7877
.6589
.8369
.1808
.8455
.8459
8468

of around 0.2% after incorporating the image modality, while
HMEA only showed a 1% improvement after replacing image
data through web crawling. Therefore, we believe that the performance of the image modality depends not only on the method
itself but also on the quality of the data. Furthermore, the paper [62] also mentioned the poor performance of the image data
in this dataset, as it introduced a significant amount of noise and
even caused a decrease in model accuracy after incorporating the
image modality.

5.4. Multi-view analysis (RQ3)
We also performed a separate EA experiment on each view, called
an ablation study, under different partitions of the training and test
datasets. The ablation study results are presented in Table 3.
• Validity of the BERT. The BERT model performs reasonably
well, and simply using BERT in experimentation can surpass the
previous model. Our improvement over the previous model is
largely due to the Bert model.
• The Importance of Image. Experiments using only image modes
were not effective enough to support the whole EA tasks, possibly
because of the low number and poor quality of images. But it is
indisputable that the image modal has played a role as the icing
on the cake.
• The Image Data in the Dataset is of Poor Quality. Although
the addition of the image modality only resulted in a slight
improvement of around 0.2%, it still showed some positive effect.
When using the same dataset, MMEA achieved an improvement

5.5. Parameter analysis
In Fig. 6, we compare the impact of different numbers of the hidden
nodes in the MLP layer for the fusion module. It can be found that our
model is insensitive to this hyper-parameter and satisfactory results can
be obtained for all cases.
In Table 4, we conducted ablation experiments with combinations
of different views in the MMIEA model to verify the effectiveness of
9

Information Fusion 100 (2023) 101935

B. Zhu et al.

Fig. 6. Comparison results with different numbers of the hidden nodes for the fusion module.

Table 4
Ablation study of MMIEA with different combinations of views.
Component

name+image
neighbor+image
attribute+image

FB-DB

FB-YAGO

Hits@1

Hits@5

Hits@10

MRR

Hits@1

Hits@5

Hits@10

MRR

.68166
.59910
.71203

.78320
.72313
.80335

.80695
.75574
.81659

.72724
.65634
.75317

.68054
.53689
.77810

.77743
.67016
.82208

.79942
.71258
.82654

.72340
.59915
.79772

Declaration of competing interest

different views. The experimental results demonstrate that the model
with the addition of picture views improves the accuracy, compared to
a single view.

The authors declare that they have no known competing financial interests or personal relationships that could have appeared to
influence the work reported in this paper.

6. Conclusions

Data availability

Entity alignment is fundamental for supporting the downstream application of the knowledge graph. Many researchers use the structural
information of KG to align entities, but the side information, such as
descriptions and attributes, is not sufficient. In particular, the use of
multi-modal information such as images further affects the accuracy of
entity alignment. To this end, we propose a multi-modal interaction entity alignment model (MMIEA) to completely utilize side information,
including descriptions, attributes, and images. It calculates the degree
of matching of entities in an interactive manner. Extensive experiments
on two public datasets demonstrated the effectiveness of the MMIEA
model with a significant margin compared to state-of-the-art methods.

No data was used for the research described in the article.
Acknowledgments
This work was supported in part by the National Natural Science Foundation of China (under grants 61806065, 61976120 and
62120106008), the Natural Science Key Foundation of Jiangsu Education Department under Grant 21KJA510004, the Fundamental Research
Funds for the Central Universities (under grant JZ2022HGTB0239), and
the Open Fund of Infrared and Low Temperature Plasma Key Laboratory of Anhui Province, NUDT, China under grants IRKL2022KF06 and
KYWX2023002. Our codes can be obtained upon request.

CRediT authorship contribution statement
Bin Zhu: Conceptualization, Methodology, Review & editing. Meng
Wu: Writing – original draft, Data curation, Visualization, Writing –
review & editing. Yunpeng Hong: Data curation, Writing – review &
editing. Yi Chen: Discussed the results, Writing – review & editing. Bo
Xie: Discussed the results, Writing – review & editing. Fei Liu: Data
curation, Writing – review & editing. Chenyang Bu: Conceptualization,
Investigation, Supervision, Writing – review & editing. Weiping Ding:
Methodology, Investigation, Supervision, Writing – review & editing.

References
[1] Sameer Hasija, Zuo-Jun Max Shen, Chung-Piaw Teo, Smart city operations:
Modeling challenges and opportunities, Manuf. Serv. Oper. Manag. 22 (1) (2020)
203–213.
[2] Simon Elias Bibri, John Krogstie, Smart sustainable cities of the future: An
extensive interdisciplinary literature review, Sustainable Cities Soc. 31 (2017)
183–212.
10

Information Fusion 100 (2023) 101935

B. Zhu et al.

[29] Muhao Chen, Yingtao Tian, Mohan Yang, Carlo Zaniolo, Multilingual knowledge
graph embeddings for cross-lingual knowledge alignment, in: Proceedings of
International Joint Conference on Artificial Intelligence, 2017, pp. 1511–1517.
[30] Hao Zhu, Ruobing Xie, Zhiyuan Liu, Maosong Sun, Iterative entity alignment via
joint knowledge embeddings, in: Proceedings of International Joint Conference
on Artificial Intelligence, 2017, pp. 4258–4264.
[31] Kexuan Xin, Zequn Sun, Wen Hua, Wei Hu, Jianfeng Qu, Xiaofang Zhou,
Large-scale entity alignment via knowledge graph merging, partitioning and
embedding, in: Proceedings of ACM International Conference on Information &
Knowledge Management, 2022, pp. 2240–2249.
[32] Zhichun Wang, Qingsong Lv, Xiaohan Lan, Yu Zhang, Cross-lingual knowledge
graph alignment via graph convolutional networks, in: Proceedings of Conference
on Empirical Methods in Natural Language Processing, 2018, pp. 349–357.
[33] Yuting Wu, Xiao Liu, Yansong Feng, Zheng Wang, Rui Yan, Dongyan Zhao,
Relation-aware entity alignment for heterogeneous knowledge graphs, in: Proceedings of the International Joint Conference on Artificial Intelligence, 2019,
pp. 5278–5284.
[34] Tam Thanh Nguyen, Thanh Trung Huynh, Hongzhi Yin, Vinh Van Tong, Darnbi
Sakong, Bolong Zheng, Quoc Viet Hung Nguyen, Entity alignment for knowledge
graphs with multi-order convolutional networks, IEEE Trans Knowl. Data Eng.
34 (09) (2020) 4201–4214.
[35] Congcong Ge, Xiaoze Liu, Lu Chen, Baihua Zheng, Yunjun Gao, Make it easy: An
effective end-to-end entity alignment framework, in: Proceedings of International
ACM SIGIR Conference on Research and Development in Information Retrieval,
2021, pp. 777–786.
[36] Weixin Zeng, Xiang Zhao, Jiuyang Tang, Xuemin Lin, Paul Groth, Reinforcement
Learning–based Collective Entity Alignment with Adaptive Features, ACM Trans.
Inf. Syst. 39 (3) (2021) 1–31.
[37] Zequn Sun, Wei Hu, Chengming Wang, Yuxin Wang, Yuzhong Qu, Revisiting
embedding-based entity alignment: A robust and adaptive method, IEEE Trans.
Knowl. Data Eng. (2022) 1–14.
[38] Jinghui Peng, Xinyu Hu, Wenbo Huang, Jian Yang, What is a multi-modal
knowledge graph: A survey, Big Data Res. 32 (2023) 100380.
[39] Fangyu Liu, Muhao Chen, Dan Roth, Nigel Collier, Visual pivoting for (unsupervised) entity alignment, in: Proceedings of the AAAI Conference on Artificial
Intelligence, vol. 35, (no. 5) 2021, pp. 4257–4266.
[40] Bo Cheng, Jia Zhu, Meimei Guo, MultiJAF: Multi-modal joint entity alignment
framework for multi-modal knowledge graph, Neurocomputing 500 (2022)
581–591.
[41] Zhenxi Lin, Ziheng Zhang, Meng Wang, Yinghui Shi, Xian Wu, Yefeng Zheng,
Multi-modal contrastive representation learning for entity alignment, in: Proceedings of International Conference on Computational Linguistics, 2022, pp.
2572–2584.
[42] Dongxu Li, Junnan Li, Hongdong Li, Juan Carlos Niebles, Steven C.H. Hoi,
Align and prompt: Video-and-language pre-training with entity prompts, in:
Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern
Recognition, 2022, pp. 4953–4963.
[43] Xinyu Lu, Lifang Wang, Zejun Jiang, Shichang He, Shizhong Liu, MMKRL: A
robust embedding approach for multi-modal knowledge graph representation
learning, Appl. Intell. 52 (7) (2022) 7480–7497.
[44] Shahi Dost, Luciano Serafini, Marco Rospocher, Lamberto Ballan, Alessandro
Sperduti, Aligning and linking entity mentions in image, text, and knowledge
base, Data Knowl. Eng. 138 (2022) 101975.
[45] Zhiyuan Ma, Jianjun Li, Guohui Li, Yongjing Cheng, UniTranSeR: A unified
transformer semantic representation framework for multimodal task-oriented
dialog system, in: Proceedings of the Association for Computational Linguistics,
2022, pp. 103–114.
[46] Chenxu Wang, Zhenhao Huang, Yue Wan, Junyu Wei, Junzhou Zhao, Pinghui
Wang, Fualign: Cross-lingual entity alignment via multi-view representation
learning of fused knowledge graphs, Inf. Fusion 89 (2023) 41–52.
[47] Kun Xu, Liwei Wang, Mo Yu, Yansong Feng, Yan Song, Zhiguo Wang, Dong Yu,
Cross-lingual knowledge graph alignment via graph matching neural network, in:
Proceedings of Annual Meeting of the Association for Computational Linguistics,
2019, pp. 3156–3161.
[48] Fabian M. Suchanek, Gjergji Kasneci, Gerhard Weikum, YAGO: A large ontology
from wikipedia and WordNet, J. Web Semant. 6 (3) (2008) 203–217.
[49] Kurt Bollacker, Colin Evans, Praveen Paritosh, Tim Sturge, Jamie Taylor, Freebase: A collaboratively created graph database for structuring human knowledge,
in: Proceedings of ACM SIGMOD International Conference on Management of
Data, 2008, pp. 1247–1250.
[50] Jens Lehmann, Robert Isele, Max Jakob, Anja Jentzsch, Dimitris Kontokostas,
Pablo N. Mendes, Sebastian Hellmann, Mohamed Morsey, Patrick Van Kleef,
Sören Auer, Christian Bizer, DBpedia - A large-scale, multilingual knowledge
base extracted from Wikipedia, Semantic Web 6 (2) (2015) 167–195.
[51] Andrew Philpot, Eduard Hovy, Patrick Pantel, The omega ontology, in:
Proceedings of Ontologies and Lexical Resources, 2010, pp. 59–66.
[52] Jacob Devlin, Ming Wei Chang, Kenton Lee, Kristina Toutanova, BERT: Pretraining of deep bidirectional transformers for language understanding, in:
Proceedings of Conference of the North American Chapter of the Association
for Computational Linguistics: Human Language Technologies, vol. 1, 2019.

[3] Samiksha Shukla, Balachandran K., Sumitha V. S., A framework for smart
transportation using big data, in: Proceedings of International Conference on
ICT in Business Industry & Government, 2016, pp. 1–3.
[4] Wardani Muhamad, Novianto Budi Kurniawan, Suhardi, Setiadi Yazid, Smart
campus features, technologies, and applications: A systematic literature review,
in: Proceedings of International Conference on Information Technology Systems
and Innovation, 2017, pp. 384–391.
[5] Nikolaos Dimakis, Avgoustinos Filippoupolitis, Erol Gelenbe, Distributed building
evacuation simulator for smart emergency management, Comput. J. 53 (9)
(2010) 1384–1400.
[6] Ahmet Uyar, Farouk Musa Aliyu, Evaluating search features of Google Knowledge
graph and Bing Satori, Online Inf. Rev. 39 (2) (2015) 197–213.
[7] Shuguang Zhu, Xiang Cheng, Sen Su, Knowledge-based question answering by
tree-to-sequence learning, Neurocomputing 372 (2020) 64–72.
[8] Hongwei Wang, Miao Zhao, Xing Xie, Wenjie Li, Minyi Guo, Knowledge graph
convolutional networks for recommender systems, in: Proceeding of World Wide
Web Conference, 2019, pp. 3307–3313.
[9] Ru Wang, Meng Wu, Shengwei Ji, Meta-path enhanced knowledge graph convolutional network for recommender systems, in: Proceedings of IEEE International
Conference on Big Knowledge, 2021, pp. 110–116.
[10] Ishani Mondal, Yufang Hou, Charles Jochim, End-to-end construction of
NLP knowledge graph, in: Proceeding of the Association for Computational
Linguistics, 2021, pp. 1885–1895.
[11] Tong Yu, Jinghua Li, Qi Yu, Ye Tian, Xiaofeng Shun, Lili Xu, Ling Zhu, Hongjie
Gao, Knowledge graph for TCM health preservation: Design, construction, and
applications, Artif. Intell. Med. 77 (2017) 48–52.
[12] Xiangru Zhu, Zhixu Li, Xiaodan Wang, Xueyao Jiang, Penglei Sun, Xuwu Wang,
Yanghua Xiao, Nicholas Jing Yuan, Multi-modal knowledge graph construction and application: A survey, IEEE Trans. Knowl. Data Eng. (2022) 1–20,
doi:10.1109/TKDE.2022.3224228.
[13] Hao Guo, Jiuyang Tang, Weixin Zeng, Xiang Zhao, Li Liu, Multi-modal entity
alignment in hyperbolic space, Neurocomputing 461 (2021) 598–607.
[14] Tingting Jiang, Chenyang Bu, Yi Zhu, Xindong Wu, Combining embedding-based
and symbol-based methods for entity alignment, Pattern Recognit. 124 (2022)
108433.
[15] Tingting Jiang, Chenyang Bu, Yi Zhu, Xindong Wu, Two-stage entity alignment:
Combining hybrid knowledge graph embedding with similarity-based relation
alignment, in: Proceedings of Pacific Rim International Conference on Artificial
Intelligence, 2019, pp. 162–175.
[16] Lingbing Guo, Qiang Zhang, Zequn Sun, Mingyang Chen, Wei Hu, Huajun Chen,
Understanding and improving knowledge graph embedding for entity alignment,
in: Proceedings of International Conference on Machine Learning, 2022, pp.
8145–8156.
[17] Kexuan Xin, Zequn Sun, Wen Hua, Wei Hu, Xiaofang Zhou, Informed multicontext entity alignment, in: Proceedings of ACM International Conference on
Web Search and Data Mining, 2022, pp. 1197–1205.
[18] Antoine Bordes, Nicolas Usunier, Alberto Garcia-Duran, Jason Weston, Oksana
Yakhnenko, Translating embeddings for modeling multi-relational data, in:
Proceedings of Advances in Neural Information Processing Systems, 2013, pp.
2787–2795.
[19] Sun Xian, Tian Yu, Lu Wanxuan, Wang Peijing, Niu Ruigang, Yu Hongfeng,
Fu Kun, From single- to multi-modal remote sensing imagery interpretation: A
survey and taxonomy, Sci. China Inf. Sci. 66 (4) (2023) 1–28.
[20] Ye Liu, Hui Li, Alberto Garcia-Duran, Mathias Niepert, Daniel Onoro-Rubio,
David S. Rosenblum, MMKG: Multi-modal knowledge graphs, in: Proceedings
of the Semantic Web, 2019, pp. 459–474.
[21] Liyi Chen, Zhi Li, Yijun Wang, Tong Xu, Zhefeng Wang, Enhong Chen, MMEA:
Entity alignment for multi-modal knowledge graph, in: Proceedings of Knowledge
Science, Engineering and Management, 2020, pp. 134–147.
[22] Xiaobin Tang, Jing Zhang, Bo Chen, Yang Yang, Hong Chen, Cuiping Li,
BERT-INT: A BERT-based interaction model for knowledge graph alignment, in:
Proceedings of International Joint Conference on Artificial Intelligence, 2020,
pp. 3174–3180.
[23] Kaisheng Zeng, Chengjiang Li, Lei Hou, Juanzi Li, Ling Feng, A comprehensive
survey of entity alignment for knowledge graphs, AI Open 2 (2021) 1–13.
[24] Rui Zhang, Bayu Distiawan Trisedya, Miao Li, Yong Jiang, Jianzhong Qi, A
benchmark and comprehensive survey on knowledge graph entity alignment via
representation learning, VLDB J. 31 (5) (2022) 1143–1168.
[25] Zequn Sun, Qingheng Zhang, Wei Hu, Chengming Wang, Muhao Chen, Farahnaz Akrami, Chengkai Li, A benchmarking study of embedding-based entity
alignment for knowledge graphs, Proc. VLDB Endow. 13 (11) (2020) 2326–2340.
[26] Shaoxiong Ji, Shirui Pan, Erik Cambria, Pekka Marttinen, S. Yu Philip, A survey
on knowledge graphs: Representation, acquisition, and applications, IEEE Trans.
Neural Netw. Learn. Syst. 33 (2) (2021) 494–514.
[27] Marko Gulić, Ivan Magdalenić, Boris Vrdoljak, Ontology matching using TF/IDF
measure with synonym recognition, in: Information and Software Technologies,
2013, pp. 22–33.
[28] Indrajit Bhattacharya, Lise Getoor, A latent dirichlet model for unsupervised
entity resolution, in: Proceedings of SIAM International Conference on Data
Mining, 2006, pp. 47–58.
11

Information Fusion 100 (2023) 101935

B. Zhu et al.
[53] Karen Simonyan, Andrew Zisserman, Very deep convolutional networks for largescale image recognition, in: Proceedings of International Conference on Learning
Representations, 2015, [Online]. Available: http://arxiv.org/abs/1409.1556.pdf.
[54] John Arevalo, Thamar Solorio, Manuel Montes-y Gómez, Fabio A. González,
Gated multimodal units for information fusion, 2017, http://dx.doi.org/
10.48550/arXiv.1702.01992, [Online]. Available: https://arxiv.org/abs/1702.
01992.pdf.
[55] Chenyan Xiong, Zhuyun Dai, Jamie Callan, Zhiyuan Liu, Russell Power, End-toend neural ad-hoc ranking with kernel pooling, in: Proceedings of International
ACM SIGIR Conference on Research and Development in Information Retrieval,
2017, pp. 55–64.
[56] Shichao Pei, Lu Yu, Robert Hoehndorf, Xiangliang Zhang, Semi-supervised entity
alignment via knowledge graph embedding with awareness of degree difference,
in: Proceedings of World Wide Web Conference, 2019, pp. 3130–3136.
[57] Fuzhen He, Zhixu Li, Yang Qiang, An Liu, Guanfeng Liu, Pengpeng Zhao, Lei
Zhao, Min Zhang, Zhigang Chen, Unsupervised entity alignment using attribute
triples and relation triples, in: Proceedings of Database Systems for Advanced
Applications, 2019, pp. 367–382.
[58] Fangyu Liu, Muhao Chen, Dan Roth, Nigel Collier, Visual pivoting for (unsupervised) entity alignment, in: Proceedings of the AAAI Conference on Artificial
Intelligence, 2021, pp. 4257–4266.
[59] Jia Zhu, Changqin Huang, Pasquale De Meo, DFMKE: A dual fusion multi-modal
knowledge graph embedding framework for entity alignment, Inf. Fusion 90
(2023) 111–119.
[60] Zhuo Chen, Jiaoyan Chen, Wen Zhang, Lingbing Guo, Yin Fang, Yufeng Huang,
Yuxia Geng, Jeff Z. Pan, Wenting Song, Huajun Chen, MEAformer: Multimodal entity alignment transformer for meta modality hybrid, 2022, http://dx.
doi.org/10.48550/arXiv.2212.14454, [Online]. Available: https://arxiv.org/abs/
2212.14454.pdf.
[61] Liyi Chen, Zhi Li, Tong Xu, Han Wu, Zhefeng Wang, Nicholas Jing Yuan, Enhong
Chen, Multi-modal siamese network for entity alignment, in: Proceedings of
ACM SIGKDD Conference on Knowledge Discovery and Data Mining, 2022, pp.
118–126.
[62] Fenglong Su, Chengjin Xu, Han Yang, Zhongwu Chen, Ning Jing, Neural entity
alignment with cross-modal supervision, Inf. Process. Manage. 60 (2) (2023)
103174.

Bo Xie is a lecturer at the State Key Laboratory of Pulsed
Power Laser Technology, National University of Defense
Technology, Hefei, China. He received his BS and MS
degrees in Optical Engineering from the National University
of Defense Technology in 2016 and 2018 respectively.
His research interests include machine learning and image
processing.

Fei Liu received her B.E. degree and M.E. degree in 2016
and 2019 from Hefei University of Technology, China,
respectively. Now she is pursuing her Ph.D at the School
of Computer Science and Information Engineering in Hefei
University of Technology, China. Her research mainly lies
in educational data mining and knowledge graphs. She has
published articles in international conferences and journals,
such as ACM KDD, IEEE Transactions on Fuzzy Systems
(IEEE TFS) and IEEE Transactions on Emerging Topics
in Computational Intelligence (IEEE TETCI). She is a PC
member of WWW’22, AAAI’23.

Chenyang Bu is an associate professor at Key Laboratory
of Knowledge Engineering with Big Data (the Ministry of
Education of China), Hefei University of Technology, Hefei,
China. He obtained the Ph. D degree from University of
Science and Technology of China. He is a recipient of a Best
Paper Award at IEEE International Conference on Knowledge Graph (ICKG) 2020 and a Best Student Paper Award at
ICKG 2022. His research interests include knowledge graph
construction and application, as well as automated graph
learning with evolutionary algorithms.

Bin Zhu Associate professor, deputy director of State Key
Laboratory of Pulsed Power Laser Technology (Hefei China),
National University of Defense Technology. He received his
MS, PhD degrees in Optical Engineering and Signal and
Information Processing from National University of Defense
Technology, in 2007 and 2010 respectively. His study focuses on machine learning and image processing, including
multi-modal information fusion, target and environment
intelligent perception, etc.

Weiping Ding received the Ph.D. degree in Computer
Science, Nanjing University of Aeronautics and Astronautics
(NUAA), Nanjing, China, in 2013. From 2014 to 2015, he
is a Postdoctoral Researcher at the Brain Research Center,
National Chiao Tung University (NCTU), Hsinchu, Taiwan.
In 2016, He was a Visiting Scholar at National University
of Singapore (NUS), Singapore. From 2017 to 2018, he
was a Visiting Professor at University of Technology Sydney
(UTS), Ultimo, NSW, Australia. He is currently a professor
with the School of Information Science and Technology,
Nantong University, Nantong, China, and also the supervisor
of Master and Ph.D postgraduate by the Faculty of Data
Science at City University of Macau. His research interests
include deep neural networks, multi-modal machine learning, granular data mining, and medical images analysis. In
these areas, he has published over 200 scientific articles
in refereed international journals, such as IEEE T-FS, TNNLS, T-CYB, T-SMCS, T-BME, T-EVC, T-II, T-ETCI, T-CDS,
T-ITS and T-AI. He has held 20 approved invention patents
in total over 35 issued patents. He has co-authored two
books. His fifteen authored/co-authored papers have been
selected as ESI Highly Cited Papers (i.e. listed in Top 1%
globally in the corresponding discipline). Dr. Ding is the
Founding Chair of IEEE CIS Task Force on Granular Data
Mining for Big Data. He is vigorously involved in editorial activities. He served/serves on the Editorial Advisory
Board of Knowledge-Based Systems and Editorial Board of
Information Fusion, Engineering Applications of Artificial
Intelligence and Applied Soft Computing. He served/serves
as an Associate Editor of IEEE Transactions on Neural
Networks and Learning Systems, IEEE Transactions on Fuzzy
Systems, IEEE/CAA Journal of Automatica Sinica, Information Sciences, Neurocomputing, Swarm and Evolutionary
Computation, IEEE Access and Journal of Intelligent &
Fuzzy Systems, and Co-Editor-in-Chief of Journal of Artificial Intelligence and System. He is the Leading Guest
Editor of Special Issues in several prestigious journals,
including IEEE Transactions on Evolutionary Computation,
IEEE Transactions on Fuzzy Systems.

Meng Wu received his bachelor’s degree from Hefei University of Technology in 2020. He is currently working
toward the master’ s degree with the School of Computer
Science and Information Engineering, Hefei University of
Technology, Hefei, China. His research interests lie in
entity alignment and recommendation systems based on
knowledge graphs.

Yunpeng Hong received the bachelor’s degree from the
Anhui University, HeFei, China, in 2022. He is currently
working toward the masters degree with the School of Computer Science and Information Engineering, Hefei University
of Technology, Hefei, China. His research interests include
entity alignment and knowledge graph.

Yi Chen is a lecturer at the National University of Defense
Technology. He received his MS and PhD degrees in Optical
Engineering from the National University of Defense Technology in 2016 and 2020, respectively. His current research
interests include optical imaging, computational imaging
and computer vision.

12
PAPER_TEXT
