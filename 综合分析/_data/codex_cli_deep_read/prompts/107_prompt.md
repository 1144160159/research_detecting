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
# [107] Flow Sequence-Based Anonymity Network Traffic Identification with Residual Graph Convolutional Networks
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
编号：107
题名：Flow Sequence-Based Anonymity Network Traffic Identification with Residual Graph Convolutional Networks
年份：2022
DOI：10.1109/iwqos54832.2022.9812882
来源：2022 IEEE/ACM 30th International Symposium on Quality of Service (IWQoS)
PDF：paper/10.1109_iwqos54832.2022.9812882.pdf
已有粗分类：加密流量分类与应用识别
二级关联：图学习、知识图谱与威胁情报
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\107.txt
- 原始字符数：52790
- 本次发送字符数：52790
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2022 IEEE/ACM 30th International Symposium on Quality of Service (IWQoS) | 978-1-6654-6824-4/22/$31.00 ©2022 IEEE | DOI: 10.1109/IWQoS54832.2022.9812882

Flow Sequence-Based Anonymity Network Traffic
Identification with Residual Graph Convolutional Networks
Ruijie Zhao† , Xianwen Deng† , Yanhao Wang‡ , Libo Chen† , Ming Liu† , Zhi Xue† , and Yijun Wang†∗
† School of Electronic Information and Electrical Engineering, Shanghai Jiao Tong University, Shanghai, China
‡ NIO Security Research, Shanghai, China
∗ Corresponding Author

Abstract—Identifying anonymity services from network traffic is a crucial task for network management and security.
Currently, some works based on deep learning have achieved
excellent performance for traffic analysis, especially those based
on flow sequence (FS), which utilizes information and features
of the traffic flow. However, these models still face a serious
challenge because of lacking a mechanism to take into account
relationships between flows, resulting in mistakenly recognizing
irrelevant flows in FS as clues for identifying traffic. In this
paper, we propose a novel FS-based anonymity network traffic
identification framework to tackle this problem, which leverages
Residual Graph Convolutional Network (ResGCN) to exploit
relationships between flows for FS feature extraction. Moreover,
we design a practical scheme to preprocess the raw data of realworld traffic, which further improves identification performance
and efficiency. Experimental results on two real-world traffic
datasets demonstrate that our method outperforms state-of-theart methods by a large margin.
Index Terms—Anonymity network, traffic classification, flow
sequence, deep learning, graph convolutional networks.

I. I NTRODUCTION
Due to the increasing demand for the protection of personal
network meta-data, anonymity networks have grown in popularity. They provide a way for users to achieve anonymity
online. In detail, anonymity networks use encryption and
obfuscation methods in communication to conceal the transmission content and the true identity of users. However, while
making communication harder to trace and identify, anonymity
networks also provide hiding space for illegal and criminal
activities [1]–[3]. Thus, it is essential to design an effective
traffic analysis system to supervise anonymity networks.
In the early stage, the traditional network traffic analysis
system, mainly based on rules to realize scene identification,
plays a vital role in network monitoring. These methods
identify a limited number of services by analyzing the inherent
components (i.e., port numbers and characteristic values) in the
traffic packet. Unfortunately, the identification method based
on port numbers has become invalid due to the mechanism of
anonymity networks and many other networks using random
ports [4]. At the same time, the growth of network scale and
the application of encryption technology have also adversely
affected the performance of traffic analysis methods based on
characteristic values.
Recently, benefiting from the development of artificial intelligence (AI) technology, many efforts [5]–[12] have been
978-1-6654-6824-4/22/$31.00 © 2022 IEEE

made to develop various traffic analysis methods based on
machine learning (ML) and deep learning (DL) algorithms.
The AI-based traffic analysis methods monitor traffic data’s
basic and statistical characteristics to better deal with complex
and changeable network traffic. There is no doubt that AI
technology has greatly improved the performance of traffic
analysis methods. In addition, we note that many studies have
shown that the traffic data has obvious spatio-temporal correlations [13]–[15]. For example, when a user uses an anonymity
network to browse the web, many related application requests
will appear in a short period. These application requests will
generate corresponding multiple flows in the traffic. Based
on the spatio-temporal correlation, some researchers proposed
methods [16]–[18] to establish flow sequences to achieve better traffic analysis performance. However, they all ignore some
critical relationships between flows, resulting in mistakenly
taking irrelevant flows in the flow sequence as clues for traffic
identification. Therefore, to make the identification more accurate, we should leverage these relationships to extract features
from flow sequences. The definitions of these relationships are
listed below.
Attribute Relationship. The same application request
generated forward direction flow (F-flow) and corresponding reverse direction flow (R-flow) have the attribute relationship.
• Time Relationship. The time relationship represents the
time interval between the flows. The longer the interval,
the lower the correlation between them.
•

Due to the structural constraints of current methods implemented based on DL algorithms (e.g., CNN and LSTM), they
cannot consider the two relationships during the feature extraction process. So how can we leverage these relationships? The
graph convolutional network (GCN), which connects neighbor
nodes through edges with different weights and updates the
feature representation by calculating the feature summation
of neighbor nodes, provides a way to solve this problem by
connecting flows according to their relationships.
In this paper, we propose a novel flow sequence-based traffic
identification framework with residual graph convolutional
network (ResGCN). We take continuous multiple flows (i.e.,
the flow sequence) as the input feature. Each flow is a node,
and the weight of the edge is set according to the relationships
between flows. To better preserve the spatial structure of the

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:57 UTC from IEEE Xplore. Restrictions apply.

