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
# [579] 5G Mobile Networked Clusters Anomaly Detection Under Distribution Shifts: A Causal Perspective
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
编号：579
题名：5G Mobile Networked Clusters Anomaly Detection Under Distribution Shifts: A Causal Perspective
年份：2025
DOI：10.1109/tccn.2025.3632390
来源：IEEE Transactions on Cognitive Communications and Networking
PDF：paper/10.1109_TCCN.2025.3632390.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\579.txt
- 原始字符数：83208
- 本次发送字符数：83208
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
3600

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

5G Mobile Networked Clusters Anomaly Detection
Under Distribution Shifts: A Causal Perspective
Xuyuan Liu, Chao Luo , Member, IEEE, and Rui Shao
Abstract— Along with the application of the C-band of the
high-frequency spectrum, the number of 5G wireless base stations
has increased significantly compared with 3G/4G networks.
Therefore, how to intelligently detect anomalies in base stations is
crucial for the daily operation and maintenance of 5G networks.
Nowadays, 5G Mobile Network Clusters (5G-MNCs) are gradually replacing individual base stations for maintenance as a group
of regional base stations with high internal correlation. However,
anomaly detection in 5G-MNC remains challenging due to the
complex spatio-temporal measurement data, and additionally, the
distributional variations of such data’s time series can also have
a large impact on anomaly detection. In this work, we propose a
novel architecture that integrates causal intervention with doubly
residual spatio-temporal graph convolution (Causal-DRSTGC).
First, a causal intervention module is introduced to eliminate
the effect of confounders due to distribution shifts. Second,
a doubly residual structure is adopted to output reconstruction
and hidden representations respectively, which is more conducive
to promoting the representation capability of 5G-MNC data.
Third, after stacking multiple DRSTGC blocks, a reconstruction
module and a discrimination module are designed to process
data reconstruction representation and hidden representations
for joint optimization. Finally, a flexible score is designed to
balance the contributions of each component to improve the
overall performance of anomaly detection. Extensive experiments
conducted on China Mobile’s real-world dataset demonstrate that
the proposed model achieves remarkable performance. For Cluster1, the F1-scores for shielding and decommissioning anomalies
reach 89.29% and 90.53%, respectively. Additional validation
on public industrial datasets demonstrates its generalization
capability, achieving an F1-score of 83.43% on PSM, confirming
its effectiveness in various application scenarios.
Index Terms— Anomaly detection, causal interventions, spatiotemporal modeling, graph convolution network, 5G mobile
network.

I. I NTRODUCTION
ITH its high bandwidth, ultra-low latency, and extensive connection, the 5G mobile network offers vital
technical support for vertical sector applications such as smart

W

Received 3 June 2025; revised 5 September 2025 and 17 October 2025;
accepted 10 November 2025. Date of publication 13 November 2025; date of
current version 31 December 2025. This research is supported by the National
Natural Science Foundation of China (Nos: 62172264). The associate editor
coordinating the review of this article and approving it for publication was
R. Malekian. (Corresponding author: Chao Luo.)
Xuyuan Liu is with the School of Information Science and Engineering,
Shandong Normal University, Jinan 250014, China.
Chao Luo is with the School of Information Science and Engineering,
Shandong Normal University, Jinan 250014, China, and also with Shandong
Provincial Key Laboratory for Novel Distributed Computer Software Technology, Jinan 250014, China (e-mail: luochao@sdnu.edu.cn).
Rui Shao is with the Center of Network Optimization, China Mobile
Shandong Company Ltd., Jinan 250014, China.
This article has supplementary downloadable material available at
https://doi.org/10.1109/TCCN.2025.3632390, provided by the authors.
Digital Object Identifier 10.1109/TCCN.2025.3632390

healthcare systems, vehicle-to-everything communications,
drone communication systems, and the industrial Internet of
Things (IoT) [1], [2], [3], [4].
Although 5G’s millimeter wave spectrum enables increased
bandwidth, it also requires a significant increase in base
station density. This presents deployment challenges for wireless base stations—essential components of communication
infrastructure. A vital operational priority is anomaly detection
in base station clusters, which is highlighted by this rapid
infrastructure growth.
Traditional approaches for mobile network anomaly detection mostly use manually set fixed criteria to track Key
Performance Indicators (KPIs) at specific base stations [5],
[6], [7]. Despite the interpretability benefits of these expert
knowledge-based approaches, they have three key drawbacks. First, for modern networks—comprising hundreds of
thousands of base station nodes—creating separate threshold models for each base station requires substantial expert
input and ongoing maintenance as network topologies change.
This drives operating costs to unaffordable levels. Second,
current methods usually use monitoring systems with just
one variable, analyzing each base station’s KPIs separately.
This design is still vulnerable to false alarms brought on by
single-node data changes and exhibits significant sensitivity to
local noise. Third, the spatial correlation features inherent in
base station clusters are not sufficiently captured by existing
solutions. Notably, in cellular network designs, neighboring
base stations achieve spatial coordination through techniques
like load balancing and handover optimization. However, the
intrinsic spatio-temporal coupling properties of KPI data are
not captured by conventional threshold-based methods, leading
to systematic discrepancies in the assessment of the overall
normal condition of the network [8].
In practical operational scenarios, compared to the discrete
deployment architectures of 3G/4G networks, 5G systems
exhibit a denser network topology. This denser topology
facilitates resource sharing and dynamic scheduling through
clustered configurations rather than relying on individual or
loosely coordinated base stations [9]. A 5G-MNC can be
defined as a closely coordinated cluster of base stations within
specific coverage areas, as illustrated in Fig.1. To ensure
continuous coverage and effective load distribution across 5G
base stations, strong interconnections between wireless nodes
must be maintained across the service area. This architecture
enables seamless handover between multiple base stations
during user mobility, ensures load balancing, and leverages
collaborative virtualization technologies to achieve resource
sharing and dynamic scheduling. This focus on real-time

2332-7731 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

LIU et al.:5G MOBILE NETWORKED CLUSTERS ANOMALY DETECTION UNDER DISTRIBUTION SHIFTS

Fig. 1.

Example of 5G-MNCs, and each node represents a base station.

performance aligns with advancements in related wireless
communications technologies [10].
Therefore, in this study, we conduct anomaly detection in
5G mobile networks through the lens of 5G-MNC architecture.
The methodological strengths are multifold: By establishing
the entire 5G mobile network as a unified monitoring and
modeling architecture, our approach captures spatio-temporal
correlations among network nodes, consequently enhancing anomaly detection performance. System-wide anomaly
detection across the 5G-MNC substantially mitigates the
effects of noise and fluctuations originating from individual
nodes on collective detection performance. The proposed
technique effectively suppresses false positives induced by
unaccounted node interactions, thereby strengthening both
robustness and stability in detection processes. Moreover,
this paradigm promotes data-driven learning mechanisms that
remove dependency on expert-configured thresholds, achieving
dual improvements in the reduction of maintenance costs and
the enhancement of detection efficiency.
From another perspective, distribution shift problems
with 5G-MNC data may compromise the accuracy of
anomaly detection systems. Variations in the environment
are the main cause of these shifts in distribution. Building environment-invariant representations of data is crucial
to reducing the effects of distribution shifts. To learn
invariant representations in this situation, we include a Partial Conditional Invariance Regularization (PCIR) term in
this architecture [11]. By lowering the Maximum Mean
Discrepancy (MMD), we decrease the disparity between representations from various environments. Therefore, due to the
influence of communication environment, distribution shift
problems are commonly present in intelligent wireless communication systems [12]. This research effectively eliminates
the impact of distribution shifts brought on by environmental
changes using causal intervention approaches.
For analyzing complex spatio-temporal interdependencies
within 5G-MNC data, we develop a Doubly Residual
Spatio-Temporal Graph Convolution (DRSTGC) block incorporating two graph convolution components with residual
connections. The primary component systematically incorporates predefined domain knowledge, while the auxiliary
component employs data-driven methodology to address residual patterns unresolved by the preceding module. This
innovative architecture effectively leverages 5G-MNC’s pre-

3601

defined topological characteristics while elucidating intrinsic
synchronization dependencies between base stations. Furthermore, the DRSTGC module incorporates a doubly residual
architecture that simultaneously outputs reconstruction and
hidden representations to enhance the representational capacity of 5G-MNC data. Following two stacked DRSTGC
modules, we implement causal intervention mechanisms to
mitigate distribution shift effects. Finally, we develop a
dual-component architecture comprising discrimination and
reconstruction modules for collaborative anomaly detection,
effectively integrating information from both original data
domains and latent spatial representations. The synergistic
integration of these modules with an adaptive anomaly scoring mechanism enables complementary inference capabilities,
thereby achieving enhanced detection robustness. The main
contributions of this work are summarized as follows:
1) A novel anomaly detection model (Causal-DRSTGC) is
proposed, by combining causal learning with graph learning
mechanisms, which can effectively eliminate environmental confounding factors and address anomaly detection of
spatio-temporal data in distribution shifts.
2) The introduction of a joint optimization mechanism
enables the synergistic integration of discrimination-based and
reconstruction-based modules, which are implemented in the
latent and original data domains, respectively. This integration
is designed to achieve superior model performance.
3) Extensive experiments on real-world 5G-MNC datasets
and public industrial datasets validate the superiority of the
proposed method in various application scenarios.
II. R ELATED W ORK
A. Mobile Network Anomaly Detection
The domain of mobile network anomaly detection has
seen extensive methodological development, with various
approaches investigating distinct strategies and frameworks
for identifying network irregularities. Dridi et al. [13] developed an automated framework that employs machine learning
techniques, including One-Class Support Vector Machines,
Support Vector Regression, and Long Short-Term Memory
(LSTM), to detect network anomalies in cellular traffic in real
time. Sangaiah et al. [14] devised an automated procedure that
integrates unsupervised learning with classification algorithms
to detect and diagnose active failures in mobile networks by
combining network-collected data with manual drive testing.
The data generated by 5G-MNCs exhibit inherent nonlocalized spatio-temporal dependencies and temporal state
relationships between current and historical data matrices [15].
The inherent complexity of these spatio-temporal characteristics substantially increases anomaly detection difficulty for
5G-MNC data streams. Consequently, conventional statistical
approaches and machine learning methods may be inadequate,
requiring specialized computational architectures for 5G-MNC
anomaly detection.
B. Deep Learning Approaches for Anomaly Detection
The effectiveness of deep learning-based methods in
anomaly detection has been empirically validated across

