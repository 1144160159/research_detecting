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
# [570] Unmasking the Internet: A Survey of Fine-Grained Network Traffic Analysis
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
编号：570
题名：Unmasking the Internet: A Survey of Fine-Grained Network Traffic Analysis
年份：2025
DOI：10.1109/comst.2025.3545541
来源：IEEE Communications Surveys & Tutorials
PDF：paper/10.1109_comst.2025.3545541.pdf
已有粗分类：数据集、基准、综述与开源工具
二级关联：网络流量监测、测量与工具
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\570.txt
- 原始字符数：274683
- 本次发送字符数：140043
- 是否截断：True

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

1

Unmasking the Internet: A Survey of
Fine-Grained Network Traffic Analysis
Yebo Feng, Jun Li, Jelena Mirkovic, Cong Wu, Chong Wang, Hao Ren, Jiahua Xu, and Yang Liu

Abstract—Fine-grained traffic analysis (FGTA), as an advanced form of traffic analysis (TA), aims to analyze network
traffic to deduce fine-grained information on or above the
application layer, such as application-layer activities, fine-grained
user behaviors, or message content, even in the presence of traffic
encryption or traffic obfuscation. Different from traditional TA,
FGTA approaches are usually based on complicated processing
pipelines or sophisticated data mining techniques such as deep
learning or high-dimensional clustering, enabling them to discover subtle differences between different network traffic groups.
Nowadays, with the increasingly complex Internet architecture,
the increasingly frequent transmission of user data, and the
widespread use of traffic encryption, FGTA is becoming an
essential tool for both network administrators and attackers to
gain different levels of visibility over the network. It plays a
critical role in intrusion and anomaly detection, quality of experience investigation, user activity inference, website fingerprinting,
location estimation, etc. To help scholars and developers research
and advance this technology, in this survey paper, we examine
the literature that deals with FGTA, investigating the frontier
developments in this domain. By comprehensively surveying
different approaches toward FGTA, we introduce their input
traffic data, elaborate on their operating principles by different
use cases, indicate their limitations and countermeasures, and
raise several promising future research avenues.
Index Terms—Network traffic, traffic analysis, traffic classification, traffic monitoring, fine-grained traffic analysis, intrusion
detection, user behavior identification.

I. I NTRODUCTION

I

N the context of Internet, protocols and applications are
usually built upon hierarchical models [1] (e.g., TCP/IP
and OSI), where the communication functions of a telecommunication or computing system are categorized into several
abstraction layers. Higher layers only encapsulate high-level
methods, protocols, and specifications, operating with the
support of lower layers [2]. With such design, programmers can easily develop interoperable Internet applications
regardless of diverse underlying protocols and technologies.
However, this convention also makes cross-layered network
analysis feasible. As developers of higher layer applications
Yebo Feng, Cong Wu, Chong Wang, Hao Ren, and Yang Liu are with
the College of Computing and Data Science (CCDS), Nanyang Technological
University, Singapore, 639798 (E-mail: {yebo.feng, cong.wu, chong.wang,
yangliu}@ntu.edu.sg and hao.ren@ieee.org).
Jun Li is with the Computer Science Department, University of Oregon,
Eugene, OR, 97403, USA (E-mail: lijun@cs.uoregon.edu).
Jelena Mirkovic is with the Information Sciences Institute, University of Southern California, Marina del Rey, CA, 90292, USA (E-mail:
mirkovic@isi.edu).
Jiahua Xu is with the Computer Science Department, University College
London, UK (Email: jiahua.xu@ucl.ac.uk).
Corresponding author: Hao Ren.

usually only take higher-layer measures (e.g., encryption,
anonymization, etc.) to preserve the user privacy regardless
of leaving traceable patterns on lower layers, analyzers can
capture network features from the lower layers to infer higherlayer knowledge in communication [3], even in the presence
of message encryption. Such a process is called traffic analysis
(TA), a technique widely used in today’s Internet.
TA has been studied for decades, with myriad systems,
tools, and algorithms [4]–[10] developed to serve different
types of purposes, such as traffic measurement, traffic engineering, anomaly detection, and network surveillance. In early
development of TA, traditional TA approaches were mainly
designed for basic network traffic measurement/forecast [11]–
[13], anomaly detection [14], and coarse-grained traffic classification [15]. These approaches are usually rule-based,
statistics-based, sketch-based [16], [17] or clustering-based,
can separate traffic of different network protocols or conduct basic modeling of traffic flow changes. Later, with the
advancement of the Internet and the growing complexity of
network traffic, a deeper level of network visibility became
necessary. For instance, application-layer visibility is crucial
for measuring application usage, conducting application security inspections, and monitoring fine-grained network events.
Similarly, visibility above the application layer is vital for
modeling user behavior, analyzing user experiences, and performing content analysis. As a result, researchers and developers are evolving traditional TA into the more sophisticated
fine-grained traffic analysis (FGTA), enabling the extraction
of more granular insights from network traffic data. In this
paper, we define FGTA as a type of advanced TA techniques
that focus on deducing information on or above the application
layer from network traffic data. These processes utilize only
link-layer or network-layer traffic data and are applicable
regardless of whether the traffic data is encrypted.
As a subset of TA, FGTA is mainly different from traditional
TA in the following ways:
• The most essential difference is the output of analysis.
Traditional TA can coarsely distinguish or model traffic from different types of protocols (e.g., HTTPS vs.
SMPT), communication methods (e.g., VPN vs. Tor), or
networking models (e.g., peer-to-peer vs client-server),
generating coarse-grained traffic statistics, traffic flow
models, or traffic classification results. However, FGTA
aims to analyze traffic at a finer granularity, providing
fine-grained analysis results on or above the application
layer, such as traffic from different application-layer activities (e.g., Twitter posting vs. Twitter reading), different
groups of application users (e.g., online social network

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

2

(OSN) bots vs. normal users), or different user content
(e.g., the visiting of a specific website).
• The analysis pipelines of traditional TA and FGTA are
often, but not always, distinct. FGTA, aiming at generating more granular information, usually have more
complicated and sophisticated analysis pipelines. For
example, some FGTA approaches takes traditional TA as
a prerequisite step to “preprocess” the traffic before the
final inference, such as a FGTA approach that tries to
identify the web page the user is visiting needs to first
leverage traditional TA to extract all the web browsing
traffic.
• As for analysis algorithms, compared to traditional TA
approaches, most FGTA approaches depend on more
sophisticated modeling, classification, or prediction methods, such as deep machine learning or high-dimensional
clustering, to tackle the challenging fine-grained analysis
tasks. On the other hand, traditional TA, dealing with
more straightforward tasks, can utilize a number of different analytical methods, such as rule-based, statisticsbased, or soft-computing-based approaches.
With the increasingly complex Internet architecture, increasingly frequent transmission of user data, and the widespread
use of traffic encryption [6], FGTA is becoming a more and
more important research topic. Compared with traditional TA,
FGTA can reveal more information from network traffic and
can achieve high efficacy even in various complicated network
environments [18]. Besides, as network traffic data become
more easily accessible than before, the applicable scenarios of
FGTA are more extensive compared with directly analyzing
traffic content. Furthermore, FGTA is efficient and portable in
discovering application-layer knowledge [19]–[21]. By analyzing a small amount of metadata or statistical information of
traffic, FGTA can obtain almost the same level of visibility as
decoding large amount of message content. Therefore, FGTA
has a wide range of usage scenarios. As for network managements, FGTA can help measure application usage [22], detect
complicated network intrusions or anomalies [23], investigate
edge user experience [24], etc. As for the attacker side, FGTA
can help eavesdrop on private information of users [25], model
user behaviors [26], estimate user locations [27], etc. Studying
FGTA is essential for comprehensive network inspection,
safeguarding information transmission, and precise network
configuration.
In this paper, we conduct a comprehensive examination
of over 300 pieces of literature related to FGTA. Our selection criteria encompassed sources from academic journals,
academic conference proceedings, workshop papers, industry
reports, preprint papers, etc. We prioritized academic publications that have made significant theoretical and practical
contributions to the field of FGTA, published in reputable
venues (e.g., ACM Computing Surveys, ACM CCS, Usenix
Security, NDSS, ACM IMC, etc.), or have been widely cited.
We search the literature from popular academic databases,
such as IEEE Xplore, ACM Digital Library, SpringerLink, ScienceDirect, etc., and search engines, such as Google Scholar,
Microsoft Academic, Google, etc. We employ a diverse set

I. Introduction

V. Use Cases and Representative Approaches

II. Related Work
Intrusion/anomaly detection

III. Traffic Input
Passive

Network

and active observation
TA

point

Quality of experience measurement

Traffic data acquiring
Packet-level
Flow-level

Traffic
capture

IV. Methodology
Pipeline

Feature extraction

Application identification

engines

Device identification
Location inference

Intrinsic feature
Derived feature

Application usage inference
Website fingerprinting

Classification and prediction approach

VI. Limitations
Traditional statistical approach

VII. Countermeasures

Rule-based approach
Probabilistic approach
Surprised machine learning

Network-layer countermeasures
Application-layer countermeasures

Unsupervised machine learning
Hybrid approach
Evaluation metrics

Classification efficacy
Efficiency
Other metrics

VIII. Future Research Direction
IX. Conclusion

Acronyms
Acknowledgements
References

Fig. 1: The paper organization and snapshots of proposed
taxonomies.

of keywords and keyword combinations to broadly identify
potentially relevant literature1 . Subsequently, we manually
review the content of these works to ensure their relevance to
FGTA. This survey primarily focuses on literature published
within the last two decades, specifically from 2004 to 2024.
This time frame was deliberately chosen to capture both the
foundational theories and the latest advancements in FGTA.
Our analysis of the literature is conducted in a two-stage
process: firstly, an initial review is conducted to assess the
relevance, quality, and alignment of the sources with the
objectives of our survey; secondly, we perform an in-depth
review of these sources to identify their key contributions,
methodologies, limitations, experimental setups, results, etc.
The methodology we adopted aims to strike a balance between
comprehensiveness and depth. By doing so, we ensure that
our survey not only covers the most pertinent literature in the
field of FGTA but also provides a thorough analysis of the
most significant contributions within this domain.
The rest of this paper is organized as follows. We first
introduce related work and compare existing surveys to our
work in Section II. We then discuss the input data of FGTA
(i.e., network traffic data) and its collection in real-world
environments in Section III. Next, in Section IV, we discuss
and summarize the methodologies of FGTA, including their
operating pipelines, feature extraction methods, classification
approaches, and evaluation metrics. Besides, we elaborate on
frontier developments of FGTA by their use cases in Section V.
We then point out the limitations of existing FGTA in Section VI and introduce the countermeasures in Section VII.
In addition, based on our observations and reflections on
1 The keywords include but are not limited to: fine-grained traffic analysis, fine-grained network traffic classification, traffic-based user behavior
inference, application-layer behavior modeling with network traffic, website
fingerprinting, user location estimation with network traffic, detailed network
traffic classification, etc.

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

3

TABLE I: Overview of related literature (#: not included; #
G: partially included;
Ref.

Year

Summary

Focus
General
TA

This paper

2025

[17]

2023

[28]

2023

[18]

2022

[29]

2022

[30]

2022

[6]

2021

[31]

2021

[32]

2020

[5]

2019

[33]

2018

[7]

2018

[34]

2016

[35]

2015

[36]

2014

[37]

2013

[38]

2009

[39]

2009

A survey of FGTA, which aims to analyze network traffic to
deduce information related to high-layer activities, fine-grained
user behaviors, or application-layer message content.
A survey of sketch-based traffic analysis using sliding windows,
including their fundamental principles, primary use cases, advantages, and limitations.
A review of the literature on network traffic prediction, including
experiments based on real data sets to compare the various
approaches directly in terms of fitting quality and computational
costs.
A recent survey on achievements in machine learning-powered
encrypted traffic analysis, including the workflow, feature extraction, and algorithms.
A survey that consists of an analysis of IoT traffic data acquisition
approaches, a classification of public datasets, a literature evaluation of IoT traffic processing, and a comparison of ML approaches
for IoT device classification.
A survey of deep neural network (DNN) architectures commonly
used in the traffic flow prediction literatures, categorizes and
describes the literatures themselves, and presents an overview of
the commonalities and differences among different works.
A survey of literature that deals with network traffic analysis
and inspection after the ascent of encryption in communication
channels.
An extensive analysis of the communications channels of 32 IoT
consumer devices, including traffic measurement and modelling.
A survey that looks at the emerging trends of network traffic
classification in IoT and the utilization of traffic classification in
its applications. It also compares the legacy of traffic classification
methods.
A survey that mainly focuses on approaches and technologies to
manage the big traffic data, additionally briefly discussing big data
analytics (e.g., machine learning) for the sake of TA.
A review of works that contributed to the network traffic analysis
targeting mobile devices, including a systematic classification of
such works according to their goal, traffic capture point, and
targeted platforms.
A systematic review based on the steps to achieve traffic classification by using machine learning techniques, including their
workflow, feature extraction, deployment, etc.
An examination of the literature on analyses of mobile traffic
collected by operators within their network infrastructure.
A survey of approaches for classification and analysis of encrypted
traffic, including widespread encryption protocols and payload and
feature-based classification approaches.
A survey in which a complete and thorough analysis of the
most important opensource deep packet inspection modules is
performed.
A survey of peer-to-peer traffic detection and classification, with
an extended review of the related literature.
A survey explains the main techniques and problems known in the
field of IP traffic analysis and focuses on application detection.
A report attempts to provide an overview of some of the widely
used network traffic models, highlighting the core features of the
model and traffic characteristics they capture best.

this field, we propose some avenues for future research in
Section VIII, thereby helping future academics and developers
to advance FGTA. In the end, we conclude this paper in
Section IX. To our best knowledge, this paper is the first
survey paper that focuses on FGTA and compares the stateof-the-art approaches in this field. Figure 1 illustrates the
organization of this survey paper and give snapshots of the
proposed taxonomies.

: included).
Subjects covered
FGTA

Traffic
capture

Countermeasure

FGTA

G
#

Sketch-based TA

G
#

#

G
#

#

Network traffic
prediction

G
#

#

G
#

#

Machinelearning-based
encrypted TA
Machinelearning-based
IoT TA

G
#

G
#

#
G

G
#

#

#
G

DNN-based traffic prediction

G
#

#

G
#

Encrypted TA

G
#

G
#

#

IoT TA

G
#

G
#

#
G

IoT TA

#
G

#

G
#

#
G

General TA

#

#

#

#

device

G
#

G
#

#
G

Machinelearning-based
TA
Mobile
device
TA
Encrypted TA

G
#

G
#

#

G
#

G
#
G
#

#

Payload-based
TA

G
#

#

G
#

#

P2P TA

G
#

#

#

#

G
#

#

#

Mobile
TA

General TA
General TA

G
#

#

#
#
#

#

#

II. R ELATED W ORK
In this section, we introduce related work on TA and
compare our paper with them. Table I summarizes the most
related and representative ones.
Our work differs from existing survey works regarding TA
in the following aspects:
•

