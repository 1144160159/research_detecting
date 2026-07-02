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
# [654] Early-Stage Detection of Encrypted Malware Traffic via Multi-Flow Temporal Graph Learning
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
编号：654
题名：Early-Stage Detection of Encrypted Malware Traffic via Multi-Flow Temporal Graph Learning
年份：2026
DOI：10.1109/tifs.2026.3685079
来源：IEEE Transactions on Information Forensics and Security
PDF：paper/10.1109_TIFS.2026.3685079.pdf
已有粗分类：加密流量分类与应用识别
二级关联：恶意流量、暗网与攻击检测、图学习、知识图谱与威胁情报
相关性：强相关，分数 21
已有代码状态：已下载；DawnGuard -> source\DawnGuard

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\654.txt
- 原始字符数：73895
- 本次发送字符数：73895
- 是否截断：False

代码包：
- 仓库：DawnGuard
  - URL：https://github.com/jiajizhe1997/DawnGuard
  - 状态：downloaded
  - 本地目录：source\DawnGuard
  - 顶层结构：README.md
  - 主要语言：
  - README 标题：DawnGuard、Code、Dataset、Supported Environments、Operating System、Programming Language & Version、Software & Libraries、Hardware Requirements、Recommended Configuration、Contact
  - README 运行线索：sh session-based context, grouping logical interactions into local subgraphs.；Python 3.10 is required.；sh session-based context, grouping logical interactions into local subgraphs.；Python 3.10 is required.；sh session-based context, grouping logical interactions into local subgraphs.；Python 3.10 is required.
  - 关键文件：{}
  - 数据集线索：Tor、USTC、tor

论文正文包开始：
<<<PAPER_TEXT
4460

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

Early-Stage Detection of Encrypted Malware Traffic
via Multi-Flow Temporal Graph Learning
Jizhe Jia, Yi Zhao , Member, IEEE, Meng Shen , Member, IEEE, Susu Cui , Jing Wang, Bufan Zhao,
Wei Wang , Member, IEEE, and Liehuang Zhu , Senior Member, IEEE
Abstract—Malware widely adopts network traffic encryption
techniques to conceal malicious activities. Recent research has
demonstrated the effectiveness of machine learning (ML)-, deep
learning (DL)-, and pre-training-based malware traffic detection
methods. However, a vast majority of these methods rely on
the collected complete traffic during the malware attack. While
certain methods can operate on partial traffic, their detection
accuracy often significantly decreases when the available data is
restricted to the extreme early stage, where information is most
sparse. In this paper, we propose DawnGuard, an effective earlystage encrypted malware traffic detection framework through
multi-flow temporal graph learning. Specifically, based on the
temporal packet density distribution analysis, DawnGuard innovatively proposes a self-adjusting data augmentation strategy for
early-stage malware traffic, which can force the model to focus
on the early-stage interaction phase with more distinguishable
properties. Meanwhile, considering that temporal-topological
correlations among multiple flows can provide more distinguishable properties in a malware attack, we further develop a
temporal graph learning framework to extract features, which
can form Multi-Flow Graph Features (MGF). By utilizing MGF,
DawnGuard implements a Vision Transformer-based detection
mechanism, enabling accurate and precise encrypted malware
traffic detection with early-stage traffic by capturing both local
and global contextual relationships. Extensive experiments with
two real-world datasets demonstrate that DawnGuard outperforms the state-of-the-art (SOTA) methods in three typical
scenarios: varying early-stage time windows, imbalanced data,
and unseen malware detection. Particularly, DawnGuard achieves
an average F1 of 95.11%, 8.7% higher than the SOTA method,
by only utilizing the first 20% loading ratio of complete traffic.
Index Terms—Malware traffic detection, encrypted traffic
analysis, graph learning.

Received 19 May 2025; revised 12 January 2026 and 24 March 2026;
accepted 12 April 2026. Date of publication 17 April 2026; date of current
version 4 May 2026. This work was supported in part by NSFC under Project
U25A20428, Project U23A20304, and Project 62472036; in part by Beijing
Advanced Innovation Center for Future Blockchain and Privacy Computing;
and in part by Beijing Nova Program. The associate editor coordinating
the review of this article and approving it for publication was Dr. Daisuke
Mashima. (Corresponding author: Meng Shen.)
Jizhe Jia and Meng Shen are with the School of Cyberspace Science and
Technology, Beijing Institute of Technology, Beijing 100081, China, and also
with the State Key Laboratory of Cryptology, Beijing 100878, China (e-mail:
jiajizhe@bit.edu.cn; shenmeng@bit.edu.cn).
Yi Zhao, Bufan Zhao, and Liehuang Zhu are with the School of Cyberspace
Science and Technology, Beijing Institute of Technology, Beijing 100081,
China (e-mail: zhaoyi@bit.edu.cn; bitzbf@163.com; liehuangz@bit.edu.cn).
Susu Cui is with the Institute of Information Engineering, Chinese Academy
of Sciences, Beijing 100089, China (e-mail: cuisusu@iie.ac.cn).
Jing Wang is with the National Computer Network Emergency Response
Technical Team/Coordination Center of China, Beijing 100094, China (e-mail:
wangjing str@163.com).
Wei Wang is with the Key Laboratory for Intelligent Networks and Network
Security, Ministry of Education, Xi’an Jiaotong University, Xi’an 710049,
China (e-mail: wangwei1@bjtu.edu.cn).
Digital Object Identifier 10.1109/TIFS.2026.3685079

I. I NTRODUCTION
HE proliferation of network encryption protocols
(SSL/TLS [1]), while essential for privacy protection, has
inadvertently empowered cyber attackers to weaponize cryptographic channels. Modern malware, particularly remote access
trojans (RATs) that grant attackers administrative control
over compromised systems, increasingly leverages encrypted
traffic to evade traditional signature-based network intrusion
detection systems (NIDS) [2], [3], [4], [5]. This encryption
paradigm fundamentally reduces observable payload information at the transport layer [6], [7], [8], [9], resulting in sparser
features available for detection. Alarmingly, 60% of malware
spread over encrypted connections during Q4 of 2024, which
is an 8% increase from last quarter and a continued increase
for the year [10].
Researchers have proposed various detection methods that
can be categorized into four types based on their technical approaches: rule-based methods [11], machine learning
(ML)-based methods [2], [4], [12], deep learning (DL)-based
methods [3], [13], [14], and pre-training-based methods [15],
[16], [17]. Most of these methods mainly focus on specific
field features, statistical features, and packet sequence features
of full flows to build detection models. However, malware
attacks typically unfold through a phased and sequential process, and waiting for a complete flow collection will result in
delayed detection, which introduces a prolonged period before
taking countermeasures, resulting in non-negligible security
risks (e.g., financial losses and confidential data thefts). For
instance, in 2022, Costa Rica declared a nationwide emergency
following a major ransomware attack by the Conti Group,
impacting its Department of Finance and business activities.
The ransom demanded up to 20 million [18]. Early-stage
malware traffic detection refers to a continuous monitoring
and detection mechanism that can detect malware traffic as
early as possible (i.e., 20%, 30%) before the complete flow
transmission, which mitigates the risks to the victim, including
system file encryption, credential theft, and data exfiltration.
Despite some progress on detection accuracy and efficiency
in encrypted malware traffic detection [2], [3], [4], critical
challenges remain, which can be summarized as follows:
1) Information sparsity in early-stage traffic. While certain
methods [14], [16], [20] have explored detection using partial
traffic features, they heavily rely on the temporal accumulation
of intra-flow features. For instance, sequence-based models
like RNNs with attention [14] often require a substantial
observation budget (e.g., a large number of initial packets or
higher loading ratios) to achieve stable performance. When the
available traffic is extremely limited (e.g., the first 20%), the
information within a single isolated flow is often too sparse

T

1556-6021 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

JIA et al.: EARLY-STAGE DETECTION OF ENCRYPTED MALWARE TRAFFIC VIA TEMPORAL GRAPH LEARNING

TABLE I
F LOW D URATION S TATISTICS (S ECONDS ) OF THE S IX T YPICAL M ALWARE
IN THE CTU-M ALWARE DATASET [19]