3602

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

multiple domains, establishing a robust theoretical foundation
for further exploration and practical implementation [16],
[17], [18], [19]. Particularly notable contributions include
Thill et al. [20], who developed a temporal convolutional
autoencoder (AE) for ECG signal anomaly detection. Li et al.
[21] proposed a stacked variational autoencoder (VAE) integrated with GNNs to address time series anomaly detection
challenges. Lunardi et al. [22] introduced an unsupervised
deep anomaly detection system that employs convolutional
autoencoding for network traffic profiling from initial packet
sequences, incorporating adversarial training strategies to
enhance detection robustness. Deng and Hooi [23] established
a GNN-based predictive paradigm that identifies anomalies
through systematic deviations between predicted and observed
values. Liu et al. [24] employed a Temporal Convolutional
Network (TCN)-based deep learning approach for channel
prediction, with its computationally intensive tasks handled
by Mobile Edge Computing (MEC) to reduce the response
time. Huang et al. [25] devised HitAnomaly, a hierarchical Transformer-based model for log anomaly detection that
effectively processes unseen log templates and anomalous
parameter values.
Nam et al. [26] proposed the Dual-Time-Frequency
(DualTF) model, which employs a nested sliding window
mechanism: the outer and inner windows process temporal
and frequency domain features, respectively; this synchronizes
anomaly scoring across domains to resolve time-frequency
granularity discrepancies. Lee et al. [27] introduced an
Uncertainty-aware Dynamic Thresholding (UDT) method
that dynamically adjusts detection thresholds by quantifying epistemic and aleatoric uncertainties in temporal data
for time-series anomaly detection. Liu et al. [28] developed TopoGDN for fine-grained modeling of temporal and
feature dimensions. The model utilizes multi-scale temporal
convolution modules for feature extraction and incorporates
graph structure learning with topological attention mechanisms. This combined approach effectively captures both
inter-feature dependencies and high-order topological patterns.
Dai and Chen [29] presented a Graph-Augmented Normalizing
Flow (GANF) model that establishes causal dependencies
among multivariate time series through Bayesian networks
while employing normalizing flows for density estimation
in anomaly detection. Wang et al. [30] devised COCA,
a deep contrastive one-class framework combining contrastive
learning with normality assumptions for time-series anomaly
detection. Yang et al. [31] proposed DCdetector, featuring a
dual-attention contrastive architecture with multi-scale patch
design that generates multi-view temporal representations and
enhances discriminative power through contrastive loss optimization. Meli [32] proposed a novel OUAD, using causal
discovery to learn a normal causal graph of the system, and
it evaluated the persistency of causal links during real-time
acquisition of sensor data to promptly detect anomalies.
The above methods typically operate under the fundamental assumption that models cannot accurately reconstruct
or predict unseen anomalous samples, thereby differentiating
between normal and anomalous instances. However, their
modeling approaches may inadvertently induce overfitting,

potentially enabling even anomalous data to achieve satisfactory reconstruction fidelity [33]. Furthermore, 5G network measurement data inherently has complex dynamic
spatio-temporal characteristics and is susceptible to distribution shifts—making it imperative to develop novel
methodologies tailored for 5G-MNC data.
C. Out-of-Distribution (OOD) Challenges With Temporal
Shift
Inspired by OOD graph learning advancements, researchers
have recently focused on temporal shift-induced OOD problems. For instance, CauSTG [34] introduces a causal framework that transfers both local and global spatio-temporal
invariant relationships to OOD scenarios. CaST [35] employs a
structural causal model (SCM) to interpret the data generation
process in spatio-temporal graphs, and uses backdoor adjustment to decouple invariant features from temporal environments. STVE [36] encodes traffic data into two disentangled
representations and incorporates contextual information from
spatio-temporal environments—using them as self-supervised
signals to enhance the generalizability of context-oriented
representations and improve OOD performance.
However, current research mostly focuses on predicting
temporal drift but has limited exploration of time series
anomaly detection. Existing detection methodologies mainly
address anomalies under identical training-testing distribution
assumptions. However, experiments show significant performance degradation when facing data with diverse distribution
shifts in real applications.
III. P ROBLEM S TATEMENT
This study formulates the anomaly detection problem
in 5G Mobile Network Configuration (5G-MNC) as a
spatio-temporal anomaly detection task. As illustrated in Fig.2,
the 5G-MNC system is formally represented as a weighted
graph G = (V, E, A), where the node set V comprises N base
stations (N = |V |); the edge set E captures inter-base station connectivity relationships; the weighted adjacency matrix
A ∈ RN ×N is constructed through geographical distance
metrics, with each matrix element Ai,j corresponding to the
geographical distance between nodes vi and vj .
The 5G-MNC state at each timestep t is mathematically
represented as a graph signal matrix Xt ∈ RN ×C , where
C denotes the feature dimensionality. To effectively capture temporal dependencies, we employ a sliding window of
length T to construct spatio-temporal feature sequences Xt =
(Xt−T +1 , Xt−T +2 , . . . , Xt ), as model inputs. The anomaly
detection objective involves generating binary classification
labels y ∈ {0, 1} for given samples (the numbers 0 and
1 represent normal and anomalous, respectively).
Notably, this study adopts a semi-supervised learning
paradigm: the training set X contains exclusively normal
samples, while the testing set X ′ incorporates both normal and
anomalous instances for model validation. This configuration
effectively simulates practical engineering requirements in
application scenarios where anomaly samples are scarce but
require precise identification.

LIU et al.:5G MOBILE NETWORKED CLUSTERS ANOMALY DETECTION UNDER DISTRIBUTION SHIFTS

3603

B. Doubly Residual Stacking Architecture

Fig. 2.

Graph structure of 5G-MNC.

IV. P ROPOSED A PPROACH
This study introduces a deep spatio-temporal graph convolutional anomaly detection architecture, with its core
architecture depicted in Fig.3. The methodology employs
stacked Doubly Residual Spatio-temporal Graph Convolution
(DRSTGC) blocks design. Each DRSTGC block contains
two complementary graph convolutional modules: spatiotemporal graph convolution module (STGCM) synchronously
extracts spatio-temporal correlations based on existing graph
structures, and auxiliary spatio-temporal graph convolution
module (ASTGCM) learns hidden spatio-temporal dependencies. To address distribution shifts in practical scenarios,
a novel intervention module is integrated to mitigate confounding factor interference. The architecture ultimately performs
anomaly detection through synergistic integration of discrimination and reconstruction modules. They effectively integrate
information from both the original data domain and latent
spatial representations. By integrating these modules with an
adaptive scoring mechanism, the proposed model leverages
their complementary strengths to achieve more robust anomaly
detection. Subsequent subsections offer detailed descriptions
of each individual component.
A. Temporal Embedding
The KPI metrics generated by 5G-MNC systems are significantly influenced by user behaviors and temporal patterns,
consequently exhibiting seasonal variations that recur at periodic intervals (e.g., daily and weekly cycles).
To comprehensively model periodic dependencies in 5GMNC base stations, we employ temporal embedding to encode
each timestep into vector representations. For a given timestep,
two one-hot encoded vectors are generated based on its
hour-of-day and day-of-week attributes. These vectors are
subsequently concatenated and projected through a fully connected layer to obtain temporal embeddings mt ∈ Rm . For
the t-th temporal segment containing historical timesteps, the
corresponding temporal embedding matrix is formulated as
Mt = [mt−T +1 , mt−T +2 , . . . mt ]T ∈ RT ×D . The resultant
temporal embeddings encapsulate critical timing information
that is subsequently integrated into DRSTGC blocks for
spatio-temporal modeling.

Inspired by the doubly residual architecture of NBEATS [37], this study proposes a novel Doubly Residual
Spatio-temporal Graph Convolution (DRSTGC) block to
model implicit synchronous dependencies among base stations
in 5G Mobile Network Clusters (5G-MNC). Our approach
demonstrates significant architectural and functional innovations compared to N-BEATS:
Multidimensional Expansion: While N-BEATS addresses
temporal dependencies in general time series through predictive sequence modeling, DRSTGC employs spatio-temporal
graph convolutions to capture complex spatio-temporal correlations in input sequences. This extension enables effective
modeling of both spatial topological relationships between
base stations and temporal dynamics of signal propagation.
Functional Innovation: Diverging from N-BEATS’s doubly
residual architecture for time-series forecasting, our structure enhances representational capacity for anomaly detection
(l)
tasks. As illustrated in Fig.4, the input Xt to the l-th block
(l)
generates two outputs: Reconstruction Output X̂t : Partial
reconstruction results removing resolved explicit features.
(l)
Hidden Representation Ot : Residual-connected features capturing unresolved latent patterns.
Progressive Feature Decoupling: The cascaded residual
architecture enables hierarchical feature extraction. In the
reconstruction path, previous modules progressively strip
(l−1)
resolved explicit features X̂t
, forcing subsequent modules
to focus on unresolved information. The collective output of
all blocks is formulated as
X (l)
X̂t =
X̂t
(1)
Ot =

