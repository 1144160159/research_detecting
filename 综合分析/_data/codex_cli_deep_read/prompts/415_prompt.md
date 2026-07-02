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
# [415] End-to-End Abnormal Subgraph Detection via Subgraph-Level Contrastive Learning
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
编号：415
题名：End-to-End Abnormal Subgraph Detection via Subgraph-Level Contrastive Learning
年份：2025
DOI：10.1109/tnnls.2025.3573922
来源：IEEE Transactions on Neural Networks and Learning Systems
PDF：paper/10.1109_TNNLS.2025.3573922.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测、图学习、知识图谱与威胁情报
相关性：弱相关，分数 1
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\415.txt
- 原始字符数：80528
- 本次发送字符数：80528
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
18312

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

End-to-End Abnormal Subgraph Detection via
Subgraph-Level Contrastive Learning
Zhen Peng , Yunfan Wang , Qika Lin , Member, IEEE, Bin Shi , Chen Chen ,
Bo Dong , Member, IEEE, and Chao Shen

Abstract—Abnormal subgraph (AS) detection plays a significant role in ensuring the security of many high-impact domains.
Unlike node anomaly detection, identifying subgraph anomalies
is extremely challenging due to the exponentially large subgraph
space caused by various combinations of nodes and edges. Moreover, in the absence of supervisory signals, how to quantify the
abnormality of subgraphs poses another pressing challenge. Traditional methods typically rely on handcrafted subgraph anomaly
measures, making it hard to handle potential unknown anomalies with limited prior knowledge. Recent deep learning-based
techniques are predominantly designed to discover individual
node anomalies, which could be suboptimal for AS detection due
to the inconsideration of collaborative behaviors between nodes
in the subgraph. In fact, existing studies have put very little
effort into this task, and even dedicated performance evaluation
metrics are not yet available. To address the above challenges
and promote related research, in this article, we propose a
end-to-end unsupervised subgraph anomaly detection framework
(EndSubG), which jointly models subgraph partition and AS
detection as a whole instead of treating them as two separate
stages. Specifically, E ND S UB G uncovers potential AS boundaries
that violate the Homophily assumption by modeling the edge existence probability, then achieves anomaly-aware graph embedding
and subgraph partition based on the refined topology. By forming
a coarsened subgraph network, E ND S UB G picks out subgraph
anomalies by learning the “subgraph-vicinity” matching patterns.
Additionally, we design an evaluation metric weighted normalized
mutual information centered on AS (AS-WNMI) specifically
Received 20 May 2024; revised 16 February 2025 and 3 May 2025;
accepted 22 May 2025. Date of publication 5 June 2025; date of current version 9 October 2025. This work was supported in part by the
National Key Research and Development Program of China under Grant
2021ZD0110700; in part by the National Natural Science Foundation of China
under Grant 62302380, Grant 62476215, Grant 62250009, Grant 62037001,
Grant U24B20185, Grant T2442014, Grant 62161160337, Grant 62132011,
and Grant U21B2018; in part by the Key Research and Development Program
of Shaanxi Province under Grant 2022GXLH01-03, Grant 2023-ZDLGY38, and Grant 2021ZDLGY01-02; in part by China Post-Doctoral Science
Foundation under Grant 2023M742789; and in part by Shaanxi Continuing
Higher Education Teaching Reform Research Project under Grant 21XJZ014.
(Corresponding author: Bin Shi.)
Zhen Peng and Bin Shi are with the School of Computer Science and
Technology, Xi’an Jiaotong University, Xi’an 710049, China (e-mail: zhenpeng27@outlook.com; shibin@xjtu.edu.cn).
Yunfan Wang and Chen Chen are with the Department of Computer
Science, University of Virginia, Charlottesville, VA 22904 USA (e-mail:
abe6fq@virginia.edu; zrh6du@virginia.edu).
Qika Lin is with the Saw Swee Hock School of Public Health,
National University of Singapore, Singapore 117549 (e-mail:
linqika@nus.edu.sg).
Bo Dong is with the School of Distance Education, Xi’an Jiaotong
University, Xi’an 710049, China (e-mail: dong.bo@xjtu.edu.cn).
Chao Shen is with the School of Cyber Science and Engineering, Xi’an
Jiaotong University, Xi’an 710049, China (e-mail: chaoshen@xjtu.edu.cn).
Digital Object Identifier 10.1109/TNNLS.2025.3573922

for subgraph anomaly detection, which is a variant of vanilla
NMI and quantifies detection performance from both subgraph
partition and anomaly recognition. The experimental results on
synthetic and real-world datasets corroborate the superiority of
end-to-end unsupervised subgraph anomaly detection framework
(EndSubG) in terms of area under the curve (AUC), average
precision (AP), and AS-WNMI. We also provide an intuitive
analysis of the detected subgraphs through visualization for
better understanding.
Index Terms—Anomaly-aware graph embedding, contrastive
learning, graph neural networks, subgraph anomaly detection.

I. I NTRODUCTION
RAPH-STRUCTURED data is ubiquitous and has
proved to be a powerful tool to model and analyze
various modern information networks, such as social networks,
transaction networks, and biological networks. To prevent
unpredictable hazards, graph anomaly detection has been
widely used to help regulators proactively uncover suspicious
objects. In addition to the well-known abnormal objects that
exist in the form of individuals, such as a rumor spreader in
social media, some anomalies may exhibit collective behavior
in reality, such as multiple fraudsters colluding with each other
to garner benefits [1]. These anomalies and their interactions
typically form subgraph structures. Effectively mining those
unusual subgraphs in networks is of great significance to many
high-impact domains [2], [3], [4]. For instance, as shown in
Fig. 1, locating corporate groups that issue false and fictitious
VAT invoices will help maintain a healthy and fair business
environment. In a health surveillance network, the Centers for
Disease Control and Prevention (CDC) staff have an interest
in locating a collective of infected patients with significant
abnormal symptoms, which may reveal a potential disease
outbreak like COVID-19.
The superior performance of deep neural nets, especially
graph neural networks [5], has promoted the rapid development of deep graph anomaly detection. However, most existing
efforts [6], [7], [8] only focus on spotting individual graph
anomalies, that is, single nodes or edges. In contrast, the
abnormal subgraph (AS) detection task has received much
less scrutiny despite the pressing need from real applications
[1]. For instance, early methods [9], [10] exploit topological
signals such as L1 properties of the eigenvectors of the
modularity matrix to reveal dense anomaly regions, yet the
neglect of node attributes limits their identification of various intricate anomalies. Instead, AMEN [11] considers both
attribute and topological information. It spots subgraph anomalies that exhibit special attribute distributions by measuring the

G

2162-237X © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

PENG et al.: END-TO-END AS DETECTION VIA SUBGRAPH-LEVEL CONTRASTIVE LEARNING

Fig. 1. (a) Fraudulent companies engage in tax evasion by issuing false VAT
invoices to each other, often forming a subgraph with dense edge connections.
(b) Group of patients infected with COVID-19 have unusual disease symptoms
from healthy residents, that is, higher temperature (T), lower oxygen saturation
(SaO2 ), and higher respiratory rate (RR).

normality of the subgraph. However, the traditional data statistical technique used by AMEN results in low computational
efficiency and poor scalability. Recent deep learning methods
DeepFD [12] and FraudNE [13] first derive node embeddings
through an autoencoder and then feed them into distribution density-based DBSCAN [14] to detect dense blocks as
anomalies. However, this pipeline scheme is difficult to ensure
that the learned representations are conducive to identifying anomalies and can easily lead to suboptimal solutions
compared to end-to-end optimization. As a recent sophisticated end-to-end subgraph anomaly detection framework,
AS-GAE [4] presents a location-aware graph autoencoder and
a supermodular graph scoring function to uncover anomalous
areas. However, its reliance on a manually set threshold is
prone to mislocating abnormal areas, limiting its effectiveness
in many complicated scenarios. Additionally, existing node
anomaly detection approaches such as ANEMONE [15] and
GRADATE [8] cannot be simply applied to identify subgraphlevel anomalies as they lack recognition of subgraph structures
and consideration of collaborative behaviors between nodes
within the subgraph. More dedicated efforts are therefore
needed to explore a promising solution for anomalous subgraph detection, which motivates our research work.
Combined with practical application scenarios, identifying
subgraph anomalies faces the following challenging issues.
First of all, it is inaccessible to acquire sufficient and
high-quality ground-truth anomalies to support an end-toend supervised learning paradigm. Due to the diversity of
anomalies, in most cases, we have little or no prior knowledge about abnormal patterns in advance to label samples.
Moreover, the combinatorial nature of subgraphs would make

18313

