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
# [129] Detecting Unknown Encrypted Malicious Traffic in Real Time via Flow Interaction Graph Analysis
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
编号：129
题名：Detecting Unknown Encrypted Malicious Traffic in Real Time via Flow Interaction Graph Analysis
年份：2023
DOI：10.14722/ndss.2023.23080
来源：Proceedings 2023 Network and Distributed System Security Symposium
PDF：paper/10.14722_ndss.2023.23080.pdf
已有粗分类：恶意流量、暗网与攻击检测
二级关联：图学习、知识图谱与威胁情报
相关性：强相关，分数 14
已有代码状态：已下载；HyperVision -> source\HyperVision

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\129.txt
- 原始字符数：113721
- 本次发送字符数：113721
- 是否截断：False

代码包：
- 仓库：HyperVision
  - URL：https://github.com/fuchuanpu/HyperVision
  - 状态：downloaded
  - 本地目录：source\HyperVision
  - 顶层结构：.gitignore、CMakeLists.txt、LICENSE、README.md、common.hpp、configuration/、dataset_construct/、env/、flow_construct/、graph_analyze/、init.sh、main.cpp、option.hpp、packet_parse/、result_analyze/、script/
  - 主要语言：JSON:81、C++ Header:13、C++:13、Shell:9、Python:3
  - README 标题：HyperVision、__0x00__ Hardware、__0x01__ Software、Establish env.、Download dataset.、Build and run HyperVision.、Analyze the results.、__0x02__ Reference、HyperVision、__0x00__ Hardware
  - README 运行线索：bash # Establish env.；sh # Download dataset.；sh ./script/expand.sh；sh && cd ..；bash # Establish env.；sh # Download dataset.；sh ./script/expand.sh；sh && cd ..
  - 关键文件：{"推理/演示入口": ["script/run_all_brute.sh", "script/run_all_lrscan.sh", "script/run_all_malware.sh", "script/run_all_misc.sh", "script/run_all_web.sh"], "配置文件": ["result_analyze/configure.json"]}
  - 数据集线索：ton、tor

论文正文包开始：
<<<PAPER_TEXT
Detecting Unknown Encrypted Malicious Traffic in
Real Time via Flow Interaction Graph Analysis
Chuanpu Fu∗ , Qi Li†‡ , Ke Xu∗‡
∗ Department of Computer Science and Technology, Tsinghua University

arXiv:2301.13686v1 [cs.CR] 31 Jan 2023

† Institute for Network Sciences and Cyberspace, Tsinghua University ‡ Zhongguancun Lab

Abstract—Nowadays traffic on the Internet has been widely
encrypted to protect its confidentiality and privacy. However,
traffic encryption is always abused by attackers to conceal their
malicious behaviors. Since the encrypted malicious traffic has
similar features to benign flows, it can easily evade traditional
detection methods. Particularly, the existing encrypted malicious
traffic detection methods are supervised and they rely on the prior
knowledge of known attacks (e.g., labeled datasets). Detecting
unknown encrypted malicious traffic in real time, which does not
require prior domain knowledge, is still an open problem.
In this paper, we propose HyperVision, a realtime unsupervised machine learning (ML) based malicious traffic detection
system. Particularly, HyperVision is able to detect unknown
patterns of encrypted malicious traffic by utilizing a compact inmemory graph built upon the traffic patterns. The graph captures
flow interaction patterns represented by the graph structural
features, instead of the features of specific known attacks. We develop an unsupervised graph learning method to detect abnormal
interaction patterns by analyzing the connectivity, sparsity, and
statistical features of the graph, which allows HyperVision to detect various encrypted attack traffic without requiring any labeled
datasets of known attacks. Moreover, we establish an information
theory model to demonstrate that the information preserved by
the graph approaches the ideal theoretical bound. We show the
performance of HyperVision by real-world experiments with 92
datasets including 48 attacks with encrypted malicious traffic. The
experimental results illustrate that HyperVision achieves at least
0.92 AUC and 0.86 F1, which significantly outperform the stateof-the-art methods. In particular, more than 50% attacks in our
experiments can evade all these methods. Moreover, HyperVision
achieves at least 80.6 Gb/s detection throughput with the average
detection latency of 0.83s.

I.

I NTRODUCTION

Traffic encryption has been widely adopted to protect the
information delivered on the Internet. Over 80% websites
adopted HTTPS to prevent data breach in 2019 [16], [62].
However, the cipher-suite for such protection is double-edged.
In particular, the encrypted traffic also allows attackers to conceal their malicious behaviors, e.g., malware campaigns [2],
exploiting vulnerabilities [64], and data exfiltration [77]. The
ratio of encrypted malicious traffic on the Internet is growing
significantly [2], [3], [76] and exceeds 70% of the entire
malicious traffic [16].
However, encrypted malicious traffic detection is not well
addressed due to the low-rate and diverse traffic patterns [2],
[39], [77]. The traditional signature based methods that leverage deep packet inspection (DPI) are invalid under the attacks with the encrypted payloads [34]. Table I compares the
Network and Distributed System Security (NDSS) Symposium 2023
27 February - 3 March 2023, San Diego, CA, USA
ISBN 1-891562-83-5
https://dx.doi.org/10.14722/ndss.2023.23080
www.ndss-symposium.org

existing malicious traffic detection methods. Different from
plain-text malicious traffic, the encrypted traffic has similar
features to benign flows and thus can evade existing machine
learning (ML) based detection systems as well [2], [3], [62].
Particularly, the existing encrypted traffic detection methods
are supervised, i.e., relying on the prior knowledge of known
attacks, and can only detect attacks with known traffic patterns.
They extract features of specific known attacks and use labeled
datasets of known malicious traffic for model training [2],
[3], [76]. Thus, they are unable to detect a broad spectrum
of attacks with encrypted traffic [39], [41], [64], [77], which
are constructed with unknown patterns [22]. Besides, these
methods are incapable of detecting both attacks constructed
with and without encrypted traffic and unable to achieve
generic detection because features of encrypted and nonencrypted attack traffic are significantly different [2], [3].
In a nutshell, the existing methods cannot achieve unsupervised detection and they are unable to detect encrypted malicious traffic with unknown patterns. In particular, the encrypted
malicious traffic has stealthy behaviors, which cannot be captured by these methods [2], [76] that detect attacks according
to the patterns of a single flow. However, it is still feasible to
detect such attack traffic because these attacks involve multiple
attack steps with different flow interactions among attackers
and victims, which are distinct from benign flow interactions
patterns [24], [26], [39], [46], [61]. For example, the encrypted
flow interactions between spam bots and SMTP servers are
significantly different from the legitimate communications [61]
even if the single flow of the attack is similar to the benign one.
Thus, this paper explores utilizing interaction patterns among
various flows for malicious traffic detection.
To the end, we propose HyperVision, a realtime detection
system that aims to capture footprints of encrypted malicious
traffic by analyzing interaction patterns among flows. In particular, it can detect encrypted malicious flows with unknown
footprints by identifying abnormal flow interactions, i.e., the
interaction patterns that are distinct from benign ones. To
achieve this, we build a compact graph to capture various
flow interaction patterns so that HyperVision can perform
detection on various encrypted traffic according to the graph.
The graph allows us to detect attacks without accessing packet
payloads, while retaining the ability of detecting traditional
(known) attacks with plain-text traffic. Therefore, HyperVision
can detect the malicious traffic with unknown patterns by
learning the graph structural features. Meanwhile, by learning
the graph structural features, it realizes unsupervised detection,
which does not require model training with labeled datasets.
However, it is challenging to build the graph for realtime
detection. We cannot simply use IP addresses as vertices and
traditional four-tuple of flows [19], [36] as edges to construct
the graph because the resulting dense graph cannot maintain

TABLE I.
Data Source
Categories

Data Sources

Protocol Headers
Encrypted Traffic
Related Flows
Network Logs
Plain-text and
Encrypted Traffic

1

Traffic Features

T HE COMPARISON WITH THE EXISTING METHODS OF MALICIOUS TRAFFIC DETECTION .
Typical Methods
TLS Extensions [16]
HTTPS Headers [3]
Time Series [76]
TLS Handshakes [2]
Flow Statistics [90]
Intrusion Events [20]
Sampled Connections [8]
Per-Packet Features [56]
Per-Flow Features [5]
Flow Interaction Graph

Data for Detection
Design Goals
Detection Performance
Unlabeled Multi-Flow Generic Realtime Unknown
Low
High
Datasets
Features
Detection Detection Attacks Latency Throughput
×
×
×
×
X
X
X
X
×
X

×
×
×
×
×
×
X1
×
×
X

×
×
×
×
×
×
×
×
×
X

×
×
×
×
X
×
X
×
X
X

×
×
×
×
×
X
×
X
×
X

×
×
×
×
×
×
×
X
X
X

X
×
×
×
X
×
X
×
×
X

Existing multi-flow features can only represent the features of specific flows, which cannot be used to represent complicated interaction patterns among various flows.

We prototype HyperVision1 with Intel’s Data Plane Development Kit (DPDK) [37]. To extensively evaluate the
performance of the prototype, we replayed 92 attack datasets
including 80 new datasets collected in our virtual private
cloud (VPC) with more than 1,500 instances. In the VPC, we
collected 48 typical encrypted malicious traffic, including (i)
encrypted flooding traffic, e.g., flooding target links [41]; (ii)
web attacks, e.g., exploiting web vulnerabilities [64]; (iii) malware campaigns, including connectivity testing, dependency
update, and downloading. In the presence of the background
traffic by replaying the backbone network traffic [80], HyperVision achieves 13.9% ∼ 36.1% accuracy improvements over
five state-of-the-art methods. It detects all encrypted malicious
traffic in an unsupervised manner with more than 0.92 AUC,
0.86 F1, where 44 of the real-world stealthy traffic cannot be
identified by all the baselines, e.g., an advanced side-channel
attack exploiting the CVE-2020-36516 [26] and many newly
discovered cryptojacking attacks [7]. Moreover, HyperVision
achieves on average more than 100 Gb/s detection throughput
with the average detection latency of 0.83s.

interaction patterns among various flows, e.g., incurring the
dependence explosion problem [87]. Inspired by the study of
the flow size distribution [25], [84], i.e., most flows on the
Internet are short while most packets are associated with long
flows, we utilize two strategies to record different sizes of
flows, and process the interaction patterns of short and long
flows separately in the graph. Specifically, it aggregates the
short flows based on the similarity of massive short flows
on the Internet, which reduces the density of the graph, and
performs distribution fitting for the long flows, which can
effectively preserve flow interaction information.
We design a four-step lightweight unsupervised graph
learning approach to detect encrypted malicious traffic by
utilizing the rich flow interaction information maintained on
the graph. First, we analyze the connectivity of the graph by
extracting the connected components and identify abnormal
components by clustering the high-level statistical features.
By excluding the benign components, we also significantly
reduce the learning overhead. Second, we pre-cluster the edges
according to the observed local adjacency in edge features.
The pre-clustering operations significantly reduce the feature
processing overhead and ensure realtime detection. Third, we
extract critical vertices by solving a vertex cover problem using
Z3 SMT solver [55] to minimize the number of clustering. Finally, we cluster each critical vertex according to its connected
edges, which are in the centers of the clusters produced by the
pre-clustering, and thus obtain the abnormal edges indicating
encrypted malicious traffic.

In summary, the contributions of our paper are five-fold:
• We propose HyperVision, the first realtime unsupervised
detection for encrypted malicious traffic with unknown
patterns by utilizing the flow interaction graph.
• We develop several algorithms to build the in-memory
graph that allows us to accurately capture interaction
patterns among various flows.
• We design a lightweight unsupervised graph learning
method to detect encrypted traffic via graph features.
• We develop a theoretical analysis framework established
by information theory to show that the graph captures
near-optimal traffic interaction information.
• We prototype HyperVision and use the extensive experiments with various real-world encrypted malicious traffic
to validate its accuracy and efficiency.

Moreover, to quantify the benefits of the graph based flow
recording of HyperVision over the existing approaches, we
develop a flow recording entropy model, an information theory
based framework that theoretically analyzes the amount of
information retained by the existing data sources of malicious
traffic detection systems. By using this framework, we show
that the existing sampling based and event based traffic data
sources (e.g., NetFlow [19] and Zeek [86]) cannot retain highfidelity traffic information. Thus, they are unable to record
flow interaction information for the detection. But the graph
in HyperVision captures near-optimal traffic information for
the graph learning based detection and the amount of the
information maintained in the graph approaches the theoretical
up-bound of the idealized data source with infinite storage
according to the data processing inequality [85]. Also, the
analysis results demonstrate that the graph in HyperVision
achieves higher information density (i.e., amount of traffic
information per unit of storage) than all existing data sources,
which is the foundation of the accurate and efficient detection.

The rest of the paper is organized as follows: Section II introduces the threat model of HyperVision. Section III presents
the high-level design of HyperVision. In section IV, V, and VI,
we describe the detailed designs. In Section VII, we conduct
the theoretical analysis. In Section VIII, we experimentally
evaluate the performances. Section IX reviews related works
and Section X concludes this paper. Finally, we present details
in Appendix.
1 Source code and datasets: https://github.com/fuchuanpu/HyperVision.

2

Attacker
Malicious Flow
Benign User
Benign Flow



Raw Packet
Parser














Packet Feature Distribution
Long Flows




Benign


Identified Cluster

 Critical
Vertex

Critical Vertex Detection

Edge Pre-Clustering

Malicious





2. Graph Pre-Processing

Fig. 1.

Long Flow Distribution Fitting



Abnormal
Component Detection

Flow Interaction Graph

Similar Short Flows

Flow Classification

Component
Statistical Features

Connected Components

Short Flows

Flow Collection





Timeout
Threshold



Long Flows
Short Flows

Ongoing
Traffic

Short Flow Aggregation

1. Graph Construction



Attacker



Benign

Interaction Pattern
Clustering

3. Abnormal Interaction Detection

Malicious Traffic

Victims

Abnormal
Component

The overview of HyperVision.

II.

T HREAT M ODEL A ND D ESIGN G OALS

