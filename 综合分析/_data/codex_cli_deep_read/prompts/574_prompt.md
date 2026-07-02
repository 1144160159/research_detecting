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
# [574] VPN-Encrypted Network Traffic Classification Using a Time-Series Approach
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
编号：574
题名：VPN-Encrypted Network Traffic Classification Using a Time-Series Approach
年份：2025
DOI：10.1109/tnsm.2025.3543903
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2025.3543903.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 16
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\574.txt
- 原始字符数：52867
- 本次发送字符数：52867
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 2, APRIL 2025

2225

VPN-Encrypted Network Traffic Classification
Using a Time-Series Approach
Jaidip Kotak , Idan Yankelev , Idan Bibi, Yuval Elovici , and Asaf Shabtai

Abstract—Network traffic classification provides value to organizations and Internet service providers (ISPs). The identification
of applications or services from network traffic enables organizations to better manage their business, and ISPs to offer
services to their users. Given the vast quantity of traffic flowing
in and out of organizations, it is impractical to write manual
signatures for traffic identification. The effectiveness of machine
learning (ML) in the identification of applications or services
from network traffic has been demonstrated. Even when network
traffic is encrypted, ML algorithms achieve high accuracy in the
task of traffic identification based on statistical information and
the packets’ headers and payloads. However, existing approaches
were shown to be ineffective for VPN-encrypted network traffic.
In this study, we propose a novel time-series based approach for
the identification of traffic/source applications on VPN-encrypted
traffic. We also demonstrate the broad applicability of our
proposed approach by evaluating its effectiveness on non-VPN
traffic that is encrypted, and on IoT traffic.
Index Terms—Network traffic classification, virtual private
networks (VPN), machine learning, encrypted traffic and cybersecurity.

I. I NTRODUCTION
MONG other changes in the past decade, today’s workfrom-home culture has played a role in shifting people
to online platforms, which has led to a dramatic increase in
the amount of Internet traffic. The number of Internet users
worldwide is currently around 4.9 billion; this means that
almost two-thirds of the world’s population is connected to
the Internet [1].
Due to online privacy campaigns and growing concern from
advertisers, Internet service providers (ISPs), and governments
regarding the disruption, manipulation, and monitoring of
Internet traffic, users’ awareness of privacy issues associated
with Internet use has grown [2], [3], [4], [5], [6], [7]. To
preserve privacy, circumvent censorship, and access geofiltered content, many users use virtual private network (VPN)
technology [8], [9], [10].
Given the increased volume of network traffic, there is
a need for service providers and organizations to perform
automatic network traffic classification (NTC) to infer the

A

Received 25 December 2023; revised 12 August 2024 and 22 November
2024; accepted 23 January 2025. Date of publication 20 February 2025;
date of current version 22 April 2025. The associate editor coordinating
the review of this article and approving it for publication was Y. Diao.
(Corresponding author: Jaidip Kotak.)
The authors are with the Department of Software and Information Systems
Engineering, Ben-Gurion University of the Negev, Be’er Sheva 84105, Israel
(e-mail: jaidip@post.bgu.ac.il).
Digital Object Identifier 10.1109/TNSM.2025.3543903

applications or the type of applications, by analyzing the
packets. This capability is extremely important for organizations and network service providers, since it (1) provides
effective security (e.g., detecting anomalous traffic or application behavior), and (2) guarantees network quality-of-service
(QoS) for specific applications (e.g., video streaming).
The main challenges faced when performing NTC are:
(1) the large volume of network traffic, (2) the evolving nature
of network traffic patterns due to user behavior and changes
in applications’ functionality, and (3) the use of technologies
like network address translation (NAT), internal proxies, and
VPNs.
The two existing network traffic classification approaches—
feature-based and rule-based methods (statistical and
behavioral)—are not directly applicable to VPN-encrypted
traffic. The limitation of the feature-based approach is based
on the network flow, from which it identifies the right
features and preprocesses them for the machine learning
(ML) model [11], [12]; it is not possible to segregate
different network flows in VPN-encrypted traffic, as all of
the traffic is within a single VPN-encrypted tunnel and is
therefore a single network flow. The rule-based approach relies
mainly on the port number and the header fields of network
communication [13], [14]. However, as mentioned, in VPNencrypted traffic there is a single network flow and the header
information is not visible due to the encryption provided by the
VPN. Therefore, these approaches are not directly applicable
to VPN-encrypted network traffic classification (V-NTC).
Our Method: We propose a method for V-NTC, which is
based on the sliding window of a time series. In this method,
features from the packets are derived every second, and the
features of m seconds are appended to form a single training
or testing instance, where m is the window length. Then, to
form the next data instance, we slide by one second (i.e., 2
to m+1 seconds) and construct a second data instance. The
InceptionTime model [15] was used to classify the time-series
based instances.
Evaluation: Initially, we planned to use the publicly
available VPN traffic dataset – ISCXVPN2016 [16] –
to evaluate the proposed method for VPN-encrypted traffic classification. However, since we found a discrepancy
in this dataset (described in detail in Section II-B),
we formed our own dataset that includes traffic from
three geographical locations. This dataset is available
at https://zenodo.org/records/13301379. We evaluated our
approach on the entire dataset and for each geographical location, on both the classification task at the category level (e.g.,

c 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
1932-4537 
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

2226

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 2, APRIL 2025

streaming, chat), and the application level (e.g., YouTube,
Vimeo). An accuracy of 93-95% was obtained for categorylevel classification for each location and for the combined
traffic from all three locations. Accuracy ranging from 84%
to 91% was obtained for application-level classification for
each location and when combining the traffic from all three
locations. To demonstrate our method’s generic nature on nonVPN traffic, we evaluated it on the ISCXVPN2016 dataset and
a subset of the IoTTrace [17] dataset.
Contribution: The contributions of our research are as
follows:
• To the best of our knowledge, we are the first to classify
and identify VPN-encrypted traffic using a time-series
approach.
• The proposed approach is generic in nature, i.e., it is
applicable to VPN-encrypted traffic, non-VPN traffic, and
IoT device type classification, as demonstrated in our
evaluation on different datasets.
• The proposed approach can be used on network traffic
originating from different geographical locations (using
a VPN).
• We created a dataset of VPN-encrypted and non-VPN
traffic from three different geographical locations which
contains more unique applications than existing datasets
and will make this dataset available to the research
community.
The remainder of this paper is organized as follows.
Section II reviews the related work on VPN traffic classification and the existing public VPN dataset. Section III
describes the characteristics of the VPN-encrypted traffic
dataset, the network setup during data generation, and the
data generation process. Section IV outlines the methods
used, including data preprocessing, feature construction, and
the classification model. Section V presents the experiments
conducted and their results. Section VI discusses the findings,
limitations, and potential areas for future research. Finally,
Section VII concludes the paper by summarizing our findings
and contributions.
II. R ELATED W ORK
A. Network Traffic Classification
In the past, network traffic detection was performed based
on the port numbers used in network communication. The
same port numbers were used by all the applications that
were communicating on the same protocol [18]. Therefore,
it was easy to identify the network traffic, as mentioned
in [19], [20], [21]. Later, payload-based deep packet inspection (DPI) tools such as PACE, OpenDPI, L7-filter, nDPI and
Cisco’s NBAR were used to extract features from packets’
payloads; and then, simple ML models (such as decision tree
(DT), random forest (RF), and k-nearest neighbors (KNN))
capable of bifurcating between the different traffic groups and
classifying the packets based on the features were used, as
mentioned in [22], [23], [24], [25], [26], [27].
However, as the Internet evolved, the above-mentioned
methods have become obsolete, since most developers today
do not follow a specific standard in selecting the port number

