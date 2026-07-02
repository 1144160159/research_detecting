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
# [656] Edge-QSFL: Quantum-Enhanced Split Federated Learning With Multi-Head Temporal Networks for Edge-Based Intelligent Transportation Security
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
编号：656
题名：Edge-QSFL: Quantum-Enhanced Split Federated Learning With Multi-Head Temporal Networks for Edge-Based Intelligent Transportation Security
年份：2026
DOI：10.1109/tce.2026.3665233
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2026.3665233.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：时序、日志、KPI 与云原生异常检测、IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\656.txt
- 原始字符数：50733
- 本次发送字符数：50733
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

3929

Edge-QSFL: Quantum-Enhanced Split Federated
Learning With Multi-Head Temporal Networks for
Edge-Based Intelligent Transportation Security
Yue Zhao , Farhan Ullah , Nazeeruddin Mohammad , Senior Member, IEEE,
Umar Raza , Senior Member, IEEE, and Jawad Ahmad , Senior Member, IEEE
Abstract—The fast development of Intelligent Transportation
Systems (ITS) and the Internet of Vehicles (IoV) has shifted the
consumer mobility experience. However, the rapid expansion of
such technologies presents serious cybersecurity risks, demanding the implementation of a privacy-preserving, adaptive, and
powerful Intrusion Detection System (IDS). Currently, Federated
Learning (FL) paradigms in ITS are vulnerable to data poisoning
and model-based challenges in diverse applications due to a
lack of particular architectures capable of processing temporal
data streams. This paper introduces Edge-QSFL, a novel framework that combines quantum-enhanced Split Federated Learning
(SFL) and multi-head temporal networks. Our approach extracts
features from IoV streaming data using lightweight multi-head
Temporal Convolutional Networks (TCN) on edge clients. Subsequently, a quantum-based adaptive aggregation mechanism
is implemented by a global server. This mechanism employs
dynamic weighting to guarantee that the learning process is
resilient to data heterogeneity and poisoning. The architecture
also incorporates quantum-enhanced security packages to protect
the integrity of models. Extensive analyses of three sample
datasets, CICIoV2024, N-BaIoT, and UAVAttackData, indicate
almost perfect accuracy scores of 99.42%, 94.82%, and 98.0%,
respectively, and show to be more resilient to cyber threats.
The results reveal that Edge-QSFL presents a scalable, secure,
and high-performance solution, making it suitable for the next
generation of ITS networks.
Index Terms—Quantum machine learning, split federated
learning, edge intelligence, adaptive intrusion detection, intelligent transportation, quantum cryptography.

I. I NTRODUCTION

T

HE rapid digital transformation of ITS, driven by IoV
and connected consumer infrastructure, has allowed for
innovative forms of urban mobility and traffic optimization.
Received 30 November 2025; revised 26 January 2026; accepted 12 February 2026. Date of publication 16 February 2026; date of current version 2 June
2026. (Corresponding author: Farhan Ullah.)
Yue Zhao is with the Department of Computer Science, College of Science,
Mathematics and Technology, Wenzhou-Kean University, Wenzhou 325060,
China (e-mail: yuezhao@kean.edu).
Farhan Ullah and Jawad Ahmad are with the Cybersecurity Center, Prince
Mohammad Bin Fahd University, Khobar 31952, Saudi Arabia (e-mail:
fullah@pmu.edu.sa; JAHMAD@pmu.edu.sa).
Nazeeruddin Mohammad is with the School of Computer and Mathematical
Sciences, The University of Adelaide, Adelaide, SA 5005, Australia (e-mail:
nazeer.mohammad@adelaide.edu.au).
Umar Raza is with the Faculty of Science and Engineering, Department
of Engineering, Manchester Metropolitan University, M15 6BX Manchester,
U.K. (e-mail: u.raza@mmu.ac.uk).
Digital Object Identifier 10.1109/TCE.2026.3665233

The advancement of smart vehicles, roadside units, and transportation sensors has led to the development of networked
ecosystems that generate valuable mobility and safety data [1],
[2]. This transformation could enhance public safety, travel
times, and congestion management through real-time data
analytics and automated maintenance procedures.
Edge computing has emerged as an important paradigm for
efficient and low-latency data processing in ITS. Analyzing
vehicle data locally saves response times and bandwidth
usage while addressing privacy concerns about transferring
sensitive data to clouds. However, due to their distributed and
large-scale nature, modern transportation networks are highly
vulnerable to sophisticated cyberattacks [3]. Adversarial actors
pose a threat to the security of the population if they are
able to disrupt vehicle routing algorithms or inflict substantial
infrastructure harm by attacking traffic management systems.
This requires a strong cybersecurity paradigm with effective
defensive capabilities to protect the collaborative operational
integrity. In this scenario, the centralized nature of traditional
detection systems also encounters two significant challenges
[4]. The large-scale sharing of vehicle data and the high
privacy requirements of edge computing patterns are initially
challenging to balance. The learning process is still vulnerable
to modern adversarial techniques, such as data poisoning and
model integrity attacks.
FL allows training a shared model on several edge devices
without having to transfer raw data, which makes it a highly
important approach to resolving data privacy problems. SFL
collaborative learning architecture integrates the advantages
of FL and Split Learning (SL). This architecture is characterized by client devices computing the first layers of the
neural network, which they then send intermediate feature
representations to a central server, which computes the rest of
the forward pass. This design has the advantage of reducing
computation load on edge clients, but has a greater communication overhead and may cause bottlenecks because training
rounds can run sequentially. SFL provides a balanced trade-off
by enabling clients to simultaneously train a sub-part of the
model as in FL and at the same time partitioning the model
between client and server, such as in SL. Such a structure facilitates the first-time identification and prevention of abnormal
behaviors when they have not spread across the network [5],
[6]. SFL improves processing and communication capabilities
and thus can be used with scaled deployments in dynamic
edge situations. The system design enables the sharing of
models partially to complement responsiveness and reduce
latency to ITS and other real-time applications [7]. Despite
these benefits, current SFL systems continue to face limitations

1558-4127 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

3930

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

