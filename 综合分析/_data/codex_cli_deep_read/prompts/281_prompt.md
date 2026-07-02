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
# [281] Privacy-Preserving Few-Shot Traffic Detection Against Advanced Persistent Threats via Federated Meta Learning
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
编号：281
题名：Privacy-Preserving Few-Shot Traffic Detection Against Advanced Persistent Threats via Federated Meta Learning
年份：2023
DOI：10.1109/tnse.2023.3304556
来源：IEEE Transactions on Network Science and Engineering
PDF：paper/10.1109_tnse.2023.3304556.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：无
相关性：强相关，分数 11
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\281.txt
- 原始字符数：61107
- 本次发送字符数：61107
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 3, MAY/JUNE 2024

2549

Privacy-Preserving Few-Shot Traffic Detection
Against Advanced Persistent Threats via
Federated Meta Learning
Yilun Hu , Jun Wu , Senior Member, IEEE, Gaolei Li , Member, IEEE, Jianhua Li , Senior Member, IEEE,
and Jinke Cheng

Abstract—Advanced Persistent Threats (APT) utilizes multiple
zero-day vulnerabilities to threaten critical industrial infrastructure, having the characteristics of burst, unknown and crossdomain. To resist APT attacks, existing wisdom usually establish a
security monitoring platform that remotely links to the cloud-based
threat intelligence center. However, the real scenario where few
victim users are willing to share raw attack samples considering
privacy-preservation, such mentality is hysteretic and cannot identify APT attacks quickly without sacrificing additional incentives.
To address this issue, a novel privacy-preserving few-shot traffic
detection (PFTD) method based on federated meta learning (FML)
is proposed. The PFTD treats the APT detection task as a model
generalization optimization process, that transfers the learned
knowledge to identify local unknown samples. Client-side models
in FML achieve knowledge transferring by two-phase updating
over both support dataset and query dataset, while the server-side
model obtains global knowledge with model aggregation. These
processes compile useful knowledge against APT attacks. With a
novel wisdom, we obtained three advantages: 1) High accuracy
with a few attack samples; 2) Low latency detection for removing
rules matching process; 3) High personalizing to cross-domain
APT attacks. Extensive experiments based on multiple benchmark
datasets like CICIDS2017 and DAPT 2020 prove the superiority of
proposed PFTD.
Index Terms—Advanced persistent threats, federated meta
learning, few-shot traffic detection, privacy-preserving.

I. INTRODUCTION
RAFFIC detection system is an important research field in
computer system and network, it is used to detect network
intrusion behavior. However, traffic detection systems cannot
identify unknown attack behaviors [1]. In recent years, security incidents caused by unknown cyber attacks have emerged

T

Manuscript received 15 January 2023; revised 24 May 2023; accepted 2 July
2023. Date of publication 11 August 2023; date of current version 30 April 2024.
This work was supported in part by the National Nature Science Foundation of
China under Grants U21B2019, 62202303, and U20B2048, in part by Shanghai Sailing Program under Grant 21YF1421700, and in part by the Defence
Industrial Technology Development Program under Grant JCKY2020604B004.
Recommended for acceptance by Dr. He Huang. (Corresponding authors : Jun
Wu; Gaolei Li.)
The authors are with the School of Electronic Information and Electrical
Engineering, Shanghai Jiao Tong University, Shanghai 200240, China, and also
with the Shanghai Key Laboratory of Integrated Administration Technologies
for Information Security, Shanghai 200240, China (e-mail: huyilun1218@
sjtu.edu.cn; junwuhn@sjtu.edu.cn; gaolei_li@sjtu.edu.cn; lijh888@sjtu.edu.cn;
jinkecheng@sjtu.edu.cn).
Digital Object Identifier 10.1109/TNSE.2023.3304556

one after another, causing a huge economic stress around the
world. On May 2021, Colonial Pipeline, the largest oil product
pipeline operator in the United States, was attacked by a ransomware network from the hacker group Darkside. The group
exploited the vulnerability of the software to hack into central
systems, disrupt and steal the computer data, and also take
the pipeline systems that transport oil and gas in major cities
on the eastern seaboard offline. Since 2015, OceanLotus, an
APT organization in Southeast Asia, has carried out long-term
and continuous cyber attacks in China. The organization often
exploits 0-day/N-day vulnerabilities during intrusion and lateral
movement. During the Russian-Ukrainian war, the cyber-attacks
against Ukraine by groups such as APT28 and AgentTesla were
strategically used to support ground operations. The spy Trojans
and other malicious codes use custom or encrypted protocols to
establish covert communication channels and finally bypass the
detection of traditional security devices such as firewalls and
intrusion detection systems (IDSs). These new types of attacks,
especially APT attacks, have brought great challenges to traffic
detection technology.
r APT attacks have many characteristics such as burst, unknown and cross-domain. Existing traffic detection methods are limited by the fragmentation of threat intelligence
and tend to focus more on discovering locally known attack
behaviors.
r Due to privacy concerns or the desire to avoid embarrassment, original APT attack samples cannot be shared timely.
As a result, the defenders can only resort to remediation
and damage control after the attack has occurred.
To address the above challenges, introducing artificial intelligence (AI), Big Data analysis and cloud technology in the
APT detection field has become a trend [2], [3]. For example,
AI-based IDS systems aim to extract abnormal/normal features
from massive network traffic, and distinguishes whether it is benign or malicious traffic. The Big Data framework enhances the
ability of traffic inspection systems in understanding the increasingly complex data distribution of intrusion patterns [4]. The
introduction of cloud computing has enhanced the efficiency of
traditional traffic detection systems in the face of network attacks
with variability, invisibility and unpredictability [5]. Among
them, deep learning (DL) is considered to be the most important
enabling technique that may have great ability to discover APT
attacks. Deep learning-empowered methods utilizes deep neural
networks to perform representation learning on network traffic.

2327-4697 © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

2550

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 3, MAY/JUNE 2024

