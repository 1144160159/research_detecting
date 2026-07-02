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
# [545] SENTINEL: Insider Threat Detection Based on Multi-Timescale User Behavior Interaction Graph Learning
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
编号：545
题名：SENTINEL: Insider Threat Detection Based on Multi-Timescale User Behavior Interaction Graph Learning
年份：2024
DOI：10.1109/tnse.2024.3519155
来源：IEEE Transactions on Network Science and Engineering
PDF：paper/10.1109_TNSE.2024.3519155.pdf
已有粗分类：图学习、知识图谱与威胁情报
二级关联：恶意流量、暗网与攻击检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\545.txt
- 原始字符数：90156
- 本次发送字符数：90156
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
774

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 12, NO. 2, MARCH/APRIL 2025

SENTINEL: Insider Threat Detection Based
on Multi-Timescale User Behavior
Interaction Graph Learning
Fengrui Xiao , Student Member, IEEE, Shuangwu Chen , Member, IEEE, Siyang Chen, Student Member, IEEE,
Yuanyi Ma , Student Member, IEEE, Huasen He , Member, IEEE, and Jian Yang , Senior Member, IEEE

Abstract—Insider threats have become a prominent driver behind a myriad of cybersecurity incidents in recent years. Since
the threats take place within intranet, traditional security devices located at the network perimeter can hardly detect them.
The trust management methods employed within the organization are likewise incapable of intercepting access actions already
authenticated with valid credentials. In this paper, we propose a
novel insider threat detection method named SENTINEL, which
identifies abnormal behavior of insiders and provides fine-grained
threat intelligence. We devise a dynamic user behavior interaction
graph (BIG), which jointly considers the spatial distribution of
user behavioral trajectories among the network topology and the
temporal variations of user behavioral profiles. By incorporating a
spatio-temporal graph neural network, SENTINEL is able to learn
the operation regularities of users at specific times and respective
positions in BIG. In order to perceive both the abrupt and persistent threats simultaneously, we conceive a multi-timescale fusion
mechanism for detecting users’ activities at different timescales.
SENTINEL implements a log-entry-level detection without requiring any attack samples during model training. The experiments
conducted on widely-used public datasets demonstrate that SENTINEL achieves superior performance while maintaining a relatively low computational overhead compared to the state-of-the-art
methods.
Index Terms—Insider threat detection, graph neural network,
anomaly detection, behavior interaction graph (BIG).

I. INTRODUCTION
MIDST the rapidly evolving landscape of network security, insider threats have become a prominent driver behind
a myriad of cybersecurity incidents in recent years, which have
inflicted substantial detriment upon government, enterprises and
education networks. Insider threats commonly emerges from
the actions of either malicious or unintentional insiders, who
exploit their authorized access to negatively affect the reliability
of the organization’s information systems [1]. According to

A

Received 5 November 2023; revised 24 October 2024; accepted 12 December
2024. Date of publication 17 December 2024; date of current version 24
February 2025. This work was supported in part by the National Natural Science
Foundation of China under Grant U23A20275 and Grant 62101525 and in
part by the China Environment for Network Innovations (CENI) under Grant
2016-000052-73-01-000515. Recommended for acceptance by Dr. Baochun Li.
(Corresponding author: Shuangwu Chen.)
The authors are with the Department of Automation, University of Science
and Technology of China, Hefei 230026, China (e-mail: chensw@ustc.edu.cn).
Digital Object Identifier 10.1109/TNSE.2024.3519155

Ponemon’s 2022 Insider Threat Report [2], there has been a significant 44% increase in insider threat incidents over the past two
years and the financial impact of each incident has risen by more
than a third, with the amount of money lost per incident reaching
a staggering $15.38 million. In contrast to external attacks that
need to breach security perimeter, attacks from insiders are more
pernicious because the malicious insiders are well-acquainted
with core secrets and may already have delegated authority to
access sensitive data. Hence, insider threat poses serious security
risks and potential harm to the organization’s network.
Detecting insider threat still face many challenges for businesses and organizations of all sizes and across diverse industries. Firstly, due to their position within security perimeter,
internal employees can inadvertently launch attacks without
triggering alarms from security devices. Besides, these insiders
with privileged access can leverage the credentials associated
with their working accounts to circumvent the multi-layer trust
management mechanisms within the organization [3]. Secondly,
malicious activity carried out by insiders is relatively uncommon. As a result, there is often limited available data to describe
and analyze such activities [4]. Thirdly, for the sake of exfiltrating confidential files, tampering with sensitive data, and sabotaging system components, insider threats perpetrators would
move laterally across multiple hosts in the target network using
stolen credentials and accounts [5]. The attacker’s footprints
could be fragmented and scattered across various user and host
records, which makes it difficult to raise security personnel’s
attention. Lastly, well-planned attackers usually employ sophisticated strategies, like multistage persistent threats and mimicry
attacks, to circumvent detection [6].
Massive efforts have been made to promptly detect insider
threats. Existing insider threat detection methods can be roughly
divided into three categories: rule-based methods, machine
learning based methods, and graph-based methods [7]. Rulebased methods [8], [9], [10] employ manually defined rules
to detect data leakage, which however heavily rely on expert
knowledge, and thus can hardly handle attacks beyond predefined rules and prior experiences. Machine learning based [1],
[4], [11], [12] approaches necessitate manual design of feature
engineering and employ techniques such as Markov models or
deep learning models to accomplish the detection task. Moreover, machine learning algorithms face the challenges of feature
redundancy, feature correlation, and temporal-spatial feature

2327-4697 © 2024 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

XIAO et al.: SENTINEL: INSIDER THREAT DETECTION BASED ON MULTI-TIMESCALE USER BEHAVIOR INTERACTION GRAPH LEARNING

processing [13] and rely on large volumes of labeled data to
learn patterns of malicious activity. However, for insider threat
detection, obtaining sufficiently high quality labeled data is very
difficult. Lack of sufficient labeled data can result in inadequate
or biased training of the model. Graph-based methods leverage the sequential relationships between log entries to learn
normal patterns from graph structures (e.g. user authentication
networks and lateral movement traces) [14], [15], [16], [17].
Existing graph-based insider threat detection methods usually
treat operation logs as nodes and attempt to convert log records
into a graph according to correlation relationships among them,
which incurs high computational burden and lengthy execution
times for large-scale graph learning.
Inspired by the limitations of current researches, we propose
a novel insider threat detection method named SENTINEL,
which provides a systematic and dynamic perspective on users’
behavior within the intranet. Since insider threats often involve
multiple stages, including reconnaissance, lateral movement,
foothold establishment, and remote command and control, the
behavior patterns of malicious insiders would exhibit temporal
dependencies. Meanwhile, the network within organizations
typically is comprised of multiple subnets and regions with
specific network topologies. Thus, it is possible that the attackers
need to traverse across various network regions or subnets to
gain access to diverse systems during the execution of threat
activities. This topological constraint indicates the spatial dependencies of insider threats. Based on this observation, we
model user behaviors in different time periods into dynamic
graph instances and develop an insider threat detection model
using spatio-temporal graph neural network (ST-GNN). However, existing graph learning-based methods [14], [16], [18], [19]
for insider threat detection generally treat logs as nodes, which
results in extremely large graphs and significant computational
overhead. In contrast, SENTINEL treats user interaction behavior logs between network hosts as edges rather than nodes of
the graph, which greatly reduces the amount of nodes in graphs
and thereby alleviates computational burden. Besides, analyzing
insider threats requires investigating and processing diverse and
voluminous users’ log data [1], such as network traffic, file
access records, logon authentication events, etc. Fusing such
a substantial volume of data to capture complex relationships
is a tricky problem. Nevertheless, traditional ST-GNN models
only focus on the propagation of node attributes, but ignore the
edges attributes. In this paper, edges represent user interactions
between hosts, and their attributes often reflect the behavioral
routines of different users. We can profile a user behavioral
baseline based on the edge attributes, which plays a more critical
role than the node attributes in our insider threat detection. To
address this problem, we leverage an Edge Graph Attention
(EGAT) mechanism [20] to acquire the feature representations
of various operation types among system hosts, which allows
us to capture the behavioral pattern implied by edge attributes.
Moreover, in practical applications, abrupt threats and persistent
threats may exist at the same time. To deal with a broad range
of attack scenarios, we integrate user behavior states at multiple
timescales into the detection model, which enables SENTINEL
to capture dependencies in user behavior over different time

775

intervals [21]. Through this way, SENTINEL not only excels
in rapidly responding sudden dangerous actions, but also can
perceive the long-term evolutionary pattern of user behavior.
Furthermore, to deal with the insufficiency of abnormal samples,
a semi-supervised insider threat detection algorithm is proposed,
which solely requires the training data to be benign.
Our contributions of this paper are fourfold as follows:
r We propose SENTINEL, an insider threat detection algorithm, to identify abnormal behavior of insiders and to
provide fine-grained threat intelligence. SENTINEL implements a log-entry-level detection without requiring any
attack samples during model training.
r We devise a dynamic user behavior interaction graph
(BIG), which jointly considers the spatial distribution of
user behavioral trajectories among the network topology
and the temporal variations of user behavioral profiles. By
incorporating ST-GNN with edge feature enhancement,
the BIG achieves accurate modeling of spatio-temporal
relationships between nodes, enhancing the representative
ability of user behaviors.
r In order to perceive both the abrupt and persistent threats
simultaneously, we conceive a multi-timescale fusion
mechanism for incorporating users’ activities at different
timescales. With the help of the temporal hierarchy aggregation layer, the multi-level temporal interaction context
is explicitly embedded into the potential representation of
timescale-aware.
r We conduct experiments on three public datasets to compare the performance of SENTINEL to the state-of-theart methods. The results demonstrate that SENTINEL
achieves superior AUC value of 0.980 while maintaining a
relatively low computational overhead.
The rest of our paper is organized as follows. Section II
summarizes the related work. Section III describes our threat
model and challenges, and the detailed system architecture is
proposed in Section IV. Section V presents the comparative
experiments. Finally, we conclude this paper in Section VII.
II. RELATED WORK
Existing Researches on insider threat detection can be divided
into three categories: rule matching based methods, machine
learning based methods, and graph-based methods.
Rule matching has been widely applied in insider threat
detection. Early detection tools, such as Addamark LMS [8] and
Splunk [9], primarily generated alerts by monitoring users’ log
files or network requests and matching configurable rule lists.
With the help of these tools, security analyst could determine
the pertinent log files to assess and prescribe appropriate alert
actions [22]. Although these offline tools or schemes could be
executed multiple times within an hour or a day, they lacked
the capacity to conduct longitudinal log analysis or proactively
respond in real-time. To remedy these deficiencies and deal
with new emerged Advanced Persistent Threat (APT), Milajerdi
et al. [10] utilized the Tactics, Techniques, and Procedures
(TTPs) abstract rules based on MITER’s ATT&CK framework [23], and mapped the low-level audit logs to the high-level

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

