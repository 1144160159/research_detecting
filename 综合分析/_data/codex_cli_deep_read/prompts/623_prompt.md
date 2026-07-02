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
# [623] CATwin-IDS: Context-Aware Intrusion Detection System for Both In-Vehicle and External-Vehicle Networks via Digital Twin
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
编号：623
题名：CATwin-IDS: Context-Aware Intrusion Detection System for Both In-Vehicle and External-Vehicle Networks via Digital Twin
年份：2026
DOI：10.1109/tits.2026.3669369
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2026.3669369.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全
相关性：强相关，分数 13
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\623.txt
- 原始字符数：72794
- 本次发送字符数：72794
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

1

CATwin-IDS: Context-Aware Intrusion Detection
System for Both In-Vehicle and External-Vehicle
Networks via Digital Twin
Chang Liu , Member, IEEE, Yurong Zhang, Graduate Student Member, IEEE, Zheng Xue ,
Zhengguo Sheng , Senior Member, IEEE, Jiawen Kang , Senior Member, IEEE,
and Guojun Han , Senior Member, IEEE
Abstract—With the rapid development of the Internet of
Vehicles (IoV), the tight coupling between In-Vehicle Networks
(IVN) and External Vehicle Networks (EVN) has made vehicular
systems vulnerable to sophisticated cross-network attack chains.
Existing Intrusion Detection Systems (IDS), however, typically
operate in isolation on either IVN or EVN, and lack effective
context-aware mechanisms for capturing inter-domain dependencies. To overcome this limitation, we propose CATwin-IDS,
a context-aware intrusion detection framework that integrates
digital twin technology with a lightweight Distilled Bidirectional Encoder Representations from Transformers (DistilBERT)
model. In our design, Conditional Mutual Information (CMI)
and Borderline Synthetic Minority Over-sampling Technique
(Borderline-SMOTE) are applied for feature optimization and
data balancing, while Temporal Self-Attention (TSA) enhances
the modeling of spatiotemporal dependencies across heterogeneous traffic. The digital twin provides real-time bidirectional
synchronization and a simulation environment, enabling proactive adaptation to dynamic threats. Experimental results on
benchmark datasets (Car-Hacking, CICIoV2024, CICIDS2018,
CICIoT2023) demonstrate that CATwin-IDS achieves higher
accuracy and real-time efficiency compared with state-of-the-art
methods, providing a holistic solution for securing IoV against
cross-network intrusions.
Index Terms—IoV security, intrusion detection system, DistilBERT, digital twin, pre-trained transformer model.

I. I NTRODUCTION
HE rapid advancement of the Internet of Vehicles
(IoV) has revolutionized the automotive industry. As
vehicles become increasingly connected, they communicate
with diverse entities, enhancing convenience and operational
efficiency [1]. However, this connectivity also exposes the

T

Received 11 September 2025; revised 12 January 2026; accepted 22
February 2026. This work was supported in part by the Natural Science
Foundation of China under Grant 62501174 and Grant 62471151 and in
part by Guangdong Introducing Innovative and Entrepreneurial Teams of
“The Pearl River Talent Recruitment Program” under Grant 2021ZT09X044.
The Associate Editor for this article was X. Li. (Corresponding author:
Zheng Xue.)
Chang Liu, Yurong Zhang, Zheng Xue, and Guojun Han are
with the School of Information Engineering, Guangdong University
of Technology, Guangzhou 510006, China (e-mail: liuchang@gdut.
edu.cn; 2112303067@mail2.gdut.edu.cn; xuezheng@gdut.edu.cn; gjhan@
gdut.edu.cn).
Zhengguo Sheng is with the Department of Engineering and Design, University of Sussex, BN1 9RH Brighton, U.K. (e-mail: z.sheng@sussex.ac.uk).
Jiawen Kang is with the School of Automation, Guangdong University of
Technology, Guangzhou 510006, China (e-mail: kavinkang@gdut.edu.cn).
Digital Object Identifier 10.1109/TITS.2026.3669369

automotive ecosystem to numerous security risks [2]. The
IoV framework consists of the In-Vehicle Network (IVN)
[3] and the External Vehicle Network (EVN) [4]. The IVN
coordinates communication among Electronic Control Units
(ECUs), primarily employing Controller Area Network (CAN)
bus technology, which inherently lacks authentication mechanisms [5]. This weakness allows attackers to infiltrate the IVN
via physical interfaces such as Universal Serial Bus (USB)
or On-Board Diagnostics (OBD) [6]. In contrast, the EVN
leverages Vehicle to Everything (V2X) technology for external interactions and faces wireless threats through Wireless
Fidelity (Wi-Fi), Bluetooth, or cellular networks [7], as well as
physical-layer vulnerabilities in emerging ambient backscatter
NOMA systems [8], [9]. Moreover, the IoV relies on data
exchange with cloud services via Road Side Units (RSUs)
[10], which introduces additional vulnerabilities.
The IVN and EVN are deeply interdependent through
vehicle gateways and cloud platforms [11]. EVN-acquired
data (e.g., road conditions, traffic signals) directly influences
IVN control decisions (e.g., speed modulation, route planning), while IVN status data (e.g., vehicle speed, diagnostic
information) is transmitted externally. This bidirectional flow
enables new attack vectors: adversaries may exploit EVN vulnerabilities to compromise the IVN or leverage IVN flaws to
disrupt EVN communications. Consequently, siloed Intrusion
Detection Systems (IDS) focusing on IVN or EVN alone fail
to address these cross-network attack chains. A context-aware
intrusion detection approach that jointly analyzes heterogeneous data sources is therefore essential.
Digital twin technology offers unique opportunities for
enhancing IoV security. By creating real-time digital replicas
of vehicles and networks, digital twins enable bidirectional synchronization and dynamic context modeling between
physical and virtual environments [12]. Unlike static IDS
frameworks, a digital twin-based IDS can simulate crossnetwork attacks, generate synthetic rare samples, and adapt
detection models to evolving conditions. Particularly in the
IoV domain, its ability to integrate multi-modal sensor inputs
(Radio Detection And Ranging (RADAR), Light Detection
and Ranging (LiDAR), Global Positioning System (GPS),
cameras) [13] with network data enables comprehensive situational awareness. Thus, digital twin technology not only
provides a simulation environment but also acts as a context
provide for intrusion detection.

1558-0016 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
2

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Fig. 1. CAN packet structure.

The increasing sophistication of cyberattacks further underlines the urgency of this approach. For example, a German
security expert demonstrated a Tesla vulnerability in 2022
that allowed remote exploitation of 25 vehicles across 13
countries by leveraging EVN flaws to gain IVN control [14].
Traditional IDS methods-whether anomaly-based, rule-based,
or signature-based [15]-struggle to adapt to such multi-domain,
evolving threats. Although machine learning methods have
been applied to CAN traffic and V2X data, they are limited by
heterogeneous encoding formats and protocol diversity [16].
More importantly, most IDS operate in isolation, ignoring
real-time IVN–EVN interactions, and therefore lack contextawareness in detecting coordinated attacks. In this work,
“context” refers to the mutual dependencies among traffic
features, such as temporal sequences, cross-protocol interactions, and statistical co-variations, within a shared operational
window. Inspired by BERT-style contextual representation
learning, each feature (e.g., CAN ID, packet size, or V2X field)
is treated as a token whose semantic meaning is dynamically
shaped by its surrounding features and the real-time vehicle
state provided by the digital twin.
Recent advances in pre-trained Transformer models [17]
inspire new opportunities. Their sequence modeling capabilities align well with vehicular data streams, where CAN
frames and V2X payloads exhibit complex temporal dependencies. To balance effectiveness and efficiency, we adopt
Distilled Bidirectional Encoder Representations from Transformers (DistilBERT) with only three Transformer layers, and
enhance it with a Temporal Self-Attention (TSA) module. This
design captures temporal dependencies in traffic data while
meeting the stringent latency and resource constraints of invehicle devices.
Based on these motivations, we propose CATwin-IDS: a
Context-Aware Intrusion Detection System for both IVN and
EVN via digital twin. CATwin-IDS integrates a lightweight
DistilBERT model with temporal attention and leverages
digital twin technology for real-time context fusion, attack
simulation, and adaptive detection. This synergy enables
efficient modeling of cross-network contextual dependencies
while ensuring practical deployability in edge environments.
The main contributions of this paper are summarized as
follows:
• We propose CATwin-IDS, a context-aware intrusion
detection system empowered by digital twin technology.
It fuses IVN and EVN features in real time, enabling
cross-domain context modeling and adaptive detection of
coordinated attacks.
• We design a hybrid feature engineering approach integrating Conditional Mutual Information (CMI) and
Borderline Synthetic Minority Over-sampling Technique

