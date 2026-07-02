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
# [320] Unsupervised Anomaly Detection on Attributed Networks With Graph Contrastive Learning for Consumer Electronics Security
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
编号：320
题名：Unsupervised Anomaly Detection on Attributed Networks With Graph Contrastive Learning for Consumer Electronics Security
年份：2024
DOI：10.1109/tce.2024.3355122
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2024.3355122.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测、IoT、车联网、工业互联网与边缘安全
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\320.txt
- 原始字符数：58940
- 本次发送字符数：58940
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
4062

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Unsupervised Anomaly Detection on Attributed
Networks With Graph Contrastive Learning
for Consumer Electronics Security
Bo Xu , Member, IEEE, Jinpeng Wang , Zhehuan Zhao , Member, IEEE, Hongfei Lin ,
and Feng Xia , Senior Member, IEEE

Abstract—The proliferation of consumer electronic products
has engendered a substantial surge in data generation and
information exchange, concurrently escalating the potential for
security threats. Detecting anomalies effectively on attributed
networks has undeniable positive significance for consumer
electronic security, such as fraudulent user detection, malicious
consumption actions analysis, and network threat detection.
However, the lack of real tags poses great challenges for detecting
anomalies. Therefore, this paper introduces an unsupervised
learning framework, namely ADVANCE, to jointly optimize the
graph contrastive learning module and the network reconstruction module to accurately discover the anomalies on attributed
networks in unsupervised scenarios. Specifically, ADVANCE first
constructs the target view and the self-enhanced view to encode
view representations by maximizing the consistency between
the two views with graph contrastive learning. Subsequently,
a network reconstruction module is introduced to assess the
anomaly status of each node based on the degree of consistency
from both topological structure and node attributes perspectives.
The nodes with higher reconstruction errors are considered as
anomalous nodes. Finally, the two complementary modules are
jointly trained to enhance the accuracy of anomaly detection.
Extensive experimental results on three benchmark datasets
demonstrate the remarkable effectiveness of our proposed framework in unsupervised anomaly detection.
Index Terms—Anomaly detection, attributed networks, graph
contrastive learning, unsupervised learning, consumer electronics
security.

I. I NTRODUCTION
ITH the popularity of consumer electronics [1], [2], a
substantial volume of electronic consumption behaviors rapidly disseminate across the Internet, which constitutes
a complex attributed network and fosters an increasing number

W

Manuscript received 8 September 2023; revised 7 November 2023; accepted
11 January 2024. Date of publication 17 January 2024; date of current
version 26 April 2024. This work was supported in part by the National
Natural Science Foundation of China under Grant 62072073, Grant 61906028,
Grant 62076046, and Grant 62106034; and in part by the Dalian Innovation
Fund under Grant 2021JJ12GX016. (Corresponding author: Feng Xia.)
Bo Xu, Jinpeng Wang, and Zhehuan Zhao are with the School of Software,
Dalian University of Technology, Dalian 116620, China (e-mail: boxu@
dlut.edu.cn; wangjinpengdlut@163.com; z.zhao@dlut.edu.cn).
Hongfei Lin is with the School of Computer Science and Technology,
Dalian University of Technology, Dalian 116620, China (e-mail: hflin@
dlut.edu.cn).
Feng Xia is with the School of Computing Technologies, RMIT University,
Melbourne, VIC 3000, Australia (e-mail: f.xia@ieee.org).
Digital Object Identifier 10.1109/TCE.2024.3355122

of financial fraudulent users and malicious consumer behaviors. This burgeoning landscape poses significant security
challenges for consumer electronics, consequently attracting extensive research attention in recent years [3], [4], [5].
Detecting anomalies on attributed networks can facilitate the
early identification of fraudulent users and financial fraud
activities, which plays a crucial role in purifying the online
consumption environment and ensuring the safety of consumer
electronics.
Attribute networks are prevalent across various practical applications. Compared with the conventional plain
networks which solely encompass interactions between nodes,
attributed networks contain rich feature information of each
node [6], [7], [8], providing possibilities for modeling more
complex interaction systems. Detection of anomalous nodes
in attributed networks is of great significance for various security-related applications, and has become an urgent
research question in recent years, such as social spam detection [9], [10], financial fraud detection [11], [12], and network
intrusion detection [13], [14], [15]. However, the anomalous
patterns of nodes on attributed networks are related to not
only the interactions between nodes but also the inconsistency
of node attributes. Thus, detecting anomalies on attributed
networks is highly challenging.
Early anomaly detection methods leverage shallow
mechanisms such as CUR decomposition [16], subspace
selection [17], ego-network analysis [18], and residual
analysis [19], [20] to identify anomalous nodes. However,
these methods usually rely on feature engineering or observed
node interactions, which exhibit insensitivity to the nonlinear
characteristics of networks. Recently, graph neural networks
have found widespread application in anomaly detection [21],
[22], [23], [24], which aim to capture network nonlinearity
and learn node representations for anomalous patterns with
deep neural networks. Due to the high cost and unreliability
associated with labeling anomalies, unsupervised methods for
anomaly detection are more reliable [25], [26].
The rise of graph contrastive learning provides a new
direction for unsupervised anomaly detection [28], [38]. Graph
contrastive learning has promising properties for anomaly
detection. First, maximizing mutual information strategy of
graph contrastive learning can effectively learn the deep
information of graphs without the guidance of labels. Second,
graph contrastive learning models measure the consistency

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1558-4127 
See https://www.ieee.org/publications/rights/index.html for more information.

XU et al.: UNSUPERVISED ANOMALY DETECTION ON ATTRIBUTED NETWORKS

among elements within each instance pair and the consistency
is highly correlated with the abnormality of instance. However,
existing SOTA (state-of-the-art) methods based on contrastive
learning typically constructed positive and negative instance
pairs based on node subgraphs. These methods learned node
representations by maximizing the mutual information (MI)
between the target node and positive instances and minimizing
the mutual information (MI) between the target node and
negative instances, which may not be effective for learning
heterogeneous graphs, where the target node and its neighbors
do not belong to the same category.
To overcome the shortcomings, some studies have constructed different view information to learn the embedding
representations of networks by maximizing the similarity
between different views [29], [56]. Based on this inspiration,
we can construct views with different structural information
and encode the node representations by maximizing the MI of
different views, so as to detect anomalies more efficiently and
ensure the safety of consumer electronics.
In this paper, we propose a novel view-level unsupervised contrastive learning framework for anomaly detection
on attributed networks (ADVANCE for abbreviation), which
contains a graph contrastive learning module and a network
reconstruction module. The graph contrastive learning module
aims to maximize the consistency between the target view and
the self-enhanced view. The network reconstruction module
measures the reconstruction error of nodes from both the
structural and attribute perspectives. Specifically, ADVANCE
first generates a target view with edge attributes information
from the original data as the learning guidance, and then
constructs a self-enhanced view by using the full graph
parameterization method and k-nearest neighbors algorithm.
Next, two weight-shared graph convolutional networks are
used to generate representations of the two views. After
obtaining the representations of the two views, we construct
a contrastive loss to maximize the MI between the target
view and the self-enhanced view, thereby encoding deeper
potential information of the graph. The network reconstruction
module receives the potential representations of the selfenhanced view and reconstructs the original network from two
perspectives: node attributes and network structure. Finally,
the two complementary modules are integrated to detect
anomalous nodes through reconstruction errors of nodes. Our
primary contributions can be summarized as follows:
• We design a view-level contrastive learning model
that encodes view representations by maximizing the
consistency between the self-enhanced view and the welldesigned target view with edge attributes.
• We propose a novel unsupervised learning framework,
namely ADVANCE, for anomaly detection on attributed
networks. ADVANCE can effectively integrate graph
contrastive learning-based and network reconstructionbased modules and enhance the efficiency of anomaly
detection by jointly optimizing the two complementary
modules, which provides a high guarantee for the safety
of consumer electronics.
• We perform extensive experiments on three benchmark
datasets to evaluate the performance of the ADVANCE.