l
X

(l)

Ot

(2)

l

The final reconstruction X̂t constitutes the aggregated summation of partial reconstructions from all blocks, achieving
hierarchical decomposition while enabling interpretable output
generation. Moreover, the reconstruction representation can
uniquely identify this segment of temporal data as label
information within the causal intervention module. Analogously, the ultimate hidden representation Ot , emerges as the
cumulative integration of latent partial representations. Hidden
representations can serve as core temporal information for
causal intervention within the causal intervention module. This
multi-scale aggregation mechanism facilitates multi-view representation aggregation and enables multi-scale latent pattern
extraction, thereby enhancing anomaly detection sensitivity.
C. Doubly Residual Spatio-Temporal Graph Convolution
Block
We propose the Doubly Residual Spatio-temporal Graph
Convolution (DRSTGC) block to simultaneously capture
temporal and spatial dependencies in 5G-MNC data.
As depicted in Fig.5, the proposed architecture comprises
two spatio-temporal graph convolution modules with doubly residual connections. The primary module systematically
incorporates domain-specific prior knowledge, while the

3604

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

auxiliary module subsequently processes residual information
unresolved by its predecessor.
1) Spatio-temporal Graph Convolution Module (STGCM):
The STGCM is designed to synchronously extract
spatio-temporal correlations through integrated Graph
Convolutional Gated Recurrent Units (GCGRUs) [38] and
fully connected layers. Given a graph G = (V, E, A), the
spectral graph convolution operation ∗ g on input signal X
can be formally defined as:
Wg ∗G X = σ (LXWg + bg )

(3)

1
1
where L = I − D−( 2 ) AD−( 2 ) denotes the Laplacian matrix,
I is the identity matrix, and D is the degree matrix. Wg and bg
are the learnable parameters. σ is the ReLU activation function. In the construction of GCGRU, the matrix multiplication
in GRU is replaced with graph convolution operation. For
convenience of presentation, omitting the superscript and the
operation of GCGRU can be defined as

zt = σ (Wz ∗G [It ; Ht−1 ] + bz )
rt = σ (Wr ∗G [It ; Ht−1 ] + br )
ct = tanh (Wc ∗G [It ; rt ⊙ Ht−1 ] + bc )
Ht = zt ⊙ Ht−1 + (1 − zt ) ⊙ ct

(4)
(5)
(6)
(7)

function is applied to eliminate weak connections, followed
by a softmax operation to normalize the learned auxiliary
adjacency matrix.
Subsequently, the self-learned auxiliary graph G =
(V, E, Aaux ) undergoes the same Graph Convolutional Gated
Recurrent Unit (GCGRU) operations as the STGCM. The
output of the GCGRU is then fed into two fully connected
layers with ReLU activation functions to generate partial
reconstructions and hidden representation outputs. The operations are formally defined as follows:


(l,2)
(11)
Ot
= σ U1l,2 Htl,2 + bl,2
1
(l,2)

X̂t
(l,2)

(l,1)

(l,1)

where Ot
and X̂t
are the partial hidden representation
and the partial reconstruction of STGCM, and U1l,1 , U1l,1 , bl,1
1
and bl,1
2 are learnable parameters.
2) Auxiliary Spatio-temporal Graph Convolution Module (ASTGCM): The ASTGCM serves as a complement to
the STGCM, addressing information flows that cannot be
resolved through prior knowledge derived from available graph
structures. While the ASTGCM shares the same fundamental architecture as the STGCM, it distinguishes itself by
employing an auxiliary adjacency matrix to autonomously
learn unresolved hidden spatial dependencies. This auxiliary
adjacency matrix is designed to complement the prior graph.
Specifically, two randomly initialized node embeddings with
learnable parameters are defined, and the auxiliary adjacency
matrix is formulated as:

Aaux = sofmax σ E1 ET
(10)
2
Here, E1 and E2 represent the source and target node
embeddings, respectively, where their multiplicative product
defines the spatial dependency weights. The ReLU activation

(12)

(l,2)

where Ot
and X̂t
are the partial hidden representation
and the partial reconstruction of ASTGCM.
3) Block Output: The outputs of the doubly residual
spatio-temporal graph convolution block consist of two parts,
one is the fusion of the partial hidden representations of
(l,1)
(l,2)
Ot
and Ot , and the other is the summation of the
(l,2)
(l,1)
and X̂t . The
partial reconstruction representations of X̂t
outputs are defined as
(l)

(l,1)

Ot = σ(W l [Ot
(l)

(l,2)

; Ot

(l)
(l,1)
(l,2)
X̂t = X̂t
+ X̂t

where It = Xt∗ + mt

denotes the summation of input and
temporal embedding, and Xt∗ ∈RD represents the result of a
fully connected transformation of Xt , aiming to have the same
dimension as mt . Ht denotes the output of GCGRU at time t.
WZ , Wr , Wc , bz , br and bc are learnable parameters.
Then, two branches consisting of two fully connected layers
are used to output partial reconstruction and partial hidden
representation. For the STGCM in the l-th block, the outputs
are defined as


(l,1)
Ot
= σ U1l,1 Htl,1 + bl,1
(8)
1


(l,1)
X̂t
= σ U2l,1 Htl,1 + bl,1
(9)
2

= σ(U2l,2 Htl,2 + bl,2
2 )

] + bl )

(13)
(14)

(l)

where Ot and X̂t are the hidden representation and reconstruction outputs of the l-th block, respectively.
To address the interference of confounding factors in time
series data under distribution shifts, this study proposes a
causal intervention module. It mitigates the impact of distributional variations by introducing a PCIR regularization term.
(l)
(l)
Therefore, Ot and X̂t are fed into the intervention module
to compute the causal loss. Finally, the respective partial
(l)
reconstructions X̂t of each DRSTGC block are summed and
fed into the reconstruction module to compute reconstruction
(l)
scores. The partial hidden representations Ot are aggregated and delivered to the discrimination module to calculate
anomaly probabilities.
D. Intervention Module
1) Invariant Representation Context Under Distribution
Shifts: Our formulation operates under the assumptions of an
environmental set (denoted as E) and a sample space (denoted
as X) of time series data. We consider a sliding time window
sample Xt drawn from an unknown distribution pn , which is
primarily concentrated on a subset N ⊆ X defining the normal
class. Given Xt ∼ pn , we decompose Xt into a pair of random
variables Xa and Xe such that X = (Xa , Xe ). Here, the
environment E exclusively influences Xe . Conceptually, Xa
represents the relevant features of time series X that determine
its anomaly status, while Xe represents style features of time
series X that determine its environmental status. While these
style features remain unaffected by the anomaly status of the
time series, they are influenced by environmental conditions.
Building on causal inference theory [11], we consider the
process from Xt to Ot in Fig.4 as the encoder f : X → O that

LIU et al.:5G MOBILE NETWORKED CLUSTERS ANOMALY DETECTION UNDER DISTRIBUTION SHIFTS

Fig. 3.

Fig. 4.

3605

Overall architecture of the model.

Construct of doubly residual stacking architecture.

Causal-DRSTGC model to obtain an invariant representation
O of the original sample X. This enables more effective
processing in the subsequent module for calculating more
accurate anomaly scores. Below, we elaborate on the main
workflow of the causal intervention module.
Firstly, we introduce a causal graph for anomaly detection
based on a structural causal model (SCM), as illustrated in
Fig.6. We treat X̂ as the environment E described above.
As discussed in Section IV-B, X̂ serves as the reconstruction
representation of X, functioning to distinguish samples X
and assign them to their corresponding environmental labels.
Therefore, we further obtain:
We say O is an invariant representation of X under domain
shift if
′

pdo(X̂=e) (O = ·) = pdo(X̂=e ) (O = ·) , f oranye, e′ ∈ X̂.
(16)

Fig. 5. Construct of Doubly Residual Spatio-temporal Graph Convolution
block(DRSTGC block).

maps raw observations to a representation space O.Here, O =
f (X) constitutes the final representation. Domain invariance
is formalized as follows:
Definition. We say O is an invariant representation of X
under domain shift if
′

pdo(E=e) (O = ·) = pdo(E=e ) (O = ·) , f oranye, e′ ∈ E.
(15)
The symbol do denotes an intervention operation. That
is, the intervention E = e is represented as do (E = e),
which differs from observing E = e through existing data. p
denotes probability. Invariant representations prevent anomaly
detectors from misclassifying phenomena induced by domain
shift. By definition, these representations O exhibit resistance
to variations in E.
Therefore, this module aims to derive a causal loss function
as a partial conditional invariance regularization (PCIR) term
through causal intervention theory. This function trains the

Xa and Xe denote relevant features and the style features,
respectively. The hidden representation O represents the final
representation of time series X. We introduce new random
variable W that is a binary variable indicating whether a
sample is normal (W = 0) or anomalous (W = 1).
It establishes causal relationships among five variables,
where links from one variable to another indicate causation:
cause → effect. We present the following interpretation of
SCM:
Xa → O: Since Xa is the primary feature and f is the
mapping from X to O, any probability associated with X can
be replaced by O. O also serves as the final output of the
model, used to determine whether a sample is anomalous.
Xa ← W → Xe : W fundamentally determines the
sample attribute X, thus constituting a causal relationship, and
consequently influences both Xa and Xe .
X̂ → Xe → O: The reconstruction representation X̂ is
treated as an environmental label at the causal level, uniquely
determining the style features Xe within the sample. Subsequently, these style features exert a certain influence on O.
Theorem 1: Suppose that f learns an invariant representation, O⊥X̂.
Proof. Since f learns an invariant representation and is
measurable, O becomes Xa measurable. This implies that any