due to the temporal dynamics associated with transportation
data and the development of adequate security mechanisms
[8], [9], [10]. The quantum-inspired algorithmic frameworks
and quantum-based security primitives of Edge-QSFL are significantly different. This framework utilizes quantum-inspired
algorithmic principles to enhance traditional machine learning systems. Temperature-scaled aggregation approximates
a Boltzmann distribution to produce perturbation-resistant
client weighting. Quantum-based noise injection is employed
to improve model generalization. Furthermore, Edge-QSFL
employs quantum-resistant hashing primitives, such as
SHA3-256, to ensure model integrity and quantum key distribution algorithms to preserve the communication channel
between a client and a server. The concept uses quantum
technology and advanced cryptography to strengthen standard
computing infrastructure.
The proposed Edge-QSFL architecture integrates multiscale temporal processing with quantum-enhanced security
for intelligent transportation systems, addressing these critical
challenges [11]. Quantum-secure protocols and multi-head
TCNs are used to achieve complicated vehicular network
traffic temporal patterns and privacy-preserving IDS. The
quantum-inspired optimization promotes efficient learning
across distributed edge nodes, while the adaptive aggregation
approach strengthens resilience to cyber threats. The following
are the primary contributions of the paper.
1) We introduce Edge-QSFL, a novel quantum-enhanced
SFL framework that combines multi-head TCNs with
quantum-enhanced ITS security measures. This integrated approach solves the important concerns of
cybersecurity, privacy protection, and temporal pattern
detection in distributed network traffic.
2) The proposed multi-head, quantum-enhanced TCN
model is achieved by employing exponential dilation
rates to produce a cascade of dilated causal convolutions with residual connections. This facilitates
the retrieval of multi-scale time-varying features from
periodic network-traffic measurements and preserves
computational efficiency on resource-constrained edge
computers.
3) We also provide a quantum-enhanced adaptive aggregation approach that leverages quantum-inspired temperature scaling to dynamically compensate client input
based on pre-specified performance criteria. Modelpoisoning risks are reduced, and the global model
converges through client performance-based decisions.
4) We integrate robust quantum-security layers, including
model-integrity checking and quantum key-generation
techniques in distributed learning to defend against new
attacks. The resulting security solution ensures verifiable
implementation and the ability to model change throughout the federated network.
The remainder of this paper is organized as follows: Section II explains the related work, and Section III describes
the proposed method. Section IV presents the experimental
results, and Section V concludes the work.
II. R ELATED W ORK
The deployment of edge-based FL for IDS significantly
improves transportation security, offering an effective alternative to classical machine learning. This technique effectively overcomes two key issues associated with centralized

approaches: data privacy concerns and the computing limits
inherent in ITS [1]. Security measures are critically assessed
as the industry moves from cloud-based solutions to edge
computing, FL, and SFL-driven decentralized frameworks [3],
[6], [7].
A. Edge Computing
Devarajan et al. [5] introduce security and efficiency in
consumer IoV with blockchain and FL. Blockchain technology
enables vehicle-wide model training and update consistency
while protecting data. The system improves edge and cloud
task offloading to improve traffic forecasting, security, and
performance. Lin et al. [9] investigated edge computing
IDS architecture and resource management. Their proposed
approach effectively optimizes the distribution of various
resources. They implement a Single-layer Dominant and MaxMin Fair (SDMMF) approach to ensure balance among various
levels of a large-scale, edge-based IDS. They use Multilayer
Dominant and Max-Min Fair (MDMMF) to manage system
layer resources. Hasan et al. [12] suggested a federated
learning technique to optimize computational offloading in 6G
vehicle networks. This method ensures consistent performance
across various hardware platforms while also improving privacy and security by training models locally on edge devices.
The system updates vehicle information while optimizing
6G-V2X connectivity for self-driving capabilities. Cui et al.
[13] introduce an improved Gradient Boosting Decision Tree
model for secure edge computing in the Industrial Internet
of Things (IIoT). Yao et al. [14] developed an edge-assisted
technique to detect fraudulent attacks. Their wrapper-based
feature selection improves IDS by removing irrelevant and
redundant features. The algorithm divides attackers into four
groups based on their capabilities and uses ensemble learning
to improve detection rates. To reduce latency, several edge
nodes execute the lightweight detection method simultaneously.
B. Federated Learning
Several studies [4], [5] utilized FL-based IDS techniques
for transportation security. Mothukuri et al. [15] introduced
an FL framework to enhance the security and privacy of IoT.
Locally, it trains Gated Recurrent Unit (GRU) models on
devices, transmitting only model updates to a central server
rather than raw data. This solution protects user privacy while
also creating a powerful global IDS. Dos Santos et al. [16]
developed an FL system for network IDS that guarantees
trustworthy model updates. Their system evaluates classification confidence independently, lowering model maintenance
costs and errors. These techniques decreased false alarms by
12% missed detections by 9.6%, and modified the MAWIFlow
dataset procedures. Ruzafa-Alc ázar et al. [17] investigated
several privacy methodologies for training a federated IDS
in IIoT situations. The authors compare traditional (FedAvg)
and advanced (Fed+) aggregation methods on the non-uniform
ToN IoT dataset under various privacy requirements. The
Fed+ algorithm retains detection accuracy even when privacyprotecting noise is used in training. Ullah et al. [18] proposed
ZTID-IoV as a privacy-preserving IDS for IoVs. The system uses FL, a lightweight transformer, and meta-learning
to identify potential risks without gathering user data. Neurosymbolic AI produces interpretable results with minimal
processing resources, making it useful for resource-constrained

ZHAO et al.: EDGE-QSFL: QUANTUM-ENHANCED SPLIT FL WITH MULTI-HEAD TEMPORAL NETWORKS

3931

