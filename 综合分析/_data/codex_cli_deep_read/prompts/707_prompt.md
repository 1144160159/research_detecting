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
# [707] HTTP/2 DoS Attacks in 5G Networks: Impact Analysis and Anomaly Detection
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
编号：707
题名：HTTP/2 DoS Attacks in 5G Networks: Impact Analysis and Anomaly Detection
年份：2026
DOI：10.1109/tmc.2026.3657143
来源：IEEE Transactions on Mobile Computing
PDF：paper/10.1109_TMC.2026.3657143.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：恶意流量、暗网与攻击检测、入侵检测与网络异常检测
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\707.txt
- 原始字符数：73977
- 本次发送字符数：73977
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 7, JULY 2026

10061

HTTP/2 DoS Attacks in 5G Networks: Impact
Analysis and Anomaly Detection
Nathalie Wehbe , Member, IEEE, Hyame Assem Alameddine , Member, IEEE, and Chadi Assi , Fellow, IEEE

Abstract—Fifth Generation (5G) and beyond networks rely on
the HTTP/2 protocol for signaling between core Network Functions (NFs). While HTTP/2 vulnerabilities have been exploited to
perform various types of Denial of Service (DoS) attacks in web environments, their impact on telecommunication networks remains
under-studied. Though secure by design, the 5G Service-Based
Architecture (SBA) can be vulnerable to misconfigurations and virtualization exploits, particularly with Mobile Network Operators
(MNOs) using hyper-scale technologies. This work addresses the
lack of practical studies and analyses on the impact of HTTP/2
attacks on 5G networks, especially given the absence of a 5Gcompliant dataset for anomaly detection. Utilizing the open-source
free5GC testbed and UERANSIM emulator, we emulate six different HTTP/2 attacks on various NFs within the 5G SBA. We
analyze their impact on the network and demonstrate that many
of them cause cascading effects on other NFs involved in related
jeopardized 5G procedures. Our emulations include both malicious
and normal network behavior, resulting in the first 5G anomaly
detection dataset that we are aware of. Using CICFlowmeter, we
extract flow-based features known for their anomaly detection
capabilities and train multiple machine learning models. These
models can serve as benchmarks for detecting HTTP/2 attacks in
5G networks.
Index Terms—5G networks, 5G security, HTTP/2, HTTP/2
attacks, 5G SBA security, 5G dataset, machine learning, anomaly
detection.

I. INTRODUCTION
HE Fifth Generation (5G) mobile networks introduce remarkable advancement in communication technology [1].
Designed to accommodate a wide range of applications, 5G
networks enhance everything from broadband mobile services to
the Internet of Things (IoT) and critical communication tasks [2].
At the heart of 5G architecture is the innovative Service-Based
Architecture (SBA) (Fig. 1), which coordinates specialized Network Functions (NFs) to manage network operations [3]. These
NFs utilize standardized protocols for their efficient communication. The Third Generation Partnership Project (3GPP) adopted
the Hypertext Transfer Protocol Version 2 (HTTP/2) as their

T

Received 27 December 2024; revised 15 June 2025; accepted 15 January
2026. Date of publication 29 January 2026; date of current version 5 June 2026.
This work was supported in part by the National Cybersecurity Consortium,
in part by the Government of Canada, in part by Ericsson Canada, and in
part by Concordia University. Recommended for acceptance by M. N. Aman.
(Corresponding author: Chadi Assi.)
Nathalie Wehbe and Chadi Assi are with the Concordia University, Montreal,
QC H3G 1M8, Canada (e-mail: Chadi.assi@concordia.ca).
Hyame Assem Alameddine is with the Ericsson Research, Montreal, QC H3B
4W5, Canada.
Digital Object Identifier 10.1109/TMC.2026.3657143

Fig. 1.

5G service-based architecture [3].

communication protocol in 5G SBA [4], [5]. 5G employs a
Service-based Interface (SBI) (i.e., nnrf, namf, nsmf, etc.) using
an Application Programming Interface (API) over HTTP/2 [4]
in the Control Plane (Fig. 1).
HTTP/2 introduces significant improvements over its predecessor, HTTP/1.1, providing features like stream multiplexing,
header compression, and optimized connection management [6].
These enhancements are crucial for handling the increased
signaling traffic and dynamic interactions between 5G NFs.
HTTP/2, a fundamental component of the 5G SBA, enables
reduced latency, efficient resource allocation, and scalable operations among NFs [4]. By harnessing the protocol features,
HTTP/2 ensures robust and seamless communication [4].
To ensure a resilient and dependable experience for 5G users,
SBA includes crucial functionalities such as NF registration,
discovery, and authorization, along with security measures for
the SBI [7]. These functions are supported by the standardized
HTTP/2 protocol, secured with Transport Layer Security (TLS),
enhancing both security and the system’s agility and scalability.
Nonetheless, securing 5G SBA presents notable challenges.
For instance, NFs can enable on-demand firewall and Intrusion
Detection Systems (IDS) to block or reroute malicious traffic.
However, the design of such dynamic NF-based security mechanisms is yet to be explored [8]. It is imperative to investigate
emerging security challenges specific to the 5G SBA and its
associated technologies and protocols. There is a significant need
for more research into the cybersecurity impacts of web-based
technologies such as HTTP/2 on SBA.
Although 5G network security has been the focus of extensive research, most studies concentrate on well-known threats
such as jamming, Denial of Service (DoS), eavesdropping,
and Man-in-the-Middle (MITM) attacks [2]. Other works [1],
[9], [10] explore the implications of virtualization in 5G SBA,
revealing how the use of containers, VNFs, and cloud-native
infrastructure broadens the attack surface. However, far fewer
studies have critically examined the security implications of

1536-1233 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

10062

adopting HTTP/2 as the core signaling protocol in 5G SBA.
Only a limited number of efforts [11], [12], [13] have addressed
this emerging threat landscape, usually focused on signaling
vulnerabilities or specific features of HTTP/2. In particular, the
work in [13] investigates HTTP/2 Stream Multiplexing Attacks
(SMAs) in a 5G environment but does not release its dataset or
extend the analysis to other classes of attacks. Similarly, [14]
introduces fuzzing and replay methodologies using 5Greplay,
but does not simulate these threats in a full 5G testbed, thus
lacking empirical information on their operational impact.
These limitations highlight a critical gap in the literature
related to the absence of a publicly available dataset, or a
comprehensive experimental analysis of HTTP/2 attacks affecting 5G NFs. Furthermore, existing anomaly detection efforts
have not focused on HTTP/2 threats within a standalone 5G
SBA environment. To bridge this gap, our work makes several
novel contributions motivated by the shortcomings of prior
studies [11], [12], [13], [14], [15]:
r We leverage the open-source free5GC [16] core and
UERANSIM [17] UE/RAN emulator, aligned with 3GPP
standards [18]. We emulate realistic 5G control plane
operations and inject six distinct HTTP/2-based attacks,
including variations of stream multiplexing, rapid reset,
and slow rate attacks. Unlike previous studies that focus on
isolated NFs or simulated HTTP/2 traffic, our emulations
capture the full impact on NF-to-NF signaling, cascading
failures, and degradation of service availability across the
entire SBA.
r We build a novel dataset that includes both benign and
malicious traffic flows generated during the emulation of
realistic 5G procedures and attacks. To the best of our
knowledge, this dataset is the first to capture HTTP/2
behavior within a fully functional 5G SBA environment.
It is designed to support advanced research in areas such
as adversarial robustness, transfer learning, and adaptive
anomaly detection. The dataset will be made publicly
available upon acceptance.
r We pre-process our 5G HTTP/2 dataset to extract flowbased features that are widely known in the literature for
their ability to distinguish between normal and malicious
behaviors. We evaluate three unsupervised machine learning models for detecting HTTP/2-based anomalies: Autoencoder (AE), LSTM-Autoencoder, and Isolation Forest
(IF). The AE model builds on our prior work [13] which
focused on detecting HTTP/2 SMAs. In this work, we test
its ability to generalize across all six attack types. LSTMAE, inspired by its successful use in detecting non-HTTP/2
attacks in 5G SBA [19], demonstrates the advantage of
modeling temporal dependencies. Our evaluation shows
that LSTM-AE achieves the highest average F1-score of
92.24%, confirming the viability of using flow-based models for HTTP/2 attack detection in real 5G environments.
The paper is organized as follows: Section II gives a background on the 5G networks, then an overview of related works
is presented in Section III. The threat model for HTTP/2 attacks and its variants are explored in Section IV. Furthermore,
Section V outlines the experimental setup, including the normal

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 7, JULY 2026

