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
# [100] DarknetSec: A novel self-attentive deep learning method for darknet traffic classification and application identification
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
编号：100
题名：DarknetSec: A novel self-attentive deep learning method for darknet traffic classification and application identification
年份：2022
DOI：10.1016/j.cose.2022.102663
来源：Computers & Security
PDF：paper/10.1016_j.cose.2022.102663.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测、恶意流量、暗网与攻击检测
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\100.txt
- 原始字符数：81480
- 本次发送字符数：81480
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Computers & Security 116 (2022) 102663

Contents lists available at ScienceDirect

Computers & Security
journal homepage: www.elsevier.com/locate/cose

DarknetSec: A novel self-attentive deep learning method for darknet
traﬃc classiﬁcation and application identiﬁcation
Jinghong Lan a,b,∗, Xudong Liu a,b, Bo Li a,b, Yanan Li c, Tongtong Geng d
a

School of Computer Science and Engineering, Beihang University, Beijing, China
Beijing Advanced Innovation Center for Big Data and Brain Computing, Beihang University, Beijing, China
c
School of Computer and Information Security, Guilin University of Electronic Technology, Guilin, China
d
School of Economics and Management, Xidian University, Xi’an, China
b

a r t i c l e

i n f o

Article history:
Received 20 October 2021
Revised 10 January 2022
Accepted 15 February 2022
Available online 17 February 2022
Keywords:
Darknet traﬃc
Convolutional neural network
Long short-term memory
Self-attention mechanism
Spatial-temporal features
Classiﬁcation

a b s t r a c t
Darknet traﬃc classiﬁcation is crucial for identifying anonymous network applications and defensing cyber crimes. Although notable research efforts have been dedicated to classifying darknet traﬃc by combining machine learning algorithms and elaborately designed features, current methods either heavily
depend on hand-crafted features or overlook the global intrinsic relationships among the local features
automatically extracted from different data positions, leading to limited classiﬁcation performance. To
tackle this issue, we propose DarknetSec, a novel self-attentive deep learning method for darknet trafﬁc classiﬁcation and application identiﬁcation. Concretely, DarknetSec utilizes a cascaded model with a
1-dimensional Convolutional Neural Network (1D CNN) and a bidirectional Long Short-Term Memory (BiLSTM) network to capture local spatial-temporal features from the payload content of packets, while the
self-attention mechanism is integrated into the abovementioned feature extraction network to mine the
intrinsic relationships and hidden connections among the previously extracted content features. In addition, DarknetSec extracts side-channel features from payload statistics to enhance its classiﬁcation performance. We evaluate DarknetSec on the CICDarknet2020 dataset, which is a representative of darknet
traﬃc covering both Virtual Private Network (VPN) and The Onion Router (Tor) applications. Thorough
experiments show that DarknetSec is superior to other state-of-the-art methods, achieving a multiclass
accuracy of 92.22% and a macro-F1-score of 92.10%. Additionally, DarknetSec maintains its high accuracy
when applied to other encrypted traﬃc classiﬁcation tasks.
© 2022 Elsevier Ltd. All rights reserved.

1. Introduction
Darknet is described as an individual encrypted part of the Internet that can only be accessed with speciﬁc anonymity tools
such as The Onion Router (Tor), Invisible Internet Project (I2P),
Virtual Private Network (VPN), and JonDonym (generally known
as Java Anon Proxy, JAP, or WebMix) (Montieri et al., 2018). The
earliest case of using darknet can be traced back to 1971, when
two students from the Massachusetts Institute of Technology and
Stanford University used the Advanced Research Project Agency
(ARPANET) to trade marijuana in the artiﬁcial intelligence laboratory of the Massachusetts Institute of Technology (Buxton and
Bingham, 2015). Since the ARPANET was formed, the deﬁnition of

∗
Corresponding author at: School of Computer Science and Engineering, Beihang
University, Beijing, China.
E-mail addresses: lanjh@act.buaa.edu.cn (J. Lan), liuxd@act.buaa.edu.cn (X. Liu),
libo@act.buaa.edu.cn (B. Li), xxgcliyanan@163.com (Y. Li), gtt.jesse@veda.com (T.
Geng).

https://doi.org/10.1016/j.cose.2022.102663
0167-4048/© 2022 Elsevier Ltd. All rights reserved.

darknet has been extended to Peer-to-Peer (P2P) networks and private networks such as Tor (Barratt, 2015; Wood, 2009). After the
publication of “The Darknet and the Future of Content Distribution” in 2002 (Biddle et al., 2002), the concept of darknet has
gained wide acceptance in academic communities. It should be
noted that in some previous literature, darknet is also deﬁned as
the unused address space of the Internet (also known as network
telescopes, sinkholes, or blackholes) that has not been assigned
to any hosts or devices (Fachkha and Debbabi, 2015; Iglesias and
Zseby, 2017; Niranjana et al., 2020). However, such type of darknet is beyond the scope of this paper and will be left for future
research.
Through encryption techniques and P2P connection networks,
darknet provides anonymous services to individual users and can
effectively combat routing eavesdropping and other traﬃc analysis techniques, thus ensuring the conﬁdentiality and integrity of
the communication data. In the ﬁrst quarter of 2020, nearly two
million worldwide users directly connected to Tor services, while
approximately 50,0 0 0 users indirectly connected to Tor services

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

through bridges (Habibi Lashkari et al., 2020). Due to its anonymous nature, darknet is widely used for criminogenic activities,
such as drug dealing, arms smuggling, child pornography, terrorism and cyberattacks (e.g., botnets) (Adewopo et al., 2019; Al-Nabki
et al., 2019). Therefore, accurately identifying darknet traﬃc and its
corresponding application types is very meaningful for monitoring malware propagation early, detecting malicious activities and
combating cybercrimes. Although private networks and encryption
techniques provide individual users with anonymity, the interactive network traﬃc generated when an end user visits a darknet
application can still reveal the intrinsic characteristics of the hidden network service (Dong et al., 2020; Lin et al., 2021; Shapira
and Shavitt, 2021). Indeed, as an essential part of traﬃc engineering, network traﬃc classiﬁcation can be used to identify the speciﬁc darknet application type that an end user communicates with.
Previous works on network traﬃc classiﬁcation can be distributed into three main categories according to their analysis approaches: port-based, signature-based and statistical-based techniques (Xie et al., 2021). Port-based methods rely on the speciﬁc
transport port numbers registered by the Internet Assigned Numbers Authority (IANA) to represent well-known services; such approaches are prone to failure due to the widespread use of dynamic ports and covert channel techniques. Signature-based methods generally use payload analysis techniques such as Deep Packet
Inspection (DPI) to mine unique signatures from packet payloads
and judge whether the traﬃc to be inspected contains a speciﬁc signature. However, due to the adoption of encrypted communication techniques, conventional signature-based methods fail
to analyze darknet traﬃc. Statistical-based methods extract trafﬁc features at the packet-level or ﬂow-level and leverage machine learning algorithms to train a classiﬁer to distinguish between different traﬃc types. Since machine learning has made
great progress in many classiﬁcation-related ﬁelds, statistical-based
methods have become a research hotspot in network traﬃc classiﬁcation, attracting widespread attention from both academia and
industry (Pacheco et al., 2018).
At present, many researchers mainly adopt the technical route
of executing data-driven methods to make full use of the powerful learning capabilities of machine learning algorithms to solve
the darknet traﬃc classiﬁcation problem. For instance, several conventional machine learning methods, including the Light Gradient Boosting Machine (LightGBM), K-nearest Neighbor (KNN) algorithm, Logistic Regression (LR), Random Forest (RF), Naive Bayesian
(NB) model and Decision Tree (DTree) (Kumar et al., 2019; Montieri et al., 2018; 2019), have already been applied to this research ﬁeld. However, in terms of model training, these methods
either rely heavily on hand-crafted features or resort to a timeconsuming feature selection process, thus leading to unstable performance when dealing with different network environments. As
a further improvement, deep learning methods (Dong et al., 2020;
Habibi Lashkari et al., 2020; Lin et al., 2021; Shapira and Shavitt,
2021; Singh et al., 2021) such as Convolutional Neural Networks
(CNNs) and Recurrent Neural Networks (RNNs) have also been introduced to automatically extract high-level features representations from network traﬃc, thus signiﬁcantly reducing the reliance
on domain experts and improving the generalizability for different network environments. Compared with conventional machine
learning approaches, deep learning possesses an advantage in that
features are not extracted manually but rather are automatically
learned from the input data through a neural network. However,
current deep learning-based methods mainly concentrate on extracting local spatial or temporal features from network traﬃc,
whereas the global intrinsic dependency relationships and hidden
connections among the local features extracted from different data
positions are not fully considered, which ultimately leads to unsatisﬁed classiﬁcation performance.