the solution space exponentially large, which makes manual
annotation almost impossible. Thus, exploring an unsupervised framework for AS detection is quite necessary. Second,
deriving the anomaly-aware subgraph partition from both
topological and attribute perspectives simultaneously can be a
daunting task. Unlike independent nodes or edges, subgraphs
composed of nodes and edges come in various sizes and
inner structures due to their different construction forms.
Meanwhile, the abnormality of subgraphs may be manifested
in deviated attributes, dense topological connections, inconsistent associations between attributes and structures, and so
forth. To reveal ASs, adaptively searching an anomaly-aware
subgraph division through attribute and structural information
is indispensable yet challenging, especially in unsupervised
conditions where the potential subgraph space can be as high
as exponential. Finally, it is challenging to design training
objectives to effectively distinguish ASs from benign ones
and quantify their degree of abnormality. The anomaly detection process necessitates appropriate objective functions to
enable the detection model to capture the distinction between
anomalies and benign counterparts. However, it is extremely
hard to model the deviation or even quantify the arbitrary
abnormal patterns within subgraphs when the ground-truth
anomaly type is unknown. Although the previous nondeep
methods [16], [17] resort to handcrafted measure functions,
the poor expressive power of fixed features limits their ability
to generalize to unseen anomalies.
To cope with the above challenges, we propose a endto-end unsupervised subgraph anomaly detection framework
(EndSubG), which jointly models subgraph partition and AS
recognition in an end-to-end manner. Specifically, E ND S UB G
learns anomaly-aware graph embedding by explicitly capturing
possible abnormal edges that violate the Homophily assumption [18]. Note that nodes exhibiting unusual collaborative
behaviors have similar patterns and tend to form a subgraph.
A trainable clustering layer is employed to learn subgraph
partition according to semantic distribution while capturing
the boundaries between anomalies and normal regions that
contribute to uncovering anomalies. The learned soft clustering
assignment ensures the possibility of nodes belonging to
multiple subgraphs, which is more consistent with reality
[19]. By coarsening the node and edge sets into subgraphs,
we arrive at the subgraph-level composition of the input
network. Then, a contrastive learning strategy that models the
congruence between each subgraph and its vicinity derived
from the coarsened subgraph network is introduced to measure
the abnormality. Through end-to-end joint optimization, E ND S UB G implements adaptive anomaly-aware graph embedding
and subgraph division to facilitate the identification of ASs
that deviate from the majority. In contrast, the two-stage
pipeline method is prone to erroneously dividing the graph
due to not directly targeting the anomaly detection task (e.g.,
the partitioning stage targets maximizing modularity [20] or
graph reconstruction [21]), leading to failure in subgraph
anomaly recognition. In practice, pipeline-based methods often
involve the combination of various deep or nondeep models,
resulting in an explosion of parameter combination space,
from which selecting to obtain promising performance is
very time-consuming. In addition, we design a new metric
weighted normalized mutual information centered on AS (AS-

18314

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

WNMI) that measures the quality of subgraph partitioning
while assessing the ability to identify anomalies, which fills
the gap in performance evaluation for the subgraph anomaly
detection task. Our main contributions are summarized as
follows.
1) We examine the limitations of existing works, then introduce a new idea that jointly models subgraph partition
and subgraph anomaly detection as a whole instead of
treating them as two separate steps.
2) We propose an end-to-end AS detection framework
E ND S UB G based on anomaly-aware subgraph partition
and subgraph-level contrastive learning, providing a new
solution for the field of deep subgraph anomaly detection
that has received less attention.
3) We design a new evaluation metric AS-WNMI to
promote research on elaborate metrics for this task.
Moreover, we empirically validate the superiority of
E ND S UB G on both synthetic and real-world datasets,
and intuitively explain and analyze the detected subgraphs through case studies.
II. R ELATED W ORKS
A. Node Anomaly Detection
Most existing efforts focus on identifying abnormal nodes
following the unsupervised learning paradigm. Here, we
briefly introduce the following three types of representative
algorithms. Traditional shallow models such as Radar [22] and
ANOMALOUS [23] resort to matrix factorization combined
with residual analysis to spot abnormal nodes. With the
rapid development of graph neural networks, deep frameworks
such as D OMINANT [24], SpecAE [25], and AnomalyDAE
[26] uncover anomalies utilizing GCN-based autoencoder with
the capability of learning the expressive representations of
nonlinear relationships within the complex structure. Subsequently, the powerful performance of contrastive learning
brought new directions to the development of graph anomaly
detection. Popular methods including CoLA [6], ANEMONE
[15], and GRADATE [8] derive anomaly scores by learning
to measure the agreement between contrastive counterparts.
Recently, promising detection techniques have continued to be
enriched. For instance, RG-GLD [27] achieves the lightweight
anomaly detection for secure and efficient Internet-of-Things
(IoT) communications by reconstructing the directed graph
formed by data communications with global-local knowledge distillation. ARISE [28] spots topology anomalies and
attribute anomalies simultaneously by perceiving suspicious
substructures through a region proposal module. However,
these methods aim to identify the abnormal behavior of a
single entity rather than analyzing the discrepancy between
node collaborative behaviors on a subgraph basis, making them
unable to be directly applied in AS identification scenarios.
B. Subgraph Anomaly Detection
Unlike spotting node anomalies, anomaly detection on the
subgraph level has received much less attention due to the
difficulties in subgraph pattern modeling and subgraph abnormality quantification. One mainstream of existing works is
nondeep techniques based on traditional graph analysis. For

instance, Miller et al. [9] provided a statistical model to detect
less-correlated subgraphs through L1 properties of the graph’s
eigenvectors. SODA [16] designs a system that finds ASs
given a graph and a query by indications of edge occurrence. Motivated by special attribute distributions of subgraph
anomalies, gAnomaly [2], AMEN [11], and Slicendice [29]
model attribute distributions and measure the normality of
subgraphs for detection. Nonetheless, the dependency on handcrafted anomaly measure functions makes it difficult for them
to handle unknown anomaly patterns in the absence of prior
information. Moreover, these methods cannot learn high-order
semantic information from structure and attribute simultaneously, making them noise-sensitive and unable to generalize.
Deep subgraph anomaly detection frameworks have recently
shown superior performance and have become a hot research
topic for future development. For instance, DeepFD [12]
and FraudNE [13] project the user-item bipartite graph into
node embeddings first and then find dense blocks through
a density-based algorithm such as DBSCAN. However, the
way that separates representation and anomaly detection as
two independent steps easily leads to a suboptimal solution.
In contrast, AS-GAE [4] develops an end-to-end detection
framework. It employs a location-aware graph autoencoder
to uncover anomalous areas based on reconstruction and a
supermodular graph scoring function to measure the anomaly
score of each subgraph. However, its reliance on a manually
set threshold is prone to mislocating abnormal areas, and its
inappropriate subgraph extraction strategy further leads to poor
performance. To address the above limitations, we explore an
end-to-end unsupervised subgraph anomaly detection method,
which adaptively performs anomaly-aware graph embedding
and subgraph extraction, then quantifies subgraph anomaly
based on contrastive learning.
III. P ROPOSED F RAMEWORK : E ND S UB G
Before going further, we first give a formal definition of the
studied problem. Given an attributed network G = (V, E, F)
with |V| = n nodes and |E| = m edges, where each node vi ∈ V
is affiliated with a set of d-dimensional attributes (features)
F = { f1 , f2 , . . . , fd }. We let the matrix X ∈ Rn×d represent node
attributes, where xi ∈ Rd denotes the feature for node vi . The
adjacency matrix A ∈ {0, 1}n×n is used to record edge links,
where Ai j = 1 indicates the existence of an edge ei j = (vi , v j )
between nodes vi and vj ; otherwise, Ai j = 0. A subgraph of
G is denoted as S = (VS , ES , F), where VS ⊆ V and ES ⊆
E ∩ P(VS ). P(VS ) indicates the powerset of VS . With the above
notations, the goal of unsupervised AS detection aims to spot
suspicious subgraphs S ⊆ G that significantly deviate from
the major patterns of the graph G, where the likelihood of the
subgraph being abnormal is quantified by a scoring function
f (·). It should be emphasized that in this problem set, the
candidate subgraph set S̄ = {S1 , S2 , . . . , S p } for graph G is
not given in advance. Considering that the potential subgraph
search space is as large as exponential, our studied problem is
more challenging than the setting where a candidate subgraph
set is given beforehand like [3]. Next, we elaborate on the
proposed end-to-end joint modeling framework E ND S UB G, a
high-level overview of which is shown in Fig. 2.

PENG et al.: END-TO-END AS DETECTION VIA SUBGRAPH-LEVEL CONTRASTIVE LEARNING

18315

Fig. 2. High-level overview of the proposed E ND S UB G. Given an attributed graph, E ND S UB G achieves anomaly-aware graph embedding and subgraph
partition by explicitly considering potential abnormal edges and capturing the boundaries between anomalies and normal regions. After forming the coarsened
subgraph network, it spots ASs by learning the “subgraph-vicinity” matching patterns. E ND S UB G follows an idea that jointly models graph embedding,
subgraph partition, and subgraph anomaly detection.

