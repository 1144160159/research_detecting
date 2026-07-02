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
# [802] Securing Vehicular Ad Hoc Networks via Digital Twin-Driven Anomaly Detection and Graph Reinforcement Learning
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
编号：802
题名：Securing Vehicular Ad Hoc Networks via Digital Twin-Driven Anomaly Detection and Graph Reinforcement Learning
年份：2026
DOI：10.1109/tvt.2026.3688587
来源：IEEE Transactions on Vehicular Technology
PDF：paper/10.1109_TVT.2026.3688587.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、图学习、知识图谱与威胁情报
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\802.txt
- 原始字符数：80438
- 本次发送字符数：80438
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

1

Securing Vehicular Ad Hoc Networks via Digital Twin-Driven
Anomaly Detection and Graph Reinforcement Learning
Latifa El Bouga, Amine Andam, Jamal Bentahar, El Mehdi Amhoud, Mustapha Hedabou

Abstract—Vehicular Ad Hoc Networks (VANETs) support
critical safety and coordination functions in Intelligent Transportation Systems by enabling vehicles to exchange real-time
information. Applications like collision avoidance, cooperative
awareness, and traffic optimization depend on reliable Vehicleto-Vehicle (V2V) communication. However, VANETs remain
vulnerable to security threats such as blackhole attacks, message
falsification, and data injection due to their dynamic topology
and limited interaction durations. While machine learning-based
approaches have been applied to anomaly detection in VANETs,
most rely on static features or vehicle-level trust, and lack
post-detection control strategies. This paper proposes a realtime VANET security framework implemented within a Digital
Twin (DT) environment that mirrors the network operation. The
framework integrates time-series-based anomaly detection with
post-detection mitigation using Graph Reinforcement Learning
(GRL). A transfer-learned temporal model, pre-trained on large
public data and fine-tuned on simulation outputs, classifies
V2V messages based on dynamic behavioral patterns. While
a GRL agent observes the evolving communication graph and
learns to prune or preserve links to reduce the impact of
malicious or misclassified messages. Unlike existing approaches,
the system directly addresses false positives and false negatives by
learning corrective control policies over time. We implement this
framework using OMNeT++, SUMO, and Veins, and evaluate its
performance across several road topologies and attack scenarios.
Results show improved resilience and reliability compared to
detection-only baselines. An ablation study further highlights
the value of GRL in enhancing system performance under
challenging conditions, achieving a 3.2% improvement in F1score over a state-of-the-art anomaly detection baseline.
Index Terms—Vehicular Ad Hoc Networks (VANETs), anomaly
detection, Digital Twin, time-series analysis, Graph Reinforcement Learning, post-detection mitigation.

I. I NTRODUCTION
Vehicular Ad Hoc Networks (VANETs) [1] form a critical component of modern Intelligent Transportation Systems
(ITS), enabling real-time exchange of safety and traffic information between vehicles and infrastructure [2]. Applications
such as collision avoidance, cooperative lane change, and
traffic control rely heavily on accurate and timely Vehicleto-Vehicle (V2V) and Vehicle-to-Infrastructure (V2I) communication [3]. However, the open and decentralized nature
of VANETs, characterized by open wireless channels, high
node mobility, and the absence of centralized control, makes
Latifa El Bouga, Amine Andam, El Mehdi Amhoud, and Mustapha
Hedabou are with Mohammed VI Polytechnic University, Benguerir,
Morocco. E-mails: {latifa.elbouga, amine.andam, elmehdi.amhoud,
mustapha.hedabou}@um6p.ma
Jamal Bentahar is with Khalifa University, 6G Research Center, Abu
Dhabi, UAE, and Concordia University, Montreal, Canada. E-mail: jamal.bentahar@ku.ac.ae

them vulnerable to a range of security threats [4], including
blackhole attacks, denial-of-service (DoS), Sybil attacks, and
false data injection [5], [6].
Ensuring secure message exchange in VANETs is particularly challenging due to their dynamic topology, frequent
node mobility, and the absence of persistent trust relationships.
Traditional cryptographic techniques and static rule-based
models are often insufficient in these environments [7]. As
a result, learning-based methods, especially those leveraging
machine learning (ML) and deep learning (DL), have been
widely studied to detect misbehavior in VANETs [8]. Recent
work has also explored ensemble learning approaches for
fault detection in VANETs [9], primarily targeting general
vehicular faults rather than real-time message-level anomaly
handling. However, most existing approaches operate solely
at the detection level, using static features or without any
mechanism to respond to misclassified or malicious messages
during operation. Moreover, many systems assess vehicle-level
trustworthiness based on behavioral history (entity-oriented),
which can be unreliable in high-mobility environments where
interactions are brief and inconsistent [10].
To address this, recent studies have explored data-oriented
anomaly detection methods that analyze the real-time content
of each V2V message, independent of vehicle history. In
particular, time-series models such as LSTMs [11], Transformers [12], and CNN-based architectures have shown success
in learning dynamic communication patterns and detecting
anomalous message flows [13]. However, these systems typically operate as passive detectors, flagging anomalous messages but providing no mechanism to control their spread or
influence on the network.
In parallel, graph-based learning methods, such as Graph
Neural Networks (GNNs) and Reinforcement Learning (RL),
have gained attention for modeling the structure and evolution
of vehicular networks [14], [15]. These techniques allow the
system to reason over communication topology, identify structural vulnerabilities, and even guide decisions about message
forwarding and routing [16], [17]. Yet, most graph-based
systems operate on static graph snapshots, focus exclusively
on node-level or routing-level inference, and are rarely coupled
with real-time anomaly detection systems [13].
This paper addresses these limitations by introducing a Digital Twin (DT)-based VANET security framework that operates
in real time. The proposed system mirrors the VANET simulation environment and integrates time-series-based message
classification with graph-level post-detection mitigation. A
fine-tuned state-of-the-art temporal model performs messagelevel anomaly detection, while a Graph Reinforcement Learning (GRL) agent processes the evolving communication graph

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

2

to selectively prune or preserve links. This approach not only
mitigates the propagation of malicious data, but also helps
correct false positives and false negatives, increasing overall
decision reliability. The main contributions of our work are
summarized as follows:
• We propose a real-time DT framework for VANET security that unifies anomaly detection and post-detection
mitigation in a closed-loop simulation.
• We propose a two-stage training strategy that first trains
time-series models on a large-scale public dataset, then
fine-tunes them on a smaller, domain-shifted simulation
dataset. This approach balances generalization and resource efficiency, enabling real-time classification without
requiring massive amounts of simulation data.
• We design a GRL based mitigation strategy that learns
to prune or preserve communication links in the message
graph, helping correct false positives and false negatives
in classification.
• We conducted a thorough ablation study to assess the
impact of GRL on system performance and robustness,
quantifying its added value over standalone classification.
• We evaluated the full framework using realistic VANET
simulation tools (OMNeT++, SUMO, Veins) across multiple attack types and traffic topologies.
The remainder of this paper is organized as follows. Section
II presents a review of related work on anomaly detection,
graph-based learning, and reinforcement learning in VANET
security. Section III introduces the proposed framework, including the DT architecture, the anomaly detection module,
and the GRL-based control layer. Section IV details the training methodology, covers the datasets, and the model training
procedures. Section V describes the experimental setup, test
datasets, attack scenarios, evaluation results, and the ablation
study. Finally, Section VI discusses limitations and outlines
directions for future work, followed by the conclusion in
Section VII.
II. R ELATED W ORK
Security and anomaly detection in VANETs have been
widely studied using ML, DL, GNNs, and RL. Prior
works generally fall into four main categories: ML/DL-based
anomaly detection, GNN-based modeling, RL-based adaptation, and frameworks that combine detection with postdetection control. One key modeling difference lies in whether
a system analyzes vehicles as entities (evaluating their longterm behavior) or evaluates messages individually based on
their real-time content. The latter, known as data-oriented
detection, is often better suited for VANETs, where vehicles
frequently join and leave the network and may not retain a
persistent history.
A. Anomaly Detection in VANETs Using Machine and Deep
Learning
Entity-oriented detection is still common in routing-focused
security systems. Hassan et al. [18] proposed an artificial neural network that is trained to identify blackhole attacks based
on vehicle behavior, which is then used to support enhanced

