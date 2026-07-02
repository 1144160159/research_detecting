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
# [611] Anomaly Detection in EVCS using Federated Learning with Auto-Optimized Edge Models
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
编号：611
题名：Anomaly Detection in EVCS using Federated Learning with Auto-Optimized Edge Models
年份：2026
DOI：10.1109/tia.2026.3661521
来源：IEEE Transactions on Industry Applications
PDF：paper/10.1109_TIA.2026.3661521.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\611.txt
- 原始字符数：56028
- 本次发送字符数：56028
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3661521

1

Anomaly Detection in EVCS using Federated
Learning with Auto-Optimized Edge Models
Arif Hussain, Member, IEEE, Ankit Yadav, Member, IEEE, Gelli Ravikumar, Sr. Member, IEEE

Abstract—This paper presents FedNAS, a novel federated
learning (FL) framework designed for robust and personalized
models to detect anomalies at distributed electric vehicle charging
stations (EVCSs), tailored to real-world industrial deployment.
The proposed framework enables collaborative anomaly detection
in spatially distributed EVCS without sharing raw data, thus
preserving user privacy and complying with data governance
requirements. A lightweight neural architecture search (NAS)optimized Simple Neural Network (SimpleNN) is proposed for
each EVCS node to ensure computational efficiency within
edge resource constraints. In contrast to traditional methods
that depend on fixed structures and simplistic aggregation,
FedNAS employs an ensemble-based meta-aggregation strategy,
facilitating superior knowledge integration among heterogeneous
clients compared to standard Federated Averaging (FedAvg). The
framework is evaluated using the IEEE 123-bus test system
with multiple EVCS nodes subjected to a cyberattack. The
results demonstrate that the FL framework achieves a detection
accuracy of up to 98.25%, with significantly reduced communication overhead and improved resilience to adversarial threats.
Comparative analysis with centralized learning and federated
variants validates the robustness and scalability of the proposed
approach outperforms FedAvg by 6.25% in average precision.
Furthermore, real-time simulation data is extracted using the
OPAL-RT platform to emulate realistic industrial grid conditions, validating the framework’s effectiveness in cyberattack
detection within dynamic EVCS environments. These findings
highlight the potential of federated learning to enable secure,
privacy-preserving, and scalable cyberattack detection for nextgeneration EVCS infrastructure.
Index Terms—Federated Learning, electric vehicle charging
station, cyber-attacks, anomalies, data preservation, neural architecture search,

I. I NTRODUCTION
The integration of electric vehicles into power grids, mainly
through EVCS, has transformed the Distributed Energy Resource (DER) ecosystem. However, as EVCSs have become
more complex and interconnected, they have been vulnerable
to cyber-attacks [1]. Traditional centralized machine learning
algorithms for detecting such abnormalities are challenging,
particularly regarding data privacy, communication overhead,
and real-time responsiveness, because they rely on collecting
raw data from all EVCS units at a central location [2]. EV
charging stations collect massive volumes of data, which can
be utilized to identify and prevent cyber-attacks. However,
“This research is funded partly by US NSF Grant # CNS 2105269 and US
DOE CESER Grant DE-CR000016.”
Arif Hussain, is with Department of Electrical Engineering, Louisiana
Tech. University, USA, Ankit Yadav is with the Department of Electrical and
Computer Engineering, Iowa State University, USA, and Gelli Ravikumar
is with the Department of Electrical and Computer Engineering, Florida
State University, USA (e-mail: ahussain@latech.edu, ankity@iastate.edu, and
rgelli@fsu.edu).

the centralization of this data collection method creates two
significant issues: privacy problems and scalability restrictions.
Data collection from geographically spread EVCS devices
may expose sensitive information, such as user data, car
charging habits, and grid-related information, to cyber threats.
Furthermore, sending vast amounts of data to a central server
causes significant bandwidth costs and system slowness. These
issues impede the effective detection of real-time cyberattacks,
necessitating low-latency responses and safe data handling
systems [3].
FL provides a decentralized alternative that directly addresses these challenges. In an FL architecture, EVCS units
train models locally with their data and share only the model
outputs (predictions), not the raw data, with a central server.
This approach inherently preserves data privacy and significantly reduces communication overhead. After collaborative
training, personalized models are deployed on the EVCS
nodes, enabling local, real-time inference for tasks such as
anomaly detection without requiring continuous server communication. This framework not only maintains data integrity
and security but also supports scalable implementations across
numerous distributed EVCS units [4], [5]. FL has been widely
promoted as a privacy-preserving machine learning approach
for distributed and sensitive data sources [6]. Its application in
power systems spans forecasting [7]–[10], grid management
[11]–[13], and anomaly detection [14]–[16], demonstrating
its capability for collaborative learning while preserving data
privacy. However, in the context of EVCS anomaly detection,
the data involved, such as voltage, frequency, power, and state
of charge (SoC), is primarily operational and non-personal.
Consequently, while prior studies [17], [18] frame FL’s benefit
as privacy preservation, its primary value in this infrastructurelevel context shifts towards data preservation. This emphasizes
maintaining data locality and integrity, enabling collaborative
learning under the constraints of limited communication, realtime processing, and data heterogeneity across EVCS nodes.
FL is traditionally categorized into horizontal federated
learning (HFL) and vertical federated learning (VFL) approaches [19], [20], both of which have been applied in
anomaly detection [21]–[25]. In HFL, clients share the same
feature space but possess different data samples. This aligns
perfectly with the EVCS use case, where distributed stations
monitor identical metrics (e.g., voltage, power) but from distinct charging sessions and locations. In contrast, VFL requires
clients with different feature sets to share a common user base,
a condition not met by geographically separate EVCS units.
Therefore, our work adopts the HFL paradigm.
In FL for EVCS cybersecurity, selecting an effective neural
network architecture is crucial for high detection accuracy.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3661521

2

