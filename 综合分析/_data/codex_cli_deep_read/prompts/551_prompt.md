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
# [551] StatAvg: Mitigating Data Heterogeneity in Federated Learning for Intrusion Detection Systems
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
编号：551
题名：StatAvg: Mitigating Data Heterogeneity in Federated Learning for Intrusion Detection Systems
年份：2025
DOI：10.1109/tnsm.2025.3564387
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2025.3564387.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：联邦学习、隐私保护与分布式协同
相关性：中相关，分数 9
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\551.txt
- 原始字符数：62191
- 本次发送字符数：62191
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2944

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 4, AUGUST 2025

StatAvg: Mitigating Data Heterogeneity in
Federated Learning for Intrusion Detection Systems
Pavlos S. Bouzinis , Panagiotis Radoglou-Grammatikis , Member, IEEE, Ioannis Makris ,
Thomas Lagkas , Senior Member, IEEE, Vasileios Argyriou , Georgios Th. Papadopoulos , Member, IEEE,
Panagiotis Sarigiannidis , Member, IEEE, and George K. Karagiannidis , Fellow, IEEE

Abstract—Federated learning (FL) enables devices to collaboratively build a shared machine learning (ML) or deep learning
(DL) model without exposing raw data. Its privacy-preserving
nature has made it popular for intrusion detection systems
(IDS) in the field of cybersecurity. However, data heterogeneity
across participants poses challenges for FL-based IDS. This paper
proposes statistical averaging (StatAvg) method to alleviate
non-independently and identically (non-iid) distributed features
across local clients’ data in FL. In particular, StatAvg allows
the FL clients to share their individual local data statistics
with the server. These statistics include the mean and variance
of each client’s feature vector. The server then aggregates
this information to produce global statistics, which are shared
with the clients and used for universal data normalization,
i.e., common scaling of the input features by all clients. It is
worth mentioning that StatAvg can seamlessly integrate with
any FL aggregation strategy, as it occurs before the actual
FL training process. The proposed method is evaluated against
well-known baseline approaches that rely on batch and layer
normalization, such as FedBN, and address the non-iid features
issue in FL. Experiments were conducted using the TON-IoT
and CIC-IoT-2023 datasets, which are relevant to the design of
host and network IDS, respectively. The experimental results
Received 6 November 2024; revised 22 March 2025; accepted 17
April 2025. Date of publication 25 April 2025; date of current version
7 August 2025. This work has received funding from the European UnionâĂŹs
Horizon Europe research and innovation programme under grant agreement
No 101070450 (AI4CYBER). Disclaimer: Funded by the European Union.
Views and opinions expressed are however those of the author(s) only
and do not necessarily reflect those of the European Union or European
Commission. Neither the European Union nor the European Commission
can be held responsible for them. The associate editor coordinating the
review of this article and approving it for publication was H. Ould-Slimane.
(Corresponding author: Panagiotis Radoglou-Grammatikis.)
Pavlos S. Bouzinis and Ioannis Makris are with the Research &
Development Department, MetaMind Innovation P.C., 501 00 Kozani, Greece
(e-mail: pbouzinis@metamind.gr; makris@metamind.gr).
Panagiotis Radoglou-Grammatikis is with the Department of Electrical and
Computer Engineering, University of Western Macedonia, 501 00 Kozani,
Greece, and also with the Research & Development Department, K3Y Ltd.,
1000 Sofia, Bulgaria (e-mail: pradoglou@uowm.gr).
Thomas Lagkas is with the Department of Computer Science, Democritus
University of Thrace (Kavala Campus), 654 04 Kavala, Greece (e-mail:
tlagkas@cs.duth.gr).
Vasileios Argyriou is with the Department of Networks and Digital Media,
Kingston University London, KT1 2EE London, U.K. (e-mail: vasileios.
argyriou@kingston.ac.uk).
Georgios Th. Papadopoulos is with the Department of Informatics and
Telematics, Harokopio University of Athens, 177 78 Athens, Greece (e-mail:
g.th.papadopoulos@hua.gr).
Panagiotis Sarigiannidis is with the Department of Electrical and Computer
Engineering, University of Western Macedonia, 501 00 Kozani, Greece
(e-mail: psarigiannidis@uowm.gr).
George K. Karagiannidis is with the Department of Electrical and Computer
Engineering, Aristotle University of Thessaloniki, 541 24 Thessaloniki, Greece
(e-mail: geokarag@auth.gr).
Digital Object Identifier 10.1109/TNSM.2025.3564387

demonstrate the efficiency of StatAvg in mitigating non-iid
feature distributions across the FL clients compared to the
baseline methods, offering a gain in IDS accuracy ranging from
4% to 17%.
Index Terms—Cybersecurity, intrusion detection systems, federated learning, data heterogeneity, statistical averaging.

I. I NTRODUCTION
N THE dynamic era of smart technologies, including the
Internet of Things (IoT) [1], artificial intelligence (AI) [2]
and future wireless networks [3], [4], the attack surface
increases significantly. In particular, from single-step attacks,
the attackers now have the ability to design and execute multistep attack scenarios, targeting multiple systems and domains
in a coordinated and synchronized manner. According to the
MITRE ATT&CK framework, notable examples of attack
campaigns include (a) C0034 - the 2022 Ukraine Electric
Power Attack, and (b) C0022 - Operation Dream Job. These
incidents highlight the increasingly complex and evolving
nature of cyber threats, which continue to pose significant
risks to critical infrastructure and organizational security. As
cyberattack strategies evolve and grow more complex, it is
evident that traditional methods are no longer sufficient to
safeguard critical infrastructure and organizational security.
Hence, there is now a strong demand for reliable, real-time
intrusion detection systems (IDS). In a cybersecurity landscape
where threats can quickly morph and adapt, efficient IDS are
not just important, but essential.
Traditionally, IDS rely on signature-based methods, where
predefined attack rules or patterns, referred to as signatures,
are identified and compared with the monitoring data, thus
alerting a potential threat if a match is found. For instance,
Snort and Suricata are popular IDS in this category. On
the other hand, in recent years, both machine learning (ML)
and deep learning (DL) models have already demonstrated
significant promise as a means to detect cyberattacks [5].
However, it is worth mentioning that these models need
the presence of appropriate security datasets that are often
not publicly available, especially for critical domains [5]. In
addition, appropriate adjustments are required to re-train and
integrate these models. Finally, conventional ML/DL methods
are conducted in a centralized fashion, where a central entity
collects all the necessary data from endpoints to construct
training datasets and afterwards generates the ML/DL models.
Although this approach successfully enables the detection of

I

c 2025 The Authors. This work is licensed under a Creative Commons Attribution 4.0 License.

For more information, see https://creativecommons.org/licenses/by/4.0/

BOUZINIS et al.: STATAVG: MITIGATING DATA HETEROGENEITY IN FL FOR IDS