for their application’s communication. Even DPI tools are
irrelevant, as most of the traffic is encrypted or VPN-encrypted
these days.
Due to the lack of privacy, technologies such as NAT,
internal proxies, and VPNs were established to allow companies, organizations, and individuals to use a network without
revealing any identifying data; as a result, new methods
capable of performing encrypted NTC with high accuracy
without compromising users’ privacy are needed. Advances in
the field led to the development of novel approaches based
on network traffic flow features, well suited to the data’s
encrypted nature, as well as the use of deep neural network
methods which allow the computer to find its own weights in
order to correctly classify the traffic classes.
In [28], the authors proposed a framework that employs a
stacked autoencoder (SAE) and convolution neural network
(CNN) to classify network traffic. To train the neural networks,
they performed a preprocessing phase in which the Ethernet
header and uniformed protocol header length were removed,
and the packets’ bits were transformed to bytes; afterward,
they filtered out all non-application data-related packets, such
as packets with ACK/SYN/FIN flags or DNS queries. The
framework achieved 98% accuracy in the application identification task and 93% in the traffic categorization task by using
the CNN network as the classification model. Similar work has
been performed by [30], [31], [34], [39], [41] and [40] who
utilized payload and other header information, applying deep
learning models like a CNN, 1D-CNN & bidirectional gated
recurrent unit (BiGRU), bidirectional encoder representation
Transformer (BERT) & CNN, three-layer multilayer perception (MLP), CNN, and ensemble long short-term memory
(LSTM), respectively, and achieving results in a similar range.
However, the major limitation of these approaches is that they
rely on the presence of clear text information in encrypted
traffic, particularly with the TLS protocol, where initial negotiation happens in clear text. In real VPN traffic, however, this
information is encrypted and hidden within the VPN tunnel,
making these methods bound to fail.
In addition to deep learning models, several studies have
leveraged machine learning algorithms for classifying VPN
and non-VPN network traffic. For instance, [32] proposed a
method that utilized time-related statistical features generated
by ISCXFlowMeter/CICFlowMeter, such as flow duration,
flow bytes per second, max active time, max biat (backward
inter-arrival time), max flowiat (flow inter-arrival time), mean
biat, min active time, min biat, and std active time (standard
deviation of active time). These features were then used to
train a RF model, achieving over 95% accuracy for categorylevel VPN traffic classification.
ISCXFlowMeter/CICFlowMeter is a network traffic flow
generator and analyzer that processes packet capture (PCAP)
files to generate bidirectional flows. Each flow is identified
based on the direction of the first packet (source to destination
or destination to source) and enriched with over 80 statistical
features, including flow duration, packet counts, byte counts,
and packet lengths for both forward and backward directions.
These features are frequently used in network traffic classification tasks, enabling the detection and differentiation of

KOTAK et al.: VPN-ENCRYPTED NETWORK TRAFFIC CLASSIFICATION USING A TIME-SERIES APPROACH

2227

TABLE I
S UMMARY OF E NCRYPTED T RAFFIC C LASSIFICATION A PPROACHES

various traffic types. However, it is important to note that these
features rely on the ability to aggregate the packets by flows.
This dependency makes such methods unsuitable with datasets
where multiple flows are encapsulated within a VPN tunnel,
appearing as a single flow.
Similarly, studies like [35] and [37] have employed features
derived from ISCXFlowMeter with machine learning models such as neural networks (NN), support vector machines
(SVM), and boosting algorithms (e.g., XGBoost, LightGBM,
AdaBoost), achieving comparable results.
The limitation of such studies is that ISCXFlowMeter/
CICFlowmeter assume that traffic can be segmented into flow
records using 5-tuple values (source IP, destination IP, source
port, destination port, and protocol). However, this assumption
does not hold true for real VPN traffic, where traffic flows are
often merged and encrypted in the VPN tunnel. As a result,
these methods are not directly applicable to real VPN traffic
scenarios.
Additionally, studies such as [33] and [36] utilized only
the packet sizes and inter-arrival times for classification,
employing LSTM & ordinary differential equation networks
(ODENet) and adversarial auto-encoder (AAE) & deep support
vector data description (DSVDD), respectively. However, these
approaches assume that traffic can be neatly segmented into

flows, which limits their applicability to real-world VPN
scenarios where this assumption does not hold true.
In contrast, Vu et al., [29] developed a time-series feature
extraction method consisting of a feature engineering method,
which is used to extract significant attributes of the encrypted
network traffic behavior by analyzing the time series of
receiving packets, and a deep learning-based method which
is used to exploit the correlation of time-series data samples
of the encrypted network applications. The authors used the
newly generated time-series features to train a model based on
the LSTM recurrent neural network to learn the features in the
time-series samples. The method’s performance surpassed that
of methods proposed in prior studies, obtaining an accuracy
of 98.17% while reducing the number of features used to
55; in contrast, 1,500 features were required in the model
proposed in [28]. The method was primarily tested on category
classification instead of application classification.
Table I summarizes recent work on encrypted network
traffic classification. It highlights that most studies utilize the
ISCXVPN2016 dataset, which contains known discrepancies.
Additionally, many approaches either assume that traffic can
be segmented into multiple flows or rely on application
payload content, neither of which is applicable to real VPN
traffic scenarios.

