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
# [440] FedIn-NID: A Federated Learning Framework for Network Intrusion Detection in Large-Scale Heterogeneous Industrial IoT
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
编号：440
题名：FedIn-NID: A Federated Learning Framework for Network Intrusion Detection in Large-Scale Heterogeneous Industrial IoT
年份：2025
DOI：10.1109/tifs.2025.3602226
来源：IEEE Transactions on Information Forensics and Security
PDF：paper/10.1109_TIFS.2025.3602226.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、联邦学习、隐私保护与分布式协同
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\440.txt
- 原始字符数：61295
- 本次发送字符数：61295
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
9250

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

FedIn-NID: A Federated Learning Framework for
Network Intrusion Detection in Large-Scale
Heterogeneous Industrial IoT
Jingxin Mao , Zhiwei Wei , Bing Li , Member, IEEE, Rongqing Zhang , Member, IEEE,
and Lingyang Song , Fellow, IEEE

Abstract—The evolving Industrial Internet of Things (IIoT)
is shifting towards decentralized collaborative manufacturing,
posing heightened network security issues within interconnected
value chains, thus requiring advanced Network Intrusion Detection (NID) systems to identify potential threats. In this context,
traditional centralized NID systems are insufficient due to crossindustrial privacy concerns and interconnected secure threats.
Federated Learning (FL) has emerged as a promising solution
to enable the sharing of security insights without compromising
privacy across participants. However, establishing an FL-based
NID framework in realistic IIoT scenarios faces several hurdles,
including the limited availability of large-scale devices and
heterogeneous attack data distributions. The former leads to
inconsistent client participation and degraded performance, while
the latter hinders model convergence. To address these, we
propose a novel Federated Learning-based Industrial Network
Intrusion Detection (FedIn-NID) framework, incorporating a
multidimensional client selection strategy and a dynamic global
aggregation strategy. The selection strategy synergistically considers multidimensional factors including client availability, local
dataset distribution, and dataset size. This approach accommodates clients with varying availability and avoids the selection
of biased clients with data concentrated in a few categories.
During model aggregation, the proposed strategy leverages the
concept of exponential moving average to dynamically balance
the holistic yet slightly older knowledge in the global model
with the partial but relatively newer knowledge in local models,
ensuring effective aggregation and convergence of the global NID
model. Experiments demonstrate that FedIn-NID outperforms
baselines by 10% to 30%, showcasing remarkable robustness
with increasing data distribution heterogeneity and device count.
Received 4 October 2024; revised 27 June 2025; accepted 16 August 2025.
Date of publication 25 August 2025; date of current version 5 September
2025. This work was supported in part by the National Key Research and
Development Program of China under Grant 2022YFB3104200, in part by
the National Natural Science Foundation of China under Grant 62271351 and
Grant 62201390, and in part by the Fundamental Research Funds for the
Central Universities. The associate editor coordinating the review of this
article and approving it for publication was Prof. Abderrahim Benslimane.
(Corresponding author: Rongqing Zhang.)
Jingxin Mao and Rongqing Zhang are with the Thrust of Intelligent
Transportation, The Hong Kong University of Science and Technology (Guangzhou), Guangzhou 511453, China (e-mail: jmao913@connect.
hkust-gz.edu.cn; rongqingz@tongji.edu.cn).
Zhiwei Wei is with Shanghai Research Institute for Intelligent
Autonomous Systems, Tongji University, Shanghai 201210, China (e-mail:
2311769@tongji.edu.cn).
Bing Li is with the School of Computer Science and Technology, Tongji
University, Shanghai 200092, China (e-mail: lizi@tongji.edu.cn).
Lingyang Song is with the School of Electronics, Peking University, Beijing
100871, China (e-mail: lingyang.song@pku.edu.cn).
Digital Object Identifier 10.1109/TIFS.2025.3602226

Index Terms—Federated learning, industrial Internet of Things
(IIoT), network intrusion detection.

I. I NTRODUCTION

T

HE advent of Industry 4.0 marks a transformative era
in both manufacturing and service sectors, with the
Industrial Internet of Things (IIoT) serving as its cornerstone [1]. Enabled by advanced wireless technologies like 5G
and Beyond 5G (B5G), the IIoT landscape is increasingly
characterized by cross-industrial collaborative manufacturing,
allowing diverse entities and stakeholders to join forces
for resource sharing and cooperative work [2]. While this
integrated approach offers enormous benefits in terms of
operational efficiency and innovation, it introduces unique
network security challenges. In a collaborative manufacturing
ecosystem, entities not only share resources but also integrate
their data streams and control systems, increasing the surface
area for potential cyber-attacks, thereby exposing their collaborators to new and diverse threat landscapes. Subsequently, to
efficiently identify and counteract the various types of security
threats in the foreseeable collaborative IIoT paradigm, the
critical role of Network Intrusion Detection (NID) has been
magnified [3].
NID is a security mechanism designed to monitor and
analyze network traffic for signs of malicious attacks or
security policy violations. However, traditional NID methodologies, such as signature-based and rule-based systems [4],
[5], are becoming increasingly inadequate and less scalable
in collaborative manufacturing facilitated by the complex
interconnection of systems and attack-type imbalances. With
the development of powerful deep learning techniques, specifically exemplified by Convolutional Neural Networks (CNNs)
and Recurrent Neural Networks (RNNs), existing works have
turned to learning-based NID systems [6], [7], [8]. These deep
learning architectures are adept at modeling complex patterns
and extracting hierarchical features from data, making them
intrinsically suited for identifying a wide array of intrusion
activities in the next-generation IIoT. In [9], Shone et al.
introduced nonsymmetric deep autoencoder and random forest
classification for NID. In [10], Liang et al. proposed an
industrial NID algorithm based on multifeature data clustering
optimization model. In [11], Lin et al. introduced an intrusion
detection system featuring stacked sparse autoencoders and

1556-6021 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

MAO et al.: FedIn-NID: A FL FRAMEWORK FOR NID IN LARGE-SCALE HETEROGENEOUS INDUSTRIAL IoT