to provide a definitive signature, leading to a significant drop
in accuracy for these methods. 2) Heterogeneity of attack
patterns. The heterogeneity of malware attack patterns is a
natural concealment method relative to detection methods, thus
posing a critical challenge to achieving high precision in earlystage traffic detection. For example, malicious activities (e.g.,
victim scanning, spam propagation, or click fraud) exhibit
highly divergent flow duration characteristics [21]. Botnets
like Zeus predominantly generate short-lived flows (median
duration < 1 second), whereas advanced threats like TrickBot
sustain prolonged connections (median duration > 1 minute),
as quantified in TABLE I.
In this paper, we propose DawnGuard, an effective
early-stage detection method that can accurately distinguish encrypted malware traffic based on early-stage traffic.
Specifically, due to information sparsity, existing single-flow
detection methods fail to identify encrypted malware traffic
in the early stage [20], [22]. To maximize the utilization of
available information in the early stage, we can analyze multiflow temporal interaction patterns that reveal distinct attack
behaviors (e.g., abnormal spam bot-SMTP communications
[4]) that deviate from benign traffic.
DawnGuard is composed of three key modules. First, the
early-stage interaction phase (e.g., protocol handshake and
configuration download) contains more distinctive properties
than the subsequent phase [2], [23]. To force the model
to focus on the early-stage interaction phase, we design
a self-adjusting data augmentation strategy. Crucially, this
strategy is self-adjusting because it dynamically determines
the optimal cut-off point for tail-masking for each flow by
analyzing its unique temporal packet density distribution.
This ensures that the augmented data consistently retains the
most discriminative, the early-stage interaction phase of the
traffic, which systematically addresses the sparsity of earlystage traffic information. Second, to address attack pattern
heterogeneity, we design a multi-flow temporal graph learning algorithm, which can explore temporal and topological
correlations between multiple flows to enrich discriminative
features in a malware attack, named Multi-Flow Graph Features (MGF) from multiple flows. Notably, compared with
single flow-based detection methods, a more global view
based on multiple flows within a malware attack reflects
more flow inter-relationships. Finally, we construct a Vision
Transformer (ViT)-based detector, which can capture both
local and global contextual relationships for accurate and
precise encrypted malware traffic detection with early-stage
traffic. For real-world deployments, DawnGuard employs a
persistent monitoring mechanism that iteratively collects packets and performs progressive traffic analysis across subsequent
monitoring cycles.

4461

The main contributions of this paper are as follows:
• We propose DawnGuard, an effective early-stage malware
traffic detection framework based on multi-flow temporal
graph learning. By focusing on information sparsity and
attack pattern heterogeneity, it achieves high-precision
early-stage detection by emphasizing high-density information, expanding multi-flow distinguishable properties,
as well as integrating local and global contextual
relationships.
• To solve information sparsity and boost training data
diversity, we propose a self-adjusting data augmentation
strategy, which combines temporal packet density analysis with a tail-masking method, thereby forcing the model
to focus on the early-stage interaction phase with more
distinctive characteristics.
• To adapt to the heterogeneity of attack patterns, we
develop the temporal graph learning method to extract
temporal-topological correlations among multiple flows
in a malware attack (i.e., MGF), which can provide more
distinguishable properties for early-stage detection.
• We evaluate DawnGuard in two real-world datasets in
three typical scenarios, i.e., varying early-stage time windows, imbalanced data, and unseen malware detection.
The results demonstrate that DawnGuard significantly
outperforms existing methods in all scenarios. Particularly, DawnGuard achieves an average F1 of 95.11%,
8.7% higher than the SOTA method, with the first 20%
loading ratio of complete traffic. We release the dataset
and source code of DawnGuard.1
The rest of the paper is organized as follows. We first
introduce the background and the threat model in Section II.
We present the high-level design of DawnGuard in Section III
and the design details in Section IV. Next, we conduct the
theoretical analysis in Section V and comprehensive experiments to evaluate the detection performance of DawnGuard
in Section VI. Finally, we review related works in Section VII
and conclude this paper in Section VIII.
II. P RELIMINARIES
In this section, we introduce the threat model and the
definition of early-stage detection.
A. Threat Model
From the attacker’s perspective, the attack surface comprises
the network boundary where compromised internal devices
interact with external malicious infrastructures, such as C&C
servers and malware delivery sites [2]. We assume that the
attacker can leverage encryption protocols (e.g., SSL/TLS) to
obscure payloads, rendering traditional Deep Packet Inspection
(DPI) ineffective. In addition, they can coordinate multiple
network flows to execute sophisticated, multi-stage objectives.
Note that, these attacks are typically constructed with numerous addresses controlled by attackers [4].
From the defender’s perspective, DawnGuard operates at
the network level, collecting traffic via port mirroring at
edge routers without deploying agents on end-user devices
1 https://github.com/jiajizhe1997/DawnGuard

4462

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

Fig. 1. The KDE of malware and benign traffic across packet length and IAT
in CTU-Malware dataset [19].

[3]. Our detection model operates under the assumptions that
the encryption algorithms can not be decrypted. Furthermore,
our detection scope is focused on detecting active network
attacks, excluding passive eavesdropping or side-channel analysis which do not generate network traffic.
B. Early-Stage Detection
A core challenge in this threat landscape is achieving effective early-stage detection, the ability to identify and prevent
damage before an attack sequence fully unfolds. Ideally, a
detection model should react within the initial phase of a
connection (e.g., the first 20-40% of the complete traffic).2
This not only enables timely mitigation but also ensures
the model acquires sufficient discriminative data before a
potentially short-lived malicious flow terminates [24].
A natural question that arises is the selection between
relative and absolute early-stage time windows. We analyze
the flow durations of six representative malware families (i.e.,
Dridex, Emotet, Geodo, Miuref, Zeus, and TrickBot) from the
malware capture project [19]. As shown in TABLE I, the
flow durations exhibit significant statistical variations across
different malware. An absolute window that is effective for
a short-lived attack might be insufficient for a long-running
one. Therefore, to ensure that DawnGuard remains effective
across diverse malware, we adopt a relative early-stage time
window, analyzing packets across different loading ratios of a
flow rather than relying on a fixed absolute time window.
III. D ESIGN OF DAWN G UARD
In this section, we present the motivation for our design and
provide an overview of DawnGuard.
A. Motivation
Malware traffic detection faces a dual challenge. As shown
in Fig. 1, fundamental single-flow features (e.g., packet length,
IAT) exhibit significant overlap between benign and malware
traffic in CTU-Malware [19]. This ambiguity limits single
flow-based methods [15], [25], [26], which lack the context
to detect multi-flow patterns like C&C communication.
To incorporate such context, graph-learning techniques [2],
[4], [27] have been adopted but suffer from two shortcomings.
First, global modeling paradigms indiscriminately include all
concurrent flows, introducing noise from irrelevant activities.
Second, static graph modeling ignores temporal interdependencies, causing flows with different chronological orders to
yield isomorphic structures, thus eroding the detection of timesensitive patterns.
2 For instance, DawnGuard detects TrickBot traffic, which has an average
duration exceeding 60 seconds, using only the first ∼12 seconds (20%) of the
flow, as shown in TABLE I.

Fig. 2. Packet load ratio analysis over time for the flows of six typical malware
in the CTU-Malware dataset [19].

Afterward, we explore the possibility of achieving earlystage malware traffic detection without waiting for the whole
flow termination. While recent methods [14] have investigated early detection by focusing on initial packet segments
within isolated flows, they remain constrained by single-flow
information scarcity. Our analysis of such methods reveals
that they often require a relatively high observation budget
(e.g., a substantial number of initial packets or higher loading ratios) to extract stable signatures. When the available
traffic is extremely limited (e.g., the first 20%), the internal
information of a single flow is often too sparse to provide a
definitive malicious signature, leading to degraded reliability.
However, temporal packet density analysis (Fig. 2) reveals
that even within these sparse segments, early interactions
(e.g., handshakes, C&C establishment) exhibit higher packet
concentrations and more distinctive properties than subsequent phases. Thus, the key challenge is to extract these
discriminative signals from minimal and sparse early-stage
data.
Driven by these observations, the design of DawnGuard
is guided by two core intuitions to overcome the limitations
of current detection approaches. First, to resolve single-flow
ambiguity and filter global noise, we propose a multi-flow temporal graph learning framework. Unlike single-flow sequence
models that hit an information bottleneck in the earliest
phases, this framework leverages the topological structure
of concurrent flows to reconstruct the global attack context,
thereby isolating attack progression from background noise
even with minimal data. Second, to specifically address information sparsity at extremely low loading ratios, we design
a self-adjusting data augmentation mechanism. By dynamically locating high-density interaction phases and generating
diverse, realistic training samples, this mechanism forces the
model to learn intrinsic malicious patterns that remain invisible
to methods relying on isolated single flow or static observation
windows.
B. Overview of DawnGuard
As shown in Fig. 3, itDawnGuard consists of three
modules: Self-Adjusting Data Augmentation, Multi-Flow
Temporal Graph Learning, and Early-Stage Malware
Detection.
1) Self-Adjusting Data Augmentation: To address information sparsity, we design a self-adjusting mechanism that
dynamically determines the optimal tail-masking point for
each flow. This approach generates diverse training samples

JIA et al.: EARLY-STAGE DETECTION OF ENCRYPTED MALWARE TRAFFIC VIA TEMPORAL GRAPH LEARNING

4463

Fig. 3. The system overview of DawnGuard.

and directs the model’s attention to the critical early interaction
phase with distinctive characteristics. We detail this module in
Section IV-A.
2) Multi-Flow Temporal Graph Learning: To address
attack pattern heterogeneity, we design an algorithm to synergistically explore temporal-topological correlations among
multiple flows (i.e., MGF). This approach integrates distinguishable properties reflected by flow inter-relationships to
enhance early-stage malware detection. We elaborate on this
module in Section IV-B.
3) Early-Stage Malware Detection: Given the multi-flowbased traffic representation, i.e., MGF of each flow, we develop
a ViT-based detector to capture both local and global contextual relationships from spatial-temporal features and detect
early-stage encrypted malware traffic accurately and precisely.
We will describe the details of our detector in Section IV-C.

