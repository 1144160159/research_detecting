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
# [638] DALAD: Unsupervised Detection of Global and Local Anomalies in Microservice Systems
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
编号：638
题名：DALAD: Unsupervised Detection of Global and Local Anomalies in Microservice Systems
年份：2025
DOI：10.1109/tsc.2025.3649198
来源：IEEE Transactions on Services Computing
PDF：paper/10.1109_TSC.2025.3649198.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：无
相关性：中相关，分数 6
已有代码状态：已下载；intse/DALAD -> source\DALAD

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\638.txt
- 原始字符数：61025
- 本次发送字符数：61025
- 是否截断：False

代码包：
- 仓库：intse/DALAD
  - URL：https://github.com/intse/DALAD
  - 状态：downloaded
  - 本地目录：source\DALAD
  - 顶层结构：ADGS/、README.md、SN_execute.py、TT_execute.py、dataset/、model/、utils/
  - 主要语言：Python:10
  - README 标题：Paper、Dataset、Paper、Dataset、Paper、Dataset
  - README 运行线索：
  - 关键文件：{}
  - 数据集线索：tor

论文正文包开始：
<<<PAPER_TEXT
240

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 1, JANUARY/FEBRUARY 2026

DALAD: Unsupervised Detection of Global and
Local Anomalies in Microservice Systems
Xiangbo Tian , Shi Ying , Tiangang Li , Ting Zhang , and Yong Wang

Abstract—Accurate anomaly detection is crucial for the reliability of microservice systems. However, most existing anomaly detection approaches only detect deviations from the global expected
patterns, while overlooking anomalies that conform to the global
expected patterns but deviate from the local expected patterns. In
this paper, we propose DALAD, a novel distribution-adversariallearning-based anomaly detection approach for microservice systems, which jointly learns the normal and anomalous system
pattern distributions to effectively detect both global and local
anomalies. In detail, DALAD first designs an adversarial data
generation strategy to automatically generate anomalous traces at
a low cost. Then, Distribution-Adversarial-Learning Trace Representation is designed to jointly learn the multivariate-Gaussiandistribution-based vector representations of normal and anomalous traces, which can reflect the difference between traces in a
more fine-grained manner. Finally, it further models the normal
and anomalous system pattern distributions from these vector representations, and detects anomalies by comparing the likelihoods
of traces under these distributions. Experimental results on two
datasets show that DALAD achieves the best anomaly detection
performance while maintaining a competitive computational cost.
Index Terms—Microservice systems, anomaly detection, trace
representation, distribution adversarial learning, graph neural
networks, variational autoencoder.

I. INTRODUCTION
ICROSERVICES architecture is a cloud-native architecture method, which has emerged as the mainstream
method of developing cloud applications [1], [2], [3], [4], [5].
Compared with monolithic architecture, this architecture is composed of a set of services deployed independently on different
machines [2], [6], which ensures the flexibility of software
development and the stability of software operation.
During the operation of microservice systems, anomalies are
inevitable and varied due to their complexity and large scale [7],
[8], [9], [10]. The behavior patterns of microservice systems
can be roughly divided into the global expected patterns and

M

Received 22 November 2024; revised 16 December 2025; accepted 25 December 2025. Date of publication 30 December 2025; date of current version
5 February 2026. This work was supported in part by the National Key R&D
Program of Chinaunder Grant 2022YFB3304300 and in part by the National
Natural Science Foundation Project of China under Grant 62472329 and Grant
62072342. (Corresponding author: Shi Ying.)
Xiangbo Tian, Shi Ying, and Tiangang Li are with the School of Computer Science, Wuhan University, Wuhan 430072, China (e-mail: tianxiangbo@
whu.edu.cn; yingshi@whu.edu.cn; tiangangli@whu.edu.cn).
Ting Zhang and Yong Wang are with the School of Artificial Intelligence,
Wuhan Technology and Business University, Wuhan 430065, China (e-mail:
zhangting@wtbu.edu.cn; wangyong001@wtbu.edu.cn).
Digital Object Identifier 10.1109/TSC.2025.3649198

Fig. 1.

Visualization of traces from the Social Network microservice system.

the local expected patterns. The former refers to the end-to-end
behaviors of the entire system, such as the complete execution
process of a ticket purchase workflow, while the latter represents the behaviors of a specific service, such as the response
time of the payment service in the ticket purchase workflow.
To intuitively illustrate different types of anomalies, we use
a state-of-the-art trace representation approach iTCRL [2] to
map the end-to-end execution sequences of microservice systems into a high-dimensional feature space. This feature space
encodes the operation information and invocation relationships
of microservice systems to achieve semantic representations for
traces. In this space, the relative positions of traces reflect their
similarities in the execution patterns, and traces with similar
execution patterns are close to each other. For better observation,
we further use t-SNE to reduce high-dimensional trace representations. This allows traces with similar features to naturally
cluster in two-dimensional space since t-SNE can preserve the
local structure of high-dimensional feature space and make
distance reflect the similarity between traces. Fig. 1 shows the
visualization of traces from the Social Network microservice
system [11], [12], where green dots denote normal traces, red
crosses represent traces that significantly deviate from the global
expected patterns (global anomalies), and red triangles indicate
traces that conform to the global expected patterns but deviate
from the local expected patterns (local anomalies). These clusters intuitively show the differences in the execution patterns
between traces and provide evidence of how anomalies emerge
at different levels in microservice systems.

1939-1374 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

TIAN et al.: DALAD: UNSUPERVISED DETECTION OF GLOBAL AND LOCAL ANOMALIES IN MICROSERVICE SYSTEMS

Fig. 2.

241

Overview of DALAD.

From Fig. 1, we can observe that anomalies may occur at different levels in microservice systems, ranging from significant
global deviations to subtle local deviations. However, existing
anomaly detection approaches typically model only the global
behavior patterns of microservice systems and detect anomalies
based on deviations from such patterns [13]. Although these
approaches can effectively detect global anomalies, they struggle
to capture local anomalies that only deviate from the local expected patterns. Therefore, it is necessary for anomaly detection
approaches in microservice systems to take both global and local
anomalies into account. Motivated by this, we propose DALAD,
a novel distribution-adversarial-learning-based anomaly detection approach for microservice systems, which jointly learns the
normal and anomalous system pattern distributions to effectively
detect both global and local anomalies.
In detail, an adversarial data generation strategy is first designed to automatically generate anomalous trace data, which
can provide sufficient and various anomalous traces based on
the anomalous system patterns of microservice systems at a low
cost. Then, Distribution-Adversarial-Learning Trace Representation is proposed to jointly learn the multivariate-Gaussiandistribution-based vector representations of normal and anomalous traces, which can reflect the difference between traces in
a more fine-grained manner. Specifically, it integrates a graph
neural network with a variational autoencoder to encode each
trace into a multivariate-Gaussian-distribution-based vector representation, while introducing a distribution adversarial learning
strategy to jointly learn normal and anomalous traces. Unlike single-point vector representations, multivariate-Gaussiandistribution-based vector representations not only preserve the
global features of traces but also capture the richer statistical
and relational patterns between traces, thereby retaining subtle
yet critical differences and providing a more fine-grained trace
representation. Finally, DALAD learns the Gaussian mixture
distributions of normal and anomalous traces from these vector

