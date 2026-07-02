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
# [812] StatGraph: Effective In-Vehicle Intrusion Detection via Multi-View Statistical Graph Learning
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
编号：812
题名：StatGraph: Effective In-Vehicle Intrusion Detection via Multi-View Statistical Graph Learning
年份：2025
DOI：10.1109/tmc.2025.3636517
来源：IEEE Transactions on Mobile Computing
PDF：paper/10.1109_TMC.2025.3636517.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：图学习、知识图谱与威胁情报、IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 11
已有代码状态：已下载；StatGraph -> source\StatGraph

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\812.txt
- 原始字符数：90601
- 本次发送字符数：90601
- 是否截断：False

代码包：
- 仓库：StatGraph
  - URL：https://github.com/wangkai-tech23/StatGraph
  - 状态：downloaded
  - 本地目录：source\StatGraph
  - 顶层结构：BaselineModels/、Dataset/、README.md、StatGraph-CarHacking/、StatGraph-ROAD/、requirements.txt
  - 主要语言：Python:48
  - README 标题：StatGraph、StatGraph、StatGraph
  - README 运行线索：
  - 关键文件：{"依赖环境": ["requirements.txt"], "推理/演示入口": ["BaselineModels/CarHacking/CANet/predict-CANet.py", "BaselineModels/CarHacking/EfficientNet/predict-Efficient.py.py", "BaselineModels/CarHacking/MobileNet/predict-MobileV3.py", "BaselineModels/ROAD/CANet/predict-CANet ROAD.py", "BaselineModels/ROAD/EfficientNet/predict-Efficient ROAD.py", "BaselineModels/ROAD/MobileNet/predict-MobileV3 ROAD.py.py", "StatGraph-CarHacking/ModelAdapting/run50_40/predict32.py", "StatGraph-ROAD/ModelAdapting/run400_5/predict32.py"], "数据处理入口": ["BaselineModels/ROAD/process_ROAD_to_fig.py"], "模型定义": ["BaselineModels/CarHacking/MobileNet/model_v3.py", "BaselineModels/ROAD/MobileNet/model_v3.py"], "训练入口": ["BaselineModels/CarHacking/CANet/train-CANet.py", "BaselineModels/CarHacking/EfficientNet/train-Efficient.py.py", "BaselineModels/CarHacking/MobileNet/train-MobileV3.py", "BaselineModels/ROAD/CANet/train-CANet ROAD.py", "BaselineModels/ROAD/EfficientNet/train-Efficient ROAD.py", "BaselineModels/ROAD/MobileNet/train-MobileV3 ROAD.py", "StatGraph-CarHacking/ModelAdapting/run50_40/train32.py", "StatGraph-ROAD/ModelAdapting/run400_5/train32.py"]}
  - 数据集线索：dapt、tor

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 5, MAY 2026

6335

STATGRAPH: Effective In-Vehicle Intrusion Detection
via Multi-View Statistical Graph Learning
Kai Wang , Member, IEEE, Qiguang Jiang , Bailing Wang , Member, IEEE, Yulei Wu , Senior Member, IEEE,
and Hongke Zhang , Fellow, IEEE

Abstract—In-vehicle networks (IVNs) face growing threats from
advanced cyber-attacks, particularly stealthy masquerade attacks
that mimic legitimate message patterns. This paper proposes STATGRAPH, a fine-grained intrusion detection framework based on
multi-view statistical graph learning over the Controller Area
Network (CAN) messages within IVNs. STATGRAPH constructs
two graphs per detection window: a Timing Correlation Graph
(TCG) capturing temporal ID dependencies, and a Coupling Relationship Graph (CRG) modeling short-term contextual relations.
TCG and CRG are further used to generate graph structure encoding payload variations and embedded signal co-occurrence. A
lightweight multi-layered Graph Convolutional Network (GCN)
is then applied to classify each message, leveraging the expressive representations from TCG and CRG. To ensure effectiveness
against diverse attacks, we evaluate STATGRAPH on two real-world
CAN datasets featuring five underexplored masquerade attacks.
Experimental results show that STATGRAPH significantly improves
detection granularity and outperforms state-of-the-art methods,
with F1-score gains of 7% and 22%, while maintaining the highest
accuracy.
Index Terms—Intrusion detection, masquerade attacks, Internet
of Vehicles, in-vehicle network, controller area network, multi-view
statistical graph.

I. INTRODUCTION

A

S A vital component of vehicle-to-everything (V2X) systems, intelligent connected vehicles (ICVs), which are

Received 25 February 2025; revised 6 November 2025; accepted 17 November 2025. Date of publication 24 November 2025; date of current version
6 April 2026. This work was supported in part by TaiShan Scholars under
Grant tsqn202408112, in part by National Natural Science Foundation of China
(NSFC) under Grant 62272129, and in part by Key Laboratory of Cognitive Intelligence and Content Security, Ministry of Education under Grant RZZN202414.
Recommended for acceptance by C. Wang. (Corresponding authors: Kai Wang;
Bailing Wang.)
Kai Wang and Qiguang Jiang are with the School of Computer Science
and Technology, Harbin Institute of Technology, Weihai 264209, China, and
also with the Shandong Key Laboratory of Industrial Network Security, Weihai
264209, China (e-mail: dr.wangkai@hit.edu.cn; jiangqiguang_971@163.com).
Bailing Wang is with the Harbin Institute of Technology (Weihai) Qingdao
Research Institute, Qingdao 266109, China, and also with the Shandong Key
Laboratory of Industrial Network Security, Weihai 264209, China (e-mail:
wbl@hit.edu.cn).
Yulei Wu is with the Faculty of Engineering and the Bristol Digital Futures Institute, University of Bristol, BS8 1QU Bristol, U.K. (e-mail: y.l.wu@
bristol.ac.uk).
Hongke Zhang is with the School of Electronic and Information Engineering, Beijing Jiaotong University, Beijing 100044, China (e-mail: hkzhang@
bjtu.edu.cn).
Code is available at https://github.com/wangkai-tech23/StatGraph.
Digital Object Identifier 10.1109/TMC.2025.3636517

equipped with in-vehicle communication networks and various embedded computing devices, have rapidly proliferated
and become a prevailing trend [1]. With the increasing number of intelligent technologies integrated into vehicles, ICVs
now offer a variety of advanced services and enhanced user
experiences, such as autonomous driving, collision avoidance,
and automated parking assistance. However, these technologies
have also introduced new external attack surfaces to in-vehicle
networks (IVNs), making them more vulnerable to a growing
range of evolving and sophisticated cyber threats. These threats
jeopardize not only the security of IVNs but also the safety of
passengers [2].
Among in-vehicle communication protocols, the Controller
Area Network (CAN) is widely regarded as the de facto standard
for communication among Electronic Control Units (ECUs) in
embedded IVN systems [3]. Malicious CAN messages can lead
to severe consequences, particularly when they target critical
systems such as the brakes, powertrain, or safety controls of
a vehicle [4]. In light of this, recent studies have proposed
various methods to enhance IVN security by detecting intrusions
on the CAN bus [5], [6], [7]. While encryption and authentication techniques can enhance the security of IVNs [8], they
often necessitate modifications to the existing CAN protocol
specifications and communication procedures. Such changes are
generally considered impractical and cost-prohibitive, given the
widespread adoption of the CAN protocol in the automotive
manufacturing industry. As a more feasible alternative, the intrusion detection system (IDS) offers a non-invasive security
solution by leveraging bypass monitoring mechanisms that do
not require any changes to the CAN protocol or ECU hardware. This characteristic makes IDS particularly suitable for
real-world deployment, offering both technical viability and
economic efficiency [9].
As artificial intelligence advances in network traffic identification, IVN intrusion detection has shifted from monitoring
the physical characteristics of the ECU to analyzing the characteristics of the CAN data flow, reflecting interactions between
the ECUs. Mainstream approaches predominantly use deep
neural networks or graph-based methods, such as Convolutional
Neural Networks (CNNs), Recurrent Neural Networks (RNNs),
and graph-based intrusion detection systems [10], [11], [12].
However, existing supervised neural network models label all
CAN messages within a data flow as anomalous, regardless of
the number of actual abnormal messages [13]. This leads to
coarse-grained detection, where only the overall anomaly of a

1536-1233 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

6336

detection window is identified, without fine-grained recognition
of individual messages [14], [15]. Consequently, the traceability
of detection is lost, making it difficult to locate the exact source
of anomalies [16], [17], [18]. Additionally, current graph-based
methods primarily focus on simpler attack types [10], [19],
leaving the detection of sophisticated masquerade attacks largely
unexplored [9], [20], [21], [22]. Masquerade attacks are especially stealthy, as they replace legitimate messages while maintaining transmission timing and interaction patterns, but inject
malicious payloads. However, most mainstream single-view
graph-based intrusion detection methods primarily model the
relationships among CAN message IDs and their transmission
frequencies. While these approaches are effective for detecting
simple anomalies, they often fail to identify masquerade attacks
that modify only the payload, due to their limited ability to
capture the coupling structure of data flow [11].
To address the aforementioned issues, we propose STATGRAPH, an effective in-vehicle intrusion detection approach that
achieves fine-grained classification through multi-view statistical graph learning. Unlike previous single-view models, STATGRAPH adopts a dual-graph learning paradigm that simultaneously captures global statistical regularities and local contextual
dependencies. It constructs node feature vectors and adjacency
matrices for the Graph Convolutional Network (GCN) by generating two statistical views: the Timing Correlation Graph (TCG)
and the Coupling Relationship Graph (CRG). The TCG models
long-range statistical distributions among CAN messages by
capturing temporal correlations between different CAN IDs
within detection windows. In contrast, the CRG encodes both
temporal adjacency and contextual similarity, reflecting the continuity of identical CAN IDs and variations in payload values
or signal-level patterns over short time spans. These two graph
views are integrated through graph convolutional operations,
which enable multi-view feature propagation and abstraction.
This design results in enriched representations of in-vehicle
communication dynamics and enhances the model’s ability to
detect complex and subtle anomalies. Additionally, the GCN’s
compatibility with small-scale graphs in streaming contexts,
along with its computational efficiency, makes it well suited
for IVN intrusion detection scenarios where rapid response is
essential.
The main contributions of this paper can be summarized as
follows:
r We propose STATGRAPH, a multi-view statistical graph
learning framework for effective intrusion detection in
IVNs. By considering both the interactive relationships
among CAN messages and their payload-level contextual
similarities, STATGRAPH accurately captures variations in
periodicity, payload content, and signal combinations. This
enables the detection of a wide range of attacks, including
sophisticated and complex masquerade attacks.
r Current deep learning-based approaches build the model
input with multiple CAN messages, resulting in coarse
recognition and the inability to locate the malicious message. To accurately quantify the message-level recognition accuracy, we introduce a new criterion, Identification
Granularity (IG), which is used to assess how precisely

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 5, MAY 2026