3606

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

representation Ot . This enhances the generalization capability
of Causal-DRSTGC under distribution shifts. Moreover, the
proposed model automatically generates environment labels
through the reconstruction patterns decomposed by DRSTGC,
eliminating the need for manual annotation and better suiting
real-world application scenarios.
E. Discrimination Module

Fig. 6.

Causal graph for anomaly detection.

probability involving events of O can be expressed in terms
of probabilities involving Xa . It thus suffices to demonstrate
Xa ⊥X̂. We prove this via d-separation. Note that there are
two paths from Xa to X̂. One via W and the other via O.
The path via W is blocked because Xe is a collision, and
neither Xe nor its descendant O are observed. The path via O
is blocked because O is a collision with no descendants and
is not observed. Hence, Xa ⊥X̂.
The
fundamental
challenge
lies
in
ensuring
statistical independence between O and X̂.If this
independence holds, we find that pdo(X̂=e) (O = ·) =
′
pdo(X̂=e ) (O = ·) , f oranye, e′ ∈ X̂. By definition, O is an
invariant representation of time series X.
Secondly, while counterfactual examples are generally
inaccessible, enforcing appropriate conditional independence
constraints can still induce counterfactual invariance. In practice, this condition may be formulated as M M D(p(O =
·|X̂ = e), p(O = ·|X̂ = e′ )) = 0, where M M D denotes
the Maximum Mean Discrepancy. To capture complex highdimensional differences, we utilize a cosine kernel, which
is particularly effective in comparing the angular similarity
between feature vectors.
X
Lmmd =
MMD
e, e′ ∈ X̂ ,e̸=e′



p(Ot = · | W = ·, X̂t = e), p(Ot = · | W = ·, X̂t = e′ )
(17)

The causality loss function, as shown in Eq.(17), can serve
as a PCIR term. Specifically, due to the temporal continuity,
we randomly set the window value to 10. Additionally, there is
a one-to-one correspondence between every element of X̂t and
Ot . For each value of X̂t and Ot , we obtain the corresponding environmental label ei , i ∈ [1, 10], from reconstruction
representation X̂t .And we obtain the corresponding hidden
representation oi , i ∈ [1, 10], from hidden representation Ot .
We then apply M M D (oi , oj ) = 0, f oranyei ̸= ej , thereby
obtaining the corresponding causal loss.
Furthermore, we compute the causal loss separately for
normal samples (W=0) and anomalous samples (W=1),
ultimately achieving a stronger decoupling between
the reconstructed representation X̂t and the hidden

Within the discrimination module, the learned hidden representations are employed to distinguish anomalous data in
the latent space. However, during 5G network operation
and maintenance, generating sufficient anomalous samples
for supervised training is usually infeasible—anomalies occur
infrequently. To address this limitation, we implement a computationally efficient negative sampling strategy to generate
pseudo-anomalous samples. Given a temporal segment Xt ,
we apply a permutation perturbation strategy to produce
negative samples Xt′ . Specifically, the permutation operation
divides the signal into randomly sized subsequences and
shuffles them, with each base station sequence undergoing
independent permutation to deliberately disrupt inter-sequence
correlations. Subsequently, random temporal jittering is introduced to the permuted segments.
The discrimination module processes hidden representations
from either original inputs or negative-sampled data through a
gated recurrent unit (GRU) layer, which sequentially computes
hidden states across temporal intervals. The final hidden
state is then passed to a fully connected layer with sigmoid
activation to derive anomaly scores within [0,1] for each input
segment, and to calculate the discrimination loss. The module
is ultimately trained in an end-to-end manner using pseudo
labels.
F. Model Training
Building upon the preceding analysis, we propose the utilization of MMD between two distributions as the driving
mechanism for invariance induction. Additionally, we introduce Eq.(17) as a PCIR term specifically applied to anomaly
detection in time series under distribution shifts.
The discrimination and reconstruction modules exhibit distinct yet complementary strengths, forming mutually reinforcing components. Specifically, the reconstruction module learns
latent representations by reconstructing original observations,
with anomaly detection achieved through reconstruction errors
since unseen anomalies tend to induce substantial deviations. Nevertheless, the reconstruction-based module primarily
focuses on sample reconstruction fidelity while ensuring
distinctiveness between normal and anomalous sample representations. Consequently, this approach may enable accurate
reconstruction of anomalous data.
The discrimination module is trained to identify anomaly in
temporal evolution patterns, guaranteeing discriminative separability in the latent space. This effectively compensates for the
limitations inherent in reconstruction-based methodologies.
Accordingly, the composite loss function is formulated as
the weighted summation of three optimization objectives,

LIU et al.:5G MOBILE NETWORKED CLUSTERS ANOMALY DETECTION UNDER DISTRIBUTION SHIFTS

Algorithm 1 Training procedure of Causal-DRSTGC
Input: Training data set X = {X1 , X2 ,. . . , Xt }, Epoch E.
Output: The learned model parameters Θ.
1: Initialize all parameters;
2: for e = 1, 2,. . . . . . , E do
3: for t = 1, 2, . . . . . . , T do
(1)
(1)
4: Ot , X̂t ← Block 1 (Xt , Mt , E1 , E2 )
(2)
(2)
(1)
5: Ot , X̂t ← Block 2 (Xt − X̂t , Mt , E1 , E2 )
(1)
(2)
6: Ot = Ot + Ot
(1)
(2)
7: X̂t = X̂t + X̂t
8: Generate negative sample Xt′ and perform forward
propagation to obtain the negative representation Ot′ and
the negative reconstruction representation X̂t′ .
9: // Calculate the total loss using
 Eq. (20)
10:
L
=
Lrec Xt , X̂t
+ Ldis (Ot , Ot′ ) +
Lmmd ((X̂t , X̂t′ ), (Ot , Ot′ ))
11: Update model parameters using L;
12: end for
13: end for
14: return The learned parameters.

In this architecture, D denotes the discriminator, where
Ot represents the hidden representation of the input sample,
and Ot′ corresponds to the hidden representation generated
by the negative sampling strategy. The training procedure for
Causal-DRSTGC is outlined in Algorithm 1.
G. Model Inference
As mentioned in previous sections, the reconstruction and
discrimination modules are jointly trained to optimize targets.
As a result, both modules are encouraged to contribute to
anomaly detection cooperatively. In order to do this, we create
a scoring system based on reconstruction and discrimination
that balances each of their contributions, increasing anomaly
detection’s overall efficacy. In particular, given an observation
segment (Xt−T +1 , Xt−T +2 , . . . , X t ), the reconstruction score
is calculated from the deviation between the reconstructed values and the original observations, whereas the discrimination
score, pt is derived from the discriminator’s output probability.
The definition of the inference score st is
T
P

st =
Algorithm 2 Inference procedure of Causal-DRSTGC
Input: Testing data set X = {X1 ,X2 ,. . . ,XT }, model parameter Θ, threshold τ .
Output:The label yt of Xt .
1: Load the trained model parameters Θ;
2: for t = 1, 2, . . . T, do
(1)
(1)
3: Ot , X̂t ← Block 1 (Xt , Mt , E1 , E2 )
(2)
(2)
(1)
4: Ot , X̂t ← Block 2 (Xt − X̂t , Mt , E1 , E2 )
(1)
(2)
5: Ot = Ot + Ot
(1)
(2)
6: X̂t = X̂t + X̂t
7: Calculate the inference score st using Eq. (21);
8: if st >τ then
9:
yt =“Anomalous”
10: else
11:
yt =“Normal”
12: end if
13: end for

denoted as Eq.(20). Here, Lrec represents the reconstructionbased loss, defined as the mean squared error (MSE) between
targets and reconstructed values. Ldis corresponds to the
discrimination loss employing binary cross-entropy. Lmmd
serves as the loss function for the intervention module, which
incorporates the aforementioned regularization strategy. The
hyperparameter α and λ balance the loss contributions of the
three modules.
X
Ldis = −
log(1 − D(Ot )) + log(D(Ot′ ))
(18)
t
T
X

1
∥ Xt+i − X̂t+i ∥22
T i=1

(19)

L = (1 − α)Lrec + αLdis + λLmmd

(20)

Lrec =

3607

∥ Xt−T +i − X̂t−T +i ∥22 +α × (1 − pt )

i=1

1+α

(21)

The hyperparameter α, which balances the contributions
of the two components, will be thoroughly investigated in
the subsequent sensitivity analysis section. An anomaly is
identified when the inference score exceeds a threshold [39],
where this threshold is determined through grid search on the
validation set. The detailed inference procedure is presented
in Algorithm 2.
V. E XPERIMENT
This section begins with an introduction to the dataset
and experimental setup. Subsequently, the performance of
Causal-DRSTGC is validated using real-world operational data
from 5G-MNC systems. A case study is then conducted to analyze experimental outcomes, accompanied by ablation studies
and sensitivity analysis. Finally, the model’s performance is
further validated on industrial datasets, and a complexity
analysis is conducted.
A. Dataset Description
To evaluate the proposed method’s effectiveness, we use
a real-world 5G-MNC dataset. Collected by China Mobile
Communications in Jinan, Shandong Province, it contains Key
Performance Indicator (KPI) records from two 5G-MNCs.
Cluster1 comprises 5 base stations, while Cluster2 consists
of 14 base stations. The selected KPI for anomaly detection
is the average number of Radio Resource Control (RRC)
connections, with data aggregated at 15-minute intervals. The
dataset spans from September 3, 2021, to January 3, 2022.
Table I presents the partition lengths of the training and testing
sets.
In practical applications, decommissioning and shielding
represent two categories of anomalies in the operational maintenance of 5G networks, described as follows:

3608

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

Decommissioning. Base station decommissioning refers to
the phenomenon where base stations unexpectedly go offline
during operation. It is caused by factors like severe weather
and transmission failures, resulting in communication service
interruption.
Shielding. As critical components of mobile communication
systems, base stations play a pivotal role in maintaining
communication quality. However, physical obstructions caused
by billboards and outdoor buildings can degrade signal transmission. Therefore, base station shielding as an anomaly can
affect the daily operation of 5G-MNC.
Fig.7 illustrates two real-world anomaly scenarios involving
14 base stations in a 5G-MNC system, with each subplot
depicting the average number of RRC connections. Fig.7(a)
demonstrates the decommissioning anomaly case, showing
a simultaneous sharp decline in RRC connections across a
group of base stations. As shown in Fig.7(b) for the shielding
anomaly case, a decrease in RRC connections at base stations
B1, B3, B4, and B6 results in a corresponding surge at the
neighboring base stations B2 and B5.
In 5G-MNC systems, anomalies are highly uncommon
in practical scenarios, and existing anomaly datasets remain
insufficient to validate the comparative performance of detection models. To address this, we implemented anomaly
data imputation using the following methodology. Specifically, to simulate base station decommissioning anomalies,
we stochastically reduced the number of users establishing
connections with neighboring base stations at a specified rate
of 0.6 over a given time interval. For base station shielding
anomalies, we proportionally reduced the number of connected
users at a target base station by a defined ratio of 0.6, then
redistributed the reduced connections to its geographically
adjacent base stations based on spatial proximity. Statistical
metrics for both anomaly clusters are provided in Table I.
To more effectively simulate scenarios involving distribution shifts and render the distribution shifts in the testing
sets more pronounced, while simultaneously enabling comprehensive demonstration of our proposed model’s superior
capabilities, we adopted a specific approach. Accordingly,
we manually introduced distribution shifts into the testing sets
of the aforementioned datasets by adjusting the magnitude of
fluctuations to 0.5. Within the middle 70% of the temporal
range, two continuous intervals were selected for each of the
five feature columns, and variance manipulation was applied
to approximately 10% of the data. This process retained the
mean of the selected data segments while randomly altering
the variance of individual data points.
Taking the testing set of Cluster1 as an example (total
sample size: 3,542), two consecutive intervals were chosen
for each of the five feature columns within the middle 70%
of the time series. A total of 342 samples (approximately
9.66%) underwent variance perturbation. Features 1–4 each
had 70 data points modified (1.98% per feature), while Feature
5 contained 62 modified points (1.75%). As exemplified in
Fig.8, the blue curve represents the original time series, and
the orange curve illustrates the modified data distribution.
This experimental design effectively validates the model’s
robustness under variance shifts conditions.

Fig. 7. Two real anomalies in the 5G-MNC data. (a) Decommissioning
anomaly. (b) Shielding anomaly.

TABLE I
C LUSTER 1 AND C LUSTER 2 DATA STATISTICS

B. Experimental Setup
Evaluation Metrics. To measure and evaluate method performance, four standard metrics were employed: precision (P),
recall (R), F1-score (F1), and ROC-AUC (AUC) [40], [41].
In practical applications, anomalies typically manifest as continuous segments; thus, point-wise metrics are not prioritized.
Following the evaluation strategy of [42], if any anomalous
observation exists within a segment, the entire segment is
labeled as the positive class.

LIU et al.:5G MOBILE NETWORKED CLUSTERS ANOMALY DETECTION UNDER DISTRIBUTION SHIFTS

Fig. 8. Samples distribution shift for manual processing. The blue curve
represents the original time series, and the orange curve illustrates the modified
data distribution.

Baselines. The proposed method was compared against
seven baselines: DCdetector (2023), GANF (2022), COCA
(2023), UDT (2025), DUALTF (2024), TopoGDN (2024), and
OUAD (2024). All comparisons adhered to the architectures
recommended in their original publications. Since not all
anomaly detection methods were designed for 5G-MNC scenarios, each model was evaluated across all feasible thresholds,
and experimental results were reported based on the highest
F1-score.
Data Preprocessing. Consistent with [43], Z-score normalization was first applied to the training and testing sets to
enhance the robustness of the proposed method. Additionally,
aligning with [44], the adjacency matrix for 5G-MNC was
computed based on the geographical distances between base
stations within the mobile network cluster. The weighted
adjacency matrix A can be formulated as:
2
2
ηij
ηij
),
i
=
̸
jandexp(−
)≥ϵ
Aij =
δ2
δ2

0, otherwise