776

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 12, NO. 2, MARCH/APRIL 2025

attack kill chain stages. Though rule matching approaches have
demonstrated favorable performance in insider threat scenarios,
they necessitate substantial expert and prior knowledge [16] and
face challenges in adapting to the constantly evolving landscape
of network attacks.
Given massive data generated daily within organizations,
machine learning based detection methods have emerged as one
of the most promising ways for detecting insider threats. Senator et al. [24] employed machine learning algorithms such as
Hidden Markov Models (HMM) and Gaussian Mixture Models
(GMM) to detect subtle threat signals within enterprise data
systems. However, these static features often cannot reflect
the dynamic changes of user behavior. Recognizing that user
behavior evolves over time, Chattopadhyay et al. [12] proposed a
technique to detect insider threat scenarios by constructing time
series with the statistics features of each single day feature. Due
to the variable duration of threat activities, Le et al. [4] devised a
user-centric insider threat detection system with multiple levels
of data granularity, employing several classic machine learning
algorithms. Meng et al. [25] introduced a trust management
approach in healthcare environments based on Bayesian inference to identify malicious devices. Le et al. [1] investigated
the effectiveness of various anomaly detection algorithms in the
context of insider threat scenarios. In general, traditional shallow
machine learning algorithms achieve commendable accuracy in
insider threats detection. Nevertheless, these methods often rely
on manual feature engineering, which significantly restricts their
flexibility.
By contrast, deep learning, renowned for its ability to learn
multi-level hidden representations from intricate data, can serve
as a powerful tool to identify potential malicious insider activity.
In [26], Tuor et al. proposed an adaptive detection algorithm
based on Recurrent Neural Network (RNN) language models.
They trained an online unsupervised neural network language
model by treating system logs as interleaved “sentences”. In order to further predict the specific steps the adversary would take
when performing the attack, Shen et al. from Symantec Labs proposed Tiresias [11], an Long Short Term Memory (LSTM) based
system designed for predicting future attack events. Randive
et al. [27] introduced an innovative image-based insider threat
detection framework that utilizes wavelet transform and capsule
networks to discern the spatial arrangement and relationships
among internal user behavior features. Deep learning methods
possess the capability to capture temporal information from user
activity sequences, but they would encounter high false alarm
rates when users modify their daily behavioral routines.
Considering that users within an organization conduct their
daily activities through email, shared files or public devices,
utilizing a graph structure to illustrate the relationships and
dependencies between user behaviors is a reasonable approach.
In [28], Eberle et al. utilized the Minimum Description Length
(MDL) to learn normative patterns from the entire graph that
capture the correspondence of insiders. Similarly, Bian et al. [15]
constructed authentication graphs based on login authentication
events between hosts. Traditional machine learning techniques
are then applied to detect hosts in the network that may be targeted by insiders. Inspired by graph embedding techniques, Liu
et al. [14] utilized heuristic rules to build a heterogeneous graph

where log entries represented nodes. Afterwards, they employed
Deepwalk [29] to generate node embedding vectors, which were
subsequently input into clustering algorithms for anomaly detection. To identify and track lateral movement of insiders within
the intranet, Fang et al. [19] proposed LMTracker, an attack
path detection algorithm based on meta-path and heterogeneous
graph learning. It should be noted that when the data cannot
be readily represented as a graph structure, the construction of
the graph becomes a laborious task, often requiring extensive
manual engineering efforts [14].
In recent years, Graph Neural Networks (GNNs) have gained
popularity in graph analysis and have been successfully applied to anomaly detection in organizational information networks [30]. Li et al. [5] designed a hierarchical detection
method. They introduced a meta-path aggregation GNN and
an edge-augmented GNN for embedding provenance graphs
and host interaction graphs respectively. Xiao et al. [16] proposed a multi-edge weight relationship graph neural network
(MEWRGNN) for robust anomaly detection, which converted
time series related to user behavior logs into graphs. Li et al. [17]
proposed a modular approach called Dual-domain Graph Convolutional Network (DD-GCN), which transformed user features
and structural data into heterogeneous graphs to achieve accurate
and adaptive insider threat detection.
Currently, few studies take into account the dynamic migration of user activities across the network topology to identify
the criminals’ activity path and behavioral profiles in multi-host
intranet environment. Actually, there are significant differences
in the temporal and spatial distribution of attack activities in
the insider threat scenarios, which lead to potential false alarms
and intelligence omissions. In light of this, we conceive a novel
insider threat detection algorithm based on multi-timescale STGNN. We compare the key characteristics of the related studies
and our current work on detecting insider threats in Table I.
III. THREAT MODEL AND MOTIVATION
A. Threat Model
Insider threats commonly arise from internal employees or
hackers who infiltrate internal networks through APTs. These
cybercrime initiators usually possess authorized access to systems and deliberately exploit it to jeopardize the confidentiality,
integrity, or availability of those systems [7]. In practice, insider
threats typically involve multi-step attacks, wherein attackers
orchestrate a series of individual steps based on specific logical
relationships.
Particularly, we consider an insider threat conducted by an
institution employee who is familiar with business logic and does
not initially have administrative privileges assigned to a local
computer. This employee may hold a technical position such as
a systems analyst or IT support personnel, which grants him/her
access to partial sensitive information. Such attackers may have
different expertise but generally possess knowledge of computer
network protocols and architecture, as well as experience with
scripting/programming languages such as Python, PowerShell,
and Bash. Additionally, they are likely to be well-versed in the
company’s security policies. These attackers may be dissatisfied
with their current situation in the company (e.g. frustrated by

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

XIAO et al.: SENTINEL: INSIDER THREAT DETECTION BASED ON MULTI-TIMESCALE USER BEHAVIOR INTERACTION GRAPH LEARNING

777

TABLE I
INSIDER THREAT DETECTION METHODS WITH CORRELATION ANALYSIS

Fig. 1. Examples of three abnormal activities of insider threat with different
spatial characteristics: (a) In-star. (b) Out-star. (c) K-path.

lack of promotions or financial incentives) and deliberately
abuse their access for malicious revenge, economic gain, or
both. Consequently, they tend to target valuable and confidential
information, like clients’ details and tax records stored on the
database server.
With the aim of surreptitiously exfiltrating confidential information, the attackers usually execute the following steps:
1) escalate their user privileges through illegal levers such as
credentials theft; 2) move between machines via login or remote
command execution events with stolen credentials for authentication; 3) launch covert and persistent attacks towards target
accounts and hosts to acquire confidential data; 4) exploit already
installed applications such as Powershell, and run malicious
scripts to establish remote connections for transferring stolen
data. Traditional enterprise security solutions, such as firewalls,
intrusion detection systems (IDS), and intrusion prevention systems (IPS), are primarily implemented at network perimeter, and
thus cannot adequately detect and prevent insider threats.
B. Motivation
In real-world system, attackers’ historical operation data exhibit distinct spatio-temporal patterns and behavioral profiles
that deviate from normal service logic, and such characteristics
are widely distributed in data with multiple timescales.
Spatio-temporal Patterns. Typical insider threats may involve
multiple stages such as reconnaissance, lateral movement, and
foothold establishment, which will give rise to serial event sequences in the log system. These sequential information not only
possess temporal dependencies but also often have the characteristics of spatial patterns. Fig. 1 illustrates the communication
characteristics that an attacker may exhibit during each stage: a)

In-Star. Multiple accounts attempt to log into a critical server.
b) Out-Star. Attackers systematically scan a range of internal
network nodes in search of vulnerable hosts with open services
and exploitable vulnerabilities. c) K-Path. Attackers initiate their
attack from a foothold on a host, and systematically migrate
and infiltrate the internal network, seeking out target hosts to
store critical data. All of these activity patterns show distinct
spatial topological patterns, which can be easily obscured by the
abundance of parallel irrelevant data in serialized data. However,
attackers’ lateral movement through compromised accounts has
a common feature that the access path of attackers does not
include systems/hosts frequently accessed by compromised accounts [32]. This unusual access/behavior trajectory can be a
precursor to stolen credentials or dangerous operations. Besides,
crucial hosts with masses of critical data, e.g. database servers,
are often selected as targets of cybercrime. The interaction between users and nodes in such networks contains more effective
information. By analyzing the spatio-temporal patterns of users,
the detection system can learn the operation regularities of users
at specific times and respective positions. This is beneficial to
detecting any activities that deviate from the established normal
patterns.
Behavioral Profiles: Behavioral profiles, which include relevant information such as logon type, authentication type, logon timestamp, etc., can describe and analyze the behavioral
characteristics of an individual. By constructing users’ behavior
profiles, we can gain an insight into their normal operation
routines and attributes on each host. In some cases, they can even
reveal some potential threat behaviors. The attribute changes of
user operations in the same hosts may indicate the presence of
potential security risks. For example, the attacker can exploit
stolen accounts to remotely access a database server, and then
implant a backdoor for the purpose of monitoring the flow of
information and stealing credentials. If the Service Principal
Name (SPN) of this server is registered in the Active Directory,
the victim would have accessed the server through the Kerberos
protocol to retrieve information. However, other services (e.g.
backdoor software) are not registered in Active Directory. At
this point, the attacker has to replace Kerberos with another
protocol, NTLM. In this case, changes in the behavioral profile
should be of concern. Behavior profiles offers a comprehensive
perspective for detecting and identifying potential security risks
and threat behaviors.

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