Fig. 1.

CAN frame.

an intrusion detection model can classify each individual
CAN message within a detection window, in contrast to
traditional metrics that evaluate performance at the window
or segment level.
r To evaluate the classification ability of STATGRAPH on captured CAN messages of realistic in-vehicle environment,
we conduct experiments on an in-vehicle computing platform (NVIDIA Jetson Nano T206 with ARM architecture)
and on a personal computer (LENOVO 90VA000JCP),
respectively. Besides, we select the Car Hacking dataset
and the ROAD dataset to cover as many types of attacks
as possible, which are both directly generated from real
vehicles on sale. Notably, to the best of our knowledge, we
are the first to investigate 5 new types of masquerade attacks
introduced by the ROAD dataset, which can cause incorrect
working status of physical components within real vehicles
(e.g., wrong speed indicator position by injecting fake
wheel speed values) and bring in severe damage on both
vehicles and passengers.
The remainder of this paper is organized as follows: Section II
introduces the related background knowledge. Section III describes our proposed STATGRAPH. We show the experimental
setup and results in Section IV followed by the discussion
in Section V. Section VI summarizes existing representative
IVN intrusion detection methods. We conclude the paper in
Section VII.
II. BACKGROUND
In this section, we provide a brief introduction to the IVN
CAN protocol and adversary types related to our STATGRAPH.
A. IVN CAN Details
CAN is the current de facto standard for IVN, which is widely
used in the automotive industry to connect different ECUs in
vehicles and support messaging between ECUs. There are four
types of CAN frames: 1) Data frame; 2) Remote frame; 3) Error
frame; 4) Overload frame. Fig. 1 illustrates the format of a CAN
data frame, which is the default mode used for CAN message
transmission. CAN data frames support payloads of up to 8 bytes
and have an 11-bit arbitration ID (CAN ID) that can be extended
to 29 bits.
The arbitration ID (CAN ID) plays a dual role in CAN
communication: it governs message priority during bus arbitration and simultaneously serves as a semantic identifier. During
arbitration, the message with the numerically lowest CAN ID
is granted bus access, while others must defer until the bus is
idle. Beyond arbitration, the CAN ID conveys content-specific
semantics, as defined by the Original Equipment Manufacturer
(OEM)-provided communication matrix. For instance, in several
publicly available datasets, ID 0x45D is transmitted by the

WANG et al.: STATGRAPH: EFFECTIVE IN-VEHICLE INTRUSION DETECTION VIA MULTI-VIEW STATISTICAL GRAPH LEARNING

powertrain control module every 0.01s to report gas and brake
pedal positions, while ID 0x102 from the same module contains
drivetrain-related information. These IDs exemplify how CAN
messages are tied to specific modules and functions, with fixed
payload formats and transmission intervals.
The Data Field (payload) contains up to 8 bytes and typically encodes multiple physical signals. Each signal is precisely defined by the communication matrix, which specifies
its start bit, length in bits, scaling factor, and valid range. This
bit-level packing enables compact and efficient transmission,
with multiple quantities multiplexed into a single message.
However, this design also introduces attack surfaces: adversaries
may tamper with individual bits to subtly alter signal values
while maintaining the overall message frequency and structure. Such fine-grained manipulations are often undetectable
by coarse-grained detection models, highlighting the necessity
of payload-level analysis. Additionally, the coexistence of various transmission patterns (e.g., periodic, event-triggered, or
conditional) introduces complex temporal dependencies among
CAN messages, as discussed in [23]. This structural complexity
motivates the use of graph-based methods that can effectively
model inter-message relationships across time and semantics.
B. Threat Model
ECUs employ bit-by-bit arbitration and explicit broadcasting
to transmit CAN protocol messages, enabling fast and efficient data exchange. An adversary may access the CAN bus
through the OBD-II port or exploit the telematics service of
the OEM via remote network access. Based on the attacker’s
objectives, such intrusions are typically classified into three
categories.
1) Fabrication Attacks. An adversary compromises an ECU
and injects malicious messages with forged IDs and data fields
into the CAN bus. This is a common and straightforward attack,
easily executed. Despite this, all legitimate ECUs remain active,
transmitting their original data. Fabrication attacks increase
CAN bus traffic, leading to dynamic and distributed changes in
communication behavior. Examples include Denial of Service
(DoS) attacks, fuzzy attacks, and targeted ID attacks.
2) Suspension Attacks. In this type of attack, legitimate ECUs
can be disabled by an adversary. Specifically, the targeted ECU
is weakly compromised and loses the ability to transmit messages, impairing other ECUs that rely on its data to function
properly. As a result, suspension attacks can affect not only the
compromised ECU itself but also other receiving ECUs.
3) Masquerade Attacks. These attacks combine fabrication
and suspension techniques, exhibiting highly sophisticated and
stealthy behavior patterns. The adversary first disables the ECU
intended for replacement, removing it from the CAN network.
A fully compromised ECU then sends spoofed messages with
the same ID at a realistic frequency, effectively masquerading
as the original. In this advanced strategy, only the payload is
subtly altered, while the behavioral characteristics of the target
ECU are preserved. As a result, message conflicts are avoided,
and communication dynamics remain unchanged, causing many
intrusion detection methods to fail.

6337

III. METHODOLOGY
In this section, we give the system overview of the STATGRAPH, and then present the details of its key components.
A. System Overview
STATGRAPH consists of the following three components, as
illustrated in Fig. 2. In contrast to prior works such as [11],
which rely on a single statistical view of CAN message IDs,
STATGRAPH introduces a multi-view graph construction framework that jointly models global statistical trends and local contextual dependencies. This dual-graph architecture is designed
to capture complementary aspects of in-vehicle communication
behavior, enabling a richer and more nuanced representation
of message dynamics. The TCG captures long-range behavioral patterns by aggregating messages with the same CAN
ID, enabling the detection of anomalies in message periodicity and distributional shifts. Complementing this, the CRG
preserves message-level granularity and constructs edges based
on temporal adjacency and ID similarity, allowing the model to
detect localized irregularities in payload content and inter-signal
consistency. Their integration through graph convolution enables feature propagation across the two graph structures, rather
than relying on simple feature concatenation. This approach
reinforces the model’s capacity to generalize from complex
communication patterns.
This architectural design provides a structured foundation that
encodes three critical dimensions of communication behavior:
periodicity, payload semantics, and signal relationships. These
aspects are not modeled independently but are jointly embedded in the node features and adjacency structures, equipping
the system with strong inductive biases for fine-grained and
interpretable anomaly detection.
r Global Feature Fusion Module (Section III-B) constructs
the TCG and derives statistical behavioral features such as
frequency and temporal regularity. These features, together with
the raw payload bytes, are fused into node-level feature vectors
that encode long-term communication patterns in IVNs. In the
TCG, each unique CAN ID within the detection window is
represented as a node. All messages associated with the same ID
are aggregated to extract global statistical attributes that collectively reflect the periodicity and distributional characteristics of
message transmissions. The resulting rich and structured node
representations benefit downstream relational modeling in the
CRG to further capture multiple dimensions of communication
behavior, including timing consistency, payload semantics, and
inter-signal relationships.
r Association Enhancement Module (Section III-C) constructs the CRG to generate adjacency matrices that encode finegrained communication dependencies among CAN messages.
Unlike conventional adjacency constructions that rely solely
on message co-occurrence or ID similarity, the CRG models
two complementary relational patterns: temporal adjacency between consecutive messages and semantic consistency among
messages sharing the same CAN ID. Within each detection
window, every individual CAN message is treated as a separate
node. Edges are established either between temporally adjacent

6338

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 5, MAY 2026

Fig. 2. Architecture of STATGRAPH. Global Feature Fusion Module (III-B) generates node feature vectors by constructing TCGs that react to the long-term
distribution of IVN CAN messages. Association enhancement module (III-C) produces adjacency matrixes by constructing CRGs whose edges reflect both
contextual adjacency and intra-message dynamics between adjacent CAN messages or those with the same ID. GCN classification module (III-D) accepts the
generation of streaming graph-structured data from the global feature fusion module and association enhancement module to perform training and detection tasks.

Fig. 3.

NVIDIA Jetson Nano T206.

messages or between messages that share the same ID. This
design enables the CRG to encode both temporal continuity and
ID semantic regularities at the message level, thereby capturing
localized structural patterns that reflect message periodicity,
payload semantics, and inter-signal dependencies. These three
dimensions are jointly embedded in the graph topology and serve
as critical relational cues for detecting fine-grained anomalies
that may elude traditional statistical aggregation methods.
r GCN Classification Module (Section III-D) consumes the
graph-structured representations constructed by the Global Feature Fusion Module and Association Enhancement Module to
perform message-level classification. The module takes as input
the node features derived from the TCG, which reflect global
statistical patterns such as frequency and temporal regularity,
together with the adjacency matrices built from the CRG, which
encode localized contextual and semantic relationships among
CAN messages. This dual-graph input enables the GCN to
jointly model long-term communication behavior and shortterm structural dependencies, equipping it with strong inductive
bias for detecting both overt and stealthy anomalies. By leveraging this architecture, the GCN module facilitates high-resolution
threat detection by leveraging both statistical abstraction and
structural semantics, thereby improving classification accuracy
while preserving temporal and message-level interpretability.

We define two different types of generated multi-view in the
following definition.
Definition 1: We consider two types of graphs: the TCG
G(V, E), which captures long-term statistical attributes, and the
CRG Ĝ(V̂ , Ê), which models the topological structure of shortterm message interactions. Here, vi , vj ∈ V and v̂i , v̂j ∈ V̂
denote nodes, while eij ∈ E ⊆ V × V and êij ∈ Ê ⊆ V̂ × V̂
represent edges. The values wij and ŵij are the respective
weights of edges eij and êij .
B. Global Feature Fusion Module
To capture long-term behavioral patterns in in-vehicle communication, this module constructs the TCG, which abstracts
statistical dependencies among CAN IDs by extracting interaction features from continuous data streams. Unlike traditional
approaches based mainly on frequency or co-occurrence statistics, the TCG employs directed edges to encode conditional
dependencies derived from ID orderings within each detection
window.
• Generation of TCG based on CAN stream
The CAN flow can be regarded as multivariate time series.
Definition 2: (Multivariate Time Series) CAN data is a
multivariate time series Ψ ∈ RT ×V :
Ψ = {ψ1 , ψ2 , . . . , ψt , . . . , ψT }