A. Anomaly-Aware Graph Embedding and Subgraph
Partition
High-quality graph embedding is adept at capturing finegrained pattern distinctions among nodes, which is essential
for exposing unusual and problematic graph components
to facilitate subgraph partition. Inspired by modern selfsupervised graph representation learning [30], [31], we expect
to build a graph embedding mechanism similar to GMI [32]
that maximizes graphical mutual information between the
0
input graph G and node embeddings H ∈ Rn×d . However, the
existence of ASs may negatively impact representation quality
through neighborhood message propagation and mutual information operations. Specifically, we find that the boundaries
of ASs and normal regions often have illegal edge links
that violate the Homophily principle. These edges have lower
existence probabilities predicted by attribute similarity than
others, introducing heterophily into the graph. However, many
theoretical studies [33], [34], [35] have shown that conventional GNN models employ homophily as a strong inductive
bias, and the heterophilic edges will seriously degrade their
performance. Thus, capturing these boundaries helps GNN
models perceive potential anomalies and focus on finely modeling the similarity of homophily signals. This facilitates good
partitioning of subgraphs with similar collaborative behaviors.
To this end, we refine the input graph topology by reweighting
A with potential anomaly probabilities according to the wellknown three-sigma rule (3σ rule) [36] in statistics. It states that
almost all (99.73%) values are within three standard deviations
of the mean, while values outside this range are most likely to
be anomalies, which has been widely used in various fields for
outlier detection [37], [38], [39]. Formally, for an edge eij , we
estimate its anomaly probability Pi j by quantifying whether its
existence probability is less than the average probability of all
edges in G with a predefined number λ of deviation standards
(
ri j , if ri j < MEAN rkl − λ STD rkl
ekl ∈E
ekl ∈E
Pi j =
(1)
1, otherwise

where ri j = cos(xi , x j ) aims to calculate the existence probability of eij . Note that in practice, the standard deviation interval
can be adjusted according to the requirements of different
fields or tasks. To better adapt to distinct data distributions, we
introduce the hyperparameter λ in (1) to control the threshold
range. The experiments on parameter analysis also demonstrate the effectiveness of adjusting thresholds on different
datasets. Then, we derive adjusted graph structure A0 = A P,
where denotes the Hadamard product.
Now, we perform anomaly-aware graph embedding by introducing weights A0 to adjust the calculation of the graphical
mutual information loss (see [32] for detailed theoretical
analysis). We first define the computation graph of node vi
that specifies the neighborhood around a particular node to
perform a localized convolution as Gi , then maximize the
0
mutual information between hi ∈ Rd and Gi by
I(hi ; Gi ) = I(hi ; xi ) +

X
j∈N (i)


A0i j
I(hi ; x j ) + I wi j ; A0i j (2)
|N (i)|

where wi j = σ(h>i h j ) with the sigmoid function σ. Under the
guidance of weight A0i j , the representation hi will extract and
preserve less information about neighboring nodes that may be
anomalies while weakening the topological tie with the possibly abnormal nodes to form a boundary. As for I(hi ; x j ), we
can employ well-known mutual information estimators such
as the Jensen-Shannon MI estimator (JSD) [40] to calculate
(see experiments for the other estimator)



I(hi ; x j ) = −sp −DΘ hi , x j − Evn ∼Pn sp DΘ hi , xvn
(3)
where Pn denotes the uniform distribution on the node set
V \ {v j }, and sp(x) = log(1 + e x ) is the soft-plus function. The
discriminator DΘ : d0 × d → R we applied is a simple bilinear
scoring function

DΘ (hi , x j ) = σ h>i Θx j
(4)

18316

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

where Θ denotes a learnable parameter and the logistic sigmoid nonlinearity σ aims to convert scores into probabilities
of (hi , x j ) being a positive pair. In addition, we maximize
I(wi j ; A0i j ) via calculating an adjusted cross-entropy

wi j
I wi j ; A0i j = Ai j log 0 + (1 − Ai j ) log(1 − wi j ). (5)
Ai j
Now, we arrive at the objective loss for graph embedding
X
Lenc = −
I(hi ; Gi ).
(6)
vi ∈V

By maximizing I(hi ; Gi ) with the sum of (3) and (5) over all
hidden vectors H, the learned representations finely preserve
the attribute and topological information inherent in the graph,
and has good separability between benign and abnormal,
which helps in adaptive division of subgraphs.
Considering that nodes exhibiting collaborative behaviors
typically have similar patterns, leading to their high proximity
in the embedding space. This inspires us to utilize a differentiable clustering layer [41] for adaptive subgraph partitioning
based on the semantic distribution of representations. As
the model trains, this layer continuously optimizes the soft
assignment of nodes to clusters (i.e., subgraphs), then the
above nodes will tend to be grouped into a subgraph.
Let µc indicate the center of cluster c ∈ {1, 2, . . . , C}. The
assignment matrix to be learned is denoted as S ∈ Rn×C , where
Sic records the degree to which node vi is assigned to cluster
c. Here, we utilize a soft-min assignment to assign each node
vi to the cluster centers based on distance

exp −τ khi − µc k

Sic = P
(7)
C exp −τ khi − µC k
where τ is an inverse-temperature hyperparameter, and we
use norm k·k as negative cosine similarity due to its good
performance. The soft assignments S are more adaptable to
the assumption that nodes may participate in multiple clusters simultaneously. Similar to typical K-means, we optimize
each cluster
center
P
P by alternately updating Sic via (7) and
µc =
i Sic hi /
i Sic . This iterative process will converge to
a fixed point where µ remains unchanged between successive
updates [42].
Intuitively, the more common subgraphs node vi and node
vj participate in, the more likely they are to be connected
by an edge. At the same time, we also need to force nodes
at the boundary to be divided into different clusters. Hence,
we aim to apply A0i j carrying anomaly boundary information
to constrain the similarity and dissimilarity between cluster
assignment vectors of different nodes
!
X


σ Si S>j
Lpar = −
log
− EPn log σ −Sn S>m
0
Ai j
(vi ,v j )∈E

(8)
where Pn denotes the uniform distribution over nonedges
(vn , vm ) in G. As can be seen, the trainable clustering layer will
adaptively group nodes with similar patterns that may belong
to normal or abnormal subgraphs. Based on the subgraph
composition of graph G, we switch the perspective from node
level to subgraph level to examine the abnormality of each
subgraph, which is the focus in Section III-B.

It should also be noted that the behavior of subgraph
anomaly detection heavily depends on the quality of extracted
subgraphs, especially in unsupervised scenarios. Existing
methods have paid little attention to this aspect and still
have many limitations. For instance, AMEN treats the egonet of each node as a subgraph to be examined. Although
it reaches fine granularity, it ignores the role of attribute
correlation in subgraph division. AS-GAE extracts subgraphs
by finding connected components in the residual network.
This partitioning fails to capture the cooperativity exhibited by
subgraph anomalies, leading to undesirable results. In contrast,
the learnable clustering strategy we adopt achieves adaptive
anomaly-aware subgraph partition, which is beneficial to the
subsequent accurate identification of subgraph anomalies.
B. Subgraph-Level Contrastive Learning
For the exported candidate subgraph set {S1 , S2 , . . . , SC },
the key question is how to measure the abnormality of each
subgraph in an unsupervised manner to distinguish anomalies
from benign. Note that ASs often exhibit discrepancies with
their surrounding areas, serving as a good anomaly indicator.
Hence, we focus on picking out this inconsistency by learning
the “subgraph-vicinity” matching patterns. In specific, we first
convert the input graph G into a subgraph-level composition
form through the following coarsening operations:
XS = S> H ∈ RC×d

0

AS = S> AS ∈ RC×C

(9)

where XS stores hidden embeddings for each of the subgraphs,
which is derived by aggregating node embeddings according
to the learned cluster assignments. Similarly, AS is the coarsened subgraph adjacency matrix that records the connectivity
strength between each pair of subgraphs.
To adapt to the lack of prior annotations, we create
“subgraph versus vicinity” instance pairs and model their
matching associations in a contrastive learning manner. For
each subgraph Si , its vicinity
P V i is defined by the fused
neighboring subgraphs V i = j∈N (i) AS i j XS j , which together
form a positive pair. To generate negative instances, we build
e = (e
a corrupt graph G
X, A) by adding noise sampled from a
uniform distribution to the given attributes, that is, e
X = X + .
After passing through the same graph encoding layer, we get
e The objective
negative subgraph representation e
XS by S> H.
function follows a standard binary cross-entropy loss to make
the discriminator successfully differentiate between positive
and negative examples:
Lcon = −

C


1 X
log DΨ XS i , V i + log 1 − DΨ e
XS i , V i
2C
i=1
(10)

where DΨ : d0 × d0 → R is a discriminator similar to (4) with
trainable parameters Ψ.
C. Joint Optimization for Subgraph Anomaly Detection
By combining the above three objectives through tradeoff
parameters α and β, we get the complete objective function
for E ND S UB G
L = αLenc + βLpar + Lcon .

(11)

PENG et al.: END-TO-END AS DETECTION VIA SUBGRAPH-LEVEL CONTRASTIVE LEARNING

After end-to-end joint training of graph embedding, subgraph
partition, and anomaly identification, we acquire a useful classifier DΨ to discriminate the consistency between a subgraph
and its vicinity. Then, the abnormality of each subgraph ai
can be quantified by the scoring function f = 1 − DΨ (XS i , V i ),
where a ∈ RC records the anomaly scores of all subgraphs.
Multiple rounds of statistical analysis can also be used to
calculate anomaly scores [6], [15]. Due to the mismatching
with surrounding areas, an AS will be assigned a lower
probability of being positive (close to 0) by DΨ , thus having a
higher anomaly score. Interestingly, we can then evaluate the
abnormality of each node through S · a, where the anomalous
nodes will provide node-level explanations for the subgraph
anomaly. In other words, for the detected AS, we can further
figure out the abnormality of each node, which is of great
significance for subsequent analysis, management, and even
rectification of anomalies.
D. Complexity Analysis
The graph embedding stage adopts a vanilla GCN [43]
encoder, which has the computational complexity of O(lndd0 +
lmd0 ), where l denotes the number of layers. The discriminator
DΘ has complexity O(ndd0 +nd), and the clustering assignment
needs O(nd0C). During the network coarsening phase, it needs
O(nd0C + mC + C 2 n). The embedding of corrupt graph also
costs O(lndd0 + lmd0 ), and the discriminator DΨ has complexity O(Cd02 + Cd0 ). Note that l and C are usually much
smaller than n, m, d, and d0 , the overall time complexity is
num iters ∗ O(ndd0 + md0 ), which is linearly related to the
number of nodes and edges.
IV. E XPERIMENTS
In this section, we propose a new metric specifically
designed to evaluate the quality of subgraph anomaly detection, which fills the gap in performance evaluation for this task.
Then, we empirically evaluate E ND S UB G on both synthetic
and real-world datasets. A case study is also given to intuitively demonstrate the quality of ASs identified by E ND S UB G
and other baselines. Specifically, we mainly attempt to answer
the following four research questions.
1) Q1: How to quantitatively evaluate the performance of
an algorithm in identifying ASs?
2) Q2: How impactful is the proposed framework on synthetic datasets with different background graphs?
3) Q3: Does the proposed framework work well on realworld datasets with different numbers of ASs?
4) Q4: How to understand ASs identified by the proposed
framework (visual analysis)?
A. New Evaluation Metric: AS-WNMI (Answer to Q1)
Currently, there is no unified specification on how to evaluate the performance of AS detection. Most existing works [4],
[13] still employ commonly used area under the curve (AUC)
or F1 to assess detection results at the node level, which
completely ignores the role of subgraphs. Besides, it should
be noted that in the task setting of unsupervised subgraph
anomaly detection, there is no pregiven candidate subgraph set
S̄ = {S1 , S2 , . . . , SC } with subgraph anomaly labels. Instead of