gradient, we adopt the residual structure to extract features.
Besides, as an end-to-end framework for identifying realworld traffic, it extracts rich features (e.g., statistical features,
basic features, etc.) from the raw traffic according to the flow
segmentation scheme, and uses the Light Gradient Boosting
Machine (LightGBM) algorithm to select the optimal combination of features, improving the model performance and
efficiency.
In summary, this paper makes the following contributions:
• We propose exploiting the attribute and time relationships
between the flows and realizing a more reasonable and
effective feature extraction of the flow sequence for traffic
identification. We posit that graph convolutional network
(GCN) is suitable for our purpose, and propose a novel
R ES GCN model to identify different network services.
To our best knowledge, this is the first investigation in
this direction.
• We design a practical scheme to process real-world raw
traffic data. It considers flow segmentation, which is
used to generate and enrich the flow features of the raw
traffic, and LightGBM-based feature combination, which
avoids the insignificant features from reducing model
performance and efficiency.
• We evaluate the framework on two real-world traffic
datasets. Experimental results show that our method has
a more excellent classification performance than other
methods, and it is suitable for identifying different network services.
II. R ELATED W ORK
The identification of anonymity network traffic is a typical traffic classification task. Network traffic classification
methods are mainly implemented using three methods (i.e.,
rules, ML, and DL). The rule-based analysis method can
only analyze the uncomplicated network traffic, and the port
number identification has been proved to be invalid [19] in the
complex network environment.
To solve the issues with rule-based analysis methods, researchers applied ML and DL algorithms to analyze the traffic
of anonymity networks or other networks. For instance, Cai et
al. [2] adopted feature selection algorithm to filter out some
irrelevant and redundant features, and then used XGBoostbased algorithm to identify Tor, I2P, and JonDonym networks
for four scenarios; Wang et al. [9] proposed an encrypted
traffic classification method based on 2D-CNN, which converted traffic data into image representations; Lin et al. [10]
proposed an intrusion detection system with stacked sparse autoencoder (SSAE) and recurrent neural network (RNN), which
extracts traffic features with the greedy layer-wise strategy
to obtain good detection performance. Due to the structural
constraints of aforementioned algorithms, they cannot consider
the relationships between flows during the feature extraction
process. Recently, we have also noticed some works exploring
graph neural networks (GNN) for traffic classification tasks.
Shen et al. [11] proposed to use different applications’ graph
structures (e.g., spindle-shaped, fish-shaped) as input features

for classification. Obviously, a large amount of traffic packets
are needed to form structures with different characteristics.
Sun et al. [12] designed a traffic classifier based on GNN
and k-nearest neighbors. Their edge weights of the graph are
the similarity of 5 nearest neighbors selected by k-nearest
neighbor (KNN). However, the graph of this method relies
heavily on the KNN, which means that the quality of the graph
is not stable.
To conquer the limitations in current studies, we propose
a R ES GCN classifier for anonymity network traffic identification, which explores the use of attribute relationships and
time relationships between flows to build graph structures for
feature extraction. Our method uses statistical features of flows
to counter obfuscation and encryption techniques (as described
in Section III-A), and builds graphs in only eight continuous
flows for real-time analysis.
III. P ROBLEM F ORMULATION AND A PPROACH OVERVIEW
In this section, we first provide the background of flows in
the traffic. Then, we introduce the preliminaries of ML-based
feature selection algorithm and DL-based feature extraction
algorithm. Finally, we present an overview of our approach
to identifying the various anonymity services in the network
traffic.
A. Flow Generation
In packet switching networks, traffic flow is a sequence
of packets carrying information between two hosts. The raw
traffic data is captured and stored in pcap (abbreviation of
packet capture) format. As a kind of encrypted traffic, it
is more difficult to identify different services by directly
analyzing the pcap file of anonymity network traffic. Thus,
it is necessary to calculate and extract the statistical features
to enrich the feature information of each flow.
The statistical features of encrypted traffic are calculated
through the Layer 2 to Layer 4 header features, which are
not affected by any encryption on Layer 7 1 . These statistical
features reflect the characteristics of the traffic from many
aspects. For instance, the inter-arrival time (IAT) represents the
packet interval; the maximum, minimum, and average package
size of the Layer 3 reflects the package size characteristics
of the traffic; packet length (PL) represents the length of
the packet produced by each flow from the beginning. Note
that as above-mentioned are only a tiny part of the statistical
features. Since the statistical features are computed using the
lightweight traffic feature extraction tool Tranalyzer2 , which is
not the contribution of our method, we only briefly introduce
them.
To preserve the spatio-temporal correlations of the raw traffic, we need to store the generated flow sequentially according
to the timestamp during extraction. As shown in Fig. 1, we
take continuous I flows as a flow sequence, where each flow
contains a total of J features. The raw traffic is composed of K
1 In the OSI reference model, the communications between a computing
system are split into seven different abstraction layers, labelled 1 to 7.
2 https://tranalyzer.com

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:57 UTC from IEEE Xplore. Restrictions apply.

Sequences
Features

i-th flow

I

j-th feature

Flows
J

I

I

K
J

J

k-th sequence

K
J

Fig. 1. The traffic flow model.

flow sequences, and each sequence is continuous in time with
the previous sequence. As the same type of network behavior
often lasts for a certain period, building a flow sequence
for analysis has become an effective method to improve
classification performance. Obviously, there are some relationships (i.e., attribute and time relationships) between flows
in each sequence. If these relationships can be considered in
the feature extraction process, the classifier network’s design
will be more reasonable and effective. Unfortunately, there is
currently no related work that combines these relationships for
feature extraction.
In addition, many variables will affect the results generated during the flow generation process. First, flows can be
segmented according to different durations or packet sizes,
directly affecting the calculation results of related statistics.
Second, the generated flows contain different statistical features, but some may be meaningless for traffic identification.
To achieve optimal flow generation results, we should consider
the following two aspects:
• Effectiveness: Effectiveness means that the classifier can
achieve excellent classification performance by using the
generated flows.
• Timeliness: Timeliness means that anonymous services
can be identified as quickly as possible.
Therefore, based on effectiveness and timeliness, the performance of different segmentation methods and selected features
will be comprehensively evaluated in Section V-C.

performance. However, these methods are time-consuming
since they have to scan all sample points for each feature
to select the best segmentation point. LightGBM greatly
reduces the time complexity of processing samples through the
gradient-based one-side sampling (GOSS) algorithm [23]. The
main idea of the GOSS algorithm is that samples with large
gradients play a major role in the calculation of information
gain, which means that these samples with large gradients will
contribute more information gain. Therefore, to maintain the
accuracy of information gain evaluation, samples with large
gradients can be retained when samples are down-sampled,
and samples with small gradients are randomly sampled in
proportion. Due to the reduction of a large number of data
samples with small gradients, the amount of calculation is
greatly reduced.
C. GCN for Feature Extraction
Graph convolution network (GCN) is derived from graph
spectral theory [24], which extends the convolution operation from grid-based data to graph structure data. GCN also
solved natural language processing (NLP) tasks with similar
issues (i.e., the relationship between words in a sentence) and
achieved great success [25]. In this research, we regard the
flow sequence as a graph, and each flow is a node in the
graph. A connection relationship is formed according to the
relationship between different flows.
Based on the decomposition of graph Laplacian matrix, the
signal x on the graph G is filtered by a kernel gθ:
gθ ∗G x = gθ (L)x = gθ (U ΛU T )x = U gθ (Λ)U T x,

