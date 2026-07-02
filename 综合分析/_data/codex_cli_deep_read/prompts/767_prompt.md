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
# [767] NOVA: A Self-Supervised Graph Framework for Real-Time Anomaly Detection in Internet of Vehicles
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
编号：767
题名：NOVA: A Self-Supervised Graph Framework for Real-Time Anomaly Detection in Internet of Vehicles
年份：2026
DOI：10.1109/tnsm.2026.3696324
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2026.3696324.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、图学习、知识图谱与威胁情报
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\767.txt
- 原始字符数：73317
- 本次发送字符数：73317
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

1

NOVA: A Self-Supervised Graph Framework for RealTime Anomaly Detection in Internet of Vehicles
Arash Heidari, Jamal N. Al-Karaki

Abstract— The Internet of Vehicles (IoV) enables cooperative
driving
and
real-time
Vehicle-to-Everything
(V2X)
communication but remains vulnerable to behavioral and
structural anomalies due to its dynamic, decentralized nature.
Existing deep learning methods either overlook topological
inconsistencies or ignore communication feature fidelity, while
random-walk sampling introduces contextual noise. In this
paper, we propose Network Observation for Vehicular
Anomalies (NOVA), a self-supervised graph-based framework
that detects both behavioral and structural anomalies in IoV
networks without labeled data. NOVA models vehicular
communications as attributed graphs and employs intimacyguided subgraph sampling to extract meaningful neighborhoods.
A Graph Convolutional Network (GCN)–based generative
module reconstructs node attributes to reveal behavioral
deviations, while a contrastive module validates structural
coherence through embedding comparisons of real and
perturbed contexts. Their hybrid anomaly score enables
accurate, scalable, and real-time detection of compromised nodes.
Performance results show that NOVA achieves state-of-the-art
performance (98.7% accuracy, 98.1% F1), real-time throughput
(~4.7k events/s at 5k msg/s), and strong robustness (AUROC 0.99,
AUPRC 0.98, FAR 0.05) with near-linear scalability (≤40 ms
latency for 50k vehicles). By integrating generative and
contrastive self-supervised learning with context-aware sampling,
NOVA significantly enhances IoV security, reliability, and
adaptability.
Index Terms— Internet of Vehicles, V2X Security, Anomaly
Detection, Self-Supervised Learning, Graph Neural Networks.

T

I. INTRODUCTION

he Internet of Vehicles (IoV) has become a key part of
Intelligent Transportation Systems (ITS) [1, 2]. It lets
vehicles, Roadside Units (RSUs), and cloud
infrastructures connect easily through Vehicle-toEverything (V2X) communication [3]. This high level of
connectivity makes it possible for safety-critical applications
like cooperative adaptive cruise control, autonomous driving
coordination, and sending emergency messages [4]. IoV
Arash Heidari and Jamal N. Al-Karaki are with the Computational Systems
Department, Zayed University, United Arab Emirates. Their contact emails
are: Arash_heidari@ieee.org, and Jamal.Al-Karaki@zu.ac.ae
The corresponding authors: Arash Heidari and Jamal N. Al-Karaki
This work was not supported by any external funding.
The authors contributed equally to this work.

communication is dynamic and decentralized, which makes it
easy for anomalous behaviors and cyber-physical threats to
happen [5, 6]. Nodes that do not work right or are hacked can
send bad data, stop routing updates, or change transmissions
that are sensitive to delay, which can have serious effects on
road safety and traffic flow [7]. So, it is very important to
build strong frameworks for detecting anomalies to keep IoV
ecosystems safe, reliable, and strong [8, 9].
Recent developments in deep learning have provided
powerful tools for anomaly detection in the IoV, as their
capability to learn intricate spatiotemporal correlations in
vehicular data has been effectively leveraged [10, 11]. On the
other hand, Graph Neural Networks (GNNs), Convolutional
Neural Networks (CNNs), and hybrid deep architectures have
been utilized to simulate the communication dynamics inside
IoV environments [12]. These models use things like packet
transmission rates, mobility patterns, and changes in topology
to find unusual behaviors [13, 14]. However, current methods
frequently encounter two significant challenges: (1) the
difficulty in detecting both node-level behavioral anomalies
and structural irregularities in dynamic vehicular graphs, and
(2) an excessive dependence on labeled training datasets,
which are expensive and impractical in extensive vehicular
contexts [15, 16]. Consequently, there is an urgent
requirement for self-supervised and hybrid anomaly detection
methodologies capable of generalizing across diverse IoV
scenarios without extensive labeling [6, 17, 18].
Although significant progress has been achieved, there are
still significant gaps that hinder trust in real-world IoV
anomaly detection. In dynamic V2X graphs, most techniques
identify behavioral or structural irregularities, but not both.
Under the mobility churn, the common neighborhood
sampling methods can contain noise, leading to unstable
representations and false alarms. Furthermore, there are many
studies that focus on the accuracy of the data but do not
provide any real-time guarantees of latency and throughput in
large, safety-critical V2X deployments. Transferable
adversarial attacks are also an emerging threat to deep IDS
models, as perturbations generated on surrogate models may
transfer to target detectors by exploiting shared latent feature
representations [19]. Network Observation for Vehicular
Anomalies (NOVA) is made to fill these gaps by combining
generative attribute reconstruction with node-context
contrastive structural validation and using intimacy-guided
subgraph sampling to keep high-fidelity neighborhoods while
keeping a scalable pipeline that can be used in real time.
NOVA sees vehicular networks as topological graphs, with
vehicles, RSUs, or infrastructure as nodes and Vehicle-toVehicle (V2V) / Vehicle-to-Infrastructure (V2I) / Vehicle-toNetwork (V2N) communication as edges. NOVA learns to

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

2
find both behavioral and topological anomalies without any
help by using subgraph sampling, attribute reconstruction, and
structural contrastive learning. It combines attribute-level
reconstruction errors and structure-level consistency scores
into a hybrid anomaly score during inference. This makes it
possible to find compromised or malfunctioning nodes in real
time and on a large scale. NOVA combines generative
reconstruction and contrastive validation, but its novelty does
not come from having two self-supervised losses at the same
time. Instead, it comes from a non-trivial combination of (i)
intimacy-guided subgraph sampling that filters out lowfidelity neighbors caused by mobility and stabilizes the node's
contextual view, (ii) target-node anonymization within
sampled contexts, which stops shortcut learning and forces
true context-conditioned inference (which makes it more
robust to poisoning and transient correlations), and (iii) a
hybrid anomaly scoring mechanism that explicitly combines
attribute deviation signals with topology-consistency signals.
These parts are all connected in important ways. For example,
without intimacy-guided sampling, contrastive node–context
validation is dominated by noisy contexts. Without
anonymization, reconstruction can turn into feature copying.
And without hybrid scoring, either branch alone is
systematically blind to a major anomaly class. This synergy
lets NOVA find small problems that are both behavioral and
structural, and it stays stable even when there is a lot of
change and can grow to handle real-time IoV operations. This
paper's primary contributions can be summarized as follows:
•

•

•

•
•

Modeling IoV communication as a dynamic attributed
graph that includes both operational aspects and
topological connection;
Introducing a new hybrid framework that uses generative
learning to rebuild attributes and contrastive learning to
make sure that structures are consistent;
Creating a better subgraph sampling technique based on
closeness scoring to get high-quality communication
situations;
Making a dual-path self-supervised learning pipeline that
does not need labeled training data;
Showing that NOVA works by doing both theoretical
analysis and real-world testing, which shows that it can
better find both behavioral and structural problems in IoV
networks.

The rest of the paper is organized as follows. Section II
presents a summary of the latest findings that are related to the
study topic. The system model is elaborated in Section III.
Also, the NOVA method will be provided in Section IV. The
paper presents the results of the NOVA method and provides a
comprehensive comparison with existing approaches in
Section V. Section VI provides an overview and conclusion.
II. RELATED WORK
In this section, we consider related research addressing the
topic of finding anomalies and intrusions in the IoV and linked
vehicle systems. In this regard, Sboui, et al. [20] presented a