778

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 12, NO. 2, MARCH/APRIL 2025

Fig. 2. The framework of SENTINEL, which mainly consists of three stages: 1) BIG construction. 2) ST-GNN based behavioral dependency learning. 3) Insider
threat detection.

Multiple Timescales: Due to the high uncertainty of insider
threat, it is necessary to fuse multiple timescales in the detection
scheme to describe the behavioral patterns of users. On one
hand, insider threats occur at different frequencies, some events
may occur with low frequency but high risk, while others may
occur with high frequency but low risk. By building a multitimescale model, it becomes possible to analyze and compare
low-frequency and high-frequency events to normal behavior
patterns simultaneously. On the other hand, users’ behavior
baselines may change over time. Persistent changes over time
may indicate a potential insider threat, but infrequent behavioral
patterns in the short term could still be normal or accidental.
Fusing the multi-timescale context information can contribute
to handling alerts of suspicious behavior and clarifying the
boundary between malicious behavior and normal operation.
IV. INSIDER THREAT DETECTION BASED ON EDGE FEATURE
ENHANCED SPATIO-TEMPORAL GRAPH NEURAL NETWORK
A. Overview
We propose a novel framework for detecting insider threats,
named “SENTINEL”, as shown in Fig. 2. SENTINEL infers
potential insider threats that may endanger the system security
from large amounts of heterogeneous users’ behavior logs collected by geographically dispersed servers and terminals in the
internal network.
SENTINEL consists of three main parts:
1) User Behavior Interaction Graph Construction: The existing computer system is essentially a distributed system comprised of multiple hosts, network components, and storage
devices. Sensitive information may be stored in the storage
devices or across multiple nodes within this system. This graph
provides us a holistic view of structural interactive topology and
a detailed users’ behavioral profile. Under this situation, users’
requests may be transmitted and processed among different
hosts to fetch their desired resources. The interactive behaviors
across internal systems are naturally formed as a graph, named
Behavior Interaction Graph (BIG), where the internal network
hosts and the users’ operational behaviors across hosts denote
nodes and edges, respectively.
2) Spatio-Temporal Graph Neural Network Model: We employ ST-GNN, which integrates GNN and temporal model,

Fig. 3. An example of user behavior interaction graph where nodes represent
diverse network hosts (such as DNS server, database, users’ terminal, etc.) and
edges represent different interaction events (such as authentication, network
transfers and DNS lookup, etc.) with multidimensional information.

to learn the spatio-temporal dependencies of user behavior.
Considering the uncertainty of insider threats, SENTINEL simultaneously extracts state information at multiple timescales
and proposes an aggregation layer to model the underlying
dependencies of multiple temporal dynamics. This modeling
scheme is beneficial to perceiving propagation paths of insider
threats, and promptly identifying potential sources of threats.
3) Insider Threat Detection: We assess the threat degree of
behavioral events by utilizing the learned node feature representations. To adapt to the extremely sparse abnormal data in
network security logs, we uses negative sampling to train the
entire network and implement a semi-supervised training model.
B. User Behavior Interaction Graph Construction
We adopt user behavior interaction graphs to model users’
interaction in the intranet. Fig. 3 presents an example of BIG
where users log into their work accounts, and produce various
types of operational events which are represented by different
types of edges. Since individuals within an organization have
diverse tasks and positions, the edges exhibit multiple attributes
in the graph. For example, administrators usually access different hosts for network configuration, database maintenance and
risk assessment, whereas the common users frequently perform
file transmissions and Internet access, which may generate vast
quantities of network stream records and DNS traffic logs. To
depict these inter-host behaviors, BIG needs to consider the

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

XIAO et al.: SENTINEL: INSIDER THREAT DETECTION BASED ON MULTI-TIMESCALE USER BEHAVIOR INTERACTION GRAPH LEARNING

effects of multiple types of events simultaneously. Formally,
a BIG is denoted by G = (V, E), where V is the set of vertices, each v ∈ V representing a host node or user entity in
the local network topology; E is the set of edges, each e ∈ E
representing an event that occurs between different hosts. Let
H = [h1 , h2 , . . ., hN ] ∈ RN ×d denote the node embedding in
the graph where N represents the number of graph nodes and d is
the dimension of node embedding. The connection relationship
between nodes in the graph can be represented by an adjacent
matrix A, where ∀e = (i, j) ∈ E, A[i][j] = 1.
To capture temporal dependencies in user behaviors, SENTINEL dissects the long-term log stream into a sequence of
short-term snapshots, each of which encapsulates all interactive
events taking place within a discrete time interval (e.g., hours).
Let T denote the total number of time snapshots. A BIG stream
is denoted by {Gt }Tt=1 , where each Gt = {Vt , Et } represents
the BIG snapshot at time t. For convenience, let V = ∪Tt=1 Vt
and E = ∪Tt=1 Et denote the set of nodes and edges across all
time intervals, respectively. Given the union of BIG stream
{Gt }Tt=1 = (V, E), the goal of SENTINEL is to detect malicious events (i.e. edges in the graph E) caused by insider threats.
C. Edge Feature Enhanced Graph Embedding
BIG describes a series of communication and interaction
actions of users within intranet. These actions are characterized
as multi-attribute edges in the BIG, which can help us understand
the behavioral habits of users in their daily work and identify
abnormal operation sequences. Hence, the edge of BIG plays a
more important role than node in insider threat detection, that
is, BIG is edge-sensitive. However, the existing graph learning
methods are typically node-centric, which fail to effectively
leverage edge features. Based on such node-centric graph, previous graph-based insider threat detection methods [14], [16], [33]
treat operation logs as nodes and attempt to convert log records
into a graph according to correlation relationships among them.
However, since the number of user logs may be several orders of
magnitude higher than the number of network endpoints, the size
of the graph is very huge, which makes these methods encounter
significant computational complexity issues. Hence, in this section, we propose a graph embedding method to aggregate node
features with edge attributes for enhancing the model’s ability
to capture complex relationships between nodes.
The raw operation logs consist of both numerical and textual
fields. For the numerical fields, such as network flow bytes and
port numbers, are already represented as numerical values and
do not require any conversion. In order to handle the unstructured
text in the raw operation logs, we have to transform them into
a numerical vector so that the learning-based detection model
can handle the logs. The operation logs typically contain two
kinds of textual fields: 1) discrete text often represents the
distinct operation objects and types, such as logon authentication
protocol and logon type, which is predefined and thus has a
finite value range. We can employ simple ordinal encoding to
convert the discrete text into a numerical vector. 2) continuous
text typically represents the description of accessed resources,
such as file paths and file contents, which is comprised of

779

symbols, words, or sentences. Following the approach in [16],
we utilize the Word2Vec [34] to convert the continuous text into
a numerical vector. In fact, different operations may possess
distinct log formats (i.e. containing different fields), which may
lead to a potential escalation in the logical intricacies of data
processing. To address this problem, we create a uniform log
format containing all the fields appeared in the logs. If a certain
log record does not contain a specific field, we can pad such
field with 0. Suppose the operation logs contain K distinct fields
and each field generates a corresponding numerical vector f k .
Then, we can get a feature vector for each log by cascading all
numerical vectors, i.e. Fij = fij1 ||fij2 ||. . .||fijK . If a user has an
interactive event between nodes i and j, there exists an edge
between them, which is represented by (i, j, Fij ). Since users
may interact with other hosts after logging into a source host,
we use an attention mechanism to aggregate these operational
features. Actually, different log field exhibits different importance for threat detection. For example, the usage of removable
devices are likely indicative of data breach. Hence, given an edge
e = (i, j, Fij ) in G = (V, E), we regard the K fields of Fij as
K-channel signals, and utilize a separate attention network for
each channel to update the original node features H. For the k-th
k
is calculated as follows:
field, the attention coefficient αij
k
βij
= a(Whk hi ||Whk hj ||Wek fijk ),
k
αij
=