The broad range of applications of deep learning-empowered
methods includes both relationship-oriented deep learning in
which the detector trends to identify the combination methods of
each network attack tools with correlation analysis using Graph
Neural Networks [6], [7], and timing-oriented deep learning in
which the detector tends to judge the intent of a network attack
with the connections between traffic features and time sequence
using Recurrent Neural Networks [8], [9].
However, deploying DL-based APT detection systems in
cloud-side data centers faces with many challenges. First, cloudside computing struggles with leakage of the sensitive and confidential information; second, since the cloud-side computing
cannot integrate heterogeneous and dispersed threat intelligence
due to real-time constraints, it is difficult to discover efficient and
real-time unknown attacks. In addition, with the influx of a large
number of edge devices, different suppliers require personalized
security defence abilities. Therefore, it is particularly important
to deploy intelligent APT detection systems to discover unknown attack behaviors at the edge side. Recently, many studies
have focused on the construction of edge-side APT detection
systems. For example, Yuan et al. [10] designed a CNN-based
intrusion detection system and deployed it on the edge devices
to identify attack behaviors, which transferred data flows into
the form of images. Yet, although the DL-based APT detection
technology develops rapidly, there are still numerous challenges
when deploying it at the edge side:
r Due to the complexity and dynamic of the Internet environment, it is very difficult for existing traffic detection
methods to identify various types of APT attack behaviors
according to limited threat intelligence;
r Since massive heterogeneous devices are connected to edge
networks, it is difficult for existing APT detection methods
to identify the latest evolved attacks;
r Training a chatGPT-like pre-trained model that can fit all
local datasets on each edge device is very difficult for the
number of APT attack samples is usually nonpublic.
Federated meta-learning (FML) has been proved that it can
improve the personalization and generalization capabilities of
deep neural networks at edge devices. FML refers to combining
many edge devices (meta-learners) to train a large global metalearner by aggregating model parameters collected on the server.
This global learner has a strong generalization ability because
it has learnt many samples, a personalized model for each node
can be obtained by performing a few steps of gradient descent
using the Model-Agnostic Meta-Learning (MAML) algorithm
on edge devices. MAML retains the information of different
sub-tasks in the form of parameter updates during the training
process of each sub-task, so the model trained by meta-learning
has better generalization ability [11]. At the same time, FML
protects the privacy of each edge device. With the assistance of
FML, the global model can be personalized to fit the local data.
Therefore, in order to solve the problem of intrusion detection
in APT attacks which is difficult for edge-side smart devices to
deal with unknown behavior attacks in the context of federated
learning, with the help of the idea of FML, we propose an edge
synergy-empowered FML model for few-shot malicious traffic
detection against APT attacks. In our method, the malicious
traffic detection model is distributed by the central server, and
the edge-side nodes jointly maintain the central model using the

meta-learning method. At the same time, MAML algorithms
maintain the personalization of the local model. In the model
training phase, we deployed more than 400 edge devices to
simulate real distributed scenarios. All edge devices will jointly
maintain the central model. In the classification phase, we
compared the five-classification capabilities of two different
classification networks, FPN and Resnet, for malicious network
traffic.
The main contributions of our work are as follows.
1) A privacy-preserving few-shot traffic detection (PFTD)
framework against APT attacks is proposed based on
federated meta learning. In the PFTD training phase, only
10 samples in each type of attack methods participate in
the model updating process, maximizing the simulation
of real scenarios with a limited number of APT attack
samples. Besides, our proposed framework realizes the
detection function for unknown samples with leaving data
from local devices.
2) An edge synergy-empowered FML training algorithm is
also designed to improve the accuracy of proposed PFTD
framework. On each edge devices, the model-agnostic
meta learning (MAML) unit can quickly obtain a personalized FML model that adapts to local small sample
data through several steps of gradient descent. At the same
time, the great generalization ability brought by the global
model ensures that unknown samples can be identified,
according to its poor prediction values in the classification
results of each category.
3) To improve the adaptability of proposed PFTD to the heterogeneous threat intelligence samples collected by each
edge device, we also propose a novel support-query mutual
guidance mechanism to associate the support set and the
query set, and then quickly achieve a local personalized
model by fine-tuning.
The remainder of the article is organized as follows.
Section II discusses the related work. Section III formulates challenges, motivations and system model, while Section
IV describes our proposed FML method and training steps.
Section V introduces the experiment. Section VII draws conclusions.
II. RELATED WORK
In this section, we will first introduce the abnormal traffic
detection method for the APT attack, and then the research work
related to Federated Meta Learning is discussed.
A. Anomaly Traffic Detection Against APT Attacks
Personalized anomaly traffic detection system is a personalized network traffic anomaly detection method proposed by
us. Traditional network traffic anomaly detection methods often
use machine learning and deep learning frameworks to detect
abnormal network traffic. There are many machine learning
methods applied to network traffic anormaly detection, such
as random forest (RF), support vector machine (SVM), naive
Bayesian network (NBN), logistic regression and other methods.
Since traditional machine learning models only learn the attack
patterns of simple features in TCP/IP packets. The models often
exhibit high false positive rates [12]. Therefore, deep learning is

HU et al.: PRIVACY-PRESERVING FEW-SHOT TRAFFIC DETECTION AGAINST ADVANCED PERSISTENT THREATS

proposed, in which CNN can comprehensively learn the complex
hierarchical feature representation of TCP/IP data packets; RNN
can remember past information in a large number of TCP/IP
packets, and the detection efficiency is greatly improved. Xiao
et al. [13] proposed an intrusion detection model based on feature dimensionality reduction and convolutional neural network,
which extracts and analyzes data features for classification by
convolutional neural network. The experimental results show
that the prediction accuracy of the model can reach 94.00%.
Althubiti et al. [14] used a long short-term memory network,
a special recurrent neural network (RNN), to build an intrusion detection model, which achieved a prediction accuracy of
84.83% on the CICDS001 data set. In addition, many methods
has further improved the detection accuracy by combining the
models. Andresini et al. [15] proposed an intrusion detection
model that combines generative adversarial network (GAN)
and convolutional neural network (CNN). The model achieves
93.29% accuracy on the KDD99 data set. Hassan et al. [16]
building an intrusion detection model by combining a CNN
with a long short-term memory network. The experimental
results show that the prediction accuracy of the model can reach
97.17%.
In recent years, the design of edge-side intrusion detection
system has became a new research direction. Kumar et al. [17]
proposed the development of distributed intrusion detection
systems (DIDS) using emerging and promising technologies
such as blockchain on stable platforms in cloud infrastructure.
The collaborative intrusion detection system (CIDS) developed
by Sharma et al. [18] protects edge devices against cyber attacks such as denial of service (DoS) and distributed denial of
service (DDoS) under the multi-access edge computing (MEC)
architecture. After 2 years, Sharma et al. [19] proposed a new
pure edge-based hybrid CIDS architecture based on CIDS to
complement the previous work. Nie et al. [20] proposed a
GAN-based multi-stage deep learning framework to achieve
intrusion detection against multiple attacks at the edge network.
Yin et al. [21] proposed a data collaboration mechanism that
offloads the training model to distributed edge devices to achieve
cooperative privacy protection for IoT.
There are many detection methods for APT attacks. In recent years, APT attack detection methods based on provenance
graphs have achieved good results. The team at the University
of Illinois at Chicago proposed the SLEUTH [22] method in
2017. Based on log data, it uses causal relationship tracking and
provenance graphs to construct a model and finally reconstructs
APT attacks. On this basis, the team introduced two methods,
Poirot [9] and Holmes [7] in 2019. Poirot introduced cyber
threat intelligence (CTI) and graph matching algorithm based
on provenance graph. Holmes designed the high-level scenario
graph (HSG) to realize the mapping of low-level (log, alarm)
information to high-level. In 2021, the team further proposed
the Extrator [23] method. It introduces natural language processing (NLP) into the CTI report, so as to realize the precise
extraction of attack behavior in CTI. It also uses semantic
role labeling (SRL) for semantic analysis to understand the
relationship between attack behaviors and convert unstructured
text into provenance graphs. In addition, due to the lack of
explanation for decision-making in AI-based CTI and the massive deployment of edge devices, Li et al. [24] proposed an

