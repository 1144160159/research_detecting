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
# [228] FedPot: A Quality-Aware Collaborative and Incentivized Honeypot-Based Detector for Smart Grid Networks
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
编号：228
题名：FedPot: A Quality-Aware Collaborative and Incentivized Honeypot-Based Detector for Smart Grid Networks
年份：2024
DOI：10.1109/tnsm.2024.3387710
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2024.3387710.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：IoT、车联网、工业互联网与边缘安全
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\228.txt
- 原始字符数：88010
- 本次发送字符数：88010
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
4844

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 4, AUGUST 2024

FedPot: A Quality-Aware Collaborative and
Incentivized Honeypot-Based Detector
for Smart Grid Networks
Abdullatif Albaseer , Member, IEEE, Nima Abdi , Mohamed Abdallah , Senior Member, IEEE,
Marwa Qaraqe , Senior Member, IEEE, and Saif Al-Kuwari , Senior Member, IEEE

Abstract—Honeypot technologies provide an effective defense
strategy for the Industrial Internet of Things (IIoT), particularly
in enhancing the Advanced Metering Infrastructure’s (AMI)
security by bolstering the network intrusion detection system.
For this security paradigm to be fully realized, it necessitates
the active participation of small-scale power suppliers (SPSs)
in implementing honeypots and engaging in collaborative data
sharing with traditional power retailers (TPRs). To motivate this
interaction, TPRs incentivize data sharing with tangible rewards.
However, without access to an SPS’s confidential data, it is
daunting for TPRs to validate shared data, thereby risking SPSs’
privacy and increasing sharing costs due to voluminous honeypot
logs. These challenges can be resolved by utilizing Federated
Learning (FL), a distributed machine learning (ML) technique
that allows for model training without data relocation. However,
the conventional FL algorithm lacks the requisite functionality
for both the security defense model and the rewards system of
the AMI network. This work presents two solutions: first, an
enhanced and cost-efficient FedAvg algorithm incorporating a
novel data quality measure, and second, FedPot, the development
of an effective security model with a fair incentives mechanism
under an FL architecture. Accordingly, SPSs are limited to
sharing the ML model they learn after efficiently measuring their
local data quality, whereas TPRs can verify the participants’
uploaded models and fairly compensate each participant for their
contributions through rewards. Moreover, the proposed scheme
addresses the problem of harmful participants who share subpar
models while claiming high-quality data through a two-step
verification approach. Simulation results, drawn from realistic
mircorgrid network log datasets, demonstrate that the proposed
solutions outperform state-of-the-art techniques by enhancing the
security model and guaranteeing fair reward distributions.
Index Terms—AMI, honeypot-based detector, security model,
machine learning, incentive mechanism, collaborative learning.

Manuscript received 30 October 2023; revised 10 February 2024 and 5
April 2024; accepted 6 April 2024. Date of publication 12 April 2024; date of
current version 21 August 2024. This publication was made possible by NPRP
Cluster project (NPRP-C) Twelve (12th) Cycle grant # NPRP12C-33905-SP67 from the Qatar National Research Fund (a member of Qatar Foundation).
Preliminary results in this work are presented at the IEEE CCNC Conference,
2023 [1] [DOI: 10.1109/CCNC51644.2023.10060393]. The associate editor
coordinating the review of this article and approving it for publication was
Y. D. Lin. (Corresponding author: Abdullatif Albaseer.)
The authors are with the Division of Information and Computing
Technology, College of Science and Engineering, Hamad Bin
Khalifa University, Doha, Qatar (e-mail: aalbaseer@hbku.edu.qa;
niab52126@hbku.edu.qa; moabdallah@hbku.edu.qa; mqaraqe@hbku.edu.qa;
smalkuwari@hbku.edu.qa).
Digital Object Identifier 10.1109/TNSM.2024.3387710

N OMENCLATURE
V (z )
Vm
V m (j )
η
Λ(xi , δ)

global model at z-th training round
local model of SPS m
the local model update at j local iteration
the learning rate
an open ball space with a radius of δ
centered at xi
Sz
the selection set at round z
the model and its rewards of type m
πm
θm
SPS type: θ1 ≤ . . . ≤ θm ≤ . . . ≤ θM
ϕ(Dm )
the estimation of the local VDD quality
ξ
the defense model size
Cd
the honeypot deploying cost
Cm
the local deployment, training, and uploading costs
Ct
the local training cost to update the defense
model
Cu
the uploading cost of the local defense
model
E
number of local training epochs
Fm (V m (j )) the local loss function at j local iteration
Fm (V m )
the updated local loss function
the revenue given by each SPS m
G(Vm )
M
number of connected SPSs
Rm
the reward given to SPS m
Szm
the selection binary variable
T max
the maximum latency in each round
Um
the utility of SPS m
UTPR
the utility of TPR (i.e., utility company)
Π
Incentive set for all types
Fi (V m , xi , yi ) loss function on sample i
AMI
Advanced Metering Infrastructure
CPU
Central Processing Unit
DDoS
Distributed Denial-of-Service
DL
Deep Learning
DoS
Denial-of-Service
FL
Federated Learning
GDPR
General Data Protection Regulation
IC
Incentive Compatibility
IID
Independent and Identically Distributed
IIoT
Industrial Internet of Things
IR
Individual Rationality
LDIC
Local Downward Incentive Compatibility
LUIC
Local Upward Incentive Compatibility

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1932-4537 
See https://www.ieee.org/publications/rights/index.html for more information.

ALBASEER et al.: FedPot: A QUALITY-AWARE COLLABORATIVE AND INCENTIVIZED HONEYPOT

MITM
ML
NIDS
PLCs
RTUs
SG
SPSs
TNR
TPRate
TPRs
VDD

Man-in-the-Middle
Machine Learning
Network Intrusion Detection System
Programmable Logic Controllers
Remote Terminal Units
Smart Grid
Small-Scale Power Suppliers
True Negative Rate
True Positive Rate
Traditional power retailers
Valid Defense Data
I. I NTRODUCTION

SMART Grid (SG) is an advanced electricity system that
leverages digital tech, IIoT, and networking to boost efficiency, reliability, and sustainability. It achieves this through
a cyber-physical system for the bidirectional flow of power
and information, automating supply-demand balance with realtime data [2]. SG allows individuals to become small-scale
power suppliers (SPSs) using renewable sources, reducing the
burden on traditional power retailers (TPRs) and fostering
advanced metering infrastructure (AMI) integration [3], [4].
However, integrating different network technologies to
interconnect SPSs and TPRs, which lack a proper defense
system, is raising concerns about the security and privacy
of SG systems. Adversaries have access to numerous vulnerabilities, including ways to launch destructive attacks and
access sensitive information such as a homeowner’s residential address, social security number, daily habits, and any
information related to unauthorized electricity consumption or
disruption in the network. As an example of such attacks, the
2015 Ukrainian power outage illustrates the critical vulnerabilities to cyber-attacks in both the control center and the smart
devices employed for managing and observing the electrical
system [5].
In addition, SG is subject to denial-of-service (DoS)
attacks, which can flood the network with traffic, causing delays in data transmission and processing. This can
lead to disruptions in the system’s normal operation and
potentially cause critical elements of the energy system to
fail [6]. To protect the communication infrastructure, implementing a Network Intrusion Detection System (NIDS) is
crucial. NIDS serves as a robust shield, detecting numerous
threats that extend beyond the capacity of traditional firewalls. The protective capability of NIDS has been notably
enhanced by the advent of Machine Learning (ML) and Deep
Learning (DL)-based approaches, pushing their performance
to a significantly higher level. This interconnected relationship
between NIDS, ML, and DL demonstrates a synergistic blend of network security and advanced computational
methodologies [7].
Building upon this security paradigm, incorporating honeypot technology further enriches the protective capabilities
of ML/DL-based NIDSs. Honeypots empower these systems
to meticulously map the attack surface, discern patterns, and
thwart malicious actions by delivering detailed insights into
potential intruder behavior. Within the realm of SG, a honeypot

A

4845

mimics the regular operations of a meter with the intent
to deceive, misdirect, and analyze the activities of potential
intruders. Employing such tactics allows SPSs to develop
independent, streamlined security measures. Furthermore, it
facilitates the exchange of defensive information with TPRs,
eliminating the need for TPRs to purchase costly security
models from security retailers. This approach amplifies the
protective layers of AMI, creating a more robust defense
mechanism. Simultaneously, it alleviates the financial strain
associated with defense strategies for TPRs, presenting a dual
advantage by strengthening network security while managing
costs effectively [8].
Significant effort in the literature has been devoted to
developing incentive mechanisms and designing contracts to
encourage SPSs to implement honeypots and share protective
information with TPRs while maintaining a balance such
that SPSs do not reap excessive benefits beyond their due.
For example, in [9], [10], the authors proposed information
asymmetry-based contract theory approaches considering different communication systems. Concentrating on the SG
network, the work in [11] introduced a recent motivationdriven approach where TPR motivates SPSs to deploy
honeypots and exchange defensive information to enhance
the security framework. This approach relies on a range of
essential prerequisites, including the dimensions of the shared
data and the related expenses. However, all the prior work
may violate the SPSs’ privacy while increasing the cost of
sharing the obtained raw data. The recent enforcement of
stringent data privacy regulations, such as the General Data
Protection Regulation (GDPR) [12], further underscores the
importance of maintaining data privacy. Additionally, the large
volume of honeypot logs can lead to excessive transmission
costs and network congestion. It is also worth noting that the
shared honeypot logs may not always yield benefits, as they
could contain redundant information that does not enhance
the existing protection strategy. Given the aforementioned
concerns, federated learning (FL) [13] has become an effective
distributed ML/DL method to maintain privacy and minimize
communication costs by exclusively sharing the ML model
while retaining the raw data in its original repository. This
seamlessly connects the need for privacy preservation and
cost-efficiency with the advantages of shared data for network
security. Current research on FL typically assumes that entities
are willing to participate in the FL training process and use
the collected data to improve the shared model [14], [15].
In reality, entities may be reluctant to join without properly
designed incentives (i.e., contracts) because FL consumes
significant resources (i.e., computation and communication
costs). Furthermore, entities in FL are autonomous actors who
decide when and how to interact. When dealing with different
reward strategies from different alliances, participants may use
different training techniques, influencing the performance of
the resulting models. To that end, it is critical to develop an
efficient reward mechanism to encourage entities to participate
in FL while maintaining the required level of data quality.
Researchers have recently presented several incentive schemes
aimed at compensating the involved parties (i.e., SPSs) using
financial incentives according to the magnitude of their data