(1)

where ψt = {timestamp, ID, DLC, d1 , . . . , d8 , type} ∈ RV .
V = 12 is the dimension of a recorded data CAN message.
We choose ID = d0 , data field {d1 , d2 , . . . , d8 } ∈ R8 and
label value dl to form φt = {d0 , d1 , d2 , . . . , d8 , dl } ∈ R10 as
input representation for STATGRAPH.
Since recurrent ID patterns reflect the periodicity of CAN
messages, we divide IVN CAN traffic into multiple detection
windows and characterize message distributions within each

WANG et al.: STATGRAPH: EFFECTIVE IN-VEHICLE INTRUSION DETECTION VIA MULTI-VIEW STATISTICAL GRAPH LEARNING

window separately, enabling more efficient data preprocessing
for STATGRAPH.
We divide the CAN detection windows as follows:
Definition 3: A series of CAN messages monitored from the
IVN arranged according to the normal communication sequence
can be regarded as located within a single detection window. In
proposed algorithm, we consider N messages to be a detection
window [11]. N is the detection window size. Let’s assume that
there are K detection windows in total. wk denotes the matrix
consisting of CAN messages within k-th detection window after
preprocessing.
wk = {φk∗N +1 , φk∗N +2 , . . . , φk∗N +N }

(2)

Therein, k ∈ {0, 1, 2, . . . , K − 1}.
After dividing the CAN messages into K detection windows
according to Definition 3, our scheme introduces Algorithm 1 to
track valid transitions between the IDs of consecutive CAN messages and construct a TCG list based on multivariate time-series
data. Specifically, for each set of N messages within a detection
window, the algorithm treats each distinct CAN ID as a node
and builds edges to represent ID-to-ID relationships. For clarity,
Set[IDi ] = {φn | φn [d0 ] = IDi , φn ∈ wk } denotes the set of
messages with the same IDi , where IDi is the key for Set[IDi ].
The algorithm iterates over all detection windows (Line 2). For
the k-th window, it collects each unique ID and creates a new
key-value pair when the ID first appears (Lines 4 and 8). Then,
an edge is added between the IDs of two consecutive messages.
If the edge already exists, its weight is incremented (Line 11).
In the resulting TCG, each node corresponds to a unique
CAN ID, and directed edges represent long-term statistical
dependencies based on co-occurrence patterns observed within
detection windows. Specifically, a directed edge from node IDB
to node IDA is added whenever IDB appears after IDA within
the same detection window, regardless of how frequently this
occurs. In other words, the presence of such an edge does not
imply a minimum frequency threshold, but rather reflects the
existence of at least one instance of sequential co-occurrence.
Each time IDB follows IDA , the weight of the edge from IDB
to IDA is incremented by one, thus encoding the strength of
this historical statistical association. This edge orientation does
not represent a strict physical or chronological order, but instead
models a backward statistical dependency: the current behavior
of a CAN ID is understood in relation to the aggregate patterns
of its preceding IDs. Consequently, the edge direction captures
accumulated historical influence rather than deterministic temporal causality.
The rationale for this edge orientation is rooted in the assumption that the behavior of a CAN ID is influenced by the statistical
characteristics of its predecessors. To capture this influence in
a graph neural network, where information propagates from
neighboring nodes to a target node during aggregation, the
edge must be directed from IDB to IDA . This configuration
allows node IDB to receive contextual information from node
IDA , thereby encoding historical dependencies into the node
representations. Such a design is particularly effective in identifying masquerade attacks, where adversarial messages mimic
the surface statistics of normal traffic but disrupt underlying

6339

Algorithm 1: TCG Building Algorithm.
Require:
Detection Window List of CAN Messages:
CAN W indowList = {w1 , w2 , . . . , wK }, therein wk =
{φk∗N +1 , φk∗N +2 , . . . , φk∗N +N }.
Ensure:
CorrelationGraphList[G1 , G2 , . . . , GK ]  Timing
Correlation Graph array of CAN bus data;
1: CorrelationGraphList ← [ ], IDDictionary ←
{}
2: for wk in CAN W indowList do
3:
Initialize Graph;
4:
LastID ← φk∗N +1 [d0 ];
5:
IDDictionary[LastID] ← len(IDDictionary)
 Create a new key/value pair in the dictionary;
6:
for i in {2, . . . , N } do
7:
N owID ← φk∗N +i [d0 ];
8:
if not NowID in IDDictionary.keys() then
9:
IDDictionary[N owID] ←
len(IDDictionary)  Create a new key/value
pair in the dictionary;
10:
end if
11:
Connect an edge from vIDDictionary[N owID] to
vIDDictionary[LastID]  Create link between two
graph nodes;
12:
LastID ← N owID;
13:
end for
14:
Append Graph to the CorrelationGraphList;
15:
IDDictionary.clear  clear IDDictionary
16: end for
transmission patterns. By modeling statistical dependencies in
this manner, the TCG enhances the model’s capacity to recognize
subtle anomalies in message sequences.

+1, φn ∈ Set[IDj ], φn+1 ∈ Set[IDi ]
wi,j ←
+0, else
The algorithm keeps the graph Gk built by the current detection window (Line 14) and eventually returns the graphs
G1 , . . . , GK for all detection windows.
• Building feature vector of each node
After construction of TCG, graph feature vectors can be
generated by statistical attributes of TCG, such as: the number
of edges, the number of nodes, the max weight, the average
weight, the max degree, etc. Our proposed method characterizes
feature vector for each CAN message, which could be defined
as Xk,n , denoting the node feature of n-th message in k-th
detection window of raw CAN messages, n ∈ {1, 2, . . . , N }.
Hence, denote node feature matrixes of k-th detection window
as:
Xk , k ∈ {0, 1, . . . , K − 1}

(3)

According to research [11], we choose to extract the node
number, edge number, and maximum degree from a single
constructed TCG, and consider them as global features to be
appended to the node feature vectors.

6340

Hence, node feature is designed accordingly as Xk,n =
{d0 , d1 , d2 , . . . , d8 , x9 , . . . , x11 } ∈ R12 , where d0 is CAN ID
converted to decimal, d1 , d2 , . . . , d8 mean the data value in data
field and x9 , x10 , x11 represent the node number, edge number
and maximum degree of the TCG to which the node belongs,
respectively. To test and verify the detection granularity for
each CAN message, the node feature Xk,n retains the label
in the model training and testing process indicating whether
it is normal or injected, though it is not a necessary part of the
input node feature vector when implemented in the real IDS
environment.
The TCG models the periodic transmission behavior of CAN
messages based on the timestamps and IDs of consecutive entries. By analyzing ID transitions and their recurrence within detection windows, the TCG captures temporal regularities and detects deviations indicative of anomalous behavior. As legitimate
messages typically exhibit stable timing patterns, disruptions
caused by injected messages can be identified through statistical
variations such as frequency shifts and entropy fluctuations. For
example, a message with ID 0x45D, normally transmitted every
10 milliseconds, may display altered periodicity under attack
conditions.
In addition, the TCG provides statistical features to construct
node feature vectors, which incorporate payload bytes d1 to
d8 along with temporal statistics, forming a representation that
captures both content and timing characteristics. This design
integrates message periodicity, payload content, and signal correlations into a unified node feature representation for the first
time, yielding a more expressive global view and offering a
stable, generalized structural prior for downstream relationship
modeling.

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 5, MAY 2026

Algorithm 2. CRG Building Algorithm.
Require:
Detection Window List of CAN Messages:
CAN W indowList = {w1 , w2 , . . . , wK }, therein wk =
{φk∗N +1 , φk∗N +2 , . . . , φk∗N +N }.
Ensure:
RelationshipGraphList[Ĝ1 , Ĝ2 , . . . , ĜK ]  Coupling
Relationship Graph array of CAN bus data;
1: RelationshipGraphList ← [ ], IDSet ← { }
2: for wk in CAN W indowList do
3:
Initialize Graph;
4:
LastID ← φk∗N +1 [d0 ];
5:
IDSet[LastID] ← len(IDSet)  Create a new
key/value pair in the dictionary;
6:
for i in {2, . . . , N } do
7:
N owID ← φk∗N +i [d0 ];
8:
(v̂i−1 , v̂i ) ← 1  Link two neighbor nodes
(Contextual correlation property);
9:
if not NowID in IDSet.keys() then
10:
IDSet[N owID] ← [i]  Create a new
key/value pair in the dictionary;
11:
else
12:
Append i to the IDSet[N owID];
13:
Link the edges between nodes in
IDSet[N owID]  Connect all nodes with the
same ID value (Similarity);
14:
end if
15:
end for
16:
Append Graph to the CorrelationGraphList;
17:
IDSet.clear  clear IDSet
18: end for

C. Association Enhancement Module
This module leverages CRGs to enhance the association
between CAN messages that exhibit similarity and short-term
dependence. While TCGs capture periodicity and regularity,
they cannot detect masquerade attacks, which alter payloads
without affecting statistical patterns. Legitimate message payloads fluctuate but exhibit regularities within the same ECU [24],
and CAN messages from different ECUs may share common
patterns, which masquerade attacks disrupt.
CRGs capture these coupling relationships by reinforcing
links between messages based on short-term correlations. Unlike
approaches that rely solely on contextual connections due to
the simplicity of the CAN format, CRGs integrate both contextual correlation and content similarity, providing a more
comprehensive representation of CAN message associations. As
illustrated in Fig. 2, the gray links denote similarity relationships
among groups of CAN IDs, whereas the black links capture the
contextual correlation between successive CAN messages.
Despite substantial efforts to model graph structural information, existing methods remain limited in capturing coupled
relationships [13]. By incorporating both contextual adjacency
(the contextual relevance among two adjacent messages) and
intra-message dynamics (the similarity of intra message with the
same ID), the CRG preserves localized communication patterns

