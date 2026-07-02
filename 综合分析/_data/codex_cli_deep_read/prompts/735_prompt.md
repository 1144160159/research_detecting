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
# [735] MAGNN: Multi-scale adaptive graph neural networks with contrastive learning for malicious network traffic detection
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
编号：735
题名：MAGNN: Multi-scale adaptive graph neural networks with contrastive learning for malicious network traffic detection
年份：2026
DOI：10.1016/j.jpdc.2026.105240
来源：Journal of Parallel and Distributed Computing
PDF：paper/10.1016_j.jpdc.2026.105240.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\735.txt
- 原始字符数：77852
- 本次发送字符数：77852
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
MAGNN: Multi-scale adaptive graph neural networks with contrastive
learning for malicious network traﬃc detection
Mukhtar Ahmed
a

a , Jinfu Chen

a,b,∗, Ernest Akpaku

a , Ali Bux

c

School of Computer Science and Communication Engineering, Jiangsu University, 301 Xuefu Road, Zhenjiang, 212013, Jiangsu, China

b Jiangsu Key Laboratory of Security Technology for Industrial Cyberspace, Jiangsu University, 301 Xuefu Road, Zhenjiang, 212013, Jiangsu, China
c

School of Management, Jiangsu University, 301 Xuefu Road, Zhenjiang, 212013, Jiangsu, China

a r t i c l e

i n f o

Keywords:
Malicious network traﬃc
Network security
Multi-scale contrastive learning
Graph neural networks
Temporal-node contrast
Edge-level contrast

a b s t r a c t
Network traﬃc analysis is a critical task in cybersecurity, enabling the classiﬁcation of malicious traﬃc and the
identiﬁcation of potentially dangerous connections. Existing approaches often utilize traditional graph neural
networks (GNNs) to represent and analyze the inherent graph-like structures in network traﬃc, where nodes
correspond to entities such as IP addresses or devices, and edges represent communication or data ﬂow between
them. However, these methods primarily focus on node features, often neglect crucial edge-level (packet-level)
information and struggle to adapt to diverse and evolving traﬃc patterns. To overcome these limitations, we
propose a novel framework, Multi-Scale Adaptive Graph Neural Networks (MAGNN), for malicious network trafﬁc detection. MAGNN integrates both node and edge features within a multi-scale contrastive learning framework, introducing three novel mechanisms: temporal-node contrast, edge-level contrast, and multi-head hierarchical contrast, to capture complex dependencies in network behavior. MAGNN is evaluated on four diverse
benchmark datasets-CTU-13, ISCXVPN2016, CICIDS-2017, and CIRA-CIC-DoHBrw-2020-demonstrating superior
performance in detecting malicious traﬃc. In addition to classiﬁcation accuracy, MAGNN supports temporal
traﬃc trend estimation, where error-based (regression-task) metrics are employed to assess the model’s ability
to forecast evolving traﬃc dynamics. Furthermore, MAGNN demonstrates robust scalability through linear computational complexity, support for distributed training with multi-GPU architectures, and eﬃcient convergence
across large-scale graphs.

1. Introduction
The increasing frequency and sophistication of cyberattacks pose
substantial threats to the security of computer networks and information
systems. Malicious network traﬃc detection methods are critical for protecting critical infrastructure by analyzing raw network traﬃc, such as
packet captures or ﬂow-based records, to extract detailed statistics and
identify potential threats. Traditional malicious detection approaches
are broadly categorized into signature-based and behavior-based methods. Signature-based methods rely on predeﬁned rules or metrics to classify traﬃc, while behavior-based approaches use machine learning to
detect complex and evolving attack patterns [1]. Behavior-based approaches [2,3] are preferred for their ability to detect previously unseen attacks, including zero-day vulnerabilities, but their reliance on
large volumes of labeled data often limits their practicality in real-world
scenarios [4].

Another limitation of traditional detection systems is their inability
to capture topological patterns in network traﬃc. These patterns are vital for identifying advanced intrusions, such as persistent threats that
involve lateral movement across a network [5]. Incorporating topological relationships into detection frameworks can signiﬁcantly enhance
their ability to detect sophisticated attacks by analyzing network graph
structures and communication pathways [6].
Graph-based deep learning has emerged as a promising approach
for addressing these challenges due to its ability to handle complex
relational data [7,8]. Within this domain, graph-based malicious trafﬁc detection identiﬁes malicious nodes in graph structures and has
been widely applied in areas such as ﬁnancial fraud detection, misinformation detection, and network intrusion detection [9,10]. Unlike
other ﬁelds of malicious detection, graph-based methods uniquely combine node features and graph structures, enabling a more comprehensive analysis [11]. Malicious traﬃc is often categorized as either

∗ Corresponding author.

E-mail address: jinfuchen@ujs.edu.cn (J. Chen).
https://doi.org/10.1016/j.jpdc.2026.105240
Received 28 December 2024; Received in revised form 26 July 2025; Accepted 9 February 2026
Available online 14 February 2026
0743-7315/© 2026 Elsevier Inc. All rights are reserved, including those for text and data mining, AI training, and similar technologies.

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

feature-based, where node attributes deviate signiﬁcantly from their
neighbors, or structural, where anomalous patterns emerge in closely
connected groups of nodes [12].
Over the years, numerous methods have been developed to address
these challenges. Early approaches primarily compared a node’s features with its neighbors or used network structure for detection [13,14].
Other techniques focused on feature subspace selection [15,16], but
these methods often relied on domain-speciﬁc knowledge and failed to
capture deep, non-linear relationships in graph data, limiting their scalability and eﬀectiveness.
The advent of Graph Neural Networks (GNNs) [17] marked a major breakthrough in graph-based malicious traﬃc detection. Early GNNbased approaches, such as Anomal-E [18], identiﬁed malicious traﬃc
by comparing restructured features and adjacency matrices. However,
these methods often failed to capture critical malicious patterns due
to their reliance on neighborhood aggregation, which can dilute essential signals [19]. Recent advancements introduced contrastive learning
paradigms [20] to graph-based malicious detection, leveraging relationships between nodes and their neighborhoods to improve representation
learning [21]. While eﬀective, these methods often neglect subgraphlevel information, which is crucial for optimizing embeddings and capturing complex dependencies in graph data [22].
To address these limitations, we propose MAGNN: Multi-Scale Adaptive Graph Neural Networks for malicious traﬃc detection. MAGNN
combines node and edge features with the graph’s topological structure in a multi-scale contrastive learning framework. The framework
introduces three innovative mechanisms-temporal-node contrast, edgelevel contrast, and multi-head hierarchical contrast-to capture diverse
dependencies and improve detection accuracy. This multi-view design
integrates various sources of malicious traﬃc information, computing
reliable malicious scores for each node while maintaining scalability
and robustness. Furthermore, MAGNN incorporates graph augmentation techniques to enhance subgraph representation learning, addressing challenges commonly encountered in practical deployment, such as
data scarcity and evolving attack patterns.
Unlike traditional supervised models, MAGNN operates in a selfsupervised manner, reducing its reliance on extensive labeled data
and making it more practical for deployment in operational network
environments where labeled traﬃc is often unavailable. By leveraging the graph-based nature of network traﬃc-where nodes represent
hosts and edges denote communication ﬂows-MAGNN captures both
node and edge features, enabling the detection of sophisticated intrusions. To address the practical challenges posed by contemporary network environments-particularly the scarcity of labeled malicious traﬃcMAGNN is designed around a self-supervised training paradigm. Instead
of relying on large labeled datasets, MAGNN learns informative representations by optimizing multi-scale contrastive objectives derived
from intrinsic graph structures and temporal dynamics. These include
temporal-node, edge-level, and hierarchical contrasts, which allow the
model to extract semantic features from unlabeled traﬃc data. During
evaluation or deployment, a small set of labeled examples can optionally be used for ﬁne-tuning or scoring, making MAGNN highly adaptable to semi-supervised scenarios. This hybrid capability ensures that
the framework remains robust, scalable, and eﬀective in modern cybersecurity operations where labeling is often limited or delayed. The
proposed MAGNN framework makes the following key contributions to
the ﬁeld of malicious network traﬃc detection:

