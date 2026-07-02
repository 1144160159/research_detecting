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
# [230] Fusion Graph Structure Learning-Based Multivariate Time Series Anomaly Detection With Structured Prior Knowledge
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
编号：230
题名：Fusion Graph Structure Learning-Based Multivariate Time Series Anomaly Detection With Structured Prior Knowledge
年份：2024
DOI：10.1109/tifs.2024.3459631
来源：IEEE Transactions on Information Forensics and Security
PDF：paper/10.1109_TIFS.2024.3459631.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：图学习、知识图谱与威胁情报、入侵检测与网络异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\230.txt
- 原始字符数：59728
- 本次发送字符数：59728
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
8760

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

Fusion Graph Structure Learning-Based Multivariate
Time Series Anomaly Detection With Structured
Prior Knowledge
Shiming He , Genxin Li , Kun Xie , Member, IEEE, and Pradip Kumar Sharma , Senior Member, IEEE
Abstract— Multivariate time series anomaly detection
(MTSAD) plays a crucial role in the Internet of Things (IoT)
to identify device malfunction or system attacks. Graph neural
networks (GNN) are widely applied in MTSAD to capture
the spatial features among sensors. However, GNNs depend
on a graph structure and explicit graph structures are not
always available. To solve the problem of missing explicit graph
structure, graph structure learning is introduced to learn an
accurate graph structure joint with a GNNs-based anomaly
detection task. However, the existing GSL-based methods provide
only a partial view of the graph structure and cannot represent
multiple and complex relationships. The noise of data also brings
noisy edges. Therefore, we propose a fusion graph structure
learning-based multivariate time-series anomaly detection with
structured prior knowledge (FuGLAD). To the best of our
knowledge, it appears to be the first application of fusion graphs
in time series anomaly detection. FuGLAD selects three kinds of
typical graph structure learners to learn as many relationship
types among sensors as possible and exploits the prior similarity
to evaluate the importance of all learned graphs and adaptively
learn the fusion weight instead of the direct average weight.
To handle noise in raw data, FuGLAD compares the neighbors
of nodes by Jaccard similarity to identify and remove the noisy
edges in the prior graph. Extensive experiments demonstrate
that our approach outperforms state-of-the-art single-graph
structure learning techniques in detection performance across
four public and real-world datasets.
Index Terms— Multivariate time series, anomaly detection,
graph structure learning, fusion graph.

Received 3 January 2024; revised 6 August 2024; accepted 3 September
2024. Date of publication 12 September 2024; date of current version
30 September 2024. This work was supported in part by the National Natural
Science Foundation of China under Grant 62272062 and Grant 62025201; in
part by the Science and Technology Innovation Program of Hunan Province
under Grant 2023RC3139; in part by the Scientific Research Fund of Hunan
Provincial Transportation Department under Grant 202143; and in part by
the Open Fund of Key Laboratory of Safety Control of Bridge Engineering,
Ministry of Education (Changsha University of Science and Technology),
under Grant 21KB07. The associate editor coordinating the review of this
article and approving it for publication was Prof. Kun Sun. (Corresponding
author: Kun Xie.)
Shiming He and Genxin Li are with the School of Computer and Communication Engineering and Hunan Provincial Key Laboratory of Intelligent
Processing of Big Data on Transportation, Changsha University of Science
and Technology, Changsha 410114, China (e-mail: smhe_cs@csust.edu.cn;
22108031619@stu.csust.edu.cn).
Kun Xie is with the College of Computer Science and Electronics Engineering, Ministry of Education Key Laboratory of Fusion Computing of
Supercomputing and Artificial Intelligence, Hunan University, Changsha
410082, China (e-mail: xiekun@hnu.edu.cn).
Pradip Kumar Sharma is with the Department of Computing Science,
University of Aberdeen, AB24 3UE Aberdeen, U.K. (e-mail: Pradip.sharma@
abdn.ac.uk).
Digital Object Identifier 10.1109/TIFS.2024.3459631

I. I NTRODUCTION

I

N THE Internet of Things (IoT), more and more critical
infrastructures are being deployed by various sensors. The
data generated by these multiple sensors is known as multivariate time series data (MTS). When abnormal changes occur
in the MTS, it indicates that the equipment has failed or
the system is under attack. If the anomaly is not discovered
and dealt with in time, the whole system may fail and lead
to economic losses [1]. Therefore, multivariate time series
anomaly detection (MTSAD) stands as a crucial undertaking
within the domain of IoT [2]. In the IoT, sensors rely on
and interact with each other. Therefore, when conducting
MTSAD, it is crucial to understand both the temporal relationships of individual indicators1 and the interrelationships
among these indicators. In recent years, graph neural networks
(GNNs) have been introduced into the field of multivariate
time series anomaly detection for modeling the relationships
among indicators. Existing GNNs-based anomaly detection
methods, such as the Arvalus and its variant D-Arvalus [3]
utilize a fixed graph structure constructed from domain expert
knowledge for modeling the relationships among indicators.
However, explicit graph structures are not always available
in every application. Therefore, how to define an accurate
graph structure becomes a key task for GNNs-based anomaly
detection.
As a result, graph structure learning (GSL) has arisen in
MTSAD [4], [5], [6]. It learns an optimal graph structure in
conjunction with the subsequent downstream anomaly detection task. Fig. 1 shows the GSL-based anomaly detection
process. However, GSL-based methods still face several challenges.
• Existing methods provide only a partial view of the
graph structure, which cannot represent the multiple
and complex relationships that exist between indicators. The existing graph structure learning methods
can be classified into three categories [7]: metric-based,
neural network-based, and direct methods. The current
GSL-based anomaly detection methods all solely adopt
one of these three methods to learn a partial view of the
graph structure. The ideal graph structure is not always
available or may be incomplete due to the difficulty
in obtaining such information or deliberate shielding to
1 Here, “indicator” signifies the time series of a particular variable.

1556-6021 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

HE et al.: FUSION GRAPH STRUCTURE LEARNING-BASED MTSAD WITH STRUCTURED PRIOR KNOWLEDGE

8761

In basic graph structure learner selection, to learn as many
relationship types among sensors as possible, we choose
three graph structure learning methods that have been
widely proven to be effective. K -Nearest Neighbour
method is for the association, causal graph learning is
for causality, and the fully parameterized method treats all
elements in the adjacency matrix as independent variables
which is the replenishment of the two former.
• In graph fusion, we propose a prior similarity-based
weighted fusion method (PSF) instead of average fusion
since a prior graph (such as a kNN graph derived from
data) still serves as reasonable knowledge [8]. It exploits
the cosine similarity between the prior graph and the
learning graph to evaluate the importance of all learned
graphs and adaptively learn the fusion weight, rather than
simply taking the average of the learned graphs.
• To handle noise in raw data, we design a structured prior
graph (SPG) generator to construct a prior graph in the
structured space. SPG compares the neighbors of nodes
by Jaccard similarity to identify and remove the noise
edges in the prior graph.
• Extensive experiments on four public and real-world
datasets are conducted to evaluate the performance of
FuGLAD. Compared to the thirteen baseline methods,
FuGLAD consistently has the highest F1 score.
The following sections of this paper are organized as
follows: Section II reviews the related work. Section III covers
preliminary knowledge and problem definition. Section V
details the FuGLAD approach. Section VI discusses performance evaluation through experiments. Finally, Section VII
summarizes the findings and explores future work.
•