k
))
exp(LeakyReLU(βij
k
s∈Ni exp( LeakyReLU(βis ))

(1)
,

(2)

where Whk and Wek are the weight matrices for the k-th channel,
hi and hj are the node feature vectors of node i and node j
respectively, Ni is the neighboring of node i, and a(.) is a linear
mapping function.
By concatenating the outputs of each channel, we can update
the node embedding vector as follows:
hi = (K
k=1 σ(



k
αij
(Whk hj ||Wek fijk )))Wo ,

(3)

j∈Ni

where Wo is a projection weight vector and σ(.) is the Sigmoid
function. In this way, the whole graph is embedded as follows:
H = EGAT (H, E),

(4)

where H is the updated embedding vector of all nodes in V.
The above aggregation process is illustrated in Fig. 4.
Aggregating the edge features can enhance the ability of
BIG to represent the behavioral routines of insiders. Since the
embedding of a node fuses the features of all the edges originating from such node, the node embedding characterizes all
interactive operations launched by this node (i.e. host or user)
towards other system entities. Therefore, we can employ the
widely-used node-centric graph learning method to handle the
edge-sensitive BIG. As the size of BIG depends on the number
of hosts in the intranet which is far less than the number of
logs, the computational burden of graph learning can be greatly
alleviated.

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

780

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 12, NO. 2, MARCH/APRIL 2025

In order to combine the spatial and temporal dependencies, we
employ a GRU to fuse Spat(L) with Tempt , where Spat(L)
and Tempt serve as the current input and the hidden state of
GRU, respectively. The GRU is composed of an update gate Zt
and a reset gate Rt , which are calculated by:

Fig. 4. Illustration of edge graph attention layer. Each edge is composed of K
channels, denoted by different colors. Fij is the feature vector of the directed
edge eij and αij is the attention factor calculated through (2). hi indicates the
initial node embedding of node i and hi is the updated node embedding which
aggregates edge information through (3).

D. Spatio-Temporal Behavioral Dependencies Learning
The insider threat activities typical exhibit obvious spatiotemporal pattern as illustrated in Section III-B. In light of this,
we attempt to learn the operation regularities of users at specific
times and positions from the above edge-enhanced BIG. As
ST-GNNs can effectively capture both the spatial and temporal
characteristics of graphs, we adopt a GCN+GRU model [35] to
learn the spatio-temporal behavioral dependencies from BIG.
At time t, the snapshot of user behavioral logs is modeled as
a BIG Gt = {Vt , Et } with an adjacent matrix At and a node
embedding matrix Ht ∈ RN ×d . Here, an L-layer GCN [36] is
exploited to capture the spatial correlations between nodes in
BIG. The spatial embedding at l-th layer is described as
1

1

Spat(l) = ReLU (D̃− 2 Ãt D̃− 2 Spat(l−1) W(l−1) ),

(5)

where Spat(0) = H , Ãt = At + IN isthe regularized adjat
cent matrix with self loops, and D̃ii = N
j=i Ãij denotes the
degree of node i. The propagation process of GCN describes how
intensively hosts or users in the internal network interact with
other system entities. Spat(L) represents the structural patterns
of users’ behaviors.
The enormous logs generated by users’ daily activities within
the internal network may form a large number of graph snapshots. Analyzing the association among all the snapshots may
lead to dependency explosion [37]. Therefore, we use a sliding
time window with a size of ω to capture the temporal dependencies among graph snapshots over a short period of time.
At time t, a historical sequence of embedding of node i over
, . . ., ht−1
recent snapshots is denoted by Cth,i = [ht−ω
i
i ]. We use
a hierarchical contextual attention (HCA) based model [38] to
capture the sequential dependencies of Cth,i as follows:
ath,i = sof tmax(rT tanh(Qh (Cth,i )T )),

(6)

where Qh and r are weight parameters. ath,i measures the impact
of the historical behaviors of node i on its current behavior. The
temporal embedding of all nodes in V is described as:
Tempt = [tempt1 , . . . , tempti , . . . , temptN ],
where tempti = (ath,i Cth,i )T .

(7)

Zt = σ(UZ Spat(L) + WZ Tempt + bZ ),

(8)

Rt = σ(UR Spat(L) + WR Tempt + bR ),

(9)

where σ(x) = 1/(1 + e−x ) is the Sigmoid function, and
WZ , WR , UZ , UR , bZ , bR are weight matrices and biases
matrices of GRU. Reset gate Rt determines the relevant past
information to incorporate when generating a new state H̃t :
H̃t = tanh(Uh Spat(L) + Wh (Rt  Tempt )),

(10)

where  is the element-wise multiplication operator, and
Wh , Uh are weight matrices. Afterwards, the update gate Zt
removes the forgotten information from the previous states, and
retains the information that need to be remembered. Finally, we
can get a graph embedding Ht fusing both spatial and temporal
dependencies as follows:
Ht = (1 − Zt )  Tempt + Zt  H̃t .

(11)

The final graph embedding H not only captures the temporal
dependencies of user behavior, but also aggregates the structural
features of users’ interactive trails.
t

E. Multiple Timescales Fusion
Insider threat activity may emerge abruptly in a brief time (e.g
a half day) or persist gradually within the system over a long
duration (e.g several months). Hence, monitoring the alterations
of user behavior solely in a single timescale is insufficient
to perceive these uncertain insider threats. A short-timescale
monitoring is beneficial for the detection of abrupt abnormal
behaviors, although it may introduce more noise and false
positives. Whereas, a long-timescale monitoring contributes to
capturing the persistent abnormal behavior patterns, which may
overlook subtle but crucial events. The insider threat detection
system should monitor user behaviors at different timescales.
To achieve this goal, current researches [1], [4], [12] train a
separate detection model for each timescale, which incurs extra
storage and computation burden, and more importantly, may
increase false alarms. The regular actions that are conducted
infrequently in a short term are easily misidentified as attacks,
for example the data backup by administrators could be regarded
as data breaches. Therefore, we attempt to fuse multi-timescale
BIG embedding in this section.
When fusing the embedding of different timescale, the embedding of different node at different timescales has a distinct
weight. Taking the CERT dataset [39] as an example, the interactive behaviors between some hosts have obvious peak hours in
the morning and evening. In this situation, the daily-period and
weekly-period detection are more critical than monthly-period.
However, there are no distinct behavioral patterns for some other
hosts, thus the daily-period and weekly-period detection may be
unhelpful. Here, we use a gate mechanism to learn the weights
of node embedding at different timescales.

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

XIAO et al.: SENTINEL: INSIDER THREAT DETECTION BASED ON MULTI-TIMESCALE USER BEHAVIOR INTERACTION GRAPH LEARNING

781

Fig. 5. An example of fetching snapshot into the sliding windows at different timescales. Ts represents the duration of a snapshot which is half day in the
figure. Td , Tw and Tm denote the time interval of daily-period, weekly-period, and monthly-period respectively. Gt represents a graph snapshot fetched at
time t.

We analyze the BIG embedding at three timescales, i.e. dailyperiod, weekly-period, and monthly-period, the time intervals
of which are denoted by Td , Tw , and Tm , respectively. As
mentioned in Section IV-D, we capture the temporal dependencies among graph snapshot in the sliding window ω. Here,
as illustrated in Fig. 5, we fetch the snapshots in the same
time of past few days, weeks or months and put them into the
daily-period, weekly-period, and monthly-period sliding windows, respectively. The snapshots in the three-timescale sliding
windows are defined as:

the graph. Specifically, we define a Bernoulli distribution for
negative sampling. Given a normal edge e = (i, j, Fij ), we
i
or the
replace the source host i with the probability of did+d
j

Gtp = [Gt−(ω−1)∗Tp , . . . , Gt−Tp , Gt ]

S(e) = σ(ws (hi ||hj ||Fij ) + bs ),

(12)

where p ∈ [day, week, month] represent the timescale.
Through aforementioned spatio-temporal dependency learning, we can acquire the node embedding Htd , Htw , Htm at different timescales. The multi-timescale node embedding is fused as
follows:
Ht = Wd  Htd + Ww  Htw + Wm  Htm .

(13)

where  is the element-wise multiplication operator, and
Wd , Ww , Wm are linear parameters for different timescales.
Ht is the weighted sum of multi-timescale node embedding.
F. Negative Sampling and Anomaly Detection
Due to the diversity and stealthiness of insider threats, it is
almost impossible to acquire adequate labeled data for comprehensively describing their attack tactics. Additionally, there is
serious data imbalance where the quantity of normal behavior
samples far exceeds abnormal behavior samples. Therefore, conventional supervised methods are not suitable for the scenario
of insider threat detection. To address this issue, we train the
detection model using negative sampling, which eliminates the
requirement for balanced and well-annotated samples. Afterwards, we propose anomaly scores to quantify the degree that a
behavior deviates from the baseline of normal behavior, so that
the anomalous edges can be detected in a semi-supervised way.
To surmount the insufficiency of anomaly data, we adopt the
negative sampling [40] to generate an anomalous edge for each
normal edge. Intuitively, abnormal edges are generated when
insiders establish interactions with the hosts that are rarely
accessed. For a graph snapshot Gt = (Vt , Et ), we generate
|Et | new edges as the candidates of negative edges by randomly
replacing the endpoints of normal edges with other nodes in

d

j
, where di and dj
destination host with the probability of di +d
j
represent the degrees of node i and node j, respectively.
Even though we have corrupted normal samples with negative
sampling, there still exists the possibility that the generated
edges turn out to be normal. Hence, we use a critic network
to evaluate the anomaly score as follows:

(14)

where hi and hj denote the embedding of node i and node
j respectively, σ(.) is the Sigmoid function, and ws and bs
are network parameters. Moreover, strict loss functions such as
cross-entropy is not feasible to distinguish original edges from
generated edges. Instead, we employ an edge-based pairwise
loss function in the training of SENTINEL:

Lt = min
max{0, γ + S(e) − S(eneg )},
(15)
e∈Et

where S(.) is the anomaly score function, eneg is the generated negative edge, γ ∈ (0, 1) is the margin (hyperparameter)
between the possibilities of normal edge and anomalous edge,
and S(e) and S(eneg ) are the anomaly scores of original samples
and negative samples, respectively.
The minimization of the loss Lt encourages that the anomaly
score of normal samples become smaller while the anomaly
score of generated negative samples become larger, which fits
with our aim perfectly. In addition, we introduce L2 regularization loss to avoid model overfitting. The final loss function is
summarized as follows:
L = Lt + λLreg ,

(16)

where λ is a hyperparameter and Lreg is an L2-regularization
loss.
We provide the training process of SENTINEL in Algorithm 1. SENTINEL trains in an iterative and end-to-end manner. In each iteration, each edge is first undergoing negative
sampling to generate a negative edge (line 5). Then, for all
positive and negative edges, we conduct edge feature enhancing,
spatio-temporal dependency learning, multi-timescale feature
fusing, and anomaly score computing successively (lines 6-11).

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

782

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 12, NO. 2, MARCH/APRIL 2025

Algorithm 1: The Training Process of SENTINEL.
Input: User behavior logs x collected from the internal
network, Number of training epochs I.
Output: Anomaly score S(.) of logs x.
1: Parse log x into graph edges {Et }Tt=1 , and generate
graph snapshots sequences {Gt }Tt=1 .
2: for i = 1 to I do
3:
for t = 1 to T do
4:
for e in Et do
5:
eneg ← negative sampling;
6:
H ←

k
k
k k
hi = (K
k=1 σ(
j∈Ni αij (Wh hj ||We fij )))Wo
for each node i;
7:
Spat(L) ← Spat(l) = GCN (Spat(l−1) ) for l
in range (L) where Spat(0) = H ;
8:
for p in timescales {day, week, month} do
9:
Tempt ← tempti = (ath,i Cth,i )T for each
node i;
10:
Htp = GRU (Spat(L) , Tempt );
11:
end for
12:
Ht ← Wd  Htd + Ww  Htw + Wm  Htm
13:
S(e), S(eneg ) ← S(.) =
σ(ws (hi ||hj ||Fij ) + bs )
14:
end for 
15:
Lt ← min e∈Et max{0, γ + S(e) − S(eneg )}
16:
Back propagation and update the parameters;
17:
end for
18: end for
Finally, the parameters are updated through back propagation
under the supervision of loss function defined in (15).
During the detection phase, we can acquire an anomaly score
for each edge in BIG, which measures the degree that a behavior
deviates from the baseline of normal behavior. Hence, we set a
threshold as the anomalous boundary to detect which behavior
is abnormal.

employees, such as lateral movement and unauthorized access.
In this paper, we employ the authentication events, DNS lookup
events and network flow events of the LANL dataset. We select
all 104 malicious insiders that have ever appeared in red team
activity, and randomly select 400 normal users. Our final dataset
consists of 4,735,761 authentication events, 619,552 network
flows events, and 574,651 DNS lookup events involving 7,825
hosts for 504 users, of which 698 events are malicious attack
events.
CERT Dataset: The CERT (Computer Emergency Response
Team) dataset [39] is a well-known dataset in the field of insider threat detection, which collects synthetic attacks’ activities
records and provide both background and malicious actor synthetic data. It is comprised of many types of data, including users’
logon, http communication, file operations, emails, and device
usage. However, in real-world scenarios, obtaining user email
and http communication data can often be challenging due to
privacy and security concerns. Therefore, in our experiments, we
utilize three files from the latest version of the CERT6.2 dataset,
which separately record logon operations, usage of removable
storage devices, and file operations. CERT dataset also contains
records of real insider threat incidents, providing detailed information on how internal attackers use organizational resources
to launch attacks. The final dataset consists of 40,051 operation
events from 5 abnormal users and 25 randomly selected normal
users, involving 4,400 host nodes. Among these events, there
are 161 abnormal events.
TWOS Dataset: The TWOS (The Wolf of SUTD) dataset [42]
is collected during a competition held by the Singapore University of Technology and Design in March 2017. It includes six
data sources as well as psychological personality questionnaire
data. The competition simulates user interactions within and
between competing companies over a period of 5 days, including
12 masquerader incidents and 1 traitor incident. In this study,
we use logon events, mouse records and keystroke records. The
final dataset consists of 1,433,094 operational events involving
32 users and host nodes. Among these events, there are 1,892
malicious events.

V. EXPERIMENT
In this section, we present the evaluation of our proposed
SENTINEL. Specifically, we first introduce the datasets. Then,
the experimental setup are elaborated, including the comparative
baselines and the metrics for evaluation. Finally, the effectiveness and accuracy of SENTINEL are evaluated, and the comparison experiments with the baseline methods are also presented.
A. Dataset
We evaluate the performance of our proposed SENTINEL on
three publicly available datasets including LANL dataset, CERT
and TWOS dataset, which are widely employed in the field of
insider threats detection [1], [4], [5], [12], [14], [15], [16], [31].
The detailed description are demonstrated as follows.
LANL Dataset: LANL dataset is generated by Los Alamos
National Laboratory (LANL) [41], which documents a sequence
of user operational events within the laboratory’s internal computer network, including irregular actions by certain malicious

B. Experimental Settings
1) Baselines: We compare SENTINEL to several state-ofthe-art baselines for insider threat detection, such as machine
learning-based methods and deep learning-based methods. The
machine learning methods applied to compare in this section include two excellent machine learning-based methods of
anomaly detection, i.e. Lightweight on-line Detector of Anomalies (LODA) [43] and Local Outlier Factor (LOF) [44], which
have shown good performance in insider threats field [1]. The
deep learning-based schemes in this section include an LSTMbased sequential language model [26], a graph dynamic detection algorithm named Addgraph [35], an EGAT-based hierarchical APT detection model [5] and two heterogeneous graph
learning-based methods, i.e. Log2vec [14] and LMTracker [19].
2) Metrics: In this paper, Accuracy, ROC (Receiver Operating Characteristic) Curve and AUC (Area Under the Curve)

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