2551

explainable intelligence-driven APT edge defense mechanism.
This approach increases the level of protection and defense
against APTs at the edge.
B. Federated Meta Learning
Federated meta learning (FML) is the framework that combining federated learning and meta-learning [25]. Fallah et al. [26]
used meta learning to implement personalized and differentiated
training for federated learning. The federated learning (FL)
framework is first proposed as standard federated training (FedAvg) [27], [28], [29]. FL has made great contributions in ensuring information security during Big Data exchange, protecting
terminal data and personal data privacy. Wu et al. [30] designed
a blockchain-empowered privacy preservation architecture for
5G-enabled drone communications. Yang et al. [31] present a
design of blockchain-based crowdsourcing FL system for IoT
devices manufacturers to learn customers better, the use of differential privacy (DP) protects the privacy of customer data and
improves the accuracy of the model. Besides that, the blockchain
will audit all client updates during federated training so that the
system can be held accountable for model updates to prevent
malicious clients or manufacturers. Moon et al. [32] reviewed the
application of FL methods in the field of healthcare, including
COVID-19, mammograms, and brain tumor segmentation. They
believed that compared with traditional centralized models,
FL-based models improved the model performance. While FL
models in wearable healthcare do not significantly outperform
centralized models, FL provides better results in terms of data
privacy. Li et al. [33] proposed a federated deep learning method
called DeepFed to develop a novel federated learning framework
for multiple industrial CPSs that can collectively build a comprehensive intrusion detection model in a privacy-preserving
manner. As the most representative method in few-shot learning,
model-agnostic meta-learning (MAML) [34], which treats the
designed meta-learner as an optimizer that learns to update the
parameters of any model, was proposed to solve the problem of
small amount of data and strong heterogeneity in edge devices
in federated learning. The work of Jiang et al. [35] and Li
et al. [36] corroborate that the FML model is a personalized
global model with strong generalization ability. Apart from that,
FML has made great contributions in multiple fields. A FML
method proposed by Zhao et al. [37] reduced the BER performance and complexity of classical matched filter (MF)-based
detectors; it demonstrated that FML is useful in an acoustic
radio cooperative wireless network environment outperforms
federated learning-based systems and has higher generalization
ability. Zhang et al. [38] used a federated meta-learning approach
to improve the accuracy of wireless traffic prediction at the
edge. Additionally, FML has made significant contributions in
several fields. This work trains an inductive network through
meta-learning, applies the FSL architecture to NLP tasks in a
federated environment, reduces the communication frequency
between nodes, and has good compatibility for devices with
small amounts of data [39]. Jiang et al. [40] proposed a Federated
Meta-Location Learning (FMLL) method that improves the
accuracy of fine-grained location prediction on smartphones in
5 G scenarios. The FML model designed by Elgabli et al. [41]
can be fine-tuned to new tasks with a small number of samples

2552

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 3, MAY/JUNE 2024

in a distributed environment, and the model reduces the energy
consumption of computation.
The success of federated learning depends on the fact that
the data in each data center is independent and identically distributed (IID). Personalized federated learning (PFL) can solve
the problem of data heterogeneity in federated learning and the
lack of personalization of models for local tasks or data sets.
Tan et al. [42] divided PFL into two categories: global model
personalization and learning personalized model. Global model
personalization focuses on the training ability of the global FL
model on non-IID data, while learning personalized model focuses on achieving model personality during the training phase.
Considering that this article mainly focuses on the problem
of non-independent and identical distribution of edge device
traffic data, we mainly research articles related to global model
personalization. [43], [44], [45] These three papers all add a
regular term on the basis of the federated average. The FedProx
algorithm dynamically controls the number of updates of each
node in each round of communication through the gamma inequality; the novelty of the L2GD algorithm is that it controls
node training and server aggregation through probability; the
advantage of the Ditto algorithm is that the local model is first
optimized according to the FedAvg algorithm, and then a regular
term is added to continue to optimize the local model, and finally
optimization results are sent to the server without a regular term.
Fallah et al. [26] regarded the training phase of FL as the training
phase of meta-learning, regarded the personalization phase of FL
model as the testing phase of meta-learning, and migrated the
meta-learning model to personalized federated learning.
III. PROBLEM FORMULATION
A. Challenges and Motivation
Traditional malicious detection models are often deployed at
the center of distributed systems. This tends to present some
challenges:
1) Less fault tolerance, central models tend to be fragile
when faced with multivariate and heterogeneous data. The
retraining process of the model is accompanied by a huge
waste of resources.
2) The volume of traffic data aggregated by distributed devices is huge, and the traffic data of distributed devices
is unbalanced. Data cleaning, preprocessing, standardization, and normalization will lead to huge consumption of
computing resources.
3) There is a delay in the response time of the malicious
detection system deployed in the center, which is often
caused by two reasons. On the one hand, it is the computing
delay caused by the huge amount of data, and on the other
hand, it is the physical delay caused by the distributed
devices being far away from the central server.
The advantages of meta-learning itself can improve the efficiency of malicious detection models. First, meta-learning can
deal with the problem of data imbalance brought by distributed
systems. When faced with the problem of data imbalance, metalearning can process the head and tail data differently, adaptively
learn how to re-weight, or formulate a domain adaptive problem.
Second, meta-learning has a strong generalization ability, it

performs few-shot learning by training a model on a set of source
tasks that is only a few gradient descent steps away from a good
task-specific model. Deploying meta-learning models on edge
devices can meet the personalized learning needs of non-IID
data, and the source tasks distributed by the central server can
match the personalized task models of edge devices after several
steps of gradient descent.
Therefore, building malicious detection models with federated meta-learning will bring many benefits. First, deploying
the model on edge devices in a distributed environment can
effectively alleviate the computational cost of the central server
and greatly reduce the response time. Secondly, the introduction
of meta-learning can help the central model to quickly adapt
to local data samples, and the generalization ability is greatly
enhanced; the model’s processing ability to unbalanced data is
greatly improved.