Fig. 1. A framework for anomaly detection based on graph structure learning.

protect sensitive information [8]. The learned graph
structure is only an estimate of the ideal graph and only
represents the relationships from a single view, which
inevitably has a certain degree of information loss or
misconnection [9].
i) The metric-based approach only focuses on the similarity relationship. It establishes connections between
nodes with higher similarity of node embedding vector to form edges. However, the relationships between
nodes still include causality and distance except for
similarity. ii) Neural network-based graph learning
methods depend on the type of neural network. If
simple linear neural networks are used, learned graph
structure learning may not yield satisfactory results. Conversely, complex neural network structures increase the
training cost of the model.
iii) The direct approach offers great flexibility as it
does not rely solely on node representation. It treats
the adjacency matrix of the target graph as a free variable
for learning. Nonetheless, in many practical applications,
node features are equally crucial for comprehending and
predicting the behavior of sensors.
• Noise in the raw data can affect the quality of the prior
graph. To constrain the learning of graph structure, some
prior information is usually added to the graph learning
process. Existing methods usually utilize the original
data to generate a K -nearest Neighbors (KNN) graph
as prior information, termed a prior graph. However,
there is usually noise in the raw data resulting in an
inevitable presence of uncertain, redundant, incorrect, and
incomplete connections within the prior graph, termed
noisy edges. Such noisy information in the prior may
damage the performance of GNNs.
To address these challenges, we propose FuGLAD, a technique that fuses multiple graph structures to refine the quality
of the learning graph and uses the structured prior graph to
eliminate the effects of noise in the original data. To the best
of our knowledge, this is the first work to apply fusion graphs
in time series anomaly detection. Our major contributions can
be summarized as follows:
• To address the single view representation of individual
graph structures, we propose a fusion graph structure
learning method that merges various graph structures
to mine multiple view relationships between sensors.
It consists of two key steps: the basic graph structure
learner selection and graph fusion.

II. R ELATED W ORK
A. Temporal Feature-Based Anomaly Detection Method
LSTM is widely used in multivariate time series anomaly
detection because of its ability to process sequence data.
LSTM-NDT [10] utilizes LSTM for accurate predictions while
maintaining the interpretability of the whole system. A nonparametric, dynamic, and unsupervised threshold method
is provided to detect anomalies. MSCRED [11] constructs
a multi-scale feature matrix and uses conv-LSTM neural
networks to encode the correlation between sensors and reconstruct the multi-scale feature matrix. The residual feature
matrix helps to detect and diagnose anomalies. MAD-GAN
[12] employs LSTM as the foundational model within the
GAN framework, capturing the temporal correlation of time
series, extracting potential interactions, and detecting anomalies by discrimination and reconstruction. LSTM-VAE [13]
introduces the multi-modal observation and time dependence
into the potential space, reconstructs the expected distribution, and evaluates the anomalies based on the reconstructed
anomaly scores. OmniAnomaly [14] utilizes a stochastic
recurrent neural network to capture the robust representation
of normal patterns and reconstruct observations. DAGMM
[15] utilizes depth self-coding and Gaussian mixture model
to obtain low-dimensional representation and exploit reconstruction errors to detect anomalies. CAE-M [16] employs a

8762

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

Convolutional Autoencoding Memory Network to effectively
handle time series data. By utilizing a Convolutional Neural
Network (CNN), CAE-M efficiently processes the input time
series. The resulting output of CNN is then subjected to a
bi-directional Long LSTM network, enabling the model to
effectively capture and analyze long-term time trends.
Although LSTM networks have demonstrated promising
results in modeling the temporal dependencies of MTS, they
are unable to directly capture the correlations between different
indicators [17].

intraspinal correlations, while GSLAD [24] uses a diffusion
convolutional recurrent neural network for anomaly detection.
Although anomaly detection methods based on graph learning are able to adaptively generate a suitable graph structure
for the downstream task through backpropagation, it is important to note that current approaches solely produce a partial
view of the graph structure, consequently leading to the
unavoidable loss of information.
III. P ROBLEM D EFINITION AND P RELIMINARIES
A. Multivariate Time Series

B. Graph-Based Anomaly Detection Method
Recent studies have demonstrated the effectiveness of graph
neural networks in predicting temporal dependencies and modeling correlations between indicators. For example, MTAD-TF
[18] uses multi-scale convolution and graph attention networks
to capture temporal pattern information. Similarly, MTADGAT [19] employs two parallel graph attention layers to model
both temporal features and correlations between indicators,
which are then passed to a lightweight Gated Recurrent
Unit (GRU) network. Additionally, Arvalus and its variant
D-Arvalus [3] represent system components as nodes and
their dependencies and locations as edges to improve anomaly
identification and localization.
Although graph neural network-based anomaly detection
methods have effectively modeled time-series correlations
between indicators, they still have some limitations. Most of
the existing graph neural network-based anomaly detection
methods [3], [18], [19] assume that the relationship between
indicators is known or assume there is a relationship between
any two indicators, which increases computational overhead
with increasing dimensionality [20].
C. Graph Structure Learning-Based Anomaly Detection
Method
To address MTSAD without a predefined graph structure,
Graph Structure Learning-based methods have been developed. For example, GDN [4] generates an embedding vector
for each node and settles to compute the similarity between the
embedding vectors between any two nodes, and subsequently
selects the top k nodes with the highest similarity to form the
graph. This graph is then used by a graph attention network to
forecast future sensor behavior. FuSAGNet [5] categorizes the
sensor nodes by function and recursively encodes the nodes in
each category. Subsequently, it uses the resulting embeddings
to compute the similarity between the nodes and selects the
top k nodes with the highest similarity to form the graph.
ACGSL [21] generates dynamic graphs for each subsequence
by minimizing differences between consecutive ones.
GTA [6] treats adjacency matrix elements as learnable
parameters and uses a Transformer-based model to automatically learn the graph structure and temporal dependencies.
GLAD [22] combines GAT and Transformer to extract
global and local features for anomaly detection. MGCLAD
[23] employs two directed graphs to learn intersignal and

Multivariate time series can be described as X = (x 1 , x 2 ,
. . . , x N )T ∈ R K ×N , where K represents the number of
indicators and N signifies the number of timestamps. The
values of i-th indicator are represented as x i = (x1i , x2i ,
i ). The values at timestamp t are represented as
. . . , xN
x t = (xt1 , xt2 , . . . , xtK )T . A history window of length ω at
timestamp t is defined as the subsequence X t = (x t−ω ,
x t−ω+1 , . . . , x t−1 )T ∈ R K ×ω .
B. Graph Structure Learning in MTS
Given the time series X ∈ R K ×N , graph structure learning
aims to construct a graph G = (V, E) and its adjacency
matrix A ∈ R K ×K . In this graph, the nodes v represent
the sensors that produce the indicators, while the edges E
denote the hidden relationships between these sensors. The
adjacency matrix A stores the edge information, which reflects
the underlying dependencies among the indicators.
C. GSL-Based Multivariate Time Series Anomaly Detection
Multivariate time series anomaly detection calculates an
anomaly score for each timestamp, denoted as st , according
to the historical subsequence X t and the adjacency matrix A
generated by GSL. An anomaly is deemed to have transpired at
timestamp t if the anomaly score st surpasses a predetermined
threshold. The process is shown as follows:
A = G S L(X )

