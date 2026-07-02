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
# [582] A Domain-Informed Hierarchical Federated Learning Framework for DDoS Detection in WSN for Critical Infrastructure
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
编号：582
题名：A Domain-Informed Hierarchical Federated Learning Framework for DDoS Detection in WSN for Critical Infrastructure
年份：2026
DOI：10.1109/tnsm.2026.3693112
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2026.3693112.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：IoT、车联网、工业互联网与边缘安全、恶意流量、暗网与攻击检测
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\582.txt
- 原始字符数：94406
- 本次发送字符数：94406
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
4586

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

A Domain-Informed Hierarchical Federated
Learning Framework for DDoS Detection
in WSN for Critical Infrastructure
Md Facklasur Rahaman , Makhduma F. Saiyed , Member, IEEE, Irfan Al-Anbagi , Senior Member, IEEE,
and Ramakrishna Gokaraju , Senior Member, IEEE

Abstract—The deployment of Wireless Sensor Networks
(WSN) in critical infrastructure, such as Small Modular Reactors
(SMRs), faces cybersecurity threats like Distributed Denial of
Service (DDoS) attacks that can overload these networks and
disrupt monitoring and control functions. Current DDoS detection systems often suffer from high false positive rates, neglect
domain-specific operational constraints, and rely on centralized
architectures that pose privacy risks, making them less suitable
for distributed Internet of Things (IoT) environments. To address
these issues, we propose a novel Domain-informed Hierarchical
Federated Learning (DHFL) framework for WSN used in SMR
monitoring and control applications. Our framework features
a dual-branch bidirectional Long Short-Term Memory (LSTM)
architecture comprising of two parallel processing branches
with network-specific constraints, facilitating precise detection
of DDoS attacks. It includes differentiable penalty functions to
enforce domain-aligned behaviour and employs adaptive trust
scoring to evaluate the reliability of individual nodes. These
elements operate within a hierarchical Federated Learning (FL)
structure organized into three tiers: sensor nodes, local aggregators, and a global coordinator, allowing collaborative training
that preserves privacy. Unlike earlier approaches, our method
not only maintains privacy by ensuring that raw sensor data
never leaves the local nodes and only model updates are shared
but also considers the operational importance and trustworthiness of each node through tier-weighted aggregation. Tested on
the CICIoT2023 dataset, our system achieved 93.4% accuracy,
94.5% precision, 97.5% recall, 95.5% F1-score, and 98.9% AUC,
surpassing state-of-the-art FL methods in both performance and
efficiency. Furthermore, it converged in fewer communication
rounds (30–50) with reduced communication costs (from 45 MB
to 30 MB per round). Our framework can differentiate between
normal reactor transients and actual attacks, making it suitable
for mission-critical SMR cybersecurity.

Received 24 December 2025; revised 8 April 2026; accepted 8 May 2026.
Date of publication 13 May 2026; date of current version 19 May 2026.
This work was funded by the Natural Sciences and Engineering Research
Council of Canada and Canadian Nuclear Safety Commission as the Small
Modular Reactors Research Grant, ALLRP 580480-2022. The associate editor
coordinating the review of this article and approving it for publication was
K. Hammar. (Corresponding author: Irfan Al-Anbagi.)
Md Facklasur Rahaman and Irfan Al-Anbagi are with the Faculty of
Engineering and Applied Science, University of Regina, Regina, SK S4S 0A2,
Canada (e-mail: facklasurrahaman@gmail.com; Irfan.Al-Anbagi@uregina.ca).
Makhduma F. Saiyed is with the Department of Computer Science, Trent
University, Oshawa, ON L1J 5Y1, Canada (e-mail: makhdumabanusaiyed@
trentu.ca).
Ramakrishna Gokaraju is with the Department of Electrical and Computer
Engineering, University of Saskatchewan, Saskatoon, SK S7N 5A9, Canada
(e-mail: rama.krishna@usask.ca).
Digital Object Identifier 10.1109/TNSM.2026.3693112

Index Terms—Wireless sensor networks (WSN), small modular reactor (SMR), distributed IoT sensors, federated learning,
LSTM, hierarchical aggregation, DDoS attack detection, domaininformed LSTM, trust-aware systems.

I. I NTRODUCTION

W

IRELESS Sensor Networks (WSN) have emerged as
fundamental building blocks for modern Internet of
Things (IoT) systems. They enable real time monitoring and
control across diverse industrial applications through distributed sensing capabilities and autonomous data collection
mechanisms. These networks, consisting of spatially distributed sensor nodes that communicate wirelessly to monitor
physical or environmental conditions, have proven valuable in
mission-critical infrastructures where continuous monitoring
and rapid response capabilities are essential for operational
safety [1]. These networks have found widespread adoption
across various sectors including energy industry automation,
transportation systems, and critical infrastructure protection,
demonstrating their versatility and reliability in missioncritical applications [2].
The use of WSNs in critical infrastructure such as Small
Modular Reactors (SMR)-based power generation units facilitate real-time condition monitoring, support safety, and enable
rapid decision-making [3]. As critical infrastructure components, SMR-based power generation units rely on WSN to
enable real-time monitoring of reactor parameters, coolant
systems, and safety mechanisms across distributed facility
locations. However, these technological advances also expose
SMRs to a variety of cyber threats, particularly in terms of
potential disruptions that could compromise the integrity and
safety of these critical systems.
Among the various cyber threats facing SMR-based power
generation units, Distributed Denial of Service (DDoS) attacks
pose a significant risk due to their potential to overwhelm
the WSN enabled systems [4]. In such environments, WSN
deployments create distributed attack surfaces where DDoS
threats can target individual sensor nodes, communication
gateways, or the entire network. Typically initiated by botnets
or malicious entities, these attacks flood the network with
traffic, disrupting real-time monitoring, control, and safety
operations by congesting sensor communication links and data
aggregation points [5]. The distributed nature of WSN makes

1932-4537 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

RAHAMAN et al.: DOMAIN-INFORMED HIERARCHICAL FL FRAMEWORK FOR DDoS DETECTION

them particularly vulnerable, as attackers can simultaneously
target multiple sensor clusters to amplify disruption effects.
For instance, one of the most notable DDoS attacks takes
place in 2022, when Ukraine’s state-owned nuclear power
company, Energoatom, reports an unprecedented DDoS attack
orchestrated by the hacktivist group People’s Cyber Army. The
group employs a botnet of 7.25 million compromised accounts
to flood Energoatom’s website, rendering it temporarily inaccessible. Despite the scale of the attack, Energoatom quickly
regains control and no operational disturbances are reported at
the nuclear facilities [6]. Additionally, the United Kingdom’s
Sellafield nuclear waste site experiences cyberattacks. While
these attacks did not directly damage critical systems, they
underscore the persistent threat to critical infrastructure facilities and their supporting WSN architectures [7]. In 2021, a
cybercriminal group, Garnesia Team, claimed responsibility
for a DDoS attack on the Nuclear Power Corporation of India
Limited (NPCIL) website. The attack results in temporary
inaccessibility of the site, although no impact on operational
systems is confirmed [8]. Before North Korea’s nuclear test
in 2016, a DDoS attack targeted a website that monitors the
country’s nuclear test site. The timing of the attack raises
suspicions about its origin, although there is no direct evidence
linking it to state-sponsored actors [9].
To detect various cyberattacks, several detection approaches
have been developed using Machine Learning (ML) and Deep
Learning (DL) models. These models are trained on historical
data to recognize and classify malicious traffic. However,
existing solutions face multiple limitations for critical infrastructure [10]. Traditional Intrusion Detection Systems (IDS)
often produce high false positives in dynamic environments
[11], which is unacceptable for critical infrastructure where
false alarms can lead to costly shutdowns and missed detections can pose radiological risks [12]. These systems also
lack integration of the domain knowledge of the operational
network, leading to misclassification of legitimate transitions
of the state of the reactor as anomalies and the failure to detect
attacks that breach the specific time and safety constraints
of the SMR [13]. Furthermore, the heterogeneity of sensor
communication patterns in WSN-based architectures, which
varies with physical location and operational criticality, makes
detection more challenging.
To overcome the limitations of conventional ML and DL
models in specialized critical infrastructure, researchers have
explored domain-informed approaches that embed specific
operational constraints into the detection process. One such
model, the Domain Informed Long Short-Term Memory
(LSTM), integrates physics-based rules such as permissible
packet rates, bandwidth thresholds, and thermal safety limits
into its architecture [14]. This design helps reduce false
positives by aligning model behavior with actual operation
conditions, allowing it to better differentiate between normal system state transitions and malicious traffic. However,
while domain-informed models improve context awareness
and detection accuracy, they still rely on centralized architectures and require access to large volumes of sensitive
operational data, which introduces privacy risks and communication overhead.

4587

To address the privacy and communication limitations
of centralized domain-informed models, Federated Learning
(FL) has emerged as a promising approach that enables
decentralized model training directly on edge devices [15].
This eliminates the need to transmit sensitive raw data,
reducing communication overhead and privacy risks [16],
[17]. FL allows distributed devices to collaboratively train
models while sharing only model updates with a central
aggregator [18]. However, conventional FL frameworks also
exhibit critical limitations in such networks. Specifically, they
fail to address the heterogeneous and multi-tiered architectures, where certain tiers require a higher level of trust
and influence compared to peripheral monitoring devices.
Moreover, most existing FL methods do not incorporate
operational domain constraints, which are essential to reliably distinguish between normal behavior and malicious
activity.
To address these challenges, this paper proposes a Domaininformed Hierarchical Federated Learning (DHFL) framework,
designed for cyberattack detection in critical infrastructure.
The DHFL framework enables collaborative model training
across distributed sensor nodes without sharing raw data, thus
preserving privacy and reducing communication overhead.
The framework integrates a domain-informed BiLSTM model
with a hierarchical, trust-aware aggregation mechanism that
reflects the varying criticality of the nodes within the networks.
The core novelty lies in its dual-branch LSTM architecture
(DI-LSTM), which concurrently captures temporal network
traffic patterns and specific operational constraints through
a differentiable penalty function. This design enables DHFL
framework to accurately distinguish between legitimate operational transients from reactors and actual cyberattacks. By
embedding domain knowledge directly into both the model
architecture and the training process, the proposed system
overcomes the limitations of traditional IDS approaches, which
often generate high false positives by misclassifying routine
state changes as anomalies. The primary contributions of this
paper are as follows:
• We propose a domain-informed dual-branch Bi-LSTM
model for detecting DDoS attacks in IoT networks.
This model integrates temporal traffic pattern learning
with domain constraints such as packet rate limits and
control system latencies. Embedding these constraints as
differentiable penalty functions improves detection accuracy and reduces false positives by enforcing physically
consistent behavior.
• We develop a hierarchical FL framework (DHFL) to
preserve data privacy and address node heterogeneity that
groups nodes by criticality into core, edge, and peripheral
tiers based on their influences. An adaptive trust scoring
mechanism evaluates nodes across multiple dimensions
to guide participant selection and trust-weighted aggregation, thus improving robustness against malicious clients.
• We incorporate secure aggregation protocols to protect local model updates during federated training.
This ensures a resilient and privacy-preserving detection framework, tailored for the stringent cybersecurity
requirements of mission-critical SMR environments.

