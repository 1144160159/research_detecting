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
# [743] MPdetector: A Multi-Party Collaborative Federated Transfer Learning Approach for IoT Intrusion Detection
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
编号：743
题名：MPdetector: A Multi-Party Collaborative Federated Transfer Learning Approach for IoT Intrusion Detection
年份：2025
DOI：10.1109/tmc.2025.3600306
来源：IEEE Transactions on Mobile Computing
PDF：paper/10.1109_TMC.2025.3600306.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：联邦学习、隐私保护与分布式协同、IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 15
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\743.txt
- 原始字符数：68982
- 本次发送字符数：68982
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
920

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 1, JANUARY 2026

MPdetector: A Multi-Party Collaborative Federated
Transfer Learning Approach for IoT
Intrusion Detection
Li Lin , Member, IEEE, and ZhenKun Chen

Abstract—The pervasive adoption of the Internet of Things (IoT)
is accompanied by numerous network security threats, making the
timely detection of anomalies in traffic data through intrusion detection increasingly critical. The existing intrusion detection methods based on federated learning can achieve good results under
the condition of sufficient labeled data. However, the traffic data of
participants in real IoT environments have various characteristics
and there are a large amount of unlabeled data, which easily leads
to the performance degradation of the intrusion detection model.
To address this challenge, this paper proposes a novel federated
transfer learning approach for IoT intrusion detection based on
multi-party collaboration called MPdetector. MPdetector uses an
encoder to extract the feature representation of diverse traffic data
from heterogeneous clients, and maps the feature representation of
each client to a unified feature space. In addition, a label transfer
strategy is introduced to make full use of unlabeled data, and a
new mapping function is used to reconstruct the traffic data of each
client to expand client’s local data set, which can further improve
the detection performance of the model in varied and complex IoT
environments. Theoretical analysis proves that the entire transfer
learning process of MPdetector is conducted within a secure context. Experiments on four widely used intrusion detection datasets
show that MPdetector can detect known and unknown abnormal
traffic more accurately than the existing three classical intrusion
detection algorithms, and has strong generalization. Meanwhile,
the detection effect of MPdetector will be further improved with
the increase of the volume of labeled traffic.
Index Terms—IoT, intrusion detection, federated transfer
learning, deep learning.

I. INTRODUCTION
ITH the rapid development and widespread application
of IoT technology [1], [2], [3], the number and types
of IoT devices have increased rapidly in the past few years [4].
However, most IoT devices are small, low-cost, lack fixed power
supplies, and are difficult to maintain. These characteristics
often result in inadequate security considerations, making these
devices more vulnerable to cyber-attacks [5] such as Zero-day

W

Received 2 January 2025; revised 10 July 2025; accepted 13 August 2025.
Date of publication 19 August 2025; date of current version 3 December 2025.
This work was supported by the China National Science Foundation under
Grant 61502017. Recommended for acceptance by F. Restuccia. (Corresponding
author: Li Lin.)
Li Lin is with the College of Computer Science, Beijing University of
Technology, Beijing 100124, China, and also with the Beijing Key Laboratory of
Trusted Computing, Beijing 100124, China (e-mail: linli_2009@bjut.edu.cn).
ZhenKun Chen is with the College of Computer Science, Beijing University
of Technology, Beijing 100124, China (e-mail: 1317889183@qq.com).
Digital Object Identifier 10.1109/TMC.2025.3600306

attacks and Distributed Denial of Service (DDoS) attacks [6].
According to statistics, IoT devices on the Internet suffered up to
5.7 billion attacks in 2020, most of which were DDoS and botnet
attacks launched by malware such as Mirai and Gafgyt [7]. In
addition, there are differences in terminal devices, applications
and network protocols in IoT network, which makes network
traffic highly heterogeneous and leads to increasingly complex
patterns of network attacks. Consequently, detecting potential
intrusions in IoT environment to avoid more threats is crucial
for the healthy and sustainable development of IoT.
Traditional network intrusion detection methods are typically divided into two categories: signature-based and anomalybased [8]. Signature-based methods identify intrusions by
matching known attack features or patterns stored in a feature
library. However, it is difficult for these methods to detect
unknown attacks such as Zero-day attacks [9]. With the advancement of machine learning and deep learning, anomalybased detection methods have shown improved performance
in recognizing complex attack patterns and detecting Zero-day
attacks [10]. Despite these advances, the training of these models
often relies on single-source datasets i.e., traffic data collected
from a single node. Single-souce datasets are insufficient to
reflect the complex network intrusions behaviors such as DDoS
and botnet attacks that widely appear in IoT environments. For
instance, botnet attacks typically involve large amounts of data
from multiple nodes [11]. If the detection model lacks sufficient
information, it often causes problems such as model overfitting
and poor generalization.
In addition, the above schemes also ignore the privacy leakage
problem introduced by collecting the data of IoT devices [12]. A
common approach to address the privacy issue is the deployment
of federated learning technology in network intrusion detection [13], where participant nodes only upload model parameters
without sharing their local training data, a intrusion detection
center server is responsible for aggregating the model parameters
and distributing to the participant nodes, and the participant
nodes update the model locally. However, most existing federated learning-based network intrusion detection schemes usually
require data samples to have the same feature space. Then the
heterogeneous traffic data in the real IoT environments will
significantly affect the global model performance of federated
learning IoT intrusion detection [14].
Several studies have proposed to use federated transfer learning technology to achieve knowledge sharing required for IoT

1536-1233 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

LIN AND CHEN: MPDETECTOR: A MULTI-PARTY COLLABORATIVE FEDERATED TRANSFER LEARNING APPROACH

intrusion detection while protecting participant’s privacy [15],
that is, leveraging rich labels in fully labeled data source domains to help build flexible and efficient detection models in
target domains with large amounts of unlabeled data. Unlike
traditional federated learning methods, federated transfer learning technology does not require participants to have the same
features or the same sample space, so it is now receiving more
and more attention. According to the number of participants,
existing schemes can be divided into two categories. One is
designed for two parties (a single source domain and a single
target domain) [16], [17], which still faces the limitation of
single-source data.The other is suitable for multiple parties [8],
[18], [19], [20], [21], [22], but it requires the central server to
have a common data set for initializing the model and the local
training data set of participants must be labeled data. However,
in real IoT environments, most traffic data is unlabeled. On
the one hand, manual labeling requires professional knowledge
and is time-consuming. On the other hand, labeled data usually
raises privacy concerns, so many participating organizations or
institutions only provide unlabeled data.
To address the above issues, exploiting the idea of
SHFTL [23], this paper proposes a novel federated transfer learning approach for IoT intrusion detection based on multi-party
collaboration called MPdetector. In MPdetector, each participating client extracts the feature representation of its traffic data,
which is mapped into a unified feature space by a task manager
to realize the alignment of feature representations of traffic data
and reduce the difference between feature representations. A
label transfer scheme is introduced to assign pseudo-labels to
unlabeled network traffic data, and these pseudo-labeled data
are integrated into the set of labeled data to participate in
supervised training. Additionally, a deep learning-based traffic
data reconstruction mechanism is proposed to facilitate feature
transfer among clients, and a new mapping function is used to
reconstruct unlabeled traffic data of each client, so as to fully
integrate multi-source data information.
Compared with existing work, our contributions are summarized as follows.
r A novel IoT intrusion detection method is proposed, which
uses multi-party semi-supervised federated transfer learning to better exploit unlabeled valuable data, and integrates
feature representation alignment and reconstruction mechanisms, to solve the performance degradation problem of
detection model caused by a large number of unlabeled
data of participants and heterogeneity of data samples in
existing IoT attack detection methods.
r A traffic data reconstruction mechanism is proposed to
generate pseudo-labels from unlabeled data, which optimizes the mapping function in the classical federated
transfer learning, achieves high detection accuracy without
increasing the training cost and with minimal labeled data
requirements, enhancing the ability of the model to identify
malicious traffic data.
r The auxiliary training information provided by the unlabeled data in the target domain of intrusion detection was
fully used to realize the collaborative training between a
single source domain and multiple target domains, and the

