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
# [033] How far can we push flow analysis to identify encrypted anonymity network traffic?
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
编号：033
题名：How far can we push flow analysis to identify encrypted anonymity network traffic?
年份：2018
DOI：10.1109/noms.2018.8406156
来源：NOMS 2018 - 2018 IEEE/IFIP Network Operations and Management Symposium
PDF：paper/10.1109_noms.2018.8406156.pdf
已有粗分类：加密流量分类与应用识别
二级关联：无
相关性：强相关，分数 16
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\033.txt
- 原始字符数：33798
- 本次发送字符数：33798
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
How Far Can We Push Flow Analysis to Identify
Encrypted Anonymity Network Traffic?
Khalid Shahbar
A. Nur Zincir-Heywood
Faculty of Computer Science
Dalhousie University
Halifax, Canada
{Shahbar, Zincir}@ cs.dal.ca
Abstract— Anonymity networks provide privacy to the users
by relaying their data to multiple destinations in order to reach
the final destination anonymously. Multilayer of encryption is
used to protect the users’ privacy from attacks or even from the
operators of the stations. In this research, we showed how flow
analysis could be used to identify encrypted anonymity network
traffic under four scenarios: (i) Identifying anonymity networks
compared to normal background traffic; (ii) Identifying the type
of applications used on the anonymity networks; (iii) Identifying
traffic flow behaviors of the anonymity network users; and (iv)
Identifying / profiling the users on an anonymity network based
on the traffic flow behavior. In order to study these, we employ a
machine learning based flow analysis approach and explore how
far we can push such an approach.
Keywords— Dataset; Tor; I2P; JonDonym; Traffic Flow;
Anonymity

I.

INTRODUCTION

Anonymity networks aim to provide the users with some
level of privacy. These networks enable the users on the Internet
to freely access websites or run applications on the Internet
without revealing their identity to any site that observes the
network. In addition, anonymity networks hide the users’
identity from the final destination (web server). Some of the
most used and known anonymity networks are Tor [1],
JonDonym [2], and I2P [3].
Anonymity networks (services) have much in common in
more than one aspect. They provide services to the users on the
Internet while keeping their identity hidden. In addition, most of
the time, anonymity services provide anonymity to the users by
forwarding the users’ traffic through multiple stations until the
users' data reach to their destination. During this journey, the
data are encrypted multiple times. This way, the users’ data stay
anonymous where each station during the journey knows only
part of the information. Therefore, it becomes difficult to trace
the users’ data in these networks.
At the same time, these networks have differences between
them. They differ in the design; this includes how the data is
forwarded between the stations, the type of the encryption used,
the way to manage the networks, the protocol to select the
stations, the operators of the stations, and other details regarding
the design. On the other hand, these networks have different
goals under the design and different supported applications
within the networks. For example, the anonymity networks
could be designed specifically to browse the Internet websites
anonymously. Others could be designed to be a private network

that users trade information internally. Such a network is not
optimized to browse Internet web sites. The supported
applications on these networks are different, such as browsing,
file sharing, IRC, web hosting, etc. One type of difference is the
operators of the networks; some anonymity networks count on
volunteers to provide the service to the users. Others use
companies to provide the service. In addition, the threat models
of these networks are not the same based on their design. What
could be a threat to one of these networks might not form any
threat to the others.
Tor [1] [15], JonDoNym [2] and I2P [3] are the three wellknown anonymity networks that we included on the proposed
data set. Tor provides the users with anonymity by passing the
traffic through three stations (nodes). These nodes run by
volunteers shared their bandwidth with the anonymity network.
The selection of these nodes is done by a protocol called path
selection protocol. The users get the list of the currently
available nodes on the networks from directory authorities
servers. The path that the users use is not fixed, it continuously
keeps changing. The user has the option to define the first or the
last node on the path instead of counting on the path selection
protocol to select the nodes.
JonDonym provides anonymity service to the users by
passing the traffic through multiple stations (Mixes). The path
(cascade) on the JonDonym network is fixed. The user can select
the cascade that will relay the traffic but cannot change the
mixes on the path. This is due to the difference in design of the
anonymity networks. The mix on the JonDonym network
multiplexes traffic from different users and sends it to the next
mix on the cascade.
The Invisible Internet Project (I2P) is a packet switched
network that uses multilayer encryption to provide anonymity to
its users. The path (Tunnels) on the I2P network is
unidirectional. The user builds an encrypted tunnel to the final
destination to send messages using the created tunnel (outbound
tunnel). The messages travel in one direction only; therefore,
messages from destination to the sender must use another tunnel
(inbound tunnel). Tunnels on the I2P networks are used for
communication and management. By default, the users on the
I2P network share bandwidth by participating on building I2P
Tunnels. The user has the option to reduce or increase the
amount of participation on building I2P Tunnels.
The connection between the user and any of these anonymity
networks is not hidden. These networks aim to provide
anonymity to the user, but they do not hide that the user is