(1)

where ∗G denotes a graph convolution operation. L is the
graph Laplacian matrix. The eigenvalue decomposition of the
Laplacian matrix is L = U ΛU T , where Λ is a diagonal
matrix, and U is Fourier basis.
However, the decomposition becomes very difficult when
the scale of the graph is large. For this purpose, Chebyshev
polynomials are adopted to solve this computational problem:
gθ ∗G x = gθ (L)x =

M
−1
X

θm Cm (L̃)x,

(2)

m=0

B. LightGBM for Feature Selection
Feature selection is to remove insignificant features in the
generated flows, which can make the generated results more
in line with effectiveness and timeliness [20]–[22]. In terms
of effectiveness, insignificant features can be characterized as
noise under certain conditions, which can adversely affect the
identification result. In terms of timeliness, removing these
features can reduce the calculation of statistics in the flow
generation process and speed up flow generation. In addition,
low-dimensional features will also reduce the complexity and
classification time of the feature extraction network.
LightGBM is an ML algorithm based on a gradient boosting
decision tree (GBDT). As the GBDT algorithm sorts the
importance of features during the training process, it is very
suitable for feature selection tasks. Traditional GBDT-based
algorithms (e.g., PGBRT and XGBoost) have achieved good

2
L − IN ,
where θm is the learnable parameters. L̃ = λmax
in which λmax is the maximum eigenvalue of the Laplacian
matrix and IN is a unit matrix. The recursive definition of the
Chebyshev polynomial is Cm (L̃) = 2L̃Cm−1 (L̃) − Cm−2 (L̃)
and C1 (L̃) = L̃, C0 (L̃) = IN .

D. Our Approach
In this paper, our research focuses on how to identify
different anonymity services in real-world anonymity networks
more effectively and quickly. Thus, our approach includes a
novel traffic classifier and the scheme of traffic acquisition,
flow generation, and feature selection.
Our approach includes three steps. As the first step, we
configure the switch mirror port, and use the traffic capture
tool tcpdump to obtain the real-time traffic and save it as a
series of pcap files. The frequency of traffic acquisition can

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:57 UTC from IEEE Xplore. Restrictions apply.

Generate Flows

3rd flow

3rd flow

4th flow

4th flow

…

4th flow

Ith flow

Ith flow

Ith flow

1st FS

2nd FS

Kth FS

…

…

3rd flow

1st FS graph

Kth FS graph

LightGBM

IMPOTRANCE High
uppQuartileIat
pktps
ipMinTTL
ipMaxTTL
dsIqdIat
MaxIAT
dsRobStdIat
dsMeanIat
…

Features

…

…

dir pktps tcnt … bytps

Flows

…

Generator

Select Feature Combination

ResGCN Classifier

Output

2nd flow

Build Graph Structures

st

MLP

1 flow

2nd flow

st

ResGCN Blocks

1 flow

2nd flow

st

Input

1 flow

dir pktps tcnt … bytps
dir pktps tcnt … bytps

Raw Traffic Data

Compose Flow Sequences

dir pktps tcnt … bytps

Low

Fig. 2. Overview of the flow sequence-based anonymity network traffic identification framework.

be set differently according to the actual situation. Second, we
use a flow generator to realize the fast and real-time analysis
of pcap files. According to the preset rules, we extract the flow
in the pcap file. The flow sequence is composed of multiple
continuous flows, and the relationship graph between different
flows will also be generated in this step. Then, the LightGBMbased feature selection method is used to select the optimal
feature combination. Finally, the proposed R ES GCN classifier
leverages generated relationship graphs to realize effective
anonymity network traffic identification.
IV. F RAMEWORK OF A NONYMITY N ETWORK T RAFFIC
I DENTIFICATION
In this section, we introduce our anonymity network traffic
identification method. After processing the raw traffic data,
R ES GCN is adopted to realize the anonymity services identification. The overview of the proposed method is shown in
Fig. 2, and the process of our approach is summarized in
Algorithm 1. The details of each processing stage in the
proposed framework are presented as follows.
Algorithm 1 Pseudocode of the Proposed Framework
Input: raw traffic data Dr , total epoch times n
Output: ResGCN model for anonymity network traffic identification
1: procedure Data Preprocessing (Dr )
2:
Generate flows and compute the standardization result
3:
Take continuous multiple flows as flow sequences
4:
Build relationship graph between flows
5:
Use LightGBM-based method to select feature combination
6:
Dp ←− New training dataset after preprocessing
7:
Gp ←− Graph structure of the training data
8: return Dp , Gp
9: procedure ResGCN Model (Dp , Gp )
10: while i ≤ n do
11:
Load the proposed network
12:
Input Dp , Gp into the network for training
13:
Update the model according to cross entropy loss
14:
Save ResGCNi model
15: end while
16: Save ResGCNn as the final model