18317

Fig. 3. 3-D surface plot of AS-WNMI, NMI, and JS distance values under
different simulation cases.

simply judging whether each subgraph Si in the given set is
abnormal, each method utilizes different partition strategies
as discussed in Section III-A to get subgraphs of various
shapes and then spots anomalies accordingly. In this case,
metrics similar to classification accuracy cannot be used. To
meet different application needs, more dedicated research on
new metrics that evaluate anomaly detection quality from the
subgraph level is urgently needed [1].
It can be observed that the quality of the identified ASs
depends on the correctness of the extracted subgraphs and
abnormality measurements. Accordingly, we introduce the
anomaly prediction difference as a weight into NMI (often
used to measure the quality of community detection [19]) and
propose an AS-WNMI as a new evaluation metric. Assume
that the ground-truth subgraph anomaly labels consist of the
subgraph set S̄ ∗ and node anomaly labels y∗ = [y∗1 , y∗2 , . . . , y∗n ] ∈
{0, 1}n , where all nodes belonging to ASs Si∗ are labeled with
1, and others are marked as 0. Similarly, the outputs of the
detection model include the predicted subgraph set S̄ and node
anomaly scores y = [y1 , y2 , . . . , yn ] ∈ [0, 1]n . First, unlike the
community detection task that focuses on whether each community (subgraph) partition is correct, our task concentrates on
extracting ASs rather than the division of normal regions. That
is, normal regions can be divided in any way that helps identify
ASs. Thus, we prune S̄ ∗ by merging all normal subgraphs into
one to omit concerns about the partitioning results of normal
regions. And do the same for S̄. (If S̄ ∗ or S̄ only involves ASs
without further subgraph division of normal regions, the above
operation is unnecessary.) Then, the AS-WNMI (S̄ ∗ , S̄, y∗ , y)
score is defined as



P ∗ P
n n
−2 Ci=1 Cj=1 ni j log niinj j 1 − JS y∗S ∗ , yS j
i
(12)
PC ∗
PC
nj
ni
i=1 ni log n +
j=1 n j log n
where C ∗ and C are the number of ground truth and detected
subgraphs, respectively. nij denotes the number of nodes
appearing in both the ith ground-truth subgraph Si∗ and the
jth detected subgraph S j . n is the number of nodes in G. ni
and nj sum up the number of nodes in Si∗ and S j , respectively.
y∗S ∗ denotes the anomaly labels of nodes belonging to Si∗ , and
i

18318

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

yS j is the predicted anomaly scores of nodes belonging to S j .
JS(p, q) calculates the Jensen–Shannon distance between two
probability vectors p and q, which is the square root of the
Jensen–Shannon divergence and defined as
r
KL( p k m) + KL(q k m)
(13)
2
where KL(·) denotes the Kullback-Leibler divergence, and
m = ( p+q)/2. By measuring the anomaly prediction difference
between y∗S ∗ and yS j (the smaller the difference, the value
i
of JS(y∗S ∗ , yS j ) approaches 0, otherwise, it approaches 1),
i
(13) quantifies the anomaly recognition performance of the
detection model on the subgraph from the node level. After
introducing [1 − JS(y∗S ∗ , yS j )] as weight into NMI, (12) meai
sures the quality of subgraph partitioning and simultaneously
evaluates the ability to identify anomalies in subgraphs. Here,
a simulation experiment is used to illustrate the superiority of
the proposed AS-WNMI over the vanilla NMI. Let us consider
a simple situation. There exist only two clusters, the first one
consisting of five nodes is labeled as normal cluster and the
second one with three nodes is abnormal. We enumerate all
possible partitioning cases (28 = 256) and all possible anomaly
cluster prediction results (2! = 2), leading to 256 × 2 = 512
possible outcomes. We then calculate the scores for each of the
three metrics (i.e., NMI, JS distance, and AS-WNMI) in each
case and draw them in a 3-D surface plot, as shown in Fig. 3.
As can be seen, the value range of AS-WNMI belongs to [0, 1]
and will reach its maximum value of 1 only when NMI reaches
1 and JS distance reaches 0. In other words, AS-WNMI can
reach its highest value only when the AS is correctly divided
from the normal region and all nodes in each part are correctly
judged, that is, the nodes in the AS are predicted to be
anomalous and the nodes in the normal region are determined
as benign. In this sense, the evaluation perspective of the ASWNMI metric is more comprehensive compared with NMI
which only measures the quality of subgraph partition, and
the traditional AUC or average precision (AP) metric which
only considers whether abnormal nodes are identified. Thus,
obtaining a high AS-WNMI score is somewhat challenging
for the detection model.
B. Compared Methods
It needs to be emphasized again that, there are limited
existing studies on unsupervised static subgraph anomaly
detection, as mentioned in the related work. Thus, we select
the following four categories of methods as baselines to meet
the focus of our work.
1) Node Anomaly Detection: Two state-of-the-art methods
are selected to explore whether they are still effective in
subgraph anomaly detection, which are both based on selfsupervised contrastive learning.
1) ANEMONE [15]: spots anomalous nodes by learning
the patch-level (i.e., node versus node) agreement and
context-level (i.e., node versus ego-net) agreement concurrently.
2) GRADATE [8]: presents a multiscale contrastive learning framework with an augmented graph view for node
anomaly detection.

2) Dense Block Detection: Following the idea of DeepFD
[12] and FraudNE [13] that learn bipartite graph embedding
first and then uncover suspicious dense blocks with DBSCAN
[14] for fraud detection, we design a baseline consisting of
two phases: attributed graph representation learning and dense
block detection.
1) GAE [44] + DBSCAN: GAE generates node embeddings
by learning to reconstruct topological links, after which
DBSCAN identifies dense regions in the vector space.
2) DGI [30] + DBSCAN: DGI derives informative node
embeddings via maximizing the mutual information
between patch-level and graph-level representations and
then achieves dense block detection by DBSCAN.
3) Subgraph Anomaly Detection (Pipeline): For an arbitrary subgraph set, SADE [3] learns role-guided subgraph
embedding first by taking into consideration both local connections and global roles and then employs classic unsupervised
outlier detection techniques such as Isolation Forest [45] or
LOF [46] to spot suspicious transactions in the encoded subgraph embedding space. Since there is no predefined subgraph
set under our task setting, we adapt SADE to a baseline that
follows a pipeline of subgraph division, subgraph embedding,
and outlier detection.
1) Louvain [47] + SADE: Louvain divides the input graph
into multiple communities based on modularity optimization, which is fed into SADE to derive subgraph
embeddings, and then LOF spots outlies in the vector
space by measuring the local deviation of the density of
a certain object with respect to its neighbors.
2) CommDGI [20] + SADE: CommDGI performs clustering assignment by learning to maximize community
mutual information and modularity from both attribute
and topological perspectives and then identifies anomalies in the subgraph embedding space with the help of
SADE.
4) Subgraph Anomaly Detection (End-to-End): We compare E ND S UB G with existing two open-source end-to-end
methods, including a traditional nondeep model and a deep
learning framework.
1) AMEN [11]: introduces a measure called normality to
evaluate the abnormality of attributed neighborhoods
from both internal consistency and external separability.
2) AS-GAE [4]: learns a residual graph by location-aware
graph autoencoder, on which a trainable supermodular
graph scoring function is applied to assign anomaly
scores to the extracted subgraphs.
C. Parameter Settings and Metrics
All experiments, except AMEN based on MATLAB, are
implemented in PyTorch and carried out on a single NVIDIA
4090 GPU. Since SADE does not have a public source code,
we implemented it ourselves based on its published paper.
As for other baselines, they are all implemented using the
released source code and undergo parameter tuning according
to the empirical strategies reported in their papers. About
E ND S UB G, we adopt two layers of GCN with 512 or 128
neurons as the graph encoder. The number of negative samples
for the JSD estimator is set to 5. We select the number of

PENG et al.: END-TO-END AS DETECTION VIA SUBGRAPH-LEVEL CONTRASTIVE LEARNING

18319

TABLE I
S TATISTICS OF S YNTHETIC AND R EAL -W ORLD DATASETS

extracted subgraphs C from {8, 10, 12, 15, 20}, and the initial
cluster centers are chosen by the idea of K-means++, which
benefits to accelerate the convergence of the model [48].
During training, we adopt the Adam [49] optimizer with
the learning rate adjusted in the range of {1e−3 , 3e−4 , 1e−4 }.
The inverse-temperature hyperparameter τ is set to 30. The
parameters α and β are selected from {0.1, 0.3, 0.5, 0.7, 1.0},
and we tune the parameter λ in [1, 2] combined with the
interquartile range (IQR) rule [50].
On the one hand, following the commonly used metrics
in the previous subgraph anomaly detection works [4], [11],
which only consider whether node anomalies are spotted, we
also calculate AUC and AP based on y∗ and y to assess the
detection results. The AUC score (area under the receiver
operating characteristic curve, ROC-AUC) assesses how well
the model generates relative scores to distinguish positive or
negative examples across all classification thresholds. The AP
score evaluates the ability of the model to identify positive
instances accurately while maintaining high precision. AP
is more suitable for anomaly detection tasks where positive (abnormal) and negative (benign) samples are extremely
imbalanced. On the other hand, we adopt our proposed ASWNMI to comprehensively evaluate the subgraph anomaly
detection performance from both subgraph partitioning and
anomaly identification. Here, we report the average results
over five runs for the above metrics.