routing. Although effective in improving routing security, the
model relies on historical data on node trustworthiness and
does not support message-level or real-time adaptation.
Canh et al. [19] used features generated from NS-3 simulations [20] and applied classifiers such as Gradient Boosting to
detect malicious nodes. Similarly, El-Shafai et al. [21] applied
a combination of Random Forest, Extra Trees, and CNN to
physical layer metrics such as Received Signal Strength (RSS)
and Bit Error Rate (BER). While both systems achieve strong
performance, they are limited by not providing post-detection
mitigation.
A more data-oriented method is proposed by Alladi et al.
[22]. This model uses a CNN-LSTM architecture to learn
patterns in communication flows and detect a variety of attack
types without requiring labeled data. Although the system
analyzes message content and generalizes well, it does not
integrate mitigation or support structural changes to communication patterns during operation.
While many anomaly detection methods in VANETs rely
on static features extracted from individual messages, similar
machine learning-based intrusion detection approaches have
also been explored in broader networked and IoT environments
[23], highlighting shared challenges related to scalability and
real-time adaptation. However, such models often overlook
how vehicle behavior unfolds over time. In a dynamic and
fast-changing environment like VANETs, threats may manifest
as subtle temporal inconsistencies, such as gradually drifting
positions or fluctuating speeds that static classifiers fail to
detect. Time-series models, on the other hand, are designed to
capture sequential patterns and temporal dependencies, making
them more effective in identifying evolving attack behavior.
Prior work in sequential anomaly detection has shown that
such models can outperform traditional approaches [22], [24].
Building on this insight, our framework incorporates finetuned temporal models to perform real-time message-level
classification. These outputs are then used to inform postdetection mitigation within a DT, enabling both accurate
detection and adaptive response.
B. Graph-Based Learning in VANET Security
Graph-based methods have emerged to model relationships
between vehicles and communication patterns. Ramkumar
et al. [13] use a semantic-aware GNN to detect malicious
vehicles by modeling node and edge relationships. However,
the approach relies on static graph snapshots and performs
only node-level classification, without responding to detected
anomalies at the link or message level. In a more comprehensive setup, Hidalgo et al. [14] proposed the SerIoT platform,
which combines GNN-based detection with Software Defined
Network (SDN) and RL for flow control and rerouting. While
promising, the platform is heavy on infrastructure and depends
on SDN controllers and fog nodes.
C. Reinforcement Learning in VANET Security
RL has been explored to enable adaptive trust and routing
decisions in VANETs. Guo et al. [25] presented a Q-learning
agent that dynamically adjusts the weighting between internal

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

3

sensor data and external V2V messages when evaluating
incoming information. The model is data-oriented, as it assesses each message in its situational context (e.g., event type,
location, entropy), rather than relying on historical vehicle
behavior. However, it does not model the communication
structure as a graph and lacks the ability to enforce structural
mitigation, such as pruning or blocking message links.
Sedar et al. [26] proposed a DRL-based system in which
RSUs share knowledge across domains to detect misbehavior
under unseen conditions. While this enables generalization, the
approach focuses on node-level detection without supporting
real-time message-level control, or structural adaptation of the
communication graph.
D. Beyond Detection: Learning-Based Detection and PostDetection Response
Some frameworks extend anomaly detection by combining
time-series modeling with RL. He et al. [27] presented a timeseries anomaly detector for traffic flow data using LSTM to
encode temporal patterns and a DQN [28] agent to classify
data points as normal or anomalous. In this case, RL is used
directly for detection decisions, not for post-detection mitigation, and the system is not designed for VANET environments,
unlike our framework, which uses RL for real-time mitigation
in a VANET setting.
Golchin et al. [29] proposed a time-series anomaly detection
framework that combines LSTM-based modeling with RL and
variational autoencoders (VAE). The RL agent learns to detect
anomalies by balancing rewards from limited labeled data and
unsupervised VAE signals. While this enhances detection, the
system is not applied to VANETs and does not perform postdetection control or communication-level decision-making,
capabilities that are explicitly addressed in our work.
Other studies apply RL within closed-loop frameworks that
include control or response mechanisms. Jayakrishna et al.
[30] proposed a VANET security system that detects DDoS
attacks using DL and applies RL to adjust the network rate
limits. Their control is applied at the infrastructure level
(e.g., RSUs), which may impact both malicious and legitimate
traffic. The method also focuses only on DDoS attacks and
does not address more general forms of message falsification,
unlike our system, which operates at the message level and
targets a broader range of attacks.
Zhang et al. [31] proposed an autonomous driving system that uses LSTM to predict surrounding vehicle behavior
and RL to make lane-change and car-following decisions.
Although this combines time-series forecasting and decisionmaking, it is designed for motion control in autonomous
vehicles rather than VANET security or communication-level
response.
While these works combine time-series models and RL in
useful ways, none of them supports message-level mitigation
or uses RL to make post-detection decisions within a VANET
communication context, as addressed in our framework.
E. Privacy and Authentication in VANETs
In parallel to detection and mitigation, several works have
addressed privacy-preserving communication and secure authentication in VANETs. Tan et al. [32] proposed a blockchainassisted conditional anonymous authentication protocol with
adaptive group key agreement. Their system ensures identity
privacy, revocation, and secure cross-domain communication
using smart contracts and tree-based key structures. Similarly,
Ismail et al. [33] introduced a biometric-enhanced anonymous key agreement scheme that leverages smart cards, fuzzy
extractors, and elliptic curve cryptography to provide finegrained access control and conditional traceability. While our
framework focuses on detection and mitigation rather than
communication-layer privacy or authentication, it is compatible with existing privacy-preserving protocols and can be
extended to operate alongside them in future deployments.
In contrast, our work presents a complete, time-series-driven
security framework that spans the entire security pipeline,
from message generation and anomaly detection to postdetection control. The system is implemented within a DT
that mirrors the VANET simulation in real time, enabling synchronized classification and mitigation. It performs messagelevel anomaly detection using a temporal DL model and
applies GRL to dynamically prune or preserve links in the
communication graph. The GRL agent learns from previous
predictions and local graph context, helping to reduce false
positives and false negatives while maintaining communication
integrity. Together, these components form a unified real-time
system for detection and mitigation in VANETs.
III. P ROPOSED M ETHODOLOGY
A. Overview of the Proposed Approach
This work introduces a real-time DT framework designed
to enhance VANET security through integrated detection and
mitigation of malicious V2V communications. The DT mirrors the behavior of a simulated VANET by continuously
receiving live vehicle state data and performing real-time
analysis through two core modules (see Figure 1): a timeseries anomaly detection module and a GRL agent module
for post-detection control.
The VANET environment is emulated using SUMO (Simulation of Urban MObility) [34] for mobility modeling and
OMNeT++ (Objective Modular Network Testbed in C++) [35]
with Veins (Vehicles in Network Simulation) [36] for wireless communication. Vehicles periodically exchange structured
V2V messages that contain movement-related attributes such
as position, speed, acceleration, and heading. These messages
are streamed in real time to the DT back-end, enabling
synchronized monitoring and decision-making.
Within the DT, the first module uses a fine-tuned time-series
classification model to analyze sequences of recent vehicle
states and classify each message as normal or anomalous.
These predictions are then fused with vehicle metadata to construct a dynamic VANET communication graph, where nodes
represent vehicles, and edges represent active V2V communication links. The node features include physical movement
data and binary anomaly labels from the classification model.
The second module of the DT applies GRL to this constructed graph. The problem is formulated as a Markov
Decision Process (MDP), where the agent observes the graph

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

4

2. Anomaly Detection Model

1. VANET Simulation Environment

Encoder
Vehicle Time
Series Data

Decoder
Masked
Prob Sparse Self-Attention

Feed Forward

input
Embedding

Full Attention
Layer

LayerNorm
LayerNorm
Normal V2V
Malicious V2V

Prob Sparse SelfAttention

Feed Forward

Classification Head

Action
Maintain / Prune

Anomalies
0/1

3. Graph Reinforcement Learning
PPO Agent

GNN

GNN Features

Graph Construction

Input Layer

Policy Network

Value Network

Linear Layers
Linear Layers

Linear Layers
Linear Layers

Action Probabilities

State Value

Residual Block
Residual Block
Attention block

Branch 1:
Linear + Norm

Branch 2:
Linear + Norm

PPO Loss Optimization
Feature Layer

Fig. 1. Overview of the proposed VANET security framework. The system operates as a simulation-driven Digital Twin that integrates time-series anomaly
detection model and Graph Reinforcement Learning for real-time classification and mitigation of malicious V2V messages.

at each time step and decides, for each communication link,
whether it should be maintained or pruned. A GNN extracts
latent node features, which are processed by a Proximal Policy
Optimization (PPO) [37] policy to generate edge-level actions.
The reward function is designed to balance detection precision,
ensuring that the agent suppresses malicious communication
links while minimizing disruption to normal traffic flow.
Figure 1 summarizes the overall system architecture. The
simulation environment (Block 1) generates live vehicle messages, which are transmitted to the anomaly detection module
(Block 2) for real-time classification. The resulting predictions,
combined with vehicle state information, are used to construct
a dynamic communication graph. This graph is then processed
by the control module (Block 3), where a GNN–PPO policy
evaluates each communication link and decides whether to
prune or retain it. These control actions are sent back to the
simulation in real time, forming a closed-loop DT that can
both monitor and influence network behavior securely.
With the overall architecture defined, we now detail the
two core components of the proposed DT framework. We
begin with the anomaly classification module, which detects
message-level anomalies based on temporal behavior patterns
in vehicle communication.