and malicious network emulations. In addition, we conduct a
thorough analysis of the impact of HTTP/2 attacks on 5G
networks with protection measures in Section VI. Section VII
presents our dataset. Our model results are presented in Section VIII. The paper concludes in Section X.
II. BACKGROUND ON HTTP/2 IN 5G
The HTTP/2 protocol was developed to address the shortcomings and performance limitations of its predecessor,
HTTP/1.1 [6]. HTTP/2 uses stream for Request/Response exchanges, where each message is either a request or a response.
HTTP/2 messages are built from HTTP/2 frames. An HTTP/2
frame is the smallest unit of communication within an HTTP/2
connection, encoded in binary. HTTP/2 frames include (1)
HEADERS frame for opening streams and contain different
header fields in the form of key-value pairs, (2) DATA frame
carries a payload, and (3) SETTINGS frame carries configuration parameters that impact the communication [6]. For example, SETTINGS_MAX_CONCURRENT_STREAMS SETTINGS allows an HTTP/2 client/server to limit the maximum
number of concurrent streams over a single HTTP/2 connection
with its peers and enables the HTTP/2 stream multiplexing
features. Other HTTP/2 features include flow control, and header
compression, among others [6]. For instance, header compression minimizes the redundancy and size of header data, which
minimizes bandwidth utilization [6].
3GPP adopted the HTTP/2 protocol in 5G to facilitate signaling between 5G NFs given its secure, reliable, and bidirectional communication [2]. These benefits position HTTP/2 as a
proficient choice for 5G NFs communication, enabling robust,
efficient, and scalable network operations. This communication
takes the form of Request/Response or Subscribe/Notify, enabling seamless interaction between the NF Service consumer
(NFc) and the NF Service producer (NFp) [4]. Request/Response
is used when the NFc requests a service and the NFp responds. In
contrast, Subscribe/Notify is employed when the NFc subscribes
to an NFp event (e.g., Session Management Function (SMF)
subscribes to location report to get notified of the last known
location of a UE or group of UEs by the Access and Mobility
Management Function (AMF) [4], etc.), that causes the NFc
to be called back when the event occurs. HTTP/2 enhances
efficiency and speed, however, it opens up new avenues for
exploitation by malicious actors. For instance, despite 5G SBA
being secure by design, it remains susceptible to virtualization
exploits and misconfigurations which can be used as entry points
to launch attacks exploiting HTTP/2 vulnerabilities [10], [20],
[21].
III. RELATED WORKS
A. HTTP/2 Anomaly Detection
Numerous studies examine threats exploiting the HTTP/2
protocol in web environments, such as HTTP/2 stream multiplexing attacks [13], [22], HTTP/2 rapid reset attacks [23],
[24], and HTTP/2 slow rate attacks [25], [26]. These studies
often suggest anomaly detection methods that are generally less

WEHBE et al.: HTTP/2 DOS ATTACKS IN 5G NETWORKS: IMPACT ANALYSIS AND ANOMALY DETECTION

effective against HTTP/2 threats targeting web environments.
For example, [22] shows that the HTTP/2 stream multiplexing
feature can be exploited to launch multiple streams over the
same connection, overwhelming the server or causing DoS. In
HTTP/2 slow rate DoS attacks, attackers send multiple specially
crafted incomplete requests that occupy the server’s connection
queue space, preventing it from processing other requests [25].
They can still exhaust server resources, leading to performance
degradation and DoS. To detect such attacks, [25] proposes
using a Chi-square test to identify abnormal intervals of HTTP/2
traffic. However, its effectiveness varies with the attack rate and
the chosen detection interval. The same authors later developed
an event sequence analysis method, achieving high accuracy
with minimal computational demands [26], only for this attack.
Another method by [27] focuses on identifying HTTP/2 multiplexed asymmetric DDoS attacks by contrasting the behavior
of legitimate users and attackers. While effective for DDoS
attacks, this approach fails to detect HTTP/2 slow-rate DoS
attacks due to the minimal computational overhead and pattern
mimicking by attackers. Both slow rate and stream multiplexing
attacks exploit various HTTP/2 parameters, leading to a DoS.
One of the latest attacks related to HTTP/2 is the HTTP/2 rapid
reset attack, identified as CVE-2023-44487 [24]. This attack
exploits the stream multiplexing feature by resetting streams
currently handling requests using the RST_STREAM frame. The
mitigation for this attack involved bounding the number of
simultaneously executing handler routines to a defined limit
(SETTINGS_MAX_CONCURRENT_STREAMS=200), preventing server overload by queuing incoming requests until a
current request is completed. If the queue becomes excessively
long, the server terminates the connection.
With the adoption of the HTTP/2 protocol by 3GPP as
a signaling protocol in 5G networks, it becomes crucial to
understand its security implications. To date, to the best of
our knowledge, [13] remains the only study that has emulated
HTTP/2-related attacks in a 5G SBA environment. This research
focused on anomaly detection systems that monitor stream patterns to identify malicious behaviors, specifically targeting only
HTTP/2 stream multiplexing attacks within the context of a 5G
network. Another work [14], proposed testing methodologies
using an open-source solution called 5Greplay, allowing network operators to defend against flooding and fuzzing attacks.
However, the authors did not focus on the impact of these attacks
on 5G networks, as their study did not employ a 5G testbed.
Additionally, the HTTP/2 dataset in their research was created
using MMT-DPI, a tool developed to parse and mutate HTTP/2
packets. Unlike [13], [14], the current paper significantly expands their scopes by targeting multiple HTTP/2-related attack
types, including slow-rate and rapid-reset attacks, in addition to
stream multiplexing within 5G SBA. Furthermore, our dataset
is based on a 5GC testbed that follows 3GPP standardization.
B. HTTP/2 Datasets
Several prior studies have leveraged publicly available
datasets such as CICIDS2018, CICDDoS2019, and datasets
derived from 4G-LTE and traditional HTTP/1.1-to-HTTP/2

10063

transitions [27], [28], [29], [30], [31]. These datasets have
proven useful for general network anomaly detection and have
demonstrated the value of flow-based features in identifying
threats such as DoS attacks, unauthorized access, and traffic
manipulation. Flow features such as duration, volume, and
packet counts provide a compact yet powerful representation
of network behavior, especially useful in environments with
limited visibility into payload data. However, these datasets
fall short when applied to 5G SBA scenarios. First, most of
them were created in pre-5G contexts and do not reflect the
architectural changes, service-based interactions, or traffic
characteristics of standalone 5G networks. Second, while a few
recent efforts have attempted to model HTTP/2 specific behavior
and attacks, such as those using stream multiplexing in 5G [13],
they either rely on private datasets or simulate traffic without
grounding in a real 5G SBA testbed. Furthermore, works that
use 5G testbeds often focus on non-HTTP/2 protocols and
do not capture the application layer characteristics unique to
HTTP/2-based service communication in 5G [32], [33], [34].
This lack of a public, domain-specific dataset limits researchers’ ability to design, evaluate, and compare anomaly detection methods tailored for real-world 5G HTTP/2 traffic. The
need for such datasets is especially pressing given the growing
adoption of HTTP/2 in 5G core networks and the increasing
sophistication of potential attacks. In response to this gap, our
work contributes a novel dataset that captures both normal and
malicious traffic in a controlled 5G SBA environment using
real NF interactions and HTTP/2 communication. By emulating
diverse HTTP/2-specific attacks and collecting flow-level data
in a fully standalone 5G testbed, we provide the community
with a resource that better reflects the operational realities of
modern 5G deployments. This significantly advances the field
of 5G security, facilitating further exploration and development
of effective anomaly detection and security measures for safeguarding 5G networks.
IV. HTTP/2 ATTACKS IN 5G NETWORKS
Although secure by design, the 5G SBA can still experience
some attacks resulting from virtualization exploits, misconfigurations, and its HTTP/2 signaling protocol vulnerabilities. In the
following, we shed light on some HTTP/2 attacks in 5G networks
while detailing the vulnerabilities they exploit and their related
threat models.
A. Assumptions
HTTP/2 attacks in 5G networks can be performed through
misconfigured or compromised NFs. We consider the following
assumptions for HTTP/2 attacks, assuming that attackers compromise the NFc and use it to attack the NFp or vice versa.
1) Attacker compromises an NFc: Many standardization documents discuss threats brought by NFV and virtualization
technologies (e.g., container, virtual machines, etc.) to
telecommunication networks and 5G [20]. The adoption of
hyper-scale cloud by mobile operators extends the attack
surface of their network and makes their NFs vulnerable [20]. An attacker can compromise 5G NFs deployed

10064

Fig. 2.

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 7, JULY 2026

HTTP/2 attacks in 5G SBA.