A. Raw Traffic Data Processing Scheme
As mentioned in Section III-A, the raw traffic data is
obtained as the pcap file, which needs to be processed to
be more effectively applied to the R ES GCN model. Data
processing includes the following four steps.
1) Generate Flows: In real-world traffic, e.g., the service
provided by BitTorrent will cause a very long flow duration.
If we do not segment the long-duration flow, it will adversely
affect the classification efficiency. Flow segmentation schemes
can be divided into two categories: time-based and size-based.
The time-based segmentation scheme sets the upper limit of
the duration of the flow, and the size-based segmentation
scheme sets the upper limit of the maximum packet size. Thus,
we first use the generator to generate rich features from the raw
traffic through a time-based or size-based flow segmentation
scheme. Then, the following standard normalization method
is adopted to improve the reliability of the data:
x−µ
,
(3)
z=
σ
where µ represents the mean of the original data, and σ the
standard deviation of the original data.
2) Compose Flow Sequences: Some previous studies on
traffic classification have shown that the use of flow sequences
will significantly improve the classification performance [16]–
[18]. However, a flow sequence containing too few flows
has insufficient information and cannot achieve the ideal
classification performance; too many flows will bring more
computational burden and reduce efficiency. Thus, we set each
of the flow sequence to contain eight continuous flows.
3) Build Graph Structures: Graph generation is the key to
the successful application of GCN. We want to achieve a more
effective and reasonable analysis of the flow sequences through
the graph structure. Obviously, there are many relationships
between the different flows in each sequence. We build the
graph structure from the following two aspects.
Attribute Relationship Graph (ARG): As mentioned in
Section I, the relationship between the F-flow and the Rflow generated by an application request is defined as the
attribute relationship. Obviously, these two flows have a strong
correlation. We determine the attribute relationship between
the two flows through the 3-tuple (i.e., flow index, transmitted
bytes, and received bytes). During the flow generation process,
a flow index is generated according to the source/destination
IP, source/destination port, and protocol. However, the segmentation scheme splits the flow, resulting in a situation where

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:57 UTC from IEEE Xplore. Restrictions apply.

8th R-flow

7th F-flow

6th R-flow

5th F-flow

4th F-flow

3rd R-flow

2nd F-flow

1st R-flow

Flow Sequence

F(x)

Input

x

F(x) + x

GFI RFI
GCN Unit

GCN Unit

ResGCN Block  4

FS & FS Graph

MLP

Output

3 Layers

Traffic Label

GFI RFI
Relu

Relu

Fig. 4. The structure of ResGCN.

Attribute Relationship

Time Relationship

Fig. 3. The time relationship and attribute relationship of different flows
in the flow sequence.

there are multiple continuous flows with the same index. if the
two flows have the same flow index and swap the number of
transmitted bytes and received bytes, they have an attribute
relationship. Based on the 3-tuple, we connect the F-flow and
the R-flow and set their attribute relationship weight to 1.

P
P
where nO =
I[xi ∈ O], njl|O (d) =
I[xi ∈ O : xi ≤ d]
P
I[xi ∈ O : xi >d]. Traverse the split point
and njr|O (d) =
of each feature, find the split point d∗j = argmaxd Vj (d)
and calculate the maximum information gain Vj (d∗j ), and then
divide the data into the left and right child nodes according
to the split point d∗j of feature j ∗ . After sorting and random
sampling operations, the information gain is estimated by the
following formulas:
X
1−a X
vl =
gi +
gi ,
(8)
b
xi ∈Al

Ga (V, E) = 3T upleM atching.

Time Relationship Graph (TRG): The continuous multiple
flows are arranged in order according to the generation time of
the flow. We build TRG for different flows based on generation
time. If the generation time of the traffic is closer, the higher
the weight will be set. Specifically, in each flow sequence, the
A-th flow is f lowa , and the B-th flow is f lowb . The distance
between the two flows is |B − A|, and the initial weight is
1
|B−A| . Only flows in the same direction (i.e., forward direction
or reverse direction) will be connected.
Gt (V, E) = distance−1 .

(5)

To set the time relationship weights of each flow more
reasonably, we input the time relationship weights of each
flow into the Softmax function, so that the sum of the new
weights is 1. Suppose we have n time relationship weights in
a flow, we can denote the process as:
w1′ , w2′ , ..., wn′ = Sof tmax(w1 , w2 , ..., wn ).

xi ∈Bl

(4)

(6)

As shown in Fig. 3, different flows in the flow sequence
are connected through the attribute relationship and time
relationship. After establishing the ARG and TRG, we perform
normalized on the adjacency matrix of these two graphs to
obtain the fusion graph.
4) Select Feature Combination: The LightGBM-based
feature selection method is designed to select the optimal feature combination, which can effectively avoid the insignificant
features from reducing the performance and efficiency of the
classifier.
To evaluate the importance of the j-th feature shown in
Fig. 1, we adopt LightGBM to calculate the gradient of each
sample. For the gradient calculation of each sample, O is the
flows on a fixed node in the decision tree. The variance gain
of node split feature j at point d is expressed as:
P
P
2
( xi ∈O:xi >d gi )2
1 ( xi ∈O:xi ≤d gi )
(
+
) (7)
Vj|O (d) =
nO
njl|O (d)
njr|O (d)

vr =

1−a X
gi ,
b

(9)