XIAO et al.: SENTINEL: INSIDER THREAT DETECTION BASED ON MULTI-TIMESCALE USER BEHAVIOR INTERACTION GRAPH LEARNING

Fig. 6. Performance of SENTINEL under (a) different snapshot duration. (b)
different timescales.

metrics are used to measure the performance of insider threat detection. The ROC curve is a plot of the True Positive Rate (TPR)
against the False Positive Rate (FPR). The AUC summarizes the
ROC curve by measuring the area under the ROC curves. In the
insider threat scenarios, relying solely on the accuracy metric
can not exactly reflect of the model’s detection performance
because the majority of samples that need to be detected are
normal samples. Considering TPR and FPR jointly, ROC curve
and AUC metric can effectively evaluate the performance of
model under serious data imbalance.
3) Parameter Setup: We divide the three datasets into snapshots with a fixed time duration. For the LANL dataset, we use
the first 40 hours of benign activity before the first abnormal
event appearing to train the anomaly detector and the rest for
testing. The duration of each snapshot is 1 h. Similarly, for
the CERT dataset, we use the first 200 days of benign activity
for training and the rest for testing. Due to the conspicuous
association between employees’ regularity and the designated
working hours, we set the duration of each snapshot to half a day
(12 hours) to distinguish between working hours and off-duty
hours. In detail, we divide a day into two distinct time slices: 7:00
a.m. to 7:00 p.m. and 7:00 p.m. to 7:00 a.m.+1. For the TWOS
dataset, we select the first day of benign activity for training and
the rest for testing. The duration of each graph snapshot is set as
1 h. We set the time window of each graph snapshot stream as
3. We set the learning rate to 0.001, the number of GCN layers
to 3, and the regularization weight decay λ to 5e-7. Dropout is
set to 0.2, and the hidden state dimension size is set to 512. The
margin γ is set to 0.7. The detection threshold is set as 0.05 for
LANL, 0.02 for CERT and 0.05 for TWOS respectively.
4) Equipment Environment: We use the TensorFlow library
to build SENTINEL, version 2.11.0. We conduct all comparative
experiments on a 64-bit CentOS 7.9 operating system. An Nvidia
A100 GPUs with 40GB of memory each is used as accelerators.
C. Experiment on Multiple Timescales
To evaluate the performance of SENTINEL under different
graph snapshot duration, we conduct experiments on the CERT
dataset, which offers an extensive time span for evaluation. We
consider five time spans in our evaluation varying from half a
day, a day, a week, 10 days to a month (30 days). Fig. 6(a)
illustrates the detection performance under different time spans.
It is evident that the detection effectiveness improves as the

783

Fig. 7. Performance comparison under multiple timescales. (a) ROC curves.
(b) AUC values comparison between single temporal and multiple timescales.

duration of snapshot decreases, i.e. the AUC rises from 0.677 to
0.941. A smaller time span implies a shorter log sequence under
monitoring, which is more sensitive to the abnormal behaviors.
Conversely, a larger time span may potentially overshadow such
behavior within the log stream.
In order to explore the impact of different detection
timescales on the performance, we change the time interval
between snapshots, including day (D), week (W), month (M),
day+week (D+W), day+month (D+M), week+month (W+M),
and day+week+month (D+W+M). Fig. 6(b) depicts SENTINEL’s performance of different timescale combinations. The
figure clearly demonstrates that the one-day interval yields the
best performance among the single-timescale results. As the
increase of time interval, the performance deteriorates significantly due to the difficulty of capturing short-term behavioral patterns. Notably, the model incorporating three different timescales exhibits the highest AUC of 0.960. Leaning
the temporal hierarchy with daily, weekly and monthly behavioral patterns enhances the ability to perceive uncertain insider
threats. This result indicates that fusing the temporal feature
representations of multiple timescales could greatly improve the
overall performance.
Afterwards, our investigation focuses on comparing the performance of SENTINEL, AddGraph and EGAT when fusing
multi-timescale features. The rest of the baselines are not included in this comparison because they do not utilize feature representations specifically related to multiple timescales.
The results presented in Fig. 7 reveal that all the three methods demonstrate a performance improvement compared to the
single-timescale results, i.e. an average increase of 0.061in AUC
value. And SENTINEL still outperforms than baselines. In
summary, decomposing the temporal effects into multiple scalespecific feature representations proves beneficial for accurately
modeling users’ behavioral temporal regularity.

D. Experiment on Single Log Source
To further demonstrate the effectiveness of the SENTINEL,
we compare its performance to baselines on single data source
dataset, which is the validation way that many methods [15],
[26], [31], [45], [46] have used. Due to the limited time span,

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

784

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 12, NO. 2, MARCH/APRIL 2025

Fig. 8.

Performance comparison on single log source for LANL dataset. (a) AUC value. (b) Accuracy. (c) True positive rate. (d) False positive rate.

Fig. 9.

Performance comparison on single log source for CERT dataset. (a) AUC value. (b) Accuracy. (c) True positive rate. d) False positive rate.

Fig. 10.

Performance comparison on single log source for TWOS dataset. (a) AUC value. (b) Accuracy. (c) True positive rate. (d) False positive rate.

