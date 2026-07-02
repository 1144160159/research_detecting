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
# [832] Ultimate Encrypted Traffic Feature Engineering: HTTPS Encrypted Traffic Classification Using Restored Application Data Unit Length
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
编号：832
题名：Ultimate Encrypted Traffic Feature Engineering: HTTPS Encrypted Traffic Classification Using Restored Application Data Unit Length
年份：2025
DOI：10.1109/tdsc.2025.3615592
来源：IEEE Transactions on Dependable and Secure Computing
PDF：paper/10.1109_TDSC.2025.3615592.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 17
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\832.txt
- 原始字符数：87935
- 本次发送字符数：87935
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1290

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 1, JANUARY/FEBRUARY 2026

Ultimate Encrypted Traffic Feature Engineering:
HTTPS Encrypted Traffic Classification Using
Restored Application Data Unit Length
Zihan Chen , Member, IEEE, Guang Cheng , Member, IEEE, Dandan Niu , Student Member, IEEE,
Yuyu Zhao , Member, IEEE, Yuyang Zhou , Member, IEEE, and Shanqing Jiang , Member, IEEE

Abstract—Over-the-top (OTT) applications mainly communicate through HTTPS, the most famous encryption protocol family
on the Internet. The classification of HTTPS encrypted traffic can
effectively obtain fine-grained OTT application information for
network management and cyber security. As the most expressive
feature, the side-channel length sequence is widely used by current
research, especially the packet length sequence. However, these
attempts ignored interferences from protocol piecewise decoupling
and encryption covering, leading to poor performance. Based on
the application layer feature engineering theory, we proposed a
new metric called Application Data Unit (ADU) length to eliminate the interferences. However, ADU length cannot be obtained
directly from packets as the TLS encryption protocol covers the
entire application layer, which contains an intrusive and variable
HTTP header. Hence, we designed a Length-Correction Multiple
Regression Neural Network (LC-MRNN) algorithm to restore the
real ADU length sequences accurately. Exhaustive experiments in
two scenarios of the real CERNET network show that no matter the
HTTP-1.1 or HTTP-2.0 protocol, the LC-MRNN model can achieve
significantly accurate ADU length restoration. In classification,
with the assistance of the LS-LSTM classifier, our method outperforms the state-of-the-art methods with about 4.2% improvement
in F1-score (93.52%).
Index Terms—Encrypted traffic classification, application layer
feature engineering, application data unit, length-correction
multiple regression neural network, HTTPS.

I. INTRODUCTION
NCRYPTED traffic has become an inevitable trend, led
by the HTTPS (HyperText Transfer Protocol over TLS
(Transport Layer Security)) encryption protocol family [1].

E

Received 14 December 2023; revised 23 September 2025; accepted 25
September 2025. Date of publication 29 September 2025; date of current version
14 January 2026. This work was supported by the General Program of the
National Natural Science Foundation of China under Grant 62172093, in part by
the Joint Funds of the National Natural Science Foundation of China under Grant
U22B2025, in part by the Youth Fund of the National Natural Science Foundation
of China under Grant 62402101, and in part by the Jiangsu Funding Program for
Excellent Postdoctoral Talent under Grant 2024ZB494. (Corresponding author:
Guang Cheng.)
Zihan Chen, Dandan Niu, Yuyu Zhao, and Yuyang Zhou are with the School of
Cyber Science and Engineering, Southeast University, Nanjing 211102, China.
Guang Cheng and Shanqing Jiang are with the School of Cyber Science
and Engineering, Southeast University, Nanjing 211102, China, and also with
the Purple Mountain Laboratories, Nanjing 211111, China (e-mail: chengguang@seu.edu.cn).
Digital Object Identifier 10.1109/TDSC.2025.3615592

According to the Google Transparency Report [2], as of October 2023, the percentage of Chrome Web pages that are
encrypted has reached 98%, and almost 100% of traffic across
all Google products and services is encrypted. Despite the
fact that QUIC (Quick UDP Internet Connections, i.e. HTTP3.0) has been embraced by certain applications, HTTP-TLSTCP ecosystem still constitutes the mainstream at present.
Encrypted traffic provides users and companies with data security and privacy protection [3]. However, it brings trouble
to Internet Service Providers (ISPs) in network management
(e.g. traffic acceleration), information forensics (e.g., behavior
auditing), and cyber security (e.g., intrusion blocking), especially for Over-the-top (OTT) services and applications. Traffic encryption makes it difficult to use the traditional Deep
Packet Inspection (DPI) [4] method based on plaintext. Therefore, current research on encrypted traffic classification focuses
on HTTPS traffic, which is also the main concern of this
paper.
To tackle this problem, the academic realm has put forward
encrypted traffic classification methods [5] to uphold the merits
of timeliness, large-scale processing, transparency, and privacy
protection in traffic-side analysis. These methods make use
of features that are not obscured by encryption to categorize
or identify the actual kinds of Internet services, applications,
functions, and malicious intent underlying the current traffic.
They are capable of offering effective intelligence support for
currently impaired network management and security. Nonetheless, distinct from natural language and images, encrypted traffic
is structured sequence data in a non-Euclidean space [6]. Packets
serve as the fundamental transmission unit, and flows act as
the atomized service support. As a typical supervised learning problem, when disregarding data sources, encrypted traffic
classification currently confronts two of the most formidable
challenges: (1) In the context of ever-evolving protocols, network environments, and applications, which features should be
employed for classification? (2) Which model is most appropriate for representing these features? At present, the research in
this domain predominantly centers on feature engineering and
classifier optimization.
Considering that features establish the upper bound of classification performance, while models merely strive to approximate
it, the most critical aspect in the realm of encrypted traffic

1545-5971 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

CHEN et al.: ULTIMATE ENCRYPTED TRAFFIC FEATURE ENGINEERING: HTTPS ENCRYPTED TRAFFIC CLASSIFICATION

Fig. 1. HTTPS encrypted traffic transmitting protocol stack and source of
interference.

analysis persists as feature engineering. Although the accuracy
upper limit is classifier-dependent [7], the gradual improvement of classification accuracy shows that the limit of feature
information disclosure is also gradually increasing. In other
words, improving classification accuracy, especially the lower
limit of classification accuracy, requires the input features to
contain as much information disclosure as possible. At present,
feature engineering for encrypted traffic predominantly centers
around three categories of features: residual plaintext header
features, inter-arrival time distribution features, and length sequence features. Regarding generalization capabilities, length
sequence features have been empirically demonstrated to exhibit
superior performance in the majority of classification scenarios
associated with data behavior [8].
However, the current encrypted traffic classification methods predominantly utilize packets as the input unit. Only a
limited number of studies have employed Protocol Data Units
(PDUs) of high-level protocols (e.g., TLS) as input units [9],
[10]. From the perspective of protocol engineering design,
higher-level protocols are more intricately associated with the
application’s behavior, whereas lower-level protocols are more
closely related to the network environment. The encrypted traffic
classification methods based on the length sequence of packets
or TLS segments encounter feature interference resulting from
piecewise decoupling. For instance, in the case of HTTPS, the
data generated by OTT applications is successively encapsulated
and segmented by the HTTP, TLS, TCP, and IP protocols.
Consequently, when packets or TLS segment sequences are
used as the source for encrypted traffic feature extraction, the
disclosure of information regarding encrypted traffic features is
restricted compared to the original data. This is mainly because
the encrypted traffic introduces two instances of segmentation
and one instance of encryption interference, as depicted in Fig. 1.
As a result, there is inconsistency between the actual data volume
and the total length of the packets, which causes errors in
classification.
In this paper, we focus on the ultimate encrypted traffic
feature engineering, aiming to classify encrypted traffic using
the features most relevant to the data transmitted by encrypted
traffic in the protocol stack. The work we have done is shown

1291

Fig. 2. Procedures in encrypted traffic classification with the current research
focuses.

in Fig. 2 from the perspective of the HTTPS network protocol
stack. Based on the Application Layer Feature Engineering
(ALFE) and Application Data Unit (ADU) length sequence
feature proposed earlier [11], we instantiate the concept of ADU
under HTTPS protocol and theoretically prove the superiority
of the ADU length sequence feature under HTTPS encrypted
traffic classification. Furthermore, aiming at the problem that the
real ADU length is disturbed by TLS encryption and underlying
HTTP header with variable length, we study the sources of interference, including systematic error and random error. Based on
removing systematic errors, we propose the Length-Correction
Multiple Regression Neural Networks (LC-MRNN) algorithm for random error reduction to restore the real ADU length
sequences from the TLS segment length sequences. We further
instantiate LC-MRNN with the state-of-the-art LS-LSTM classifier [9] into the LC-MRNN with Application Classification
(LC-MRNN-AC) model in HTTPS scenarios with both the
HTTP-1.1 and HTTP-2.0 application layer protocol. Finally, the
application classification of encrypted traffic with high precision
is realized.
Our main contributions are summarized as follows:
r On the basis of previous work ALFE [11], we have broken
through the concept of BBP’s (Bit-Per-Peak) description of
application transmission data under streaming media [12],
and innovatively defined the concept of ADU - a new
metric of encrypted traffic inputs in the HTTPS scenario
and use the ADU length sequence to classify encrypted
traffic. By further proposing three new evaluation criteria,
we prove the theoretical advantages of ADU in encrypted
traffic classification compared with TLS segment and TCP
packet.
r We design LC-MRNN, a transformer-based ADU length
restoration algorithm, which can accurately restore the
ADU length sequence of HTTPS traffic (both HTTP-1.1
and HTTP-2.0 protocols are included). The restoration of
ADU length through decoding the application layer segmentation semantics becomes the key to breaking through
the bottleneck of classification accuracy for encrypted traffic - this is precisely the core contribution of this paper.

1292

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 1, JANUARY/FEBRUARY 2026

TABLE I
ALL THE ACRONYMS USED IN THIS PAPER

