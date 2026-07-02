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
# [693] Graph Neural Networks for Graphs With Heterophily: A Survey
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
编号：693
题名：Graph Neural Networks for Graphs With Heterophily: A Survey
年份：2026
DOI：10.1109/tkde.2026.3680353
来源：IEEE Transactions on Knowledge and Data Engineering
PDF：paper/10.1109_TKDE.2026.3680353.pdf
已有粗分类：数据集、基准、综述与开源工具
二级关联：图学习、知识图谱与威胁情报
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\693.txt
- 原始字符数：118367
- 本次发送字符数：118367
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

4385

Graph Neural Networks for Graphs With
Heterophily: A Survey
Xin Zheng , Yi Wang , Yixin Liu , Ming Li , Member, IEEE, Miao Zhang , Di Jin ,
Philip S. Yu , Fellow, IEEE, and Shirui Pan , Senior Member, IEEE
(Survey Paper)

Abstract—Recent years have witnessed fast developments of
graph neural networks (GNNs) that have benefited myriad graph
analytic tasks and applications. Most GNNs rely on the homophily
assumption that nodes belonging to the same class are more likely to
be connected. However, as a ubiquitous graph property in numerous real-world scenarios, heterophily, i.e., nodes with different labels tend to be linked, significantly limits the performance of tailormade homophilic GNNs. Hence, GNNs for heterophilic graphs are
gaining increasing research attention to enhance graph learning
with heterophily. In this paper, we provide a comprehensive review
of GNNs for heterophilic graphs. Specifically, we propose a systematic taxonomy that governs existing heterophilic GNN models,
along with general summaries and detailed analyses. Furthermore,
we discuss the relationship between heterophily and various graph
research domains, aiming to facilitate the development of more
effective GNNs across a spectrum of practical applications and
learning tasks in the graph research community. In the end, we
point out potential directions to advance and inspire future research
and applications on heterophilic graph learning with GNNs.
Index Terms—Graph neural networks, heterophily, graph
representation learning, message passing.
Received 28 May 2025; revised 14 March 2026; accepted 29 March 2026.
Date of publication 2 April 2026; date of current version 2 June 2026. The
work of Shirui Pan was supported in part by the Australian Research Council
(ARC) under Grant FT210100097 and Grant DP240101547. The work of Yixin
Liu was supported in part by the Australian Research Council (ARC) under
Grant DE260101172. The work of Yi Wang was supported by the Research
Grants Council of Hong Kong CityU under Grant 11301224. The work of
Ming Li was supported from National Natural Science Foundation of China
under Grant 62536006. The work of Philip S. Yu was supported in part by
NSF under Grant III-2106758 and Grant POSE-2346158. Recommended for
acceptance by S. Whang. (Xin Zheng and Yi Wang contributed equally to this
work.) (Corresponding authors: Ming Li; Shirui Pan.)
Xin Zheng is with the School of Computing Technologies, RMIT University,
Melbourne, VIC 3000, Australia (e-mail: xin.zheng2@rmit.edu.au).
Yi Wang is with the Department of Mathematics, City University of Hong
Kong, Hong Kong, SAR, China (e-mail: ywan72@cityu.edu.hk).
Yixin Liu and Shirui Pan are with the School of Information and Communication Technology, Griffith University, Southport, QLD 4215, Australia (e-mail:
yixin.liu@griffith.edu.au; s.pan@griffith.edu.au).
Ming Li is with the Zhejiang Key Laboratory of Intelligent Education Technology and Application, Zhejiang Normal University, Jinhua 321004, China
(e-mail: mingli@zjnu.edu.cn).
Miao Zhang is with the School of Computer Science and Technology,
Harbin Institute of Technology (Shenzhen), Shenzhen 518055, China (e-mail:
zhangmiao@hit.edu.cn).
Di Jin is with the School of Computer Science and Technology, Tianjin
University, Tianjin 300072, China (e-mail: jindi@tju.edu.cn).
Philip S. Yu is with the Department of Computer Science, University of Illinois
at Chicago, Chicago, IL 60607 USA (e-mail: psyu@uic.edu).
This article has supplementary downloadable material available at
https://doi.org/10.1109/TKDE.2026.3680353, provided by the authors.
Digital Object Identifier 10.1109/TKDE.2026.3680353

I. INTRODUCTION
RAPHS are pervasively structured data and have been
widely used in many real-world scenarios, such as social
networks [1], [2], knowledge bases [3], traffic networks [4],
and recommendation systems [5], [6]. Recently, graph neural
networks (GNNs) have achieved remarkable success with powerful learning ability and become prevalent models to tackle
various graph analytical tasks, such as node classification, link
prediction, and graph classification [3], [7], [8], [9].
While a large number of GNNs with diverse architectures
have been designed [10], [11], [12], [13], [14], [15], the majority
of them follow the homophily assumption, i.e., nodes with
similar features or same class labels are linked together. For
example, in citation networks, a study usually cites reference
papers from the same research area [16]. However, real-world
graphs do not always obey the homophily assumption but show
an opposite property, i.e., heterophily that linked nodes have
dissimilar features and different class labels [17], [18], [19], [20],
[21]. For instance, in online transaction networks, fraudsters
are more likely to build connections with customers instead of
other fraudsters [22]; in dating networks, most people prefer
to date with people of the opposite gender [23]; in molecular
networks, protein structures are more likely composed of different types of amino acids that are linked together [24]. The
examples of homophilic and heterophilic graphs are provided
in Fig. 1 to illustrate their difference visually. Importantly,
such heterophily restricts the learning ability of existing homophilic GNNs on general graph-structural data, resulting in
significant performance degradation on heterophilic graphs [23],
[24], [25].
Core Challenges of GNNs for Heterophily: We attribute
the performance degradation to the uniform message passing
framework under the homophily setting. The procedure of this
framework can be summarized as: first aggregating the messages extracted from local neighbor nodes, then updating the
final ego node (the current central node itself) representations
with aggregated neighbor messages. Nevertheless, due to the
heterophily property of graphs, this mechanism poses significant
challenges for the development of heterophilic GNNs, primarily
manifesting in two aspects:
r Challenge-1. Undiscovered Non-local Neighbors: Guided
by homophily, neighbor aggregation in homophilic GNNs

G

1041-4347 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

4386

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

Fig. 1. Examples of homophilic and heterophilic graphs (Left: (a) a citation
network; Right: (b) an online transaction network).

restricts information extraction to the proximal local
topology of graphs. When applied to graphs with heterophily, it fails to explore non-local topology, where heterophilic nodes of the same class are typically situated
at long-term distances. This poses a significant challenge
in identifying and learning informative nodes with high
structural and semantic similarities on heterophilic graphs.
r Challenge-2. Indistinguishable Node Representation
Learning: Homophilic GNNs employ uniform local
neighbor aggregation and update the central node
representation when they are typically similar and share
the same labels. Consequently, on heterophilic graphs,
the discrepancy between similar non-local neighbors
and dissimilar local neighbors can not be effectively
captured. This results in critical challenges in learning
discriminative node representations with distinguishable
heterophily information through diverse customized
message passing.
In light of these challenges, recently, an increasing number
of researchers have started turning their attention to the study
of GNNs with heterophily. The research focus is sufficiently
broad, from heterophilic graph data exploration [26], [27], [28]
to various technical algorithm development [17], [19], [21],
[25], [29], [30], [31].
Importance of Developing Heterophilic GNNs: Heterophilic
graph learning with GNNs is becoming an upward trending
research topic and it shows closely tied connections with diverse domains in graph research. The compelling significance
of GNN development for heterophilic graphs is underscored by
the following aspects:
r Enhancing the understanding of complex and diverse heterophily graphs: Graph-structure data with the heterophilic
property presents great complexity and diversity, and it is
prevalent across various real-world application scenarios,
ranging from daily-life personal relationships to scientific
chemical molecular study. A thorough and ongoing exploration of heterophily graph data would significantly
enhance the understanding of complex and diverse heterophily graphs, thereby providing valuable guidance for
the development of GNN models and advancements in
heterophily graph learning.
r Advancing heterophilic graph analysis and learning: Heterophilic graph analysis and learning tasks are still open
and promising research topics in development, while

numerous challenges need to be tackled for designing
heterophilic GNN models with expressive performance,
robustness, and generalization ability. The advancement
of heterophilic GNNs is pivotal for unlocking the full potential of heterophilic graph analysis in addressing various
practical graph learning tasks covering both heterophilic
node representations and graph structures.
r Adapting with versatility in heterophilic GNN development: As heterophilic graphs exist prevalently and show
close connections with various graph research domains,
e.g., over-smoothing and anomaly detection. Hence, developing specialized heterophilic GNN architectures and
learning techniques would be pivotal in expanding the versatility and adaptability of GNN models, unleashing power
of heterophilic GNNs in cross graph research domains and
applications.
Distinctions from Existing Surveys: This study constitutes
an expansion of the domain survey initially released on arXiv
(preprint 2202.07082v1), the first comprehensive review in this
field. Notably, since the publication of this seminal survey in
2022, we have witnessed exponential growth in related research.
Available statistics indicate that the volume of new literature
generated between 2022 and 2024 exceeded fivefold compared
to the preceding five-year period. While several review articles [32], [33], [34] have emerged during this timeframe, our
work demonstrates distinctive value through the following dimensions:
r In contrast to the prior efforts by Zhu et al. [32] and
Gong et al. [33] largely limited to pre-2023 methods, our
survey presents three key advances: (1) systematic integration of cutting-edge developments through March 2025,
(2) proposal of a more explicit taxonomy for heterophily
GNNs with independent significance in categorization,
and (3) complementary technical visualizations including
schematic framework diagrams and inductive mathematical formulations.
r While the recent domain handbook by Luan et al. [34]
provides broad literature coverage, including many 2024
studies (primarily ArXiv preprints), our survey reveals twofold differentiation:
(1) classification clarity – contrasting their simplified listing paradigm, we establish a clear hierarchical classification taxonomy; (2) temporal completeness - extending beyond their Q2-2024 cutoff, our survey incorporates critical
March 2025 advancements.
In this paper, we present a comprehensive and systematic
review of GNNs for heterophilic graphs, aiming to provide a general blueprint of heterophilic graph research. It can be beneficial
to establish connections and make comparisons among different
heterophilic GNN methods, leading to an in-depth understanding of how different methods tackle the challenges of heterophily
learning. We are expecting that our survey will significantly
inspire and facilitate the development of heterophilic graphs1 .
The contributions of our work are summarized as follows:
1 Our preprint of this article [35] has attracted more than 420 citations, showing
a strong uptrend of this research topic.

ZHENG et al.: GNNS FOR GRAPHS WITH HETEROPHILY: A SURVEY

r Comprehensive Overview: We provide a comprehensive
overview of current heterophilic GNNs in terms of data,
algorithms, and applications. We provide detailed descriptions of each model type, along with the necessary comparison and the gist summary.
r Systematic Taxonomy: We provide a systematic taxonomy
of heterophilic GNNs and categorize existing methods into
three classes, i.e., non-local neighbor extension methods,
GNN architecture refinement methods, and hybrid methods.
r Thorough Discussion: We provide a thorough discussion
of the correlation between graph heterophily and various
graph research domains, including the relation between
graph heterophily and model robustness, over-smoothing,
and graph anomaly detection.
r Future Directions: We suggest promising future research
directions and discuss the limitations of existing heterophilic GNNs from multiple perspectives, namely interpretability, robustness, scalability, and heterophilic graph
data exploration.
The remainder of this article is organized as follows. Section II
defines the related concepts and provides notations used in
this survey. Section III describes the framework of heterophilic
GNNs and provides the taxonomy. Sections IV–VI review three
categories of heterophilic GNNs methods respectively. Section VII discusses heterophily GNNs on diverse graphs and
the correlation between heterophily and diverse graph research
domains. Section VIII analyzes the unexplored challenges and
potential future directions. Section IX concludes this article in
the end. More details of real-world heterophilic graph dataset
benchmarks, open-source codes, and the overall development
timeline of heterophilic GNNs can be found in the Appendix,
online available.

II. PRELIMINARY
A. Notations
Let G = (V, E) be an undirected, unweighted graph where
V = {v1 , . . . , v|V| } is the node set and E ∈ V × V is the edge
set. The neighbor set of node v is denoted as N (v) = {u :
(v, u) ∈ E}. The node features are represented by a feature
matrix X ∈ R|V|×d , where the i-th row xi ∈ Rd is the feature
vector of node vi and d is the number of feature dimensions. Connectivity is represented by the adjacency matrix A ∈ {0, 1}n×n .
For any matrix A, we use Auv to refer to the scalar value at the
(u, v) location. The graph Laplacian is defined as L = D − A,
where D ∈ Rn×n is the diagonal degree matrix. Due to its
generalization ability [36], the symmetric normalized Laplacian
is often used, which is defined as L̃ = D−1/2 LD−1/2 . Another
option is random walk normalization: L̃ = D−1 L. Note that normalization could also be applied to the adjacency matrix. Their
relationship can be derived as L̃ = I − Ã, where I is the identity
matrix. Through eigendecomposition, L can be expressed as
L̃ = UΛUT , where each column of U ∈ Rn×n represents an
eigenvector of L, Λ is the diagonal matrix whose diagonal
elements are the corresponding eigenvalues (i.e., Λii = λi ).

4387

B. Graph Neural Networks
Generally, GNNs adopt the message passing mechanism,
where each node representation is updated by aggregating the
messages from local neighbor representations, and then combining the aggregated messages with its ego representation [10].
The updating process of the l-th GNN layer for each node v ∈ V
can be described as:


(l)
{h(l−1)
: u ∈ N (v)} ,
m(l)
v = AGGREGATE
u


(l)
h(l−1)
,
(1)
h(l)
, m(l)
v = UPDATE
v
v
(l)

(l)

where mv and hv stand for the message vector and the
representation vector of node v at the l-th layer, respectively. And
AGGREGATE(·) and UPDATE(·) are aggregation function
(e.g., mean, LSTM, and max pooling) and update function (e.g.,
linear-layer combination) [8], respectively. Given the input of
the first layer as H(0) = X, the learned node representations
(l)
at each layer of L-layer GNN can be denoted as H(l) = [hv ]
for v = (1, . . . , |V|) and l = (1, . . . , L). For node classification
task, the final node representation H(L) would be fed into a
classifier network (e.g., a fully-connected layer) to generate the
predictions for classes.
C. Spectral Graph Convolution
A graph convolution operation is defined in the Fourier domain such that