on docker containers in the cloud, by exploiting docker
vulnerabilities to perform container escape (i.e., CVE2016-5195 [35], CVE-2019-5736 [36], and CVE-202320864 [37]) [38]. Breach of isolation between network
slices served by the same compromised NF can also be
exploited by attackers [39], [40].
2) NFc can successfully authenticate with the NFp: We assume that if TLS is used, the malicious NFc can still
authenticate with the NFp as the attacker has access to
its public/private key pairs.
3) NFc is authorized to access NFp services: We assume that
the malicious NFc has already acquired OAuth2.0 access
tokens to the NFp services. These tokens are cached and
can be reused by the attacker [2], [41]. Alternatively, the
malicious NFc can request new access tokens from the
NRF given that it can successfully authenticate with it (i.e.,
assumption 2). An attacker can exploit vulnerabilities in
network slicing and service authorization, as noted in [40],
to access NFp services.
4) Attacker has access to UE information: As some network
services require exchanging UE information (e.g., Subscription Permanent Identifier (SUPI)) [42], we assume
that the attacker can gain access to such information by
monitoring NFc communications or even by requesting
such information from other NFs.
We should note that these attacks are not new or novel.
HTTP/2 attacks are general attacks that can occur in a web
environment as they exploit HTTP/2 features. However, their
variations, applicability, and impact on a 5G network are different from a web environment due to the specificity of the
5G SBA and the 5G procedures. In 5G, any NF can act as a
service consumer (i.e., HTTP/2 client) or producer (i.e., HTTP/2
server), enabling attacks from both HTTP/2 clients and servers.
However, in a web environment, attacks are generally initiated
from HTTP/2 clients to the web server. Although exploited in
the web, applying these attacks in a 5G environment requires

leveraging 5G-specific APIs, making these attacks more challenging to perform than in a web, where APIs are not necessarily
used. Furthermore, their impact on a 5G network can be more
disruptive than in a web environment, given the dependencies
and interactions existing between the different 5G NFs, as we
show in Section VI.
B. Attack 1: HTTP/2 Stream Multiplexing Attack (SMA)
To perform an HTTP/2 SMA, attackers send multiple
requests, as much as the NFp allows in the HTTP/2 SETTINGS_
MAX_CONCURRENT_STREAMS, into a single HTTP/2
connection. By default, the NFc can send up to 2,147,483,647
(default value of SETTINGS_MAX_CONCURRENT_
STREAMS) streams per HTTP/2 connection [6]. Attackers can
trigger HTTP/2 SMA in two ways within 5G SBA, either by
employing the Request/Response or the Subscribe/Notify.
1) Attack 1.1-SMA-Request/Response: In an HTTP/2 SMA
using Request/Response (Fig. 2(a)), attackers compromise NFc
and send multiple requests over a single HTTP/2 connection towards NFp. Attackers repeat this behavior over multiple HTTP/2
connections which results in a DoS on the NFp.
2) Attack 1.2-SMA-Subscribe/Notify: According to 3GPP
[4], the Subscribe/Notify service operations in HTTP/2 involve
two HTTP/2 connections, each handling one direction of traffic.
NFc acts as an HTTP/2 client when subscribing to notifications,
while NFp functions as an HTTP/2 server. Conversely, the roles
are reversed when NFp sends notifications to NFc. As depicted in
Fig. 2(b), a compromised NFc establishes an HTTP/2 connection
with NFp and sends a subscription request containing a notify
URI to signal to the NFp to notify it when the occurrence of the
API-related event (e.g., N1N2TransferFailureNotification [43]
is triggered). Attackers exploit the event conditions (i.e., UE state
is DISCONNECTED [43]) to initiate the notification. Attackers
repeat the request with the notification URI to cause an SMA
and overwhelm both NFp and NFc. The NFc will be receiving an

WEHBE et al.: HTTP/2 DOS ATTACKS IN 5G NETWORKS: IMPACT ANALYSIS AND ANOMALY DETECTION

excessive number of notifications causing a DoS, while the NFp
struggles with the high number of requests and from managing
and forwarding the notifications to the NFc, eventually leading
to resource exhaustion and DoS on the NFp.
C. Attack 2: HTTP/2 Rapid Reset Attack
Attack 2-Rapid Reset, identified as CVE-2023-44487 [24],
exploits the stream multiplexing feature of HTTP/2. It employs
the RST_STREAM frame to terminate streams that are currently
processing requests [6]. In this case, the number of streams that
were reset by the RST_STREAM frame do not count towards
SETTINGS_MAX_CONCURRENT_STREAMS. The mitigation for this attack considers counting any request reaching the
server, even if it is a RST_STREAM frame, as part of the defined
maximum stream limit. It involves limiting the number of simultaneously executing handler routines (SETTINGS_MAX_
CONCURRENT_STREAMS= 200) and prevents server overload by queuing incoming requests until a current request is
completed. If the queue becomes excessively long, the server
terminates the connection as a safeguard. However, increasing
the SETTINGS_MAX_CONCURRENT_STREAMS slightly
could significantly impact network performance.
In this attack (Fig. 2(c)), attackers compromise the NFc
and establish an HTTP/2 connection with the NFp. In this
work, we assume that the reset attack is patched, however, we
assume that the NFp is misconfigured to allow an unusually
high number of concurrent streams (e.g., SETTINGS_MAX_
CONCURRENT_STREAMS = 1000 instead of the default 200
set in the golang library). The malicious NFc then rapidly generates requests and immediately issues RST_STREAM frames
for each request across multiple HTTP/2 connections, forcing
the NFp to terminate the requests. This flood of reset stream
requests can lead to resource exhaustion at the NFp.
D. Attack 3: HTTP/2 Slow Rate Attacks
Another type of HTTP/2 attack is an HTTP/2 slow rate DoS
attack which involves attackers sending HTTP/2 frames at a
deliberately slow rate to exhaust NFp resources [21], [25], [26].
HTTP/2 slow rate attacks require low bandwidth and are difficult
to detect. Attackers exploit the HTTP/2 frame between the NFc
and NFp, such as the exchange of SETTINGS frame, capitalizing
on the design of NFp which waits for certain responses. In this
work, we target three variations of HTTP/2 slow rate attacks.
1) Attack 3.1-Slow Rate-Setting: HTTP/2 slow Rate-Setting
is a slow rate attack that is based on un-acknowledging a SETTINGS frame. In a normal HTTP/2 communication scenario,
both endpoints must exchange SETTINGS frames at the start
of a connection and may send them at any other time during
the connection. SETTINGS frame allows each endpoint to acknowledge the parameters of the connection. When an endpoint
receives a SETTINGS frame, it should send an acknowledgment
response that tells the sender that the SETTINGS frame was received and processed. Thus, the slow Rate-Setting attack mainly
takes advantage of the SETTINGS frame to let the endpoint
wait. As depicted in Fig. 2(d), attackers compromise the NFp
that has already been authenticated and authorized to access

10065

NFc services. The NFc initiates the first HTTP/2 connection
with the compromised NFp, followed by sending a SETTINGS
frame. However, the malicious NFp does not acknowledge the
received SETTINGS frame. NFc continues to send numerous
requests of SETTINGS frame to NFp. Since the malicious NFp
consistently fails to acknowledge the HTTP/2 SETTINGS frame
for all messages received, it can exhaust the available connection
pool. This not only blocks other NFs from communicating with
the victim NFc but also keeps the connection from NFc open for
an extended period.
2) Attack 3.2-Slow Rate-Connection Preface: The connection preface is sent from the NFc to inform the NFp that
HTTP/2 will be used for further communications. In this attack (Fig. 2(e)), after establishing an HTTP/2 connection, a
compromised NFc sends the connection preface to the NFp,
prompting it to wait for a GET/POST HTTP/2 request. However,
the malicious NFc intentionally withholds any HTTP/2 requests,
forcing the NFp to wait until the NFp drops the connection, thus
wasting its resources and denying its service to other NFs.
3) Attack 3.3-Slow Rate-Window Size: In a standard HTTP/2
connection, both endpoints are required to send an HTTP/2
payload that includes a SETTINGS frame with the SETTINGS_INITIAL_WINDOW_SIZE field, along with a complete
GET request. The SETTINGS_INITIAL_WINDOW_SIZE field
specifies the sender’s capacity to receive data in bytes from its
peer. Upon receiving this, the NFp expects that the NFc can
receive data of the indicated size. However, attackers exploit
this mechanism for a slow rate attack by compromising the
NFc (Fig. 2(f)). After establishing the HTTP/2 connection,
the malicious NFc sends a SETTINGS frame with the SETTINGS_INITIAL_WINDOW_SIZE set to zero, falsely indicating
no available window space for data reception. The NFp, in turn,
holds the data until it receives a WINDOW_UPDATE frame
that increases the window size. Nonetheless, the malicious NFc
intentionally never sends a WINDOW_UPDATE, thus causing
the NFp to wait till the connection pool is full, resulting in
dropping the connection. Thus, this attack exhausts the available
connection pool at the NFp and blocks its service for other
legitimate UEs.
V. ENVIRONMENT SETUP
In this section, we present the environment that we use to
emulate normal and malicious network traffic.
A. Emulation Setup - 5G Testbed
We emulate the HTTP/2 attacks using free5GC [16], an
open-source 5G core network testbed, and UERANSIM [17],
a UE/RAN emulator, adhering to the 3GPP standard [18].
We [44] as depicted in Fig. 3. The VMs are equipped with
Ubuntu 20.04-Focal, 8 virtual Central Processing Units (CPU),
and 64 GB of RAM. We use free5GC docker-compose version
3.4.0 [45], which runs NFs in separate containers on the same
VM. UERANSIM facilitates the emulation of network traffic
and 5G operations, including UE registration, deregistration,
and service requests [42], providing crucial insights into network
behavior and system performance.

10066

