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
# [235] Graph Anomaly Detection via Multi-View Discriminative Awareness Learning
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
编号：235
题名：Graph Anomaly Detection via Multi-View Discriminative Awareness Learning
年份：2024
DOI：10.1109/tnse.2024.3462462
来源：IEEE Transactions on Network Science and Engineering
PDF：paper/10.1109_TNSE.2024.3462462.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：图学习、知识图谱与威胁情报、入侵检测与网络异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\235.txt
- 原始字符数：58215
- 本次发送字符数：58215
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 6, NOVEMBER/DECEMBER 2024

6623

Graph Anomaly Detection via Multi-View
Discriminative Awareness Learning
Jie Lian, Xuzheng Wang, Xincan Lin , Zhihao Wu , Shiping Wang , Senior Member, IEEE,
and Wenzhong Guo

Abstract—With the deeper research on attributed networks,
graph anomaly detection is becoming an increasingly important
topic. It aims to identify patterns deviating from a majority of
nodes. Currently, graph anomaly detection algorithms based on
reconstruction-based learning and contrastive-based learning have
gained significant attention. To harness diverse supervised signals,
an intuitive approach is to find an elegant strategy to fuse these
two paradigms, forming the hybrid learning paradigm. Despite
the success of the hybrid learning paradigm, due to its subgraph
sampling based approach, it still grapples with issues related to
unreliable neighborhood information and the neglect of topological
details. To address these limitations, this paper proposes a new
hybrid learning paradigm via multi-view discriminative awareness learning for graph anomaly detection. Unlike the previous
hybrid learning paradigm, the graph reconstruction module fully
incorporates attribute and topology information, enhancing the
comprehensiveness of data reconstruction. Moreover, the multiview discrimination module employs a view-level contrast method
based on the complete graph, which helps to comprehensively
extract the information in the attributed network and mitigates the
neighborhood unreliability without increasing the complexity. The
experimental results, obtained from a rigorous evaluation on six
benchmark datasets, demonstrate the effectiveness of the proposed
method compared to existing baseline methods.
Index Terms—Attributed networks, graph anomaly detection,
graph neural networks, self-supervised learning.

I. INTRODUCTION
ITH the development of information technology, numerous fields have generated complex, interdependent,
and interrelated data represented in the form of graphs [1], [2],
[3]. These data are commonly known as attributed networks or
attributed graphs. In attributed networks, nodes and edges represent multivariate information about entities and their complex
relationships. With the extensive attention given to the study of

W

Received 23 April 2024; revised 5 August 2024; accepted 8 September
2024. Date of publication 17 September 2024; date of current version 15
November 2024. This work was supported in part by the National Natural
Science Foundation of China under Grant U21A20472 and Grant 62276065,
and in part by the National Key Research and Development Plan of China under
Grant 2021YFB3600503. Recommended for acceptance by Dr. Yuedong Xu.
(Corresponding author: Wenzhong Guo.)
The authors are with the College of Computer and Data Science, Fuzhou
University, Fuzhou 350108, China, and also with the Fujian Provincial Key Laboratory of Network Computing and Intelligent Information Processing, Fuzhou
University, Fuzhou 350108, China (e-mail: linj2680157@gmail.com; wang
xuzheng@126.com; xincanlinms@gmail.com; zhihaowu1999@gmail.com;
shipingwangphd@163.com; guowenzhong@fzu.edu.cn).
Digital Object Identifier 10.1109/TNSE.2024.3462462

Fig. 1. An example illustrates two typical anomalies in the attributed networks:
1) Topology anomaly: incorrectly linked unrelated nodes; 2) Attribute anomaly:
nodes with disturbed attributes. Nodes with the same color represent that they
have similar attributes.

attributed networks, notable progress has been made across various tasks within these networks, such as node classification, link
prediction, and graph classification. Among these tasks, graph
anomaly detection is a fundamental data mining task [4]. It has
practical significance in various fields [5], including social spam
detection [6], telecommunication fraud detection [7], network
malware attack [8], and financial fraud detection [9].
Graph anomaly detection aims to identify patterns that deviate from the majority of node specifications in the attributed
networks [10]. Based on previous studies, anomalies can be
categorized into two types: attribute anomaly and topology
anomaly. As shown in Fig. 1, attribute anomaly occurs when
node attributes are contaminated by factors like noise, while
topology anomaly arises due to incorrect links between nodes.
Despite the clear definition of graph anomalies, it is still a tough
challenge to solve graph anomaly detection problems due to the
complexity of graph data, the absence of labeled information,
and the diversity of anomaly patterns.
Considering these challenges, extensive studies have been
conducted in the domain of anomaly detection on attributed
networks. Numerous traditional methods [11], [12], [13], [14],
[15] have been widely explored. Nonetheless, limited to relying
on domain-specific knowledge, they can not effectively capture
deep nonlinear information. Fortunately, aided by deep learning,

2327-4697 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

6624

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 6, NOVEMBER/DECEMBER 2024

Fig. 2. The proposed framework consists of three parts: graph reconstruction module, multi-view discrimination module, and graph anomaly scoring module.
Graph reconstruction module aims to identify anomalies by performing attribute regression and adjacency matrix regression on the original view through a graph
encoding-decoding structure. Multi-view discrimination module aims to identify anomalies from potential patterns of anomalies by generating positive and negative
views that are discriminated against the original view at the view level. Finally, the final anomaly score is computed through the graph anomaly scoring module.

recent advancements in graph anomaly detection have led to
impressive results. Currently, graph anomaly detection models using reconstruction-based learning and contrastive-based
learning have garnered considerable interest. In specific, the
reconstruction-based learning paradigm [16], [17], [18] aims
to measure the abnormality by calculating the reconstruction
errors of the nodes using the graph autoencoder. Nevertheless,
due to the sparseness of the anomaly samples, this approach
is vulnerable to the class imbalance problem. In contrast, the
contrastive-based learning paradigm [19], [20] utilizes a fixedsize subgraph sampling strategy for each node to design a proxy
task that predicts the relationship between a node and a subgraph.
This method utilizes node-subgraph pairing to establish an equal
number of positive and negative instance pairs for node-level
contrastive learning, effectively alleviating the class imbalance
problem. However, fixed-size subgraph sampling may lead to the
loss of neighborhood information of nodes with higher degrees,
thus degrading the effectiveness of contrastive learning.
To leverage diverse supervised signals, prior studies [21],
[22] have enhanced the contrastive-based learning paradigm by
incorporating reconstruction learning, a method referred to as
the hybrid learning paradigm. Nevertheless, by revisiting this
paradigm, it is found that most methods still rely on fixed-size
subgraph sampling, which focuses only on local information
rather than global information. In particular, the incomplete
capture of subgraphs and the presence of abnormal nodes result in the unreliability of neighborhoods. This undermines
the completeness of reconstruction learning and fundamentally
fails to address the limitations inherent in the contrastive-based
learning paradigm. Additionally, the current hybrid learning
paradigm only considers attribute reconstruction while ignoring
topological information, making it difficult to identify topological anomalies.