in particular, encrypted malicious traffic. Normally, patterns
of each flow in the encrypted malicious traffic, i.e., singleflow patterns, may be similar to benign flows, which allow
them to evade the existing detection. However, the malicious
behaviors appearing in the interaction patterns between the
attackers and victims will be more distinct from the benign
ones. Thus, in HyperVision, we construct a compact graph
to maintain interaction patterns among various flows and
detect abnormal interaction patterns by learning the features of
the graph. HyperVision analyzes the graph structural features
representing the interaction patterns without prior knowledge
of known attack traffic and thus can achieve unsupervised
detection against various attacks. It realizes generic detection
by analyzing flows regardless of the traffic type and can detect
encrypted and non-encrypted malicious traffic. Figure 1 shows
three key parts of HyperVision, i.e., graph construction, graph
pre-processing, and abnormal interaction detection.

We aim to develop a realtime system (i.e., HyperVision)
to detect encrypted malicious traffic. It performs detection according to the traffic replicated by routers through port mirroring [17], which ensures that the system will not interfere with
the traffic forwarding. After identifying encrypted malicious
traffic, it can cooperate with the existing on-path malicious
traffic defenses [48], [49], [88] to throttle the detected traffic.
To perform detection on encrypted traffic, we cannot parse and
analyze application layer headers and payloads.
In this paper, we focus on detecting active attacks constructed with encrypted traffic. We do not consider passive
attacks that do not generate traffic to victims, e.g., traffic
eavesdropping [68] and passive traffic analysis [70]. According
to the existing studies [10], [24], [29], [40], [46], [81], attackers utilize reconnaissance steps to probe the information of
victims, e.g., the password of a victim [39], the TCP sequence
number of a TLS connection [26], [27], and the randomized
memory layout of a web server [75], which cannot be accessed
directly by attackers due to lack of prior knowledge. Note that,
these attacks are normally constructed with many addresses
owned or faked by attackers.

Graph Construction. HyperVision collects network flows for
graph construction. Meanwhile, it classifies the flows into
short and long ones and records their interaction patterns
separately for the purpose of reducing the density of the
graph. In the graph, it uses different addresses as vertices
that connect the edges associated with short and long flows,
respectively. It aggregates the massive similar short flows
to construct one edge for a group of short flows, and thus
reduces the overhead for maintaining flow interaction patterns.
Moreover, it fits the distributions of the packet features in the
long flows to construct the edges associated with long flows,
which ensures high-fidelity recorded flow interaction patterns,
while addressing the issue of coarse-grained flow features in
the traditional methods [36]. We will detail how HyperVision
maintains the high-fidelity flow interaction patterns in the inmemory graph in Section IV.

The design goals of HyperVision are as follows: First,
it should be able to achieve generic detection, i.e., detect
attacks constructed with encrypted or non-encrypted traffic,
which ensures that the attacks cannot evade detection by traffic
encryption [2], [77]. Second, it is able to achieve realtime
high-speed traffic processing, which means that it can identify
whether the passing through encrypted traffic is malicious,
while incurring low detection latency. Third, the performed
detection by HyperVision is unsupervised, which means that it
does not require any prior knowledge of encrypted malicious
traffic. That is, it should be able to deal with attacks with
unknown patterns, i.e., zero-day attacks, which have not been
disclosed [30]. Thus, we do not use any labeled traffic datasets
for ML training. These issues cannot be well addressed by the
existing detection methods [62].
III.

Graph Pre-Processing. We pre-process the built interaction
graph to reduce the overhead of processing the graph by
extracting connected components and cluster the components
using high-level statistics. In particular, the clustering can
detect the components with only benign interaction patterns
accurately and thus filters these benign components to reduce
the scale of the graph. Moreover, we perform a pre-clustering
and use the generated cluster centers to represent the edges in

OVERVIEW OF H YPERV ISION

In this section, we develop HyperVision that is an unsupervised detection system to capture malicious traffic in real time,
3

Fig. 2.

 3 ' )

 $ Y J   1 X P       

 $ Y J   6 L ] H        

 % X F N H W  1 X P 

 & H Q W U D O L ] H G  ' L V W U L E X W L R Q

                                
 1 X P E H U  R I  % X F N H W V  >    % \ W H V @

(a) Number of packet length buckets.
Fig. 4.

 % X F N H W  6 L ] H

   
     + L J K  8 W L O L ] D W L R Q
   
   
   
   
   
   
                                           
 3 D F N H W  / H Q J W K  % X F N H W  6 L ] H  >log10   6 F D O H @
(b) Maximum bucket size.

The number and size of the buckets for feature distribution fitting.

can be extracted from both encrypted and plain-text traffic for
generic detection. We develop a flow classification algorithm to
classify the traffic (see Algorithm 1 in Appendix A). It maintains a timer TIME NOW, a hash table that uses H ASH ( SRC ,
DST, SRC PORT, DST PORT ) as key and the collected flows
indicated by the sequences of their per-packet features as
values. It traverses the hash table every JUDGE INTERVAL second according to TIME NOW and judges the flow completion
when the last packet arrived before PKT TIMEOUT second
of TIME NOW. When the flows are completed, we classify
them as long flows if the flows have more than FLOW LINE
packets. Otherwise, we classify them as short flows. As shown
in Figure 2(b), we can accurately classify short and long
flows. The definitions of the hyper-parameters can be found in
Table VII (see Appendix A). Note that, we poll the state-less
per-packet information from data-plane, while not maintaining
flow states (e.g., a state machine [89]) on the data-plane to
prevent attackers manipulating the states, e.g., side-channel
attack [65] and evading detection [79].

(b) Short flow aggregation.

HyperVision aggregates short flows to reduce the dense graph.

the identified clusters. We will detail the graph pre-processing
in Section V.
Malicious Traffic Detection Based on the Graph. We
achieve unsupervised encrypted malicious traffic detection by
analyzing the graph features. We identify critical vertices in the
graph by solving a vertex cover problem, which ensures that
the clustering based graph learning processes all edges with the
minimum number of clustering. For each selected vertex, we
cluster all connected edges according to their flow features and
structural features that represent the flow interaction patterns.
HyperVision can identify abnormal edges in real time by
computing the loss function of the clustering. We will describe
the details of graph learning based detection in Section VI.
IV.

    
    
    
    
    
    

 3 ' )

 $ O O

   
 / R Q J
 0 R V W  3 D F N H W V  $ U H
 6 K R U W
   L Q  / R Q J  ) O R Z V
   
   
   
   
                                       
 ) O R Z  / H Q J W K  >log10   6 F D O H @
(b) Flow length distribution.

The real-world flow features distribution of short and long flows.

(a) Traditional flows as edges.
Fig. 3.

   

 $ O O

   
 / R Q J
 0 R V W  ) O R Z V  $ U H
 6 K R U W
     6 K R U W  W H U P
   
   
   
   
                                           
 ) O R Z  & R P S O H W L R Q  7 L P H  >log10   6 F D O H @
(a) FCT distribution.

 3 ' )

 3 ' )

   

B. Short Flow Aggregation
We need to reduce the density of the graph for analysis.
As shown in Figure 3(a), the graph will be very dense for
analysis if we use traditional four-tuple flows as edges, which
is similar to the dependency explosion problem in provenance
analysis [83], [87]. We observe that most short flows have
almost the same per-packet feature sequences. For instance, the
encrypted flows of repetitive SSH cracking attempts originated
from specific attackers [39]. Thus, we perform the short flow
aggregation to represent similar flows using one edge after the
classification.

G RAPH C ONSTRUCTION

In this section, we present the design details of constructing
the flow interaction graph that maintains interaction patterns
among various flows. In particular, we classify different flows,
i.e., short and long flows, and aggregate short flows, and
perform the distribution fitting for long flows, respectively, for
efficient graph construction. In Section VII, we will show that
the graph retains the near-optimal information for detection.

In order to efficiently analyze flows captured on the Internet, we need to avoid the dependency explosion among
flows during the graph construction. We classify the collected
flows into short and long flows, according to the flow size
distribution [25] (see Figure 2), and then reduce the density of
the graph (shown in Figure 3). Figure 2 shows the distribution
of flow completion time (FCT) and flow length of the MAWI
Internet traffic dataset [80] in Jan. 2020. For simplicity, we use
the first 13 × 106 packets to plot the figure. According to the
figure, we observe that only 5.52% flows have FCT > 2.0s.
However, 93.70% packets in the dataset are long flows with
only 2.36% proportion. Inspired by the observation, we apply
different flow collection strategies for the short and long flows.

We design an algorithm to aggregate short flows (see
Algorithm 2 in Appendix A). A set of flows can be aggregated
when all the following requirements are satisfied: (i) the flows
have the same source and/or destination addresses, which
implies similar behaviors generated from the addresses; (ii)
the flows have the same protocol type; (iii) the number of the
flows is large enough, i.e., when the number of the short flows
reaches the threshold AGG LINE, which ensures that the flows
are repetitive enough. Next, we construct an edge for the short
flows, which preserves one feature sequence (i.e., protocols,
lengths, and arrival intervals) for all the flows, and their
four-tuples. As a result, four types of edges associated with
short flows exist on the graph, i.e., source address aggregated,
destination address aggregated, both addresses aggregated, and
without aggregation. Thus, a vertex connected to the edge can
denote a group of addresses or a single address.

We poll the per-packet information from a data-plane highspeed packet parsing engine and obtain their source and destination addresses, port numbers, and per-packet features, including protocols, lengths, and arrival intervals. These features

Figure 3 compares the graph using traditional flows as
edges and our aggregated graph by using the real-world backbone traffic dataset, which is same to that used in Figure 2. The
diameter of a vertex indicates the number of addresses denoted

A. Flow Classification

4

 3 ' )

   
   
   
   
   
   

 6 K R U W  ) O R Z

 / R Q J  ) O R Z V

 6 P D O O  & R P S R Q H Q W V

                               
 1 X P E H U  R I  % \ W H V  >log10   6 F D O H @ 

(a) Component size distribution.
Fig. 5.

   
   
   
   
   
   
   

   
   
   
   
    
 2 X W O L H U  & R P S R Q H Q W V
    
    
                                                
 3 & $  ' H F R P S R V H G  ) H D W X U H V 
(b) Scatter of the components.

The statistical features of the components.

Fig. 6.