Convolutional Neural Network–Bidirectional Long ShortTerm Memory (CNN-BiLSTM) / Variational Autoencoder
(VAE) framework for detecting anomalies in spatio-temporal
Light Detection and Ranging (LiDAR) data. As well, Tiwari,
et al. [21] also suggested a fine tree-based IDS for IoV, which
achieved high accuracy on benchmark datasets. In addition,
Cheng, et al. [22] used a spatial-temporal correlation module
with attention and a patch-based transformer. In a similar
project, Cao, et al. [23] created a self-supervised IDS for InVehicle Networks (IVNs) that used hierarchical transformers
and can be updated online. As well, A hybrid model was
proposed by Zhao, et al. [24] to find problems in Basic Safety
Messages (BSMs). It combined VAE and Generative
Adversarial Network (GAN). Singh and Rathore [25], on the
other hand, used a Bayesian Online Change Point
identification (BOCPD) method for real-time anomaly
identification in connected vehicles, along with ways to
recover from them. Moreover, Li, et al. [26] introduced a
meta-heuristic optimized deep random neural network that
was 99.2% accurate at finding IoT-based anomalies.
Mansourian, et al. [27] also suggested a Controller Area
Network (CAN) bus IDS that used LSTM and ConvLSTM
modules along with a Gaussian Naïve Bayes classifier. Plus,
Van Wyk, et al. [28] used a χ²-detector with CNN and Kalman
filtering to find anomalies in Connected and Autonomous
Vehicles (CAVs). Devika, et al. [29] made a GAN-based
anomaly detector that works best for CAV dynamics. As well,
Yang, et al. [30] put forward an approach for detecting GPS
spoofing attacks that is based on domain knowledge and uses
trajectory prediction and statistical dissimilarity tests.
Moreover, He, et al. [31] introduced a multi-information
fusion CNN that focuses on vehicle sensor abnormalities. In
another work, He, et al. [32] created a Wavelet Kernel
Network with omni-scale convolution that picked up highfrequency information for finding anomalies in ITS.
Khanmohammadi and Azmi [33] also came out with a DCNN-LSTM Autoencoder that used preprocessing approaches
like Differencing and Moving Standard Deviation to greatly
increase F1-scores. Also, Zhang, et al. [34] suggested a dualchannel self-attention CNN for finding anomalous patterns in
multivariate time series data. Al-Absi, et al. [35] presented the
DST-IDS, a dynamic spatial-temporal graph-transformer
network to detect intrusions in IVNs, which captured the
changing nature of vehicle communication patterns. Lastly,
Wang, et al. [36] proposed a class-imbalance-aware IDS on
spatiotemporal GNNs on software-defined vehicles that
learned the topology and temporal communication structures.
There are a lot of different ways to find anomalies in IoV
and CAVs, but most of them have serious flaws. In real-world
driving situations, labeled datasets are hard to find and
expensive; thus, many supervised methods need them.
Generative and hybrid models make it easier to find
anomalies, but they often have problems with scalability and
training stability. Self-supervised and transformer-based
algorithms lessen the need for labeling, but they mostly
concentrate on modeling sequential messages, ignoring the
structural abnormalities that are typical in IoV networks. Also,
sampling methods like random walks often introduce noise

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

3
and make detection less accurate. To address these issues, we
provide NOVA, a self-supervised graph-based framework that
incorporates intimacy-guided subgraph sampling, generative
Graph Convolutional Network (GCN) reconstruction, and
contrastive structural validation. NOVA strikes a balance
between communication fidelity and structural consistency,
creating a single anomaly score that may be used to find
compromised nodes in real time. This makes it scalable, labelfree, and able to handle both behavioral and structural
problems, which are the main problems with earlier studies.

TABLE I
DEFINITIONS OF THE SYMBOLS
Symbol
𝑮
𝑬
𝑨
𝛗

𝒈𝒊

𝜶
Ā
𝝋𝒋

III. SYSTEM MODEL
In NOVA, the IoV communication environment is shown as a
topology graph. Each node represents an entity in the
vehicular network, like a vehicle, RSU, or infrastructure
component. Each edge shows an active communication link,
such as V2V, V2I, or V2N connections. The communication
and operational features of each node, like packet transmission
rates, latency, signal strength, routing updates, and mobility
patterns, make up its attribute vector. On-board sensors and
network monitoring modules constantly gather these
parameters and send them to a security management system
for centralized or edge-based analysis. The structural half of
the graph shows the changing communication topology of the
vehicular network, while the attribute part shows how each
participant behaves and works. This changes the problem of
finding malicious or malfunctioning activity into the problem
of finding nodes in the graph that are out of the ordinary.
NOVA uses an augmented intelligence–driven detection
technique to find these kinds of problems. The network is
formally represented as 𝐺 = (𝑉, 𝐸, 𝑋, 𝐴), where 𝑉 =
{𝑣1 , 𝑣 2 , … , 𝑣𝑛 } constitutes the set of nodes, 𝐸 represents the
set of edges, 𝑋 ∈ ℝ𝑁×𝐷 signifies the node feature matrix, and
𝐴 ∈ ℝ𝑁×𝑁 denotes the adjacency matrix, with 𝐷 indicating
the number of feature dimensions. Fig. 1 shows how the
NOVA engine works in an IoV setting, where vehicles share
information over V2V links and talk to RSUs that send data to
a security management system to find problems. The green
dots show safe vehicles, the red dots show nodes that are not
normal, and the blue dashed lines depict V2V
communications. Also, Table I shows the used symbols.

𝑳𝑪
𝒙

𝝈(·)
𝒉𝒊
𝒋

𝒆𝒊
𝝀, 𝜸
𝐬𝐜𝐨𝐫𝐞(𝒗𝒊)

Definition
Communication graph
Set of edges
Adjacency matrix of
the vehicular graph
𝑗 − 𝑡ℎ contextual
subgraph
Damping factor
Column-normalized
adjacency matrix
Contrastive loss for

Symbol
𝑽
𝑿
𝑫

Reconstructed feature
vector
Nonlinear activation
function
Embedding vector of
target node 𝒗𝒊
Positive pair:

𝑬𝒏𝒄(
·), 𝑫𝒆𝒄(·)
𝝋𝒋
𝑿˜

Weighting factors
Final anomaly score

𝑺
𝑰𝒕𝒊
𝑯𝝋𝒋
𝒙𝒊

𝒊

𝒔𝒋
𝒋

𝒆‾𝒊
𝜽
𝑳

Definition
Set of nodes
Node feature matrix
Number of feature
dimensions
Communication
relevance matrix
Intimacy score
Node embedding
matrix of the subgraph
Original feature vector
Encoder and decoder
functions
Reconstructed feature
matrix
Pooled embedding
vector
Negative pair
Scaling parameter
Overall training loss

IV. THE NOVA METHOD
NOVA identifies abnormal IoV objects in three synchronized
processes: intimacy-directed context selection, GCN-based
attribute reconstruction and node-context contrastive
validation. Given each target node, NOVA first identifies
high-relevance subgraphs of context, masks the target-node
features within each context, and then measures whether the
node fits in the communication neighborhood of its attributes
and structures. The overall methodological pipeline is
summarized in Fig. 2.
Next, NOVA uses graph-view sampling to get subgraphs
that show the local communication neighbourhood of each
target node. This is important because high-quality context is
needed to learn reliable representations, and naive randomwalk sampling can add noise by treating all neighbours as
equally informative. Specifically, NOVA first uses random
walks to create several candidate subgraphs. Then, it uses a
custom PageRank-inspired scoring system to figure out how
important each neighbour is by calculating the relevance
matrix 𝑆 = 𝛼𝐼 − (1 − 𝛼)𝐴ˉ, where 𝐼 is the identity matrix, 𝛼 ∈
[0,1](typically 0.15), and 𝐴ˉ = 𝐴𝐷 −1 is the column-normalized
adjacency matrix with 𝐷(𝑖, 𝑖) = ∑𝑗 𝐴(𝑖, 𝑗). Here, 𝑆(𝑖, 𝑗)
measures how well 𝑣𝑖 and 𝑣𝑗 communicate with each other.
𝜙
Each candidate subgraph 𝑔𝑖 1 gets an intimacy score 𝐼𝑖𝑡 =
∑𝑗 𝑆(𝑖, 𝑗). The top-k subgraphs with the highest intimacy
scores are kept as the best training contexts. Finally, NOVA
uses target-node anonymization by zero-masking the original
features of the target node in each sampled subgraph. This
stops direct information leakage and makes the model guess
node properties and structural changes based on the
communication context around them. This makes it easier to
find both behavioural and topological anomalies.
(𝜙𝑗 )

Formally, for a selected contextual subgraph 𝑔𝑖
Fig. 1. NOVA system model for IoV anomaly detection.

of target

(𝜙𝑗 )
node 𝑣𝑖 with feature matrix 𝑋𝑖
∈ ℝ∣𝑉𝑠 ∣×𝐹 , NOVA performs

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

4
target-node anonymization by replacing the target node’s
feature vector with an all-zero vector, 𝑥̃𝑖 = 0 ∈ ℝ𝐹 . The
(𝜙𝑗 )
resulting masked feature matrix 𝑋̃𝑖 is defined by setting the
target row to zero while leaving all other node features
unchanged. So, NOVA uses explicit zero-masking rather than
a dataset-mean vector or a learnable [𝑀𝐴𝑆𝐾] token.