Typically, a single, fixed architecture is prescribed for all
clients [25]–[27]. This approach implicitly assumes uniform
data distributions across clients—an assumption that rarely
holds in real-world EVCS environments, where stations exhibit
significant heterogeneity in usage patterns, local conditions,
and threat landscapes. Consequently, there is a pressing need
for methods that can tailor architectures to each client’s
unique data characteristics while still enabling effective global
collaboration.
A second major limitation is the reliance on the Federated Averaging (FedAvg) algorithm for aggregation, which
is prevalent in existing anomaly detection studies [4], [9],
[26], [28]. While computationally efficient, FedAvg performs
optimally only under the assumption of IID (Independent and
Identically Distributed) client data. In practical EVCS settings,
data is inherently non-IID. This divergence leads to suboptimal
global models, hampered convergence, and reduced detection
accuracy as client models develop biases from their local
data. This creates a demand for aggregation strategies that can
reconcile these local biases with global patterns to improve
generalization without sacrificing personalization.
A third challenge lies in the evaluation methodology. Many
prior studies rely on synthetic or benchmark datasets [17],
[18], failing to validate FL models within realistic gridconnected environments like IEEE test systems with integrated EVCS infrastructure. This reliance on centralized data
sources contradicts the core principle of FL—learning from
distributed, non-IID data. Moreover, such datasets often lack
the spatial, temporal, and operational variability inherent in
real EVCS deployments, thereby overlooking critical challenges like consumption heterogeneity, diverse attack surfaces,
and the distinct characteristics of local data streams.
To address the identified limitations: i) client-specific heterogeneity, ii) rigid model architectures, iii) FedAvg’s poor
performance on non-IID data, and iv) unrealistic evaluation settings, we propose FedNAS, a novel FL framework
for anomaly and cyberattack detection in EVCS. FedNAS
integrates Neural Architecture Search (NAS) [29] with an
ensemble-based meta-aggregation strategy [30] to achieve personalized yet globally coordinated learning. Within this framework, each client independently employs NAS to discover an
optimal, lightweight architecture (a SimpleNN model) tailored
to its local data, while the server performs meta-aggregation
of model insights. This decentralized approach ensures data
preservation and scalability. The framework’s effectiveness is
validated under realistic grid-connected conditions using an
IEEE 123-bus test system with four integrated EVCS nodes
subjected to cyberattack scenarios.
The key contributions of this study are:
• We propose a personalized FedNAS framework for cyberattack detection in EVCS, enabling each client to
autonomously discover optimal lightweight architectures
tailored to its local data characteristics.
• Unlike traditional FL methods requiring uniform architectures or weight alignment, our approach introduces
a robust ensemble-based meta-aggregation strategy that
fuses predictions from diverse client models, preserving
heterogeneity while enabling collaborative performance.

Fig. 1: Illustration of high-level architecture of the FedNAS
detection model
Our framework ensures data-preserving federated learning across EVCS nodes, where only model outputs are
shared during aggregation, enhancing scalability and privacy while avoiding direct model parameter exchange.
• A comprehensive evaluation of FedNAS using OPALRT-based real-time simulations on the IEEE 123-bus test
system with four integrated EVCS nodes. The results
demonstrate the framework’s strong detection performance, scalability, and resilience under multiple cyberattack scenarios.
• A rigorous comparative analysis against state-of-the-art
FL baselines (including FedAvg and FedProx) and centralized learning, demonstrating FedNAS’s superior performance in anomaly detection accuracy, communication
efficiency, and resilience to non-IID data.
•

We presented a preliminary version of this work at the
2025 Texas Power and Energy Conference (TPEC) [31]. This
research presents an FL framework and employs a lightweight
SimpleNN model to identify cyberattacks in EVCS. Although
the initial results showed promise, we faced limitations in
model scalability, limited technical insight, fixed architecture,
and simple aggregation for the global model.
The rest of the paper is organized as follows: Section II
presents the system model, threat model, and problem formulation. Section III details the proposed FedNAS framework.
Section IV presents a case study. Section V discusses the
results, and finally, Section VI concludes the paper.
II. S YSTEM M ODEL , T HREAT M ODEL , AND P ROBLEM
F ORMULATION
A. System Model
In this research, we introduce a federated learning-based
decentralized optimized framework for attack detection using
neural architecture search, called FedNAS. This framework is
specifically designed to improve the detection of cyberattacks
targeting EVCS, which are distributed at various locations and
integrated into a smart distribution grid. Using the principles of

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3661521

3

federated learning, FedNAS ensures the effectiveness of cybersecurity measures while preserving data privacy and security
at these critical infrastructure points. This innovative approach
not only increases the resilience of EVCSs against potential
threats but also supports the overall integrity and efficiency of
the smart distribution grid. The system comprises a collection
of clients, denoted as K = {1, 2, . . . , K}, where each client
k ∈ K represents a different node of the charging station for
electric vehicles connected to the grid. These EVCS nodes
are strategically deployed in various locations to facilitate the
efficient charging of electric vehicles. The central server plays
a crucial role in managing the federated training process, coordinating communication between clients, and ensuring that
model updates are aggregated securely and efficiently. This
architecture enhances the system’s ability to leverage local data
for model improvement, all while maintaining data privacy
and reducing training latency. Each client contributes to the
overall training objective by utilizing its local dataset and
communicating the necessary parameters back to the central
server, thus fostering a collaborative learning environment
without the need to share sensitive data.
We implement an HFL framework where each EVCS node
securely retains its raw operational data locally. In this collaborative setting, nodes share only the model weights Wk ∈ Rd
and the configurations of their searched architectures Ak ∈ A
with each other. This approach effectively safeguards user
privacy while significantly reducing the risk of data leakage,
which is particularly critical in the context of privacy-sensitive
energy systems. To simulate a realistic environment, each
client within the network operates under distinct user profiles
and varying cyberattack conditions, all modeled within the
IEEE 123-bus test system. The local dataset for each client is
defined as Dk = Dktrain ∪Dktest . This dataset captures both spatial
and temporal diversity, incorporating various load behaviors
and patterns of local cyberattacks, reflecting the complexity
of real-world energy use scenarios. The heterogeneity present
in both the data distribution and the dynamic characteristics
of the system reinforces the need for personalized neural
architectures and model outputs (predictions). This tailored
approach enables each EVCS to adapt more effectively to its
unique operational context while contributing to the overall
robustness and performance of the federated learning model. A
high-level architecture FedNAS detection model is illustrated
in Fig. 1.
The proposed FedNAS framework operates in synchronous
communication rounds indexed by t = 1, 2, . . . , T . In each
round, the following steps are performed collaboratively between clients and the central server:
(i) NAS-Based Architecture Search: Each client k ∈ K
performs a local Neural Architecture Search (NAS) to
(t)
identify a task-specific architecture Ak best suited to its
train
local data Dk .
(ii) Local Model Training: The client trains the selected
(t)
architecture Ak on its private dataset to obtain updated
(t)
model weights Wk .
(iii) Model Upload: Each client transmits its model tuple
(t)
(t)
(Wk , Ak ) to the central server, without revealing raw