TABLE II
L IST OF N OTATIONS

IV. D ESIGN D ETAILS
In this section, we present the design details of DawnGuard, including self-adjusting data augmentation, multi-flow
temporal graph learning, and early-stage malware detection.
The main notations are illustrated in Table II.
A. Self-Adjusting Data Augmentation
To address the challenge of information sparsity in earlystage traffic, we propose a self-adjusting data augmentation
module. Self-adjusting refers to the mechanism that dynamically determines the optimal tail-masking point for each
traffic flow, rather than applying a fixed or random masking
ratio. This process aims to precisely preserve the critical, high-density early-stage interaction phase (e.g., protocol
handshakes) within the augmented traffic. Consequently, this
strategy forces the model to focus on the more distinguishable
property part in the early stages, thereby boosting training data
diversity and enhancing detection performance.
1) Temporal Packet Density Distribution Analysis: To
ensure the augmented traffic contains sufficient information
for detection, we analyze packet distributions by dividing

flows into loading ratio slots. We define the packet density
di ∈ D = {d1 , d2 , . . ., dn } as the ratio of packets in the i-th slot
to the total packet count. For generality, we analyze six typical
malware from the CTU-Malware dataset [19].
As illustrated in Fig. 2, packet density is significantly
higher in the early-stage interaction phase than in subsequent

4464

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

phases. Specifically, 35% of total packets (and up to 96%
for Geodo) are typically transmitted within the initial 10%
of flow duration, driven by protocol handshakes and C&C
establishment. This pattern concludes with a low-activity phase
or session termination. Consequently, we design a mask-based
data augmentation strategy that preserves these high-density,
discriminative early-stage interactions.
2) Mask-Based Data Augmentation: Data augmentation
improves model performance by boosting training diversity,
but fixed masking ratios either erase critical semantics or retain
redundant noise. To address this, we propose a density-aware,
self-adjusting data augmentation strategy. By dynamically
generating early-stage samples with adaptive tail-masking,
it enables the subsequent graph learning module to capture
multi-scale temporal dependencies and resolve information
sparsity. As detailed in Algorithm 1, the process involves
three phases: adaptive time bin partition, density-aware dualthreshold selection, and adaptive tail masking.
a) Adaptive Time Bin Partition (Algorithm 1, Lines 3-8).
To handle flows of varying durations, we partition each flow
into K adaptive time bins and calculate the raw packet density
array D in each time bin in Eq. (1).
(k − 1)
K+1
T total
(1)
where bk = t1 +
B = {bk }k=1
K
We then apply Savitzky-Golay smoothing [28] to suppress
high-frequency noise while preserving critical phase transition
patterns, yielding the smoothed density curve D̃, thereby
facilitating the robust location of density plunge points for
threshold calculation in Eq. (2).
D̃[k] = SG-Filter(D, window, poly order)

(2)

Here, window denotes the number of adjacent data points used
for local polynomial fitting, while poly order denotes the
polynomial degree to model the underlying trend.
b) Density-Aware Dual-Threshold Selection (Algorithm 1,
Lines 10-16). We design a dual-threshold mechanism to locate
the optimal plunge point of early-stage interactions. A hard
threshold τh detects sharp traffic drops (e.g., handshake completion) by finding the first bin where density falls below a
fraction γ of the peak density within a search bound β:
˚
kh = min k ∈ {1, . . . , K} | D̃[k] < γ · max(D̃[1 : dβKe]) (3)
Alternatively, a soft threshold τ s identifies progressive density decay. We introduce a sensitivity hyperparameter θ (i.e.,
representing the declination angle) to control this progressive
decay detection. The soft threshold is dynamically calculated
based on the average density scaled by this slope factor, as
defined in Eq. (4).
K

τ s = tan(θ) ·

1 X
D̃[k]
K

(4)

k=1

Here, D̃[k] represents the packet density in the k-th bin,
and tan(θ) adjusts the threshold relative to the overall traffic
volume. We then slide a three-slot window to find the first
point k s where the density decrease ∆ s across three consecutive
bins consistently exceeds τ s :
8
9
2
<
=
^
k s = min k ∈ {3, . . . , K} |
(∆ s [k − j] > τ s )
(5)
:
;
j=0

Algorithm 1 Self-Adjusting Data Augmentation

The final termination point is determined by the minimum of
kh , k s , and a pre-defined minimum retention bound derived
from ratio α (Algorithm 1, lines 15-16).
c) Adaptive Tail Masking (Algorithm 1, Lines 18-22). Based
on the identified termination point, we establish a masking
window Wi to obscure the non-critical tail traffic of flow fi ,
yielding Fmasked (Algorithm 1, lines 18-22). This strategic truncation forces the subsequent graph learning module to focus on
highly distinguishable early-stage interaction representations.

B. Multi-Flow Temporal Graph Learning
Utilizing the early-stage traffic generated by the selfadjusting data augmentation module, the multi-flow temporal
graph learning module explores temporal-topological correlations among multiple flows in a malware attack (i.e., MGF),
which enriches discriminative features for early-stage malware
traffic detection. Specifically, we first design a traffic representation method to extract single-flow features (i.e., Packet Byte
Matrix) efficiently from raw traffic. Afterward, we construct a
host-server bipartite graph to capture the interactions between
hosts and external servers. Based on the bipartite graph,
we design a multi-flow temporal graph learning algorithm
to extract temporal-topological correlations between multiple
flows in a malware attack. The details are as follows:

JIA et al.: EARLY-STAGE DETECTION OF ENCRYPTED MALWARE TRAFFIC VIA TEMPORAL GRAPH LEARNING

4465

Algorithm 2 Temporal Graph Learning

Fig. 4. Illustration of observable unencrypted metadata (e.g., Extensions)
within the payload bytes of encrypted traffic.

1) Single-Flow Feature Extraction: To extract multidimensional features efficiently, we design the Packet Byte
Matrix (PBM). For each flow, we strictly monitor the first M
consecutive packets. Each packet is partitioned into a header
segment (X bytes) and a payload segment (Y bytes). To prevent
the model from overfitting to network-specific artifacts (e.g.,
MAC/IP addresses and port numbers), we apply standard
traffic anonymization strategies [29] to these raw bytes.
We preserve complete header fields and retain the first
Y bytes of the packet payload. Crucially, while encryption
obscures the semantic content of the payload, the initial
bytes in early-stage traffic often carry unencrypted protocol
metadata specific to malware families [2], [20], such as TLS
handshake extensions and Server Name Indication (SNI), as
shown in Fig. 4. By including these payload segments in
the PBM, we enable the model to capture these fingerprints
that remain observable even in encrypted traffic. The headerpayload sequences from M packets are reshaped into a 2D
matrix M ∈ R2×Q . Here, Q = M × (X + Y)/2.
2) Bipartite Graph Construction: We design a bipartite
graph, G = (H, S, E, F, T ) to represent the interaction relationships between hosts and external servers that are linked to each
host. We denote the hosts as a vertex set H, where each host is
uniquely identified by its IP address. Differently, we denote the
external servers as a vertex set S, where each external server
is uniquely identified by its IP address and port. Besides, we
adopt an edge set E = {e|e = {he , se }, ∀he ∈ H, ∀se ∈ D} to
denote all interaction relationships between hosts and servers.
If there is a connection between the host h and an external
server s, then an edge e = (h, s) is constructed between them.
We denote the features extracted from every single flow e as
F = { fe |∀e ∈ E} through the single-flow feature extraction.
We denote the corresponding timestamp of every flow e as
T = {te |∀e ∈ E}. Here, te is defined as the timestamp of the
first packet in flow e.
3) Graph Representation Learning: To explore temporaltopological correlations among concurrent flows in a malware
attack, we design a Temporal Graph Learning Algorithm
tailored for early-stage detection. Compared to traditional
Probabilistic Graphical Models (PGM) [30] that rely on
predefined assumptions and struggle with continuous traffic,
our approach enables joint end-to-end optimization of intraflow features and inter-flow topologies, effectively capturing
complex non-linear malware attack correlations.
As outlined in Algorithm 2, the learning process integrates
sinusoidal temporal encoding, time-aware neighbor sampling,
and time-weighted aggregation across K layers to generate the
final Multi-Flow Graph Features (MGF).

a) Sinusoidal Temporal Encoding (Algorithm 2, Line 2). To
model the sequential dependencies of concurrent flows without
introducing absolute timestamp bias, we project flow initiation timestamps into a continuous vector space. Inspired by
Transformer positional encodings [31], we apply a sinusoidal
mapping Φ(te ) as shown in Eq. (6).
!
!
te
te
Φ(te )2i = sin 2i/d p , Φ(te )2i+1 = cos 2i/d p
(6)
τbase
τbase
Note that d p is the encoding dimension and τbase = 10000.
Instead of directly concatenating Φ(te ) with node features, we
maintain it as a parallel structural context to calculate the
relative time lag ∆tu,e between flows, dynamically modulating
subsequent neighbor filtering and aggregation.
b) Time-Aware Neighbor Sampling (Algorithm 2,
Lines 7-11). Malware attacks typically exhibit strong temporal
locality [20], while older flows often represent unrelated
background noise. To maintain computational efficiency and
focus on highly correlated events, we dynamically filter the
host-centric neighborhood Ce . At each layer k, we restrict
candidate neighbors to a sliding time window τk and retain
only the top-n most recent interactions:
˚
Nt(k) (e) = Top-n u ∈ Ce | ∆tu,e ≤ τk
(7)

