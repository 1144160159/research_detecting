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
# [453] Graph Anomaly Detection via Multiscale Contrastive Self-Supervised Learning From Local to Global
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
编号：453
题名：Graph Anomaly Detection via Multiscale Contrastive Self-Supervised Learning From Local to Global
年份：2024
DOI：10.1109/tcss.2024.3457161
来源：IEEE Transactions on Computational Social Systems
PDF：paper/10.1109_TCSS.2024.3457161.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测、图学习、知识图谱与威胁情报
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\453.txt
- 原始字符数：66883
- 本次发送字符数：66883
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 12, NO. 2, APRIL 2025

485

Graph Anomaly Detection via Multiscale
Contrastive Self-Supervised Learning
From Local to Global
Xiaofeng Wang , Shuaiming Lai , Shuailei Zhu , Yuntao Chen , Laishui Lv , and Yuanyuan Qi

Abstract—Graph anomaly detection is a challenging task in
graph data mining, aiming to recognize unconventional patterns
within a network. Recently, there has been increasing attention
on graph anomaly detection based on contrastive learning due to
its high adaptability to the sample imbalance problem. However,
most existing work typically focuses on the contrast of local
views while neglecting global comparison information, leading
to suboptimal performance. To address this issue, we introduce
a new multiscale contrastive self-supervised learning framework
for graph anomaly detection (GADMCLG). Our approach incorporates local-level contrasts involving node–node and node–
subgraph contrast, and global-level subgraph–subgraph contrast.
The former mines localized abnormal information, while the latter is intended to capture global anomalous patterns. Specifically,
our proposed subgraph–subgraph contrast adopts the h-order
neighbor subgraph sampling instead of augmented subgraphs
through edge perturbation. This sampling strategy ensures a
comprehensive observation of the neighborhood surrounding the
target node, thereby mitigating the introduction of extraneous
noise and providing interpretability for the detected results.
Furthermore, we incorporate a subgraph centralization technique to reduce the bias caused by the absolute position of
subgraphs in the attribute space, which enhances the model’s
ability to identify anomalies at different scales. Extensive experimental results on six real-world datasets demonstrate the
effectiveness of our method and its superiority compared with
state-of-the-art approaches.
Index Terms—Contrastive learning, graph anomaly detection, multiscale framework, subgraph centralization, subgraph
sampling.

I. INTRODUCTION

G

RAPH anomaly detection is one of the most important
tasks in graph machine learning, which seeks to identify
atypical graph patterns, including anomalous nodes, edges, and
subgraphs in a given graph [1]. Node anomaly detection focuses
on exploring individual data instances within the graph that deviate from expected patterns, making it the most prevalent task

Received 12 January 2024; revised 10 July 2024; accepted 6 September
2024. Date of publication 30 September 2024; date of current version
3 April 2025. This work was supported by the “Leading Goose” R&D
Program of Zhejiang Province under Grant 2024C01107. (Corresponding
author: Xiaofeng Wang.)
The authors are with the School of Information Engineering, China Jiliang
University, Hangzhou 310018, China (e-mail: xfwang@cjlu.edu.cn).
Digital Object Identifier 10.1109/TCSS.2024.3457161

in graph anomaly detection. Recently, graphs have emerged as a
universal data structure for modeling diverse complex systems.
Consequently, anomaly detection on graphs has garnered growing attention [2]. Graph anomaly detection techniques have
found application in diverse fields, including fraud detection
[3], social network analysis [4], recommendation systems [5],
and network security [6]. In these domains, graph anomaly
detection plays a crucial role in informing decision-making
processes and facilitating effective problem-solving endeavors.
Traditional anomaly detection approaches face challenges in
effectively addressing this issue due to the intricate nature of
on-Euclidea graph-structured data [1]. Specifically, graphs emphasize the complex structural relationships between objects,
which provides valuable auxiliary information for anomaly detection. In online social networks, malicious social bots usually
build relationships with a large number of normal users to
obtain user privacy information and can also disguise themselves by imitating the behavior of normal users [7]. In such
cases, traditional techniques may not be able to distinguish
between fake users and normal users based solely on attribute
information. Furthermore, the differences in topology and attributes give rise to two principal categories of graph anomalies:
structural anomalies and attribute anomalies [8] in Fig. 1. Nodes
A and C are identified as attributed anomalies, while nodes A
and B are identified as structural anomalies. The former refers
to nodes within the graph that exhibit dissimilar interaction
behaviors in comparison with other nodes, signifying disparities
in the structural connectivity of the network. The latter involves
interconnected nodes that exhibit unusual node attributes, highlighting the inconsistency of node attributes.
Over the past decade, numerous graph anomaly detection
methods have been proposed. Early work such as LOF [9],
AMEN [10], and ANOMALOUS [11] primarily utilized specific domain knowledge on graphs to identify anomalies, relying on manual feature engineering and statistical models.
These conventional approaches fail to capture the nonlinear
characteristics of nodes and scale to large-scale graphs. To
address these limitations, deep learning has been introduced
to uncover anomalous graph patterns, leveraging its success
in representation learning and pattern recognition [12]. Deep
neural networks with nonlinearity exhibit significant advantages in handling large-scale data and learning distributed representations for uncovering anomalies [13]. To capture more

2329-924X © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

486

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 12, NO. 2, APRIL 2025

(b)

(a)
(c)
Fig. 1.

Toy example of two basic types of graph anomalies.

discriminated information in graph data for anomaly detection,
graph representation learning techniques have been widely exploited [14], [15], [16]. For example, Hu et al. [17] proposed an
effective embedding approach to identify structural anomalies
by analyzing the relationship between nodes and communities.
Moreover, many typical shallow models for graph embedding
such as DeepWalk [18] and node2vec [19] have been used for
generating node representations in graph anomaly detection.
Recently, graph neural networks (GNNs) have been introduced to graph anomaly detection, attracting increasing
attention due to their highly expressive capability in graph
representation learning [8]. As a pioneering work, DOMINANT
[20] utilizes a graph auto-encoder (GAE) based on a graph
convolutional network (GCN) to identify anomalies in an unsupervised setting, where anomaly scores for nodes are calculated
by leveraging the reconstruction errors of node attributes and
graph structure. Subsequently, some variants were proposed,
such as SpecAE [21], ALAMR [22], and ComGA [23]. GAEbased methods do not directly identify anomalous targets, making it difficult to fully utilize the rich information present in the
attribute network [8]. Moreover, based on the self-supervised
learning paradigm, CoLA [24] introduces a novel approach by
combining contrastive learning with GNNs, which identifies
anomalies by measuring the consistency between a target node
and its neighboring nodes. On this basis, ANEMONE [25]
captures more subtle abnormal information by building additional contrast between the target node and its masked nodes.
Furthermore, GCAD [26] identifies anomalies by comparing
the similarity between subgraphs. However, these methods typically employ a local contrastive mode or a single-scale contrast,
while ignoring potential global anomaly information in complex graph-structured data.
To address this issue, we propose a novel graph anomaly
detection method via multiscale contrastive self-supervised
learning from local to global, denoted as GADMCLG. It integrates the local- and global-level contrasts to comprehensively detect anomalies in attributed graphs. Specifically, the
local-level contrasts include node–node and node–subgraph
contrasts. We utilize the node–subgraph contrast to capture
potential matching patterns between each normal node and
its corresponding neighbor subgraph sampled through random
walk (RW). Moreover, the node–node contrast is used to mine
more subtle local abnormal information. For the global-level
contrast, we propose a subgraph–subgraph contrast based on the