and content semantic consistency at the message level, which
facilitates the detection of subtle variations in payload content
and embedded signals in each CAN message. In STATGRAPH, the
CRG innovatively defines data flow coupling by capturing two
essential forms of contextual correlation: temporal adjacency
between consecutive CAN messages and semantic consistency
among messages sharing the same ID. Unlike conventional
methods that construct graphs based only on message cooccurrence or ID similarity, the CRG preserves message-level
granularity and incorporates both temporal ordering and ID
relationships into its adjacency structure. This design enables the
model to retain fine-grained contextual dependencies, allowing
it to detect localized anomalies such as unexpected changes
in payload values or disrupted signal correlations embedded
in d1 to d8 . The CRG thus offers a structural representation
of communication patterns that are sensitive to violations in
temporal continuity, payload integrity, and inter-signal coherence. To operationalize these relationships, we propose a novel
construction strategy for the CRG’s adjacency matrix, as detailed
in Algorithm 2.
From Definition 3, we set the same detection windows as Section III-B. Each CAN message in the k-th detection window is
treated as a node in the CRG, which contains N nodes, and edges

WANG et al.: STATGRAPH: EFFECTIVE IN-VEHICLE INTRUSION DETECTION VIA MULTI-VIEW STATISTICAL GRAPH LEARNING

are constructed to represent short-term relationships between
messages. A loop is iterated over each detection window (Line
2). In the k-th detection window, we define the nodes with the
same ID as a set denoted Set[IDi ] = {φn |φn [d0 ] = IDi , φn ∈
wk }, which is constructed by counting the messages corresponding to each ID (Lines 5 and 9). Next, the algorithm constructs
edges of CRG Ĝk by searching coupling relationships. For i, j
in {1, 2, . . . , N }, we have
⎧
⎨1, j = i + 1 or i = j + 1
(4)
êij = 1, φj , φi ∈ Set[IDm ]
⎩
0, else
The first row in (4) specifies that an edge is created between
nodes representing two consecutive CAN messages (Line 7).
The second row in (4) indicates that nodes sharing the same
CAN ID are interconnected (Line 12). The last row of (4) states
that edges not satisfying the aforementioned relationships are
excluded from the graph.
Finally, Algorithm 2 returns undirected graph instances of
CRGs for multiple detection windows, whose adjacency matrices will be used for the classification task in the GCN by learning
generalizable patterns. Therefore, the adjacency matrix of k-th
detection window as input for next GCN classification module
can be defined as:
Ak , k ∈ {0, 1, . . . , K − 1}

(5)

The CRG captures short-term communication dependencies
by treating each individual CAN message as a node and constructing edges based on temporal adjacency and ID similarity.
Edges are constructed to reflect the expected local communication flow and semantic regularities. This graph is built directly
from message timestamps and CAN IDs, enabling the model
to represent fine-grained variations in message timing. Subtle
temporal deviations such as jitter or irregular intervals may
signal stealthy intrusions and can thus be effectively identified.
Although the CRG does not explicitly interpret the semantics
of the payload, it retains payload similarity structures among
messages, including correlations across the eight signal bytes d1
through d8 . This retention allows the model to capture changes
in contextual consistency and signal co-evolution patterns. For
instance, messages with the same ID but exhibiting sudden shifts
in payload distributions or disrupted signal correlations may
indicate semantic manipulation or low-rate injection attacks. By
preserving message-level granularity and local structural continuity, the CRG transforms subtle inconsistencies into structural
variations, which can be effectively captured by the downstream
GCN classifier.
D. GCN Classification Module
We propose a multi-layer GCN model for classifying attacks
on the in-vehicle CAN bus, trained using graph-structured data
generated by the Global Feature Fusion and Association Enhancement modules, which capture both temporal and contextual dependencies of IVN message streams.
Based on this design, the GCN module functions as the core
classifier in STATGRAPH, integrating node-level features from

6341

TABLE I
STRUCTURE AND DIMENSIONS OF ALL LAYERS OF STATGRAPH

the TCG with edge-level structures defined by the CRG. The
TCG models long-range communication patterns by aggregating
messages with the same CAN ID, enabling the extraction of
global statistical features such as frequency shifts and periodic
anomalies. In contrast, the CRG preserves message-level granularity and constructs the adjacency matrix by jointly modeling
two types of relational dependencies: temporal adjacency among
consecutive messages and semantic similarity among messages
sharing the same CAN ID. This allows the CRG to encode both
the contextual flow and ID structural regularities. As a result,
disruptions in expected message timing, payload consistency,
or inter-signal correlations can be reflected as abnormal edge
patterns. By jointly leveraging the statistical aggregation of
TCG and the localized structural encoding of CRG, the GCN
receives a rich representation of communication behavior, which
supports precise and fine-grained classification of each message.
This unified modeling approach ensures that both global distributional shifts and localized anomalies are effectively captured.
The GCN model [25] applies first-order graph convolution to
jointly model structural information and node attributes.
To formalize the learning process, the multi-layer GCN is
defined as:


H (l+1) = σ D̃−1/2 ÃD̃−1/2 H (l) W (l)
where H (l) is the matrix of activations in the l-th layer, W (l)
denotes the trainable weight matrix of l-th layer. σ(·) is the
activation function. Denote number of hidden layer units as h,
and l ∈ {0, 1, 2, . . . , L}. Set the adjacency matrix of input graph
as A. Ã = A + IM , where M is the size of A and IM is the
M -dimensional
identity matrix, D̃ is degree matrix of Ã and

D̃ii = j Ãij . Denoting the node feature matrix of input graph
as X, we can get initial H (0) = X. After multiple experiments,
from the perspective of lightweighting and performance, our
GCN model consists of an input layer, L hidden layers and a
dense layer, shown in Table I.
In order to improve the training efficiency of the model in
coding, we set batchsize=B, which means that we take the node
feature matrixes and the adjacency matrixes corresponding to B
consecutive detection windows as once input. Hence, the input
node feature matrix X ∈ R(B∗N )×12 is the continuous Xk splice
of B and the input adjacency matrix A with size (B ∗ N, B ∗ N )
is a diagonal concatenation of B continuous matrixes Ak .

6342

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 5, MAY 2026

TABLE II
HYPERPARAMETERS FOR TRAINING THE STATGRAPH MODEL

With the structural and feature information embedded in
the input, the GCN proceeds to node classification, producing
abstract representations for each CAN message to enable finegrained detection.
For k-th detection window, the last dense layer of GCN model
returns output Zk = {Zk,1 , . . . , Zk,N }, where Zk is the set of
Zk,n and Zk,n ∈ {0, 1, 2, . . . , F } is employed to predict the attribute labels of the n-th message in the k-th detection window. In
the training phase, the cross − entropy loss function compares
real label of the n-th message in the k-th detection window to
Zk,n through a sigmoid activation function.
Besides, L2 regularization is used to restrict the values of
weights to prevent overfitting. Besides, our GCN model is
trained using the Adam optimizer, with a learning rate of 10−3 .
In addition, we deploy dropout layers with a rate of 0.005 after
each GraphConv layer. Moreover, we set the rectified linear
unit (ReLU), a widely used nonlinear function, as activation
function in our model. It introduces nonlinearity and allows
the neural network to learn complex relationships in the data.
And hyperparameters for training the STATGRAPH are shown in
Table II.
This module fully utilizes node features by fusing statistical
regularities derived from recurrent ID patterns and association
relations enhanced by adjacency matrices, thereby enabling
high-performance, fine-grained detection and classification of
multiple attacks. The use of backward edge direction in the
TCG is motivated by the GCN message aggregation mechanism,
where each node aggregates information from its incoming
neighbors. By directing edges from the latter ID to the former, the model allows emerging nodes to incorporate historical
contextual features during convolution, facilitating the learning
of temporal correlations among CAN IDs, particularly those
with fixed or periodic transmission characteristics. By jointly
leveraging both the TCG and CRG, the STATGRAPH framework
captures multiple dimensions of in-vehicle communication dynamics. The TCG constructs node features by aggregating all
messages sharing the same CAN ID within a detection window. This process extracts statistical characteristics such as frequency, entropy, and inter-arrival time, enabling the encoding of
long-term communication patterns. Directed edges in the TCG
represent statistical dependencies among different IDs, allowing
the GCN to aggregate contextual information from historically
correlated message flows. The CRG, in contrast, defines the adjacency matrix based on two criteria: temporal adjacency between
consecutive messages and ID similarity. This graph preserves
message-level granularity and captures localized contextual and
semantic dependencies, including fine-grained timing variations
and signal correlations inferred from payload bytes.

Together, the global and local priors encoded by the TCG and
CRG enable joint representation learning that effectively models
multi-scale behavioral patterns in in-vehicle communication.
The dual-graph design produces highly expressive inputs for
GCN-based classification, allowing even shallow architectures
to achieve strong performance. This efficiency stems from the
rich feature encoding in the graph representations, reducing the
need for complex model depth while enabling robust detection
of stealthy intrusions, such as masquerade attacks that preserve
surface-level message patterns.
IV. EXPERIMENT
This section presents the implementation of the STATGRAPH
framework under two computing environments (Section IV-A)
and introduces the evaluation metrics used to quantify detection
granularity (Section IV-B). Baseline methods for comparison
are described in Section IV-C. The dataset details are provided
in Section IV-D, followed by a parameter sensitivity analysis in
Section IV-E. We evaluate runtime and detection performance in
Sections IV-F and IV-G, respectively. The fine-grained detection
capability is explored in Section IV-H.
A. Environment
As a core technology for vehicle network security, the intrusion detection model must offer real-time detection capabilities
and a low false positive rate, particularly in vehicle environments
with limited computational resources.
With this in mind, we deploy and evaluate it on the NVIDIA
Jetson Orin Nano platform (as shown in Fig. 3), a widely
adopted hardware system in both the automotive industry and
academia. This platform supports CAN bus communication,
features an ARMv8 Processor rev 1, and integrates a 512-core
NVIDIA Ampere architecture GPU with 8.0 GB of memory.
With approximately 21 Tera Operations Per Second (TOPS)
of computing power and low energy consumption, the device
supports inference for medium-sized deep learning models,
including tasks such as target detection and time-series data
analysis, making it well suited for evaluating complex intrusion detection algorithms under resource-constrained onboard
conditions. The software environment includes PyTorch 1.12.1
with Python 3.8.10.
For training, we utilize a more powerful device, the LENOVO
90VA000JCP with 49 TOPS of computational power, to simulate
a cloud environment and accelerate the training process. It
features a 64-bit Intel Core i7-13700 CPU at 3.6 GHz and a
Geforce RTX 4080 32 GB GPU, with PyTorch 1.13 and Python
3.8 for the STATGRAPH model.
B. Evaluation Metrics
To evaluate the effectiveness of different methods, this paper
adopts a set of standard classification metrics. Accuracy, Precision, and Recall can be calculated using the numbers of true
negatives (TN), true positives (TP), false negatives (FN), and
false positives (FP), defined as follows:
Accuray =

TP + TN
TP + TN + FP + FN