RNNs. In [12], He et al. proposed an intrusion detection model
that leverages multi-modal deep autoencoders and LSTM to
effectively integrate features from different levels of network
connections. In [13], Hu et al. proposed a deep learning-based
one-class intrusion detection scheme to improve the security
of industrial networks. In [14], Andresini et al. introduced a
method that represents network flows as images and obtains its
imagery representation by combining nearest neighbor search
and clustering processes. Thanks to the nonlinearity approximation capabilities of neural networks, the learning-based
NID methodologies can effectively extract latent features and
patterns from IIoT networks, and excels at detecting intrusions.
Nonetheless, these approaches necessitate extensive datasets
for effective training among different entities, a requirement
that often involves handling diverse data characteristics due
to the geographical distribution variances of these industrial
entities [15]. Further complicating matters is the sensitive
nature of IIoT data, which demands adherence to rigorous
privacy regulations and ethical guidelines, thereby obviating
the feasibility of centralized data pooling for model training
[16]. In light of these constraints, Federated Learning (FL) [17]
emerges as a promising solution. FL aligns seamlessly with the
distributed and edge-centric characteristics of contemporary
IIoT systems. By retaining data locally on edge devices, FL
not only fulfills privacy and regulatory mandates but also
accommodates the inherent geographical distribution diversity,
allowing for more contextually relevant model development
without the need for centralized data aggregation. Additionally,
FL facilitates the deployment of robust deep learning models
across a distributed network without the necessity for centralized data collection, thus offering a holistic resolution to the
multifaceted challenges of network security in distributed IIoT.
Since its inception, research in FL has rapidly evolved,
with a significant focus on the security and robustness of
the learning process itself. For instance, to defend against
model poisoning attacks, Ma et al. [18] proposed ShieldFL, a
defense using homomorphic encryption to identify malicious
encrypted gradients, while Yazdinejad et al. [19] developed
a model with an internal auditor using statistical methods
for the same purpose. Other works focus on securing the
aggregation process; Jebreel et al. [20] presented fragmented
federated learning to reconcile accuracy with security by
mixing update fragments, and Eltaras et al. [21] introduced
an efficient protocol that is robust against user dropouts.
From an attack perspective, research has also revealed new
vulnerabilities, such as the External Gradient Inversion Attack
(EGIA) proposed by Liang et al. [22], which shows that external adversaries can reconstruct private data from intercepted
gradients.
While securing the FL process against such attacks is a
critical long-term goal, the practical application of FL to a
demanding domain like NID first requires overcoming more
foundational challenges that can prevent the model from
converging effectively. This has motivated a significant line
of work focused on making FL viable for NID in the first
place. For example, Mothukuri et al. [23] introduced an FL
approach for intrusion detection in IoT networks, Liu et al.
[24] combined FL with blockchain technology to develop an

9251

intrusion detection system for securing vehicular networks,
Sun et al. [25] proposed a hierarchical FL intrusion detection
system with transformer-based local models, and Ruzafa et al.
[26] evaluated the use of various differential privacy methods
in FL-based network intrusion detection.
Despite these pioneering efforts, the application of FLbased network intrusion detection in realistic (i.e., large-scale
and heterogeneous) IIoT environments still faces two main
challenges that hinder model performance:
1) Massive devices as clients with limited availability1 :
Though massive devices are interconnected in IIoT
networks, not all devices can maintain consistent active
states in each communication round due to resource constraints on access devices and communication overhead
costs on the server. This results in inconsistent selection
of clients over iterations, leading to divergent directions
during the model aggregation process, potentially causing the trapped in the sub-optimal global model.
2) Data heterogeneity: The data on each device is inherently heterogeneous. This stems from intrinsic factors,
such as different device types generating unique benign
traffic patterns, as well as external factors like diverse
attack distributions, where different devices are exposed
to various types of attacks. This overall heterogeneity
means the local data of any specific device does not
represent the global data distribution.
Most existing methods [23], [24], [25] have not explicitly
handled data heterogeneity or provided detailed insights into
the scale and quantity of participating clients for FL in
NID. While [26] addresses data heterogeneity, the application
scenario is primarily confined to small-scale clients scenario
(5 to 10 clients). There exists a pronounced research gap for an
FL-based framework capable of concurrently addressing these
challenges in the large-scale heterogeneous IIoT environment.
Motivated by this, in this paper, we propose an effective and
robust Federated Learning-based Industrial Network Intrusion
Detection (FedIn-NID) framework. We first propose a novel
client selection strategy that synergistically integrates multidimensional factors (including client availability, local dataset
distribution, and dataset size) to ensure efficient and balanced
client participation. By leveraging these factors, the approach
effectively evaluates the consistency of participating clients
and avoids the selection of biased clients with data concentrated in a few categories. Then, considering the heterogeneity
of attack data distributions, we introduce FedEMA, a dynamic
aggregation strategy that leverages the concept of Exponential
Moving Average (EMA) to dynamically update the global
model. This innovative approach harmoniously integrates both
previously learned global knowledge and newly acquired local
knowledge, consequently accelerating the convergence of the
global model and improving the performance of the detection
model. Our contributions are summarized as follows:
1) Comprehensive FedIn-NID Framework for IIoT Environments: We propose a FedIn-NID framework to
1 Limited availability means that not all devices can maintain consistent
active states in each communication round due to interruptions caused by
changes in device state, system quotas, and network connectivity [15], [27].

9252

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

address the comprehensive challenges in the realistic
IIoT environment characterized by heterogeneous data
distribution, inherent massive devices as clients, and
limited availability across devices. Additionally, we contribute a 1D-CNN model for efficient network intrusion
detection, enhancing the practicality and applicability of
our framework in real industrial settings.
2) Multidimensional Client Selection Strategy: We introduce a client selection strategy that synergistically
integrates multidimensional factors, including client
availability, local dataset distribution, and dataset size.
By leveraging a selection weight derived from these
factors, the strategy effectively mitigates the consistency
among participating clients and avoids the selection of
biased clients with data concentrated in a few categories,
ultimately enhancing the performance of FL in realistic
and dynamic IIoT scenarios.
3) Global Model Aggregation Strategy Using FedEMA: We
present a dynamic global model aggregation strategy,
termed FedEMA. This strategy employs the concept of
exponential moving average to dynamically balance the
holistic yet slightly older knowledge in the global model
with the partial yet relatively newer knowledge in local
models. Consequently, FedEMA achieves a harmonious
integration of knowledge acquired by the global model
and local models, accelerating the convergence of the
global model and improving the model performance.
Our experiments demonstrate that our proposed FedInNID achieves efficient detection of network intrusions amidst
the large-scale heterogeneous IIoT environment. Specifically,
FedIn-NID exhibits outstanding performance by 10% to 30%
over baselines. Compared to other methods, our approach
excels in detecting rare categories of attack instances, emphasizing its effectiveness in the heterogeneous data distribution
environment. Furthermore, our method exhibits significant
robustness in diverse heterogeneous data distribution settings
and varying client numbers, confirming its superior adaptability to the complexity of realistic IIoT environments.
The remainder of the paper is organized as follows:
Section II provides the system modeling. Section III describes
the proposed FedIn-NID framework, including the proposed
multidimensional client selection strategy, the designs of the
model structure, local training, and the FedEMA strategy.
Section IV presents the experimental setup and results. Finally,
we conclude the paper with a summary in Section V.
II. S YSTEM M ODEL
In this section, we illustrate the client model and network
intrusion model in the large-scale heterogeneous IIoT scenario.
A. Client Model
The large-scale heterogeneous IIoT environment is illustrated on the right side of Fig. 1. We denote a total of M
clients (devices) as C = {C1 , . . . , C M }. Each client Ci has a local
dataset˚ (collected
D i comprising Ni data pairs, defined as
 Ndata)
i
D i = xi, j , yi, j j=1
, where xi, j ∈ X ⊂ Rd represents a network
flow with d features, and yi, j ∈ Y ⊂ {0, 1, . . . , K − 1} denotes

