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
# [792] Robust AI-Driven Intrusion Detection and Defense for Next-Generation Consumer Services
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
编号：792
题名：Robust AI-Driven Intrusion Detection and Defense for Next-Generation Consumer Services
年份：2025
DOI：10.1109/tce.2025.3631965
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2025.3631965.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：时序、日志、KPI 与云原生异常检测
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\792.txt
- 原始字符数：56661
- 本次发送字符数：56661
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1544

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

Robust AI-Driven Intrusion Detection and Defense
for Next-Generation Consumer Services
Yufeng Li , Yang Li , Member, IEEE, Jing Nie , and Sezai Ercisli
Abstract— With the deep integration of 6G, the Internet
of Things, and artificial intelligence, this paper proposes an
intrusion detection and defense framework that combines robust
AI kernel reconstruction, a cross-layer collaborative perception
architecture, and a dynamic defense closed-loop mechanism
to address advanced persistent threats and dynamically evolving attacks targeting next-generation consumer services. First,
a lightweight detection model ATF-KDBC is designed based on
adversarial training and online knowledge distillation. Gradient
masking and noise injection are employed to enhance robustness against adversarial samples, while a drift-aware module
enables adaptive optimization under concept drift scenarios.
The model achieves accuracies of 99.25% and 99.84% on
the NSL-KDD and IoT-23 hybrid datasets, respectively, and
compresses the model size to 1.08 MB, representing a 97.6%
reduction compared with the BERT teacher model. Second,
a multidimensional attack chain analysis model is developed
based on a STHGN. By integrating semantic, structural, and
temporal features with a multi-head self-attention mechanism,
the model enables cross-layer threat tracing and millisecond-level
response, achieving an F1-score exceeding 97.0% on the DARPA
dataset. Furthermore, this study explores the construction of a
distributed CTIS network by integrating federated learning and
blockchain technology. Zero-knowledge proofs are employed to
ensure privacy preservation, while a Quality of Data and Quality
of Model scoring mechanism enables efficient and precise deployment of defense strategies. Experimental results demonstrate that
the proposed framework significantly outperforms traditional
methods in terms of robustness, environmental adaptability,
and computational efficiency, thereby providing both theoretical
support and a technical pathway for enhancing the resilience and
security of next-generation consumer services.
Index Terms— Artificial intelligence, consumer services, knowledge distillation, sixth-generation communication networks.

I. I NTRODUCTION
RIVEN by the rapid development of 6G and the Internet
of Things (IoT), along with the deep integration of cloud
computing, artificial intelligence, and big data analytics, the
consumer services sector is entering a new stage of digital

D

Received 18 August 2025; revised 29 September 2025 and 24 October 2025;
accepted 9 November 2025. Date of publication 12 November 2025; date of
current version 25 March 2026. (Corresponding authors: Yang Li; Jing Nie.)
Yufeng Li is with the College of Mechanical and Electrical
Engineering, Shihezi University, Shihezi 832003, China (e-mail:
20202109051@stu.shzu.edu.cn).
Yang Li and Jing Nie are with the College of Mechanical and Electrical Engineering, Shihezi University, Shihezi 832003, China, also with
Xinjiang Production and Construction Corps Key Laboratory of Modern
Agricultural Machinery, Shihezi 832003, China, and also with the Key
Laboratory of Northwest Agricultural Equipment, Ministry of Agriculture
and Rural Affairs, Shihezi 832003, China (e-mail: liyang328@shzu.edu.cn;
niejing19@shzu.edu.cn).
Sezai Ercisli is with the Faculty of Agriculture, Atatürk University, 25240
Erzurum, Türkiye (e-mail: sercisli@gmail.com).
Digital Object Identifier 10.1109/TCE.2025.3631965

transformation. Next-generation consumer services mark a
paradigm shift from traditional online services, characterized
by hyper-personalization, real-time interactivity, intelligent
automation, and seamless omnichannel experiences. These services have deeply penetrated critical modern-life scenarios—
such as real-time financial transactions, intelligent customer
delivery, context-aware delivery platforms, and immersive
social commerce [1]. This trend indicates that we are entering
a new era of digital consumption in which virtually anything
can be purchased online as a service via consumers’ electronic devices. However, the combination of ubiquity, technical
complexity, and operational criticality renders next-generation
consumer services high-value targets for Advanced Persistent
Threats (APTs) [2]. Security vulnerabilities in consumer electronics are evident through compromised smart home cameras
enabling unauthorized disclosure of personal privacy, wearable
IoT devices susceptible to unauthorized access of health data,
and in-vehicle telematics systems subjected to remote control
exploitation, with instances demonstrating critical security
flaws in connected devices [3]. Ensuring their security, privacy,
and resilience has moved beyond purely technical concerns to
become a fundamental prerequisite for sustainable development and the establishment of user trust in the digital era.
The cloud-native architectures, API-driven economy, and
deep AI integration underpinning next-generation consumer
services, while fostering business innovation, have also introduced multi-layer and cross-layer coupled security challenges
[4], [5], [6]. At the user-interaction layer, automated crawlers
that exfiltrate sensitive data and adversarially crafted phishing
attacks have resulted in annual losses exceeding $10 billion.
Lateral infiltration into business microservices and fraud targeting distributed transactions are further amplified and can
proliferate rapidly in decentralized architectures. Targeted
attacks on the AI-model layer are particularly severe because
they directly exploit vulnerabilities in conventional defense
mechanisms. [7], [8] while container escapes and supply-chain
poisoning at the infrastructure layer further magnify systemic
risk. These threats are dynamically evolving, coordinated
across layers, and can produce nonlinear escalations of
harm, thereby revealing fundamental limitations of detection
schemes that depend on static rules and shallow AI—
particularly with respect to robustness, correlation analysis,
and real-time responsiveness. There is an urgent need for a
new AI-driven detection-and-defense paradigm that integrates
adversarial robustness, cross-layer perception, and adaptive
decision-making [9].
Conventional intrusion-detection mechanisms exhibit three
structural deficiencies when confronted with the dynamic
threat environment of next-generation consumer services [10].

1558-4127 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

LI et al.: ROBUST AI-DRIVEN INTRUSION DETECTION AND DEFENSE FOR NEXT-GENERATION CONSUMER SERVICES