978-1-5386-3416-5/18/$31.00©2018 Crown

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:05:50 UTC from IEEE Xplore. Restrictions apply.

connecting to such anonymity network. Therefore, blocking
these anonymity networks is possible. Thus, Tor employed
different obfuscation techniques (Pluggable Transports) to hide
the connection to the Tor network. The implemented pluggable
transports are Scramblesuit [9], Flashproxy [10], Obfs3 [11],
Meek [12], Format-transforming encryption (FTE) [13].
Furthermore, JonDonym offers two options to resist the network
blockage: TCP/IP forward and Skype tunnel. Both could be used
to connect the user to the JonDonym network if the network is
blocked. On the I2P network, the obfuscation options are
considered but not implemented yet.
Anonymity networks have differences in the design, the
applications they support, the main goal of the network and how
the network resists censorship. In addition, the encryption
employed in anonymity networks prevents using payload
analysis to perform traffic analysis. On the other hand, flow
analysis deals with statistical information extracted from the
header of the traffic without the need to deal with the encryption.
Therefore, in this paper, we explore the boundaries of flow
analysis employment in anonymity network analysis.
The rest of this paper is organized as follows. Related work
is reviewed in Section II. The Anon17 data set and the flow
analysis approach used in this research are discussed in Section
III. Section IV presents the use of flow analysis to identify
anonymity networks. Section V presents the analysis of
identifying the type of application on the anonymity network
traffic. Whereas Section VI presents the analysis for identifying
the traffic flows of users as well as user profiles. Finally,
conclusions are drawn, and the future work is discussed in
Section VII.
II.

RELATED WORK

Flow analysis is applied in many researches to solve
different types of problems. One of the applications of using
flow analysis is encrypted traffic classification. Anonymity
networks traffic is based on multiple layers of encryption.
Therefore, flow analysis is studied to identify anonymity
networks. Barker et al. [8] collected Tor data using a simulated
environment. The goal of their research is to study the possibility
to differentiate between encrypted traffic and Tor traffic. The
data included HTTP and HTTPS traffic over the simulated Tor
network and HTTPS traffic. NetAI was used to export flows
from the captured traffic. The exported flows were analyzed
using three machine learning algorithms namely, Random
Forest, J4.8, and Adaboost. The result showed that it is possible
to differentiate between Tor and encrypted traffic with more
than 90% accuracy.
Machine learning algorithms are also used to identify the
type of application running anonymously on an anonymity
network. Alsabah et al. [17] used Naïve Bayes, Bayesian
Networks, and Decision Tree algorithms to classify the
application used by Tor’s users. The applications are Browsing,
Streaming and BitTorrent. Given that Tor traffic is encrypted,
they used the circuit level and the cell level information to do
the classification. The circuit level information included the
circuit lifetime and the amount of data transferred by the circuit.
The cell level information included the cells inter arrival time
and their statistics. The classification included online and offline
classification. The online classification used the cell level

