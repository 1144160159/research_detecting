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
# [223] Federated Deep Learning for Intrusion Detection in Consumer-Centric Internet of Things
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
编号：223
题名：Federated Deep Learning for Intrusion Detection in Consumer-Centric Internet of Things
年份：2023
DOI：10.1109/tce.2023.3347170
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2023.3347170.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、联邦学习、隐私保护与分布式协同
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\223.txt
- 原始字符数：60491
- 本次发送字符数：60491
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1610

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Federated Deep Learning for Intrusion Detection in
Consumer-Centric Internet of Things
Segun I. Popoola , Member, IEEE, Agbotiname Lucky Imoize , Senior Member, IEEE,
Mohammad Hammoudeh , Senior Member, IEEE, Bamidele Adebisi , Senior Member, IEEE,
Olamide Jogunola , Member, IEEE, and Abiodun M. Aibinu

Abstract—Consumer-centric Internet of Things (CIoT) will
play a pivotal role in the fifth industrial revolution (Industry 5.0)
but it exhibits vulnerabilities that can render it susceptible to
various cyberattacks. Recent studies have explored the potential
of Federated Learning (FL) for privacy-preserving intrusion
detection in IoT. However, the development of the FL models
relied on unrealistic and irrelevant network traffic data, while
also exhibiting limitations in terms of covered attack types and
classification scenarios. In this paper, we develop Federated
Deep Learning (FDL) models using three recent and highly
relevant datasets, covering a wide range of attack types as
well as binary and multi-class classification scenarios. Our
findings demonstrate that the FDL models not only achieve high
classification performance, comparable to traditional Centralized
Deep Learning (CDL) models, in terms of accuracy (99.60 ±
0.46%), precision (92.50 ± 8.40%), recall (95.42 ± 6.24%), and
F1 score (93.51 ± 7.76%) but also exhibit superior computational efficiency compared to their CDL counterparts. The FDL
approach reduces the training time by 30.52 − 75.87%. These
classification performance and computational efficiency were
achieved through multiple rounds of distributed local training in
FDL. Therefore, the proposed FDL framework presents a robust
security solution for designing and deploying a resilient CIoT.
Index Terms—Federated learning, intrusion detection, cyber
security, deep learning, Industrial Internet of Things.

I. I NTRODUCTION

T

HE FIFTH industrial revolution, commonly referred to
as Industry 5.0, has garnered significant attention and

Manuscript received 29 May 2023; revised 23 August 2023, 9 October
2023, and 8 November 2023; accepted 21 December 2023. Date of publication
25 December 2023; date of current version 26 April 2024. This work
was supported in part by the Engineering and Physical Sciences Research
Council under Grant EP/X039021/1, and in part by the European Research
Executive Agency (REA) under Project 101086387 (REMARKABLE).
(Corresponding author: Segun I. Popoola.)
Segun I. Popoola and Olamide Jogunola are with the Department of
Computing and Mathematics, Manchester Metropolitan University, M1 5GD
Manchester, U.K. (e-mail: segunpopoola@ieee.org).
Agbotiname Lucky Imoize is with the Department of Electrical and
Electronics Engineering, Faculty of Engineering, University of Lagos, Lagos
100213, Nigeria, and also with the Department of Electrical Engineering and
Information Technology, Institute of Digital Communication, Ruhr University,
44801 Bochum, Germany.
Mohammad Hammoudeh is with the Department of Information and
Computer Science, King Fahd University of Petroleum and Minerals, Dhahran
31261, Saudi Arabia.
Bamidele Adebisi is with the Department of Engineering, Manchester
Metropolitan University, M1 5GD Manchester, U.K.
Abiodun M. Aibinu is with the Department of Mechatronics, Federal
University of Technology, Minna 920101, Nigeria.
Digital Object Identifier 10.1109/TCE.2023.3347170

recognition within the industrial sector, owing to its extensive
advantages. This is still an open and evolving concept with
no generally acceptable definition or standard yet. However,
according to the European Commission report [1], “Industry
5.0 recognizes the power of industry to achieve societal
goals beyond jobs and growth to become a resilient provider
of prosperity, by making production respect the boundaries
of our planet and placing the well-being of the industry
worker at the center of the production process.” The vision of
Industry 5.0 revolves around sustainability, human-centricity,
and resiliency, embodying a forward-thinking approach to
industrial development [2].
Consumer-centric Internet of Things (CIoT) will play a
pivotal role in the fifth industrial revolution (Industry 5.0) but it
exhibits vulnerabilities that can render it susceptible to various
cyberattacks. Moreover, the unlawful exploitation of critical
user information within the CIoT poses significant risks to
trust, security, and can potentially lead to the collapse of the
system. Consequently, CIoT must be resilient to cyberattacks
to ensure the confidentiality, integrity, and availability of data
and infrastructure.
Artificial Intelligence (AI) can simulate human intelligence,
and this is crucial in building resilient CIoT. In particular,
Machine Learning (ML) and Deep Learning (DL) models
can be developed to automatically detect cyber-attacks in
IIoT systems. In Centralized ML (CML) and Centralized DL
(CDL), distributed data from multiple sources are transmitted
to a central location, such as a cloud server, for storage,
processing, and model training. However, these centralized
approaches face critical privacy concerns, high communication
overhead, and computational complexity [3].
Federated Learning (FL) is a decentralized and privacypreserving approach for ML and DL [4]. It offers lower
communication overhead and computational complexity compared to the conventional centralized approach. Distributed
network traffic data may contain private and sensitive
information about users and this poses a high risk of privacy
leakage in CDL [5]. Furthermore, the current strict data
privacy protection laws, such as the European Union’s General
Data Protection Regulation (GDPR)1 and the Consumer
Privacy Bill of Rights in the United States of America,
necessitates the adoption of a privacy-preserving DL approach.

1 https://gdpr.eu/

c 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1558-4127 
See https://www.ieee.org/publications/rights/index.html for more information.

POPOOLA et al.: FDL FOR INTRUSION DETECTION IN CIoT

In this paper, we propose FDL approach for network
intrusion detection in CIoT to address the limitations of CDL
method. Our objective is to develop FDL models for collaborative and privacy-preserving network intrusion detection
in CIoT while ensuring high classification performance and
computational efficiency. Although there are some related
works in the literature, previous studies used outdated and
irrelevant data sets to develop FL models. Furthermore, the
coverage of attack types and classification scenarios was
limited in those studies. Later in Section II, we will go into
a comprehensive review of the relevant literature. The main
contributions of this paper can be summarized as follows.
1) We propose an FDL method that utilizes a Deep Neural
Network (DNN) model architecture for local training at
the network edge. This method is designed for privacypreserving, network-based intrusion detection in CIoT.
2) We train and evaluate multiple FDL models using
three most relevant and recent datasets (i.e., X-IIoTID,
Edge-IIoTset, and WUSTL-IoT-2021) to assess the classification performance and computational efficiency of
the proposed method. The evaluation metrics include
accuracy, recall, precision, F1 score, training time, and
testing time.
3) We conduct a comprehensive investigation to validate
the effectiveness of the FDL models in both binary and
multiclass classification scenarios. We then compare the
classification performance and computational efficiency
of the FDL models with traditional CDL models.
The remaining parts of the paper are organized as follows: Section II provides a review of the related work.
Section III presents the security threats and data distribution
in CIoT datasets. Section IV discusses the centralized and
federated deep learning processes for intrusion detection in
CIoT. Section IV analyzes and discusses the results of our
experiments. Finally, in Section V, we summarize our findings
and provide directions for future research.
II. R EVIEW OF R ELATED W ORK
In the literature, researchers used different datasets to
develop and evaluate the effectiveness of FL models for
intrusion detection in IoT systems. The list of these datasets
is presented in Table I. However, these datasets are not
suitable for efficient network-based intrusion detection in CIoT
systems [6], [7]. For instance, the Bitcoin Transactions and
Ethereum Classic (ETC) BigQuery datasets contain benign
and malicious cryptocurrency transaction information, which
are largely irrelevant to intrusion detection in CIoT. These
datasets are more suitable for anomaly and fraud detection in
a blockchain network.
The Power System dataset contains normal operation activities, natural events (short-circuit fault and line maintenance),
and attack events (remote tripping command injection, relay
setting change, and data injection). The features in the
dataset are electrical parameters collected from phasor measurement units within an electricity grid network. However,
the requirements and the operational patterns of CIoT are
different compared to power systems. Therefore, the relevant