First, static rule-based schemes cannot adapt to continuously
evolving, cross-layer composite attacks and impose a substantial manual-maintenance burden. Second, traditional machinelearning models, while capable of detecting some anomalous
traffic, have insufficient representational capacity for highdimensional [11], heterogeneous data. Third, mainstream
deep-learning detectors exhibit reduced adversarial robustness,
limited adaptability, and compromised cross-layer correlations
despite high accuracy. They lack core robustness design,
effective mechanisms, and cross-layer intelligence fusion, failing to satisfy high precision, robustness, and low latency
requirements for next-generation consumer services [12], [13].
Current AI intrusion detection for consumer services is
vulnerable to adversarial attacks, noise, and concept drift.
Multi-dimensional attack chains are covert and cross-layer
correlated, impeding real-time accuracy and threat awareness.
This study introduces robust detection via core reconstruction, cross-layer perception, and dynamic defense closed-loop.
The main contributions of this paper are summarized as
follows:
• Proposes a lightweight detection model integrating adversarial training and knowledge distillation, employing
gradient masking and noise injection for robustness, and
featuring a drift-aware module for adaptive stability.
• Proposes a heterogeneous GNN-based model for crosslayer attack-chain analysis, integrating edge-cloud feature
extraction and adaptive task offloading to enable precise
attribution with millisecond response.
• Swarm learning enables a distributed threat intelligence network for cross-domain knowledge aggregation,
enhancing unknown threat detection. An uncertaintyestimation-driven hierarchical response dynamically triggers precise defensive actions, forming an autonomous
detection-decision-suppression loop.
Here is the structural outline of the remaining content:
Section II conducts a comprehensive review of existing literature; Section III introduces the comprehensive model and
its underlying framework; Section IV elaborates on the experimental investigations on individual components; Section V
presents the systematic analysis of performance metrics;
whereas Section VI delivers the concluding remarks and future
research directions.
II. R ELATED W ORK
Malware is a broad term referring to “malicious software.”
Such software can gain access to or infect a system without the
system owner’s knowledge. In this paper, we provide a brief
overview of various known types of malware to date, including
viruses, ransomware, botnets, adware, and others. In addition, we discuss the corresponding countermeasure—intrusion
detection. Li et al. [14] proposed an accelerated attack
correcting adversarial gradients with original images during
backpropagation, showing superior transferability over stateof-the-art attacks against undefended and defended models.
He et al. [15] introduced the momentum-enhanced PGD attack
(M-PGD) and applied it in adversarial training, significantly
enhancing model robustness. Huang et al. [16] developed
an adaptive step-size method (ATAS) that effectively mitigates overfitting in FGSM adversarial training. Evaluations

1545

on relevant datasets showed a marked improvement in model
robustness.
Knowledge distillation trains a robust teacher from
lightweight-generated
samples,
distilling
robustness
knowledge via probability distributions to a student model,
ensuring inherited robustness and maintained efficiency.
Wang et al. [17] addressed resource constraints of IoT
devices by proposing a lightweight intrusion detection
model, TBCLNN, which integrates bHHO-based feature
dimensionality reduction, Tied Block Convolution (TBC),
and an improved Self-Knowledge Distillation (SKD) loss.
This approach achieves over 99% accuracy on multiple
datasets while maintaining a compact model size and
low computational cost. Yang et al. [18] introduced the
LNet-SKD method to tackle network intrusion detection
challenges in resource-limited environments. By leveraging
the DeepMax module and self-knowledge distillation, LNetSKD reduces parameter count and computational cost while
outperforming existing techniques. Aljuhani et al. [19]
proposed a lightweight intrusion detection framework that
combines knowledge distillation, fuzzy logic, structured
pruning, and quantization to balance security and efficiency
on resource-constrained devices, achieving 98% accuracy
with significantly reduced model resource overhead.
Next-generation consumer services, with multi-layer architectures and massive data interactions, face cross-layer
attack vulnerabilities. A multi-dimensional attack-chain model
employs spatiotemporal graph neural networks and endpointnetwork dual-fusion for real-time threat propagation modeling.
This approach adapts to dynamic data drift and personalized behaviors, enabling precise defense from point detection
to global tracing, thereby ensuring system resilience and
user security. Wang et al. [20] addressed limitations in
early detection and transferability by proposing K-GetNID,
which employs heterogeneous temporal graphs (HTGraph) and
HTGNN models guided by knowledge to enable efficient intrusion detection. Hahn et al. [21] proposed a layered attack-chain
framework for cyber-physical systems using kill-chain metamodel, enabling causal chain analysis and cross-layer attack
tracing for multi-dimensional defense. Zhang et al. [22]
proposed PdGAT-ID for ICS intrusion detection, integrating
periodic features with spatiotemporal GAT, boosting F1 scores
by 1.55–5.51% on SWaT.
Next-gen consumer services, reliant on IoT, cloud, and big
data, face expanded attack surfaces. A decentralized threat
intelligence network enables real-time multi-source analysis,
dynamic updates, and cross-domain defense, enhancing APT
and ransomware response while ensuring system resilience and
data security. Homan et al. [23] introduces a decentralized
CTI exchange architecture leveraging blockchain technology,
with modularized communication pathways governed by the
Traffic Light Protocol (TLP) framework. However, it lacks
considerations for incentives, privacy, and confidentiality.
Jiang et al. [24] addressed privacy concerns in network threat
intelligence sharing by proposing the BFLS method, which
combines blockchain and federated learning to achieve secure
CTI sharing and high-accuracy threat detection. Juan et al. [25]
proposed a framework integrating privacy-enhancing technologies with federated processing, addressing information

1546

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

A minimax game between A-model and D-model is formulated: generator amplifies discriminator activations for
adversarial samples, while discriminator suppresses activations for synthetic data and enhances for authentic samples,
establishing competitive equilibrium. The game between the
A-model and the D-model can be expressed as:
min max E x∼Pr [D(x)] + E A(z)∼Pg [−D(A(z))]
A

D

(1)

Here, x denotes a real sample and z denotes a random
noise vector. The outputs of the A-model and D-model are
represented as A(z) and D(x), respectively. When the A-model
is fixed, the loss function can be expressed as follows:

loss(x, z) = D(x) − D A∗ (z)
(2)
Since D(x) remains constant when the D-model is fixed,
Equation (2) can be simplified to Equation (3). At this stage,
the A-model should minimize Equation (3) to establish a
minimax game between the a-model and the D-model.
loss(z) = −D ∗ (A(z))

Fig. 1. Robust intrusion detection framework based on adversarial training
and knowledge distillation.