4588

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

The remainder of this paper is structured as follows: Section II provides an overview of the related work. Section III
presents a detailed explanation of the proposed methodology.
Section IV elaborates on the performance evaluation of the
overall approach. Finally, Section V concludes the paper and
outlines the directions for future work.
II. R ELATED W ORKS
This section reviews the state-of-the-art in detecting DDoS
attacks, with particular emphasis on ML, DL and FL frameworks in cyber-physical systems. Recent advances in FL
techniques aimed at preserving data privacy and addressing heterogeneous, resource-constrained environments are
critically examined. Additionally, the emergence of physicsinformed DL models which integrate domain-specific operational constraints to enhance anomaly detection accuracy and
interpretability, is discussed.
The development of DDoS detection has gained significant
attention in recent years due to its criticality in ensuring the
security and privacy of critical and sensitive infrastructures.
The authors in [24] proposed a holistic feature engineering and
ML framework for detecting DDoS attacks, which simulated
cross-layer DDoS attacks in standardized IoT networks based
on the 6LoWPAN protocol stack. It achieved enhanced detection accuracy and reduced computational overhead through
optimized feature selection and ensemble classification. The
proposed approach relied on offline training and centralized
detection on the 6LoWPAN Border Router, which could
become a single point of failure and faced practical challenges
in real-world deployment related to sniffer node placement
and communication reliability. In [22], the authors proposed
a time-efficient Software-Defined Networking (SDN)-based
security framework using a customized SDNWISE controller
to detect DDoS attacks in IoT networks through session IP
counters and IP payload analysis. The framework achieved
early-stage detection with high accuracy (98%–100%) and low
false positive rates. However, it relied on a centralized controller and logging mechanism, which could become a single
point of failure and face scalability issues in large, diverse
IoT deployments. Similarly, in [21], the authors introduced
an explainable hybrid DL model that combined convolutional
neural network (CNN) and LSTM for real-time DDoS detection in SDN-IoT-based Healthcare Industry 5.0 environments.
They used SHapley Additive exPlanations (SHAP) for interpretability and showed high detection accuracy on benchmark
datasets. However, the model’s dependence on supervised
learning and large amounts of training data might limit its
ability to adapt to new or evolving attack types in dynamic
healthcare IoT systems.
Building upon these advancements, recent research has
explored the integration of domain-specific knowledge into
ML models to enhance detection robustness and interpretability in critical IoT environments and infrastructures. Among
these, the Physics-Informed DL model stands out by embedding physical constraints directly into the detection process,
addressing key challenges in safeguarding sensitive and safetycritical networks. Likewise, Wu et al. [14] developed a

physics-informed recurrent neural network (PIRNN) detector
combined with a knowledge-guided extended Kalman filter
(EKF) for real-time detection and resilient control of sensor
cyberattacks in nonlinear chemical processes. This approach
showed improved detection accuracy, lower data requirements,
and better state estimation compared to traditional data-driven
methods. Additionally, Wu et al. [23] proposed a physicsinformed graph convolutional recurrent network (PIGCRN)
that incorporated chemical process topology and prior knowledge of cyberattack patterns into a unified spatial-temporal
learning framework. This model improved detection accuracy in complex chemical process networks while reducing
the need for large training datasets. However, both methods
depended on accurate prior knowledge of attack patterns and
system-specific domain information, which could limit their
effectiveness against unknown or evolving cyberattacks and
in cases with incomplete or inaccurate process models.
Moreover, Vyas et al. [25] developed a physics-informed
neural network (PINN) framework for cyberattack detection
in vehicle platoons which combines physics-based models and
real-time data to improve attack isolability and reduce the
effect of model uncertainties. Gaggero et al. [26] provided
a survey of AI-based and physics-based anomaly detection
methods in the Smart Grid, highlighting the integration of
physical laws with ML to improve detection robustness and
resilience. Lei et al. [27] proposed a physics-informed LSTM
with adaptive weight allocation for accurate and stable prediction of dissolved gases in power transformers. Their method
combined data-driven and physical models to enhance forecast
accuracy under normal and fault conditions. However, a common limitation in these works was the reliance on centralized
data collection, raising privacy concerns and limiting scalability and collaborative learning in real-time between distributed,
privacy-sensitive nodes.
Recent advances in FL and physics-informed ML have
demonstrated promising directions for secure, scalable, and
privacy-preserving anomaly detection in heterogeneous IoT
environments. Iqbal et al. [20] proposed a hierarchical continual FL framework for healthcare Internet of Medical
Things (IoMT) applications, integrating continual learning
strategies with FL to overcome catastrophic forgetting while
ensuring privacy and domain knowledge retention through
multi-tier models. Wu et al. [28] addressed the challenge of
non-Independent and Identically Distributed (non-IID) data
distribution in IoT by developing an improved Gale–Shapleybased hierarchical FL method, which pairs devices with
complementary datasets to improve local model quality, thus
improving global convergence speed and accuracy without
additional communication overhead. Similarly, apart from
cyberattack detection, in other target systems, Devaraj et al.
[29] presented a hierarchical FL architecture designed for
precision agriculture, combining distributed sensing with a
personalized FL strategy to enable scalable, privacy-aware
crop health monitoring across geographically dispersed farms.
Wang et al. [19] introduced a two-tier hierarchical FL scheme
supported by aerial relay nodes that serve as both data sources
and intermediate aggregators, optimizing resource allocation
and minimizing latency for FL convergence in wireless IoT

RAHAMAN et al.: DOMAIN-INFORMED HIERARCHICAL FL FRAMEWORK FOR DDoS DETECTION

4589

TABLE I
C OMPARATIVE A NALYSIS OF P ROPOSED DHFL F RAMEWORK W ITH E XISTING W ORKS

networks, thus improving system robustness and communication efficiency. Despite these contributions, the presented
the approaches largely depended on handling heterogeneous,
dynamic, and often non-IID data under strict resource and
privacy constraints. This makes real-time model adaptation
and generalization difficult, especially in privacy-sensitive and
safety-critical IoT applications. Moreover, the lack of explicit
integration of domain-specific physical constraints in anomaly
detection models often results in higher false positive rates
and increased vulnerability to subtle, sophisticated attacks that
closely mimicked normal behavior.
Recent research efforts have begun to address the cybersecurity of SMR-specific control systems, with a focus on
both architectural and detection model innovations. In [13],
Salehpour and Al-Anbagi developed a cyberattack detection system for SMR-based digital substations, integrating
real-time simulation using RTDS and NS3 to evaluate the
performance of machine learning-based detection. However,
their framework lacked domain-informed context and did not
include any privacy-preserving mechanisms. Ayodeji et al.
[30] introduced a wave-attention DL model for real-time
attack detection in digital SMR control systems using the
Asherah Nuclear Simulator. The model demonstrated higher
accuracy compared to traditional approaches; however, it
relied on centralized data processing and did not incorporate
federated or trust-aware learning. Rockabrand’s dissertation
[31] proposed the integration of AI into SMR emergency
preparedness frameworks, focusing on real-time monitoring
and autonomous response. However, it highlighted key challenges in aligning AI with operational safety of SMR and
human decision-making. Meanwhile, Nam et al. [32] introduced a high-fidelity testbed for cyber-physical SMR systems
designed to simulate and evaluate advanced attacks. Despite
its capabilities, the testbed lacked a federated architecture
and a hierarchical defense model. These studies reflected
growing interest in SMR-specific cybersecurity but shared
common limitations in privacy preservation, multi-tier node
organization, and the integration of domain-informed anomaly
detection. Table I shows a comparative analysis of recent

frameworks, highlighting key limitations such as the lack of
hierarchical FL, adaptive trust, and domain-informed models.
In contrast, our proposed framework addresses these gaps
through a domain-aware hierarchical FL approach for SMR
sensor networks.
Our proposed DHFL framework directly addresses the challenges of high false positive rates when legitimate reactor
state transitions (such as startup sequences or emergency
procedures) are misclassified as cyberattacks and the lack hierarchical FL structures that account for the different operational
importance levels in SMR systems, which fails to give critical
reactor control nodes greater influence than peripheral monitoring systems while maintaining privacy across distributed
sensor networks. It does that by embedding network domain
system constraints into a dual-branch DI-LSTM architecture
for temporal and domain-informed feature learning at the
local node level. This integration enforces physically domainconsistent behavior during detection, substantially reducing
false positives and enhancing generalization to unseen attack
patterns. Furthermore, the hierarchical FL structure orchestrates collaborative model training by partitioning SMR IoT
sensor networks into core, edge, and peripheral tiers, with an
adaptive trust scoring mechanism evaluating nodes across multiple dimensions to ensure robust aggregation that is resilient
to malicious or low-quality updates. This tiered approach
balances computational load and communication overhead,
enabling scalable, privacy-preserving, and upgraded DDoS
attack detection within resource-constrained mission-critical
environments. By coupling domain-informed local learning
with trust-aware hierarchical FL, our DHFL framework overcomes the inherent limitations of existing IoT anomaly
detection frameworks, providing a logically and technically
sound solution to safeguard critical infrastructure in complex,
dynamic settings.
III. T HE P ROPOSED DHFL F RAMEWORK
W ITH W ORKFLOW
Before presenting our DHFL framework architecture, it
is essential to establish the foundational context of SMR

4590

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 1. DHFL framework for DDoS detection in SMR sensor networks with
tier-weighted aggregation.

operational environments and their cybersecurity requirements.
This preliminary discussion provides the necessary background to understand why conventional FL approaches are
insufficient for critical infrastructure and how our domaininformed hierarchical design addresses the specific challenges
of SMR sensor networks. The following subsections detail the
operational constraints, security hierarchies, and trust dynamics that inform our DHFL framework design decisions.
A. WSN-Based SMR Monitoring
Unlike conventional IoT environments, SMR IoT networks
operate under stringent safety-critical constraints where sensor
data directly influence reactor control decisions, necessitating
detection systems that inherently understand physical operational boundaries. We consider a hierarchical FL structure
with three distinct tiers core (reactor control systems), edge
(secondary monitoring), and peripheral (facility networks)
which mirror the inherent security classification and operational criticality within SMR where core systems demand
the highest trust and computational priority while peripheral
systems provide supplementary intelligence without compromising critical operations. This tiered approach becomes
essential given that SMR are typically deployed in geographically isolated, high-security zones where centralized
data aggregation poses both logistical and cybersecurity risks,
making FL not only advantageous, but operationally necessary. The integration of Domain-Informed LSTM (DI-LSTM)
over traditional LSTM architectures addresses a fundamental limitation in cyber-physical attack detection: conventional
models may flag legitimate operational transients (such as
reactor startup sequences or emergency response procedures)
as anomalies, whereas DI-LSTM incorporates domain-specific
constraints as differentiable penalty functions within the dualbranch architecture to distinguish between benign operational
variations and genuine cyberattacks. The adaptive trust scoring
mechanism becomes critical in this context because SMR
nodes exhibit heterogeneous reliability profiles based on their
physical location, security clearance levels, and exposure to

