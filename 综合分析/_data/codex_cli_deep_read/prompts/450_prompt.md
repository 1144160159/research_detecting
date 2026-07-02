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
# [450] GNN-Enhanced Traffic Anomaly Detection for Next-Generation SDN-Enabled Consumer Electronics
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
编号：450
题名：GNN-Enhanced Traffic Anomaly Detection for Next-Generation SDN-Enabled Consumer Electronics
年份：2025
DOI：10.1109/tce.2025.3620095
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2025.3620095.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、图学习、知识图谱与威胁情报
相关性：强相关，分数 11
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\450.txt
- 原始字符数：51363
- 本次发送字符数：51363
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

10977

GNN-Enhanced Traffic Anomaly Detection for
Next-Generation SDN-Enabled
Consumer Electronics
Guan-Yan Yang , Graduate Student Member, IEEE, Farn Wang , Member, IEEE,
and Kuo-Hui Yeh , Senior Member, IEEE

Abstract— Consumer electronics (CE) connected to the Internet of Things are susceptible to various attacks, including DDoS
and web-based threats, which can compromise their functionality and facilitate remote hijacking. These vulnerabilities allow
attackers to exploit CE for broader system attacks while enabling
the propagation of malicious code across the CE network,
resulting in device failures. Existing deep learning-based traffic
anomaly detection systems exhibit high accuracy in traditional
network environments but are often overly complex and reliant
on static infrastructure, necessitating manual configuration and
management. To address these limitations, we propose a scalable network model that integrates Software-defined Networking
(SDN) and Compute First Networking (CFN) for next-generation
CE networks. In this network model, we propose a Graph
Neural Networks-based Network Anomaly Detection framework (GNN-NAD) that integrates SDN-based CE networks and
enables the CFN architecture. GNN-NAD uniquely fuses a static,
vulnerability-aware attack graph with dynamic traffic features,
providing a holistic view of network security. The core of the
framework is a GNN model (GSAGE) for graph representation
learning, followed by a Random Forest (RF) classifier. This design
(GSAGE+RF) demonstrates superior performance compared to
existing feature selection methods. Experimental evaluations on
CE environment reveal that GNN-NAD achieves superior metrics
in accuracy, recall, precision, and F1 score, even with small
sample sizes, exceeding the performance of current network
anomaly detection methods. This work advances the security and
efficiency of next-generation intelligent CE networks.

Received 23 June 2025; revised 1 August 2025 and 8 September 2025;
accepted 6 October 2025. Date of publication 10 October 2025; date of
current version 8 December 2025. This work was supported in part by Taiwan
Academic Cybersecurity Center, National Taiwan University of Science
and Technology; in part by the National Science and Technology Council
(NSTC) under Grant 114-2221-E-002-217, Grant 114-2622-E-A49-022, Grant
114-2221-E-A49-210, Grant 114-2634-F-011-002-MBK, and Grant 114-2923E-194-001-MY3; in part by National Taiwan University (NTU) and the NTU
Core Consortium Project as part of the Higher Education Sprout Project
by the Ministry of Education in Taiwan under Grant NTU-CC-114L895501
and Grant NTU-G0647; in part by the Department of Industrial Technology,
Ministry of Economic Affairs, through the “2025 ITRI Advanced Research
Program,” under Grant 114-EC-17-A-21-0337; in part by the Hon Hai
Research Institute, Taipei, Taiwan, under Project 114UA90042; and in part by
the Industry-Academia Innovation School, National Yang Ming Chiao Tung
University (NYCU), Taiwan, under Project 113UC2N006. (Corresponding
authors: Kuo-Hui Yeh; Farn Wang.)
Guan-Yan Yang and Farn Wang are with the Department of Electrical
Engineering, National Taiwan University, Taipei 106319, Taiwan (e-mail:
f11921091@ntu.edu.tw; farn@ntu.edu.tw).
Kuo-Hui Yeh is with the Institute of Artificial Intelligence Innovation,
National Yang Ming Chiao Tung University, Hsinchu 300093, Taiwan, and
also with the Department of Information Management, National Dong Hwa
University, Shoufeng, Hualien 974301, Taiwan (e-mail: khyeh@nycu.edu.tw).
Digital Object Identifier 10.1109/TCE.2025.3620095

Index Terms— Consumer electronics, compute first networking, cyberattack, graph neural networks, Internet of Things,
intrusion detection, network anomaly, next-generation networking, denial-of-service attack, cyberattack, cybersecurity,
software-defined networking.

I. I NTRODUCTION

T

HE rapid expansion of the Internet of Things (IoT)
has seamlessly integrated consumer electronics (CE)
devices—such as smartphones, smartwatches, and laptops—
into our daily lives, enabling remote access and connectivity
across diverse sectors like e-healthcare, smart cities, and
intelligent transportation [1]. The CE market is projected to
reach 2.873 billion users by 2025, driven by the capacity of
nearly every device to generate and share data [2], [3].
CE networks, composed of heterogeneous devices from
various manufacturers, present unique challenges due to
large-scale deployment, high device diversity, and limited
computational resources [1], [4]. Unlike traditional IT networks, CE devices such as smart home appliances and
wearables require lightweight, secure, and low-latency communication [5]. Their traffic is often encrypted, intermittent,
and follows irregular patterns, complicating the task of network anomaly detection (NAD) [6]. Security breaches in CE
can have severe consequences, including privacy invasion,
financial loss, and physical safety risks, and compromised
devices can be conscripted into botnets for large-scale attacks
like DDoS campaigns [7], [8], [9].
While existing machine learning (ML) and deep learning
(DL) methods for NAD have shown promise, they often
suffer from time-consuming feature extraction processes and
require extensive manual configuration, making them ill-suited
for the dynamic nature of CE networks [10]. To overcome
these limitations, advanced architectures like Compute First
Networking (CFN) and Software-Defined Networking (SDN)
are gaining traction. CFN integrates cloud, edge, and end-user
computing resources to optimize performance [11], [12], while
SDN centralizes network control, providing a global view
essential for robust security management [13]. The synergy
between SDN and GNN-NAD is particularly powerful; once
an anomaly is detected, the SDN controller can be programmed to automatically install new flow rules to isolate
a malicious device, thus creating a closed-loop system that
moves seamlessly from detection to response.

1558-4127 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

10978

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