1611

TABLE I
DATASETS U SED FOR FL M ODELS IN R ELATED W ORK

application of this dataset is limited to fault and attack
detection in power systems.
The Secure Water Treatment (SWaT), Water Distribution
(WADI), Gas Pipeline, and Water Storage Tank datasets
are popularly used for attack detection in specific industrial
process within the context of Industrial Control System (ICS).
These datasets depend highly on features related to sensor
measurements, actuators’ statuses, and specific parameters of
industrial packets, which limited their use for diverse industrial
systems.
Furthermore, the NSL-KDD, UNSW-NB15, CIC-IDS2017, CIC-IDS-2018, CIC-DDoS2019, and LITNET-2020 are
mostly relevant to intrusion detection in traditional computer
networks. These datasets provide the network traffic characteristics of attacks against traditional IT services but they
do not contain realistic CIoT systems’ activities, connection
protocols and services, diverse communication patterns, and
CIoT-specific attack behaviours. For instance, the data samples
in the NSL-KDD dataset were collected more than 20 years
ago. The testbed did not include any CIoT device because the
dataset was created before the widespread adoption of CIoT.
In fact, the samples in the NSL-KDD dataset were simulated
to represent a typical United States Air Force’s local area
network.
The benign traffic samples in the CIC-DDoS2019 were generated by four traditional Personal Computers (PCs) using the
Hypertext Transfer Protocol (HTTP), HTTP Secure (HTTPS),
File Transfer Protocol (FTP), Secure Socket Shell (SSH), and
email communication protocols. An effective dataset should
cover a wide range of attacks that could be launched against
IIoT systems. However, some of the datasets have limited
attack types. For example, the CIC-DDoS2019 dataset contains
only Distributed Denial of Service (DDoS) attacks.
In recent research, the development of datasets such as the
X-IIoTID [7], Edge-IIoTset [6], and WUSTL-2021-IIoT [21]
datasets has been specifically tailored for intrusion detection
within the CIoT context. These datasets were created with
an emphasis on multi-platform connectivity protocols and
incorporate devices from a range of vendors. They exhibit
both connectivity and device agnosticism. This means that they
maintain compatibility with CIoT systems regardless of the
specific connectivity protocols, platforms, configurations, or

1612

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

TABLE II
R EVIEW OF R ELATED W ORK

[36], [37] focused on the Edge-IIoTset dataset only. Among
them, Ferrag et al. [6] explored all classification scenarios
in the dataset, Aouedi and Piamrat [35] considered only two
scenarios, i.e., 6-class and 15-class, and Houda et al. [14],
Friha et al. [34], Hamouda et al. [36], and Rashid et al. [37]
explored binary, 6-class, and 15-class scenarios, respectively.
To address these gaps in the literature, we propose to
develop and evaluate CDL and FDL models using all three
datasets and cover all classification scenarios in each dataset.
To the best of our knowledge, our study is the first to use the
WUSTL-IIoT-2021 dataset for FL-based intrusion detection
in CIoT. The proposed study is expected to contribute to the
development of more accurate and efficient intrusion detection
systems for CIoT.
III. C ENTRALIZED AND F EDERATED D EEP L EARNING
A. Deep Neural Network

the particular hardware and software deployed. This characteristic aptly mirrors the heterogeneity of network traffic and
system activities generated by various CIoT devices, connectivity protocols, and communication patterns, thus ensuring
the interoperability of CIoT systems. These datasets encapsulate the behaviours associated with novel CIoT connectivity
protocols, the activities of contemporary IIoT devices, and a
diverse array of attack types and scenarios. They comprise of
multi-view features, including network traffic, host resources,
logs, and alerts.
The taxonomy of related work that has utilized X-IIoTID,
Edge-IIoTset, and WUSTL-IIoT-2021 datasets for intrusion
detection in IIoT is presented in Table II. In previous work [7],
[25], [26], [27], [28], [29], [30], researchers have proposed
different ML and DL frameworks for intrusion detection in
IIoT based on the CL approach. However, none of these studies
explored the FL approach. Furthermore, none of the authors
evaluated their CL models using all three datasets.
Al-Hawawreh et al. [7] explored all classification scenarios
in the X-IIoTID dataset, but they did not cover the other
two datasets. On the other hand, authors in [25], [26], [27],
[28], [29], [30] focused on the WUSTL-IIoT-2021 dataset
only. However, some of them explored only binary classification [25], [26], [27], [29], while others focused on
5-class classification [28], [30]. Thus, no study has covered
all classification scenarios in all three datasets. Similarly, the
authors in [6], [14], [31], [32], [33], [34], [35], [36], [37]
explored the FL approach for intrusion detection in IIoT, but
none of them developed and evaluated their FL models using
all three datasets.
In addition, Makkar et al. [32], Hamouda et al. [36],
and Houda et al. [14] did not consider the CL approach.
Therefore, the performance and computation efficiency of
their FL models could not be compared with those of corresponding CL models. Some studies [6], [14], [34], [35],

A DNN architecture is used to learn the hierarchical
features, complex patterns, and non-linear relationships in the
network traffic data, X ∈ RM×Din , where M is the total number
of samples and Din is the number of input features. The
feedforward neural network is made up of an input layer,
three hidden layers, and an output layer. The first hidden layer
transforms a batch of the input data, Xbatch ∈ RN×Din and
produces:


(1)
Z1 = σ1 Xbatch · W1 + B1 ,
where N = M/Nbatch , N is the number of samples in a batch,
Nbatch is the number of batches in the entire dataset, Z1 ∈
RN×H1 is the output of the first hidden layer, W1 ∈ RDin ×H1 is
the weight, H1 is the number of hidden neurons, B1 ∈ RN×H1
is the bias, and (·) is a matrix dot multiplication. σ1 is a ReLU
activation function defined as:
f (a) = max(0, a).

(2)

The second hidden layer transforms Z1 and produces:


(3)
Z2 = σ1 Z1 · W2 + B2 ,
where Z2 ∈ RN×H2 is the output of the second hidden layer,
W2 ∈ RH1 ×H2 is the weight, H2 is the number of hidden
neurons, and B2 ∈ RN×H2 is the bias.
The third hidden layer transforms Z2 and produces:


