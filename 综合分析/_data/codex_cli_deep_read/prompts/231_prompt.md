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
# [231] GCN-MHSA: A novel malicious traffic detection method based on graph convolutional neural network and multi-head self-attention mechanism
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
编号：231
题名：GCN-MHSA: A novel malicious traffic detection method based on graph convolutional neural network and multi-head self-attention mechanism
年份：2024
DOI：10.1016/j.cose.2024.104083
来源：Computers & Security
PDF：paper/10.1016_j.cose.2024.104083.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：恶意流量、暗网与攻击检测
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\231.txt
- 原始字符数：85256
- 本次发送字符数：85256
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Computers & Security 147 (2024) 104083

Contents lists available at ScienceDirect

Computers & Security
journal homepage: www.elsevier.com/locate/cose

GCN-MHSA: A novel malicious traffic detection method based on graph
convolutional neural network and multi-head self-attention mechanism
Jinfu Chen a,b , Haodi Xie a,b , Saihua Cai a,b ,∗, Luo Song a,b , Bo Geng a,b , Wuhao Guo c
a
b
c

School of Computer Science and Communication Engineering, Jiangsu University, 301 Xuefu Road, Zhenjiang, 212013, Jiangsu, China
Jiangsu Key Laboratory of Security Technology for Industrial Cyberspace, Jiangsu University, 301 Xuefu Road, Zhenjiang, 212013, Jiangsu, China
Asiainfo Security Technology Co., Ltd Nanjing, 210012, Jiangsu, China

ARTICLE

INFO

Keywords:
Malicious traffic detection
Graph convolutional neural network
Multi-head self-attention mechanism
Feature extending

ABSTRACT
With the increasing size and complexity of network, network traffic becomes more and more correlated with
each other, and the traditional manner of presenting network traffic in a Euclidean structure is difficult
to effectively capture the correlation information of network traffic. In contrast, graph structured data has
gained much attention in recent years due to its ability to represent the correlation between different traffic
flows; In addition, models and algorithms related to Graph Convolution Neural network (GCN) have been
used for malicious traffic detection. However, existing GCN-based malicious traffic detection methods still
suffer from incomplete description of the flow-level features of network traffic, imperfect traffic correlation
establishment mechanism and failure to distinguish the importance of features during model training. Based on
this, this study proposes a malicious traffic detection method called GCN-MHSA based on Graph Convolutional
Neural network and Multi-Head Self-Attention mechanism. Firstly, the flow-level features of network traffic
are populated and more information close to the features are selected to describe the network traffic; And
then, the link homogeneity is used to establish the correlations between network traffic; Moreover, multi-head
self-attention mechanism is introduced in the GCN model to provide larger weight to important features;
Finally, an improved GCN is used as a deep learning model to detect malicious traffic. Extensive experimental
results on three publicly available network traffic datasets and a real network traffic dataset show that the
proposed GCN-MHSA method performs better than five baselines in terms of detection effect and stability,
with an improvement of about 2.4% in accuracy, recall and F1-measure as well as an improvement of about
2.1% in precision.

1. Introduction
With the popularization of Internet, the scale of network traffic
shows a continuous growth trend, and the complexity of network traffic
is also increasing. Complex network architecture allows hackers to
utilize more avenues for malicious attacks or performing abnormal
behaviors, such as the communication in computer networks with
attack behavior (Eswaran and Faloutsos, 2018) and the spread of false
information in social networks (Gupta et al., 2012), which brings
great challenges to network security. Compared with normal access,
malicious attacks often generate malicious traffic with attack attributes,
thus, we can identify the type of malicious attacks through detecting
traffic and then take relevant measures to defend against network
threats (Chen et al., 2023c). However, in real life scenarios, an access to a web page by users may trigger the download of multiple

resources and a response of a service may require multiple requests
and responses, which leads to the strong correlation of network traffic
reflecting users’ operations. These correlated flows create complex
interactions and dependencies in the network, therefore, understanding
and analyzing such correlations can provide a more comprehensive
view, which can help to more accurately detect malicious traffic. Graph
structure can pay better attention on the correlation between network
traffic due to its strong information expression ability, and some common dynamic networks, such as social networks, transaction networks
for transferring money between accounts and computer communication
networks, are all represented by graph-structured data. However, traditional malicious traffic detection methods based on recurrent neural
network, convolutional neural network and their variants are not applicable to the detection task oriented to graph structure. Therefore,

∗ Corresponding author at: School of Computer Science and Communication Engineering, Jiangsu University, 301 Xuefu Road, Zhenjiang, 212013, Jiangsu,
China.
E-mail addresses: jinfuchen@ujs.edu.cn (J. Chen), 2222108039@stmail.ujs.edu.cn (H. Xie), caisaih@ujs.edu.cn (S. Cai), 2212108063@stmail.ujs.edu.cn
(L. Song), 2212308011@stmail.ujs.edu.cn (B. Geng), guo.wuhao@asiainfo-sec.com (W. Guo).

https://doi.org/10.1016/j.cose.2024.104083
Received 24 December 2023; Received in revised form 11 July 2024; Accepted 26 August 2024
Available online 30 August 2024
0167-4048/© 2024 Elsevier Ltd. All rights are reserved, including those for text and data mining, AI training, and similar technologies.

Computers & Security 147 (2024) 104083

J. Chen et al.

2. Related work

how to build graph structures for the correlated network traffic and
effectively detect malicious traffic with the help of graph structures that
can better reflect the correlation of network traffic, has become a hot
research topic.
In recent years, researchers tried to use graph neural network models to detect malicious traffic in large-scale network traffic. However,
the existing researches on of network flow-level characterization still
remains in the 5-tuple features of network traffic (including: source
IP, source port, destination IP, destination port, protocol), which leads
to the fact that these methods cannot fully reflect the complexity of
network traffic characterization in the representation of traffic information (Sun et al., 2020). The existing methods also suffer from the
problems of incomplete traffic correlation mechanism and not focusing
on important features, which means that they may not be able to fully
capture the correlations and interactions between different nodes in
traffic data (Zheng et al., 2022). The incomplete correlation mechanism
may cause the model ignoring some important information and patterns
when analyzing network traffic, thus affecting its performance and
accuracy. Moreover, existing methods fail to pay sufficient attention
on important features when dealing with network traffic (Chen et al.,
2023a). There is a large amount of information in network traffic
data, but not all features are equally important to our study or task,
while current methods may underutilize some key features due to
not accurately evaluate and select the importance of features, thereby
affecting the performance and accuracy of the model (Niu et al., 2022).
To address the problems of existing methods, we first propose a
feature extending scheme to describe the network traffic as much detail
as possible. More specifically, we extend the original network traffic
features in the feature preprocessing stage and extract 12-tuple features
of network traffic, where the source IP and port, the destination IP and
port are used as two node features of in the graph structure, and other
features such as the number of incoming and outgoing bytes, the number of incoming and outgoing packets, and the interval time are used as
the edge features in the graph structure. In the constructing of graph
structure for network traffic, we also consider the link homogeneity
between network traffic (i.e., the similar network traffic may originate
from same application) as well as further introduce the indirect correlation and direct correlation between network traffic to assign different
weights to different degrees of correlation, thereby fully reflecting the
correlation information between network traffic and take advantages of
graph structure data. After constructing network traffic graph structure,
we combine the Graph Convolutional Neural network and a MultiHead Self-Attention mechanism to form an effective malicious traffic
detection method called GCN-MHSA, thereby further improving the
stability of detection model and the detection efficiency of malicious
network traffic.
The main contributions of this paper are as follows:

Malicious traffic detection aims to detect abnormal network traffic
from large-scale network traffic to seek for the attack behavior or
unusual operations, it is an important aspect of network security.
With the development of artificial intelligence, machine learning, deep
learning and graph neural network techniques have been widely used
in malicious traffic detection.
2.1. Machine learning-based malicious detection methods
Machine learning-based malicious detection methods distinguish
malicious traffic from normal traffic by learning the features of network traffic usingmachine learning models. For example, Moore and
Zuev (2005) proposed a Bayesian classifier-based malicious detection
method, it had high detection accuracy, but the time consumption used
in feature extraction process is very high. Zhang et al. (2018) proposed
a network intrusion detection method that combines Principal Component Analysis (PCA) and Gaussian naive Bayes to detect malicious
traffic, it weighted the first few features obtained by traditional PCA
to reduce the data dimension, thereby reducing the time consumption.
Alshammari and Zincir-Heywood (2009) conducted a large number
of experiments and found that using C4.5 classification can improve
the detection accuracy and robustness on SSH and Skype networks
compared with Adabost, Naive Bayes and RIPPER, but this approach
produced a high false positive rate. Okada et al. (2011) proposed an
EFM method based on SVM to detect malicious traffic from encrypted
traffic with an overall accuracy of 97.2%, but this method did not
consider the optimal combination of features for network traffic. Shams
and Rizaner (2018) introduced a network traffic intrusion detection
tool using support vector machine, which significantly improved network reliability by detecting and removing malicious nodes in the
network. In 2016, Anderson and McGrew (2016) proposed a supervised
machine learning model, it combined context information and observable data in the network traffic to detect malicious traffic. Wu et al.
(2021) preprocessed network packets by collecting network traffic data,
system logs, user behavior and host information, and then used random
forest algorithm to train the data; In addition, they also calculated the
importance of features to reduce data dimensionality. Barradas et al.
(2021) developed the Flowlens, it relied on programmable switches
to collect flow distribution information on the data-plane for feature
extraction and detected the attacks by applying a random forest algorithm. However, this method did not consider the external relationships
between traffic flows, which may limit its effectiveness in capturing
complex network behaviors and interactions. Holland et al. (2021)
proposed nPrint, a tool that generated a unified packet representation
by using the maximum header length allowed for each protocol and
concatenating different protocol headers into a fixed-length header,
it integrated the nPrint with automated machine learning (AutoML)
for automatically classifying network traffic. However, nPrint offered
only a little assistance in extracting flow-level sequence information,
which limited its effectiveness in feature extraction of network traffic.
In recent years, several studies have made significant contributions
to the field of real-time malicious traffic detection. For example, Fu
et al. (2021) developed the Whisper leveraging frequency domain features, it realized the robust and real-time detection in high throughput
network. Zhou et al. (2023) proposed a multi-phase sequential model
architecture, this method introduced a new paradigm for the joint design and deployment of intelligent network models and programmable
network hardware. Fu et al. (2023) proposed the HyperVision, an
unsupervised graph learning method, which used the DBSCAN and KDTree to analyze the connectivity, sparsity and statistical features of the
graph for flow interaction patterns, thereby detecting the unknown patterns in encrypted malicious traffic. Compared with these methods, the
GCN-based methods require the construction of extensive graph structures and entail higher computational overhead, they offer a distinct