This paper introduces a novel GNN-based Network
Anomaly Detection (GNN-NAD) framework designed for
SDN-enabled CE networks. The core novelty of our work
lies in its holistic approach. Most NAD systems analyze only
traffic statistics (the “how” of an attack), while traditional
vulnerability analysis focuses only on static configurations
(the “what”). Our framework uniquely combines both: we
construct a static, vulnerability-aware attack graph that models
potential exploit paths (the “what”) and enrich it with realtime, dynamic traffic data (the “how”). This synthesis of
static posture and dynamic behavior allows for a far more
comprehensive and accurate security assessment than either
approach could achieve alone.
The key contributions of this work are as follows:
• We propose a novel GNN-NAD framework that integrates
a static attack graph with dynamic traffic features. Our
specialized GNN model, GSAGE, is tailored to learn
rich representations from this combined graph structure,
outperforming standard GNN models.
• We benchmark GNN-NAD against state-of-the-art
(SOTA) NAD approaches, demonstrating its superior
accuracy, precision, recall, and F1-score.
• Through robustness analysis at various data sampling
rates, we validate that our framework is highly effective
for early detection, maintaining high accuracy even with
limited data. Representing our work is probably widely
used for real-world CE and IoT scenarios.
The rest of this paper is organized as follows: Section II
reviews related work. Section III details the network model.
Section IV introduces the GNN-NAD framework. Section V
presents the experimental setup, evaluation metrics, and detection performance. Finally, Section VI concludes the study and
outlines directions for future research.
II. R ELATED W ORKS
This section reviews prior work in CFN security and
network anomaly detection, creating a foundation for our
proposed framework by identifying existing research gaps.
A. Security in CFN and Intelligent IoT
Current research in Compute First Networking (CFN)
primarily addresses integration architectures, resource scheduling, and security [12], [14], [15]. Resource scheduling has
been explored through centralized and decentralized management [16], microservice-based models [17], prioritization
strategies [18], and cloud-edge frameworks [19]. Recent work
in the broader field of AIoT has also addressed resource
allocation challenges; for instance, Li et al. [20] proposed
an AI-driven task scheduling mechanism to manage computational resources in dynamic vehicular networks for smart
warehousing, demonstrating the growing trend of integrating
intelligence into resource management.
Security in CFN has been advanced through mechanisms
like the CFN Watchdog for fault detection [21], federated
learning for secure operations [22], and blockchain for data
integrity [23]. However, as noted in [24], dedicated research on
NAD specifically for CFN environments is still lacking. This

represents a critical gap, as the distributed and dynamic nature
of CFN introduces unique security challenges that traditional
methods may not adequately address.
B. Traditional and ML-Based NAD
Traditional NAD methods often rely on statistical features extracted from network flows. Vinayakumar et al.
[25] employed Deep Neural Networks (DNNs) on the CICIDS2017 dataset, showing strong performance. Ning et al. [26]
improved cross-domain generalization through the integration
of semi-supervised learning, transfer learning, and domain
adaptation, validated on the USTC-TFC2016 dataset. Anbalagan et al. [27] developed an intelligent intrusion detection
system for 5G vehicular networks, employing enhanced convolutional neural networks and hyperparameter optimization
on simulated traffic. Huang et al. [28] proposed a two-stage
multi-label network attack detection method validated on the
UNSW-NB15 dataset, demonstrating enhanced accuracy over
existing techniques. Nie et al. [29] examined abnormal traffic
fluctuations in the Internet of Vehicles (IoV) by analyzing
roadside units (RSUs), validated through self-simulated traffic
anomalies. Other notable works in CE network include SEMIGRU [30], which used a semi-supervised GRU for vehicular
networks, and the work by Javeed et al. [31], which developed a CUDA-optimized BLSTM (Cu-LSTM) for SDN-based
cyberattack detection.
While effective, these approaches primarily analyze traffic statistics in isolation, ignoring the underlying network
topology and device vulnerabilities. They can struggle to
detect sophisticated attacks that mimic normal traffic patterns.
Furthermore, many require extensive, well-labeled datasets for
training, which are not always available in real-world CE
environments.
C. GNN-Based and Advanced NAD
To overcome the limitations of traditional methods,
researchers have turned to Graph Neural Networks (GNNs),
which can naturally model the relational structure of networks.
Deng et al. [32] proposed a traffic graph with interval constraints and a spatial attention mechanism for label-limited
intrusion detection, validated on three public datasets. Chang
and Branco [33] addressed class imbalance by enhancing
GraphSAGE and GAT algorithms with residual connections,
showing effectiveness on UNSW-NB15 and CIC-IDS2017.
Reference [34] developed a GNN-based method for NAD that
constructs host connection graphs using traffic flow features,
though it faces high computational costs due to reliance on
aggregated observations and traditional statistical features.
This approach was validated on the CIC-IDS2017 dataset.
Golchin et al. [35] achieved 96.54% accuracy on the CICIDS2017 dataset, while Li et al. [36] attained 99.9% accuracy
and a 95% weighted recall rate by integrating contrastive
learning with CNN and GRU models. Despite these promising
results, a well-documented limitation of contrastive learning is
its high computational overhead, which stems from the need
for a large number of negative samples during training [37].
Huang et al. [28] proposed a two-stage multi-label network

YANG et al.: GNN-ENHANCED TRAFFIC ANOMALY DETECTION FOR NEXT-GENERATION SDN-ENABLED CE