by the vertex and the depth of the color indicates the repeated
edges. In Figure 3(b), we observe that the algorithm reduces
93.94% vertices and 94.04% edges. The edge highlighted in
green indicates short flows (i.e., 2.38 Kpps, from PH) exploiting a vulnerability. Note that, the flow aggregation reduces
the storage overhead, which makes it feasible to maintain the
in-memory graph for realtime detection.

   
   
 $ G M D F H Q W  ( G J H V
 ( G J H  ) H D W X U H V

   

                       
 3 & $  ' H F R P S R V H G  / R Q J  ) O R Z  ) H D W X U H V
(a) Adjacent long flows.

                               
 3 & $  ' H F R P S R V H G  6 K R U W  ) O R Z  ) H D W X U H V
(b) Adjacent short flows.

The sparsity of edges in the graph feature space.
Selected





Selected

Degree = 6

Malicious



Degree = 5


Flows in a
component

Fig. 7.

C. Feature Distribution Fitting for Long Flows

  Selected

Calculate the
subset of vertices

Degree = 3

Cluster the edges
for selected vertices

Benign


Benign

Identify the edges
denoting attacks

Critical vertices identification via solving the vertex cover problem.

(DFS) and split the graph by the components. Figure 5(a)
presents the size distribution of the identified components of
the MAWI traffic dataset [80] collected in Jan. 2020. We
observe that most components contain few edges with similar
interaction patterns. Thus, we perform a clustering on the highlevel statistics for the connected components to capture the
abnormal components that have over one order of magnitude
clustering loss than normal components as clustering outliers.
Specifically, we extract five features to profile the components,
including: (i) the number of long flows; (ii) the number of
short flows; (iii) the number of edges denoting short flows;
(iv) the number of bytes in long flows; and (v) the number of
bytes in short flows. We perform a min-max normalization
and acquire the centers using the density based clustering,
i.e., DBSCAN [32]. For each component, we calculate the
Euclidean distance to its nearest center. We detect an abnormal
component when its distance is over the 99th percentile of all
the distances based on our empirical study.

Now we use histograms to represent the per-packet feature
distributions of a long flow which avoid preserving their long
per-packet feature sequences, since the features in long flows
are centrally distributed. Specifically, we maintain a hash table
to construct the histogram for each per-packet feature sequence
in each long flow. According to our empirical study, we set
the buckets widths for packet-length and arrival interval as 10
bytes and 1 ms, respectively, to trade off between the fitting
accuracy and overhead. We calculate the hash code by dividing
the per-packet features by the bucket width and increase the
counter indexed by the hash code. Finally, we record the hash
codes and the associated counters as the histograms. Note that,
the coarse-grained flow statistics, e.g., numbers of packets [36],
are insufficient for encrypted malicious traffic detection [76],
which also lose the flow interaction information [18].
Figure 4 shows the number of the used buckets and
the maximum bucket size for the long flows in the same
dataset shown in Figure 2. We confirm the centralized feature
distribution, i.e., most packets in the long flows have similar
packet lengths and arrival intervals. Specifically, in Figure 4(a),
we fit the distribution of packet length using only 11 buckets on
average, and most of the buckets collect more than 200 packets
(see Figure 4(b)), which demonstrate that the histogram based
fitting is effective with low storage overhead. Similarly, the
fitting for arrival interval uses 121 buckets on average and
realizes 71 packets per bucket high utilization. Besides, we use
the same method for protocol. We use the mask of protocols as
the hash code and use smaller numbers of buckets to realize
more efficient fitting due to the limited number of protocol
types. Note that, Flowlens [5] used a similar histogram to
efficiently utilize hardware flow tables on P4 switches. Instead,
we construct the histograms to accurately analyze long flows.
V.

   

Figure 5(b) shows an instance of the clustering, where the
diameters indicate the scale of the traffic on the components (in
the unit of bytes). We observe that most components are small,
and a high ratio of huge components is classified as abnormal.
All edges associated with the normal components are labeled
as benign traffic, and the edges associated with the abnormal
components will be further processed by the following steps.
B. Edge Pre-Clustering
Now we further need to process and pre-cluster the graph
for efficient detection. As shown in Figure 5, the abnormal
components in the graph have massive vertices and edges. In
particular, we cannot directly apply graph representation learning, e.g., graph neural network (GNN), for realtime detection.
Figure 6 shows the edges from the components in the graph
structural feature space. We observe that the distribution of
the edges is sparse, i.e., most edges are adjacent to massive
similar edges in the feature space. To utilize the sparsity, we
perform a pre-clustering using DBSCAN [32] that leverages
KD-Tree for efficient local search and select the cluster centers
of the identified clusters to represent all edges in each cluster
to reduce the overhead for graph processing.

G RAPH P RE -P ROCESSING

In this section, we pre-process the flow interaction graph
to identify key components and pre-cluster the edges, which
can enable realtime graph learning based detection against
encrypted malicious traffic with unknown patterns.
A. Connectivity Analysis

Specifically, we extract eight and four graph structural
features (see Table V in Appendix A) for the edges associated
with short and long flow, respectively, e.g., the in-degree of

To perform the connectivity analysis of the graph, we
obtain the connected components by using depth-first search
5

the source vertex of an edge associated with a long flow.
These degree features of malicious traffic are significantly
distinct from the benign ones, e.g., the vertices denoting
spam bots have higher out-degrees than benign clients due
to their frequent interactions with servers. Then, we perform
a min-max normalization for the features, and adopt a small
search range  and a large minimum number of points for
DBSCAN clustering (see Section VIII-A for the setting of
hyper-parameters) to avoid including irrelevant edges in the
clusters, which may incur false positives. Moreover, some
edges cannot be clustered and should be treated as outliers,
which will be processed as clusters with only one edge.
VI.

where K is the number of obtained cluster centers, Ci is the
ith center, f (edge) is the feature vector, C(edge) contains all
edges in the cluster of edge produced by pre-clustering, and
TimeRange calculates the time range covered by the flows
denoted by the edges.
According to Equation (4), the loss has three parts: (i)
losscenter in (1) is the Euclidean distance to the cluster centers
which indicates the difference from other edges connected to
the critical vertex; (ii) losscluster in (2) indicates the time range
covered by the cluster identified by the pre-clustering in Section V-B which implies long lasting interaction patterns tend to
be benign; (iii) losscount in (3) is the number of flows denoted
by the edges, which means a burst of massive flows implies
malicious behaviors. Moreover, we used weights: α, β, γ to
balance the loss terms. Finally, it detects the associated flows
as malicious when the loss function of the edge is larger than
a threshold.

M ALICIOUS T RAFFIC D ETECTION

In this section, we detect encrypted malicious traffic by
identifying abnormal interaction patterns on the graph. In
particular, we cluster edges connected to the same critical
vertex and detects outliers as malicious traffic (see Figure 7).

VII.

A. Identifying Critical Vertices

In this section, we develop a theoretical analysis framework, i.e., flow recording entropy model, to analyze the information preserved in the graph of HyperVision for graph
learning based detection. The detailed analysis can be found
in Appendix C.

To efficiently learn the interaction patterns of the traffic,
we do not perform clustering for all edges directly but cluster edges connected to critical vertices. For each connected
component, we select a subset of all vertices in the connected
component as the critical vertices according to the following
conditions: (i) the source and/or destination vertices of each
edge in the component are in the subset, which ensures that
all the edges are connected to more than one critical vertices
and clustered at least once; and (ii) the number of selected
vertices in the subset is minimized, which aims to minimize the
number of clustering to reduce the overhead of graph learning.
Finding such a subset of vertices is an optimization problem
and equivalent to the vertex cover problem [33], which was
proved to be NP Complete (NPC). We select all edges and
all vertices on each component to solve the problem. And we
reformulate the problem to a Satisfiability Modulo Theories
(SMT) problem that can be effectively solved by using Z3
SMT solver [55]. Since we pre-cluster the massive edges and
reduce the scale of the problem (see Section V-B), the NPC
problem can be solved in real time.

A. Information Entropy Based Analysis
We develop the framework that aims to quantitatively evaluate the information retained by the exiting traffic recording
modes, which decide the data representations for malicious
traffic detection, by using three metrics: (i) the amount of
information, i.e., the average Shannon entropy obtained by
recording one packet; (ii) the scale of data, i.e., the space
used to store the information; (iii) the density of information,
i.e., the amount of information on a unit of storage. By using
this framework, we model the graph based traffic recording
mode used by HyperVision as well as three typical types of
flow recording modes, i.e., (i) idealized mode that records and
stores the whole per-packet feature sequence; (ii) event based
mode (e.g., Zeek) that records specific events [2], [20]; and
(iii) sampling based mode (e.g., NetFlow) that records coarsegrained flow information [8], [51].

B. Edge Feature Clustering for Detection
Now we cluster the edges connected to each critical vertex
to identify abnormal interaction patterns. In this step, we use
the structural features in Section V-B, and the flow features
extracted from the per-packet feature sequences of short flows
or the fitted feature distributions of long flows. All features are
shown in Table V (see Appendix A). We use the lightweight
K-Means algorithm to cluster the edges associated with short
and long flows, respectively, and calculate the clustering loss
that indicates the degree of maliciousness for malicious flow
detection.
losscenter (edge) =

min

Ci ∈{C1 ,...,CK }

||Ci − f (edge)||2 ,

We model a flow, i.e., a sequence of per-packet features,
as a sequence of random variables represented by an aperiodic irreducible discrete-time Markov chain (DTMC). Let
G = {V, E} denote the state diagram of the DTMC, where
V is the set of states (i.e., the values of the variables) and
E denotes the edges. We define s = |V| as the number of
different states and use W = [wij ]s×s to denote the weight
matrix of G. All of the weights are equal and normalized:
∀ 1 ≤ i, j, m, n ≤ s, (wij =wmn ) ∨ (wij = 0 ∨ wmn = 0),
s
s
X
X
(5)
wi =
wij , 1 =
wi .

(1)

losscluster (edge) = TimeRange(C(edge)),
losscount (edge) = log2 (Size(C(edge)) + 1),

(2)
(3)

loss(edge) =αlosscenter (edge)
−βlosscluster (edge) + γlosscount (edge),

(4)

T HEORETICAL A NALYSIS

j=1

i=1

The state transition is performed based on the weights, i.e.,
the transition probability matrix P = [Pij ], Pij = wij /wi .
Therefore, the DTMC has a stationary distribution µ:
6

(
µP = µ,
P
1 = sj=1 µj

⇒

µj = w j ,

∀ 1 ≤ j ≤ s.

1 − (Kq + 1)(1 − q)K
1
H[G] + s(1 − q)K
q
4
[(1 + s) lnps + 2 ln 2πe + 2q ln K − 2s(1 + p + γ)].
HH.V. =

(6)

Assume that the stationary distribution is a binomial distribution with the parameter: 0.1 ≤ p ≤ 0.9 to approach Gaussian
distribution with low skewness:
App.

µ ∼ B(s, p) −→ N (sp, sp(1 − p)).

We can also obtain the expected data scale and the density:
LH.V. = s(1 − q)K +

(7)

H[G] =

i=1

µi

s
X
j=1

pij ln

s X
s
X

DH.V. =

1
ln 2πsep(1 − p).
2

(8)

Moreover, for the real-world flow size distribution, we assume that the length of the sequence of random variables obeys
a geometric distribution with high skewness, i.e., L ∼ G(q)
with a parameter: 0.5 ≤ q ≤ 0.9. H, L, and D denote the
expectation of the metrics, i.e., the amount of information, the
scale of data, and the density, respectively.

HSamp. = H[XSamp. ] =

Idealized Recording Mode. The idealized recording mode has
infinite storage and captures optimal fidelity traffic information
by recording each random variable from the sequence without
any processing. Thus, the obtained information entropy of the
idealized mode grows at the entropy rate of the DTMC:
HIdeal = E[LH[G]] =

1
1
ln |E| −
ln 2πsep(1 − p).
q
2q

(9)

DIdeal =

HIdeal
= H[G].
LIdeal

(14)

1
ln 2
ln 2πesp(1 − p) +
q(1 − q). (15)
2
2
LSamp. = 1.

(16)

DSamp. = HSamp.

(17)

HEve. = −2θ ln θ,

(18)

where θ = ηζ , ζ = q − qps , and η = q − ps (q − 1).

We can obtain the scale of data and the density of information for the idealized recording mode as follows:
1
.
q

HH.V.
.
LH.V.

Event Based Recording Mode. The event based recording
mode inspects each random variable in the sequence and
records events with a small probability. Since the observation
that the event based methods do not generate repetitive events
for a long flow with a larger s, for simplicity, we assume that
the probability is ps ∝ 1/s. Then, we can obtain the concise
closed-form solution of the amount of information, the scale of
data, and the density of information for event based recording
mode as follows:

According to data processing inequality [85], the information retained in the idealized recording mode reaches the
optimal value. It implies that processing of the observed perpacket features denoted by the random variables may incur
information loss. In the following sections, we will show that
the other mode incurs information loss.

LIdeal = E[L] =

(13)

Sampling Based Recording Mode. Similarly, the sampling
based mode extracts and records flow statistics for the detection. We analyze the accumulative statistics (e.g. the total
number of bytes) that are widely adopted [19], [36]. Let
hs1 , s2 , ..., sP
L i denote the sequence of random variables, and
L
XSamp. = i=1 si indicates the flow statistic to be recorded.
We can obtain a tight lower bound as an estimation for the
amount of information and the other metrics as follows:

s
X

1
=−
wij ln wij +
wj ln wj
pij
i=1 j=1
j=1

= ln |E| −

1 − (Kq + 1)(1 − q)K
,
Cq

where C is the average number of flows denoted by an edge
associated with short flows.

Based on the distribution, we obtain the entropy rate of
the DTMC which is the expected Shannon entropy increase
for each step in the state transition, i.e., the expected Shannon
entropy of each random variable in the sequence, (using nat
as unit, 1 nat ≈ 1.44 bit):
s
X

(12)

ps
.
η

(19)

2ζ
ln θ.
ps

(20)

LEve. = −

(10)

DEve. =

(11)

B. Analysis Results
Graph Based Recording Mode of HyperVision. HyperVision
applies different strategies to process short and long flows for
the graph construction. Let K denote the threshold for classifying the flows. When L < K, it collects all random variables
from the sequence for short flows. Otherwise, it collects the
histogram to fit the distribution for long flows. Then, we can
obtain the lower bound to estimate the information entropy in
the graph of HyperVision:

We perform numerical studies to compare the flow recording modes in real-world setting. We select three per-packet
features: protocol, length, and the arrival interval (in ms) as
the instances of the DTMC, then we measure the parameters
of the DTMC, i.e., |E| and |V| according to the first 106 packets
in the MAWI dataset on Jan. 2020 [80]. We also measure K,
C, and estimate the geometric distribution parameter q via the
second moment. We have the following three key results.
7

 6 D P S 

 ( Y H 

 , G H D O

 +  9 

 6 D P S 

 ( Y H 

 , G H D O

 +  9 

 6 D P S 

 ( Y H 

 ' H Q V L W \  , Q F U H D V H  > +  9     , G H D O @

 +  9 

 ' H Q V L W \  > Q D W    U H F R U G @

 , G H D O

   
   
   
   
   
   

   
   
   
   
   
   
   
   

   
   
   
   
   

   
   
   
 / H Q    
 J W K     
     D U D P  p
 3 D U D    
 P  q             7 0 &  3
 '
(a) The entropy of the modes.

   
   
   
 / H Q    
 J W K     
     D U D P  p
 3 D U D    
 P  q             7 0 &  3
 '
(b) The data scale of the modes.

   
   
   
 / H Q    
 J W K     
     D U D P  p
 3 D U D    
 P  q             7 0 &  3
 '
(c) The density of the modes.

   
   
   
 / H Q    
 J W K     
     D U D P  p
 3 D U D    
 P  q             7 0 &  3
 '
(d) The density improvement.

 ( Q W U R S \  > Q D W @

 ' D W D  6 F D O H  > 1 X P  @

   
   
   
   
   
   
   
   

The traffic information retained by different recording modes on the feasible region of the parameters.

   
 + \ S H U 9 L V L R Q
   
 , G H D O  0 R G H
   
   
   
                                      
 ' 7 0 &  3 D U D P  p

(a) Fix q and leave p as variable.

 ( Q W U R S \  > Q D W @

 ( Q W U R S \  > Q D W @

Fig. 8.

   
 + \ S H U 9 L V L R Q
   
 , G H D O  0 R G H
   
   
   
   
                                                
 ) O R Z  / H Q J W K  3 D U D P  q

Figure 8(d). From Table II, we find that, for all kinds of perpacket features, HyperVision can increase the density ranging
between 35.51% and 47.27% due to the different recording
strategies for short and long flows.
In summary, the flow interaction graph provides highfidelity and low-redundancy traffic information with obvious
flow interaction patterns, which ensures that HyperVision
achieves realtime and unsupervised detection, particularly,
detecting encrypted malicious traffic with unknown patterns.

(b) Fix p and leave q as variable.

Fig. 9.
HyperVision approaches the idealized flow recording mode on
information entropy.
TABLE II.

T HE INTEGRAL OF THE DENSITY IN THE FEASIBLE REGION .

Per-Packet Features
RR
D
(p, q)dpdq
RR F Ideal
DSamp. (p, q)dpdq
F
RR
F DEve. (p, q)dpdq
RR
F DH.V. (p, q)dpdq

VIII.

Packet Length Time Interval Protocol Type
1.011H32.10% 0.918H32.00% 0.795H32.51%
0.965H35.17% 0.963H28.66% 0.800H32.08%
0.588H60.51% 0.588H56.44% 0.588H50.08%

E XPERIMENTAL E VALUATION

A. Experiment Setup
Implementation. We prototype HyperVision with more than
8,000 Line of Code (LOC). The prototype is compiled by gcc
9.3.0 and cmake 3.16.3. We use DPDK [37] version 19.11.9
encapsulated by libpcap++ [63] version 21.05 to implement
the high-speed data-plane module. The graph construction
module maintains the graph in memory for realtime detection.
The graph learning module detects the encrypted malicious
traffic on the interaction graph. It uses DBSCAN and K-Means
in mlpack [57] (version 3.4.2) for clustering and Z3 SMT
Solver [55] (version 4.8) to identify the critical vertices.

1.489N47.27% 1.350N35.51% 1.178N48.18%

(1) HyperVision maintains more information using the graph
than the existing methods. Figure 8 shows the results on the
feasible region (F = {0.1 ≤ p ≤ 0.9, 0.5 ≤ q ≤ 0.9}).
We observe that HyperVision maintains at least 2.37 and 1.34
times information entropy than traditional flow sampling and
event based flow recording. Thus, the traditional detection
methods cannot retain high-fidelity flow interaction information. Actually, they only analyze the features of a single
flow, which can be evaded by encrypted traffic. According
to Figure 8(b), HyperVision has 69.69% data scale of the
sampling based mode. It implies that the data scale is the key
challenge for the existing methods to utilize flow interaction
patterns. We well address this issue by using the compact graph
for maintaining the interactions among flows.

Testbed. We deploy HyperVision on a testbed built upon
DELL servers (PowerEdge R410, produced in 2012) with two
Intel Xeon E5645 CPUs (2 × 12 cores), Ubuntu 20.04.2 (Linux
5.11.0), Docker 20.10.7, 24GB memory, one Intel 82599ES 10
Gb/s NIC, and two Intel 850nm SFP+ laser ports for optical
fiber connections. We configure 6GB huge page memory for
DPDK (3GB/NUMA Node) and bind 8 threads on 8 physical
cores for 16 NIC RX queues to parse the per-packet features
from high-speed traffic. We use 8 cores for in-memory graph
construction, and 7 cores are used for graph learning, the rest
one core is used as DPDK master core.

(2) HyperVision maintains near-optimal information using the
graph. According to Figure 8(a), we observe that the information maintained by the graph almost equals to the theoretical
optimum, with the difference ranging from 4.6 × 10−9 to 2.6
nat. When the parameter of the geometric distribution of L
approaches 0.9, the flow information loss is larger because of
the increasing ratio of long flows that incur more information
loss. Figure 9 compares the information in HyperVision and
the idealized system when q = 0.59 and p = 0.8. We have
similar results. The gaps between the graph mode and the
optimal mode are only 0.056 and 0.021.

Datasets. We use real-world backbone network traffic datasets
from the vantage-G of WIDE MAWI project [80] in AS2500,
Tokyo Japan, Jan. ∼ Jun. 2020 as background traffic. The
vantage transits traffic from/to its BGP peers and providers
using 10 Gb/s fiber linked to its IXP (DIX-IE), and the traffic
is collected using port mirroring, which is consistent with
our threat model and the physical testbed described above.
We remove the attack traffic with obvious patterns in the
background traffic dataset according to the rules defined by the
existing studies [22], [43], [66], e.g., traffic will be detected as
scanning traffic if it has scanned over 10% IPv4 addresses [22].
We generate the malicious traffic by constructing real attacks
or replaying the existing traces in our testbed. Specifically, we
collect malicious traffic in our virtual private cloud (VPC) with

(3) HyperVision has higher information density than the existing methods. Figure 8(c) shows that HyperVision realizes
1.46, 1.54, and 2.39 times information density than the existing
methods, respectively. Although the idealized system realizes
the optimal amount of traffic information, the density is
only 78.55% of HyperVision in the worst case, as shown in
8

more than 1,500 instances. We manipulate the instances to perform attacks according to the real-world measurements [22],
[24], [40], [42], [43], [54], [66] and the same settings in the
existing studies [11], [26], [41], [44]. We classify 80 new
datasets used in our experiments (see Table VI for details) into
four groups, three of which are encrypted malicious traffic:

TABLE III.

T HE AVERAGE ACCURACY ON THE GROUPS OF DATASETS .

Method Metric

Traditional
Attacks

AUC
F1
AUC
FlowLens
F1
AUC
Whisper
F1
AUC
Kitsune
F1
AUC
DeepLog
F1

0.913H7% 0.782H19%
N/A1
N/A
0.867H12%
0.819H16% 0.495H46%
N/A
N/A
0.705H26%
0.939H4% 0.757H22% 0.685H30% 0.768H22% 0.752H36%
0.799H18% 0.651H29% 0.384H59% 0.411H57% 0.451H41%
0.951H3% 0.932H4% 0.958H2% 0.648H34% 0.752H23%
0.705H27% 0.461H50% 0.546H42% 0.357H62% 0.407H57%
0.748H24%
-2
0.759H22%
0.751H23%
0.419H57%
0.366H61%
0.402H58%
0.716H27% 0.621H26% 0.767H22% 0.653H34% 0.666H32%
0.513H47% 0.508H45% 0.572H40% 0.628H34% 0.597H37%

Jaqen

• Traditional brute force attack. Although HyperVision focuses on encrypted traffic, we generate 28 kinds of traditional flooding attacks to verify its generic detection and
the correctness of baselines including 18 high-rate and 10
low-rate attacks: (i) the brute scanning with the real packet
rates [22]; (ii) the source spoofing DDoS with various
rates [40]; (iii) the amplification attacks [43]; (iv) probing
vulnerable applications [21], [22]. We collected the traffic
in our VPC to avoid interference with real services.
• Encrypted flooding traffic. Different from the brute force
flooding, the encrypted flooding is generated by repetitive
attack behaviors which target specific applications: (i) the
link flooding generates encrypted low-rate flows, e.g., the
low-rate TCP attacks [44], [52] and the Crossfire attack [41],
to congest links; (ii) injecting encrypted flows that exploits
protocol vulnerabilities by flooding attack traffic and inject
packets into the channel [11], [26], [28]; (iii) the password
cracking performs slow attempts to hijack the encrypted
communication protocols [39], [50]. We perform SSH cracking in the VPC with the scale of SSH servers in the ASes
reachable to AS2500.
• Encrypted web malicious traffic. Web malicious traffic is
normally encrypted by HTTPS. We collect the traffic generated by seven widely used web attacks including automatic
vulnerabilities discovery (including XSS, CSRF, various
injections) [64], SSL vulnerabilities detection [53], and
crawlers. We also collect the SMTP-over-TLS spam traffic
that lures victims to visit the phishing sites [61].
• Malware generated encrypted traffic. The traffic of malware
campaigns is low-rate and encrypted, e.g., malware component update or delivery [9], command and control (C&C)
channel [8], and data exfiltration [77]. We use the malware
infection statistics published in 2020 [42] and probed active
addresses from the adopted vantage [23], [59] to estimate
the number of visible victims. We use the same number
of instances to replay public malware traffic datasets [13],
[73] to mimic malware campaigns, which is similar to the
existing study [58].

H.V.
1
2

Flooding
Enc. Traffic

Enc. Web
Attacks

Malware
Traffic

Overall

AUC 0.988N8% 0.974N4% 0.985N2% 0.993N29% 0.988N13%
F1 0.978N19% 0.927N42% 0.957N67% 0.970N54% 0.960N36%

The results are N/A because Jaqen is designed for detection of volumetric attacks.
- means that the average AUC is lower than 0.60, which is nearly the result of
random guessing.

attacks, which aims to verify the long-run performances of
HyperVision (see Appendix B3). Moreover, we validate the
robustness of HyperVision against evasion attacks with obfuscation techniques, which can be found in Appendix B4.
Baselines. We use five state-of-the-art generic malicious traffic
detection methods as baselines:
• Jaqen (sampling based recording and signature based detection). Jaqen [51] uses Sketches to obtain flow statistics
and applies the threshold based detection. We prototype
Jaqen on the testbed, and adjust the signatures for each
statistic and each attack to obtain the best accuracy.
• FlowLens (sampling based recording and ML based detection). FlowLens [5] uses sampled flow distribution and
supervised learning, i.e., random forest. We use the hyperparameter setting with the best accuracy used in the paper
to retrain the ML model.
• Whisper (flow-level features and ML based detection).
Whisper [30], [31] extracts the frequency domain features
of flows and uses clustering to learn the features. We deploy
Whisper on the physical testbed without modifications and
then retrain the clustering model.
• Kitsune (packet-level features and DL based detection).
Kitsune extracts per-packet features and uses autoencoders
to learn the features which is an unsupervised method [56].
We use its default hyper-parameters and retrain the model.
• DeepLog (event based recording and DL based detection).
DeepLog is a general log analyzer using LSTN RNN [20].
We use the logs of connections for detection and its original
hyper-parameter setting to achieve the best accuracy.

The malicious traffic is replayed with the background traffic
datasets on the physical testbed simultaneously according to
their original packet rates [80] which is the same as the existing
studies [30], [47], [51]. Specifically, each dataset contains
12∼15 million packets and the replay lasts 45s and the first
75% time does not contain malicious traffic for collecting flow
interactions and training the baselines. Note that, the rates of
the encrypted attack flows in our datasets are only 0.01 ∼
8.79 Kpps which consume only 0.01% ∼ 0.72% bandwidth.
We will show that these stealthy attacks evade most baselines.

Note that, in the baselines above, we do not include DPIbased encrypted malicious traffic detection because they are
unable to investigate encrypted payloads [34]. Also, we do not
compare the task-specific detection methods [3], [76] because
they cannot achieve acceptable detection accuracy. Features in
FlowLens, Kitsune, and Whisper are similar to them, e.g., flow
features [3], packet header features [2], and time-series [76].

To eliminate the impact of the dataset bias, we also use 12
existing datasets including the Kitsune datasets [56], the CICDDoS2019 datasets [14], and the CIC-IDS2017 datasets [15],
which are collected in the real-world. These detailed results
can be found in Appendix B2. In particular, the traffic in
two CIC datasets [14], [15] lasts 6∼8 hours under multiple

Metrics. We mainly use AUC and F1 score because they
are most widely used in the literature [8], [20], [30], [35],
[56], [75], [91]. Also, we use other six metrics to validate the
improvements of HyperVision, including precision, recall, F2,
ACC, FPR, and EER.
9

TABLE IV.
Method Metric
AUC
F1
AUC
FlowLens
F1
AUC
Whisper
F1
AUC
Kitsune
F1
AUC
DeepLog
F1
Jaqen

Brute Scanning
SSH SQL DNS HTTP HTTPS NTP

Amplification Attack
Source Spoofing DDoS
DNS CharG. SSDP RIPv1 Mem. CLDAP SYN RST UDP ICMP

0.9478 0.9989 0.9706 0.9851 0.9989 0.9774 0.9988 0.9822 0.9590 0.9860 0.9907 0.9011 0.9586 0.9537 0.9976 0.9985 0.9682 0.9995
0.9710 0.9356 0.9835 0.9924 0.9965 0.9884 0.9299 0.9457 0.8816 0.7986 0.7054 0.6549 0.8500 0.7931 0.9614 0.9236 0.5603 0.9861
0.9906 0.9021 0.9961 0.9993 0.9985 0.9874 0.9226 0.9784 0.8001 0.9998 0.9907 0.9833 0.9786 0.9993 0.9912 0.9918 0.9999 0.6351
0.9181 0.6528 0.8899 0.9996 0.9992 0.9936 0.9572 0.9794 0.7127 0.9991 0.8918 0.9889 0.9691 0.9986 0.8638 0.8173 0.9990 0.2632
0.9499 0.9796 0.9562 0.9811 0.9832 0.9658 0.9827 0.9125 0.9645 0.8489 0.9662 0.9761 0.8954 0.9402 0.9563 0.9658 0.8956 0.9489
0.7004 0.7585 0.8869 0.7022 0.6748 0.7182 0.7489 0.8248 0.8435 0.4686 0.6195 0.6396 0.6956 0.8620 0.7587 0.8778 0.4857 0.4192
0.4522 0.7252 - 2 0.7439 0.7228 0.7380 0.9614 0.7340 0.9994 0.9998 0.9989 0.4343 0.3993 0.7592 0.6210 0.4086 0.8534 0.7913
- 1 0.3459
0.5033 0.4923 0.4798 0.4878 0.4461 0.5031 0.4609 0.4360
0.3838 0.3361
0.4539 0.4153
0.6717 0.8232 0.8377 0.6518 0.8261 0.6617 0.5545 0.7475 0.7428 0.7462 0.7458 0.7487 0.7480 0.7483 0.7564 0.2470 0.7012 0.7521
0.3566 0.4178 0.5266 0.2695 0.4050 0.2668 0.3653 0.5108 0.7201 0.5705 0.4313 0.3368 0.3321 0.3424 0.6074
0.4370 0.3428

 7 U X H  3 R V L W L Y H  5 D W H

We highlight the best accuracy in • and the worst accuracy in •. We mark - for the F1 when the AUC is lower than 0.50, which is the accuracy of random guessing.
Kitsune did not finish the detection within 90 min (i.e., meaningless for defenses). And H.V. is short for HyperVision.

   
   
   
   
   
   

 - D T H Q
 ) O R Z / H Q V
 : K L V S H U

 . L W V X Q H
 ' H H S / R J
 +  9 

 7 U X H  3 R V L W L Y H  5 D W H

1

NTP

AUC 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9999 0.9998 0.9989 0.9998 0.9969 0.9999 0.9999 0.9999 0.9996 0.9928
F1 0.9939 0.9928 0.9960 0.9932 0.9831 0.9808 0.9892 0.9998 0.9998 0.9992 0.9956 0.9984 0.9983 0.9996 0.9993 0.9571 0.9981 0.9295

H.V.
2

ICMP

D ETECTION ACCURACY OF H YPERV ISION AND THE BASELINES ON TRADITIONAL BRUTE FORCE ATTACKS .

 - D T H Q
 ) O R Z / H Q V
 : K L V S H U

HyperVision has 0.992 ∼ 0.999 AUC and 0.929 ∼ 0.999 F1,
which achieves at most 13.4% and 1.3% improvement of F1
and AUC over the best performance of the baselines. The ROC
and PRC results are illustrated in Figure 10. According to
Figure 10(a) and 10(b), we observe that HyperVision has less
false positives while achieving similar accuracy. Figure 10(c)
and Figure 10(d) show that the PRC of HyperVision is largely
better than the baselines, which means that it has a higher
precision when all methods reach the same recall.

 . L W V X Q H
 ' H H S / R J
 +  9 

Fig. 10.

 5 H F D O O

                   
                       
 ) D O V H  3 R V L W L Y H  5 D W H
 ) D O V H  3 R V L W L Y H  5 D W H
(a) ROC of detecting NTP DDoS. (b) ROC of detecting HTTP scan.
   
   
 - D T H Q
 - D T H Q
   
   
 ) O R Z / H Q V
 ) O R Z / H Q V
   
   
 : K L V S H U
 : K L V S H U
 . L W V X Q H
 . L W V X Q H
   
   
 ' H H S / R J
 ' H H S / R J
   
  
 
 +  9 
 +  9 
   
   
                                   
                                   
 3 U H F L V L R Q
 3 U H F L V L R Q
(c) PRC of detecting NTP DDoS. (d) PRC of detecting SYN DDoS.
 5 H F D O O

   

   
   
   
   
   
   

Second, by comparing HyperVision with Jaqen, we can see
that HyperVision can realize higher accuracy (i.e., a 19.4% F1
improvement) than Jaqen with the best threshold set manually.
That is, the unsupervised method allows reducing manual
design efforts. Moreover, it has 56.3% AUC improvement
over the typical supervised ML based method (FlowLens).
Note that, we assume that HyperVision cannot acquire labeled
datasets for training, which is more realistic. Also, it outperforms Whisper with 11.6% AUC, which is an unsupervised
detection in high-speed network. We observe that Kitsune and
DeepLog have lower accuracy because they cannot afford highspeed backbone traffic.

ROC and PRC of HyperVision and all the baselines.

Hyper-parameter Selection. We conduct four-fold cross validation to avoid overfitting and hyper-parameter bias. Specifically, the datasets are equally partitioned into four subsets.
Each subset is used once as a validation set to tune the
hyper-parameters via the empirical study and the remaining
three subsets are used as testing sets. Finally, four results are
averaged to produce final results. Moreover, our ablation study
shows that the different threshold settings incur at most 5.2%
accuracy loss. Therefore, the hyper-parameter selection has
limited impacts on the detection results.

Third, we measure the detection accuracy of probing
vulnerable applications. As shown in Figure 11, we see that
HyperVision can detect the low-rate attacks with 0.920 ∼
0.994 F1 and 0.916 ∼ 0.999 AUC under 6 ∼ 268 attackers
with 17.6 ∼ 97.9 Kpps total bandwidth. It also achieves
at most 46.8% F1 and 27.3% AUC improvements over the
baselines that have a more significant accuracy decrease than
the high-rate attacks. For example, FlowLens only achieves
averagely 0.684 F1, which is only 77% under the high-rate
attacks. Although Jaqen can be deployed on programmable
switches, its thresholds are invalided by the low-rate attacks.
And Whisper is unable to detect the attacks with two datasets.
Moreover, Kitsune and DeepLog cannot detect the attacks
because of the low rate of malicious packets (≤ 1.2%).

B. Accuracy Evaluation
Table III summarizes the detection accuracy and the improvements of HyperVision over the existing methods. In general, HyperVision achieves average F1 ranging between 0.927
and 0.978 and average AUC ranging between 0.974 and 0.993
on the 80 datasets, which are 35% and 13% improvements over
the best accuracy of the baselines. In 44 datasets, none of the
baselines achieves F1 higher than 0.80, which means that they
are not effective to detect the attacks. Due to the page limits,
we do not show the failed detection results of these baselines.

The reason why HyperVision can detect the slow probing
while maintaining the similar accuracy to the high-rate attacks
is that the graph preserves flow interaction patterns. Although
the flows from a single attacker are slow, e.g., at least 244 pps,
HyperVision can record and analyze their interaction patterns.
Specifically, each flow in the stealthy attack traffic can be
represented by an edge in the graph, while the vertices in the
graph indicate the addresses generating the traffic. Thus, the

Traditional Brute Force Attacks. First, we measure the
performance of the baselines by using the flooding attacks with
short flows. Although HyperVision is designed for encrypted
malicious traffic detection, we find that it can also detect traditional attacks accurately. The results are shown in Table IV.
10

 5 ' 3  + 7 7 3

 ' 1 6  , & 0 3

 6 6 +

 - D T H Q                                          

 

                    

 ) O R Z / H Q V                                          

 

                    

 

      

 : K L V S H U                                          
 . L W V X Q H                                   

 

 

                    

      
 

 +  9                                                                       
 ) 