h-order neighbor subgraph sampling strategy. Different from
the existing method [27] that relies on edge modification to
construct subgraph–subgraph contrast, our approach ensures a
comprehensive observation of the neighborhood of the target
node from local to global perspectives, thereby mitigating the
introduction of extraneous noise. Furthermore, we perform subgraph centralization on all subgraphs to reduce the deviation
caused by their absolute position in the attribute space. Finally,
we design a multiscale contrastive learning framework by combining both local and global-level contrasts to identify potential abnormal nodes. The main contributions are summarized
as follows.
1) We propose a novel graph anomaly detection method
that leverages the synergy between local and global contrastive patterns to effectively identify node anomalies in
attributed graphs.
2) We investigate the effects of various subgraph sampling
methods on contrastive learning and conclude that the
h-order neighborhood subgraph sampling strategy is the
most suitable for the graph anomaly detection task.
3) Extensive experiments on six real-world datasets demonstrate the effectiveness of the proposed method and its
advantages compared to state-of-the-art baselines.
The rest of the sections of this article are organized as follows. In Section II, we provide a general review of related
work. Section III introduces fundamental concepts employed
in this work and outlines the task objective of anomaly detection on attributed networks. We provide a detailed presentation
of the proposed method in Section IV. Section V evaluates
and analyzes the experimental results conducted across various datasets. Finally, Section VI presents the conclusion of
our work.
II. RELATED WORK
Our work addresses the issue of graph anomaly detection
using graph contrastive learning in attributed graphs. In this
section, we first review the primary methods of graph anomaly
detection and then introduce the pertinent work on graph contrastive learning.
A. Graph Anomaly Detection
Graph anomaly detection is a crucial topic in graph data
mining, primarily employed to identify patterns that deviate
from the majority within a graph. Much early work has been
proposed to identify node anomalies. Breuning et al. [9] introduced a density-based local method LOF, which identifies
anomalous nodes by comparing the attribute characteristics of
their neighboring nodes. AMEN [10] focuses on identifying
anomalous entities based on their local connectivity within the
graph. Additionally, ANOMALOUS [11] utilizes a joint framework to leverage both structural properties and node attributes
to reveal inherent patterns and identify anomalies. These traditional approaches primarily utilized specific domain knowledge on graphs to identify anomalies but failed to capture the
nonlinear features of nodes, lacking deeper insight into graph
data [1].

WANG et al.: GRAPH ANOMALY DETECTION VIA MULTISCALE CONTRASTIVE SELF-SUPERVISED LEARNING

GNNs have emerged as an effective tool for graph representation learning, with the ability to extract complex nonlinear information. Consequently, numerous GNN-based methods have
been proposed to uncover graph anomalies by learning expressive and informative node representations. DOMINANT [20]
first introduces an anomaly detection approach based on GAE,
which uncovers node anomalies by reconstructing both graph
structure and node attributes in a supervised manner. SpecAE
[21] utilizes GAE to extract low-dimensional embedding and
performs anomaly detection via density estimation. Furthermore, ComGA [23] proposes a community-aware structure encoder and integrates a customized deep graph convolutional
network to address the challenge of over-smoothing in GNNs.
Moreover, AEGIS [28] extends GAE to the inductive setting,
accommodating scenarios where previously unseen anomalies
may be present. Despite the remarkable performance achieved
by these methods in anomaly detection, it is noteworthy that
they do not explicitly frame anomaly detection as a dedicated
task, leading to suboptimal performance.
Recent studies have demonstrated that graph contrastive
learning benefits graph-based machine learning tasks [29]. Consequently, the combination of graph contrastive learning for
anomaly detection has received increasing attention. As a local
contrastive learning method, CoLA [24] identifies anomalies
by calculating the consistency between the target node and
its neighboring nodes. Furthermore, SL-GAD [30] develops
both generative attribute regression and contrastive learning
framework to detect graph anomalies. ANEMONE [25] further
combines the node–node contrast with the node–subgraph contrast and focuses on mining the local anomalous information.
Moreover, GCAD [26] introduces a method based on global
contrastive learning, which adopts subgraph–subgraph contrast
to mine global anomaly information but ignores local anomaly
patterns. GCCAD [31] designs a context-aware GNN encoder to
learn both node and context representations, detecting abnormal
information through the similarity between them.
B. Graph Contrastive Learning
As one of the most crucial paradigms in graph self-supervised
learning, graph contrastive learning extracts supervised signals
for downstream tasks without explicit labels by maximizing the
mutual information (MI) between instances possessing similar semantic information [29]. Graph contrastive learning has
gained popularity for its ability to capture complex relationships
and structures in graph-structured data. Considering the scale
differences in MI between instances, the existing work on graph
contrastive learning can be mainly divided into two types: sameand cross-scale contrastive learning [32].
The same-scale contrast approaches for contrastive learning
can be further divided into node- and graph-level contrasts.
The underlying assumption of node-level contrastive learning
is that nodes with similar contextual information should have
similar representations. Early methods such as DeepWalk [18]
and Node2Vec [19] utilize RW to extract contextual details surrounding target nodes in unattributed networks. Furthermore,
GraphSAGE [33] further extends RW to attribute networks

487

and introduces a new graph convolutional network to inductively learn node embeddings. Different from these methods,
recent work has shifted toward exploring more intricate semantic information by employing graph augmentation techniques.
GRACE [34] leverages node feature masking and edge dropping to create two contrastive views, bringing closer representations of the same node in different views. Moreover, GCA
[35] introduces the adaptive augmentation of graph-structured
data based on the underlying graph properties, enriching the
semantic information. On the other hand, graph-level methods
utilize similar augmentation techniques and contrastive frameworks and employ readout functions on node representations
to learn graph-level embeddings. JOAO [36] introduces a joint
augmentation optimization strategy, cohesively optimizing augmentation selection and contrastive objectives. Besides, CSSL
[37] is constructed upon the foundation of MoCo [38] and
reduces model overfitting via graph-level contrastive learning.
The cross-scale approaches for contrastive learning emphasize the global comparison of views at different scales. As the
pioneering work, DGI [39] proposes a patch-global contrast
that contrasts node-level embeddings with graph-level representations to maximize the MI between these distinct scales of
representation so as to aid the graph encoder in capturing both
localized and global semantic information. Furthermore, HDGI
[40] extends DGI to heterogeneous graphs by aggregating node
representations on various meta paths to calculate the final node
representation. Moreover, EGI [41] captures advanced transferable graph knowledge by forcing node features to maintain a
consistent distribution with graph structure and then maximizes
the MI between node embeddings and their surrounding egographs. From the perspective of context-global contrasts, BiGI
[42] learns the graph-level representation of the input graph by
aggregating two types of node embeddings in a bipartite graph,
as well as learning the local context representation of the target
edge between two nodes over the sampled original graph. Besides, HTC [43] maximizes the MI between the representation
of the entire graph and the contextual embedding calculated
through aggregated sampling graphs.
III. PROBLEM DEFINITION
In this section, we introduce the task of graph anomaly detection in attributed networks and provide an overview of the
notations used throughout this work. Table I summarizes the
key notations used in this article.
Attributed Networks: For the given attributed network G =
(V, E), V = {v1 ,v2 , . . . ,vN } denotes the node set with N nodes,
and E indicates the edge set with M edges. Moreover, the
adjacency matrix A ∈ Rn×n and feature matrix X ∈ Rn×d represent the graph-structured information and the node-attribute
information, respectively. It notes that Aij = 1 indicates that
there is an edge between node vi and node vj , otherwise
Aij = 0.
Graph Anomaly Detection: The task of graph anomaly detection is to learn an anomaly scoring function f (·), which computes the anomaly score for each node. The higher value of the
score indicates a greater likelihood that the node is anomalous.

488

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 12, NO. 2, APRIL 2025

(a)

(b)

(c)

Fig. 2. Overview of the proposed GADMCLG. (a) Instance pair sampling module. (b) Multi-scale contrastive learning module. (c) Anomaly scoring
module.

TABLE I
NOTATIONS AND DESCRIPTION TO GADMCLG
Notation

Description

G
V
E
A ∈ Rn×n
X ∈ Rn×d

Attributed network.
Node set of G.
Edge set of G.
Adjacency matrix of G.
Attribute matrix of G.


H() ∈ Rn×d


W() ∈ Rd ×d

 − th layer hidden embedding matrix.
 − th layer network parameters.

φ(vi )
Zvi

Final node embedding of node vi .
WL-embedded vector of the entire subgraph with
Node vi as the source node.

f (vi )

Final anomaly score of node vi .