(1)

x̂t = f (X t , A)

(2)

st = ϕ(xt , x̂t )
(
1, if st > T
ŷt =
0, if st ≤ T

(3)
(4)

where f () denotes the prediction function, x̂t represents the
forecasted value of xt at timestamp t, ϕ is the function used
to calculate the anomaly score, and T stands for the threshold.
IV. M OTIVATION
The current graph neural network-based anomaly detection
methods are all based on a partial view of the graph structure [25]. In the world, objects might form different kinds of
relationships with others (e.g., sensor distance and data semantic relationship on IoT). This results in multi-view graphs that
contain more than one type of edge between two nodes [26],
[27]. Therefore, anomaly detection can be performed using

HE et al.: FUSION GRAPH STRUCTURE LEARNING-BASED MTSAD WITH STRUCTURED PRIOR KNOWLEDGE

8763

Fig. 2. The FuGLAD framework includes three primary modules. The first module, illustrated in blue, captures the relationships between indicators. The
second module, in gold, generates a structured prior graph that aids the graph structure learner with prior information. The third module, in green, uses a
DCRNN predictor to produce precise indicator forecasts.

a multi-view approach, where multiple views allow us to
analyze the characteristics of a physical object from different
perspectives. Each view can offer complementary information
to the other views. For example, an anomaly may not be
identifiable in one view but can be in another. There exists
a plethora of research in data mining focusing on multi-view
learning [28], [29]. However, multi-view learning for anomaly
detection is still in its infancy. For this reason, we propose a multi-graph structure learning method for anomaly
detection.
Although multiple views contain rich information, there
may be inconsistencies among them. Digesting the relationship between views is crucial for the success of multi-graph
learning algorithms, as two views may provide opposite/complementary information for anomaly detection [25].
To this end, we propose a fusion approach based on a priori
graph. The constraints of a priori graph make the learned
graphs as close as possible without generating opposite

information and not the same to provide complementary
information for each other.
V. P ROPOSED M ETHODOLOGY
A. Overview
To address the single-view representation of individual
graph structures, we propose FuGLAD, which fuses multiple
basic learned graph structures to accurately represent relationships. Fig. 2 shows the framework of FuGLAD. It primarily
consists of three main components:
• Structured Prior Graph Generator: It acquires a
structured prior graph from noise data that offers prior
information for graph learning.
• Fusion Graph Structure Learner: It utilizes three
mainstream graph structure learners to generate multiple
graphs and fuse them to characterize complex relationships among sensors.

8764

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

TABLE I
L IST OF N OTATIONS

It goes beyond the direct connection between two nodes and
takes into account their position in the entire space and their
relationships with other nodes. Nodes with a greater number
of common neighbors display higher similarity. Consequently,
the presence of a noisy edge can be alleviated by tallying the
count of common neighbors, as long as this noisy edge is not
shared among multiple nodes, which is typically unlikely.
We calculate the Jaccard similarity among nodes on the
KNN graph and generate a structured graph by selecting
the top-k nodes with the highest Jaccard similarity for each
node as its neighbor. This process effectively transforms
the traditional KNN graph into a structured space. In the
structure space, the features have the capability to encode a
greater amount of texture information by perceiving the data
distribution thus being more robust [32].
Initially, we construct a feature extractor for characterizing
the behavior of each sensor as follows:
(t)

Vi

(t)

= FC(Conv(Conv(xi )))

(5)

(t)

DCRNN Predictor and Anomaly Score: It utilizes
the diffusion convolutional recurrent neural network
(DCRNN) for predicting the future values of each sensor and calculates the anomaly score by the difference
between the prediction and ground truth.
The process of FuGLAD can be summarized as follows:
Firstly, the fusion graph structure learner learns multiple basic
graph structures and fuses them to obtain a fused adjacency
matrix A. Secondly, based on the fused adjacency matrix A,
a DCRNN predictor predicts the value x̂ t of the t-th timestamp
from the historical observations x t−w , . . . , x t−1 . Then, the
basic graph structures are jointly trained with the prediction
task, and the normalized prediction error between the predicted
value x̂ t and the ground truth x t is treated as the anomaly
score. Finally, a grid search algorithm is used to select a
threshold for best detection accuracy. Once the anomaly score
at timestamp t exceeds the threshold, timestamp t is taken
as an anomaly. The notation employed here is outlined in
Table I.
•

B. Structured Prior Graph Generator
Using prior graphs extracted from raw data as a guide
is an effective and widely applied approach to constrain
the direction during the training of graph structure learning,
ensuring the quality of the learned graph [8], [30]. Many
prior graph generation methods extract node features from
the raw data. The features are then utilized to compute a
K -Nearest Neighbor (KNN) graph, which serves as the prior
knowledge for the learned graph. Nevertheless, the presence
of noise in the data may corrupt the node feature vectors,
resulting in an inevitable presence of uncertain, redundant,
incorrect, and incomplete connections within the prior graph,
termed noisy edges. To reduce the noisy edges, inspired
by the common-neighbor-based metric [31], we propose a
structured prior graph generator based on Jaccard similarity.
Jaccard similarity compares the common neighbors between
nodes, enabling the consideration of a broader spatial structure.

where xi ∈ R w represents the subsequence for sensor i at
(t)
timestamp t, Vi denotes the feature vector of sensor i at
timestamp t, Conv refers to the one-dimensional convolutional
layer, and FC refers to the fully connected layer.
Subsequently, the cosine similarity is computed for the
feature vectors of every node pair as follows:
(t)
(t)
cos(Vi , V j ) =

(t)

(t)

Vi • V j
(t)

(6)

(t)

||V i || • ||V j ||

where ∥ · ∥ denotes magnitude. Afterward, the top-k nodes
with the highest similarity are selected as the neighbors of
Ni , noted as ν (t) (Ni , k) = {Ni,1 , Ni,2 , . . . , Ni,k }. It generate a
(t)
KNN graph θ K N N .
Finally, we compute the Jaccard similarity of the node pair
on the KNN graph to compare the common-neighbor. The k
nodes with the highest Jaccard similarity are designated as
the neighbors of node Ni to generate a structured graph as
follows:
|ν(Ni , k) ∩ ν(N j , k)|
S J ac (ν(Ni , k), ν(N j , k)) =
(7)
|ν(Ni , k) ∪ ν(N j , k)|
(t)

θi j = 1, j ∈ topk(S J ac (ν(Ni , k), ν(N j , k)))
(t)

(8)

where S J ac represents the Jaccard similarity, θi j denotes the
element in the i-th row and j-th column of the prior graph,
and topk(·) function extracts the top k values, enabling focus
on the most relevant data points based on the specified criteria.
[4].
We take an example to illuminate how Jaccard similarity
removes the noisy edge. As shown in Fig. 3, there are nine
nodes, and Ci represents the neighbor set of node i. The
edge between nodes 2 and 3 is a noisy edge (marked in red).
According to Eq. (7), we can obtain the Jaccard similarity of
C1∩C2
2
nodes 1 and 2, which is S J ac (C1, C2) = C1∪C2
= 2+2+3
=
0.286. Similarly, the Jaccard similarity of node 2 and 3 is
3
J ac (C2, C3) is
S J ac (C2, C3) = C2∩C3
C2∪C3 = 1+3+2 = 0.5. S
J
ac
smaller than S (C1, C2). When selecting the top-k neighbors, node 2 prioritizes choosing node 1 as a neighbor over

HE et al.: FUSION GRAPH STRUCTURE LEARNING-BASED MTSAD WITH STRUCTURED PRIOR KNOWLEDGE

8765

where ∥ · ∥ denotes the magnitude, and topk(·) extracts the
top k values, enabling focus on the most relevant data points
based on the specified criteria [4].
b) Causal graph learning (CGL) method: Among the
neural network-based graph learning methods, we select a
unidirectional graph structure learning method that can model
causal relationships between sensors [33]. It defines a source
and a destination node embedding for each node and generates
the second adjacency matrix A2 . It is referred to as CGL,
whose procedure is shown as follows:

Fig. 3. A simple example of eliminating the noisy edge by the Jaccard
similarity.

M1 = tanh(α E 1 β1 )

(11)

M2 = tanh(α E 2 β2 )

(12)

A2 = ReLU(tanh(α(M1 M2T − M2 M1T )))

(13)

for i = 1, 2, . . . , K :
(i,:)

id x = arg topk(A2 )

node 3. Consequently, by doing so, we can eliminate the noisy
edge (2, 3) and obtain the correct edge (1, 2).

C. Fusion Graph Structure Learner
In graph structure learning-based anomaly detection, the
ideal graph structure is not always available or may be
incomplete. The currently given adjacency matrix is only an
approximation of the ideal graph structure. Consequently, this
approximation leads to a certain extent of information loss.
To address this issue, it is advantageous to have multiple
adjacency matrices that represent various viewpoints of the
graph structure and fusion them for anomaly detection. Therefore, we propose fusion graph structure learning. As shown in
Fig. 2, fusion graph structure learning consists of two main
parts: basic graph structure learners and graph fusion.
1) Basic Graph Structure Leaner: The existing graph
structure learning methods can be classified into three categories [7]: metric-based, neural network-based, and direct
methods. From these three types of methods, we select the
three most representative graph structure learners to individually characterize the relationships between nodes from
different perspectives: K -Nearest neighbor, causal graph learning, and fully parameterized method. K -Nearest neighbor
method is for the association, causal graph learning is for
causality, and the fully parameterized method treats all elements in the adjacency matrix as independent variables which
is the replenishment of the two formers.
a) K neighbor Method (K neighbor): Among the
metric-based graph learning methods, we select the method
based on pairwise cosine similarity [4] for the association.
It defines a node embedding for each node and the top-k
highest cosine similarity nodes are treated as neighbors, which
generates the first adjacency matrix A1 . It is referred to as the
K neighbor, whose procedure is shown as follows:
(t)
(t)
cos(E i , E j ) =
(i, j)

A1

(t)

(t)

Ei • E j
(t)

(t)

(9)

||E i || • ||E j ||
(t)

(t)

= 1, j ∈ topk(cos(E i , E j ))

(10)

(i, j)

A2

= 1,

j ∈ id x

(14)

where E 1 and E 2 denote the source and destination node
embeddings, β1 , β2 are model parameters, α represents the
activation function’s saturation rate, and arg topk(·) returns
the indices of the top-k largest values in a vector.
To reduce the training cost, the CGL method only employs
a single-layer network, while it can be complemented by the
other two graph learning approaches to ensure performance.
c) Fully Parameterized Method (FPM): Among
the direct methods, we select one that employs the
Gumbel-softmax technique to construct the graph structure
[6]. It exploits a probability matrix to generate the third
adjacency matrix A3 . It is referred to as FPM, whose
procedure is shown as follows::
gi = − log(− log(u)), u ∼ Uniform(0, 1)
 

i, j
exp log π1 +g i, j /τ
i, j

 
z1 = P
i, j
exp log πv +g i, j /τ

(15)
(16)

v∈{0,1}

where u represents samples drawn from the Uniform(0,1)
i, j
distribution, g i, j denotes the Gumbel distribution, and π1
is the value in row i and column j of the probability matrix
π1 ∈ R K ×K , indicating the probability that node i is connected
to node j in the graph. The temperature parameter τ controls
i, j
the distribution, with z 1 approaching 0 or 1 as τ approaches 0,
making the Gumbel-Softmax distribution converge to the class
distribution. Finally, the element in row i and column j of the
(i, j)
i, j
third adjacency matrix A3
is set to z 1 , which is 1 with
i, j
probability π1 .
2) Fusion Graph: After generating these three graph structures, the most important step is how to fuse them. The
simplest approach is fusing them by average. However,
it ignores the importance and qualities of all learned graph
structures. Therefore, we propose the prior similarity-based
weighted fusion method to adaptively learn the fusion weight
instead of the direct average weight.
We obtain a quantitative assessment of the similarity
between each learned graph and the prior structured graph
to evaluate the importance. Subsequently, we normalize the

8766

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

importance by softmax to derive probability weights for
learned graphs. Finally, the probability weights are used to
compute a weighted sum of multiple learned graphs to generate a fusion adjacency matrix to characterize the relationship
between sensors.
αi = Softmax(cos(Ai , θ (t) ))
A=

3
X

αi Ai

(17)
(18)

i=1

where cos(A, B) denotes the cosine similarity of A and B.
D. DCRNN Predictor
DCRNN [34] is an exceptional spatio-temporal graph convolutional networks, which can capture the temporal and
spatial features simultaneously. It captures spatial dependencies through diffusion convolution and temporal dependencies
with an encoder-decoder architecture. In the diffusion convolution operation, each node aggregates information from its
neighbors up to L steps away, where L is referred as the
diffusion degree. This operation can be performed in both the
outward and inward directions, meaning that a node can gather
information from its outgoing neighbors (i.e., nodes it points
to) and its incoming neighbors (i.e., nodes that point to it).
Therefore, we utilize DCRNN instead of GCN. The formula
for DCRNN is as follows:



Rt = sigmoid W R ◦ xt ||H(t−1) + b R
(19)



Ct = tanh WC ◦ xt ||(Rt ⊙ H(t−1) ) + bC
(20)



Ut = sigmoid WU ◦ xt ||H(t−1) + bU
(21)
H(t) = Ut ⊙ H(t−1) + (1−Ut ) ⊙ Ct
(22)
l