asymmetry in CTI sharing, boosting dataset size and defense
accuracy while balancing confidentiality and sharing benefits.
III. M ODEL F RAMEWORK
A. Intrusion Detection Framework Integrating Adversarial
Training and Knowledge Distillation
1) Series Adversarial Training-Based Intrusion Detection Model Inspired by Generative Adversarial Networks
(GANs): We propose an online knowledge distillation–based
lightweight adversarial training model tailored for consumer
service platforms. The model is designed to mitigate threats
such as API abuse, which can cause service interruptions or
performance degradation. It is applicable to training diverse
intrusion detection systems (IDS), as illustrated in Figure 1.
The adversarial training adopts a framework inspired by
Generative Adversarial Networks (GANs). To enhance the performance of the intrusion detection system (IDS), we employ
an generator module (A-model) and a discriminator module
(D-model) to generate adversarial samples, which are subsequently used to train the IDS, enabling it to resist attack
samples effectively. Taking the distribution of normal samples
in the training set as the target distribution, the A-model
first receives random noise and maps it to samples that
closely approximate the distribution of normal data. A dualstage adversarial learnin architecture is implemented, where
the D-model computes the divergence between synthetic and
legitimate data distributions. The A-model iteratively adjusts
its parameters to minimize this divergence metric, forming an
adversarial equilibrium.

(3)

2) A Knowledge Distillation Framework Based on BERT
and CNN-BiLSTM: The adversarially trained BERT-based
binary classifier (teacher model) is compressed via lightweight
knowledge distillation for efficient deployment on resourceconstrained consumer service platforms. The framework
integrates a BERT teacher, CNN-BiLSTM student, and distillation process, with BERT automatically extracting relevant
features from network traffic to eliminate manual feature
engineering for intrusion detection [26]. BERT, a pretrained
deep neural network, substantially enhances intrusion detection efficiency and accuracy through large-scale pretraining.
It offers strong cross-domain adaptability and fine-tuning capabilities for task-specific optimization. The core architecture
employs a Transformer encoder with multi-head self-attention
and feed-forward neural networks (FFNN) for effective feature
representation.
a) Multi-head self-attention mechanism: Multi-head selfattention partitions input features into 8 parallel subspaces
(optimal via ablation studies), projecting them into query (Q),
key (K), and value (V) vectors. Each head computes attention
weights via Q-K similarity and aggregates V for feature extraction. Outputs are concatenated and linearly transformed to fuse
multi-perspective representations, enabling robust capture of
local correlations and global dependencies for high-accuracy
intrusion detection in network security systems. The computational formula is as follows:


QK T
Attention(Q, K , V ) = σ √
V
(4)
dk
MultiHead (Q, K , V )
= Concat ( head 1 , head 2 , . . . , head h ) · W O


Q
headi = Attention QWi , K WiK , V WiV

(5)
(6)

Here, σ denotes the softmax function, and Q, K , and V
represent the query, key, and value matrices, respectively.
The variable dk indicates the dimension of the key vectors.
Additionally, T denotes the transpose operation. The variable
Q
h represents the number of attention heads, while Wi , WiK ,
V
O
Wi , and W are learnable parameter matrices.

LI et al.: ROBUST AI-DRIVEN INTRUSION DETECTION AND DEFENSE FOR NEXT-GENERATION CONSUMER SERVICES

1547

b) Feed-forward neural network (FFNN): The FFNN
applies further transformations to the vector at each position.
The model implementation includes a pair of affine operations
combined with a rectified linear unit (ReLU) activation mechanism. This operation can be analytically described as:
F F N N (z) = max (0, z · W1 + b1 ) · W2 + b2

(7)

Here, z denotes the input to the FFNN layer. W1 and b1
represent the weight matrix and bias vector of the first fully
connected (FC) layer, respectively, while W2 and b2 denote
the weight matrix and bias vector of the second FC layer.
The output layer of the BERT model varies according
to the specific task. During the pretraining phase, this layer
is utilized to compute the loss for the masked language model
(MLM).
X

LM L M = −
log P xt | X \M
(8)
t∈M

Here, M denotes the set of masked positions, and X \M
represents the input sequence containing masked tokens. The
variable xt corresponds to the true value of the masked word
at index t.
Due to resource constraints on consumer service platforms,
the student model reduces computational complexity and
compresses size while preserving high intrusion detection
performance. The CNN-BiLSTM architecture combines
CNN for local feature extraction and BiLSTM for long-term
dependency capture, significantly enhancing detection
accuracy. [27]. As illustrated in Fig. 1, the model employs two
CNN layers with Batch Normalization and ReLU for efficient
feature extraction, enhancing stability and convergence.
Dropout mitigates overfitting. A Bi-LSTM layer captures
bidirectional dependencies, transforming spatial features to
temporal. A fully connected layer with sigmoid outputs binary
probabilities. This architecture integrates CNN, BN/ReLU, and
Bi-LSTM for high-accuracy intrusion detection with minimal
computational overhead on resource-constrained platforms.
B. Edge-Cloud Collaborative Multi-Dimensional Attack
Chain Analysis
Based on the knowledge distillation framework, a multidimensional attack chain analysis model is developed for
cross-layer threat tracing via edge-to-cloud architecture,
as shown in Fig. 2.
Edge nodes transmit intrusion features to the cloud for
global correlation analysis via a deep correlation engine.
The cloud aggregates updated models, redistributes them
with embedded attack patterns, and generates structured
attack chain evidence for threat intelligence sharing. We propose STHGN for multi-dimensional attack chain analysis,
which separately encodes semantic and structural features to
effectively extract spatial information. Specifically, it constructs sentences based on each node’s first-hop neighbors
and employs Word2Vec to learn the semantic features of
nodes. Structural features are represented via HGN for spatial modeling. Temporal dependencies are modeled by TGN,
and a multi-head self-attention mechanism fuses spatial and

Fig. 2. Next-generation edge-cloud collaborative multi-dimensional attack
chain analysis framework for consumer services.

temporal features to generate robust spatiotemporal embeddings, enabling comprehensive multi-dimensional attack chain
analysis.
X
X

L=
log P wt+ j | wt
(9)
wt ∈V −c≤ j≤c, j̸ =0

where V denotes the vocabulary, wt is the target word, wt+ j
is a context word,
 c represents the context window size,
and P wt+ j | wt denotes the probability of predicting the
context word wt given the target word wt+ j . This probability
is typically computed using the softmax function:


T
exp vw
·
v
w

t
t+ j

(10)
P wt+ j | wt = P
T ·v
exp vw
wt
w∈V

Here, vw represents the vector representation of w.
After semantic feature extraction, a Heterogeneous Graph
Neural Network (HGNN) is employed to capture the structural
characteristics of nodes. Unlike conventional Graph Convolutional Networks (GCNs), the HGNN [28] adopts a hierarchical
processing strategy that combines local neighborhood information with global topological structures, allowing it to
aggregate information according to the relative importance of
different neighbors. In structural feature extraction, STHGN’s
HGNN employs a hierarchical aggregation mechanism with
dual receptive fields based on one-hop neighbors and metapaths to capture both local and global structural information.
For a heterogeneous graph containing nodes such as users,
devices, and IP addresses, HGNN first captures local structures
(e.g., “user-device” direct connections) through the one-hop
neighbor receptive field. Subsequently, it integrates multihop path information (e.g., “user-device-IP address”) via the
meta-path-based receptive field. This hierarchical processing
strategy enables the model to dynamically adjust the receptive
field size, preserving local details while capturing global topological patterns. During each aggregation layer, HGNN utilizes