we have a clear and focused survey topic: the whole paper
focuses on FGTA, which aims to analyze network traffic
to only deduce fine-grained outputs, such as information

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

4

related to high-layer application activities, fine-grained
user behaviors, or application-layer message content. Notably, no other related survey papers, including [17], [18],
and [29], have FGTA as their primary focus;
• to investigate FGTA comprehensively, our paper utilizes
multiple methodologies, including literature survey, summarization, and taxonomization, to cover different related
subjects, such as traffic capture, application identification, website fingerprinting, countermeasures, etc. Most
existing related survey papers only cover a subset of the
aforementioned topics;
• although studied for many years, TA is still iterating
rapidly and continuously, especially for FGTA. Compared
with other earlier literature, this paper sorts out and
examine the most recent development of FGTA at the
time of writing this paper.
In the early development of TA (i.e., before 2010), the
survey papers in this field mainly focus on coarse-grained
traditional TA [38]–[40], including protocol-level traffic classification, TA approaches based on deep packet inspection
(DPI), distinguishing server or peer-to-peer nodes from clients,
and coarse grained application identifications.
Later, due to increasingly diverse web-applications and
widespread use of traffic encryption, there is an increasing
need for more sophisticated TA approaches to monitor and
analyze the modern networks. Meanwhile, the evolution of
classification algorithms and easy access to big data also
effectively stimulate the development of TA. Therefore, survey
papers began to examine works that leverage big data [5],
machine learning [7], or efficient data structures [17] to tackle
TA.
On the other hand, the network is also becoming more and
more specialized, which has spawned many TA approaches
with specific design goals. To track such a trend, many of the
recent survey papers only investigate a certain type of TA approaches, such as TA for Internet of things (IoT) devices [31],
[32], encrypted TA [6], [18], TA for mobile devices [33], [34],
among others. Similar to these papers, our work focuses on a
new and specific topic—FGTA, which means our paper only
focus on the TA approaches that input conventional network
traffic data but generate fine-grained inference outputs (e.g.,
fine-grained user behaviors and application message content).
This direction has not been systematically studied before.
III. T RAFFIC I NPUT
Similar to traditional TA, FGTA approaches utilize the same
type of network traffic data from some vantage points in the
network as input to synthesize knowledge. Network traffic
data refers to the information exchanged between devices on
a computer network. Such data can be in diverse formats and
include a wide range of information, such as communication
logs, packet headers, and payload. The network traffic data is
the inference object for all TA approaches. In this section,
we introduce different types of traffic capture engines by
the way they collect network traffic data, compare different
types of network traffic data, and survey their usabilities. We
also introduce these traffic capture engines’ deployments and
application scenarios in FGTA.

A. Passive and Active TA
TA can be generally classified into passive and active
approaches based on the way they collect network traffic
data [41], [42].
Passive TA approaches involves monitoring and analyzing
network traffic without altering or injecting any data into
the network [42], [43]. It relies solely on the observation of
existing traffic flows. Typically, passive TA approaches consist
of capturing packets, logging traffic patterns, and analyzing
these logs to infer information. Such approach offer several
advantages. First of all, passive TA approaches are nonintrusive. Since they do not interfere with the network, they
are less likely to be detected by users or security mechanisms.
Furthermore, passive TA approaches do not add additional
load to the network, making them suitable for continuous
monitoring. However, passive TA approaches may not capture
all relevant information, particularly in cases of encrypted
or obfuscated traffic. Additionally, as they rely on existing
traffic flows, passive TA approaches cannot proactively test or
measure specific aspects of network performance or behavior,
making them inherently reactive.
Active TA approaches involve actively injecting data into the
network to provoke responses, which are then analyzed to gain
insights into the network’s behavior and performance [44],
[45]. Active TA approaches may include techniques such as
sending probe packets [46], watermarking existing traffic [47]–
[49], performing packet timing analysis, or conducting specific
tests to measure latency, throughput, and other metrics. Compare to passive TA approaches, active TA approaches offer several advantages. First, active TA approaches can provide more
detailed and precise information, especially about specific
network conditions and device status. Besides, By generating
traffic, active TA approaches can test scenarios and conditions
that may not naturally occur, allowing for more thorough
analysis. However, the act of injecting traffic can be detected
by network users and security mechanisms, potentially leading
to countermeasures [50]. Active TA approaches also add additional load to the network, which can affect performance and
may not be suitable for continuous monitoring. Furthermore,
active TA approaches require additional network infrastructure
and resources to operate, such as a traffic encoder to inject or
watermark traffic flows and a traffic decoder to identify marked
traffic flows. This makes active TA approaches less applicable
in real-world scenarios.
In the context of FGTA, passive TA approaches are more
commonly used due to their non-intrusive nature, ability to
continuously delve into network traffic data, and their focus
on user-behavior-centric analysis models. In contrast, active
TA approaches are rarely employed in FGTA as they are
designed for measuring specific network conditions, endpoint
device status, or the accessibility of network services, and
focus less on undisturbed user behavior, which is the core of
FGTA. Therefore, throughout this paper, we primarily focus on
passive TA approaches. In this section, we specifically discuss
the network traffic input by passive TA approaches rather than
active TA approaches.

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

5

Observation Point

...
Observation
Point

...

(a) The observation point is the
gateway of the network. The
traffic capture engine can collect
bidirectional traffic data.

...

(b) The observation point is in
the network. The captured traffic
can be asymmetric.

Fig. 2: Network visibility with different observation locations.
B. Network Observation Point
The observation point of the traffic capture engine will
significantly impact the integrity of the captured data and the
network visibility. Different observation points are suitable for
different types of TA tasks.
The optimal observation point for most FGTA tasks is at
the network gateway (as shown in Figure 2a), as it provides
full visibility into communication sessions between two nodes.
The gateway allows for the capture of complete inbound
and outbound traffic, which is essential for FGTA. Although
such a bidirectional traffic dataset is suitable to infer the
interactions between the observed network and rest of the
Internet, analyzers cannot learn about the traffic in the rest
of the Internet according to this dataset.
Sometimes, the observation point can be in the middle of the
network (illustrated in Figure 2b), especially when the traffic
capture engine is deployed by an ISP or IXP. In this case, the
capture engine is able to collect a large amount of traffic that
pass by it. However, it also raises the following concerns:
• Due to asymmetric packet routing [51], in-network observation point sometime may only capture traffic in one
direction (illustrated in Figure 2b).
• It cannot guarantee the integrity of captured traffic for a
long period because of the deployment of various traffic
engineering techniques [52], [53]. The routing path for
any packet can be dynamic in today’s networks.
Therefore, in-network observation points may be more suitable
for traditional TA tasks such as Internet measurement and
network-layer anomaly detection. As for FGTA, many approaches (e.g., user behavior inference, website fingerprinting)
prefer to use the gateway-based observation point to capture
more complete traffic data from endpoints. However, wherever
the observation point is located, it is difficult to capture all the
relevant traffic in the network.
To capture comprehensive traffic data from the network with
complex topology, we can deploy multiple observation points
at different vantage points if conditions permit. By using a pool
of metering processes to collect network packets at multiple
observation points, optionally filter them and aggregate information about these packets, a traffic exporter can gather each
of the observation points together into an observation domain
and sends this information to a traffic capture engine [54].
Then we can obtain relatively comprehensive network traffic data without redundancy. Another benefit of deploying

multiple observation points is that it allows distributed or
cooperative TA, where multiple analyzers can collaborate
to analyze traffic data and synthesize more comprehensive
knowledge [55]–[57]. For example, analyzers can choose to
upload only extracted features or intermediate results to a
central server to reduce the burden of data transmission or
enhance the privacy of the data [58]; researchers can also
leverage federated learning techniques to train a global model
without sharing sensitive traffic data [59]–[62]. However, these
approaches are costly to implement and often impractical
due to real-world constraints, making them seldom used in
practice, particularly in the context of FGTA.
C. Traffic Data Acquiring
Since the birth of the Internet, various traffic capture engines
have been developed to log traffic information. TA approaches
can further leverage these “log information” to measure network events, detect anomalies, and analyze network behaviors.
Based on different information captured, these traffic capture
engines can be classified into either packet-level or flowlevel [4].
1) Packet-level capture: Packet-level capture is widely used
in local networks and endpoint devices. As its name states, it
copies or makes a snapshot of all the network packets that pass
by the network interface and forwards the collected data to a
collector. The agent that takes charge of the capture is called a
packet-level traffic capture engine or a “sniffer”, which can be
either software-based (e.g., Snoop [63], Wireshark [64], etc.)
or hardware-based (e.g., Sniffer InfiniStream [65]). It can be
as simple as an IP table rule on a route that copies all the
traffic to a cloud disk besides normal forwarding.
Packet-level capture can collect raw network traffic, containing both packet headers and packet payloads. Theoretically,
it can support all types of FGTA tasks by logging all the
information flowing through the network, making it an ideal
input source for FGTA. However, in most cases, packet-level
traffic capture might not be the right solution to deploy for the
following reasons:
• Packet-level traffic capture is expensive, not only because
the interface needs to copy all the packets that pass by
it, but also because the interface needs to forward all
the captured traffic to an analysis node through a link.
All these operations will double the workload of the
network interface and occupy a considerable amount of
link bandwidth. Packet-level traffic capture is therefore
not scalable.
• The information contained in packet-level traffic data
is sometimes an “overkill” for TA, as many TA approaches only require statistical information from the
packet headers to complete the analysis. Moreover, user
messages, website content, and video streaming are usually contained in packet payloads in encrypted forms,
making most information captured in packet-level traffic
meaningless for all TA approaches.
• Packet-level traffic may contain sensitive information
(i.e., payload) of users. Thus, network service providers
are cautious about capturing and analyzing such data.

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

6

Workflow without traffic capture engines
Forward/
Drop

Ingress Port

Forward

Traffic
Forwarding

All Packets

Forward

Sample?
Copy of Packet Headers

Header Information
Processing and
Flow Cache Updating

New or
Existing
Flow?

New

Ingress Port

Workflow with
Cflowd as the
traffic capture
engine

Add Entry

Existing

Update Entry

Flow Cache

Collector Port

Fig. 3: Workflow of a network interface when Cflowd serves
as the traffic captured engine.

2) Flow-level capture: To address the aforementioned issues of packet-level traffic captures and make traffic capturing affordable, scalable, and practical for network service
providers, researchers and developers have proposed myriad
flow-level traffic capture engines.
In flow-level traffic capture systems, the capture engines
no longer copy or make snapshots of each packet, instead,
they first aggregate relevant packets into a flow and then
capture metadata or statistical information to represent that
flow. Here, the concept of flow has been around for a long
time. Typically, a flow can be identified by either a 5-tuple
(i.e., source IP address, source TCP/UDP port, destination
IP address, destination TCP/UDP port, and IP protocol) or a
3-tuple (i.e., source IP address, destination IP address, and
IP protocol) [66]. However, with the development of flow
capture engines, researchers have proposed many other formal
and informal definitions of network traffic flows (e.g., RFC
2722 [67], RFC 3697 [68], RFC 3917 [69], etc.). In this paper,
we define a network traffic flow as a sequence of relevant
network packets from a source to a destination for the same
application. In most instances, the network system will process
packets within a flow in the same manner. Besides, each
application-layer behavior will generate one or multiple flows
in both directions.
By capturing traffic at flow-level, traffic capture engines no
longer suffer from high system overhead and high bandwidth
usage. Figure 3 illustrates the workflows of a network interface
with and without Cflowd as the flow-level traffic captured
engine [70]. Unlike packet-level traffic capture that will copy
and forward any packet entirely to the collector port, flowlevel traffic capture only copies information from headers to
assemble traffic flows. The volume of data to process is then
largely reduced in such a procedure. According to existing
literature [71], NetFlow, the most frequently used flow-level
traffic capture engine, only creates 1-1.5% of throughput
(without sampling) on the interface it is exported on [72].
With a great deal of data reduction, network administrators can
store, process, inspect and analyze large amounts of network
data efficiently. Furthermore, when combining this procedure

with packet sampling, it becomes feasible to capture and store
traffic flows at an ISP or IXP scale, thereby extending the
usage scenarios of TA. As we can see from a study, NetFlow
only occupies around 15% of the router/switch’s CPU load
when capturing sampled network traffic [73]. Compared with
packet-level traffic capture that sometimes may double the
system overhead and link usage, flow-level traffic capture is a
huge improvement regarding efficiency and deployability.
However, flow-level traffic capture has a notable
drawback—it reduces the visibility of network traffic
by providing only metadata and aggregated statistical
information rather than details of individual packets. This
limitation is particularly problematic for FGTA, as many
approaches rely on inter-packet information, such as packet
interval times. To address this issue, the lifecycle of each
flow in traffic capture engines can be shortened, allowing
flows to be generated more frequently and thereby improving
network visibility.
D. Widely used traffic capture engines
Here, we introduce widely-used traffic capture engines in
academia and industry (Table II shows comparisons of them).
1) Packet-level traffic capture engines: Back in the early
days of Internet, developers had realized the importance of
capturing network packets for troubleshooting. Thus, Tcpdump [80], a software-based packet-level traffic capture engine
(sniffer), was proposed in 1988. It allows users to store and
display TCP/IP and other packets being transmitted or received
over a network. Nowadays, Tcpdump has been ported to
several operating systems (e.g., Unix with libpcap library,
Windows with WinPcap) and is still frequently used in network
studies. Similar software-based sniffers were also proposed
to meet different needs. For example, Snoop [63], a simple
packet capture tool that is bundled on Solaris operating system;
Wireshark [64], a free packet capture and analysis software
that not only supports multiple operating systems (e.g., Linux,
Solaris, Windows, FreeBSD, Mac OS, etc.), but also comes
with a user-friendly interface; PF RING [81], a high speed
packet capture library that can turn a commodity PC into an
efficient and cheap network measurement box suitable for both
packet capture and TA. As for routers and switches, traffic
mirroring [83]–[85] is also well-studied, with many software
or hardware-based approaches [65], [86] proposed to support
real-time packet capture for enterprise-level networks.
However, as capturing the entire packet is expensive and
sometimes impractical, people began to make a snapshot of
each packet rather than storing it entirely. The most frequentlyused approach is sFlow [79], an industrial method (defined in
RFC 3176 [79]) originally developed by InMon Inc., to capture
packet-level snapshot from switches and routers. Compared
to previous packet-level traffic capture engines, sFlow offers
several features that make it an ideal input for most FGTA
approaches:
• Without capturing the entire packet, sFlow can just copy
the first N bytes of a packet to save computing and
transmission resource. This is especially useful for TA
tasks as packet payloads are useless in such scenarios

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

7

TABLE II: Comparisons of selected widely-used traffic capture engines ( : fully supported; #
G: partially supported; #: not
supported.).
Traffic
Capture
Engine

Data Captured

Granularity

SNMP [74]

High-level statistical information about the interface.

IPFIX [75]
NetFlow v9 [76]
NetFlow v5 [77]
Argus [78]