representations to capture the normal and anomalous system
patterns, and detects anomalies by comparing the likelihoods of
traces under these distributions. Experimental results on two
datasets show that DALAD achieves the best anomaly detection
performance while maintaining a competitive computational
cost. In summary, our contributions are given as follows.
r To our best knowledge, we are the first to use distributions
to represent traces, which can reflect the difference between
traces in a more fine-grained manner.
r We design a novel distribution-adversarial-learning-based
anomaly detection approach, which can effectively detect
both global and local anomalies in microservice systems.
r We conduct extensive experiments on two datasets, and
experimental results show that DALAD achieves the best
anomaly detection performance while maintaining a competitive computational cost.
The rest of the paper is organized as follows. Section II introduces the background and preliminaries of this study. Section III
describes the specific details of our proposed approach. Section IV gives the experimental results and analysis of DALAD.
Section V introduces the related works. Section VI concludes
our work and gives future research directions.
II. BACKGROUND AND PRELIMINARIES
A. Background
Microservice Systems: A microservice system is a largescale distributed system. It allows developers to independently
develop and deploy functional units [10] and complete user
requests through these loosely-coupled functional units. This
design enhances the flexibility and scalability of systems but
introduces complex service interactions, which further increase
operational challenges. In this context, distributed tracing plays
an important role in ensuring the observability of microservice
systems.

242

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 1, JANUARY/FEBRUARY 2026

Distributed Tracing: Distributed tracing aims to capture the
execution path of a user request throughout microservice systems [14]. By assigning a unique trace ID, it can effectively
record the operations, service invocations and time information
throughout the end-to-end execution of a user request. This
design can fully preserve system observability and achieve
effective monitoring for complex microservice systems.
Trace Data: A trace records a complete execution path of a
user request throughout microservice systems [14]. It is composed of many spans. Each span represents a service invocation,
which consists of much key execution information, such as
timestamps, span contexts, span attributes, span events, span
status and invocation relationships [14]. Thus, a trace can be
naturally described as a graph, which forms the basis for applying graph neural networks to trace analysis.
B. Preliminaries
Graph Neural Network (GNN): Graph neural networks can
effectively model graph-structured data, such as social networks and recommendation systems. By iteratively aggregating
information from neighboring nodes, it can effectively learn
low-dimensional vector representations for nodes or graphs,
which makes it particularly suitable for modeling trace data.
Popular graph neural network architectures contain Graph Convolutional Network [15], Graph Attention Network [16], and
Heterogeneous Attention Network [17], etc.
Variational Autoencoder (VAE): A variational autoencoder
is a generative model that learns a latent probabilistic representation by mapping input data to a latent distribution [18].
It is composed of an encoder and a decoder. The former maps
input data to a latent distribution, while the latter reconstructs the
original input data from the latent distribution. It can effectively
capture the complex data distribution characteristics, which
makes it particularly suitable for the fine-grained representation
learning of traces.
Gaussian Mixture Model (GMM): A Gaussian mixture model
is a probabilistic model that represents a distribution as a
weighted combination of multiple Gaussian components. Each
Gaussian component is defined by a mean vector and a standard
deviation vector. It can effectively model complex multimodal
distributions, which makes it particularly suitable for the finegrained learning of system patterns.
III. APPROACH
The objective of DALAD is to accurately detect both global
and local anomalies in microservice systems. This approach
takes trace data as input and jointly learns the Gaussian mixture
distributions of normal and anomalous traces to capture the
normal and anomalous system patterns. During inference, it
calculates and compares the likelihoods of an unseen trace under
these distributions to determine whether it is anomalous.
The overview of DALAD is shown in Fig. 2, which consists
of three components. Adversarial Data Generation Strategy
(ADGS) automatically produces anomalous traces according
to the anomalous system patterns of microservice systems.
Distribution-Adversarial-Learning Trace Representation

(DALTR) jointly learns the multivariate-Gaussian-distributionbased vector representations of each normal trace and its
corresponding anomalous trace. Distribution-Comparison
Anomaly Detection (DCAD) learns the Gaussian mixture distributions of normal and anomalous traces from these vector
representations, and detects anomalies by comparing the likelihoods of traces under these distributions.
A. Adversarial Data Generation Strategy
In microservice systems, trace data consists of much useful
information, such as span events, span attributes and timestamps [2]. The information is very helpful for the anomaly
detection task of microservice systems. However, most existing
research only considers service invocation relationships but
ignores the fine-grained execution information. To make full
use of this information, we transform trace data into ServiceEvent-based Trace Graphs (SETGs) following [2]. The specific
process consists of four steps:
r Trace Data Preprocessing: We extract Service Runtime
Events (SREs), Service Invocation Events (SIEs) from
traces, and calculate Service Event Metrics (SEMs) based
on the span information.
r Span Data Parsing: We extract the constant templates
and variable templates from Service Runtime/Invocation
Events using the Drain algorithm [19], and divide Service Event Metrics into Service Event Runtime Metrics
(SERMs) and Service Event Invocation Metrics (SEIMs)
according to their meaning and effects.
r Vector Representation: For Service Event Runtime/ Invocation Metrics, we directly transform them into vector
representations, where each dimension represents a metric.
For Service Runtime/Invocation Events, their templates are
embedded as vector representations using GloVe [20] with
TF-IDF [21].
r Graph Construction: We build a graph for each trace
where nodes represent Service Runtime/Invocation Events
described by their vectors, and edges denote the invocation
relationships between service events.
The detailed definitions and processes strictly follow [2].
During the operation of microservice systems, anomalies are
inevitable [9]. Among these anomalies, some deviate from the
global expected patterns while others only deviate from the
local expected patterns. To address this problem, DALAD simultaneously models normal and anomalous system behaviors.
However, the cost of obtaining anomalous traces is very high.
Therefore, we analyze the anomalous system patterns of industrial microservice systems and design Adversarial Data Generation Strategy (ADGS) to automatically generate anomalous
traces. The specific generation process is given by the following
equations.
GtN = T1 (Gt )

(1)

GtA = T2 (Gt )

(2)

where Gt is the SETG of trace t; GtN and GtA represent the normal
and anomalous SETGs corresponding to trace t, respectively;

TIAN et al.: DALAD: UNSUPERVISED DETECTION OF GLOBAL AND LOCAL ANOMALIES IN MICROSERVICE SYSTEMS