B. Anomaly Classification module
The anomaly classification module represents the first stage
of the DT framework, responsible for detecting abnormal V2V
communication behavior in real time. Operating continuously
alongside the simulated VANET, this module monitors vehicle activity and produces binary predictions that inform the
downstream decision-making process.
We formulate anomaly detection as a binary time-series
classification task. Each V2V message mt generated at time
t, is associated with a temporal sequence of past observations:
Xt = [xt−T +1 , xt−T +2 , . . . , xt ] ∈ RT ×d .

(1)

where xt ∈ Rd denotes the state vector of the vehicle at
time t, T is the size of the temporal window, and d is the
dimensionality of the features. Each xt includes a set of
physical and contextual features:
xt = [PosXt , PosYt , SpdXt , SpdYt ,AclXt , AclYt ,
HedXt , HedYt ]

(2)

The objective is to learn a classification function fθ , parameterized by model weights θ, that maps each input sequence

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

5

Xt to a binary output:
ybt = fθ (Xt ) ∈ {0, 1}

(3)

where ybt = 1 denotes a malicious message and ybt = 0
indicates a normal one.
During training, the model is supervised using ground-truth
labels yt ∈ {0, 1}, which indicate whether the message at time
t is actually malicious. The model parameters θ are optimized
using the Binary Cross-Entropy (BCE) loss:
X
LBCE = −
[yt log(ybt ) + (1 − yt ) log(1 − ybt )]
(4)
t

To implement this classification function, we evaluate several state-of-the-art deep temporal models known for their
effectiveness on sequential data:
• TimesNet [38] a convolutional neural network that captures long-range temporal patterns using temporal convolutional blocks.
• Non-Stationary
Transformer
(NST), [39] a
Transformer-based model designed to handle evolving
temporal distributions.
• Informer, [40] another Transformer-based model optimized for efficient modeling of long sequences through
probabilistic self-attention mechanisms.
Each of these models takes the sequence Xt as input and
outputs a probability indicating the likelihood of a malicious
message. The final binary prediction ybt is then used as an input
feature in the graph constructed by the next module GRL. This
allows the agent to reason over both physical dynamics and
inferred message trustworthiness.
While this module provides fast, data-driven detection, it
may still produce false positives FP (incorrectly flagging
normal messages) and false negatives FN (missing actual
attacks). These uncertainties motivate the use of the GRL module, which refines the final security decisions by evaluating
predictions in the context of the overall communication graph.
C. Graph Reinforcement Learning module
While the anomaly classifier produces real-time, messagelevel predictions, its output may contain errors such as FP or
FN. To enhance robustness, the DT framework includes a GRL
agent. This agent operates on a dynamic graph representation
of the VANET and learns to selectively prune unsafe communication by observing the evolving structure and behavior of
the network.
We formulate this control task as a Markov Decision Process
(MDP) defined by the tuple (S, A, P, R, γ), where:
1) State Space S: At each timestep t, the VANET is
represented as a directed graph Gt = (Vt , Et ), where:
• Vt is the set of vehicles (nodes),
• Et ⊆ Vt × Vt is the set of active V2V communication
links (edges).
Each edge eij ∈ Et is encoded as a feature vector:
stij = [SenderIDi , ReceiverIDj , Timestamp, PosX, PosY,
SpdX, SpdY, AclX, AclY, HedX, HedY,
AnomalyLabel, FP Rate, FN Rate]

(5)

Each stij includes:
• Physical state of the sender vehicle (position, speed,
acceleration, heading).
• Anomaly Label predicted by the anomaly detection
model indicating whether the message is predicted to be
malicious.
• Communication Metadata: The message timestamp and
the sender and receiver indices, identifying the link
context.
• Temporal Risk Statistics: The FP and FN rates, computed over a sliding window to capture recent classification trends and guide the GRL agent’s response to
evolving uncertainty.
2) Action Space A: The GRL agent must decide, for each
edge eij ∈ Et , whether to allow or block communication:
atij ∈ {0, 1},

where 1 = Prune, 0 = Maintain

(6)

The action vector At includes a binary decision for every edge
in the graph. These actions are applied at the end of each
timestep, and communication on pruned links is blocked in
the subsequent simulation step.
3) Reward Function R: Unlike traditional environments
where each time step has a scalar reward, our agent receives
per-edge rewards based on the correctness of each pruning
decision. The reward function balances True Positives (TP),
False Positives (FP), False Negatives (FN), and True Negatives
t
(TN). For each edge eij , the reward rij
is computed as:

t

+α · wmal if aij = 1 ∧ yij = 1 (TP)

−β · w
t
norm if aij = 1 ∧ yij = 0 (FP)
t
(7)
rij
=
−γ · wmal
if atij = 0 ∧ yij = 1 (FN)



+δ · wnorm if atij = 0 ∧ yij = 0 (TN)
where:
t
• aij : Agent’s action (1 = prune, 0 = keep)
• yij : Ground-truth class (1 = malicious, 0 = normal)
• wmal , wnorm : dynamic class weights based on the proportion of malicious and normal messages in the current
timestep, calculated as:
Nnorm
Nmal
, wnorm =
(8)
wmal =
N
N
where Nmal is the number of malicious messages (i.e.,
messages with yij = 1 at the current timestep, Nnorm is
the number of normal messages (i.e., messages with yij =
0, and N = Nmal +Nnorm . These weights emphasize the
minority class by giving it proportionally higher influence
in the reward function.
To prevent reward accumulation from masking poor decisions (e.g., being rewarded for pruning some malicious links
while still maintaining others), we implement adaptive penalty
scaling. The environment tracks recent FP and FN rates over
a sliding window and increases β or γ dynamically when
the corresponding error rate increases. This adaptive shaping
ensures that the agent focuses on improving its weakest
decision type over time. The agent’s total reward at time t
is the sum of edge-level rewards:
X
t
Rt =
rij
(9)
eij ∈Et

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

6

The agent learns a policy πθ that maximizes the expected
cumulative discounted reward.
" T
#
X
π ∗ = arg max Eπ [Gt ] = arg max Eπ
γ t Rt
(10)
π

π

t=0

where γ ∈ [0, 1] is the discount factor.
4) GRL Agent Architecture: The GRL policy network is
composed of a GNN used as a feature extractor, followed
by two output heads trained using PPO. The GNN processes
graph-structured state information and encodes it into a compact latent representation that supports link-level decisionmaking.
The architecture, see figure 1, begins with a fully connected
layer, followed by two residual blocks with batch normalization, gated skip connections, and dropout. This is followed
by a self-attention block to model long-range interactions.
And a multi-branch downsampling unit to compress node
embeddings into a shared feature vector.
This representation is shared by two separate heads:
• The policy head: produces edge-level logits that are
thresholded into binary actions (prune or maintain).
• The value head: estimates the scalar value of the current
graph state, providing a baseline for policy optimization.
5) Training Strategy: The GRL agent is trained offline using PPO on data collected from simulated VANET trajectories.
At each training step, a graph is constructed from the vehicle
states and the predictions. Rewards are computed using the
adaptive shaping strategy, and gradients are optimized using
the clipped PPO objective.
h

i
LPPO = Et min rt (θ)Ât , clip (rt (θ), 1 − ϵ, 1 + ϵ) Ât
+ c1 · MSE(V (st ), Gt ) − c2 · H[πθ ]

(11)

where rt (θ) is the ratio between the new and old policy
probabilities, Ât is the advantage estimate from Generalized
Advantage Estimation (GAE) [41], and H[πθ ] is the entropy
of the policy to encourage exploration. The constants c1 and
c2 weight the value loss and entropy regularization.
Hyperparameters such as batch size, learning rate, and
entropy coefficient are tuned for training stability.
6) GRL Decision-Making Mechanism: At each decision
step, the GRL agent observes a dynamically constructed V2V
communication graph, where nodes represent vehicles, and
edges correspond to active V2V message exchanges. Each
edge is encoded with a feature vector that captures the physical
state and communication context, including sender and receiver identifiers, message timestamp, vehicle position, speed,
acceleration, heading, the binary anomaly label produced by
the detector, and the recent false positive and false negative
rates computed over a sliding window. The agent processes the
full graph using a GNN encoder and outputs a binary action
for each edge: maintain (retain the communication link) or
prune (suppress the link). These decisions are applied after
each detection cycle in real time, allowing the communication
graph to adapt dynamically based on evolving message behavior. The policy is trained using PPO to maximize a reward
that promotes correct suppression of malicious links while
preserving legitimate communication.