4063

The results validate the effectiveness of ADVANCE,
which outperforms existing SOTA methods.
The rest of the paper is organised as follows: Section II
summarizes related work. Section III introduces the concept
of attributed networks and formally formulates the problem
of unsupervised anomaly detection on attributed networks.
Section IV discusses our optimal solution (ADVANCE) and
describes its architecture in detail, and Section V represents
the experiments and results. Finally, Section VI concludes the
paper.
II. R ELATED W ORK
A. Anomaly Detection on Attributed Networks
Recently, how to detect anomalies on attributed networks
has aroused extensive research interest. Anomaly detection
can be regarded as a data mining process that aims to
identify data points deviating from the normal patterns
within a dataset [30], [31]. Early anomaly detection works
relied heavily on feature engineering constructed by domain
experts [32], [33], which not only requires a lot of domain
knowledge but also limits the performance of anomaly detection methods. Many machine learning techniques are also
used to detect anomalies on attributed networks, Radar [19]
characterized the residuals of attributes information and its
coherence with network information, addressing the issue
of complicating the residual modeling process due to interinstance interactions. ANOMALOUS [16] combined CUR
decomposition and residual analysis, treating them as a whole
for attribute selection and anomaly detection. However, these
shallow methods cannot effectively be extended to highdimensional data and lack the ability to capture non-linear
attributes in networks.
To alleviate the above drawbacks, recent studies have
adopted deep learning techniques to detect anomalies on
attributed networks [25], [34]. Dual-SVDAE [36] introduced
a dual hypersphere learning mechanism to learn hyperspheres
for normal nodes and measures the distances from nodes to
the learning centers of these hyperspheres to detect anomalous nodes. CFAD [35] learned causal relations in attributed
networks and identified abnormal nodes from the perspective
of structure and context. GraphBEAN [37] focuses on the
rich interactions in bipartite graphs, which uses a bipartite
node-and-edge-attributed graph to generate anomaly scores
for each edge and each bipartite node, respectively. Although
these methods have achieved better performance than shallow
approaches by using deep neural networks, the single graph
convolutional network encoder still has the limitation of not
being able to fully model the complex attributes of the
network. Furthermore, marking anomalous nodes is also a
challenging task.
With the popularization of contrastive learning, the application of this approach to anomaly detection on attributed
networks has attracted the attention of researchers. SubCR [38] established two contrastive learning views to encode
local and global information related to anomalies, and then
introduced a reconstruction module based on masked autoencoder to identify nodes with large reconstruction errors as

4064

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

anomalous nodes. Hu and Shao [39] proposed an improved
unsupervised contrastive learning method, which comprehensively compared both the internal and external aspects of
subgraphs and leverages a trained teacher model as prior
knowledge to modify the sampling probabilities for selectively
aggregating neighbor nodes. However, related researches in
this field remain limited, and the development of new anomaly
detection methods based on contrastive learning is still worth
exploring.

TABLE I
D ESCRIPTION OF N OTATIONS

B. Graph Contrastive Learning
Contrastive learning models the general characteristics of
networks by letting the model learn which nodes are similar
or different without labels. The great success of contrastive
learning in computer vision [40], [41] has motivated its continuous migration to the field of graph learning. DGI [57]
maximized the mutual information between graph-enhanced
representations and the currently extracted graph information,
enabling the node representations learning in an unsupervised
setting. GMI [58] proposed a novel concept, Graphical Mutual
Information (GMI), which is trained by maximizing the GMI
between the input and output of a Graph Neural Encoder.
GIC [42] performed joint optimized clustering of nodes and
retained Infomax target items of MI between nodes of the same
clustering. The fundamental idea behind graph contrastive
learning is to maximize the mutual information between nodes,
which brings the representations of semantically similar nodes
closer while simultaneously distancing the representations of
semantically unrelated nodes. However, the above-mentioned
methods aim to maximize the MI between the embeddings of
the target node and its neighboring nodes, which may not be
effective for learning heterogeneous graphs, where the target
node and its neighbors do not belong to the same category.
Recent studies have considered the above problems and constructed different view information to learn the representations
of graphs by maximizing the similarity between different views. MVGRL [29] proposed a contrastive multi-view
representation learning method by contrasting embeddings
from two structural views of graphs. SAIL [43] performed self-augmented graph contrastive learning through
two complementary self-distilling regularization modules,
i.e., intra-graph and inter-graph knowledge distillation.
SUBLIME [44] constructed an “anchor graph” from the
original data as a learning guide, and utilized contrastive
learning to maximize the mutual information between the
anchor graph and the learned graph. Graph contrastive
learning is also beneficial for diverse applications, such as
chemical prediction [45], [46], federated learning [47], [48],
and recommendation [49], [50], [51]. Numerous studies have
demonstrated the wide application of graph contrastive learning, but how to detect anomalies on attributed networks with
graph contrastive learning is still a novel and challenging
research topic.
III. P ROBLEM F ORMULATION
In this section, we formally define attributed networks and
the unsupervised anomaly detection problem on attributed

networks. Table I lists the description of the notations mainly
used in this paper.
Definition 1 (Attributed Networks): An attributed network
can be represented as G = (V, E, X), where V = {v1 , . . . , vN }
and E denote the set of nodes and edges, respectively. X ∈
RN×d is the attribute matrix, where N is the number of nodes
in the attributed network and d is the dimension of attributes.
The ith row vector xi ∈ Rd in the attribute matrix is the
attributes for the ith node vi .
Definition 2 (Unsupervised Anomaly Detection on Attributed
Networks): The objective of this paper is to detect nodes
with significant differences in attributed networks based on
structure and attribute vectors in an unsupervised setting.
Specifically, given an attributed network G = (V, E, X),
ADVANCE learns an anomaly score function score(.) to
calculate each node’s anomaly score score(vi ), which measures
the degree of abnormality for each node without anomaly
labels as training guidance. Generally, nodes with higher
anomaly scores are more likely to be considered as anomalous
nodes.
IV. T HE F RAMEWORK OF ADVANCE
This section elaborates on our proposed ADVANCE, which
is shown in Fig. 1. The following subsections provide a
detailed overview of each module respectively.
A. Graph Contrastive Learning Module
As a critical component of ADVANCE, Graph Contrastive
Learning Module aims to establish two distinct views to