data.
(iv) Meta-Learned Ensemble Aggregation The server colK
(t)
lects probabilistic predictions pk (xi )k=1 from client
models and performs meta-learned aggregation through
logistic regression:

pglobal (xi ) =

K
X

(t) (t)

αk pk (xi ),

k=1

eθ k
(t)
αk = PK

j=1 e

θj

(1)

where θ is learned by minimizing the meta-loss:
Lmeta =

X

i = 1N ℓ(yi , pglobal (xi )) + λ|θ|2

(2)

This approach forms a global decision mechanism without weight-level averaging or architectural alignment
∗(t+1)
∗(t+1)
(Wk
, Ak
), achieving higher accuracy than majority voting while preserving client heterogeneity.
B. Threat Model
EVCS is increasingly recognized as a critical component of
the smart grid infrastructure, but it is also vulnerable to a range
of cyberattacks, including replay attacks, spoofing, denialof– service (DoS), and man-in-the-middle (MitM) attacks. We
considered two distinct cyberattack scenarios: a single-pulse
attack and a more complex multiple-pulse attack. In both
cases, a MitM adversary manipulates control reference signals
to disrupt the charging process.
Single-Pulse Attack: In a single-pulse attack scenario, the
MitM adversary introduces a single rectangular pulse, denoted
A1 (w, d), to manipulate the control reference signals and
therefore disrupt the charging process. Here, A1 represents the
amplitude of the pulse, w is the total duration of the pulse, and
d is the duty cycle. The rectangular pulse is constructed such
that it attains an amplitude of A1 for the initial w ∗ d seconds
and drops to zero for the remaining (1 − w ∗ d) seconds.
The amplitude A1 could be positive or negative, depending
on the nature of the attack. To generate the tempered control
signal, the MitM attacker multiplies the original active power
s
reference Pref
with a rectangular pulse shifted by dc of the
form (1 + A1 (w, d)), resulting in a distorted reference signal
st
Pref
, as in (3). This modified signal is subsequently processed
by the calculation block Pref , which produces a distorted
t
power reference output Pref
, as in (4).
st
s
Pref
= Pref
∗ (1 + A1 (w, d))

(3)

t
Pref
= Pref ∗ (1 + A1 (w, d))

(4)

Multiple-Pulse Attack: To model a more stealthy and disruptive adversary, we extend the threat model to a multiplepulse attack. This attack is characterized
by a sequence of N
PN
rectangular pulses, denoted
A
(w
,
di , ∆ti ), where Ai
i
i
i=1
is the amplitude of the i-th pulse, wi its duration, di its duty
cycle, and ∆ti the time interval between the start of the i-th
and (i+1)-th pulses. This pattern creates aperiodic disruptions,
making detection more challenging. The attacker multiplies
the original power reference by this pulse train, resulting in a

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3661521

4

mt
compound distorted signal Pref
, as in (5). The corresponding
output from the calculation block is given by (6).
!
N
X
mt
s
Pref = Pref · 1 +
Ai (wi , di , ∆ti )
(5)
i=1
t
Pref
= Pref ·

1+

N
X

!
Ai (wi , di , ∆ti )

(6)

i=1

C. Problem Formulation
The objective of the proposed FedNAS framework is to
collaboratively learn personalized anomaly detection models
across a set of distributed EVCSs, while preserving data
privacy and addressing system heterogeneity. Each client
k ∈ K holds a private dataset Dk = Dktrain ∪ Dkval ∪ Dktest , a
local architecture Ak ∈ A, and corresponding model weights
Wk ∈ Rd .
The key challenges include:
• Non-IID data distributions across clients due to varying
grid conditions, load profiles, and attack scenarios.
• Need for personalized architectures and model outputs
(predictions) to reflect local characteristics.
• Communication efficiency and model generalization
across heterogeneous environments.
To address these challenges, we formulate the following
federated bi-level optimization problem that jointly learns
client-specific architectures and model outputs (predictions):
min

{Ak ,Wk }k∈K

X |Dk |
k∈K

|D|

Lval (Wk , Ak ; Dkval )

(7)

subject to: Wk = arg min Ltrain (W, Ak ; Dktrain ),

∀k ∈ K
(8)
Here, Ltrain and Lval denote the local training and validation
loss functions, respectively. The outer objective seeks to minimize the global validation loss across all clients by weighting
each client’s contribution proportionally to its dataset size. The
inner problem ensures that model weights are optimally trained
for the chosen architecture on local data.
W

III. P ROPOSED F ED NAS F RAMEWORK
The proposed fedNAS framework is designed to improve
privacy preservation, optimize communication efficiency, and
provide personalized anomaly detection specifically for distributed EVCSs. This framework confronts several pivotal
challenges encountered in traditional FL for power systems,
especially non-IID data distributions, model heterogeneity, and
the necessity for adaptable architectures that cater to edge
devices operating in diverse environments. At its core, the
framework employs a HFL paradigm, where each EVCS node
operates as an independent client, maintaining private local
datasets that remain securely on-device throughout the entire
training process. A significant innovation of this approach is
the integration of NAS at the client level, combined with
an ensemble-based meta-aggregation mechanism at the server
level. This dual-layered strategy ensures both architecture-level