Fig. 3.

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 7, JULY 2026

5G Testbed with normal and malicious network behaviors.

TABLE I
LOGICAL DEPENDENCY BETWEEN 5G PROCEDURES

B. Emulation Configuration
Given the lack of publicly accessible datasets for anomaly
detection in the 5G SBA, we employ our emulated 5G testbed to
emulate normal and malicious network behaviors. For normal
network behavior, we replicate the standard activities of UEs
within our 5G testbed by leveraging different 5G procedures
implemented in UERANSIM (Table I). These same procedures
are also employed to model HTTP/2 attacks and generate malicious traffic.
C. Normal Network Behavior Emulation
To emulate normal network behavior, we consider the arrival
of 100 UEs to the network using a Poisson process [46], [47]
over two hours. The Poisson process is widely recognized as
an effective method for modeling arrival times of events in
network traffic due to its ability to capture the randomness of user
behavior and service requests over time. For our implementation,
we defined the load (number of requests) per 10-minute intervals
as [1, 2, 3, 5, 6, 7, 8, 9, 7, 5, 3, 0.5], to reflect the dynamic nature of
5G network traffic. We use 100 UEs in each 10-minute interval,
representing one predefined network load. For each load value,
we emulate a number of 5G procedures calculated based on
the Poisson process for each of these 100 UEs. This approach

follows the principles outlined in [48], where Poisson processes
are used to model the arrival of UE requests in realistic network
scenarios. Each UE engages in one or more 5G procedures
selected from a set provided by UERANSIM (Table I). To ensure
that our emulation of 5G normal network behavior is realistic,
we follow the 3GPP standard definition of the different 5G procedures and their logical dependencies [18], [42]. We limit these
procedures to those available in UERANSIM and which we
can emulate. Table I defines the possible subsequent procedure
for each triggered procedure by the UE following the 3GPP
standard. Given that 5G procedures have logical dependencies
and specific order requirements defined by the 3GPP standard,
in our emulation, we choose a subsequent procedure (p + 1) that
follows a procedure p for a UE by randomly selecting it from
a predefined list of procedures that logically follow p . The list
of the possible subsequent procedures for each 5G operation in
UERANSIM, is outlined in Table I. For instance, a UE cannot
proceed to deregistration if it has not completed its registration.
Moreover, each 5G procedure triggers various communication
between NFs. These communications may vary based on the UE
state (e.g., CONNECTED, IDLE, DISCONNECTED) and other
factors such as network conditions and RAN resources [42].
In our emulation, each UE starts by first registering to the
network and then selects a subsequent procedure as detailed
in Table I. Hence, the following procedure is randomly chosen
from the appropriate options, which include Uplink, Downlink,
UE release PDU session, gNodeB release PDU session, and
Deregistration procedures. After the registration, let us assume,
for example, that the gNodeB release PDU session procedure
was selected by the UE. Following its execution, either Uplink,
Downlink, or Deregistration procedures can be initiated. Note
that these procedures are triggered for the same UE at different
times to replicate 5G communications and can switch the UE
between different states. For example, (1) UE registers to the
network; after a certain period of time, (2) RAN releases the
PDU resources allocated to the UE, switching its state to IDLE;
(3) Subsequently, a Downlink procedure is triggered from the

WEHBE et al.: HTTP/2 DOS ATTACKS IN 5G NETWORKS: IMPACT ANALYSIS AND ANOMALY DETECTION

Fig. 4.

Benign network traffic.

network to signal to the UE which is in IDLE state, hence,
switching its state to CONNECTED.
Fig. 4 highlights the interactions between pairs of NFs observed within our 5G testbed (i.e., control plane). We extract the
total number of messages reflecting these interactions between
pairs of NFs during 20 minutes of emulations of different 5G
procedures and present them in Fig. 4(a). The latter shows that
interactions involving the AMF, SMF, UDR, and PCF are more
frequent, reflecting the intensive activity associated with Uplink,
Downlink, and UDR management procedures during our normal
network traffic. This data is crucial as it represents the peak
demands for each interaction, offering insights into network load
during typical operations.
Along with observing NFs interactions, we monitor resource
utilization during normal network traffic by tracking CPU consumption across various NFs over two hours, as shown in
Fig. 4(b). We observe that although the CPU load of the different
NFs remains under 25%, AMF, SMF, and UDR exhibit higher
CPU consumption than other NFs which can be explained by
the high number of requests they manage (Fig. 4(a)).
D. Malicious Network Behavior Emulation
5G testbed emulates various HTTP/2 attacks to expose potential vulnerabilities within the 5G SBA. Specifically, we target

10067

procedures such as Uplink, Downlink, UE release PDU session,
and UDR Management, frequently used in our 5G testbed. We
emulate HTTP/2 attacks (Section IV) where attackers compromise NFc/NFp which are highlighted in red, such as a
PCF, UDR, or SMF, as shown in Fig. 3, in addition to UE
information (i.e., SUPI). We assume that attackers exploit 30
legitimate UEs out of 100. Through the compromised NFc,
each attack is launched using the IMSI of the 30 legitimate
UEs, where multiple HTTP/2 connections are established toward the NFp. These connections are configured with a default
SETTINGS_MAX_CONCURRENT_STREAMS=200 in our 5G
testbed. Thus, in our attack emulations, the network operates
normally for the first 60 minutes, after which the attack is
initiated when the load in the network is designed to be around
its peak (load = 8).
1) Attack 1: HTTP/2 Stream Multiplexing Attack: For instance, Fig. 2(a) involves a malicious SMF that randomly triggers various procedures toward the AMF, adhering to HTTP/2
protocol precedence constraints [6], [43]. For Attack 1.1-SMARequest/Response, we use three different procedures, that are
triggered from the malicious SMF towards the AMF using the
same Namf_Communication_N1N2MessageTransfer API, such
as Uplink, downlink, and UE release PDU session. Note that this
API covers most of the service operations provided by the AMF
and consumed by the SMF [43]. As attackers, we repeat this
attack over 55,954 HTTP/2 connections, each handling up to 907
requests, resulting in an NFp overload and a DoS. The second
attack scenario (Fig. 2(b)) considers an SMA that involves a malicious SMF exploiting 30 UEs by triggering only the Downlink
procedure using Namf_Communication_N1N2MessageTransfer
API, however, we include a notify URI for DISCONNECTED
UEs. According to 3GPP specifications [43], when the Downlink
procedure is initiated while the UE state is DISCONNECTED,
the N1N2TransferFailureNotification API is triggered to notify
SMF that the UE is unreachable [43]. Consequently, the AMF
sends a notification back to the malicious SMF. We emulated
this attack using 54,188 HTTP/2 connections, each handling up
to 841 requests over 40 minutes before the AMF goes down.
This attack effectively exploits the signaling mechanisms of the
network, leading to a DoS on the AMF and SMF. The continuous
failure notifications overwhelm both AMF and SMF, making
it unresponsive and crippling NFs, degrading the Quality of
Service (QoS) for legitimate UEs.
To better illustrate how we perform Attack 1.1-SMA-Request/
Response, we illustrate in Fig. 5 the normal Downlink procedure
triggered from the Data Network (DN) when the UE is in the
IDLE state [43], and highlight in red how an attacker can perform
the attack as in our emulation assuming that the SMF was
compromised. In a normal scenario, the SMF sends a request to
the AMF using Namf_Communication_N1N2MessageTransfer
API (Fig. 5(3a)). The AMF responds to the SMF indicating
that the UE is not reachable, and subsequently sends a Paging Request to the UE/RAN (Fig. 5(4b)). The Paging Request triggers the Uplink procedure to activate the UE. In
the dashed red box (Fig. 5), we highlight a scenario where
an attacker compromises the SMF and launches a malicious
Namf_Communication_N1N2MessageTransfer request towards
the AMF, triggering a Downlink procedure for a UE in IDLE

10068

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 7, JULY 2026

SETTINGS_INITIAL_WINDOW_SIZE equal to zero, signaling
that the PCF can no longer receive data. This manipulation
forces the UDR to halt all data transmissions until it receives
a WINDOW_UPDATE frame, effectively freezing the data flow.
The malicious PCF repeats this attack over 3,815 HTTP/2 connections severely impacting the 5G network availability.
VI. ATTACKS IMPACT AND PREVENTION
A. HTTP/2 Attacks Impact

Fig. 5.

Network triggered service request procedure [43].