IV. METHODOLOGY
In this section, we introduce the proposed method GADMCLG, and its overall framework is shown in Fig. 2. GADMCLG consists of three main components: an instance pair
sampling module, a multiscale contrastive learning module,
and an anomaly scoring module. Specifically, in the instance
pair sampling module, we first adopt random walk with restart
(RWR) [44] and h-order neighbor sampling strategy to construct
two different subgraph sample pools for local- and global-level
contrasts, respectively. Subsequently, the multiscale contrastive
learning module extracts local anomalous information within
local-level node–subgraph and node–node contrasts while simultaneously capturing global anomalous information through
subgraph–subgraph contrast. Finally, the anomaly scoring module calculates the final anomaly score for each node in the graph,
which is obtained through the weighted aggregation of anomaly
scores derived from the three distinct contrastive mechanisms.

A. Contrastive Instance Pair Sampling
To comprehensively capture local and global anomalous information, GADMCLG employs contrastive learning across
various scales. In the context of graph contrastive learning,
contrastive instance pair sampling involves selecting pairs of
nodes or subgraphs in a graph, where positive pairs might be
nodes that are close in proximity or share similar attributes,
and negative pairs are nodes that are far apart or have distinct
features. It notes that the effectiveness of contrastive learning
methods heavily depends on the definition of the contrastive
instance pairs. In this article, we adopt the RWR and h-order
neighbor sampling strategy instead of random sampling by edge
perturbation to construct two different subgraph sample pools
for local and global contrasts, respectively.
First, we define the node–subgraph contrast and node–node
contrast to capture the local distribution pattern of nodes within
the graph. Specifically, for the node–subgraph contrast, a target node needs to be selected first, and then the contrastive
subgraphs of the target node are sampled by RWR and form
contrastive positive pairs with the target node. In particular, to
prevent the information leakage of the initial node of RWR
during the contrastive learning process, we substitute the attribute vector with a zero vector to mask its node attribute.
Subsequently, the node–node contrast is composed of the target
node and masked initial node of RWR, which can mine more
potential local anomalous information. It notes that positive
and negative instance sampling strategies need to be adopted in
local-level contrasts. For positive instance pairs, the initial node
of the RWR corresponds to the target node, while for negative
instance pairs, the initial node is randomly selected from all
nodes except the target node.
Moreover, to establish the global connection between all
the subgraphs, we define the subgraph–subgraph contrast that
compares the structural similarity between different subgraphs

WANG et al.: GRAPH ANOMALY DETECTION VIA MULTISCALE CONTRASTIVE SELF-SUPERVISED LEARNING

489

matching patterns between each normal node and its corresponding neighbor subgraph sampled through RWR. Node–
subgraph contrast follows the assumption that normal nodes
should maintain a high degree of consistency with their neighboring nodes, while abnormal nodes should be the opposite.
To calculate the consistency between the target node and its
contrastive subgraph, we initially utilize a GNN encoder with a
GCN layer [GNN encoder 1 in Fig. 2(b)] to map node attributes
in the subgraph to the embedding space. The subgraph hiddenlayer representation can be expressed as


−1
−1
(+1)
()
= σ D̃i 2 Ãi D̃i 2 Hi W()
(1)
Hi
Fig. 3.

Process of subgraph centralization.

globally. Different from the approach of subgraph sampling
for the local contrasts, for subgraph–subgraph contrast, the
subgraph of the target node is obtained by the h-order neighbor
sampling strategy. Specifically, this sampling strategy extracts
the adjacent nodes directly connected to the target node at a
specified depth h.

where Hi () denotes th layer hidden representation of ith sub−(1/2)
−(1/2)
Ãi D̃i
graph, D̃i
is the normalized adjacency matrix
()
of ith subgraph, W indicates the trainable weight parameters
in th layer network, and σ(·) is the nonlinear activation function such as ReLU. We utilize a Readout function to calculate
the final representation zi of ith subgraph. The Readout function
can be denoted as follows:
zi = Readout(Hi ) =

ni

(Hi )j
j=1

B. Subgraph Centralization
As previously mentioned, subgraph–subgraph comparison
involves comparing the structures of individual h-subgraphs.
These structures are determined by the relative positions of
nodes in the h-subgraph but are independent of the absolute
positions of nodes in the node vector space. It notes that the
absolute positions of subgraphs in the attribute space may cause
bias in the similarity calculation between subgraphs. To address
this issue, we perform attribute centralization on all subgraphs
to generate the relative positions of all subgraphs. Specifically,
we map all target nodes to the origin of the node-attribute space,
and accordingly, other nodes in the corresponding subgraph are
transformed to the same degree as their target nodes being transformed to the origin. This process is described in Fig. 3, where
subgraphs G  (v1 ) and G  (v2 ) represent the state of subgraphs
G(v1 ) and G(v2 ) after subgraph centralization.
C. Multiscale Contrastive Learning Module
After the instance pair sampling process, a multiscale contrastive learning module is used to capture robust and discriminative feature representations in attributed graphs for anomaly
detection in a self-supervised manner. Contrastive learning has
proven to be effective for graph anomaly detection. However,
most approaches rely on local- or single-scale contrast, which
may limit their capability to capture comprehensive anomalous
information. In this work, we construct a multiscale graph
contrastive learning module, including local- and global-level
contrast. Specifically, this module consists of three components: node–subgraph contrast, node–node contrast, and global
subgraph–subgraph contrast.
1) Node–Subgraph Contrast: To capture local anomalies,
we first utilize the node–subgraph contrast to capture potential

ni

(2)

where Hi is the embedding of the ith subgraph after GCN
mapping, and ni is the number of all nodes in the ith subgraph.
Since the target node vi lacks structural information, we
utilize a multilayer perceptron (MLP) to obtain its embedding
so that it can be contrasted with its contrastive subgraph in the
same attribute space. The MLP hidden layer is defined as
hi (+1) = σ(hi () W() )

(3)

where W() is the weight matrix shared with GCN layer. ei is
the final embedding of the target node. After that, we adopt a
bilinear model to calculate the similarity si of the target node
and its contrastive subgraph
si = Bilinear(zi , ei ) = σ(zi Wei T ).

(4)

It notes that the target node and its contrastive subgraph tend
to be similar in positive pairs, while in negative pairs, they
should be dissimilar. Therefore, based on this observation, we
employ binary cross entropy (BCE) loss to train the contrast
LN S = −

N


(yi log(si ) + (1 − yi ) log(1 − si ))

(5)

i=1

where the value of yi is 1 in positive pairs and 0 in negative
pairs.
2) Node–Node Contrast: Similar to the node–subgraph contrast, node–node contrast focuses on capturing the local anomalous information at the node level. It notes that the representation of the masked initial node of RWR is aggregated from the
other nodes present in the subgraph. We establish a positive pair
between the target node and its masked node while forming a
negative pair between the target node and other masked nodes
that are not target nodes. After that, an additional GNN model

490

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 12, NO. 2, APRIL 2025

with a GCN layer [GNN encoder 2 in Fig. 2(b)] is employed
to learn the representation of the subgraph


− 1
− 1
(+1)
()
(6)
Hi
= σ D̃i 2 Ãi D̃i 2 Hi W()
()

where Hi denotes th layer hidden representation of ith sub−(1/2)  −(1/2)
graph, D̃i
is the normalized adjacency matrix
Ãi D̃i
of ith subgraph, and W() indicates the parameter matrix.
(+1)
hi  (+1) = Hi
[1, :] is the representation of the masked
initial node vi  of RWR in the ( + 1)th hidden layer and ui
is the final embedding of vi  . We leverage MLP to transform
the target node attribute to the same embedding space as the
masked target node


(+1)
()
(7)
= σ hi W()
hi
where W() is the same parameter matrix in Eq. (6). After MLP
ei  is the final embedding of the target node.
Similarly, we utilize a Bilinear model to calculate the similarity si  between ei  and ui . Subsequently, the loss associated
with node–node contrast can be computed as follows:
LN N = −

N


(yi log(si ) + (1 − yi ) log(1 − si ))

(8)

i=1