Here, 𝐻 𝜑𝑗 is the node embedding matrix of the subgraph
𝜑𝑗
𝜑𝑗
𝜑
𝑔𝑖 1 , 𝑋𝑖 and 𝐴𝑖 are the feature and adjacency matrices of the
subgraph, respectively, 𝜎(⋅) denotes a non-linear activation
function such as ReLU, 𝐷(𝑖, 𝑖) = 𝛴𝑗 𝐴(𝑖, 𝑗) is the degree
matrix, and 𝑊𝑒 is the learnable weight matrix for the encoder.
If fewer than 𝑘 valid high-intimacy contexts are available
for a target node, NOVA uses all available contexts 𝑚𝑖 < 𝑘
for that node and normalizes the generative and contrastive
objectives by 𝑚𝑖 instead of 𝑘. No synthetic padding is used
during inference; during batched training, missing slots are
masked out and excluded from loss aggregation.
The graph decoder in NOVA is set up the same way as the
encoder, using one GCN layer to recreate the original node
attributes from the learned embeddings. The decoder uses the
embedding matrix that the encoder made as its input. The
decoder sends information over the subgraph's local
communication topology. The decoding process is defined as:
𝜑
𝜑
𝑋˜𝑖 𝑗 = Dec𝐺𝐶𝑁 (𝐻 𝜑𝑗 , 𝐴𝑖 𝑗 )

(2)

= 𝜎 (𝐷

Fig. 2. NOVA pipeline.

Random-walk and k-hop sampling tend to include too
many transient or weakly related neighbors in dynamic IoV
graphs. This makes the context noise higher: when links
appear and disappear quickly, the sampled neighborhood
distribution changes between time windows, making
subgraphs with higher variance and less consistent supervision
for both reconstruction and contrastive alignment. Intimacyguided sampling helps with this by ranking possible contexts
based on a communication-relevance signal (PageRankinspired intimacy). This works like a relevance filter that
focuses probability mass on stable, high-interaction neighbors.
Churn lowers the expected number of temporary edges and the
variance of the aggregated context embedding. This means
that the generative branch sees less reconstruction noise (more
predictable neighbor-conditioned attributes), and the
contrastive branch sees a clearer separation between real and
corrupted contexts. In contrast, naive k-hop expansion can
make neighborhoods bigger in dense areas and make hubinduced dilution worse, while random walks can go into
loosely connected areas and add nodes that are not in the right
context. Importantly, intimacy-guided selection makes the
system more robust without raising the asymptotic cost. This
is because sampling stays local and scoring candidates is
limited by the same neighborhood statistics that are already
available at RSUs. This creates a useful trade-off: lower-noise
contexts and more stable learning when mobility churn
happens. This explains the empirical FAR/F1 gains over
RandomWalk and degree-based baselines.
NOVA uses a one-layer GCN encoder to map the node
features of each subgraph into a low-dimensional embedding
space:
𝜑

𝜑

(1)

𝐻 𝜑𝑗 = EncGCN (𝑋𝑖 𝑗 , 𝐴𝑖 𝑗 )
= 𝜎 (𝐷

−

1
1 𝜑
𝜑𝑗
𝑗
−
2 (𝐴
2
𝑖 + 𝐼)𝐷 𝑋𝑖 𝑊𝑒 )

−

1
1
𝜑𝑗
−
2 (𝐴
2 𝜑𝑗
𝑖 + 𝐼)𝐷 𝐻 𝑊𝑑 )

where 𝑊𝑑 is the weight matrix that can be trained for the
decoding process, 𝐻 𝜑𝑗 is the matrix that the encoder uses to
𝜑𝑗
incorporate, 𝐴𝑖 is the subgraph's adjacency matrix, 𝐷 is the
degree matrix, and 𝜎(⋅) is a nonlinear activation function like
ReLU.
For a certain target node 𝑣𝑖 attribute reconstruction
𝜑
𝜑
depends on its anonymized subgraphs 𝑔𝑖 1 , … , 𝑔𝑖 𝑘 . NOVA
makes the reconstruction process reliant only on contextual
information from adjacent nodes by setting the target node's
characteristics to zero. This architecture ensures that both
direct neighbors and connections of a higher order help find
behavioral inconsistencies. The goal of the generative learning
process is to lower the Mean Squared Error (MSE) between
the reconstructed feature vector and the target node's original
feature vector. The generating loss for the 𝑗th selected
subgraph is:
𝑁

𝜑

𝐿𝑔 𝑗 =

2
1
𝜑
∑ (𝑋˜𝑖 𝑗 [−1, : ], 𝑥𝑖 ) , 𝑗 ∈ {1, … , 𝑘}
𝑁

(3)

𝑖=1

𝜑𝑗
where 𝑋˜𝑖 is the reconstructed feature matrix from the
𝜑𝑗

decoder for subgraph 𝑔𝑖 , and 𝑥𝑖 is the initial feature vector
for node 𝑣𝑖 . To find the ultimate generating loss for a target
node, take the average of all 𝑘 chosen subgraphs:
𝑘

1
𝜑𝑗
𝐿𝑔 = ∑ (𝐿𝑔 )
𝑘

(4)

𝑗=1

Although the generative branch can be used to capture the
attribute inconsistency, structural anomalies need to be
compared between the target node and its communication
context. NOVA thus incorporates the contrastive branch,
which matches target embedding to its actual contextual
subgraph and distinguishes between it and degraded
contextual views.
The purpose of the contrastive learning module in NOVA
is to find structural problems by comparing the representation

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

5
of a target node with that of its contextual subgraph. The GCN
encoder takes in two parts: the feature matrix of the subgraph
and the feature vector of the target node. The way to encode
the feature matrix of the subgraph is the same as what was
said before in Eq. (1). For individual nodes, the encoding
method is more straightforward since a single node lacks its
adjacency structure. The embedding of a target node 𝑣𝑖 is
gotten as:
ℎ𝑖 = 𝜎(𝑥𝑖 𝑊𝑒 )
(5)

𝑘

𝐿𝐶 =

1
𝜑𝑗
∑ (𝐿𝐶 )
𝑘

(10)

𝑗=1

The formulation of the generative loss and contrastive loss
employed in the training phase of NOVA was covered in the
preceding sections. These elements are utilized to calculate the
final anomaly scores for every node in the IoV communication
graph during the inference stage. Given that most nodes in the
network should act appropriately, the trained GCN encoder–
where 𝑥𝑖 is the feature vector of 𝑣𝑖 , ℎ𝑖 is the embedding decoder should be able to accurately reconstruct and map their
vector that comes out of it, 𝑊𝑒 is the parameter matrix that the feature vectors into a suitable latent representation. On the
generative encoder uses, and 𝜎(⋅) is a nonlinear activation other hand, when projected into the latent space, anomalous
function like ReLU. Also, the parameter matrix 𝑊𝑒 is the same nodes, whether they have structural or attribute irregularities,
as Eq. (1). NOVA uses a pooling function to combine the will have distorted representations, leading to weaker
embeddings of all the nodes in the sampled subgraph into a alignment with their context or higher reconstruction errors.
single representation vector. There are many different pooling Reconstructing a target node's attributes in the generative
strategies, like average pooling, max pooling, and bilinear module only uses the contextual neighbors' features in the
pooling, but NOVA uses a simple and effective average chosen subgraphs. An indicator of anomaly likelihood is the
degree of discrepancy between the original and reconstructed
pooling operation:
𝑛
feature vectors. This discrepancy is measured by NOVA using
(6)
1
𝑠𝑗 = Φ(𝐻 𝜑𝑗 ) = ∑ 𝐻 𝜑𝑗 [𝑘, : ]
the L2-average norm distance across the top k contextual
𝑛
subgraphs:
𝑘=1
𝑘

𝜑𝑗
In this case, 𝑛 is the number of nodes in the subgraph, 𝑔𝑖

is the embedding matrix that the GCN encoder makes, and 𝑠𝑗
is the vector that represents the generated subgraph. The
𝑗
positive example 𝑒𝑖 is made by combining the target node's
embedding with the real representation of its contextual
subgraph:

score𝑔 (𝑣𝑖 ) =

1
𝜑𝑗
∑ (𝜃(‖𝑋‾𝑖 [−1, : ] − 𝑥𝑖 )‖22 )
𝑘

(11)

𝑗=1