4846

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 4, AUGUST 2024

contributions [16], [17], [18]. Utilizing current FL methodologies, all participants acquire the same model upon the end
of the training phase, regardless of the produced data quality
(i.e., honeypot logs) or the impact of the submitted local
models. Consequently, certain participants possessing large
datasets may provide inadequate contributions yet attain a
higher proficiency level than others who possess high-quality
data. This scenario gives rise to a challenging issue called the
FL free-rider problem.
A. Contribution
Considering the previously mentioned remarks, we introduce FedPot, an FL framework initially designed for SG
networks but validated across diverse scenarios, including
IEC 104 and N-BaIoT datasets. This architecture incorporates
refined, efficient, and resilient aggregation and averaging
techniques complemented by a fair rewards system based on
data quality. While our primary case study is centered on
SGs, our approach of combining honeypot logs and FL has
shown adaptability and effectiveness across multiple domains.
We introduce novel schemes for local data quality, participant
selection, and global model averaging, where the TPR resolves
a convex optimization problem that prioritizes data quality
over data size. Each SPS fine-tunes the global model received
from the TPR using its honeypot logs and transmits back the
model parameters. After that, the TPR combines and enhances
the defensive model employing the proposed approaches, as
detailed later. To overcome the FL free-rider problem within
AMI networks, we propose a novel metric to measure local
data quality and contributions instead of data size, which
may contain redundant information that does not improve the
security defense model. We devised a two-step verification
process to tackle malicious or poorly performing participants.
The TPR verifies submitted models, then updates the global
model and allocates incentives based on contribution. In
summary, the primary contributions of this work are:
• Develop an effective architecture for privacy-preserving
honeypot-based detectors, FedPot, that protects user privacy while considering data quality, an efficient global
model, and fair incentives. The proposed solution handles
and ensures a reliable FL training process based on valid
defense data acquired by implementing honeypots on the
SPS side.
• Formulate the problem as an optimization problem, then
provide solutions incorporating (i) problem reformulation
and transformation, (ii) the prior quality determination
of the local data through novel metrics, and (iii) two
schemes for reliable global averaging and contributionbased reward distributions.
• In response to the challenge of adversarial perturbations
in model uploads, we introduce a universally applicable
two-step verification system. This robust approach is
designed to ensure the integrity of model contributions.
• Carry out comprehensive simulations using realistic
log data from various datasets (i.e., N-BaIoT, IEC
104, and IEC MMS datasets). The results affirm
that our proposed framework outperforms existing

state-of-the-art
domains.

techniques

in

multiple

application

B. Organization
The remainder of the paper is structured as follows.
Section II briefly reviews the relevant literature on NIDSs
and honeypot deployment. The system models, including
the learning, cost, and reward, are presented in Section III.
The problem is formulated in Section IV, and the proposed
solution, including the problem reformulation and transformation, is presented in Section V. In Section VI, we discuss
the experimental setup and present the numerical results.
Finally, Section VII concludes this paper and suggests possible
directions for further research.
II. R ELATED W ORK
With the proliferation of microgrids, major concerns about
cyberattacks on such systems via smart meters have arisen.
The United States Department of Homeland Security reported
224 destructive cyber intrusions against local electric utilities
between 2013 and 2014 [19].
A. AMI Security
Security concerns have been intensively investigated in the
past few years as a key component of the IIoT. Authors in [20]
studied the security approach to mitigate cyber-attacks in the
context of the IIoT. The main assumption was that the attackers
have sufficient tools to identify advanced vulnerabilities that
enable them to attack IIoT systems. In [21], Li et al. used
consortium blockchain technology to overcome transaction
constraints in the IIoT. However, fewer studies have been conducted on the security of various components of AMI systems.
The work in [22] introduced a security protocol that preserves
AMI private information while securely delivering control
packets at the exact time. In [23], Fasial et al. investigated
the feasibility of employing data stream mining to improve
AMI cybersecurity via NIDS. Yan et al. [24] describe an SG
AMI security framework where different security concerns
associated with AMI deployment are considered.
B. ML/DL-Based and FL-Based NIDSs
Many ML algorithms have been utilized to boost the
NIDS in the past years to understand complicated network
traffic better [25], [26], [27]. ML/DL-based NIDSs are used
to identify unknown intrusions by analyzing the statistical
characteristics of the network traffic. However, DL-based solutions have shown better performance, especially in extracting
knowledge from complicated features rather than the shallow
features in ML-based detectors [25], [26], [27]. Recently, FL
has been increasingly employed in the realm of NIDSs
for the collaborative design of ML and DL-based detectors [28]. Specifically, the work presented in [29] developed
a cooperative detector capable of identifying zero-day botnet
attacks in oT networks using FL. Extending FL’s utility to
energy systems, [30] introduced a privacy-preserving and
communication-efficient FL-based energy predictor for netmetering systems. This approach combines a hybrid DL

ALBASEER et al.: FedPot: A QUALITY-AWARE COLLABORATIVE AND INCENTIVIZED HONEYPOT

Fig. 1. Micro-grid system where M SPSs deploy honeypot and transfer
security model with a single TPR.

model for high-accuracy energy forecasting with an InnerProduct Functional Encryption scheme to encrypt local model
parameters, maintaining data privacy.
C. Honeypot Deployment Based Incentive Mechanisms
Honeypots are practical security tools that deceive cyber
attackers by acting as vulnerability traps [31]. It has been
widely used to enhance defensive performance on different
systems [8], [32]. Tian et al. [32] developed a honeypot system
to defend against APT attacks in the SG, mainly in the bus
nodes. In their system, low-interaction and high-interaction
honeypots were applied. Similarly, Wang et al. [33] proposed a
honeypot scheme with various mixed distributions to detect the
AMI network traffic. However, Wang et al. failed to consider
how using a honeypot system could reduce TPR defensive
pressure while increasing AMI defensive effectiveness. Using
a honeypot, Liu et al. [8] captured distributed denial of
service attacks (DDoS) attacks in AMI. The implemented
methodology uses incomplete information static game and
honeypot deployment to investigate non-cooperative problems.
Householders, for example, install small wind turbines for
small enterprises to sell excess electricity and get a profit
from utility companies [3]. The work in [11] proposed a game
theory-based approach to designing an incentive mechanism
that allows SPSs to share their defense data with TPRs; thus,
the TPR can pay the rewards accordingly.
To summarize, significant effort has been made in the
literature to overcome the challenge of deploying the honeypot
and exchanging the obtained defensive data in AMI. However,
most of these studies focused on log size and overlooked
data redundancy that may be received from multiple SPSs.
Furthermore, the privacy of the SPSs was completely ignored,
posing an undesirable privacy risk to target consumers. Finally,
there are additional costs associated with uploading large
logs. Thus, in this paper, we propose FedPot. This efficient
framework not only focuses on all these challenges but also
solves advanced issues associated with malicious SPSs and
ensures a more reliable defense model.
III. S YSTEM M ODEL
This paper considers singular TPR within an AMI network,
which gathers defensive data from M interconnected SPSs, as
depicted in Fig. 1. In our microgrid system, SPSs can acquire
defense data by implementing and deploying honeypots. This
includes mimicking real and different services (i.e., IEC 104
and GOOSE), applications, and typical vulnerabilities. The

4847

honeypot remains an attractive target while collecting diverse
attack patterns to evolve with the changing landscape of
threats. In this work, we consider two types of traffic captured
by honeypots: fake traffic, which enables us to understand
attacker tactics without data centralization, and legitimate
traffic, which provides valuable insights into user behavior
patterns processed in a decentralized manner to maintain
privacy. To foster a diverse range of defense data, TPR may
provide incentives to stimulate SPSs to establish honeypots,
gather cyber-attack intelligence, encapsulate the defensive
data, and transmit it to the TPR.
Though SPSs can exchange defense data in the AMI
network, there is an information imbalance between the TPR
and SPS. This discrepancy arises because the SPS knows its
valid defense data (VDD) while the TPR is not. The VDD
includes the undisclosed attack event logs gathered by honeypots and used by the currently deployed TPR defensive system
to improve the existing architecture. Practically, the honeypot
logs amassed are extensive and could include users’ sensitive
information, leading to concerns surrounding computation and
communication costs and potential privacy violations. FL can
mitigate these issues by utilizing ML algorithms to extract
knowledge from the local VDD of each SPS and share only
the model attributes with the TPR. Nevertheless, traditional
FL Integration algorithms and incentive techniques are not
ideally suited for the security defense framework within the
AMI network. As a result, we introduce a privacy-preserving
framework for effective honeypot-based detection. Our objective is to develop a method that promotes effective assurance
of local model quality and provides incentives to bolster the
defense system of the AMI network. We presume the SPSs
hold M distinct data types that are separately distributed.
Let θ1 ≤ . . . ≤ θm ≤ . . . ≤ θM denote the VDD type for
each SPS, with a higher type signifying superior quality. To
conduct FL model training, the TPR must ensure the desired
quality at every global training round by devising an incentive
set (i.e., contract) Π = {πm = (V m , Rm )|m ∈ {1, . . . , M }},
which establishes the relationship between rewards and local
model quality based on the type, where V m denotes the
local model attributes of m VDD type and Rm represents
the incentives provided by the TPR. For participant selection,
the TPR needs initial information such as how many SPSs
are available to participate in defense model training, effort
duration, declared data quality, and associated costs. To guarantee an efficient training procedure, the TPR imposes a time
constraint for every global round z, beyond which the model
modifying and transferring must be finalized. The chosen SPSs
employ their VDD to refine the global model and subsequently
transfer the upgraded model to the TPR. According to [14],
the local model is formulated as follows:
V m (j ) = V m (j − 1) − η∇Fm (V m (j )),

(1)

where j = 1, 2, . . . , E Dbm represents the index of local update
for batch b and the epoch count E, and
Fm (V m ) 