1. We extend the traditional 5-tuple flow-level features of network
traffic into 12-tuples to describe the network traffic with richer
information.
2. We introduce the indirect and direct correlations between network traffic using link homogeneity between network traffic
and assign different weights to different degrees of correlation,
thereby more effectively describing the correlations between
network traffic.
3. We introduce the multi-head self-attention mechanism into
graph convolutional neural network to provide larger weight
for more important features, thereby improving the stability and
detection efficiency of malicious network traffic method.
The remainder of this paper is organized as follows. Section 2
presents the related work on malicious traffic detection. Section 3
describes the proposed GCN-MHSA method, including the preprocessing of network traffic, the establishment of graph structure, and the
construction of GCN-MHSA method. Section 4 makes an experimental
comparison between the proposed GCN-MHSA method and state-of-theart methods. Finally, Section 5 concludes this paper and discusses the
future work.
2

Computers & Security 147 (2024) 104083

J. Chen et al.

schemes and model optimization. For example, Kipf and Welling (2017)
proposed a scalable semi-supervised GNN-based learning method, it
directly acted on GNN structure based on an effective variant of CNN
to effectively improve the detection efficiency. Fang et al. (2022)
proposed a switching aware spatio-temporal GNN model based on
dynamic graph convolution and gated linear unit to predict the traffic
consumption in short, medium and long time frames, but this method
could not obtain a hybrid graph structure with detailed information
about network traffic. After a lot of analysis, Zola et al. (2022) found
that the key to malicious traffic detection is not only to detect a
single malicious connection, but also to detect which node in the
network is generating malicious traffic in many cases, and then they
tool corresponding measures to reduce the threat and improve the
network security of system; However, this method had a bad detection
efficiency problem due to the lack of denoising processing on network
traffic. Xiao et al. (2023) proposed a control area network-based graph
attention network (CAN-GAT) model to realize anomaly detection for
in-vehicle network, and then proposed a malicious detection framework
based on graph convolution network and graph attention network to
detect anomalies in CAN bus in-vehicle network, but the detection
stability of this method needs to be further verified. Guo et al. (2020)
proposed a GNN-based anomaly detection algorithm, it introduced
graph structure, attribute and dynamic change information into the
model to learn the representation vector of anomaly detection, but
the operation efficiency of this method needs to be improved. Zheng
et al. (2022) proposed an encrypted malicious traffic detection method
called GCN-ETA based on graph convolutional network as well as a
new traffic representation and correlation construction scheme, but the
traffic direction and the weights of different correlation types were
not considered in the traffic correlation. Lan et al. (2022) proposed
E-minBatch, a model based on GraphSAGE, it took the application
layer source port and source IP address as the source node, the application layer target port and target IP address as the target node,
and the remaining traffic information as the edge information, thereby
completing the construction of graph structure, but this method was
limited to the detection of industrial Internet traffic. Jiang et al. (2022)
designed a new trust evaluation framework called GATrust based on
GAT, it could assign different attention coefficients to various attributes
of users in online social networks and improve the prediction accuracy
of social trust evaluation; However, the generality of this method on
graph structure data needs to be verified. Niu et al. (2022) proposed
a method based on adaptive online analysis to accurately determine
malware via analyzing the encrypted, drifting and unbalanced network
traffic. The GNN-based model Euler (King and Huang, 2022) belonged
to unsupervised method, it utilized the temporal graph link prediction
to incorporate the temporal nature of data along with GNN model for
anomaly-based intrusion detection. The unsupervised learning method
Euler exhibited higher false positive rate and false negative rate in some
cases, it was owing to that unsupervised methods rely on the inherent
structure of the data without the guidance of supervised signals, making
them more susceptible to noise compared to supervised methods. (1)
In the feature extraction, the edges in the graph structure of Euler
model did not include any information of network traffic, they only
represented the existence of relationships between two entity nodes,
leading to the loss of much useful information. (2) Regarding the correlation between network traffic, Euler model treated all correlations
between network traffic uniformly and fails to account for the varying
degrees of relevance and importance among different network traffic,
it may hinder the effectiveness of malicious activities detection. (3) In
the training of the detection model, Euler had the advantage of not
requiring labeled data, it outperformed other unsupervised anomalybased intrusion detection methods; However, Euler model assigned
equal weights to each feature, this manner could significantly limit its
ability to capture the importance of different features.
In summary, the studies on GNN-based malicious detection have
become a hot research topic in recent years. However, the existing

advantage by capturing the complex dependencies and relationships
between different network traffic, leading to more effective detection
of malicious traffic.
In general, machine learning-based malicious traffic detection methods attempt to discriminate normal network traffic and malicious network traffic using machine learning models. Although this kind of
malicious traffic detection methods has made some progress, they
suffer from the following problems: (1) The feature extraction process
is time-consuming in large-scale networks and the dimensionality reduction techniques do not always preserve all essential information,
leading to the loss of potential information; (2) Most methods face high
false positive rate due to the need of feature extraction with greater
subjectivity.
2.2. Deep learning-based malicious detection methods
Compared with traditional machine learning-based malicious detection methods, deep learning-based models have the advantage of
directly extracting features from original network traffic, thus, it has
been widely used in the detection of malicious traffic in recent years.
For example, Prasse et al. (2017) proposed a long short-term memory
(LSTM)-based model to detect malware based on the Https traffic with
the focus on host address, timestamp and data information. Wang
et al. (2017a) proposed an automatic malware detection method, it
used the natural language processing to extract text features from
network traffic and then used the text features to construct an effective
malware detection model based on text semantic features. Wang et al.
(2017b) proposed a malicious traffic detection method based on onedimensional convolutional neural network (1D-CNN), but this method
only used spatial features and ignored temporal features. Marín et al.
(2019) used raw measurements of monitored byte streams as input
to the proposed model and evaluated different raw traffic representation to better capture the basic statistics of malicious traffic. In
addition, Chen et al. (2023b) proposed a malicious traffic detection
method based on temporal convolutional network (TCN), it used exponential linear units (ELU) activation function to solve the problem of
low detection accuracy caused by the neuron ‘‘death’’ in the training
process. Sun et al. (2020) developed an intrusion detection system
called DL-IDS with the use of hybrid network (containing CNN and
LSTM) to extract the spatial and temporal features of network traffic,
but its detection accuracy for some attack types needs to be improved. Wu et al. (2020) designed a LDoS attack classifier using HSMM
network model as well as proposed a LDoS attack detection method
based on wavelet energy spectrum entropy and hidden semi-Markov
model, they had better detection performance. Mirsky et al. (2018)
developed the Kitsune to learn the per-packet features by adopting
auto-encoders, it was an unsupervised method and could eliminate the
need for labeled datasets as well as was capable of handling zero-day
attacks. However, this packet-level method used the statistics as the
context information, resulting in unable to achieve robust detection
under evasion attacks.
In general, deep learning-based methods provide an effective way
to detect malicious network traffic, they also have better accuracy and
portability compared with traditional machine learning-based methods.
However, deep learning-based methods primarily focus on extracting spatial and temporal features from network traffic, these methods face the challenges in effectively capturing the intricate network
relationships and graph structures associated with malicious activities.
2.3. Graph neural network-based malicious detection methods
Considering the advantages of graph structure in representing network traffic, researchers have begun to study graph neural network
(GNN)-based models and algorithms in recent years. In GNN-based malicious traffic detection methods, researchers ensure the detection reliability through different data preprocessing methods, feature extraction
3

Computers & Security 147 (2024) 104083

J. Chen et al.
Table 1
The comparison of malicious traffic detection methods.
Method

Feature extraction

Using graph structure

Considering feature weights

Zhang et al. (2018)
Shams and Rizaner (2018)
Wang et al. (2017a)
Wang et al. (2017b)
Marín et al. (2019)
Zheng et al. (2022)
Lan et al. (2022)
Jiang et al. (2022)
Niu et al. (2022)
Sun et al. (2020)
GCN-MHSA (ours)

Processed
Processed
Direct
Direct
Direct
Direct
Direct
Direct
Processed
Direct
Direct

×
×
×
×
×
✓
✓
✓
×
×
✓

×
×
×
×
×
×
×
×
×
×
✓

Fig. 1. The workflow of GCN-MHSA method.

researches do not give a complete set of flow-level features to describe
network traffic and ignore the link homogeneity between network
traffic when establishing their correlation, which seriously affect the
efficiency of GNN-based malicious traffic detection methods. Therefore,
it is necessary to strengthen the preprocessing process of original network traffic, improve the attention to the correlation between network
traffic, enhance the effectiveness of GNN-based model in the training
phase and strengthen the attention on important features of network
traffic, thereby further improving the detection efficiency of malicious
traffic.
The comparison of some aforementioned malicious traffic detection
methods is shown in Table 1.

mechanism. The overall workflow of proposed GCN-MHSA method is
shown in Fig. 1.
Firstly, the basic preprocessing operations such as data segmentation, filtering and dumping are performed on the original network
traffic. Then, the features of processed network traffic are extracted
and extended with the flow-level features, and the selected features
are evaluated to ensure that the selected features have positive feedback. Next, the correlation between network traffic is established using
link homogeneity to assign different degrees for indirect and direct
correlations. Finally, different features are assigned different weights
through multi-head self-attention mechanism based on their importance to the determination of malicious traffic. With above operations,
the adjacency matrix, flow-level features and other information are
provided for the training of malicious traffic detection model to more
accurately detect malicious traffic. Compared with existing methods,
the proposed method extends the flow-level features of network traffic,
that is, selecting more information close to the features of network
traffic to describe it, as well as analyze the homogeneity between
network traffic, and then introduces the multi-headed self-attention
mechanism into GCN model to assign different weights for features.
Through these improvements, the effect of malicious traffic detection is