complementary graph views. This strategy simulates realistic variations in network traﬃc, enhancing the model’s robustness and adaptability to emerging attack scenarios and diverse malicious behaviors.
3. Unlike traditional graph neural network methods, which primarily
focus on node-level features, MAGNN explicitly incorporates temporal information and edge-level attributes. This comprehensive integration addresses the limitations of node-centric approaches and
provides a holistic understanding of network ﬂow patterns, critical
for detecting sophisticated malicious traﬃc.
4. MAGNN adopts a self-supervised learning strategy that enables training without labeled data, while supporting optional semi-supervised
reﬁnement during evaluation. This design ensures robust performance on large-scale datasets, maintains computational eﬃciency,
and enhances applicability in practical cybersecurity environments
where labeled data is limited.
The rest of the paper is organized as follows. Section 2 discusses
related work in network traﬃc detection. Section 3 details the proposed model architecture and design. Section 4 presents the experimental setup and evaluation metrics. Section 5 discusses the results and comparisons with baseline methods. Finally, Section 6 concludes the paper
with future research directions.
2. Related work
The detection of malicious network traﬃc has been a crucial area
of research, with signiﬁcant advancements in leveraging graph-based
models and deep learning techniques to address increasingly sophisticated cyber threats. Early approaches, including those by Li et al. [23]
and Zola et al. [24], employed traditional graph-based methods that primarily analyzed the structural and feature-based properties of network
graphs. While these methods oﬀered initial insights into malicious behavior, their limitations in capturing complex, non-linear dependencies
and adapting to dynamic network behaviors hindered their eﬀectiveness
in evolving threat scenarios.
The emergence of GNNs has revolutionized the ﬁeld by enabling the
modeling of intricate dependencies within graph-structured data. GNNbased approaches have demonstrated signiﬁcant improvements in identifying malicious activities by leveraging both local and global graph features. For instance, Zhou et al. [25] introduced a GNN-based framework
for botnet detection that focused on the topological structure of network
traﬃc, achieving higher accuracy than traditional machine learning
methods. Similarly, Liu et al. [12] proposed a Contrastive self-supervised
Learning framework for Anomaly (CoLA), a contrastive learning-based
technique for anomaly detection in graph data, which inspired further reﬁnements like the Abnormality-Aware Graph Neural Network
(AAGNN) [25] and Host-based Intrusion Detection System (HIDS) [26].
These advancements incorporated sophisticated paradigms, including
one-class GNNs and GCN-based feature extraction, to enhance the robustness of malicious traﬃc detection.
The integration of self-supervised learning into GNN frameworks
has further expanded their capabilities, particularly in handling unlabeled data-a common challenge in real-world cybersecurity applications. Anomal-E [18], for example, utilized self-supervised methods to
generate edge embeddings and detect network intrusions, outperforming traditional feature-based models. Similarly, the adoption of graph
contrastive learning methods, as highlighted by Velickovic et al. [27],
Li et al. [28], and Hafdi et al. [29], has been instrumental in improving malicious traﬃc detection. These methods employ techniques such
as node-subgraph and edge-level contrasts to optimize node representations and identify malicious patterns more eﬀectively.
Data augmentation techniques have also been integrated into graphbased frameworks to improve generalization and robustness. Strategies such as Robust Self-Aligned (RoSA) [30] and Random Walk with
Restart (RWR) [31] create augmented graph views, simulating realistic
variations in network traﬃc. GRaph Anomaly Detection AugmenTEd

1. MAGNN introduces an innovative multi-scale contrastive learning
framework that integrates temporal-node, edge-level, and multihead hierarchical contrasts. This approach enables the model to capture diverse malicious patterns across varying levels of granularity,
signiﬁcantly enhancing its ability to detect both localized malicious
activities and broader structural deviations in network traﬃc.
2. The framework employs a graph augmentation technique that combines edge modiﬁcation and random walk with restart to generate
2

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

(GRADATE) [32] further advanced this ﬁeld by combining graph augmentation with multi-scale contrastive learning, capturing relationships
across nodes, subgraphs, and the entire graph. These methodologies enhance the detection of diverse and evolving attack patterns, showcasing
the potential of graph augmentation in malicious traﬃc detection.
Despite these advancements, many existing models rely heavily on
node-level features and overlook the importance of integrating edgelevel information and temporal dynamics, which are critical for a comprehensive understanding of network ﬂow patterns. The Net-ﬂow Edge
Graph Attention Network (NEGAT) [17], for instance, addressed this
gap by incorporating Net Flow-based features to distinguish network
attacks in real-time. However, the scalability and adaptability of such
approaches remain limited in dynamic and large-scale network environments.
Recently, the Robust Adaptive Graph Network (RAGN) [33] introduced a dynamic attention mechanism and iterative reﬁnement of graph
structures and node features, guided by feature smoothness regularization. This design allows RAGN to adapt to adversarial changes in real
time by assigning lower attention weights to unreliable edges and reﬁning node features to suppress perturbations. These mechanisms collectively enhance its robustness and accuracy in dynamic, adversarial environments. In contrast, the proposed MAGNN framework adopts a multiscale self-supervised contrastive learning strategy that captures both localized and global structural semantics within graph-structured network
traﬃc data. Instead of relying on explicit regularization, MAGNN leverages hierarchical contrastive objectives-including temporal-node, edgelevel, and subgraph-to-graph contrast-guided by multi-head attention
mechanisms to enhance the expressiveness and robustness of node representations. Furthermore, it incorporates graph augmentation techniques
to enrich subgraph learning and improve generalization under limited
data and evolving attack patterns, making it well-suited for dynamic
malicious traﬃc detection tasks across diverse real-world scenarios.
Recent eﬀorts by Zhou et al. introduced a Reconstructed Graph neural network with Global-Local Distillation (RG-GLD) [34], which focuses on building lightweight GNNs for anomaly detection by reducing
model complexity through knowledge distillation. Unlike this approach,
MAGNN emphasizes multi-scale semantic representation learning via
contrastive objectives, providing robustness across diverse attack types
while maintaining computational eﬃciency through subgraph sampling
and distributed training.
Li et al. [35] proposed Flow GAN Anomaly, an adversarial learningbased anomaly detection framework that models traﬃc ﬂow distributions to identify anomalies in network intrusion detection systems.
While eﬀective in capturing distributional shifts, such generative approaches often face limitations in interpretability and scalability. In contrast, MAGNN explicitly models structural and semantic dependencies
through multi-scale contrastive learning on graphs, enhancing both generalization and explainability.
The Flow Interaction Relationship Graph Neural Network (FIRGNN) [36] leverages ﬂow interaction relationships to detect intrusions
in consumer IoT environments using graph neural networks. Our work
diﬀers by aiming for broader generalization across multiple domains
and by integrating both temporal and edge-level contrastive mechanisms. This design enables MAGNN to identify malicious behaviors
across a wider range of traﬃc environments, beyond smart homes and
into more diverse scenarios. Building on these foundations, our proposed MAGNN framework introduces a multi-scale contrastive learning
approach that incorporates temporal-node, edge-level, and multi-head
hierarchical contrasts. By integrating node and edge features with the
graph’s topological structure, MAGNN addresses the limitations of existing methods and enables the detection of both localized and global
malicious behaviors. Furthermore, the framework leverages advanced
graph augmentation techniques, including edge modiﬁcation and RWR,
to enhance its robustness and adaptability to diverse attack scenarios.

Table 1 provides a comparative summary of key challenges in existing malicious traﬃc detection approaches and illustrates how the proposed MAGNN framework eﬀectively addresses these limitations.
3. Design of MAGAN model
3.1. Preliminaries
We deﬁne the task of malicious traﬃc detection within the framework of graph-based analysis, where the network traﬃc is represented
as an undirected graph 𝐺 = (𝑉 , 𝐸). Here, 𝑉 = {𝑣1 , 𝑣2 , … , 𝑣𝑁 } represents
the set of 𝑁 nodes, each corresponding to a network entity such as an
IP address or a device, and 𝐸 denotes the set of 𝑀 edges, representing interactions or connections between these entities, such as network
packets or communication sessions.
Each node 𝑣𝑖 ∈ 𝑉 is associated with a 𝑑-dimensional feature vector
encapsulated in the node feature matrix 𝑋 ∈ ℝ𝑁×𝑑 . These features may
include attributes such as traﬃc volume, packet statistics, or behavioral
patterns. The structural relationships among the nodes are captured by
the adjacency matrix 𝐴 ∈ ℝ𝑁×𝑁 , where 𝐴𝑖𝑗 = 1 if an edge exists between
nodes 𝑣𝑖 and 𝑣𝑗 , and 𝐴𝑖𝑗 = 0 otherwise. This adjacency matrix encodes
the graph’s topology, which reﬂects the inherent relationships within
the network traﬃc data.
The objective of malicious traﬃc detection is to learn a scoring function 𝑓 ∶ 𝑉 → ℝ that assigns a maliciousness score 𝑆𝑖 to each node 𝑣𝑖 . A
higher score 𝑆𝑖 indicates a greater likelihood that the node 𝑣𝑖 is associated with malicious activity. The scoring function 𝑓 must eﬀectively
leverage both the node-level attributes and the edge-level relationships
within the graph. Moreover, it must capture the multi-scale dependencies within the network, integrating topological information and feature
representations to identify malicious behaviors with high accuracy and
robustness. This formulation lays the foundation for graph-based malicious traﬃc detection, emphasizing the critical role of both structural
and feature-based representations in accurately modeling network trafﬁc and identifying malicious entities (Table 2).
3.2. MAGNN framework
The proposed MAGNN framework is designed to address the complexities of malicious network traﬃc analysis through a multi-stage
graph-based learning pipeline, as shown in Fig. 1. The process begins with constructing graph-structured representations from raw packet
ﬂows, where nodes encode diverse semantics such as temporal instances,
protocol types, and edge-level time dependencies. The relationships
among these nodes are captured in an adjacency matrix that preserves
the topological structure of the network traﬃc, enabling MAGNN to effectively model interaction patterns.
MAGNN operates in a self-supervised learning setting using a contrastive learning objective. To support robust representation learning,
MAGNN ﬁrst generates two augmented views of the constructed trafﬁc graph through stochastic transformations such as node dropout and
topology-aware edge perturbations guided by graph centrality. These
augmented views are passed through a shared graph encoder that computes node embeddings reﬂecting both structural and semantic similarities.
At the core of the MAGNN architecture is a multi-head hierarchical
attention mechanism, which integrates information at three levels: (i)
Node-level attention, focusing on the importance of immediate neighbors; (ii) Subgraph-level attention, capturing mid-range dependencies
within semantic clusters; and (iii) Graph-level attention, aggregating
global information across the entire graph to provide broader contextual understanding.
The representations learned at each level are passed through
contrastive modules, which compute a contrastive loss between

3

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

Table 1
Comparative summary of addressed research gaps and contributions..
Challenge/Gap in prior work

Limitation in existing studies

How MAGNN addresses it

Static or non-adaptive graph construction.