1548

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

graph convolution operations to perform weighted fusion of
neighboring node information, ensuring critical connections’
features are adequately preserved while suppressing the impact
of noisy links. In the attack chain, nodes such as users, devices,
and IP addresses contain diverse attributes, including user
activity logs, device fingerprints, and geographical locations.
Through hierarchical aggregation, the HGNN integrates these
heterogeneous node features into a unified representation
space.
Given a heterogeneous graph G, the goal of the HGN is
to process the message receptive fields C. There are two
types of message receptive fields: the first type is based
on one-hop neighbors, which considers directly connected
neighboring nodes during message passing. The second type
is based on meta-paths, where a set of receptive fields C can
be extracted according to predefined meta-path settings T P .
For a given heterogeneous graph G, let X l denote the node
representation at layer l, and C be the set of message receptive
fields extracted from G. Let t represent the target node. Then,
the representation X tl+1 at layer (l + 1)th can be obtained by
aggregating the messages from the neighbors X sl of t across
all receptive fields in C at layer l, i.e.:




l+1
(C)
(C)
l
l
X t ← HAggr Aggr
Encd
Xs , Xt
(11)
∀(s→t)∈C

∀C∈C

The above model can be divided into the following
components:


(C)
Mst ← Encd (C) X sl , X tl
(12)
n
o
(C)
(C)
X t ← Aggr(C) Mst | ∀(s → t) ∈ C
(13)
n
o
(C)
X tl+1 ← HAggr
X t | ∀C ∈ C
(14)
∀C∈C

In this formula, (s → t) ∈ C denotes a neighboring
node s of the target node t within a message receptive field
C ∈ C. Encd(·) represents a message encoding function that
extracts information from neighboring nodes X sl , encodes their
(C)
representations, and generates the message Ms . Aggr (·) is
a feature aggregation function that aggregates messages from
neighbors within each receptive field C ∈ C, while H Aggr (·)
denotes a hybrid aggregation function that integrates the
representations from all message receptive fields.
It is important to note that Aggr (·) and H Aggr (·) share the
same underlying operational function. The Aggr (·) function
processes messages within a single receptive field C, where
each input corresponds to the representation of an individual
neighboring node. In contrast, the H Aggr (·) function aggregates messages across multiple receptive fields C, where each
input corresponds to the aggregated representation of a specific
receptive field.
Given the inherent dynamism of cyberattacks, modeling
temporal information in the source graph is critical for
capturing evolving malicious activities. TGN [29] analyzes
time-series features—such as transaction timestamps and login
frequencies—to facilitate global temporal modeling. In the
temporal embedding generation phase, each edge timestamp
te is embedded into a vector te using positional encoding.
This method maps the timestamp into a high-dimensional

space through sine and cosine functions. Formally, for a given
timestamp te , the temporal embedding is computed as:
 


d/2
te
te
, cos
(15)
te = sin
100002i/d
100002i/d i=1
Here, d denotes the dimensionality of the embedding space,
and i denotes the index of the positional-encoding dimension.
In the time-aware information aggregation phase, the temporal feature h i (t) of each node vi is updated by integrating
information from its neighboring nodes. Specifically, the feature representation h i (t) of node vi at time t is updated
by aggregating the features of its neighbors along with the
temporal embeddings of the edges connecting them. For a
neighboring node v j and an edge ei j , the update rule is
expressed as:


h i (t) = AGG R E G AT E h j (t)∥tei j | v j ∈ N (vi )
(16)
In this equation, AGG R E G AT E represents the aggregation function, the symbol ∥ denotes the feature concatenation
operation, and N (vi ) denotes the set of neighboring nodes of
node v.
Finally, during the node-embedding update phase, the
embedding h i (t) of each node at the end of time step t is
updated to a new time-aware embedding. The update function
typically comprises a fully connected layer followed by an
activation function, which integrates the previous time-step
state with the current time-step features. The update equation
is expressed as:
h i (t + 1) = ReLU (W · h i (t) + b)

(17)

Through these steps, the TGN generates time-aware node
embeddings h i (t) that reflect the dynamic behavior and temporal evolution of nodes in the graph. A multi-head self-attention
mechanism further enhances these time-aware embeddings to
better capture long-term temporal dependencies.
To seamlessly integrate spatial features—derived from
semantic vectors obtained via Word2Vec and structural features captured by the HGN—with temporal features extracted
through the TGN, we employ a multi-head self- attention
mechanism. This design choice aims to ensure that the fused
spatiotemporal representations effectively capture temporal
dependencies among nodes while re- taining the rich information embedded in both spatial and temporal domains.
By leveraging multi-head self- attention, the model can attend
to diverse aspects of the spatiotemporal features from multiple
perspectives, thereby generating more accurate and robust
represen- tations for multi-dimensional attack chain analysis
and detection.
Formally, let the spatial vector X s , which concatenates the
Word2Vec-derived semantic features and the HGNN-extracted
structural features, and the temporal vector X t , obtained from
the TGN, represent the inputs to the fusion stage. For each
attention head h, we compute the query, key, and value
matrices as follows:
Q h = W Q h [X s ∥X t ],
K h = W K h [X s ∥X t ],
Vh = WVh [X s ∥X t ]

(18)

LI et al.: ROBUST AI-DRIVEN INTRUSION DETECTION AND DEFENSE FOR NEXT-GENERATION CONSUMER SERVICES

1549

