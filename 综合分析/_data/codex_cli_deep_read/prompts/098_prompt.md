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
# [098] An encrypted traffic classification method based on contrastive learning
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
编号：098
题名：An encrypted traffic classification method based on contrastive learning
年份：2022
DOI：10.1145/3571662.3571678
来源：Proceedings of the 8th International Conference on Communication and Information Processing
PDF：paper/10.1145_3571662.3571678.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 11
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\098.txt
- 原始字符数：21651
- 本次发送字符数：21651
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
An encrypted traffic classification method based on contrastive
learning
siyuan tian

Yating Gao

Guoquan Yuan

Beijing University of Posts and
Telecommunications

State Grid Information &
Telecommunication Branch, Beijing
100761, China

Information & Telecommunication
Branch, State Grid Jiangsu Electric
Power Co. Ltd, Nanjing, China

Ru ZHANG∗

Jinmeng Zhao

Song Zhang

Beijing University of Posts and
Telecommunications

State Grid Information &
Telecommunication Branch, Beijing
100761, China

Information & Telecommunication
Branch, State Grid Jiangsu Electric
Power Co. Ltd, Nanjing, China

ABSTRACT
Network traffic classification has become an important part of
network management, which is conducive to realizing intelligent
network operation and maintenance, improving network quality
of service (QoS), and ensuring network security. With the rapid
development of various applications and protocols, more and more
encrypted traffic appears in the network. Due to the loss of semantic
information after traffic encryption, poor content intelligibility, and
difficulty in feature extraction, traditional detection methods are no
longer applicable. Existing solutions mainly rely on the powerful
feature self-learning ability of end-to-end deep neural networks to
identify encrypted traffic. However, such methods are overly dependent on data size, and it has been experimentally proven that it is
often difficult to achieve satisfactory results when validating across
datasets. In order to solve this problem, this paper proposes an encrypted traffic identification method based on contrastive learning.
First, the clustering method is used to expand the labeled data set.
When the encrypted traffic features are difficult to extract, it is only
necessary to learn the feature space to achieve discrimination.more
suitable for encrypted traffic identification. When validating across
datasets, only fine-tuning is required on a small amount of labeled
data to achieve good recognition results. Compared with the endto-end learning method, there is an improvement of about 5%.
CCS CONCEPTS •Security and privacy •Network security
•Security protocols

KEYWORDS
encrypted traffic, contrastive learning, feature extraction
ACM Reference Format:
siyuan tian, Yating Gao, Guoquan Yuan, Ru ZHANG, Jinmeng Zhao,
and Song Zhang. 2022. An encrypted traffic classification method based
∗ Corresponding Author email: zhangru@bupt.edu.cn

Permission to make digital or hard copies of all or part of this work for personal or
classroom use is granted without fee provided that copies are not made or distributed
for profit or commercial advantage and that copies bear this notice and the full citation
on the first page. Copyrights for components of this work owned by others than ACM
must be honored. Abstracting with credit is permitted. To copy otherwise, or republish,
to post on servers or to redistribute to lists, requires prior specific permission and/or a
fee. Request permissions from permissions@acm.org.
ICCIP 2022, November 03–05, 2022, Beijing, China
© 2022 Association for Computing Machinery.
ACM ISBN 978-1-4503-9710-0/22/11. . . $15.00
https://doi.org/10.1145/3571662.3571678

101

on contrastive learning. In 2022 the 8th International Conference on Communication and Information Processing (ICCIP 2022), November 03–05, 2022,
Beijing, China. ACM, New York, NY, USA, 5 pages. https://doi.org/10.1145/
3571662.3571678

1

INTRODUCTION