where the value of yi  is 1 in positive pairs and is 0 in negative
pairs.
3) Subgraph–Subgraph Contrast: Intuitively, each node in
the network is more susceptible to the influence of its directly
connected neighboring nodes. Therefore, abnormal nodes can
often be represented through abnormal subgraphs. To capture
global-level abnormal nodes, we score every node by calculating the similarity between all n subgraphs. The node vi will
have a higher anomaly score if its subgraph with vi as the source
node is different from most other subgraphs in the network.
Before calculating the similarity between subgraphs, we use
Weisfeiler–Lehman (WL) [45] to learn subgraph embeddings.
Specifically, we use the average neighborhood information of
nodes to iteratively update their vectors. The iterative updating
process of node vi can be expressed as

1
1
Xk (vi ) = (Xk−1 (vi ) +
X k−1 (w)) (9)
2
deg(vi )

D. Anomaly Scoring Module
After completing the training process in the multiscale contrastive learning module, the anomaly scoring module is used
to calculate the node’s anomaly score. For different contrasts,
normal nodes typically exhibit obvious similarities or dissimilarities when compared to instances in positive and negative
pairs. However, abnormal nodes are not distinguishable from
positively and negatively aligned instances. Here, we compute
the final anomaly score of each node from both local and
global perspectives.
1) Local Anomaly Score: Local-level contrast consists of
node–subgraph and node–node contrasts. A normal node exhibits similarity to its contrastive subgraph with it as the source
node in positive pairs, while exhibiting dissimilarity in its negative pair. So that the anomaly score of the target node vi can
be calculated as follows:
p
n
sns
i = si − si

n
p
snn
i = si − si
nns
ns
si = βsi + (1 − β)snn
i

(12)

where sns
and snn
denote the anomaly score to the node–
i
i
subgraph and node–node contrast, respectively, sni and spi represent the similarity to the node–subgraph contrast in negative
and positive pairs, respectively, si n and si p represent the similarity to the node–node contrast in negative and positive pairs,
respectively, and β is the balance parameter of node–subgraph
is the anomaly score of the local
and node–node contrast. snns
i
contrast after balancing the scores of node–subgraph and node–
node contrast. It notes that the subgraph obtained from one
RWR will lead to an incomplete observation of anomalous
information. To this end, we conduct multiround detections,
and the anomaly score of the target node vi can be represented
as follows:
1  nns(r)
s̄i =
s
R r=1 i


R 

1 
nns(r)
nns
si
si = s̄i + 
− s̄i
R r=1
R

(13)

w∈N (vi )

k

where X (vi ) denotes the vector of the node vi in the kth
iteration, deg(vi ) indicates the degree of node vi , and N (vi ) is
the set of one-hop neighbors of node vi in the target subgraph.
It notes that the final node embedding φ(vi ) of node vi is the
concatenation of vector from each iteration
φ(vi ) = [X0 (vi ), . . . , Xk (vi )]T .

(10)

Therefore, the WL-embedded vector zvi of the entire target
subgraph with the node vi as the source node can be calculated
as follows:

1
φ(u)
(11)
zv i =
|Vsub_vi |
u∈Vsub_vi

where Vsub_vi indicates the subgraph with the node vi as the
source node.

where s̄i is the mean from multiround detections, and R is the
total rounds of anomaly detection.
2) Global Anomaly Score: After the WL-embedded vectors
of all the subgraphs are computed, a point anomaly detector
based on Euclidean distance is trained from them and produces
an anomaly score s for the node vi , which is the source
node of the ith subgraph. Given that the depth of subgraphs
may be greater than 1, a depth-based weighted anomaly score
is introduced for further improvement of anomaly detection.
Specifically, for the target node vi , its anomaly score sss
i is the
weighted score between all the source nodes and a larger weight
will be given to sss
j if the node vj is closer to node vi

(vj ,vi ) 
s j
v ∈V λ
ss
si = j
(14)
(v
,v
j
i)
vj ∈V λ

WANG et al.: GRAPH ANOMALY DETECTION VIA MULTISCALE CONTRASTIVE SELF-SUPERVISED LEARNING

where V is the set of all score nodes, λ ∈ (0, 1) denotes the
weight to anomaly score sj , and (vj , vi ) indicates the number
of hops from node vj to node vi .
Finally, the anomaly score of the target node vi can be denoted as follows:
+ γsss
f (vi ) = snns
i
i

(15)

where γ is the balance parameter between the local anomaly
score derived from node–subgraph and node–node contrasts
and the global anomaly score from subgraph–subgraph contrast.
E. Loss Function
As shown in Fig. 2, the proposed GADMCLG model is
divided into three phases: contrastive instance pair sampling,
multiscale contrastive learning, and anomaly scoring. For the
anomaly detection task, the entire model is first trained with
sampled instance pairs in an unsupervised manner, and then the
inference process is performed to obtain the anomaly score of
each node. To combine the benefits of different contrasts, we
optimize the joint loss function:
L = βLN S + (1 − β)LN N

(16)

where β ∈ (0, 1) is the balance parameter of node–subgraph
and node–node contrast. It should be noted that, owing to the
utilization of the WL propagation scheme in learning subgraph
representations, the subgraph–subgraph contrast does not participate in joint training of node–subgraph and node–node contrasts. The overall procedures of our proposed GADMCLG are
depicted in Algorithm 1.
V. EXPERIMENTS
In this section, we conduct extensive experiments on nine
real-world graph datasets to demonstrate the excellent performance of GADMCLG. First, we provide an overview of the
datasets and experimental setup. Then, we validate the effectiveness of the proposed method and evaluate the experimental
results in a comparative view.

491

Algorithm 1 The Overall Procedures of GADMCLG.
Input: An attributed network G = (V, E); number of training
epoches T ; batch size B; subgraph depth h.
Output: Anomaly scoring function f (·).
1: for t ∈ T do
2:
Build positive and negative subgraph sample pools via
RWR in G.
3:
Randomly divide V into batches of size B.
4:
for b ∈ B do
5:
In node-subgraph contrast, calculate the embedding
similarity si of the target node vi and the subgraph
with vi as the source node in positive and negative
pairs via Eq. 4.
6:
In node-node contrast, calculate the embedding similarity si  of the target node and the masked initial
node of RWR in positive and negative pairs like nodesubgraph contrast.
7:
Calculate the joint loss L of node-subgraph and nodenode contrasts via Eq. 16.
8:
Backpropagation and update the trainable parameters
of our model.
9:
end for
10: end for
11: Calculate the joint anomaly score snns of node-subgraph
and node-node contrasts via multi-round detections.
12: for v ∈ V do
13:
Sample subgraphs with depth h.
14:
Perform subgraph centralization on all subgraphs and
Embed them to vectors via WL.
15: end for
16: Get the set Zall of all subgraph vectors.
17: for v ∈ V do
18:
Calculate anomaly score si  for zi with a point detector.
19: end for
20: Calculate the weighted scores sss via Eq. 14.
21: Calculate the final anomaly score f of all nodes.

A. Datasets
We first estimate the performance of GADMCLG and its
baseline methods on six injected anomaly graph datasets, which
include two social network datasets (BlogCatalog and Flickr
[46]) and five citation network datasets (ACM [47], Cora,
Citeseer, Pubmed [48], and ogbn-arxiv [49]). Note that the
ogbn-arxiv dataset, sourced from the open graph benchmark
(OGB), is a large-scale graph dataset comprising over 169 000
nodes and 1.1 million edges. Since these datasets lack groundtruth anomalies, we completely followed the anomaly injection
method in [11] and [14] to generate graph anomalies. Furthermore, to estimate the effectiveness of GADMCLG in real-world
scenarios, we use two real-world anomaly graph datasets used
in [23] and [50]. Among the real-world anomaly graph datasets,
Amazon [51] represents a copurchase network in which nodes
labeled as “amazonfail” are identified as abnormal, and Enron [52] is an email network where spammers are marked as
abnormal nodes. Detailed information about these datasets is
provided in Table II.

TABLE II
DETAILS OF DATASETS
Dataset

Nodes

Edges

Features

Anomalies

BlogCatalog
Flickr
ACM
Cora
Citeseer
Pubmed
ogbn-arxiv

5196
7575
16 484
2708
3327
19 717
169 343

171 743
239 738
71 980
5429
4732
44 338
1 166 243

8189
12 407
8337
1433
3703
500
128

300
450
597
150
150
600
6000

Amazon
Enron

1418
13 533

3695
176 987

28
20