(2)
f1 ∗ f2 = U (UT f1 )  UT f2 ,
where  is the element-wise product, and f1 /f2 are two signals
defined on nodes. It follows that a node signal f2 = X is filtered
by spectral signal fˆ1 = UT f1 = g as
(l−1)
= U[g(Λ)  (UT h(l−1)
)] = Ug(Λ)UT h(l−1)
,
h(l)
v = g(L̃)hv
v
v
(3)
where g is known as frequency response function. Therefore,
the objective of spectral methods is to learn a function g(·). In
simpler terms, g(·) can be seen as a way to re-weight signals
of different frequencies (or eigenvalues). Eigenvalues represent
the smoothness or frequency of the corresponding eigenvectors.
Consequently, assigning greater weight to smaller eigenvalues
retains more low-frequency information, while assigning greater
weight to larger eigenvalues retains more high-frequency information. In general, FLP = I + D−1/2 AD−1/2 = ( + 1)I −
L is a low-pass filter, while FHP = I − D−1/2 AD−1/2 =
( − 1)I + L denotes high-pass filter.

D. Measure of Heterophily & Homophily
In general, heterophily and homophily of a graph G = (V, E)
can be measured by following metrics: node homophily [37],
edge homophily [24], class homophily [27], adjusted homophily [38], and unbiased homophily [39].
Node homophily and edge homophily are two essential measures. Concretely, the node homophily is the average proportion

4388

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

of the neighbors with the same class of each node:
Hnode =

1  |{u ∈ N (v) : yv = yu }|
.
|V|
|N (v)|

(4)

v∈V

The edge homophily is the proportion of edges connecting two
nodes with the same class:
Hedge =

|{(v, u) ∈ E : yv = yu }|
.
|E|

(5)

To alleviate the sensitivity issue of Hnode and Hedge on the
node class number, the class homophily measures the average
proportion of neighbors with the same class across all nodes
of each class while taking into account the constraint of class
proportions, that is

Fig. 2.

Categorization of heterophily GNNs.

F. Mainstream Heterophily Learning Task

The main objective learning task of heterophily GNNs is semisupervised node classification. In this task, we have a training
C
graph G = (X, A, Y), where X ∈ RN ×d denotes N nodes with
nc
1 
v:yv=c |{u ∈ N (v) : yv = yu }|
−
,
Hclass =
d-dimensional features, and A ∈ RN ×N denotes the adjacency
C − 1 c=1
|V|
v:yv =c |N (v)|
+
(6) matrix indicating the edge connection. Assuming each node v
where nc = |{u : yu = c}| denotes the node number of class c. belongs to one out of C classes, only a part of nodes are provided
Platonov et al. [38] and Mironov et al. [39] have progressively with labels as Yv ∈ YL = {1, . . . , C} in the training node set.
advanced homophily measurement by introducing metrics that The goal of the task is to predict the classes of nodes whose
fulfill an increasing number of desirable properties. Their first labels are not given.
Concretely, given a heterophily GNN model parameterized
study [38] proposed adjusted homophily, that is
by
θ, denoting as GNNθ (·). For semi-supervised node class

2
C
classification
task, the cross-entropy loss is minimized to learn
Hedge − c=1
v:yv =c |N (v)|/(2|E|)
the
optimal
GNN
parameters θ over all labeled nodes as:
,
(7)
Hadj =

2
1− C
|N
(v)|/(2|E|)


v:yv =c
c=1
min Lcross-entropy Ŷ, Y , where Ŷ = GNNθ (X, A), (9)
θ
which is comparable across datasets with varying class statistics.
And recent research [39] introduced unbiased homophily
where Ŷ = [Ŷv ]v∈V denotes GNN predicted node labels and
√
i<j ( cii cjj − cij )
Y
= [Yv ]v∈V is the ground-truth node labels.
Hun =
,
(8)
√
(
c
c
+
c
)
ii
jj
ij
i<j
where cii = |{(v, u) ∈ E : yv = yu = i}|/|E| and cij =
|{(v, u) ∈ E : {yv , yu } = {i, j}}|/(2|E|) for i = j. This metric
is designed for reliable application across differing label
distributions that satisfies the vast majority of these properties.
Remark: Node homophily Hnode and edge homophily Hedge
are still popular measurement methods among recent works.

III. GNNS WITH HETEROPHILY: FRAMEWORK AND
TAXONOMY
In this section, we provide a unified framework of heterophilic
GNNs, and further categorize it from the lens of the message
passing mechanism.

E. Real-World Benchmarks

A. Framework of Heterophilic GNNs

Benchmark datasets are fundamental for evaluating model
performance. The field was initially shaped by Pei et al. [37],
who introduced six benchmark heterophilic graphs—Cornell,
Texas, Wisconsin, Chameleon, Squirrel, and Actor—that remain
the most widely adopted in current literature, despite their generally small scale. Building upon these, Lim et al. [26], [27]
proposed a series of large-scale datasets, including ArXiv-Year,
Snap-Patents, Penn94, Pokec, Genius, Deezer-Europe, TwitchGamers, and YelpChi. More recently, work in [40] identified
limitations such as small scale, class imbalance, and class
leakage in earlier widely-used datasets, and subsequently introduced five high-quality alternatives: Roman-Empire, AmazonRatings, Minesweeper, Tolokers, and Questions. A detailed
description of these datasets is provided in Appendix B, online
available.

Following the general message passing principle for GNN
model design, heterophilic GNNs focus on customizing the
neighborhood aggregation and feature update schemes that
specifically model the heterophily property. In contrast to homophilic GNNs, heterophilic GNNs exhibit distinct characteristics in three key design principles:
P1. Non-locality of Neighbor Sets: Incorporating information
from non-local neighbors that may share the same class label as
the central node;
P2. Class Distinguishability: Ensuring the aggregation process to effectively distinguish the class labels from both local
and non-local neighbors;
P3. Depth Fusion of Multi-layer Information: Integrating
hierarchical messages from different inter layers of GNNs for
capturing comprehensive heterophily property.

ZHENG et al.: GNNS FOR GRAPHS WITH HETEROPHILY: A SURVEY

4389

B. Taxonomy of GNNs With Heterophily
According to the above three-fold design principles in heterophily instructed neighbor aggregation and feature updating,
heterophilic GNNs can be categorized into three groups, including:
(1) Non-local neighbor extension methods ← P1.
(2) GNN architecture refinement methods ← P2 & P3.
(3) Hybrid methods ← P1, P2 & P3.
More fine-grained categorizations of these methods are briefly
discussed below and shown in Fig. 2.
Non-Local Neighbor Extension Methods attempt to improve
node representation by incorporating higher-order neighbor
nodes that share labels during the message-passing process. This
kind of methods break the locality limitations of N (v) in (1) by
reconstructing the non-local neighbor set from two perspectives:
high-order neighbor mixing and potential neighbor discovery.
Specifically, these methods focus on discovering appropriate
neighbors from multi-hops nodes and redefining neighbor sets as
Np (v) = {u : dist(u, v) ≤ p} in the message aggregation stage
in (1), where dist(u, v) denotes the distance method to measure
the distance between nodes u and v. p is a threshold to limit the
number of neighbors. In particular, Np (v) can be degenerated
into N (v) when the metric function dist(·) is the shortest path
distance and p = 1.
GNN Architecture Refinement Methods boost the expressive
ability of GNNs by facilitating message passing that distinguishes between similar and dissimilar neighbors or by deeply
fusing multi-layer information. Specifically, focusing on the
crafted architecture design of message aggregation and feature
updates, these methods are categorized into identifiable message aggregation methods and inter-layer combination methods. Among these, identifiable message aggregation methods
have gained significant attention. Their objective is to allocate
appropriate weights in the message aggregation process, aiming
to strengthen the fusion of homophilic information while mitigating the fusion of heterophilic information. With a focus on
weight assignment schemes from various perspectives, existing
methods can be further classified into three types: edge-related
weight, feature-related weight, and hybrid weight.
Hybrid Methods can be taken as the combination of non-local
neighbor extension methods and GNNs architecture refinement
methods. Typically, hybrid methods first construct an appropriate neighbor set through non-local neighbor extension, and then
refine the GNN architectures from two perspectives: (1) locallevel incorporation, that focuses on intra-layer heterophilyguided message passing, and (2) global-level incorporation, that
enhances effective inter-layer heterophily information transfer
throughout the entire GNN architecture.
Discussion: Different heterophilic GNNs exhibit distinct
properties. The fundamental concept of non-local neighbor
extension methods is quite straightforward and simple to implement, as it directly models and captures the similarity relationships between nodes to enhance the homophily of local neighborhoods; however, for large-scale graphs, it can be
memory-intensive to traverse the entire graph in order to model
the similarity between each pair of nodes. GNN architecture

Fig. 3. Schematic diagram of high-order neighbor mixing method and potential neighbor discovery method.

refinement methods focus on mitigating the impact of local heterophilic information during the message passing process. This
primarily involves further refinement of message aggregation
and feature updates for the heterophilic design. However, the
challenge lies in how to customize the heterophilic message
passing mechanism with only a limited number of observable
homophilic or heterophilic relationships. Hybrid methods combine the advantages of both non-local neighbor extension and
GNN architecture refinement. Nevertheless, a major challenge is
devising a strategy for seamlessly integrating these approaches
into the message-passing process.
IV. HETEROPHILIC GNNS WITH NON-LOCAL NEIGHBOR
EXTENSION
Under the uniform message passing framework of homophilic
GNNs, the neighborhood is usually defined as the set of all
neighbors one-hop away (e.g., GCN), which means only messages from proximal nodes in a graph are aggregated. However,
such a local neighborhood definition might not be appropriate
for heterophilic graphs, where nodes belonging to the same
class exhibit high structural similarity but can be farther away
from each other. In light of these, current heterophilic GNNs
attempt to extend the local neighbors to non-local ones primarily
through two schemes: high-order neighbor mixing and potential
neighbor discovery. As a result, the representation ability of
heterophilic GNNs can be improved significantly by capturing
the important features from distant and informative nodes. The
pipelines of two example methods are given in Fig. 3, and a
summary of the non-local neighbor extension works is illustrated
in Table I.
A. High-Order Neighbor Mixing
Higher-order neighbor mixing allows the ego node to receive
latent representations from their local one-hop neighbors and
from further k-hop neighbors, so that the heterophilic GNNs
can mix latent information from neighbors at various distances.
Formally, the k-hop neighbor set is defined as
Nk (v) = {u : dist(u, v) = k},

(10)

where dist(u, v) measures the shortest path distance between
nodes u and v. In addition, how to mix the information from the
different k-hop neighbor sets is an important research point of
higher-order neighbor mixing methods.

4390

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

TABLE I
SUMMARY OF NON-LOCAL NEIGHBOR EXTENSION METHODS. ‘STRUCTURE-BASED DISTANCE’, ‘FEATURE-BASED DISTANCE’, AND ‘HYBRID DISTANCETANCE’
TAKE THE STRUCTURE-BASED SCHEME, FEATURE-BASED SCHEME, AND HYBRID SCHEME AS THE DISTANCE METRIC FOR POTENTIAL NEIGHBOR DISCOVERY,
RESPECTIVELY.

TABLE II
SUMMARY OF GNN ARCHITECTURE REFINEMENT METHODS. ‘FEATURE-RELATED’, ‘EDGE-RELATED’ AND ‘HYBRID’ RESPECTIVELY
REPRESENT WEIGHT
√
ASSIGNMENT SCHEMES THAT WORK ON NODE FEATURE, EDGES, AND BOTH OF THEM FOR ADAPTIVE MESSAGE AGGREGATION. ‘ ’ AND ‘✗’ INDICATE WHETHER
TO INCLUDE THE ACCORDING SCHEMES, RESPECTIVELY.

ZHENG et al.: GNNS FOR GRAPHS WITH HETEROPHILY: A SURVEY

4391

TABLE III
SUMMARY OF HYBRID EXTENSION METHODS. ‘HN’ AND ‘PN’ MEAN ‘HIGH-ORDER NEIGHBORS MIXING’ AND ‘POTENTIAL NEIGHBORS DISCOVERY’,
RESPECTIVELY. ‘IA’ AND ‘IC’ MEAN ‘IDENTIFIABLE MESSAGE AGGREGATION’ AND ‘INTER-LAYER COMBINATION’, RESPECTIVELY. ‘LOCAL-LEVEL’ AND
‘GLOBAL-LEVEL’ INDICATE WHETHER THE GNN ARCHITECTURE REFINEMENT METHOD, INCORPORATING NEIGHBOR EXTENSION TECHNOLOGY, PRIMARILY
FOCUSES ON HETEROPHILIC DESIGN WITHIN THE MESSAGE-PASSING LAYER OR ENHANCES EFFECTIVE INTER-LAYER INFORMATION TRANSFER THROUGHOUT
THE ENTIRE NETWORK ARCHITECTURE, RESPECTIVELY.

Typically, MixHop [41] is a representative method that aggregates messages from multi-hop neighbors. Apart from onehop neighbors, MixHop also considers two-hop neighbors for
message propagation. After that, the messages acquired from
different hops are encoded by different linear transformations
and then mixed by concatenation. The l-th layer of MixHop for
each node v ∈ V can be described as


(l)
: u ∈ Nk (v) ,
mv,k = AGGREGATE(l) h(l−1)
u


(l)
(l)
hv,k = UPDATE(l) h(l−1)
, mv,k ,
v
h(l)
v =

(l)
k=2 hv,k ,

(11)

where k=2 means column-wise combination of information
from 2-hop neighbors. It can be noted that cross-level information fusion of MixHop is performed after the feature aggregation
and updating among the same hop neighbors.
Another perspective for cross-level information fusion is to
merge cross-hop neighbors before the feature aggregation stage,
and then aggregate and update multi-hop neighbors’ features simultaneously. The most representative method is TDGNN [42],
which uses a tree decomposition method to disentangle neighborhood information in different layers and focus on adjusting
the aggregation stage in (1) to promote information fusion
among different layers, modeled as


