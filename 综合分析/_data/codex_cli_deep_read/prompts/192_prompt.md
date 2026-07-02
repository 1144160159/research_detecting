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
# [192] Combine intra- and inter-flow: A multimodal encrypted traffic classification model driven by diverse features
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
编号：192
题名：Combine intra- and inter-flow: A multimodal encrypted traffic classification model driven by diverse features
年份：2024
DOI：10.1016/j.comnet.2024.110403
来源：Computer Networks
PDF：paper/10.1016_j.comnet.2024.110403.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\192.txt
- 原始字符数：66757
- 本次发送字符数：66757
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Computer Networks 245 (2024) 110403

Contents lists available at ScienceDirect

Computer Networks
journal homepage: www.elsevier.com/locate/comnet

Combine intra- and inter-flow: A multimodal encrypted traffic classification
model driven by diverse features
Xiangbin Wang a,b , Qingjun Yuan a,b ,∗, Yongjuan Wang a,b , Gaopeng Gou c,d , Chunxiang Gu a,b ,
Gang Yu a,b , Gang Xiong c,d
a

Information Engineering University, Zhengzhou, 450001, China

b Henan Key Laboratory of Network Cryptography Technology, Zhengzhou, 450001, China
c Institute of Information Engineering, Chinese Academy of Sciences, Beijing, 100093, China
d School of Cyber Security, University of Chinese Academy of Sciences, Beijing, 100093, China

ARTICLE

INFO

Keywords:
Encrypted traffic classification
Spectrogram
Graph convolutional network
Multimodal learning

ABSTRACT
The increasing prevalence of encryption for data security in network communication highlights the urgent
need for effective encrypted traffic identification methods. Challenges such as payload concealment, diverse
encryption protocols, and evasion tactics necessitate innovative approaches, including deep learning and
multiple features integration. Multimodal learning, which utilizes features from multiple sources, proves
more effective than single-modality methods, offering a more comprehensive analysis. However, current
methods often overlook valuable inter-flow information, hindering optimal classification. Hence, we propose
a novel multimodal encrypted traffic classification model driven by diverse features, named MeDF, which
combines intra- and inter-flow features. MeDF leverages both intra-flow and inter-flow features: it constructs
spectrograms of flows’ raw bytes and extracts statistical features, combining the two as the intra-flow
features. MeDF also builds flow relation graph to extracts inter-flow features, helping the model learn the
complex relationships between flows. The intra- and inter-flow features complement each other and extract
the maximum amount of valid information from encrypted traffic. Thus, MeDF overcomes the performance
limitations of existing multimodal models for encrypted traffic classification. MeDF is validated on 2 realworld traffic datasets with accuracy of 98.57% and 94.73%. The outperformance can be attributed to the
complementary information of the employed features and the modeling of complex relationships, when
compared to both classical single-modality classification methods and state-of-the-art multimodal methods.

1. Introduction
Network traffic classification is a crucial tool for network supervision [1,2]. In recent years, machine learning, particularly deep learning
methods capable of handling intricate data relationships and largescale data processing, has gained more preference over traditional
methods [3,4].
In order to fully unleash the potential of the model, it is typically
necessary to choose appropriate features from encrypted traffic data
for learning. We have summarized the types of features used in recent
network traffic classification works in Table 1. These features include
statistical feature, Temporal feature, original traffic and graph feature.
Statistical features of network flows, such as packet number, average packet size, and average arrival time, prompt the use of learningbased algorithms to model feature distributions for network flow classification [5–7]. Temporal features include the packet length sequence
and packet arrival interval sequence, treating flows as time series [8].

Some models use raw flow data, like L4 payload, as input, integrating feature/representation learning and classification into a unified
pipeline [6,7,9]. Handling these features typically involves the use of
CNN, MLP, ensemble learning, and Transformer models.
Additionally, when different network flows share common
attributes like IP, port, and protocol, these correlation features contribute to effective traffic classification. Often represented through
graph structures, these are referred to as graph features. It is crucial
to note that certain studies, despite using graph structures, represent
an individual flow with a single graph, deviating from the conventional understanding of graph features in this context [10–15]. GNN
is commonly used to learn graph feature.
It can be observed that the majority of methods for encrypted traffic
classification typically focus solely on one aspect of encrypted traffic
features [16,17]. This limitation hinders the full utilization of information from other aspects during classification, thereby weakening overall

∗ Corresponding author at: Information Engineering University, Zhengzhou, 450001, China.

E-mail addresses: Moskyes@outlook.com (X. Wang), gcxyuan@outlook.com (Q. Yuan), pinkywyj@163.com (Y. Wang).
https://doi.org/10.1016/j.comnet.2024.110403
Received 15 January 2024; Received in revised form 6 March 2024; Accepted 6 April 2024
Available online 8 April 2024
1389-1286/© 2024 Elsevier B.V. All rights reserved.

Computer Networks 245 (2024) 110403

X. Wang et al.
Table 1
Summary of the features used in recent network traffic classification work and our MeDF.
Feature
Intra-flow feature
Inter-flow feature
Model
Statistical feature
Temporal feature
Original traffic
Graph feature
1D-CNN [9]
✗
✗
✓
✗
✓
✗
✗
✗
XGBoost [5]
ACID [8]
✗
✓
✗
✗
✗
✗
✗
✓
ProGraph [13]
WTAGraph [15]
✗
✗
✗
✓
AppNet [6]
✓
✗
✓
✗
MIMETIC [7]
✓
✗
✓
✗
MeDF (Ours)
✓
✓
✓
✓

diversified feature representation method helps to improve the
model’s adaptability and generalization ability to new situations,
making the model more robust when encountering new data.

effectiveness. To address this, multimodal learning methods have been
introduced to the task of encrypted traffic classification. [6,7]
Multimodal learning, a technique integrating information from two
or more modalities, facilitates effective classification and prediction
[18]. In contrast to general encrypted traffic classification methods,
approaches based on multimodal learning can simultaneously leverage features from different perspectives of traffic, thereby enhancing
classification effectiveness. These approaches treat features as different
modalities and learn them using an appropriate model to combine
multiple sources of information for classifying encrypted traffic.
Network traffic inherently consists of multimodal data with diverse
features. The features fall into two main categories: intra-flow features
and inter-flow features. Intra-flow features consist of statistical characteristics of the traffic, raw bytes, etc. These features can be directly
quantified and represented in Euclidean space, constituting Euclidean
space features. They help capture the fundamental patterns and behaviors of the traffic, providing an intuitive feature representation for
classification tasks. Inter-flow features can be extracted from the structural or sequential characteristics of encrypted traffic. For instance,
relationships between flows in the traffic can be captured through
graph representation learning methods, which are more naturally represented in non-Euclidean spaces such as graph space, constituting
non-Euclidean space features. The diverse features enable multimodal
learning to be effectively applied to encrypted traffic classification
tasks.
Currently, many research studies focus on either intra-flow or interflow features exclusively. Our focus, however, lies on methods employing multimodal learning. Theoretically, multimodal learning necessitates complementary and heterogeneous characteristics among different modalities. Utilizing features meeting these criteria as modalities
enhances the information exchange between them, thereby improving
the effectiveness of multimodal learning. Despite the utilization of
multimodal learning in existing research, feature selection remains
limited to a single type of intra-flow feature. This constraint may hinder
the model’s ability to fully capture features from diverse perspectives
of network flows, potentially impacting classification performance.
Combining intra-flow and inter-flow features as Euclidean space and
non Euclidean space features respectively has certain advantages:

In this study, we introduce MeDF, a multimodal encrypted traffic classification model, driven by a diverse array of features. Our
approach emphasizes the simultaneous utilization of both intra-flow
and inter-flow features. Specifically, we employ statistical features and
time–frequency domain features as intra-flow features for network
flows, while graph features serve as inter-flow features. Given that traffic data inherently encompasses temporal features in both the time and
frequency domains, we treat these features as intra-flow components
within the Euclidean space. To comprehensively characterize features
in both domains, we leverage spectrograms, allowing us to address
the potential oversight of using only one aspect of the features and
mitigating the lack of information on the other.
Recognizing the necessity of non-Euclidean features, we introduce
the concept of a relation graph of flows to represent inter-flow features.
This supplementary representation in non-Euclidean space enhances
the model’s capacity to capture diverse aspects of network traffic
relationships. Our classification process entails the use of three distinct deep learning models, each specialized in learning one of the
three feature types. Subsequently, these models seamlessly integrate to
achieve a comprehensive classification outcome. This holistic approach,
combining Euclidean and non-Euclidean spaces, ensures our model
effectively addresses the intricate challenges associated with encrypted
traffic classification.
To the best of our knowledge, this is the first encrypted traffic
classification model that uses both of intra-flow and inter-flow features.
The main contributions of this study are as follows.
1. We construct a multimodal classification model MeDF. It can
make full use of the comprehensive information extracted from
inter-flow and intra-flow features, meeting the needs of multimodal learning for feature complementarity and heterogeneity.
2. We use the flow relation graph to characterize the inter-flow
features while spectrogram and statistical feature to characterize
the intra-flow features. These complementary features on both
aspects can provide more comprehensive information about encrypted traffic to the model. Therefore, MeDF can achieve better
classification result.
3. We validate the model on the real-world dataset and achieve
good results, proving that classification using both intra-flow
features and inter-flow features is highly effective.

1. Complementarity: Euclidean space features are typically suitable for capturing linear relationships and regular geometric
structures, while non Euclidean space features excel at handling
complex topological structures and nonlinear relationships. This
complementarity can enable the model to comprehensively understand and characterize encrypted traffic, and also meet the
requirements of multimodal learning.
2. Enhanced representation capability: By combining two spatial
features, the model can more flexibly represent different types
of data and relationships. This enhanced representation ability
helps to improve the generalization ability and accuracy of the
model.
3. Improving the generalization ability of the model: Non Euclidean
features can help the model capture deeper, non explicit data
structures and relationships, while Euclidean features can provide more intuitive and conventional data representations. This

The subsequent chapters of this paper are organized as follows:
Section 2 focuses on the works related to network traffic classification
and some basic knowledge required in this paper. Section 3 explains the
model framework of MeDF. Section 4 verifies the validity of the model
through experiments. Section 5 concludes the work of this paper.
2. Background and related work
Network traffic classification is one of the key research problems
in the field of network security. This section focuses on a review of
2

Computer Networks 245 (2024) 110403

X. Wang et al.

In our model, We use the spectrograms of flows as the representation of intra-flow features. Spectrograms can provide both time
domain and frequency domain attributes of flows, avoiding the lack of
information due to the use of only a single attribute. In addition, we
also utilize statistical features as supplementary information to ensure
that the model captures sufficient information from the traffic.

existing work, including the definition of network traffic classification (Section 2.1), feature-based classification methods (Section 2.2),
and current works related to encrypted traffic classification that use
multimodal learning (Section 2.3).
2.1. Definition of network traffic classification
Encrypted traffic classification refers to the identification of the
category to which the traffic belongs without decrypting the traffic,
such as the application generating the traffic or the purpose of the
traffic. The encrypted traffic classification is typically done at the
packet, flow, or session level. A flow is a set of packets represented by a
five-tuple, including destination IP, source IP, destination port, source
port, and protocol. A session refers to the bidirectional flow between
two network nodes over a period of time.
Assuming we have a set of encrypted traffic data  = (𝐱𝑖 , 𝑦𝑖 ), 𝑖 =
1, … , 𝑁, where 𝑁 is the number of samples, 𝐱𝑖 represents the feature
representation of the 𝑖th sample, and 𝑦𝑖 is the corresponding class label.
In multimodal learning, 𝐱𝑖 can be composed of data from multiple
modalities, such as raw bytes, packet size distributions, etc. Therefore,
𝐱𝑖 can be further represented as 𝐱𝑖 = (𝐱𝑖1 , 𝐱𝑖2 , … , 𝐱𝑖𝑀 ), where 𝑀 is the
number of modalities, and 𝐱𝑖𝑚 represents the feature representation of
the 𝑖th sample in the 𝑚th modality.
The structure of a multimodal learning model typically includes submodels that process features from each modality and a fusion network
that combines these features for final classification. In the context of
encrypted traffic classification, this can be represented as follows:
Modality feature extraction: For each modality 𝑚, there exists a
function 𝑓 𝑚 (⋅) to extract relevant features, i.e., 𝐳𝑖𝑚 = 𝑓 𝑚 (𝐱𝑖𝑚 ).
Modality fusion: After extracting the features𝐳𝑖1 , 𝐳𝑖2 , … , 𝐳𝑖𝑀 , these features are combined using a fusion function𝑓 (⋅), i.e., 𝐳𝑖 = 𝑓 (𝐳𝑖1 , 𝐳𝑖2 , … , 𝐳𝑖𝑀 ).
Classification: Finally, a classification function ℎ(⋅) is used to predict
the class from the fused features, i.e., 𝑦̂𝑖 = ℎ(𝐳𝑖 ).

2.2.2. Inter-flow-feature-based methods
Inter-flow features mainly refer to the relationship features in
network flows. Different network flows may have the same source/
destination IP, protocols, and representative work to construct flow relation graph, and train GNN to complete the classification of encrypted
traffic.
Yang et al. [15] propose WTAGRAPH, a network tracking and ad
detection framework based on Graph Neural Networks (GNN). We
first construct an Attribute Homogeneous Multigraph (AHMG) representing HTTP network traffic, and formulate network tracking and
ad detection as tasks of edge representation learning and classification based on GNN in AHMG. Li et al. [13] proposed ProGraph,a
graph-propagation-based method. It builds a correlation graph with
session clusters aggregated from different networks, upon which effective graph propagation can be implemented iteratively to predict
labels for test nodes. Cai et al. [23] proposed the MEMG method, which
combines Markov chains and graph neural networks to represent the
encrypted traffic of mobile applications as a first-order Markov chain
graph representation, transforming the encrypted traffic classification
problem into a graph classification problem.
Essentially, intra-flow features are features in Euclidean space,
which are the various properties of the encrypted flows themselves.
Meanwhile, inter-flow features are features on non-Euclidean space,
which can reflect the relationship between multiple network flows.
Our model combines these two types of features to classify encrypted
traffic. It can preserve the complete information of encrypted traffic
and optimize the classification effect.

2.2. Feature-based methods
2.3. Multimodal-learning-based methods
The primary concept of feature-based classification methods is to extract various types of features of network traffic and combine them with
classification algorithms, such as machine learning or deep learning, to
accomplish the classification of traffic. The existing feature-based work
can be categorized into two categories: methods based on intra-flow
features and methods based on inter-flow features.

Multimodal learning refers to the process of integrating information from several modalities, specifically, combining information from
multiple perspectives of an object, to perform classification. When
performing classification, a single modality typically cannot contain all
the valid information needed to produce accurate prediction results.
In contrast to from the general feature-based encrypted traffic classification methods, the approach of multimodal learning in encrypted
traffic classification aims to synthesize multiple features of traffic by
leveraging the concept of multimodal learning. The approach treats
different features of traffic as different modalities, and learn them using
models that are compatible with the modalities to unify multifaceted
information to complete the classification of encrypted traffic. Aceto
et al. proposed MIMETIC [7], a multimodal deep learning framework
that uses the first 576 bytes of payload and four protocol features as
input sources. The payload part is processed using a one-dimensional
CNN and the protocol feature part is processed using a lightweight
RNN structure GRU. Most previous approaches work by obtaining the
payload portion of the first packet or by piecing together a mixed
payload by extracting specific bytes from multiple packets, which lacks
feature information of the entire network flow.
Wang et al. proposed a multimodal encrypted traffic classification
framework, called AppNet. The framework uses a 1-D CNN to extract
features from the first 1014 bytes and uses LSTM to learn the temporal relationship of the packet length sequence, and finally connects
the features learned from both perspectives for classification [9]. Lin
et al. proposed PEAN [24], a model that takes raw bytes and length
sequences as input. It utilizes Transformer and bidirectional LSTM
as sub-models and employs self-attention mechanism to learn deep
relationships between network packets.