Moreover, we further instantiate LC-MRNN with our previous work LS-LSTM classifier [9] and A3C system [13]
into the LC-MRNN-AC model. It guarantees that the classification can be realized effectively and efficiently.
r We have deepened the open-world scenario and proposed
the concept of the small world and the big world. We then
collect and publish real-world HTTPS data in the largescale CERNET environment with pure real application
labels and corresponding decrypted HTTP plaintext data in
reassembled data form. Experiments conducted in the big
and small worlds show that LC-MRNN can effectively restore the real ADU length sequence and greatly improve the
classification effect of existing encrypted traffic classifiers.
LC-MRNN-AC outperforms state-of-the-art methods.
The rest of the paper is shown as follows. Section II introduces
the main research directions of existing encrypted traffic from
two perspectives: classifier and length feature engineering. In
Section III, we theoretically prove the ADU length sequence’s
effectiveness and formalize this paper’s research problems.
Section IV puts forward the LC-MRNN algorithm and implements it concretely in HTTP-1.1 and HTTP-2.0 scenarios. In
Section V, we conduct experiments from two perspectives to
prove the method’s effectiveness. Finally, we summarize our research and discuss the existing problems and further research in
Section VI. All the abbreviations mentioned in this paper are
shown in Table I.
II. RELATED WORK
Encrypted traffic classification pursues good performance,
and the evaluation indexes can be accuracy, precision, recall, etc.
The optimization of these indexes is reflected in each procedure
of encrypted traffic classification.
A. Classifiers of Encrypted Traffic
Encrypted traffic classification is a typical supervised learning
problem for which the labeled sample dataset is critical [14]. In
the classification of encrypted traffic, the current mainstream
classification methods have transitioned from machine learning
methods to deep learning methods. These deep learning classifiers can be divided into three categories: single base model,
model overlay, and model fusion.

In the single base model, the most classical CNN was pioneered for encrypted traffic classification [15] to take advantage of its end-to-end learning features. And then, MLP [16],
RNN (LSTM) [17], Text-CNN [18], CapsNet [19] are used
in encrypted traffic classification to deal with the problem of
poor representation of sequential data features by CNN. These
methods use the binary or byte information of the raw packet
for classification.
However, the automatic feature extraction ability of a single
deep learning model is limited, which is manifested in the
different attention to the classification accuracy of different categories [20]. Therefore, with the development of semi-supervised
learning and hardware computing power, some studies tend to
use multiple deep learning models to classify encrypted traffic
to improve the classification effect. The most direct way is the
model overlay. It uses multiple models (usually models with
different structures) to make up for the feature presentation
shortcomings of a single model.
In the model overlay, the representive ones are STNN [21]
(LSTM and 3d-CNN), TEST [22] (CNN and LSTM), CNN and
LSTM combined with distributed training [23], DISTILLER [6]
(CNN and MLP), CENTIME [24] (ResNet and AutoEncoder).
Another way to combine multiple models is the model fusion, which combines multiple base model elements into a
new neural network classifier. It includes CLD-NET [25] (serialized CNN, LSTM and Fully-Connected Network (FCN)),
ICLSTM [26] (Inception CNN juxtaposed with LSTM),
SAM [27] (self-attention combined with CNN), tree-RNNs [28],
I2 RNN [29] (using each round of output during the iteration of an LSTM classifier as a fingerprint), ensemble
Graph Neural Networks (GNN) [20]. Model fusion can further coordinate the feature expression capabilities of different neural network elements but relies more on expert
knowledge.
A summary of the three different schema of deep learning
classifiers is shown in Table II.
In addition, some studies have applied other deep learning
optimization techniques to existing deep learning base models.
For example, incremental learning [30], explainable artificial
intelligence [31], unknown application clustering [32], triple
attention mechanism [33], multimodal learning [34].

CHEN et al.: ULTIMATE ENCRYPTED TRAFFIC FEATURE ENGINEERING: HTTPS ENCRYPTED TRAFFIC CLASSIFICATION

TABLE II
CURRENT DEEP LEARNING MODELS IN ENCRYPTED TRAFFIC CLASSIFICATION

B. Encrypted Traffic Length Feature Engineering
Feature is an essential basis of classification. A good feature
can effectively represent the gap between different categories to
achieve classification effectively. However, the current research
suggests that direct input of all raw bytes of the flow does not
perform well in the cases of high encryption ratio [35]. It further
evidences that the selected features are not necessarily the best
and cannot be interpreted [6].
The main reason is the non-high-dimensional optimization
of features (similar to natural language, traffic data will be
segmented into different PDUs due to the network protocol
stack, and the direct input of the original traffic data will lead
to the loss of high-dimensional features) and local optimal
with structural features ignorance [6] (encrypted traffic, unlike
images, is structured data containing security protocols and
network protocol stacks, and the original traffic directly input
will erase such features). This phenomenon creates a serious
concept drift [36].
Encrypted traffic is essentially a packet sequence in the network [37]. Therefore, the existing research on feature optimization mainly starts from its serialization characteristics, especially
the Markov features between packets.
Korczy M. et al. [38] first proposed the FoSM to depict the
change relation of message type in TLS headers. Further, TLS
handshake certificates and the first application data length were
proposed, named SoB [39]. Then, Chang Liu et al. first proposed
LaFFT [40] based on fast Fourier transform, then proposed
MaMPF [41] based on message type sequence and length block
sequence, and finally proposed FS-Net [8] based on full packet
length and representation learning. So far, the classification of
encrypted traffic has mainly adopted the feature of the length
sequence [42], [43], [44].
As a result of the layered design of network protocols, data
needs to be segmented during actual transmission. As a result,
the length of packets obtained at the network layer or transport
layer differs greatly from that at the application layer. Subsequent studies pay more attention to the high dimensional length
sequence features of encrypted traffic length sequences [45].
The high dimensional length sequence feature refers to the one

1293

TABLE III
REPRESENTATIVE ENCRYPTED TRAFFIC LENGTH FEATURE ENGINEERING
WORKS

obtained by further calculation or reconstruction of the packet
length values. The most typical is to reconstruct the PDU of the
packet sequence, using the PDU of the higher layer protocol as
the input unit to eliminate the error caused by packet-level data
segmentation.
In this kind of research, the representative features include
TLS segment length sequence [46], TLS bidirectional Application Data (a special message type, different from ADU in
this paper) length sequence [10], TLS bidirectional flow length
sequence [47] and multi-PDU length sequence [45] with its
N-gram length hyper-sequence [9] in our previous studies.
In addition to high protocol level length features, there are
also studies on cumulative length features [3], graphic length
features [48], and multi-flow features [49].
A summary of different length feature engineering works
is shown in Table III. The feature determines the upper limit
of the classification effect, and the model only approximates
it. However, the premise for practical feature engineering and
model building is that there should be no errors or interferences
in the input. Otherwise, the significance of selected features will
be suppressed. This is also the problem that this paper needs to
overcome.
III. APPLICATION DATA UNIT LENGTH SEQUENCE
In this section, we first introduced and defined the concept
of ADU in encrypted HTTPS traffic classification. Then, we
prove that the ADU length sequence is more efficient than TLS
segment and TCP packet length sequences. Afterwards, the
ADU length interference is analyzed, and the problems to be
solved in this paper are also formally defined.
A. Application Data Unit
It is worth noting that ADU is not a completely new concept in
the field of networks. It has already been introduced in the QoE
estimations and classifications domain (although not named
strictly as ADU, the meaning is highly relevant), and it mainly
focuses on the fragments after the video is segmented [12].
However, during this process, these concepts are mainly used

1294

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 1, JANUARY/FEBRUARY 2026

to calculate the statistical features of streaming media transmission such as BBP, rather than focusing on the relationship
between the variable headers and core body of the encrypted
application layer. For the classification scenarios of encrypted
traffic, especially the HTTPS, in our previous work, we proposed
the theory of ALFE [11]. In ALFE, ADU is a general name
for all PDU at the application layer. However, currently in
the field of encrypted traffic classification, ADU has not been
clearly defined. Therefore, considering different message queue
patterns, taking the HTTPS protocol stack as an example, we
define the ADU in HTTPS encrypted traffic classification as
follows.
Definition 1 (ADU). ADU is all data transmitted by HTTP
protocol in a single request or response process: From the
definition, it is evident that the distinction between BBP and
ADU lies in the following aspects. Regarding encrypted videos,
BBP constitutes a part of the entire encrypted protocol and
encompasses the application layer header. In the case of the
downlink stream response, ADU represents the actual size of the
video fragments without the header. When it comes to HTTPS,
BBP can be likened to the aggregation of TLS Segments. Simultaneously, BBP depends on well-defined boundaries. It is more
appropriate for streaming media videos that are transmitted in
fragments. However, it is less suitable for application scenarios
such as web pages.
In an actual network environment, if an ADU is needed, we
only need to obtain the HTTP request body and response body,
that is, the data transmitted in the HTTP communication process.
However, TLS encrypts all HTTP contents (including headers
and bodies).

B. Superiority of ADU Length Sequence
The HTTPS protocol stack has three different PDUs without
considering the IP layer. They are packet length sequence, TLS
segment length sequence, and ADU length sequence. The reason
for not considering the IP layer is that its fixed IP header
length and the existence of DHCP make its features irrelevant to
classification. Since the ADU length is consistent with the data
block length transferred in each request-response pair, it strongly
correlates with the data standing back from the application to be
classified.
In our prior research [11], we theoretically established the
superiority of the ADU features. According to the principle [7],
within the context of the same dataset and classification objective, the greater the feature information gain, the more effectively
it can differentiate samples and fulfill the classification task.
To illustrate the superiority of the ADU length sequence in
encrypted traffic classification based on datasets, we chose the
CERNET-1.1 Dataset (to be detailed later) for a preliminary
experiment. We directly compared the relative information gains
of the ADU length sequence, the TLS Segment length sequence,
and the packet length sequence. The results indicate that the
relative information gain of ADU (0.9978) exceeds that of the
TLS segment (0.9950) and is significantly higher than that of
the TCP packet (0.8483). Hence, theoretically, the ADU length