the flow type, with the number of classes for network flows
(benign and other attack types) denoted by K. The distribution
of this data is naturally heterogeneous, influenced by both the
intrinsic characteristics of the client device (e.g., its function
and resulting benign traffic patterns) and its unique exposure
to different types of network attacks. Following [28] and [29],
we perform Dirichlet distribution for train to generate NonIID data partitions. Specifically, consider the data distribution
as follows:
π = [π0 , π1 , . . . , πK−1 ]T ,
(1)
where πk (k ∈ {0, 1, . . . , K − 1}) is the data distribution for M
clients at the kth class as follows:
M

πk ∼ Dir(πk |γk ) =

1 Y γk, j −1
πk, j ,
B(γk )

(2)

j=1



where πk = πk,1 , πk,2 , . . . , πk,M , and πk, j is the proportion
of the instances of the kth class for the jth client; γk =
[γk,1 , γk,2 , . . . , γk,M ]  0 is the parameter of the Dirichlet
distribution; B(γk ) is the multivariate beta function for normalization. Hence, π ∼ Dir(γ) denotes the data
T
 distribution across
=
M clients for K classes, where γ = γ0 , γ1 , . . . , γK−1
γ · 1K×M . For ease of presentation, we adopt Dir(γ) to denote
the Dirichlet distribution with the scalar hyper-parameter γ.
Then, we follow [30], [31] to model the availability of
clients in a heterogeneous IIoT environment. The availability
of clients are affected by their current conditions, basically
including their state of energy, communication costs for FL,
and computational costs for local training. To facilitate comparison among those factors, we project them to the range of
0 to 1 without loss of generality.
1) State of Energy (Oenergy,i ): The state of energy can be
estimated based on the current and maximum energy capacity
of the client, as outlined below:
Oenergy,i = e

−γ E

Ei
Max,i

,

(3)

where Ei is the remaining energy of client Ci , EMax,i denotes
it maximum energy capacity, and γ is the scaling factor.
2) Communication Cost (Ocomm,i ): In this paper, the communication cost is evaluated by the quality of transmission
(i.e., transmission rate) and can be modeled as:
rMin
Ocomm,i =
,
(4)
ri
where ri ∈ [rMin , rMax ] is the transmission rate. A higher rate
indicates lower communication cost for FL.
3) Computation Cost (Ocomp,i ): The computation cost is
based on the client’s available computational capability, such
as CPU or GPU performance per training task. The higher
the computational capability, the more efficiently the client
can handle tasks, resulting in a lower cost. The cost can be
computed as follows:
Ocomp,i =

PMax
Pi

(5)

where Pi ∈ [PMin , PMax ] is the computational power. Note that
rMin , rMax , PMin , PMax are evaluated from the bound of total
clients C.

MAO et al.: FedIn-NID: A FL FRAMEWORK FOR NID IN LARGE-SCALE HETEROGENEOUS INDUSTRIAL IoT

9253

Fig. 1. An overview of our proposed FedIn-NID framework in the large-scale heterogeneous industrial IoT environment.

To summarize, the total cost for client Ci can be calculated
as follows:
Oi = wT O,
(6)

T
where O = Oenergy,i , Ocomm,i , Ocomp,i is the cost vector for

T
client Ci , and w = wenergy , wcomm , wcomp is the corresponding
weight vector that indicate the importance of each cost, and
device availability for Ci is given by:
Ai =

1
1 + Oi

(7)

where higher weighed costs lead to lower device availability.
B. Network Intrusion Model
Each client Ci has a local multi-class NetFlow traffic classification model θi , and the goal is to collaboratively train
a good multi-class NetFlow traffic classification model θg
by leveraging the isolated local datasets for efficient NID.
NetFlow collects data about the IP traffic passing through
it. This data is aggregated into what are called “flows”. A
flow is typically defined by several key attributes, such as
source/destination IP address and port, network protocol, type
of service, etc. Based on NetFlow, the following attack types
are considered in this paper besides “benign” flows:
1) Scanning: An unusually high number of flows indicating
an attempt to discover accessible devices or services.
2) Cross-Site Scripting (XSS): Irregular flow patterns to
web servers, indicating injection of malicious scripts.
3) Distributed Denial of Service (DDoS) & Denial of Service (DoS): A surge in flow volume, targeting specific
destinations, overwhelming the network resources.
4) Password Attacks: Repeated flows to authentication services, suggesting brute-force attempts.
5) Injection: Unusual or unexpected flows to database
servers, attempting to exploit database vulnerabilities.

6) Backdoor: Anomalous flows to uncommon ports or destinations, indicating traffic to unauthorized entry points.
7) Man-In-The-Middle (MITM): Anomalies in flow data
that may suggest interception or alteration of traffic.
8) Ransomware: Abnormal flow patterns related to encryption or data exfiltration activities.
Given the pressing need to enhance NID accuracy while
concerning clients’ data privacy, there is a compelling case for
adopting an FL framework. To further address the comprehensive challenges in the realistic IIoT environment characterized
by heterogeneous data distribution and limited device availability, a FedIn-NID framework is proposed in Section III.
III. P ROPOSED F ED I N -NID F RAMEWORK
In this section, we introduce the proposed FedIn-NID framework. We first provide an overview of the framework. Then we
present the multidimensional client selection strategy, followed
by the proposed model structure design for network intrusion
detection, the descriptions of local training, and the proposed
FedEMA aggregation algorithm.

A. FedIn-NID Framework
Fig. 1 and Algorithm 1 provide the overview and procedure
of our designed FedIn-NID framework in investigated largescale heterogeneous IIoT environment. In the initialization
phase, the global model is used to initialize the local models of
1
all clients (step O).
In each communication round, client selection is performed to obtain a subset of clients for participating
2
in the current round (step O).
All participating clients undergo
3
local training (step O),
then upload the updated local models to
4
The server employs our proposed FedEMA
the server (step O).
5
to aggregate uploaded local models (step O),
resulting in a new
6
global model for the next communication round (step O).

9254

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Algorithm 1 FedIn-NID Framework

Algorithm 2 Multidimisional Client Selection at the t-Th
Communication Round

In addition to the aforementioned algorithmic procedure, the
framework includes the following pivotal parts: the proposed
client selection strategy, the proposed model design structure,
the local training method, and the proposed FedEMA global
aggregation algorithm. Each of these details will be introduced
in the following subsections.

learning in large-scale heterogeneous IIoT environments. This
becomes even more important when facing diverse network
attacks with varying intensities and extreme heterogeneity. To
this end, we introduce a novel client selection strategy in our
proposed FedIn-NID framework, as illustrated in Algorithm 2.
Firstly, for each client Ci and its local dataset D i , the client
derives the count Y i and distribution probability P i of attack
categories in D i as follows:

Yi,yi, j = Yi,yi, j + 1, for each xi, j , yi, j ∈ D i ,
(8)
Yi
P i = PK−1
,
(9)
k=0 Yi,k


where Yi,k ∈ Y i = Yi,0 , Yi,1 , . . . , Yi,K−1 ∈ NK is initialized
to 0 before counting attack categories, and P i =

Pi,0 , Pi,1 , . . . , Pi,K−1 ∈ RK . Hence, the local dataset distribution of client Ci can be quantified as follows:

B. Multidimisional Client Selection Strategy
In practice, the limited availability of the devices in the
IIoT environment restricts their consistent participation in each
round of FL, different from the devices in data centers. The
main discrepancy between end devices and data centers is their
availability [15], which is affected by the interruption due to
changes in device state and network connectivity. Hence, in
2
the communication round of FL (step O),
only a small subset
of all devices can participate.
In [17], an initial client selection strategy based on random
sampling is proposed. In this approach, a subset of clients
is randomly chosen to participate in each communication
round of federated learning. Due to its straightforward implementation, this random sampling method has been widely
adopted in subsequent works [32]. However, random selection
is trivial as it does not account for specific client availabilities.
Additionally, it fails to consider the variability and heterogeneity of local datasets among clients. Addressing these factors
is essential for the effectiveness and efficiency of federated

Hi = −

K−1
X


Pi,k log2 Pi,k +  ,

k=0
K−1
X

Gi = 1 −

(10)

2
Pi,k
,

(11)

k=0

Bi = Hi ∗ Gi =

K−1
X
k=0

!
Pi,k log2 Pi,k + 



MAO et al.: FedIn-NID: A FL FRAMEWORK FOR NID IN LARGE-SCALE HETEROGENEOUS INDUSTRIAL IoT

∗

K−1
X

9255

!
2
Pi,k
−1 ,

(12)

k=0

where  = 1e−8 is a small positive constant, Pi,k ∈ P i is the
probability distribution of class k for client Ci , Hi is the entropy
of P i , Gi is the Gini coefficient (also known as the Gini index)
of P i , a common metric used to measure the inequality of a
distribution [33]. A higher Gini coefficient indicates a greater
concentration of data within a few categories, signifying a
less balanced distribution. Bi is the distribution balance factor.
The combination of entropy and the Gini coefficient reflects
both the balance and uniformity of the data distribution. By
multiplying entropy and Gini coefficient, the balance of the
client’s dataset distribution is quantified. A higher Bi indicates
that the data distribution P i of client Ci is more uniform and
balanced, without being dominated by any particular category.
In addition to data distribution, the quantity of local dataset
D i in each client Ci also plays a crucial role in FL. Therefore,
we define the local dataset volume impact factor for each client
as follows:
|C| ∗ Ni
(13)
Ni = P|C| ,
i=1 Ni
where Ni = |D i | is the quantity of local dataset D i , and |C|
represents the total number of clients, M. The |C| term serves
to scale this factor by normalizing the client’s data contribution against the average data volume across all clients. This
ensures Ni is on a comparable numerical scale to the other
factors in (14). Hence, by synergistically considering these
multidimensional factors, which do not compromise the data
privacy of clients, we ultimately derive the selection weight
Ri for each client Ci by combining these factors. To allow for
tunable importance of each dimension while preserving the
multiplicative gating effect, we use an exponential weighting
scheme:
w
(14)
Ri = Ati A ∗ (Ni )wN ∗ (Bi )wB ,
˚
where Ri ∈ R = R1 , R2 , . . . , R|C| , and the non-negative
exponents (wA , wN , wB ) control the sensitivity of the total
score to each factor. A weight wk > 1 makes the selection criterion stricter by amplifying the influence of the
corresponding factor k. This intensifies penalties for clients
with suboptimal scores (e.g., in availability) and accentuates
differences in other dimensions by strongly rewarding high
scores and penalizing low ones (e.g., in data volume and
distribution). Conversely, a weight 0 < wk < 1 reduces the
influence factor k, leading to a more lenient selection by
narrowing disparities among clients. This formulation offers
flexibility in tuning the selection behavior to suit different
operational scenarios. By comprehensively considering client
availability, local dataset distribution, and the size of the local
dataset, the selection weights Ri can be used to optimize the
selection of participating clients in large-scale heterogeneous
IIoT environments. The details are as follows:
I = Index(R) = {1, 2, . . . , |C|}} ,

(15)

0
I = arg sort(R), where RI00 ≥ RI10 ≥ . . . ≥ RI|C|−1
,

(16)

0

where Index(·) is the indices function that maps an index to
each element in the set, and arg sort(·) is the index-sorting

Fig. 2. Structure of designed 1D-CNN for network intrusion detection. The
final linear layer outputs predictions for 10 classes, corresponding to one
benign class and the nine attack types detailed in Section IV-A.

function that returns the indices of the set sorted in descending
order. Therefore, the selected participating clients and their
corresponding indices are as follows:
˚
0
I select = I00 , I10 , . . . , Im−1
,
˚
0
0
0
C select = CI0 , CI1 , . . . , CIm−1 ,
(17)
where m = max (1, b|C| ∗ Fc) is the number of participating
clients, and F ∈ [0, 1] represents the client participation ratio.
C. Model Structure Design
In the continuation of our FedIn-NID framework, the
model structure is intricately designed to cater to the intricate
requirements of network intrusion detection within the IIoT
landscape. At its core, the model harnesses a deep neural network architecture optimized for extracting meaningful
representations from the network traffic data. To effectively
classify the attack types of NetFlow traffic for the NID task, we
introduce a dedicated 1-dimensional CNN (1D-CNN) model
structure tailored specifically for NID.
As depicted in Fig. 2, we employ a 1D-CNN as the feature
extractor for the NID task, with a fully connected layer serving
as the classification head to output the classification predictions. The designed network architecture primarily consists
of 1D convolutional layers, ReLU activation layers, maxpooling layers, and fully connected layers. More specifically,
we employ four 1D convolutional layers with a kernel size
of 3, no padding, and a stride of 1, with output dimensions
of 32, 64, 128, and 256, respectively. Each convolutional
layer is subsequently followed by a ReLU activation layer,
collectively constituting a convolutional module. Additionally,
following the initial two convolutional modules and the latter
two, we apply max-pooling and adaptive max-pooling to
downsample the convolutional results, respectively. Finally,
a fully connected layer is used as the classification head,
yielding classification logits as the output.
D. Local Training for NID
For each participating client Ci in the t-th communication
round, we conduct local training for NID on θti by minimizing
the loss as follows:
Ni K−1

1 XX
I(yi, j = k) log (ŷi, j )k ,
LCE xi, j , yi, j = −
Ni
j=1 k=0

ŷi, j = softmax f xi, j ; θti

(18)

9256

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

e f ( xi, j ;θi )
,
t
e( f ( xi, j ;θi ))k
t

=P
xi, j ; θti

(19)

k



where f
is the output of given network flow xi, j
through a NID model that is parameterized by θti , I(·) is the
indicator function, and (·)k denotes the kth element of (·).
E. Global Aggregation With FedEMA
During the global model aggregation at the server side, the
most widely employed aggregation method is FedAvg [17]:
θgt+1 =

n
X

N
Pn i

i=1

j=1 N j

θti ,

(20)