K

(l)
(l)
(l−1)
hu
:u∈
Nk (v)
,
mv = AGGREGATE
k=1

(12)
where K is the highest-hop setting the collection neighbor sets.
Recently, Ordered GNN [43] proposes to order the messages
passing into the node representation, with specific blocks of
neurons targeted for message passing within specific hops. This
is achieved by aligning the hierarchy of the rooted-tree of a
central node with the ordered neurons in its node representation.
Based on simple design in the spectral domain, EvenNet [44]
discards messages from odd-order neighbors inspired by balance
theory, deriving a graph filter with only even-order terms, which
can be generalized to graphs of different homophily.
In summary, the high-order neighbor mixing methods
straightforwardly include higher-order neighbors in local neighbor sets and devise an appropriate combination scheme to effectively integrate multi-order neighborhood information. Its

objective is to alleviate the impact of local heterophily by
incorporating richer homophilic information from higher-order
neighborhoods.
B. Potential Neighbor Discovery
Compared to high-order neighbor mixing methods directly
utilizing the inherent structural information from graphs, potential neighbor discovery methods reconsider the definition of
neighbors in heterophilic graphs and build innovative structural
neighbors through the entire topology exploration with heterophily. Apart from the original neighbor set, these methods
construct a new potential neighbor set that can be further formalized as
Nρ (v) = {u : dist(v, u) < ρ},

(13)

where dist(u, v) is a metric function that measures the distance
between nodes u and v in a specifically defined latent space and
ρ is a threshold to limit the number of neighbors. It is evident
that distance measurement plays a pivotal role in identifying
suitable potential neighbors. Current methods can be categorized
into three main types based on the focal variables of distance
measurement: structure-based distance, feature-based distance,
and hybrid distance.
1) Structure-Based Distance: Structure-based distance
methods typically search for potential neighbors that meet
measurement criteria within the geometric relationship latent
space, which is defined by prior information about the graph
topology. Typically, Geom-GCN [37] maps the input graph to a
continuous latent space and defines the geometric relationships,
i.e., split 2D Euclidean geometry locations, as the criteria to
discover potential neighbors. Apart from inherent neighbors
in original input graphs, neighbors that conform to the
defined geometric relationships also participate in the message
aggregation of GCN. Specifically, based on the graph and latent
space, a structural neighborhood is built as ({N (v), Nρ (v)}, τ )
underlying the relational operator τ , where N (v) is the set of
adjacent nodes of v in the graph, Nρ (v) is the set of potential
neighbors from which the distance to v is less than a pre-given
parameter ρ in the latent space, described as
Nρ (v) = {u : hu − hv 2 < ρ},

(14)

4392

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

where hu and hv are the representations for nodes u and v. · 2
is the Euclidean norm to measure relative positions between two
nodes. ρ is determined from zero until the average cardinality
of Ns (v) equals that of N (v), ∀v ∈ V, that is, when the average
neighborhood sizes in the graph and latent spaces are the same.
2) Feature-Based Distance: Different from the structurebased distance methods that use structural information to determine potential neighbor nodes, feature-based distance methods
determine connection relationships based on feature similarity.
For instance, U-GCN [45] and SimP-GCN [46] choose top k
similar node pairs in terms of feature-level cosine similarity for
each ego node to construct the neighbor set through the kNN
algorithm. The potential neighbor set for this method can be
built as
NK (v) = {u : TopK(Cos(hu , hv ), K)},

(15)

where Cos(·, ·) is usually defined the cosine similarity function,
K is the number of nearest neighbors set manually, TopK(·)
denotes a pooling operation for discovering potential neighbors
with K highest similarity. The recent work HES-GSL [47] still
determines relationships of node pairs through cosine similarity,
and further designs homophily-enhanced self-supervision to
provide more supervision for similarity learning.
3) Hybrid Distance: Recent works increasingly emphasize
the comprehensive consideration of structural and node feature
information in potential neighbor discovery. These methods
focus more on the potential message passing among global
homophily neighbors in the graph. Typically, HOG-GCN [52]
and GloGNN [53] design similarity calculation modules to
capture the correlations between global nodes through both
topological and attribute information. Specifically, HOG-GCN
constructs a homophily degree matrix with the label propagation
technique to explore the extent to which a pair of nodes belong
to the same class in the entire heterophilic graph from the
perspective of topology space. By involving the class-aware
information during the propagation process, intra-class nodes
with higher heterophily (i.e., lower homophily degree) would
contribute more to the neighbor aggregation than underlying
inter-class nodes. More simplified than HOG-GCN, GloGNN
directly measures potential correlations between global nodes
in terms of both feature attribute similarity and topology similarity by further regularizing node representations with nodes’
multi-hop reachabilities. In general, the potential neighbors set
can be defined as
N (v) = NT (v) ∩ NS (v),

(16)

T
where NT (v) = {u : h̃u h̃T
v = 0} and NS (v) = {u : ĥu ĥv <

ρ} are potential neighbor sets defined by measuring node correlations in terms of topology similarity and feature similarity, ∩
is the intersection operation, and h̃u and ĥu are representations
of node u through topology structure information (i.e., A) and
node attribute information (i.e., X), respectively.
Furthermore, SE-GSL [55] offers an effective measure of
the information embedded in an arbitrary graph and structural
diversity (where NT (v) is characterized by both the kNN structure and the original topology structure) and presents a novel
sampling-based mechanism for restoring the graph structure via

node structural entropy distribution. It increases the connectivity
among nodes with larger uncertainty in lower-level communities. GraphTU [86] offers a probabilistic approach to exploring
potential neighbors. A key observation in this research is that
the statistical variances based features and topology information
within local neighborhoods can be effectively harnessed to extend the training distribution, creating novel potential neighbor
sets through a non-parametric method. This approach is particularly valuable for addressing heterophily within the entire graph,
especially in the case of minor class nodes. To reveal attribute
relationships among nodes in the entire graph, GOAL [21]
augments the existing graph by constructing a fully connected
graph through a graph completion process. This augmentation
considers two modes: homophilic connections and heterophilic
connections. An important aspect involves developing a method
to distinguish between connections that reflect a tendency for
homophily and those that indicate heterophily. This distinction
is made based on the Connected Structure Difference (CSD)
computed between connected node pairs and randomly selected
node pairs, ultimately facilitating the optimization of the complemented graph.
In summary, potential neighbor discovery methods focus on
identifying homophilic neighbors among high-order neighbors
and incorporating them into local neighbor sets to enhance
homophilic message-passing. By measuring the similarity of
node features with different distance calculation schemes, potential neighbor discovery methods are able to effectively identify
potential homophilic neighbors that share the same class labels.
V. HETEROPHILIC GNN ARCHITECTURE REFINEMENT
General GNN architectures in (1) contain two essential components: the aggregation function AGGREGATE(·) to integrate information from the discovered neighbors, and the update function UPDATE(·) to combine the learned neighbor
messages with the initial ego representation. Given the original
local neighbors and the extended non-local neighbors on heterophilic graphs, existing GNN architecture refinement methods
contribute to fully exploiting the neighbor information from the
following aspects by accordingly revising AGGREGATE(·)
and UPDATE(·): (1) Identifiable message aggregation discriminates and enhances the messages of similar neighbors from
dissimilar ones; (2) Inter-layer combination emphasizes the
effect of different propagation ranges (i.e., the number of GNN
layers) on node representation learning. All these two aspects
come to the same destination: boosting the expressive ability of
GNNs for heterophilic graphs by encouraging distinguishable
and discriminative node representations. A summary of the GNN
architecture refinement works is illustrated in Table II.
A. Identifiable Message Aggregation
Given the neighbors to be aggregated, the key of integrating
beneficial messages on heterophilic graphs is distinguishing
the information of similar neighbors (likely in the same class)
from that of dissimilar neighbors (likely in different classes).
To make node representations on heterophilic graphs more discriminative, identifiable message aggregation methods alter the

ZHENG et al.: GNNS FOR GRAPHS WITH HETEROPHILY: A SURVEY

4393

Fig. 4. Illustration of identifiable message passing with edge-related weight and feature-related weight assignment schemes in GNN architecture refinement
methods.

aggregation operation AGGREGATE(·) by imposing adaptive
(l)
edge-aware weights auv for node pair (u, v) at the l-th layer as:


(l)
(l) (l−1)
m(l)
{a
=
AGGREGATE
h
:
u
∈
N
(v)}
.
v
uv u
(17)
In this way, different methods develop various weight
(l)
assignment schemes for auv to model the importance of
similar and dissimilar neighbors during aggregation. In the
following, we provide the details of weight assignment schemes
adopted by existing methods, which respectively work on node
feature and edge related weights. Fig. 4 provides the pipelines
of two weight assignment schemes.
1) Edge-Related Weight: In general, edge-related methods
simultaneously focus on spectral domain and the spatial domain.
To be concrete, spectral GNNs leverage the theory of graph
signal processing to design graph filters, and spatial GNNs
focus on the graph structural topology to develop aggregation
strategies.
Spectral Perspective: In contrast to Laplacian smoothing [87]
and low-pass filtering [88] to approximate graph Fourier transformation on homophilic graphs, spectral GNNs on heterophilic
graphs involve both low-pass and high-pass filters to adaptively
extract low-frequency and high-frequency graph signals. The
essential intuition behind this lies in that low-pass filters mainly
retain the commonality of node features, while high-pass filters
capture the difference between nodes.
Typically, FAGCN [25] adopts a self-gating attention mechanism to learn the proportion of low-frequency and high(l)
frequency signals by splitting the auv into two components, i.e.,
(l,LP )
(l,HP )
and auv
, corresponding to low-pass and high-pass
auv
filters, respectively. Through adaptive frequency signal learning, FAGCN could achieve expressive performance on different
types of graphs with homophily and heterophily. Formally,
(l)
adaptive edge-aware weights auv are defined in FAGCN as
a(l)
uv =

(l,LP )

auv

√

(l,HP )

− auv
du dv

,

(18)

where du and dv respectively denote the degree of node u and v,
(l,LP )
(l,HP )
− auv
is the coefficient learned through a shared selfauv
gating mechanism tanh (qT [hu ; hv ]), from which [; ] denotes
the concatenation operation, g can be seen as a shared convolutional kernel, tanh (·) is the hyperbolic tangent function, which
(l,LP )
(l,HP )
− auv
in [−1, 1]. In
can naturally limits the value of auv
a similar fashion, RFA-GNN [67] captures edge-aware weights