state without requiring network signaling. Although the attacker
only initiates a single request, it results in a chain of other
messages (Fig. 5(3b-8)) related to paging, service request, PDU
session update, and PDU session modification in the 5G network.
This depicts a high overhead that an attacker can introduce to
the network with a single malicious request.
2) Attack 2: HTTP/2 Rapid Reset Attack: In our emulation
of Attack 2-Rapid Reset, a compromised PCF targets the UDR
using a UDR Management procedure [42]. We assume that
the UDR sets its HTTP/2 connection with SETTINGS_MAX_
CONCURRENT_STREAMS= 1000. As depicted in Fig. 2(c), the
PCF sends to the UDR a request using Nudr_DataManagement
API followed by a RST_STREAM frame to stop the sent request.
The malicious PCF establishes around 263,251 HTTP/2 connection with the UDR over 2 hours, with up to 2306 requests and
RST_STREAM frame per connection. This action aims to create
a DoS situation, effectively disrupting the network’s operations
and impacting its ability to process legitimate requests.
3) Attack 3: HTTP/2 Slow Rate Attack: We emulate three
variations of HTTP/2 slow rate attack from PCF to UDR. As depicted in Fig. 2(d), to emulate the Attack 3.1-Slow Rate-Setting,
the PCF establishes around 3,947 HTTP/2 connections with the
UDR and sends to it on each of them a SETTINGS frame. As
the UDR is malicious, it does not acknowledge the SETTINGS
frames sent by the PCF, leading to a backlog of unacknowledged
frames, hence, causing a drop of these connections after a certain
timeout time. We emulate the Attack 3.2-Slow Rate-Connection
Preface (Fig. 2(e)) by accounting for a malicious PCF that sends
a connection preface to the UDR without following it by any
HTTP/2 GET/POST. This makes the UDR wait endlessly for
an HTTP/2 request that never arrives. This scenario is repeated
over 5,733 HTTP/2 connections and exhibits similar behavior
to normal network traffic. During Attack 3.3-Slow Rate-Window
Size (Fig. 2(f)), the malicious PCF establishes the first HTTP/2
connection and sends a manipulated HTTP/2 SETTINGS with

Our emulations of HTTP/2 attacks on 5G SBA presents various impact on NFs resource utilization that we measure through
observing the CPU consumption of the different NFs in Fig. 6.
Additionally, we measure the total number of messages (i.e.,
requests and notifications only) exchanged per each pair of NFs
within the 5G SBA during 20 minutes of the different attacks
as shown in Fig. 7. This metric reflects the volume of control
signaling traffic impacted by the HTTP/2 attacks especially
when compared to the benign traffic captured for the same period
during the benign emulation (Fig. 4). We analyze in the following
the impact of the different attacks on 5G networks, suggest
prevention and mitigation measures, and summarize them in
Table II.
1) Attack 1: HTTP/2 Stream Multiplexing Attack: Upon the
start of Attack 1.1-SMA-Request/Response (Fig. 6(a)) and Attack 1.2-SMA-Subscribe/Notify (Fig. 6(b)) at time 60 (i.e., after
around an hour of emulations), the CPU usage of the AMF and
SMF increases sharply, while the CPU usage for the rest of
the NFs decreases. This is mainly attributed to the overload
at the AMF and SMF, delaying and potentially blocking the
completion of 5G procedures that are stuck at the SMF-AMF
interactions. As shown in Fig. 6(a), at time 104 (i.e., after
44 minutes of the start of the attack), the AMF fails, resulting in a DoS. Further, the regular CPU spikes during Attack
1.2-SMA-Subscribe/Notify (Fig. 6(b)) highlight intense activity
periods that stress the SMF and potentially degrade services of
other NFs. Notably, we observe the highest number of messages
during SMF-AMF interaction due to frequent attack requests
from the SMF towards the AMF as illustrated in Fig. 7(a) and
(b). Additionally, the number of messages in the AMF-SMF
interactions during Attack 1.2-SMA-Subscribe/Notify (Fig. 7(b))
is higher than during the Attack 1.1-SMA-Request/Response
(Fig. 6(a)) due to the notifications sent from the AMF to the
SMF. In summary, SMA attacks significantly impact network
availability by exhausting its resources, and causing a DoS on
the targeted NF and potentially on the whole 5G network.
2) Attack 2: HTTP/2 Rapid Reset Attack: Although the Attack 2: HTTP/2 Rapid Reset was emulated while the official
patch was deployed in our network, we notice that the increase in the SETTINGS_MAX_CONCURRENT_STREAMS
(Section IV-C) can still disrupt the provided QoS, not only by
overloading the attack target (i.e., UDR) but also the attack
source (i.e., PCF). Fig. 6(c) shows high CPU consumption at
the UDR and PCF that often reaches 80% for an hour. However,
after 2 hours of running the attack, we observe CPU spikes
reaching 160% between times 120 and 180, indicating moments
of intense load on the UDR, always accompanied by a high load

WEHBE et al.: HTTP/2 DOS ATTACKS IN 5G NETWORKS: IMPACT ANALYSIS AND ANOMALY DETECTION

Fig. 6.

5G SBA NFs CPU consumption during malicious network behavior.

Fig. 7.

Total number of messages between pairs of NFs in 5G SBA during malicious network behavior.

on the PCF. This is also reflected by the high number of messages
exchanged between PCF and UDR in Fig. 7(c). However, a lower
CPU consumption is observed at the remainder NFs between
times 120 and 180 reflecting a DoS attack on the network and a
degradation of the QoS of those NFs (Fig. 6(c)).

10069

3) Attack 3: HTTP/2 Slow Rate Attack: When examining the
variations of HTTP/2 slow rate attacks, we notice their distinct
impacts on the NFs within the 5G SBA, starting at attack time 60.
Fig. 6(d) and (f) reflect a high CPU consumption on the targeted
NF, the PCF, with a degradation of the CPU consumption on the

10070

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 7, JULY 2026

TABLE II
HTTP/2 ATTACKS, IMPACT AND PROTECTION MEASURES IN 5G SBA

other NFs, reflecting a degradation of the network availability
and QoS without observing a total DoS. Although the PCF
CPU consumption is comparable in both, Attack 3.1-Slow RateSetting and Attack 3.3-Slow Rate-Window Size, we notice from
Fig. 7(d) and (f) that the number of messages exchanged between
UDR and PCF is higher in Attack 3.3-Slow Rate-Window Size
than in Attack 3.1-Slow Rate-Setting. This explains that the high
CPU consumption is not a result of the number of exchanged
messages but rather of resources allocated during the waiting
times at the PCF for a SETTINGS acknowledgment in case of
Attack 3.1-Slow Rate-Setting and for a WINDOW_UPDATE in
case of Attack 3.3-Slow Rate-Window Size.
Attack 3.2-Slow Rate-Connection Preface does not exhibit a
significant impact on the CPU of the different NFs, as illustrated
in Fig. 6(e). In contrast, although the trend is different, the
CPU consumption is comparable to the benign network behavior
shown in Fig. 4(b). This indicates that detecting this attack may
be more challenging. By observing Fig. 7(d), (e), and (f), we
note that the total number of messages exchanged during the
different HTTP/2 slow rate attacks is lower than that exchanged
during normal network operations (Fig. 4(b)). This demonstrates
that simply counting messages between NFs is insufficient to
detect manipulation in the HTTP/2 flow, particularly in HTTP/2
frames.
B. Discussion and Mitigation Measures
The analysis of HTTP/2 attacks on our 5G testbed reveal that
HTTP/2 SMA attacks are the most damaging due to the DoS
impact they cause on the targeted NF and on the 5G network as
a whole. More specifically, degradation of the performance of
the 5G NFs not directly involved in the attack is observed and
is highly related to the type of the targeted NFs. For instance,
the emulated 5G procedures (Table I) involve many interactions
between the AMF and SMF that cause a bottleneck for the

completion of these procedures which was reflected by a degradation of the CPU consumption of other NFs which were not
receiving as many messages as during the normal network traffic
emulations. Similar performance degradation was also observed
on the NFs not involved in the attack during the rapid reset and
slow rate attacks. However, these attacks exploit the inherent
limitations in timeout and rate-handling mechanisms within
the network, pushing the 5G SBA towards a slow degradation
rather than a sudden failure. This subtlety can lead to longer
periods of unnoticed impact, allowing significant damage over
time.
It is worth noting that the value assigned to the SETTINGS_MAX_CONCURRENT_STREAMS plays an important role in protecting the network against SMA and rapid reset
attacks. Here, an intelligent solution for setting the value of
this SETTINGS_MAX_CONCURRENT_STREAMS is highly
important to achieve the trade-off between network security and network performance. A high value of this setting
can maximize the benefits of the stream multiplexing feature
in terms of latency, however, it can increase the SMA impact on the network. Thus, an intelligent and adaptive SETTINGS_MAX_CONCURRENT_STREAMS value adjustment
solution based on network state can be efficient in protecting the
network against SMA attacks. The stealthy nature of slow-rate
attacks can make their detection challenging, requiring intelligent anomaly detection solutions. In contrast, they can be
prevented by intelligent monitoring solutions and timer values
to drop or close malicious connections with long inactivity time
at the HTTP/2 client. Although these attacks are exploited in
the web, exploiting these attacks in a 5G environment requires
attacking 5G specific API, making these attacks more challenging to perform than in the web where APIs are not necessarily
used. Furthermore, their impact on 5G network can be more
disruptive than in a web environment given the dependencies
and interactions existing between 5G NFs.

WEHBE et al.: HTTP/2 DOS ATTACKS IN 5G NETWORKS: IMPACT ANALYSIS AND ANOMALY DETECTION

TABLE III
SELECTED FLOW-BASED FEATURES [50]