information to classify the circuit while it is in use. The offline
classification used both the cell and the circuit level information
to classify the circuit. In terms of accuracy, the best result they
achieved in the offline classification was 91%, whereas the best
results achieved in the online classification was 97.8%.
In terms of the data set used on anonymity networks studies,
researches in this filed used simulation environments to generate
the data or collected the data from the anonymity network. Bauer
et al. [7] presented a Tor network emulation tool, namely
ExperimenTor. The tool provides a test environment for the Tor
researchers by modeling Tor routers, bandwidth, users, and
applications. The ExperimenTor tool is available as standalone
and a VMware image that has the tool installed and configured.
There are many other researches on Tor, JonDonym, and I2P
anonymity networks [16] [17] [18] [19] where researchers used
their own data to conduct their research. In this work, we also
collect our own data on three anonymity tools, namely Tor,
JonDonym, and I2P. Furthermore, we make this dataset,
Anon17, publicly available for further research.
III. DATASET AND FLOW ANALYSIS
Flow analysis calculates statistical information extracted
from the header of the packet to describe the communication
between two parties. The following sections describe how the
anonymity network data was collected and the flow exporter tool
was used to generate the flows.
A. Anon17
There are many studies conducted on these anonymity
networks. The researches include a wide range of aspects related
to the anonymity field such as improving the design, performing
attacks on the anonymity network, analyzing the users’ behavior
on the anonymity network, studying the performance and delay,
revealing the users’ identity, and many others.
In some of the anonymity researches, the used data are
collected in a simulated environment. Others used real data
collected by the researchers themselves. The most common
issue that faces researchers in the anonymity field is that these
anonymity networks provide anonymity to the users; thus,
collecting the data and making it publicly available might affect
the privacy of users of the anonymity tools. Therefore, the
researches on the anonymity field count on data collected from
a simulated environment or collected by the researchers
themselves.
Anon17 [14] is the dataset we used in this work to identify
anonymity networks. Anon17 is collected at the NIMS lab [6]
between 2014-2017 in a real network environment. The dataset
is labeled based on the information that we could extract from
the anonymity networks while collecting the data. For example,
in the Tor network, the IP addresses of the Tor nodes are
available. Therefore, whenever we collect data related to a node
on the Tor network, we use the IP address to label this traffic as
“Tor”. The same applies for all the labeling in our data as
detailed below. We did not use any application classification
tools to label our data. Instead, we used the ground-truth that we
know to label all the traffic in Anon17. The port number was
used only to label the background traffic collected by other
research group. The background traffic was classified into

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:05:50 UTC from IEEE Xplore. Restrictions apply.

multiple applications / protocols to investigate the ability to
distinguish between the anonymity traffic and different
background application.
Anon17 contains data for three popular and well-known
anonymity networks: Tor, JonDonym, and I2P. We provide
these data and make it publicly available without affecting the
privacy of the users. To this end, the IP addresses of the users
have been removed. The payload information only used for
statistical measurement and then are removed. This is because
we aim to provide a publicly available anonymity dataset that
could be used to study the aforementioned anonymity tools. The
dataset includes several applications used on these anonymity
networks and also includes several obfuscation techniques that
are used on some of these networks. Therefore, the dataset could
be used for multiple types of researches.
The following details the content of Anon17 used in this
paper and our previous works:
1) Tor
The Tor dataset contains Tor traffic. The traffic includes the
circuit establishment and the user activities on the Tor network
such as browsing the Internet websites. The Tor traffic does not
include any obfuscated traffic. The data collected from multiple
machines in NIMS labs while using Tor to browse Internet web
pages.
2) TorApp
The TorApp dataset contains flows for three machines
(computers) running three applications on the Tor network
(Browsing, Video streaming, and File sharing). Therefore, there
are three classes on the TorApp dataset (Browsing, streaming,
and BitTorrent). The Browsing class contains connection flows
between a user and an entry node on the Tor network when the
user is using Tor to browse different Internet websites. The
Streaming class is the connection flows between the user and the
entry node when the user is watching videos on Tor. The last
class, the BitTorrent class contains flows between the user and
the first node when the user is using Torrent files on the Tor
network
3) TorPT
The TorPT dataset contains flows for Tor pluggable
transports. The TorPT has five classes: Obfs3, Meek,
Flashproxy, FTE, and Scramblesuit. The TorPT is collected by
connecting to the pluggable transports form the NIMS lab and
capture the traffic. The Obfs3 is collected from two different
Obfs3 bridges. The Scramblesuit traffic is collected by
connecting to 22 different Scramblesuit servers. This is to ensure
that we include the effect of changing the flow behavior that
Scramblesuit pluggable transport aims to achieve.
4) I2PApp80BW
These traffic flows are collected while running three
applications on the I2P network. The applications (classes) are
Eepsites (the websites browsing on the I2P network), jIRCii
(Internet Relay Chat (IRC) plugin on the I2P network), and
I2Psnark (the file sharing plugin on the I2P network). The
bandwidth sharing on the I2P client is set to default which is
80% sharing rate of the user bandwidth. In this dataset, each
class contains the application flows in addition to the
management traffic flows. For example, the Eepsites flows