(6)

WANG et al.: STATGRAPH: EFFECTIVE IN-VEHICLE INTRUSION DETECTION VIA MULTI-VIEW STATISTICAL GRAPH LEARNING

TP
TP + FP
TP
Recall =
TP + FN

Precision =

6343

TABLE III
OPEN CAN DATASETS

(7)
(8)

Besides, F1-score is more useful than accuracy in the case of
an unbalanced class distribution. It is the harmonic mean of
precision and recall, calculated as follows:
F1 − score =

2 × Precision × Recall
Precision + Recall

(9)

IG is a fine-grained evaluation metric that quantifies the
message-level recognition accuracy of intrusion detection methods. This metric is particularly necessary because existing
graph-based intrusion detection approaches for IVNs predominantly adopt coarse-grained classification strategies, wherein
a single anomaly label is typically assigned to an entire message window or sequence. Such granularity is often insufficient for timely and precise threat localization, especially in
scenarios involving stealthy or transient attacks. To address
this limitation, STATGRAPH is, to the best of our knowledge,
the first graph-based framework specifically designed to enable
fine-grained, message-level intrusion detection. By providing
classification results for each individual CAN message, the
proposed framework achieves higher temporal resolution and
improved diagnostic accuracy. The IG metric is introduced to
formally quantify this capability, as it captures evaluation aspects
that are overlooked by conventional, window-level performance
metrics.
Based on the correct identification of the detection window
(that is, the label of the k-th detection window, labelk = the
predicted value of the k-th detection window, predictk ), IG is
calculated through TI (True Identification), which represents the
number of correctly identified samples per detection window.
Hence, the IG is defined as follows:
IG =
where


Ck =

1,
0,

1
N

K

TIk × Ck

(10)

k=1

labelk = predictk
labelk = predictk

It measures how precisely a model can determine the status of
each individual CAN message within a detection window, thus
enabling a clear distinction between models that perform well
only at a coarse-grained level and those capable of delivering
reliable fine-grained identification.
C. Compared Methods
To ensure a fair comparison, several representative and advanced models are selected for binary and multi-classification
tasks, as well as for coarse-grained and fine-grained levels:
r Graph-based intrusion detection system (Graph-based
IDS) [11]: A coarse-grained, graph-based IVN intrusion
detection method that uses the median and Chi-squared
tests for binary classification tasks. It operates on the

number of nodes, edges, and maximum degree of graphstructured data generated from CAN messages over six
detection windows.
r G-IDCS TH_classifier [12]: This graph-based IVN intrusion detection method performs binary classification based
on thresholds for the number of nodes, edges, and maximum degree of graph-structured data within each detection
window.
r G-IDCS ML_classifier [12]: Using the same graph generation process as G-IDCS TH_classifier, this method
performs multi-class classification tasks using a Random
Forest (RF) algorithm on the generated graph-structured
data within each detection window.
r EfficientNet [26]: A neural network architecture with a
novel compound scaling method that balances network
width, depth, and resolution. It performs coarse-grained
multi-classification intrusion detection tasks in resourceconstrained IVN environments.
r MobileNetV3 [27]: A lightweight neural network that utilizes efficient depthwise separable convolutions, suitable
for IVN multi-classification intrusion detection tasks at a
coarse-grained level (window-level classification).
r CANet [16]: The first deep learning-based method for IVN
multi-classification intrusion detection, which checks individual CAN messages using a tailored network structure
that fits the signal space of CAN data for each detection
window.
r CAN-RF [28]: A fine-grained multi-classification method
based on an integrated learning framework where each decision tree is constructed from a random subset of features
of each CAN message.
r MultiLayer Perceptron (CAN-MLP) [28]: This model executes multi-class classification tasks on each CAN message
using a feedforward neural network structure.
r Long Short Term Memory (CAN-LSTM) [29]: A popular
RNN variant that predicts the next CAN ID more effectively based on previous observations, making it suitable
for fine-grained multi-classification tasks.
D. Datasets Details
To the best of our knowledge, seven publicly available CAN
datasets with labeled attacks exist (see Table III). We prioritize

6344

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 5, MAY 2026

TABLE IV
THE DISTRIBUTION OF THE CAR HACKING DATASET

datasets involving real attacks on actual vehicles, as simulated
data may lack real-world fidelity. While prior IDS research
has largely focused on fabrication attacks, masquerade attacks
remain underexplored. The Car Hacking dataset, widely used in
IVN intrusion detection research, contains various fabrication
attacks. In contrast, the ROAD dataset offers high fidelity and
includes diverse masquerade attacks, with their physical effects
validated on real vehicles. For example, injecting false wheel
speed values can trigger critical malfunctions, posing safety
risks to both the vehicle and passengers. Detailed descriptions
and experimental setups for each dataset are presented in the
following subsections.
1) Car Hacking Dataset: It was produced by the Hacking
and Countermeasure Research Lab (HCRL) of Korea University,
recording CAN traffic through the OBD-II port of a real vehicle [13]. It includes one normal dataset and four attack datasets:
DoS, Fuzzy, spoofing GEAR, and spoofing RPM. The sample
distribution of the Car Hacking dataset is presented in Table IV.
For detection window integrity, we classify each window based
on its content: a window containing both normal and attack data
is categorized as an attack window, with labels for both malicious
and normal frames. A window containing only normal data is
classified as a normal detection window.
To ensure a balanced and non-overlapping dataset division,
we first partitioned the normal samples in the normal.csv file
by allocating 80% to the training set and the remaining 20%
to the validation set. For attack samples contained in files such
as DoS.csv, Fuzzy.csv, GEAR.csv, and RPM.csv, we assigned
70% to the training set, 20% to the validation set, and the
remaining 10% to test the detection ability of STATGRAPH
on unknown attacks, since they never appeared during model
training. In addition to these attack samples, the test set also
includes residual normal samples that were not utilized during
training or validation, i.e., normal instances embedded within the
attack files. This partitioning strategy maintains a representative
distribution of normal and attack behaviors across all stages,
which is particularly important given the large volume of normal
messages in the dataset. It reflects real-world conditions, where
normal traffic dominates even in the presence of attacks, and
ensures clear separation between subsets. The same division is
consistently applied across all models to support fair comparison
and reproducibility.
2) Road Dataset: It includes a variety of CAN attacks collected from a passenger vehicle [19]. We choose the following
five advanced masquerade attacks whose sample distribution is
shown in Table V:

TABLE V
THE DISTRIBUTION OF REPRESENTATIVE MASQUERADE ATTACKS IN ROAD
DATASET

r Correlated Signal Masquerade Attack: The vehicle receives four false wheel speed values from injected malicious CAN messages, which disables the accelerator pedal
and even makes a restart of the automotive electronic and
electrical systems.
r Max Engine Coolant Temp Masquerade Attack: The vehicle receives an alarm of “engine coolant too high” that
may mislead drivers to operate unnecessarily, due to the
malicious modification of the engine coolant signal value
with the maximum (0xFF) by attackers.
r Max Speedometer Masquerade Attack: The speedometer
incorrectly displays the maximum value (0xFF) due to
the injected malicious CAN messages, and may cause the
driver to brake urgently.
r Reverse Light Off Masquerade Attack: The reverse lights of
the vehicle are maliciously turned off when in reverse-gear,
which may have danger to pedestrians due to lack of signal
light alerts.
r Reverse Light On Masquerade Attack: The reverse lights
of the vehicle are maliciously turned on when in drivegear, which may mislead the vehicles following behind
and result in improper operation.
The ROAD dataset provides both labeled signals translated
using the CAN-D algorithm [34] and raw, unlabeled data. Since
OEMs of passenger vehicles keep their proprietary CAN signal
encodings confidential and vary them across models, the CAN-D
algorithm is not always reliable for translating unknown CAN
signals. The translation process only involves the payload, excluding the CAN ID and timestamps.
To address this, we compare the IDs and timestamps of the
translated signals (in CSV format) with those of the raw data (in
log files), considering messages with identical IDs and timestamps as corresponding messages. These are then formatted to
match the structure of the Car Hacking Dataset.
E. Parameters Analysis
We evaluate the effects of different parameters that affect
the performance of STATGRAPH to find the optimal detection
window size N , number of hidden layer units h, and batchsize
B. The experiments are conducted as follows:

WANG et al.: STATGRAPH: EFFECTIVE IN-VEHICLE INTRUSION DETECTION VIA MULTI-VIEW STATISTICAL GRAPH LEARNING

Fig. 4.

Performance of STATGRAPH in Different Detection Window Size N .

Fig. 5.

Performance of STATGRAPH in Different Hidden-layer Units h.

1) Sensitivity to detection window size: Fig. 4 illustrates the
performance comparison for detection window sizes N ranging
from 25 to 200 (Car Hacking) and 100 to 800 (ROAD). The
results show that the impact of N is dataset-dependent. On the
Car Hacking dataset, the detection window size significantly
influences accuracy due to the simplicity and abrupt nature of
the attacks, where small changes in N can alter the detection
outcomes noticeably. The highest F1-Score is achieved with
N = 50. In contrast, on the ROAD dataset, which contains more
stealthy and complex attacks mimicking normal behavior, the
detection performance is relatively stable across a wide range of
window sizes. This indicates that once N is sufficiently large to
capture the temporal and statistical patterns, further increases do
not dramatically affect detection. The best F1-Score on ROAD
is achieved with N = 400.
These findings imply that while the model leverages N to
construct both TCG and CRG structures, it maintains superior
performance when N is reasonably configured to align with the
dataset’s temporal characteristics.
This robustness can be partly attributed to the structural
design of STATGRAPH. The TCG captures temporal rhythm
changes through edge weight and node degree distributions,
rather than relying on absolute message indices, while the
CRG encodes short-term dependencies through local contextual
relationships. Consequently, even under fluctuating message
frequencies, structural anomalies remain detectable. Empirical
results show that abrupt attacks in the Car Hacking dataset
exhibit higher sensitivity to N , whereas stealthy attacks in the
ROAD dataset benefit from larger windows that accumulate
sufficient statistical deviations. These results demonstrate that
the choice of N is closely related to the nature of attacks and
highlight the importance of proper parameter configuration for
practical deployment.
2) Sensitivity to number of hidden layer units h: Fig. 5
compares performance across different latent space dimensions,
ranging from 16 to 64. The results reveal that excessively large
dimensions lead to a significant decline in F1-Score, likely due

6345

Fig. 6.

Performance of STATGRAPH in Different Batchsize B.

Fig. 7.