using a relation-based frequency adaptive mechanism. This
mechanism takes into account higher-order contextual information compared to FAGCN. It precisely defines edge-aware
weights for a specific relation. Specifically, the edge-aware
weight of (l + 1)-order information between nodes u and v for
(l)
(l)
(l)
relation k is described as auvk = tanh (qT
lk [hU K ; hvk ]), where
qlk is the attention coefficient for relation k in the l-th iteration.
Apart from low-pass and high-pass filters, ACM [59] further
involves the identity filter, which is the linear combination of
low-pass and high-pass filters, i.e.,
 


) (l,IP ) (l,HP )
(l)
/τ Wuv
,
a(l)
a(l,LP
, auv , auv
uv = Softmax
uv
(19)
(l)
where τ indicates a temperature parameter and Wuv ∈ R1×3
is used to learn which filters is important or not for each
(l,LP ) (l,IP )
(l,HP )
respectively denotes low-pass,
node. auv , auv and auv
identity and high-pass edge-aware weights, which learn from
3 channels features. AutoGCN [68] captures the full spectrum
of graph signals and automatically update the bandwidth of
graph convolutional filters. In addition, Mid-GCN [70] contains
a mid-pass filter determined by both low-pass and high-pass
filters. The robustness of signals passing through this mid-pass
filter is theoretically guaranteed by their analyses.
In this way, ACM, AutoGCN and Mid-GCN could adaptively
exploit beneficial neighbor information from different filter
channels for each node; Meanwhile, their identity or mid-pass
filters could guarantee less information loss of the input signal.
Spatial Perspective: Heterophilic GNNs in the spatial domain
require the diverse topology-based aggregation of neighbors
from the same or different classes guided by the heterophily.
Therefore, the edge-aware weights of neighbors should be assigned according to the spatial graph topology and node labels.
Taking node attributes as weak labels, DMP method [29] considers node attribute heterophily for diverse message passing
and specifies every attribute propagation weight on each edge.
(l)
Furthermore, instead of the scalar weight auv that aggregates
all the node attributes with the same weight at the node level,
(l)
DMP extends the weight to a vector auv through operating in
the attribute dimension, and this vector can be calculated by
either relaxing GAT [9] weights to real values or allowing an
element-wise average of neighbor weights.
Moreover, certain methods learn edge-aware weights based on
node labels. For instance, Chen et al. [89] introduce the concept
of graph decoupling attention Markov networks (GDAMNs).

4394

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

This approach incorporates variational inference to model edge
uncertainty and employs both hard and soft attention mechanisms on node labels to improve the learning of edge-aware
weights, represented as
a(l)
uv =

(l−1)

ahard
uv exp δuv

(l−1)
N
hard
v=1 auv exp δuv

,

(20)

T
where ahard
uv = Auv · ỹ wuv ỹ is the hard attention with label
(l−1)
(l−1)
(l−1)
similarity and δuv = − Cos(hu , hv ) denotes the soft
attention with feature dissimilarity. In general, the hard attention
is learned on labels for a refined graph structure with fewer
inter-class edges so that the aggregation’s negative disturbance
can be reduced. The soft attention aims to learn the aggregation
weights based on features over the refined graph structure to
enhance information gains during message passing.
Recent research has shown a growing interest in the efficiency of computing edge-aware weights for large-scale graphs.
CGP [90] introduces a graph pruning paradigm during training,
enabling the discovery of high-performing sparse GNNs within a
single training process. Additionally, a global graph transformer
model has been proposed for large-scale heterophilic node classification tasks, known as GOAT [69]. GOAT samples potential
neighbors for each node from its k-hop neighbors. To distinguish
between neighbors based on topology information during the
propagation process, GOAT further incorporates a global attention module designed to learn attention scores between potential
neighbors and source nodes.
2) Feature-Related Weight: Apart from the adaptive edgeaware weight learning, there is another solution working on
(l−1)
in
the neighbor representation learning by revising hu
(l)
(l−1)
(l)
: u ∈ N (v)}). Conventionally,
AGGREGATE ({auv hu
the above-mentioned methods mainly utilize the contextual
node representations of neighbors; In contrast, this solution
(l−1)
to other nodetransforms contextual node embeddings hu
level properties that reflect the heterophily. In this way, het(l)
erophilic GNNs learn node-level attention βv , which is shared
with each u ∈ N (v), to capture the beneficial information
of heterophily for distinguishable node representation learning. As a result, the aggregation progress can be redefined as
(l) (l−1)
: u ∈ N (v)}). Existing methAGGREGATE(l) ({βv hu
(l)
ods mainly learn βv through two schemes based on homophily/heterophily prior knowledge and homophily attributes
attention.
Prior-Based: The prior-based method considers the incorporation of homophily/heterophily prior knowledge in the process
of feature transformation, primarily estimating the assignment
(l)
weight βv through class information. Typically, instead of
propagating original node feature representations, CPGNN [23]
propagates a prior belief estimation based on a compatibility
matrix, so that it can capture both heterophily and homophily by
modeling the likelihood of connections between nodes in dif(l−1)
ferent classes. The feature-aware weight of embeddings hv
with prior belief is defined as

βv(l) = Sinkhorn-Knopp (yv , Av , Bv ) ,

(21)

where Sinkhorn-Knopp denotes the Sinkhorn-Knopp algo(l)
rithm proposed in [91], which is to ensure that βv is doubly
stochastic. Bv denotes an enhanced belief matrix for node
v, depending on a training mask matrix and a prior belief.
Going beyond the uniform GCN aggregation, NLGNN [92]
and GPNN [93] consider the sequential aggregation where
the neighbors are ranked based on the class similarity (i.e.,
a homophily/heterophily prior belief) in order. A regular 1Dconvolution layer is applied to extract the affinities between
the sequential nodes whether the nodes are close or distant
in heterophilic graphs. GIND [63] extends the linear isotropic
diffusion to a more expressive nonlinear diffusion mechanism,
which learns nonlinear flux features between node pairs before
aggregation. This design of the nonlinear diffusion ensures that
more information can be aggregated from similar neighbors and
(l)
less from dissimilar neighbors by learning βv , making node
features less likely to over-smooth.
Attention-Based: The majority of research focuses on devel(l)
oping diverse attention mechanisms for learning βv . A straightforward approach involves learning attribute similarity and utilizing this similarity to determine attention on node features.
CGCN [28] uses the cosine similarity to send signed neighbor
features under certain constraints of relative node degrees. In
this way, the messages are allowed to be optionally multiplied
by a negative sign or a positive sign, i.e., for node v, its message
is described as



(l) (l)
(l)
(l)
(l)
s
=
σ
β
+
β

A
h̃
h̃(l)
h(l+1)
v
v
v,pos
v
v
0
1

(l)
(l)
(l)
,
(22)
+ β2 (s(l)
v,neg  Av )h̃v
(l)

(l)

(l)

(l)

where β0 , β1 , and β2 are the l-th layer learned scalars. su,pos
(l)
and su,neg respectively indicate positive matrix and negative
matrix, which are split from the matrix with sign information.
Intuitively, signed messages consist of the negated messages
sent by neighbors of the opposing classes, and the positive
messages sent by neighbors of the same class. Similarly,
Du et al. [60] propose a method for defining positive and
negative correlation weights when modeling the similarity and
dissimilarity between node features. They introduce a novel
GNN model called GBK-GNN, which is based on a bi-kernel
feature transformation and a selection gate. The two kernels
capture homophily and heterophily information, and the gate
is used to determine which kernel should be applied to a
specific pair of nodes. Formally, the gate signal is described
(l)
(l−1)
(l−1)
(l−1)
as βv = u∈N (v) Sigmoid(MLP(hv , hu ; Wv )),
where MLP(·) is a multilayer perceptron. MMP [94] decouples
the messages into two parts, i.e., memory for propagation and
self-embedding for discrimination. The memory for propagation
aims to endow each node with a memory cell and sends messages
from the memory cell instead of hidden self-embedding.
After propagation, each node can leverage a learnable control
mechanism to adaptively update its self-embedding and memory
cell according to their recent states. CAGNNs [95] investigates
the feature aggregation of inter-class edges from an entire
neighbor identifiable perspective by a new metric based on von

ZHENG et al.: GNNS FOR GRAPHS WITH HETEROPHILY: A SURVEY

(l)

Neumann entropy. Using an importance score βv obtained by a
mixer combines discriminant feature and neighbor information,
(l−1)
which are decoupled from embedding hv . To overcome the
limitations of traditional messaging methods, NCGNN [66]
represents nodes as collections of node-level capsules. Each
capsule is responsible for extracting distinct features from its
associated node. For each node-level capsule, a novel dynamic
routing procedure is implemented to intelligently select the most
suitable capsules for aggregation from a subgraph identified
by the designed graph filter. NCGNN exclusively aggregates
advantageous capsules while constraining irrelevant messages
to prevent excessive feature mixing among interacting nodes. As
a result, this approach mitigates the problem of oversmoothing
and enables the learning of effective node representations in
graphs characterized by either homophily or heterophily.
3) Hybrid Weight: Hybrid methods aim to calculate edge
weights guided by node features and edge information simultaneously. A typical method is MWGNN [62], which models the node local distribution from node feature, topological
structure, and positional identity aspects with the meta-weight.
Then, based on the meta-weight, an adaptive graph convolution
is derived to conduct node-specific weighted aggregation for
boosted node representation learning.
Remark: On heterophilic graphs, an ego node is likely to be
dissimilar with its neighbors in terms of class labels. Hence,
encoding ego-node representations separately from the aggregated representations of neighbor nodes would benefit distinguishable node embedding learning. In detail, ego-neighbor separation methods detach self-loop connections of the ego nodes
in AGGREGATE(·). Meanwhile, they alter the UPDATE(·)
as the non-mixing operations, e.g., concatenation, instead of the
mixing operation, e.g., “average” in vanilla GCN. H2GCN [24]
first proposes to exclude the self-loop connection and points
out that the non-mixing operations in the update function ensure
that expressive node representations would survive over multiple
rounds of propagation without becoming prohibitively similar.
Besides, WRGNN [97] imposes different mapping functions on
the ego-node embedding and its neighbor aggregated messages,
while GGCN [28] simplifies the mapping functions to learnable
scalar parameters to separately learn ego-neighbor representations. Moreover, ACM [59] adopts the identity filter to separate
the ego embedding and then conducts the channel-level combination with its neighbor information in the update function.
B. Inter-Layer Combination
Different from identifiable message aggregation methods focusing on the fine-grained intra-layer design of GNN architectures with heterophily, inter-layer combination methods consider layer-wise operations to boost the representation power of
heterophilic GNNs. The intuition behind this strategy is that in
the shallow layers of GNNs, they collect local information, e.g.,
one-hop neighbor locality in two-layer vanilla GCN, when the
layers go deeper, GNNs gradually capture global information
implicitly via multiple rounds of neighbor propagation. Due to
the heterophily characteristic, neighbors with similar information, i.e., class labels, might locate in both local geometry and

4395

long-term global topology. Hence, combining intermediate representations from each layer contributes to leveraging different
neighbor ranges with the consideration of both local and global
structural properties, resulting in powerful heterophilic GNNs.
Fig. 5 shows the formulation and illustrations of the closely
related methods.
The prior idea first comes from JK-Net [84] which flexibly
captures better structure-aware representation with different
neighborhood ranges. The combination of features among different layers is described as


(23)
ĥv = LA h(1) , h(2) , . . . , h(L) ,
where LA(·) denotes the layer aggregation, such as column-wise
combination, max pooling, attention with LSTM, etc.
Compared with the methods using all previous intermediate
representations, GCNII [96] only integrates the first layer’s node
embedding at each layer with the initial residual connection,
defined as
(0)
(l)
(l−1)
h(l)
: u ∈ N (v)}),
v = αhv +AGGREGATE ({(1−α)hv
(24)
where α is a hyperparameter that maintains a balance between
the node embedding of the first layer and the representation of
the current layer.
Instead of using the simple concatenation operation, GPRGNN [30] further assigns learnable weights to combine the representations of each layer adaptively via the Generalized PageRank (GPR) technique. PowerEmbed [85] employs an inception
network to learn the rich representations that interpolate from
local message-passing features to global spectral information.
Hence, inter-layer combination methods are able to conduct
topological feature exploration and benefit from informative
multi-round propagation, making node features of heterophilic
graphs distinguishable.

VI. HYBRID METHODS
Recently, researchers have recognized that simultaneously
expanding the non-local neighbor set and refining heterophilyguided GNN architectures, can significantly facilitate heterophilic graph representation learning. Generally, existing hybrid methods can be categorized into two groups: (1) local-level
incorporation, which designs intra-layer heterophilic GNN message passing with the neighbor extension; and (2) global-level
incorporation, which enhances effective inter-layer information
transfer of heterophilic GNNs with the neighbor extension. The
diagram of two types of hybrid methods is presented in Fig. 6
and a summary of the hybrid methods is illustrated in Table III.
The majority of methods fall into the category of local-level
incorporation, typically following a two-step process. First, they
establish a graph topology that emphasizes local homophily,
and then they design a message aggregation method based on
this homophilic topology. For instance, WRGNN [97] employs
the degree sequence of neighbor nodes as a metric for measuring structural similarity between ego nodes. This is used to
reconstruct a multi-relational graph that captures homophily in
relational edges, followed by relational aggregation with explicit

4396

Fig. 5.

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

Illustration of typical inter-layer combination methods: (1) GPR-GNN [30]; (2) JK-Net [84]; and (3) GCNII [96].

Fig. 6. A diagram of two types of hybrid methods: Local-level incorporation
and global-level incorporation.

link weights. Additionally, BM-GCN [99] constructs a novel
network topology using a block similarity matrix. This approach
allows it to explore block-guided neighbors and perform classified aggregation with distinct aggregation rules for homophilic
and heterophilic nodes. RAW-GNN [98] employs breadth-first
random walk searches to capture homophily information and
depth-first searches to gather heterophily information. Instead of
traditional neighborhoods, it utilizes path-based neighborhoods
and introduces a new path-based aggregator based on Recurrent
Neural Networks. GPNN [93] leverages a pointer network to
rank the potential neighbor nodes according to the attention
scores or the relevant relationships to the ego node. In this way,
potential neighbors that are most similar to the ego node in
heterophilic graphs can be discovered and selected. Deformable
GCN, as presented in the recent work by Park et al. [100],
dynamically conducts convolution in multiple latent spaces,
enabling it to capture both short and long-range dependencies
between nodes. In this approach, the model also learns the
positional embeddings (coordinates) of nodes to infer the relationships between nodes in an end-to-end manner. Depending
on the position of a node, the convolution kernels are deformed
using deformation vectors and make distinct transformations
being applied to neighbors.
The global-level incorporation method, which is intended
to establish effective homophilic guidance within the graph
network framework. A typical example of such a method
is H2GNN [24], which incorporates a set of crucial

design elements. These include the separation of egoand neighbor-embedding, higher-order neighborhoods, and
incorporation of intermediate representations into a graph
neural network. These design choices collectively enhance the
model’s capacity to learn from the graph structure, especially
when dealing with heterophilic relationships. Furthermore,
NLGNN [92] employs the attention mechanism to guide the
sorting of non-local neighbors based on their importance. The
entire architecture achieves efficient node classification on a
heterogeneous graph using only two steps: straightforward
attention-guided sorting and non-local aggregation.
Significance: Sections IV–VI discuss heterophilic GNNs,
which are essential for applications like fraud detection [102],
[103], where anomalous nodes deliberately connect with benign ones to evade homophilic models (e.g., GCN). While
heterophily-specific designs generally outperform homophilic
GNNs, recent studies urge a re-evaluation of early empirical
results. Specifically, [40] identifies critical flaws (e.g., class
imbalance, data leakage) in existing datasets and introduces rigorous new benchmarks. Furthermore, [38] notes that traditional
metrics hinder cross-dataset comparisons, proposing “label informativeness” to transcend the simple homophily-heterophily
dichotomy. Moreover, [59], [104] show that well-tuned GCNs
can succeed on certain heterophilic graphs, delineating strict
boundary conditions; [104] explains that GCNs primarily fail
when neighborhood distributions across distinct classes become indistinguishable. Collectively, these insights reflect a
broader shift from empirical trial-and-error toward theoretically
grounded design and robust generalization. Accordingly, we
encourage evaluating future methods on reliable, high-quality
datasets. Following this standard, Appendix C (online available)
provides our additional comparisons,.
VII. DISCUSSION
A. Heterophily GNNs on Diverse Graph Types
Current research predominantly focuses on heterophily modeling in single-relational static graphs, yet real-world applications (e.g., traffic flow dynamics and user-item hypergraph copurchasing relationships [105], [106], [107]) typically involve
diverse graph structures like dynamic graphs and hypergraphs.
While recent studies [108], [109], [110] have initiated concepts
for heterophilic dynamic graphs and hypergraphs, this expansion
also brings forth a set of unique challenges for heterophilic
GNNs to address.

ZHENG et al.: GNNS FOR GRAPHS WITH HETEROPHILY: A SURVEY

Fig. 7. Examples of (a) heterophilic dynamic graph and (b) heterophilic
hypergraph.

1) Heterophily GNNs on Dynamic Graphs: As a typical dynamic graph instantiation, spatial-temporal graph data is often
inherently heterophilic. Zhou et al. [108] recently aimed to
validate this assertion by exploring spatial-temporal graphs in
various real-world scenarios, such as traffic control, climate
early-warning, and social networks. As depicted in Fig. 7(a),
observations in these scenarios tend to change over time, leading
to dynamic and time-varying characteristics in the correlation
between nodes. The challenge posed by these dynamic and timevarying characteristics is termed “topology-task discordance”
in [108]. This challenge arises when employing homophilic
graph neural networks for node-level regression tasks on spatialtemporal graphs. It refers to the utilization of a pre-defined
fixed topology for message passing on spatial-temporal graphs
with diverse node-wise relations, resulting in the aggregation of
neighbors that deviate from the intended target.
To formally measure spatial-temporal heterophily, two types
of homophily measurements are introduced: “intra-graph spatial
homophily”, capturing node correlations within the same graph
frames, and “inter-graph transition homophily” which extracts
temporal evolution between adjacent temporal frames. The
study further investigates the average homophily ratios for four
real-world dynamic graphs: Metr-LA [111], PeMS-Bay [111],
KnowAir [112], and Temperature [112]. The homophily ratios
within intra-graph frames and across temporally adjacent frames
are observed to be low. This suggests that physically connected
nodes may not necessarily share similar observations or exhibit
the same directional variations.
Furthermore, adapting existing homophily theories to address
the topology-task discordance based on the spatial-temporal
characteristics of node-wise relationships remains a challenging endeavor. The primary hurdles can be summarized as
follows:
r Determining which pairs of nodes belong to homophily
components in the absence of categorical labels.
r Incorporating target information to reconstruct nodewise correlations, thereby enabling improved and targetoriented aggregations.
r Leveraging dynamic local neighborhood environments for
personalized high-order propagation.
These three aspects are expected to be key challenges in the
study of heterophilic GNNs on dynamic graphs. This research
direction will continue to demand the dedicated efforts of a
significant number of researchers.

4397

2) Heterophily GNNs on Hypergraphs: Fig. 7(b) illustrates
a heterophilic hypergraph using a social network as an example.
Each node represents a social user, and the hyperedge connects
all users in the same community. It is common for users within
the same community to have different identity backgrounds
but be connected by attributes such as interests and hobbies,
resembling the concept of heterophily in graphs. Recently, heterophily has been demonstrated in [113] to be a more prevalent
phenomenon in hypergraphs compared to graphs. This is due to
the challenge of expecting all nodes within a large hyperedge
to share a common label. Li et al. [109] are the first to focus
on heterophilic hypergraph learning (HHL), paving the way for
HHL by addressing key gaps from multiple perspectives: measurement, dataset diversity, and baseline model development.
Consequently, recent research on hypergraph neural network
methods has shifted its focus towards highlighting their exceptional performance on heterophilic hypergraphs.
Inspired by hypergraph diffusion algorithms, ED-HNN [110]
has been developed as a novel hypergraph neural network (HNN)
architecture that can effectively approximate any continuous
equivariant hypergraph diffusion operators. These operators
have the capability to model a wide array of higher-order relations. In this research, it is asserted that predicting node labels
in heterophilic hypergraphs is more intricate than in graphs since
a hyperedge may consist of nodes from multiple categories.
Therefore, the research further analyzes its learnable equivariant
diffusion operator and demonstrates its superiority in predicting
heterophilic node labels on four hypergraphs: Congress [114],
Senate [114], Walmart [115], and House [116].
However, based on our review of related works, there is
currently no established characterization or algorithmic design
for specific heterophilic hypergraphs. The primary challenges
revolve around accurately describing the heterophily of hypergraphs and developing architecture refinement methods that capture the local homophily of hypergraphs. This research direction
is still promising but in its early stages of development.
3) Heterophily GNNs on Heterogeneous Graphs: Recent
years have witnessed growing scholarly attention to heterophily
characterization in heterogeneous graph analysis. Pioneering
work by Lin et al. [117] made dual contributions: not only did
they systematically demonstrate the coexistence of heterophilic
patterns in homogeneous graphs and homophilic structures in
heterogeneous graphs across real-world applications, but they
also introduced the H2 ˜GB benchmark dataset, effectively
addressing critical gaps in standardized evaluation protocols.
In parallel, Shen et al. [118] tackled heterophily challenges
through an unsupervised perspective, formally defining the concept of semantic heterophily and developing LatGRL—a latent
graph-guided reinforcement learning framework for hierarchical feature disentanglement. Despite these advancements, current research exhibits limitations, such as available benchmark
datasets suffer from limited scale and scenario coverage. These
unresolved issues necessitate coordinated efforts in developing theoretically grounded measurement systems, constructing
large-scale multi-domain testbeds, and exploring cross-layer
heterophily propagation mechanisms.