To tackle the aforementioned problems, in this paper, we propose DarknetSec, a novel self-attentive deep learning method for
darknet traﬃc classiﬁcation and application identiﬁcation. Each
part of DarknetSec processes the payload content or payload statistics of a network ﬂow. Concretely, a self-attention-embedded 1D
CNN and a bidirectional Long Short-Term Memory (Bi-LSTM) network are leveraged to extract local spatial-temporal features from
the payload content of packets, and a multi-head self-attention
module is designed to deal with the payload content in parallel.
The output of the multi-head self-attention module and the local
spatial-temporal features extracted by the self-attention-embedded
1D CNN and Bi-LSTM network are simultaneously fed into another
attention module to automatically capture the global intrinsic dependency relationships and hidden connections among the local
spatial-temporal features with different attention weights. Additionally, to enhance classiﬁcation accuracy, a side-channel feature
learning module is leveraged to extract feature representations
from the payload statistics. Finally, the multiple abovementioned
deep features are concatenated into a single vector and fed into
a classiﬁcation layer to obtain predictions. Thorough experiments
on the CICDarknet2020 dataset show that the adoption of the selfattention mechanism, as well as the comprehensive consideration
of both side-channel features and content features, signiﬁcantly
improves the accuracy of darknet traﬃc classiﬁcation and application identiﬁcation.
In summary, the main contributions of this paper are as follows:
• The 1D CNN, Bi-LSTM network and self-attention mechanism
are integrated into a classiﬁer to capture eﬃcient local spatialtemporal features and mine the global intrinsic dependency relationships and hidden connections among them. To the best of
our knowledge, this is the ﬁrst study that addresses the darknet
traﬃc classiﬁcation problem using a multi-head self-attention
module.
• We propose DarknetSec, a powerful end-to-end deep learningbased classiﬁcation architecture using both side-channel features and content features. Our experiments show that DarknetSec can not only accurately classify darknet traﬃc but also
maintain a high accuracy when applied to other encrypted trafﬁc classiﬁcation tasks.
• Extensive experiments conducted on the CICDarknet2020
dataset show that DarknetSec signiﬁcantly outperforms other
state-of-the-art methods in terms of the accuracy and F1score metrics, demonstrating its superiority to effectively classify darknet traﬃc and identify its underlying application types.
The rest of this paper is organized as follows. Section 2 reviews
the state-of-the-art related work. The system architecture of DarknetSec and its key components are detailed in Section 3. Experimental evaluations are presented in Section 4, and we conclude
this paper in Section 5.
2. Related work
In this section, we review the related studies that investigate,
analyze and classify darknet traﬃc, and we also shed light on encrypted traﬃc classiﬁcation and spatial-temporal feature learning
for classiﬁcation-related tasks.
2.1. Darknet traﬃc analysis
In the last decade, academic communities have published a
large number of representative works on darknet traﬃc analysis. For instance, Iliadis and Kaifas (2021) conducted a comparative study of feature selection and classiﬁcation model chosen
2

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

for the accurate prediction of darknet traﬃc on the CICDarknet2020 dataset. Shahbar and Zincir-Heywood (2017) proposed to
use a C4.5 classiﬁer with network ﬂow-level features to proﬁle the
users and applications on the I2P networks. Rao et al. (2018) proposed an unsupervised method with gravitational clustering to
identify Tor network ﬂows from non-anonymous network data.
Montieri et al. (2018) used several conventional machine learning methods (NB, C4.5, and RF) to classify anonymous services
(Tor, I2P, and JonDonym) and predict the speciﬁc application types
from both ﬂow-based and packet-based perspectives. More recently, deep learning having the ability of dealing with complex structures of high dimensional data has also been introduced to this research ﬁeld. Sarwar et al. (2021) adopted modiﬁed Convolution-LSTM (CNN-LSTM) and Convolution-Gradient Recurrent Unit (CNN-GRU) deep learning techniques to conduct the
darknet traﬃc classiﬁcation and application identiﬁcation task.
Sirinam et al. (2019) proposed to use triplet networks with a KNN
classiﬁer to perform website ﬁngerprinting against Tor anonymity
systems. Pour et al. (2020) designed a binary classiﬁer based on a
CNN to identify compromised IoT devices by merely operating on
darknet traﬃc, thus providing essential evidence for inferring ongoing orchestrated botnets. Habibi Lashkari et al. (2020) proposed
DeepImage, which converts the optimized statistical features selected by a forest of tree classiﬁers into gray images and trains a 2dimensional CNN (2D CNN)-based classiﬁer to classify darknet trafﬁc. Singh et al. (2021) proposed a deep transfer learning architecture consisting of a pre-trained model and a baseline classiﬁer to
distinguish darknet traﬃc from benign traﬃc. Lin et al. (2021) proposed combining a 1D CNN and a stacked Bi-LSTM network to automatically extract high-level feature representations for the ﬁnegrained classiﬁcation of Tor traﬃc.

ing methods have already adopted the attention mechanism to pay
increased attention to the features that contribute most to trafﬁc classiﬁcation. However, instead of fully mining the global internal dependencies and hidden connections among the extracted
local features during the feature extraction process, these methods only apply a single attention layer to the output feature vector, thus leaving much room for improvement (Dong et al., 2020;
Liu et al., 2020b; Yao et al., 2019). In addition, to the best of our
knowledge, the multi-head self-attention mechanism has not been
used for darknet traﬃc classiﬁcation in previous studies.

2.3. Spatial-temporal feature learning
Spatial-temporal feature learning is widely used in
classiﬁcation-related tasks, such as image classiﬁcation, fault
diagnosis, traﬃc ﬂow prediction and network intrusion detection. Here, we only discuss those works that are closely related
to this paper. Hassan et al. (2020), Kanna and Santhi (2021),
Xie et al. (2020) used a CNN and a LSTM network successively
to extract the spatial-temporal features of network traﬃc for
intrusion detection. Speciﬁcally, Hassan et al. (2020) proposed a
hybrid deep learning model to detect network intrusions based
on a CNN and a weight-dropped LSTM (WDLSTM) network. The
deep CNN was used to extract spatial features from network traﬃc
data, and the WDLSTM was used to extract long-term temporal
dependencies from the features extracted by the CNN. Kanna and
Santhi (2021) proposed a uniﬁed model of an optimized CNN
(OCNN) and a hierarchical multi-scale LSTM (HMLSTM) network
to extract spatial-temporal features from the input network
ﬂows, while the Lion Swarm Optimization (LSO) algorithm is
adopted to ﬁne-tune the hyperparameters of the former OCNN.
Xie et al. (2020) proposed HSTF-Model, an HTTP-based Trojan
detection model based on the hierarchical spatial-temporal features of traﬃc at both packet-level and network ﬂow-level. The
authors used a standard CNN to extract spatial information and an
LSTM network to extract temporal information. In terms of fault
diagnosis, some representative works like (Yang et al., 2020a;
2020b) leveraged a cascaded model of a CNN and a GRU network
to capture the spatial relations and long-term temporal dependencies among the time series signals collected from multiple
sensors. Similarly, researchers also used the combination of CNN
and RNN for traﬃc ﬂow prediction in the intelligent transportation
systems (Liu et al., 2020a; Zheng et al., 2020).
Compared with conventional machine learning methods, deep
learning can capture nonlinear features from the input data more
effectively. Additionally, in terms of classiﬁcation tasks, the cascade of CNN and RNN has also been proven to be suitable for
extracting discriminative and expressive feature representations
from the original input data with spatial-temporal characteristics
(e.g., network traﬃc, time series of sensor signals). Furthermore,
Sarwar et al. (2021) compared the performance of conventional
machine learning and deep learning methods especially for darknet
traﬃc classiﬁcation, and demonstrated that deep learning is more
accurate than conventional machine learning methods. Therefore,
this paper takes a 1D CNN and a Bi-LSTM network as the basic unit
to learn local spatial-temporal feature representations from the input network ﬂows, and the self-attention mechanism is integrated
into the deep feature extraction process to fully mine the inherent
dependencies of the extracted local spatial-temporal features, thus
contributing to capturing global and discriminative feature representations for ﬁne-grained darknet traﬃc classiﬁcation. Besides, instead of using a CNN with a ﬁxed convolution kernel size, we use
multiple convolution kernels of different sizes to extract different
local spatial features of the input network ﬂows and combine them
to realize the accurate darknet traﬃc identiﬁcation.

2.2. Encrypted traﬃc classiﬁcation
Various works utilize machine learning-based methods to
deal with encrypted traﬃc classiﬁcation tasks, such as webpage ﬁngerprinting (Shen et al., 2020), IoT device identiﬁcation (Pinheiro et al., 2019), malicious communication detection (Fang et al., 2021) and encrypted application classiﬁcation
(Dong et al., 2020; Liu et al., 2020b; Shapira and Shavitt, 2021;
Shen et al., 2021; Yao et al., 2019).
Shen et al. (2020) used the packet length information of clientserver interactions to perform webpage ﬁngerprinting. Speciﬁcally, three types of features, i.e., block features, sequence features, and statistical features, were extracted during the uplinkdominant stage and fed into a conventional machine learning
model (e.g., RF, KNN or DTree) to generate a ﬁne-grained classiﬁer. Pinheiro et al. (2019) utilized packet length statistics and
packet transmission rates to classify IoT and non-IoT devices.
Fang et al. (2021) presented a communication channel-based
method to detect malicious HTTPS traﬃc. Network packets with
the same destination IP address and destination port were aggregated into a communication channel, and three types of features, i.e., distribution features, consistency features and statistical features, were extracted independently. Subsequently, a genetic
algorithm-based method was used for feature selection, and a ﬁnal
classiﬁer was built based on the RF algorithm.
For the encrypted application classiﬁcation, recent studies have
tended to utilize the powerful non-linear learning abilities of
deep learning algorithms to obtain effective feature representations automatically, including 2D CNN (Shapira and Shavitt, 2021),
1D CNN with a bidirectional Gate Recurrent Unit (Bi-GRU) network (Dong et al., 2020), LSTM network with a hierarchical
attention mechanism (Yao et al., 2019), graph neural network
(GNN) (Shen et al., 2021), and Bi-GRU network with an attention
mechanism (Liu et al., 2020b). It is worth noting that several exist3

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663
Table 1
List of notations.
Notation

Description

Pi
bij
N
M
xsta
xseq
xsc f
xcontent
L
H
K
Q
V
osc f
omsa
olst f
oac f f
yˆ
y