devices in zero-trust contexts. De Oliveira et al. [19] proposed
F-NIDS, which improves IDS scalability and data privacy. This
system employs a federated AI architecture with asynchronous
interactions to facilitate horizontal scaling and differential privacy to protect data integrity. The architecture is intended for
flexible deployment in a variety of cloud or fog environments.
The model accurately detects and classifies network threats
while protecting privacy.
C. Split Federated Learning
Thapa et al. [20] introduced a method, SFL, that combines FL and SL. SFL solves the SL problem, protects data,
and works with distributed learning models on resourceconstrained devices. Furthermore, the SFL framework proposes using the idea of differential privacy to improve data
security. Otoum et al. [21] proposed using an SL-based
IDS for ITS to address security threats in wireless vehicle
networks. The model employs SL to enhance the accuracy
of detection and classification. SL enhanced FL and transfer
learning models by 2-5% in accuracy and detection rates
while conserving power. Turina et al. [22] propose SFL, a
hybrid of federated and SL that incorporates their privacy and
efficiency advantages. SFL has a superior accuracy-privacy
tradeoff than parallel SL, allows for concurrent processing,
and minimizes client processing requirements. Additionally, it
maintains high accuracy on imbalanced data. The RingSFL
is a distributed learning technique designed to overcome the
fundamental limitations of standard FL [7]. RingSFL arranges
clients in a ring topology and trains a subset of the model
with FL and a model-splitting technique. This architecture
solves the problem caused by device heterogeneity, resulting in
significantly higher training efficiency. Local models are combined across the ring to prevent eavesdroppers from rebuilding
the model or recovering raw training data. Pasquini et al. [23]
explored potential vulnerabilities in split learning, a collaborative machine learning system. It shows that a malicious server
can actively hijack learning to reassemble client training data.
The developed threats are effective across a variety of datasets
and can overcome newly proposed protective mechanisms.
Furthermore, the study confirms that the protocol is vulnerable
to attacks from malicious clients, introducing the known risks
of FL to this decentralized system. Xu et al. [24] proposed
an SFL system that combines FL parallel training with split
learning model splitting. The method enables heterogeneous
devices to individually select their optimal deep neural network split points, thereby addressing resource constraints in
edge devices. To reduce system delay, it developed a strategy
that optimizes both the selection of split points and the
allocation of bandwidth simultaneously.
Our paper introduces Edge-QSFL, an innovative framework
for IDS in ITS. The architecture combines quantum-secure
SFL with multi-head temporal networks to develop a reliable and privacy-preserving IDS. It extracts features using
lightweight TCNs on edge clients and aggregates them using
quantum-inspired algorithms on a central server. This system
exhibits high accuracy and increased resilience against cyber
threats, providing a scalable and secure approach to transportation security.
III. P ROPOSED M ETHOD : E DGE -QSFL F RAMEWORK
Figure 1 illustrates the Edge-QSFL framework, which provides a secure ITS solution. Quantum-enhanced learning and

Fig. 1. Edge-QSFL: Quantum-enhanced split federated learning with multiscale temporal processing for secure intelligent transportation networks.

multi-scale temporal processing are integrated into a secure
SFL system. The method leverages quantum principles to
enhance resilience and efficiency. The complete architecture
is detailed in the following subsections.
A. Dataset Preparation
Three real-world datasets are used to evaluate the proposed
approach. The CICIoV20241 [25] dataset aims to improve
cybersecurity for IoVs. It includes authentic CAN bus data
from a 2019 Ford vehicle, as well as five spoofing and
Denial-of-Service (DoS) attacks. This dataset, designed as
a benchmark, enables the development and evaluation of
machine learning-based IDS to protect vehicles from cyber
attacks. N-BaIoT2 [26] is developed in a laboratory by attacking nine commercial IoT devices with Mirai botnet traffic,
allowing assessment of the method and identifying malicious
data from infected devices. The UAVAttackData3 [27] dataset
records GPS spoofing and jamming attacks on autonomous
aerial vehicles (AAVs). It comprises data from both simulated
and live flight testing, documenting both normal operations
and attack scenarios. The live attacks are carried out utilizing
a software-defined radio to broadcast fraudulent GPS locations
or jamming signals. This dataset is a helpful resource for
developing and assessing detection algorithms for typical AAV
cybersecurity threats. Table I summarizes the class distribution
for three cybersecurity datasets. The CICIoV2024 dataset
for automobiles is strongly dominated by spoofing attacks
(57.74%), including subcategories that break down individual
attack types. UDP threats comprise 38.39% of the N-BaIoT
dataset for IoT devices. The UAVAttackData datasets for
drones are significantly dominated by benign traffic (77% and
86%), while jamming and spoofing attacks are the minority
classes.
B. Quantum-Enhanced Data Preprocessing and Sequential
Formulation
The quantum-enhanced preprocessing phase addresses class
imbalances, where minority attack classes Cmin have significantly fewer samples than the main traffic class Cmaj .
1 https://www.unb.ca/cic/datasets/iov-dataset-2024.html
2 https://ieee-dataport.org/documents/n-baiot
3 https://ieee-dataport.org/open-access/uav-attack-dataset

3932

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

TABLE I
S UMMARY OF C LASS D ISTRIBUTION ACROSS CICI OV2024, N-BA I OT,
AND UAVATTACK DATA DATASETS

3) Sequential Data Formulation: The transformation of
tabular data into sequential formulations is utilized to leverage
the temporal features of cyber threats. The temporal sequences
of length L are constructed as illustrated in equation 6, using
a standardized feature matrix X ∈ RN×d .
St = {xt−L+1 , xt−L+2 , . . ., xt }

(6)

The sequence St represents temporal constraints. Equation
7 uses adaptive configuration to determine the sequence length
L based on the application environment. Equation 8 is used to
build the sequential dataset.
8
IoV CAN bus data multi-message patterns
<Llong
L = Lshort
real-time AAV threat detection
:
Lmedium IoT device traffic analysis
(7)
Dsequential = {(St , yt )}Tt=L
Furthermore, these procedures are adjusted to prepare the data
for quantum enhancement and efficient IDS processing.
1) Data Cleaning and Balancing: We first employ detailed
data cleaning to address missing values and infinite records in
N
a raw dataset Draw = {(xi , yi )}i=1
with N samples, as illustrated
in equation 1.
Dclean = {xi ∈ Draw | xi , NaN ∧ xi , ±∞}

(1)

The Synthetic Minority Over-sampling Technique (SMOTE)
with adaptive neighborhood parameters is used to achieve class
balancing. Let Ck be the k-th class, which has |Ck | samples [28].
Using equation 2, the SMOTE algorithm produces synthetic
samples for minority classes by linearly interpolating between
a sample xi and its k-nearest neighbors.
xnew = xi + λ · (x j − xi )

(2)