exp(−

(22)

where Aij is the weight of the edge, and it is determined by
ηij , which is the geographical distance between base stations
i and j. δ 2 and ϵ are the thresholds to control the distribution
and sparsity of adjacency matrix A, and they are set to 1e-5
and 0.3 in this work, respectively.
C. Experimental Results
In this subsection, we conducted experiments on the realworld 5G-MNC dataset to evaluate the effectiveness of
Causal-DRSTGC against seven baseline methods. Table II
presents the shielding anomaly detection performance comparison between Cluster1 and Cluster2, while Table III
summarizes the decommissioning anomaly detection results.
The best score achieved is highlighted in bold.
The proposed Causal-DRSTGC architecture comprehensively explores spatio-temporal patterns in original 5G-MNC
data through specifically designed components. The STGCM
and ASTGCM modules effectively leverage domain-specific
knowledge to capture inherent synchronous dependencies
within 5G-MNC systems. Discrimination and reconstruction

3609

modules facilitate collaborative anomaly detection in both
original data space and latent feature domains. Furthermore,
the integration of causal graphs with intervention mechanisms
effectively mitigates confounding effects under distribution
shifts, significantly enhancing model robustness. Experimental
results demonstrate that Causal-DRSTGC achieves state-ofthe-art performance compared to existing methods.
Shielding anomalies differ fundamentally from decommissioning scenarios in 5G-MNC operations. While decommissioning involves simultaneous failures across multiple base
stations within a region, shielding anomalies typically occur
within individual base stations, where adjacent nodes compensate through dynamic traffic redistribution. This distinction
results in stronger spatial dependencies during shielding events
compared to decommissioning scenarios. Causal-DRSTGC
effectively models evolutionary relationships between base
stations and their neighbors through spatio-temporal correlation mining, with particular sensitivity to dependency
alterations caused by shielding anomalies. This capability
positions Causal-DRSTGC as a promising solution for 5GMNC anomaly detection challenges.
To comprehensively evaluate the scalability and robustness
of Causal-DRSTGC on large datasets with varying topologies,
we expanded our data scope to clusters of different scales: 2,
4, 6, 8, 10, 12, 14, 16, and 19 nodes. Results demonstrate that
Causal-DRSTGC maintains stably high performance across
clusters of all scales, enabling reliable scaling to larger datasets
and adaptation to diverse topologies. Experimental results are
shown in Fig.9.
To rigorously test the model’s adaptability to real-time
environmental changes and dynamic topology shifts, we randomly altered the adjacency relationships among nodes four
times within a 16-node cluster, simulating continuous network
topology evolution. Experimental results demonstrate that our
model continues to exhibit robust performance, effectively
proving its stability and adaptability to dynamic 5G network
environments. Experimental results are shown in Fig.10.
To validate the impact of long-range temporal and spatial
dependencies across multiple nodes on anomaly detection,
we further conducted the following experiments. Specifically,
we set the time window size to 100 sample points. On the
Cluster1 dataset, we removed one time window, three consecutive time windows, and three non-consecutive time windows
respectively, and performed anomaly detection. The detection
results are shown in Table IV, with the maximum values of
the core metrics F1-score and AUC highlighted in bold. The
results show that even a small amount of missing historical
data has an impact on anomaly detection results, which proves
that the model can extract effectively long-range dependencies
from historical time-series data.
Subsequently, from a spatial perspective, on the Cluster1
dataset, we removed the adjacency edges of node 5, the
adjacency edges between nodes 4 and 5, and the adjacency
edges between nodes 3, 4, and 5, respectively, as illustrated
in Fig.11. The detection results are shown in Table V, with
the maximum values of the core metrics F1-score and AUC
highlighted in bold. The findings indicate that the absence
of link relationships from the original cluster reduces the

3610

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

Fig. 11. Node relationship diagram after removing adjacent edges of specific
nodes.

Fig. 9.
Performance of clusters with different numbers of nodes. The
blue curve represents shielding anomalies, and the orange curve represents
decommissioning anomalies.

Fig. 10.
Performance of different adjacency relationships in a cluster
with 16 nodes, where the first row shows topological structures of different
adjacency relationships among 16 nodes, the second row shows performance
metrics for shielding anomalies and the third row shows performance metrics
for decommissioning anomalies.

performance of anomaly detection to varying degrees, which
demonstrates that the proposed model can capture spatial
relationships between non-directly adjacent nodes for carrying
out anomaly detection.
To comprehensively evaluate our model’s adaptability
beyond a single KPI, we conducted additional experiments
using the signal strength (RSRP) metric on the original Cluster1 and Cluster2 datasets. As shown in Table II and Table III,
the model still achieves competitive F1-scores and AUC values
for both shielding and decommissioning anomalies.
D. Ablation Study
To investigate the effectiveness of distinct components in
Causal-DRSTGC for anomaly detection, we employed the

Cluster2 dataset for ablation studies in this section. Specifically, we disabled individual modules within Causal-DRSTGC
for systematic evaluation. w/o STGCM and w/o ASTGCM
denote the variants where the spatio-temporal graph convolution module (STGCM) and auxiliary spatio-temporal
graph convolution module (ASTGCM) are deactivated in each
block, respectively. The w/o Reconstruction variant performs
anomaly detection exclusively through the discrimination
mode, while the w/o Discrimination variant relies solely on the
reconstruction mode. The w/o Intervention variant eliminates
the causal intervention mechanism. As shown in Table VI,
experimental results confirm the indispensability of all aforementioned modules in Causal-DRSTGC.
In the w/o ASTGCM configuration, only predefined
topological information from 5G-MNC is utilized for representation learning, which restricts comprehensive exploration
of 5G-MNC data characteristics. Similarly, disabling STGCM
prevents full exploitation of prior knowledge, emphasizing the
complementary roles of both modules. The absence of the
reconstruction module confines anomaly detection to latent
space analysis, neglecting informational cues from original data. Conversely, removal of the discrimination module
prioritizes reconstruction fidelity while disregarding critical
discriminative features that separate normal and anomalous
samples. Eliminating the intervention module impairs the
model’s capacity to address distribution shifts, ultimately
degrading detection performance.
To intuitively validate the effect of causal intervention
module and the discrimination module, we provide a comparative visualization of the model’s latent representations in
Fig. 12. Specifically, we selected a continuous sequence with
anomalies and visualized the model’s output representations.
We first reduced the dimensions to 2D space via UMAP, then
generated scatterplots for visualization.
Fig.12(a) illustrates the mapping of the proposed model,
while Fig.12(b) depicts the visualization without the intervention module. A stark contrast can be observed: the
representations in Fig.12(a) exhibit tighter, more structured
clusters corresponding to normal and anomalous states. This
suggests that the intervention module effectively disentangles
the confounders, allowing the model to learn more invariant
and robust representations that are irrelevant to distribution

LIU et al.:5G MOBILE NETWORKED CLUSTERS ANOMALY DETECTION UNDER DISTRIBUTION SHIFTS

3611

shifts. In contrast, the features in Fig. 12(b) are more dispersed and overlapping. This dispersion indicates that the
ablated model is susceptible to spurious correlations introduced by shifting data distributions. This visual evidence
directly supports our quantitative results in Table II and
Table III, explaining why the intervention module contributes
to a significant accuracy improvement. That is, it guides the
model to base its decisions on relevant features rather than on
confounding factors.
Fig.12(c) presents the visualization without the discrimination module. It further elucidates that integrating the
discrimination module into the hidden representation imposes
direct constraints on the distribution of normal and anomalous samples in the latent space, thereby enhancing model
performance.
Collectively, architectural ablation of any module degrades
detection efficacy.
E. Case Study
To visually demonstrate the anomaly detection performance of Causal-DRSTGC on 5G-MNC data, Fig.13 and
Fig.14 presented two distinct visualization results. Specifically,
we selected two anomalous 5G-MNC data segments from
Cluster1 and Cluster2 datasets, respectively, then computed
and displayed their anomaly scores. Fig.13 illustrates a shielding anomaly detection result on Cluster1, where node B3
exhibits a significant performance decline in the anomalous
region, simultaneously inducing concurrent load increases in
its associated nodes B1, B4, and B5. Fig.14 demonstrates a
decommissioning anomaly detection result on Cluster2, where
a group of neighboring base stations (B3, B8, B11, B12,
and B13) show synchronized reductions in RCC connections
within the anomalous region. Notably, in both cases, CausalDRSTGC promptly generates conspicuous spike alerts.
Furthermore, in the architectural design of CausalDRSTGC, the ASTGCM module employs an auxiliary
self-learned adjacency matrix to capture unresolved hidden
spatial dependencies, serving as complementary information
to the predefined graph structure. To validate this mechanism, we conducted a case study visualizing the self-learned
adjacency matrix. Specifically, we presented the geographical
layout of base station B7 and its neighbors, along with the
corresponding rows from both the predefined adjacency matrix
and the self-learned matrix in Fig.15. Blue markers denote
the top three neighbors specified in the predefined adjacency
matrix for node B7, while brown markers indicate the top three
neighbors identified in the self-learned matrix. The visualization reveals three additional base stations in the self-learned
matrix that, despite lacking direct adjacency in the predefined
structure, maintain relatively close geographical proximity
and demonstrate measurable influence on B7’s actual operational status. This evidence confirms that the self-learned
matrix effectively supplements the predefined graph structure,
enabling ASTGCM to uncover latent spatial relationships.
Given the multi-stage architecture with stacked DRSTGC
blocks, there is a possibility of error propagation through the
layers. We conducted a controlled experiment in which artificial errors were introduced after the first DRSTGC block. For

Fig. 12. Mapping of different variants of the model in two dimensions (red
dots are anomalous samples, blue dots are normal samples).

specific details, please refer to the Appendix A (Supplementary
Material).
It is common for base stations to experience fault recovery
scenarios in real applications. To validate the model’s adaptability in such cases, we manually added more pronounced
fault data to simulate the kind of transition processes and test
the proposed model. For specific details, please refer to the
Appendix E (Supplementary Material).
In addition, the impact of extreme weather is also a factor
that base stations need to consider in practical scenarios.
Hence, we simulated the data fluctuations and distribution

3612

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

TABLE II
P ERFORMANCE COMPARISON OF SHIELDING ANOMALY DETECTION FOR C LUSTER 1 AND C LUSTER 2

TABLE III
P ERFORMANCE COMPARISON OF DECOMMISSIONING ANOMALY DETECTION FOR C LUSTER 1 AND C LUSTER 2

changes caused by extreme weather conditions (such as heavy
rain and blizzards) and further validate the performance of
model. For specific details of experiments, please refer to the
Appendix F (Supplementary Material).
F. Sensitivity Analysis
During model training, the hyperparameters α and λ balance
the loss contributions of the reconstruction, discrimination,
and intervention modules, which critically influence anomaly
detection performance in 5G-MNC systems. To analyze the
sensitivity of Causal-DRSTGC, extensive experiments were

conducted using the Cluster1 and Cluster2 datasets. Specifically, we evaluated the recall, precision, F1-score, and AUC
for decommissioning anomalies and shielding anomalies under
varying α values, with results visualized in Fig.16 and Fig.17.
For Cluster2, experimental results demonstrate that the
model achieves optimal overall performance for shielding
anomalies at α = 0.1 and λ = 0.1, while the optimal
configuration for decommissioning anomalies occurs at α =
0.3 with λ = 0.1. The reconstruction module learns data
distributions by minimizing the mean squared error between
inputs and outputs. However, the scarcity of anomalous samples in detection tasks may render this module sensitive to

LIU et al.:5G MOBILE NETWORKED CLUSTERS ANOMALY DETECTION UNDER DISTRIBUTION SHIFTS

3613

TABLE IV

TABLE VI

P ERFORMANCE COMPARISON OF TEMPORAL RELATIONSHIPS AFFECTED
BY HISTORICAL TIME - SERIES . D0 INDICATES ORIGINAL DATA . D1
INDICATES DATA AFTER REMOVING ONE TIME WINDOW. D2 INDI -

C OMPARISON OF DIFFERENT VARIANTS

CATES DATA AFTER REMOVING THREE CONSECUTIVE TIME
WINDOWS . D3 INDICATES DATA AFTER REMOVING THREE
NON - CONSECUTIVE TIME WINDOWS

TABLE V
P ERFORMANCE COMPARISON OF SPATIAL RELATIONSHIPS AFFECTED BY
NON - ADJACENT NODES . D0 INDICATES ORIGINAL DATA . T1 INDICATES
THE DATA AFTER REMOVING THE ADJACENT EDGES OF NODE 5.
T2 INDICATES THE DATA AFTER REMOVING THE ADJACENT
EDGES OF NODES 4 AND 5. T3 INDICATES THE DATA AFTER
REMOVING THE ADJACENT EDGES OF NODES 3, 4, AND 5

noise. Concurrently, maintaining partial reconstruction constraints helps capture spatio-temporal dependencies among
base stations, providing auxiliary information for the discrimination module. The discrimination module employs binary
cross-entropy loss to distinguish normal samples from pseudoanomalies. Higher weights prioritize discrimination capability
enhancement, amplifying representational divergence between
normal and anomalous samples to improve detection sensitivity for rare anomalies. The configuration λ = 0.1 balances
robustness and flexibility, suppressing distribution shifts from
environmental factors while preserving critical spatio-temporal
patterns related to anomalies. Thus, for Cluster2, we select

Fig. 13.

Case of shielding anomaly detection result on Cluster1.

Fig. 14.

Case of decommissioning anomaly detection result on Cluster2.

α = 0.1 and λ = 0.1 for shielding anomalies and α = 0.3 with
λ = 0.1 for decommissioning anomalies.

3614

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

Fig. 15. Locations of base station B7 and its neighbors (each marker denotes
a base station). The row of B7 in the adjacency matrix (blue) and the row of
B7 in the learned matrix (brown).

For Cluster1, experimental results reveal that α = 0.5 and
λ = 0.1 yield optimal performance for both anomaly types.
Compared with Cluster2, Cluster1 contains fewer base stations with lower feature dimensionality, exhibiting simpler
spatio-temporal dependencies but more pronounced localized
distribution disturbances. The higher α value (0.5) imposes
stronger reconstruction constraints, effectively suppressing
noise interference in low-dimensional feature space through
enhanced input-output alignment while preserving essential
spatio-temporal correlations. Furthermore, λ = 0.1 minimizes
representation discrepancies across environments, mitigating
amplified distribution shifts in low-dimensional features to
ensure robustness under complex conditions. These experiments confirm that parameter selection must consider data
characteristics: for 5G-MNC scenarios with smaller scale and
lower feature dimensionality, we recommend α = 0.5 and
λ = 0.1.
We further conducted parameter sensitivity analysis with
2-node and 10-node clusters to investigate the adaptability
of hyperparameters across different network scales. For specific details, please refer to the Appendix B (Supplementary
Material).
Besides, in order to conduct a more comprehensive analysis of the model, we have further implemented sensitivity
analysis from multiple perspectives including the influence
of batch size on training efficiency and performance, the
optimal stacking block number for DRSTGC, and the chosen
of the negative sampling strategy. Due to space limitations,
for specific details, please refer to Appendix C, D, and G
(Supplementary Material).

Fig. 16. Comparison of the performance of different parameters in Cluster2.
(a) Shielding anomaly detection. (b) Decommissioning anomaly detection.

G. Industrial Data Applications
1) Datasets: To further validate the generalizability of
our proposed method, we conducted experiments using the
following datasets. The PSM dataset [45], a public dataset
obtained from eBay server machines, contains 25-dimensional
metrics. The MSL dataset [46], collected by NASA, records
sensor and actuator status data from the Mars rover. The