The ith packet of a network ﬂow with only payload content
The jth byte of the ith packet
Number of packets kept in a network ﬂow for content feature extraction
Number of bytes kept in a packet for content feature extraction
Statistical features
Sequential features
Side-channel features
Content features
Size of the input packet length sequence
Number of heads in the multi-head self-attention module
Key matrix of the self-attention mechanism
Query matrix of the self-attention mechanism
Value matrix of the self-attention mechanism
Output of the side-channel feature learning module
Output of the multi-head self-attention module
Output of the local spatial-temporal feature learning module
Output of the attentive content feature fusion module
Predicted probability vector of being a speciﬁc application type
True label of ground truth presented in a one-hot encoding vector

3. The proposed DarknetSec

3.2. Preprocessing layer

In this work, we propose DarknetSec, a self-attentive deep feature learning architecture, to classify darknet traﬃc and identify its
speciﬁc application types. We present the overview and design details of each layer in DarknetSec. In summary, DarknetSec is a typical end-to-end classiﬁcation solution for darknet traﬃc that outputs the application type of each network ﬂow. The notations introduced in this paper are presented in Table 1.

In this subsection, we focus on discussing the selection of suitable features to handle the darknet traﬃc classiﬁcation problem.
We select two types of features from the input network traﬃc, i.e.,
content features and side-channel features. Since raw network trafﬁc is usually stored in pcapng or pcap ﬁles, whose formats cannot
be directly used for machine learning, preprocessing is essential to
split the raw packets into network ﬂows. In this paper, a network
ﬂow is deﬁned as a set of packets belonging to the same transportlevel communication that have the same ﬁve-tuples (source IP address, destination IP address, source port, destination port, and
transport-layer protocol) in both directions, i.e., the source IP address/port can be exchanged with the destination IP address/port
correspondingly. This deﬁnition of a network ﬂow is widely used
in network traﬃc classiﬁcation-related literature.
Although the protocol ﬁelds of the network layer and transport
layer are essential parts of a packet, they are mainly designed for
network transmission rather than application identiﬁcation. Furthermore, the protocol ﬁelds below the application layer contain
little effective information and cannot adequately provide discriminative features for ﬁne-grained traﬃc classiﬁcation. Consequently,
when extracting ﬁve-tuple network ﬂows, we remove the packet
header and retain only the application layer data for each packet.
Moreover, packets with no application layer data, malformed packets, loop packets, and retransmitted packets are discarded. As an
example, the statistical distribution of network ﬂows containing
application layer data in the CICDarknet2020 dataset is shown in
Fig. 2. Despite of the imbalance of traﬃc categories,we still can
obtain enough training samples to build an accurate traﬃc classifer. Note that the same packet preprocessing approach was also
used by Dong et al. (2020), in which the VPN part of the CICDarknet2020 dataset was used to perform application classiﬁcation to
demonstrate that only using the application layer data of network
packets as inputs is eﬃcient for the encrypted traﬃc classiﬁcation
task.
Content features. Content features are extracted from the payload content of each selected packet. Since the number of packets
contained in a network ﬂow and the size of each packet are commonly uncertain and are determined by the speciﬁc application
type under study, a typical method is to select the ﬁrst N packets
of a network ﬂow while retaining the ﬁrst M bytes for each packet.
N and M are the two hyperparameters of DarknetSec. Note that if
a network ﬂow contains more than N packets, truncation is per-

3.1. DarknetSec overview
As shown in Fig. 1, DarknetSec is composed of three basic layers: a preprocessing layer, a feature learning layer and a classiﬁcation layer. The preprocessing layer takes raw packets as inputs and
splits them into network ﬂows. Then, two types of features, i.e.,
content and side-channel features, are simultaneously extracted
and converted into standard normalized vectors, which are fed into
the feature learning layer. The feature learning layer consists of a
side-channel feature learning module, a multi-head self-attention
module, a local spatial-temporal feature learning module, and an
attentive content feature fusion module. For the side-channel feature learning module, the side-channel features (statistical and sequential features) are fed into a Multilayer Perceptron (MLP) network to obtain abstract and high-level representations from the inputs, which will be proven to be helpful for improving the classiﬁcation performance in Section 4.3. The content features are duplicated into two copies, which are fed into the multi-head selfattention module and the local spatial-temporal feature learning
module to generate embedded feature representations. After that,
the attentive content feature fusion module is utilized to fuse the
outputs of the two content feature learning modules to highlight
the intrinsic relationships among the learned spatial-temporal features. In DarknetSec, the abovementioned feature learning modules
focus on different modalities of network traﬃc. The side-channel
feature learning module summarizes the statistical and sequential
characteristics from a global perspective, whereas the multi-head
self-attention module and local spatial-temporal feature learning
module present ﬁne-grained content representations for darknet
traﬃc classiﬁcation. The classiﬁcation layer concatenates the outputs of the side-channel feature learning module and the attentive
content feature fusion module. It is composed of a dense layer and
a softmax layer. The focal loss between the true labels and prediction probabilities is utilized for the overall training process.
4

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

Fig. 1. The architecture of DarknetSec.

Fig. 2. Distribution of network ﬂows containing application layer data in the CICDarknet2020 dataset.

formed; otherwise, it is padded with zeros. Similarly, if a packet
contains more or fewer than M bytes, preprocessing will be performed in the same way.
As shown in Fig. 3, in terms of content feature extraction and
vectorization, the encrypted input packet sequence is converted
into the ﬂow packet format to adapt to the local spatial-temporal
feature mining from packet bytes. The payload content of a network ﬂow is formalized as

xcontent = [P 1 , P 2 , . . . , P N ], N ∈ Z+

(1)

P i = [bi1 , bi2 , . . . , biM ], i ∈ [1, N]

(2)

Fig. 3. The payload vectorization method for a network ﬂow.

where xcontent represents the content features of a network ﬂow,
P i is the ith packet with only application layer data, and bij ∈
[0, 0xff], i ∈ [1, N], j ∈ [1, M] denotes the jth byte of the ith packet.
Then, data normalization is performed to map the numeric
packet bytes to [0,1] by dividing all byte values by 0xff.
Side-channel features. Side-channel features are deﬁned as the
information that can be extracted from encrypted network trafﬁc without decryption (Stergiopoulos et al., 2018); they are composed of statistical and sequential features. Multiple statistical fea5

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663
Table 2
Detailed descriptions of the selected side-channel features.
Feature Type

Feature description

Number

Statistical features

Flow duration
Time intervals among packets(max, min, mean, standard deviation, median)
Packet length statistics(max, min, mean, standard deviation, median)
Inbound packet length statistics(max, min, mean, standard deviation, median)
Outbound packet length statistics(max, min, mean, standard deviation, median)
Number of packets/bytes
Number of inbound packets/bytes
Number of outbound packets/bytes
Number of packets/bytes per second
Number of inbound packets/bytes per second
Number of outbound packets/bytes per second
Ratio of inbound and outbound packets/bytes
Packet length vector for the ﬁrst L packets

35

Sequential features

tures are extracted from the payload content of packets based on
the granularity of a network ﬂow, and the packet length vector for
the ﬁrst L packets of a network ﬂow is selected as the sequential
features. Note that L is a hyperparameter and will be discussed in
Section 4.2. Detailed descriptions of the selected side-channel features is presented in Table 2. Additionally, to eliminate the negative effects of different side-channel feature value ranges on the
classiﬁer, as deﬁned in Eq. (4), a normalization method called the
“min-max” is utilized for the side-channel data preprocessing. Finally, the statistical features, sequential features and side-channel
features are denoted as xsta , xseq , and xsc f , respectively.

x=

x − xmin
xmax − xmin

L

malized as



i

h =

σ (W i xsc f + bi ), i = 1
σ (W i hi−1 + bi ), 1 < i ≤ Z

(4)

where W i , bi , and hi denote the weight matrix, bias vector, and
output vector of layer i, respectively. σ () is a non-linear activation
function. The MLP is introduced to capture an abstract representation from the original numerical side-channel features. This representation is combined with the output of the attentive content
feature fusion module to determine the ﬁnal classiﬁcation.
3.3.2. Multi-head self-attention module
For traﬃc classiﬁcation tasks, network traﬃc is often sequential, and internal dependencies commonly exist among the payload
content of packets. Thus, we need to develop an appropriate approach that not only pays attention to extracting spatial-temporal
representations from the payload content, but also considers their
inherent dependencies. Sequence encoding based on CNNs or RNNs
is essentially a type of local encoding method that only models
the local dependencies among the input data. Although RNNs can
theoretically establish long-distance dependencies, they are limited
by the information storage capacity and vanishing gradient problems, thus resulting in only short-distance dependencies. In addition, improved RNNs such as LSTM also have some shortcomings. For example, LSTM considers the later features to be more
important than the previous ones. In this paper, inspired by the
network structure of Transformer (Vaswani et al., 2017), which is
a sequence learning model based on attention mechanisms, we
leverage a multi-head self-attention network to mine the multidimensional dependencies inherent within a network ﬂow and dynamically generate attentive weights for different data positions
of the input network ﬂows. The multi-head self-attention network
can adaptively pay more attention to speciﬁc parts of the input
that are related to the classiﬁcation and give less attention to
the irrelevant parts, thus contributing to better capturing complex
spatial-temporal representations from the input network ﬂows.
The self-attention mechanism usually adopts a query-key-value
(QKV) mode, whose calculation procedure is shown in Fig. 4. We
ﬁrst map the input xcontent ∈ RN×M linearly into three different
spaces to obtain a query matrix Q , a key matrix K , and a value
matrix V . This linear mapping can be formalized as

(3)

where xmin and xmax denote the minimum and maximum values
of feature x, respectively.