where λ ∼ U(0, 1) is a random interpolation coefficient and x j
is a randomly chosen neighbor among the k-nearest neighbors
of xi . Equation 3 illustrates the adaptive determination of the
neighborhood size k. It ensures that small minority classes
have valid neighborhood structure.
k = min(5, |Cmin | − 1)

(3)

2) Quantum-Inspired Feature Transformation: This
includes amplitude encoding and a quantum-inspired
transformation that projects features onto a unit sphere
via L2 normalization (Eq. 4). This mimics quantum state
representation, where kx̃i k2 = 1 analogous to quantum
state vectors. Unlike standard normalization, this creates
a geometry compatible with subsequent quantum-inspired
operations.
xi
(4)
x̃i =
kxi k2
Quantum computing data loading inspired this encoding
paradigm, which offers three benefits. First, the angular separations of the unit sphere provide greater feature discrimination.
Second, it is resistant to amplitude variance in IoT and IoV
traffic feature sets; and third, it enables quantum-inspired noise
injection strategies, making regularization easy.


xi
Dquantum = (x̃i , yi ) | x̃i =
, ∀(xi , yi ) ∈ Dbalanced
(5)
kxi k2

(8)

The label yt corresponds to the final element of the series
St , whereas T represents the total number of sequences.
The sequence lengths are empirically set at Llong = 10 for
CICIoV2024, Lmedium = 7 for N-BaIoT, and Lshort = 5 for
UAVAttackData. These parameters emerged using systematic
testing to balance temporal context capture and computational
performance for each dataset domain.
4) Quantum Noise Injection for Robustness: We injected
quantum-inspired noise during the training phase as a
principled regularizer to enhance model robustness and generalization across diverse environments. We employ equation
9 to apply additive noise to each input sequence St .
St0 = St + 

(9)

where  ∼ N (0, σ2 I) and the noise variance σ2 is dynamically
modified using equation 10 according to the features of the
data set.
σ2 = α · Var(Dtrain ) · βdomain
(10)
A scaling factor is represented by α, and the variance of
training features is Var(Dtrain). For network traffic, the unpredictability of wireless channels is taken into consideration
using a domain-specific multiplier, βdomain. The reliable representation of features is facilitated by this quantum-enhanced
preprocessing. This preserves temporal relationships needed to
detect cybersecurity risks in different applications.
C. Quantum-Optimized Multi-Head TCN Architecture
Figure 2 shows the architecture of the proposed quantumenhanced TCN. A multi-head TCN with quantum-inspired
techniques recognizes evolving attack patterns in the proposed
model. These enhancements include consistent initialization,
multi-scale feature capture, and adaptive attention. For stable
and reliable FL convergence, the model uses a quantuminspired approach to determine initial parameters (Eq. 12).
Based on quantum superposition, the system analyzes attack
data using exponential dilation rates (dh = 2h−1 ) across various time scales. Quantum-inspired attention mechanism (Eq.
13-14) dynamically adjusts network head priority, modeling
quantum measurement probabilities to emphasize important
temporal aspects for each input.

ZHAO et al.: EDGE-QSFL: QUANTUM-ENHANCED SPLIT FL WITH MULTI-HEAD TEMPORAL NETWORKS

3933

Algorithm 1 Quantum-Enhanced Client Update With MultiHead TCN Processing and Security Verification

Fig. 2. Quantum-enhanced multi-head TCN architecture featuring dilated
causal convolutions with residual connections for temporal feature extraction.

1) Multi-Scale Temporal Processing: The design includes
H parallel TCN heads with exponentially increasing dilation
rates dh = 2h−1 , where h = 1, 2, . . ., H. This multi-scale
architecture allows for the simultaneous monitoring of both
long-term intrusion patterns and short-term attack signatures [29], [30]. In Algorithm 1, each head processes input
sequences using dilated causal convolutions and residual
connections to maintain temporal causality and capture dependencies over extended time horizons. Equation 11 describes
the temporal processing for each head h. The computational
complexity of the client update in Algorithm 1 is O(H · L ·C 2 ),
dominated by the parallel temporal convolutions across H
heads for a sequence of length L and channel dimension C.
Th = TemporalBlock(Z, dh )

(11)

where Z = Wproj reshape(X ) represents the expected input
sequence. The Th ∈ RB×C×L indicates the temporal features
retrieved by head h, where B is the batch size, C is the number
of channels, and L is the sequence length.
2) Quantum-Inspired Parameter Initialization: A modified
normal distribution derived from the probability densities of
quantum harmonic generators is used to initialize the model
parameters in a quantum-inspired approach. To initialize each
weight matrix W ∈ Rm×n , use equation 12.
!
r
2
2
(12)
Wi j ∼ N 0, σ ·
m+n
0

where the variance scaling is improved by the principles of
quantum uncertainty, with σ > 1. Convergence stability is
improved across diverse client data distributions, and gradient
flow is enhanced during federated training using this initialization method.

3) Attention-Based Feature Fusion: A quantum-inspired
attention mechanism combines the outputs from several TCN
heads by dynamically weighting the contributions of each
head. The compressed temporal features from head h are represented by hh = GlobalAvgPool(Th ). The attention weights
are calculated using the equation 13.
exp(W2 tanh(W1 hh ))
αh = P H
j=1 exp(W2 tanh(W1 h j ))

(13)

where W1 ∈ Rda ×dh and W2 ∈ R1×da are learnable projection
matrices, and da is the attention dimension. The final attended

3934

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

3) Quantum Entropy Monitoring: We continuously monitor quantum-inspired entropy throughout federated learning
rounds, using equation 20:

representation is obtained through equation 14.
hfinal =

H
X

αh · h h

(14)
Et = −

h=1

The model uses adaptive integration to emphasize relevant
temporal scales for individual attack types, such as short-term
patterns for jamming detection and long-term dependencies
for complex spoofing attacks.
4) Temporal Block Design: The equation 15 is employed by
each TemporalBlock to implement dilated causal convolutions
with gated activation functions.
TemporalBlock(X, d) = ReLU(X + Conv1Dd (X))

(15)

To ensure that the output at time t depends only on inputs up
to time t, the dilated causal convolution with a dilation rate
d is denoted as Conv1Dd . Equation 16 summarizes the full
forward pass of the TCN that has been improved for quantum
computing.
hfinal , α = fc (X; Θc )