contain flows for the Eepsites Tunnels in addition to the Tunnels
used for the management of the I2P network and tunnels used to
share bandwidth such as the Exploratory and the Participating
Tunnels.
5) I2PApp0BW
This dataset is similar to the I2Papp80BW; the difference is
that the amount of shared bandwidth is set to 0%. This will
reduce the amount of management traffic flows on each class.
6) I2PUsers
This dataset contains the traffic flows for three users on the
I2P network. The classes are named PC1, PC2, and PC3. The
dataset I2PUsers is the same dataset used in I2PApp80BW. The
difference is that the data is classified differently. Instead of
labeling the dataset based on the application; the dataset is
labeled based on the user traffic. Therefore, any class on this
dataset will contain the three applications used on the
I2Papp80BW dataset. For example, the PC1 flows contain
flows for the machine of the first users when the users used
Eepsites, jIRCii, and I2Psnark on the I2P network.
7) I2PApp
This dataset contains traffic flows for the same three
applications used in I2PApp80BW. The difference is that this
dataset contains separate classes for the management tunnels.
The total number of classes on this dataset is five: Eepsites,
jIRCii, I2Psnark, Exploratory Tunnels, and Participating
Tunnels. Therefore, the application tunnels do not contain any
management tunnels flows.
8) JonDonym
The JonDonym dataset contains traffic flows for the
JonDonym network as well as traffic flows for the whole free
mixes in the JonDonym network [14].
B. Flow Exporter
We used Tranalyzer [4] to extract the flows from the PCAP
files we captured in the NIMS lab. Tranalyzer has 92 features
based on the plug-ins used such as Number of bytes sent,
Number of bytes received, Statistics about the Inter-arrival time,
and Number of connection etc. Some of the unrelated features
are removed from the dataset such as the ICMP features and
VLAN features because they do not provide useful information
for our purposes. IP addresses and payloads of the packets are
also removed from the dataset to protect the privacy of the users.
In the dataset, the values of some features might have zeros. For
example, the I2P network works on both TCP and UDP.
Therefore, if the I2P data set contains UDP connections then all
the TCP related features will have zero values.
Tranalyzer has both the flow exporter and the flow collector
integrated into the Tranalyzer. Figure 1. Shows the setup for
collecting the data in Anon17.
The data is formatted into arff file format used in the open
source data mining software tool, Weka [5]. Table I summarizes
the features included in Anon17 dataset.

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:05:50 UTC from IEEE Xplore. Restrictions apply.

IV. IDENTIFYING ANONYMITY NETWORKS

Fig. 1. Anon17 Flow Analysis.
TABLE I.

ANON17 DATASET FEATURES

Features

Description

dir time_first, time_last, duration

Flow direction, time, and
duration of the flow

numPktsSnt numPktsRcvd
numBytesSnt numBytesRcvd
minPktSz maxPktSz avePktSize pktps
bytps pktAsm
bytAsm

Counting of Packets and
Bytes

