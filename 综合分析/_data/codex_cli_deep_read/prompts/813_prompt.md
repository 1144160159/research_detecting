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
# [813] STELLAR: Similarity-Based Satellite Federated Learning for Malicious Traffic Recognition
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
编号：813
题名：STELLAR: Similarity-Based Satellite Federated Learning for Malicious Traffic Recognition
年份：2026
DOI：10.1109/tifs.2026.3659044
来源：IEEE Transactions on Information Forensics and Security
PDF：paper/10.1109_TIFS.2026.3659044.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：恶意流量、暗网与攻击检测
相关性：中相关，分数 9
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\813.txt
- 原始字符数：71601
- 本次发送字符数：71601
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
1766

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

STELLAR: Similarity-Based Satellite Federated
Learning for Malicious Traffic Recognition
Yubo Li , Li Zhang , Kai Li, and Haoru Su
Abstract—Resource constraints and data heterogeneity pose
significant hurdles for malicious traffic detection in satellite networks. To address this, we propose STELLAR, a similarity-based
federated learning framework tailored for efficient space computing. STELLAR introduces a multi-dimensional similarity metric
to dynamically select representative nodes, effectively eliminating computational redundancy. Furthermore, it ensures system
robustness and trust through a time-window asynchronous protocol with staleness compensation and a lightweight proxy-based
authentication scheme. Evaluations demonstrate that STELLAR
outperforms specialized baselines, reducing network-wide energy
consumption by 77%–80% while achieving 99.72% detection
accuracy in heterogeneous Non-IID environments. These results
validate STELLAR as a sustainable and robust solution for
distributed security in resource-constrained satellite networks.
Index Terms—Federated learning, LEO satellite networks,
intrusion detection, multi-dimensional similarity, asynchronous
aggregation, lightweight authentication.

I. I NTRODUCTION
ATELLITE networks, operating in open space environments, are inherently vulnerable to malicious attacks.
Satellite nodes are characterized by strictly limited computing
power, storage capacity, and energy supply, coupled with
low-bandwidth and unstable inter-satellite links. Furthermore,
satellite traffic differs sharply from terrestrial Internet patterns,
dominated by specialized services such as remote sensing and
meteorological data. Attackers often exploit these characteristics to launch energy-targeted strikes (e.g., during low-energy
eclipse periods). These constraints hinder the deployment of
computationally intensive terrestrial detection models, such as
complex deep learning architectures, directly onto satellites.
Deep learning methods have adapted neural networks for
satellite environments with promising performance; however,
they often fail to meet practical requirements due to resource
bottlenecks [1]. A critical hurdle is the scarcity of open,
authentic, and diverse satellite traffic datasets. Emerging applications and novel attack vectors lead to high rates of unknown
traffic, rendering models trained on outdated or terrestrial
datasets ineffective. Moreover, transmitting large-scale raw
traffic to terrestrial ground stations for centralized training incurs prohibitive communication overhead and latency,

S

Received 26 July 2025; revised 30 December 2025; accepted 23 January
2026. Date of publication 28 January 2026; date of current version 5 February
2026. This work was supported by the Beijing Municipal Natural Science
Foundation under Grant L222048. The associate editor coordinating the
review of this article and approving it for publication was Prof. Guowen Xu.
(Corresponding author: Li Zhang.)
The authors are with the College of Computer Science, Beijing University of Technology, Beijing 100124, China (e-mail: yubolee1217@163.com;
zl hlj@126.com).
This article has supplementary downloadable material available at
https://doi.org/10.1109/TIFS.2026.3659044, provided by the authors.
Digital Object Identifier 10.1109/TIFS.2026.3659044

raising significant concerns regarding privacy, data confidentiality, and timeliness. Training models on satellites can
address the transmission overhead caused by dataset updates,
but even lightweight continuous online learning imposes a
severe strain on scarce space resources.
Federated Learning (FL) offers a paradigm shift by
enabling data-localized collaborative training, which mitigates data scarcity and transmission overhead by aggregating
distributed on-board insights, theoretically suiting capabilitylimited nodes. However, directly applying terrestrial FL
frameworks to satellite networks faces unresolved challenges:
data distribution heterogeneity (Non-IID), low communication
efficiency, and security vulnerabilities. For instance, many
algorithms require frequent transmission of large models to
a central server [2], yet satellite links—characterized by
high latency and dynamic topology—render such large-scale
exchange inefficient. Although local training preserves privacy,
it suffers from uneven dataset distributions and feature skew,
leading to slow convergence or model divergence. Crucially,
neighboring satellites often share similar coverage and mission tasks, leading to highly redundant training that incurs
unnecessary energy expenditure. Additionally, traditional synchronous aggregation protocols are fragile; a few straggler
nodes caused by link instability can stall the entire training
process. Finally, while most frameworks focus on data privacy,
they often overlook participant trustworthiness. In the open
space environment, node hijacking is a tangible risk, as the
inclusion of a single malicious node can poison the global
model.
To address these challenges, we propose STELLAR:
Similarity-based saTellite fEderated Learning for maLicious
trAffic Recognition. Tailored for resource-constrained satellite networks, STELLAR leverages collaborative federated
learning to identify malicious traffic. It effectively mitigates single-node data limitations while significantly reducing
communication and computational overhead. Representative
nodes are selected via data similarity to reduce computational
overhead, while multi-layer aggregation coordinated by an
asynchronous protocol minimizes costs and ensures survivability against stragglers. It employs a lightweight authentication
scheme utilizing cryptography to authenticate entities, form
keys, and ensure participant trustworthiness and transmission
security.
The main innovations and contributions of this paper are
summarized as follows:
(1) Multi-dimensional data similarity measurement for
satellite robustness: We propose a composite metric
that fuses model parameters, convergence patterns, and
prediction behaviors. This metric accurately character-

1556-6021 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

LI et al.: STELLAR: SIMILARITY-BASED SATELLITE FL FOR MALICIOUS TRAFFIC RECOGNITION

1767

izes intrinsic correlations within data distributions and
functions as a semantic filter, ensuring robust grouping
even in the presence of high transmission noise in
satellite links.
(2) Energy-efficient representative mechanism: We introduce an adaptive grouping-based Representative Node
mechanism to mitigate redundant computation and
reduce network-wide energy consumption.
(3) Asynchronous protocol for survivability under instability: We design a time-window-based asynchronous
aggregation protocol equipped with a staleness compensation mechanism. This design enables the system to effectively leverage late updates and maintain
model convergence despite severe delays or interruptions, ensuring system survivability in harsh space
environments.
(4) Orbit-adaptive quality-aware hierarchical aggregation: We develop an aggregation mechanism tailored to
the dynamic orbital topology. By incorporating a qualityaware weighting strategy, it balances model accuracy
with data scale, guaranteeing global model stability even
when individual satellites provide low-quality updates
due to resource fluctuations.
(5) Lightweight trust via proxy-based authentication:
We devise a proxy-based satellite node authentication scheme to address strict security requirements
and environmental constraints. It achieves secure node
authentication and key negotiation with minimal latency
and computational overhead, ensuring both framework
security and operational efficiency.

unbearable energy costs on satellites. STELLAR addresses this
via similarity-based representative selection to significantly
reduce energy consumption while ensuring convergence.
Clustering methods (e.g., CFL [13], FeSEM [14]) improve
FL convergence on Non-IID data via personalized modeling.
However, they fundamentally rely on full client participation—requiring every node to continuously perform local
training for clustering—which is impractical for energystarved satellite networks. Similarly, Hierarchical FL [15]
enhances cloud-edge efficiency but depends on static edge
l
| l
servers and simple size-weighted averaging ( |D
|D| w ). In contrast, STELLAR adapts to the dynamic orbital topology
through quality-aware weighting and representative rotation.
Beyond efficient training, ensuring the integrity of the collaborative process is equally critical. In the domain of satellite
security, Abdrabou et al. designed cross-orbital key agreement
with link switching prediction, maintaining stable short-term
delays in inter-satellite switching [16] while imposing heavy
computational burdens on satellite payloads.
To address satellite computational and storage constraints,
lightweight authentication is key. Symmetric encryption-based
protocols have been extensively explored, such as the constellation maintenance schemes by Huang et al. [17] and the LEO
identity authentication methods by Zhu et al. [18], [19], which
utilize pre-computation to reduce overhead. Other lightweight
approaches include non-interactive elliptic curve cryptography
[20], hash-XOR hybrid frameworks [21], and proxy signature
verification [22]. Building on these foundations, this paper
designs an authentication scheme to further reduce overhead.