IV. T RAINING M ETHODOLOGY
This section presents the full training methodology for the
proposed DT-based VANET security framework. We use a
combination of a large-scale public dataset (VeReMi) [42] and
simulation-generated data to enable both generalization and
environment-specific adaptation. The entire training process
that covers data, model training, and policy optimization is
summarized in Algorithm 1.
Algorithm 1 Training Pipeline for the VANET Digital Twin
Framework
Input: VeReMi dataset Dpublic , simulation-generated dataset
Dsim
Output: Trained anomaly detection model fθ , trained GRL
policy πϕ
1. Train Anomaly Detector
Pre-train time-series model fθ on Dpublic
Fine-tune fθ on simulation data Dsim
2. Generate Graph-Based Training Data
Run simulation and classify messages using fθ
Construct communication graphs using vehicle state and
predicted labels
3. Train GRL Agent
Train GRL policy πϕ using PPO on collected graph
trajectories

A. Dataset Description
This study uses a combination of public and simulationgenerated datasets to train, adapt, and evaluate the components
of the proposed VANET security framework. All datasets
consist of structured V2V messages that contain vehicle behavioral features such as position, speed, acceleration, heading,
sender/receiver IDs, and timestamps. Each message is labeled
as normal (0) or malicious (1), depending on whether it was
affected by an injected attack.
1) VeReMi Dataset: The Vehicular Reference Misbehavior (VeReMi) dataset [42] is a widely used benchmark for
anomaly detection in VANETs. It includes multiple attack
scenarios such as GPS falsification, message flooding, and
Sybil attacks. In this work, VeReMi is used to train and
benchmark the anomaly classifier within the DT framework.
The dataset includes approximately 3.2 million V2V messages,
with around 40.5% labeled as malicious. The class distribution
is illustrated in Figure 2.
2) Simulation-Generated Dataset: To adapt the anomaly
detector to our simulation domain and train the GRL agent,
we generated custom datasets using our simulation framework.
Two simulation runs were conducted, each with different
randomized parameters and attack schedules:
• The first dataset was used to fine-tune the anomaly
detector on domain-specific behavioral patterns.
• The second was used to train the GRL agent, enabling it
to learn context-aware link pruning strategies

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

7

59.49%

TimesNet
Informer
NST

Loss

0.13

1.5
Count

Loss (train)

0.14

40.51%

0.80

5

10

Epoch

15

0.65 0

0.85

F1 Score (train)

0.80
0.75

0.70

0

0.5

Accuracy (train)

0.75

0.12
0.11

1.0

0.85

F1 Score

2.0

Distribution of attacks

Accuracy

1e6

5

TimesNet
Informer
NST
10 15

Epoch

0.70
0.65 0

5

TimesNet
Informer
NST
10 15

Epoch

Fig. 4. Training loss, accuracy, and F1-score over epochs for TimesNet,
Informer, and NST trained on the VeReMi dataset

0.0

Normal

Class

Attack

TABLE I
ACCURACY AND F1- SCORE OF EACH DT MODEL ON THE V E R E M I TEST
SET

Fig. 2. The class distribution of VeReMi Dataset

16000
14000

Distribution of attacks

51.40%

48.60%

Count

12000

Accuracy
0.8192
0.8190
0.8168

F1-Score
0.8077
0.8067
0.8041

TABLE II
ACCURACY AND F1- SCORE OF DT MODELS ON SIMULATION - GENERATED
DATA BEFORE FINE - TUNING .

10000
8000
6000

Model
TimesNet
Informer
NST

4000
2000
0

Model
TimesNet
Informer
NST

Normal

Class

Accuracy
0.4669
0.4555
0.4283

F1-Score
0.3743
0.3534
0.3199

Attack

Fig. 3. The class distribution of Generated Dataset

To ensure proper domain adaptation and avoid leakage, the
simulation data used for training is completely disjoint from
the datasets used during evaluation. The types of attacks used
in these training datasets are described in Section V. Figure
3 shows the class distribution of one simulation run used for
training.
B. Anomaly Detector Training
To assess the effectiveness of time-series anomaly classification, we benchmark three state-of-the-art deep temporal
models on the VeReMi dataset: TimesNet, Non-Stationary
Transformer (NST), and Informer. These models are designed
to capture temporal dependencies in sequential data, a critical
capability for detecting malicious V2V messages in dynamic
vehicular environments.
All models were trained using a consistent set of input
features, including vehicle position, speed, acceleration, and
heading. The dataset was split into 80% training and 20%
testing. Training was conducted for a maximum of 20 epochs
using the Adam optimizer and early stopping based on validation loss to prevent overfitting.
Figure 4 shows the performance of the training in terms of
loss, accuracy and F1-score over epochs. TimesNet showed the
fastest convergence and highest training performance, while
Informer and NST followed closely with more gradual but
stable improvements.
To assess generalization, all models were evaluated on the
test set. Table I presents the accuracy and F1-score achieved

by each model. All three achieved strong classification performance, with TimesNet slightly outperforming the others in
both accuracy and F1-score.
C. Distribution Shift & Fine-Tuning
Although the anomaly detection models performed well on
the VeReMi dataset, their performance deteriorated significantly when applied directly to our simulation environment. As
discussed in Section IV-A2, we generated new datasets, which
introduced variability in road structures, vehicle dynamics,
message timings, and randomized attack scheduling. These
differences introduced a distribution shift between the training
domain (VeReMi) and the target simulation environment used
throughout this work.
This shift impacts model generalization. The TimesNet,
Informer, and NST models were initially trained on the structured patterns present in VeReMi, which do not fully reflect the
diversity and randomness of our simulation-based scenarios.
When evaluated on one of our generated datasets, all models
exhibited a substantial drop in accuracy and F1-score (see
Table II), confirming the need for adaptation.
While one option would be to train anomaly detection
models directly on simulation data, this approach presents
several limitations. First, our simulation datasets contain only
about 27,000 labeled samples, whereas VeReMi offers more
than 3 million V2V messages, making them more suitable
for training deep temporal models. Second, collecting large
amounts of simulation data is both time-consuming and computationally expensive. As a result, training models from
scratch on simulation-only data would likely lead to suboptimal performance and a high data collection cost.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

8

Accuracy (train)

Loss (train)

1.5

TimesNet
Informer
NST

0.70
0.65

Loss

0.5

0.55
0.50

0.5
0

5

10

0.45

Epoch

TimesNet
Informer
NST

0.6

0.60

1.0

F1 Score (train)

0.7

F1 Score

TimesNet
Informer
NST

Accuracy

2.0

0.4
0

5

10

Epoch

0

5

10

Epoch

Fig. 5. Training loss, accuracy, and F1-score curves for fine-tuning DT models
on simulation data.
TABLE III
P OST- FINETUNING ACCURACY, F1- SCORE , GPU MEMORY USAGE , AND
INFERENCE TIME .
Model
TimesNet
Informer
NST

Accuracy
0.6033
0.8134
0.6199

F1-Score
0.6136
0.8249
0.6222

GPU Mem
17.91 GB
0.17 GB
0.19 GB

Inf. Time
228.24 s
33.20 s
33.50 s

To overcome this, we adopt a two-stage training strategy:
models are first trained on VeReMi to capture general communication patterns, then fine-tuned on simulation output to
adapt to scenario-specific dynamics.
Figure 5 shows the progress of the training of all three
models during fine-tuning, including loss, accuracy, and the
F1-score in epochs. Informer exhibited the most stable and
rapid convergence, followed by NST and TimesNet.
After fine-tuning, the models were re-evaluated on the test
set. Table III summarizes the results, including classification
performance and resource usage. Informer achieved the highest
classification performance while also requiring significantly
less GPU memory and inference time. Based on these results,
Informer was selected as the final anomaly detection model
for all remaining experiments. It offers the best balance
between classification accuracy and real-time inference efficiency, which makes it well suited for integration into the
real-time simulation loop described in Section III-A.
D. Graph Construction
Once the anomaly detection model is fine-tuned, its outputs are used to generate graph-based observations for GRL
training. Each node in the graph represents a vehicle and is
assigned a feature vector containing physical state information
(e.g., position, velocity, acceleration, heading), along with the
binary anomaly labels generated by the classifier. Edges represent active V2V communication links between vehicles. These
node and edge definitions form a dynamic communication
graph, which is constructed at each simulation timestep. The
graph is updated every 0.1 seconds (see Table IV), aligned
with the beacon interval used in the communication protocol.
This frequency ensures that the GRL agent receives up-todate inputs reflecting recent V2V interactions. It provides a
balance between real-time responsiveness and computational
efficiency: more frequent updates would increase system latency, while slower updates could delay corrective actions and
reduce mitigation effectiveness.