where W Q h , W K h , and WVh are the learned projection matrices
for head h, and ∥ denotes concatenation.
Within the multi-head attention framework, the scaled
dot-product mechanism is employed to derive attention
weights for each individual head:
!
Q h K h⊤
Vh (19)
Attention h (Q h , K h , Vh ) = so f tmax
√
dk
where dk denotes the dimensionality of the key vectors. These
attention scores allow the model to assign varying weights
to different spatiotemporal features, thereby enabling it to
dynamically focus on the most relevant aspects.
i
h
H
Z = W O ∥h=1
Attention h (Q h , K h , Vh )
(20)
where W O denotes the learnable output projection matrix, and
H denotes the number of attention heads.
The final output Z represents the fused spatiotemporal
features, capturing diverse relationships across both temporal
and spatial dimensions. The multi-head attention mechanism
enhances the model’s capacity to learn complex spatiotemporal
patterns, thereby improving the performance of downstream
attack detection tasks. By modeling long-term dependencies
across time and space, this mechanism facilitates the detection
of slow, continuously evolving cyberattacks, which is essential
for identifying anomalies over extended time horizons.
C. Next-Generation Consumer Service Threat Intelligence
Sharing Network (CTIS)
Next-generation consumer services, which integrate emerging technologies such as big data, cloud computing, and 6G,
are confronted with increasingly severe cybersecurity challenges. To address these issues, a strategic defense framework
emphasizing proactive defense, traceability, and adversarial
resilience has been proposed [30]. Building on detection and
analysis, a threat intelligence sharing network architecture
is developed, primarily leveraging federated learning and
blockchain technologies [31]. This framework enables secure
CTI sharing via collaborative global model training, safeguarding confidential data. A trust-based evaluation framework
employs auditing entities to assess and filter suboptimal local
updates during aggregation, with credibility verified using
zero-knowledge proof (ZKP) protocols for robust validation.
Zero-knowledge proofs verify security feature authenticity
without exposing sensitive data, balancing privacy and security
in multi-device collaborative defense. The lightweight framework is feasible on resource-constrained consumer devices,
which are high-value attack targets. This mechanism enhances
detection and defense against advanced persistent threats while
securing user data, providing a reliable privacy solution for
next-generation consumer services. A visual representation of
the complete system architecture is provided in Figure 4.
Edge node clusters function as federated learning clients,
retaining private data and training models. Verifier nodes,
selected by reputation scores, rank local contributions per
iteration to identify the global model (GM), enabling secure
CTI sharing. Verifier trustworthiness is validated via zeroknowledge proof (ZKP) protocols. Cluster aggregation nodes
randomly aggregate top-quality models. Blockchain stores

Fig. 3. Distributed threat intelligence sharing and defense framework based
on federated learning and blockchain technologies.

ZKP outputs and transaction results. The Coordinator Smart
Contract (CSC) manages verification addresses, IPFS model
references, trust metrics, and iteration counts. The Verifier
Smart Contract (VSC) processes ZKP proofs, ensuring
robust network security through efficient CTI sharing. Smart
contracts enable secure sharing and verification of threat
intelligence through pre-defined automated rules. When a node
submits threat intelligence, the smart contract first verifies its
digital signature and data hash value to ensure that the intelligence source is trustworthy and has not been tampered with;
Subsequently, the contract triggers a multi node verification
mechanism based on PBFT consensus algorithm, requiring
at least 70% of trusted nodes to cross verify the intelligence
content. Only after the verification is passed, the intelligence
will be written into the blockchain and broadcasted to the
entire network. This mechanism protects node privacy through
zero knowledge proof technology. A core component of the
defense chain architecture is a blockchain-based consortium
trust setup, implemented atop the Dolus defense mechanism as
described in [32]. The defense chain evaluates peer-provided
detection and mitigation services using Quality of Detection
(QoD) and Quality of Mitigation (QoM) metrics, enabling
requesters to select high-quality domains. The architecture
integrates on-chain and off-chain components: IPFS serves as
decentralized off-chain storage for threat intelligence, while
blockchain anchors transactional records. Organizations share
a common IPFS instance, with oracles facilitating periodic
data interactions. On-chain chaincode retrieves IPFS-stored
details to compute QoD/QoM, with storage capacity scaling
dynamically to transaction volume and attack frequency. IPFS
hashes are referenced in chaincode for efficient peer-to-peer
data access. Service providers detect attacks, gather evidence,
and deploy mitigations; completed transactions with comprehensive details are appended to blockchain, enabling secure,
transparent CTI sharing among consortium members for robust
network security.
Upon attacks targeting federated peers, the Freatic runtimeenabled monitoring subcomponent tracks cloud network traffic
via SDN switches. The defensive architecture employs a

1550

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

dual-phase ensemble learning framework (Dolus-inspired) to
process traffic from malicious and legitimate perspectives.
The first phase uses multivariate Gaussian methods for
anomaly detection (e.g., connection exhaustion), identifying
multi-source attack patterns to distinguish attackers from
benign users, thereby enabling highly effective adversarial
pattern categorization in real-time for enhanced network security. Outlier detection is performed using multiple effective
multivariate detectors, each generating a set of hypotheses
H = {h 1 , h 2 , . . . , h n }. The combined result corresponds to
the hypothesis set described by the following equation. For
improved accuracy, a Bayesian voting scheme is employed,
which leverages the posterior probabilities of each hypothesis
to assess their likelihoods.
X
h(x)P(h | D)
(21)
F=
h∈H

The final ensemble result F consists of all hypotheses in H,
with each hypothesis h weighted by its posterior probability
P(h | D). The posterior probability is proportional to the
likelihood of the training data D given h multiplied by the
prior probability of h.
P(h | D) ∝ P(h)P(D | h)

(22)

Second-stage anomaly classification distinguishes significant events from false alarms via a simple classifier: consistent
multi-threshold outcomes indicate adversarial patterns, divergent results are classified as benign. A suspicion score,
combined with adversarial metadata (malicious entity, IP,
traffic volume), is stored in IPFS. The detection chaincode
computes and displays the QoD score on the UI, with provider
peers initiating attack detection upon service requests. Upon
receiving service requests, provider peers initiate attack detection. The attack detection time, combined with tmin (the
assumed minimum time required to detect or mitigate attacks)
and tmax (the assumed maximum time to detect or mitigate
attacks), is used to calculate a normalized detection time,
which in turn is utilized to estimate QoD. Let td′ denote the
normalized detection time based on the actual attack detection
time td . It is defined as:
td − tmin
(23)
td′ =
tmax − tmin
QoD estimate, prior to accounting for penalties and based on
the deadline tdeadline and the actual response time tr , is defined
as:
Pk S
n
1 X ai ∗ j=1 norm
k
A=
(24)
n
td′
i=1

The final Quality of Detection (QoD) calculation treats the
response time as the critical factor for score assignment. Let y
represent the penalty variable defined by the Watchdog, which
is applied when the response time exceeds the deadline. In this
context, y is set to 0.8, corresponding to a 20 % reduction in
the score. Expanding on Equation (25), the QoD is expressed
as:

A,
if tr ≤ tdeadline
QoD =
(25)
A · y, if tr > tdeadline

TABLE I
E XPERIMENTAL E NVIRONMENT

Following attack detection, the requester submits a mitigation request based on trust metrics. The detection module
synchronizes with mitigation for real-time threat characterization and response coordination. Candidate and trusted
mitigators participate, with chaincode automating strategy execution. Attack traffic is routed to QVMs, resource availability
verified, and response time reported. The chaincode analyzes
system resources, service latency, and detection performance
to compute Quality of Mitigation.
Let t′ denote the normalized time to mitigate an attack,
scaled within the range [0,1]. Let er represent the attack
recurrence rate, and Sr denote the success rate of the mitigator.
The Quality of Mitigation (QoM) is defined by the following
formula:
i=1
P