II. R ELATED W ORK

III. STELLAR: S IMILARITY-BASED S ATELLITE
F EDERATED L EARNING F RAMEWORK

Deep learning approaches, such as BiLSTM [3],
BiTCN+MHSA [4], and GAN+RF [5], have achieved
breakthroughs in terrestrial malicious traffic detection through
automatic feature extraction. However, these methods typically
incur high computational complexity and require substantial
resource consumption.
Due to the unique characteristics of satellite networks,
terrestrial methods are ill-suited for direct deployment. While
recent works have explored neural network optimization for
satellite environments [6], [7], their simulation scenarios often
oversimplify the dynamic topology of integrated satelliteterrestrial networks [6], or they exhibit excessive complexity
that hinders on-board deployment [7].
Federated learning (FL) enables collaborative training while
preserving data locality. Early satellite FL works [8], [9]
proposed distributed intrusion detection systems but failed
to address the Non-IID nature of satellite traffic, leading to
performance degradation. Recent advances have incorporated
anti-adversarial mechanisms [10], mesh architectures [11],
and synthetic data generation [12]. Nevertheless, these methods face several limitations: (1) performance deterioration
when the proportion of malicious participants is high [10];
(2) difficulties in assessing node trust [11]; and (3) risks of
feature leakage combined with a neglect of orbital dynamics
[12]. Critically, most existing approaches assume full participation or frequent synchronous updates, which imposes

A. Design Objectives and Problem Formulation
STELLAR aims to establish an effective malicious traffic
detection system for resource-constrained satellite networks.
To achieve this, we adopt Federated Learning (FL) as the
training paradigm, which enables satellites to collaboratively
train a detection model without centralizing raw data. Within
the FL framework, STELLAR is designed to fulfill three
objectives:
Objective 1: Energy Efficiency with Accuracy Preservation. Given the severe energy constraints of satellite platforms,
the framework must minimize computational and communication resource consumption while maintaining detection
accuracy:
S T ELLAR
min Etotal
,

s.t.

Accuracy ≥ ηacc

(1)

S T ELLAR
where Etotal
denotes the total energy consumption, and
ηacc is the target accuracy threshold.
This objective is addressed by the similarity-based satellite
selection strategy (Section III-D), which groups satellites with
similar data distributions and selects representative nodes
for training, significantly reducing the number of active
participants.

1768

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

Fig. 1. Stellar framework architecture.

Objective 2: Convergence Guarantee. The global model
must converge to an -stationary point despite partial participation and communication instability:

C. Lightweight Detection Model

T −1

1X
Ek∇F(wt )k2 ≤ 
T

Component ensures participant trustworthiness via proxybased verification.
Additionally, STELLAR employs an asynchronous aggregation protocol with staleness compensation to enhance
robustness against intermittent LEO satellite links.
As shown in Fig. 1, the core learning modules form the
federated learning processing unit. The Data Foundation Component supports the Model Detection and Adaptive Grouping
Components with data; the latter two interact bidirectionally
for coordinated training; the Adaptive Grouping Component
passes results to the Hierarchical Aggregation Component for
global model aggregation, which feeds back parameters to the
Model Detection Component, forming a complete federated
learning loop. The Security Authentication Component serves
as an independent security assurance layer, authenticating
nodes and encrypting communications throughout the framework.
The following subsections elaborate on the key components
(excluding the data foundation).

(2)

t=0

where F(·) denotes the global loss function, wt is the global
model parameter at round t, and T represents the total number
of training rounds.
This objective is addressed by the quality-aware hierarchical aggregation mechanism (Section III-E) and the asynchronous aggregation protocol with staleness compensation
(Section III-F), which ensure stable convergence under heterogeneous data and intermittent links.
Objective 3: Security Guarantee. Operating in an open
space environment, the framework must ensure: (a) only
authenticated satellites participate in training; and (b) model
parameters are protected during transmission.
This objective is addressed by the lightweight LASS-PN
authentication protocol (Section III-G), which achieves secure
node authentication and key negotiation with minimal computational overhead.
The Core Challenge. Objectives 1 and 2 are inherently
conflicting. Standard FL requires all N satellites to train every
round, achieving convergence but imposing prohibitive energy
FedAvg
costs (Etotal
= T · N · eact ). The key question STELLAR
addresses is: What is the minimum number of active satellites R̄
that still guarantees both convergence and detection accuracy?
B. Framework Architecture
To address the objectives in Section III-A, STELLAR
integrates five core components (Fig. 1). The Data Foundation Component manages satellite traffic and states. The
Model Detection Component implements a lightweight neural network for traffic recognition. To balance energy and
convergence, the Lightweight Adaptive Grouping Component groups similar satellites to select representatives. The
Hierarchical Aggregation Component executes a three-level
update strategy (intra-orbital, ground station, global) with
quality-aware weighting. Finally, the Security Authentication

In STELLAR, representative nodes train the base model
while others utilize it for detection. To balance recognition
capability with resource constraints, we adopt a threelayer neural network architecture (Fig. 2) with only 3,682
parameters.
Parameterized as
f (x; w), the model processes
20-dimensional traffic features through an expand-thencontract structure (20 → 64 → 32 → 2). It employs Batch
Normalization (BN) for stability, ReLU activation for nonlinearity, and Dropout to prevent overfitting. The network
is trained by minimizing the standard cross-entropy loss.
Future work may explore more advanced architectures, but
this lightweight design currently meets the dual requirements
of accuracy and efficiency.
D. Similarity-Based Representative Selection
Addressing Objectives 1 and 2. To reduce active satellites
(R̄) while maintaining convergence, we group satellites with
similar data and select representatives. This simultaneously
addresses:
• Objective 1 (Energy): Reduces R̄ from N to M (number
of groups)
• Objective 2 (Convergence): Bounded bias ensures convergence is preserved
Key Intuition. Satellites with similar traffic distributions
tend to produce similar optimization signals. Therefore, one
representative can approximate the update of a group of highly
similar satellites, enabling us to reduce the number of active
trainers while preserving convergence.
Formal Guarantee. This intuition is formalized in the
theoretical analysis (Section III-I) via a similarity–gradient
assumption and a representative-bias bound, which together
justify similarity-based grouping and representative selection
under Non-IID data and intermittent links.
1) Multi-Dimensional Similarity Metric: Direct distributional distance computation is infeasible. We infer via three
proxies:

LI et al.: STELLAR: SIMILARITY-BASED SATELLITE FL FOR MALICIOUS TRAFFIC RECOGNITION

1769

Fig. 2. Malicious traffic detection model architecture (20 → 64 → 32 → 2).

a) Model parameter similarity: Rationale: Similar data
yields similar parameters.
Raw cosine similarity (not rescaled).
Simraw
param (i, j) =

|Θ|
X

wk ·

k=1

vec(θik ) · vec(θkj )
kvec(θik )k · kvec(θkj )k

(3)

where θik and θkj are k-th layer parameters of satellites i and j
respectively, |Θ| is the number of model layers, vec(·) denotes
matrix vectorization operation, P
wk is the weight coefficient for
the k-th layer with wk ≥ 0 and |Θ|
k=1 wk = 1, and deeper layers
are typically assigned higher weights as they better reflect data
distribution characteristics.
Rescaling to [0, 1] (for consistency with other metrics).
Since the cosine similarity in Eq. (3) lies in [−1, 1], we linearly
rescale it to [0, 1]:
Simraw
param (i, j) + 1
(4)
2
For computational efficiency, model parameter similarity
calculation is optimized by: (1) selecting key weight parameters while ignoring biases and batch normalization parameters;
(2) normalizing parameters to reduce dimensional effects.
b) Training loss dynamics similarity: Rationale: Similar
data distributions tend to induce similar loss decrease trends,
which serve as a lightweight proxy for convergence behaviors.
Raw cosine similarity (not rescaled)
Sim param (i, j) =

PE−1