Fig. 2: Working flow of Proposed FedNAS-based Framework.
Note: While (Wi , A) is shown for mathematical representation,
clients actually share predictions Pi for ensemble aggregation.
and parameter-level personalization, adapting to the unique
statistical characteristics and operational variances exhibited
by each client.
The operational flow of the FedNAS framework is visually
represented in Figure 2. The process begins with the comprehensive collection and labeling of data under both normal operational conditions and various attack scenarios. Each client
undertakes local preprocessing tasks, which include feature
extraction and the application of architecture search techniques
to identify the optimal neural network structure tailored to its
specific local dataset. Following the architecture selection, the
client trains the identified model. For aggregation, the client
then generates predictions on a server-provided validation
set and transmits these model outputs (predictions) to the
central server. Upon receiving the predictions, the central
server employs a metalearning-based aggregator. This aggregator combines the predictions from all participating clients
using ensemble methods. The meta-aggregation weights are
optimized using a small labeled validation set maintained at
s
the server (Dval
), containing representative normal and attack
scenarios generated from simulations. This dataset ensures
consistent evaluation across heterogeneous clients while preserving privacy, as it contains only operational data without

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3661521

5

(t)

user-specific information. The meta-weights αk are learned
based on each client model’s predictive performance on this
validation set, dynamically prioritizing more reliable models
regardless of their local dataset size. Calculate a personalized
global update for each client, effectively leveraging insights
gained from diverse client contributions. Following this aggregation, the personalized updates are redistributed to the
respective clients for local testing and evaluation, creating
a feedback loop that enhances model robustness and accuracy. This iterative refinement process unfolds over multiple
communication rounds, allowing for an ongoing convergence
of both architecture choices and weight adjustments across
the heterogeneous network of EVCS nodes. The framework
ensures data preservation by design, as clients only share
model predictions rather than raw data or model parameters.
This approach inherently mitigates privacy risks associated
with data reconstruction from model weights. Furthermore, the
ensemble-based aggregation provides natural resilience against
model poisoning attacks by diluting the influence of any single
malicious client through the meta-weighting mechanism.
The Federated Neural Architecture Search with ensemblebased meta-aggregation training methodology is comprehensively described in Algorithm 1, providing a clear framework
for implementing this advanced approach to anomaly detection
in distributed settings.
Algorithm 1 FedNAS: Federated Neural Architecture Search
with Ensemble-Based Meta-Aggregation
1: Input: Set of clients C = {C1 , C2 , ..., Cn }, number of
s
global rounds R, server validation set Dval
2: Initialize global meta-model Mg
3: for each round r = 1 to R do
4:
Initialize list Plocal ← [ ] ▷ List for client predictions
5:
for each client Ci ∈ C in parallel do
6:
Perform NAS on local data Di to obtain architecture Ai
7:
Train local model Mi using Ai and Di
8:
Generate predictions Pi on server validation set
s
Dval
using Mi
9:
Append Pi to Plocal
10:
end for
11:
Aggregate Plocal using ensemble-based metas
aggregation (with labels from Dval
) to update Mg
12:
for each client Ci ∈ C do
13:
Distribute updated meta-model Mg to Ci
14:
end for
15: end for
16: Output: Personalized and aggregated global meta-model
Mg

A. Deployment Architecture
The FedNAS framework employs a clear separation between
training and inference phases to optimize both performance
and latency:
Training Phase:

Edge (EVCS Nodes): Perform local NAS, model training, and generate predictions on server validation data
• Server: Maintains validation set, performs metaaggregation of client predictions, and computes ensemble
weights for model updates
Inference Phase:
• Edge (EVCS Nodes): Execute real-time anomaly detection using personalized models (Wk∗ , A∗k ) without server
communication
• Server: No operational role during inference—designed
for low-latency edge deployment
This architecture ensures that real-time anomaly detection
occurs locally at each EVCS node, meeting strict latency
requirements while leveraging collaborative learning during
training periods.
•

IV. C ASE S TUDY
This section describes the experimental environment, implementation details, dataset, and evaluation methodology used
to validate the proposed FedNAS framework for anomaly
detection in EVCS integrated into power distribution networks.
A. Experimental Setup and Reproducibility
All experiments used fixed random seeds for reproducibility.
The NAS process generates one optimal architecture per client
per round using our constrained search space with dynamic
scaling based on input dimensions. To handle heterogeneous
feature dimensions across clients (16-28 features as shown
in Table I), we employ zero-padding to the maximum feature dimension (28 features). The NAS process generates
architectures optimized for these standardized inputs while
maintaining computational efficiency through our lightweight
SimpleNN constraint. For complete reproducibility, detailed
hyperparameters, NAS configuration, and training protocols
are provided in Appendix TABLE VI: Experimental Configuration. The following subsections detail the test system, dataset
preparation, and signal response under normal and cyberattack
scenarios.
B. Test System Details
As depicted in Fig. 3, the IEEE 123 bus system testbed
has four EVCS, denoted by subscripts 1, 2, 3, and 4. These
are integrated into the distribution grid on buses 25, 51, 54,
and 97, respectively. Fig. 4 presents the block diagram for each
EVCS. The EVCS1 and EVCS3 have two extreme fast charges
(XFCs) each, while the EVCS2 and EVCS4 have four XFCs
each. These are represented as XFCjk , where ‘j’ stands for the
respective EVCS they are connected to, and ‘k’ denotes their
position within the EVCS. Thus, the testbed has 12 chargers,
each connected with an EV.
Each XFC-EV combination is a separate unit with an equivalent P-Q load. The model also incorporated SoC calculation
and charging management. This indicates that once the EV is
connected in G2V mode, the charging starts when the SoC is
less than 100. Similarly, in V2G mode, discharging is enabled
when SoC is greater than 0. However, once the SoC level

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3661521