To overcome the above weakness, in this paper, we propose
a new hybrid paradigm via Multi-view Discriminative Awareness learning for Graph Anomaly Detection (MDA-GAD). The
framework of the proposed method is shown in Fig. 2. Specifically, a graph anomaly detection model is designed, which
includes a graph reconstruction module and a multi-view discrimination module that work in parallel. Unlike existing hybrid
learning methods, which are limited to attribute reconstruction,
the graph reconstruction module simultaneously reconstructs
both attribute and topology, enhancing the ability to detect
various anomalies. The multi-view discrimination module employs a sampling-free view generation method that generates
positive and negative views directly from the original view for
view-level discrimination learning. Finally, a graph anomaly
scoring module is designed for the anomaly evaluation of each
node. The proposed method utilizes complete graph information to ensure a comprehensive representation on the attributed
networks, effectively reducing the neighborhood unreliability
without increasing complexity. Overall, the main contributions
are summarised as follows:
r Present a novel hybrid learning approach that effectively integrates contrastive-based and reconstruction-based learning paradigms for anomaly detection on attributed networks.
r Introduce a new method to generate views and shift the focus from node-level to view-level contrast, overcoming the
drawbacks of previous hybrid learning methods regarding
neighborhood unreliability and high complexity.
r The experimental results illustrate the effectiveness of the
proposed method, showing its superiority over existing
baselines and its high time efficiency.
The rest parts of this paper are organized as follows. In
Section II, most relative approaches to the proposed method

LIAN et al.: GRAPH ANOMALY DETECTION VIA MULTI-VIEW DISCRIMINATIVE AWARENESS LEARNING

are introduced. Then, problem definitions and notations are
introduced in Section III. Section IV discusses the proposed
framework in detail, and comprehensive experiments are conducted in Section V. Finally, Section VI presents the conclusions
of this work.
II. RELATED WORK
In this section, we provide a brief overview of related
works, encompassing graph anomaly detection and graph selfsupervised learning.
A. Graph Anomaly Detection
As the rise of attributed networks, graph anomaly detection
algorithm has garnered attention from many researchers. Numerous machine learning algorithms have been widely explored
in the field of anomaly detection. Perozzi et al. [12] uses the egonetwork information of nodes to detect anomalous neighbors. Li
et al. [14] analyzes the attribute information residuals and their
consistent representation. Further, Peng et al. [15] combines
residual analysis and CUR decomposition for anomaly detection. All of the mentioned methods demonstrate excellent performance in low-dimensional attributed networks. Nonetheless,
due to their shallow learning mechanism, these algorithms may
struggle to effectively detect anomalies with high dimensions.
In recent years, deep learning-based anomaly detection algorithms have been increasingly explored with impressive achievements. Ding et al. [16] employs a graph convolutional network
(GCN) [23] based autoencoder to quantify the anomaly degree
of a node by calculating the reconstruction loss of both the
adjacency matrix and the attribute matrix. Fan et al. [24] integrates graph attention networks (GAT) [25] into the autoencoder
framework. Pei et al. [17] improves GAT by adding residual
information. Luo et al. [18] offers a community-aware tailored
GCN to mitigate the over-smoothing of anomalous node representations. Roy et al. [26] develops a method by reconstructing
the self-feature, degree, and neighborhood node distribution
representations. Nevertheless, the reconstruction-based learning
paradigm is susceptible to class imbalance. To overcome this
limitation, Liu et al. [19] first employs a contrastive-based
learning approach that utilizes metric instance pairs to achieve
node-subgraph contrast. Jin et al. [20] and Duan et al. [27]
enhance the contrastive-based learning paradigm by incorporating node-node contrast and subgraph-subgraph contrast into
node-subgraph contrast gradually, enabling anomaly detection
through multi-scale contrastive learning. Duan et al. [28] introduces normality learning in the contrastive-based learning
paradigm to mitigate the damage of abnormal nodes. Pan
et al. [29] designs a ego-neighbor comparison learning method
to efficiently detect graph anomalies. It is noteworthy that the
aforementioned methods are confined to the contrastive-based
learning paradigm and might not fully exploit the model’s
learning capacity with respect to supervised signals. Zheng
et al. [21] proposes a hybrid learning paradigm from the joint
perspective of the contrastive-based learning paradigm and the
reconstruction-based learning paradigm. Zhang et al. [22] improves the hybrid learning approach by utilizing a multi-view

6625

mechanism that includes both original and diffuse perspectives.
Nonetheless, these methods still rely on fixed-size subgraph
sampling and focus solely on attribute reconstruction, neglecting
the combined reconstruction of both attribute and topology. To
address this issue, the proposed method introduces a samplingfree contrastive strategy and considers the integrity of the reconstruction.
B. Graph Self-Supervised Learning
The emergence of self-supervised learning brings a new
paradigm for graph learning. It focuses on extracting graph
representations by designing suitable tasks that no longer require
manually labeled data. Generation-based models and contrastbased models are the two dominant graph self-supervised
types [30].
Generation-based models use a graph autoencoder to obtain a
representation by reconstructing graph information. The earliest
models, including GAE and VGAE [31], concentrate on reconstructing the adjacency matrix to acquire graph embeddings.
Building upon the effective masking strategy in computer vision [32], Tan et al. [33] improves GAE by incorporating edge
masking. Furthermore, Li et al. [34] introduces a novel path
masking strategy that enhances the graph mask autoencoder.
Hou et al. [35] adapts the graph mask autoencoder by utilizing a
double-masking strategy and scaled cosine error. Wang et al. [36]
introduces an easy-to-hard adversarial masking strategy to enhance alignment performance by generating challenging samples.
Contrast-based models are designed with suitable pretext
tasks that maximize the mutual information of positive samples.
Velivckovic et al. [37] pioneers graph self-supervised contrastive
learning by maximizing mutual information at both node and
graph levels to capture the global structure. On this basis, Hassani et al. [38] proposes contrastive learning through original and
diffuse graphs. Lin et al. [39] proposes a spectral augmentation
scheme to generate topological augmentation through perturbation mapping to improve the performance. Shen et al. [40]
utilizes a multi-head attention mechanism to learn graph augmented views with adaptive topology for conrtastive learning.
These works have shown desirable performance in downstream tasks, such as node classification and link prediction.
Nevertheless, there have been very limited attempts for anomaly
detection tasks. Motivated by the above methods, an anomaly
detection framework is designed from both generative and contrastive perspectives.
III. PROBLEM DEFINITION
In this section, we define the problems associated with node
anomaly detection on attributed networks. For better understanding, Table I presents the notations along with their descriptions.
Accordingly, the definition of attributed networks is given as
below.
For a given attributed network G = (V, E, X), where V and
E represent the set of nodes and edges, which can be formalized
by the adjacency matrix A ∈ RN ×N , X ∈ RN ×F denotes the