2228

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 2, APRIL 2025

TABLE II
C HARACTERISTICS OF O UR DATASET

B. Publicly Available Network Traffic Dataset
In most prior works, the ISCXVPN2016 dataset (VPNnonVPN dataset) was used to demonstrate the effectiveness
of the proposed NTC and V-NTC approaches [42], [43], [44],
[45], [46], [47]. However, on taking a more in-depth look
at the content of the dataset’s files, we made the following
observations:
• In some PCAP files, the content of the packets is in clear
text.
• The port numbers used are well-known port numbers for
different services.
• In some PCAP files, the protocols are TLS, HTTP, etc.
• Certain structures of the protocol (like HTML pages for
the HTTP protocol) are present in the clear text.
• On resolving the DNS name for the IP address, we found
that the IP address belongs to the server of well-known
applications.
• There are multiple flow records.
The above observations derived from the VPN-encrypted
traffic PCAP files suggest that the dataset does not contain
VPN-encrypted data (see also A). Ideally, in VPN-encrypted
data, we would see one (or a few) flow records for the VPN
tunnel(s), which might not use well-known ports. Also, due to
the presence of the VPN tunnel in real VPN-encrypted traffic,
network traffic should not contain the structure/header of any
protocol; however, in this dataset, protocols are detected based
on the structure/header.
Since there is a need for a VPN-encrypted dataset on which
NTC and V-NTC approaches can be tested, to evaluate the
method proposed in this study, we created our own dataset,
details of which are provided in Section III.
III. E NCRYPTED T RAFFIC DATASET
In this section, we describe the characteristics of our dataset
and provide an overview of how it was created. We collected
25 GB of labeled network traffic and approximately 76.5 hours
of packet capture from our four categories of traffic (chat,
video, file transfer, and video conferencing), containing both
VPN-encrypted and non-VPN-encrypted traffic flows. Data

was collected using one VPN client, which was configured
for three geographical locations (Canada, England, and Japan).
The characteristics of our dataset are presented in Table II.
The categories are based on those used in [16] with some
exceptions (like P2P, Web browsing).
A. Dataset Characteristics
The three geographical locations (Europe, North America,
and Asia) were used to observe the impact that location has on
the performance of our approach. Traffic from each application
was captured for 1.5 hours, thus the recorded PCAP files
in the dataset are nearly uniform (+/- 5-10 minutes). The
first difference observed in the data from the three locations
was in the amount of traffic recorded (in GB) for a fixed
period of time (1.5 hours). When using a VPN client for
the geographical location of Canada, 10 GB of traffic was
captured, whereas 7 GB was captured for England, and 8 GB
was captured for Japan.
After capturing the traffic, the PCAP files were cleaned,
removing the background noise, and segregated so they only
contained the traffic flow from the VPN tunnel; this way, the
dataset can be used in future research without the need to clean
the files again.
B. Network Setup
To produce the dataset, we used VirtualBox to create a
virtual machine on top of the host computer. Wireshark was
used on both the virtual machine and the host computer to
capture non-VPN and VPN-encrypted network traffic, respectively. OpenVPN was used on the host computer as the VPN
client with configurations for three different countries: Japan,
Canada, and England, i.e., the VPN servers were located in
those locations (while the VPN client was located in Israel).
Firefox was used for all of the applications requiring a Web
browser. VPN-encrypted traffic was captured between the
VPN client (host computer) and the VPN server. In addition,
non-VPN-encrypted traffic was captured between the virtual
machine and the application layer.

KOTAK et al.: VPN-ENCRYPTED NETWORK TRAFFIC CLASSIFICATION USING A TIME-SERIES APPROACH

Fig. 1.

2229

Comparison of generic machine learning systems and VPN-encrypted traffic classification framework.

C. Data Generation
The dataset was made up of traffic from each application
mentioned in Table II. Wireshark was used to create a single
1.5 hour PCAP file for each application. The traffic in
the video category, which consists of Vimeo, Netflix, and
YouTube, was produced by members of the research team
as they watched videos on each platform. The traffic in the
chat category, which consists of Skype, Facebook, Google
Hangouts, WhatsApp, and Telegram, was created by team
members as they chatted with one another on each platform.
The traffic in the video conferencing category, which consists
of Skype, Google Meet, Zoom, and Microsoft Teams, was
generated by team members as they participated in conference
calls on each platform. For the file transfer category, which
consists of WhatsApp, Dropbox, Google Drive, Skype, and
Telegram, we uploaded and downloaded files of various sizes
on the different applications and captured the traffic.
IV. M ETHODS
A comparison between a generic machine learning system
and our VPN-encrypted traffic classification approach is provided in Fig. 1, which highlights the process flow from data
capture to output analysis; shows how network traffic is
captured, preprocessed, modeled, and analyzed to determine
application or category probabilities; and aids in network
device management. The subsections that follow provide
detailed explanations of each stage: data preprocessing, feature
construction, and classification model.
A. Data Preprocessing
From the PCAP file of each application, we first filtered
out the single largest flow (by size) which contains the
application’s VPN-encrypted traffic. By performing this step
we eliminated any unwanted traffic (noise) generated by other
applications running in the background. The published dataset
will consist of these cleaned PCAP files. After obtaining
the single VPN-encrypted flow for each application, it was
processed using Tshark1 to extract fields like the timestamp,
1 https://tshark.dev

Fig. 2.

Data instances construction using sliding window.