sequence exhibits the optimal classification performance in these
PDUs.
In addition to information gain, we also need to consider the
real network characteristics because network protocols impose
new restrictions on different PDU lengths.
If Ethernet is used as the data link layer protocol, the length
of captured IP packets cannot exceed the default MTU (1500
bytes). Therefore, the length of the TCP payload does not
exceed 1460 bytes (the IP header is fixed at 20 bytes, and the
TCP header is at least 20 bytes). Therefore, two new concepts,
namely Projection Ratio (PJR) and Occupation Ratio (OPR),
are proposed to describe this feature.
PJR is proposed to represent the proportion of the packet
length value in the valid length range. OPR represents the
coverage ratio of the number of length values in the current
sample space. It is worth noting that since the TLS segment and
ADU do not have a clear and fixed upper limit, the value interval
between the maximum and minimum length values in the current
sample is selected as the length interval to be projected.
Suppose that the sample set is X, the PDUs used in the current
classification are u, all length values of the current PDU are L(u)
(including duplicates, equal to all length data), its quantity is
n(u) , and the number of length values that do not duplicate is
s(u) , then the formal expression of PJR and OPR is as follows:





P JR = s(u) / max L(u) − min L(u)
OP R = s(u) /n(u)

(1)

Given the differences in the size of flows and the splicing of
PDUs among applications, we select 50% of the PDU quantity
of the flow with the largest number of PDUs in a certain category
of the current dataset as the selection threshold. According to
the arrival order of PDUs (i.e., the position of PDUs in the flow,
starting from 1), PDUs with positions less than this threshold in
each flow will be included in the calculation.
Why do we choose the position of PDU as the selection metric
and set the threshold at 50%? The reasons mainly come from
four aspects.
r Firstly, the PDU sequence input in the process of encrypted
traffic classification is continuous, and there is a Markovian
relationship between adjacent PDUs. The position of PDU
directly represents the arrival stage of data, and starting
from the first position can meet the complete characterization of the flow.
r Secondly, the number of packets in network flows can be
approximately fitted by a Zipf distribution [50], allowing
us to select a moderate proportion and still obtain a large
proportion of PDUs.
P (k; s, N ) =

N

1
1/k s
, HN,s =
s
HN,s
i
i=1

(2)

During this process, the PDUs from a very small number
of flows without similar volume references can be eliminated. When s = 1, the proportion of considered PDUs
to all PDUs is approximately 1 − 0.5/ ln(N ). When N is
1000, the acquisition ratio can reach 92.76%. For actual

CHEN et al.: ULTIMATE ENCRYPTED TRAFFIC FEATURE ENGINEERING: HTTPS ENCRYPTED TRAFFIC CLASSIFICATION

1295

TABLE IV
PJR, OPR AND FEC OF THREE DIFFERENT PDUS

networks, the N value is much larger, and the distribution
of flows within the same type is more concentrated, so the
actual proportion of obtained PDUs will be even higher.
r Thirdly, we verified this theoretical result through a preexperiment. Taking the CERNET-1.1 dataset as an example, we can calculate that at the 50% threshold, the proportion of ADU obtained is 98.80%, that of TLS Segment is
99.79%, and that of TCP packets is 98.58%. This selection
ratio is completely in line with expectations.
r Fourth, given that there may be differences in the distribution of long and short flows among different categories, we
adopted the principle of median robustness, which means
that for skewed flow features, the median is more resistant
to the interference of outliers than the mean. Therefore, we
selected 50% as the threshold.
Since PJR reflects the proportion in the value space, the lower
PJR is, the looser distribution of features relative to the value
space is, and the lower the probability of feature similarity is.
OPR reflects the proportion in the sample space, so the higher
OPR is, the lower the probability of feature similarity is. In order
to effectively combine these two evaluation criteria, we further
propose a new concept called Feature Efficiency Coefficient
(FEC):

F EC = log

1
P JR


+ OP R

(3)

We take logarithm base 2 of reciprocal of PJR. The main
reason is that the maximum value determines the value space of
PJR in ADU or segment in the current sample (to avoid almost
zero PJR when a potential PDU max size is too large). If the
logarithmic constraint is not used, the utility of OPR will be
significantly reduced.
Table IV shows the PJR and OPR of the eight representative
applications of HTTP-1.1 under three different PDUs, as well
as the FEC of each PDU. Noted that if there is only one possible
length, the PJR at that position is 0.
We also conducted statistics on the HTTP-2.0 dataset
(CERNET-Web-2.0). The FEC presented by the three different
PDUs is consistent with Table IV, that is, the FEC contained in
the ADU is higher than that of the other two PDUs. The results
show that the ADU length sequence is the most expressive.
Therefore, we select the ADU length sequence as the optimized
feature to classify encrypted traffic.

Fig. 3.

Illustration of systematic and random errors in HTTPS ADU length.

C. ADU Length Interference and Restoration
However, TLS effectively encrypts the entire HTTP application layer. Therefore, the real features of ADU, especially the
length features, cannot be obtained directly. The ADU length
read from the PDU segments of TLS has systematic and random
errors. The systematic errors are caused by the plaintext TLS
header and the encrypted fixed part in the HTTP header. It is
worth noting that the fixed HTTP header length is derived from
the fixed-length field in the HTTP header. Random errors are
more varied than systematic errors, including non-fixed fields
and variable-length fields of HTTP headers. Systematic errors
need to be compensated by analyzing their causes, while random
errors can only be reduced by estimation. The two errors are
illustrated in Fig. 3.
Systematic errors can also be reduced using models, but it is
better to remove them directly. As TLS headers are all plaintext
(in TLS-1.3, the encrypted handshake part is determined as data),
the systematic errors caused by the TLS layer can be directly
removed. However, systematic errors in the HTTP layer need
to be further calculated. After statistical analysis of massive
samples, typical systematic errors in HTTP layer (include both
HTTP-1.1 and HTTP-2.0) are listed in Table V. It can be seen
that the systematic error of HTTP-2.0 is much less than that of
HTTP-1.1. It is because HTTP-2.0 uses standardized static and
dynamic parameter tables and the HPACK dynamic compression
mechanism to compress the original fixed-length content greatly.
After the systematic error is removed, the remaining random
error needs to be reduced by the model, which is the core
problem to be solved in this paper. The essence of ADU accurate
restoration is to restore the TLS segment length sequence to the
real ADU length sequence.
D. Problem Definition
Before the real ADU length restoration, the problem of encrypted traffic classification based on length should be formally
described. The problem of encrypted traffic classification based
on length is to classify encrypted traffic to a specific service or
application, using only the length sequence of the traffic as the
original input. Assuming there are N samples to be classified
and C different categories, then the k-th sample (assuming
(k) (k)
(k)
(k)
the sequence length is m) xk = [l1 , l2 , . . . , lm ], where lu

1296

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 1, JANUARY/FEBRUARY 2026

TABLE V
TYPICAL SYSTEMATIC ERRORS OF ADU LENGTH IN HTTP LAYER OF HTTP-1.1 AND HTTP-2.0

refers to the length of the u-th unit (ADU, in this paper) in the
sequence. If it is a service classification and the real category of
xk is Sk , the goal of the encrypted traffic service classification
is to build a model ϕ(xk ) to get a predicted label Sk which is
expected to be the real label Sk .
(k)
For ADU restoration, we aim to make lu closer to the real
length we need. Therefore, assume that the current sample for
classification is x (the sequence length is m), the observation
sequence length is x = [l1 , l2 , . . . , lm ], and the corresponding
real ADU length sequence is r(x) = [l1 , l2 , . . . , lm ]. The goal
of restoring ADU length sequence is to create a model that
makes the length value of each ADU lu (1 ≤ u ≤ m) in the
sequence closer to its corresponding real length lu . It is assumed that the ADU length are independent and identically
distributed, and since the minimum systematic error Eω is
removed, the observed value must be greater than the real ADU
length value. It means if the random error of ADU length is
Eδ , for ∀1 ≤ u ≤ m, E δ (u) = lu − Eω − lu ≥ 0. Hence, this
paper aims to build a model μ that is according to the minimum
sum of the differences between all the observed lengths and true
lengths in a sequence, namely argmin m
u [μ(lu − Eω − lu )].
IV. LENGTH-CORRECTION MULTIPLE REGRESSION NEURAL
NETWORK
In order to restore the ADU length, we propose a LC-MRNN
model, which takes the spliced TLS segment length sequence
as input and restores each value to the real ADU length in the
sequence.
A. LC-MRNN Overview
The essence of ADU length restoration is to convert one
length sequence into another length sequence, and the two
length sequences can be equal in size. The relationship between
each ADU length value in the ADU length sequence represents
the relationship underlying the original data to be transmitted.

Therefore, the Markov properties between ADUs are not only
reflected in the values but also in the positions of the sequences.
In an actual network environment, the HTTP header length
will continue to change as the transmission progresses. In HTTP1.1, we call this inter-flow header length variability. It refers
to the effect that HTTP headers vary in length across different
flows, even when the same data is transmitted. In HTTP-2.0,
the presence of HPACK makes this more variable, which we
call intra-flow header length variability. Through an extensive
sample collection, it is found that in the vast majority of traffic,
the length of ADU is much larger than the length of the HTTP
header. Therefore, we restore the ADU length sequence directly
from the TLS segment length sequence. Since the browser’s
caching mechanism only affects the resource, there is no need
to consider the impact of browser caching in this process.
In recent years, Google has proposed Transformer [51], a
deep neural network architecture for machine translation in NLP,
which can make good use of self-attention of the sentence for
translation. The ADU restoration process can be considered as
translating the spliced TLS segment length sequence into the real
ADU length sequence. The relationship between length values
before and after the restoration is not strictly corresponding and
the values are discrete, similar to the translation problem.
Therefore, we propose a Length-Correction Multiple
Regression Neural Network (LC-MRNN) algorithm based on
Transformer to achieve the ADU restoration. The algorithm is
shown in Fig. 4. It is worth noting that although LC-MRNN has a
similar architecture to the standard Transformer, we have introduced additional local dependency-enhanced padding screening
layers and hierarchical normalization strategies to adapt to the
scenario where the PDU number of encrypted flow is variable.
To improve computational efficiency (the embedding size is
much larger than natural language), we have also introduced
dynamic attention scaling and gradient clipping. Additionally,
we customize and construct pad-aware loss and direction-aware
filtering. Therefore, while focusing on global dependencies, we
also explicitly enhance the ability to extract local features.