attack detection method validated on the UNSW-NB15 dataset,
demonstrating enhanced accuracy over existing techniques.
Zeng et al. [38] presented a “Human-in-the-Loop” framework
that incorporates human expertise for intrusion detection,
achieving 99.16% accuracy with 28,100 manually labeled
samples on the CIC-IDS2017 dataset. Tran and Park [39]
developed a hybrid model integrating GCN and SAGEConv for
graph-based feature learning, surpassing previous methods in
accuracy and other performance metrics on the CIC-IDS2017
dataset. Recent related research by Islam et al. [40] introduces
an explainable AutoML-driven scheme for intrusion prevention in Zero-Touch Networks, highlighting the trend towards
automated and transparent security solutions. In 2025, Fu et al.
[41] presented a GNN that uses flow interaction relationships
for intrusion detection on consumer electronics within smart
home networks. Concurrently, Pei et al. [42] proposed an
edge intelligence-enabled network intrusion detection system
tailored for Compute First Networking, emphasizing the move
towards decentralized and resource-aware security architectures. Later, we introduced GSL-IDS [43], a graph structure
learning-based method for enhancing network resilience with
network intrusion detection, which provides strong resilience
against model adversarial attacks.
D. Research Gap Summary
The existing literature reveals a clear gap: a lack of NAD
frameworks that holistically integrate static vulnerability information with dynamic traffic analysis in a computationally
efficient manner suitable for CE networks. Our GNN-NAD
framework directly addresses this gap by creating a unified
graph representation that captures both the “what” (vulnerabilities) and the “how” (traffic patterns) of network security.
III. O UR N ETWORK M ODEL
The CFN is gaining recognition as an effective strategy for
developing converged networks. Its architecture is defined by
the separation of four key components: the computing resource
pool (infrastructure), the routing plane, the control plane
(orchestration and management layer), and the service plane
(application layer). This separation ensures both simplicity and
flexibility. In contrast, traditional networks are limited because
each router can only perceive the status of its local network,
lacking a comprehensive view of the entire network. This
limitation creates significant challenges in developing robust
defense mechanisms against network threats.
Integrating CFN with SDN gives the network a global perspective and centralized control capabilities. This combination
facilitates easier access to network statistics. Within the CFN
framework, the service plane offers computational services to
users, enabling consumer electronics (CE) applications like
smart homes, intelligent transportation systems, and mobile
computing. The control plane handles routing, data transmission, and traffic monitoring through advanced application
technologies. The routing plane consists of numerous CE
switches and routers, while the computing resource pool
includes various CE devices, such as smart devices, sensors,
and other wireless technologies.

Fig. 1.

10979

Our Network Model.

In our model, CE devices (such as smart TVs, wearables,
home gateways, IoT sensors) are directly represented as nodes
in the network, each with unique resource constraints and
communication patterns. The SDN/CFN architecture enables
dynamic, centralized management of these heterogeneous
devices, supporting the specific needs of CE networks such as
seamless device onboarding, real-time anomaly detection, and
adaptive resource allocation. Our anomaly detection framework is designed to operate efficiently in such environments,
considering the limited typical capabilities of CE devices.
As illustrated in Figure 1, our model positions the proposed
GNN-NAD framework within the CFN Control Plane. This
placement is strategic: the control plane, managed by an SDN
controller, has access to all network statistics and can dynamically manage network elements. This allows GNN-NAD not
only to detect threats but also to orchestrate an immediate,
automated response. For example, upon detecting a malicious
device, the framework can instruct the SDN controller to install
flow rules that isolate the device, effectively closing the loop
from detection to mitigation.
Integrating CE, CFN, and SDN offers a streamlined solution
for monitoring network traffic, enhancing the detection of
attacks and suspicious activities. CFN and SDN provide a
cohesive view of all devices and network elements, significantly improving the ability to monitor traffic and identify
potential threats, attacks, and adverse events. Thus, CFN
and SDN represent a promising direction for advancing CE
networks.
IV. P ROPOSED GNN-NAD F RAMEWORK
This section proposes a network anomaly detection method
based on graph neural network embeddings (GNN-NAD),
as illustrated in Figure 2. We first introduce the key
components of GNN-NAD, including graph construction,
GNN-based graph representation learning, and classification.

10980

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

Algorithm 1 Encode Attack Graph
Require: nodes V , edges E, statements {Sv | ∀v ∈ V }
Ensure: Encoded attack graph S AG = (V, E, F)
1: Initialize C set
2: for v ∈ V do
3:
for w ∈ Sv do
4:
Add w to Cset
5:
end for
6: end for
7: Convert C set to a list C
8: Create an index map map ← {C[i] → i}
9: Let D ← |C|
10: Initialize a feature matrix F[n][D] with zeros
11: for v ∈ V do
12:
for w ∈ Sv do
13:
i ← map[w]
14:
F[v][i] ← 1
15:
end for
16: end for
Fig. 2.

Our Proposed Detection Framework.

Network Assets: Includes the hostnames, IP addresses,
interface names, target network IP addresses, and subnet
masks, as well as source and destination IPs and ports
along with their associated transport protocols.
• Network
Hosts: Captures the interface names,
IP addresses, and their corresponding relationships
with LAN/WAN connections.
• Network Vulnerabilities: Identifies potential CVEs collected from the National Vulnerability Database (NVD).
2) Dynamic Traffic Data: Dynamic measurements are typically presented in time series format, which is crucial for the
real-time dynamic analysis of complex CE networks. In GNNNAD, we have multiple actions, each representing either an
attack or a benign action. We represent dynamic measurements
at time t as RDMt , the real-time dynamic measurements of a
network are expressed as:
•

A. Graph Construction
1) Static Attack Graph: An attack graph (AG) is a directed
acyclic graph (DAG) that represents the potential attack paths
an adversary might exploit within a network by leveraging
vulnerabilities [44]. Based on network security analysis, several attack graph models have been proposed [45], [46], [47].
The Multi-host, Multi-stage Vulnerability Analysis Language
(MulVAL) approach [48] stands out for its scalability and
low computational complexity. As a result, we employ MulVAL for AG generation and then design the AG encoding
method to get a static attack graph (SAG) in our proposed GNN-based Network Attack Detection (GNN-NAD)
framework.
We encode this logical AG into a Static Attack Graph (SAG)
for our GNN. The SAG is represented as SAG = (V, E, F),
where V is the set of nodes, E is the set of edges, and F ∈
Rn×D is the node feature matrix. The features are derived from
the text statements associated with each MulVAL node (such
as ‘execCode(webServer,_)’). As detailed in Algorithm 1,
we use a bag-of-words approach to create a one-hot encoded
vector fv for each node v, where the vocabulary C is built
from all unique tokens (words, predicates, parameters) across
all node statements.
While more complex node embedding techniques like
Word2Vec were considered, we chose the bag-of-words
method for its simplicity, direct interpretability, and potential
computational efficiency. This is a critical design choice for
ensuring the framework remains lightweight and suitable for
resource-constrained CE environments. Our experiments confirm that this straightforward encoding is highly effective for
this task.
Since our focus is on generating a SAG, we collect the
following types of static information:
• Network Configuration: Includes the IP ranges, subnets,
IP addresses, subnet masks, and gateway addresses of the
covered network segments.