2.2.1. Intra-flow-feature-based methods
The methods based on intra-flow features can be categorized into
attribute-based features and sequence-based features. Among them,
attribute-based features include statistical features such as maximum
packet size, the average packet size of packets and string features
extracted directly from the flow.
Machine learning or deep learning algorithms can use these features
as input to classify encrypted traffic. Taylor et al. [19]. designed burst
and flow statistical features and proposed AppScanner for fingerprint
mobile applications. Chen et al. [20]. proposed Multi-Attribute Association Fingerprinting (MAAF) to classify mobile encrypted services.
MAAF uses domain names, certificates, and data length to predict the
application to which the encrypted flow belongs.
The sequence-based features of encrypted traffic include packet
length and message state sequences. Liu et al. [21]. used first-order
Markov chains to model packet length sequences and constructed a
multi-attribute Markov probabilistic fingerprint model MaMPF. Liu
et al. [22]. also designed a neural network model called Flowing
Sequence Network (FS-Net), which consists of an encoder, decoder,
and classifier. The encoder converts the input length sequence into
encoded features, while the decoder attempts to recover the sequence
by reconstructing the layers; the classifier uses the encoded features to
identify the application class of the flow.
3

Computer Networks 245 (2024) 110403

X. Wang et al.

Fig. 1. The framework of MeDF.

Numerous current encrypted traffic classification methods using the
multimodal learning use a combination of multiple intra-flow features.
Additionally there is a lack of research on using both intra-flow features
and inter-flow features for encrypted traffic classification. Therefore, in
this study, we consider using the time–frequency domain features of
flows as intra-flow features and the flow relation graph as inter-flow
features of encrypted traffic.

Algorithm 1: Framework of MeDF
Input: Several pcap files containing 𝑚 flows in total
Output: Classification results
Initialize 𝑀 as an empty set;
Let 𝑖 = 𝑚;
3 Intra-Flow features extraction:
4 while 𝑖 > 0 do
5
Extract the raw byte sequence 𝐑𝐁𝐒𝐢 of 𝐟 𝐥𝐨𝐰𝐢 ;
6
Generate the spectrogram 𝐬𝐩𝐞𝐜𝐢 of 𝐑𝐁𝐒𝐢 ;
7
Extract the statistical features vector 𝐬𝐟 𝐯𝐢 of 𝐟 𝐥𝐨𝐰𝐢 ;
8
Input 𝐬𝐩𝐞𝐜𝐢 and 𝐬𝐟 𝐯𝐢 into CNN and MLP respectively, and
obtain sub-modalities 𝑚1𝑖 and 𝑚2𝑖 ;
9
Let 𝑀1𝑖 = 𝑓 (𝑚1𝑖 , 𝑚2𝑖 ),where 𝑓 is the modality fusion
function;
10
𝑖 = 𝑖 − 1;
1
2

3. Description of MeDF
This section introduces MeDF, the proposed encrypted traffic classification model. This model mainly consists of four parts: Traffic
data preprocessing, Inter-flow features extraction, Intra-flow features
extraction and classification module, as shown in Fig. 1. It aims to
achieve the integration of intra-flow and inter-flow features to meet the
requirements of multimodal learning for modality complementarity and
heterogeneity. To achieve this, we design two modules for extracting
preprocessed traffic features: one for intra-flow features and the other
for inter-flow features.
Specifically, we construct a flow relationship graph to reflect the
connections between different flows and utilize graph convolutional
networks to extract inter-flow features. For intra-flow feature extraction, it involves two aspects: flow spectrogram and flow statistical
features. Since traffic can be considered a type of time series data, we
aim to use spectrograms to simultaneously capture its features in both
the time and frequency domains. Additionally, combining statistical
features, known for their universality and effectiveness, forms the intraflow features. Finally, we input both inter-flow and intra-flow features
into the classification module to complete the final classification. We
describe each module in detail as following.

Inter-Flow features extraction:
Build the relation graph 𝐺 of all the 𝑚 flows;
13 Input 𝐺 into GCN;
14 while 𝑖 > 0 do
15
Obtain the representation vector of the node 𝑖 as the
modality 𝑀2𝑖 ;
16
𝑖 = 𝑖 − 1;
11
12

Multimodal classification:
while 𝑖 > 0 do
19
Let 𝑀𝑖 = 𝑓 (𝑀1𝑖 , 𝑀2𝑖 );
20
Save 𝑀𝑖 to 𝑀;
21
𝑖 = 𝑖 − 1;

17
18

22

3.1. Traffic data preprocessing

23

The pcap data is divided into flows based on five tuples {source IP,
source port, destination IP address, destination port, protocol}. It is also
necessary to filter out the following three types of traffic.
4

Input 𝑀 into the classification model to obtain the 𝑟𝑒𝑠𝑢𝑙𝑡
return 𝑟𝑒𝑠𝑢𝑙𝑡

Computer Networks 245 (2024) 110403

X. Wang et al.

1. TCP Handshake Failed flows. The data packets of a failed
handshake do not carry with any valid application information
and does not provide valid information for the actual service
traffic identification. The TCP handshake failure packet does not
carry any valid application information and does not provide
valid information for actual service traffic identification. The
filtering criteria for this type of session is that the transport layer
protocol is TCP and the entire session handshake information is
incomplete or there is no service load.
2. DNS domain name query flows. The IP address and port of
the DNS server are generally different from the IP address and
destination port of the specific business traffic. Therefore, even
if a traffic service requires the use of a DNS service, its DNS
query traffic and the business-specific traffic will be divided
into different sessions when session segmentation is performed.
Separate DNS traffic sessions are less helpful for traffic type
identification. The traffic filtering criteria for this type of session
is that the entire session data packet is a DNS protocol packet.
3. LLMNR protocol flows. Application Scenarios for the LLMNR
Protocol Similar to the DNS protocol, DNS client computers can
use the LLMNR protocol to resolve names on local network
segments when DNS servers are unavailable.

Fig. 2. An example of the flow relation graph.

Algorithm 2: Construct Flow Relation Graph
Input: The set 𝐹 of flows; Each flow is represented as a triplet
{S_IP, D_IP, protocol}.
Output: The flow relation graph 𝐺.

The above three types of flows occur frequently in different types
of traffic and can be regarded as common background traffic [25,26].
However, they carry less effective information by themselves, which
is not conducive to the model’s extraction and learning of specific
business features of this type of traffic. Therefore, they are filtered out
in the data processing.

Function ConstructGraph(𝐹 ):
Initialize an empty undirected graph 𝐺;
3
for each flow {S_IP, D_IP, protocol} in 𝐹 do
4
Generate a unique node ID using S_IP, D_IP, and
protocol;
5
Add the node to graph 𝐺;

1

2

6

3.2. Inter-flow features extraction

7
8

This section describes the construction method of the network flow
relation graph used in the model.
The purpose of constructing the flow relation graph is to obtain
the inter-flow features of network flows, specifically whether there is
any correlation between flows. Therefore, we use flows as nodes in the
graph. In this process, the directionality between flows is not necessary,
so we use an undirected graph for construction, where edges represent
the existence of correlations between flows. Whether to add an edge
between nodes depends on the node attributes. The node attributes we
consider are the triplet source IP, destination IP, protocol. The specific
process is as follows:

9

for each node 𝑋 in graph 𝐺 do
for each node 𝑌 in graph 𝐺 do
if 𝑋 ≠ 𝑌 and S_IP or D_IP of 𝑋 is the same as 𝑌 , and
protocol is also the same then
return graph 𝐺;

Fig. 2 provides an example of a flow relation graph, which includes
8 nodes representing 8 flows., while the presence of an edge between
two nodes indicates that the source IP of one of these two network
flows is the same as the source/destination IP of the other flow, or the
destination IP of one flow is the same as the source/destination IP of
the other flow and they have the same protocol.