source and destination IP address, source and destination port
number, and packet size of each packet. This process results
in a raw feature file for each application.
B. Feature Construction
Within each feature file, the packets are grouped, per
second; then the features listed in Table III are created for
each group. A one-second sliding window is used to provide
high granularity and capture real-time variations in traffic,
which is essential for timely detection and response. Statistical
features were also included, as they were shown to be effective
for online network intrusion detection in the paper presenting
Kitsune [48]. We focus on three primary series of features:
time delta, packet sizes, and accumulated directional packet
sizes, in addition to some other features. The time delta
series involves the generation of statistical features based on
the time difference ratios between consecutive packets. For
the packet sizes series, we create statistical features related
to the size ratios between consecutive packets. In contrast,
the accumulated directional packet sizes series involves the
construction of statistical features that account for the ratio of
cumulative packet size between consecutive packets, considering the direction of each packet. This comprehensive approach
ensures that we capture both instantaneous and cumulative
behaviors in packet transmission (refer to Algorithm 1 in the
Appendix for the pseudocode).
Then we applied the concept of the sliding window, wherein
a single instance is created by appending n features of m
seconds (i.e., the window length) which results in a single
instance with the shape of 1 x n x m (refer Fig. 2 where

2230

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 2, APRIL 2025

TABLE III
D ETAILED D ESCRIPTIONS OF F EATURES , I NCLUDING T HEIR S ERIES , S UB -S ERIES , AND R ELEVANCE TO VPN T RAFFIC

the window length is five). Table II contains the number
of data instances (column Total Instances) after the features
were constructed. We also performed standardization (i.e.,

Z-score normalization) on the entire dataset, transforming the
data so that it has a mean of zero and a standard deviation
of one. Our aim in performing this feature construction

KOTAK et al.: VPN-ENCRYPTED NETWORK TRAFFIC CLASSIFICATION USING A TIME-SERIES APPROACH

2231

TABLE IV
S UMMARY OF THE E XPERIMENTS P ERFORMED

process was to convert the network traffic data to time-series
data.
C. Classification Model
For the classification of the VPN-encrypted network traffic (that was converted to time-series data), we used the
InceptionTime model [15]. This model is an inception-based
network [49] that applies several convolutions with filters of
various lengths. It consists of an ensemble of five different
inception networks that are initialized randomly.
Inception network classifiers contain two different residual
blocks. For the inception network, each block is comprised
of three inception modules rather than traditional fully convolutional layers. Each inception module applies convolutions
with lengths of 10, 20, and 40, with a max pooling operation
followed by a bottleneck layer, and concatenates the outputs.
Each residual block’s input is transferred via a shortcut linear
connection so it can be added to the next block’s input, thus
mitigating the vanishing gradient problem by allowing a direct
flow of the gradient [50]. The padding chosen aims to maintain
the dimensionality of the time series after the convolutions.
After the residual blocks, a global average pooling (GAP)
layer is employed which averages the output (in the form
of multivariate time series) over the whole time dimension.
The network is comprised of six inception modules stacked
sequentially within each residual block. Each module includes
a bottleneck layer to reduce dimensionality, which is followed
by multiple convolutional layers with different filter lengths.
Then, a final traditional fully connected softmax layer is used,
with the number of neurons equal to the number of classes
in the dataset. Fig. 3 depicts the architecture of an inception
network in which six inception modules are stacked one after
the other. The inception modules use multiple filters of varying
lengths, specifically three sets of filters each with lengths of
10, 20, and 40. For more details about the model, please refer
to [15].
V. E XPERIMENTS AND R ESULTS
Table IV provides a summary of the experiments performed.
We divided the data into training and test sets for each

Fig. 3.

Inception network for time-series classification [49].

Fig. 4.

Data split for 5-fold cross-validation in time-series analysis.

application, as shown in Fig. 4, for five folds, where 80%
of the dataset was used for training, and 20% was used for
testing. We divided the training and test set in a sequential
manner to avoid leaking any information resulting from the
features’ construction (described in Section IV-B) to the test
set. We used a batch size of 64, and training was performed
for 10 epochs. The metrics used in our evaluation are the F1score and accuracy. Note that as shown in Table III, feature
numbers 44-47 will not have any impact in experiments 1-4,
because in VPN traffic, the unique source and destination IP
and the unique source and destination port will remain the
same across all applications. Values for these features will
differ in experiments 5-6 and therefore will have an impact on
the performance in those cases.
Experiments 1-2: Classification of Network Traffic at the
Category- and Application-Level for the Entire Dataset
In these two experiments, traffic from all three geographical
locations was combined. In the first experiment, there were
four labels, i.e., four application categories. The classification
accuracy and F1-score results are presented in Table V; as
can be seen, when the length of the sliding window was

2232

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 2, APRIL 2025

TABLE V
E XPERIMENT 1 - P ERFORMANCE OF D IFFERENT A PPLICATIONS FOR C ATEGORY-L EVEL C LASSIFICATION
W ITH A S LIDING W INDOW L ENGTH OF 60 S ECONDS

TABLE VI
E XPERIMENT 2 - P ERFORMANCE OF D IFFERENT A PPLICATIONS FOR A PPLICATION -L EVEL C LASSIFICATION
W ITH A S LIDING W INDOW L ENGTH OF 60 S ECONDS

Fig. 5.

Performance of the models trained on the entire dataset for various sliding window lengths (Y-axis).

60 seconds, the overall accuracy obtained was 93.80%. In the
second experiment, there were 17 labels, i.e., one for each
application. The classification accuracy and F1-score results
are presented in Table VI; as can be seen, when the length
of the sliding window was 60 seconds, the overall accuracy
obtained was 86.50%. Note that to obtain a granular view
of the performance, we examined each application’s test data

against the model; the results can be found in Tables V and VI.
The results for smaller sized sliding windows are presented in
Fig. 5; results for longer sized sliding windows are presented
in Fig. 8 in the Appendix. As can be seen, larger sliding
windows, such as 120 seconds, result in minimal improvement
in accuracy while significantly increasing latency. Based on
this analysis, a 60-second sliding window was chosen as it

KOTAK et al.: VPN-ENCRYPTED NETWORK TRAFFIC CLASSIFICATION USING A TIME-SERIES APPROACH

2233

TABLE VII
E XPERIMENT 3 - P ERFORMANCE OF D IFFERENT A PPLICATIONS FOR E ACH C OUNTRY FOR C ATEGORY-L EVEL C LASSIFICATION
W ITH A S LIDING W INDOW L ENGTH OF 60 S ECONDS

TABLE VIII
E XPERIMENT 4 - P ERFORMANCE OF D IFFERENT A PPLICATIONS FOR E ACH C OUNTRY FOR A PPLICATION -L EVEL C LASSIFICATION FOR A
S LIDING W INDOW L ENGTH OF 60 S ECONDS