l 
XL  Q 
Q
−1 T
WQ ◦ Y =
wl,1 D −1
Y
O A + wl,2 D I A
l=0

(23)
where D O and D I are the out-degree matrix and in-degree
matrix, || is concatenation operation, Rt is the reset gate, Ct
Q
Q
is the candidate hidden state, Ut is the update gate, wl,1 , wl,2 ,
b Q are the model parameter, and the diffusion degree L is a
hyperparameter.
The DCRNN-based predictor works as follows. In the
encoder, xt ′ and node feature H(t ′ −1) enter diffusion convolutional lay to get node feature H(t ′ ) at the next timestamp t ′ .
The encoder updates node feature H(·) from timestamp t − w
to timestamp t − 1 and obtains the total node feature H(t−1) of
this subsequence. In the decoder, the total node feature H(t−1)
is the input. After a layer of the decoder model, a hidden
feature and predicted value x̂t at timestamp t are obtained,
as shown in Fig. 2.
E. Loss Function
Firstly, we use the mean absolute error (MAE) loss p
between the prediction and ground truth as the loss function
for the prediction task.
K

loss p =

1 X i
|x̂t − xti |
K
i=1

(24)

where x̂ti and xti represent the predicted value and ground truth
of the i-th indicator at timestamp t, respectively.
Secondly, We utilize the cross-entropy between the prior
graph structure θ (t) and the fusion graph structure A as graph
learning loss to constraints the learning graph during model
training.
X (t)
(t)
lossg =
−θi, j log Ai, j − (1 − θi, j ) log(1 − Ai, j ) (25)
ij

Our aim is to optimize the model’s performance in accurately predicting the indicators and capturing the underlying
relationships among them. We achieve this by balancing
the MAE loss function for the prediction task and the
cross-entropy loss function for the graph learning task. To
mitigate over-fitting, an L 2 regularization term is incorporated
into the loss function. The total loss function of the model is
as follows:
loss = loss p + λ1lossg + λ2 ∥w∥22

(26)

where the parameters λ1 and λ2 is the regularization magnitude.
F. Anomaly Score and Threshold Selection
The purpose of anomaly detection is to identify the abnormal situation that deviates from the normal behavior according
to the ground truth and prediction. Therefore, we first compute
the prediction error Erri (t) of the sensor i at timestamp t
by calculating the difference between ground truth and the
prediction.
Erri (t) = xti − b
xti

(27)

Secondly, we normalize the prediction error and compute
the anomaly score at timestamp t by selecting the highest value
among all sensors.
s(t) = max si (t) = max
i

i

Erri (t) − µi
σi

(28)

where µi and σi are the mean and standard deviation of
Erri (t), respectively.
Grid search is crucial for finding the optimal threshold.
It involves defining the threshold bounds as the maximum and
minimum values of s(t). We exhaustively search all possible
thresholds with a step size of 0.01, selecting the threshold that
yields the highest F1 score. Additionally, we apply a point
adjustment strategy for anomaly scores.
VI. E XPERIMENTS E VALUATION
We thoroughly describe our experiments and address the
following research questions:
• RQ1 (Effectiveness and Efficiency): Does FuGLAD
exceed the baseline methods in both effectiveness and
efficiency?
• RQ2 (Parameter Sensitivity): How sensitive is
FuGLAD to various hyperparameters?
• RQ3 (Structured Prior Graph Performance): Whether
the structured prior graph can effectively handle data with
noise?

HE et al.: FUSION GRAPH STRUCTURE LEARNING-BASED MTSAD WITH STRUCTURED PRIOR KNOWLEDGE

TABLE II
D ETAILED I NFORMATION OF DATASETS

•

C. Baselines

RQ4 (Fusion Graph Structure Learning Performance): Does our proposed fusion graph structure
learning method outperform other single graph structure
learning methods and other fusion methods?

A. Datasets
We use four real-world public datasets, whose detailed
information is shown in Table II.
• Safe Water Treatment (SWAT) Dataset: Collected by
the Singapore Public Utilities Bureau, this dataset spans
11 days with continuous 24-hour monitoring. It includes
network traffic and data from 51 sensors and actuators on
a water treatment test bench.
• Water Distribution (WADI) Dataset: An extension of
the SWAT platform, WADI offers a more comprehensive
view of water treatment, storage, and distribution. It covers 16 days (14 for routine operations and 2 for attack
simulations) using 127 sensors and actuators.
• Mars Science Laboratory Rover (MSL) Dataset:
This dataset from NASA features 55 indicators across
27 unique entities related to the Mars rover’s sensors and
actuators.
• Soil Moisture Active Passive (SMAP) Dataset: Collected by NASA using the Mars probe, this dataset
includes 25 indicators for 55 soil samples and telemetry
data.
In order to handle voluminous raw data, the SWAT and
WADI datasets undergo a down-sampling process every
10 seconds, capturing the median. During this period, once
an anomaly occurs, it is tagged as an anomaly.
B. Evaluation Metrics
We utilize F1-Score (F1), precision (Pre), and recall (Rec)
to evaluate the effectiveness of anomaly detection.
TP
TP + FP
TP
Rec =
TP + FN
2 × Prec × Rec
F1 =
.
Prec + Rec

Prec =

8767

(29)
(30)

The baselines are the following thirteen methods.
• AE: The input data is reconstructed by an autoencoder,
and the resulting reconstruction error is used as the
anomaly score.
• IF [35]: The Isolation Forest algorithm identifies anomalies by isolating data points in a tree-based model,
effectively detecting outliers.
• DAGMM [15]: This method combines deep autoencoders
with Gaussian Mixture Models to model normal data
distribution and identify anomalies through reconstruction
errors.
• LSTM-NDT [10]: This method utilizes LSTM networks
to capture contextual information and dependencies in
sequential data for anomaly detection.
• LSTM-VAE [13]: This method projects multimodal
observations and time dependencies into a latent space,
using a VAE based on LSTM to reconstruct the expected
distribution.
• MAD-GAN [12]: This method uses LSTM within a GAN
framework to model temporal correlations in time series
data.
• OmniAnomaly [14]: This method is a priori-driven
stochastic model used to detect timestamp anomalies,
returning the reconstruction probability directly.
• USAD [36]: This method trains an encoder-decoder
framework in an adversarial manner to achieve fast and
efficient training.
• AT-DCAEP [37]: This method integrates a convolutional
autoencoder for feature extraction and an attention-based
prediction network to capture temporal dependencies,
which operates in an unsupervised manner, eliminating
the need for extensive data labeling.
• MTAD-GAT [19]: This method considers the relationships between sensors as a complete graph and uses a
graph attention neural network for anomaly detection.
• GDN [4]: This method builds a graph structure based
on pairwise cosine similarity between nodes, uses
attention-based graph neural networks to learn time series
dependencies, and predicts future behaviors.
• FuSAGNet [5]: The graph structure is learned by pairwise
cosine similarity between recursive sensor embeddings.
Subsequently, it employs a sparse autoencoder to derive
a sparse representation of the input data, which is then
inputted into a graph attention network for forecasting.
• GTA [6]: This method automatically learns the graph
structure by a direct approach and leverages graph convolution along with a transformer-based architecture to
capture temporal dependencies.