(4)
Z3 = σ1 Z2 · W3 + B3 ,
where Z3 ∈ RN×H3 is the output of the third hidden layer,
W3 ∈ RH2 ×H3 is the weight, H3 is the number of hidden
neurons, and B3 ∈ RN×H3 is the bias.
Finally, the output layer transforms Z4 and produces:


(5)
Ypred = σ2 Z3 · Wout + Bout ,
where Ypred ∈ RN×Dout is the final output which represents the
predicted class probabilities, Wout ∈ RH3 ×Dout is the weight,
Dout is the number of output neurons, and Bout ∈ RN×Dout is
the bias. σ2 is a softmax activation function defined as:
ezj
σ2 (z)j = D

out zk
k=1 e

,

(6)

POPOOLA et al.: FDL FOR INTRUSION DETECTION IN CIoT

1613

where j = {1, . . . , Dout }, e is the base of natural logarithm, zj
is the jth element of the input vector z, and σ2 (z)j represents
the jth component of the output of the softmax function applied
to z.
B. Centralized Deep Learning
In CDL, all the participating CIoT nodes are expected to
send their private network traffic data to a cloud server for
aggregation and global model training. In this case, the DNN
model is trained centrally with all the data in the training sets
of each of the three datasets. The predicted probabilities of
the DNN model, Ypred , is compared with the one-hot encoded
labels, Ytrue . The categorical cross-entropy loss function (φ)
is used to measure the differences between Ypred and Ytrue as
follows:
N





Ytrue (i) log Ypred (i)
L = φ Ypred , Ytrue = −

(7)

n=1

To reduce the training losses, the weights and biases of
the DNN model are adjusted over E epochs using the
Adam [40] and RMSprop optimizers (), as recommended
in [6], [7], [21]. The learning rate (η) was set to 0.001 to
ensure model convergence.

Algorithm 1: Model Aggregation for FDL
1: Initialize K = 10
2: Initialize R = 10
3: Initialize server model parameters W (0)
4: for r = 1 to R do
5:
for k = 1 to K do
6:
Set the client model parameters
(r)
7:
Wk = W (r)
8:
Train the client model on its local data Dk
9:
Wk(r+1) = Wk(r) − η∇φk (Wk(r) , Dk )
10:
end for
11:
Aggregate the
parameters
local models’
(r+1)
12:
W (r+1) = K1 K
W
k=1 k
13: end for

CIoT edge nodes have updated their respective local DNN
models, they send their parameters to the cloud server. Then,
the server aggregates the local model updates to improve the
classification performance of the FDL model. The updated
FDL model parameters, W r+1 , are calculated as the average
of the parameters of all the local DNN models:
W (r+1) =

C. Federated Deep Learning
The FDL is modeled as a collaborative learning process
which involves a cloud server and K distributed edge nodes
in an CIoT network. Due to the resource-constraints in some
CIoT devices, the local training is performed at the edge
nodes close to the devices based on the concept of edge
computing. The integration of edge computing with federated
learning in the CIoT domain offers a powerful solution to
the challenges of privacy, network efficiency, latency, and
resource limitations. It empowers edge devices to contribute
meaningfully to model training while staying within their
operational constraints. Thus, a global DNN model (also
known as FDL model) and K local DNN models are created
using the same hyperparameters. Similarly, the weights of the
local DNN models are set to be the same as those of the FDL
model. The local DNN models are trained with their respective
private training data for a single epoch. At the end of the
training, the weights of the local DNN models are sent to the
cloud server for aggregation using the FedAvg algorithm [4].
The model aggregation process for FDL is described in
Algorithm 1. Each CIoT edge node, k ∈ {1, . . . , K}, sets its
local DNN model to the initial weights of the global DNN
model, W (r=0) . The CIoT edge node then trains its local DNN
model on its private data, Dk ∈ {D1 , . . . , DK }. The updated
local model parameters, Wkr+1 , are computed as:


Wk(r+1) = Wk(r) − η∇φk Wk(r) , Dk ,
(8)
where, φk is the categorical loss function for the local DNN
model on CIoT edge node k’s private data, η is the rate at
which the learning moves towards a minimum of the loss
function, and ∇(·) is the gradient of the categorical loss
function with respect to the model parameters. After all the

1  (r+1)
Wk
K
K

(9)

k=1

The averaging method ensures that each IIoT edge node’s
model contributes equally to the global model, regardless of
the size or distribution of its private data.
D. Experiments
We conducted several experiments to train and test the
proposed CDL and FDL models for network intrusion detection in CIoT environment using the X-IIoTID, Edge-IIoTset,
and WUSTL-IIoT-2021 datasets. The experimental setup for
the development of the models involves both computer hardware and software, as presented in Table III.
The computation involves the use of Central Processing
Unit (CPU), Random Access Memory (RAM), and Graphical
Processing Unit (GPU). A special software framework, known
as Compute Unified Device Architecture (CUDA),2 was used
to gain direct access to the GPU’s virtual instruction set
and parallel computational elements. The computer program
was written using the Python programming language. Scikitlearn,3 Pandas,4 and Numpy5 libraries were used for data
preprocessing, while TensorFlow and Keras frameworks were
used for the development of the CDL and FDL models.
1) Data Pre-Processing: The effectiveness of CDL and
FDL models can be influenced by a range of factors. These
factors encompass the quality of the training data, the relevance of network traffic features, the dataset’s size and
representativeness, and the complexity of the classification
problem at hand. These considerations guided the selection of
2 https://developer.nvidia.com/cuda-toolkit
3 https://scikit-learn.org/stable/
4 https://pandas.pydata.org/
5 https://numpy.org/

1614

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

TABLE III
H ARDWARE AND S OFTWARE S PECIFICATIONS

TABLE IV
C ENTRALIZED DATA D ISTRIBUTION FOR X-II OTID DATASET

TABLE V
C ENTRALIZED DATA D ISTRIBUTION FOR E DGE -II OT SET DATASET

the most pertinent datasets, namely X-IIoTID, Edge-IIoTset,
and WUSTL-IIoT-2021, while also highlighting the necessity
of data preprocessing.
X-IIoTID dataset comprises 65 network traffic features
and 820,834 network traffic samples. These samples can be
classified into three distinct scenarios: binary, 10-class, and
19-class, as presented in Table IV.
Edge-IIoTset dataset encompasses 61 network traffic features and 1,909,671 network traffic samples. These samples
are categorized into three distinct scenarios: binary, 6-class,
and 15-class, as presented in Table V.
WUSTL-IIoT-2021 dataset comprises 1,194,464 network
traffic samples characterized by 47 distinct features. These

TABLE VI
C ENTRALIZED DATA D ISTRIBUTION FOR WUSTL-II OT-2021 DATASET