(16)

The attention weights across all heads are represented by
α = [α1 , α2 , . . ., αH ], and the client-side model parameters
are denoted by Θc . This architecture establishes a strong
foundation for the extraction of temporal features.

D. Quantum Security Layer Implementation
We employ a comprehensive quantum security layer to
address critical security requirements in FL environments,
ensuring end-to-end protection throughout the learning process.
1) Quantum Key Distribution Simulation: Secure clientserver communication is achieved through the simulation of
quantum key distribution principles [10]. The quantum circuit
described in Equation 17 is simulated within the Qiskit environment, with Hadamard gates establishing superposition and
CNOT gates implementing qubit entanglement.
|ψi =

Nq
O
i=1

H|0i,

Uent =

(t)
w(t)
k log(wk )

where Et denotes quantum-inspired entropy at round t, and
w(t)
k are aggregation weights. Significant changes in entropy
patterns indicate potential adversarial activity.
4) Quantum Entropy Monitoring: The vulnerabilities can
be detected by continuously monitoring quantum entropy
measures throughout federated learning rounds, utilizing
equation 20.
|St |
X
(t)
Et = −
w(t)
(20)
k log(wk )
k=1

The quantum entropy at round t is denoted by Et , and the
aggregation weights are w(t)
k . Significant changes in entropy
patterns warn security personnel of probable adversary activity.
The privacy and integrity of the FL process are preserved,
while effective defense against a variety of threats is ensured
by this multi-layered security approach.
E. Split Federated Learning Framework
Our approach employs an SFL architecture to distribute the
quantum-optimized TCN between edge clients and a central
server [6], [7], balancing privacy preservation and detection
performance as shown in Algorithm 2. The computation perround cost of the Edge-QSFL coordination method described
in Algorithm 2 is of the order of O(K · (H · L · C 2 ) + K log K),
where K is the size of the client group. The first term
corresponds to K client updates, each with the complexity
O(H · L · C 2 ) as analyzed in Algorithm 1. The second term
accounts for the overhead of quantum-enhanced, adaptive
aggregation.
1) Client-Server Model Partitioning: The model is split at
the final attention-pooling layer of the multi-head TCN. Clients
retain the temporal processing layers to locally analyze raw
sensor data, producing only the intermediate feature vector
hk = hfinal ∈ Rdh with dh = 128 using equation 21.
hk , α = fc (Xk ; Θc ).

CNOT(i, i + 1)

(17)

i=1

The quantum circuit simulation is executed using Qiskit’s
Aer simulator, producing measurement outcomes that form
cryptographically secure keys. In practice, this simulation
runs on classical hardware and serves as a quantum-inspired
key generation mechanism. These keys are then used for
establishing encrypted channels for transmitting intermediate
features hk and seeding the quantum-resistant hashing in the
integrity verification layer.
2) Model Integrity Verification: Each client calculates
quantum-resistant hash values of local model parameters using
the SHA3-256 algorithm, as shown in equation 18:
Hq = SHA3-256(Θ(k) )

(18)

These cryptographic hashes serve as digital fingerprints during
federated aggregation to detect model manipulation or Byzantine attacks.

(19)

k=1

Nq −1

Y

|St |
X

(21)

Transmitting this compressed, abstract representation hk ,
rather than raw data Xk or full gradients, enhances privacy: the
non-linear features are difficult to invert, significantly reducing
data leakage risks compared to standard FL.
2) Server-Side Classification: The server hosts the classification head, which processes the received features to generate
final predictions using equation 22.
ŷ = f s (hk ; Θ s ).

(22)

This split design reduces communication overhead while maintaining privacy across all application domains [8], [20].
3) Federated Learning Formulation: The joint optimization
objective combines client-side feature extraction and serverside classification using equation 23.
min

Θc ,Θ s

N
X

E(X,y)∼Dk [L( f s ( fc (X; Θc ); Θ s ), y)],

(23)

k=1

where L is the cross-entropy loss and Dk is the local data
distribution at client k.

ZHAO et al.: EDGE-QSFL: QUANTUM-ENHANCED SPLIT FL WITH MULTI-HEAD TEMPORAL NETWORKS

Algorithm 2 Edge-QSFL: Quantum-Enhanced SFL for Secure
ITS

3935

4) Dynamic Client Participation: The participation rate p
can be changed using equation 24, enabling the system to
accommodate adjustable participation patterns. This enables
intermittent connectivity in resource-constrained edge devices,
ensuring dependable functioning in real-world deployment
scenarios.
|St | = bpNc
(24)
F. Quantum-Inspired Adaptive Aggregation Mechanism
The aggregation phase uses a novel quantum-inspired
weighting technique to dynamically adjust client contributions
based on data quality and performance. To compute aggregation weights, we employ a quantum Boltzmann distribution,
with client accuracies treated as energy levels rather than
uniform averaging. Equation 25 scales performance metrics
exponentially to derive client aggregation weights.
wk = P

exp(acck /τ)
j∈St exp(acc j /τ)

(25)

where acck represents client k’s validation accuracy, and τ
is a quantum-inspired temperature parameter that controls
selectivity. The temperature adapts based on performance
variance across clients using equation 26.
τ = max(τmin , τmax − γ · σ(A))

(26)

The standard deviation of client accuracy is σ(A), temperature boundaries are τmin and τmax , and scaling factor
is γ. This adaptive temperature allows stable aggregation
during the initial learning phases, but becomes more selective
as models converge. Equation 27 is employed to aggregate
client-side parameters in the model. Similarly, server-side
parameters Θ(t+1)
are aggregated. Quantum entropy is mons
itored constantly by the framework to ensure model diversity,
as indicated by equation 28.
X
Θ(t+1)
=
wk · Θ(k)
(27)
c
c
k∈St

Et = −

|St |
X

wk log(wk )

(28)

k=1

This entropy metric functions as a diversity indicator,
ensuring that the model maintains beneficial variation during
training while simultaneously preventing adverse divergence.
The aggregation approach easily handles heterogeneous data
distributions across various vehicle models, IoT device types,
and AAV systems, while prioritizing clients for improved data
quality and better model performance.
IV. R ESULTS AND D ISCUSSIONS
A. Performance Metrics
We chose a variety of network traffic-based datasets and
several clients to thoroughly test the proposed method. The
suggested method is tested with three publicly available
standard datasets: CICIoV2024, N-BaIoT, and UAVAttackData. We evaluated performance by utilizing precision,
recall, F-measure, and accuracy, respectively. These measures are derived from True Positive (TP), False Positive