t
RDMt = {xaction
, ∀action ∈ actions}.
t
Here, xaction
∈ R K and K is the number of measured variables.
These measurements are aggregated over discrete time windows. Let t be a continuous time index. We aggregate features
over a time window [t1 , t2 ]. Specifically, the k-th measurement
at time t can be calculated using the following formula:
t1
t2
t
xaction,k
= AGG(xaction,k
, . . . , xaction,k
),

t1 ≤ t ≤ t2 .

After a number of these aggregation rounds, indexed by
k, we can set X dyn [action] = xaction , i.e., obtain the final
dynamic feature vectors for each observed action (such as
a network flow). For clarity, t refers to the fine-grained
timestamp of a raw data point, while k refers to the discrete
update cycle or round in which aggregated data is processed.
B. Integrating Static and Dynamic Features
This step is crucial for fusing the “what” (static vulnerabilities) with the “how” (dynamic traffic). Dynamic
traffic features, which are flow-based (such as containing
source/destination IPs and ports), are mapped onto the nodes

YANG et al.: GNN-ENHANCED TRAFFIC ANOMALY DETECTION FOR NEXT-GENERATION SDN-ENABLED CE

of the static graph. A dynamic feature vector from a specific
traffic flow is mapped to a node i in the SAG if the statement
Si of that node contains corresponding network identifiers.
For example, a dynamic flow log showing traffic between
IP ‘172.30.211.20’ and ‘172.30.211.24’ would have its feature
vector (such as packet count, byte count) mapped to the
specific nodes in the SAG that represent these two hosts. This
is achieved by searching for the IPs in the node statements.
The initial feature vector for each node i is then formed by
concatenating its static feature vector F[i] with its mapped
dynamic feature vector X dyn [i]:
(0)

hi

← Concat(F[i], X dyn [i]),

∀i ∈ V

(0)
This integrated feature vector h i serves as the input for the

GNN.
C. GNN-Based Representation Learning
To learn a comprehensive representation of the entire graph,
we use our custom GNN model, GSAGE. As demonstrated
in Figure 2, the GNN-NAD framework defines GSAGE as
a model composed of three SAGE Convolution (SC) layers,
each followed by a ReLU activation and a Dropout layer
for regularization. This learned representation is then passed
through a global pooling layer to produce a single embedding
for the entire graph.
The distinction between our GSAGE model and a baseline
GraphSAGE lies in its specific, streamlined architecture. While
GraphSAGE is a general framework, GSAGE is an implementation optimized for our specific task. Key differences include:
• Architecture: GSAGE uses a 3-layer stack with 256 hidden units, a configuration found to be optimal for
capturing complex patterns in our vulnerability-traffic
graphs without overfitting.
• Efficiency: The architecture is intentionally lean to ensure
fast processing on resource-aware CE hardware. It is
designed to handle the sparse but high-dimensional feature vectors generated by our graph construction process
effectively.
The propagation rule for each SC layer l is:



(l)
(l+1)
(l)
hi
= σ W (l) · AGGR {h i } ∪ {h j , ∀ j ∈ N (i)}
where the propagation of features occurs across layers, with
(l)
each node i represented by its feature vector h i at layer
l. The transformation of these features relies on the trainable weight matrix W (l) specific to that layer. To effectively
capture information from neighboring nodes, the aggregation
function denoted as AGGR is employed, which can take the
form of mean or sum, depending on the desired outcome.
Subsequently, an activation function σ , such as the ReLU
function, is applied to introduce non-linearity, facilitating
complex pattern recognition within the graph. Furthermore,
the set of neighbors for any given node i is represented by
N (i), which plays a crucial role in the aggregation process.
For other layers, Dropout regularization is applied to node
representations:
h (l) = Dropout(h (l) ; p)
where p is the dropout probability.

10981

In the global pooling layer, we combine node embeddings
into a single graph embedding:
n

h graph =

1 X (L)
hi
n
i=1

where n is the number of nodes and L is the final layer.
Moreover, the graph representation learning objective function uses cross-entropy loss. After learning, the system will
run the next phase, i.e., classification.
D. Classification
For our classification task, we chose to use the random
forest algorithm. Random forest is a highly effective classifier
known for its exceptional accuracy and strong ability to
generalize. By combining predictions from multiple decision
trees, it reduces the risk of overfitting, making it particularly
suitable for high-dimensional data. Additionally, random forest
includes an inherent feature selection mechanism. It also
performs well with imbalanced datasets by adjusting sample
weights to improve classification performance. Its strong resistance to noise further minimizes the impact of outliers on the
model. For these reasons, we have selected the random forest
classifier for this study.
V. E XPERIMENT
This section presents the experiments and evaluation of the
performance of our proposed GSAGE model. We detail the
experimental setup, evaluation metrics, and discuss the results.
Specifically, we investigate the effect of the number of samples
used to update the graph on our detection performance of
GSAGE. We also highlight the advantages of GSAGE in network traffic feature extraction. Furthermore, we demonstrate
the performance of GNN-NAD in comparison to the SOTA
NAD approach.
A. Dataset and Preparation
The CIC-IDS-2017 dataset [49] is one of the most widely
utilized NAD datasets in recent years. It includes attack
and benign traffic data collected over five days under simulated network conditions. For data preprocessing, we first
removed all rows containing missing or non-numeric values,
as these could negatively impact the model’s performance.
Given the imbalance in sample distribution, certain categories,
such as infiltration and Heartbleed attacks, contained fewer
samples. To address this imbalance, we excluded these minority categories from our experiments. We randomly selected
1,000 traffic samples from each remaining category. To better
reflect real-world scenarios where benign traffic predominates,
we randomly selected 9,000 benign samples, which represent approximately 56% of the total dataset. Furthermore,
we applied min-max normalization to the data before updating
the graphs.
B. Environment
The proposed model is implemented using Python
3.8.20 and trained with PyTorch. All experiments are run on
Docker. The experimental environment has been specifically

10982

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

TABLE I
PARAMETER OF O UR M ODELS

Fig. 3.

Topology for our experiment. (Screenshot from Onos Controller.)