1. Create an empty undirected graph: First, initialize an empty
undirected graph G.
2. Add flows as nodes: Iterate through all flows, and for each flow,
add it as a node to the graph G. Each node represents a flow
and has three attributes: source IP, destination IP, and protocol.
Make sure each node has a unique identifier to distinguish
different flows.
3. Check flow attributes and add edges: For each flow node A in the
graph, iterate through all other flow nodes in the graph (B, C,
etc.). For each pair of flow nodes, perform the following checks:
if the source IP, destination IP set of flow A has common values
with the source IP, destination IP set of flow B, and they use the
same protocol, add an edge between node A and node B. This
edge represents the association between flow A and flow B.
4. Repeat the checking process: Continue to repeat step 3 for the
remaining flow nodes in the graph until all possible pairs of flow
nodes have been considered.
5. Complete the flow relationship graph: When all flows have been
traversed, and their relationships have been checked and added
to the graph, the undirected graph G is completed. This graph
represents flows as nodes and their relationships as edges.

3.3. Intra-flow features extraction
We use flow spectrograms as a representation of intra-flow features,
while using statistical features as supplements. The following will
explain them separately.
3.3.1. Flow time–frequency spectrogram generation
Network traffic data can be considered as a discrete time series, typically analyzed in the time domain in previous studies. This approach,
however, may not fully leverage the potential information within the
frequency domain, either because it is theoretically unavailable or
challenging to utilize when solely focusing on time domain analysis.
Conversely, relying solely on frequency domain information may result
in the loss of valuable information from the time domain.
Therefore, we use time–frequency spectrograms to depict the features of traffic in both the time and frequency domains. The traffic
in the time domain undergoes Fourier transform processing, resulting
in the generation of a time–frequency spectrogram for the traffic data.
This spectrogram encapsulates the distinctive features of the traffic data
in both time and frequency domains, facilitating the comprehensive
utilization of information within the traffic.
5

Computer Networks 245 (2024) 110403

X. Wang et al.