6626

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 6, NOVEMBER/DECEMBER 2024

TABLE I
NOTATIONS AND DESCRIPTIONS

existing anomaly detection methods, deep autoencoders are considered to have strong potential. The degree of node abnormality
can be quantified by the reconstruction loss. To reconstruct
the graph information efficiently, a graph autoencoder structure
is employed. Empowered by the autoencoder, the proposed
framework effectively captures and reproduces the complex
relationships within the graph, facilitating the identification of
anomalies through disparities in both topology and attribute
information.
View Encoder: A generalized approach is adopted to encode the original view by GCN. Utilizing the inherent efficient
modeling and information aggregation capabilities of GCN, the
encoder adeptly acquires a comprehensive representation of the
network. The representation of each graph convolutional layer
is formulated as follows:


1
1
(1)
H(+1) = σ D̃− 2 ÃD̃− 2 H() W() ,
where H() and H(+1) are the inputs and outputs of the -th
1
1
convolutional layer respectively, D̃− 2 ÃD̃− 2 denotes a symmetric normalization of the adjacency matrix, Ã represents the
adjacency matrix with self-loop, and W() represents the shared
weight matrix of all nodes in the network. σ(·) represents a
non-linear activation function. Then, the view encoder is defined
as:

attribute matrix of all nodes. Thus, the attributed network is also
expressed as G = (A, X).
The focus of this paper is the unsupervised node-level
anomaly detection problem on attributed networks, which is
formalized as follows:
For a given attributed network G = (V, E, X), the objective of
this task is to compute a score and rank the abnormality degree
of each node vi by defining a valid anomaly function, which can
be formalized as g(·) : RN ×F → RN ×1 . Typically, nodes with
high scores are considered as abnormal nodes.
IV. THE PROPOSED METHOD
In this section, we outline the overall framework of the
algorithm for detecting node-level graph anomalies in a selfsupervised manner. The proposed method has three distinct
components, including graph reconstruction module, multi-view
discrimination module, and graph anomaly scoring module.
First, the graph reconstruction module is designed to identify
node anomalies by measuring the degree of mismatch between
the reconstructed and the original views using the regression
loss generated by the reconstruction. Second, the multi-view
discrimination module is designed to generate high-quality positive and negative views to detect anomalies through a view-level
contrastive learning task. Finally, the anomaly score for all
nodes is computed by aggregating the scores from the first two
modules. Multiple rounds of anomaly scores are averaged to
mitigate the randomness associated with view generation.
A. Graph Reconstruction Module
Abnormal nodes exhibit patterns that differ from the typical
behaviors observed in the majority of normal nodes. Among

Zraw = GCNenc (Xraw , A; Wenc ) ,

(2)

where Zraw , Xraw , A, Wenc denote the node embedding
matrix, feature matrix, the adjacency matrix, and the weight
matrix of the encoder, respectively.
Topology Reconstruction Decoder: The topology reconstruction decoder aims to restore node structure information and
can effectively detect structural anomalies in the graph. The
GCN acts as a topology decoder, reconstructing node topology
information from latent node representations. The topology
reconstruction decoder can be represented as:
H = GCNT dec (Zraw , A; WT dec ) ,

(3)

 = HHT ,
A

(4)

where H, WT dec denote the potential node embedding matrix
after the decoder and the weight matrix of the topology decoder.
 denotes the reconstructed adjacency matrix obtained from the
A
inner product of H.
Attribute Reconstruction Decoder: The attribute reconstruction decoder is designed to regress node attributes and serves as
a powerful tool for detecting contextual anomalies on graphs.
Similarly, the GCN is employed as an attribute decoder. If
the node attributes can be effectively approximated using the
decoder, which suggests that the node is less likely to be abnormal. Conversely, if the attribute pattern cannot be accurately
reconstructed, it is indicated that the node attributes diverges
from the pattern observed in most normal nodes. The attribute
reconstruction decoder can be represented by:
 raw = GCNAdec (Zraw , A; WAdec ) ,
X

(5)

 raw , WAdec denote the reconstructed attribute matrix
where X
and weight matrix of the attribute decoder.

LIAN et al.: GRAPH ANOMALY DETECTION VIA MULTI-VIEW DISCRIMINATIVE AWARENESS LEARNING

6627

Topology and attribute regression are two crucial tasks performed by the graph reconstruction module. The reconstruction
errors from both types of information are combined, and the
objective function can be formulated as follows:

relationships and patterns between features, the bilinear layer
enables effective discrimination between original and generated
views. The similarity between the original view and the positive
(negative) view is computed as follows:

 2 + αXraw − X
 raw 2 .
Lrec = (1 − α)A − A
F
F

(6)

spos = Bilinear (Zraw , Zpos ; Wdis ) ,

(9)

where α is a parameter employed to balance the reconstruction
of topology and attributes.

sneg = Bilinear (Zraw , Zneg ; Wdis ) ,

(10)

B. Multi-View Discrimination Module
Contrastive learning has proven to be a successful approach
in detecting anomalies on graphs, effectively mitigating the
challenges posed by the extreme imbalance between normal and
abnormal nodes [19]. In this module, a view-level contrastivebased learning paradigm is designed. By employing this approach, the model efficiently learns the inherent patterns within
the graph, thereby augmenting its capability to identify abnormal
nodes.
View Generator: Existing node-level contrast approaches relying on subgraph sampling inadequately consider the global
structure, resulting in the omission of high-order information.
To overcome this limitation, a method for generating positive
and negative views is introduced. To enhance the view discrimination ability, inspired by the effectiveness of data augmentation
methods in graph self-supervised learning, feature masking is
utilized to augment the original features for the positive view.
Specifically, the positive view involves randomly masking node
attributes by setting the attributes of the masked nodes to zero.
This feature masking helps the model to implicitly perform
attribute regression, thereby boosting its discriminative capabilities. For the negative view, randomized row transformations
are employed on the node features from the original view. It
aims to simulate the representation of nodes post-injection with
anomalies simply. By completely altering the graph structure,
this approach effectively models anomalies in node attributes
and topology. To maintain consistency, the feature masking
applied to negative views is the same as that used to positive
views.
View Generation Encoder: This sub-module aims to extract
feature embeddings from the positive and negative views to
facilitate the discriminative task within the original features.
To maintain consistency, the view generation encoder shares
weights with the original view encoder. The view generation
encoder can be defined as follows:
Zpos = GCNenc (Xpos , A; Wenc ) ,