D. Results on Synthetic Datasets (Answer to Q2)
1) Data Generation: To simulate different scenarios comprehensively, we consider the following three network models
as background graphs: 1) Erdős-Rényi (ER) model that generates a graph where a given number of nodes are randomly
connected with a certain probability; 2) Barabási–Albert
(BA) model that creates scale-free graphs; 3) connected
Watts–Strogatz (CWS) model that produces connected smallworld property graphs. We choose one specific type above
and utilize the following NetworkX graph generators to
generate 20 independent subgraphs with different numbers
of nodes and structural properties sampled from a given
distribution range.
1) ER graph is generated with the function
erdos renyi graph(n,p), where n for the number
of nodes and p for the probability for edge creation.

TABLE II
PARAMETER S ETTINGS FOR N ETWORK API S

2) BA
graph
is
created
with
the
function
extended barabasi albert graph(n,m,p,q),
where n for the number of nodes, m for the number
of edges with which a new node attaches to existing
nodes, p for the probability value for adding an edge
between existing nodes, and q for the probability value
of rewiring of existing edges.
3) connected watts strogatz graph(n,k,p) is for
the CWS graph, where n for the number of nodes, k for
the number of nearest neighbors in a ring topology, and
p for the probability of rewiring each edge.
We select four from all subgraphs and label them as
anomalies by setting parameters to make them smaller in
network size and denser in topological structure. Then, we
connect all subgraphs together to form a connected graph by
setting a probability of 0.3 of one node connecting to any
node in the other subgraph. In addition, node feature design
follows the pattern provided by AS-GAE [4]. Node features in
normal subgraphs and ASs are sampled from different Poisson
distributions with randomly selected λ and the constraint
(λanomaly /λnormal ) = 5. The definition of a Poisson distribution
is Pλ (x) = (λ x e−λ /x!). The data statistics are summarized in
Table I. All parameters are randomly selected from a specific
distribution shown in Table II.
2) Performance Evaluation: Table III reports AUC, AP, and
AS-WNMI scores of all methods, based on which we have the
following observations.
1) Across all datasets, E ND S UB G achieves almost the
best results concerning all metrics, except AS-WNMI
on the BA graph (detailed explanations of this special case later). The best AUC and AP scores reflect
the superiority of E ND S UB G in discovering anomalies

18320

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

TABLE III
P ERFORMANCE OF D IFFERENT M ETHODS ON S YNTHETIC DATASETS . T HE B EST R ESULTS A RE M ARKED IN B OLD . N/A M EANS N OT A PPLICABLE

from the node granularity compared to other baselines.
Besides, the promising AS-WNMI value shows that
E ND S UB G works well in spotting subgraph anomalies
from the perspective of subgraph division and anomaly
identification in an unsupervised fashion. This advantage
benefits from the fact that the anomaly-aware graph
embedding and subgraph partition explicitly capture the
boundary between anomaly and benign, which facilitates the discovery of subgraph anomalies through
subgraph-vicinity contrastive learning. Moreover, our
E ND S UB G is relatively robust to different background
graph types.
2) Overall, dense block detection models and pipelinebased methods exhibit undesirable performance on this
task, although GAE + DBSCAN and DGI + DBSCAN
get good results in the BA graph. Note that the BA graph
is a scale-free network that is closer to reality and much
sparser than the other two graphs (see Table III). ASs are
obviously denser in the network and are therefore easily
recognized by dense block detection methods. However,
in the denser CWS graph and ER graph, it is difficult
to distinguish the boundary between ASs and normal
regions based on density alone, so the performance is
depressing. Moreover, the high AS-WNMI score on the
BA graph is since the DBSCAN generates clear anomaly
and benign labels rather than anomaly scores (probabilities), that is, the prediction y = [0, 1, . . . , 1] ∈ {0, 1}n
instead of y ∈ [0, 1]n , which will result in a higher
AS-WNMI value due to less error when calculating
JS(y∗S ∗ , yS j ). Methods that output anomaly probabilities
i
suffer slightly in this regard, but the anomaly warning
level supported by the probability is more suitable for
practical application. The higher AUC and AP scores
still reflect the stronger anomaly identification ability of
E ND S UB G. Moreover, the large parameter search space
caused by the combination of multiple methods leads
to a formidable defect. It should also be noted that
the synthetic datasets here simulate an ideal detection
scenario with obvious subgraph anomalies. While these
methods are somewhat effective, whether they still work
well in more complicated real-world situations will be
explored later.
3) Although two node anomaly detection models still
uncover a certain portion of anomalies, due to the lack
of recognition of the subgraph structure, their detection

outputs do not form the concept of subgraph anomalies,
thus inapplicable to AS-WNMI. Besides, the sparseness
of the BA graph makes it difficult to ensure the diversity
of sampled contrast pairs based on random walk with
restart (RWR), thus impairing the correct identification
of anomalies by the discriminator.
E. Results on Real-World Datasets (Answer to Q3)
1) Data Description and Anomaly Injection: Note that
there are currently almost no real-world datasets for AS
detection publicly available in the research community. Privacy
policy aside, manually spotting and annotating anomalous
subgraphs is inherently challenging. Thus, we select four real
datasets here, then following the previous studies [4], [51]
inject ASs for experimentation.
LargeCora is an extension of the common citation network
Cora [43], where nodes correspond to documents and edges
indicate citation relations. Each node is associated with a bagof-words representation whose dimension is determined by the
dictionary size. AmazonComputer is the “Computer” part of
the Amazon co-purchase graph [52], where nodes represent
computers, edges indicate that two products are frequently
bought together, and node features are bag-of-words encoded
product reviews. Reddit [53] contains a user-subreddit graph
that captures posts shared across subreddits for a month. The
nodes represent users, whose interactions with posts form
edges, and posts are converted into node features. Questions
[54] is collected from the question-answering website Yandex
Q, where nodes are users and edges indicate that one user
answered the other user’s question during one year. Each user
has a description that is converted into an average of FastText
embeddings for words. Since the latter two datasets contain
annotated node anomalies, they need to be removed before
injecting anomalous subgraphs.
Following the method outlined in [51], we inject one or
three ASs into each dataset to simulate two detection scenarios.
Taking the injection of one anomaly as an example, we
first find two connected subgraphs from the graph randomly,
one of which is larger and the other is smaller. Then, we
select a connected subset of nodes in the larger subgraph
that matches the size of the smaller subgraph as a candidate
for subgraph anomaly. The node attributes of this subset are
replaced by those of the smaller subgraph to ensure a collective attribute distribution. Moreover, edge links are randomly

PENG et al.: END-TO-END AS DETECTION VIA SUBGRAPH-LEVEL CONTRASTIVE LEARNING

18321

TABLE IV
P ERFORMANCE OF D IFFERENT M ETHODS ON R EAL -W ORLD DATASETS W ITH O NE AS. T HE B EST R ESULTS A RE M ARKED IN B OLD

TABLE V
P ERFORMANCE OF D IFFERENT M ETHODS ON R EAL -W ORLD DATASETS W ITH T HREE AS S . T HE B EST R ESULTS A RE M ARKED IN B OLD

introduced between nodes in the subset for perturbation from
the topological perspective. The detection model is expected to
uncover these ASs by considering both attributes and structural
properties. Detailed dataset statistics are listed in Table I.
2) Performance Comparison: The results with only one
AS and three ASs are summarized in Tables IV and V,
respectively. We have the following observations.
1) E ND S UB G consistently outperforms other baselines
in real-world datasets involving different numbers of
subgraph anomalies, which strongly confirms the effectiveness of our proposed joint modeling framework for
anomaly-aware subgraph partition and anomaly detection. By contrast, AS-GAE relies on a manually set
threshold to locate unusual areas, which is difficult to
adapt to the unknown data distribution and prone to erroneously narrowing the scope of the abnormal regions.
Besides, it treats connected components in the network
as extracted candidate subgraphs with the neglect of
correlations between graph topology and node attributes.
This problematic subgraph division further makes it fail
to detect subgraph anomalies accurately (see case study).
2) On real-world datasets with no clear subgraph boundaries and more complex types of anomalies, dense block
detection models including GAE + DBSCAN and DGI
+ DBSCAN no longer achieve the same good results as
on the synthetic BA graph. From the perspective of AP
scores, their performance has declined significantly, and
the recognition precision of anomalies is less than 10%.
Additionally, the gap between pipeline-based methods
and our E ND S UB G once again corroborates the superiority of exploring end-to-end methods to solve the
subgraph anomaly detection from a holistic perspective.
3) Impact of Different Mutual Information Estimators:
We additionally explore the impact of another widely used
InfoNCE estimator on detection performance. Since we follow
the InfoMax principle [55] to directly maximize the mutual
information between input node features and embeddings,
which have different dimensions, the InfoNCE formulation in
Deep InfoMax [56] is used here to calculate I(hi ; x j )
h X
i
I(hi ; x j ) = DΘ (hi , x j ) − Evn ∼Pn log
eDΘ ( hi ,xvn ) . (14)
We replace only the mutual information estimator and keep
other experimental settings unchanged. As can be seen from
the last two rows of Tables IV and V, compared with the
JSD estimator, InfoNCE achieves both gains and decreases in
performance on different datasets. Overall, the performance
of these two mutual information estimators is quite comparable, and in practice, they can both be considered promising
solutions (with a suitable number of negative samples).
F. Case Studies (Answer to Q4)
We provide intuitive visual analysis to better understand the
detected ASs. Since the large number of nodes in real datasets
results in poor visualization, we adopt the graph generation
strategy mentioned in Section IV-D1 to create a synthetic
dataset with the BA model as background graphs. It contains
1050 nodes belonging to ten communities (subgraphs), among
which two ASs have denser topological links and deviated
node attributes, as shown in Fig. 4. We use different colors

