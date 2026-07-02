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
# [301] Semi-Supervised Encrypted Malicious Traffic Detection Based on Multimodal Traffic Characteristics
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
编号：301
题名：Semi-Supervised Encrypted Malicious Traffic Detection Based on Multimodal Traffic Characteristics
年份：2024
DOI：10.3390/s24206507
来源：Sensors
PDF：paper/10.3390_s24206507.pdf
已有粗分类：恶意流量、暗网与攻击检测
二级关联：无
相关性：强相关，分数 15
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\301.txt
- 原始字符数：96453
- 本次发送字符数：96453
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
sensors
Article

Semi-Supervised Encrypted Malicious Traffic Detection Based on
Multimodal Traffic Characteristics
Ming Liu

, Qichao Yang, Wenqing Wang and Shengli Liu *
Information Engineering University, Zhengzhou 450001, China; lm_puree@outlook.com (M.L.);
yangqichaoo@foxmail.com (Q.Y.); wenqingww@126.com (W.W.)
* Correspondence: mr_shengliliu@163.com

Abstract: The exponential growth of encrypted network traffic poses significant challenges for detecting malicious activities online. The scale of emerging malicious traffic is significantly smaller than that
of normal traffic, and the imbalanced data distribution poses challenges for detection. However, most
existing methods rely on single-category features for classification, which struggle to detect covert
malicious traffic behaviors. In this paper, we introduce a novel semi-supervised approach to identify
malicious traffic by leveraging multimodal traffic characteristics. By integrating the sequence and
topological information inherent in the traffic, we achieve a multifaceted representation of encrypted
traffic. We design two independent neural networks to learn the corresponding sequence and topological features from the traffic. This dual-feature extraction enhances the model’s robustness in detecting
anomalies within encrypted traffic. The model is trained using a joint strategy that minimizes both the
reconstruction error from the autoencoder and the classification loss, allowing it to effectively utilize
limited labeled data alongside a large amount of unlabeled data. A confidence-estimation module
enhances the classifier’s ability to detect unknown attacks. Finally, our method is evaluated on two
benchmark datasets, UNSW-NB15 and CICIDS2017, under various scenarios, including different
training set label ratios and the presence of unknown attacks. Our model outperforms other models
by 3.49% and 5.69% in F1 score at labeling rates of 1% and 0.1%, respectively.
Keywords: encrypted malicious traffic detection; semi-supervised learning; multimodal features;
network security
Citation: Liu, M.; Yang, Q.; Wang, W.;
Liu, S. Semi-Supervised Encrypted
Malicious Traffic Detection Based on
Multimodal Traffic Characteristics.
Sensors 2024, 24, 6507. https://
doi.org/10.3390/s24206507
Academic Editor: Chase Wu
Received: 11 September 2024
Revised: 3 October 2024
Accepted: 9 October 2024
Published: 10 October 2024

Copyright: © 2024 by the authors.
Licensee MDPI, Basel, Switzerland.
This article is an open access article
distributed under the terms and
conditions of the Creative Commons
Attribution (CC BY) license (https://
creativecommons.org/licenses/by/
4.0/).

1. Introduction
Network traffic serves as the medium for the transmission and exchange of information
online. It contains vast amounts of valuable data. Many malicious actors intercept and alter
this traffic to achieve illegal objectives. Moreover, they use network traffic to launch attacks,
which often carry viruses, worms, and Trojans, posing significant risks to network security.
To safeguard privacy and data security, encryption technologies are widely employed in
network data transmission. The use of traffic-encryption provides a secure data-transfer
channel for legitimate users, ensuring the safety of data transmission. Nonetheless, while
traffic-encryption technologies protect privacy and communication security, they also
introduce new security risks. Some malicious actors use encrypted channels to transmit
malicious data, aiming to conceal their malicious intent and evade firewall detection, thus
creating potential risks to network security.
In the year 2023, according to a report [1] by Sonicwall, there was a substantial surge
in browser-based exploits and adware-infested websites, with increases of 297.1% and
290.5%, respectively. This highlights a worrisome pattern where encrypted pathways
are being leveraged to target weaknesses in Internet browsers and propagate spyware.
Additionally, Zscaler’s 2023 report [2] on the state of encrypted attacks indicated that
an alarming 85.9% of all detected threats were transmitted via encrypted channels. This
emphasizes the critical necessity for comprehensive traffic scrutiny to ensure security.

Sensors 2024, 24, 6507. https://doi.org/10.3390/s24206507

https://www.mdpi.com/journal/sensors

Sensors 2024, 24, x FOR PEER REVIEW

2 of 21

alarming 85.9% of all detected threats were transmitted via encrypted channels.
emphasizes the critical necessity for comprehensive traffic scrutiny to ensure secu
Figure 1 shows the top five most attacked industries and the year-over-year growth
Figure 1 shows the top five most attacked industries and the year-over-year growth rate
of attack frequency. Consequently, rapidly and accurately identifying malicious t
of attack frequency. Consequently, rapidly and accurately identifying malicious traffic
within SSL/TLS encrypted flows is of paramount importance for ensuring the securi
within SSL/TLS encrypted flows is of paramount importance for ensuring the security of
network traffic.
network traffic.
2022 year

300

2023 year

increase / decrease %
9403.7

8000
7323.1

7494.6

250
200

6956.1

150

6000

100
3978.4

4000

Change %

,
10000

Hits(million)

Sensors 2024, 24, 6507

2

50
1998.3

2000

2359.0
1827.7

2187.3

0
530.9

0

-50
Education

Healthcare

Services

Tech & Com Manufacturing

Figure 1. The top five industries globally affected by encrypted attacks from 2022 to 2023. The
horizontal axis Figure
represents
fivetop
distinct
The line chart
shows
growth
rates. from 2022 to 2023
1. The
five industries.
industries globally
affected
by their
encrypted
attacks
horizontal axis represents five distinct industries. The line chart shows their growth rates.

The core difference between identifying encrypted and unencrypted traffic lies in
the alteration of distinguishing
features
due to
encryption.
When and
the unencrypted
content of data
The core difference
between
identifying
encrypted
traffic lies i
packets is encrypted,
theoforiginal
text is transformed
into
unreadableWhen
format.
a result,
alteration
distinguishing
features due
toan
encryption.
theAs
content
of data pa
various statistical
characteristics
at bothtext
the is
packet
and flowinto
levels
be altered
post- As a re
is encrypted,
the original
transformed
an can
unreadable
format.
encryption. This
includes
metrics
like the total at
byte
count
a flow,
theflow
size levels
of individual
various
statistical
characteristics
both
the of
packet
and
can be altered
packets, and the
time
gaps
between
the
arrival
of
successive
packets.
The
alterations
in of indiv
encryption. This includes metrics like the total byte count of a flow, the size
these featurespackets,
pose three
key
challenges
to
the
methods
of
traffic
detection
in
real-world
and the time gaps between the arrival of successive packets. The alteratio
networks. (1)these
Encrypted
traffic-classification
models have
limited
expressive
and in real-w
features
pose three key challenges
to the
methods
of trafficpower,
detection
reliance on a single
feature
is
not
suitable
for
model
generalization
across
multiple
scenarios.
networks. (1) Encrypted traffic-classification models have limited expressive power
Simple statistical
features
TLS characteristics,
exclude
interaction data,
reliance
on and
a single
feature is notwhich
suitable
for inter-host
model generalization
across mu
are insufficient
for
abstracting
critical
patterns
of
advanced
attack
behaviors.
(2) There
is
scenarios. Simple statistical features and TLS characteristics, which
exclude
inter
a severe imbalance
in
the
samples.
Typically,
in
training
datasets,
the
number
of
normal
interaction data, are insufficient for abstracting critical patterns of advanced a
traffic instances
significantly
exceeds
number
of attackinsamples,
leading
to the frequent
behaviors.
(2) There
is athe
severe
imbalance
the samples.
Typically,
in training data
inaccurate detection of minority classes. This extreme class imbalance has always been a
the number of normal traffic instances significantly exceeds the number of attack sam
significant challenge for detection problems. (3) There is an inability to detect unknown
leading to the frequent inaccurate detection of minority classes. This extreme
attacks. Real-world network environments are often complex and dynamic, with new
imbalance has always been a significant challenge for detection problems. (3) There
types of network attacks continuously emerging. Consequently, it is common to encounter
inability to detect unknown attacks. Real-world network environments are often com
attack types during testing that were not present in the training data, and classifiers often
and dynamic, with new types of network attacks continuously emerging. Conseque
lack the ability to recognize these, resulting in poor detection accuracy. These challenges
it is common to encounter attack types during testing that were not present in the tra
render some traditional identification methods difficult or even inapplicable [3]. Effectively
data, and classifiers often lack the ability to recognize these, resulting in poor dete
detecting and handling malicious traffic within encrypted flows is a crucial measure for
accuracy. These challenges render some traditional identification methods difficu
defending against network attacks and safeguarding network security. Consequently, it
even inapplicable [3]. Effectively detecting and handling malicious traffic w
is imperative to seek a new method to differentiate between malicious and normal data
encrypted flows is a crucial measure for defending against network attacks
within encrypted traffic in real-world network environments.
safeguarding
security.ofConsequently,
is imperative
seek a new metho
In the last
few years, network
the application
deep learningittechnology
hastoexpanded
differentiate
between
malicious and
data within
significantly and
introduced
new approaches
for normal
the identification
of encrypted
encrypted traffic
traffic.in real-w
network
environments.
Semi-supervised detection methods, which leverage large amounts of unlabeled data, have
demonstrated the ability to enhance model accuracy with only a small amount of labeled
data in fields such as NLP and CV [4,5]. Thus, the objective of this paper is to detect

Sensors 2024, 24, 6507

3 of 21

hidden malicious traffic within encrypted flows, based on features that include network
packet sequence characteristics and packet interaction graphs, using only a small amount of
labeled normal and malicious traffic. Our study employs a semi-supervised joint training
strategy with multimodal fusion decision-making, which exhibits improved detection
capabilities for both known and unknown attacks.
Research Contributions
(1)

(2)

(3)

Extraction of Multimodal Network Traffic Features. Addressing the difficulty in
mining deep-level encrypted traffic packet features, we propose multimodal features based on sequence characteristics and heterogeneous graph structures from
the perspectives of encryption-independent and transmission interaction behaviors.
By analyzing heterogeneous features at different levels, we enhance the model’s
robustness against encrypted traffic.
Based on the characteristics of multimodal features, we have designed a unique
semi-supervised learning model that combines GRU and GCN. By jointly training the
reconstruction error of the autoencoder and the classification loss of the classifier, we
aim to improve detection effectiveness. Additionally, we propose an uncertainty estimation of classification results during the training process to better identify unknown
malicious traffic.
This paper conducts experimental analysis of our method on two intrusion-detection
datasets CICIDS2017 and UNSWNB15, examining various aspects such as different
training set label ratios, the presence of unknown attacks, and ablation studies. The
results validate the robustness of the proposed model across different scenarios, with
the integrated model outperforming any single model.

The second part of the paper investigates the fundamental representations of network
traffic and summarizes existing network traffic-detection methods. The third part provides
a detailed introduction to our semi-supervised detection method based on multimodal
traffic features. The fourth part conducts experiments on two public network-intrusion
datasets and analyzes the experimental results. The fifth part concludes the paper.
2. Related Work
2.1. Extraction of Network Traffic Characteristics
There are numerous methods for extracting network traffic features, which can be
categorized into statistical features, payload features, and other features.
Statistical feature extraction typically involves manually designed features such as the
number of packets, flow duration, and average packet size. These features are generated
by aggregating packet information within the same flow. Barradas et al. [6] proposed a
method based on random forests for detecting malicious covert tunnels in multimedia
encrypted traffic. This method extracts statistical features based on traffic behavior patterns,
including the maximum and minimum packet lengths, the duration and number of packets
at peak times, and the number of bytes sent and received for each connection. The study
collected normal and malicious multimedia traffic for both QUIC14 and TLS encryption
protocols and established a binary classification model using random forests, achieving a
90% detection accuracy for covert tunnels. However, the method has a high false positive
rate, exceeding 10%. Anderson et al. [7] presented a method for detecting botnet traffic. It
was the first to propose extracting features from TLS handshake information, including
low-security cipher suites and self-signed certificates in the certificate content. The method
tested various classification algorithms, including random forests, logistic regression, and
MLP, all of which achieved high accuracy. However, the detection accuracy for newly
discovered malicious traffic was lower than the accuracy achieved in the training set. These
methods can effectively reduce data dimensionality, making them more suitable for deep
learning tasks. However, they also lose much useful traffic information, such as packet
payload and changes in packet behavior over time.