strikes a balance between capturing sufficient data for accurate
classification and maintaining low latency for practical realworld application. It can be seen that poorer accuracy was
obtained for the Whatsapp_files application at the category
level (see Table V) with the combined data from all three
countries; this could stem from the different sizes of the
files that were used when capturing the network traffic.
After removing the Whatsapp_files application’s data from the
training and test samples, the overall category-level accuracy
results improved from 93.80% to 96.20%, and the overall
application-level accuracy results improved from 86.50% to
88.60%.
The experiments were conducted on a system with the
following configuration: a single NVIDIA TITAN X (Pascal)
GPU, 6 CPU cores, 125.21 GB of RAM, and 12.0 GB of GPU
memory. The average CPU utilization during the experiments
was 8.37%, the average GPU utilization was 4.69%, and the

Fig. 6.

Comparative analysis of various models for experiment 1-2.

average RAM utilization was 11.56%. The average prediction
time for 1,000 instances was 0.0639 seconds, and the training
time per epoch was approximately 38 seconds.

2234

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 2, APRIL 2025

TABLE IX
C HARACTERISTICS OF THE ISCXVPN2016 DATASET S UBSET

TABLE X
E XPERIMENTS 5 & 6 - P ERFORMANCE OF D IFFERENT A PPLICATIONS FOR C ATEGORY- AND A PPLICATION -L EVEL C LASSIFICATION

The bar chart in Fig. 6 compares our proposed method’s
performance with that of the method of Vu et al. [29] and
a method with baseline LSTM model. As can be seen,
our proposed method outperforms the others on all metrics.
The significant difference in application-level performance
indicates that our method captures granular patterns more
effectively than the other two method, reflecting its superior
capability in detailed pattern recognition.

The baseline LSTM model (denoted as LSTM 80 40 20)
used for comparison consists of a sequential architecture with
an 80-neuron LSTM layer, followed by a 40-neuron LSTM
layer, and a 20-neuron dense layer. This architecture also
includes three dropout layers, each with a dropout rate of
0.5, and uses the features proposed in this paper. The worst
performance of the three was obtained by the model of
Vu et al. [29], as depicted in the graph.

KOTAK et al.: VPN-ENCRYPTED NETWORK TRAFFIC CLASSIFICATION USING A TIME-SERIES APPROACH

Fig. 7.

2235

Performance of the models trained on country-specific data for various sliding window lengths (Y-axis).
TABLE XI
E XPERIMENT 7 - P ERFORMANCE ON I OT DATA FOR S LIDING W INDOWS OF VARIOUS L ENGTHS (O CTOBER 23)

TABLE XII
E XPERIMENT 7 - P ERFORMANCE ON I OT DATA FOR S LIDING W INDOWS OF VARIOUS L ENGTHS (O CTOBER 24)

Fig. 8.

Performance of the models trained on the entire dataset for prolonged sliding window lengths (Y-axis).

Experiments 3-4: Classification of Network Traffic at the
Category- and Application-Level for Each Country
In these two experiments, models were trained separately
for each country, i.e., trained and tested on one country. In the
third experiment, there were four labels, i.e., four application

categories. The classification accuracy and F1-score results
for the three models trained respectively on traffic from
Japan, Canada, and England are presented in Table VII. In
the fourth experiment, there were 17 labels, i.e., one for each
application. The classification accuracy and F1-score results

2236

Fig. 9.

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 2, APRIL 2025

HTTP protocol tags are visible in the payload of data.

for the three models trained on traffic from Japan, Canada, and
England respectively are presented in Table VIII. The results
for smaller sliding windows are presented in Fig. 7. As can be
seen, in most cases the accuracy and F1-score results improve
as the size of the sliding window increases.
Experiments 5-6: Classification of Network Traffic at the
Category- and Application-Level for Non-VPN-Encrypted
Traffic
In these two experiments, a subset of non-VPN traffic from
the ISCXVPN2016 datset was used; the characteristics of
the subset are presented in Table IX. In both experiments,
we considered files in which the traffic was present for at
least 300 seconds, i.e., at least five minutes of recording.
Please note: In these two experiments, as there were multiple
files per application, we calculated weighted accuracy. Also,
as mentioned earlier, we use all the features mentioned in
Table III in these experiments.

In the fifth experiment, there were six labels, i.e., six
application categories. The classification accuracy and F1score results are presented in Table X; as can be seen, the
overall accuracy was 97.30% when the length of the sliding
window was 60 seconds. As seen in the table, the accuracy
of our approach at the category level was lower for Spotify;
this could be due to Spotify’s streaming format (audio) which
differs from that of the other recorded streaming services
(video).
In the sixth experiment, there were 21 labels, i.e., one
for each application. The classification accuracy and F1-score
results are presented in Table X; as can be seen, the overall
accuracy was 93.40% when the length of the sliding window
was 60 seconds.
To see the impact of the last four features (i.e., feature
numbers 44 to 47), we reran these two experiments without those four features and obtained 95.5% (compared to
97.30%) accuracy in category classification (experiment five)

KOTAK et al.: VPN-ENCRYPTED NETWORK TRAFFIC CLASSIFICATION USING A TIME-SERIES APPROACH

Fig. 10.

2237

Syntax of the FTP protocol is visible in the payload of data.

and 83.60% (compared to 93.40%) accuracy in application
classification (experiment six). This shows that applicationlevel accuracy drops significantly after removing the last four
features, which shows the major contribution of those features.
Note that to obtain a granular view of the performance, we
examined each application’s test data against the model; the
results can be found in Table X.
We also represent the top 10 features for each experiment
in the Appendix.
VI. D ISCUSSION
Prior research [16], [29], [31] only demonstrated the
proposed method’s effectiveness on the existing dataset, which
has limitations. Here we produced a new balanced dataset with

data from a larger number of applications and from different
geographical locations, which is better suited to today’s applications, and used it to demonstrate the effectiveness of our
proposed approach. To demonstrate the generic and universal
nature of our approach, we also assessed our approach’s ability
to identify applications in non-VPN-encrypted network traffic
(experiments 5 & 6) as well as IoT devices; the results of
this experiment (experiment 7) are presented at the end of this
section).
We used a sliding window time-series approach which
enables our method to identity any type of traffic with less data
than that needed by other methods, i.e., the number of seconds
of traffic needed is equal to the length of the sliding window.
In other approaches one might need to wait for the flow’s