10071

TABLE IV
FLOW-BASED DATASET IN 5G NETWORKS

are mutually exclusive and do not include any redundant records.
For the data to be usable for anomaly detection, we label our
flows as benign (0) and attack (1) based on our knowledge of
the compromised UEs used and the time of the attack emulations
were launched.
VIII. HTTP/2 ANOMALY DETECTION
VII. DATASETS
To generate a 5G dataset that mirrors real 5G network traffic,
we emulate normal and attack traffic as noted in Section V and
collect the generated data. Using Wireshark [49], a network
monitoring tool, we capture network traffic data within our
5G testbed. These captures are raw packets stored as PCAP
files [49], and document raw network interactions between
various entities like UE, RAN, and 5G NFs. We collect benign data and execute HTTP/2 attacks at different times. We
refine our dataset by processing raw network-layer data with
CICFlowMeter [50], which generates 84 flow-based features
capable of distinguishing normal and malicious behaviors [29],
[30], [31]. Each row in the resulting CSV file represents a single
flow, defined as packets with the same source IP, destination IP,
source port, and destination port within a specified time interval.
Separate CSV files were created for benign traffic and each
emulated HTTP/2 attack.1
Following the extracted features, we perform feature normalization and select the most relevant ones. At the feature
selection stage, we use the variance threshold [51] function
to determine the most relevant variance value of the features.
We choose this selection function, as it is well known for its
usage in unsupervised models [51]. The purpose of its usage is
to help in removing features with minimal variations or those
deemed as noise. As the model is highly dependent on 5G SBA
behavior patterns, the features selected to train the model must
be accurately represented (i.e., have high variance) and provided
to the anomaly detection module, as a result, we consider 54
features that have high variance, as shown in Table III.
For each emulated scenario, we divide the flow-based dataset
(Table IV) into two categories: benign and attack, with the total
duration of each emulation. Although emulations were planned
for two hours, Attack 1.1-SMA-Request/Response and Attack
1.2-SMA-Subscribe/Notify lasted for 1 hour 40 minutes and
1 hour 50 minutes, respectively, as the network went down due to
the attack. It is worth noting that the reported datasets in Table IV
1 The different CSV files from our dataset will be made publicly available
upon the paper acceptance.

In this section, we evaluate the performance of three unsupervised models using flow-based features as an anomaly
detection solution in 5G SBA, focusing on their ability to identify
HTTP/2-5G-specific attacks.
A. Anomaly Detection Benchmark Models
To detect HTTP/2 attacks in 5G networks, we adopt unsupervised machine learning models due to the lack of labeled
real-world data and the need to detect zero-day attacks [52]. In
5G SBA, compromised Network Functions (NFs) may act maliciously while still appearing legitimate, and the origin of such
attacks is often unknown. Unsupervised models are therefore
well-suited to this threat landscape.
Among the unsupervised models, we first include the AE.
AEs are designed to learn compact representations of normal
data through reconstruction, such that large reconstruction errors
indicate deviations or anomalies [53]. We selected the AE model
not only because of its proven applicability in general anomaly
detection, but also to evaluate its performance beyond its original design context in [13], where we previously developed an
AE-based solution specifically for detecting HTTP/2 SMA. In
this work, we challenge the AE’s ability to generalize by testing
whether a model effective against a single known attack (SMA)
can also identify five additional HTTP/2 attacks that exhibit
different traffic characteristics and complexities. This allows us
to evaluate the generalization capability of AE for broader 5G
HTTP/2 attack detection.
We further include the LSTM-based Autoencoder (LSTMAE) to account for temporal patterns in 5G network traffic [54].
5G SBA communication flows exhibit sequential dependencies due to service chaining, stateful procedures, and inter-NF
signaling. LSTM layers can capture these dependencies, making LSTM-AE particularly effective for recognizing complex,
multi-stage attacks that develop over time. Our choice is also
motivated by the work in [19], which successfully employed
LSTM-AE for detecting non-HTTP/2-based attacks in 5G SBA.
By adopting and adapting the same model in this study, we
extend its application to new attack classes specific to HTTP/2,
assessing its robustness across a wider threat spectrum in the 5G
context.

10072

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 7, JULY 2026

TABLE V
HYPERPARAMETERS

TABLE VI
F1-SCORE OF LSTM-AE, AE, IF ACROSS HTTP/2 ATTACKS

Fig. 8.

Finally, we include the Isolation Forest (IF) as a lightweight,
scalable, and interpretable unsupervised model. IF is effective
for detecting outliers in high-dimensional data by recursively
partitioning data points based on randomly selected features. Its
core strength lies in its independence from distribution assumptions and its capability to isolate rare anomalies quickly [55].
This is crucial in our use case, where the attacker may compromise any NF (NFc or NFp) and initiate attacks without triggering
obvious symptoms. Since we do not assume prior knowledge
of the attack’s origin, and the dataset is largely unlabelled, IF
allows us to detect anomalous flows without explicit supervision,
relying instead on the statistical rarity of malicious behavior in
the flow-based feature space. Thus, we train and compare the
performance of LSTM-AE, AE, and IF in detecting HTTP/2
attacks.
B. Experimental Results
We evaluate the performance of the three aforementioned
models in detecting the six HTTP/2 attacks that we emulated.
We use the F1-score, an effective evaluation metric to assess
the models’ precision and recall capabilities and hence, their
detection performance. We first train and validate multiple architectures for each of the three models, selecting the one with
the best detection performance. The final chosen architecture
and hyperparameters for each model are reported in Table V. To
accomplish this, we allocate 20% of the training dataset of size
100,000 rows as a validation dataset, and we train the models
using the remaining training dataset. To test the three models
and to check their performance over different HTTP/2 attacks,
we select from each attack file (Table IV) 30,000 benign rows
and 10,000 attack rows.
After training and validating the models, we test each model
using the test dataset. As shown in Table VI, LSTM-AE outperforms AE and IF across all HTTP/2 attacks. LSTM-AE achieves
an average F1-score of 92.24% across HTTP/2 attacks, reflecting
its robustness in anomaly detection. IF follows with a lower
F1-score. AE shows a comparable average F1-score to IF, but
a lower F1-score particularly in more complex attack scenarios
(i.e., attack 1.1, attack 3.3), indicating its relative difficulty in
capturing all anomalies compared to other models. Fig. 8 shows a

LSTM-AE performance across HTTP/2 attacks.

detailed performance of LSTM-AE which consistently achieved
the highest F1-score across all HTTP/2 attacks, highlighting its
superior ability to capture temporal dependencies in 5G network
data. Notably, it has higher precision for Attack 1.1 or Attack 3.1
depicting the ability of LSTM-AE to detect them. However, a
higher recall is obtained for the remaining attacks, showing the
model struggles to correctly detect them. The results suggest
that although LSTM-AE is the most robust, further fine-tuning
and optimization of all models are necessary to enhance their
performance, especially in complex scenarios.
To better evaluate the LSTM-AE model across six distinct
attacks, we rely on the Receiver Operating Characteristic (ROC)
curves. An ROC curve illustrates the trade-off between the False
Positive Rate (FPR) and the True Positive Rate (TPR) across
all thresholds [56]. The Area Under the ROC Curve (AUC) is
a commonly used metric in conjunction with the ROC curve,
providing an aggregated measure of the model’s performance
over all thresholds. An AU C = 1 indicates a perfect model
capable of achieving T P R = 1 and F P R = 0 with an ideal
threshold. Fig. 9 showcases the performance of the LSTM-AE
model tested over six attacks. With AUC values ranging from
0.87 to 0.97 across HTTP/2 attacks, the results highlight the
model’s ability to detect anomalies effectively. However, the
variation in AUC across attacks emphasizes the impact of attack
complexity and feature relevance on the detection performance.
We analyzed the LSTM-AE model’s training and detection
time efficiency to examine its scalability. The model processes
input batches with low memory overhead and <50 millisecond
detection time per 1,000 records on a standard GPU, making
it suitable for near real-time detection tasks. Its architecture
also supports parallelization across slices or functions. These
characteristics suggest that the model can scale to larger deployments by replicating across multiple nodes in a 5G environment,
maintaining consistent performance.
IX. COMPARISON WITH THE STATE OF THE ART
Despite the increasing reliance on HTTP/2 as the primary
signaling protocol in 5G SBA, there remains a significant gap in

WEHBE et al.: HTTP/2 DOS ATTACKS IN 5G NETWORKS: IMPACT ANALYSIS AND ANOMALY DETECTION

Fig. 9.

10073

AUC-ROC of LSTM-AE across HTTP/2 attacks.