B. System Model
In traditional machine learning tasks, algorithms tend to
focus on one specific task. In a network traffic-based attack
behavior discovery system, a basic task is to use a classifier to label network traffic. That is, we have K samples
and M labels denoted as follows: D = {(x1 , y1 ), (x2 , y2 ), · · ·
(xi , yj ) · · · (xK , yM )}, xi ∈ R, yi ∈ {0, 1, 2 · · · M }. The main
goal is to build a multi-class classifier where xi is the input to
the model, yj will be the output, and yj is a possible estimate of
the sample labels. In the traditional supervised learning scenario,
the number of samples K is very large, and the data set containing
all samples will be simply divided into two parts D(train) and
D(test) . However, in APT attack behavior detection, the number
of samples is limited, and the entire task will be regarded as a
small sample learning task. The conditional supervised learning
method often used in few shot learning will face the problem
of overfitting. In addition, in a distributed scenario, the traffic
data samples collected by each device are not balanced, so the
intrusion detection model should be retrained in order to adapt
to new local data. Besides, the attack behavior detection system
for APT often maps the attack behavior to the cyber kill chain.
To address these differences, we propose the FML framework to
implement abnormal traffic detection, and accordingly, as shown
in Fig. 1, our proposed method no longer focuses on a single task
but on multiple tasks, allowing the model to learn. The entire
federated meta-learning model is divided into three levels. The
bottom layer presents data sources which cover gateways, firewalls and base stations. In our model, each edge node represents
an independent edge device, and each edge device will train a
local personalized model through meta-learning on the basis of
the initial model and update the parameters of the local model to
the central server. The weight parameters will be aggregated at
the server and new parameters counted by the aggregation algorithm will be redistributed to each device.
In the FML framework, considering the limited number of
advanced persistent threats samples, the training task of the
device will be regarded as a few-shot learning task. In addition,
the introduction of the FML framework will solve the problem
of unbalanced traffic data on edge devices. The specific method
will be described in Sections 4.1 and 4.2.

HU et al.: PRIVACY-PRESERVING FEW-SHOT TRAFFIC DETECTION AGAINST ADVANCED PERSISTENT THREATS

2553

Algorithm 1: FedMeta with MAML.

Fig. 1. An overview of Federated Meta Learning in staged APT detection at
edge devices.
TABLE I
SYMBOL LIST

IV. THE PFTD WORKFLOW
In abnormal traffic detection scenarios, where the number of
samples with supervised information is limited or impossible
to obtain, few-shot learning is proposed to learn from a limited
number of samples with supervised information. For the convenience of reading, the explanation of related symbols is shown
in Table I.
A. Few-Shot Learning Formulation
In the FSL task, the dataset D is divided into two parts Dtrain
and Dtest . Training set Dtrain = {(xi , yi )}Ii=1 where I is small,
testing set Dtest = {xtest }. In FSL we denote the ground truth
joint probability distribution of input x and output y by p(x, y).
The ĥ represents the optimal hypothesis from x to y, which
is descovered by fitting Dtrain and testing on Dtest . The FSL

Fig. 2.

The system model of proposed PFTD based on federated meta learning.

model defines a hypothesis space H, which consists of h(; θ) s,
to approximate the ĥ. FSL is a continuous optimization process
whose purpose is to searches Hto find the θ that parameterizes
the best h∗ ∈ H. The performance of FSL is measured by the
loss function l(ŷ, y), where ŷ is the predicted value and y is the
observed output.
B. Edge Synergy-Empowered FML Model Training
The structure of the FML model is shown in Fig. 2. Suppose
there are N devices and 13 different attack types of traffic
data in the federated meta-learning scenario. The edge synergyempowered feature of the FML model is reflected in the training

2554

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 3, MAY/JUNE 2024

process. The entire FML model will complete the training process under the cooperation of these N edge devices. Each edge
device will pass the parameters to the central server and get
the initial parameters by means of average aggregation. In the
meta-training stage, 400 devices (from 0 to 399) will be used to
train a well-initialized model. In the meta-testing stage, 4 devices
(from 400 to 403) will be used to verify the generalization ability
of the model and the ability to identify unknown samples. The
traffic data contains 14 categories, O represents benign traffic
and from A to M are 13 different types of attack samples.In
the meta-training stage, considering the limited number of APT
attack samples, each device extracts 4 types of traffic data from
A − I with O as support and query sets Strain , each type has K
samples. We define Su = {A, B, C, D, E, F, G, H, I} samples
a set Su [i] of i types of attack data from Su (i from 0 to 4).
Strain = {Su [4], O}.
In the meta-testing stage, in order to verify the generalization
of the model against non-IID local data and the ability to identify
unknown attacks, we trained J-M samples on the test device according to different proportions. We define Sv = {J, K, L, M }
samples a set Sv [j] of j types of attack data from Sj (j from
1 to 4). On each edge device we extract 4 types of attack data
from A to M with normal traffic data O as support and query set
Stest . Stest = {Sv [j], Su [4 − j], O}.
The goal of traditional FL can be expressed as:

C. Personalizing to Individual Edge Devices

n

1
min f (w) :=
fi (w)
d
n i=1
w∈R

(1)

The optimization objective can be defined as:
fi (w) := E(x,y)∼pi [li (w; x, y)]

Algorithm 2: Personalized FedAvg Algorithm.

(2)

The algorithmic structure of the entire federated metalearning with MAML is shown in Algorithm 1, which modified
from the research of Chen et al. [46]. The training process of
MAML includes two levels of parameter update and transfer.
First, the initialization parameter θ0 is used to train the taskspecific model, and then the loss of all tasks is used to update
the initialization parameters of the model. Under the federated
setting, each client downloads the initialization parameters of
the model from the server, uses the support set to train the
model, and then sends the test loss obtained by the query set to
the server. The server side saves the initialization of the model
and collects the test loss sent back by the clients of each mini
batch. The messages transmitted between server and client are
only model initialization parameters and test loss. Specifically,
in Algorithm update stage, n edge devices sampled from Ut will
receive an initial parameter θ for MAML process. Afer model
training, loss function gu is calculated and the new parameters
θ is send to the server. In model training stage, each edge device
samples support set Strain and query set Stest . During the
training process, the support set and the query set guide each
other and transfer knowledge. Different from the traditional FL
method, the parameters finally passed by the edge device are
generated under the mutual guidance of the support set and the
query set. The whole process is shown in the Model Training
MAML process in Alforithm 1. The loss function gu will return
to server.

In order to generalize the model from a single edge device
to multiple devices and ensure that each edge device can obtain
a model adapted to local data with only a few steps gradient
descents. We implement federated meta-learning using the PerFedAvg method [26]. The algorithmic structure of the entire
FedAvg method is shown in Algorithm 2. For each edge device,
its meta function Fi (ω) can be defined as:
Fi (ω) := fi (ω − α∇fi (ω)).

(3)

The optimization objective can be defined as:
n

min Fi (ω) :=

ω∈Rd

1
fi (ω − α∇fi (ω)).
n i=1

(4)

Here α is the learning rate, n is the number of tasks involved
in training. This formula could ensure that the central model
can capture the differences between different edge devices, and
each device can modify the initial model according to its own
data. Algorithm 2 describes the entire FML implementation
process. The optimization objective Fi (ω) is the average of all
meta-functions. On each edge device, the gradient of the local
functions ∇Fi (ω) needs to be computed first:
∇Fi (ω) = (I − α∇2 fi (ω))∇fi (ω − α∇fi (ω)).

(5)

Since computing ∇fi (ω)is expensive, so take a batch of data Di
to get an unbiased estimate:

˜ i (ω, Di ) := 1
∇f
∇li (ω; x, y).
(6)
|Di |
i
(x,y)∈D

At the kth round of communication, the server sends the current global model to several randomly selected edge devices, and
each edge device performs t rounds of local gradient updates.