v2
1 vl2
+ j r ).
( j
n nl (d) nr (d)

(10)

X

gi +

xi ∈Ar

Ṽj (d) =

xi ∈Br

In subsequent experiments, different comparison algorithms
will be used to implement feature selection, and the performance of these algorithms will be compared.
B. Flow Sequence-based R ES GCN Classifier
Some previous studies have considered the use of flow
sequences to achieve better traffic classification performance [16]–[18], but they cannot carry out directed information exchange between flows. Aiming to address the limitations of these methods, we leverage a GCN over the fused
graph of the flows, which allows related flows in the flow
sequence to exchange information.
The input of R ES GCN is a flow sequence consisting of
eight continuous flows after feature selection, which can be
constructed as a graph mentioned above. Every flow is seen
as a node in a graph. The entire model is composed of four
ResGCN blocks and a 3-layer MLP.
The structure of the ResGCN block is shown in Fig. 4.
It consists of two GCN units, and the activation function
ReLU is used in between. The residual structure is applied in
the ResGCN block, which can solve the degradation problem
that occurs as the depth of the network increases. The GCN
unit includes two key components, i.e., the generated features
interaction module (GFI) and related flows interaction module
(RFI). The GFI is a fully connected layer without bias. It
performs a linear transformation on the features (e.g., packet
interval, package size, etc.) of each flow, allowing different
features to interact. The RFI enables related flows to exchange
information based on the relationship graph. According to
the fusion graph mentioned above, these two modules can
perform effective information interaction on different features
and related flows.

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:57 UTC from IEEE Xplore. Restrictions apply.

TABLE I
S UMMARY OF T HE DATASETS U SED FOR E VALUATION .
Dataset

SJTU-AN21
(D1 )

ISCXVPN2016
(D2 )

Category

Training dataset

Test dataset

Eepsites
IRC
Snark
Video
JonDonym
Bittorrent
Chat
FTP
Streaming
Browsing

1,825
3,009
7,284
12,577
1,254
198
624
364
949
1,130

1,197
484
1,784
581
967
76
150
184
598
958

Total

29,214

6,979

Browsing
FTP
P2P
VoIP
Email
Streaming
Chat

3,646
4,446
736
8,464
689
1,523
3,209

912
1,112
184
2,117
173
381
803

Total

22,713

5,682

After information interaction through 4 ResGCN blocks, a
dropout layer is used to improve model generalization ability
and reduce overfitting. Finally, the output of the dropout layer
is flattened, and a 3-layer MLP with two hidden layers and one
output layer is used to perform traffic classification. The first
hidden layer consists of a linear layer with output size 220,
followed by rectified linear units (ReLU) [26]. The second
hidden layer has a similar structure but with an output size of
110. The hidden layer can learn nonlinear functions for feature
extraction.
V. P ERFORMANCE E VALUATIONS
In this section, we present and discuss our experimental
results. Especially, we answer the following three research
questions:
RQ1: How effective is the traffic data processing scheme in
processing real-world raw traffic? (Section V-C)
• RQ2: How well does R ES GCN work on real-world network
traffic, identifying different network services? (Section V-D)
• RQ3: If R ES GCN achieves better performance than the
state-of-the-art methods? (Section V-E)

•

generated by ten anonymity services3 . There are 29,214 flows
and 6,979 flows in the training and test datasets, respectively.
To evaluate the generality of the classifier, we introduce
another real-world traffic dataset ISCXVPN2016 (D2 ) [29].
This dataset provides the traffic of different application services over virtual private network (VPN). VPN also provide
anonymity by creating a private network from a public internet
connection. Unlike Tor, I2P, and JonDonym, which are slow
and privacy-oriented, VPN is faster and more suitable for
daily tasks like casual browsing and streaming. A total of 7
application services (Browsing, FTP, VoIP, etc.) are included
in the selected dataset, and 28,395 flows are parsed for
classification. The ISCXVPN2016 dataset is divided into an
independent training dataset and test dataset according to the
proportion of 80% and 20%. Details of these two datasets are
summarized in TABLE I.
B. Experiment Setup
We design several experiments to evaluate the efficacy of
our method for classifying anonymity network traffic. To
answer RQ1, we evaluate the performance of the proposed raw
traffic data processing method on different flow segmentation
schemes and feature selection methods, and determine the
optimal combination for subsequent experiments. To answer
RQ2, we analyze the training process of R ES GCN, and
discuss the confusion matrix of the classification results on
the test dataset. To answer RQ3, we compare the classification
performance of R ES GCN and the state of the art of traffic
classification methods on the test dataset. It should be noted
that both AnonymityNet and ISCXVPN2016 datasets are used
to conduct the above evaluation experiments. To make the
experimental evaluation clearer, we introduce the experimental
environment and evaluation metrics as follows.
1) Experimental Environment: All the evaluations are conducted in Python 3.7 with the PyTorch framework of version 1.9.0 and running on the PC with Intel® Core™ i911900K@3.50 GHz, 64 GB RAM, and an NVIDIA GeForce
RTX3090 GPU.
2) Evaluation Metrics: To measure the classification performance of our method, we calculate the number of True
Positive (Tp ), True Negative (Tn ), False Positive (Fp ), and
False Negative (Fn ). Based on the above definition, Recall,
Precision and F1 can be obtained:
Recall =

Tp
,
Tp + Fn

(11)

A. Datasets for Evaluation
Currently, there are two mainstream datasets (i.e., ISCXTor2016 [27] and Anon17 [28]) for anonymity network traffic
analysis, released in 2016 and 2017, respectively. Due to
many changes in protocols and communication mechanisms
of anonymity networks over the years, these two datasets are
no longer suitable for the current anonymity network traffic
analysis. Thus, we use the latest SJTU-AN21 dataset (D1 ),
which includes the traffic data in the latest version of the three
most popular anonymity networks (i.e., Tor, I2P, JonDonym)

P recision =

F1 = 2 ·

Tp
,
Tp + Fp

P recision · Recall
.
P recision + Recall

(12)

(13)

Beside, Floating-Point-Operations (FLOPs) is used to evaluate
the model complexity.
3 SJTU-AN21 dataset: https://github.com/iZRJ/The-SJTU-AN21-Dataset

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:57 UTC from IEEE Xplore. Restrictions apply.

Accuracy on D1 [%]

Number of Features (Selected by XGBoost)

Number of Features (Selected by LightGBM)

Number of Features (Selected by PCA)

Number of Features (Selected by XGBoost)

Number of Features (Selected by LightGBM)

Accuracy on D2 [%]

Number of Features (Selected by PCA)

Fig. 5. Classification accuracy with different flow segmentation schemes and feature selection methods.

3) Hyper-parameter Configurations: For all the experiments in this section, we optimize the cross-entropy loss using
stochastic gradient descent (SGD) optimizer over 100 epochs.
The initial learning rate is set to 0.01 with the batch size 80
and a momentum of 0.9.
C. Efficacy of Raw Traffic Data Processing Scheme (to RQ1)
Our aim is to classify real-world anonymity network traffic
effectively, so it is not enough to design the classifier. After
capturing the raw traffic, different traffic data processing
schemes can significantly affect the classification performance.
In this stage, we conduct research on the following three main
influencing factors: flow segmentation, feature combination,
and flow sequence length.
We evaluate the performance of 6 segmentation schemes
(i.e., time-based 5s, 10s, 15s, and size-based 5MB, 10MB,
and 15MB) and 3 feature selection methods (i.e., PCA-based,
XGBoost-based, and LightGBM-based). XGBoost and LightGBM are both GBDT-based ML algorithms, which calculate
the gain of the j-th feature in the tree to reflect the feature
importance. The PCA algorithm reduces the data dimension by
maximizing the variance of the target dimension. We use the
training dataset for feature selection and evaluate the accuracy
of our method on the test dataset.
It can be seen from Fig. 5 that the 10s feature segmentation
scheme achieves the best classification performance on both
datasets, and the 15MB segmentation scheme has the worst
performance. Furthermore, through data analysis of the 15MB
flow segmentation scheme, it is found that the duration of
many flows using this segmentation scheme is very long, and
it is evident that the spatio-temporal correlation between flows
is weakened. Besides, in the comparison of feature selection
algorithms, the LightGBM-based method and the XGBoostbased method achieve higher maximum accuracy (MaxAcc)
than the PCA-based method. However, the performance of