E. GRL Agent Training
The GRL agent is trained offline using the communication graph sequences generated during simulation. At each
timestep, the agent observes a graph and outputs edge-level
decisions to prune or maintain each communication link. After
each decision, a reward is computed for every edge based on
the accuracy of the pruning action. The reward formulation,
introduced in Section III-C3, balances precision and recall
using class-weighted signals and adaptive shaping based on
recent trends in false positives and false negatives.
The agent is optimized using the PPO algorithm. The
GRL policy network consists of a GNN encoder followed
by two output heads: one for the edge-level pruning actions
and one for the state value estimation. Advantage estimates
are computed using GAE to guide policy updates. PPO was
selected due to its state-of-the-art performance reported on
a wide range of RL tasks [37]. As a policy gradient method,
PPO offers stable learning and is relatively easy to implement,
making it well-suited for training in dynamic, graph-based
environments such as VANETs. Compared to value-based
methods such as DQN, PPO has been shown to perform more
reliably in high-dimensional scenarios, which are typical in
our message-level mitigation task [43].
V. E XPERIMENTAL S ETUP AND R ESULTS
We now evaluate the effectiveness of the proposed framework in a simulated VANET environment, using unseen road
topologies, varying traffic conditions, and multiple attack
scenarios.
A. Simulation Scenario Setup
To emulate realistic vehicle mobility and communication
behavior, we implement a simulation-driven DT using a hybrid
framework composed of OMNeT++, SUMO, and Veins (a
video demonstration is available) 1 :
• OMNeT++ handles the simulation of the discrete event
network.
• SUMO performs microscopic vehicular traffic simulation.
• Veins integrates OMNeT++ and SUMO through TraCI
(Traffic Control Interface) [44], enabling real-time interaction between vehicle mobility and communication.
The details of the full simulation environment are summarized in Table IV.
1) Real-World Roads Topologies: To ensure environmental
diversity and urban realism, three real-world road networks
were extracted from OpenStreetMap (OSM) and manually
refined using JOSM (Java OpenStreetMap Editor). This preprocessing removed invalid geometries and simplified the
networks for simulation.
• Road 1: A simpler layout with roundabouts from Marrakech, Morocco.
• Road 2: A denser and irregular urban zone from
Casablanca, Morocco.
• Road 3: A structured urban grid from Orlando, USA.
1 A demonstration video link https://youtu.be/LPpwGdiFBXw

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

9

TABLE IV
S IMULATION E NVIRONMENT D ETAILS
Parameter

Value
Simulation Tools
Traffic Simulator
SUMO 1.8.0
Network Simulator
OMNeT++ 5.6.2
V2X Framework
Veins 5.2
Road Scenarios
Road 1
2.7 km × 2.1 km
Road 2
12.5 km × 6.9 km
Road 3
6.9 km × 9.0 km
Map Source
OpenStreetMap
Traffic Configuration
Simulation Time
500 s
Number of Vehicles
20, 50, 100
Vehicle Generation Rate
1 veh/s
Number of Lanes
1–2 per direction
Vehicle Speed
50–100 km/h
Communication Configuration
MAC Protocol
IEEE 802.11p
Frequency Band
5.9 GHz
Channel Bandwidth
10 MHz
Transmission Power
20 mW
Beacon Interval
0.1 s
Attack Configuration
Malicious Vehicle Ratio
10%, 20%, 30%, 50%
Attack Types
DoS, Random Speed, Position Offset

These maps provide varying traffic conditions, road connectivity, and topology complexity (see Figure 6).
Each road was simulated with three different vehicle densities (20, 50, 100 vehicles) and four levels of malicious node
presence (10%, 20%, 30%, 50%). Vehicles exchange V2V
messages within a 400-meter communication radius.
2) Attack Injection Models: To evaluate the system under
adversarial conditions, we implement three realistic messagelevel attack models, each designed to degrade the quality of
shared information differently:
• DoS Disruptive Attack: This attack aims to overload the
network by generating a large volume of falsified motion
data. It achieves this by injecting speed values that follow
a sinusoidal pattern and by synthesizing false acceleration
and heading information. The impact of this attack lies
in its ability to flood the communication channel and
overwhelm receivers with contradictory signals.
• Random Speed Attack: The objective of this attack is
to subtly corrupt the velocity data in a way that appears
plausible to anomaly detectors. It operates by adding
Gaussian noise (σ = 15/3) to the actual speed values,
while also introducing small random perturbations to
acceleration.
• Constant Position Offset Attack: This attack persistently shifts the vehicle’s reported position by a fixed
spatial offset (σ = 40meters), while preserving normallooking speed and acceleration values. It subtly injects
location errors over time, causing the vehicle to appear
to be offset from its actual trajectory. This creates “ghost
vehicle” effects in the perception of neighboring nodes.
Each attack is triggered probabilistically during the simulation based on the assigned malicious vehicle ratio and may
vary in temporal and spatial execution to simulate various realworld threat patterns.

(a)

(b)

(c)
Fig. 6. Real-world road networks used in the simulation experiments. (a)
Road 1: Marrakech, Morocco. (b) Road 2: Casablanca, Morocco. (c) Road 3:
Orlando, USA.

3) Hardware Setup: All simulations were executed on
a desktop machine equipped with an Intel Core i7-10700
CPU @ 2.90 GHz and 16 GB RAM. Training for anomaly
detection models and the GRL agent was performed offline
on a NVIDIA A100-SXM4 GPU with 80 GB memory. All
simulation runs were initialized with different random seeds
to ensure statistical diversity and reproducibility.
4) Real-Time System Integration: The proposed framework
integrates a VANET simulation with a Python-based backend responsible for real-time anomaly detection and postdetection control. This setup forms a closed-loop system
where V2V messages are classified in real time, and link-level
control actions are enforced dynamically within the simulation.
Communication between OMNeT++ and the Python back-end
is established using a TCP/IP socket based on the Winsock
API. At each simulation timestep, when a vehicle transmits a
message, relevant data such as sender ID, position, velocity,
acceleration, heading, and timestamp are extracted and sent to
the Python server. The server reconstructs the input time-series
sequence for the message sender and uses a checkpointed
Informer model to classify the message as normal or malicious. The binary prediction, along with the corresponding
vehicle state and context, is then embedded in a dynamic
communication graph. This graph is passed to the GRL agent,

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

10

TABLE V
GNN S TRUCTURE
Parameter
Number of Layers
Hidden Dimensions
Output Dimension
Attention Heads
Activation Function
Dropout Rate
Normalization

Value
2 Residual Blocks + 1 Attention Layer
512 → 768 → 512
512
8
GELU
0.25
LayerNorm + BatchNorm

TABLE VI
PPO H YPERPARAMETERS
Parameter
Learning Rate
Discount Factor (γ)
GAE Lambda (λ)
Clip Range
Batch Size
Number of Epochs
Entropy Coefficient

Value
3 × 10−4
0.995
0.95
0.2
256
8
0.005

which uses a trained GNN + PPO policy to determine, for
each edge, whether to maintain or prune the communication
link. These decisions are sent back to the C++ simulation
via the same TCP socket. Upon receiving the decision, the
simulation enforces the pruning action by suppressing message
forwarding between affected vehicles in the next simulation
step. This tight integration allows the system to maintain
temporal consistency and ensures that detection and control
occur continuously during the simulation runtime.
B. Evaluation Datasets
All evaluation results are based on simulation-generated
datasets that are completely separate from those used during
training and fine-tuning. These test datasets were generated
with varied road structures, traffic densities, and attack ratios.
This allowed us to assess the generalization and robustness of
the full system.
C. GRL Architecture and Training Configuration
The GRL agent was trained offline for 100,000 training
steps on a single NVIDIA A100-SXM4-80GB GPU. The
training process took approximately 2.5 hours. To ensure
reproducibility of the GRL module, we provide a complete
description of the GNN architecture and the hyperparameters
used to train the PPO agent. Table V summarizes the architecture of the GNN, including the number of layers, hidden
dimensions, attention heads, and activation functions. Table
VI lists the full PPO training configuration. All parameters
were tuned for stability and performance within the simulation
domain. Our code is publicly accessible on GitHub 2 .
D. Evaluation and Ablation Study
In this section, we evaluate the complete VANET security
framework and analyze the contribution of the GRL module
through ablation to the baseline classifier.
2 Source code is available at: https://github.com/latifa1999/VanetSecurity