where score𝑔 (𝑣𝑖 ) is the generative anomaly score for node 𝑣𝑖 ,
𝜑𝑗
θ is a scaling parameter to normalize scores to [0,1], 𝑋‾𝑖 is the
reconstructed feature matrix, and 𝑥𝑖 is the original feature
𝑗
(7) vector. Higher values of score𝑔 (𝑣𝑖 ) indicate greater deviations
𝑒𝑖 = (ℎ𝑖 , 𝑠𝑗 ),
in communication behavior relative to its neighborhood. For
the contrastive module, anomaly scoring is based on the
𝑗
The negative example 𝑒‾𝑖 is made by messing up the discrimination scores computed during training for positive
subgraph embedding, more especially by messing up the and negative sample pairs, as defined before. The contrastive
1
𝑗
matrix that embeds the subgraph 𝐻 𝜑𝑗 and then putting it all anomaly score is calculated as score𝑐 (𝑣𝑖 ) = 𝑘 ∑𝑘𝑗=1 (𝑑˙𝑖 −
𝑗
back together using the pooling operation 𝑒‾𝑖 = (ℎ𝑖 , 𝑠˜𝑗 ). Then, 𝑑˜ 𝑗 ). Here, 𝑑 𝑗 matches the similarity between the target node
𝑖
𝑖
𝑗
NOVA calculates discrimination ratings for each pair:
and its real contextual subgraph, while 𝑑˜𝑖 is equal to how
similar the node is to a broken subgraph. If a node is different
𝑗
(8)
𝑗
𝑗
𝑑𝑖 = 𝜎(ℎ𝑖 𝑊𝑑 𝑠𝑗 )
from the rest of its neighborhood, it will make 𝑑𝑖 and 𝑑˜𝑖 near
𝑗
in number, which makes their difference less. For a regular
𝑑˜𝑖 = 𝜎(ℎ𝑖 𝑊𝑑 𝑠˜𝑗 )
𝑗
𝑗
node, on the other hand, 𝑑𝑖 will get close to 1 while 𝑑˜𝑖 gets
where 𝑊𝑑 is a trainable parameter matrix and 𝜎(⋅) is the closer to 0, which makes the difference closer to 1.
sigmoid activation function, ensuring the scores lie within
[0,1]. An anomalous node should exhibit a much larger
Finally, NOVA combines the attribute-based and structure𝑗
𝑗
difference between 𝑑𝑖 (positive pair score) and 𝑑˜𝑖 (negative based signals into one hybrid anomaly score 𝑠𝑐𝑜𝑟𝑒(𝑣𝑖 ) =
pair score). The Jensen–Shannon divergence is used by 𝜆 𝑠𝑐𝑜𝑟𝑒𝑔 (𝑣𝑖 ) + 𝛾 𝑠𝑐𝑜𝑟𝑒𝑐 (𝑣𝑖 ). The values of 𝜆 and 𝛾 control
NOVA to quantify this difference:
how much behavioural deviations and topological
𝑁
(9)
1
inconsistencies contribute to the score. It also optimizes a
𝜑𝑗
𝜑𝑗
𝜑𝑗
𝐿𝐶 = −
∑ (log (𝑑𝑖 ) + log (1 − 𝑑˜𝑖 )) , 𝑗
single objective 𝐿 = 𝜆𝐿𝑔 + 𝛾𝐿𝑐 , where 𝐿 is the overall loss
2𝑁
𝑖=1
that balances generative attribute reconstruction and
∈ {1, … , 𝑘}
contrastive structural validation. During training, NOVA first
𝜑𝑗
𝜑𝑗
picks a group of target nodes from the IoV graph. For each
In this case, 𝐿𝐶 is the subgraph's contrastive loss for 𝑔𝑖
target node, it makes 𝑘 candidate contextual subgraphs and
Then. By averaging across all k subgraphs, the node's final
keeps the ones with the highest intimacy scores for later dualcontrastive loss is determined:

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

6
branch learning. Also, Fig. 3 shows NOVA's self-supervised
learning approach in detail.

Fig. 3. Dual-path self-supervised learning in NOVA.

V.

RESULTS AND COMPARISONS

In the next several parts, we will talk about the simulation
environments, datasets, assessment measures, and how our
results compare to the best ones out there.
A.
Simulation Environments
We create a multi-layer SUMO-NS3 co-simulation platform to
test NOVA in practice IoV scenarios with V2V, V2I and V2N
communications. SUMO simulates urban, highway, and mixed
mobility scenarios and NS-3 simulates wireless packet
delivery over IEEE 802.11p/DSRC and 5G NR-V2X channels,
including packet transmission rates, delays, jitters, dynamic
routing information, and mobility-induced link changes.
To ensure complete reproducibility, we explicitly define
NOVA's fundamental configurations before the presentation
of results. For each target node, we create contextual
candidates through random walks (with a walk length of 𝐿 =
4, 𝑀 = 10 walks per node, and 𝐾𝑐𝑎𝑛𝑑 = 20 candidate
subgraphs). We then keep the top 𝑘 = 5 contexts based on
the intimacy score calculated using PageRank-style damping
with 𝛼 = 0.15. For vehicular traces (VeReMi/CARLA), we
use a rolling time window of 𝛥 = 1 𝑠, and for flow datasets
(CICIDS2017/UNSW-NB15/NSL-KDD), we use a rolling
time window of 𝛥 = 5𝑠. Target-node anonymization is
implemented by replacing the target node’s feature vector with
an all-zero vector, i.e., 𝑥𝑖 ← 0 ∈ ℝ𝐹 , within each sampled
context subgraph, no mean vector or learnable [𝑀𝐴𝑆𝐾] token
is used. This makes reconstruction and structural validation
depend on the neighborhood. The generative branch uses a
one-layer GCN encoder and a one-layer GCN decoder with
ReLU activation. The contrastive branch uses mean pooling to
get the context embedding and a sigmoid bilinear
discriminator to score node–context pairs. Negative pairs are
made by changing the edge/feature of the contextual view.
Hybrid scoring uses balanced fusion with 𝜆 = 0.5 and 𝛾 =
0.5. The decision threshold is set to 𝜏 = 𝜏 ∗ selected on the
validation split by maximizing F1@τ (ties broken by lower
FAR). To cut down on the random selection of contexts, final
anomaly scores are averaged over 𝑅 = 5 repeated sampling
trials during inference.

B.
Dataset
We use five diverse data sources (VeReMi, CARLA-based
IoV traces, CICIDS2017, UNSW-NB15, and NSL-KDD) to
assess the NOVA under a variety of IoV and network-security
scenarios. VeReMi and CARLA include vehicle/V2X-focused
traces, containing malicious activity, mobility, and
communication events, whereas CICIDS2017 and UNSWNB15 provide a variety of contemporary IP-based attack
scenarios to test the cross-domain intrusion-detection capacity.
NSL-KDD is included as a baseline to compare with previous
IDS works. To facilitate fair comparisons, we map each of
these diverse data sources into a common set of dynamic
attributed graphs. At each time step 𝑡, we build 𝐺𝑡 =
(𝑉𝑡 , 𝐸𝑡 , 𝑋𝑡 ), where nodes represent IoV communication parties
(vehicles, RSUs, hosts, or infrastructure services), edges
model observed interactions, flows, or connectivity events,
and node attributes quantify a range of behavioral features
such as packet/byte rates, flow/messages count, inter-arrival
statistics, protocol or service type distributions, delay/loss
proxies, and mobility features when available. In VeReMi and
CARLA, we map graph structures to V2V, V2I and V2N
interactions; in CICIDS2017, UNSW-NB15, and NSL-KDD,
we treat endpoints as if they were IoV communication
endpoints and aggregate endpoint-level flow statistics.
To make it possible to reproduce the results, we turn each
dataset into a series of windowed, dynamically attributed
graphs 𝐺𝑡 = (𝑉𝑡 ,𝐸𝑡 , 𝑋𝑡 ), using fixed-length time windows of
length Δ (Table II shows the dataset-specific node/edge
definitions, window sizes, and feature groups). Nodes
represent entities that communicate (vehicles/RSUs for
vehicular traces; endpoints/hosts for flow datasets), edges
show "active links" that were seen in window 𝑡, and node
attributes 𝑋𝑡 are calculated as per-node aggregates of all
events/flows that were assigned to that window via 𝑡 =
⌊(𝑇 − 𝑇0 )/𝛥⌋. If 𝑢 and 𝑣 interact at least once in the
window, an edge (𝑢, 𝑣) ∈ 𝐸𝑡 is created. For flow datasets,
bidirectional flows are combined into a single undirected
interaction, with optional edge aggregates like flow count and
byte volume. In VeReMi and CARLA, active links come from
V2X message exchanges and/or connectivity events
(V2V/V2I/V2N). When both logs are available, message
exchange is given priority, and connectivity is used to keep
short-lived but physically plausible neighbors. We use a
consistent feature template across datasets, using available
subsets of: traffic intensity (packet/byte rates, message/flow
counts), timing (inter-arrival mean/variance, burstiness
proxies), protocol/service composition (e.g., TCP/UDP/ICMP
fractions or service types), reliability proxies (loss/failedconnection ratios or error indicators), routing/control
dynamics (vehicular traces), and mobility descriptors
(speed/acceleration/heading-change for CARLA/VeReMi); all
numeric features are normalized per dataset (z-score). We set
𝛥 = 1 𝑠 for vehicular traces and 𝛥 = 5 s for flow datasets
unless otherwise noted. To explicitly synchronize it, each
timestamp 𝑇 record is assigned a window 𝑡 = ⌊(𝑇 − 𝑇0 )/Δ⌋,
and all the packets, flows and mobility/beacon updates which
are mapped to the same t are considered to be concurrently
observed to form 𝐺𝑡 = (𝑉𝑡 , 𝐸𝑡 , 𝑋𝑡 ). We set 𝛥 in a way that
gathers several vehicular beacon chances and maintains local

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