(Borderline-SMOTE), improving feature relevance while
addressing severe class imbalance in heterogeneous
vehicular traffic.
• We develop a lightweight DistilBERT model with TSA,
which captures both semantic-rich EVN payloads and
time-critical IVN dependencies, thus modeling crossnetwork contextual correlations under in-vehicle resource
constraints.
• We construct a hierarchical digital twin architecture
(physical, digital twin, application) that supports bidirectional synchronization, provides a simulation environment
for cross-network attack scenarios. This integration
enhances the IDS with real-time adaptability and contextawareness.
The remainder of this paper is organized as follows.
Section II discusses the related work. Section III presents the
proposed model and its key technologies. Section IV describes
the experimental results. Section V concludes the paper.
II. R ELATED W ORK
To comprehensively address the challenges of intrusion
detection in IoV systems, this section reviews existing research
from three perspectives: detection methods for IVN intrusions,
strategies to tackle EVN intrusion risks, and hybrid frameworks integrating IVN and EVN detection. These existing
studies on single-network and hybrid network approaches are
summarized in Table I.
A. In-Vehicle Network Intrusion Detection
In the development of connected and autonomous vehicles,
securing IVNs through robust intrusion detection has become
increasingly critical. Within the complex ecosystem of IVNs,
intrusion detection technologies have overwhelmingly centered
on protecting the CAN bus-primarily because it serves as the
backbone for data communication between in-vehicle ECUs.
As the primary medium for transmitting in-vehicle data, CAN
messages and packets are relayed through this bus architecture.
Specifically, a CAN data packet, as depicted in Fig. 1, consists
of seven key fields: frame start, arbitration field, control field,
data field, Cyclic Redundancy Check (CRC) Field, Acknowledgment (ACK) Field, and frame end [29]. Among these, the
Data Field is the most vulnerable to exploitation by attackers,
as it contains the actual transmitted data that determines the
operations of the ECUs, such as throttle control, brake signals,
and steering angle adjustments. Attackers can infiltrate or
control the vehicle by injecting malicious messages into the
Data Field of the CAN data packet [30].
In recent years, many researchers have focused on IDS
based on the CAN bus. In [19], a binary classification detection system based on a hybrid Long Short-Term Memory
(LSTM) and Convolutional Neural Networks (CNN) model
was proposed. Reference [21] and others used CNN deep
learning models to experiment with real vehicle data, focusing
on specific types of attacks. The authors of [31] applied
a multi-stage method combining Artificial Neural Network
(ANN) and LSTM, achieving an F1 score of 0.95 and a
detection rate of 99.99% on benchmark datasets published
by [32] and others. In [33], a scheme was proposed to

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIU et al.: CATwin-IDS: CONTEXT-AWARE INTRUSION DETECTION SYSTEM

3

TABLE I
C OMPARISON OF R ELATED W ORK

detect intrusions by establishing voltage fingerprints for each
ECU’s ID, with experiments conducted on three real vehicles.
The study [34] introduced a cluster-based open set recognition method for CAN bus intrusion detection, which can
detect known categories and identify unknown attacks. It
achieved accuracies of 99.37%, 99.36%, 98.93%, and 98.09%
on the Car-Hacking dataset [35] for Dos, Fuzzy, Gear, and
Rpm attack types, respectively. Although the abovementioned
machine-learning-based IDS are efficient and effective, they
often lack interpretability. The work [36] addresses this by
integrating a threshold-based IDS with a machine learning
classifier for attack type categorization, providing explanations

for the IDS. Li et al. [27] proposed a cloud-collaborative
intrusion detection and prevention system that integrates the
Car-Hacking dataset, survival analysis dataset, and data collected from real or simulated vehicular environments. By
utilizing the contextual modeling capabilities of the Bidirectional Encoder Representations from Transformers (BERT)
model, the system classifies in-vehicle traffic. Additionally,
they introduced the Encode 2 ID algorithm to encode malicious traffic, generating a unique ID for each traffic instance,
thereby saving storage space.
In summary, research on IVN intrusion detection has not
only promoted an in-depth understanding of CAN bus attack

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
4

patterns but also offered important references for protocol
feature mining and anomaly modeling in IVN. However, existing methods, while effective for single-bus protocol defense,
insufficiently address the dynamic interplay between IVN and
external networks-lacking multi-protocol compatibility, crossscenario generalization, and interpretability, which limits their
applicability to the coupled nature of IoV.
B. External Network Intrusion Detection
Network intrusion detection in the EVN within the IoV has
also attracted widespread attention from researchers. In [12],
an IoT-based attack behavior recognition system was proposed,
which integrates spatiotemporal feature fusion. This system
uses a simplified CNN model to learn the spatial features
of attacks and a Bidirectional Long Short-Term Memory
(BiLSTM) model to capture the temporal features of attacks.
Experiments were conducted on the UNSW-NB15 [37] and
CICIDS2017 datasets [38]. To address the issue of detecting
low-probability attacks, [22] proposed an intrusion detection
system based on Transformer models. In [25], machine learning techniques such as One-Class Support Vector Machine
(OCSVM) and isolation Forest (iForest) were employed to
detect both known and zero-day attacks. [39] introduced an
IDS based on Deep Transfer Learning (DTL) that employs a
three-tier architecture integrating CNN, Genetic Algorithms
(GA), and bootstrap aggregation techniques. By transforming cybersecurity datasets into image data and optimizing
model hyperparameters using genetic algorithms, this system
achieved a 100% accuracy rate on the Edge-IIoTset dataset
[40], which includes 14 types of attacks.
Research on EVN intrusion detection has made progress in
spatio-temporal feature fusion, transfer learning, Transformerbased models, and the application of large language models
like BERT in text-based data processing. Nevertheless, existing
methods are mostly designed for independent EVN scenarios
with high system model complexity, and their adaptability in
resource-constrained in-vehicle edge environments still needs
to be strengthened. This deficiency further heightens the urgent
demand for the realization of collaborative defense between
in-vehicle and external networks to address the practical
challenges in EVN security.
C. Hybrid Intrusion Detection
Recent studies have explored hybrid IDS for integrated
IVN-EVN security, aiming to address cross-network attack
scenarios. In [18], an ensemble method combining Decision
Trees (DT), Random Forest (RF), Extremely Randomized
Trees (ET), and XGBoost was proposed, achieving accuracies
of 99.99% and 99.88% on the Car-Hacking (representing IVN)
and CICIDS2017 (representing EVN) datasets, respectively.
In [11], a CNN was used to convert network numerical data
into images, making it easier to identify attack types, and the
method was validated on the collected dataset. In [1], the relationship between network traffic was considered, and data was
converted into text based on a BERT model. The system was
validated on the CICIDS and BoT-IoT [41] datasets. In [24], a
BiLSTM-based intrusion detection system was employed for
binary classification, and Federated Learning was utilized to

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

