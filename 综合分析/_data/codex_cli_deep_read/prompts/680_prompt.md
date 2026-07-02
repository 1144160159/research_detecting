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
# [680] Federated and Quantized-Based Intrusion Detection for Embedded On-Board Automotive Networks
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
编号：680
题名：Federated and Quantized-Based Intrusion Detection for Embedded On-Board Automotive Networks
年份：2025
DOI：10.1109/tits.2025.3645854
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2025.3645854.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：联邦学习、隐私保护与分布式协同
相关性：强相关，分数 18
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\680.txt
- 原始字符数：64135
- 本次发送字符数：64135
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

1

Federated and Quantized-Based Intrusion Detection
for Embedded On-Board Automotive Networks
Muhammad Adil , Danish Javeed , Member, IEEE, and Prabhat Kumar , Member, IEEE

Abstract—Intelligent vehicles rely on hybrid On-Board Automotive Networks (OANs), such as Time-Sensitive Networking
(TSN) and Controller Area Networks (CAN), to support
autonomous driving and ADAS. Securing these networks is challenging due to resource constraints, heterogeneous protocols, and
evolving attacks. We propose an embedded-optimized, privacypreserving collaborative IDS for hybrid OANs. Leveraging Cloud
Vehicle Functions (CVFs), the framework enables robust model
training across vehicles without sharing raw data. To efficiently
process multi-protocol traffic, we introduce the Network Traffic
Temporal Encoder (NTTE), which transforms network packets
into temporal traffic images for anomaly detection. These NTTE
representations are analyzed by TCNnet, a lightweight neural
network designed for efficient embedded deployment. To make
TCNnet suitable for resource-constrained embedded systems,
we propose post-training quantization, significantly reducing its
computational and storage demands. Evaluated on real traffic, the
quantized TCNnet maintains over 99% detection accuracy, while
reducing model size by over 91% and memory footprint by 51%,
enabling practical deployment on resource-constrained ECUs.
To link IDS outputs to real-world transportation outcomes, we
develop the Transportation Impact Modeling Module (TIMM),
which maps network-level detection performance to vehiclelevel safety metrics (collision likelihood and Safety Message
Delivery Ratio, SMDR) and fleet-level traffic indicators (Vehicle
Flow Efficiency, VFE). TIMM simulations across Urban, Suburban, and Highway scenarios show the IDS reduces expected
collisions by up to 97.9%, while maintaining high traffic
flow efficiency (VFE = 0.949–0.995) and message reliability
(SMDR = 0.988–0.994). These results demonstrate that the
proposed IDS not only excels in network-level detection but
also directly enhances vehicular safety and traffic performance,
confirming its practical applicability in Intelligent Transportation
Systems.
Index Terms—Intrusion detection system, collaborative learning, intra-vehicular network, cloud vehicle.

T

I. I NTRODUCTION
HE rise in automation levels (LoA) in intelligent vehicles,
as defined by SAE J3016 [1], has increased the number

Received 1 March 2025; revised 30 July 2025 and 14 November
2025; accepted 12 December 2025. This work was supported
by the Research Council of Finland with CHIST-ERA through
the project AI4MultiGIS-AI integrated framework for intelligent
geospatial handling and robust operation in MultiGIS applications
under Grant 368766. The Associate Editor for this article was
T. R. Gadekallu. (Corresponding author: Prabhat Kumar.)
Muhammad Adil is with the School of Computer Science and Technology,
College of Intelligence and Computing, Tianjin University, Tianjin 300350,
China (e-mail: 6122000014@tju.edu.cn).
Danish Javeed is with the College of Artificial Intelligence, Dalian Maritime
University, Dalian 116026, China.
Prabhat Kumar is with the Department of Software Engineering, LUT
School of Engineering Science, LUT University, 53850 Lappeenranta, Finland
(e-mail: prabhat.kumar@lut.fi).
Digital Object Identifier 10.1109/TITS.2025.3645854

Fig. 1. Illustrations of various attack scenarios in hybrid OANs.

of electronic control units (ECUs) supporting ADAS and
autonomous driving. This growth places higher demands on
on-board automotive networks (OANs), especially as highdefinition sensors strain the bandwidth limits of legacy IVN
technologies such as MOST, CAN, and FlexRay [2]. TimeSensitive Networking (TSN) addresses these limitations by
providing bounded latency, guaranteed bandwidth, and precise time synchronization [3]. For instance, IEEE 1722–2016
ensures reliable audio-video transport through AVTP [4], while
gPTP enables synchronized transmissions across TSN-based
OANs. TSN thus represents a key advancement for modern
OANs and is expected to coexist with established technologies like CAN [5]. However, integrating these technologies
also introduces security risks. Both TSN and CAN lack
strong security mechanisms, making them vulnerable to cyber
threats [7], as shown in Fig. 1, including unauthorized access
and sensor data manipulation [8]. Such attacks can directly
compromise vehicle safety: manipulated AVTP packets may
misinform ADAS and trigger hazardous decisions. Fig. 2
shows how an attacker can sniff and compromise AVTP
traffic at the talker, inject forged packets to the listener, and

© 2025 The Authors. This work is licensed under a Creative Commons Attribution 4.0 License.
For more information, see https://creativecommons.org/licenses/by/4.0/

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
2

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Fig. 2. Illustrating the impact of malicious AVTP packets from a compromised
AVB talker on traffic safety communication, potentially causing ADAS to
make incorrect decisions and leading to dangerous vehicle maneuvers in crosstraffic and pedestrian scenarios [6].

mislead ADAS into unsafe actions, such as misjudging traffic
or failing to avoid collisions. Traditional security measures like
encryption and authentication introduce overhead that conflicts
with the strict timing requirements of OAN, making realtime security challenging. Intrusion Detection Systems (IDS)
provide an alternative by monitoring network behavior without
modifying existing nodes [9]. Recently, ML-based IDS have
gained traction for detecting complex attacks in OANs [10].
Although ML-based IDS solutions show promise, they face
key challenges in intelligent vehicles. Resource constraints
limit the deployment of computationally heavy models, while
rapidly evolving attacks demand adaptive detection. The heterogeneity of OAN protocols (e.g., AVTP, CAN, gPTP) further
complicates feature extraction due to protocol-specific attack
behaviors. A critical gap also persists in system evaluation:
despite high reported network-level accuracy, the real impact
on transportation safety and traffic flow is rarely quantified. Existing IDS frameworks lack a formal methodology
to translate network metrics (e.g., TPR) into vehicle-level
safety outcomes (e.g., collision probability) and fleet-level
efficiency, which are central to ITS. These challenges motivate
a collaborative approach in which edge vehicles collectively
extract, learn, and share attack patterns in a privacy-preserving
manner, allowing them to pool computational resources and
adapt to emerging threats without overloading individual
nodes. To link network security with transportation safety, we
develop the Transportation Impact Modeling Module (TIMM),
a framework that formally maps IDS performance metrics
(detection latency, TPR, FPR) to ITS-level outcomes. TIMM
integrates a discrete-time vehicle dynamics model, a probabilistic attack–detection timing model, and aggregation rules
to quantify how IDS behavior influences collision likelihood,
safety-message reliability, and traffic-flow efficiency. The main
contributions of our work are as follows:
• We propose a privacy-preserving collaborative learning
framework with adaptive momentum-aware aggregation,
leveraging the Cloud Vehicle Function (CVF) [11] to
enable vehicles to collaboratively learn attack patterns
and improve model robustness under heterogeneous traffic
conditions.

