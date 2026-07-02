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
# [289] Relation-aware heterogeneous graph neural network for entity alignment
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
编号：289
题名：Relation-aware heterogeneous graph neural network for entity alignment
年份：2024
DOI：10.1016/j.neucom.2024.127797
来源：Neurocomputing
PDF：paper/10.1016_j.neucom.2024.127797.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：无
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\289.txt
- 原始字符数：46423
- 本次发送字符数：46423
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Neurocomputing 592 (2024) 127797

Contents lists available at ScienceDirect

Neurocomputing
journal homepage: www.elsevier.com/locate/neucom

Relation-aware heterogeneous graph neural network for entity alignment
Zirui Zhang a , Yiyu Yang a , Benhui Chen a,b ,∗
a
b

Dali University, Dali, 671000, Yunnan, China
Lijiang Normal College, Lijiang, 674100, Yunnan, China

ARTICLE

INFO

Communicated by G. Fenza
Keywords:
Entity alignment
Knowledge graph
Heterogeneous graph neural network
Relation awareness
Iterative fusion

ABSTRACT
Entity alignment refers to finding equivalent entities from different knowledge graphs. Most of the existing
entity alignment methods are studied based on homogeneous graphs. However, the knowledge graph is a
heterogeneous graph containing many types of nodes, such as entities, relations, and attributes. Therefore,
we propose introducing a heterogeneous graph neural network to model entities and relations simultaneously
and propose an iterative fusion method to enhance the interaction between these two semantic nodes. Since
not all datasets contain relation information, this paper does not directly introduce a feature representation
of relations. The generalizability of the approach is improved by utilizing a relation-aware strategy to obtain
information about the relation. Specifically, the information propagation of the head and tail entities in the
triplet is utilized to obtain the feature representation of the relation. Experimental results show that the present
method performs better on three cross-lingual datasets 𝐷𝐵𝑃 15𝐾 and two large-scale datasets 𝐷𝑊 𝑌 100𝐾.

1. Introduction
In recent years, knowledge graph (KG) has become a very hot research direction, and research results related to knowledge graph have
been launched continuously [1–3]. Entity alignment, as an essential
step in knowledge graph construction and fusion, aims to determine
whether two entities from different knowledge graphs are equivalent.
More specifically, it is to judge whether these two entities point to
the same object in the real world. The accuracy and completeness of
the entity alignment results will directly affect the final constructed
knowledge graph’s quality and indirectly determine the downstream
tasks’ performance. This also indicates that the link of entity alignment
is crucial. Entities can be aligned mainly based on the assumption that
entities adjacent to an aligned entity may also be aligned. As shown in
Fig. 1, new aligned entities can be inferred in the knowledge graph if
a portion of the aligned entities is known in advance.
There are two main types of traditional entity alignment methods: one is based on probabilistic models [4–6], and the other is
based on machine learning [7,8]. However, with the increasing size
of knowledge graphs, traditional entity alignment methods can no
longer effectively align entities in different knowledge graphs and are
thus gradually no longer used. As representation learning techniques
begin to be widely used in knowledge graphs, some researchers have
begun to apply representation learning to the entity alignment task and
have performed well. Entity alignment methods using representation
learning to obtain entity embeddings [9] have become mainstream.

Currently, embedding-based models are broadly classified into two
categories: one is based on TransE [10–13]. This approach interprets
the relations in a relation triplet as translation vectors from head
entity to tail entity, and the low-dimensional embedding vector space
reflects the semantic information of the entities. Another category
is GNN-based models [14,15]. This approach treats the knowledge
graph entities as nodes and relations as edges. It uses the edges to
propagate information to obtain more expressive embeddings by fusing
the entity’s neighborhood information into the entity embeddings. One
problem with this approach is that relations are used only as edges, ignoring the rich information in them. This may lead to poor performance
on entity alignment with similar structures.
The two entities in Fig. 2 have the same structure, and the two central entities, ‘‘China’’ and ‘‘Beijing’’, are aligned based on the structure
information alone. However, in reality, the two entities are entirely
different, which is the disadvantage of relying solely on structural
information. In order to solve this problem, this paper adds relation
information to the entity alignment task, and the entity alignment
after considering the relation is shown in Fig. 3. After considering
the relation information, although the two entities have the same surrounding structure, they do not have the same relation with the same
neighboring entities. Therefore, it can be judged that the probability
of these two entities not matching is relatively high, thus successfully
avoiding mismatching.
This paper proposes an entity alignment method based on relationaware heterogeneous graph neural networks to address the above

∗ Corresponding author.

E-mail addresses: zzr@stu.dali.edu.cn (Z. Zhang), yangyiyu@dali.edu.cn (Y. Yang), bhchen@dali.edu.cn (B. Chen).
https://doi.org/10.1016/j.neucom.2024.127797
Received 14 January 2024; Received in revised form 24 April 2024; Accepted 27 April 2024
Available online 6 May 2024
0925-2312/© 2024 Elsevier B.V. All rights reserved.

Neurocomputing 592 (2024) 127797

Z. Zhang et al.

2. Related work
Early approaches to entity alignment relied heavily on manual
annotation with crowdsourcing techniques [17,18]. With the continuous development of the knowledge graph scale, manual annotation
will consume a lot of time and human resources. Most existing entity
alignment methods are based on embedding, and TransE [10] is one
of the main techniques for entity embedding. MTransE proposed by
Chen et al. [19] first embeds each knowledge graph into a separate
low-dimensional vector space and then constructs transitions between
different vector spaces. TransE can only model single-hop relations
between entities and cannot handle complex multi-hop relations, thus
losing important information. Therefore, Zhu et al. [20] proposed
PTransE to embed entities and relations from different knowledge
graphs into the joint semantic space based on the seed set. Instead of
TransE, PTransE [21] is used to model multi-step relations. At the same
time, high-confidence predicted aligned entities are filtered and added
to the seed set to guide the subsequent entity alignment training. A
truncated uniform negative sampling approach is designed in BootEA,
proposed by Sun et al. [22]. From the original random selection of
entities from all entities to replace the head or tail entity, it is changed
to selecting one of several entities with the closest cosine distance to
the head or tail entity. In addition, BootEA uses an iterative alignment
method similar to IPTransE. However, BootEA can edit new entity pairs
to reduce error propagation.
Graph Convolutional Networks (GCN) [23–25] is another major
technique for KG embedding that has made significant progress in
recent years. Wang et al. [26] proposed GCN-Align, which for the first
time, uses a GCN model for the entity alignment task. The structural
and entity attributes of the knowledge graph are embedded by two
GCN models stacked in two layers, respectively. However, GCN can
aggregate the neighbors’ information around an entity well but ignores
the relation information. RDGCN, proposed by Wu et al. [27] is a bigraph convolutional structure constructing a dyadic graph for each
knowledge graph. By alternating convolution operations on the original
graph and the dyadic graph, the relation information in the knowledge
graph is fully utilized to enhance the entity representation. The graph
attention mechanism is applied in RDGCN, and the MuGNN proposed
by Cao et al. [28] also applies the graph attention network. The
knowledge graph is first complemented using rule knowledge, reducing
heterogeneity between the two knowledge graphs. Then, two adjacency
matrices are generated based on the self-attention and cross-graph
attention channels and input into the GNN for embedding entities.
Finally, a pooling function aggregates the two representations for entity alignment. Wu et al. [29] proposed a cross-graph neighborhood
matching network NMN, which samples the entity neighbors to obtain
the most informative neighbors. Their attention weights are computed
based on the neighbor representation. Then, cross-graph matching
vectors containing information about the entity and neighbor-matching
information are generated for entity alignment. Most GNN-based approaches learn the embeddings of different KGs separately and ignore
the useful pre-aligned links between two KGs. Xie et al. [30] proposed a
new context-aligned augmented cross-graph attentional network CAECGAT for cross-lingual entity alignment tasks. This network can colearn embeddings in different KGs by propagating cross-KG information
through pre-aligned seed alignment. Also, Xie et al. [31] proposed
DuGa-DIT, a dual-gated graph attention network with dynamic iterative
training. Neighborhood and cross-KG alignment features are captured
using intra-KG attention layers and cross-KG attention layers, and more
cross-KG information is captured through a dynamic iterative process.
Recently, the emergence of several new approaches has led to significant progress in entity alignment. Wang et al. [32] proposed PEAMA,
which utilizes multi-information aggregated persona entities for entity
alignment. Huang et al. [33] proposed a new framework, RpAlign,
which enables entity alignment between different KGs by predicting the
relation of the entities. Lu et al. [34] presented a multi-neighborhood