3. Proposed model
To solve the problems of existing GCN-based malicious traffic detection methods, such as the incomplete description of flow-level features
of network traffic, the incomplete traffic correlation mechanism and
not focusing on important features in the model training process, we
propose a malicious traffic detection method called GCN-MHSA based
on graph convolution neural network and multi-head self-attention
4

Computers & Security 147 (2024) 104083

J. Chen et al.

improved while fully considering the relevant information and features
between network traffic.
3.1. The preprocessing of network traffic based on feature extending and
network correlation analysis
The GCN-based malicious traffic detection method can use the traffic trajectory graph to construct graph structure. Generally, the nodes in
the graph structure are represented by the IP and port, and the edges in
the graph structure represent the information of network traffic. From
the perspective of logical reasoning, the node information in the graph
structure is IP and port and the edge information in the graph structure
is the related network protocol number, that is, the flow-level feature
tuple of network flow is 𝐹 (𝑠𝑟𝑐_𝐼𝑃 , 𝑑𝑠𝑡_𝐼𝑃 , 𝑠𝑟𝑐_𝑃 , 𝑑𝑠𝑡_𝑃 , 𝑃 𝑟𝑜).
Although this practice considers the advantages of using graph
structure to represent network traffic, but the contained information
is far from covering the specific characteristics of a network traffic.
In order to take full advantage of graph structure to store network
traffic, the feature information to be stored on each network traffic is
first extended with the features. Specifically, because the IP address
and port of each network traffic are sufficient to describe each node,
and too much description of endpoint information of each network
traffic may not only cause data redundancy, but also affect the construction efficiency of graph structure, thus, the information of features
contained in each node of graph structure is not changed. For the
description information on the edges of graph structure, the protocol
number information used by most researchers to describe the features
of network traffic is obviously insufficient, where the protocol number
usually only provides rough information about the protocol to which
the traffic belongs but lacks more specific information about the details
and behavior of traffic camouflage, which will have a negative effect on
the detection efficiency of malicious traffic. For this reason, this study
not chooses to use protocol number to describe the network traffic, but
selects some features most relevant to each network flow, including
the number of inflow bytes (num(𝑖𝑛_𝑏)), the number of outflow bytes
(num(𝑜𝑢𝑡_𝑏)), the sum number of bytes (num(𝑠𝑢𝑚_𝑏)), the length of
inflow packets (len(𝑖𝑛_𝑝)), the length of outflow packets (len(𝑜𝑢𝑡_𝑝)), the
sum number of packets (num(𝑠𝑢𝑚_𝑝)), the interval time between current
network traffic and last network traffic (int(𝑡𝑖𝑚𝑒)), and the duration of
current network traffic (dur(𝑛𝑡)). The above key features of network
traffic are extracted by the tshark (a Wireshark’s built-in command-line
tool). This process aims to build a more comprehensive and accurate set
of features to support subsequent tasks of network traffic analysis and
malicious traffic detection. These features are described as follows:

Fig. 2. The extended schematic of flow-level features.

3. int(𝑡𝑖𝑚𝑒), dur(𝑛𝑡): Different types of applications or protocols
usually have different traffic time interval and different duration, observing the interval time between current network traffic
and last network traffic as well as duration of current network
traffic can reveal regular, periodic or abnormal traffic events,
which can help to distinguish and identify specific applications,
user behaviors or network events.
With the above considered factors, the extended 12-tuple is
𝐹 (𝑠𝑟𝑐_𝐼𝑃 , 𝑑𝑠𝑡_𝐼𝑃 , 𝑠𝑟𝑐_𝑃 , 𝑑𝑠𝑡_𝑃 , 𝑖𝑛_𝑏, 𝑜𝑢𝑡_𝑏, 𝑖𝑛_𝑝, 𝑜𝑢𝑡_𝑝, 𝑠𝑢𝑚_𝑝, 𝑠𝑢𝑚_𝑏, 𝑖𝑛𝑡,
𝑑𝑢𝑟), where 𝑠𝑟𝑐_𝐼𝑃 : 𝑠𝑟𝑐_𝑃 and 𝑑𝑠𝑡_𝐼𝑃 : 𝑑𝑠𝑡_𝑃 are the direct relationship
between each IP and its port, 𝑠𝑢𝑚_𝑝 = 𝑖𝑛_𝑝+𝑜𝑢𝑡_𝑝, 𝑠𝑢𝑚_𝑏 = 𝑖𝑛_𝑏+𝑜𝑢𝑡_𝑏.
The extended schematic of flow-level features is shown in Fig. 2,
where Fig. 2(a) is the features of network traffic before extending and
Fig. 2(b) is the features of network traffic after extending. This study
uses these information of features to describe each network traffic in
more detail, so as to improve the detection efficiency of malicious
network traffic.
3.2. The correlation conversion of network traffic based on link homogeneity and weight assignment
The network traffic with same IP host are more likely to be the
same software compared with randomly selected network traffic, that
is, there is link homogeneity in the network (Zheng et al., 2022)
(link homogeneity refers to the degree of similarity between network
correlations and transmission paths in the network). Taking whether
there is a common IP between two network traffic as the basis for
judging whether there is a correlation between network traffic, the edge
classification in network traffic detection can be transformed into a
node classification problem. The edge classification problem is usually
more complex and requires more time overhead because it needs to
consider every edge in the network. Compared with edge classification
problem, the node classification focuses on the classification at the
node level, and it is easier to obtain label because nodes are usually
directly related to specific identifiers (such as IP address or hostname).
Considering that network traffic has flow direction, this study improves
the original undirected graph of traffic correlation into a directed graph
and further defines the direct and indirect correlation between network
traffic, as well as assigns different weights to the direct and indirect
correlation to consider more important correlated information. The
improved structure of graph conversion is shown in Fig. 3.
The definition of graph in Fig. 3 is 𝐺 = (𝑉 , 𝐴), where 𝑉 is the set
of nodes and 𝐴 is a symmetric adjacency matrix. The elements 𝑎𝑖𝑗 of
adjacency matrix are the weights of edges between nodes 𝑣𝑖 and 𝑣𝑗 ,
where 𝑎𝑖𝑗 = 0 indicates that there is no edge correlation between two
nodes, 𝑎𝑖𝑗 = 1 indicates that there is an indirect correlation between two
edges, and 𝑎𝑖𝑗 = 2 indicates that there is a direct correlation between
two edges. In addition, we also define the degree matrix 𝐷 = diag

1. num(𝑖𝑛_𝑏), num(𝑜𝑢𝑡_𝑏), num(𝑠𝑢𝑚_𝑏): The number of inflow bytes
of malicious traffic (num(𝑖𝑛_𝑏)), the number of outflow bytes
of malicious traffic (num(𝑜𝑢𝑡_𝑏)) and the sum number of inflow
and outflow bytes of malicious traffic (num(𝑠𝑢𝑚_𝑏)) may indicate potential malicious behavior or intrusion attempts, thus,
the malicious traffic patterns of network attacks or other abnormal conditions can be detected by counting the number of
bytes flowing in and out, thereby detecting and preventing the
network security threats.
2. len(𝑖𝑛_𝑝), len(𝑜𝑢𝑡_𝑝), num(𝑠𝑢𝑚_𝑝): Different types of applications
or protocols usually have different distributions of packet length
and different sum number of packet, these features can be used
to identify and distinguish different types of network traffic,
such as Web browsing, file transfer or video streaming. In addition, the packet length also can be used to analyze the delay
characteristics of network traffic. Therefore, the malicious traffic
patterns of network attacks or other abnormal conditions can be
detected by counting the length and total number of packets.
5

Computers & Security 147 (2024) 104083

J. Chen et al.

nodes, but it is difficult to model the complex dependency between the
nodes in network traffic. To solve this problem, we introduce multihead self-attention mechanism and correlation matrix into the GCN
model to assign different weights to direct correlation and indirect
correlation. Among them, the correlation matrix allows the weights of
edges in the graph to be adjusted to more accurately reflect the degree
of dependency between nodes, which can help GCN to aggregate more
accurate features of network traffic nodes. The overall framework of
GCN-MHSA model is shown in Fig. 4.
GCN is a multi-layer neural network model that provides a powerful
tool for malicious traffic detection. It can directly process the data in
graph structure and use the attributes of adjacent nodes to guide the
embedding vector learning of each node, thereby obtaining the feature
representations of new node. These feature representations are further
used as input to a linear classifier for the classification task of nodes.
In addition, through the stacking of multi-layer GCN, a wider range
of information can be gradually integrated to effectively analyze the
relationship between network topology and node attributes as well as
identify abnormal behavior, thereby more comprehensively capturing
the relevant information in the detection of malicious traffic. For the
𝑘th graph convolution layer, the matrices 𝐻 (𝑘−1) and 𝐻 (𝑘) represent the
representations of input node and output node, respectively. In general,
the representation of initial node is the original input feature 𝐻 (0) = 𝑋,
which represents the input of first graph convolution layer. For a singlelayer GCN, the new d’-dimensional node feature matrix 𝐻 (1) is shown
in formula (1).

Fig. 3. The correlation conversion of network traffic.

(𝑑1 , . . . , 𝑑𝑛 ), where each node 𝑣𝑖 in the graph has a corresponding ddimensional feature vector. The feature vectors of all n nodes form a
complete feature matrix 𝑋.
According to the above definition, suppose there are n network
flows and each has d-dimensional features, feature matrix 𝑋 and adjacency matrix 𝐴. Specifically, when two network traffic share the same
IP host, 𝑎𝑖𝑗 can take the value of 1 or 2, respectively, which represents
the degree of correlation between network traffic. If there is no IP
host sharing, 𝑎𝑖𝑗 is set to 0, indicating that there is no correlation
between network traffic. In addition, in order to better distinguish the
importance of different correlations, we define the cases in which there
is a correlation between two network traffic:

𝐻 (1) = 𝑅𝑒𝐿𝑈 (𝑀𝑋𝜃 (1) )

1. Direct correlation: When the source IP address of one traffic is
the same as the destination IP address of another network, these
two network traffic are regarded as direct correlation, where
the value of corresponding position is set to 2 in the adjacency
matrix, indicating that they are more connected, and this higher
weight helps to highlight the importance of direct connected
network traffic.
2. Indirect correlation: When two network traffic has same source
IP address or destination IP address, these two network traffic
are regarded as indirect connected, where the value of corresponding position is set to 1 in the adjacency matrix. This lower
weight indicates that although they may be connected with same
IP address, they may not have close communication, therefore,
their relevance is not as high as that of direct connected network
traffic.

(1)

In formula (1), the normalized adjacency matrix 𝑀 of self-loop is
added, that is, the connection between nodes and themselves in the
graph is also considered when the adjacency matrix is normalized,
which is shown in formula (2).
1

1

̃− 2
̃ − 2 𝐴̃𝐷
𝑀 =𝐷

(2)

̃ is a degree matrix, the weight matrix
In formula (2), 𝐴̃ = 𝐴 + 𝐼, 𝐷
𝜃 (1) used to smooth the linear transformation of the hidden feature
representation. In the GCN model, multiple GCN layers can be stacked
to capture higher-order domain information, which is shown in formula
(3).
𝐻 (𝑘) = 𝑅𝑒𝐿𝑈 (𝑀𝐻 (𝑘−1) 𝜃 (𝑘) )

(3)

For node classification, the last layer of GCN uses classifier to
predict labels. The predicted class of 𝑛 nodes is defined as 𝑌̂ = 𝑌̂𝑖𝑐 𝑛×𝑐,
where 𝑌̂𝑖𝑐 represents the probability that node 𝑖 belongs to class 𝐶.
Therefore, the e-class prediction of GCN at layer 𝐾 is shown in formula
(4).

This strategy of different weight allocation can better distinguish
the importance of different correlations. Typically, direct connected
network traffic imply the closer communication and they should be
assigned larger weights; While indirect correlations imply that although
such correlations are still considered in the connected network traffic,
they may involve the same IP address but do not necessarily indicate
direct communication, they should be assigned smaller weights. This
strategy helps to more accurately capture the correlation information
between network traffic and reflect the degree of these correlations in
the adjacency matrix.
As shown in Fig. 3, the destination IP of traffic A is the source IP of
traffic B, so there is a direct correlation between them, thus, the value
of its corresponding position in the adjacency matrix is set to 2. Traffic
B and E have the same source IP, and traffic C and F have the same
destination IP, that is, B and E, C and F are indirectly connected, thus,
the value of their corresponding position in the adjacency matrix is set
to 1.

𝑌̂𝐺𝐶𝑁 = 𝑠𝑜𝑓 𝑡𝑚𝑎𝑥(𝑀𝐻(𝐾 − 1)(𝐾))

(4)

Assuming constructing a two-layer GCN (𝐾 = 2), the overall forward
propagation mode is shown in formula (5).
𝑌̂ = 𝑓 (𝑋, 𝐴) = 𝑠𝑜𝑓 𝑡𝑚𝑎𝑥(𝑀 × 𝑅𝑒𝐿𝑈 (𝑀𝑋𝜃 (1) )𝜃 (2) )

(5)

Finally, the cross-entropy loss function of all labeled nodes is calculated, and the sequence of features in high-dimensional network traffic
is obtained by inputting the traffic features of graph structure into GCN.
In view of the complex inter-correlations between network traffic,
it is urgent to deeply focus on and clearly express the complex relationships between different network traffic. Therefore, we introduce a
multi-head self-attention mechanism into GCN model, it uses multiple
different attention heads to calculate the relationships between nodes,
thereby improving the expressive ability of the model. In particular, it
is worth noting that the application of multi-head self-attention mechanism in the GCN-MHSA hidden layer means that the self-attention
mechanism is introduced between the node representations of each
layer, thereby accurately capturing the dependency between nodes.

3.3. The framework and algorithm of GCN-MHSA
After constructing graph structure for network traffic, we use an
improved GCN model called GCN-MHSA to detect malicious traffic. Traditional GCN-based methods can learn the correlated features between
6

Computers & Security 147 (2024) 104083

J. Chen et al.

Fig. 4. The framework of GCN-MHSA model.

and then obtain labels based on classification results of GCN model
as well as calculate the loss and update the weight matrices to obtain
a high-dimensional set of correlated features after each training batch.
Subsequently, apply the multi-head self-attention mechanism to process
the correlated features and focus on the most important features.
Finally, the detection operation is performed to obtain the malicious
traffic.

This improvement permits a more detailed analysis and understanding of the correlations between different network traffic, thus further
improving the accuracy and performance of the model detection.
Assuming that the input feature matrix is 𝑋𝑛×𝑑 , where 𝑛 represents
the number of traffic sequences and 𝑑 represents the feature dimension
of each traffic sequence. Firstly, the multi-head attention mechanism
is used to weight the input features and produce an attention matrix
𝐴𝑛×𝑛 , as shown in formula (6).
𝐴 = 𝑠𝑜𝑓 𝑡𝑚𝑎𝑥(

𝑋𝑊 𝑄 (𝑋𝑊 𝐾 )𝑇
)
√
𝑑𝑘

Algorithm 1 GCN-MHSA
Input: 𝐺(𝑉 , 𝐴), learning rate, epoch, dropout, batch
Output: Detection result

(6)

In formula (6), 𝑊 𝑄 and 𝑊 𝐾 are matrices used to project input
feature 𝑋 onto query matrix 𝑄 and key matrix 𝐾, and 𝑑𝑘 represents
the dimension of each head. Multi-head attention mechanism uses
ℎ different 𝑊 𝑄 and 𝑊 𝐾 to learn the dependency between nodes,
resulting in ℎ attention matrices 𝐴1 , 𝐴2 , . . . , 𝐴ℎ . Softmax operation
√
normalizes the weights in the attention matrix to range [0,1], 𝑑𝑘 is
used for scaling to prevent excessive inner product being too large. The
calculation of attention matrix for each head is shown in formula (7).
ℎ𝑒𝑎𝑑𝑖 = 𝑠𝑜𝑓 𝑡𝑚𝑎𝑥(

𝑋𝑊𝑖𝑄 (𝑋𝑊𝑖𝐾 )𝑇
), 𝑖 = 1, … , ℎ
√
𝑑𝑘

1: SetParameters(𝑙𝑒𝑎𝑟𝑛𝑖𝑛𝑔𝑟𝑎𝑡𝑒, 𝑒𝑝𝑜𝑐ℎ, 𝑑𝑟𝑜𝑝𝑜𝑢𝑡)
2: LoadData(𝐺)
3: 𝐺 → GCN-MHSA model
4: for each epoch do
5:
for each epoch do
6:
ExtractFeatures()
7:
classification result based on GCN → label
8:
CalculateLoss()
9:
renew weight values 𝑊
10:
obtain the association feature 𝐴𝐹
11:
end for
12:
𝐴𝐹 = MultiHeadAttention(𝐴𝐹 )
13: end for
14: 𝑅𝑒𝑠𝑢𝑙𝑡 = Classification (𝐴𝐹 )
15: return Result

(7)

For each attention matrix ℎ𝑒𝑎𝑑𝑖 , we can use the same way as the
traditional GCN to calculate its feature representation 𝑍𝑖 , which is
shown in formula (8).
1

1

̃− 2 𝐴
̃𝑖 𝐷
̃ − 2 𝑋𝑊 𝑉 )
𝑍𝑖 = 𝜎(𝐷
𝑖

(8)

In formula (8), 𝑍𝑖 is obtained by encoding the feature 𝑋 of the
̃𝑖 is the attention matrix with self-loop added, 𝐷
̃ is
𝑖th head node, 𝐴
the diagonal matrix, and the weight matrix 𝑊𝑖 is used to perform
linear transformation on 𝑋 and project the input feature onto the
value 𝑉 . 𝑑×𝑣 is the output dimension of each head. The multi-head
feature representation 𝑍𝑑×𝑣 can be obtained by connecting the feature
representation of each head, which is shown in formula (9).
𝑍 = 𝑐𝑜𝑛𝑐𝑎𝑡(𝑍1 , … , 𝑍ℎ )

The proposed GCN-MHSA model can achieve more powerful and
flexible feature extraction through multi-head self-attention mechanism, multi-head feature representation and multi-head feature fusion.
In the multi-head self-attention mechanism, each head focuses on different features, which provides the model with multiple attention
methods to better capture complex patterns in network traffic. In addition, multi-head feature representation and multi-head feature fusion
enhance the feature representation and help to characterize network
traffic more comprehensively. This manner also allows weighted aggregation of nodes’ neighboring nodes, which further enriches the
representation of nodes and enables the model to capture the complex
relationships among nodes more accurately.
Through flexibly combining the attention weights of different heads,
the model can more accurately express the relationship between nodes,
which improves the generalization ability of the model and enables it
better adapt to different network traffic datasets and tasks. In addition,
the introduction of multi-head self-attention mechanism helps to reduce
the impact of noise on the model for improving the robustness of
the model as well as significantly improves the learning efficiency
and training convergence speed of the model, thereby accelerating the
training process of the model, improving the detection performance and
better adapting to the changing network environment.

(9)

Finally, a fully connected layer is used to fuse the multi-head feature
representation 𝑍, which is shown in formula (10).
1

̃ − 2 𝑍𝑊 𝑜𝑢𝑡 )
𝐻 𝑙+1 = 𝑅𝑒𝐿𝑈 (𝐷

(10)

In formula (10), 𝑊 𝑜𝑢𝑡 is the weight matrix used to project the multihead feature representation to the next hidden layer, and 𝐻 𝑙+1 is the
feature representation of the next hidden layer.
The detailed process of malicious traffic detecting by GCN-MHSA
model is shown in Algorithm 1. Firstly, the parameters including
learning rate, number of epoch and dropout rate are set to initialize
the model; And then, the data in graph structure is input into the
GCN-MHSA model for processing. Within each training epoch, iterate
through each batch of data to extract features from graph structure,
7

Computers & Security 147 (2024) 104083

J. Chen et al.
Table 2
The description of UJS-IDS2022 dataset.
Normal

Filesize (KB)

Malware

Filesize (KB)

Tencent video
QQ music
Thunder
Youku
Iqiyi
Mango video
Himalaya
Baidu post bar
League of legends
Bilibili

32 450
30 220
492 530
288 026
40 592
179 003
8944
89 530
13 096
108

ArkeiStealer
AsyncRAT
AveMariaRAT
Formbook
Hive
Kutaki
Loki
MassLogger
OskiStealer
RedLineStealer

159 477
27 492
297 535
379 488
560 345
234 207
17 261
171 313
77 368
160 061

Negative) refers to the number of normal traffic correctly identified by
the GCN-MHSA method as normal traffic; 𝐹 𝑁 (False Negative) refers to
the number of malicious traffic incorrectly identified by the GCN-MHSA
method as normal traffic.
4.3. Experimental setup
The hardware environment of the experiment is two 20-core 40thread CPUs, 128G RAM and two RTX3090 GPUs, and the software
environment is Ubuntu 20.04.2 LTS x86_64, TensorFlow 2.4.0 and
Python 3.8.
To determine the optimal model parameters, we employ grid search
to systematically explore a wide range of configurations. The parameters includes the batch_size of 16, 32 and 64; the dropout rate of 0.4,
0.5 and 0.6; the epoch_size of 10, 30, 50 and 70; and the learning
rate of 0.1, 0.01 and 0.001. Each parameter combination is evaluated
for 30 times and the hyperparameter under highest detection accuracy is selected as the parameter of our GCN-MHSA model, including
batch_size = 64, dropout rate = 0.5, epoch_size = 50, and learning
rate = 0.01. To ensure the fairness across experiments, all baselines
are trained using identical hyperparameter settings. Additionally, after
several experimental iterations, we incorporate three layers of multihead self-attention mechanism with four attention heads in the model
to balance the performance with computational cost. The ratio of
training datasets to testing datasets is 8:2 for all used four network
traffic datasets.