QoM =

· Sr
n
er · tm′

(26)

IV. E XPERIMENT
A. Experiments on Lightweight Models Based on Adversarial
Training and Knowledge Distillation
1) Experimental Setup: Performance evaluation of the
proposed framework across three components—intrusion
detection, multi-dimensional attack chain analysis, and threat
intelligence sharing—used large-scale intrusion datasets.
Hardware: AMD Ryzen 7 5800H, NVIDIA RTX 3070, 32GB
RAM, Windows 10.
The software platform was implemented using Python 3.8,
with TensorFlow 2.6.0 serving as the deep learning framework.
Wireshark was employed to convert specific raw flow files into
the desired format, while SplitCap (Version 2.1) was used for
rapid segmentation of the raw flows. Flow processing within
the system was performed using the Scapy Python package.
2) Dataset: Two public IoT datasets, NSL-KDD [32] and
IoT-23 [33], were employed to evaluate the proposed intrusion
detection model integrating adversarial training and knowledge
distillation.Both datasets contain raw network traffic data,
including diverse malicious traffic patterns from real IoT environments. The IoT-23 dataset, collected by the Stratosphere
Laboratory of CTU University, comprises 23 traffic capture
scenarios—20 from malware-infected IoT devices and 3 from
benign IoT devices, with device names recorded.
3) Evaluation Metrics: To evaluate the performance of the
proposed intrusion detection framework, we employed Accuracy, Precision, Recall, and F1-Score—metrics commonly
used in intrusion detection system (IDS) evaluation. These
metrics were computed as follows, where TP, FP, TN, and

LI et al.: ROBUST AI-DRIVEN INTRUSION DETECTION AND DEFENSE FOR NEXT-GENERATION CONSUMER SERVICES

1551

TABLE II
S AMPLE N UMBER OF T WO DATASET C ATEGORIES

Fig. 5. Comparison of three models on the combined IoT-23 and NSL-KDD
dataset.
TABLE III
T HE C OST OF T HREE M ODELS O N IoT-23 + NSL-KDD

TABLE IV
DARPA E3 DATASET D ESCRIPTION

Fig. 4.

Comparison of the three models on the NSL-KDD dataset.

FN represent true positives, false positives, true negatives, and
false negatives, respectively.
TP +TN
(27)
T P + T N + FP + FN
TP
Pr ecision =
(28)
T P + FP
TP
Recall =
(29)
T P + FN
2 × Precision × Recall
F1 − Scor e =
(30)
Precision + Recall
4) Experimental Results: Experimental evaluation on two
benchmark datasets confirms the ATF-KDBC framework’s
superior efficiency and accuracy over multiple baseline models, effectively demonstrating its enhanced performance for
intrusion detection systems in network security applications.
Experiments on NSL-KDD and IoT-23 datasets compare
BERT (teacher), CNN-BiLSTM (baseline), and ATF-KDBC
against state-of-the-art methods. Figure 4 presents NSL-KDD
results: BERT achieves 0.9936 accuracy and 0.9832 F1-score,
while ATF-KDBC attains 0.9871 accuracy and 0.9823
F1-score, significantly outperforming baselines. This validates ATF-KDBC’s enhanced intrusion detection efficacy for
resource-constrained network security applications.
In contrast, the proposed ATF-KDBC model closely follows,
exhibiting robust performance with an accuracy of 0.9925—
slightly lower than that of the BERT model—while achieving a
high F1-score of 0.9821. Notably, the original CNN-BiLSTM
model, which lacks knowledge distillation optimization,
Accuracy =

demonstrates comparatively weaker detection performance
among the three models, with an accuracy of 0.9687 and an
F1-score of 0.9395.
Comparative analysis reveals that the knowledge
distillation-enhanced KDBC model achieves performance
nearly indistinguishable from the teacher BERT model
while significantly outperforming the original CNN-BiLSTM
model. Quantitatively, the ATF-KDBC model achieves an
increase of 2.38 percentage points in classification accuracy
and a rise of 0.0426 in F1-measure, thereby substantiating
its superior performance and enhanced efficacy in adversarial
attack detection.
To further validate the model’s performance, this study
combined the IoT-23 and NSL-KDD datasets and conducted
experiments on the merged dataset. For the combined training
set, the total training time was 3.36 h, and the average GPU
utilization during training was 68%. The results, presented in
Figure 5, systematically compare the key performance metrics
of the three models. The teacher model (BERT) maintains the
lead, achieving an accuracy of 0.9987 and an exceptionally
high F1-score of 0.9987.
Following the BERT model is the proposed ATF-KDBC
model, a CNN-BiLSTM architecture enhanced through adversarial training and knowledge distillation. The ATF-KDBC
model exhibits strong performance on the combined dataset,
achieving an accuracy of 0.9984 and an F1-score of
0.9985, with only a marginal difference from the teacher
model. In contrast, the original CNN-BiLSTM model without
adversarial training and knowledge distillation demonstrates
comparatively weaker performance, with an accuracy of
0.9658 and an F1-score of 0.9696.

1552

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

TABLE V
C OMPARISON E XPERIMENTS

Comparative analysis of the experimental data indicates that
the ATF-KDBC model not only approaches the performance of
the teacher BERT model but also significantly outperforms the
original CNN-BiLSTM model. Specifically, the ATF-KDBC
model’s accuracy increases by 3.26 percentage points, and its
F1-score improves by 0.0289.
Due to limited computational resources on consumer platforms, lightweight models are evaluated for performance and
size. BERT (417.67 MB) achieves superior accuracy but is
bulky; CNN-BiLSTM (2.37 MB) and ATF-KDBC (1.08 MB)
are compact, with ATF-KDBC offering optimal efficiency for
resource-constrained intrusion detection deployments.
B. Experiment on Multi-Dimensional Attack-Chain Analysis
1) Dataset: The DARPA dataset [34] is a high-fidelity
cybersecurity dataset crafted to simulate complex enterprise
environments and advanced persistent threats (APTs).
It emphasizes multi-stage attacks within realistic network
architectures, capturing detailed host and network events
encompassing both benign and malicious activities. Given
our requirement for rich semantic information, we selected
the more comprehensive Trace, Theia, and Cadets subsets
for evaluation. Detailed dataset information is summarized in
Table IV.
2) Comparative Experiments: In this section, we evaluate
the performance of STHGN on three datasets and compare
it with prior detection methods. Table V presents the
experimental results, where STHGN consistently outperforms
competitors across the Trace, Cats, and Theia datasets,
achieving F1 scores exceeding 97%. By comparison, the
static-feature-based detector HOLMES attains an F1 score of
only 2.45%, the spatial-feature-based detector FLASH reaches
up to 95%, and the temporal-feature-based detector TGN
achieves approximately 95%. The early HOLMES detector,
based on the APT lifecycle model [35], employs a set of TTP
rules to identify patterns in the graph. However, these rules
often match benign behavior, resulting in a high false positive
rate and thus high recall but low precision (below 5%).
Threatrace, relying solely on GraphSAGE for spatial features,
neglects semantic and spatiotemporal information, resulting
in poor detection (F1 < 50%). FLASH enhances spatial
feature extraction by combining Word2Vec semantic features
with GCN structural features. Spatiotemporal detectors
Unicorn and AnoGraph model temporal frequencies with
low-dimensional features, yielding average F1 < 50% due
to insufficient spatial context. The traditional TGN model
outperforms them (F1 > 90%) by effectively capturing node