18322

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

Fig. 4. (a) Synthetic dataset where two ASs are marked by diamond-shaped nodes. Visualization of detection results on the synthetic dataset from (b) DGI
+ DBSCAN, (c) AS-GAE, and (d) our E ND S UB G.

Fig. 5. AUC, AP, and AS-WNMI plots of E ND S UB G with respect to different λ on four real-world datasets. (a) LargeCora 3AS. (b) AmazonComputer 3AS.
(c) Reddit 3AS. (d) Questions 3AS.

to display the subgraph division results of each algorithm.
For DGI + DBSCAN, although the discovered noisy nodes
have a lot of overlap with true ASs, there are still many
misidentified anomalies. Besides, DBSCAN only divides the
nodes in the input graph into two clusters and does not
further distinguish the other eight normal subgraphs in the
ground truth, which seems very coarse-grained. As for ASGAE, the residual graph derived by manual threshold may
mistakenly narrow the scope of the anomaly area, and the
inappropriately connected subgraph extraction further causes
a big gap between the identified AS and the ground truth.
By contrast, our E ND S UB G implements explicit anomalyaware subgraph division, a form of subgraph composition that
highlights anomalies in the input graph. The shade of node
color represents the anomaly score evaluated by E ND S UB G.
The higher the score, the darker the color. It can be seen
from Fig. 4(d) that the division of subgraphs is similar to the
intrinsic community structure of the input graph. For two ASs,
E ND S UB G summarizes them into a unified AS, and almost all
the nodes involved are ferreted out. For our assumed normal
areas, the model also pre-evaluates the potential risk levels
in each subarea. Overall, E ND S UB G shows superior subgraph
anomaly detection quality than other baselines.
G. Parameter Analysis
Note that the model E ND S UB G involves several hyperparameters such as the predefined number λ of deviation
standards in (1), the number of extracted subgraphs C in
(8), an inverse-temperature parameter τ in (7), and the tradeoff parameters α and β in (11). In this part, we mainly
explore the impact of these important parameters on detection
performance.

1) Extent of Anomaly Perception: We change λ from 0 to
2.5 in the step of 0.5 and keep the other parameters unchanged.
Fig. 5 shows the changes of E ND S UB G regarding the above
three metrics on four real-world datasets with three ASs.
As can be seen, with the growth of λ, AUC, AP, and ASWNMI scores all gradually increase and then tend to decline.
Through analysis, we attribute it to the fact that when λ = 0,
most edges (e.g., about 59% in LargeCora 3AS and 57%
in AmazonComputer 3AS) are treated as potential anomalies
and filtered out, including many normal edge structures. This
undoubtedly loses a lot of useful information, leading to
poor detection performance. As λ grows, the filtering range
gradually narrows to real potential abnormal edges, and the
performance becomes better accordingly. But when λ is set
too large, for example, λ = 2.5 in AmazonComputer 3AS,
all edge links will be preserved and utilized. Then potential
anomalies will become noise and negatively impact detection
performance, which reflects the importance of anomaly-aware
thinking. As for LargeCora 3AS, when λ is set to 2 and 2.5,
the model will not filter out any potential anomalies, so the
metric values are the same. In practice, we adjust λ to adapt to
different data distributions and keep the proportion of filtered
edges from being too high as anomalies generally account for
a minority. Overall, setting it to 1.5 to 2.0 is more appropriate.
2) Granularity of Subgraph Partition: We adjust C
from {6, 8, 10, 12, 15, 20, 30} and keep the other parameters
unchanged. The AUC, AP, and AS-WNMI of E ND S UB G
concerning different C on four real-world datasets are illustrated in Fig. 6. It can be seen that all three metrics improve
accordingly as C gradually increases at the beginning. With the
continuous rise of C, the performance drops moderately but
overall maintains a good and stable trend. Too few subgraph
partitions imply oversimplification, which is not conducive to

PENG et al.: END-TO-END AS DETECTION VIA SUBGRAPH-LEVEL CONTRASTIVE LEARNING

18323

Fig. 6. AUC, AP, and AS-WNMI plots of E ND S UB G with respect to different C on four real-world datasets. (a) LargeCora 3AS. (b) AmazonComputer 3AS.
(c) Reddit 3AS. (d) Questions 3AS.

Fig. 7. AUC, AP, and AS-WNMI plots of E ND S UB G with respect to different τ on four real-world datasets. (a) LargeCora 3AS. (b) AmazonComputer 3AS.
(c) Reddit 3AS. (d) Questions 3AS.

the discriminator identifying anomalies by learning “subgraphvicinity” matching patterns. However, if the number of
subgraphs is too large, the subgraphs may be too granular and
difficult to interpret. The overly subtle distribution differences
between subgraphs make it difficult for the discriminator to
delineate the boundary between anomalies and benign ones. In
practice, we recommend employing unsupervised community
detection techniques such as B IG C LAM [57] to automatically
estimate the appropriate number of subgraphs in advance.
3) Impact of Inverse-Temperature Parameter: We tune
τ from {0.1, 1, 10, 30, 50} and keep the other parameters
unchanged. Fig. 7 shows the changes of E ND S UB G regarding
the AUC, AP, and AS-WNMI metrics on four real-world
datasets. It can be seen that the detection performance gradually improves as the τ increases. When τ reaches 50, the
metrics drop slightly. Recall that in (7), a larger inversetemperature value will make the probability distribution
sharper and tend to give higher membership probabilities to
the nearest clusters, which makes the model tend to partition
clearer subgraphs. However, an excessive τ value results
in overly concentrated output probabilities, weakening the
tolerance for overlapping clusters. On the contrary, a smaller
temperature value leads to smoother probability distributions,
making it more difficult for the model to determine the
boundaries of subgraphs and uncover ASs. Overall, the value
of τ cannot be set too small in practice, and it seems more
appropriate to set it around 10–30.
4) Effect of Tradeoff Parameters: We adjust α and β from
{0.1, 0.3, 0.5, 0.7, 1.0} to explore their effects on detection
performance. The performance variance results in terms of
AUC, AP, and AS-WNMI on LargeCora 3AS and AmazonComputer 3AS are shown in Fig. 8. It can be seen that when
α and β are both small, all three metrics are at low levels since

poor quality graph embedding and subgraph partition hinder
the identification of anomalies. The gradual performance gains
come from the increase of α and β, and the promising results
fall within the range of α from 0.7 to 1.0 and β from 0.5 to 1.0.
Accordingly, we recommend setting both α and β around
0.7–1.0 to ensure a positive foundation for graph embedding
and subgraph partition.

H. Computation Load Analysis
In addition to the theoretical complexity analysis, here, we
make an intuitive comparison between the computation loads
of different methods. Table VI lists the GPU/CPU memory and
running time consumed by different methods when detecting
datasets containing three ASs. For pipeline methods, we report
the highest memory usage among the two stages, as well
as the total running time of both stages. Since Louvain +
SADE and AMEN are traditional nondeep methods and do not
involve any operations on GPU, “/” means not applicable. It
can be seen that our method could complete the detection in a
relatively short time (although slightly longer on large datasets,
but acceptable). Although some methods like AS-GAE and
DGI + DBSCAN are somewhat faster, their performance on
all three metrics is significantly lower than ours. Since our
method involves many complex computational processes, it
does consume a lot of GPU/CPU memory, but in exchange
for superior subgraph anomaly detection performance. Overall,
our E ND S UB G could work normally on commonly used GPUs
such as NVIDIA RTX 4090 or A100 and derive promising subgraph anomaly detection results within an acceptable
response time. Here, on large dataset Questions 3AS, we
employ the sampling strategy to avoid GPU memory overflow.
Optimization of the code implementation may further speed up

18324

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

TABLE VI
C OMPUTATION L OADS OF D IFFERENT M ETHODS W ITH R ESPECT T O M EMORY A SSUMPTION (MB) AND RUNNING T IME ,
W HERE MG D ENOTES M AX GPU M EMORY AND MC M EANS M AX CPU M EMORY

TABLE VII
P ERFORMANCE OF E ND S UB G U NDER D IFFERENT DATA M ISSING R ATIOS

TABLE VIII
P ERFORMANCE OF E ND S UB G U NDER D IFFERENT DATA N OISE

I. Further Explorations

still works well when a small amount of data is missing
(e.g., 10% mask), but as the degree of data incompleteness
gradually increases, the performance shows a downward trend.
Introducing attribute-missing graph representation learning
techniques [58] may be a promising solution to address this
limitation.
2) Noisy Data Scenario: Here, we consider two types of
noise scenarios from the aspects of attributes and topology,
respectively. In specific, we add random variables that satisfy
the standard normal distribution to the node attributes to
generate noisy attributes. In addition, we randomly add 100
edge links in the original topology to simulate structural
noise. Table VIII reports the results on two datasets. It can
be found that structural noise seems to have less impact on
the model, which could benefit from the model’s perception
and refinement of noise edges that do not conform to the
homogeneity assumption. In contrast, the model is not robust
enough to attribute noise. Noise-resistant robust graph learning
and anomaly detection techniques [59], [60] may be feasible
solutions to overcome this limitation.