• We develop the TCNnet, a lightweight convolutional
model designed for efficient intrusion detection in network traffic. TCNnet extracts spatial features using
convolutional layers while leveraging post-training quantization to optimize memory usage and computational
efficiency. This makes it particularly suitable for deployment on resource-constrained edge devices.
• We introduce the Network Traffic Temporal Encoder
(NTTE), which processes packets from multiple protocols
(e.g., AVTP, CAN, gPTP), generating network traffic
images that capture temporal anomalies, enhancing the
detection of cross-protocol attacks.
• We design the TIMM to rigorously evaluate the realworld transportation impact of the proposed IDS.
TIMM translates network-level detection performance
into vehicle-level safety metrics (e.g., collision likelihood)
and fleet-level traffic efficiency indicators (e.g., Vehicle
Flow Efficiency), thereby directly linking cybersecurity
performance to ITS safety and operational goals.
II. R ELATED W ORK
The authors in [12] designed an approach to derive two
distinctive features of CAN bus communication: the time
interval between successive frames (interframe space or IFS)
and the counter-related values embedded in the data payload.
These features form the basis of their decision tree-driven
IDS. To assess their effectiveness, the authors conducted
evaluations using well-known ensemble learning algorithms,
specifically Random Forest (RF) and XGBoost classifiers. In
[13], the authors introduced CANShield, a DL–driven framework designed for signal-level monitoring of the CAN bus.
Their proposed architecture comprises three core components:
(a) a data preprocessing module that transforms the highdimensional CAN signal stream into structured time-series
data suitable for DL; (b) a data analysis module employing
multiple deep autoencoders, each operating at distinct temporal
resolutions to capture patterns across varying time scales; and
(c) an attack detection module that aggregates the outputs
using an ensemble-based decision strategy to identify malicious activity. The authors in [14] proposed an ML-based
IDS to detect attacks in intra-vehicle networks, especially in
CAN. Their proposed IDS utilizes Recurrence Plot (RP) to
exploit the temporal properties of CAN messages as well
as intra- and inter-message dependencies to create high-level
representations of CAN messages that are transmitted on the
bus. These representations are then fed into a custom neural
network that is trained to identify new intrusions. In [15],
the authors proposed a multi-stage IDS, where in the first
stage, the authors utilize an artificial neural network to detect
known attacks, while the second stage comprises an LSTM
autoencoder for new and unseen attack detection. Further, the
authors used a hierarchical federated learning environment to
preserve data privacy, analyze diverse driving behavior, and
update the model with the latest patterns of attacks.
Furthermore, the authors in [16] proposed a multi-stage
IDS based on DL for the detection and classification of
cyberattacks in Automotive Ethernet Networks (AENs). In
the first stage, the authors employed RF for cyberattacks
detection, while the authors utilized a Pruned CNN in the

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ADIL et al.: FEDERATED AND QUANTIZED-BASED INTRUSION DETECTION

second stage to minimize the false positive rate of their
IDS during the classification of various attacks. Similarly,
the authors in [17] designed an IDS named “AERO” for
in-vehicle networks. Their proposed “AERO” IDS comprises
three modules, i.e., a feature extractor for the construction of
three multimodal features, a neural network to process the
extracted features, and an online anomaly detector for the
calculation of the outlier scores in real time. In [18],
the authors propose an evaluation framework designed to
support reproducible, consistent, and efficient benchmarking
of detection algorithms. Their proposed framework utilizes a
simulation toolchain that offers customizable network topologies, traffic patterns, anomaly injections, attack scenarios, and
detection mechanisms. To illustrate its capabilities, the authors
evaluate their Network Anomaly Detection Systems (NADSs)
within a detailed in-vehicle communication environment, simulating realistic traffic anomalies. Moreover, the authors of
[19] introduce an IDS to detect the audio-video transport
protocol stream injection attacks in AENs. Their proposed IDS
is based on feature generation and CNN. Further, the authors
built a physical BroadR-Reach-based testbed and captured
real audio-video transport protocol packets to evaluate their
proposed IDS.
While existing IDS solutions for in-vehicle networks have
shown promise, they face key limitations. Many are too
resource-intensive for embedded environments, lack support
for hybrid protocols like CAN and TSN, and do not address
privacy concerns in collaborative settings. Moreover, current
models often struggle to adapt to evolving or zero-day attacks
due to their reliance on static training data. To address
these challenges, our proposed IDS integrates a lightweight,
quantized Tiny CNN (TCNnet) for efficient deployment, a
Network Traffic Temporal Encoder (NTTE) for cross-protocol
anomaly detection, and a privacy-preserving collaborative
learning framework using Cloud Vehicle Functions (CVFs).
III. P ROPOSED F RAMEWORK
In this section, we first provide the details of the encoding
mechanism, followed by the architecture of a deep learningbased intrusion detector. Finally, we present the proposed
privacy-preserved collaborative IDS.
A. Network Traffic Temporal Encoder (NTTE)
The first module of our proposed framework is the Network
Traffic Temporal Encoder (NTTE). This module processes
traffic packets from various protocols received from network nodes via port mirroring (e.g., BroadR-Reach) and
encodes these packets into network images. NTTE is designed
to accommodate heterogeneous protocol formats, including
CAN, TSN, and IP-based traffic, in order to standardize packet
structures through protocol-independent byte extraction and
alignment. These images serve as feature representations and
are used as input to the DL-based intrusion detector. Let Ξ[k]
denote a one-dimensional column vector representing the k-th
traffic packet. Formally, it is defined as:
0 [k] 1
Ψ1
BΨ[k] C
B 2 C
Ξ[k] = B . C ,
(1)
@ .. A
Ψ[k]
n

3

where each Ψ[k]
i represents a payload byte of the traffic packet
[k]
Ξ[k] and satisfies the condition Ψ[k]
i ∈ N with 0 ≤ Ψi < 256.
The total number of bytes in the traffic packet is denoted by n.
The size of Ξ[k] may vary depending on the type of protocol.
To analyze temporal dependencies between network packets, we group them using an overlapping sequence window of
length Υ ∈ N, where Υ ≥ 1. The collected packets within each
sequence window are expressed as:

Ξ[Υ] = Ξ[k] Ξ[k+1] Ξ[k+2] . . . Ξ[k+(Υ−1)] ,
(2)
where Ξ[Υ] is a structured matrix aggregating multiple packets.
To advance the window along the sequence of packets, we
introduce the stride parameter τ ∈ N, where τ ≥ 1. This
parameter controls the step size by which the window shifts,
thereby influencing the amount of temporal context preserved
from the previous window.
For clarity, the aggregated packets along with each element
j]
Ψ[k+
are structured in the following matrix representation:
i
0 [k] [k+1] [k+2]
1
Ψ1 Ψ1
Ψ1
. . . Ψ1[k+(Υ−1)]
BΨ[k] Ψ[k+1] Ψ[k+2] . . . Ψ[k+(Υ−1)] C
2
2
2
B 2
C
[Υ]
Ξ =B .
(3)
C,
..
..
..
..
@ ..
A
.
.
.
.
[k+1]
Ψ[k]
Ψn[k+2] . . . Ψn[k+(Υ−1)]
n Ψn
where each column corresponds to a single traffic packet,
and each row represents a specific byte position across the
aggregated packets.
After the aggregation of packets, the next step is to extract
a fixed number of bytes, s, from each packet in Ξ[Υ] . Since
OANs utilize multiple protocols with varying traffic image
sizes, a standardized packet length is required to ensure
consistency. To achieve this, we apply mean padding instead
of zero padding, as it better preserves statistical characteristics
of the data. The resulting structured representation, denoted as
Ξ[SPS] (Standardized traffic image size), is given by:
0 [k] [k+1] [k+2]
1
Ψ1 Ψ1
Ψ1
. . . Ψ1[k+(Υ−1)]
[k+(Υ−1)]
[k]
[k+1]
[k+2]
BΨ Ψ
C
Ψ2
. . . Ψ2
2
B 2
C
Ξ[SPS] = B .
(4)
C,
.
.
.
.
..
..
..
..
@ ..
A
[k+1]
Ψ[k]
Ψ[k+2]
. . . Ψ[k+(Υ−1)]
s
s Ψs
s
j]
where each element Ψ[k+
of Ξ[SPS] is defined as:
m
(
j]
Ψ[k+
, if i ≤ n(k + j),
[k+ j]
i
Ψm
=
µ,
if i > n(k + j).

(5)

j]
where, Ψ[k+
represents the i-th byte of the Ξ[k] -th packet.
i
To capture the temporal changes between consecutive packets, we compute the modulus of the difference between two
consecutive packets Ξ([k−1] and Ξ([k] . This difference is defined
as:

∆Ξ[k] ≡ Ξ([k] − Ξ([k−1] mod 28 .
(6)

The rate of change ∆ can be expanded to all packets within
the window size Υ, and formally defined as:
 [k]

∆Ξ
∆Ξ[k+1] ∆Ξ[k+2]
[Υ]
∆Ξ =
,
(7)
. . . ∆Ξ[k+(Υ−1)]
where ∆Ξ[k] represents the state of change between the Ξ[k] -th
and Ξ[k−1] -th packets.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
4

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Fig. 3. Illustration of proposed TCNnet with post-quantization process.

The matrix of changes for all elements in each packet within
a specified window size for SPS can be formalized as follows:
1
0 [k]
∆Ψ1 ∆Ψ[k+1]
∆Ψ[k+2]
. . . ∆Ψ[k+(Υ−1)]
1
1
1
B∆Ψ[k] ∆Ψ[k+1] ∆Ψ[k+2] . . . ∆Ψ[k+(Υ−1)] C
2
2
2
C
B 2
∆Ξ[SPS] = B .
C (8)
..
..
..
..
@ ..
A
.
.
.
.
[k+1]
∆Ψ[k]
∆Ψ[k+2]
. . . ∆Ψ[k+(Υ−1)]
s
s ∆Ψ s
s

Finally, to better analyze the data within packets, each
[k+ j]
element ∆Ψm
(byte) of ∆Ξ[S PS ] is further divided into 4-bit
segments (e.g. nibbles). This process is formalized as:
%
8$
[k+ j]
ˆ
< ∆Ψm
,
if m is odd,
j]
24
(9)
∆Ψ̃[k+
=
m
ˆ
: [k+ j]
∆Ψm &0 × 0F, if m is even.
[SPS]

The resulting detailed matrix ∆Ξ̃
is represented as:
0 [k]
1
[k+1]
[k+2]
∆Ψ̃1 ∆Ψ̃1
∆Ψ̃1
. . . ∆Ψ̃[k+(Υ−1)]
1
B∆Ψ̃[k] ∆Ψ̃[k+1] ∆Ψ̃[k+2] . . . ∆Ψ̃[k+(Υ−1)] C
2
2
2
[SPS]
B 2
C
∆Ξ̃
=B .
C . (10)
..
..
..
..
@ ..
A
.
.
.
.
[k+1]
∆Ψ̃[k]
∆Ψ̃[k+2]
. . . ∆Ψ̃[k+(Υ−1)]
s
s ∆Ψ̃ s
s

a) Convolutional layers with quantization: The convolutional feature extraction follows:
0
1
M−1 X
N−1
X
h[l+1] (x) = AF @
(11)
θi[l]j × xi[l]j + Bias[l] A ,
j=0 i=0

with weights and activations quantized post-training:
'
$
'
$ [l]
θi j − min(θ[l] )
A[l] − min(A[l] )
[l]
[l]
, Â =
θ̂i j =
∆[l]
∆[l]
A
with corresponding quantization steps:

[l]
[l]
[l]
θmax
− θmin
A[l]
max − Amin
[l]
,
∆
.
(13)
=
A
2n − 1
2n − 1
b) Layer normalization and max pooling: Layer normalization stabilizes activations:
X − µX
,
Z norm = γX + β,
(14)
X = q
2
σX + 

∆[l] =

followed by max pooling for spatial downsampling.
2) Fully Connected Layer With Quantization: Fully connected operations follow:

[SPS]

The intrusion detector takes ∆Ξ̃
as its input. The core
purpose of the detector is to recognize deviations between
normal and malicious packets by analyzing the pattern of
packet changes. To achieve this, each input matrix ∆Ξ[SPS]
is labeled based on its corresponding network activity, where
normal traffic is assigned a benign label, and attack patterns are
categorized accordingly. The details of the labeling process for
both binary and multi-class traffic classification are provided
in Subsection III-C.
B. Intrusion Detector
Our proposed intrusion detector, TCNnet, is a lightweight
Tiny Convolutional Neural Network tailored for networktraffic intrusion detection. It extracts spatial features using
stacked convolutional layers, followed by layer normalization
and max pooling to preserve salient patterns while improving
generalization. The complete workflow, including post-training
quantization, is shown in Fig. 3.
1) Tiny Convolutional Neural Network (TCNnet): TCNnet
consists of convolutional, normalization, pooling, and fully
connected layers, all quantized post-training using TensorFlow
Lite to reduce model size and inference latency. The core
operations for each layer are summarized below.

(12)

A = θ X + B,

(15)

with quantized weights and activations:




θ − min(θ)
A − min(A)
θ̂ =
,
Â =
,
∆θ
∆A

(16)

where
θmax − θmin
Amax − Amin
,
∆A =
.
n
2 −1
2n − 1
A ReLU activation is applied afterward:
∆θ =

A0 = max(0, Â).

(17)

(18)

3) Output Layer and Softmax: The final logits are computed as:
Y f = θˆf Â0 + B f ,
(19)
with quantized output weights:


θ f − θ f ,min
θ f ,max − θ f ,min
θ̂ f =
,
∆θ f =
.
∆θ f
2n − 1

(20)

Softmax yields class probabilities:
i

P(Ŷ)i = P

eY f

C
Y fj
j=1 e

.

(21)

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ADIL et al.: FEDERATED AND QUANTIZED-BASED INTRUSION DETECTION

5

Fig. 4. Illustration of proposed collaborative learning framework with adaptive momentum-aware aggregation strategy.

4) Loss Function:
Cross-Entropy:
L=−

Training
C
X

minimizes


Yi log P(Ŷ)i .

Categorical

(22)

i=1

Overall, TCNnet applies quantization to all major layers
(convolutional, normalization, and fully connected), significantly reducing memory and computation while preserving
detection accuracy, making it suitable for deployment in
resource-constrained environments.
C. Privacy-Preserved Collaborative IDS
The next module of the framework is the collaborative
learning stage, illustrated in Fig. 4. The CVF aggregator
initializes the TCNnet detector and broadcasts it to all edge
vehicles. Each vehicle preprocesses its local traffic using
NTTE (Section III-A), producing traffic images for TCNnet.
These images are then labeled using two criteria: (i) binary
(normal vs. attack) and (ii) multi-class (specific attack types),
formally defined in Algorithms 1 and 2. The labeled images
are used to train TCNnet locally, after which each vehicle
sends its model updates to the aggregator. The aggregator fuses

Algorithm 1 Labeling Criteria for Binary Traffic (AEID) Υ
Is the Window Size, ∆Ξ[SPS] Is a Group of Malicious Packets,
and Ξ[Υ] Is a Stream of Raw Packets
1: procedure L ABEL PACKETS (Ξ[Υ] , Υ, ∆Ξ[SPS] )
2:
Initialize an empty set to store labels for Υ: Γ ← {}
3:
for each window wi of size Υ ∈ Ξ[Υ] = [0, . . . , n − 1] do
4:
Check if wi contains any packet in ∆Ξ[SPS]
5:
if wi ∩ ∆Ξ[SPS] , {} then
6:
Assign binary label: Γwi ← [0, 1] .[Normal, Attack]
7:
else
8:
Assign binary label: Γwi ← [1, 0] .[Normal, Attack]
9:
end if
10:
Append the label to the set of labels: Γ ← Γ∪{(wi , Γwi )}
11:
end for
12:
return Γ
13: end procedure

the received updates and redistributes the refined global model.
This process repeats iteratively until convergence or until a
predefined performance threshold is met.
Let’s assume a vehicular network consisting of a set of edge
vehicles denoted as D = {1, 2, 3, . . . , n}, where each vehicle di

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
6

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Algorithm 2 Labeling Criteria for Multi-Class Traffic (TOW)
Υ Is the Window Size, A Is a Set of Attack Types, and Ξ[Υ]
Is a Stream of Raw Packets
1: procedure L ABEL PACKETS (Ξ[Υ] , Υ, A)
2:
Initialize an empty set to store labels for Υ: Γ ← {}
3:
for each window wi of size Υ ∈ Ξ[Υ] = [0, . . . , n − 1] do
4:
Initialize one-hot vector: Γwi ← [1, 0, . . ., 0] .Default is
Normal
5:
for each attack type a j in A do
6:
if wi ∩ a j , {} then
7:
Set attack label: Γwi [ j] ← 1, Γwi [0] ← 0
8:
break
9:
end if
10:
end for
11:
Append the label to the set of labels: Γ ← Γ∪{(wi , Γwi )}
12:
end for
13:
return Γ
14: end procedure

where