Fig. 1. Example of alignment of two heterogeneous KGs(Circles of the same color
indicate priority alignment.).

Fig. 2. An incorrect entity alignment.

Fig. 3. Consider entity alignment of relations.

problems. The basic idea of this method is to model both entities
and relations simultaneously by introducing a heterogeneous graph
neural network. An iterative fusion method is also utilized to obtain
a better entity representation. A concise version of this work has been
successfully published in the IJCNN conference. See [16] for details.
This paper increases the generalizability of the approach compared to
the work at that time. Since not all datasets contain information about
relations, this paper does not directly introduce a feature representation
of relations. Instead, a relation-aware strategy is used to obtain the relations information, and the performance is slightly improved from the
experimental results. Meanwhile, this paper also verifies the method’s
effectiveness from different angles through many experiments.
The contributions of this paper can be summarized as follows:
(i) A relation-aware strategy is introduced to perceive the characteristic representation of a relation through entity information.
(ii) An iterative fusion method is proposed by which the interaction
between entities and relations can be better enhanced.
(iii) The performance of the present model is shown to outperform the baseline model through extensive experiments on five public
datasets.
2

Neurocomputing 592 (2024) 127797

Z. Zhang et al.

sampling matching network MSM to address the challenge of structural heterogeneity through a new KG comparison network. Zhang
et al. [35] proposed a neighboring entity filtering rule based on entity
names and attributes for cross-language entity alignment. Using birelational graphs as supporting evidence in case of insufficient attribute
information effectively promotes the close connection between entities. Li et al. [36] proposed a generative adversarial entity alignment
method with stronger robustness to noisy data. An unsupervised entity
alignment algorithm can automatically align entities without training
labels. Chen et al. [37] proposed a locally inflated higher-order graph
neural network HOLI-GNN for entity alignment. The effect of excessive
smoothing due to neighborhood aggregation is mitigated by introducing a local expansion mechanism to amplify each feature of an entity.
Li et al. [38] proposed a new joint unsupervised relation alignment
model URAEA based on GCN for entity alignment. The model first
adopts a novel approach to computing relation embeddings using entity
embeddings, and then constructs unsupervised seeded relation alignments from these relation embeddings. Finally, entity alignment and
relation alignment are performed together. Yang et al. [39] designed
a novel entity-aligned relation mapping RMHN based on higher-order
graph convolutional networks. By designing a novel higher-order GCN
to aggregate higher-order information to obtain entity embeddings in
bulk.
Most of the existing methods for the entity alignment task are based
on homogeneous graphs for research. However, the actual knowledge
graph is heterogeneous, and current approaches lack the study of
heterogeneous graph neural networks. Therefore, we hope that a better
representation of entity alignment tasks can be obtained by applying
heterogeneous graph neural networks.

3.1.2. Relation nodes
To improve the generality of the method, this paper does not
directly introduce the feature representation of the relation. Instead, it
is obtained using the feature transformation of the relation’s head entity
and tail entity. Specifically, the relation embedding with weights is
computed by applying a linear transformation to the entity embeddings
and then calculating the relation embedding with weights. For relation
𝒓𝑘 , the feature representation of the head entity 𝒓ℎ𝑘 is computed as
follows:
(
( [
]))
exp LeakReLU 𝒂𝑇 𝒙𝑖 𝑾 ℎ ||𝒙𝑗 𝑾 𝑡
𝑘
𝛼𝑖𝑗 = ∑
(2)
(
( [
]))
∑
𝑇 𝒙 ′ 𝑾 ℎ ||𝒙 ′ 𝑾 𝑡
𝑖
𝑗
𝑒 ′ ∈𝑟
𝑒 ′ ∈ 𝑟𝑘 exp LeakReLU 𝒂
𝑖

𝑘

𝑗

𝑒

⎛ ∑
⎞
∑
𝒓ℎ𝑘 = ReLU ⎜
𝛼𝑖𝑗𝑘 𝒙𝑖 𝑾 ℎ ⎟
⎜𝑒 ∈
⎟
⎝ 𝑖 𝑟𝑘 𝑒𝑗 ∈𝑒𝑖 𝑟𝑘
⎠

(3)

𝛼𝑖𝑗𝑘 represents the weight representation of the head entity 𝑒𝑖 of
relation 𝒓𝑘 in the triplet, and 𝑟𝑘 is the set of head entities of relation
𝒓𝑘 in the triplet. 𝑒𝑖 𝑟𝑘 is the set of tail entities with head entity 𝑒𝑖 and
relation 𝒓𝑘 . 𝒂 is a one-dimensional vector mapping a two-dimensional
input to a scalar. 𝑾 ℎ and 𝑾 𝑡 are the linear transfer matrices for
the relation’s head entity representation and tail entity representation,
respectively.
By a similar process, one can compute the representation 𝒓𝑡𝑘 of the
tail entities and then add them to obtain the relation representation 𝒓𝑘 :
⎛ ∑
⎞
∑
𝑘
𝒓𝑡𝑘 = ReLU ⎜
𝛼𝑗𝑖
𝒙𝑗 𝑾 𝑡 ⎟
⎜
⎟
⎝𝑒𝑗 ∈𝑟𝑘 𝑒𝑖 ∈𝑟𝑘 𝑒𝑗
⎠