(Lie −Lie+1 )(Lej −Le+1
)
j
qP
E−1 e
e+1 2
e+1 2
)
)
e=1 (Li −Li
e=1 (L j −L j

e=1
Simraw
loss (i, j) = √PE−1 e

(5)

where Lie is the local loss value of satellite i after the e-th local
epoch and E is the number of local epochs.
Rescaling to [0, 1] (for consistency with other metrics).
Since the cosine similarity in Eq. (5) lies in [−1, 1], we linearly
rescale it to [0, 1]:
Simraw
loss (i, j) + 1
(6)
2
c) Prediction behavior similarity: Rationale: Similar
data yields similar predictions.
Hellinger-based similarity (already in [0, 1]).
Simloss (i, j) =

K

Sim pred (i, j) = 1 −

1 X 1
√ ·
K
2

k=1
v
u C 
2
uX p
p
t
ŷi,k,c − ŷ j,k,c
c=1

(7)

where ŷi,k,c represents satellite i’s model prediction probability
for class c on the k-th test sample, K is shared test set size,
C is the number of classes. This calculation, using Hellinger
distance of prediction probability distributions, effectively captures differences in model prediction behavior.
d) Comprehensive similarity calculation: After normalizing all three similarity components to the range [0, 1], they
are weighted and combined to yield comprehensive similarity:
Sim(i, j) = α · Sim param (i, j) + β · Simloss (i, j)
+ γ · Sim pred (i, j)

(8)

where α, β, and γ are weight coefficients satisfying α+β+γ =
1. Based on experimental tuning, we set α = 0.6, β = 0.2,
γ = 0.2 to balance contributions of the three similarities.
This multi-dimensional metric integrates model parameters,
loss dynamics, and prediction behaviors to capture data distribution similarity. The normalization ensures Sim(i, j) ∈ [0, 1],
consistent with Assumption A3 in Section III-I.
2) Adaptive Satellite Grouping: Design Rationale. STELLAR adopts lightweight greedy grouping rather than complex
AI schedulers (e.g., DRL). While heavy schedulers might
offer theoretical optimality, their on-board inference energy
would negate FL savings. Our data-driven threshold adaptation
(Eq. 9) achieves adaptivity with minimal overhead.
Based on the multi-dimensional similarity, we propose a
systematic grouping strategy. Initially, a coordinator node with
optimal ground station visibility is selected for each orbit. The
system initializes with each satellite as an independent group,
setting a maximum neighborhood search distance (dmax ), a
group size threshold (Gt ), and an initial similarity threshold
(θi = 0.8).
The grouping process employs a greedy strategy: the coordinator sequentially processes unvisited satellites as “source
nodes” i, searching for candidate neighbors j within |i − j| ≤
dmax . If an ungrouped node j satisfies Sim(i, j) ≥ θi , it is
absorbed into group i. Even if j belongs to another group, it
is reallocated to group i if it exhibits higher similarity. The
search terminates when consecutive nodes cannot join. This
strategy recalculates similarity and updates groupings every
T update rounds to adapt to topology changes.
To address the limitation of static scheduling, we introduce
a Data-Driven Threshold Adaptation mechanism. The similarity threshold θ is dynamically updated based on real-time
group statistics to prevent groups from becoming too loose or
strict as data distributions drift:
θnew (i) = max 0.6, min(1.0,

1770

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026


min Sim(i, k)) if |Gi | ≥ Gt .
k∈Gi

(9)

Additionally, we enforce a Participation Control constraint, |S active | ≤ S max , to prevent system overload in
high-density orbits.
3) Representative Node Selection: Upon successful group
formation, the source node i serves as the initial representative
node, responsible for the group’s first model training and
parameter communication tasks. To achieve balanced resource
utilization and extend satellite operational lifespans, representative nodes are periodically rotated to prevent energy
depletion from continuous training loads.
Representative node rotation occurs in non-grouping refresh
rounds as follows:
1) Rotation sequence establishment: Group members
form an ordered rotation sequence based on their positions, with the source node as the initial representative.
2) Clockwise rotation mechanism: The representative role
transfers sequentially to the next member in the predefined order, cycling back to the first member after the
last.
3) Energy-aware selection: Before assignment, the system
checks that the candidate node has sufficient energy for
training and communication. If energy is insufficient, the
next node is evaluated. If no energy-sufficient node is
found after checking all group members, the group will
have no active representatives and thus not participate
in training or model aggregation in this round.
This rotation mechanism ensures load balancing and system
stability via energy-aware representative selection, preventing
premature node failures from resource exhaustion.
4) Intra-Group Model Training: After group formation,
the representative node conducts model training while others
directly utilize the result, significantly reducing computational
overhead.
The representative node executes the complete training
lifecycle: (1) receiving current global model parameters from
the coordinator; (2) performing local training via gradient
descent on the local dataset; (3) generating model updates
for aggregation; and (4) distributing the updated parameters
to group members.
In contrast, non-representative members operate in a
passive mode, primarily responsible for: (1) synchronizing
model parameters from the representative; (2) executing inference tasks directly; and (3) periodically broadcasting energy
status to facilitate rotation decisions. This distinct division of
labor maximizes computational efficiency and prolongs the
operational lifespan of individual satellites.

mechanism is designed: intra-orbital aggregation, ground station aggregation, and global aggregation.
1) Intra-Orbital Aggregation: Orbital coordinators collect
model updates from representative nodes of all groups within
the same orbit and perform weighted average aggregation.
The aggregation weights consider three factors: (1) Group
size—larger groups receive higher weights reflecting more
represented satellites; (2) Training data volume—groups with
more training samples receive higher weights; (3) Model
performance—groups with higher local validation accuracy
receive higher weights.
The intra-orbital aggregation is formulated as:
∆worbit =

M
X

αi · ∆wi

(10)

i=1

where ∆worbit is the aggregated orbital update, ∆wi is the i-th
group’s model update, M is the number of groups in the orbit,
and αi is the normalized weight:
]i
G̃i · D̃i · ACC
(11)
αi = P M
]
j=1 G̃ j · D̃ j · ACC j
It is worth noting that while our theoretical analysis assumes
static weights (proportional to data volume) for mathematical
tractability, the practical implementation employs the dynamic
quality-aware weights defined in Eq. (11). Empirically, this
strategy acts as a variance reduction technique by downweighting low-quality updates from unstable satellites, further
enhancing convergence stability beyond the theoretical lower
bounds.
2) Ground Station and Global Aggregation: Ground stations aggregate orbital updates from their assigned orbits
(typically 1-2 orbits per station):
m
X
∆w station =
βi · ∆worbit,i
(12)
i=1

where m is the number of orbits per station, and βi weights
are proportional to orbital data volumes.
Finally, global aggregation combines all station updates:
s
X
∆wglobal =
γi · ∆w station,i
(13)
i=1

where s is the number of ground stations, and γi weights reflect
station data contributions.
This hierarchical architecture leverages the satellite
network’s natural topology, minimizing inter-satellite communication while maintaining aggregation quality through
contribution-based weighting at each level.
F. Asynchronous Aggregation and Staleness Compensation

E. Hierarchical Aggregation Mechanism
Addressing Objective 2 (Convergence under Non-IID
Data). To maintain convergence despite data heterogeneity, we
design quality-aware weighting that balances group size, data
volume, and local accuracy. This prevents low-quality updates
from dominating the global model, ensuring convergence in
Non-IID scenarios.
To reduce communication overhead while ensuring aggregation effectiveness, a three-level hierarchical aggregation

Enhancing Robustness against Link Instability. Recognizing the inherent intermittency and high latency of LEO
satellite links, STELLAR incorporates a time-window-based
asynchronous aggregation protocol equipped with staleness
compensation. This mechanism serves as a critical resilience
layer, operating synergistically with the quality-aware aggregation (Section III-E) to ensure continuous training progress
and system survivability, even when communication links
experience severe delays or interruptions.

LI et al.: STELLAR: SIMILARITY-BASED SATELLITE FL FOR MALICIOUS TRAFFIC RECOGNITION