HU et al.: PRIVACY-PRESERVING FEW-SHOT TRAFFIC DETECTION AGAINST ADVANCED PERSISTENT THREATS

TABLE II
THE ATTACK TYPES OF CICIDS2017 AND DAPT2020

TABLE III
MULTI-CLASSIFICATION ACCURACY CONFUSION MATRIX

We optimize the meta-model based on the support set, where β
is the learning rate of the local update, i represents user i, k + 1
refers to using the meta-model parameters of the kth round for
training, and t is the number of local iterations:
i
i
˜ i (ω i
ωk+1,t
= ωk+1,t−1
− β ∇F
k+1,t−1 ).

2555

(7)

The last step is to use the query set to calculate the loss and its
i
i
gradient to ωk+1,t
based on the optimized meta-model ωk+1,t
:



i
i
˜ i (ωk+1,t−1
˜ 2 fi (ωk+1,t−1
∇F
) := I − α∇
, Dti )



i
i
i
˜ i ωi
˜
(8)
∇f
k+1,t−1 − α∇fi (ωk+1,t−1 , Dt ), Dt .
i
Each edge device sends the local ωk+1,t
to the server, and the
server updates the global model by calculating the average of
ωk+1 :
1 
ωk+1 =
ωi
(9)
i∈Ak k+1,τ
rn

V. EXPERIMENTS
A. Datasets
Our proposed method is evaluated on the DAPT 2020 dataset.
Only csv data obtained from CICFlowMeter feature extraction
was used. External and internal network traffic were mixed
together. The original data table contains 85 columns with 83
features and 2 labels. Columns 1 to 7 of the table data are traffic
identification features, and all of them except the protocol column were removed. Another 12 columns were removed because
they were recorded the same on all traffic. The CICIDS2017
dataset contains benign and recent common attacks similar to
real-world data (PCAPs).
The DAPT2020 dataset contains 5 days of network traffic,
including normal traffic and 7 kinds of APT attack traffic.
CICDIS2017 contains 5 days of network traffic data, including
normal traffic and 14 types of malicious traffic. The specific
attack types of the two datasets are shown in Table II. As shown
in Fig. 2, in the training phase, we will randomly sample 4
types of malicious traffic, plus normal traffic, a total of five
types of traffic data. For each type of traffic, we will draw 10
samples as data sources to build tasks. Each task is defined as a
few-shot five-classification task to distinguish between normal
traffic and different kinds of malicious traffic. In the testing
phase, we select 4 types of traffic as unknown traffic to test the
detection accuracy of the FML model when there are unknown
types of attacks locally. Specially, he classification task on the

DAPT2020 dataset will eventually map data traffic to the five
stages of APT attacks.
B. Metrics
Accuracy and macro F1 score are used as evaluation metrics.
Accuracy represents the ratio of correctly classified samples to
all samples. When the data is unbalanced, the accuracy rate
cannot reflect the classification effect of the class with a small
number of samples. In addition to the accuracy index, the macro
average F1 score is used as the evaluation criterion, which is the
average of five F1 scores as shown below.
m
F 1 scorei
M acro F 1 = i
(10)
m
The basic unit of meta-learning is a task, so the evaluation
of meta-learning performance needs to calculate the accuracy
of classification results according to the confusion matrix, as
shown in Table III. For multivariate classification tasks, the
classification results correspond to the following two results:
1) True Positive (TP): Normal samples are classified as
normal;
2) False positive (FP): Normal samples are classified as malicious (false positive);
Based on this, precision can be defined as shown below.
Accuracy =

TP1
TP1 + FP5 + FP6 + FP7 + FP8

(11)

C. Experimental Settings
Experiments were performed using the following hardware
and software platforms: Intel(R) Xeon(R) Platinum CPU @
2.50 GHz, 128 GB RAM, NVIDIA GeForce RTX 3090, Ubuntu
20.04.3 LTS, CUDA 11.3, and PyTorch 1.12.1.
To apply the federated meta-learning approach, the dataset
is resampled and distributed across different edge devices. The
dataset is divided into 70% and 30% parts for training and testing
edge devices respectively. In particular, the 15 traffic data in
the data-stealing stage are manually divided into the latter. For
training and testing edge devices, we set up their classification
tasks in different ways. For training edge devices, we split the
data by “activity”. Each edge device randomly has data of 5
activities, and each activity has 15 traffic. For the test edge
device, we split the data by “stages”. Each edge device has 15
flows per attack phase. Finally, each edge device has a different
5-classification task to simulate the different distribution of
traffic classes on each node. For all edge devices, 10 samples
of each class are used as the support set and 5 samples are used
as the query set.

2556

Fig. 3.

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 3, MAY/JUNE 2024

Detection results of experiments on the CICIDS2017 dataset.

D. Results
1) Compatibility Test: In the FML scenario, the number of
edge devices affects the training effect of the model. We compared the impact of different numbers of edge devices on the
accuracy of the model when the local unknown sample types
are both 2. The experimental results are shown in Fig. 4. Two
conclusions can be drawn:
1) The more edge devices, the higher detection rate of the
model. The increase in the number of edge devices allows
the central model to fit a greater number and variety of
samples. Of course, this improvement is not unlimited.
When the number of edge devices is sufficient to cover
enough sample types, the accuracy of the model will no
longer improve.
2) Scenarios with a small number of edge devices are not
suitable for deploying FML models. When the number of
edge devices is only 20, the model accuracy is lower than
default initialization. The limited number of edge clients
means that they vary greatly, which is not guaranteed that
the central model has learned enough sample features
during the training process. This leads to experimental
results lower than default initialization. Meanwhile, When
the number of edge clients increases by a small amount,
the models learned by the central server are quite different.
When the client base is large enough, the number of clients
will increase less and has less impact on the overall model

Fig. 4. Comparisons of the detection accuracy against different numbers of
edge devices.

variance. This leads to the fact that the offset between 20
and 40 is larger than that of 40 and 60.
2) Comparative Experiment: We tested our method on two
different datasets: CICIDS2017 and DAPT2020. The detection
results of experiments on the CICIDS2017 dataset are shown in

HU et al.: PRIVACY-PRESERVING FEW-SHOT TRAFFIC DETECTION AGAINST ADVANCED PERSISTENT THREATS

2557

TABLE IV
COMPARISON OF DETECTION RESULTS, THE NUMBER OF SAMPLES AND CLASSIFICATION METHOD IN THE PROPOSED METHOD AND RELATED RESEARCH WORKS