samples are grouped into two primary scenarios: binary and
5-class, as presented in Table VI.
In preparation for the model development phase, the three
datasets were transformed to ensure they were in suitable
for effective learning. This process of data preprocessing
encompassed several key steps, including data cleaning, feature scaling, and data partitioning. In the data cleaning stage,
efforts were made to remove duplicate samples, redundant
features, and instances with missing values. To enhance model
convergence, the features of the datasets were normalized
using the min-max normalization method.
From the X-IIoTID dataset, we removed six features: date,
timestamp, source IP, destination IP, source port, and destination port. This action decreased the feature count from 65 to
59. Fifteen features, including time, source host, destination
host, sender IP address, target IP address, file data, full
request URI, transmit timestamp, request URI query, TCP
options, TCP payload, TCP source port, TCP destination port,
UDP port, and message, were removed from the Edge-IIoTset
dataset, reducing the feature count from 61 to 46.
For the WUSTL-IIoT-2021 dataset, we eliminated six features: start time, last time, source address, destination address,
source IP identifier, and destination IP identifier, thereby
reducing the feature count from 47 to 41. The datasets’
categorical features and labels were converted into numerical
data through the application of one-hot encoding. The EdgeIIoTset dataset contained seven categorical features that were
transformed into 49 numerical inputs, increasing the overall
feature count from 46 to 95.
Subsequently, each dataset was divided into a training set
comprising 70% of the data and a testing set comprising the
remaining 30%. This division aimed to facilitate thorough
model training and robust testing to evaluate the models’
performance.
2) Centralized and Federated Deep Learning: The classification performance of the CDL models depends on the
choice of the hyperparameters and regularization techniques.
Therefore, we employed the settings that were used in the
previous related studies [6], [7], [41] because they yielded
good classification performance. The hyperparameters of the
DNN model are presented in Table VII. The regularization
technique helped mitigate overfitting and improved generalization by adding a penalty term to the loss function. The careful
selection of hyperparameters led to optimal performance and
better convergence during training. These combined efforts
contributed to enhancing the overall effectiveness of the FDL
model in capturing complex patterns within the data.
For the FDL, each of the training sets for the X-IIoTID,
Edge-IIoTset, and WUSTL-IIoT-2021 datasets was divided

POPOOLA et al.: FDL FOR INTRUSION DETECTION IN CIoT

1615

TABLE VII
H YPERPARAMETERS FOR CDL AND FDL M ODELS

A. Centralized Deep Learning

among K(= 10) CIoT edge nodes as shown in Tables VIII-X,
respectively. The entire process was repeated for R(= 10)
communication rounds. This approach ensures that the FDL
model is trained on all the CIoT edge nodes’ private data
without needing to send them to the cloud server.
E. Performance Evaluation
In recent related studies [6], [32], [33], [34], [35], [36],
[37], [38], the classification performance of the CL and FL
models were evaluated based on accuracy, recall, precision,
and F1 score. There are other performance metrics, such
as Receiver Operating Characteristic (ROC) curve. However,
these four metrics (accuracy, recall, precision, and F1 score)
are popularly used and they have proved to be sufficient and
reliable in assessing the classification performance of ML, DL,
and FL models in different application scenarios. So, for the
sake of consistency and ease of result comparison, we decided
to evaluate the classification performance of the CDL and FDL
models in this study using the same metrics.
TP + TN
,
TP + TN + FP + FN
TP
,
Recall =
TP + FN
TP
Precision =
,
TP + FP
2 × Precision × Recall
,
F1 score =
Precision + Recall

Accuracy =

(10)
(11)
(12)
(13)

where True Positive (TP) is the number of malicious samples
in the testing set that were correctly classified. True Negative
(TN) is the number of benign samples that were correctly
classified. False Positive (FP) is the number of benign samples
that were misclassified as malicious. False Negative (FN) is
the number of malicious samples that were misclassified as
benign. Also, the computation efficiency of the models are
evaluated based on training time and testing time.
IV. R ESULTS AND D ISCUSSION
In this section, we analyze and discuss the classification
performance and the computational efficiency of the CDL
and FDL models in both binary and multi-class classification
scenarios for each of the three datasets in this study.

1) X-IIoTID: Table XI
presents
the
classification
performance of the CDL model on the X-IIoTID dataset. The
model correctly identified 99.55% of benign and 98.48% of
malicious samples in the binary scenario, signifying efficient
detection with very few false alarms. In the 10-class scenario,
the model correctly classified over 97% of samples in six
categories but misclassified 14.15% of C&C, 5.66% of
crypto ransomware, 15.64% of exploitation, and 5.78% of
reconnaissance samples due to class imbalance in the training
set. In the 19-class scenario, the CDL model accurately
classified over 92% of samples for most classes. However, the
false negative rates were 21.7% for C&C, 12.92% for CoAP
scanning, 40.91% for fuzzing, 23.81% for MITM, 15.82% for
shell, and 39.44% for TCP relay attacks, attributed to class
imbalance in the training set.
The model effectively detects many types of attacks,
yet exhibits higher false negative rates for C&C, CoAP
scan, fuzzing, MITM, shell, and TCP relay attacks. These
results show that while the CDL model is generally
effective in network intrusion detection, its classification
performance varies across different types of attacks. The
higher false negative rates for specific attack categories will
potentially make CIoT systems more vulnerable to these
types of intrusions. Therefore, there is a need to generate and include more samples of these attack classes in
the training set. Alternatively, data-level techniques (e.g.,
oversampling, undersampling, hybrid) and algorithmic solutions (e.g., cost-sensitive learning, re-weighting, threshold
moving) may be explored to improve the training set
balance.
2) Edge-IIoTset: Table XII presents the classification
performance of the CDL models trained and tested on the
Edge-IIoTset dataset. In the binary scenario, the CDL model
correctly classified all the benign and malicious samples,
demonstrating its ability to distinguish between benign and
malicious network traffic without any errors.
In the 6-class scenario, the CDL model correctly identified
over 98% of samples in each of three classes, namely benign,
DoS/DDoS, and MITM. However, due to class imbalance in
the training set, the model misclassified 24.6% of information
gathering samples, 11.66% of injection samples, and 51.09%
of malware samples. Thus, the model effectively detects
benign traffic and DoS/DDoS and MITM attacks, but struggles
with identifying information gathering, injection, and malware
attacks.
In the 15-class scenario, the CDL model correctly classified
over 93% of the samples across benign, backdoor, DDoS, and
MITM classes. Yet, the model misclassified 15.58% to 66.71%
of samples in the fingerprinting, password, port scanning,
ransomware, SQL injection, uploading, vulnerability scanning,
and XSS classes, primarily due to the class imbalance in the
training set. Consequently, while the model excels at detecting
benign traffic, backdoor, DDoS, and MITM attacks, it has a
higher false negative rate when identifying attacks within the
aforementioned classes.
3) WUSTL-IIoT-2021: Table XIII presents the accuracy,
recall, precision, and F1 score of the CDL models trained

1616

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

TABLE VIII
F EDERATED DATA D ISTRIBUTION FOR X-II OTID DATASET

TABLE IX
F EDERATED DATA D ISTRIBUTION FOR E DGE -II OT SET DATASET

TABLE X
F EDERATED DATA D ISTRIBUTION FOR WUSTL-II OT-2021 DATASET

and tested on the WUSTL-IIoT-2021 dataset. In binary
classification, the CDL model correctly identified all benign
instances and 99.87% of malicious instances, confirming

its effectiveness in distinguishing network traffic types with
virtually no false positives and minimal false negatives. For
the 5-class classification, it correctly identified over 99% of