electromagnetic interference. Figure 1 illustrates the proposed
DHFL framework.
DHFL contains a dual-branch bidirectional LSTM architecture that simultaneously processes temporal network traffic
patterns and SMR-specific operational constraints through differentiable penalty functions, integrated within a hierarchical
FL structure with adaptive trust scoring. Initially, distributed
SMR sensor nodes (organized into core, edge, and peripheral)
locally train dual branch bidirectional LSTM models on private
datasets. It also simultaneously computes domain compliance
penalties through domain-informed constraints in the network.
This can distinguish legitimate reactor operational transients
from genuine cyberattacks. These nodes then transmit model
parameters and trust metrics to a central aggregator which
evaluates multidimensional trust scores across six dimensions (accuracy, data quality, timeliness, consistency, domain
compliance, security clearance) and performs tier-aware node
selection, which ensures balanced representation across operational hierarchies. For our framework, we choose these
six dimensions because they can capture both computational
readability and operational integrity. Computational readability
tracks four dimensions, which are accuracy, data quality,
timeliness, and consistency, whereas operational integrity adds
domain compliance and security clearance assessments. This
is crucial for SMR environments where individual nodes
show different reliability patterns. The placement of the nodes
varies based on their physical location, security level requirements, and exposure to electromagnetic interference. These
factors can degrade specific performance metrics, making
trust evaluation across those dimensions essential for maintaining the framework’s integrity. The aggregation proceeds
through a two-level scheme: intra-tier trust-weighted averaging followed by inter-tier combination using fixed weights
(core = 0.5, edge = 0.3, peripheral = 0.2), preserving the
strategic influence of critical reactor control systems while
incorporating intelligence from secondary monitoring and
facility networks. Finally, the global model is distributed
back to participating nodes, enabling continuous adaptation to
evolving threats while maintaining network domain-informed
constraints essential for SMR operational integrity, creating a
hierarchically aware, privacy-preserving defense framework.
B. Problem Formulation
The problem of DDoS attack detection in SMR sensor
networks can be formally characterized as a multi-objective
optimization challenge that must simultaneously address
anomaly detection accuracy, privacy preservation, and operational integrity under safety-critical constraints. Let N =
{N1 , N2 , . . . , Nn } represent the set of distributed SMR
sensor nodes organized into three hierarchical tiers Θ =
{Θcore , Θedge , Θperipheral }, where each node Ni maintains a
|Di |
local dataset Di = {(xi,j , yi,j )}j=1
containing network traffic
features and binary labels (DDoS/Normal). The primary objective is to learn a global detection model θglobal that minimizes
the federated loss function:
n
X
min
ωi · τi · L(fθ (Xi ), Yi ) + λ · Φ(Xi )
(1)
θglobal

i=1

RAHAMAN et al.: DOMAIN-INFORMED HIERARCHICAL FL FRAMEWORK FOR DDoS DETECTION

subject to the constraints: Raw data Di never leave node
(t)
Ni , with only model parameters θi transmitted during
federated rounds; All network features must satisfy SMR
operational bounds; Node influence weights ωi must reflect
both tier membership
tier ∈ {0.5, 0.3, 0.2}) and adaptive
P(ω
6
trust scores τi =
d=1 ωd · si,d across six dimensions;
and Local datasets exhibit heterogeneous class distributions
|DDoS|i /|Normal|i 6= constant, reflecting real-world deployment scenarios where different SMR subsystems experience
varying attack patterns.
The dual-branch domain-informed architecture addresses
the fundamental limitation that conventional LSTM models
cannot distinguish between legitimate operational transients
(reactor state transitions, emergency procedures) and malicious
anomalies, as both may exhibit similar statistical signatures but
differ in their adherence to reactor constraints. The domain
penalty function Φ(P, B, S) = (ϕpacket · ϕbandwidth · ϕsize )1/3
acts as a domain-informed regularizer that penalizes violations of SMR communication constraints, thereby reducing
false positive rates. The hierarchical FL framework with tierP
(t+1)
(t+1)
weighted aggregation θglobal =
ensures
tier ωtier · θtier
that critical reactor control nodes (Core Tier) maintain disproportionate influence over the global model while still
incorporating intelligence from secondary monitoring systems
(edge tier) and administrative facility networks (peripheral
tier), thus balancing detection accuracy with operational
safety priorities. This formulation transforms the traditionally centralized DDoS detection problem into a distributed,
privacy-preserving solution that explicitly accounts for the
heterogeneous, mission-critical nature of the SMR cyberphysical infrastructure.

4591

where xt represents the input feature vector at time t, ht and
Ct denote the hidden and cell states respectively, W{f,i,C,o}
and b{f,i,C,o} are learnable weights and biases, σ(·) is the
sigmoid activation function, and
indicates element-wise
multiplication.
To enrich the model’s representation capacity for detecting
bidirectional attack patterns, a bidirectional configuration is
employed where the output at each time step t is a concatenation of forward and backward hidden states:
→
− ←
−
ht = [ ht ; ht ].
(8)
The Bi-LSTM architecture implemented in this study
comprises two layers optimized for SMR network traffic characteristics. The first layer contains 128 bidirectional units with
return sequences enabled, followed by batch normalization
and dropout (rate = 0.4) to prevent overfitting. The second
layer consists of 64 bidirectional units without sequence
return, again followed by batch normalization and dropout
(rate = 0.4). These stacked layers allow the model to abstract
multi-level temporal features from the input traffic flows,
progressing from low-level packet-by-packet patterns to highlevel communication flow signatures. Subsequent dense layers
perform nonlinear transformations for binary classification,
with dropout rates of 0.3 and 0.2 respectively to maintain
generalization capability.
This temporal encoder serves as the foundation for the
domain-informed dual-branch design, which further incorporates domain-specific physical constraints of SMR systems
to distinguish between legitimate operational transients and
genuine cyberattacks, as detailed in the following subsection.
D. Domain-Informed Dual-Branch LSTM Architecture

C. Temporal-Aware LSTM Modeling for Traffic Dynamics
Building upon the formalized optimization framework, the
detection of DDoS attacks in SMR IoT sensor networks
requires the capture of rapid, temporal deviations in otherwise consistent communication flows that characterize normal
reactor operations. These time-sensitive anomalies manifest
as sudden changes in packet transmission patterns, spikes in
bandwidth utilization, or unusual latency variations that can
compromise critical control communications. To address this
temporal complexity, we employ a neural network capable of
learning temporal dependencies in both forward and backward
directions.
The LSTM architecture is governed by gated operations that
regulate the flow of information across time steps, dynamically updating the memory and hidden states of the network
to capture both long-term operational baselines and shortterm anomalous deviations. The functional components of the
LSTM cell are defined as follows:
ft = σ(Wf [ht−1 , xt ] + bf ),

(2)

it = σ(Wi [ht−1 , xt ] + bi ),

(3)

C̃t = tanh(WC [ht−1 , xt ] + bC ),

(4)

Ct = ft

C̃t ,

(5)

ot = σ(Wo [ht−1 , xt ] + bo ),

(6)

ht = ot

(7)

Ct−1 + it
tanh(Ct ),

Building upon the foundation of temporal modeling established in the previous subsection, we enhance the robustness
of the detection framework by extending the core Bi-LSTM
network with a domain-informed module that integrates
domain-specific constraints from SMR operations, as shown
in Figure 2. This dual-branch architecture enables the model
to process temporal traffic features and physically grounded
attributes in parallel, enforcing structural priors during learning, and reducing susceptibility to adversarial or physically
implausible inputs that could compromise detection accuracy
in safety-critical SMR environments.
The operational characteristics of SMRs impose network
domain constraints on communication behavior, particularly
in the dynamics of data transmission rates, packet sizes, and
bandwidth usage [33]. These constraints are derived from
safety-critical assumptions about reactor control loops and
sensor bandwidth limits established through rigorous nuclear
engineering standards [34], [35], [36]. Specifically, the following operational bounds are defined based on SMR control
system specifications:
Maximum packet rate:


Rmax
,
(9)
Pmax = Pnorm 1 +
100
where Pnorm = 1000 packets/sec represents the nominal rate
and Rmax = 500% defines the allowable deviation.

4592

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 2. Dual-branch Bi-LSTM model with domain-informed features for
DDoS detection in SMR.

Maximum bandwidth:

Bmax = Bnorm

Bchange
1+
100


,

(10)

The aggregate domain compliance score is computed using
the geometric mean to ensure balanced consideration of all
physical dimensions:

with Bnorm = 10 Mbps and Bchange = 800%.
Maximum packet size:
Smax = 2 · Snorm ,

(11)

where Snorm = 1500 bytes.
Rate-of-change constraint on packet rate:
Pmax − Pnorm
dP (t)
≤
,
dt
Tcontrol

are designed with specific capacity limits. The response time
of the control system (Tcontrol = 100 ms) is particularly
significant, as it encodes the fundamental timing constraints
of safety-critical control loops that cannot physically respond
faster than their mechanical and electrical components allow
[38], [39], [40], [41], [42].
To evaluate the adherence to operational constraints, we
define a generalized domain compliance framework. Consider a cyber-physical system with M constraint dimensions.
For each dimension k, we define a compliance function as
ϕk (xk ) = min(1, xbound
/xk ). This function returns 1 when the
k
observed value xk stays within the operational bound xbound
.
k
It degrades monotonically as the value exceeds the bound.
The aggregate compliance score is the geometric mean across
Q
1/M
M
all dimensions: Φ(x) =
ϕ
(x
)
. This ensures
k
k
k=1
balanced penalization when any constraint is violated [43].
For SMR sensor networks, we instantiate our framework with
M = 3 constraint dimensions using the operational bounds
defined in Equations (9)–(11):


Pmax
,
(13)
ϕpacket (P ) = min 1,
P


Bmax
ϕbandwidth (B) = min 1,
,
(14)
B


2 · Smax
.
(15)
ϕsize (S) = min 1,
S

(12)

with Tcontrol = 100 ms representing the response latency of
the SMR control systems. These values serve as demonstration
parameters for framework validation.
Due to the classified nature of actual SMR operational data,
we employ representative parameter values for demonstration
purposes, as our primary focus is to build the framework architecture. The domain-informed constraints are hypothesized
and considered from established nuclear industry standards
with parameters refined through empirical analysis of the
CICIoT2023 dataset [37] to ensure operational relevance. The
normal packet rate (Pnorm = 1000 packets/sec) represents
the typical traffic volume observed in industrial control networks used in nuclear facilities, which maintain constant
message rates for sensor readings and control commands.
The maximum allowable deviation (Rmax = 500%) accounts
for legitimate traffic spikes during reactor state transitions
(e.g., startup sequences or emergency response procedures),
while still identifying anomalous behavior beyond physical
possibility. Similarly, the bandwidth parameters (Bnorm =
10 Mbps, Bchange = 800%) reflect the bounded communication
infrastructure in SMR environments, where network interfaces

Φ(P, B, S) = (ϕpacket (P ) · ϕbandwidth (B) · ϕsize (S))

1/3

. (16)

This formulation ensures a smooth penalty gradient and
enforces proportional degradation for violations in any of the
physical domain dimensions, guiding the model away from
physically implausible network behavior patterns.
The dual-branch LSTM architecture is implemented through
parallel processing steps. The main branch processes timeseries network features through the Bi-LSTM stack described
in the previous subsection. Concurrently, the domain-informed
branch extracts and transforms physical features at the
final time step, incorporating the following domain-specific
attributes:
• Packet rate (packets/sec)
• Average packet size (bytes)
• Bandwidth usage (Mbps)
• Domain penalty score Φ
Let X ∈ RT ×d denote the input tensor, where T is the
number of time steps and d is the number of features. The
Domain-specific features are extracted using a custom Lambda
function at the final time step T :
fphysics (X) = XT,Iphysics ,

(17)

where Iphysics indexes the physical domain features. These
features are then processed through a nonlinear transformation
pipeline:
zphysics = ReLU(Wphysics fphysics + bphysics ),

(18)

RAHAMAN et al.: DOMAIN-INFORMED HIERARCHICAL FL FRAMEWORK FOR DDoS DETECTION

z̃physics = BatchNorm(zphysics ),

(19)

ẑphysics = Dropout(z̃physics , p = 0.3).

(20)

4593

The outputs from the LSTM temporal encoder hLSTM and the
domain-informed encoder ẑphysics are concatenated to form a
unified representation:
zcombined = [hLSTM ; ẑphysics ].

(21)

This joint embedding is passed through fully connected layers
for final classification:
z1 = ReLU(W1 zcombined + b1 ),

(22)

z̃1 = BatchNorm(z1 ),

(23)

ẑ1 = Dropout(z̃1 , p = 0.3),

(24)

z2 = ReLU(W2 ẑ1 + b2 ),

(25)

ẑ2 = Dropout(z2 , p = 0.2),

(26)

ŷ = Softmax(W3 ẑ2 + b3 ).

(27)

This dual-branch configuration ensures that the model not
only learns abstract temporal representations but also incorporates network domain constraints into its decision boundary.
During training, the inclusion of the penalty score Φ as a
feature and regularizer guides the model away from physically implausible decisions, thus improving generalization and
adversarial robustness in SMR-specific operational settings.
However, deploying this model across distributed SMR sensor
networks presents challenges related to data privacy, computational efficiency, and domain security separation. To address
these challenges while preserving the benefits of the domaininformed approach, we integrate this architecture within a
hierarchical FL framework, as detailed in the following subsection.
E. Federated Learning With Hierarchical Structure
The domain-informed dual-branch LSTM architecture provides a robust foundation for detecting DDoS attacks by
incorporating both temporal network patterns and SMRspecific network domain constraints. However, deploying this
model across distributed SMR sensor networks presents challenges related to data privacy, computational efficiency, and
security domain separation. To preserve the confidentiality of
sensor-level network traffic while enabling collaborative learning across SMR nodes, we implemented an FL architecture
that allows decentralized nodes to train local models without
exposing raw data, thus mitigating risks of centralized data
leakage.
Not all nodes in an SMR environment exhibit equal trustworthiness or criticality due to their varying operational roles
and security classifications. To account for this inherent heterogeneity, we employ a hierarchical FL structure that stratifies
nodes into security tiers and applies weighted aggregation
based on both tier level and trust score, as illustrated in
Figure 3.
1) Hierarchical Node Organization: The Nodes are organized into three tiers according to their operational roles and
associated security levels. This reflects the natural hierarchy
present in SMR sensor networks [44]:

Fig. 3. Hierarchical FL with tier-aware aggregation across SMR nodes.

• Core Tier: Includes primary reactor control systems and
critical infrastructure interfaces responsible for safetycritical operations such as reactor power regulation,
coolant flow control, and emergency shutdown systems.
• Edge Tier: Encompasses secondary monitoring components, such as subsystems linked to local diagnostics,
backup monitoring systems, steam generation controls,
and non-critical control loops.
• Peripheral Tier: Represents ancillary facilities, general IT interfaces, communication systems, external
interfaces, and less-trusted subsystems within the administrative building infrastructure.
Each tier is assigned an influence weight based on operational criticality and also can be varied ωtier during model
aggregation, reflecting its relative importance in the framework
hierarchy:


0.5, if tier = core,
ωtier = 0.3, if tier = edge,
(28)


0.2, if tier = peripheral.
2) Tier-Aware Node Selection Strategy: For each FL round,
a minimum number of nodes is selected from each tier to
ensure comprehensive tier representation and maintain the
hierarchical balance essential for SMR operational integrity:
|Stier | ≥ mtier ,

∀tier ∈ {core, edge, peripheral},

(29)

where Stier is the set of selected nodes from the tier and mtier
is the minimum required nodes from each tier.
Additional nodes are selected based on available computational resources and tier weights to optimize the balance
between representation and efficiency:
$
!
%
X
ntier =
Ntarget −
mtier · ωtier ,
(30)
tier

4594

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

where Ntarget denotes the total number of participants intended
for a training round.
3) Two-Level Aggregation Scheme: The model aggregation
process proceeds in two distinct stages to maintain both tierspecific characteristics and global model coherence:
Stage 1: Intra-Tier Aggregation - Within each tier, model
updates are aggregated using trust scores τi and dataset sizes
ni to ensure that more reliable and data-rich nodes have greater
influence within their tier:
P
t+1
i∈Stier τi ni θi
t+1
,
(31)
θtier = P
i∈Stier τi ni
where θit+1 denotes the model parameters submitted by node
i after local training in round t + 1.
Stage 2: Inter-Tier Aggregation - Aggregated tier models
are then combined into the global model based on the fixed
tier weights, ensuring that core systems maintain strategic
influence:
X
t+1
t+1
θglobal
=
ωtier · θtier
.
(32)
tier∈{core,edge,peripheral}

If any tier lacks participants in a given round, its weight is
redistributed proportionally across the remaining active tiers
to maintain aggregation stability:
ωtier
adjusted
.
(33)
ωtier
=P
0
tier0 ∈active tiers ωtier
4) Implementation Details: The hierarchical structure is
realized through a multi-class node registration and routing
system that dynamically allocates clients to tiers based on their
operational roles and security classifications. In each FL round,
the server utilizes both the node’s current trust score and its
tier affiliation to determine participation eligibility, ensuring
that only qualified nodes contribute to model updates.
Aggregation is performed by custom routines that
normalize updates according to Equation (31) and apply
tier weights via Equation (32). This implementation directly
corresponds to the HierarchicalFederatedLearning
class in our codebase, which manages tier assignments, node selection, and hierarchical aggregation
through
the
select_nodes_for_round()
and
aggregate_models() methods.
This tier-aware aggregation scheme offers several advantages for SMR environments. Firstly, it reflects the operational
hierarchy inherent in SMRs by giving more influence to nodes
with higher safety criticality, ensuring that critical reactor
control systems maintain primary decision-making authority.
Secondly, it mitigates the risk posed by compromised or
untrusted nodes in lower tiers, preventing malicious updates
from peripheral systems from affecting the global model.
Finally, it aligns with defense-in-depth principles by embedding institutional trust boundaries directly into the learning
process, creating multiple layers of security that correspond
to the physical security zones within SMR facilities.
The hierarchical FL framework thus provides a foundation
for secure, distributed learning that respects the operational and security requirements of SMR environments while
enabling collaborative DDoS detection across diverse network

components. Building upon this hierarchical structure, the next
subsection details the adaptive trust scoring mechanism that
dynamically evaluates node reliability and guides participation
decisions.
F. Adaptive Multi-Dimensional Trust Scoring
Following the establishment of the hierarchical FL structure,
robust FL in SMR environments demands accurate evaluation of participating nodes, particularly when they differ in
behavior, reliability, or susceptibility to cyber compromise.
The heterogeneous nature of the sensor data comprising core
reactor control systems, edge monitoring components, and
peripheral facility devices data requires a sophisticated trust
assessment mechanism that can dynamically adapt to varying node performance and operational conditions. To capture
this heterogeneity and ensure reliable model aggregation, we
design an adaptive trust scoring mechanism that evaluates
each node based on six orthogonal dimensions. The resulting
trust score τi informs both the selection of nodes and the
aggregation of the model, ensuring that the most trustworthy
nodes exert greater influence on the global model while
mitigating the risks of compromised or unreliable participants.
1) Multi-Dimensional Evaluation Criteria: Each node i in
the SMR federated network is evaluated across the following
six dimensions, selected to capture both technical performance
and operational trustworthiness:
• d1 : Accuracy — Predictive performance of the local
model measured through validation metrics.
• d2 : Data Quality — Integrity and representativeness
of the node’s dataset, including completeness and noise
levels.
• d3 : Timeliness — Responsiveness in submitting local
updates within prescribed federated learning rounds.
• d4 : Consistency — Stability of performance over recent
rounds, indicating operational reliability.
• d5 : Domain Compliance — Adherence to SMR-specific
physical network domain constraints as defined in the
previous subsection.
• d6 : Security Clearance — Node’s baseline trust level
based on tier classification or security access level.
Each dimension d is assigned a weight ωd reflecting its
relative importance in the SMR operational context:

0.25 if d = d1 (accuracy),



0.20 if d = d (data quality),
2
ωd =
(34)
0.15 if d ∈ {d3 , d4 , d5 },



0.10 if d = d6 (security clearance).
The total trust score is computed as a weighted sum across all
dimensions:
6
X
τi =
ωd · si,d ,
(35)
d=1

where si,d denotes the score of node i in dimension d,
normalized to the interval [0, 1].
2) Domain Compliance Scoring: To integrate domain
knowledge into trust estimation and maintain consistency with