1) Time-Window Asynchronous Protocol: Unlike synchronous FL protocols that must wait for all stragglers,
STELLAR imposes a strict maximum waiting window ∆T for
each aggregation round. Updates arriving within this window
are aggregated immediately, while late updates are buffered
and treated as “stale” in subsequent rounds.
• Intra-orbital Window: ∆T orbit = 30 s, accounting for
local training latency and ISL transmission delays.
• Ground Station Window: ∆T gs = 60 s, adapted to the
limited visibility duration of LEO satellites relative to
ground stations.
Updates that miss the current window are preserved for the
next available round, tagged with a specific staleness value τ.
2) Staleness Compensation: Stale updates may carry gradients derived from obsolete model parameters, potentially
introducing noise. To leverage this data while mitigating
adverse effects, we define the staleness of an update from node
i as τi = tcurr − tgen , where tcurr is the current aggregation time
and tgen is the timestamp when the node’s local model was
generated. In our theoretical analysis, staleness is measured in
rounds; the time-window delays can be mapped to a bounded
round-level delay τ ≤ τmax (Assumption A4). We apply an
Inverse Time Decay function to weight these updates:
1
(14)
β(τ) =
1+λ·τ
where λ is a tunable decay coefficient. This mechanism ensures
that fresh updates (τ → 0, β ≈ 1) contribute fully, whereas
stale updates are down-weighted rather than discarded, thereby
maximizing data utilization under unstable conditions. Theoretical analysis (Section III-I) further demonstrates that the
error introduced by this asynchronous mechanism is bounded
and controllable.
G. Lightweight Satellite Authentication Based on Proxy
Nodes
Addressing Security Requirements. The security of satellite identities and parameter passing is crucial for federated
learning. Given resource-constrained space environments and
intermittent connectivity, we design LASS-PN (Lightweight
Authentication for Satellites based on Proxy Nodes) to ensure
participant trustworthiness with minimal overhead.
LASS-PN verifies satellite legitimacy, generates communication keys, and enables authentication among all satellites
via cryptographic techniques and proxy node mechanisms.
LASS-PN selects Proxy Authentication Satellites (PAS) for
professional authentication handling. Normal Satellites (NS)
only interact with PAS to authenticate trust, freeing them from
cumbersome processes and significantly reducing overhead.
LASS-PN’s core cryptographic modules use coordinated
SM3 and SM4 algorithms: Authentication uses an SM3-256
hash engine, with MAC generation function f 1 truncating
the first 128 bits of hashes to generate MAC, and response
function f 2 extracting the last 128 bits as RES. Key derivation
function KDF employs SM3-HMAC-256, truncating the first
128 bits of 256-bit output as encryption keys. Data encryption
enc uses 128-bit key SM4, ensuring confidentiality via fixedlength ciphertext with security equivalent to AES-128.

1771

Fig. 3. Proxy node satellite-ground authentication process.

1) Node Registration: Network Authentication Center
(NAC) assigns parameters to satellites (PAS and NS) via
out-of-band secure channels. The parameters include identity identifiers ID, secrets CKey, intra-group pre-shared keys
GKey, and NS identity keys IDKey.
For PAS registration, NAC generates identifier IDA for
satellite A, designates A as PAS according to the grouping
strategy, gets current timestamp t s , and generates PAS identity
secret CKeyA using NAC private key s as follows:
CKeyA = KDF(s, IDA , t s ).

(15)

NAC generates GKeyA as intra-group identity shared key of
PAS A and intra-group normal nodes, which is used by PAS to
authenticate the group identity of intra-group NS. NAC sends
CKeyA and GKeyA to PAS through secure channels.
For NS registration, NAC assigns unique identifier IDi to
NS i , assigns NS i to the group of nearby proxy PAS A based
on satellite orbital parameters and topological visibility. NAC
generates NS i ’s identity secret CKeyi using its private key s,
and sends it along with the group’s intra-group identity shared
key GKeyA and group member IDs to NS i through secure
channels.
2) Proxy Node Authentication: First, PAS and NAC perform satellite-ground authentication and negotiate session key
skNA . Then, Adjacent PAS authentication is conducted.
a) Satellite-ground authentication: NAC authenticates
PAS legitimacy; upon completion, it generates PAS-NAC
communication key skNA . Steps are in Fig. 3.
Step 1: PAS A gets current timestamp t1 , generates random number r, and produces MAC, authentication
response XRES , and PAS A − NAC communication
key skNA via formulas as in Fig. 3.
After generating these parameters, PAS A adds current
timestamp t2 and sends authentication request containing the content hMAC, IDA , t1 , t2 , ri to NAC.
Step 2: NAC parses the request, extracts parameters, checks
IDA legitimacy and timestamp validity (t0 − t2 ≤ ∆t),
with t0 as current time and ∆t maximum transmission
time). If valid, it queries satellite info via IDA ; if none

1772

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

Fig. 4. Adjacent proxy node authentication process.

exists, it deems the satellite illegal and stops verification. Otherwise, it extracts CKeyA , gets r and t1 from
the message, and calculates message verification code
XMAC.
If verification passes, PAS A is authenticated. NAC
generates skNA and response code RES via formulas
as in Fig. 3, then sends RES to PAS A .
Step 3: PAS A verifies response code consistency with XRES ;
if valid, it completes identity authentication and session key negotiation with NAC. PAS A and NAC then
use skNA for secure communication.
Step 4: After PAS authentication completion, NAC sends
network-wide satellite identifiers and grouping correspondences hIDs, PAS i to each PAS via the
negotiated session key skNA . Each PAS stores locally
for subsequent intra-group satellite authentication
and rapid determination of normal node groups and
corresponding PAS during inter-group authentication
communication.
Simultaneously, NAC generates NS i identity key IDKeyi
using NS i identity secret CKeyi and corresponding PAS A
identity identifier IDA :
IDKeyi = KDF(CKeyi , IDA ).

(16)

NAC sends hID, IDKeyi to corresponding PAS A through
negotiated session key skNA . PAS utilizes IDKey to verify NS
identity during intra-group authentication.
b) Adjacent proxy node authentication: Adjacent proxy
nodes need to interact and assist in completing authentication
between inter-group members. Therefore, proxy nodes first
authenticate each other’s identities. This authentication is
completed collaboratively by relevant proxy nodes and NAC.
The process is shown in Fig. 4.
Step 1: Assume authentication is initiated by proxy satellite PAS B . PAS B first generates random number
r1 , timestamp t1 , and generates MAC, expected
response value XRES , and inter-proxy communication key skAB as in Fig. 4. PAS B obtains
current timestamp t2 and sends authentication request
hMAC, enc(skNB , IDA , IDB , t1 , t2 , r1 )i to NAC.

Step 2: NAC parses received information, verifies validity of
IDB and IDA , and determines whether timestamp
t2 satisfies t0 − t2 ≤ ∆t. Next, NAC queries corresponding identity information based on identifier IDB .
If satellite is unregistered, authentication terminates;
otherwise, XMAC is generated using CKeyB as in
Fig. 4 to verify MAC legitimacy.
NAC then calculates response value RES and interproxy communication key skAB as in Fig. 4.
NAC obtains current timestamp t3 , encrypts t3 , RES ,
skAB using skNA and sends to PAS A as in Fig. 4.
Step 3: PAS A decrypts the message using skNA and verifies
timestamp t0 − t3 ≤ ∆t. After verification passes, it
encrypts RES using skAB to get CMAC and sends to
PAS B as in Fig. 4.
Step 4: PAS B decrypts CMAC using skAB to obtain parameter
RES , verifies consistency between XRES and RES .
If verification passes, PAS B completes authentication
of PAS A .
3) Intra-Group Node Authentication: Intra-group authentication must be completed before normal satellite nodes
communicate. The process is as shown in Fig. 5.
Step 1: Normal satellite NS i generates key IDKeyi using registration phase identity secret CKeyi and its PAS node
PAS A identifier IDA via formula 16, then encrypts
timestamp t1 with it, and sends the authentication
request hIDi , enc(IDKeyi , t1 , IDi )i to PAS A .
Step 2: PAS A receives authentication request from IDi , it
determines whether IDi is its group member assigned
by NAC. After confirming that, it extracts IDKeyi
through hID, IDKeyi correspondence obtained during
PAS authentication phase to decrypt and verify IDi .
Finally, it verifies timestamp t0 − t1 ≤ ∆t.
After verification passes, PAS A generates random
number r1 , timestamp t2 , and generates MAC along
with GKeyA . Then it generates encrypted timestamp protection sequence AK and intra-group session
key skA . PAS A encrypts authentication message
hIDA , MAC, enc(IDKeyi , r1 , t1 , t2 ⊕ AK)i with IDKeyi
to send to node NS i .
Step 3: NS i receives returned message from PAS A , decrypts
with IDKeyi , generates XMAC to verify legitimacy.
After verification passes, NS i parses message parameters
and generate intra-group communication key skA .
This process repeats for other group members, ultimately
establishing secure intra-group communication via shared key
skA .
4) Inter-Group Node Authentication: Edge satellites of
adjacent groups cannot complete mutual authentication via
intra-group authentication; the authentication is assisted by the
corresponding group proxy satellites.
Given normal satellites NS i (of PAS A group) and NS j (of
PAS B group), NS i seeks to authenticate NS j , the process is
as in Fig. 6.
Step 1: NS i gets the timestamp t1 and sends to PAS A an
ID j -included authentication request encrypted via
intra-group key skA .