28
5

B. Experimental Settings
In this section, we describe the experimental settings, encompassing the baseline methods for comparative analysis, evaluation metrics, and parameter settings for our model.

492

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 12, NO. 2, APRIL 2025

1) Baselines: To verify the effectiveness and advantage of
our proposed GADMCLG, we compare GADMCLG with six
state-of-the-art baseline methods.
a) DOMINANT [20]: DOMINANT is a typical method
based on deep learning, which utilizes a GAE to calculate
the reconstruction error of graph structure and node attributes, thereby detecting anomalies from both structural
and attribute perspectives simultaneously.
b) CoLA [24]: CoLA adopts a local contrastive selfsupervised learning approach, leveraging a GNN-based
encoder model to identify anomalies through an evaluation of the concordance between each node and its
neighboring subgraph.
c) SL-GAD [30]: SL-GAD integrates generative modeling
and contrastive self-supervised learning in graph anomaly
detection.
d) ComGA [23]: ComGA introduces a community-aware
structure encoder and integrates a customized deep graph
convolutional network to address the challenge of oversmoothing in GNNs.
e) GCAD [26]: GCAD is a global contrastive learning
method for graph anomaly detection, calculating the similarity of subgraphs to dig global anomalous information.
f) GRADATE [27]: It constructs a multiscale contrastive
learning network frame with an augmented view.
2) Metrics: To evaluate the performance of GADMCLG
and the baseline methods, we utilize the extensively adopted
metric in anomaly detection, namely AUC-ROC. The ROC
curve illustrates the graphical representation of the true positive rate (accurate identification of anomalous nodes) plotted
against the false positive rate (misidentification of normal
nodes as anomalies). Moreover, the AUC value, ranging from
0 to 1, quantifies the area under the ROC curve. A higher
AUC value signifies better anomaly detection performance
exhibited by the model under evaluation. Furthermore, the
AUPR score serves as an extra evaluative metric for anomaly
detection, particularly effective in contexts characterized by
imbalanced data distributions. AUPR quantifies model performance by computing the area under the precision-recall
curve across varying decision thresholds. Higher AUPR scores
indicate superior model capability in correctly identifying
positive samples.
3) Parameter Settings: For GADMCLG, the subgraph size
is fixed to 4 for both node–subgraph contrast and node–node
contrast. Both GNN models employ a single GCN layer and
adopt ReLU as the activation function. Besides, the embedding
dimension of both the target node and its contrastive subgraph
is set to 64. During the training phase, the batch size B, the
learning rate α, and the total training epoch T for all datasets
are set to 300, 0.001, and 400, respectively. During the inference
phase, we conduct 256 round detections to ensure accurate
detection results for each dataset. The balance parameter β
between node–subgraph and node–node contrast is set to (0, 1).
For subgraph–subgraph contrast, it adopts WL to embed all
the subgraphs, and the depth h of the extracted subgraph for
each dataset is set to 1. Moreover, the balance parameter γ
between local contrasts and the global contrast is set to (0, 1).

To reproduce the results of other baseline methods, we adhere
to the parameter settings specified in the respective publications. In cases where specific datasets do not have specified
parameters, we employ a grid search to select the best parameters for optimal performance. Specifically, for DOMINANT,
the balance parameters of attribute reconstruction error and
structure reconstruction error on BlogCatalog, Flickr, ACM,
Cora, Citeseer, and Pubmed datasets are set to 0.4, 0.7, 0.5,
0.4, 0.6, and 0.7, respectively. For CoLA, the subgraph size,
embedding dimension, and sampling round are configured to
4, 64, and 256 for each dataset. In SL-GAD, the weight of the
contrastive scores across all datasets is set to 1, with the weights
of the generative scores being 0.6, 0.6, 0.7, 0.4, 0.5, and 0.4,
respectively. For ComGA, the balance parameters of attribute
reconstruction error and structure reconstruction error are set
to 0.4, 0.4, 0.2, 0.2, 0.1, and 0.1, respectively. For GRADATE,
the balance parameters of importance between the original view
and the second view obtained through edge modification are
0.9, 0.5, 0.9, 0.9, 0.3, and 0.3, respectively. The balance parameters between subgraph- and node-level anomaly scores are
0.9, 0.3, 0.5, 0.3, 0.3, and 0.9. Last, the depth of subgraphs in
GCAD for each dataset is set to 1.
C. Result Analysis
In this section, we evaluate the performance of GADMCLG
in anomaly detection by comparing it with six state-of-theart baselines. Fig. 4 illustrates the comparison of ROC curves.
Moreover, the AUC and AUPR scores on the injected graph
datasets and real-world anomaly graph datasets are presented in
Tables III and IV, respectively. Based on the results, we make
the following observations.
1) On the first six injected anomaly graph datasets, our proposed method GADMCLG outperforms all the baseline
methods in terms of AUC. Specifically, GADMCLG obtains notable AUC gains of 1.67%, 0.77%, 4.24%, 3.80%,
2.46%, and 2.77% compared to the second-best performance on BlogCatalog, Flickr, ACM, Cora, Citeseer, and
Pubmed, respectively. Simultaneously, the AUPR results
demonstrate that GADMCLG significantly enhances positive sample detection relative to its baseline methods
on most datasets, particularly achieving an approximate
23.13% increase in AUPR on the Citeseer dataset. These
results suggest that GADMCLG exhibits superior overall performance and can effectively accommodate the
varying requirements of different scenarios. The primary
reason for the results is that our anomaly detection model
based on multiscale contrastive learning can effectively
capture both local and global anomaly information in the
network simultaneously.
2) GADMCLG is successfully expanded to the large-scale
network dataset ogbn-arxiv, overcoming a significant
limitation of many baseline methods that are unable
to perform anomaly detection due to extensive memory requirements. Although GADMCLG can also scale
to even larger datasets, it necessitates increased computational time. This advantage is attributable to the

WANG et al.: GRAPH ANOMALY DETECTION VIA MULTISCALE CONTRASTIVE SELF-SUPERVISED LEARNING

Fig. 4.

493

(a)

(b)

(c)

(d)

(e)

(f)

(g)

(h)

(i)

ROC curves comparison on nine benchmark datasets. (a) BlogCatalog. (b) Flickr. (c) ACM. (d) Cora. (e) Citeseer. (f) Pubmed.

TABLE III
AUC AND AUPR VALUES COMPARISON ON THE INJECTED ANOMALY GRAPH DATASETS
methods

BlogCatalog

Flickr

ACM

Cora

Citeseer

Pubmed

ogbn-arxiv

AUC

AUPR

AUC

AUPR

AUC

AUPR

AUC

AUPR

AUC

AUPR

AUC

AUPR

AUC

AUPR

DOMINANT(2019) 0.7667
CoLA(2021)
0.7780
SL-GAD(2021)
0.8047
ComGA(2022)
0.8008
GRADATE(2023) 0.7190
GCAD(2023)
0.7512
GADMCLG(ours) 0.8214

0.3071
0.3278
0.4387
0.3327
0.1666
0.3630
0.4036

0.7563
0.7522
0.7898
0.7768
0.7370
0.7409
0.7975

0.1534
0.2733
0.4463
0.3550
0.2795
0.4017
0.3999

0.7608
0.8151
0.8221
0.8210
0.8817
0.8448
0.9241

0.1036
0.3177
0.4179
0.1071
0.3286
0.1853
0.4647

0.8336
0.8911
0.9058
0.8643
0.9075
0.9174
0.9554

0.3354
0.4390
0.5707
0.2250
0.5481
0.5323
0.7417

0.8282
0.8877
0.9184
0.9054
0.8601
0.9475
0.9721

0.3500
0.4387
0.5510
0.1921
0.2116
0.5345
0.7823

0.8143
0.9495
0.9588
0.9159
0.9279
0.9160
0.9865

0.1023
0.4080
0.6009
0.1768
0.3931
0.1813
0.7631

OOM
0.8171
OOM
OOM
OOM
0.8223
0.9238

OOM
0.2318
OOM
OOM
OOM
0.1712
0.4421

Note: The best performance on each dataset is highlighted in bold, and the second-best performance is marked underlined.