where θti is the local model of Ci at the t-th communication
round and θt+1
is the global model for the next round.
g
However, naively aggregating local models using FedAvg
makes it challenging to effectively adapt to the heterogeneous and dynamic NID environment in federated learning.
Furthermore, in the next-generation IIoT environments with
large-scale clients, traditional solutions for heterogeneous federated learning struggle to address the challenges posed by
massive clients combined with a low participation ratio. It
is difficult to strike an effective balance between the overall
global model and the local models acquired by a small
subset of participating clients. Consequently, straightforward
application of FedAvg can easily lead to the global model bias,
hindering the acquisition of genuinely valuable knowledge.
To address this, we propose a novel dynamic aggregation
strategy, termed FedEMA. By incorporating the concept of
Exponential Moving Average, FedEMA dynamically balances
the relatively older but holistic knowledge acquired by the
global model with the relatively newer but partial knowledge acquired by a small subset of participating clients.
This approach enables us to encompass both previously
learned global knowledge and newly acquired local knowledge. Specifically, we calculate the global model for the next
communication round using FedEMA as follows:
θt+1
= αθtg + (1 − α)
g

n
X
i=1

N
Pn i

θti ,
N
j
j=1

t+1 2

α = λe−β(1− T ) ,

(21)
(22)

where α is the exponential moving average factor, FedEMA
degenerates into FedAvg when α is 0 and retains the global
model from the previous round without any updates when α is
1; λ ∈ [0, 1] is the extremum control coefficient; β > 0 is the
control coefficient of the exponential moving average process;
T is the total number of communication round.
IV. E XPERIMENT AND R ESULTS
Given the requirements for data security and privacy in
the large-scale heterogeneous IIoT environment, effectively
conducting network intrusion detection under the premise of
privacy protection is crucial. Furthermore, the fluctuations
in device statuses, operating system quotas, and network
connections across a myriad of IIoT devices result in device
interruptions, leading to limited device availability. This makes

it exceedingly challenging for all devices to maintain a
consistent active state during each communication round. Consequently, the central server can only gather responses from a
small fraction of devices for updates, causing the global model
bias and deviating toward different subsets of devices during
the iterative training process, diminishing convergence speed
and model performance. To this end, we set a vast number of
clients within the federated learning scenario (ranging from
50 to 500), but with a low client participation ratio (10%),
to simulate the realistic IIoT environment. To demonstrate
the performance and robustness of our FedIn-NID in such
a realistic IIoT scenario, we conduct experiments on a real
IoT dataset and further evaluate our approach with elaborate
settings.
A. Dataset and Preprocessing
We employ NF-ToN-IoT-v2 [34] as the network intrusion
detection dataset, which is an IoT network dataset based
on NetFlow involving diverse attack categories, and its NetFlow records are generated using publicly available pcap
files from the ToN-IoT dataset. The dataset comprises a
total of 16,940,496 data flows, with 10,841,027 (63.99%)
attack instances and 6,099,469 (36.01%) benign instances.
Specifically, the attack categories consist of nine distinct types:
Scanning, XSS, DDoS, Password, DoS, Injection, Backdoor,
MITM, and Ransomware. Besides, each data flow is made up
of 43 NetFlow features.
We perform preprocessing for this dataset at the experimental setup stage. To begin with, we remove two features in the
dataset: IPV4 SRC ADDR and IPV4 DST ADDR. Subsequently, we perform label encoding to all remaining features
and drop the redundant data flows. Finally, we randomly split
60% of data flows as train and the rest of 40% as test,
followed by dataset normalization.
We conduct data partitions on train according to
Section II-A, Figs. 3, 4 and 5 illustrate the data distributions under varying Non-IID settings with Dir(γ) for diverse
numbers of clients. It is evident that as γ decreases from 0.5
to 0.2 and then to 0.1, the heterogeneity in data distribution
significantly intensifies. This strategy of partitioning a featurerich dataset across numerous, heterogeneously distributed, and
intermittently available clients (as detailed in Section IV-C)
allows us to effectively simulate the complex data and device
landscape of a real-world large-scale heterogeneous IIoT
environment.
B. Compared Methods
We compare our method against three methods, including:
1) FedAvg [17], which serves as a baseline for federated
learning;
2) FedProx [35], which incorporates a proximal term during local model training to prevent over-bias, becoming
the baseline for federated learning under Non-IID data
settings;
3) SCAFFOLD [32], which corrects the overall model
training direction using a control variable, standing as
a state-of-the-art for federated learning under Non-IID
data settings.

MAO et al.: FedIn-NID: A FL FRAMEWORK FOR NID IN LARGE-SCALE HETEROGENEOUS INDUSTRIAL IoT

9257

Fig. 3. Data distribution of each client under Non-IID setting with Dir(0.5). The color bar refers to the number of data samples. Each patch represents the
number of data samples for a specific class in a client. The horizontal axis denotes the client ID, and the vertical axis denotes the attack class ID.

Fig. 4. Data distribution of each client under Non-IID setting with Dir(0.2). The color bar refers to the number of data samples. Each patch represents the
number of data samples for a specific class in a client. The horizontal axis denotes the client ID, and the vertical axis denotes the attack class ID.

Fig. 5. Data distribution of each client under Non-IID setting with Dir(0.1). The color bar refers to the number of data samples. Each patch represents the
number of data samples for a specific class in a client. The horizontal axis denotes the client ID, and the vertical axis denotes the attack class ID.

To more accurately evaluate the performance of each
baseline in large-scale heterogeneous IIoT environments, we
employ a client selection strategy based on client availability
for these methods as follows:
I  = arg sort(At ), where AtI0 ≥ AtI1 ≥ . . . ≥ AtI|C|−1
, (23)

˚  


I select = I0 , I1 , . . . , Im−1 ,
˚

C select = CI0 , CI1 , . . . , CIm−1
,
(24)
n
o
where Ati ∈ At = At1 , At2 , . . . , At|C| is the device availability
for client Ci at the t-th communication round, and C select is the
selected clients for these baseline methods at this round.

C. Implementation Details
We employ Pytorch to conduct our experiment, utilizing
the Adam optimizer with an initial learning rate of 1e−3 .
The batch size is set to 1024. We train 50 communication
rounds (T ), with the client participation ratio (F) of 0.1, and
the local epoch (E) is set to 1. During the training stage,
we adopt AMP (Automatic mixed precision) to all methods.
Evaluations are conducted at an interval of 5 communication
rounds. For two hyper-parameters of FedEMA, we empirically
set the extremum control coefficient λ = 0.5 and the control
coefficient of the exponential moving average process β = 4.0
for all experiments. Furthermore, we set wA = wN = wB = 1

9258

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Fig. 6. Illustrate the quantitative results (average and standard deviation of 5 trials) on test in terms of accuracy.
TABLE I
Q UANTITATIVE R ESULTS (AVERAGE AND S TANDARD D EVIATION OF 5 T RIALS ) ON test IN T ERMS OF F1-S CORE U NDER D IR (0.5) S ETTING

to FedIn-NID. To reduce computational complexity, the availability of each client is sampled from a random distribution
in each communication round.
D. Evaluation Metrics
To evaluate the performance of network intrusion detection,
we employ widely-used metrics such as F1-score and accuracy
for the multi-class classification task. Furthermore, we utilize
the macro-average to calculate average values for the multiclass NID task.
1) F1-Score: This metric represents the harmonic average
of precision and recall, formulated as follows:
2 ∗ Precision ∗ Recall
F1 =
Precision + Recall
2 ∗ TP
.
(25)
=
2 ∗ TP + FN + FP
This metric provides a balanced measure of accuracy for
the NID task. We calculate the macro-F1 as follows:
K−1
1 X (k)
macro-F1 =
F1 ,
(26)
K
k=0