ip_mindIPID ip_maxdIPID ip_minTTL
ip_maxTTL ip_TTL_Chg ip_TOS
ip_flags ip_Opt ip_OptCnt

The IP Header related
features such as TOS, TTL
etc.

TABLE II.

RESULTS FOR JONDONYM FLOW ANALYSIS.

JonDoNym

TP Rate
0.997

FP Rate
0

Precision
1

F-Measure
0.998

BackGround

1

0.003

1

1

LBNL/ICSI

tcp_PSeqCnt tcp_SeqSntBytes
tcp_SeqFaultCnt tcp_PAckCnt
tcp_FlwLssAckRcvdBytes
tcp_AckFaultCnt tcp_InitWinSz
tcp_AveWinSz tcp_MinWinSz
tcp_MaxWinSz tcp_WinSzDwnCnt
tcp_WinSzUpCnt
tcp_WinSzChgDirCnt tcp_AggrFlags
tcp_AggrAnomaly tcp_AggrOptions
tcp_MSS tcp_WS tcp_OptCnt tcp_SSA/SA-A_Trip tcp_S-SA-A/A-A_RTT
tcp_RTTAckTripMin
tcp_RTTAckTripMax
tcp_RTTAckTripAve tcpStates

The TCP Header related
features such as Window
size, sequence number etc.

connSrc connDst connSrc<->Dst

Counting of number of
connections between source
and destination/ source to
different destinations.

min_pl max_pl mean_pl
low_quartile_pl median_pl
upp_quartile_pl iqd_pl mode_pl
range_pl std_pl stdrob_pl skew_pl
exc_pl

In this section, the flow analysis is used to identify an
anonymity network among different background traffic. The
selected anonymity network to be studied using flow analysis in
this section is JonDonym. The JonDonym data employed in this
analysis is the JonDonym part from the Anon17 dataset. The
data of JonDonym are collected from three machines at NIMS
lab by connecting to all the free cascades on the JonDonym
network. For a background traffic, LBNL/ICSI [20] data set are
employed as the background traffic. It contains network traces
collected from more than 100 hours of activities for several
thousands of hosts. The data size is 11 GB. The data are publicly
available in a PCAP form. The data are distributed over several
small PCAP files. For this analysis, a total of 211,370 flows are
extracted from around 1.5 GB. Table II shows the result of the
JonDonym traffic with the background traffic. The results show
that JonDonym flows can be distinguished from background
traces with a high accuracy level (99.99%).

Packet length statistics

min_iat max_iat mean_iat
low_quartile_iat median_iat
upp_quartile_iat iqd_iat mode_iat
range_iat std_iat stdrob_iat skew_iat
exc_iat nfp_pl_iat ps_iat_histo

Inter arrival time statistics

TrafficType

The classes

Accuracy

99.99%

The next part of the analysis is performed by labeling the
background data to application/protocol names based on the port
number. The background data contains a vast number of
applications and protocols. Some of the application or the
protocols appear just a few times while others have a high
number of appearances in the data. Therefore, the top appeared
applications on the data are labeled with their application name,
the rest are labeled as others. Thus, instead of having one class,
namely background, the data will have 12 classes namely,
HTTP, HTTPS, IMAPS, SNMP, NetBIOS-SSN, DNS, POP3,
LPD, EPMAP, SMTP, SSH, and other. Table III shows the
results of the applications and JonDonym analysis. The results
dropped by 2% compared to the previous analysis where all the
background traffic flows were grouped into one class.
V.

IDENTIFYING THE OBFUSCATED ANONYMITY
NETWORK TRAFFIC

The flow analysis could be used to explore the behavior of
the anonymity network when anti-censorship techniques are
used on these networks. Tor pluggable transports systems work
to provide access to the Tor network in adversarial (censorship)
environments. Most of the pluggable transports tools
concentrate on hiding the content of the packets in a way that
makes it hard for the adversaries when using deep packet
inspection (DPI) to detect the connection to the bridges. But DPI
is not the only method used to detect Tor traffic. The active
probing and the flow analysis are some of the other popular
methods used to detect Tor traffic. In our previous analysis [21],
we demonstrated the resistance of Tor pluggable transports

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:05:50 UTC from IEEE Xplore. Restrictions apply.