Traffic classification is an essential task for traffic engineering, network management, quality of service (QoS), and network security.
Its purpose is to identify categories of traffic from various applications or web services. In recent years, with the popularization
of traffic encryption technology and the rapid growth of network
throughput, traffic encryption has been widely used on the Internet.
Numerous services and applications use encryption algorithms to
protect their information. It is becoming increasingly difficult to
accurately identify encrypted traffic in real time. The classification
and identification framework of encrypted traffic based on deep
learning meets the needs of end-to-end classification and identification. Using the original traffic content as the model input, 1D-CNN,
2D-CNN, etc. are used for feature extraction. Although validating
on a single dataset works well, it is often difficult to achieve ideal
results when validating across datasets. Therefore, how to capture
the implicit and robust patterns in various encrypted traffic and support accurate and general traffic classification is the key to achieve
high network security and effective network management.
Contrastive learning has demonstrated its advantages for feature extraction in a wide range of applications across domains,
such as visual language and computer vision. Aiming at the above
problems, this paper designs a method for identifying encrypted
traffic based on contrastive learning. After the encrypted traffic
data is preprocessed, in the case of only a small number of labeled
samples, first use the clustering method to expand the data volume of the training set, and obtain a pre-trained model based on
supervised comparative learning training, and then use a small
number of samples for fine-tuning for downstream use. Task. The
experimental results show that the generalization ability of this
method is improved compared with the end-to-end encrypted traffic
identification method.

ICCIP 2022, November 03–05, 2022, Beijing, China

Siyuan Tian et al.

2 RELATED WORK
2.1 Identification of Encrypted Traffic
2.1.1 Payload-based approach. Bonfiglio et al. [1] utilize the unencrypted 4-byte header and the first 4 of the payload based on the
Pearson chi-square test and the Naive Bayes classifier. Chi-square
detection is performed on each byte to extract the fingerprint of
the protocol frame structure for Skype traffic identification. Bai Yu
[2] established a first-order homogeneous Markov chain by using
the secure socket protocol (SSL) and transport layer protocol (TLS)
message types as eigenvalues, and calculated the initial state and
end state by using the frequency statistics of state appearance and
transition to build a Markov model (fingerprint model) of the data.
2.1.2 Statistical feature-based Methods. According to the unencrypted bit stream data of different lengths in the link layer, Xing
Meng [3] et al. used four classical methods such as symbol frequency
detection in NIST detection to extract and identify its features.
2.1.3 Machine-learning Based Methods. Sun et al. [4] proposed
a hybrid approach to classify encrypted traffic. In this approach,
the SSL/TLS protocol is first identified using a signature matching
method. A Naive Bayesian machine learning algorithm is then applied to identify encrypted applications under the SSL/TLS protocol.
Alshammari [5] studied the performance of C5.0, AdaBoost, and
Genetic Programming (GP) algorithms for recognizing Voice over
IP (VoIP) traffic. Finally, it is concluded that applying suitable sampling and machine learning methods is important for VoIP traffic
classification. In addition, other feature-based methods are widely
used in traffic classification[6, 7, 8].
2.1.4 Deep-learning Based Methods. Vinh et al. used neural networks to classify news and proved the effectiveness of neural networks in sequence classification[9].Wang et al. [10] first proposed a
classification and recognition framework based on one-dimensional
CNN, which overcomes the problem that traditional machine learning algorithms are difficult to obtain the global optimal value, and
meets the needs of end-to-end classification and recognition. Based
on this, the subsequent research designs different preprocessing
methods of encrypted traffic data using two-dimensional CNN or
one-dimensional CNN to design the recognition framework [11, 12].

2.2

Contrastive Learning

This simple idea has been widely used in self-supervised learning of
image features and pre-training of model parameters in recent years.
Chen uses two augmentation mechanisms to generate two interrelated views for each example, making related views attract each
other while repelling other examples. Representations are learned
by maximizing the consistency between different augmented views
of the same data example through a contrastive loss in the latent
space [13]. Based on the given label information, Khosla et al. make
the samples with the same label as positive samples and other samples as negative samples. Using the supervised contrastive learning
method has achieved better results on the ImageNet dataset than
the traditional model based on the cross-entropy loss function [14].

102

Figure 1: Visualization of traffic preprocessing results