(a) AUC of detecting probing vulnerable application.
 - D T H Q                                          

 

                    

 

                    

 

      

 . L W V X Q H                                   

 

 

                    

 6 L ] H         V  % X U V W     V  % X U V W     V  % X U V W

 $ & .  , Q M 

 , 3 , '  , Q M   , 3 , '  3 R U W

 & U R V V I L U H  $ W W D F N

   
   
   
   
   
   

 6 L ] H    

 6 L ] H    

 / R Z  U D W H  7 & 3  ' R 6

 6 6 +  & R Q Q   , Q M H F W L R Q

 6 L ] H         V  % X U V W     V  % X U V W     V  % X U V W

 $ & .  , Q M 

 , 3 , '  , Q M   , 3 , '  3 R U W

      
 

 ' H H S / R J                                                                      
 +  9                                                                       

(b) F1 of detecting probing vulnerable application.
Fig. 11.

 6 L ] H    

 6 6 +   & R Q Q   , Q M H F W L R Q

(b) F1 of detecting encrypted link-flooding and encrypted channel injection.
 $ 8 &

 : K L V S H U                                          

 6 L ] H    

 +  9 
 / R Z  U D W H  7 & 3  ' R 6

(a) AUC of detecting encrypted link-flooding and encrypted channel injection.

 ' H H S / R J                                                                      

 ) O R Z / H Q V                                          

 ) O R Z O H Q V
 : K L V S H U
 & U R V V I L U H  $ W W D F N

   
   
   
   
   
   

 6 6 +

   
   
   
   
   

 7 H O Q H W

 ) 

 9 / &  6 1 0 3

 $ 8 &

 6 0 7  1 H W % L R  7 H O Q
 H W
 3
 V

    Y       Y       Y      Y 
 1 X P   9 L F W L P

    Y 

    Y 

