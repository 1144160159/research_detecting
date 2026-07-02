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
# [092] TSCRNN: A novel classification scheme of encrypted traffic based on flow spatiotemporal features for efficient management of IIoT
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
编号：092
题名：TSCRNN: A novel classification scheme of encrypted traffic based on flow spatiotemporal features for efficient management of IIoT
年份：2021
DOI：10.1016/j.comnet.2021.107974
来源：Computer Networks
PDF：paper/10.1016_j.comnet.2021.107974.pdf
已有粗分类：加密流量分类与应用识别
二级关联：IoT、车联网、工业互联网与边缘安全、时序、日志、KPI 与云原生异常检测
相关性：强相关，分数 15
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\092.txt
- 原始字符数：57056
- 本次发送字符数：57056
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Computer Networks 190 (2021) 107974

Contents lists available at ScienceDirect

Computer Networks
journal homepage: www.elsevier.com/locate/comnet

TSCRNN: A novel classification scheme of encrypted traffic based on flow
spatiotemporal features for efficient management of IIoT
Kunda Lin a, Xiaolong Xu b, *, Honghao Gao c, *
a

Jiangsu Key Laboratory of Big Data Security & Intelligent Processing, Nanjing University of Posts and Telecommunications, Nanjing, China
School of Computer Science, Nanjing University of Posts and Telecommunications, Nanjing, China
c
School of Computer Engineering and Science, Shanghai University, Shanghai, China
b

A R T I C L E I N F O

A B S T R A C T

Keywords:
Encrypted traffic classification
Tor network traffic
Traffic characterization
Deep learning

In the Industrial Internet of Things (IIoT) in the 5G era, the growth of smart devices will generate a large amount
of data traffic, bringing a huge challenge of network traffic classification, which is the prerequisite of IIoT traffic
engineering, quality of service (QoS), cyberspace security, etc. It is difficult for current traffic classification
methods to distinguish encrypted dataflow and design effective handcraft features. In this paper, a novel iden­
tification scheme of encrypted traffic, TSCRNN, is proposed to automatically extract features for efficient traffic
classification, which is based on spatiotemporal features. TSCRNN includes the preprocessing phase and the
classification phase. In the preprocessing phase, raw traffic data are processed with flow segmentation, sampling,
and vectorization, etc. To solve the classification problem of long time flow, sampling strategies are used to
collect samples from the middle of the long-lived flow. In the classification phase, TSCRNN extracts abstract
spatial features by CNN and then introduces stack bidirectional LSTM to learn the temporal characteristics. The
experiments were performed on the dataset ISCXTor2016. The experimental results show that TSCRNN out­
performs other typical methods in all scenarios, which achieves the accuracy up to 99.4% and 95.0% respectively
in Tor/nonTor binary classification tasks and sixteen classification tasks. Furthermore, TSCRNN is applied to
other real network datasets obtained the satisfactory performance, which validates its feasibility and univer­
sality. It means that TSCRNN can effectively identify encrypted and anonymous traffic, provide a fine-grained
traffic characterization mechanism, which will support the development of core technologies in the Industrial
Internet of Things.

1. Introduction
Traffic classification is the essential task for traffic engineering,
network management, quality of service (QoS), and cybersecurity.
However, with the popularity of traffic encryption techniques and the
rapid growth of network throughput [1], accurate identification of
encrypted traffic in real-time is becoming much harder [2]. Recently,
demands of traffic analysis have also emerged in new network systems,
such as Industrial Internet of Things (IIoT) [3], software-defined
network (SDN) [4], and mobile Internet [5]. Therefore, encrypted
traffic classification has attracted more attention.
Sensory perception, communication interaction, network intercon­
nection, information processing, and security defense are the core
technologies that make up the IIoT. The industry uses a large number of
smart sensors to collect data generated in various links of industrial

production, to conduct intelligent data analysis and resource manage­
ment. However, mass devices will generate extremely huge traffic,
which brings great pressure on data communication transmission,
resource management, QoS, and causes more security problems [6].
Besides, traffic encryption, obfuscation, and anonymity technologies
have become a common practice in the industry [7], which makes it
difficult to perceive and manage traffic at the network level. At the same
time, security attacks make extensive use of these technologies to evade
the interception of firewalls and intrusion detection systems [8]. With
the advent of the 5G era, the data collected by sensors will become more
abundant, causing these problems to be further aggravated. Therefore,
the research on the classification of network encrypted traffic will help
strengthen the resource management and security assurance of the IIoT
in the 5G era [9].
Typical encrypted traffic classification methods can be divided into

* Corresponding authors.
E-mail addresses: xuxl@njupt.edu.cn (X. Xu), gaohonghao@shu.edu.cn (H. Gao).
https://doi.org/10.1016/j.comnet.2021.107974
Received 14 December 2020; Received in revised form 6 February 2021; Accepted 26 February 2021
Available online 3 March 2021
1389-1286/© 2021 Elsevier B.V. All rights reserved.

K. Lin et al.

Computer Networks 190 (2021) 107974

three main categories: port-based methods, payload-based methods, and
statistics-based methods[2,10]. Port-based methods can only achieve
low accuracy due to the prevalence of dynamic port and port camouflage
techniques. Payload-based detection methods need to match traffic
fingerprints, which is time-consuming. At present, more attention is
focused on statistics-based methods, which are based on machine
learning, and require domain-experts to extract hand-crafted features
for a specified scenario. At the same time, offline algorithms are
generally required for overall statistical characteristics. Therefore, they
usually more time-consuming.
Deep learning has achieved considerable progress in many fields
related to classification problems. Convolutional neural networks (CNN)
can learn abstract spatial features in data through multi-layer stacking,
while recurrent neural networks (RNN) accepts data at multiple time
steps and can learn the time characteristics between data. As a typical
classification task, deep learning methods can be also applicable to
encrypted traffic identification [11]. However, recent studies on the
classification of encrypted traffic based on deep learning have not taken
into account the packet-to-packet interrelationship. Therefore, in this
paper, we combine the stacked bidirectional LSTM (RNN-based archi­
tecture) to learn the temporal features of the spatial features extracted
by CNN. Furthermore, considering the continuous emergence of new
types of network applications, the service types of traffic would be
classified (for instance, Chat, P2P, Video, and so on), which is called
traffic characterization.
In this paper, a novel identification scheme of encrypted traffic,
TSCRNN, is proposed to automatically extract features for efficient
traffic classification. The main contributions of this paper are as follows:

patterns of traffic, maintaining a library of traffic fingerprints to identify
traffic like string regular matching. The most famous payload-based
approach is deep packet inspection (DPI) [15,16]. Those methods are
widely used in industry, however, they are time-consuming and the
existing patterns are prone to invalidate due to traffic encryption and
anonymous technologies [17].
The emergence of machine learning makes up for the deficiency of
rule-based methods. Liu et al. [18] designed a series of statistical fea­
tures at the packet level, such as maximum, minimum, mean, packet
size, etc., which were used in a semi-supervised learning framework to
classify the encrypted traffic. Anderson et al. [19] used several features,
including the meta-information in the header of TLS flow, the distri­
bution of packet length, arrival time, etc., in a logistic regression model
to distinguish 18 types of malicious traffic. Fahad et al. [20] chose some
features from a features list presented by Moore et al. [21] and intro­
duced the Bayesian kernel estimation method to classify the traffic.
Similarly, Yamansavascilar et al. [22] referred to the same features list
and selected 111 flow characteristics to classify 11 types of traffic ap­
plications with the k-nearest neighbor algorithm (k-NN), achieving the
94% of accuracy rate. However, none of them considered the strategy of
feature selection. Alshammari et al. [23] chose the features without
basic information of traffic (IP, port, etc.) to improve the universality,
using the C4.5 decision tree which achieved an accuracy of up to 90%. In
[24], the robust traffic classification mechanism (RTC) and the bag of
words classifier (BoW) are proposed to classify encrypted traffic. Ex­
periments demonstrated that they perform better and are more robust
than other machine learning-based methods. In [25], artificial neural
networks and support vector machines were used to dichotomize the
public dataset ISCXTor2016 with a 99% accuracy rate. However, it is
only suitable for simple coarse-grained binary classifications.
In conclusion, the domain experts are required to extract handcrafted features, only suitable for specific scenarios. The distribution
of traffic flow is used as main feature, which usually requires long traffic
collections. It means that a large of temporary traffic needs to be cached
and consumes more storage resources.
Deep learning is a branch of machine learning. Compared to the
above machine learning-based methods, deep learning-based methods
for encrypted traffic classification do not require the design of manual
features, which are generally end-to-end. Wang et al. [26] were the first
to introduce the one-dimensional convolutional neural networks
(1D-CNN) for the VPN-nonVPN dataset [27], which reaches 86.6% ac­
curacy of 12 types of traffic services classification. The 1D-CNN captured
byte features at the packet level to realize automatic traffic feature
extraction, while temporal characteristics were not considered. The
paper [28] presents a traffic classification system, combining multi-level
features extracted by both machine learning and deep learning, to
identify 4 types of encrypted traffic with high accuracy. As an offline
algorithm, it is time-consuming and requires handcrafted feature design
as well. The two-dimensional convolutional neural networks (2D-CNN)
has been widely applied in image classification. In [29], the FlowPic
model is proposed, which transforms a series of packet size in each flow
into two-dimensional gray images, and then used CNN to implement the
image classification. FlowPic has strong universality as the simple but
effective conversion method. However, FlowPic requires long time
traffic capturing, which is not suitable for short-lived traffic classifica­
tion. Also, the author points out that it is not appropriate for tor network
traffic classification. The papers [30,31] also combine CNN and RNN to
design model architecture. However, Lopez-Martin. et al [30] used
manual features to encode traffic without considering the distribution
characteristics of traffic bytes. Wang .et al [31] considered spatiotem­
poral features as well, but he proposed a two-stage model to identify
network malicious attacks. Each packet is one-hot encoded and inputted
to CNN to obtain their respective spatial features at first, and then use
RNN to learn the overall timing features.

• In the preprocessing phase, the original traffic data was subjected to
flow segmentation, vectorization, normalization, and other processes
to preserve the sequential relationship between packets. Besides, a
sampling method was used to collect samples from long flow in the
Tor network. TSCRNN used only a small number of packets to realize
the early identification of traffic.
• TSCRNN combined CNN and RNN to extract abstract features of the
flow at first, and learn the temporal characteristics, to realize effi­
cient identification. Most experiments were conducted on the ISCX­
Tor2016 dataset [12]. For the traffic characterization task (sixteen
classifications), TSCRNN achieved average accuracy up to 94.8%
without handcrafted features design, which is better than both con­
ventional machine learning and deep learning methods.
• TSCRNN was applied to other traffic datasets directly. Without any
special configuration, it can still show ideal performance, which in­
dicates that TSCRNN is universal and is not limited to specified
scenarios. Experiments show that TSCRNN can effectively identify
encrypted and anonymous traffic and achieve fine-grained traffic
characterization, which can provide support for network resource
management, QoS, and security assurance in the IIoT.
The rest of the paper is organized as follows. Related works about
encrypted traffic classification are analyzed in Section 2. In Section 3, we
introduce the architecture of TSRCNN, presenting the workflow of the
preprocessing and the classification in detail. Section 4 presents the
experimental environment and datasets, evaluation matrices, experi­
mental results, and the corresponding analysis. Section 5 concludes this
paper and shows the future work.
2. Related work
Typical encrypted traffic classification methods can be divided into
three main categories: port-based methods, pay-load-based methods,
and statistics-based methods.
With the rapid development of the network, port-based identification
methods of encrypted traffic are no longer suitable for the current
network environment [13,14]. The payload-based methods extract byte
2

K. Lin et al.

Computer Networks 190 (2021) 107974

samples. The reason for the scarcity of the tor traffic flow is that a virtual
circuit may be established to retain a long time session communicating
on the tor network, which generates long-lived flows. It is called the
onion routing technique proposed for privacy, which encrypts traffic
multiple times and hides source addresses.
The paper[32] proposes a sampling method to obtain samples from
the elephant flow for semi-supervised learning. Inspired by it, we use an
in-flow sampling method to obtain enough samples from Tor long-live
flows for supervised learning. The three kinds of sampling strategies
are as follows: Random Sampling, the default strategy, randomly selects
sampling points in the flow; Fixed Step Sampling, which selects sam­
pling points in a fixed-step; Mixed Sampling, combining the time in­
terval and packet length to find the sampling points in a flow.
In TCP or UDP transmissions, the packets used for interaction
without payload are usually less than 60 bytes, Mixed Sampling detects
such packets and obtains a series of collection points combining the
packet interval time. However, as mentioned in the paper [2], sampling
samples from the middle of a flow is still an open problem to be studied.
This heuristic method of Mixed Sampling is only for comparison. The
default sampling strategy in the experiments is Random Sampling.

3. Methodology
3.1. Framework of TSCRNN
TSCRNN is designed to solve the problem of encrypted traffic clas­
sification, which includes the preprocessing phase and the classification
phase. Fig. 1 shows the framework of TSCRNN. The raw traffic data are
converted to the standard formatted data via preprocessing, including
flow segmentation, sampling, vectorization, and normalization. In the
classification phase, the spatiotemporal features are captured to distin­
guish traffic types by the mixed neural networks model proposed in this
paper. TSCRNN is an end-to-end traffic classification scheme, which
outputs the label of traffic service types.
3.2. Preprocessing
3.2.1. Flow segmentation
In a real network system, the traffic collected at a node is not an
ordered sequence from a single application. For example, the traffic
captured from a gateway may be composed of all packets sent from
various hosts on the same network segment. To distinguish the traffic
flow produced by a single application, we need to split the raw traffic.
A flow implies that a sequence that contains packets that have the
same 5-tuple: (source IP, source port, destination IP, destination port,
transport layer protocol). The original traf-fic should be read, cached
and segmented according to the 5-tuple information.