against network traffic flow analysis techniques. Table IV shows
the result of the flow analysis of Tor pluggable transports with
different background traffic from our previous works. The
pluggable transport traffic includes FTE, Scramblesuit, Meek,
Flashproxy, and Obfs3. The pluggable transports related traffic
could be found in the Anon17 datasets, under TorPT. The
background traffic includes HTTP, HTTPS, SSH, BitTorrent,
and Encrypted BitTorrent. In this case, the results show 97%.
TABLE III.

RESULTS OF APPLICATIONS AND JONDONYM FLOW
ANALYSIS
TP Rate

FP Rate

0.986
0.897
0.88
0.998
0.974
0.997
0.982
0.998
0.993
0.948
0.455
0.973
0.999

0.013
0.004
0.001
0.000
0.002
0.000
0.000
0.000
0.000
0.000
0.000
0.006
0.000

HTTP
HTTPS
IMAPS
SNMP
NETBIOS-SSN
DNS
POP3
LPD
EPMAP
SMTP
SSH
OTHER
JonDonym
Accuracy

TABLE IV.

Precision

F-Measure

0.981
0.919
0.900
0.996
0.971
0.998
0.969
0.998
0.988
0.961
0.613
0.976
1.000
97.99%

0.984
0.908
0.888
0.997
0.972
0.998
0.975
0.998
0.990
0.955
0.522
0.974
1.000

three computers to connect to our configured node on the Tor
network and collected the flow of these three applications. The
flow analysis is then employed to identify the type of
application running on the Tor network. The flows are extracted
using both Tranalyzer and Tcptrace. Four machine learning
algorithms namely C4.5, Naïve Bayes, Random Forest, and
Bayesian Network are used in the analysis of these three
applications. Table IV shows the results of the four classifying
algorithms for the two employed flow exporters. The accuracy
is between 92% - 99% based on the machine learning algorithm
and the flow exporter used. Table V shows the results of the
Tranalyzer flow analysis against different background traffic.
The flows of the three applications on Tor are included in
Anon17 and called TorApp.
TABLE V.
RESULTS FOR THE FLOW ANALYSIS OF TOR PLUGGABLE
TRANSPORTS AGAINST DIFFERENT BACKGROUND TRAFFIC
Class

Background
Traffic

Pluggable
Transports

APPLICATIONS ANALYSIS ON THE TOR NETWORK

Traffic
Classifier
TRANALYZER2

Bayes net
Naïve Bayes
C4.5
Random Forest

TCPTRACE

Bayes net
Naïve Bayes
C4.5
Random Forest

Accuracy

F-Measure
Browsing

Streaming

BitTorrent

99.2%

0.99

0.99

1

93.3%

0.98

0.90

0.93

97.2%

0.96

0.98

0.98

98.8%

0.99

0.98

0.99

97.7%

0.98

0.97

0.99

92.2%

0.96

0.89

0.92

96.1%

0.96

0.95

0.98

97.7%

0.99

0.96

0.98

VI. IDENTIFYING APPLICATIONS ON ANONYMITY
NETWORKS

The flow analysis could be used to identify the applications
on the anonymity networks. In our previous works, we studied
the possibility to identify the application on two well-known
anonymity networks (Tor [1] and I2P [3]). The following
sections show the finding on identifying applications on
anonymity networks.
A. Applications Classification on the Tor Network
Browsing, Video streaming, and BitTorrent are the three
applications we studied in our previous work [21]. We set up

Overall
Correctly
Classified
Instances

HTTP
HTTPS
SSH
BT
BTecr
FTE
Scramble
suit
Meek
Flash
proxy
Obfs3

TP
Rate
%

FP
Rate
%

Precision
%

FMeasure
%

99
94
99
94
89
99

0.1
0
0
2.5
0.9
0