Table VII presents the performance comparison across three
representative attack types: Constant Position Offset, Random
Speed, and DoS. Tables VIII, IX, and X summarize the
performance comparison in three different road configurations,
varying vehicle density (20, 50, 100 vehicles) and malicious
vehicle ratios (10% to 50%). Each table compares the baseline Informer performance with the proposed Informer+GRL
pipeline in terms of precision, recall, F1-score, and accuracy.
The improvement column reflects the gain in F1-score, which
we consider to be the most representative metric in this setting.
Overall, the proposed framework demonstrates consistent performance improvements in all road scenarios and evaluation
settings, highlighting the generalizability of our approach. The
GRL component improves the reliability of the classification
under varying traffic densities and attack intensities. In the
following, we summarize the key findings that emerge from
this evaluation:
1) Performance Across Attack Types: Table VII reports
model performance across three attack types under the same
traffic scenario. The Constant Position Offset attack shows
the lowest baseline F1-score (0.8085), as it preserves realistic
speed and acceleration while introducing a persistent spatial
displacement that is difficult for time-series models to detect.
This is where the GRL agent provides the largest F1-score
improvement (+2.36%), as graph-based reasoning exposes
spatial inconsistencies between neighboring vehicles.
The DoS Disruptive and Random Speed attacks yield similar
baseline F1-scores (≈0.828), with smaller GRL F1-score gains
(+0.41% and +0.39%, respectively). Random Speed introduces
subtle Gaussian noise that is effectively captured by temporal
patterns, while DoS primarily affects message volume and
congestion, offering limited stable structural cues for graphbased correction.
Across all attack types, Recall gains exceed Precision gains,
indicating that GRL mainly reduces false negatives by correcting missed detections, while maintaining a low false-positive
rate.
2) Performance by road scenario:
• Road 3 (Table X) shows the most significant optimization
potential, with an average improvement in the F1-score
of +3.18% and a peak gain of +17.86% in the most
challenging setting (20 vehicles, 50% malicious nodes).
This indicates that the GRL agent is highly effective in
handling complex or irregular environments, where the
base Informer model tends to make more classification
errors.
• Road 2 (Table IX) achieves the highest absolute performance, with an average F1-score of 83.09% after applying GRL. However, the average improvement is smaller
(+1.60%), suggesting that Informer already performed
strongly in this structured setting, leaving less room for
post-classification correction.
• Road 1 (Table VIII) demonstrates consistent refinement
capabilities, with an average improvement of +2.32% in
F1-score in all densities and attack levels. This confirms
the robustness of the GRL post-processing module in
moderately complex network configurations.
3) Impact of Network Density:

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

11

TABLE VII
P ERFORMANCE C OMPARISON ACROSS ATTACK T YPES
Attack Type
Constant Position Offset
DoS Disruptive
Random Speed

Method
Informer
Informer+GRL
Informer
Informer+GRL
Informer
Informer+GRL

Precision
0.9303
0.9633
0.9691
0.9709
0.9680
0.9706

The Informer+GRL system performs best in low-density
scenarios, particularly with 20 vehicles, where it achieves
the highest average improvement in F1-score on all roads
(up to +5.88%). In such settings, the graph structure is
simpler, making malicious behavior more distinguishable
through relational context.
• In denser environments (100 vehicles), the average gain
drops (e.g., +1.55%), likely due to increased message
overlap, graph sparsity and noise, which limit the agent’s
ability to confidently distinguish anomalous patterns.
4) Effect of Attack Intensity:
• The GRL layer is especially effective under high attack
conditions. On Road 3, it achieves a gain of nearly
+17% in F1-score at 50% malicious nodes, showcasing its
capacity to correct classification errors when the Informer
becomes less reliable.
• Even under lower threat levels (e.g., 10–20% malicious),
the GRL consistently contributes positive improvements,
highlighting its generalization capability across varying
degrees of adversarial influence.
5) Interaction Between Vehicle Density and Attack Intensity: Tables VIII, IX and X reveal how vehicle density and
attack intensity jointly influence GRL effectiveness.
The strongest improvements occur in low-density settings
with high attack intensity. At 20 vehicles and 50% malicious
nodes, GRL achieves +17.86% on Road 3 and +4.46% on
Road 1 in the F1-score. In such cases, the sparse graph
provides clearer topological structure, and the higher error
rate gives the agent more opportunities to correct classification
mistakes.
In contrast, high density with low attack intensity yields
minimal gains in F1-score. At 100 vehicles with 10% malicious nodes, the improvements drop to +0.25% (Road 1) and
+0.48% (Road 2). Here, the dense graph structure obscures
relational patterns, and there are few classification errors
to correct. Moreover, the interaction effect varies with road
complexity. On Road 3 (most complex), the performance in
the F1-score improves steadily with the attack ratio in lowdensity conditions (+0.93% at 10% to +17.86% at 50%).
This suggests that GRL is most helpful when the Informer
struggles in challenging environments. However, on simpler
roads, improvements tend to level off at moderate attack ratios
(20–30%), indicating less room for graph-based correction.
This ablation study confirms that the integration of GRL
into the VANET DT significantly enhances the mitigation
of anomalies. The GRL agent consistently improves performance over the base classifier, especially in complex road
layouts, low-density scenarios, and high-attack conditions.
•

Recall
0.7284
0.7550
0.7473
0.7524
0.7468
0.7515

F1-Score
0.8085
0.8276
0.8285
0.8319
0.8280
0.8312

Improvement (F1-score)
+2.36%
+0.41%
+0.39%

These results position GRL as a powerful, context-aware
post-classification optimization layer capable of maintaining
communication integrity in diverse and dynamic VANET
environments.
VI. D ISCUSSION AND FUTURE WORK
This work presents a complete real-time security framework for VANETs that integrates time-series-based anomaly
detection with post-detection mitigation via GRL. Unlike prior
approaches that separate detection from response, this system
processes V2V message streams continuously, classifies messages based on temporal patterns, and adapts the communication graph by pruning links identified as risky. Experimental
results in multiple road topologies and attack intensities show
that the framework improves system resilience, especially
under sparse traffic and high-threat scenarios, by correcting
false positives and false negatives and maintaining message
flow integrity. Additionally, the use of a fine-tuning pipeline
allows us to leverage large-scale public datasets for general
representation learning while efficiently adapting to simulated
conditions with far fewer data.
However, several important aspects deserve further discussion. The proposed GRL-based framework demonstrates
consistent performance across varying traffic densities (20, 50,
and 100 vehicles), indicating its ability to scale to moderately
sized VANET scenarios. As the number of vehicles increases,
the communication graph becomes larger and more complex,
leading to higher computational and memory requirements
for real-time decision-making. While the current centralized
design remains effective within the evaluated settings, future
work will explore Multi-Agent Graph Reinforcement Learning
(MAGRL) to enable distributed decision-making over localized subgraphs, improving scalability and responsiveness in
large-scale environments.
In addition, although the framework is evaluated on representative attack types (DoS, Random Speed, and Position
Offset), its design is general and can be extended to incorporate a broader range of attack models. This includes more
sophisticated threats such as Sybil attacks, replay attacks, and
coordinated multi-node misbehavior, which can be integrated
within the same detection-mitigation pipeline.
From a deployment perspective, the proposed framework
is designed to operate in real time within a Digital Twin
environment; however, its practical implementation would
require integration with edge computing infrastructure such as
Road Side Units (RSUs). Challenges such as communication
latency, synchronization between simulation and real-world

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

12

TABLE VIII
P ERFORMANCE A NALYSIS ON ROAD 1: I NFORMER VS I NFORMER + GRL ACROSS D IFFERENT V EHICLE D ENSITIES AND ATTACK I NTENSITIES
Vehicles
20

Attack %

Method

10%

Informer
Informer+GRL
20%
Informer
Informer+GRL
30%
Informer
Informer+GRL
50%
Informer
Informer+GRL
50
10%
Informer
Informer+GRL
20%
Informer
Informer+GRL
30%
Informer
Informer+GRL
50%
Informer
Informer+GRL
100
10%
Informer
Informer+GRL
20%
Informer
Informer+GRL
30%
Informer
Informer+GRL
50%
Informer
Informer+GRL
Informer Average
Informer+GRL Average

Precision
89.11
93.28
81.11
89.18
84.44
90.09
80.91
89.15
83.72
89.89
81.00
88.54
84.23
90.38
88.81
92.39
87.01
90.57
83.95
90.33
87.21
91.65
86.60
92.86
86.49
90.45

Performance Metrics (%)
Recall
F1-Score
Accuracy
74.51
79.46
74.51
76.93
81.58
76.93
75.88
77.16
75.88
81.39
82.52
81.39
78.70
80.44
78.70
79.06
81.26
79.06
80.92
80.92
80.92
85.35
85.38
85.35
77.93
79.96
77.93
79.17
81.23
79.17
79.94
80.20
79.94
83.27
83.57
83.27
78.40
80.25
78.40
79.09
81.43
79.09
74.57
78.97
74.57
76.83
80.95
76.83
78.06
80.88
78.06
78.54
81.13
78.54
75.90
78.45
75.90
76.54
79.50
76.54
76.66
79.97
76.66
77.11
80.70
77.11
71.93
77.26
71.93
73.07
78.54
73.07
77.19
79.51
77.19
79.31
81.83
79.31