1 
F i V m , x i , yi ,
Dm
i∈Dm

(2)

4848

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 4, AUGUST 2024

denotes the local loss function, quantifying the model’s error
concerning local data samples, Dm signifies the quantity of
data examples in the gathered records (i.e., traffic logs), and η
stands for the learning rate. Upon completion of local training
by all chosen SPSs, their updates are transmitted to the TPR.
Then, the TPR consolidates these updates and modifies the
global model given by:
V (z) =

M

Dm
m=1

D

V m,

(3)

M
where D =
m=1 Dm , represents the aggregate samples
across all SPSs. Moreover, to guarantee that the attained
accuracy is generalized, the TPR evaluates the uploaded
models and provides incentives only to SPSs exceeding the
threshold, ψm , as determined by the quality assessment
algorithm discussed subsequently. SPSs that pass the quality
evaluation receive rewards. The TPR iterates this procedure
for Z global iterations until the shared security model reaches
the target accuracy level. In this paper, we highlight that the
incentive set is constructed every global round, where the TPR
aims to sustain the desired accuracy while allowing for a slight
increment in succeeding rounds.
A. Participation Willingness
In addition to the cost of deploying the honeypot, the
suppliers bear the cost of training and uploading the local
models. This cost includes the time and energy consumption
for the honeypot deployment as well as training and uploading
their local models. As such, the TPR cannot serve all existing
devices due to insufficient bandwidth sub-channels. Thus, in
every FL round, just a subset of the participants Sz can send
their updates. The chosen set is described as follows:
Sz = {m | Szm = 1, m = 1, 2, . . . , M },

(4)

where Szm = 1 denotes that device m is in the selected set Sz ,
otherwise Szm = 0. The latency among the chosen set consists