4466

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

c) Time-Weighted Aggregation (Algorithm 2, Lines 13-21).
Standard graph convolutions treat all neighbors equally, failing
to capture the time-sensitive nature of attack behaviors. We
introduce a time decay factor λ to assign higher attention
weights to recent interactions. For each neighbor u, the weight
wu,e is computed as shown in Eq. (8).
wu,e = exp(−λ · ∆tu,e )

(8)

A positive λ ensures recent edges receive higher weights
(wu,e ≈ 1 when ∆t → 0). Neighbor features are then aggregated
into a latent space as detailed in Eq. (9):
1
0
X
w
C
B
Pu,e h̃(k−1)
(9)
h(k)
A
u
N (e) = σ @
w
(k)
u∈Nsampled

w

where Pu,ew is the normalized temporal coefficient ensuring
scale-invariance, and h̃(k−1)
denotes the neighbor representation
u
from the previous iteration (with h̃(0) = F).
To update the edge representation, we concatenate selfinformation with aggregated context, as shown in Eq. (10).


(k) (k−1) (k)
h̃(k)
, hN (e) )
(10)
e = σ CONCAT(Wself h̃e

b) Transformer Encoder. The embedded patches pass
through six Transformer encoder layers, each consisting of
Multi-Head Self-Attention (MHSA) with eight heads to model
long-range dependencies, layer normalization after each sublayer, a position-wise feed-forward network with Gaussian
Error Linear Unit (GELU) activation, and residual connections around each sub-layer. Specifically, MHSA projects the
queries, keys, and values into h independent subspaces through
linear transformations in Eq. (12).
MHS A(Q, K, V)
= CONCAT (head1 , head2 , . . . , headh )W O

(12)

Note that headi = Attention(QWiQ , KWiK , VWiV ), and WiQ , WiK ,
WiV , and W O are all learnable parameter matrices.
Following the self-attention mechanism in our ViT architecture, the second sublayer implements a position-wise
feed-forward network (FFN), which consists of two consecutive linear transformations with a GELU activation in
Eq. (13).
FFN(x) = W2 · GELU(W1 x + b1 ) + b2

(13)

Here, W(k)
self is a learnable matrix designed to preserve the
edge’s own information from the previous state, while σ(·)
(ReLU) mitigates gradient vanishing. After K iterations, the
representation is normalized to a unit vector (Algorithm 2,
line 18). For notational convenience, we denote the final
representation output at depth K as zeK (Algorithm 2, line 19).
Finally, to prevent the dilution of original single-flow features
fe , we extract MGF (i.e., zeK ) as shown in Eq. (11).

Here, W1 and W2 are the weight parameters, b1 and b2 are the
bias parameters.
c) Classification Head. We apply a lightweight classification
head to the final [CLS] token embedding, consisting of layer
normalization and a linear layer with a softmax function. The
model is optimized via Adam with weight decay and crossentropy loss, using dropout for regularization.

zeK = CONCAT ( fe , zeK )

V. T HEORETICAL A NALYSIS

(11)

C. Early-Stage Malware Detection
In this module, we propose a ViT-based detector to
capture both local and global contextual relationships and
achieve early-stage encrypted malware traffic detection, consisting of an input layer and a ViT-based architecture, as
follows:
1) Input Layer: The proposed ViT-based detector accepts
the output MGF (i.e., zeK ) of the multi-flow feature extraction
as input, represented as a 2D matrix M ∈ R2×(Q+L) with a
single channel (1 × 2 × (Q + L)). By adjusting the number
of packets M, the number of bytes for the packet header X,
and the payload Y, we extract various lengths of PBM, i.e.,
Q. By adjusting the output length of the multi-flow feature
embedding, we extract various lengths of zeK , i.e., L.
2) ViT-Based Architecture: We adopt the ViT framework
[32] to capture both local and global contextual relationships
in the traffic data. The architecture consists of three main
components as follows.
a) Patch Embedding and Positional Encoding. We split
the input tensor into non-overlapping patches. Each patch is
projected into an embedding space through a linear layer.
To retain positional information, we add learnable 1D positional embeddings and a [CLS] token to aggregate global
features.

To quantitatively analyze the optimality of DawnGuard, we
model the malware traffic detection process as an information
preservation problem. Let the optimal detection performance
be bounded by the mutual information I(X ; Y) between the
raw traffic space X and the label space Y. We demonstrate that
our three-stage design minimizes the information loss Lin f o
compared to existing methods.

A. Entropy Model Setup
We formalize a single flow as a random variable sequence
X = {x1 , x2 , . . ., xL } governed by a distribution P(X). For
detection methods treating flows in isolation, performance is
theoretically bounded by the mutual information I(X; Y) with
the label Y. By the data processing inequality [33], any feature
extraction φ(X) yields I(φ(X); Y) ≤ I(X; Y), establishing an
information barrier for intra-flow methods.
However, in real-world networks, X correlates with neighbor
flows, denoted as context C. Consequently, the true approachable bound is their joint mutual information: I(X, C; Y) =
I(X; Y) + I(C; Y|X). While single-flow baselines are limited to
I(X; Y), our graph-based framework leverages this expanded
observable space to capture the conditional mutual information
I(C; Y|X), fundamentally raising the theoretical upper bound of
detection accuracy.

JIA et al.: EARLY-STAGE DETECTION OF ENCRYPTED MALWARE TRAFFIC VIA TEMPORAL GRAPH LEARNING

B. Analysis of Main Modules in DawnGuard
1) Self-Adjusting Augmentation as Optimal Information
Selection: Unlike simply assigning more weight to early
stages of data, our Self-Adjusting Data Augmentation identifies and preserves the region of highest information density.
Given a flow X with packet densities D = {d1 , . . ., dL }, the
goal of tail masking is to find an optimal truncation point
k∗ such that the retained subsequence X1:k∗ maximizes the
relevant information density while minimizing redundancy, as
shown in Eq. (14).
I(X1:k ; Y)
s.t. k ≥ αL
(14)
k∗ = arg max
k
k
Our dual-threshold mechanism (Algorithm 1) dynamically
estimates this k∗ by detecting the plunge point of packet
(i)
density. By synthesizing augmented samples {X1:k
∗ } concentrated around this high-density phase (e.g., handshakes), we
reconstruct a training distribution P̂aug that approximates the
true intrinsic distribution Pint of malware behaviors more
accurately than the raw distribution Praw . Thus,
H(P̂aug ) ≈ H(Pint ) =⇒ I(Daug ; Y)  I(D static ; Y)

(15)

This proves that our density-aware strategy theoretically
retains more discriminative information than static weighting.
2) Temporal Graph Learning as Causal Information Recovery: While existing graph learning based methods exploit
contextual information, they typically treat all neighbors N (e)
equally, ignoring the temporal interdependencies between multiple flows. In malware detection, attack patterns exhibit strong
causal dependencies. Treating historical neighbors (high ∆t)
as equivalent to recent ones introduces temporal noise, which
increases the conditional entropy H(Y|N (e)). Our module
addresses this by maximizing the Causal Mutual Information
through two mechanisms as follows.
a) Time-Aware Sampling as Relevance Denoising: Let the
neighborhood set Nall contain all historical interactions. Most
elements in Nall are statistically independent of the current
attack state Y due to large time lags (i.e., larger than 5 minutes
[20]). DawnGuard filters neighbors using a sliding window τk
to construct a subset Nt∗ . This process can be modeled as
searching for the optimal context window that maximizes the
information density, as shown in Eq. (16).
I(S; Y)
s.t. ∀u ∈ S, ∆tu,e ≤ τk
(16)
Nt∗ = arg max
S⊆Nall
|S|
By discarding outdated interactions, we effectively prune the
graph topology to remove uncorrelated edges that would act
as entropy noise sources.
b) Time-Weighted Aggregation as Causal Weighting: Even
within the active window,
P relevance is different. The standard aggregation sum
hu assumes a uniform prior on
neighbor importance [27]. Our decay mechanism wu,e =
exp(−λ∆tu,e ) introduces a temporal prior Ptime (∆t) that aligns
with the natural decay of network causality. The aggregated
(k)
representation hN
(e) thus represents a weighted information
integration:
X
(k)
I(hN
wu,e · I(u; Y)
(17)
(e) ; Y) ≈
u∈Nt∗

Specifically, our mechanism aligns the attention weights wu,e
with the temporal decay of causal dependencies, thereby prioritizing recent neighbors that inherently maximize the mutual

4467