LI et al.: STELLAR: SIMILARITY-BASED SATELLITE FL FOR MALICIOUS TRAFFIC RECOGNITION

1773

Fig. 7. Stellar deployment diagram.

Fig. 5. Intra-group satellite authentication process.

The upper right details a 10-satellite orbit: satellites form
authentication groups (dashed boxes) by visibility, managed
by fixed PAS nodes, and computational groups (colored)
by data similarity for federated learning. Each computational
group selects a representative (bold) for training; others adopt
its model. Representatives rotate (dashed arrows) for load
balancing. During aggregation, representatives send updates
(orange lines) to orbital coordinators, implementing three-level
aggregation: intra-orbital → ground station → global.
I. Theoretical Analysis

Fig. 6. Inter-group satellite authentication process.

Step 2: PAS A decrypts the request, verifies parameters, finds
PAS B via ID j , generates r, then creates S Kgab using
CKeyA , r, IDi , and ID j , sets the expiration time T . IDi
and ID j are used to generate the inter-group session
key to enhance its randomness, not to limit it to IDi ID j communication. PAS A encrypts and sends AK,
t2, T to PAS B via inter-proxy key skAB , generates
timestamp t3 , and sends inter-group key S Kgab to
intra-group nodes using intra-group key skA .
Step 3: PAS B verifies t2, T , etc. Upon success, it generates
inter-group key S Kgab , and sends it to intra-group
nodes via skB .
H. STELLAR Deployment
Fig. 7 shows STELLAR’s deployment. All nodes authenticate via LASS-PN before communication, establishing trust
and secure keys.

This section provides rigorous guarantees for STELLAR’s
design objectives. To strictly analyze the impact of our
proposed Similarity-based Representative Selection and Asynchronous Staleness Compensation, we formulate the analysis
under the Asynchronous Stochastic Gradient Descent (AsyncSGD) setting. While our implementation uses Local SGD
(FedAvg) for communication efficiency, standard FL theory
confirms that local updates introduce only an additional
bounded drift term [23]. Our proofs focus on bounding the
unique error terms introduced by STELLAR: the representative bias and the asynchronous staleness.
1) Problem Setting: Consider N satellites V = {1, 2, . . . , N},
nv
each holding local data Dv = {(xi(v) , y(v)
i )}i=1 . The local objective
is
nv
N
X
1 X
(v) (v)
pv Fv (w), (17)
`(w; xi , yi ), F(w) =
Fv (w) =
nv
v=1
i=1
P
where pv = nv / u nu and `(·) is the local loss. STELLAR
activates only a subset of satellites Rt (representatives) at each
round t.
The total per-round energy is

Ettot = |Rt |eact + (N − |Rt |)epas ,

(18)

where eact and epas = εeact are active and passive energy costs.
Thus, total energy over T rounds is Etotal ≈ T R̄eact , implying
that minimizing the number of active representatives R̄ directly
improves energy efficiency.
2) Assumptions:
• A1 (Smoothness). Each Fv is L–smooth: k∇Fv (w) −
∇Fv (w0 )k ≤ Lkw − w0 k.
• A2 (Bounded Variance). Ek∇`(w; ξ) − ∇Fv (w)k2 ≤ σ2 .

1774

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

For each group Gm with representative rm and minimum
intra-group similarity θm = mini, j∈Gm Sim(i, j),
kgm (w) − ∇Frm (w)k ≤ φ(1 − θm ).
Consequently, letting θ = mint minm θm(t) ,
kgrep (w) − ∇F(w)k ≤ φ(1 − θ).
Remark: This lemma formalizes the intuition in
Section III-D that similarity-based grouping introduces
bounded bias, validating the representative mechanism for
energy reduction while preserving convergence.
4) Asynchronous Aggregation: The global model is updated
as wt+1 = wt − ηĝt , where η > 0 is the learning rate.
STELLAR adopts a time–window protocol where late
updates are weighted by
Fig. 8. Empirical validation of A3. Strong correlation (r = 0.80) between
metric dissimilarity δ and gradient distance supports the proposed multidimensional similarity metric.

• A3 (Similarity–Gradient Relationship). There exists a
non-decreasing function φ : [0, 1] → R+ with φ(0) = 0
such that for any satellites i, j,
k∇Fi (w) − ∇F j (w)k ≤ φ(1 − Sim(i, j)).

β(τ) =


λ ∈ 0, 1 .

(20)

We use grm (w) to denote a stochastic gradient computed by
representative rm at model parameter w, with E[grm (w)] =
∇Frm (w).
We denote by ĝt the staleness-compensated aggregated
gradient at round t:

(19)

Empirical Evidence. At round 6 (after similarity-based
grouping is activated), we compute δi j = 1 − Sim(i, j)
and the corresponding gradient distance for all 208,335
satellite pairs in the simulated constellation, and observe a
strong positive correlation (Pearson r = 0.80, p < 0.001),
indicating that larger metric dissimilarity aligns with
larger gradient discrepancy (Fig. 8). Using linear regression, we fit a conservative linear form φ(δ) ≈ 66.2δ. At
the design threshold θ = 0.8 (i.e., δmax = 0.2), this yields
a worst-case bound φ(0.2) ≈ 13.2. In practice, the intragroup pairs produced by our grouping procedure typically
exhibit much smaller dissimilarity (often δ  0.2),
leading to substantially tighter observed gradient gaps and
providing a safety margin in our deployment setting.
• A4 (Bounded Staleness). Delays τt,r satisfy 0 ≤ τt,r ≤ τmax .
• A5 (Bounded Gradient). The stochastic gradients are
almost surely bounded: k∇`(w; ξ)k ≤ G, ∀w, ξ.
3) Representative Approximation: Satellites are partitioned
Mt
into similarity
P groups {Gm }m=1 , each represented by rm ∈ Gm .
Let Pm = j∈Gm p j denote the aggregate weight of group m.
Since grouping may change over rounds, define the global
minimum intra-group similarity as θ , mint minm θm(t) , where
θm(t) = mini, j∈Gm(t) Sim(i, j).
We define two key quantities:
P
pj
• Group-average gradient: gm (w) =
j∈Gm Pm ∇F j (w),
which is the true weighted gradient of all satellites in
group m.
P Mt
• Representative gradient: grep (w) =
m=1 Pm ∇F rm (w),
which aggregates only gradients from representatives.
The core question is: how well does grep (w) approximate
the true global gradient ∇F(w)?
Lemma 1: [Representative Bias Control]

1
,
1 + λτ

ĝt =

Mt
X

Pm β(τt,m ) grm (wt−τt,m ),

m=1

Lemma 2: [Asynchronous Error Bound]
Under Assumptions A1–A5,
τ2max
(1 + λτmax )2
+ 4L2 η2G2 τ2max + 2σ2 .

Ekĝt − grep (wt )k2 ≤ 4G2

(21)

Thus, the asynchronous effect is bounded and decreases as
λ increases (for λ ∈ (0, 1]).
5) Main Results:
Theorem 1: [Convergence Guarantee
(Objective 2)]
√
Under A1–A5 and η = O(1/ T ),
T −1

 
1X
Ek∇F(wt )k2 ≤ O √1T + O(σ2 )
T
t=0


+ O φ(1 − θ)2 + O Ψ(τmax , λ) . (22)


τ2max
where Ψ(τmax , λ) = O (1+λτ
is the asynchronous error
2
max )
term √
from Lemma 2. Hence, STELLAR achieves the same
O(1/ T ) convergence rate as full-participation FL, with controlled bias. Moreover, it converges to a neighborhood of
stationary points whose radius is determined by σ2 , φ(1 − θ)2 ,
and Ψ(τmax , λ).
Theorem 2: [Energy Saving Guarantee (Objective 1)]
Compared with FedAvg, STELLAR reduces energy consumption by


R̄
ρsave = (1 − ε) 1 −
,
(23)
N
where ε = epas /eact  1. In our simulated configuration (N =
646, R̄ ≈ 150), this predicts ρsave ≈ 73%, consistent with the
measured 77–80% reduction.

LI et al.: STELLAR: SIMILARITY-BASED SATELLITE FL FOR MALICIOUS TRAFFIC RECOGNITION

Proof Sketch: The analysis proceeds as follows. (1) By
Lemma 1, the representative gradient approximates the true
gradient with bias φ(1 − θ). (2) Lemma 2 bounds the staleness
error using β(τ) decay. (3) Substituting both bounds into the
smoothness-based descent inequality and telescoping over T
iterations yields the final rate. (4) Energy efficiency follows
from the reduced number of active satellites per round.
Remark: Detailed proofs and intermediate derivations are
provided in the supplementary material.