of two parts: uploading latency and computing latency. For
the uploading latency, all devices have the same defense
model structure determined by TPR, with a size v z denoted
by ξ. Generally, we consider that the orthogonal frequency
division multiple access (OFDMA) scheme is used for the
communication between the BS and the devices, where each
m-th device is given bandwidth of size λm
z B . Additionally,
based on the size of the model, the system bandwidth is split
into N sub-channels given by: N = Bξ , where each participant
is assigned an 1-th sub-channel of size λm
z B . As a result,
z =
the m-th device is capable of achieving a data rate of αm
m
m
2
Pz |hz |
λm
), where hzm represents the channel gain
z B ln (1 +
N0
between the BS and client m, while Pzm denotes the transmit
power of the m-th client, and N0 denotes background noise
(i.e., Additive White Gaussian Noise (AWGN)). Hence, the
trans = ξ , · and the related
uploading latency is given by: Tm
αzm
trans p trans , where
transmission cost is defined as: Cu = Tm
m
trans
is the transmit power. Regarding the calculated latency,
pm
m
=
every device requires a time duration defined as: Tcmp
φm D m
E fm , to train its local model, where φm (cycles/sample)

denotes the number of processing cycles to execute one
sample, and fm (cycles/second) is the central processing unit
(CPU) frequency. Accordingly, the training cost is defined as:
m , where κ
Ct = κ̂m fm3 Tcmp
m is the capacitor’s coefficient
related to the chip. As a result, the combined latency for
computation and uploading for each m-th participant during
m
m
m . In a
= Ttrans
+ Tcmp
the z-th round is expressed as: Ttotal
real FL scenario, the coordinating server (i.e., TPR) establishes
a time constraint, i.e., round deadline constraint, ensuring
that every SPS participant completes their tasks within this
specified timeframe. Specifically, this time can be identified
based on the latency of the slowest chosen SPS m ∈ Sz , which
is defined as:
 m
m 
}.
(5)
+ Tcmp
T max = max{Szm Ttrans
It is worth emphasizing that while SPSs do benefit from the
globally trained model, this alone does not ensure a model
tailored to their unique threat landscape. Incentives encourage
SPSs to actively contribute quality data, keeping the model
updated and effective against evolving cybersecurity threats,
leading to solving the free-rider problem in FL. Incentives
also offset the operational costs of maintaining honeypots and
promote diverse participation. This results in a more robust and
tailored global model, rewarding contributors with a system
better suited to their security needs.
B. SPS and TPR Utilities
To calculate the SPS utility, which involves implementing
the honeypot and exchanging information associated with the
VDD data (i.e., the updated local model), we initially have to
compute the total incurred cost in the following manner:
Cm = Cd + C t + C u ,

(6)

where Cd represents the cost related to running the honeypot,
Ct is the cost related to updating the local model utilizing the
gathered logs, and Cu is the cost related to uploading the local
update. Accordingly, the utility of each SPS is expressed as:
Um = ln(θm Rm ) − Cm .

(7)

Equ. (7) implies that while the reward increases, the utility
does not increase at the same rate due to the diminishing
returns property of the logarithmic function. Once all SPSs
taking part in the updating and uploading of the global defense
model finish their tasks, the utility of the TPR is computed as
follows:
UTPR =

M


(θm G(Vm ) − Rm ),

(8)

m=1

where G(Vm ) represents the revenue obtained from each
SPS’s update. Specifically, each SPS shares its model, Vm ,
which will add a profit, G(Vm ) to TPR with associated costs.
C. Adversarial Model and Assumption
In this research paper, we analyze two stages of adversarial
behavior using the N-BaIoT dataset. The first stage involves
deploying botnets to carry out DDoS attacks by introducing

ALBASEER et al.: FedPot: A QUALITY-AWARE COLLABORATIVE AND INCENTIVIZED HONEYPOT

networked zombies into the SPSs. The SPS implements a
honeypot system to counter these threats, collect valuable
information about the attack surface, and document all activities. These logs are then integrated into a collaborative model
training approach, enabling information exchange with the
TPR and enhancing understanding of the attacker’s behavior.
The second stage of adversarial conduct occurs during the
FL process when a malicious SPS falsely claims superior
local data quality while contributing subpar updates to the
model. To develop a secure and efficient FL process that can
mitigate such issues, we put forward two distinct aggregation
and averaging techniques. These methods will be discussed in
greater detail later in the paper, providing insight into their
practical applications and advantages.

in which the retailer can redesign the contracts every round.
The problem is reformulated as:
P2.

The TPR aims to optimize data quality to boost the
performance of the target model and assures fair incentives to
all participating SPSs. This is equivalent to the optimization
problem given by:

Π

M
Z


z =1 m=1

Szm (θm G(Vm ) − Rm )

(9)

such that
C 1: ln(θm Rm ) − Cm ≥ 0, ∀m ∈ {1, 2, . . . , M }, (10)


m
,
C 2: ln(θm Rm ) − Cm ≥ θm Rm  − Cm
∀m  = m, m, m  ∈ {1, . . . , M },
M
Z 

C 3:
Rm ≤ B ,
C 4:

z =1 m=1
total
Tm
< T max ,

C 5: Rm > 0,


∀m ∈ {1, 2, . . . , M },

Π

M


Szm (θm G(Vm ) − Rm )

(11)
(12)
(13)
(14)

m is the cost of the supplier in type m, selecting
where Cm
a contract of type m  , and B is the allocated total budget
for upgrading the security defense model. In (9), C1 is the
individual rationality (IR) constraint in which each supplier
has to gain non-negative utility. Constraint C2 is incentive
compatibility (IC), in which each supplier should choose
the exact incentive aligned with its type. In C3, the retailer
guarantees that the rewards delivered to the participants do not
surpass the allocated budget. The delay constraint given by
C4 ensures that participants complete the assigned tasks in a
defined period. In C5, each participating SPS should receive
non-negative rewards. It is worth noting that the TPR can pay
for the model upgrade from the security market if the required
rewards are high and exceed its allocated budget.
Finding the direct solution for (9) is extremely intricate
due to the need for previous knowledge of all participants
over all rounds, which is nearly unattainable. Additionally, the
contracts must be adjusted based on the SPSs’ participation
over the training period since contributions decrease over time,
and the model may converge to various stationary points,
resulting in slower convergence. To address these challenges,
we propose to transform the problem into an online problem

(15)

m=1

C 1: ln(θm Rm ) − Cm ≥ 0, ∀m ∈ {1, . . . , M },
C 2:

m
ln(θm Rm ) − Cm ≥ ln(θm Rm  ) − Cm
,



∀m = m, m, m ∈ {1, . . . , M },
M

C 3:
Rm ≤ B z ,
m=1
total
Tm
< T max

∀m ∈ {1, 2, . . . , M },

C 5: Rm > 0,

IV. P ROBLEM F ORMULATION

max :

max :

such that

C 4:

P1.

4849

(16)
(17)
(18)
(19)
(20)

where Bz is the budget allocated for round z. For example,
Bz = B
Z , if we aim to allocate a fixed budget in each round,
it can be adjusted depending on the TPR’s gain.
Clearly, (15) is intractable, and the constraints are coupled.
In particular, constraint C1 in (15) related to IR and M(M − 1)
constraints related to IC make finding a direct solution for (15)
very challenging. Thus, we start by reducing the IR and
IC constraints. Then, we propose FedPot, a framework that
includes tractable solutions to these challenges. FedPot is
divided into two blocks, one on the SPS side and one on
the TPR side. On the TPR side, we initially use the local
data quality to ensure maximum utility for the TPR. Then we
relax the problem to enable the TPR to select the optimal
participating SPS. Next, we propose two averaging schemes
considering the security aspects. To ensure fair incentives, we
also proposed two reward schemes based on the claimed data
quality and the contribution to the global model.
V. P ROPOSED S OLUTION
This section introduces the proposed solutions, including
how we reduced the constraints’ complexity, the prior quality
determination of the local VDD, the trusted and untrusted
model averaging schemes, and the rewards distribution. The
proposed solution for the SPS side starts by deploying a
honeypot on the SPS side to record all network traffic into
log files. The logs are then transformed into a readable
format (i.e., CSV) and cleaned with an extensive preprocessing
step. It is worth mentioning that the practice of anonymizing
data (i.e., CSV files) is a commonly used method to protect
sensitive information. However, several factors motivate us to
use FL rather than simply anonymizing the data. First, FL
mitigates the risk of data re-identification, a vulnerability in
anonymization. Second, unlike anonymized CSV files, FL only
shares aggregated model parameters, preserving data patterns
while reducing exposure risks. Third, FL minimizes the chance
of large-scale breaches by avoiding centralized data storage.
Lastly, FL enables collaborative learning across distributed
honeypots without centralization, reducing communication and
storage costs. We propose a local evaluation scheme in which
each SPS evaluates its local VDD to determine whether
to participate in the FL learning process. It is important

4850

Fig. 2.

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 4, AUGUST 2024

FedPot Architecture.

to mention that the SPS is willing to participate only if
the required quality is achieved. Fig. 2 illustrates the whole
procedure performed at both the SPS and TPR.
A. Constraints Complexity Reduction
As stated previously, it is almost intractable to directly
solve (15). To simplify, we present the subsequent lemmas.
Lemma 1: Given the budget for each round Bz , for any
feasible contract (V m , Rm ), Rm ≥ Rm  ⇐⇒ m ≥ m 
∀ m, m  ∈ {1, 2, . . . , M }.
Proof: We first prove that if θm ≥ θm  where m ≥ m  ,
then Rm ≥ Rm  . Adding the IC constraints for both types θm
and θm  , yields:
ln(θm Rm ) − Cm ≥ ln(θm Rm  ) − Cm  ,

(21)

ln(θm  Rm  ) − Cm  ≥ ln(θm  Rm ) − Cm ,

(22)

and

We add both (21) and (22), we have:
ln(θm − θm  )(Rm − Rm  ) ≥ 0.

(23)

Thus, Rm ≥ Rm  .
From Lemma 1, we note that more rewards will be given
to more participants. This means that Lemma 1 is monotonic.

Hence, this analysis of IC constraints reduces the IR constraints as indicated in the following lemma.
Lemma 2: Given the Bz , and Lemma 1 related to IC
constraints and the sorted participants based on their data
quality, the IR condition can be reduced as:
ln(θ1 R1 ) − C1 ≥ 0

(24)

Proof: Given the sorted SPSs based on their types as defined
in Section III, the IC constraints are used as follows:
ln(θm Rm )−Cm ≥ ln(θm R1 ) − C1 ≥ ln(θ1 R1 ) − C1 ≥ 0.

(25)

From Section V-A, we note that if the first SPS’s type meets
the IR constraint, all other SPSs’ types will automatically meet
other IR constraints. Therefore, the IR of type 1 is sufficient
to achieve all other IR constraints.
According to Lemma 1, Lemma 2, we can transform the IC
constraint into local downward incentive compatibility (LDIC)
as follows [34]:
ln(θm Rm ) − Cm ≥ ln(θm Rm−1 ) − Cm−1 ,
∀n ∈ {2, 3, . . . , M },

(26)

and local upward incentive compatibility (LUIC) as follows:
ln(θm Rm ) − Cm ≤ ln(θm Rm+1 ) − Cm+1 ,
∀n ∈ {1, 2, . . . , M − 1}.

(27)

ALBASEER et al.: FedPot: A QUALITY-AWARE COLLABORATIVE AND INCENTIVIZED HONEYPOT

4851

From Equations (26), (27), we note that participants should be
given rewards based solely on their contributions. Moreover,
we observe that the objective function in (15) is decreasing
w.r.t Rm and increasing w.r.t G(Vm ).
B. Quality Measure of the SPSs’ VDD
The SPSs asymmetrically exchange information, sharing
only the local model updated using the collected VDD with the
TPR, rather than the VDD itself. Hence, the TPR is necessary
to validate the uploaded models. The quality of the local model
depends on several factors, including the variety of the data,
the number of contained classes, and the number of updates
performed. In this regard, we first model the SPS’s data by
considering the data quality, and , then by assessing the impact
of the local models on the generalization of the global model.
This strategy allows the TPR to guarantee a robust model even
in the presence of malicious participants. Each local dataset
Dm generally comprises traffic data with input-output pairs of
(m) (m) m
(m)
d
{xi,d , yi }D
i=1 , where xi,d ∈ R denotes the input holding
(m)

d attributes, and yi
∈ R denotes the matching class label.
Given that every SPS has its own network traffic patterns and
a varying response according to its activity, the honeypot logs
produce data of various sizes and follow a non-identical and
independently distributed (non-i.i.d.) manner. Furthermore, the
logs in each SPS may have distinct attack types, and some
of the SPSs might not have any malicious samples. Let D =
{D1 ∪ D2 ∪ . . . , ∪ DM } represent the aggregated dataset from
all SPSs. We define the probability of a sample, i, being
included in the local logs as:

1 : i ∈ Dm
.
(28)
ρ(Dm |i ) =
0 : otherwise
Definition 1 (δ-Data Coverage): With a predetermined
radius, the coverage of data collection through sampling is
obtained by:
ρ(Dm , δ) = D ∩ ∪xi ∈Dm Λ(xi , δ),

(29)

where Λ(xi , δ) is an open ball space with a radius of δ centered
at xi .
Considering the data space among all SPSs is an √
Euclidean
space, the range of δ is confined to the interval [0, d ].
Definition 2 (VDD Quality): ϕ(Dm ) gives the estimation
of the local VDD quality measurements defined as:
√

d
1
ρ(Dm , δ) dδ
(30)
ϕ(Dm ) = √
d 0
Remark 1: The value of ϕ(Dm ) can indicate the quality of
the local VDD. A more increased value of ϕ(Dm ) implies
improved data diversity, resulting in a better quality of the
locally updated model. This is because greater spaces between
traffic samples grasp more patterns during model training,
enhancing the overall generalization of the global model. Let
φ = ϕ1 , . . . , ϕM be the quality set of all SPS with M types,
m
and all SPSs with ϕ(Dm ) ∈ [ m−1
M , M ] hold a data of type m.
To solve Equation (15), the TPR can leverage each participant’s previous performance, which might be time-consuming
since assessing all upgraded models is a post-processing

Fig. 3.

Schematic illustrating how the luring score can be determined.

action. As a result, the quantity of ϕ(Dm ) can be utilized to
measure local VDD quality before a given SPS is selected.
This approach allows the TPR to select high-quality data and
avoid using models from participants with low-quality data,
which can negatively impact the global model’s performance.
By employing this technique, the TPR can ensure that the final
model is robust, even in the presence of malicious participants.
We can substitute πm = (V m , Rm ) in Section III by
πm = (Ω, Rm ). Accordingly, we can further reformulate the
optimization problem in (15) as follows:
P3.

max :
Π

M


Szm ϕ(Dm )

(31)

m=1

such that
(32)
C 1: ln(θ1 R1 ) − C1 ≥ 0,
C 2: ln(θm Rm ) − Cm ≥ ln(θm Rm−1 ) − Cm−1 , ∀m, (33)
C 3: ln(θm Rm ) − Cm ≤ ln(θm Rm ) − Cm+1 , ∀m,
C 4:

M


Rm ≤ B z ,
m=1
total
Tm
≤ T max

C 5:
C 6: Rm > 0.

(34)
(35)

∀m ∈ {1, 2, . . . , M },

(36)
(37)

It is worth mentioning that the optimization problem (P3)
considers the lure score to adaptively place honeypots in
the network to maximize their luring potential. As in our
proposed approach, the lure score can be calculated based
on various factors such as network traffic patterns, historical
attack vectors, and even machine learning models trained for
this specific purpose. Fig. 3 illustrates how the luring score
can be determined. The system ensures that honeypots are
effectively deployed by considering the lure score, which will
most likely capture meaningful data and contribute to better
FL. Specifically, high-quality data, signifying that the user’s
honeypot has successfully deceived the attackers, is defined by
a luring score. This leads to the development of more accurate
and comprehensive models, which are essential for detecting
and mitigating sophisticated cyber threats.
However, we note that the problem in (31) is still challenging to be solved directly due to the monotonic constraints in
C1, C2, and C3. The authors in [34] proposed relaxing such

4852

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 4, AUGUST 2024

constraints, enabling the problem to be directly solvable as an
optimization problem. However, in the context of FL, it is not
practical to apply such solutions due to the following:
• The server cannot adequately analyze local updates even
if all selected SPSs are trusted. The VDD quality metric
can only be utilized as described in Section V-B only if
all participants are completely trusted.
• Similar data may have varying contributions during the
global training rounds, wherein it could initially make
a higher contribution but gets reduced over time. For
instance, the training process slows down if the model is
closer to its stationary point, regardless of the associated
cost or local data quality. Thus, the rewards should be
given based on the value added to the global model every
round, not as a fixed contract.
• The server should ensure fairness between the participants where the higher cost does not imply higher quality.
In the following section, we solve this problem iteratively
by implementing a smooth FL process, including novel selection, aggregation, and averaging schemes. Then, we design
a fair and efficient postprocessing rewards mechanism that
fully ensures fairness so that the constraints (36–39) can
be implicitly satisfied. The introduced solutions incorporate
three phases; the first phase (i.e., the Preprocessing Phase)
aims to solve an optimized relaxation problem to select
the proper participants. The selected participants receive the
global model, update it locally, and upload it to the TPR.
In the second phase, the locally upgraded models by all
participating SPSs are aggregated. The TPR evaluates the
received models using two schemes (discussed below) and
assigns a contribution rank for each model. In the third phase,
the enhanced FedAvg based on adopted weights is applied
under two scenarios when the participants are fully trusted and
when some participants are malicious. The rewards are then
given based on the contribution rank given to each participant
(i.e., based on the uploaded model).

In contrast to the conventional FedAvg, which utilizes the
amount of data samples, this enhanced FedAvg does model
averaging by weighting the local models according to the
local data quality. Practically, weighting the model parameters
according to the amount of data is futile since the data may
contain redundancies and slightly affect the global model.
Further details can be found in Section VI, where the conventional FedAvg approach demonstrates inferior performance.
D. Two-Steps Verification Mechanism
In this approach, the retailer initially selects the participating
suppliers based on their local data quality. As explained
in Section V-B, the higher the data quality, the better the
model update. Thus, the server adopts the value of ϕ(Dm ) to
prioritize the suppliers and select the best set. However, the
malicious supplier may claim higher data quality. Therefore,
the server needs to apply a further verification step by testing
the model update before confirming the supplier’s reward. This
can be done by estimating the Euclidean distance between
two consecutive updates of the global model and the updated
local model, respectively, or by having global data samples
and feeding them into the uploaded models one by one before
conducting the global averaging.
1) Untrust-Based Model Averaging: In this scenario, some
participating SPSs might declare to have valuable data, yet
the shared models may be perturbed or generated randomly.
Consequently, a two-step verification is proposed, where the
TPR initially assesses the obtained model employing the
Euclidean distance or utilizing generalized test data evaluating
every model independently. Assuming the latter is utilized,
the adjusted averaging weights can be determined using the
formula as follows:
G(vm )
(40)
w m = M
m=1 G(vm )
Following that, the model is generated and updated based
on (39).