Graphs are often predeﬁned and fail to adapt to trafﬁc dynamics.
Prior methods often overlook the hierarchical nature of traﬃc features.
Models can be easily misled by crafted or noisy samples.
Models often overﬁt speciﬁc traﬃc types or sources.

MAGNN incorporates adaptive edge modiﬁcation and sampling strategies to
dynamically construct graphs from traﬃc data.
MAGNN fuses multi-scale features using hierarchical contrastive learning
modules.
MAGNN incorporates adversarial contrastive learning to improve robustness
against perturbations.
MAGNN applies generalizable graph augmentation and contrastive objectives
to improve cross-dataset performance.
MAGNN uses subgraph sampling and multi-head attention to reduce computational overhead.

Lack of multiscale feature integration.
Vulnerability to adversarial perturbations.
Limited ability to generalize across datasets.
High computational cost of full-graph GNNs.

Processing entire graphs increases latency and
memory cost.

Table 2
Comprehensive list of abbreviations used throughout the paper to enhance
clarity and understanding of technical terms..
Abbreviation

process involves both edge deletion and edge addition to maintain the
graph’s structural properties while ensuring robustness in the learned
representations.
Let 𝑃 represent the proportion of edges to modify, and 𝑀 denote the
total number of edges in the original graph. The number of edges to be
deleted and added is deﬁned as 𝑃 2𝑀 . The modiﬁed adjacency matrix 𝐴′
is constructed as follows:

Description

GNN
Graph Neural Network
MAGNN
Multi-Scale Adaptive Graph Neural Network
CoLA
Contrastive self-supervised Learning framework for Anomaly
AAGNN
Abnormality-Aware Graph Neural Network
HIDS
Host-based Intrusion Detection System
GCN
Graph Convolutional Network
GRADATE
GRaph Anomaly Detection AugmenTEd
NEGAT
Net-ﬂow Edge Graph Attention Network
RAGN
Robust Adaptive Graph Network
RG-GLD
Reconstructed Graph neural network with Global-Local Distillation
FIR-GNN
Flow Interaction Relationship Graph Neural Network
RoSA
Robust Self-Aligned
EM
Edge Modiﬁcation
RWR
Random Walk with Restart
MHHC
Multi-Head Hierarchical Contrast
MHA
Multi-Head Attention
MAE
Mean Absolute Error
MSE
Mean Squared Error
RMSE
Root Mean Squared Error
MAPE
Mean Absolute Percentage Error
VPN
Virtual Private Network
CTU-13
Czech Technical University Botnet Dataset
ISCXVPN2016 Intrusion Detection Evaluation Dataset with VPN Traﬃc (2016)
CICIDS-2017 Canadian Institute for Cybersecurity Intrusion Detection Dataset (2017)
DoHBrw-2020 DNS over HTTPS Browsing Dataset (2020)
DDP
Distributed Data Parallel (PyTorch module)
APTs
Advanced Persistent Threats

𝐴′ = 𝐴 − 𝐴delete + 𝐴add

(1)

where 𝐴delete represents the matrix with 𝑃 2𝑀 edges uniformly and randomly removed, and 𝐴add represents the matrix with 𝑃 2𝑀 edges uniformly and randomly added.
This edge modiﬁcation ensures that the second view retains critical graph properties while introducing suﬃcient variability for robust
representation learning.

3.3.2. Random walk with restart
To eﬀectively capture the local neighborhood structure around a target node, we use the RWR strategy [38] for subgraph sampling. This approach enables the selection of semantically and topologically relevant
nodes based on their proximity to the target node 𝑣𝑖 in the graph. For
a given target node 𝑣𝑖 , the RWR process deﬁnes an iterative probability
update over time steps 𝑡, governed by the following recurrence relation:
𝐩𝑡 = (1 − 𝛼)𝐴𝐩𝑡−1 + 𝛼𝐞𝑖

(2)

Here, 𝛼 ∈ [0, 1] is the restart probability, which determines the likelihood of jumping back to the starting node 𝑣𝑖 at each step. 𝐴 ∈ ℝ𝑁×𝑁
̂
denotes the row-normalized adjacency matrix, computed as 𝐴 = 𝐷−1 𝐴,
where 𝐴̂ = 𝐴 + 𝐼 includes self-loops and 𝐷 is the diagonal degree matrix. This normalization ensures that each row of 𝐴 represents a valid
transition probability distribution across neighboring nodes.
The initialization of the random walk is explicitly deﬁned by setting
𝐩0 = 𝐞𝑖 , where 𝐞𝑖 ∈ ℝ𝑁 is a one-hot vector with a value of 1 at the index
corresponding to the target node 𝑣𝑖 , and 0 elsewhere. This initialization
assigns the entire probability mass to the starting node, ensuring that
the walk originates from 𝑣𝑖 . At each subsequent step 𝑡, the probability
vector 𝐩𝑡 ∈ ℝ𝑁 is updated using the row-normalized adjacency matrix
𝐴.
The iterative updates continue until the probability vector 𝐩𝑡 converges to a stationary distribution, denoted 𝐩∞ . This distribution encodes the steady-state probabilities of visiting other nodes from 𝑣𝑖 , effectively capturing their proximity and relevance. Nodes with higher
stationary probabilities are considered more structurally and semantically related to the target and are thus included in the sampled subgraph. This proximity-aware subgraph sampling mechanism facilitates
the identiﬁcation of meaningful local contexts for contrastive learning.
Moreover, deviations in feature similarity between the target node and
its neighbors in the sampled subgraph can signal potential anomalies in
the network traﬃc.

corresponding nodes in the augmented views. This promotes invariance
to perturbations while preserving meaningful discriminative features.
The resulting embeddings are then evaluated using a malicious score
function, which estimates the likelihood of a node or ﬂow being associated with anomalous behavior.
This end-to-end pipeline-spanning graph construction, contrastive
learning, hierarchical attention, and anomaly scoring-enables MAGNN
to adapt dynamically to unseen attacks and evolving traﬃc patterns,
while maintaining computational eﬃciency through distributed training and subgraph sampling strategies.
3.3. Graph augmentation
Graph augmentation plays a vital role in the self-supervised learning
paradigm, enabling the model to extract deeper semantic information
from the graph structure. In this paper, we employ edge modiﬁcation
and a random walk with restart to create a second view of the graph and
sample subgraphs around nodes, respectively. These augmented graph
views and subgraphs are fed into the graph contrastive network.
3.3.1. Edge modiﬁcation
Edge Modiﬁcation (EM) generates the second view of the graph by
perturbing the edges in the adjacency matrix 𝐴. Inspired by [37], this
4

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

Fig. 1. Overview of the proposed MAGNN framework. (a) Network traﬃc is represented as graphs where nodes denote devices and edges represent packet ﬂows.
(b) Multi-head hierarchical contrastive module operates at the node, subgraph, and graph levels to learn robust feature representations. (c) Self-supervised learning
process optimizes the model using contrastive loss, leading to accurate malicious score predictions for network entities.

3.4. Graph contrastive network

from localized node interactions to global graph-level structures, which
is crucial for detecting both subtle and large-scale malicious activities
in network traﬃc.

The contrastive learning paradigm has proven eﬀective for graph
anomaly detection [39]. In our proposed framework, the graph contrastive network operates on multiple views of the graph and incorporates three types of contrasts: temporal-node contrast, edge-level contrast, and multi-head hierarchical contrast.

3.4.4. Multi-head attention mechanism
Before delving into the MHHC Loss, it is important to clarify the
structure of the MHA mechanism, which is central to this module. The
MHA allows the model to attend to diﬀerent parts of the input graph
simultaneously, capturing various types of interactions at diﬀerent levels of granularity. Each attention head learns an independent similarity
space, enabling the model to focus on diﬀerent types of relations between nodes and subgraphs.

3.4.1. Temporal-node contrast
Temporal-node contrast captures time-dependent anomalies by
leveraging temporal features (e.g., packet timestamps) in network trafﬁc. For a target node 𝑣𝑖 , its temporal features are compared across different time intervals. The contrastive objective is deﬁned as:
temporal-node = −

𝑁
∑
𝑖=1

(𝑡 )

(𝑡 )

log ∑

(𝑡 )

exp(sim(𝐳𝑖 1 , 𝐳𝑖 2 )∕𝜏)
(𝑡1 ) (𝑡2 )
𝑗∈ exp(sim(𝐳𝑖 , 𝐳𝑗 )∕𝜏)

(3)

Key components of MHA
• Number of attention heads (H): This refers to the number of separate attention mechanisms used in parallel. Each attention head operates independently, attending to diﬀerent features of the graph. The
number of heads 𝐻 is a hyperparameter that determines the model’s
ability to capture diverse relationships. In this design, we set 𝐻 to a
value that balances performance and computational eﬃciency.
• Query, Key, and Value matrices (Q, K, V): These matrices are used
to project the input feature space into three diﬀerent spaces: queries
(Q), keys (K), and values (V). For each attention head, the matrices 𝑄(ℎ) , 𝐾 (ℎ) , 𝑉 (ℎ) are linearly projected from the subgraph or node
embeddings using learnable parameter matrices 𝑊𝑄(ℎ) , 𝑊𝐾(ℎ) , 𝑊𝑉(ℎ) ∈

(𝑡 )