Sensors 2024, 24, 6507

4 of 21

Payload-based feature extraction utilizes the original packet payload content, containing richer traffic information. If the payload representation can be effectively learned, it
can address a wider range of attack types. Lin et al. [8] modeled the temporal relationships
between bytes and packets in network flows, training a pre-trained model to learn a general
vector representation of encrypted traffic. For different detection scenarios, the pre-trained
model can significantly accelerate the training of detection models. Kim et al. [9] employed
machine learning methods such as K-nearest neighbors and convolutional neural networks
to evaluate traffic fingerprinting methods based on Markov chains and other methods.
It concludes that, with an appropriate classifier, the Markov chain-based fingerprinting
method outperforms other methods in detection effectiveness. Liu et al. [10] introduced a
method that constructs multilevel attributes for encrypted traffic based on the distribution
of encryption cipher suites and uses these attributes to extract fingerprint information from
encrypted traffic.
Currently, alternative methods are beginning to explore the use of sequence features
and graph representations based on traffic packets. Typically, only header information is
used to construct features, which allows the model to avoid interference from encryption
algorithms. Xie et al. [11] presented the HSTF model, a neural network detection model
based on spatiotemporal hierarchical features. The model combines CNN and LSTM and
takes input data that includes raw image data, packet-level features, and flow-level features.
This enhances the model’s ability to learn autonomously and detect HTTP-based malware,
achieving an accuracy rate of 99.4%. This method can capture more specific network
behavior information than statistical features and can handle encrypted traffic, making it an
effective supplement to methods based on statistical features. Rezaei et al. [12] suggested
that the order information between adjacent network flows is beneficial for identifying
homogeneous flows. They employ LSTM networks to uncover the sequential patterns
between network flows.
Graph-based representations are particularly adept at maintaining the topological
integrity of network packets. Shen et al. [13] introduced a novel decentralized application
fingerprinting method. This method proposes a graph structure named Traffic Interaction
Graph, which retains rich original flow characteristics. It uses Multilayer Perceptron (MLP)
for vector representation and conducts classification research. However, this method lacks
the extraction of flow statistical information and external topological structure information. Busch et al. [14] proposed representing the flow between the same endpoints of
network streams as a simple edge and implementing malware detection through graph
neural networks.
2.2. Malicious Traffic Detection
Based on the types of data covered by the training and test sets, previous detection
methods can be primarily categorized into three types.
Supervised detection methods. Experimental results indicate that TLS features, when
combined with other features, can achieve higher recall rates. et al. Lee [15] proposed
an intrusion-detection method combining a Transformer encoder and an LSTM network.
However, supervised detection methods have several limitations. Initially, the prevalence
of anomalous instances is significantly less than that of typical instances, which results in
suboptimal classification accuracy for the model. Secondly, obtaining label information
can be challenging. Thirdly, the model’s generalization cannot be guaranteed to detect
unknown attacks.
Unsupervised detection methods. Li et al. [16] presented a method for detecting
malicious TLS traffic using clustering techniques. The authors assume that normal TLS
traffic is diverse and cannot be clustered into a single class, therefore, outliers in clustering
are considered normal flows. On the other hand, traffic originating from the same family
of malicious software exhibits similar traits, allowing it to be categorized into unified or
multiple classes. Caville et al. [17] tackled the challenge of acquiring high-fidelity, labeled
network traffic data in practical settings. They introduced a self-supervised edge embed-

Sensors 2024, 24, 6507

5 of 21

ding technique that combines E-GraphSAGE with advanced graph-based deep learning
methods, thereby diminishing the need for labeled samples. This approach leverages the
graph neural network algorithm E-GraphSAGE to extract edge attributes and the graph’s
topological configuration. Additionally, it implements deep graph mutual information
maximization strategies for self-supervised learning processes. Min et al. [18] addressed
the issue of imbalanced data in traffic datasets by proposing a dataset balancing method
based on Generative Adversarial Networks (GANs). The method processes the UGR’16
dataset to balance the sample distribution, generating attack samples for underrepresented
categories using GANs and incorporating them into the original dataset. It then uses a
Multi-Layer Perceptron (MLP) neural network to experimentally validate the effectiveness
of the balanced dataset. The experimental findings demonstrated that the MLP model is
capable of yielding higher precision with the GAN-balanced dataset. However, this method
has higher requirements for machine performance and presents challenges in processing
non-numeric features such as IP addresses. Unsupervised methods are widely applied due
to their ability to adapt well to the variability of network traffic and the absence of manual
labeling. However, their accuracy is relatively low.
Semi-supervised detection methods. Semi-supervised methods are less commonly
used in network traffic anomaly detection. Sun et al. [19] characterized the semi-supervised
context by having an abundance of normal data devoid of anomalies. Their model assimilates the typical patterns exhibited by normal data and contrasts these with the test samples
against a normative model to identify potential anomalies. Additionally, Min et al. [20]
adhered to a general definition, where only a portion of the training data is labeled, and
unlabeled data is used to assist in the learning of labeled data. Wagh et al. [21] employed a
self-training method for intrusion-detection tasks. This method labels samples with high
prediction confidence from unlabeled data, adds them to the training set, and iteratively
refines the process to enhance the training effect of the classifier.
However, most of these methods do not consider the highly imbalanced distribution of normal and anomalous traffic in real-world network environments, nor do they
address the detection of unknown attack categories. Their approach is entirely dependent on the intrinsic generalization abilities of the classification model, which retains
considerable constraints.
3. Method
3.1. Preliminaries
3.1.1. Problem Statement
In real-world network environments, it is challenging to collect pure traffic data that is
free from noise. Training a detection model with only normal or malicious samples limits
its learning capabilities. Therefore, we hypothesize the research scenario: the training
dataset comprises a limited set of labeled benign and malicious instances, supplemented
by an ample quantity of unlabeled normal samples. The labeled malicious samples may
not encompass all types of malicious traffic, indicating that only a subset of malicious
categories is known.
3.1.2. Notations
Given N data streams, x1 , x2 , x3 , . . . , x N ∈ Xtrain , where M samples have label information, M ≪ N. ( x 1 , y1 ) , ( x 2 , y2 ) , ( x 3 , y3 ) , . . . , ( x M , y M ) ∈ Xk × Y, and Xk ⊆ Xtrain ,
Y = {0, 1}. We assume that when y = 0, the sample belongs to normal traffic, and when
y = 1, the sample belongs to malicious traffic. We propose a novel traffic-detection method
ψ based on multimodal traffic features, which include network traffic sequence features Ts
and graph features Tg . In the test set, we are given T stream data, x̂1 , x̂2 , x̂3 , . . . , x̂ T ∈ Xtest .
We ultimately aim to use the model ψ to provide an anomaly score x̂i = ψ( x̂i ) for each
stream to assess its likelihood of being malicious traffic.

and graph features 𝑇𝑔 . In the test set, we are given T stream data, 𝑥̂1 , 𝑥̂2 , 𝑥̂3 , … , 𝑥̂𝑇 ∈ 𝑋𝑡
We ultimately aim to use the model 𝜓 to provide an anomaly 𝑠𝑐𝑜𝑟𝑒𝑥̂𝑖 = 𝜓(𝑥̂𝑖 ) for ea
stream to assess its likelihood of being malicious traffic.
Sensors 2024, 24, 6507

6 of 21

3.2. Framework

Given
that statistical features of network traffic can result in significant loss
3.2. Framework
information
from
original
data,of
wenetwork
propose
a multimodal
monitori
Given
thatthe
statistical
features
traffic
can result insemi-supervised
significant loss of inmodel
for
detecting
encrypted
malicious
traffic.
This
model
is
based
on
traffic
formation from the original data, we propose a multimodal semi-supervised monitoring sequen
model
forheterogeneous
detecting encrypted
malicious
traffic. This
model
is based on
sequencedetailed
analysis
and
graph
embedding.
The
framework
oftraffic
the model,
analysis
and
heterogeneous
graph
embedding.
The
framework
of
the
model,
detailed
Figure 2, encompasses several key components: data preprocessing, featureinextracti
Figure 2, encompasses several key components: data preprocessing, feature extraction,
semi-supervised
learning, and multimodal decision fusion.
semi-supervised learning, and multimodal decision fusion.

Figure
2. Our
approach
the identification
of encrypted
malicious tra
Figure
2. Oursemi-supervised
semi-supervised approach
for thefor
identification
of encrypted malicious
traffic utilizing
features
from multiple
modalities.
utilizing
features
from multiple
modalities.
3.3. Data Preprocessing

3.3. Data The
Preprocessing
granularity of network traffic detection addressed in this study is focused on the

flow level,
which typically
involves
the collection
of data
packets that
share
a common
set
The
granularity
of network
traffic
detection
addressed
in this
study
is focused
on
characteristics,
includinginvolves
the sourcethe
IP, collection
source port, of
destination
IP, andthat
destination
flow of
level,
which typically
data packets
share aport.
common
Since general attacks or abnormal behaviors are often manifested within flows rather than
of characteristics, including the source IP, source port, destination IP, and destinati
individual packets, this aggregation approach can significantly reduce resource overhead.
port. Compared
Since general
attacks orflows,
abnormal
behaviors
areofoften
within flows rath
to unidirectional
from the
perspective
traffic manifested
interaction, bidirectional
than flows
individual
packets,
thisareaggregation
approach
can significantly
with richer
information
chosen as the detection
granularity.
Therefore, wereduce
catego- resou
rize
the
packets
in
PCAP
files
into
different
session
flows
based
on
the
five-tuple,
which
overhead. Compared to unidirectional flows, from the perspective of traffic
interacti
facilitates subsequent labeling and processing. The segmentation process utilizes the tool
bidirectional flows with richer information are chosen as the detection granulari
pkt2flow [22], using source address, destination address, source port, and destination
Therefore,
categorize
the packets
PCAP
files
different
session
flows
port as we
classification
information
to splitinthe
packets
intointo
bidirectional
session
flows,
with based
the five-tuple,
which
facilitates
subsequent
labeling
and
processing.
The
segmentati
each session flow saved to a separate PCAP file. Subsequently, invalid packets are
removed,
and dirty
each session
flow after
segmentation,
ARP packets,
process
utilizes
the data
toolwithin
pkt2flow
[22], using
source
address,including
destination
address, sou
and retransmission
packets, are cleared
to minimizeto
their
impact
the
port, DNS
andpackets,
destination
port as classification
information
split
theon packets
in
detection results.
bidirectional session flows, with each session flow saved to a separate PCAP fi
Subsequently,
invalid
packets
areand
removed,
3.4. Multimodal
Feature
Extraction
Encoding and dirty data within each session flow af
3.4.1.
Sequence
Feature
segmentation, including ARP packets, DNS packets, and retransmission packets,
use only the
header
portion
each
traffic data
packet for feature extraction. The
cleared toWe
minimize
their
impact
onofthe
detection
results.

features extracted for each packet are listed in Table 1. In total, we extract five types of
packet features, which effectively reflect the unique properties of traffic data packets within
3.4. Multimodal Feature Extraction and Encoding
the sequence.
3.4.1. Sequence
Among Feature
these, the target port number does not inherently possess a measure of magnitude and is not suitable for direct treatment as a continuous feature. Consequently, we
We use only the header portion of each traffic data packet for feature extraction. T
consider encoding it as a discrete value. The range of port number features is extensive, pofeatures
extracted
packet
are Therefore,
listed in using
TableOne-Hot
1. In total,
weisextract
five types
tentially
spanningfor
theeach
interval
[0, 65536].
Encoding
impractical.
packet
features,
effectively
reflect
the for
unique
properties
traffic
data pack
As a
result, wewhich
have resorted
to binary
encoding
all features
except foroftime
intervals
and
packet
payload
sizes.
We
also
utilize
the
size
of
the
packet
payload
and
the
size
of
the
within the sequence.
packet header as features. Since the header size can indicate the type of multi-layer protocol
to some extent, we consider encoding it as a discrete value. The numerical value of the
payload size is more meaningful, so we directly use numerical encoding for it. Compared to
traditional statistical features, our method based on packet sequence modeling can capture