Fig. 17. Comparison of the performance of different parameters in Cluster1.
(a) Shielding anomaly detection. (b) Decommissioning anomaly detection.

SMAP dataset [46], also collected by NASA, provides soil
sample measurements and telemetry information from the

LIU et al.:5G MOBILE NETWORKED CLUSTERS ANOMALY DETECTION UNDER DISTRIBUTION SHIFTS

3615

TABLE VII
P ERFORMANCE COMPARISON OF PSM, MSL, AND SMAP DATASETS ON DIFFERENT BASELINES

TABLE VIII
P ERFORMANCE COMPARISON OF THE P EPPER DATASET ON DIFFERENT BASELINES

Mars rover. Compared with MSL, SMAP exhibits a higher
incidence of point anomalies. Pepper is a humanoid robot
developed by SoftBank Robotics for use in human–robot
interaction and social assistance [47]. The dataset comprises
256 sensor readings. It records data for three distinct types
of cyber-physical attacks: “JointsControl”, “LedsControl” and
“WheelsControl”. The Pepper dataset is a well-known benchmark for anomaly detection in robotics, and is considered
particularly challenging due to the high dimensionality of the
data.
Similar to the 5G-MNC dataset, the testing sets were modified by introducing artificial distribution shifts through manual
processing. Given the substantial data volume, our adjustment
involved setting the fluctuation amplitude to 0.5 and applying
variance perturbation to 30% of the data in the central 70%
region.
2) Baselines: We selected the following advanced anomaly
detection methods for comparison: TopoGDN(2024) [28],
GANF(2022) [29], COCA(2023) [30], DUALTF(2024) [26],
OUAD(2024) [32]. Our evaluation metrics included precision
(P), recall (R), F1-score (F1), and ROC-AUC (AUC).
3) Performance Evaluation: We conducted comparative
analyses of Causal-DRSTGC against baseline methods with
results presented in Table VII. The experimental results
demonstrate that Causal-DRSTGC achieves superior F1-scores
across all three public datasets. Except for the SMAP
dataset, Causal-DRSTGC achieves the highest AUC values
on both PSM and MSL datasets, indicating its enhanced

capability to distinguish between normal and anomalous samples. Although GANF exhibits a marginally higher AUC
than Causal-DRSTGC on the SMAP dataset, Causal-DRSTGC
maintains significantly superior F1-score performance, suggesting a better balance between precision and recall.
We conducted experiments under three types of attacks
on the Pepper dataset, with results shown in Table VIII.
The findings indicate that our model also achieved the best
performance. These experimental outcomes validate CausalDRSTGC’s generalizability and effectiveness, particularly its
significant advantages over existing baselines in balancing
precision-recall tradeoffs, handling distribution shifts, and
modeling complex spatio-temporal dependencies.
This demonstrates that the proposed model not only applies
to 5G-MNC scenarios but also generalizes effectively to
diverse time-series anomaly detection tasks, including server
monitoring, aerospace sensor, and robot data, highlighting its
practical utility.
H. Complexity Analysis
The time complexity of the DRSTGC block stacking architecture is O(BT (N 2 D + N D2 )). The time complexity of
the causal intervention module is O(BT 2 N D). Here, B
represents the batch size, T represents the size of the time
window, N represents the number of feature nodes, and D
represents the feature dimension after data processing.
Besides, we calculated the actual running time and memory
consumption of the proposed model on both Cluster1 and

3616

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

TABLE IX
RUNNING TIME AND MEMORY CONSUMPTION OF
C LUSTER 1 AND C LUSTER 2

Cluster2 listed in Table IX. The running time listed is the
cumulative time for training dataset. We performed inference
on the test dataset item by item to simulate real-world streaming scenarios, avoiding the use of any vectorization methods.
One can observe that each item of data for inference requires
approximately 0.07 seconds. Considering that the minimum
time interval for mobile operators to collect each item of
data is 15 minutes, the responsiveness of the model can meet
the requirements of real-time applications. The experimental
environment utilized an NVIDIA GeForce RTX 3090 GPU @
128GB RAM configuration computer. These results demonstrate the capability of the proposed model for deployment in
real-world industrial scenarios.
VI. C ONCLUSION
In 5G Mobile Network Clusters (5G-MNCs), the proposed
model effectively resolves complex spatio-temporal pattern
recognition and distribution shifts robustness issues. The
designed DRSTGC block achieves deep modeling of inter-base
station synchronization dependencies through integration of
predefined topological information with data-driven hidden
dependency mining. By incorporating causal intervention
mechanisms and partial conditional invariance regularization (PCIR), the architecture eliminates confounding effects
induced by distribution shifts, significantly enhancing detection robustness in non-stationary environments. A joint optimization strategy combining discrimination and reconstruction
modules leverages complementary information between original data and latent feature spaces, establishing a more reliable
anomaly scoring mechanism.
Experimental results demonstrate that Causal-DRSTGC outperforms state-of-the-art methods on real-world China Mobile
5G-MNC datasets, particularly excelling in shielding and
decommissioning anomaly scenarios with superior F1-score
and AUC metrics. Ablation studies confirm the necessity of
core components. Generalization experiments further reveal
outstanding cross-domain performance on widely-used industrial benchmark datasets, highlighting strong universality and
practical value.
Although this study demonstrated effectiveness, real-world
5G-MNC deployments still face challenges. First, the identification of anomaly types still relies on prior expert knowledge,
particularly in dynamic and complex network environments,
where autonomous anomaly categorization remains challenge.
Second, the application background of mobile network clusters
leads to the difficulty of root cause localization in real scenarios. Currently, there is a lack of systematic and automated

solutions to trace back to the fundamental causes, which
hinders further improvements in overall operational efficiency.
Hence, in future work, how to autonomously identify the
emergence of new anomalies and locate the root causes of
anomalies in 5G-MNCs are valuable research directions.
R EFERENCES
[1] J. Contreras-Castillo, J. Guerrero-Ibañez, S. Zeadally, and E.-K. Hong,
“Generative AI for Internet of Vehicles (IoV): Potential and challenges,”
IEEE Commun. Standards Mag., vol. 9, no. 2, pp. 106–116, Jun. 2025.
[2] S. A. A. Hakeem and H. Kim, “Advancing intrusion detection in
V2X networks: A comprehensive survey on machine learning, federated
learning, and edge AI for V2X security,” IEEE Trans. Intell. Transp.
Syst., vol. 26, no. 8, pp. 1–69, Aug. 2025.
[3] Q. Zheng et al., “MobileRaT: A lightweight radio transformer method
for automatic modulation classification in drone communication systems,” Drones, vol. 7, no. 10, p. 596, Sep. 2023.
[4] Y. Tan, J. Liu, Y. Li, and J. Wang, “Deep learning based proactive
anomaly detection for 5G core control plane network function interactions,” IEEE Trans. Cognit. Commun. Netw., early access, Feb. 7, 2025,
doi: 10.1109/TCCN.2025.3539660.
[5] S. F. Ahmed et al., “Toward a secure 5G-enabled Internet of Things: A
survey on requirements, privacy, security, challenges, and opportunities,”
IEEE Access, vol. 12, pp. 13125–13145, 2024.
[6] X. Chen, Q. Qiu, C. Li, and K. Xie, “GraphAD: A graph neural network
for entity-wise multivariate time-series anomaly detection,” in Proc. 45th
Int. ACM SIGIR Conf. Res. Develop. Inf. Retr., Jul. 2022, pp. 2297–2302.
[7] N. Zhao, B. Han, R. Li, J. Su, and C. Zhou, “A multivariate KPIs
anomaly detection framework with dynamic balancing loss training,”
IEEE Trans. Netw. Service Manage., vol. 20, no. 2, pp. 1418–1429,
Jun. 2023.
[8] X. Wang et al., “Adaptive multi-receptive field spatial–temporal graph
convolutional network for traffic forecasting,” in Proc. IEEE Global
Commun. Conf. (GLOBECOM), Dec. 2021, pp. 1–7.
[9] S. Piltyay, A. Bulashenko, and I. Demchenko, “Wireless sensor network
connectivity in heterogeneous 5G mobile systems,” in Proc. IEEE Int.
Conf. Problems Infocommunications Sci. Technol. (PIC ST), Oct. 2020,
pp. 625–630.
[10] Q. Zheng, S. Saponara, X. Tian, Z. Yu, A. Elhanashi, and R. Yu, “A
real-time constellation image classification method of wireless communication signals based on the lightweight network MobileViT,” Cognit.
Neurodynamics, vol. 18, no. 2, pp. 659–671, Apr. 2024.
[11] J. B. S. Carvalho, M. Zhang, R. Geyer, C. Cotrini, and J. M. Buhmann,
“Invariant anomaly detection under distribution shifts: A causal perspective,” in Proc. Adv. Neural Inf. Process. Syst., 2023, pp. 310–337.
[12] Q. Zheng, X. Tian, L. Yu, A. Elhanashi, and S. Saponara, “Recent
advances in automatic modulation classification technology: Methods,
results, and prospects,” Int. J. Intell. Syst., vol. 2025, no. 1, Jan. 2025,
Art. no. 4067323.
[13] A. Dridi, C. Boucetta, S. E. Hammami, H. Afifi, and H. Moungla,
“STAD: Spatio-temporal anomaly detection mechanism for mobile network management,” IEEE Trans. Netw. Service Manage., vol. 18, no. 1,
pp. 894–906, Mar. 2021.
[14] A. K. Sangaiah, S. Rezaei, A. Javadpour, F. Miri, W. Zhang, and
D. Wang, “Automatic fault detection and diagnosis in cellular networks
and beyond 5G: Intelligent network management,” Algorithms, vol. 15,
no. 11, p. 432, Nov. 2022.
[15] F. Wen and H. Wymeersch, “5G synchronization, positioning, and
mapping from diffuse multipath,” IEEE Wireless Commun. Lett., vol. 10,
no. 1, pp. 43–47, Jan. 2021.
[16] L. Chao, L. Yinghua, D. Fengqian, and S. Rui, “Spatio-temporal
anomaly detection for 5G-clusters: A multi-scale fuzzy contrastive
learning approach,” IEEE Trans. Netw., vol. 33, no. 4, pp. 1588–1602,
Aug. 2025.
[17] P. K. Deka, Y. Verma, A. B. Bhutto, E. Elmroth, and M. Bhuyan, “Semisupervised range-based anomaly detection for cloud systems,” IEEE
Trans. Netw. Service Manage., vol. 20, no. 2, pp. 1290–1304, Jun. 2023.
[18] Y. Wang, J. Zhang, S. Guo, H. Yin, C. Li, and H. Chen, “Decoupling
representation learning and classification for GNN-based anomaly detection,” in Proc. 44th ACM SIGIR Conf. Res. Dev. Inf. Retr., Jul. 2021,
pp. 1239–1248.
[19] Y. Liu et al., “Anomaly detection in dynamic graphs via transformer,”
IEEE Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12081–12094,
Dec. 2023.