Metadata and statistical information about the flow.
Metadata and statistical information about the flow.
Metadata and statistical information about the flow.
Metadata and statistical information about the flow.

Flow-level
(aggregated)
Flow-level
Flow-level
Flow-level
Flow-level

Complete packet headers and partial packet payloads.

Packet-level

Network information passing through the observation point.
Network information passing through the observation point.
Network information passing through the observation point.
Network information in the memory of the observation point.

Packet-level
Packet-level
Packet-level
Packet-level

sFlow [79]
Tcpdump [80]
Wireshark [64]
PF RING [81]
Netmap [82]

but the entire packet headers are still preserved for finegrained analysis.
• As an industrial standard, sFlow is compatible on many
different platforms of network switches and routers and
utilizes a dedicated chip built into the devices to operate,
which removes the burden of the CPU and memory of
the router or switch when capturing the traffic.
• By introducing time-based or packet-based sampling
techniques, sFlow can capture traffic on all interfaces
simultaneously at wire speed.
Therefore, sFlow can reach a good balance between data
integrity and velocity for FGTA—being able to capture all
the packet headers and simultaneously create less burden on
the router or switch.
2) Flow-level traffic capture engines: Flow-level traffic
capture engines also have a long history. Back in 1984,
the Audit Record Generation and Utilization System (Argus
flow [78]) was proposed as the first implementation of network
flow monitoring, and is still an ongoing open source network
flow monitor project now. Argus can monitor all network traffic, including Internet Protocol (IP) traffic, data plane, control
plane and management plane. It captures much of the packet
dynamics and semantics in each flow, providing reachability,
availability, connectivity, duration, rate, load, delay metrics
for all network flows. It also captures most attributes that are
available from the packet headers [87]. Later, in 1988, Simple
Network Management Protocol (SNMP) [74] was proposed as
a component of the Internet Protocol Suite as defined by the
Internet Engineering Task Force (IETF). Unlike Argus flow
that provides rich information about ongoing traffic, SNMP
only provides statistical information per interface, such as link
utilization, interface bandwidth, and some other information
if the device provides. SNMP is thus less applicable in TA
compared with Argus, especially in the domain of FGTA.
With rapid development and popularization of the Internet,
the industry had realized the importance of flow-level traffic
capture engine and many solutions were proposed. The most
typical example is NetFlow [76], so far the most widelyused flow-level capture engine with many TA approaches
built upon. Just like Argus, NetFlow uses a flow record to
represent a set of packets. However, unlike Argus, which is a

Open
or
Proprietary

Layer
(OSI)

Hardware
Acceleration

Sampling

Open

2, 3

Open
Proprietary
Proprietary
Open
Partially
Open
Open
Open
Open
Open

3, 4
3, 4
3, 4
2, 3, 4

#

#

#

2-7
2-7
2-7
2-7
2-7

#
#

#
#
#
G
#
G

bidirectional monitoring approach, NetFlow is a unidirectional
flow monitor, reporting flow information of each direction
of conversations independently. This feature allows NetFlow
to have a finer granularity than Argus. Since NetFlow was
developed by Cisco, it is bundled with most Cisco routers
and switches, making it the object of imitation of the entire
industry. Following NetFlow, many similar systems were proposed by both research institutions and commercial companies,
such as Cflowd [70], J-Flow [88], NetStream [89], Remote
Network Monitoring (RMON) [90], etc. NetFlow itself also
has evolved into different variations. The most famous one is
Internet Protocol Flow Information Export (IPFIX) [75], an
IETF protocol built upon NetFlow v9.
The most recent development of traffic capture and traffic
handling have been mainly focusing on the velocity issue.
Researchers have proposed multiple approaches to capture
large volume of network traffic at line speed without having
any effect on data plane. For example, Netmap [82] a memorybased framework that enables commodity operating systems
to handle millions of packets per seconds without the support
of custom hardware; eXpress Data Path (XDP) [91], a fast
programmable packet processing approach based on the operating system kernel, supports high speed packet logging and
processing; hXDP [92], an efficient software network packet
processing approach written in extended Berkeley Packet
Filter (eBPF) on Field Programmable Gate Arrays (FPGA)
network interface controllers (NICs); NetSeer [93], a flow
event telemetry (FET) monitor, which aims to discover and
record all performance-critical events on the programmable
data plane. However, these approaches do not alter the FGTA
pipeline; they simply enhance the speed of infrastructure for
capturing and processing network traffic, without modifying
the captured data itself.
IV. M ETHODOLOGY
In this section, we delve into the methodology of FGTA
and explore this field from the perspectives of data processing
pipelines, feature extraction approaches, classification & prediction approaches, and evaluation metrics. These components
are integral to the success of FGTA and play crucial roles in
achieving accurate results.

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

8

Traffic collection

Preprocessing

Feature Extraction
Training
Future steps
(e.g., access
control)

Inference
(e.g., classification)

Fig. 4: The most widely-used processing pipeline for FGTA,
which consists of three key steps: preprocessing, feature
extraction, and classification.
Traffic collection
Traffic matching
Future steps
(e.g., access
control)

FGTA
Rules

Fig. 5: Example of a simplified FGTA data processing pipeline,
which is used when the target traffic pattern is distinct or welldefined.

A. Pipeline
The process of generating fine-grained analysis results from
raw network traffic collected from network infrastructures typically involves several necessary steps. These data processing
procedures are known as the FGTA pipeline. Different FGTA
approaches may have different pipelines, with different steps
and different orders. In this subsection, we discuss three types
of FGTA pipelines (illustrated in Figure 5, 4, and 6).
Figure 4 depicts a commonly adopted pipeline for FGTA.
This pipeline is also prevalent in traditional TA methodologies as it offers a complete and versatile framework for the
processing of network traffic data. Regardless of whether the
input traffic is in flow-level or packet-level format, it usually
cannot be directly processed by analysis algorithms. Therefore,
similar to traditional TA pipeline, the first step of this FGTA
pipeline is usually to preprocess the raw traffic data. The
preprocessing step typically involves the following tasks:
• Data decoding: the raw network traffic data is usually
encoded in a format that is not easily processable (e.g.,
binary format or encrypted form). This task converts the
raw traffic data into a readable and processable form.
• Data cleaning: the raw traffic data may contain some
noise, invalid data, or control messages. This task extracts
only the valuable data for further analysis.
• Data refactoring: this task refactors the raw network
traffic data and make it suitable for the subsequent
analysis or maintenance. For example, indexing the raw
traffic data by socket pairs, or converting the flow records
to a B tree structure [94].
• Other tasks necessary for subsequent steps: depending
on different FGTA pipelines, there may be other tasks
necessary for subsequent steps. For example, extracting
marked packets from the raw traffic data, anonymizing the
raw traffic data for General Data Protection Regulation

(GDPR) compliance [95], or compressing the data for
efficient storage.
After the preprocessing step, FGTA approaches usually
move to feature extraction, which refers to the process of
selecting and transforming raw network traffic data into a set
of relevant features that are suitable for machine learning,
inference, or other analysis steps. For both traditional TA
and FGTA approaches, the feature extraction is a particularly
important step for representing the ongoing network events and
achieving accurate results. However, compared with traditional
TA approaches, FGTA approaches may require more sophisticated feature extraction steps as they often need to extract
more detailed information from the raw traffic data. We further
discuss more details about feature extraction in Section IV-B.
After relevant features are extracted, FGTA approaches are
typically ready for inference. The inference goals of these
approaches can vary, including identifying specific network
events, classifying traffic flows based on different application
behaviors, detecting network anomalies, or predicting specific
future network traffic. We further discuss the use cases of
FGTA approaches in Section V. The inference results of FGTA
approaches can be used for a variety of purposes, including
network monitoring, access control, device management, data
center protection, etc. However, regardless of the inference
goal, the inference step of FGTA always operates in the
form of fine-grained classification or prediction. For example,
classifying outlier traffic flows from normal traffic flows (i.e.,
anomaly detection), or classifying traffic flows according to
different applications (i.e., application identification). Therefore, we use the term classification and prediction to refer to
the inference step of FGTA approaches. Compared traditional
TA approaches, FGTA approaches may require more sophisticated classification and prediction approaches as they often
need to classify or predict more detailed information from
extracted features. These advancements may include more
sophisticated machine learning algorithms, more sophisticated
statistical modeling, or more complicated rule-based matching. Section IV-C discusses the classification and prediction
approaches used in FGTA.
The previously mentioned pipeline outlines the general steps
for FGTA approaches. However, depending on the specific
goals, system design, and operational environments, the FGTA
pipeline can be simplified or extended, with specific steps
omitted or added.
Figure 5 illustrates a simplified FGTA pipeline, where the
raw network traffic data is directly used for rule-based traffic
pattern matching. A short data processing pipeline is very
efficient to operate and can still generate accurate results if the
pre-defined matching rules are simple and effective. It is useful
when target traffic pattern is distinct or well-defined (i.e.,
location inference [27]). This simplified pipeline is widelyused in traditional TA approaches due to the simplicity of the
target traffic pattern. For example, sketch-based approaches
utilize probabilistic data structures (e.g., hash-based methods)
to directly match and measure incoming traffic’s statistics with
low overheads and high throughput [96]–[101]. However, these
approaches can only coarsely distinguish or measure traffic
from different types of devices, protocols, or distinguishable

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

9

Flow record
Traffic collection

Derived flow point

Preprocessing

Input flow
records

Classification 1

Flow points
from flow
records

Session assembly
Visualization
Feature extraction

Session 1

Training
Future steps
(e.g., access
control)

Classification 2

Fig. 6: Example of a more complicated FGTA data processing
pipeline, which is used when the target traffic pattern is not
directly distinguishable.

applications, serving as a tool for large-scale network measurement or a prerequisite step for more sophisticated FGTA approaches. To generate fine-grained, application-layer inference
results, such a simplified pipeline is inadequate. Additional
data processing steps are needed to more thoroughly analyze
the traffic data for digging the hidden fine-grained information.
To infer high-level, fine-grained information from contentagnostic network traffic data, many FGTA approaches tend to
employ more complicated pipelines to mine hidden and hardto-dig knowledge. These complicated pipelines are not widely
seen in traditional TA approaches due to the simplicity of
the target traffic pattern and added computational complexity.
Figure 6 illustrates such an example. Many application usage
inference approaches apply similar pipelines [26], [102], [103]
because they need to extract features and classify traffic for
multiple times at different phases to derive detailed user
behavior information of specific applications. The sample
pipeline include two different analysis phases, with one for
narrowing down the analysis scope and the other for generating
fine-grained analysis results. More importantly, this pipeline
re-assemble traffic flows into sessions (some papers may call
them transactions [21] or bursts [22], [104]) before extracting
features for the final classification. This step is very helpful for
digging fine-grained behavior information from the traffic data
because the target network behavior or event usually consist of
multiple packets or traffic flows. Simply analyzing the network
traffic flow by flow or packet by packet may not be able
to capture the whole picture of the ongoing network events.
Therefore, session assembly is used to aggregate adjacent,
relevant, or similar traffic data into an analysis unit, which
is a more representative data structure to present the ongoing
network events and makes it easier for FGTA approaches
to infer fine-grained application-layer information. Figure 7
illustrates an example of session assembly [103], where flow
records are divided into flow points and then aggregated into
sessions according to the traffic density. Based on current
literature, the following approaches are commonly used for
session assembly:
• Time-based session assembly: this approach aggregates

Session 2

Aggregated
sessions

time

Fig. 7: Example of a session assembly procedure, where
relevant flow records are aggregated into a traffic session to
represent a network event.
traffic flows into sessions based on the timing or the
intervals of ongoing network traffic.
• Clustering-based session assembly: this approach utilize clustering algorithms to group traffic flows into
sessions.
• Index-based session assembly: this approach aggregates
traffic flows into sessions by specific indexes (e.g., socket
pair, packet ID ranges, time to live (TTL), etc).
• Rule-based session assembly: this approach aggregates
traffic flows based on pre-defined rules (e.g., rules on the
hash value of packet payload, rules on TCP flags, etc.).
The session assembly step is rare in traditional TA approaches.
After sessions are assembled, representative features can be
properly extracted and forwarded to next steps for fine-grained
classifications or predictions.
B. Feature extraction
Feature extraction is a term refers to the process of selecting
and generating relevant features from the raw data in order to
create a representation that can be used for machine learning,
statistical modeling, or other analysis procedures [105]. It is
an essential step for both traditional TA approaches and FGTA
approaches. In the context of TA, feature extraction involves
inspecting network traffic data to identify relevant features
that can be used for the corresponding classification tasks.
This process typically involves techniques such as packet
inspection, data fusion, and statistical modeling to identify
and derive patterns or characteristics in the data that are
relevant to the specific inference goal. Recently, the rise of
deep learning techniques has enabled numerous approaches
to automatically extract or select features from preprocessed
data inputs or extensive feature sets [106]–[108]. However,
considerations of efficiency, efficacy, explainability, and the
complexity of network traffic data mean that many FGTA
approaches continue to depend on meticulously crafted feature extraction techniques to generate features for subsequent
analytical steps. The resulting set of features will be used as

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

10

TABLE III: Examples for intrinsic and derived features for
FGTA.
Category
Intrinsic
feature

Derived
feature

Example
Flow-level

Packet-level

Flow size, number of packets,
AS number, protocol type,
flow duration, etc.

TCP flag, ToS, packet size,
packet interval,
first n bytes of the payload, etc.

Flow/packet-based

Session-based

Interval deviation, size deviation,
interval distribution,
inbound/outbound packet ratio,
packet similarity, etc.

Session duration,
density distribution, session image,
normalized session vector,
round-way communication number,
etc.

input to the classification or prediction models to generate
the analysis output. In contrast to traditional TA methods,
FGTA often necessitates more advanced and intricate feature
extraction techniques. This is because FGTA aims to deduce
detailed application-layer information from raw traffic data,
requiring a more insightful and informative representation of
the network traffic data.
Due to the nature of network traffic collection, all the
extracted features can be categorized into two types: intrinsic
features and derived features. Intrinsic features are directly
contained in the raw network traffic data, such as packet
length, packet header fields, etc. The process of fetching intrinsic features is simple and straightforward. The analysis system
can directly select, slice, or generate intrinsic features from the
raw data, requiring little to no additional processing. On the
other hand, derived features are not directly contained in the
raw network traffic data. They are generated by applying some
data processing techniques to the raw data, such as statistical
modeling, feature transformation, information assembly, data
fusion, etc. Typically, traditional TA methods more commonly
utilize intrinsic features, while FGTA approaches tend to rely
on derived features. This preference is attributed to their
differing analysis objectives, granularity, and efficiency goals.
Table III lists some typical examples of intrinsic and derived
features. Different features are suitable for different FGTA
tasks. Typically, some relatively easy FGTA tasks may only
require intrinsic features to operate. For example, some application identification or anomaly detection approaches can generate accurate results by directly inputting intrinsic features.
Because the network traffic of such applications or anomalies
can already be distinguishable by intrinsic features [20], [109],
[110]. However, some more complex FGTA tasks may require
derived features for finer granularity analysis, especially for
tasks that infer detailed, application-layer user behaviors [22],
[103], [111]. The target network traffic of these FGTA tasks
is less distinguishable and may only show obvious patterns
with sophisticated feature engineering techniques. We discuss
more details about suitable features for different FGTA tasks
in Section V.
Although derived features are more powerful than intrinsic
features in mining fine-grained information from network
traffic data, they are also more complex and expensive to
generate. One may need to apply sophisticated data processing
techniques, such as traffic buffering, data fusion, session