spatial information. STHGN achieves the highest performance
(F1 > 98%) through integrated spatiotemporal feature fusion,
generating highly discriminative representations for robust
intrusion detection in network security applications.
V. C ONCLUSION AND F UTURE W ORK
This study proposes a resource-efficient intrusion detection framework based on adversarial training and knowledge
distillation to address the limitations of existing algorithms
in computational efficiency and robustness. The framework
integrates an edge-cloud collaborative spatio-temporal heterogeneous graph network (STHGN) to analyze multidimensional
attack chains, ensuring data privacy preservation and mitigating poisoning risks. Experimental results demonstrate
that the proposed architecture achieves significant computational resource savings while enhancing detection and defense
robustness. This work provides a robust security solution for
next-generation consumer service platforms, establishing its
practical applicability through quantitative evaluations. The
methodology advances state-of-the-art intrusion detection by
combining adversarial resilience mechanisms with distributed
threat intelligence sharing, offering critical implications for
secure consumer electronics ecosystems.
R EFERENCES
[1] Z. Chen, J. Xu, Y. Guo, and J. Hao, “Joint optimization of multiUAV assisted computation offloading and topological task routing for
consumer IoT emerging businesses,” IEEE Trans. Consum. Electron.,
p. 1, 2025, doi: 10.1109/TCE.2025.3598638.
[2] G. Xie, X. Xu, H. Gao, and M. Iqbal, “HASGDetector: An effective hostbased intrusion anomaly detection framework with large-scale attribute
heterogeneous graphs,” IEEE Trans. Consum. Electron., vol. 71, no. 3,
pp. 7523–7538, Aug. 2025.
[3] M. J. Baucas, P. Spachos, and S. Gregori, “Private blockchain-based
wireless body area network platform for wearable Internet of Thing
devices in healthcare,” in Proc. IEEE Int. Conf. Commun., May 2023,
pp. 6181–6186.
[4] Y. Li, J. Yang, Z. Zhang, J. Wen, and P. Kumar, “Healthcare data quality
assessment for cybersecurity intelligence,” IEEE Trans. Ind. Informat.,
vol. 19, no. 1, pp. 841–848, Jan. 2023.
[5] Y. Li, J. Yang, and J. Wen, “Entropy-based redundancy analysis
and information screening,” Digit. Commun. Netw., vol. 9, no. 5,
pp. 1061–1069, Oct. 2023.
[6] J. Nie, K. Wu, Y. Li, J. Li, and B. Hou, “Advances in hyperspectral
remote sensing for precision fertilization decision-making: A comprehensive overview,” Turkish J. Agricult. Forestry, vol. 48, no. 6,
pp. 1084–1104, Dec. 2024.
[7] J. Nie et al., “Towards intent-based network management: Intentoptimized cross-shard transactions and malicious node detection
in blockchain system,” IEEE Internet Things J., p. 1, 2025,
doi: 10.1109/JIOT.2025.3601827.

LI et al.: ROBUST AI-DRIVEN INTRUSION DETECTION AND DEFENSE FOR NEXT-GENERATION CONSUMER SERVICES