POPOOLA et al.: FDL FOR INTRUSION DETECTION IN CIoT

TABLE XI
P ERFORMANCE OF C ENTRALIZED D EEP L EARNING M ODELS
BASED ON X-II OTID DATASET

1617

TABLE XIII
P ERFORMANCE OF C ENTRALIZED D EEP L EARNING M ODELS
BASED ON WUSTL-II OT-2021 DATASET

TABLE XIV
C OMPUTATION E FFICIENCY OF C ENTRALIZED D EEP L EARNING M ODELS

TABLE XII
P ERFORMANCE OF C ENTRALIZED D EEP L EARNING M ODELS
BASED ON E DGE -II OT SET DATASET

set. Despite its excellence in detecting benign, DoS, and
reconnaissance traffic, the model shows higher false negative
rates for backdoor and command injection attacks.
4) Computation Efficiency: Table XIV presents the duration required to train and test the CDL models utilizing
the X-IIoTID, Edge-IIoTset, and WUSTL-IIoT-2021 datasets,
in the context of both binary and multi-class classification
scenarios. The average training times for the models, using
the three datasets, were 215.36, 378.87, and 301.75 seconds,
respectively. The training duration exhibited variation depending on the number of samples present in the training set of the
employed dataset. A larger training set size correlated with a
more extended training period.
Conversely, the trained models required an average of
3.14, 7.17, and 4.30 seconds to categorize samples in the
testing sets for each of the three datasets, respectively. Similar
to the training duration, the testing time was also directly
proportional to the size of the samples in the testing set.
B. Federated Deep Learning

samples in benign, DoS, and reconnaissance classes. However,
it misclassified 21.54% of backdoor and 10.26% of command
injection instances due to the class imbalance in the training

1) X-IIoTID Dataset: Figure 1 shows the FDL model’s
performance in a binary classification scenario using the XIIoTID dataset. The model’s classification accuracy improved
with increasing communication rounds between clients and
the aggregation server. After ten rounds, the model reached
an accuracy of 98.56%, a recall of 98.53%, a precision
of 98.60%, and an F1 score of 98.55%, closely aligning
with that of the CDL model with a marginal difference of
0.45 − 0.49%.
Within the context of a 10-class classification scenario,
Figure 2 shows the performance of the FDL model that was
trained and tested with the X-IIoTID dataset. The model’s classification accuracy improved as the number of communication
rounds between clients and the aggregation server increased.
At the end of the tenth communication round, the model

1618

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Fig. 1. Performance of FDL model in binary scenario based on X-IIoTID
dataset.

Fig. 4. Performance of FDL model in binary scenario based on Edge-IIoTset
dataset.

Fig. 2. Performance of FDL model in 10-class scenario based on X-IIoTID
dataset.

Fig. 5. Performance of FDL model in 6-class scenario based on Edge-IIoTset
dataset.

Fig. 3. Performance of FDL model in 19-class scenario based on X-IIoTID
dataset.

attained an optimal performance with an accuracy of 99.71%,
recall of 94.55%, precision of 96.47%, and an F1 score of
95.47%. The performance is comparable to that of the CDL
model, with only a negligible difference of 0.02 − 0.82%.
The performance of the FDL model in a 19-class classification scenario, trained and tested with the X-IIoTID dataset, is
illustrated in Figure 3. The model’s classification performance
improved with an increase in the number of communication
rounds between clients and the aggregation server. Notably,
the model achieved optimal performance with an accuracy
of 99.35%, recall of 74.98%, precision of 79.83%, and an
F1 score of 75.24% after the 25th communication round.
These results are comparable to those obtained with the CDL
model, with a difference of only 0.2 − 4.37%.

2) Edge-IIoTset Dataset: Figure 4 shows the performance
of the FDL model which was trained and tested with the
Edge-IIoTset dataset within the context of binary classification
scenario. Impressively, the model achieved a perfect classification performance with an accuracy, recall, precision, and
F1 score of 100%. Of particular interest, the FDL model’s
performance was identical to that of the CDL model. These
results indicate the suitability and effectiveness of the FDL
model for binary classification tasks, while also highlighting
its parity with the CDL model in terms of performance
outcomes.
Figure 5 illustrates the performance of the FDL model
trained and tested using the Edge-IIoTset dataset within the
context of a 6-class classification scenario. The classification
performance of the model exhibited an improvement with
increasing rounds of communication between clients and the
aggregation server. The optimal performance was achieved
at the end of the twenty-first communication round with an
accuracy of 98.80%, recall of 84.57%, precision of 90.85%,
and an F1 score of 86.23%. These results demonstrate that the
FDL model’s performance is comparable to that of the CDL
model, with a negligible difference of 0.03 − 0.73%.
Figure 6 shows the effectiveness of the FDL model when
subjected to the Edge-IIoTset dataset under a 15-class classification setting. The FDL model’s classification capability
showed a marked improvement as the number of communication rounds between the clients and the aggregation server
increased. The optimal classification performance was attained
after the 25th round of communication, with the model

POPOOLA et al.: FDL FOR INTRUSION DETECTION IN CIoT

Fig. 6. Performance of FDL model in 15-class scenario based on EdgeIIoTset dataset.

1619

Fig. 8. Performance of FDL model in 5-class scenario based on WUSTLIIoT-2021 dataset.
TABLE XV
C OMPUTATION E FFICIENCY OF F EDERATED D EEP L EARNING M ODELS

Fig. 7. Performance of FDL model in binary scenario based on WUSTLIIoT-2021 dataset.

achieving an accuracy of 98.80%, recall of 84.57%, precision
of 90.85%, and an F1 score of 86.23%. These results prove
that the FDL model can perform comparably to the CDL
model, with a negligible deviation of 0.04 − 2.43%.
3) WUSTL-IIoT-2021 Dataset: The performance of the
FDL model, trained and tested with the WUSTL-IIoT2021 dataset in a binary classification scenario, is depicted
in Figure 7. The classification performance of the model
increased with an increase in the number of communication
rounds between the clients and the aggregation server. The
model achieved a remarkable accuracy of 99.39%, a recall of
99.86%, a precision of 99.95%, and an F1 score of 99.90%.
This performance is comparable to that of the CDL model,
with only a marginal difference of 0.02 − 0.08%.
Figure 8 illustrates the performance of the FDL model,
which was both trained and tested using the WUSTL-IIoT2021 dataset for a 5-class classification scenario. The model’s
classification performance improved as the number of communication rounds between clients and the aggregation server
increased. The FDL model achieved an accuracy of 99.99%,
a recall of 94.60%, a precision of 96.27%, and an F1 score
of 95.38%. This level of performance is comparable to that of
the CDL model, with only a slight difference of 0 − 0.68%.
4) Computation Complexity: Table XV presents the training and testing duration for FDL models utilizing three
different datasets, namely X-IIoTID, Edge-IIoTset, and
WUSTL-IIoT-2021, in both binary and multi-class classification settings. The average duration of training the models
using the three datasets was 52.73, 263.22, and 72.80 seconds,