spatial complexity of GADMCLG being entirely independent of the number of nodes. Furthermore, GADMCLG shows significant performance advantages, with
AUC and AUPR increased by 10.15% and 21.03%, respectively, compared to suboptimal performance.

3) As demonstrated in Table IV, GADMCLG achieves superior anomaly detection performance in terms of AUC
on two real-world anomaly graph datasets, Amazon and
Enron, with improvements of 3.1% and 9.88% over the
suboptimal performance, respectively. Nevertheless, the

494

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 12, NO. 2, APRIL 2025

TABLE IV
AUC AND AUPR VALUES COMPARISON ON THE REAL-WORLD
ANOMALY GRAPH DATASETS
methods
DOMINANT(2019)
CoLA(2021)
SL-GAD(2021)
ComGA(2022)
GRADATE(2023)
GCAD(2023)
GADMCLG(ours)

Amazon

Enron

AUC

AUPR

AUC

AUPR

0.6348
0.4705
0.5717
0.6401
0.6003
0.6510
0.6820

0.1168
0.0232
0.0251
0.0333
0.0256
0.0146
0.0452

0.6363
0.4721
0.5815
0.6021
0.5671
0.5855
0.7351

0.0008
0.0004
0.0005
0.0004
0.0005
0.0005
0.0011

Note: The best performance on each dataset is highlighted in bold, and
the second-best performance is marked underlined.

significant imbalance between real anomalies and normal
nodes in the Amazon and Enron datasets poses substantial challenges for all methods in accurately identifying anomalies. This can be observed from the relatively
low evaluation scores, especially in AUPR. GADMCLG
achieved the highest AUPR score on Enron, but it performed lower than DOMINANT on Amazon. Addressing
this limitation will be a key focus of our future research.
4) The GAE-based methods, DOMINANT and ComGA,
cannot achieve satisfying results through network reconstruction error. The reason is that they do not directly
consider anomaly detection as a specific task leading to
suboptimal performance. In contrast, GADMCLG adopts
a contrastive learning-based approach by assessing the
consistency among nodes or subgraphs, thereby enabling
the direct detection of graph anomalies and providing
more reasonable explanations for detected anomalies.
5) The contrastive learning methods, CoLA, GCAD, and
GADMCLG, exhibit improved performance compared
to GAE-based methods. This suggests that contrastive
learning methods more effectively identify anomalies by
capturing the information consistency differences in attributes and structures within the network. Furthermore,
compared to GADMCLG based on multiscale contrastive
learning, the other two methods only utilize single-scale
contrast, resulting in incomplete capture of anomalous
information and, therefore, lowering performance.
6) Compared to another multiscale contrastive learning
method GRADATE, GADMCLG achieved an average
7.11% performance improvement in terms of AUC metric. The reason is that GADMCLG adopts the h-order
subgraph sampling strategy, while GRADATE uses edge
modification to generate contrast pairs within subgraph–
subgraph contrast. This type of graph augmentation has
the potential to introduce additional noise interference,
consequently impeding the efficacy of anomaly detection.
D. Parameter Analysis
In this section, we explore the hyperparameter sensitivity of
two important balance parameters β and γ, and the performance
of the proposed model. In this experiment, we investigate their

impacts on AUC. Both of these two hyperparameters are tuned
within the range from 0 to 1 at intervals of 0.1. The experimental
results on the six benchmark datasets are shown in Fig. 5.
As depicted in Fig. 5, the hyperparameters β and γ are found
to be effective in enhancing the performance of the proposed
model across all datasets. With the increase in parameter values,
AUC has improved to varying degrees, especially on the Citeseer and Pubmed datasets. The above experimental observations
indicate that for BlogCatalog, Flickr, ACM, Cora, Citeseer, and
Pubmed datasets, setting β to 0.2, 0.3, 0.3, 0.4, 0.8, and 0.6,
respectively, alongside setting γ at 0.9, 0.2, 0.7, 0.8, 0.6, and
0.5, our proposed GADMCLG exhibits optimal performance
for anomaly detection.
E. Ablation Study
In this section, we verify the effectiveness of the proposed
multiscale contrastive strategy employed in GADMCLG and
examine the influence of various subgraph sampling strategies
on anomaly detection performance.
1) Multiscale Contrastive Strategy: To validate the effectiveness of our proposed GADMCLG based on multiscale contrastive learning, we perform an ablation study on the six
datasets and evaluate the performance in terms of AUC. In this
experiment, we define three variants: GADMCLG w/o ns,
GADMCLG w/o nn, and GADMCLG w/o ss. Specifically,
GADMCLGw/o ns represents the variant of GADMCLG without the node–subgraph contrast, GADMCLG w/o nn is its variant that excludes the node–node contrast, and GADMCLG w/o
ss indicates only the node–subgraph and subgraph–subgraph
contrasts are used for detecting anomalies. The performance
variance results are presented in Table V.
The experimental results indicate an insightful observation
that node–subgraph contrast manifests a more significant impact on the performance of anomaly detection in comparison
with node–node contrast. This is because, for node–node contrast, we construct the comparison between the target node and
the initial masked node of RWR. However, it notes that the
representation of the masked initial node is generated by aggregating its neighboring attribute information. Consequently,
node–node contrast essentially constitutes an alternative manifestation of node–subgraph contrast. Moreover, compared with
GADMCLG w/o ss, GADMCLG achieves significant performance improvement because subgraph–subgraph contrast captures important global anomaly information in the network
by calculating the anomaly score of their central nodes based
on the similarity between subgraphs. Therefore, the multiscale
contrastive strategy that combines local and global abnormal
information leads to the best performance.
2) Subgraph Centralization: The calculation of subgraph
similarity is a complex problem, and its accuracy is affected by
the relative positions between subgraphs. To verify the impact
of the subgraph centralization technique we used on the performance of graph anomaly detection, we remove this technique
from the global comparison and define the variant as GADMCLG w/o sc. The experimental results on six datasets are shown
in Fig. 6.

WANG et al.: GRAPH ANOMALY DETECTION VIA MULTISCALE CONTRASTIVE SELF-SUPERVISED LEARNING

Fig. 5.

495

(a)

(b)

(c)

(d)

(e)

(f)

Sensitivity analysis for the balance parameters β and γ w.r.t AUC. (a) BlogCatalog. (b) Flickr. (c) ACM. (d) Cora. (e) Citeseer. (f) Pubmed.
TABLE V
EFFECT OF DIFFERENT CONTRASTIVE STRATEGIES W.R.T AUC
Methods

BlogCatalog

Flickr

ACM

Cora

Citeseer

Pubmed

GADMCLG w/o ns
GADMCLG w/o nn
GADMCLG w/o ss
GADMCLG

0.7697
0.8118
0.7976
0.8214

0.7882
0.7802
0.7584
0.7975

0.8789
0.9077
0.8730
0.9241

0.9300
0.9461
0.9113
0.9554

0.9601
0.9631
0.9105
0.9721

0.9771
0.9796
0.9548
0.9865

Note: The best performance on each dataset is highlighted in bold.

Fig. 6.

Effect of subgraph centralization on the performance of GADMCLG.

Based on the above experimental results, we found that subgraph centralization greatly affects the final anomaly detection
performance of our model. Without this important component,

GADMCLG experienced a significant performance decline on
all six datasets. This indicates that subgraph centralization technology is very necessary for graph anomaly detection.
3) Subgraph Sampling Strategy: To investigate the impact of different subgraph sampling strategies on subgraph–
subgraph contrast in graph anomaly detection, we compare
the h-order sampling with two additional sampling strategies:
RWR and intracommunity RW [53]. Correspondingly, we combine these two sampling strategies with multiscale contrastive
learning and then define two variants GADMCLG-RWR and
GADMCLG-CW, respectively. The comparative results are
shown in Fig. 7.
It can be observed that the proposed GADMCLG performs best across all datasets compared to GADMCLG-RWR
and GADMCLG-CW. This result demonstrates that the horder neighbor subgraph sampling strategy is more suitable for
subgraph–subgraph contrast than the other two sampling strategies. Further analysis reveals that RWR introduces a significant

496

Fig. 7.