[8] Y. Li, M. Wei, J. Nie, S. Ercisli, K. Fang, and T. R. Gadekallu,
“Enhancing DDoS defense in the Internet of Energy through
intelligent task scheduling framework,” IEEE Netw., p. 1, 2025,
doi: 10.1109/MNET.2025.3589717.
[9] V. J. Prakash, S. A. A. Vijay, G. Sundaram, M. Driss and W. Boulila,
“Efficient hierarchical multimodal graph neural networks for AI-driven
decision-making in consumer data,” IEEE Trans. Consum. Electron.,
vol. 71, no. 3, pp. 8850–8863, Aug. 2025.
[10] H. Byeon et al., “Post-quantum secure blockchain framework for edgebased mobile task offloading in consumer electronics and IoTs,” IEEE
Trans. Consum. Electron., vol. 71, no. 3, pp. 8407–8416, Aug. 2025.
[11] M. Y. Saeed, J. He, N. Zhu, M. Farhan, M. M. Alnfiai, and J. Fang,
“Agents incorporating XRL based method for threat detection in mobile
edge networks for consumer electronics,” IEEE Trans. Consum. Electron., vol. 71, no. 3, pp. 8829–8838, Aug. 2025.
[12] S. Mahmood, M. Gohar, S.-J. Koh, M. U. Tariq, and A. Ghani,
“Application level trust authority (APPLETA) for resource-constrained
edge devices in IoT and 6G,” IEEE Trans. Consum. Electron., vol. 71,
no. 2, pp. 4934–4948, May 2025.
[13] X. Zhao, Y. Shi, S. Chen, J. Liu, B. Ji, and S. Mumtaz, “MAPSM:
Mobility-aware proactive service migration framework for mobile-edge
computing in consumer Internet of Vehicles,” IEEE Trans. Consum.
Electron., vol. 71, no. 2, pp. 3753–3766, May 2025.
[14] J.-W. Li, W.-Z. Shao, Y.-B. Sun, L.-Q. Wang, Q. Ge, and
L. Xiao, “Boosting adversarial transferability via relative feature
importance-aware attacks,” IEEE Trans. Inf. Forensics Security, vol. 20,
pp. 3489–3504, 2025.
[15] C. He et al., “Boosting the robustness of neural networks with M-PGD,”
in Proc. Int. Conf. Neural Inf. Process. Cham, Switzerland: Springer,
2022, pp. 562–573.
[16] Z. Huang et al., “Fast adversarial training with adaptive step size,” IEEE
Trans. Image Process., vol. 32, pp. 6102–6114, 2023.
[17] Z. Wang, R. Zhou, S. Yang, D. He, and S. Chan, “A novel
lightweight IoT intrusion detection model based on self-knowledge
distillation,” IEEE Internet Things J., vol. 12, no. 11, pp. 16912–16930,
Jun. 2025.
[18] S. Yang, X. Zheng, Z. Xu, and X. Wang, “A lightweight approach
for network intrusion detection based on self-knowledge distillation,”
in Proc. IEEE Int. Conf. Commun., May 2023, pp. 3000–3005.
[19] A. Aljuhani, A. Alamri, and A. Jolfaei, “Lightweight fuzzy-driven
intrusion detection for consumer life-tech applications,” IEEE Trans.
Consum. Electron., vol. 71, no. 1, pp. 2347–2349, Feb. 2025.
[20] M. Wang, N. Yang, and N. Weng, “K-GetNID: Knowledge-guided
graphs for early and transferable network intrusion detection,” IEEE
Trans. Inf. Forensics Security, vol. 19, pp. 7147–7160, 2024.
[21] A. Hahn, R. K. Thomas, I. Lozano, and A. Cardenas, “A multi-layered
and kill-chain based security analysis framework for cyber-physical
systems,” Int. J. Crit. Infrastruct. Protection, vol. 11, pp. 39–50,
Dec. 2015.
[22] D. Zhang, M. Wang, Y. Bu, J. Yu, and L. Yang, “PdGAT-ID: An
intrusion detection method for industrial control systems based on
periodic extraction and spatiotemporal graph attention,” Comput. Secur.,
vol. 149, Feb. 2025, Art. no. 104210.
[23] D. Homan, I. Shiel, and C. Thorpe, “A new network model for cyber
threat intelligence sharing using blockchain technology,” in Proc. 10th
IFIP Int. Conf. New Technol., Mobility Secur. (NTMS), Jun. 2019,
pp. 1–6.
[24] T. Jiang, G. Shen, C. Guo, Y. Cui, and B. Xie, “BFLS: Blockchain and
federated learning for sharing threat detection models as cyber threat
intelligence,” Comput. Netw., vol. 224, Apr. 2023, Art. no. 109604.
[25] J. R. Trocoso-Pastoriza et al., “Orchestrating collaborative cybersecurity:
A secure framework for distributed privacy-preserving threat intelligence
sharing,” 2022, arXiv:2209.02676.
[26] W. Serrano, “CyberAIBot: Artificial intelligence in an intrusion detection
system for CyberSecurity in the IoT,” Future Gener. Comput. Syst.,
vol. 166, May 2025, Art. no. 107543.
[27] S. Li, Y. Cao, G. Peng, M. Li, W. Sun, and L. Chen, “Efficient intrusion
detection for in-vehicle networks using knowledge distillation from
BERT to CNN-BiLSTM,” IEEE Trans. Inf. Forensics Security, vol. 20,
pp. 6398–6412, 2025.
[28] Y. Gao et al., “HGNAS++: Efficient architecture search for heterogeneous graph neural networks,” IEEE Trans. Knowl. Data Eng., vol. 35,
no. 9, pp. 9448–9461, Sep. 2023.

1553

[29] A. Sang et al., “STGAN: Detecting host threats via fusion of spatial–
temporal features in host provenance graphs,” in Proc. ACM Web Conf.,
Apr. 2025, pp. 1046–1057.
[30] S. Duan et al., “Distributed artificial intelligence empowered by endedge-cloud computing: A survey,” IEEE Commun. Surveys Tuts., vol. 25,
no. 1, pp. 591–624, 1st Quart., 2023.
[31] S. M. Hasan, A. M. Alotaibi, S. Talukder, and A. R. Shahid, “Distributed
threat intelligence at the edge devices: A large language model-driven
approach,” in Proc. IEEE 48th Annu. Comput., Softw., Appl. Conf.
(COMPSAC), Jul. 2024, pp. 1496–1497.
[32] S. Purohit et al., “Cyber threat intelligence sharing for co-operative
defense in multi-domain entities,” IEEE Trans. Depend. Secure Comput.,
vol. 20, no. 5, pp. 4273–4290, Sep. 2023.
[33] H. Alfares and O. Banimelhem, “Comparative analysis of machine
learning techniques for handling imbalance in IoT-23 dataset for intrusion detection systems,” in Proc. 11th Int. Conf. Internet Things, Syst.,
Manage. Secur. (IOTSMS), Sep. 2024, pp. 112–119.
[34] M. M. Anjum, S. Iqbal, and B. Hamelin, “Analyzing the usefulness of
the DARPA OpTC dataset in cyber threat detection research,” in Proc.
26th ACM Symp. Access Control Models Technol., Jun. 2021, pp. 27–32.
[35] H. Li et al., “MIRDETECTOR: Applying malicious intent representation for enhanced APT anomaly detection,” Comput. Secur., vol. 157,
Oct. 2025, Art. no. 104588.
Yufeng Li received the M.S. degree in mechanical
engineering and automation from Shihezi
University, Shihezi, China, in 2023, where he is
currently pursuing the Ph.D. degree in agricultural
engineering with the College of Mechanical and
Electrical Engineering.
His research interests include artificial intelligence
and electronic communication technology.

Yang Li (Member, IEEE) received the M.S. degree
in electrical engineering from Dalian University of
Technology, Dalian, China, in 2016, and the Ph.D.
degree in information and communication engineering from Tianjin University, Tianjin, China, in 2023.
He is currently an Associate Professor with the
College of Mechanical and Electrical Engineering,
Shihezi University; also with Xinjiang Production
and Construction Corps Key Laboratory of Modern
Agricultural Machinery, Shihezi; and also with the
Key Laboratory of Northwest Agricultural Equipment, Ministry of Agriculture and Rural Affairs, China. His research interests
include image processing, the IoT, and data quality assessment.
Jing Nie received the M.S. degree in mechatronic
engineering from Xinjiang University, Ürümqi,
China, in 2007, and the Ph.D. degree in mechatronic
engineering from Shihezi University, Shihezi, China,
in 2023.
He is currently a Professor with the College of
Mechanical and Electrical Engineering, Shihezi
University; also with Xinjiang Production and
Construction Corps Key Laboratory of Modern
Agricultural Machinery, Shihezi; and also with the
Key Laboratory of Northwest Agricultural Equipment, Ministry of Agriculture and Rural Affairs, China. His research interests
include deep learning, image processing, and agricultural IoT applications.
Sezai Ercisli received the Ph.D. degree in agricultural engineering from Atatürk University, Erzurum,
Türkiye, in 1996.
He is currently a Professor with the Department
of Horticulture, Faculty of Agriculture, Atatürk University. His research interests include the modern
technology in agricultural production, such as deep
learning, image processing, and the Internet of
Things.
PAPER_TEXT