T1 (·) is the normal trace generation operation, which is the identity transformation in this paper; T2 (·) denotes the anomalous
trace generation operation, which simulates five types of anomalies in industrial microservice systems, as described below.
r Operation Anomaly: Randomly change the attributes of a
certain proportion of span events in a trace, including event
type (EventType), event label (EventLabel) and event parameters, to simulate inconsistencies in service execution
events.
r Service Metric Anomaly: Randomly change the timestamp
information of a certain proportion of traces to modify
the service-level metrics derived from traces, including
throughput, response time and error rate, to simulate degraded or anomalous service performance.
r Invocation Metric Anomaly: Randomly change a certain
proportion of inter-service invocation attributes, including
invocation latency and success rate, to simulate degraded
or failed service invocations.
r Operation Sequence Anomaly: Randomly swap the execution order of a certain proportion of span events, including
ParentSpanID, SpanID and startTime, to simulate incorrect
execution sequences.
r Invocation Interruption Anomaly: Randomly remove a certain proportion of invocation relationships and all downstream span events in a trace to simulate the interruption
of service invocation chains.
The modification proportions are determined according to the
granularity and structural impact of different anomaly types.
Operation Anomalies directly perturb fine-grained execution
attributes of span events and an excessively high proportion
may severely distort the execution semantics. Therefore, the
modification proportion for them is set to 0.1. In contrast, other
anomalies mainly affect service-level behaviors or structural
attributes. For them, a proportion of 0.2 is adopted to ensure that
anomalous patterns are sufficiently observable while preserving
the overall structure. By the above strategy, we can generate
different anomalous traces for each normal trace, which can
provide sufficient and various anomalous traces at a low cost.
B. Distribution-Adversarial-Learning Trace Representation
After transforming traces into SETGs, we need to represent them by low-dimensional vectors to facilitate the subsequent anomaly detection task. To reflect the difference between traces in a more fine-grained manner, DistributionAdversarial-Learning Trace Representation (DALTR) is designed to jointly learn the multivariate-Gaussian-distributionbased vector representations of each normal trace and its corresponding anomalous trace. In detail, it consists of Heterogeneous Node-edge-aggregated Trace Encoder (HNTE) and
Adversarial Variational Autoencoder (AVAE). Among them,
HNTE is used to aggregate the operation and invocation information of traces, and AVAE is used to jointly learn the
multivariate-Gaussian-distribution-based vector representations
of traces.
1) Heterogeneous Node-Edge-Aggregated Trace Encoder:
HNTE is used to aggregate the operation and invocation

243

information of traces and get their single-point vector representations. It consists of five steps: Trace Content Initialization,
Trace Content Transformation, Neighborhood Aggregation,
Node Content Update and Trace Graph Pooling.
Trace Content Initialization aims to integrate the diverse
attributes of nodes in SETGs to facilitate downstream feature
extraction and analysis. Since each node contains multiple attributes with different semantic meanings, an attribute-based
fusion operation is applied for each node, which is shown by
the following equation.
(0)

hi

= tanh (WI [Xi,0 Xi,1  · · · Xi,n ] + bI )

(3)

(0)

where hi is the initialized feature vector of node i; WI
and bI represent the learnable weight matrix and bias matrix,
respectively;  is the concatenation operation; Xi,k denotes the
k-th attribute feature vector of node i; n represents the attribute
number of node i. In SETGs, edges are described by both types
and attributes, which record different useful information. For
edge types, a type-mapping operation is used to map edge types
to feature vectors, which is given by the following equation.
(0)

Aji = LeakyReLU(q(Aji ))

(4)

(0)

where Aji is the initialized feature vector of the edge type
from node j to node i; Aji denotes the edge type from node j to
node i; q(·) represents a learnable feature dictionary. For edge
attributes, the input attribute feature vector is directly used as
the initialized edge attribute feature vector, which is given by
the following equation.
(0)

Eji = Eji

(5)

(0)

where Eji represents the initialized edge attribute feature vector
from node j to node i; Eji denotes the input edge attribute feature
vector from node j to node i.
Trace Content Transformation aims to project trace content
into a new feature space to extract useful features and enhance
feature expression capability. For nodes, a node-type-specific
linear transformation is applied to project different types of
nodes into the same feature space. The specific transformation
process of nodes is shown by the following equation.
(l+1)

hi

(l+1) (l)

(l+1)

= Wϕ(i) hi + bϕ(i)

(6)

(l+1)

where hi
is the projected feature vector of node i in layer
(l+1)
(l+1)
l + 1; Wϕ(i) and bϕ(i) are the learnable weight matrix and
bias matrix in layer l + 1, respectively; ϕ(i) represents the type
of node i. For edges, two linear transformations are applied for
their type feature vector and attribute feature vector, respectively.
The specific transformation process of edges is given by the
following equations.
(l+1)

= LeakyReLU(WA

(l+1)

= LeakyReLU(WE

Aji

Eji

(l+1)

(l+1)

(l+1)

(l+1)

(l)

(l+1)

)

(7)

(l)

(l+1)

)

(8)

Aji + bA
Eji + bE

and Eji
are the projected edge type feature
where Aji
vector and edge attribute feature vector from node j to node i in

244

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 1, JANUARY/FEBRUARY 2026

(l+1)

(l+1)

layer l + 1, respectively; WA
and WE
are two learnable
(l+1)
(l+1)
and bE
denote two
weight matrixes in layer l + 1; bA
learnable bias matrixes in layer l + 1.
Neighborhood Aggregation aims to integrate the operation
and invocation information from neighboring nodes. In the
aggregation process, the multi-head attention mechanism [22]
is used to stabilize the attention learning process and enrich
the model capacity [16]. In detail, the aggregation message is
first calculated by fusing the neighbor feature vector, edge type
feature vector and edge attribute feature vector. The specific
message calculation process is shown by the following equation.


(l+1,m)
(l+1,m)
(l+1)
(l+1)
(l+1)
(l+1,m)
hj
+ bM
= WM
Aji Eji
mji
(9)
(l+1,m)

where mji

is the aggregation message from node j to node
(l+1,m)

(l+1,m)

i in m-th head of layer l + 1; WM
and bM
denote the
learnable weight matrix and bias matrix in m-th head of layer
l + 1, respectively. Then, the normalized importance weight for
each neighboring node is calculated based on the node feature
vector, neighbor feature vector, edge type feature vector and
edge attribute feature vector to reflect the different importance of
neighboring node. The specific normalization process is shown
by the following equations.
(l+1,m)

oji

(l+1,m)

= LeakyReLU(WO
(l+1)

· [hi
(l+1,m)

αji

(l+1)

hj

(l+1,m)

=

exp(oji

(l+1)

Aji

(l+1)

Eji

)

(l+1,m)
)
k∈ε(i) exp(oki

(l+1,m)

])

(10)
(11)

(l+1,m)

and αji
are the importance weight and
where oji
normalized weight from node j to node i in m-th head of layer
(l+1,m)
represents the learnable weight
l + 1, respectively. WO
matrix; ε(i) denotes the neighborhood set of node i. Finally, we
perform the weighted summation on all aggregation message by
the following equation.
 (l+1,m)
(l+1,m)
(l+1,m)
=
αji
× mji
(12)
hi
j∈ε(i)
(l+1,m)

where hi
is the neighborhood aggregation result of node
i in m-th head of layer l + 1.
Node Content Update aims to concatenate the neighborhood
aggregation results of M attention heads of node i, and update
the feature vector of node i in layer l + 1 based on shortcuts [23].
The specific update process is given by the following equation.
(l+1)

hi
(l+1)

(l)

M

(l+1,m)

= hi +  hi
m=1

(13)

is the feature vector of node i in layer l + 1.
where hi
Trace Graph Pooling aims to calculate the single-point vector representations of traces based on the feature vectors of all
nodes in traces. In this process, the attention pooling is used to
reflect the different importance of nodes. The specific pooling

process is given by the following equation.