(31)

where TP, TN, FP, and FN represent the numbers of true
positives, true negatives, false positives, and false negatives,
respectively.
Additionally, the efficiencies of training and inference can
be evaluated by metrics such as training time per epoch,
inference time, memory usage, and the number of parameters.

D. Settings
The experimental parameters are listed in Table III. The
experiments were run with Python 3.8, PyTorch 1.10, and
CUDA 11.3, on a server featuring an Intel(R) Xeon(R) Platinum 8255C CPU and an NVIDIA RTX 3090 GPU. In
the case of the baseline methods, we utilized the default

8768

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

TABLE III
E XPERIMENTAL PARAMETER S ETTING

Fig. 4.

Distributions of the F1 scores on the four datasets.

experimental parameters as outlined in the paper. Specifically,
the window size ω for GDN and FuSAGNet is set to 5, while
for GTA, it is set to 60.
E. RQ1. Effectiveness and Efficiency
Initially, a performance comparison is made between
FuGLAD and all baselines. The recorded outcomes are presented in Table IV. Moreover, to demonstrate the stability of
our model, we conduct several experiments and plot box plots
of the model’s F1 scores on four datasets, which are shown in
Fig. 4. Finally, a comparison between existing graph structure
learning-based anomaly detection methods [4], [5], [6] and our
method is conducted in regard to efficiency. The findings of
this analysis are displayed in Table V and Table VI.
1) Effectiveness: FuGLAD demonstrates significant superiority over other baseline methods. Compared to the most
recent GSL-based anomaly detection methods, such as GDN
[4], FuSAGNet [5] and GTA [6], FuGLAD enhances learning
graph quality through the fusion graph structure and structured
prior graph. In addition, as shown in Fig. 4, FuGLAD has
stable performance.
All methods perform worse on the WADI dataset compared
to others due to its lower anomaly rates, as shown in Table II.
However, FuGLAD still shows the best performance on WADI
over the baseline methods. This demonstrates FuGLAD ’s
effectiveness in handling high dimensional time series data
and imbalanced samples, rendering it well-suited for practical
applications.
FuSAGNet’s subpar anomaly detection performance on the
SMAP and MSL datasets can be attributed to its design focus

on Cyber-Physical Systems (CPSs), which classifies sensors
by their specific process functions [5]. FuSAGNet incorporates sensors tailored to these specific processes, whereas the
sensors in the SMAP and MSL datasets do not have a clear
functional classification, leading to reduced effectiveness.
2) Efficiency: We compare our method with the existing
GSL-based anomaly detection methods in terms of training
time on four datasets and inference efficiency on the SWAT
dataset. The results are shown in Table V and Table VI.
Compared to FuSAGNet [5] and GTA [6], FuGLAD has
shorter training time and inference time. The training time of
GDN [4] is shorter than that of FuGLAD, but the performance
of GTA is much worse than that of FuGLAD. GDN’s shorter
training time and inference time can be attributed to its simplistic architecture, which only uses a graph attention network.
In contrast, GTA has the longest training time and inference
time because it uses Transformer, increasing its complexity.
FuSAGNet, which employs a sparse encoder SAE and a graph
attention network, requires joint training of reconstruction and
prediction models, resulting in performance and time that fall
between those of GDN and GTA. FuGLAD, with DCRNN
for prediction, significantly reduces time while maintaining
model performance. When considering memory usage and the
number of parameters, GDN and FuSAGNet exhibit lower
memory usage and parameters than the other two methods.
FuGLAD demonstrates lower memory usage and parameters
compared to GTA, attributed to FuGLAD’s efficient network
structure.
F. RQ2. Parameter Sensitivity
To show the robustness of our approach to varying parameters, we examine how different hyperparameters affect the
model’s performance.
1) Window Size: In this experiment, we examine the impact
of window size on our model’s effectiveness and training time.
The performance of the FuGLAD model with various window
sizes can be observed in Fig. 5. Additionally, Table VII
illustrates the training time per epoch of FuGLAD, also with
different window sizes. The experimental findings indicate
that the window size has an impact on both the anomaly
detection performance and training time. In situations where
a smaller window is utilized, FuGLAD can detect anomalies
more swiftly due to the shorter training time for smaller inputs.
However, if the window size is excessively large, shorter
anomalies may be concealed among a substantial number
of data points within the window, resulting in a decrease
in the model’s effectiveness. To strike a reasonable balance
between the F1 score and training time, a window size of 15 is

HE et al.: FUSION GRAPH STRUCTURE LEARNING-BASED MTSAD WITH STRUCTURED PRIOR KNOWLEDGE

8769

TABLE IV
P RECISION , R ECALL AND F1 S CORE ON THE F OUR DATASETS . T HE H IGHEST AND S ECOND -H IGHEST R ESULTS A RE H IGHLIGHTED W ITH B OLDFACE
AND U NDERLINE , R ESPECTIVELY

TABLE V
T RAINING T IME P ER EPOCH ( S )

TABLE VII
T RAINING T IME P ER EPOCH ( S ) W ITH D IFFERENT W INDOW S IZE

TABLE VI
I NFERENCE E FFICIENCY O FDIFFERENT GSL-BASED M ETHODS

Fig. 6.

The impact of regularization parameter.

λ2 from 0.0001 to 0.0008. Based on the results shown in Fig. 6,
FuGLAD demonstrates that the model has stable performance
at different regulation parameters.
Fig. 5.

The impact of window size.

employed for the SWAT and WADI datasets, while a window
size of 12 is utilized for the MSL and SMAP datasets.
2) Regularization Parameter: In this subsection, we present
the impact of regularization parameters on the anomaly detection results across four datasets. In this experiment, we vary

G. RQ3. Structured Prior Graph Performance
To demonstrate the effectiveness of the structured prior
graph in mitigating the impact of noise in data, we conduct
some experiments. We randomly generate noise from a normal
distribution Z ∼ N (0, 0.2) and add it to the raw data.
Subsequently, we compare the anomaly detection performance
(t)
of models using KNN prior graph θ K N N and structured prior

8770

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

TABLE VIII
M ODEL P ERFORMANCE W ITH D IFFERENT P RIOR G RAPHS AND DATA

TABLE IX
M ODEL P ERFORMANCE W ITH D IFFERENT G RAPH S TRUCTURE L EARNERS

Fig. 7.

Left: Partial graph structure learned on SWAT dataset. Right: Understand the relationship between sensors with ground truth and prediction.

TABLE X
I NFERENCE E FFICIENCY W ITH D IFFERENT G RAPH S TRUCTURE L EARNERS

data inherently introduces noise. Additionally, the larger the
dataset, the greater the amount of noise it contains.
H. RQ4. Fusion Graph Structure Learner Performance