Sensors 2024, 24, 6507

7 of 21

more detailed patterns of traffic behavior, effectively leveraging the temporal attributes
of packets. Additionally, due to the low computational cost of feature extraction, this
approach offers significant advantages in terms of time efficiency.
Table 1. Overview of traffic sequence characteristics.
Feature

Coded Format

Destination Port
Time Interval
Packet Header Size (Byte)
Packet Payload Size (Byte)
TCP Window Size

Binary coding
Numerical coding
Binary coding
Numerical coding
Binary coding

We utilize an autoencoder model based on Gated Recurrent Units (GRU) to extract
and reconstruct features from unlabeled sequence data. GRUs are effective in encoding
variable-length input sequences into fixed-length vectors. Let si represent the current input
sample sequence, si = (e1 , e2 , . . . , en ) and n denote the length of sequence si . Consequently,
the relationship for the hidden state of the first GRU layer can be expressed as shown in
Equation (1).
(
(1)

0, t = 0
ht =
(1)
(1)
GRU ht−1 , et , 1 ≤ t ≤ n
ht−1 represents the hidden state from the previous moment. The GRU () function
denotes the transition relationship between hidden states at adjacent moments. We employ
a stacked multi-layer GRU architecture for encoding, with a total of H layers. For layers
where i > 1, the input to the ith GRU unit is generated by the output of the previous layer
at the same time step. Since the GRU uses the hidden state G for information transfer
between adjacent moments and directly for the output of the GRU unit at that moment, the
relationship for the i-th layer GRU can be expressed as Equation (2).


(i )
(i )
( i −1)
ht = GRU ht−1 , ht
, 1 ≤ t ≤ n, i > 1
(2)
Essentially, we utilize the output of the hidden state from the last layer as a fixedlength vector representation z that we obtain from the encoding process, which can be
(H)

denoted as z = hn .
Similarly, the decoder is composed of several layers of GRU units and a dense layer,
configured to calculate the discrepancy in the reconstruction between the generated sequence and the original input. Within the decoder, the ultimate output z derived from the
encoder serves as the initial input, as demonstrated in Equation (3).


(i )
(i )
ĥt = GRU ĥt−1 , z , 1 ≤ t ≤ n
(3)
At the final stage of the decoder, we employ a fully connected layer to generate the
seq
reconstructed sequence, which is then employed to calculate the reconstruction loss Lrec , as
illustrated in Equation (4).


N

n

Lrec = ∑i=1 ∑t=i 1 l et′i , eit
seq

(4)

l represents the distance function between vectors, and we use the mean squared error
for this calculation. Figure 3 depicts the process of extracting traffic sequence features and
calculating reconstruction loss.

features and calculating reconstruction loss.
𝑠𝑒𝑞

𝑛

𝑖
′𝑖 𝑖
𝐿𝑟𝑒𝑐 = ∑𝑁
𝑖=1 ∑𝑡=1 𝑙(𝑒𝑡 , 𝑒𝑡 )

Sensors 2024, 24, 6507

(4)

𝑙 represents the distance function between vectors, and we use the mean squared
error for this calculation. Figure 3 depicts the process of extracting traffic sequence
8 of 21
features and calculating reconstruction loss.

Figure 3. Illustration of traffic sequence feature extraction.

3.4.2. Graph Feature
To avoid
feature
overlap
between
traffic
flows of different categories and versions,
Figure
3. Illustration
Illustration
of traffic
traffic
sequence
feature
extraction.
Figure
3.
of
sequence
feature
extraction.
we describe the traffic features from another perspective as a supplement to flow sequence
3.4.2. Graph Feature
features.
This topological
feature can capture the connection behaviors between different
3.4.2. Graph
Feature
To avoid feature overlap between traffic flows of different categories and versions, we
host applications.
Moreover,
the low-dimensional
feature vectors
generated
through
To avoid
feature
overlap
between
traffic
flows of as
different
categories
and sequence
versions,
describe
the traffic
features
from
another
perspective
a supplement
to flow
graph
embedding
technology
are
independent
of the statistical
features
of encrypted
flow
we
describe
thetopological
traffic
features
from
another
perspective
as a supplement
to flow
sequence
features.
This
feature
can
capture
the connection
behaviors between
different
data
and
possess
a
certain
level
of
anti-interference
capability.
Building
upon
the
work
features.
This
topological
feature
can
capture
the
connection
behaviors
between
different
host applications. Moreover, the low-dimensional feature vectors generated through graph
host
Moreover,
the traffic
low-dimensional
feature
vectors
generatedflow
through
[13],
weapplications.
further
optimized
the
graph
byofembedding
packet
embedding
technology
are independent
ofinteraction
the statistical
features
encrypted
data size,
graph
embedding
technology
are packet
independent
of the statistical
encrypted
flow
direction,
order,
and
graph-level
information
into
thefeatures
heterogeneous
neural
and possess
a certain
level of anti-interference
capability.
Building
uponof
the
workgraph
[13],
we
data
and
possess
a
certain
level
of
anti-interference
capability.
Building
upon
the
work
further We
optimized
interaction
graph
embedding
direction,
order,
network.
definethe
thetraffic
packet
length as
the by
vertices
of thepacket
graphsize,
structure
and
arrange
[13],
we furtherpacket
optimized
traffic
interaction
graph
by neural
embedding
packet
size,
andin
graph-level
information
intoTo
the
heterogeneous
We
them
sequence within
the the
graph.
represent
the graph
direction
ofnetwork.
packets
indefine
the
graph
direction,
order,
and
graph-level
packet
information
into
the
heterogeneous
graph neural
the
packet
length
as
the
vertices
of
the
graph
structure
and
arrange
them
in
sequence
within
structure, we use positive and negative signs to denote downstream and upstream
network.
thethe
packet
length
the vertices
of the structure,
graph structure
arrange
the graph.We
To define
represent
direction
of as
packets
in the graph
we use and
positive
and
packets,
respectively.
Subsequently,
the
entire
flow
is
divided
into
multiple
burst
data
them
in sequence
withindownstream
the graph. and
To represent
the direction
of packets
in the graph
negative
signs to denote
upstream packets,
respectively.
Subsequently,
the
packets
basedison
thepositive
packet-transmission
direction.
First,
we
connect the
within
structure,
use
and negative
signs
to denote
and vertices
upstream
entire flowwe
divided
into multiple
burst data
packets
baseddownstream
on the packet-transmission
thepackets,
same
group
of
burst
data
packets
with
edges.
Unlike
[13],
we
use
a
different
type
of
Subsequently,
thewithin
entirethe
flow
is divided
multiple
burst data
direction.respectively.
First, we connect
the vertices
same
group ofinto
burst
data packets
with
edge
to connect
different
of type
burstof
data
indifferent
sequence.
4within
provides
a
packets
based [13],
on
the
direction.
First, we
connectgroups
theFigure
vertices
edges.
Unlike
wepacket-transmission
usegroups
a different
edge packets
to connect
of burst
data
the
same
group
of
burst
data
packets
with
edges.
Unlike
[13],
we
use
a
different
type
of
detailed
illustration
of
the
heterogeneous
traffic
burst
graph.
Different
colored
lines
in
the
packets in sequence. Figure 4 provides a detailed illustration of the heterogeneous traffic
edge
to
connect
different
groups
ofinburst
data packets
in two
sequence.
burstrepresent
graph.
Different
colored
lines
the figure
represent
types ofFigure
edges.4 provides a
figure
two
types
of edges.
detailed illustration of the heterogeneous traffic burst graph. Different colored lines in the
figure represent two types of edges.

Figure
4. Illustrationofoftraffic
trafficgraph
graph feature
feature construction.
The
transfer
of packets
between
clientclient
and and
Figure
4. Illustration
construction.
The
transfer
of packets
between
Figure
4. transformed
Illustration ofinto
traffic
graph feature graph
construction.
The transfer of packets between client and
server
is
a
heterogeneous
representation.
server
is transformed into a heterogeneous graph representation.
server is transformed into a heterogeneous graph representation.

We employ a heterogeneous graph encoder that combines different relationships
within the heterogeneous graph to learn high-quality representations of network traffic. The
strength of a heterogeneous graph is its capacity to encapsulate diverse types of relationship
data, effectively converting high-dimensional, sparsely distributed topological graph data
into concise vector forms. This transformation aims to preserve the structural and semantic
details of the nodes to the greatest extent possible. As depicted in Figure 5, we deploy a
GCN to distill the representation for each node within the graph. The convolutional layer
operation in GCN can be formalized as Equation (5).

Sensors 2024, 24, 6507

within the heterogeneous graph to learn high-quality representations of network traffic.
The strength of a heterogeneous graph is its capacity to encapsulate diverse types of
relationship data, effectively converting high-dimensional, sparsely distributed
topological graph data into concise vector forms. This transformation aims to preserve the
9 of 21
structural and semantic details of the nodes to the greatest extent possible. As depicted
in
Figure 5, we deploy a GCN to distill the representation for each node within the graph.
The convolutional layer operation in GCN
can be formalized as Equation (5).
∼−1 ∼ ∼−1
2
H1( j) W ( j) )
−
̃ 2 𝐴̃𝐷
̃ −2 𝐻(𝑗) 𝑊 (𝑗) )
= 𝜎(𝐷

H ( l +1) = σ ( D

∼

∼

𝐻

(𝑙+1)

2

AD
1

(5)

(5)

where, ̃D = D + IN , ̃ A = A + IN , IN represents the identity matrix. D represents the
where,
𝐷 = 𝐷 + 𝐼𝑁 , 𝐴 = 𝐴 + 𝐼𝑁 , 𝐼𝑁 represents the identity matrix. 𝐷 represents the
degree matrix of the nodes, which indicates the degree of each node. A represents the
degree matrix of the (nodes,
which indicates the degree of each node. A represents the
adjacency matrix. H(𝑗)j) represents the feature matrix of the j-th layer. W ( j) represents
the
(𝑗)
adjacency
matrix.
𝐻
represents
the
feature
matrix
of
the
j-th
layer.
𝑊
represents
learned weights. σ denotes the non-linear activation function. After encoding through the the
learned
weights.𝜎
denotes
the non-linear
activationisfunction.
encoding
through the
GCN layer,
the final
embedded
feature representation
given by After
Equation
(6).
GCN layer, the final embedded feature representation is given by Equation (6).
∼ − 21 ∼ ∼ − 12
∼ − 21 ∼ ∼ − 12
1
1
1
1 (0)
A−D2 ̃ ̃·−σ2( D ̃A−D
XW
)(0)
W (1) )(1)
Z = GCN ( GCN ( X, A)) = so f tmax ( D ̃
−
2 ̃̃ 2

𝑍 = 𝐺𝐶𝑁(𝐺𝐶𝑁(𝑋, 𝐴)) = 𝑠𝑜𝑓𝑡𝑚𝑎𝑥(𝐷 𝐴𝐷

⋅ 𝜎(𝐷 𝐴𝐷 𝑋𝑊

)𝑊

)

(6)

(6)

Thedecoder
decoderpart
part of
of the
typically
computes
the reconstructed
The
the graph
graphconvolution
convolution
typically
computes
the reconstructed
adjacency
matrix
Â
through
the
use
of
an
inner
product,
as
indicated
in
Equation
(7). (7).
̂
adjacency matrix 𝐴 through the use of an inner product, as indicated in Equation




T 𝑇
Â =𝐴̂σ= ZZ
=) sigmoid
ZZ T 𝑇 )
(7) (7)
𝜎(𝑍𝑍
= 𝑠𝑖𝑔𝑚𝑜𝑖𝑑(𝑍𝑍

Throughout
thetraining
training
phase,
the objective
of the
to reduce the
Throughout the
phase,
the objective
of the decoder
is todecoder
reduce theisdiscrepancy
discrepancy
original
and theversion,
reconstructed
version,the
thereby
between thebetween
original the
graph
datasetgraph
and thedataset
reconstructed
thereby enabling
enabling
theof acquisition
robust feature
representations.
Commonly,error
the isgraph
acquisition
robust featureof
representations.
Commonly,
the graph reconstruction
quantified using
the mean
squared error
(MSE)
the primary
metric
the overall
graph
reconstruction
error
is quantified
using
the as
mean
squared
errorfor(MSE)
as the
primary
reconstruction
loss, asgraph
indicated
in Equation (8).
metric
for the overall
reconstruction
loss, as indicated in Equation (8).

N 𝑁
gra 𝑔𝑟𝑎 =
𝑀𝑆𝐸(𝐴,
Lrec 𝐿=
MSE
A, Â 𝐴̂)
𝑟𝑒𝑐∑i =∑
0 𝑖=0

(8)

(8)

Figure
Frameworkof
ofgraph
graph encoder
Figure
5. 5.
Framework
encodernetwork.
network.

3.5. Semi-Supervised Co-Training

3.5. Semi-Supervised Co-Training

Given that the training dataset Xtrain comprises a limited set of labeled instances and
Given thatamount
the training
dataset
𝑋𝑡𝑟𝑎𝑖𝑛
comprises
a limited set
of labeled instances
a substantial
of unlabeled
ones,
traditional
semi-supervised
classification
methods and
a often
substantial
unlabeled
ones,training
traditional
semi-supervised
classification
utilize allamount
unlabeledofdata
for pre-training,
an autoencoder
network, and
learning
reconstruction
error
loss
to
better
learn
the
original
features
and
reduce
dimensionality.
methods often utilize all unlabeled data for pre-training, training an autoencoder
Subsequently,
one can continue
to fine-tune
theloss
original
encoder
using
labeled
datafeatures
to train and
network,
and learning
reconstruction
error
to better
learn
the
original
the
final
classifier.
However,
we
found
that
the
method
of
initializing
the
classifier
weights
reduce dimensionality. Subsequently, one can continue to fine-tune the original encoder
through pre-training often encounters performance limitations. Therefore, we design a
using labeled data to train the final classifier. However, we found that the method of
joint training approach for the autoencoder and the classifier, simultaneously learning
initializing
the classifier weights through pre-training often encounters performance
reconstruction error and classification error to update the model weights. In this context,
limitations.
Therefore,
we
design a joint
training
approach
forperformance
the autoencoder
and the
the autoencoder
acts as
a regularizer,
which
often leads
to better
than the
classifier,
simultaneously
learning
reconstruction
and
classification
error6. to
update
general separate
model. The
specific
training phaseerror
process
is depicted
in Figure
The
model can be divided into the training phase and the detection phase.

Sensors 2024, 24, 6507

the model weights. In this context, the autoencoder acts as a regularizer, which often leads
to better performance than the general separate model. The specific training phase process
10 detection
of 21
is depicted in Figure 6. The model can be divided into the training phase and the
phase.

Figure
Descriptionof
ofour
our semi-supervised
semi-supervised co-training
framework.
TheThe
process
primarily
consists
Figure
6. 6.
Description
co-training
framework.
process
primarily
consists
of two
components:the
thetraining
training phase
phase.
of two
components:
phaseand
andthe
thedetection
detection
phase.

The classifier module first utilizes the output of the encoder as the supervised learning
The
classifier module
first utilizes the output of the encoder as the supervised
∼
s i , which,
input for
labeled
data
after
being encoded by the encoding layer, yields a fixedlearning
input
for
labeled
data
∼
∼𝑠̃ 𝑖 , which, after being encoded by the encoding layer,
o i into a fullỹ connected
length
vector o i . We
input𝑜̃the
layer and a softmax layer
to
yields
a fixed-length
vector
a softmax
𝑖 . We input the 𝑜
𝑖 into a fully connected layer and
∼
p
train
a
binary
classifier,
with
the
output
representing
the
predicted
probability
of
the
i
layer to train a binary classifier, with the output representing the predicted probability
𝑝̃𝑖
classification result.
of the classification result.
To counteract the challenge of a significant imbalance between the positive and negTo counteract the challenge of a significant imbalance between the positive and
ative samples in the training data, we employ the focal loss [23], function in place of the
negative
samples
in the training
we employ
the focaldiminishes
loss [23], the
function
of
standard
cross-entropy
loss. Thisdata,
specialized
loss function
impactinofplace
a
themultitude
standardofcross-entropy
loss.
This
specialized
loss
function
diminishes
the
impact
of
a
straightforward negative examples during training, thereby boosting the
multitude
of straightforward
negativesamples.
examples
training,
thereby
boosting the
model’s capacity
to learn from complex
Theduring
computation
of this
loss is depicted
in Equation
(9). to learn fromcomplex
model’s
capacity
samples.
The
computation
of
this
loss
is depicted



∼ 
∼
∼ γ
in Equation (9).
FL p i = −α 1 − p i · log p i
(9)

𝐹𝐿(𝑝
̃𝑖 )respectively
= −𝛼(1 − 𝑝control
̃𝑖 )𝛾 ⋅ 𝑙𝑜𝑔(𝑝
̃𝑖 ) of sample imbalance and (9)
α and γ are weighting factors
that
issues
the difficulty of recognition. We have adopted the value of 2 for γ as recommended in the
𝛼 𝑎𝑛𝑑 𝛾 are weighting factors that respectively control issues of sample imbalance
focal loss [23], and we have used the default value of 1 for α.
and theFor
difficulty
of recognition.
have adopted
value of 2design
for γ aasconfidencerecommended
the detection
of unknownWe
malicious
traffic, wethe
concurrently
in estimation
the focal loss
[23],
and
we
have
used
the
default
value
of
1
for
α.
method during the training of the classifier. When faced with unknown samples,
the detection
malicious
traffic,
werepresent
concurrently
design
a confidencetheFor
probability
output of
of aunknown
typical classifier
cannot
directly
the model’s
confidence
in the classification
Even
a sample does
not classifier.
belong to the
same faced
distribution
the
estimation
method result.
during
theif training
of the
When
withasunknown
training
set
of
the
classifier,
the
classifier
often
provides
a
very
high
probability
output,
even
samples, the probability output of a typical classifier cannot directly represent the model’s
for an incorrect
Therefore,
weEven
introduced
an uncertainty-estimation
confidence
in theprediction.
classification
result.
if a sample
does not belong method
to the same
∼
in
the
classification
module
to
calculate
the
confidence
estimate
for
samples
in
test high
c
i
distribution as the training set of the classifier, the classifier
often provides the
a very
set. The architecture primarily comprises several dense layers and a sigmoid activation
probability output, even for an incorrect prediction. Therefore, we introduced an
function. The confidence score is bounded within the interval [0, 1], where a higher score
uncertainty-estimation method in the classification module to calculate the confidence 𝑐̃𝑖
indicates higher certainty. Facing unknown anomalies in the test set often results in lower
estimate
for samples
in help
the test
set. The
architecture
comprisesanomalies.
several dense
confidence,
which will
improve
the model’s
abilityprimarily
to detect unknown
layers
and
a
sigmoid
activation
function.
The
confidence
score
is
bounded
within the
To incorporate confidence into the model training, we adjust the classification prediction
interval
[0, 1], where
a higher
score indicates
higher certainty. Facing unknown anomalies
probabilities
as indicated
in Equation
(10).
in the test set often results in lower
confidence,
which will help improve the model’s

∼ ∼1 ∼

ability to detect unknown anomalies.
Tocincorporate
∼′
i · p y = 0 confidence into the model training,
p i = ∼ ∼1  i i ∼  ∼
(10)
we adjust the classification prediction
indicated
in Equation (10).
 c i · probabilities
p + 1 − c i yas =
1
i

i
1
c̃i ⋅p̃ ỹ i =0
∼′
’
{ 1 i sample
p i represents the probability thatp̃ai =predicted
is malicious, and similarly, the (10)
̃′i ⋅p̃ i +(1-c̃i ) ỹ i =1
∼c
probability that a sample is benign is 1 − p i . Intuitively, when the predicted confidence is
high,
use the original
predictionthat
to calculate
the loss,
whileis
when
the confidence
is low, the
𝑝̃𝑖′ we
represents
the probability
a predicted
sample
malicious,
and similarly,
the training
provides
a hint,
i.e., we is
calculate
loss using when
the true
label.
probability
that
a sample
is benign
1 − 𝑝̃𝑖′ .the
Intuitively,
the
predicted confidence is

the training provides a hint, i.e., we calculate the loss using the true label.
During the training phase, a joint training process is achieved through alternating
labeled and unlabeled data. The ultimate loss function is a combination of the
classification loss and the reconstruction loss, as shown in Equation (11).
11 of 21

Sensors 2024, 24, 6507

(11)

𝐿 = 𝐿𝑟𝑒𝑐 + 𝜇𝐿𝑐𝑙𝑠

the to
training
phase,
a joint training
process
is achieved through
where During
𝜇 is used
balance
the classification
loss
and reconstruction
loss. alternating
labeled
and6b
unlabeled
data. the
The anomaly-detection
ultimate loss function stage,
is a combination
of the
classification
Figure
represents
where we
combine
three loss
loss
and
the
reconstruction
loss,
as
shown
in
Equation
(11).
functions that are meaningful for detecting unknown malicious traffic samples to evaluate
anomalies. For each test sample 𝑥̂𝑖 ,Lwe
its anomaly score 𝑠𝑐𝑜𝑟𝑒𝑥̂𝑖 , as shown
in
= Lcalculate
(11)
rec + µLcls
Equation (12).
where µ is used to balance the classification
loss𝑖 and reconstruction
loss.
𝑖
𝑖
𝑖
𝑠𝑐𝑜𝑟𝑒
=
𝜆
⋅
𝑠𝑐𝑜𝑟𝑒
⋅
𝑠𝑐𝑜𝑟𝑒
−
𝜃
⋅
𝑠𝑐𝑜𝑟𝑒
+ 𝑠𝑐𝑜𝑟𝑒
̂
𝑥
𝑟𝑒𝑐 functions (12)
𝑐𝑙𝑠
𝑐𝑜𝑛𝑓
𝑐𝑜𝑛𝑓
Figure 6b represents𝑖 the anomaly-detection stage, where we combine
three loss
that
areaim
meaningful
detecting unknown
malicious
to evaluate anomalies.
We
to jointlyfordetermine
the anomaly
scoretraffic
basedsamples
on the classification
results from
For each test sample x̂i , we calculate its anomaly score scorex̂i , as shown in Equation (12).

supervised learning and the reconstruction error from unsupervised learning. We use the
i
i a sample i as anomalous
i
product of the probability
classifying
and the (12)
model’s
score x̂i = λ ·of
score
cls · scorecon f − θ · scorecon f + scorerec
confidence as the core influence of the classifier, with 𝜆 being used to adjust the weights.
We aim we
to jointly
determine
the anomaly
score based aonsample
the classification
results from
Additionally,
consider
the possibility
of classifying
as an unknown
malicious
supervised
learning
and
the
reconstruction
error
from
unsupervised
learning.
We
use
type when the confidence is low. Therefore, we also use a penalty term 𝜃 to the
assign a
product
of the probability
a sample
anomalous
and theand
model’s
confidence
higher
anomaly
estimateof classifying
to samples
with aslow
confidence
sum
it with the
as the core influence of the classifier, with λ being used to adjust the weights. Additionally,
reconstruction error to obtain the final anomaly score. In summary, for samples with high
we consider the possibility of classifying a sample as an unknown malicious type when
confidence
in the classification results, the model tends to rely on supervised learning
the confidence is low. Therefore, we also use a penalty term θ to assign a higher anomaly
outcomes
judgment.
forand
samples
lowreconstruction
classificationerror
confidence,
estimate for
to samples
withConversely,
low confidence
sum it with
with the
to obtain there
is the
a strong
likelihood
that
they
belong
to
unknown
categories,
and
we
prefer to use
final anomaly score. In summary, for samples with high confidence in the classification
reconstruction
error
for determination.
results, the model
tends
to rely on supervised learning outcomes for judgment. Conversely,
for samples with low classification confidence, there is a strong likelihood that they belong
unknown categories,
3.6.toMultimodal
Fusion and we prefer to use reconstruction error for determination.

this section,
we describe the detection framework based on multimodal data. For
3.6.InMultimodal
Fusion
each flow,
we
can
types offramework
features:based
traffic
sequence data.
features
In this section, weobtain
describetwo
the detection
on multimodal
For and
heterogeneous
graph
embedding
features.
aim
to adopt
an appropriate
multimodal
each flow, we can
obtain
two types of
features:We
traffic
sequence
features
and heterogeneous
strategy
to
effectively
combine
the
multimodal
features
of
network
traffic.
To
graph embedding features. We aim to adopt an appropriate multimodal strategy to effectively
effecutilize
two distinct
feature representations
of sequences
and topological
graphs,
tivelythe
combine
the multimodal
features of network
traffic. To effectively
utilize the
two and
distinct
feature
representations
of
sequences
and
topological
graphs,
and
to
integrate
with
to integrate with the semi-supervised joint training model proposed by us, we will
the semi-supervised
jointdetection
training model
proposed
by us,
will construct afusion
multimodal
construct
a multimodal
framework
using
a we
post-processing
approach,
detection
framework
using
a
post-processing
fusion
approach,
which
is
also
known
as
which is also known as decision fusion.
decision fusion.
As shown in Figure 7, we train a semi-supervised model using an unlabeled dataset
As shown in Figure 7, we train a semi-supervised model using an unlabeled dataset
and
a labeled dataset. The sequence features 𝑠𝑖 and
the heterogeneous graph features 𝑔𝑖
and a labeled dataset. The sequence features si and
the heterogeneous graph features gi are
areused
used
to
train
these
two
models,
respectively.
For
the test
combine the
to train these two models, respectively. For the test sample,
wesample,
combine we
the score
total
score
by the
twotomodels
measure
the that
probability
that
the sample
belongs to
output
by the two
models
measuretothe
probability
the sample
belongs
to malicious
total output
malicious
traffic.
The parameter
is used
adjustofthe
of the two models.
traffic. The
parameter
τ is used to𝜏adjust
the to
weights
theweights
two models.
= score
⋅ score
total
graph
scorescore
score
τ+· τscore
seq +seq
total =
graph

{

,

,

} =1

{( ,

)} =1

{( ,

)} =1
Figure 7. Overall discriminator model based on multimodal data.

(13) (13)

Sensors 2024, 24, x FOR PEER REVIEW

12 of 21

Figure 7. Overall discriminator model based on multimodal data.
Sensors 2024, 24, 6507

12 of 21

4. Experiment
4.1. Dataset
4. Experiment
To substantiate the robustness of our suggested model in various settings, we
4.1. Dataset
performed experiments utilizing two publicly available datasets, namely UNSW-NB15
robustness of our suggested model in various settings, we per[24] To
andsubstantiate
CICIDS2017the
[25].
formed
experiments
utilizing
two
publicly
available
datasets,
namelynetwork
UNSW-NB15
UNSW-NB15 is a network
attack
dataset
that includes
genuine
traffic [24]
and
and
CICIDS2017
[25].
composite malicious communication behaviors within a real network environment. The
UNSW-NB15
is a network
attack
genuine
and
records
are primarily
categorized
intodataset
benignthat
andincludes
malicious
types,network
with thetraffic
malicious
composite malicious communication behaviors within a real network environment. The
records further divided into nine categories. The original network data in the dataset was
records are primarily categorized into benign and malicious types, with the malicious
created by the Cyber Range Lab, utilizing the IXIA PerfectStorm tool
records further divided into nine categories. The original network data in the dataset was
(https://research.unsw.edu.au/projects/unsw-nb15-dataset, accessed on 8 October 2024).
created by the Cyber Range Lab, utilizing the IXIA PerfectStorm tool (https://research.
The quantities of each category are listed in Table 2 and Figure 8. In the UNSW-NB15
unsw.edu.au/projects/unsw-nb15-dataset, accessed on 8 October 2024). The quantities of
dataset, the majority of the data is normal traffic, with Generic and Exploits attack types
each category are listed in Table 2 and Figure 8. In the UNSW-NB15 dataset, the majority
also accounting for a significant proportion. The execution complexity of various attack
of the data is normal traffic, with Generic and Exploits attack types also accounting for a
behaviors, the potential benefits, and their occurrence frequency result in a highly skewed
significant proportion. The execution complexity of various attack behaviors, the potential
distribution of attack types within the network traffic data. This imbalance presents a
benefits, and their occurrence frequency result in a highly skewed distribution of attack
considerable challenge for the detection of anomalous network traffic patterns.
types within the network traffic data. This imbalance presents a considerable challenge for
the detection of anomalous network traffic patterns.
Table 2. The composition of the UNSW-NB15 dataset.

Table
2. The composition of the UNSW-NB15 dataset.
Classes
Quantity

Normal
Classes
Reconnaissance
Normal
Worms
Reconnaissance
Dos
Worms
Generic
Dos
Generic
Analysis
Analysis
Fuzzers
Fuzzers
Shellcode
Shellcode
Backdoor
Backdoor
Exploits
Exploits
Total
Total

2,218,761
Quantity
13,987
2,218,761
174
13,987
16,353
174
215,481
16,353
215,481
2677
2677
24,246
24,246
1511
1511
2329
2329
44,525
44,525
2,540,044
2,540,044

0.1%

0.1%
0.1%

87.4%

0.6%

1%

1.8%
0.6%

8.5%

Normal
Dos
Shellcode

Generic
Reconnaissance
Worms

Exploits
Analysis

Fuzzers
Backdoor

Figure8.8. Overall
Overall category
categorydistribution
distributionof
ofthe
theUNSW-NB15.
UNSW-NB15.
Figure

CICIDS2017 collects five days of simulated real-world traffic generated by the BProfile system, encompassing a variety of network services and attack methods, including
DoS, DDoS, and Port Scanning, among others. Consequently, the dataset contains both
benign and various malicious traffic, widely used for the classification of encrypted traffic.

Sensors 2024, 24, 6507

CICIDS2017 collects five days of simulated real-world traffic generated by th
Profile system, encompassing a variety of network services and attack methods, inclu
13 of 21contains
DoS, DDoS, and Port Scanning, among others. Consequently, the dataset
benign and various malicious traffic, widely used for the classification of encrypted tra
This paper filters out 10 types of attacks, with the specific categories and their quant
in types
Table of
3. attacks,
Figure 9with
presents
a pie chart
that graphically
depicts the catego
This paper filterslisted
out 10
the specific
categories
and their quantities
within thea dataset.
listed in Table 3.distribution
Figure 9 presents
pie chart that graphically depicts the categorical
distribution within the dataset.
Table 3. The composition of the CICIDS2017 dataset.

Table 3. The composition of the CICIDS2017 dataset.

Classes
Normal
Classes
Dos Hulk
Normal
Port Scan
Dos Hulk
DDos
Port Scan
DDos
Dos GoldenEye
Dos GoldenEye FTP-Patator
FTP-Patator
SSH-Patator
SSH-Patator
Dos slowloris Dos slowloris
Dos SlowhttptestDos Slowhttptest
Bot
Bot
Web Attack
Web Attack
Total
Total

Quantity
2,271,320
230,124
158,804
128,025
10,293
7935
5897
5796
5499
1956
1507
2,827,156

Quantity
2,271,320
230,124
158,804
128,025
10,293
7935
5897
5796
5499
1956
1507
2,827,156

0.1%
0.1%

0.2%

0.4%
1.5%

80.3%

0.2%

4.5%

0.3%
0.2%

5.6%
8.1%

Normal
Dos GoldenEye
Dos Slowhttptest

Dos Hulk
FTP-Patator
Bot

Port Scan
SSH-Patator
Web Attack

DDos
Dos slowloris

Figure 9. distribution
Overall category
distribution
of the CICIDS2017.
Figure 9. Overall category
of the
CICIDS2017.

4.2. Environment4.2.
andEnvironment
Parameters Setting
and Parameters Setting

The experimentsThe
were
conductedwere
on a conducted
Windows 10
with Python
3.7 with
and Pyexperiments
onsystem
a Windows
10 system
Python 3.7
Torch 1.10. During
the preprocessing
the traffic data,
theofopen-source
tool pkt2flow
PyTorch
1.10. Duringstage
the of
preprocessing
stage
the traffic data,
the open-source
is used to convert
the original
PCAP
files into
theinto
stages
of model
pkt2flow
is used
to convert
thesession
originalflows.
PCAPIn
files
session
flows.conIn the stage
struction and training,
model was
built
and trained
using
PyTorch,
with
optimization
model the
construction
and
training,
the model
was
built and
trained
using PyTorch,
performed
on for
an acceleration.
NVIDIA GeForce
RTX
4080 for
acceleration.
For
performed on anoptimization
NVIDIA GeForce
RTX 4080
For the
sequential
feature
ensequential
feature
encoder,
the GRU model
canwe
easily
perform
reconstruction. Thus
coder, the GRU model
can easily
perform
reconstruction.
Thus,
equate
the classification
equate the classification
the
reconstruction
settingthe
μ RGAT
to 1. For the g
loss with the reconstruction
loss, settingloss
µ towith
1. For
the
graph featureloss,
encoder,
feature
encoder,
the
RGAT
model
experiences
a
higher
reconstruction
loss during
model experiences a higher reconstruction loss during the initial epochs of iteration. To
initial
epochs
of
iteration.
To
balance
the
joint
training
loss,
we
set
μ
to
2 for the g
balance the joint training loss, we set µ to 2 for the graph structure branch. To standardize
structure
branch.
To
standardize
the
units,
we
manually
set
λ
to
1
and
θ
to 0.05. Tab
the units, we manually set λ to 1 and θ to 0.05. Table 4 presents the parameter values for
presents
the parameter
the network structure attributes chosen in our mod
the network structure
attributes
chosenvalues
in ourfor
model.

Sensors 2024, 24, 6507

14 of 21

Table 4. The main parameters setting.
Parameters

Default Value

Epoch
Learning rate
Optimizer
Batch size
Layer of GRU
Layer of GCN
α, γ
µ
λ, θ
τ

200
0.0005
Adam
64
3
2
(1, 2)
1, 2
(1, 0.05)
1

4.3. Evaluation and Validation Metrics
This section utilizes four key performance indicators for assessment: accuracy, precision, recall, and the F1 score. Accuracy, the most frequently used metric, indicates the
ratio of correctly identified instances to the total instances. Precision is defined as the ratio
of true positive instances to the total number of instances labeled as positive. Recall, on
the other hand, is the ratio of true positive instances to the total actual positive instances.
The F1 score is a metric that provides a balance between precision and recall. To reduce the
variability from a single trial, this study conducts the experiment five times, each with a
random split of the dataset into training and testing subsets. The final experimental result
is determined by averaging the results from these five iterations.
We design three sets of experiments to evaluate the performance of various methods:
(1)

Performance of the model under different label ratios.

During the semi-supervised training phase, different quantities of labeled samples
were used to train each model to observe the performance under varying degrees of
labeled samples.
(2)

Performance in detecting unknown malicious traffic.

For the two datasets, the experimental scenario was uniformly set to 1% label ratio.
Two types of malicious traffic are selected from each dataset as unknown categories for
experiments, and corresponding ROC curves were plotted to observe the detection results.
(3)

The role of each component in our model.

To analyze the actual effects of each component in the model, including confidence
estimation, reconstruction error, and the effect of multimodal fusion. Experiments were
conducted under a known label ratio of 1% in the IDS2017 dataset.
To more thoroughly assess the efficacy of our proposed model, we select various
baselines for comparison. An introduction to the selected methods is as follows.

•
•

•

•

•

CNN+LSTM Model [11]: This model combines convolutional neural networks and
long short-term memory to integrate spatial and temporal features of traffic data.
E-GraphSAGE Model [18]: This model is the first to introduce graph neural networks
into the field of anomaly traffic detection, focusing on the aggregation and update of
graph information on edge features.
E-ResGAT Model [26]: This model replaces the backbone network with Graph Attention Networks on the basis of E-GraphSAGE, introduces attention mechanisms into
graph neural networks, calculates the mutual importance of each node to its adjacent
nodes, and participates in the aggregation of information on the graph.
BYOL-NIDS Model [27]: This model implements self-supervised learning for anomaly
traffic-intrusion detection, introduces the BYOL model into the field of anomaly traffic
detection and specifically performs data augmentation.
RUIDS Model [28]: This model implements an anomaly traffic-detection scheme based
on self-supervised masked time context using the Transform.

Sensors 2024, 24, 6507

15 of 21

•

•

VGAE Model [29]: This model uses variational graph auto-encoders to achieve selfsupervised capture and learning of feature representations of traffic graphs for traffic classification.
CNN+AE [30]: Composed of a pre-trained CNN model and an autoencoder model for
classification. The CNN model automatically extracts deep features from the payload
of network traffic, and the AE model judges normal and malicious traffic through the
reconstruction error of deep features.

4.4. Detection Analysis on Known Samples and Varying Label Ratios
In the experiment with known sample verification, both the training and test data
consist of the same malicious family. The objective of this experiment is to verify whether
different detection models can effectively distinguish between malicious and normal traffic.
Table 5 first presents the detection results of our proposed model and other baseline models
on the complete labeled training set.
On the UNSW-NB15 dataset, our model achieves the Acc, Pre, Rec, and F1 rates by
99.51%, 99.46%, 99.36% and 99.41% respectively. It can be observed that on the IDS2017
dataset, our model still achieves the best classification performance. All four metrics have
exceeded 99%. This demonstrates that our model has good generalization capabilities.
The E-ResGAT model, which employs an attention mechanism to focus on the channel
dimensions of traffic features, yields good results.
Table 5. Comparison of detection performance on UNSW-NB15 and CICIDS2017.
UNSW-NB15
Model

CICIDS2017

Acc

Pre

Rec

F1

Acc

Pre

Rec

F1

1D-CNN
LSTM
CNN+LSTM
E-GraphSAGE
E-ResGAT
BYOL-NIDS
RUIDS
VGAE
CNN+AE

96.61
95.10
97.95
98.93
99.40
97.05
98.91
98.63
96.96

96.55
92.94
97.03
98.64
99.50
97.26
98.80
98.80
97.19

96.51
95.17
97.48
98.18
98.90
98.72
98.86
97.63
97.22

96.53
91.83
96.80
98.41
99.20
96.54
98.77
99.38
97.17

95.16
96.78
98.02
99.09
99.84
96.70
99.09
97.20
98.64

91.63
96.07
98.05
99.06
99.65
95.24
99.06
97.26
98.62

95.39
96.56
98.20
99.29
99.43
95.74
99.69
97.40
98.59

89.79
95.83
98.25
98.94
99.76
94.99
98.75
97.19
98.63

Our

99.51

99.46

99.36

99.41

99.99

99.98

99.98

99.98

In real network environments, malicious data is far less common than benign data.
To better reflect this characteristic in dataset validation. We set up training sets with
different proportions of labeled malicious traffic. For each of the two datasets, we will
evaluate whether the model can still achieve good performance with a very small amount
of labeled data. We will conduct experiments with label proportions in the training set
at 0.5%, 1%, 5%, 10%, and 20%. The F1 score on the CICIDS2017 dataset, as shown in
Table 6, indicates that the method proposed by us consistently achieves nearly the best
performance across varying label ratios. When the percentage of labeled training samples
exceeds 10%, all methods exhibit similar performance to the previous experiment. The
performance of all other models, except for ours, has significantly decreased to varying
degrees when the label ratio is low. Specifically, when the labeling rate is reduced to 5%,
our method outperforms current baseline methods by more than 2.69%. As the labeling
rate decreases to 1% and 0.5%, supervised learning models [11,18,26] tend to focus more
on extracting features from normal traffic. The insufficient extraction of malicious traffic
features often leads to a significant decrease in the F1 score. When compared to selfsupervised learning methods [27–29], our approach demonstrates significant advantages,
outperforming the best models by 3.49% and 5.69% in F1 score, respectively. We attribute
this to our joint training method and confidence-estimation design, which more effectively
utilizes unlabeled data to enhance the model’s robustness.

Table 6. Comparative experiment on different label ratios on CICIDS2017.
Table 6. Comparative experiment on different label ratios on CICIDS2017.

1D-CNN
LSTM
1D-CNN
CNN+LSTM
LSTM
CNN+LSTM
E-GraphSAGE
E-GraphSAGE
E-ResGAT
E-ResGAT
BYOL-NIDS
BYOL-NIDS
RUIDS
RUIDS
VGAE
VGAE
CNN+AE
CNN+AE
Our
Our

0.5%
67.81
0.5%
70.95
67.81
78.18
70.95
78.18
80.78
80.78
82.02
82.02
85.29
85.29
92.33
92.33
87.05
87.05
79.59
79.59
98.02
98.02

1%
81.09
1%
79.23
81.09
82.71
79.23
82.71
92.72
92.72
94.10
94.10
90.73
90.73
95.16
95.16
93.72
93.72
84.71
84.71
98.65
98.65

5%
88.61
5%
89.08
88.61
90.16
89.08
90.16
94.86
94.86
95.74
95.74
92.72
92.72
96.71
96.71
96.44
96.44
93.16
93.16
99.40
99.40

10%
90.55
10%
92.32
90.55
92.80
92.32
92.80
95.77
95.77
96.79
96.79
95.09
95.09
97.68
97.68
96.81
96.81
94.66
94.66
99.40
99.40

20%
94.36
20%
96.09
94.36
97.81
96.09
97.81
98.56
98.56
99.13
99.13
96.07
96.07
98.84
98.84
97.15
97.15
98.41
98.41
99.73
99.73

Figure
Figure 10
10 illustrates
illustrates the
the accuracy
accuracy rates
rates of
of our
our model
model during
during each
each epoch
epoch of
of training
training on
on
CICIDS2017, with labeled samples comprising 0.5%, 1%, 5%, and 10% of the dataset. The
performance of our model is slightly influenced by the number of labeled samples
samples in the
early stages. As the
the number
numberofofiterations
iterationsincreases,
increases,the
the
accuracy
method
rapidly
accuracy
of of
ourour
method
rapidly
imimproves,
compensating
forinsufficient
the insufficient
number
of training
150
proves, compensating
for the
number
of training
samples.samples.
After 150 After
iterations,
iterations,
model
trained
with 1%
labeledhas
samples
hasthe
achieved
the same performance
the model the
trained
with
1% labeled
samples
achieved
same performance
as the one
as
the one
with samples.
10% labeled
samples.
both
methods
still exhibit
a
trained
withtrained
10% labeled
However,
bothHowever,
methods still
exhibit
a performance
gap
performance
gapmodel
compared
to the
model
20% labeled samples.
compared to the
trained
with
20% trained
labeled with
samples.
1.00
0.95
0.90
Accuracy

Sensors 2024, 24, 6507

supervised learning methods [27–29], our approach demonstrates significant advantages,
outperforming the best models by 3.49% and 5.69% in F1 score, respectively. We attribute
this to our joint training method and confidence-estimation design, which more effectively
utilizes unlabeled data to enhance the model’s robustness.
16 of 21

0.85
0.80
20%
10%
5%
1%
0.5%

0.75
0.70
0

50

100
Epoch

150

200

Figure
Figure 10.
10. Accuracy
Accuracy curves
curves of
of our
our model
model during
during training
training with
with different
different label
label ratios.
ratios.

4.5. Detection
Detection Analysis
Analysis on
on Unknown
Unknown Attacks
Attacks
4.5.
In this
this part,
part, we
we primarily
evaluate the
the model’s
model’s detection
detection effectiveness
effectiveness for
for attacks
attacks of
of
In
primarily evaluate
unknown
categories.
In
the
experimental
process,
we
start
with
the
initial
data
partition
that
unknown categories. In the experimental process, we start with the initial data partition
excludes
unknown
attacks.
We remove
all samples
corresponding
to the attack
categories
that
excludes
unknown
attacks.
We remove
all samples
corresponding
to the
attack
from
the
labeled
training
data,
while
still
retaining
these
samples
in
the
unlabeled
categories from the labeled training data, while still retaining these samples indata
the
and test sets.
Equally,
wesets.
have
standardized
thestandardized
experimentalthe
setup
to a 1% labeled
unlabeled
data
and test
Equally,
we have
experimental
setup data
to a
ratio. We conduct a comparative study of our method with four baseline models that
have shown good performance in known attack detection. Furthermore, to mitigate the
impact of training instability on the assessment, we performed five repetitions for each
experimental scenario and calculated the average results.
In selecting samples from unknown categories, we aim to train the detector using
common and low-risk attack traffic to identify those categories that are high-risk and

In selecting
selecting samples
samples from
from unknown
unknown categories,
categories, we
we aim
aim to
to train
train the
the detector
detector usi
usi
In
common and
and low-risk
low-risk attack
attack traffic
traffic to
to identify
identify those
those categories
categories that
that are
are high-risk
high-risk aa
common
highly stealthy.
stealthy. Consequently,
Consequently, for
for the
the UNSW-NB15
UNSW-NB15 dataset,
dataset, we
we have
have selected
selected Backdo
Backdo
highly
and Exploits
Exploits attack
attack traffic
traffic for
for the
the test
test set.
set. For
For the
the CICIDS.2017
CICIDS.2017 dataset,
dataset, we
we have
have chos
chos
and
17 of 21
PortScan and
and DoS
DoS Hulk
Hulk attack
attack traffic
traffic to
to be
be included
included in
in the
the test
test set.
set.
PortScan
Figures 11
11 and
and 12
12 correspond
correspond to
to the
the ROC
ROC curves
curves for
for three
three scenarios
scenarios in
in the
the UNS
UNS
Figures
NB15
and
CICIDS2017
datasets,
respectively.
It
is
observable
that
the
detection
efficacy
stealthy. Consequently,
the UNSW-NB15
we have
Backdoorefficacy
NB15highly
and CICIDS2017
datasets,for
respectively.
It isdataset,
observable
thatselected
the detection
and
Exploits
attack
traffic
for
the
test
set.
For
the
CICIDS.2017
dataset,
we
have
chosen attac
methods
relying
on
classifiers
markedly
diminishes
in
the
presence
of
unknown
attac
methods relying on classifiers markedly diminishes in the presence of unknown
PortScan
and
DoS
Hulk
attack
traffic
to
be
included
in
the
test
set.
With the
the exception
exception of
of our
our method,
method, the
the other
other methods
methods have
have weak
weak capabilities
capabilities in
in identifyi
identifyi
With
Figures 11 and 12 correspond to the ROC curves for three scenarios in the UNSWunknown
attacks.
Methods
[18,26]
based Iton
on
supervised
learning
have
high
rate
unknown
attacks.
Methods
[18,26]
based
supervised
have
aa high
rate
NB15 and
CICIDS2017
datasets,
respectively.
is observable
that learning
the detection
efficacy
of
misclassification,
confirming
that
they are
are
insufficient
in characterizing
characterizing
traffic
interacti
methods relying
on classifiersthat
markedly
diminishes
in the in
presence
of unknowntraffic
attacks.
misclassification,
confirming
they
insufficient
interacti
With the
ofthe
our detection
method, theeffectiveness
other methods of
have
weak capabilities in
identifying
behaviors.
Inexception
contrast,
the
detection
effectiveness
of
semi-supervised
methods
experien
behaviors.
In
contrast,
semi-supervised
methods
experien
unknown
attacks.
Methods
[18,26]
based
on
supervised
learning
have
a
high
rate
of
only aa slight
slight reduction.
reduction. However,
However, our
our method,
method, which
which is
is based
based on
on multimodal
multimodal
featu
only
featu
misclassification, confirming that they are insufficient in characterizing traffic interaction
extraction
and
semi-supervised
training,
shows
no
significant
change.
The
embeddi
extraction
andInsemi-supervised
training,
shows
no significant
change.
The embeddi
behaviors.
contrast, the detection
effectiveness
of semi-supervised
methods
experiences
features
calculated
by
our
method
are
not
confined
to
the
characteristics
of aa sin
sin
features
by our
methodourare
not confined
to the
characteristics
of
only calculated
a slight reduction.
However,
method,
which is based
on multimodal
feature
network
session,
but rather
rather represent
represent
the
multidimensional
features
of network
network traffi
traffi
extraction
and but
semi-supervised
training,the
shows
no significant change.
The embedding
network
session,
multidimensional
features
of
features
calculated
by
our
method
are
not
confined
to
the
characteristics
of
a
single
network
which can
can uncover
uncover more
more classification
classification features
features for
for both
both benign
benign and
and malicious
malicious traffi
traffi
which
session, but rather represent the multidimensional features of network traffic, which can
Therefore, the
the method
method introduced
introduced in this
this chapter
chapter is better
better suited
suited to
to detect unknown
unknown atta
atta
Therefore,
uncover more
classification featuresinfor
both benign is
and malicious
traffic.detect
Therefore, the
traffic.
traffic.
method introduced in this chapter is better suited to detect unknown attack traffic.
1.0
1.0

1.0
1.0

0.8
0.8

0.8
0.8

0.8
0.8

0.6
0.6
0.4
0.4
Our(AUC=0.9940)
Our(AUC=0.9940)
E-ResGAT(AUC=0.9922)
E-ResGAT(AUC=0.9922)
E-GraphSAGE(AUC=0.9874)
E-GraphSAGE(AUC=0.9874)
RUIDS(AUC=0.9813)
RUIDS(AUC=0.9813)
VGAE(AUC=0.9900)
VGAE(AUC=0.9900)

0.2
0.2
0.0
0.0
0.0
0.0

0.2
0.2

0.4
0.4

0.6
0.6

False Positive
Positive Rate
Rate
False

0.8
0.8

0.6
0.6
0.4
0.4
Our(AUC=0.9636)
Our(AUC=0.9636)
E-ResGAT(AUC=0.9387)
E-ResGAT(AUC=0.9387)
E-GraphSAGE(AUC=0.9284)
E-GraphSAGE(AUC=0.9284)
RUIDS(AUC=0.9461)
RUIDS(AUC=0.9461)
VGAE(AUC=0.9203)
VGAE(AUC=0.9203)

0.2
0.2
0.0
0.0
0.0
0.0

1.0
1.0

0.2
0.2

0.4
0.4

0.6
0.6

False Positive
Positive Rate
Rate
False

(a)
(a)

0.8
0.8

1.0
1.0

True
Rate
PositiveRate
TruePositive

1.0
1.0

True
Rate
PositiveRate
TruePositive

True
Rate
PositiveRate
TruePositive

Sensors 2024, 24, 6507

0.6
0.6
0.4
0.4
Our(AUC=0.9709)
Our(AUC=0.9709)
E-ResGAT(AUC=0.9400)
E-ResGAT(AUC=0.9400)
E-GraphSAGE(AUC=0.9367)
E-GraphSAGE(AUC=0.9367)
RUIDS(AUC=0.9480)
RUIDS(AUC=0.9480)
VGAE(AUC=0.9442)
VGAE(AUC=0.9442)

0.2
0.2
0.0
0.0
0.0
0.0

0.2
0.2

0.4
0.4

0.6
0.6

False Positive
Positive Rate
Rate
False

(b)
(b)

0.8
0.8

1.0
1.0

(c)
(c)

1.0
1.0

1.0
1.0

0.8
0.8

0.8
0.8

0.8
0.8

0.6
0.6
0.4
0.4
Our(AUC=0.9898)
Our(AUC=0.9898)
E-ResGAT(AUC=0.9830)
E-ResGAT(AUC=0.9830)
E-GraphSAGE(AUC=0.9610)
E-GraphSAGE(AUC=0.9610)
RUIDS(AUC=0.9796)
RUIDS(AUC=0.9796)
VGAE(AUC=0.9762)
VGAE(AUC=0.9762)

0.2
0.2
0.0
0.0
0.0
0.0

0.2
0.2

0.4
0.4

0.6
0.6

False Positive
Positive Rate
Rate
False
(a)
(a)

0.8
0.8

1.0
1.0

0.6
0.6
0.4
0.4
Our(AUC=0.9758)
Our(AUC=0.9758)
E-ResGAT(AUC=0.9564)
E-ResGAT(AUC=0.9564)
E-GraphSAGE(AUC=0.8739)
E-GraphSAGE(AUC=0.8739)
RUIDS(AUC=0.9463)
RUIDS(AUC=0.9463)
VGAE(AUC=0.9450)
VGAE(AUC=0.9450)

0.2
0.2
0.0
0.0
0.0
0.0

0.2
0.2

0.4
0.4

0.6
0.6

False Positive
Positive Rate
Rate
False
(b)
(b)

0.8
0.8

1.0
1.0

True
Rate
PositiveRate
TruePositive

1.0
1.0

True
Rate
PositiveRate
TruePositive

True
Rate
PositiveRate
TruePositive

Figure
11. 11.
Evaluation
ofunknown
unknown
attack
detection
on the
the UNSW-NB15
UNSW-NB15
dataset.
(a) With
With
Figure
11.
Evaluation
of
unknown
detection
on
dataset.
(a)
Figure
Evaluation of
attackattack
detection
on the UNSW-NB15
dataset. (a) Without
unknown
unknown
attacks.
(b)
With unknown
unknown
attacks as
as
backdoor.
(c) attacks
With unknown
unknown
attacks as
as exploits.
exploits.
attacks.
(b) With
unknown
attacks as backdoor.
(c) backdoor.
With unknown
as exploits. attacks
unknown
attacks.
(b)
With
attacks
(c)
With

0.6
0.6
0.4
0.4
Our(AUC=0.9645)
Our(AUC=0.9645)
E-ResGAT(AUC=0.8637)
E-ResGAT(AUC=0.8637)
E-GraphSAGE(AUC=0.8376)
E-GraphSAGE(AUC=0.8376)
RUIDS(AUC=0.9206)
RUIDS(AUC=0.9206)
VGAE(AUC=0.9283)
VGAE(AUC=0.9283)

0.2
0.2
0.0
0.0
0.0
0.0

0.2
0.2

0.4
0.4

0.6
0.6

False Positive
Positive Rate
Rate
False
(c)
(c)

0.8
0.8

1.0
1.0

Figure
Evaluation of
attackattack
detection
on the CICIDS2017
(a) Without
unknown
Figure
12. 12.
Evaluation
ofunknown
unknown
attack
detection
on the
the dataset.
CICIDS2017
dataset.
(a) With
With
Figure
12.
Evaluation
of
unknown
detection
on
CICIDS2017
dataset.
(a)
attacks.
(b)
With
unknown
attacks
as
DoS
Hulk.
(c)
With
unknown
attacks
as
PortScan.
unknown
attacks.
(b)
With
unknown
attacks
as
DoS
Hulk.
(c)
With
unknown
attacks
as
PortScan
unknown attacks. (b) With unknown attacks as DoS Hulk. (c) With unknown attacks as PortScan

4.6. Ablation Experiment

4.6. Ablation
Ablation
Experiment
4.6.
Experiment
4.6.1. Effect
Analysis of Model Components
Finally,
we analyze
the practical
effects of each component of our model. This includes
4.6.1. Effect
Effect
Analysis
of Model
Model
Components
4.6.1.
Analysis
of
Components
an analysis of the effectiveness of confidence estimation, reconstruction error, different

Finally,
weloss
analyze
theandpractical
practical
effects
of For
each
component
of our
our model.
model. T
T
Finally,
we
analyze
the
effects
of
each
of
classification
functions,
single-modal
models.
thecomponent
following experiments,
we
includes
anexperimental
analysis of
of
the effectiveness
effectiveness
of
confidence
estimation, reconstruction
reconstruction err
err
includes
an
analysis
the
confidence
estimation,
set the
scenario
to have a label of
ratio
of 1%.
The ablation study results are presented in Table 7. Compared to the original model
proposed in this paper, the detection performance of all variants, which have had one

module removed, has decreased to varying degrees. This indicates that each module plays
a positive role in the detection of anomalous traffic. The removal of the GCN component
results in a significant decrease in model performance, indicating that graph neural
networks are more effective at extracting correlations between features, thereby detecting
18 of 21
more subtle attacks. It can be observed that the F1 score significantly decreases when the
focal loss function is substituted by cross entropy loss, indicating that the model may have
reduced
ability tohas
detect
covertto
classes.
moduleitsremoved,
decreased
varying degrees. This indicates that each module

Sensors 2024, 24, 6507

plays a positive role in the detection of anomalous traffic. The removal of the GCN
Table
7. Ablation
study
components
on the
UNSW-NB15
and CICIDS2017
component
results
inof
a key
significant
decrease
in model
performance,
indicating dataset.
that graph
neural networks are more effective at extracting correlations between features, thereby
Dataset
Acc
Rec decreases
F1
detecting more Method
subtle attacks. It can be observed that the
F1 scorePre
significantly
w/ofunction
confidence
estimation
95.91
95.28
95.36
95.32
when the focal loss
is substituted
by cross entropy
loss, indicating
that
the model
may have reduced
ability to detecterror
covert classes. 94.84
w/oits
reconstruction
93.67
93.22
93.44

w/o sequence feature
91.29
91.40
90.25
90.82
Table 7. Ablation study of key components on the UNSW-NB15 and CICIDS2017 dataset.
UNSW-NB15
w/o graph feature
90.89
90.46
90.99
90.72
Dataset
Method
Acc
Pre
Rec
F1
w/cross-entropy loss
94.96
94.28
93.33
93.80
w/o
confidence
estimation
95.91
95.28
95.36
95.32
default (all)
97.63
98.37
94.23
96.26
w/o reconstruction error
94.84
93.67
93.22
93.44
w/o
confidence
estimation
97.42
97.36
96.74
w/o sequence feature
91.29
91.40
90.25
90.82 97.05
UNSW-NB15
w/oreconstruction
graph feature
90.46
90.99
90.72 94.89
w/o
error 90.89
96.55
95.23
94.55
w/cross-entropy loss
94.96
94.28
93.33
93.80
w/o sequence feature
94.63
93.74
93.56
97.63
98.37
94.23
96.26 93.65
CICIDS2017 default (all)
w/o
feature
94.19
93.80
93.93
w/ograph
confidence
estimation
97.42
97.36
96.74
97.05 93.86
w/o
reconstruction
error
96.55
95.23
94.55
94.89
w/cross-entropy loss
96.32
96.95
95.29
96.11
w/o sequence feature
94.63
93.74
93.56
93.65
CICIDS2017 default (all)
98.79
98.68
98.63
w/o graph feature
94.19
93.80
93.93
93.86 98.65
w/cross-entropy loss
default (all)

96.32
98.79

4.6.2. Parameter Sensitivity Analysis

96.95
98.68

95.29
98.63

96.11
98.65

We conducted a parameter comparison between the number of GRU layers and GCN
4.6.2. Parameter Sensitivity Analysis
layers in semi-supervised learning, examining the impact of varying network layer depths
We conducted a parameter comparison between the number of GRU layers and
on GCN
model
accuracy,
as shown in learning,
Figure 13.
By stacking
layers in
graph
neurallayer
network,
layers
in semi-supervised
examining
the impact
of the
varying
network
thedepths
modeloncan
capture
higher-order
neighbor
feature
information,
leading
to
a more
model accuracy, as shown in Figure 13. By stacking layers in the graph neural
precise
representation.
an excessive
number
ofinformation,
layers can leading
result to
ina overnetwork,
the model canHowever,
capture higher-order
neighbor
feature
smoothing,
where
the featuresHowever,
of different
nodes become
homogenized,
making
it difficult
more precise
representation.
an excessive
number
of layers can result
in overwhere
the features
of different
become homogenized,
making itperformance.
difficult
to smoothing,
distinguish
between
nodes
and nodes
negatively
impacting model
to distinguish the
between
nodesaccuracy
and negatively
impacting
model
performance.
Consequently,
Consequently,
model’s
initially
increases
with
the addition
of layers but
the
model’s
accuracy
initially
increases
with
the
addition
of
layers
but
eventually
decreases.
eventually decreases. According to the experimental data, configuring the model in this
According to the experimental data, configuring the model in this study with 3 GRU
study with 3 GRU layers and 2 GCN layers strikes a balance that efficiently captures the
layers and 2 GCN layers strikes a balance that efficiently captures the characteristics of
characteristics
of network flows.
network flows.
95

95

UNSW-NB15
CICIDS2017

F1

90

F1

90

UNSW-NB15
CICIDS2017

85

85

80

80
1

2

3

4

5

6

7

1

2

3

4

Layer

Layer

(a)

(b)

5

6

7

Figure 13. F1 Scores for models with different layer configurations. (a) GRU layers. (b) GCN layers.

Additionally, we assess the importance of the branches for the fusion of sequential and
graph features. We assign three different values to τ to combine them, and the classification
results are shown in Table 8. The results indicate that different settings yield satisfactory
outcomes, demonstrating that both sequential features and graph structures are equally

Sensors 2024, 24, 6507

19 of 21

important for the identification of malicious traffic. Therefore, in our experiment, we assign
equal decision weights to both modalities.
Table 8. Ablation study of key parameter on the UNSW-NB15 and CICIDS2017 dataset.
τ

Acc

Pre

Rec

F1

UNSW-NB15

0.5
1
5

97.67
97.63
97.46

97.70
98.37
96.84

94.66
94.23
94.57

96.16
96.26
95.69

CICIDS2017

0.5
1
5

98.67
98.79
97.84

98.85
98.68
98.13

98.58
98.63
98.40

98.71
98.65
98.26

5. Conclusions
To address the challenges in malicious traffic detection, such as the difficulty in labeling samples and capturing attack traffic, as well as the limitations of existing deep
learning methods in uncovering subtle malicious activities and low detection accuracy,
this paper introduces a multimodal approach for detecting malicious traffic. We characterize encrypted traffic by leveraging both sequential and graph structural features of the
traffic flow. Initially, we segment the traffic based on session granularity and then train a
multimodal deep learning model that integrates these two types of features, providing a
holistic description of malicious traffic behavior. The co-training of confidence loss and
classification loss effectively mitigates the issue of insufficient sample information mining
common in existing semi-supervised training methods, enhancing the robustness of the
classifier. Experimental results on multiple datasets demonstrate the effectiveness of the
proposed fusion method for malicious network traffic detection, particularly outperforming benchmark methods in scenarios with scarce labeled samples and the discovery of
unknown malicious categories.
To advance the research on encrypted malicious traffic detection, future efforts will
concentrate on the following areas: (1) Enhancing the scale of samples. It is well recognized
that the quantity of samples significantly impacts deep learning models; hence, we will
explore the use of contrastive representation learning ang generative adversarial networks
to augment the sample size. (2) Improving the interpretability of traffic features. While
deep learning is powerful in its end-to-end data learning capabilities, its interpretability
has been a persistent challenge. Poor interpretability can limit the practical application of
traffic features.
Author Contributions: Conceptualization, M.L.; Methodology, M.L., Q.Y., W.W. and S.L.; Validation,
M.L.; Formal analysis, M.L., Q.Y. and S.L.; Writing—original draft, M.L.; Writing—review & editing,
Q.Y. and S.L.; Visualization, W.W. All authors have read and agreed to the published version of
the manuscript.
Funding: This research was funded by National Key Research and Development Program of China
(Grant number: 2019QY1300) and Science & Technology Commission Foundation Strengthening
Project (Grant number: 2019-JCJQ-ZD113).
Institutional Review Board Statement: Not applicable.
Informed Consent Statement: Not applicable.
Data Availability Statement: The data presented in this study are openly available in [24,25].
Conflicts of Interest: The authors declare no conflict of interest.

Sensors 2024, 24, 6507

20 of 21

References
1.
2.
3.
4.
5.
6.
7.

8.
9.

10.
11.
12.
13.
14.

15.

16.
17.
18.
19.

20.

21.
22.
23.
24.

25.
26.

2023 SonicWall Cyber Threat Report. Available online: https://www.sonicwall.com/resources/white-papers/mid-year-2023
-sonicwall-cyber-threat-report (accessed on 31 August 2024).
Zscaler ThreatLabz 2023 State of Encrypted Attacks Report. Available online: https://www.zscaler.com/resources/2023
-threatlabz-state-of-encrypted-attacks-report (accessed on 31 August 2024).
Ji, I.H.; Lee, J.H.; Kang, M.J.; Park, W.J.; Jeon, S.H.; Seo, J.T. Artificial intelligence-based anomaly detection technology over
encrypted traffic: A systematic literature review. Sensors 2024, 24, 898. [CrossRef] [PubMed]
Wu, M. Commonsense knowledge powered heterogeneous graph attention networks for semi-supervised short text classification.
Expert Syst. Appl. 2023, 232, 120800. [CrossRef]
Yang, X.; Song, Z.; King, I.; Xu, Z. A survey on deep semi-supervised learning. IEEE Trans. Knowl. Data Eng. 2022, 35, 8934–8954.
[CrossRef]
Barradas, D.; Santos, N.; Rodrigues, L. Effective detection of multimedia protocol tunneling using machine learning. In
Proceedings of the 27th USENIX Security Symposium (USENIX Security 18), Baltimore, MD, USA, 15–17 August 2018; pp. 169–185.
Anderson, B.; McGrew, D. Machine learning for encrypted malware traffic classification: Accounting for noisy labels and
non-stationarity. In Proceedings of the 23rd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining,
Halifax, NS, Canada, 13–17 August 2017; pp. 1723–1732.
Lin, X.; Xiong, G.; Gou, G.; Li, Z.; Shi, J.; Yu, J. Et-bert: A contextualized datagram representation with pre-training transformers
for encrypted traffic classification. In Proceedings of the ACM Web Conference 2022, Lyon, France, 25–29 April 2022; pp. 633–642.
Kim, H.; Kim, M.; Ha, J.; Roh, H. Revisiting TLS-encrypted traffic fingerprinting methods for malware family classification. In
Proceedings of the 2022 13th International Conference on Information and Communication Technology Convergence (ICTC),
Jeju Island, Republic of Korea, 19–21 October 2022; pp. 1273–1278.
Liu, C.; Xiong, G.; Gou, G.; Yiu, S.M.; Li, Z.; Tian, Z. Classifying encrypted traffic using adaptive fingerprints with multi-level
attributes. World Wide Web 2021, 24, 2071–2097. [CrossRef]
Xie, J.; Li, S.; Yun, X.; Zhang, Y.; Chang, P. Hstf-model: An http-based trojan detection model via the hierarchical spatio-temporal
features of traffics. Comput. Secur. 2020, 96, 101923. [CrossRef]
Rezaei, S.; Kroencke, B.; Liu, X. Large-scale mobile app identification using deep learning. IEEE Access 2019, 8, 348–362. [CrossRef]
Shen, M.; Zhang, J.; Zhu, L.; Xu, K.; Du, X. Accurate decentralized application identification via encrypted traffic analysis using
graph neural networks. IEEE Trans. Inf. Forensics Secur. 2021, 16, 2367–2380. [CrossRef]
Busch, J.; Kocheturov, A.; Tresp, V.; Seidl, T. NF-GNN: Network flow graph neural networks for malware detection and
classification. In Proceedings of the 33rd International Conference on Scientific and Statistical Database Management, Tampa, FL,
USA, 6–7 July 2021; pp. 121–132.
Lee, W.; Xi, S. Encrypted malware traffic detection using TLS features and random forest. In Proceedings of the International
Conference on Computational & Experimental Engineering and Sciences, Phuket, Thailand, 6–10 January; Springer International
Publishing: Cham, Switzerland, 2021; pp. 85–100.
Li, W.; Zhang, X.Y.; Bao, H.; Shi, H.; Wang, Q. ProGraph: Robust network traffic identification with graph propagation. IEEE/ACM
Trans. Netw. 2022, 31, 1385–1399. [CrossRef]
Caville, E.; Lo, W.W.; Layeghy, S.; Portmann, M. Anomal-E: A self-supervised network intrusion detection system based on graph
neural networks. Knowl. Based Syst. 2022, 258, 110030. [CrossRef]
Min, B.; Yoo, J.; Kim, S.; Shin, D.; Shin, D. Network anomaly detection using memory-augmented deep autoencoder. IEEE Access
2021, 9, 104695–104706. [CrossRef]
Sun, Y.; Guo, L.; Li, Y.; Xu, L.; Wang, Y. Semi-supervised deep learning for network anomaly detection. In Algorithms and
Architectures for Parallel Processing, Proceedings of the 19th International Conference, ICA3PP 2019, Melbourne, VIC, Australia, 9–11
December 2019; Proceedings, Part II 19; Springer International Publishing: Cham, Switzerland, 2020; pp. 383–390.
Min, E.; Long, J.; Liu, Q.; Cui, J.; Cai, Z.; Ma, J. Su-ids: A semi-supervised and unsupervised framework for network intrusion
detection. In Cloud Computing and Security, Proceedings of the 4th International Conference, ICCCS 2018, Haikou, China, 8–10 June 2018;
Revised Selected Papers, Part III 4; Springer International Publishing: Cham, Switzerland, 2018; pp. 322–334.
Wagh, S.K.; Kolhe, S.R. Effective intrusion detection system using semi-supervised learning. In Proceedings of the 2014
International Conference on Data Mining and Intelligent Computing (ICDMIC), Delhi, India, 5–6 September 2014; pp. 1–5.
Pkt2flow. Available online: https://github.com/caesar0301/pkt2flow (accessed on 21 February 2024).
Lin, T.; Goyal, P.; Girshick, R.; He, K.; Dollár, P. Focal loss for dense object detection. In Proceedings of the IEEE Conference on
Computer Vision and Pattern Recognition, Venice, Italy, 22–29 October 2017; pp. 2980–2988.
Moustafa, N.; Slay, J. UNSW-NB15, a comprehensive data set for network intrusion detection systems (UNSW-NB15 network data
set). In Proceedings of the 2015 Military Communications and Information Systems Conference (MilCIS), Canberra, Australia,
10–12 November 2015; pp. 1–6.
Sharafaldin, I.; Lashkari, A.H.; Ghorbani, A.A. Toward generating a new intrusion detection dataset and intrusion traffic
characterization. ICISSp 2018, 1, 108–116.
Chang, L.; Branco, P. Graph-based solutions with residuals for intrusion detection: The modified e-graphsage and e-resgat
algorithms. arXiv 2021, arXiv:2111.13597.

Sensors 2024, 24, 6507

27.
28.
29.
30.

21 of 21

Wang, Z.; Li, Z.; Wang, J.; Li, D. Network Intrusion Detection Model Based on Improved BYOL Self-Supervised Learning. Secur.
Commun. Netw. 2021, 2021, 9486949.
Wang, Z.; Li, Z.; Wang, J.; Li, D. Robust unsupervised network intrusion detection with self-supervised masked context
reconstruction. Comput. Secur. 2023, 128, 103131. [CrossRef]
Zakroum, M.; François, J.; Ghogho, M.; Chrisment, I. Self-Supervised Latent Representations of Network Flows and Application
to Darknet Traffic Classification. IEEE Access 2023, 11, 90749–90765. [CrossRef]
He, M.; Wang, X.; Zhou, J.; Xi, Y.; Jin, L.; Wang, X. Deep-Feature-Based Autoencoder Network for Few-Shot Malicious Traffic
Detection. Secur. Commun. Netw. 2021, 2021, 6659022. [CrossRef]

Disclaimer/Publisher’s Note: The statements, opinions and data contained in all publications are solely those of the individual
author(s) and contributor(s) and not of MDPI and/or the editor(s). MDPI and/or the editor(s) disclaim responsibility for any injury to
people or property resulting from any ideas, methods, instructions or products referred to in the content.
PAPER_TEXT