(4)

𝒓𝑘 = 𝒓ℎ𝑘 + 𝒓𝑡𝑘

(5)

3. Methodology
3.2. Heterogeneous graph iterative process
In this section, the general framework of the entity alignment
method based on relation-aware heterogeneous graph neural networks
is presented in detail, and the model framework is shown in Fig. 4. It
consists of three main parts:

In this section, the construction process and iterative fusion process
of heterogeneous graphs are described in detail.
3.2.1. Initial construction of the heterogeneous graph
Two types of semantic node representations are given: entity nodes
and relation nodes 𝑅 = {𝐫𝑗 }𝑀
, where 𝑁 represents the
𝐸 = {𝐞𝑖 }𝑁
𝑖=1
𝑗=1
number of entities, and 𝑀 represents the number of relations. The
initial construction of the heterogeneous graph 𝐺 is shown below:

∙ Node Encoding Process. Given entity names and descriptions,
the entity names or descriptions are encoded as vectors by the
pre-trained model BERT.1 The feature representation of the relation is also perceived through the entity information using the
relation-aware strategy.
∙ Heterogeneous Graph Iterative Process. An iterative fusion
method is proposed to enhance the interaction of entity and
relation nodes in heterogeneous graph neural networks.
∙ Entity Alignment Process. After obtaining the representation of
entity nodes and relation nodes, a specific entity alignment step
is performed by a distance function.

3.2.2. Nodes updating with iterative fusion
When the initial construction of the heterogeneous graph is completed, the relation nodes and entity nodes are updated and iteratively
fused. As shown in Fig. 5, the relation nodes aggregate all the entity
information directly adjacent to them. The updated relation node representation is used to update the entity nodes. Thus, iterative updates
make the node representation more suitable for the entity alignment
task.
Graph Attention Network (GAT) is used to complete the updating
of nodes for better semantic fusion between entity nodes and relation
nodes. In this paper, we give the updating process of relation and entity
nodes in the 𝑙th layer of the iterative process. The updating process of
relation nodes in the 𝑙th layer can be represented as:
( { }
)
𝐫̃ 𝑗𝑙+1 = 𝐆𝐀𝐓 𝐫𝑗𝑙 , 𝐞𝑙𝑖 𝑖∈
(7)

3.1. Node encoding process
In this paper, two types of semantic nodes are constructed for the
proposed heterogeneous graph: entity nodes and relation nodes.
3.1.1. Entity nodes
For entity node 𝑒, this paper encodes the entity name/description
using the BERT pre-training model. The CLS embedding of BERT is
then filtered by a multilayer perceptron to obtain the initial entity
representation 𝐶(𝑒):
𝐶(𝑒) = MLP(CLS(𝑒))

𝑗

𝐫𝑗𝑙+1 = 𝐫̃ 𝑗𝑙+1 ⊕ 𝐫𝑗𝑙

(1)

(8)

When the relation node update is completed, the updated relation
node is used to update the entity node. The process of entity node
update in layer 𝑙 can be represented as:
( {
)
}
𝑙
𝑙+1
𝐞̃ 𝑙+1
=
𝐆𝐀𝐓
𝐞
,
𝐫
(9)
𝑖
𝑖
𝑗

where CLS is the overall entity semantic representation vector of the
BERT output, and MLP is the multilayer perception.

1

(6)

𝐺 = (𝐸, 𝑅)

https://github.com/google-research/bert

𝑗∈𝑖

3

Neurocomputing 592 (2024) 127797

Z. Zhang et al.

Fig. 4. Overview framework of the model. The circles in the heterogeneity diagram represent relation-type nodes, and the squares represent entity-type nodes. The entity type
nodes in red in the entity alignment process are the potentially matching entity pairs we want to find.

4

Neurocomputing 592 (2024) 127797

Z. Zhang et al.

Algorithm 1: Encoding, iteration and training processes for
heterogeneous graphs
Input: Source Knowledge Graph 𝐾𝐺1 and Target Knowledge
Graph 𝐾𝐺2
Output: Entity embedding 𝐻𝑒′ and relation embedding 𝐻𝑟′
1 Initialization:
2 for 𝐾𝐺 = (𝐸ℎ , 𝑅, 𝐸𝑡 ) in 𝐾𝐺1 , 𝐾𝐺2 do
3
𝐻𝑒 ← 𝑀𝐿𝑃 (𝐵𝐸𝑅𝑇 (𝐸ℎ , 𝐸𝑡 )) // Entity node encoding
4
𝐻𝑟 ← 𝐸𝑚𝑏𝑒𝑑𝑑𝑖𝑛𝑔(𝑅) // Relation node encoding
5 end
6 Construction of heterogeneous graphs 𝐺1 and 𝐺2 for 𝐾𝐺1 and
𝐾𝐺2 respectively
7 Training:
8 for epo in range(epoch) do
9
Iterative fusion of entity and relation:
10
Compute 𝐻𝑟′ ← 𝑓 (𝐻𝑒 , 𝐻𝑟 ) // Update relation nodes
11
𝐻𝑟′ ← 𝐻𝑟 ∪ 𝐻𝑟′
12
Compute 𝐻𝑒′ ← 𝑓 (𝐻𝑒 , 𝐻𝑟′ ) // Update entity nodes
13
𝐻𝑒′ ← 𝐻𝑒 ∪ 𝐻𝑒′
14
Calculate the loss:
15
Evaluate the loss function 𝑙𝑜𝑠𝑠𝑁 by Eq. (15)

Fig. 5. Example of a one-round iterative fusion process.

𝐞𝑙+1
= 𝐞̃ 𝑙+1
⊕ 𝐞𝑙𝑖
𝑖
𝑖

(10)

In the updating process, this paper uses a graph attention network
to update the representation of nodes. Take the entity node update as
an example. Its specific update process is shown as follows:
[
]
𝑐𝑖𝑗 = 𝑊𝑐 𝑊𝑞 𝐞𝑖 ⊕ 𝑊𝑘 𝐫𝑗
(11)
( )
exp 𝑐𝑖𝑗
𝛼𝑖𝑗 = ∑
( )
𝑙∈𝑖 exp 𝑐𝑖𝑙
∑
𝐞̃ 𝑖 = 𝐞𝑖 +
𝛼𝑖𝑗 𝑊𝑟 𝐫𝑗

// Calculating node encoding loss
16

(12)

Evaluate the loss function 𝑙𝑜𝑠𝑠𝐴 by Eq. (16)

// Calculating entity alignment loss
𝐿 ← 𝑙𝑜𝑠𝑠𝑁 + 𝑙𝑜𝑠𝑠𝐴
18
L.backward() // Perform backpropagation
19 end
′
′
20 return 𝐻 and 𝐻
𝑒
𝑟
17

(13)

𝑗∈𝑖