TABLE II
P ERFORMANCE OF T HREE F EATURE S ELECTION M ETHODS .
Performance

PCA

XGBoost

LightGBM

MaxAcc1 [FN]
MaxAcc2 [FN]
Time (s)

85.60% [84]
94.03% [70]
4.17

86.56% [65]
94.36% [60]
62.9

87.31% [50]
95.37% [50]
11.11

1 MaxAcc and MaxAcc represent the maximum accuracy on Anonymi1
2

tyNe dataset and ISCXVPN2016 dataset, respectively.
2 FN represents the number of features with the maximum accuracy.

the PCA-based method is better when the number of features
is small, which is because the PCA method maps the original high-dimensional features to low-dimensional, so very
low-dimensionality can retain more information. TABLE II
comprehensively shows the performance of the three feature
selection methods. LightGBM-based feature selection method
achieves the highest MaxAcc on two datasets, and the number of features is 50. PCA method has achieved apparent
advantages in speed, but it is not satisfactory in terms of
accuracy. It can be concluded that the LightGBM-based feature
selection method has the best overall performance because of
its high accuracy and computational efficiency. Thus, we use
the LightGBM-based method to set the feature number to 50
with the LightGBM for subsequent experiments.
D. Performance of R ES GCN Classifier (to RQ2)
The train accuracy and loss using the R ES GCN model for
the two datasets are shown in Fig. 6. It can be seen that
the R ES GCN model learns the feature information of the
training dataset very well during the training process, which
has satisfactory performance in terms of accuracy and loss.
To comprehensively evaluate the classification performance
of R ES GCN, we analyze the confusion matrices of the classification results on the test datasets. As shown in Fig. 7,

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:57 UTC from IEEE Xplore. Restrictions apply.

1.0

Bro. Str. FTP Chat Bit. Jon. Vid. Sna. IRC Eep.

Loss [10-2]

Accuracy on D1 [%]

Confusion Matrix on D1

Number of Features

0.8

0.6

0.4
0.2

Eep. IRC Sna. Vid. Jon. Bit. Chat FTP Str. Bro.

(a) Training process on D1

(a) Confusion matrix of D1

Confusion Matrix on D2
Bro.

1.0

FTP

Accuracy on D2 [%]

0.0

0.6

0.4
0.2

Chat

Loss [10-2]

Str. Email VOIP P2P

0.8

Number of Features

Bro. FTP

P2P VOIP Email Str.

Chat

0.0

(b) Training process on D2

(b) Confusion matrix of D2

Fig. 6. Train accuracy and loss of R ES GCN model on two datasets.

Fig. 7. Performance confusion matrices of classifier on two datasets.

our classifier can effectively classify the traffic generated by
different services. On the AnonymityNet dataset, the traffic
of the three types of anonymity networks (i.e., I2P, Tor,
JonDoNym) is correctly distinguished. In terms of identifying
anonymity network services, services on I2P networks are
the most difficult to identify, and there have been some
misclassifications. On the ISCXVPN2016 dataset, we can see
that the classifier has some classification errors between the
FTP and Chat service traffic. By referring to the official
description of the ISCXVPN2016 dataset, we found that both
services contain the traffic generated by the Skype application,
which is the main cause of misclassification.
To further examine the level of benefit that each component
of R ES GCN brings to the performance, an ablation study is
performed on R ES GCN. The evaluation results are reported in
TABLE III. We also present the results of R ES CNN as a baseline, which uses residual CNN blocks with similar structures
to residual GCN blocks. First, the removal of GFI leads to
significant performance drops, which illustrates the necessity
of GFI for information interaction between generated features.
Compared with R ES GCN, R ES GCN w/o RFI is much less
powerful on two datasets. Thus it could be concluded that
RFI contributes to R ES GCN to a considerable extent since

RFI leverages the relationship graph of the flow sequence for
more reasonable and effective feature extraction. Moreover,
the performance of R ES GCN w/o RES (i.e., preserving GCN
units, but without residual structure) shows that the residual
structure can effectively avoid network degradation through direct signal transmission. The experimental results of R ES GCN
w/o GCN and the R ES CNN both prove that the GCN unit
plays a vital role in feature extraction of the flow sequence.
E. Comparison with Other Methods (to RQ3)
To comprehensively evaluate our model, we compare R ES GCN with a range of baselines and state-of-the-art models, as
listed below:
• NB, SVM, and C4.5 are implemented based on the
popular data mining tool Weka [30].
• CNN and LSTM models use the structure similar to R ES GCN (i.e., the same number of layers and input/output
size), and use flow sequences as input for classification.
• 2D-CNN proposed by Wang et al. [9] directly reads
traffic pcap files and converts them into grey images (size
of each image is 28×28) for classification.
• 3D-CNN is an improved model of the 2D-CNN proposed
by Zhang et al. [8], which uses multiple channels to

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:57 UTC from IEEE Xplore. Restrictions apply.

TABLE III
A BLATION S TUDY.
Model

AnonymityNet
Acc.
F1

ISCXVPN2016
Acc.
F1

R ES GCN
R ES CNN

87.3%
82.1%

87.4%
81.6%

95.4%
91.0%

95.4%
91.0%

R ES GCN w/o GFI
R ES GCN w/o RFI
R ES GCN w/o GCN
R ES GCN w/o RES

79.4%
81.9%
78.1%
81.0%

78.7%
81.6%
77.6%
80.6%

91.8%
88.9%
87.1%
92.4%

91.9%
89.1%
87.3%
92.5%

TABLE IV
T HE P ERFORMANCE C OMPARISON WITH OTHER M ETHODS .
Model

AnonymityNet
Acc.
F1

ISCXVPN2016
Acc.
F1

FLOPs
(106 )

Params
(104 )

Size
(KB)

Speed
(flows/ms)

NB
SVM
C4.5

34.0%
46.8%
48.4%

27.0%
42.8%
48.7%