4398

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

Fig. 8. Small, adversarial perturbations of the graph structure and node features lead GNN to misclassify target u.

B. Unveiling the Correlation Between Graph Heterophily and
Other Research Problems
1) Relation Between Graph Heterophily and Adversarial
Robustness: Adversarial robustness in GNNs addresses model
vulnerability to imperceptible structural perturbations, critical
for trustworthy AI systems. While early studies focused on homophilic graphs [119], [120], recent work recognizes structural
attacks inherently exhibit heterophily (Fig. 8), driving defense
strategies:
r GNNGUARD [121]: Detects feature-structure correlations
to filter adversarial heterophilic edges, ensuring robust
message propagation.
r GARNET [122] & ATDGIA [123]: Treat heterophilic connections as adversarial edges, embedding anti-interference
mechanisms.
r Theoretical Foundations [124]: Establishes homophilyheterophily dynamics under structural attacks, proving
heterophily-aware designs inherently enhance robustness.
Current research converges on dual defense paradigms:
explicit adversarial filtering and implicit robustness through
heterophily-adaptive architectures.
Robustness and the interplay between homophily and heterophily in structural attacks on GNNs are key areas of investigation in these studies, with implications for improving robust
GNN model designs.
2) Relation Between Graph Heterophily and OverSmoothing: Contemporary GNNs face dual challenges:
heterophily violating homophily assumptions and oversmoothing eroding feature distinctiveness. As Fig. 9
illustrates, these phenomena exhibit intrinsic connections heterophilic aggregation leads to information dissipation in
deep architectures [125]. Additionally, emerging studies reveal
an intrinsic duality between these challenges: novel architectures
designed for heterophilic graphs (e.g., FAGCN [25],
NLGNN [92]) exhibit inherent anti-over-smoothing properties,
whereas certain over-smoothing mitigation strategies conversely
enhance heterophilic learning [96].
Theoretical unification reveals:
r Sheaf-Theoretic Foundation: Cellular sheaf theory [54]
demonstrated underlying sheaf structure of the graph is
intimately linked with both heterophily and oversmoothing
that influence the performance of GNNs.
r Signed Message Explanation: Yan et al. [28] and Bodnar et al. [54] found evidence supporting the benefits of
negatively signed edges in GNNs, albeit with different
mathematical justifications. These theoretical findings also

provide support for the effectiveness of technologies represented by FAGCN [25].
These theoretical convergences enable unified frameworks
achieving performance improvement across heterophilic benchmarks while maintaining stable higher layer performance
- resolving the depth-performance trade-off in conventional
GNNs.
3) Relation Between Graph Heterophily and Graph Anomaly
Detection: Fraud detection, as a specialized anomaly detection
task, increasingly focuses on heterophilic patterns in graphstructured financial data [103], [126], [127], [128]. As visualized
in Fig. 10, fraudulent nodes typically form minority clusters surrounded by normal nodes, exhibiting higher heterophily ratios
than legitimate entities [103].
Conventional graph anomaly detection (GAD) methods predominantly optimize homophilic message passing, inadvertently amplifying heterophily-induced noise during aggregation [102]. This manifests as significant performance degradation in real-world fraud detection benchmarks. Recent advances
address this through:
r Structural Adaptation: Gong et al. [103] develop graph
sparsification techniques that selectively prune heterophilic edges while preserving homophilic dependencies.
r Distribution Alignment: Gao’s SDS framework [126] mitigates structural distribution shifts between imbalanced
classes via adversarial topology regularization.
r Spectral Decoupling: Hybrid approaches [127], [129] dynamically combine low/high-frequency signals, achieving high precision in identifying heterophilic anomalies
through adaptive graph filtering.
These methodologies establish heterophily suppression as
critical for robust fraud detection systems, with spectral-graph
fusion strategies demonstrating performance improvements over
conventional GAD baselines.
4) Relation Between Graph Heterophily and Uncertainty
Modeling: Uncertainty quantification in graph-structured data
has become pivotal for reliable decision systems [86], [130],
[131], [132]. Under graph heterophily where nodes exhibit diverse connections (Fig. 11), topological uncertainty arises from
heterogeneous relationship intensities that complicate information propagation.
Node-level analysis reveals real-world graphs often intermix homophilic/heterophilic connections, exposing GNNs’ inherent bias toward homophilic patterns - models trained on
semi-homophilic graphs show accuracy drops on purely heterophilic subsets [131]. This bias-stability dilemma necessitates
uncertainty-aware solutions:
r Uncertainty Debiasing: Liu’s framework [131] employs
epistemic uncertainty estimation to identify heterophilic
nodes, preserving reliable predictions while rectifying
high-uncertainty cases.
r Topology Augmentation: Gao et al. [86] propose GraphTU,
a probabilistic method exploiting neighborhood variance to enhance minor class representation through nonparametric topology perturbation.

ZHENG et al.: GNNS FOR GRAPHS WITH HETEROPHILY: A SURVEY

Fig. 9.

4399

Illustration of the connection between the heterophily property (Left) and the over-smoothing issue (Right) on GNNs.

Fig. 10. A toy graph for anomaly detection. The average homophily and
heterophily for anomalies and normals are presented.

Furthermore, it executes contrastive learning by sampling homophily neighbors as positive examples, offering innovative
insights for the design of heterophilic GNNs. To address the
limitations imposed by the strong homophily assumption and
label dependency, Li et al. [134] introduced a novel multi-task
model named PairE with a contrastive learning method. This
model is designed to preserve information pertaining to both
homophily and heterophily by transcending the localized node
view. It achieves this by harnessing higher-level entities with
more expressive power, enabling the representation of feature
signals beyond homophily. In a similar vein and motivated by
comparable considerations, Liu et al. [31] propose an innovative
self-supervised Graph Representation Learning method called
Edge Heterophily Discriminating (GREET). By discriminating
edges, GREET obtains contrastive views with both homophilic
and heterophilic edges, leveraging them to learn expressive
representations.
VIII. FUTURE DIRECTIONS

Fig. 11.

Illustration of the uncertainty of connections in a graph.

These advances establish heterophily-uncertainty interdependence as crucial for developing robust GNNs, offering new
directions for social network analysis to biomedical discovery.
Other Promising Heterophily Explorations: Recently, researchers have sought to extend the design of heterophilic
GNNs beyond the semi-supervised paradigm, focusing on selfsupervised heterophilic GNNs [31], [133], [134]. It is noteworthy that He et al. [133] identified commonalities between
the establishment of the Graph Contrastive Learning (GCL)
framework and the design of heterophilic GNNs. In the GCL
framework, the task involves identifying additional positive
samples belonging to the same class, while in the design of
heterophilic GNNs, the objective is to identify other intra-class
neighbors for each node. Recognizing this similarity, they integrated the GCL sampling strategy with homophily discrimination, creating a novel contrastive learning framework to address
these crucial challenges. This framework draws inspiration from
homophily, breaking traditional data enhancement strategies and
providing a fresh perspective on establishing a GCL framework.

GNNs for heterophilic graphs are fast developing in the past
few years. Beyond current research, there still remain several
open challenges and opportunities worthy of further attention
and exploration. In this section, we discuss the following directions to stimulate future research.
Interpretable Heterophilic GNNs: Interpretability is a crucial aspect of GNN models in risk-sensitive or privacy-related
application fields, e.g., healthcare and cybersecurity. Although
there are several studies on the interpretability [135], [136],
[137] for homophilic GNNs, how to explain the predictions of
heterophilic GNNs is still under-explored. Heterophily makes
interpretability more challenging than homophily: since most
local neighbor nodes are not in the same class as the ego nodes,
extracting explainable subgraphs from highly heterophilic graph
data is much harder, where both proximal and distant topological
structures are required to be discovered and exploited. For instance, ShapeGGen [137] typically proposed a dataset generator
that can automatically generate a variety of benchmark datasets
(e.g., varying graph sizes, degree distributions, homophilic and
heterophilic graphs), accompanied by ground-truth explanations
From the data-centric view of heterophilic graphs, how to extract
explainable subgraphs under complex similarity relationships
between ego nodes and their potential neighbors on heterophilic
graphs for interpretability is an open question. Moreover, from

4400

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

the model-centric view of heterophilic GNNs, how to explain
the model’s predictions on graphs with different degrees of
heterophily also deserves further exploration.
Scalable Heterophilic GNNs: Current heterophilic GNNs are
generally trained on relatively small graphs, which significantly
limits their ability to model large-scale data and explore more
complicated heterophilic patterns. Although possible solutions
to tackle scalability can be borrowed from the mainstream graph
sampling strategies [138], [139] for homophilic GNNs, the
connections and relationships of heterophilic nodes would be
undermined by sampling only mini-batches, especially when
similar and dissimilar neighbors contribute differently to learning the ego-node representations. LINKX [27] recently verifies
that even a simple MLP-based model could outperform GNNs
for mini-batch training on large-scale heterophilic graphs. Moreover, HopGNN [56] introduces a hop interaction paradigm to
address the scalability and over-smoothing problem of GNNs
simultaneously, where its core idea is to convert the interaction
target among nodes to pre-processed multi-hop features inside
each node. Hence, addressing the scalability problem of heterophilic graphs requires exploring more relationships between
ego-neighbor node features and multi-hop information. How
to keep the inherent heterophily unchanged when conducting
sampling on heterophilic graphs is still an open question.
Theoretical Heterophily Exploration: Despite the notable
achievements of heterophilic GNNs across diverse tasks and
datasets, their efficacy lacks a solid theoretical foundation to
substantiate their impact on enhancing graph representation
learning. Presently, many methods are predominantly designed
based on intuition and evaluated through empirical experiments.
Notably, a recent breakthrough by Ma et al. [104] has unveiled
that, under specific conditions, GCN can exhibit remarkable
performance on heterophilic graphs. This discovery has been
supported by comprehensive theoretical validation, outlining
the distinctive characteristics and conditions under which heterophilic graphs can excel with GCN. The elucidation of these
theoretical findings poses a significant challenge to the current
rationale underlying the design of heterophilic GNNs. Consequently, there arises a critical need for intensified theoretical
exploration in the future. This exploration should delve into
aspects such as the impact of heterophily on altering the trends of
generalization bounds. Bridging this explanatory gap is crucial
for comprehending the extent to which heterophily influences
the performance constraints of homophilic GNNs.
Diverse Heterophily Learning Tasks: The research on heterophilic GNNs has primarily demonstrated success in nodelevel tasks, covering both semi-supervised [41], [60], [69] and
unsupervised scenarios [31], [133], [140]. A recent study by
Zhou et al. [141] introduces a novel heterophilic framework
named DisenLink, specifically designed for addressing linklevel tasks on heterophilic graphs. In heterophilic graphs, DisenLink reveals that link formation is influenced by numerous latent
factors, causing linked nodes to share similarity in certain factors
while being dissimilar in others. This results in an overall low
similarity between linked nodes. Many existing link prediction
approaches operate under the homophily assumption, using
similarity-based heuristics or representation learning methods