C. Quality-Assurance Model Averaging
The phases of the proposed solution are as follows. By
resolving (31) during the initial phase (i.e., the preprocessing
phase), it attempts to identify the appropriate SPSs. The
identified participants will then receive the global model for
local updating. The second phase combines the local updates
from all SPSs to mitigate the challenges arising using the
traditional FedAvg approach being assessed in two different
settings.
1) Trust-Based Model Averaging: The TPR trusts all participants, and the weight of each participant is determined
according to their reported data quality:
ϕ(Dm )

vm = M

m=1 ϕ(Dm )

(38)

Following that, the global model is generated and updated
given by
V (z) =

M

m=1

vm V m .

(39)

E. Incentive Reward design
We propose applying the Soft-max function to determine
the incentives provided to the selected SPSs after computing
the authentic average weights employing one of the methods
outlined in the preceding section. This will guarantee equality
according to the contribution provided by each SPS. It can be
expressed as follows:
e vm
w m = M

m=1 e

vm

.

(41)

It is important to note that for each round z, the total
rewards will be less than the budget assigned. As a result, the
participants receive the earned rewards from:
Rm = wm Bz .

(42)

We may infer from (41) and (42) that the obtained rewards
ensure equality for all SPSs participants and completely meet
the assigned budget. It is worth noting that our approach
considers the heterogeneity of threats and their distribution

ALBASEER et al.: FedPot: A QUALITY-AWARE COLLABORATIVE AND INCENTIVIZED HONEYPOT

Algorithm 1: FedPot Framework
Input: All available SPSs M
Output: Upgraded Security Model V
1 Initialize: starting global model V0 , local epochs ε, step size η, rounds
Z, and assigned budget for every global round;
2 TPR collects previous information (e.g, ϕ(Dm ), from existing SPSs
M.;
3 for z = 1 to Z do
4
The TPR establishes the time limit (i.e., deadline);
5
TPR addresses the optimization problem, P3, to choose the best
entities for participating in the model update;
6
TPR shares the model Vz −1 to chosen SPSs;
7
for Each SPS m ∈ M synchronously do
8
SPS m gets Vz −1 ;
9
SPS m updates m employing its VDD obtained data for E
epochs;
10
SPS m uploads Vm to TPR;
11
12
13

14
15
16

17

The TPR gathers all submitted updates from participating SPSs;
if Every participant is trusted then
TPR employs Equation (38) to recompute the weight
associated with each update.
else
TPR assesses each model using the generalization test data;
TPR utilizes Equation (40) to recompute the weight for every
update
TPR utilizes equation (39) to generate a modified global model.

implying that most SPSs, over a reasonable time frame, are
exposed to some kind of malicious activity. It might be
accurate that at certain times, specific SPS face a higher
volume or intensity of attacks, but when viewed over an
extended period, the distribution becomes relatively even. We
have designed the reward mechanism to factor in not just the
volume but also the quality of the data. This way, even if an
SPS does not face a high number of attacks, the uniqueness
or novelty of a single quality data point they contribute could
be of immense value, ensuring they are adequately rewarded.
Alg. 1 outlines the overall process of the suggested approach.
In Alg. 1, the TPR starts by initializing the model and the
hyper-parameters (step 1), then gathering prior information
from all SPSs (step 2). From steps 3–17, the TPR runs the
FL algorithm by determining the deadline for each round
(step 4) and solving the relaxed P3 (step 5) to select the best
participants while accounting for the stated data quality. The
global model is then sent (step 6), and all selected participants
undertake local training and submit all local models once
finished (steps 7–10). The TPR aggregates all models (step 11)
before deciding on one of the proposed schemes. If the TPR
can confirm the trustworthiness of the participating SPSs, the
solution in Section V-C is applied (steps 12 and 13), and the
solution in Section V-D is applied (steps 15 and 16) if TPR
can not. Finally, as explained in Section V-E, the rewards are
fairly given to the participants efficiently.
F. Architectural Mapping of the Proposed Solution
It is worth noting that our control framework is designed
to emulate the hierarchical architecture commonly observed
in modern SG systems. It comprises three main layers: the
Data Acquisition Layer, the Control Layer, and the Decision
Layer. Data Acquisition Layer: This is the base layer where
all sensors and IoT devices (as represented by our use of the

4853

N-BaIoT dataset in Section VI) are located. These devices
are responsible for collecting real-time information such as
voltage, current, and frequency from different points in the
grid. Control Layer: where the real-time data is analyzed
and control signals are generated. This layer integrates the
security protocols as studied through the IEC 104 dataset
in section VI-C. The layer includes controllers like Remote
Terminal Units (RTUs) and programmable logic controllers
(PLCs), which interact directly with the devices in the Data
Acquisition Layer. The control layer continuously monitors
and analyzes real-time data, identifying potential cyber threats
or operational anomalies. This layer generates signals, executes responses to mitigate threats, and integrates various
security protocols. A key feature is the strategic deployment
of honeypots within the network. These honeypots serve as
decoy systems designed to attract cyber attackers. This allows
for an in-depth analysis of attack strategies, significantly
enhancing the grid’s cyber resilience and providing valuable
insights into potential vulnerabilities. Decision Layer: This
is the topmost layer, consisting of control centers or cloudbased systems where higher-level decision-making processes
occur. Here, our proposed anomaly detection algorithms and
security measures are implemented (i.e., ML-based detector).
To generate realistic grid scenarios, we employed both the NBaIoT and IEC 104 datasets, creating a diverse set of operating
conditions and cyber-attack vectors. Our framework is also
designed to be scalable and robust, which allows for the
integration of additional sensors and control units as required.
The proposed incentive-based model is implemented at the
Decision Layer, ensuring that it benefits from the real-time
data collected and analyzed at the lower layers and addressing
the free-rider problem. This facilitates more effective and
timely decision-making. It is worth noting that in this layer
of the context of cybersecurity, test datasets cannot remain
static. When a new type of attack is detected by a honeypot, it
may initially be evaluated through heuristics, expert rules, and
anomaly detection methods for interim validation. Contextual
information provided by the SPS also helps the TPR to assess
the contribution’s potential impact. To corroborate new threats,
we propose sharing them (anonymously) with a subset of
trusted SPS for additional verification. As these new types
of attacks are validated, they will be incorporated into future
iterations of the test data, ensuring a relevant benchmark for
subsequent evaluations.
G. Theoretical Analysis of Robustness Against Malicious
SPSs
To validate the resilience of our Quality-Assurance Model
Averaging and Two-step Verification Mechanism against malicious activity, we introduce some theoretical metrics and
analysis. Let ΔV (z ) denote the deviation of the global model
V (z ) under the Trust-based Model Averaging scheme given
by (39):
ΔV (z ) = V (z ) − V ∗

(43)

Here, V ∗ represents the optimal global model that would have
been achieved without any malicious activity. We aim to bound

4854

Fig. 4.

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 4, AUGUST 2024

Label distribution among the logs of the first three devices.

ΔV (z ):
ΔV (z ) ≤ f (ϕ(Dm ), M , vm , . . .)

(44)

Here, f is a function that encapsulates the contributions of
local data quality ϕ(Dm ), the total number of participants
M, and their respective weights vm , among other parameters.
Similarly, we define ΔW (z ) as the deviation under the
Untrust-based Model Averaging scheme given by (40).
ΔW (z ) = V (z ) − V ∗

(45)

We aim to bound ΔW (z ) as follows:
ΔW (z ) ≤ g(G(vm ), M , wm , . . .)

(46)

Here, g is a function capturing the effects of the generalized
test G(vm ), total number of participants M, and the adjusted
weights wm , among others. In essence, the bounded nature
of ΔV (z ) and ΔW (z ) implies that our proposed schemes
are robust against a variable number of malicious SPSs,
maintaining the global model’s efficacy.
VI. P ERFORMANCE E VALUATION
In this section, we establish an experimental setting to
evaluate the efficacy of our proposed methods for improving
the security defense model and allocating fair incentives.
A. Experimental Setup
We employ the N-BaIoT [35] as well as IEC 104 and IEC
MMS datasets [36]. N-BaIoT was initially designed to cover
the security aspects of IoT devices. This dataset is crucial
for modern SG systems increasingly relying on IoT sensors
and actuators for efficient and intelligent grid management.
It includes data from benign operations as well as from a
range of attacks like Mirai and Gafgyt (Bashlite). Mirai attacks
focus on different flooding techniques using ACK, SYN, UDP,
and other protocols while performing device vulnerability
scans. Gafgyt attacks, similarly, engage in device scanning
and deploy a mix of attack strategies, including TCP and
UDP flooding. As in Fig. 4 for the first three devices, it
consists of eleven classes, one benign, while the remaining ten
represent adversarial classes (i.e., indicating malicious data),
with each sample including 115 attributes. These datasets, in
particular, include DDoS, which causes networks to become

overloaded with traffic; bot attacks that take advantage of
device flaws; man-in-the-middle attacks that intercept communications; SQL injection that manipulates databases; and XSS
which injects malicious scripts. Firmware flashing, physical
tampering, and side-channel attacks also represent advanced
threats. In SG, DDoS attacks can disrupt grid communications,
Bot attacks may compromise grid control systems, and MitM
attacks pose risks to data integrity. SQL injection and XSS are
relevant where SGs use Web interfaces or databases. Firmware
flashing and physical Tampering highlight the need to secure
grid hardware, while side-channel attacks demonstrate the
importance of protecting against indirect data leaks.
We compare our proposed method with the traditional
FedAvg technique, where the server allocates weights to the
local model updates based on the amount of traffic data
samples they include. Furthermore, we evaluate the incentivesbased algorithm against a customized-based algorithm. We
employ a supervised deep neural network (DNN) model consisting of 115 input layers followed by 115, 62, and 32 hidden
layers in which 12 , 14 , and 18 inputs follow each hidden layer,
respectively. The cross-entropy is used as a loss function. We
initially consider the N-BaIoT dataset’s initial device count,
consisting of nine devices exhibiting non-i.i.d. characteristics.
Similar parameters are adopted for all experiments. There are
eight SPSs as participants in the FL configurations, with each
SPS possessing one out of the nine devices present in the NBaIoT datasets, including both benign and adversarial samples.
One device is solely utilized to evaluate the overall model
developed by each of the other eight participants. We conduct
each experiment five times to ensure the accuracy of the
findings. Then, 50 devices are added to the data distribution.
Every device uses a 10 local epoch and a 32 local batch size.
We employ an adjustable learning rate with a default value of
0.01.
We assess the efficiency of our proposed scheme using
the following metrics accuracy, loss, true positive rate
(TPRate), false positive rate (FPR), and F1-measure given by:
TN
TPRate = TPTP
+FN , TNR = TN +FP , and F 1−score =
2∗Precision∗Recall . To assess the model’s efficacy, we utilize
Precision+Recall
the testing accuracy, which measures the proportion of accurately identified used incursions as a performance indicator.
Finally, we use rewards distribution fairness to showcase the
efficiency of the proposed rewards allocation framework.

ALBASEER et al.: FedPot: A QUALITY-AWARE COLLABORATIVE AND INCENTIVIZED HONEYPOT

4855

TABLE I
C OMPARATIVE R ESULTS FOR TPR ATE AND TNR OF C ONVENTIONAL
F EDAVG AND P ROPOSED S OLUTIONS U NDER ATTACK AND N ON -ATTACK
S CENARIOS ( I . I . D . DATA D ISTRIBUTION , N-BA I OT DATASET )

Fig. 5.
Comparative Analysis of Test Accuracy: Enhanced FedAvg,
Conventional FedAvg, and Centralized-Based Algorithms.

B. Numerical Results on BaIoT Dataset
In this section, we perform our numerical analysis on IDD
and non-i.i.d assumptions.
1) The IID Setting: Fig. 5 provides an overview of the
trust-based model averaging framework performance under
several distinct settings: complete data offloading to TPR (centralized training), the conventional FedAvg, and the proposed
enhanced-FedAvg (FedAvg based on data quality). The results
of the proposed algorithm demonstrate that it outperforms
the conventional FL approach, which can be attributed to the
effect of assigning model weights according to the local data
quality instead of the data size as in conventional FedAvg.
Furthermore, the enhanced FedAvg scheme can attain almost
traditional centralized performance. In contrast, the traditional
FedAvg algorithm needs more rounds to obtain the required
accuracy, which increases the cost, leading to surpassing the
budget assigned.
Fig. 6(a) shows the impact of the untrust-based model averaging framework under two scenarios: when all participants
are completely trusted and when some are malicious. Our
observations reveal that depending solely on the data quality
asserted by SPSs, the presence of corrupted models leads to
subpar models. This outcome arises due to malicious participants who assert high-quality data yet disperse it arbitrarily
or manipulate local models. The suggested untrusted model
averaging approach may efficiently remove detrimental models
by assigning weights to the shared models according to the
generalization test data. This causes the effects of adversarial
or disturbed models to vanish during the averaging phase or
at least reduces their negative impact on the designed global
model utilized for NIDS. Contrarily, malicious participants
may significantly reduce the defensive model’s effectiveness,
despite the data quality they claimed throughout the selection
process. We repeat similar experiments while splitting the data
between 50 and 100 SPSs to showcase the effectiveness of the
proposed approaches.
As shown in Fig. 6(b) and 6 (c), we use similar settings but
distribute the data across 50 and 100 SPSs and keep the labels
in an i.i.d fashion. We follow the original data distribution,
where the labels across the SPSs follow the same distribution.
We observe that even if the data is i.i.d, the presence of some