where K is the number of classes, and F1(k) denotes the F1score for the kth class.

2) Accuracy: The multi-class accuracy is given by:
PK−1 (k)
TP
Accuracy = PK−1 k=0
,
(k)
+ FN(k) )
k=0 (TP

(27)

where K is the number of classes, TP(k) and FN(k) denote the
true positive and false negative values for the kth class in the
confusion matrix, respectively.
E. Quantitative Results
Tables I, II, and III present the quantitative results of our
proposed FedIn-NID and other methods on NF-ToN-IoT-v2 in
terms of F1. The IMP column in the tables demonstrates the
improvement of the other methods over the traditional FedAvg.
Fig. 6, illustrates the quantitative results of our proposed
FedIn-NID and other methods on NF-ToN-IoT-v2 in terms
of Accuracy. Due to the diversification of NetFlow attack
types and the disparities in encountering different network
attacks, the NetFlow attack category classification datasets
often exhibit severe class imbalance. For instance, the benign
category constitutes the majority, while there are significant
numerical disparities among attack categories. Therefore, we
comprehensively evaluate performance employing the F1 and

MAO et al.: FedIn-NID: A FL FRAMEWORK FOR NID IN LARGE-SCALE HETEROGENEOUS INDUSTRIAL IoT

9259

TABLE II
Q UANTITATIVE R ESULTS (AVERAGE AND S TANDARD D EVIATION OF 5 T RIALS ) ON test IN T ERMS OF F1-S CORE U NDER D IR (0.2) S ETTING

TABLE III
Q UANTITATIVE R ESULTS (AVERAGE AND S TANDARD D EVIATION OF 5 T RIALS ) ON test IN T ERMS OF F1-S CORE U NDER D IR (0.1) S ETTING

Accuracy from fine-grained and coarse-grained perspectives,
respectively.
When interpreting the results, it is important to consider
the nature of the macro-average F1-score in the context of the
highly imbalanced NF-ToN-IoT-v2 dataset. The macro-average
F1-score computes the unweighted mean of per-class F1scores, giving equal importance to both populous classes (e.g.,
Benign) and extremely rare attack classes (e.g., Ransomware,
MITM). As shown in Tables I, II, and III, achieving a high
F1-score on these rare categories is exceptionally challenging,
with many baseline methods scoring 0.00. These low scores
from the minority classes significantly pull down the overall
macro-average value for all methods. The key strength of
FedIn-NID is its superior performance on these specific rare
classes, which demonstrates its enhanced robustness against
severe class imbalance and is the primary driver of its overall
performance gains. We analyze the experimental result from
two distinct perspectives as follows:
1) Evaluation on Data Distribution: It is evident that as
the heterogeneity of the datasets increases (i.e., as γ decreases
in Dir(γ)), the performance of all methods suffers degradation, further demonstrating the impact of heterogeneous data
on federated learning [15], [36]. Nevertheless, our FedInNID continues to demonstrate outstanding performance and
robustness, particularly in small-sample categories such as

Injection, Backdoor, and Ransomware, which become increasingly difficult for other methods to classify as dataset
heterogeneity increases. Significantly, FedAvg fails to classify
some small-sample categories under all settings, which is
primarily due to the fact that our FL scenario involves a
vast number of clients, but only a minuscule proportion of
clients participate in each communication round. The scenario
stands in stark contrast with the generic scenario of FedAvg
(with fewer clients and higher participation proportion), further
underscoring that FedAvg fails to meet the requirements of the
more complex and realistic IIoT environment characterized
by data heterogeneity, massive devices, and limited device
availability.
From the fine-grained perspective of F1, FedIn-NID outperforms FedAvg by approximately 8% to 30% under all γ
settings. For example, under the Dir(0.1) setting in Table III,
FedIn-NID achieves around 20% to 30% improvement over
FedAvg in macro-F1, demonstrating its robustness even in
extreme heterogeneity scenarios. This further demonstrates
that the multidimensional client selection strategy within the
FedIn-NID framework ensures efficient and balanced client
participation, thus effectively mitigating the heterogeneity in
attack data. Other methods, such as FedProx and SCAFFOLD,
struggle to maintain high performance as γ decreases, particularly in small-sample categories. The stability and robustness

9260

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Fig. 7. Convergence plots in terms of macro-F1 for FedIn-NID and baselines. Subplots represent varying total client counts (M) and data heterogeneity levels
controlled by the Dirichlet parameter (γ), where a lower γ indicates higher heterogeneity.

of FedIn-NID in classifying both frequent and rare categories
make it especially suitable for highly heterogeneous IIoT
environments.
From the coarse-grained perspective of Accuracy, FedInNID also outperforms other methods, with an average
improvement of around 5% to 20% across all γ settings. However, due to the dominance of benign categories, the Accuracy
improvements are less pronounced than the F1 improvements.
This highlights the need to evaluate performance using multiple metrics, especially in imbalanced classification tasks like
network intrusion detection.
2) Evaluation on the Total Number of Clients: With an
increase in the total number of clients, it is evident that all
methods undergo a performance decline. This is attributed to
the reduction in the number of training instances per client
as the number of total clients grows. When conducting local
training with fewer training samples, it becomes easier for
the model to overfit, leading to increased disparities among
models during global model aggregation, exacerbating model
drift. This is due to the reduction in training samples per
client, leading to overfitting during local training and increased
model drift during global aggregation. However, FedInNID consistently demonstrates superior performance across

different client numbers. For example, in the M = 500 setting,
FedIn-NID delivers a significant improvement over FedAvg,
achieving up to 22% higher macro-F1 under the Dir(0.5)
and Dir(0.2) settings, and maintaining a 23% improvement
even under the more challenging Dir(0.1) setting. This further
demonstrates that the FedEMA global model aggregation
strategy dynamically balances global model updates by using
an exponential moving average to reduce the bias introduced
by large-scale and highly diverse client models.
From the coarse-grained perspective of Accuracy, it can
be observed that when the total number of clients is relatively low, the performance of FedProx is inferior to FedAvg,
particularly under more heterogeneous settings like Dir(0.2)
and Dir(0.1). Conversely, with a relatively larger total number
of clients, FedProx shows performance improvement against
SCAFFOLD. This demonstrates that SCAFFOLD performs
worse under the more large-scale client environment. In contrast, FedIn-NID exhibits consistently stable and outstanding
performance across all client numbers and data distributions,
reinforcing its robustness and suitability for large-scale IIoT.
3) Convergence Analysis: To further illustrate the convergence dynamics and the impact of our proposed framework,
Fig. 7 presents the macro-F1 score of all methods over the

MAO et al.: FedIn-NID: A FL FRAMEWORK FOR NID IN LARGE-SCALE HETEROGENEOUS INDUSTRIAL IoT