3.3. Feature learning layer
To obtain high-level representations from the original sidechannel features and content features, we design a side-channel
feature learning module, a multi-head self-attention module, a local spatial-temporal feature learning module, and an attentive content feature fusion module.
First, the statistical features xsta and sequential features xseq are
concatenated into a single vector as the side-channel features xsc f ,
which are subsequently fed into an MLP network. The content features xcontent are duplicated into two copies and simultaneously
handled by the multi-head self-attention module and local spatialtemporal feature learning module. Then, the outputs of the two
abovementioned content feature learning modules ﬂow to an attentive content feature fusion module to capture the corresponding weighted spatial-temporal representations. Finally, the sidechannel feature learning module generates an output osc f , while
the attentive content feature fusion module generates an output
oac f f . These two output vectors are fed into the classiﬁcation layer
to generate the ﬁnal prediction.

3.3.1. Side-channel feature learning module
The MLP is one of the most basic type of neural networks. The
neurons in two adjacent layers are fully connected, so the MLP is
also called the fully connected neural network. An MLP classiﬁer
is a typical machine learning model with strong nonlinear representation ability that is widely used in classiﬁcation-related tasks.
For the side-channel features xsc f , we leverage an MLP network
to mine high-level representations from the input data. osc f is the
output of this module, as shown in Fig. 1(osc f = hZ ). More specifically, the MLP used for side-channel feature learning can be for6

Q = W q xcontent ∈ RDk ×M

(5)

K = W k xcontent ∈ RDk ×M

(6)

V = W v xcontent ∈ RDv ×M

(7)

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

Fig. 4. The calculation procedure of the self-attention mechanism model.

our model, gconv () is leveraged to capture local spatial representations from the input content features. It is worth noting that since
the spatial feature dimension is not large, a pooling layer is not
used after the 1-dimensional convolution function.
Batch normalization is a technique used to improve the performance and stability of neural networks. It generates an input with
zero mean/unit variance for any layer of a speciﬁc neural network.
Even if the mean and variance change during the training process,
batch normalization can standardize the data adaptively, thus facilitating gradient propagation and speeding up the training process.
The calculation process of normalization can be formalized as

where W q ∈ RDk ×N , W k ∈ RDk ×N , and W v ∈ RDv ×N denote the three
parameter matrices of the linear mapping, which are randomly initialized and updated through backpropagation during the training
process.
The query matrix Q and key matrix K are used to generate a
distribution of attention weights, while the value matrix V is used
to obtain the selected information. The output matrix is calculated
as

K TQ
Attention(Q , K , V ) = V · Softmax(  )
Dk

(8)

exp(X i j )
Softmax(X i j ) = 
k exp (X k j )

(9)

gbn (x1 , x2 , . . . , xNbatch ) = (α xˆ1 + β , α xˆ2 + β , . . . , α xˆNbatch + β )
xˆi =

where Softmax() represents a column-wise-normalized function.
In this paper, we employ a multi-head self-attention module to
obtain better nonlinear representations; this module uses multiple
query vectors to select multiple sets of information from the input
data in parallel, and each attentive head focuses on a different part
of the input data. This provides an approach to fully mine the information from multiple representation subspaces at different positions. Speciﬁcally, the multi-head self-attention module can be
formalized as

x i − μb
δb + ξ

μb =

(15)


Nbatch

1
Nbatch


δb =

(14)

xi

(16)

i=1

1
Nbatch



Nbatch

( x i − μb ) 2

(17)

i=1

omsa = Multihead(Q , K , V ) = Concat(head1 , head2 , . . . , headH )W msa where xbn = x1 , x2 , . . . , xN
denotes the input of the batch norbatch
(10)
malization function, and μb and δb are the mean and standard deheadi = Attention(W qi xcontent , W ki xcontent , W vi xcontent )

viation of xbn , respectively. α ∈ R+ and β ∈ R are trainable neural
network parameters. ξ is an arbitrarily small constant.
As shown in Fig. 1, after the two-layer Conv1D network, a selfattention layer is placed before the Bi-LSTM network to associate
the positions of the local spatial features obtained by the Conv1D
network, which enriches the input features for the following BiLSTM network.
Bi-LSTM. After the two-layer Conv1D network and selfattention layer, we apply a Bi-LSTM network to perform comprehensive and thorough feature extraction for xcontent in view of the
temporal dependencies within a network ﬂow. Bi-LSTM consists of
a forward LSTM and a backward LSTM. Speciﬁcally, the calculation
process of an LSTM unit can be formulated as

(11)

Dv ×M

where H and omsa ∈ R
denote the head number and output
of the multi-head self-attention module, respectively, and W msa ∈
RHM×M , W qi ∈ RDk ×N , W ki ∈ RDk ×N , and W vi ∈ RDv ×N are parameter
matrices.
3.3.3. Local spatial-temporal feature learning module
As shown in Fig. 1, the local spatial-temporal feature learning
module consists of a two-layer Conv1D network, a self-attention
mechanism layer, and a Bi-LSTM network. It is a core component of
DarknetSec that aims to capture the local spatial-temporal patterns
of an input network ﬂow. The detailed descriptions are presented
as follows.
Conv1D. We utilize Conv1D to capture the spatial dependencies
of xcontent . Conv1D is composed of a 1D CNN layer, a batch normalization layer, and a Rectiﬁed Linear Unit (ReLU) activation function,
which can be formalized as

it = σ (W i xt + U i ht−1 + bi )

(18)

f t = σ (W f xt + U f ht−1 + b f )

(19)

oconv1d (x ) = grelu (gbn (gconv (x )))

(12)

ot = σ (W oxt + U oht−1 + bo )

(20)

gconv (x ) = W conv  x + bconv

(13)

ct = f t  ct−1 + it  tanh(W c xt + U c ht−1 + bc )

(21)

ht = ot  tanh(ct )

(22)

where x and oconv1d (x ) denote the input and output of a Conv1D
block, respectively. gconv (), gbn (), and grelu () are the 1-dimensional
convolution function, batch normalization function, and ReLU activation function, respectively. W conv , bconv , and  denote the parameter matrix, bias vector, and convolution operation, respectively. In

where W i , U i , W f , U f , W o, U o, bi , b f , bo denote trainable network
parameters, xt is the input vector at time step t, σ () is the
7

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

weight, γ is the focusing parameter, and c denotes the label of the
ground truth. Note that yc = 1 and that other yi (i = c ) values are
all equal to 0 in y ∈ RC .
By combining the side-channel feature learning and spatialtemporal content feature learning components, DarknetSec provides a ﬁnal prediction for each network ﬂow. Overall, the detailed
workﬂow of DarknetSec is presented in Algorithm 1 .

element-wise sigmoid activation function and tanh() is the hyperbolic tangent activation function.  denotes element-wise multiplication.
−
→
←
−
A forward hidden state h t and backward hidden state h t are
generated at time step t. The ﬁnal hidden state at time step t is obtained by concatenating the forward and backward hidden states,
−
→ ←
−
i.e., ht = [ h t ; h t ], The hidden state ht contains high-level spatialtemporal feature representations obtained from raw content features. In our model, we take all the hidden states of the Bi-LSTM
network as the output of the local spatial-temporal feature learning module, which is denoted as olst f .

Algorithm 1: The workﬂow of DarknetSec.
Input: 5-tuple network ﬂows extracted from raw network
traﬃc
Output: The predicted type of each network ﬂow
1 Generating xcontent , xsta and xseq ;
2 Initializing neural network parameters;
3 for each training iteration do
4
Selecting a batch of training samples;
5
xsc f = Concat(xsta , xseq );
6
osc f = MLP(xsc f );
7
omsa = Multi_head_self_attention(xcontent );
8
olst f =
Bi_LSTM(self_attention(Two_layer_Conv1D(xcontent )));
9
oac f f = Attentive(omsa , olst f ) =

3.3.4. Attentive content feature fusion module
Composed of an approximate self-attention layer and a dense
layer, the attentive content feature fusion module is designed to
fuse the outputs of the multi-head self-attention module and the
local spatial-temporal feature learning module, thereby helping to
obtain the inner dependency relationships among the different
data positions of a network ﬂow from a global perspective and
contributing to the learning of comprehensive content features.
More speciﬁcally, the output of the multi-head self-attention module serves as the key matrix K and query matrix Q , while the output of the local spatial-temporal feature learning module serves as
the value matrix V . The attentive content feature fusion module
can be further formalized as

oT

10

oac f f = Attentive(omsa , olst f )
oTmsa omsa
= W ac f f (olst f · Softmax( 
)) + bac f f
domsa

·o
domsa

msa msa
W ac f f (olst f · Softmax( √
)) + bac f f ;

11
12

(23)

oc = Dense(Concat(osc f , oac f f ));
Obtaining yˆ using a softmax layer: yˆ = softmax(oc );
Updating the trainable parameters of DarknetSec for the
current batch of training samples with the focal loss;

for each test iteration do
Selecting a batch of test data;
15
Calculating and saving yˆ = argmax(yˆ ) using the trained
parameters;

13

where domsa is the dimensionality of omsa used to control the scale,
and omsa , olst f , and oac f f denote the outputs of the multi-head selfattention module, local spatial-temporal feature learning module
and attentive content feature fusion module, respectively. W ac f f
and bac f f respectively denote the parameter matrix and bias vector
of the dense layer used to compress oac f f to a speciﬁed dimensionality.

14

16

return yˆ for all test network ﬂows;