1775

urban), resulting in significant differences in traffic
statistical features (Feature Skew).
• Intra-orbit Data Overlap: Considering the temporal
correlation of satellites in the same orbital plane, we
introduce a data overlap mechanism (overlap ratio
set to 0.5) to simulate the shared traffic characteristics of adjacent satellites during orbital movement.
The data allocation strictly follows the physical topology of
the OneWeb constellation to validate STELLAR’s robustness
against realistic heterogeneity.

IV. P ERFORMANCE E VALUATION
A. Experimental Environment and Dataset
The experimental network simulates a large-scale LEO
satellite network based on the OneWeb constellation. The
orbital parameters are initialized using public TLE data.
Although the raw TLE set contains 651 satellite entries,
we filter out inactive/standby units, resulting in 646 active
satellites distributed across 12 orbital planes. The constellation
operates at an altitude of approximately 1200 km with an
inclination of 87.9◦ .
The simulation core uses the Skyfield library to calculate real-time satellite positions and velocities via TLE data.
Simulation Fidelity: Our environment models the dynamic
topology evolution of the OneWeb constellation. Satellite
positions and inter-satellite link (ISL) visibility are updated
every second based on orbital mechanics. Unless otherwise
stated, the main experiments assume ideal communication
links (no stochastic delay or packet loss) to isolate algorithmic gains. We acknowledge this represents a best-case
scenario; Section IV-E partially addresses this limitation by
validating system robustness under severe delays (up to 60%
link instability).
Each satellite has 1000 Wh batteries and 2.5 m2 solar
panels (30% conversion efficiency). Energy consumption is
dynamically calculated by actual tasks: transmission energy
depends on data size and bandwidth; computational energy is
proportional to training operations.
This paper utilizes satellite network traffic data from the
STIN-IDS dataset [12]. To adapt the dataset for binary intrusion detection, we merge the original labels: the ‘Benign’ class
is mapped to Normal, and all 7 attack types are unified as
Malicious. After preprocessing, the dataset contains 2,122,322
records, partitioned into training and testing sets with an
8:2 ratio.
To rigorously evaluate the proposed framework, we design
two data distribution scenarios:
1) Independent and Identically Distributed (IID): Data
is randomly shuffled and uniformly distributed across all
satellites, ensuring that each node holds samples with
similar feature distributions.
2) Non-Independent and Identically Distributed (NonIID): Unlike the standard Dirichlet partition, we
construct a feature-skewed non-IID scenario based on
physical geographic mappings to reflect realistic satellite
coverage:
• Inter-orbit Feature Shift: Satellites in different orbits
cover distinct geographic regions (e.g., ocean vs.

B. Evaluation Metrics
To comprehensively assess the performance of the proposed
framework, we utilize the following metrics:
• Accuracy: Proportion of correctly classified samples;
• Precision: Ratio of true positives to total positive predictions;
• Recall: Ratio of true positives to actual positive samples;
• F1-Score: Harmonic mean of precision and recall;
• Energy Consumption: Total energy consumption per
training round;
• Participating Satellites: Number of satellites actively
participating in training per round;
• Energy Efficiency: Ratio of accuracy to energy consumption;
• Training Efficiency: Convergence speed measured by
rounds to reach target accuracy.

C. Comparison Methods
STELLAR is compared with the following baselines:
1) FedAvg: The standard Federated Averaging algorithm,
where participating satellites upload locally trained
model parameters, and the server aggregates them via
weighted averaging.
2) FedProx: An improved framework based on FedAvg
that introduces a proximal term to the local objective
function. It limits the deviation between local and global
models, theoretically designed to address system heterogeneity and Non-IID data challenges.
3) SDA-FL: A specialized federated learning framework
tailored for satellite networks, which integrates semisupervised domain adaptation. It utilizes GANs
to generate synthetic data and incorporates iterative
pseudo-labeling mechanisms to align feature distributions across heterogeneous satellites.
All methods are implemented in the same OneWeb simulation environment with identical hyperparameters to ensure a
fair comparison.

D. Experimental Results and Analysis
1) Performance in IID and Non-IID Environments: Fig. 9
presents the comprehensive performance comparison across
both data distribution scenarios.

1776

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

Fig. 9. Accuracy and energy consumption comparison in IID and Non-IID environments. Top row: IID scenario where STELLAR achieves 99.55% accuracy
with 77% energy savings. Bottom row: Non-IID scenario where STELLAR reaches 99.72% accuracy with 80% energy savings. The sharp energy drop at
Round 6 corresponds to the activation of similarity-based grouping, reducing active satellites from 646 to approximately 150-170.

a) IID environment: From Fig. 9a, STELLAR achieves
detection accuracy comparable to the best baseline FedAvg,
maintaining over 99.5% in the later stages. SDA-FL starts
with lower accuracy but gradually catches up, while FedProx
shows relatively weaker performance (∼98.7%) and slower
convergence. Notably, despite actively using only a fraction of
the constellation after Round 6, STELLAR maintains this competitive accuracy, demonstrating that the representative node
mechanism effectively captures the global data distribution
without requiring full participation.
The resource efficiency advantage of STELLAR is drastic,
as shown in Fig. 9b. Before Round 6 (warm-up phase),
all methods consume similar energy (∼260 Wh). However,
once the similarity-based grouping is activated at Round
6, STELLAR’s energy consumption plummets to approx.
60 Wh, resulting in a 77% reduction compared to baselines. This energy reduction corresponds to a sharp drop
in active satellites from 646 to roughly 150, achieving
an energy efficiency (Accuracy/Energy) improvement of 4×
(1.7 vs. 0.4%/Wh). In contrast, SDA-FL consumes the highest
energy (∼310 Wh) due to the computational overhead of GAN
training. In terms of communication overhead, STELLAR
reduces per-round model uploads from 646 to approximately
150, corresponding to a 77% reduction in transmitted data
volume.
b) Non-IID environment: In the more challenging
Non-IID scenario (Fig. 9c), STELLAR demonstrates superior

robustness, with its accuracy curve consistently outperforming
other methods and stabilizing near 99.8%. FedAvg follows
closely, while SDA-FL exhibits instability and high variance.
Most notably, FedProx performs the worst, contradicting
theoretical expectations. This is attributed to the feature skew
nature of satellite data: the proximal term in FedProx restricts
local models from adapting to the distinct feature distributions of different orbital regions (e.g., ocean vs. urban),
leading to over-regularization. STELLAR’s grouping strategy avoids this by allowing similar nodes to collaborate
freely.
The energy advantage of STELLAR becomes even more
critical in Non-IID settings, as shown in Fig. 9d. Baseline
methods consume significantly more energy (∼400-450 Wh)
compared to the IID scenario due to the difficulty of convergence. However, STELLAR maintains its low-energy profile,
dropping to ∼80 Wh after Round 6. This represents an
80% energy saving compared to SDA-FL and FedProx.
With active satellites reduced from 646 to approximately 170,
STELLAR achieves an energy efficiency of ∼1.2%/Wh,
whereas other methods struggle at ∼0.25%/Wh—a 5×
improvement. This confirms that STELLAR provides a sustainable solution for massive satellite constellations where
energy is a scarce resource.
2) Performance Comparison Under Different Data Distributions: To comprehensively evaluate method adaptability
under different data distribution conditions, we compare final

LI et al.: STELLAR: SIMILARITY-BASED SATELLITE FL FOR MALICIOUS TRAFFIC RECOGNITION

TABLE I
P ERFORMANCE C OMPARISON OF M ETHODS U NDER IID AND
N ON -IID D ISTRIBUTIONS