information I(u; Y). This targeted prioritization allows the
model to effectively extract temporal discriminative patterns
while suppressing interference from outdated noise.
3) ViT as Optimal Information Aggregation: Finally, we
analyze the encoding efficiency. Let Z be the final representation. A standard CNN encoder with local receptive fields
effectively applies a mask M, losing long-range dependencies:
I(ZCNN ; Y) = I(X; Y) − H(Xlong ). In contrast, the ViT architecture in DawnGuard, with its global self-attention mechanism,
maintains a global receptive field. Thus, it minimizes the
encoding loss, as shown in Eq. (18).
HDawnGuard ≥ HCNN =⇒ I(ZViT ; Y) ≈ I(Zoptimal ; Y)

(18)

C. Quantitative Analysis of Information Loss
To evaluate the theoretical optimality discussed in
Section V-B, we conduct a quantitative evaluation of the information preservation capabilities of DawnGuard. Following
the entropy model setup, we need to measure the Mutual
Information I(Z; Y) between the extracted high-dimensional
continuous features Z and the discrete label space Y. To quantify this, we utilize the Kraskov-Stögbauer-Grassberger (KSG)
estimator [34]. Because traditional binning-based methods
suffer from severe bias in high-dimensional continuous spaces.
In contrast, the KSG estimator provides estimation based
on k-nearest neighbors. It adjusts neighborhood distances to
mitigate estimation bias for continuous, discrete variable pairs
without requiring prior assumptions about the data distribution,
thereby ensuring the reliability of our information loss quantification. Our evaluation subset comprises randomly selected
1000 TrickBot samples in the CTU-Malware dataset [19] from
D1 and 1000 benign samples from D4 .
As shown in Table III, the results demonstrate a significant
reduction in information loss across all three dimensions:
1) Sparsity-Induced Loss Reduction: Compared to applying
a static high weight to the first 30% traffic, our self-adjusting
data augmentation preserves more discriminative information
by dynamically locating high-density interaction phases.
2) Independence-Assumption Loss Reduction: By expanding the observation space from isolated single flows to
temporal multi-flow graphs, DawnGuard captures the conditional mutual information I(C; Y|X), and reduces the entropy
noise from irrelevant background traffic.
3) Locality-Induced Loss Reduction: The ViT-based architecture, benefiting from its global self-attention mechanism,
minimizes encoding loss by maintaining long-range dependencies that are often masked by the local receptive fields of
CNN-based models.
These findings demonstrate that unlike the methods that
suffer from sparsity-induced loss (low Ĥ), independenceassumption loss (missing I(C|X)), and locality-induced loss
(masking Xlong ), DawnGuard minimizes these information
losses, theoretically approaching the detection optimality.
VI. P ERFORMANCE E VALUATION
We prototype DawnGuard and conduct extensive experiments to evaluate its effectiveness. Moreover, we compare its
accuracy with state-of-the-art methods on existing datasets,
including two well-known real-world datasets. In general, the
experiments will demonstrate that DawnGuard is able to:

4468

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

TABLE III
Q UANTITATIVE R EDUCTION OF I NFORMATION L OSSES ACROSS D IFFERENT M ODULES IN DAWN G UARD

• detect various malware traffic in varying early-stage loading ratios and time windows (Section VI-B).
• achieve reliable early-stage malware detection in highly
imbalanced data scenarios, effectively mitigating the bias
towards the majority benign class (Section VI-C).
• achieve zero-shot detection ability to capture unseen patterns of malware traffic generated by unknown malware
types (Section VI-D).
• exhibit strong stability across different parameter configurations (Section VI-E).

A. Experiment Setting
Baseline Methods. To measure the improvement achieved
by DawnGuard, we establish five baselines, among which two
are multi-flow-based, i.e., ST-Graph [2] and CBSeq [3]. Additionally, YaTC [16] is included as a representative baseline
that enables detection without requiring complete traffic.
• Kitsune [13] uses unsupervised autoencoders for feature
learning and anomaly detection.
• FC-Net [15] detects malicious traffic by extracting imagebased feature maps from raw flows.
• ST-Graph [2] explores network behaviors using graph
learning frameworks integrated with TLS metadata.
• CBSeq [3] characterizes attacking intents via a
Transformer-based multi-flow representation.
• YaTC [16] leverages a Masked Autoencoder architecture
and raw-byte representations for traffic classification.
Evaluation Dataset. As shown in TABLE IV, we use the
following public datasets for evaluation.
• CTU-Malware [19]. Comprising continuous real-world
PCAP traces, this dataset preserves flow chronology
for the temporal-topological reconstruction of multi-flow
attacks. We select six malware families (Dridex, Emotet,
Geodo, Miuref, Zeus, TrickBot) for D1 , reserving the
remainder (D2 ) for unseen malware evaluation.
• USTC-TFC2016 [35]. Comprising ten categories each of
benign and malware traffic, this dataset’s timestamps and
IPs are used to establish session contexts, grouping interactions into local subgraphs. D3 and D4 are constructed
from its malware and benign subsets, respectively.
Evaluation criteria. The fundamental goal of encrypted
malware traffic detection is to be accurate. To achieve this goal,
we mainly use the F1 and AUC because they are most widely
used in the literature [3], [4], [13]. We also use precision to
validate DawnGuard’s improvements. The formal definitions
of these metrics are presented in Eq. 19 and 20.
Precision =

TP
,
T P + FP

Recall =

TP
T P + FN

(19)

Fig. 5. The evaluation results (%) of different detection methods at different
loading ratios of malware in D3 .

F1 =

2 · Precision · Recall
,
Precision + Recall

AUC =

Z 1
ROC(x) dx
0

(20)
T P, T N, FP, and FN denote the number of True Positives,
True Negatives, False Positives, and False Negatives.
Implementation Details. To ensure the reproducibility of
our results and facilitate fair comparisons with baselines, we
provide the implementation details as follows.
• Setup & Scalability. All experiments were conducted
on a server with an Intel Core i73.4 GHz, 32GB RAM,
and an RTX 3080 using PyTorch. To ensure scalability
on RAM-constrained hardware, DawnGuard avoids full
dataset loading by streaming traffic via mini-batches.
• Data Partitioning & Preprocessing. Datasets (D1 –D4 )
were split into training, validation, and testing sets at flow
granularity via stratified sampling with an 8 : 1 : 1 ratio.
To build inter-flow interaction graphs, we sorted flows
chronologically, which bridges the gap between discrete
flows and the required graph structure.
• Evaluation Setting. For fair comparison, baseline hyperparameters were tuned on our validation set to match
or exceed their reported performance. Under loading
ratio η, input traffic was truncated for all methods to
the same initial segment and all statistics were derived
from these observed segments to eliminate look-ahead
bias.
• Validation. It is important to note that the datasets used
in training and testing are entirely independent. To reduce
the impact of randomness in sample selection, we repeat
all experiments ten times to ensure more credible results.
• Hyperparameter Settings. Data Augmentation: retention
ratio α = 0.1, min packets µ = 6, Savitzky-Golay smoothing (window 11, poly order 3), threshold coefficient
γ = 0.3, peak density bound β = 0.15, and soft threshold
angle θ = 30◦ . Feature Extraction: initial packets M = 6,
header bytes X = 80, and payload bytes Y = 240 [16].
Graph Learning: time window τk = 5 minutes [20], max
neighbors n = 8, depth K = 2, time encoding dimension

JIA et al.: EARLY-STAGE DETECTION OF ENCRYPTED MALWARE TRAFFIC VIA TEMPORAL GRAPH LEARNING

4469

TABLE IV
S UMMARY OF THE DATASETS W ITH T RAFFIC T YPES AND F LOW C OUNTS PER C ATEGORY

TABLE V
T HE E VALUATION R ESULTS (%) OF D IFFERENT D ETECTION M ETHODS AT D IFFERENT L OADING R ATIOS OF M ALWARE IN D1

TABLE VI
T HE E VALUATION R ESULTS (%) OF D IFFERENT D ETECTION M ETHODS AT D IFFERENT E ARLY-S TAGE T IME W INDOWS OF M ALWARE IN D1

m = 64, edge embedding dimension ω = 512, and dropout
0.1. Detection Phase: 2D matrix M ∈ R2×1088 (fusing
1920 single-flow and 256 multi-flow features), patch size
2×64. The Transformer Encoder uses 6 layers, 8 attention
heads, and a hidden dimension of 512. We trained the
model with a batch size of 150, learning rate 0.0001, and
weight decay 0.001.
B. Malware Detection in Varying Early-Stage Time Window
We evaluate detection performance in relatively early-stage
windows (loading ratios η ∈ {20%, 30%, 40%, 100%}) and

absolute windows (t ∈ {1s, 3s, 5s, 10s}) based on Table I. We
build binary classifiers for malware in D1 , D3 , and benign
traffic in D4 . To observe the performance of these methods
in detecting early-stage malware traffic, we generate testing
traffic in different loading ratios and time windows based on
packet timestamps. The results are illustrated in Fig. 5 and 6,
TABLE V and VI.
As shown in TABLE V and Fig. 5, itDawnGuard achieves
the best detection F1 and AUC under each early-stage time
window setting in both evaluation datasets. Specifically, Fig. 5
(a) and (b) visualize the Precision and F1 trends on D3 . It is
evident that while the performance of all methods improves