(L)
(0)
tanh Wg [hi hi ] + bg
Ht =
i∈V (t)



(L)
(0)
 tanh Wp [hi hi ] + bp

(14)

where Ht is the single-point vector representation of trace t;
Wg and Wp represent the learnable weight matrixes; bg and
bp denote the learnable bias matrixes; V (t) is the node set of
trace t.
2) Adversarial Variational Autoencoder: Although singlepoint vector representations can effectively capture the global
characteristics of a trace, they fail to model uncertainty and
feature correlations. Thus, AVAE is designed to jointly learn the
multivariate-Gaussian-distribution-based vector representations
of normal and anomalous traces from their single-point vector
representations. It consists of three steps: Trace Distribution
Encoder, Trace Distribution Decoder and Trace Adversarial
Loss.
Trace Distribution Encoder aims to learn the hidden multivariate Gaussian distributions of traces. First, the variational
net f (·) is used to learn the hidden feature vector zφt of trace t,
which is shown by the following equation.
zφt = f (Ht )

(15)

where f (·) is a multilayer perceptron. Then, the mean vector μt
and standard deviation vector σ t of trace t are calculated by the
following equations.
μt = Wμ zφt + bμ

(16)

σ t = Wσ zφt + bσ

(17)

where Wμ and Wσ are two learnable weight matrixes; bμ and
bσ are two learnable bias matrixes. Finally, the mean vector
μt and standard deviation vector σ t of trace t are concatenated
to get the multivariate-Gaussian-distribution-based vector representation Zt of trace t, which is given by the following equation.
Zt = μt σ t

(18)

Trace Distribution Decoder aims to reconstruct the singlepoint vector representations of traces from their hidden multivariate Gaussian distributions. First, the hidden single-point
vector representation zθt of trace t is sampled from its hidden
multivariate Gaussian distribution N (μt , σ 2t ) by the following
equation.
zθt = μt + σ t × 

(19)

where  is the value sampled from N (0, 1). Then, the generative
net g(·) is used to get the reconstructed single-point vector
representation Ĥt of trace t by the following equation.
Ĥt = g(zθt )

(20)

where g(·) denotes a multilayer perceptron.
Trace Adversarial Loss aims to achieve joint learning of
normal and anomalous traces. In the joint learning process, the
reconstruction loss should be as small as possible, while the

TIAN et al.: DALAD: UNSUPERVISED DETECTION OF GLOBAL AND LOCAL ANOMALIES IN MICROSERVICE SYSTEMS

245

hidden distribution should be as close to the normal distribution
as possible. Therefore, the reconstruction loss LN and LA of
normal and anomalous traces are defined as follows.


1 
MSE Ht,N , Ĥt,N
LN =
|T |
t∈T

+ KL N (μt,N , σ 2t,N ), N (0, 1)
(21)



1 
MSE Ht,A , Ĥt,A
LA =
|T |
t∈T

+ KL N (μt,A , σ 2t,A ), N (0, 1)
(22)
where T is the trace set; MSE(·, ·) represents the mean-square
error; KL(·, ·) denotes the Kullback-Leibler divergence; Ht,N
and Ht,A represent the single-point vector representations of
normal trace t and its corresponding anomalous trace, respectively; Ĥt,N and Ĥt,A are the reconstructed single-point vector
representations of normal trace t and its corresponding anomalous trace, respectively; N (μt,N , σ 2t,N ) and N (μt,A , σ 2t,A ) are
the hidden distributions of normal trace t and its corresponding
anomalous trace, respectively. Besides, the difference between
the hidden distributions of normal and anomalous traces should
be as large as possible to distinguish them as much as possible.
Therefore, the adversarial loss LC is defined as follows.


2 
t∈T μt,N
t∈T σ t,N
,
,
LC = KL N
|T |
|T |


2 
μ
σ
t,A
t,A
t∈T
t∈T
N
,
(23)
|T |
|T |
Finally, integrating these three loss, the trace adversarial loss L
is designed as follows.
L=

λ
LN + L A
+
βLC
2

Nl


W(l) 2F

(24)

l=1

where λ is the regularization coefficient; β represents the weight
of adversarial loss LC ; Nl denotes the weight matrix number
of DALTR model; W(l) represents the l-th weight matrix of
DALTR model.

Fig. 3.

SETG of the normal trace t.

each Gaussian component; ωkN and ωkA denote the weight of
the k-th Gaussian component in two GMMs, respectively; K
represents the number of Gaussian component in two GMMs;
N
A
A
N (Zt,N |μN
k , Σk ) and N (Zt,A |μk , Σk ) are the probability density functions of the k-th Gaussian component in two GMMs,
respectively. Then, the Expectation-Maximization algorithm is
used to estimate the parameters ΘN and ΘA of two GMMs,
respectively. Finally, DALAD quantifies the severity of anomalies by comparing the log-likelihood values of traces under
normal and anomalous Gaussian mixture distributions, thereby
providing a reference for alarm prioritization. Given a trace t,
its anomalous severity score S(t) is calculated by the following
equations.
log PN (Zt |ΘN ) = log

K


ωkN × N




N
Zt |μN
k , Σk

k=1

log PA (Zt |ΘA ) = log

K


ωkA × N



(26)


A
Zt |μA
k , Σk

(27)

k=1

S(t) = log PA (Zt |ΘA ) − log PN (Zt |ΘN ) (28)
where S(t) ≥ 0 represents anomalous, S(t) < 0 denotes normal, and the larger the value of S(t), the more severe the
anomaly.

C. Distribution-Comparison Anomaly Detection
In microservice systems, each normal trace can be regarded
as a sample drawn from the normal system pattern distribution,
while each anomalous trace corresponds to a sample drawn from
the anomalous system pattern distribution. Therefore, the normal
and anomalous system pattern distributions can be modeled
using the vector representations of normal and anomalous traces.
First, two GMMs are used to model the normal and anomalous
system pattern distributions by the following equations.
⎧

K
N
⎨PN (Zt,N |ΘN ) = k=1 ωkN × N Zt,N |μN
k , Σk
(25)

K
⎩
A
A
A
PA (Zt,A |ΘA ) = k=1 ωk × N Zt,A |μk , Σk
where ΘN and ΘA are the parameter set of two GMMs,
which consist of the weight, mean and covariance matrix of

D. Running Example
To clearly illustrate the workflow of DALAD across all
its components (ADGS, DALTR and DCAD), we construct a
running example, including a normal trace. Table I shows the
original data of this running example.
During training, given a normal trace t, ADGS first transforms
it into a SETG, shown in Fig. 3, where green and gray rectangles
denote SIEs and SREs, respectively, and the elements in them
represent their three attributes.
Based on this graph, ADGS randomly selects one of the predefined anomalous trace generation operations and applies it to
generate an anomalous trace. Suppose the selected operation
is Operation Anomaly, an anomalous trace t is generated, as
shown in Fig. 4.

246

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 1, JANUARY/FEBRUARY 2026

TABLE I
ORIGINAL DATA OF A RUNNING EXAMPLE

TABLE II
DETAILS OF DATASETS

Fig. 4.

SETG of the anomalous trace t .