3 ALGORITHM DESIGN
3.1 Granularity Selection
The split granularity of network traffic includes TCP connections,
flows, sessions, services and hosts. A session is a collection of
flows, and a flow is defined as all packets with the same five-tuple.
The five-tuple contains source IP, destination IP, source port, Destination port and transport level protocols, sessions are bidirectional flows, covering both flows where source IP/port and destination IP/port are interchangeable. To construct the set of sessions, we describe all packets in the original network traffic as a
group 𝑃 = {𝑝 1, 𝑝 2, ·𝑠, 𝑝 |𝑝 | }, and each packet in the group is represented as 𝑝 𝑖 = (𝑥 𝑖 , 𝑏𝑖 , 𝑡 𝑖 ), 𝑖 = 1, 2, 3, ·𝑠. 𝑥 𝑖 represents a quintuple, 𝑏𝑖
represents the byte size of the corresponding packet, and 𝑡 𝑖 represents the time when the packet starts to be sent. A group 𝑃 in
the original network traffic is divided into multiple subsets, each
subset represents a flow, and a subset is described in the form of
𝑓 = (𝑥, 𝑏, 𝑑, 𝑡). 𝑥 represents the same quintuple, 𝑏 represents the
sum of the sizes of all packets in a stream, 𝑑𝑡 represents the duration
of the stream, and 𝑡 represents the time when the first packet of the
stream starts outputting. During a period of time, multiple flows
with the same or opposite quintuple information form a session
𝑆, and the original network traffic can be converted into a set of
multiple sessions, that is, the flow 𝑇 = (𝑆 1, 𝑆 2, 𝑆 3, ·𝑠).

3.2

Unlabeled data processing

Supervised contrastive learning relies on deep features, which depend on data size. In order to expand the amount of labeled data in
the dataset, the PCA method is first used to reduce the dimension of
high-dimensional traffic data to obtain a low-dimensional representation of the data, so as to avoid the problem of dimension disaster
caused by too high feature dimensions. Then, the labeled data and
unlabeled data are clustered together by clustering method, and the
unlabeled data with higher confidence is determined according to
the proportion of labeled data in different clusters to the data in the
whole cluster, and pseudo-labels are added to expand the labeled
data set.

3.3

Encrypted traffic identification method
based on supervised contrastive learning

This paper proposes an encrypted traffic identification method
based on supervised contrastive learning. For the first time, the
supervised contrastive learning method is used in the encrypted
traffic identification pre-training model. The pre-training model
consists of two neural networks, one of which is used for encrypted
traffic feature extraction called encoding. The projector 𝐸, and the

An encrypted traffic classification method based on contrastive learning

ICCIP 2022, November 03–05, 2022, Beijing, China

Table 1: ISCX VPN-nonVPN classification results
Traffic type

Content

Chat
E-mail
File
Streaming
Voip

Aim、Facebook、Hangouts、Icq、Skype
Email
Ftps、Skype
Spotify、Vimeo、Youtube
Facebook、Hangouts、Voipbuster

Table 2: USTC-TFC2016 classification results

Figure 2: Dimensionality reduction visualization of encrypted traffic features

Traffic type

Content

Chat
E-mail
File
P2p
Voip

Skype
GEmail、Outlook
Ftp、SMB
BitTorrent
Facetime

traffic. Consists of 15 apps such as Facebook, Youtube, Netflix. Selected applications are encrypted using various security protocols,
including HTTPS, SSL, SSH, and proprietary protocols. The USTCTFC2016 dataset contains encrypted traffic of 10 application types
such as MySQL, Gmail, and Outlook. Both datasets are collected
from real network environments.
We manually label the two datasets, ISCX VPN-nonVPN and
USTC-TFC2016, respectively, so that the two datasets are divided
into five categories. Table 1 and Table 2 show our classification
results.

Figure 3: Internal composition of residual structure

other for converting high-dimensional features to low-dimensional
features is called projector 𝑃. In terms of model selection, this paper
selects the resnet model proposed by He Yuming et al. of Microsoft
Research in 2015 as the encoder architecture.
Suppose the input is 𝑥, and the mapping learned by two fully
connected layers is 𝐻 (𝑥). Assuming that the dimensions of 𝐻 (𝑥)
and 𝑥 are the same, then fitting 𝐻 (𝑥) is equivalent to fitting residual
function 𝐻 (𝑥) −𝑥. Let residual function 𝐹 (𝑥) = 𝐻 (𝑥) −𝑥, then The
original function becomes 𝐹 (𝑥) − 𝑥, so a cross-layer connection is
added directly on the basis of the original network. In essence, the
objective function 𝐻 (𝑥) is not changed, and the network structure
is split into two branches, one of which is the residual. To map
𝐹 (𝑥), one branch is the identity map 𝑥, so the network only needs
to learn the residual map 𝐹 (𝑥).Considering the small size of the
dataset, this paper only uses the resnet18 model with the fewest
parameters for training.