3936

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

Fig. 3. Accuracy progression of individual clients and the global model during federated training with 3 clients, demonstrating stable convergence across the
(a) CICIoV2024, (b) N-BaIoT, and (c) UAVAttackData datasets.

Fig. 4. Evolution of quantum-enhanced aggregation weights across training rounds with 3 clients, showing dynamic prioritization of reliable contributors to
mitigate poisoning attacks on the (a) CICIoV2024, (b) N-BaIoT, and (c) UAVAttackData datasets.

Fig. 5. Temporal progression of quantum entropy during aggregation with 3 clients, showing stable values that indicate balanced participation and prevent
client dominance across the (a) CICIoV2024, (b) N-BaIoT, and (c) UAVAttackData datasets.

(FP), True Negative (TN), and False Negative (FN) values.
Equation 29-32 provide performance measurements.
TP
Precision =
(29)
T P + FP
TP
Recall =
(30)
T P + FN
2 × TP
F-measure =
(31)
2 × T P + FP + FN
TP + TN
Accuracy =
(32)
T P + T N + FP + FN
B. Performance Analysis and Comparisons
Figure 3 shows that the quantum-enhanced FL model
showed consistent performance gains across all three datasets
across 100 training iterations. Accuracy in the CICIoV2024
dataset improved from a range of 0.3362–0.3821 to 1.0.
The accuracy of the N-BaIoT dataset increased from
0.1994–0.3299 to a range of 0.9217–0.9824 across five
IoT attack categories. During training, all datasets demonstrated considerable accuracy gains, with the greatest peaks

of 0.9653-0.9870, 0.8885-0.9326, and 0.9547-0.9831, respectively. Figure 4 illustrates the progression of the aggregation
weights with each subsequent federated round. client 1 scores
0.2852 and client 3 scores 0.4254 at round 18, and the
two scores converge to approximately 0.333 by round 30 in
the CICIoV2024 case. This resulted in a 32.37% accuracy
shift to complete 100% success, which is sustained by a
stable quantum entropy of 1.098. A balance of 0.333 and an
entropy of 1.097 in the five-class experiment adjusted accuracy
from 24.28% to 94.78%. Similar to UAVAttackData, quantumenhanced aggregation is stable and versatile across smart-city
purposes. Figure 5 illustrates quantum-enhanced entropy monitoring results. For the CICIoV2024 dataset, entropy remained
high and stable over 50 rounds, averaging 1.098. For the NBaIoT dataset, entropy values between 2.07 and 2.08 over 100
rounds indicated excellent diversity and balanced client participation, supporting the final 99.42% accuracy. Figure 6 depicts
the model’s convergence. On CICIoV2024, loss dropped
from 1.1871 to near zero over 100 rounds, improving accuracy from 32.37% to 100%. Similar stable convergence was
observed on other datasets. Figure 7 shows the accuracy trend.
For CICIoV2024, accuracy surged from 28.61% to 99.42%,

ZHAO et al.: EDGE-QSFL: QUANTUM-ENHANCED SPLIT FL WITH MULTI-HEAD TEMPORAL NETWORKS

3937

Fig. 6. Global training loss reduction over federated rounds with 3 clients, demonstrating smooth convergence and validating the stability of the quantuminspired aggregation across the (a) CICIoV2024, (b) N-BaIoT, and (c) UAVAttackData datasets.

Fig. 7. Accuracy progression with 8 clients, demonstrating maintained convergence and performance scalability with a larger, heterogeneous client pool across
the (a) CICIoV2024, (b) N-BaIoT, and (c) UAVAttackData datasets.

TABLE II
P ERFORMANCE R ESULTS FOR CICI OV2024 DATASET W ITH
D IFFERENT N UMBERS OF C LIENTS

reaching 50% by round 11 and 85% by round 40. The
N-BaIoT and UAVAttackData datasets exhibited similar adaptive and stable learning across smart city environments.
The performance evaluation of the model across three
datasets is summarized in Tables II to IV. On the CICIoV2024
dataset, Table II shows the model achieves near-perfect detection for DoS and spoofing attacks with 3 and 8 clients.
However, scaling to 14 clients degrades performance for
certain classes, such as the benign class, where the F1-score
drops to 0.71, though configuration remains critical as the
Speed class retains perfect detection. Table III details results
for the N-BaIoT dataset, where high initial F1-scores, such as
0.99 for Scan and Syn classes, are achieved with 3 clients.
Performance declines as clients increase, exemplified by the
Ack class F1-score falling from 0.86 to 0.52 when scaling from
3 to 13 clients. For the UAVAttackData dataset in Table IV,
performance varies by attack type. Jamming detection reaches

TABLE III
P ERFORMANCE R ESULTS FOR N-BA I OT DATASET W ITH
D IFFERENT N UMBERS OF C LIENTS

TABLE IV
P ERFORMANCE R ESULTS FOR UAVATTACK DATA DATASET W ITH
D IFFERENT N UMBERS OF C LIENTS AND ATTACK T YPES

an F1-score of 0.98 with 8 clients, falling to 0.68 with
13 clients. Spoofing detection shows variability, scoring 0.93,
0.65, and 0.84 with 3, 8, and 12 clients respectively. These

3938

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 2, MAY 2026

TABLE V
P ERFORMANCE C OMPARISON ACROSS D IFFERENT C LIENT C ONFIGURATIONS U SING CICI OV2024 DATASET

TABLE VI
P ERFORMANCE C OMPARISON ACROSS D IFFERENT C LIENT C ONFIGURATIONS U SING N-BA I OT DATASET

TABLE VII
P ERFORMANCE C OMPARISON ACROSS D IFFERENT C LIENT C ONFIGURATIONS U SING UAVATTACK DATA DATASET

TABLE VIII
P ERFORMANCE C OMPARISON W ITH R ELATED P UBLISHED S TUDIES

TABLE IX
A BLATION S TUDY: C OMPARISON W ITH BASELINE M ETHODS