54.7%
71.8%
78.5%

57.2%
72.0%
76.2%

N/A
N/A
N/A

N/A
N/A
N/A

N/A
N/A
N/A

18.3
56.8
113.6

CNN
LSTM
2D-CNN
3D-CNN
LAttn
FS-Net

78.3%
79.1%
65.0%
71.9%
81.5%
83.7%

77.0%
77.9%
66.9%
73.2%
81.1%
86.3%

90.2%
90.2%
86.2%
87.6%
92.3%
92.4%

90.4%
90.3%
86.1%
87.9%
92.3%
92.6%

46.5
114.6
1110.7
113.4
28.3
497.6

16.2
26.5
327.5
44.7
12.2
64.6

642
1,043
12,796
1,749
484
2,532

84.1
23.5
4.9
8.8
17.7
2.1

Ours

87.3%

87.4%

95.4%

95.4%

20.9

12.1

482

100.7

1 We highlight the best in • and the worst in •.
2 Speed is evaluated on CPU mode.
3 Since the three ML-based models are directly implemented and tested on the data mining tool Weka, the results of FLOPs, Params, and model size

cannot be obtained (marked N/A).

enrich feature information during image conversion. The
model input is the 3D tensor with the size of 22×22×3,
which can be visualized as 24-bit RGB images.
• LSTM+Attn proposed by Yao et al. [17] uses LSTM
combined with a self-attention mechanism to pay attention to important flows in the flow sequence.
• FS-Net is a LSTM-based network proposed by Liu et
al. [13] for encrypted traffic classification. This method
leveraged reconstruction loss to ensure that the extracted
features by LSTM contain more information of the raw
flow sequences.
TABLE IV shows the results of traffic classification performance. It can be seen that R ES GCN achieves the best
performance in both two datasets in terms of almost all evaluation metrics. We can observe that the classification results of
traditional ML-based methods are usually not ideal, demonstrating those methods’ limited abilities to classify complex
network traffic. The classification performance of the 2D-CNN
and 3D-CNN models (i.e., directly reading pcap files without
calculating the statistical features; see Section III-A) is very
limited. CNN, LSTM and LDAE all use statistical features
and the flow sequence to achieve significant performance
improvements. However, due to the lack of mining the inherent
relationship of the flow sequence, they still cannot achieve
high accuracy. The LAttn model learns the inherent relationship of the flow sequence through the attention mechanism,

and its performance is further improved. FS-Net achieves a
better feature representation of encrypted traffic by introducing reconstruction loss, effectively improving classification
performance. However, this model structure also brings a
larger amount of parameters. Our R ES GCN designs the model
structure from a brand-new perspective. It leverages generated
relationship graphs for feature extraction of flow sequence,
which significantly improves the classification performance on
anonymity network traffic.
Further, we analyze the model complexity, model parameter size, model size, and speed. These evaluations are very
important for some deployments, where a much smaller model
(or faster model that can analyze traffic in real-time) is more
important than the performance classification of a model
that, in the end, cannot be run on some devices. Since the
Memory and CPU usage are easily interfered with by other
programs, we use FLOPs to reflect the model complexity for
evaluating the hardware consumption of the running model.
The model parameter size also affects memory usage during
model inference. Besides, the model size indicates the disk
space occupied by this model, and the speed indicates the
number of flows that the model can process per millisecond.
We observe that, due to the use of 2D convolution for feature
extraction, both the 2D-CNN and 3D-CNN models are highly
complex. The complicated gate structure of the LSTM-based
model leads to very low computational efficiency. Thus, the

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:57 UTC from IEEE Xplore. Restrictions apply.

speed of the three LSTM-based models (i.e., LSTM, LAttn,
and FS-Net) is very slow. Benefiting from the effective feature extraction of flow sequences by GCN, R ES GCN can
achieve accurate classification without large parameters. We
also noticed that the C4.5 has a fast speed, but the subpar
classification performance limits its deployment. It can be
concluded that the R ES GCN classifier achieves the highest
classification accuracy as well as has low complexity and high
speed due to excellent structural design.
VI. C ONCLUSION
In this paper, we propose a novel flow sequence-based network traffic identification framework, which leverages R ES GCN to exploit attribute relationships and time relationships
between flows and successfully identifies different anonymity
network services. Moreover, as an end-to-end and real-time
traffic identification method, our framework can effectively
process real-world traffic. It takes into account flow segmentation, which is used to generate and enrich the flow
features from the raw traffic, and LightGBM-based feature
combination, which avoids the insignificant features from
reducing model performance and efficiency. The results of our
experiments show that the R ES GCN classifier achieves the
highest classification accuracy as well as has low complexity
and high speed due to excellent structural design.
ACKNOWLEDGMENT
This work was supported by the Foundation Item: Cyber Security from the National Key Research and Development Program of Shanghai Jiao Tong University under Grant
2019QY0703. Yijun Wang is the corresponding author.
R EFERENCES
[1] A. Montieri et al., “Anonymity services Tor, I2P, JonDonym: classifying
in the dark (web),” IEEE Transactions on Dependable and Secure
Computing, vol. 17, no. 3, pp. 662–675, 2020.
[2] Z. Cai, B. Jiang, Z. Lu, J. Liu, and P. Ma, “isAnon: Flow-based
anonymity network traffic identification using extreme gradient boosting,” in 2019 International Joint Conference on Neural Networks
(IJCNN), Budapest, Hungary, Jul. 14–19, 2019, pp. 1-8.
[3] L. Wang et al., “Multilevel identification and classification analysis of
Tor on mobile and PC platforms,” IEEE Transactions on Industrial
Informatics, vol. 17, no. 2, pp. 1079–1088, 2021.
[4] E. Papadogiannaki and S. Ioannidis, ”A survey on encrypted network
traffic analysis applications, techniques, and countermeasures,” ACM
Computing Surveys, vol. 54, no. 6, pp. 1–35, 2021.
[5] C. Fu, Q. Li, M. Shen, and K. Xu, ”Realtime robust malicious traffic
detection via frequency domain analysis,” in ACM SIGSAC Conference
on Computer and Communications Security (CCS), Virtual, Korea, Nov.
15 – 19, 2021, pp. 3431–3446.
[6] A. Khan, N. Hassan, C. Yuen, J. Zhao, D. Niyato, Y. Zhang, and H.
Vincent Poor, ”Blockchain and 6G: the future of secure and ubiquitous
communication,” IEEE Wireless Communications, vol. 29, no. 1, pp.
194–201, 2022.
[7] M. Shen, Z. Gao, L. Zhu, and K. Xu, “Efficient fine-grained website fingerprinting via encrypted traffic analysis with deep learning,”
in IEEE/ACM 29th International Symposium on Quality of Service
(IWQoS), Tokyo, Japan, Jun. 25–28, 2021, pp. 1-10.
[8] J. Zhang et al., “Autonomous unknown-application filtering and labeling
for DL-based traffic classifier update,” in IEEE Conference on Computer
Communications, Toronto, Canada, Jul. 6–9, 2020, pp. 397–405.