where 𝐳𝑖 1 and 𝐳𝑖 2 are the embeddings of node 𝑣𝑖 at time intervals 𝑡1
and 𝑡2 , sim(⋅, ⋅) denotes a similarity function (e.g., cosine similarity), 𝜏
is the temperature parameter, and  is the set of negative samples.
3.4.2. Edge-level contrast
Edge-level contrast focuses on detecting anomalies at the packet
level by comparing edge embeddings across diﬀerent views. For an edge
𝑒𝑖𝑗 between nodes 𝑣𝑖 and 𝑣𝑗 , the contrastive loss is deﬁned as:
edge-level = −

∑
𝑒𝑖𝑗 ∈𝐸

log ∑

exp(sim(𝐳𝑒(1)
, 𝐳𝑒(2)
)∕𝜏)
𝑖𝑗
𝑖𝑗

(1) (2)
𝑒𝑘𝑙 ∈𝐸 exp(sim(𝐳𝑒𝑖𝑗 , 𝐳𝑒𝑘𝑙 )∕𝜏)

(4)

′

𝑑
ℝ𝑑×𝑑 , where 𝑑 is the input feature dimension and 𝑑 ′ = 𝐻
is the dimensionality per head.
• Scaled dot-product attention: The attention scores are computed
by measuring the similarity between the query and key vectors using
the scaled dot-product attention mechanism. This allows each attention head to weigh the importance of diﬀerent elements in the graph
for a given query:
(
)
𝑄(ℎ) (𝐾 (ℎ) )𝑇
Attention(𝑄(ℎ) , 𝐾 (ℎ) , 𝑉 (ℎ) ) = softmax
𝑉 (ℎ)
(5)
√
𝑑′

where 𝐳𝑒(1)
and 𝐳𝑒(2)
are edge embeddings in the two graph views, and 𝐸
𝑖𝑗
𝑖𝑗
is the set of negative edge samples.
3.4.3. Multi-head hierarchical contrast
The Multi-Head Hierarchical Contrast (MHHC) module is designed
to capture multi-scale structural dependencies by applying a Multi-Head
Attention (MHA) mechanism across hierarchical levels of the graphnamely, nodes, subgraphs, and the entire graph [40]. This design allows the model to simultaneously focus on diverse relational patterns,
5

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

Fig. 2. MAGNN integrates temporal node, edge-level, and multi-head hierarchical attention modules, captures dependencies at nodes, subgraph, and global levels
using multiple attention heads.

√
where 𝑑 ′ is a scaling factor to stabilize the gradients during training.
• Concatenation of outputs: After the attention mechanism is applied
in each head, the results from all heads are concatenated to form a
uniﬁed representation:
𝐳𝑆𝑖 = Concat(𝐳𝑆(1) , … , 𝐳𝑆(𝐻) )𝑊𝑂
𝑖

𝑖

the model to capture both static and dynamic characteristics of network
traﬃc. The total training loss is deﬁned as:
total = 𝜆1 ⋅ contrastive + 𝜆2 ⋅ regression

Here, contrastive is the integrated loss from Eq. 8, and regression is computed using MAE, MSE, RMSE, and MAPE between predicted and actual
traﬃc feature values. 𝜆1 and 𝜆2 are task-level weighting coeﬃcients used
to balance the classiﬁcation and regression objectives.
This multi-task loss enables MAGNN to learn temporally aware and
semantically rich representations, improving its robustness in detecting
evolving or stealthy attack patterns.
Attributed graph 𝐺 = (𝑉 , 𝐸, 𝑋), where: 𝑉 is the set of nodes, 𝐸 is
the set of edges, 𝑋 ∈ ℝ|𝑉 |×𝑑 is the node feature matrix, where each row
𝐱𝑣 ∈ ℝ𝑑 represents a 𝑑-dimensional feature vector for node 𝑣 ∈ 𝑉 .

(6)

where 𝑊𝑂 ∈ ℝ𝑑×𝑑 is a learnable output projection matrix that combines the concatenated outputs into the ﬁnal subgraph representation.
3.4.5. Multi-head hierarchical contrast loss
The MHHC loss utilizes the multi-head attention mechanism described above to impose a contrastive learning objective across multiple
hierarchical levels of the graph. The attention-based hierarchical contrastive loss is deﬁned as:
(
)
𝑁
exp sim(𝐳𝑆𝑖 , 𝐳𝐺 )∕𝜏
∑
MHHC = −
log ∑
(7)
(
)
𝑖=1
𝑗∈𝑆 exp sim(𝐳𝑆𝑖 , 𝐳𝑆𝑗 )∕𝜏

3.5. Optimization and complexity analysis
The proposed MAGNN framework is end-to-end trainable using backpropagation and gradient descent. During training, the model simultaneously minimizes the classiﬁcation-driven contrastive loss and the auxiliary regression loss using the multi-task formulation in Eq. 9.
In terms of computational complexity, the time complexity of
MAGNN is dominated by graph propagation and embedding transformation steps. As shown in Section 3.5.1, the model scales linearly with
the number of nodes and edges, making it suitable for large-scale network traﬃc datasets.
By leveraging multi-scale contrastive learning objectives, our model
can be eﬃciently optimized using gradient descent. The optimization
process integrates the three contrastive losses- temporal-node contrast,
edge-level contrast, and hierarchical contrast -into a single uniﬁed loss
function as shown in Eq. 8.

where: 𝐳𝐺 is the embedding of the entire graph, 𝑆 is the set of negative
subgraph samples, sim(⋅, ⋅) denotes the cosine similarity between embeddings, 𝜏 is a temperature scaling parameter that controls the sharpness
of the probability distribution.
This loss encourages the model to bring similar subgraphs (positive
samples) closer together in the embedding space while pushing dissimilar subgraphs (negative samples) apart, leading to improved generalization across hierarchical levels. The multi-head design in the MHA
mechanism improves the model’s capacity to generalize across varying
structural contexts, enabling robust detection of both local anomalies
and global threats in dynamic traﬃc graphs.

3.5.1. Time complexity
The time complexity of the MAGNN framework is primarily inﬂuenced by two key operations: (i) neighborhood aggregation through
graph neural network layers, and (ii) feature transformation via contrastive projection heads [41]. For a graph with 𝑁 = |𝑉 | nodes and
𝑀 = |𝐸| edges, and assuming 𝑓𝑖 is the dimensionality of the 𝑖-th layer
and 𝐿 is the total number of layers.
∑
The ﬁrst term, 𝑀 𝐿
𝑖=0 𝑓𝑖 , corresponds to the cost of message passing
and attention computation across edges for each GNN layer. At each
layer, messages (or neighbor features) are aggregated per edge, scaled
by the dimensionality of the current layer’s features.
(
)
𝐿
𝐿
∑
∑
 𝑀
𝑓𝑖 + 𝑁
𝑓𝑖−1 𝑓𝑖
(10)

3.4.6. Integrated contrastive loss
The MAGNN framework combines three contrastive objectives to
guide representation learning at diﬀerent levels of graph structure:
contrastive = 𝛼1 temporal-node + 𝛼2 edge-level + 𝛼3 MHHC

(9)

(8)

where 𝛼1 , 𝛼2 , and 𝛼3 are hyperparameters that balance the contribution
of each contrastive component. This integrated contrastive loss constitutes the classiﬁcation-driven objective in the MAGNN framework.
3.4.7. Multi-task loss function
MAGNN is formulated as a multi-task learning framework that simultaneously performs malicious traﬃc detection (classiﬁcation) and
temporal traﬃc prediction (regression). This joint optimization helps

𝑖=0

6

𝑖=1

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

∑
The second term, 𝑁 𝐿
𝑖=1 𝑓𝑖−1 𝑓𝑖 , represents the cost of feature transformation at each node, where node features are projected from 𝑓𝑖−1 to
𝑓𝑖 dimensions using learned linear transformations. Together, these two
terms capture the computational load of the entire model during training. Importantly, this formulation conﬁrms that the time complexity is
linear with respect to the number of nodes and edges ((𝑁 + 𝑀) when
𝑓𝑖 is bounded), thus ensuring the MAGNN framework is scalable and
eﬃcient for processing large-scale network traﬃc graphs.

2. The ISCXVPN2016 [43] dataset, also developed by the Canadian Institute for Cybersecurity, focuses on Virtual Private Network (VPN)
traﬃc analysis. This dataset simulates realistic network traﬃc patterns, including both encrypted (VPN) and unencrypted traﬃc. It
includes a variety of application types such as web browsing, Email,
ﬁle transfer, and multimedia streaming, with malicious activities interspersed. The dataset is particularly valuable for evaluating the
eﬀectiveness of intrusion detection systems in handling encrypted
traﬃc, which poses unique challenges for cybersecurity research.
3. The CICIDS-2017 [44] dataset, developed by the Canadian Institute
for Cybersecurity, provides a comprehensive benchmark for intrusion detection systems. It includes network traﬃc data from both
benign activities and a wide range of modern attack scenarios. This
dataset simulates realistic day-to-day network traﬃc alongside malicious behavior, oﬀering detailed features and diverse attack patterns.
Its realism and scope make it an invaluable resource for evaluating
the performance of malicious traﬃc detection models.
4. The CIRA-CIC-DoHBrw-2020 [45] dataset, created by the Canadian
Institute for Cybersecurity, focuses on the detection of malicious trafﬁc using DNS over HTTPS (DoH) communication. The dataset includes a variety of benign and malicious web traﬃc scenarios, representing a wide range of real-world browsing activities. Its detailed
feature set captures the unique characteristics of encrypted DoH trafﬁc, enabling researchers to evaluate the eﬀectiveness of detection
methods in handling this emerging and challenging network communication protocol.