XU et al.: UNSUPERVISED ANOMALY DETECTION ON ATTRIBUTED NETWORKS

4065

Fig. 1. The overall pipeline of ADVANCE. The target is to predict the anomaly score of each node in attributed networks. In graph contrastive learning
module (a), “node v.s. node” consistency is learned by contrasting the target view with the self-enhanced view, thereby encoding deep information of the
graph. In network reconstruction module (b), the optimal graph representation encoded by the contrastive learning module is used to reconstruct node attributes
and topological structure, and to identify anomalous nodes through reconstruction loss.

TABLE II
C ALCULATION M ETHODS FOR S IX S IMILARITY I NDICES

2) Self-Enhanced View Learning Component: The main
function of the Self-Enhanced View Learning Component is
to generate a self-enhanced adjacency matrix S ∈ RN×N with
a parameterized model to construct self-enhanced view Gs =
(S, X) for graph contrastive learning. Inspired by previous
work [44], we use the full graph parameterization method as
the self-enhanced view learner:
S = Fω (X) = σ (W)

contrast: the self-enhanced view that learns the optimal graph
latent representations and the target view that guides representation learning. Subsequently, node-level contrastive learning
is employed to maximize consistency between the two views,
thus encoding graph information effectively.
1) Target View Generating Component: A target view is
defined as a view constructed directly from input data rather
than being learned, which aims to provide correct guidance
for graph contrastive learning. In this paper, we fully consider the interaction information between nodes and attributes
information contained in the attributed network and construct
the target view Gt = (At , X) with edge attributes information,
where At ∈ RN×N denotes the adjacency matrix with edge
attributes, X ∈ RN×d denotes the attribute matrix for nodes.
Specifically, six similarity indices are selected to calculate the
similarity of two connected nodes as edge attributes, including
the degree of node vi , the degree of node vi s neighbors,
common neighbors (CN), Admaic-Adar Index, Jaccard Index,
and Preferential Attachment Index (PA). TABLE II lists the
calculation methods for six similarity indices, where the N(vi )
denotes the neighbor’s set of node vi . Next, the adjacency
matrix At with edge attributes is constructed as:
At = λ

EA

◦A

(1)

where λEA is the edge attribute matrix calculated by the
similarity of two connected nodes, A denotes the original graph
adjacency matrix and ◦ represents the Hadamard product. To
ensure the stability and effectiveness of the learning process,
we implement a target view update mechanism to update the
target view, which will be described in Section IV-A4.

(2)

where ω = W is a parameter matrix and σ is a nonlinear activation function. Full graph parameterization method
assumes that each edge exists independently in the graph, so
the adjacency matrix can be optimized directly without the
participation of node features, which is very advantageous for
modeling attributed networks with node attribute anomalies.
However, the adjacency matrix S constructed by the full
graph parameterization method is usually dense, which will
mask important interactions of the network and consume
computing resources extremely. Hence, we use the k-nearest
neighbors (knn) algorithm to reserve the edges with top-k
connection values for each node as its neighborhood structure
to build the sparse self-enhanced adjacency matrix S:

Sij , Sij ∈ top_k(Si )
(3)
Sij =
/ top_k(Si )
0, Sij ∈
where top_k(Si ) is the set of top-k values of row vector Si .
3) Contrastive Learning Component: Given the target view
and self-enhanced view, we perform the normalization process
to ensure that the adjacency matrix is symmetric and consists
of non-negative elements:
A = sym(nor(A)) =

σ (A) + σ (A)T
2

(4)

where σ is a non-linear activation function that maps elements
to [0, 1] and (.)T denotes the transposition operation.
After obtaining normalized views (i.e., Gt and Gs ), two
weight-shared Graph Convolutional Network Encoders [52]
are utilized to generate multi-view representations.
Specifically, we input the target view Gt and the self-enhanced
view Gs into GCN1 and GCN2 to perform neighborhood

4066

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

information aggregation and output corresponding view
representations Zt and Zs :
⎧




 
⎨ Zt = GCN1(Gt ) = MLP σ Ât σ Ât XW (0) W (1) W (2)

 (5)
 
⎩ Zs = GCN2(Gs ) = MLP σ Ŝσ (ŜXW (0) )W (1) W (2)
−1/2

−1/2

−1/2

−1/2

where Ât = Dt
(At + I)Dt
, Ŝ = Ds (S + I)Ds ,
X ∈ RN×d represents the attribute matrix of nodes, W (0) , W (1) ,
W (2) is the learnable weight matrix in Graph Convolutional
Network Encoders. Here, Dt and Ds are the diagonal degree
matrix of (At + I) and (S + I), respectively. We notice that
using only A means that only the characteristic information of
all nodes’ neighbors is considered, but the nodes themselves
are neglected. Therefore, we add self-connections in the graph
(i.e., using (A+I)) to ensure that the nodes’ own characteristic
information also participates in aggregation.
The main objective of contrastive learning is to encourage
the representations of semantically similar pairs (x, x+ ) to
be close, while the representations of semantically dissimilar
pairs (x, x− ) should be pushed apart. To achieve the above
goal, a contrastive loss is designed to maximize the similarity
between the same nodes’ representations from different views.
Specifically, in Eq. (6) and Eq. (7), after obtaining the
representations Zt and Zs , we apply a symmetric normalized
temperature-scaled cross-entropy loss to design a node-level
contrastive loss function for the target view and self-enhanced
view, which can pull the representations of the same nodes
from different views close to each other while pushing the
representation of one node far away from the representations
of other nodes from both the same view and different views:


v
v
sim Zt i ,Zs i /ϑ

L1cl (vi ) = −log

e
N


vj 
v
sim Zt i ,Zs /ϑ

(6)

j=1 e



v
v
sim Zs i ,Zt i /ϑ

L2cl (vi ) = −log

e
N


vj 
v
sim Zs i ,Zt /ϑ

(7)

j=1 e

where ϑ represents the temperature factor that controls the
concentration level of the distribution, sim(.) is the similarity
function to measure the similarity of representations of two
nodes. Combining the above two losses, the objective function
of the graph contrastive learning module is defined as follows:
Lcl =

1
2N

N 

L1cl (vi ) + L2cl (vi )


(8)

i=1

where N is the number of nodes in the attributed network.
Through the above equation, we can encode graph information
and learn the optimal graph representation without the guidance of labels.
4) Target View Update Mechanism: In order to make the
self-enhanced view learn the graph representations containing
fewer anomalous information, we design a target view update
mechanism during the contrastive learning process. The main
idea of the target view update mechanism is to update
the target structure slowly according to the probability of
edges existing between every pair of nodes calculated by