2238

Fig. 11.

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 2, APRIL 2025

PCAP shows multiple flows with well-known domain names and ports.

TABLE XIII
M OST I MPORTANT F EATURES IN E XPERIMENT 1

TABLE XIV
M OST I MPORTANT F EATURES IN E XPERIMENT 2

completion or for a certain number of packets to be exchanged,
which can often be time consuming. Our aim in proposing this
approach was to provide a time-series-based approach which
is generic in nature and can be applied to different network
scenarios, irrespective of the domain (e.g., IoT and computer
network), protocol (e.g., TCP and UDP), and the type of
encryption (e.g., VPN-encrypted, TLS-encrypted, and nonencrypted). As our approach differs from existing approaches
in that it is based on time series, we could not directly
compare the methods’ accuracy in our performance evaluation;

in existing flow-based approaches if there are 10 flows in the
traffic there will be 10 data instances, whereas in our approach,
the number of data instances can vary based on the time;
therefore, we were unable to compare the performance of our
approach directly with the performance of existing methods.
However, the accuracy reported in this paper is comparable or
better than the accuracy obtained by other methods in most of
the examined scenarios.

KOTAK et al.: VPN-ENCRYPTED NETWORK TRAFFIC CLASSIFICATION USING A TIME-SERIES APPROACH

TABLE XV
M OST I MPORTANT F EATURES IN E XPERIMENT 3 (JAPAN )

2239

TABLE XVII
M OST I MPORTANT F EATURES IN E XPERIMENT 3 (C ANADA )

TABLE XVIII
M OST I MPORTANT F EATURES IN E XPERIMENT 4 (JAPAN )

TABLE XVI
M OST I MPORTANT F EATURES IN E XPERIMENT 3 (E NGLAND )

Experiment 7: Classification of IoT Device Type
In this experiment, we used a subset of the IoTTrace [17]
dataset (specifically, traffic from October 23 and 24). We took
into account IoT devices whose network traffic lasted for more
than 3000 seconds (i.e., 50 minutes) to train two models (each
model was trained for a day). We used 8000 seconds of traffic
from each IoT device in the experiment. We were unable to
use the entire dataset, because the data was not continuous,
as is needed for training in our approach. However, our aim
was only to perform a proof of concept demonstrating the
applicability of our approach on a different type of dataset.
The results of the two models trained and tested on traffic

from October 23 and 24 are presented in Tables XI and XII
respectively. In this experiment we removed the features
(for example, fw_1250_packets) that had a standard deviation
value of zero, since they had no impact on the performance
and created an error (division by zero) when performing
standardization. Also, as mentioned earlier we included the
last four features mentioned in Table III in this experiment.
We note that although we used two different Netatmo devices,
the model was able to bifurcate their traffic correctly despite
both devices coming from the same manufacturer.
To see the impact of the last four features (i.e., feature
numbers 44 to 47), we reran this experiment for a sliding
window of 60 seconds without those four features and obtained
97.80% (compared to 97.80%) and 98.90% (compared to
99.80%) accuracy for the October 23 and October 24 datasets
respectively. This shows that removing the last four features
had no, or very minimal, impact on performance in this case.

2240

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 2, APRIL 2025

TABLE XIX
M OST I MPORTANT F EATURES IN E XPERIMENT 4 (E NGLAND )

TABLE XX
M OST I MPORTANT F EATURES IN E XPERIMENT 4 (C ANADA )

TABLE XXI
M OST I MPORTANT F EATURES IN E XPERIMENT 5

VII. C ONCLUSION
In this paper, we proposed a time-series-based approach
for the classification of VPN-encrypted network traffic at the

TABLE XXII
M OST I MPORTANT F EATURES IN E XPERIMENT 6

TABLE XXIII
M OST I MPORTANT F EATURES IN E XPERIMENT 7 (O CTOBER 23)

TABLE XXIV
M OST I MPORTANT F EATURES IN E XPERIMENT 7 (O CTOBER 24)

application- and category-levels. To evaluate our approach we
created a new dataset that consists of the traffic of different applications captured from three different geographical

KOTAK et al.: VPN-ENCRYPTED NETWORK TRAFFIC CLASSIFICATION USING A TIME-SERIES APPROACH