Then, DALTR takes the SETGs of the normal trace t and
anomalous trace t as input, and jointly learns their multivariateGaussian-distribution-based vector representations Zt and Zt .
Finally, DCAD employs GMMs to model the normal and anomalous system pattern distributions based on Zt and Zt .
During inference, an unseen trace is first transformed into
a SETG as described above. Then, this SETG is input into the
trained DALTR to obtain its multivariate-Gaussian-distributionbased vector representation. Finally, this vector representation
is input into the trained DCAD to calculate its anomaly severity
score based on its likelihoods under the normal and anomalous
system pattern distributions, and determine whether it is anomalous.
IV. EVALUATION
We implement DALAD using Python 3.7, PyTorch 1.11.0
and PyTorch Geometric 2.1.0. Based on this implementation,
we conduct extensive experiments to answer the following questions.
r RQ1: How effective is DALAD in microservice anomaly
detection compared with baselines?
r RQ2: What is the computational cost of DALAD in microservice anomaly detection compared with baselines?
r RQ3: How much does ADGS contribute to DALAD?
r RQ4: How much does hyperparameter configuration affect
the effectiveness of DALAD?
A. Experimental Setup
1) Datasets: Experiments are conducted on two datasets.
One is collected from the Train Ticket microservice system that

has been widely used in many studies [6], [8], [11], [24], [25].
The other is a public dataset provided by [11]. The details of
these two datasets are shown in Table II.
r TT: This dataset is collected from the Train Ticket microservice system with 45 microservices [6], [8], [11], [24],
[25]. We deploy this microservice system on a Kubernetes
cluster composed of 6 machines with Intel Core i7-4790
3.60 GHz CPU and 8 GB RAM, and collect 151911
normal traces and 15138 anomalous traces (containing
Code Defect, Incorrect Configuration, CPU Exhaustion
and Network Jam).
r SN: This dataset is provided by [11], which is collected
from the Social Network microservice system with 21
microservices [12]. It consists of 13612 normal traces
and 1106 anomalous traces (containing CPU Exhaustion,
Network Jam and Network Loss).
2) Baselines: To evaluate DALAD, five anomaly detection
approaches are selected as baselines.
r DeepLog [26]: A log-based anomaly detection approach,
which adopts an LSTM model to learn the normal sequential patterns of log events, and detects anomalies by
predicting the next log event.
r LogAnomaly [27]: A log-based anomaly detection approach, which adopts an LSTM model to learn the normal
sequential patterns and quantitative patterns of log events,
and detects anomalies by predicting the next log event.
r TraceAnomaly [28]: A trace-based anomaly detection approach, which combines STV with a VAE with posterior
flow to learn the normal system patterns from traces, and
detects anomalies by identifying the traces that deviate
from these patterns.

TIAN et al.: DALAD: UNSUPERVISED DETECTION OF GLOBAL AND LOCAL ANOMALIES IN MICROSERVICE SYSTEMS

247

TABLE III
EFFECTIVENESS EVALUATION RESULTS OF DIFFERENT APPROACHES

r DeepTraLog [6]: A multimodal data-based anomaly detection approach, which combines GGNNs and deep SVDD to
learn the normal system patterns from traces and logs, and
detects anomalies by identifying the behaviors that deviate
from these patterns.
r iTCRL-LOF [2]: A trace-based anomaly detection approach, which combines iTCRL with the LOF algorithm
to learn the normal system patterns from traces, and detect
anomalies by identifying the traces that deviate from these
patterns.
3) Evaluation Metrics: To evaluate the effectiveness of
DALAD, we use the following three evaluation metrics.
r Precision: The proportion of the real anomalous traces over
all traces detected as anomalies, which is calculated as:
TP
, where TP is the number of anomalous
Precision = TP+FP
traces detected as anomalies, and FP represents the number
of normal traces detected as anomalies.
r Recall: The proportion of the real anomalous traces detected as anomalies over all anomalous traces, which is calTP
, where FN denotes the number
culated as: Recall = TP+FN
of anomalous traces detected as normal.
r F1-Score: The harmonic mean of Precision and Recall,
which is calculated as: F1-Score = 2×Precision×Recall
Precision+Recall .
To evaluate the computational cost of DALAD, we use the
following five evaluation metrics.
r #Params: The total number of trainable parameters in
models.
r Train Time: The total time required to train models on the
training set.
r Infer Time: The total time required to perform inference on
the testing set.
r Train Mem: The peak GPU memory usage during training
on the training set.
r Infer Mem: The peak GPU memory usage during inference
on the testing set.
4) Settings: All experiments are conducted on a server with
an Intel Core i7-12700 2.10 GHz CPU, 64 GB RAM, RTX 4080
with 16 GB GPU memory. The settings of DALAD are the
following: the number of Gaussian components K is set to 32,
the embedding size D is set to 32, the number of hidden layers
L is set to 1, the weight of adversarial loss β is set to 1.0, the
learning rate η is set to 10−4 , and the regularization coefficient
λ is set to 10−4 . In experiments, the normal traces are split into
training set, validation set and testing set by the ratio of 8 : 1 : 1,

while all anomalous traces are put into the testing set. To mitigate
the effect of randomness, we repeat all experiments five times
and report the average results. The source code and datasets of
DALAD are available at https://github.com/intse/DALAD.
B. RQ1: Effectiveness of DALAD
Experiments are conducted on two datasets to evaluate the
effectiveness of DALAD. Table III shows the effectiveness evaluation results of different approaches on two datasets. As shown
in Table III, DALAD outperforms all baselines on two datasets.
On the TT dataset, it improves Precision by 10.13% ∼ 100.36%
and F1-Score by 5.03% ∼ 51.54% compared to baselines, while
it is slightly worse than DeepTraLog and iTCRL-LOF in terms
of Recall. On the SN dataset, it improves Precision by 12.32% ∼
99.96% and F1-Score by 5.37% ∼ 54.04% compared to baselines, while it is only worse than iTCRL-LOF in terms of
Recall. The excellent performance of DALAD is attributed to
two reasons. (1) DALAD represents traces using multivariateGaussian-distribution-based vector representations, which not
only preserve the global features of traces but also capture the
richer statistical and relational patterns between traces, thereby
retaining subtle yet critical differences and providing a more
fine-grained trace representation. (2) DALAD jointly learns the
normal and anomalous system pattern distributions and detects
anomalies by comparing the likelihoods of traces under these
distributions, which can effectively detect both global and local
anomalies in microservice systems.
C. RQ2: Computational Cost of DALAD
The computational cost of anomaly detection models is crucial for the anomaly detection task in microservice systems.
Table IV shows the computational cost evaluation results of
different approaches on two datasets. As shown in Table IV,
DALAD shows superior efficiency and resource usage on both
datasets. On the TT dataset, the training time of DALAD
(1671.77 s) is only 3.9% of that of LogAnomaly, and its inference time (40.16 s) is also significantly lower than most
baselines. Although the parameter size and training memory
of DALAD are larger than simple baselines, such as DeepLog
and iTCRL-LOF, DALAD achieves better anomaly detection
performance at a lower cost compared to large baselines such
as TraceAnomaly (7.40 M parameters, 13607 MB Memory),
LogAnomaly (0.19 M parameters, 8360 MB memory), and

248

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 1, JANUARY/FEBRUARY 2026