(7)

Zneg = GCNenc (Xneg , A; Wenc ) ,

(8)

where Xpos , Zpos denote the attribute matrix and node embedding matrix corresponding to the positive views, and Xneg and
Zneg represent the attribute matrix and node embedding matrix
for the negative views, respectively.
View Discriminator: The discriminator takes both original
and generated view features as inputs. It employs a shared
bilinear layer to compute the similarity between these views,
which generates a score for discriminating between the positive
and negative instances. Facilitating the extraction of intricate

where spos represents the similarity between the original view
and the positive view, sneg represents the similarity between the
original view and the negative view, and Wdis represents the
weight matrix of the discriminator. If a node is deemed normal,
the discriminator easily distinguishes between the positives
and negatives of the generated view. Conversely, if a node is
classified as abnormal, the discriminator struggles to accurately
determine the positives and negatives of the generated view.
To promote the discrimination of the learned representation,
the binary cross-entropy loss is employed as the objective function:
1 
(yi log si + (1 − yi ) log (1 − si )) ,
2N i=1
N

Ldis = −

(11)

where yi represents labels 1 and 0 for positive and negative views
respectively, and si represents the similarity score between the
original view and the generated view of each node vi . Finally,
the loss function of the two modules can be expressed as follows:
L = (1 − β)Ldis + βLrec .

(12)

where β is a parameter used to balance the reconstruction module
and the discrimination module.
C. Graph Anomaly Scoring Module
After introducing the graph reconstruction module and the
multi-view discrimination module, the calculation of anomaly
scores for each module is defined.
Graph Reconstruction Score: The graph reconstruction score
consists of attribute and topology reconstruction errors. The
score srec,i for each node vi is calculated as follows:
i 22 ,
stop,i = ai − a

(13)

i 22 ,
satt,i = xi − x

(14)

srec,i = (1 − α)stop,i + αsatt,i ,

(15)

where ai denotes the i-th row vector of A, and xi denotes the i-th
row vector of Xraw , satt,i denotes the attribute reconstruction
score of vi and stop,i denotes the topology reconstruction score
of vi . The parameter α is the same as (6) to balance reconstruction module. The higher the reconstruction score is, the more
abnormal the node is.
Graph Discrimination Score: Given the nature of similarity
scores, normal nodes are expected to have a score close to 1 for
positive views and close to 0 for negative views in an ideal case.
For each node vi , the anomaly degree is defined as the difference
between positive and negative scores:
sdis,i = sneg,i − spos,i ,

(16)

6628

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 6, NOVEMBER/DECEMBER 2024

where spos,i represents the positive view score of vi and sneg,i
represents the negative view score of vi .
Graph Anomaly Score: The scores of the reconstruction module and the discrimination module are weighted to produce the
composite score ai , and the formula is as follows:
ai = (1 − β)sdis,i + βsrec,i ,

(17)

where β balances the scores of the two modules, consistent
with (12). However, the single-round score calculation does
not adequately capture the diverse patterns of anomalies and
randomness generated by the negative view. To tackle these challenges, multiple rounds of score averaging are incorporated to
obtain the final result. Specifically, the anomaly score calculation
for vi is expressed as:
1  (r)
a .
R r=1 i
R

score (vi ) =

(18)

where score(vi ) represents the anomaly score of vi , and R is the
number of test rounds. Ideally, increasing the number of rounds
for computing the score leads to better stability.
The algorithmic process of the proposed method is presented
in Algorithm 1. This algorithm is comprised of two phases:
training and testing. During the training phase, the model is
trained on two self-supervised tasks: reconstructing the original
view and generating positive and negative view contrasts. During
the testing phase, iterative rounds of inference computation are
employed to derive the final anomaly scores for all nodes.

Algorithm 1: The Algorithmic Process of MDA-GAD.
Input: An attributed network G = (V, E, X); Number of
training epoch T , Number of test epoch R.
Output: Anomaly score function score(·).
1: Initialize trainable parameters Wenc , WT dec , WAdec ,
and Wdis .
2: // Training Stage
3: for t = 1 → T do
4:
Generate the positive view Xpos by randomly
masking the original feature Xraw .
5:
Generate the negative view Xneg by randomly
masking and row transforming the original feature
Xraw .
6:
Calculate the reconstruction score for all nodes by
(13), (14), and (15).
7:
Calculate the discrimination score for all nodes by
(16).
8:
Calculate the overall loss L by (12).
9:
Back propagate and update the trainable parameters
Wenc , WT dec , WAdec , and Wdis .
10: end for
11: // Testing Stage
12: for r = 1 → R do
13:
Calculate the composite anomaly score for all nodes
by (17).
14: end for
15: Calculate the average of the composite scores for
multiple rounds by (18).

D. Complexity Analysis
The time complexity of the proposed method comes mainly
from its graph reconstruction and multi-view discrimination modules. The graph reconstruction module utilizes a
GCN-based encoder and decoder with complexity O(LM D +
LN D2 )), and the complexity of the matrix reconstruction is
O(N 2 D), and the total complexity is O(LM D + LN D2 +
N 2 D). The multi-view discrimination module includes a
GCN-based encoder and a discriminator with complexities of
O(LM D + LN D2 ) and O(N D2 ) respectively, summing to
O(LM D + LN D2 + N D2 ). Therefore, the total time complexity is O((LM D + LN D2 + N 2 D)(T + R)), where L is
the number of GCN layers, M is the number of edges, N is the
number of nodes, D is the hidden dimension, and T and R are
the number of training and inference epochs.
Table II presents a comparison of time complexities between
the proposed method and the baseline methods. It is evident that
methods employing subgraph sampling exhibit higher complexities, where the complexity of sampling subgraphs is as high as
O(N P δ). In contrast, the proposed method demonstrates lower
complexity while enhancing performance.
V. EXPERIMENTAL ANALYSIS
In this section, we describe the datasets used for the experiments and the parameter settings. Then the experimental results are presented, including performance comparison, ablation
study, and parameter sensitivity.

TABLE II
COMPARISON OF TIME COMPLEXITY (P AND Q REPRESENT THE NUMBER OF
NODES AND EDGES OF THE SUBGRAPH, AND δ IS THE MEAN DEGREE OF
NETWORK)

A. Dataset Description
Experiments are conducted on six benchmark datasets, consisting of three citation networks, one web citation network and
two social networks, as described below.
r Citation Network: Cora, Citeseer,1 and ACM2 datasets represent citation networks of scientific publications, where
nodes represent papers and edges represent citation relationships between papers.

1 https://github.com/kimiyoung/planetoid
2 https://github.com/kaize0409/GCN_AnomalyDetection