4. Experiment
This section first describes the dataset, evaluation metrics, experimental settings and baselines used in the experiment, and then verifies
the effectiveness of the proposed GCN-MHSA method with five state-ofthe-art methods and discusses the experimental results. Subsequently,
the ablation experiment is conducted to verify the effectiveness of the
improved scheme proposed in this study.
4.1. Dataset description
CIC-IDS2017 dataset is a collection of network attack data collected
by the Canadian Cyber Security Research Institute from computer
simulated network attack scenarios on multiple local area networks,
it is produced and maintained by researchers from the University of
New Brunswick, Canada. This dataset is generated from a large-scale
simulation of network traffic, including both normal network traffic
and malicious network traffic. Among them, malicious network traffic
includes 16 different types of network attack, such as DoS, Scan, R2L,
U2R and others.
CTU-13 is a dataset for cybersecurity research, it is provided by
the researchers from Computer Science Department of Czech Technical University. The dataset contains network traffic captured in a
real network environment, which contains normal network traffic as
well as samples from 13 different types of attacks, including: worms,
Trojans, DDoS attacks, botnets, sniffing, scanning, malware downloads,
etc. Each attack sample contains multiple network sessions, and each
session has a set of packets and associated metadata information, such
as timestamp, IP address, port number and so on.
USTC-TFC2016 dataset is created and collected by the University
of Science and Technology of China (USTC) to analyze and detect
malicious traffic, it contains multiple types of malicious traffic. The
images in the dataset come from different scenes and environments
in the real world and cover multiple categories of objects to make it
having diversity and representative.
UJS-IDS2022 dataset is the collected network traffic produced by
multiple normal software and malware in the real environment by the
Key Laboratory of Industrial Cyberspace Security Technology of Jiangsu
University from June 5, 2022 to June 18, 2022. The number of network
traffic in this dataset is 7.67 million (2.76 million for benign, 4.91
million for malicious). The specific software and the size of PCAP files
corresponding to their network traffic are shown in Table 2.

4.4. Baselines
In order to verify the validity of the proposed GCN-MHSA model,
five advanced and representative baselines are used in the experiment
for comparison.
1. E-minBatch GraphSAGE (Lan et al., 2022). It is an improved
GraphSAGE neural network model that can adapt to complex
network environment.
2. GATrust (Jiang et al., 2022). It is an improved graph attention
network that can assign different attention coefficients in the
network.
3. IARF (Niu et al., 2022). It is an improved encryption malicious
traffic detection method based on adaptive random forest.
4. CNN-LSTM (Sun et al., 2020). It is a hybrid network of CNN
and LSTM that can effectively capture and extract the spatiotemporal features of network traffic.
5. GCN-ETA (Zheng et al., 2022). It is an encrypted malicious
traffic detection method based on graph convolutional neural
networks.
4.5. Experimental results and analysis
4.5.1. The performance analysis of multiclassification
In order to evaluate the multi-classification performance of the
proposed GCN-MHSA method, we conduct a large number of experiments on three public network traffic datasets and a real network
traffic dataset with the comparison of five baselines. Fig. 5 shows the
experimental results on CICIDS-2017 dataset using confusion matrix,
where the horizontal axis represents the class predicted by the GCNMHSA method and the vertical axis represents the true class of network
traffic. The values in the matrix have been normalized, and the diagonal
elements correspond to the detection accuracy of the model.
As is shown in Fig. 5(f), GCN-MHSA method has good performance
in malicious traffic detection with an accuracy close to 98%. Fig. 5(a)
shows that the E-minBatch GraphSAGE method has a poor detection
efficiency on certain types of malicious traffic when processing a small
number of samples, and its overall performance is lower than that of
proposed GCN-MHSA method due to it is prone to overfitting in the