[di ]
i]
∂Loss(Ξ[d
i , Γi ; θ)
.
(29)
∂θ
Instead of using the entire traffic image dataset in each
optimization step, a subset of traffic images, denoted by
S ⊂ {1, 2, . . . , n}, is randomly chosen at each iteration. This
results in a modified loss function that focuses only on the
selected subset is defined as:

di (θ) =

min FS (θ),

(30)

θ∈Rd

where
FS (θ) =

1 X
[di ]
i]
Loss(Ξ[d
i , Γi ; θ),
nS

(31)

i∈S

with nS representing the total number of selected traffic
images, nS = |S|.
We also compute the gradient d only for the selected traffic
images. This gradient for the subset can be represented as:
1 X
di (θ),
(32)
dS (θ) = ∇FS (θ) =
nS
i∈S

holds a set of traffic packets represented as:
[di ]
[di ]
[di ]
i]
Ξ[di ] = {Ξ[d
1 , Ξ2 , Ξ3 , . . . , Ξn }

(23)

These traffic flows are processed by NTTE to generate traffic
images for intrusion detection. Each image is represented
by a feature matrix Ξ[dj i ] that encodes the key characteristics
distinguishing normal and attack behaviors. Thus, each vehicle
di maintains a dataset of labeled traffic images defined as:
D[di ] = {(Ξ[dj i ] , Γ[dj i ] ) | j = 1, 2, . . . , M [di ] },

(24)

where Ξ[dj i ] is the feature matrix corresponding to the j-th
traffic image, and Γ[dj i ] represents its attack type label. The
total number of traffic images stored in each vehicle is given
by M [di ] = |D[di ] |.
For a detection task, the attack label Γ[dj i ] is represented as
a one-hot encoded vector:
[di ]
[di ]
i]
Γ[dj i ] = [Γ[d
[ j,0] , Γ[ j,1] , . . . , Γ[ j,Ω−1] ],

(26)

θ∈Rd

where

M

F(θ) =

1 X
[di ]
i]
Loss(Ξ[d
i , Γi ; θ),
M

(27)

i=1

[di ]
i]
and Loss(Ξ[d
i , Γi ; θ) is the loss function computed for the
[di ]
i]
feature matrix Ξi and its corresponding attack label Γ[d
with
i
respect to the TCNnet parameters θ.
A gradient update involves computing the gradient of F(θ),
which can be expressed as:
M

dmean (θ) = ∇F(θ) =

1 X
di (θ),
M
i=1

F(θ) = arg min
θ∈Rd

where
Fdi (θ) =

n
X
D[di ]
i=1

D

Fdi (θ),

1 X
Loss(Ξ[dj i ] , Γ[dj i ] ; θ).
D[di ]
[d ]
j∈M

(33)

(34)

i

In this revised formulation, rather than computing the loss
function by averaging
P M over a local set of M traffic images,
Fi (θ), we first compute the individual
expressed as M1 i=1
loss function for each edge vehicle di . The local objective
function for a given vehicle di is defined as:
M [di ]

(25)

where Ω is the total number of attack types.
DL-based intrusion detectors are trained by minimizing
an objective function, where the overall loss aggregates the
errors across all training samples. This optimization process
is expressed as follows:
min F(θ),

The earlier loss function applies to a single vehicle di . In the
collaborative setting, multiple vehicles participate in training;
thus, the loss must be extended to a set of n contributing
vehicles, expressed as:

(28)

1 X
Fdi (θ) = [d ]
Loss(Ξ[dj i ] , Γ[dj i ] ; θ).
|D i |

(35)

j=1

Following this, a weighted aggregation is performed over
all participating n vehicles, where the weight assigned to each
vehicle is proportional to the number of traffic images |D[di ] |
it possesses.
For each vehicle di , an input sample Ξ[dj i ] is transformed into
[SPS]
a network traffic image, denoted as ∆Ξ̃
∈ R(Υ−1)×s-bytes .
[di ]
The corresponding output label Γ j is represented as a onehot encoded vector in RΩ , where Ω is the total number
of attack categories. Each vehicle maintains a local dataset
D[di ] , consisting of M[di ] labeled traffic samples. To minimize
its empirical risk, each vehicle independently optimizes its
local objective function. The overall global empirical risk,
considering all participating vehicles, is expressed as:
F(θ1 , . . . , θn ) = arg min

[d ]

n
X
|D[di ] |

θi ∈R|D i | i=1

|D|

Fdi (θ).

(36)

Before the commencement of the initial communication
round in our collaborative learning paradigm, an aggregator

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ADIL et al.: FEDERATED AND QUANTIZED-BASED INTRUSION DETECTION

at CVF initializes the TCNnet model and disseminates it to
all selected edge vehicles in the network, formally defined as:
θdi ← θ[global] ,

(37)

where θ[global] represents the global TCNnet parameters, while
θdi refers to the local TCNnet parameters assigned to each
edge vehicle di . Beyond maintaining individual vehicle loss
function as formulated in Eq. 35, each vehicle must compute
its gradient to facilitate parameter updates. Within this collaborative framework, the local gradient ∇Fdi is computed over
the vehicle’s private dataset as:
1 X
∇F j (θ).
(38)
∇Fdi (θ) = [d ]
|D i | j
Subsequently, the global gradient ∇F [global] across all participating vehicles is derived using an adaptive momentum-aware
aggregation strategy:
[global]

∇Ft

=

n
X
|D[di ] | h
i=1

|D|

[global]

β · ∇Ft−1

i
+ (1 − β) · ∇Fd(t)i (θ) ,
(39)

where β ∈ [0, 1) is the momentum coefficient and t is the
current communication round. This aggregation balances past
and recent gradients, improving stability and convergence
under non-IID, heterogeneous vehicular data, and enabling a
more robust global IDS model.
These steps are repeated for a fixed number of iterations.
Algorithm 3 summarizes the full collaborative IDS framework,
integrating NTTE, TCNnet, and the privacy-preserved federated learning process.
D. Transportation Impact Modeling Module (TIMM)
To formally connect network-level intrusion detection outputs to vehicle-level safety and traffic-flow indicators, we
introduce a Transportation Impact Modeling Module (TIMM).
TIMM consists of (i) a discrete-time longitudinal vehicle dynamics model with perception channel modeling that
captures corrupted/filtered V2X/CAM information; (ii) a
probabilistic attack–detection timing model that uses IDS performance statistics (TPR, FPR, tdet ); and (iii) aggregation rules
that map vehicle-level events to network-level flow metrics.
We adopt discrete-time notation with sampling interval ∆t > 0.
Let time indices be k ∈ N and physical time t = k∆t.
1) Vehicle State and Controller Model: Consider a platoon/vehicle string of N vehicles indexed by i = 1, . . . , N,
where vehicle i = 1 is the leader. For each vehicle i at time
step k define the state vector:


pi [k]
xi [k] =
,
(40)
vi [k]
with longitudinal position pi and speed vi . The discrete-time
kinematics are:
pi [k + 1] = pi [k] + vi [k]∆t,

vi [k + 1] = vi [k] + ai [k]∆t,
(41)

where ai [k] is the longitudinal acceleration applied by the
vehicle controller.

7