4. Experimental evaluation
3.4. Classiﬁcation layer
In this section, we are dedicated to evaluate the performance of DarknetSec. We conduct most experiments on the CICDarknet2020 dataset, which is composed of VPN and Tor applications and acts as a real representative of darknet traﬃc
by merging two public datasets, namely, ISCXTor2016 and ISCXVPN2016 (Habibi Lashkari et al., 2020). Network ﬂow samples
are divided into two types: benign and darknet types, and the
numbers of benign and darknet network ﬂows containing application layer data are 102,480 and 21,041, respectively. The network ﬂows of darknet traﬃc in CICDarknet2020 can be divided
into eight categories, i.e., Audio-Stream, Browsing, Chat, Email, P2P,
File-Transfer, Video-Stream, and VOIP. Detailed descriptions of the
darknet applications are shown in Table 3.
In the following subsections, we start by introducing the experimental settings used for evaluation purposes. After that, we
present a comprehensive evaluation of DarknetSec from the following four perspectives. First, we perform experiments to discuss
the inﬂuences of several hyperparameters and their corresponding
optimal choices. Second, we conduct an ablation study to evaluate the contribution of each component of DarknetSec to the ﬁnal classiﬁcation performance. Third, we verify the effectiveness
of DarknetSec by comparing it with several state-of-the-art methods in both binary and multiclass classiﬁcation scenarios. Finally,
we demonstrate the generalizability and adaptability of DarknetSec on conventional encrypted traﬃc classiﬁcation tasks using two
other public datasets. Note that the experiments in Section 4.2,
4.3, and 4.5 involve only multiclass classiﬁcation scenarios, while

Composed of a dense layer and a softmax layer, the classiﬁcation layer combines the outputs of the side-channel feature learning module and the attentive content feature fusion module. Considering the class imbalance problem in darknet traﬃc classiﬁcation, we take the focal loss between the one-hot encoding vectors
of the true labels and the predicted probability distribution vectors
as the loss values of the backpropagation during the deep learningbased training process. The core idea of the focal loss function is
that samples which are diﬃcult to classify are important for the
entire classiﬁcation model.

oc = W c · Concat(osc f , oac f f ) + bc

(24)

yˆ = softmax(oc )

(25)

where osc f is the output vector of the side-channel feature learning
module, and oac f f is the output vector of the attentive content feature fusion module. W c and bc are the weight matrix and bias vector of the dense layer, respectively. oc and yˆ denote the outputs of
the dense layer and the predicted probability vector, respectively.
The focal loss function for a C-class classiﬁcation task can be formalized as

FL(yˆ , y, α , γ ) = −α (1 − yˆc )γ log(yˆc )
C

(26)

C

where y ∈ R and yˆ ∈ R denote the one-hot vector of the true label and the predicted probability vector, respectively. α is the class
8

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663
Table 3
Detailed descriptions of the darknet applications in CICDarknet2020.
Application type

Detailed description

Audio-Stream
Browsing
Chat
Email
P2P
File-Transfer
Video-Stream
VOIP

Vimeo and Youtube
Firefox and Chrome
ICQ, AIM, Skype, Facebook and Hangouts
SMTPS, POP3S and IMAPS
uTorrent and Transmission (BitTorrent)
Skype, FTP over SSH (SFTP) and FTP over SSL (FTPS) using Filezilla and an external service
Vimeo and Youtube
Facebook, Skype and Hangouts voice calls

both binary and multiclass classiﬁcation scenarios are discussed
in Section 4.4, which presents detailed performance comparisons
with other state-of-the-art methods.

4.1.2. Cross-validation
We use 10-fold cross-validation for the comparison experiments. We randomly divide the dataset into ten disjoint subsets
of equal size. For each experiment, we perform training and testing ten times, selecting one subset as the test set and the remaining nine subsets as the training set each time. We use the average value of the ten tests as the ﬁnal result. Note that all experiments are conducted on a personal computer with an Intel i78700K 3.7 GHz CPU, an NVIDIA GeForce GTX1650 4 GHz GPU and
32 GB of memory.

4.1. Experimental settings
4.1.1. Methods for comparative evaluation
To fully demonstrate the effectiveness of DarknetSec in terms of
darknet traﬃc classiﬁcation, we choose six existing representative
methods for comparison, which are brieﬂy introduced as follows.
Note that the parameters of all these methods are ﬁne tuned to obtain the best classiﬁcation performance on the evaluation datasets.
FlowPic, which transforms the basic byte data of each network ﬂow into a grayscale image and uses a typical 2D CNN to
classify the encrypted network traﬃc and identify the application
in use. FlowPic provides a generic representation learning model
for encrypted traﬃc classiﬁcation and application identiﬁcation,
where a LeNet-5-style architecture is leveraged to build the classiﬁer (Shapira and Shavitt, 2021).
CETAnalytics, which extracts high-level feature representations
for encrypted traﬃc classiﬁcation from both payload content and
payload statistics. A Bi-GRU network and a cascaded model composed of a 1D CNN and a Bi-GRU network are used to realize the
payload statistics and payload content analytics, respectively. Additionally, to improve accuracy and reduce dimensionality, a simple attention layer is introduced to the output of the feature extraction module to create the ﬁnal feature vector for classiﬁcation (Dong et al., 2020).
BGRUA, which uses a Bi-GRU network and an attention mechanism to classify web services running on HTTPS connections. Note
that the author only uses three consecutive packets of a network
ﬂow and 900 bytes for each packet to build the classiﬁer (Liu et al.,
2020b).
VGG19+RF, which transforms the time-based features of darknet traﬃc into three-dimensional images and uses a pre-trained
neural network model to perform feature extraction. After that, a
traditional machine learning method is introduced for classiﬁcation. The combination of VGG19 and RF is chosen as the best combination (Singh et al., 2021).
RF, which addresses traﬃc classiﬁcation for anonymous services
(Tor, I2P, JonDonym) in both ﬂow-based and packet-based classiﬁcation scenarios. For the ﬂow-based scenario, 74 ﬂow-based statistics are extracted, and several supervised classiﬁcation algorithms
are employed for classiﬁcation. Here, we consider only the ﬂowbased classiﬁcation scenario and chose the RF algorithm for comparison since it achieves the highest accuracy with respect to the
classiﬁcation of anonymous services (Montieri et al., 2018).
DIDarknet, which uses CICFlowMeter to extract 80 statistical
features from each network ﬂow of darknet traﬃc, after which an
RF-based feature selection method is employed to select the most
important features, which are then converted into grayscale images and fed into a 2D CNN for classiﬁcation (Habibi Lashkari et al.,
2020).

4.1.3. Implementation details
As shown in Section 3.2, the size of xcontent is N ∗ M, which denotes the ﬁrst N packets of each network ﬂow and the ﬁrst M bytes
of each packet. Each Conv1D block represents a 1D CNN model.
Speciﬁcally, for the Conv1D block directly connected to xcontent , we
set the number of convolution kernels to 128, the kernel size to
3, the step size to 1, and the padding ﬁeld to ‘SAME’. Each of the
following four parallel Conv1D blocks has 32 convolution kernels,
each with the same step size of 1 and the same padding ﬁeld
of ‘SAME’. However, the kernel sizes of the four parallel Conv1D
blocks are set to 1, 3, 5 and 7, respectively. DarknetSec uses several convolution kernels of different sizes to extract multiple local
spatial features for each network ﬂow and combines the outputs of
the four Conv1D blocks to obtain ﬁne-grained spatial feature representations.
The input and output size of the self-attention layer after the
Conv1D block are both 128∗ N. We set the number of hidden units
to 256 for the Bi-LSTM network and set the number of heads to
8 for the multi-head self-attention module. The output sizes of
the Bi-LSTM network and the multi-head self-attention module are
both 128∗ 256. The attentive content feature fusion module consists
of a self-attention layer and a dense layer, and the output sizes of
these two layers are 16∗ 256 and 256, respectively.
The statistical feature learning module consists of an MLP with
a 64-unit hidden layer and a 32-unit output layer. The MLP in the
classiﬁcation layer has a hidden layer, and the number of hidden
units is set to 64.
We employ the Adam optimizer with a learning rate of 0.001
for DarknetSec. Adam is an eﬃcient stochastic optimization algorithm that performs step-by-step optimization on a stochastic objective function with adaptive low-order moment estimation. Additionally, DarknetSec is executed with 30 training epochs and a
batch size of 32.
4.1.4. Evaluation metrics
To comprehensively evaluate the classiﬁcation performance of
the proposed architecture, ﬁve well-known metrics are adopted for
our experiments, i.e., the Accuracy (Acc), False Positive Rate (F P R),
Precision (P re), Recall (Rec), and F1-score (F 1), which are widely
used in classiﬁcation-related tasks. The abovementioned metrics
are based on four basic indicators, namely True Positive (T P ), True
Negative (T N), False Positive (F P ) and False Negative (F N). Additionally, Macro − P re, Macro − Rec and Macro − F 1 are the average
9

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

Meanwhile, we set N, M, and β as 30, 256 and 2, respectively. As
shown in Fig. 6, the accuracy gradually improves with increasing
L. When L reaches 100, the best accuracy rate emerges and begins
to remain stable. Thus, L = 100 is selected as the optimal value for
the subsequent experiments.

values of precision, recall, and F1-score values for all of each class
in the multiclass classiﬁcation scenario, respectively.

Acc =

TP + TN
TP + TN + FP + FN

(27)

F PR =

FP
FP + TN

(28)

P re =

TP
TP + FP

(29)

Rec =

TP
TP + FN

(30)

F1 =

2 ∗ P re ∗ Rec
P re + Rec

(31)