Fig. 3. In this experiment, we compare the accuracy of anomalous traffic detection systems in three scenarios, training the
samples in central server, deploying a federated meta-learning
model, and fine-tuning a local model before testing. The neural
networks used for classifying are FCN (Fully Connected Network) and Resnet. Form Fig. 3(a) to (c) and from Fig. 3(d) to (f),
the number of unknown class in attack data was set differently.
The experimental results show that, comparing with training the
samples in center server, deploying the federated meta-learning
model can improve the edge device’s recognition accuracy of
attack samples. In the case of a small number of unknown attack
types, the detection accuracy of the test edge device after model
fine-tuning is also improved compared with the accuracy of the
traditional central server training model. However, the results
of model fine-tuning drop when the number of unknown attack
types grows. This result occurs because the local sample is quite
different from the sample fitted by the central model.
The detection results of experiments on the DAPT2020
dataset are shown in Fig. 5. This experiment studies a fivecategory problem, and malicious traffic will be mapped to the
five attack stages in the APT attack. The settings of this experiment remain unchanged, and the neural networks used for
classification are FCN and Resnet. We compared the detection
accuracy on default initialization, federated meta learning and
FML with fine-tuning. In this experiment we did not test the
model for unknown class samples recognition ability, but instead
focuses on detecting the detection ability of FML in different
datasets. The results show that the application of FML improves
the detection accuracy of traditional centralized training while
using FCN as the classifier. The difference from the results of
the CICIDS2017 dataset is that the accuracy produced by model
fine-tuning is not stable above the default initialization. The
reason for this phenomenon is that different attack stages often
have traffic data generated by similar system behaviors. The
FCN network does not fully learn this classification method.
However, when resnet is used as the classifier, the results of
the three cases do not show a large difference as the number of
training rounds increases. The occurrence of this phenomenon
has a certain relationship with the residual structure of the resnet
model. The deeper network layer makes the classification results
of the model relatively stable, so under the effect of FML and
fine-tuning, the degree of discrimination is not obvious.
Detailed results of comparative experiments are shown in
Table IV. In the test of the CICIDS2017 dataset, we add different

Fig. 5.

Detection results of experiments on the DAPT2020 dataset.

types of unknown samples. The results show that under a FCN
classification network, when the number of unknown species
is small, the application of FML can improve the detection

2558

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 3, MAY/JUNE 2024

TABLE V
COMPARISON OF DATASETS, UNKNOWN ATTACK NUMBER AND DETECTION RESULTS IN PROPOSED METHOD

accuracy by about 10%, and finally reach more than 80%. Model
fine-tuning also has better detection accuracy. When the number
of unknown species is large, the accuracy rate decreases. Due
to the powerful classification function of ResNet, the FML does
not improve the accuracy rate significantly, but it also has a
certain effect. The first reason for the difference in accuracy
improvement is that different DNN networks have different
matching degrees with data. Resnet may be more suitable for
classifying traffic data, so the improvement in accuracy rate
is not as obvious as FCN. Secondly, another reason is that
Resnet’s residual structure has more advantages than FCN in
the face of deep networks. Resnet solves the problem of gradient
disappearance encountered in the case of deepening the network.
So in the default training stage, it has a higher accuracy rate. In
the test of the DAPT2020 dataset, we classified the five APT
attack stages corresponding to the samples. The experimental
results show that under the FCN classification network, the
application of FML improves the accuracy of the model, and
the F1 score also improves. However, due to the classification
performance of the Resnet network, in the FML scenario, the
classification accuracy has not improved.
Considering that the classification networks in CICIDS2017
and DAPT2020 are both five-category, we conducted a migration experiment of the model, which trained the model on
CICIDS2017 and tested it on DAPT2020. In the FCN network,
as shown in Fig. 6(a), after 40 rounds of local edge device
training on the DAPT2020 dataset, the central model learned
from CICIDS2017 can well adapt to local samples, and the
accuracy rate increases to 70%. The accuracy of the model after
fine-tuning is several percentage points higher than the previous
experiment. In the resnet network, as shown in Fig. 6(b), after
40 rounds of training, the accuracy of the model is the same as
the previous experiment. It can be seen that the FML model has
certain migration capabilities.
Table V shows the comparison of detection results, the number
of samples and classification method in the proposed method
and related research works, which is extended from the work of
Xu et al. [47]. On the whole, there is a certain gap between our
detection accuracy and previous work, but considering that we
use a multi-classification network, and FML will have a certain

Fig. 6. Detection results of experiments when training on CICIDS2017 and
texting on DAPT2020.

HU et al.: PRIVACY-PRESERVING FEW-SHOT TRAFFIC DETECTION AGAINST ADVANCED PERSISTENT THREATS

impact on the results in the selection of model aggregation
algorithms, so consider from this perspective, our proposed
method is feasible.
VI. CONCLUSION
In this article, we proposed a novel detection method based
on federated meta learning framework to implement few-shot
abnormal traffic detection. For this purpose, a virtual federated
meta-learning scenario with hundreds of edge devices and two
different five-class classification networks: FCN and ResNet
were constructed for learning. The proposed method accomplishes this task by training a FML-based abnormal traffic training and detection model. In order to adapt to the characteristics of
APT attacks, we only use a small number of labeled samples for
training, and use FCN and ResNet to implement five-category
tasks and identify unknown attack behaviors. On the edge device,
we use the MAML method to realize the personalized adjustment
of the central model to the local data, so that the central model can
quickly adapt to the local data and achieve high classification
accuracy. At the same time, the combination of MAML and
federated learning protects the information security and privacy
of edge devices. Experimental results show that the proposed
small-shot APT detection method achieves state-of-the-art performance in FML scenarios. Our work shows that federated
meta-learning methods can maintain the performance of APT
attack detection methods in distributed scenarios, which will
inspire other researchers to design better deep neural networks
for APT attack detection along this direction.
REFERENCES
[1] Y. Wu, H.-N. Dai, H. Wang, Z. Xiong, and S. Guo, “A survey of intelligent
network slicing management for industrial IoTT: Integrated approaches
for smart transportation, smart energy, and smart factory,” IEEE Commun.
Surveys Tut., vol. 24, no. 2, pp. 1175–1211, Secondquarter 2022.
[2] P. A. A, A. Maryposonia, and P. V. S, “An efficient network intrusion detection system for distributed networks using machine learning technique,”
in Proc. 7th Int. Conf. Trends Electron. Informat., 2023, pp. 1258–1263.
[3] T. Ye, G. Li, I. Ahmad, C. Zhang, X. Lin, and J. Li, “FLAG: Few-shot
latent dirichlet generative learning for semantic-aware traffic detection,”
IEEE Trans. Netw. Service Manag., vol. 19, no. 1, pp. 73–88, Mar. 2022.
[4] W. Zhong, N. Yu, and C. Ai, “Applying Big Data based deep learning
system to intrusion detection,” Big Data Mining Analytics, vol. 3, no. 3,
pp. 181–195, 2020.
[5] L. Chen, M. Xian, J. Liu, and H. Wang, “Intrusion detection system in
cloud computing environment,” in Proc. Int. Conf. Comput. Commun.
Netw. Secur., 2020, pp. 131–135.
[6] W. W. Lo, S. Layeghy, M. Sarhan, M. Gallagher, and M. Portmann, “EGraphSAGE: A graph neural network based intrusion detection system for
IoT,” in Proc. IEEE/IFIP Netw. Operations Manage. Symp., 2022, pp. 1–9.
[7] S. M. Milajerdi, R. Gjomemo, B. Eshete, R. Sekar, and V. N. Venkatakrishnan, “HOLMES: Real-time apt detection through correlation of suspicious
information flows,” in Proc. IEEE Symp. Secur. Privacy, 2019, pp. 1137–
1152.
[8] T. A. Tang, L. Mhamdi, D. McLernon, S. A. R. Zaidi, and M. Ghogho,
“Deep recurrent neural network for intrusion detection in SDN-based
networks,” in Proc. IEEE Conf. Netw. Softwarization Workshops (NetSoft),
2018, pp. 202–206.
[9] S. M. Milajerdi, B. Eshete, R. Gjomemo, and V. N. Venkatakrishnan,
“POIROT: Aligning attack behavior with kernel audit records for cyber
threat hunting,” in Proc. ACM SIGSAC Conf. Comput. Commun. Secur.,
2019, pp. 1795–1812.
[10] D. Yuan et al., “Intrusion detection for smart home security based on data
augmentation with edge computing,” in Proc. IEEE Int. Conf. Commun.,
2020, pp. 1–6.