we can only evaluate the performance of single-timescale SENTINEL on LANL and TWOS dataset, denoted as SENTINELST. Accordingly, the multi-timescale SENTINEL model is denoted as SENTINEL-MT. In addition, LMTracker, LOF and
LODA methods need to collect features involving multiple logs
and thus cannot participate in the evaluation on a single data
source. For the LANL dataset, we use authentication events,
while for the CERT and TWOS dataset, we use users’ logon
records. In a real-world scenario, security audit experts can
leverage this type of log files to identify attackers exhibiting
signs of lateral movement or internal employees engaging in
covert file exfiltration.
The experimental results are shown in the Figs. 8, 9
and 10. We observe that the SENTINEL outperforms other baseline methods in terms of AUC values for all datasets, i.e. 0.972

for LANL, 0.917 for CERT and 0.921 for TWOS, followed by
the Addgraph. The results suggest that the dynamic graph detection methods is sensitive to malicious activities within internal
networks. However, since Addgraph hardly considers interactive
features, its performance is slightly lower than SENTINEL. The
Log2vec shows a good performance on the LANL dataset with
the AUC value of 0.852, but underperforms on the CERT and
TWOS dataset, as it has high false positive rates with low AUC
values of only 0.520 and 0.451. This result can be attributed to the
fact that the heterogeneous graph constructed by Log2vec graph
rules under the single data source of CERT/TWOS dataset is too
sparse, and the random walk based embedding method cannot
learn the relationship between logs. Additionally, the graph embedding method employed by Log2vec disregards the attributes
of logs, which have an obvious impact on its performance. The

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

XIAO et al.: SENTINEL: INSIDER THREAT DETECTION BASED ON MULTI-TIMESCALE USER BEHAVIOR INTERACTION GRAPH LEARNING

Fig. 11.

Performance comparison on multiple log source for LANL dataset. (a) AUC value. (b) Accuracy. (c) True positive rate. (d) False positive rate.

Fig. 12.

Performance comparison on multiple log source for CERT dataset. (a) AUC value. (b) Accuracy. (c) True positive rate. (d) False positive rate.

Fig. 13.

Performance comparison on multiple log sources for TWOS dataset. (a) AUC value. (b) Accuracy. (c) True positive rate. (d) False positive rate.

EGAT solely relies on edge features and lacks a mechanism
to recognize the dynamic changes in the graph structure. This
limitation is particularly evident in the results obtained from
the CERT dataset, i.e. a low AUC value of 0.473. Although the
LSTM model performs well on LANL authentication events, its
effectiveness is hindered in the CERT and TWOS dataset. The
relatively short length of logon logs results in insufficient context
information and adversely impacts its detection performance.
The above results indicate that the SENTINEL method can effectively detect insider threats involving logon or authentication
events in an internal network.
E. Experiments on Multiple Log Sources
To evaluate the performance of SENTINEL in detecting
threats from multi-source data, we conduct experiments on
multiple types of log files in LANL, CERT and TWOS datasets.
For the LANL dataset, we use authentication events, DNS

785

events, and network flow events. For the CERT dataset, we
use logon records, usage of removable storage devices, and file
operation records. For TWOS dataset, we use logon records,
mouse records and keystroke records.
Figs. 11, 12 and 13 illustrates the comparison results of
SENTINEL and baselines on multiple sources experiments.
Table II presents the AUC values comparison between singlesource experiments and multi-source experiments. It is observed
that SENTINEL consistently achieves the best performance on
multi-source experiments, i.e. the largest AUC values of 0.980
on the LANL dataset, 0.960 on the CERT dataset and 0.956
on the TWOS dataset. Compared to the previous single-source
results, SENTINEL’s multi-source results exhibit an increase in
AUC on the three datasets by 0.008, 0.04 and 0.035, respectively. Log2vec shows a notable performance improvement, especially on the CERT dataset where the AUC increases by 0.245.
Log2vec utilizes different graph constructing rules to integrate
different types of logs into a heterogeneous graph, expanding

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

786

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 12, NO. 2, MARCH/APRIL 2025

TABLE II
AUC COMPARISON BETWEEN SINGLE LOG SOURCE AND MULTIPLE LOG SOURCES

its coverage to monitor more network behaviors and thus can
more accurately identify outlier abnormal events. In practice,
attackers usually participate in a wide range of threat activities,
including but not limited to lateral movement and data theft.
Therefore, incorporating a larger number of logs from different
sources can improve the accuracy of identifying outliers. Similar
method LMTracker, which builds heterogeneous graphs based
on meta-paths, also achieves better results because its meta-path
rules are more directional. Machine learning-based anomaly
detection methods LOF and LODA cannot capture the complex
features and interrelations of structural information, thus their
performance is often inferior to graph-based methods. However,
using multiple log source is also a double-edged sword. For some
unstable models like EGAT and LSTM, the use of multiple types
of log records may introduce substantial data noise, which may
lead to the degradation of performance on the contrary.
F. Comparison of Different Threat Scenarios
In order to explore whether SENTINEL’s performance is
consistent in different insider threat scenarios, we conduct an
analysis of its performance variances within multiple threat
scenarios present in the CERT r6.2 dataset. The CERT r6.2
dataset contains four explicit threat scenarios:
r A departing employee, who has never used a removable
drive or worked overtime before, logs in after office hours
and uploads data to a publicly accessible website (S1 ).
r A employee seeking new employment opportunities frequently access job search websites and use a thumb drive
to steal confidential information before leaving (S2 ).
r A system administrator who is disgruntled with his/her
supervisor downloads a keylogger and obtains a list of passwords belonging to various employees within the organization. Subsequently, he/she uses a thumb drive to transfer
the password list to the supervisor’s machine and attempts
to search for the supervisor’s password. Ultimately, he/she
logs into the supervisor’s machine and sends a mass email
designed to create panic, resulting in chaos within the
organization (S3 ).
r An indignant employee logs into other users’ computers,
searches for files of interest, and sends these files to their
personal email address (S4 ).
Table III shows the true positive rates and false negatives rate
(FNR) of SENTINEL for the above four threat scenarios. As
illustrated, SENTINEL performs well on S1 , S2 , and S4 with an

TABLE III
COMPARISON OF DIFFERENT THREAT SCENARIOS

TABLE IV
ABLATION STUDY OF KEY COMPONENTS IN SENTINEL ON THE CERT
DATASET

average TPR of 98%, but exhibits poor performance on S3 where
nearly 42% of malicious behaviors undergo undetected. The
result reveals that SENTINEL works well in those scenarios (e.g,
S1 , S2 , S4 ) where malicious insiders conduct actions diverging
from their routine operations, but may fail in the scenarios (e.g,
S3 ) where malicious contents is hidden in routine operations.
For instance, the insider in S1 has no prior history of using
removable drives or working overtime; in S2 , there is a sudden
spike in the insider’s thumb drive device usage; and in S4 ,
the insider has never logged into another individual’s machine
using his/her own credentials before. In contrast, since the crime
administrator in S3 already possesses high authority, his/her
historical behavior of frequently logging into other machines
may make SENTINEL misclassify the action of logging into
the supervisor’s machine as normal operation. This suggests that
SENTINEL is prone to misjudging malicious actions that closely
resemble routine tasks.
G. Ablation Study
We present ablation study in this subsection to evaluate the
contribution of each key component on the widely used CERT
dataset. The results are presented in Table IV, where EFE represents the edge feature embedding component, SDL and TDL
respectively represent the spatial dependency learning component and the temporal dependency learning component of the
spatial-temporal graph neural network, and MTF represents the
multiple timescale fusion component. We can observe from the

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

XIAO et al.: SENTINEL: INSIDER THREAT DETECTION BASED ON MULTI-TIMESCALE USER BEHAVIOR INTERACTION GRAPH LEARNING

Fig. 15.

787

SENTINEL’s (a) ROC curves. (b) TPR&FPR difference curves.

to the detection of more malicious behaviors. However, this
benefit comes at the cost of generating more false positives.
In general, the experimental results show that a longer training
set duration can cover users’ normal behavior routines more
comprehensively, leading to a more effective trained model.
I. Selection of Detection Threshold

Fig. 14. Performance comparison on varying training sets. (a) AUC value. (b)
Accuracy. (c) True positive rate. (d) False positive rate.

table that the w/o EFE model results in the poorest performance,
with a decrease in AUC value by 0.084 compared to full model.
This result indicates the critical importance of using users’
behavioral feature for detecting insider threats. Comparing to
the w/o TDL model, the w/o SDL model has a more severe
performance degradation due to the absence of spatial topology
learning. This result suggests that malicious insider threat behaviors exhibit more significant changes in network topology
than in temporal pattern. We also find that the w/o MTF model
results in a decrease in AUC value by 0.019, which demonstrates
the effectiveness of integrating multi-time scale information.
H. Influence of Varying Training Sets
In order to demonstrate the influence of varying training
sets on SENTINEL, we conduct comparative experiments by
controlling the proportion of training data. Taking the LANL
dataset as an example, a training proportion of 100% indicates
that the training set consists of all 40 hours of benign activity
prior to the appearance of the first abnormal event whereas
50% means using the first 20 hours as the training set, and
so on. Fig. 14 shows the experimental results of SENTINEL
across various datasets. We can observe that as the proportion
of training data decreases, the overall model performance tends
to decline. Specifically, accuracy decreases by an average of
20.8%, the AUC value decreases by an average of 14.6%, and
the FPR increases by an average of 2.08 times. This is consistent
with our expectations, as a smaller training set causes the model
to learn a more prejudiced behavioral baseline, which is unable
to cover the diverse range of normal behaviors. Interestingly,
we find that SENTINEL’s TPR tends to increase on the LANL
and TWOS datasets. Our analysis suggests that limited training
data might make insider threats more conspicuous, which leads