to predict links. Therefore, accurately predicting links with
heterophilic attributes, determined by specific potential similar
factors, poses a significant challenge. DisenLink identifies the
challenges of link-level tasks on heterophilic graphs, but there
are still significant open questions in this domain. These include
the development of reasonable heterophilic benchmark datasets
and the refinement of GNN architectures for link-level tasks.
Additionally, similar open questions exist for graph-level tasks,
indicating that further exploration is needed in these areas.
Broader Scope of Practical Applications: In the real world,
heterophilic relationships are pervasive and exist widely in
various graph-structured data [142], [143], [144], [145], [146],
[147], [148], [149]. However, current research on heterophilic
GNNs predominantly focuses on specific strong heterophilic
graphs, such as social networks [145] and web page networks [146]. Other fields, such as biomedicine [147] and chemistry [148], [149], which also naturally exhibit the heterophilic
property, deserve more explorations. For instance, in proteinprotein interaction networks, proteins with interactions often
belong to different gene ontologies. Moreover, in the field of drug
discovery, DCMGCN [149] verifies the heterophily property of
the drug-drug networks and proposed a combination of intermediate representations, and high-similarity neighborhoods, to
boost GCN learning on the heterophily and sparse drug-drug
networks. Besides, in the field of fraud detection, fraudsters
tend to be more connected to regular users represented by fraud
networks. And some existing research, e.g., DRAG [150] and
GAGA [151], solved the problem by conducting the binary heterophilic graph classification task. This highlights the untapped
potential of heterophilic GNNs in a broader range of application
areas. There is an expectation to extend the use of heterophilic
GNNs to various fields, including financial networks, network
security, community detection, biomedicine, and chemistry.
IX. CONCLUSION
This paper presents a comprehensive overview of graph neural
networks for heterophilic graphs. We introduce a systematic
taxonomy categorizing existing methods into three classes: nonlocal neighbor extension, GNN architecture refinement, and
hybrid approaches. The study surveys current research progress
and challenges in heterophilic graph learning, and discusses the
relevance of graph heterophily to various domains such as model
robustness, over-smoothing, and graph anomaly detection. In the
end, we shared our insights into future research opportunities and
directions that can contribute to the advancement of heterophilic
GNNs.
REFERENCES
[1] J. Tang, J. Sun, C. Wang, and Z. Yang, “Social influence analysis in
large-scale networks,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov.
Data Mining, 2009, pp. 807–816.
[2] H. Peng, R. Zhang, S. Li, Y. Cao, S. Pan, and P. Yu, “Reinforced,
incremental and cross-lingual event detection from social messages,”
IEEE Trans. Pattern Anal. Mach. Intell., vol. 45, no. 1, pp. 980–998,
Jan. 2023.
[3] S. Vashishth, S. Sanyal, V. Nitin, and P. Talukdar, “Composition-based
multi-relational graph convolutional networks,” in Proc. Int. Conf. Learn.
Representations, 2019, pp. 5250–5265.

ZHENG et al.: GNNS FOR GRAPHS WITH HETEROPHILY: A SURVEY

[4] Z. Wu, S. Pan, G. Long, J. Jiang, X. Chang, and C. Zhang, “Connecting the
dots: Multivariate time series forecasting with graph neural networks,”
in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 753–763.
[5] R. Ying, R. He, K. Chen, P. Eksombatchai, W. L. Hamilton, and J.
Leskovec, “Graph convolutional neural networks for web-scale recommender systems,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2018, pp. 974–983.
[6] J. Ma, C. Zhou, P. Cui, H. Yang, and W. Zhu, “Learning disentangled
representations for recommendation,” in Proc. Int. Conf. Neural Inf.
Process. Syst., 2019, pp. 5711–5722.
[7] T. N. Kipf and M. Welling, “Semi-supervised classification with graph
convolutional networks,” in Proc. Int. Conf. Learn. Representations,
2017, pp. 2713–2726.
[8] W. L. Hamilton, R. Ying, and J. Leskovec, “Inductive representation
learning on large graphs,” in Proc. Int. Conf. Neural Inf. Process. Syst.,
2017, pp. 1025–1035.
[9] P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Liò, and Y.
Bengio, “Graph attention networks,” in Proc. Int. Conf. Learn. Representations, 2018, pp. 2920–2931.
[10] K. Xu, W. Hu, J. Leskovec, and S. Jegelka, “How powerful are graph
neural networks?,” in Proc. Int. Conf. Learn. Representations, 2019,
pp. 9104–9120.
[11] Z. Wu, S. Pan, F. Chen, G. Long, C. Zhang, and S. Y. Philip, “A
comprehensive survey on graph neural networks,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 32, no. 1, pp. 4–24, Jan. 2021.
[12] S. Zhu, S. Pan, C. Zhou, J. Wu, Y. Cao, and B. Wang, “Graph geometry
interaction learning,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2020,
pp. 7548–7558.
[13] Y. Liu, K. Ding, Q. Lu, F. Li, L. Y. Zhang, and S. Pan, “Towards selfinterpretable graph-level anomaly detection,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2023, pp. 8975–8987.
[14] X. Zheng, M. Zhang, C. Chen, Q. V. H. Nguyen, X. Zhu, and S. Pan,
“Structure-free graph condensation: From large-scale graphs to condensed graph-free data,” in Proc. Int. Conf. Neural Inf. Process. Syst.,
2023, pp. 6026–6047.
[15] X. Zheng, M. Zhang, C. Chen, S. Molaei, C. Zhou, and S. Pan,
“GNNEvaluator: Evaluating GNN performance on unseen graphs without labels,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2023,
pp. 33606–33623.
[16] V. Ciotti, M. Bonaventura, V. Nicosia, P. Panzarasa, and V. Latora,
“Homophily and missing links in citation networks,” EPJ Data Sci.,
vol. 5, pp. 1–14, 2016.
[17] X. Zheng, M. Zhang, C. Chen, Q. Zhang, C. Zhou, and S. Pan, “AutoHeG: Automated graph neural network on heterophilic graphs,” in Proc.
ACM Web Conf., 2023, pp. 611–620.
[18] J. Xu, E. Dai, X. Zhang, and S. Wang, “HP-GMN: Graph memory networks for heterophilous graphs,” in Proc. IEEE Int. Conf. Data Mining,
2022, pp. 1263–1268.
[19] Y. Liu, Y. Zheng, D. Zhang, H. Chen, H. Peng, and S. Pan, “Towards
unsupervised deep graph structure learning,” in Proc. ACM Web Conf.,
2022, pp. 1392–1403.
[20] X. Zheng, M. Zhang, C. Chen, C. Li, C. Zhou, and S. Pan, “Multirelational graph neural architecture search with fine-grained message
passing,” in Proc. IEEE Int. Conf. Data Mining, 2022, pp. 783–792.
[21] Y. Zheng, H. Zhang, V. Lee, Y. Zheng, X. Wang, and S. Pan, “Finding
the missing-half: Graph complementary learning for homophily-prone
and heterophily-prone graphs,” in Proc. Int. Conf. Mach. Learn., 2023,
pp. 42492–42505.
[22] S. Pandit, D. H. Chau, S. Wang, and C. Faloutsos, “NetProbe: A fast and
scalable system for fraud detection in online auction networks,” in Proc.
ACM Web Conf., 2007, pp. 201–210.
[23] J. Zhu et al., “Graph neural networks with heterophily,” in Proc. AAAI
Conf. Artif. Intell., 2021, pp. 11168–11176.
[24] J. Zhu, Y. Yan, L. Zhao, M. Heimann, L. Akoglu, and D. Koutra,
“Beyond homophily in graph neural networks: Current limitations and
effective designs,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2020,
pp. 7793–7804.
[25] D. Bo, X. Wang, C. Shi, and H. Shen, “Beyond low-frequency information
in graph convolutional networks,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 3950–3957.
[26] D. Lim, X. Li, F. Hohne, and S.-N. Lim, “Large scale learning on nonhomophilous graphs: New benchmarks and strong simple methods,” in
Adv. Neural Inf. Process. Syst., 2021, pp. 20887–20902.

4401

[27] D. Lim et al., “Large scale learning on non-homophilous graphs: New
benchmarks and strong simple methods,” in Proc. Int. Conf. Neural Inf.
Process. Syst., 2021, pp. 20887–20902.
[28] Y. Yan, M. Hashemi, K. Swersky, Y. Yang, and D. Koutra, “Two sides
of the same coin: Heterophily and oversmoothing in graph convolutional
neural networks,” 2021, arXiv:2102.06462.
[29] L. Yang et al., “Diverse message passing for attribute with heterophily,”
in Proc. Int. Conf. Neural Inf. Process. Syst., 2021, pp. 4751–4763.
[30] E. Chien, J. Peng, P. Li, and O. Milenkovic, “Adaptive universal generalized PageRank graph neural network,” in Proc. Int. Conf. Learn.
Representations, 2021, pp. 16138–16161.
[31] Y. Liu, Y. Zheng, D. Zhang, V. C. Lee, and S. Pan, “Beyond
smoothing: Unsupervised graph representation learning with edge heterophily discriminating,” in Proc. AAAI Conf. Artif. Intell., 2023,
pp. 4516–4524.
[32] J. Zhu, Y. Yan, M. Heimann, L. Zhao, L. Akoglu, and D. Koutra,
“Heterophily and graph neural networks: Past, present and future,” IEEE
Data Eng. Bull., vol. 47, no. 2, pp. 10–32, 2023.
[33] C. Gong et al., “A survey on learning from graphs with heterophily:
Recent advances and future directions,” 2024, arXiv:2401.09769.
[34] S. Luan et al., “The heterophilic graph learning handbook: Benchmarks, models, theoretical analysis, applications and challenges,”
2024, arXiv:2407.09618.
[35] X. Zheng, Y. Liu, S. Pan, M. Zhang, D. Jin, and P. S. Yu, “Graph neural networks for graphs with heterophily: A survey,” 2022, arXiv:2202.07082.
[36] B. Bollobás, Extremal Graph Theory. North Chelmsford, MA, USA:
Courier Corporation, 2004.
[37] H. Pei, B. Wei, K. C.-C. Chang, Y. Lei, and B. Yang, “Geom-GCN:
Geometric graph convolutional networks,” in Proc. Int. Conf. Learn.
Representations, 2020, pp. 10247–10258.
[38] O. Platonov, D. Kuznedelev, A. Babenko, and L. Prokhorenkova, “Characterizing graph datasets for node classification: Homophily-heterophily
dichotomy and beyond,” in Proc. Int. Conf. Neural Inf. Process. Syst.,
2023, pp. 523–548.
[39] M. Mironov and L. Prokhorenkova, “Revisiting graph homophily measures,” in Proc. Learn. Graphs Conf., 2024, pp. 1–22.
[40] O. Platonov, D. Kuznedelev, M. Diskin, A. Babenko, and L.
Prokhorenkova, “A critical look at the evaluation of GNNs under heterophily: Are we really making progress?,” in Proc. Int. Conf. Learn.
Representations, 2023, pp. 18738–18752.
[41] S. Abu-El-Haija et al., “MixHop: Higher-order graph convolutional architectures via sparsified neighborhood mixing,” in Proc. Int. Conf. Mach.
Learn., 2019, pp. 21–29.
[42] Y. Wang and T. Derr, “Tree decomposed graph neural network,” in Proc.
ACM Int. Conf. Inf. Knowl. Manage., 2021, pp. 2040–2049.
[43] Y. Song, C. Zhou, X. Wang, and Z. Lin, “Ordered GNN: Ordering
message passing to deal with heterophily and over-smoothing,” in Proc.
Int. Conf. Learn. Representations, 2023, pp. 35954–35971.
[44] R. Lei, Z. Wang, Y. Li, B. Ding, and Z. Wei, “EvenNet: Ignoring odd-hop
neighbors improves robustness of graph neural networks,” in Proc. Int.
Conf. Neural Inf. Process. Syst., 2022, pp. 4694–4706.
[45] D. Jin et al., “Universal graph convolutional networks,” in Proc. Int. Conf.
Neural Inf. Process. Syst., 2021, pp. 10654–10664.
[46] W. Jin, T. Derr, Y. Wang, Y. Ma, Z. Liu, and J. Tang, “Node similarity
preserving graph convolutional networks,” in Proc. ACM Int. Conf. Web
Search Data Mining, 2021, pp. 148–156.
[47] L. Wu, H. Lin, Z. Liu, Z. Liu, Y. Huang, and S. Z. Li, “Homophilyenhanced self-supervision for graph structure learning: Insights and
directions,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 9,
pp. 12358–12372, Sep. 2024.
[48] D. Li, B. Qi, J. Gao, H. Xiong, B. Gu, and X. Chen, “MPformer: Advancing graph modeling through heterophily relationship-based position
encoding,” in Proc. Int. Conf. Learn. Representations, 2024. [Online].
Available: https://openreview.net/forum?id=C4s9CAvqyg
[49] H. Sun, X. Li, Z. Wu, D. Su, R.-H. Li, and G. Wang, “Breaking the
entanglement of homophily and heterophily in semi-supervised node
classification,” in Proc. IEEE Int. Conf. Data Eng., 2024, pp. 2379–2392.
[50] S. Rey, M. Navarro, V. M. Tenorio, S. Segarra, and A. G. Marques, “Redesigning graph filter-based GNNs to relax the homophily assumption,”
in Proc. IEEE Int. Conf. Acoust. Speech Signal Process., 2025, pp. 1–5.
[51] K. Goyal, S. Samanta, V. Goyal, and M. Mohania, “PathLens: Structurally
enhancing heterophilic graphs for GNNs,” in Proc. ACM Int. Conf. Inf.
Knowl. Manage., 2025, pp. 729–739.