50 communication rounds for each experimental setting. To
better visualize the underlying convergence trends, the solid
lines show the average performance smoothed with a Gaussian
filter [37] (with σ = 0.9), while the shaded regions represent
the standard deviation of the raw results across trials. The
convergence plots clearly show that FedIn-NID consistently
achieves a higher macro-F1 score throughout the training process compared to the baseline methods. It not only converges
to a superior final performance but also demonstrates a faster
convergence rate. This advantage is especially pronounced in
the more challenging settings with higher data heterogeneity
(i.e., lower γ) and a larger number of clients. This empirically
demonstrates that the proposed multidimensional client selection and FedEMA aggregation strategies work in synergy to
create a more stable and efficient training process, leading to
a more robust final global model.
In summary, the comprehensive experimental results, conducted under varying dataset distributions and client numbers,
consistently demonstrate the excellent performance and robustness of our proposed FedIn-NID framework. The framework
excels in handling heterogeneous, large-scale IIoT networks,
providing significant improvements over baselines across all
settings.
V. C ONCLUSION AND F UTURE W ORK
The advent of the next-generation Industrial IoT has intensified the demand for robust, scalable, and decentralized network
security mechanisms. This paper presented a novel FedInNID framework to effectively tackle the issues arising from
heterogeneous data distributions, large numbers of devices,
and varying device availability in realistic IIoT environments.
We introduced a novel multidimensional client selection strategy that integrates various factors to ensure efficient and
balanced client participation. This strategy effectively mitigates the attack data heterogeneity among participating clients
and accommodates the diverse availability of these clients.
Additionally, we proposed FedEMA, a dynamic global model
aggregation strategy to balance the global model and local
models, achieving a robust and efficient integration of knowledge. Extensive experiments demonstrated the effectiveness of
FedIn-NID, particularly its robust detection performance as
data distribution heterogeneity increases and the number of
devices grows, showcasing its superior overall performance
compared to existing solutions. In summary, FedIn-NID offers
a harmonious blend of scalability, adaptability, and robustness,
positioning it as a cornerstone for future research and development aimed at safeguarding the increasingly complex and
distributed world of next-generation IIoT.
To build upon this foundation, our future work will address
both the practical deployment challenges and the algorithmic
adaptability of the framework. It is important to note that
our current investigation focused on fundamental algorithmic
solutions within an idealized communication environment.
Therefore, our first direction for future work is to evaluate and
enhance the proposed method on standardized FL benchmark
platforms. This will allow us to analyze its performance
under realistic communication constraints and optimize its

9261

system-level efficiency for practical, production-level deployment. Our second direction is to enhance the framework’s
adaptability to novel threats by integrating incremental learning capabilities. This will empower individual clients to locally
learn emerging, previously unseen attack classes, with the
federated learning framework then efficiently propagating this
critical knowledge to the global model. These advancements
will ensure the system can adapt more quickly to the everevolving threat landscape of real-world IIoT systems.
R EFERENCES
[1]

A. Mahmood et al., “Industrial IoT in 5G-and-beyond networks: Vision,
architecture, and design trends,” IEEE Trans. Ind. Informat., vol. 18,
no. 6, pp. 4122–4137, Jun. 2022.
[2] Y. Wang et al., “MPCSM: Microservice placement for edge-cloud
collaborative smart manufacturing,” IEEE Trans. Ind. Informat., vol. 17,
no. 9, pp. 5898–5908, Sep. 2021.
[3] A. Khraisat, I. Gondal, P. Vamplew, and J. Kamruzzaman, “Survey
of intrusion detection systems: Techniques, datasets and challenges,”
Cybersecurity, vol. 2, no. 1, pp. 1–22, Dec. 2019.
[4] B. Mukherjee, L. T. Heberlein, and K. Levitt, “Network intrusion
detection,” IEEE Netw., vol. 8, no. 3, pp. 26–41, Mar. 1994.
[5] P. Garcı́a-Teodoro, J. Dı́az-Verdejo, G. Maciá-Fernández, and
E. Vázquez, “Anomaly-based network intrusion detection: Techniques,
systems and challenges,” Comput. Secur., vol. 28, nos. 1–2, pp. 18–28,
Feb. 2009.
[6] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 770–778.
[7] J. Gu et al., “Recent advances in convolutional neural networks,” Pattern
Recognit., vol. 77, pp. 354–377, Apr. 2017.
[8] Y. Yu, X. Si, C. Hu, and J. Zhang, “A review of recurrent neural
networks: LSTM cells and network architectures,” Neural Comput.,
vol. 31, no. 7, pp. 1235–1270, Jul. 2019.
[9] N. Shone, T. N. Ngoc, V. D. Phai, and Q. Shi, “A deep learning approach
to network intrusion detection,” IEEE Trans. Emerg. Topics Comput.
Intell., vol. 2, no. 1, pp. 41–50, Feb. 2018.
[10] W. Liang, K.-C. Li, J. Long, X. Kui, and A. Y. Zomaya, “An industrial
network intrusion detection algorithm based on multifeature data clustering optimization model,” IEEE Trans. Ind. Informat., vol. 16, no. 3,
pp. 2063–2071, Mar. 2020.
[11] Y. Lin, J. Wang, Y. Tu, L. Chen, and Z. Dou, “Time-related network
intrusion detection model: A deep learning method,” in Proc. IEEE
Global Commun. Conf. (GLOBECOM), Dec. 2019, pp. 1–6.
[12] H. He, X. Sun, H. He, G. Zhao, L. He, and J. Ren, “A novel multimodalsequential approach based on multi-view features for network intrusion
detection,” IEEE Access, vol. 7, pp. 183207–183221, 2019.
[13] B. Hu et al., “A deep one-class intrusion detection scheme in softwaredefined industrial networks,” IEEE Trans. Ind. Informat., vol. 18, no. 6,
pp. 4286–4296, Jun. 2022.
[14] G. Andresini, A. Appice, and D. Malerba, “Nearest cluster-based intrusion detection through convolutional neural networks,” Knowl.-Based
Syst., vol. 216, Mar. 2021, Art. no. 106798.
[15] P. Kairouz et al., “Advances and open problems in federated learning,”
Found. Trends Mach. Learn., vol. 14, nos. 1–2, pp. 1–210, 2021.
[16] Q. Yang, Y. Liu, T. Chen, and Y. Tong, “Federated machine learning:
Concept and applications,” ACM Trans. Intell. Syst. Technol., vol. 10,
no. 2, pp. 1–19, 2019.
[17] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. Y. Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” in Proc. 20th Int. Conf. Artif. Intell. Statist., 2017, pp. 1273–1282.
[18] Z. Ma, J. Ma, Y. Miao, Y. Li, and R. H. Deng, “ShieldFL: Mitigating
model poisoning attacks in privacy-preserving federated learning,” IEEE
Trans. Inf. Forensics Security, vol. 17, pp. 1639–1654, 2022.
[19] A. Yazdinejad, A. Dehghantanha, H. Karimipour, G. Srivastava, and
R. M. Parizi, “A robust privacy-preserving federated learning model
against model poisoning attacks,” IEEE Trans. Inf. Forensics Security,
vol. 19, pp. 6693–6708, 2024.
[20] N. M. Jebreel, J. Domingo-Ferrer, A. Blanco-Justicia, and D. Sánchez,
“Enhanced security and privacy via fragmented federated learning,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 5, pp. 6703–6717,
May 2024.