99
95
99
84
96
99

99
95
99
89
92
99

98

0.1

92

95

99

0

99

99

99

0.1

99

99

99

0

99

99

97%

B. Bandwidth and Applications Analysis on the I2P
Network.
I2P network uses unidirectional tunnels for the outgoing and
incoming traffic. The default setting on the I2P network enables
bandwidth participations. This means that users on the I2P
networks share their bandwidth to build tunnels that could be
used by other I2P’s users. The default setting is 80% bandwidth
participating. In our previous work [22], we studied the effect of
sharing bandwidth on the anonymity of I2P network using the
flow analysis. We set up three machines to connect to the I2P
network and collect data. Browsing, File downloading, and IRC
are the three applications each machine run while collecting the
data. The data is included in Anon17 and called I2P80BW. The
bandwidth participation is then disabled, and the threeapplications data collection is repeated. In Anon17, this part is
called I2P0BW. The accuracy when using the flow analysis for
the applications classification on the I2P networks shows low
accuracy when the bandwidth participation is high. On the other
hand, when the bandwidth participation is disabled, then the
accuracy improved. The labeling in the I2P80BW and I2P0BW
ignores that the tunnels on the I2P are used for data and also for
managing the network. Therefore, the flows for any of the three
applications are not pure application flows but also includes
flows that belong to the management of the network. Therefore,

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:05:50 UTC from IEEE Xplore. Restrictions apply.

another experiment is conducted to collect data from the same
three machines and for the same three applications where the
management tunnels are separated from the data. This part of the
data is called I2Papp. It contains five classes, three for the
applications and two for the management part as explained in
our previous work [22].
C. User Profiling on the I2P network
The same data used in section B is used to study flow
analysis for profiling users on the I2P network. Instead of
labeling the data based on the applications, the data is labeled
based on the machine. In this set of experiments, each machine
represents a different user. The I2PUsers in Anon17 represents
the data for user profiling we used explore how far user profiling
can be pushed on the I2P network. I2PUsers contains three
classes, one for each machine. Table VI shows the results when
using the flow analysis for both applications classification and
users profiling when the bandwidth participating is disabled.
TABLE VI.

APPLICATIONS CLASSIFICATION AND USERS PROFILING ON
THE I2P NETWORKS

Traffic Profiling
Traffic Profiling – TCP Only
Traffic Profiling – UDP Only
User Profiling
User Profiling – TCP Only
User Profiling – UDP Only

VII.

Number of
Instances
195,081
40,075
155,006
195,081
40,075
155,006

Accuracy (%)
73.7
65.6
75.7
66.7
81.7
63.2

CONCLUSION AND FUTURE WORK

In this paper, we showed the potential of using the flow
analysis and its applications on the identification of the
anonymity networks. The flow analysis has high accuracy in
identification of the encrypted anonymity networks. We
employed the flow analysis in three main categories: (i)
identifying the anonymity networks and the ability to
differentiate any encrypted traffic from encrypted anonymity
networks traffic; (ii) identifying the obfuscated anonymity
network traffic within the encrypted traffic; and (iii) applications
profiling using the flow analysis. In our experiments, the
accuracy varies based on the applications, the anonymity
network, and the user’s configuration when using the anonymity
network. Furthermore, Anon17 is presented in this paper and
made publicly available. Anon17 contains the traffic samples for
three anonymity networks: Tor, JonDonym, and I2P. For future
work, we will expand Anon17 to include additional applications
running on these anonymity networks.
REFERENCES
[1]

R. Dingledine, N. Mathewson, and P. Syverson, “Tor: the secondgeneration onion router,” in Proceedings of the 13th conference on
USENIX Security Symposium - Volume 13. USENIX Association, 2004,
pp. 21–21.

[2]