921

generalization performance and detection performance of
the model on target domains were improved.
r We have successfully implemented and evaluated MPdetector on the UNSW-NB15 [24], NSL-KDD [25], CICIDS2017 [26], and N-BaIoT [27], [28] datasets. The results demonstrate that MPdetector can achieve a detection
accuracy of up to 98.2%, substantially outperforming the
existing methods based on deep learning, semi-supervised
learning, federated learning and semi-supervised federated
learning.
II. PROBLEM STATEMENT
In the traditional IoT intrusion detection scenarios using
machine learning or deep learning, IoT devices provide their
local data as participants to participate in the network intrusion
detection model training, and the final model is used to distinguish normal and abnormal traffic. However, these methods face
two main challenges. On the one hand, the detection accuracy of
these methods is limited by the small amount of labeled data per
client. On the other hand, it is easy to expose the user privacy of
IoT devices when aggregating network traffic data from multiple
clients. Although the IoT intrusion detection scheme based on
federated learning does not require clients to provide local traffic
data, the model performance is still affected by the heterogeneity
of network traffic data. To overcome the above issues, federated
transfer learning can be employed to assign pseudo-labels to unlabeled data and then clients can use both labeled and unlabeled
data for intrusion detection model training. Meanwhile each IoT
client does not expose data information during the process of
collaborative transfer learning, which ensures the security of
users’ privacy.
This paper proposes a method designed for scenarios involving multiple participants, where most of the data on the client
side is unlabeled, as illustrated in Fig. 1. It is important to note
that, unlike existing two-party-based approaches [17], the proposed method fully supports collaborative participation of over
100 clients in the same task. A central task manager coordinates
with all clients to jointly perform federated transfer learning.
This design offers greater generality and scalability. Assume
that there are n IoT device participants, denoted as client k (k =
1, 2 . . . , n), participating in the collaboration. Each client possesses a network traffic dataset, represented as X 1 , X 2 , . . . , X n ,
with the corresponding sample sizes M 1 , M 2 , . . . , M n . Considering the heterogeneity of traffic data features between multiple
clients, that is, there is no overlap of traffic data features between
clients but their traffic data samples partially overlap. Denote
the overlap of traffic data samples between the kth client and
k
MO
and the non-overlapping part as
other clients as Ok = {xki }i=1
Mk

N
, where MOk represents the number of overlapN k = {xkj }j=1
k
ping samples and MN
represents the number of non-overlapping
k
. Moreover, the
samples. Obviously there is M k = MOk + MN

Mk

O
, and the
overlapping traffic data is labeled as yo = {yik }i=1
label information is stored by the task manager, while the nonoverlapping traffic data remains unlabeled. A specific example
of network traffic data distribution is illustrated in Fig. 2.

922

Fig. 1.

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 1, JANUARY 2026

IoT intrusion detection scenario with federated transfer learning.
TABLE I
SYMBOL DEFINITIONS

Fig. 2.

Illustration of data distribution.

The goal of this paper is to propose a new federated transfer
learning approach that is applicable to the above multi-party
scenarios and has high performance. That is, the following
problem will be solved.
The Optimal Ferderated Transfer Learning Problem is as
follows.
Input: The number of participants n, the initial Intrusion Dek
, the local dataset of participants
tection Classification Model gcla
k
is X .
Question: Is there an optimal federated transfer learning approach that maximizes the ACC of intrusion detection classification models.
To address unlabeled traffic data, an effective feature extraction scheme and a label transfer scheme are presented in
the proposed transfer learning approach. Participating clients
provide unlabeled traffic data and extract network traffic feature
representations. The task manager aligns these feature representations, assigns pseudo-labels to the unlabeled data, and
reconstructs participating clients’ traffic data using mapping
functions.
To standardize the notation, the symbols used are defined in
Table I.
III. DESIGN OF MPDETECTOR
In this section, we will give the design of the proposed approach MPdetector, including its working principles and detailed
functions.
A. Sections and Subsections
As depicted in Fig. 3, in MPdetector, each participating client
is responsible for achieving the feature representation extraction,
while the task manager stores the overlapping network traffic

label information and handles feature representation alignment,
label transfer, and feature transfer. The workflow of MPdetector
is as follows.

1 Each participating client trains an encoder to extract the
feature representation of its traffic data and sends it to the
task manager.

2 The task manager aligns the feature representations of
the clients to reduce the differences between the feature
representations of different clients.

3 The task manager assigns pseudo-labels to the nonoverlapping traffic data using the aligned global representation, selects the non-overlapping traffic data with

LIN AND CHEN: MPDETECTOR: A MULTI-PARTY COLLABORATIVE FEDERATED TRANSFER LEARNING APPROACH

Fig. 3.

923

Interaction flow between the task manager and the client.

k
k
(RO
). The classificlassification result is denoted as ŷlk = gcla
cation loss function is as follows.
M0k



k
Arg min Lcla =
XE ŷik , yik ,
k
k
θenc
,θcla
i=1

Fig. 4.

Extracting feature representations of traffic data.

more reliable pseudo-labels to participate in the training
of intrusion detection model, and sends the unified feature representation and pseudo-labels to the participating
clients.

4 Each participating client uses an optimized traffic data
mapping function to reconstruct the unified feature representation of non-overlapping traffic data from other
clients, and adds the reconstructed traffic data to its training dataset.

5 Each participating client uses the extended data set to
train and obtain an intrusion detection model, and then
uses the model to classify and detect the traffic data.
B. Local Representation Extraction
In MPdetector, each client extracts the feature representation
of its networking traffic data using a combination of encoder,
classifier and decoder, and the extraction process is divided
into two tasks, supervised classification and unsupervised reconstruction, according to whether the data has labels, as shown
in Fig. 4.
For client k, as described in Table I, its overlapping traffic data
Ok contains labeled data where labels information is stored by
the task manager, its non-overlapping traffic data N k contains
k
is uesd to extract feature
unlabeled data. The encoder genc
k
k
k
k
k
= genc
(N k ) of
representation RO = genc (O ) of Ok and RN
k
N .
k
,
For the feature representation of labeled traffic data RO
k
the task manager uses the classifier gcla for classification. The

(1)

k
k
, θcla
represent the model parameters of the encoder
where, θenc
k
k
, respectively, and M SE is the crossgenc and classifier gcla
entropy loss function.
For the feature representation of unlabeled traffic data, the
k
for reconstruction. The reconstrucclient uses the decoder gdec
k
k
k
(RN
). The reconstruction loss
tion result is denoted as x̃j = gdec
is defined as follows:
k
MN



k
M SE x̃kj , xkj ,
Arg min Ldec =
k
k
θenc
,θdec
j=1

(2)

k
k
where θdec
is the model parameter of the decoder gdec
and M SE
is the mean square error loss function. In this way, the final
objective function for extracting the feature representation of
traffic data is as follows.

Arg min Lkr = Lkdec = Lkcla + λLkdec ,

(3)

k ,θ k
k
θenc
,θcla
dec

where λ(λ ∈ (0, 1)) is a hyperparameter that balances classification and reconstruction.
The specific feature extraction algorithm is outlined in
Algorithm 1.
C. Feature Representation Alignment
In order to reduce the feature differences of traffic data between clients, MPdetector map the traffic data features of clients
into a unified feature space, that is, to realize the alignment of
traffic data features between clients.
First, the task manager
 uses client k’s classification accuracy