4402

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

[52] T. Wang, R. Wang, D. Jin, D. He, and Y. Huang, “Powerful graph convolutioal networks with adaptive propagation mechanism for homophily
and heterophily,” in Proc. AAAI Conf. Artif. Intell., 2022, pp. 4210–4218.
[53] X. Li et al., “Finding global homophily in graph neural networks
when meeting heterophily,” in Proc. Int. Conf. Mach. Learn., 2022,
pp. 13242–13256.
[54] C. Bodnar, F. Di Giovanni, B. Chamberlain, P. Liò, and M. Bronstein,
“Neural sheaf diffusion: A topological perspective on heterophily and
oversmoothing in GNNs,” in Proc. Int. Conf. Neural Inf. Process. Syst.,
2022, pp. 18527–18541.
[55] D. Zou et al., “SE-GSL: A general and effective graph structure learning
framework through structural entropy optimization,” in Proc. ACM Web
Conf., 2023, pp. 499–510.
[56] J. Chen, Z. Li, Y. Zhu, J. Zhang, and J. Pu, “From node interaction to hop
interaction: New effective and scalable graph learning paradigm,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2023, pp. 7876–7885.
[57] Z. Yu, B. Feng, D. He, Z. Wang, Y. Huang, and Z. Feng, “LG-GNN: Localglobal adaptive graph neural network for modeling both homophily and
heterophily,” in Proc. Int. Joint Conf. Artif. Intell., 2024, pp. 2515–2523.
[58] D. Su, X. Li, Z. Li, Y. Liao, R.-H. Li, and G. Wang, “DiRW: Path-aware
digraph learning for heterophily,” in Proc. ACM Int. Conf. Inf. Knowl.
Manage., 2025, pp. 2771–2780.
[59] S. Luan et al., “Revisiting heterophily for graph neural networks,” in
Proc. Int. Conf. Neural Inf. Process. Syst., 2022, pp. 1362–1375.
[60] L. Du et al., “GBK-GNN: Gated bi-kernel graph neural networks for
modeling both homophily and heterophily,” in Proc. ACM Web Conf.,
2022, pp. 1550–1558.
[61] L. Wei, H. Zhao, and Z. He, “Designing the topology of graph neural
networks: A novel feature fusion perspective,” in Proc. ACM Web Conf.,
2022, pp. 1381–1391.
[62] X. Ma, Q. Chen, Y. Ren, G. Song, and L. Wang, “Meta-weight graph
neural network: Push the limits beyond global homophily,” in Proc. ACM
Web Conf., 2022, pp. 1270–1280.
[63] Q. Chen, Y. Wang, Y. Wang, J. Yang, and Z. Lin, “Optimization-induced
graph implicit nonlinear diffusion,” in Proc. Int. Conf. Mach. Learn.,
2022, pp. 3648–3661.
[64] S. Chanpuriya and C. Musco, “Simplified graph convolution with
heterophily,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2022,
pp. 27184–27197.
[65] D. Tortorella and A. Micheli, “Leave graphs alone: Addressing oversquashing without rewiring,” in Proc. Learn. Graphs Conf., 2022, pp. 1–8.
[66] R. Yang, W. Dai, C. Li, J. Zou, and H. Xiong, “NCGNN: Node-level
capsule graph neural network for semisupervised classification,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 35, no. 1, pp. 1025–1039, Jan. 2024.
[67] L. Wu et al., “Beyond homophily and homogeneity assumption: Relationbased frequency adaptive graph neural networks,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 35, no. 6, pp. 8497–8509, Jun. 2024.
[68] Z. Wu, S. Pan, G. Long, J. Jiang, and C. Zhang, “Beyond low-pass
filtering: Graph convolutional networks with automatic filtering,” IEEE
Trans. Knowl. Data Eng., vol. 35, no. 07, pp. 6687–6697, Jul. 2023.
[69] K. Kong, J. Chen, J. Kirchenbauer, R. Ni, C. B. Bruss, and T. Goldstein,
“GOAT: A global transformer on large-scale graphs,” in Proc. Int. Conf.
Mach. Learn., 2023, pp. 17375–17390.
[70] J. Huang, L. Du, X. Chen, Q. Fu, S. Han, and D. Zhang, “Robust mid-pass
filtering graph convolutional networks,” in Proc. ACM Web Conf., 2023,
pp. 328–338.
[71] Y. Yan et al., “From trainable negative depth to edge heterophily
in graphs,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2023,
pp. 70162–70178.
[72] L. Liang, X. Hu, Z. Xu, Z. Song, and I. King, “Predicting global label
relationship matrix for graph neural networks under heterophily,” in Proc.
Int. Conf. Neural Inf. Process. Syst., 2023, pp. 10909–10921.
[73] Z. Wen et al., “Homophily-related: Adaptive hybrid graph filter for
multi-view graph clustering,” in Proc. AAAI Conf. Artif. Intell., 2024,
pp. 15841–15849.
[74] B. Li, E. Pan, and Z. Kang, “PC-Conv: Unifying homophily and heterophily with two-fold filtering,” in Proc. AAAI Conf. Artif. Intell., 2024,
pp. 13437–13445.
[75] F. Shi et al., “VR-GNN: Variational relation vector graph neural network
for modeling homophily and heterophily,” World Wide Web, vol. 27, 2024,
Art. no. 32.
[76] R. Duan et al., “Unifying homophily and heterophily for spectral graph
neural networks via triple filter ensembles,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2024, pp. 93540–93567.

[77] J. Li, R. Zheng, H. Feng, M. Li, and X. Zhuang, “Permutation equivariant
graph framelets for heterophilous graph learning,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 35, no. 9, pp. 11634–11648, Sep. 2024.
[78] W. Bi, L. Du, Q. Fu, Y. Wang, S. Han, and D. Zhang, “Make heterophilic
graphs better fit GNN: A graph rewiring approach,” IEEE Trans. Knowl.
Data Eng., vol. 36, no. 12, pp. 8744–8757, Dec. 2024.
[79] C. Huang et al., “Flow2GNN: Flexible two-way flow message passing
for enhancing GNNs beyond homophily,” IEEE Trans. Cybern., vol. 54,
no. 11, pp. 6607–6618, Nov. 2024.
[80] Z. Zou, L. Shen, Y. Li, Y. Lu, J. Liu, and X. Liu, “RETAIN: Reliable topology augmentation for both heterophilic and homophilic
graphs,” in Proc. IEEE Int. Conf. Acoust. Speech Signal Process., 2025,
pp. 1–5.
[81] Y. Wang, C. Huang, M. Li, T. Cai, Z. Zheng, and X. Huang, “All roads
lead to rome: Exploring edge distribution shifts for heterophilic graph
learning,” in Proc. Int. Joint Conf. Artif. Intell., 2025, pp. 6487–6495.
[82] H. Liu et al., “Global structure-aware and feature-augmented graph neural
network for heterophilic graphs,” ACM Trans. Inf. Syst., vol. 44, 2025,
Art. no. 33.
[83] Z. Zheng, Y. Yang, Z. Guan, W. Zhao, and W. Lu, “Enhancing
homophily-heterophily separation: Relation-aware learning in heterogeneous graphs,” in Proc. ACM SIGKDD Conf. Knowl. Discov. Data
Mining, 2025, pp. 4050–4061.
[84] K. Xu, C. Li, Y. Tian, T. Sonobe, K.-I. Kawarabayashi, and S. Jegelka,
“Representation learning on graphs with jumping knowledge networks,”
in Proc. Int. Conf. Mach. Learn., 2018, pp. 5453–5462.
[85] N. T. Huang et al., “From local to global: Spectral-inspired graph neural
networks,” in Proc. NeurIPS 2022 Workshop: New Frontiers Graph
Learn., 2022.
[86] J. Gao, J. Li, K. Zhang, and Y. Kong, “Topology uncertainty modeling
for imbalanced node classification on graphs,” in Proc. IEEE Int. Conf.
Acoust. Speech Signal Process., 2023, pp. 1–5.
[87] Q. Li, Z. Han, and X.-M. Wu, “Deeper insights into graph convolutional
networks for semi-supervised learning,” in Proc. AAAI Conf. Artif. Intell.,
2018, pp. 3538–3545.
[88] F. Wu, A. Souza, T. Zhang, C. Fifty, T. Yu, and K. Weinberger, “Simplifying graph convolutional networks,” in Proc. Int. Conf. Mach. Learn.,
2019, pp. 6861–6871.
[89] J. Chen, S. Chen, M. Bai, J. Pu, J. Zhang, and J. Gao, “Graph decoupling
attention markov networks for semisupervised graph node classification,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 34, no. 12, pp. 9859–9873,
Dec. 2023.
[90] C. Liu et al., “Comprehensive graph gradual pruning for sparse training in
graph neural networks,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35,
no. 10, pp. 14903–14917, Oct. 2024.
[91] R. Sinkhorn and P. Knopp, “Concerning nonnegativematrices and doubly stochastic matrices,” Pacific J. Math., vol. 21, no. 2, pp. 343–348,
1967.
[92] M. Liu, Z. Wang, and S. Ji, “Non-local graph neural networks,” IEEE
Trans. Pattern Anal. Mach. Intell., vol. 44, no. 12, pp. 10270–10276,
Dec. 2022.
[93] T. Yang, Y. Wang, Z. Yue, Y. Yang, Y. Tong, and J. Bai, “Graph pointer
neural networks,” in Proc. AAAI Conf. Artif. Intell., 2022, pp. 8832–8839.
[94] J. Chen, W. Liu, and J. Pu, “Memory-based message passing: Decoupling
the message for propagation from discrimination,” in Proc. IEEE Int.
Conf. Acoust. Speech Signal Process., 2022, pp. 4033–4037.
[95] J. Chen, S. Chen, J. Gao, Z. Huang, J. Zhang, and J. Pu, “Exploiting neighbor effect: Conv-agnostic GNN framework for graphs with heterophily,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 10, pp. 13383–13396,
Oct. 2024.
[96] M. Chen, Z. Wei, Z. Huang, B. Ding, and Y. Li, “Simple and deep
graph convolutional networks,” in Proc. Int. Conf. Mach. Learn., 2020,
pp. 1725–1735.
[97] S. Suresh, V. Budde, J. Neville, P. Li, and J. Ma, “Breaking the limit of
graph neural networks by improving the assortativity of graphs with local
mixing patterns,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2021, pp. 1541–1551.
[98] D. Jin et al., “RAW-GNN: Random walk aggregation based graph neural
network,” in Proc. Int. Joint Conf. Artif. Intell., 2022, pp. 2108–2114.
[99] D. He, C. Liang, H. Liu, M. Wen, P. Jiao, and Z. Feng, “Block modelingguided graph convolutional neural networks,” in Proc. AAAI Conf. Artif.
Intell., 2022, pp. 4022–4029.
[100] J. Park, S. Yoo, J. Park, and H. J. Kim, “Deformable graph convolutional
networks,” in Proc. AAAI Conf. Artif. Intell., 2022, pp. 7949–7956.

ZHENG et al.: GNNS FOR GRAPHS WITH HETEROPHILY: A SURVEY

[101] L. Siqi, H. Dongxiao, Y. Zhizhi, J. Di, F. Shiyong, and W. Zhang,
“Integrating co-training with edge discrimination to enhance graph neural
networks under heterophily,” in Proc. AAAI Conf. Artif. Intell., 2025,
pp. 18960–18968.
[102] X. Ma et al., “A comprehensive survey on graph anomaly detection
with deep learning,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12,
pp. 12012–12038, Dec. 2023.
[103] Z. Gong et al., “Beyond homophily: Robust graph anomaly detection
via neural sparsification,” in Proc. Int. Joint Conf. Artif. Intell., 2023,
pp. 2104–2113.
[104] Y. Ma, X. Liu, N. Shah, and J. Tang, “Is homophily a necessity for graph
neural networks?,” in Proc. Int. Conf. Learn. Representations, 2022,
pp. 26342–26369.
[105] F. Luo, J. Z. Wang, and E. Promislow, “Exploring local community
structures in large networks,” in Proc. IEEE/WIC/ACM Int. Conf. Web
Intell., 2006, pp. 233–239.
[106] Y. Ding, E. Yan, A. Frazho, and J. Caverlee, “PageRank for ranking
authors in co-citation networks,” J. Amer. Soc. Inf. Sci. Technol., vol. 60,
no. 11, pp. 2229–2243, 2009.
[107] G. Xiao et al., “A hybrid visualization model for knowledge mapping: Scientometrics, SAOM, and SAO,” IEEE Trans. Intell. Transp. Syst., vol. 25,
no. 3, pp. 2208–2221, Mar. 2024, doi: 10.1109/TITS.2023.3327266.
[108] Z. Zhou et al., “GReTo: Remedying dynamic graph topology-task discordance via target homophily,” in Proc. Int. Conf. Learn. Representations,
2023, pp. 6694–6720.
[109] M. Li et al., “When hypergraph meets heterophily: New benchmark datasets and baseline,” in Proc. AAAI Conf. Artif. Intell., 2025,
pp. 18377–18384.
[110] P. Wang, S. Yang, Y. Liu, Z. Wang, and P. Li, “Equivariant hypergraph
diffusion neural operators,” in Proc. Int. Conf. Learn. Representations,
2023, pp. 16983–17006.
[111] Y. Li, R. Yu, C. Shahabi, and Y. Liu, “Diffusion convolutional recurrent
neural network: Data-driven traffic forecasting,” in Proc. Int. Conf. Learn.
Representations, 2018, pp. 2079–2094.
[112] S. Wang, Y. Li, J. Zhang, Q. Meng, L. Meng, and F. Gao, “PM2.5GNN: A domain knowledge enhanced graph neural network for PM2.5
forecasting,” in Proc. ACM Int. Conf. Adv. Geographic Inf. Syst., 2020,
pp. 163–166.
[113] N. Veldt, A. R. Benson, and J. Kleinberg, “Higher-order homophily is
combinatorially impossible,” 2022, arXiv:2103.11818.
[114] J. H. Fowler, “Legislative cosponsorship networks in the US house and
senate,” Social Netw., vol. 28, no. 4, pp. 454–465, 2006.
[115] I. Amburg, N. Veldt, and A. Benson, “Clustering in graphs and hypergraphs with categorical edge labels,” in Proc. ACM Web Conf., 2020,
pp. 706–717.
[116] P. S. Chodrow, N. Veldt, and A. R. Benson, “Hypergraph clustering: From
blockmodels to modularity,” Sci. Adv., vol. 7, 2021, Art. no. eabh1303.
[117] J. Lin, X. Guo, S. Zhang, D. Zhou, Y. Zhu, and J. Shun, “When heterophily
meets heterogeneity: New graph benchmarks and effective methods,”
2024, arXiv:2407.10916.
[118] Z. Shen and Z. Kang, “When heterophily meets heterogeneous graphs:
Latent graphs guided unsupervised representation learning,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 36, no. 6, pp. 10283–10296, Jun. 2025,
doi: 10.1109/TNNLS.2025.3540063.
[119] L. Sun et al., “Adversarial attack and defense on graph data: A survey,”
2018, arXiv:1812.10528.
[120] H. Wu, C. Wang, Y. Tyshetskiy, A. Docherty, K. Lu, and L. Zhu,
“Adversarial examples for graph data: Deep insights into attack and
defense,” in Proc. Int. Joint Conf. Artif. Intell., 2019, pp. 4816–4823.
[121] X. Zhang and M. Zitnik, “GNNGUARD: Defending graph neural networks against adversarial attacks,” in Proc. Int. Conf. Neural Inf. Process.
Syst., 2020, pp. 9263–9275.
[122] C. Deng, X. Li, Z. Feng, and Z. Zhang, “GARNET: Reduced-rank
topology learning for robust and scalable graph neural networks,” in Proc.
Learn. Graphs Conf., 2022, pp. 1–23.
[123] Y. Chen et al., “Understanding and improving graph injection attack by
promoting unnoticeability,” in Proc. Int. Conf. Learn. Representations,
2022, pp. 15404–15445.
[124] J. Zhu, J. Jin, D. Loveland, M. T. Schaub, and D. Koutra, “How does
heterophily impact the robustness of graph neural networks? Theoretical
connections and practical implications,” in Proc. ACM SIGKDD Int. Conf.
Knowl. Discov. Data Mining, 2022, pp. 2637–2647.
[125] H. Pei et al., “Multi-track message passing: Tackling oversmoothing and
oversquashing in graph learning via preventing heterophily mixing,” in
Proc. Int. Conf. Mach. Learn., 2024, pp. 40078–40091.