protect data privacy. Performance validation was conducted
on the UNSW-NB15, CAN-Intrusion [32], and CICIDS2017
datasets. Hybrid frameworks have explored the collaborative
defense ideas between IVN and EVN, showing potential in
improving the coverage of cross-network attack detection.
However, existing methods are either limited by complex
architectures resulting in insufficient real-time performance or
have limitations in the depth of heterogeneous data fusion and
the refinement of contextual modeling, making it difficult to
fully capture the dynamic coupling relationship between invehicle and external networks.
Existing intrusion detection research has explored crossnetwork hybrid architectures for the IoV, but these frameworks exhibit several limitations. Hybrid architectures achieve
cross-network detection through approaches like multi-model
integration but typically retain bulky structures, making them
unsuitable for resource-constrained in-vehicle edge environments. Most importantly, they fail to fully capture the
time-critical CAN frame dependencies between the IVN and
EVN, with shortcomings in multi-classification capability,
detection performance, and interpretability further restricting
their practicality.
Recent studies have begun to explore efficient adaptations
of pre-trained Transformer models to address these challenges.
For instance, Li et al. [42] proposed a knowledge distillation
framework that transfers semantic knowledge from BERT
to a lightweight CNN-BiLSTM model, achieving over 98%
accuracy while significantly reducing computational overhead.
Bimmo et al. [43] introduced Fed-CALiBER, a federated
learning system integrating a lightweight BERT variant for
real-time (<4 ms/sample) CAN bus intrusion detection on edge
devices, demonstrating the feasibility of privacy-preserving
LLM deployment in distributed vehicular settings. Meanwhile,
Sharma et al. [44] leveraged pre-trained Transformer models
for context-aware authentication in V2V/V2I communications, highlighting the potential of pre-trained Transformer
models in building adaptive, intelligent security mechanisms
beyond mere detection. These advances collectively signal a
shift toward lightweight, context-sensitive, and privacy-aware
pre-trained Transformer model applications in automotive
cybersecurity-trends that directly motivate our architectural
choices.
Notably, EVN-focused research [1], which leverages
BERT’s sequence modeling capabilities, has inspired our work
by demonstrating the potential of pre-trained Transformer
models to capture contextual connections in vehicular network data. Building upon this insight, we adopt DistilBERT-a
6-layer lightweight variant of BERT obtained via knowledge distillation-as the foundation of our framework. To
further adapt it to the stringent real-time requirements of IoV,
we streamline the encoder depth from six to three layers
and refine the attention mechanism into TSA. This twofold
optimization not only alleviates the computational burden
compared to both BERT and standard DistilBERT, but also
enhances the model’s ability to capture temporal dynamics
in cross-network traffic. Combined with digital twin-driven
dynamic adaptation, the framework effectively addresses the
limitations of existing single-network and hybrid-network IDS
approaches.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIU et al.: CATwin-IDS: CONTEXT-AWARE INTRUSION DETECTION SYSTEM

5

Fig. 2. Application scenario diagram of digital twin intrusion detection system for IoV.

III. S YSTEM M ODEL
In this section, we introduce the proposed CATwin-IDS
system model in detail, as illustrated in Fig. 2. First, we outline
the overall IoV digital twin architecture, which is organized
into three layers-physical, digital twin, and application-to
enable bidirectional synchronization and cross-domain feature
fusion. Next, we describe the training framework of the
proposed IDS, consisting of data preprocessing, feature engineering, and the Lightweight DistilBERT Classifier, supported
by digital twin simulation. The following subsections elaborate
on the preprocessing strategies for heterogeneous vehicular
traffic, the hybrid feature engineering methods that enhance
discriminative power, and the lightweight DistilBERT model
specifically optimized with TSA for resource-constrained environments. Together, these components constitute a cohesive
framework that enables efficient and accurate intrusion detection across both IVN and EVN.
A. IoV Digital Twin Architecture Overview
The three-layer architecture of CATwin-IDS is designed
to address the dynamic coupling between IVN and EVN,
and to bridge the gap between real-world vehicular data
acquisition and virtualized intrusion detection. This architecture enables bidirectional data synchronization, cross-domain
feature fusion, and secure simulation of attack scenarioskey capabilities for overcoming the limitations of traditional
isolated-network IDS. Each layer undertakes distinct but interdependent roles, forming a closed-loop system that supports
real-time, adaptive intrusion detection for IoV.
1) Physical Layer: The core communication protocol of
IVN is the CAN bus protocol, which allows various Electronic
Control Units (ECUs) in the vehicle to receive signals from
sensors and make control decisions based on these signals.
These ECUs communicate with each other and exchange data
with the vehicle gateway via the CAN bus protocol. The
vehicle gateway serves as a central hub, not only transmitting

data within the vehicle’s internal network but also enhancing network security through an integrated IDS, effectively
defending against potential network attack threats.
Vehicle interfaces such as USB, OBD, and Unified Diagnostic Services (UDS) provide means for interaction with
the external environment but may also introduce security
risks related to in-vehicle intrusion. Therefore, these interfaces
require appropriate security measures to protect them from
potential attacks by external intruders. The Telematics-Box
(T-Box), as the vehicle’s remote communication unit, provides
functions like cellular networks and short-range communication (such as Near Field Communication (NFC), Bluetooth,
and Wi-Fi). While these communication capabilities enhance
the vehicle’s connectivity, they also increase the risk of
external vehicle intrusion.
In addition, the physical layer includes all physical devices
and sensors, such as GPS positioning systems, high-definition
cameras, and LiDAR. These devices are responsible for collecting real-time data on the vehicle, covering key information
such as the vehicle’s operational status, environmental conditions, and driving behavior. The primary task of the physical
layer is to ensure the accuracy and integrity of this data,
providing reliable input for the digital twin layer. To achieve
this, the physical layer not only needs to efficiently collect
and transmit data but also must implement multiple security
measures to prevent data from being tampered with or lost,
thereby providing a solid foundation for intelligent decisionmaking and control.
2) Digital Twin Layer: The digital twin layer is responsible
for constructing and maintaining a high-fidelity virtual replica
of the IoV environment, faithfully reflecting both the IVN and
the EVN. Its architecture follows the modular design shown in
Fig. 2, consisting of a data processing framework and a system
management framework, with the two frameworks interacting
dynamically to achieve precise mapping and intelligent management of IVN-EVN interactions.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
6

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

The data processing framework integrates continuous realtime streams from physical sensors, ECUs, and external
communication modules (e.g., V2X, Wi-Fi). This data is
first normalized and stored, ensuring integrity and temporal
alignment across domains. The virtual twin’s state stwin
is
t
updated through a bidirectional synchronization process:
phys

stwin
= (1 − α) stwin
t
t−1 + α st

,

(1)

where α ∈ [0, 1] controls the update rate between physical
phys
measurements st
and the previous virtual state stwin
t−1 . This
mechanism enables the twin to remain consistent with the
real system while preserving short-term predictive dynamics,
ensuring timely tracking of sudden changes in IVN (e.g.,
abnormal CAN bus frequency) and EVN (e.g., V2X signal
spoofing) for rapid threat identification.
The system management framework incorporates:
• Security Management: Interfaces with the IDS to detect
and mitigate threats, validating countermeasures in the
virtual space before deployment.
• Model Management: Continuously refines virtual model
parameters by comparing simulated and observed outputs.
• Topology Management: Dynamically maps IVN-EVN
interconnections, tracking gateway, T-Box, and access
point configurations.
The data processing framework provides real-time updated
state data as input for the system management framework,
while the topology management results from the system
management framework guide the priority setting of data
streams in the data processing framework, forming a closedloop optimization mechanism.
Cross-domain feature fusion module aligns heterogeneous
IVN and EVN features into a unified embedding space:
z ∈ Rd = fIVN (xIVN ) k fEVN (xEVN ),

(2)

where k denotes vector concatenation, and fIVN , fEVN are
domain-specific encoders mapping IVN and EVN features
into the joint embedding space Rd . This representation feeds
into the Borderline-SMOTE in Sec. III-B, ensuring synthetic
samples preserve real-world cross-network dependencies, and
directly serves as the input for the Lightweight DistilBERT
classifier to support its modeling of spatiotemporal correlations
across heterogeneous networks.
During inference, the fused features are continuously
streamed into the DistilBERT classifier, enabling real-time
and context-aware intrusion detection. In this way, the digital
twin not only maintains a synchronized virtual replica of the
physical system but also functions as a live feature provider
for the detection model. Beyond online detection, the twin
further offers a secure experimentation environment in which
simulated attack scenarios (e.g., CAN flooding and V2X
spoofing) can be executed to support adaptive classifier tuning
without risking the physical vehicle.
3) Application Layer: The application layer serves as
the interface for end-users, translating the analysis results
and detection decisions from the digital twin layer into
actionable steps and feedback. Application scenarios include
autonomous vehicle security, intelligent transportation systems
(ITS), remote software updates and OTA services, and more.