2559

[11] W. Zheng, L. Yan, C. Gou, and F.-Y. Wang, “Federated meta-learning for
fraudulent credit card detection,” in Proc. Int. Conf. Int. Joint Conf. Artif.
Intell., 2021, pp. 4654–4660.
[12] K. Atefi, H. Hashim, and M. Kassim, “Anomaly analysis for the classification purpose of intrusion detection system with k-nearest neighbors
and deep neural network,” in Proc. IEEE 7th Conf. Syst., Process Control,
2019, pp. 269–274.
[13] Y. Xiao, C. Xing, T. Zhang, and Z. Zhao, “An intrusion detection model
based on feature reduction and convolutional neural networks,” IEEE
Access, vol. 7, pp. 42210–42219, 2019.
[14] S. A. Althubiti, E. M. Jones, and K. Roy, “LSTM for anomaly-based
network intrusion detection,” in Proc. 28th Int. Telecommunication Netw.
Appl. Conf., 2018, pp. 1–3.
[15] G. Andresini, A. Appice, L. D. Rose, and D. Malerba, “GAN augmentation
to deal with imbalance in imaging-based intrusion detection,” Future
Gener. Comput. Syst., vol. 123, pp. 108–127, 2021.
[16] M. M. Hassan, A. Gumaei, A. Alsanad, M. Alrubaian, and G. Fortino, “A
hybrid deep learning model for efficient intrusion detection in Big Data
environment,” Inf. Sci., vol. 513, pp. 386–396, 2020.
[17] M. Kumar and A. K. Singh, “Distributed intrusion detection system using
blockchain and cloud computing infrastructure,” in Proc. 4th Int. Conf.
Trends Electron. Informat., 2020, pp. 248–252.
[18] R. Sharma, C. A. Chan, and C. Leckie, “Evaluation of centralised vs
distributed collaborative intrusion detection systems in multi-access edge
computing,” in Proc. IFIP Netw. Conf. (Netw.), 2020, pp. 343–351.
[19] R. Sharma, C. A. Chan, and C. Leckie, “Hybrid collaborative architectures for intrusion detection in multi-access edge computing,” in Proc.
IEEE/IFIP Netw. Operations Manage. Symp., 2022, pp. 1–7.
[20] L. Nie et al., “Intrusion detection for secure social Internet of Things based
on collaborative edge computing: A generative adversarial network-based
approach,” IEEE Trans. Computat. Social Syst., vol. 9, no. 1, pp. 134–145,
Feb. 2022.
[21] B. Yin, H. Yin, Y. Wu, and Z. Jiang, “FDC: A secure federated deep
learning mechanism for data collaborations in the Internet of Things,”
IEEE Internet Things J., vol. 7, no. 7, pp. 6348–6359, Jul. 2020.
[22] M. N. Hossain et al., “Sleuth: Real-time attack scenario reconstruction
from cots audit data,” in Proc. USENIX Secur. Symp., 2017, pp. 487–504.
[23] K. Satvat, R. Gjomemo, and V. Venkatakrishnan, “Extractor: Extracting
attack behavior from threat reports,” in Proc. IEEE Eur. Symp. Secur.
Privacy, 2021, pp. 598–615.
[24] H. Li, J. Wu, H. Xu, G. Li, and M. Guizani, “Explainable intelligencedriven defense mechanism against advanced persistent threats: A joint
edge game and AI approach,” IEEE Trans. Dependable Secure Comput.,
vol. 19, no. 2, pp. 757–775, Mar./Apr. 2022.
[25] S. Zhang, Y. Zhou, H. Qu, Y. Zhu, and L. You, “Reinforcement learning
based incentive mechanism for federated meta learning: A game-theoretic
perspective,” in Proc. IEEE 34th Int. Conf. Tools with Artif. Intell., 2022,
pp. 1152–1159.
[26] A. Fallah, A. Mokhtari, and A. Ozdaglar, “Personalized federated learning
with theoretical guarantees: A model-agnostic meta-learning approach,”
Proc. 34th Int. Conf. Neural Inform. Process. Syst., vol. 300, no. 12, 2020.
[27] B. Ghimire and D. B. Rawat, “Recent advances on federated learning
for cybersecurity and cybersecurity for federated learning for Internet of
Things,” IEEE Internet Things J., vol. 9, no. 11, pp. 8229–8249, Jun. 2022.
[28] G. Li, J. Wu, S. Li, W. Yang, and C. Li, “Multitentacle federated learning
over software-defined industrial Internet of Things against adaptive poisoning attacks,” IEEE Trans. Ind. Informat., vol. 19, no. 2, pp. 1260–1269,
Feb. 2023.
[29] Z. Yang, G. Li, J. Wu, and W. Yang, “Propagable backdoors over
blockchain-based federated learning via sample-specific eclipse,” in Proc.
IEEE Glob. Commun. Conf., 2022, pp. 2579–2584.
[30] Y. Lu, X. Huang, Y. Dai, S. Maharjan, and Y. Zhang, “Blockchain and
federated learning for privacy-preserved data sharing in industrial IoT,”
IEEE Trans. Ind. Informat., vol. 16, no. 6, pp. 4177–4186, Jun. 2020.
[31] Y. Zhao et al., “Privacy-preserving blockchain-based federated learning
for IoT devices,” IEEE Internet Things J., vol. 8, no. 3, pp. 1817–1829,
Jan./Feb. 2022.
[32] S. Moon and W. H. Lee, “Privacy-preserving federated learning in healthcare,” in Proc. Int. Conf. Electron., Inf., Commun., 2023, pp. 1–4.
[33] B. Li, Y. Wu, J. Song, R. Lu, T. Li, and L. Zhao, “Deepfed: Federated
deep learning for intrusion detection in industrial cyber–physical systems,”
IEEE Trans. Ind. Inform., vol. 17, no. 8, pp. 5615–5624, Aug. 2021.
[34] C. Finn, P. Abbeel, and S. Levine, “Model-agnostic meta-learning for fast
adaptation of deep networks,” in Proc. Int. Conf. Mach. Learn., 2017,
pp. 1126–1135.