4470

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

Fig. 6. ROC of different detection methods at different loading ratios of
malware in D1 and D3 .

Fig. 8. The detection F1 (%) of different parameter settings at different loading
ratios of malware in D3 .

Fig. 7. The early-stage unseen malware detection F1 of different methods
under different imbalance ratios in D2 .

as the loading ratio increases from 20% to 100%, DawnGuard
maintains a consistently high performance curve. In contrast,
the curves for baseline methods like FC-Net and Kitsune
show a sharp decline in the low loading ratio region (e.g.,
20%-30%), visually demonstrating their inability to handle
sparse early-stage information. Even in the smallest loading
ratio scenario in D1 , i.e., η = 20%, where data is most sparse,
DawnGuard still achieves an average F1 of 95.11%, which
is 8.7% improvement over the best accuracy of the SOTA
methods. DawnGuard demonstrates a significant advantage
in early-stage detection compared with the SOTA methods,
which can be primarily attributed to our self-adjusting data
augmentation and the MGF representation. The self-adjusting
data augmentation dynamically creates effective training samples from limited early-stage data (see the 22.33% F1 drop
without the data augmentation module in ablation study in
Fig. 9), while the MGF representation’s ability to model interflow dependencies allows it to extract meaningful patterns even
from scarce data (see the 14.57% F1 drop without multi-flow
features in ablation study in Fig. 9). In contrast, methods
relying on single flow or static graph fail to compensate
for the information scarcity. The results at different specificsize time windows are illustrated in TABLE VI and also
demonstrate the effectiveness of DawnGuard in early-stage
detection.

Fig. 9. Ablation study: comparing existing models.

As shown in TABLE V, DawnGuard consistently outperforms baselines across all early-stage settings, exhibiting the
highest average and minimum precision on the six malware
families. This demonstrates its reliability in early-stage detection. It stems from our multi-flow temporal graph learning,
which extracts distinguishable properties among multiple flows
to precisely detect diverse malware attacks.
In addition, we also evaluate the performance of DawnGuard under the complete dataset without splitting early-stage
time windows. As shown in TABLE V and Fig. 5, it can
be found that DawnGuard achieves the F1 of 99.36% and
AUC of 99.81% on average in D1 , and the F1 of 99.88% and
AUC of 99.99% on average in D3 , which are higher than the
best accuracy of the SOTA methods. While Kitsune fails in
D1 due to ineffective feature extraction, these results confirm
that our MGF representation efficiently captures discriminative
features for malware traffic detection.
To further evaluate the robustness against false positives,
which is critical for deployment in large-scale networks, we
analyze the Receiver Operating Characteristic (ROC) curves of

JIA et al.: EARLY-STAGE DETECTION OF ENCRYPTED MALWARE TRAFFIC VIA TEMPORAL GRAPH LEARNING

4471

TABLE VII
T HE E VALUATION R ESULTS (%) OF D IFFERENT D ETECTION M ETHODS U NDER D IFFERENT I MBALANCE R ATIOS OF B ENIGN AND M ALWARE IN D1

TABLE VIII
T HE E VALUATION R ESULTS (%) OF D IFFERENT D ETECTION M ETHODS U NDER D IFFERENT I MBALANCE R ATIOS OF B ENIGN AND M ALWARE IN D3

different methods. Fig. 6 illustrates the ROC curves for loading
ratios of 20% and 30% on both D1 and D3 . We observe that
DawnGuard consistently maintains a better performance, with
its curve significantly closer to the top-left corner compared to
all baselines. Specifically, as shown in Fig. 6(a) and (c), even at
a challenging 20% loading ratio, DawnGuard achieves a high
True Positive Rate (TPR) while suppressing the False Positive
Rate (FPR) to a near-zero level. In contrast, baseline methods
like Kitsune and FC-Net exhibit a much slower rise in TPR,
indicating they would trigger significantly more false alarms
to reach the same detection sensitivity. This high resistance to
false positives demonstrates that our multi-flow temporal graph
learning can extract discriminative features that effectively
distinguish coordinated malware activities from benign traffic.

which reinforces discriminative features in sparse early stages
to mitigate bias towards the majority class. The evaluation
results under different imbalanced ratios in D3 are shown in
TABLE VIII, which also demonstrates the generalization capability of DawnGuard in imbalanced data.
In addition, TABLE VII also illustrates that DawnGuard
achieves the most stable detection performance in average
and minimum precision across different malware under each
imbalance ratio setting. From ρ = 4 : 1 enlarges to ρ = 48 : 1,
average precision remains higher than 89% and only reduces
by 4.54%, which is superior to the SOTA methods. In the
highest imbalance ratio, i.e., ρ = 48 : 1, DawnGuard achieves
an average and minimum precision of 91.53% and 89.73%,
which are 34.83% and 42.75% higher than the SOTA method
in this scenario, FC-Net.

C. Early-Stage Malware Detection in Imbalanced Data
To evaluate the ability against imbalanced data in earlystage detection, we construct a binary classifier for each type
of malware traffic in D1 and D3 and benign traffic in D4 .
Performance across varying imbalance ratios of benign and
malware samples ρ ∈ {4 : 1, 16 : 1, 48 : 1} is summarized in
TABLES VII and VIII.
As shown in TABLE VII, DawnGuard consistently outperforms baselines across all imbalance ratios. Even under
extreme imbalance, i.e., ρ = 48 : 1, it achieves an average F1 of 92.9% and an AUC of 99.54%, surpassing the
best SOTA method by 35.19% and 7.89%, respectively. This
advantage stems from our self-adjusting data augmentation,

D. Unseen Malware Early Detection in Imbalanced Data
In this section, we evaluate the ability of different methods
to deal with imbalanced datasets in early-stage unseen malware detection. Specifically, we construct a binary classifier
trained by D1 and detect malware traffic in D2 in the early
stage. To observe the detection performance of these methods
when the imbalance ratio changes, we set the imbalance ratios
of the data as ρ ∈ {4 : 1, 16 : 1, 48 : 1}.
As shown in Fig. 7, itDawnGuard achieves the best
unseen malware detection accuracy under each imbalance ratio
setting. Even in the most highly imbalanced dataset scenario,
i.e., ρ = 48 : 1, DawnGuard still achieves an average F1 of

4472

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

TABLE IX
E VALUATION OF E FFICIENCY: T RAINING AND T ESTING T IME

TABLE X
E UCLIDEAN D ISTANCE B ETWEEN M ALWARE AND B ENIGN T RAFFIC
U NDER D IFFERENT R EPRESENTATIONS

F. Evaluation of Efficiency
We evaluate the time cost of all methods across training
and testing phases, as summarized in TABLE IX. The training
process comprises feature extraction time (FET), classifier
training time (CTT), and pre-training time (PTT) specifically
for meta-learning methods. Testing time represents the inference latency of the trained classifier. We set the sample size
for model retraining to 10.
As shown in TABLE IX, DawnGuard achieves a relatively short CTT and the second-shortest testing time. Since
FC-Net directly converts raw traffic into color images, it
achieves the shortest FET and testing time. However, this
simple representation lacks the expressiveness of our MGF.
While DawnGuard’s longer FET stems from computational
overheads in data augmentation and graph learning, these
modules are crucial for detection accuracy improvements
(Section VI-G).
G. Ablation Experiment

91.34%, which is 42.68% higher than the SOTA method in
this scenario, i.e., ST-Graph, demonstrating DawnGuard can
extract general features of malware traffic and remain resistant
in the high imbalance ratio. When the imbalance ratio enlarges,
FC-Net, CBSeq, and YaTC lose the ability to detect unseen
malware traffic, which achieves F1 of 17.08%, 18.18%, and
27.63%, respectively, when ρ = 48 : 1. This is because the
features extracted by these methods are not distinguishable
enough to detect unseen malware traffic, evidenced by quantitative analysis of feature representation in TABLE X.

E. Parameter Sensitivity Analysis
We further study the impact of different parameter values
on the performance of DawnGuard. We select six key parameters across different modules, including the hard threshold
coefficient γ, the peak density search upper bound β, the soft
threshold angle θ, the number of initial consecutive packets
M, the neighborhood sample max size n, and the dimension
of edge embeddings ω. We measure the F1 of DawnGuard in
D3 under different loading ratios (i.e., 20%, 30%, and 40%).
As shown in Fig. 8, itDawnGuard demonstrates strong
robustness to these parameters. For instance, the number
of initial packets M, which defines the input granularity
of single-flow features, shows minimal impact on the F1
within the range of [4, 8]. Specifically, at a 20% loading
ratio, the F1 only varies between 92.76% and 94.69% as
M changes. Similarly, the performance remains stable when
the edge embedding dimension ω varies from 128 to 1024,
and when the neighborhood sample size n ranges from 2 to
14. The high stability across these parameters, particularly
those governing the self-adjusting augmentation (i.e., γ, β, θ),
confirms that DawnGuard effectively captures the intrinsic
patterns of early-stage traffic through its design rather than
relying on an over-optimized parameter space. In conclusion,
the performance of DawnGuard is not sensitive to parameter
choices.