4.2.3. The hyperparameters of the focal loss function
The focal loss function has two adjustable parameters, namely,
α and γ . α represents the weight of each class in the training set.
It is obvious that compared with the majority classes, the minority classes with fewer training samples are more diﬃcult to classify accurately. Therefore, the minority classes need to be assigned
larger weights. In this paper, α is commonly deﬁned as the reciprocal of the category ratio for each class.
In the following discussion, we focus on the inﬂuence of γ ,
which represents how much the classiﬁcation model pays attention to the minority classes that are diﬃcult to classify. Generally,
γ should be set as a natural number. When α = 1 and γ = 0, the
focal loss function degenerates into the standard cross-entropy loss
function.
We conduct experiments to select the suitable value of γ for
the imbalanced dataset of DarknetSec. γ is successively set as 1,
2, 3, 4, and 5, and the other hyperparameters are set as N = 30,
M = 256, and L = 100. Additionally, since the focal loss function
mainly focuses on alleviating the problem of class imbalance, in
addition to the accuracy metric, we also calculate the Macro −
P re, Macro − Rec and Macro − F 1 of each class. Fig. 7 presents the
abovementioned four metrics by calculating the average of the 10fold cross-validation results obtained with different values of γ .
We can see that γ = 2 achieves the best performance and slightly
outperforms the other results when γ is set to larger than 2. We
can also conclude a value of γ that is too large may result in
overﬁtting. These experiments demonstrate that the most suitable
value of γ is 2.

4.2. Parameter optimization of DarknetSec
The selection of hyperparameters has a signiﬁcant impact on
the performance of DarknetSec. In this subsection, we discuss
the selection of several important hyperparameters, including the
number of packets N for each network ﬂow and the number of
bytes M for each selected packet used to generate the content features, the size of packet length sequence L for the sequential features, and the focusing parameter β of the focal loss.
4.2.1. The numbers of packets (N) and bytes (M)
The number of packets N and the number of bytes M used
to generate content features can directly inﬂuence the execution eﬃciency and accuracy of the neural network. Therefore,
we conduct experiments to obtain the optimal values of N and
M. To reduce the complexity of the training process, we choose
smaller values of N and M. We construct various training and
test sets with N = 15, 20, 25, 30, 35, 40, 50, 60, 70, 80, 90, 100 and
M = 64, 128, 256, 512, 1500 (consistent with the Maximum Transmission Unit (MTU)). Furthermore, the other hyperparameters are
set as L = 100, and β = 2.
We choose the average accuracy of 10-fold cross-validation as
the evaluation metric. An exhaustive grid search with a total of 60
experiments is conducted for all values of N and M. The experimental results obtained with different N and M values are presented in Fig. 5. When M reaches 256, the increase in the number
of bytes for each selected packet has a very weak effect on the resulting accuracy. Thus, we set M as 256 to ensure high accuracy
with a moderate training overhead. As shown in Fig. 5, the accuracies yielded with a varying number of packets selected for each
network ﬂow are presented with a red curve when M is set to 256.
When only the ﬁrst 15 packets of each network ﬂow are utilized
(N = 15), DarknetSec achieves a multiclass accuracy of 86.15%. With
the increase in the number of selected packets, the accuracy rate
signiﬁcantly improves when provided with more packets to generate content features. When N exceeds 30, the accuracy is maintained at approximately 92.22% and tends to be stable with no signiﬁcant change. Therefore, we choose N = 30, and M = 256 for the
following experiments.

4.3. Ablation study
DarknetSec contains several components for content and sidechannel feature extraction that use hybrid deep learning algorithms. We want to evaluate the contribution of each component
to the ﬁnal classiﬁcation performance.
As shown in Table 4, we can obtain an Acc of 76.56% and a
Macro − F 1 of 77.94% by leveraging only the sequential features,
while the performance of the statistical features is slightly better than that of the sequential features. By considering both feature sets, namely, by using side-channel features, the Acc and
Macro − F 1 can be increased to 84.26% and 84.75%, respectively.
However, since the payload content of packets is nonexistent in
the side-channel features, this approach may not be able to provide
enough suﬃcient information for accurately predicting application
types.
A more interesting ﬁnding is that we can obtain an Acc of
85.42% and a Macro − F 1 of 85.41% by using the content features only; these values are even higher than those yielded by the
combination of statistical features and sequential features, which
demonstrates that the payload content of packets plays a greater
role than payload statistics when applied to encrypted traﬃc analysis. Furthermore, if we combine the content features and the
side-channel features, the Acc and Macro − F 1 can be improved
to 87.68% and 87.84%, respectively. This also veriﬁes that the ﬁnegrained analysis of encrypted traﬃc by comprehensively considering both context features and side-channel features can effectively
facilitate the accurate classiﬁcation of darknet traﬃc.
We next discuss the impact of the self-attention mechanism,
including the multi-head self-attention module and the selfattention layer embedded in the local spatial-temporal feature

4.2.2. The size of packet length sequence L
For the extraction of sequential features, the size of packet
length sequence L needs to be speciﬁed. To make full use of
the sequence characteristics of the packets in a network ﬂow,
we consider a larger range of L from 15 to 300 and use the
average accuracy of 10-fold cross-validation as the evaluation metric. Various values of L are selected from the set of
{15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 150, 180, 200, 250, 300}.
10

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

Fig. 5. The average Acc of 10-fold cross-validation with different values of N and M.

Fig. 6. The average Acc of 10-fold cross-validation with different values of L.

Table 4
Descriptions of the evaluation results regarding the different feature learning components of DarknetSec.
Feature learning components

Acc

Macro − Pre

Macro − Rec

Macro − F 1

Statistical features
Sequential features
Side-channel features (statistical + sequential features)
Content features
Content + side-channel features
Content + side-channel features + multi-head self-attention module
All

78.13 ± 2.34
76.56 ± 3.72
84.26 ± 2.18
85.42 ± 2.11
87.68 ± 1.31
91.28 ± 0.64
92.22 ± 0.51

80.54 ± 3.15
78.63 ± 2.80
84.64 ± 2.42
85.46 ± 1.62
87.56 ± 0.82
91.96 ± 0.70
93.36 ± 0.62

77.82 ± 2.56
77.27 ± 1.92
84.86 ± 1.94
85.38 ± 2.04
88.12 ± 1.04
90.67 ± 1.18
90.88 ± 1.24

79.16 ± 2.79
77.94 ± 2.22
84.75 ± 2.06
85.41 ± 1.87
87.84 ± 0.98
91.31 ± 1.04
92.10 ± 0.92

11

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

Fig. 7. The average Acc, Macro − Pre, Macro − Rec and Macro − F 1 of 10-fold cross-validation with different values of γ .

learning module, on darknet traﬃc classiﬁcation. On the basis of
using a combination of content features and side-channel features
(with an Acc of 87.68% and a Macro − F 1 of 87.84%), the application
of multi-head self-attention module signiﬁcantly increases the Acc
and Macro − F 1 by 3.60% and 3.47%, respectively. The experimental results demonstrate that the multi-head self-attention module
can effectively mine the inherent dependencies and hidden connections among the local spatial-temporal features extracted from
the input encrypted traﬃc, thus contributing to providing more
discriminative feature representations for ﬁne-grained darknet trafﬁc classiﬁcation. Finally, by embedding a self-attention layer into
the local spatial-temporal feature learning module to help the neural network pay more attention to the most important spatialtemporal feature variables, the Acc and Macro − F 1 are increased
from 91.28% and 91.31% to 92.22% and 92.10%, respectively.

clude that DarknetSec is superior to its counterparts in terms of
the binary classiﬁcation scenario.
In addition, to further verify the stability of DarknetSec, we randomly select 80 0 0 network ﬂows proportionally from the 8 types
of darknet applications (stratiﬁed sampling). The ratio of benign
and darknet network ﬂows is gradually increased from 1:1 to 9:1.
Fig. 9 presents the recall and FPR values of all comparison methods with a varying ratio of benign and darknet network ﬂows.
In general, the recall and FPR values of all methods decrease as
the proportion of benign network ﬂows increases, and DarknetSec
achieves the best classiﬁcation results when compared with the
rest of the methods. Furthermore, with the increase in the proportion of benign network ﬂows, the recall and FPR values of DarknetSec decrease the least. When the ratio of benign and darknet
network ﬂows reaches 5:1, the recall and FPR of DarknetSec tend
to be stable at approximately 96.20% and 1.44%, respectively. However, the recall values of the remaining methods continue to decrease when the ratio of benign and darknet network ﬂows reaches
9:1, as more darknet network ﬂows are undetected.
The reason for this phenomenon is that DarknetSec extracts
more stable and comprehensive feature representations from network ﬂows, which contribute to the accurate identiﬁcation of darknet ﬂows from a large number of benign ﬂows; in contrast, the
other approaches are not suﬃciently discriminative to differentiate between benign and darknet network ﬂows. The comparison
results show that DarknetSec is superior to the other methods, especially in scenarios with a large amount of background traﬃc.

4.4. Performance comparison with existing methods
In this subsection, we evaluate the performance of DarknetSec
relative to several representative methods in binary and multiclass
classiﬁcation scenarios. We apply 10-fold cross-validation and take
the average values as the ﬁnal results.
4.4.1. Binary classiﬁcation
In terms of the binary classiﬁcation scenario, all application
types of darknet traﬃc are treated as a single class. This scenario
aims to distinguish between benign and darknet network ﬂows. It
is worth noting that if a network ﬂow is labeled with the darknet type, we can further employ the multiclass classiﬁcation model
(see Section 4.2.2) to identify the speciﬁc application type to which
it belongs.
We use the Acc, P re, Rec and F 1 metrics to evaluate the classiﬁcation results of all these methods. The average metrics obtained
via 10-fold cross-validation are presented in Fig. 8. DarknetSec signiﬁcantly outperforms the other methods in all evaluation metrics. By jointly considering the accuracy and F1-score values obtained on the representative dataset of Darknet2020, we can con-