2560

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 3, MAY/JUNE 2024

[35] Y. Jiang, J. Konečný, K. Rush, and S. Kannan, “Improving federated learning personalization via model agnostic meta learning,” 2019,
arXiv:1909.12488.
[36] G. Li, Y. Zhao, W. Wei, and Y. Liu, “Few-shot multi-domain knowledge
rearming for context-aware defence against advanced persistent threats,”
2023, arXiv:2306.07685.
[37] H. Zhao, F. Ji, Q. Li, Q. Guan, S. Wang, and M. Wen, “Federated
meta-learning enhanced acoustic radio cooperative framework for ocean
of things,” IEEE J. Sel. Topics Signal Process., vol. 16, no. 3, pp. 474–486,
Apr. 2022.
[38] L. Zhang, C. Zhang, and B. Shihada, “Efficient wireless traffic prediction
at the edge: A federated meta-learning approach,” IEEE Commun. Lett.,
vol. 26, no. 7, pp. 1573–1577, Jul. 2022.
[39] N. Muthukumar, “Few-shot learning text classification in federated environments,” in Proc. Smart Technol., Commun. Robot., 2021, pp. 1–3.
[40] X. Jiang et al., “Federated meta-location learning for fine-grained location
prediction,” in Proc. IEEE Int. Conf. Big Data (Big Data), 2021, pp. 446–
456.
[41] A. Elgabli, C. B. Issaid, A. S. Bedi, M. Bennis, and V. Aggarwal, “Energyefficient and federated meta-learning via projected stochastic gradient
ascent,” in Proc. IEEE Glob. Commun. Conf., 2021, pp. 1–6.
[42] A. Z. Tan, H. Yu, L. Cui, and Q. Yang, “Towards personalized federated
learning,” IEEE Trans. Neural Netw. Learn. Syst., early access, Mar.
28, 2022, doi: 10.1109/TNNLS.2022.3160699.
[43] T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith,
“Federated optimization in heterogeneous networks,” Proc. Mach. Learn.
Syst., vol. 2, pp. 429–450, 2020.
[44] O. Marfoq, G. Neglia, A. Bellet, L. Kameni, and R. Vidal, “Federated
multi-task learning under a mixture of distributions,” Proc. 35th Conf.
Neural Inform. Process. Syst., vol. 34, 2021.
[45] T. Li, S. Hu, A. Beirami, and V. Smith, “Ditto: Fair and robust federated
learning through personalization,” in Proc. Int. Conf. Mach. Learn., 2021,
pp. 6357–6368.
[46] F. Chen, M. Luo, Z. Dong, Z. Li, and X. He, “Federated meta-learning with
fast convergence and efficient communication,” 2018, arXiv:1802.07876.
[47] C. Xu, J. Shen, and X. Du, “A method of few-shot network intrusion
detection based on meta-learning framework,” IEEE Trans. Inf. Forensics
Secur., vol. 15, pp. 3540–3552, 2020.

Yilun Hu received the B.S. degree in communication
engineering from Beijing Jiaotong University, Beijing, China, in 2016, and the M.S. degree in informatics from Northeastern University, Boston, MA,
USA, in 2019. He is currently working toward the
Ph.D. degree with the School of Electronic Information and Electrical Engineering, Shanghai Jiao Tong
University, Shanghai, China. His research interests
include Internet of Things, machine learning, and
cybersecurity.

Jun Wu (Senior Member, IEEE) received the Ph.D.
degree in information and telecommunication studies
from Waseda University, Shinjuku City, Japan, in
2011. He is currently a professor with the School
of Electronic Information and Electrical Engineering,
Shanghai Jiao Tong University. His research interests
include the intelligence and security techniques of
Internet of Things (IoT), edge computing, Big Data,
5 G/6 G. He is the Chair of IEEE P21451-1-5 Standard
Working Group for Internet of things. His publications have received a few distinctions, which include
the Best Paper Award of IEEE Transactions on Emerging Topics in Computing,
in 2020, Best Paper Award of International Conference on Telecommunications
and Signal Process in 2019, Best Conference Paper Award of the IEEE ComSoc
Technical Committee on Communications Systems Integration and Modeling in
2018. He was the Track Chair for VTC 2019, VTC 2020 and the TPC Member
of more than ten international conferences including ICC, GLOBECOM. He is
an Associate Editor for the IEEE SYSTEMS JOURNAL and IEEE NETWORKING
LETTERS. He was the Guest Editor for the IEEE TRANSACTIONS ON INDUSTRIAL
INFORMATICS, IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION, IEEE
SENSORS JOURNAL, Sensors, Frontiers of Information Technology Electronic
Engineering (FITEE).

Gaolei Li (Member, IEEE) received the B.S. degree
from Sichuan University, Chengdu, China, and the
Ph.D. degree from Shanghai Jiao Tong University,
Shanghai, China. During 2018–2019, he visited at
Muroran Institution of Technology, Muroran, Japan,
granted by the China Scholarship Council Program.
He is currently an Assistant Professor with the School
of Electronic Information and Electrical Engineering,
Shanghai Jiao Tong University. His research interests
include adversarial machine learning and privacy protection. He was the recipient of the best paper awards
from the IEEE ComSoc CSIM Committee, Chinese Association for Cryptologic
Research (CACR) and IEEE Globecom student travel grant Award. He is a
reviewer of IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTINGC,
TII, TCCN, and PC member of AAAI, IEEE Globecom, IEEE ICC, IEEE VTC.

Jianhua Li (Senior Member, IEEE) received the B.S.,
M.S., and Ph.D. degrees from Shanghai Jiao Tong
University, Shanghai, China, in 1986, 1991 and 1998,
respectively. He is currently a Professor/Ph.D. Supervisor and the Dean of Institute of Cyber Science and
Technology, Shanghai Jiao Tong University, Shanghai, China. He is also the Director of National Engineering Laboratory for Information Content Analysis
Technology, the Director of Engineering Research
Center for Network Information Security Management and Service of Chinese Ministry of Education,
and the Director of Shanghai Key Laboratory of Integrated Administration
Technologies for Information Security, China. He is the Vice President of
Association of Cyber Security Association of China. He was the Chief Expert
with the information security committee experts of National High Technology
Research and Development Program of China (863 Program) of China. He was
the leader of more than 30 state/province projects of China, and authored or
coauthored more than 300 papers. He authored or coauthored six books and
has about 20 patents. His research interests include information security, signal
process, computer network communication. He made three standards and has
five software copyrights. He was the recipient of the Second Prize of National
Technology Progress Award of China in 2005.

Jinke Cheng received the B.S. degree from Xidian
University, Xi’an, China, in 2022. He is currently
working toward the M.S. degree with the School of
Electronic Information and Electrical Engineering,
Shanghai Jiao Tong University, Shanghai, China. His
research interests include machine learning for cybersecurity and cybersecurity for machine learning. He
has participated in many projects, including National
Natural Science Foundation of China, and CCF-Ant
group funding.
PAPER_TEXT