Experimental Flowchart of Vehicle-Cloud Detection Architecture.

to overfitting. Conversely, overly small dimensions result in
substantial information loss during encoding, severely degrading
GCN performance. A latent space dimension of 32 achieves the
best F1-Score on both datasets, enabling STATGRAPH to balance
training efficiency and accuracy.
3) Sensitivity to batch size: Fig. 6 compares performance
across batch sizes from 20 to 80 on the Car Hacking dataset
and from 1 to 20 on the ROAD dataset. The results indicate that
both excessively large and small batch sizes degrade intrusion
detection performance. The highest F1-Score is achieved with
a batch size B of 50 for the Car Hacking dataset and 5 for the
ROAD dataset, respectively.
F. Vehicle-Cloud Collaboration Framework
In real-world deployment, in-vehicle IDS must operate under
strict resource constraints while ensuring real-time responsiveness and high detection accuracy. To meet these challenges, we
adopt a vehicle-cloud collaborative framework that decouples
training and inference, assigning them to the cloud and vehicle sides respectively for improved efficiency and robustness.
Specifically, the cloud server performs offline training and optimization, while the vehicle-side platform (e.g., NVIDIA Jetson
Nano T206) handles real-time inference. As shown in Fig. 7,
the interaction between cloud and vehicle is bidirectional and
continuous:
On the cloud side, a centralized platform handles model
training and optimization by aggregating CAN message streams
from multiple vehicles. It performs preprocessing and iteratively improves the model through incremental retraining with
new attack patterns, as well as hyperparameter optimization.
The trained model is then deployed to vehicle-side devices. In
practice, dataset aggregation, model training, validation, and
hyperparameter tuning are performed in the cloud, while the

6346

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 5, MAY 2026

Fig. 9.

Fig. 8.

Running Time Comparison Evaluation.

vehicle receives updated model weights, ensuring that detection
capabilities evolve as attack scenarios change.
On the vehicle side, a lightweight embedded platform (e.g.,
Jetson Nano T206) conducts real-time inference using the
cloud-trained model. It monitors incoming CAN messages and
triggers alerts upon detecting anomalies. Detection outcomes
and runtime metadata are uploaded to the cloud, enabling the
cloud to retrain or fine-tune the model based on evolving attack
strategies or environmental changes. It is important to emphasize
that the vehicle is responsible solely for inference, while all
training is conducted in the cloud. Model updates are performed
by periodically transmitting retrained weights from the cloud
to the vehicle, thereby avoiding computational bottlenecks on
resource-constrained devices.
This collaborative architecture balances cloud-side computational power with vehicle-side responsiveness, ensuring scalable, low-latency, and adaptive intrusion detection. As validated
in Figs. 8 and 9, this architecture ensures real-time feasibility:
the cloud handles training and inference efficiently, while the
vehicle-side platform achieves low-latency detection within limited memory resources. These results confirm that centralizing
training in the cloud and deploying lightweight inference on
vehicles is a practical and effective strategy. Based on this
deployment architecture, we conduct performance evaluations
of STATGRAPH and several baseline methods in both cloud and
vehicle environments. Figs. 8 and 9 show the average inference
time and memory usage of each method, respectively.
The results indicate that cloud devices generally offer
lower inference times due to greater computational power. For

Memory Comparison Evaluation.

instance, G-IDCS ML_classifier achieves low latency by summarizing 200 CAN messages into a single feature vector per
window, while CAN-RF detects messages individually with
minimal processing overhead. Deep learning models such as
CAN-MLP and CAN-LSTM maintain stable but higher inference times due to their network complexity. Image-based models (e.g., EfficientNet, MobileNetV3, CANet) incur additional
time costs from raw-to-image transformations. STATGRAPH performs competitively in the cloud but exhibits increased latency
on edge devices due to time-intensive graph construction and
preprocessing.
In terms of memory consumption, most models consume
more resources in cloud environments. However, methods like
CAN-RF, CAN-MLP, CAN-LSTM, and STATGRAPH show favorable memory footprints on embedded hardware, making
them viable for real-world deployment. Notably, STATGRAPH
successfully meets real-time inference requirements under resource constraints, demonstrating its practical applicability.
To further reduce communication and computation overhead, the current implementation deploys the IDS on bypassmonitoring devices connected to the CAN bus rather than directly on ECUs. This design balances detection efficiency with
system safety and scalability.
In summary, our vehicle-cloud collaborative deployment
aligns with real-world in-vehicle environments, allowing STATGRAPH to deliver fine-grained, real-time intrusion detection
while leveraging cloud-side computational advantages for
model training and continuous adaptation. This division of labor
enables high detection accuracy and low latency, while ensuring scalability and deployability under constrained in-vehicle
resources.
G. Detection Performance
The effectiveness of STATGRAPH is evaluated against state-ofthe-art IVN intrusion detection methods. Experimental results
on in-vehicle equipment demonstrate that STATGRAPH outperforms competing approaches in detecting anomalies across both
datasets.
Tables VI and VII report the Accuracy, Precision, Recall,
F1-score, and Window Size/Label Number for all evaluated
methods on the Car Hacking dataset and ROAD dataset. The
Window Size/Label Number metric reflects detection granularity

WANG et al.: STATGRAPH: EFFECTIVE IN-VEHICLE INTRUSION DETECTION VIA MULTI-VIEW STATISTICAL GRAPH LEARNING

6347

TABLE VI
TEST RESULTS OF EACH METHOD FOR DIFFERENT ATTACKS IN CAR HACKING DATASET

TABLE VII
BEST TEST RESULTS OF EACH METHOD FOR DIFFERENT ATTACKS IN ROAD DATASET

by measuring the ratio between the number of messages within
a detection window and the number of classification decisions
produced. Traditional coarse-grained methods assign one label
per window regardless of its size, leading to high ratios (e.g.,
100/1). In contrast, STATGRAPH performs detection at the message level, achieving a 1/1 ratio that represents significantly finer
granularity.
As the nature of binary detection methods, Graph-based
IDS [11] and G-IDCS TH_classifier [12] are fail to set consistent
thresholds for multiple attack categories, and thus we only place
the results of those multi-classification methods when detecting
the Mixing Fabrication Attack and Mixing Masquerade Attack.
On the relatively simpler Car Hacking dataset, STATGRAPH
achieves near-perfect results, with 99.40% accuracy and 94.03%
F1-score. In contrast, the ROAD dataset poses a greater

challenge due to its stealthy masquerade attacks that preserve
the statistical properties of normal traffic while subtly altering
payload values. Despite this, STATGRAPH maintains strong performance, reaching 97.91% accuracy and 97.46% F1-score.
This robustness is attributed to the complementary roles of the
TCG and CRG. The TCG captures long-term statistical behavior
by aggregating messages with the same CAN ID, enabling
detection of anomalies in transmission periodicity. The CRG
complements this by modeling short-term contextual structure:
it preserves the original temporal sequence of messages and
connects those with similar IDs, making it sensitive to abrupt
changes in payload distributions and inconsistencies among correlated signals within data field. These two perspectives jointly
enhance the model’s ability to identify both global and localized
disruptions.

6348

Crucially, the integration of TCG-based timing anomalies
and CRG-reflected payload inconsistencies provides a rich and
interpretable basis for anomaly detection. Variations in message
periodicity, sudden signal deviations, and unexpected changes
in signal correlation patterns all serve as interpretable cues
for distinguishing normal from malicious behavior. Together,
these mechanisms support fine-grained, message-level detection, contributing to both the high accuracy and the practical
explainability of STATGRAPH.
Furthermore, baseline model generalizability varies considerably. For instance, EfficientNet and MobileNetV3 perform well
on the ROAD dataset but poorly on the Car Hacking dataset,
whereas CAN-RF, CAN-MLP, CAN-LSTM, and CANet exhibit
the opposite trend. In contrast, STATGRAPH consistently achieves
the highest Accuracy and F1-score on both datasets, demonstrating superior adaptability and robustness. The Window Size/Label
Number metric further highlights a key advantage of STATGRAPH
over existing graph-based approaches. While most methods
operate at the window or segment level, STATGRAPH generates
predictions for each message individually. This fine-grained
detection enables earlier threat identification and more precise
localization, which is especially valuable in time-sensitive and
safety-critical IVN environments.
H. Fine-Grained Potential Exploration
Previous studies typically labeled an entire segment of consecutive CAN messages as an attack sample if it contained at least
one injected message, while segments without injections were
labeled as normal [10]. However, aside from a few graph-based
methods [11], [12], prior work has not provided a clear rationale
for the choice of sample size.
To address this gap, we define sample size criteria based on
CAN bus transmission rates and latency requirements, referencing application scenarios in Intelligent Connected Vehicles and
Industrial Control Internet. Industrial automation and remote
driving generally require latency below 10ms . Given a CAN
bus speed of 125kbps to 1Mbps and a maximum extended frame
length of 150 bits, the bus can transmit at least 8 messages and
on average 34 messages every 10ms at 500kbps. Based on this,
we define three recognition granularity intervals: 0 ∼ 8, 8 ∼ 34,
and 34 ∼ +∞, to evaluate the performance of coarse-grained
methods across varying levels of granularity. Corresponding
detection window sizes are set to 3, 27, and 54 for comparison.
STATGRAPH is evaluated against prior methods using F1-score
and IG under these settings, as reported in Table VIII. Notably,
STATGRAPH performs detection at the per-message level regardless of the window size N = (3, 27, 54), yielding stable and
consistent results across all intervals.
It is evident that STATGRAPH achieves the highest F1-score
and IG values on both datasets. On the Car Hacking dataset,
among the remaining models, CANet delivers the best performance when N = 54, suggesting that it relies on a larger
detection window to accumulate sufficient contextual information for effective classification. On the ROAD dataset, where
normal data accounts for over 90% of the samples, many models
tend to classify most messages as normal. Compared to other

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 5, MAY 2026

TABLE VIII
TEST RESULTS OF EACH METHOD IN MIX ATTACKS (REAL-TIME DETECTION:
N = 3, SEMI-REAL-TIME DETECTION: N = 27 AND OFFLINE DETECTION:
N = 54 )