9262

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

[21] T. Eltaras, F. Sabry, W. Labda, K. Alzoubi, and Q. Ahmedeltaras,
“Efficient verifiable protocol for privacy-preserving aggregation in
federated learning,” IEEE Trans. Inf. Forensics Security, vol. 18,
pp. 2977–2990, 2023.
[22] H. Liang, Y. Li, C. Zhang, X. Liu, and L. Zhu, “EGIA: An external gradient inversion attack in federated learning,” IEEE Trans. Inf. Forensics
Security, vol. 18, pp. 4984–4995, 2023.
[23] V. Mothukuri, P. Khare, R. M. Parizi, S. Pouriyeh, A. Dehghantanha,
and G. Srivastava, “Federated-learning-based anomaly detection for IoT
security attacks,” IEEE Internet Things J., vol. 9, no. 4, pp. 2545–2554,
Feb. 2022.
[24] H. Liu et al., “Blockchain and federated learning for collaborative
intrusion detection in vehicular edge computing,” IEEE Trans. Veh.
Technol., vol. 70, no. 6, pp. 6073–6084, Jun. 2021.
[25] X. Sun et al., “A hierarchical federated learning-based intrusion detection system for 5G smart grids,” Electronics, vol. 11, no. 16, p. 2627,
Aug. 2022.
[26] P. Ruzafa-Alcázar et al., “Intrusion detection based on privacypreserving federated learning for the industrial IoT,” IEEE Trans. Ind.
Informat., vol. 19, no. 2, pp. 1145–1154, Feb. 2023.
[27] X. Gu, K. Huang, J. Zhang, and L. Huang, “Fast federated learning in
the presence of arbitrary device unavailability,” in Proc. Adv. Neural Inf.
Process. Syst., 2021, pp. 12052–12064.
[28] H. Wang, M. Yurochkin, Y. Sun, D. Papailiopoulos, and Y. Khazaeni,
“Federated learning with matched averaging,” in Proc. 8th Int. Conf.
Learn. Represent., 2020, pp. 1–16.
[29] J. Mao, Z. Wei, B. Li, R. Zhang, and L. Song, “Toward ever-evolution
network threats: A hierarchical federated class-incremental learning
approach for network intrusion detection in IIoT,” IEEE Internet Things
J., vol. 11, no. 18, pp. 29864–29877, Sep. 2024.
[30] B. Luo, X. Li, S. Wang, J. Huang, and L. Tassiulas, “Cost-effective
federated learning design,” in Proc. IEEE Conf. Comput. Commun., May
2021, pp. 1–10.
[31] P. M. Mammen, “Federated learning: Opportunities and challenges,”
2021, arXiv:2101.05428.
[32] S. P. Karimireddy, S. Kale, M. Mohri, S. J. Reddi, S. U. Stich,
and A. T. Suresh, “SCAFFOLD: Stochastic controlled averaging for
federated learning,” in Proc. 37th Int. Conf. Mach. Learn., 2019,
pp. 5132–5143.
[33] J. Franklin, “The elements of statistical learning: Data mining, inference
and prediction,” Math. Intelligencer, vol. 27, no. 2, pp. 83–85, Mar.
2005.
[34] M. Sarhan, S. Layeghy, and M. Portmann, “Towards a standard feature
set for network intrusion detection system datasets,” Mobile Netw. Appl.,
vol. 27, no. 1, pp. 357–370, Feb. 2022.
[35] T. Li, A. K. Sahu, M. Zaheer, M. Sanjabi, A. Talwalkar, and V. Smith,
“Federated optimization in heterogeneous networks,” in Proc. Mach.
Learn. Syst., 2018, pp. 1–22.
[36] Q. Li, Y. Diao, Q. Chen, and B. He, “Federated learning on non-IID
data silos: An experimental study,” in Proc. IEEE 38th Int. Conf. Data
Eng. (ICDE), May 2022, pp. 965–978.
[37] J.-S. Lee, “Digital image smoothing and the sigma filter,” Comput. Vis.,
Graph., Image Process., vol. 24, no. 2, pp. 255–269, Nov. 1983.

Jingxin Mao received the B.E. and M.E. degrees
from Tongji University, Shanghai, China, in 2022
and 2025, respectively. He is currently pursuing the
Ph.D. degree in intelligent transportation with The
Hong Kong University of Science and Technology
(Guangzhou). His current research interests include
federated learning, large language models, semisupervised learning, and incremental learning.

Zhiwei Wei received the master’s degree from
Tongji University, Shanghai, China, in 2023.
He is currently pursuing the Ph.D. degree with
Shanghai Research Institute for Intelligent
Autonomous Systems, Tongji University. His
research interests include vehicular fog computing,
industrial service provision, and dynamic resource
allocation.

Bing Li (Member, IEEE) received the Ph.D. degree
from Tongji University, Shanghai, China, in 2021.
She is currently an Assistant Professor with Tongji
University. Her current research interests include
UAV communications, wireless resource allocation,
and relay communications.

Rongqing Zhang (Member, IEEE) received the B.S.
and Ph.D. degrees (Hons.) from Peking University,
Beijing, China, in 2009 and 2014, respectively.
Currently, he is an Associate Professor at The
Hong Kong University of Science and Technology
(Guangzhou), Guangzhou, China. Before joining
HKUST(GZ), he held faculty positions at Tongji
University and Colorado State University. His
research interests include vehicular communications
and networking, low-altitude vehicular networks,
and connected intelligence. He has authored and
co-authored three monographs and over 200 papers in top journals and conferences, with three best paper awards at IEEE ICC 2016, GLOBECOM 2018,
and ICC 2019. He also received the 2017 First-Class Prize in Natural Science
of Ministry of Education of China, the 2023 First-Class Prize in Natural
Science of Chinese Association of Automation, and the 2023 First-Class
Prize in Natural Science of China Institute of Communications. He is also
serving as the Secretary General for the Connected Intelligence Committee
of Chinese Association of Automation, the Vice-Chair for the Information
Services Committee of IEEE ComSoc Asian–Pacific Board, and an Associate
Editor for IEEE T RANSACTIONS ON V EHICULAR T ECHNOLOGY and IET
Communications.

Lingyang Song (Fellow, IEEE) received the Ph.D.
degree from the University of York, U.K., in 2007.
He was a Research Fellow with the University
of Oslo, Norway, until rejoining Philips Research,
U.K., in March 2008. In May 2009, he joined the
Department of Electronics, School of Electronics
Engineering and Computer Science, Peking University, and is currently a Boya Distinguished Professor.
His research interests include wireless communication and networks, signal processing, and machine
learning. He was a recipient of the IEEE Leonard
G. Abraham Prize in 2016 and the IEEE Asia Pacific (AP) Young Researcher
Award in 2012. He has been an IEEE Distinguished Lecturer since 2015. He
received the K. M. Stott Prize for excellent research from the University of
York.
PAPER_TEXT