[9] W. Wang, M. Zhu, X. Zeng, X. Ye, and Y. Sheng, “Malware traffic
classification using convolutional neural network for representation
learning,” in 2017 International Conference on Information Networking
(ICOIN), Da Nang, Vietnam, Jan. 11–13, 2017, pp. 712–717.
[10] Y. Lin et al., “Time-related network intrusion detection model: a deep
learning method,” in 2019 IEEE Global Communications Conference,
Waikoloa, USA, Dec. 9–13, 2019, pp. 1–6.
[11] M. Shen et al., “Accurate decentralized application identification via encrypted traffic analysis using graph neural networks,” IEEE Transactions
on Information Forensics and Security, vol. 16, pp. 2367–2380, 2021.
[12] B. Sun et al., “An encrypted traffic classification method combining graph convolutional network and autoencoder,” in IEEE International Performance Computing and Communications Conference,
Austin, USA, Nov. 6–8, 2020, pp. 1–8.
[13] C. Liu et al., “FS-Net: A flow sequence network for encrypted traffic
classification,” in IEEE Conference on Computer Communications,
Paris, France, Apr. 29 – May 2, 2019, pp. 1171–1179.
[14] T. Ede et al., “FlowPrint: semi-supervised mobile-app fingerprinting on
encrypted network traffic,” in NDSS, San Diego, USA, Feb. 23–26, 2020,
pp. 1–18.
[15] J. Wang, J. Tang, Z. Xu, Y. Wang, G. Xue, X. Zhang, and D. Yang,
“Spatiotemporal modeling and prediction in cellular networks: A big
data enabled deep learning approach,” in IEEE Conference on Computer
Communications, Atlanta, USA, May 1–4, 2017, pp. 1-9.
[16] Y. Yan, L. Qi, J. Wang, Y. Lin, and L. Chen, “A network intrusion
detection method based on stacked autoencoder and LSTM,” in 2020
IEEE International Conference on Communications, Dublin, Ireland,
Jun. 7–11, 2020, pp. 1–6.
[17] H. Yao, C. Liu, P. Zhang, S. Wu, C. Jiang, and S. Yu, “Identification
of encrypted traffic through attention mechanism based long short
term memory,” IEEE Transactions on Big Data, doi: 10.1109/TBDATA.2019.2940675.
[18] H. He, X. Sun, H. He, G. Zhao, L. He, and J. Ren, “A novel multimodalsequential approach based on multi-view features for network intrusion
detection,” IEEE Access, vol. 7, pp. 183207–183221, 2019.
[19] A. Madhukar and C. Williamson, “A longitudinal study of P2P traffic
classification,” in IEEE International Symposium on Modeling, Analysis,
and Simulation, Monterey, USA, Sept. 11–14, 2006, pp. 179–188.
[20] A. Montieri et al., “A dive into the dark web: hierarchical traffic classification of anonymity tools,” IEEE Transactions on Network Science
and Engineering, vol. 7, no. 3, pp. 1043–1054, 2020.
[21] X. Li, W. Chen, Q. Zhang, and L. Wu, “Building auto-encoder intrusion
detection system based on random forest feature selection,” Computers
& Security, vol. 95, artcile number: 101851, 2020.
[22] Y. Dong, J. Zhao, and J. Jin, “Novel feature selection and classification
of Internet video traffic based on a hierarchical scheme,” Computer
Networks, vol. 119, no. 4, pp. 102–111, 2017.
[23] G. Ke, Q. Meng, T. Finley, T. Wang, W. Chen, W. Ma, Q. Ye, and T.
Liu, “LightGBM: A highly efficient gradient boosting decision tree,”
NIPS 2017, Long Beach, USA, Dec. 3–9, 2017, pp. 3149–3157.
[24] J. Bruna et al., “Spectral networks and locally connected networks on
graphs,” in 2014 International Conference on Learning Representations
(ICLR), Banff, Canada, Apr. 14–16, 2014, pp. 1-14.
[25] Z. Yu et al, “CodeCMR: cross-modal retrieval for function-level binary
source code matching,” NIPS 2020, pp. 3872-3883, 2020.
[26] V. Nair and G. Hinton, “Rectified linear units improve restricted boltzmann machines,” in 27th International Conference on Machine Learning
(ICML), Haifa, Israel, Jun. 21-24, 2010, pp. 807–814.
[27] A. H. Lashkari, G. D. Gil, M. S. I. Mamun, and A. A. Ghorbani,
“Characterization of tor traffic using time based features,” in 3rd
International Conference on Information System Security and Privacy,
Porto, Portugal, Feb. 19–21, 2017, pp. 253–262.
[28] K. Shahbar and A. N. Zincir-Heywood, “Packet momentum for identification of anonymity networks,” Journal of Cyber Security and Mobility,
vol. 6, no. 1, pp. 27–56, 2017.
[29] G. Draper-Gil, A. H. Lashkari, M. S. I. Mamun, and A. A. Ghorbani,
“Characterization of encrypted and vpn traffic using time-related,” in 2nd
International Conference on Information Systems Security and Privacy,
Rome, Italy, Feb. 19–21, 2016, pp. 407—414.
[30] M. Hall, E. Frank, G. Holmes, B. Pfahringer, P. Reutemann, and I. H.
Witten, “The weka data mining software: an update,” ACM SIGKDD
explorations newsletter, vol. 11, no. 1, pp. 10–18, 2009.

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:57 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