LIU et al.:5G MOBILE NETWORKED CLUSTERS ANOMALY DETECTION UNDER DISTRIBUTION SHIFTS

[20] M. Thill, W. Konen, H. Wang, and T. Bäck, “Temporal convolutional
autoencoder for unsupervised anomaly detection in time series,” Appl.
Soft Comput., vol. 112, Nov. 2021, Art. no. 107751.
[21] W. Li, W. Hu, T. Chen, N. Chen, and C. Feng, “StackVAE-G: An
efficient and interpretable model for time series anomaly detection,” AI
Open, vol. 3, pp. 101–110, Jun. 2022.
[22] W. T. Lunardi, M. A. Lopez, and J.-P. Giacalone, “ARCADE: Adversarially regularized convolutional autoencoder for network anomaly
detection,” IEEE Trans. Netw. Service Manage., vol. 20, no. 2,
pp. 1305–1318, Jun. 2023.
[23] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., May 2021,
vol. 35, no. 5, pp. 4027–4035.
[24] K. Liu et al., “DeepBAN: A temporal convolution-based communication
framework for dynamic WBANs,” IEEE Trans. Commun., vol. 69,
no. 10, pp. 6675–6690, Oct. 2021.
[25] S. Huang et al., “HitAnomaly: Hierarchical transformers for anomaly
detection in system log,” IEEE Trans. Netw. Service Manage., vol. 17,
no. 4, pp. 2064–2076, Dec. 2020.
[26] Y. Nam et al., “Breaking the time-frequency granularity discrepancy in
time-series anomaly detection,” in Proc. ACM Web Conf., May 2024,
pp. 4204–4215.
[27] J. Lee, J. Lee, and S. B. Kim, “Uncertainty-informed dynamic threshold for time series anomaly detection,” Expert Syst. Appl., vol. 278,
Jun. 2025, Art. no. 127379.
[28] Z. Liu, X. Huang, J. Zhang, Z. Hao, L. Sun, and H. Peng, “Multivariate time-series anomaly detection based on enhancing graph attention
networks with topological analysis,” in Proc. 33rd ACM Int. Conf. Inf.
Knowl. Manag., Jul. 2024, pp. 1555–1564.
[29] E. Dai and J. Chen, “Graph-augmented normalizing flows for anomaly
detection of multiple time series,” 2022, arXiv:2202.07857.
[30] R. Wang et al., “Deep contrastive one-class time series anomaly detection,” in Proc. SDM, Jun. 2023, pp. 694–702.
[31] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “DCdetector: Dual
attention contrastive representation learning for time series anomaly
detection,” in Proc. 29th ACM SIGKDD Conf. Knowl. Discovery Data
Mining, Aug. 2023, pp. 3033–3045.
[32] D. Meli, “Explainable online unsupervised anomaly detection for
cyber-physical systems via causal discovery from time series,” in
Proc. IEEE 20th Int. Conf. Autom. Sci. Eng. (CASE), Aug. 2024,
pp. 4120–4125.
[33] N. Huyan, D. Quan, X. Zhang, X. Liang, J. Chanussot, and L. Jiao,
“Unsupervised outlier detection using memory and contrastive learning,”
IEEE Trans. Image Process., vol. 31, pp. 6440–6454, 2022.
[34] Z. Zhou et al., “Maintaining the status quo: Capturing invariant relations
for OOD spatiotemporal learning,” in Proc. 29th ACM SIGKDD Conf.
Knowl. Discovery Data Mining, Aug. 2023, pp. 3603–3614.
[35] Y. Xia et al., “Deciphering spatio-temporal graph forecasting: A causal
lens and treatment,” in Proc. NeurIPS, vol. 36, 2023, pp. 37068–37088.
[36] J. Hu, Y. Liang, Z. Fan, H. Chen, Y. Zheng, and R. Zimmermann,
“Graph neural processes for spatio-temporal extrapolation,” in Proc. 29th
ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining, Sep. 2023,
pp. 752–763.
[37] B. N. Oreshkin, D. Carpov, N. Chapados, and Y. Bengio, “N-BEATS:
Neural basis expansion analysis for interpretable time series forecasting,”
2019, arXiv:1905.10437.
[38] S. Rahmani, A. Baghbani, N. Bouguila, and Z. Patterson, “Graph neural
networks for intelligent transportation systems: A survey,” IEEE Trans.
Intell. Transp. Syst., vol. 24, no. 8, pp. 8846–8885, Aug. 2023.
[39] H. Zhang et al., “Spatio-temporal weighted graph reason learning for
multivariate time-series anomaly detection,” IEEE Internet Things J.,
vol. 12, no. 15, pp. 29373–29383, Aug. 2025.
[40] S. He, Q. Guo, G. Li, K. Xie, and P. K. Sharma, “Multivariate time series
anomaly detection based on multiple spatiotemporal graph convolution,”
IEEE Trans. Instrum. Meas., vol. 74, pp. 1–14, 2025.
[41] X. Zhang et al., “Rethinking robust multivariate time series anomaly
detection: A hierarchical spatio-temporal variational perspective,” IEEE
Trans. Knowl. Data Eng., vol. 36, no. 12, pp. 9136–9149, Dec. 2024.

3617

[42] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discovery Data
Mining, Jul. 2019, pp. 2828–2837.
[43] J. Li, H. Izakian, W. Pedrycz, and I. Jamal, “Clustering-based anomaly
detection in multivariate time series data,” Appl. Soft Comput., vol. 100,
Mar. 2021, Art. no. 106919.
[44] X. Zhang, Z. Tian, Y. Shi, Q. Guan, Y. Lu, and Y. Pan, “STFGCN:
Spatio-temporal fusion graph convolutional networks for subway traffic
prediction,” IEEE Access, vol. 12, pp. 194449–194461, 2024.
[45] A. Abdulaal, Z. Liu, and T. Lancewicki, “Practical approach to asynchronous multivariate time series anomaly detection and localization,”
in Proc. 27th ACM SIGKDD Conf. Knowl. Discovery Data Mining,
Aug. 2021, pp. 2485–2494.
[46] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and
T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric dynamic thresholding,” in Proc. 24th ACM SIGKDD Int.
Conf. Knowl. Discovery Data Mining, Jul. 2018, pp. 387–395.
[47] A. K. Pandey, R. Gelin, and A. Robot, “Pepper: The first machine of its
kind,” IEEE Robot Autom. Mag., vol. 25, no. 3, pp. 40–48, Mar. 2018.

Xuyuan Liu received the B.E. degree from Qingdao
University of Technology, China, in 2024. He is
currently pursuing the M.E. degree with the School
of Information Science and Engineering, Shandong
Normal University. His research interests include
anomaly detection and multivariate time series
analysis.

Chao Luo (Member, IEEE) received the Ph.D.
degree in computer science from Dalian University
of Technology, China, in 2013. He is currently a Professor with the School of Information Science and
Engineering, Shandong Normal University, China.
He has published more than 60 refereed articles. His
research interests include machine learning, complex
systems, and time series analysis.

Rui Shao received the master’s degree in computer software and theory from Shandong University.
He is currently with China Mobile Communications
Group Shandong Company Ltd., mainly engaged in
wireless network optimization and planning work
for 5G/4G networks. His research interests include
5G communication network planning, strategy optimization, SON, anomaly recognition, and network
structure optimization.
PAPER_TEXT