methods, STATGRAPH consistently achieves higher IG values
and F1-scores across all window sizes on both datasets, demonstrating its superior accuracy and robustness in the presence of
imbalanced data distributions.
I. Ablation Experiment
Within STATGRAPH, the TCG and CRG are designed to capture distinct structural properties of CAN traffic, grounded in
different theoretical assumptions. The TCG, proposed in the
Global Feature Fusion Module, aggregates all messages with
the same CAN ID to form node-level statistical features such
as frequency and entropy. This global representation captures
long-range behavioral patterns across messages sharing the same
ID that is effective for detecting distributional shifts caused by
attacks. In contrast, the CRG, constructed in the Association
Enhancement Module, retains each message as an individual
node and connects them based on temporal adjacency and ID
similarity. By preserving both temporal order and message-level
granularity, the CRG captures fine-grained structural dynamics
and enables the detection of localized disruptions that may be
overlooked by aggregated models. This dual-graph architecture
allows STATGRAPH to jointly encode global distributional context and localized temporal structure, offering a comprehensive
representation of communication dependencies in IVNs.
To assess the individual contributions of global feature fusion
and temporal adjacency enhancement, we conduct an ablation
study. In the Node ablation setting (excluding the TCG), only
8-dimensional payload vectors are used as node features, excluding the fused global attributes. This allows us to evaluate
the impact of global feature fusion on node representation. In
the Edge ablation setting (excluding the CRG), the adjacency
matrix generated by the temporal association module is replaced
with a unit matrix, thereby removing temporal dependencies and
enabling assessment of correlation modeling.
The effectiveness of this design is validated by the ablation
results shown in Fig. 10. Although the Edge ablation model
achieves slightly higher accuracy and F1-score on the Car
Hacking dataset, it suffers a substantial drop in recall, indicating
that temporal adjacency is critical for detecting low-frequency
or stealthy attacks. The Node ablation model shows consistent
performance degradation across all major metrics, underscoring

WANG et al.: STATGRAPH: EFFECTIVE IN-VEHICLE INTRUSION DETECTION VIA MULTI-VIEW STATISTICAL GRAPH LEARNING

Fig. 10. Performance of different ablation components of STATGRAPH on two
datasets.

the role of global feature fusion in improving node representation
and detection accuracy.
Taken together, these findings confirm that STATGRAPH
achieves optimal performance when both temporal correlations
and global contextual features are preserved. In particular, improvements in recall and F1-score underscore the model’s ability
to deliver fine-grained and robust intrusion detection in complex
in-vehicle network environments.
V. DISCUSSION
The experimental results demonstrate that STATGRAPH consistently outperforms existing methods on both the Car Hacking
dataset and the ROAD dataset when evaluated independently.
Although some alternatives achieve satisfactory performance,
such as EfficientNet and MobileNetV3 on the ROAD dataset,
and CANet, G-IDCS ML_classifier, CAN-RF, CAN-MLP, and
CAN-LSTM on the Car Hacking dataset, STATGRAPH achieves
the most robust and consistent results across both datasets.
While our TCG design shares conceptual similarities
with [11], STATGRAPH introduces key advancements by incorporating the CRG and enabling fine-grained, message-level
classification. In contrast to [11], which relies on window-level
statistical features, STATGRAPH performs per-message detection
by fusing global statistical context with local payload and signals dynamics. This allows it to capture subtle anomalies (e.g.,
mixing masquerade attacks) that are often missed by traditional
threshold-based approaches.
In addition, STATGRAPH is deployed within a practical
vehicle-cloud collaborative framework, delivering strong detection performance even in the presence of stealthy and lowfrequency masquerade attacks. These architectural innovations
and deployment strategies represent a substantial and novel
contribution to graph-based intrusion detection for IVNs.
In real in-vehicle environments, message transmission frequencies vary with operating conditions, which may limit the
practicality of fixed-window strategies. This limitation is not
specific to our work but represents a broader challenge for IDS
deployment. As future work, we plan to incorporate adaptive
window mechanisms that adjust N dynamically based on realtime message rates. We also aim to investigate multi-scale window modeling, where detection results across different temporal
resolutions are integrated to improve robustness against both
bursty and stealthy attacks.

6349

Moreover, the limitations of supervised models, particularly
the reliance on labeled data, remain a key challenge. This
motivates the development of self-supervised and unsupervised
frameworks that can adapt to evolving threats without annotated
attack data. The graph-based representation in our framework,
comprising both the TCG and CRG, provides a structured
input space well-suited for self-supervised objectives, including contrastive learning, masked signal prediction, and graph
structure reconstruction. For instance, intrusion detection can
be performed by applying perturbations to subgraphs and using
graph contrastive learning to capture intrinsic features of normal
behavior, allowing the model to differentiate between benign
and malicious graphs without ground-truth labels. Extending
STATGRAPH with such self-supervised strategies thus offers a
promising direction to enhance robustness in low-label and
zero-day attack scenarios.
Another important direction is addressing data imbalance,
which can impair detection under sparse or skewed attack distributions. Future work may incorporate synthetic data generation
or adversarial training strategies to enhance model robustness.
In addition, improving model interpretability is essential for
practical deployment. Post-hoc interpretation techniques, such
as GNNExplainer [35] and Integrated Gradients [36], can be
employed to identify the node features (derived from the TCG)
or edge structures (captured by the CRG) that contribute most
significantly to anomaly classification. These insights can help
practitioners assess whether the model’s decisions align with
domain knowledge, thereby increasing trust and enhancing the
diagnostic value of intrusion detection systems in safety-critical
onboard environments.
VI. RELATED WORK
Deep learning-based intrusion detection methods hold significant promise for securing IVNs, but they face critical limitations
in detection granularity and effectiveness against sophisticated
attacks, which constrain their practical deployment [4], [6],
[9], [21], [22]. First, most existing approaches perform coarsegrained detection, identifying anomalies only at the detection
window level rather than at the level of individual CAN messages [14], [15]. This lack of fine-grained resolution undermines
their diagnostic reliability and limits timely threat localization.
Second, as attack strategies evolve, increasingly advanced masquerade attacks have emerged. These attacks manipulate the
payload content while mimicking the timing and frequency
of legitimate messages, allowing them to evade detection by
existing models that rely primarily on statistical or temporal
patterns [5], [7], [19].
Besides, graph-based intrusion detection methods have
gained traction in IVN security due to their strong abstraction capabilities in modeling interactions among heterogeneous
ECUs, effectively capturing the collaborative processes and data
distribution patterns of the CAN bus. However, most existing graph-based approaches focus predominantly on detecting
relatively simple types of attacks [11], while the detection of
advanced and stealthy masquerade attacks remains significantly
underexplored. Methods such as [11], [12], [37], and [38] rely

6350

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 5, MAY 2026

solely on CAN IDs and overlook the critical need to learn
payload variation patterns. As a result, they are ineffective
against masquerade attacks that precisely replicate the statistical properties of legitimate messages but subtly manipulate
payload thresholds. Furthermore, many graph-based methods
adopt coarse-grained detection strategies, identifying anomalies
only after large message intervals (e.g., every 1200 messages
in [11] and every 200 in [12]), which fails to satisfy the realtime responsiveness required in IVN applications. In contrast to
most existing single-view models [11], [12], [37], [38], STATGRAPH introduces a multi-view graph representation that captures diverse relationships among CAN messages. By integrating different graph perspectives, STATGRAPH is better positioned
to detect subtle and complex intrusion behaviors with higher
fidelity.
VII. CONCLUSION
Intrusion detection based on deep neural networks and graph
learning has advanced IVN security, yet improving detection
granularity and identifying complex attacks remains challenging. To address these limitations, we propose STATGRAPH, a
fine-grained IVN intrusion detection framework that effectively
detects both simple attacks (e.g., fabrication) and sophisticated
ones (e.g., masquerade) by leveraging multi-view statistical
graph learning on CAN messages. STATGRAPH adopts a dualgraph design in which the TCG captures global temporal and
distributional patterns, while the CRG retains local adjacency
and semantic consistency at the message level. Their integration
through graph convolution enables cross-graph feature propagation, allowing STATGRAPH to effectively capture variations in
message periodicity, payload content, and signal correlations.
We further introduce the Identification Granularity (IG) metric
to quantify detection resolution, providing a foundation for
future research on fine-grained intrusion detection. Extensive
experiments demonstrate that STATGRAPH outperforms traditional machine learning models, deep neural networks, and
existing graph-based methods in terms of runtime efficiency,
detection accuracy, and granularity across both the Car Hacking
and ROAD datasets. Future work will explore attack traceability
using fine-grained detection and develop unsupervised intrusion
detection mechanisms to address class imbalance problems in
real-world scenarios.
REFERENCES
[1] H. H. Jeong, Y. C. Shen, J. P. Jeong, and T. T. Oh, “A comprehensive
survey on vehicular networking for safe and efficient driving in smart
transportation: A focus on systems, protocols, and applications,” Veh.
Commun., vol. 31, Oct. 2021, Art. no. 100349.
[2] B. Lampe and W. Meng, “Intrusion detection in the automotive domain:
A comprehensive review,” IEEE Commun. Surv. Tuts., vol. 25, no. 4,
pp. 2356–2426, Fourth Quarter 2023.
[3] X. Zhou, W. Liang, J. She, Z. Yan, and K. I.-K. Wang, “Two-layer federated
learning with heterogeneous model aggregation for 6G supported Internet
of Vehicles,” IEEE Trans. Veh. Technol, vol. 70, no. 6, pp. 5308–5317,
Jun. 2021.
[4] Y. Xie, G. Zeng, R. Kurachi, F. Xiao, H. Takada, and S. Hu, “Timing analysis of CAN FD for security-aware automotive cyber-physical systems,”
IEEE Trans. Dependable Secure Comput., vol. 20, no. 4, pp. 3064–3078,
Jul./Aug. 2023.