3.2.3. Vectorization
Network traffic is binary data. To facilitate the calculation, the traffic
is read as bytes, converted to integers from 0 to 255 (8 bits). Each traffic
flow contains several time-related packets, we use the first N packets of
each flow, the first M bytes of each packet. Fig. 3 shows a vector of flow
after vectorization, which contains N packets. Each packet contains M
bytes (padding with 0 × 00).
To select appropriate values of N and M, the distribution of the
number of all flows and the distribution of the length of all packets of the
Tor-nonTor dataset are counted, as shown in Fig. 4 More than 90% of
flows are between 0 and 15, as shown in Fig. 4 (a), while the lengths of
almost all packets are in the interval from 0 to 1500 bytes, as shown in
Fig. 4 (b). The MTU (Maximum Transmission Unit) of Ethernet is exactly
1500 bytes.

3.2.2. Sampling
As shown in Fig. 2, the flow number of traffic service types in the TornonTor dataset shows the problem of data imbalance (the y-axis is a
logarithmic scale). Some types have a large sample size, such as
Browsing and P2P; while Tor types generally only have dozens of

3.2.4. Normalization
To make the model easier to train, all data are normalized by
dividing all numbers by 255.
3.3. Classification
The raw traffic data is high dimensional after vectorization. It greatly
increases the number of parameters of the deep learning model and
computation time, which is more likely to cause overfitting and is harder
to train. The sequential relationship between packet to packet is not
considered enough.
In this paper, we used CNN to learn the spatial characteristics, so that
high-dimensional features could be distilled into abstract feature maps,
and then designed a network architecture with RNN to learn the tem­
poral characteristics.
3.3.1. Features extraction
CNN is widely used in the field of deep learning for image processing
using 2D-CNN generally. LeCun et al. [33] pointed out that 1D-CNN is
suitable for one-dimensional sequence data that has strong local corre­
lations or whose features can appear anywhere. In the network flow,
there are specific patterns that could be captured by CNN, and abstract
spatial features are extracted through a multi-layer architecture. For
example, 1D-CNN [34] was soon used in text data. In the domain of
traffic classification, Wang et al. [26] introduced 1D-CNN to converted
the traffic flow into a one-dimensional sequence. However, the temporal
characteristics of traffic are not preserved, and the timing relationships
between packets are lost.
In this paper, the temporal dimension is preserved in the process of

Fig. 1. The framework of TSCRNN.
3

K. Lin et al.

Computer Networks 190 (2021) 107974

Fig. 2. The flow number of service types in the Tor-nonTor dataset.