6

exceeds these thresholds, the power reference to the XFC
control (i.e., charging control) is zero. Because this research
aims to examine the influence of EV charging and cyberattacks on EVSE on distribution, thorough modeling of XFC,
EV, and their respective controllers is not included.

Fig. 3: IEEE 123 Bus Feeder with EV integration

Fig. 5: Behavior of signal during normal scenarios
distribution, following the same feature extraction process
as client data. This ensures the meta-weights are optimized
on representative infrastructure-level operational data while
maintaining separation from client-specific datasets. Table 1
summarizes the comprehensive feature sets for each client.
TABLE I: Feature Distribution Across EVCS Clients

Fig. 4: The setup of EVs inside each EVCS

Client

Frequency

Voltage

Power

SoC

Total

Client 1
Client 2
Client 3
Client 4

4
4
4
4

4
8
4
8

4
8
4
8

4
8
4
8

16
28
16
28

C. Preparation of Dataset
In this case study, we constructed a variety of datasets
that included normal operating settings, single-pulse, and
multi-pulse cyberattacks. For regular operation, EVs were
gradually incorporated into the system using two scenarios:
with and without progressive ramping (slope). In contrast, the
frequency of single-pulse attacks was changed to ensure that
the data set included various possible scenarios. Key system
characteristics such as voltage, frequency, SoC, and power
were gathered from each EV charging station and the PCC
frequency. Following data collection, to create a manageable
and representative dataset for machine learning, we performed
feature extraction via a sliding window approach. A window
size of 20,000 samples was used, corresponding to 1-second
operational segments. Feature extraction was done by computing each feature’s mean and variance, which were computed
for every signal, effectively capturing both the steady-state and
dynamic behavior of the system. This process transformed
the high-resolution time-series data into a structured feature
matrix. This feature matrix was then used to train and test the
proposed FL model. For server-side meta-aggregation, a separate validation set was created with balanced normal/attack

D. Signal Response under Normal and Cyberattack Scenarios
Critical system characteristics such as voltage, power, SoC,
and frequency were continuously monitored on the EVCS
buses. This section examines the observed behaviors of these
metrics under normal operating scenarios and after a cyberattack. In normal scenarios, the integration of electric vehicles
into the system causes temporary changes in the measured
parameters. As shown in Fig. 5, when an EV integrates into
the system after 13 seconds, the frequency at the EVCS
bus oscillates briefly before settling within milliseconds. This
temporary behavior is primarily due to the intrinsic resilience
of the large-scale test system, which efficiently dampens
oscillations and recovers frequency stability. Similarly, when
an EV is integrated, the voltage at the EVCS bus drops
briefly, reflecting the sudden increase in demand. However, the
system quickly adapts to these fluctuations, ensuring general
stability. During normal operation, power and SoC signals
behave as predicted, with smooth transitions and constant
levels indicating reliable EV integration.
In the cyber-attack scenario, Fig. 6 depicts a single-pulse
attack. The attack happens at 51 seconds, causing dramatic

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3661521

7

Fig. 6: Behavior of signal during single-attacked scenarios

changes in the frequency and voltage signals on the EVCS
bus. Solid oscillations and uneven patterns throughout the
attack mark these alterations. Fig. 7 shows the multi-attack,
where both single and double pulse attacks are inserted in the
system. Notably, the SoC signal remains flat during the assault,
preventing the predicted charging process. Despite these disturbances, the system shows strong recovery capabilities. Once
the attack is complete, the frequency and voltage signals revert
to normal levels, demonstrating the test system’s resilience in
mitigating and recovering from cyber-attack transient disturbances. This recovery reflects the system’s capacity to retain
operational stability even in unfavorable circumstances.
V. R ESULTS AND D ISCUSSION
The dataset for this study was carefully developed by
incorporating a variety of relevant parameters (as indicated in
Table I), such as voltage, frequency, SoC, and power metrics
from the IEEE 123-bus system with distributed EVCS. These
attributes were chosen based on their importance in detecting
abnormalities and maintaining system reliability. Voltage and
frequency show the grid’s operational state and aid in detecting
anomalies such as voltage sags or frequency changes caused by
cyberattacks or operational problems. SoC reflects EV battery
levels, which might be affected by unusual charging behaviors
or attacks on EVCS operations. At the same time, power
records energy use and generation trends, which might be
valuable indicators of irregularities. The preprocessed dataset
was divided into training and testing subsets in an 80/20 split
to ensure a fair evaluation of the proposed federated learning
model. Data normalization approaches, such as standard scaling, were used to preserve consistency across feature ranges
and increase SimpleNN performance.

Fig. 7: Behavior of signal during multi-attacked scenarios

A. Client-Specific Performance Analysis
The evaluation results presented in Table II demonstrate
consistently high performance across all client models, with all
configurations achieving perfect recall (100%) on their respective test sets. Clients 1, 2, and 3 exhibit identical performance
profiles with 97.00% accuracy, 94.34% precision, and 97.09%
F1-score, suggesting these clients’ data distributions may share
similar characteristics. Client 4 shows higher performance
(100.00% accuracy, 100.00% precision, 100.00% F1-score),
potentially indicating either greater data complexity or fewer
training samples in this partition.
Notably, the global model maintains strong performance
(98.25% accuracy, 96.62% precision, 98.28% F1-score) that
closely matches the client-level results, demonstrating effective
knowledge aggregation while preserving the individual models’ ability to identify positive cases. The universal 100% recall
across all models suggests the architecture is particularly wellsuited for applications where false negatives carry significant
consequences, such as medical diagnosis or safety-critical
systems. The minor variations in precision with consistently
high accuracy indicate that most classification errors occur
near the decision boundary, with the models maintaining
excellent separation between classes overall.
The global meta-weighted ensemble achieves strong alignment between predictions (orange line) and ground truth
(blue dashed line), as shown in Fig. 8. The model maintains perfect recall (100%) with all attack events correctly
identified, evidenced by exact matches during attack periods.
While most normal operations are correctly classified (98.25%
accuracy), occasional false positives appear as isolated orange
spikes during non-attack intervals. The ensemble’s proba-

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3661521