Algorithm 3 Embedded-Optimized Intrusion Detection
1: Procedure CLOUD VEHICLE FUNCTION EXECUTES:
[global]
2: Initialize global model parameters θ0
, communication
round C = 0
3: while not converged or communication rounds C < N do
4:
M ← MAX(K × V, 1) .K = fraction of vehicles selected
per round
5:
S t ← random set of M vehicles
6:
for each vehicle [di ] ∈ {0, 1, . . . , S t − 1} in parallel do
[di ]
7:
θt+1
← LocalUpdate(di , θt[global] ) .Local TCNnet update
8:
end for P
n D[di ] [di ]
9:
θt+1 ←
i=1 D θt+1 .Aggregate updates: weighted
sum, where D[di ] is the local traffic image dataset size
and D is the overall size
10: C ← C + 1 .Proceed to the next Comm. Round
11: end while
12: Procedure EDGE VEHICLE EXECUTES:
[global]
from aggregator
13: Receive TCNnet parameters θt
14: Network Traffic Processing:
15: * Extract traffic packets Ξ[di ]
16: * Transform packets into network traffic images dataset:
D[di ] ← NTTE(Ξ[di ] )
Label images using appropriate algorithm:
if TrafficType == Binary then
19:
Γ[di ] ← BinClass(Ξ[di ] ) (refer to Algorithm 1)
20: else
21:
Γ[di ] ← MultiClass(Ξ[di ] ) (refer to Algorithm 2)
22: end if
23: TCNnet Model Training:
[d ]
24: Initialize TCNnet model θt i from aggregator
v
25: Split labeled dataset M into batches of size S
26: for each local epoch i ∈ {0, 1, . . . , E − 1} do
27:
for each mini-batch s ∈ S do
i]
28:
Compute gradient: g[d
s ← ∇ Loss(θt ; s)
[di ]
i]
29:
Local update: θt+1 ← θt[di ] − η × g[d
s
30:
end for
31: end for
[di ]
32: Send updated TCNnet θt+1
to CVF
33: Post-Training Quantization:
34: Optimize TCNnet for embedded deployment:

17:
18:

[di ]
[di ]
← Quantize(θt+1
)
θt+1

35:

End Procedure

We use a perception-based linear car-following controller
[20] (suitable for ADAS/platoon controllers). Let the controller
command be:
ai [k] = K p (v̂i−1→i [k] − vi [k]) + Kh s? − si [k]



(42)

where:
• si [k] = pi−1 [k] − pi [k] is the gap to the preceding vehicle,
• s? is the desired spacing (safe headway),
• K p , Kh > 0 are the control gains,

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
8

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

• v̂i−1→i [k] is the perceived speed of the preceding vehicle
at vehicle i (this may be derived from received CAM/V2X
messages or local sensing.)
Perception Channel Model: The perceived speed of the
preceding vehicle v̂i−1→i [k] equals the true speed vi−1 [k] unless
an attack has corrupted the information or the IDS has filtered
it:
8
ˆ
<ṽi−1 [k], if a malicious message is received
v̂i−1→i [k] =
at k and not yet mitigated,
ˆ
:v [k], otherwise.
i−1
(43)
Here ṽi−1 [k] is the attacker-specified (spoofed) value. IDS
actions (detection + mitigation) can restore correct perception
by blocking or flagging corrupted CAMs. False positives
can also cause legitimate messages to be dropped, producing
delayed perception updates (stale values).
2) Attack and IDS Timing Model: Model an attack instance
arriving at time t0 . Let tdet denote the IDS detection latency
for that instance, and let Ft (τ) be the Cumulative Distribution
Function (CDF) of detection latency. Formally define:
• tc : critical time window for which corrupted perception
can cause an unsafe control action (time-to-act). For a
particular follower i, tc can be approximated by the TimeTo-Collision (TTC) threshold or the controller reaction
window (see Section V).
• Iharm = 1{tdet ≥ tc }: indicator that detection is too late to
prevent harm. More generally, if the latency is random:
P(tdet ≥ tc ) = 1 − Ft (tc ).

(44)

Assume the IDS correctly identifies an attack with probability
equal to the recall/TPR and falsely flags a benign message
with probability FPR. We model the effect of IDS+mitigation
as instantaneous upon detection.
Let A denote an attack event; for a single attack, the
probability that the attack remains effective (i.e., causes the
vehicle to act on corrupted perception before mitigation) is:
Peff = P(A) · (1 − TPR · Ft (tc )) ,

(45)

where P(A) is the probability that the message is manipulated
(given prevalence). For point estimates using mean latency t¯det
and deterministic threshold:
Peff ≈ P(A) · (1 − TPR · 1{t¯det < tc }) .

(46)

If the attack is effective for time window T eff = min(tc , tdet )
(i.e., until detection or until critical harm occurs), the follower
may execute a sequence of corrupted control updates during
dT eff /∆te steps.
3) Collision Likelihood for a Vehicle Pair: For a follower
i, define the instantaneous time-to-collision (TTC) under perceived data as:
si [k]
,
(47)
TTCi [k] =
max(0, vi [k] − v̂i−1→i [k]) + 
with small  > 0 to avoid division by zero. A collision
is declared at step k if si [k] ≤ smin (vehicle overlap) or
TTCi [k] < τcrit . This definition yields a binary collision
outcome per realization, while the overall collision likelihood

Pcoll|A remains probabilistic, as it depends on the stochastic
nature of perception errors and detection latency.
For probabilistic analysis, the conditional probability that
an ongoing effective attack leads to a collision within horizon
H is given by:
Pcoll|A = P ∃k ∈ {k0 , . . . , k0 + H} :

TTCi [k] < τcrit | A effective ,

(48)

which represents the general probabilistic formulation. In
practice, we employ two complementary approaches: (i) an
analytical conservative bound based on deterministic gapclosing time, and (ii) a numerical estimation via discrete-time
propagation under stochastic delay and corrupted velocity
perception for tightened scenario evaluation. Analytical bound
(conservative): If the attacker causes a perceived speed reduction such that the relative velocity ∆v = vi − ṽi−1 > 0, the
time until the inter-vehicle gap closes is approximately si /∆v.
If the detection latency tdet exceeds this time, a collision
is deemed inevitable. Hence, this condition defines a binary
outcome (collision or no collision), producing a conservative
probabilistic bound:

si 
· TPR.
(49)
Pcoll|A & Pr tdet ≥
∆v
This conservative bound is complemented by a Monte
Carlo–based evaluation that incorporates stochastic communication delay, braking dynamics, and varying end-to-end
latency to obtain a more realistic continuous estimate of Pcoll|A .
4) Aggregation to Fleet-Level Collision Likelihood and
Flow Effects: Let the attack arrival rate (per vehicle) be λA
(attacks/sec) and consider the time horizon T. The expected
number of attack attempts in a fleet of N vehicles is NλA T .
Under independence, expected collisions in the horizon T are:
E[Ncoll ] ≈ NλA T · Peff · Pcoll|A .

(50)

Use the conservative bound for Pcoll|A above when analytic
tractability is required.
Flow-level effect (Vehicle Flow Efficiency, VFE): Let baseline flow (no attack) at link be q0 = k0 · v0 (vehicles/hr), where
k0 is density and v0 average speed. Each collision or critical
event causes a local disruption of duration T disr and reduces
throughput by δq during disruption. Then the expected mean
flow reduction over T is:
∆q ≈

E[Ncoll ] · δq · T disr
,
T

and

VFE = 1 −

∆q
.
q0

(51)

For small E[Ncoll ], linearization yields VFE close to 1.
5) IDS-Induced Message Loss and False-Positive Consequences: Let the total messages in the horizon T be M, of
which a fraction pattack is malicious. Using IDS confusion
terms:
• True positives (TP): TP ≈ M pattack · TPR
• False positives (FP): FP ≈ M(1 − pattack ) · FPR
If IDS mitigation blocks messages flagged as malicious, the
Safety Message Delivery Ratio (SMDR) for legitimate safety
messages is:
SMDR =

M(1 − pattack ) − FP
= 1 − FPR.
M(1 − pattack )

(52)

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ADIL et al.: FEDERATED AND QUANTIZED-BASED INTRUSION DETECTION

(If mitigation causes delay instead of drop, model delay
effects below.)
If mitigation introduces additional per-message processing
delay dproc , and dropped/flagged messages are retransmitted or
suppressed, the effective average CAM latency becomes:
d̄cam = dnet + FPR · dproc

9

TABLE I
AEID DATASET D ETAILS FOR D IFFERENT N ETWORK S CENARIOS

(53)

where dnet is base network latency. Increased CAM latency
can increase TTC uncertainty; incorporate via inflated tc or
larger  in TTC.
6) Summary: TIMM Input-Output Mappings: Collectively,
TIMM yields closed-form or computable mappings from IDS
performance to transportation impact metrics:
• Extra travel distance during detection: ∆d = v tdet
• Probability an attack remains effective: Peff ≈ pattack (1 −
TPR · Ft (tc ))
• Expected collisions per time: E[Ncoll ] ≈ NλA Peff Pcoll|A
• Safety Message Delivery Ratio: SMDR = 1 − FPR (if
blocked messages are primary mitigation)
E[Ncoll ] · δq · T disr
• Vehicle Flow Efficiency: VFE = 1 −
q0 T
All mappings are parameterized by scenario variables
{v, s? , si [0], ∆t} and IDS variables {TPR, FPR, t¯det , Ft (·)}. In
Section IV, we define the evaluation metrics, and in Section V,
we present parametric sweeps and results.

TABLE II
TWO-IDS DATASET D ETAILS FOR D IFFERENT T RAFFIC
I MAGE S IZES AND ATTACK T YPES

realistic assessment of the detector’s robustness and its ability
to generalize to unseen traffic patterns.