results indicate that while adding clients generally reduces
performance, the specific impact depends on the attack type.
The overall performance of the model on the CICIoV2024
dataset under various client settings is summarized in Table V.
The model obtains an accuracy of 0.994 with 8 clients under
optimal conditions. Table VI shows that performance decreases
with increasing client count, with an accuracy of 0.749 for 13
clients. A significant experiment with 14 clients showed good
accuracy, such as 0.962, proving that data distribution is more
important than client count. Table VII shows that performance
is high for jamming accuracy 0.98 but lowers for spoofing,
such as 0.736, with only altered setups restoring performance.
These results show a fundamental scalability trade-off: client
engagement increases noise and heterogeneity, which degrades
the global model. As a result, system designers must prioritize
data quality and training dynamics over solely aggregating
additional clients. These results show that attack type and
client distribution greatly affect classification accuracy.
Table VIII compares the proposed Edge-QSFL system to
related studies. Edge-QSFL attains the highest overall performance, with a 99.37% F1-score, 100%, 99.26% recall, and
99.42% accuracy. The proposed framework outperforms the

related studies in an edge-based learning environment, proving
its dependability and effectiveness. Table IX presents an ablation study. It compares Edge-QSFL with standard baselines
and a key variant where only the aggregation mechanism
is changed. The results show that while the split-learning
architecture (SFL-AdaptSplit) improves over standard FL, our
proposed method, Quantum-Enhanced Adaptive Aggregation
(QE-AA) is the critical component. Replacing QE-AA with
standard averaging causes a clear drop in accuracy (from
99.4% to 97.5%) and slower convergence (44 rounds vs. 39).
V. C ONCLUSION
The Edge-QSFL work integrates a multi-head TCN and
quantum-inspired safety measures to enhance smart transportation infrastructures. This design can efficiently utilize
temporal network data while maintaining privacy with a
decentralized learning regime that integrates edge devices and
central servers. The adaptive aggregation protocol, supported
by quantum-inspired temperature modulation, protects against
data poisoning and the changing spectrum of cyber threats.
The quantum-enhanced multi-head TCN architecture captures
sequential traffic by utilizing multi-scale features. Embedding

ZHAO et al.: EDGE-QSFL: QUANTUM-ENHANCED SPLIT FL WITH MULTI-HEAD TEMPORAL NETWORKS

quantum security layers, using quantum-resistant hashing, and
modeling quantum key distribution show model consistency.
The approach performed well empirically across three different real-world datasets. Edge-QSFL detected vehicle-specific
threats, including CAN bus spoofing and DoS, with 99.42%
accuracy at CICIoV2024. N-BaIoT successfully classified
Mirai botnet variants with 94.82% accuracy for IoT device
security. In AAV scenarios (UAVAttackData), it achieved an
accuracy of 98.0% in distinguishing benign from GPS interference and spoofing. Quantum-enhanced adaptive aggregation
preserved high client diversity and proactively prioritized
trusted contributors, improving resilience to harmful updates.
Edge-QSFL demonstrated satisfactory performance with
3–8 clients; however, we observed a scalability trade-off,
as accuracy decreased as client pools expanded (e.g., at
14 clients). This suggests that hierarchical aggregation or
client clustering may be advantageous in environments that
are exceedingly heterogeneous. Quantum cryptography, such
as realistic quantum key distribution, may be explored
to improve model update security. However, processing,
memory, energy, and quantum hardware restrictions make
quantum cryptography on edge devices difficult. Lightweight
quantum-compatible hardware interfaces or efficient hybrid
classical–quantum protocols are needed to address these
issues. The quantum-inspired components can be optimized
for resource-constrained edge devices and integrate client
selection and hierarchical aggregation algorithms to enable
larger and more complicated transportation networks.
R EFERENCES
[1]

H. N. AlEisa et al., “Transforming transportation: Safe and secure
vehicular communication and anomaly detection with intelligent
cyber–physical system and deep learning,” IEEE Trans. Consum. Electron., vol. 70, no. 1, pp. 1736–1746, Feb. 2024.
[2] Y. Liu, Y. Wang, and G. Chang, “Efficient privacy-preserving dual
authentication and key agreement scheme for secure V2V communications in an IoV paradigm,” IEEE Trans. Intell. Transp. Syst., vol. 18,
no. 10, pp. 2740–2749, Oct. 2017.
[3] P. Ranaweera, A. D. Jurcut, and M. Liyanage, “Survey on multi-access
edge computing security and privacy,” IEEE Commun. Surveys Tuts.,
vol. 23, no. 2, pp. 1078–1124, 2nd Quart., 2021.
[4] H. Liu et al., “Blockchain and federated learning for collaborative
intrusion detection in vehicular edge computing,” IEEE Trans. Veh.
Technol., vol. 70, no. 6, pp. 6073–6084, Jun. 2021.
[5] G. G. Devarajan, S. Thangam, M. J. F. Alenazi, U. Kumaran, G. Chandran, and A. K. Bashir, “Federated learning and blockchain-enabled
framework for traffic rerouting and task offloading in the Internet
of Vehicles (IoV),” IEEE Trans. Consum. Electron., vol. 71, no. 2,
pp. 3817–3825, May 2025.
[6] L. U. Khan, M. Guizani, S. Muhaidat, and M. Ayyash, “QoS-enabled
wireless split federated learning: A reinforcement learning and optimization approach,” IEEE Trans. Consum. Electron., vol. 71, no. 3,
pp. 8968–8978, Aug. 2025.
[7] J. Shen et al., “RingSFL: An adaptive split federated learning towards
taming client heterogeneity,” IEEE Trans. Mobile Comput., vol. 23,
no. 5, pp. 5462–5478, May 2024.
[8] X. Liu, Y. Deng, and T. Mahmoodi, “Wireless distributed learning: A
new hybrid split and federated learning approach,” IEEE Trans. Wireless
Commun., vol. 22, no. 4, pp. 2650–2665, Apr. 2023.
[9] F. Lin, Y. Zhou, X. An, I. You, and K.-K.-R. Choo, “Fair resource
allocation in an intrusion-detection system for edge computing: Ensuring
the security of Internet of Things devices,” IEEE Consum. Electron.
Mag., vol. 7, no. 6, pp. 45–50, Nov. 2018.
[10] C. Qiao, M. Li, Y. Liu, and Z. Tian, “Transitioning from federated learning to quantum federated learning in Internet of Things: A
comprehensive survey,” IEEE Commun. Surveys Tuts., vol. 27, no. 1,
pp. 509–545, Feb. 2025.