Algorithm 1 Feature Extraction
1: Input:
• TSV_file: TSV file containing parsed packet data
• window_length: List of time window lengths in
seconds (e.g. 30, 40, 50, 60 etc.) for feature extraction
2: Output:
• features_df: Dataframe containing extracted features
3: Algorithm:
4: Load parsed packet data from TSV file into dataframe
5: Determine packet direction based on source port
6: Initialize an empty list for statistics
7: for each time sample in window_length do
8:
Extract data sample within the specified time window
from dataframe
9:
Compute time delta features:
•
Bidirectional delta ratios between consecutive packbi ) = Δtin,i
ets: (rΔt
i
Δtout,i+1
•
Ingoing delta ratios between consecutive packets:
in ) = Δtin,i
(rΔt
i
Δtin,i+1
•
Outgoing delta ratios between consecutive packets:
out ) = Δtout,i
(rΔt
i
Δtout,i+1
10:
Compute packet size features:
•
Bidirectional size ratios between consecutive packets:
bi ) = sizein,i
(rsize
i
sizeout,i+1
•
Ingoing size ratios between consecutive packets:
in ) = sizein,i
(rsize
i
sizein,i+1
•
Outgoing size ratios between consecutive packets:
out ) = sizeout,i
(rsize
i
sizeout,i+1
11:
Compute accumulated packet size features:
•
Accumulated i bidirectional
size
ratios:
j =1 sizein,j
bi

(r
)
=
i+1
size i
•

Accumulated 
in
(r

•

size )i =

j =1 sizeout,j

ingoing

size

ratios:

outgoing

size

ratios:

i
j =1 sizein,j
i+1
j =1 sizein,j

Accumulated 

i
out ) = j =1 sizeout,j
(r
i+1
size i
sizeout,j
j =1

Compute additional features
13:
Append all computed features to the statistics list
14: end for
15: Convert the statistics list into a new dataframe (features_df)
16: Return features_df
12:

locations. Such a dataset is needed by the research community,
since we found that the existing dataset has several limitations.
We also demonstrated the generic nature of the proposed
approach by evaluating it in several other scenarios, such as
classification of non-VPN-encrypted traffic and IoT device
type. It should also be noted that along with organizations and
ISPs, methods of this type can also be used by adversaries for
reconnaissance of their targets. In future research, we plan to
apply our approach in scenarios where there is network traffic
flowing simultaneously from different applications within the
same VPN tunnel. We also plan to train our approach on data

2241

from a particular country and test it against data from different
countries.
A PPENDIX
The tables below present the 10 most important features
for each experiment. The “Difference (%)” column in each
table represents the difference between the baseline validation
accuracy (with all features) and the new validation accuracy
(without the feature mentioned).
R EFERENCES
[1] Statista. “Topic: Internet usage worldwide.” [Online]. Available: https://
www.statista.com/topics/1145/internet-usage-worldwide/#topicHeader_
_wrapper
[2] R. Subramanian, “The growth of global Internet censorship and circumvention: A survey,” Commun. Int. Inf. Manag. Assoc., vol. 11, no. 2,
p. 6, 2011.
[3] F. Li, A. A. Niaki, D. Choffnes, P. Gill, and A. Mislove, “A largescale analysis of deployed traffic differentiation practices,” in Proc. ACM
Special Interest Group Data Commun., 2019, pp. 130–144.
[4] N. Weaver, C. Kreibich, and V. Paxson, “Redirecting DNS for Ads
and profit,” in Proc. USENIX Workshop Free Open Commun. Internet
(FOCI), 2011, p. 12.
[5] A. M. Kakhki et al., “Identifying traffic differentiation in mobile
networks,” in Proc. Internet Meas. Conf., 2015, pp. 239–251.
[6] T. Garrett, L. E. Setenareski, L. M. Peres, L. C. Bona, and E. P. Duarte,
“Monitoring network neutrality: A survey on traffic differentiation
detection,” IEEE Commun. Surveys Tuts., vol. 20, no. 3, pp. 2486–2517,
3rd Quart., 2018.
[7] R. S. Raman, L. Evdokimov, E. Wurstrow, J. A. Halderman, and
R. Ensafi, “Investigating large scale HTTPS interception in Kazakhstan,”
in Proc. ACM Internet Meas. Conf., 2020, pp. 125–132.
[8] M. T. Khan, J. DeBlasio, G. M. Voelker, A. C. Snoeren, C. Kanich, and
N. Vallina-Rodriguez, “An empirical analysis of the commercial VPN
ecosystem,” in Proc. Internet Meas. Conf., 2018, pp. 443–456.
[9] M. Ikram, N. Vallina-Rodriguez, S. Seneviratne, M. A. Kaafar, and
V. Paxson, “An analysis of the privacy and security risks of android
VPN permission-enabled APPs,” in Proc. Internet Meas. Conf., 2016,
pp. 349–364.
[10] T. Sharma and M. Bashir, “Privacy apps for smartphones: An assessment
of users’ preferences and limitations,” in Proc. Int. Conf. Human–
Comput. Interact., 2020, pp. 533–546.
[11] J. Zhang, X. Chen, Y. Xiang, W. Zhou, and J. Wu, “Robust
network traffic classification,” IEEE/ACM Trans. Netw., vol. 23, no. 4,
pp. 1257–1270, Aug. 2015.
[12] T. T. Nguyen and G. Armitage, “A survey of techniques for Internet
traffic classification using machine learning,” IEEE Commun. Surveys
Tuts., vol. 10, no. 4, pp. 56–76, 4th Quart., 2008.
[13] A. Callado et al., “A survey on Internet traffic identification,” IEEE
Commun. Surveys Tuts., vol. 11, no. 3, pp. 37–52, 3rd Quart., 2009.
[14] N. Al Khater and R. E. Overill, “Network traffic classification techniques
and challenges,” in Proc. IEEE 10th Int. Conf. Digit. Inf. Manag.
(ICDIM), 2015, pp. 43–48.
[15] H. I. Fawaz et al., “InceptionTime: Finding AlexNet for time series
classification,” Data Min. Knowl. Disc., vol. 34, no. 6, pp. 1936–1962,
2020.
[16] G. Draper-Gil, A. H. Lashkari, M. S. I. Mamun, and A. A. Ghorbani,
“Characterization of encrypted and VPN traffic using time-related,”
in Proc. 2nd Int. Conf. Inf. Syst. Security Privacy (ICISSP), 2016,
pp. 407–414.
[17] A. Sivanathan et al., “Classifying IoT devices in smart environments
using network traffic characteristics,” IEEE Trans. Mobile Comput.,
vol. 18, no. 8, pp. 1745–1759, Aug. 2018.
[18] “Service name and transport protocol port number registry.” 2019.
[Online]. Available: https://www.iana.org/assignments/service-namesport-numbers/service-names-port-numbers.xhtml?&amp;page=1
[19] P. Schneider, TCP/IP Traffic Classification Based on Port Numbers,
Harvard Univ., Cambridge, MA, USA, 1997.
[20] G. Cheng and S. Wang, “Traffic classification based on port connection
pattern,” in Proc. Int. Conf. Comput. Sci. Service Syst. (CSSS), 2011,
pp. 914–917.

2242

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 2, APRIL 2025

[21] Q. Zhang, Y. Ma, J. Wang, and X. Li, “UDP traffic classification using
most distinguished port,” in Proc. 16th Asia–Pac. Netw. Oper. Manag.
Symp., 2014, pp. 1–4.
[22] M. Finsterbusch, C. Richter, E. Rocha, J.-A. Muller, and K. Hanssgen,
“A survey of payload-based traffic classification approaches,” IEEE
Commun. Surveys Tuts., vol. 16, no. 2, pp. 1135–1156, 2nd Quart.,
2013.
[23] H.-K. Lim, J.-B. Kim, K. Kim, Y.-G. Hong, and Y.-H. Han, “Payloadbased traffic classification using multi-layer LSTM in software defined
networks,” Appl. Sci., vol. 9, no. 12, p. 2550, 2019. [Online]. Available:
https://www.mdpi.com/2076-3417/9/12/2550
[24] F. Risso, M. Baldi, O. Morandi, A. Baldini, and P. Monclus,
“Lightweight, payload-based traffic classification: An experimental evaluation,” in Proc. IEEE Int. Conf. Commun., 2008, pp. 5869–5875.
[25] Z. Fan and R. Liu, “Investigation of machine learning based network
traffic classification,” in Proc. Int. Symp. Wireless Commun. Syst.
(ISWCS), 2017, pp. 1–6.
[26] S. Özdel, Ç. Ateş, P. D. Ateş, M. Koca, and E. Anarım, “Payloadbased network traffic analysis for application classification and intrusion
detection,” in Proc. 30th Eur. Signal Process. Conf. (EUSIPCO), 2022,
pp. 638–642.
[27] J. Kotak and Y. Elovici, “IoT device identification using deep learning,”
in Proc. Comput. Intell. Security Inf. Syst. Conf., 2019, pp. 76–86.
[28] M. Lotfollahi, M. J. Siavoshani, R. S. H. Zade, and M. Saberian, “Deep
packet: A novel approach for encrypted traffic classification using deep
learning,” Soft Comput., vol. 24, no. 3, pp. 1999–2012, 2020.
[29] L. Vu et al., “Time series analysis for encrypted traffic classification: A
deep learning approach,” in Proc. IEEE 18th Int. Symp. Commun. Inf.
Technol. (ISCIT), 2018, pp. 121–126.
[30] S. Soleymanpour, H. Sadr, and M. N. Soleimandarabi, “CSCNN:
Cost-sensitive convolutional neural network for encrypted traffic classification,” Neural Process. Lett., vol. 53, no. 5, pp. 3497–3523, 2021.
[31] G. Aceto, D. Ciuonzo, A. Montieri, and A. Pescapé, “DISTILLER:
Encrypted traffic classification via multimodal multitask deep learning,”
J. Netw. Comput. Appl., vols. 183–184, Jun. 2021, Art. no. 102985.
[32] M. Al-Fayoumi, M. Al-Fawa’reh, and S. Nashwan, “VPN and nonVPN network traffic classification using time-related features,” Comput.
Materials Continua, vol. 72, no. 2, p. 12, 2022.
[33] S. Roy, T. Shapira, and Y. Shavitt, “Fast and lean encrypted Internet traffic classification,” Comput. Commun., vol. 186, pp. 166–173, Mar. 2022.
[34] Z. Shi, N. Luktarhan, Y. Song, and G. Tian, “BFCN: A novel classification method of encrypted traffic based on BERT and CNN,” Electronics,
vol. 12, no. 3, p. 516, 2023.
[35] S. Ramraj and G. Usha, “Hybrid feature learning framework for the
classification of encrypted network traffic,” Connection Sci., vol. 35,
no. 1, 2023, Art. no. 2197172.

[36] S. Lv, C. Wang, Z. Wang, S. Wang, B. Wang, and Y. Zhang, “AAEDSVDD: A one-class classification model for VPN traffic identification,”
Comput. Netw., vol. 236, Nov. 2023, Art. no. 109990.
[37] G. Abbas, U. Farooq, P. Singh, S. S. Khurana, and P. Singh, “Feature
engineering and ensemble learning-based classification of VPN and nonVPN-based network traffic over temporal features,” SN Comput. Sci.,
vol. 4, no. 5, p. 546, 2023.
[38] Z. Wang et al. “An effective real-time traffic classification method
using convolutional neural network.” 2023. [Online]. Available:
https://ouci.dntb.gov.ua/en/works/4ggEk2B4/
[39] Y. Xu, J. Cao, K. Song, Q. Xiang, and G. Cheng, “FastTraffic: A
lightweight method for encrypted traffic fast classification,” Comput.
Netw., vol. 235, Nov. 2023, Art. no. 109965.
[40] R. T. Elmaghraby, N. M. A. Aziem, M. A. Sobh, and A. M. Bahaa-Eldin,
“Encrypted network traffic classification based on machine learning,”
Ain Shams Eng. J., vol. 15, no. 2, 2024, Art. no. 102361.
[41] S. Soleymanpour, H. Sadr, and H. Beheshti, “An efficient deep learning
method for encrypted traffic classification on the Web,” in Proc. IEEE
6th Int. Conf. Web Res. (ICWR), 2020, pp. 209–216.
[42] A. Iliyasu and H. Deng, “Semi-supervised encrypted traffic classification
with deep convolutional generative adversarial networks,” IEEE Access,
vol. 8, pp. 118–126, 2019.
[43] R. Nigmatullin, A. Ivchenko, and S. Dorokhin, “Differentiation of
sliding rescaled ranges: New approach to encrypted and VPN traffic
detection,” in Proc. Int. Conf. Eng. Telecommun. (En&T), 2020, pp. 1–5.
[44] B. Appiah, A. Sackey, O.-A. Kwabena, J. B. Ansuura, and P. Buah,
“Fusion dilated CNN for encrypted Web traffic classification,” Int. J.
Netw. Security, vol. 24, pp. 733–740, Jul. 2022.
[45] D. Wei, F. Shi, and S. Dhelim, “A self-supervised learning model for
unknown internet traffic identification based on surge period,” Future
Internet, vol. 14, p. 289, Oct. 2022.
[46] M. Pathmaperuma, Y. Rahulamathavn, S. Dogan, and A. Kondoz, “Deep
learning for encrypted traffic classification and unknown data detection,”
Sensors, vol. 22, p. 7643, Oct. 2022.
[47] Y. Li, F. Wang, and S. Chen, “VPN traffic identification based on
tunneling protocol characteristics,” in Proc. IEEE CCET, Aug. 2022,
pp. 150–156.
[48] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “KitSune: An
ensemble of autoencoders for online network intrusion detection,” in
Proc. Netw. Distrib. Syst. Security Symp., 2018, pp. 1–8.
[49] C. Szegedy, S. Ioffe, V. Vanhoucke, and A. A. Alemi, “Inception-v4,
inception-ResNet and the impact of residual connections on learning,”
in Proc. 31st AAAI Conf. Artif. Intell., 2017, pp. 4278–4284.
[50] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for image
recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2016,
pp. 770–778.
PAPER_TEXT