LIAN et al.: GRAPH ANOMALY DETECTION VIA MULTI-VIEW DISCRIMINATIVE AWARENESS LEARNING

TABLE III
THE STATISTICS OF THE DATASETS

r Web Citation Network: UAI3 dataset pertains to a web
citation network, where nodes represent pages and edges
represent hyperlinks.
r Social Network: BlogCatalog and Flickr4 datasets are
social networks, where nodes represent users and edges
represent their relationships.
In the mentioned attributed network datasets, inherent
anomaly nodes are not present. To facilitate experimentation
with the anomaly detection framework, the common practice of
introducing anomaly nodes is followed.
Topology Anomaly Injection: The injection of topological
anomalies aims to disrupt the relationships between nodes on
graphs [41], [42]. This is achieved by randomly selecting t nodes
and establishing fully connected links between them. Based on
the experience of previous work [19], [20], [21], this process is
repeated a total of n times. t is fixed at 15, and n is set to [5, 5,
5, 10, 15, 20] for Cora, Citeseer, UAI, BlogCatalog, Flickr, and
ACM, respectively.
Contextual Anomaly Injection: The injection of context exceptions is to disorder the properties of nodes [43]. We randomly
select a node vi , a subset S, find the node vf ar in the subset S
that has the largest distance to the attribute valued by the node
vi , and assign the attribute of vf ar to vi . To be consistent with
the ratio of topology anomaly injection, contextual anomalies
are injected for t × n nodes.
Finally, an equal proportion of topological and contextual
anomalies are introduced into all datasets. By the above injection
method, we obtain the perturbed datasets, as shown in Table III.
B. Experimental Settings
In this subsection, we describe the experimental setup, including baseline methods, evaluation metrics, parameter settings,
and computing infrastructures.
Baselines: As presented in Table IV, the proposed method
considers the strategies more comprehensively than other baseline methods. A brief description of the baseline methods is
given as follows:
r DOMINANT [16] is an unsupervised anomaly detection
framework leveraging deep learning, employing a GCNbased encoder to jointly reconstruct the adjacency and
attribute matrix.
r CoLA [19] captures anomalous patterns through contrastive self-supervised learning, evaluating consistency
3 https://github.com/zhumeiqiBUPT/AM-GCN
4 http://socialcomputing.asu.edu/pages/datasets

6629

between nodes and neighboring subgraphs using a GNNbased encoder.
r ANEMONE [20] introduces a multi-scale contrastive learning objective for anomaly detection, where the encoder
learns consistency between instances at patch and context
levels simultaneously.
r SL-GAD [21] is a framework designed to construct various
contextual subgraphs centered around target nodes and
facilitate anomaly detection through generative attribute
regression and multi-view contrast.
r Sub-CR [22] is a contrastive learning-based anomaly detection framework that uses graph diffusion to augment the
original graph for both inner and outer views.
r GRADATE [27] enhances anomaly detection by incorporating subgraph-subgraph and node-node contrasts alongside node-subgraph contrasts within a multi-scale contrast
learning framework.
r NLGAD [28] is a multi-scale contrastive learning network
that incorporates high-confidence nodes into the normality
pool, achieving superior results through training based on
these nodes.
Evaluation Metric: The anomaly detection performance of all
the methods is evaluated using the widely adopted ROC-AUC
metric. The ROC curve illustrates the relationship between the
true-positive rate and the false-positive rate, and the area under
the ROC curve is denoted as AUC. To eliminate the impact
of randomness, all experiments are repeated 10 times, and the
mean and standard deviation of the results are recorded for
comparison.
Parameter Settings: In all experiments, the mask rate p is uniformly set to 0.2. In the basic framework, the encoder employs
a two-layer GCN, the attribute decoder employs a two-layer
GCN, and the topology decoder employs a one-layer GCN. The
hidden dimension is set to 64, and the number of test rounds
is fixed to 50. For the learning rate, we use a value of 0.001
for Cora, Citeseer, BlogCatalog, and ACM datasets, 0.0005
for Flickr dataset, and 0.002 for UAI dataset. The number of
training epochs is set to 250 for Cora, Citeseer, UAI, Flickr, and
ACM datasets, and 300 for BlogCatalog dataset. The α and β
parameters perform a grid search between 0.1 and 0.9.
Computing Infrastructures: The experiments for all models
are conducted on the PyTorch 1.8.1 platform. The hardware
configuration includes an Intel(R) Xeon(R) Silver 4210R CPU
operating at a frequency of 2.40 GHz, 56 GB of RAM, and an
NVIDIA GeForce RTX 3090 GPU with 24 GB of memory.
C. Experimental Results
In this subsection, we present a performance comparison
between the proposed method and seven baseline methods. The
ROC curves of all methods on six benchmark datasets are shown
in Fig. 3. According to the results, the following conclusions can
be drawn:
r Compared to all the baseline methods, the proposed method
offers optimal performance across most datasets. As shown
in Table V, the proposed method outperforms the current
best baseline by 2.81%, 4.06%, 1.49%, 2.12%, 1.23% in

6630

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 6, NOVEMBER/DECEMBER 2024

TABLE IV
ARCHITECTURE COMPARISON BETWEEN THE PROPOSED METHOD AND BASELINES

Fig. 3. ROC curves on six benchmark datasets. A larger area under the AUC curve indicates better anomaly detection performance. The black dotted lines refers
to the “random line”, indicating the performance under random guessing.

TABLE V
COMPARATIVE RESULTS OF GRAPH ANOMALY DETECTION WITH AUC (RUNNING MEANS AND STANDARD DEVIATIONS OF TEN TRIALS)

LIAN et al.: GRAPH ANOMALY DETECTION VIA MULTI-VIEW DISCRIMINATIVE AWARENESS LEARNING

Fig. 4.

Visualization of the anomaly score distribution for eight methods on the Citeseer dataset. The scores are normalized to a range of 0 to 1.

Fig. 5.

Runtime and maximum memory usage comparison between the proposed method and baselines on six benchmark datasets.

Cora, Citeseer, UAI, Flickr, and ACM respectively. Fig. 4
shows the distribution of anomaly scores for different
comparison methods on Citeseer. It is noticed that the
anomaly score distribution for the proposed method is more
centralized, and the distinction in the score distribution
between normal and abnormal nodes is more prominent.
r The experiments comparing the runtime and maximum
memory usage of all methods are shown in Fig. 5. The
proposed method excels in time efficiency, second only
to DOMINANT. Compared to the suboptimal model, the
proposed method has a runtime 53 times faster than SLGAD and 49 times faster than NLGAD. Besides, the
proposed method has a higher memory usage compared
to baseline methods, mainly because it utilizes the full
graph input, whereas most methods employ batch training.