performance metrics under IID and Non-IID environments, as
shown in Table I.
From Table I, the methods exhibit distinct performance
characteristics across environments. In the ideal IID scenario,
FedAvg achieves the highest performance metrics (Accuracy
99.66%), serving as a strong baseline. STELLAR follows
closely with an accuracy of 99.55%, showing a negligible gap
(<0.15%) compared to the full-participation FedAvg. FedProx
performs the weakest in both scenarios (∼98.7%–98.9%),
further confirming that its proximal term limits the model’s
potential in this specific feature space.
However, the superiority of STELLAR becomes evident
in the challenging Non-IID scenario. While FedAvg maintains its performance, STELLAR surpasses all baselines,
achieving the highest Accuracy (99.72%), F1-Score (99.68%),
Precision (99.72%), and Recall (99.65%). This indicates that
STELLAR’s multi-dimensional similarity grouping effectively
captures the heterogeneous data distribution, allowing the
model to generalize better than random aggregation (FedAvg)
or rigid regularization (FedProx).
Most importantly, this performance must be viewed in the
context of resource consumption (Fig. 9). Although STELLAR is marginally lower than FedAvg in the IID setting,
it achieves this near-optimal performance while consuming
approximately 77% less energy. In the Non-IID setting,
STELLAR achieves a “double win”—providing both the
highest classification accuracy and the lowest energy cost
(80% savings). This fully proves its excellent performanceenergy balance for resource-constrained satellite networks.
E. Validation of Asynchronous Aggregation and Staleness
Compensation
The main performance comparison (Section IV-D) and the
subsequent ablation studies (Sections IV-F–IV-G) assume ideal
communication links to isolate algorithmic gains. However,
LEO satellite networks face inevitable communication delays
due to intermittent orbital visibility and fluctuating onboard
capabilities. To validate the asynchronous aggregation protocol
proposed in Section III-F, we stress-tested STELLAR under
varying delay scenarios on the OneWeb constellation.
1) Experiment Setup: We evaluate three scenarios to test
system survivability:
1) Baseline (Sync): 0% delay probability (ideal reference);
2) Mild Async: 30% delay, 1–2 rounds lag (typical
congestion);
3) Severe Async: 60% delay, 1–4 rounds lag (frequent link
interruptions).

1777

STELLAR uses staleness compensation with decay coefficient
λ = 0.5 (Section III-F). Traditional synchronous FL either
waits indefinitely for stragglers or discards late updates, while
STELLAR’s time-window protocol salvages them via the
staleness weighting mechanism in Eq. 14.
2) Convergence and Stability Analysis: Robustness Under
Severe Delays: Fig. 10a shows STELLAR maintains convergence even under the Severe Async scenario (60% nodes
with 1–4 rounds lag). Although minor fluctuations occur (e.g.,
Round 19 drops to ∼98.5%), the model quickly recovers and
avoids the divergence or complete stalls typical of strict synchronous protocols. This validates the time-window protocol’s
effectiveness in harsh space environments.
Mild Asynchrony as Regularization: Interestingly, the
Mild Async scenario performs comparably to—and occasionally outperforms—the synchronous baseline in early rounds
(1)–(5). This suggests moderate asynchronous noise can act as
implicit regularization, helping the model escape local optima.
However, this benefit diminishes in later stages, confirming
that asynchrony is primarily a robustness mechanism rather
than an optimization technique.
Critical Data Salvaging Capability: Fig. 10b illustrates
the mechanism’s value in extreme cases. At Round 12, zero
fresh updates arrived (all ground stations experienced communication failures). Under strict synchronous FL, this would
cause complete training failure or infinite waiting. However,
STELLAR successfully salvaged 4 stale updates from previous
rounds, ensuring continuous progress. Over 20 rounds, 49 stale
packages were recovered, providing essential data volume to
maintain the convergence trend in Fig. 10a. This demonstrates
that the staleness compensation mechanism effectively trades
temporal flexibility for maximized data utilization, as theoretically bounded in Lemma 2.
F. Multi-Dimensional Similarity Ablation Study
To quantitatively evaluate the individual contribution of
each similarity component and validate the necessity of the
proposed multi-dimensional metric design, we conducted an
extensive ablation study in the Non-IID scenario.
1) Experimental Design: STELLAR’s multi-dimensional
similarity is a weighted sum of Parameter Similarity
(Sim param ), Convergence Pattern Similarity (Simloss ), and Prediction Behavior Similarity (Sim pred ). We designed two sets
of variants for comparison:
• Single Component Variants: Only one similarity metric
is retained (denoted as Only-Param, Only-Loss, OnlyPred) to observe individual contributions.
• Component Necessity Variants: One metric is removed
while the other two are retained and equally weighted
(denoted as No-Param, No-Loss, No-Pred) to analyze the
indispensability of each dimension.
All other experimental conditions (topology, data partition,
model structure) remain consistent with previous sections.
Each variant was run independently 4 times, and the test
accuracy was smoothed via a sliding window to reduce noise.
2) Result Analysis: Fig. 11 presents the ablation results.
Single Component Analysis (Left):

1778

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

Fig. 10. Asynchronous aggregation performance. (a) model accuracy remains robust even under severe delays (60% links with 1-4 rounds lag). (b) Stale
updates (red hatched bars) are salvaged to maintain data availability—49 total packages recovered over 20 rounds.

Fig. 11. Ablation study of STELLAR’s Multi-dimensional similarity under non-IID Scenario. The left plot compares single-component variants against the
full baseline, while the right plot compares variants with one component removed.

• Superiority of Multi-dimensional Fusion: The full
Baseline (Black line) consistently achieves the highest
accuracy and fastest convergence rate, especially during
the first 15 rounds. This empirically proves that fusing
multiple dimensions yields better grouping quality than
any single metric alone.
• Dominance of Parameter Similarity: Among the singlecomponent variants, Only-Param (Red line) performs the
best and is the closest to the Baseline. However, it still
lags behind the Baseline in the early-to-mid training
stages, indicating that relying solely on parameters is
insufficient for rapid convergence.
• Auxiliary Role of Behavior Metrics: Both OnlyPred (Orange) and Only-Loss (Green) show significantly
slower start-up speeds. However, Only-Pred catches up
in later rounds, suggesting that prediction behavior provides valuable discriminative information as the model
matures.
Component Necessity Analysis (Right):

• No-Param exhibits the lowest performance, significantly lagging behind the Baseline, confirming that
direct parameter similarity is critical for grouping
quality.
• No-Loss and No-Pred perform better than No-Param
but still show degradation compared to the Baseline.
This indicates that convergence patterns and prediction
behaviors provide essential supplementary and corrective
information.
• All “missing-one” variants show performance degradation, proving that the three dimensions are complementary: simultaneously utilizing parameter, loss, and
prediction information yields the most stable and precise
grouping.
Conclusion: The ablation study confirms that the three
metrics are complementary: Parameter similarity ensures the
performance lower bound (Foundation), Prediction behavior
guarantees training stability (Stabilizer), and Loss patterns
provide fine-grained refinement (Fine-tuner). Simultaneously

LI et al.: STELLAR: SIMILARITY-BASED SATELLITE FL FOR MALICIOUS TRAFFIC RECOGNITION

1779

Fig. 12. Sensitivity and robustness analysis. (a) illustrates the impact of parameter similarity weight α on convergence, identifying α = 0.6 as the optimal
configuration. (b) visualizes the system robustness under noise: the left plot shows the accuracy comparison, while the right plot displays the stability (rolling
standard deviation). The proposed hybrid metric (α = 0.6) maintains high accuracy and low variance compared to the single-metric approach (α = 1.0).

utilizing all three yields the most stable and precise grouping
results.
G. Sensitivity and Robustness Analysis
To determine the optimal weight configuration and justify
the multi-dimensional design, we conducted a sensitivity analysis followed by a robustness stress test.
1) Experimental Design: First, we analyzed sensitivity by
varying α from 0.0 to 1.0 with a step size of 0.2 (setting
β = γ = 1−α
2 ). The results (Fig. 12a) identify the hybrid configuration (α = 0.6) as the optimum, though the pure parameter
strategy (α = 1.0) remains competitive in ideal settings (gap
<0.15%). To verify whether the multi-dimensional design
provides essential stability beyond this marginal accuracy
gain, we designed a stress test comparing the two. Specifically,
we injected Gaussian white noise into model parameters
uploaded by satellites starting from Round 5 to simulate
transmission distortion.
2) Result Analysis: The robustness test (Fig. 12b) confirms our hypothesis. Upon noise injection, the single-metric
approach (α = 1.0) becomes highly unstable, with accuracy
dropping to ∼97.0% and variance spiking. In contrast, the
hybrid metric (α = 0.6) demonstrates superior resilience,
maintaining accuracy above 99.0% with minimal fluctuations.
This proves that auxiliary behavioral metrics effectively offset
parameter noise, ensuring system reliability in practical satellite environments.
V. C ONCLUSION
In this paper, we present STELLAR, a similarity-based
federated learning framework designed to reconcile the conflict between high detection accuracy and strict resource
constraints in LEO satellite networks. By synergizing a
multi-dimensional similarity metric with an energy-efficient
representative selection mechanism, STELLAR effectively
eliminates computational redundancy. Extensive evaluations
demonstrate that our framework reduces network-wide energy
consumption by 77%–80% while maintaining a near-optimal
detection accuracy of 99.72%, even in highly heterogeneous
Non-IID environments.
Furthermore, we provided
√ a rigorous theoretical analysis guaranteeing an O(1/ T ) convergence rate. The proposed time-window asynchronous protocol with staleness