respectively. The training time was observed to vary based on
the size of the training set used in each dataset, with larger sets
requiring a longer duration for training. Our findings indicate
that FDL models have significantly faster training times, with
30.52 − 75.87% lower training times than CDL models.
By contrast, the average time required by the trained models
to classify the testing set samples for the corresponding
datasets was 3.05, 7.01, and 4.16 seconds, respectively. The
duration of testing was found to be directly proportional to the
size of the testing set employed in each dataset, mirroring the
trend observed in training. Notably, our findings indicate that
the FDL model exhibited similar testing times to those of the
CDL model.
C. Discussion
In this study, we considered three distinct threat models
that are relevant to CIoT environment. A high classification
performance when the X-IIoTID dataset was used implies that
the CDL and FDL models can effectively detect and prevent
the nine attack scenarios: reconnaissance, weaponization,
exploitation, lateral movement, C&C, exfiltration, tampering,
crypto ransomware, and RDoS.
Reconnaissance involves several potential actions for attackers including: (i) scanning the target machine to gather general
information, such as listening ports, operating system details,
and available services; (ii) identifying known vulnerabilities
and misconfigurations; (iii) discovering system or software
errors and exceptions; and (iv) detecting available resources
within the target environment. Weaponization enables attackers
to gain entry into the target environment. This could occur
through methods like brute force attacks, dictionary attacks,
or exploits by malicious insiders.

1620

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Exploitation entails attackers capitalizing on known vulnerabilities within the target to establish a reverse TCP
shell or initiate a Man-in-the-Middle (MITM) attack. Lateral
movement empowers attackers to navigate further within
the target environment, establishing a stronger foothold and
compromising additional systems and networks. This could
involve accessing MQTT cloud broker subscriptions and
Modbus register readings, as well as infiltrating the mail server
through TCP relay attacks. C&C allows attackers to establish
communication channels between compromised machines and
their servers. This facilitates the transmission of commands,
enabling the attackers to gain control over compromised
systems.
Exfiltration encompasses the theft of private and sensitive
data from compromised machines using techniques such as
compression and obfuscation. Tampering involves intentional
manipulation, destruction, or alteration of information on
compromised machines, often through methods like false
data injection or counterfeit notifications. Crypto ransomware
revolves around attackers encrypting critical data on compromised machines and subsequently demanding cryptocurrency
payments in exchange for providing the decryption key. RDoS
involves attackers threatening to launch DDoS attacks against
the target’s machines unless a ransom is paid.
For the Edge-IIoTset dataset [6], a high classification
performance implies that the CDL and FDL models can
effectively detect and prevent the following attack vectors:
information gathering, DoS/DDoS attack, MITM attack, injection attack, and malware attack. DoS/DDoS attacks can be
executed using methods like TCP SYN, UDP, HTTP, or ICMP
flooding, causing a target system to become overwhelmed and
unavailable.
Information gathering can acquire crucial information about
target machines through techniques such as port scanning,
OS fingerprinting, and vulnerability scanning. MITM attacks
- the adversaries aim to compromise and manipulate the
communication flow between two endpoints that assume
they are communicating directly. Spoofing the Domain Name
System (DNS) or the Address Resolution Protocol (ARP) are
common methods. Injection attacks seek to compromise the
confidentiality and integrity of a target machine by injecting
malicious scripts into websites, altering a running Structured
Query Language (SQL) query, or uploading malware onto Web
servers.
Malware attacks take forms such as backdoors, password
cracking, or ransomware, all of which can lead to unauthorized access, data breaches, or system disruption. Finally, a
high classification performance when the WUSTL-IIoT-2021
dataset was used implies that the CDL and FDL models
can effectively detect and prevent reconnaissance, command
injection attacks, DoS attacks, and backdoor attacks in IIoT
environment.
V. C ONCLUSION
In this paper, we developed FDL models for privacypreserving network intrusion detection in CIoT networks using
three recent and relevant datasets (X-IIoTID, Edge-IIoTset,

and WUSTL-IIoT-2021), and covered all the binary and
multi-class classification scenarios in the datasets. The results
of this study show that, across all classification scenarios, the
FDL models consistently achieved high performance in terms
of accuracy, recall, precision, and F1 score. This performance
was found to be comparable with that of the corresponding
CDL models.
In assessing the computational efficiency, we observed that
the training and testing times for the models were dependent
on the size of the respective training and testing sets for each
dataset. As expected, larger datasets required longer duration
for training and testing. Importantly, our findings indicate that
the FDL models exhibited significantly faster training times
compared to the CDL models, while maintaining comparable
testing times. The findings of this research demonstrate that the
FDL framework exhibits superior efficacy in achieving timely
and privacy-preserving intrusion detection in CIoT settings.
Moreover, this enhanced performance is attained without any
significant degradation in classification performance.
It is also important to note that the present study does
not address security and privacy concerns in FL framework,
which include issues like membership inference, model poisoning, and data poisoning. In future research, a combination
of cryptographic techniques and adversarial defenses, such
as differential privacy, homomorphic encryption, multi-party
computation, and blockchain, will be taken into consideration.
These measures aim to establish a secure and privacypreserving FL methodology for intrusion detection in the IIoT.

R EFERENCES
[1] M. Breque, L. De Nul, and A. Petridis, Industry 5.0: Towards a
Sustainable, Human-Centric and Resilient European Industry. Eur.
Union, Luxembourg City, Luxembourg, 2021.
[2] L. Zong, F. H. Memon, X. Li, H. Wang, and K. Dev, “End-to-end
transmission control for cross-regional industrial Internet of Things in
industry 5.0,” IEEE Trans. Ind. Informat., vol. 18, no. 6, pp. 4215–4223,
Jun. 2022.
[3] S. I. Popoola, R. Ande, B. Adebisi, G. Gui, M. Hammoudeh, and
O. Jogunola, “Federated deep learning for zero-day botnet attack
detection in IoT-edge devices,” IEEE Internet Things J., vol. 9, no. 5,
pp. 3930–3944, Mar. 2022.
[4] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. y Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” in Proc. Artif. Intell. Statist., 2017, pp. 1273–1282.
[5] S. I. Popoola, G. Gui, B. Adebisi, M. Hammoudeh, and H. Gacanin,
“Federated deep learning for collaborative intrusion detection in heterogeneous networks,” in Proc. IEEE 94th Veh. Technol. Conf. (VTC-Fall),
2021, pp. 1–6.
[6] M. A. Ferrag, O. Friha, D. Hamouda, L. Maglaras, and H. Janicke,
“Edge-IIoTset: A new comprehensive realistic cyber security dataset of
IoT and IIoT applications for centralized and federated learning,” IEEE
Access, vol. 10, pp. 40281–40306, 2022.
[7] M. Al-Hawawreh, E. Sitnikova, and N. Aboutorab, “X-IIoTID: A
connectivity-agnostic and device-agnostic intrusion data set for industrial Internet of Things,” IEEE Internet Things J., vol. 9, no. 5,
pp. 3962–3977, Mar. 2022.
[8] A. Yazdinejad, A. Dehghantanha, R. M. Parizi, M. Hammoudeh,
H. Karimipour, and G. Srivastava, “Block hunter: Federated learning for
cyber threat hunting in blockchain-based iiot networks,” IEEE Trans.
Ind. Informat., vol. 18, no. 11, pp. 8356–8366, Nov. 2022.
[9] M. Abdel-Basset, N. Moustafa, and H. Hawash, “Privacy-preserved
generative network for trustworthy anomaly detection in smart grids: A
federated semisupervised approach,” IEEE Trans. Ind. Informat., vol. 19,
no. 1, pp. 995–1005, Jan. 2023.