Algorithm 1 Proposed Intrusion Detection Algorithm With
Lightweight DistilBERT Classifier
Input: Network traffic data D (structured data), digital twin
environment T ;
Output: Predicted labels y;
Step 1: Data Preprocessing
1 Load dataset D;
2 Perform data cleaning (e.g., handle missing values and
outliers);
3 Encode categorical labels into numeric values;
4 Standardize numeric features to ensure consistent scales;
Step 2: Feature Engineering
5 Select top-k features using CMI;
6 Split D into training (80%) and testing (20%) subsets;
7 Apply Borderline-SMOTE to balance class distribution in
training data;
8 Transform structured features into textual representations;
Step 3: Digital Twin Simulation
9 Initialize digital twin environment T for real-time traffic
simulation;
Step 4: Lightweight DistilBERT Feature Extraction
←
10 Tokenize
textual
input:
Input tokens
Tokenizer(Textual Representation);
11 Add [CLS] and [SEP] tokens;
12 Pass
tokenized inputs through the Lightweight
DistilBERT Classifier: All Layers Output
←
LightweightDistilBERT(Input tokens);
13 Extract
contextual
embeddings
from
the
final (third) encoder layer: Embeddings
←
All Layers Output.Encoder3;
Step 5: Classification
14 Feed embeddings into the Lightweight DistilBERT
Classifier’s output layer (FFNN + softmax);
15 Compute class probabilities and assign predicted labels:
Predicted Labels ← arg max(Probabilities);
Step 6: Output
Return the final predicted labels y as intrusion detection
outcomes.

B. Context-Aware Intrusion Detection Framework
CATwin-IDS employs a DistilBERT encoder to learn
contextualized feature representations. Through bidirectional
self-attention, every feature embedding incorporates information from all other features within the same detection
window, capturing both temporal and statistical correlations.
The digital-twin layer enriches this process by injecting
environment-specific variables, enabling conditional context
modeling under real-time vehicle states.
The training framework integrated into the digital twin layer
primarily consists of three stages: data preprocessing, feature
engineering, and the Lightweight DistilBERT Classifier, as
shown in Fig. 3. The pseudocode for the intrusion detection
process, including data preprocessing, feature engineering,
digital twin simulation, lightweight DistilBERT feature extraction, and final classification decisions, is described in Alg. 1.
1) Data Pre-Processing: In real-world application scenarios, network traffic data typically exhibits class imbalance [45],

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIU et al.: CATwin-IDS: CONTEXT-AWARE INTRUSION DETECTION SYSTEM

where the volume of normal traffic significantly exceeds that
of anomalous traffic. To enhance the model’s ability to detect
anomalous traffic and improve its generalization performance
in diverse data environments, it is necessary to preprocess
the data, transforming raw network traffic data into a format
suitable for spatiotemporal feature analysis, thus providing
an appropriate data foundation for in-depth data mining and
model training.
To address the class imbalance issue, we employed random
sampling techniques to balance the sample sizes of different
attack types and normal traffic within the dataset. This process
ensures the representativeness of each sample type during
model training, thereby improving the fairness of the training
process and the accuracy of evaluation.
During the data processing, to handle the occurrence of
infinite or NaN values, this paper adopted a mean imputation
strategy. By replacing infinite or NaN values with the corresponding feature’s average value, the integrity and consistency
of the data were effectively maintained, providing a reliable
foundation for subsequent data analysis. Additionally, to facilitate model processing, LabelEncoder technology was used to
encode the labels of the dataset [46]. This technique converts
categorical text labels into numerical values, which not only
simplifies the model’s input requirements but also enhances
the efficiency of data processing by the model.
2) Feature Engineering: Building upon data preprocessing, the goal of feature engineering is to further refine and
optimize the dataset to improve model training efficiency
and classification performance. To address the challenges of
modeling cross-domain dependencies between IVN and EVN,
traditional single-network feature selection methods can only
analyze IVN’s CAN bus features (e.g., message ID frequency)
or EVN’s V2X protocol characteristics, while neglecting the
attack chains formed through gateway data synchronization
(e.g., spoofed EVN traffic signals infiltrating IVN to disrupt
ECU decision-making). To overcome this limitation, this paper
integrates multiple feature selection methods-including Mutual
Information (MI) for nonlinear correlation analysis, Chi-square
test for categorical variable screening, and Principal Component Analysis (PCA) for linear dimensionality reduction-to
perform cross-domain feature selection. This approach preserves critical original features while eliminating redundant
dimensions, ultimately constructing a low-dimensional yet
highly discriminative feature subset through cross-network
dependency mining to achieve effective anomalous traffic
detection. Below are several commonly used feature selection
methods and their mathematical expressions:
• MI: MI is a method used to assess the amount of shared
information between two random variables. It can capture
both linear and nonlinear relationships between variables.
The expression for calculating MI is as follows:


XX
P(x, y)
,
(3)
MI(X, Y) =
P(x, y) log
P(x)P(y)
x∈X y∈Y
where X represents cross-network interaction features
(e.g., combined IVN-EVN attributes such as CAN ID frequency and V2X packet rate), Y denotes attack categories
(e.g., benign, DoS, spoofing), p(x, y) is the joint probability distribution, and p(x) and p(y) are the marginal

7

probability distributions. By computing the MI between
each feature and the target variable, followed by MI value
ranking, we prioritize retaining features that simultaneously influence both IVN and EVN.
• CMI: To further capture the latent cross-domain dependency between IVN and EVN under specific operational
contexts (e.g., gateway load state, time window), we
extend MI to its conditional form:
XXX
I(Bk ; F | Z) =
p(bk , f , z)
z

bk

f

p(bk , f | z)
,
× log
p(bk | z)p( f | z)

(4)

where Bk denotes the k-th CAN payload byte, F denotes
a selected EVN feature (e.g., Flow_Byts/s), and Z
represents contextual variables such as gateway state or
time interval. We further adopt the normalized form:
NCMI(Bk ; F | Z) = √

I(Bk ; F | Z)
,
H(Bk | Z) H(F | Z)

(5)

where H(· | Z) denotes conditional entropy. This metric
allows fair comparison between heterogeneous feature
pairs and prioritizes those most indicative of crossnetwork attack chains.
• Chi-squared Test: The chi-squared test is a statistical
method used to test the independence between categorical variables. In feature selection, it is used to assess
the association between a single feature and the target
variable, expressed as:
X (O − E)2
,
(6)
χ2 =
E
where O represents the observed frequency, and E
is the expected frequency under the assumption of
independence.
• PCA: PCA transforms a set of possibly correlated
variables into a set of linearly uncorrelated principal
components via orthogonal transformation:
PCA(X) = XW,

(7)

where X is the original dataset matrix, and W contains
eigenvectors of the covariance matrix.
In this paper, to quantify the interdependence between
features and the target variable, we adopt MI and extend
it to CMI for cross-domain feature selection, ensuring that
selected features capture correlated anomalies in both IVN and
EVN. By quantifying these correlations, the system identifies
attack propagation patterns across networks (e.g., DoS attacks
manifesting as EVN traffic surges alongside excessive CAN
bus load in IVN). Following this feature selection, the dataset
is partitioned into training (80%) and testing (20%) sets.
To further address the issue of class imbalance, we adopt
Borderline-SMOTE, which differs from traditional Synthetic
Minority Over-Sampling Technique (SMOTE) by focusing
on minority samples located near the decision boundary.
Instead of generating synthetic samples uniformly across
the feature space, Borderline-SMOTE interpolates new data
points in these critical regions where misclassification is most
likely to occur. This targeted sampling strategy enhances the

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
8

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

model’s ability to distinguish between normal and attack
traffic, reduces the risk of introducing noisy or redundant samples, and improves classification robustness under imbalanced
conditions.
Finally, numeric features are converted into text format
for input into the Lightweight DistilBERT Classifier. The
text transformation process directly maps structured numeric
features to sequential text strings while preserving the original
feature order. This design enables the Lightweight DistilBERT classifier to leverage its pre-trained sequence modeling
capabilities without requiring additional input layers for heterogeneous numeric features, reducing model complexity. For
illustration, a sample from the CICIDS2018 (EVN) dataset,
consisting of protocol and traffic-related numeric features, is
converted into a text sequence such as “6 64 9306.82 120 0
. . .”. Similarly, a sample from the Car-Hacking (IVN) dataset,
including the CAN ID and eight payload fields, is transformed
into a sequence like “1201 41 39 39 35 0 0 0 154”. Both IVN
and EVN samples follow the same numeric-to-text conversion
rule, ensuring unified processing of cross-domain traffic while
preserving intrinsic temporal ordering, which further facilitates
the TSA mechanism in capturing dynamic traffic patterns.
3) The Lightweight DistilBERT Classifier: The lightweight
DistilBERT classifier is a refined variant of the original DistilBERT model, specifically adapted for intrusion detection in
the IoV. While standard DistilBERT employs knowledge distillation to compress BERT into a six-layer architecture [47],
our variant further reduces the encoder depth to three layers
to meet the stringent latency and memory requirements of
in-vehicle edge devices. This reduction lowers computational
overhead and improves deployability in resource-constrained
environments, without sacrificing essential contextual modeling capacity.
Each encoder layer consists of a Temporal Self-Attention
(TSA) mechanism, a position-wise feed-forward network
(FFN), and residual connections with layer normalization. The
TSA mechanism introduces a temporal bias into the attention
weights, explicitly capturing the order and intervals of network
events:


QK T
Attention(Q, K, V, ∆t) = softmax √ − β|∆t| V,
(8)
dk
where Q, K, and V denote the query, key, and value, dk is
the key dimension, ∆t is the timestamp difference between
tokens, and β > 0 controls the temporal decay. This allows the
model to prioritize temporally proximate features, improving
detection of time-sensitive anomalies in network traffic.
The FFN performs a nonlinear transformation at each
position:
FFN(x) = max(0, xW1 + b1 )W2 + b2 ,

(9)

where x is the input, W1 and b1 are parameters of the first
fully connected layer with ReLU activation, and W2 , b2 are
parameters of the second fully connected layer. Residual
connections and layer normalization are applied after both
TSA and FFN to ensure training stability:
Y = LayerNorm(x + Sublayer(x)),
x−µ
LayerNorm(x) = γ
+ β,
σ

(10)
(11)

where µ and σ are the mean and standard deviation, and γ
and β are learnable parameters.
Distinct from the original NLP-oriented DistilBERT that
relies on masked token prediction during pretraining, our
classifier directly consumes structured vehicular traffic features
converted into sequential text form. By treating each numeric
feature as an individual token, the Lightweight DistilBERT
Classifier effectively transforms heterogeneous vehicular data
into a unified representation space. The incorporation of
temporal attention further enhances the ability to correlate
abnormal EVN communication patterns with time-critical IVN
CAN bus signals. As a result, the model achieves robust intrusion detection performance across heterogeneous domains,
offering a practical and scalable solution for real-time IoV
security.
In summary, the lightweight DistilBERT classifier, combined with TSA, FFN, and residual connections, forms the
core of our intrusion detection framework. Integrated with
the digital twin layer and preceded by data preprocessing
and feature engineering, this architecture enables efficient,
context-aware detection of cross-network attacks while meeting the real-time and resource-constrained requirements of IoV
environments.
IV. E VALUATION R ESULTS
This section provides a detailed overview of the experimental design and results analysis, aiming to validate the
effectiveness and performance of the proposed CATwin-IDS
model in both EVN and IVN. A VMware ESXi virtualization
server runs the digital twin of the IoV network environment,
replicating the exact topology and functions of the physical
IVN and EVN; all traffic data from the physical networks
is mirrored to this virtualized server to ensure consistency.
First, it introduces the characteristics and sources of the
datasets used for training and evaluation. Next, it describes
the hardware and software environment, as well as the data
preprocessing and sampling methods employed in the experiments. Finally, the chapter comprehensively evaluates the
superiority of the CATwin-IDS model across multiple performance metrics through comparisons with various baseline
models, conducts an in-depth analysis of its performance using
confusion matrices and performance comparison charts, and
validates its cross-network intrusion detection efficacy.
A. Experimental Design
This paper involves datasets primarily categorized into two
main types: EVN and IVN, aimed at providing the necessary network traffic data for training and evaluating IDS
models to determine whether network behaviors are benign.
The EVN dataset is sourced from the Canadian Institute
for Cybersecurity (CIC), including CICIDS2018 [38] and
CICIoT2023 [48], covering various types of network attacks.
The CICIoT2023 dataset includes 33 types of attacks, categorized into seven classes: DDoS, DoS, Recon, Web-based,
Brute-force, Spoofing, and Mirai attacks, and it contains 39
features. The CICIDS2018 dataset comprises 78 features and
multiple types of attacks, including Brute-force, Heartbleed,
Botnet, DoS, DDoS, Web application, and Infiltration attacks

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIU et al.: CATwin-IDS: CONTEXT-AWARE INTRUSION DETECTION SYSTEM

9

Fig. 4. Selected feature importance from CICIDS2018.
TABLE II
C AR -H ACKING DATASET

(TN), False Positives (FP), and False Negatives (FN), as
provided below.
Fig. 3. The overall framework of CATwin-IDS.

of the network from inside. The IVN dataset is specifically
focused on collecting traffic data related to the CAN bus.
This dataset meticulously records feature information, including timestamps, CAN IDs, Data Length Codes (DLC), and
the 8-byte data fields (DATA[0]-DATA[7]) in CAN packets,
providing essential contextual information for analyzing communications on the CAN bus. The IVN datasets used in this
paper for evaluating IDS performance in vehicular network
environments include Car-Hacking [35] and CICIoV2024 [49].
By integrating both EVN and IVN datasets, this paper can
comprehensively assess the performance of IDS across different network environments, ensuring that the proposed solutions
are effective against a diverse range of network attacks and
enhancing the overall security of vehicular networks. By
integrating both EVN and IVN datasets, this paper can comprehensively assess the performance of IDS across different
network environments, ensuring that the proposed solutions
are effective against a diverse range of network attacks and
enhancing the overall security of vehicular networks.
The experimental setup adopts NVIDIA GeForce RTX 3060
with 12 GB of GPU memory. The experiments were conducted
using Python version 3.8.0. Model construction was primarily
carried out using PyTorch, version 1.9.0.
The performance evaluation metrics utilized in this paper
include accuracy, precision, recall, and F1, derived from four
fundamental parameters: True Positives (TP), True Negatives

TP + TN
,
TP + TN + FP + FN
TP
,
Precision =
TP + FP
TP
Recall =
,
TP + FN
2 × Precision × Recall
F1 =
.
Precision + Recall

Accuracy =

(12)
(13)
(14)
(15)

B. Data Preprocessing
In real-life scenarios, normal data typically constitutes a
large proportion, leading to highly imbalanced datasets. This
imbalance often undermines the generalization and stability
of system models, as they may become biased towards the
majority class. To enhance the robustness of the experimental
results, we conducted uniform sampling for each type of attack
and normal samples, ensuring that the data volume for each
type is the same. Due to the large number of attack class labels,
we referred to the attack classification standards of the CIC
to group class labels with similar characteristics into unified
attack types. This classification approach not only aligns with
CIC but also enables more effective analysis and evaluation.
This paper considers each type of attack and uniformly collects data for each type as the experimental evaluation object,
comparing two datasets each for IVN and EVN. The details of
the original datasets, attack types, training sets, and test sets
for these four datasets are respectively presented in Table II,
Table III, Table IV, and Table V. In the data preprocessing
stage, CMI was used to perform feature selection on four

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
10

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

TABLE III
CICI OV2024 DATASET

TABLE VI
CICIDS2018 DATASET E VALUATION M ETRICS

TABLE IV
CICIDS2018 DATASET

TABLE VII
CICI OT2023 DATASET E VALUATION M ETRICS

TABLE V
CICI OT2023 DATASET

the selected features from the CICIoT2023 dataset is illustrated
in the Fig. 4.
C. Model Comparison and Performance Analysis

datasets. Taking the CICIDS2018 dataset as an example, 18
out of 78 features were chosen as input features. This approach
effectively maintains detection capabilities while reducing
computational complexity and redundancy. The importance of

To comprehensively evaluate CATwin-IDS across different methodological paradigms, we select 14 baseline models
covering (1) traditional machine learning methods (KNN,
DT, ET, SVM, LightGBM, CatBoost, XGBoost) representing tree-based and distance-based classifiers; (2) sequential
deep networks (LSTM, BiLSTM, RNN, CNN) focusing on
temporal and local feature learning; and (3) Transformerbased models (BERT, Distilling BERT for Natural Language
Understanding (TinyBERT), Transformer) for contextual feature understanding and efficiency comparison. The results of
these comparisons are shown in Table VI and Table VII. The
CATwin-IDS model achieved an F1 score of 100% across all
types of attacks on the Car-Hacking and CICIoV2024 datasets.
In the more complex EVN datasets, namely CICIDS2018
and CICIoT2023, the CATwin-IDS model adopted in this
paper demonstrated outstanding performance, leading other
models with accuracy scores of 0.9097 and 0.8396, and F1
scores of 0.9094 and 0.8382, respectively. The comparison
includes a standard Transformer model, which achieved

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIU et al.: CATwin-IDS: CONTEXT-AWARE INTRUSION DETECTION SYSTEM

11

TABLE VIII
A BLATION E XPERIMENT R ESULTS ON CICIDS2018 DATASET