7
mobility consistency, namely, we would take Δ = 1 s = 10𝑏
in the case of CAM/BSM-style signaling with nominal period
𝑏 ≈ 100 ms(10 Hz), and Δ = 5 s in the case of flow data.
When a node is sampled in between two beacon intervals, and
no new beacon-derived attribute is seen in the current window,
we use a last-observation-carried-forward rule in the same
(𝑚)
(𝑚)
horizon Δ; formally, 𝑥𝑖 (𝑡) = 𝑥𝑖 (𝑡 − ) in the most recent
valid observation 𝑡 − within that horizon, and otherwise the
attribute is replaced by a neutral default. The sampling is
therefore based on the representation on a synchronized
window level as opposed to a single beacon at the
instantaneous level, and therefore, the fact that beacon updates
will be missed occasionally does not refute context selection.
We also only synchronize asynchronous records by assigning
timestamps to windows and treating interactions within a
window as concurrent. Graphs are made for each dataset
separately (no merging across datasets) and split into threetime windows: 70% for training, 10% for validation, and 20%
for testing. This is done to avoid temporal leakage.
TABLE II
DATASET-TO-GRAPH MAPPING
Dataset
VeReMi
CARLA

Nodes
Vehicles/RSU
s
Vehicles/RSU
s

CICIDS2
017

Endpoints/hos
ts

UNSWNB15

Endpoints/hos
ts

NSLKDD

Logical
endpoints

Edges
V2X message
exchange
V2X
exchange/conne
ctivity
Flows per pair
(bidirectional
consolidated)
Flows per pair
(bidirectional
consolidated)
Connections
per pair

Δ
1s
1s
5s
5s
5s

Attributes
Intensity,
timing, routing
Intensity,
timing, mobility
Intensity,
timing,
protocol/service
Intensity,
timing,
protocol/service
Intensity,
timing,
protocol/service

C.
PERFORMANCE METRICS AND EVALUATION
We have chosen representative baselines that represent the key
paradigms of IoV/CAV anomaly detection: CNVA [20],
MKFA [22], IVNS [23], VADG [29], DST-IDS [35], and
GATransformer [36]. They collectively include CNNBiLSTM/VAE,
attention-transformer,
self-supervised
transformer, GAN-based, and graph-based IDS families, and
are compared using an identical data pipeline and metrics.
• Performance Comparison
Fig. 4 is a full comparison of all the baselines. Fig. 4(a) also
demonstrates that NOVA performs best on all datasets, with a
98.7% accuracy, 97.9% precision, 98.3% recall, and 98.1%
F1-score. The nearest competitor of the graph-based baselines
is GATransformer, then DST-IDS, which validates the
advantage of explicit spatio-temporal graph modeling.
Nevertheless, NOVA continues to perform better due to the
combination of intimacy-based context selection and GCNbased reconstruction with node-context contrastive validation.
Fig. 4(b) further shows that NOVA maintains the highest F1score across all datasets, ranging from 97.8% to 98.4%, while
GATransformer ranges from 97.2% to 97.8%, DST-IDS from
96.9% to 97.4%, VADG from 95.9% to 96.5%, IVNS from
94.6% to 95.1%, MKFA from 92.6% to 93.3%, and CNVA
from 91.0% to 91.5%. The respective FAR trends are reported
in Fig. 4(c), with the lowest false-alarm rate of NOVA

between 3.8% and 4.5%. Comparatively, the graph-based
baselines would be upper, 5.0%-5.6% of GATransformer and
5.8%-6.5% of DST-IDS, whereas the non-graph baselines
have higher FAR values.

Fig. 4. Performance comparison of methods across the average
results of all datasets.
TABLE III
PER-DATASET PERFORMANCE COMPARISON (%)
Dataset
VeReMi
VeReMi
VeReMi
VeReMi
VeReMi
VeReMi
VeReMi
CARLA
CARLA
CARLA
CARLA
CARLA
CARLA
CARLA
CICIDS2017
CICIDS2017
CICIDS2017
CICIDS2017
CICIDS2017
CICIDS2017
CICIDS2017
UNSW-NB15
UNSW-NB15
UNSW-NB15
UNSW-NB15
UNSW-NB15
UNSW-NB15
UNSW-NB15
NSL-KDD
NSL-KDD
NSL-KDD
NSL-KDD
NSL-KDD
NSL-KDD
NSL-KDD

Method
NOVA
GATransformer
DST-IDS
VADG
IVNS
MKFA
CNVA
NOVA
GATransformer
DST-IDS
VADG
IVNS
MKFA
CNVA
NOVA
GATransformer
DST-IDS
VADG
IVNS
MKFA
CNVA
NOVA
GATransformer
DST-IDS
VADG
IVNS
MKFA
CNVA
NOVA
GATransformer
DST-IDS
VADG
IVNS
MKFA
CNVA

Accuracy
98.9
98.1
97.7
96.7
95.4
93.5
91.8
98.6
97.5
97.1
96.4
95.2
93.2
91.5
98.8
98.0
97.6
97.0
95.7
93.9
92.0
98.5
97.4
97.0
96.6
95.3
93.6
91.7
98.7
97.8
97.4
96.9
95.6
93.8
91.9

Precision
98.2
97.4
97.1
96.0
94.6
92.7
91.0
97.8
96.9
96.6
95.8
94.5
92.4
90.9
98.0
97.3
97.0
96.3
95.0
93.0
91.3
97.6
96.8
96.5
95.9
94.7
92.8
91.1
97.9
97.1
96.8
96.2
94.9
92.9
91.2

Recall
98.6
98.2
97.7
96.4
95.1
93.1
91.5
98.1
97.7
97.2
96.0
94.8
92.8
91.1
98.4
98.1
97.7
96.7
95.3
93.6
91.7
98.0
97.6
97.3
96.2
95.0
93.2
91.4
98.3
97.9
97.5
96.5
95.2
93.4
91.6

F1-Score
98.4
97.8
97.4
96.2
94.9
92.9
91.2
97.9
97.3
96.9
95.9
94.6
92.6
91.0
98.2
97.7
97.3
96.5
95.1
93.3
91.5
97.8
97.2
96.9
96.0
94.8
93.0
91.2
98.1
97.5
97.1
96.3
95.0
93.2
91.4

Table III shows how well VeReMi, CARLA,
CICIDS2017, UNSW-NB15, and NSL-KDD did on each
dataset (Accuracy, Precision, Recall, and F1-Score). Its
accuracy is around 98.5–98.9%, and its F1-Score is around
97.8–98.4%, which shows that it can detect things well and
consistently across different situations.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

8
and P99 from ~40 to 100 ms, and a sustained throughput of
~4.7 k events/s at 5 k msg/s.
The end-to-end latency for real-time detection includes
three stages: (i) graph orchestration, which includes graph
feature extraction, time-windowing, and incremental graph
updates; (ii) context selection includes candidate generation,
intimacy scoring, and top-k selection; and (iii) model
inference includes GCN encoder–decoder passes, contrastive
discrimination, and hybrid scoring. The subgraph-local
inference cost is 𝑂(𝑅𝑘 ∣ 𝑉𝑠 ∣ 𝐹𝐻), and the final scoring costs
𝑂(𝑅(𝐹 + 𝐻)). To minimize overhead during mobility churn,
RSUs incrementally update local graph neighborhoods and are
then able to reuse cached neighbor statistics for intimacy
scoring without reconstructing the entire graph.
• False Alarms under Mobility Churn
We examine the urban mobility churn in QOS evaluation:
FAR and F1@τ in Fig. 6. The best performance is achieved by
NOVA, where the FAR is 0.05 and the F1@τ is 0.98,
indicating that it is very robust to speed changes, link
dynamics and handoffs. VADG outperforms with FAR = 0.08
and F1@τ = 0.95, and IVNS achieves F1 = 0.94 and FAR =
0.09, but has no structural adaptability. The handcrafted
features cause MKFA to perform moderately (0.10, 0.93) and
the lack of structural awareness causes CNVA to perform
worse (0.12, 0.91).

Fig. 6. FAR and F1-score at threshold τ (F1@τ).

Fig. 5. QoS under variable input load (500→5k messages/s):
per-method P95/P99 end-to-end latency (left Y) and
throughput (right Y).
Since this may be biased by the corpus, the latency and
throughput data reported in Fig. 5 are averages over all
datasets. P95 latency is used to encode high load latency
behavior and P99 latency is used to capture tail latency
behavior, which is critical for such applications as emergency
messages in IoV applications, braking decisions, and multihop relay V2X. As the input load is increased to 5 k msg/s, the
delay growth of CNVA is the highest among the three, with
P95 growing from ~70 to 180 ms, and P99 growing from ~90
to 240 ms, and the events/s is still ~2.3 k events/s. The
overhead of feature-engineering and distillation, however,
causes high tail latency in MKFA, whereas both throughput
and tail latency are low. IVNS and VADG have lower latency
and higher throughput, with IVNS reaching P95/P99 of
~110/~150ms and ~3.6k events/s, and VADG reaching
~105/~145ms and ~3.7k events/s at a high load. NOVA's
latency profile is quite flat, with P95 rising from ~30 to 80 ms,

• Structural Attack Robustness
Fig. 7, it shows that Sybil identities, bogus neighbor
insertions, and link perturbations are effective structural
attacks on IoV communication graphs. NOVA has the best
AUROC of 0.99, AUPRC of 0.98 and the lowest
misclassification error of 0.05. VADG and IVNS are also
good, but do not show an explicit use of structural reasoning
and focus primarily on sequential patterns.