such as the hyperbolic tangent. The filter is applied to the whole
sequence {x1:h , x2:h+1 , …, xn− h+1:n } to generate a feature map a〈c〉 .
]
[
〈c〉
〈c〉
a〈c〉 = a〈c〉
(3)
1 , a2 , …, an− h+1
where a〈c〉 is the feature map of the c-th filter. And then all feature maps

generated by m filters will be concatenated to be a new vector a ∈ Rmn ,
′
where n = n − h + 1 and a refer to a new feature map, containing m
channels. Besides, we use the max-over-time pooling operation to
downsample the traffic, which is similar to the convolution operation,
but each filter retains the maximum value as a new feature in each
operation.
In essence, CNN and fully connected neural networks are similar,
while CNN is characterized by filter weight sharing and sparse connec­
tion [33], which is of great help for the operation of high-dimensional
vectors. Here, traffic data is downsampled by 1D-CNN, and as the
layers deepen, the convolution operation will generate more abstract
feature maps. It means that the model will learn more advanced fea­
tures, which will assist subsequent learning of temporal features.
′

Fig. 3. The vectorization method of a traffic flow.

vectorization. Suppose that x〈t〉 ∈ Rk is a k-dimensional vector corre­
sponding to the t-th packet in a flow.
[
]
x = x〈1〉 , x〈t〉 , ⋯, x〈n〉
(1)
where x represents a flow with n packets. x is regarded as a twodimensional vector with n channels, each of which is k-dimension.
xi:i+h− 1 refers to traffic bytes from i to i + h − 1 in all channels. A con­
volutional operation involves the c-th filter w〈c〉 ∈ Rhk , which is applied
to a window of h traffic bytes in all channels to generate a new feature
a〈c〉 .
〈c〉
〈c〉
a〈c〉
i = f (w ⋅xi:i+h− 1 + b )

3.3.2. Abstract temporal features learning
RNN plays an important role in the represent learning of time series.
The most famous unit structure is Long Short-Term Memory(LSTM) [35,
36], which can solve the problem of gradient vanish(explosion) and has
been proved to achieve acceptable detection results in time series
analysis. For the same reason, LSTM could be used for network traffic
analysis, since it is a high time-dependent data as well.

(2)

where b〈c〉 ∈ R is a bias term and f is a non-linear activation function

Fig. 4. The statistical distributions of the Tor-nonTor dataset. (a) is the distribution of packet numbers in all flows. And (b) is the distribution of length of all packets.
4

K. Lin et al.

Computer Networks 190 (2021) 107974

]
)
( [
̃
c〈t〉 = tanh wc h〈t− 1〉 , a〈t〉 + bc

The second part includes the layers of RNN. The dimension of the
hidden layer of the Bi-LSTM unit is set to 256. However, the actual
output dimension is 512, for it concatenates the outputs of both di­
rections. Bi-LSTM needs to retain the output of each time step except the
last layer because of the stack architecture we used. Besides, to alleviate
the phenomenon of overfitting, the dropout layer is added after BiLSTM, and the dropout rate is set to 0.5. The last part is a fully con­
nected layer, which inputs a 512-dimensional vector and outputs a 16dimensional vector. The final output dimension is the same as the
number of categories corresponding to scenarios. Finally, Softmax is
used to calculate the prediction probability of each type. Detailed ar­
chitecture and parameters of the classification model are shown in
Table I, where F is filter size and S is stride and the total parameters are
2,897,104.
It extracts abstract features before learning temporal characteristics,
that can reduce the number of parameters. The classification model
combines the speed of CNN and the time-sensitivity of RNN, which
makes it more lightweight while retaining both advantages.
In the training processing, the batch size is set to 128 and the opti­
mizer is Adam. Besides, we use the learning rate scheduling technique to
help the model converge better. First of all, in the first 30 epochs, the
learning rate is set to 1e − 3, as a larger learning rate can accelerate the
convergence in the early phase of training. After that, the learning rate
will be reduced by a fixed multiple of 0.3 iteratively, training a total of
20 epochs. Finally, the best performance model is obtained by early stop.
Algorithm 1 is the pseudo-code of the classification model of
TSCRNN, describing how a vector of traffic is identified by the classifi­
cation model.

(4)

where a〈t〉 ∈ Rs , representing the t-th channel of the feature map, which

is a s-dimensional vector. h〈t− 1〉 ∈ Ru is the output of the hidden layer at
the last time step, and its dimension is u. w and b are the corresponding
parameters matrix and bias term respectively. And̃
c〈t〉 is the intermediate
output of the hidden layer. The ultimate output is determined by three
terms called gate in LSTM.
( [
]
)
(5)
Γ u = σ wu h〈t− 1〉 , a〈t〉 + bu

( [
]
)
Γ f = σ wf h〈t− 1〉 , a〈t〉 + bf

(6)

( [
]
)
Γ o = σ wo h〈t− 1〉 , a〈t〉 + bo

(7)

The calculation of the three gates are similar tõc . They act as
switches to control output values. Γ u , Γ f and Γ o are called update gate,
forget gate, and output gate respectively.
〈t〉

c〈t〉 = Γ u ⊙ ̃
c〈t〉 + Γ f ⊙ c〈t− 1〉

(8)

h〈t〉 = Γ o ⊙ tanh(c〈t〉 )

(9)

where h〈t〉 is the final output of the hidden layer at the current time step.
It is affected by three gates, which represent the trade-offs of the past,
current and total output respectively. The ⊙ operator is the Hadamard
product. Based on abstract features, stack bidirectional LSTM is used to
design the proposed architecture. Stack LSTM refers to a multi-layer
LSTM, and bidirectional LSTM (Bi-LSTM) is to perform LSTM opera­
tion simultaneously in both directions in the original sequence. It means
←〈t〉
→〈t〉
that h〈t〉 is the concatenate vector of both directions outputs, h and h ,
when using the Bi-LSTM. As the contextual information contains both
the front and the back [37].
[→t ←t ]
(10)
ht = h , h

4. Experiments
4.1. Experimental dataset
We implemented most experiments based on the ISCX-Tor2016
dataset, which was collected by Lashkari on the network of New
Brunswick University (UNB) [12]. ISCX-Tor2016 contains two kinds of
labels. One is traffic application, including AIM chat, Skype, Youtube,
etc. The other is traffic service type, including Chat, Audio, FTP, etc., as
shown in Table II. Two versions of each type are collected in a regular
network and a tor network at the same time.
To validate the universality of TSCRNN, we also implemented ex­
periments based on other datasets. One of them is the VPN-nonVPN
dataset [27]. The details of the VPN-nonVPN dataset are shown in
Table III.
Another dataset is the USTC-TFC2016 dataset, containing ten cate­
gories of benign traffic and ten categories of malicious traffic [39], as
shown in Table IV.
All the datasets mentioned above were collected from the real
network environment.

3.3.3. Classification model
Fig. 5 shows the classification model of TSCRNN of TSCRNN. The
classification model is composed of three parts, the first part includes the
convolution related layers. This part contains four different layers,
comprising 1D-CNN, BatchNormalization, ReLU, and MaxPooling.
The filter size of 1D-CNN is set to 3, the stride is 1, the padding is 1.
The batch normalization [38] is used to standardize the output of the
last layer, which makes gradient descent easier. At the end of this block,
MaxPooling is applied to downsample the data.

Table I
Parameters of the classification model.
Block

Layer Name

F

S

Output

Parameter

Conv1

Conv1d-1
BatchNorm1d-2
ReLU-3
MaxPool1d-4
Conv1d-5
BatchNorm1d-6
ReLU-7
MaxPool1d-8
Bi-Lstm-9
Dropout-10
Bi-Lstm-11
Dropout-12
Linear-13
Softmax-14

3
2
3
2
-

1
2
1
2
-

(64, 1500)
(64, 1500)
(64, 1500)
(64, 750)
(64, 750)
(64, 750)
(64, 750)
(64, 325)
(64, 512)
(64, 512)
(512,)
(512,)
(16,)
(16,)

2,944
128
12,352
128
-

Conv2

LSTM

FC
Softmax

Fig. 5. The classification model in TSCRNN.
5

2,873,344
8,208
-

K. Lin et al.

Computer Networks 190 (2021) 107974

tasks. Scenario B is to distinguish between eight normal traffic ser­
vices like audio, browsing, etc. Scenario C is similar to B, while its target
labels are eight traffic services of the tor version. Scenario D mixes all the
sixteen types mentioned in scenario B and scenario C to perform the 16classification task.

Table II
The description of the tor-nontor dataset.
Type

Labels

Tor
nonTor

Audio, Browsing, Chat, Email, FTP, P2P, Video, VoIP
torAudio, torBrowsing, torChat, torEmail, torFTP, torP2P, torVideo,
torVoIP

4.3.1. Selections of preprocessing strategy
In the preprocessing phase, different strategies were chosen,
including the selection of sampling methods and the settings of packet
parameters.
For sampling strategies, there were three methods tested, including
Random Sampling, Fixed Step Sampling, and Mixed Sampling, and
Table VI shows the Marco − F1 of all scenarios affected by each of them.
As shown in Table VI, sampling strategies of both Fixed Step sam­
pling and Mixed sampling have slightly improved the performance of
scenario B and scenario D. However, the disparities are too small to be
noticed, which implies that the traffic classification of middle flow
sampling is not sensitive to sampling strategies. In other words, it has
robustness in this respect.
Furthermore, we need to focus on the settings of packet parameters.
From the distribution of packet number (Fig. 4 (a)) in a flow and packets
length (Fig. 4 (b)), it can be observed that they are mainly distributed in
(0, 15) and in (0, 1500)respectively. Consequently, the numbers of
packets are selected as 5, 10, and 15, while the packet lengths are
selected as 500, 1000, and 1500. And a grid search is performed for all of
them.
The Table VII showed the performances with different packet
parameter settings in all scenarios, including the packet number of each
flow and packet length. It indicates that the improvement of packet
length on the F1 value is not obvious. Even after the packet length in­
creases to more than 1000 bytes, there are some weak negative effects. It
is speculated that the longer packet length is, the more information is
obtained and the more noise is introduced at the same time.
Another packet parameter is the number of packets in each flow,
which has a great impact on the performance. That is, with the increase
of packets of each flow, the F1 value of each scenario has a certain de­
gree of improvement. This is because more packets can help the model to
capture the time-related features.
It can be seen that the best performance emerged when the packet
number is set to 15 and the packet length is set to 500, which demon­
strates that the most valid information exists in the front part of the
packet. However, considering the effect of packet length selections is
weak which is also affected by training randomness, so the parameter of
packet length is set to 1500 (consistent with MTU) without loss of
generality. In subsequent experiments, the default sampling strategy is
random sampling, while the number of packets is set to 15.

Table III
The description of the VPN-nonVPN dataset.
Type

Labels

VPN
nonVPN

Chat, Email, FTP, P2P, Streaming, VoIP
vpnChat, vpnEmail, vpnFTP, vpnP2P, vpnStreaming, vpnVoIP

Table IV
The description of USTC-TFC2016 dataset.
Type

Labels

Benign

BitTorrent, Facetime, FTP, Gmail, MySQL, Outlook, Skype, SMB, Weibo,
WorldOfWarcraft
Cridex, Geodo, Htbot, Miuref, Neris, Nsis-ay, Shifu, Tinba, Virut, Zeus

Malware

4.2. Evaluation metric
We used four metrics to evaluate the classification performances of
different methods, including accuracy (AC), precision (PR), recall (RC),
and F1. For a multi-classification problem, each class and the remaining
samples are considered as a binary classification at first, which makes
the precision and recall of each type can be calculated directly.
TP + TN
TP + TN + FP + FN

(11)

TP
TP + FP

(12)

Accuracy (AC) =

Precision (PR) =

Recall (RC) =

F1 = 2 ×

TP
TP + FN

Precision × Recall
Precision + Recall

(13)
(14)

where TP, FP, TN, FN refer to true positive, false positive, true negative,
false negative respectively. To compare the quality of multiple in­
dicators jointly, the harmonic average F1 is used to unify both PR and RC
into a single metric.
Since it is a multi-classification problem, it is not convenient to use
PR, RC, F1 for a single type. Therefore, Macro Average [40] is used to
calculate the mean value of precision, recall, F1 of each category as
follows:
∑
F1i
Macro − F1 = i ∈ classes
(15)
N

4.3.2. Experimental results
As shown in Table VIII and Fig. 6, TSCRNN performs well in all four
scenarios. It is worth noting that all metrics of the whole types
usemacro-average and the same as below.
4.3.3. Comparison with related works
In [12], The author used machine learning methods to perform bi­
nary classifications and eight classification tasks of Tor traffic. Since the
data imbalance problem of the binary classification task is not dealt with
in the paper, the experimental results cannot reflect the real

4.3. Experimental results and analysis
The experimental hardware platform is a computer equipped with a
CPU of ADM RYZEN 3700 × 3.6GHz and a 16 GB of memory. The GPU
accelerator is NVIDIA GeForce RTX 2070S. The framework runs on
Python 3.7, and the deep learning platform is Pytorch 1.4.0. SplitCap
(version 2.1) is used in the preprocessing phase, and the binary output
stream is read by Scapy.
To test the performance of TSCRNN, four scenarios of different
classification tasks were proposed in experiments as shown in Table V.
Scenario A is a 2-classification to indicate whether the traffic flow is tor
or normal traffic. Both scenario B and scenario C are 8-classification

Table V
The experimental description.

6

Scenario

Description Classifier

Scenario A
Scenario B
Scenario C
Scenario D

Tor and Non-Tor traffic identification 2-class
Regular encrypted traffic classification 8-class
Tor protocol encapsulated traffic classification 8-class
Encrypted traffic classification 16-class

K. Lin et al.

Computer Networks 190 (2021) 107974

from Table X that the performance of TSCRNN based on spatiotemporal
features in Scenario A, B, and D is better than other deep learning
methods, and only slightly worse in Scenario C.
In recent years, many studies have conducted experiments of
encrypted traffic classification on VPN-nonVPN dataset and proposed
state of the art methods based on deep learning. To better compare with
these methods, we conduct experiments on the VPN-nonVPN dataset as
well.
Among them, One-dim CNN was proposed by Wang [26], and for the
first time, CNN was used to capture the spatial characteristics of the
traffic. Haipen Yao. et al [41] proposed HAN and Attention Based LSTM,
which are based on time characteristics and combined with the attention
mechanism. Deep Packet is proposed in the paper [7].
It can be seen from Table XI that TSCRNN has achieved excellent
performance in the VPN-nonVPN dataset, and only Scenario B per­
formed poorly.

Table VI
The Macro-F1 values of all scenario with different sampling strategies (F1).
Strategy

Scenario A

Scenario B

Scenario C

Scenario D

Random
Fixed Step
Mixed

0.979
0.980
0.979

0.979
0.995
0.996

0.909
0.909
0.908

0.948
0.949
0.947

Table VII
The Macro-F1 values of all scenario with different packet parameters (F1).
Strategy

Scenario A

Scenario B

Scenario C

Scenario D

5, 500
5, 1000
5, 1500
10, 500
10, 1000
10, 1500
15, 500
15, 1000
15, 1500

0.983
0.984
0.981
0.979
0.981
0.979
0.983
0.981
0.979

0.992
0.993
0.987
0.992
0.990
0.979
0.993
0.991
0.979

0.888
0.902
0.899
0.909
0.913
0.912
0.913
0.906
0.909

0.939
0.936
0.934
0.947
0.946
0.940
0.951
0.949
0.948

4.3.4. Experiments of 16-classification
Further experiments were implemented in the most complex task in
scenario D, that is, the sixteen classification task. As shown in Table XII,
TSCRNN performs well in all types of traffic except Email and Chat. One
reason is that there is not sufficient raw data of Email and Chat in the
dataset. Another reason is that these two types of traffic are difficult to
identify through multiple experiments, due to they are both short-lived
data stream and similar in time distribution.
As shown in Fig. 7, it can readily find from the confusion matrix that
the reason why the Email and Chat traffic have poor performance is that
they are easily confused with each other. That is, 26% of Email flows are
incorrectly identified as Chat, while 12% of Chat samples are predicted
as Email. Such a phenomenon appeared in a series of experiments, which
illustrates that the spatial and temporal distributions of both of them are
similar. Fig. 8 visualizes the detailed experimental data for convenient
observations.

Table VIII
The experimental results in all scenarios.
Scenario

AC

PR

RC

F1

Scenario A
Scenario B
Scenario C
Scenario D

0.994
0.979
0.909
0.950

0.987
0.979
0.910
0.949

0.990
0.979
0.908
0.948

0.988
0.979
0.909
0.948

4.3.5. Visualization of traffic
To verify whether the model correctly learns the spatiotemporal
features, the activation on each byte in each flow is visualized as well.
Fig. 9 shows one way to visualize traffic, which stretches the sample
with the dimension of 1 × 15 × 1500 to a one-dimensional array with
the dimension of 22,500 × 1, regrading the bytes as the strength of the
signal on each position with the range (0, 255).
It is easy for our humans to find that different service types of traffic
in Fig. 10 have different distribution characteristics. Besides, compared
with Fig. 9 (a) and Fig. 9 (b), it can be found that the distinction becomes
more obvious after tor network encryption. That is why TSCRNN per­
formed better on tor traffic than those of normal traffic in multiple ex­
periments. Furthermore, it can be found that the presentations of Email
and Chat are quite similar.
On the other hand, we visualized the activation on each point in the
traffic flow of the classification model. The red area in Fig. 10 indicates
the interest of the model in each part of the flow. The loss function is
used to calculate the gradient on the input. And the values of gradient
represent the activations on each byte, referring to their contribution to
the final prediction.
In Fig. 10, four samples were randomly chosen. From the perspective
of the overall flow, the interest region is more concentrated on the first
few packets in a flow. And from the perspective of each packet, the
model focuses on the front bytes of the packet. This is in line with our

Fig. 6. The experimental results in all scenarios.

performance. Therefore, only the Tor eight classification task is
compared as shown in Table IX. It can be seen from Table IX that
TSCRNN performs better than machine learning methods, and its Pre­
cision and Recall reach 97.9% and 97.8%.
There are few methods based on deep learning on the Tor-nonTor
dataset, so we implemented the other two methods based on deep
learning to compare with TSCRNN.
One-dim CNN is mainly based on spatial features, and the model
design refers to the paper []. Time Series mainly considers the time step
characteristics of packets, whose design is based on LSTM. It can be seen

Table IX
Comparison of TSCRNN and machine learning methods in Tor eight classifica­
tion task.
Metric

TSCRNN

RandomForest

C4.5

KNN

Precision
Recall

0.979
0.978

0.842
0.836

0.797
0.798

0.704
0.707

Table X
Comparison of TSCRNN and deep learning methods in tor-nontor dataset (F1).

7

Method

Scenario A

Scenario B

Scenario C

Scenario D

One-dim CNN
Time Series
TSCRNN

0.981
0.979
0.988

0.957
0.941
0.979

0.901
0.915
0.909

0.927
0.925
0.948

K. Lin et al.

Computer Networks 190 (2021) 107974

results of the twelve classification tasks of the VPN-nonVPN dataset will
be reported in Table XIII.
Furthermore, we validated the performance of TSCRNN on the
USTC-TFC2016 datasets, detecting malicious traffic, which is different
from the other two datasets captured by UNB. Table XIV shows the
experimental results of a 20-classification task in USTC-TFC2016.
TSCRNN achieves the F1 values up to 90% in mostly all categories,
and even reaches 100% in some classes.

Table XI
Accuracy comparison of TSCRNN and deep learning methods in VPN-nonVPN
dataset.
Method

Scenario A

Scenario B

One-dim CNN
HAN
Attention Based LSTM
Deep Packet
TSCRNN

0.990
0.995
0.997
0.992
0.997

0.818
0.851
0.893
0.868
0.864

Scenario C

0.986
0.929
0.948
0.923
0.965

Scenario D

0.866
0.895
0.912
0.895
0.917

4.3.7. Summary of performance analysis
The accuracies of TSCRNN in Scenario A, B, C, D are 99.4%, 97.9%,
90.9%, 95.5% severally, while the values of F1 are 98.8%, 97.9%,
90.9%, and 94.8%. Experimental data, confusion matrix, and activation
visualization demonstrates that TSCRNN can better learn the spatio­
temporal features of the traffic flows.
TSCRNN was applied to the other two datasets, ISCXVPN2016 and
USTC-TFC2016, without any special settings. The values of F1 of both
entire datasets reached 92.6% and 98.7% respectively. It proves that
TSCRNN is universal, not limited to specific scenarios.
To sum up, TSCRNN performs well in most classification tasks of

Table XII
The detailed experimental results of sixteen classification task.
Type

PR

RC

F1

Audio
Browsing
Chat
Email
FTP
P2P
Video
VoIP
torAudio
torBrowsing
torChat
torEmail
torFTP
torP2P
torVideo
torVoIP
Macro-Avg

0.944
0.949
0.733
0.839
0.996
0.996
0.922
0.919
0.981
0.977
0.996
0.996
0.992
0.959
0.985
1.000
0.949

0.948
0.970
0.822
0.717
0.988
0.992
0.901
0.954
0.966
0.977
0.989
0.975
0.996
0.992
0.996
0.988
0.948

0.946
0.960
0.775
0.773
0.992
0.994
0.912
0.936
0.973
0.977
0.993
0.985
0.994
0.976
0.991
0.994
0.948

expectations that the model has captured spatiotemporal features of
traffic flow correctly.
4.3.6. Experiments on other datasets
TSCRNN has performed well in the Tor-nonTor dataset. To verify its
versatility, TSCRNN was applied to other datasets. Similarly, raw traffic
of the other two datasets is input into TSCRNN and the labels are output,
with the same preprocessing process, model, and parameter settings.
The first dataset is the VPN-nonVPN dataset. The detailed experimental

Fig. 8. The detailed experimental results of scenario D.

Fig. 7. The confusion matrix of the sixteen-classification task.
8

K. Lin et al.

Computer Networks 190 (2021) 107974

experiments. The main experiments were carried out on the Tor-nonTor
dataset. TSCRNN outperforms other classification methods based on
machine learning and deep learning.The reason is that TSCRNN con­
siders the temporal and spatial characteristics at the same time. TSCRNN
uses CNN to extract abstract features and then learned the temporal
characteristics based on those low-dimensional feature maps by stack BiLTSM.
Furthermore, TSCRNN is validated on other datasets without any
special settings, which achieves appropriate performance as well. It
means that the traffic service perception and identification mechanism
provided by TSCRNN will be helpful to IIoT, such as communication,
network, information processing, and security.
In the future, we will focus on the following three aspects.
• The traffic datasets are always unbalanced. Therefore, generative
models like the autoencoder or the generative adversarial network
(GAN) can be used to solve this problem.
• There is currently no unified preprocessing scheme in the field of
traffic classification. Different preprocessing methods can corre­
spond to different levels of features, such as byte features, packet
time-related features, statistical features, etc. Multi-level features
fusion can be used to further improve performance.
• The labeling of real-world traffic is still a challenge in this field.
Unsupervised learning and semi-supervised learning may help to
classification with limited labeled samples.
Declaration of Competing Interest
The authors declare that they have no known competing financial
interests or personal relationships that could have appeared to influence
Fig. 9. The visualization of traffic flows. (a) are samples of normal traffic, and
(b) are the samples of tor traffic.

Table XIII
The detailed experimental results of VPN-nonVPN dataset.

network traffic.
5. Conclusion
Network encryption traffic classification is one of the essential tasks
in systems of IIoT, such as networking, communication, security, and
information processing. In this paper, we proposed a novel approach
TSCRNN to realize encrypted traffic classification. There were pre­
processing module and classification module in the framework of
TSCRNN, which was input raw traffic file and outputted the label of
prediction.
To evaluated TSCRNN, four distinct scenarios were set for

Type

PR

RC

F1

Chat
Email
FTP
P2P
Stream
VOIP
vpnChat
vpnEmail
vpnFTP
vpnP2P
vpnStream
vpnVOIP
Macro-Avg

0.762
0.842
0.943
0.977
0.965
0.843
0.967
0.963
0.957
0.972
0.950
0.985
0.927

0.851
0.780
0.892
0.955
0.935
0.913
0.972
0.987
0.941
0.965
0.945
0.977
0.926

0.804
0.810
0.917
0.966
0.950
0.877
0.970
0.975
0.949
0.968
0.948
0.981
0.926

Fig. 10. The activations on each byte of traffic flow.
9

K. Lin et al.

Computer Networks 190 (2021) 107974
[3] H. Tahaei, F. Afifi, A. Asemi, F. Zaki, N.B. Anuar, The rise of traffic classification in
IoT networks: A survey, J. Netw. Comp. Appl.154 (2020), 102538.
[4] J. Xie, F.R. Yu, T. Huang, R. Xie, J. Liu, C. Wang, Y. Liu, A survey of machine
learning techniques applied to software defined networking (SDN): Research issues
and challenges, IEEE Commun. Surv. Tutor.21 (1) (2018) 393–430.
[5] G. Aceto, D. Ciuonzo, A. Montieri, A. Pescapé, Mobile encrypted traffic
classification using deep learning: Experimental evaluation, lessons learned, and
challenges, IEEE Trans. Netw. Serv. Manag.16 (2) (2019) 445–458.
[6] S. Yu, M. Liu, W. Dou, X. Liu, S. Zhou, Networking for big data: A survey, IEEE
Commun. Surv. Tutor. 19 (1) (2016) 531–549.
[7] M. Lotfollahi, M.J. Siavoshani, R.S.H. Zade, M. Saberian, Deep packet: A novel
approach for encrypted traffic classification using deep learning, Soft Computing
24 (3) (2020) 1999–2012.
[8] S. Yu, W. Zhou, W. Jia, S. Guo, Y. Xiang, F. Tang, Discriminating DDoS attacks from
flash crowds using flow correlation coefficient, IEEE Trans. Parallel Distribut. Syst.
23 (6) (2011) 1073–1080.
[9] Y. Wu, Cloud-edge orchestration for the internet-of-things: Architectureand aipowered data processing, IEEE Internet of Things J. (2020).
[10] P. Ducange, G. Mannarà, F. Marcelloni, R. Pecori, M. Vecchio, A novel approach for
internet traffic classification based on multi-objective evolutionary fuzzy
classifiers, in: 2017 IEEE international conference on fuzzy systems (FUZZ-IEEE),
IEEE, 2017, pp. 1–6.
[11] G. Aceto, D. Ciuonzo, A. Montieri, A. Pescapé, Toward effective mobile encrypted
traffic classification through deep learning, Neurocomputing 409 (2020) 306–315.
[12] A.H. Lashkari, G.D. Gil, M.S.I. Mamun, A.A. Ghorbani, Characterization of tor
traffic using time based features, in: ICISSP 2017 - Proceedings of the 3rd
International Conference on Information Systems Security and Privacy 2017-Janua
(September), 2017, pp. 253–262, https://doi.org/10.5220/0006105602530262.
[13] Y. Qi, L. Xu, B. Yang, Y. Xue, J. Li, Packet classification algorithms: From theory to
practice, in: IEEE INFOCOM 2009, IEEE, 2009, pp. 648–656.
[14] A. Madhukar, C. Williamson, A longitudinal study of P2P traffic classification, in:
14th IEEE International Symposium on Modeling, Analysis, and Simulation, IEEE,
2006, pp. 179–188.
[15] J. Sherry, C. Lan, R.A. Popa, S. Ratnasamy, Blindbox: Deep packet inspection over
encrypted traffic, in: Proceedings of the 2015 ACM Conference on Special Interest
Group on Data Communication, 2015, pp. 213–226.
[16] D. Bonfiglio, M. Mellia, M. Meo, D. Rossi, P. Tofanelli, Revealing skype traffic:
when randomness plays with you, in: Proceedings of the 2007 conference on
Applications, technologies, architectures, and protocols for computer
communications, 2007, pp. 37–48.
[17] S. Yu, G. Zhao, W. Dou, S. James, Predicted packet padding for anonymous web
browsing against traffic analysis attacks, IEEE Trans. Inform. Forens. Secur.7 (4)
(2012) 1381–1393.
[18] H. Liu, Z. Wang, Y. Wang, Semi-supervised encrypted traffic classification using
composite features set, J. Netw.7 (8) (2012) 1195.
[19] B. Anderson, S. Paul, D. McGrew, Deciphering malware’s use of TLS (without
decryption), J. Comp. Virol. Hack. Tech.14 (3) (2018) 195–211.
[20] A. Fahad, Z. Tari, I. Khalil, I. Habib, H. Alnuweiri, Toward an efficient and scalable
feature selection approach for internet traffic classification, Comp. Netw.57 (9)
(2013) 2040–2057.
[21] A. Moore, D. Zuev, M. Crogan, Discriminators for use in flow-based classification,
Tech. Rep. (2013).
[22] B. Yamansavascilar, M.A. Guvensan, A.G. Yavuz, M.E. Karsligil, Application
identification via network traffic classification, in: 2017 International Conference
on Computing, Networking and Communications (ICNC), IEEE, 2017, pp. 843–848.
[23] R. Alshammari, A.N. Zincir-Heywood, Can encrypted traffic be identified without
port numbers, IP addresses and payload inspection? Comp. Netw. 55 (6) (2011)
1326–1350.
[24] J. Zhang, X. Chen, Y. Xiang, W. Zhou, J. Wu, Robust network traffic classification,
IEEE/ACM Trans. Netw.23 (4) (2014) 1257–1270.
[25] E. Hodo, X. Bellekens, E. Iorkyase, A. Hamilton, C. Tachtatzis, R. Atkinson,
Machine learning approach for detection of nontor traffic, in: Proceedings of the
12th International Conference on Availability, Reliability and Security, 2017,
pp. 1–6.
[26] W. Wang, M. Zhu, J. Wang, X. Zeng, Z. Yang, End-to-end encrypted traffic
classification with one-dimensional convolution neural networks, in: 2017 IEEE
International Conference on Intelligence and Security Informatics (ISI), IEEE, 2017,
pp. 43–48.
[27] G. Draper-Gil, A.H. Lashkari, M.S.I. Mamun, A.A. Ghorbani, Characterization of
encrypted and VPN traffic using time-related features, in: ICISSP 2016 Proceedings of the 2nd International Conference on Information Systems Security
and Privacy, no, Icissp, 2016, pp. 407–414, https://doi.org/10.5220/
0005740704070414.
[28] V. Tong, H.A. Tran, S. Souihi, A. Mellouk, A novel quic traffic classifier based on
convolutional neural networks, in: 2018 IEEE Global Communications Conference
(GLOBECOM), IEEE, 2018, pp. 1–6.
[29] T. Shapira, Y. Shavitt, Flowpic: Encrypted internet traffic classification is as easy as
image recognition, in: IEEE INFOCOM 2019-IEEE Conference on Computer
Communications Workshops (INFOCOM WKSHPS), IEEE, 2019, pp. 680–687.
[30] M. Lopez-Martin, B. Carro, A. Sanchez-Esguevillas, J. Lloret, Network traffic
classifier with convolutional and recurrent neural networks for Internet of Things,
IEEE Access 5 (2017) 18042–18050.
[31] W. Wang, Y. Sheng, J. Wang, X. Zeng, X. Ye, Y. Huang, M. Zhu, HAST-IDS: Learning
hierarchical spatial-temporal features using deep neural networks to improve
intrusion detection, IEEE Access 6 (2017) 1792–1806.

Table XIV
The detailed experimental results of USTC-TFC2016 dataset.
Type

PR

RC

F1

Cridex
Geodo
Htbot
Miuref
Neris
Nsis-ay
Shifu
Tinba
Virut
Zeus
BitTor
Facetime
FTP
Gmail
MySQL
Outlook
Skype
SMB
Weibo
Wow
Macro-Avg

1.000
1.000
1.000
1.000
0.892
0.996
0.996
0.996
0.862
1.000
1.000
1.000
1.000
1.000
1.000
1.000
1.000
0.996
1.000
1.000
0.987

1.000
1.000
1.000
0.996
0.848
0.972
1.000
0.996
0.921
1.000
1.000
1.000
1.000
1.000
1.000
1.000
1.000
1.000
0.996
1.000
0.986

1.000
1.000
1.000
0.998
0.870
0.984
0.998
0.996
0.891
1.000
1.000
1.000
1.000
1.000
1.000
1.000
1.000
0.998
0.998
1.000
0.987

Algorithm 1
Classification model.
Input: x, x ∈ Rnk , referring to a vector of flow, which containing n packets and
dimension of each packet is k
Output: The probabilities of each type
1 a = x;
2 Downsampling through Ncnn convolutional layers, including Conv1D,
BatchNormalizaion, MaxPooling;
3 fori = 1; i ≤ Ncnn ; i + + do
4 a = Conv1D(a);
5 a = BatchNormalization1D(a);
6 a = MaxPooling(a);
8 end for
9 Learning time-series features throughNlstm layers of BiLSTM;
10 fori = 1; i ≤ Nlstm ; i + + do

11ApplyingLSTM at each time step in both directions;
12 fora〈t〉 in ado
→〈t〉
13 h = LSTM1 (a〈t〉 );
←〈t〉

14 h

= LSTM2 (a〈t〉 );

→〈t〉 ←〈t〉
15 h〈t〉 = [ h , h ];

16 end for

17 a = [h〈1〉 , h〈2〉 , ⋯, h〈t〉 ];
18 end for
19 a = FullConnet(a〈n〉 );
20 probabilites = Softmax(a);
21 return probabilites;

the work reported in this paper.
Acknowledgments
We would like to thank the reviewers in advance for their comments
to help us improve the quality of this paper. This work was supported by
the National Natural Science Foundation of China under Grant
62072255.
References
[1] H. Wang, Y. Wu, G. Min, W. Miao, A Graph Neural Network-based Digital Twin for
Network Slicing Management, IEEE Trans. Indust. Inform. (2020).
[2] S. Rezaei, X. Liu, Deep learning for encrypted traffic classification: An overview,
IEEE Commun. Mag.57 (5) (2019) 76–81.

10

K. Lin et al.

Computer Networks 190 (2021) 107974
Xiaolong Xuis currently a professor in the School of Computer
Science, Nanjing University of Posts & Telecommunications,
Nanjing, China. He is also working for the Jiangsu Key Labo­
ratory of Big Data Security & Intelligent Processing. He
received the B.E. in computer and its applications, M.E. in
computer software and theories and Ph.D. degree in commu­
nications and information systems, in 1999, 2002 and 2008,
respectively. He is a senior member of China Computer
Federation. He teaches graduate courses and conducts research
in areas of Cloud Computing, Big Data, Information Security
and Novel Network Computing Technologies. As the leader of
project teams, he has successfully completed a number of highlevel research projects, including the projects sponsored by the National Science Fund of
China. He has published more than 100 Journal and conference papers as the first or
corresponding author and 5 books. He is authorized 52 patents by the State Intellectual
Property Office of China as the first inventor. He was rated as excellent young professor of
Jiangsu Province in 2014, selected as the high-level creative talents of Jiangsu province in
2015, and won the title of outstanding expert in the area of computer science and
technology.

[32] S.Rezaei, X.Liu, How to achieve high classification accuracy with just a few labels:
A semi-supervised approach using sampled packets, arXiv preprint arXiv:
1812.09761 (2018).
[33] Y. LeCun, Y. Bengio, G. Hinton, Deep learning, Nature 521 (7553) (2015) 436–444.
Google Scholar Google Scholar Cross Ref Cross Ref.
[34] Y. Kim, Convolutional neural networks for sentence classification, EMNLP (2014).
[35] S. Hochreiter, J. Schmidhuber, Long short-term memory, Neural Computation 9 (8)
(1997) 1735–1780.
[36] Y. Bengio, P. Simard, P. Frasconi, Learning long-term dependencies with gradient
descent is difficult, IEEE Trans. Neur. Netw.5 (2) (1994) 157–166.
[37] X. Liu, J. You, Y. Wu, T. Li, L. Li, Z. Zhang, J. Ge, Attention-based bidirectional
GRU networks for efficient HTTPS traffic classification, Inform. Sci.541 (2020)
297–315.
[38] S. Ioffe, C. Szegedy, Batch normalization: Accelerating deep network training by
reducing internal covariate shift, in: International conference on machine learning,
PMLR, 2015, pp. 448–456.
[39] W. Wang, M. Zhu, X. Zeng, X. Ye, Y. Sheng, Malware traffic classification using
convolutional neural network for representation learning, in: 2017 International
Conference on Information Networking (ICOIN), IEEE, 2017, pp. 712–717.
[40] C. Liu, W. Wang, M. Wang, F. Lv, M. Konan, An efficient instance selection
algorithm to reconstruct training set for support vector machine, Knowledge-Based
Systems 116 (2017) 58–73.
[41] H. Yao, C. Liu, P. Zhang, S. Wu, C. Jiang, S. Yu, Identification of Encrypted Traffic
Through Attention Mechanism Based Long Short Term Memory, IEEE Transactions
on Big Data (2019).

Honghao Gao received the Ph.D. degree in Computer Science
and started his academic career at Shanghai University in
2012. Prof. Gao is currently with the School of Computer En­
gineering and Science, Shanghai University, China. He is also a
Professor at Gachon University, South Korea. Prior to that, he
was a Research Fellow with the Software Engineering Infor­
mation Technology Institute of Central Michigan University
(CMU), USA, and was also an Adjunct Professor at Hangzhou
Dianzi University, China. His research interests include Soft­
ware Formal Verification, Industrial IoT/Wireless Networks,
Service Collaborative Computing, and Intelligent Medical
Image Processing. He has publications in IEEE TII, IEEE T-ITS,
IEEE IoT-J, IEEE TNSE, IEEE TCCN, IEEE/ACM TCBB, ACM TOIT, ACM TOMM, IEEE TCSS,
IEEE TETCI, IEEE Network, and IEEE JBHI. Prof. Gao is a Fellow of IET, BCS, and EAI, and
a Senior Member of IEEE, CCF, and CAAI. He is the Editor-in-Chief for International
Journal of Intelligent Internet of Things Computing(IJIITC), Editor for Wireless Network
(WINE) and IET Wireless Sensor Systems(IET WSS), and Associate Editor for IET Software,
International Journal of Communication Systems(IJCS), Journal of Internet Technology
(JIT), and Journal of Medical Imaging and Health Informatics(JMIHI). Moreover, he has
broad working experiences in industry-university-research cooperation. He is a European
Union Institutions appoint external expert for reviewing and monitoring EU Project, is a
member of the EPSRC Peer Review Associate College for UK Research and Innovation in
the UK, and is also a founding member of IEEE Computer Society Smart Manufacturing
Standards Committee.

Kunda Lin is currently working as a researcher for the Jiangsu
Key Laboratory of Big Data Security & Intelligent Processing,
Nanjing, China. His research interests include AI-based IoT
optimization. He has a patent in the above field authorized by
the State Intellectual Property Office of China as one of the key
inventors. He has won three national and provincial competi­
tion awards, and ranked first in school algorithm competition.
He won several scholarships during university. He used to work
at Institute of Big Data Research at Yancheng. He is going to
pursue his PhD degree major in Information networks in
Nanjing University of Posts & Telecommunications, Nanjing,
China .

11
PAPER_TEXT