TABLE IV
COMPUTATIONAL COST EVALUATION RESULTS OF DIFFERENT APPROACHES

Fig. 5.

Effectiveness evaluation results under different anomaly coverage.

DeepTraLog (0.81 M parameters, 836 MB memory). On the SN
dataset, DALAD achieves the lowest inference memory (68 MB)
while maintaining competitive training and inference times.
In summary, although DALAD integrates GNN and VAE, its
computational cost is only slightly higher than that of simple
baselines but significantly lower than that of large baselines
by effective network depth controlling, embedding dimension
controlling and mini-batch training strategy. Moreover, the computational cost of DALAD mainly lies in the training stage, and
the inference cost is low, which makes it feasible to be deployed
in large-scale microservice systems. In practical applications,
DALAD can be efficiently trained on a single 16 GB GPU
and further reduce computational cost through mixed-precision
training and neighborhood sampling.

maintaining comparable effectiveness in high-anomalycoverage scenarios. In two datasets, the F1-Score of DALAD
w/o ADGS increases with anomaly coverage, while that of
DALAD remains stable, as it does not rely on real anomalous
traces. When anomaly coverage is lower than 80%, DALAD
significantly outperforms DALAD w/o ADGS, while DALAD
w/o ADGS approaches or even surpasses DALAD when
anomaly coverage exceeds 80%. This phenomenon shows that
ADGS effectively compensates for the lack of anomalous traces
by automatically generating various anomalous traces. This
advantage is particularly critical in real-world scenarios where
anomalous traces are scarce and costly to obtain, which makes
DALAD more applicable and robust in real-world scenarios.
E. RQ4: Sensitivity of Hyperparameter

D. RQ3: Contribution of ADGS
To evaluate the contribution of ADGS to DALAD, we derive
a variant of DALAD by removing ADGS from DALAD, in
which real anomalous traces are used for training. Fig. 5 shows
the effectiveness evaluation results under different anomaly
coverage. As shown in Fig. 5, DALAD significantly outperforms
DALAD w/o ADGS in low-anomaly-coverage scenarios while

The effectiveness of DALAD is affected by six hyperparameters: number of Gaussian components K, embedding size D,
number of hidden layers L, weight of adversarial loss β, learning
rate η, and regularization coefficient λ.
To evaluate the impact of K, experiments are conducted
on two datasets when other hyperparameters are fixed. Fig. 6
shows the impact of hyperparameter K. As shown in Fig. 6, the

TIAN et al.: DALAD: UNSUPERVISED DETECTION OF GLOBAL AND LOCAL ANOMALIES IN MICROSERVICE SYSTEMS

Fig. 6.

Impact of hyperparameter K.

Fig. 8.

Impact of hyperparameter L.

Fig. 7.

Impact of hyperparameter D.

Fig. 9.

Impact of hyperparameter β.

F1-Score of DALAD first increases and then starts to decrease
or stabilize with K, and reaches a relatively high level around
K = 32 on both datasets. This is because DALAD needs a
suitable K to capture the complex data distributions. A smaller
K will lead to underfitting, while a larger K will lead to overfitting. Therefore, the choice of K is crucial to balance model
complexity and generalization performance.
We explore the impact of D on two datasets when other
hyperparameters are fixed. Fig. 7 gives the impact of hyperparameter D. As shown in Fig. 7, the F1-Score of DALAD first
rises and then starts to drop or stabilize with D, and reaches a
relatively high level around D = 32 on both datasets. The reason
is that DALAD relies on an appropriate D to effectively encode
useful information for anomaly detection. A smaller D fails to
fully capture useful features, while a larger D may introduce
redundant information. Therefore, the choice of D must strike
a balance between information preservation and redundancy
control.
We check the impact of L on two datasets when other hyperparameters are fixed. Fig. 8 shows the impact of hyperparameter
L. From Fig. 8, we can see that the F1-Score of DALAD first stabilizes and then starts to decrease with L on the TT dataset while
continuously decreasing on the SN dataset. It reaches a relatively
high F1-Score around L = 1 on both datasets. This is because
DALAD needs a suitable L to learn helpful information for
anomaly detection, and a larger L may lead to over-smoothing.

249

Therefore, the choice of L is crucial to learn useful information
for anomaly detection.
To evaluate the impact of β, experiments are conducted on two
datasets when other hyperparameters are fixed. Fig. 9 gives the
impact of hyperparameter β. As shown in Fig. 9, the F1-Score of
DALAD first increases and then starts to drop with β on the TT
dataset while stabilizing on the SN dataset. It reaches a relatively
high F1-Score around β = 1.0 on both datasets. The reason
is that β is used to control the trade-off between distribution
fitting and normal-anomalous distribution separation. A smaller
β will lead to excessive attention to distribution separation
and reduce distribution fitting, while a larger β will weaken
distribution separation and pay more attention to distribution
fitting. Therefore, the choice of β must strike a balance between
distribution fitting and distribution separation.
We explore the impact of η on two datasets when other
hyperparameters are fixed. Fig. 10 shows the impact of hyperparameter η. As shown in Fig. 10, DALAD achieves a good
performance and shows insensitivity to η on the SN dataset.
On the TT dataset, DALAD performs well when η is small,
but its F1-Score significantly decreases when η > 10−4 , which
indicates that it is highly sensitive to η. It reaches a relatively high
F1-Score around η = 10−4 on both datasets. This is because the
SN dataset has a good distribution and low noise, while the TT
dataset has a complex distribution and more noise. Therefore, the
choice of η is very important for ensuring DALAD convergence.

250

Fig. 10.

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 1, JANUARY/FEBRUARY 2026

Impact of hyperparameter η.

The threats to external validity mainly lie in the experimental
environment. Although DALAD is designed as a model that can
be trained offline and applied in an online inference manner,
all experiments were conducted on two datasets collected from
the widely used benchmark microservice systems, Train Ticket
and Social Network. There is still a potential threat to external
validity since the proposed approach has not yet been integrated
into a real production system. We mitigate this threat from three
aspects. First, these two datasets consist of complex traces with
more than 700 and 150 events, respectively, which are comparable to the hundreds of events typically found in real production
systems [6], [8]. Second, we analyze the typical anomalies in
real production systems and design anomalous cases based on
them, which can ensure that the anomalous scenarios used in
our evaluation are representative. Finally, we plan to collaborate
with a large-scale cloud provider in the future to further validate
our approach.
V. RELATED WORKS

Fig. 11.

Impact of hyperparameter λ.

We check the impact of λ on two datasets when other hyperparameters are fixed. Fig. 11 gives the impact of hyperparameter
λ. From Fig. 11, we can observe that the F1-Score of DALAD
stabilizes on the SN dataset while decreasing with λ on the
TT dataset. DALAD reaches a relatively high F1-Score around
λ = 10−4 on both datasets. The TT dataset has a more complex
distribution and more noise than the SN dataset, which makes the
former more sensitive to regularization than the latter. Therefore,
the choice of λ must strike a balance between distribution fitting
and distribution generalization.
F. Threats to Validity
The threats to internal validity mainly lie in the collection
of normal data and the design of Adversarial Data Generation
Strategy (ADGS). (1) The effectiveness of DALAD is directly
affected by the coverage of normal data since it relies on normal
data for training. If certain types of user requests are missing
from normal data, DALAD may misidentify these missing parts
as anomalies. To mitigate this threat, we simulate various types
of user requests during data collection to ensure the coverage of
normal data. (2) ADGS aims to automatically generate anomalous trace data, which is the basis of DALAD. Therefore, its
quality determines the effectiveness of DALAD. To mitigate this
threat, we carefully design this strategy based on the anomalous
system patterns of industrial microservice systems.