(c) F1 of password cracking.

Heatmap of accuracy for probing vulnerabilities.

Fig. 12.

 +  9   $ Y J   $ 8 &

 : K L V S H U

 +  9 

    
    
    
    
    

 3 D
 2 U  G G L Q
 D  J
 > ;  F O H
 V V V  ;
 Q L S  6 6
 H
 > 6 6  6 6 /  U @
 / 6   9 X
 3  F D Q  O 
 > & R D U D P  @
 P P    , Q
 L [  M 
 > & R & R G  @
 P P  H  , Q
 L [  M 
 > & R $ J H Q  @
 P P  W  , Q
 L  M 
     & [ @
     9 (
    
     &  
     9 (
     
 &
 > % R  6 5 )
 O W @
 &
 > 6 F  U D Z
 U D S  O H U
 \ @
 >    6 S D
 % R  P
 W
 >    6 S @
  % R  D P
 W V @
 >    6
   %  S D
 R W V  P
 @

 $ 8 &

(d) AUC of password cracking.

Detection accuracy of encrypted flooding traffic.
 : K L V S H U  $ Y J   $ 8 &

traffic can be captured by identifying vertices with large outdegrees (i.e., a large number of edges). Moreover, the brute
force attacks validate that our method is effective to capture
the DDoS traffic because it utilizes the short flow aggregation
to construct the edge associated with short flows and avoids
inspecting each short spoofing flow. Besides, the experiment
results also show that the critical vertices denote the addresses
of major active flows, e.g., web servers, DNS servers, and
scanners. Note that, we exclude the results of the baselines that
cannot detect encrypted traffic with lower rates in the following
sections due to the page limits.

 7 H O Q H W
     6 6 +
   
   
   
    Y       Y       Y      Y      Y      Y 
 1 X P   9 L F W L P

 ) 

(a) AUC of detecting encrypted web attack traffic.
 : K L V S H U  $ Y J   ) 

 +  9   $ Y J   ) 

 : K L V S H U

 +  9 

 3 D
 2 U  G G L Q
 D  J
 > ;  F O H
 V V V  ;
 Q L S  6 6
 H
 > 6 6  6 6 /  U @
 / 6   9 X
 3  F D Q  O 
 > & R D U D P  @
 P P    , Q
 L [  M 
 > & R & R G  @
 P P  H  , Q
 L [  M 
 > & R $ J H Q  @
 P P  W  , Q
 L  M 
     & [ @
     9 (
    
     &  
     9 (
     
 &
 > % R  6 5 )
 O W @
 &
 > 6 F  U D Z
 U D S  O H U
 \ @
 >    6 S D
 % R  P
 W
 >    6 S @
  % R  D P
 W V @
 >    6
   %  S D
 R W V  P
 @

Encrypted Flooding Traffic. Figure 12 shows the detection
accuracy under flooding attacks using encrypted traffic. Generally, HyperVision achieves 0.856 ∼ 0.981 F1 and 0.917
∼ 0.998 AUC, which are 58.7% and 25.3% accuracy improvements over the baselines that can detect such attacks.
Specifically, as shown in Figure 12(a) and 12(b), we observe
that HyperVision can accurately detect the link flooding traffic
consists of various encrypted traffic with different parameters.
For instance, it can detect the Crossfire attack using HTTPS
web requests generated by different sizes of botnets [41]
with at most 0.939 F1. The massive web traffic generated by
bots, which is low-rate (≤ 4Kbps) and encrypted, evades the
detection of Whisper and FlowLens (F1 ≤ 0.8). As shown in
Figure 14(a), HyperVision can detect the attack efficiently by
splitting the botnet clusters into a single connected component
to exclude the interference from the similar benign web traffic,
where the inner layer denotes botnets and the outer denotes
decoy servers.

    
    
    
    
    
    

(b) F1 of detecting encrypted web attack traffic.
Fig. 13.

Moreover, we find that HyperVision can detect low-rate
TCP DoS attacks that use burst encrypted video traffic for
at most 0.995 AUC and 0.938 F1. Although Whisper has
slightly better AUC in some cases, we find that it cannot
achieve high accuracy on all scenarios. As a result, it has
only 55.5% AUC in the worse case. Moreover, HyperVision
can aggregate the short flows in the SSH connection injection
attacks and achieves more than 0.95 F1. The attacks exploiting
protocol vulnerabilities realize low-rate packet injection and
evade the detection of FlowLens (i.e., AUC ≤ 0.774, F1 ≤
0.513). Figure 12(c) and 12(d) illustrate that HyperVision can
identify slow and persisted password attempts for the channels

Fig. 14.

Accuracy of encrypted web attack traffic detection.

(a) Crossfire.

(b) SSH cracking.

(c) XSS detection.

(d) P2P botnet.

Subgraph with various encrypted malicious traffic.

with over 0.881 F1 and 0.917 AUC, which are 1.19 and 1.28
times improvements over FlowLens and Whisper. The reason is
that HyperVision maintains the interaction patterns of attackers
using the graph, e.g., the massive short flows for login attempts
shown as red edges in Figure 14(b).
11

 $ 8 &

    
    
    
    
    

 $ G Z D U H

    
                      
 7 K U R X J K S X W  > * E  V @

(c) Graph detection throughput.
Fig. 16.

(a) Graph construction latency.
   
 $ Y J        V
   
 - D Q      
   
   
   
99th   3 H U F H Q W L O H
   
   
   
   
                               
 / D W H Q F \  > V @

(c) Graph detection latency.

   
   
   
   
   
   
   
   
   
   
   

    
   
   
   
   
   
   
   
   

                                
 7 L P H  > V @

(a) Runtime memory usages.

 - D Q 
 ) H E 
 $ S U 
 - X Q 

    
    
    
    
    

   
     - D Q        % H Q L J Q  - X Q        5 6 7  ' R 6
   
   
   
   
   
   
   
   G  L   N
 
 G  L   N
 + H D  6 X U  = H H  +  9  + H D  6 X U  = H H  +  9

(b) Graph storage usages.

Hardware resource usages of HyperVision.

encrypted malware traffic is hard to detect for the baselines
because it is slow and persistent. However, HyperVision accurately detects the malware campaigns with at least 0.964
AUC and 0.891 F1. Specifically, it captures the C&C servers
of spyware for exfiltration as abnormal critical vertices that
are connected by massive infected hosts in the graph. As
a result, it detects the encrypted malicious traffic of the
malware with at least 0.942 F1. For example, to detect Sality
P2P botnet shown in Figure 14(d), HyperVision collects the
interactions among similar P2P bots, aggregates the encrypted
short flows as edges, and finally clusters the edges with higher
loss than benign interaction patterns. Similarly, it can capture
the static servers of adware, malware component delivery
servers, the infected miner pools as abnormal vertices. Note
that, the low-rate malicious flows (at least 0.814 pps) are
represented as the edges associated with short flows connected
to critical vertices. Meanwhile, the massive long flows with
almost 100% encrypted packet proportion are represented as
the edges associated with long flows to the vertices. Therefore,
a critical vertex connected with the edges indicates the malware
campaign that is significantly different from benign vertices
with large degrees, e.g., benign websites.

                              
 6 W D E O H  7 K U R X J K S X W  > * E  V @

 - D Q      

 R W  W H W  D Q  R W  L W \  R W
 7 + %  ( P R  6 Q R M  7 U L F N E  6 D O 0 D ] D U E

 2 Y H U D O O
 * U D S K

Fig. 18.

Throughput of graph construction and detection.

   
 - D Q      
   
 - X Q      
   
   
   
   
   
                                            
 / D W H Q F \  > V @

Fig. 17.

 - D Q 
 ) H E 
 $ S U 
 - X Q 

(d) Stable detection throughput.

 / D W H Q F \  > V @

 

 3 ' )

 $ Y J       * E  V
 - D Q      

    
    
    
    
    
    

 - X Q      

 ) O R Z  3 U R F   3 U R F   ) O R Z  3 U R F   3 U R F 
 & O D V V   / R Q J  6 K R U W  & O D V V   / R Q J  6 K R U W

(b) Construct latency composition.

 / W H Q F \  >10x   V @

 3 ' )  >×10 2  @

    
    

    
    
    
    
    
    
    
  

 U
 U  J  R  U  [
 . R O H 6 Y S H D Q Q V R P Q E Q D O R F N H ' U L G H  L W & R L Q 7 0 U R M D Q R 0 L Q 0 L Q H
 %
 5  : D
 &

                 
 0 D [ L P X P  7 K U R X J K S X W  > * E  V @
(b) Max construction throughput.

    

 3 ' )

 % R W Z D U H

 ) 

HyperVision can detect various encrypted malware traffic.

(a) Graph construction throughput.

 3 ' )

 0 L Q H U

 6 W R U D J H  8 V D J H  >10x   0 % @

 R  K  G  S
 ) H L 0 Z R E L G D V  $ G O R D H E & R P
 :

 0 H P R U \  8 V D J H  > * % @

 L F  H U  Q  R  H  H U
 0 D J 7 U L F N V W 3 O D Q N W R 3 H Q H W K  = V R & Q & O H D Q

    
 $ Y J        * E  V
    
 - D Q      
    
    
    
    
                          
 7 K U R X J K S X W  > * E  V @

    

 5 D Q V R P H Z D U H

 $ Y J   )      