Improvement (F1-score)
+2.12%
+5.36%
+0.82%
+4.46%
+1.27%
+3.37%
+1.18%
+1.98%
+0.25%
+1.05%
+0.73%
+1.28%
+2.32%

TABLE IX
P ERFORMANCE A NALYSIS ON ROAD 2: I NFORMER VS I NFORMER +GRL ACROSS D IFFERENT V EHICLE D ENSITIES AND ATTACK I NTENSITIES
Vehicles
20

Attack %
10%

Method

Informer
Informer+GRL
20%
Informer
Informer+GRL
30%
Informer
Informer+GRL
50%
Informer
Informer+GRL
50
10%
Informer
Informer+GRL
20%
Informer
Informer+GRL
30%
Informer
GRL
50%
Informer
Informer+GRL
100
10%
Informer
Informer+GRL
20%
Informer
Informer+GRL
30%
Informer
Informer+GRL
50%
Informer
Informer+GRL
Informer Average
Informer+GRL Average

Precision
81.92
90.01
82.28
90.72
82.81
89.15
88.90
91.05
89.11
92.91
83.30
89.70
83.73
90.10
88.97
92.43
82.48
88.38
83.83
88.67
91.45
93.97
92.11
94.86
85.26
88.63

Performance Metrics (%)
Recall
F1-Score
Accuracy
78.26
78.77
78.26
85.99
86.32
85.99
81.86
81.73
81.86
88.73
88.51
88.73
82.69
82.72
82.69
85.71
85.62
85.71
87.80
87.79
87.80
89.26
89.04
89.26
76.65
80.77
76.65
77.59
81.81
77.59
80.48
81.40
80.48
80.76
82.32
80.76
76.64
78.77
76.64
78.45
80.80
78.45
76.12
80.15
76.12
77.13
81.19
77.13
82.06
82.21
82.06
82.19
82.69
82.19
83.54
83.63
83.54
83.99
84.16
83.99
74.98
80.41
74.98
77.59
82.48
77.59
74.78
81.01
74.78
75.06
81.35
75.06
79.89
81.49
79.89
81.41
83.09
81.41

data, and distributed coordination must be carefully addressed
to ensure reliable operation in real-world scenarios.
Future work will further investigate distributed GRL strategies and enhance robustness against adaptive and evolving
attack behaviors, enabling the system to maintain reliable
performance in increasingly complex VANET environments.

Improvement (F1-score)
+7.55%
+6.78%
+2.90%
+1.25%
+1.04%
+0.92%
+2.03%
+1.04%
+0.48%
+0.53%
+2.07%
+0.34%
+1.60%

VII. C ONCLUSION
Securing VANETs against malicious behaviors remains a
fundamental challenge due to their dynamic topology, realtime communication demands, and susceptibility to data-level
attacks. Traditional detection methods often rely on static
features or fail to address how the system should respond after

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

13

TABLE X
P ERFORMANCE A NALYSIS ON ROAD 3: I NFORMER VS I NFORMER + GRL ACROSS D IFFERENT V EHICLE D ENSITIES AND ATTACK I NTENSITIES
Vehicles
20

Attack %

Method

10%

Informer
Informer+GRL
20%
Informer
Informer+GRL
30%
Informer
Informer+GRL
50%
Informer
Informer+GRL
50
10%
Informer
Informer+GRL
20%
Informer
Informer+GRL
30%
Informer
Informer+GRL
50%
Informer
Informer+GRL
100
10%
Informer
Informer+GRL
20%
Informer
Informer+GRL
30%
Informer
Informer+GRL
50%
Informer
Informer+GRL
Informer Average
Informer+GRL Average

Precision
86.40
90.60
75.11
88.90
73.77
88.00
67.47
88.96
82.85
88.66
82.11
89.42
80.26
89.14
80.89
89.62
86.45
92.93
91.14
93.71
88.51
92.13
85.35
90.26
81.62
86.70

Performance Metrics (%)
Recall
F1-Score
Accuracy
78.15
80.46
78.15
78.87
81.39
78.87
70.88
72.04
70.88
81.91
82.76
81.91
72.72
73.02
72.72
82.42
82.63
82.42
67.52
67.49
67.52
85.50
85.35
85.50
79.07
80.09
79.07
79.41
80.75
79.41
78.54
79.71
78.54
79.29
81.06
79.29
77.68
78.53
77.68
81.01
82.22
81.01
76.29
77.78
76.29
79.76
81.52
79.76
72.07
77.20
72.07
76.77
81.24
76.77
79.03
83.31
79.03
86.00
89.69
86.00
76.19
80.47
76.19
76.64
80.65
76.64
77.72
79.87
77.72
78.82
81.17
78.82
76.54
78.36
76.54
80.49
81.54
80.49

detecting suspicious behavior, especially in the presence of FP
or FN.
This work presents a complete real-time VANET security
framework that integrates time-series-based anomaly detection
with post-detection control through GRL. By fine-tuning a
state-of-the-art temporal model on V2V communication data,
the system is capable of detecting anomalies at the message
level. The GRL agent then interprets these outputs in the
context of a dynamic communication graph and learns to prune
or retain links to contain the spread of malicious information
and improve network reliability.
Through simulation-based evaluation across varying road
scenarios and attack conditions, the system demonstrated
improved resilience and adaptability, particularly in difficult
cases such as sparse traffic or high attack ratios. An ablation
study further confirmed the added value of GRL in enhancing
detection robustness and correcting classification errors in real
time.
Overall, this work contributes to a unified and data-oriented
security architecture that brings together detection and control
in a single loop. It provides a foundation for building future
intelligent and adaptive security systems capable of learning,
reacting, and adapting to evolving threats in VANET environments.
ACKNOWLEDGMENTS
This research was partially funded by Khalifa University of
Science and Technology through the Faculty Start Up Grant
Program under Project ID: KU-INT-FSU-2024-8471000001PD#10261. This research was also supported by the 6G Research Center, Khalifa University of Science and Technology

Improvement (F1-score)
+0.93%
+10.72%
+9.61%
+17.86%
+0.66%
+1.35%
+3.69%
+3.74%
+4.04%
+6.33%
+0.18%
+1.30%
+3.18%

(KU-6G). Computing resources for this study were provided
by the Toubkal High-Perormance Computing facilities of
Mohamed VI Polytechnic University at Benguerir.
R EFERENCES
[1] S. Rehman, M. A. Khan, T. Zia, and L. Zheng, “Vehicular ad-hoc
networks (VANETs)-an overview and challenges,” Journal of Wireless
Networking and Communications, vol. 3, no. 3, pp. 29–38, 2013.
[2] H. Hartenstein and K. Laberteaux, “A tutorial survey on vehicular ad
hoc networks,” IEEE Communications Magazine, vol. 46, no. 6, pp.
164–171, 2008.
[3] M. S. Sheikh and J. Liang, “A comprehensive survey on VANET security
services in traffic management system,” Wireless Communications and
Mobile Computing, vol. 2019, p. 2423915, 2019.
[4] Z. G. Al-Mekhlafi, “Software-defined vehicular networks (SDVN),”
International Journal of Computer Science & Network Security, pp.
231–243, 2022.
[5] H. Hasrouny, A. E. Samhat, C. Bassil, and A. Laouiti, “VANet security
challenges and solutions: A survey,” Vehicular Communications, vol. 7,
pp. 7–20, 2017.
[6] J. Petit and S. Shladover, “Potential cyberattacks on automated vehicles,”
IEEE Transactions on Intelligent Transportation Systems, vol. 16, no. 2,
pp. 546–556, 2015.
[7] P. Papadimitratos, L. Buttyan, T. Holczer, E. Schoch, J. Freudiger,
M. Raya, Z. Ma, F. Kargl, A. Kung, and J.-P. Hubaux, “Secure vehicular
communication systems: Design and architecture,” IEEE Communications Magazine, vol. 46, no. 11, pp. 100–109, 2008.
[8] A. Talpur and M. Gurusamy, “Machine learning for security in vehicular
networks: A comprehensive survey,” IEEE Communications Surveys &
Tutorials, vol. 24, no. 1, pp. 346–390, 2022.
[9] J. Liu, H. Zhao, P. Han, G. Gui, T. Ohtsuki, H. Sari, and F. Adachi,
“An ensemble learning-based fault detection method for vehicular ad
hoc networks in intelligent transportation systems,” IEEE Transactions
on Vehicular Technology, vol. 74, no. 3, pp. 5114–5124, 2025.
[10] N. Lu, N. Cheng, N. Zhang, X. Shen, and J. Mark, “Connected vehicles:
Solutions and challenges,” IEEE Internet of Things Journal, vol. 1, no. 4,
pp. 289–299, 2014.
[11] S. Hochreiter and J. Schmidhuber, “Long short-term memory,” Neural
Computation, vol. 9, no. 8, pp. 1735–1780, 1997.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Vehicular Technology. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TVT.2026.3688587