8

Fig. 8: Prediction results of the global meta-weighted ensemble model across test samples
TABLE II: Performance Evaluation Across Clients and Global
Model
Model

Accuracy

Precision

Recall

F1-Score

Client 1
Client 2
Client 3
Client 4

97.00
97.00
97.00
100.0

94.34
94.34
94.34
100.0

100.0
100.0
100.0
100.0

97.09
97.09
97.09
100.0

Global Model

98.25

96.62

100.00

98.28

bilistic weighting effectively combines client models, with
prediction confidence exceeding 0.99 during true attack events.
These results demonstrate reliable cyber-attack detection while
preserving EVCS operational data privacy.
TABLE III: Performance Comparison of FL Approaches
Metric
Accuracy
Precision
Recall
F1
ROC AUC
Avg Precision

FedAvg
0.9625
0.9302
1.0000
0.9639
0.9625
0.9302

FedProx
0.9575
0.9463
0.9700
0.9580
0.9575
0.9330

FedNAS
0.9825
0.9662
1.0000
0.9828
0.9960
0.9955

Improvement
+2.00% vs FedAvg
+1.98% vs FedProx
+0.00% vs FedAvg
+1.89% vs FedAvg
+3.35% vs FedAvg
+6.25% vs FedProx

B. Comparative Performance Analysis
As demonstrated in Table III, FedNAS achieves consistent
performance improvements across all evaluation metrics compared to both FedAvg and FedProx. The proposed method
attains 98.25% accuracy, representing a 2.00% improvement
over FedAvg and 2.50% over FedProx. Notably, FedNAS
maintains perfect recall (100%) while simultaneously improving precision to 96.62% - outperforming FedProx by 1.98%
and FedAvg by 3.60%. The balanced performance is reflected
in FedNAS’s superior F1-score of 98.28%, which exceeds
both baselines by approximately 1.89-2.48%. More significantly, FedNAS demonstrates remarkable probabilistic calibration with a 99.60% ROC AUC score (3.35% improvement
over FedAvg) and 99.55% average precision (6.25% improvement over FedProx). These near-perfect scores approaching

the theoretical maximum of 1.0 indicate exceptional ranking
capability and confidence estimation. The results validate
that FedNAS’s personalized architecture approach, combined
with meta-learning aggregation, effectively leverages client
heterogeneity to achieve comprehensive performance gains.
The method proves particularly advantageous for probabilitysensitive applications like EVCS anomaly detection, where
both detection reliability (recall) and confidence calibration
(AUC-AP) are critical for operational safety and maintenance
planning.
C. Computational, Communication Overhead and Deployment Performance
The resource utilization analysis in Table IV demonstrates
that FedNAS achieves superior computational efficiency, requiring only 18.76s computation time - representing 11%
reduction compared to FedAvg (21.05s) and 25% reduction
compared to FedProx (24.99s). FedNAS maintains comparable communication efficiency (0.0010s) while providing
enhanced privacy through prediction-based aggregation rather
than weight exchange. In the training phase, clients share
predictions (not raw data or weights) with the server for
meta-aggregation. Fully edge-based inference, each EVCS
uses its personalized model locally with zero server communication. The real-time performance, 0.0208ms inference
latency, enables immediate anomaly detection at the edge.
FedNAS’s computational advantage stems from its efficient
two-phase architecture search, which optimizes client-specific
models without the computational overhead of FedProx’s proximal regularization. The approach maintains the fundamental
federated learning principle of sharing only model outputs
while delivering both performance gains and computational
efficiency.
As expected in a federated learning setting, 100% of the
raw client data is preserved locally, with zero exposure to the
central server. This stands in direct contrast to a centralized
model, which requires full data sharing and retains no data
locally, thereby posing significant privacy and security risks.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3661521

9

TABLE IV: Resource Overhead and Deployment Performance
Comparison
Metric
Computation Time (s)
Communication Time (s)
Inference Latency (ms)
Inference Communication

FedAvg

FedProx

FedNAS

21.05
0.0019
0.0220
Local Only

24.99
0.0018
0.0209
Local Only

18.76
0.0010
0.0208
Local Only

The FedNAS framework further enhances this data-preserving
principle by sharing only model predictions during aggregation, rather than raw data or model parameters, ensuring
that sensitive operational information never leaves the EVCS
nodes.
D. NAS Architecture Impact Analysis
The neural architecture search process revealed diverse
architectural preferences across clients as shown in Table V,
with both 16-neuron ReLU and 12-neuron LeakyReLU architectures emerging equally (50% distribution each). This balanced distribution demonstrates FedNAS’s adaptive capability
to match architectures to client-specific data characteristics:
• Architectural Diversity: The equal split between ReLU
and LeakyReLU activations indicates that different nonlinearity functions benefit different client datasets, with
LeakyReLU providing advantages for specific data distributions.
• Optimized Complexity: The discovered architectures
(12-16 neurons) confirm that moderate network capacity
sufficiently captures the anomaly detection patterns while
maintaining edge compatibility.
• Efficient Personalization: The architectural variation
demonstrates FedNAS’s ability to automatically tailor
model complexity to individual client needs without
manual intervention.
These findings validate our constrained search space design,
which efficiently discovers client-optimal architectures while
maintaining computational feasibility for edge deployment.
TABLE V: Discovered Architecture Distribution
Architecture

Frequency

16-neuron ReLU
12-neuron LeakyReLU

2
2

VI. C ONCLUSION
This research proposed FedNAS, a novel federated learning
framework enhanced with neural architecture search (NAS)
and a meta-learned ensemble aggregate for cyberattack detection in EVCS deployed on the IEEE-123 bus system. Unlike
conventional FL approaches, FedNAS addresses communication efficiency and model personalization by dynamically
optimizing client-specific architectures while preserving data
locality. Key Contributions and Findings
• Efficient and Scalable FL Framework: Reduced communication overhead to 0.16 MB (45% lower than centralized methods) by sharing only model weights, not
raw data. Demonstrated real-world scalability through