Algorithm 1 Proposed model: MAGNN framework.
Require: Attributed graph 𝐺 = (𝑉 , 𝐸, 𝑋), where 𝑉 is the set of nodes, 𝐸
is the set of edges, and 𝑋 ∈ ℝ|𝑉 |×𝑑 is the node feature matrix, where
each row 𝐱𝑣 ∈ ℝ𝑑 represents a 𝑑-dimensional feature vector for node
𝑣 ∈ 𝑉 ; number of training epochs 𝑇 , batch size 𝐵, augmentation
parameter 𝑃 , restart probability 𝛼.
Ensure: Malicious score function 𝑓 (𝑣) for each node 𝑣 ∈ 𝑉 .
1: Initialization: Randomly initialize the parameters of the MAGNN
framework.
2: for 𝑡 = 1 to 𝑇 do
3:
Generate two graph views by randomly deleting and adding 𝑃 ⋅
|𝐸| edges to simulate structural perturbation.
4:
Sample subgraphs for each node 𝑣 ∈ 𝑉 using random walk with
restart with restart probability 𝛼.
5:
Compute node embeddings 𝐳𝑣 using a multi-layer GNN with
multi-head attention.
6:
Compute edge embeddings 𝐳𝑒 via concatenation and multi-layer
perceptron on node pairs.
7:
Compute subgraph embeddings 𝐳𝑆 using hierarchical attention
pooling.
8:
Compute the temporal-node contrast loss temporal-node by comparing node embeddings across diﬀerent time intervals.
9:
Compute the edge-level contrast loss edge-level by comparing
edge embeddings across augmented graph views.
10:
Compute the multi-head hierarchical contrast loss MHHC using
Eq. 7, capturing relationships between subgraph and global graph
embeddings.
11:
Combine all contrastive losses into the integrated loss function
using Eq. 8.
12:
Perform backpropagation and update the model parameters using gradient descent.
13: end for
14: Compute the malicious score 𝑓 (𝑣) ∈ [0, 1] for each node 𝑣 ∈ 𝑉 based
on the learned embeddings and aggregated contrastive objectives.
15: Return Malicious score function 𝑓 (𝑣) for all nodes 𝑣 ∈ 𝑉 .

4.2. Evaluation metrics

4. Experimental setup

F1-Score = 2 ⋅

To comprehensively evaluate the performance of MAGNN, we employ both classiﬁcation and error-based metrics.
Classiﬁcation metrics: We use accuracy, precision, recall, and f1score to assess the model’s ability to correctly identify malicious and benign traﬃc. These metrics are computed using predicted class labels and
are standard for evaluating binary and multiclass classiﬁcation tasks.
Precision and Recall are particularly important in cybersecurity contexts
where minimizing false positives and false negatives is critical.
Accuracy =

TP + TN
TP + TN + FP + FN

(11)

Precision =

TP
TP + FP

(12)

Recall =

TP
TP + FN
Precision ⋅ Recall
Precision + Recall

(13)

(14)

Error-based metrics: In addition to classiﬁcation metrics, we report
error-based metrics-Mean Absolute Error (MAE), Mean Squared Error
(MSE), Root Mean Squared Error (RMSE), and Mean Absolute Percentage Error (MAPE)-to assess the model’s prediction conﬁdence and misclassiﬁcation cost. These metrics are calculated on the model’s predicted
probability scores (i.e., soft outputs from the ﬁnal layer before thresholding). Their inclusion provides insight into how well the model’s probabilistic outputs align with ground truth labels and helps quantify uncertainty or deviation from expected classiﬁcation behavior.
Let 𝑦𝑖 ∈ {0, 1} denote the true label and 𝑦̂𝑖 ∈ [0, 1] denote the predicted probability for the 𝑖-th sample, with 𝑛 total samples. The formulas
for the error metrics are as follows:

4.1. Datasets description
We used four benchmark datasets to evaluate the eﬀectiveness of the
proposed MAGNN framework for malicious network traﬃc detection.
These datasets represent diverse network traﬃc scenarios, attack types,
and real-world network conditions.
1. The CTU-13 [42] dataset is a well-known benchmark dataset for botnet traﬃc analysis, developed by the Czech Technical University
(CTU). It contains network traﬃc traces of both normal and malicious botnet activities across 13 distinct scenarios. The dataset includes a mix of real botnet infections, background traﬃc, and benign user activities, making it a valuable resource for evaluating the
performance of intrusion detection and network anomaly detection
systems. Its detailed annotations and realistic traﬃc patterns have
made it a popular choice for research in cybersecurity and botnet
detection.

•

MAE measures the average absolute diﬀerence between predicted
probabilities and actual binary labels.
1∑
|𝑦 − 𝑦̂𝑖 |
𝑛 𝑖=1 𝑖
𝑛

MAE =
7

(15)

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.
•

MSE penalizes larger errors more heavily, reﬂecting overall prediction deviation.
1∑
(𝑦 − 𝑦̂𝑖 )2
𝑛 𝑖=1 𝑖

objective by encouraging the model to learn generalized and robust features. MAGNN was trained end-to-end using backpropagation with an
integrated loss function that combined temporal-node, edge-level, and
hierarchical contrastive components. The weighting coeﬃcients 𝜆1 , 𝜆2 ,
and 𝜆3 were tuned empirically to balance the contributions of each contrastive mechanism. The overall setup ensured eﬃcient scalability and
robust performance across multiple datasets and traﬃc scenarios.

𝑛

MSE =
•

(16)

RMSE provides a more interpretable error scale by taking the square
root of MSE.
√
√ 𝑛
√
√1 ∑
RMSE = MSE = √
(𝑦 − 𝑦̂𝑖 )2
(17)
𝑛 𝑖=1 𝑖

4.4. Baseline methods
•

•

Anomal-E [18] employs a self-supervised approach to leverage edge
features and graph topology for network intrusion detection. It generates edge embeddings without relying on labeled data, which can
then be used with traditional malicious detection algorithms, such
as isolation forests.
• NEGAT [17]: is used of NetFlow-based network traﬃc ﬂows. The
model integrates network ﬂow insights into node representations,
enhancing graph representation with self-supervision. It is designed
to distinguish network attacks from hackers in real-time by monitoring network traﬃc ﬂows across routers and identifying speciﬁc types
of ﬂows.
• E-GraphSAGE [46] leverages GNNs to detect and mitigate network
traﬃc-based cyberattacks. By incorporating both edge features and
topological information, it eﬀectively models network traﬃc in a
graph representation to identify malicious activities.
• TCGNN [47] is designed for packet-grained network traﬃc classiﬁcation using GNNs. It transforms each network packet into an undirected graph and employs a two-layer graph convolutional network
with three distinct aggregation strategies to enhance classiﬁcation
accuracy and performance.
• DE-GNN [48]: A graph-based structure that learns packet-level representations directly from raw bytes. It constructs network ﬂows
as a Traﬃc Interaction Graph, integrating behavioral patterns and
packet-level features. It utilizes GNNs to extract ﬂow-level features,
providing a comprehensive view of network interactions.

MAPE expresses the error as a percentage, oﬀering an intuitive sense
of prediction quality relative to actual values.
1 ∑ || 𝑦𝑖 − 𝑦̂𝑖 ||
𝑛 𝑖=1 || 𝑦𝑖 + 𝜖 ||
𝑛

MAPE =

(18)

where 𝜖 is a small constant added to avoid division by zero.
These error-based metrics complement traditional classiﬁcation metrics by oﬀering a ﬁner-grained view of model calibration and misclassiﬁcation impact, especially important in real-time applications where
false conﬁdence can be costly.
4.3. Implementation details
4.3.1. Experimental platform and software
All experiments were conducted on a Linux-based high-performance
workstation equipped with an NVIDIA RTX 3090 GPU (24 GB VRAM),
64 GB of RAM, and an AMD Ryzen 9 5950X CPU, running Ubuntu 22.04.
The implementation was carried out using Python 3.9. We employed
PyTorch 2.0 and PyTorch Geometric 2.3.1 as the primary frameworks
for deep learning and graph-based processing. Data preprocessing and
manipulation were performed using NumPy (v1.24) and Pandas (v1.5).
This setup was chosen to ensure reproducibility, scalability, and compatibility with GPU-accelerated computation.
4.3.2. Model architecture and training setup
The MAGNN framework was developed using these open-source libraries to facilitate eﬃcient deep learning computations and scalable
graph processing. PyTorch Geometric was selected due to its robust support for graph operations and seamless integration with PyTorch. This
enabled eﬃcient implementation of the model’s components, including
the graph attention mechanisms, multi-scale contrastive learning modules, and hierarchical aggregation strategies. MAGNN learns network
traﬃc representations through a combination of temporal-node, edgelevel, and hierarchical contrastive learning objectives. Temporal dependencies were modeled using a graph attention mechanism with four attention heads and a hidden dimension size of 128, capturing sequential
patterns while maintaining computational eﬃciency. The hierarchical
structure was built using three graph convolutional layers, each processing up to two-hop neighborhoods to capture both local and global
dependencies.