Fig. 15.

 3 ' )

 ) 
 6 S \ Z D U H

 3 ' )

 $ 8 &

      $ Y J   $ 8 &

   
   
   
   
   
   
   
   
   

 7 R W D O  & R P S   3 U H  & U L W L F D O  & O X V W H U 
 , G H Q W L I \  & O X V W H U   9 H U W H [
(d) Detection latency composition.

C. Performance Results

Latency of graph construction and detection.

Throughput. We truncate the packets to the first 200 bytes
on the physical testbed and increase the sending rates until
the graph construction module reaches maximum throughput.
Figure 16 shows the throughput of the graph construction
and the detection. Figure 16(a) presents the distribution of
average throughput within a 1.0s time window. We observe
that HyperVision constructs the graph for 28.21 Gb traffic per
second. Figure 16(b) presents the maximum throughput in each
time window with all the backbone traffic datasets used in
the experiments. HyperVision achieves 32.43 ∼ 39.71 peak
throughput on average. Moreover, we measure the throughput
of the graph learning module, which inspects flow interactions.
According to Figure 16(c), we observe that it can analyze
121.14 Gb traffic per second on average. Note that, the detection throughput is 4.2 times higher than the construction so
that the detection can analyze the recorded traffic iteratively to
consider the past interaction information. We observe that the
average throughput exhibits a bimodal distribution. The peak
of low throughput (around 75 Gb/s) is caused by lacking the
information on the graph for analyzing during cold start stages.

Encrypted Web Malicious Traffic. Figure 13 presents the
detection accuracy of the encrypted traffic generated by various
web vulnerabilities discovery. HyperVision achieves 0.985
average AUC and 0.957 average F1 (i.e., 2.8% and 75.2%
increase compared to Whisper). The flow based ML detection
cannot detect web encrypted malicious traffic because the traffic has single-flow patterns that are almost same to benign web
access flows. HyperVision can accurately detect the encrypted
web malicious traffic, because, as shown in Figure 14(c), it
captures the traffic from the frequent interactions as the edges
associated with long flows, and identifies the malicious traffic
(denoted by red edges) generated by the attacker (denoted
by the green vertex) by clustering the edges associated with
benign web traffic that are connected to the same critical vertex
(denoted by the red solid vertex).
Encrypted Malware Traffic. We show the detection accuracy
of encrypted malware traffic in Figure 15. Note that, the
12

achieves task-agnostic encrypted traffic detection. Note that,
the provenance graph based attack forensic analysis [83], [87]
is orthogonal to our traffic detection.

Figure 16(d) illustrates the throughput when the performance
of the system is stable. We observe that it achieves 80.6 ∼
148.9 Gb/s throughput. Note that, the throughput on Apr. and
Jun. 2020 datasets is lower because of their low original traffic
volume.

DTMC Based Anomaly Detection. Discrete-Time Markov
Chain (DTMC) has been used to model the behaviors of
users/devices [1], [71], [72]. These methods aim to predict
behaviors of users and devices by utilizing DTMC. For instance, Peek-a-Boo predicted user activities [1], Aegis predicted user behaviors for abnormal event detection [72], and
6thSense predicted sensor behaviors for detecting sensor-based
attacks [71]. Different to these methods, our work utilizes
DTMC to quantify the benefits of building the compact graph
for detecting various unknown attacks.

Latency. We measure the latency caused by graph construction
and detection. Figure 17(a) presents the PDF of the maximum
latency for constructing each edge within a 1.0s window. We
observe that HyperVision has 1.09s ∼ 1.04s average construction latency with an upper bound of 1.93s. The distribution
is a significant bimodal one because the receive side scaling
(RSS) on the Intel NIC is unbalanced on the threads. The
light-load threads have only 0.75s latency. We analyze the
composition of the latency in Figure 17(b) (where the error bar
is 10th and 90th percentile) and find that the flow classification,
short flow aggregation, and long flow distribution fitting share
50.95%, 35.03%, and 14.0% latency, respectively. We measure
the average detection latency. Figure 17(c) shows that the
learning module has a 0.83s latency on average with a 99th
percentile of 4.48s. We also analyze the latency in each
step (see Figure 17(d)). We see that 75.8% of the latency
comes from pre-clustering (i.e., 0.66s on average). However,
the pre-clustering step reduces the processing overhead of
the subsequent processing, i.e., selecting critical vertex and
clustering, for 5.5 × 10−3 s (0.64%) and 3.4 × 10−3 s (0.40%).

ML Based Malicious Traffic Detection. ML based detection can detect zero-day attacks [12] and achieve higher
accuracy than the traditional signature based methods [89].
For example, Fu et al. leveraged frequency domain features
to realize realtime detection [30]. Barradas et al. developed
Flowlens to extract flow distribution features on data-plane
and detect attacks by applying random forest [5]. Stealthwatch
detected attacks by analyzing flow features extracted from
NetFlow [16]. Mirsky et al. developed Kitsune to learn the
per-packet features by adopting auto-encoders [56]. For taskspecific methods, Nelms et al. [60], Invernizzi et al. [38],
and Bilge et al. [8] detected traffic in the different stages of
malware campaigns by using statistical ML. Bartos et al. [6]
and Tang et al. [75] detect malformed HTTP request traffic.
Holland et al. [35] developed an automatic pipeline for traffic
detection. All these methods cannot effectively detect attacks
based on encrypted traffic.

Resource Consumption. Figure 18(a) presents the memory
usage of HyperVision. Note that, the DPDK huge pages require
6GB memory and thus we measure the consumption when the
usage reaches 6GB. We observe that the increasing rate of
memory for maintaining the graph is only 13.1 MB/s. Finally,
HyperVision utilizes 1.78 GB memory to maintain the flow
interaction patterns extracted from 2.82 TB ongoing traffic.
HyperVision incurs low memory consumption because the feature distribution fitting for long flow and short flow aggregation
make the in-memory graph compact which ensures low-latency
detection and long-term recording. Moreover, the memory
consumption of the learning algorithm is 1.452 ∼ 1.619 GB.
HyperVision can export the graph to disk for forensic analysis.
Figure 18(b) shows the storage used for recording the first
45s traffic of the MAWI dataset by different methods, i.e.,
HyperVision, event based network monitors (i.e., Suricata [74]
and Zeek [86]), and raw packet headers. We observe that
HyperVision achieves 8.99%, 55.7%, 98.1% storage reduction
over the baselines, respectively. Meanwhile, our analysis shows
that HyperVision retains more traffic information than the
existing tools (see Section VII). Thus, the graph based analysis
is more efficient than these existing tools.
IX.

Task-Specific Encrypted Traffic Detection. The existing
encrypted traffic detection relies on domain knowledge for
short-term flow-level features [2], [16], [62]. For example,
Zheng et al. leveraged SDN to achieve crossfire attack detection [90], and Xing et al. designed the primitives for the
programmable switch to detect link flooding attacks [82].
For encrypted malware traffic, Bilge et al. [8] leveraged
the traffic history to detect C&C server, and Tegeler et al.
developed supervised learning using time-scale flow features
extracted from malware binaries [76]. Anderson et al. studies
the feasibility of detecting malware encrypted communication
via malformed TLS headers [3]. To the best of our knowledge,
our HyperVision is the first system that enables unsupervised
detection for the encrypted traffic with unknown patterns.

R ELATED W ORK

Encrypted Traffic Classification. HyperVision aims to identify the malicious behaviors according to encrypted traffic. It
is different from encrypted traffic classifications that decide if
the traffic is generated by certain applications or users [69].
For instance, Rimmer et al. leveraged DL for web fingerprint,
which de-anonymizes Tor traffic by classifying encrypted web
traffic [67]. Siby et al. showed that classifying encrypted
DNS traffic can jeopardize the user privacy [70]. Similarly,
Bahramali et al. classified the encrypted traffic of instant messaging applications [4]. Ede et al. designed semi-supervised
learning for mobile applications fingerprinting [78]. All these
classifications are orthogonal to HyperVision.

Graph Based Anomaly Detection. Graph based structures
have been used for task-specific traffic detection. These methods heavily rely on DPI and thus cannot be applied to detect
encrypted traffic [76]. Kwon et al. analyzed the download relationship graph to identify malware downloading [45], which
is similar to WebWitness [60]. Eshete et al. constructed HTTP
interaction graphs to detect malware static resources [24],
and Invernizzi et al. used a graph constructed from plaintext traffic to identify malware infrastructures [38]. Different
from these works, HyperVision constructs the interaction graph
without parsing specific application layer headers and thus
13

X.

C ONCLUSION

In this paper, we present HyperVision, an ML based
realtime detection system for encrypted malicious traffic with
unknown patterns. HyperVision utilizes a compact in-memory
graph to retain flow interaction patterns, while not requiring
prior knowledge on the traffic. Specifically, HyperVision uses
two different strategies to represent the interaction patterns
generated by short and long flows and aggregates the information of these flows. We develop an unsupervised graph learning
method to detect the traffic by utilizing the connectivity,
sparsity, and statistical features in the graph. Moreover, we
establish an information theory based analysis framework to
demonstrate that HyperVision preserves near-optimal information of flows for effective detection. The experiments with 92
real-world attack traffic datasets demonstrate that HyperVision
achieves at least 0.86 F1 and 0.92 AUC with over 80.6 Gb/s
detection throughput and average detection latency of 0.83s.
In particular, 44 out of the attacks can evade all five stateof-the-art methods, which demonstrate the effectiveness of
HyperVision.

R EFERENCES

[18]

——, “Network as a Security Sensor Threat Defense
with
Full
NetFlow,”
https://www.cisco.com/c/en/us/solutions/
collateral/enterprise-networks/enterprise-network-security/
white-paper-c11-736595.pdf, Accessed May 2022.

[19]

——, “RFC 3954, Cisco Systems NetFlow Services Export Version 9,”
https://doi.org/10.17487/RFC3954, Accessed May 2022.

[20]

M. Du et al., “Deeplog: Anomaly detection and diagnosis from system
logs through deep learning,” in CCS. ACM, 2017, pp. 1285–1298.

[21]

Z. Durumeric et al., “Zmap: Fast internet-wide scanning and its security
applications,” in Security. USENIX, 2013, pp. 605–620.

[22]

——, “An internet-wide view of internet-wide scanning,” in Security.
USENIX, 2014, pp. 65–78.

[23]

H. Electric, “Internet Backbone and Colocation Provider.” http://he.net/,
Accessed May 2022.

[24]

B. Eshete and V. N. Venkatakrishnan, “Dynaminer: Leveraging offline
infection analytics for on-the-wire malware detection,” in DSN. IEEE,
2017, pp. 463–474.

[25]

C. Estan and G. Varghese, “New directions in traffic measurement and
accounting: Focusing on the elephants, ignoring the mice,” ACM Trans.
Comput. Syst., vol. 21, no. 3, pp. 270–313, 2003.

[26]

X. Feng et al., “Off-path TCP exploits of the mixed IPID assignment,”
in CCS. ACM, 2020, pp. 1323–1335.

[27]

——, “Off-path network traffic manipulation via revitalized icmp redirect attacks,” in Security. USENIX, 2022.

[28]

——, “Off-path TCP hijacking attacks via the side channel of downgraded IPID,” IEEE/ACM Trans. Netw., vol. 30, no. 1, pp. 409–422,
2022.

[1]

A. Acar et al., “Peek-a-boo: i see your smart home activities, even
encrypted!” in WiSec. ACM, 2020, pp. 207–218.

[29]

[2]

B. Anderson and D. A. McGrew, “Identifying encrypted malware traffic
with contextual flow data,” in AISec. ACM, 2016, pp. 35–46.

——, “Pmtud is not panacea: Revisiting ip fragmentation attacks against
tcp,” in NDSS. ISOC, 2022.

[30]

[3]

——, “Machine learning for encrypted malware traffic classification:
Accounting for noisy labels and non-stationarity,” in SIGKDD. ACM,
2017, pp. 1723–1732.

C. Fu et al., “Realtime robust malicious traffic detection via frequency
domain analysis,” in CCS. ACM, 2021, pp. 3431–3446.

[31]

——, “Frequency domain feature based robust malicious traffic detection,” IEEE/ACM Trans. Netw., to appear.

[4]

A. Bahramali et al., “Practical traffic analysis attacks on secure messaging applications,” in NDSS. ISOC, 2020.

[32]

J. Gan and Y. Tao, “DBSCAN revisited: Mis-claim, un-fixability, and
approximation,” in SIGMOD. ACM, 2015, pp. 519–530.

[5]

D. Barradas et al., “Flowlens: Enabling efficient flow classification for
ml-based network security applications,” in NDSS. ISOC, 2021.

[33]

M. R. Garey et al., “Some simplified np-complete problems,” in STOC.
ACM, 1974, pp. 47–63.

[6]

K. Bartos et al., “Optimized invariant representation of network traffic
for detecting unseen malware variants,” in Security. USENIX, 2016,
pp. 807–822.

[34]

G. Gu et al., “Botsniffer: Detecting botnet command and control
channels in network traffic,” in NDSS. ISOC, 2008.

[35]

[7]

H. L. J. Bijmans et al., “Just the tip of the iceberg: Internet-scale
exploitation of routers for cryptojacking,” in CCS. ACM, 2019, pp.
449–464.

J. Holland et al., “New directions in automated traffic analysis,” in CCS.
ACM, 2021, pp. 3366–3383.

[36]

L. Bilge et al., “Disclosure: detecting botnet command and control
servers through large-scale netflow analysis,” in ACSAC. ACM, 2012,
pp. 129–138.

IETF, “RFC 7011, Specification of the IP Flow Information Export (IPFIX) Protocol,” https://www.rfc-editor.org/info/rfc7011, Accessed May
2022.

[37]

Intel, “Data Plane Development Kit,” https://www.dpdk.org/, Accessed
May 2022.

[9]

J. Caballero et al., “Measuring pay-per-install: The commoditization of
malware distribution,” in Security. USENIX, 2011.

[38]

L. Invernizzi et al., “Nazca: Detecting malware distribution in largescale networks,” in NDSS. ISOC, 2014.

[10]

J. Cao et al., “The loft attack: Overflowing sdn flow tables at a low
rate,” IEEE/ACM Trans. Netw., to appear.

[39]

M. Javed and V. Paxson, “Detecting stealthy, distributed SSH bruteforcing,” in CCS. ACM, 2013, pp. 85–96.

[11]

Y. Cao et al., “Off-path TCP exploits: Global rate limit considered
dangerous,” in Security. USENIX, 2016, pp. 209–225.

[40]

[12]

V. Chandola et al., “Anomaly detection: A survey,” ACM Comput. Surv.,
vol. 41, no. 3, Jul. 2009.

M. Jonker et al., “Millions of targets under attack: a macroscopic
characterization of the dos ecosystem,” in IMC. ACM, 2017, pp.
100–113.

[41]

[13]

CIC, “Canadian Institute for Cybersecurity Datasets.” https://www.unb.
ca/cic/datasets/index.html, Accessed May 2022.

M. S. Kang et al., “The crossfire attack,” in SP.
127–141.

[42]

[14]

——, “DDoS Evaluation Datasets (CIC-DDoS2019),” https://www.unb.
ca/cic/datasets/ddos-2019.html, Accessed May 2022.

Kaspersky, “Kaspersky Security Bulletin 2020. Statistics,” https://
go.kaspersky.com/rs/802-IJN-240/images/KSB statistics 2020 en.pdf,
Accessed May 2022.

[15]

——, “Intrusion Detection Evaluation Datasets (CIC-IDS2017),” https:
//www.unb.ca/cic/datasets/ids-2017.html, Accessed May 2022.

[43]

D. Kopp et al., “Ddos hide & seek: On the effectiveness of a booter
services takedown,” in IMC. ACM, 2019, pp. 65–72.

[16]

Cisco, “Cisco Encrypted Traffic Analytics,” https://www.cisco.com/
c/en/us/solutionsenterprise-networks/enterprise-network-security/eta.
html, Accessed May 2022.

[44]

A. Kuzmanovic and E. W. Knightly, “Low-rate tcp-targeted denial of
service attacks: the shrew vs. the mice and elephants,” in SIGCOMM.
ACM, 2003, pp. 75–86.

[17]

——, “Cisco SPAN.” https://www.cisco.com/c/en/us/support/docs/
swit-ches/catalyst-6500-series-switches/10570-41.html, Accessed May
2022.

[45]

B. J. Kwon et al., “The dropper effect: Insights into malware distribution
with downloader graph analytics,” in CCS. ACM, 2015, pp. 1118–
1129.

[8]

14

IEEE, 2013, pp.

[46]

C. Lever et al., “A lustrum of malware network communication:
Evolution and insights,” in SP. IEEE, 2017, pp. 788–804.

[74]

[47]

G. Li et al., “Enabling performant, flexible and cost-efficient ddos
defense with programmable switches,” IEEE/ACM Trans. Netw., vol. 29,
no. 4, pp. 1509–1526, 2021.

[75]

[48]

Q. Li et al., “Dynamic network function enforcement via joint flow
and function scheduling,” IEEE Trans. Inf. Forensics Secur., vol. 17,
pp. 486–499, 2022.

[76]

[49]

——, “Efficient forwarding anomaly detection in software-defined
networks,” IEEE Trans. Parallel Distributed Syst., vol. 11, pp. 2676–
2690, 32.

[77]
[78]

[50]

E. Liu et al., “Reasoning analytically about password-cracking software,” in SP. IEEE, 2019, pp. 380–397.

[79]

[51]

Z. Liu et al., “Jaqen: A high-performance switch-native approach for
detecting and mitigating volumetric ddos attacks with programmable
switches,” in Security. USENIX, 2021, pp. 3829–3846.

[80]

[52]

X. Luo and R. K. C. Chang, “On a new class of pulsing denial-ofservice attacks and the defense,” in NDSS. ISOC, 2005.

[82]

[53]

R. Merget et al., “Scalable scanning and automatic classification of
TLS padding oracle vulnerabilities,” in Security. USENIX, 2019, pp.
1029–1046.

[83]

[54]

R. Miao et al., “The dark menace: Characterizing network-based attacks
in the cloud,” in IMC. ACM, 2015, pp. 169–182.

[84]

[55]

Microsoft, “A Theorem Prover from Microsoft Research.” https://
github.com/Z3Prover/z3, Accessed May 2022.

[85]

[56]

Y. Mirsky et al., “Kitsune: An ensemble of autoencoders for online
network intrusion detection,” in NDSS. ISOC, 2018.

[57]

mlpack, “Mlpack: Open source machine learning library,” https://www.
mlpack.org/, accessed May 2022.

[58]

A. Nappa et al., “Cyberprobe: Towards internet-scale active detection
of malicious servers,” in NDSS. ISOC, 2014.

[59]

R. NCC, “the RIPE NCC is building the largest Internet measurement
network ever made.” https://atlas.ripe.net/, Accessed May 2022.

[60]

T. Nelms et al., “Webwitness: Investigating, categorizing, and mitigating
malware download paths,” in Security. USENIX, 2015, pp. 1025–1040.

[61]

A. Oest et al., “Sunrise to sunset: Analyzing the end-to-end life cycle
and effectiveness of phishing attacks at scale,” in Security. USENIX,
2020, pp. 2039–2056.

[62]

E. Papadogiannaki and S. Ioannidis, “A survey on encrypted network
traffic analysis applications, techniques, and countermeasures,” ACM
Comput. Surv., vol. 54, no. 6, pp. 123:1–123:35, 2021.

[63]

PcapPlusPlus, “A C++ Library for Capturing, Parsing and Crafting of
Network Packets,” https://pcapplusplus.github.io/, Accessed May 2022.

[64]

G. Pellegrino et al., “Deemon: Detecting CSRF with dynamic analysis
and property graphs,” in CCS. ACM, 2017, pp. 1757–1771.

[65]

Z. Qian and Z. M. Mao, “Off-path TCP sequence number inference
attack - how firewall middleboxes reduce security,” in SP. IEEE, 2012,
pp. 347–361.

[66]

P. Richter and A. W. Berger, “Scanning the scanners: Sensing the
internet from a massively distributed network telescope,” in IMC.
ACM, 2019, pp. 144–157.

[67]

V. Rimmer et al., “Automated website fingerprinting through deep
learning,” in NDSS. ISOC, 2018.

[68]

D. Rupprecht et al., “Call me maybe: Eavesdropping encrypted LTE
calls with revolte,” in Security. USENIX, 2020, pp. 73–88.

[69]

M. Shen et al., “Accurate decentralized application identification via
encrypted traffic analysis using graph neural networks,” IEEE Trans.
Inf. Forensics Secur., vol. 16, pp. 2367–2380, 2021.

[70]

S. Siby et al., “Encrypted DNS -> privacy? A traffic analysis perspective,” in NDSS. ISOC, 2020.

[71]

A. K. Sikder et al., “6thsense: A context-aware sensor-based attack
detector for smart devices,” in Security. USENIX, 2017, pp. 397–414.

[72]

——, “Aegis: a context-aware security framework for smart home
systems,” in ACSAC. ACM, 2019, pp. 28–41.

[73]

Stratosphere, “Real Malware Traffic Captures.” https://www.
strato-sphereips.org/datasets-overview, Accessed May 2022.

[81]

[86]
[87]
[88]
[89]
[90]

[91]

Suricata, “An Open Source Threat Detection Engine,” https://
suricata-ids.org/, Accessed May 2022.
R. Tang et al., “Zerowall: Detecting zero-day web attacks through
encoder-decoder recurrent neural networks,” in INFOCOM. IEEE,
2020, pp. 2479–2488.
F. Tegeler et al., “Botfinder: finding bots in network traffic without deep
packet inspection,” in CoNEXT. ACM, 2012, pp. 349–360.
K. Thomas et al., “Data breaches, phishing, or malware?: Understanding
the risks of stolen credentials,” in CCS. ACM, 2017, pp. 1421–1434.
T. van Ede et al., “Flowprint: Semi-supervised mobile-app fingerprinting
on encrypted network traffic,” in NDSS. ISOC, 2020.
Z. Wang et al., “Symtcp: Eluding stateful deep packet inspection with
automated discrepancy discovery,” in NDSS. ISOC, 2020.
WIDE, “MAWI Working Group Traffic Archive,” http://mawi.wide.ad.
jp/mawi/, Accessed May 2022.
R. Xie et al., “Disrupting the sdn control channel via shared links:
Attacks and countermeasures,” IEEE/ACM Trans. Netw., to appear.
J. Xing et al., “Ripple: A programmable, decentralized link-flooding
defense against adaptive adversaries,” in Security. USENIX, 2021, pp.
3865–3880.
R. Yang et al., “Uiscope: Accurate, instrumentation-free, and visible
attack investigation for GUI applications,” in NDSS. ISOC, 2020.
T. Yang et al., “Elastic sketch: adaptive and fast network-wide measurements,” in SIGCOMM. ACM, 2018, pp. 561–575.
R. Zamir, “A proof of the fisher information inequality via a data
processing argument,” IEEE Trans. Inf. Theory, vol. 44, no. 3, pp. 1246–
1250, 1998.
Zeek, “An Open Source Network Security Monitoring Tool,” https://
zeek.org/, Accessed May 2022.
J. Zeng et al., “WATSON: abstracting behaviors from audit logs via
aggregation of contextual semantics,” in NDSS. ISOC, 2021.
M. Zhang et al., “Poseidon: Mitigating volumetric ddos attacks with
programmable switches,” in NDSS. ISOC, 2020.
Z. Zhao et al., “Achieving 100gbps intrusion prevention on a single
server,” in OSDI. USENIX, 2020, pp. 1083–1100.
J. Zheng et al., “Realtime ddos defense using cots sdn switches via
adaptive correlation analysis,” IEEE Trans. Inf. Forensics Secur., vol. 13,
no. 7, pp. 1838–1853, 2018.
S. Zhu et al., “You do (not) belong here: detecting DPI evasion attacks
with context learning,” in CoNEXT. ACM, 2020, pp. 183–197.

A PPENDIX
A. Details of Implementations
We present the details of the flow classification and short
flow aggregation algorithm in Algorithm 1 and 2, respectively.
The features used for edge pre-clustering and clustering are
shown in Table V. And Table VII shows the hyper-parameters
used in HyperVision and the recommended values.

15

TABLE V.

T HE FEATURES OF EDGES USED IN H YPERV ISION .

statistical

Edge Denoting Long Flows

structural

statistical

structural

Edge Denoting Short Flows

Edge Group Data

TABLE VII.

Description

Group

bool
Denoting short flows with the same source address.
bool
Denoting short flows with the same source port.
bool
Denoting short flows with the same destination address.
bool
Denoting show flows with the same destination port.
int
The in-degree of the connected source vertex.
int
The out-degree of the connected source vertex.
int
The in-degree of the connected destination vertex.
int
The out-degree of the connected destination vertex.
int
The number of flows denoted by the edge.
int The length of the feature sequence associated with the edge.
int
The sum of packet lengths in the feature sequence.
int
The mask of protocols in the feature sequence.
float
The mean of arrival intervals in the feature sequence.

Description

Value

PKT TIMEOUT
FLOW LINE
AGG LINE

Flow completion time threshold.
Flow classification threshold.
Flow aggregation threshold.

10.0s
15
20

Graph PreProcessing


minPoint

DBSCAN hyper-parameters for
clustering components and edges.

4 × 10−3
40

Traffic
Detection

K
T
α
β
γ

K-means hyper-parameter.
Loss threshold for malicious traffic.

10
10.0
0.1
0.5
1.7

Graph
Construction

int
The in-degree of the connected source vertex.
int
The out-degree of the connected source vertex.
int
The in-degree of the connected destination vertex.
int
The out-degree of the connected destination vertex.
float
The flow completion time of the denoted long flow.
float
The packet rate of the denoted long flow.
int
The number of packets in the denoted long flow.
int The maximum bin size for fitting packet length distribution.
int
The length associated with the maximum bin size.
int
The maximum bin size for fitting protocol distribution.
int
The protocol associated with the maximum bin size.

ck
rce
oof

Brute Scanning

Encrypted Web Traffic
SMTP
Web Attacks
SSL

Encrypted Flooding Traffic
Password
SSH
Link Flooding
Cracking
Inject

Malware Related Encrypted Traffic
RansomSpyware
Botware
Adware
Miner
ware

Class

Dataset
Label

1
2

Magic.
Magic Hound spyware.
Trickster
Encrypted C&C connections.
Plankton
Pulling components from CDN.
Penetho
Wifi cracking APK spyware.
Zsone
Multi-round encrypted uploads.
CCleaner
Unwanted software downloads.
Feiwo
Encrypted ad API calls.
Mobidash
Periodical statistic ad updates.
WebComp.
WebCompanion click tricker.
Adload
Static resources for PPI adware.
Svpeng Periodical C&C interactions (10s).
Koler
Invalid TLS connections.
Ransombo Executable malware downloads.
WannaL. Wannalocker delivers components.
Dridex
Victim locations uploading.
BitCoinM.
Abnormal encrypted channels.
TrojanM. Long SSL connections to C&C.
CoinM.
Periodical connections to pool.
THBot
Getting C&C server addresses.
Emotet
Communication to C&C servers.
Snojan
PPI malware downloading.
Trickbot
Connecting to alternative C&C.
Mazarbot Long C&C connections to cloud.
Sality
A P2P botware.

Att.1 Vic. B.W.2
2
2
3
1
1
4
3
3
3
1
2
3
5
2
1
1
3
1
4
6
3
4
3
20

4

6

197
278
503
5.57
3.25
1.90
1.78
0.28
1.83
0.63
1.70
2.76
1.39
2.49
5.53

100%
100%
100%
100%
100%
100%
100%
100%
100%
100%
100%
100%

Oracle
XSS
SSLScan
Param.Inj.
Cookie.Inj.
Agent.Inj.
WebCVE
WebShell
CSRF
Crawl
Spam1
Spam50
Spam100

1
1
1
1
1
1
1
1
1
1
1
1
1

3.99
31.8
15.0
17.1
39.6
19.7
2.30
11.2
7.73
29.7
36.2
61.7
88.9

100%
100%
100%
100%
100%
100%
100%
100%
100%
100%
100%
100%
100%

ICMP
NTP
SSH
SQL
DNS
HTTP
HTTPS
SYN
RST

We use the brute force scanning
rates identified by darknet
in [22]. We reproduce the
scan using Zmap which targets
the peers and customers
of AS 2500.
We use the protocol types and

1
1
1
1
1
1
1
1
1
1
1
50
100

1
211K 5.61
1 99.3K 3.87
1
205K 5.79
1
112K 3.04
1
198K 6.61
1 93.7K 2.68
1
209K 4.89
6.50K 1 11.41
32.5K 1
5.79

-

if Hash(pkt) not in FlowHashTable then
FlowHashTable adds an entry for pkt.
FlowHashTable[Hash(pkt)] appends pkt.
if time now − last check > JUDGE INTERVAL then
for flow in FlowHashTable do

// Judge the completion of flows.
8

if time now − flow[−1].time > PKT TIMEOUT then

// Classify the flow via the number of packets.

479 0.34 0.13%
793 0.63 10.0%
579 59.2 23.8%
516 3.57 100%
479 5.98 93.0%
466 28.1 4.09%
1.00K 19.8 100%
624 6.08 100%
281 8.38 55.2%
280 1.04 1.09%
403 1.21 1.26%
333 2.22 100%
369 58.6 42.7%
275 7.49 30.3%
429 4.10 100%
1.54K 0.79 100%
1.37K 2.39 89.4%
1.40K 0.21 100%
103 1.72 2.71%
1.17K 1.43 68.6%
326 8.94 100%
347 0.57 100%
409 6.13 30.9%
247 2.19 100%
313
313
313
1
1
1
2
2
1
19
43
83
35
257
486

TLS padding Oracle.
Xsssniper XSS detection.
SSL vulnerabilities detection.
Commix parameter injection.
Commix cookie injection.
Commix agent-based injection.
Exploiting CVE-2013-2028.
Exploiting CVE-2014-6271.
Bolt CSRF detection.
A crawler using scrapy.
Spam using SMTP-over-SSL.
Encrypted spam with 50 bots.
Brute spam using 100 bots.

7

Enc.
Ratio

CrossfireS. We use the botnet cluster sizes
100
CrossfireM. and the ratio of decony servers
200
CrossfireL.
(HTTPS) in [41].
500
LrDoS 0.2 We use the traffic of an encrypted 1
LrDoS 0.5 video application and the settings
1
LrDoS 1.0
in WAN experiments [44]
1
ACK Inj. SSH injection via ACK rate-limits. 1
IPID Inj. SSH injection via IPID counters.
1
IPID Port
Requires of the SSH injection.
1
Telnet S.
Telnet servers in AS38635.
1
Telnet M.
Telnet servers in AS2501.
1
Telnet L.
Telnet servers in AS2500.
1
SSH S.
SSH servers in AS9376.
1
SSH M.
SSH servers in AS2500.
1
SSH L.
SSH servers in AS2501.
1

Input: Per-packet features: PktInfo, the hash table for flow collecting:
FlowHashTable.
Output: Classified flows: ShortFlow and LongFlow.
time now := PktInfo[0].time, last check := time now.
for pkt in PktInfo do

// Aggregate packets into flows.
3

D ETAILS OF MALICIOUS TRAFFIC DATASETS .
Description

Balancing the terms in
the loss function.

Algorithm 1: Secure flow classification.

5

TABLE VI.

R ECOMMENDED HYPER - PARAMETER CONFIGURATION .
Hyper-Parameter

10

if flow.size > FLOW LINE then
ShortFlow adds flow.

11

else

9

LongFlow adds flow.

12
13

FlowHashTable clears the states of flow.

14

last check ← time now. // Record the time of checking.

15

time now ← pkt.time. // Update the timer.

Algorithm 2: Short flow aggregation.

1

Input: Short flows: ShortFlow.
Output: Constructed edges: ShortEdge.
Initialize ProtoHashTable as an empty table.

// Select candidate protocols for the aggregation.
2

for flow in ShortFlow do

// Calculate the protocol mask of a short flow.
3
4
5
6

flow proto := (flow[0].proto|...|...|flow[−1].proto).
if Hash(flow proto) not in ProtoHashTable then
ProtoHashTable adds an entry for flow proto.
Append flow to ProtoHashTable[Hash(flow proto)].

// Perform the source aggregation.
for flows in ProtoHashTable with same protocols do
SrcAddrTable collects the flows with same sources in flows.
9
for sflow in SrcAddrTable do

7

8

// The flows can be aggregated and denoted by one edge.
10
11
12
13

if sflow.size > AGG LINE then
edge.features := sflow[0].features.
edge.source := sflow[0].source.
if an unique destination in sflow then

// Source and destination aggregation.
edge.destination saves the unique destination.

14
15

else

// Source aggregation only.
16
17
18
19
20

Record each destination in sflow.
Add the constructed edge to ShortEdge.
SrcAddrTable evicts sflow.
DstAddrTable collects flows with same destinations.
Inspect the flows with the same destinations similarly.

// Process short flows which cannot be aggregated.
21

16

ShortEdge adds flows in SrcAddrTable and DstAddrTable.

B. Details of Experiments
1) Details of Datasets: We present the detailed properties
of the 80 newly collected datasets in Table VI, including the
number of attackers and victims, the packet rates of attack
flows, and the ratios of encrypted traffic. All the datasets
are collected and labeled using the same method as MAWI
datasets [80] and CIC datasets [14], [15].