graph θ (t) . This comparison was done with both the raw data
and the noisy data.
The experimental results are depicted in Table VIII. When
noisy data is utilized, FuGLAD demonstrates a noteworthy
improvement compared to the model that relies on the KNN
prior graph. This is due to the effective avoidance of data
noise when the prior graph is mapped into the structured
space. Furthermore, even when raw data is employed, the
structured prior continues to outperform the KNN prior graph.
This superiority is especially pronounced when considering the
SWAT and WADI datasets, as the collection process of raw

To validate the effectiveness of fusion graphs, we compare
this method with the three single graph learning methods in
Section V, as well as a method that directly trains DCRNN
with the prior graph from original data without graph learning
(ω/o GSL). For the three single graph learning methods,
we replace the fusion graph learning by K neighbor, CGL,
or FPM, while the rest modules are the same as FuGLAD.
ω/o GSL takes the prior graph as the graph structure of
DCRNN without graph learning. As shown in Table IX,
FuGLAD with multiple graphs outperforms other single graph
learning methods and prior graphs on all four datasets. Moreover, we evaluate the model’s inference efficiency, including
inference time, memory usage, and parameters. As shown in
Table X, FuGLAD requires slightly more inference time, memory, and parameters compared with the other four methods.
Furthermore, to demonstrate the effectiveness of our
proposed prior similarity-based weighted fusion method,

HE et al.: FUSION GRAPH STRUCTURE LEARNING-BASED MTSAD WITH STRUCTURED PRIOR KNOWLEDGE

8771

TABLE XI
M ODEL P ERFORMANCE W ITH D IFFERENT F USION M ETHODS

we conduct a comparative analysis with two other fusion
approaches. The first approach stochastically selects one of
the three graphs for model training (Random SG), while the
second approach fuses the three graphs by averaging them
(AVG). As shown in Table XI, PSF outperforms other fusion
methods on all four datasets, validating the effectiveness of
our proposed method.
We conduct a case study, as depicted in Fig. 7. Fig. 7
(left) illustrates a partial graph structure learned by FuGLAD,
while Fig. 7 (right) presents the predictions of our model for
relevant sensors. In this scenario, sensor AI T − 202 was compromised between timestamps 710 to 730. FuGLAD detected
the attack by identifying a significant difference between the
predictions and the ground truth for AI T − 202 during this
time period. Owing to the correlation between sensors in
the water treatment process, the attack on AI T − 202 led
to the shutdown of the dosing pump P − 203 and affected
the permeate conductivity analyzer AI T − 503. FuGLAD
accurately predicted the changes in P-203 from timestamps
710 to 730 and in AI T − 503 from timestamps 800 to 900.
The values of P −203 and AI T −503 followed the changes in
the ground truth and were not anomalies, as demonstrated in
Fig. 7 (right). This success is attributed to FuGLAD’s ability
to correctly learn the correlation among the three sensors,
as illustrated in Fig. 7 (left).
VII. C ONCLUSION AND F UTURE W ORK
In this paper, we propose FuGLAD, a technique that fuses
graph structures to refine the quality of the learning graph
and exploits the structured prior graph to eliminate the effects
of noise in the data. Besides, we combine the learned graph
with the DCRNN predictor to efficiently forecast future sensor
behavior and detect anomalies based on prediction errors. Our
method outperforms the baselines on four public datasets,
delivering the best performance with short-term data and
reduced training overhead. Future work will focus on improving the model’s scalability for large graphs.
R EFERENCES
[1] S. He et al., “A joint matrix factorization and clustering scheme for
irregular time series data,” Inf. Sci., vol. 644, Oct. 2023, Art. no. 119220.
[2] S. He, Z. Li, J. Wang, and N. N. Xiong, “Intelligent detection for
key performance indicators in industrial-based cyber-physical systems,”
IEEE Trans. Ind. Informat., vol. 17, no. 8, pp. 5799–5809, Aug. 2021.
[3] D. Scheinert, A. Acker, L. Thamsen, M. K. Geldenhuys, and O. Kao,
“Learning dependencies in distributed cloud applications to identify and
localize anomalies,” in Proc. IEEE/ACM Int. Workshop Cloud Intell.,
May 2021, pp. 7–12.
[4] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. 35th AAAI Conf. Artif. Intell., 2021,
pp. 4027–4035.

[5] S. Han and S. S. Woo, “Learning sparse latent graph representations for anomaly detection in multivariate time series,” in Proc. 28th
ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug. 2022,
pp. 2977–2986.
[6] Z. Chen, D. Chen, X. Zhang, Z. Yuan, and X. Cheng, “Learning
graph structures with transformer for multivariate time-series anomaly
detection in IoT,” IEEE Internet Things J., vol. 9, no. 12, pp. 9179–9189,
Jun. 2022.
[7] Y. Zhu et al., “A survey on graph structure learning: Progress and
opportunities,” 2021, arXiv:2103.03036.
[8] C. Shang, J. Chen, and J. Bi, “Discrete graph structure learning for
forecasting multiple time series,” 2021, arXiv:2101.06861.
[9] K. Yao, J. Liang, J. Liang, M. Li, and F. Cao, “Multi-view graph convolutional networks with attention mechanism,” Artif. Intell., vol. 307,
Jun. 2022, Art. no. 103708.
[10] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and
T. Söderström, “Detecting spacecraft anomalies using LSTMs and nonparametric dynamic thresholding,” in Proc. 24th ACM SIGKDD Int.
Conf. Knowl. Discovery Data Mining, Jul. 2018, pp. 387–395.
[11] C. Zhang et al., “A deep neural network for unsupervised anomaly
detection and diagnosis in multivariate time series data,” in Proc. AAAI
Conf. Artif. Intell., vol. 33, 2019, pp. 1409–1416.
[12] D. Li, D. Chen, B. Jin, L. Shi, J. Goh, and S.-K. Ng, “MAD-GAN:
Multivariate anomaly detection for time series data with generative
adversarial networks,” in Proc. Int. Conf. Artif. Neural Netw. (ICANN).
Munich, Germany: Springer, 2019, pp. 703–716.
[13] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly detector for
robot-assisted feeding using an LSTM-based variational autoencoder,”
IEEE Robot. Autom. Lett., vol. 3, no. 3, pp. 1544–1551, Jul. 2018.
[14] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discovery Data
Mining, 2019, pp. 2828–2837.
[15] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Represent., 2018,
pp. 1–19.
[16] Y. Zhang, Y. Chen, J. Wang, and Z. Pan, “Unsupervised deep anomaly
detection for multi-sensor time-series signals,” IEEE Trans. Knowl. Data
Eng., vol. 35, no. 2, pp. 2118–2132, Feb. 2023.
[17] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” 2022,
arXiv:2201.07284.
[18] Q. He, Y. J. Zheng, C. L. Zhang, and H. Y. Wang, “MTAD-TF:
Multivariate time series anomaly detection using the combination of
temporal pattern and feature pattern,” Complexity, vol. 2020, pp. 1–9,
Oct. 2020.
[19] H. Zhao et al., “Multivariate time-series anomaly detection via graph
attention network,” in Proc. IEEE Int. Conf. Data Mining (ICDM),
Nov. 2020, pp. 841–850.
[20] W. Zhang, C. Zhang, and F. Tsung, “GRELEN: Multivariate time series
anomaly detection from the perspective of graph relational learning,” in
Proc. Int. Joint Conf. Artif. Intell. (IJCAI), 2022, pp. 2390–2397.
[21] H. Pang et al., “Asymptotic consistent graph structure learning for multivariate time-series anomaly detection,” IEEE Trans. Instrum. Meas.,
vol. 73, pp. 1–10, 2024, doi: 10.1109/TIM.2024.3369159.
[22] X. Zhou, C. Dai, W. Wang, and T. Qiu, “Global–local association
discrepancy for multivariate time series anomaly detection in IIoT,”
IEEE Internet Things J., vol. 11, no. 7, pp. 11287–11297, Apr. 2024,
doi: 10.1109/JIOT.2023.3330696.
[23] S. Qin, L. Chen, Y. Luo, and G. Tao, “Multiview graph contrastive
learning for multivariate time-series anomaly detection in IoT,” IEEE
Internet Things J., vol. 10, no. 24, pp. 22401–22414, Dec. 2023, doi:
10.1109/JIOT.2023.3303946.