intrusions, it raises privacy concerns since endpoints’ private
data are shared with third parties.
To alleviate privacy issues and mitigate communication
overhead, federated learning (FL) has been proposed as
an inherently privacy-preserving decentralized learning solution [6], [7]. According to the FL principles, the participating
clients are building an ML/DL model collaboratively with the
aid of a central entity (e.g., a central server). The salient
feature of FL is that clients transmit locally trained models
to the server rather than raw data. Afterwards, the server
aggregates the received parameters, updates the global model,
and subsequently broadcasts it to the clients. Consequently,
the server has no access to clients’ raw datasets. However,
despite the benefits of FL, a notable challenge in the design
of an FL-based IDS is the existence of non-independently
and identically distributed (iid) data among clients, commonly
referred to as data heterogeneity. In particular, if the data is
not representative across the clients, the global model may
become biased, thus working efficiently on some cases but
inaccurately on others. Also, the presence of non-iid data can
affect the federated training procedure in terms of delaying or
hindering convergence.
A. Related Work
The related work is organized into two subsections. The
first focuses on the design of general FL-based IDS, while the
second examines studies that address non-IID data challenges
in FL-based IDS. The latter will primarily be the driving factor
for the motivation behind our proposed approach.
1) FL-Based IDS: Several works investigate the role and
impact of FL in cybersecurity and, more precisely, in the scope
of intrusion detection. Some survey papers in this field are
listed in [8], [9], [10], [11], [12]. In [8], the authors present a
comprehensive survey regarding the impact of FL within the
scope of intrusion detection, highlighting challenges and future
directions. In [9], a detailed comparison regarding centralized,
distributed and FL-driven intrusion detection mechanisms for
IoT environments was provided. Similarly, the authors in [10]
discuss advances of FL within cybersecurity applications in
IoT ecosystems. Reference [11], provide a comprehensive
study regarding FL-driven intrusion detection, game theory,
social psychology and explainable AI. Finally, in [12], the
authors focus their attention on security and privacy issues
regarding FL applications. Next, we further discuss recent
works that deliver FL-driven IDS.
In [13], the authors introduce DeepFed, an FL-driven IDS
for cyber-physical systems. In this method, a trust authority is
introduced, whose role is to produce the encryption keys for
the proposed Pailier public-key cryptosystem utilized for the
communication between the server and the industrial clients.
For the detection process, the authors leverage a combined
convolutional neural network (CNN) - gated recurrent unit
(GRU), while special attention is paid to the proposed Pailierbased secure communication protocol for the communication
between the server and the clients. Finally, three evaluation
metrics are considered, namely accuracy, precision, recall and
F1-score, demonstrating the detection efficiency of DeepFed.

2945

In [14], authors describe MV-FLID, a multi-view FL-based
IDS which focuses on the detection of attacks against message queuing telemetry transport (MQTT) communications
within IoT environments. In particular, MV-FLID adopts a
multi-view approach, combining bi-directional flow features,
un-directional flow features and packet features. An FL model
is generated for each of the previous viewpoints. Regarding
the feature selection process, the authors leverage the grey
wolf optimizer introduced in [15]. Next, the federated training
procedure follows. Finally, an ensemble-based technique is
used to combine the outcomes of the FL models in order to
provide a unified prediction outcome. Traditional performance
evaluation metrics are considered to demonstrate the overall
detection effectiveness of MV-FLID.
In [16], a semisupervised FL scheme for intrusion detection within IoT environments was introduced. The proposed
scheme relies on CNN models, while four phases are followed
in an iterative manner within the FL fashion, namely (a) client
training, (b) knowledge distillation, (c) discrimination between
familiar and unfamiliar traffic packets and (d) hard-labeling
and voting. During the first phase, the clients train their
CNNs with private local data. In the second phase, knowledge
distillation follows a teacher-student approach, where a teacher
model guides the training of a student model, providing soft
targets or logits. Next, a discrimination network is used from
the FL server to evaluate further the predicted labels of each
client’s CNN. Finally, hard labeling and voting mechanisms
take place in order to consider only the labels from the
majority of the FL clients and proceed with the aggregation
process.
2) Non-iid Data in FL-Based IDS: Non-iid data and data
heterogeneity refers to the variation in the distribution, types,
or characteristics of data across different clients. This variation poses challenges when creating FL models, as they
need to generalize across diverse datasets. Towards tackling
the above challenge in FL-based IDS, [17] proposes the
FL-based Attention-Gated Recurrent Unit (FedAGRU) to
address, among others, the issue of different label distribution across clients’ data, thus demonstrating performance
gains over conventional FL aggregation strategies. Moreover,
in [18], the authors propose a peer-to-peer algorithm, namely
P2PK-SMOTE, to train FL-driven anomaly detection models
in non-iid data scenarios. The latter refers to inter and intraimbalanced classes across the FL clients. Numerical results
indicated performance gain of the proposed strategy against
non-rebalancing approaches. Additionally, [19] leveraged the
Fed+ method [20] for FL-driven intrusion detection in heterogeneous networks. The clients own datasets from various
types of networks, such as industrial IoT, wireless networks
and wireless vehicular networks, while Fed+ facilitates the
generation of personalized local models with enhanced attack
classification performance. The concept of non-iid data was
supported by the assumption that the data stem from different
network devices. In addition to this, in [21], the authors
take Fed+ a step further by incorporating differential privacy
techniques. Next, in [22], data augmentation techniques to
address class imbalance and non-iid settings are investigated.
Specifically, data augmentation methods such as SMOTE,

2946

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 4, AUGUST 2025

ADASYN and adversarial generative networks were invoked
to support upsampling of the imbalanced client data. The evaluation results indicate a performance improvement compared
with baselines that do not rely on data augmentation strategies.
Finally, in [23], authors propose a clustering-enabled FL metalearning framework to tackle class imbalance and non-iid data.
Specifically, they design a data- and model-agnostic metasampler that adaptively balances local data sets, and thus,
mitigating the data imbalance problem. Hence, the focus of
this work lies mainly in dealing with class imbalance in FLbased IDS.
B. Motivation
Undoubtedly, the previous works offer valuable insights and
methodologies. However, in the majority of them, the assumption of iid data across the clients is not valid within realistic
FL conditions. Conventional FL strategies like FedAvg are
not designed for handling non-iid data and may experience
notable performance degradation or even divergence when
applied in such situations [24]. Although the works [17], [18]
and [16], [22], [23] successfully examine and design FL-based
IDS considering non-iid data, emphasis was mainly given to
the following cases: (a) class imbalance across clients datasets
and/or different label distributions and (b) different number
of samples per client. Therefore, the aforementioned works
mainly address class and data imbalance issues. The case of
non-iid features among clients’ data is underrepresented, while
its impact on the global model convergence remains vague.
On the contrary, the authors in [19] study a broader aspect of
non-iid settings by considering heterogeneous datasets across
the clients. However, personalized FL methods such as Fed+
are employed, generating multiple personalized local models
instead of a unified global one. Such approach prevents the
generation of a single global model, that can be further
distributed to third parties.
Well-known techniques in the literature that address noniid data issues include FedProx [25], which stabilizes local
training by introducing a proximal term, FedNova [26],
which considers that each client may conduct a different
number of local training steps, and SCAFFOLD [27], which
uses control variates both at server and clients to estimate the
model update direction. However, as mentioned previously, a
particular example of non-iid data among clients is the case of
non-iid features, which has generally received less attention in
the FL-related literature. Methods addressing this issue mainly
rely on layer normalization [28] and batch normalization [29]
techniques. Specifically, [29] proposes FedBN, a method
that incorporates batch normalization layers on local clients’
model, which are not included in the aggregation step at
the server side. Although FedBN has shown potential in
mitigating non-iid features, it assumes that clients possess
batch normalization layers and have been actively involved
in the FL training. Consequently, non-participating clients
that may want to access the global model are excluded, as
the method cannot generate a universally applicable global
model. This fact implies limitations in distributing the global
model to additional entities. Moreover, the work in [30],