designed to reflect the proposed CFN architecture using lowpower, accessible hardware. The entire SDN topology is
constructed using three Raspberry Pi computers. This setup
provides a cost-effective yet powerful platform for emulating
a CE network.
The roles of the Raspberry Pi devices are distributed as
follows:
• Raspberry Pi 5 with 16GB RAM (Controller & NAD):
Hosts the ONOS SDN controller and runs the GNN-NAD
detection framework. It manages the network and performs the data analysis.
• Raspberry Pi 5 with 16GB RAM (SDN Switch): Configured with Open vSwitch to act as the forwarding element
in the routing plane. It connects the traffic-generating
device to the network and communicates with the ONOS
controller via the OpenFlow protocol.
• Raspberry Pi 4 with 8GB RAM (CE Device): Represents
the CE devices in the “CFN Service Plane,” such as smart
TVs, wearables, or IoT sensors. It serves as the traffic
source, generating diverse traffic patterns that simulate
real-world CE device usage. As a node in the CFN Computing Resource Pool, its traffic patterns and resource
constraints are designed to be representative of typical
CE devices. It is used to replay the attack and benign
scenarios from the CIC-IDS-2017 dataset.
This physical topology, with the controller’s view captured in Figure 3, allows us to evaluate the effectiveness
and efficiency of our anomaly detection framework under
conditions that closely resemble real-world, resource-aware
CE deployments. The traffic patterns and attack scenarios are
designed to reflect typical CE network usage, including bursty
traffic and the introduction of malicious data flows, providing
a robust testbed for our system.
C. Metrics
We evaluate GNN-NAD based on the following metrics:
TP +TN
Accuracy =
,
T P + T N + FP + FN
TP
Recall =
,
T P + FN
TP
Precision =
,
T P + FP
Recall × Precision
F1-score = 2 ×
,
Recall + Precision

where TP, FP, TN, and FN represent true positives, false
positives, true negatives, and false negatives, respectively.
D. Model Parameters
We randomly partition the dataset by allocating 80% of the
samples to the training set, while reserving the remaining 20%
for the test set. Each experiment is repeated ten times to obtain
average results. The parameters for the GSAGE, DNN, and
GNN models are presented in Table I. For the parameters of
SOTA methods, we follow the settings in their article.
E. Experimental Methods
For our experiment, we first examined the effectiveness of
GSAGE+RF in traffic feature extraction and classification by
contrasting it with a non-graph statistical flow feature method.
We selected representative models from deep learning as comparison benchmarks. Additionally, we compared GSAGE+RF
against two prominent GNN models to establish its superiority
in classification contexts.
Furthermore, we evaluated GSAGE+RF against
advanced NAD methods, including DNN, SEMI-GRU,
Cu-LSTM, GNN-NIDS, FN-GNN, GSL-IDS, FIR-GNN, and
NAAE-GCN. The first three utilize traditional approaches
based on traffic statistical features, while the latter five
incorporate structural features and statistics. We also
investigated the influence of sampling rate on detection
performance by systematically reducing the sample set of
CICIDS2017, selecting 20% of samples from each category.
F. Results
1) Compare With Representative Models: We first compared our graph-based approach (GSAGE+RF) against several
baselines. This includes models using traditional statistical
features extracted by CICFlowMeter (denoted with “CIC”) and
models using our graph construction method.
As shown in Table II, our proposed GSAGE+RF model
significantly outperforms all other configurations, achieving an
accuracy of 99.69%. Notably, when using statistical features
from CICFlowMeter, our GSAGE model architecture still
performs better than other model architectures (NN, GCN,
GraphSAGE). This indicates the robustness of the GSAGE
architecture itself. However, the most significant performance
lift comes from combining GSAGE with our novel graph
construction method, demonstrating the superiority of learning
from integrated static and dynamic graph features.

YANG et al.: GNN-ENHANCED TRAFFIC ANOMALY DETECTION FOR NEXT-GENERATION SDN-ENABLED CE

10983

TABLE II
P ERFORMANCE C OMPARISON W ITH R EPRESENTATIVE M ETHODS

Fig. 5.

Compare Testing Time with Baseline methods.
TABLE III
P ERFORMANCE C OMPARISON W ITH SOTA M ETHODS

Fig. 4. Compare with widely used NN and GNN models with different
sample rates with our graph classification method.

To further assess model performance under different data
conditions, we trained models using various sampling rates,
with accuracy results shown in Figure 4. GSAGE+RF consistently outperformed baseline methods across all sampling
rates, achieving an accuracy of 98.85% even at a 10% sampling rate.
We also analyzed model testing time, defined as the execution time on a pre-constructed graph or pre-processed
features (Figure 5). The results show two key trends. First,
our graph-based methods are substantially more efficient than
the CICFlowMeter-based approaches. For instance, inference
with our GSAGE model took 2.25s, a marked improvement
over the 7.07s for GraphSAGE with CICFlowMeter features.
Second, among the different architectures, NN-based models
were the fastest, and GSAGE was consistently quicker than the
standard GraphSAGE model. Moreover, the initial static graph
construction is a one-time offline cost (taking 4.12 seconds
in our experiments) and is not included in this recurring
testing time, making our overall approach highly efficient
for consumer electronic networks that require lightweight and
high accuracy.
2) Compare With SOTA NAD: We evaluated the performance of GSAGE+RF against various SOTA methods in
traffic feature extraction and graph classification. As shown
in Table III, GSAGE+RF outperformed all SOTA approaches
across four key metrics. Additionally, we trained our model
on datasets sampled at different rates, with accuracy results
illustrated in Figure 6. When the sample size was limited
(10%), most SOTA methods struggled to achieve satisfactory performance, with only simple models like DNN

Fig. 6.

Compare with SOTA NAD methods with different sample rates.

surpassing 90% accuracy. In contrast, GSAGE+RF achieved
98.85% accuracy and consistently outperformed other methods
across all sampling rates. These results demonstrate that our
GNN-NAD approach, powered by GSAGE+RF, can effectively detect network traffic anomalies with minimal training
data.
VI. C ONCLUSION AND F UTURE W ORK
In this paper, we introduced GNN-NAD, a novel network
anomaly detection framework tailored for next-generation
SDN-enabled CE networks. Our approach formulates NAD
as a graph classification problem by uniquely fusing a static
attack graph, which captures network vulnerabilities (the
“what”), with dynamic traffic data (the “how”). The core
of our framework, a combination of a streamlined GSAGE
model and a Random Forest classifier, proved highly effective. Experiments conducted on a realistic testbed of CE