3939

[11] Z. Qu, Z. Chen, S. Dehdashti, and P. Tiwari, “QFSM: A novel quantum
federated learning algorithm for speech emotion recognition with minimal gated unit in 5G IoV,” IEEE Trans. Intell. Vehicles, vol. 9, no. 10,
pp. 6512–6523, Oct. 2024.
[12] M. K. Hasan et al., “Federated learning for computational offloading and resource management of vehicular edge computing in
6G-V2X network,” IEEE Trans. Consum. Electron., vol. 70, no. 1,
pp. 3827–3847, Feb. 2024.
[13] J.-F. Cui, H. Xia, R. Zhang, B.-X. Hu, and X.-G. Cheng, “Optimization
scheme for intrusion detection scheme GBDT in edge computing
center,” Comput. Commun., vol. 168, pp. 136–145, Feb. 2021.
[14] W. Yao, K. Zhang, C. Yu, and H. Zhao, “Exploiting ensemble learning
for edge-assisted anomaly detection scheme in e-healthcare system,” in
Proc. IEEE Global Commun. Conf. (GLOBECOM), Dec. 2021, pp. 1–7.
[15] V. Mothukuri, P. Khare, R. M. Parizi, S. Pouriyeh, A. Dehghantanha,
and G. Srivastava, “Federated-learning-based anomaly detection for IoT
security attacks,” IEEE Internet Things J., vol. 9, no. 4, pp. 2545–2554,
Feb. 2022.
[16] R. R. dos Santos, E. K. Viegas, A. O. Santin, and P. Tedeschi,
“Federated learning for reliable model updates in network-based intrusion detection,” Comput. Secur., vol. 133, Oct. 2023, Art. no. 103413.
[17] P. Ruzafa-Alcázar et al., “Intrusion detection based on privacypreserving federated learning for the industrial IoT,” IEEE Trans. Ind.
Informat., vol. 19, no. 2, pp. 1145–1154, Feb. 2023.
[18] F. Ullah, G. Srivastava, L. Mostarda, and U. Raza, “ZTID-IoV: Zerotrust intrusion detection in IoV using neurosymbolic AI approach with
federated meta-learning,” IEEE Trans. Consum. Electron., vol. 71, no. 4,
pp. 12037–12046, Nov. 2025.
[19] J. A. de Oliveira et al., “F-NIDS—A network intrusion detection system
based on federated learning,” Comput. Netw., vol. 236, Nov. 2023, Art.
no. 110010.
[20] C. Thapa, P. C. M. Arachchige, S. Camtepe, and L. Sun, “SplitFed:
When federated learning meets split learning,” in Proc. AAAI Conf. Artif.
Intell., vol. 36, 2022, pp. 8485–8493.
[21] S. Otoum, N. Guizani, and H. Mouftah, “On the feasibility of split
learning, transfer learning and federated learning for preserving security
in ITS systems,” IEEE Trans. Intell. Transp. Syst., vol. 24, no. 7,
pp. 7462–7470, Jul. 2023.
[22] V. Turina, Z. Zhang, F. Esposito, and I. Matta, “Federated or split? A
performance and privacy analysis of hybrid split and federated learning
architectures,” in Proc. IEEE 14th Int. Conf. Cloud Comput. (CLOUD),
Sep. 2021, pp. 250–260.
[23] D. Pasquini, G. Ateniese, and M. Bernaschi, “Unleashing the tiger:
Inference attacks on split learning,” in Proc. ACM SIGSAC Conf.
Comput. Commun. Secur., Nov. 2021, pp. 2113–2129.
[24] C. Xu, J. Li, Y. Liu, Y. Ling, and M. Wen, “Accelerating split federated
learning over wireless communication networks,” IEEE Trans. Wireless
Commun., vol. 23, no. 6, pp. 5587–5599, Jun. 2024.
[25] E. C. P. Neto et al., “CICIoV2024: Advancing realistic IDS approaches
against DoS and spoofing attack in IoV CAN bus,” Internet Things,
vol. 26, Jul. 2024, Art. no. 101209.
[26] Y. Meidan et al., “N-BaIoT—Network-based detection of IoT botnet
attacks using deep autoencoders,” IEEE Pervasive Comput., vol. 17,
no. 3, pp. 12–22, Jul. 2018.
[27] J. Whelan, T. Sangarapillai, O. Minawi, A. Almehmadi, and K. ElKhatib, “Novelty-based intrusion detection of sensor attacks on
unmanned aerial vehicles,” in Proc. 16th ACM Symp. QoS Secur.
Wireless Mobile Netw., Nov. 2020, pp. 23–28.
[28] D. Dablain, B. Krawczyk, and N. V. Chawla, “DeepSMOTE: Fusing
deep learning and SMOTE for imbalanced data,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 34, no. 9, pp. 6390–6404, Sep. 2023.
[29] I. Gupta, D. Saxena, A. K. Singh, and C.-N. Lee, “A multiple controlled
Toffoli driven adaptive quantum neural network model for dynamic
workload prediction in cloud environments,” IEEE Trans. Pattern Anal.
Mach. Intell., vol. 46, no. 12, pp. 7574–7588, Dec. 2024.
[30] F. Sadique and S. Sengupta, “Modeling and analyzing attacker behavior
in IoT botnet using temporal convolution network (TCN),” Comput.
Secur., vol. 117, Jun. 2022, Art. no. 102714.
[31] S. Latif et al., “Mitigating model poisoning and tampering in consumer
IoT with HMAC in split federated learning,” IEEE Trans. Consum.
Electron., vol. 71, no. 4, pp. 12312–12322, Nov. 2025.
[32] W. Lu et al., “Stones from other hills: Intrusion detection in statistical
heterogeneous IoT by self-labeled personalized federated learning,”
IEEE Internet Things J., vol. 12, no. 10, pp. 14348–14361, May 2025.
PAPER_TEXT