CHEN et al.: ULTIMATE ENCRYPTED TRAFFIC FEATURE ENGINEERING: HTTPS ENCRYPTED TRAFFIC CLASSIFICATION

Fig. 4.

Fig. 5.

1297

Neural network overview of LC-MRNN algorithm.

Illustration of two different length sequence encoding ways.

We first encode the input length sequence by embedding,
and then, in order to reflect the position relationship between
the length values, we encode the position. Then, we use the
multi-head self-attention mechanism to dig into the significance
and relationship between the values in the length sequence and
finally restore the ADU length sequence.
Since encoding of length sequences is involved, there are two
ways to do this. The first way is to encode the length value of the
spliced TLS segment directly, that is, treat the length value as a
numerical value. The second way is similar to the encoding in
NLP, which first converts a word to an index and then encodes it.
The two encoding paths are shown in Fig. 5. The specific choice
of which way we further in-depth in the follow-up experiment.
In this paper, we finally choose the word-to-index scheme.
B. Application Classification Based on Restored ADU Length
ADU length sequence restoration is to improve the effect of
encrypted traffic classification, so we associate ADU restoration
with encrypted traffic application classification.

ADU restoration uses one model, while application classification requires another. The output of the restoration model
is related to the input of the classification model. Both models
have their own training and prediction stages, so it is necessary
to consider what data the two models use as input in the training
and prediction stages, respectively.
For LC-MRNN, its training stage requires the TLS segment
length sequence and the corresponding real ADU length sequence as inputs. The real ADU length sequence is masked by
encryption, so it can only be obtained by decryption. Based on
the A3C system [13] in our previous research, we can effectively
obtain application-level encrypted traffic with labels and only
need to decrypt it to obtain the real ADU length sequence.
However, since the decryption of encrypted traffic must be
carried out using the key of the controllable end during visiting
and requires the authorization of the visitor (involving personal
privacy), it is difficult to deploy on a large scale. We call such
nodes A3C core collection points.
However, for the classifier, because it only cares about classifying the input into a specific application category, it also
needs a large number of labeled samples for training to cover
the diversified functions and behaviors within the application.
Therefore, it must be supported by a labeled dataset that can be
obtained on a large scale. The A3C system without decryption
does not involve any privacy issues, and its ability to deploy on
a large scale without affecting normal use is also proven. Therefore, we can use many volunteered devices to obtain encrypted
traffic samples corresponding to massive TLS segment length
sequences and application category labels.
Due to the need to use the ADU length sequence as the input
of the classifier to improve the classification effect, we choose
to use the restored ADU length sequence after the LC-MRNN
model as the input of the classifier (the training stage is the same
as the prediction stage). It can effectively solve the problem that
the two models have different emphases on input requirements.
Hence, we propose a new composite model called LCMRNN-AC (LC-MRNN with Application Classification) for
ADU restoration and encrypted traffic application classification.
The model combines the LC-MRNN restorer and the classifier. As this paper does not explicitly study the classifiers, our
previous work - the current state-of-the-art LS-LSTM model’s
classification layer [9] is selected as a classifier (N-gram layer

1298

Fig. 6.

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 1, JANUARY/FEBRUARY 2026

The relationship between two submodels in LC-MRNN-AC and the overall deployment structure diagram.

is deprecated). The structure and process of the LC-MRNN-AC
model are shown in Fig. 6.
It is worth noting that because some HTTP requests do not
contain data body, the ADU length is restored to 0, which will
cause certain information loss and may also affect the expression
ability of the classifier. Therefore, we add a positive value to
supplement to solve the problem that the input is 0 and the
embedding input cannot be negative simultaneously.

TABLE VI
STATISTICS OF CERNET-1.1 DATASET AND CERNET-WEB-2.0 DATASET

V. PERFORMANCE EVALUATION
In order to prove the methods in this paper, we carried out
three stages of experiments. First, we conducted experiments
to prove the significance of ADU length restoration. Then, we
performed restoration experiments to prove the effectiveness of
LC-MRNN. They were done in conjunction with the classification experiment, which included two different scenarios of the
small world and the big world. Then, we made a deep comparison
between LC-MRNN-AC and existing state-of-the-art methods
in classification, including classification effect and performance
cost, to prove the superiority of our method.
A. Dataset & Experimental Settings
As this paper involves the restoration of ADU, current public
datasets are difficult to support our experiment. Therefore, based
on the improved A3C system [13], we collected traffic from
nine mainstream web-based applications on the current Chinese
Internet, covering video, e-commerce, social media, news, and
other service types. Traffic samples were collected in the actual
CERNET network environment from November 2021 to May
2023, and each sample has a complete encrypted flow with the
corresponding ADU sequence decrypted as HTTP-1.1.
Meanwhile, to test the method’s validity under the HTTP-2.0
protocol, we collected another dataset and named it CERNETWeb-2.0. CERNET-Web-2.0 consists of 300 pages with 155194
samples (including article pages, blog pages, news pages, course
pages, and resource pages) from CSDN blog website which
is frequently visited in China. It is worth noting that due to
the multiplexing characteristics of HTTP-2.0, the protocol is
currently mainly used for website access. The two datasets will

be available at https://data.iptas.edu.cn/web/tbps. The statistics
of two datasets are shown in Table VI.
To make the experiment more practical, we conducted the
experiments on a workstation cluster (the primary device is
AMD 5950x + RTX 3090). Although the cluster contains devices
with different computility, we ensured the computing units were
consistent in each experiment.
For the experimental scenario, because the data scene classification faced is different from ADU restoration, it is inappropriate
to apply the close-world and the open-world directly. Therefore,
we deepen the concept of the open-world and propose smallworld scenarios and big-world scenarios.
Since this paper does not consider sample similarity measurement, we use time and cyberspace span as the distinction criteria
of small-world and big-world scenarios. In terms of time, we use
the year as a unit, much larger than the application version update
cycle, representing the difference in application data version
or function. In cyberspace, we distinguish the geographical
location of the server cluster (obtained by querying the IP home),
such as the cloud center in Beijing and Shanghai, which can
effectively represent the difference in user habits.
Therefore, a small-world scenario refers to a scenario where
the feature distribution of the application or data is similar. In
addition, the real ADU length can be acquired by the A3C
core point in a small-world scenario, as the sphere of influence
is limited. On the contrary, the big-world scenario represents
the data scene where the real length of the ADU cannot be
effectively obtained. The data feature distribution, application

CHEN et al.: ULTIMATE ENCRYPTED TRAFFIC FEATURE ENGINEERING: HTTPS ENCRYPTED TRAFFIC CLASSIFICATION

Fig. 7.

1299

Convergence curves of three different PDU length sequences under three models.

TABLE VII
COMPARISON OF THREE DIFFERENT LENGTH SEQUENCE INPUTS UNDER
CERNET-1.1 HTTPS SAMPLES

type, and function are significantly different from the smallworld scenario.
Before the experiments, we divided the two datasets into 60%
small-world dataset and 40% big-world dataset according to the
time and server IP of sample data collection. The small-world
dataset is used for LC-MRNN model training and testing, and the
big-world dataset is not used for training. The big-world dataset
is only used for the testing of models trained by small-world
datasets.
B. ADU Restoration Significance Experiment
As ADU serve for encrypted traffic classification in practical,
we conducted a controlled experiment to prove the ADU length
sequence’s optimization effect on encrypted traffic classification. Classifiers used for the experiment include LS-LSTM [9],
LS-CapsNet [45], and FS-Net [8], which are currently the most
representative encrypted traffic classification models based on
length sequence.
When the input size is limited to 24, the full traffic classification results under CERNET-1.1 dataset are shown in Table VII
(Pr represents precision and Rc is Recall).
Taking the amount of input packet counts as the independent
variable (it is worth noting that since traffic is collected in the
packet granularity and TLS Segment and ADU are spliced on
packets, the packet is taken as the input unit), we further conducted experiments on the classification effects of three different
PDUs under LS-LSTM in this scenario.
In addition, to prove the advantages of ADU length sequence
in model training, we evaluated the convergence experiments
under the three models based on a fixed number of input TCP
packets of 800, as shown in Fig. 7.

Fig. 8.

Count distribution of adjacent ADU length interval.

This figure shows that the ADU length sequence features
a faster convergence speed. In LS-CapsNet, the continuous
oscillation is caused by the specialty of the model itself (CapsNet
uses dynamic routing instead of gradient descent). The overall
results demonstrate that the ADU length sequence has the best
effect, which further verifies the effectiveness and necessity of
ADU restoration.
C. Small-World LC-MRNN Superiority Experiment With
Numerical Encoding
After determining the necessity of restoration, we conducted
experiments on the effect of the LC-MRNN algorithm on the
small-world dataset. We selected six representative applications
of HTTP-1.1 with relatively uniform length distribution and
similar ADU length values (which are more challenging to
restore accurately) for the LC-MRNN restoration experiment.
In the meantime, we first experimented with numerical coding.
Since the theoretical maximum length of ADU is infinite, and
sequences are embedded in the LC-MRNN algorithm, the vast
ADU size will also cause a colossal memory occupation for the
model. Therefore, we first made statistics on the size of adjacent
intervals of all ADU length values in the CERNET-1.1 dataset,
which are shown in Fig. 8. Since these statistics aim to find the
factor of scaling, the distribution is represented as an exponential
form with a base of 10.