proposed a FL/split learning method to address non-iid data in
a user authentication scenario. The method involves splitting
a global model trained initially on a public dataset, into
two parts: a feature extractor subnetwork and a classifier
head. Clients compute the mean and variance of the feature
extractor based on their local datasets and send these statistics
to the server. The server then generates a synthetic dataset
by sampling from the aggregated client statistics. While this
method proved effective, it assumes the availability of a preexisting public dataset on the server and depends on data
augmentation techniques. Finally, as per [31] experimental
study, none of the existing state-of-the-art FL methods and
aggregation strategies for non-iid data outperform the other
ones in all cases. Therefore, exploring novel techniques to
address the impact of data heterogeneity in terms of noniid features, particularly within FL-based IDS, which is still
immature in the context of the mentioned challenge, is an
interesting and promising topic. To the best of our knowledge,
limited attention has been given to the issue of non-iid features
among clients in FL-based IDS. Notably, the works [17], [18],
[19], [20], [21], [22], [23] do not particularly focus on this
subject.
C. Contribution
In light of the aforementioned motives, in this paper, we
introduce the Statistical Averaging (StatAvg)
method to circumvent the challenges of non-iid features
of clients in FL. Due to different feature distributions
across clients, the local data normalization process may differ
from client to client. It is noted here that data normalization refers to the scaling of the input data, e.g., the
scaling of features through methods such as standard scaling.
Inconsistencies in feature distribution can hinder or even
prevent the convergence of the federated global model, as each
local model is trained on a different input data distribution. To
this end, StatAvg aims at producing global data statistics that
can serve as a universal normalization for the local data of each
client. This approach enables clients to scale their input data
(features) based on this unique global scaler. To achieve this,
the server is responsible for collecting the local data statistics
of the clients and afterwards aggregating them properly to
produce global data statistics. In this way, clients use a
shared global normalization scale, based on the aggregated
data statistics, to standardize their local data, helping to reduce
the impact of non-iid features in their individual datasets. The
contributions of our work are summarized as follows:
• The StatAvg method is proposed to alleviate the
effects of non-iid feature distributions in FL. According
to StatAvg, the FL clients calculate their local data
statistics, specifically the mean and variance of the input
feature vector, and transmit them to the server. The server
aggregates the clients’ local statistics to generate global
statistics. We prove mathematically that the aggregated
global statistics represent the true mean and variance of the
combined datasets across all clients. Afterwards, the server
broadcasts the global statistics to all clients, normalizing
their input features based on these global statistics.

BOUZINIS et al.: STATAVG: MITIGATING DATA HETEROGENEITY IN FL FOR IDS

•

StatAvg enables the generation of global data statistics
that can be interpreted as a universal input data normalization process and applied before feeding the data
into the global model. It is important to emphasize that
typically, a trained model should be accompanied by the
corresponding normalization technique on the input data.
Otherwise, the model will be ineffective during inference,
without the proper input data normalization. However,
this aspect is often overlooked in the existing literature.
Therefore, StatAvg serves as a means to offer a global
data normalization technique that can be applied to the
global model by external entities that are not necessarily
involved in the training procedure.
• The performance of StatAvg is evaluated through
experiments on two open datasets for host and network
intrusion detection, namely the TON-IoT and CIC-IoT2023. Various FL aggregation strategies are used as
baseline methods for comparison, including FedAvg,
FedLN [28], and FedBN [29]. The demonstrated results
showcase the prevalence of StatAvg over the baselines
in terms of evaluation metrics such as the detection
accuracy and the F1 score. Finally, some illustrative
insights are provided that justify the presence of clients’
non-iid features on the examined intrusion detection
datasets.
D. Structure
The structure of the paper comes as follows. Section II
provides preliminary information regarding FL and non-iid
features. Next, Section III presents and analyzes StatAvg.
Finally, Section IV focuses on the evaluation analysis of
StatAvg, while Section V concludes this paper.
II. P RELIMINARIES OF F EDERATED L EARNING
A. FL System
We consider an FL environment consisting of N clients,
indexed as i ∈ N = {1,2,. . ., N} and a server. Each client
j
i
owns a dataset Di = {(x ji , yij ) ∈ RS × C}D
j =1 , where x i is
the j-th input sample, Di = |Di | is the number of samples
and S denotes the number of features. Here, R denotes the
set of real numbers. Additionally, we denote C as the set to
j
which the label yi belongs, e.g., it could be a subset of the real
numbers, a set of categorical values for classification tasks, etc.
In this paper, C contains the labels of cyberattacks and will
be described below in this work, along with the description of
the datasets used in the evaluation experiments.
The overall dataset across all clients is denoted
as D =

∪ Di and the size of all training data is D = N
n=i Di . The
i∈N

loss function of client i, is defined as:
Di 

1 
φ w , x ji , yij ,
Di

Fi (w ) 

∀i ∈ N ,

(1)

j =1

j

j

where φ(w , x i , yi ) captures the error of the model parameter
w ∈ RK for the input-output pair (x ji , yij ), where K is the
size of model parameters. The ultimate goal of the FL process

2947

is to obtain the global parameter w , which minimizes the loss
function on the whole dataset.
F (w ) =

N


ni Fi (w ),

(2)

n=1
i
where ni = D
D is the proportion of data samples owned by
client i relative to the entire dataset.
In a nutshell, the FL process is executed for a specified
number of communication rounds. At the t-th round, the server
firstly broadcasts the global model w (t) to all clients. Each
(t)
client i updates its local model w i via a gradient-based
method on the loss function Fi and uploads it to the server.
Finally, the server generates the global model w (t+1) by using
an aggregation strategy of its preference. The aforementioned
process is repeated for the selected number of rounds until the
convergence of the global model is achieved.

B. Non-iid Features in FL
In line with the definitions provided by [24] and [29], the
presence of non-iid features across clients can be expressed
through the following concepts:
• Feature distribution skew (covariate shift): The marginal
distributions Pi (x ) varies across clients, even if Pi (y|x )
is the same for all clients.
• Same label, different features (concept drift): The conditional distributions Pi (x |y) may vary across clients even
if Pi (y) is common. As such, the same label y can have
different features x for different clients.
Non-iid features can significantly degrade the performance
of FL, by introducing inconsistencies in model updates across
clients. Since each client is exposed to different input distributions, their local models may learn patterns that do not
generalize well to other clients. This inconsistency can result
in unstable training, where the global model struggles to
converge in a timely manner. In extreme cases, the divergence
between local models can be so severe that the global model
completely fails to converge. These challenges make it difficult
for the server to effectively aggregate the locally trained
models into a coherent global model that performs well across
all clients. Consequently, the presence of non-iid features
requires specialized techniques or modifications to standard
FL algorithms to ensure successful training and generalization.
III. S TATAVG - S TATISTICAL AVERAGING
A. Description and Algorithm
Traditionally, individual FL clients normalize their local
data based on their own local statistics, with the most prominent normalization technique being the z-score normalization,
i.e., clients subtract the mean from each data sample of a given
feature and then divide it with the standard deviation. This is
equivalent to shifting the input feature distribution to have a
zero mean and unit variance. Accordingly, in the testing phase,
the testing dataset is scaled based on the aforementioned
normalization, individually per client. In the presence of noniid features between clients, the local normalization process
may significantly differ from client to client. As a result,