We observe that ∂H[I∂qEve. ] ≈ 0 when q > 0.5. Thus, we use
the second-order taylor series of q to approach HEve. :

2) Detection Accuracy of Other Datasets: We use 12
existing datasets to eliminate the impact of dataset bias.
Overall, HyperVision achieves 7.8%, 11.0%, 5.1% F1 improvements over the best accuracy of the baselines on Kitsune
datasets [56], CIC-IDS2017 datasets [15], and CIC-DDoS2019
datasets [14], respectively. From the Kitsune datasets, we
validate the correctness of the deployed baselines.

where θ = ηζ , ζ = q − qps , and η = q − ps (q − 1). Similarly,
we obtain the expected data scale LEve. and the information
density DEve. :

s

HEve. =

DEve. =

XSamp. =

=−

ps
,
η

HEve.
2ζ
= s · ln θ.
LEve.
p

(24)

L
X

si ,

si ∼ B(s, p) ⇒ XSamp. ∼ B(Ls, p).

(25)

i=1

The amount of the information recorded by the sampling
based mode is the Shannon entropy of XSamp. . We decompose
the entropy as conditional entropy and mutual information:
HSamp. = H[XSamp. ]
= H[XSamp. |L] + I(XSamp. ; L).

(26)

We assume that the mutual information between the sequence length L and the accumulative statistic XSamp. is close
to zero. It implies the impossibility of inferring the statistic
from the length of the packet sequence. Then we obtain a
lower bound of the entropy as an estimation which is verified
to be a tight bound via numerical analysis:

C. Details of Theoretical Analysis
1) Analysis of Event based Mode: Let random variable
IEve. indicate if the event based mode records an event for a
flow denoted by a random variable sequence, hs1 , s2 , . . . , sL i,
L ∼ G(q). And we assume that the mode can merge repetitive
events. First, we obtain the probability distribution of the
random variable IEve. :


H

Samp. = H[XSamp. |L]

∞
P

P[L = l] · H[XSamp. |L = l]
l=1
= 21 ln 2πelsp(1 − p),
∞
qX
l−1

=

H[XSamp. |L = l]
1
⇒ HSamp. = ln 2πesp(1 − p) +
2
2

P[IEve. = 1] = 1 − P[IEve. = 0],
∞
X
P[IEve. = 0] =
P[L = l] · P[IEve. = 0|L = l]



(1 − q)

ln l.

(27)

l=1

(21)

We observed that the second-order taylor series can accurately approach the second term of the entropy:

l=1
s

=

ps
ps (1 − q) + q

2) Analysis of Sampling based Mode: We use XSamp.
to denote the random variable to be recorded as the flow
information in the sampling based mode which is the sum
of the observed per-packet features denoted by the random
variable sequence. We can obtain the distribution of XSamp.
as follows:

The reason why the obfuscation techniques incur negligible
accuracy decrease is that they only manipulate patterns of a
single flow. HyperVision can still detect the evasion attacks by
learning the interaction patterns among various flows.

(1 − q)l−1 · q · (1 − ps )l

(23)

= −2θ ln θ,

Here, we complete the analysis for the event based mode.

4) Robustness Against Obfuscation Techniques: We validate our method under evasion attacks with different obfuscation techniques according to a recent study [30], i.e., injecting
three kinds of benign traffic. The results demonstrate that the
accuracy decrease incurred by the obfuscation is bounded by
4.3% F1. Specifically, when benign TLS traffic, UDP video
traffic, and normal ICMP traffic is injected into brute force
attack traffic, the average F1 decreases by 1.7%, 0.9%, and
2.4%, respectively.

=

ps (q − 1) − q

LEve. = P[IEve. = 1] =

3) Long-run Performances: By using the CIC datasets [14],
[15], we validate the long-run performances of HyperVision.
Specifically, the experiments show that HyperVision achieves
over 0.95 F1 and 0.99 AUC in long-run detection (6∼8 hours).
The results also verify that the accumulation of detection errors
cannot interfere with HyperVision, and HyperVision can detect
multiple attacks simultaneously even in the presence of attacks
with changed addresses. Moreover, the memory consumption
of the compact graph is bounded by 15.6 GB.

l=1
∞
X

−1)q
2q(1 − ps ) ln[ ps(p(q−1)−q
]

q(1 − p )
.
1 − (1 − q)(1 − ps )

HSamp. =

1
ln 2
ln 2πesp(1 − p) +
q(1 − q).
2
2

(28)

Then, we obtain the entropy of the random variable IEve. :
Finally, we obtain the expected data scale and the information density similar to the analysis for the event based mode
and complete the analysis for the sampling based mode.

HEve. = H[IEve. ] =
(22)
−P[IEve. = 0] ln P[IEve. = 0] − P[IEve. = 1] ln P[IEve. = 1].

17

3) Analysis of Graph based Mode in HyperVision: HyperVision applies different recording strategies for short and long
flows, i.e., when L > K it extracts the histogram for long
flow feature distribution fitting, and when L ≤ K it records
detailed per-packet features and aggregates short flows. Let
XH.V. denote the random set of the recorded information. For
short flows, all the random variables are collected in XH.V. .
For long flows, XH.V. collects s counters of the histogram
for each state on the state diagram of the DTMC. First, we
decompose the entropy of the graph based recording mode as
the terms for short and long flows:
HH.V. = H[XH.V. |L] =

∞
X

Basing on the distribution of the collected counters, we
obtain the entropy of the random set:


L

H[XH.V. |L]

=

K
P

P[L = l] · H[XH.V. |L = l]

=

∞
X
l=K+1
∞
X

i −sp

1
ln 2πel (sp) i!e
2
s
P
H[υi |L = l],

(35)

i=1

L
P[L = l] · H[XH.V.
|L = l]

q(1 − q)l−1 ·

s
X
1
i=1

l=K+1

(29)

2

ln 2πel

(sp)i e−sp
i!

K

=

P[L = l] · H[XH.V. |L = l]

l=1
∞
P

L
H[XH.V.
|L = l]

=

l=1

=

=

L
H[XH.V.
|L] =

S
L
= H[XH.V.
|L] + H[XH.V.
|L]



S

|L]
H[XH.V.


H[υi |L = l]

(1 − q)
s(s + 1)
[s ln 2πe +
ln sp
2
2
∞
s
X
qs X
− sp2 −
(1 − q)l−1 ln l].
ln i!] + [
2
i=1
l=K+1

P[L = l] · H[XH.V. |L = l].

The assumption of q > 0.5 implies K th order taylor series
can accurately approach the last term in (35). Moreover,
we
Ps
utilize the quadric term of s in the taylor series of i=1 ln i!
to approach the entropy of long flows (γ is Euler–Mascheroni
constant):

l=K+1

Short Flow Information. HyperVision records detailed perpacket feature sequences for short flows which is the same as
the brute recording in the idealized mode. Thus, the increasing
rate of information equals the entropy rate of the DTMC:

1
s(1 − q)K [(1 + s) ln ps+
4
2 ln 2πe + 2q ln K − 2s(1 + p + γ)].

L
H[XH.V.
|L] =

H[XH.V. |L = l] = l · H[G],
S
H[XH.V.
|L] =

K
X

(30)

P[L = l] · l · H[G]

Finally, we take (31) and (36) in (29) and complete the
analysis for the entropy of the graph based recording mode.
Similarly, we obtain the expected data scale by analyzing the
conditions of short and long flows separately:

l=1
K
X
= q · H[G] ·
(1 − q)l−1 · l

(31)

l=1

=

1 − (Kq + 1)(1 − q)K
· H[G].
q

LH.V. = E[LSH.V. |L] + E[LL
H.V. |L]
=

Long Flow Information. When L > K, the random set
collects the counters for distribution fitting. When the DTMC
has s states, the histogram has s counters υ1 , υ2 , . . . , υs , i.e.,
XH.V. = {υ1 , υ2 , . . . , υs }. We assume that the counters are
independent:
υi =

L
X
j=1

δj ,

(
1,
δj =
0,

if sj is the ith state
else.

= s(1 − q)K +

(32)

i −sp

υi ∼π(L · P[si = i])
λi =

(sp)i e−sp
.
i!

∞
X
L
+
s · P[L = l]
C
l=K+1

(37)

1 − (Kq + 1)(1 − q)
,
Cq

where C is the average number of flows denoted by an edge
associated with short flows. Also, we obtain the expected
information density by its definition: DH.V. = HH.V. /LH.V.
and complete the analysis for the graph based recording mode
used by HyperVision.

as an
To obtain the closed-form solution, we use (sp) i!e
estimation of Csi pi (1 − p)s−i . Moreover, the length of the perpacket feature sequence of a long flow is relatively large which
implies υi approaches a Poisson distribution:

∼π(λi ),

P[L = l] ·

K

(33)

∼ B(L, Csi pi (1 − p)s−i ).

K
X
l=1

We observe that hυ1 , υ2 , . . . , υs i is a binomial process:
υi ∼ B(L, P[si = i])

(36)

(34)

18
PAPER_TEXT