10984

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 71, NO. 4, NOVEMBER 2025

devices demonstrated that GNN-NAD achieves state-of-theart performance, maintaining exceptional accuracy even with
limited training data. This makes it a practical and powerful
solution for securing heterogeneous and resource-constrained
CE environments.
This work opens several exciting avenues for future
research.
• Proactive and Predictive Defense: The static attack
graph contains rich information about potential attack
paths. This could be leveraged not just for detection
but for proactive defense, such as identifying critical
vulnerabilities to patch to disrupt the most likely attack
chains.
• Federated and Online Learning: To enhance privacy
and adaptability, a federated version of GNN-NAD could
be developed to train models across multiple CE networks
without sharing raw data. Furthermore, transitioning to an
online learning model would allow the system to adapt
to new threats continuously without the need for periodic
offline retraining.
• Explainable AI (XAI): A major challenge with GNNs
is their “black box” nature. Integrating XAI techniques,
such as GNNExplainer, would provide invaluable insights
into why the model flags certain activities as malicious,
making the system more transparent and trustworthy for
security analysts.
By pursuing these directions, we can further enhance the
security, intelligence, and autonomy of future CE networks.
ACKNOWLEDGMENT
The authors would like to express their gratitude for
the financial support. Thanks to the editors and the anonymous reviewers for their valuable comments. They appreciate
the technical support from the Speech AI Research Center,
National Yang Ming Chiao Tung University. Guan-Yan Yang
is grateful to the National Science and Technology Council
(NSTC), Taiwan, for the graduate research fellowship (NSTCGRF) and to Prof. Hung-Yi Lee for co-hosting his Ph.D
research project.
R EFERENCES
[1] C. K. Wu, C.-T. Cheng, Y. Uwate, G. Chen, S. Mumtaz, and K. F. Tsang,
“State-of-the-art and research opportunities for next-generation consumer electronics,” IEEE Trans. Consum. Electron., vol. 69, no. 4,
pp. 937–948, Nov. 2023.
[2] Statista. (2024). Consumer Electronics. Accessed: Mar. 2025.
[Online]. Available: https://www.statista.com/outlook/dmo/ecommerce/
electronics/consumer-electronics/worldwide
[3] M. Ibrar, L. Wang, G.-M. Muntean, J. Chen, N. Shah, and A. Akbar,
“IHSF: An intelligent solution for improved performance of reliable
and time-sensitive flows in hybrid SDN-based FC IoT systems,” IEEE
Internet Things J., vol. 8, no. 5, pp. 3130–3142, Mar. 2021.
[4] D.-J. Kim, N. G. B. Amma, and V. Sarveshwaran, “A novel
split learning-based consumer electronics network traffic anomaly
detection framework for smart city environment,” IEEE Trans. Consum. Electron., vol. 70, no. 1, pp. 4197–4204, Feb. 2024, doi:
10.1109/TCE.2024.3367330.
[5] J.-H. Syu, J. C.-W. Lin, G. Srivastava, and K. Yu, “A comprehensive
survey on artificial intelligence empowered edge computing on consumer electronics,” IEEE Trans. Consum. Electron., vol. 69, no. 4,
pp. 1023–1034, Nov. 2023.

[6] M. Adil, M. K. Khan, A. Farouk, M. A. Jan, A. Anwar, and Z. Jin, “AIdriven EEC for healthcare IoT: Security challenges and future research
directions,” IEEE Consum. Electron. Mag., vol. 13, no. 1, pp. 39–47,
Jan. 2024.
[7] S. Rani, D. Gupta, S. Garg, M. J. Piran, and M. S. Hossain, “Consumer electronic devices: Evolution and edge security solutions,” IEEE
Consum. Electron. Mag., vol. 11, no. 2, pp. 15–20, Mar. 2022.
[8] G.-Y. Yang, K.-H. Yeh, and L.-F. Lee, “Towards a novel interoperability
management scheme for cross-blockchain transactions,” in Proc. IEEE
10th Global Conf. Consum. Electron. (GCCE), Oct. 2021, pp. 942–943.
[9] R. Rajesh, S. Hemalatha, S. M. Nagarajan, G. G. Devarajan, M. Omar,
and A. K. Bashir, “Threat detection and mitigation for tactile internet
driven consumer IoT-healthcare system,” IEEE Trans. Consum. Electron., vol. 70, no. 1, pp. 4249–4257, Feb. 2024.
[10] D. Javeed, T. Gao, M. Khan, and I. Ahmad, “A hybrid deep learningdriven SDN enabled mechanism for secure communication in Internet
of Things (IoT),” Sensors, vol. 21, no. 14, p. 4884, Jul. 2021. [Online].
Available: https://www.mdpi.com/1424-8220/21/14/4884
[11] Y. Cui, Y. Li, J. He, L. Geng, P. Liu, and Y. Cui, “Framework of
compute first networking (CFN),” Internet Engineering Task Force, p.
14, Nov. 2019. [Online]. Available: https://datatracker.ietf.org/doc/draftli-rtgwg-cfn-framework/00/
[12] X. Tang et al., “Computing power network: The architecture of convergence of computing and networking towards 6G requirement,” China
Commun., vol. 18, no. 2, pp. 175–185, Feb. 2021.
[13] J. C. C. Chica, J. C. Imbachi, and J. F. B. Vega, “Security in SDN:
A comprehensive survey,” J. Netw. Comput. Appl., vol. 159, Jun. 2020,
Art. no. 102595.
[14] X. Gong, C. Bai, S. Ren, J. Wang, and C. Wang, “A survey of compute
first networking,” in Proc. IEEE 23rd Int. Conf. Commun. Technol.
(ICCT), Oct. 2023, pp. 688–695.
[15] X. Wang, X. Ren, C. Qiu, Y. Cao, T. Taleb, and V. C. M. Leung, “Netin-AI: A computing-power networking framework with adaptability,
flexibility, and profitability for ubiquitous AI,” IEEE Netw., vol. 35,
no. 1, pp. 280–288, Jan. 2021.
[16] K.-H. Yeh, G.-Y. Yang, C. Butpheng, L.-F. Lee, and Y.-H. Liu, “A secure
interoperability management scheme for cross-blockchain transactions,”
Symmetry, vol. 14, no. 12, p. 2473, Nov. 2022.
[17] Z. Yu, Y. Jiang, X. Liu, Y. Shi, C. Jiang, and L. Kuang, “Microservice
deployment in space computing power networks via robust reinforcement learning,” 2025, arXiv:2501.06244.
[18] G.-Y. Yang et al., “TPSQLi: Test prioritization for SQL injection
vulnerability detection in web applications,” Appl. Sci., vol. 14, no. 18,
p. 8365, Sep. 2024.
[19] X. Zhou and Z. Li, “Cloud-edge-end collaborative scheduling technology for computing power network,” ZTE Technol. J., vol. 29, no. 4,
pp. 32–37, 2023.
[20] Y. Li et al., “AIoT-enhanced outlier-resilient SLAM for smart warehousing in dynamic environments,” IEEE Internet Things J., vol. 12, no. 19,
pp. 39505–39518, Oct. 2025.
[21] H. Liang, L. Feng, F. Xu, G. Li, J. Xu, and Y. Chen, “A
novel CFN-watchdog protocol for edge computing,” Appl. Soft Comput., vol. 113, Dec. 2021, Art. no. 107873. [Online]. Available:
https://www.sciencedirect.com/science/article/pii/S156849462100795X
[22] L. Zhao, X. Tang, Z. You, Y. Pang, H. Xue, and L. Zhu, “Operation and
security considerations of federated learning platform based on compute
first network,” in Proc. IEEE/CIC Int. Conf. Commun. China (ICCC
Workshops), China, Aug. 2020, pp. 117–121.
[23] X. Xu, X. Zhang, H. Gao, Y. Xue, L. Qi, and W. Dou, “BeCome:
Blockchain-enabled computation offloading for IoT in mobile edge
computing,” IEEE Trans. Ind. Informat., vol. 16, no. 6, pp. 4187–4195,
Jun. 2020.
[24] S. Yukun et al., “Computing power network: A survey,” China Commun.,
vol. 21, no. 9, pp. 109–145, Sep. 2024.
[25] R. Vinayakumar, M. Alazab, K. P. Soman, P. Poornachandran,
A. Al-Nemrat, and S. Venkatraman, “Deep learning approach
for intelligent intrusion detection system,” IEEE Access, vol. 7,
pp. 41525–41550, 2019.
[26] J. Ning et al., “Malware traffic classification using domain adaptation
and ladder network for secure industrial Internet of Things,” IEEE
Internet Things J., vol. 9, no. 18, pp. 17058–17069, Sep. 2022.
[27] S. Anbalagan, G. Raja, S. Gurumoorthy, R. D. Suresh, and K. Dev,
“IIDS: Intelligent intrusion detection system for sustainable development
in autonomous vehicles,” IEEE Trans. Intell. Transp. Syst., vol. 24,
no. 12, pp. 15866–15875, Dec. 2023.