As mentioned in Section IV-F, SENTINEL finally outputs
anomaly scores for different user behavior events. To select an
appropriate detection threshold, we first plot the ROC curve of
SENTINEL on test data. The closer the ROC curve is to the
top-left corner (indicating high TPR and low FPR), the better
the model’s performance. Therefore, we choose the detection
threshold corresponding to the point nearest to the upper left
corner of the ROC curve, i.e. maximizing (TPR - FPR). Specifically, during the test, setting different detection thresholds th
(i.e. samples with anomaly scores greater than th are classified as
anomalies) will yield multiple sets of TPR and FPR. These (TPR,
FPR) tuples can form a ROC curve. Fig. 15(a) shows the ROC
curves of SENTINEL on three datasets. Then, we analyze the
differences between the TPR and FPR across various detection
thresholds, as illustrated in Fig. 15(b). We select the threshold
with the maximum TPR/FPR difference as the decision boundary. For the CERT dataset, the optimal threshold is th = 0.02,
which results in the largest difference of 0.874. For the LANL
and TWOS datasets, the optimal threshold is th = 0.05, with the
maximum differences reaching 0.892 and 0.824, respectively.
Fig. 16 presents the Kernel Density Estimation (KDE) distributions of the testing samples’ anomaly scores for SENTINEL
across three datasets. We can observe that the aforementioned
selected thresholds effectively differentiate between normal behavior and malicious insider threat behaviors, thereby justifying
the appropriateness of these thresholds.
J. Runtime Overhead Analysis
Finally, we investigate the model efficiency of our SENTINEL. We present SENTINEL’s training time and resource
consumption on three datasets in Table V. As shown in the
table, the training time for the LANL dataset is 488 seconds,
significantly higher than the other two datasets. This is because
the LANL dataset includes 7825 nodes, significantly more than
CERT (4400 nodes) and TWOS (32 nodes), and also contains a
larger number of logs, resulting in an average of 4246.2 edges
per graph snapshot, compared to 145.9 for CERT and 74.6 for

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

788

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 12, NO. 2, MARCH/APRIL 2025

TABLE V
SENTINEL’S TRAINING TIME AND RESOURCE CONSUMPTION

TABLE VI
DETECTION COMPUTATIONAL COMPLEXITY OF DIFFERENT COMPARISON METHODS

Fig. 16. SENTINEL’s KDE distribution of normal and anomaly samples on
(a) LANL dataset. (b) CERT dataset. (c) TWOS dataset.

TWOS. Despite the large data scale, most graphs in the LANL
dataset are sparse, which means that the number of parameters
involved in each update is not excessive. Therefore, the GPU
memory usage for LANL training is only 20.7% higher than
CERT and 27.4% higher than TWOS, with GPU utilization
being approximately twice that of the other datasets. Overall,
SENTINEL’s training time and resource consumption remain
acceptable.
At detection phase, for the two anomaly detection algorithms,
i.e. LOF and LODA, we can achieve fast detection speed without
GPU acceleration, which benefits from the relatively simple
computational architecture of machine learning. However, it
should be noted that these two methods rely on pre-extracted
complex features, which took more than 90 minutes before
testing. In comparison, SENTINEL requires a graph construction process, which takes only less 18 seconds due to the
small size of our graph. Table VI shows the average GPU
utilization, average GPU memory usage, and time consuming

of different comparative methods. We observe that AddGraph
exhibits the least resource occupancy and the fast running speed
compared to other methods. By contrast, the detection time and
computational overhead are slightly increased for SENTINEL.
It is worth noting that the attention-based graph embedding
propagation layer of SENTINEL incurs a higher computational
cost compared to the adjacent matrix-based graph convolution
utilized by AddGraph. Considering the comparison of prediction
accuracy between SENTINEL and Addgraph, the additional
computational cost could bring positive results via learning
the correlation of edge features. Similarly, the attention-based
EGAT presents a notable increase in GPU memory usage and
utilization due to the high-dimensional node embedding. In
Table VI, LSTM and Log2vec exhibit an average GPU utilization
of over 50%, which is significantly higher than that of AddGraph
and SENTINEL (less than 5%). Furthermore, we also find
that the average GPU memory usage of LSTM is the largest,
followed by EGAT and Log2vec. In addition, the detection time
consuming of SENTINEL, Addgraph and EGAT is far less than
the log generation time (mins vs hours), which can meet the
needs of real-time insider threat detection. Overall, SENTINEL
can achieve a good detection accuracy at the cost of a minor
computational burden.

VI. CASE STUDIES
SENTINEL is deployed within an organization’s local area
network, specifically tailored for detecting insider threats in
sensitive government departments and enterprises. By analyzing
network interaction behaviors of internal employees and audit
logs from terminal hosts, SENTINEL could monitor the threat
levels of insiders in real time. If monitored user behavior is
deemed highly threatening, such as exhibiting unusual characteristics or logon patterns divergent from typical activities,
the security operation center will initiate appropriate responses.
Below, we illustrate two typical insider threat scenarios, i.e.
malicious insiders and compromised insiders.
r Malicious Insiders: User 1 typically logs into his/her host
between 8:30 and 9:00 AM, and logs out between 6:30
and 7:00 PM. However, this user frequently logs into other
users’ computers around 12:00 noon and 6:00 PM, searches
for files of interest, and subsequently emails these files to

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

XIAO et al.: SENTINEL: INSIDER THREAT DETECTION BASED ON MULTI-TIMESCALE USER BEHAVIOR INTERACTION GRAPH LEARNING

personal addresses. This unusual logon pattern triggers an
alert from SENTINEL.
r Compromised Insiders: User 2 steals user 3’s credentials through a covertly installed keylogger. Subsequently,
he/she utilizes these credentials to remotely access the
database server and implant a backdoor, aiming to monitor
information flow and steal commercial secrets. Since the
Service Principal Name of this server is registered in Active
Directory, user 3 generally accesses the server through the
Kerberos protocol to retrieve information. However, user
2’s backdoor software operates outside Active Directory
and thus he/she is compelled to use NTLM protocol for
authentication. SENTINEL identifies this shift in user operation attributes, and signals a potential security risk.
VII. CONCLUSION AND FUTURE WORK
In this paper, we propose a novel method SENTINEL, which
utilizes an edge-enhanced spatio-temporal graph neural network
for detecting insider threats. In SENTINEL, user’s behavior interactions within the internal network are formed as a graph. We
subsequently employ an ST-GNN to learn the spatio-temporal
operation regularities of users. SENTINEL adopts a semisupervised strategy that requires only normal behavior log data
for training, which enhances the flexibility of deployment. Evaluation on the LANL/CERT/TWOS datasets demonstrates that
SENTINEL outperforms state-of-the-art approaches in terms of
AUC and ROC curve. To address the problem that SENTINEL
is prone to misjudging malicious actions that closely resemble
routine operation, we will integrate additional behavioral indicators, such as employees’ mental health status or social records
for insider threat detection in the future. Moreover, we will focus
on automating the reconstruction of the attack scenarios for
insider threat based on threat alerts. This will provide a clear
understanding of the attack strategy and intentions.
REFERENCES
[1] D. C. Le and N. Zincir-Heywood, “Anomaly detection for insider threats
using unsupervised ensembles,” IEEE Trans. Netw. Service Manag.,
vol. 18, no. 2, pp. 1152–1164, Jun. 2021.
[2] Proofpoint, “2022 ponemon cost of insider threats global report,”
2022. [Online]. Available: https://www.proofpoint.com/us/resources/
threat-reports/cost-of-insider-threats
[3] N. F. Syed, S. W. Shah, A. Shaghaghi, A. Anwar, Z. Baig, and R. Doss,
“Zero trust architecture (ZTA): A comprehensive survey,” IEEE Access,
vol. 10, pp. 57143–57179, 2022.
[4] D. C. Le, N. Zincir-Heywood, and M. I. Heywood, “Analyzing data
granularity levels for insider threat detection using machine learning,”
IEEE Trans. Netw. Service Manag., vol. 17, no. 1, pp. 30–44, Mar. 2020.
[5] Z. Li, X. Cheng, L. Sun, J. Zhang, and B. Chen, “A hierarchical approach
for advanced persistent threat detection with attention-based graph neural
networks,” Secur. Commun. Netw., vol. 2021, 2021, Art. no. 9961342.
[6] M. Villarreal-Vasquez, G. M. Howard, S. Dube, and B. Bhargava, “Hunting
for insider threats using LSTM-based anomaly detection,” IEEE Trans.
Dependable Secur. Comput., vol. 20, no. 1, pp. 451–462, Jan./Feb. 2023.
[7] L. Liu, O. De Vel, Q.-L. Han, J. Zhang, and Y. Xiang, “Detecting and
preventing cyber insider threats: A survey,” IEEE Commun. Surveys Tut.,
vol. 20, no. 2, pp. 1397–1417, Second Quarter 2018.
[8] A. Sah et al., “A new architecture for managing enterprise log data,” in
Proc. Conf. Syst. Admin., 2002, pp. 121–132.
[9] M. Hanley and J. Montelibano, “Insider threat control: Using centralized
logging to detect data exfiltration near insider termination,” DTIC, Fort
Belvoir, VA, USA, Tech. Rep. 024, 2011.

789