assembly, statistical modeling, etc., to fetch these derived
features. Such processes are time-consuming and may require
significant computational resources. As time-sensitive tasks,
it is vital for FGTA procedures to be efficient and scalable,
thereby outputting analysis results in a timely manner. Thus,
carefully selecting and generating necessary features is a
critical step for all FGTA approaches.
C. Classification and prediction approach
The key step of FGTA is to classify the target network traffic
from others or to predict the target network traffic’s behavior.
Designing a proper classification or prediction approach determines the efficacy and performance of FGTA approaches. In
many cases, constructing a classification or prediction model
requires labeled data. In the context of FGTA, labeled data
refers to network traffic data that has been manually labeled
or annotated with ground truth information. This ground truth
information typically includes information such as the application type, user behavior type, or whether the traffic is generated
by malicious behavior or not. Obtaining labeled data can
be a challenging and resource-intensive process. It typically
requires a significant amount of manual effort and expertise to
accurately label network traffic data. Researchers may be able
to automate the labeling process with the help of other stateof-the-art classification approaches, but the accuracy of labels
may not be ideal [112]. On the other hand, some classification
and prediction approaches can be trained without labeled data
or with other forms of prior knowledge. In the remaining of
this subsection, we discuss the classification and prediction
approaches that are commonly used in FGTA approaches
(summarized in Table IV).
1) Traditional statistical approach: Traditional statistical
approaches leverage statistical properties, statistical models or
some other mathematical methods to identify subtle differences or patterns in different groups of network traffic [123].
Typical examples of statistical approaches include distribution
fitting [113], logistic regression [114], linear regression [23],
etc. Traditional statistical approaches are widely used in
traditional TA tasks because they are explainable, easy to
implement, usually efficient to operate, and good at tackling
relatively easy tasks. However, as FGTA tasks becoming more
and more challenging, traditional statistical approaches are not
sufficient to identify subtle differences in network traffic. Thus,
traditional statistical approaches are gradually replaced by
more sophisticated classification approaches, such as machine
learning approaches. Still, traditional statistical approaches
are commonly used in feature extraction, pre-analysis, and
pre-classification. For example, many FGTA approaches use
traditional statistical approaches to narrow down the analysis
scope before fine-grained analysis, thereby reducing the computational complexity of the subsequent procedures [113].
2) Rule-based approach: Rule-based approaches are based
on a set of pre-defined rules that are manually designed by
experts to locate the target network traffic group [124]. Before
defining the classification rules, the experts usually need a
thorough understanding of the target network traffic and the
network environment. Typical examples of classification rules

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

11

TABLE IV: Summary of widely-used classification and prediction approaches in FGTA.
Category

Representative
algorithms/approaches

Description

Pros

Cons

Use in FGTA

Reference

Traditional
statistical
approach

Leverage statistical properties
or statistical models for FGTA
tasks.

Distribution fitting, regression, variance matching, etc.

Explainable, easy to implement, and efficient to handle
large amounts of network traffic.

Poor efficacy especially when
the FGTA task is challenging.

Limited

[23], [113], [114]

Rule-based
approach

Utilize a set of pre-defined
rules to locate the target network traffic group. For FGTA
tasks, the rules can be complicated.

Session signatures, traffic
thresholds, predefined packet
header fields, etc.

Explainable, easy to implement, controllable, and efficient to handle large amounts
of network traffic.

It is usually challenging to
define rules for FGTA tasks.
Poor efficacy and poor flexibility.

Limited

[19], [24], [115]

Probabilistic
approach

Approaches based on probability theories to analyze network traffic at a fine granularity.

Bayesian classifier, Markov
model, HMM, etc.

Flexibility, adaptability, and
ease of use.

Complexity, sensitivity to assumptions, limited accuracy,
and relatively poor explainability.

Popular

[109], [116], [117]

Supervised
machine
learning

ML methods that rely on labeled network traffic data to
learn knowledge, which can
be used for network traffic
classifications or predictions.

KNN, SVM, LSTM, transformer, few shot learning, etc.

Great efficacy, ease of use,
and good flexibility.

Limited explainability, overfitting, dependency on highquality labeled data, limited
scalability, and requiring relatively long training time.

Most popular

[118]–[120]

Unsupervised
machine
learning

ML methods that do not require labeled training data and
can discover patterns and relationships in the network traffic
data on its own.

K-means, PCA, DBSCAN,
etc.

Discovering unknown patterns
in network traffic data, flexibility, no labels needed, and
no training time.

Limited result interpretability,
limited efficacy, poor scalability in inference, and overfitting.

Popular

[103], [121], [122]

Hybrid
approach

Combine multiple different
approaches for better performance in FGTA.

Ensemble
model,
semisupervised machine learning,
combining
statistical
approaches with rule-based
approaches, etc.

Inherits advantages of multiple classification or prediction
approaches.

Complicated to design, and
computationally expensive.

Popular

[20], [113], [122]

include session signatures [24], traffic thresholds [115], predefined packet header fields [19], etc. Similar to traditional
statistical approaches, rule-based approaches are explainable,
easy to implement, and efficient to operate, thereby being
widely used in traditional TA tasks. However, in the era
of FGTA, the analysis tasks are in finer granularity and
becoming more and more challenging. Thus, the pre-defined
rule sets are becoming larger, more complex, making them
more difficult to define, verify, and maintain. Moreover, the
rule-based approaches are not able to adapt to the dynamic
network environment, which is a common feature of modern
networks. Therefore, in recent trends, rule-based approaches
are less used in FGTA tasks. But they are still powerful tools in
some specific FGTA tasks, pre-classification, and accelerating
the analysis process.
3) Probabilistic approach: Probabilistic approaches are
based on probability theory and statistical inference to identify
the target network traffic group [125]. They model the traffic
data probabilistically for classification tasks. For instance,
typical probabilistic approaches like Bayesian classifier [126],
Markov model [127], or hidden Markov model (HMM) [128]
are widely used to model network traffic first. These models
can then be utilized to identify traffic patterns of specific
applications, protocols, anomaly, or behaviors. Benefitting
from the following advantages, a variety of FGTA approaches
have been proposed based on probabilistic approaches to tackle
different FGTA tasks [109], [116], [117]:
Flexibility: probabilistic approaches can be used to model
a wide range of traffic patterns and behaviors. Besides,
they can tolerate noise and uncertainty in the data,
making them powerful tools for analyzing complex and
heterogeneous traffic data.
• Adaptability: probabilistic approaches can be easily

•

adapted to changes in traffic patterns over time, allowing
them to detect new or previously unseen threats.
• Ease of use: with the support of various libraries, probabilistic approaches are relatively easy to implement
and does not require extensive domain knowledge or
expertise.
However, probabilistic approaches feature the following disadvantages, resulting limited performance and application
especially in complicated FGTA tasks (e.g., user behavior
inference):
• Complexity: probabilistic approaches are usually computationally expensive, especially when the network traffic
data is large and complex.
• Sensitivity to assumptions: probabilistic approaches are
sensitive to the assumptions (labels) made during model
training or development, and incorrect assumptions can
lead to inaccurate results.
• Limited accuracy: probabilistic approaches may not
achieve the highest accuracy compared to other more
advanced methods, such as deep learning, in some scenarios. Also, they are relatively weak in handling nondiscrete
data.
• Explainability: probabilistic approaches may not provide
as much interpretability as other methods, making it
difficult to understand how the models arrived at their
conclusions.
4) Supervised machine learning: Supervised machine
learning is a widely used machine learning method that can
be applied to almost any FGTA tasks with reliable prior
knowledge [18]. In supervised machine learning, a classifier
is trained using a labeled training dataset that includes known
classification labels. The trained classifier is then used to
classify or detect anomalies in new traffic data. Supervised ma-

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

12

chine learning approaches typically involve two main phases:
training and inference. During the training phase, the classifier
is trained on the labeled dataset (i.e., labeled network traffic)
to learn the relationship between the input features and the
classification labels. The inference phase involves using the
trained classifier to infer the classification labels of ongoing
network traffic.
With decades of development, researchers have proposed a
variety of supervised machine learning approaches [129], from
traditional machine learning methods, such as k-nearest neighbor (KNN), decision tree, Support Vector Machine (SVM), to
advanced deep learning methods [130], [131], such as multilayer perceptron (MLP), recurrent neural network (RNN),
long short-term memory (LSTM). Recently, there has been
a notable surge in applying state-of-the-art machine learning
techniques to FGTA. These include few-shot learning [132]–
[135], which achieves commendable accuracy with minimal
training network traffic data; transformers [136], [137], known
for their superior pattern recognition capabilities and scalability in training; transfer learning [138], [139], which utilizes
knowledge from other tasks or domains to enhance FGTA
performance with limited training traffic data; and online learning [140], a dynamic approach where the model continually
updates and refines its parameters with incoming network
traffic streams, enabling real-time adaptation to evolving network traffic patterns. Each of the proposed supervised machine
learning approaches has its own advantages and disadvantages,
making them suitable for different FGTA tasks. Selecting the
most suitable supervised machine learning approach is the
key to designing an effective ML-based FGTA approach. We
discuss more details about the ML algorithm select by use
case in Section V.
Overall, due to the following advantages, supervised machine learning approaches are the most widely used approaches in FGTA [23], [118]–[120]:
High accuracy: supervised machine learning can achieve
high accuracy in FGTA, especially when compared to
other methods.
• Ease of use: on the one hand, supervised machine learning approaches are relatively easy to implement, with
supports of various libraries and tools [141]–[143]. On
the other hand, they do not require extensive domain
knowledge or expertise to manually identify distinguishable rules or patterns.
• Flexibility: supervised machine learning approaches can
be used to model a wide range of traffic patterns and
behaviors.

•

However, supervised machine learning approaches also have
many shortcomings that limit their performance and use cases
in FGTA tasks:
Limited explainability: many supervised machine learning algorithms, such as DNN, can be difficult to interpret,
which can limit their usefulness in some applications,
especially in anomaly or attack detection.
• Overfitting: supervised machine learning models can
overfit to the training data, which can result in poor
performance on new data.
•

Dependency on labeled data: supervised machine learning
requires high-quality labeled training data, which can
be time-consuming and expensive to collect, making
them less effective than unsupervised or semi-supervised
methods in some cases.
• Limited scalability: many supervised machine learning
approaches may not scale well to extremely large or
complex datasets. Both the training and inference phases
may be computationally expensive.
•

5) Unsupervised machine learning: Unlike supervised machine learning, unsupervised machine learning is a machine
learning method that does not require labeled training data
and can discover patterns and relationships in the data on
its own [144]. Unsupervised machine learning algorithms
typically involve clustering [145] or dimensionality reduction [146] techniques that can help identify similarities and
differences between traffic flows. These algorithms do not
directly output labeled classification results, but can be used
to group similar traffic flows together or identify anomalous
traffic flows that do not fit into any of the existing clusters.
Widely used unsupervised machine learning algorithms include K-means [147], DBSCAN, principal component analysis
(PCA) [148], hierarchical clustering [149], etc.
Unsupervised machine learning algorithms feature the following advantages in FGTA:
Discovering unknown patterns: unsupervised machine
learning approaches can identify previously unknown
patterns and behaviors in the traffic data, which can be
useful for detecting new or emerging threats.
• Flexibility: unsupervised machine learning approaches
can be more flexible and adaptable than supervised machine learning as they do not require labeled data, making
them easy to work with a wide variety of traffic datasets.
• No training time: unsupervised machine learning approaches usually takes zero training time, making them
more efficient than supervised machine learning approaches regarding model development.
•

They also inevitably have the following disadvantages:
Limited result interpretability: interpreting the results
of the clustering or dimensionality reduction algorithms
used in unsupervised machine learning can be difficult
without prior domain knowledge.
• Limited accuracy: unsupervised machine learning may
not achieve the same level of accuracy as supervised
machine learning, especially when dealing with complex
or noisy traffic datasets.
• Scalability in inference: although taking no time for
training, some unsupervised machine learning algorithms
are computationally expensive in the inference phase,
which can limit their scalability.
• Overfitting: unsupervised machine learning models can
also suffer from overfitting or underfitting, which can
result in poor performance on certain datasets.
•

In conclusion, unsupervised machine learning is a powerful
tool for FGTA, but it may have limitations in terms of result interpretability and accuracy. Due to such natures, unsupervised

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

13

TABLE V: Widely used metrics that indicate the classification
efficacy for FGTA, where T P denotes the number of true
positives, T N denotes the number of true negatives, F P
denotes the number of false positives, and F N denotes the
number of false negatives.
Metric

Description

Calculation

TPR

The probability that an actual positive will test positive,
the key metric that indicates the sensitivity or true positive
rate of an analysis, reflects the FGTA approach’s ability
to correctly identify those with the condition.

TP
T P +F N

TNR

The probability that an actual negative will test negative.

TN
T N +F P

PPV

The probability that an item with a positive test result is
truly positive.

TP
T P +F P

NPV

The probability that an item with a negative test result is
truly negative.

TN
T N +F N

FNR

The probability of positives which yield negative outcomes, an important metric especially in anomaly or attack
detection.

FN
F N +T P

FPR

The probability of negatives which yield positive outcomes, one of the most important metrics that indicates the
usability of the FGTA approach. A high false positive rate
(FPR) can lead to a large number of false alarms, forcing
network administrators to ignore the analysis results.

FP
F P +T N

FDR

The probability that an item with a positive test result is
truly negative.

FP
F P +T P

FOR

The probability that an item with a negative test result is
truly positive.

FN
F N +T N

F1

The harmonic mean of precision (PPV) and recall (TPR),
indicating a balance bet

[...正文过长，此处由批处理脚本仅做上下文截断；请在结论中说明该限制...]