accuracy of 0.8856 and F1 of 0.8845 on CICIDS2018, and
accuracy of 0.8277 and F1 of 0.8250 on CICIoT2023. When
compared with traditional machine learning models, CATwinIDS showed higher performance on both the CICIDS2018
and CICIoT2023 datasets. Although CatBoost and XGBoost
performed well on the CICIDS2018 dataset, and LightGBM,
CatBoost, and XGBoost also showed good performance on
the CICIoT2023 dataset, their accuracy and F1 scores were
slightly lower than those of DistilBERT. This indicates potential limitations of these models in handling complex data.
Furthermore, DistilBERT maintained performance similar to
BERT while reducing model complexity and computational
resource requirements, thereby enhancing efficiency in practical applications. Compared to TinyBERT, another lightweight
BERT model, DistilBERT demonstrated advantages in both
resource consumption and performance metrics. These results
indicate that DistilBERT not only provides high accuracy in
classification tasks but also maintains high recall and precision.
An ablation experiment was conducted to investigate the
impact of encoder depth on long-range temporal dependency
capture and model efficiency. As shown in Table VIII, the
3-layer configuration, integrated with the TSA mechanism,
achieves an optimal balance between long-range dependency
modeling capability and computational efficiency. Specifically,
this design reduces relative computational cost by 49.2%
and improves inference efficiency by 46.4% compared to
deeper architectures, while attaining an F1-score of 0.9104
that outperforms the 2-layer TSA-integrated variant by 0.25%.
In contrast, the 2-layer configuration exhibits insufficient
capacity to capture complex long-range dependencies, and
the 4-layer configuration delivers only marginal performance
changes while incurring a 41.4% increase in convergence
time. This validates our design choice of the 3-layer structure for lightweight and real-time network intrusion detection
scenarios.
D. Classification Performance and Confusion Matrix
Analysis
The proposed CATwin-IDS framework was systematically
evaluated against LSTM, BiLSTM, RNN, CNN, TinyBERT
and Transformer models across multiple datasets. For CATwinIDS, the hyperparameters were configured as follows: a base
layer dropout rate of 0.25, a sequence classification layer
dropout rate of 0.3, the AdamW optimizer (learning rate of
8 × 10−6 , weight decay coefficient of 0.1, bias correction
disabled), a batch size of 32, and a fixed training duration of
50 epochs. To ensure fair comparison, identical preprocessing
pipelines and training epochs were applied to all models.
TinyBERT was trained with the same hyperparameter

Fig. 5. Comparison of EVN performance indicators on CICIDS2018 dataset.

configuration as CATwin-IDS to validate transferability under
equivalent resource constraints, while LSTM, BiLSTM, RNN,
and CNN followed widely adopted baseline configurations in
the IDS literature:
• LSTM/BiLSTM/RNN: 50 hidden units →
64dimensional fully connected layer (ReLU activation) →
Dropout(0.2) → classification layer.
• CNN: 64 convolutional kernels (kernel size 3) → max
pooling → flattening → 64-dimensional fully connected
layer (ReLU activation) → Dropout(0.2) → classification
layer.
On CICIDS2018 (Fig. 5(a), 5(b)), CATwin-IDS demonstrates
faster convergence (loss stabilizing below 0.20 after 20 epochs)
and higher test accuracy than LSTM, BiLSTM, CNN, and
RNN, the latter showing substantial instability with fluctuating losses. On CICIoT2023 (Fig. 6(a), 6(b)), CATwin-IDS
achieves accuracy gains of 1.1% over TinyBERT while
converging earlier (15 epochs). Under identical hardware
(NVIDIA GeForce RTX 3060 GPU), CATwin-IDS requires
252 seconds per validation epoch, compared to 871 seconds
for BERT, corresponding to a 71.1% reduction in runtime.
This relative efficiency gain demonstrates the effectiveness
of our streamlined architecture (e.g., 3-layer Transformer,
TSA) in balancing accuracy and computational cost. On
Car-Hacking and CICIoV2024 (Figs. 7 and 8), CATwinIDS consistently achieves accuracy above 0.99 with loss
below 0.02, validating its robustness and generalizability
across heterogeneous vehicular domains for reliable crossnetwork intrusion detection. While in-vehicle edge devices
(with stricter resource constraints than GPUs) demand even
lower latency, this result highlights a critical step toward
real-time responsiveness, outperforming heavyweight models

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
12

Fig. 6. Comparison of EVN performance indicators on CICIoT2023 dataset.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Fig. 8. Comparison of IVN performance indicators on CICIoV2024 dataset.

Fig. 9 presents the confusion matrices of the classification performance of the proposed system across four distinct
datasets, which span both IVN and EVN scenarios, including
Car-Hacking, CICloV2024, CICIDS2018, and CICloT2023.
The results indicate that the system generally performs well in
identifying the BENIGN (normal traffic) category but shows
some confusion in differentiating certain types of attacks, such
as DoS and Bot. Particularly in the CICIDS2018 dataset, the
system exhibits high accuracy in recognizing DoS and Bot
attacks, while in the CICloT2023 dataset, the performance
is also commendable for Bot and DoS categories. However,
for complex attack patterns like Web attacks and Infiltration,
there is room for improvement in the system’s performance.
These findings suggest that although the proposed system
demonstrates robust classification capabilities across multiple
datasets, further refinement is needed to enhance its detection
accuracy and robustness, especially for specific types of cyber
attacks.

Fig. 7. Comparison of IVN performance indicators on car-hacking dataset.

like BERT in resource efficiency, which is foundational for
deployment on automotive-grade hardware. Future work will
further optimize via model quantization and hardware-aware
pruning to align with the stringent real-time requirements of
IoV.

E. Cross-Network Intrusion Detection
To verify the effectiveness of our system in detecting crossnetwork attacks, we focused on DoS attacks in our simulation
experiments due to their prevalence and severe impact on
cross-network security. By simulating DoS attacks on the IVN
datasets (Car-Hacking and CICIoV2024) and evaluating their
effects on the EVN datasets (CICIDS2018 and CICIoT2023),
we demonstrated the capability of CATwin-IDS in detecting
cross-network threats. As shown in Table IX, CATwin-IDS
achieved an F1 score of 0.9231 on the CICIDS2018 dataset
and 0.8774 on the CICIoT2023 dataset, significantly outperforming other comparative systems. These results confirm that

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIU et al.: CATwin-IDS: CONTEXT-AWARE INTRUSION DETECTION SYSTEM

13

Fig. 9. Confusion matrices of classification performance.

TABLE IX
F1 S CORE C OMPARISON B ETWEEN CAT WIN -IDS AND BASELINE M ODELS
FOR C ROSS -N ETWORK D O S I NTRUSION D ETECTION

our solution effectively mitigates DoS attacks exploiting the
IVN-EVN coupling, ensuring higher accuracy and reliability
in EVN intrusion detection.
Although our experiments primarily focused on DoS
attacks, the design of CATwin-IDS positions it well to address
other types of attacks. The system employs digital twin

technology to construct dynamic models of both the IVN and
EVN, enabling real-time monitoring and analysis of crossnetwork traffic anomalies. This digital twin-based detection
mechanism not only enhances the detection of DoS attacks
but also provides a robust foundation for identifying other
attack types, such as data tampering and malicious injection.
Specifically, digital twin technology can capture changes in
network states in real-time, recognizing patterns of abnormal
behavior rather than just specific attack signatures. Thus, even
when confronted with unknown or emerging attack types,
CATwin-IDS can promptly detect anomalies and respond
accordingly. Additionally, the modular design of the system
allows for the easy integration of new detection algorithms or
features as needed, further enhancing its adaptability and scalability. These design features indicate that CATwin-IDS, while
excelling in DoS attack detection, also holds the potential to be
extended to other attack types, offering comprehensive security
protection for connected vehicles.
V. C ONCLUSION
This paper addresses the challenge of cross-network intrusions arising from the tight coupling between IVN and EVN by
proposing CATwin-IDS. The framework leverages DistilBERT

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
14

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