RAHAMAN et al.: DOMAIN-INFORMED HIERARCHICAL FL FRAMEWORK FOR DDoS DETECTION

the domain-informed architecture, we incorporate the domain
penalty function defined in Equation (16). For node i with
local dataset Di , the domain compliance score is calculated
as:
1 X
Φ(Px , Bx , Sx ),
(36)
si,d5 =
|Di |
x∈Di

integrity of the global detection model while accommodating the dynamic and heterogeneous nature of SMR sensor
networks, thereby establishing the foundation for secure aggregation and framework integration, as detailed in the following
subsection.
G. Secure Aggregation and System Integration

ensuring that nodes transmitting physically implausible traffic
patterns are penalized, thereby aligning trust assessment with
SMR operational integrity and the domain-informed detection
principles established in the dual-branch architecture.
3) Adaptive Trust Updates: Trust scores are dynamically
updated after each FL round using exponential smoothing to
incorporate recent performance while maintaining historical
context:
t
t
st+1
(37)
i,d = αd · vi,d + (1 − αd ) · si,d ,
t
where vi,d
is the observed metric in round t and αd is a
dimension-specific smoothing factor. For domain compliance,
we apply heavier penalization for severe violations to maintain
safety-critical operational boundaries:
(
t
0.5 if vi,d
< 0.5,
5
αd5 =
(38)
0.3 otherwise.

4) Consistency Evaluation: To capture temporal stability
and identify erratic behavior that can indicate compromised
or unreliable nodes, the consistency score is derived from
the variance of historical performance across accuracy and
data quality dimensions. Given a decay factor γ = 0.9, the
weighted variance is computed as:
Pt
t−j
(sj,i,d0 − µw )2
j=1 γ
0
,
(39)
Varw (s1:t,i,d ) =
Pt
t−j
j=1 γ
where the exponentially weighted mean is:
Pt
t−j
sj,i,d0
j=1 γ
µw =
.
Pt
t−j
j=1 γ

4595

(40)

The consistency score is then calculated as:
P
0
d0 ∈{d1 ,d2 } Varw (s1:t,i,d )
t
si,d4 = 1 − 10 ·
.
(41)
2
This formulation penalizes erratic behavior over time, enabling
the identification of unstable or potentially compromised nodes
that exhibit inconsistent performance patterns.
5) Integration and Export: The trust module maintains a
dynamic trust map across all participating nodes and exports
the scores for use in both the hierarchical aggregation process
and secure audit trails. By coupling data-driven performance
metrics with domain-aware scoring, this mechanism provides
a comprehensive and context-sensitive assessment of trustworthiness specifically tailored for SMR federated environments.
The adaptive nature of this trust scoring function ensures
that nodes demonstrating consistent high performance and
domain compliance receive greater influence in model aggregation, while nodes exhibiting suspicious behavior or poor
performance are appropriately down-weighted or excluded
from critical aggregation rounds. This approach maintains the

Our architectural approach brings together several critical components. We integrate temporal learning capabilities
with physical network domain expertise. Additionally, we
incorporate adaptive trust scoring mechanisms. All of these
elements operate within a privacy-preserving federated framework. This comprehensive integration creates a robust defense
strategy. The strategy specifically targets the unique challenges
found in SMR cyber-physical systems. These systems operate
in mission-critical environments where security cannot be
compromised. Protecting model updates during transmission
presents significant challenges. We address this through secure
aggregation protocols. These protocols must align with strict
SMR regulatory requirements [45]. They also support the
defense-in-depth strategies that nuclear infrastructure protection demands [46]. The model update structure we have
developed serves multiple purposes. Updates flow from clients
to our hierarchical FL server through carefully designed
channels. This structure enables encrypted aggregation while
maintaining tier-specific weighting capabilities. Importantly, it
does this without exposing individual contributions or sensitive
operational data.
The integrated FL workflow proceeds through the following
systematic phases:
Phase 1: Local Model Training and Domain Compliance
Assessment
Each distributed SMR node develops its local dual-branch
DI-LSTM model through training on private datasets. This
process follows the architecture outlined in Subsections III-B
and III-C. The nodes simultaneously compute compliance
penalties for the network domain using Equation (16), which
ensures that the local models naturally adhere to the operating boundaries of the SMR. The domain penalty function
Φ(P, B, S) operates dual roles—it functions as both feature
input and regularization tool. This design steers local models
from physically impossible decisions while preserving their
ability to detect legitimate attack signatures.
Phase 2: Secure Parameter Transmission and Trust
Evaluation
The distributed nodes forward their updated model parame(t+1)
ters θi
to the central aggregator via secure communication
pathways. Along with these parameters, trust metrics travel
through the same channels, including accuracy measurements,
domain compliance scores, and data quality indicators. Participation metadata also accompany this transmission. The server
conducts thorough evaluation of multi-dimensional trust scores
through its adaptive assessment framework. This process utilizes the scheme detailed in Equations (35)–(41). Real-time
performance data merge with historical consistency records
during this evaluation. This integration creates a comprehensive approach to the robust assessment of the reliability of the
nodes.

4596

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Phase 3: Hierarchical Node Selection and Tier-aware
Aggregation
The FL aggregation server selects qualified node subsets
from each operational tier through its tier-aware selection
approach. This strategy ensures balanced representation spans
core, edge, and peripheral systems. Priority goes to nodes
demonstrating higher trust scores along with the best network
domain compliance ratings. The selection framework preserves
SMR’s natural operational hierarchy. Moreover, it blocks
malicious or unreliable nodes from undermining the integrity
of the global model.
Phase 4: Two-Level Model Aggregation
Individual tier models undergo aggregation through trustweighted averaging, following the specifications in Equation
(31). Inter-tier aggregation follows this process, applying fixed
tier weights according to Equation (32). This hierarchical
approach preserves the strategic influence of critical reactor
control nodes within the global model.
Phase 5: Global Model Distribution and Continuous
Adaptation
(t+1)
The aggregated global model θglobal is distributed back to
all participating nodes. Each node replaces its local model
parameters with the updated global parameters before the
next training round begins. The domain-informed constraints
defined in Equation (16) remain enforced during subsequent
local training, and trust scores are carried forward to inform
node selection in the next round. This cycle repeats for T
communication rounds until convergence.
H. Theoretical Convergence Analysis
To provide theoretical analysis for the faster convergence
observed in our framework, we analyze how the hierarchical
tier-weighted aggregation and adaptive trust scoring jointly
reduce the effective variance of the global model updates.
In standard FL with uniform aggregation, the global model
PK (t+1)
1
, where
update at round t is given by θ(t+1) = K
i=1 θi
K is the number of participating clients. Under non-IID data
distributions, the variance of the aggregated update is bounded
by [47]:

E

θ

(t+1)

−θ

∗

2



i

i

i

Since the trust scoring mechanism assigns higher weights τi
to nodes with lower local variance (i.e., more consistent and
accurate clients) and lower weights to unreliable nodes, the
trust-weighted scheme follows:
K

X

wi · σi2 ≤

i

1 X 2
σ ,
K i=1 i

(45)

This inequality holds under the assumption that the adaptive
trust scoring mechanism (Equations (35)–(41)) assigns higher
aggregate scores to nodes exhibiting lower local gradient
variance, which is supported by the inclusion of accuracy
(d1 ) and consistency (d4 ) as dominant trust dimensions with
combined weight ωd1 + ωd4 = 0.40 in Equation (34).
Furthermore, the hierarchical structure contributes to variance reduction by partitioning clients into tiers with distinct
data characteristics. The inter-tier aggregation with fixed
weights ωtier acts as a stratified sampling estimator. By the
law of total variance:
X
2
Var(θDHFL ) =
ωtier
· Varintra (tier) + Varinter (θ̄tier ), (46)
tier

where the first term captures within-tier variance (reduced
by trust weighting) and the second term captures betweentier variance (controlled by the fixed tier weights). When the
tier weights ωtier are chosen proportional to the operational
reliability of each tier, as in our framework where ωcore =
0.5 > ωedge = 0.3 > ωperipheral = 0.2, the inter-tier variance
component is minimized by giving greater influence to the
most stable tier (core), which processes higher-quality data
with lower gradient noise.
By combining these two mechanisms, we obtain the
following convergence bound for our framework after T
communication rounds:
!


X
2
η
(T )
2
2
ωtier
· σ̄tier
+ Γ2DHFL , (47)
E θDHFL − θ∗
≤
T
tier

K

1 X 2
σ + Γ2 ,
≤
K i=1 i

effective weight assigned to client i in our framework. The
variance of the weighted aggregation follows:

 X
X
(t+1)
Var(θDHFL ) =
wi2 · σi2 ≤ max wi ·
wi · σi2 . (44)

(42)

where σi2 denotes the local gradient variance at node i and
Γ2 captures the divergence due to non-IID data heterogeneity
across clients.
In our framework, the global update follows two-level
weighted aggregation. At the intra-tier level, updates are
weighted by trust scores τi (Equation (31)), and at the intertier level, tier weights ωtier are applied (Equation (32)). Our
DHFL aggregation can be expressed as:
P
(t+1)
X
(t+1)
i∈Stier τi θi
P
θDHFL =
ωtier ·
.
(43)
i∈Stier τi
tier

We now show that this formulationPreduces the effective
update variance. Let wi = ωtier(i) · τi / j∈Stier(i) τj denote the

2
where σ̄tier
is the trust-weighted average variance within each
tier and Γ2DHFL represents the residual heterogeneity after
2
≤
hierarchical stratification. Since trust weighting ensures σ̄tier
2
σ̄uniform (Inequality (45)) and hierarchical stratification reduces
Γ2DHFL ≤ Γ2 by grouping nodes with similar operational

profiles, our framework convergence bound in Equation (47)
is strictly tighter than the standard FedAvg bound in Equation
(42). This theoretical result explains the empirical observation
that our framework converges within 30–50 rounds compared
to baseline methods.
IV. P ERFORMANCE E VALUATION
The experimental evaluation is being done in a controlled
cloud-based virtual environment that simulates the distributed
nature of SMR IoT sensor networks. This environment mimics
real-world deployment scenarios with multiple FL clients

RAHAMAN et al.: DOMAIN-INFORMED HIERARCHICAL FL FRAMEWORK FOR DDoS DETECTION

TABLE II
H ARDWARE AND S OFTWARE S PECIFICATION OF THE
S IMULATION E NVIRONMENT