where ⊕ denotes the splicing between two vectors. 𝑊𝑐 , 𝑊𝑞 , 𝑊𝑘 and 𝑊𝑟
are trainable weight parameters. 𝛼𝑖𝑗 is the attention weight coefficient
between 𝐞𝑖 ∈ R𝑑ℎ and 𝐫𝑗 ∈ R𝑑ℎ . 𝐞̃ 𝑖 is the updated entity node
representation.

iterative fusion. 𝑇 ′ represents the set of negative sample triples of 𝑇 .
𝛾1 > 0 is the edge hyperparameter separating positive and negative
triples. 𝑇 ′ is generated by destroying 𝑇 . For example, for a triplet
(𝑒ℎ , 𝑟, 𝑒𝑡 ) ∈ 𝑇 , a negative triplet (𝑒′ℎ , 𝑟, 𝑒𝑡 ) is generated by replacing 𝑒ℎ ,
where 𝑒′ℎ also has the same relation type 𝑟 connected to 𝑒𝑡 , and the same
substitution process for 𝑒𝑡 .

3.3. Entity alignment process
The distance between two entities is measured as a criterion for
entity alignment, using the final entity representation 𝑋 collected from
the output of the heterogeneous graph neural network. Specifically, the
distance 𝑑(𝑒1 , 𝑒2 ) between two entities 𝑒1 ∈ 𝐺1 and 𝑒2 ∈ 𝐺2 can be
calculated as:
(
) ‖
‖
𝑑 𝑒1 , 𝑒2 = ‖𝑥𝑒1 − 𝑥𝑒2 ‖
(14)
‖
‖2
where ‖𝑥𝑒1 − 𝑥𝑒2 ‖2 is the 𝐿2 distance between the aligned entity pairs
(𝑒1 , 𝑒2 ).