IV. E XPERIMENTAL D ETAILS
This section outlines the datasets used in our evaluation,
followed by the architectural and training configuration of
TCNnet. All experiments were conducted on a standard workstation equipped with an Intel Core i9 CPU and 32 GB of
RAM, using Python with TensorFlow, Keras, Pandas, and
NumPy in a lightweight, resource-efficient setup suitable for
deployment on edge vehicles.
A. Datasets Detail
We evaluate the proposed framework using two realworld benchmark datasets: the Automotive Ethernet Intrusion
Dataset (AEID) [19] and the TOW dataset [21]. AEID contains
port-mirrored 100BASE-T1 traffic from a vehicle-mounted
camera in both driving and non-driving scenarios, with replay
attacks generated from 36 recorded packets. TOW provides
100BASE-T1 traffic with five attack types: replay, frame injection, MAC flooding, PTP manipulation, and CAN DoS, with
each packet labeled as normal or attack. To assess scalability,
we evaluate TCNnet using multiple NTTE-generated trafficimage sizes (Ξ[32×32] , Ξ[60×60] , Ξ[116×116] , Ξ[452×452] ). For the
TOW dataset, we apply data augmentation consisting of centering, standard normalization, a 20◦ rotation, and width/height
shifts of 0.2 to improve generalization.
In our experimental setup, we use these datasets to evaluate
TCNnet under diverse network scenarios and image sizes.
Tables I and II summarize the dataset compositions, including normal and attack traffic across conditions. To emulate
realistic deployment, five edge vehicles participate in privacypreserving collaborative learning, each training on a distinct
data partition. This introduces natural distribution shifts across
scenarios, attack types, and image resolutions, enabling a

B. TCNnet Architectural and Experimental Settings
TCNnet is designed as a lightweight intrusion detector for
OVNs, combining convolutional layers for feature extraction
with layer normalization for stable training. We adopt a twolevel learning strategy: edge vehicles train using the Adam
optimizer with a learning rate of 0.01, while the aggregator
updates the global model with a learning rate of 0.05. The
number of communication rounds is adjusted per dataset and
scenario to ensure stable convergence. Architectural details,
hyperparameters, and training settings are summarized in
Table IV.
C. Evaluation Metrics
1) Standard IDS Performance Metrics: We evaluate TCNnet using standard intrusion detection metrics: Accuracy
(ACC), Precision (PRE), Recall (REC), Area Under the Curve
(AUC), False Positive Rate (FPR), True Positive Rate (TPR),
and detection latency (tdet ) [26].
2) Transportation Impact Assessment: To quantitatively
evaluate the real-world safety and efficiency consequences of
cyber-attacks and our IDS, we employ the proposed TIMM.
This analytical framework establishes formal mappings from
IDS performance metrics (TPR, FPR, latency) to critical
transportation-level outcomes, including SMDR, collision likelihood, and VF, as detailed in Section III-D. The car-following
dynamics and controller model within TIMM are grounded in
established Adaptive Cruise Control research [22], [23]. The
safety assessment is based on the formalized TTC metric, a
recognized standard for collision risk analysis [24], while the
overall cybersecurity-to-safety evaluation addresses a critical
gap identified in connected vehicle security [25]. The specific

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
10

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

TABLE III
PARAMETERS FOR TIMM-BASED I NTRUSION I MPACT E VALUATION

TABLE V
P ERFORMANCE E VALUATION OF TCN NET OVER M ULTIPLE C OMMUNI CATION ROUNDS ON THE AEID DATASET FOR N ON -D RIVING AND
D RIVING S CENARIOS . T HE R ESULTS S HOWCASE ACC, PRE, REC,
AUC, AND L OSS AT D IFFERENT ROUNDS OF THE
L EARNING P ROCESS

privacy-preserved collaborative learning framework. Second,
to assess the resource efficiency of TCNnet from various
aspects and its feasibility. Third, to conduct a comparative
analysis against state-of-the-art methods.
A. Detection Results of Proposed Framework

TABLE IV
H YPERPARAMETERS AND I MPLEMENTATION D ETAILS

The experimental setup for TCNnet employs collaborative
learning, where the aggregator initializes the model and edge
vehicles, denoted as N, update it in a privacy-preserving
manner by sharing only model parameters. For evaluation, we
set N = 5 for AEID and N = 10 for TOW to cover diverse
deployment scenarios.
For AEID, TCNnet converged in 100 rounds for the nondriving scenario due to complex, varied attack patterns, and
in 20 rounds for the driving scenario with more structured
attacks. Upon convergence, non-driving results were ACC
99.86%, PRE 99.73%, REC 99.82%, AUC 99.91%, and loss
0.008; driving results were ACC 99.98%, PRE 99.99%, REC
99.93%, AUC 99.99%, and loss 0.001. Detailed results across
rounds are presented in Table V, confirming TCNnet’s effectiveness in learning attack patterns while preserving privacy.
TCNnet was evaluated across multiple NTTE-generated traffic
image sizes to assess adaptability to diverse protocols. Sizes
ranged from 32 × 32 to 452 × 452. For 32 × 32 and 60 × 60,
learning was smooth, with convergence in 50 and 15 communication rounds, respectively. Accuracy reached 99.99%, with
precision slightly lower at 99.95% for 32 × 32. For 116 × 116,
initial fluctuations stabilized after 30 rounds, achieving ACC
99.99%, PRE 99.95%, REC 99.99%, and AUC 99.99%. The
largest size, 452 × 452, showed significant early fluctuations
(ACC 55% in the first 10 rounds) but eventually reached
99.99% across all metrics. Detailed results across rounds and
image sizes are summarized in Table VI.
B. Embedded-Optimized Quantized TCNnet

parameter settings for the Urban, Suburban, and Highway
scenarios are provided in Table III.
V. P ERFORMANCE E VALUATION
In this section, we assess the performance of the proposed framework. Our experimental objectives are threefold:
first, to build, train, and evaluate the TCNnet within a

Designing a tiny intrusion detection model is only half
the challenge; ensuring that it remains highly effective after
quantization is equally important. To enable deployment
in resource-constrained on-board automotive networks, we
quantized TCNnet into Q-TCNnet using TensorFlow Lite,
converting all FP32 weights into 8-bit INT8 representations
through post-training quantization. Despite this substantial
reduction in numerical precision, Q-TCNnet preserves performance extremely well: as summarized in Table VII, accuracy,

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ADIL et al.: FEDERATED AND QUANTIZED-BASED INTRUSION DETECTION

11

TABLE VI

TABLE VIII

P ERFORMANCE E VALUATION OF TCN NET OVER M ULTIPLE C OMMU NICATION ROUNDS ON THE TOW DATASET IN A C OLLABORATIVE
L EARNING S ETTING FOR D IFFERENT T RAFFIC I MAGE S IZES . T HE
TABLE P RESENTS ACC, PRE, REC, AUC, AND L OSS FOR E ACH
S IZE AT VARIOUS ROUNDS OF THE L EARNING P ROCESS

C OMPARISON OF D IFFERENT IDS M ODELS ON AEID
AND TOW DATASETS

TABLE VII
P ERFORMANCE AND R ESOURCE C OMPARISON
OF TCN NET AND Q-TCN NET

precision, recall, and AUC decrease by only 0.04% or less.
Conversely, quantization yields major resource savings. Storage requirements drop by more than 90% (2.81 MB to
0.23 MB), and memory usage is reduced by over 51%
(0.91 MB to 0.44 MB). These reductions make Q-TCNnet
highly suitable for real-time, embedded deployment within
on-board automotive networks where computational and memory budgets are tightly constrained.
C. Comparison With Existing SOTA Methods
We evaluated our proposed IDS by comparing its performance against state-of-the-art (SOTA) methods. The evaluation was based on key performance metrics, including ACC,
PRE, REC, and AUC. These comparative results were taken
directly from the literature to maintain consistency with the
original studies and ensure transparency, providing readers
with an accurate reference for performance benchmarking. For
the AEID dataset, we conducted a comprehensive performance
comparison against SOTA methods, including those presented
in [16], [19], [27], and [28]. For the first three SOTA methods
[16], [27], [28], we were able to compare performance only
within the driving scenario due to the unavailability of nondriving network scenario results. However, for the fourth
method [19], we compared performance in both scenarios
using all key metrics.
In the driving scenario, our proposed TCNnet and its
quantized version (Q-TCNnet) outperformed the most recent
multi-stage method [16]. TCNnet achieved an ACC of 99.99%,
while Q-TCNnet obtained 99.96%, both surpassing the 97.97%