the literature regarding the empirical analysis and detection of
HTTP/2-based attacks within this context. Existing works either
lack experiments or provide only a limited evaluation of specific
attack types. For example, [11], [12] provide general overviews
of signaling security in 5G networks and mention potential
HTTP/2-related risks. However, their studies are theoretical
and do not include simulation, detection, or attack modeling.
Similarly, [57] highlighted flaws in HTTP/2 design but focused
on general web environments rather than 5G-specific systems.
Several studies have experimentally analyzed HTTP/2 attacks, but mostly outside the 5G context. [25], [26], [58] demonstrated slow-rate DoS attacks using settings flooding, connection
preface abuse, and delayed streams, proposing detection based
on event-sequence analysis. [22], [28] explored asymmetric
multiplexing-based attacks, while [59] proposed intelligent feature selection techniques for detecting HTTP/2 threats. However, these efforts did not consider the 5G SBA architecture,
limiting their relevance to 5G networks. In addition, [14] focused
on HTTP/2 attack traffic generation using 5Greplay, allowing
replay-based simulation of protocol-level threats. While the tool
supports traffic generation, the study did not include evaluations
of detection performance, impact on 5G functions, or dataset
release for benchmarking.
In contrast, [13] is the only work that emulates HTTP/2 attacks
in 5G SBA. While this study takes an important step forward, it
focuses exclusively on SMAs and lacks coverage of other critical
HTTP/2 attack vectors, such as rapid reset and slow-rate attacks.
Furthermore, [13] does not release its dataset publicly, limiting
reproducibility and comparative research across the field. The
detection method used in [13] relies on AE. We test the AE with
the six HTTP/2 attacks, which report an average F1-score of
83.28%. These results surpass those reported in [13] in terms of
detection accuracy and the range and realism of attack scenarios
covered.
Our work addresses these limitations by significantly expanding the attack coverage and introducing a detailed,

practical evaluation of six HTTP/2 attack variants: two SMAs
(Request/Response and Subscribe/Notify), one rapid reset attack (CVE-2023-44487), and three slow-rate attacks (based on
settings frame, connection preface, and window size manipulation). All attacks were implemented and evaluated on a fully
standalone 5G testbed, adhering to 3GPP standards to ensure
a realistic emulation of 5G network interactions and control
plane behavior. Additionally, this study is the first to generate
and publish a comprehensive dataset capturing both benign and
malicious HTTP/2 traffic within a real 5G SBA environment.
This dataset includes flow-based features commonly used in
anomaly detection and is structured to support reproducibility,
benchmarking, and further research on 5G network security.
In summary, unlike [11], [12], which remains theoretical,
and [13], which is limited in scope and effectiveness, our work
delivers a comprehensive, practical, and publicly reproducible
framework for evaluating the impact of HTTP/2 attacks on 5G
SBA. It also provides a solid benchmark for developing and
testing advanced anomaly detection models specifically tailored
to the security challenges of HTTP/2 in next-generation mobile
networks.
X. CONCLUSION
In conclusion, this work presented the first practical study
of various HTTP/2 attacks in 5G SBA using the open-source
free5GC testbed and UERANSIM, adhering to 3GPP standards.
For instance, our emulation showed that an attacker who managed to compromise an NF can cause harm to a 5G network
through HTTP/2 DoS attacks and that HTTP/2 settings configuration across the different 5G NFs play a crucial role in securing
5G networks against such exploitation. Further, our emulations
were leveraged to offer the first public dataset for anomaly detection in a 5G network. The dataset depicted flow-based features
of benign and six different HTTP/2 attacks traffic, including two
versions of HTTP/2 stream multiplexing attacks, HTTP/2 rapid

10074

IEEE TRANSACTIONS ON MOBILE COMPUTING, VOL. 25, NO. 7, JULY 2026

reset attacks, and three variations of HTTP/2 slow rate attacks.
Finally, we presented three machine learning models, including
AE, LSTM-AE, and IF, that detected HTTP/2 attacks with a
respective average F1-score of 92.24%, 83.28%, and 84.34%.
These models can serve as benchmarking algorithms for future
research.
Future work will focus on refining and combining the proposed models through ensemble learning, while incorporating
diverse feature types such as flow-based, temporal, and protocolspecific features to improve detection accuracy and robustness
against sophisticated and evolving HTTP/2 threats in 5G networks.
ACKNOWLEDGMENT
The authors thank Dr. Makan Pourzandi, Dr. Amine
Boukhtouta, Dr. Luis Suárez, and Dr. Boubakr Nour from Ericsson Research, for their invaluable feedback.
REFERENCES
[1] B. Christine Jost, “Security for 5G service-based architecture: What
you need to know,” 2020. Accessed: Mar. 18, 2022. [Online]. Available: https://www.ericsson.com/en/blog/2020/8/security-for-5g-servicebased-architecture
[2] 3GPP, “5G; Security architecture and procedures for 5G System: TS
33.501 v.17.5.0,” The 3rd Generation Partnership Project (3GPP), 2022.
[3] 3GPP, “5G; System architecture for the 5G System: TS 23.501 v.17.5.0,”
The 3rd Generation Partnership Project (3GPP), 2022.
[4] 3GPP, “5G; 5G System; Technical Realization of Service Based Architecture; Stage 3: TS 29.500 v.17.7.0,” The 3rd Generation Partnership Project
(3GPP), 2022.
[5] A. Dutta and E. Hammad, “5G security challenges and opportunities: A
system approach,” in Proc. IEEE 3rd 5G World Forum, 2020, pp. 109–114.
[6] IETF, “Hypertext transfer protocol version 2 (HTTP/2) - RFC 7540,”
Internet Engineering Task Force (IETF), 2015.
[7] 3GPP, “5G; Security architecture and procedures for 5G System: TS
33.501 v.17.5.0,” The 3rd Generation Partnership Project (3GPP), 2022.
[8] R. Khan, P. Kumar, D. N. K. Jayakody, and M. Liyanage, “A survey on
security and privacy of 5G technologies: Potential solutions, recent advancements, and future directions,” IEEE Commun. Surveys Tuts., vol. 22,
no. 1, pp. 196–248, First Quarter 2020.
[9] M. Akon, T. Yang, Y. Dong, and S. R. Hussain, “Formal analysis of access
control mechanism of 5G core network,” in Proc. ACM SIGSAC Conf.
Comput. Commun. Secur., 2023, pp. 666–680.
[10] ENISA, “Security in 5G Specifications Controls in 3GPP Security Specifications (5G SA),” 2021.
[11] N. Wehbe, H. A. Alameddine, M. Pourzandi, E. Bou-Harb, and
C. Assi, “A security assessment of HTTP/2 usage in 5G servicebased architecture,” IEEE Commun. Mag., vol. 61, no. 1, pp. 48–54,
Jan. 2023.
[12] X. Hu, C. Liu, S. Liu, W. You, and Y. Zhao, “Signalling security analysis:
Is HTTP/2 secure in 5G core network?,” in Proc. 10th Int. Conf. Wireless
Commun. Signal Process., 2018, pp. 1–6.
[13] N. Wehbe, H. A. Alameddine, M. Pourzandi, and C. Assi, “5GShield:
HTTP/2 anomaly detection in 5G service-based architecture,” in Proc.
2023 IFIP Netw. Conf., 2023, pp. 1–9.
[14] F. G. Caccavale, H.-N. Nguyen, A. Cavalli, E. Montes De Oca, and W.
Mallouli, “HTTP/2 attacks generation using 5GREPlay,” in Proc. 18th
Int. Conf. Availability Rel. Secur., 2023, pp. 1–7.
[15] r. Communications security and interoperability council VIII working
group 1: 5G signaling protocols security, “Report on security vulnerabilities in http/2,” Communications security, reliability, and interoperability
council VIII, 2022.
[16] Free5GC, “Free5GC,” Free5GC, 2021. [Online]. Available: https://www.
free5gc.org/
[17] aligungr, “UERANSIM,” 2021. [Online]. Available: https://github.com/
aligungr/UERANSIM
[18] 3GPP, “The 5G standard,” 2023. Accessed: Aug. 2023. [Online]. Available: https://www.3gpp.org/