arranged in hierarchical tiers. Each tier represents different
levels of computational power and network limitations, similar
to what is found in actual nuclear facility infrastructures. The
framework supports up to 30 distributed FL clients and allows
flexible configuration of communication rounds, data splits,
and training behaviors. The use of GPUs such as NVIDIA
Tesla T4 or V100 accelerates training, while modern libraries
like TensorFlow, NumPy, and Scikit-learn support DL and
data processing tasks. Flower (flwr) 1.1.0 manages the FL
orchestration, enabling up to 50 communication rounds. The
CICIoT2023 dataset, which includes 2.8 million records, helps
model realistic attack scenarios and normal traffic patterns.
This ensures that the simulation reflects the complexity of realworld SMR networks. Table II summarizes the hardware and
software used in the simulation environment.
A. Dataset Description
We evaluated our DHFL framework using the CICIoT2023
dataset [37], which contains approximately 464 million IoT
network flows and 33 attack types, including DDoS variants
such as HTTP, UDP and TCP floods, as well as Slowloris.
These attacks align closely with the threat scenarios faced by
SMR environments, such as the 2022 Energoatom incident
[6], where nuclear infrastructure was targeted by sophisticated DDoS attacks. Due to the classified nature of real
SMR operational data (as outlined in our problem formulation) and to ensure computational efficiency and balanced
representation across attack types, we strategically sample
2.8 million records from the full CICIoT2023 dataset. This
subset preserves the original class distribution, maintaining
a realistic imbalance of approximately 78% normal traffic
and 22% DDoS attack traffic. CICIoT2023 is a representative
dataset for our study, as its IoT architecture mirrors our
proposed three-tier SMR structure. We retain the non-IID
distribution constraint, where the ratio |DDoS|i /|N ormal|i
varies across tiers, allowing us to evaluate the robustness of our
HierarchicalFederatedLearning class in handling
tier-specific data allocation. Our main objective is to demonstrate the architecture of the framework and the effectiveness
of the hierarchical FL approach using a representative subset
that captures key DDoS attack patterns relevant to SMR
security.
For federated simulation, the dataset is partitioned across
30 nodes according to our hierarchical structure with

4597

non-IID distributions. The core nodes, which represent
critical reactor control systems, receive 40% of high-quality
data to reflect their operational importance, with a tier weight
of ωcore = 0.5. Edge nodes, which simulate secondary monitoring systems, are allocated 35% of moderately variable
data with a weight of ωedge = 0.3. The peripheral nodes,
corresponding to larger facility networks, handle 25% of
higher-noise patterns with ωperipheral = 0.2. This distribution
is implemented in our create_federated_datasets()
function and is enforced through the tier weights defined
in Equation (28). To assess the compliance of each node
with the operational constraints of the SMR, we pre-calculate
the domain compliance scores Φ(P, B, S) using a geometric
mean penalty function. These scores are integrated into our
AdaptiveTrustScorer class, which enables the framework to distinguish between legitimate operational transients
of the reactor (e.g., initialization sequences) and genuine
cyberattacks. This domain-informed detection is supported by
our dual-branch architecture, which processes both temporal
patterns and domain-specific network constraints simultaneously.
B. Implementation Details and Hyperparameters
Our FL simulation implements a hierarchical framework
that mirrors real-world SMR deployment scenarios through
systematic evaluation phases. The simulation orchestrates 30
distributed clients across three operational tiers: 5 core nodes
(representing critical reactor control systems), 10 edge nodes
(secondary monitoring components) and 15 peripheral nodes
(facility networks), conducting up to 50 communication rounds
to ensure convergence stability. Each federated round follows
a structured workflow. It begins with local domain-informed
dual-branch Bi-LSTM training that incorporates network constraints. This is followed by secure parameter transmission
and multi-dimensional trust evaluation across six dimensions:
accuracy, data quality, timeliness, consistency, domain compliance, and security clearance. Hierarchical node selection
is applied to ensure minimum representation of each tier.
The aggregation process includes two levels: trust-weighted
intra-tier averaging, followed by tier-weighted inter-tier combination using fixed weights (ωcore = 0.5, ωedge = 0.3,
ωperipheral = 0.2). The simulation incorporates a non-IID
data distribution, where different tiers experience varying
attack patterns. The core nodes receive 40% of high-quality
data to reflect their operational criticality, the edge nodes
obtain 35% with moderate variability, and the peripheral
nodes handle 25% with higher noise levels. Our adaptive
trust scoring mechanism dynamically evaluates the reliability
of the nodes using exponential smoothing with dimensionspecific weights. Furthermore, domain compliance scoring
integrates the geometric mean penalty function Φ(P, B, S) to
enforce compliance to SMR-specific operational constraints
throughout the FL process.
C. Results and Analysis
Figure 4(a) shows the overall learning progress of the global
model in terms of accuracy and F1- score over 50 communication rounds. The accuracy increases steadily from around 68%

4598

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 4. Performance metrics of various FL parameters for proposed DHFL framework.

in the first few rounds to 93.4% in the final round, showing
a total improvement of approximately 25.4 percentage points.
The F1-score follows a similar trend, reaching a final value
of 95.5%, indicating an excellent precision-recall balance.
This strong convergence behavior confirms that the federated
learning process effectively learns from non-IID data across
all tiers. The absence of major fluctuations shows that the
framework is stable and resistant to low-quality or noisy client
updates. Figure 4(b) shows a clear downward trend in training
loss, following an exponential decay pattern with a slope of
approximately–0.015 per round. Initially, the loss starts above
1.0, but at the end of the simulation, it drops below 0.1,
marking a 90% reduction. This consistent decrease in loss
suggests that the model progressively minimizes its error, even
when aggregating knowledge from heterogeneous clients.
Figure 4(c) shows how many nodes from each tier actively
participate in each communication round. The core nodes
with weight (ω = 0.5) contribute 2 to 4 nodes per round,
the edge nodes (ω = 0.3) contribute 4 to 7 nodes, and
the peripheral nodes (ω = 0.2) contribute 6 to 11 nodes.
Consistent participation from all tiers helps the model learn
from different types of data and system roles, which is important in SMR environments where both core and peripheral
systems matter. The participation distribution also validates
our hierarchical client selection policy, which maintains proportional tier-wise representation in every round. The graph in
Figure 4(d) presents the evolution of the average trust scores
over time, starting at 0.65 and increasing to 0.87 by the final
round, showing an improvement in trust scores of 0.174 or
approximately 26.7% gain. This increase demonstrates the
effectiveness of our adaptive trust evaluation system that monitors six critical dimensions (accuracy, data quality, timeliness,
consistency, domain compliance, and security clearance). Over
time, less reliable or inconsistent clients are excluded or

contribute less to the global model, while high-trust nodes
are favored, resulting in stronger convergence and improved
model robustness.
Figure 4(e) shows two critical metrics: communication
overhead in megabytes (MB) and aggregation time in seconds. Initially, the communication overhead is about 45MB,
which gradually decreases to around 30MB, a 33% reduction
over the course of training. Similarly, the aggregation time
decreases from approximately 8 seconds to 4 seconds, also
indicating a 50% improvement. These results highlight the
benefits of our tier-aware aggregation strategy and selective
client participation, which reduce the communication burden
and make the framework more scalable and practical for realworld SMR deployments. Figure 4(f) show the improvement
in the accuracy of the model in each round. While the
improvement is not uniform across all rounds, the average
per-round improvement is 0.0103, or roughly 1.03% per round.
Some rounds show sharp increases of up to 0.042, while others
offer minimal gains. The variation indicates that certain rounds
contribute significantly more, often when high-trust nodes of
the core or edge tiers are involved.
Figure 5 shows the confusion matrix analysis, which reveals
the steady detection capabilities of the framework. The model
correctly classifies 23,718 normal instances and 67,988 DDoS
attacks, while only 2,309 normal samples are misclassified as
DDoS and 1,690 DDoS samples are misclassified as normal.
This shows a high true positive rate for DDoS detection and a
low false alarm rate. These results confirm our hypothesis that
the integration of SMR-specific domain constraints through
the penalty function Φ(P, B, S) within the hierarchical FL
process significantly improves both the detection accuracy
and the reliability of the framework. By aligning the learning
process with the operational context of nuclear systems, the
framework not only improves classification performance but

RAHAMAN et al.: DOMAIN-INFORMED HIERARCHICAL FL FRAMEWORK FOR DDoS DETECTION

4599

TABLE III
P ERFORMANCE C OMPARISON W ITH E XISTING F EDERATED L EARNING M ETHODS

by enforcing physically plausible behavior. Eliminating the
hierarchical aggregation causes the largest decline in accuracy and overall performance, which highlights its critical
role in handling non-IID data and preserving the influence
of high-importance nodes. In contrast, removing the trust
scoring mechanism results in a moderate degradation across
all metrics, showing that trust-aware client selection improves
robustness by limiting the effect of unreliable updates. Finally,
the full DHFL framework achieves the highest accuracy of
93.4% with an AUC of 0.989, confirming that all three components contribute positively to the overall detection capability.
E. Comparative Analysis With State-of-the-Art Methods

Fig. 5. Confusion matrix of the proposed DHFL framework.

also supports the cybersecurity requirements of critical SMR
infrastructure.
D. Ablation Studies
To evaluate individual contribution of each of our
framework’s components, we conduct a systematic ablation
study by selectively disabling one component at a time
while keeping all other elements unchanged. Specifically,
we evaluate three ablated variants against the full DHFL
configuration: (i) DHFL without (w/o) Physics, which removes
the domain-informed dual-branch architecture and trains a
standard Bi-LSTM without the physics penalty function
Φ(P, B, S); (ii) DHFL w/o Hierarchy, which replaces the tierweighted aggregation with uniform weights and assigns all
nodes to a single tier, effectively reducing the framework to flat
FedAvg; and (iii) DHFL w/o Trust, which fixes all trust scores
at τi = 1.0 and disables the adaptive multi-dimensional trust
update mechanism, treating all participating nodes as equally
reliable. Each variant is trained under identical conditions
using the same CICIoT2023 dataset, 30 federated clients, nonIID data distribution, and 50 communication rounds.
In Table V, we present the detection performance of each
configuration. The ablation results demonstrate the impact
of each component in our DHFL framework. Removing the
physics constraints leads to a drop in precision and AUC,
which indicates that the domain-informed penalty function
Φ(P, B, S) is making an impact for reducing false positives