POPOOLA et al.: FDL FOR INTRUSION DETECTION IN CIoT

[10] A. N. Jahromi, H. Karimipour, and A. Dehghantanha, “Deep federated
learning-based cyber-attack detection in industrial control systems,” in
Proc. 18th Int. Conf. Privacy, Security Trust (PST), 2021, pp. 1–6.
[11] X. Huang, J. Liu, Y. Lai, B. Mao, and H. Lyu, “EEFED: Personalized
federated learning of execution&evaluation dual network for CPS intrusion detection,” IEEE Trans. Inf. Forensics Security, vol. 18, pp. 41–56,
2023.
[12] O. Aouedi, K. Piamrat, G. Muller, and K. Singh, “Federated semisupervised learning for attack detection in industrial Internet of Things,” IEEE
Trans. Ind. Informat., vol. 19, no. 1, pp. 286–295, Jan. 2023.
[13] B. Li, Y. Wu, J. Song, R. Lu, T. Li, and L. Zhao, “DeepFed: Federated
deep learning for intrusion detection in industrial cyber–physical
systems,” IEEE Trans. Ind. Informat., vol. 17, no. 8, pp. 5615–5624,
Aug. 2021.
[14] Z. A. E. Houda, B. Brik, A. Ksentini, L. Khoukhi, and M. Guizani,
“When federated learning meets game theory: A cooperative framework
to secure IIoT applications on edge computing,” IEEE Trans. Ind.
Informat., vol. 18, no. 11, pp. 7988–7997, Nov. 2022.
[15] S. Islam, S. Badsha, S. Sengupta, I. Khalil, and M. Atiquzzaman,
“An intelligent privacy preservation scheme for EV charging infrastructure,” IEEE Trans. Ind. Informat., vol. 19, no. 2, pp. 1238–1247, Feb.
2023.
[16] J. Zhang, C. Luo, M. Carpenter, and G. Min, “Federated
learning for distributed IIoT intrusion detection using transfer
approaches,” IEEE Trans. Ind. Informat., vol. 19, no. 7, pp. 8159–8169,
Jul. 2023.
[17] M. Abdel-Basset, N. Moustafa, and H. Hawash, “Privacy-preserved
Cyberattack detection in industrial edge of things (IEoT): A blockchainorchestrated federated learning approach,” IEEE Trans. Ind. Informat.,
vol. 18, no. 11, pp. 7920–7934, Nov. 2022.
[18] P. Ruzafa-Alcázar et al., “Intrusion detection based on privacypreserving federated learning for the industrial IoT,” IEEE Trans. Ind.
Informat., vol. 19, no. 2, pp. 1145–1154, Feb. 2023.
[19] P. T. Duy, T. Van Hung, N. H. Ha, H. Do Hoang, and V.-H. Pham,
“Federated learning-based intrusion detection in SDN-enabled IIoT
networks,” in Proc. 8th NAFOSTED Conf. Inf. Comput. Sci. (NICS),
2021, pp. 424–429.
[20] A. Zainudin, R. Akter, D.-S. Kim, and J.-M. Lee, “FedDDoS: An
efficient federated learning-based DDoS attacks classification in SDNenabled IIoT networks,” in Proc. 13th Int. Conf. Inf. Commun. Technol.
Converg. (ICTC), 2022, pp. 1279–1283.
[21] M. Zolanvari, M. A. Teixeira, L. Gupta, K. K. M, and R. Jain, 2021,
“WUSTL-IIOT-2021 Dataset for IIoT cybersecurity research,” WUSTL.
[Online]. Available: http://www.cse.wustl.edu/ jain/iiot2/index.html
[22] H. Zhao et al., “An enhanced intrusion detection method for AIM of
smart grid,” J. Ambient Intell. Hum. Comput., vol. 14, pp. 1–13, Feb.
2023.
[23] H. C. Altunay and Z. Albayrak, “A hybrid CNN+ LSTM based intrusion
detection system for industrial IoT networks,” Eng. Sci. Technol., Int.
J., vol. 38, Feb. 2023, Art. no. 101322.
[24] P. L. S. Jayalaxmi, R. Saha, G. Kumar, M. Alazab, M. Conti,
and X. Cheng, “PIGNUS: A deep learning model for IDS in
industrial Internet-of-Things,” Comput. Secur., vol. 132, Sep. 2023,
Art. no. 103315.
[25] M. Zolanvari, Z. Yang, K. Khan, R. Jain, and N. Meskin, “TRUST
XAI: Model-agnostic explanations for AI with a case study on IIoT
security,” IEEE Internet Things J., vol. 10, no. 4, pp. 2967–2978, Feb.
2023.
[26] M. M. Alani, E. Damiani, and U. Ghosh, “DeepIIoT: An explainable deep learning based intrusion detection system for industrial
IOT,” in Proc. IEEE 42nd Int. Conf. Distrib. Comput. Syst. Workshops
(ICDCSW), 2022, pp. 169–174.
[27] M. Mohy-eddine, A. Guezzaz, S. Benkirane, and M. Azrour, “An
effective intrusion detection approach based on ensemble learning for
IIoT edge computing,” J. Comput. Virology Hack. Techn., vol. 19,
pp. 469–481, Nov. 2023.
[28] A. S. Dina, A. Siddique, and D. Manivannan, “A deep learning
approach for intrusion detection in Internet of Things using focal loss
function,” Internet Things, vol. 22, Jul. 2023, Art. no. 100699.
[29] M. M. Alani, “An explainable efficient flow-based industrial IoT
intrusion detection system,” Comput. Elect. Eng., vol. 108, May 2023,
Art. no. 108732.

1621