[19] R. M. A. Molina, N. Wehbe, H. A. Alameddine, M. Pourzandi, and C.
Assi, “Inter-slice defender: An anomaly detection solution for distributed
slice mobility attacks,” in Proc. IFIP Netw. Conf., 2024, pp. 432–440.
[20] ETSI, “Network functions virtualisation (NFV) release 4; security;
secure end-to-end VNF and NS management specification,” ETSI,
2020. [Online]. Available: https://portal.etsi.org/webapp/WorkProgram/
Report_WorkItem.asp?WKI_ID=59208
[21] E. Chatzoglou, V. Kouliaridis, G. Kambourakis, G. Karopoulos, and
S. Gritzalis, “A hands-on gaze on HTTP/3 security through the lens
of HTTP/2 and a public dataset,” Comput. Secur., vol. 125, 2023,
Art. no. 103051.
[22] A. Praseed and P. S. Thilagam, “Multiplexed asymmetric attacks: Nextgeneration DDoS on HTTP/2 servers,” IEEE Trans. Inf. Forensics Secur.,
vol. 15, pp. 1790–1800, 2020.
[23] N. V. D. (NVD), “CVE-2023-39325,” 2023. [Online]. Available: https:
//nvd.nist.gov/vuln/detail/CVE-2023-39325
[24] National Vulnerability Database (NVD), “CVE-2023-44487,” 2023. [Online]. Available: https://nvd.nist.gov/vuln/detail/CVE-2023-44487
[25] N. Tripathi and N. Hubballi, “Slow rate denial of service attacks
against HTTP/2 and detection,” Comput. Secur., vol. 72, pp. 255–272,
2018.
[26] N. Tripathi, “Delays have dangerous ends: Slow HTTP/2 DoS attacks into
the wild and their real-time detection using event sequence analysis,” 2022,
arXiv:2203.16796.
[27] A. Praseed and P. S. Thilagam, “Fuzzy request set modelling for detecting
multiplexed asymmetric DDoS attacks on HTTP/2 servers,” Expert Syst.
Appl., vol. 186, 2021, Art. no. 115697.
[28] A. Praseed and P. S. Thilagam, “Modelling behavioural dynamics for
asymmetric application layer DDoS detection,” IEEE Trans. Inf. Forensics
Secur., vol. 16, pp. 617–626, 2021.
[29] B. Hussain, Q. Du, B. Sun, and Z. Han, “Deep learning-based DDOS-attack
detection for cyber-physical systems over 5G network,” IEEE Trans. Ind.
Informat., vol. 17, no. 2, pp. 860–870, Feb. 2021.
[30] M. A. Salahuddin, V. Pourahmadi, H. A. Alameddine, M. F. Bari, and
R. Boutaba, “Chronos: DDoS attack detection using time-based autoencoder,” IEEE Trans. Netw. Service Manag., vol. 19, no. 1, pp. 627–641,
Mar. 2022.
[31] V. Pourahmadi, H. A. Alameddine, M. A. Salahuddin, and R. Boutaba,
“Spotting anomalies at the edge: Outlier exposure-based cross-silo federated learning for DDoS detection,” IEEE Trans. Dependable Secure
Comput., vol. 20, no. 5, pp. 4002–4015, Sep./Oct. 2023.
[32] S. Samarakoon et al., “5G-NIDD: A comprehensive network intrusion detection dataset generated over 5G wireless network,” 2022,
arXiv:2212.01298.
[33] G. Amponis et al., “Generating full-stack 5G security datasets: IP-layer and
core network persistent PDU session attacks,” Int. J. Electron. Commun.,
vol. 171, 2023, Art. no. 154913.
[34] I. Karim, K. S. Mubasshir, M. M. Rahman, and E. Bertino,
“SPEC5G: A dataset for 5G cellular network protocol analysis,” 2023,
arXiv:2301.09201.
[35] N. V. D. (NVD), “CVE-2016-5195,” 2019. [Online]. Available: https://
nvd.nist.gov/vuln/detail/CVE-2016-5195
[36] National Vulnerability Database (NVD), “CVE-2016-5736,” 2019. [Online]. Available: https://nvd.nist.gov/vuln/detail/CVE-2019-5736
[37] National Vulnerability Database, “CVE-2023-20864,” 2023. [Online].
Available: https://nvd.nist.gov/vuln/detail/CVE-2023-20864
[38] T. Madi, H. A. Alameddine, M. Pourzandi, and A. Boukhtouta, “NFV
security survey in 5G networks: A three-dimensional threat taxonomy,”
Comput. Netw., vol. 197, 2021, Art. no. 108288.
[39] D. Sattar, A. H. Vasoukolaei, P. Crysdale, and A. Matrawy, “A stride
threat model for 5G core slicing,” in Proc. IEEE 4th 5G World Forum,
2021, pp. 247–252.
[40] AdaptiveMobile, “A slice in time: Slicing security in 5G core
networks,” 2021. [Online]. Available: https://info.adaptivemobile.com/
network-slicing-security?hsLang=en#download
[41] G. TSG-SA3, “Key issue on misuse of OAuth 2.0 access token by
anomalous network functions, TSG-SA3 meeting #108e, S3-221787,”
3GPP, 2022. [Online]. Available: https://www.3gpp.org/ftp/TSG_SA/
WG3_Security/TSGS3_108e/Docs/S3-221787.zip
[42] 3GPP, “5G; Procedures for the 5G system (5GS) TS 123.502 v.17.5.0,”
The 3rd Generation Partnership Project (3GPP), 2022.
[43] 3GPP, “5G; 5G system; Access and mobility management services; TS
129.518 v.17.5.0,” The 3rd Generation Partnership Project (3GPP), 2022.
[44] OpenStack, “Build the future of open infrastructure,” The Wireshark Team,
2021. [Online]. Available: https://www.openstack.org/

WEHBE et al.: HTTP/2 DOS ATTACKS IN 5G NETWORKS: IMPACT ANALYSIS AND ANOMALY DETECTION

[45] Free5GC, “Free5GC-compose,” Free5GC, 2021. [Online]. Available:
https://github.com/free5gc/free5gc-compose/tree/v3.0.5
[46] Y. Raaijmakers, S. Mandelli, and M. Doll, “Reinforcement learning for
admission control in 5G wireless networks,” in Proc. IEEE Glob. Commun.
Conf., 2021, pp. 1–6.
[47] J. Navarro-Ortiz, P. Romero-Diaz, S. Sendra, P. Ameigeiras, J. J. RamosMunoz, and J. M. Lopez-Soler, “A survey on 5G usage scenarios and traffic
models,” IEEE Commun. Surv. Tut., vol. 22, no. 2, pp. 905–929, Second
Quarter, 2020.
[48] F. Mehmeti and T. F. La Porta, “Modeling and analysis of mMTC traffic
in 5G base stations,” in Proc. IEEE 19th Annu. Consum. Commun. Netw.
Conf., 2022, pp. 652–660.
[49] T. W. Team, “Wireshark, go deep,” The Wireshark Team, 2021. [Online].
Available: https://www.wireshark.org/
[50] C. I. Cybersecurity, “Cicflowmeter,” Canadian Institute for
Cybersecurity, 2020. [Online]. Available: https://github.com/
CanadianInstituteForCybersecurity/CICFlowMeter/blob/master/
ReadMe.txt
[51] scikit learn, “scikit-learn,” scikit-learn Team, 2021. [Online].
Available:
https://scikit-learn.org/stable/modules/generated/sklearn.
feature_selection.VarianceThreshold.html
[52] Y. Li et al., “Self-supervised MAFENN for classifying low-labeled distorted images over mobile fading channels,” IEEE Trans. Mobile Comput.,
vol. 23, no. 8, pp. 8077–8091, Aug. 2024.
[53] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “Kitsune: An ensemble of autoencoders for online network intrusion detection,” 2018,
arXiv:1802.09089.
[54] M. Said Elsayed, N.-A. Le-Khac, S. Dev, and A. D. Jurcut, “Network
anomaly detection using LSTM based autoencoder,” in Proc. 16th ACM
Symp. QoS Secur. Wireless Mobile Netw., 2020, pp. 37–45.
[55] M. T. R. Laskar et al., “Extending isolation forest for anomaly detection
in Big Data via k-means,” ACM Trans. Cyber- Phys. Syst., vol. 5, no. 4,
pp. 1–26, 2021.
[56] H. Dalianis, “Evaluation metrics and evaluation,” in Clinical Text Mining.
Berlin, Germany: Springer, 2018, pp. 45–53.
[57] Imperva, “HTTP/2: In-depth analysis of the top four flaws of the next
generation web protocol,” 2016.
[58] N. Tripathi and A. K. Shaji, “Defer no time, delays have dangerous ends:
Slow HTTP/2 DoS attacks into the wild,” in Proc. 14th Int. Conf. Commun.
Syst. Netw., 2022, pp. 194–198.
[59] E. Adi and Z. Baig, “Intelligent feature selection for detecting HTTP/2
denial of service attacks,” 2017.

10075

Nathalie Wehbe (Member, IEEE) received the
BSc and MSc degrees in software engineer from
Antonine University, Lebanon, in 2016, and the PhD
degree in information and systems engineering from
Concordia University, Canada, in 2025. Her current
research interests include the areas of 5G networks,
security, anomaly detection, and machine learning.

Hyame Assem Alameddine (Member, IEEE) received the PhD degree in information and systems
engineering from Concordia University, Canada, in
2019. She is currently a senior specialist in security
automation for mobile networks with Ericsson Research, Canada, and an affiliated assistant professor
with Concordia University, Canada. Before joining
Ericsson, she served as a postdoctoral fellow with
the Cheriton School of Computer Science, University
of Waterloo, Canada, between 2019 and 2020. Her
current research interests include cybersecurity, 5G
networks, O-RAN, intent-based networking, anomaly detection, attack mitigation, network slicing, ML/AI, edge computing, network management, network
function virtualization, and Internet of Things. She serves as a technical program
committee member and a member of the organizing committees at multiple
international conferences and is a reviewer for various journals and magazines.

Chadi Assi (Fellow, IEEE) received the PhD degree
from CUNY, where his thesis received the Mina Rees
Dissertation Award. He is a professor with Concordia
University, holding a university research chair. His
research interests include networks, cybersecurity,
cyber threat intelligence, and 5G technologies.
PAPER_TEXT