with TSA for contextual feature modeling, employs CMI
and Borderline-SMOTE for feature optimization and data
balancing, and integrates digital twin technology to enable
dynamic simulation and real-time synchronization. Experimental evaluations confirm that CATwin-IDS achieves higher
detection performance and efficiency across multiple benchmark datasets, overcoming the limitations of existing IDS in
handling cross-network attacks.
Future work will focus on enhancing the detection of
complex cross-network attacks (e.g., Infiltration and Webbased threats) by enriching the diversity and fidelity of
attack scenarios simulated in the digital twin environment,
addressing the limited availability of rare attack samples. In
addition, model compression and quantization techniques will
be explored to further reduce inference latency and memory
footprint for real-time deployment on in-vehicle edge devices.
Finally, we plan to improve the interpretability of the detection
results, for example through SHAP-based analysis, to provide
deeper insights into feature contributions and model decision
mechanisms.

R EFERENCES
[1]

M. Fu, P. Wang, M. Liu, Z. Zhang, and X. Zhou, “IoV-BERT-IDS:
Hybrid network intrusion detection system in IoV using large language
models,” IEEE Trans. Veh. Technol., vol. 74, no. 2, pp. 1909–1921, Feb.
2025.
[2] Z. Xue, Y. Liu, G. Han, F. Ayaz, Z. Sheng, and Y. Wang, “Two-layer
distributed content caching for infotainment applications in VANETs,”
IEEE Internet Things J., vol. 9, no. 3, pp. 1696–1711, Feb. 2022.
[3] M. Almehdhar et al., “Deep learning in the fast lane: A survey on
advanced intrusion detection systems for intelligent vehicle networks,”
IEEE Open J. Veh. Technol., vol. 5, pp. 869–906, 2024.
[4] S. Wang, Y. Wang, B. Zheng, J. Cheng, Y. Su, and Y. Dai, “Intrusion
detection system for vehicular networks based on MobileNetV3,” IEEE
Access, vol. 12, pp. 106285–106302, 2024.
[5] E. Levy, A. Shabtai, B. Groza, P.-S. Murvay, and Y. Elovici, “CAN-LOC:
Spoofing detection and physical intrusion localization on an in-vehicle
CAN bus based on deep features of voltage signals,” IEEE Trans. Inf.
Forensics Security, vol. 18, pp. 4800–4814, 2023.
[6] Q. Liu et al., “MDHP-Net: Detecting an emerging time-exciting threat
in IVN,” 2024, arXiv:2411.10258.
[7] H. Taslimasa, S. Dadkhah, E. C. P. Neto, P. Xiong, S. Ray, and
A. A. Ghorbani, “Security issues in Internet of Vehicles (IoV): A
comprehensive survey,” Internet Things, vol. 22, Jul. 2023, Art. no.
100809.
[8] X. Li et al., “Hardware impaired ambient backscatter NOMA systems: Reliability and security,” IEEE Trans. Commun., vol. 69, no. 4,
pp. 2723–2736, Apr. 2021.
[9] X. Li et al., “Physical-layer authentication for ambient backscatteraided NOMA symbiotic systems,” IEEE Trans. Commun., vol. 71, no. 4,
pp. 2288–2303, Apr. 2023.
[10] D. Zhang, W. Wang, J. Zhang, T. Zhang, J. Du, and C. Yang, “Novel
edge caching approach based on multi-agent deep reinforcement learning
for Internet of Vehicles,” IEEE Trans. Intell. Transp. Syst., vol. 24, no. 8,
pp. 8324–8338, Aug. 2023.
[11] S. Anbalagan, G. Raja, S. Gurumoorthy, R. D. Suresh, and K. Dev,
“IIDS: Intelligent intrusion detection system for sustainable development
in autonomous vehicles,” IEEE Trans. Intell. Transp. Syst., vol. 24,
no. 12, pp. 15866–15875, Dec. 2023.
[12] H. Wang, X. Di, Y. Wang, B. Ren, G. Gao, and J. Deng, “An intelligent
digital twin method based on spatio-temporal feature fusion for IoT
attack behavior identification,” IEEE J. Sel. Areas Commun., vol. 41,
no. 11, pp. 3561–3572, Nov. 2023.
[13] C. Campolo, G. Genovese, A. Molinaro, B. Pizzimenti, G. Ruggeri, and
D. M. Zappalà, “An edge-based digital twin framework for connected
and autonomous vehicles: Design and evaluation,” IEEE Access, vol. 12,
pp. 46290–46303, 2024.

[14] J. R. K. Nicholas and Bloomberg. (Jan. 2022). Teen Hacker Says
He’s Found Way to Remotely Control 25 Teslaevs Around the World.
[Online]. Available: https://fortune.com/2022/01/12/teen-hacker-davidcolombo-took-control-25-tesla-ev/
[15] O. H. Abdulganiyu, T. A. Tchakoucht, and Y. K. Saheed, “A systematic
literature review for network intrusion detection system (IDS),” Int.
J. Inf. Secur., vol. 22, no. 5, pp. 1125–1162, Mar. 2023.
[16] Y. Lee, Y.-E. Kim, J.-G. Chung, and S. Woo, “Real time perfect bit
modification attack on in-vehicle CAN,” IEEE Trans. Veh. Technol.,
vol. 72, no. 12, pp. 15154–15171, Dec. 2023.
[17] M. Xu et al., “Integration of mixture of experts and multimodal generative AI in Internet of Vehicles: A survey,” 2024, arXiv:2401.01544.
[18] L. Yang, A. Moubayed, and A. Shami, “MTH-IDS: A multitiered hybrid
intrusion detection system for Internet of Vehicles,” IEEE Internet
Things J., vol. 9, no. 1, pp. 616–632, Jan. 2022.
[19] K. Agrawal, T. Alladi, A. Agrawal, V. Chamola, and A. Benslimane, “NovelADS: A novel anomaly detection system for intravehicular networks,” IEEE Trans. Intell. Transp. Syst., vol. 23, no. 11,
pp. 22596–22606, Nov. 2022.
[20] R. Ben Said, Z. Sabir, and I. Askerzade, “CNN-BiLSTM: A hybrid deep
learning approach for network intrusion detection system in softwaredefined networking with hybrid feature selection,” IEEE Access, vol. 11,
pp. 138732–138747, 2023.
[21] L. Wang, X. Zhang, D. Li, and H. Liu, “Multi-sensors space and time
dimension based intrusion detection system in automated vehicles,”
IEEE Trans. Veh. Technol., vol. 73, no. 1, pp. 200–215, Jan. 2024.
[22] Q. Lai et al., “Improved transformer-based privacy-preserving architecture for intrusion detection in secure V2X communications,” IEEE
Trans. Consum. Electron., vol. 70, no. 1, pp. 1810–1820, Feb. 2024.
[23] S. Jeong, S. Lee, H. Lee, and H. K. Kim, “X-CANIDS: Signal-aware
explainable intrusion detection system for controller area networkbased in-vehicle network,” IEEE Trans. Veh. Technol., vol. 73, no. 3,
pp. 3230–3246, Mar. 2024.
[24] R. Chen, X. Chen, and J. Zhao, “Private and utility enhanced intrusion
detection based on attack behavior analysis with local differential privacy
on IoV,” Comput. Netw., vol. 250, Aug. 2024, Art. no. 110560.
[25] J. Cui et al., “LH-IDS: Lightweight hybrid intrusion detection system
based on differential privacy in VANETs,” IEEE Trans. Mobile Comput.,
vol. 23, no. 12, pp. 12195–12210, Dec. 2024.
[26] J. Gao, Y. Lu, Y. He, M. Fan, D. Han, and Y. Qiao, “Tokenization
representation and deep-learning-based intrusion detection in Internet of
Vehicles,” IEEE Internet Things J., vol. 11, no. 23, pp. 37974–37987,
Dec. 2024.
[27] S. Li, Y. Cao, Y. Zhang, T. Liao, F. Yan, and H. Lin, “A cloud
collaborative-based intrusion detection and prevention system for IVN,”
IEEE Trans. Cognit. Commun. Netw., vol. 11, no. 4, pp. 2768–2785,
Aug. 2025.
[28] I. Ullah, I. Khalil, X. Bai, S. Garg, G. Kaddoum, and M. Shamim
Hossain, “An ensemble-based hybrid model for the detection of attacks
in the Internet of VehicularTthings,” IEEE Trans. Intell. Transp. Syst.,
vol. 26, no. 10, pp. 17914–17927, Oct. 2025.
[29] Y. Feng, Y. Lai, Y. Chen, Z. Zhang, and J. Wei, “LSTM-based model
compression for CAN security in intelligent vehicles,” IEEE Trans. Artif.
Intell., vol. 5, no. 12, pp. 6457–6471, Dec. 2024.
[30] S. Gao, L. Zhang, L. He, X. Deng, H. Yin, and H. Zhang,
“Attack detection for intelligent vehicles via CAN- bus: A lightweight
image network approach,” IEEE Trans. Veh. Technol., vol. 72, no. 12,
pp. 16624–16636, Dec. 2023.
[31] M. Althunayyan, A. Javed, and O. Rana, “A robust multi-stage intrusion
detection system for in-vehicle network security using hierarchical
federated learning,” Veh. Commun., vol. 49, Oct. 2024, Art. no. 100837.
[32] E. Seo, H. M. Song, and H. K. Kim, “GIDS: GAN based intrusion
detection system for in-vehicle network,” in Proc. 16th Annu. Conf.
Privacy, Secur. Trust (PST), Aug. 2018, pp. 1–6.
[33] Z. Deng, J. Liu, Y. Xun, and J. Qin, “IdentifierIDS: A practical voltagebased intrusion detection system for real in-vehicle networks,” IEEE
Trans. Inf. Forensics Security, vol. 19, pp. 661–676, Oct. 2024.
[34] L. Du, Z. Gu, Y. Wang, and C. Gao, “Open world intrusion detection:
An open set recognition method for CAN bus in intelligent connected
vehicles,” IEEE Netw., vol. 38, no. 3, pp. 76–82, May 2024.
[35] H. M. Song, J. Woo, and H. K. Kim, “In-vehicle network intrusion
detection using deep convolutional neural network,” Veh. Commun.,
vol. 21, Jan. 2020, Art. no. 100198.
[36] S. B. Park, H. J. Jo, and D. H. Lee, “G-IDCS: Graph-based intrusion
detection and classification system for CAN protocol,” IEEE Access,
vol. 11, pp. 39213–39227, 2023.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LIU et al.: CATwin-IDS: CONTEXT-AWARE INTRUSION DETECTION SYSTEM