1300

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 1, JANUARY/FEBRUARY 2026

TABLE VIII
SMALL-WORLD: RESTORATION RESULT UNDER FIVE CRITERIONS

TABLE IX
BIG-WORLD: RESTORATION RESULT UNDER FIVE CRITERIONS
Fig. 9.

Model memory size cost under different MATR after scaling.

The results show that the most ADU lengths are more than
100 bytes. Since the scaling will cause a loss of accuracy, we
finally use 10 as the scaling factor to pre-compress the maximum
length of ADU. When the ADU length is restored and the real
ADU length is used as LC-MRNN model input, they will be
scaled first and divided by 10.
Further, although we have scaled down the ADU length upper
limit to one-tenth of the original size, the upper limit is still a
variable. The input of the neural network requires that the upper
limit of ADU length should be a certain value, and the selection
of this value should balance the model’s size and effect.
Therefore, we conducted experiments to fix the maximum size
of ADU, which is determined by the Maximum ADU Threshold
Rate (MATR). MATR is the ratio of the chosen ADU length
upper limit to the maximum value of all ADUs in the sample.
The relationship between MATR (from 50% to 99%) and model
size is shown in Fig. 9.
The results show that with the increase of MATR, the model’s
size increases significantly, and the higher the MATR, the faster
the rise. It is because an enormous ADU value is also a tiny
percentage of the sample space, but it will greatly increase model
size. Therefore, we need to limit the model size through MATR
on the premise of ensuring accuracy. Otherwise, models over
1 GB are unacceptable on common traffic acquisition analysis
points like gateways. Meanwhile, during the period from 50% to
80%, the accuracy rate increases significantly with the increase
of MATR. The accuracy also improved from 80% to 99%, but
the improvement was slight.
In order to determine the final MATR and obtain the fixed
embedding size, we choose four representative MATRs from
the above experimental results to carry out in-depth experiments,
namely, 98%, 95%, 90%, and 80%. After we numeralize them,
the four MATRs correspond to 83030, 55670, 43910, and 23450,
respectively. The classification results of four MATR by LCMRNN-AC are shown in Fig. 10.
The results show that 83030 has the fastest convergence speed
with the best accuracy. Therefore, we choose 83030 as the ADU
length upper limit (after scaling), and any value exceeding this
length will be transformed into 83030.
On this basis, we further experiment with the restoration effect
of the core LC-MRNN restoration model. The experimental
results are shown in Table VIII. It is worth noting that the
distance D used here is the Euclidean distance of the sequences.

Among them, D̄, M ax(D) and δ(D) refer to the average,
maximum and standard variance of D, respectively. Zero rates
r(0) refer to the ratio that the distance between two sequences
is 0 (totally same). The higher the r(0) is, the more precise the
restoration is. The restoration rate β refers to the length ratio of
the restored part to the part that should be restored. It is used
to evaluate the overall restoration effect, and the restoration
rate should be about 1. It can be seen from the results that
the restoration effect of the small-world dataset is excellent.
Although the restoration distance of a few sequences is large,
almost identical restoration can be achieved on the whole.
Further, we carried out the classification experiment under the
small-world dataset, and the experimental results are shown in
Fig. 11.
The results show that the classification is outstanding under
the small-world dataset. In other words, when there is a certain similarity between the sequence to be classified and the
labeled sample sequence, it can achieve almost 100% accurate
classification.
D. Big-World LC-MRNN-AC Classification Experiment With
Index Encoding
In an actual network open-world environment, a model trained
in a controlled domain will likely be used nationally or globally.
In the non-controllable domain, it is impossible to train LCMRNN. Therefore, based on the LC-MRNN instance trained in
small-world datasets, we use big-world datasets for restoration
tests and classification experiments. The results are shown in
Table IX.
There is a particular gap between this restoration result and
the small-world dataset’s result. Although the average and maximum restoration distances are negligible compared with the total
length, the zero rates are too low and the restoration rates are
far higher than those in the small-world experiment. Therefore,
if numerical coding is used, there may be problems of overreduction and insufficient accuracy in the big-world scenario,
so we use index encoding instead. We name it isomorphic
length-to-index. In other words, the lengths of PDU and ADU

CHEN et al.: ULTIMATE ENCRYPTED TRAFFIC FEATURE ENGINEERING: HTTPS ENCRYPTED TRAFFIC CLASSIFICATION

Fig. 10.

1301

LC-MRNN-AC Classification Results with Increasing Epoch of Four MATR: (a) Accuracy, (b) Restoration Loss.

Fig. 11.
matrix.

Small-world: Classification precision/recall curve and confusion

Fig. 12.

Big-world: Index encoding accuracy and loss curve.

(which could contain the same value) are encoded to form two
dictionaries, respectively.
Since the brand new PDU and ADU length values will always
exist in the big-world environment, we adopt the dynamic coding
extension method to encode the new values continuously. For the
problem that it is difficult to restore new values that have never
appeared accurately, we rely on the robustness of the classifier
to support it. The restoration accuracy curve of the LC-MRNN
model encoded by an index is shown in Fig. 12.
It can be seen from the results that the overall restoration
accuracy is not very high due to the existence of fresh values
(corresponding to zero rate in numerical encoding), but it is
far higher than the effect of numerical encoding. Since the
purpose of restoration is ultimately classification, it is necessary
to consider the effect of classification in the context of the big
world.

In order to prove the universal superiority of the LC-MRNNAC model, we compare the classification effect of the LCMRNN-AC model with other state-of-the-art models using different feature engineering models on the big-world dataset. In
order to ensure fairness, other models use their preset inputs
and parameters. The models used for comparison are the most
basic CNN [15] (modified to fit length sequences), SAE extracted from Deep Packet, FS-Net [8] for flow length features,
LS-LSTM (without N-gram) [9] for the PDU length sequence
features, GGNN [20] for the graphical packet length sequence,
and miniflowpic [52] for both time and the sequence of lengths.
Firstly, we used the restored ADU length sequence for training
the LS-LSTM classifier in the LC-MRNN-AC. Then, we conducted tests using the original TLS segment length sequence
(LCMRNNAC-TLS-24) and the restored ADU length sequence
(LCMRNNAC-RADU-24). The experimental results showed
that LCMRNNAC-RADU-24 was superior to LCMRNNACTLS-24, which in turn was superior to LSLSTM-TLS. This
proved the superiority of ADU restoration in classification. In
addition, since we found that ADU restoration may lead to the
existence of most 0 values in the request (HTTP request is
likely to contain no data, only headers), which will cause the
classifier’s poor effect to a certain extent, we proposed three
feature enhancement schemes in big-world scenarios. The first
is the direct addition of spliced PDU values and ADU values
for calculation (Direct PDU and ADU Sum, DPAS), the second
is the absolute value addition of spliced PDU values and ADU
values (ABsolute PDU + ADU, ABPAS), and the third is the
substitution of ADU sequences with non-zero values in the
spliced PDU sequence (PDU-ADU Replacement, PAR). The
results are shown in Table X.
The round-wise classification results are shown in Fig. 13.
The results show that LC-MRNN-AC has a classification
effect far exceeding the existing state-of-the-art and is better than
the complex and huge LS-LSTM model with the same amount of
data input. The superiority of LC-MRNN-AC under HTTP-1.1
is proved.
E. Applicability of Classification for Extremely Similar
Samples Under HTTP-2.0
In addition to HTTP-1.1, HTTP-2.0 is now HTTPS’s mainstream application layer protocol. However, HTTP-2.0 is mostly

1302

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 1, JANUARY/FEBRUARY 2026

TABLE X
BIG-WORLD HTTP-1.1: CLASSIFICATION RESULTS OF DIFFERENT SOTA
METHODS WITH DIFFERENT PDUS AND INPUT SIZES

Fig. 13. Big-world HTTP-1.1: Comparison of state-of-the-art methods with
different input features.

Fig. 14. Big-world HTTP-2.0: Convergence Curves of Loss and Test Accuracy
of LC-MRNN restorer.

used for web pages, which makes in-app confusion very serious.
Therefore, we conducted experiments on the restoration performance of the LC-MRNN-AC model for HTTP-2.0 samples
and its classification applicability in extremely similar sample
environments under the CERNET-Web-2.0 dataset.
This is an extremely difficult classification scenario because
the data length changes every time we access it and the number
of classes is large. Moreover, the pages on the same website are

very similar, each sequence is very short, and the PDU sequence
that does not meet the input requirements is aligned by filling in
0. In addition, using encrypted traffic application classification
classifiers for web page classification can better reflect the generalization ability of the architecture. It is worth noting that due
to the nature of HTTP-2.0, the distributed correlation between
the training set and the test set generated by random partitioning
will be weak.
First, we conducted a restoration effect experiment, and the
experimental results are shown in Fig. 14. The training and test
sets still follow the 60% vs. 40% rule of the big and small worlds.
The results show that even with the existence of multiplexing
and HPACK head compression, which seriously interfere with
the ADU length restoration, the LC-MRNN model can still
realize the ADU restoration of HTTP-2.0 protocol encrypted
traffic, and the restoration accuracy is even higher than that of
HTTP-1.1.
On this basis, we also compared the LC-MRNN-AC model
with the control group used in HTTP-1.1, and the experimental
results are shown in Fig. 15.
Results show that the classification effect is not good, no
matter what kind of classifier, which is as expected. There are
three main reasons. First, the structural design of the above
classifier is not for the unified website webpage classification
but for the broad category of applications. Second, HTTP-2.0
header compression and multiplexing significantly impact the

CHEN et al.: ULTIMATE ENCRYPTED TRAFFIC FEATURE ENGINEERING: HTTPS ENCRYPTED TRAFFIC CLASSIFICATION

Fig. 15. Big-world HTTP-2.0: Extreme classification convergence curves of
five methods.