In this section, we evaluate the contribution of the main
modules of DawnGuard separately, illustrated in Fig. 9. We
conduct experiments with the loading ratio η = 30% and
the imbalance ratio ρ = 4 : 1 in D1 . We also evaluate the
effectiveness of MGF with quantitative measures.
1) Self-Adjusting Data Augmentation Module: To validate
our augmentation strategy, we first remove the module entirely.
This results in a significant performance degradation, with an
average drop of 22.33% in F1 and 5.33% in AUC. Furthermore, we evaluate an alternative strategy that applies a static
high weight to the first 30% of the traffic. While this simple
weighting improves the F1 to 82.95% from the non-augmented
baseline (74.11%), it remains 13.49% lower than DawnGuard.
This substantial gap demonstrates that the effectiveness of our
approach stems from generating diverse, structurally-aware
samples, rather than merely biasing the model’s attention
towards the beginning of the flow.
2) Multi-Flow Temporal Graph Learning Module: To justify our choice of temporal graph learning, we compare
DawnGuard against two categories of modeling paradigms:
static graph neural networks (GraphSAGE [36] and GAT
[37]) and fundamental Probabilistic Graphical Models (PGMs)
including Hidden Markov Model (HMM) [38], Bayesian
Networks [39], and Markov Random Field (MRF) [40].
The results clearly show the necessity of capturing temporal dynamics. Replacing Temporal GraphSAGE with static
GraphSAGE and GAT causes the F1 to drop to 87.46% and
58.60%, respectively. Furthermore, the PGM-based models
(HMM, Bayesian Networks, and MRF) exhibit limited effectiveness, achieving F1 of only 71.01%, 71.00%, and 74.92%.
This performance gap demonstrates that PGMs, limited by
structural assumptions and feature representation scalability,
cannot effectively model the temporal-topological correlations
that DawnGuard extracts.
3) Early-Stage Malware Detection Module: We select ViT
[32] as the backbone for its superior feature extraction capabilities. To validate this choice, we conduct experiments
by replacing ViT with other powerful architectures suitable for processing our 2 × 1216 MGF matrix: Transformer
[31], ResNet50, and LSTM. All three alternatives lead to a

JIA et al.: EARLY-STAGE DETECTION OF ENCRYPTED MALWARE TRAFFIC VIA TEMPORAL GRAPH LEARNING

4473

TABLE XI
C OMPARISON B ETWEEN DAWN G UARD AND THE SOTA BASELINE M ETHODS E VALUATED IN T HIS W ORK

notable performance decline. Specifically, their F1 decrease by
14.09%, 18.65%, and 21.01%, respectively, compared to the
ViT-based DawnGuard. This demonstrates that ViT’s global
self-attention mechanism is more effective at mining highlevel discriminative features from the MGF representations,
thus enhancing the overall detection performance.
4) Effectiveness of Feature Representation: To evaluate
the effectiveness of our multi-flow representation MGF, we
compare it against three flow-based baselines: Color Image
[15], ST-Graph [2], and MFR [16], excluding non-flow-based
methods [3], [13]. Using 3,000 samples per category from
D1 , we vectorize the initial 30% of each flow to compute
the Euclidean distance between benign and malware samples
(larger indicates better discriminability). The hyperparameters chosen for baselines are identical to those in [2], [15],
and [16].
As shown in TABLE X, MGF achieves the highest average distance across all malware categories. This quantitative
evidence confirms that MGF extracts more discriminative
features than existing representations, creating a feature space
where benign and malicious traffic are more separable thereby,
reducing the detection difficulty in early stages.
VII. R ELATED W ORK
Existing malware traffic detection methods can be broadly
categorized into rule-based, machine learning (ML)-based,
deep learning (DL)-based, and pre-training-based methods.
We summarize the multi-dimensional differences between
DawnGuard and the representative SOTA baseline methods
evaluated in this study in Table XI.
A. Rule- and ML-Based Methods
Traditional malware traffic detection methods often rely on
predefined rules. Bro [11] utilizes a layered architecture to
separate event engines from policy scripts for real-time detection. To handle encrypted traffic, ML-based methods focused
on extracting statistical features from specific protocols (e.g.,
TLS/DNS) [20] or leveraging graph models. For instance,
ST-Graph [2] constructs spatio-temporal graphs to analyze
full flows. Other methods leverage factor graphs to infer user
states [41]. Furthermore, to achieve detection without complete
traffic, researchers have explored side-channel features [42],
randomness tests [12], and transport-layer behaviors [43].
B. DL-Based Methods
To reduce reliance on expert knowledge, DL-based methods
have been proposed for automated feature extraction. GGFAST

[44] extracts characteristic sequences of message lengths to
achieve classification. Kitsune [13] uses autoencoders for
packet-level statistical feature analysis. To utilize multi-flow
features, CBSeq [3] employs Transformers to analyze behavior sequences from full channels. Other approaches include
attention-based certificate identification [45] and methods that
adopt the sequential nature of packets within isolated flows
for early detection [14].
C. Pre-Training-Based Methods
In recent years, pre-training frameworks have been introduced to malware traffic detection models. FC-Net [15]
leverages meta-learning for few-shot detection by representing
full flows as color images datasets. In another approach,
YaTC [16] utilizes masked autoencoders to learn high-level
representations from the first five packets.
D. Summary
In conclusion, the limitations of existing methods reflect
two fundamental challenges of NIDS [46], [47], [48]: 1)
Information sparsity in early-stage traffic. Most methods rely on intra-flow features within a flow and suffer
from a significant performance drop when only a small
fraction of traffic is available. 2) Heterogeneity of attack
patterns. Existing methods often treat flows in isolation,
failing to capture the features across contextual flows. DawnGuard addresses these gaps by integrating self-adjusting data
augmentation, which dynamically optimizes tail-masking to
focus the model on discriminative early-stage interaction
phases, with multi-flow temporal graph learning to extract
temporal-topological correlations for reliable detection with
early-stage traffic data.
VIII. C ONCLUSION
In this paper, we proposed DawnGuard, an effective
and reliable early-stage encrypted malware traffic detection
method. Specifically, DawnGuard utilized the temporal packet
density distribution of malware traffic to achieve self-adjusting
data augmentation and employed temporal graph learning
to extract temporal-topological correlations among multiple
flows, which formed MGF. By utilizing MGF, DawnGuard
constructed a ViT-based detector to capture both local and
global contextual relationships, thereby enabling early-stage
encrypted malware traffic detection. We conducted extensive
experiments to evaluate DawnGuard, and the results demonstrated that DawnGuard achieved effectiveness for early-stage

4474

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 21, 2026

encrypted malware traffic detection. In future work, we will
combine DawnGuard with unsupervised learning to improve
the performance of early-stage unknown encrypted malware
traffic detection. Furthermore, we plan to deploy DawnGuard in an edge gateway for analysis on large-scale ISP
traffic to further validate its robustness in high-throughput
environments.
R EFERENCES
[1]