4.4.2. Multiclass classiﬁcation
In the multiclass classiﬁcation scenario, there are a total of nine
classes of network ﬂows, namely, Benign, VoIP, Video-Stream, P2P,
Email, File-Transfer, Chat, Browsing and Audio-Stream. We use the
Acc, Macro − P re, Macro − Rec and Macro − F 1 metrics to evaluate
the classiﬁcation results of all the tested methods. As shown in
Fig. 10, similar to those for the binary classiﬁcation results, the
above four evaluation metrics of DarknetSec are better than those
of the other methods. In addition, we provide the accuracy values of each type for all methods, as shown in Table 5. Darknet12

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

Fig. 8. Binary classiﬁcation: the average Acc, Pre, Rec and F 1 of different methods.

Fig. 9. Binary classiﬁcation: impact of the ratio of benign and darknet network ﬂows on the Rec and F PR.
Table 5
Multiclass classiﬁcation: the Acc of different methods for each type of network ﬂow in DarknetSec.
Traﬃc
Type

Methods
FlowPic

CETAnalytics

BGRUA

VGG19+RF

RF

DIDarknet

DarknetSec

Benign
VoIP
Video-Stream
P2P
Email
File-Transfer
Chat
Browsing
Audio-Stream

98.29 ± 0.73
89.58 ± 0.83
89.22 ± 0.27
90.64 ± 0.72
79.25 ± 0.93
90.64 ± 0.72
94.26 ± 0.35
78.05 ± 0.94
98.21 ± 0.43

99.64 ±0.28
90.17 ± 0.49
89.87 ± 0.91
92.26 ± 0.54
80.34 ± 0.75
91.86 ± 0.54
94.63 ± 0.75
78.92 ± 0.85
98.32 ± 0.78

98.22 ± 0.43
89.14 ± 0.54
88.76 ± 0.23
90.12 ± 0.83
78.33 ± 0.77
90.12 ± 0.83
94.86 ± 0.81
78.28 ± 0.65
97.62 ± 0.35

99.10 ± 0.36
89.92 ± 0.68
89.58 ± 1.11
90.34 ± 0.83
79.60 ± 0.71
91.14 ± 0.83
93.57 ± 0.64
78.34 ± 0.72
98.53 ± 0.65

97.68 ± 1.23
89.51 ± 0.39
86.29 ± 0.66
88.79 ± 0.63
75.65 ± 1.21
88.79 ± 0.63
92.58 ± 0.95
77.54 ± 1.21
96.24 ± 0.83

98.66 ± 0.82
89.04 ± 0.71
88.33 ± 0.76
89.86 ± 0.78
78.13 ± 0.60
89.86 ± 0.78
94.23 ± 1.08
78.11 ± 1.12
97.36 ± 0.16

99.54 ± 0.54
91.35 ± 0.84
92.56 ± 0.72
94.69 ± 0.57
81.68 ± 1.05
94.69 ± 0.57
95.58 ± 0.63
82.74 ± 0.38
98.45 ± 0.56

Sec achieves the best classiﬁcation accuracy values on traﬃc types
except Benign and Audio-Stream. Furthermore, for the Benign and
Audio-Stream traﬃc types, the accuracy values of DarknetSec are
only 0.10% and 0.08% lower than the second-place metrics, respectively; this is obviously trivial, and no obvious differences are exhibited. From the ﬁne-grained experimental multiclass classiﬁcation results, we can obtain several major conclusions as follows.

(1) DarknetSec outperforms all other approaches, with the
highest Acc (92.22%) and Macro − F 1 (92.10%) values. Compared
with those of the second-place method, i.e., CETAnalytics, the accuracy and Macro-F1-score values are 2.96% and 3.06% higher, respectively, which shows that our classiﬁcation architecture has better accuracy and adaptability than other state-of-the-art methods.

13

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

Fig. 10. Multiclass classiﬁcation: the average Acc, Macro − Pre, Macro − Rec and Macro − F 1 of different methods.

Fig. 11. Multiclass classiﬁcation results obtained with different methods on USTC-TFC2016 and The Open HTTPS Dataset.

(2) The multiple deep features, i.e., content features, statistical features, and sequence features, make different contributions to the classiﬁcation of darknet traﬃc. It can be seen that
the comprehensive utilization of these three types of features helps
DarknetSec achieve the best classiﬁcation performance.
(3) The multi-head self-attention module in parallel with the
local spatial-temporal feature extraction module helps to capture the global intrinsic relationships among the local spatialtemporal features extracted from different data positions. Although two other methods, i.e., CETAnalytics and BGRUA, also use
the attention mechanism, unlike DarknetSec, they use only a simple attention layer in a cascaded manner after performing feature
extraction, which is equivalent to adding a module for the selection of feature importance rather than mining the global inherent
dependencies and hidden connections among the extracted local
spatial-temporal features.
In summary, the comparison results demonstrate the superiority of DarknetSec in terms of darknet traﬃc classiﬁcation and application identiﬁcation due to the use of the self-attention mechanism and multiple deep feature learning.

4.5. Evaluation on other encrypted traﬃc classiﬁcation tasks
Although DarknetSec is proposed to classify the encrypted darknet traﬃc of VPN and Tor applications, it is still suitable for other
encrypted traﬃc classiﬁcation tasks. To demonstrate the generalizability of DarknetSec, we conduct comparison experiments on two
other public datasets, namely, USTC-TFC2016 (Wang et al., 2017)
and The Open HTTPS Dataset (Wazen Shbair, 2016). Speciﬁcally, as
shown in Table 6, we choose the benign part of the USTC-TFC2016
dataset that has ten traﬃc types in fourteen pcap ﬁles (with a total size of 3.71 GB) and randomly selected ten HTTPS services with
more than 10 0 0 network ﬂows from The Open HTTPS Dataset for
evaluation. As this is a multiclass classiﬁcation task, we use the
Acc and Macro − F 1 metrics to analyze the performance of each
method.
Fig. 11 (a) and (b) show the Acc and Macro − F 1 values
of different methods, respectively. FlowPic, CETAnalytics, BGRUA,
VGG19+RF and DarknetSec obtain superior performance, revealing
that the feature representations learned by these methods are distinguishable enough to identify the network applications in these
14

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

Table 6
Description of USTC-TFC2016 and The Open HTTPS Dataset used to evaluate the generalizability of DarknetSec.
Dataset

Traﬃc types

USTC-TFC2016
(benign part)

BitTorrent, Facetime, FTP, Gmail,
MySQL, Outlook, Skype, SMB, Weibo,
WorldOfWarcraft
www.google.com, r.nexac.com,
spanalytics.yahoo.com, ib.adnxs.com,
bat.bing.com, www.facebook.com,
bat.bing.com, selfrepair.mozilla.org,
pixel.quantserve.com, tags.tiqcdn.com

The Open HTTPS
Dataset (10
randomly selected
HTTPS services)