YANG et al.: GNN-ENHANCED TRAFFIC ANOMALY DETECTION FOR NEXT-GENERATION SDN-ENABLED CE

[28] Y. Huang, J. Gou, Z. Fan, Y. Liao, and Y. Zhuang, “A multi-label network attack detection approach based on two-stage model fusion,” J. Inf.
Secur. Appl., vol. 83, Jun. 2024, Art. no. 103790. [Online]. Available:
https://www.sciencedirect.com/science/article/pii/S2214212624000930
[29] L. Nie, Z. Ning, X. Wang, X. Hu, J. Cheng, and Y. Li, “Datadriven intrusion detection for intelligent Internet of Vehicles: A deep
convolutional neural network-based method,” IEEE Trans. Netw. Sci.
Eng., vol. 7, no. 4, pp. 2219–2230, Oct. 2020.
[30] G. Almahadin et al., “VANET network traffic anomaly detection using
GRU-based deep learning model,” IEEE Trans. Consum. Electron.,
vol. 70, no. 1, pp. 4548–4555, Feb. 2024.
[31] D. Javeed, M. S. Saeed, I. Ahmad, P. Kumar, A. Jolfaei, and M. Tahir,
“An intelligent intrusion detection system for smart consumer electronics
network,” IEEE Trans. Consum. Electron., vol. 69, no. 4, pp. 906–913,
Nov. 2023.
[32] X. Deng, J. Zhu, X. Pei, L. Zhang, Z. Ling, and K. Xue, “Flow
topology-based graph convolutional network for intrusion detection
in label-limited IoT networks,” IEEE Trans. Netw. Service Manage.,
vol. 20, no. 1, pp. 684–696, Mar. 2023.
[33] L. Chang and P. Branco, “Embedding residuals in graph-based solutions:
The E-ResSAGE and E-ResGAT algorithms. A case study in intrusion
detection,” Appl. Intell., vol. 54, no. 8, pp. 6025–6040, Apr. 2024.
[34] D. Pujol-Perich, J. Suarez-Varela, A. Cabellos-Aparicio, and
P. Barlet-Ros, “Unveiling the potential of graph neural networks
for robust intrusion detection,” ACM SIGMETRICS Perform. Eval. Rev.,
vol. 49, no. 4, pp. 111–117, Jun. 2022.
[35] P. Golchin, N. Rafiee, M. Hajizadeh, A. Khalil, R. Kundel, and
R. Steinmetz, “SSCL-IDS: Enhancing generalization of intrusion detection with self-supervised contrastive learning,” in Proc. IFIP Netw. Conf.
(IFIP Netw.), Jun. 2024, pp. 404–412.
[36] L. Li, Y. Lu, G. Yang, and X. Yan, “End-to-end network intrusion
detection based on contrastive learning,” Sensors, vol. 24, no. 7,
p. 2122, Mar. 2024. [Online]. Available: https://www.mdpi.com/14248220/24/7/2122
[37] T. Chen, S. Kornblith, M. Norouzi, and G. E. Hinton, “A simple
framework for contrastive learning of visual representations,” in Proc.
37th Int. Conf. Mach. Learn., vol. 119, 2020, pp. 1597–1607. [Online].
Available: https://proceedings.mlr.press/v119/chen20j.html
[38] Z. Zeng, B. Zhao, H.-C. Chao, I. You, K.-H. Yeh, and W. Meng,
“Towards intelligent attack detection using DNA computing,” ACM
Trans. Multimedia Comput., Commun., Appl., vol. 19, no. 3s, pp. 1–27,
Feb. 2023, doi: 10.1145/3561057.
[39] D.-H. Tran and M. Park, “FN-GNN: A novel graph embedding approach
for enhancing graph neural networks in network intrusion detection
systems,” Appl. Sci., vol. 14, no. 16, p. 6932, Aug. 2024. [Online].
Available: https://www.mdpi.com/2076-3417/14/16/6932
[40] A. Islam, H. Karimipour, and T. R. Gadekallu, “An explainable AutoMLdriven meta-learning scheme for intrusion prevention in zero-touch
networks within carbon intelligent IIoT,” IEEE Internet Things J.,
vol. 12, no. 17, pp. 34731–34742, Sep. 2025.
[41] M. Fu, P. Wang, S. Liu, X. Chen, and X. Zhou, “FIR-GNN: A
graph neural network using flow interaction relationships for intrusion
detection of consumer electronics in smart home network,” IEEE Trans.
Consum. Electron., vol. 71, no. 2, pp. 4892–4902, May 2025.
[42] X. Pei, J. Song, Q. Yang, S. Tian, L. Yu, and G. Chen, “Edge
intelligence-enabled network intrusion detection in compute first networking,” IEEE Trans. Consum. Electron., early access, Aug. 5, 2025,
doi: 10.1109/TCE.2025.3595881.
[43] G.-Y. Yang, J.-N. Chen, F. Wang, and K.-H. Yeh, “Enhancing
resilience for IoE: A perspective of networking-level safeguard,” 2025,
arXiv:2508.20504.
[44] A.-M. Konsta, A. L. Lafuente, B. Spiga, and N. Dragoni, “Survey:
Automatic generation of attack trees and attack graphs,” Comput. Secur.,
vol. 137, Mar. 2023, Art. no. 103602.
[45] B. Wang and N. Z. Gong, “Attacking graph-based classification via
manipulating the graph structure,” in Proc. 26th ACM SIGSAC Conf.
Comput. Commun. Security (CCS), London, U.K., 2019, pp. 2023–2040.
[46] K. Durkota, V. Lisý, B. Bošanský, and C. Kiekintveld, “Optimal network
security hardening using attack graph games,” in Proc. IJCAI, 2015,
pp. 7–14.
[47] A. Presekal, A. Ştefanov, V. S. Rajkumar, and P. Palensky, “Attack
graph model for cyber-physical power systems using hybrid deep
learning,” IEEE Trans. Smart Grid, vol. 14, no. 5, pp. 4007–4020,
Sep. 2023.