Fig. 7. Structural attack robustness across methods, showing
AUROC, AUPRC, and inverse MR (1-MR).

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

9
• Label Efficiency / Label-Free Operation
The label efficiency is measured on CICIDS2017 and UNSWNB15, where 10% of the data is labeled for reliable labels for
controlled ablation, as shown in Fig. 8. The AUROC of
CNVA and MKFA drops significantly as the number of labels
decreases, and eventually becomes below AUROC 0.70 when
there are no labels. Although limited supervision, VADG stays
stable with little improvement, IVNS, thanks to selfsupervised transformer learning, remains above 0.90. Without
label information, NOVA gets the best fit at 0.89, and keeps
increasing steadily to 0.97 at 10% labels.

highest level of resistance, with an AUROC of ≈0.95 (≈0.93);
and the backdoor success rate is around 10%. IVNS and
VADG are still moderately powerful (≈0.85-0.88 AUROC),
but IVNS is still prone to sequence-level triggers and VADG
to poisoning instability. The performance of the two
algorithms that do not use adversarial regularization, MKFA
and CNVA, is weakest with AUROCs less than ≈0.85.
Overall, NOVA has an AUROC of about 10% higher and 2–3
times lower poisoning success, making it more appropriate for
adversarial IoV deployments.

Fig. 8. AUROC vs. label fraction across methods under CICIDS2017
and UNSW-NB15 datasets with labels gradually ablated.

• Concept Drift & Online Adaptation
These datasets were then used to simulate progressive drift
with various conditions of vehicles and clouds. Based on Fig.
9, NOVA is the most “stable”, as it has suffered only a ~4%
drop in F1, and IVNS a ~6% drop in F1. VADG experiences a
drop of ~14% when the traffic is not stationary, while MKFA
experiences a drop of 20% because of handcrafted features.
The performance is worst in CNVA with a drop of more than
24% due to the fact that the feature is static and the
embeddings are static, which is bound to a sensor.

Fig. 10. Throughput, latency, and memory usage for CNVA, MKFA,
IVNS, VADG, and NOVA as the number of vehicles increases from
500 to 50,000 in NS-3 with RSU aggregation.

Fig. 11. Adversarial and poisoning robustness across methods.
Fig. 9. Concept drift and online adaptation.

• Scalability with Fleet/Graph Size
There are differences in scalability in large vehicle networks,
as illustrated in Fig. 10. NOVA does best on 50,000 vehicles,
processing up to 25,000 events/s, and achieving a latency of
less than 40 ms and memory of less than 2 GB. MKFA and
CNVA scale poorly, achieving 2,800 and just over 2,000
events/s, respectively, while CNVA consumes over 120 ms
latency and 4 GB of memory.
• Adversarial & Poisoning Robustness
Fig. 11 compares the robustness with respect to FGSM, PGD
and poisoning attacks. Under FGSM (PGD), NOVA has the

• Cross-Modality Generalization
The differences in modality transfer are obvious as seen in
Fig. 12. The smallest generalization gaps (~0.05 sensor-tocomm and ~0.04 comm-to-sensor) are obtained by NOVA,
which can simultaneously learn a combination of attribute
vectors and structural embeddings in its graph abstraction. The
lower gaps follow after IVNS (~0.12/0.11), but the stability is
affected by the topology changes. However, the gaps for
CNVA (~0.20/0.18) are the largest, attributable to the reliance
on engineered features, and the reliance on a LiDAR-like
sensor setting means that the accuracy is not maintained when
transferring beyond that setting.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

10
attacker and the alignment-only attacker, respectively. The
best is the joint multi-context attacker, where there is
simultaneous perturbation of features and topology, which
raises its ASR between 15 and 51.

Fig. 12. Cross-modality generalization gap (ΔAUROC) when
transferring from sensor-heavy datasets (LiDAR/CARLA) to
communication-heavy datasets.

• Absolute Context-Selection Latency Analysis
The absolute wall-clock latency of the isolated contextselection stage in the same settings was reported in Fig. 13 and
the absolute latency of the RandomWalk baseline was
compared to the intimacy-guided selection of NOVA.
RandomWalk baseline can only generate the candidates
through random-walking, but NOVA can generate the
candidates and then score them using intimacy and select the
top-k. The extra overhead of the intimacy-guided selection is
not very large in absolute terms: the mean latency becomes
5.36 ms and the P95 and P99 latencies become 7.41 ms and
8.94 ms, respectively. These correspond to absolute increases
of 1.08 ms, 1.36 ms, and 1.63 ms, and relative overheads of
25.2%, 22.5%, and 22.3%, respectively.

Fig. 14. ASR under increasingly strong adaptive attacks.

• Sparse-Context Fallback and Performance
Fig. 15 demonstrates how decreased availability of context
affects NOVA with a sparse-context fallback policy, where the
model applies all available high-intimacy contexts and
averages the score by this actual number. Starting from the
default regime of 𝑚 = 5, NOVA achieves F1@τ = 0.980,
AUROC = 0.990, and FAR = 0.040. The degradation is small
when one of the contexts is not present (𝑚 = 4), with F1@τ
0.976, AUROC = 0.987, and FAR = 0.043, or a loss of just 0.4
percentage points in F1 and 0.3 points in AUROC. At 𝑚 = 3,
the performance is good with F1=0.969, AUROC=0.981, and
FAR is slightly greater, at 0.048. More noticeable degradation
appears only under severe sparsity: at 𝑚 = 2, F1@τ drops to
0.955, AUROC to 0.970, and FAR rises to 0.058; at 𝑚 = 1,
the model reaches F1@τ = 0.934, AUROC = 0.951, and FAR
= 0.071.

Fig. 13. Absolute context-selection latency comparison between the
RandomWalk baseline and NOVA’s intimacy-guided selection under
identical settings.

•

Adaptive Joint-Objective Multi-Context Attack
Robustness
Fig. 14 provides the Attack Success Rate (ASR) of four
increasingly robust adaptive adversaries with perturbation
budgets of 2 to 10%. The weakest of the two attackers is the
reconstruction-only attacker, whose ASR grows slowly, 6 to
22 percent, which means that it is not enough to suppress the
generative signal to be able to evade NOVA with a high
probability. The alignment-only attacker is more potent, and
ASR rises by 8 to 29, and it is clear that the attack on the
node-context similarity is more effective than the attack on the
reconstruction error, yet it is not strong enough to outsmart the
hybrid detector. The joint multi-context attacker is
significantly stronger when both objectives are being
optimized: the feature-only joint multi-context attacker
achieves ASR 12% at 2% budget and 43% at the 10% budget,
a 21% and 14% improvement over the reconstruction-only

Fig. 15. Performance degradation under reduced context availability
using NOVA’s sparse-context fallback. When fewer than the default
𝑘 = 5 high-intimacy contexts are available, the model uses all
available contexts and normalizes by the actual count.

As can be seen in Fig. 16, NOVA is the strongest when
stressed. NOVA achieves the lowest F1@τ (0.982→0.965)
and the lowest FAR increase (0.038→0.055) compared to
DST-IDS and GATransformer, which shows that it has the
least mobility churn. NOVA also shows improved AUROC
(0.990→0.968) and reduced MR (0.045→0.078) under a
structural perturbation. In concept drift, both baselines
(0.981→0.956 and 0.975) degrade less and recover from the
update faster than NOVA (0.981→0.956 and 0.975) does.
As can be seen in the results shown in Fig. 17, NOVA is
the most efficient in terms of deployment when realistic IoV
workloads are taken into account. NOVA has the lowest P99

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

11
latency as load progressively increases from 500 to 5000
messages/s, increasing from ~38 to ~95 ms, which is better
than DST-IDS (~42–155 ms) and GATransformer (~44–165
ms). NOVA also achieves the highest throughput across 500–
50,000 nodes (~8,500–25,500 events/s) while using the least
memory at 50,000 nodes (~1.85 GB vs. 2.80 GB and 3.10
GB).

Fig. 16. Robustness stress test under realistic IoV conditions: (a)
churn effects on F1@τ/FAR, (b) structural attacks on AUROC/MR,
and (c) concept drift effects on F1@τ.

Fig. 17. Deployment efficiency of NOVA vs. GNN baselines: (a) P99
latency under increasing load, (b) throughput across fleet/graph
sizes, and (c) peak memory usage across fleet/graph sizes.

D.

Complexity Analysis

Let 𝑁 =∣ 𝑉 ∣be the number of nodes in the global IoV graph,
𝐾cand the number of candidate subgraphs per target node,
𝐿 the random-walk length, 𝑘 the number of selected contexts,
𝑅 the number of repeated inference trials, and ∣ 𝑉𝑠 ∣, ∣ 𝐸𝑠 ∣, 𝐹,
and 𝐻 the average subgraph nodes, subgraph edges, input
feature dimension, and hidden dimension, respectively. During
inference, candidate generation costs 𝑂(𝐾cand 𝐿), intimacy