6631

Although batch training reduces memory consumption, it
significantly increases the time overhead due to its inherent
complexity.
r Compared to models that solely rely on contrastive selfsupervised learning methods like CoLA, ANEMONE,
GRADATE, and NLGAD, and models that exclusively
utilize reconstruction methods like DOMINANT, the proposed method demonstrates superior anomaly detection
and generalization capabilities. A pivotal factor contributing to this advantage lies in the integration of two selfsupervised methods, which harnesses a more diverse set of
supervised signals.
r Compared to hybrid learning paradigms like SL-GAD
and Sub-CR, the proposed method also exhibits strong
performance. Research has demonstrated that hybrid

6632

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 6, NOVEMBER/DECEMBER 2024

TABLE VI
RESULTS OF ABLATION EXPERIMENTS (RUNNING MEANS AND STANDARD DEVIATIONS OF TEN TRIALS)

learning approaches can produce both suboptimal and
optimal outcomes, underscoring the effectiveness of this
strategy. Nonetheless, SL-GAD and Sub-CR rely on subgraph sampling, limiting their ability to estimate attributes
solely based on sampled neighbors. This constraint may
lead to information loss and an inability to fully exploit
the potential of the reconstruction module. In contrast,
the proposed method, utilizing complete graph training,
avoids these drawbacks and maintains the effectiveness of
the reconstruction module.
r The proposed method has exhibited exceptional performance in citation networks. However, there is still potential
for further improvements to augment its effectiveness in
the context of social networks. This is because social
networks typically have a significantly higher average node
degree compared to citation networks, resulting in more
node relationships that pose a greater challenge for graph
anomaly detection.
D. Ablation Study
In this subsection, we perform an ablation study to assess
the effectiveness of the graph reconstruction module and the
multi-view discrimination module. Specifically, four scenarios
are evaluated: w/o Res, w/o Dis, w/o Pos, and w/o Neg. In the
w/o Res scenario, the graph reconstruction module is excluded,
leading the model to rely solely on the multi-view discrimination
module during training. In the w/o Dis scenario, the multi-view
discrimination module is entirely removed, resulting in no discriminant scores being utilized in the training process. In the w/o
Pos scenario, only the scores of the generated negative views are
used as discriminant scores, while in the w/o Neg scenario, only
the scores of the generated positive views are employed. The
conclusions drawn from the results in Table VI are as follows:
r After removing the graph reconstruction module, the performance of using only the multi-view discrimination module significantly declines. This is likely because, without
joint learning, the original views containing anomalies
cannot be effectively distinguished at the view level by
contrastive learning alone. In other words, the absence
of the graph reconstruction module prevents the model
from capturing and reconstructing node topology and node
attributes of the graph, which consequently affects the discriminative ability of the multi-view discrimination module.
r Although the graph reconstruction module has shown performance improvements on specific datasets like Cora and

Citeseer, its adaptability to a broader range of scenarios remains limited. The success of the proposed method across
most datasets underlines the effectiveness and importance
of integrating the multi-view discrimination module. This
component enhances the its capacity to capture and leverage information from diverse perspectives, leading to an
overall performance enhancement. Therefore, the joint
learning of both modules is crucial for achieving robust
anomaly detection.
r Across all datasets, the multi-view discrimination module
that utilizes only positive view scores consistently has
higher AUC values compared to modules that rely solely
on negative view scores. Nevertheless, the failure of the
positive view-only scoring approach to take advantage
of the variable anomaly patterns present in the negative
views leads to sub-optimal results. Similarly, due to the
uncertainty associated with these patterns, relying solely
on the negative view score may lead to model instability.
Therefore, a more effective approach is to combine the
two views, leveraging their respective strengths to achieve
better performance.
E. Parameters Sensitivity
In this subsection, we conduct experiments to assess the
impacts of various hyperparameters. These hyperparameters
include the balancing parameters α and β, the mask rate p, the
hidden dimension D, and the number of test rounds R.
Influence of the balancing parameters: Fig. 6 shows a demonstration of the effect of the balancing parameter under different
datasets. The balancing parameter α is responsible for controlling the weighting between attribute reconstruction and topology
reconstruction. After analyzing the obtained parameters, it is evident that attribute reconstruction is typically assigned to a higher
weight proportion in the proposed method. Similarly, the balance
parameter β governs the weights of the reconstruction module
and the view discrimination module. For Cora and Citeseer
datasets, both the reconstruction module and the discrimination
module play equally important roles. On the contrary, for UAI
and Flickr datasets, the discrimination module proves to be more
advantageous, while for BlogCatalog and ACM datasets, the
reconstruction module demonstrates greater utility.
Influence of the mask rate: To further investigate the impact of
mask rate size on the generated views across different datasets,
a detailed analysis is conducted. Fig. 7(a) shows the AUC
values corresponding to different mask rates. It indicates a slight
increase in the AUC value as the mask rate reaches 0.2. However,

LIAN et al.: GRAPH ANOMALY DETECTION VIA MULTI-VIEW DISCRIMINATIVE AWARENESS LEARNING

Fig. 6.

6633

The experimental results for the investigation of α and β parameters. These subfigures show the effect of the α and β parameters on the AUC value.

Fig. 7. The experimental results of the parametric study are presented. These subfigures show the effectiveness of the masking rate, embedding dimension, and
number of test rounds on the AUC values, respectively.

it starts to decrease after exceeding this threshold. The decline
observed in this case can be attributed to an excessively high
mask rate. High rate disrupts the inherent pattern of the original
view, which hampers the effective differentiation between positive and negative views. Based on the analysis, a mask rate of
0.2 is a suitable choice for generating views.
Influence of the hidden dimension: In this experiment, we
investigate the effect of hidden dimensions on the framework’s
performance, as illustrated in Fig. 7(b). Notably, an enhancement
in anomaly detection performance is observed as the hidden

dimension increases from 1 to 64. Nonetheless, surpassing this
threshold results in a decline of performance. This decline may
be due to the increased risk of overfitting associated with the
increase in model parameters. Therefore, it is concluded that a
64-dimensional hidden embedding suffices to provide adequate
information for subsequent anomaly detection tasks across most
datasets.
Influence of the number of test rounds: In this experiment, we
further explore the influence of test rounds on the model across
different R values. Fig. 7(c) illustrates the variation of AUC

6634

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 6, NOVEMBER/DECEMBER 2024