[37] N. Moustafa and J. Slay, “UNSW-NB15: A comprehensive data set for
network intrusion detection systems,” in Proc. Mil. Commun. Inf. Syst.
Conf. (MilCIS), Nov. 2015, pp. 1–6.
[38] I. Sharafaldin, A. H. Lashkari, and A. A. Ghorbani, “Toward generating
a new intrusion detection dataset and intrusion traffic characterization,”
in Proc. 4th Int. Conf. Inf. Syst. Secur. Privacy (ICISSP), 2018,
pp. 108–116.
[39] S. Latif, W. Boulila, A. Koubaa, Z. Zou, and J. Ahmad, “DTL-IDS: An
optimized intrusion detection framework using deep transfer learning
and genetic algorithm,” J. Netw. Comput. Appl., vol. 221, Jan. 2024,
Art. no. 103784.
[40] M. A. Ferrag, O. Friha, D. Hamouda, L. Maglaras, and H. Janicke,
“Edge-IIoTset: A new comprehensive realistic cyber security dataset of
IoT and IIoT applications for centralized and federated learning,” IEEE
Access, vol. 10, pp. 40281–40306, 2022.
[41] N. Koroniotis, N. Moustafa, E. Sitnikova, and B. Turnbull, “Towards
the development of realistic botnet dataset in the Internet of Things for
network forensic analytics: Bot-IoT dataset,” Future Gener. Comput.
Syst., vol. 100, pp. 779–796, Nov. 2019.
[42] S. Li, Y. Cao, G. Peng, M. Li, W. Sun, and L. Chen, “Efficient intrusion
detection for in-vehicle networks using knowledge distillation from
BERT to CNN-BiLSTM,” IEEE Trans. Inf. Forensics Security, vol. 20,
pp. 6398–6412, Jun. 2025.
[43] H. A. Bimmo and B. Rahardjo, “Fed-CALiBER: Federated lightweight
BERT intrusion detection on CAN bus protocol in autonomous vehicle,”
IEEE Access, vol. 13, pp. 172384–172401, 2025.
[44] A. Sharma and S. Rani, “Context-aware authentication framework for
secure V2V and V2I communications in autonomous vehicles using
LLM,” IEEE Trans. Intell. Transp. Syst., early access, May 12, 2025,
doi: 10.1109/TITS.2025.3563913.
[45] S. Amaouche et al., “FSCB-IDS: Feature selection and minority class
balancing for attacks detection in VANETs,” Appl. Sci., vol. 13, no. 13,
p. 7488, Jun. 2023.
[46] F. S. Alrayes, M. Zakariah, S. U. Amin, Z. I. Khan, and M. Helal,
“Intrusion detection in IoT systems using denoising autoencoder,” IEEE
Access, vol. 12, pp. 122401–122425, 2024.
[47] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pretraining of deep bidirectional transformers for language understanding,”
in Proc. Conf. North Amer. Chapter Assoc. Comput. Linguistics, Hum.
Lang. Technol. Minneapolis, MI, USA: Association for Computational
Linguistics, vol. 1, Jun. 2019, pp. 4171–4186.
[48] E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu, and
A. A. Ghorbani, “CICIoT2023: A real-time dataset and benchmark
for large-scale attacks in IoT environment,” Sensors, vol. 23, no. 13,
p. 5941, Jun. 2023.
[49] E. C. P. Neto et al., “CICIoV2024: Advancing realistic IDS approaches
against DoS and spoofing attack in IoV CAN bus,” Internet Things,
vol. 26, Jul. 2024, Art. no. 101209.

Chang Liu (Member, IEEE) received the B.E.
and M.S. degrees from Jilin University, Changchun,
China, in 2009 and 2012, respectively, and
the Ph.D. degree from Kansas State University,
Manhattan, KS, USA, in 2016. She is currently a
Full Professor with Guangdong University of Technology, Guangzhou, China. Her current research
areas include the Internet of Vehicles and 6G
communications.

Yurong Zhang (Graduate Student Member, IEEE)
received the B.E. degree in electronic information engineering from Hengyang Normal University,
Hengyang, China, in 2023. She is currently pursuing the master’s degree in new-generation electronic information technology with the School of
Information Engineering, Guangdong University of
Technology, Guangzhou, China. Her research interests include the Internet of Vehicles and intrusion
detection systems.

15

Zheng Xue received the M.E. degree in electronic and communication engineering and the Ph.D.
degree in information and communication engineering from Guangdong University of Technology,
Guangzhou, China, in 2021 and 2024, respectively.
He is currently a Post-Doctoral Research Fellow
with the Department of Communication Engineering, Guangdong University of Technology. His
research interests include vehicular networks, edge
intelligence, and cooperative perception.

Zhengguo Sheng (Senior Member, IEEE) received
the B.Sc. degree from the University of Electronic
Science and Technology of China, Chengdu, China,
in 2006, and the M.S. and Ph.D. degrees from the
Imperial College London, London, U.K., in 2007
and 2011, respectively. He is currently a Professor
and the Dean of Sussex AI Institute, University
of Sussex, U.K. Previously, he was with UBC,
Vancouver, BC, Canada, as a Research Associate and
with Orange Laboratories as a Senior Researcher.
He has more than 160 publications. His research
interests cover the IoT, vehicular communications, and cloud/edge computing.
He is also a Senior Member of IET and a fellow of The Higher Education
Academy (HEA).

Jiawen Kang (Senior Member, IEEE) received
the M.S. and Ph.D. degrees from Guangdong University of Technology, China, in 2015 and 2018,
respectively. He is currently a Full Professor with
Guangdong University of Technology. He was a
Post-Doctoral Researcher with Nanyang Technological University, Singapore, from 2018 to 2021.
His research interests focus on blockchain, metaverse, and AIGC in wireless communications and
networking.

Guojun Han (Senior Member, IEEE) received
the M.E. degree from the South China University of Technology, Guangzhou, China, in 2004,
and the Ph.D. degree from Sun Yat-sen University,
Guangzhou, in 2011. From March 2011 to August
2013, he was a Research Fellow with the School
of Electrical and Electronic Engineering, Nanyang
Technological University, Singapore. From October
2013 to April 2014, he was a Research Associate
with the Department of Electrical and Electronic
Engineering, The Hong Kong University of Science
and Technology. He is currently a Full Professor and the Dean of the School of
Information Engineering, Guangdong University of Technology, Guangzhou.
His research interests are in the areas of wireless communications, signal
processing, and coding and information theory. He has more than 15 years
experience on research and development of advanced channel coding and
signal processing algorithms and techniques for various data storage and
communication systems.
PAPER_TEXT