4.2

4 EXPERIMENT
4.1 Dataset Selection
We validate our method using two public encrypted traffic
datasets, ISCX VPN-nonVPN (Draper-Gil et al., 2016)[15] and USTCTFC2016[16]. The ISCX VPN-nonVPN traffic dataset used for evaluation includes 7 regular encrypted traffic and 7 protocol encapsulated

103

Experimental results and analysis

In the TFC-2016 dataset, based on 9000 pieces of labeled data, we
first use PCA to reduce the dimension of the data and select five
cluster centers for clustering using K-Means, adding pseudo-labels
to the unlabeled data, as Supervised contrastive learning prepares
data. PCA technology can achieve dimensionality reduction to simplify the model, while maintaining the information of the original
data to the greatest extent.
After clustering and adding pseudo-labels, 14,000 pieces of data
with pseudo-labels are obtained. In order to verify the generalization
ability of the model, we will use 23,000 pieces of data to use endto-end and supervised comparative learning methods to train the
feature extraction model. After the training is completed, a fully
connected layer is added, and a small amount of data is used for finetuning in the ISCX dataset to finally verify the model’s encrypted
traffic recognition effect across datasets.
In order to verify that the generalization ability of the pre-trained
model after adding pseudo-labeled data is improved compared with
before, this paper sets up a control experiment. In addition to the
above set of experiments, only the labeled data is used for model
training, and cross-dataset verification is still performed.
The above experimental results are organized as shown in the
following table.

ICCIP 2022, November 03–05, 2022, Beijing, China

Siyuan Tian et al.

Table 3: TFC dataset clustering results
cluster id

Label_-1

Label0

Label1

Label2

Label3

Label4

0
1
2
3
4

10812
9344
3525
2933
3905

109
0
0
405
266

190
1806
7
0
85

1649
159
0
0
260

776
1470
0
0
196

0
316
1585
0
40

Table 4: Summary of experimental results (accuracy rate)
Amount of training data
9000
23000

methods

end-to-end learning
79
84.5

Supervised Contrastive Learning
86
90.55

Figure 4: End-to-end training cross-dataset validation results

Figure 7: Contrastive learning cross-dataset validation results
It can be seen from the above results that when the model converges, the model trained by comparative learning has better generalization ability than the end-to-end model, and can achieve better
results in cross-dataset validation, and under the same conditions.
In this case, the pre-training model based on contrastive learning
can achieve the effect of end-to-end training in only 10 training
rounds. In addition, under the same other conditions, in order to
verify the validity of the pseudo-label data, adding pseudo-label
data during the training process slightly improves the effect of the
two training modes.

Figure 5: Contrastive learning cross-dataset validation results

5

CONCLUSION

After the traffic is encrypted, the intelligibility of the payload content is poor, and feature extraction is difficult. The traditional end-toend model is difficult to understand the true meaning of the payload
content. Comparative learning only needs to learn the distinction
in the feature space, without the need for a deep understanding
of the encrypted content. It is suitable for feature extraction of
encrypted traffic and can get better results in downstream tasks
after fine-tuning. In addition, in order to solve the problem that a
large amount of labeled data is needed for supervised comparative
learning, this paper adopts the clustering method to select data with
high confidence to expand the labeled data set. The experimental
results show that after adding pseudo-labeled data, the generalization of the model The ability is slightly improved compared to

Figure 6: End-to-end training cross-dataset validation results

104

An encrypted traffic classification method based on contrastive learning

ICCIP 2022, November 03–05, 2022, Beijing, China

the previous one, which shows the effectiveness of this method for
feature extraction of encrypted traffic.

ACKNOWLEDGMENTS
The authors would like to thank the anonymous referees for their
valuable comments and helpful suggestions. The work is supported
by Science and Technology Project of the Headquarters of State
Grid Corporation of China, “The research and technology for collaborative defense and linkage disposal in network security devices”
(5700-202152186A-0-0-00).