The experimental evaluation shows that our proposed framework achieves consistently strong results across multiple FL
metrics. As shown in Table III, our framework achieves an
accuracy of 93.4%, precision of 94.5%, recall of 97.5%,
F1-score of 95.5%, and AUC of 98.9%. Compared to the
best-performing baseline method [20], which records 92.3%
accuracy and 92.3% F1-score, our framework shows an overall
improvement of approximately 1 to 3% across key performance metrics such as accuracy, F1-score, and recall. These
gains are especially significant for SMR sensor networks,
where high recall (i.e., minimizing false negatives) is critical to
detect DDoS attacks that could otherwise impact operational
safety.
In terms of communication efficiency, Table IV shows
that our framework reaches convergence within 30 to 50
communication rounds, compared to 60 to 110 rounds required
by other methods, a reduction of up to 55% in training rounds.
This is made possible by our adaptive trust scoring mechanism, which evaluates clients in six dimensions: accuracy,
data quality, timeliness, consistency, domain compliance, and
security clearance, and selects high-trust clients for participation. This approach enables faster convergence, reduces
communication overhead, and supports both privacy and scalability requirements, making it well-suited for deployment in
resource-constrained and mission-critical SMR infrastructures.
Fig. 6 shows a comparison of the convergence speed
between our proposed framework and other existing federated learning methods. The results show that our framework
achieves an accuracy greater than 90% in just 32 communication rounds, which is faster than other approaches such
as UAV-FL (75 rounds), Healthcare FL (55 rounds), NonIID FL (68 rounds) and Agriculture FL (82 rounds). This
translates to a 40% to 60% reduction in training rounds,

4600

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

TABLE IV
F EDERATED L EARNING C OMMUNICATION AND C OMPUTATIONAL E FFICIENCY C OMPARISON

TABLE V
A BLATION S TUDY: C OMPONENT C ONTRIBUTION A NALYSIS (P = P HYSICS C ONSTRAINTS , H = H IERARCHICAL AGGREGATION , T = T RUST S CORING )

CICIoT2023 results, the performance gap is expected because
the two datasets have fundamentally different characteristics in
terms of network topology, attack types, and traffic generation
tools. Additionally, the feature distributions differ substantially
between the two datasets. Although both share flow-based features, their statistical properties vary due to different network
configurations. Despite these differences, all three framework
components, including the hierarchical aggregation, trust scoring, and domain penalty function, operate on this unseen
dataset.
G. Discussion

Fig. 6. Convergence speed comparison with state-of-the-art methods.

depending on the baseline, and highlights the effectiveness of
our trust- and tier-aware aggregation strategy in accelerating
learning. In addition to faster convergence, our framework also
demonstrates enhanced communication efficiency. The total
communication cost is limited to 1,480 MB, reflecting both
the reduced number of rounds and the selective participation
of high-trust nodes. By minimizing redundant or low-quality
updates, the framework ensures that only meaningful contributions are exchanged and aggregated. This not only reduces
bandwidth usage, but also shortens training time, making the
solution more scalable and suitable for resource-constrained
environments. By addressing slow convergence, high communication cost, and lack of domain trust, our framework
provides a practical and efficient solution to secure learning
in nuclear environments.
F. Cross-Dataset Validation: A Case Study With
CIC-DDoS2019
To assess the generalizability of our framework beyond the
primary evaluation dataset, we conduct a cross-dataset validation using the CIC-DDoS2019 dataset [49]. The framework
achieves 87.5% accuracy, 91.7% AUC, and 90.3% F1 score
on CIC-DDoS2019. While these numbers are lower than the

Our experimental results, presented in this section, demonstrate the effectiveness of our framework across multiple
evaluation dimensions. However, we acknowledge several considerations that contextualize these findings.
First, the experimental validation relies on publicly available
IoT datasets rather than real SMR operational data. This is
a practical constraint shared across the nuclear cybersecurity
research community, as actual SMR network traffic data is
classified for national security reasons. No publicly available
dataset currently captures real SMR sensor network communications. Recent SMR cybersecurity studies face the same
limitation: Salehpour et al. [13] used RTDS simulation without
domain-informed or federated learning components, and Ayodeji et al. [30] relied on the Asherah Nuclear Simulator without
privacy-preserving mechanisms. We selected CICIoT2023 as
our primary dataset because its hierarchical IoT architecture
closely mirrors our proposed three-tier SMR structure, and
it contains DDoS attack variants that align with real-world
nuclear infrastructure threats such as the 2022 Energoatom
incident [6]. The cross-dataset validation with CIC-DDoS2019
dataset further confirms that our framework is not tailored to
a single benchmark.
Second, the primary contribution of our work is the framework architecture itself. The generalized domain compliance
framework introduced in Subsection III-D is designed so that
domain expert can instantiate it by specifying operational
bounds for their specific system. The theoretical convergence analysis (Subsection III-H) and the ablation study

RAHAMAN et al.: DOMAIN-INFORMED HIERARCHICAL FL FRAMEWORK FOR DDoS DETECTION

(Subsection IV-D) validate the design choices independently
of any particular dataset. This positions our framework as a
reusable and adaptable solution for federated DDoS detection
in hierarchical sensor networks across different critical infrastructure domains.
Third, future work will focus on two key directions:
(i) deploying the framework in a simulated SMR testbed to
assess practical scalability and regulatory compliance, and
(ii) expanding the detection scope beyond DDoS attacks to
encompass more sophisticated cyber threats.
V. C ONCLUSION
This paper presented a Domain-informed Hierarchical Federated Learning (DHFL) framework for detecting DDoS
attacks in SMR IoT sensor networks. The framework
integrated a dual-branch Bi-LSTM architecture with networkspecific domain constraints and a multi-dimensional adaptive
trust mechanism, enabling accurate and privacy-preserving
collaborative learning across core, edge, and peripheral
tiers. Through tier-weighted aggregation and domain penalty
enforcement, the framework maintained SMR operational
integrity while improving detection accuracy. The experimental evaluation demonstrated robust performance with 93.4%
accuracy, 97.5% recall, and 98.9% AUC, along with faster
convergence and lower communication overhead compared to
existing methods. These results suggest the suitability of the
framework for deployment in safety-critical IoT environments
where privacy, reliability, and system-specific compliance are
essential. Future work will focus on expanding the framework beyond DDoS attacks to encompass sophisticated cyber
threats, such as false data injection and persistent threats,
and deploying the framework in a simulated testbed to assess
practical scalability and regulatory compliance.
R EFERENCES
[1]

[2]
[3]
[4]

[5]
[6]

[7]

[8]
[9]

H. F. Rashvand, A. Abedi, J. M. Alcaraz-Calero, P. D. Mitchell,
and S. C. Mukhopadhyay, “Wireless sensor systems for space and
extreme environments: A review,” IEEE Sensors J., vol. 14, no. 11,
pp. 3955–3970, Nov. 2014.
P. Suriyachai, U. Roedig, and A. Scott, “A survey of MAC protocols
for mission-critical applications in wireless sensor networks,” IEEE
Commun. Surveys Tuts., vol. 14, no. 2, pp. 240–264, 2nd Quart., 2012.
C. Jendoubi and A. Asad, “A survey of artificial intelligence applications
in nuclear power plants,” IoT, vol. 5, no. 4, pp. 666–691, Oct. 2024.
A. Ayodeji, M. Mohamed, L. Li, A. D. Buono, I. Pierce, and H. Ahmed,
“Cyber security in the nuclear industry: A closer look at digital control
systems, networks and human factors,” Prog. Nucl. Energy, vol. 161,
Jul. 2023, Art. no. 104738.
A. B. de Neira, B. Kantarci, and M. Nogueira, “Distributed denial of
service attack prediction: Challenges, open issues and opportunities,”
Comput. Netw., vol. 222, Feb. 2023, Art. no. 109553.
T. Record. (2023). Ukraine’s State-Owned Nuclear Power Operator
Said Russian Hackers Attacked Website. [Online]. Available:
https://therecord.media/ukraines-state- owned-nuclear-power-operatorsaid-russian-hackers-attacked-website
C. Hub. (2023). Sellafield Nuclear Site Attacked by Cyber Groups Linked
to Russia and China. [Online]. Available: https://www.cshub.com/
attacks/news/sellafield- nuclear-site-attacked-by-cyber-groups-linked-torussia-and-china
T. C. Express. (2023). Garnesia Team Claims Npcil Cyberattack.
[Online]. Available: https://thecyberexpress.com/npcil-cyberattack-bygarnesia-team/
A. Greenberg. (2019). The Wired Guide to Cyberwar. [Online]. Available: https://www.wired.com/story/cyberwar-guide/

4601