[10] S. M. Milajerdi, R. Gjomemo, B. Eshete, R. Sekar, and V. Venkatakrishnan, “HOLMES: Real-time APT detection through correlation of suspicious information flows,” in Proc. IEEE Symp. Secur. Privacy, 2019,
pp. 1137–1152.
[11] Y. Shen, E. Mariconti, P. A. Vervier, and G. Stringhini, “Tiresias: Predicting
security events through deep learning,” in Proc. ACM Conf. Comput.
Commun. Secur., 2018, pp. 592–605.
[12] P. Chattopadhyay, L. Wang, and Y.-P. Tan, “Scenario-based insider threat
detection from cyber activities,” IEEE Trans. Comput. Soc. Syst., vol. 5,
no. 3, pp. 660–675, Sep. 2018.
[13] S. Lei, C. Xia, Z. Li, X. Li, and T. Wang, “HNN: A novel model to study
the intrusion detection based on multi-feature correlation and temporalspatial analysis,” IEEE Trans. Netw. Sci. Eng, vol. 8, no. 4, pp. 3257–3274,
Oct.–Dec. 2021.
[14] F. Liu, Y. Wen, D. Zhang, X. Jiang, X. Xing, and D. Meng, “Log2vec:
A heterogeneous graph embedding based approach for detecting cyber
threats within enterprise,” in Proc. ACM Conf. Comput. Commun. Secur.,
2019, pp. 1777–1794.
[15] H. Bian, T. Bai, M. A. Salahuddin, N. Limam, A. Abou Daya,
and R. Boutaba, “Uncovering lateral movement using authentication
logs,” IEEE Trans. Netw. Serv. Manag., vol. 18, no. 1, pp. 1049–1063,
Mar. 2021.
[16] J. Xiao, L. Yang, F. Zhong, X. Wang, H. Chen, and D. Li, “Robust anomalybased insider threat detection using graph neural network,” IEEE Trans.
Netw. Service Manag., vol. 20, no. 3, pp. 3717–3733, Sep. 2022.
[17] X. Li et al., “A high accuracy and adaptive anomaly detection model with
dual-domain graph convolutional network for insider threat detection,”
IEEE Trans. Inf. Forensic Secur., vol. 18, pp. 1638–1652, 2023.
[18] F. Liu, Y. Wen, Y. Wu, S. Liang, X. Jiang, and D. Meng, “MLTracer: Malicious logins detection system via graph neural network,” in
Proc. IEEE Int. Conf. Trust, Secur. Privacy Comput. Commun., 2020,
pp. 715–726.
[19] Y. Fang, C. Wang, Z. Fang, and C. Huang, “LMTracker: Lateral movement
path detection based on heterogeneous graph embedding,” Neurocomputing, vol. 474, pp. 37–47, 2022.
[20] Z. Wang, J. Chen, and H. Chen, “EGAT: Edge-featured graph attention
network,” in Proc. 30th Int. Conf. Artif. Neural Netw., Springer, 2021,
pp. 253–264.
[21] X. Zhang et al., “Traffic flow forecasting with spatial-temporal
graph diffusion network,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 15008–15015.
[22] A. Ambre and N. M. Shekokar, “Insider threat detection using log analysis
and event correlation,” Procedia Comput. Sci., vol. 45, pp. 436–445, 2015.
[23] MITRE, “Adversarial tactics, techniques and common knowledge,” (n.d.).
2013. [Online]. Available: https://attack.mitre.org
[24] T. E. Senator et al., “Detecting insider threats in a real corporate database
of computer usage activity,” in Proc. ACM SIGKDD Int. Conf. Knowl.
Discov. Data Min., 2013, pp. 1393–1401.
[25] W. Meng, K.-K. R. Choo, S. Furnell, A. V. Vasilakos, and C. W. Probst, “Towards Bayesian-based trust management for insider attacks in healthcare
software-defined networks,” IEEE Trans. Netw. Service Manag., vol. 15,
no. 2, pp. 761–773, Jun. 2018.
[26] A. R. Tuor, R. Baerwolf, N. Knowles, B. Hutchinson, N. Nichols, and R.
Jasper, “Recurrent neural network language models for open vocabulary
event-level cyber anomaly detection,” in Proc. AAAI Conf. Artif. Intell.,
2018, pp. 285–293.
[27] K. D. Randive and M. Ramasundaram, “MWCapsNet: A novel multilevel wavelet capsule network for insider threat detection using image
representations,” Neurocomputing, vol. 553, 2023, Art. no. 126588.
[28] W. Eberle, J. Graves, and L. Holder, “Insider threat detection using a
graph-based approach,” J. Appl. Secur. Res., vol. 6, no. 1, pp. 32–81, 2010.
[29] B. Perozzi, R. Al-Rfou, and S. Skiena, “Deepwalk: Online learning of
social representations,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov.
Data Min., pp. 701–710, 2014.
[30] Y. Zhang, C. Yang, K. Huang, and Y. Li, “Intrusion detection of industrial
Internet-of-Things based on reconstructed graph neural networks,” IEEE
Trans. Netw. Sci. Eng, vol. 10, no. 5, pp. 2894–2905, Sep./Oct. 2023.
[31] B. Bowman, C. Laprade, Y. Ji, and H. H. Huang, “Detecting lateral
movement in enterprise computer networks with unsupervised graph AI,”
in Proc. Int. Symp. Res. Attacks, Intrusions Defenses, 2020, pp. 257–268.
[32] G. Ho et al., “Hopper: Modeling and detecting lateral movement.,” in Proc.
USENIX Secur. Symp., 2021, pp. 3093–3110.
[33] C. Wang and H. Zhu, “Wrongdoing monitor: A graph-based behavioral
anomaly detection in cyber security,” IEEE Trans. Inf. Forensic Secur.,
vol. 17, pp. 2703–2718, 2022.

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.

790

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 12, NO. 2, MARCH/APRIL 2025

[34] T. Mikolov, I. Sutskever, K. Chen, G. S. Corrado, and J. Dean, “Distributed
representations of words and phrases and their compositionality,” in Proc.
Adv. Neural Inf. Proces. Syst., 2013, pp. 3111–3119.
[35] L. Zheng, Z. Li, J. Li, Z. Li, and J. Gao, “AddGraph: Anomaly detection in
dynamic graph using attention-based temporal GCN,” in Proc. Int. Joint
Conf. Artif. Intell., 2019, pp. 4419–4425.
[36] T. N. Kipf and M. Welling, “Semi-supervised classification with graph
convolutional networks,” in Proc. Int. Conf. Learn. Representations, 2017,
pp. 1–12.
[37] Y. Kwon et al., “MCI: Modeling-based causality inference in audit logging
for attack investigation,” in Proc. Netw. Distrib. Syst. Secur. Symp., vol. 2,
p. 4, 2018.
[38] Q. Cui, S. Wu, Y. Huang, and L. Wang, “A hierarchical contextual
attention-based network for sequential recommendation,” Neurocomputing, vol. 358, pp. 141–149, 2019.
[39] J. Glasser and B. Lindauer, “Bridging the gap: A pragmatic approach to
generating insider threat data,” in Proc. IEEE CS Secur. Privacy Workshops, 2013, pp. 98–104.
[40] Z. Wang, J. Zhang, J. Feng, and Z. Chen, “Knowledge graph embedding
by translating on hyperplanes,” in Proc. AAAI Conf. Artif. Intell., 2014,
pp. 1112–1119.
[41] A. D. Kent, “Comprehensive, Multi-source cyber-security events,” Los
Alamos Nat. Lab., Los Alamos, NM, USA, 2015, doi: 10.17021/1179829.
[42] A. Harilal, F. Toffalini, J. Castellanos, J. Guarnizo, I. Homoliak, and M.
Ochoa, “TWOS: A dataset of malicious insider threat behavior based on
a gamified competition,” in Proc. Int. Workshop Manag. Insider Secur.
Threats, 2017, pp. 45–56.
[43] T. Pevny, “Loda: Lightweight on-line detector of anomalies,” Mach.
Learn., vol. 102, pp. 275–304, 2016.
[44] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” in Proc. ACM SIGMOD Int. Conf. Manag.
Data, 2000, pp. 93–104.
[45] R. Paudel and H. H. Huang, “Pikachu: Temporal walk based dynamic
graph embedding for network anomaly detection,” in Proc. IEEE/IFIP
Netw. Oper. Manag. Symp., 2022, pp. 1–7.
[46] Y. Yuan, S. S. Adhatarao, M. Lin, Y. Yuan, Z. Liu, and X. Fu, “ADA:
Adaptive deep log anomaly detector,” in Proc. IEEE Conf. Comput.
Commun., 2020, pp. 2449–2458.

Siyang Chen (Student Member, IEEE) received the
B.S. degree in 2019 from the University of Science
and Technology of China (USTC), Hefei, China,
where he is currently working toward the Ph.D. degree
with the School of Information Science and Technology, USTC, affiliated with the Laboratory for Future
Network. His research interests include network security traffic analysis, and website fingerprinting.

Fengrui Xiao (Student Member, IEEE) received the
B.E. degree in information science and technology in
2019 from the University of Science and Technology
of China (USTC), Hefei, China, where he is currently
working toward the Ph.D. degree. His research interests include encrypted traffic classification, insider
threats, and multi-step attack.

Jian Yang (Senior Member, IEEE) received the B.S.
and Ph.D. degrees from the University of Science and
Technology of China (USTC), Hefei, China, in 2001
and 2006, respectively. He is currently a Professor in
the School of Information Science and Technology,
USTC. His research interests include future network,
distributed system design, modeling and optimization, multimedia over wired and wireless and stochastic optimization. Dr. Yang was the recipient of the Lu
Jia-Xi Young Talent Award from Chinese Academy
of Sciences in 2009.

Yuanyi Ma (Student Member, IEEE) received the
B.S. degree in 2018 from the University of Science
and Technology of China, Hefei, China, where he is
currently working toward the Ph.D. degree with the
School of Information Science and Technology. His
research interests include future network, network
optimization, and network security.

Huasen He (Member, IEEE) received the B.S. degree in automation from the University of Science
and Technology of China (USTC), Hefei, China,
in 2013, and the M.S. degree in signal processing
and communications and the Ph.D. degree in digital
communications from the University of Edinburgh,
Edinburgh, U.K., in 2014 and 2018, respectively.
He is currently an Associate Research Fellow with
the School of Information Science and Technology,
USTC. His research interests include future networks,
network modeling, and optimization.

Shuangwu Chen (Member, IEEE) received the B.S.
and Ph.D. degrees from the University of Science
and Technology of China (USTC), Hefei, China,
in 2011 and 2016, respectively. He is currently an
Associate Professor with the Department of Automation, USTC. His research interests include multimedia communications, future network, and stochastic
optimization.

Authorized licensed use limited to: NATIONAL INSTITUTE OF TECHNOLOGY CALICUT. Downloaded on April 01,2026 at 02:00:48 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