5-formats, accessed: 2022-03-14.
[78] “Argus project,” https://openargus.org/, date of visit: 2021-11-25.
[79] P. Phaal, S. Panchen, and N. McKee, “Rfc3176: Inmon corporation’s
sflow: A method for monitoring traffic in switched and routed networks,” 2001.
[80] “Tcpdump & libpcap,” https://www.tcpdump.org/, accessed: 2022-0210.
[81] ntop, “Pf ring documentation,” https://www.ntop.org/guides/pf ring/,
accessed: 2022-02-12.
[82] L. Rizzo, “netmap: a novel framework for fast packet i/o,” in 21st
USENIX Security Symposium (USENIX Security 12), 2012, pp. 101–
112.
[83] J. Rasley, B. Stephens, C. Dixon, E. Rozner, W. Felter, K. Agarwal,
J. Carter, and R. Fonseca, “Planck: Millisecond-scale monitoring and
control for commodity networks,” ACM SIGCOMM Computer Communication Review, vol. 44, no. 4, pp. 407–418, 2014.
[84] J. Svoboda, I. Ghafir, V. Prenosil et al., “Network monitoring approaches: An overview,” Int J Adv Comput Netw Secur, vol. 5, no. 2,
pp. 88–93, 2015.
[85] L.-M. Wang, T. Miskell, J. Morgan, and E. Verplanke, “Design of a
real-time traffic mirroring system,” in 2021 IFIP/IEEE International
Symposium on Integrated Network Management (IM). IEEE, 2021,
pp. 793–796.
[86] “ProfiShark
Network
TAPs,”
https://www.profitap.com/
profishark-network-taps/, 2019, accessed: 2022-02-11.
[87] Wikipedia, “Argus – audit record generation and utilization system,”
https://en.wikipedia.org/wiki/Argus %E2%80%93 Audit Record
Generation and Utilization System, accessed: 2022-02-11.
[88] Í. Cunha, F. Silveira, R. Oliveira, R. Teixeira, and C. Diot, “Uncovering
artifacts of flow measurement tools,” in International Conference on
Passive and Active Network Measurement. Springer, 2009, pp. 187–
196.
[89] Huawei, “Configuration guide - network management and monitoring,” https://support.huawei.com/enterprise/en/doc/EDOC1000178174/
986bf11e/overview-of-netstream, accessed: 2022-02-11.

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

33

[90] S. Waldbusser, R. Cole, C. Kalbfleisch, and D. Romascanu, “Introduction to the remote monitoring (rmon) family of mib modules,”
RFC3577, Network Working Group, 2003.
[91] T. Høiland-Jørgensen, J. D. Brouer, D. Borkmann, J. Fastabend,
T. Herbert, D. Ahern, and D. Miller, “The express data path: Fast
programmable packet processing in the operating system kernel,” in
Proceedings of the 14th international conference on emerging networking experiments and technologies, 2018, pp. 54–66.
[92] M. S. Brunella, G. Belocchi, M. Bonola, S. Pontarelli, G. Siracusano,
G. Bianchi, A. Cammarano, A. Palumbo, L. Petrucci, and R. Bifulco,
“{hXDP}: Efficient software packet processing on {FPGA}{NICs},”
in 14th USENIX Symposium on Operating Systems Design and Implementation (OSDI 20), 2020, pp. 973–990.
[93] Y. Zhou, C. Sun, H. H. Liu, R. Miao, S. Bai, B. Li, Z. Zheng,
L. Zhu, Z. Shen, Y. Xi et al., “Flow event telemetry on programmable
data plane,” in Proceedings of the Annual conference of the ACM
Special Interest Group on Data Communication on the applications,
technologies, architectures, and protocols for computer communication,
2020, pp. 76–89.
[94] D. Comer, “Ubiquitous b-tree,” ACM Computing Surveys (CSUR),
vol. 11, no. 2, pp. 121–137, 1979.
[95] P. Voigt and A. Von dem Bussche, “The eu general data protection
regulation (gdpr),” A Practical Guide, 1st Ed., Cham: Springer International Publishing, vol. 10, no. 3152676, pp. 10–5555, 2017.
[96] Q. Huang, X. Jin, P. P. Lee, R. Li, L. Tang, Y.-C. Chen, and
G. Zhang, “Sketchvisor: Robust network measurement for software
packet processing,” in Proceedings of the Conference of the ACM
Special Interest Group on Data Communication, 2017, pp. 113–126.
[97] T. Yang, J. Jiang, P. Liu, Q. Huang, J. Gong, Y. Zhou, R. Miao,
X. Li, and S. Uhlig, “Elastic sketch: Adaptive and fast network-wide
measurements,” in Proceedings of the 2018 Conference of the ACM
Special Interest Group on Data Communication, 2018, pp. 561–575.
[98] Y. Zhou, Y. Zhang, C. Ma, S. Chen, and O. O. Odegbile, “Generalized
sketch families for network traffic measurement,” Proceedings of the
ACM on Measurement and Analysis of Computing Systems, vol. 3,
no. 3, pp. 1–34, 2019.
[99] K. Yang, S. Long, Q. Shi, Y. Li, Z. Liu, Y. Wu, T. Yang, and Z. Jia,
“Sketchint: Empowering int with towersketch for per-flow per-switch
measurement,” IEEE Transactions on Parallel and Distributed Systems,
2023.
[100] R. Miao, Y. Zhang, Z. Zheng, R. Wang, R. Zhang, T. Yang, Z. Liu,
and J. Jiang, “Cocosketch: High-performance sketch-based measurement over arbitrary partial key query,” IEEE/ACM Transactions on
Networking, vol. 31, no. 6, pp. 2653–2668, 2023.
[101] H. Namkung, Z. Liu, D. Kim, V. Sekar, and P. Steenkiste,
“Sketchovsky: Enabling ensembles of sketches on programmable
switches,” in 20th USENIX Symposium on Networked Systems Design
and Implementation (NSDI 23), 2023, pp. 1273–1292.
[102] Y. Feng, J. Luo, C. Ma, T. Li, and L. Hui, “I can still observe
you: Flow-level behavior fingerprinting for online social network,” in
GLOBECOM 2022-2022 IEEE Global Communications Conference.
IEEE, 2022, pp. 6427–6432.
[103] Y. Feng, J. Li, L. Jiao, and X. Wu, “Towards learning-based, contentagnostic detection of social bot traffic,” IEEE Transactions on Dependable and Secure Computing, vol. 18, no. 5, pp. 2149–2163, 2021.
[104] M. Shen, J. Zhang, L. Zhu, K. Xu, X. Du, and Y. Liu, “Encrypted
traffic classification of decentralized applications on ethereum using
feature fusion,” in 2019 IEEE/ACM 27th International Symposium on
Quality of Service (IWQoS). IEEE, 2019, pp. 1–10.
[105] I. Guyon, S. Gunn, M. Nikravesh, and L. A. Zadeh, Feature extraction:
foundations and applications. Springer, 2008, vol. 207.
[106] S. Khalid, T. Khalil, and S. Nasreen, “A survey of feature selection and
feature extraction techniques in machine learning,” in 2014 science and
information conference. IEEE, 2014, pp. 372–378.
[107] R. Zebari, A. Abdulazeez, D. Zeebaree, D. Zebari, and J. Saeed,
“A comprehensive review of dimensionality reduction techniques for
feature selection and feature extraction,” Journal of Applied Science
and Technology Trends, vol. 1, no. 2, pp. 56–70, 2020.
[108] P. Dhal and C. Azad, “A comprehensive survey on feature selection in
the various fields of machine learning,” Applied Intelligence, pp. 1–39,
2022.
[109] H. F. Alan and J. Kaur, “Can android applications be identified using
only tcp/ip headers of their launch time traffic?” in Proceedings of
the 9th ACM conference on security & privacy in wireless and mobile
networks, 2016, pp. 61–66.
[110] T. A. Tang, L. Mhamdi, D. McLernon, S. A. R. Zaidi, and M. Ghogho,
“Deep learning approach for network intrusion detection in software