[10] M. P. Arthur, G. Ramachandran, K. Sood, P. Kaarthik, S. Sridhar, and
M. Chowdhury, “Empirical study of hierarchical intrusion detection
systems for unknown attacks,” IEEE Trans. Netw. Service Manage.,
vol. 22, no. 6, pp. 5564–5581, Dec. 2025.
[11] M. L. Ali, K. Thakur, S. Schmeelk, J. Debello, and D. Dragos,
“Deep learning vs. machine learning for intrusion detection in computer
networks: A comparative study,” Appl. Sci., vol. 15, no. 4, p. 1903, Feb.
2025.
[12] M. Mendoza and P. V. Tsvetkov, “An intelligent fault detection and
diagnosis monitoring system for reactor operational resilience: Unknown
fault detection,” Prog. Nucl. Energy, vol. 171, Jun. 2024, Art. no.
105167.
[13] A. Salehpour and I. Al-Anbagi, “Digital substations: Cyberattack detection system for small modular reactor-based power plants.,” IEEE
Electrific. Mag., vol. 12, no. 4, pp. 57–67, Dec. 2024.
[14] G. Wu, Y. Wang, and Z. Wu, “Physics-informed machine learning
in cyber-attack detection and resilient control of chemical processes,”
Chem. Eng. Res. Des., vol. 204, pp. 544–555, Apr. 2024.
[15] A. Zainudin, L. A. C. Ahakonye, R. Akter, D.-S. Kim, and J.-M. Lee,
“An efficient hybrid-DNN for DDoS detection and classification in
software-defined IIoT networks,” IEEE Internet Things J., vol. 10,
no. 10, pp. 8491–8504, May 2023.
[16] S. Mohammadi, A. Balador, S. Sinaei, and F. Flammini, “Balancing
privacy and performance in federated learning: A systematic literature
review on methods and metrics,” J. Parallel Distrib. Comput., vol. 192,
Oct. 2024, Art. no. 104918.
[17] S. Wang, S. Hosseinalipour, M. Gorlatova, C. G. Brinton, and M. Chiang, “UAV-assisted online machine learning over multi-tiered networks:
A hierarchical nested personalized federated learning approach,” IEEE
Trans. Netw. Service Manage., vol. 20, no. 2, pp. 1847–1865, Jun. 2023.
[18] A. Zainudin, R. Akter, D.-S. Kim, and J.-M. Lee, “Federated learning
inspired low-complexity intrusion detection and classification technique
for SDN-based industrial CPS,” IEEE Trans. Netw. Service Manage.,
vol. 20, no. 3, pp. 2442–2459, Sep. 2023.
[19] T. Wang, X. Huang, Y. Wu, L. Qian, B. Lin, and Z. Su, “UAV swarmassisted two-tier hierarchical federated learning,” IEEE Trans. Netw. Sci.
Eng., vol. 11, no. 1, pp. 943–956, Jan. 2024.
[20] S. Iqbal et al., “Hierarchical continual learning for domain-knowledge
retention in healthcare federated learning,” IEEE Trans. Consum. Electron., vol. 71, no. 2, pp. 5025–5035, May 2025.
[21] Z. Ullah et al., “Hybrid CNN-LSTM model for DDoS attack detection in
Internet of Things-based healthcare Industry 5.0,” IEEE Internet Things
J., vol. 12, no. 22, pp. 46075–46082, Nov. 2025.
[22] J. Bhayo, R. Jafaq, A. Ahmed, S. Hameed, and S. A. Shah, “A timeefficient approach toward DDoS attack detection in IoT network using
SDN,” IEEE Internet Things J., vol. 9, no. 5, pp. 3612–3630, Mar. 2022.
[23] G. Wu, H. Zhang, W. Wu, Y. Wang, and Z. Wu, “Physics-informed graph
convolutional recurrent network for cyber-attack detection in chemical
process networks,” Ind. Eng. Chem. Res., vol. 64, no. 6, pp. 3370–3382,
Feb. 2025.
[24] Kamaldeep, M. Malik, and M. Dutta, “Feature engineering and machine
learning framework for DDoS attack detection in the standardized Internet of Things,” IEEE Internet Things J., vol. 10, no. 10, pp. 8658–8669,
May 2023.
[25] S. D. Vyas, S. Kumar Padisala, and S. Dey, “A physics-informed neural
network approach towards cyber attack detection in vehicle platoons,”
in Proc. Amer. Control Conf. (ACC), May 2023, pp. 4537–4542.
[26] G. B. Gaggero, P. Girdinio, and M. Marchese, “Artificial intelligence
and physics-based anomaly detection in the smart grid: A survey,” IEEE
Access, vol. 13, pp. 23597–23606, 2025.
[27] L. Lei, Y. He, Z. Xing, Z. Li, and Y. Zhou, “Physics-informed LSTMbased time-series forecasting model for power transformers,” IEEE
Trans. Ind. Informat., vol. 21, no. 7, pp. 5411–5419, Jul. 2025.
[28] X. Wu, P. Li, Y. Gu, J. Tao, S. Shen, and S. Yu, “Improved
Gale–Shapley-based hierarchical federated learning for IoT scenarios,”
IEEE Internet Things J., vol. 12, no. 7, pp. 9195–9205, Apr. 2025.
[29] H. Devaraj et al., “RuralAI in tomato farming: Integrated sensor system,
distributed computing, and hierarchical federated learning for crop health
monitoring,” IEEE Sensors Lett., vol. 8, no. 5, pp. 1–4, May 2024.
[30] A. Ayodeji, A. Di Buono, I. Pierce, and H. Ahmed, “Wavy-attention
network for real-time cyber-attack detection in a small modular pressurized water reactor digital control system,” Nucl. Eng. Design, vol. 424,
Aug. 2024, Art. no. 113277.
[31] R. Rockabrand, “How artificial intelligence will power emergency preparedness and response for small modular reactors,” Ph.D. dissertation,
Dept. Artif. Intell., Capitol Technol. Univ., Laurel, MD, USA, 2025.

4602

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

[32] K. Nam, K. Kwon, and A. Kim, “HINT-sec: Hardware-in-the-loop
nuclear power plant testbed for cyber security,” Prog. Nucl. Energy,
vol. 180, Feb. 2025, Art. no. 105600.
[33] B. Zhang, S. Wang, S. Cheng, J. Sun, M. Peng, and C. Wang, “Transient
trend prediction of safety parameters for small modular reactor considering equipment degradation,” Ann. Nucl. Energy, vol. 181, Feb. 2023,
Art. no. 109507.
[34] International Atomic Energy Agency. (2024). Small Modular
Reactors: Advances in SMR Developments 2024. Vienna, Non-Serial
Publications. [Online]. Available: https://aris.iaea.org/Publications/
SMR catalogue 2024.pdf
[35] World Nuclear Association. (2024). Small Nuclear Power
Reactors.
Accessed:
Jun.
2,
2025.
[Online].
Available:
https://world-nuclear.org/information-library/nuclear-fuel-cycle/nuclearpower-reactors/small-nuclear-power-reactors
[36] International Atomic Energy Agency, Technology Roadmap for Small
Modular Reactor Deployment, document NR-T-1.18, IAEA Nuclear
Energy Series, IAEA. Vienna, Austria, 2021. [Online]. Available: https://
www-pub.iaea.org/MTCD/Publications/PDF/PUB1944 web.pdf
[37] E. C. P. Neto, S. Dadkhah, R. Ferreira, A. Zohourian, R. Lu, and
A. A. Ghorbani, “CICIoT2023: A real-time dataset and benchmark
for large-scale attacks in IoT environment,” Sensors, vol. 23, no. 13,
p. 5941, Jun. 2023.
[38] U.S. Nuclear Regulatory Commission. (2025). Digital Instrumentation
and Controls Research. Accessed: May 18, 2025. [Online]. Available:
https://www.nrc.gov/about-nrc/regulatory/research/digital.html
[39] International Atomic Energy Agency. (Dec. 2021). Small Modular
Reactors: Design Features, Safety Approaches and Research Programs.
International Atomic Energy Agency (IAEA). Accessed: May 18,
2025. [Online]. Available: https://www.iaea.org/sites/default/files/19/12/
smr rf dsa interim report.pdf
[40] NuScale Power. (2025). Design Documents. Accessed: May 18, 2025.
[Online]. Available: https://www.nuscalepower.com/technology/designdocuments
[41] Standards Council of Canada. (2025). Cybersecurity Standard CSA
t100. Accessed: May 18, 2025. [Online]. Available: https://scc-ccn.ca/
standardsdb/standards/2030549
[42] I. Al-Anbagi, M. Erol-Kantarci, and H. T. Mouftah, “Delayaware medium access schemes for WSN-based partial discharge
measurement,” IEEE Trans. Instrum. Meas., vol. 63, no. 12,
pp. 3045–3057, Dec. 2014.
[43] S. Boyd and L. Vandenberghe, Convex Optimization. Cambridge, U.K.:
Cambridge Univ. Press, 2004.
[44] A. Polanco and M. E. J. Newman, “Hierarchical core-periphery structure
in networks,” Phys. Rev. E, Stat. Phys. Plasmas Fluids Relat. Interdiscip.
Top., vol. 108, no. 2, Aug. 2023, Art. no. 024311.
[45] Canadian Nuclear Safety Commission. (2025). Dis-16-04: Small
Modular Reactors-Regulatory Strategy, Approaches and Challenges.
Canadian Nuclear Safety Commission, Discussion Paper DIS16-04. [Online]. Available: https://www.cnsc-ccsn.gc.ca/eng/acts-andregulations/consultation/comment/d-16-04/
[46] North American Electric Reliability Corporation (NERC). (Feb.
2022).
Provincial
Summary-Saskatchewan.
PDF
Document.
[Online]. Available: https://www.nerc.com/AboutNERC/keyplayers/
ProvincialSummaries/Saskatchewan.pdf
[47] T. Li, A. K. Sahu, A. Talwalkar, and V. Smith, “Federated learning:
Challenges, methods, and future directions,” IEEE Signal Process. Mag.,
vol. 37, no. 3, pp. 50–60, May 2020.
[48] H. Liu, Y. Ma, C. Guo, X. Liu, and T. Wang, “MOHFL: Multi-level oneshot hierarchical federated learning with enhanced model aggregation
over non-IID data,” IEEE Trans. Netw. Service Manage., vol. 22, no. 3,
pp. 2853–2865, Jun. 2025.
[49] I. Sharafaldin, A. H. Lashkari, S. Hakak, and A. A. Ghorbani,
“Developing realistic distributed denial of service (DDoS) attack dataset
and taxonomy,” in Proc. Int. Carnahan Conf. Secur. Technol. (ICCST),
Oct. 2019, pp. 1–8.

Md Facklasur Rahaman received the B.Sc.
degree in electrical and electronic engineering from
Rajshahi University of Engineering and Technology,
Bangladesh, in 2016, and the Master of Engineering degree in IT convergence engineering from the
Kumoh National Institute of Technology, Gumi,
South Korea, in 2025. He is currently pursuing
the Ph.D. degree in electronic systems engineering
with the University of Regina, Canada. His research
interests include federated learning, blockchain,
metaverse, the Internet of Things, and large language
models.

Makhduma F. Saiyed (Member, IEEE) received
the Ph.D. degree in electronic systems engineering from the University of Regina, Regina, SK,
Canada, in 2025. She was a Post-Doctoral Fellow
with the University of Regina from March 2025 to
June 2025. Currently, she is an Assistant Professor
with the Department of Computer Science, Trent
University, Oshawa, ON, Canada. She is also a
registered Engineer-in-Training (EIT) with the Association of Professional Engineers and Geoscientists
of Saskatchewan (APEGS), Regina. She has over ten
years of teaching experience and has published numerous research articles.
Her current research interests include network security, the Internet of Things
(IoT), machine learning, deep neural networks, game theory, explainable AI,
and large language models.

Irfan Al-Anbagi (Senior Member, IEEE) received
the Ph.D. degree in electrical and computer engineering from the University of Ottawa in October 2013.
From 2013 to 2015, he was a Post-Doctoral Fellow
and the Product Development Manager of the SecCharge Project with the University of Ottawa. He is
currently a Professor with the Faculty of Engineering
and Applied Science, University of Regina, and an
Adjunct Professor with the Department of Electrical
and Computer Engineering, College of Engineering,
University of Saskatchewan. He is also registered as
a Professional Engineer with the Association of Professional Engineers and
Geoscientists of Saskatchewan (APEGS) and a Professional Engineers Ontario
(PEO). His research interests include security and reliability in cyber-physical
systems, the Internet of Things (IoT) systems, and edge computing.

Ramakrishna Gokaraju (Senior Member, IEEE)
received the B.E. degree (Hons.) in electrical and
electronics engineering from the National Institute of
Technology, Tiruchirappalli, India, in 1992, and the
M.Sc. and Ph.D. degrees in electrical and computer
engineering from the University of Calgary, Canada,
in 1996 and 2000, respectively. He was a Research
Scientist with Alberta Research Council and a Staff
Software Engineer with the IBM Toronto Laboratory. Since 2003, he has been with the University
of Saskatchewan, where he is currently a Professor
and a Graduate Chair with the Department of Electrical and Computer
Engineering. His research interests include power system protection and
control and nuclear modeling of small modular reactors (SMRs). His research
was funded by the NSERC Discovery Grant and the NSERC-Canada Nuclear
Safety Commission (CNSC) Small Modular Reactor Research Grant.
PAPER_TEXT