5. Experimental results
5.1. Comparative performance evaluation against baseline methods on
multiple datasets
The performance of the proposed MAGNN model is evaluated against
several baseline methods across four benchmark datasets: CTU-13, ISCXVPN2016, CICIDS-2017, and CIRA-CIC-DoHBrw-2020. Fig. 3 illustrates the accuracy comparison of MAGNN with Anomal-E, NEGAT, EGraphSAGE, TCGNN, and DE-GNN under varying convergence steps.
The results demonstrate that MAGNN consistently outperforms all baseline models across the datasets. For instance, on the CTU-13 dataset,
MAGNN achieves an accuracy of approximately 97.80% at 100 convergence steps, surpassing all competitors. On the ISCXVPN2016 dataset,
it attains 98.60% accuracy, showing steady improvement throughout
convergence and strong generalization capabilities. On the CICIDS-2017
dataset, MAGNN achieves an accuracy close to 99.13%, outperforming
baseline models. Similarly, on the CIRA-CIC-DoHBrw-2020 dataset, the
model reaches a peak accuracy of 99.30%, conﬁrming its robustness and
adaptability to diverse traﬃc patterns.
Fig. 4 shows the F1-score performance of MAGNN compared to the
baselines under varying convergence steps. On the CTU-13 dataset,
MAGNN achieves the highest F1-score of 98.94% at 100 steps, signiﬁcantly outperforming models such as TCGNN and DE-GNN. On ISCXVPN2016, it steadily improves to reach an F1-score of 99.36%,
eﬀectively addressing encrypted traﬃc challenges. For CICIDS-2017,
MAGNN records an F1-score of approximately 98.97%, demonstrating
its capacity to detect complex and diverse attack patterns. On CIRA-CICDoHBrw-2020, it achieves a peak F1-score of 99.10%, highlighting its
adaptability to evolving network anomalies and malicious behaviors.

4.3.3. Training conﬁguration and hyperparameters
To optimize model performance, hyperparameter tuning was conducted. The learning rate was set to 0.001 with a scheduler that decayed it by a factor of 0.1 after ten epochs without validation loss
improvement. The Adam optimizer was used with a weight decay of
0.00001 to mitigate overﬁtting. A batch size of 64 was selected to balance memory and training eﬃciency. Training was performed over 100
epochs, with early stopping based on validation performance. Dirichlet neighbor sampling (size = 30) was adopted to ensure robustness
in sparse environments and to reduce sensitivity to noise. Graph augmentation was applied through edge modiﬁcation by randomly adding
or deleting edges to generate diverse graph views for contrastive learning. This technique complemented the multi-scale contrastive learning
8

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

Fig. 3. Accuracy of diﬀerent methods under varying convergence steps.

Fig. 4. F1 score of diﬀerent methods under varying convergence steps.

These results validate the superiority of the MAGNN framework over
existing methods. MAGNN consistently achieves higher accuracy and
F1-scores across all datasets and convergence steps, reﬂecting faster convergence, improved classiﬁcation performance, and strong generalization to varying traﬃc conditions. The consistent improvements further
conﬁrm its robustness and scalability. By integrating multi-scale adaptive graph learning and contrastive mechanisms, MAGNN oﬀers a powerful and eﬃcient solution for malicious network traﬃc detection.
Table 3 summarizes the performance of MAGNN compared to ﬁve
baseline models across four benchmark datasets. On the CTU-13 dataset,
MAGNN achieves the highest accuracy (98.45%), precision (97.88%),
recall (97.30%), and F1-score (97.58%), along with the lowest error
metrics (MSE: 0.06, RMSE: 0.20, MAE: 0.31, MAPE: 1.08). DE-GNN
ranks second with an F1-score of 96.06%. For ISCXVPN2016, MAGNN
maintains superior performance (Acc: 98.10%, F1: 97.12%) and low errors (MSE: 0.07, RMSE: 0.22). While TCGNN performs well, it falls short
in classiﬁcation accuracy and error reduction. On CICIDS-2017, MAGNN
reaches an F1-score of 97.45% and again records the lowest error values.
DE-GNN and TCGNN follow, but with weaker generalization. On the
DoHBrw-2020 dataset, MAGNN attains the best results across all metrics
(Acc: 99.20%, F1: 98.35%, MSE: 0.05), showcasing strong adaptability to complex traﬃc. E-GraphSAGE and DE-GNN are competitive but
still lag behind. Overall, MAGNN consistently outperforms all baselines
in both classiﬁcation accuracy and error minimization. Its multi-scale
adaptive graph learning and contrastive mechanisms enable robust generalization across diverse and evolving network traﬃc scenarios.

In contrast, MAGNN combines edge modiﬁcation, subgraph sampling, and contrastive learning at multiple levels (node, edge, and hierarchy), enabling it to learn more robust and generalizable representations of network traﬃc. These design elements collectively contribute
to MAGNN’s superior detection capabilities, especially in scenarios involving sparse or imbalanced traﬃc.
5.2. Network traﬃc prediction and analysis of prediction accuracy
Fig. 5 illustrates the MAE performance of all models across varying temporal steps on the four benchmark datasets. As expected, MAE
values increase with longer prediction horizons, reﬂecting the growing
diﬃculty of modeling long-term patterns. Nevertheless, the proposed
MAGNN consistently achieves the lowest MAE across all datasets. On the
CTU-13 dataset, MAGNN exhibits minimal error growth, consistently
outperforming Anomal-E and NEGAT. Similarly, on ISCXVPN2016,
MAGNN demonstrates signiﬁcantly lower MAE values than TCGNN
and DE-GNN. For CICIDS-2017, MAGNN maintains clear superiority
over all baselines, particularly NEGAT and E-GraphSAGE. On CIRA-CICDoHBrw-2020, MAGNN sustains robust performance, achieving the lowest MAE throughout, indicating strong generalization to complex traﬃc
patterns.
Fig. 6 presents MAPE values across increasing prediction steps. As a
relative error metric, MAPE highlights prediction reliability. MAGNN
consistently yields lower MAPE values across all datasets. On CTU13, it maintains minimal error growth compared to E-GraphSAGE and
Anomal-E. For ISCXVPN2016, MAGNN achieves the lowest MAPE at
longer horizons, outperforming NEGAT and TCGNN. In the CICIDS2017 scenario, MAGNN generalizes eﬀectively, signiﬁcantly reducing
MAPE relative to DE-GNN and other baselines. Similarly, for CIRA-CICDoHBrw-2020, MAGNN sustains low and stable MAPE growth, reinforcing its resilience to evolving traﬃc patterns.
Fig. 7 displays MSE trends as temporal steps increase. As a squared
error metric, MSE is particularly sensitive to larger deviations. MAGNN
achieves the lowest MSE across all datasets. On CTU-13, it surpasses
NEGAT, TCGNN, and E-GraphSAGE. On ISCXVPN2016, it consistently
outperforms DE-GNN and TCGNN by a clear margin. For CICIDS-2017,
MAGNN again records the lowest MSE, validating its accuracy and
stability. On CIRA-CIC-DoHBrw-2020, it demonstrates outstanding error minimization, maintaining the best performance at all prediction
horizons.

5.1.1. Analysis of model design relative to prior work
To contextualize the performance of the proposed MAGNN framework, we conducted a comprehensive comparison with several stateof-the-art models. As presented in Tables 3 to 5, MAGNN consistently
outperforms all baseline methods across multiple datasets and a range of
evaluation metrics, including error-based performance measures. Compared to models like Anomal-E and NEGAT, MAGNN’s superior performance can be attributed to its multi-scale hierarchical design, which
captures both local and global topological patterns. While E-GraphSAGE
integrates edge features, it lacks hierarchical contrastive objectives, limiting its robustness to structural perturbations. DE-GNN and TCGNN attempt to capture deeper graph semantics, but they do not integrate explicit augmentation strategies, making them more sensitive to noisy or
incomplete data.
9

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

Table 3
Comparative performance of MAGNN and baseline methods on benchmark datasets..
Dataset

Model

Acc.

Pre.

Rec.

F1

MSE

RMSE

MAE

MAPE

CTU-13

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

91.23
93.75
95.10
96.45
97.12
98.45

90.45
92.90
94.62
95.82
96.34
97.88

89.80
91.87
93.85
94.93
95.78
97.30

90.12
92.38
94.23
95.37
96.06
97.58

0.15
0.12
0.10
0.09
0.08
0.06

0.35
0.31
0.28
0.26
0.24
0.20

0.79
0.72
0.58
0.50
0.42
0.31

1.45
1.38
1.28
1.22
1.15
1.08

ISCXVPN2016

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

90.90
92.80
94.50
95.80
96.50
98.10

89.87
91.45
93.60
94.75
95.80
97.45

88.65
90.85
92.90
94.05
95.10
96.80

89.25
91.15
93.25
94.40
95.45
97.12

0.16
0.13
0.11
0.10
0.09
0.07

0.38
0.34
0.30
0.27
0.25
0.22

0.81
0.75
0.61
0.54
0.45
0.33

1.50
1.40
1.30
1.22
1.17
1.10

CICIDS-2017

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

92.35
94.25
95.65
96.90
97.55
98.65

91.50
93.50
94.80
96.00
96.85
98.00

90.90
92.80
94.15
95.30
96.10
97.40

91.20
93.15
94.45
95.65
96.45
97.70

0.14
0.11
0.10
0.09
0.08
0.06

0.32
0.29
0.26
0.24
0.23
0.19

0.77
0.68
0.55
0.48
0.39
0.29

1.42
1.32
1.25
1.20
1.13
1.05

DoHBrw-2020

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

93.10
95.00
96.20
97.35
98.00
99.20

92.20
94.10
95.50
96.55
97.25
98.60

91.60
93.50
94.80
95.95
96.70
98.10

91.90
93.80
95.15
96.25
97.00
98.35

0.13
0.10
0.09
0.08
0.07
0.05

0.31
0.28
0.25
0.24
0.22
0.18

0.74
0.66
0.51
0.43
0.38
0.27

1.38
1.28
1.20
1.15
1.10
1.02

Fig. 5. MAE of diﬀerent methods under varying prediction temporal steps.

5.3. Analysis of computational eﬃciency across temporal snapshot sizes