[30] T. Gaber, J. B. Awotunde, S. O. Folorunso, S. A. Ajagbe, and
E. Eldesouky, “Industrial Internet of Things intrusion detection method
using machine learning and optimization techniques,” Wireless Commun.
Mobile Comput., vol. 2023, Apr. 2023, Art. no. 3939895. [Online].
Available: https://doi.org/10.1155/2023/3939895
[31] M. Al-Hawawreh, E. Sitnikova, and N. Aboutorab, “Asynchronous peerto-peer federated capability-based targeted ransomware detection model
for industrial IoT,” IEEE Access, vol. 9, pp. 148738–148755, 2021.
[32] A. Makkar, T. W. Kim, A. K. Singh, J. Kang, and J. H. Park,
“Secureiiot environment: Federated learning empowered approach for
securing iiot from data breach,” IEEE Trans. Ind. Informat., vol. 18,
no. 9, pp. 6406–6414, Sep. 2022.
[33] P. Verma, J. G. Breslin, and D. O Shea, “FLDID: Federated
learning enabled deep intrusion detection in smart manufacturing industries,” Sensors, vol. 22, no. 22, p. 8974, 2022.
[34] O. Friha, M. A. Ferrag, M. Benbouzid, T. Berghout, B. Kantarci,
and K.-K. R. Choo, “2DF-IDS: Decentralized and differentially private federated learning-based intrusion detection system for industrial
IoT,” Comput. Security, vol. 127, Apr. 2023, Art. no. 103097.
[35] O. Aouedi and K. Piamrat, “F-BIDS: Federated-blending based intrusion
detection system,” Pervasive Mobile Comput., vol. 89, Feb. 2023,
Art. no. 101750.
[36] D. Hamouda, M. A. Ferrag, N. Benhamida, and H. Seridi, “PPSS:
A privacy-preserving secure framework using blockchain-enabled federated deep learning for industrial IoTs,” Pervasive Mobile Comput.,
vol. 88, Jan. 2023, Art. no. 101738.
[37] M. M. Rashid, S. U. Khan, F. Eusufzai, M. A. Redwan, S. R. Sabuj,
and M. Elsharief, “A federated learning-based approach for improving
intrusion detection in industrial Internet of Things networks,” Network,
vol. 3, no. 1, pp. 158–179, 2023.
[38] Z. A. El Houda, B. Brik, A. Ksentini, and L. Khoukhi, “A MECbased architecture to secure IoT applications using federated deep
learning,” IEEE Internet Things Mag., vol. 6, no. 1, pp. 60–63, Mar.
2023.
[39] M. Al-Hawawreh and M. S. Hossain, “Federated learning-assisted
distributed intrusion detection using mesh satellite nets for autonomous
vehicle protection,” IEEE Trans. Consum. Electron., early access, Sep.
25, 2023, doi: 10.1109/TCE.2023.3318727.
[40] D. P. Kingma and J. Ba, “Adam: A method for stochastic
optimization,” 2017, arXiv:1412.6980.
[41] M. Zolanvari, M. A. Teixeira, L. Gupta, K. M. Khan, and R. Jain,
“Machine learning-based network vulnerability analysis of industrial Internet of Things,” IEEE Internet Things J., vol. 6, no. 4,
pp. 6822–6834, Aug. 2019.

Segun I. Popoola (Member, IEEE) received the
B.Tech. degree in electronic and electrical engineering from the Ladoke Akintola University of
Technology, Ogbomoso, Nigeria in 2014, the M.Eng.
degree in information and communication engineering from the Department of Electrical and
Information Engineering, Covenant University, Ota,
Nigeria, in 2018, and the Ph.D. degree in cyber security and artificial intelligence from the Department
of Engineering, Faculty of Science and Engineering,
Manchester Metropolitan University, Manchester,
U.K., in 2022. His Ph.D. thesis on federated deep learning for botnet attack
detection in IoT networks was a product of an academic-industry partnership
project jointly funded by the department of engineering at Manchester
Metropolitan University and a cyber security company, Cyraatek Ltd UK.
He is a Lecturer with the Department of Computing and Mathematics,
Manchester Metropolitan University, U.K. He has published more than 100
research papers in reputable journals and conference proceedings, including
IEEE I NTERNET OF T HINGS J OURNAL, IEEE ACCESS, and IEEE Vehicular
Technology Conference. His research interests include wireless communications, machine/deep learning, cybersecurity, and the Internet of Things. He is
a Registered Engineer with the Council for the Regulation of Engineering in
Nigeria. In June 2022, he was endorsed as a Global Exceptional Talent by
the Royal Society.

1622

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Agbotiname Lucky Imoize (Senior Member, IEEE)
is a Lecturer with the Department of Electrical
and Electronics Engineering, University of Lagos,
Nigeria. Before joining the University of Lagos,
he was a Lecturer with the Bells University of
Technology, Nigeria. He also worked as a Core
Network Products Manager with ZTE, Nigeria, and
as a Network Switching Subsystem Engineer with
Globacom, Nigeria. He was awarded the Fulbright
Fellowship as a Visiting Research Scholar with the
Wireless@VT Laboratory, Bradley Department of
Electrical and Computer Engineering, Virginia Tech, USA, from 2017 to 2018.
He is a Research Scholar with Ruhr University Bochum, Germany, under the
sponsorship of the Nigerian Petroleum Technology Development Fund and the
German Academic Exchange Service (DAAD) through the Nigerian-German
Postgraduate Program. His research interests cover the fields of 6G wireless
communication systems, wireless security systems, and artificial intelligence.
He is the Vice Chair of the IEEE Communication Society, Nigeria Chapter,
and a Registered Engineer with the Council for the Regulation of Engineering
in Nigeria.

Olamide Jogunola (Member, IEEE) received the
B.Eng. degree in electrical engineering from the
University of Ilorin, Nigeria, in 2011, the M.Sc.
degree in networking and data communication from
Kingston University, U.K., in 2015, and the Ph.D.
degree in electrical engineering from Manchester
Metropolitan University, U.K., in 2020. She is a
Lecturer in Cyber Security and Smart Grids with
Manchester Metropolitan University (MMU). Her
research interests include energy transitions, local
energy markets, and the cyber security of critical
national infrastructure including smart grid. She was a Research Associate
on several industry and Government-funded projects. She was a recipient of
the MMU Department of Engineering Ph.D. Studentship. She was a PI on a
SuperGen Network/EPSRC-funded project and a Co-PI in a NWPST-funded
project on interlinked computing. She is currently an academic supervisor on
a KTP with Badger Energy.

Mohammad Hammoudeh (Senior Member, IEEE)
received the B.Sc. degree in computer communications from Arts Sciences and Technology University
in 2004, the M.Sc. degree in advanced distributed
systems from the University of Leicester in 2006,
and the Ph.D. degree in computer science from the
University of Wolverhampton in 2008. He is the
Saudi Aramco Chair Professor of Cyber Security
with the King Fahd University of Petroleum and
Minerals. His research interests include the applications of zero trust security to internet-connected
critical national infrastructures, blockchains, and other complex highly decentralized systems.

Bamidele Adebisi (Senior Member, IEEE) received
the B.S. degree in electrical engineering from
Ahmadu Bello University, Zaria, Nigeria, in 1999,
and the M.S. degree in advanced mobile communication engineering, and the Ph.D. degree in
communication systems from Lancaster University,
Lancaster, U.K., in 2003 and 2009, respectively. He was a Senior Research Associate with
the School of Computing and Communication,
Lancaster University from 2005 to 2012. He joined
Manchester Metropolitan University, Manchester,
U.K., in 2012, where he is currently a Professor in Intelligent Infrastructure
Systems. He has been involving in several commercial and government
projects focusing on various aspects of wireline and wireless communications.
He is particularly interested in the research and development of communication technologies for electrical energy monitoring/management, transport,
water, critical infrastructures protection, home automation, the IoTs, and cyber
physical systems. He has several publications and a patent in the research
area of data communications over power line networks and smart grid. He is
a member of IET.

Abiodun M. Aibinu received the Ph.D. degree from
International Islamic University Malaysia in 2010.
He is currently a Professor with the Department
of Mechatronics Engineering, Federal University of
Technology, Minna, Nigeria. He is also the ViceChancellor of Summit University, Offa, Nigeria.
His research interests include digital signal and
image processing, instrumentation and measurement,
intelligent system design, and artificial intelligence
with an emphasis on artificial neural networks and
genetic algorithm. He has participated and won
several awards at various international and national exhibitions and was
nominated for the 2012 Promising Researcher Award and a Best Teacher
Award at IIUM Malaysia. He has also won several research grant awards in
and outside Nigeria and has authored/coauthored several publications in both
local and international journals and conferences.
PAPER_TEXT