8772

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 19, 2024

[24] S. He et al., “Graph structure learning-based multivariate time series
anomaly detection in Internet of Things for human-centric consumer
applications,” IEEE Trans. Consum. Electron., early access, Jun. 4, 2024,
doi: 10.1109/TCE.2024.3409391.
[25] X. Ma et al., “A comprehensive survey on graph anomaly detection
with deep learning,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12,
pp. 12012–12038, Dec. 2023.
[26] M. R. Khan and J. E. Blumenstock, “Multi-GCN: Graph convolutional
networks for multi-view networks, with applications to global poverty,”
in Proc. AAAI Conf. Artif. Intell., Jul. 2019, vol. 33, no. 1, pp. 606–613.
[27] S. Fan, X. Wang, C. Shi, E. Lu, K. Lin, and B. Wang, “One2Multi
graph autoencoder for multi-view graph clustering,” in Proc. Web Conf.,
Apr. 2020, pp. 3070–3076.
[28] H. Xiao, J. Gao, D. S. Turaga, L. H. Vu, and A. Biem, “Temporal multiview inconsistency detection for network traffic analysis,” in Proc. 24th
Int. Conf. World Wide Web, May 2015, pp. 455–465.
[29] E. Gujral, R. Pasricha, and E. Papalexakis, “Beyond rank-1: Discovering
rich community structure in multi-aspect graphs,” in Proc. Web Conf.,
Apr. 2020, pp. 452–462.
[30] H. Yu et al., “Regularized graph structure learning with semantic knowledge for multi-variates time-series forecasting,” 2022,
arXiv:2210.06126.
[31] Z. Zhong, L. Zheng, D. Cao, and S. Li, “Re-ranking person reidentification with K-reciprocal encoding,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit., Jul. 2017, pp. 1318–1327.
[32] X. Zhang, M. Jiang, Z. Zheng, X. Tan, E. Ding, and Y. Yang,
“Understanding image retrieval re-ranking: A graph neural network
perspective,” 2020, arXiv:2012.07620.
[33] Z. Wu, S. Pan, G. Long, J. Jiang, X. Chang, and C. Zhang, “Connecting the dots: Multivariate time series forecasting with graph neural
networks,” in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discovery
Data Mining, Aug. 2020, pp. 753–763.
[34] Y. Li, R. Yu, C. Shahabi, and Y. Liu, “Diffusion convolutional
recurrent neural network: Data-driven traffic forecasting,” 2017,
arXiv:1707.01926.
[35] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. 8th
IEEE Int. Conf. Data Mining, Jun. 2008, pp. 413–422.
[36] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining,
2020, pp. 3395–3404.
[37] W. Liu et al., “Unsupervised deep anomaly detection for industrial
multivariate time series data,” Appl. Sci., vol. 14, no. 2, p. 774, Jan. 2024.

Shiming He received the B.S. degree in information
security and the Ph.D. degree in computer science
and technology from Hunan University, China, in
2006 and 2013, respectively. She is currently an
Associate Professor with the School of Computer
and Communication Engineering, Changsha University of Science and Technology, Changsha, China.
Her research interests include machine learning, data
analysis, and anomaly detection.

Genxin Li received the B.S. degree from Jiangxi
Science and Technology Normal University in 2021.
He is currently pursuing the M.S. degree in computer
science and technology with Changsha University
of Science and Technology. His research interests
include deep learning, data analysis, and anomaly
detection.

Kun Xie (Member, IEEE) received the Ph.D.
degree in computer application from Hunan University, Changsha, China, in 2007. She has published
over 100 papers in major journals and conference proceedings, including journals such as
IEEE/ACM T RANSACTIONS ON N ETWORKING,
IEEE T RANSACTIONS ON M OBILE C OMPUTING,
IEEE T RANSACTIONS ON C OMPUTERS, IEEE
T RANSACTIONS ON PARALLEL AND D ISTRIBUTED
S YSTEMS, IEEE T RANSACTIONS ON W IRELESS
C OMMUNICATIONS, and IEEE T RANSACTIONS ON
S ERVICES C OMPUTING, and conferences, including SIGMOD, INFOCOM,
ICDCS, SECON, DSN, and IWQoS. Her research interests include network
measurement, network security, big data, and AI.
Pradip Kumar Sharma (Senior Member, IEEE)
received the Ph.D. degree in CSE from Seoul
National University of Science and Technology,
South Korea, in August 2019.
He was a Post-Doctoral Research Fellow with the
Department of Multimedia Engineering, Dongguk
University, South Korea. He was a Software Engineer with MAQ Software, India, and was involved
in a variety of projects, proficient in building
largescale complex data warehouses, OLAP models,
and reporting solutions that meet business objectives
and align IT with business. He is currently an Assistant Professor of cybersecurity with the Department of Computing Science, University of Aberdeen,
U.K. He has published many technical research articles in leading journals
from IEEE, Elsevier, Springer, and MDPI. Some of his research findings are
published in the most cited journals. His current research interests include
cybersecurity, blockchain, edge computing, SDN, and the IoT security. He has
also been invited to serve as a Technical Program Committee Member and
the Chair in several reputed international conferences, such as IEEE DASC
2021, IEEE CNCC 2021, CSA 2020, IEEE ICC 2019, IEEE MENACOMM
2019, and 3ICT 2019. He received a Top 1% Reviewer in computer science by
Publons Peer Review Awards 2018 and 2019, Clarivate Analytics. He has been
an expert reviewer for IEEE T RANSACTIONS, Elsevier, Springer, and MDPI
journals and magazines. He is an Associate Editor of Peer-to-Peer Networking and Applications (PPNA), Human-Centric Computing and Information
Sciences (HCIS), Electronics (MDPI), and Journal of Information Processing
Systems (JIPS). He has been serving as the Guest Editor for international
journals of certain publishers, such as IEEE, Elsevier, Springer, MDPI, and
JIPS. He is listed in the World’s Top 2% Scientists for citation impact during
the calendar year 2019 by Stanford University.
PAPER_TEXT