[5] A. Nichelini, C. A. Pozzoli, S. Longari, M. Carminati, and S. Zanero,
“CANova: A hybrid intrusion detection framework based on automatic signal classification for CAN,” Comput. Secur., vol. 128, 2023,
Art. no. 103166.
[6] M. L. Han, B. I. Kwak, and H. K. Kim, “TOW-IDS: Intrusion detection
system based on three overlapped wavelets for automotive ethernet,” IEEE
Trans. Inf. Forensics Secur., vol. 18, pp. 411–422, 2023.
[7] M. H. Shahriar, Y. Xiao, P. Moriano, W. Lou, and Y. T. Hou, “CANShield:
Deep learning-based intrusion detection framework for controller area
networks at the signal-level,” IEEE Internet Things J., vol. 10, no. 24,
pp. 22111–22127, Dec. 2023.
[8] Z. Lu, Q. Wang, X. Chen, G. Qu, Y. Lyu, and Z. Liu, “LEAP: A lightweight
encryption and authentication protocol for in-vehicle communications,” in
Proc. IEEE Intell. Transp. Syst. Conf., 2019, pp. 1158–1164.
[9] S. Rajapaksha, H. Kalutarage, M. O. Al-Kadri, A. Petrovski, G. Madzudzo,
and M. Cheah, “AI-based intrusion detection systems for in-vehicle networks: A survey,” ACM Comput. Surv., vol. 55, no. 11, pp. 1–40, Feb. 2023.
[10] K. Wang, A. Zhang, H. Sun, and B. Wang, “Analysis of recent deeplearning-based intrusion detection methods for in-vehicle network,” IEEE
Trans. Intell. Transp. Syst., vol. 24, no. 2, pp. 1843–1854, Feb. 2023.
[11] R. Islam, R. U. D. Refat, S. M. Yerram, and H. Malik, “Graph-based
intrusion detection system for controller area networks,” IEEE Trans.
Intell. Transp. Syst., vol. 23, no. 3, pp. 1727–1736, Mar. 2022.
[12] S. B. Park, H. J. Jo, and D. H. Lee, “G-IDCS: Graph-based intrusion
detection and classification system for CAN protocol,” IEEE Access,
vol. 11, pp. 39213–39227, 2023.
[13] H. M. Song, J. Woo, and H. K. Kim, “In-vehicle network intrusion detection using deep convolutional neural network,” Veh. Commun., vol. 21,
no. 100198, pp. 1–13, Jan. 2020.
[14] T.-N. Hoang and D. Kim, “Detecting in-vehicle intrusion via semisupervised learning-based convolutional adversarial autoencoders,” Veh.
Commun., vol. 38, 2022, Art. no. 100520.
[15] A. K. Desta, S. Ohira, I. Arai, and K. Fujikawa, “ID sequence analysis
for intrusion detection in the CAN bus using long short term memory
networks,” in Proc. 2020 IEEE Int. Conf. Pervasive Comput. Commun.
Workshops, 2020, pp. 1–6.
[16] M. Hanselmann, T. Strauss, K. Dormann, and H. Ulmer, “CANet: An
unsupervised intrusion detection system for high dimensional CAN bus
data,” IEEE Access, vol. 8, pp. 58194–58205, 2020.
[17] H. K. Kalutarage, M. O. Al-Kadri, M. Cheah, and G. Madzudzo, “Contextaware anomaly detector for monitoring cyber attacks on automotive CAN
bus,” in Proc. 3rd ACM Comput. Sci. Cars Symp., 2019, pp. 1–8.
[18] M. Jedh, L. B. Othmane, N. Ahmed, and B. Bhargava, “Detection of
message injection attacks onto the CAN bus using similarities of successive
messages-sequence graphs,” IEEE Trans. Inf. Forensics Secur., vol. 16,
pp. 4133–4146, 2021.
[19] M. E. Verma et al., “A comprehensive guide to CAN IDS data and
introduction of the road dataset,” PLoS One, vol. 19, no. 1, pp. 1–32,
Jan. 2024.
[20] F. Fenzl, R. Rieke, and A. Dominik, “In-vehicle detection of targeted CAN
bus attacks,” in Proc. 16th Int. Conf. Availability Rel. Secur., 2021, pp. 1–7.
[21] S. Jeong, S. Lee, H. Lee, and H. K. Kim, “X-CANIDS: Signal-aware
explainable intrusion detection system for controller area network-based
in-vehicle network,” IEEE Trans. Veh. Technol, vol. 73, no. 3, pp. 3230–
3246, Mar. 2024.
[22] S. Jeong, H. K. Kim, M. L. Han, and B. I. Kwak, “AERO: Automotive
ethernet real-time observer for anomaly detection in in-vehicle networks,”
IEEE Trans. Ind. Informat., vol. 20, no. 3, pp. 4651–4662, Mar. 2024.
[23] G. Xie, L. T. Yang, Y. Yang, H. Luo, R. Li, and M. Alazab, “Threat analysis
for automotive CAN networks: A GAN model-based intrusion detection
technique,” IEEE Trans. Intell. Transp. Syst., vol. 22, no. 7, pp. 4467–4477,
Jul. 2021.
[24] C. Miller and C. Valasek, “Advanced CAN injection techniques for vehicle
networks,” in Proc. Black Hat USA, 2016, pp. 1–28.
[25] T. N. Kipf and M. Welling, “Semi-supervised classification with graph
convolutional networks,” 2017, arXiv:1609.02907v4.
[26] M. Tan and Q. Le, “EfficientNet: Rethinking model scaling for convolutional neural networks,” in Proc. 36th Int. Conf. Mach. Learn., 2019,
pp. 1–10.
[27] A. Howard et al., “Searching for MobileNetV3,” in Proc. IEEE/CVF Int.
Conf. Comput. Vis., 2019, pp. 1314–1324.
[28] T. Moulahi, S. Zidi, A. Alabdulatif, and M. Atiquzzaman, “Comparative performance evaluation of intrusion detection based on machine
learning in in-vehicle controller area network bus,” IEEE Access, vol. 9,
pp. 99595–99605, 2021.

WANG et al.: STATGRAPH: EFFECTIVE IN-VEHICLE INTRUSION DETECTION VIA MULTI-VIEW STATISTICAL GRAPH LEARNING

[29] I. Berger, R. Rieke, M. Kolomeets, A. Chechulin, and I. Kotenko, “Comparative study of machine learning methods for in-vehicle intrusion detection,” in Proc. Int. Workshop Secur. Privacy Requirements Eng., 2018,
pp. 85–101.
[30] H. Lee, S. H. Jeong, and H. K. Kim, “OTIDS: A novel intrusion detection
system for in-vehicle network by using remote frame,” in Proc. 15th Annu.
Conf. Privacy Secur. Trust, 2017, pp. 57–66.
[31] M. L. Han, B. I. Kwak, and H. K. Kim, “Anomaly intrusion detection
method for vehicular networks based on survival analysis,” Veh. Commun.,
vol. 14, pp. 52–63, 2018.
[32] E. Seo, H. M. Song, and H. K. Kim, “GIDS: GAN based intrusion detection
system for in-vehicle network,” in Proc. 16th Annu. Conf. Privacy Secur.
Trust, 2018, pp. 1–6.
[33] G. Dupont, A. Lekidis, J. I. den Hartog, and S. Etalle, “Automotive
controller area network (CAN) bus intrusion dataset v2,” 4TU.Centre for
Research Data, Dept. Math. Comput. Sci., TU Eindhoven, Nov. 2019, doi:
10.4121/uuid:b74b4928-c377-4585-9432-2004dfa20a5d.
[34] M. E. Verma, R. A. Bridges, J. J. Sosnowski, S. C. Hollifield, and M. D.
Iannacone, “CAN-D: A modular four-step pipeline for comprehensively
decoding controller area network data,” IEEE Trans. Veh. Technol, vol. 70,
no. 10, pp. 9685–9700, Oct. 2021.
[35] Z. Ying, D. Bourgeois, J. You, M. Zitnik, and J. Leskovec, “GNNExplainer:
Generating explanations for graph neural networks,” in Proc. Int. Conf.
Neural Inf. Process. Syst., 2019, Art. no. 829.
[36] Y. Wang, T. Zhang, X. Guo, and Z. Shen, “Gradient based feature attribution in explainable AI: A technical review,” 2024, arXiv:2403.10415.
[37] H. Zhang, K. Zeng, and S. Lin, “Federated graph neural network for fast
anomaly detection in controller area networks,” IEEE Trans. Inf. Forensics
Secur., vol. 18, pp. 1566–1579, 2023.
[38] R. Islam, M. K. Devnath, M. D. Samad, and S. M. J. A. Kadry, “GGNB:
Graph-based Gaussian naive Bayes intrusion detection system for CAN
bus,” Veh. Commun., vol. 33, Jan. 2022, Art. no. 100442.

Kai Wang (Member, IEEE) received the PhD degree
in communication and information systems from Beijing Jiaotong University, China, in 2014. He is a full
professor with the School of Computer Science and
Technology, Weihai and with the Faculty of Computing, Harbin, Harbin Institute of Technology, China.
His research interests include trustworthy AI and
network intrusion detection. He has published more
than 40 papers in prestigious international journals,
including the IEEE Transactions on Services Computing, IEEE Transactions on Intelligent Transportation
Systems, ACM Transactions on Internet Technology, ACM Transactions on
Intelligent Systems and Technology, etc. From 2017 to 2019, he was a postdoc
researcher in computer science and technology with Tsinghua University, China.
He is a member of the ACM, and a senior member of the China Computer
Federation (CCF).

Qiguang Jiang received the master’s degree in computer science and technology from the Harbin Institute of Technology (HIT), China. Her research
interests include intelligent and efficient in-vehicle
intrusion detection models.

6351

Bailing Wang (Member, IEEE) received the PhD
degree in computer architecture from the Harbin Institute of Technology (HIT), China, in 2006. He is a
full professor with the Harbin Institute of Technology (Weihai) Qingdao Research Institute, Qingdao,
China. His research interests include information content security and industrial control network security.
He has published more than 80 papers in prestigious
international journals and been selected for the China
national talent plan.

Yulei Wu (Senior Member, IEEE) received the BSc
(1st class hons.) degree in computer science and the
PhD degree in computing and mathematics from the
University of Bradford, United Kingdom. He is an
associate professor with the Faculty of Engineering
and the Bristol Digital Futures Institute, University
of Bristol, U.K. His research mainly focuses on network digital twins, native AI networks and systems,
edge AI, and trustworthy AI. He has published more
than 10 authored/edited monograph books, and more
than 150 peer-reviewed research papers in prestigious
international journals and conferences. He serves as an associate editor of the
IEEE Transactions on Network and Service Management and IEEE Transactions
on Network Science and Engineering, as well as an editorial board member
of the Computer Networks, Future Generation Computer Systems, and Nature
Scientific Reports at Nature Portfolio. He is chairing an IEEE Special Interest
Group (SIG) on Ethical AI for future networks and digital infrastructure. He is
a senior member of the ACM.

Hongke Zhang (Fellow, IEEE) received the PhD degree in communication and information system from
the University of Electronic Science and Technology
of China, Chengdu, China, in 1992. He is currently a
professor with the School of Electronic and Information Engineering, Beijing Jiaotong University, Beijing, China, where he currently directs the National
Engineering Center of China on Mobile Specialized
Network. His current research interests include architecture and protocol design for the future Internet
and specialized networks. He currently serves as an
associate editor of the IEEE Transactions on Network and Service Management
and IEEE Internet of Things Journal. He is an academician of China Engineering
Academy.
PAPER_TEXT