Fig. 8 depicts RMSE values for MAGNN and the baseline models.
As the square root of MSE, RMSE reﬂects the magnitude of overall
prediction error. MAGNN again achieves the lowest RMSE across all
datasets. On CTU-13, it demonstrates reduced RMSE growth, outperforming Anomal-E, NEGAT, and E-GraphSAGE. For ISCXVPN2016 and
CICIDS-2017, MAGNN maintains clear advantages over all baselines,
particularly under longer prediction horizons. On CIRA-CIC-DoHBrw2020, it consistently achieves the lowest RMSE, highlighting its robustness and precision.
These results demonstrate that MAGNN signiﬁcantly outperforms all
baseline methods across MAE, MAPE, MSE, and RMSE metrics. Its superior performance is attributed to its multi-scale adaptive graph learning
and contrastive mechanisms, which enable eﬀective modeling of both
local and global dependencies. The consistent improvements across increasing prediction horizons further underscore MAGNN’s robustness,
scalability, and eﬀectiveness in accurately detecting malicious network
traﬃc.
Table 4 presents the experimental results of the proposed MAGNN
framework compared to baseline models, with all results reported to
four decimal places. It can be observed that the proposed MAGNN
achieves the smallest values for RMSE, MAE, MSE, and MAPE across
all four datasets. These lower error values indicate that the predictions
made by the MAGNN model are closer to the actual network traﬃc
values, demonstrating its superior accuracy and reliability. The results
show that the MAGNN framework is more eﬀective and competitive for
malicious network traﬃc detection tasks compared to other baseline
models.

The computational eﬃciency of the proposed MAGNN model and
baseline methods is evaluated by measuring the training duration per
epoch across four benchmark datasets. Fig. 9 presents the time required
for a single training epoch at varying temporal sizes (300s, 600s, and
900s). As expected, computational cost increases with longer snapshot
durations due to greater data volume and complexity.
For the CTU-13 dataset (Fig. 9(a)), MAGNN demonstrates competitive training eﬃciency. While DE-GNN and TCGNN experience a noticeable increase in training time at 900s, MAGNN maintains a relatively low training duration, highlighting its eﬃciency. Similarly, for
ISCXVPN2016 (Fig. 9(b)), MAGNN strikes an eﬀective balance between
performance and training time. Although NEGAT and E-GraphSAGE
show slightly lower durations at 300s and 600s, MAGNN scales more
eﬃciently at 900s, outperforming others in both speed and accuracy.
On the CICIDS-2017 dataset (Fig. 9(c)), MAGNN consistently exhibits
lower training times than DE-GNN and TCGNN, whose durations increase sharply with larger temporal sizes. This illustrates the architectural eﬃciency of MAGNN in handling more complex, time-extensive
data. For the CIRA-CIC-DoHBrw-2020 dataset (Fig. 9(d)), MAGNN again
achieves superior scalability, maintaining the lowest training time at
900s among all compared models.
The observed trends conﬁrm that MAGNN oﬀers both fast convergence and reduced computational cost while sustaining high predictive
performance. In contrast, baseline models such as DE-GNN and TCGNN
incur substantial overhead at larger temporal sizes. The eﬃciency of
10

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

Table 4
Error-based performance comparison of MAGNN and baseline models across four benchmark
datasets.
Data sets

Model

RMSE

MAE

MSE

MAPE

CTU-13

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

78.1240
75.8967
74.5893
73.2384
72.1032
69.8452

61.2413
58.7856
57.6842
56.5423
54.9140
51.7631

6103.2354
5769.4301
5567.8902
5362.9284
5198.1235
4879.1320

11.1023
10.4321
10.0516
9.7562
9.4213
8.9456

ISCXVPN2016

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

65.2481
63.5674
61.9843
60.4821
59.2340
56.7123

50.9243
48.8562
47.2314
45.9852
44.8230
42.3412

4256.9341
4057.8924
3849.4351
3695.1423
3567.1243
3218.5342

9.4212
8.7623
8.2345
7.9421
7.6512
7.1435

CICIDS-2017

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

70.7841
68.4921
66.9812
65.4320
63.8924
61.0234

55.2384
52.8342
50.8921
49.2356
47.9841
45.2312

5012.9843
4789.1234
4489.3214
4287.2134
4056.8942
3735.1284

10.3412
9.8745
9.5643
9.2342
8.9245
8.3456

CIRA-CIC-DoHBrw-2020

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

82.3412
79.8642
77.2845
75.7642
74.1231
71.4532

66.2314
63.8941
61.3212
59.8324
58.4210
55.2341

6194.9834
5982.3412
5723.4501
5498.3214
5287.8912
4987.4512

11.5243
10.8723
10.5412
10.1123
9.8456
9.3412

Fig. 6. MAPE of diﬀerent methods under diﬀerent prediction temporal steps.

Fig. 7. MSE of diﬀerent methods under diﬀerent prediction temporal steps.

Fig. 8. RMSE of diﬀerent methods under diﬀerent prediction temporal steps.
11

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

Fig. 9. Duration of a single training epoch when using the diﬀerent dataset.

MAGNN’s design ensures computational viability, making it suitable for
deployment in dynamic and large-scale network environments.

Table 5
Training and inference time per epoch (in seconds) of MAGNN compared to
baseline models across four benchmark datasets.

5.4. Computation time analysis

Dataset

Method

Training (s/epoch)

Inference (s/epoch)

CTU-13

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

35.2
32.8
30.1
28.4
26.7
18.5

3.5
3.2
2.9
2.6
2.3
1.4

ISCXVPN2016

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

40.1
37.5
35.2
32.8
30.6
21.4

4.1
3.8
3.5
3.2
3.0
1.6

CICIDS-2017

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

45.7
42.3
39.8
37.2
35.4
24.5

4.8
4.5
4.2
3.8
3.6
1.9

CIRA-CIC-DoHBrw-2020

Anomal-E
NEGAT
E-GraphSAGE
TCGNN
DE-GNN
MAGNN

50.8
48.3
44.6
42.1
40.4
28.7

5.2
4.9
4.5
4.2
4.0
2.4

In this section, we analyze the computational time overhead of the
proposed MAGNN framework compared to the state-of-the-art models.
It can be seen from Table 5 that the proposed MAGNN model consistently achieves the lowest training and inference times compared to
the baseline models across all datasets. Speciﬁcally, the training time
for MAGNN is signiﬁcantly reduced, demonstrating its computational
eﬃciency in handling malicious network traﬃc detection tasks. For instance, on the CTU-13 dataset, MAGNN achieves a training time of 18.5s
per epoch, while the closest competing model, DE-GNN, requires 26.7s
per epoch. Similarly, the inference time for MAGNN on the same dataset
is 1.4s per epoch, which is notably faster than all baseline models.
The superior computational eﬃciency of MAGNN can be attributed
to the following reasons:
•

The multi-scale adaptive architecture of MAGNN eﬃciently processes both node-level and edge-level information while reducing
redundant computations.
• The integrated contrastive learning mechanism is optimized to minimize the computational overhead during both training and inference.
• MAGNN avoids complex recursive operations and computational
bottlenecks often encountered in models like TCGNN and DE-GNN.

Fig. 10 provides a conceptual and performance comparison of
the three paradigms across four widely used datasets: CTU-13, ISCXVPN2016, CICIDS-2017, and CIRA-CIC-DoHBrw-2020. The results
clearly show that our host-centric paradigm consistently outperforms
the other two across all datasets and evaluation metrics. For instance,
on CIRA-CIC-DoHBrw-2020, the host-centric approach achieves an accuracy of 98.91%, compared to 94.61% for the ﬂow-centric model and
90.70% for the feature-centric model. Similar trends are observed across
the remaining datasets, with an average improvement of 4-8% in each
metric.
These ﬁndings validate our design choice to represent devices as
nodes and model the communication ﬂow between them. This structure preserves both topological and temporal context, enabling more
robust multi-scale behavioral pattern learning. In contrast, while the
ﬂow-centric approach captures localized ﬂow relationships, it lacks
broader structural awareness. The feature-centric paradigm, although
lightweight, struggles to encode sequential dependencies or hierarchical semantics, especially in encrypted or high-volume traﬃc scenarios.

While models such as E-GraphSAGE and TCGNN perform well in
terms of training eﬃciency, their inference times remain higher compared to MAGNN. For instance, on the CIRA-CIC-DoHBrw-2020 dataset,
MAGNN achieves an inference time of 2.4s per epoch, whereas EGraphSAGE and TCGNN take 4.5s and 4.2s, respectively.
These results highlight the ability of MAGNN to achieve a balance
between computational eﬃciency and detection accuracy. The reduced
training and inference times make MAGNN highly suitable for real-time
malicious traﬃc detection, where fast and eﬃcient processing is critical.
Additionally, the scalability of MAGNN across multiple datasets further
validates its robustness and practical applicability for large-scale cybersecurity systems.
5.5. Comparison of graph construction paradigms
To evaluate the eﬀectiveness of the graph construction strategy, we
compare three diﬀerent paradigms for representing network traﬃc as
graphs, each integrated into the MAGNN framework: (a) a host-centric
graph, where nodes represent IPs or devices and edges represent communication ﬂows; (b) a ﬂow-centric graph, where nodes correspond to
individual traﬃc ﬂows and edges capture topological or temporal relationships (e.g., shared hosts or adjacent timestamps); and (c) a featurelevel graph, where nodes represent ﬂow features and edges reﬂect statistical correlations among them.

5.6. Distributed training evaluation
To further validate the scalability and computational eﬃciency of
the proposed MAGNN framework, we conducted a comprehensive evaluation of its training behavior under both non-distributed (single GPU)
12