the constantly learning representations of self-enhanced view
Zs instead of keeping the target view Gt unchanged. The
assumption behind the target view update mechanism is that if
there is a real link between two nodes, its connectivity patterns
can be well reconstructed. On the contrary, if the probability of
a connection existing between two nodes is low, it implies that
there is no link or anomalous link between them. Specifically,
we take the latent representations of self-enhanced view Zs as
input and predict whether there is a link between each pair of
two nodes:
P = sigmoid Zs ZsT

(9)

Next, given a decay rate δ ∈ [0, 1], the target view structure
At is updated every ε iterations as follows:
At = δAt + (1 − δ)P

(10)

Through the target view update mechanism, the selfenhanced view Gs can constantly correct anomalous patterns
existing in the target view and alleviate structural anomaly.
B. Network Reconstruction Module
The network reconstruction module consists of structure
reconstruction component and attribute reconstruction component, with the objective of decoding the self-enhanced view
representations Zs to reconstruct network structure information
and node attributes information. After that, anomalous nodes
can be identified by the reconstruction error of nodes.
1) Structure Reconstruction Component: The structure
reconstruction component mainly discusses how to reconstruct
the original topological structure with the learned potential
representations Zs from the graph contrastive learning module.
If Ã denotes the reconstructed adjacency matrix, then the
structural anomalies on the network can be determined by
using the structure reconstruction error RS = ||A − Ã||2F .
Specifically, if the neighborhood structural information of a
certain node can be effectively approximated to the original
structure through the structure reconstruction component, then
it is less likely that the node is an anomalous node. On
the contrary, if the neighborhood structural information of a
certain node cannot be effectively reconstructed, it implies the
presence of abnormal patterns in its structural information.
Therefore, a larger norm of RiS = ||ai − ãi ||2F indicates a higher
probability of network structural anomalies for the i-th node
on the attributed network. Particularly, we first use a graph
convolutional network as a structure reconstruction decoder to
decode the input potential representation Zs :


 
H = GCN3(Zs , A) = MLP σ ÂZs W (3) W (4)
(11)
where W (3) , W (4) is the learnable weight matrix in the structure
reconstruction decoder. Then, we predict whether there is a
link between each pair of nodes based on the decoding vector
H to generate the reconstructed adjacency matrix Ã:
Ã = sigmoid HH T

(12)

XU et al.: UNSUPERVISED ANOMALY DETECTION ON ATTRIBUTED NETWORKS

2) Attribute Reconstruction Component: In order to calculate the attribute reconstruction error RA = ||X − X̃||2F
to determine the attributed anomalies on the network, we
propose an attribute reconstruction decoder to approximate
the original node attributes information according to the
potential representation Zs generated by the graph contrastive
learning module. Similarly, if the reconstructed attributes of
a node are closer to the original attributes, the node is more
inclined to be a normal node. On the opposite side, if the
reconstructed attributes of a node are quite different from the
original attributes, it is of high probability to be anomalous.
Specifically, we utilize another graph convolutional network as
the attribute reconstruction decoder to reconstruct the original
attributes of nodes as follows:



  
X̃ = GCN4(Zs , A) = MLP σ Âσ ÂZs W (5) W (6) W (7)
(13)
where W (5) , W (6) , W (7) is the learnable weight matrix. To
jointly learn the reconstruction errors, we combine the structure reconstruction component and the attribute reconstruction
component to construct the objective function of the network
reconstruction module:
Lres = αRA + (1 − α)RS = α||X − X̃||2F + (1 − α)||A − Ã||2F
(14)
where α is an important control parameter to balance the
influence of structure and attribute reconstruction.
C. Anomaly Detection
To jointly train the graph contrastive learning module and
the network reconstruction module, we optimize the following
objective function:
L = μLcl + (1 − μ)Lres

(15)

where μ is a non-negative tuning parameter that measures the
importance of two complementary modules. Then an anomaly
score function is defined to detect anomalies. Inspired by [25],
taking node vi as an example, we can calculate the anomaly
score of node vi according to the reconstruction error:
score(vi ) = α||xi − x̃i ||2 + (1 − α)||ai − ãi ||2

(16)

where x̃i (xi ) is the reconstructed (original) attributes vector of
the node vi , ãi (ai ) is the i-th row vector of the reconstructed
adjacency matrix Ã (original graph adjacency matrix A),
which denotes the reconstructed (original) structure vector
of node vi . Specially, nodes with higher scores are more
likely to exhibit anomalous patterns, thus we can sort the
nodes according to the anomaly scores to identify anomalous
nodes. The calculation process of the ADVANCE framework
is summarized as Algorithm 1.

4067

Algorithm 1: The Calculation Process of ADVANCE
Input: Node attributs matrix X; Original graph adjacency
matrix A; Number of nearest neighbors k; Control
parameters for balancing the structure
reconstruction and attribute reconstruction α;
Tuning parameters for balancing graph contrastive
learning module and network reconstruction
module μ; Temperature factor ϑ; Target view
update mechanism decay rate δ; Target view
update mechanism interval ε; Epoch number ξ ;
Output: Anomaly score of all nodes score(V);
EA by the similarity of
1 Calculate edge attribute matrix λ
two connected nodes;
EA ◦ A;
2 Initialize target view Gt = (At , X) by At = λ
3 Initialize parameters
ω, W (0) , W (1) , W (2) , W (3) , W (4) , W (5) , W (6) , W (7) ;
4 for iter =1 to ξ do
5
Calculate S with Self-Enhanced View Learning
Component;
6
Establish self-enhanced view Gs = (S, X);
7
Normalize Gt , Gs with normalization operation;
8
Calculate view representations Zt , Zs with graph
contrastive learning encoder;
9
Calculate graph contrastive loss Lcl ;
10
Calculate reconstructed adjacency matrix Ã with
Structure Reconstruction Component;
11
Calculate reconstructed attribute matrix X̃ with
Attribute Reconstruction Component;
12
Calculate network reconstruction loss Lres ;
13
Calculate total loss of ADVANCE framework L;
14
Update parameters
ω, W (0) , W (1) , W (2) , W (3) , W (4) , W (5) , W (6) , W (7)
via back propagation;
15
if iter mod ε = 0 then
16
Calculate the probability P that there is a link
between each pair of nodes according to Zs ;
17
Update Gt by target view update mechanism
decay rate δ;
18
end
19 end
20 Calculate the anomaly score of all nodes score(V)
according to the reconstruction error;

aim to answer three research questions as follows: RQ1: How
effective is ADVANCE for detecting anomalies on attributed
networks under unsupervised settings? RQ2: How do key
hyper-parameters influence the performance of ADVANCE?
and RQ3: How do the contrastive learning component, structure reconstruction component, and attribute reconstruction
component impact the performance of ADVANCE?

V. E XPERIMENTS
In this section, we first introduce the dataset, the comparison
algorithm, and the evaluation criteria used in the experiments.
Next, we conduct numerous experiments to substantiate the
superior validity of the proposed framework ADVANCE. We

A. Datasets
To assess the performance of ADVANCE in anomaly detection, we employed three real-world attributed network datasets
that have been widely utilized in previous studies [28], [53]:

4068

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

TABLE III
T HE S TATISTICS OF THE DATASETS

•

Cora: Cora is an attributed network that contains seven
categories of published papers related to machine learning. It takes the form of a citation network where each
paper serves as a node, and edges denote the citation
relations between different papers.
• BlogCatalog: BlogCatalog constructs a social network
by gathering data from the blog-sharing website
BlogCatalog, where the users are represented as nodes,
and edges symbolize the following relationships between
users.
• Flickr: Flickr serves as a website for image management
and sharing. Similar to BlogCatalog, users on Flickr have
the ability to mutually follow each other, thereby forming
a social network.
Given the absence of ground truth anomalies in the aforementioned datasets, it is necessary to inject anomalies into a
clean attributed network to evaluate our proposed framework.
Specifically, we refer to two anomaly injection methods
commonly employed in previous researches [25], [54] to
inject structure anomaly and attribute anomaly for each
dataset. The statistics of the datasets are presented in
TABLE III.

B. Baselines and Evaluation Criteria
We conduct a comparative analysis of ADVANCE against
nine mainstream anomaly detection methods:
• Radar [19]: Radar models the residuals of node attributes
and their coherence with network structure, serving the
purpose of anomaly detection.
• ANOMALOUS [16]: ANOMALOUS jointly optimizes
attribute selection and anomaly detection using CUR
decomposition and residual analysis methods.
• DOMINANT [25]: DOMINANT utilizes graph convolutional autoencoder to jointly reconstruct network structure
and node attributes to identify anomalous nodes.
• DGI [57]: DGI maximized mutual information between
patch representations and corresponding high-level graph
summaries to characterize network information.
• DeepAE [55]: DeepAE uses Laplacian sharpening to
enlarge the difference between normal and anomalous nodes and calculate reconstruction errors to detect
anomalies.
• Deep2NAD [26]: Deep2NAD utilizes a Variational
AutoEncoder (VAE) to detect anomalies by simultaneously considering both network structure and node
attributes.
• ANEMONE [27]: ANEMONE performs multi-scale contrastive learning at both patch and context levels for
anomaly detection.

Fig. 2.

Performance of different anomaly detection methods w.r.t. AUC.

•

CoLA [28]: CoLA utilizes contrastive learning to learn
representations from node-subgraph instance pairs and
provides the discriminant scores of anomaly ranking.
• Sub-CR [38]: Sub-CR utilizes multi-view contrastive
learning to integrate local and global information so as
to provide high features for detecting anomalous nodes.
Furthermore, we use the average of three evaluation metrics
(i.e., AUC, Precision@K, and Recall@K) obtained from 5
independent training cycles to measure the performance of the
ADVANCE framework and baseline. The details of these three
evaluation metrics are extensively elaborated in [25].
C. Experiment Reproducibility
For the proposed framework ADVANCE, the number of
epoch and learning rate are set as 3000 and 0.005 for
BlogCatalog dataset and Flickr dataset and Cora dataset. To
generate the target view, the common neighbors (CN) is
selected as the edge attributes for the Flickr dataset and the
average of the calculated results of six similarity indices as
the edge attributes for the remaining datasets. For constructing
self-enhanced view, we use full graph parameterization learner
on all three datasets, and set the number of nearest neighbors
k to 40, 30, and 10 for the BlogCatalog dataset, Flickr dataset,
and Cora dataset, respectively. The tuning parameter μ that
measures the importance of graph contrastive learning module
and network reconstruction module are set to 0.8, 0.8, and 0.9
for the BlogCatalog dataset, Flickr dataset, and Cora dataset,
respectively. For the control parameter α that balances the
influence of structure reconstruction and attribute reconstruction, we follow the settings of previous work [25], [27]. For
the BlogCatalog and Flickr datasets, a reasonable choice for
α is approximately 0.4 to 0.7, while for the Cora dataset, a
reasonable choice is around 0.7 to 0.8. Finally, for the decay
rate δ and interval ε in the structure feedback mechanism,
the most suitable combination of parameters is selected for
each dataset according to Section V-E, which are {δ =
0.9999, ε = 0}, {δ = 0.9999, ε = 0}, and {δ = 0.999, ε =
0} for BlogCatalog dataset, Flickr dataset, and Cora dataset,
respectively.
D. Performance Comparison (RQ1)
Fig. 2 illustrates the comparison results of these methods
in terms of AUC value on three datasets and TABLE IV

XU et al.: UNSUPERVISED ANOMALY DETECTION ON ATTRIBUTED NETWORKS

4069

TABLE IV
P ERFORMANCE OF D IFFERENT A NOMALY D ETECTION M ETHODS W. R . T. P RECISION @K AND R ECALL @K

shows the performance of our framework and baselines in
terms of Precision@K and Recall@K for K = 50, 100,
200, 300. From the comparison results, we summarize the
following conclusions: (1) Our proposed ADVANCE outperforms all baselines on the BlogCatalog dataset, and achieves
the runner-up position on the Flickr and Cora datasets. The
superior performance of ADVANCE verifies the effectiveness
of the joint optimizing graph contrastive learning module and
network reconstruction module, which can better capture node
attributes and topology structure of attributed networks for
anomaly detection. (2) Compared with the deep learning-based
methods, shallow methods such as Radar and ANOMALOUS
can not achieve satisfactory results because these methods
lack the ability to model high-dimensional attributes vectors
and intricate network structures. Deep learning-based methods
(DOMINANT, DeepAE, and Deep2NAD) break through the
limitation of shallow mechanisms to capture the highly nonlinear attributes, which extensively leverages the intrinsic
information of the network and achieves superior performance
than the shallow methods. (3) The performance of methods
based on contrastive learning (ANEMONE, COLA, SubCR, and ADVANCE) is superior to the shallow and deep
learning methods, which indicates that the idea of mining
hidden information from graph data by contrastive learning
to provide auxiliary guidance for anomaly detection is feasible. However, DGI, which also adopts contrastive learning
mechanism, does not show competitive performance. The
reason behind this limitation lies in the use of node-to-globalinstance comparisons in contrastive learning, which cannot
capture anomalies within local substructure and is not friendly
to heterogeneous graphs. The outstanding performance of
Sub-CR can be attributed to its adept aggregation of localglobal structural information, an aspect that ADVANCE lacks
in its consideration. Node anomalies in the graph often