values. As the R value increases, the AUC stabilizes and shows
some improvement. Based on the experimental findings, only
50 tests are necessary to stabilize the results. This enhancement
can be attributed to the increased number of rounds, which helps
mitigate the impact of randomness generated in the multi-view
discrimination module and allows for the capture of a broader
range of negative pattern information. However, excessively
high numbers of rounds can lead to an escalation in the computational overhead of the model. Nevertheless, compared to
methods relying on subgraph sampling, the proposed method
exhibits superior performance with fewer rounds.
VI. CONCLUSION
In this paper, we proposed a novel hybrid method via multiview discriminative awareness learning for graph anomaly detection. The anomaly detection task was completed through two
distinct self-supervised modules, namely the graph reconstruction module and the multi-view discrimination module. The
graph reconstruction module effectively identified the degree
of anomalies of a node by leveraging reconstruction errors.
The multi-view discrimination module provided more diverse
supervised signals by generating positive and negative views for
view-level contrast. The experimental results on six benchmark
datasets demonstrated that the proposed method outperformed
existing state-of-the-art models in terms of AUC when solving graph anomaly detection problems. Despite the superior
performance gained by the proposed method, a drawback is
the intensive memory utilization, particularly when processing
large-scale datasets. Consequently, our future work will concentrate on the memory optimization to address this concern.
REFERENCES
[1] Z. Wu, S. Pan, F. Chen, G. Long, C. Zhang, and S. Y. Philip, “A comprehensive survey on graph neural networks,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 32, no. 1, pp. 4–24, Jan. 2021.
[2] K. Berahmand, M. Mohammadi, F. Saberi-Movahed, Y. Li, and Y. Xu,
“Graph regularized nonnegative matrix factorization for community detection in attributed networks,” IEEE Trans. Netw. Sci. Eng., vol. 10, no. 1,
pp. 372–385, Jan./Feb. 2023.
[3] Z. Chen, Z. Wu, S. Wang, and W. Guo, “Dual low-rank graph autoencoder
for semantic and topological networks,” in Proc. 37th AAAI Conf. Artif.
Intell., 2023, pp. 4191–4198.
[4] Y. Huang, L. Wang, F. Zhang, and X. Lin, “Unsupervised graph outlier
detection: Problem revisit, new insight, and superior method,” in 2023
IEEE 39th Int. Conf. Data Eng., 2023, pp. 2565–2578.
[5] X. Ma et al., “A comprehensive survey on graph anomaly detection
with deep learning,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12,
pp. 12012–12038, Dec. 2023.
[6] S. Rao, A. K. Verma, and T. Bhatia, “A review on social spam detection: Challenges, open issues, and future directions,” Expert Syst. Appl.,
vol. 186, pp. 1–31, 2021.
[7] X. Hu, H. Chen, S. Liu, H. Jiang, G. Chu, and R. Li, “BTG: A bridge to
graph machine learning in telecommunications fraud detection,” Future
Gener. Comput. Syst., vol. 137, pp. 274–287, 2022.
[8] S. Xu, Y. Qian, and R. Q. Hu, “Data-driven edge intelligence for robust
network anomaly detection,” IEEE Trans. Netw. Sci. Eng., vol. 7, no. 3,
pp. 1481–1492, Third Quarter 2020.
[9] G. Zhang et al., “eFraudCom: An e-commerce fraud detection system via
competitive graph neural networks,” ACM Trans. Inf. Syst., vol. 40, no. 3,
pp. 1–29, 2022.
[10] G. Pang, C. Shen, L. Cao, and A. V. D. Hengel, “Deep learning for anomaly
detection: A review,” ACM Comput. Surv., vol. 54, no. 2, pp. 1–38, 2021.

[11] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” in Proc. ACM SIGMOD Int. Conf. Manage.
Data, 2000, pp. 93–104.
[12] B. Perozzi and L. Akoglu, “Scalable anomaly ranking of attributed
neighborhoods,” in Proc. SIAM Int. Conf. Data Mining, 2016,
pp. 207–215.
[13] X. Xu, N. Yuruk, Z. Feng, and T. A. Schweiger, “SCAN: A structural
clustering algorithm for networks,” in Proc. 13th ACM SIGKDD Int. Conf.
Knowl. Discov. Data Mining, 2007, pp. 824–833.
[14] J. Li, H. Dani, X. Hu, and H. Liu, “Radar: Residual analysis for anomaly
detection in attributed networks,” in Proc. 26th Int. Joint Conf. Artif. Intell.,
2017, pp. 2152–2158.
[15] Z. Peng et al., “ANOMALOUS: A joint modeling approach for anomaly
detection on attributed networks,” in Proc. 27th Int. Joint Conf. Artif. Intell.,
2018, pp. 3513–3519.
[16] K. Ding, J. Li, R. Bhanushali, and H. Liu, “Deep anomaly detection on
attributed networks,” in Proc. SIAM Int. Conf. Data Mining, 2019, pp. 594–
602.
[17] Y. Pei, T. Huang, W. van Ipenburg, and M. Pechenizkiy, “ResGCN:
Attention-based deep residual modeling for anomaly detection on attributed networks,” in 2021 IEEE 8th Int. Conf. Data Sci. Adv. Analytics,
2021, pp. 1–2.
[18] X. Luo et al., “ComGA: Community-aware attributed graph anomaly
detection,” in Proc. 15th ACM Int. Conf. Web Search Data Mining, 2022,
pp. 657–665.
[19] Y. Liu, Z. Li, S. Pan, C. Gong, C. Zhou, and G. Karypis, “Anomaly
detection on attributed networks via contrastive self-supervised learning,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2378–2392,
Jun. 2022.
[20] M. Jin, Y. Liu, Y. Zheng, L. Chi, Y.-F. Li, and S. Pan, “ANEMONE:
Graph anomaly detection with multi-scale contrastive learning,” in Proc.
30th ACM Int. Conf. Inf. Knowl. Manage., 2021, pp. 3122–3126.
[21] Y. Zheng, M. Jin, Y. Liu, L. Chi, K. T. Phan, and Y.-P. P. Chen, “Generative and contrastive self-supervised learning for graph anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12220–12233,
Dec. 2023.
[22] J. Zhang, S. Wang, and S. Chen, “Reconstruction enhanced multi-view
contrastive learning for anomaly detection on attributed networks,” in Proc.
31st Int. Joint Conf. Artif. Intell., 2022, pp. 2376–2382.
[23] T. N. Kipf and M. Welling, “Semi-supervised classification with graph
convolutional networks,” in Proc. Int. Conf. Learn. Representations, 2016,
pp. 1–14.
[24] H. Fan, F. Zhang, and Z. Li, “AnomalyDAE: Dual autoencoder for anomaly
detection on attributed networks,” in 2020 IEEE Int. Conf. Acoust. Speech
Signal Process., 2020, pp. 5685–5689.
[25] P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Liò, and Y. Bengio,
“Graph attention networks,” in Proc. Int. Conf. Learn. Representations,
2018, pp. 1–12.
[26] A. Roy et al., “GAD-NR: Graph anomaly detection via neighborhood
reconstruction,” in Proc. 17th ACM Int. Conf. Web Search Data Mining,
2024, pp. 576–585.
[27] J. Duan et al., “Graph anomaly detection via multi-scale contrastive
learning networks with augmented view,” in Proc. AAAI Conf. Artif. Intell.,
2023, pp. 7459–7467.
[28] J. Duan et al., “Normality learning-based graph anomaly detection via
multi-scale contrastive learning,” in Proc. 31st ACM Int. Conf. Multimedia,
2023, pp. 7502–7511.
[29] J. Pan, Y. Liu, Y. Zheng, and S. Pan, “PREM: A simple yet effective
approach for node-level graph anomaly detection,” in 2023 IEEE Int. Conf.
Data Mining, 2023, pp. 1253–1258.
[30] Y. Liu et al., “Graph self-supervised learning: A survey,” IEEE Trans.
Knowl. Data Eng., vol. 35, no. 6, pp. 5879–5900, Jun. 2023.
[31] T. N. Kipf and M. Welling, “Variational graph auto-encoders,” 2016,
arXiv:1611.07308.
[32] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2022, pp. 16000–16009.
[33] Q. Tan et al., “MGAE: Masked autoencoders for self-supervised learning
on graphs,” 2022, arXiv:2201.02534.
[34] J. Li et al., “What’s behind the mask: Understanding masked graph
modeling for graph autoencoders,” in Proc. 29th ACM SIGKDD Conf.
Knowl. Discov. Data Mining, 2023, pp. 1268–1279.
[35] Z. Hou et al., “GraphMAE: Self-supervised masked graph autoencoders,”
in Proc. 28th ACM SIGKDD Conf. Knowl. Discov. Data Mining, 2022,
pp. 594–604.