10985

[48] X. Ou, S. Govindavajhala, and A. W. Appel, “Mulval: A logic-based
network security analyzer,” in Proc. 14th Conf. USENIX Secur. Symp.,
2005, pp. 113–128.
[49] I. Sharafaldin, A. H. Lashkari, and A. A. Ghorbani, “Toward generating
a new intrusion detection dataset and intrusion traffic characterization,”
in Proc. ICISSp, vol. 1, 2018, pp. 108–116.

Guan-Yan Yang (Graduate Student Member, IEEE)
received the bachelor’s degree from the Department
of Information Management, National Dong Hwa
University, Hualien, Taiwan, in 2022. He is currently
pursuing the Ph.D. degree with the Department of
Electrical Engineering, National Taiwan University,
Taipei, Taiwan. In 2023, he was a Software Engineer at the Design Technology Platform, Research
and Development Division, Taiwan Semiconductor
Manufacturing Company. Since 2024, he has been
a Researcher at Taiwan Academic Cybersecurity
Center and the Institute of Information Science, Academia Sinica, Taiwan.
His research interests include security, safety, deep learning, generative AI,
the Internet of Things, formal verification, and software testing. He is a
member of the IEEE Computer Society, the IEEE Reliability Society, the
IEEE Communication Society, the IEEE Consumer Technology Society, and
SEAT. In 2024, he received a scholarship from the Norman and Lina Chang
Foundation, USA. In 2024, he was awarded the Graduate Research Fellowship
from the National Science and Technology Council in the information security
category. Additionally, he won the 7th and Taiwan Star Award (First Place in
Taiwan) in the World Security Competition HITCON CTF.

Farn Wang (Member, IEEE) received the B.S.
degree in electrical engineering from National
Taiwan University in 1982, the M.S. degree in
computer engineering from National Chiao-Tung
University in 1984, and the Ph.D. degree in computer
science from The University of Texas at Austin
in 1993. He is currently a Full Professor with
the Department of Electrical Engineering, National
Taiwan University. His research interests include formal verification, model-checking, software testing,
security, verification automation, AI, and language
models. He is a Founding Member and the Chairperson of the Steering
Committee of the International Symposium on Automated Technology for
Verification and Analysis (ATVA) from 2003 to 2022. He has served on
the ATVA Advisory Committee since 2022. He was an Associate Editor of
International Journal on Formal Methods in System Design (FMSD, SpringerVerlag). He has been named as the World’s Top 2% Scientists in a career-long
list by Stanford University since 2020.

Kuo-Hui Yeh (Senior Member, IEEE) received
the M.S. and Ph.D. degrees in information management from the National Taiwan University of
Science and Technology, Taipei, Taiwan, in 2005 and
2010, respectively. He is currently a Professor
with the Institute of Artificial Intelligence Innovation, National Yang Ming Chiao Tung University,
Hsinchu, Taiwan. Prior to this appointment, he was
a Professor at the Department of Information Management, National Dong Hwa University, Hualien,
Taiwan, from February 2012 to January 2024. He has
contributed over 150 articles to esteemed journals and conferences, covering
a wide array of research interests, such as the IoT security, blockchain,
NFC/RFID security, authentication, digital signatures, data privacy, and
network security. Furthermore, he plays a pivotal role in the academic
community, serving as an Associate Editor (or Editorial Board Member)
for several journals, including Journal of Information Security and Applications (JISA), Human-centric Computing and Information Sciences (HCIS),
Symmetry, Journal of Internet Technology (JIT), and Computers, Materials
and Continua (CMC). In the professional realm, he holds memberships with
ISC2, ISA, ISACA, CAA, and CCISA. His professional qualifications include
certifications, like CISSP, CISM, Security+, ISO 27001/27701/42001 Lead
Auditor, IEC 62443-2-1 Lead Auditor, and ISA/IEC 62443 Cybersecurity
Expert, covering fundamentals, risk assessment, design, and maintenance
specialties.
PAPER_TEXT