malicious participants affects the performance of the models,
especially as the number of SPSs increases. Nevertheless, the
untrust-based averaging scheme still performs better than the
trust-based scheme. Yet, the accuracy is slightly decreased as
the number of SPSs increases.
Furthermore, we assess the efficacy of the proposed
approaches regarding the fairness of the reward using the
true positive rate (TPRate) and the true negative rate (TNR),
critical performance indicators for the rewards allocation and
detection rate, and in the security defense model. Table I
shows that, whether malicious participants are present or
not, both proposed approaches exceed the traditional FedAvg.
Nonetheless, in the presence of malicious participants, the
proposed trust-based model averaging (PTrusted) performance
exhibits a considerable decline in TPRate, TNR, and fairness
of rewards. This degradation occurs as we solely depend on
the claimed data quality. On the other hand, the proposed
untrust-based model averaging ensures adequate outcomes
despite malicious participants. This is achieved through a
two-step verification process that excludes altered models
and accordingly assigns rewards, thereby achieving a high
level of fairness. Meanwhile, FedAvg distributes the incentives
randomly depending on the data size.
2) The Non-IID setting: For the non-i.i.d. setting, we
assume that each SPS holds only a maximum of 2 types
of attacks (i.e., Mirai UDP and combo). We consider three
scenarios regarding the number of devices: 9, 50, and 100.
We assign only a maximum of two classes for each SPS to
ensure that the datasets amongst SPSs are non-i.i.d. The default
data distribution is considered non-i.i.d. However, as illustrated
in Fig. 4, the labels’ distribution across all devices is almost
identical, even for those holding only 6 classes. Hence, in this
work, we consider a realistic non-i.i.d. distribution to evaluate
the performance in the worst situations.
As shown in Fig. 7(a), we initially run the first scenario
when the number of devices is only 9. One can see that
the performance in general drops by approximately 15%
for both proposed averaging schemes. However, when some
participants maliciously claimed high-quality local logs during the selection phase and uploaded perturbed models, the
performance of the first proposed scheme (i.e., trust-based
model averaging) dramatically dropped by almost 50% to
reach 46% accuracy. This is due to adopting inaccurate
weights during the evaluation phase, thereby impacting the
performance of the global model. In contrast, the second
proposed scheme (i.e., untrust-based model averaging) shows

4856

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 4, AUGUST 2024

Fig. 6. Test Accuracy Comparison of Proposed Schemes in the Presence of Malicious SPSs Claiming High-Quality Data While Uploading Defective Models
(i.i.d. Data Distribution, N-BaIoT dataset).

Fig. 7. Test Accuracy Comparison of Proposed Schemes in the Presence of Malicious SPSs Claiming High-Quality Data While Uploading Defective Models
(non-I.I.D. Data Distribution, N-BaIoT dataset).
TABLE II
C OMPARATIVE R ESULTS FOR TPR ATE AND TNR OF C ONVENTIONAL
F EDAVG AND P ROPOSED S OLUTIONS U NDER ATTACK AND N ON -ATTACK
S CENARIOS (N ON - I . I . D . DATA D ISTRIBUTION , N-BA I OT DATASET )

immunity against the perturbed models even when the data is
non-i.i.d.
In Fig. 7(b) and 7(c), we repeat the same experiments,
distributing the data across 50 and 100 SPSs, respectively.
From a security perspective, the performance in both figures
almost matches the performance in Fig. 7(a), where the second
scheme outperforms the first averaging scheme when attacks
are present. However, the convergence becomes slightly slower
as the number of SPSs grows. In the case of massively
distributed data due to the increased number of SPSs, more
rounds are required to capture patterns from all available SPSs.
We also investigate the effect of all proposed schemes,
including the reward mechanisms, on the overall performance
in terms of detection rate (i.e., TPRate and TNR) and the
fairness of reward distribution. From Table II, it can be
shown that proposed averaging methods significantly surpass
the conventional FedAvg, whether or not adversarial participants are present. However, when particular participants

are adversarial, the proposed trust-based model averaging (PTrusted) suffers drastically in terms of TPRate, TNR, and
reward fairness, which is unsurprising as these are heavily
based on the data quality. In contrast, the proposed untrustbased model averaging successfully filters the contaminated
uploaded models using a two-stage verification process. It
distributes the rewards appropriately, achieving a high degree
of fairness despite the presence of adversarial participants.
FedAvg, on the other hand, distributes its incentives randomly
according to the amount of data gathered. Nevertheless, all
schemes are affected by the data distribution amongst SPSs,
as we note when comparing the i.i.d. to non-i.i.d. results.
C. Numerical Results on IEC 104 Dataset
The IEC 104 Dataset was released by Brno University
in March 2022 and represents a significant resource in
the field of SG security [36]. It comprises IEC 104 and
IEC MMS headers and is primarily designed for anomaly
detection and security monitoring. The dataset captures a
broad spectrum of attack scenarios across different folders.
For instance, the but-iec104-i folder contains various attacks,
including Denial of Service (DoS), Injection, and Man-in-theMiddle (MITM) attacks. These offer a comprehensive view
of the threat landscape in the Industrial. Control Systems
(ICS) communications. Another folder, vrt-iec104, presents
a different set of intriguing attacks, such as value change
and masquerading attacks. It is worth mentioning that The
IEC 60870-104 (IEC 104) and IEC 61850 (MMS) datasets,
produced by the “Security monitoring of communication in
the smart grid (Bonnet)” project at the Brno University of

ALBASEER et al.: FedPot: A QUALITY-AWARE COLLABORATIVE AND INCENTIVIZED HONEYPOT

4857

Fig. 8. Test Accuracy Comparison of Proposed Schemes in the Presence of Malicious SPSs Claiming High-Quality Data While Uploading Defective Models
(I.I.D. Data Distribution, IEC 104 dataset).

Fig. 9. Test Accuracy Comparison of Proposed Schemes in the Presence of Malicious SPSs Claiming High-Quality Data While Uploading Defective Models
(non-I.I.D. Data Distribution, IEC 104 dataset).