compensation ensures system robustness against severe communication delays (up to 60% link instability). Comparative
results show that STELLAR consistently outperforms specialized baselines such as FedAvg, FedProx, and SDA-FL. These
findings establish STELLAR as a sustainable and robust security paradigm for next-generation mega-constellations where
resource optimization is paramount.
R EFERENCES
[1]

Z. Lin, Z. Chen, Z. Fang, X. Chen, X. Wang, and Y. Gao, “FedSN: A federated learning framework over heterogeneous LEO satellite networks,”
IEEE Trans. Mobile Comput., vol. 24, no. 3, pp. 1293–1307, Mar. 2025.
[2] M. Elmahallawy, T. Luo, and M. I. Ibrahem, “Secure and efficient federated learning in LEO constellations using decentralized key generation
and on-orbit model aggregation,” in Proc. IEEE Global Commun. Conf.,
Dec. 2023, pp. 5727–5732.
[3] X. Yu, Y. Huang, Y. Zhang, M. Song, and Z. Jia, “Network intrusion
traffic detection based on feature extraction,” Comput., Mater. Continua,
vol. 78, no. 1, pp. 473–492, 2024.
[4] S. Cai, H. Xu, M. Liu, Z. Chen, and G. Zhang, “A malicious network
traffic detection model based on bidirectional temporal convolutional
network with multi-head self-attention mechanism,” Comput. Secur.,
vol. 136, Jan. 2024, Art. no. 103580.
[5] X. Zhao, K. W. Fok, and V. L. L. Thing, “Enhancing network intrusion
detection performance using generative adversarial networks,” Comput.
Secur., vol. 145, Oct. 2024, Art. no. 104005.
[6] N. Sitouah, F. Merazka, and A. Hedjazi, “Deep learning approach
for interruption attacks detection in LEO satellite networks,” 2022,
arXiv:2301.03998.
[7] Y. Zhang and Q. Liu, “On IoT intrusion detection based on data
augmentation for enhancing learning on unbalanced samples,” Future
Gener. Comput. Syst., vol. 133, pp. 213–227, Aug. 2022.
[8] K. Li, H. Zhou, Z. Tu, W. Wang, and H. Zhang, “Distributed network
intrusion detection system in satellite-terrestrial integrated networks
using federated learning,” IEEE Access, vol. 8, pp. 214852–214865,
2020.
[9] N. Moustafa et al., “DFSat: Deep federated learning for identifying cyber
threats in IoT-based satellite networks,” IEEE Trans. Ind. Informat., early
access, Oct. 20, 2022, doi: 10.1109/TII.2022.3214652.
[10] P. M. S. Sánchez et al., “Studying the robustness of anti-adversarial federated learning models detecting cyberattacks in IoT spectrum sensors,”
IEEE Trans. Dependable Secure Comput., vol. 21, no. 2, pp. 573–584,
Mar. 2024.
[11] M. Al-Hawawreh and M. S. Hossain, “Federated learning-assisted
distributed intrusion detection using mesh satellite nets for autonomous
vehicle protection,” IEEE Trans. Consum. Electron., vol. 70, no. 1,
pp. 854–862, Feb. 2024.
[12] J. He, X. Li, X. Zhang, W. Niu, and F. Li, “A synthetic data-assisted
satellite terrestrial integrated network intrusion detection framework,”
IEEE Trans. Inf. Forensics Security, vol. 20, pp. 1739–1754, 2025.
[13] F. Sattler, K.-R. Müller, and W. Samek, “Clustered federated learning: Model-agnostic distributed multitask optimization under privacy
constraints,” IEEE Trans. Neural Netw. Learn. Syst., vol. 32, no. 8,
pp. 3710–3722, Aug. 2021.

1780

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

[14] G. Long, M. Xie, T. Shen, T. Zhou, X. Wang, and J. Jiang, “Multi-center
federated learning: Clients clustering for better personalization,” World
Wide Web, vol. 26, no. 1, pp. 481–500, Jun. 2022, doi: 10.1007/s11280022-01046-x.
[15] L. Liu, J. Zhang, S. H. Song, and K. B. Letaief, “Client-edge-cloud
hierarchical federated learning,” in Proc. ICC - IEEE Int. Conf. Commun.
(ICC), Jun. 2020, pp. 1–6.
[16] M. Abdrabou et al., “Advanced security framework for low Earth orbit
satellites in space information network,” EURASIP J. Wireless Commun.
Netw., vol. 2024, no. 1, p. 87, Nov. 2024.
[17] C. Huang, L. Zhu, C. Li, C. Zhang, Y. Chen, and Z. Zhang, “A new
satellite constellation networking certification and reliable maintenance
protocol (DISA),” in Proc. 30th Int. Conf. Softw. Eng. Knowl. Eng.,
2018, pp. 1–6.
[18] H. Zhu, H. Wu, L. Zhang, Y. Zhao, H. Zhao, and H. Li, Intersatellite networking authentication system and method for low Earth
orbit satellite networks, CN Patent 109 547 213 A, Mar. 29, 2019.
[19] H. Zhu, H. Wu, H. Zhao, Y. Zhao, and H. Li, “Inter-satellite networking
authentication scheme for two-layer satellite networks,” J. Commun.,
vol. 40, no. 3, pp. 1–9, 2019.
[20] M. H. Ibrahim, S. Kumari, A. K. Das, and V. Odelu, “Jamming resistant non-interactive anonymous and unlinkable authentication scheme
for mobile satellite networks,” Secur. Commun. Netw., vol. 9, no. 18,
pp. 5563–5580, Dec. 2016.
[21] Y. Liu, A. Zhang, S. Li, J. Tang, and J. Li, “A lightweight authentication
scheme based on self-updating strategy for space information network,”
Int. J. Satell. Commun. Netw., vol. 35, no. 3, pp. 231–248, May 2017.
[22] W. Meng, K. Xue, J. Xu, J. Hong, and N. Yu, “Low-latency authentication against satellite compromising for space information network,” in
Proc. IEEE 15th Int. Conf. Mobile Ad Hoc Sensor Syst. (MASS), Oct.
2018, pp. 237–244.
[23] X. Li, K. Huang, W. Yang, S. Wang, and Z. Zhang, “On the convergence
of FedAvg on non-IID data,” 2019, arXiv:1907.02189.

Yubo Li received the B.S. degree in computer
science and technology from Northeast Forestry
University, Harbin, China, in 2023. He is currently
pursuing the M.S. degree with Beijing University of
Technology, Beijing, China. His research interests
include federated learning for satellite networks and
malicious traffic detection.

Li Zhang received the B.S. and M.S. degrees
in computer architecture from Harbin Institute of
Technology, Harbin, China, in 1996 and 2000,
respectively, and the Ph.D. degree in computer
architecture from Peking University, Beijing, China,
in 2004. She visited the Institute of Network
Technology, Department of Computer Science and
Technology, Tsinghua University, for one year, and
worked as a Visiting Scholar with the Multimedia
Laboratory, Department of Computer Science and
Engineering, University at Buffalo, USA, from 2014
to 2015. She is currently an Associate Professor with the School of Computer
Science, Beijing University of Technology, Beijing, China. Her research
interests include satellite networks and future network architecture.

Kai Li received the B.S. degree in computer science
and technology from Wuhan University of Science
and Technology, Wuhan, China, in 2022, and the
M.S. degree from Beijing University of Technology, Beijing, China, in 2025. His research interests
include cryptography and satellite network security.

Haoru Su received the B.S. degree in computer
science and engineering and the M.S. degree in
computer applied technology from Northeastern
University, Shenyang, China, and the Ph.D. degree
from the Department of Electrical and Computer
Engineering, Korea University, South Korea. She is
currently an Associate Professor with the Faculty of
Information Technology, Beijing University of Technology, Beijing, China. She was a Visiting Scholar
with the Broadband Communications Research Laboratory, University of Waterloo, Canada, in 2019.
Her research interests include protocol design and performance evaluation
for wireless body area networks, the Internet of Things, and mobile edge
computing.
PAPER_TEXT