wk as the weight wk ( nk=1 wk = 1), to synthesize the feature
representations of different clients’ traffic data
 to obtain ithe
).
global feature representation of traffic data RU ( ni=1 wi ∗ RO

924

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 1, JANUARY 2026

Algorithm 1: Local Feature Representation Extraction.
Input: Overlapping and non-overlapping portions of client
k
MO
and
k’s network traffic data Ok = {xki , yik }i=1
Mk

k
k
N
, client k’s encoder genc
, classifier gcla
, and
N k = {xkj }j=1
k
decoder gdec
.
Output: The feature representation of client k’s labeled and
k
k
and RN
, classification accuracy
unlabeled traffic data RO
k
.
wk of classifier gcla
1: for k = 1 to n do
k
k
k
= genc
(xki ) and sends RO
to
2: Client k calculates RO
the task manager;
k
k
= genc
(xkj );
3: Client k calculates RN
k
k
4: (x̃kj ) = gdec
(RN
);
k
k
5: The task manager calculates ŷlk = gcla
(RO
);
6: The task manager calculates the classification loss Lkcla
according to Formula (1);
7: Client k calculates the reconstruction loss Lkdec
according to Formula (2);
k
k
k
, θcla
, θdec
based on Lkdec and
8: Client k’s updates θenc
k
Lcla ;
k
to calculate wk ;
9: Client k uses the trained gcla
10: end for
k
k
, RN
and wk ;
11: returnRO

The task manager uses the mapping function F k to map the
labeled traffic data feature representations and obtain the unik
k
k
fied feature representation RU
O = F (RO ). To ensure that the
mapped feature representations retain their classification information, the classifier FCk is used to classify the mapped feature
k
representations ŷlk = Fck (RU
O ). Then, the objective function
for traffic data feature mapping is then expressed as follows.
k

arg min LkU =
k ,θ k
θmap
clb

MO

j=1

  k

, RU
MSE F k RO
⎛

+γ⎝

k
MU
O





XE Fck



k
RU
O





⎞

, yi ⎠ ,

(4)

i=1
k
k
where θmap
and θclb
are the model parameters of the mapping
k
function F and the classifier ŷlk = FCk , respectively γ(γ ∈
(0, 1)) is a hyperparameter. Using the optimized mapping function, the aligned uniform feature representation of labeled traffic
k
k
k
data RU
O = F (RO ) and the unified feature representation of
k
k
k
unlabeled traffic data RU
N = F (RN ) can be obtained.
The specific algorithm is shown in Algorithm 2.

D. Label Transfer
In real IoT environments, the amount of labeled traffic data
available to each client is limited. Only using labeled traffic
data to train intrusion detection models is easy to cause model
overfitting. To fully utilize the information in unlabeled traffic
data, a label transfer scheme is introduced into MPdetector,
which enable the task manager to assign pseudo-labels to the

Algorithm 2: Feature Representation Alignment.
Input: The feature representation of the client k’s labeled
and unlabeled traffic data, label set of the client k’s labeled
k
MO
traffic data {yik }i=1
, classification accuracy wk of
k
classifier gcla , and initialized mapping function F k and
classifier FCk (k = 1, 2 . . . , n).
Output: Unified feature representations of client k’s
k
k
labeled and unlabeled traffic data RU
O and RU N .
k
1: w (k = 1, 2 . . . , n) is normalized such that
( nk=1 wk = 1);
k
k
k
2: RU
O = F (RO );
k
k
k
3: RU N = F (RN
);
4: 
calculate
the
reconstruction
loss
K
MO
k
L
(R
,
R
);
M
SE
U
UO
j=1
k
5: ŷlk = FCk (RU
O );
MOk
6: calculates the classification loss i=1
LXE (ŷik , yik );
k
k
7: update θmap and θclb based on Formula (4);
k
k
8: returnRU
O and RU N ;
unlabeled traffic data by leveraging the similarity between the
labeled and unlabeled traffic data. The label transfer process
is illustrated in Fig. 5. The task manager concatenates feature
k
k
representations RU
O and RU N of the client k’s traffic data to
k
k
k
obtain RU = [RU O ; RU N ], which is used to construct its W k .
A labeling matrix Y k is defined for client k, where the row
vectors in the Y k corresponding to the one-hot encoded vectors
of labeled traffic data and the rows for unlabeled traffic data are
set to zero.
The probability matrix Z k is used to assign pseudo-labels to
unlabeled traffic data. The probability matrix Z k can be obtained
by using the conjugate gradient method to solve the linear system
(I − αS k )Z k = Y k [29], where I is the identity matrix, and
α(α ∈ (0, 1)) is used to regulate the relative importance of a
traffic data samples and its neighboring traffic data samples.
Finally, based on the probability matrix Z k , the pseudo-labels
of unlabeled traffic data are calculated as follows.
ŷpk = Arg max Z k (i, j),

(5)

j

where the element Z k (i, j) represents the values at the i-th row
and j-th column in the matrix Z k .
The pseudo-labels derived from this process may not always
be accurate, and training with incorrect pseudo-labels can degrade the performance of the client-side intrusion detection
model. To mitigate this issue, the entropy value of traffic data
samples is calculated to measure the uncertainty. The pseudok
are selected to ensure accuracy, and
labels with high certainty ŷps
the feature representation of corresponding traffic data samples
k
Nhk is expressed as RU
NS.
To further improve pseudo-label accuracy, each client initializes a N N Rw model. The model is trained using the global feak
ture representations RU
O of labeled traffic data. After training
completion, this model is applied to label unmarked traffic data,
generating a membership matrix for each sample. This matrix
represents the probability distribution of samples belonging to

LIN AND CHEN: MPDETECTOR: A MULTI-PARTY COLLABORATIVE FEDERATED TRANSFER LEARNING APPROACH

Fig. 5.

K-nearest neighbors matrix propagation process.

Fig. 6.

Label transfer process.

different categories. The fuzziness of traffic data is then calculated through membership vectors V = {u1 , u2 , . . ., un }.
1
[ui log ui + (1 − ui ) log (1 − ui )] ,
n i=1

925

either the size of the labeled traffic dataset stabilizes or the maximum number of iterations is reached. The detailed algorithm is
provided in Algorithm 3.

n

F (V ) = −

(6)

where u1 represents the membership degree of the traffic data.
As shown in Fig. 6, the traffic data is divided into low fuzziness
group F Glow , medium fuzziness group F Gmid , and high fuzziness group F Ghigh based on the fuzziness value F(V). Samples
belonging to F Gmid and F Ghigh are selected, and their labeling
k
.
results from the N N Rw model are used as pseudo-labels ŷpsf
k
Additionally, pseudo-labels ŷps for unlabeled traffic data are
obtained using the K-nearest neighbor matrix label propagation
method. The pseudo-labels generated by the N N Rw model
are then compared with those obtained through the K-nearest
neighbor matrix label propagation approach. Consistent results
from both methods are selected as the final pseudo-labels for
these unlabeled traffic data samples. These filtered unlabeled
traffic data are subsequently merged into the labeled traffic
dataset to retrain the N N Rw model. This process repeats until

E. Feature Transfer
Through the above label transfer scheme, client k can obtain
k
for unlabeled traffic data and the correspondpseudo-labels ŷps
k
ing global feature representation RU
N S . However, since the
feature information of each clients’ traffic data is limited, a
feature transfer scheme is introduced into MPdetector. In the
scheme, a new nonlinear mapping function H k is proposed,
which is used to reconstruct the unlabeled traffic data from other
clients and expand the missing features of the labeled traffic data
by client k, so that the intrusion detection model can learn a
more comprehensive network traffic feature representation and
improve the ability of the model to identify abnormal traffic and
normal traffic.
Compared with the linear mapping matrix, the deep learning
model uses nonlinear activation functions to extract and learn
the abstract features and representations of the data step by step
through the multi-level structure [10]. It can better fit the network

926

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 1, JANUARY 2026

Algorithm 3: Label Transfer.

Algorithm 4: Feature Transfer.

k
k
Input: global feature representations RU
O and RU N for
client k’s labeled and unlabeled traffic data
(k = 1, 2, . . . , n).
k
and the
Output: highly accurate pseudo-labels ŷps
k
corresponding global feature representation RU
NS.
1: for k = 1 to n do
k
k
k
← [RU
2: RU
O ; RU N ];

k
k
Input: global feature representations RU
O and RU N S of
the clients’ labeled and unlabeled traffic data, mapping
function H k (k = 1, 2 . . . , n).
k
of client k.
Output: the expanded traffic dataset XE
1: reconstruct the global feature representation of the
k
labeled traffic data H k (RU
O );
2: calculate the reconstruction loss Lk based on Formula
(6);
k
according to the reconstructed loss Lk ;
3: update θres
kt
4: (x̃js ) = H n (xti ) is sent to other client;
k
k
kn
5: merges the data set XE
= {xki ; x̃k1
js ; . . .; xjs ; . . .; x̃js };
k
6: returnXE
;

Rk (i,:)−Rk (j,:)2

U
Generate W k where Wijk = exp(− U
)
σ2
(i = j);
4: S k ← (Dk )−1/2 W k (Dk )−1/2 ;
5: Z k ← (I − αS k )−1 Y k ;
6: Calculate ŷpk using Formula (5);
7: while iteration ≤ T do
8:
Calculate F (V ) using Formula (6);
K
9:
Select samples RU
N E from both F Gmid and
F Ghigh groups;
k
and ŷpk , then send
10:
Check consistency between ŷpsf
k
matching pseudo-labels ŷps to clients;
k
k
= N N Rw (RU
11:
ŷpsf
N E );
k
12:
Select high confidence ŷps
and denote the
k
corresponding feature representation as RU
NS;
13: end while
k
k
and RU
14: Send ŷps
N S to client k;
15: end for
k
k
and RU
16: return ŷps
NS;

3:

Algorithm 5: Traffic Data Recognition.
k
k
Input: client k s trained encoder genc
and classifier gcla
,
k
and its network traffic dataset X .
Output: predicted labels Ŷ k for the network traffic dataset
Xk.
k
k
(genc
(X k ));
1: Ŷ k = gcla
2: returnŶ k ;

the traffic data feature representation, which ensures the privacy
security of client k. The detailed algorithm is shown as follows.
F. Traffic Data Recognition

traffic data, understand the internal structure of traffic data more
accurately, and then realize more effective data reconstruction.
However, in real IoT environment, most of IoT devices have
limited computing and storage resources, so it is more important
to save the cost of client-side intrusion detection model training.
Therefore, MPdetector uses a nonlinear deep learning model to
reconstruct traffic data, which can not only reduce the pressure of
client model training, but also improve the reconstruction effect
of traffic data.
The objective function of traffic data feature reconstruction
can be expressed as follows.

k
to train an
Next, client k uses the expanded traffic dataset XE
intrusion detection model to accurately identify normal traffic
and abnormal traffic. To achieve this goal, client k retrains
k
k
and classifier gcla
, to minimize the following
the encoder genc
objective function.
 k  k  k  K 
Arg min Lkcla = XE gcla
genc XE , YE ,
(8)
k
k
θenc
,θcla

k
k
k
where θenc
and θcla
are the model parameters of encoder genc
k
and classifier gcla , respectively.
The detail is presented in Algorithm 5.

IV. THEORETICAL ANALYSIS
k
MO

Arg min LkC =
k
θres



 k

K
K
M SE RU
N S , H (RU O ) ,

(7)

j=1

k
where θres
is the model parameter of the mapping function H k .
Client k (k = 1, 2 . . . , n) uses the trained mapping function
H k to reconstruct the unlabeled traffic data from other clients
k t
x̃kt
js = H (xi ). Then, the reconstructed traffic data and the original traffic data set of client k can be merged to obtain the extended
k
k
kn
= {xki ; x̃k1
traffic data set XE
js ; . . .; xjs ; . . .; x̃js }, with the cork
k
j k
responding label set YE = {y , {ŷs }j=1 }. Since the traffic data
feature representation needs the original traffic data dimension
to reconstruct the original traffic data, the original traffic data
dimension is only accessed by client k, and other parties cannot
obtain the information of the original traffic data only through

A. Complexity Analysis of Mapping Functions
Theorem 1: Let H k be the new mapping function for feature
transfer on client side in MPdetector, where a deep neural
network model replaces the mapping matrix M (n∗) . The computational complexity of H k is O(Eiter MOn L−1
l=1 Sl Sl+1 ), which
is approximately the same as the computational complexity
O(MOn 3 ) of M (n∗) .
Proof: The computational cost of matrix mapping
mainly lies in matrix multiplication. The matrix M n∗ =
−1
n
n T
n
n T
has a computational comRU
N S RU O (RU O RU O + μI)
n3
n
plexity of O(MO ), where MO represents the number of overlapping traffic data samples.
For deep neural network mapping, the computational cost
is concentrated in the forward and backward transfer phases.

LIN AND CHEN: MPDETECTOR: A MULTI-PARTY COLLABORATIVE FEDERATED TRANSFER LEARNING APPROACH

If the network has L layers with Sl neurons in each layer,
and the number of iterations during training is Eiter , the
time complexity is O(Eiter MOn L−1
l=1 Sl Sl+1 ), where, Eiter =
epochs ∗ (MOn /batch_size). And the epochs and batch size are
approximately the same, that means, epochs ≈ batch_size, so
Eiter ≈ MOn . With the increase of the amount of traffic data
MOn , in order to ensure that the deep learning model can better
fit the traffic data structure, the number of layers of the neural
network may increase, and the model can still converge when
L−1
n

l=1 Sl Sl+1 ≈ MO .
Theorem 1 indicates that the computational complexity of
deep neural networks is approximately the same as that of
matrix mapping. This means that, compared with the traditional
lightweight matrix mapping reconstruction methods applicable
to resource-constrained IoT devices, the method in MPdetector,
which uses deep learning (non-linear mapping functions) to
reconstruct traffic features, does not introduce additional time
overhead.
B. Security Analysis
Theorem 2: During the the feature representation alignment
process in MPdetector, the task manager cannot retrieve client
k’s original traffic data (k ∈ (1, n)).
Proof: If the task manager want to obtain client k’s traffic data
Ok and N k (k ∈ (1, n)), it must access the feature dimensions of
k
. As stated in
Ok and N k and client k’s encoder parameters θenc
Section III, the task manager can only access to the the encoded
k
k
and RN
in MPdetector but cannot get the
representations RO
feature dimensions of the traffic data.

Theorem 3: During the label transfer process in MPdetector,
the task manager cannot retrieve client k’s original traffic data
k (k = 1, 2 . . . , n).
Proof: During the label transfer process, if the task manager
want to access client k’s original traffic data Ok and N k , the
k
k
number of the unified feature representations RU
O and RU N
must exceed the feature dimension. The labels corresponding
k
k
to the unified feature representations RU
O and RU N have two
k ∈ (0, 1) and y ∈ (0, 1). The feature dimension
categories: yˆis
o
k
k
k
of RU O and RU
N is equal to the number of neurons Eenc in
k
k
2, the
the final layer of the encoder genc , and since Eenc
k
k
2, therefore
feature dimensions of RU
O and RU N will also
the task manager is prevented from accessing the client k’s original traffic data.the labels corresponding to the uniform feature
ˆk
k
k
representations RU
O and RU N are yis ∈ (0, 1) and yo ∈ (0, 1),
k
representing two classes. The feature dimension of RU
O and
k
k
RU N is determined by the number of neurons Eenc in the final
k
k
. If Eenc
2, the feature dimensions
layer of the encoder genc
k
k
of RU O and RU N will also greatly exceed 2. Therefore, the task
manager is prevented from accessing client k’s original traffic
data.

Theorems 2 and 3 show that even if the task manager is untrusted, it cannot obtain the clients’ original traffic data through
feature representations or pseudo-labels of traffic data, thus
ensuring the security of clients’ data. That is, the entire federated
transfer learning process in MPdetector is conducted within a
secure context.

927

V. EXPERIMENT EVALUATION
In this section, comprehensive experiments have been conducted to evaluate the effect of MPdetector.
A. Experimental Environment
We have implemented MPdetector using Python3 and PyTorch to achieve deep learning algorithm. An autoencoder is
used as the feature extraction model, a decoder is used to
reconstruct the traffic data, and a classifier is used to classify
the traffic data. The learning objective is to classify the traffic
data into two classes. The learning rate is set to 0.0001, and the
experiments is conducted on Intel Core i9-12900H, 2.50 GHz
CPU, 16 GB memory.
Four well-known intrusion detection datasets: UNSWNB15 [24], NSL-KDD [25], CICIDS2017 [26], and NBaIoT [27], [28] are used to evaluate the performance of MPdetector. The UNSW-NB15 dataset was collected in 2015 from a
real network environment at the Australian Security Laboratory.
It includes a diverse range of network traffic, featuring both
common network attacks and normal traffic. The NSL-KDD
dataset is a refined version of the classic KDD dataset, created
by removing duplicate samples from the original training and
test sets. The CICIDS2017 dataset contains daily benign activity
traffic data and various types of attacks, closely resembling
real-world data. The N-BaIoT dataset consists of raw traffic
captured from nine kinds of IoT devices infected by the Mirai
and BASHLITE botnets.
The experimental procedure consists of the following steps.
First, we preprocess the aforementioned datasets by randomly sampling the processed traffic data to create overlapping and non-overlapping traffic data for IoT clients. Without loss of generality, the non-overlapping data is then divided into training, validation, and test sets with a ratio of
7:2:1.
MPdetector fully supports applications in scenarios with
homogeneous traffic data or partial feature overlap. However,
to experimentally verify its detection performance under fully
heterogeneous client traffic data, we partition the traffic features
to simulate a feature-heterogeneous environment, where the
feature spaces of different clients do not overlap at all, as shown
in Table II. To simulate such a setting, in our experiments, if
there are n clients participating in training, the traffic features
are divided into n parts. Each client is then assigned a distinct
feature space, achieving feature heterogeneity. However, to extend this partitioning to over 100 clients, the features would
need to be split into more than 100 parts. Due to the limited
feature dimensions in existing intrusion detection datasets, this
would inevitably cause overlap between client feature spaces,
making it impossible to simulate a completely heterogeneous
scenario. Therefore, to evaluate MPDetector in a setting where
feature spaces are entirely disjoint, we conducted experiments
on multiple clients (without loss of generality, n = 3) using
datasets with limited feature dimensions. Among these, the
client responsible for maintaining network traffic data labels
serves as the task manager, which typically initiates the intrusion
detection model training process. The remaining clients function

928

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 1, JANUARY 2026

TABLE II
FEATURE PARTITIONING OF THE DATASET

as participants. The final experimental results are reported as the
average performance across all participating clients.

TABLE III
COMPARISON ON ACC, FAR, AND F1 FOR DIFFERENT DATASETS UNDER FIVE
METHODS

B. Classification Performance
In the experiment, MPdetector was compared with deep
learning (DL), semi-supervised deep learning (SDL), federated
learning (FL), and semi-supervised FL (SFL) based intrusion
detection methods. In DL-based methods, each client uses an
autoencoder to extract feature representations from the training data and then trains a classifier to detect intrusions. In
SDL-based methods, each client extracts feature representations
using an autoencoder, clusters the non-overlapping traffic data
with K-means, and then trains classifiers on both overlapping
and non-overlapping traffic data. The FL-based method applies
the FedAVG algorithm to detect intrusions using an aggregated
model. In SFL-based methods Each client employs an autoencoder to extract feature representations from training data. The
K-means technique is then applied to cluster feature representations of non-overlapping traffic data. Both overlapping and
non-overlapping traffic data are subsequently used as inputs for
the FedAVG algorithm during federated training. Finally, the
aggregated model obtained from this training process is utilized
to evaluate the training data.
In the experiment, some common machine learning performance indicators are used to compare and evaluate the performance of different intrusion detection methods as follows.
Accuracy (ACC) is the ratio of traffic data correctly identified
by the intrusion detection model, which is calculated according
to the following Formula (8).
ACC =

TP + TN
,
TP + TN + FP + FN

(9)

False Alarm Rate (FAR) represents the proportion of normal
traffic data being misclassified as abnormal traffic data resulting
in false positives and is calculated according to Formula (9).
F AR =

FP
,
TN + FP

(10)

The F1 Score (F1 ) provides a balanced evaluation of precision
and recall. It is calculated using (10):
F1 =

TP
,
T P + 12 (F P + F N )

(11)

In the above equations, TP represents correctly classified
normal traffic data, FP refers to normal traffic data misclassified
as abnormal, TN represents correctly classified abnormal traffic,
and FN refers to abnormal traffic misclassified as normal.

As shown in Table III, FL performs worse than DL on
the UNSW-NB15 and CICIDS2017 datasets. It is due to the
different training data characteristics used by each client, and
the heterogeneity of data feature space between clients, which
affects the performance of FL. For the UNSW-NB15 dataset,
SDL achieves higher detection accuracy than DL. However,
on the NSL-KDD and CICIDS2017 datasets, SDL performs
worse than DL. This is because when using K-means technology for clustering, some traffic data clustering results do
not match the actual labels, which affects the performance of
the final model. On relevant datasets, SFL consistently demonstrates higher accuracy than FL, as semi-supervised learning
effectively addresses the insufficiency of labeled data across
clients. However, the persistent feature heterogeneity among
clients results in SFL’s accuracy remaining lower than SDL’s
performance. MPdetector demonstrates superior performance
across all evaluated datasets, achieving particularly outstanding
results on the CICIDS2017 dataset with 98.86% accuracy. This
exceptional performance stems from the fine-grained feature
characteristics of CICIDS2017 dataset, combined with MPdetector’s collaborative transfer mechanism that effectively integrates comprehensive feature representations. The model’s ability to precisely capture complex attack patterns is significantly
enhanced through this feature integration approach. Experimental results confirm that MPdetector exhibits strong generalization
capabilities across diverse datasets. Compared with DL, SDL,
FL, and SFL methods, MPdetector consistently achieves higher
accuracy and F1 scores while maintaining lower false alarm
rates.
In MPdetector, the task manager acts as the knowledge-rich
source domain, while the clients act as the knowledge-poor

LIN AND CHEN: MPDETECTOR: A MULTI-PARTY COLLABORATIVE FEDERATED TRANSFER LEARNING APPROACH

Fig. 7.

929

Feature distribution and correlation analysis on the UNSW-NB15 dataset.

target domain. Collaborative knowledge transfer occurs between the task manager and multiple clients. This cooperative
framework helps the clients train intrusion detection models,
effectively addressing the issue of insufficient labeled data.
Additionally, MPdetector employs a label transfer mechanism to
assign pseudo labels to unlabeled data, and uses a nonlinear data
reconstruction mechanism to achieve feature transfer to enrich
the feature representation of traffic data. These measures collectively solve the problem of data heterogeneity and significantly
improve the detection accuracy of client traffic analysis.
To better interpret the detection results, we conducted feature correlation analysis on the UNSW-NB15 dataset based
on MPdetector’s outputs, as illustrated in Fig. 7. The analysis
reveals that connection timing features (ct_srv_dst, ct_src_ltm,
ct_srv_src, ct_dst_ltm) and traffic behavior features (Sload, Sttl,
Swin) show the most significant correlations with intrusion
detection. Specifically, ct_srv_dst effectively identifies abnormal service access patterns by counting connection frequencies between specific services and destination addresses, while
ct_src_ltm and ct_dst_ltm detect lateral movement behaviors

by tracking connection frequencies of source/destination addresses within time windows. Abnormal values in Sload (source
instantaneous transmission rate) and Sttl (initial time-to-live)
typically correlate with Exploits or Shellcode attacks, as these
often involve non-standard packet rates or forged hop counts.
Swin (TCP receive window size) reflects protocol-level flow
control anomalies. Additionally, Proto (protocol type) and Dttl
(destination-to-source TTL value) further assist in detecting
abnormal behaviors, such as UDP protocol abuse or TTL manipulation. These features collectively form the detection basis
for MPdetector, and the correlation analysis demonstrates its
effectiveness in capturing attack-related anomalies.
Fig. 7 shows the feature distribution of traffic data, comparing normal and anomalous traffic across clients. The most
distinguishable features between normal and anomalous traffic are crucial for model detection. For Client 1, significant
distribution differences appear in ct_srv_dst, ct_src_ltm, and
ct_dst_sport_ltm. The median ct_srv_dst value for normal traffic
reaches 0.3, substantially higher than anomalous traffic, with a
wider interquartile range. For Client 2, clear differences appear

930

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 1, JANUARY 2026

Fig. 8. Different numbers of overlapping data versus detection accuracy under
two different traffic mapping functions.

Fig. 9. Different numbers of overlapping data versus Pseudo-labeling accuracy
on different datasets under MPdetector.

in ct_srv_src, ct_dst_src_item, and ct_dst_ltm. Although swin
and proto_udp demonstrate high correlation with detection results in Fig. 7, their distributions show no discernible difference
between normal and anomalous traffic, potentially leading to
model misclassification. For Client 3, marked differences exist
in dttl and ct_state_ttl between traffic types.
C. Influence of Different Mapping Function
This experiment evaluates whether the new nonlinear mapping function proposed in the feature transfer part of MPdetector
can improve the detection performance while ensuring the computational overhead of participating clients. We compare detection accuracy of two mapping functions: a linear mapping matrix
(LiMatrix) and the nonlinear mapping function (NonLiFunc) in
MPdetector, across various amounts of overlapping traffic data.
Detection accuracy is the model performance trained on both
overlapping and non-overlapping data. As illustrated in Fig. 8,
the horizontal axis represents the number of overlapping data,
and the vertical axis represents detection accuracy. The results
show that NonLiFunc significantly improves the performance
of the intrusion detection model. Notably, the enhancement is
more pronounced when the number of overlapping data reaches
50 and 1,000 rows.
D. Influence of Different Amounts of Overlapping Data
This experiment examines how different amounts of overlapping data affect pseudo-labeling accuracy and detection accuracy, when MPdetector is applied. Pseudo-label accuracy is
the accuracy of pseudo-labels assigned to non-overlapping data
during label transfer process, detection accuracy is the model
performance trained on both overlapping and non-overlapping
data. The results are illustrated in Figs. 9 and 10 . Fig. 9 shows
the impact of overlapping data on pseudo-labeling accuracy
across different datasets. As shown in Fig. 9, the horizontal axis
represents the number of overlapping data, and the vertical axis
represents the pseudo-labeling accuracy. The results indicate
that pseudo-labeling accuracy improves with the increasing in
overlapping data and the number of labeled data involved in the
transfer of labels. Fig. 10 illustrates the effect of overlapping
data on detection accuracy for different datasets. As shown in

Fig. 10. Different numbers of overlapping data versus detection accuracy on
different datasets under MPdetector.

Fig. 10, the horizontal axis represents the number of overlapping
data, and the vertical axis represents detection accuracy. The
results reveals that as the amount of overlapping data increases,
the shared knowledge among clients grows, the effect of transfer learning is improved, and model detection performance is
significantly improved. In summary, pseudo-labeling accuracy
significantly impacts model performance. When the amount
of overlapping data reaches 500, both pseudo-label accuracy
and model detection performance achieve satisfactory results
on relevant datasets. MPdetector significantly mitigates the adverse impact of limited overlapping data on model performance
through its nonlinear data reconstruction method and label transfer approach. With the increasing of overlapping data, pseudolabeling accuracy continues to rise, and detection accuracy is
further improved.
E. Generalization Performance
This experiment uses the N-BaIoT dataset to evaluate whether
MPdetector not only detects abnormal traffic within the training
set but also enhances the ability to identify unknown abnormal
traffic through knowledge transfer. Since the datasets of seven
kinds of IoT devices in the N-BaIoT dataset contain two types
of botnets, Gafgyt and Mirai, the data of these seven kinds
of IoT devices are mainly used in this experiment, denoted

LIN AND CHEN: MPDETECTOR: A MULTI-PARTY COLLABORATIVE FEDERATED TRANSFER LEARNING APPROACH

Fig. 11.

931

Different kinds of IoT devices versus detection accuracy under different intrusion detection methods on two different cases.

as device1 - 7. The experiment involves two cases. Case 1 is
called OnlyMirai, where Gafgyt attack data is removed from
the training set and only Mirai attack data is retained to test
the detection accuracy for Gafgyt attack data. Case 2 is called
OnlyGafgyt, where the Mirai attack data is removed from the
training set and only Gafgyt attack data is retained to test the
detection accuracy for Mirai attack data.
The experimental results are shown in Fig. 11, where the horizontal axis represents the data of seven kinds of IoT devices and
the vertical axis represents detection accuracy under different
intrusion detection methods. The results show that the detection
accuracy of MPdetector in identifying unknown abnormal traffic
data is higher than that of other methods, which indicates that
MPdetector has strong generalization ability. This is because
MPdetector uses the similarity between labeled and unlabeled
data for label transfer, makes full use of the information provided
by unlabeled data, and then greatly improves the identification
ability of unknown traffic data.
VI. RELATED WORK
With the development of machine learning and deep learning
technology, intrusion detection methods based on deep learning
have achieved good results in learning complex attack patterns
and zero-day attack detection [10]. These algorithms have been
used to detect anomalies in IoT networks, and have achieved
good detection results. Abdelmoumin et al. [30] used hyperparameter adjustment and ensemble learning to optimize the
learning model to detect intrusion in the Internet of things in
order to solve the problem of insufficient training data and
single model easily falling into local optimum. Saba et al. [31]
used genetic algorithm to select important features to improve
the accuracy of the model, and machine learning algorithm to
distinguish malicious traffic from regular traffic. Ge et al. [32]
proposed an intrusion detection method based on deep learning
network traffic classification, considering both multi-class and
binary classification schemes. A feed-forward neural network
with embedding layers and a second neural network for binary
classification are used to leverage network embedding and transfer learning. However, IoT intrusion detection methods based on
machine learning or deep learning rely on a large amount of data
to achieve high performance. In reality, there is a phenomenon of
data islands. Due to privacy and security concerns, data cannot

be shared between clients. Meanwhile, various types of client
attack data are unbalanced. Different types of attack data from
different clients also suffer from imbalance.
Federated learning offers a solution by allowing clients to
collaboratively train a model without directly sharing local data,
thus maintaining data security and achieving privacy protection. Idrissi et al. [33] proposed a federated learning based
intrusion detection method to tackle privacy issues associated
with centralized models. An autoencoder is used to calculate
the intrusion score based on the reconstruction error, which
achieves high accuracy and low false alarm rate. Li et al. [34]
adopted federated learning with dynamic filtering and weighting
strategies to protect data privacy and reduce communication
overhead, and proved through experiments that the detection
performance was improved with minimal network communication. Rashid et al. al. [35] show that federated learning can ensure
privacy and security by having IoT clients only share parameter
updates and a central server is responsible for aggregating and
refining parameters. Karmakar et al. [36] enhanced the sharing of
Autonomous Aerial Vehicle (AAV) data with federated learning,
which enables multiple deep neural network models to collaboratively learn and update their parameters. Although the above
federated learning schemes can solve the problem of privacy
protection, they still require enough labeled data for local model
training. In addition, data heterogeneity among participants can
affect model performance. Consequently, numerous studies have
proposed intrusion detection methods utilizing self-supervised
learning and transfer learning approaches.
Self-supervised learning is an unsupervised approach that
generates supervisory signals from data characteristics without
manual labeling. Nguyen et al. [37] proposed a GNN-based
self-supervised method for IoT intrusion detection, which learns
node features through graph networks and enhances representation learning via traffic attribute prediction. Evaluations on real
network traffic demonstrated its superiority in binary/multi-class
attack detection, significantly outperforming GNN baselines in
AUC and F1-score. Xu et al. [38] developed a graph contrastive
learning framework using edge-attention encoders to capture
traffic interaction patterns, achieving supervised-comparable
accuracy with lower computational costs. However, these graphbased methods suffer from high complexity when handling
large-scale node-edge relationships, making them unsuitable for
IoT scenarios.

932

Adaptive transfer learning dynamically optimizes knowledge
transfer between domains. Anley et al. [39] designed depthadaptive CNNs with traffic-to-image conversion, enabling pretrained vision models to process non-visual data and achieve
cross-dataset feature transfer. Ajayi et al. [40] proposed an
LSTM-based domain adaptation method for host intrusion detection, transferring knowledge via sequence modeling and
fine-tuning to reduce label dependency. While effective, these
approaches only support single-source-to-single-target transfer,
requiring separate adaptations for multiple targets with substantial resource consumption.
Federated transfer learning seeks to transfer knowledge from
diverse data sources to enhance local models’ performance.
This approach often outperforms models trained solely on local
data [41]. Khoa et al. [17] introduced a collaborative learning
framework that allows a target network, which has only unlabeled data, to learn efficiently from an original network with
extensive labeled data. This framework improves performance
by over 40% compared to existing deep learning methods.
However, it is limited to interactions between two parties. When
multiple participants are involved, updating models requires
exchanging parameters in pairs, which complicates the process
and increases both communication and computational costs.
Cheng et al. [21] integrated federated 11 transfer learning
with reinforcement learning to optimize intrusion detection in
mobile edge computing. Their approach aims to achieve the
highest detection accuracy with a limited number of clients
while reducing costs. Ji et al. [20] proposed a method combining
federated transfer learning with convolutional neural networks.
This method builds a cloud model and then personalizes learning
across organizations through transfer learning. After numerous
iterations, it produces a highly effective detection model. Fan
et al. [18] developed a federated transfer learning-based intrusion detection frame work for 5 G IoT. The framework aggregates data through federated learning and customizes detection
models through transfer learning, allowing IoT clients to share
knowledge while preserving privacy, which in turn improves
detection performance. Zhang et al. [8] proposed a lightweight
anomaly based intrusion detection algorithm using a two-step
fusion boosting strategy. This strategy evaluates data distribution
variance with maximum average variance and adjusts model
weights to enhance overall detection performance. However,
these federated transfer learning methods typically require a
central server to possess a large, labeled dataset to initialize the
model, making them unsuitable for intrusion detection scenarios
with extensive amounts of unlabeled data.
Unlike the above methods that require both extensive labeled
traffic data for training initial detection models and homogeneous data distribution to achieve optimal performance, this paper propose MPdetector, a federated transfer learning approach
for IoT intrusion detection, which supports the collaborative
transfer learning of multiple clients and is effective even when
most local data is unlabeled. It also addresses the challenges of
IoT traffic data heterogeneity and the abundance of unlabeled
data. Experimental results demonstrate that MPdetector can
maintain superior detection accuracy even with limited labeled
data and under significant feature heterogeneity conditions.

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 1, JANUARY 2026

VII. CONCLUSION AND FUTURE WORK
To address the challenges of heterogeneous IoT network
traffic data and the large volume of unlabeled data, this paper
proposes a federated transfer learning method for IoT intrusion
detection based on multi-party collaboration, called MPdetector.
In MPdetector each client extracts feature representations of
both label and unlabeled traffic data using an autoencoder. The
task manager maps these feature representations to a unified
feature space and applies a label transfer scheme to assign
pseudo-labels to unlabeled data, enabling label transfer. Each
client then can use a new proposed new mapping function to
reconstruct the traffic data of other clients, achieving feature
transfer of the traffic data. The effectiveness of MPdetector is
verified by theoretical analysis and experiments. Experimental
results show that MPdetector can achieve a detection accuracy
as high as 98.2% and has strong generalization. Meanwhile the
higher the number of labeled traffic data, the better the detection
performance.
The effectiveness of MPdetector has been validated through
experiments. The experimental results show that the intrusion
detection accuracy of MPdetector is as high as 98.2%, which
can effectively identify known and unknown abnormal traffic
data, and has strong generalization. The higher the number of
labeled traffic data, the better the detection performance.
MPdetector introduces a label transfer scheme to realize label
transfer and reconstruct client traffic data to enable feature
transfer across clients. However, the pseudo-labeling accuracy
and the quality of data reconstruction may lead to irrelevant
knowledge being learned, resulting in a decrease in detection
accuracy. There are still some challenges to improve the pseudolabeling accuracy and the quality of data reconstruction. In the
next step, the optimized pseudo-label allocation method and data
mapping method will be given to improve thepseudo-labeling
accuracy and the quality of data reconstruction, and further
improve the identification efficiency of traffic data. In addition,
the current MPdetector approach involves multiple interactions
between participating clients. In the future, the interaction between the task manager and the clients will be further optimized
to ensure the detection accuracy while reducing the communication overhead of clients. In the future, it is expected to
reduce the interaction between clients, and reduce the communication overhead of clients while ensuring the detection
accuracy.
REFERENCES
[1] L. Catarinucci et al., “An IoT-aware architecture for smart healthcare
systems,” IEEE Internet Things J., vol. 2, no. 6, pp. 515–526, Dec. 2015.
[2] Y. Tian, B. Zheng, and Z. Li, “Agricultural greenhouse environment
monitoring system based on Internet of Things,” in Proc. 3rd IEEE Int.
Conf. Comput. Commun., 2017, pp. 2981–2985.
[3] H. Ghayvat, S. Mukhopadhyay, X. Gui, and N. Suryadevara, “WSN-and
IoT-based smart homes and their extension to smart buildings,” Sensors,
vol. 15, no. 5, pp. 10350–10379, 2015.
[4] F. Sattler, S. Wiedemann, K.-R. Müller, and W. Samek, “Robust and
communication-efficient federated learning from non-i.i.d. data,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 31, no. 9, pp. 3400–3413, Sep. 2020.
[5] M. Abomhara and G. M. Køien, “Cyber security and the Internet of Things:
Vulnerabilities, threats, intruders and attacks,” J. Cyber Secur. Mobility,
vol. 4, pp. 65–88, 2015.

LIN AND CHEN: MPDETECTOR: A MULTI-PARTY COLLABORATIVE FEDERATED TRANSFER LEARNING APPROACH

[6] Y. R. Siwakoti, M. Bhurtel, D. B. Rawat, A. Oest, and R. Johnson, “Advances in IoT security: Vulnerabilities, enabled criminal services, attacks,
countermeasures,” IEEE Internet Things J., vol. 10, no. 13, pp. 11224–
11239, Jul. 2023.
[7] NSFocus Information Technology Co Ltd, “2020 cybersecurity insights,”
vol. 1, 2022. [Online]. Available: https://nsfocusglobal.com/wp-content/
uploads/2021/06/2020-NSFOCUS-Cybersecurity-Insights.pdf
[8] J. Zhang, C. Luo, M. Carpenter, and G. Min, “Federated learning for
distributed IIoT intrusion detection using transfer approaches,” IEEE
Trans. Ind. Informat., vol. 19, no. 7, pp. 8159–8169, Jul. 2023.
[9] A. L. Buczak and E. Guven, “A survey of data mining and machine learning
methods for cyber security intrusion detection,” IEEE Commun. Surveys
Tuts., vol. 18, no. 2, pp. 1153–1176, Second Quarter, 2016.
[10] A. Aldweesh, A. Derhab, and A. Z. Emam, “Deep learning approaches
for anomaly-based intrusion detection systems: A survey, taxonomy, and
open issues,” Knowl.-Based Syst., vol. 189, 2020, Art. no. 105124.
[11] H. Wang, J. Hou, and Z. Gong, “BotNet detection architecture based on
heterogeneous multi-sensor information fusion,” J. Netw., vol. 6, no. 12,
2011, Art. no. 1655.
[12] S. Hui et al., “Systematically quantifying IoT privacy leakage in mobile networks,” IEEE Internet Things J., vol. 8, no. 9, pp. 7115–7125,
May 2021.
[13] S. Agrawal et al., “Federated learning for intrusion detection system:
Concepts, challenges and future directions,” Comput. Commun., vol. 195,
pp. 346–361, 2022.
[14] K. Chen et al., “Privacy preserving federated learning for full heterogeneity,” ISA Trans., vol. 141, pp. 73–83, 2023.
[15] Y. Liu, Y. Kang, C. Xing, T. Chen, and Q. Yang, “A secure federated
transfer learning framework,” IEEE Intell. Syst., vol. 35, no. 4, pp. 70–82,
Jul./Aug. 2020.
[16] J. Zhao, S. Shetty, and J. W. Pan, “Feature-based transfer learning
for network security,” in Proc. 2017 IEEE Mil. Commun. Conf., 2017,
pp. 17–22.
[17] T. V. Khoa et al., “Deep transfer learning: A novel collaborative learning
model for cyberattack detection systems in IoT networks,” IEEE Internet
Things J., vol. 10, no. 10, pp. 8578–8589, May 2023.
[18] Y. Fan, Y. Li, M. Zhan, H. Cui, and Y. Zhang, “IoTDefender: A federated
transfer learning intrusion detection framework for 5G IoT,” in Proc. IEEE
14th Int. Conf. Big Data Sci. Eng., 2020, pp. 88–95.
[19] Y. Otoum, V. Chamola, and A. Nayak, “Federated and transfer learningempowered intrusion detection IoT applications,” IEEE Internet Things
Mag., vol. 5, no. 3, pp. 50–54, Sep. 2022.
[20] X. Ji, H. Zhang, and X. Ma, “A novel method of intrusion detection based
on federated transfer learning and convolutional neural network,” in Proc.
IEEE 10th Joint Int. Inf. Technol. Artif. Intell. Conf., 2022, pp. 338–343.
[21] Y. Cheng, J. Lu, D. Niyato, B. Lyu, J. Kang, and S. Zhu, “Federated
transfer learning with client selection for intrusion detection in mobile edge
computing,” IEEE Commun. Lett., vol. 26, no. 3, pp. 552–556, Mar. 2022.
[22] Y. Otoum, Y. Wan, and A. Nayak, “Federated transfer learning-based IDS
for the internet of medical things (IoMT),” in Proc. 2021 IEEE Globecom
Workshops, 2021, pp. 1–6.
[23] S. Feng, B. Li, H. Yu, Y. Liu, and Q. Yang, “Semi-supervised federated
heterogeneous transfer learning,” Knowl.-Based Syst., vol. 252, 2022,
Art. no. 109384.
[24] N. Moustafa and J. Slay, “UNSW-NB15: A comprehensive data set for
network intrusion detection systems (UNSW-NB15 network data set),” in
Proc. 2015 Mil. Commun. Inf. Syst. Conf., 2015, pp. 1–6.
[25] NSL-KDD dataset, 2009. Accessed: Feb. 08, 2021. [Online]. Available:
https://www.unb.ca/cic/datasets/nsl.html
[26] I. Sharafaldin et al., “Toward generating a new intrusion detection dataset
and intrusion traffic characterization,” in Proc. 4th Int. Conf. Inf. Syst.
Secur. Privacy, 2018, pp. 108–116.
[27] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “Kitsune: An ensemble of autoencoders for online network intrusion detection,” 2018, arXiv:
1802.09089.
[28] Y. Meidan et al., “N-BaIoT—Network-based detection of IoT BotNet
attacks using deep autoencoders,” IEEE Pervasive Comput., vol. 17, no. 3,
pp. 12–22, Third Quarter 2018.
[29] A. Iscen, G. Tolias, Y. Avrithis, and O. Chum, “Label propagation for deep
semi-supervised learning,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2019, pp. 5070–5079.

933

[30] G. Abdelmoumin, D. B. Rawat, and A. Rahman, “On the performance of
machine learning models for anomaly-based intelligent intrusion detection
systems for the Internet of Things,” IEEE Internet Things J., vol. 9, no. 6,
pp. 4280–4290, Mar. 2022.
[31] T. Saba, T. Sadad, A. Rehman, Z. Mehmood, and Q. Javaid, “Intrusion
detection system through advance machine learning for the Internet of
Things networks,” IT Professional, vol. 23, no. 2, pp. 58–64, 2021.
[32] M. Ge, N. F. Syed, X. Fu, Z. Baig, and A. Robles-Kelly, “Towards a
deep learning-driven intrusion detection approach for Internet of Things,”
Comput. Netw., vol. 186, 2021, Art. no. 107784.
[33] M. J. Idrissi et al., “Fed-ANIDS: Federated learning for anomaly-based
network intrusion detection systems,” Expert Syst. Appl., vol. 234, 2023,
Art. no. 121000.
[34] J. Li, X. Tong, J. Liu, and L. Cheng, “An efficient federated learning
system for network intrusion detection,” IEEE Syst. J., vol. 17, no. 2,
pp. 2455–2464, Jun. 2023.
[35] M. M. Rashid, S. U. Khan, F. Eusufzai, M. A. Redwan, S. R. Sabuj, and M.
Elsharief, “A federated learning-based approach for improving intrusion
detection in industrial Internet of Things networks,” Network, vol. 3, no. 1,
pp. 158–179, 2023.
[36] R. Karmakar, G. Kaddoum, and O. Akhrif, “A novel federated learningbased smart power and 3D trajectory control for fairness optimization in
secure UAV-assisted MEC services,” IEEE Trans. Mobile Comput., vol. 23,
no. 5, pp. 4832–4848, May 2024.
[37] H. Nguyen and R. Kashef, “TS-IDS: Traffic-aware self-supervised learning for IoT network intrusion detection,” Knowl.-Based Syst., vol. 279,
2023, Art. no. 110966.
[38] R. Xu, G. Wu, W. Wang, X. Gao, A. He, and Z. Zhang, “Applying selfsupervised learning to network intrusion detection for network flows with
graph neural network,” Comput. Netw., vol. 248, 2024, Art. no. 110495.
[39] M. B. Anley, A. Genovese, D. Agostinello, and V. Piuri, “Robust DDoS
attack detection with adaptive transfer learning,” Comput. Secur., vol. 144,
2024, Art. no. 103962.
[40] O. Ajayi and A. Gangopadhyay, “DAHID: Domain adaptive host-based
intrusion detection,” in Proc. 2021 IEEE Int. Conf. Cyber Secur. Resilience,
2021, pp. 467–472.
[41] D. Gao, X. Yao, and Q. Yang, “A survey on heterogeneous federated
learning,” 2022, arXiv:2210.04505.

Li Lin (Member, IEEE) received the BS and MS degrees in mathematics from Guangxi Normal University, Guangxi Zhuang Autonomous Region, China,
in 2001 and 2004, respectively, and the PhD degree
in computer science from Beihang University, in
2009. She is currently an associate professor and a
supervisor of master’s candidates with the College of
Computer Science, Beijing University of Technology,
China. She has under taken research projects funded
by National Natural Science Foundation of China
and Beijing Natural Science Foundation and has been
participating in various research projects supported by the National High-Tech
Research and Development Program of China etc. Her current research interests
include cloud computing and edge computing security, Big Data security and
privacy protection, and artificial intelligence security.

ZhenKun Chen received the BS degree from the
School of Information, Beijing Wuzi University, Beijing, China, in 2022, and the MS degree from the
College of Computer Science, Beijing University of
Technology, Beijing, China, in 2025. His research
interests include federated transfer learning and intrusion detection technology. He has participated in
some research projects funded by National Natural
Science Foundation of China and Beijing Natural
Science Foundation.
PAPER_TEXT