Technology, Czech Republic (2019-2022), include CSV traces
from PCAP files [36]. These datasets, derived from both
real device observations and virtual application monitoring,
provide a comprehensive view of normal and attack traffic
patterns within smart grid environments. This dual approach,
blending real-world operational traffic with simulated attack
scenarios, ensures the datasets support robust model training
and validation, preparing the models to detect and mitigate
both existing and emerging threats effectively. Despite its
richness, the dataset was originally unlabeled and required substantial preprocessing. This step was critical to ensure that our
subsequent analyses were based on accurate, well-defined data.
The dataset is organized into multiple folders, each containing
data related to either IEC 104 or IEC MMS headers. Each
folder has a readme.txt file that provides valuable information,
including data types and timestamps related to the attacks. This
level of detail enabled us to better understand the structure and
implications of the data. We performed preprocessing steps
through a multi-stage process to adequately prepare the data
for our experimental framework. This involved labeling the
samples into categories such as benign, switching, scanning, or
communication interruption; cleaning the data to remove any
irrelevant or inaccurate information, and finally transforming it
into a format suitable for our machine learning algorithms. The
encoding was significant for nominal or categorical data. The
following section focuses on the numerical analysis conducted
using the IEC 104 dataset. We examine performance under
two conditions: the i.i.d. and non-i.i.d settings.
1) The IID Setting: We consider three scenarios featuring
varying numbers of substations: 20, 50, and 100. Fig. 8(a)–
8(c) display the performance of our framework, which includes

both trust-based and untrust-based schemes when the data
is IID (i.e., all clients have the same data distribution). Our
results clearly demonstrate the superiority of the enhanced
FedAvg, which achieves performance levels nearly identical
to centralized models. This can be attributed to our focus on
local data quality for model weight assignment as opposed
to merely considering data volume, as in traditional FedAvg.
This advantage holds even when malicious participants are
involved. Performance significantly drops and fluctuates when
only the trust-based scheme is employed. This drop is due
to the exclusive reliance on local data quality. However,
our untrust-based averaging scheme effectively mitigates this
by leveraging generalization test data to allocate weights,
neutralizing the impact of corrupted local models.
2) The Non-IID Setting: In this setting, we assume that
each SPS is limited to specific types of IEC 104 traffic patterns.
Fig. 9(a)–9(c) show that our proposed untrust-based averaging
scheme performs exceptionally well, even in the presence of
malicious activity. Trust-based model averaging struggles in
this context, experiencing a significant decline in accuracy due
to its reliance on claimed data quality. Furthermore, Table III
reveals that our approaches outperform traditional FedAvg in
critical security metrics such as TPRate and TNR, especially
when adversarial participants are present. The trust-based
model sees a decline in these metrics due to its dependence
on claimed data quality. In contrast, our untrust-based model
averaging maintains robust performance, demonstrating its
value in real-world scenarios where malicious activity is a
concern. Notably, our proposed approaches exhibit superior
performance in non-IID settings. This is due to our emphasis
on evaluating the quality of returned contributions rather

4858

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 4, AUGUST 2024

Fig. 10. Test Accuracy Comparison of Proposed Schemes in the Presence of Malicious SPSs Claiming High-Quality Data While Uploading Defective Models
(non-I.I.D. Data Distribution, IEC 61850 (MMS) dataset).
TABLE III
C OMPARATIVE R ESULTS FOR TPR ATE AND TNR OF C ONVENTIONAL
F EDAVG AND P ROPOSED S OLUTIONS U NDER ATTACK AND N ON -ATTACK
S CENARIOS (N ON - I . I . D DATA D ISTRIBUTION AND IEC 104 DATASET )

than just data quantity, leading to a more generalizable
global model. In summary, our numerical evaluation of the
IEC 104 dataset validates the effectiveness of our proposed
methodologies, particularly in non-i.i.d settings and when
malicious participants are involved. The insights gained from
this analysis will be crucial for refining and optimizing our
models for intrusion detection in ICS.
D. Verification With IEC 61850 Manufacturing Message
Specification (MMS) Dataset
To further verify our results, we carry out experiments using the IEC 61850 (MMS) dataset. IEC 61850
(MMS) is extensively employed in electric utility companies,
predominantly for substation automation and ensuring interoperability between different manufacturers’ systems. This
global standard is important for streamlining the communication infrastructure of electrical substations and facilitating the
integration, operation, and maintenance of diverse devices and
systems in SG. Its usage spans various applications, including
real-time monitoring, control of substation components, and
ensuring robust, reliable data exchange. The dataset used
includes both benign and malicious data samples. Remarkably,
the performance trends observed with this dataset closely
mirror those identified using the IEC 104 protocol data.
Specifically, under non-IID settings as a most challenging
scenario, our enhanced FedAvg framework, which includes
both trust-based and untrust-based schemes, continued to
demonstrate superior performance, closely approximating that
of centralized models. This consistency highlights the robustness of our approach, particularly our novel method of
weighting model updates based on the quality of local data
rather than its volume. Including the IEC 61850 dataset
not only verifies our initial findings but also broadens the

applicability of our framework. It shows that our untrust-based
averaging scheme, which assesses the quality of contributions
through generalization on test data, can effectively neutralize
the influence of corrupted local models, ensuring stable and
reliable model performance even in the face of malicious
activity. This result demonstrates the generalizability and
robustness of our approach across different SG communication
protocols, further validating the effectiveness of our method in
enhancing security and reliability in real-world, heterogeneous
SG network environments.
VII. C ONCLUSION
In this paper, we introduced FedPot, a novel quality assurance honeypot-based FL framework designed for network
security in SG. FedPot incorporates a novel, efficient, and
resilient aggregation and averaging schemes coupled with a
fair rewards mechanism. We presented novel schemes for local
data quality, participant selection, and global model upgrading
using the N-BaIoT, IEC 104, and IEC MMS datasets. In
FedPot, the TPR addresses a convex optimization problem,
prioritizing data quality over data size. Each SPS optimizes
the global model with its honeypot logs and transmits the
model updates back to the TPR. Subsequently, the TPR
enhances the defensive model using the approaches proposed
in this study. To mitigate the free-rider issue prevalent in AMI
networks within the FL framework, we proposed a new metric
to gauge local data quality and contributions, eliminating
the need to rely on data size. We also devised a two-step
verification process to address the challenge of adversaries
or underperforming SPSs. Additionally, we introduced an
improved FedAvg scheme for local model aggregations. The
results obtained from extensive simulations with realistic log
data attest to the effectiveness of our proposed scheme, which
outperforms current state-of-the-art techniques. As a direction
for future research, investigating the real-time implementation and assessment of FedPot in streaming, diverse, and
larger-scale environments would be insightful. Lastly, adapting
the FedPot framework to address other cybersecurity threats
within various IIoT applications could also be advantageous.
R EFERENCES
[1] A. Albaseer and M. Abdallah, “Privacy-preserving honeypot-based
detector in smart grid networks: A new design for quality-assurance
and fair incentives federated learning framework,” in Proc. IEEE 20th
Consum. Commun. Netw. Conf. (CCNC), 2023, pp. 722–727.

ALBASEER et al.: FedPot: A QUALITY-AWARE COLLABORATIVE AND INCENTIVIZED HONEYPOT

[2] P. Kumar, Y. Lin, G. Bai, A. Paverd, J. S. Dong, and A. Martin, “Smart
grid metering networks: A survey on security, privacy and open research
issues,” IEEE Commun. Surveys Tuts., vol. 21, no. 3, pp. 2886–2927,
3rd Quart., 2019.
[3] T. Morstyn, A. Teytelboym, and M. D. McCulloch, “Bilateral contract
networks for peer-to-peer energy trading,” IEEE Trans. Smart Grid,
vol. 10, no. 2, pp. 2026–2035, Mar. 2019.
[4] B. Zhang, C. Jiang, J.-L. Yu, and Z. Han, “A contract game for direct
energy trading in smart grid,” IEEE Trans. Smart Grid, vol. 9, no. 4,
pp. 2873–2884, Jul. 2018.
[5] G. Liang, S. R. Weller, J. Zhao, F. Luo, and Z. Y. Dong, “The 2015
Ukraine blackout: Implications for false data injection attacks,” IEEE
Trans. Power Syst., vol. 32, no. 4, pp. 3317–3318, Jul. 2017.
[6] D. Du, X. Li, W. Li, R. Chen, M. Fei, and L. Wu, “ADMM-based
distributed state estimation of smart grid under data deception and denial
of service attacks,” IEEE Trans. Syst., Man, Cybern., Syst., vol. 49, no. 8,
pp. 1698–1711, Aug. 2019.
[7] N. Abdi, A. Albaseer, and M. Abdallah, “The role of deep learning
in advancing proactive cybersecurity measures for smart grid networks:
A survey,” IEEE Internet Things J., early access, Jan. 17, 2024,
doi: 10.1109/JIOT.2024.3354045.
[8] J. Liu, X. Wang, S. Shen, G. Yue, S. Yu, and M. Li, “A Bayesian
Q-learning game for dependable task offloading against DDoS attacks
in sensor edge cloud,” IEEE Internet Things J., vol. 8, no. 9,
pp. 7546–7561, May 2021.
[9] P. Bolton and M. Dewatripont, Contract Theory. Cambridge, MA, USA:
MIT Press, 2004.
[10] K. Hamidouche, W. Saad, M. Debbah, M. T. Thai, and Z. Han,
“Contract-based incentive mechanism for LTE over unlicensed channels,” IEEE Trans. Commun., vol. 67, no. 9, pp. 6427–6440, Sep. 2019.
[11] W. Tian, M. Du, X. Ji, G. Liu, Y. Dai, and Z. Han, “Contractbased incentive mechanisms for honeypot defense in advanced metering
infrastructure,” IEEE Trans. Smart Grid, vol. 12, no. 5, pp. 4259–4268,
Sep. 2021.
[12] P. Voigt and A. Von dem Bussche, “The EU general data protection
regulation (GDPR),” in A Practical Guide, vol. 10, 1st ed., Cham,
Switzerland: Springer Int. Publ., 2017.
[13] D. C. Nguyen, M. Ding, P. N. Pathirana, A. Seneviratne, J. Li, and
H. V. Poor, “Federated learning for Internet of Things: A comprehensive
survey,” IEEE Commun. Surveys Tuts., vol. 23, no. 3, pp. 1622–1658,
3rd Quart., 2021.
[14] A. M. Albaseer, M. Abdallah, A. Al-Fuqaha, and A. Erbad, “Finegrained data selection for improved energy efficiency of federated edge
learning,” IEEE Trans. Netw. Sci. Eng., vol. 9, no. 5, pp. 3258–3271,
Sep./Oct. 2022.
[15] Z. Wang, M. Song, Z. Zhang, Y. Song, Q. Wang, and H. Qi, “Beyond
inferring class representatives: User-level privacy leakage from federated
learning,” in Proc. IEEE Conf. Comput. Commun., 2019, pp. 2512–2520.
[16] A. Ghorbani and J. Zou, “Data Shapley: Equitable valuation of
data for machine learning,” in Proc. Int. Conf. Mach. Learn., 2019,
pp. 2242–2251.
[17] J. Zhang, Y. Wu, and R. Pan, “Incentive mechanism for horizontal
federated learning based on reputation and reverse auction,” in Proc.
Web Conf., 2021, pp. 947–956.
[18] L. Lyu, X. Xu, Q. Wang, and H. Yu, “Collaborative fairness in federated
learning,” in Federated Learning. Cham, Switzerland: Springer, 2020,
pp. 189–204.
[19] W. Chen, D. Ding, H. Dong, and G. Wei, “Distributed resilient filtering
for power systems subject to denial-of-service attacks,” IEEE Trans.
Syst., Man, Cybern., Syst., vol. 49, no. 8, pp. 1688–1697, Aug. 2019.
[20] M. Du and K. Wang, “An SDN-enabled pseudo-honeypot strategy for
distributed denial of service attacks in Industrial Internet of Things,”
IEEE Trans. Ind. Informat., vol. 16, no. 1, pp. 648–657, Jan. 2020.
[21] Z. Li, J. Kang, R. Yu, D. Ye, Q. Deng, and Y. Zhang, “Consortium
blockchain for secure energy trading in Industrial Internet of Things,”
IEEE Trans. Ind. Informat., vol. 14, no. 8, pp. 3690–3700, Aug. 2018.
[22] F. Ye, Y. Qian, and R. Q. Hu, “A security protocol for advanced metering
infrastructure in smart grid,” in Proc. IEEE Global Commun. Conf.,
2014, pp. 649–654.
[23] M. A. Faisal, Z. Aung, J. R. Williams, and A. Sanchez, “Data-streambased intrusion detection system for advanced metering infrastructure in
smart grid: A feasibility study,” IEEE Syst. J., vol. 9, no. 1, pp. 31–44,
Mar. 2015.
[24] Y. Yan, R. Q. Hu, S. K. Das, H. Sharif, and Y. Qian, “An efficient
security protocol for advanced metering infrastructure in smart grid,”
IEEE Netw., vol. 27, no. 4, pp. 64–71, Jul./Aug. 2013.