occur on different scales. For example, in social networks,
a user’s behavior may be considered normal within their
circle of friends (i.e., local anomalies) but not across the
entire network (i.e., global anomalies). Therefore, integrating
local and global structural information can better capture
structural features of different scales associated with anomaly
patterns.
E. Parameter Analysis (RQ2)
In this subsection, we investigate the impacts of four
important parameters on the performance of ADVANCE: the
tuning parameter μ, the number of nearest neighbors k, the
target view update mechanism decay rate δ, and the edge
attributes.
Tuning parameter μ aims to balance the importance of
graph contrastive learning module and network reconstruction
module. When μ = 1, we only use the information of
graph contrastive learning module to train ADVANCE while
ignoring the network reconstruction error. When μ = 0,
we use graph convolutional networks to encode view representations instead of using a contrastive learning mechanism
to mine the intrinsic information of graphs. Fig. 3(a) shows
the effect of different μ values on the performance. The
performance of ADVANCE degrades either without training
graph contrastive learning module (μ = 0) or without training
network reconstruction module (μ = 1), which demonstrates
that the joint optimization of two complementary modules
is helpful to improve the performance of ADVANCE in
detecting anomalies, especially the network reconstruction
module. Furthermore, the importance of different modules
varies on different datasets, and the optimal tuning parameters
for BlogCatalog, Flickr, and Cora datasets are 0.8, 0.8, and
0.9, respectively.

4070

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Fig. 3. Experimental results for parameter analysis. (a), (b), and (c) show the impact of different tuning parameter, numbers of nearest neighbors, and target
view update mechanism decay rate w.r.t. Precision@50, respectively.
TABLE V
E FFECT OF D IFFERENT E DGE ATTRIBUTES W. R . T. P RECISION @K

Fig. 4.

Experimental results for ablation study. (a), (b), and (c) show the performance of ADVANCE and its variants w.r.t. Precision@K.

The number of nearest neighbors k is crucial for constructing the self-enhanced view, which reflects the neighborhood
size of each node in the self-enhanced view. Smaller values
of k may not enable nodes to aggregate neighborhood features
adequately, while larger values of k may add invisible noise to
node attributes aggregation. Fig. 3(b) shows the performance
of ADVANCE with different numbers of nearest neighbors.
Overall, for BlogCatalog, Flickr, and Cora datasets, the best
performances are achieved when the number of nearest neighbors k are set as 40, 30, and 10, respectively.
The target view update mechanism decay rate δ plays a
critical role in controlling the update process of the target
view. A larger decay rate will cause the target view to be
updated too slowly, while a smaller decay rate may cause
the target view to update too sharply. When the decay rate
δ = 1, the target view is never updated and maintains the
original structure. The selection of the decay rate for the target
view update mechanism is critical in determining whether the
target view can effectively alleviate the structural anomalies
and guide the self-enhanced view to learn more valuable

network information. Fig. 3(c) shows the performance of
the ADVANCE framework for different target view update
mechanism decay rates. In the experiment, we set the target
view update mechanism interval ε to 0 for all three datasets.
As can be observed, various networks require distinct rates
of update for the target view. The optimal decay rate is δ =
0.9999 for BlogCatalog dataset and Flickr dataset and δ =
0.999 for the Cora dataset. Furthermore, the performance of
ADVANCE decreases when the decay rate δ = 1, which
proves the effectiveness of the target view update mechanism.
Edge attributes represent the edge attributes information
used when initializing the target view. Section IV-A1 mentions
that six similarity indices are considered to calculate the
similarity of two connected nodes as edge attributes. The
experimental results are shown in TABLE V, where Mean
of six indices denotes the average of the calculated results
of six similarity indices as the edge attributes. It can be
seen that different networks have different adaptability to
edge attributes. For BlogCatalog and Cora datasets, it is more
advantageous to consider six edge attributes simultaneously,

XU et al.: UNSUPERVISED ANOMALY DETECTION ON ATTRIBUTED NETWORKS

while for Flickr dataset, using common neighbors to calculate
edge attributes is more effective in detecting anomalous nodes.
F. Ablation Study (RQ3)
We further compare the results of ADVANCE and its
variables, namely ADVANCE w/o CL, ADVANCE w/o ARes
and ADVANCE w/o SRes. ADVANCE w/o CL, ADVANCE
w/o ARes, and ADVANCE w/o SRes denote the framework
without contrastive learning component (i.e., μ is set to 0),
without attribute reconstruction component (i.e., α is set to
0) and without structure reconstruction component (i.e., α is
set to 1) in anomaly detection, respectively. As we can see
in Fig. 4, ADVANCE outperforms all the variants consistently
on all three datasets, which indicates that all three components in ADVANCE contribute to the detection of anomalies.
Especially, ADVANCE outperforms ADVANCE w/o CL by
12%, 13.2%, 11.6% on three datasets w.r.t. Precision@50,
respectively, which demonstrates the contrastive-based module
is crucially important to ADVANCE. The attribute reconstruction component and structure reconstruction component
reconstruct the node attributes and topology structure of the
original graph, respectively, so as to identify the anomalies
in the network from multiple perspectives. According to the
experimental results, the importance of attribute reconstruction
and structure reconstruction in detecting anomalies is different for different attributed networks. For BlogCatalog and
Flickr datasets, the node attributes contribute more to finding
anomalous nodes, while for Cora dataset, paying attention to
topology structure is more conducive to detecting anomalies
in attributed networks.
VI. C ONCLUSION
In this paper, we propose a novel anomaly detection framework based on graph contrastive learning, namely ADVANCE,
which is consisted of two modules: graph contrastive learning module and network reconstruction module. ADVANCE
innovatively constructs the target view and learnable selfenhanced view and takes advantage of the graph contrastive
learning method to maximize the consistency between the
target view and learnable view, which captures network
information related to anomalies without the guidance of
external information (i.e., labels). Next, the node attributes
and topology structure of the original attributed networks
are reconstructed by the network reconstruction module.
Finally, two complementary modules are jointly trained to
achieve more effective anomaly detection. A series of experiments on three benchmark datasets prove the effectiveness of
ADVANCE. The proposed ADVANCE framework facilitates
the early detection of fraudulent users and illicit financial
transaction activities within consumer electronic networks,
thereby furnishing consumer electronics with a dependable
security assurance.
R EFERENCES
[1] W. Hamidouche, F. Pescador, T. Biatek, and E. François, “Editorial realtime implementation of VVC standard for consumer electronic devices,”
IEEE Trans. Consum. Electron., vol. 68, no. 2, pp. 93–95, May 2022.

4071