scoring costs 𝑂(𝐾cand (∣ 𝑉𝑠 ∣ +∣ 𝐸𝑠 ∣)), and top-𝑘 selection
costs 𝑂(𝐾cand log 𝑘). For each selected context, the one-layer
GCN encoder–decoder costs 𝑂(∣ 𝑉𝑠 ∣ 𝐹𝐻+∣ 𝐸𝑠 ∣ (𝐹 + 𝐻)),
while pooling, bilinear node–context discrimination,
reconstruction-distance computation, and score fusion add 𝑂(∣
𝑉𝑠 ∣ 𝐻 + 𝐻2 + 𝐹). Therefore, the per-node inference
complexity
is
𝑂(𝑅[𝐾cand (𝐿+∣ 𝑉𝑠 ∣ +∣ 𝐸𝑠 ∣ +log 𝑘) +
𝑘(∣ 𝑉𝑠 ∣ 𝐹𝐻+∣ 𝐸𝑠 ∣ (𝐹 + 𝐻)+∣ 𝑉𝑠 ∣ 𝐻 + 𝐻2 + 𝐹)]).
Under
bounded RSU-local contexts, 𝐾cand , 𝐿, 𝑘, 𝑅, ∣ 𝑉𝑠 ∣, and ∣ 𝐸𝑠 ∣
are fixed deployment constants. Hence, the per-node
inference cost is independent of the global fleet size 𝑁, and
fleet-level inference scales linearly as 𝑂(𝑁). This formal
inference-time complexity supports NOVA’s real-time
execution on the RSU-side and vehicular-edge infrastructure.
E.
Discussion
NOVA can be deployed in an edge–cloud hierarchy to achieve
a balance of latency, bandwidth and computational cost for
real IoV systems. On the edge, RSUs are capable of windowed
feature aggregation, intimacy-driven subgraph sampling and
lightweight inference based on a GCN and hybrid anomaly
scoring, allowing to detect anomalies in real-time without
sharing raw telemetry. Cloud provides long-term statistics,
calibrates thresholds, provides cross-RSU consistency, retrains
the model, tunes hyperparameters, and distills global models
for heterogeneous RSUs. RSUs should be located at highobservability hot-spots (intersections, highway merges, urban
corridors), and overlap should be provided to enhance handoff
and cross-RSU scoring. Communication overheads are
minimized by having RSUs send only a summary and a few
graph updates, and the cost of the uplink varies roughly as 𝑂(∣
𝑉𝑅𝑆𝑈 ∣⋅ 𝐷) + 𝑂(∣ 𝐸𝑅𝑆𝑈 ∣) per window, after sparsification,
quantization and batching. Updates of the model are made
using a hybrid approach: frequent lightweight threshold
adjustments, and infrequent changes of the model when
retraining is scheduled or when a drift indicator is activated.
To guarantee the same detection, in bandwidth-limited
settings, model deltas or distilled student models can be
downloaded to the RSUs.
Also, our experiments focus on standard evasion and
poisoning; however, it is crucial to account for adaptive
adversaries that exploit both attributes and topology to
concurrently diminish reconstruction error and enhance nodecontext alignment. Transferable adversarial attacks add
another form of black-box threat where the attacker trains a
surrogate IDS on a similar set of data of vehicles and applies
the resulting perturbations to NOVA. NOVA can be
susceptible to these attacks in part due to its GCN encoder that
projects node attributes and local topology into latent
embeddings, and trained surrogate graph models that learn
partially correlated feature sensitivities on similar V2X
distributions. But in NOVA, we also have mechanisms that are
capable of lowering direct transferability. Target-node
anonymization makes sure that the detector does not just use
the raw feature vector of the target node, but rather requires
reconstruction and validation to be based upon neighborhood
context, which has the ability to smooth sensitivities of
shortcut-based features. Furthermore, intimacy-based multicontext testing involves transferred perturbations to be

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

12
consistent among a set of highly relevant subgraphs, whereas
hybrid generative-contrastive scoring involves the attacker
minimizing
reconstruction
error
and
node-context
compatibility at the same time. Thus, despite the fact that
NOVA is not resistant to transferable adversarial attacks, its
context-conditioned and dual-path representation does not
ensure the direct perturbation transfer in comparison with the
IDS models that are based solely on features.
NOVA is hard to evade as a node is evaluated in multiple
intimacy-selected contexts using both GCN-based profile
synthesis and node-node contrast in an intimacy-driven
context. So, adversaries must preserve their behavior across
multiple relevant neighborhoods as topologies shift due to
mobility. Although poisoning or collusion attacks (e.g., Sybil)
can still impact the learned normal profile, NOVA mitigates
shortcut learning by anonymizing target nodes and assessing
valid (as opposed to malicious) contexts. In practice,
robustness can be further enhanced using a sliding-window
retraining, trusted-trace calibration, cross-RSU correlation,
reputation, and plausibility checks in the physical layer.
VI. CONCLUSION AND FUTURE WORK
In this paper, we introduced a self-supervised graph-based
framework for IoV anomaly detection, called NOVA. NOVA
is designed to detect behavioral and topological anomalies by
engaging in both graph structure validation via contrastive
learning and attribute reconstruction using the GCN
framework while simultaneously sampling graphs from the
graph domain with guidance from the intimacy. NOVA
achieves high detection accuracy, F1 score, AUROC/AUPRC,
low FAR and latency, scalable and high adversarial robustness
and outperforms baselines in all these metrics across extensive
evaluations
performed
on
VeReMi,
CARLA-IoV,
CICIDS2017, UNSW-NB15, and NSL-KDD. NOVA is
effective in the presence of mobility churn, structural attacks,
concept drift, label scarcity and poisoning/evasion attempts,
and is scalable linearly and maintains near real-time tail
latency. The results show that the self-supervised graph
learning with anonymized contextual reconstruction and
hybrid scoring is a viable and reliable learning paradigm for
ensuring safety in safety-critical IoV/V2X environments.
We tested NOVA in real time using a SUMO–NS3 cosimulation IoV testbed with RSU/cloud hardware. The results
were promising, but there are still some problems. First, the
testbed uses simulated mobility and network stacks, so more
field testing with V2X traffic over the air is needed to make
sure it works in the real world. Second, even though we add
examples of behavioral and structural anomalies (like Sybil,
DoS, and link perturbations), the adversarial landscape is
always changing. This calls for more stress testing and
constant model updates to protect against multi-stage, stealthy,
and adaptive attacks. Future directions will also test black-box
transferable adversarial attacks on independently trained
surrogate graph models and explore randomized latent feature
selection or feature-subspace ensembling as other defense
strategies. Thirdly, NOVA uses subgraph-local reconstruction
and node–context validation, which could turn out to be less
reliable in scenarios characterized by sparse connectivity or
high mobility, where the neighborhood structure is unstable

and thresholds might be more difficult to calibrate. Future
work will involve: (i) Federated and edge distributed NOVA
for privacy preserving cross fleet learning; (ii) Temporal graph
extensions for dynamic V2X interactions and short-lived
anomalies; (iii) Cross-modality fusion with LiDAR, GPS, and
radar; (iv) Trust/reputation integration for risk-aware
mitigation; (v) Adaptive thresholding and online calibration
against poisoning and evasion; and (vi) hardware efficient
acceleration for real-time RSU and in-vehicle deployment.
SUPPLEMENTARY MATERIAL
Additional ablation studies, sampling and anonymization
analyses, parameter-sensitivity evaluations, robustness results,
and real-time deployment details are provided in the
Supplementary Material.
DECLARATION OF COMPETING INTEREST: NA
REFERENCES
[1]

[2]
[3]

[4]
[5]
[6]

[7]
[8]
[9]

[10]

[11]

[12]

[13]