Journal of Parallel and Distributed Computing 211 (2026) 105240

M. Ahmed, J. Chen, E. Akpaku et al.

Fig. 10. Comparative performance of diﬀerent graph construction paradigms on four network traﬃc datasets: (a) IPs or devices as nodes with communication ﬂows
as edges, (b) Traﬃc ﬂows as nodes with topological relationships as edges, and (c) Flow features as nodes with feature correlation-based edges.

Table 6
Ablation study of the proposed MAGNN model.

and distributed (multi-GPU) conﬁgurations. The distributed implementation employs PyTorch’s Distributed Data Parallel (DDP) module across
multiple NVIDIA GPUs, enabling parallel gradient computations and
synchronized parameter updates. We selected PyTorch DDP due to its
communication eﬃciency and widespread adoption in research and production environments, establishing a reliable baseline for scalable training evaluation.
Figs. 11(a)-11(d) present the normalized distribution of network trafﬁc data (nodes and edges) across 1, 2, 3, and 4 GPUs for the CTU-13,
ISCXVPN2016, CICIDS-2017, and CIRA-CIC-DoHBrw-2020 datasets, respectively. The results show that the graph partitioning achieves a stable and eﬃcient distribution of traﬃc data even as the number of GPUs
increases. For instance, on the CTU-13 dataset (Fig. 11(a)), the node
and edge traﬃc distribution remained between approximately 88% and
110% as the number of GPUs increased from 1 to 4, indicating consistent workload sharing. Similar trends are observed for the ISCXVPN2016
(Fig. 11(b)), CICIDS-2017 (Fig. 11(c)), and CIRA-CIC-DoHBrw-2020
(Fig. 11(d)) datasets, demonstrating that MAGNN maintains stable and
eﬃcient distribution of network traﬃc data across GPUs.
Figs. 12(a)-12(d) report the normalized training time and speedup
percentages achieved with distributed conﬁgurations. For all datasets,
the training time at 1 GPU is normalized to 100%, and the relative training times for 2, 3, and 4 GPUs show signiﬁcant reductions. For instance,
on the CTU-13 dataset (Fig. 12(a)), the training time decreases by approximately 39.52% when using two GPUs, and by up to 59.83% with
four GPUs. Similar improvements are observed on the ISCXVPN2016
(Fig. 12(b)), CICIDS-2017 (Fig. 12(c)), and CIRA-CIC-DoHBrw-2020
(Fig. 12(d)) datasets, with speedup rates consistently exceeding 50%
when utilizing three or more GPUs.
Importantly, distributed training did not compromise detection performance. The convergence rates and classiﬁcation metrics remained
comparable between single-GPU and multi-GPU settings, ensuring that
the parallelization process preserved model eﬀectiveness. The workload
variations observed during graph partitioning did not adversely impact
model convergence or stability.
These results demonstrate that MAGNN not only achieves high detection accuracy but also scales eﬃciently with additional computational
resources. This capability makes MAGNN a practical and robust solution for large-scale, real-time network traﬃc detection scenarios, where
rapid model updates and the ability to handle massive graph structures
are essential.

Ablation Component

Acc.

F1-Score

MSE

RMSE

MAE

MAPE

Full Model (MAGNN)
Without Multi-Head Contrast
Without Edge-Level Contrast
Without Temporal-Node Contrast
Without Graph Augmentation
Without Integrated Loss

98.45
97.30
97.10
96.80
96.50
96.90

97.58
96.85
96.45
96.00
95.75
96.20

0.06
0.09
0.10
0.12
0.13
0.11

0.20
0.25
0.26
0.28
0.30
0.27

0.31
0.42
0.48
0.50
0.54
0.49

1.08
1.15
1.22
1.25
1.28
1.20

(97.58%) across all metrics. Additionally, the full model recorded the
lowest error values for MSE, RMSE, MAE, and MAPE, highlighting its
superior predictive capability and robustness.
When the multi-head hierarchical contrast module was removed,
the performance dropped signiﬁcantly, with a reduction in accuracy
(97.30%) and F1-score (96.85%), indicating that this component is
crucial for capturing multi-scale hierarchical dependencies within the
graph. Similarly, disabling the edge-level contrast resulted in further
degradation of performance, particularly in error metrics, with MSE and
RMSE increasing to 0.10 and 0.26, respectively. This underscores the importance of edge embeddings in capturing packet-level relationships for
malicious traﬃc detection.
The temporal-node contrast, designed to model temporal dependencies in network traﬃc, also proved essential. Its removal led to further
performance reductions, with an F1-score dropping to 96.00%, emphasizing the role of temporal information in identifying evolving threats
and malicious behaviors. The absence of the graph augmentation module, which incorporates edge modiﬁcations and random walk sampling,
resulted in the most signiﬁcant degradation in error metrics, with MAE
and MAPE increasing to 0.54 and 1.28, respectively. This highlights the
importance of augmentation strategies in improving model generalization and robustness to diverse network scenarios.
Finally, replacing the integrated loss function with individual loss objectives revealed the importance of the multi-scale optimization framework. The performance of the model decreased across all metrics, with
accuracy dropping to 96.90% and F1-score to 96.20%. This demonstrates that the integrated loss function enables the framework to eﬀectively combine hierarchical, temporal, and edge-level information for
optimal performance.
Finally, the ablation study validates the design choices in the
MAGNN framework, with each component contributing signiﬁcantly to
the overall performance. The results highlight the eﬀectiveness of combining multi-scale adaptive graph learning, contrastive mechanisms,
and augmentation strategies for malicious network traﬃc detection.

5.7. Ablation study
The eﬀectiveness of the proposed MAGNN framework was analyzed by conducting an ablation study, systematically disabling speciﬁc
modules to assess their contributions to overall performance. Table 6
presents the results, demonstrating the critical role of each component
in achieving optimal results for malicious network traﬃc detection.
The complete MAGNN Model consistently outperformed its ablated variants, achieving the highest accuracy (98.45%) and F1-score

5.8. Adaptability to evolving threats
MAGNN is inherently designed to enhance generalization through
contrastive learning with graph augmentation and hierarchical representations, which can help improve resilience to zero-day attacks and
13

M. Ahmed, J. Chen, E. Akpaku et al.

Journal of Parallel and Distributed Computing 211 (2026) 105240

Fig. 11. MAGNN achieves stable and eﬃcient workload distribution across multiple GPUs, with node and edge partitioning.

Fig. 12. MAGNN achieves substantial training eﬃciency gains as the number of GPUs increases, demonstrating its scalability under distributed training setups.

unforeseen anomalies. Speciﬁcally, the multi-scale contrastive framework enables the model to learn robust structural and semantic patterns
rather than relying solely on known attack signatures. This capability
supports the detection of zero-day threats that exhibit novel behaviors.
While MAGNN does not explicitly model long-term temporal dependencies associated with Advanced Persistent Threats (APTs), its hierarchical and edge-level encoding can capture ﬁne-grained interactions
that may indicate dormant or stealthy patterns. Additionally, the use of
stochastic graph augmentations (e.g., edge modiﬁcations and subgraph
sampling) promotes adaptability to dynamic changes in traﬃc feature
distributions.
Nonetheless, we acknowledge that further improvements could be
achieved by integrating online learning mechanisms or memory-based
architectures to track evolving behaviors over time. Future work may
explore continual contrastive learning or temporal memory networks to
enhance MAGNN’s responsiveness to concept drift and long-term attack
evolution.
6. Conclusion
The proposed MAGNN framework presents signiﬁcant advancements
in malicious network traﬃc detection by leveraging multi-scale adaptive
graph learning and contrastive mechanisms. By integrating temporalnode, edge-level, and hierarchical contrastive learning, MAGNN eﬀectively captures both local and global dependencies within network trafﬁc data, ensuring robustness and scalability across diverse environments. Experimental evaluations on four benchmark datasets-CTU-13,
ISCXVPN2016, CICIDS-2017, and CIRA-CIC-DoHBrw-2020-demonstrate
the consistent superiority of MAGNN over state-of-the-art baseline models, including Anomal-E, NEGAT, E-Graph SAGE, TCGNN, and DE-GNN.
MAGNN achieved higher accuracy and F1-scores while maintaining
lower error rates across all datasets, conﬁrming its ability to handle
complex and evolving traﬃc patterns. The use of a novel graph augmentation strategy and a self-supervised learning paradigm further reduced
dependency on labeled data, enhancing its applicability to real-world
cybersecurity challenges.
The results highlight MAGNN’s robustness, faster convergence, and
computational eﬃciency compared to existing approaches. Its strong
generalization capability across heterogeneous network environments
and its eﬀectiveness in detecting emerging threats position it as a
practical and scalable solution for large-scale cybersecurity systems.
Looking ahead, several promising directions exist for extending this

work. First, incorporating advanced graph augmentation techniques and
dynamic graph representations could further enhance adaptability to
rapidly changing network conditions. Integrating additional contextual
features-such as application-layer protocols or user behavior metricsmay improve the detection of previously unseen attack patterns.
Expanding evaluations to include larger, more diverse datasets and
real-time network traﬃc would further validate the framework’s practical applicability. Exploring hybrid models that combine graph-based
learning with other paradigms, such as transformers or reinforcement
learning, also holds potential. Lastly, addressing explainability in graph
neural networks remains critical; developing interpretable mechanisms
within MAGNN will be key to fostering trust and adoption in operational
cybersecurity environments. These future directions aim to further reﬁne MAGNN’s capabilities, ensuring its continued eﬀectiveness in the
face of evolving network threats.
PAPER_TEXT