4859

[25] H. Teryak, A. Albaseer, M. Abdallah, S. Al-Kuwari, and M. Qaraqe,
“Double-edged defense: Thwarting Cyber attacks and adversarial
machine learning in IEC 60870-5-104 smart grids,” IEEE Open J. Ind.
Electron. Soc., vol. 4, pp. 629–642, 2023.
[26] M. E. Eddin et al., “Fine-tuned RNN-based detector for electricity theft
attacks in smart grid generation domain,” IEEE Open J. Ind. Electron.
Soc., vol. 3, pp. 733–750, 2022.
[27] A. Albaseer and M. Abdallah, “Fine-tuned LSTM-based model for
efficient honeypot-based network intrusion detection system in smart
grid networks,” in Proc. 5th Int. Conf. Commun., Signal Process., Their
Appl. (ICCSPA), Dec. 2022, pp. 1–6.
[28] J. Kang, Z. Xiong, D. Niyato, S. Xie, and J. Zhang, “Incentive
mechanism for reliable federated learning: A joint optimization approach
to combining reputation and contract theory,” IEEE Internet Things J.,
vol. 6, no. 6, pp. 10700–10714, Dec. 2019.
[29] S. I. Popoola, R. Ande, B. Adebisi, G. Gui, M. Hammoudeh, and
O. Jogunola, “Federated deep learning for zero-day botnet attack
detection in IoT-edge devices,” IEEE Internet Things J., vol. 9, no. 5,
pp. 3930–3944, Mar. 2022.
[30] M. M. Badr et al., “Privacy-preserving and communication-efficient
energy prediction scheme based on federated learning for smart grids,”
IEEE Internet Things J., vol. 10, no. 9, pp. 7719–7736, May 2023.
[31] M. Ammar, M. Rizk, A. Abdel-Hamid, and A. K. Aboul-Seoud, “A
framework for security enhancement in SDN-based datacenters,” in
Proc. 8th IFIP Int. Conf. New Technol., Mobility Security (NTMS), 2016,
pp. 1–4.
[32] W. Tian et al., “Honeypot game-theoretical model for defending against
APT attacks with limited resources in cyber-physical systems,” ETRI J.,
vol. 41, no. 5, pp. 585–598, 2019.
[33] K. Wang, M. Du, S. Maharjan, and Y. Sun, “Strategic honeypot game
model for distributed denial of service attacks in the smart grid,” IEEE
Trans. Smart Grid, vol. 8, no. 5, pp. 2474–2482, Sep. 2017.
[34] D. Ye, R. Yu, M. Pan, and Z. Han, “Federated learning in vehicular
edge computing: A selective model aggregation approach,” IEEE Access,
vol. 8, pp. 23920–23935, 2020.
[35] Y. Meidan et al., “N-BaIoT—Network-based detection of IoT botnet
attacks using deep autoencoders,” IEEE Pervasive Comput., vol. 17,
no. 3, pp. 12–22, Jul.–Sep. 2018.
[36] “Bezpecnostní
monitorování
rídící
komunikace
ICS
v
energetických sítích (BONNET).” 2022. [Online]. Available:
https://www.fit.vut.cz/research/project/1303/.en

Abdullatif Albaseer (Member, IEEE) received
an M.Sc. degree in computer networks from the
King Fahd University of Petroleum and Minerals,
Dhahran, Saudi Arabia, in 2017, and the Ph.D.
degree in computer science and engineering from
Hamad Bin Khalifa University, Doha, Qatar, in 2022,
where he is a Postdoctoral Research Fellow with
Smart Cities and IoT Lab. He has authored and
coauthored over 30 conference and journal papers
in IEEE ICC, IEEE Globecom, IEEE CCNC, IEEE
WCNC, and IEEE Transactions. He also has six U.S.
patents in the area of the wireless network edge. His current research interests
include AI for networking, AI for cybersecurity, distributed AI, and edge
LLMs.

Nima Abdi received the B.Sc. degree in electrical
engineering from Qatar University in 2020. She is
currently pursuing the M.Sc. degree in data science
and engineering with Hamad Bin Khalifa University.
Her research focus is on the application of artificial
intelligence on smart grid security, specifically the
physical layer.

4860

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 4, AUGUST 2024

Mohamed Abdallah (Senior Member, IEEE)
received the B.Sc. degree from Cairo University,
Giza, Egypt, in 1996, and the M.Sc. and Ph.D.
degrees from the University of Maryland at College
Park, College Park, MD, USA, in 2001 and 2006,
respectively. From 2006 to 2016, he held academic
and research positions with Cairo University and
Texas A&M University at Qatar, Doha, Qatar. He
is currently a Founding Faculty Member with the
rank of an Associate Professor with the College
of Science and Engineering, Hamad Bin Khalifa
University, Doha. He has published more than 150 journals and conferences and four book chapters and co-invented four patents. His current
research interests include wireless networks, wireless security, smart grids,
optical wireless communication, and blockchain applications for emerging
networks. He is a recipient of the Research Fellow Excellence Award
at Texas A&M University in Qatar in 2016, the Best Paper Award in
multiple IEEE conferences, including IEEE BlackSeaCom 2019 and the
IEEE First Workshop on Smart Grid and Renewable Energy in 2015, and
the Nortel Networks Industrial Fellowship for five consecutive years from
1999 to 2003. His professional activities include an Associate Editor of the
IEEE T RANSACTIONS ON C OMMUNICATIONS and the IEEE O PEN ACCESS
J OURNAL OF C OMMUNICATIONS, the Track Co-Chair of the IEEE VTC
Fall 2019 Conference, the Technical Program Chair of the 10th International
Conference on Cognitive Radio-Oriented Wireless Networks, and a technical
program committee member of several major IEEE conferences.

Marwa Qaraqe (Senior Member, IEEE) received
the bachelor’s degree in electrical engineering from
Texas A&M University at Qatar, Qatar, in 2010,
and the M.Sc. and Ph.D. degrees in electrical engineering from Texas A&M University in College
Station, College Station, TX, USA, in August 2012
and May 2016, respectively. She is an Associate
Professor within the Division of Information and
Communication Technology, College of Science and
Engineering, Hamad Bin Khalifa University. Her
research focuses on various aspects of wireless
communication, signal processing, and machine learning, with applications
spanning multidisciplinary areas, such as security, IoT, and health. Her specific
interests lie in physical layer security, federated learning across wireless
networks, and employing machine learning techniques for enhancing wireless
communication, security, and healthcare systems. She has been actively
involved in developing physical layer security protocols for IoT networks and
has secured a NATO SPS grant for her work in this domain. Additionally, she
is engaged in research exploring emerging technologies like reconfigurable
intelligent surfaces and reinforcement learning to advance the capabilities of
wireless communication, particularly in the context of enabling efficient and
highly secure communication infrastructures for smart cities.

Saif Al-Kuwari (Senior Member, IEEE) received
the Bachelor of Engineering degree in computers
and networks from the University of Essex, U.K.,
in 2006, the first Ph.D. degree in computer science from the University of Bath in 2011, and the
second Ph.D. degree in computer science from the
Royal Holloway, University of London, U.K. He
is currently a Faculty with the College of Science
and Engineering, Hamad Bin Khalifa University
and the Director of the Qatar Center for Quantum
Computing. His current research interests include,
mainly, quantum cryptography, and quantum machine learning. He is a Fellow
of IET and BCS, and a Senior Member of ACM.
PAPER_TEXT