IEEE TRANSACTIONS ON COMPUTATIONAL SOCIAL SYSTEMS, VOL. 12, NO. 2, APRIL 2025

Effect of different subgraph sampling strategies w.r.t. AUC.

degree of randomness, making it unable to fully capture the
entire neighborhood observation related to the target node. Besides, intracommunity RW focuses on capturing the community
structure of the target node, ignoring anomalous attribute information. However, the h-order neighbor subgraph sampling
strategy simultaneously captures the subgraph structure and
neighbor node-attribute information. Consequently, subgraph–
subgraph contrast for graph anomaly detection depends on a
comprehensive observation of the target node’s neighborhood.
VI. CONCLUSION
In this article, we proposed a graph anomaly detection model
via multiscale contrastive self-supervised learning, navigating
from local to global contexts. To uncover underlying anomaly
nodes in attributed networks, we incorporate local-level contrast
and global-level contrast to enhance the model’s capability to
discern anomalous patterns across different scales, contributing
to a more comprehensive and effective detection of anomalies
within graph-structure data. Moreover, we introduce the subgraph centralization strategy to mitigate the influence of the
absolute position of subgraphs in the attribute space on global
subgraph contrast, thereby enhancing the detection accuracy of
the proposed model. The effectiveness of the proposed approach
has been validated on six real-world benchmark datasets, and
experimental results demonstrate its superiority over competitive counterparts.
Furthermore, since subgraph contrast relies on global observations of the target node’s neighborhood, the size of its
neighbor subgraphs exhibits diversity. This diversity makes it
challenging to employ subgraph embedding methods with the
same contrast as the local contrasts, rendering them unable to
participate in joint training. In the future, we will try to solve this
problem. Moreover, the interpretability of the results constitutes
a crucial concern in graph anomaly detection. We will extend
graph contrastive learning to enhance the interpretability of
graph anomaly detection models.
REFERENCES
[1] X. Ma et al., “A comprehensive survey on graph anomaly detection
with deep learning,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12,
pp. 12012–12038, Dec. 2023.

[2] A. D. Pazho, G. A. Noghre, A. A. Purkayastha, J. Vempati, O. Martin,
and H. Tabkhi, “A survey of graph-based deep learning for anomaly
detection in distributed systems,” IEEE Trans. Knowl. Data Eng., vol. 36,
no. 1, pp. 1–20, Jan. 2024.
[3] L. Zheng, G. Liu, C. Yan, and C. Jiang, “Transaction fraud detection
based on total order relation and behavior diversity,” IEEE Trans.
Comput. Soc. Syst., vol. 5, no. 3, pp. 796–806, Sep. 2018.
[4] A. Dey, B. R. Kumar, B. Das, and A. K. Ghoshal, “Outlier detection
in social networks leveraging community structure,” Inf. Sci., vol. 634,
pp. 578–586, 2023.
[5] J. Meira et al., “Anomaly detection on natural language processing to
improve predictions on tourist preferences,” Electronics, vol. 11, no. 5,
p. 779, 2022.
[6] B. Alwasel, A. Aldribi, M. Alreshodi, I. S. Alsukayti, and M. Alsuhaibani, “Leveraging graph-based representations to enhance machine
learning performance in IIoT network security and attack detection,”
Appl. Sci., vol. 13, no. 13, p. 7774, 2023.
[7] Q. Guo, H. Xie, Y. Li, W. Ma, and C. Zhang, “Social bots detection
via fusing BERT and graph convolutional networks,” Symmetry, vol. 14,
no. 1, p. 30, 2021.
[8] H. Kim, B. S. Lee, W.-Y. Shin, and S. Lim, “Graph anomaly detection
with graph neural networks: Current status and challenges,” IEEE
Access, vol. 10, pp. 111820–111829, 2022.
[9] M. M. Breunig, H. P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” in Proc. ACM SIGMOD Int. Conf. Manag.
Data, 2000, pp. 93–104.
[10] B. Perozzi and L. Akoglu, “Scalable anomaly ranking of attributed
neighborhoods,” in Proc. 16th SIAM Int. Conf. Data Mining (SDM),
2016, pp. 207–215.
[11] Z. Peng, M. Luo, J. Li, H. Liu, and Q. Zheng, “ANOMALOUS:
A joint modeling approach for anomaly detection on attributed networks,” in Proc. 27th Int. Joint Conf. Artif. Intell. (IJCAI), Jul. 2018,
pp. 3515–3519.
[12] G. Pang, C. Shen, L. Cao, and A. V. D. Hengel, “Deep learning for
anomaly detection: A review,” ACM Comput. Surv., vol. 54, no. 2, pp. 1–
38, 2021.
[13] S. Bandyopadhyay, L. N, S. V. Vivek, and M. N. Murty, “Outlier resistant unsupervised deep architectures for attributed network embedding,”
in Proc. 13th Int. Conf. Web Search Data Mining, Jan. 2020, pp. 25–33.
[14] P. Cui, X. Wang, J. Pei, and W. Zhu, “A survey on network embedding,”
IEEE Trans. Knowl. Data Eng., vol. 31, no. 5, pp. 833–852, May 2019.
[15] J. Zhu, J. Wang, Y. Shan, S. Yu, G. Chen, and Q. Xuan, “DeepInsight:
Topology changes assisting detection of adversarial samples on graphs,”
IEEE Trans. Comput. Soc. Syst., vol. 11, no. 1, pp. 76–88, Feb. 2024.
[16] Z. Wu, S. Pan, F. Chen, G. Long, C. Zhang, and P. S. Yu, “A
comprehensive survey on graph neural networks,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 32, no. 1, pp. 4–24, Jan. 2021.
[17] R. Hu, C. C. Aggarwal, S. Ma, and J. Huai, “An embedding approach
to anomaly detection,” in Proc. IEEE Int. Conf. Data Eng. (ICDE), May
2016, pp. 385–396.
[18] B. Perozzi, R. Al-Rfou, and S. Skiena, “DeepWalk: Online learning of
social representations,” in Proc. 20th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, Aug. 2014, pp. 701–710.
[19] A. Grover and J. Leskovec, “node2vec: Scalable feature learning for
networks,” in Proc. 22nd ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, Aug. 2016, pp. 855–864.
[20] K. Ding, J. Li, R. Bhanushali, and H. Liu, “Deep anomaly detection
on attributed networks,” in Proc. SIAM Int. Conf. Data Mining (SDM),
May 2019, pp. 594–602.
[21] Y. Li, X. Huang, J. Li, M. Du, and N. Zou, “SpecAE: Spectral
autoencoder for anomaly detection in attributed networks,” in Proc. 28th
Int Conf Inf Knowl. Manage., Nov. 2019, pp. 2233–2236.
[22] Z. Peng, M. Luo, J. Li, L. Xue, and Q. Zheng, “A deep multi-view
framework for anomaly detection on attributed networks,” IEEE Trans.
Knowl. Data Eng., vol. 34, no. 6, pp. 2539–2552, Jun. 2022.
[23] X. Luo et al., “ComGA: Community-aware attributed graph anomaly
detection,” in Proc. 15th ACM Int. Conf. Web Search Data Mining
(WSDM), Feb. 2022, pp. 657–665.
[24] Y. Liu, Z. Li, S. Pan, C. Gong, C. Zhou, and G. Karypis, “Anomaly detection on attributed networks via contrastive self-supervised learning,”
IEEE Trans. Neural Netw. Learn. Syst., vol.33, no. 6, pp. 2378–2392,
Jun. 2022.
[25] M. Jin, Y. Liu, Y. Zheng, L. Chi, Y. Li, and S. Pan, “ANEMONE: Graph
anomaly detection with multi-scale contrastive learning,” in Proc. 30th
Int. Conf. Inf. Knowl. Manage. (CIKM), Oct. 2021, pp. 3122–3126.
[26] Z. Zhang, K. Ting, G. Pang, and S. Song, “Subgraph centralization:
A necessary step for graph anomaly detection,” in Proc. SIAM Int. Conf.
Data Mining (SDM), 2023, pp. 703–711.

WANG et al.: GRAPH ANOMALY DETECTION VIA MULTISCALE CONTRASTIVE SELF-SUPERVISED LEARNING