Note that real-world scenarios often involve noisy or incomplete data, we further explore the performance of E ND S UB G
in the following two situations and illustrate its potential
limitations which will be left for future research.
1) Incomplete Data Scenario: Here, we simulate different
degrees of data missing scenarios by randomly masking 10%,
30%, 50%, and 70% of node attributes. Table VII summarizes
the results on two datasets. As can be seen, the model

V. C ONCLUSION AND F UTURE W ORK
This work concentrates on the subgraph anomaly detection
task that has currently received less scrutiny. We present
an end-to-end subgraph anomaly detection framework E ND S UB G, which follows the new idea of jointly modeling
subgraph partition and anomaly detection rather than treating
them as separate steps. E ND S UB G explicitly considers the

Fig. 8. Effects of tradeoff parameters α and β in terms of AUC, AP, and
AS-WNMI on LargeCora 3AS (left) and AmazonComputer 3AS (right).

the operation and reduce memory consumption, which will be
left for future research.

PENG et al.: END-TO-END AS DETECTION VIA SUBGRAPH-LEVEL CONTRASTIVE LEARNING

potential AS boundaries via anomaly-aware graph embedding
and subgraph partition, then spots subgraph anomalies by
learning the “subgraph-vicinity” matching patterns on the
coarsened subgraph network. To comprehensively evaluate the
detection quality from both subgraph partition and anomaly
recognition, we propose an AS-WNMI as a new evaluation
metric, which fills the gap in performance evaluation for this
task. Experiments on both synthetic and real-world datasets
validate the superiority of E ND S UB G in discovering suspicious subgraphs with different numbers of subgraph anomalies
and diverse background graphs. Future work will concentrate
on improving the applicability of the model to practical
scenarios with incomplete and noisy data or integrating temporal modules to capture evolutionary information in dynamic
applications.
R EFERENCES
[1]

X. Ma et al., “A comprehensive survey on graph anomaly detection
with deep learning,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12,
pp. 12012–12038, Dec. 2023.
[2] N. Li, H. Sun, K. Chipman, J. George, and X. Yan, “A probabilistic
approach to uncovering attributed graph anomalies,” in Proc. SIAM Int.
Conf. Data Mining, Apr. 2014, pp. 82–90.
[3] Y. Pei, F. Lyu, W. van Ipenburg, and M. Pechenizkiy, “Subgraph anomaly
detection in financial transaction networks,” in Proc. 1st ACM Int. Conf.
AI Finance, Oct. 2020, pp. 1–8.
[4] Z. Zhang and L. Zhao, “Unsupervised deep subgraph anomaly
detection,” in Proc. IEEE Int. Conf. Data Mining (ICDM), Nov. 2022,
pp. 753–762.
[5] Z. Wu, S. Pan, F. Chen, G. Long, C. Zhang, and S. Y. Philip, “A
comprehensive survey on graph neural networks,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 32, no. 1, pp. 4–24, Mar. 2020.
[6] Y. Liu, Z. Li, S. Pan, C. Gong, C. Zhou, and G. Karypis,
“Anomaly detection on attributed networks via contrastive selfsupervised learning,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33,
no. 6, pp. 2378–2392, Jun. 2022.
[7] Z. Xu, X. Huang, Y. Zhao, Y. Dong, and J. Li, “Contrastive attributed
network anomaly detection with data augmentation,” in Proc. PacificAsia Conf. Knowl. Discovery Data Mining, Jan. 2022, pp. 444–457.
[8] J. Duan et al., “Graph anomaly detection via multi-scale contrastive
learning networks with augmented view,” in Proc. AAAI Conf. Artif.
Intell., 2023, pp. 7459–7467.
[9] B. Miller, N. Bliss, and P. Wolfe, “Subgraph detection using eigenvector L1 norms,” in Proc. Adv. Neural Inf. Process. Syst., 2010,
pp. 1633–1641.
[10] J. L. Sharpnack, A. Krishnamurthy, and A. Singh, “Near-optimal
anomaly detection in graphs using Lovasz extended scan statistic,” in
Proc. Adv. Neural Inf. Process. Syst., 2013, pp. 1959–1967.
[11] B. Perozzi and L. Akoglu, “Scalable anomaly ranking of attributed
neighborhoods,” in Proc. SIAM Int. Conf. Data Min., 2016, pp. 207–215.
[12] H. Wang, C. Zhou, J. Wu, W. Dang, X. Zhu, and J. Wang, “Deep
structure learning for fraud detection,” in Proc. IEEE Int. Conf. Data
Mining (ICDM), Nov. 2018, pp. 567–576.
[13] M. Zheng, C. Zhou, J. Wu, S. Pan, J. Shi, and L. Guo, “FraudNE: A
joint embedding approach for fraud detection,” in Proc. Int. Joint Conf.
Neural Netw. (IJCNN), Jul. 2018, pp. 1–8.
[14] M. Ester, H. Kriegel, J. Sander, and X. Xu, “A density-based algorithm
for discovering clusters in large spatial databases with noise,” in Proc.
2nd Int. Conf. Knowl. Discovery Data Mining, 1996, pp. 226–231.
[15] M. Jin, Y. Liu, Y. Zheng, L. Chi, Y.-F. Li, and S. Pan, “ANEMONE:
Graph anomaly detection with multi-scale contrastive learning,” in Proc.
30th ACM Int. Conf. Inf. Knowl. Manage., Oct. 2021, pp. 3122–3126.
[16] M. Gupta, A. Mallya, S. Roy, J. H. D. Cho, and J. Han, “Local learning
for mining outlier subgraphs from network datasets,” in Proc. SIAM Int.
Conf. Data Mining, Apr. 2014, pp. 73–81.
[17] F. Chen, B. Zhou, A. Alim, and L. Zhao, “A generic framework for
interesting subspace cluster detection in multi-attributed networks,” in
Proc. IEEE Int. Conf. Data Mining (ICDM), Nov. 2017, pp. 41–50.
[18] M. McPherson, L. Smith-Lovin, and J. M. Cook, “Birds of a feather:
Homophily in social networks,” Annu. Rev. Sociol., vol. 27, no. 1,
pp. 415–444, Aug. 2001.

18325

[19] X. Su et al., “A comprehensive survey on community detection with
deep learning,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 4,
pp. 4682–4702, Apr. 2024.
[20] T. Zhang, Y. Xiong, J. Zhang, Y. Zhang, Y. Jiao, and Y. Zhu,
“CommDGI: Community detection oriented deep graph infomax,”
in Proc. 29th ACM Int. Conf. Inf. Knowl. Manag., Oct. 2020,
pp. 1843–1852.
[21] D. He et al., “Community-centric graph convolutional network for
unsupervised community detection,” in Proc. 29th Int. Joint Conf. Artif.
Intell., 2021, pp. 3515–3521.
[22] J. Li, H. Dani, X. Hu, and H. Liu, “Radar: Residual analysis for anomaly
detection in attributed networks,” in Proc. Int. Joint Conf. Artif. Intell.,
2017, pp. 2152–2158.
[23] Z. Peng, M. Luo, J. Li, H. Liu, and Q. Zheng, “ANOMALOUS: A joint
modeling approach for anomaly detection on attributed networks,” in
Proc. Int. Joint Conf. Artif. Intell. (IJCAI), 2018, pp. 3513–3519.
[24] K. Ding, J. Li, R. Bhanushali, and H. Liu, “Deep anomaly detection
on attributed networks,” in Proc. SIAM Int. Conf. Data Mining, 2019,
pp. 594–602.
[25] Y. Li, X. Huang, J. Li, M. Du, and N. Zou, “SpecAE: Spectral
autoencoder for anomaly detection in attributed networks,” in Proc. 28th
ACM Int. Conf. Inf. Knowl. Manag., 2019, pp. 2233–2236.
[26] H. Fan, F. Zhang, and Z. Li, “Anomalydae: Dual autoencoder for
anomaly detection on attributed networks,” in Proc. IEEE Int. Conf.
Acoust., Speech Signal Process. (ICASSP), May 2020, pp. 5685–5689.
[27] X. Zhou et al., “Reconstructed graph neural network with knowledge
distillation for lightweight anomaly detection,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 35, no. 9, pp. 11817–11828, Sep. 2024.
[28] J. Duan, B. Xiao, S. Wang, H. Zhou, and X. Liu, “ARISE:
Graph anomaly detection on attributed networks via substructure
awareness,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 12,
pp. 18172–18185, Dec. 2024.
[29] H. Nilforoshan and N. Shah, “SliceNDice: Mining suspicious multiattribute entity groups with multi-view graphs,” in Proc. IEEE Int. Conf.
Data Sci. Adv. Analytics (DSAA), Oct. 2019, pp. 351–363.
[30] P. Veličković, W. Fedus, W. L. Hamilton, P. Liò, Y. Bengio, and
R. D. Hjelm, “Deep graph infomax,” in Proc. Int. Conf. Learn. Represent., 2019, pp. 1–17.
[31] F.-Y. Sun, J. Hoffman, V. Verma, and J. Tang, “InfoGraph: Unsupervised
and semi-supervised graph-level representation learning via mutual
information maximization,” in Proc. Int. Conf. Learn. Represent., 2020,
pp. 1–16.
[32] Z. Peng et al., “Graph representation learning via graphical mutual
information maximization,” in Proc. Web Conf., 2020, pp. 259–270.
[33] K. Huang, Y. Guang Wang, M. Li, and P. Liò, “How universal
polynomial bases enhance spectral graph neural networks: Heterophily,
over-smoothing, and over-squashing,” 2024, arXiv:2405.12474.
[34] J. Li, R. Zheng, H. Feng, M. Li, and X. Zhuang, “Permutation equivariant graph framelets for heterophilous graph learning,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 35, no. 9, pp. 11634–11648, Sep. 2024.
[35] M. Li et al., “Guest editorial: Deep neural networks for graphs: Theory,
models, algorithms, and applications,” IEEE Trans. Neural Netw. Learn.
Syst., vol. 35, no. 4, pp. 4367–4372, Apr. 2024.
[36] F. Pukelsheim, “The three sigma rule,” Amer. Statistician, vol. 48, no. 2,
pp. 88–91, May 1994.
[37] H. Liu, S. Shah, and W. Jiang, “On-line outlier detection and data
cleaning,” Comput. Chem. Eng., vol. 28, no. 9, pp. 1635–1647, 2004.
[38] V. Jakhetiya, K. Gu, T. Singhal, S. C. Guntuku, Z. Xia, and W. Lin, “A
highly efficient blind image quality assessment metric of 3-D synthesized
images using outlier detection,” IEEE Trans. Ind. Informat., vol. 15,
no. 7, pp. 4120–4128, Jul. 2019.
[39] S. Afzal, A. Afzal, M. Amin, S. Saleem, N. Ali, and M. Sajid, “A novel
approach for outlier detection in multivariate data,” Math. Problems
Eng., vol. 2021, no. 1, 2021, Art. no. 1899225.
[40] S. Nowozin, B. Cseke, and R. Tomioka, “F-GAN: Training generative
neural samplers using variational divergence minimization,” in Proc.
Adv. Neural Inf. Process. Syst., 2016, pp. 271–279.
[41] B. Wilder, E. Ewing, B. Dilkina, and M. Tambe, “End to end learning
and optimization on graphs,” in Proc. Adv. Neural Inf. Process. Syst.,
2019, pp. 4672–4683.
[42] D. J. MacKay, Information Theory, Inference and Learning Algorithms.
Cambridge, U.K.: Cambridge Univ. Press, 2003.
[43] T. N. Kipf and M. Welling, “Semi-supervised classification with graph
convolutional networks,” in Proc. Int. Conf. Learn. Represent., 2017,
pp. 1–9.
[44] T. Kipf and M. Welling, “Variational graph auto-encoders,” in Proc.
NIPS Workshop Bayesian Deep Learn., 2016, pp. 1–3.