where 𝑖 ≤ 𝑗 ≤ 𝑁 − 𝑚 + 1, 𝑖 ≠ 𝑗. Calculate the template matching
probability of the subsequence 𝑋(𝑖):
[
]
𝑛𝑢𝑚 𝑑𝑖𝑗 < 𝑟
(10)
𝐵𝑖𝑚 (𝑟) =
𝑁 −𝑚
In turn, the average similarity can be calculated for all subsequences:
∑𝑁−𝑚+1 𝑚
𝐵𝑖 (𝑟)
𝑖=1
𝐵 𝑚 (𝑟) =
(11)
𝑁 −𝑚+1
Due to the length of the raw byte sequence of the flow is a finite
value, the sample entropy of the sequence is obtained as
]
[
𝐵 𝑚+1 (𝑟)
(12)
𝐒𝐚𝐦𝐩𝐄𝐧 (𝑠𝑒𝑞) = lim −𝑙𝑛 𝑚
𝑁→∞
𝐵 (𝑟)

We employ the short-time Fourier transform (STFT) to generate
spectrograms of flows. The STFT offers precise time–frequency resolution within a predetermined window of fixed size. In practical applications, the STFT is frequently computed using overlapping analysis
windows. These windows slide in a manner that introduces dependencies between adjacent windows, thereby mitigating the loss of accuracy
at boundary locations. Typically, the STFT function can be expressed as
STFT {𝑥 [𝑡]} (𝑚, 𝜔) ≡ 𝑋 (𝑚, 𝜔)
=

+∞
∑

𝑥 [𝑡] 𝑤 [𝑡 − 𝑚𝐻] 𝑒−𝑗𝜔𝑡

(1)

−∞

where 𝑥(𝑡) denotes the input data sampled at time 𝑡, 𝑤[𝑡] is the sliding
window, 𝜔 denotes the phase, 𝑚 signifies the position of the window,
and 𝐻 is the overlap constant when the window is sliding continuously.
The STFT possesses linearity property, defined by
{
}
{
}
STFT 𝑎𝑥1 [𝑡] + 𝑏𝑥2 [𝑡] = 𝑎 ⋅ STFT 𝑥1 [𝑡]
(2)
}
{
+𝑏 ⋅ STFT 𝑥2 [𝑡]

The analysis indicates that the calculation of sample entropy in
the time domain is linear, while the Fourier transform possesses the
property of maintaining linear operations. Therefore, following the
short-time Fourier transform and considering the introduction of noise,
the information entropy in the frequency domain representation of
the flow byte sequence does not surpass that of the time domain
representation. Consequently, the information entropy of the flow byte
sequence in the time–frequency spectrogram representation exceeds
that of the time domain representation. From this, we can obtain the
following inequality.

In order to avoid complex calculations and preserve the most relevant information, it is common practice to process only the magnitude
of the STFT. This results in a joint representation of the time and
frequency domains, i.e., spectrogram. It is defined as
spectrogram {𝑥 [𝑡]} (𝑚, 𝜔) ≡ |𝑋 (𝑚, 𝜔)|2

(3)

When applied to characterize network traffic, for a flow, we take
the first 𝑛 bytes of it to form a byte sequence and use 𝐹 as the
representation of this flow in the time domain. Considering that the
byte sequence is a discrete time series, it is necessary to perform a
discrete Fourier transform on each window. In this case, the STFT can
be represented as

𝐒𝐚𝐦𝐩𝐄𝐧 (𝑠𝑒𝑞) < 𝐭𝐟 𝐄𝐧 (𝑠𝑒𝑞) ≤ 2 ⋅ 𝐒𝐚𝐦𝐩𝐄𝐧 (𝑠𝑒𝑞)

where 𝐭𝐟 𝐄𝐧 (𝑠𝑒𝑞) represents the entropy of the sequence in the time–
frequency domain.
3.3.2. Supplement with statistical features
In the context of network traffic classification, statistical features
are utilized to enhance the process of encrypting traffic. Statistical
features involve analyzing various characteristics and patterns within
the encrypted traffic data. These features may include packet size
distribution, inter-arrival time, payload length, and statistical moments
such as mean and variance.
By leveraging statistical features, the encrypted traffic can be categorized into different classes or types, allowing for more accurate
identification and classification. These features can be extracted from
the encrypted traffic data and utilized in machine learning algorithms
or statistical models to train and build classifiers.
The utilization of statistical features in encrypting traffic classification provides a robust and reliable method to differentiate various types
of encrypted traffic.
We use statistical features as a supplement to spectrograms, and
together they form the intra-flow features. They mainly include the
following categories:

STFT {F [𝑖]} (𝑚, 𝜔) ≡ 𝑋 (𝑚, 𝜔)
=

+∞
∑

F [𝑖] 𝑤 [𝑖 − 𝑚𝐻] 𝑒−𝑗𝜔𝑖

(4)

−∞

where F [𝑖] denotes the 𝑖th sample point, 1 ≤ 𝑖 ≤ 𝑛. And the spectrogram
is
spectrogram {F [𝑖]} (𝑚, 𝜔) ≡ |𝑋 (𝑚, 𝜔)|2

(5)

The spectrogram can be seen as a two-dimensional visual representation of time and frequency domain information. It simultaneously
reflects information from both the time and frequency domains, as
opposed to the one-dimensional representation in the time domain.
Here, we examine the flow’s spectrogram using information entropy
theory. The encrypted flow is treated as a time series, and we apply
the sample entropy method to gauge its information content. Sample
entropy quantifies the complexity of a time series, indicating the likelihood of new information occurring. It measures the probability of new
information in a conditional manner: the more complex the time series,
the higher the sample entropy. This metric can effectively reflect the
information content in a two-way packet size sequence.
For a sequence of flow bytes of length 𝑁,
{𝑏(1), 𝑏(2), 𝑏(3), … , 𝑏(𝑁)}

1. Packet size distribution: Statistics on the size distribution of
individual packets in encrypted traffic, including mean packet
size, median packet size, mode packet size, standard deviation,
percentiles, kurtosis and skewness.
2. Inter-arrival time: Statistics on the time intervals between individual packets in encrypted traffic, such as mean interval,
variance and maximum interval.
3. Payload length: Statistics on the length distribution of the payload in encrypted traffic,including forward byte count and packet
count, backward byte count and packet count, as well as corresponding maximum, minimum, average, variance, and standard
deviation. The payload refers to the actual effective data carried
in the packet, excluding the header or encryption parts.
4. Byte sent rate: The rate at which data is sent in bytes over a
certain period of time, including the total sent rate, forward sent
rate, and back sent rate.
5. Usage of encryption algorithms: The encryption algorithm suites
and protocol types used in encrypted traffic.

(6)

Let the similarity comparison threshold be 𝑟 and the subsequence
length metric be 𝑚. The original sequence is reconstructed so that
(𝑁 − 𝑚 + 1) subsequences can be obtained as
{𝑋(1), 𝑋(2), 𝑋(3), … , 𝑋(𝑁 − 𝑚 + 1)}

(7)

Each subsequence is denoted as
𝑋(𝑖) = 𝑏(𝑖), 𝑏(𝑖 + 1), … , 𝑏(𝑖 + 𝑚 − 1)

(13)

(8)

For any subsequence 𝑋(𝑖) we can define its distance from subsequence 𝑥(𝑗) as
{
}
|
||
𝑑(𝑖𝑗) = 𝑚𝑎𝑥 |𝑏𝑖 (𝑘) − 𝑏𝑗 (𝑘)| |𝑏𝑖 (𝑘) ∈ 𝑋(𝑖), 𝑏𝑗 (𝑘) ∈ 𝑋(𝑗)
(9)
|
||
6

Computer Networks 245 (2024) 110403

X. Wang et al.

Fig. 3. The framework of inter-flow features extractor.

3.4. Classification module
After obtaining the inter-flow and intra-flow features, we use models
that adapt to them respectively for learning, and then complete the final
classification using multimodal learning method.
Inter-flow Features Learning We use the GCN model to extract
the flow relationship features in flows. GCN is a neural network
model specifically designed for processing graph structured data. It
performs convolution operations on the graph, effectively capturing
local neighborhood information and global topology structure between
nodes [27].
The model we used is shown in Fig. 3. It contains 3 graph convolutional layers and one fully connected layer. We use the cross-entropy
loss function, and the result of this part of the loss function is noted as
𝐿𝑜𝑠𝑠𝐼𝑛𝑡𝑒𝑟 , and the obtained feature extraction result is 𝑀𝐼𝑛𝑡𝑒𝑟 .
𝐿𝑜𝑠𝑠Inter = −

𝑛
∑
(
)
( (
))
𝑝 graph𝑖 log 𝑞 graph𝑖

Fig. 4. The framework of intra-flow features extractor.

layers use 3 Convolutional kernel of 3, with a step size of 1 and padding
of 1 and all pooling layers are Maximum pooling of 2, with a step size
of 2 and no padding.
We use multi-layer perceptron(MLP) to learn statistical features.
This MLP model contains three hidden layers. The statistical features
of encrypted traffic are obtained by summarizing, calculating, or combining the original features, which may contain complex nonlinear
relationships. MLP can automatically learn complex interactions and
combination relationships between features through multiple layers of
weight combinations and activation functions. It has strong nonlinear
modeling ability and can better capture information in the statistical
features [29].
The structure of the two model is shown in Fig. 4. For both models,
we use cross entropy loss functions defined as, where the final loss
function is the sum of the two loss functions, defined as

(14)

𝑖=1

We use two parallel graph convolutional layers, where these two
layers employ different aggregation functions: sum and max, respectively. This approach allows the two graph convolutional layers to
capture different feature representations from the graph. It aids the
model in capturing a more diverse set of node features, thereby enhancing the model’s understanding and representational capacity of the
graph.
Intra-flow Features Learning After obtaining the spectrograms
representation of the flows, we use CNN to learn them. Spectrograms
often contain many local structures, such as changes in frequency
and instantaneous changes in time. CNN is capable of automatically
learning these local features through convolutional layers. Moreover,
by utilizing multiple convolutional and pooling layers, CNN can progressively extract more abstract and higher-dimensional features [28].
Thus, CNN can better capture the complex structures and patterns
within spectrograms.
The CNN model we used referred to VGG16. VGG16 is a convolutional neural network model widely used in the field of image
processing. This network model has a total of 16 layers, including 13
convolutional layers and 3 fully connected layers. In order to reduce
the amount of parameters and computation, we have replaced some
convolutional layers with depthwise separable convolution(DSC) layers
and reduced the number of layers in the network. All convolutional

𝐿𝑜𝑠𝑠CNN = −

𝑛
∑
(
)
( (
))
𝑝 𝑠𝑝𝑒𝑐𝑡𝑖 𝑙𝑜𝑔 𝑞 𝑠𝑝𝑒𝑐𝑡𝑖

(15)

𝑖=1

𝐿𝑜𝑠𝑠MLP = −

𝑛
∑
( )
( ( ))
𝑝 𝑓𝑖 𝑙𝑜𝑔 𝑞 𝑓𝑖

(16)

𝑖=1

𝐿𝑜𝑠𝑠Intra = 𝐿𝑜𝑠𝑠CNN + 𝐿𝑜𝑠𝑠MLP

(17)

We use the cross-entropy loss function, and the result of this part of the
loss function is noted as 𝐿𝑜𝑠𝑠𝐼𝑛𝑡𝑟𝑎 , and the obtained feature extraction
result is 𝑀𝐼𝑛𝑡𝑟𝑎 .
Multimodal fusion The outputs of the three sub-models are fused
in a cascading manner. Specifically, GCN is used to process the flow
relation graph, obtaining the representation vectors for each node as
inter-flow features. MLP and CNN are respectively used to process
the statistical features and spectrogram of the encrypted traffic. And
their output vectors are concatenated to obtain a representation vector.
Finally, the two representation vectors are concatenated to obtain the
7

Computer Networks 245 (2024) 110403

X. Wang et al.

Table 2
The composition of the Malicious_TLS dataset.

final representation vector, which is input into the fully connected layer
for classification.
We combine the previously extracted features 𝑀Intra and 𝑀Inter for
classification through the fully connected layer and softmax layer, also
using the cross-entropy loss function, denoted as 𝐿𝑜𝑠𝑠mf . We want
the neural network to utilize both the intra-flow features and interflow features so that they can complement each other. In order to
achieve the best classification effect of the model, we assume that the
final classification effect will be optimal when the inter-flow features
extraction module, the intra-flow features extraction module and the
classification module all reach the optimal parameters. Therefore, the
final loss function 𝐿𝑜𝑠𝑠𝑎𝑙𝑙 of the whole model is
𝐿𝑜𝑠𝑠all = 𝐿𝑜𝑠𝑠Intra + 𝐿𝑜𝑠𝑠Inter + 𝐿𝑜𝑠𝑠mf

Category

Flow count

Arachni
Awvs
Burpsuite
Shifu
Tiggre
Tor
Benign

2000
2000
2000
2000
2000
2000
4000

Table 3
The composition of the ISCX VPN-nonVPN dataset.

(18)

In multimodal learning, the weights of each modality’s loss function
represent the importance of that modality. To ensure that intra- and
inter-flow features receive equal attention during model training, we
set the weights of the loss functions for these two modalities to be the
same.

Category

Flow count

Chat
Mail
File Transfer
Streaming
Torrent
VoIP

31 334
24 719
67 790
36 128
169 309
53 040

4.2. Experiment setup
4. Experiment

This section describes the configuration of the experimental environment we used, the evaluation metrics and the baseline.

This section presents the network traffic dataset used for the experiments as well as the implementation details, evaluation metrics, and
baseline methodology. Also in this section, encrypted traffic classification experiments are performed for all models, including quantitative
evaluation, ablation studies, and sensitivity analysis, to comprehensively and specifically evaluate the performance of MeDF.

(1) Environment Settings: The computer specifications used in the
experimental environment are as follows: Intel Core i7-9700K CPU,
Nvidia 3080 GPU, 32 GB RAM, and Windows operating system. The
experiments are conducted based on the PyTorch 1.11.0 framework and
implemented in the Python language of version 3.7.13.
(2) Evaluation Metrics:In this paper, Accuracy, Recall, False Positive
Rate (FPR) and Precision are used to assess the performance of the
model and are calculated as follows.

4.1. Dataset

TP + TN
TP + TN + FP + FN
TP
TPR =
TP + FN
FP
FPR =
FP + TN
TP
Precision =
TP + FP

Accuracy =
We used two publicly available datasets:ISCX VPN-nonVPN 2016
[30] and Malicious_TLS [31]. The former is a commonly used dataset
in encrypted traffic recognition research, while the latter is used to
evaluate the performance of MeDF in malicious traffic classification.
We do not use the entire traffic data for training models when using
these two datasets.

(19)
(20)
(21)
(22)

where TP, FP, TN and FN denote true positive, false positive, true
negative and false negative, respectively.

The Malicious_TLS dataset includes traffic generated by 22 active
malicious code families from 2018 to 2021, as well as some benign
traffic. All of this traffic is collected from real networks and encrypted
through TLS. We selected six types of malicious traffic and some benign
traffic for our experiment. The composition of the dataset is shown in
Table 2.

(3) Baseline: To better evaluate the performance advantages and
disadvantages of the MeDF proposed in this paper, we selected 6
currently well-performing encrypted traffic classification models as,
two of which use unimodal learning and the other two use multimodal
learning.

The ISCX VPN-nonVPN dataset comprises 14 categories of regular
traffic (non-VPN) and VPN traffic (including VOIP, VPNVOIP, P2P,
VPN-P2P, etc.), encompassing various types of traffic such as browsing,
VoIP, streaming, chatting, email, and more. The dataset has a size of
approximately 28 GB, and for the analysis, six labeled categories of
regular traffic were used. The available dataset composition is outlined
in Table 3.

1 D-CNN An end-to-end classification method that converts bytes to
image grayscale values and then classifies traffic using 1 D-CNN [9].
XGBoost A decision tree model that is an implementation of the
Gradient Boosting algorithm and is widely used in various machine
learning tasks [5].
ACID A clustering model for encrypted traffic classification [8].
ProGraph A graph neural network based encrypted traffic classification model [13].

In practical scenarios, network traffic may contain various types of
data, including malicious traffic and regular traffic. Malicious traffic
and regular traffic often have different characteristics and behavioral
patterns. Therefore, testing on these two types of traffic can help determine the effectiveness of the model. Additionally, using these two types
of traffic for experimentation can evaluate the model’s generalization
ability. Therefore, testing the model using these two types of traffic can
better simulate real-world application scenarios and ensure the model’s
usability in a real environment.

AppNet A multimodal deep learning framework that uses the packet
length sequence of the initial packet and the payload bytes as input. The
former is modeled using Bi-LSTM and the latter using 1D-CNN [6].
MIMETIC A multimodal deep learning framework also using 4 protocol fields extracted from the bi-directional flow and payload bytes of
the initial packet as input, the former modeled using GRU (a simplified
version of LSTM) and the latter modeled using 1-D CNN [7].
8

Computer Networks 245 (2024) 110403

X. Wang et al.
Table 4
Comparison of classification results on Malicious_TLS (%).
Models

Accuracy

Recall

FPR

Precision

1D-CNN
XGBoost
ACID
ProGraph
AppNet
MIMETIC

92.37
90.29
96.13
91.55
95.52
96.73

91.76
90.17
95.87
91.34
95.30
96.32

0.31
0.37
0.22
0.33
0.27
0.26

90.78
90.21
95.98
91.39
95.52
96.29

MeDF (Ours)

98.57

98.62

0.22

98.14

Table 5
Comparison of classification results on ISCX VPN-nonVPN 2016 (%).
Models

Accuracy

Recall

FPR

Precision

1D-CNN
XGBoost
ACID
ProGraph
AppNet
MIMETIC

89.68
88.32
92.73
94.35
90.17
91.56

89.25
88.27
92.48
94.54
90.34
91.45

0.42
0.41
0.30
0.30
0.34
0.32

89.17
89.06
91.63
93.89
90.28
90.89

MeDF (Ours)

94.73

94.56

0.28

93.86

4.3. Comparison of classification results
The comparison of the classification performance of different models is shown in Tables 4 and 5, respectively, for the experimental results
on Malicious_TLS and ISCX VPN-nonVPN 2016.
MeDF achieves the best classification results of all the approaches. It can be seen that the multimodal models AppNet, MIMETIC,
and MeDF have improved in accuracy compared to the unimodal 1DCNN model on both datasets. This indicates that the multimodal models
are able to learn the information in the encrypted traffic data more fully
after obtaining more than one class of feature inputs, which leads to
better classification results. Similar to the 1D-CNN model, MeDF also
converts the raw byte information of the flow into images and then
analyzes them. The difference between 1D-CNN and MeDF is that 1DCNN converts flows into grayscale spectrograms and uses 1D CNN for
analysis, while MeDF converts flows into time–frequency spectrograms
and uses 2D convolution for analysis, in addition to adding inter-flow
relationship information, thus achieving better results.
In addition, compared to AppNet and MIMETIC models, MeDF has
further improvement in classification accuracy, which we consider because MeDF combines both inter-flow features and intra-flow features
modalities.MIMETIC uses the first 576 bytes of payload and 4 protocol
features as input; AppNet extracts features from the first 1014 bytes of
the first packet features from the first 1014 bytes of the first packet, as
well as the time-relative features of the packet length sequence. The
different modalities used by these two models are essentially interflow features. MeDF, on the other hand, uses features embedded in the
flow-relations graph to complement the inter-flow features of encrypted
traffic in addition to the inter-flow features using the time–frequency
graph to characterize it. This indicates that using both intra-flow features and inter-flow features can achieve better complementary effects
when using modality fusion methods for encrypted traffic classification,
and thus optimize the classification results.

Fig. 5.

Confusion matrices of MeDF on two datasets.

4.4. Flow spectrogram
For each flow, we extract the first 500 raw bytes of it as the input
of the STFT. For flows less than 500 bytes in length, we pad with 0
to complete 500 bytes. The IP addresses are masked. For the STFT,
there are some key parameters that need to be set in advance, including
window length, window overlap rate, and window function, etc. The
window length we use is 100, with a overlap rate of 67%, and the
window function is the Hanning window.
Fig. 6(a) shows the intuitive representation of the original byte
stream in the time domain, where the horizontal axis represents time
and the vertical axis represents the corresponding bytes. Fig. 6(b) shows
the spectrogram, where the horizontal axis represents time, the vertical
axis represents frequency.
The spectrogram can be viewed as a two-dimensional visual representation of the joint function of time domain information and
frequency domain information of a network flow. Unlike the onedimensional representation of the network flows in the time domain,
the spectrogram representation of the network flows can reflect the

The confusion matrices of MeDF on two datasets for classification
are given by Fig. 5. It can be observed that on Malicious_TLS, MeDF
achieves close to 1 prediction accuracy across all categories, while on
ISCX VPN-nonVPN, the accuracy for each category is almost all below
95%. We attribute this to the more complex data structure of ISCX
VPN-nonVPN compared to Malicious_TLS. Additionally, the weaker
correlation between flows leads to less prominent inter-flow features,
resulting in a decrease in the model’s classification accuracy.
9

Computer Networks 245 (2024) 110403

X. Wang et al.
Table 6
Ablation study results (%).
Models

Accuracy

Recall

FPR

Precision

MeDF
intra-MeDF
inter-MeDF

98.57
96.82
90.25

98.62
92.76
89.92

0.22
0.31
0.97

98.14
95.79
90.27

Table 7
Complexity of feature extraction.

Spectrogram
Flow relation graph

Time complexity

Space complexity

𝑂 (NM𝑙𝑜𝑔M)
( )
𝑂 V2

𝑂 (NM)
𝑂 (E)

4.5. Ablation study
In this section, we further illustrate the effectiveness of combining
inter-flow features and intra-flow features for multimodal learning by
constructing 2 weakened models of MeDF.
We construct two weakened models, one is to remove the interflow features extraction module from the original model and use only
the intra-flow features extraction module and classification module for
classification, called intra-MeDF; the other is to remove the intra-flow
features extraction module from the original model and use only the
flow relation graph and GCN model for classification, called interMeDF. We conducted experiments on the Malicious_TLS dataset and
obtained the results as shown in Table 6.
Both aspects of the modality extracted by MeDF are useful. And
intra-flow features are better for traffic classification than inter-flow
features we used. It can be seen that there is a significant decrease
in the classification accuracy of both weakened models compared to
MeDF: the accuracy of intra-MeDF decreased by 1.75% compared to
MeDF, while the accuracy of inter-MeDF decreased by 8.32% compared
to MeDF. The other three indicators of MeDF are also better than the
weakened models. It indicates that the inter-flow features and intraflow features of network traffic are able to complement each other in
the modality fusion process.
By comparing intra-MeDF and inter-MeDF, the accuracy, recall
and precision of inter-MeDF decreased by 6.57%, 2.84% and 5.52%
respectively compared to intra-MeDF. We think that it is because
when constructing the flow relation graph, we did not use too much
information about the network flows themselves, mainly retaining the
correlation features between flows. Therefore, using only flow relation
graph for node classification to complete traffic classification is not
effective enough. When using intra-flow features to complete classification, it contains more information about the network flow, thus
achieving better classification results.

Fig. 6. The representations of flow in different domains.

Fig. 7. The spectrograms of different applications.

4.6. Complexity analysis
In this section, we analyzed the complexity of MeDF, including time
complexity, space complexity, the number of model parameters and run
time per-epoch.

information of the encrypted traffics in both the time and frequency
domain.

(a) Complexity of feature extraction
In this part, we analyze the time and space complexity of feature
extraction in MeDF, including the construction of spectrogram and flow
relation graph. The result is as shown in the Table 7.
The method we use to construct the spectrogram is the STFT,
which involves dividing the original signal into multiple windows and
performing Fast Fourier Transform (FFT) on each window. Assuming
the length of the original signal is 𝑁 and the window length is M, the
time complexity of FFT is 𝑂 (M𝑙𝑜𝑔M). For STFT, since FFT needs to be
performed on different time windows, the overall time complexity is
𝑂 (NM𝑙𝑜𝑔M). The space complexity depends on the memory required to
store the time–frequency spectrograms. For STFT, it typically requires

Spectrogram is a more effective way to characterize network
flows than 1D time-series In the STFT process, the features are
already ‘‘pre-extracted’’. The amount of information of the features
characterized by a single point in the spectrogram is larger than that of
a single point in the one-dimensional temporal bits. So it is easier for
the classifier to use its information for feature characterization.
Fig. 7 shows the spectrograms of some malicious traffics in the
dataset we used. It can be seen that the time–frequency spectrograms
of different types of encrypted traffic have more obvious differences,
which also confirms the effectiveness of using time–frequency diagrams
to characterize the time–frequency domain of encrypted traffic.
10

Computer Networks 245 (2024) 110403

X. Wang et al.
Table 8
Model complexity.

Data availability

Model

Parameter size (millions)

RTPE (s)

MeDF (Ours)
MIMETIC

2.54
1.78

47.5
39.4

The data used in the article are all publicly available data and have
been cited.
Acknowledgments

storing the spectral information for each time window. Therefore, the
space complexity can be approximated as 𝑂 (NM).
When constructing a flow relation graph, as we need to iterate
over all subsequent flows for each flow, the time complexity can be
represented as the total computation of a nested loop. Assuming there
are V flows, the first flow needs to iterate over the remaining (V − 1)
flows, the second flow needs to iterate over the remaining (V − 2) flows,
and so on, until the second-to-last flow needs to iterate over the last
flow. Therefore, the total computation can be represented as:

This work is supported by The National Key Research and Development Program of China No. 2023YFB2705000, and The Blockchain
system security Key technology research of Henan Province Major
public welfare Project No. 201300210200. The authors would like to
thank the reviewers for their valuable comments that helped to improve
this manuscript.
References
[1] Ankit Thakkar, Ritika Lohiya, A survey on intrusion detection system: feature
selection, model, performance measures, application perspective, challenges, and
future research directions, Artif. Intell. Rev. 55 (2021) 453–563.
[2] Bhoopesh Singh Bhati, C.S. Rai, Analysis of support vector machine-based
intrusion detection techniques, Arab. J. Sci. Eng. 45 (4) (2020) 2371–2383.
[3] Thijs van Ede, Riccardo Bortolameotti, Andrea Continella, Jingjing Ren, Daniel J.
Dubois, Martina Lindorfer, David R. Choffnes, Maarten van Steen, Andreas Peter,
FlowPrint: Semi-supervised mobile-app fingerprinting on encrypted network traffic, in: Proceedings 2020 Network and Distributed System Security Symposium,
2020, pp. 1–18.
[4] Wisam Elmasry, Akhan Akbulut, Abdul Halim Zaim, Evolving deep learning
architectures for network intrusion detection using a double PSO metaheuristic,
Comput. Netw. (ISSN: 1389-1286) 168 (2020) 107042.
[5] Zhe Wang, Baihe Ma, Yong Zeng, Xiaojie Lin, Kaichao Shi, Ziwen Wang,
Differential preserving in xgboost model for encrypted traffic classification, in:
International Conference on Networking and Network Applications, 2022, pp.
220–225.
[6] Xin Wang, Shuhui Chen, Jinshu Su, App-net: A hybrid neural network for encrypted mobile traffic classification, in: IEEE INFOCOM 2020 - IEEE Conference
on Computer Communications Workshops, 2020, pp. 424–429.
[7] Giuseppe Aceto, Domenico Ciuonzo, Antonio Montieri, Antonio Pescapé,
MIMETIC: Mobile encrypted traffic classification using multimodal deep learning,
Comput. Netw. 165 (2019) 106944.1–106944.12.
[8] Alec F. Diallo, Paul Patras, Adaptive clustering-based malicious traffic classification at the network edge, in: IEEE INFOCOM 2021 - IEEE Conference on
Computer Communications, 2021, pp. 1–10.
[9] Wei Wang, Ming Zhu, Jinlin Wang, Xuewen Zeng, Zhongzhen Yang, End-to-end
encrypted traffic classification with one-dimensional convolution neural networks, in: IEEE International Conference on Intelligence and Security Informatics,
2017, pp. 43–48.
[10] A.V.D. van Deventer, R.S. Holz, A.N. Zincir-Heywood, A novel method for
encrypted traffic classification using N-gram-based techniques, IEEE Trans. Inf.
Forensics Secur. 12 (10) (2017) 2207–2220, http://dx.doi.org/10.1109/TIFS.
2017.2717945.
[11] Mohamed A. Khedr, Bassant M. El Bagoury, Alaa M. Riad, et al., Automated traffic classification and application identification using machine
learning, in: 2017 IEEE Conference on Dependable and Secure Computing,
IEEE, 2017, pp. 491–498, http://dx.doi.org/10.1109/DASC-PICom-DataComCyberSciTec.2017.242.
[12] A.V.D. van Deventer, R.S. Holz, A.N. Zincir-Heywood, Encrypted traffic classification using machine learning techniques: A case study with netflix traffic, in:
IEEE Conference on Local Computer Networks, LCN, IEEE, 2016, pp. 226–229,
http://dx.doi.org/10.1109/LCN.2016.91.
[13] Wenhao Li, Xiao-Yu Zhang, Huaifeng Bao, Haichao Shi, Qiang Wang, ProGraph:
Robust network traffic identification with graph propagation, IEEE/ACM Trans.
Netw. 31 (2023) 1385–1399.
[14] J. Zhang, Y. Xiang, Y. Wang, W. Zhou, Y. Xiang, Y. Guan, Network traffic
classification using correlation information, IEEE Trans. Parallel Distrib. Syst.
24 (1) (2013) 104–117.
[15] Zhiju Yang, Weiping Pei, Mon-Chu Chen, Chuan Yue, WTAGRAPH: Web tracking
and advertising detection using graph neural networks, in: IEEE Symposium on
Security and Privacy, 2022, pp. 1540–1557.
[16] Wenhao Li, Huaifeng Bao, Xiao-Yu Zhang, Lin Li, Amdetector: Detecting largescale and novel android malware traffic with meta-learning, in: International
Conference on Conceptual Structures, 2022, pp. 387–401.
[17] Wenhao Li, Xiao-Yu Zhang, Gblnet: Detecting intrusion traffic with multigranularity bilstm, in: International Conference on Conceptual Structures, 2022,
pp. 380–386.
[18] Peng Xu, Xiatian Zhu, David A. Clifton, Multimodal learning with transformers:
A survey, IEEE Trans. Pattern Anal. Mach. Intell. 45 (2022) 12113–12132.

(23)
(
)
V(V−1)
This is the sum of an arithmetic progression, and its sum is
.
2
( 2)
Therefore, the computational complexity is 𝑂 V .
The flow relation graph can be stored in the form of a sparse matrix.
The number of edges is much smaller than the square of the number of
nodes, resulting in a space complexity of 𝑂 (E), where E is the number
of edges in the flow relation graph.
[(V − 1) + (V − 2) + ⋯ + 1]

(b) Model complexity
In this part, we analyze the number of model parameters and RTPE
of two multimodal learning models. The result is as shown in the
Table 8.
It can be seen that MeDF has an increase in both parameter size
and RTPE compared to MIMETIC. This is because, in order to obtain
more comprehensive feature information, the model of MeDF is more
complex than MIMETIC. Due to the significant improvement in classification performance of MeDF, these additional costs are acceptable.
5. Conclusion
In this paper, we propose an encrypted traffic classification model
based on multimodal fusion, called MeDF. We mainly consider interflow features and intra-flow features when selecting features of network
traffic, in order to allow the classification model to learn information
about multiple aspects of traffic. We validated the effectiveness of
our model on a real-world encrypted traffic dataset and were able
to achieve an accuracy of over 98%, superior to multimodal learning
methods that use only intra-flow features. This shows that the combination of intra-flow and inter-flow features is effective. Moreover,
compared to MeDF using only intra-flow features and only inter-flow
features, the accuracy is improved by 2.62% and 9.19% when using
both features, respectively. This further illustrates the necessity of using
both intra- and inter-flow features for multimodal flow classification.
CRediT authorship contribution statement
Xiangbin Wang: Writing – original draft, Validation, Software,
Methodology, Conceptualization. Qingjun Yuan: Writing – review &
editing, Methodology, Formal analysis, Conceptualization. Yongjuan
Wang: Writing – review & editing, Validation, Methodology. Gaopeng
Gou: Methodology, Validation, Writing – review & editing. Chunxiang
Gu: Methodology, Validation. Gang Yu: Methodology, Formal analysis.
Gang Xiong: Writing – review & editing, Methodology.
Declaration of competing interest
The authors declare that they have no known competing financial interests or personal relationships that could have appeared to
influence the work reported in this paper.
11

Computer Networks 245 (2024) 110403

X. Wang et al.
[19] V.F. Taylor, R. Spolaor, M. Conti, I. Martinovic, AppScanner: Automatic fingerprinting of smartphone apps from encrypted network traffic, in: IEEE European
Symposium on Security and Privacy, (EuroS&P), 2016, pp. 439–454.
[20] J. Zhang, X. Chen, Y. Xiang, W. Zhou, J. Wu, Robust network traffic
classification, IEEE/ACM Trans. Netw. 23 (3) (2015) 1257–1270.
[21] C. Liu, L. He, G. Xiong, Z. Cao, Z. Li, FS-net: A flow sequence network for
encrypted traffic classification, in: IEEE INFOCOM 2019 - IEEE Conference on
Computer Communications Workshops, 2019, pp. 1171–1179.
[22] M. Shen, M. Wei, L. Zhu, M. Wang, Classification of encrypted traffic with
second-order Markov chains and application attribute bigrams, IEEE Trans. Inf.
Forensics Secur. 12 (8) (2017) 1830–1843.
[23] Wei Cai, Gaopeng Gou, Minghao Jiang, Chang Liu, Gang Xiong, Zhen Li, MEMG:
Mobile encrypted traffic classification with Markov chains and graph neural
network, in: HPCC/DSS/SmartCity/DependSys, 2021, pp. 478–486.
[24] Peng Lin, Kejiang Ye, Yishen Hu, Yanying Lin, Chengjie Xu, A novel multimodal
deep learning framework for encrypted traffic classification, IEEE/ACM Trans.
Netw. 31 (2023) 1369–1384.
[25] Khalid Shahbar, Nur Zincir-Heywood, How far can we push flow analysis to
identify encrypted anonymity network traffic? in: NOMS 2018 - 2018 IEEE/IFIP
Network Operations and Management Symposium, 2018, pp. 1–6.
[26] Riyad Alshammari, Nur Zincir-Heywood, Machine learning based encrypted
traffic classification: Identifying SSH and skype, in: 2009 IEEE Symposium on
Computational Intelligence for Security and Defense Applications, 2009, pp. 1–8.
[27] Ling Zhao, Yujiao Song, Chao Zhang, Yu Liu, Pu Wang, Tao Lin, Min Deng,
Haifeng Li, T-GCN: A temporal graph convolutional network for traffic prediction,
IEEE Trans. Intell. Transp. Syst. 21 (2018) 3848–3858.
[28] Linshan Jia, Tommy W.S. Chow, Yixuan Yuan, GTFE-net: A gramian time
frequency enhancement CNN for bearing fault diagnosis, Eng. Appl. Artif. Intell.
119 (2023) 105794.
[29] Ibrahim Masood, Statistical features-MLP neural network for recognizing bivariate spc chart patterns, Int. J. Adv. Trends Comput. Sci. Eng. 8 (1.3) (2019)
87–91.
[30] Gerard Draper-Gil, Arash Habibi Lashkari, Mohammad Saiful Islam Mamun,
Ali A. Ghorbani, Characterization of encrypted and VPN traffic using timerelated features, in: International Conference on Information Systems Security
and Privacy, 2016, pp. 312–315.
[31] Qing jun Yuan, Chang Liu, Wentao Yu, Yuefei Zhu, Gang Xiong, Yongjuan
Wang, Gaopeng Gou, Boau: Malicious traffic detection with noise labels based
on boundary augmentation, Comput. Secur. 131 (2023) 103300.

Yongjuan Wang received the Ph.D. degree from Information Engineering University in 2009. She currently works
at Information Engineering University. Her main research
interests include cryptographic analysis and cyberspace
security.

Gaopeng Gou received the Bachelor, M.Eng. and Ph.D.
degrees from Beihang University in 2005, 2008 and 2014,
respectively. He is currently a full professor in the Institute
of Information Engineering, Chinese Academy of Sciences,
China. His research interests include network security and
network anomaly detection.

Chunxiang Gu received the Ph.D. degree s Ph.D. degrees
from Information Engineering University. He is currently
a professor of Information Engineering University. His research interests include network security and cryptographic
analysis.

Gang Yu received the Ph.D. degree s Ph.D. degrees from
Information Engineering University. His research interests
include network security and blockchain applications

Xiangbin Wang received the M.Eng. degrees from Information Engineering University, China, in 2021. He is currently
a graduate student studying for a Ph.D. in Information Engineering University, China. His research interest is network
security.

Gang Xiong is currently a Full Professor and Ph.D. Supervisor with the Institute of Information Engineering, Chinese
Academy of Sciences, China. He has authored more than
60 papers in refereed journals and conference proceedings.
His research interests include network and information
security. He is a member of the 3rd Communication Security
Technical Committee of China Institute of Communications.

Qingjun Yuan received the M.Eng. degrees and Ph.D. from
Information Engineering University, China, in 2016 and
2023. His research interests include network security and
side channel attack.

12
PAPER_TEXT