Barratt, M., 2015. A discussion about dark net terminology. Drugs Internet Soc. 15.
Biddle, P., England, P., Peinado, M., Willman, B., et al., 2002. The darknet and the future of content distribution. In: ACM Workshop on Digital Rights Management,
vol. 6, p. 54.
Buxton, J., Bingham, T., 2015. The rise and challenge of dark net drug markets. Policy
Brief 7, 1–24.
Dong, C., Zhang, C., Lu, Z., Liu, B., Jiang, B., 2020. CETAnalytics: comprehensive effective traﬃc information analytics for encrypted traﬃc classiﬁcation. Comput.
Netw. 176, 107258.
Fachkha, C., Debbabi, M., 2015. Darknet as a source of cyber intelligence: survey,
taxonomy, and characterization. IEEE Commun. Surv. Tutor. 18 (2), 1197–1227.
Fang, Y., Li, K., Zheng, R., Liao, S., Wang, Y., 2021. A communication-channel-based
method for detecting deeply camouﬂaged malicious traﬃc. Comput. Netw. 197,
108297.
Habibi Lashkari, A., Kaur, G., Rahali, A., 2020. DIDarknet: a contemporary approach
to detect and characterize the darknet traﬃc using deep image learning. In:
2020 the 10th International Conference on Communication and Network Security, pp. 1–13.
Hassan, M.M., Gumaei, A., Alsanad, A., Alrubaian, M., Fortino, G., 2020. A hybrid
deep learning model for eﬃcient intrusion detection in big data environment.
Inf. Sci. 513, 386–396.
Iglesias, F., Zseby, T., 2017. Pattern discovery in internet background radiation. IEEE
Trans. Big Data 5 (4), 467–480.
Iliadis, L.A., Kaifas, T., 2021. Darknet traﬃc classiﬁcation using machine learning
techniques. In: 2021 10th International Conference on Modern Circuits and Systems Technologies (MOCAST). IEEE, pp. 1–4.
Kanna, P.R., Santhi, P., 2021. Uniﬁed deep learning approach for eﬃcient intrusion
detection system using integrated spatial–temporal features. Knowl. Based Syst.
226, 107132.
Kumar, S., Vranken, H., van Dijk, J., Hamalainen, T., 2019. Deep in the dark: a novel
threat detection system using darknet traﬃc. In: 2019 IEEE International Conference on Big Data (Big Data). IEEE, pp. 4273–4279.
Lin, K., Xu, X., Gao, H., 2021. TSCRNN: a novel classiﬁcation scheme of encrypted
traﬃc based on ﬂow spatiotemporal features for eﬃcient management of IIoT.
Comput. Netw. 190, 107974.
Liu, L., Zhen, J., Li, G., Zhan, G., He, Z., Du, B., Lin, L., 2020. Dynamic spatial-temporal representation learning for traﬃc ﬂow prediction. IEEE Trans. Intell. Transp.
Syst..
Liu, X., You, J., Wu, Y., Li, T., Li, L., Zhang, Z., Ge, J., 2020. Attention-based bidirectional GRU networks for eﬃcient HTTPS traﬃc classiﬁcation. Inf. Sci. 541,
297–315.
Montieri, A., Ciuonzo, D., Aceto, G., Pescapé, A., 2018. Anonymity services Tor, I2P,
JonDonym: classifying in the dark (web). IEEE Trans. Dependable Secure Comput. 17 (3), 662–675.
Montieri, A., Ciuonzo, D., Bovenzi, G., Persico, V., Pescapé, A., 2019. A dive into the
dark web: hierarchical traﬃc classiﬁcation of anonymity tools. IEEE Trans. Netw.
Sci. Eng. 7 (3), 1043–1054.
Niranjana, R., Kumar, V.A., Sheen, S., 2020. Darknet traﬃc analysis and classiﬁcation
using numerical AGM and mean shift clustering algorithm. SN Comput. Sci. 1
(1), 1–10.
Pacheco, F., Exposito, E., Gineste, M., Baudoin, C., Aguilar, J., 2018. Towards the deployment of machine learning solutions in network traﬃc classiﬁcation: a systematic survey. IEEE Commun. Surv. Tutor. 21 (2), 1988–2014.
Pinheiro, A.J., Bezerra, J.d.M., Burgardt, C.A., Campelo, D.R., 2019. Identifying IoT devices and events based on packet length from encrypted traﬃc. Comput. Commun. 144, 8–17.
Pour, M.S., Mangino, A., Friday, K., Rathbun, M., Bou-Harb, E., Iqbal, F., Samtani, S.,
Crichigno, J., Ghani, N., 2020. On data-driven curation, learning, and analysis for
inferring evolving internet-of-things (IoT) botnets in the wild. Comput. Secur.
91, 101707.
Rao, Z., Niu, W., Zhang, X., Li, H., 2018. Tor anonymous traﬃc identiﬁcation based
on gravitational clustering. Peer-to-Peer Netw. Appl. 11 (3), 592–601.
Sarwar, M.B., Hanif, M.K., Talib, R., Younas, M., Sarwar, M.U., 2021. DarkDetect: darknet traﬃc detection and categorization using modiﬁed convolution-long short-term memory. IEEE Access 9, 113705–113713.
Shahbar, K., Zincir-Heywood, A.N., 2017. Effects of shared bandwidth on anonymity
of the I2P network users. In: 2017 IEEE Security and Privacy Workshops (SPW).
IEEE, pp. 235–240.
Shapira, T., Shavitt, Y., 2021. FlowPic: a generic representation for encrypted traﬃc
classiﬁcation and applications identiﬁcation. IEEE Trans. Netw. Serv. Manage. 18
(2), 1218–1232.
Shen, M., Liu, Y., Zhu, L., Du, X., Hu, J., 2020. Fine-grained webpage ﬁngerprinting
using only packet length information of encrypted traﬃc. IEEE Trans. Inf. Forensics Secur. 16, 2046–2059.
Shen, M., Zhang, J., Zhu, L., Xu, K., Du, X., 2021. Accurate decentralized application
identiﬁcation via encrypted traﬃc analysis using graph neural networks. IEEE
Trans. Inf. Forensics Secur. 16, 2367–2380.
Singh, D., Shukla, A., Sajwan, M., 2021. Deep transfer learning framework for the
identiﬁcation of malicious activities to combat cyberattack. Future Gener. Comput. Syst. 125, 687–697.
Sirinam, P., Mathews, N., Rahman, M.S., Wright, M., 2019. Triplet ﬁngerprinting:
more practical and portable website ﬁngerprinting with n-shot learning. In:
Proceedings of the 2019 ACM SIGSAC Conference on Computer and Communications Security, pp. 1131–1148.

datasets. Among them, DarknetSec slightly outperforms the other
methods, demonstrating that DarknetSec is also suitable for the
conventional network traﬃc classiﬁcation tasks.
5. Conclusion
In this paper, we propose DarknetSec, which can accurately
classify the encrypted network ﬂows of darknet traﬃc using a selfattentive deep learning method. We extract content features from
the payload content of packets and side-channel features from payload statistics. Through multiple deep feature learning, we turn the
darknet application identiﬁcation problem into a typical classiﬁcation task and use hybrid deep learning algorithms to design a powerful classiﬁer. The experiments conducted on the CICDarknet2020
dataset indicate that DarknetSec performs better than other stateof-the-art methods and can distinguish darknet applications from
benign applications more accurately. Additionally, we evaluate the
effectiveness of DarknetSec on other encrypted traﬃc classiﬁcation
tasks. In the future work, we plan to use more datasets to verify
the effectiveness of DarknetSec and study the impact of network
traﬃc concept drift on the classiﬁcation performance of DarknetSec.
Declaration of Competing Interest
The authors declare that they have no known competing ﬁnancial interests or personal relationships that could have appeared to
inﬂuence the work reported in this paper.
CRediT authorship contribution statement
Jinghong Lan: Conceptualization, Methodology, Validation,
Software, Investigation, Data curation, Writing – original draft,
Writing – review & editing. Xudong Liu: Supervision, Resources,
Formal analysis, Writing – review & editing. Bo Li: Funding acquisition, Supervision, Project administration. Yanan Li: Visualization,
Software, Validation. Tongtong Geng: Validation, Writing – review
& editing.
Acknowledgments
This work was supported by the National Key R&D Program
China (2018YFB0803 503), the 2018 joint Research Foundation
of Ministry of Education, China Mobile (MCM20180507) and the
Opening Project of Shanghai Trusted Industrial Control Platform
(TICPSH202003020-ZC).
References
Adewopo, V., Gonen, B., Varlioglu, S., Ozer, M., 2019. Plunge into the underworld: a
survey on emergence of darknet. In: 2019 International Conference on Computational Science and Computational Intelligence (CSCI). IEEE, pp. 155–159.
Al-Nabki, M.W., Fidalgo, E., Alegre, E., Fernández-Robles, L., 2019. ToRank: identifying the most inﬂuential suspicious domains in the Tor network. Expert Syst.
Appl. 123, 212–226.
15

J. Lan, X. Liu, B. Li et al.

Computers & Security 116 (2022) 102663

Stergiopoulos, G., Talavari, A., Bitsikas, E., Gritzalis, D., 2018. Automatic detection of
various malicious traﬃc using side channel features on TCP packets. In: European Symposium on Research in Computer Security. Springer, pp. 346–362.
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A.N., Kaiser, Ł.,
Polosukhin, I., 2017. Attention is all you need. In: Advances in Neural Information Processing Systems, pp. 5998–6008.
Wang, W., Zhu, M., Zeng, X., Ye, X., Sheng, Y., 2017. Malware traﬃc classiﬁcation
using convolutional neural network for representation learning. In: 2017 International Conference on Information Networking (ICOIN). IEEE, pp. 712–717.
Wazen Shbair Thibault Cholez, J. F. I. C., 2016. Https websites dataset. http://
betternet.lhs.loria.fr/datasets/https/.
Wood, J.A., 2009. The darknet: a digital copyright revolution. Rich. JL Tech. 16, 1.
Xie, G., Li, Q., Jiang, Y., 2021. Self-attentive deep learning method for online traﬃc
classiﬁcation and its interpretability. Comput. Netw. 196, 108267.
Xie, J., Li, S., Yun, X., Zhang, Y., Chang, P., 2020. HSTF-model: an HTTP-based trojan
detection model via the hierarchical spatio-temporal features of traﬃcs. Comput. Secur. 96, 101923.
Yang, J., Zhang, L., Chen, C., Li, Y., Li, R., Wang, G., Jiang, S., Zeng, Z., 2020. A hierarchical deep convolutional neural network and gated recurrent unit framework
for structural damage detection. Inf. Sci. 540, 117–130.
Yang, Z.-b., Zhang, J.-p., Zhao, Z.-b., Zhai, Z., Chen, X.-f., 2020. Interpreting network
knowledge with attention mechanism for bearing fault diagnosis. Appl. Soft
Comput. 97, 106829.
Yao, H., Liu, C., Zhang, P., Wu, S., Jiang, C., Yu, S., 2019. Identiﬁcation of encrypted
traﬃc through attention mechanism based long short term memory. IEEE Trans.
Big Data.
Zheng, H., Lin, F., Feng, X., Chen, Y., 2020. A hybrid deep learning model with attention-based Conv-LSTM networks for short-term traﬃc ﬂow prediction. IEEE
Trans. Intell. Transp. Syst..

Jinghong Lan is a PhD candidate in the School of Computer Science and Engineering, Beihang University, China. He received the MS degree in the School of
Cyberspace Security from PLA Information Engineering University in Zhengzhou,
China. His current research interests include intrusion detection, machine learning,
and deception defense.
Xudong Liu is a professor in the School of Computer Science and Engineering, Beihang University, China. His current research interests include machine learning, big
data and industrial information security.
Bo Li is an Assistant Professor in the School of Computer Science and Engineering,
Beihang University, China. He received the PhD degree in the School of Computer
Science and Engineering from Beihang University. His current research interests include industrial information security, mobile and IoT security, and cyber threat intelligence.
Yanan Li is a MSc candidate in the School of Computer and Information Security, Guilin University of Electronic Technology, China. He received the BS degree
in the School of Cyberspace Security from PLA Information Engineering University
in Zhengzhou, China. His current research interests include intrusion detection, machine learning, and knowledge graph technology.
Tongtong Geng is a PhD candidate in the School of Economics and Management,
Xidian University, China. Her received the MS degree in the School of Economics
and Management, Xidian University, China. Her current research interests include
sharing economy business model, machine learning, and big data research.

16
PAPER_TEXT