4.2. Evaluation metrics
In the experiments, four evaluation metrics are selected to evaluate
the detection efficiency of proposed GCN-MHSA model for malicious
network traffic, they are shown in Table 3.
In Table 3, 𝑇 𝑃 (True Positive) refers to the number of malicious traffic correctly identified by the GCN-MHSA method as malicious traffic;
𝐹 𝑃 (False Positive) refers to the number of normal traffic incorrectly
identified by the GCN-MHSA method as malicious traffic; 𝑇 𝑁 (True
8

Computers & Security 147 (2024) 104083

J. Chen et al.
Table 3
Evaluation metric.
Metric

Formula

Meaning

Precision

𝑃
𝑃 = 𝑇 𝑃𝑇+𝐹
𝑃

The proportion of samples predicted to be positive that are actually positive.

Accuracy

+𝑇 𝑁
𝐴 = 𝑇 𝑃 +𝐹𝑇 𝑃𝑃 +𝑇
𝑁+𝐹 𝑁

The proportion of samples whose predictions are correct.

Recall

𝑃
𝑅 = 𝑇 𝑃𝑇+𝐹
𝑁
2×𝑅×𝑃
𝐹 1 = 𝑅+𝑃

The proportion of positive samples that are predicted to be positive.

F1-measure

The accuracy rate and recall rate are considered comprehensively, it is the harmonic average of the two metrics.

Fig. 5. The confusion matrix of six compared malicious traffic detection methods.

learning process. The experimental results in Fig. 5(b) and (c) show
that the GATrust and IARF methods exhibit poor detection performance
compared to the GCN-MHSA model in identifying network traffic with
certain types of attack (such as Dos, Heartbleed, synflood, PortScan and
SSH-Patator), which indicates the poor generalization ability of these
two methods. As is shown in Fig. 5(d) that the CNN-LSTM method
also has some shortcomings similar to the IARF method. Nevertheless, the CNN-LSTM method shows comparable detection accuracy to
the GCN-MHSA method in identifying normal network traffic as well
as the malicious traffic with the attack types of Dos and PortScan.
Fig. 5(e) shows that although the detection efficiency of GCN-ETA
method on Dos and PortScan attacks is close to that of GCN-MHSA,
but its detection efficiency on other types of attack is not good.

4.5.2. The performance of GCN-MHSA
To verify whether the proposed GCN-MHSA method can obtain
better detection capability of malicious traffic, we compare it with
five methods, including E-minBatch GraphSAGE, GATrust, IARF, CNNLSTM, and GCN-ETA. Each experiment is conducted for 30 times and
the average experimental result is shown in Table 4, where the positive
and negative errors are the standard deviations of 30 repetitions.
The experimental results on CICIDS-2017 dataset show that the
proposed GCN-MHSA method has better performance in malicious
traffic detection than E-minBatch GraphSAGE, GATrust, IARF, CNNLSTM and GCN-ETA methods. Specifically, compared with E-minBatch
GraphSAGE method, the accuracy, precision, recall and F1-measure
of GCN-MHSA method improve by 2.15%, 2.05%, 1.89% and 2.31%,
respectively; Compared with GATrust, these evaluation metrics improve by 1.92%, 1.46%, 1.48% and 1.62%, respectively; Compared
with IARF, the accuracy, precision, recall and F1-measure metrics of
GCN-MHSA method increase by 2.6%, 2.24%, 2.5% and 2.77%, respectively; Compared with CNN-LSTM, these metrics improve by 1.26%,
1.14%, 2.2% and 2.0%, respectively; Compared with GCN-ETA, the
above metrics increase by 4.3%, 3.9%, 4.36% and 4.42%, respectively.
Similarly, a similar effect is also can be observed on the CTU-13 dataset
and USTC-TFC2016 dataset.
In addition, in order to verify the detection efficiency of the proposed GCN-MHSA method in a real data environment, we conduct a

The experimental results show that traditional malicious traffic
methods that do not include feature weight learning can successfully
learn most of the correlated features in both normal traffic and largescale malicious traffic. However, they are not efficient in detecting
malicious traffic in small sample categories. In contrast, the proposed
GCN-MHSA method introduces a multi-head self-attention mechanism,
which can weight each element in the input sequence according to the
correlation of different positions in the input sequence, thus obtaining
accurate and reliable detection results.
9

Computers & Security 147 (2024) 104083

J. Chen et al.
Table 4
The comparison of six malicious traffic detection methods.
Methods

Dataset

Accuracy (%)

Precision (%)

Recall (%)

F1-measure (%)

E-minBatch GraphSAGE

CICIDS-2017
CTU-13
USTC-TFC2016
UJS-IDS2022

95.86 ± 0.35
96.33 ± 0.73
97.55 ± 0.66
91.36 ± 1.71

96.02 ± 0.77
96.76 ± 0.89
96.98 ± 0.91
91.82 ± 1.56

96.32 ± 1.64
95.18 ± 1.52
97.76 ± 0.82
92.55 ± 0.49

95.83 ± 0.84
96.34 ± 0.52
97.33 ± 0.69
92.18 ± 1.32

GATrust

CICIDS-2017
CTU-13
USTC-TFC2016
UJS-IDS2022

96.11 ± 0.87
97.67 ± 1.02
98.22 ± 0.54
96.28 ± 1.02

96.61 ± 1.42
97.77 ± 1.36
98.56 ± 0.75
96.96 ± 0.98

96.73 ± 0.53
97.41 ± 0.76
97.93 ± 0.42
97.16 ± 1.29

96.52 ± 0.48
97.25 ± 0.93
98.20 ± 0.77
97.06 ± 0.67

IARF

CICIDS-2017
CTU-13
USTC-TFC2016
UJS-IDS2022

95.43 ± 0.92
96.13 ± 0.85
96.81 ± 0.93
92.66 ± 1.02

95.83 ± 0.96
96.23 ± 0.62
97.04 ± 0.73
92.49 ± 0.89

95.71 ± 0.96
95.43 ± 0.65
96.57 ± 0.88
93.19 ± 0.98

95.37 ± 0.86
95.43 ± 0.79
96.82 ± 1.07
92.84 ± 0.91

CNN-LSTM

CICIDS-2017
CTU-13
USTC-TFC2016
UJS-IDS2022

96.77 ± 1.32
97.12 ± 1.63
97.98 ± 0.92
95.67 ± 2.03

96.93 ± 0.92
97.37 ± 0.63
98.48 ± 0.25
95.96 ± 1.75

96.01 ± 0.72
96.96 ± 0.34
98.18 ± 0.32
96.18 ± 1.44

96.11 ± 0.39
97.04 ± 0.81
98.39 ± 0.63
96.07 ± 1.69

GCN-ETA

CICIDS-2017
CTU-13
USTC-TFC2016
UJS-IDS2022

93.73 ± 0.57
95.72 ± 0.74
97.48 ± 0.21
90.51 ± 1.45

94.17 ± 0.89
94.90 ± 1.12
97.57 ± 0.64
90.78 ± 1.22

93.85 ± 1.00
95.47 ± 0.57
96.44 ± 0.71
91.37 ± 0.89

93.85 ± 1.00
95.18 ± 0.35
96.99 ± 0.45
91.07 ± 1.01

GCN-MHSA

CICIDS-2017
CTU-13
USTC-TFC2016
UJS-IDS2022

98.03 ± 0.15
99.06 ± 0.19
99.31 ± 0.13
96.38 ± 0.36

98.07 ± 0.15
98.76 ± 0.13
99.03 ± 0.21
96.87 ± 0.27

98.21 ± 0.23
99.03 ± 0.18
99.47 ± 0.23
97.18 ± 0.42

98.14 ± 0.08
98.90 ± 0.06
99.12 ± 0.19
97.02 ± 0.34

CNN-LSTM. In addition, the detection performance of IARF model is
weaker than other models except GCN-ETA because it only learns the
features from online streaming data, which limits its ability to learn
from large-scale datasets. Compared with above compared methods,
the detection results of GCN-ETA are weak, it is owing to that it does
not assign different weights to different levels of traffic correlations, so
unimportant features produce a greater impact on its detection results.

series of experiments on the UJS-IDS2022 dataset. The experimental
results show that compared with the experiments on public network
traffic, the detection efficiency in the real environment are generally
lower because of the diversity and complexity of collected network
traffic. Nevertheless, the proposed GCN-MHSA method still achieves the
best results in the real environment. It is worth noting that GCN-MHSA
performs slightly worse than the GATrust method on the evaluation
metrics of precision and F1-measure, it is possibly due to the GATrust
method has the ability of feature representation with strong learning adaptability, which results in it adapting to different topologies
and sizes of network traffic. Compared with the state-of-the-arts, the
proposed GCN-MHSA method has greater stability, which shows that
GCN-MHSA is an excellent detection method in the real environment,
especially in the face of diversity and complexity of network traffic.
Compared with other methods, the proposed GCN-MHSA method
achieves excellent experimental results on multiple evaluation metrics
due to the following advantages: (1) In the model preprocessing stage,
through considering and utilizing the information embedded in the
network traffic, we extend the features of network traffic to make
the model capturing the overall structure and attributes of network
traffic more comprehensively as well as avoiding information loss or
bias caused by missing data; (2) We introduce the multi-head selfattention mechanism to capture different types of interactions between
nodes more comprehensively and focus on important features, thereby
making the model able to learn different attention weights in parallel to assign different weights for the features in network traffic;
(3) Through modeling and analyzing network topology, GCN-MHSA
model can extract valuable information and patterns from complex
network traffic, this graph structure-based manner enables GCN-MHSA
method to capture the relationship and interaction between nodes
effectively, which is benefit it for learning the hidden features in
network traffic. In the compared methods, GATrust performs best because it considers more relationships among nodes in the process of
constructing graph structure through feature transformation. The CNNLSTM hybrid network has the third highest detection performance on
all datasets by extracting the spatiotemporal features of network traffic.
In contrast, E-minBatch GraphSAGE model only uses the information
of local neighbor node but not uses the global information, that is,
it does not make full use of the overall graph structure information,
which results in its detection performance weaker than GATrust and

4.5.3. The stability of GCN-MHSA
To verify the stability of the proposed GCN-MHSA method, we
conduct the experiments on four datasets for 30 times with all compared methods, and the boxplot according to the experimental results
is shown in Fig. 6.
As can be seen from Fig. 6 that compared with E-minBatch GraphSAGE, GATrust, IARF, CNN-LSTM and GCN-ETA methods, the proposed
GCN-MHSA method has significant performance advantages and higher
stability. The GCN-MHSA model always show higher accuracy, precision, recall and F1-measure, and no outliers are observed in the
experimental results. It is worth to note from Fig. 6(a) to (d) that
the interquartile range (indicating by the box length) is significantly
narrower for the GCN-MHSA model, indicating a higher stability of
its detection efficiency. The higher stability of GCN-MHSA method is
owing to that it extends the flow-level features of network traffic and
optimizes the correlation algorithm of network traffic; In addition, it
also use the multi-head self-attention mechanism to focus on those
more important features. In contrast, the compared methods exhibit a
wider range of fluctuations and have some outliers. The experimental
results on stability show that compared with five state-of-the-art malicious detection models, the proposed GCN-MHSA method has higher
accuracy and more stable detection effect.
4.5.4. Ablation experiment
To verify the influence of each module on the proposed GCN-MHSA
model, we perform a series of ablation experiments, each experiment
is conducted for 30 times and the average experimental result is shown
in Table 5, where the positive and negative errors are the standard
deviations of 30 repetitions. Among them, GCN is the original graph
convolutional neural network model, it uses 5-tuples of features for
detection. GCN-FF adds the feature extending technology on the basis of
GCN model in the preprocessing stage, and it uses extended 12-tuples
10

Computers & Security 147 (2024) 104083

J. Chen et al.

Fig. 6. The stability of six compared malicious detection methods.
Table 5
The influence of different modules on detection accuracy of GCN-MHSA.

of features for detection. GCN-CO optimizes the mechanism of traffic
correlation establishment on the basis of GCN model, that is, setting the
indirect correlation and direct correlation, and uses 5-tuples of features
for detection. GCN-M introduces a multi-head self-attention mechanism
on the basis of GCN model, it uses 5-tuples of features for detection.
GCN-FF-CO adds feature extending module and optimizes traffic correlation mechanism on the basis of GCN-FF. GCN-FF-M introduces the
multi-head self-attention mechanism based on the GCN-FF model. GCNCO-M introduces a multi-head self-attention mechanism based on the
GCN-CO model, and it uses 5-tuples of features for detection.
It can be seen from the results of ablation experiments in Table 5
that removing any module will lead to a decrease in the detection efficiency of malicious traffic, and the multi-head self-attention mechanism
plays the most critical role among these modules. After the introduction of multi-head self-attention mechanism, the detection accuracy
on all datasets has been significantly improved, which is due to the
fact that multi-head self-attention mechanism can adaptively learn the
correlation and importance between features, which is benefit for the
model to flexibly assign different weights for the features according to
task requirements, and thus making the model has good universality
ability. In addition, the feature extending and optimizing traffic correlation establishment mechanism in the preprocessing stage also play

Model

CICIDS-2017
(%)

CTU-13 (%)

USTC-TFC2016
(%)

UJSIDS2022
(%)

GCN
GCN-FF
GCN-CO
GCN-M
GCN-FF-CO
GCN-FF-M
GCN-CO-M
GCN-MHSA

91.47 ± 1.71
92.09 ± 1.67
91.93 ± 1.55
95.72 ± 1.21
95.37 ± 1.12
97.84 ± 0.17
97.91 ± 0.24
98.03 ± 0.15

94.81 ± 1.05
95.29 ± 1.23
95.04 ± 1.47
98.19 ± 1.57
95.53 ± 1.08
99.01 ± 0.24
98.45 ± 0.41
99.06 ± 0.19

97.96 ± 0.97
98.33 ± 0.85
98.17 ± 1.01
99.08 ± 1.01
98.43 ± 0.46
99.19 ± 0.15
94.14 ± 0.17
99.31 ± 0.13

93.11 ± 1.98
93.76 ± 1.34
94.03 ± 1.61
95.43 ± 1.33
94.51 ± 1.40
96.23 ± 0.68
94.03 ± 0.52
96.38 ± 0.36

a significant role in improving the detection accuracy, especially on
the CICIDS-2017 dataset. This is because the dataset contains many
attack types and provides detailed attack labels, which results in the
optimization of these modules can get better experimental results.
It can be seen from Table 5 that the proposed GCN-MHSA method
achieves the best detection efficiency and has better generalization on
all four datasets, which also shows that these improvements in the GCNMHSA method have a good effect on improving the detection efficiency
of malicious traffic.
11

Computers & Security 147 (2024) 104083

J. Chen et al.
Table 6
The time cost of six malicious traffic detection methods (s).
Model

Time cost

USTC-TFC2016

CTU-13

Stratosphere

E-minBatch GraphSAGE

Training process
Detecting process
Overall

236.33
4.48
240.81

323.57
7.99
331.56

217.53
7.37
224.90

GATrust

Training process
Detecting process
Overall

231.32
7.76
239.08

361.55
9.01
370.56

317.31
7.31
324.62

IARF

Training process
Detecting process
Overall

282.51
12.33
294.84

272.56
17.51
290.07

262.06
9.98
272.04

CNN-LSTM

Training process
Detecting process
Overall

137.13
5.37
142.50

148.65
5.09
153.74

123.01
7.32
130.33

GCN-ETA

Training process
Detecting process
Overall

166.41
8.53
174.94

173.38
11.71
185.09

153.33
8.87
162.20

GCN-MHSA

Training process
Detecting process
Overall

172.49
9.01
181.50

170.20
7.88
178.08

161.51
7.35
168.86

number and the size of packets, the interval time, the duration of
current network traffic, etc. (that is, the twelve-tuple features used
in GCN-MHSA), thereby detecting the malicious activities with high
accuracy.
GCN-MHSA model is designed to detect a variety types of malicious
traffic, including but not limited to: (1) Brute Force FTP: Attacks
targeting FTP services by attempting numerous username and password
combinations to gain unauthorized access. (2) Brute Force SSH: It
is similar to FTP brute force attacks, but the targeting is SSH login
credentials. (3) DoS: Attacks that overload the target system with a
flood of requests, rendering it unable to provide normal services. (4)
Heartbleed: Exploits vulnerabilities in OpenSSL to read protected memory, leading to the leakage of sensitive information. (5) Web Attacks:
Attacks against web applications such as SQL injection and cross-site
scripting (XSS), aiming to gain the unauthorized access or corrupt data
integrity. (6) Infiltration: Attacks gain the initial access and subsequently penetrate deeper into the network to access more resources or
cause damage. (7) Botnet: Networks of compromised devices coordinated to perform attacks such as DDoS or spam distribution. (8) DDoS:
Large-scale attacks using multiple controlled devices to overwhelm and
incapacitate a target system.
Although the proposed GCN-MHSA model is not specifically designed against evasion attacks, it can possess the robust defenses against
evasion tactics due to it combines the global feature extraction, multihead self-attention mechanism, dynamic adaptability and the stability
of graph structures. In the GCN-MHSA model, GCN is adept at capturing the global structural features of network traffic by analyzing the
overall graph structure, which makes it challenging for attackers to
evade detection by merely altering specific features of network traffic;
In addition, the stability and robustness of graph structures make it
difficult for attackers to significantly alter the overall network traffic
structure without raising suspicion. The MHSA mechanism enhances
the model’s sensitivity and robustness by capturing the features of
network traffic from multiple perspectives and scales. Even if attackers attempt minor modifications to evade detection, the multi-head
mechanism aggregates the information from various attention heads to
find potential anomalies. Furthermore, the self-attention mechanism is
dynamically adaptive, it adjusts the weights of features to capture the
evolving information of network traffic, this adaptability can ensure
that the detection model maintains high detection capabilities in the
face of new or mutated attacks.

4.5.5. Time efficiency of GCN-MHSA
In addition to detection accuracy, the time efficiency is another
important factor to measure the efficiency of malicious traffic detection
method. To verify the time efficiency, we conduct extensive experiments on three widely used public network traffic datasets, and the
experimental result is shown in Table 6.
It can be seen from the experimental results in Table 6 that the
time cost of GCN-MHSA is only slightly higher than that of CNN-LSTM
and GCN-ETA, it consumes less time than other graph neural networkbased malicious traffic detection. For the CNN-LSTM model, it achieves
the highest time efficiency because it is not a graph neural network,
thus inherently faster in processing; However, CNN-LSTM neglects the
inter-node relationships, resulting in the lower detection accuracy. The
reason for consuming shorter time of GCN-ETA is that it uses an identity
matrix to replace the weight matrix, which simplifies the computations;
However, this simplification decreases the classification accuracy.
The superior time efficiency of our model compared to other models can be largely attributed to the incorporation of multi-head selfattention (MHSA) mechanism, which enhances efficiency of GCNMHSA model through two key aspects. (1) MHSA enables simultaneous
attention to multiple parts of the graph, which allows the model to
capture diverse node relationships and interactions comprehensively.
This distributed focus facilitates more efficient learning by ensuring
that the model integrates a broader range of graph features during
each training iteration. With the use of MHSA, GCN-MHSA model can
converge more quickly because it gathers richer and more nuanced
information from the graph, enhancing its ability to learn complex
patterns and relationships. (2) The parallel processing capability of
MHSA optimizes the computational efficiency by enabling simultaneous
processing of different parts of the graph, it means that the model can
handle diverse graph features concurrently, which potentially leads to
faster training times as well as more effective using of computational resources, this advantage is particularly beneficial for large-scale datasets
and complex graph structures.
4.5.6. The application of GCN-MHSA
GCN-MHSA model is designed for deployment at the network gateway. GCN-MHSA detects the malicious traffic through analyzing the
structured data of network traffic at the gateway. Firstly, GCN effectively captures the relationships and dependencies between different
network entities, such as IP addresses, ports and protocols, and then
identifies the patterns indicative of malicious behavior. And then,
MHSA enhances the model’s ability to focus on various aspects of
network traffic simultaneously. At the gateway, the proposed GCNMHSA model can consider multiple features concurrently, such as the

5. Conclusion
In this paper, we propose a malicious traffic detection method called
GCN-MHSA based on graph convolutional neural network and multihead self-attention mechanism. Firstly, the information contained in
12

Computers & Security 147 (2024) 104083

J. Chen et al.

References

the network traffic is enriched by extending the flow-level features.
And then, the algorithm of establishing traffic correlation relationship is optimized to better capture the features of malicious traffic
by accurately establishing the correlation relationship between traffic,
thereby making the model to identify potential threats more accurately
and detect malicious traffic effectively. Subsequently, the multi-head
self-attention mechanism is integrated into graph convolutional neural
network model to effectively capture the dependence between nodes
and makes full use of local neighborhood information of nodes through
network structure, it also promotes the generation of multiple feature
combinations through stacked self-attention layers. With the use of
attention mechanism, the feature combinations that are more important
for malicious traffic detection are assigned larger weight to improve
the detection efficiency for malicious traffic. The proposed GCN-MHSA
method provides an accurate and efficient method for malicious traffic
detection by fusing graph convolutional neural network and multihead self-attention mechanism and optimizing the traffic correlation
construction algorithm, which is expected to play an important role in
the field of network security. Extensive experiments on four network
traffic show that the proposed GCN-MHSA method performs better than
E-minBatch GraphSAGE, GATrust, IARF, CNN-LSTM and GCN-ETA in
terms of accuracy, precision, recall and F1-measure, and it also has
better stability.
Although the proposed GCN-MHSA method achieves better detection results, it also has some shortcomings to be further improved in
the future:

Alshammari, R., Zincir-Heywood, A.N., 2009. Machine learning based encrypted
traffic classification: Identifying ssh and skype. In: 2009 IEEE Symposium on
Computational Intelligence for Security and Defense Applications. IEEE, pp. 1–8.
Anderson, B., McGrew, D., 2016. Identifying encrypted malware traffic with contextual
flow data. In: Proceedings of the 2016 ACM Workshop on Artificial Intelligence
and Security. pp. 35–46.
Barradas, D., Santos, N., Rodrigues, L., Signorello, S., Ramos, F.M.V., Madeira, A., 2021.
FlowLens: Enabling efficient flow classification for ML-based network security applications. In: 2021 Network and Distributed Systems Security (NDSS) Symposium.
pp. 1–18.
Chen, J., Chen, Y., Cai, S., Yin, S., Zhao, L., Zhang, Z., 2023a. An optimized feature
extraction algorithm for abnormal network traffic detection. Future Gener. Comput.
Syst. 149, 330–342.
Chen, J., Lv, T., Cai, S., Song, L., Yin, S., 2023b. A novel detection model for abnormal
network traffic based on bidirectional temporal convolutional network. Inf. Softw.
Technol. 157, 107166.
Chen, J., Song, L., Cai, S., Xie, H., Yin, S., Ahmad, B., 2023c. TLS-MHSA: An efficient
detection model for encrypted malicious traffic based on multi-head self-attention
mechanism. ACM Trans. Priv. Secur. 26 (4), 1–21.
Eswaran, D., Faloutsos, C., 2018. Sedanspot: Detecting anomalies in edge streams. In:
2018 IEEE International Conference on Data Mining. ICDM, IEEE, pp. 953–958.
Fang, Y., Ergüt, S., Patras, P., 2022. SDGNet: A handover-aware spatiotemporal graph
neural network for mobile traffic forecasting. IEEE Commun. Lett. 26 (3), 582–586.
Fu, C., Li, Q., Shen, M., Xu, K., 2021. Realtime robust malicious traffic detection via
frequency domain analysis. In: Proceedings of the 2021 ACM SIGSAC Conference
on Computer and Communications Security. CCS ’21, pp. 3431–3446.
Fu, C., Li, Q., Xu, K., 2023. Detecting unknown encrypted malicious traffic in real
time via flow interaction graph analysis. In: 2023 Network and Distributed Systems
Security (NDSS) Symposium. pp. 1–18.
Guo, Y., Li, R., Zhangyan, Wang, G., 2020. Graph neural network based anomaly
detection in dynamic networks. J. Softw. 31 (3), 748–762.
Gupta, M., Gao, J., Sun, Y., Han, J., 2012. Integrating community matching and outlier
detection for mining evolutionary community outliers. In: Proceedings of the 18th
ACM SIGKDD International Conference on Knowledge Discovery and Data Mining.
pp. 859–867.
Holland, J., Schmitt, P., Feamster, N., Mittal, P., 2021. New directions in automated
traffic analysis. In: Proceedings of the 2021 ACM SIGSAC Conference on Computer
and Communications Security. CCS ’21, pp. 3366–3383.
Jiang, N., Jie, W., Li, J., Liu, X., Jin, D., 2022. Gatrust: A multi-aspect graph attention
network model for trust assessment in osns. IEEE Trans. Knowl. Data Eng. 35 (6),
5865–5878.
King, I.J., Huang, H.H., 2022. Euler: Detecting network lateral movement via scalable
temporal graph link prediction. In: 2022 Network and Distributed Systems Security
(NDSS) Symposium. pp. 1–16.
Kipf, T.N., Welling, M., 2017. Semi-supervised classification with graph convolutional
networks. In: 2017 International Conference on Learning Representations. pp. 1–14.
Lan, J., Lu, J.Z., Wan, G.G., Wang, Y.Y., Huang, C.Y., Zhang, S.B., Huang, Y.Y., Ma, J.N.,
2022. E-minBatch GraphSAGE: An industrial internet attack detection model. Secur.
Commun. Netw. 2022, 1–12.
Marín, G., Casas, P., Capdehourat, G., 2019. Deep in the dark-deep learning-based
malware traffic detection without expert knowledge. In: 2019 IEEE Security and
Privacy Workshops. SPW, IEEE, pp. 36–42.
Mirsky, Y., Doitshman, T., Elovici, Y., Shabtai, A., 2018. Kitsune: an ensemble
of autoencoders for online network intrusion detection. In: 2018 Network and
Distributed Systems Security (NDSS) Symposium. pp. 1–15.
Moore, A.W., Zuev, D., 2005. Internet traffic classification using bayesian analysis
techniques. In: Proceedings of the 2005 ACM SIGMETRICS International Conference
on Measurement and Modeling of Computer Systems. pp. 50–60.
Niu, Z., Xue, J., Qu, D., Wang, Y., Zheng, J., Zhu, H., 2022. A novel approach based
on adaptive online analysis of encrypted traffic for identifying malware in IIoT.
Inform. Sci. 601, 162–174.
Okada, Y., Ata, S., Nakamura, N., Nakahira, Y., Oka, I., 2011. Comparisons of machine
learning algorithms for application identification of encrypted traffic. In: 2011 10th
International Conference on Machine Learning and Applications and Workshops.
Vol. 2, IEEE, pp. 358–361.
Prasse, P., Machlica, L., Pevnỳ, T., Havelka, J., Scheffer, T., 2017. Malware detection by
analysing network traffic with neural networks. In: 2017 IEEE Security and Privacy
Workshops. SPW, IEEE, pp. 205–210.
Shams, E.A., Rizaner, A., 2018. A novel support vector machine based intrusion
detection system for mobile ad hoc networks. Wirel. Netw. 24, 1821–1829.
Sun, P., Liu, P., Li, Q., Liu, C., Lu, X., Hao, R., Chen, J., 2020. DL-IDS: Extracting
features using CNN-LSTM hybrid network for intrusion detection system. Secur.
Commun. Netw. 2020, 1–11.
Wang, S., Yan, Q., Chen, Z., Yang, B., Zhao, C., Conti, M., 2017a. Detecting android
malware leveraging text semantics of network flows. IEEE Trans. Inf. Forensics
Secur. 13 (5), 1096–1109.
Wang, W., Zhu, M., Zeng, X., Ye, X., Sheng, Y., 2017b. Malware traffic classification using convolutional neural network for representation learning. In: 2017 International
Conference on Information Networking. ICOIN, IEEE, pp. 712–717.

1. Although current flow-level features of network traffic have
been greatly expanded than original five-tuples, the process of
extending flow-level features is a complex and long process,
it is necessary to study a more comprehensive and reliable
framework to extract more effective flow-level features to further
improve the detection efficiency of malicious traffic.
2. In the multi-head self-attention model, it is possible to further
optimize the weight learning ability of features. In the future, it
can be considered to introduce more levels of attention structure
to make the model can select and integrate more fine-grained
features, thereby further improving the model’s ability to learn
the correlation and importance between different features.
CRediT authorship contribution statement
Jinfu Chen: Writing – review & editing, Writing – original draft,
Validation, Methodology, Investigation, Funding acquisition, Data curation. Haodi Xie: Writing – review & editing, Writing – original draft,
Validation, Methodology, Investigation. Saihua Cai: Writing – review
& editing, Writing – original draft, Methodology, Funding acquisition,
Data curation. Luo Song: Writing – review & editing, Data curation.
Bo Geng: Writing – review & editing. Wuhao Guo: Writing – review
& editing.
Declaration of competing interest
The authors declare that they have no known competing financial interests or personal relationships that could have appeared to
influence the work reported in this paper.
Data availability
Data will be made available on request.
Acknowledgments
This work was partly supported by the National Natural Science
Foundation of China (NSFC) (Grant nos. 62172194, 62202206 and
U1836116), the China Postdoctoral Science Foundation (Grant no.
2023T160275), the Natural Science Foundation of Jiangsu Province,
China (Grant no. BK20220515), and Qinglan Project of Jiangsu Province,
China.
13

Computers & Security 147 (2024) 104083

J. Chen et al.
Wu, Z., Li, H., Liuliang, Zhang, J., Yuemeng, Leijin, 2020. Detection of LDoS attacks
based on wavelet energy entropy and hidden semi-Markov models. J. Softw. 31
(5), 1549–1562.
Wu, F., Li, T., Wu, Z., Wu, S., Xiao, C., 2021. Research on network intrusion detection
technology based on machine learning. Int. J. Wirel. Inf. Netw. 28 (3), 262–275.
Xiao, J., Yang, L., Zhong, F., Chen, H., Li, X., 2023. Robust anomaly-based intrusion
detection system for in-vehicle network by graph neural network framework. Appl.
Intell. 53 (3), 3183–3206.
Zhang, B., Liu, Z., Jia, Y., Ren, J., Zhao, X., 2018. Network intrusion detection method
based on PCA and Bayes algorithm. Secur. Commun. Netw. 2018, 1–11.
Zheng, J., Zeng, Z., Feng, T., 2022. GCN-ETA: high-efficiency encrypted malicious traffic
detection. Secur. Commun. Netw. 2022, 1–11.
Zhou, G., Liu, Z., Fu, C., Li, Q., Xu, K., 2023. An efficient design of intelligent network
data plane. In: Proceedings of the 32nd USENIX Conference on Security Symposium.
SEC ’23, USENIX Association, pp. 6203–6220.
Zola, F., Segurola-Gil, L., Bruse, J.L., Galar, M., Orduna-Urrutia, R., 2022. Network
traffic analysis through node behaviour classification: a graph-based approach with
temporal dissection and data-level preprocessing. Comput. Secur. 115, 102632.

Saihua Cai received his Ph.D. degree in Agricultural Engineering from China Agricultural University, Beijing, China,
in 2020. He is currently an associate professor in the
School of Computer Science and Communication Engineering, Jiangsu University, Zhenjiang, China. His major
research interests include malicious traffic detection, outlier
detection and software testing. He has published more than
70 papers in journals or conferences, including in ACM
Transactions on Privacy and Security, IEEE Transactions on
Reliability, Information Sciences, Computers & Security, The
Computer Journal, Knowledge-Based Systems, ISSRE, and
QRS, etc. He is a member of the IEEE and the ACM, and a
member of the China Computer Federation.

Luo Song received the B.E. degree in 2021 in Software
Engineering from Jiangsu University, Zhenjiang, China. He
is currently working towards the Master’s degree in Computer Technology at Jiangsu University, Zhenjiang, China.
His research interest includes encrypted malicious traffic
detection.

Jinfu Chen received the Ph.D. degree in computer science and technology from Huazhong University of Science
and Technology, Wuhan, China, in 2009. He is currently
a full professor in the School of Computer Science and
Communication Engineering, Jiangsu University, Zhenjiang,
China. His major research interests include software testing,
software security, and trusted software. He has published
more than 80 papers in some famous journals or conferences, including in ACM Transactions on Privacy and
Security, IEEE Transactions on Reliability, Information Sciences, Journal of Systems and Software, Information and
Software Technology, Software: Practice and Experience,
IET Software, The Computer Journal, ISSTA, ASE, ISSRE,
and QRS. He is a member of the IEEE and the ACM, and a
member of the China Computer Federation.

Bo Geng received the B.E. degree in 2020 in Material
science and technology from Harbin institute of technology, Harbin, China. He is currently working towards the
Master’s degree in Control Science and Engineering at
Jiangsu University, Zhenjiang, China. His research interest
includes malicious traffic detection and adversarial attacks
and defenses.

Wuhao Guo received the Master degree from Nanjing
University, he is currently working towards the Ph.D degree
at the School of Cyberspace Security, Southeast University.
He has joined in AsiaInfo Security in 2021, holding positions
as the Vice President, General Manager of the COO Office,
General Manager of the Solutions and Technical Support
Department, and General Manager of the Digital Support
Department. His major research interests include malicious
traffic detection, data security, and software security.

Haodi Xie received the B.E. degree in 2021 in Software
Engineering from Nantong Institute of Technology, Nantong, China. He is currently working towards the Master’s
degree in Computer Technology at Jiangsu University, Zhenjiang, China. His research interest includes malicious traffic
detection and graph neural network.

14
PAPER_TEXT