REFERENCES
[1] Dario Bonfiglio, Marco Mellia, Michela Meo, Dario Rossi, and Paolo Tofanelli.
2007. Revealing skype traffic: when randomness plays with you. SIGCOMM
Comput. Commun. Rev. 37, 4 (October 2007), 37–48.
[2] Bai Yu. Research and Implementation of Encrypted Stream Recognition System
based on Markov Chain.2015. MA Thesis, Beijing Institute of Technology.
[3] Xing Meng, Wang Tao, Wu Yang, et al. A new method to improve the recognition
rate of link layer encrypted bit stream[J]. Application Research of Computers,2015,000(11): 3443-3447.
[4] G. Sun, Y. Xue, Y. Dong, D. Wang, C. Li.An novel hybrid method for effectively
classifying encrypted traffic.2010 IEEE Global Telecommunications Conference
GLOBECOM 2010 (2010), pp. 1-5.
[5] Riyad Alshammari, A. Nur Zincir-Heywood.Identification of voip encrypted
traffic using a machine learning approach J. King Saud Univ. Comput. Inf. Sci.,
27 (1) (2015), pp. 77-92.
[6] Trung T. Nguyen, Amartya Hatua, and Andrew H. Sung, "School of Computing,
the University of Southern Mississippi, Hattiesburg, MS, U.S.A.," Vol. 8, No. 2, pp.
141-147, May, 2017. doi: 10.12720/jait.8.2.141-147.
[7] Dewan Md. Farid and Chowdhury Mofizur Rahman, "Mining Complex Data
Streams: Discretization, Attribute Selection and Classification," Journal of

105

Advances in Information Technology, Vol. 4, No. 3, pp. 129-135, August,
2013.doi:10.4304/jait.4.3.129-135.
[8] Md. Badiuzzaman Pranto, Md. Hasibul Alam Ratul, Md. Mahidur Rahman, Ishrat
Jahan Diya, and Zunayeed-Bin Zahir, "Performance of Machine Learning Techniques in Anomaly Detection with Basic Feature Selection Strategy - A Network
Intrusion Detection System," Journal of Advances in Information Technology,
Vol. 13, No. 1, pp. 36-44, February 2022.
[9] To Nguyen Phuoc Vinh and Ha Hoang Kha, "Vietnamese News Articles Classification Using Neural Networks," Journal of Advances in Information Technology,
Vol. 12, No. 4, pp. 363-369, November 2021. doi: 10.12720/jait.12.4.363-369.
[10] W. Wang, M. Zhu, J. Wang, X. Zeng and Z. Yang, "End-to-end encrypted traffic
classification with one-dimensional convolution neural networks," 2017 IEEE
International Conference on Intelligence and Security Informatics (ISI), 2017, pp.
43-48.
[11] WANG W, SHENG Y, WANG J, et al. HAST-IDS: Learning Hierarchical SpatialTemporal Features Using Deep Neural Networks to Improve Intrusion Detection[J]. IEEE Access, 2018,6(99): 1792-1806.
[12] Lotfollahi, M., Jafari Siavoshani, M., Shirali Hossein Zade, R. et al. Deep packet:
a novel approach for encrypted traffic classification using deep learning. Soft
Comput 24, 1999–2012 (2020).
[13] Ting Chen, Simon Kornblith, Mohammad Norouzi, and Geoffrey Hinton. A simple
framework for contrastive learning of visual representations. arXiv preprint
arXiv:2002.05709, 2020.
[14] Prannay Khosla, Piotr Teterwak, Chen Wang, Aaron Sarna, Yonglong Tian, Phillip
Isola, Aaron Maschinot, Ce Liu, & Dilip Krishnan (2020). Supervised Contrastive
Learning neural information processing systems.
[15] G. Draper-Gil, A. H. Lashkari, M. S. I. Mamun and A. A. Ghor-bani, "Characterization of encrypted and VPN traffic using time-related features", Proceedings of
the 2nd International Conference on Information Systems Security and Privacy
(ICISSP), pp. 407-414, 2016.
[16] Wang, M. Zhu, X. Zeng, X. Ye and Y. Sheng, "Malware traffic classification using
convolutional neural network for representation learning", Proceedings of the
31st International Conference on Information Networking (ICOIN), pp. 712-717,
2017.
PAPER_TEXT