18326

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

[45] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. 8th
IEEE Int. Conf. Data Mining, Dec. 2008, pp. 413–422.
[46] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” in Proc. ACM SIGMOD Int. Conf. Manage.
Data, 2000, pp. 93–104.
[47] V. D. Blondel, J.-L. Guillaume, R. Lambiotte, and E. Lefebvre, “Fast
unfolding of communities in large networks,” J. Stat. Mech., Theory
Exp., vol. 2008, no. 10, Oct. 2008, Art. no. P10008.
[48] D. Arthur and S. Vassilvitskii, “k-means++: The advantages of careful
seeding,” in Proc. 18th Annu. ACM-SIAM Symp. Discrete Algorithms,
2007, pp. 1027–1035.
[49] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
2014, arXiv:1412.6980.
[50] J. Yang, S. Rahardja, and P. Fränti, “Outlier detection: How to threshold
outlier scores?,” in Proc. Int. Conf. Artif. Intell., Inf. Process. Cloud
Comput., 2019, pp. 1–6.
[51] L. Huang et al., “Hybrid-order anomaly detection on attributed
networks,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12,
pp. 12249–12263, Dec. 2023.
[52] J. McAuley, C. Targett, Q. Shi, and A. van den Hengel, “Image-based
recommendations on styles and substitutes,” in Proc. 38th Int. ACM
SIGIR Conf. Res. Develop. Inf. Retr. (SIGIR), 2015, pp. 43–52.
[53] J. Tang, F. Hua, Z. Gao, P. Zhao, and J. Li, “GADBench: Revisiting
and benchmarking supervised graph anomaly detection,” in Proc. Adv.
Neural Inf. Process. Syst., 2024, pp. 1–26.
[54] O. Platonov, D. Kuznedelev, M. Diskin, A. Babenko, and
L. Prokhorenkova, “A critical look at the evaluation of GNNs
under heterophily: Are we really making progress?,” in Proc. Int. Conf.
Learn. Represent., 2023, pp. 1–15.
[55] A. J. Bell and T. J. Sejnowski, “An information-maximization approach
to blind separation and blind deconvolution,” Neural Comput., vol. 7,
no. 6, pp. 1129–1159, Nov. 1995.
[56] R. D. Hjelm et al., “Learning deep representations by mutual information
estimation and maximization,” in Proc. Int. Conf. Learn. Represent.,
2019, pp. 1–24.
[57] J. Yang and J. Leskovec, “Overlapping community detection at scale: A
nonnegative matrix factorization approach,” in Proc. 6th ACM Int. Conf.
Web Search Data Mining, Feb. 2013, pp. 587–596.
[58] X. Chen, S. Chen, J. Yao, H. Zheng, Y. Zhang, and I. W. Tsang,
“Learning on attribute-missing graphs,” IEEE Trans. Pattern Anal.
Mach. Intell., vol. 44, no. 2, pp. 740–757, Feb. 2022.
[59] S. Li, Y. Liu, Q. Chen, G. I. Webb, and S. Pan, “Noise-resilient
unsupervised graph representation learning via multi-hop feature quality
estimation,” in Proc. 33rd ACM Int. Conf. Inf. Knowl. Manage., Oct.
2024, pp. 1255–1265.
[60] Z. Gong et al., “Beyond homophily: Robust graph anomaly detection
via neural sparsification,” in Proc. 32nd Int. Joint Conf. Artif. Intell.,
Aug. 2023, pp. 2104–2113.

Qika Lin (Member, IEEE) received the Ph.D. degree
from Xi’an Jiaotong University, Xi’an, China, in
2023.
He is currently a Research Fellow with the
National University of Singapore, Singapore. He has
published many papers in top-tier journals and conferences, including TKDE, ICDE, ACL, and KDD.
His research interests include multimodal learning,
logical reasoning, and LLM.
Dr. Lin has actively contributed to several journals/conferences as a reviewer or PC member,
including IJCV, TKDE, NeurIPS, and ACL. He also served as a Guest Editor
of IEEE T RANSACTIONS ON C OMPUTATIONAL S OCIAL S YSTEMS (TCSS).

Bin Shi received the B.Eng. and Ph.D. degrees from
the School of Computer Science and Engineering,
Beihang University, Beijing, China, in 2013 and
2019, respectively.
He currently serves as an Associate Professor
with SPKLSTN Laboratory, School of Computer
Science and Technology, Xi’an Jiaotong University,
Xi’an, China. His research interests include graph
data mining, large language models, and machine
learning in open-world environments [with noise,
bias, and out-of-distribution (OOD)].

Chen Chen received the Ph.D. degree from Arizona
State University, Tempe, AZ, USA, in 2019.
She is currently an Assistant Professor from the
Computer Science Department, University of Virginia (UVA), Charlottesville, VA, USA. Before that,
she was a Research Assistant Professor at Biocomplexity Institute, UVA, and a Software Engineer at
Google. Her research has appeared in top-tier conferences (including NeurIPS, ICML, ICLR, KDD,
AAAI, IJCAI, SIGIR, WSDM, ICDM, SDM, etc.)
and prestigious journals (including PNAS, IEEE
TKDE, ACM CSUR, ACM TKDD, KAIS, and SIAM SAM). Her research
interests include the connectivity of complex networks, which have been
applied to address pressing challenges in various high-impact domains, including social media, bioinformatics, recommendation, and critical infrastructure
systems.
Dr. Chen has received several awards, including “Bests of KDD,” “Bests
of SDM,” and Rising Star in EECS.

Zhen Peng received the B.Eng. degree from the
School of Software Engineering, Xi’an Jiaotong
University, Xi’an, China, in 2017, and the Ph.D.
degree from the School of Computer Science and
Technology, Xi’an Jiaotong University, in 2023.
She is currently an Assistant Professor with Xi’an
Jiaotong University. Her research interests include
graph machine learning and its applications especially graph anomaly detection and social network
analysis.

Bo Dong (Member, IEEE) received the Ph.D. degree
in computer science and technology from Xi’an
Jiaotong University, Xi’an, China, in 2014.
From 2014 to 2017, he did postdoctoral research
in control science and engineering at Xi’an Jiaotong University, where he is currently a Professor
with SPKLSTN Laboratory. His main research interests include large language models and machine
learning.

Yunfan Wang received the B.Eng. degree in computer science and technology and the B.Eco. degree
in economics, and the M.Eng. degree in computer science and technology from Xi’an Jiaotong
University, Xi’an, China, in 2021 and 2024, respectively. He is currently pursuing the Ph.D. degree in
computer science with the University of Virginia,
Charlottesville, VA, USA.
His research interests include machine learning
systems, large language models, and graph data
mining.

Chao Shen received the B.S. degree in automation
and the Ph.D. degree in control theory and control
engineering from Xi’an Jiaotong University, Xi’an,
China, in 2007 and 2014, respectively.
He is currently a Professor with the Faculty
of Electronic and Information Engineering, Xi’an
Jiaotong University. His current research interests include AI security, insider/intrusion detection,
behavioral biometrics, and measurement and experimental methodology.
PAPER_TEXT