[2] M. Ku. JYV, A. K. Swain, K. Mahapatra, and S. P. Mohanty,
“Fortified-NoC: A robust approach for trojan-resilient network-on-chips
to fortify multicore-based consumer electronics,” IEEE Trans. Consumer
Electron., vol. 68, no. 1, pp. 57–68, Feb. 2022.
[3] Z. Kahleifeh, H. Thapliyal, and S. M. Alam, “Adiabatic/MTJ-based
physically Unclonable function for consumer electronics security,” IEEE
Trans. Consumer Electron., vol. 69, no. 1, pp. 1–8, Feb. 2023.
[4] V. S. Baghel and S. Prakash, “Generation of secure fingerprint template
using DFT for consumer electronics devices,” IEEE Trans. Consum.
Electron., vol. 69, no. 2, pp. 118–127, May 2023.
[5] X. Zhou et al., “Decentralized P2P federated learning for privacypreserving and resilient mobile robotic systems,” IEEE Wireless
Commun., vol. 30, no. 2, pp. 82–89, Apr. 2023.
[6] M. Kargar, M. Zihayat, and J. Szlichta, “Mining and exploration
of attributed graphs: Theory and applications,” in Proc. CCASCON,
Markham, ON, Canada, 2019, pp. 397–398.
[7] Z. Zang, S. Li, D. Wu, J. Guo, Y. Xu, and S. Z. Li, “Deep manifold
embedding of attributed graphs,” Neurocomputing, vol. 514, pp. 83–93,
Dec. 2022.
[8] S. Zhao, Z. Du, J. Chen, Y. Zhang, J. Tang, and P. S. Yu, “Hierarchical
representation learning for attributed networks,” IEEE Trans. Knowl.
Data Eng., vol. 35, no. 3, pp. 2641–2656, Mar. 2023.
[9] T. Qiu, X. Liu, X. Zhou, W. Qu, Z. Ning, and C. L. P. Chen, “An adaptive
social spammer detection model with semi-supervised broad learning,” IEEE Trans. Knowl. Data Eng., vol. 34, no. 10, pp. 4622–4635,
Oct. 2022.
[10] R. Ghanem and H. Erbay, “Spam detection on social networks using
deep contextualized word representation,” Multimedia Tools Appl.,
vol. 82, no. 3, pp. 3697–3712, 2023.
[11] A. Singh, A. Jain, and S. E. Biable, “Financial fraud detection
approach based on firefly optimization algorithm and support vector
machine,” Appl. Comput. Intell. Soft Comput., vol. 2022, Jun. 2022,
Art. no. 1468015.
[12] M. Y. Turaba, M. Hasan, N. I. Khan, and H. A. Rahman, “Fraud
detection during financial transactions using machine learning and deep
learning techniques,” in Proc. CCCI, Dalian, China, 2022, pp. 1–8.
[13] R. Desai and V. T. Gopalakrishnan, “Network intrusion detection through
machine learning with efficient feature selection,” in Proc. COMSNETS,
Bengaluru, India, 2022, pp. 797–801.
[14] H. Alavizadeh, H. Alavizadeh, and J. Jang-Jaccard, “Deep Q-learning
based reinforcement learning approach for network intrusion detection,”
Comput., vol. 11, no. 3, p. 41, 2022.
[15] X. Zhou, W. Liang, W. Li, K. Yan, S. Shimizu, and K. Wang,
“Hierarchical adversarial attacks against graph-neural-network-based
IoT network intrusion detection system,” IEEE Internet Things J., vol. 9,
no. 12, pp. 9310–9319, Jun. 2022.
[16] Z. Peng, M. Luo, J. Li, H. Liu, and Q. Zheng, “ANOMALOUS: A joint
modeling approach for anomaly detection on attributed networks,” in
Proc. IJCAI, Stockholm, Sweden, 2018, pp. 3513–3519.
[17] B. Perozzi, L. Akoglu, P. I. Sánchez, and E. Müller, “Focused clustering
and outlier detection in large attributed graphs,” in Proc. CKDD,
New York, NY, USA, 2014, pp. 1346–1355.
[18] B. Perozzi and L. Akoglu, “Scalable anomaly ranking of attributed
neighborhoods,” in Proc. SDM, Miami, Florida, USA, 2016,
pp. 207–215.
[19] J. Li, H. Dani, X. Hu, and H. Liu, “Radar: Residual Analysis for
anomaly detection in attributed networks,” in Proc. IJCAI, Melbourne,
VIC, Australia, 2017, pp. 2152–2158.
[20] E. Lughofer et al., “On-line anomaly detection with advanced independent component analysis of multi-variate residual signals from causal
relation networks,” Inf. Sci., vol. 537, pp. 425–451, Oct. 2020.
[21] J. Liang, P. Jacobs, J. Sun, and S. Parthasarathy, “Semi-supervised
embedding in attributed networks with outlier,” in Proc. SDM,
San Diego, CA, USA, 2018, pp. 153–161.
[22] W. Chu and K. M. Kitani, “Neural batch sampling with reinforcement learning for semi-supervised anomaly detection,” in Proc. ECCV,
Glasgow, U.K., 2020, pp. 751–766.
[23] A. Kumagai, T. Iwata, and Y. Fujiwara, “Semi-supervised anomaly
detection on attributed graphs,” in Proc. IJCNN, Shenzhen, China, 2021,
pp. 1–8.
[24] L. Zhang, X. Xie, K. Xiao, W. Bai, K. Liu, and P. Dong, “MANomaly:
Mutual adversarial networks for semi-supervised anomaly detection,”
Inf. Sci., vol. 611, pp. 65–80, Sep. 2022.
[25] K. Ding, J. Li, R. Bhanushali, and H. Liu, “Deep anomaly detection
on attributed networks,” in Proc. SDM, Calgary, AB, Canada, 2019,
pp. 594–602.

4072

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