Accurate anomaly detection is crucial for ensuring the reliability of microservice systems. Existing studies use various observability data to detect anomalies and can be divided into four
classes: metric-based anomaly detection approaches, log-based
anomaly detection approaches, trace-based anomaly detection
approaches and multimodal data-based anomaly detection approaches.
Metric-based anomaly detection approaches: These approaches usually detect anomalies by monitoring changes in service metrics. For example, Nedelkoski et al. [29] use an unsupervised deep Bayesian network to capture anomalous changes in
service response time. Li et al. [30] introduce intervention recognition to identify anomalous metrics, while Yu et al. [8] apply the
k-σ rule for the same purpose. Xie et al. [31] further extend this
idea by designing a regression-based latent-space intervention
recognition under limited observability. These approaches are
simple and interpretable, but fail to detect anomalies caused
by code defects or topological dependencies in microservice
systems.
Log-based anomaly detection approaches: These approaches
commonly focus on learning the normal sequential patterns of
log events to detect anomalies as deviations from these patterns.
For instance, Du et al. [26] use an LSTM model to learn the
normal sequential patterns of log events and detect anomalies
by predicting next log events. Meng et al. [27] extend this idea
by also modeling the quantitative patterns of log events. Zhang
et al. [32] represent log events through semantic embeddings
and use an attention-based Bi-LSTM model to detect anomalies.
These approaches are effective in detecting anomalies caused
by code defects. However, they ignore the topological features
of microservice systems, which limits their ability to capture
inter-service dependencies.
Trace-based anomaly detection approaches: These approaches typically leverage traces to learn normal system patterns and detect anomalies. For example, Liu et al. [28] combine
Service Trace Vector with a VAE with posterior flow to learn
the normal system patterns from traces and detect anomalies

TIAN et al.: DALAD: UNSUPERVISED DETECTION OF GLOBAL AND LOCAL ANOMALIES IN MICROSERVICE SYSTEMS

as those traces that deviate significantly from these patterns.
Nedelkoski et al. [33] employ a multi-modal LSTM model to
capture the normal sequential patterns of traces and flag deviations as anomalies. Tian et al. [2] integrate a GNN with causal
intervention to detect anomalies based on data density. These
approaches consider the topological features of microservice
systems and can detect anomalies caused by code defects. However, they cannot detect anomalies that conform to the global
expected patterns but deviate from the local expected patterns.
Multimodal data-based anomaly detection approaches:
These approaches usually integrate multimodal observability
data to capture normal system patterns and detect anomalies.
For example, Zhang et al. [6] combine a GGNN [34] and deep
SVDD [35] to detect anomalies based on the unified graph
representations constructed from traces and logs. Similarly,
Chen et al. [36] integrate a GNN with an LSTM model to learn
the normal system patterns from the unified graphs built using
traces and performance metrics of containers, and flag deviations
as anomalies. By integrating multimodal observability data,
these approaches can detect anomalies reflected in different
observability data. However, they remain limited in detecting
anomalies that conform to the global expected patterns but
deviate from the local expected patterns.
VI. CONCLUSION AND FUTURE WORK
In this paper, we propose DALAD, a novel distributionadversarial-learning-based anomaly detection approach for microservice systems. This approach jointly learns the normal and
anomalous system pattern distributions to effectively detect both
global and local anomalies. Specifically, we first design an adversarial data generation strategy, which can automatically generate
anomalous traces at a low cost. Then, Distribution-AdversarialLearning Trace Representation is proposed to jointly learn the
multivariate-Gaussian-distribution-based vector representations
of normal and anomalous traces, which can not only preserve the
global features of traces but also capture the richer statistical and
relational patterns between traces. Finally, DALAD learns the
normal and anomalous system pattern distributions from these
vector representations, and detects anomalies by comparing the
likelihoods of traces under these distributions. Extensive experiments show that DALAD achieves the best anomaly detection
performance while maintaining competitive computational cost.
Notably, this work is the first to use distributions to represent
traces and overcomes the limitations of existing approaches that
rely solely on modeling the global expected patterns, which can
effectively enable more robust and fine-grained anomaly detection. By jointly modeling the normal and anomalous system
patterns, DALAD can effectively detect both global and local
anomalies in microservice systems. Such capability can help
DevOps managers to promptly detect and handle both global and
local anomalies in microservice systems, thereby significantly
improving system reliability and user satisfaction.
In the future, we will further explore more comprehensive
and universal adversarial data generation strategies to improve
the generalization capability of DALAD. Secondly, we will
cooperate with a large-scale cloud provider to integrate DALAD

251