I. U. Din, K. H. Khan, A. Almogren, and M. Guizani, "Machine
Learning for Trust in Internet of Vehicles and Privacy in
Distributed Edge Networks," IEEE Internet of Things Journal,
2025.
Y. Fang et al., "Anomaly diagnosis of connected autonomous
vehicles: A survey," Information fusion, vol. 105, p. 102223, 2024.
H. I. Ali, H. Kurunathan, M. H. Eldefrawy, F. Gruian, and M.
Jonsson, "Navigating the challenges and opportunities of securing
internet of autonomous vehicles with lightweight authentication,"
IEEE Access, 2025.
R. Wang et al., "A Glimpse of Physical Layer Security in Internet
of Vehicles: Joint Design of the Transmission Power and Sensing
Power," IEEE Transactions on Vehicular Technology, 2025.
T. Alshammari and I. Mahgoub, "Nature-inspired algorithms in the
internet of vehicles: A survey and analysis," IEEE Internet of
Things Journal, 2025.
J. R. V. Solaas, E. Mariconti, and N. Tuptuk, "Systematic literature
review: Anomaly detection in connected and autonomous
vehicles," IEEE Transactions on Intelligent Transportation
Systems, 2024.
H. Huang, P. Wang, J. Pei, J. Wang, S. Alexanian, and D. Niyato,
"Deep learning advancements in anomaly detection: A
comprehensive survey," IEEE Internet of Things Journal, 2025.
A. Sakhnevych, N. Pasquino, and G. Sperlì, "Design of a machine
learning approach to anomaly detection in tyre-road interaction,"
IEEE Access, 2025.
L. Zheng, T. Feng, Z. Xie, X. Li, and C. Su, "BARM: BlockchainAssisted Anonymous Authentication and Reputation Management
for Mobile Crowdsensing in Internet of Vehicles," IEEE Internet
of Things Journal, 2025.
P. K. R. Lebaku, L. Gao, Y. Zhang, Z. Li, Y. Liu, and T. Arafin,
"Cybersecurity-focused anomaly detection in connected
autonomous vehicles using machine learning," in International
Conference on Transportation and Development 2025, 2025, pp.
566-580.
Y. Zhang et al., "A cooperative vehicle-road system for anomaly
detection on vehicle tracks with augmented intelligence of things,"
IEEE Internet of Things Journal, vol. 11, no. 22, pp. 35975-35988,
2024.
S. Mishra, N. Sengar, and D. Har, "A Secure, Blockchain-Enabled
Vehicular Sensor Communication Protocol With Deep LearningAssisted Anomaly Detection," IEEE Intelligent Transportation
Systems Magazine, 2025.
X. Wang et al., "Hyperspectral Anomaly Detection Using DualBranch Network Based on Frequency Domain Learning," IEEE
Journal of Selected Topics in Applied Earth Observations and
Remote Sensing, 2025.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696324

13
[14]

[15]

[16]

[17]

[18]
[19]

[20]
[21]
[22]

[23]

[24]

[25]
[26]

[27]

[28]

[29]

[30]

[31]

[32]

[33]

S. Baccari, M. Hadded, H. Ghazzai, H. Touati, and M. Elhadef,
"Anomaly detection in connected and autonomous vehicles: A
survey, analysis, and research challenges," IEEE access, vol. 12,
pp. 19250-19276, 2024.
D. Wang, L. Ren, X. Sun, L. Gao, and J. Chanussot, "Non-local
and local feature-coupled self-supervised network for
hyperspectral anomaly detection," IEEE Journal of Selected Topics
in Applied Earth Observations and Remote Sensing, 2025.
Q. Cheng, K. Hong, K. Huang, and Z. Liu, "Evaluating
Effectiveness and Identifying Appropriate Methods for Anomaly
Detection in Intelligent Transportation Systems," IEEE
Transactions on Intelligent Transportation Systems, 2025.
Z. Song, Y. Tao, Z. Hua, S. Wang, G. Pan, and J. An, "Generative
Artificial Intelligence-Empowered Multidomain Internet of
Vehicles Systems: Scalability, Efficiency, and Suitability," IEEE
Vehicular Technology Magazine, 2025.
J. Boone, T. Seyfi, and F. Afghah, "A Joint Reconstruction-Triplet
Loss Autoencoder Approach Towards Unseen Attack Detection in
IoV Networks," IEEE Internet of Things Journal, 2025.
E. Nowroozi, M. Mohammadi, A. Rahdari, R. Taheri, and M.
Conti, "A random deep feature selection approach to mitigate
transferable adversarial attacks," IEEE Transactions on Network
and Service Management, 2025.
N. Sboui, H. Ghazzai, M. Hadded, M. Elhadef, and G. Setti,
"Unsupervised Hybrid VAE-Based Anomaly Detection for Vehicle
Onboard LiDAR Sensors," IEEE Access, 2025.
P. K. Tiwari et al., "A secure and robust machine learning model
for intrusion detection in internet of vehicles," IEEE Access, 2025.
P. Cheng, S. Liu, Z. Wu, L. Tan, and G. Liu, "MKF-ADS: MultiKnowledge Fusion Based Anomaly Detection System in Vehicular
Control Area Networks," IEEE Transactions on Vehicular
Technology, 2025.
J. Cao et al., "Anomaly detection for in-vehicle network using selfsupervised learning with vehicle-cloud collaboration update,"
IEEE Transactions on Intelligent Transportation Systems, vol. 25,
no. 7, pp. 7454-7466, 2024.
L. Zhao et al., "Generative abnormal data detection for enhancing
cellular vehicle-to-everything-based road safety," IEEE
Transactions on Green Communications and Networking, vol. 8,
no. 4, pp. 1466-1478, 2024.
A. Singh and H. Rathore, "Advancing connected vehicle security
through real-time sensor anomaly detection and recovery,"
Vehicular Communications, vol. 52, p. 100876, 2025.
X. Li, C. Xie, Z. Zhao, C. Wang, and H. Yu, "Anomaly detection
algorithm of industrial internet of things data platform based on
deep learning," IEEE Transactions on Green Communications and
Networking, vol. 8, no. 3, pp. 1037-1048, 2024.
P. Mansourian, N. Zhang, A. Jaekel, and M. Kneppers, "Deep
learning-based anomaly detection for connected autonomous
vehicles using spatiotemporal information," IEEE Transactions on
Intelligent Transportation Systems, vol. 24, no. 12, pp. 1600616017, 2023.
F. Van Wyk, Y. Wang, A. Khojandi, and N. Masoud, "Real-time
sensor anomaly detection and identification in automated
vehicles," IEEE Transactions on Intelligent Transportation
Systems, vol. 21, no. 3, pp. 1264-1276, 2019.
S. Devika, R. R. Shrivastava, P. Narang, T. Alladi, and F. R. Yu,
"Vadgan: An unsupervised gan framework for enhanced anomaly
detection in connected and autonomous vehicles," IEEE
Transactions on Vehicular Technology, vol. 73, no. 9, pp. 1245812467, 2024.
Z. Yang et al., "Anomaly detection against GPS spoofing attacks
on connected and autonomous vehicles using learning from
demonstration," IEEE Transactions on Intelligent Transportation
Systems, vol. 24, no. 9, pp. 9462-9475, 2023.
Z. He, Y. Chen, D. Zhang, H. Zhang, and M. Liu, "MF-CANN: A
Novel Anomaly Detection Method for Connected and Automated
Vehicles," IEEE Transactions on Industrial Cyber-Physical
Systems, vol. 2, pp. 588-596, 2024.
Z. He, Y. Chen, H. Zhang, and D. Zhang, "WKN-OC: A new deep
learning method for anomaly detection in intelligent vehicles,"
IEEE Transactions on Intelligent Vehicles, vol. 8, no. 3, pp. 21622172, 2023.
F. Khanmohammadi and R. Azmi, "Time-series anomaly detection
in automated vehicles using d-cnn-lstm autoencoder," IEEE

[34]

[35]

[36]

Transactions on Intelligent Transportation Systems, vol. 25, no. 8,
pp. 9296-9307, 2024.
Z. Zhang, Y. Yao, W. Hutabarat, M. Farnsworth, D. Tiwari, and A.
Tiwari, "Time series anomaly detection in vehicle sensors using
self-attention mechanisms," IEEE Transactions on Intelligent
Transportation Systems, 2024.
G. A. Al-Absi, Y. Fang, A. A. Qaseem, and H. Al-Absi, "DSTIDS: Dynamic spatial-temporal graph-transformer network for invehicle network intrusion detection system," Vehicular
Communications, vol. 55, p. 100962, 2025.
S. Wang, Y. Zhao, X. Fu, H. Si, W. Wang, and L. Xue, "A classimbalance-aware intrusion detection system based on
spatiotemporal graph neural networks for software-defined
vehicles," Journal of Information Security and Applications, vol.
97, p. 104340, 2026.

Arash Heidari received the Ph.D. degree in
computer engineering in 2023. He is ranked
among the top 1% of scientists worldwide
(Web of Science and ISC) and is listed in
Stanford University’s ranking of the top 2% of
global scientists. He is currently a Senior
Research Scientist and a Visiting Postdoctoral
Researcher,
with
interdisciplinary
collaborations spanning Europe, the Middle
East, and North America. His research
interests include the IoT, computer vision,
distributed
computing,
deep
learning,
explainable artificial intelligence, and evolutionary computing.
Jamal Al-Karaki is currently a full
professor at CIS, Zayed university. He has a
rich University career in education, service,
and research. He holds a PhD degree (with
Distinction) in Computer Engineering from
the Iowa State University, USA, with
Research Excellence Award. He has a
proven record of progressive responsibility
including leadership positions as a college
Dean, Director of IT, Co-Founder and Dept.
Head at various institutes. He led the
development of some national centers in cyber security as well as
undergraduate and graduate computing programs. As an active researcher, he
develops plans to advance the research agenda at CIS. He Published 90+
refereed technical articles in scholarly international journals and conference
proceedings. He is a senior member of IEEE and Tau Beta Pi. He is a member
of Mohammad Bin Rashid Academy for Scientists in UAE and recently listed
among the top 2% highly cited researchers in his field worldwide. He is also a
certified reviewer for CAA and certified Pearson EDI verifier/assessor.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