Project: AN.ON – Anonymity [Online]. Available: http://anon.inf.tudresden.de/index_en.html.
[3] The Invisible Internet Project (I2P) [Online]. Available:
https://geti2p.net/en/
[4] TRANALYZER2 [Online]. Available: http://tranalyzer.com/
[5] M. Hall, E. Frank, G. Holmes, B. Pfahringer, P. Reutemann, and I.
Witten,”The WEKA data mining software: an update,” SIGKDD
Explorations, vol. 11, no. 1, pp. 10-18, 2009.
[6] NIMS: Network Information Management and Security Group [Online].
Available: https://projects.cs.dal.ca/projectx/
[7] K. Bauer, M. Sherr, D. McCoy, D. Grunwald, “ExperimenTor: a testbed
for safe and realistic tor experimentation,” in Proceedings of the 4th
conference on Cyber security experimentation and test, p.7-7, August 08,
2011, San Francisco, CA
[8] J. Barker, P. Hannay, and P. Szewczyk, "Using traffic analysis to identify
the second generation onion Router," in the 9th IFIP International
Conference on embedded and ubiquitous computing, Melbourne, AUS,
2011, pp.72-78.
[9] P. Winter, T. Pulls, and J. Fuss. “ScrambleSuit: A Polymorphic Network
Protocol to Circumvent Censorship,” In Workshop on Privacy in the
Electronic Society, Berlin, Germany, 2013. ACM.
[10] D. Fifield, N. Hardison, J. Ellithrope, E. Stark, R. Dingledine, D. Boneh,
and P. Porras, “Evading Censorship with Browser-Based Proxies,” In
PETS, 2012.
[11] Obfs3. [Online]. Available: https://gitweb.torproject.org/pluggabletransports/obfsproxy.git/tree/doc/obfs3/obfs3-protocol-spec.txt
[12] Meek.
[Online].
Available:
https://trac.torproject.org/projects/tor/wiki/doc/meek
[13] K. Dyer, S. Coull, T. Ristenpart and T. Shrimpton, “Protocol
Misidentication Made Easy with Format-Transforming Encryption,"
ACM SIGSAC Conference on Computer and Commu- nication Security,
CCS'13, pp. 61-72, ACM, 2013.
[14] Anon17: Anonymity Networks Dataset. [Online]. Available:
https://web.cs.dal.ca/~shahbar/data.html
[15] Tor
project:
Anonymity
online.
[Online].
Available:
https://www.torproject.org/
[16] A. Chaabane, P. Manils and M. A. Kaafar, "Digging into Anonymous
Traffic: A Deep Analysis of the Tor Anonymizing Network," 2010 Fourth
International Conference on Network and System Security, Melbourne,
VIC, 2010, pp. 167-174.
[17] M. AlSabah, K. Bauer, and I. Goldberg, “Enhancing Tor’s performance
using real-time traffic classification,” in Proceedings of the 2012 ACM
conference on Computer and communications security, Raleigh, USA,
2012, pp. 73-84.
[18] B. Westermann, D. Kesdogan, “Malice versus AN.ON: possible risks of
missing replay and integrity protection,” in Proceedings of the 15th
international conference on Financial Cryptography and Data Security,
2011, Gros Islet, St. Lucia.
[19] P. LIU, L. WANG, Q. TAN, Q. LI, ,X. WANG, and J. SHI, “Empirical
Measurement and Analysis of I2P Routers”. Journal of Networks, North
America, 9, sep. 2014.
[20] Ruoming Pang, Mark Allman, Vern Paxson, and Jason Lee, “The devil
and packet trace anonymization,” ACM SIGCOMM Computer
Communication Review, 36(1):29{38, 2006.
[21] K. Shahbar, and A. N. Zincir-Heywood, “Benchmarking two techniques
for Tor classification: Flow level and Circuit level classification,”. in
IEEE Symposium on Computational Intelligence in Cyber Security, 2014.
[22] K. Shahbar, and A. N. Zincir-Heywood, “Effects of shared bandwidth on
anonymity of the I2P network users,” In 38th IEEE Symposium on
Security and Privacy Workshops, 2nd International Workshop on Trafic
Measurements for Cybersecurity (WTMC 2017), May 2017.

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:05:50 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