3.4.2. Entity alignment loss
For entity alignment loss, the training objective of the model is
to minimize the representation distance of equivalent entities on all
marker alignments, similar to [40]:
(
)]
∑
∑ [
(
)
𝑙𝑜𝑠𝑠𝑎𝑙𝑖𝑔𝑛 =
dist 𝑒𝑖 , 𝑒𝑗 + 𝛾2 − dist 𝑒′𝑖 , 𝑒′𝑗
(16)
(
)
(
)
𝑒𝑖 ,𝑒𝑗 ∈𝑆 𝑒′ ,𝑒′ ∈𝑆 ′

3.4. Training

+

𝑖 𝑗

where 𝑑𝑖𝑠𝑡(𝑒𝑖 , 𝑒𝑗 ) = ‖𝑒𝑖 − 𝑒𝑗 ‖2 is the 𝐿2 distance between aligned entity
pairs (𝑒𝑖 , 𝑒𝑗 ). 𝑒𝑖 and 𝑒𝑗 are the final entity representations after iterative
fusion. 𝑆 ′ denotes the set of negative pairs of 𝑆 generated by nearest
neighbor sampling. The 𝛾2 > 0 is the edge hyperparameter. Because
of the excellent performance of 𝐿2 distance in experiments, this paper
uses 𝐿2 distance as a metric to search for the nearest negative samples.

In this section, the loss function of the model and the overall
training process will be defined. The detailed encoding, iteration, and
training process are shown in Algorithm 1. The model’s loss function
consists of two components, the node encoding loss 𝑙𝑜𝑠𝑠𝑛𝑜𝑑𝑒 and the
entity alignment loss 𝑙𝑜𝑠𝑠𝑎𝑙𝑖𝑔𝑛 , each of which is described in detail
below.
3.4.1. Node encoding loss
With the help of TransE [10], given a relation triple (𝑒ℎ , 𝑟, 𝑒𝑡 ), one
wants to make 𝑒ℎ + 𝑟 ≈ 𝑒𝑡 . Thus a scoring function 𝑓 (𝑒ℎ , 𝑟, 𝑒𝑡 ) = ‖𝑒ℎ +
𝑟 − 𝑒𝑡 ‖2 is defined to measure the plausibility of (𝑒ℎ , 𝑟, 𝑒𝑡 ), where ‖ ⋅ ‖2
denotes the 2-parametric number. After TransE, an edge-based ranking
loss function is used as the training target of the model, defined as:
∑
∑
[ (
)
(
)]
𝑙𝑜𝑠𝑠𝑛𝑜𝑑𝑒 =
𝑓 𝑒ℎ , 𝑟, 𝑒𝑡 + 𝛾1 − 𝑓 𝑒′ℎ , 𝑟′ , 𝑒′𝑡 +
(15)
(
)
(𝑒ℎ ,𝑟,𝑒𝑡 )∈𝑇 𝑒′ ,𝑟′ ,𝑒′𝑡 ∈𝑇 ′

3.4.3. Joint loss
The loss function of this model consists of two parts: the node
encoding loss 𝑙𝑜𝑠𝑠𝑛𝑜𝑑𝑒 and the entity alignment loss 𝑙𝑜𝑠𝑠𝑎𝑙𝑖𝑔𝑛 . The overall
loss function 𝑙𝑜𝑠𝑠 is calculated as follows:
𝑙𝑜𝑠𝑠 = 𝑙𝑜𝑠𝑠𝑛𝑜𝑑𝑒 + 𝑙𝑜𝑠𝑠𝑎𝑙𝑖𝑔𝑛

(17)

It is worth noting that different weights can be set for the node
encoding loss 𝑙𝑜𝑠𝑠𝑛𝑜𝑑𝑒 and entity alignment loss 𝑙𝑜𝑠𝑠𝑎𝑙𝑖𝑔𝑛 to achieve
balanced optimization. In this paper, considering that these two components are equally important, we set the same weight for them to treat
both components equally in our experiments.

ℎ

where [⋅]+ = 𝑚𝑎𝑥{0, ⋅} denotes the maximum value between 0 and
the input. Entities 𝑒ℎ and 𝑒𝑡 are the final entity representations after
iterative fusion. Relation 𝑟 is the final relation representation after
5

Neurocomputing 592 (2024) 127797

Z. Zhang et al.
Table 1
𝐷𝐵𝑃 15𝐾 and 𝐷𝑊 𝑌 100𝐾 statistical information.
Datasets

𝐷𝐵𝑃 15𝐾

Entities

Relations

Triplets

𝐷𝐵𝑃 15𝐾𝑍𝐻−𝐸𝑁

Chinese
English

66,469
98,125

2,830
2,317

153,929
237,674

𝐷𝐵𝑃 15𝐾𝐽 𝐴−𝐸𝑁

Japanese
English

65,744
95,680

2,043
2,096

164,373
233,319

𝐷𝐵𝑃 15𝐾𝐹 𝑅−𝐸𝑁

French
English

66,858
105,889

1,379
2,209

192,191
278,590

𝐷𝑊 𝑌 100𝐾𝑊 𝐷

DBpedia
Wikidata

100,000
100,000

330
220

463,294
448,774

𝐷𝑊 𝑌 100𝐾𝑌 𝐺

DBpedia
YAGO3

100,000
100,000

302
31

428,952
502,563

𝐷𝑊 𝑌 100𝐾

Table 4 reports the experimental results of the model on the largescale dataset 𝐷𝑊 𝑌 100𝐾. The experimental results show that the present
model performs better on the large-scale dataset. The present model
produces better results for cross-linguistic and large-scale data, combining the experimental results in Tables 2 and 4.
To evaluate the efficiency of this model, this paper compares the
prediction time with a good baseline model on the 𝐷𝐵𝑃 15𝐾𝐹 𝑅−𝐸𝑁
dataset. From Table 5, our method produces better results in terms of
efficiency and performance.
4.4. Sensitivity to previously aligned ratios
In this paper, we validate the method’s effectiveness by comparing
it with the baseline models RDGCN [27] and KECG [40] at different
previously aligned ratios. The results show that the present method
outperforms the compared baseline models in Fig. 6. The experimental
results of the present method are slightly worse than those of RDGCN
when less training data is used. This is because introducing two types of
nodes into the present model requires a certain amount of training data
to be iteratively fused to obtain better features. However, as the amount
of data increases, the advantages of heterogeneous graphs gradually
appear, and their growth rate is faster through the iterative fusion of
entities and relations.

4. Experiment
This paper evaluates the method’s effectiveness on three crosslinguistic datasets from 𝐷𝐵𝑃 15𝐾 and two large-scale datasets from
𝐷𝑊 𝑌 100𝐾. The models are also further compared and analyzed from
different perspectives.
4.1. Dataset
The model was evaluated by using the 𝐷𝐵𝑃 15𝐾 dataset constructed
by Sun et al. [41]. The 𝐷𝐵𝑃 15𝐾 contains three large cross-linguistic
datasets constructed from DBpedia. Use 𝐷𝐵𝑃 15𝐾𝑍𝐻−𝐸𝑁 for Chinese to
English, 𝐷𝐵𝑃 15𝐾𝐽 𝐴−𝐸𝑁 for Japanese to English, and 𝐷𝐵𝑃 15𝐾𝐹 𝑅−𝐸𝑁
for French to English. Each dataset contains 15,000 entity alignment
seed pairs.
The effectiveness of the model on large-scale data was tested by
performing experiments on 𝐷𝑊 𝑌 100𝐾 created by Sun et al. [22].
𝐷𝑊 𝑌 100𝐾 contains two large-scale datasets, 𝐷𝑊 𝑌 100𝐾𝑊 𝐷 and
𝐷𝑊 𝑌 100𝐾𝑌 𝐺 , which are extracted from DBpedia, Wikidata, and
YAGO3. 𝐷𝑊 𝑌 100𝐾𝑊 𝐷 denotes DBpedia to Wikidata, and 𝐷𝑊 𝑌 100𝐾𝑌 𝐺
denotes DBpedia to YAGO3. Each dataset has 100,000 entity-aligned
seed pairs. Table 1 lists the details of each dataset.

4.5. Ablation study
This paper conducts ablation studies on the model using three crosslinguistic datasets from 𝐷𝐵𝑃 15𝐾, validating the effectiveness of the
main components in the model. The specific experimental results of the
ablation studies are shown in Table 3.
In this paper, a total of three different combinations are performed
to verify the effectiveness of BERT encoding and heterogeneous graphs.
These include the combination of one-hot encoding and heterogeneous graph neural network (one-hot+HGNN), the combination of
BERT encoding and graph convolutional neural network (BERT+GCN),
and the combination of BERT encoding and graph attention network
(BERT+GAT). The experimental results show that the essential components of this paper are effective.

4.2. Experiment settings
For all baseline methods, 30% of entity alignment seed pairs were
randomly used as training data and the rest as test data. Two evaluation
metrics are used in this task: MRR and Hits@N. MRR denotes the
average inverse rank of all correct entities, and Hits@N represents the
proportion of right entities whose rank is not greater than N. Higher
values of MRR and Hits@N indicate a better entity alignment model.
For the parameter settings, the input dimension of Bert is set to
768, and the output dimension is set to 300. The dimension of the
GAT hidden unit is set to 300. The learning rate is set to 0.005.
The experiment results shown in this paper are after 1000 rounds of
iterative fusion of entities and relations.

4.6. Visualization of attention scores
In this paper, we observe the weight parameters of the edges in GAT
by visualizing the attention mechanism used in the iterative process.
Since the adjacency matrix generated in the construction of the graph
is sparse, only a central entity and the entities directly connected
to it are randomly selected for display. In this paper, we take the
𝐷𝐵𝑃 15𝐾𝑍𝐻−𝐸𝑁 dataset as an example and select a set of ChineseEnglish entity alignment seed pairs to display, and the visualization
results are shown in Fig. 7. Since the attention coefficients are relatively
small, the visualization results are the results after the coefficients are
magnified ten times.
The attention visualization is selected from the direct first-order
neighbors of each central entity. As can be seen in Fig. 7, the attention
mechanism is beneficial for aligning two central entities. The model
produces higher weighting coefficients for the common neighbors of
the central entities and lower weighting coefficients for their unique
’’ entity in Fig. 7(a) and
neighbors. For example, the ‘‘
the ‘‘Saint Lawrence River’’ entity in Fig. 7(b) have lower weight coefficients as their unique neighbors. This effectively alleviates the model’s
sensitivity to the structural differences of KG. This example clearly
illustrates that the attention mechanism in this model can accurately
find the more relevant features in the entity pairs.

4.3. Baselines and comparison result
Table 2 reports the experimental results of the different models
on three large cross-linguistic datasets of 𝐷𝐵𝑃 15𝐾, along with the
means and standard deviation results of the methods. In this paper, the
baseline models are classified into three categories: models based on
TransE, models based on GCN, and models based on others. The results
show that the proposed method performs well on all three datasets,
which indicates that the proposed method is effective.
This paper’s present model performs better when compared with
recent work. It is worth noting that although DuGa-DIT slightly outperforms the present model in some of the results on the three datasets,
the present model significantly outperforms DuGa-DIT regarding operational efficiency. Specific experimental results are shown in Table 5.
6

Neurocomputing 592 (2024) 127797

Z. Zhang et al.

Table 2
Baseline model comparison results in dataset 𝐷𝐵𝑃 15𝐾. The method means and standard deviations are reported in this paper. ‘‘-’’ indicates not reported
in the original paper. Scores marked in bold indicate the best performance among all methods.
Method

𝐷𝐵𝑃 15𝐾

Others

GCN

TransE

𝐷𝐵𝑃 15𝐾 𝐽 𝐴−𝐸𝑁

𝐷𝐵𝑃 15𝐾 𝑍𝐻−𝐸𝑁

𝐷𝐵𝑃 15𝐾 𝐹 𝑅−𝐸𝑁

Hits@1

Hits@10

MRR

Hits@1

Hits@10

MRR

Hits@1

Hits@10

MRR

MTransE [11]
JAPE [41]
BootEA [22]

0.279
0.363
0.622

0.575
0.685
0.854

0.349
0.476
0.701

0.308
0.412
0.629

0.614
0.745
0.848

0.364
0.490
0.703

0.244
0.324
0.653

0.556
0.667
0.874

0.335
0.430
0.731

KECG [40]
AliNet [29]
RDGCN [27]
MRAEA [42]
HMAN [33]
MHGCN [43]
EVA [44]
AttrGNN [45]
SSP [46]
DuGa-DIT [31]
CAECGAT [30]
DRG+ESGCN [35]
GAEA [36]

0.490
0.549
0.767
0.757
0.557
0.767
0.762
0.783
0.721
0.914
0.836
0.807
0.846

0.844
0.831
0.895
0.933
0.860
0.891
0.913
0.921
0.935
0.952
0.956
0.933
0.925

0.610
0.645
0.812
0.826
0.674
0.821
0.817
0.834
0.800
0.928
0.881
0.853
0.846

0.478
0.539
0.708
0.757
0.562
0.732
0.761
0.796
0.739
0.807
0.756
0.757
0.774

0.835
0.826
0.846
0.929
0.851
0.867
0.907
0.929
0.925
0.882
0.934
0.907
0.875

0.598
0.628
0.746
0.827
0.670
0.793
0.814
0.845
0.808
0.832
0.818
0.811
0.813

0.486
0.552
0.886
0.780
0.550
0.864
0.793
0.918
0.739
0.982
0.947
0.970
0.914

0.851
0.852
0.957
0.948
0.876
0.923
0.942
0.977
0.947
0.992
0.992
0.973
0.957

0.610
0.657
0.911
0.849
0.666
0.898
0.847
0.910
0.818
0.985
0.965
0.927
0.902

PEAMA [32]
RpAlign [33]
MSM [34]

0.551
0.730
0.788

0.890
0.919

0.634
0.782
-

0.562
0.748
0.708

0.889
0.867

0.644
0.794
-

0.558
0.752
0.906

0.900
0.973

0.645
0.801
-

ours

0.799
±0.002

0.972
±0.005

0.864
±0.003

0.768
±0.004

0.963
±0.002

0.843
±0.004

0.939
±0.003

0.992
±0.006

0.959
±0.004

Table 3
Comparison results of ablation studies in dataset 𝐷𝐵𝑃 15𝐾.
Model

ours(BERT+HGNN)
one-hot+HGNN
BERT+GCN
BERT+GAT

𝐷𝐵𝑃 15𝐾𝐽 𝐴−𝐸𝑁

𝐷𝐵𝑃 15𝐾𝑍𝐻−𝐸𝑁

𝐷𝐵𝑃 15𝐾𝐹 𝑅−𝐸𝑁

Hits@1

Hits@10

MRR

Hits@1

Hits@10

MRR

Hits@1

Hits@10

MRR

0.799
0.761
0.577
0.677

0.972
0.921
0.912
0.937

0.864
0.821
0.698
0.769

0.768
0.694
0.581
0.652

0.963
0.889
0.914
0.931

0.843
0.766
0.702
0.751

0.939
0.768
0.685
0.949

0.992
0.951
0.943
0.992

0.959
0.839
0.781
0.966

Fig. 6. Experimental results for different alignment ratios.

As can be seen in Fig. 8(a), Fig. 8(c), and Fig. 8(e), the overall
distribution of initial entity features on the three datasets is irregular.
As can be seen in Fig. 8(b), Fig. 8(d), and Fig. 8(f), when the entity and
relation
are iteratively fused for 1000 rounds of training, the entity pairs
appear significantly aligned on all three datasets. t-SNE visualization
also indirectly proves the effectiveness of this model.

4.7. Visualization of entity features
The entity characteristics of the initial and final stages were visualized to verify the model’s validity. To see the changes in entity feature
distribution more intuitively, this paper uses the high-dimensional
data reduction algorithm t-distributed random neighbor embedding
(t-SNE) to map the feature distribution in two-dimensional space.
The entity feature distribution by applying this method is shown in
Fig. 8. Among them, Fig. 8(a), Fig. 8(c), and Fig. 8(e) show the initial
entity feature visualization results for the datasets 𝐷𝐵𝑃 15𝐾𝑍𝐻−𝐸𝑁 ,
𝐷𝐵𝑃 15𝐾𝐽 𝐴−𝐸𝑁 , and 𝐷𝐵𝑃 15𝐾𝐹 𝑅−𝐸𝑁 , respectively. Fig. 8(b), Fig. 8(d),
and Fig. 8(f) show the visualization results of entity features of datasets
𝐷𝐵𝑃 15𝐾𝑍𝐻−𝐸𝑁 ,
𝐷𝐵𝑃 15𝐾𝐽 𝐴−𝐸𝑁
and
𝐷𝐵𝑃 15𝐾𝐹 𝑅−𝐸𝑁
after
1000 rounds of entity and relation iterative fusion, respectively.

4.8. Case study
To demonstrate the effectiveness of this methodology, a case study
is presented in this section for in-depth analysis. Fig. 9 shows the results
of the case study compared to a strong baseline. The present method
7

Neurocomputing 592 (2024) 127797

Z. Zhang et al.

Fig. 7. The results of the attention visualization are plotted. The central entities ‘‘

’’ and ‘‘Maine’’ are a set of entity alignment seed pairs in the 𝐷𝐵𝑃 15𝐾𝑍𝐻−𝐸𝑁 dataset.

Table 4
Baseline model comparison results in dataset 𝐷𝑊 𝑌 100𝐾. This paper reports the means
and standard deviations of the methods. Scores marked in bold indicate the best
performance among all methods.

to add helpful information. Therefore, the components of this method
have an essential role to play.

Method

𝐷𝑊 𝑌 100𝐾

5. Conclusion

Hits@1

Hits@10

MRR

Hits@1

Hits@10

MRR

TransE

𝐷𝑊 𝑌 100𝐾 𝑌 𝐺

MTransE [11]
JAPE [41]
BootEA [22]

0.281
0.318
0.748

0.520
0.589
0.898

0.363
0.411
0.801

0.252
0.236
0.761

0.493
0.484
0.894

0.334
0.320
0.808

GCN

𝐷𝑊 𝑌 100𝐾 𝑊 𝐷

GCN-Align [26]
KECG [40]
AliNet [29]
MRAEA [42]
SSP [46]

0.506a
0.632
0.690
0.794
0.772

0.772a
0.900
0.908
0.930
0.960

0.600a
0.726
0.766
0.856
0.842

0.597a
0.728
0.786
0.819
0.811

0.838a
0.915
0.943
0.951
0.968

0.682a
0.795
0.841
0.875
0.869

RpAlign [33]

0.826

0.934

0.862

0.838

0.945

0.872

ours

0.832
±0.003

0.958
±0.003

0.873
±0.002

0.854
±0.004

0.977
±0.002

0.894
±0.003

This paper presents an entity alignment method based on relationaware heterogeneous graph neural networks. The method uses heterogeneous graph neural networks to model entities and relations
simultaneously. It uses an iterative fusion method to enhance the interaction between the two types of semantic nodes. Since not all datasets
contain information about relations, this paper does not directly introduce information about relations. The generalizability of the approach
is improved by using a relation-aware strategy to obtain relations from
entity perception. In this paper, the method’s effectiveness is evaluated
using the cross-lingual dataset 𝐷𝐵𝑃 15𝐾 and the large-scale dataset
𝐷𝑊 𝑌 100𝐾. The results show that better performance is obtained by
improving all metrics compared to the existing methods.

a

Indicates metrics not reported in the paper. The results shown in this paper are from
Li et al. [40].

Attribute information is an essential class of information in knowledge graphs, and the advantages of this method are not apparent
when the data relations are more complex. In our future work, we
will consider introducing attribute information to further improve the
method’s performance.

Table 5
Prediction times for different models
on dataset 𝐷𝐵𝑃 15𝐾𝐹 𝑅−𝐸𝑁 .
Methods

Time

GM-EHD-JEA
RDGCN
HGCN-JE
NMN
CAECGAT
DuGa-DIT
ours

1,474 s
45 s
50 s
84 s
42 s
44 s
8 s

CRediT authorship contribution statement
Zirui Zhang: Writing – original draft, Methodology, Conceptualization. Yiyu Yang: Writing – review & editing. Benhui Chen: Supervision.

The baseline modeling experimental
results shown in this paper were
provided by Xie et al [31].

Declaration of competing interest
achieves better results. We use the highest ranked entity as the alignThe authors declare that they have no known competing financial interests or personal relationships that could have appeared to
influence the work reported in this paper.

ment centre entity for model prediction, and the experimental results of
3 samples on different models are shown in Fig. 9. The present model
obtained correct alignment results in these samples, again proving the
importance of introducing relations. When the central entity has more

Data availability

neighbor nodes (as in cases 1 and 2), the relation information can
help us distinguish different entities. When the central entity has fewer
neighbor nodes (as in the 3rd case), the relation information can help us

Data will be made available on request.
8

Neurocomputing 592 (2024) 127797

Z. Zhang et al.

Fig. 8. Visual presentation of entity features in the initial and final stages.

9

Neurocomputing 592 (2024) 127797

Z. Zhang et al.

Fig. 9. Case study on the dataset 𝐷𝐵𝑃 15𝐾𝑍𝐻−𝐸𝑁 . Green entities indicate correctly aligned central entities, and red entities indicate misaligned central entities.

References

[9] Y. Hao, Y. Zhang, S. He, K. Liu, J. Zhao, A joint embedding method for entity
alignment of knowledge bases, in: Knowledge Graph and Semantic Computing:
Semantic, Knowledge, and Linked Big Data: First China Conference, CCKS 2016,
Beijing, China, September 19–22, 2016, Revised Selected Papers 1, Springer
Singapore, 2016, pp. 3–14.

[1] Z. Li, H. Liu, Z. Zhang, T. Liu, N.N. Xiong, Learning knowledge graph embedding
with heterogeneous relation attention networks, IEEE Trans. Neural Netw. Learn.
Syst. 33 (8) (2021) 3961–3973.
[2] Z. Li, H. Liu, Z. Zhang, T. Liu, J. Shu, Recalibration convolutional networks for
learning interaction knowledge graph embedding, Neurocomputing 427 (2021)
118–130.
[3] Z. Xue, Z. Zhang, H. Liu, S. Yang, S. Han, Learning knowledge graph embedding
with multi-granularity relational augmentation network, Expert Syst. Appl. 233
(2023) 120953.
[4] I.P. Fellegi, A.B. Sunter, A theory for record linkage, J. Amer. Statist. Assoc. 118
(1969) 3–1210.
[5] W.E. Winkler, Methods for Record Linkage and Bayesian Networks, Technical
Report, Statistical Research Division, US Census Bureau, Washington, DC, 2002,
pp. 2659–2665.
[6] M. Pershina, M. Yakout, K. Chakrabarti, Holistic entity matching across knowledge graphs, in: 2015 IEEE International Conference on Big Data, Big Data, IEEE,
2015, pp. 1585–1590.
[7] M. Bilenko, R.J. Mooney, Adaptive duplicate detection using learnable string
similarity measures, in: Proceedings of the Ninth ACM SIGKDD International
Conference on Knowledge Discovery and Data Mining, 2003, pp. 39–48.
[8] H. Zhao, S. Ram, Entity matching across heterogeneous data sources: An
approach based on constrained cascade generalization, Data Knowl. Eng. 66 (3)
(2008) 368–381.

[10] A. Bordes, N. Usunier, A. Garcia-Duran, J. Weston, O. Yakhnenko, Translating
embeddings for modeling multi-relational data, Adv. Neural Inf. Process. Syst.
26 (2013).
[11] Z. Wang, J. Zhang, J. Feng, Z. Chen, Knowledge graph embedding by translating
on hyperplanes, in: Proceedings of the AAAI Conference on Artificial Intelligence,
Vol. 28, No. 1, 2014.
[12] Y. Lin, Z. Liu, M. Sun, Y. Liu, X. Zhu, Learning entity and relation embeddings
for knowledge graph completion, in: Proceedings of the AAAI Conference on
Artificial Intelligence, Vol. 29, No. 1, 2015.
[13] G. Ji, S. He, L. Xu, K. Liu, J. Zhao, Knowledge graph embedding via dynamic
mapping matrix, in: Proceedings of the 53rd Annual Meeting of the Association
for Computational Linguistics and the 7th International Joint Conference on
Natural Language Processing (Volume 1: Long Papers), 2015, pp. 687–696.
[14] J. Bruna, W. Zaremba, A. Szlam, Y. LeCun, Spectral networks and locally
connected networks on graphs, 2013, arXiv preprint arXiv:1312.6203.
[15] M. Henaff, J. Bruna, Y. LeCun, Deep convolutional networks on graph-structured
data, 2015, arXiv preprint arXiv:1506.05163.
[16] Z. Zhang, F. Meng, Y. Meng, X. Liu, B. Chen, Iterative fusion method based on
heterogeneous graph neural network for entity alignment, in: 2023 International
Joint Conference on Neural Networks, IJCNN, IEEE, 2023, pp. 01–08.
10

Neurocomputing 592 (2024) 127797

Z. Zhang et al.

[35] X. Zhang, W. Zhang, H. Wang, Cross-language entity alignment based on
dual-relation graph and neighbor entity screening, Electronics 12 (5) (2023)
1211.
[36] Y. Li, L. Chen, C. Liu, R. Zhou, J. Li, Generative adversarial network for
unsupervised multi-lingual knowledge graph entity alignment, World Wide Web
26 (5) (2023) 2265–2290.
[37] J. Chen, L. Yang, Z. Wang, M. Gong, Higher-order GNN with local inflation for
entity alignment, Knowl.-Based Syst. 293 (2024) 111634.
[38] L. Feng Ying, L. Jia Peng, D. Rong Sheng, Entity alignment with fusing relation
representation, AI Commun. (2023) 1–13.
[39] L. Yang, J. Chen, Z. Wang, F. Shang, Relation mapping based on higher-order
graph convolutional network for entity alignment, Eng. Appl. Artif. Intell. 133
(2024) 108009.
[40] C. Li, Y. Cao, L. Hou, J. Shi, J. Li, T.S. Chua, Semi-Supervised Entity Alignment
Via Joint Knowledge Embedding Model and Cross-Graph Model, Association for
Computational Linguistics, 2019.
[41] Z. Sun, W. Hu, C. Li, Cross-lingual entity alignment via joint attribute-preserving
embedding, in: The Semantic Web–ISWC 2017: 16th International Semantic
Web Conference, Vienna, Austria, October 21–25, 2017, Proceedings, Part I 16,
Springer International Publishing, 2017, pp. 628–644.
[42] X. Mao, W. Wang, H. Xu, M. Lan, Y. Wu, MRAEA: an efficient and robust
entity alignment approach for cross-lingual knowledge graph, in: Proceedings
of the 13th International Conference on Web Search and Data Mining, 2020, pp.
420–428.
[43] J. Gao, X. Liu, Y. Chen, F. Xiong, MHGCN: Multiview highway graph convolutional network for cross-lingual entity alignment, Tsinghua Sci. Technol. 27 (4)
(2021) 719–728.
[44] F. Liu, M. Chen, D. Roth, N. Collier, Visual pivoting for (unsupervised) entity
alignment, in: Proceedings of the AAAI Conference on Artificial Intelligence, Vol.
35, No. 5, 2021, pp. 4257–4266.
[45] Y. Wu, X. Liu, Y. Feng, Z. Wang, D. Zhao, Jointly learning entity and relation
representations for entity alignment, 2019, arXiv preprint arXiv:1909.09317.
[46] H. Nie, X. Han, L. Sun, C.M. Wong, Q. Chen, S. Wu, W. Zhang, Global structure
and local semantics-preserved embeddings for entity alignment, in: Proceedings
of the Twenty-Ninth International Conference on International Joint Conferences
on Artificial Intelligence, 2021, pp. 3658–3664.

[17] J. Lehmann, R. Isele, M. Jakob, A. Jentzsch, D. Kontokostas, P.N. Mendes, et al.,
Dbpedia–a large-scale, multilingual knowledge base extracted from wikipedia,
Semant. Web 6 (2) (2015) 167–195.
[18] F. Mahdisoltani, J. Biega, F.M. Suchanek, Yago3: A knowledge base from
multilingual wikipedias, in: CIDR, 2013.
[19] M. Chen, Y. Tian, M. Yang, C. Zaniolo, Multilingual knowledge graph embeddings
for cross-lingual knowledge alignment, 2016, arXiv preprint arXiv:1611.03954.
[20] H. Zhu, R. Xie, Z. Liu, M. Sun, Iterative entity alignment via joint knowledge
embeddings, in: IJCAI, Vol. 17, 2017, pp. 4258–4264.
[21] Y. Lin, Z. Liu, H. Luan, M. Sun, S. Rao, S. Liu, Modeling relation paths for
representation learning of knowledge bases, 2015, arXiv preprint arXiv:1506.
00379.
[22] Z. Sun, W. Hu, Q. Zhang, Y. Qu, Bootstrapping entity alignment with knowledge
graph embedding, in: IJCAI, Vol. 18, No. 2018, 2018.
[23] H. Liu, C. Zheng, D. Li, Z. Zhang, K. Lin, X. Shen, et al., Multi-perspective social
recommendation method with graph representation learning, Neurocomputing
468 (2022) 469–481.
[24] H. Liu, C. Zheng, D. Li, X. Shen, K. Lin, J. Wang, et al., EDMF: Efficient deep
matrix factorization with review feature learning for industrial recommender
system, IEEE Trans. Ind. Inform. 18 (7) (2021) 4361–4371.
[25] H. Liu, T. Liu, Z. Zhang, A.K. Sangaiah, B. Yang, Y. Li, Arhpe: Asymmetric
relation-aware representation learning for head pose estimation in industrial human–computer interaction, IEEE Trans. Ind. Inform. 18 (10) (2022)
7107–7117.
[26] Z. Wang, Q. Lv, X. Lan, Y. Zhang, Cross-lingual knowledge graph alignment
via graph convolutional networks, in: Proceedings of the 2018 Conference on
Empirical Methods in Natural Language Processing, 2018, pp. 349–357.
[27] Y. Wu, X. Liu, Y. Feng, Z. Wang, R. Yan, D. Zhao, Relation-aware entity
alignment for heterogeneous knowledge graphs, 2019, arXiv preprint arXiv:
1908.08210.
[28] Y. Cao, Z. Liu, C. Li, J. Li, T.S. Chua, Multi-channel graph neural network for
entity alignment, 2019, arXiv preprint arXiv:1908.09898.
[29] Y. Wu, X. Liu, Y. Feng, Z. Wang, D. Zhao, Neighborhood matching network for
entity alignment, 2020, arXiv preprint arXiv:2005.05607.
[30] Z. Xie, R. Zhu, K. Zhao, J. Liu, G. Zhou, X. Huang, A contextual alignment
enhanced cross graph attention network for cross-lingual entity alignment, in:
Proceedings of the 28th International Conference on Computational Linguistics,
2020, pp. 5918–5928.
[31] Z. Xie, R. Zhu, K. Zhao, J. Liu, G. Zhou, J.X. Huang, Dual gated graph attention
networks with dynamic iterative training for cross-lingual entity alignment, ACM
Trans. Inf. Syst. 40 (3) (2021) 1–30.
[32] H. Wang, R. Huang, J. Zhang, Person entity alignment method based on
multimodal information aggregation, Electronics 11 (19) (2022) 3163.
[33] H. Huang, C. Li, X. Peng, L. He, S. Guo, H. Peng, et al., Cross-knowledge-graph
entity alignment via relation prediction, Knowl.-Based Syst. 240 (2022) 107813.
[34] D. Lu, Y. Sun, Q. Dai, X. Li, D. Zhu, H. Du, et al., MSM: A method of
multi-neighborhood sampling matching for entity alignment, Intell. Autom. Soft
Comput. 32 (2) (2022) 1141–1151.

Zirui Zhang is a graduate student at Dali University. Contact him at zzr@stu.dali.edu.
cn.

Yiyu Yang is a researcher at Dali University. Contact him at yangyiyu@dali.edu.cn.

Benhui Chen is a professor at Dali University. Contact him at bhchen@dali.edu.cn.

11
PAPER_TEXT