2948

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 4, AUGUST 2025

this variability may affect the convergence of the global
FL model since each local model is trained on a different
input data distribution. To tackle the issue of non-iid features
across clients, our objective is to discover global statistics that
clients can share without requiring access to their raw data.
Typical statistical metrics include the mean and variance of the
features, whereas this study investigates the impact of these
particular metrics.
In the light of the previous discussion, we proceed to
compute the mean and variance for each client’s features. The
mean value across all samples of a feature s ∈ S of client i,
where S is the entire feature set, is given as:
D

i
1 
j
xi,s
μi,s =
Di

(3)

j =1

Algorithm 1 StatAvg
Input: N , {Di }i∈N , w (1)
Output: w , {μG , σ 2G }
1: for t = 0,1,2,... do
2:
if t = 0 then
3:
for each client i ∈ N do
4:
calculate μi , σ 2i according to (3), (4)
5:
send μi , σ 2i to the server
server calculates
 the global statistics as:
μG = i∈N ni μi ,



σ 2G = i∈N ni σ 2i + (μi − μG )2

6:

server sends {μG , σ 2G } to all clients
for each client i ∈ N do
normalize input features as:

7:
8:
9:

and μi = (μi,1 , μi,2 , . . . , μi,S ) is the vector with all the
j
is the
means of each feature. Its is worth noting that xi,s
j

s-th entry of x i . Accordingly, the corresponding variance is
calculated as:
Di 
2
1 
j
2
xi,s
=
− μi,s
(4)
σi,s
Di

10:

2 , σ 2 , . . . , σ 2 ). Hereinafter, with the term
and σ 2i = (σi,1
i,2
i,S
local statistics of client i, we refer to the tuple {μi , σ 2i }.
The StatAvg strategy aims at obtaining the global statistics
{μG , σ 2G } of the overall dataset D by aggregating the local
statistics {μi , σ 2i }i∈N . In this manner, all clients can normalize their data based on global statistics, which guarantees a
common normalization/scaling of the input data. The detailed
process of StatAvg is described in Algorithm 1.
As can be seen, the StatAvg strategy occurs solely during
the first round (t = 0), prior to the actual FL training. Firstly,
in steps 2 - 4, each client calculates its local statistics and
sends them to the server. Following that, in steps 5 - 6, the
server calculates the global statistics based on the received
local statistics and broadcasts them back to the clients. It
is worth mentioning that the operations in step 5 are carried out element-wise. The rationale behind the aggregation
technique used to obtain μG and σ 2G is explained later in
this work. Afterwards, in steps 7 - 8, the clients normalize
their input features based on the global statistics by utilising
conventional z-score normalization. It should be highlighted
that the communication overhead for exchanging the local
and global statistics between the clients and the server is
negligible since it takes place solely during the first round.
Additionally, the size of the local statistics tuple is negligible
compared to the size of the local model, because the number
of features is typically much smaller than the number of model
parameters (weights) used during training, i.e., 2S  K. At
step 10 and afterwards, a conventional FL process follows,
e.g., FedAvg, that will ultimately generate the global FL
model. However, the selection of the aggregation strategy
is not limited to FedAvg and can vary according to the
particularities of the underlying FL task. Note also that during
the client local update in step 13, η is the learning rate
(t)
and ξ i ⊆ D̃i is a randomly sampled mini-batch from the

14:

j =1

j
xi,s
−μG,s
, ∀j ∈ {1, ..., Di }, ∀s ∈ S
σG,s
j j Di
D̃i = {(x̃ i , yi )}j =1

j

x̃i,s =
11:
12:
13:

D̃i
15:
16:

else
 standard FL procedure
server sends w (t) to all clients i ∈ N
for each client i ∈ N do


(t)
(t)
(t) (t)
(t)
w i = w i − η∇Fi w i , ξ i , ξ i ⊆
(t)

send w i to the server

(t)
w (t+1) = i∈N ni w i

17: w = w (t)

normalized local dataset D̃i . Finally, if the local dataset Di
(t)
changes dynamically in each round (it can be denoted as Di ),
applying StatAvg in such case is straightforward. This can
be done by computing the local statistics in each round and
(t)
constructing the normalized dataset D̃i , based on the global
statistics of the given round.
It should be again clarified that StatAvg focuses on the
aggregation of statistical metrics rather than local models
(t)
w i , facilitating its integration with any model aggregation strategy. Fig. 1 provides an illustration of StatAvg’s
implementation. Finally, we stress that through StatAvg,
a universal input data normalization technique is provided.
This is a crucial remark since a trained model should
be paired with the appropriate data normalization technique (also known as scaler) to render it effective during
inference.
In the continue, we will show that μG and σ 2G are the
mean and variance of the overall dataset D. First, we assume
that Di ∩ Dk = ∅, ∀i , k ∈ N , i = k . This implies that
all local datasets are pairwise disjoint. The assumption is
reasonable, considering that each dataset originates from a
distinct client, thus making it highly unlikely - if not impossible - for identical samples to appear across different local
datasets. To this end, we proceed to formulate the following
proposition.

BOUZINIS et al.: STATAVG: MITIGATING DATA HETEROGENEITY IN FL FOR IDS

Fig. 1.

Visual representation of StatAvg design and implementation.

Proposition 1: Let x i,s ∈ RDi be the vector containing
the s-th feature across all samples of Di . Also, let z s =
(x 1,s , . . . , x N ,s ) be the concatenation of all clients vectors,
with z s ∈ RD . The mean and variance of z s are given as

ni μi,s
μG,s =
2
σG,s
=

i∈N



i∈N


2 

2
.
ni σi,s
+ μi,s − μG,s

μG =
=

D

D

N

l=1

i=1 j =1

N

D

i=1

j =1

ni μi .

j

(6)

2 , first, it is noted that for the local
Before examining σG
variances, it holds:

∀i ∈ N .

(7)

j =1

Similarly, for z we get
2
D=
σG

D


(zl − μG )2 =

l=1

Di 
N 
2

j
x i − μG
i=1 j =1

Di  
N 

2
xij − 2xij μG + μ2G .
=

(8)

i=1 j =1

The inner sum in the last term of (8) can be expanded by
adding and subtracting μ2i , as:
D i  

j 2
j
− 2xi μG + μ2G + μ2i − μ2i
xi

=

D i 
2

xij − μi + 2xij (μi − μG ) + μ2G − μ2i

j =1

j =1

= Di σi2 + Di μ2G − 2Di μi μG + Di μ2i
= Di σi2 + Di (μi − μG )2 .

2
σG
=

i=1

Di 
2

xij − μi ,
σi2 ni =

Di 
2

xij − μi + 2Di μi (μi − μG ) + Di μ2G − Di μ2i

(9)

By combining (9) with (8) we conclude to

i
i
xi
1 
1 
1  
j
zl =
xi =
Di
D
D
D
Di

N


=

(5)

Proof: First, the notation of s is dropped for the simplicity
of presentation. It is straightforward to compute the mean of
z as:

j =1

2949


i∈N



ni σi2 + (μi − μG )2 ,

(10)

which completes the proof.
Proposition 1 provides a way to obtain the global mean and
variance across the whole dataset D for a given feature s. The
proof can be easily generalized ∀ s ∈ S, which gives rise to the
vector representation of the global mean and variance for each
feature, i.e., μG and σ 2G , respectively. This result is used in
step 5 of Algorithm 1 to derive the global mean and variance.
B. Differential Privacy Extension
It is clarified that the local statistics being shared with the
server are high-level, aggregated summaries of the data and
do not reveal individual data points or sensitive attributes.
Therefore, these statistics lack sufficient granularity to reconstruct the underlying dataset or any individual client’s private
information. However, to further enhance privacy, differential privacy (DP) strategies could be easily integrated into
the proposed method during the transmission of the local
statistics [32]. Specifically, by adding a controlled amount of
random noise to the local statistics, DP ensures that individual
client contributions cannot be easily inferred by the server.
According to DP principles, instead of directly sending the
local statistics {μi , σ 2i } to the server, the clients perturbs them
and send a distorted version. Specifically, to ensure (, δ)DP [32], for a given feature s ∈ S, client i adds Gaussian
2 as follows:
noise to μi,s and σi,s


μ̃i,s = μi,s + Gaussian 0, ζμ2i,s ,

2
2
σ̃i,s = σi,s + Gaussian 0, ζσ22 ,
i,s

(11)

2950

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 4, AUGUST 2025

TABLE I
L IST OF N OTATIONS

2 are described,
where the variance of the noise for μi,s and σi,s
respectively as

2 ln(1.25/δ) 2
Δμi,s ,
2
2 ln(1.25/δ) 2
ζσ22 =
Δσ2
i,s
i,s
2

TABLE II
TON-I OT DATASET: F EATURE D ESCRIPTION

ζμ2i,s =

(12)

and the sensitivities Δ2μi,s , Δ2σ2 of the mean and variance
functions are given by
Δ2μi,s =
Δ2σ2 =

i,s

j
j
} − minj {xi,s
}
maxj {xi,s



Di

,

2
j
j
maxj {xi,s
} − minj {xi,s
}

i,s

Di

,

(13)

accordingly. By applying the above process for each feature
s ∈ S independently, each client i creates the peturbated local
statistics {μ̃i , σ̃ 2i } and sends them to the server, which then
proceeds with the conventional aggregation process.
IV. E VALUATION A NALYSIS
This section presents experiments conducted on different
datasets to detect intrusions in a federated setting. The effectiveness of the proposed strategy StatAvg is evaluated by
comparing it with various baseline methods.
A. Evaluation Datasets
The experiments were conducted on the following wellknown public datasets.
TON-IoT Dataset: Among others, the TON-IoT
Dataset [33] includes operating system data of Ubuntu versions
14 and 18, which is adopted in our work. More specifically,
it includes audit traces documenting memory activities within
the operating system. The dataset is suitable for training
and designing host-based IDS. Also, the dataset is composed
of data stemming from various physical or virtual devices
belonging to the edge and cloud layers. The description of
the selected features is provided in Table II. Furthermore,
the attacks on the host system that serve as the labels of the
dataset are “dDoS”, “DoS”, “Injection”, “Password”, “Mitm”,
while also a class named “Normal” is included, indicating the

normal behaviour of the host system. More details regarding
the dataset can be found in [33] and [34].
CIC-IoT-2023 Dataset: The CIC-IoT-2023 Dataset [35] is
a realistic IoT attack dataset, using an extensive topology composed of multiple IoT devices designated as either attackers or
targets. The dataset entails 48 features that are characterized
by metrics such as packet flow statistics, employed application
layer protocols, TCP flags, etc. As we do not explicitly
describe all features for brevity, additional information can be
found in [35]. Furthermore, the dataset categorizes attacks into
eight classes, namely “Brute force”, “dDoS”, “DoS”, “Mirai”,
“Recon”, “Spoofing”, “Web-based”, and “Normal”.
B. Baseline Aggregation Methods
To evaluate the performance of StatAvg, we use the
following baseline aggregation strategies:
FedAvg: It is the de facto approach for FL [6]. Clients
perform local model updates and the server executes the
aggregation of the local models to generate the global
model.
FedLN: The layer normalization is included in the local
models for mitigating the effects of non-iid features [28].
FedLN performs local updates and averages local models
similarly to FedAvg.

BOUZINIS et al.: STATAVG: MITIGATING DATA HETEROGENEITY IN FL FOR IDS

2951

TABLE III
E XPERIMENTAL S ETTINGS

FedBN: Employs local batch normalization (BN) to the
local models prior to averaging them towards alleviating feature shift. Nonetheless, FedBN assumes that local models have
BN layers and omits their parameters from the aggregation
step at the side of the server [29].
It is worth noting that FedLN and FedBN are specially tailored to address the issue of non-iid features,
justifying their selection. As follows, in FedAvg, FedLN
and FedBN, the normalization of the local training data
is performed based on the local client statistics, aligning
with the conventional FL approach. Also, the testing data
undergo scaling in accordance with the respective local normalization for each client individually. Finally, it is noted
that the proposed technique StatAvg utilizes FedAvg at
step 9 of Algorithm 1 as the default model aggregation
strategy.
C. Experimental Setup
The following settings apply to all experiments unless specified otherwise. The number of clients has been set as N = 5
and N = 10, while all clients are considered to participate in
every FL round. Also, the number of FL rounds is set to 50 and
80, for N = 5 and N = 10, respectively. Each client receives an
equal proportion ni = N1 of the original dataset D. Moreover,
the division is conducted through stratification based on the
labels of the original dataset, aiming to approximate a common
Pi (y) across all clients. This implies that clients share a
common label distribution. Following that, each client splits
its local dataset into training and testing subsets, with a ratio
of 4 to 1. Due to the significant class imbalance in the datasets,
each client generates synthetic instances from the minority
classes in the training set by using SMOTE [36]. It is noted
that SMOTE is applied independently on each client, after the
splitting of the overall dataset.
The local model of each client is a neural network consisting
of 3 Fully Connected (FC) hidden layers with 128 neurons
and ReLU activation, denoted as (FC(128), ReLU), followed
by a softmax activation on the output layer. In the case of
the baselines FedLN and FedBN, layer normalization (LN)
and batch normalization (BN) layers are incorporated into
the local models, resulting in each layer being structured as
(FC(128), ReLU, LN) and (FC(128), BN, ReLU), respectively. For the local training updates, the Adam optimizer is
adopted [37]. Finally, additional settings are summarized in
Table III1
1 In the spirit of reproducible research, the code used for the numerical
results is available at: https://flower.ai/docs/baselines/statavg.html.

Fig. 2.

Testing accuracy on TON-IoT dataset (N = 5 clients).

D. Evaluation Results
Regarding the performance evaluation, we use common
evaluation metrics such as the confusion matrix, accuracy, and
F1 score. Given a specific attack/class, the confusion matrix
includes the following standard metrics: the True Positive (TP)
represents instances where the model correctly identifies a
sample as belonging to a specific attack type. True Negative
(TN) counts instances where the model accurately identifies
a sample as not belonging to a specific attack type when it
truly does not. False Positive (FP) denotes instances where
the sample is predicted as of a certain attack, but actually,
the sample does not belong to that attack type. False Negative
(FN) is the number of instances for which the model fails to
predict a sample as a specific attack type, even though the
sample actually belongs to that attack. Next, the accuracy and
F1 score are defined as:
ACC =

TP + TN
TP + TN + FP + FN

(14)

2TP
,
2TP + FP + FN

(15)

and
F1 =

respectively.
The evaluation metrics showcased in the results have been
averaged across all classes due to the multi-class nature of the
problems we are addressing. Finally, it is noted the evaluation
was performed using clients’ testing sets, and the demonstrated
results were also averaged across all clients.
First, the evolution of testing accuracy throughout the
FL rounds is evaluated, for both N = 5 and N = 10
clients. In Fig. 2, 3, and Fig. 4, 5, the StatAvg strategy
is compared with the selected baselines on the TON-IoT
and CIC-IoT-2023 datasets, respectively. It is evident that

2952

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 4, AUGUST 2025

TABLE IV
E VALUATION M ETRICS ON TON-I OT DATASET

Fig. 3.

Testing accuracy on TON-IoT dataset (N = 10 clients).

Fig. 4.

Testing accuracy on CIC-IoT-2023 dataset (N = 5 clients).

Fig. 5.

Testing accuracy on CIC-IoT-2023 dataset (N = 10 clients).

StatAvg significantly outperforms the baseline strategies
across both datasets in terms of accuracy. Moreover, the
convergence curve of StatAvg is more stable compared to
that of the baseline methods, which display higher variance.
The exhibited performance gain lies in the fact that StatAvg
utilizes global statistics to normalize the clients’ features.
Although FedLN and FedBN have been designed to minimize
the effects of non-IID features between clients, it is discernible
that they struggle to address this issue in certain datasets.
The variations in local client statistics, and consequently, the
diverse local normalization utilized, appear to degrade the
performance of FL. Additionally, it is observed that Statavg

TABLE V
E VALUATION M ETRICS ON CIC-I OT-2023 DATASET

consistently outperforms the baseline methods in both client
settings, demonstrating its robustness to client scaling.
Moreover, in Table IV and Table V, some evaluation metrics for the case of TON-IoT and CIC-IoT-2023 datasets are
demonstrated, respectively. The considered metrics showcase
the performance of the best models encountered during the FL
training for each strategy. It can be observed that StatAvg
has superior performance against the baseline strategies.
Specifically, in the case of the TON-IoT dataset, StatAvg
demonstrates a notable improvement, for both settings of
clients, of over 17% and 16% in accuracy and F1 score, respectively, compared to the second-best strategy FedLN. Also,
when considering the CIC-IoT-2023 dataset, the corresponding
increase is over 4% and 2% for accuracy and F1 score. The
detailed confusion matrices of the StatAvg metho, when
considering N = 5 clients, are presented in Fig. 6 and Fig. 7,
for the TON-IoT and CIC-IoT-2023 datasets, respectively. In
both datasets, it is evident that some classes are easier to
classify, e.g., “DDoS”, “DoS”, “Mirai”, and “Normal”. This
can be attributed to the large number of samples that these
classes usually have (e.g., “DoS” and “Normal” are majority
classes in both datasets), as well as their more recognizable
traffic patterns. On the other hand, certain classes are often
misclassified, e.g., “Brute Force”, “Recon”, “Spoofing” in
Fig. 7, likely due to the similarity in their underlying traffic
patterns [35].
To shed light on the concept of non-iid features, we present
some illustrative examples derived from the examined datasets.
First, we take a deeper look into the training samples of the
CIC-IoT-2023 dataset, focusing specifically on those labelled
with the attack category y = “Web-based”. Fig. 8 illustrates

BOUZINIS et al.: STATAVG: MITIGATING DATA HETEROGENEITY IN FL FOR IDS

2953

Fig. 8. Distribution of the feature “Flow Duration”, given the attack label
“Web-based”, on CIC-IoT-2023 dataset.
TABLE VI
S TATISTICAL M ETRICS OF C LIENTS ’ F EATURES ON TON-I OT DATASET

Fig. 6.

Confusion matrix of StatAvg on TON-IoT dataset.

in Table VI. Here, statistical metrics for selected features
from the TON-IoT dataset have been calculated. It can be
observed that the feature “VSIZE” demonstrates consistent
mean and variance across clients, while the feature “MINFLT”
displays high variations in the statistical metrics. This example
highlights the statistical differences that some features may
exhibit among clients, which in turn influences the local
normalization of the features and potentially hinders the FL
stability and convergence.
V. C ONCLUSION

Fig. 7.

Confusion matrix of StatAvg on CIC-IoT-2023 dataset.

the distribution of the feature “Flow Duration” for the clients
i = {1,2}, formally written as Pi (xi,s |y = “Web-based”)
where s = “Flow Duration”. It can be observed from Fig. 8
(a) that the distributions of the clients differ. Nevertheless,
it remains uncertain whether this disparity in distributions is
inherent or if it is related to the limited number of samples
within the selected class. It is worth noting that the “Webbased” class is indeed a minority class. From Fig. 8 (b), it
is evident that the difference in distributions persists after
upsampling the dataset via SMOTE. This example shows that
even if Pi (y) is approximately the same for all clients, as
previously explained in the experimental setup, the conditional
distributions Pi (x |y) can still differ. This phenomenon is
related to the concept of Same label, different features,
discussed in Section II. Another example that highlights
the differences in the distributions of features is presented

This paper proposes the StatAvg technique for mitigating
the impact of non-iid features among clients in FL settings.
The key aspect of StatAvg is to produce global data statistics
based on the local data statistics of FL clients. The generation
of global statistics, which is carried out by the server, gives rise
to a universal data normalization technique that is performed
by all clients. Particular attention is given to FL-based IDS,
which is the focus of the experiments that were conducted.
The results corroborate the effectiveness of StatAvg in
providing robust FL convergence and classifying cyber-attacks
compared to various baseline FL schemes. Moreover, valuable
insights are offered within the scope of non-iid features among
clients for the selected intrusion detection datasets. Finally,
as StatAvg precedes the actual FL procedure, it can be
combined with any FL aggregation strategy, a topic which
is left for future investigation. Moreover, the applicability of
StatAvg is not limited solely to FL-based IDS, as its efficacy
may encompass any FL application associated with non-iid
features among clients.
ACKNOWLEDGMENT
Disclaimer: Funded by the European Union. Views and
opinions expressed are, however, those of the author(s) only
and do not necessarily reflect those of the European Union or

2954

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 4, AUGUST 2025

European Commission. Neither the European Union nor the
European Commission can be held responsible for them.
R EFERENCES
[1] X. Deng, B. Chen, X. Chen, X. Pei, S. Wan, and S. K. Goudos, “Trusted
edge computing system based on intelligent risk detection for smart IoT,”
IEEE Trans. Ind. Informat., vol. 20, no. 2, pp. 1445–1454, Feb. 2024.
[2] M. Taddeo, T. McCutcheon, and L. Floridi, “Trusting artificial intelligence in cybersecurity is a double-edged sword,” Nat. Mach. Intell.,
vol. 1, no. 12, pp. 557–560, 2019.
[3] X. Deng et al., “A review of 6G autonomous intelligent transportation
systems: Mechanisms, applications and challenges,” J. Syst. Architect.,
vol. 142, Sep. 2023, Art. no. 102929.
[4] P. Radoglou-Grammatikis et al., “Strategic honeypot deployment in
ultra-dense beyond 5G networks: A reinforcement learning approach,”
IEEE Trans. Emerg. Topics Comput., vol. 12, no. 2, pp. 643–655,
Apr./Jun. 2024.
[5] P. Radoglou-Grammatikis, P. Sarigiannidis, G. Efstathopoulos,
T. Lagkas, G. Fragulis, and A. Sarigiannidis, “A self-learning approach
for detecting intrusions in healthcare systems,” in Proc. IEEE Int. Conf.
Commun. (ICC), 2021, pp. 1–6.
[6] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. Y. Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” in Proc. Artif. Intell. Stat., 2017, pp. 1273–1282.
[7] Y. Lin et al., “DRL-based adaptive sharding for blockchain-based federated learning,” IEEE Trans. Commun., vol. 71, no. 10, pp. 5992–6004,
Oct. 2023.
[8] S. Agrawal et al., “Federated learning for intrusion detection system:
Concepts, challenges and future directions,” Comput. Commun.,
vol. 195, pp. 346–361, Nov. 2022.
[9] E. M. Campos et al., “Evaluating federated learning for intrusion
detection in Internet of Things: Review and challenges,” Comput. Netw.,
vol. 203, Feb. 2022, Art. no. 108661.
[10] B. Ghimire and D. B. Rawat, “Recent advances on federated learning
for cybersecurity and cybersecurity for federated learning for Internet of
Things,” IEEE Internet Things J., vol. 9, no. 11, pp. 8229–8249, Jun.
2022.
[11] S. Arisdakessian, O. A. Wahab, A. Mourad, H. Otrok, and M. Guizani,
“A survey on IoT intrusion detection: Federated learning, game theory,
social psychology, and explainable AI as future directions,” IEEE
Internet Things J., vol. 10, no. 5, pp. 4059–4092, Mar. 2023.
[12] V. Mothukuri, R. M. Parizi, S. Pouriyeh, Y. Huang, A. Dehghantanha,
and G. Srivastava, “A survey on security and privacy of federated learning,” Future Gener. Comput. Syst., vol. 115, pp. 619–640, Feb. 2021.
[13] B. Li, Y. Wu, J. Song, R. Lu, T. Li, and L. Zhao, “DeepFed: Federated
deep learning for intrusion detection in industrial cyber–physical
systems,” IEEE Trans. Ind. Informat., vol. 17, no. 8, pp. 5615–5624,
Aug. 2021.
[14] D. C. Attota, V. Mothukuri, R. M. Parizi, and S. Pouriyeh, “An ensemble
multi-view federated learning intrusion detection for IoT,” IEEE Access,
vol. 9, pp. 117734–117745, 2021.
[15] S. Mirjalili, S. M. Mirjalili, and A. Lewis, “Grey wolf optimizer,” Adv.
Eng. Softw., vol. 69, pp. 46–61, Mar. 2014.
[16] R. Zhao, Y. Wang, Z. Xue, T. Ohtsuki, B. Adebisi, and G. Gui,
“Semi-supervised federated learning based intrusion detection method
for Internet of Things,” IEEE Internet Things J., vol. 10, no. 10,
pp. 8645–8657, May 2023.
[17] Z. Chen, N. Lv, P. Liu, Y. Fang, K. Chen, and W. Pan, “Intrusion
detection for wireless edge networks based on federated learning,” IEEE
Access, vol. 8, pp. 217463–217472, 2020.
[18] H. Wang, L. Muñoz-González, D. Eklund, and S. Raza, “Non-IID
data re-balancing at IoT edge with peer-to-peer federated learning for
anomaly detection,” in Proc. 14th ACM Conf. Security Privacy Wireless
Mobile Netw., 2021, pp. 153–163.
[19] S. I. Popoola, G. Gui, B. Adebisi, M. Hammoudeh, and H. Gacanin,
“Federated deep learning for collaborative intrusion detection in heterogeneous networks,” in Proc. IEEE 94th Veh. Technol. Conf. (VTC-Fall),
2021, pp. 1–6.
[20] A. Kundu, P. Yu, L. Wynter, and S. H. Lim, “Robustness
and Personalization in federated learning: A unified approach via
Regularization,” in Proc. IEEE Int. Conf. Edge Comput. Commun.
(EDGE), 2022, pp. 1–11.
[21] P. Ruzafa-Alcázar et al., “Intrusion detection based on privacypreserving federated learning for the Industrial IoT,” IEEE Trans. Ind.
Informat., vol. 19, no. 2, pp. 1145–1154, Feb. 2023.

[22] B. Weinger, J. Kim, A. Sim, M. Nakashima, N. Moustafa, and K. J. Wu,
“Enhancing IoT anomaly detection performance for federated learning,”
Digit. Commun. Netw., vol. 8, no. 3, pp. 314–323, 2022.
[23] W. Han, J. Peng, J. Yu, J. Kang, J. Lu, and D. Niyato, “Heterogeneous
data-aware federated learning for intrusion detection systems via metasampling in artificial intelligence of things,” IEEE Internet Things J.,
vol. 11, no. 8, pp. 13340–13354, Apr. 2024.
[24] P. Kairouz et al., “Advances and open problems in federated learning,”
Found. Trends Mach. Learn., vol. 14, nos. 1–2, pp. 1–210, 2021.
[25] T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith,
“Federated optimization in heterogeneous networks,” Proc. Mach. Learn.
Syst., vol. 2, 2020, pp. 429–450.
[26] J. Wang, Q. Liu, H. Liang, G. Joshi, and H. V. Poor, “Tackling the objective inconsistency problem in heterogeneous federated optimization,” in
Proc. Adv. Neural Inf. Process. Syst., vol. 33, 2020, pp. 7611–7623.
[27] S. P. Karimireddy, S. Kale, M. Mohri, S. Reddi, S. Stich, and
A. T. Suresh, “Scaffold: Stochastic controlled averaging for federated
learning,” in Proc. Int. Conf. Mach. Learn., 2020, pp. 5132–5143.
[28] Z. Du et al., “Rethinking normalization methods in federated learning,”
in Proc. 3rd Int. Workshop Distrib. Mach. Learn., 2022, pp. 16–22.
[29] X. Li, M. Jiang, X. Zhang, M. Kamp, and Q. Dou, “FedBN: Federated
learning on non-IID features via local batch normalization,” 2021,
arXiv:2102.07623.
[30] P. Oza and V. M. Patel, “Federated learning-based active authentication
on mobile devices,” in Proc. IEEE Int. Joint Conf. Biometrics (IJCB),
2021, pp. 1–8.
[31] Q. Li, Y. Diao, Q. Chen, and B. He, “Federated learning on non-IID
data silos: An experimental study,” in Proc. IEEE 38th Int. Conf. Data
Eng. (ICDE), 2022, pp. 965–978.
[32] K. Wei et al., “Federated learning with differential privacy: Algorithms
and performance analysis,” IEEE Trans. Inf. Forensics Security, vol. 15,
pp. 3454–3469, 2020.
[33] A. Alsaedi, N. Moustafa, Z. Tari, A. Mahmood, and A. Anwar,
“TON_IoT telemetry dataset: A new generation dataset of IoT and
IIoT for data-driven intrusion detection systems,” IEEE Access, vol. 8,
pp. 165130–165150, 2020.
[34] N. Moustafa, M. Ahmed, and S. Ahmed, “Data analytics-enabled intrusion detection: Evaluations of ToN_IoT linux datasets,” in Proc. IEEE
19th Int. Conf. Trust Security Privacy Comput. Commun. (TrustCom),
2020, pp. 727–735.
[35] E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu, and
A. A. Ghorbani, “CICIoT2023: A real-time dataset and benchmark
for large-scale attacks in IoT environment,” Sensors, vol. 23, no. 13,
p. 5941, 2023.
[36] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer,
“SMOTE: Synthetic minority over-sampling technique,” J. Artif. Intell.
Res., vol. 16, pp. 321–357, Jun. 2002.
[37] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
2014, arXiv:1412.6980.

Pavlos S. Bouzinis received the Diploma and Ph.D.
degrees in electrical and computer engineering from
the Aristotle University of Thessaloniki, Greece, in
2019 and 2023, respectively, where he was a member
of the Wireless Communications and Information
Processing Group. He is currently works as a
Research Engineer with MetaMind Innovations P.C.
His main research interests include machine learning, optimization, and intrusion detection systems.
He has served as a Reviewer for several scientific
journals. He was an Exemplary Reviewer of IEEE
W IRELESS C OMMUNICATIONS L ETTERS, in 2021 (top 3% of reviewers).

BOUZINIS et al.: STATAVG: MITIGATING DATA HETEROGENEITY IN FL FOR IDS

Panagiotis Radoglou-Grammatikis (Member,
IEEE) received the Diploma and Ph.D. degrees
from the Department of Electrical and Computer
Engineering, University of Western Macedonia,
Greece, in 2016 and 2023, respectively. He
has published more than 50 research papers in
international scientific journals, conferences and
book chapters. He was included in Stanford
University’s list (shared by Elsevier) of the Top
2% of Scientists in the World for 2021 and 2022,
respectively. He is currently working as a Research
Director with K3Y Ltd., while he is also a Postdoc Researcher with the
ITHACA Lab, University of Western Macedonia and a Co-Founder of
MetaMind Innovations P.C. He is involved in several national and international
projects. His main research interests focus on AI-driven cybersecurity,
intrusion detection, and security games. He has received five best paper
awards. Finally, he is a member of ACM and the Technical Chamber of
Greece.

Ioannis Makris received the B.Sc. degree in
computer science with specialization in artificial
intelligence and software engineering from the
Aristotle University of Thessaloniki and the M.Sc.
degree in business analytics from the University of
Edinburgh. Furthermore, he is a Project Management
Professional by the Project Management Institute.
He is currently working as a Network and Security
Engineer/Researcher. His interests include privacypreserving AI techniques, interpretable machine
learning, and security.

Thomas Lagkas (Senior Member, IEEE) received
the Graduate (Hons.) degree from the Department
of Informatics, Aristotle University of Thessaloniki,
the Ph.D. degree in wireless networks, and the MBA
degree from Hellenic Open University. He received
a Postgraduate Certificate on Teaching and Learning
from The University of Sheffield. He is an Assistant
Professor with the Department of Computer Science,
Democritus University of Thrace and the Director
of the Laboratory of Industrial and Educational
Embedded Systems. He has been a Scholar of
the Aristotle University Research Committee and a Postdoctoral Scholar
of the National Scholarships Institute of Greece. His research interests are in
the areas of IoT communications with numerous highly cited publications.
He is a Fellow of the Higher Education Academy, U.K., and a member of
the Editorial Board of reputable scientific journals. Moreover, he actively
participates in several EU-funded research projects.

Vasileios Argyriou received the B.Sc. degree in
computer science from the Aristotle University of
Thessaloniki, Greece, in 2001, and the M.Sc. and
Ph.D. degrees in electrical engineering working on
registration from the University of Surrey, in 2003
and 2006, respectively. From 2001 to 2002, he
held a research position with Aristotle University,
with a focus on image and video watermarking. He
joined the Communications and Signal Processing
Department, Imperial College London, London, in
2007, where he was a Research Fellow working on
3D object reconstruction. He is currently a Professor with Kingston University,
London, working on computer vision and AI for crowd and human behavior
analysis, computer games, entertainment, and medical applications. Also,
research is conducted on educational games and on HCI for augmented and
virtual reality systems.

2955

Georgios Th. Papadopoulos (Member, IEEE)
received the Diploma and Ph.D. degrees in electrical and computer engineering from the Aristotle
University of Thessaloniki, Thessaloniki, Greece.
He is an Assistant Professor in the area of
computer graphics and computational vision with
the Department of Informatics and Telematics,
Harokopio University of Athens, Greece. He has
worked as a Postdoctoral Researcher with the
Foundation For Research And Technology Hellas,
Institute of Computer Science and the Centre for
Research and Technology Hellas, Information Technologies Institute. He has
published over 70 peer-reviewed research articles in international journals
and conference proceedings. His research interests include computer vision,
artificial intelligence, machine/deep learning, human action recognition,
human–computer interaction, and explainable artificial intelligence. He is a
member of the Technical Chamber of Greece.

Panagiotis Sarigiannidis (Member, IEEE) received
the B.Sc. and Ph.D. degrees in computer science from the Aristotle University of Thessaloniki,
Thessaloniki, Greece, in 2001 and 2007, respectively. He is a Director of ITHACA Lab, Co-Founder
of MetaMind Innovations P.C., and a Full Professor
with the Department of Electrical and Computer
Engineering, University of Western Macedonia,
Kozani, Greece. He has published over 270 papers
in international journals, conferences and book
chapters. He is involved in several national and
international projects. He served as the Project Coordinator of three H2020
projects, namely SPEAR, EVIDENT, and TERMINET. Moreover, he has coordinated national and Erasmus+ KA2 projects, while he served as a Principal
Investigator in SDN-microSENSE and three Erasmus+ KA2: ARRANGE-ICT,
JAUNTY, and STRONG. Finally, he participates in several editorial boards of
various journals. His research interests include telecommunication networks,
Internet of Things, and cybersecurity. He has also received five best paper
awards.

George K. Karagiannidis (Fellow, IEEE) received
the Ph.D. degree in telecommunications engineering from the Electrical Engineering Department,
University of Patras, Greece, in 1998.
He is currently a Professor with the Electrical
and Computer Engineering Department, Aristotle
University of Thessaloniki, Thessaloniki, Greece,
and the Head of Wireless Communications and
Information Processing Group. His research interests
are in the areas of wireless communications systems
and networks, signal processing, optical wireless
communications, wireless power transfer, and signal processing for biomedical
engineering. He recently received three prestigious awards: The 2021 IEEE
ComSoc RCC Technical Recognition Award, the 2018 IEEE ComSoc SPCE
Technical Recognition Award, and the 2022 Humboldt Research Award
from Alexander von Humboldt Foundation. He is one of the Highly Cited
Authors across all areas of Electrical Engineering, recognized from Clarivate
Analytics as the Web-of-Science Highly-Cited Researcher from 2015 to
2024. He is currently an Editor-in Chief of the IEEE T RANSACTIONS
ON C OMMUNICATIONS and in the past was an Editor-in Chief of IEEE
C OMMUNICATIONS L ETTERS.
PAPER_TEXT