ACC of the multi-stage IDS by over 2%. Moreover, our models
demonstrated superior AUC scores, with TCNnet achieving
99.99% and Q-TCNnet 99.98%, compared to 97.89% for
the multi-stage approach. These results were obtained despite
running only 10 epochs at the edge vehicle level, considering
resource constraints in real-world environments.
In the network scenario, our TCNnet and Q-TCNnet models performed exceptionally well, significantly outperforming
the V-2DCNN [19] across all performance metrics. TCNnet
achieved an ACC of 99.84% and Q-TCNnet 99.82%, compared to 96.55% for V-2DCNN. Furthermore, our collaborative
learning framework provides an adaptive advantage, allowing
edge vehicles to share attack patterns in a privacy-preserving
manner, enhancing detection capabilities over time.
For the TOW dataset, both TCNnet and Q-TCNnet performed exceptionally well across all traffic image sizes. For
the Ξ[32×32] image size, our models achieved ACC scores of
99.98% and 99.94%, respectively, significantly outperforming
the 92.32% of the TOW-based IDS by over 7.5%. Similarly, for
Ξ[60×60] , our models achieved a 2.58% and 2.53% higher ACC
than the TOW-based approach. For Ξ[116×116] , both models
outperformed the baseline by over 3.8%. At the Ξ[452×452] size,
our models achieved 99.98% and 99.96% ACC, outperforming
the multi-stage IDS (97.62%) and the TOW-based approach
(97.87%) by more than 2%. The FASS method also performed
significantly lower; however, its semi-supervised nature provides a different learning advantage. Detailed comparison
results for both datasets can be found in Table VIII.
These results highlight the robustness of our collaborative
learning framework, demonstrating its ability to detect and
adapt to new attack patterns effectively in resource-constrained
environments.
D. ROC and Latency Evaluation of TCNnet
To evaluate the operational sensitivity of the proposed
TCNnet detector, we computed the TPR, FPR, and inference
latency per packet size across multiple decision thresholds.
As summarized in Table IX, TCNnet maintains near-zero

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
12

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Fig. 5. Performance evaluation of the proposed TCNnet on the AEID dataset across different network scenarios.

Fig. 6. Performance evaluation of the proposed TCNnet on the TOW dataset across different traffic image sizes.

TABLE IX
ROC P OINTS OF THE P ROPOSED TCN NET D ETECTOR
AND AVERAGE L ATENCY

false alarms (FPR < 0.001) at high thresholds while gradually improving TPR from 64.7% to 98.4% as the threshold
is relaxed. This behavior reflects a stable and discriminative model, capable of maintaining detection reliability even
under varying operating points. The consistent latency of
0.086 ms demonstrates TCNnet’s feasibility for real-time ITS
deployment, where ultra-low delay is essential for safetycritical decision loops. These results represent the average
performance of TCNnet across both AEID and TOW datasets,

covering diverse packet sizes and network scenarios. Such
cross-domain consistency highlights the robustness of the
collaborative learning setup and provides a realistic view of
detector behavior under different ROC operating points. These
baseline results are critical for assessing the practicality of
the proposed IDS in intelligent transportation systems, and
serve as the foundation for subsequent subsections analyzing
its network-level impact through TIMM-based simulations.
E. TIMM-Based Evaluation of the Proposed IDS
To assess the effectiveness of the proposed IDS in realistic vehicular conditions, we performed extensive simulations
using the TIMM framework across three representative traffic
scenarios: Urban, Suburban, and Highway. The analysis considered N = 1000 vehicles over a 1-hour window (T = 3600 s)
with detailed parameters provided in Table III.
Fig. 8 and Fig. 7 present the core relationship between
IDS performance metrics and safety outcomes across all
ROC operating points derived from our model validation
(Table IX). Fig. 8 shows that collisions increase gradually with
higher false positive rates, particularly in Highway scenarios
where the impact is most pronounced due to higher speeds
and attack probabilities. Conversely, Fig. 7 demonstrates the

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ADIL et al.: FEDERATED AND QUANTIZED-BASED INTRUSION DETECTION

13

TABLE X
S CENARIO -L EVEL S UMMARY OF IDS P ERFORMANCE AT ROC P OINTS .
T HE C OLLISION VALUES AND R EDUCTION P ERCENTAGES I NCLUDE ±
VARIATION F ROM M ONTE C ARLO S IMULATIONS
W ITH 1000 R EPETITIONS

Fig. 7. Collisions avoided vs TPR at ROC Points for different traffic scenarios.

Fig. 8. Collisions avoided vs FPR at ROC points for different traffic scenarios.

Fig. 9. Safety-Efficiency Trade-off: Vehicle Flow Efficiency (VFE) vs.
Collisions Avoided across ROC operating points. Higher TPR values achieve
better safety without compromising efficiency.

critical importance of detection sensitivity, with collision
counts dropping sharply as TPR approaches 0.95 across all
scenarios, highlighting the threshold beyond which substantial
safety benefits are achieved. Moreover, the fundamental safetyefficiency trade-off is further examined in Fig. 9, which
reveals that optimal operating points (TPR > 0.95) simultaneously maximize both collision avoidance and traffic flow
efficiency. This demonstrates that our IDS achieves safety
improvements without the typical efficiency penalties observed
in conservative security systems. The color gradient (TPR)
shows that higher detection sensitivity correlates with superior
performance across both safety and efficiency metrics.

TABLE XI
P ER -S CENARIO S UMMARY OF IDS P ERFORMANCE BY S WEEP T YPE

As shown in Table X, when evaluated at the top-performing
ROC points (average TPR = 0.98, FPR = 0.0122, latency =
0.1 ms), the proposed IDS achieves remarkable safety
improvements. In Highway traffic, the system reduces expected
collisions from 36 to 0.76 per hour, corresponding to a
97.9% ± 1.2% reduction while maintaining high Vehicle
Flow Efficiency (VFE = 0.949) and Safety Message Delivery
Ratio (SMDR = 0.988). Suburban conditions show equally
strong performance with collisions decreasing from 13.5 to
0.29 (97.9% ± 1.1% reduction), VFE of 0.981, and SMDR
of 0.991. Urban traffic benefits most in relative terms, with
collisions dropping from 3.24 to 0.07 (97.9% ± 1.0% reduction) and near-perfect VFE (0.995) and SMDR (0.994). These
results, obtained from Monte Carlo simulations with 1000 repetitions, demonstrate consistent high-performance operation.
These observed safety improvements are consistent with the
probabilistic collision model Pcoll|A , confirming that higher
TPR and lower detection latency directly reduce the probability of collisions under realistic traffic scenarios.
To further examine the robustness of our approach, we
conducted sensitivity analyses through expanded parameter
sweeps summarized in Table XI. The expanded FPR sweep
(FPR 0-0.20) reveals that even under artificially high false
positive conditions, collision avoidance remains substantial
(32.40-36.00 for Highway), demonstrating system resilience.
The TNR-based sweep shows similar robustness, while the
ROC operating points analysis confirms that proper threshold
selection is crucial for maximizing safety benefits, with performance varying significantly across the ROC curve (collision
avoidance range:34.87–35.60 for Highway). Across all sweep
types, the IDS maintains excellent VFE (> 0.88) and SMDR
(> 0.90), confirming that traffic efficiency and communication reliability are preserved even under suboptimal operating
conditions.
VI. C ONCLUSION
This work presented a privacy-preserving, embeddedefficient collaborative IDS framework for securing hybrid
OANs. The NTTE module transforms raw multi-protocol

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
14

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

traffic into temporal images, while TCNnet and its quantized variant Q-TCNnet provide lightweight, high-performance
intrusion detection suitable for resource-constrained ECUs.
Post-training quantization reduced model size by over 90%
and memory usage by 51% with negligible accuracy loss.
Evaluations on AEID and TOW datasets confirmed that both
models outperform state-of-the-art baselines. To bridge network security and real-world safety, we introduced TIMM,
which maps IDS performance to ITS-level outcomes. Simulations across Urban, Suburban, and Highway settings showed
up to 97.9% collision reduction, high VFE (0.949–0.995), and
reliable SMDR (0.988–0.994), demonstrating tangible safety
benefits. Despite these strengths, protocol-specific anomalies,
rare attack types, and full integration with in-vehicle realtime systems remain open challenges. Future work includes
protocol-aware embeddings, generative data augmentation, and
deployment-oriented optimizations for ECUs and automotive
gateways.
R EFERENCES
[1]