into real production systems and further validate its practical
effectiveness and usability.
REFERENCES
[1] A. Balalaie, A. Heydarnoori, and P. Jamshidi, “Migrating to cloud-native
architectures using microservices: An experience report,” in Proc. 4th Eur.
Conf. Service-Oriented Cloud Comput., 2015, pp. 201–215.
[2] X. Tian et al., “iTCRL: Causal-intervention-based trace contrastive representation learning for microservice systems,” IEEE Trans. Softw. Eng.,
vol. 50, no. 10, pp. 2583–2601, Oct. 2024.
[3] M. Ma, W. Lin, D. Pan, and P. Wang, “Servicerank: Root cause identification of anomaly in large-scale microservice architectures,” IEEE
Trans. Dependable Secure Comput., vol. 19, no. 5, pp. 3087–3100,
Sep./Oct. 2022.
[4] J. Soldani and A. Brogi, “Anomaly detection and failure root cause analysis
in (micro) service-based cloud applications: A survey,” ACM Comput.
Surverys, vol. 55, no. 3, 2022, Art. no. 59.
[5] Y. Gan, M. Liang, S. Dev, D. Lo, and C. Delimitrou, “Sage: Practical and
scalable ML-driven performance debugging in microservices,” in Proc.
26th ACM Int. Conf. Architectural Support Program. Lang. Operating
Syst., 2021, pp. 135–151.
[6] C. Zhang et al., “Deeptralog: Trace-log combined microservice anomaly
detection through graph-based deep learning,” in Proc. 44th Int. Conf.
Softw. Eng., 2022, pp. 623–634.
[7] S. Gu et al., “TrinityRCL: Multi-granular and code-level root cause localization using multiple types of telemetry data in microservice systems,”
IEEE Trans. Softw. Eng., vol. 49, no. 5, pp. 3071–3088, May 2023.
[8] G. Yu, P. Chen, Y. Li, H. Chen, X. Li, and Z. Zheng, “Nezha: Interpretable
fine-grained root causes analysis for microservices on multi-modal observability data,” in Proc. 31st ACM Joint Eur. Softw. Eng. Conf. Symp.
Foundations Softw. Eng., 2023, pp. 553–565.
[9] L. Wang, N. Zhao, J. Chen, P. Li, W. Zhang, and K. Sui, “Root-cause
metric location for microservice systems via log anomaly detection,” in
Proc. 2020 IEEE Int. Conf. web Serv., 2020, pp. 142–150.
[10] S. Zhang et al., “Robust failure diagnosis of microservice system
through multimodal data,” IEEE Trans. Serv. Comput., vol. 16, no. 6,
pp. 3851–3864, Nov./Dec. 2023.
[11] C. Lee, T. Yang, Z. Chen, Y. Su, and M. R. Lyu, “Eadro: An end-to-end
troubleshooting framework for microservices on multi-source data,” in
Proc. IEEE/ACM 45th Int. Conf. Softw. Eng., 2023, pp. 1750–1762.
[12] Y. Gan et al., “An open-source benchmark suite for microservices and their
hardware-software implications for cloud & edge systems,” in Proc. 24th
Int. Conf. Architectural Support Program. Lang. Operating Syst., 2019,
pp. 3–18.
[13] M. Panahandeh, A. Hamou-Lhadj, M. Hamdaqa, and J. Miller, “Serviceanomaly: An anomaly detection approach in microservices using
distributed traces and profiling metrics,” J. Syst. Softw., vol. 209, 2024,
Art. no. 111917.
[14] Opentelemetry 2025 Accessed, Sep. 20, 2025 [Online]. Available: https:
//opentelemetry.io/
[15] J. Bruna, W. Zaremba, A. Szlam, and Y. LeCun, “Spectral networks and
locally connected networks on graphs,” in Proc. 2nd Int. Conf. Learn.
Representations, 2014.
[16] P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Liò, and Y. Bengio,
“Graph attention networks,” in Proc. 6th Int. Conf. Learn. Representations,
2018.
[17] X. Wang et al., “Heterogeneous graph attention network,” in Proc. 2019
World Wide Web Conf., 2019, pp. 2022–2032.
[18] D. P. Kingma and M. Welling, “Auto-encoding variational bayes,” in Proc.
2nd Int. Conf. Learn. Representationss, 2014.
[19] P. He, J. Zhu, Z. Zheng, and M. R. Lyu, “Drain: An online log parsing
approach with fixed depth tree,” in Proc. 2017 IEEE Int. Conf. Web Serv.,
2017, pp. 33–40.
[20] J. Pennington, R. Socher, and C. D. Manning, “Glove: Global vectors
for word representation,” in Proc. 2014 Conf. Empirical Methods Natural
Lang. Process. , 2014, pp. 1532–1543.
[21] G. Salton and C. Buckley, “Term-weighting approaches in automatic text
retrieval,” Inf. Process. Manage., vol. 24, no. 5, pp. 513–523, 1988.
[22] A. Vaswani et al., “Attention is all you need,” in Proc. 31st Int. Conf.
Neural Inf. Process. Syst., 2017, pp. 6000–6010.
[23] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for image
recognition,” in Proc. 33 rd IEEE Conf. Comput. Vis. Pattern Recognit.,
2016, pp. 770–778.

252

IEEE TRANSACTIONS ON SERVICES COMPUTING, VOL. 19, NO. 1, JANUARY/FEBRUARY 2026

[24] C. Zhang et al., “Tracecrl: Contrastive representation learning for microservice trace analysis,” in Proc. 30th ACM Joint Eur. Softw. Eng. Conf. Symp.
Foundations Softw. Eng., 2022, pp. 1221–1232.
[25] X. Zhou et al., “Fault analysis and debugging of microservice systems:
Industrial survey, benchmark system, and empirical study,” IEEE Trans.
Softw. Eng., vol. 47, no. 2, pp. 243–260, Feb. 2021.
[26] M. Du, F. Li, G. Zheng, and V. Srikumar, “Deeplog: Anomaly detection
and diagnosis from system logs through deep learning,” in Proc. 2017
ACM SIGSAC Conf. Comput. Commun. Secur., 2017, pp. 1285–1298.
[27] W. Meng et al., “Loganomaly: Unsupervised detection of sequential and
quantitative anomalies in unstructured logs,” in Proc. 28th Int. Joint Conf.
Artif. Intell., 2019, pp. 4739–4745.
[28] P. Liu et al., “Unsupervised detection of microservice trace anomalies
through service-level deep bayesian networks,” in Proc. 31st Int. Symp.
Softw. Rel. Eng., 2020, pp. 48–58.
[29] S. Nedelkoski, J. Cardoso, and O. Kao, “Anomaly detection and classification using distributed tracing and deep learning,” in Proc. 19th IEEE/ACM
Int. Symp. Cluster,Cloud Grid Comput., 2019, pp. 241–250.
[30] M. Li et al., “Causal inference-based root cause analysis for online service
systems with intervention recognition,” in Proc. 28th ACM SIGKDD Conf.
Knowl. Discov. Data Mining, 2022, pp. 3230–3240.
[31] Z. Xie et al., “Microservice root cause analysis with limited observability
through intervention recognition in the latent space,” in Proc. 30th ACM
SIGKDD Conf. Knowl. Discov. Data Mining, 2024, pp. 6049–6060.
[32] X. Zhang et al., “Robust log-based anomaly detection on unstable log
data,” in Proc. 27th ACM Joint Meeting Eur. Softw. Eng. Conf. Symp.
Foundations Softw. Eng., 2019, pp. 807–817.
[33] S. Nedelkoski, J. Cardoso, and O. Kao, “Anomaly detection from system
tracing data using multimodal deep learning,” in Proc. 12th Int. Conf.
Cloud Comput., 2019, pp. 179–186.
[34] Y. Li, D. Tarlow, M. Brockschmidt, and R. Zemel, “Gated graph sequence
neural networks,” in Proc. 4th Int. Conf. Learn. Representations, 2016.
[35] L. Ruff et al., “Deep one-class classification,” in Proc. 35th Int. Conf.
Mach. Learn., 2018, pp. 4393–4402.
[36] J. Chen et al., “Tracegra: A trace-based anomaly detection for microservice
using graph deep learning,” Comput. Commun., vol. 204, pp. 109–117,
2023.

Shi Ying is currently a professor with the School of
Computer Science, Wuhan University, Wuhan, China.
His main research interests include software engineering, intelligent operation and maintenance management, cloud computing, cloud service software,
and artificial intelligence.

Xiangbo Tian is currently working toward the PhD
degree with the School of Computer Science, Wuhan
University, Wuhan, China. His current research interests include microservices and AIOps.

Yong Wang is currently an associate professor with
the School of Artificial Intelligence, Wuhan Technology and Business University, Wuhan, China. His research interests include intelligent software engineering, cloud computing, Big Data analysis technology,
and artificial intelligence.

Tiangang Li is currently working toward the PhD
degree in the School of Computer Science, Wuhan
University, Wuhan, China. His research interests include cloud computing, software engineering, resource management, and reinforcement learning.

Ting Zhang is currently an associate professor with
the School of Artificial Intelligence, Wuhan Technology and Business University, Wuhan, China. Her
research interests include intelligent software engineering, data mining, Big Data analysis technology,
and artificial intelligence.
PAPER_TEXT