[27] J. Duan et al., “Graph anomaly detection via multi-scale contrastive
learning networks with augmented view,” in Proc. AAAI Conf. Artif.
Intell., vol. 37, no. 6, Jun. 2023, pp. 7459–7467.
[28] K. Ding, J. Li, N. Agarwal, and H. Liu, “Inductive anomaly detection
on attributed networks,” in Proc. 29th Int. Joint Conf. Artif. Intell.,
Jan. 2021, pp. 1288–1294.
[29] Y. Xie, Z. Xu, J. Zhang, Z. Wang, and S. Ji, “Self-supervised learning
of graph neural networks: A unified review,” IEEE Trans. Pattern Anal.
Mach. Intell., vol. 45, no. 2, pp. 2412–2429, Feb. 2023.
[30] Y. Zheng, M. Jin, Y. Liu, L. Chi, K. T. Phan, and Y.-P. P. Chen,
“Generative and contrastive self-supervised learning for graph anomaly
detection,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12220–
12233, Dec. 2023.
[31] B. Chen et al., “GCCAD: Graph contrastive coding for anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 8, pp. 8037–8051,
Aug. 2023.
[32] Y. Liu et al., “Graph self-supervised learning: A survey,” IEEE Trans.
Knowl. Data Eng., vol. 35, no. 6, pp. 5879–5900, Jun. 2023.
[33] W. Hamilton, Z. Ying, and J. Leskovec, “Inductive representation
learning on large graphs,” in Proc. Adv. Neural Inf. Process. Syst.,
vol. 30, 2017, pp. 1025–1035.
[34] Y. Zhu, Y. Xu, F. Yu, Q. Liu, S. Wu, and L. Wang, “Deep graph
contrastive representation learning,” 2020, arXiv:2006.04131.
[35] Y. Zhu, Y. Xu, F. Yu, Q. Liu, S. Wu, and L. Wang, “Graph contrastive
learning with adaptive augmentation,” in Proc. WWW, Apr. 2021,
pp. 2069–2080.
[36] Y. You, T. Chen, Y. Shen, and Z. Wang, “Graph contrastive learning automated,” in Proc. Int. Conf. Mach. Learn. (ICML), Jul. 2021,
pp. 12121–12132.
[37] J. Zeng and P. Xie, “Contrastive self-supervised learning for graph
classification,” in Proc. AAAI Conf. Artif. Intell., vol. 35, no. 12, May
2021, pp. 10824–10832.
[38] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum contrast
for unsupervised visual representation learning,” in Proc. IEEE Comput.
Soc. Conf. Comput. Vis. Pattern Recognit., 2020, pp. 9729–9738.
[39] P. Veličković, W. Fedus, W. L. Hamilton, P. Liò, Y. Bengio, and R. D.
Hjelm, “ Deep graph infomax,” 2018, arXiv:1809.10341.
[40] Y. Ren, B. Liu, C. Huang, P. Dai, L. Bo, and J. Zhang, “Heterogeneous
deep graph infomax,” 2019, arXiv:1911.08538.
[41] Q. Zhu, C. Yang, Y. Xu, H. Wang, C. Zhang, and J. Han, “Transfer learning of graph neural networks with ego-graph information maximization,”
in Proc. Adv. Neural Inf. Process. Syst., vol. 34, 2021, pp. 1766–1779.
[42] J. Cao, X. Lin, S. Gao, L. Liu, T. Liu, and B. Wang, “Bipartite graph
embedding via mutual information maximization,” in Proc. WSDM,
Mar. 2021, pp. 635–643.
[43] Z. Liu, C. Wang, C. Han, and T. Guo, “Learning graph representation
by aggregating subgraphs via mutual information maximization,” Neurocomputing, vol. 518, 2023, Art. no. 126392.
[44] H. Tong, C. Faloutsos, and J.-y. Pan, “Fast random walk with restart
and its applications,” in Proc. 6th IEEE Int. Conf. Data Mining (ICDM),
Dec. 2006, pp. 613–622.
[45] M. Togninalli, E. Ghisu, F. Llinares-López, B. Rieck, and K. Borgwardt,
“Wasserstein Weisfeiler-Lehman graph kernels,” in Proc. Adv. Neural
Inf. Process. Syst., vol. 32, 2019, pp. 6439-6449.
[46] L. Tang and H. Liu, “Relational learning via latent social dimensions,”
in Proc. 15th ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining,
Jun. 2009, pp. 817–826.
[47] J. Tang, J. Zhang, L. Yao, J. Li, L. Zhang, and Z. Su. “ArnetMiner:
Extraction and mining of academic social networks,” in Proc. 14th
ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, Aug. 2008,
pp. 990–998.
[48] P. Sen, G. Namata, M. Bilgic, L. Getoor, B. Galligher, and T. EliassiRad, “Collective classification in network data,” AI Mag., vol. 29, no. 3,
p. 93, 2008.
[49] W. Hu et al. “Open graph benchmark: Datasets for machine learning on
graphs,” in Proc. Adv. Neural Inf. Process. Syst., vol. 33, pp. 22118–
22133, 2020.
[50] Y. Pei, T. Huang, W. van Ipenburg, and M. Pechenizkiy, “ResGCN:
Attention-based deep residual modeling for anomaly detection on attributed networks,” Mach. Learn., vol. 111, no. 2, pp. 519–541, 2022.
[51] E. Müller, P. I. Sánchez, Y. Mülle, and K. Böhm, “Ranking outlier
nodes in subspaces of attributed graphs,” in Proc. 29th ICDEW, 2013,
pp. 216–222.
[52] V. Metsism, I. Androutsopoulos, and G. Paliouras, “Spam filtering with
Naive Bayes—Which naive Bayes?” in Proc. CEAS, vol. 17, 2006,
pp. 28–69.

497

[53] P. Pham, L. T. Nguyen, B. Vo, and U. Yun, “Bot2Vec: A general
approach of intra-community oriented representation learning for bot
detection in different types of social networks,” Inf. Syst., vol. 103, 2022,
Art. no. 101771.
Xiaofeng Wang received the Ph.D. degree in information and communication engineering from
Shanghai Jiao Tong University (SJTU), Shanghai,
China, in 2017.
He is currently a Lecturer with the College of
Information Engineering, China Jiliang University,
Hangzhou, China. He served as a Postdoctoral
Fellow in computer science with SJTU, and as a
Visiting Scholar with Concordia University, Montreal, Canada. His research interests include network
science, graph neural networks, data mining, and
machine learning.
Shuaiming Lai received the B.S. degree in electronic science and technology from Suzhou City
University, Suzhou, China, in 2021. He is currently
working toward the M.S. degree in artificial intelligence with China Jiliang University, Hangzhou,
China.
His research interests include graph anomaly
detection, graph neural networks, social network
analysis, and machine learning.

Shuailei Zhu received the B.S. degree in communication engineering in 2021 from the College
of Modern Science and Technology, China Jiliang
University, Hangzhou, China, where he is currently
working toward the M.S. degree in communication
engineering.
His research interests include community detection, graph neural networks, and machine learning.

Yuntao Chen received the B.S. degree in communication engineering in 2021 from the College
of Modern Science and Technology, China Jiliang
University, Hangzhou, China, where he is currently
working toward the M.S. degree in communication
engineering.
His research interests include signal graph classification, graph neural networks, and machine
learning.

Laishui Lv received the Ph.D. degree in computer
science and technology from Nanjing University of
Science and Technology, Nanjing, China, in 2021.
He is currently a Lecturer with the College of
Information Engineering, China Jiliang University,
Hangzhou, China. His research interests include
artificial intelligence, complex networks, statistical
analysis, and nonlinear optimization.

Yuanyuan Qi received the Ph.D. degree in information and communication engineering from Beijing University of Posts and Telecommunications
(BUPT), Beijing, China, in 2021.
She is currently a Lecturer with the College of
Information Engineering, China Jiliang University,
Hangzhou, China. She served as a Postdoctoral
Fellow in computer science with Zhejiang Normal
University, Hangzhou, China, and a Visiting Scholar
with York University, Toronto, Canada. Her research
interests include information retrieval, graph neural
networks, data mining, and machine learning.
PAPER_TEXT