LIAN et al.: GRAPH ANOMALY DETECTION VIA MULTI-VIEW DISCRIMINATIVE AWARENESS LEARNING

[36] L. Wang, X. Tao, Q. Liu, and S. Wu, “Rethinking graph masked autoencoders through alignment and uniformity,” in Proc. AAAI Conf. Artif.
Intell., 2024, pp. 15528–15536.
[37] P. Veličković, W. Fedus, W. L. Hamilton, P. Liò, Y. Bengio, and R. D.
Hjelm, “Deep graph infomax,” in Proc. Int. Conf. Learn. Representations,
2019, pp. 1–17.
[38] K. Hassani and A. H. Khasahmadi, “Contrastive multi-view representation
learning on graphs,” in Proc. Int. Conf. Mach. Learn., 2020, pp. 4116–
4126.
[39] L. Lin and J. Chen, “Spectral augmentation for self-supervised learning on
graphs,” in Proc. 11th Int. Conf. Learn. Representations, 2023, pp. 1–27.
[40] X. Shen, D. Sun, S. Pan, X. Zhou, and L. T. Yang, “Neighbor contrastive
learning on learnable graph augmentation,” in Proc. AAAI Conf. Artif.
Intell., 2023, pp. 9782–9791.
[41] D. B. Skillicorn, “Detecting anomalies in graphs,” in 2007 IEEE Intell.
Secur. Informat., 2007, pp. 209–216.
[42] K. Ding, J. Li, and H. Liu, “Interactive anomaly detection on attributed
networks,” in Proc. 12th ACM Int. Conf. Web Search Data Mining, 2019,
pp. 357–365.
[43] X. Song, M. Wu, C. Jermaine, and S. Ranka, “Conditional anomaly
detection,” IEEE Trans. Knowl. Data Eng., vol. 19, no. 5, pp. 631–645,
May 2007.

Jie Lian received the B.S. degree from the School
of Cyber Security and Computer, Hebei University,
Baoding, China in 2023. He is currently working
toward the M.S. degree with the College of Computer
and Data Science, Fuzhou University, Fuzhou, China.
His research interests include machine learning,
graph representation learning, and graph anomaly
detection.

Xuzheng Wang received the master’s degree from
the Department of Computer Science, University of
Leicester, Leicester, U.K., in 2016. He is currently
working toward the D.Eng. degree with the College
of Computer and Data Science, Fuzhou University,
Fuzhou, China. His research interests include machine learning, multi-view learning, and anomaly detection.

Xincan Lin received the B.S. degree from the College of Mathematics and Computer Science, Fuzhou
University, Fuzhou, China, in 2021. He is currently
working toward the M.S. degree with the College
of Computer and Data Science, Fuzhou University,
Fuzhou, China. His research interests include machine learning, multiview learning, and graph neural
networks.

6635

Zhihao Wu received the B.S. degree in 2021 from
the College of Mathematics and Computer Science,
Fuzhou University, Fuzhou, China, where he is currently working toward the M.S. degree with the College of Computer and Data Science. His research interests include machine learning, multiview learning,
and graph neural networks.

Shiping Wang (Senior Member, IEEE) received the
Ph.D. degree from the University of Electronic Science and Technology of China, Chengdu, China,
in 2014. From 2013 to 2014, he was a Visiting
Scholar with the University of Alberta, Edmonton,
AB, Canada. He was a Research Assistant with the
National University of Singapore, Singapore, from
January 2014 to August 2014, and a Research Fellow
with Nanyang Technological University of Singapore, Singapore, from 2015 to 2016. From 2019 to
2020, he was also a Visiting Researcher with Peking
University, Beijing, China. He is currently a Professor with the College of
Computer and Data Science, and the Director of the Fujian Provincial Key
Laboratory of Intelligent Metro, Fuzhou University, Fuzhou, China. His research
interests include machine learning, deep learning, feature representation, and
multimodal fusion.

Wenzhong Guo received the B.S. and M.S. degrees
in computer science and technology and the Ph.D. degree in communication and information system from
Fuzhou University, Fuzhou, China, in 2000, 2003, and
2010, respectively. He completed the Postdoctoral
Fellow with the Institute of Computer Science, National University of Defense and Technology, Changsha, China, in 2013, and a Senior Visiting Scholar
with the Faculty of Engineering, Information and
System, University of Tsukuba, Tsukuba, Japan, in
2013. He is currently a Professor with the College
of Computer and Data Science, Fuzhou University, and leads the Network
Computing and Intelligent Information Processing Laboratory, which is a key
laboratory of Fujian Province, China. He is also the Deputy Director of the
Laboratory of Spatial Data Mining and Information Sharing, which is a key
laboratory of ministry of education, China. He has authored or coauthored more
than 130 technical articles in scientific journals and conference proceedings. His
research interests include VLSI physical design, wireless sensor networks, Big
Data, and image processing. He is also a Member of ACM and Senior Member
of the China Computer Federation (CCF).
PAPER_TEXT