collaborative training across four EVCS nodes, each with
distinct operational profiles (voltage, frequency, SoC, and
power data under normal/attack conditions).
• Superior Detection Performance: Achieved 95.63% accuracy and perfect recall (100%) in attack detection, outperforming FedAvg (94.69% accuracy) while maintaining
robust precision (91.95%). The meta-learned ensemble
aggregation improved the average precision by 7.92%
(0.9963 vs 0.9171), ensuring a reliable ranking of the attack probabilities, critical to prioritizing threats in EVCS
operations.
• Architectural Adaptability: Discovered client-specific architectures (e.g., 16-neuron ReLU for simpler nodes, 32neuron LeakyReLU for complex data) via automated
NAS, balancing model expressiveness and efficiency.
FedNAS required only 1.2× more computation than FedAvg (35.87s vs. 28.96s) while reducing communication
time by 25% (0.0030s vs. 0.0040s).
• Privacy-Preserving and Practical: Retained all sensitive
EVCS data locally, using FL to share only aggregated
model updates. The framework’s low bandwidth demand
and high detection accuracy make it viable for deployment in resource-constrained edge environments.
Limitations and Future Work: The current framework’s
privacy protections lack formal guarantees against sophisticated inference attacks. Future work will integrate differential
privacy with rigorous adversarial testing to establish formal privacy bounds. While architecturally scalable, empirical
validation with larger client populations (50, 100 nodes) is
needed to quantify performance scaling and optimize system
parameters. Additionally, comprehensive statistical analysis
with multiple random seeds will strengthen result reliability
for large-scale smart grid deployments.
VII. A PPENDIX
VIII. ACKNOWLEDGMENT
This research is funded partly by US NSF Grant # CNS
2105269, US DOE CESER Grant DE-CR000016, and Iowa
Energy Center Grant #21-IEC-009.
R EFERENCES
[1] A. Hussain, A. Yadav, and G. Ravikumar, “Anomaly detection using bidirectional long short-term memory networks for cyber-physical electric
vehicle charging stations,” IEEE Transactions on Industrial CyberPhysical Systems, 2024.
[2] R. Zheng, A. Sumper, M. Aragüés-Peñalba, and S. Galceran-Arellano,
“Advancing power system services with privacy-preserving federated
learning techniques: A review,” IEEE Access, 2024.
[3] M. Alazab, S. P. RM, M. Parimala, P. K. R. Maddikunta, T. R.
Gadekallu, and Q.-V. Pham, “Federated learning for cybersecurity:
Concepts, challenges, and future directions,” IEEE Transactions on
Industrial Informatics, vol. 18, no. 5, pp. 3501–3509, 2021.
[4] S. Barja-Martinez, F. Teng, A. Junyent-Ferré, and M. Aragüés-Peñalba,
“Personalized federated learning with cost-oriented load forecasting for
home energy management systems,” IEEE Transactions on Industry
Applications, 2024.
[5] J. McCarthy, N. Grayson, J. Brule, T. Cottle, A. Dinerman, J. Dombrowski, J. Long, H. Tran, K. Quigg, M. Thompson et al., “Cybersecurity framework profile for electric vehicle extreme fast charging
infrastructure,” National Inst. of Standards and Technology (NIST),
Gaithersburg, MD (United . . . , Tech. Rep., 2023.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Industry Applications. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TIA.2026.3661521

10

TABLE VI: Experimental Configuration
Parameter
Value
Random Seeds
PyTorch/NumPy/Python 42
Training Hyperparameters
Optimizer
Adam (lr=0.001, wd=1e-5)
Batch Size
32
Local Epochs
20
Loss Function
BCE
FedProx µ
0.01
Dropout
0.2
Batch Norm
Yes
FedNAS Configuration
Search Phases
2 (Search + FL)
Candidates/Client
5
Evaluation
Multi-objective scoring
Complexity Penalty
Params/10,000
Neural Architecture Search
Neuron Ranges
4-8 (small), 8-16 (med), 16-32 (large)
Layer Depth
1-2 hidden layers
Activations
ReLU, LeakyReLU (α=0.1)
Validation Size
min(150 samples)
Data Processing
Train-Test Split
80-20
Normalization
StandardScaler
Padding
Zero-padding
Augmentation
Gaussian noise (σ=0.02)
Meta-Ensemble
Base Model
Logistic Regression (L2, C=0.1)
Weighting
Confidence + performance
Solver
L-BFGS
Threshold
Adaptive (0.35-0.65)
Federated Learning
Rounds
20
Clients
4
Evaluation
Global vs Ensemble

[6] E. T. M. Beltrán, M. Q. Pérez, P. M. S. Sánchez, S. L. Bernal,
G. Bovet, M. G. Pérez, G. M. Pérez, and A. H. Celdrán, “Decentralized
federated learning: Fundamentals, state of the art, frameworks, trends,
and challenges,” IEEE Communications Surveys & Tutorials, 2023.
[7] R. Wang, H. Yun, R. Rayhana, J. Bin, C. Zhang, O. E. Herrera, Z. Liu,
and W. Mérida, “An adaptive federated learning system for community
building energy load forecasting and anomaly prediction,” Energy and
Buildings, vol. 295, p. 113215, 2023.
[8] M. M. Badr, M. M. Mahmoud, Y. Fang, M. Abdulaal, A. J. Aljohani, W. Alasmary, and M. I. Ibrahem, “Privacy-preserving and
communication-efficient energy prediction scheme based on federated
learning for smart grids,” IEEE Internet of Things Journal, vol. 10,
no. 9, pp. 7719–7736, 2023.
[9] M. A. Husnoo, A. Anwar, N. Hosseinzadeh, S. N. Islam, A. N.
Mahmood, and R. Doss, “A secure federated learning framework for
residential short-term load forecasting,” IEEE Transactions on Smart
Grid, vol. 15, no. 2, pp. 2044–2055, 2023.
[10] Y. Wang and Q. Guo, “Privacy-preserving and adaptive federated deep
learning for multiparty wind power forecasting,” IEEE Transactions on
Industry Applications, 2024.
[11] C. Ren, R. Yan, M. Xu, H. Yu, Y. Xu, D. Niyato, and Z. Y. Dong,
“Qfdsa: A quantum-secured federated learning system for smart grid
dynamic security assessment,” IEEE Internet of Things Journal, 2023.
[12] V. Veerasamy, L. P. M. I. Sampath, S. Singh, H. D. Nguyen, and H. B.
Gooi, “Blockchain-based decentralized frequency control of microgrids
using federated learning fractional-order recurrent neural network,”
IEEE Transactions on Smart Grid, vol. 15, no. 1, pp. 1089–1102, 2023.
[13] M. Rajesh, S. Ramachandran, K. Vengatesan, S. S. Dhanabalan, and
S. K. Nataraj, “Federated learning for personalized recommendation in
securing power traces in smart grid systems,” IEEE Transactions on
Consumer Electronics, 2024.
[14] S. Islam, S. Badsha, S. Sengupta, I. Khalil, and M. Atiquzzaman, “An
intelligent privacy preservation scheme for ev charging infrastructure,”

IEEE Transactions on Industrial Informatics, vol. 19, no. 2, pp. 1238–
1247, 2022.
[15] R. Shrestha, M. Mohammadi, S. Sinaei, A. Salcines, D. Pampliega,
R. Clemente, A. L. Sanz, E. Nowroozi, and A. Lindgren, “Anomaly
detection based on lstm and autoencoders using federated learning in
smart electric grid,” Journal of Parallel and Distributed Computing, vol.
193, p. 104951, 2024.
[16] J. Jithish, B. Alangot, N. Mahalingam, and K. S. Yeo, “Distributed
anomaly detection in smart grids: a federated learning-based approach,”
IEEE Access, vol. 11, pp. 7157–7179, 2023.
[17] S. Purohit and M. Govindarasu, “Fl-evcs: Federated learning based
anomaly detection for ev charging ecosystem,” in 2024 33rd International Conference on Computer Communications and Networks (ICCCN). IEEE, 2024, pp. 1–9.
[18] Z. Lin and J. Li, “Fedevcp: Federated learning-based anomalies detection
for electric vehicle charging pile,” The Computer Journal, vol. 67, no. 4,
pp. 1521–1530, 2024.
[19] L. Lavaur, M.-O. Pahl, Y. Busnel, and F. Autrel, “The evolution of
federated learning-based intrusion detection and mitigation: A survey,”
IEEE Transactions on Network and Service Management, vol. 19, no. 3,
pp. 2309–2332, 2022.
[20] Y. Liu, Y. Kang, T. Zou, Y. Pu, Y. He, X. Ye, Y. Ouyang, Y.-Q. Zhang,
and Q. Yang, “Vertical federated learning: Concepts, advances, and
challenges,” IEEE Transactions on Knowledge and Data Engineering,
vol. 36, no. 7, pp. 3615–3634, 2024.
[21] W. Bouzeraib, A. Ghenai, and N. Zeghib, “Enhancing iot intrusion
detection systems through horizontal federated learning and optimized
wgan-gp,” IEEE Access, 2025.
[22] K. Cheng, T. Fan, Y. Jin, Y. Liu, T. Chen, D. Papadopoulos, and
Q. Yang, “Secureboost: A lossless federated learning framework,” IEEE
Intelligent Systems, vol. 36, no. 6, pp. 87–98, 2021.
[23] Y. He, Z. Shen, J. Hua, Q. Dong, J. Niu, W. Tong, X. Huang, C. Li, and
S. Zhong, “Backdoor attack against split neural network-based vertical
federated learning,” IEEE Transactions on Information Forensics and
Security, vol. 19, pp. 748–763, 2023.
[24] S. R. Kadhe, H. Ludwig, N. Baracaldo, A. King, Y. Zhou, K. Houck,
A. Rawat, M. Purcell, N. Holohan, M. Takeuchi et al., “Privacypreserving federated learning over vertically and horizontally partitioned
data for financial anomaly detection,” arXiv preprint arXiv:2310.19304,
2023.
[25] M. Kesici, B. Pal, and G. Yang, “Detection of false data injection attacks
in distribution networks: A vertical federated learning approach,” IEEE
Transactions on Smart Grid, 2024.
[26] S. Laridi, G. Palmer, and K.-M. M. Tam, “Enhanced federated anomaly
detection through autoencoders using summary statistics-based thresholding,” Scientific Reports, vol. 14, no. 1, p. 26704, 2024.
[27] L. Zhong and K. Liu, “Visual classification and detection of power
inspection images based on federated learning,” IEEE Transactions on
Industry Applications, 2024.
[28] Y. Wang, W. Fu, J. Chen, J. Wang, Z. Zhen, F. Wang, F. Xu, N. Duić,
D. Yang, and Y. Lv, “Spatiotemporal federated learning based regional
distributed pv ultra-short-term power forecasting method,” IEEE Transactions on Industry Applications, vol. 60, no. 5, pp. 7413–7425, 2024.
[29] C. He, M. Annavaram, and S. Avestimehr, “Towards non-iid and invisible data with fednas: Federated deep learning via neural architecture
search,” arXiv preprint arXiv:2004.08546, 2020.
[30] Z. Alsulaimawi, “Meta-fl: A novel meta-learning framework for optimizing heterogeneous model aggregation in federated learning,” arXiv
preprint arXiv:2406.16035, 2024.
[31] A. Hussain, A. Yadav, and G. Ravikumar, “Federated learning for
detecting cyber attacks in evcs using a lightweight neural network,” in
2025 IEEE Texas Power and Energy Conference (TPEC). IEEE, 2025,
pp. 1–6.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