defined networking,” in 2016 international conference on wireless
networks and mobile communications (WINCOM). IEEE, 2016, pp.
258–263.
[111] S. Rezaei and X. Liu, “How to achieve high classification accuracy with
just a few labels: A semi-supervised approach using sampled packets,”
arXiv preprint arXiv:1812.09761, 2018.
[112] F. Gringoli, L. Salgarelli, M. Dusi, N. Cascarano, F. Risso, and
K. Claffy, “Gt: picking up the truth from the ground for internet traffic,”
ACM SIGCOMM Computer Communication Review, vol. 39, no. 5, pp.
12–18, 2009.
[113] Y. Feng, J. Li, and D. Sisodia, “Cj-sniffer: Measurement and contentagnostic detection of cryptojacking traffic,” in Proceedings of the
25th International Symposium on Research in Attacks, Intrusions and
Defenses, 2022, pp. 482–494.
[114] M. Jiang, G. Gou, J. Shi, and G. Xiong, “I know what you are doing
with remote desktop,” in 2019 IEEE 38th International Performance
Computing and Communications Conference (IPCCC). IEEE, 2019,
pp. 1–7.
[115] G. D. Bissias, M. Liberatore, D. Jensen, and B. N. Levine, “Privacy
vulnerabilities in encrypted http streams,” in International Workshop
on Privacy Enhancing Technologies. Springer, 2005, pp. 1–11.
[116] X. Cai, X. C. Zhang, B. Joshi, and R. Johnson, “Touching from a distance: Website fingerprinting attacks and defenses,” in Proceedings of
the 2012 ACM conference on Computer and communications security,
2012, pp. 605–616.
[117] Y. Fu, H. Xiong, X. Lu, J. Yang, and C. Chen, “Service usage
classification with encrypted internet traffic in mobile messaging apps,”
IEEE Transactions on Mobile Computing, vol. 15, no. 11, pp. 2851–
2864, 2016.
[118] Y. Wang, Z. Li, G. Gou, G. Xiong, C. Wang, and Z. Li, “Identifying
dapps and user behaviors on ethereum via encrypted traffic,” in
International Conference on Security and Privacy in Communication
Systems. Springer, 2020, pp. 62–83.
[119] G. Aceto, D. Ciuonzo, A. Montieri, and A. Pescapè, “Mimetic: Mobile encrypted traffic classification using multimodal deep learning,”
Computer networks, vol. 165, p. 106944, 2019.
[120] M. Lotfollahi, M. Jafari Siavoshani, R. Shirali Hossein Zade, and
M. Saberian, “Deep packet: A novel approach for encrypted traffic
classification using deep learning,” Soft Computing, vol. 24, no. 3, pp.
1999–2012, 2020.
[121] P. V. Amoli, T. Hamalainen, G. David, M. Zolotukhin, and
M. Mirzamohammad, “Unsupervised network intrusion detection systems for zero-day fast-spreading attacks and botnets,” JDCTA (International Journal of Digital Content Technology and its Applications,
vol. 10, no. 2, pp. 1–13, 2016.
[122] N. Shone, T. N. Ngoc, V. D. Phai, and Q. Shi, “A deep learning approach to network intrusion detection,” IEEE transactions on emerging
topics in computational intelligence, vol. 2, no. 1, pp. 41–50, 2018.
[123] K. Park and W. Willinger, “Self-similar network traffic: An overview,”
Self-Similar Network Traffic and Performance Evaluation, pp. 1–38,
2000.
[124] W. Duch, R. Setiono, and J. M. Zurada, “Computational intelligence
methods for rule-based data understanding,” Proceedings of the IEEE,
vol. 92, no. 5, pp. 771–805, 2004.
[125] N. Alon and J. H. Spencer, The probabilistic method. John Wiley &
Sons, 2016.
[126] I. Rish et al., “An empirical study of the naive bayes classifier,” in
IJCAI 2001 workshop on empirical methods in artificial intelligence,
vol. 3, no. 22, 2001, pp. 41–46.
[127] M. H. Davis, Markov models & optimization. CRC Press, 1993,
vol. 49.
[128] L. Rabiner and B. Juang, “An introduction to hidden markov models,”
ieee assp magazine, vol. 3, no. 1, pp. 4–16, 1986.
[129] M. I. Jordan and T. M. Mitchell, “Machine learning: Trends, perspectives, and prospects,” Science, vol. 349, no. 6245, pp. 255–260, 2015.
[130] Y. LeCun, Y. Bengio, and G. Hinton, “Deep learning,” nature, vol. 521,
no. 7553, pp. 436–444, 2015.
[131] I. Goodfellow, Y. Bengio, and A. Courville, Deep learning. MIT
press, 2016.
[132] Q. Zhou, L. Wang, H. Zhu, and T. Lu, “Few-shot website fingerprinting
attack with cluster adaptation,” Computer Networks, vol. 229, p.
109780, 2023.
[133] H. Zou, J. Su, Z. Wei, S. Chen, and B. Zhao, “An efficient crossdomain few-shot website fingerprinting attack with brownian distance
covariance,” Computer Networks, vol. 219, p. 109461, 2022.

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

34

[134] M. Chen, Y. Wang, and X. Zhu, “Few-shot website fingerprinting attack
with meta-bias learning,” Pattern Recognition, vol. 130, p. 108739,
2022.
[135] P. Liu, L. He, and Z. Li, “A survey on deep learning for website
fingerprinting attacks and defenses,” IEEE Access, vol. 11, pp. 26 033–
26 047, 2023.
[136] M. Li, D. Han, D. Li, H. Liu, and C.-C. Chang, “Mfvt: an anomaly
traffic detection method merging feature fusion network and vision
transformer architecture,” EURASIP Journal on Wireless Communications and Networking, vol. 2022, no. 1, p. 39, 2022.
[137] X. Lin, G. Xiong, G. Gou, Z. Li, J. Shi, and J. Yu, “Et-bert: A
contextualized datagram representation with pre-training transformers
for encrypted traffic classification,” in Proceedings of the ACM Web
Conference 2022, ser. WWW ’22. New York, NY, USA: Association
for Computing Machinery, 2022, p. 633–642. [Online]. Available:
https://doi.org/10.1145/3485447.3512217
[138] D. A. Bierbrauer, M. J. De Lucia, K. Reddy, P. Maxwell, and N. D.
Bastian, “Transfer learning for raw network traffic detection,” Expert
Systems with Applications, vol. 211, p. 118641, 2023.
[139] C. Zhang, H. Zhang, J. Qiao, D. Yuan, and M. Zhang, “Deep transfer
learning for intelligent cellular traffic prediction based on cross-domain
big data,” IEEE Journal on Selected Areas in Communications, vol. 37,
no. 6, pp. 1389–1401, 2019.
[140] A. Shahraki, M. Abbasi, A. Taherkordi, and A. D. Jurcut, “A comparative study on online machine learning techniques for network traffic
streams analysis,” Computer Networks, vol. 207, p. 108836, 2022.
[141] M. Abadi, P. Barham, J. Chen, Z. Chen, A. Davis, J. Dean, M. Devin,
S. Ghemawat, G. Irving, M. Isard et al., “Tensorflow: a system for
large-scale machine learning.” in Osdi, vol. 16, no. 2016. Savannah,
GA, USA, 2016, pp. 265–283.
[142] A. Paszke, S. Gross, F. Massa, A. Lerer, J. Bradbury, G. Chanan,
T. Killeen, Z. Lin, N. Gimelshein, L. Antiga et al., “Pytorch: An
imperative style, high-performance deep learning library,” Advances
in neural information processing systems, vol. 32, 2019.
[143] Y. Jia, E. Shelhamer, J. Donahue, S. Karayev, J. Long, R. Girshick,
S. Guadarrama, and T. Darrell, “Caffe: Convolutional architecture for
fast feature embedding,” in Proceedings of the 22nd ACM international
conference on Multimedia, 2014, pp. 675–678.
[144] M. Alloghani, D. Al-Jumeily, J. Mustafina, A. Hussain, and A. J.
Aljaaf, “A systematic review on supervised and unsupervised machine
learning algorithms for data science,” Supervised and unsupervised
learning for data science, pp. 3–21, 2020.
[145] M. Usama, J. Qadir, A. Raza, H. Arif, K.-L. A. Yau, Y. Elkhatib,
A. Hussain, and A. Al-Fuqaha, “Unsupervised machine learning for
networking: Techniques, applications and research challenges,” IEEE
access, vol. 7, pp. 65 579–65 615, 2019.
[146] L. Van Der Maaten, E. Postma, J. Van den Herik et al., “Dimensionality
reduction: a comparative,” J Mach Learn Res, vol. 10, no. 66-71, p. 13,
2009.
[147] J. A. Hartigan and M. A. Wong, “Algorithm as 136: A k-means
clustering algorithm,” Journal of the royal statistical society. series
c (applied statistics), vol. 28, no. 1, pp. 100–108, 1979.
[148] G. H. Dunteman, Principal components analysis. Sage, 1989, no. 69.
[149] F. Murtagh and P. Contreras, “Algorithms for hierarchical clustering: an
overview,” Wiley Interdisciplinary Reviews: Data Mining and Knowledge Discovery, vol. 2, no. 1, pp. 86–97, 2012.
[150] J. Lever, “Classification evaluation: It is important to understand both
what a classification metric expresses and what it hides,” Nature
methods, vol. 13, no. 8, pp. 603–605, 2016.
[151] D. Barradas, N. Santos, L. Rodrigues, S. Signorello, F. M. Ramos,
and A. Madeira, “Flowlens: Enabling efficient flow classification for
ml-based network security applications,” in Proceedings of the 28th
Network and Distributed System Security Symposium (San Diego, CA,
USA, 2021.
[152] Y. Feng, J. Li, D. Sisodia, and P. Reiher, “On explainable and adaptable
detection of distributed denial-of-service traffic,” IEEE Transactions
on Dependable and Secure Computing, vol. 21, no. 4, pp. 2211–2226,
2024.
[153] P. Bukaty, The california consumer privacy act (ccpa): An implementation guide. IT Governance Ltd, 2019.
[154] A. K. Das, P. H. Pathak, C.-N. Chuah, and P. Mohapatra, “Privacyaware contextual localization using network traffic analysis,” Computer
Networks, vol. 118, pp. 24–36, 2017.
[155] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “Kitsune: An
ensemble of autoencoders for online network intrusion detection,” in
Network and Distributed Systems Security (NDSS) Symposium, 2018.

[156] N. Rosner, I. B. Kadron, L. Bang, and T. Bultan, “Profit: Detecting and
quantifying side channels in networked applications.” in NDSS, 2019.
[157] M. J. Khokhar, T. Ehlinger, and C. Barakat, “From network traffic
measurements to qoe for internet video,” in 2019 IFIP Networking
Conference (IFIP Networking). IEEE, 2019, pp. 1–9.
[158] Kentik, “Kentik—the network observability platform,” https://www.
kentik.com/, accessed: 2023-12-05.
[159] P. A. Networks, “Hunt down and stop tomorrow’s threats,
today—analyze network traffic with best-in-class machine
learning and analytics,” https://www.paloaltonetworks.com/cortex/
network-traffic-analysis, accessed: 2023-12-05.
[160] Z. M. Fadlullah, T. Taleb, N. Ansari, K. Hashimoto, Y. Miyake,
Y. Nemoto, and N. Kato, “Combating against attacks on encrypted protocols,” in 2007 IEEE International Conference on Communications.
IEEE, 2007, pp. 1211–1216.
[161] T. Taleb, Z. M. Fadlullah, K. Hashimoto, Y. Nemoto, and N. Kato,
“Tracing back attacks against encrypted protocols,” in Proceedings of
the 2007 international conference on Wireless communications and
mobile computing, 2007, pp. 121–126.
[162] Y. Feng and J. Li, “Toward explainable and adaptable detection and
classification of distributed denial-of-service attacks,” in International
Workshop on Deployable Machine Learning for Security Defense.
Springer, 2020, pp. 105–121.
[163] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A
survey,” ACM computing surveys (CSUR), vol. 41, no. 3, pp. 1–58,
2009.
[164] D. Han, Z. Wang, W. Chen, K. Wang, R. Yu, S. Wang, H. Zhang,
Z. Wang, M. Jin, J. Yang et al., “Anomaly detection in the open world:
Normality shift detection, explanation, and adaptation,” in 30th Annual
Network and Distributed System Security Symposium (NDSS), 2023.
[165] F. Ullah, S. Ullah, G. Srivastava, and J. C.-W. Lin, “Ids-int: Intrusion
detection system using transformer-based transfer learning for imbalanced network traffic,” Digital Communications and Networks, vol. 10,
no. 1, pp. 190–204, 2024.
[166] A. Shabtai, L. Tenenboim-Chekina, D. Mimran, L. Rokach, B. Shapira,
and Y. Elovici, “Mobile malware detection through analysis of deviations in application network behavior,” Computers & Security, vol. 43,
pp. 1–18, 2014.
[167] S. Wang, Z. Chen, L. Zhang, Q. Yan, B. Yang, L. Peng, and Z. Jia,
“Trafficav: An effective and explainable detection of mobile malware
behavior using network traffic,” in 2016 IEEE/ACM 24th International
Symposium on Quality of Service (IWQoS). IEEE, 2016, pp. 1–6.
[168] A. H. Lashkari, A. F. A. Kadir, H. Gonzalez, K. F. Mbah, and A. A.
Ghorbani, “Towards a network-based framework for android malware
detection and characterization,” in 2017 15th Annual conference on
privacy, security and trust (PST). IEEE, 2017, pp. 233–23 309.
[169] M. Piskozub, F. De Gaspari, F. Barr-Smith, L. Mancini, and
I. Martinovic, “Malphase: Fine-grained malware detection using
network flow data,” in Proceedings of the 2021 ACM Asia Conference
on Computer and Communications Security, ser. ASIA CCS ’21.
New York, NY, USA: Association for Computing Machinery, 2021,
p. 774–786. [Online]. Available: https://doi.org/10.1145/3433210.
3453101
[170] J. Ren, A. Rao, M. Lindorfer, A. Legout, and D. Choffnes, “Recon:
Revealing and controlling pii leaks in mobile network traffic,” in
Proceedings of the 14th Annual International Conference on Mobile
Systems, Applications, and Services, 2016, pp. 361–374.
[171] A. Continella, Y. Fratantonio, M. Lindorfer, A. Puccetti, A. Zand,
C. Kruegel, and G. Vigna, “Obfuscation-resilient privacy leak detection
for mobile apps through differential analysis.” in NDSS, 2017.
[172] D. Willems, K. Kohls, B. van der Kamp, and H. Vranken,
“Data exfiltration detection on network metadata with autoencoders,”
Electronics, vol. 12, no. 12, 2023. [Online]. Available: https:
//www.mdpi.com/2079-9292/12/12/2584
[173] R. Coulter, Q.-L. Han, L. Pan, J. Zhang, and Y. Xiang, “Datadriven cyber security in perspective—intelligent traffic analysis,” IEEE
transactions on cybernetics, vol. 50, no. 7, pp. 3081–3093, 2019.
[174] E. Papadogiannaki and S. Ioannidis, “Acceleration of intrusion detection in encrypted network traffic using heterogeneous hardware,”
Sensors, vol. 21, no. 4, p. 1140, 2021.
[175] R. Moustafa and J. Slay, “A comprehensive data set for network
intrusion detection systems,” School of Engineering and Information
Technology University of New South Wales at the Australian Defense
Force Academy Canberra, Australia, UNSW-NB15, 2015.
[176] X. Wei, L. Gomez, I. Neamtiu, and M. Faloutsos, “Profiledroid: Multilayer profiling of android applications,” in Proceedings of the 18th

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

35

annual international conference on Mobile computing and networking,
2012, pp. 137–148.
[177] W. Enck, P. Gilbert, S. Han, V. Tendulkar, B.-G. Chun, L. P. Cox,
J. Jung, P. McDaniel, and A. N. Sheth, “Taintdroid: an informationflow tracking system for realtime privacy monitoring on smartphones,”
ACM Transactions on Computer Systems (TOCS), vol. 32, no. 2, pp.
1–29, 2014.
[178] A. Razaghpanah, N. Vallina-Rodriguez, S. Sundaresan, C. Kreibich,
P. Gill, M. Allman, and V. Paxson, “Haystack: In situ mobile traffic
analysis in user space,” arXiv preprint arXiv:1510.01419, pp. 1–13,
2015.
[179] Y. Song and U. Hengartner, “Privacyguard: A vpn-based platform
to detect information leakage on android devices,” in Proceedings
of the 5th Annual ACM CCS Workshop on Security and Privacy in
Smartphones and Mobile Devices, 2015, pp. 15–26.
[180] A. Le, J. Varmarken, S. Langhoff, A. Shuba, M. Gjoka, and
A. Markopoulou, “Antmonitor: A system for monitoring from mobile
devices,” in Proceedings of the 2015 ACM SIGCOMM Workshop on
Crowdsourcing and Crowdsharing of Big (Internet) Data, 2015, pp.
15–20.
[181] M. Hall, E. Frank, G. Holmes, B. Pfahringer, P. Reutemann, and I. H.
Witten, “The weka data mining software: an update,” ACM SIGKDD
explorations newsletter, vol. 11, no. 1, pp. 10–18, 2009.
[182] Y. Feng, D. Sisodia, and J. Li, “Poster: Content-agnostic identification
of cryptojacking in network traffic,” in Proceedings of the 15th ACM
Asia Conference on Computer and Communications Security, 2020, pp.
907–909.
[183] S. Khirman and P. Henriksen, “Relationship between quality-of-service
and quality-of-experience for public internet service,” in In Proc. of the
3rd Workshop on Passive and Active Measurement, vol. 1, 2002.
[184] X. Xiao and L. M. Ni, “Internet qos: A big picture,” IEEE network,
vol. 13, no. 2, pp. 8–18, 1999.
[185] M. Karakus and A. Durresi, “Quality of service (qos) in software
defined networking (sdn): A survey,” Journal of Network and Computer
Applications, vol. 80, pp. 200–218, 2017.
[186] S. K. Keshari, V. Kansal, and S. Kumar, “A systematic review of
quality of services (qos) in software defined networking (sdn),” Wireless
Personal Communications, vol. 116, no. 3, pp. 2593–2614, 2021.
[187] J. Bi, X. Zhang, H. Yuan, J. Zhang, and M. Zhou, “A hybrid prediction method for realistic network traffic with temporal convolutional
network and lstm,” IEEE Transactions on Automation Science and
Engineering, vol. 19, no. 3, pp. 1869–1879, 2021.
[188] A. Montieri, G. Bovenzi, G. Aceto, D. Ciuonzo, V. Persico, and
A. Pescapè, “Packet-level prediction of mobile-app traffic using multitask deep learning,” Computer Networks, vol. 200, p. 108529, 2021.
[189] D. Andreoletti, S. Troia, F. Musumeci, S. Giordano, G. Maier, and
M. Tornatore, “Network traffic prediction based on diffusion convolutional recurrent neural networks,” in IEEE INFOCOM 2019 - IEEE
Conference on Computer Communications Workshops (INFOCOM
WKSHPS), 2019, pp. 246–251.
[190] I. Lohrasbinasab, A. Shahraki, A. Taherkordi, and A. Delia Jurcut,
“From statistical-to machine learning-based network traffic prediction,”
Transactions on Emerging Telecommunications Technologies, vol. 33,
no. 4, p. e4394, 2022.
[191] L. Tang, J. Li, H. Du, L. Li, J. Wu, and S. Wang, “Big data in
forecasting research: a literature review,” Big Data Research, vol. 27,
p. 100289, 2022.
[192] T. Hoßfeld and A. Binzenhöfer, “Analysis of skype voip traffic in umts:
End-to-end qos and qoe measurements,” Computer Networks, vol. 52,
no. 3, pp. 650–666, 2008.
[193] F. Agboma, M. Smy, and A. Liotta, “Qoe analysis of a peer-to-peer
television system,” in Proceedings of IADISInt. Conf. on Telecommunications, Networks and Systems, 2008, pp. 365–382.
[194] G. Dimopoulos, I. Leontiadis, P. Barlet-Ros, and K. Papagiannaki,
“Measuring video qoe from encrypted traffic,” in Proceedings of the
2016 Internet Measurement Conference, 2016, pp. 513–526.
[195] I. Orsolic, D. Pevec, M. Suznjevic, and L. Skorin-Kapov, “Youtube
qoe estimation based on the analysis of encrypted network traffic using
machine learning,” in 2016 IEEE Globecom Workshops (GC Wkshps).
IEEE, 2016, pp. 1–6.
[196] M. H. Mazhar and Z. Shafiq, “Real-time video quality of experience
monitoring for https and quic,” in IEEE INFOCOM 2018-IEEE Conference on Computer Communications. IEEE, 2018, pp. 1331–1339.
[197] D. McCoy, K. Bauer, D. Grunwald, T. Kohno, and D. Sicker, “Shining
light in dark places: Understanding the tor network,” in International
symposium on privacy enhancing technologies symposium. Springer,
2008, pp. 63–76.

[198] M.
Perry,
“Experimental
defense
for
website
traffic
fingerprinting,”
https://blog.torproject.org/
experimental-defense-website-traffic-fingerprinting/, posted: 2011-0905.
[199] “Shadowsocks - a fast tunnel proxy that helps you bypass firewalls,”
https://shadowsocks.org/, accessed: 2022-02-11.
[200] S. Mistry and B. Raman, “Quantifying traffic analysis of encrypted
web-browsing.” 1998, project paper.
[201] Q. Sun, D. R. Simon, Y.-M. Wang, W. Russell, V. N. Padmanabhan, and
L. Qiu, “Statistical identification of encrypted web browsing traffic,” in
Proceedings 2002 IEEE Symposium on Security and Privacy. IEEE,
2002, pp. 19–30.
[202] M. Liberatore and B. N. Levine, “Inferring the source of encrypted http
connections,” in Proceedings of the 13th ACM conference on Computer
and communications security, 2006, pp. 255–263.
[203] D. Herrmann, R. Wendolsky, and H. Federrath, “Website fingerprinting:
attacking popular privacy enhancing technologies with the multinomial
naı̈ve-bayes classifier,” in Proceedings of the 2009 ACM workshop on
Cloud computing security, 2009, pp. 31–42.
[204] A. Panchenko, L. Niessen, A. Zinnen, and T. Engel, “Website fingerprinting in onion routing based anonymization networks,” in Proceedings of the 10th annual ACM workshop on Privacy in the electronic
society, 2011, pp. 103–114.
[205] T. Wang, X. Cai, R. Nithyanand, R. Johnson, and I. Goldberg, “Effective attacks and provable defenses for website fingerprinting,” in
23rd USENIX Security Symposium (USENIX Security 14), 2014, pp.
143–157.
[206] J. Hayes and G. Danezis, “k-fingerprinting: A robust scalable website fingerprinting technique,” in 25th USENIX Security Symposium
(USENIX Security 16), 2016, pp. 1187–1203.
[207] V. Rimmer, D. Preuveneers, M. Juarez, T. Van Goethem, and W. Joosen,
“Automated website fingerprinting through deep learning,” 2017.
[208] P. Sirinam, M. Imani, M. Juarez, and M. Wright, “Deep fingerprinting:
Undermining website fingerprinting defenses with deep learning,” in
Proceedings of the 2018 ACM SIGSAC Conference on Computer and
Communications Security, 2018, pp. 1928–1943.
[209] P. Sirinam, N. Mathews, M. S. Rahman, and M. Wright, “Triplet
fingerprinting: More practical and portable website fingerprinting with
n-shot learning,” in Proceedings of the 2019 ACM SIGSAC Conference
on Computer and Communications Security, 2019, pp. 1131–1148.
[210] Y. Wang, H. Xu, Z. Guo, Z. Qin, and K. Ren, “Snwf: website
fingerprinting attack by ensembling the snapshot of deep learning,”
IEEE Transactions on Information Forensics and Security, vol. 17, pp.
1214–1226, 2022.
[211] X. Deng, Q. Yin, Z. Liu, X. Zhao, Q. Li, M. Xu, K. Xu, and J. Wu,
“Robust multi-tab website fingerprinting attacks in the wild,” in 2023
IEEE Symposium on Security and Privacy (SP). IEEE, 2023, pp.
1005–1022.
[212] R. Fielding, J. Gettys, J. Mogul, H. Frystyk, L. Masinter, P. Leach, and
T. Berners-Lee, “Rfc2616: Hypertext transfer protocol–http/1.1,” 1999.
[213] A. Hintz, “Fingerprinting websites using traffic analysis,” in International workshop on privacy enhancing technologies. Springer, 2002,
pp. 171–178.
[214] L. Lu, E.-C. Chang, and M. C. Chan, “Website fingerprinting and identification using ordered feature sequences,” in European Symposium on
Research in Computer Security. Springer, 2010, pp. 199–214.
[215] S. J. Murdoch and R. N. Watson, “Metrics for security and performance
in low-latency anonymity systems,” in International Symposium on
Privacy Enhancing Technologies Symposium. Springer, 2008, pp. 115–
132.
[216] W. De la Cadena, A. Mitseva, J. Hiller, J. Pennekamp, S. Reuter, J. Filter, T. Engel, K. Wehrle, and A. Panchenko, “Trafficsliver: Fighting
website fingerprinting attacks with traffic splitting,” in Proceedings of
the 2020 ACM SIGSAC Conference on Computer and Communications
Security, 2020, pp. 1971–1985.
[217] R. Dingledine and N. Mathewson, “Tor protocol specification,” https:
//gitweb.torproject.org/torspec.git/tree/tor-spec.txt, date of visit: 202110-05.
[218] K. P. Dyer, S. E. Coull, T. Ristenpart, and T. Shrimpton, “Peek-a-boo,
i still see you: Why efficient traffic analysis countermeasures fail,” in
2012 IEEE symposium on security and privacy. IEEE, 2012, pp.
332–346.
[219] T. Wang and I. Goldberg, “Improved website fingerprinting on tor,” in
Proceedings of the 12th ACM workshop on Workshop on privacy in
the electronic society, 2013, pp. 201–212.
[220] M. Juarez, S. Afroz, G. Acar, C. Diaz, and R. Greenstadt, “A critical
evaluation of website fingerprinting attacks,” in Proceedings of the 2014

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

36

ACM SIGSAC Conference on Computer and Communications Security,
2014, pp. 263–274.
[221] A. Panchenko, F. Lanze, J. Pennekamp, T. Engel, A. Zinnen, M. Henze,
and K. Wehrle, “Website fingerprinting at internet scale.” in NDSS,
2016.
[222] X. Cai, R. Nithyanand, T. Wang, R. Johnson, and I. Goldberg, “A systematic approach to developing and evaluating website fingerprinting
defenses,” in Proceedings of the 2014 ACM SIGSAC Conference on
Computer and Communications Security, 2014, pp. 227–238.
[223] T. Wang and I. Goldberg, “Walkie-talkie: An efficient defense against
passive website fingerprinting attacks,” in 26th {USENIX} Security
Symposium ({USENIX} Security 17), 2017, pp. 1375–1390.
[224] M. Juarez, M. Imani, M. Perry, C. Diaz, and M. Wright, “Toward an
efficient website fingerprinting defense,” in European Symposium on
Research in Computer Security. Springer, 2016, pp. 27–46.
[225] K. Abe and S. Goto, “Fingerprinting attack on tor anonymity using deep
learning,” Proceedings of the Asia-Pacific Advanced Network, vol. 42,
pp. 15–20, 2016.
[226] S. Bhat, D. Lu, A. Kwon, and S. Devadas, “Var-cnn: A data-efficient
website fingerprinting attack based on deep learning,” Proceedings on
Privacy Enhancing Technologies, vol. 1, p. 19.
[227] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for image
recognition,” in Proceedings of the IEEE conference on computer vision
and pattern recognition, 2016, pp. 770–778.
[228] S. E. Oh, S. Sunkam, and N. Hopper, “-fp: Extraction, classification,
and prediction of website fingerprints with deep learning,” Proceedings
on Privacy Enhancing Technologies, vol. 2019, no. 3, pp. 191–209,
2019.
[229] C. Wang, J. Dani, X. Li, X. Jia, and B. Wang, “Adaptive fingerprinting:
website fingerprinting over few encrypted traffic,” in Proceedings of
the Eleventh ACM Conference on Data and Application Security and
Privacy, 2021, pp. 149–160.
[230] N. P. Hoang, A. A. Niaki, P. Gill, and M. Polychronakis, “Domain
name encryption is not enough: privacy leakage via ip-based website
fingerprinting,” Proceedings on Privacy Enhancing Technologies, vol.
2021, no. 4, pp. 420–440, 2021.
[231] O. Ajao, J. Hong, and W. Liu, “A survey of location inference
techniques on twitter,” Journal of Information Science, vol. 41, no. 6,
pp. 855–864, 2015.
[232] Y. Ikawa, M. Enoki, and M. Tatsubori, “Location inference using microblog messages,” in Proceedings of the 21st international conference
on world wide web, 2012, pp. 687–690.
[233] J. Han, E. Owusu, L. T. Nguyen, A. Perrig, and J. Zhang, “Accomplice: Location inference using accelerometers on smartphones,” in
2012 Fourth International Conference on Communication Systems and
Networks (COMSNETS 2012). IEEE, 2012, pp. 1–9.
[234] A. Gallagher, D. Joshi, J. Yu, and J. Luo, “Geo-location inference
from image content and user tags,” in 2009 IEEE Computer Society
Conference on Computer Vision and Pattern Recognition Workshops.
IEEE, 2009, pp. 55–62.
[235] I. Trestian, S. Ranjan, A. Kuzmanovic, and A. Nucci, “Measuring
serendipity: connecting people, locations and interests in a mobile 3g
network,” in Proceedings of the 9th ACM SIGCOMM conference on
Internet measurement, 2009, pp. 267–279.
[236] A. K. Das, P. H. Pathak, C.-N. Chuah, and P. Mohapatra, “Contextual
localization through network traffic analysis,” in IEEE INFOCOM
2014-IEEE Conference on Computer Communications. IEEE, 2014,
pp. 925–933.
[237] F. Xu, Y. Li, H. Wang, P. Zhang, and D. Jin, “Understanding mobile
traffic patterns of large scale cellular towers in urban environment,”
IEEE/ACM transactions on networking, vol. 25, no. 2, pp. 1147–1161,
2016.
[238] H. Wang, F. Xu, Y. Li, P. Zhang, and D. Jin, “Understanding mobile
traffic patterns of large scale cellular towers in urban environment,” in
Proceedings of the 2015 Internet Measurement Conference, 2015, pp.
225–238.
[239] F. Xu, Y. Lin, J. Huang, D. Wu, H. Shi, J. Song, and Y. Li, “Big
data driven mobile traffic understanding and forecasting: A time series
approach,” IEEE transactions on services computing, vol. 9, no. 5, pp.
796–805, 2016.
[240] R. Lippmann, D. Fried, K. Piwowarski, and W. Streilein, “Passive operating system identification from tcp/ip packet headers,” in Workshop
on Data Mining for Computer Security, vol. 40, 2003.
[241] Y.-C. Chen, Y. Liao, M. Baldi, S.-J. Lee, and L. Qiu, “Os fingerprinting
and tethering detection in mobile networks,” in Proceedings of the 2014
Conference on Internet Measurement Conference, 2014, pp. 173–180.

[242] M. Laštovička, S. Špaček, P. Velan, and P. Čeleda, “Using tls fingerprints for os identification in encrypted traffic,” in NOMS 2020-2020
IEEE/IFIP Network Operations and Management Symposium. IEEE,
2020, pp. 1–6.
[243] N. Ruffing, Y. Zhu, R. Libertini, Y. Guan, and R. Bettati, “Smartphone reconnaissance: Operating system identification,” in 2016 13th
IEEE Annual Consumer Communications & Networking Conference
(CCNC). IEEE, 2016, pp. 1086–1091.
[244] M. Lopez-Martin, B. Carro, A. Sanchez-Esguevillas, and J. Lloret,
“Network traffic classifier with convolutional and recurrent neural
networks for internet of things,” IEEE access, vol. 5, pp. 18 042–18 050,
2017.
[245] Y. Meidan, M. Bohadana, A. Shabtai, J. D. Guarnizo, M. Ochoa, N. O.
Tippenhauer, and Y. Elovici, “Profiliot: a machine learning approach
for iot device identification based on network traffic analysis,” in
Proceedings of the symposium on applied computing, 2017, pp. 506–
509.
[246] A. Sivanathan, H. H. Gharakheili, F. Loi, A. Radford, C. Wijenayake,
A. Vishwanath, and V. Sivaraman, “Classifying iot devices in smart
environments using network traffic characteristics,” IEEE Transactions
on Mobile Computing, vol. 18, no. 8, pp. 1745–1759, 2018.
[247] H. Yao, P. Gao, J. Wang, P. Zhang, C. Jiang, and Z. Han, “Capsule
network assisted iot traffic classification mechanism for smart cities,”
IEEE Internet of Things Journal, vol. 6, no. 5, pp. 7515–7525, 2019.
[248] L. Bernaille, R. Teixeira, I. Akodkenou, A. Soule, and K. Salamatian,
“Traffic classification on the fly,” ACM SIGCOMM Computer Communication Review, vol. 36, no. 2, pp. 23–26, 2006.
[249] T. Karagiannis, K. Papagiannaki, and M. Faloutsos, “Blinc: multilevel
traffic classification in the dark,” in Proceedings of the 2005 conference on Applications, technologies, architectures, and protocols for
computer communications, 2005, pp. 229–240.
[250] L. Bernaille and R. Teixeira, “Early recognition of encrypted applications,” in International Conference on Passive and Active Network
Measurement. Springer, 2007, pp. 165–175.
[251] L. Bernaille, R. Teixeira, and K. Salamatian, “Early application identification,” in Proceedings of the 2006 ACM CoNEXT conference, 2006,
pp. 1–12.
[252] A. McGregor, M. Hall, P. Lorier, and J. Brunskill, “Flow clustering
using machine learning techniques,” in International workshop on
passive and active network measurement. Springer, 2004, pp. 205–
214.
[253] A. W. Moore and D. Zuev, “Internet traffic classification using bayesian
analysis techniques,” in Proceedings of the 2005 ACM SIGMETRICS
international conference on Measurement and modeling of computer
systems, 2005, pp. 50–60.
[254] Z. Chen, K. He, J. Li, and Y. Geng, “Seq2img: A sequence-to-image
based approach towards ip traffic classification using convolutional
neural networks,” in 2017 IEEE International conference on big data
(big data). IEEE, 2017, pp. 1271–1276.
[255] J. Zhao, Q. Li, Y. Hong, and M. Shen, “Metarocketc: Adaptive
encrypted traffic classification in complex network environments via
time series analysis and meta-learning,” IEEE Transactions on Network
and Service Management, vol. 21, no. 2, pp. 2460–2476, 2024.
[256] Q. Wang, A. Yahyavi, B. Kemme, and W. He, “I know what you did on
your smartphone: Inferring app usage over encrypted data traffic,” in
2015 IEEE conference on communications and network security (CNS).
IEEE, 2015, pp. 433–441.
[257] V. F. Taylor, R. Spolaor, M. Conti, and I. Martinovic, “Appscanner:
Automatic fingerprinting of smartphone apps from encrypted network
traffic,” in 2016 IEEE European Symposium on Security and Privacy
(EuroS&P). IEEE, 2016, pp. 439–454.
[258] G. Aceto, D. Ciuonzo, A. Montieri, and A. Pescapé, “Multiclassification approaches for classifying mobile app traffic,” Journal
of Network and Computer Applications, vol. 103, pp. 131–145, 2018.
[259] T.-D. Pham, T.-L. Ho, T. Truong-Huu, T.-D. Cao, and H.-L. Truong,
“Mappgraph: Mobile-app classification on encrypted network traffic
using deep graph convolution neural networks,” in Proceedings of the
37th Annual Computer Security Applications Conference, 2021, pp.
1025–1038.
[260] F. Aiolli, M. Conti, A. Gangwal, and M. Polato, “Mind your wallet’s
privacy: identifying bitcoin wallet apps and user’s actions through
network traffic analysis,” in Proceedings of the 34th ACM/SIGAPP
Symposium on Applied Computing, 2019, pp. 1484–1491.
[261] M. Shen, J. Zhang, L. Zhu, K. Xu, and X. Du, “Accurate decentralized
application identification via encrypted traffic analysis using graph
neural networks,” IEEE Transactions on Information Forensics and
Security, vol. 16, pp. 2367–2380, 2021.

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

37

[262] V. F. Taylor, R. Spolaor, M. Conti, and I. Martinovic, “Robust smartphone app identification via encrypted network traffic analysis,” IEEE
Transactions on Information Forensics and Security, vol. 13, no. 1, pp.
63–78, 2017.
[263] G. Aceto, D. Ciuonzo, A. Montieri, and A. Pescapé, “Mobile encrypted
traffic classification using deep learning: Experimental evaluation,
lessons learned, and challenges,” IEEE Transactions on Network and
Service Management, vol. 16, no. 2, pp. 445–458, 2019.
[264] S. E. Coull and K. P. Dyer, “Traffic analysis of encrypted messaging
services: Apple imessage and beyond,” ACM SIGCOMM Computer
Communication Review, vol. 44, no. 5, pp. 5–11, 2014.
[265] C. V. Wright, L. Ballard, S. E. Coull, F. Monrose, and G. M. Masson,
“Spot me if you can: Uncovering spoken phrases in encrypted voip
conversations,” in 2008 IEEE Symposium on Security and Privacy (sp
2008). IEEE, 2008, pp. 35–49.
[266] M. Conti, L. V. Mancini, R. Spolaor, and N. V. Verde, “Analyzing
android encrypted network traffic to identify user actions,” IEEE
Transactions on Information Forensics and Security, vol. 11, no. 1,
pp. 114–125, 2015.
[267] B. Saltaformaggio, H. Choi, K. Johnson, Y. Kwon, Q. Zhang, X. Zhang,
D. Xu, and J. Qian, “Eavesdropping on fine-grained user activities
within smartphone apps over encrypted network traffic,” in 10th
{USENIX} Workshop on Offensive Technologies ({WOOT} 16), 2016.
[268] F. Yan, M. Xu, T. Qiao, T. Wu, X. Yang, N. Zheng, and K.-K. R.
Choo, “Identifying wechat red packets and fund transfers via analyzing
encrypted network traffic,” in 2018 17th IEEE International Conference
on Trust, Security and Privacy in Computing and Communications/12th
IEEE International Conference on Big Data Science and Engineering
(TrustCom/BigDataSE). IEEE, 2018, pp. 1426–1432.
[269] Y. Wang, N. Zheng, M. Xu, T. Qiao, Q. Zhang, F. Yan, and J. Xu,
“Hierarchical identifier: Application to user privacy eavesdropping on
mobile payment app,” Sensors, vol. 19, no. 14, p. 3052, 2019.
[270] F. Schneider, A. Feldmann, B. Krishnamurthy, and W. Willinger, “Understanding online social network usage from a network perspective,”
in Proceedings of the 9th ACM SIGCOMM Conference on Internet
Measurement, 2009, pp. 35–48.
[271] Y. Feng, “Botflowmon: Identify social bot traffic with netflow and
machine learning,” 2018.
[272] M. Conti, L. V. Mancini, R. Spolaor, and N. V. Verde, “Can’t you
hear me knocking: Identification of user actions on android apps via
traffic analysis,” in Proceedings of the 5th ACM Conference on Data
and Application Security and Privacy, 2015, pp. 297–304.
[273] Y. Zhao, X. Ma, J. Li, S. Yu, and W. Li, “Revisiting website fingerprinting attacks in real-world scenarios: A case study of shadowsocks,” in
International Conference on Network and System Security. Springer,
2018, pp. 319–336.
[274] R. Nithyanand, X. Cai, and R. Johnson, “Glove: A bespoke website
fingerprinting defense,” in Proceedings of the 13th Workshop on
Privacy in the Electronic Society, 2014, pp. 131–134.
[275] A. J. Pinheiro, P. Freitas de Araujo-Filho, J. de M. Bezerra, and
D. R. Campelo, “Adaptive packet padding approach for smart home
networks: A tradeoff between privacy and performance,” IEEE Internet
of Things Journal, vol. 8, no. 5, pp. 3930–3938, 2021.
[276] J. Gong and T. Wang, “Zero-delay lightweight defenses against website
fingerprinting,” in 29th USENIX Security Symposium (USENIX Security
20), 2020, pp. 717–734.
[277] C. V. Wright, S. E. Coull, and F. Monrose, “Traffic morphing: An
efficient defense against statistical traffic analysis.” in NDSS, vol. 9.
Citeseer, 2009.
[278] X. Luo, P. Zhou, E. W. Chan, W. Lee, R. K. Chang, R. Perdisci et al.,
“Httpos: Sealing information leaks with browser-side obfuscation of
encrypted flows.” in NDSS, vol. 11, 2011.
[279] G. Cherubin, J. Hayes, and M. Juárez, “Website fingerprinting defenses
at the application layer.” Proc. Priv. Enhancing Technol., vol. 2017,
no. 2, pp. 186–203, 2017.
[280] Z. Deng, Z. Liu, Z. Chen, and Y. Guo, “The random forest based detection of shadowsock’s traffic,” in 2017 9th International Conference on
Intelligent Human-Machine Systems and Cybernetics (IHMSC), vol. 2.
IEEE, 2017, pp. 75–78.
[281] J. Beznazwy and A. Houmansadr, “How china detects and blocks
shadowsocks,” in Proceedings of the ACM Internet Measurement
Conference, 2020, pp. 111–124.
[282] G. Draper-Gil, A. H. Lashkari, M. S. I. Mamun, and A. A. Ghorbani,
“Characterization of encrypted and vpn traffic using time-related,” in
Proceedings of the 2nd international conference on information systems
security and privacy (ICISSP). sn, 2016, pp. 407–414.

[283] P. Choorod and G. Weir, “Tor traffic classification based on encrypted
payload characteristics,” in 2021 National Computing Colleges Conference (NCCC). IEEE, 2021, pp. 1–6.
[284] I. Goldberg and C. A. Wood, “Network-based website fingerprinting,”
https://datatracker.ietf.org/doc/html/draft-wood-privsec-wfattacks-00,
2019.
[285] “New tor release: Tor 0.4.0.5,” https://blog.torproject.org/
new-release-tor-0405/, 2019, accessed: 2022-02-15.
[286] S. Li, H. Guo, and N. Hopper, “Measuring information leakage in
website fingerprinting attacks and defenses,” in Proceedings of the 2018
ACM SIGSAC Conference on Computer and Communications Security,
2018, pp. 1977–1992.
[287] X. Cai, R. Nithyanand, and R. Johnson, “Cs-buflo: A congestion
sensitive website fingerprinting defense,” in Proceedings of the 13th
Workshop on Privacy in the Electronic Society, 2014, pp. 121–130.
[288] D. Lu, S. Bhat, A. Kwon, and S. Devadas, “Dynaflow: An efficient
website fingerprinting defense based on dynamically-adjusting flows,”
in Proceedings of the 2018 Workshop on Privacy in the Electronic
Society, 2018, pp. 109–113.
[289] S. Henri, G. Garcia-Aviles, P. Serrano, A. Banchs, and P. Thiran, “Protecting against website fingerprinting with multihoming,” Proceedings
on Privacy Enhancing Technologies, vol. 2020, no. 2, pp. 89–110,
2020.
[290] T. Wang, “The one-page setting: A higher standard for evaluating
website fingerprinting defenses,” in Proceedings of the 2021 ACM
SIGSAC Conference on Computer and Communications Security, 2021,
pp. 2794–2806.
[291] mikeperry,
“Experimental
defense
for
website
traffic
fingerprinting,”
https://blog.torproject.org/
experimental-defense-website-traffic-fingerprinting/, 2011, accessed:
2022-02-11.
[292] A. Fotouhi, H. Qiang, M. Ding, M. Hassan, L. G. Giordano, A. GarciaRodriguez, and J. Yuan, “Survey on uav cellular communications: Practical aspects, standardization advancements, regulation, and security
challenges,” IEEE Communications Surveys & Tutorials, vol. 21, no. 4,
pp. 3417–3442, 2019.
[293] J. Whelan, A. Almehmadi, and K. El-Khatib, “Artificial intelligence for
intrusion detection systems in unmanned aerial vehicles,” Computers
and Electrical Engineering, vol. 99, p. 107784, 2022.
[294] K. Kim, J. S. Kim, S. Jeong, J.-H. Park, and H. K. Kim, “Cybersecurity
for autonomous vehicles: Review of attacks and defense,” Computers
& Security, vol. 103, p. 102150, 2021.
[295] K. M. Ali Alheeti and K. McDonald-Maier, “Intelligent intrusion
detection in external communication systems for autonomous vehicles,”
Systems Science & Control Engineering, vol. 6, no. 1, pp. 48–56, 2018.
[296] Y. Feng, J. Li, and T. Nguyen, “Application-layer ddos defense with
reinforcement learning,” in 2020 IEEE/ACM 28th International Symposium on Quality of Service (IWQoS). IEEE, 2020, pp. 1–10.
[297] W. Wang, Y. Shang, Y. He, Y. Li, and J. Liu, “Botmark: Automated
botnet detection with hybrid analysis of flow-based and graph-based
traffic behaviors,” Information Sciences, vol. 511, pp. 284–296, 2020.
[298] M. H. Bhuyan, D. K. Bhattacharyya, and J. K. Kalita, “Network
anomaly detection: methods, systems and tools,” Ieee communications
surveys & tutorials, vol. 16, no. 1, pp. 303–336, 2013.
[299] S. Barnum, “Standardizing cyber threat intelligence information with
the structured threat information expression (stix),” Mitre Corporation,
vol. 11, pp. 1–22, 2012.
[300] OpenAI, “Chatgpt,” 2023, [Online]. Available: https://openai.com/
chatgpt.
[301] A. Nascita, G. Aceto, D. Ciuonzo, A. Montieri, V. Persico, and
A. Pescapé, “A survey on explainable artificial intelligence for internet
traffic classification and prediction, and intrusion detection,” IEEE
Communications Surveys & Tutorials, 2024.
[302] D. Han, Z. Wang, W. Chen, Y. Zhong, S. Wang, H. Zhang, J. Yang,
X. Shi, and X. Yin, “Deepaid: Interpreting and improving deep
learning-based anomaly detection in security applications,” in Proceedings of the 2021 ACM SIGSAC Conference on Computer and
Communications Security, 2021, pp. 3197–3217.
[303] S. M. Lundberg and S.-I. Lee, “A unified approach to interpreting
model predictions,” Advances in neural information processing systems,
vol. 30, 2017.
[304] M. T. Ribeiro, S. Singh, and C. Guestrin, “” why should i trust you?”
explaining the predictions of any classifier,” in Proceedings of the 22nd
ACM SIGKDD international conference on knowledge discovery and
data mining, 2016, pp. 1135–1144.

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

38

[305] G. Plumb, D. Molitor, and A. S. Talwalkar, “Model agnostic supervised local explanations,” Advances in neural information processing
systems, vol. 31, 2018.
[306] V. Belle and I. Papantonis, “Principles and practice of explainable
machine learning,” Frontiers in big Data, p. 39, 2021.
[307] U. Bhatt, A. Xiang, S. Sharma, A. Weller, A. Taly, Y. Jia, J. Ghosh,
R. Puri, J. M. Moura, and P. Eckersley, “Explainable machine learning
in deployment,” in Proceedings of the 2020 conference on fairness,
accountability, and transparency, 2020, pp. 648–657.
[308] Y. Feng, J. Xu, and L. Weymouth, “University blockchain research
initiative (ubri): Boosting blockchain education and research,” IEEE
Potentials, vol. 41, no. 6, pp. 19–25, 2022.

Cong Wu is currently a research fellow at School of
Computer Science and Engineering, Nanyang Technological University, Singapore. He received Ph.D.
degree at School of Cyber Science and Engineering,
Wuhan University in 2022. His research interests
include AI system security and Web3 security. His
research outcomes have appeared in USENIX Security, ACM CCS, IEEE TDSC, TIFS.

Yebo Feng is a research fellow in the College of
Computing and Data Science (CCDS) at Nanyang
Technological University (NTU). He received his
Ph.D. degree in Computer Science from the University of Oregon (UO) in 2023. His research interests
include network security, blockchain security, and
anomaly detection. He is the recipient of the Best
Paper Award of 2019 IEEE CNS, Gurdeep Pall
Graduate Student Fellowship of UO, and Ripple
Research Fellowship. He has served as the reviewer
of IEEE TDSC, IEEE TIFS, ACM TKDD, IEEE
JSAC, IEEE COMST, etc. Furthermore, he has been a member of the
program committees for international conferences including SDM, CIKM,
and CYBER, and has also served on the Artifact Evaluation (AE) committees
for USENIX OSDI and USENIX ATC.

Chong Wang received the bachelor’s and PhD
degrees from Fudan University, in 2018. He is
currently a research fellow at Cyber Security Laboratory, Nanyang Technologicai University. His research interests lie in the crossroads between artificial intelligence and software engineering. His overarching research mission revolves around enhancing
both productivity and security within the realm of
software development. He has published multiple
papers in international journals and conferences,
such as the IEEE Transactions on Software Engineering (TSE), ACM Transactions on Software Engineering and Methodology
(TOSEM), ACM Symposium on the Foundations of Software Engineering
(FSE), IEEE/ACM International Conference on Automated Software Engineering (ASE) and IEEE International Conference on Software Analysis,
Evolution and Reengineering (SANER).

Jun Li is a professor in the Department of Computer
Science and director of the Network and Security
Research Laboratory at the University of Oregon. He
was also a Ripple Fellow, Narus Research Fellow,
and founding director of the Center for Cyber Security and Privacy at the University of Oregon. He has
received the CAREER Award from the US National
Science Foundation, the Faculty Excellence Award
from the University of Oregon, and the Recognition
of Service Award from ACM. He received his Ph.D.
with honors from UCLA in 2002. His research interests include networking, distributed systems, cybersecurity, and blockchain.
He has published more than 100 peer-reviewed papers, including several Best
Paper awards.

Jelena Mirkovic is Research Team Leader at USC
Information Sciences Institute and Research Associate Professor of Computer Science at USC. During
her professional career she published more than 100
conference and journal papers, and the first book on
the denial-of-service attacks. She also pioneered use
of testbeds in cybersecurity education. Her research
interests span cybersecurity, networking and education.

Hao Ren was a Research Fellow at Nanyang Technological University, Singapore. He received his
Ph.D. degree in Dec. 2020 from the University of
Electronic Science and Technology of China. He
was a visiting Ph.D. student at the University of
Waterloo from Dec. 2018 to Jan. 2020. He has
published papers in major conferences/journals, including ACM ASIACCS, ACSAC, IEEE TCC, and
IEEE Network. He won the Best Paper Award from
IEEE BigDataSecurity 2023. His research interests
include applied cryptography and privacy-preserving
machine learning.

Jiahua Xu is Associate Professor in Financial
Computing, and Programme Director of the MSc
Emerging Digital Technologies at UCL. She is also
affiliated to the UCL Centre for Blockchain Technologies. Her research focuses on blockchain economics and decentralized finance. She has published
in Usenix Security, ACM IMC, FC, IEEE ICDCS
and IEEE ICBC. She has reviewed for Advances
in Complex Systems, Computer Networks, Transactions on the Web and Cities.

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Communications Surveys & Tutorials. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/COMST.2025.3545541

39

Yang Liu is currently a full professor and the
director of the cyber security lab in Nanyang Technological University, Singapore. He specializes in
software security, verification, software engineering
and artificial intelligence. His research has bridged
the gap between the theory and practical usage of
formal methods and program analysis to evaluate
the design and implementation of software for high
assurance and security. His work led to the development of state-of-the-art model checker, Process
Analysis Toolkit (PAT). By now, he has more than
200 publications and 6 best paper awards in top tier conferences and journals.
With more than 50 million Singapore dollar funding support, he is leading a
large research team working on state-of-the-art software engineering and cyber
security problems and currently serving as an associated editor of TIFS.

Authorized licensed use limited to: University College London. Downloaded on March 27,2025 at 15:11:56 UTC from IEEE Xplore. Restrictions apply.
© 2025 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