T. Inagaki and T. B. Sheridan, “A critique of the SAE conditional
driving automation definition, and analyses of options for improvement,”
Cognition, Technol. Work, vol. 21, no. 4, pp. 569–578, Nov. 2019.
[2] M. H. Khan, A. R. Javed, Z. Iqbal, M. Asim, and A. I. Awad, “DivaCAN:
Detecting in-vehicle intrusion attacks on a controller area network
using ensemble learning,” Comput. Secur., vol. 139, Apr. 2024, Art. no.
103712.
[3] A. Sabry, A. Omar, M. Hammad, and N. Abdelbaki, “AVB/TSN protocols in automotive networking,” in Proc. 15th Int. Conf. Comput. Eng.
Syst. (ICCES), Dec. 2020, pp. 1–7.
[4] IEEE 2016, IEEE Standard for a Transport Protocol for TimeSensitive Applications in Bridged Local Area Networks, IEEE Standard
1722–2016 (Revision of IEEE Standard 1722-2011), 2016, pp. 1–233,
doi: 10.1109/IEEESTD.2016.7782716.
[5] A. Nichelini, C. A. Pozzoli, S. Longari, M. Carminati, and S. Zanero,
“CANova: A hybrid intrusion detection framework based on automatic
signal classification for CAN,” Comput. Secur., vol. 128, May 2023, Art.
no. 103166.
[6] K. Burke. (2019). How Does a Self-Driving Car See? NVIDIA Blog.
Accessed: Jan. 18, 2025. [Online]. Available: https://blogs.nvidia.com/
blog/2019/04/15/how-does-a-self-driving-car-see/
[7] N. Sun, W. Wang, K. Liu, D. Li, and J. Lü, “Hybrid framework for
security evaluation in Internet of Vehicles,” Comput. Secur., vol. 153,
Jun. 2025, Art. no. 104398.
[8] A. Masood, D. S. Lakew, and S. Cho, “Security and privacy challenges
in connected vehicular cloud computing,” IEEE Commun. Surveys Tuts.,
vol. 22, no. 4, pp. 2725–2764, 4th Quart., 2020.
[9] K. Wang, A. Zhang, H. Sun, and B. Wang, “Analysis of recent deeplearning-based intrusion detection methods for in-vehicle network,”
IEEE Trans. Intell. Transp. Syst., vol. 24, no. 2, pp. 1843–1854, Feb.
2023.
[10] S. Rajapaksha, H. Kalutarage, M. O. Al-Kadri, A. Petrovski,
G. Madzudzo, and M. Cheah, “AI-based intrusion detection systems for
in-vehicle networks: A survey,” ACM Comput. Surv., vol. 55, no. 11,
pp. 1–40, Nov. 2023.
[11] F. Milani and C. Beidl, “Cloud-based vehicle functions: Motivation, usecases and classification,” in Proc. IEEE Veh. Netw. Conf. (VNC), Dec.
2018, pp. 1–4.
[12] Y. Jeong, H. Kim, S. Lee, W. Choi, D. H. Lee, and H. J. Jo, “In-vehicle
network intrusion detection system using CAN frame-aware features,”
IEEE Trans. Intell. Transp. Syst., vol. 25, no. 5, pp. 3843–3853, May
2024.

[13] M. H. Shahriar, Y. Xiao, P. Moriano, W. Lou, and Y. T. Hou,
“CANShield: Deep-learning-based intrusion detection framework for
controller area networks at the signal level,” IEEE Internet Things J.,
vol. 10, no. 24, pp. 22111–22127, Dec. 2023.
[14] O. Y. Al-Jarrah, K. E. Haloui, M. Dianati, and C. Maple, “A novel
detection approach of unknown cyber-attacks for intra-vehicle networks
using recurrence plots and neural networks,” IEEE Open J. Veh. Technol., vol. 4, pp. 271–280, 2023.
[15] M. Althunayyan, A. Javed, and O. Rana, “A robust multi-stage
intrusion detection system for in-vehicle network security using
hierarchical federated learning,” Veh. Commun., vol. 49, Oct. 2024,
Art. no. 100837.
[16] L. F. M. da Luz, P. Freitas de Araujo-Filho, and D. R. Campelo, “Multistage deep learning-based intrusion detection system for automotive
Ethernet networks,” Ad Hoc Netw., vol. 162, Sep. 2024, Art. no. 103548.
[17] S. Jeong, H. K. Kim, M. L. Han, and B. I. Kwak, “AERO: Automotive Ethernet real-time observer for anomaly detection in in-vehicle
networks,” IEEE Trans. Ind. Informat., vol. 20, no. 3, pp. 4651–4662,
Mar. 2024.
[18] P. Meyer, T. Häckel, T. Lübeck, F. Korf, and T. C. Schmidt, “A
framework for the systematic assessment of anomaly detectors in timesensitive automotive networks,” in Proc. IEEE Veh. Netw. Conf. (VNC),
May 2024, pp. 57–64.
[19] S. Jeong, B. Jeon, B. Chung, and H. K. Kim, “Convolutional neural
network-based intrusion detection system for AVTP streams in automotive Ethernet-based networks,” Veh. Commun., vol. 29, Jun. 2021, Art.
no. 100338.
[20] E. Yazdani Bejarbaneh, H. Du, and F. Naghdy, “Exploring shared
perception and control in cooperative vehicle-intersection systems:
A review,” IEEE Trans. Intell. Transp. Syst., vol. 25, no. 11,
pp. 15247–15272, Nov. 2024.
[21] M. L. Han, B. I. Kwak, and H. K. Kim, “TOW-IDS: Intrusion
detection system based on three overlapped wavelets for automotive
Ethernet,” IEEE Trans. Inf. Forensics Security, vol. 18, pp. 411–422,
2023.
[22] J. Zhao, Z. Wang, Y. Lv, J. Na, C. Liu, and Z. Zhao,
“Data-driven learning for H∞ control of adaptive cruise control
systems,” IEEE Trans. Veh. Technol., vol. 73, no. 12, pp. 18348–18362,
Dec. 2024.
[23] T. T. Zhang, P. J. Jin, S. T. McQuade, A. Bayen, and B. Piccoli,
“Car-following models: A multidisciplinary review,” IEEE Trans. Intell.
Vehicles, vol. 10, no. 1, pp. 92–116, Jan. 2025.
[24] O. Barhoumi, M. H. Zaki, and S. Tahar, “A formal approach to road
safety assessment using traffic conflict techniques,” IEEE Open J. Veh.
Technol., vol. 5, pp. 606–619, 2024.
[25] A. Abdo, H. Chen, X. Zhao, G. Wu, and Y. Feng, “Cybersecurity on
connected and automated transportation systems: A survey,” IEEE Trans.
Intell. Vehicles, vol. 9, no. 1, pp. 1382–1401, Jan. 2024.
[26] S. Shoukat, T. Gao, D. Javeed, M. S. Saeed, and M. Adil, “Trust
my IDS: An explainable AI integrated deep learning-based transparent threat detection system for industrial networks,” Comput. Secur.,
vol. 149, Feb. 2025, Art. no. 104191. [Online]. Available: https://
www.sciencedirect.com/science/article/pii/S0167404824004966
[27] L. F. M. da Luz, P. F. de Araujo-Filho, and D. R. Campelo, “Multicriteria optimized deep learning-based intrusion detection system for
detecting cyberattacks in automotive Ethernet networks,” in Proc. Anais
do XLI Simpósio Brasileiro de Redes de Computadores e Sistemas
Distribuı́dos, 2023, pp. 197–210.
[28] P. R. X. Carmo, P. F. de Araujo-Filho, D. R. Campelo, E. Freitas,
A. T. de Oliveira Filho, and D. F. H. Sadok, “Machine learning-based
intrusion detection system for automotive Ethernet: Detecting cyberattacks with a low-cost platform,” in Proc. Anais do XL Simpósio
Brasileiro de Redes de Computadores e Sistemas Distribuı́dos, 2022,
pp. 196–209.
[29] K. H. Shibly, M. D. Hossain, H. Inoue, Y. Taenaka, and Y. Kadobayashi,
“A feature-aware semi-supervised learning approach for automotive
Ethernet,” in Proc. IEEE Int. Conf. Cyber Secur. Resilience (CSR), Jul.
2023, pp. 426–431.
PAPER_TEXT