[26] P. Kavehzadeh, M. Samadi, and M. A. Haeri, “Unsupervised anomaly
detection on node attributed networks: A deep learning approach,” in
Proc. ICISS, Edinburgh, U.K., 2021, pp. 35–40.
[27] M. Jin, Y. Liu, Y. Zheng, L. Chi, Y. F. Li, and S. Pan, “ANEMONE:
Graph anomaly detection with multi-scale contrastive learning,” in Proc.
CIKM, 2021, pp. 3122–3126.
[28] Y. Liu, Z. Li, S. Pan, C. Gong, C. Zhou, and G. Karypis,
“Anomaly detection on attributed networks via contrastive selfsupervised learning,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33,
no. 6, pp. 2378–2392, Jun. 2022.
[29] K. Hassani and A. H. K. Ahmadi, “Contrastive multi-view representation
learning on graphs,” in Proc. ICML, 2020, pp. 4116–4126.
[30] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A survey,”
ACM Comput. Surv., vol. 41, no. 3, pp. 1–58, 2009.
[31] T. Pourhabibi, K. L. Ong, B. Kam, and Y. L. Boo, “Fraud detection: A systematic literature review of graph-based anomaly detection
approaches,” Decis. Support Syst., vol. 133, Jun. 2020, Art. no. 113303.
[32] N. Li, H. Sun, K. C. Chipman, J. George, and X. Yan, “A probabilistic
approach to uncovering attributed graph anomalies,” in Proc. SDM,
Philadelphia, PA, USA, 2014, pp. 82–90.
[33] D. Eswaran, C. Faloutsos, S. Guha, and N. Mishra, “SpotLight:
Detecting anomalies in streaming graphs,” in Proc. KDD, London, U.K.,
2018, pp. 1378–1386.
[34] Y. Pei, T. Huang, W. V. Ipenburg, and M. Pechenizkiy, “ResGCN:
Attention-based deep residual modeling for anomaly detection on
attributed networks,” Mach. Learn., vol. 111, no. 2, pp. 519–541, 2022.
[35] C. Xiao, X. Xu, Y. Lei, K. Zhang, S. Liu, and F. Zhou, “Counterfactual
graph learning for anomaly detection on attributed networks,” IEEE
Trans. Knowl. Data Eng., vol. 35, no. 10, pp. 10540–10553, Oct. 2023.
[36] F. Zhang, H. Fan, R. Wang, Z. Li, and T. Liang, “Deep dual support
vector data description for anomaly detection on attributed networks,”
Int. J. Intell. Syst., vol. 37, no. 2, pp. 1509–1528, 2022.
[37] R. Fathony, J. Ng, and J. Chen, “Interaction-focused anomaly detection
on bipartite node-and-edge-attributed graphs,” in Proc. IJCNN, Gold
Coast, QLD, Australia, 2023, pp. 1–10.
[38] J. Zhang, S. Wang, and S. Chen, “Reconstruction enhanced multi-view
contrastive learning for anomaly detection on attributed networks,” in
Proc. IJCAI, 2022, pp. 2376–2382.
[39] S. Hu and M. Shao, “Dual perspective contrastive learning based
subgraph anomaly detection on attributed networks,” in Proc. ICANN,
Bristol, U.K., 2022, pp. 481–493.
[40] T. Chen, S. Kornblith, M. Norouzi, and G. E. Hinton, “A simple
framework for contrastive learning of visual representations,” in Proc.
ICML, 2020, pp. 1597–1607.
[41] Y. Hua, X. Shu, Z. Wang, and L. Zhang, “Uncertainty-guided voxel-level
supervised contrastive learning for semi-supervised medical image segmentation,” Int. J. Neural Syst., vol. 32, no. 4, 2022, Art. no. 2250016.
[42] C. Mavromatis and G. Karypis, “Graph InfoClust: Maximizing
coarse-grain mutual information in graphs,” in Proc. PAKDD, 2021,
pp. 541–553.
[43] L. Yu et al., “SAIL: Self-augmented graph contrastive learning,” in Proc.
AAAI, 2022, pp. 8927–8935.
[44] Y. Liu, Y. Zheng, D. Zhang, H. Chen, H. Peng, and S. Pan, “Towards
unsupervised deep graph structure learning,” in Proc. WWW, Lyon,
France, 2022, pp. 1392–1403.
[45] H. Zhang et al., “DCML: Deep contrastive mutual learning for COVID19 recognition,” Biomed. Signal Process. Control., vol. 77, Aug. 2022,
Art. no. 103770.
[46] X. Liu, C. Song, F. Huang, H. Fu, W. Xiao, and W. Zhang, “GraphCDR:
A graph neural network method with contrastive learning for cancer drug
response prediction,” Brief. Bioinform., vol. 23, no. 1, pp. 1–9, 2022.
[47] M. Chen, W. Zhang, Z. Yuan, Y. Jia, and H. Chen, “Federated knowledge
graph completion via embedding-contrastive learning,” Knowl. Based
Syst., vol. 252, Sep. 2022, Art. no. 109459.
[48] X. Zhou et al., “Hierarchical federated learning with social context clustering-based participant selection for Internet of Medical
Things applications,” IEEE Trans. Comput. Soc. Syst., vol. 10, no. 4,
pp. 1742–1751, Aug. 2023.
[49] Y. Yang, C. Huang, L. Xia, and C. Li, “Knowledge graph contrastive
learning for recommendation,” in Proc. SIGIR, Madrid, Spain, 2022,
pp. 1434–1443.
[50] M. Chen, C. Huang, L. Xia, W. Wei, Y. Xu, and R. Luo, “Heterogeneous
graph contrastive learning for recommendation,” in Proc. WSDM,
Singapore, 2023, pp. 544–552.
[51] Y. Ma et al., “Enhancing recommendations with contrastive learning from collaborative knowledge graph,” Neurocomputing, vol. 523,
pp. 103–115, Feb. 2023.

[52] T. N. Kipf and M. Welling, “Semi-supervised classification with graph
convolutional networks,” in Proc. ICLR, Toulon, France, 2017.
[53] K. Ding, J. Li, and H. Liu, “Interactive anomaly detection on
attributed networks,” in Proc. WSDM, Melbourne, VIC, Australia, 2019,
pp. 357–365.
[54] D. B. Skillicorn, “Detecting anomalies in graphs,” in Proc. ISI, New
Brunswick, NJ, USA, 2007, pp. 209–216.
[55] D. Zhu, Y. Ma, and Y. Liu, “Anomaly detection with deep graph
autoencoders on attributed networks,” in Proc. ISCC, Rennes, France,
2020, pp. 1–6.
[56] J. Gan, R. Hu, M. Zhan, Y. Mo, Y. Wan, and X. Zhu, “Multi-view
unsupervised graph representation learning,” in Proc. IJCAI, 2022,
pp. 2987–2993.
[57] P. Velickovic, W. Fedus, W. L. Hamilton, P. Liò, Y. Bengio, and
R. D. Hjelm, “Deep graph infomax,” in Proc. ICLR, New Orleans, LA,
USA, 2019.
[58] Z. Peng et al., “Graph representation learning via graphical mutual
information maximization,” in Proc. WWW, Taipei, Taiwan, 2020,
pp. 259–270.
Bo Xu (Member, IEEE) received the B.Sc. and Ph.D.
degrees from the Dalian University of Technology,
China, in 2007 and 2014, respectively, where she
is currently an Associate Professor with the School
of Software. Her current research interests include
social computing, data mining, information retrieval,
and natural language processing.

Jinpeng Wang received the B.Sc. degree in software engineering from the Dalian University of
Technology, China, in 2021, where he is currently
working the master’s degree with the School of
Software. His research interests include data science,
social computing, and graph learning.

Zhehuan Zhao (Member, IEEE) received the B.Sc.
and Ph.D. degrees from the Dalian University of
Technology, China, in 2010 and 2017, respectively,
where he is currently an Associate Professor with
the School of Software. His current research interests
include knowledge graph, data mining, and natural
language processing.

Hongfei Lin received the M.S. degree from the
Dalian University of Technology, China, in 1992,
and the Ph.D. degree from Northeastern University,
China, in 2000. He is currently a Professor with
the College of Computer Science and Technology,
Dalian University of Technology. He has published
over 100 research papers in various journals, conferences, and books. His research interest includes
text mining for biomedical literatures, biomedical
hypothesis generation, information extraction from
huge biomedical resources, sentimental analysis, and
opinion mining.
Feng Xia (Senior Member, IEEE) received the
B.Sc. and Ph.D. degrees from Zhejiang University,
Hangzhou, China. He is a Professor with the School
of Computing Technologies, RMIT University,
Australia. He has published over 300 scientific
papers in international journals and conferences
(such as IEEE TAI, TKDE, TNNLS, TC, TMC,
TPDS, TBD, TCSS, TNSE, TETCI, TETC, THMS,
TVT, TITS, TASE, ACM TKDD, TIST, TWEB,
TOMM, WWW, AAAI, SIGIR, WSDM, CIKM,
JCDL, EMNLP, and INFOCOM). His research
interests include data science, artificial intelligence, graph learning, digital
health, and systems engineering. He is a Senior Member of ACM, and an
ACM Distinguished Speaker.
PAPER_TEXT