4403

[126] Y. Gao, X. Wang, X. He, Z. Liu, H. Feng, and Y. Zhang, “Alleviating
structural distribution shift in graph anomaly detection,” in Proc. ACM
Int. Conf. Web Search Data Mining, 2023, pp. 357–365.
[127] F. Shi, Y. Cao, Y. Shang, Y. Zhou, C. Zhou, and J. Wu, “H2-FDetector:
A GNN-based fraud detector with homophilic and heterophilic connections,” in Proc. ACM Web Conf., 2022, pp. 1486–1494.
[128] J. Pan et al., “A label-free heterophily-guided approach for unsupervised graph fraud detection,” in Proc. AAAI Conf. Artif. Intell., 2025,
pp. 12443–12451.
[129] Y. Gao, X. Wang, X. He, Z. Liu, H. Feng, and Y. Zhang, “Addressing heterophily in graph anomaly detection: A perspective of graph spectrum,”
in Proc. ACM Web Conf., 2023, pp. 1528–1538.
[130] X. Tang et al., “Prediction-uncertainty-aware decision-making for autonomous vehicles,” IEEE Trans. Intell. Veh., vol. 7, no. 4, pp. 849–862,
Dec. 2022.
[131] Y. Liu, X. Ao, F. Feng, and Q. He, “UD-GNN: Uncertainty-aware
debiased training on semi-homophilous graphs,” in Proc. ACM SIGKDD
Int. Conf. Knowl. Discov. Data Mining, 2022, pp. 1131–1140.
[132] D. Chen et al., “Bayesian hierarchical graph neural networks with uncertainty feedback for trustworthy fault diagnosis of industrial processes,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 12, pp. 18635–18648,
Dec. 2024.
[133] D. He et al., “Contrastive learning meets homophily: Two birds with one
stone,” in Proc. Int. Conf. Mach. Learn., 2023, pp. 12775–12789.
[134] Y. Li, B. Lin, B. Luo, and N. Gui, “Graph representation learning beyond
node and homophily,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 5,
pp. 4880–4893, May 2023.
[135] R. Ying, D. Bourgeois, J. You, M. Zitnik, and J. Leskovec, “GNNExplainer: Generating explanations for graph neural networks,” in Proc.
Int. Conf. Neural Inf. Process. Syst., 2019, pp. 9244–9255.
[136] D. Luo et al., “Parameterized explainer for graph neural network,” in
Proc. Int. Conf. Neural Inf. Process. Syst., 2020, pp. 19620–19631.
[137] C. Agarwal, O. Queen, H. Lakkaraju, and M. Zitnik, “Evaluating explainability for graph neural networks,” Sci. Data, vol. 10, no. 1, 2023,
Art. no. 144.
[138] W.-L. Chiang, X. Liu, S. Si, Y. Li, S. Bengio, and C.-J. Hsieh, “ClusterGCN: An efficient algorithm for training deep and large graph convolutional networks,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2019, pp. 257–266.
[139] H. Zeng, H. Zhou, A. Srivastava, R. Kannan, and V. Prasanna, “GraphSAINT: Graph sampling based inductive learning method,” in Proc. Int.
Conf. Learn. Representations, 2020, pp. 1979–1997.
[140] T. Xiao, Z. Chen, Z. Guo, Z. Zhuang, and S. Wang, “Decoupled selfsupervised learning for graphs,” in Proc. Int. Conf. Neural Inf. Process.
Syst., 2022, pp. 620–634.
[141] S. Zhou, Z. Guo, C. Aggarwal, X. Zhang, and S. Wang, “Link prediction on heterophilic graphs via disentangled representation learning,”
2022, arXiv:2208.01820.
[142] Z. Du, J. Liang, J. Liang, K. Yao, and F. Cao, “Graph regulation network
for point cloud segmentation,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 46, no. 12, pp. 7940–7955, Dec. 2024.
[143] S. Wang et al., “Multi-domain graph foundation models: Robust knowledge transfer via topology alignment,” in Proc. Int. Conf. Mach. Learn.,
2025, pp. 64806–64821.
[144] S. Wang, S. Huang, J. Yuan, Z. Shen, and Z. Kang, “Cooperation of
experts: Fusing heterogeneous information with large margin,” in Proc.
Int. Conf. Mach. Learn., 2025, pp. 63169–63185.
[145] A. Mele, “A structural model of homophily and clustering in social networks,” J. Bus. Econ. Statist., vol. 40, no. 3, pp. 1377–1389,
2022.
[146] Y. Choi, J. Choi, T. Ko, H. Byun, and C.-K. Kim, “Finding heterophilic
neighbors via confidence-based subgraph matching for semi-supervised
node classification,” in Proc. ACM Int. Conf. Inf. Knowl. Manage., 2022,
pp. 283–292.
[147] B.-M. Liu, Y.-L. Gao, F. Li, C.-H. Zheng, and J.-X. Liu, “SLGCN:
Structure-enhanced line graph convolutional network for predicting drug-disease associations,” Knowl.-Based Syst., vol. 283, 2024,
Art. no. 111187.
[148] S. Maekawa et al., “Beyond real-world benchmark datasets: An empirical
study of node classification with GNNs,” in Proc. Int. Conf. Neural Inf.
Process. Syst., 2022, pp. 5562–5574.
[149] H. Chen, Y. Lu, Y. Yang, and Y. Rao, “A drug combination prediction
framework based on graph convolutional network and heterogeneous
information,” IEEE/ACM Trans. Comput. Biol. Bioinf., vol. 20, no. 3,
pp. 1917–1925, May/Jun. 2023.

4404

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 38, NO. 7, JULY 2026

[150] H. Kim, J. Choi, and J. J. Whang, “Dynamic relation-attentive graph
neural networks for fraud detection,” 2023, arXiv:2310.04171.
[151] Y. Wang et al., “Label information enhanced fraud detection against low
homophily in graphs,” in Proc. ACM Web Conf., 2023, pp. 406–416.

Xin Zheng received the PhD degree in computer
science from Monash University, Australia, in 2024.
She is a lecturer with the School of Computing Technologies, RMIT University, Australia. Her research
interests include data-centric graph machine learning
and automated graph MLOps. To date, she has published research papers in top-tier journals and conferences, including International Journal of Computer
Vision, Pattern Recognition, NeurIPS, ICLR, ICML,
and Web Conference.

Yi Wang received the PhD degree in computer science and technology from Zhejiang Normal University, Jinhua, China, in 2025. She is presently a
postdoctoral fellow with the City University of Hong
Kong. She has published several papers in top-tier
journals and conferences, inclusing IEEE Transactions on Cybernetics, Pattern Recognition, Neural
Networks, ICML, AAAI, IJCAI. Her research interests include graph neural networks, hypergraph
computing, graph data mining, etc.

Yixin Liu received the bachelor’s and master’s degrees from Beihang University, China, and the PhD
degree in Artificial Intelligence (AI) from Monash
University, Australia. He is a lecturer and ARC DECRA fellow with Griffith University. His research
concentrates on data mining, machine learning, graph
analytics, and anomaly detection. To date, he has
published more than 30 research papers in top-tier
journals and conferences, including IEEE Transactions on Knowledge and Data Engineering, IEEE
Transactions on Neural Networks and Learning Systems, NeurIPS, KDD, AAAI, and Web Conference. He is a recipient of Google
PhD fellowship, in 2022.

Ming Li (Member, IEEE) received the PhD degree
from the Department of Computer Science and Information Technology, La Trobe University, Australia,
in 2017. After that, he completed two postdoctoral
fellowship positions with the Department of Mathematics and Statistics, La Trobe University, Australia,
and the Department of Information Technology in
Education, South China Normal University, China,
respectively. He is currently a ‘Shuang Long Scholar’
distinguished professor with Zhejiang Key Laboratory of Intelligent Education Technology and Application, Zhejiang Normal University, China. His research interests include hypergraph/graph neural networks, graph machine learning, hypergraph learning,
etc. To date, he has published more than 150 research papers in top-tier journals
and conferences, including IEEE Transactions on Pattern Analysis and Machine
Intelligence, Artificial Intelligence, IEEE Transactions on Knowledge and Data
Engineering, IEEE Transactions on Neural Networks and Learning Systems,
IEEE Transactions on Cybernetics, ICML, AAAI etc. He is an associate editor
of Pattern Recognition, Neural Networks, and an editorial board member of
Machine Learning. He is the recipient of the AAAI 2026 Outstanding Paper
Award.

Miao Zhang received the PhD degree from the University of Technology Sydney (UTS), Australia. He
is currently a professor with the Harbin Institute of
Technology (Shenzhen), Shenzhen, China. Before
that, he was an assistant professor with Aalborg
University, Aalborg, Denmark. His major research
interests include AutoML, model compression, and
continual learning.

Di Jin received the PhD degree in computer science
from Jilin University, Changchun, China, in 2012.
He was a research scholar with DMG, UIUC during
2019 to 2020. He is currently a full professor with the
College of Intelligence and Computing, Tianjin University, Tianjin, China. His research interests include
graph data mining and graph machine learning, especially on community detection, network embedding
and GNNs. To date, he has published more than 100
research papers in top-tier journals and conferences,
including IEEE Transactions on Knowledge and Data
Engineering, IEEE Transactions on Neural Networks and Learning Systems,
IEEE Transactions on Cybernetics, AAAI, IJCAI, ICML, NeurIPS, and WWW.
He serves as the associate editor of Information Sciences, action editor of
Neural Networks, PC board member of IJCAI 2022–2024, and Senor PCs in
IJCAI/AAAI. He was the recipient of the Best Paper Award Runner-Up of
WWW 2021, Best Paper Student Paper Runner-Up of ICDM 2021, and Rising
Star Award of ACM Tianjin at 2018.

Philip S. Yu (Fellow, IEEE) received the BS degree
in electrical engineering from National Taiwan University, and the MS and PhD degrees in electrical
engineering from Stanford University, in 1978. He is a
distinguished professor with the University of Illinois
at Chicago and Tsinghua University. He holds more
than 300 US patents, is ACM fellow, is editor-in-chief
of ACM Transactions on Knowledge Discovery from
Data, and has been awarded several awards by IBM
and the IEEE. His research interests are in the fields
of data mining, social network, privacy preserving
data publishing, data stream, database systems, and Internet applications and
technologies. He is an ISI Highly Cited Researcher. According to Google
Scholar, his H-index is among the ten highest in computer science.
Shirui Pan (Senior Member, IEEE) received the PhD
degree in computer science from the University of
Technology Sydney (UTS), Ultimo, NSW, Australia.
He is a professor with the School of Information
and Communication Technology, Griffith University,
Australia. Prior to this, he was a senior lecturer with
the Faculty of IT with Monash University. His research interests include data mining and machine
learning. To date, he has published more than 200
research papers in top-tier journals and conferences,
including IEEE Transactions on Pattern Analysis and
Machine Intelligence, IEEE Transactions on Knowledge and Data Engineering,
IEEE Transactions on Neural Networks and Learning Systems, ICML, NeurIPS,
and KDD. His research received the 2024 CIS IEEE TNNLS Outstanding
Paper Award and the 2020 IEEE ICDM Best Student Paper Award. He has
been recognised as one of the AI 2000 AAAI/IJCAI Most Influential Scholars
in Australia since 2021. He is an ARC future fellow and a fellow of the
Queensland Academy of Arts and Sciences (FQA). He is an associate editor of
Neural Networks, Knowledge and Information Systems, IEEE Transactions on
Cognitive and Developmental Systems, and IEEE Transactions on Cybernetics
(TCYB).
PAPER_TEXT