Fig. 16.

Memory usage of different models under HTTP-1.1 data.

characteristics of different web pages visited within the website,
and the distribution of training sets and test sets is inconsistent.
Third, the number of classification categories is about fifty
times that of the application, which may exceed the upper limit
of the current classifier hyperparameters. However, it can be
clearly seen from the results that the training accuracy of the
LC-MRNN-AC model has been improving, indicating that the
ADU length restoration still has obvious significance under
HTTP-2.0. It can effectively extract stable ADU length sequence
features from unstable TLS Segment length sequences (features
used by other classifiers). The significance of ADU restoration
and ALFE is further proved.
F. LC-MRNN-AC Performance Overhead Experiment
Since the LC-MRNN-AC model is very complex, especially
the LC-MRNN itself, it is necessary to conduct experiments
on its performance overhead to consider its applicability and
suitable scenarios in the actual network environment.
First, we experimented on memory usage, and the experimental results are shown in Fig. 16.
It can be seen from the results that LC-MRNN-AC has no
obvious advantage in memory occupancy due to the use of transformer architecture (restorer) and huge embedding (classifier),
which even consumes more resources to some extent. This is
mainly because the Transformer is a complex and large architecture, and LC-MRNN-AC consists of two models. However,
the two models can be deployed separately in the engineering
implementation to reduce the resource overhead.

Fig. 17.

1303

Training time cost of different models under HTTP-1.1 data.

Then, we experimented on the training time of the overall
encrypted traffic classification, and the experimental results are
shown in Fig. 17.
As can be seen from the results, the training time of the
classifier in LC-MRNN-AC has obvious advantages. With far
better results than other classifiers, it has less training time (the
model structure is simpler). This is due to the characteristic
advantages brought by ADU restoration, which is consistent
with the theoretical analysis in Section III.
However, it is worth noting that the training time of the
LC-MRNN-AC restorer (LC-MRNN) model is relatively high,
requiring 3714.1659 seconds to complete the training of 200
epochs in a single workstation and completing convergence
in about 170 epochs. Because there is no free lunch in the
classification task, however, the asynchronous separation deployment and the separation of big and small world datasets that
LC-MRNN-AC relies on, in practical applications, the training
cost of LC-MRNN reducers will not affect the classification
(offline advance payment).
G. Analysis & Discussion
1) Why is the ADU Length Sequence Restored From the BigWorld Dataset Used as the Input of the Classification Model?:
A labeled sample dataset with a decrypted HTTP plaintext data
counterpart to the encrypted traffic is extremely challenging
to obtain compared to an encrypted traffic dataset with only
category labels. As a result, if a real ADU length sequence is
used, the training and retraining process will be restricted by the
amount of data, and the toughness to obtain enough samples will
lead to a poor effect.
Although our LC-MRNN sequence is designed to restore the
encrypted traffic length sequence into a real ADU length sequence as accurately as possible, the precise restoration requires
similar features with a high degree found in the experiment. It
is not realistic to acquire a large enough dataset of real ADU
length sequences to cover all the scenarios of the applications.
Coupled with the difference in the network environment and
the rapid iteration of application, concept drift is more likely to
occur.
By comparing small-world datasets with big-world datasets
in experiments, we find that since the ultimate goal of restoration
is classification, the problem of concept drift can be transferred

1304

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 1, JANUARY/FEBRUARY 2026

TABLE XI
COMPARISON OF THREE ADU LENGTH SEQUENCES AS INPUT

from the restorer to the classifier. Compared with the restorer, the
negative effect caused by concept drift can be suppressed by the
classifier’s insensitivity to hits. Moreover, obtaining ADU length
sequence labeled samples is more accessible after restoration.
As an alternative, a restored ADU length sequence as the classifier’s input can significantly decrease the difficulty of classifier
training by giving the classifier sufficient samples, which is also
helpful in dealing with concept drift.
In this paper, though, the big-world dataset is derived from
the CERNET-1.1 dataset same as the small-world dataset, which
has the corresponding decrypted HTTP data. However, in the
LC-MRNN-AC model, its plaintext counterpart is not used. So
this experiment is representative. The big-world dataset at the
moment is a good representation of easily accessible labeled
sample data using A3C normal nodes. The qualitative comparison was made among the three, as shown in Table XI.
2) Why is the ADU Restoration Accuracy Rate of HTTP-2.0
Protocol With Many Interference Technologies Higher Than
That of HTTP-1.1?: HTTP-2.0 should theoretically be more
challenging to restore than HTTP-1.1 because it has a more
complex protocol structure. However, in practice, because the
header and data body of HTTP-2.0 are transmitted separately,
even if they are out of order, they are separated, which brings
the possibility of direct accurate restoration to some samples in
non-multiplexing cases. On the other hand, CERNET-Web-2.0
datasets are all Web traffic, and the ADU of Web traffic is far
less than the average value of conventional applications in terms
of the overall distribution, especially compared with multimedia
applications with extremely large data volumes. Therefore, the
coding space of HTTP-2.0 is relatively small, and thus, better
restoration accuracy is obtained.
3) Is It Worthwhile to Optimize the Input Using the LCMRNN Model in Order to Improve the Precision and Recall Rate
by About 4.2%?: It is worth it. The LS-LSTM model can achieve
89% F1-score under TLS segment length sequence. However,
encrypted traffic classification is a massive data supervised
learning problem (backbone Tbps level). In this situation, the
number of flows to be classified can be in the billion range, and
a four percent improvement might correspond to millions of
correctly classified samples. The accurate classification of encrypted traffic is an essential basis for ISP network management
and network security decision, which is of great economic value
and security protection significance. All it costs is a little extra
computing resource.
4) What are the Advantages and Disadvantages of Index
Encoding?: The most significant advantage of index encoding
is that it can achieve more accurate restoration in the big-world
environment because after index encoding, the original length

value no longer has a numerical adjacency relationship, and
the restorer can pay more attention to the sequence context.
In addition, index encoding does not need to take into account
the effects of MATR because no matter how large, the value
is converted to an equal-length alternative encoding. However,
conversely, this is also the potential disadvantage of index encoding compared to numerical encoding. First, index encoding
needs to consume more encoding space when the length value
distribution is relatively dense, and the encoding codex itself
needs to be stored, occupying additional memory. Second, index
encoding does not solve the problem of values that have not
occurred, which is also a dilemma often encountered in NLP
translation. It is more common in encrypted traffic and can
only be achieved by adding encodings, negatively impacting
restoration. Third, the length sequence is different from the
text sequence, and there is a similar relationship between the
length values; the similar values are theoretically beneficial for
classification. Index encoding ignores this feature, which results
in a loss of information gain to some extent. Therefore, the
coding method is also a key area worthy of further study.
5) Why Do the Effects of LCMRNNAC-DPAS-24 and
LCMRNNAC-ABPAS-24 Turn Out to Be Better Than Those of
LCMRNNAC-RADU-24?: The experimental results of Table X
show that some augmentation methods have achieved a further improvement in classification performance compared to
using only the restored ADU. This indicates that although TLS
segment contains less information gain than ADU, there is a
slight difference in the information coverage provided by the
two. This suggests that in some cases, the network performance
parameters contained in the TLS segment fragments and the
HTTP header length hidden in the data may also have some
effect on classification. This situation has also been indirectly
demonstrated in the papers using time interval sequences for
classification. This is also one of the reasons why miniflowpic
can function under the TLS segment length sequence.
6) Why Choose the Transformer Architecture Instead of
Other Models That are More Suitable for Local Dependencies?:
The variation of TLS segment length is mainly determined by
local dependencies, especially in multimedia transmission scenarios. However, in practical applications, many TLS segment
lengths do not reach the maximum value. At the same time, the
length variation of variable-length HTTP headers is globally
dependent (the global correlation of HTTP parameters) and
even has dependency relationships in multiple visits (application
cookies), and this phenomenon is more obvious in HTTP-2.0
(with the HPACK compression mechanism). Therefore, considering these two situations, we chose the Transformer architecture to build our restorer. It is undeniable that Transformer,

CHEN et al.: ULTIMATE ENCRYPTED TRAFFIC FEATURE ENGINEERING: HTTPS ENCRYPTED TRAFFIC CLASSIFICATION

as a heavyweight architecture, has a large training cost for
LC-MRNN. However, with the optimization of our model architecture, this cost is acceptable (it can run on consumer-grade
graphics cards ranging from 3090 to 4090). At the same time,
due to the architectural advantages of LC-MRNN-AC, it can be
used for a long time after training and reduces the long-term
cost.
7) Is ADU Suitable for QUIC? What are the Difficulties in
Using ADU Under QUIC?: Since ADU is oriented towards the
data being transmitted, it can be used for classifying QUIC
encrypted traffic. However, QUIC encrypts more metadata and
has two formats of long and short headers. Moreover, more
variable-length fields and binary encoding modes make the
systematic error less. Specifically, for the long header, there
are 9 bytes in total, including the header form (1 byte), fixed
bit (1 byte), packet number (at least 1 byte), long packet type (2
bytes), and version (4 bytes). For the short header, there are only
3 bytes, including the header form, fixed bit, and packet number.
Nevertheless, it still has a relatively stable header structure that
can support the restoration process.
In addition, the implications of QUIC streams and HTTP
frames are different. Although QUIC does not, like HTTP-2.0,
introduce an additional binary framing layer, streams and multiplexing on top of the TCP mechanism, it directly implements
streams, and each QUIC connection can carry multiple independent streams, with each stream handling one request-response
interaction. Nicely, its stream ID (connection ID) is in plaintext,
and the number of streams currently existing in the connection
can be directly known through statistics. This is also beneficial
for the precise restoration of ADU.
VI. SUMMARY AND FUTURE WORK
In this paper, we focus on the feature engineering of encryption traffic and propose a new input metric called ADU. We
first propose three evaluation criteria to prove the theoretical
advantages of ADU features in classifying encrypted traffic.
Then, we propose the LC-MRNN algorithm to solve the problem
of the real ADU length being interfered with and masked. In
the next step, we deepen the open-world concept and propose
big-world and small-world scenarios that more closely fit the
actual Internet to prove the method’s adaptability in the real
network environment. According to this setting, two datasets of
application layer protocol HTTP-1.1 and HTTP-2.0 are collected
respectively in the CERNET network environment. Based on
the LC-MRNN algorithm, combined with the characteristics of
HTTP-1.1 and HTTP-2.0 under the actual network environment,
we propose the LC-MRNN-AC model. We experimented extensively with multiple angles and finally chose index encoding
as the encoding method for the length sequence. The reduction
experiments in big and small worlds show that LC-MRNN can
restore ADU length sequences effectively. After the reduced
features are used in classification experiments, the results show
that the precision and recall of the proposed LC-MRNN-AC
model are about 4.2% higher than that of the state-of-the-art
method. Moreover, it has some advantages in memory, training
time, and other performance indicators.