E. Rescorla, SSL and TLS: Designing and Building Secure Systems,
vol. 1. Reading, MA, USA: Addison-Wesley, 2001.
[2] Z. Fu et al., “Encrypted malware traffic detection via graph-based
network analysis,” in Proc. 25th Int. Symp. Res. Attacks, Intrusions
Defenses, Oct. 2022, pp. 495–509.
[3] S. Cui, C. Dong, M. Shen, Y. Liu, B. Jiang, and Z. Lü, “CBSeq:
A channel-level behavior sequence for encrypted malware traffic
detection,” IEEE Trans. Inf. Forensics Secur., pp. 5011–5025, Aug.
2023.
[4] C. Fu, Q. Li, and K. Xu, “Detecting unknown encrypted malicious traffic
in real time via flow interaction graph analysis,” in Proc. Netw. Distrib.
Syst. Secur. Symp., 2023.
[5] M. Shen et al., “Machine learning-powered encrypted network traffic
analysis: A comprehensive survey,” IEEE Commun. Surveys Tuts.,
vol. 25, no. 1, pp. 791–824, 1st Quart., 2023.
[6] C. V. Wright, F. Monrose, G. M. Masson, and P. Chan, “On inferring
application protocol behaviors in encrypted network traffic,” JMLR,
vol. 7, pp. 2745–2769, Dec. 2006.
[7] M. Shen, J. Zhang, L. Zhu, K. Xu, and X. Du, “Accurate decentralized application identification via encrypted traffic analysis using
graph neural networks,” IEEE Trans. Inf. Forensics Security, vol. 16,
pp. 2367–2380, 2021.
[8] M. Shen, K. Ji, Z. Gao, Q. Li, L. Zhu, and K. Xu, “Subverting
website fingerprinting defenses with robust traffic representation,” in
Proc. USENIX Secur., Aug. 2023, pp. 607–624.
[9] M. Shen et al., “Swallow: A transfer-robust website fingerprinting attack
via consistent feature learning,” in Proc. ACM SIGSAC Conf. Comput.
Commun. Secur., Nov. 2025, pp. 1574–1588.
[10] (2024). WatchGuard’s Threat Lab Analyzes the Latest Malware and
Internet Attacks. [Online]. Available: https://www.watchguard.com/
wgrd-resource-center/security-report-q4-2024
[11] V. Paxson, “Bro: A system for detecting network intruders in real-time,”
Comput. Netw., vol. 31, nos. 23–24, pp. 2435–2463, Dec. 1999.
[12] W. Niu, Z. Zhuo, X. Zhang, X. Du, G. Yang, and M. Guizani,
“A heuristic statistical testing based approach for encrypted network traffic identification,” IEEE Trans. Veh. Technol., vol. 68, no. 4,
pp. 3843–3853, Apr. 2019.
[13] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “Kitsune: An
ensemble of autoencoders for online network intrusion detection,” in
Proc. Netw. Distrib. Syst. Secur. Symp., 2018.
[14] T. E. T. Djaidja, B. Brik, S. Mohammed Senouci, A. Boualouache,
and Y. Ghamri-Doudane, “Early network intrusion detection enabled by
attention mechanisms and RNNs,” IEEE Trans. Inf. Forensics Security,
vol. 19, pp. 7783–7793, 2024.
[15] C. Xu, J. Shen, and X. Du, “A method of few-shot network intrusion
detection based on meta-learning framework,” IEEE Trans. Inf. Forensics Security, vol. 15, pp. 3540–3552, 2020.
[16] R. Zhao et al., “A novel self-supervised framework based on masked
autoencoder for traffic classification,” IEEE/ACM TON, vol. 32, no. 3,
pp. 2012–2025, Jan. 2024.
[17] M. Shen, J. Wu, K. Ye, K. Xu, G. Xiong, and L. Zhu, “Robust detection
of malicious encrypted traffic via contrastive learning,” IEEE Trans. Inf.
Forensics Security, vol. 20, pp. 4228–4242, 2025.
[18] M. Cen, F. Jiang, X. Qin, Q. Jiang, and R. Doss, “Ransomware early
detection: A survey,” Comput. Netw., vol. 239, Feb. 2023, Art. no.
110138.
[19] Stratosphere.(2015). Stratosphere Laboratory Datasets. [Online]. Available: https://www.stratosphereips.org/datasets-overview
[20] B. Anderson and D. McGrew, “Identifying encrypted malware traffic
with contextual flow data,” in Proc. ACM Workshop Artif. Intell. Secur.,
Oct. 2016, pp. 35–46.
[21] G. Jacob, R. Hund, C. Kruegel, and T. Holz, “JACKSTRAWS: Picking
command and control connections from bot traffic,” in Proc. USENIX
Secur. 11, 2011, p. 29.
[22] F. Tegeler, X. Fu, G. Vigna, and C. Kruegel, “BotFinder: Finding bots in
network traffic without deep packet inspection,” in Proc. 8th Int. Conf.
Emerg. Netw. experiments Technol., Dec. 2012, pp. 349–360.

[23] X. Deng, Q. Li, and K. Xu, “Robust and reliable early-stage website fingerprinting attacks via spatial–temporal distribution analysis,”
in Proc. ACM SIGSAC Conf. Comput. Commun. Secur., Dec. 2024,
pp. 1997–2011.
[24] A. Alqahtani, M. Gazzan, and F. T. Sheldon, “A proposed
crypto-ransomware early detection(CRED) model using an integrated deep learning and vector space model approach,” in Proc.
10th Annu. Comput. Commun. Workshop Conf. (CCWC), Jan. 2020,
pp. 0275–0279.
[25] S. Rahmat, Q. Niyaz, A. Mathur, W. Sun, and A. Y. Javaid, “Network
traffic-based hybrid malware detection for smartphone and traditional networked systems,” in Proc. IEEE 10th Annu. Ubiquitous
Comput., Electron. Mobile Commun. Conf. (UEMCON), Oct. 2019,
pp. 0322–0328.
[26] M. Shen, Y. Liu, L. Zhu, X. Du, and J. Hu, “Fine-grained webpage
fingerprinting using only packet length information of encrypted traffic,”
IEEE Trans. Inf. Forensics Security, vol. 16, pp. 2046–2059, 2021.
[27] W. W. Lo, S. Layeghy, M. Sarhan, M. Gallagher, and M. Portmann, “EGraphSAGE: A graph neural network based intrusion detection system
for IoT,” in Proc. IEEE/IFIP Netw. Operations Manage. Symp., Apr.
2022, pp. 1–9.
[28] R. W. Schafer, “What is a Savitzky-Golay filter? [lecture notes],” IEEE
Signal Process. Mag., vol. 28, no. 4, pp. 111–117, Jul. 2011.
[29] D. Koukis, S. Antonatos, D. Antoniades, E. P. Markatos, and P. Trimintzios, “A generic anonymization framework for network traffic,” in
Proc. IEEE Int. Conf. Commun., Jun. 2006, pp. 2302–2309.
[30] D. Koller and N. Friedman, Probabilistic Graphical Models: Principles
and Techniques. Cambridge, MA, USA: MIT Press, 2009.
[31] A. Vaswani et al., “Attention is all you need,” in Proc. NIPS, 2017,
pp. 6000–6010.
[32] A. Dosovitskiy et al., “An image is worth 16×16 words: Transformers
for image recognition at scale,” in Proc. ICLR, 2020.
[33] R. Zamir, “A proof of the Fisher information inequality via a data
processing argument,” IEEE TIT, vol. 44, no. 3, pp. 1246–1250, May
1998.
[34] W. Gao, S. Kannan, S. Oh, and P. Viswanath, “Estimating mutual
information for discrete-continuous mixtures,” in Proc. Adv. Neural Inf.
Process. Syst., 2017, pp. 5988–5999.
[35] W. Wang, M. Zhu, X. Zeng, X. Ye, and Y. Sheng, “Malware traffic
classification using convolutional neural network for representation
learning,” in Proc. Int. Conf. Inf. Netw. (ICOIN), Da Nang, Vietnam,
Jan. 2017, pp. 712–717.
[36] W. L. Hamilton, R. Ying, and J. Leskovec, “Inductive representation
learning on large graphs,” in Proc. NIPS, vol. 30, 2017, pp. 1024–1034.
[37] P. Velickovic, G. Cucurull, A. Casanova, A. Romero, P. Lió, and
Y. Bengio, “Graph attention networks,” in Proc. ICLR, 2018.
[38] L. R. Rabiner and B. Juang, “An introduction to hidden Markov models,”
IEEE ASSP Mag., vol. ASSPM-3, no. 1, pp. 4–16, Jan. 1986.
[39] F. V. Jensen, “Bayesian networks,” Encyclopedia Statist. Quality Rel.,
vol. 1, no. 3, pp. 307–315, 2009.
[40] S. Z. Li, Markov Random Field Modeling in Image Analysis. Cham,
Switzerland: Springer, 2009.
[41] P. Cao, E. Badger, Z. Kalbarczyk, R. Iyer, and A. Slagell,
“Preemptive intrusion detection: Theoretical framework and real-world
measurements,” in Proc. Symp. Bootcamp Sci. Secur., Apr. 2015,
pp. 1–12.
[42] G. Stergiopoulos, A. Talavari, E. Bitsikas, and D. Gritzalis, “Automatic
detection of various malicious traffic using side channel features on TCP
packets,” in Proc. ESORICS, 2018, pp. 346–362.
[43] Z. Berkay Celik, R. J. Walls, P. McDaniel, and A. Swami, “Malware
traffic detection using tamper resistant features,” in Proc. MILCOM IEEE Mil. Commun. Conf., Oct. 2015, pp. 330–335.
[44] J. Piet, D. Nwoji, and V. Paxson, “GGFAST: Automating generation
of flexible network traffic classifiers,” in Proc. ACM SIGCOMM Conf.,
2023, pp. 850–866.
[45] I. Torroledo, L. D. Camacho, and A. C. Bahnsen, “Hunting malicious
TLS certificates with deep neural networks,” in Proc. 11th ACM
Workshop Artif. Intell. Secur. (CCS), S. Afroz, B. Biggio, Y. Elovici,
D. Freeman, and A. Shabtai, Eds., Toronto, ON, Canada: ACM, Oct.
2018, pp. 64–73.
[46] J. Sowa et al., “Post-quantum cryptography (PQC) network instrument:
Measuring PQC adoption rates and identifying migration pathways,”
in Proc. IEEE Int. Conf. Quantum Comput. Eng. (QCE), Sep. 2024,
pp. 1835–1846.
[47] R. Sommer and V. Paxson, “Outside the closed world: On using machine
learning for network intrusion detection,” in Proc. IEEE Symp. Secur.
Privacy, May 2010, pp. 305–316.
[48] L. Yang et al., “True attacks, attack attempts, or benign triggers? An
empirical measurement of network alerts in a security operations center,”
in Proc. USENIX Secur., 2024, pp. 1525–1542.
PAPER_TEXT