14

[12] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez,
Ł. Kaiser, and I. Polosukhin, “Attention is all you need,” in Advances
in Neural Information Processing Systems, vol. 30, 2017.
[13] M. S. Ramkumar, M. Sivaramkrishnan, G. C. P. Latha, M. Kanan,
G. Emayavaram, and J. Giri, “Semantic-and relation-aware heterogeneous graph neural network for secure routing in VANETs to avoid
blackhole attacks,” in Proceedings of the International Conference on
Machine Learning and Autonomous Systems (ICMLAS). IEEE, 2025.
[14] C. Hidalgo, M. Vaca, M. P. Nowak, and P. Frölich, “Detection, control
and mitigation system for secure vehicular communication,” Vehicular
Communications, vol. 33, p. 100405, 2022.
[15] H. Sedjelmaci, S.-M. Senouci, and N. Ansari, “A hierarchical detection
and response system to enhance security against lethal cyber-attacks in
UAV networks,” IEEE Transactions on Systems, Man, and Cybernetics:
Systems, vol. 48, no. 9, pp. 1594–1606, 2018.
[16] G. Rjoub, J. Bentahar, and O. A. Wahab, “Explainable AI-based federated deep reinforcement learning for trusted autonomous driving,” in
2022 International Wireless Communications and Mobile Computing,
IWCMC. IEEE, 2022.
[17] A. Alagha, M. Kadadha, R. Mizouni, S. Singh, J. Bentahar, and
H. Otrok, “UAV-assisted Internet of vehicles: A framework empowered
by reinforcement learning and blockchain,” Veh. Commun., vol. 52, p.
100874, 2025.
[18] M. ul Hassan, A. A. Al-Awady, A. Ali, Sifatullah, and M. Akram,
“ANN-based intelligent secure routing protocol in vehicular ad hoc
networks (VANETs) using enhanced AODV,” Sensors, vol. 24, no. 3, p.
818, 2024.
[19] T. N. Canh and X. HoangVan, “Machine learning-based malicious
vehicle detection for security threats and attacks in vehicle ad-hoc
network (VANET) communications,” in International Conference on
Computing and Communication Technologies (RIVF). IEEE, 2023.
[20] A. Mohta, S. Ajankar, and M. Chandane, “Network Simulator-3: A
review,” Review Article, 2023.
[21] W. El-Shafai, A. T. Azar, and S. Ahmed, “AI-driven ensemble classifier
for jamming attack detection in VANETs to enhance security in smart
cities,” IEEE Access, vol. 13, pp. 50 687–50 701, 2025.
[22] T. Alladi, B. Gera, A. Agrawal, V. Chamola, and F. R. Yu, “DeepADV:
A deep neural network framework for anomaly detection in VANETs,”
IEEE Transactions on Vehicular Technology, vol. 70, no. 9, pp. 9404–
9417, 2021.
[23] Z. G. Al-Mekhlafi and S. A. Alfhaid, Innovative Security Measures:
A Comprehensive Framework for Safeguarding the Internet of Things.
Cham: Springer Nature Switzerland, 2025, pp. 175–185.
[24] P. Malhotra, A. Ramakrishnan, G. Anand, L. Vig, P. Agarwal, and
G. Shroff, “LSTM-based encoder-decoder for multi-sensor anomaly
detection,” arXiv preprint arXiv:1607.00148, 2016.
[25] J. Guo, X. Li, Z. Liu, J. Ma, and C. Yang, “TROVE: A context-awareness
trust model for VANETs using reinforcement learning,” IEEE Internet
of Things Journal, vol. 7, no. 5, pp. 4101–4111, 2020.
[26] R. Sedar, C. Kalalas, P. Dini, F. Vázquez-Gallego, J. Alonso-Zarate, and
L. Alonso, “Knowledge transfer for collaborative misbehavior detection
in untrusted vehicular environments,” IEEE Transactions on Vehicular
Technology, vol. 74, no. 1, pp. 425–440, 2025.
[27] D. He, J. Kim, H. Shi, and B. Ruan, “Autonomous anomaly detection
on traffic flow time series with reinforcement learning,” Transportation
Research Part C: Emerging Technologies, vol. 150, p. 104089, 2023.
[28] V. Mnih, K. Kavukcuoglu, D. Silver, A. A. Rusu, J. Veness, M. G.
Bellemare, A. Graves, M. A. Riedmiller, A. K. Fidjeland, G. Ostrovski,
S. Petersen, C. Beattie, A. Sadik, I. Antonoglou, H. King, D. Kumaran,
D. Wierstra, S. Legg, and D. Hassabis, “Human-level control through
deep reinforcement learning,” Nature, vol. 518, no. 7540, pp. 529–533,
2015.
[29] B. Golchin and B. Rekabdar, “Anomaly detection in time series data using reinforcement learning, variational autoencoder, and active learning,”
in International Conference on AI, Science, Engineering, and Technology
(AIxSET), 2024.
[30] N. Jayakrishna and N. N. Prasanth, “Detection and mitigation of
distributed denial of service attacks in vehicular ad hoc network using
a spatiotemporal deep learning and reinforcement learning approach,”
Results in Engineering, vol. 26, p. 104839, 2025.
[31] K. Zhang, T. Pu, Q. Zhang, and Z. Nie, “Coordinated decision control
of lane-change and car-following for intelligent vehicle based on time
series prediction and deep reinforcement learning,” Sensors, vol. 24,
no. 2, p. 403, 2024.
[32] H. Tan, M. Wang, J. Shen, P. Vijayakumar, S. Moh, and Q. M. J. Wu,
“Blockchain-assisted conditional anonymous authentication and adaptive

tree-based group key agreement for VANETs,” IEEE Transactions on
Dependable and Secure Computing, vol. 20, pp. 1–16, 2025.
[33] M. Ismail, S. Chatterjee, J. K. Sing, S. Kumari, and J. J. P. C. Rodrigues,
“Designing anonymous key agreement scheme for secure vehicular adhoc networks,” IEEE Transactions on Intelligent Transportation Systems,
vol. 25, no. 9, pp. 11 382–11 396, 2024.
[34] D. Krajzewicz, G. Hertkorn, C. Feld, and P. Wagner, “SUMO (simulation
of urban MObility): An open-source traffic simulation,” in 4th Middle
East Symposium on Simulation and Modelling (MESM), 2002.
[35] A. Varga, “The OMNeT++ discrete event simulation system,” in Proceedings of the European Simulation Multiconference (ESM), vol. 9,
2001.
[36] C. Sommer, D. Eckhoff, A. Brummer, D. Buse, F. Hagenauer, S. Joerer,
and M. Segata, Veins: The Open Source Vehicular Network Simulation
Framework. Springer International Publishing, 2019.
[37] J. Schulman, F. Wolski, P. Dhariwal, A. Radford, and O. Klimov, “Proximal policy optimization algorithms,” arXiv preprint arXiv:1707.06347,
vol. 1707.06347, 2017.
[38] H. Wu, T. Hu, Y. Liu, H. Zhou, J. Wang, and M. Long, “TimesNet:
Temporal 2D-variation modeling for general time series analysis,” in
International Conference on Learning Representations (ICLR), 2023.
[39] Y. Liu, H. Wu, J. Wang, and M. Long, “Non-stationary transformers:
Exploring the stationarity in time series forecasting,” in Proceedings
of the 36th International Conference on Neural Information Processing
Systems. Curran Associates Inc., 2022.
[40] H. Zhou, S. Zhang, J. Peng, S. Zhang, J. Li, H. Xiong, and W. Zhang,
“Informer: Beyond efficient transformer for long sequence time-series
forecasting,” in Proceedings of the AAAI Conference on Artificial
Intelligence. AAAI Press, 2021.
[41] J. Schulman, P. Moritz, S. Levine, M. Jordan, and P. Abbeel, “Highdimensional continuous control using generalized advantage estimation,”
arXiv preprint arXiv:1506.02438, 2015.
[42] J. Kamel, M. Wolf, R. W. van der Hei, A. Kaiser, P. Urien, and
F. Kargl, “VeReMi extension: A dataset for comparable evaluation of
misbehavior detection in VANETs,” in IEEE International Conference
on Communications (ICC). IEEE, 2020.
[43] R. Kozlica, S. Wegenkittl, and S. Hiränder, “Deep Q-learning versus
proximal policy optimization: Performance comparison in a material
sorting task,” in IEEE 32nd International Symposium on Industrial
Electronics (ISIE), 2023.
[44] A. Wegener, M. Piorkowski, M. Raya, H. Hellbrück, S. Fischer, and J.P. Hubaux, “TraCI: An interface for coupling road traffic and network
simulators,” in Proceedings of the 11th Communications and Networking
Simulation Symposium (CNS), 2008.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