1305

Future research needs to pay more attention to three points:
r The encoding method of length sequence is very different
from the conventional text sequence, which needs further
study.
r The webpage-oriented classifiers with more capabilities
should be designed to make LC-MRNN adapt to webpage
classification. The current application of classification classifiers does not perform well under the multi-page on the
same site.
r With the wide application of the QUIC (HTTP-3.0) protocol, encrypted QUIC traffic classification with ADU
restoration will also become necessary research. Its challenges are inherently related to the life cycle. These challenges span multiple aspects, including the acquisition of
labeled samples, the development of decryption tools, the
rapid evolution of the QUIC protocol, the recombination
of ADU during restoration (since QUIC functions at the
packet level), and the alterations in data splitting techniques. All these areas hold significant research value.
ACKNOWLEDGMENT
This paper is part on the topic of the encrypted traffic classification. Manuscript created March, 2023; This work was
developed by the IEEE Publication Technology Department.
This work is distributed under the Project Public License (LPPL)
(http://www.latex-project.org/) version 1.3. A copy of the LPPL,
version 1.3, is included in the base LaTeX documentation of
all distributions of LaTeX released 2003/12/01 or later. The
opinions expressed here are entirely that of the author. No
warranty is expressed or implied. User assumes all risk.
Finally, I would like to express my deep remembrance to my
beloved wife Yuying Shi, who passed away during the course
of this research. Throughout my life and work, she provided me
with unwavering support, understanding, and encouragement,
which were a tremendous source of strength for me. Her influence is deeply embedded in this work. May she rest in peace.
REFERENCES
[1] J. Muehlstein et al., “Analyzing HTTPs encrypted traffic to identify user’s
operating system, browser and application,” in Proc. 14th IEEE Annu.
Consum. Commun. Netw. Conf., 2017, pp. 1–6.
[2] Google, “HTTPS encryption on the web–Google Transparency Report,”
2023. [Online]. Available: https://transparencyreport.google.com/https/
overview
[3] S. Xu, G. Geng, X. Jin, D. Liu, and J. Weng, “Seeing traffic paths:
Encrypted traffic classification with path signature features,” IEEE Trans.
Inf. Forensics Secur., vol. 17, pp. 2166–2181, 2022.
[4] B. Yang and D. Liu, “Research on network traffic identification based
on machine learning and deep packet inspection,” in Proc. IEEE 3rd Inf.
Technol. Netw. Electron. Automat. Control Conf., 2019, pp. 1887–1891.
[5] P. Velan, M. Čermák, P. Čeleda, and M. Drašar, “A survey of methods
for encrypted traffic classification and analysis,” Networks, vol. 25, no. 5,
pp. 355–374, Sep. 2015.
[6] G. Aceto, D. Ciuonzo, A. Montieri, A. Nascita, and A. Pescapé, “Encrypted
multitask traffic classification via multimodal deep learning,” in Proc.
IEEE Int. Conf. Commun., 2021, pp. 1–6.
[7] S. Li, H. Guo, and N. Hopper, “Measuring information leakage in website fingerprinting attacks and defenses,” in Proc. ACM SIGSAC Conf.
Comput. Commun. Secur., Toronto, ON, Canada, 2018, pp. 1977–1992,
doi: 10.1145/3243734.3243832.

1306

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 1, JANUARY/FEBRUARY 2026

[8] C. Liu, L. He, G. Xiong, Z. Cao, and Z. Li, “FS-net: A flow sequence
network for encrypted traffic classification,” in Proc. IEEE Conf. Comput.
Commun., 2019, pp. 1171–1179.
[9] Z. Chen, G. Cheng, Z. Xu, S. Guo, Y. Zhou, and Y. Zhao, “Length matters:
Scalable fast encrypted internet traffic service classification based on
multiple protocol data unit length sequence with composite deep learning,”
Digit. Commun. Netw., vol. 8, no. 3, pp. 289–302, 2021.
[10] H. Wu, L. Wang, G. Cheng, and X. Hu, “Mobile application encryption
traffic classification based on TLS flow sequence network,” in Proc. IEEE
Int. Conf. Commun. Workshops, 2021, pp. 1–6.
[11] Z. Chen, G. Cheng, Z. Wei, Z. Xu, N. Fu, and Y. Zhou, “Higher layers,
better results: Application layer feature engineering in encrypted traffic
classification,” in Wireless Algorithms, Systems, and Applications. Cham,
Switzerland: Springer, 2022, pp. 548–556.
[12] R. Dubin, A. Dvir, O. Pele, and O. Hadar, “I know what you saw
last minute—encrypted HTTP adaptive video streaming title classification,” IEEE Trans. Inf. Forensics Secur., vol. 12, no. 12, pp. 3039–3049,
Dec. 2017.
[13] Z. Chen, G. Cheng, Z. Xu, K. Xu, Y. Shan, and J. Zhang, “A3C system:
One-stop automated encrypted traffic labeled sample collection, construction and correlation in multi-systems,” Appl. Sci., vol. 12, no. 22, 2022.
[Online]. Available: https://www.mdpi.com/2076-3417/12/22/11731
[14] G. Draper-Gil, A. H. Lashkari, M. S. I. Mamun, and A. A. Ghorbani,
“Characterization of encrypted and vpn traffic using time-related,” in Proc.
2nd Int. Conf. Inf. Syst. Secur. Privacy, 2016, pp. 407–414.
[15] W. Wang, M. Zhu, J. Wang, X. Zeng, and Z. Yang, “End-to-end encrypted traffic classification with one-dimensional convolution neural
networks,” in Proc. IEEE Int. Conf. Intell. Secur. Informat., 2017,
pp. 43–48.
[16] F. Al-Obaidy, S. Momtahen, M. Hossain, and F. Mohammadi, “Encrypted
traffic classification based ml for identifying different social media applications,” in Proc. IEEE Can. Conf. Elect. Comput. Eng., 2019, pp. 1–5.
[17] H. Yao, C. Liu, P. Zhang, S. Wu, C. Jiang, and S. Yu, “Identification of encrypted traffic through attention mechanism based long short
term memory,” IEEE Trans. Big Data, vol. 8, no. 1, pp. 241–252,
Feb. 2012.
[18] M. Song, J. Ran, and S. Li, “Encrypted traffic classification based on text
convolution neural networks,” in Proc. IEEE 7th Int. Conf. Comput. Sci.
Netw. Technol., 2019, pp. 432–436.
[19] S. Cui, B. Jiang, Z. Cai, Z. Lu, S. Liu, and J. Liu, “A session-packetsbased encrypted traffic classification using capsule neural networks,” in
Proc. IEEE 21st Int. Conf. High Perform. Comput. Commun.; IEEE
17th Int. Conf. Smart City; IEEE 5th Int. Conf. Data Sci. Syst., 2019,
pp. 429–436.
[20] Z. Chen, G. Cheng, D. Niu, X. Qiu, Y. Zhao, and Y. Zhou, “WFF-EGNN:
Encrypted traffic classification based on weaved flow fragment via ensemble graph neural networks,” IEEE Trans. Mach. Learn. Commun. Netw.,
vol. 1, pp. 389–411, 2023.
[21] Y. Zhang, S. Zhao, J. Zhang, X. Ma, and F. Huang, “STNN: A novel
TLS/SSL encrypted traffic classification system based on stereo transform
neural network,” in Proc. IEEE 25th Int. Conf. Parallel Distrib. Syst., 2019,
pp. 907–910.
[22] Y. Zeng, Z. Qi, W. Chen, and Y. Huang, “Test: An end-to-end network
traffic classification system with spatio-temporal features extraction,” in
Proc. IEEE Int. Conf. Smart Cloud, 2019, pp. 131–136.
[23] G. Aceto, D. Ciuonzo, A. Montieri, V. Persico, and A. Pescapé, “Know
your Big Data trade-offs when classifying encrypted mobile traffic
with deep learning,” in Proc. Netw. Traffic Meas. Anal. Conf., 2019,
pp. 121–128.
[24] W. Maonan, Z. Kangfeng, X. Ning, Y. Yanqing, and W. Xiujuan, “Centime:
A direct comprehensive traffic features extraction for encrypted traffic
classification,” in Proc. IEEE 6th Int. Conf. Comput. Commun. Syst., 2021,
pp. 490–498.
[25] X. Hu, C. Gu, F. Wei, and C.-H. Chen, “CLD-Net: A network
combining CNN and LSTM for internet encrypted traffic classification,” Sec. Commun. Netw., vol. 2021, Jan. 2021, Art. no. 9835476,
doi: 10.1155/2021/5518460.
[26] B. Lu, N. Luktarhan, C. Ding, and W. Zhang, “ICLSTM: Encrypted
traffic service identification based on inception-LStM neural network,”
Symmetry, vol. 13, no. 6, 2021, Art. no. 1080. [Online]. Available: https:
//www.mdpi.com/2073-8994/13/6/1080
[27] G. Xie, Q. Li, and Y. Jiang, “Self-attentive deep learning method for online
traffic classification and its interpretability,” Comput. Netw., vol. 196,
2021, Art. no. 108267. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S1389128621002930

[28] X. Ren, H. Gu, and W. Wei, “Tree-RNN: Tree structural recurrent neural
network for network traffic classification,” Expert Syst. Appl., vol. 167,
2021, Art. no. 114363. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S0957417420310435
[29] Z. Song et al., “I 2 RNN: An incremental and interpretable recurrent neural
network for encrypted traffic classification,” IEEE Trans. Dependable
Secure Comput., early access, doi: 10.1109/TDSC.2023.3245411.
[30] Y. Chen, T. Zang, Y. Zhang, Y. Zhou, L. Ouyang, and P. Yang, “Incremental
learning for mobile encrypted traffic classification,” in Proc. IEEE Int.
Conf. Commun., 2021, pp. 1–6.
[31] A. Nascita, A. Montieri, G. Aceto, D. Ciuonzo, V. Persico, and A.
Pescapé, “XAI meets mobile traffic classification: Understanding and
improving multimodal deep learning architectures,” IEEE Trans. Netw.
Service Manag., vol. 18, no. 4, pp. 4225–4246, Dec. 2021.
[32] Y. Li, Y. Lu, and S. Li, “Ezac: Encrypted zero-day applications classification using CNN and k-means,” in Proc. IEEE 24th Int. Conf. Comput.
Supported Cooperative Work Des., 2021, pp. 378–383.
[33] J. Zhang, J. Zhou, and N. Zhou, “Network traffic classification method
based on subspace triple attention mechanism,” in Proc. 3rd Int. Conf. Inf.
Sci. Parallel Distrib. Syst., 2022, pp. 312–316.
[34] A. Nascita, A. Montieri, G. Aceto, D. Ciuonzo, V. Persico, and A. Pescapé,
“Improving performance, reliability, and feasibility in multimodal multitask traffic classification with XAI,” IEEE Trans. Netw. Service Manag.,
vol. 20, no. 2, pp. 1267–1289, Jun. 2023.
[35] G. Bovenzi, G. Aceto, D. Ciuonzo, V. Persico, and A. Pescapé, “A
Big Data-enabled hierarchical framework for traffic classification,” IEEE
Trans. Netw. Sci. Eng., vol. 7, no. 4, pp. 2608–2619, 4th Quarter 2020.
[36] J. Lu, A. Liu, F. Dong, F. Gu, J. Gama, and G. Zhang, “Learning under
concept drift: A review,” IEEE Trans. Knowl. Data Eng., vol. 31, no. 12,
pp. 2346–2363, Dec. 2019.
[37] V. F. Taylor, R. Spolaor, M. Conti, and I. Martinovic, “Robust smartphone
app identification via encrypted network traffic analysis,” IEEE Trans. Inf.
Forensics Secur., vol. 13, no. 1, pp. 63–78, Jan. 2018.
[38] M. Korczyński and A. Duda, “Markov chain fingerprinting to classify encrypted traffic,” in Proc. IEEE Conf. Comput. Commun., 2014,
pp. 781–789.
[39] M. Shen, M. Wei, L. Zhu, and M. Wang, “Classification of encrypted
traffic with second-order markov chains and application attribute bigrams,” IEEE Trans. Inf. Forensics Secur., vol. 12, no. 8, pp. 1830–1843,
Aug. 2017.
[40] C. Liu, Z. Cao, Z. Li, and G. Xiong, “LaFFT: Length-aware FFT based
fingerprinting for encrypted network traffic classification,” in Proc. 2018
IEEE Symp. Comput. Commun., 2018, pp. 1–6.
[41] C. Liu, Z. Cao, G. Xiong, G. Gou, S.-M. Yiu, and L. He, “MaMPF:
Encrypted traffic classification based on multi-attribute markov probability
fingerprints,” in Proc. IEEE/ACM 26th Int. Symp. Qual. Service, 2018,
pp. 1–10.
[42] C. Dong, C. Zhang, Z. Lu, B. Liu, and B. Jiang, “Cetanalytics: Comprehensive effective traffic information analytics for encrypted traffic classification,” Comput. Netw., vol. 176, 2020, Art. no. 107258. [Online]. Available:
https://www.sciencedirect.com/science/article/pii/S1389128619309466
[43] X. Yun, Y. Wang, Y. Zhang, C. Zhao, and Z. Zhao, “Encrypted TLS traffic
classification on cloud platforms,” IEEE/ACM Trans. Netw., vol. 31, no. 1,
pp. 164–177, 2023.
[44] G. Aceto, G. Bovenzi, D. Ciuonzo, A. Montieri, V. Persico, and A. Pescapé,
“Characterization and prediction of mobile-app traffic using markov modeling,” IEEE Trans. Netw. Service Manag., vol. 18, no. 1, pp. 907–925,
Mar. 2021.
[45] Z. Chen, G. Cheng, B. Jiang, S. Tang, S. Guo, and Y. Zhou, “Length
matters: Fast internet encrypted traffic service classification based on
multi-PDU lengths,” in Proc. 16th Int. Conf. Mobility Sens. Netw., 2020,
pp. 531–538.
[46] W. Chen, F. Lyu, F. Wu, P. Yang, G. Xue, and M. Li, “Sequential message
characterization for early classification of encrypted internet traffic,” IEEE
Trans. Veh. Technol., vol. 70, no. 4, pp. 3746–3760, Apr. 2021.
[47] X. Wang, S. Chen, and J. Su, “App-net: A hybrid neural network for
encrypted mobile traffic classification,” in Proc. IEEE Conf. Comput.
Commun. Workshops, 2020, pp. 424–429.
[48] M. Shen, J. Zhang, L. Zhu, K. Xu, and X. Du, “Accurate decentralized
application identification via encrypted traffic analysis using graph neural
networks,” IEEE Trans. Inf. Forensics Secur., vol. 16, pp. 2367–2380, 2021.
[49] Z. Chen, G. Cheng, Z. Wei, D. Niu, and N. Fu, “Classify traffic
rather than flow: Versatile multi-flow encrypted traffic classification with
flow clustering,” IEEE Trans. Netw. Service Manag., vol. 21, no. 2,
pp. 1446–1466, Apr. 2024.

CHEN et al.: ULTIMATE ENCRYPTED TRAFFIC FEATURE ENGINEERING: HTTPS ENCRYPTED TRAFFIC CLASSIFICATION

[50] Y. Cao, Y. Feng, H. Wang, X. Xie, and S. K. Zhou, “Learning to sketch:
A neural approach to item frequency estimation in streaming data,”
IEEE Trans. Pattern Anal. Mach. Intell., vol. 46, no. 11, pp. 7136–7153,
Nov. 2024.
[51] A. Vaswani et al., “Attention is all you need,” in Proc. 31st Int. Conf.
Neural Inf. Process. Syst., Red Hook, NY, USA: Curran Associates Inc.,
2017, pp. 6000–6010.
[52] E. Horowicz, T. Shapira, and Y. Shavitt, “A few shots traffic classification
with mini-flowpic augmentations,” in Proc. 22nd ACM Internet Meas.
Conf., Nice, France, 2022, pp. 647–654, doi: 10.1145/3517745.3561436.
Zihan Chen (Member, IEEE) received the BS degree
in software engineering from Central South University in 2017, and the PhD degree in cyber security
from Southeast University in 2023. He is currently
working as a postdoc with the School of Cyber Science and Engineering at Southeast University. His
major research interests include cyber security, encrypted traffic classification, encrypted traffic feature
engineering, and deep learning. He is a Member of
CCF and works as a reviewer for multiple Journals
such as IEEE Transactions on Dependable and Secure
Computing, IEEE Internet of Things Journal, ESWA and the duty editor of the
Journal of Cyberspace.

Guang Cheng (Member, IEEE) received the BS degree in traffic engineering from Southeast University
in 1994, the MS degree in computer application from
the Hefei University of Technology in 2000, and the
PhD degree in computer network from Southeast University in 2003. He is a full professor with the School
of Cyber Science and Engineering, Southeast University, Nanjing, China. He has authored or coauthored
seven monographs and more than 100 technical papers, including top journals and top conferences. His
research interests include network security, network
measurement, and traffic behavior analysis. He is a senior member of CCF.
Dandan Niu (Student Member, IEEE) received the
BS degree in Internet of Things from Jiangnan University in 2021. She is currently working toward the
MS degree in cyberspace security with the School
of Cyber Science and Engineering, Southeast University. Her major research interests include cyber
security, encrypted traffic analysis.

1307

Yuyu Zhao (Member, IEEE) received the BS degree
in software engineering from the Nanjing University
of Science and Technology in 2016, and the MS
and PhD degrees in cyber security from Southeast
University, Nanjing, China, in 2019 and 2023, respectively. He is a currently a lecturer with the School of
Cyber Science and Engineering, Southeast University. His research interests include in-band telemetry,
blockchain, and network processors.

Yuyang Zhou (Member, IEEE) received the BS degree in electronic information engineering from the
Nanjing University of Science and Technology in
2016 and the PhD degree in cyberspace security from
Southeast University in 2021. He is currently working as a postdoc with the School of Cyber Science
and Engineering, Southeast University. His major research interests include moving target defense, DDoS
mitigation, security modeling, intrusion detection,
and Android malware detection. He has published in
some of the topmost journals and conferences like
IEEE Transactions on Information Forensics and Security, IEEE Transactions
on Industrial Informatics, and ACM Computing Classification System, and is
involved as reviewer and in technical program committees of several journals
and conferences in the field.

Shanqing Jiang (Member, IEEE) received the BS
degree in Internet of Things engineering from North
China Electric Power University in 2017 and the PhD
degree in cyber security from Southeast University in
2023. He is currently a research associate with Purple
Mountain Laboratories, Nanjing, China. His research
interests include SDN, future network architecture,
and network resilience.
PAPER_TEXT
