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
# [783] Replica-Based Moving Target Defense Against Injection Attacks in Software-Defined Industrial Control Systems
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
编号：783
题名：Replica-Based Moving Target Defense Against Injection Attacks in Software-Defined Industrial Control Systems
年份：2026
DOI：10.1109/tdsc.2026.3652652
来源：IEEE Transactions on Dependable and Secure Computing
PDF：paper/10.1109_TDSC.2026.3652652.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：恶意流量、暗网与攻击检测
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\783.txt
- 原始字符数：97987
- 本次发送字符数：97987
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 3, MAY/JUNE 2026

5163

Replica-Based Moving Target Defense Against
Injection Attacks in Software-Defined Industrial
Control Systems
Xabier Etxezarreta , Federico Turrin , Iñaki Garitano , Mikel Iturbe , Urko Zurutuza ,
and Mauro Conti , Fellow, IEEE

Abstract—Recent incidents have demonstrated the increasing
vulnerability of Industrial Control Systems (ICSs) to sophisticated
and targeted attacks orchestrated by adversaries with high motivation, resources, and domain knowledge. Among these threats,
False Data Injection (FDI) attacks have emerged as one of the main
security threats to ICSs, involving the deliberate manipulation or
injection of false data into the control system to deceive or disrupt
operations. FDI attacks pose a significant risk due to their high
capacity of concealment and ability to evade intrusion detection
systems that rely on accurate ICS models. In this paper, we present
DEFCLON, a novel Software-Defined Networking (SDN)-based Moving Target Defense (MTD) approach against FDI attacks. DEFCLON proactively replicates network packets across multiple network paths and adaptively selects a single path using a signaling
game model to reach the destination end-device. We demonstrate
the effectiveness of our approach through simulations, numerical
analysis, and experiments on ICS network traffic and topologies.
Experimental results show that DEFCLON is able to not only mitigate
the effects of FDI attacks, but also to introduce different levels of
uncertainty without degrading network performance, significantly
increasing the difficulty for adversaries to gather information and
launch attacks.
Index Terms—Moving target defense (MTD), industrial control
systems, software-defined networking (SDN), game theory,
injection attacks.

I. INTRODUCTION
NDUSTRIAL Control System (ICS) refers to a category
of computerized systems used to monitor and control industrial processes in sectors such as manufacturing, energy,

I

Received 26 March 2024; revised 15 October 2025; accepted 1 January 2026.
Date of publication 12 January 2026; date of current version 12 May 2026. This
work was supported in part by R&D&I project under Grant PLEC2024-011222
and in part by the Spanish Government’s Ministry of Science, Innovation
and Universities under Grant MICIU/AEI/10.13039/501100011033. The work
of Xabier Etxezarreta, Iñaki Garitano, Mikel Iturbe, and Urko Zurutuza was
supported in part by Research Group under Grant IT1870-26 and in part
by the Department of Science, Universities and Innovation of the Basque
Government. (Corresponding author: Xabier Etxezarreta.)
Xabier Etxezarreta, Iñaki Garitano, Mikel Iturbe, and Urko Zurutuza are with
Data Analytics and Cybersecurity (DANZ) research group, Electronics and
Computing Department, Mondragon University, 20500 Arrasate-Mondragon,
Spain (e-mail: xetxezarreta@mondragon.edu; igaritano@mondragon.edu; miturbe@mondragon.edu; uzurutuza@mondragon.edu).
Federico Turrin is with the Department of Mathematics, University of Padova,
35121 Padua, Italy, and also with SpritzMatter srl, 35121 Padua, Italy (e-mail:
federico.turrin@spritzmatter.com).
Mauro Conti is with the Department of Mathematics, University of Padova,
35121 Padua, Italy, and also with Örebro University, 70182 Örebro, Sweden
(e-mail: mauro.conti@unipd.it).
Digital Object Identifier 10.1109/TDSC.2026.3652652

water management, transportation, and more, including Critical
Infrastructures (CIs) [1]. ICSs play a crucial role in automating
and optimizing complex industrial operations by controlling and
managing physical processes, machinery, and equipment. These
systems typically consist of a combination of hardware, software, and network infrastructure. They are designed to collect
data from various sensors and devices in real time, analyze that
data, and initiate control actions to maintain optimal operation
and safety within industrial facilities.
In the past, due to the critical nature of these systems, ICSs
were traditionally isolated from other networks, ensuring a high
level of security and stability [2]. However, with the advent of the
IT-OT (Information Technology-Operational Technology) convergence, the landscape has changed, giving rise to new threats
and challenges [3]. This convergence has brought numerous
benefits, including increased efficiency, improved data analysis,
and enhanced decision-making capabilities. However, it has also
introduced vulnerabilities and exposed ICSs to new risks. As
ICSs become more connected to IT networks and the Internet,
they become more susceptible to malicious activities. Attackers
now have a broader attack surface to target, and a successful
breach of an ICS can have severe consequences, including operational disruptions, financial losses, and even safety hazards.
Among the significant threats to ICSs, False Data Injection
(FDI) attacks pose a particularly grave risk due to the growing
connection to IT networks and the Internet. These attacks can
involve malicious actors injecting false or manipulated data
into the ICS traffic transmitted from the network, potentially
resulting in severe consequences [4].
A major concern is the use of unencrypted industrial protocols
to transmit data. Industrial protocols such as Modbus, DNP3, and
OPC were originally designed for closed, isolated environments
where security was not a primary concern. As a result, these
protocols often lack encryption and authentication mechanisms,
making them highly vulnerable to interception and manipulation
by attackers. In addition, many ICSs operate in real time with
strict latency constraints. For example, in power systems, IEC
61850 standards require fault isolation and protection services
to meet a latency limit of 3 ms. However, the implementation
of access control and cryptographic measures can introduce
significant delays that exceed these latency requirements and
disable essential real-time ICS operations [5]. Recent studies
of real-world ICS traffic over the Internet have reported the

1545-5971 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

5164

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 3, MAY/JUNE 2026

vulnerabilities of these systems [6], [7], highlighting a lack of
security features in their communications.
To address FDI attacks, researchers have employed fault
diagnosis and bad data detection techniques (e.g., least squares
method [8] or Kalman filter [9]). However, most of these detectors typically rely on an accurate ICS model, which affects
the precision and reliability of intrusion detection, allowing
an attacker that possesses knowledge of the ICS model to
design stealthy FDI attacks to evade these intrusion detection
systems [10]. In fact, one of the critical factors contributing to
the success of these attacks in ICS is the ability of attackers to
gain extensive knowledge about the topology and architecture of
the targeted ICS during the reconnaissance phase. As adversaries
accumulate deeper knowledge about the targeted system, their
capacity to launch progressively more sophisticated, stealthy and
impactful attacks escalates.
To invalidate the knowledge-gathering and stealth capabilities
of attackers, Moving Target Defense (MTD) has been proposed
to counter FDI attacks [11]. MTD is a dynamic security approach that aims to counteract the advantage gained by attackers
through increasing system complexity and uncertainty. Rather
than relying on the static nature of ICS, MTD introduces constant
variability and unpredictability into the system’s characteristics, making it significantly more challenging for adversaries
to gather accurate information, hindering the attack design and
implementation process. Nonetheless, deciding how often to
apply MTD countermeasures poses a challenge in establishing
a trade-off between defense performance and attack surface exposure time. Longer intervals can result in an extended window
of vulnerability, allowing attackers to carry out their malicious
activities. Conversely, short intervals can result in an inefficient
allocation of defensive resources.
Therefore, it is particularly important to design an MTD
approach against FDI attacks that dynamically adapts the attack
surface to changing threat scenarios without the need for an
ICS model. The dynamic aspect of MTD adds an extra layer of
complexity, requiring network orchestration technologies and
tools to implement these types of defenses. Software-Defined
Networking (SDN) has become a recurring technology in many
research works that propose the use of MTD for network security [12]. As defined in RFC 7426 [13], SDN is an approach
to network programmability, meaning the ability to dynamically
initialize, control, modify and manage network behavior through
open interfaces. To achieve this, the control plane is separated
and centralized in an external entity called SDN controller, while
the data plane remains on the network devices, focusing on
packet forwarding functionality. SDN introduces a number of
advanced capabilities, including dynamic network configuration, centralized control, granular network traffic analysis, flexible policy enforcement, automated intrusion response, continuous monitoring and analysis, and real-time incident response.
These capabilities are difficult to achieve using traditional networking technologies, but they are essential for the development
of adaptive MTD. Currently, the integration of SDN in industrial
environments is still in its early stages of development [14].
However, SDNs have already been successfully implemented
in IT environments, and several studies have demonstrated

their effectiveness in developing security solutions for ICS,
particularly in the attack detection and response field [14],
[15], [16].
To this end, in this paper we propose DEFCLON, a novel
SDN-enabled MTD framework to mitigate the impact of FDI
attacks in ICS. Our focus is on creating proactive and adaptive
network configurations that effectively change and adapt the
existing attack surface, making it more difficult for adversaries
to perform FDI attacks. Building upon previous research on
MTD, we propose a multi-layered MTD strategy that is centrally implemented on top of the SDN controller. DEFCLON
proactively replicates industrial network packets across different
network paths, reducing the ability to intercept network traffic
and limiting the ability of adversaries to gather industrial process
knowledge. Among the different paths, DEFCLON incorporates
an adaptive system based on a signaling game model [17], that
ensures that paths exhibiting suspicious behavior are not selected
for transmitting data to the destination end-device. Our results
demonstrate that DEFCLON effectively mitigates FDI attacks in
ICS. It successfully prevents attack traffic from reaching the destination device, even compared to a fully random/non-adaptive
traffic replication strategy. In summary, the contributions of this
paper are as follows:
r We propose a novel SDN-enabled MTD framework to
mitigate FDI attacks. The framework replicates industrial
network packets from a selection of different paths randomized over time. From the pool of selected paths to
transmit packets, we select a single path to transmit data
to the destination end-device, reducing attacker’s ability to
inject packets into the industrial process.
r To further enhance the effectiveness of the replication
process, we propose a signaling game model implemented
on top of the SDN controller. The game model analyzes
packets transmitting from each path in real-time without
relying on a specific ICS model and adaptively selects one
path to send data to the intended destination device. This
adaptive approach ensures that paths displaying unusual or
suspicious behavior are not chosen for data forwarding.
r We employ a simulated SDN-enabled industrial test environment to evaluate the proposed defense approach.
Through thorough numerical analysis and evaluation of
the results obtained, we demonstrate the effectiveness of
the proposed MTD framework in mitigating FDI attacks in
ICS.
The rest of the paper is organized as follows. In Section II,
we provide a discussion of related work and in Section III, we
define the threat model. Section IV describes DEFCLON treating
its theoretical aspects. Then, we present the experimental setup
and results in Sections V and VI. We discuss the limitations of
the proposed work in Section VII, and finally, we conclude this
work on Section VIII.
II. RELATED WORK
In this section, we discuss and provide an overview of existing research and literature relevant to this work. First, we
present research efforts on different MTD techniques. Second,

ETXEZARRETA et al.: REPLICA-BASED MTD AGAINST INJECTION ATTACKS IN SOFTWARE-DEFINED INDUSTRIAL

5165

strategies. If the interval is too long in a proactive strategy, attackers have enough time to compromise the system. Conversely, if
the interval is too short, MTD may be triggered unnecessarily,
consuming defense resources. To overcome this, we propose
a hybrid approach that combines shuffling and redundancybased MTD with proactive and adaptive MTD mutations using
a signaling game model. This approach allows operations to
adapt to both normal and threat scenarios, without relying on a
completely random approach.
Fig. 1. Differences between proactive and adaptive MTD [18]. The blue
vertical lines represent a proactive MTD strategy that is triggered at fixed time
intervals, while the dashed orange vertical line represents an adaptive MTD
strategy that is triggered by an event.

we provide insights into the applicability of signaling games for
attack mitigation. Finally, we analyze different MTD techniques
proposed in the literature against FDI attacks.
A. Moving Target Defense Techniques
The goal of MTD techniques is to enhance the security of
computer systems and networks by constantly changing their
attack surface and making them more challenging to exploit.
Different MTD techniques can be classified according to their
operational area [18].
Shuffling-based MTD techniques employ dynamic randomization of system configurations. This randomization process
obfuscates the configurations, making it difficult for attackers to
gather information during the reconnaissance phase. As a result,
the attack surface is reduced, and the complexity of identifying
and exploiting vulnerabilities is increased. Examples within this
category include IP address randomization [19], port number
randomization [20], network path/route randomization [21], and
packet header randomization [22]. Furthermore, several proposals have been proposed that combine multiple shuffling-based
techniques. For instance, authors in [23] propose a low-delay
approach involving IP, MAC, and port numbers randomization
to mitigate reconnaissance attacks in industrial networks.
Diversity-based MTD refers to the provision of equivalent
services using different implementations, enhancing system resilience. Code diversity aims to divide a program into components that can be executed in different execution environments [24]. Software diversity techniques involve deploying alternative versions of web servers, applications, or virtual servers
to enhance network resilience [25]. Furthermore, programming
languages diversity helps to mitigate risks of SQL or code
injection attacks [26].
Redundancy-based MTD involves deploying systems that offer the same functionality in order to enhance reliability and
availability. As an example, authors in [27] propose network
session redundancy in Cyber-Physical Systems (CPS) communications to combat traffic analysis attacks.
Hybrid MTD consists of combining shuffling, diversity and
redundancy-based MTD techniques [28], [29].
A major challenge in proactive MTD solutions is determining
the optimal timing for applying MTD countermeasures. Fig. 1
illustrates the difference between proactive and adaptive MTD

B. Signaling Games in Cybersecurity
Game theory has emerged as a framework for understanding and analyzing strategic interactions between individuals or
entities. It has found applications in various fields, and one
area where game theory has gained significant relevance is
cybersecurity [30], providing insights into the strategic decisions
made by both attackers and defenders. One particular aspect
of game theory that has proven valuable in this context is
signaling games. These games involve players who have incomplete information and strategically send signals to influence the
behavior of others. In the field of attack mitigation, signaling
games provide a framework for modeling interactions between
attackers and defenders, where defenders do not know exactly
whether the signal received comes from a legitimate user or an
attacker. Aydeger et al. [31] propose an adaptive SDN-enabled
approach to mitigate DDoS attacks. Their method involves
the randomization of network paths and employs a signaling
game model to make informed decisions on when and where
to apply this randomization. Priyadarsini et al. [32] present a
framework for both mitigating and evaluating attacks targeting
SDN controllers. Their approach uses a signaling game to model
communications between switches and SDN controller. Signaling games have also proven to be a valuable tool for integrating
Moving Target Defense (MTD) techniques with cyber deception
strategies. Zhou et al. [33] introduce an approach that combines cyber deception with multiple MTD strategies, such as IP
randomization, path randomization, and response time adaptation. Furthermore, they introduce a defender-led signaling game
model, allowing for the proactive transmission of deceptive
signals to attackers. This approach addresses the inherent information asymmetry in cyberattacks, giving defenders a strategic
advantage.
C. MTD for FDI Attacks Mitigation
The effectiveness of FDI attacks in evading detection systems
has been well established, and attackers with extensive knowledge of the parameters of the ICS model pose a significant threat.
As a result, current MTD strategies for FDI attacks primarily
focus on limiting the attacker’s ability to gain an in-depth understanding of the system or detecting these threats by revealing
attackers in MTD environments [34], [35].
A prominent MTD strategy in power systems involves altering
the physical layer using Distributed Flexible AC Transmission
System (D-FACTS) devices [36], [37] to invalidate an attacker’s
knowledge for launching stealthy FDI attacks. However, this
approach has significant limitations, as its effectiveness depends

5166

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 3, MAY/JUNE 2026

TABLE I
A COMPARATIVE ANALYSIS OF DIFFERENT MTD STRATEGIES AGAINST FDI ATTACKS

on strict topological conditions [36]. Due to these constraints and
the high infrastructure costs of D-FACTS, subsequent research
has focused on developing more cost-effective solutions by
minimizing the number of required devices and their operational
expenses, while also analyzing the defense’s impact on system
stability [38].
As an alternative to parameter perturbation, some researchers
have proposed topology switching as an MTD mechanism [39].
This approach reconfigures the system topology, for instance
through busbar switching, leveraging existing spare busbars to
serve as a security measure without requiring extra investment.
To manage the complexity of selecting optimal switching actions, the defense process was modeled as a Markov Decision
Process (MDP) and solved using Deep Reinforcement Learning
(DRL) to achieve fast and efficient decision-making suitable for
large-scale systems.
For instance, in [40], a reactive and proactive MTD mechanism is proposed that dynamically changes the controller,
altering cyber-physical system parameters, making it difficult
for attackers to perform reconnaissance in the system and to
detect compromised actuators and sensors. Similarly, the authors
in [41] propose a framework for detecting Stuxnet-like attacks
and limiting adversary knowledge by actively perturbing sensor
and control commands. To counter the emergence of adversarial FDI attacks designed to bypass even advanced Machine
Learning (ML)-based detectors, other approaches deploy a pool
of diverse Deep Neural Network (DNN) models to reduce an
attack’s transferability, which was combined with physics-based
perturbations to enhance detection accuracy [37]. Another strategy employs proactive data replication by integrating new IoT
devices to duplicate control commands and sensor readings,
thereby limiting an attacker’s state estimation capabilities and
reducing the likelihood of compromised data reaching its destination [42], [43].
However, existing approaches present several shortcomings,
as many depend on accurate system models which can be
difficult to maintain and scale. Furthermore, proactive MTD
strategies that rely on fixed randomization frequencies struggle
to adapt to evolving threats. To address these issues, we propose
an SDN-enabled proactive and adaptive traffic replication framework to mitigate FDI attacks in the ICS domain. Our framework
leverages the central management of SDN to distribute traffic
across multiple paths and, without relying on an ICS model,
employs a signaling game to detect suspicious activity. This
allows the system to adaptively manage the path selection pool,

preventing paths with suspicious behavior from reaching the
destination and overcoming the challenge of defining an optimal randomization frequency. Table I presents a comparative
analysis of different MTD strategies against FDI attacks in ICS.
III. THREAT MODEL
For our threat model, we consider an ICS network that is
centrally managed using an SDN controller. We define the
attacker’s characteristics and the attack process as follows:
Attackers’ Capabilities: An attacker within an industrial network poses a significant threat to the integrity of industrial
communications. The attacker’s potential capabilities are:
r Eavesdropping: The attacker can intercept data packets
transiting the network from any communication channel
or path. This allows them to gather sensitive information
or monitor system behavior. There are many techniques
on how an attacker could eavesdrop data packets flowing
through the SDN network. Examples of such techniques
include ARP spoofing [44], attacks to the topology discovery [45] or by physically connecting to the communication
link, all of them launched from the data plane without
needing access to the SDN controller.
r Data Injection: The attacker can inject false data into the
network traffic, potentially manipulating control signals or
disrupting system operations. Examples of an adversary’s
actions may include random attacks, carefully designed
attacks, reply attacks, stealthy attacks or packet corruption
attacks, to name a few.
We also consider the following limitations or assumptions:
r Attacker Localization: The attacker resides within the data
plane, meaning they have access to the network traffic but
not directly to the control plane (SDN controller).
r Network Redundancy: Our framework relies on the existence of network redundancy, a common feature in industrial networks designed for high availability and fault
tolerance. We assume there are at least two communication
paths between industrial devices. Ideally, these paths are
fully disjoint, meaning they share no common network
links or nodes. This configuration maximizes the effectiveness of our defense, as the compromise of one path
does not affect another. In scenarios with overlapping
paths, where paths share a common segment or node, an
attacker compromising that segment could impact multiple
replicated streams simultaneously. While this reduces the

ETXEZARRETA et al.: REPLICA-BASED MTD AGAINST INJECTION ATTACKS IN SOFTWARE-DEFINED INDUSTRIAL

Fig. 2.

5167

Attack on control packets (1) and attack on sensor packets (2).

available path diversity, the signaling game would identify
all compromised paths as suspicious. As long as at least
one uncompromised path to the destination exists, it can
be selected for secure data delivery.
r Partial Network Compromise: The attacker can compromise multiple network paths simultaneously, but not the
entire network at once. This reflects a scenario where
attackers may gain access to specific segments/paths
of the network, but face challenges achieving complete
control.
FDI Attack Process: We adopt a threat model consistent with
established research on FDI attacks in control systems [5], [46],
[47]. This model presumes an attacker has achieved a Man-inthe-Middle (MitM) position on a network communication path,
enabling them to eavesdrop on, intercept, and modify or inject
data packets in transit. The attacker’s goal is to manipulate the
physical process by sending false data to critical devices. As
shown in Fig. 2, this can manifest as tampering with sensor
readings sent to a controller (yi (t) = yia (t)) or altering control
commands sent to an actuator (ui (t) = uai (t)). By injecting
carefully crafted false values, the attacker seeks to mislead the
system’s control logic without being detected, potentially causing physical damage or operational failure. Our work directly
counters this threat by making it difficult for the attacker’s
injected data to be the one selected for delivery to the end device.
We formalize the measured variables ui (t) and yi (t) as

ui (t), yi (t) for t ∈
/ Ta


ui (t), yi (t) =
(1)
uai (t), yia (t) for t ∈ Ta
such that ui (t), yi (t) and uai (t), yia (t) correspond to the ith original and modified/tampered packet at t ≤ 0 ≤ T respectively. T
is the duration of the simulation, and Ta is the duration interval
of the attack.
The attacker can decide whether to remain idle on the network
or compromise the integrity of the industrial communication.
IV. DEFCLON: AN SDN-ENABLED PROACTIVE AND ADAPTIVE
DATA REPLICATION FRAMEWORK
In this section, we introduce the SDN-based data replication
framework. First, we provide an overview of the proposed
defense architecture. Next, we introduce the proactive path
activation and data replication mechanism, which plays a critical
role in the proposed framework by distributing multiple copies
of network packets over different paths. Finally, we present the

Fig. 3.

DEFCLON architecture and components overview.

adaptive path selection algorithm, which uses a signaling game
model to select which paths are safe to reach the destination
device.
A. Architecture
In order to explain the proposed framework in detail, we
provide an overview of the architecture and the main components
of DEFCLON. Fig. 3 presents the overall architecture which
includes two main components: the proactive path activation
and data replication, and the adaptive path selection component.
These two components are centrally implemented in the SDN
controller. The southbound interface serves as the communication link between the SDN controller (control plane) and the
forwarding devices in the network (data plane). It allows the
controller to instruct the devices on handling network traffic
based on the defined policies and rules. DEFCLON uses OpenFlow [48] as southbound interface communication protocol.
OpenFlow enables the controller to configure flow tables within
the forwarding devices, facilitating the dynamic control over
packet forwarding behavior.
The proactive path activation and data replication component
is responsible for managing the data replication through different paths of the network. Paths are randomized over time,
creating intermittent data forwarding on the paths and making
it difficult for eavesdroppers to gather complete and continuous
information. This component performs the following three key
functions:
r Network Discovery: Implements network discovery to
identify hosts and links in the network. Hosts are discovered through Address Resolution Protocol (ARP, RFC826)
messages and links are discovered through Link Layer
Discovery Protocol (LLDP, IEEE 802.1AB) messages. The
network is continuously monitored to identify changes and
to maintain an updated topology view. It is important to
note that while automated discovery is used for convenience, it is not a strict requirement. In environments where
protocols like ARP are restricted, the network topology

5168

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 3, MAY/JUNE 2026

Fig. 5.

ICS data replication with an ALL type OpenFlow group.

reaching the target device, thanks to our adaptive path selection
mechanism. More details on these two components are provided
in Sections IV-B and IV-C.
B. Proactive Path Activation and Data Replication
Fig. 4. Proactive and adaptive components of DEFCLON. The proactive component consists of replicating data from a subset of network paths that are randomized over time. The adaptive component consists of modeling the behavior
of each path with a signaling game model to dynamically forward or drop the
paths.

graph can be manually configured and provided to the
SDN controller. DEFCLON’s core defense mechanisms only
require an updated network graph and are independent of
the discovery method used.
r Data Replication: Selects a group of paths, performs copies
of the original ICS data and sends each copy from selected
paths. This module is also the responsible for changing the
path selection over time.
r Multipath forwarding: Manages forwarding rules in the
network that send the replicated data from the source to
the intended destination from the set of paths selected by
the Data Replication module.
The adaptive path selection component is the responsible for
monitoring the behavior of each path using the signaling game
model and selecting a single path to send data to the destination
end-device. To achieve this, this component assigns a status
to each path: forward or drop status. On the one hand, paths
in forward state are eligible to be selected to send data to the
destination end-device. From the set of paths in forward state, a
single path is randomly selected to reach the destination device.
On the other hand, paths in drop state are not eligible to reach
the destination end-device. The status of each path is updated in
real-time using a signaling game model.
Fig. 4 provides a visual representation of the different layers
of defense in DEFCLON. An eavesdropper that intercepts network
packets in a path gathers intermittent data caused by the proactive
path activation and data replication. Meanwhile, an attacker
attempting FDI attacks on a path will face significant obstacles in

DEFCLON utilizes a multi-layered defense strategy. It begins
with an initial layer that randomly replicates industrial network
traffic across disjointed communication paths within the network. During a predetermined time interval, the SDN controller
selects a random subset of available paths from the network
topology to replicate data from the source to the destination
device. Once the interval ends, a different and randomly selected
group of paths takes over the data transmission. By adopting this
approach, if an attacker manages to compromise one of the paths,
their access to network traffic becomes intermittent, restricting
their ability to acquire new and continuous information.
Data replication is implemented using a utility called OpenFlow groups. OpenFlow groups are a utility within the OpenFlow protocol (available since version 1.1) designed to facilitate
data replication and distribution in an SDN environment. These
groups are particularly useful for tasks such as multicast and
data replication. By specifying a set of actions within a group
(also known as buckets), administrators can ensure that certain
packets are replicated and forwarded to multiple destinations
simultaneously. This is crucial for applications where data needs
to be distributed to multiple recipients or where redundancy is
necessary. As defined by the OpenFlow protocol specification,
there are many types of OpenFlow groups. In our particular
case, we use the “ALL group”, which takes any received packet
as input and duplicates the packet to be operated independently
by each group of actions (buckets). The buckets within the group
are configured to forward data packets to its corresponding path.
The internals of and OpenFlow group (ALL type) is presented
in Fig. 5.
The OpenFlow group responsible for data replication operates
within the initial forwarding device, where it intercepts all
data transmitted by the source ICS device. Subsequently, this
group distributes multiple copies of the data packets along the
designated paths established within the group. Additionally, we
include an extra bucket in the group to mirror each packet to

ETXEZARRETA et al.: REPLICA-BASED MTD AGAINST INJECTION ATTACKS IN SOFTWARE-DEFINED INDUSTRIAL

Fig. 6.

5169

Extensive form representation of the signaling game G.

the SDN controller. This allows the controller to store historical
communication packets, which the signaling game model can
later utilize to identify suspicious activities within each path.
This technique, commonly known as port mirroring or Switched
Port Analyzer (SPAN), is a common practice in industrial environments for performing packet monitoring or analysis (NISTR
8219 [49]).
This data replication strategy is particularly synergistic with
ICS design principles. Industrial networks commonly feature
path redundancy to ensure fault tolerance and high availability.
DEFCLON leverages this existing architectural feature for security. By proactively replicating traffic across these redundant
paths, we introduce uncertainty for an adversary without altering the fundamental network topology or the high-availability
requirements of the control process.
C. Adaptive Path Selection
The second layer of defense in DEFCLON is the adaptive path
selection, which ensures that only a single, non-compromised
path delivers data to the destination device. This is achieved in
two steps. First, a filtering mechanism determines which paths
are suitable for data forwarding. It uses a signaling game model
to continuously monitor and assign a status of forward or drop to
each active path. Second, from the filtered set of paths currently
in the forward state, a single path is selected randomly to transmit
its packet to the destination. This ensures that even among trusted
paths, the final selection remains unpredictable.
As data flowing from different network paths generate uncertainty, and we have incomplete information if a specific path
is operated by an attacker or not, we propose a signaling game
model to help select the optimal status for each path (drop or
forward). The model is an attacker-led multi-stage signaling
game in which the defender monitors each path individually
and updates the status of each path every time a packet is
forwarded. At the last exit node, where the different paths
converge and a single path is selected to send data to the
destination device, the node mirrors the packets received from
each path to the SDN controller using the OpenFlow protocol,
which triggers the execution of the signaling game in each
path, updating their status. The SDN controller maintains one
signaling game per path and communication direction, updating

TABLE II
NOTATION TABLE

the status each time the node mirrors a packet from a path to the
controller.
The adaptive path selection component randomly selects a
single path from the set of paths in forward state to send data
to the destination device, and discards paths in drop state from
the selection pool. Each path is continuously and individually
monitored by a signaling game model, which adaptively updates
the path’s state (drop or forward) in real-time.
In the following, we first provide an overview of the signaling
game model by defining players, messages, and action sets.
Next, we define the belief model and the payoff functions of
both players. Finally, we analyze the game processes between
players, and explore optimal strategies by calculating the Perfect
Bayesian Nash Equilibria (PBNE) [50] in the game.
1) Game Overview: The proposed signaling game model,
represented in Fig. 6, constitutes a non-cooperative game where
each path is considered as an individual sender that could be a
legitimate or an attacker. An attacker, who has gained access to
a communication path, could tamper industrial network packets
to misguide the control algorithm or inject corrupted network
packets to generate errors in the communication. The notations
used in this paper are summarized in Table II, and the necessary
definitions in this game model are listed as follows.
Players: The interaction between the sender (S) and receiver
(R) constitutes a non-cooperative game, where the attacker

5170

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 3, MAY/JUNE 2026

assumes the role of the sender, and the defender receives the
messages in the form of replicated packets. The defender applies
MTD by replicating traffic through different paths in the network
and selecting a single path to reach the destination device. Due
to the inability to distinguish between a legitimate user and
an attacker, the defender must rely on the information in the
paths to decide. The signaling game G is played individually for
each path regardless of the sender type δ ∈ Δ = {0, 1}, where
δ = 0 is considered a legitimate user whereas δ = 1 represents
an attacker.
Messages: Signaling game G is considered a multistage game
where the sender sends a set of possible messages m ∈ M =
{0, 1} and the defender receives these signals to take the corresponding action. Various messages can be formed from different
configurations, and they have the ability to influence the defender’s viewpoint on whether a path is under attack or not. Since
the space of possible messages is large, the game focuses on two
specific messages: whether the actual replicated packet differs
from the originally forwarded packet or not. Based on this,
message m = 1 indicates that the path is suspicious, whereas
m = 0 represents that the path is under normal operation.
For example, a player δ = 1 (attacker) may choose to remain
idle on the network without modifying packets (m = 0), or to
attack by modifying or corrupting packets in transit (m = 1).
Similarly, a path under normal operation δ = 0 (legitimate)
may transmit packets correctly (m = 0), or packets may be
accidentally corrupted (m = 1) in transit due to electromagnetic
interferences, physical medium issues, signal attenuation, noise,
congestion, jitter, or hardware/software malfunctions, to name
a few.
Actions: After receiving a message m ∈ M from the sender,
the defender selects an action for the path by choosing a ∈ A =
{0, 1}. Action a = 0 denotes that the path can be selected to be
forwarded to the destination, while a = 1 signifies that the path
must be dropped.
2) Belief Model: In signaling game G, the defender cannot
determine whether the traffic comes from a legitimate user or an
attacker. Consequently, the defender monitors the signals from
each path and uses that information to form a belief function
(θ) concerning the sender’s identity on each observation. The
defender has a belief per path, i.e., if the traffic of a communication is replicated from five paths, the defender will have
five different beliefs for that communication, one per path. The
belief values range between 0 and 1, 0 representing that no sign
of suspicious activity has been detected. The belief function
comprises two parts: the initial belief that is calculated statically
at the beginning of the game at t = 0 and the dynamic belief
function used to update the belief each time the defender receives
a mirrored packet from a path at t > 0.
Initial belief: At the beginning, there is no information about
any of the paths, and the same level of suspicion is applied to all
of them. Thus, at step t = 0, the defender assumes that each path
is legitimate and free from any form of attack. The initial belief
for each path at t = 0 is initialized and calculated as follows:
θn (0) = 0, n ∈ N.

(2)

This belief initialization can be adjusted if the defender has
knowledge of whether some communication paths are more
vulnerable to attack, by setting a higher initial belief if this is
the case.
Dynamic belief: The dynamic belief of a given path is crucial
for evaluating the expected payoffs for both players. This dynamic belief, denoted by θn (t), is recalculated at each step (i.e.,
t > 0) as the game is played. The (3) describes how a player’s
dynamic belief is computed, which involves two weighted factors that are combined to produce a score. Since the weights are
normalized values, the sum of the two weights is w1 + w2 = 1
(i.e., 100% ).
θn (t) = θn (t − 1) ∗ ω1 + ψ(r, rn ) ∗ ω2 , n ∈ N, t > 0.

(3)

The first factor represents a paths’s prior belief θn (t − 1),
weighted by w1 . When evaluating a client’s behavior, it is
important to consider their history of suspicious or legitimate
actions. This is because a single deviation from their typical
behavior cannot completely negate the previously observed and
learned patterns. In other words, the client’s current action
cannot completely override the belief in their historical behavior.
Therefore, to evaluate their overall performance, the prior belief
is essential to take into account the sender’s previously observed
behavior.
The second factor of the dynamic belief function measures the
dissimilarity between a given packet rn and the original packet
r previously mirrored from the initial node and stored in the
SDN controller. In the context of ICS, the dissimilarity metric,
denoted by ψ(r, rn ), is especially powerful. Unlike IT networks,
which have highly variable traffic, ICS communications are
often deterministic and cyclical (e.g., periodic sensor polling).
Therefore, a deviation captured by this metric is a strong indicator of manipulation. The dissimilarity metric is binary and is
weighted by a parameter w2 , where ψ(r, rn ) is set to 0 if the
packets are identical and 1 otherwise.
3) Payoff Model: In the following, we define the payoff
model considering all possible strategy profiles and different
player types. Let μP (δ, m, a) represent the payoff function of
player P , where P ∈ {S, R}. Both players aim to maximize
their payoffs, maintaining a balance between gain and cost.
Receiver: If the defender chooses the drop strategy (i.e., a =
1) in response to a suspicious packet sent by an attacker (i.e.,
δ = 1), the defender effectively defends the target system. Let’s
consider N as the total number of available paths, Nf as the
number of paths in the forward state, and Nd as the number of
paths in the drop state.
The receiver’s numerical gain for defending against an attacker who plays suspiciously can be quantified using the parameter gd = 1 − NNd . A higher value of Nd results in a lower
gain from dropping, while a lower value of Nd results in a
higher gain. Dropping a path also has a cost to the defender,
as it reduces the size of the path selection pool. This cost is
denoted by the parameter cd = NNd , which represents the ratio
of paths in the drop state to the total number of available paths,
N . A higher value of Nd increases the cost of dropping another
path, while a lower value of Nd decreases the cost. Therefore,
whenever the defender decides to drop a path, it will incur a

ETXEZARRETA et al.: REPLICA-BASED MTD AGAINST INJECTION ATTACKS IN SOFTWARE-DEFINED INDUSTRIAL

cost of cd . Critically, the cost of dropping a path (cd ) lies in the
reduction of path diversity, which may weaken the industrial
network’s resilience and reliability, particularly in real-time
control operations.
It is important to note that the defender only gets the gain for
dropping a path (gd ) if the player type is δ = 1 and the signal
is m = 1. This gain from correctly dropping a compromised
path (gd ) translates directly to the prevention of physical process
disruption or equipment damage.
The defender’s numerical gain for selecting forward in a path
when the received signal is m = 0 can be expressed as the
N
parameter gf = 1 − Nf . This gain is influenced by the value
of Nf , where a higher value of Nf corresponds to a lower
gain, while a lower value of Nf corresponds to a higher gain.
Functionally, the gain from forwarding a legitimate packet (gf )
represents maintaining the operational integrity and stability
of the physical process. The defender will only gain gf when
players δ = 0 and δ = 1 send signal m = 0. If a legitimate
sender δ = 0 plays suspicious m = 1 (i.e., packet corruption
during transmission) and the defender plays a = 0, the defender
action will not result in any gain, as it may generate a delay in the
network due to the retransmission carried out by the transport
layer protocol (i.e., if TCP is used).
Sender: The attacker’s main goal is to deliver the
spoofed/tampered packets to the target device. The attacker’s
gain (ga ) is achieved only if their malicious packet is selected
to reach the end-device, allowing them to directly influence the
physical process. Because of this, the attacker gets a significant
gain ga by sending a signal m = 1, and the defender decides to
apply the action a = 0. However, being active on the network
costs the attacker ca . Thus, the attacker incurs a cost of ca every
time a signal is sent, and gains ga only when the signal is m = 1
and the defender chooses a = 0. This tradeoff between gain and
cost characterizes the attacker’s strategy in the network, while
our defense aims to make this payoff difficult to achieve.
4) Signaling Game Analysis: In games with complete information or non-Bayesian games, a strategy profile is said to be
a Nash Equilibrium (NE) if every strategy in that profile is the
best response to every other strategy. In such games, each player
knows the rules of the game and has complete information about
the other players, strategies, and payoffs. However, in Bayesian
games, players have incomplete information and uncertainty
about the other players types, which affects their expected
payoffs. In these games, players aim to maximize their expected
payoffs given their beliefs about the other players. Therefore, a
strategy profile in a Bayesian game is a PBNE if every players’
strategy is the best response to their beliefs about the other
players strategies and types, and the beliefs are consistent with
Bayes rule. PBNE is a refinement of NE that takes into account
players incomplete information and the resulting uncertainty
in their decision-making. The conditions for a PBNE are the
following:
r Condition 1: After observing a message m from the sender,
the receiver must have a belief θ(δ|m) about the sender that
satisfies

δ∈Δ

θ(δ|m) = 1 and θ(δ|m) ≥ 0.

(4)

5171

r Condition 2: For all message types m ∈ M , receiver’s

strategy εR must maximize his expected payoff given the
belief θ(δ|m) about which sender type sends m, such that

θ(δ|m)μR (δ, m, a).
(5)
εR ∈ max
m∈M

δ∈Δ

r Condition 3: The sender’s (legitimate or attacker) strategy
εS must maximize his payoff given the defender’s action
a ∈ A, such that
εS ∈ max μS (δ, m, a).
m∈M

(6)

r Condition 4: If there is a type δ that satisfies senders

strategy m∗ ∈ M , the defender’s belief about the sender
type corresponding to message m must follow the Bayes
rule so that
θ(δ|m) = 

p(δ)
.
δ∈Δ∗ p(δ)

(7)

where Δ∗ refers to the set of senders that sent m∗ and p(δ)
indicates the prior probability of sender being type δ.
Definition 1: A PBNE in a signaling game is a pair of
strategies εS (m|δ) and εR (a|m), and a belief θn (t) that satisfies
conditions 1-4.
In a signaling game, there can be multiple PBNE, which
are sets of stable strategies against deviations by either player.
These PBNEs can be divided into two categories: separating equilibrium and pooling equilibrium. In a pooling equilibrium, the sender uses the same signal for multiple types
εS (m|0) = εS (m|1), and the receiver chooses the same action
regardless of the signal received. In a separating equilibrium,
on the other hand, the sender uses a particular signal to convey
information about their type to the receiver, and the receiver
uses this information to choose the appropriate action. In a
separating equilibrium, the sender’s signal is different for each
type εS (m|0) = εS (m|1).
In order to identify the existing equilibrium profiles in the signaling game G, the conditions that lead to pooling or separating
equilibriums are examined next. The values of the payoffs may
vary depending on the network topology or number of paths
available in a communication between two devices, requiring to
determine the existence of different equilibrium profiles in the
game.
Theorem 1: There is a pooling equilibrium ∀θ on m = 1 in
the signaling game G.
Proof: Suppose both sender types follow the same strategy
m = 1. In this scenario, the defender’s belief about the sender
type is determined following Bayes rule. The defender’s expected payoff μR∗ for playing a = 0 based on its belief θ is
represented by the following equation:
μR∗
a=0 = θ(−ga ) + (1 − θ)(0).

(8)

Similarly, the following equation represents defender’s expected payoff μR∗ for playing a = 1:
μR∗
a=1 = θ(gd − cd ) + (1 − θ)(−cd ).

(9)

By comparing the expected payoffs of the defender for each
of the action sets mentioned above, a belief threshold, denoted as

5172

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 3, MAY/JUNE 2026

R∗
θ∗ , can be formulated by performing μR∗
a=0 = μa=1 calculation,
obtaining the following result:

θ∗ =

cd
.
gd + ga

(10)

Assuming that θ∗ ≥ 0, the following two cases represent a
dominant strategy for the defender in this pooling equilibrium:
r θ ≥ θ∗ = cd . Action a = 1 dominates a = 0 when obgd +ga
taining a signal m = 1 and the condition θ ≥ θ∗ is satisfied.
This can be verified by comparing expected payoffs defined
in (8) and (9). Taking into account the possible deviations of
the sender, it can be observed that both sender types have
no incentives to deviate. The attacker and the legitimate
user will obtain the same payoffs in both message types,
−ca and 0 respectively.
r θ ≤ θ∗ = cd . Action a = 0 dominates a = 1 when obgd +ga
taining a signal m = 1 and the condition θ ≤ θ∗ is satisfied.
Similar to the previous case, incentives of the senders for
deviating from m = 1 must be checked when the defender
plays a = 0 in the pooling equilibrium. As observed in the
payoffs, neither type of sender has any incentive to deviate
from its strategy. In the case of the attacker, the payoff will
drop from ga − ca to −ca , while the payoff of a legitimate
user will remain 0.
Theorem 2: There is no pooling equilibrium ∀θ at m = 0 in
the signaling game G.
Proof: Following a pooling strategy in message m = 0,
defender’s best response is a = 0, obtaining a payoff of gf with
both sender types. Hence, deviations from the sender should be
taken into account considering receivers optimal response in this
pooling strategy. As a legitimate user (i.e., sender type δ = 0
) obtains 0in all strategy profiles, let only consider attackers
δ = 1 possible deviations from the equilibrium. If it deviates
from m = 0 to m = 1, the attacker will increase its payoff from
−ca to ga − ca when the defender plays a = 0. Because of this,
there is no pooling equilibrium at ∀θ on m = 0.
Theorem 3: There are two separating equilibriums on {(δ =
0, m = 0, a = 0), (δ = 1, m = 1, a = 1)} and {(δ = 0, m =
0, a = 0), (δ = 1, m = 1, a = 0)} in the signaling game G.
Proof: Let’s suppose a separating strategy where player
type δ = 0 sends m = 0 and player type δ = 1 sends m = 1.
Best response of the defender for sender type δ = 1 sending
m = 1 can be obtained by comparing gd − cd and −ga payoffs,
resulting in:
gd∗ = cd − ga .

Algorithm 1: Adaptive Path Status Selection Algorithm.

(11)

Payoffs comparison leads to the following two scenarios:
r gd ≥ g ∗ = cd − ga . The best response for the defender is
d
a = 1 when player δ = 1 plays m = 1 and a = 0 when
player δ = 0 plays m = 0. Checking possible sender strategy deviations, both δ = 0 and δ = 1 will not have incentives to deviate as they will obtain the same payoff, 0 and
−ca respectively.
r gd ≤ g ∗ = cd − ga . In this scenario, the best response
d
for the defender, when player δ = 1 plays m = 1 and
player δ = 0 plays m = 0, is a = 0. Same as the previous

Fig. 7.

The adaptive path status decision-making process in DEFCLON.

scenario, senders have no incentive to deviate from their
strategy.
Theorem 4: There is no separating equilibrium on {(δ =
0, m = 1), (δ = 1, m = 0)} in the signaling game G.
Proof: Consider a separating strategy where player δ = 0
plays m = 1 and player δ = 1 plays m = 0. In this case, the
best response of the defender to a sender δ = 1 playing m = 0
and a player type δ = 0 playing m = 1 is a = 0. Focusing on
sender type δ = 1 possible deviations, we can conclude that there
is not a separating equilibrium in this scenario. If the sender
type δ = 1 deviates by playing m = 1 instead of m = 0 and
the defender responds to that message with a = 0, the payoff of
the sender type δ = 1 will be increased from −ca to ga − ca .
Because of this, there is no separating equilibrium on {(δ =
0, m = 1), (δ = 1, m = 0)}.
Theorems 1 to 4 represent all possible PBNE in the proposed
signaling game G. The process of adaptively monitoring and
updating the status of the paths is represented in Algorithm 1 and
Fig. 7, which details the decision logic and process for assigning
a forward or drop status to an individual path.
V. EXPERIMENTAL SETUP
In this section, we present the experimental setup for validating DEFCLON: the physical process, the network topologies, and
the FDI attack implementation process.

ETXEZARRETA et al.: REPLICA-BASED MTD AGAINST INJECTION ATTACKS IN SOFTWARE-DEFINED INDUSTRIAL

Fig. 8. First stage of the Secure Water Treatment (SWaT) testbed implementation in MiniCPS.

TABLE III
SENSORS AND ACTUATORS FUNCTION, MEASUREMENTS AND STATUS

TABLE IV
WATER TANKS LEVELS CONTROL LOGIC THRESHOLDS

5173

PLC1 is tasked with monitoring the water level data received
from sensor S_WL1 and comparing it against these thresholds.
Based on this comparison, it determines whether to open or close
actuator A_P1. Additionally, PLC1 communicates with PLC2 to
obtain sensor data from S_FR2 and with PLC3 to acquire readings from sensor S_WL2. By comparing these sensor readings
against predefined thresholds, PLC1 determines the appropriate
state for actuator A_P2 (open or close).
PLC3 is responsible for managing the water level data from
sensor S_WL2, which measures the water level in TANK 2. The
primary goal here is to prevent tank overflow by comparing the
sensor reading with the HH threshold. In the event that the water
level exceeds the maximum capacity of 1200 mm (HH), PLC3
opens actuator A_P3 to reduce the risk of overflow and tries to
reduce the water level until it reaches the H threshold.
The simulation starts with an initial water level of 800 mm
in TANK 1 and 400 mm in TANK 2. Since the water level in
TANK 2 is below the threshold L (500 mm), the control process
starts with the stabilization phase by opening actuator A_P2,
and sending water from TANK 1 to TANK 2 in order to reach
the water level indicated by threshold H (800 mm). The system
is considered stabilized when both water tanks reach a water
level of 800 mm (indicated by the H threshold). When the water
level in TANK 1 falls below the L threshold (500 mm), PLC1
opens actuator A_P1 until the water level reaches the H threshold
(800 mm).
The PLCs communicate using the Ethernet/IP protocol, which
facilitates the exchange of information to control and manage
the water treatment process.

A. Physical Process
The experimental evaluation is conducted within MiniCPS 1
framework, a platform for cyber-physical system simulation and
testing introduced by Antonioli et al. in their work [51]. This
framework includes the simulation of the first of the six stages
of the Secure Water Treatment (SWaT) system [52], which is
widely used for research and experimentation in the area of ICS
security.
The first stage of the SWaT testbed, illustrated in Fig. 8,
involves two water tanks, TANK 1 and TANK 2, two flow
rate sensors (S_FR1, S_FR2), two water level sensors (S_WL1,
S_WL2), and three actuators (A_P1, A_P2, A_P3). These actuators are responsible for regulating the water flow, ensuring
it progresses to the subsequent stages of the treatment process.
Table III provides a detailed breakdown of the sensors and actuators, including their functions, measurements, and status-related
information.
The control process depends on predefined water level thresholds, which are listed in Table IV. The primary objective of the
control logic is to maintain the water level within the specified
high (H) and low (L) thresholds in both TANK 1 and TANK 2,
ensuring that it remains within an optimal range. Furthermore,
there is an overflow threshold, denoted as HH, which represent
the upper maximum limit of the water level.

1 Available at https://github.com/scy-phy/minicps

B. Industrial Control Network Topology
We conducted the experiments in mesh and ring topologies,
each consisting of 6 nodes (Fig. 9). These network architectures
are widely used and readily available for industrial applications,
as evidenced by technical documentation and reports from various industrial equipment vendors [53], [54], [55].
A mesh topology (Fig. 9(a)) is a network design where each
device in the network is interconnected to every other device,
creating a redundant and highly fault-tolerant system. Within the
mesh network, each device serves as a node, and it communicates
directly with all other devices in the network. This redundancy
allows for data to flow through multiple paths, ensuring that even
if one link or device fails, communication can continue through
alternative routes. The mesh topology is suitable for applications such as process control, where real-time data exchange is
essential.
In contrast to the mesh topology, a ring topology (Fig. 9(b))
involves connecting devices in a circular arrangement, where
each device is connected to precisely two others, forming a
closed loop. One advantage of the ring topology is that it is
relatively simple to set up and manage compared to the mesh
topology, as there are fewer connections to configure. However,
it is less fault-tolerant; if one device or connection in the ring
fails, it can disrupt the entire network.
Furthermore, it is worth noting that in one of the experiments,
we extended the number of nodes beyond the default 6 to

5174

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 3, MAY/JUNE 2026

in the next section. In one of the experiments, we test different
weight values in the belief model and analyze the evolution under
different configurations.
C. FDI Attack Implementation
Following the threat model described in Section III, we designed the attack with the goal of degrading performance, misleading the control algorithm, and causing damage to physical
industrial equipment. The manipulated variable corresponds to
the sensor S_WL2, which measures the water level in TANK 2.
In this attack, we assume that the attacker gains access to a communication path between PLC1 and PLC3 and tampers S_WL2
sensor reading data requested by PLC1 to PLC3, changing the
water level value to 0.4 meters, below the optimal level defined
by the threshold L setting. In response, PLC1 opens actuator
A_P2, sending water from TANK 1 to TANK 2 and eventually
increasing the water level in TANK 2 until it reaches the overflow
threshold.
VI. EXPERIMENTAL RESULTS

Fig. 9. Industrial control network topologies used in the experimentation: A
mesh network topology (a) and a ring network topology (b).

introduce scalability and variation into the assessment. This
allowed us to observe how the implementation of DEFCLON
affects network performance, providing valuable insights into
its suitability for different industrial network sizes.
On top of these two network topologies, we implemented
DEFCLON on a single SDN controller powered by Ryu.2 To ensure
efficient data transmission throughout the network, we constructed the network topology using Open vSwitch3 switches.
The entire network, including the SDN controller, was deployed
on a single server powered by Ubuntu 22.04, which featured an
Intel Xeon E5-2630 processor and 32 GB of RAM.
We define the quantitative measures for the parameters of the
signaling game G for the path status decision-making as follows.
To simplify the analysis, we stabilize the attacker’s numerical
gain and loss, ga and ca , respectively, as a normalized value
of 1. We dynamically compute the remaining game parameters
(gf , gd , cd ) as described in Section IV-C3 each time the game is
played. Additionally, we set the weights in the belief model for
running the experiments to w1 = 0.9 and w2 = 0.1. With these
values, we achieve a good trade-off between past interactions
and current information sensitivity, as shown in our experiments

In this section, we first investigate the proactive path activation and adaptive path selection probabilities of DEFCLON
in Sections VI-A and VI-B. We then test DEFCLON on the
SWaT testbed in Section VI-C, and compare it to the closest
works in the literature to highlight its ability to mitigate FDI
attacks in industrial environments. In Section VI-D, we study
the behavior of the belief model with different configurations
and demonstrate the ability of the model to adapt to different
scenarios. Finally, in Section VI-E we examine the end-to-end
performance impact of DEFCLON in networks with different size.
A. Estimating Proactive Path Activation Probabilities
The proactive path activation aims to create uncertainty for attackers by preventing them from consistently accessing network
traffic and gathering information to construct effective attacks.
Considering the scenario where an attacker breaches a single
communication path, the probability of network traffic being
transmitted through the attacker’s path is calculated
com  using n!
,
binatorics. The binomial coefficient, denoted as nk = k!(n−k)!
represents the number of ways to choose k elements from a
set of n elements, regardless of their order. In DEFCLON, given
the availability of N paths to transmit data, the total number of
combinations without repetition Ct can be computed as
Ct (N ) =

N  

N
k=1

3 Available at https://www.openvswitch.org/

.

(12)

Next, we calculate the number of combinations for a single
path (Cp ) as
Cp (N ) =


N 

N −1
k=1

2 Available at https://github.com/faucetsdn/ryu

k

k−1

.

(13)

Assuming that all paths have the same probability, the probability associated with activating a particular path to transmit

ETXEZARRETA et al.: REPLICA-BASED MTD AGAINST INJECTION ATTACKS IN SOFTWARE-DEFINED INDUSTRIAL

5175

Fig. 10. Path activation (Ap ) and path selection (Sp ) probabilities under
different number of available paths.

data, denoted by Ap , is expressed by the following equation:
Ap (N ) =

Cp (N )
.
Ct (N )

(14)

Information-gathering is limited by DEFCLON: A random
subset of paths to transmit data are periodically triggered by
DEFCLON, creating intermittent data transfers. This dynamic
behavior thwarts attackers with access to these paths, limiting
their ability to collect information. As the number of available
paths grows towards infinity (N → ∞), the probability of a path
being activated to transmit data approaches 50% . Consequently,
there is a 50% chance on N → ∞ that a path will not transmit
network traffic at any given time. We illustrate this trend in
Fig. 10(a).
B. Estimating Adaptive Path Selection Probabilities
Given a pool of N available paths, all of which are in a forward
state, we can determine the probability of selecting a particular
path to forward data to the destination device using the following
calculation. Assuming an equal probability of selecting any
single path for this task, the selection probability (Sp ) can be
expressed as
N
Sp (N ) = Ap (N )

k=1

−1
(Nk−1
)

k

Cp (N )

=

1
.
N

(15)

DEFCLON introduces uncertainty in path selection: As the
number of available paths (N ) approaches infinity (N → ∞),
the probability of selecting a particular path to forward data to
the target device converges to 0% . Consequently, as the number
of paths increases, the probability of a path being selected to
forward traffic to the destination device decreases. This significantly reduces the probability of adversaries to perform FDI
attacks on a path selected to reach the destination device. This
trend is illustrated in Fig. 10(b).
C. Mitigating FDI Attacks in the SWaT Testbed
In Sections VI-A and VI-B, we demonstrated that the proactive components of DEFCLON inherently limit an attacker’s
opportunities, showing that an adversary faces significant uncertainty and a low probability of success by default. In this
section, we evaluate DEFCLON’s effectiveness under a worst-case
scenario. We simulate a scenario in which an adversary has

Fig. 11. Water level deviation under different network topologies and MTD
implementation strategies.

a presence on a network path and initiates an attack on the
path currently selected for data delivery to the end device.
This approach enables us to measure the effectiveness of the
signaling-game-based response in mitigating an ongoing attack.
For this, we executed the DEFCLON framework on the initial
stage of the SWaT testbed, as detailed in Section V-A. Fig. 11
illustrates the temporal evolution of two water tank levels,
namely TANK 1 and TANK 2, across three scenarios: (1) Water level deviation without the use of MTD or any defense
mechanism. (2) Water level deviation with the random traffic
replication MTD strategy proposed in [43] and [42]. (3) Water
level deviation with our proactive and adaptive traffic replication
MTD framework DEFCLON.
For each scenario, we conducted a total of 20 simulations,
using two different network topologies: mesh and ring, as discussed in Section V-B. We performed 10 simulations for each
topology type. The solid lines represent the mean water level
across the 10 trials for each configuration, while the shaded area
around each line in Fig. 11(c) indicates the standard deviation.
The small standard deviation observed across all trials indicates
a high degree of consistency and reproducibility of DEFCLON.
In each simulation run, we allowed an initial 2-minute window for the control logic to stabilize the process, ensuring a
water level of approximately 0.8 meters in both tanks. After

5176

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 3, MAY/JUNE 2026

TABLE V
COMPARISON OF DEFCLON WITH OTHER DATA REPLICATION STRATEGIES AGAINST FDI ATTACKS

this initialization period, a simulated adversary starts with the
FDI attack, following the procedure outlined in Section V-C.
The moment at which the testbed is actively attacked is indicated by a vertical dashed red line. During these experiments,
we assume the worst-case scenario where the attacker starts
the FDI attack in the path selected to reach the destination
end-device.
Examining Fig. 11(a), which illustrates the impact of the FDI
attack in the absence of any defense mechanism, we observe the
following sequence of events:
r At minute 2, when the attacker initiates the attack by tampering S_WL2 sensor reading packets requested to PLC3,
PLC1 responds by opening the A_P2 actuator. This action
results in the transfer of water from TANK 1 to TANK 2,
causing an increase in the water level in TANK 2 and a
corresponding decrease in TANK 1 water level.
r When the water level in TANK 2 reaches 1.2 meters, PLC3
opens A_P3 to prevent an overflow. As a result, the water
level stabilizes at 1.2 meters (threshold HH), as the rate at
which water leaves A_P3 and enters the tank matches.
r A similar phenomenon occurs in TANK 1. When PLC1
activates the A_P2 actuator to transfer water to TANK 2,
TANK 1 water level decreases until it reaches the threshold
value (L) of 0.5 meters.
r In response to this decrease, PLC1 opens the A_P1 actuator
in an attempt to stabilize the water level at 0.8 meters. The
reason TANK 1 water level stabilizes at 0.5 meters after
the attack is due to the fact that the rate of water flowing
from A_P2 matches the rate at which water enters from
A_P1.
DEFCLON outperforms random MTD strategies: The comparison presented in Fig. 11 demonstrates that DEFCLON significantly
outperforms both the MTD-IDR [42] and DMTDR [43] random
MTD strategies. In the case of the random traffic replication
MTD strategy shown in Fig. 11(b), when the attack initiates at
minute 2, the water level changes in the tanks remain identical
to the scenario without MTD. However, when the randomness
of this strategy replaces the path under attack, at minute 4 in
our simulations (indicated by a blue dashed vertical line), the
control logic attempts to stabilize both tank’s water levels at
0.8 meters. Conversely, when observing Fig. 11(c), it becomes
evident that DEFCLON’s adaptive path selection strategy, based on
the signaling game model G, is far more effective in mitigating
the attack compared to the random MTD strategy. Thanks to the
signaling game, the attacked path is rapidly replaced shortly after
the attack begins (indicated by a vertical blue dashed line). As
soon as the attacked path is replaced, PLC1 closes the actuator

A_P2 in the next cycle (indicated by a vertical green dashed line),
effectively limiting the deviation in water levels compared to the
random MTD strategy. Table V summarizes the main differences
between the random MTD strategies (MTD-IDR and DMTDR),
and our adaptive MTD proposal DEFCLON.
DEFCLON is topology-agnostic: The fact that DEFCLON performs well on different network topologies ascertains the validity of our claim about the applicability of our method to a
wide range of topologies. This versatility and adaptability of
DEFCLON in addressing FDI attacks on various ICS network
topologies is attributed to the inherent advantages provided by
SDN. SDN introduce an abstraction layer between the data
plane and the control plane, allowing for enhanced flexibility
and control in any network topology design. As shown in
Fig. 11, DEFCLON is able to respond to FDI attacks on different
ICS network topologies that had actual impact on the physical
process.
D. Experimenting With the Belief Model
The belief model plays a crucial role in the decision-making
process and equilibrium calculation within the signaling game G.
This study introduces a belief model composed of two factors,
each weighted by w1 and w2 respectively (3). By fine-tuning
these weights, we can observe diverse trajectories in the evolution of the belief values.
The belief model evolution is adaptable: To visualize different evolutions of the belief model, Fig. 12 represents three
scenarios with different weight values. In order to capture this
evolution, we conducted an attack in a path, spanning a duration
of 2 minutes. The weight w1 represents the model’s memory,
which gives precedence to the path’s historical behavior. A
higher value of w1 makes the system more conservative. It
will be slower to drop a historically reliable path based on a
single suspicious packet. On the other hand, the weight w2
represents how reactive the model is to immediate evidence.
A higher w2 value makes the system highly sensitive, causing
the belief value to spike rapidly when the first anomalous
packet is detected. While this allows for near-instantaneous
detection, it also increases the risk of misclassifying benign
packet corruption as a malicious attack. Therefore, the choice of
these parameters represents a trade-off between detection speed
and stability. For example, a configuration with w1 = 0.1 and
w2 = 0.9 is highly sensitive and suitable for environments where
even minor deviations are critical and network-induced errors
are rare. The configuration with w1 = 0.9 and w2 = 0.1 is more
cautious and is suitable for environments with potential network

ETXEZARRETA et al.: REPLICA-BASED MTD AGAINST INJECTION ATTACKS IN SOFTWARE-DEFINED INDUSTRIAL

5177

TABLE VI
ROUND TRIP TIME (RTT) OF NETWORK PACKETS UNDER NORMAL OPERATION WITHOUT MTD AND DEFCLON OPERATION

just as in a normal network operation without MTD, DEFCLON
does not introduce any delay or performance degradation in the
communications, regardless of the path length and the topology
type.
VII. LIMITATIONS AND DISCUSSION

Fig. 12.
values.

Belief value evolution in a path under attack with different weight

noise, where the system must be confident before dropping
a path.
E. Measuring Network Performance Degradation
To assess the impact of DEFCLON on network performance, we
conducted a comprehensive analysis of Round Trip Time (RTT),
involving the transmission of 400 ICMP traces along various
network paths, each with different distances or switch hops.
Our performance experiments encompassed both mesh and ring
topologies. Table VI presents RTT measurements, including
averages, minimums, maximums, and standard deviations. We
provide these measurements for scenarios both with and without
MTD, demonstrating how DEFCLON affects RTT across different
path lengths and network topologies compared to a normal
network operation.
DEFCLON does not degrade network performance: The comparison conducted in Table VI indicates that DEFCLON does not
cause any additional performance degradation in terms of endto-end latency compared to a normal network operation. The fact
that with DEFCLON network packets are matched, processed, and
forwarded directly by rules installed in the forwarding devices,

Controller scalability and computational load: A key consideration for DEFCLON is the computational load on the SDN
controller, which handles real-time path monitoring and gametheoretic calculations. The system is designed to limit this burden inherently. First, the signaling game’s calculations are computationally lightweight, involving simple arithmetic rather than
resource-intensive algorithms. Second, these calculations are
triggered only upon a packet’s arrival at the final node before the
destination, not at every hop in the network core, which significantly reduces the frequency of controller interactions. Despite
this efficiency, a single, centralized controller could still become
a performance bottleneck in large-scale or high-traffic industrial
settings. For such scenarios, established SDN patterns offer clear
scalability paths. A distributed controller architecture [56], [57]
can share the monitoring and calculation load across multiple
instances, enhancing performance and resilience. Additionally,
incorporating a stateful data plane [58] could offload computational tasks to the network devices themselves, further reducing
controller overhead.
Optimal path number selection: Refers to the challenge of
determining the ideal number of paths to use in a network.
The existing work assumes a fixed number of available paths
without considering the dynamic nature of network conditions
and requirements. This limitation can result in either underutilization of resources or insufficient redundancy. Determining the
optimal path number requires a comprehensive analysis of various factors such as network size, traffic load, desired resilience
level, and attack patterns. Future research in this area will focus
on developing adaptive algorithms that can dynamically adjust
path numbers to meet the evolving needs of modern industrial
networks.
Challenges of SDN adoption in ICS environments: While
SDN offers powerful capabilities for network management and
security, its integration into ICS environments is still in its
early stages and presents several key challenges [14]. One
significant issue is real-time performance and latency; the separation of the control and data planes in SDN can introduce
unacceptable delays for time-sensitive industrial processes that
require millisecond-level precision. Moreover, a standard SDN

5178

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 3, MAY/JUNE 2026

architecture with a single, centralized controller creates a single
point of failure, a critical risk in ICS, which demands high
availability and often necessitates a more complex, distributed,
and resilient architecture to ensure reliability. The challenge is
further compounded by the need to integrate SDN with legacy
industrial network equipment and proprietary protocols that are
not compatible with standard SDN protocols like OpenFlow,
posing a major technical and logistical hurdle. Lastly, the security of the control plane is a major concern, as the centralized
SDN controller becomes a high-value target for attackers, and
a successful breach could give an adversary complete control
over the network. Securing the controller and its communication
channels is therefore a top priority, adding another layer of
complexity to the overall system design.
Impact of network noise and measurement errors: A key
assumption in our signaling game formulation is the complete
and accurate observation of messages, specifically the packet
dissimilarity metric ψ(r, rn ) used to identify suspicious activity
in each path. However, real-world ICS networks are subject
to noise from factors like electromagnetic interference, congestion, or hardware malfunctions, which can cause benign
packet corruption. Such an event could cause the system to
misinterpret a legitimate path (δ = 0) as sending a suspicious
signal (m = 1). This would incorrectly increase the path’s belief value (θn (t)), potentially causing the defender to drop a
healthy communication channel and incur a cost (cd ) by reducing path diversity. Our framework mitigates this through its
dynamic belief model. The model’s sensitivity is managed by
weights assigned to historical behavior (w1 ) and current packet
dissimilarity (w2 ). By configuring a high weight for history
(e.g., w1 = 0.9, as used in our experiments), the defender’s
belief becomes more conservative and less reactive to isolated
instances of packet corruption. The selection of these weights
creates an operational trade-off between the speed of attack detection and the system’s stability against non-malicious network
noise.
VIII. CONCLUSION
We present a multi-layered MTD defense framework that
proactively and adaptively mitigates FDI attacks in the context
of SDN-based ICS. Leveraging SDN central management and
global view capabilities, we replicate the industrial traffic from
different network paths, and in the last exit node, we select only
a single path to be forwarded to the intended destination device.
To comprehensively depict the interactions between attacker and
defender, we propose a multi-stage signaling game to model the
attack-defense process and evaluate the payoffs of both players.
Furthermore, based on this game, we introduce an optimal path
status selection algorithm to include or exclude paths from the
selection pool for reaching the destination end-device. Our evaluation results reveal the effectiveness of the proposed framework
on multiple areas: (1) It reduces adversaries’ ability to intercept
network traffic by up to 50% . (2) It introduces uncertainty
on path selection, making difficult for adversaries to inject
malicious network packets into the industrial devices. (3) The
framework adaptively mitigates the impact of FDI attacks in
different network topologies by rapidly replacing paths under

attack, thereby preventing malicious traffic from reaching its
intended destination. (4) Our adaptable weighted belief model
proves its versatility in addressing diverse scenarios and specific
needs. (5) The framework operates without introducing any
additional performance degradation compared to a standard
network operation.

REFERENCES
[1] K. Stouffer, M. Pease, C. Tang, T. Zimmerman, V. Pillitteri, and S.
Lightman, “Guide to operational technology (OT) security,” NIST Special
Publication 800–82 Rev. 3, 2023.
[2] D. Bhamare, M. Zolanvari, A. Erbad, R. Jain, K. Khan, and N. Meskin,
“Cybersecurity for industrial control systems: A survey,” Comput. Secur., vol. 89, 2020, Art. no. 101677. [Online]. Available: https://www.
sciencedirect.com/science/article/pii/S0167404819302172
[3] M. Conti, D. Donadel, and F. Turrin, “A survey on industrial control system
testbeds and datasets for security research,” IEEE Commun. Surv. Tut.,
vol. 23, no. 4, pp. 2248–2294, Fourth Quarter 2021.
[4] A. Ameli, A. Hooshyar, A. H. Yazdavar, E. F. El-Saadany, and A. Youssef,
“Attack detection for load frequency control systems using stochastic
unknown input estimators,” IEEE Trans. Inf. Forensics Secur., vol. 13,
no. 10, pp. 2575–2590, Oct. 2018.
[5] A. Le, U. Roedig, and A. Rashid, “LASARUS: Lightweight attack surface
reduction for legacy industrial control systems,” in Proc. 9th Int. Symp.
Eng. Secure Softw. Syst., Cham, Springer International Publishing, 2017,
pp. 36–52.
[6] M. Nawrocki, T. C. Schmidt, and M. Wählisch, “Uncovering vulnerable
industrial control systems from the internet core,” in Proc. IEEE/IFIP
Netw. Operations Manage. Symp., 2020, pp. 1–9.
[7] G. Barbieri, M. Conti, N. O. Tippenhauer, and F. Turrin, “Assessing the
use of insecure ICS protocols via IXP network traffic analysis,” in Proc.
Int. Conf. Comput. Commun. Netw., 2021, pp. 1–9.
[8] B. Li, G. Xiao, R. Lu, R. Deng, and H. Bao, “On feasibility and limitations
of detecting false data injection attacks on power grid state estimation
using D-FACTS devices,” IEEE Trans. Ind. Informat., vol. 16, no. 2,
pp. 854–864, Feb. 2020.
[9] M. N. Kurt, Y. Yılmaz, and X. Wang, “Real-time detection of hybrid and
stealthy cyber-attacks in smart grid,” IEEE Trans. Inf. Forensics Secur.,
vol. 14, no. 2, pp. 498–513, Feb. 2019.
[10] D. Huang, X. Shi, and W.-A. Zhang, “False data injection attack detection
for industrial control systems based on both time- and frequency-domain
analysis of sensor data,” IEEE Internet Things J., vol. 8, no. 1, pp. 585–595,
Jan. 2021.
[11] B. Liu and H. Wu, “Optimal D-FACTS placement in moving target defense
against false data injection attacks,” IEEE Trans. Smart Grid, vol. 11, no. 5,
pp. 4345–4357, Sep. 2020.
[12] S. Sengupta, A. Chowdhary, A. Sabur, A. Alshamrani, D. Huang, and S.
Kambhampati, “A survey of moving target defenses for network security,”
IEEE Commun. Surv. Tut., vol. 22, no. 3, pp. 1909–1941, 3rd Quart., 2020.
[13] E. Haleplidis, K. Pentikousis, S. Denazis, J. H. Salim, D. Meyer, and
O. Koufopavlou, “Software-defined networking (SDN): Layers and architecture terminology,” RFC 7426, Jan. 2015. [Online]. Available: https:
//www.rfc-editor.org/info/rfc7426
[14] X. Etxezarreta, I. Garitano, M. Iturbe, and U. Zurutuza, “Softwaredefined networking approaches for intrusion response in industrial control systems: A survey,” Int. J. Crit. Infrastructure Protection, vol. 42,
2023, Art. no. 100615. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S1874548223000288
[15] S. Kim, Y. Eun, and K.-J. Park, “Stealthy sensor attack detection and realtime performance recovery for resilient CPS,” IEEE Trans. Ind. Informat.,
vol. 17, no. 11, pp. 7412–7422, Nov. 2021.
[16] T. Cai, T. Jia, S. Adepu, Y. Li, and Z. Yang, “ADAM: An adaptive DDoS
attack mitigation scheme in software-defined cyber-physical system,”
IEEE Trans. Ind. Informat., vol. 19, no. 6, pp. 7802–7813, Jun. 2023.
[17] M. Spence, “Job market signaling∗,” Quart. J. Econ., vol. 87, no. 3,
pp. 355–374, 1973, doi: 10.2307/1882010.
[18] J.-H. Cho et al., “Toward proactive, adaptive defense: A survey on moving
target defense,” IEEE Commun. Surv. Tut., vol. 22, no. 1, pp. 709–745, 1st
Quart. 2020.
[19] S.-Y. Chang, Y. Park, and B. B. Ashok Babu, “Fast IP hopping randomization to secure hop-by-hop access in SDN,” IEEE Trans. Netw. Service
Manag., vol. 16, no. 1, pp. 308–320, Mar. 2019.

ETXEZARRETA et al.: REPLICA-BASED MTD AGAINST INJECTION ATTACKS IN SOFTWARE-DEFINED INDUSTRIAL

[20] A. Chowdhary, A. Alshamrani, D. Huang, and H. Liang, “MTD
analysis and evaluation framework in software defined network (mason),” in Proc. ACM Int. Workshop Secur. Softw. Defined Netw.
Netw. Function Virtualization, New York, NY, USA, 2018, pp. 43–48,
doi: 10.1145/3180465.3180473.
[21] X. Xu, H. Hu, Y. Liu, J. Tan, H. Zhang, and H. Song, “Moving target
defense of routing randomization with deep reinforcement learning against
eavesdropping attack,” Digit. Commun. Netw., vol. 8, no. 3, pp. 373–387,
2022. [Online]. Available: https://www.sciencedirect.com/science/article/
pii/S2352864822000037
[22] Y. Wang, Q. Chen, J. Yi, and J. Guo, “U-TRI: Unlinkability through random
identifier for SDN network,” in Proc. Workshop Moving Target Defense,
New York, NY, USA, 2017, pp. 3–15, doi: 10.1145/3140549.3140554.
[23] X. Etxezarreta, I. Garitano, M. Iturbe, and U. Zurutuza, “Low delay
network attributes randomization to proactively mitigate reconnaissance
attacks in industrial control systems,” Wireless Netw., vol. 30, pp. 5077–
5091, Jan. 2023, doi: 10.1007/s11276-022-03212-5.
[24] H. Koo, Y. Chen, L. Lu, V. P. Kemerlis, and M. Polychronakis, “Compilerassisted code randomization,” in Proc. IEEE Symp. Secur. Privacy, 2018,
pp. 461–477.
[25] Y. Huang and A. K. Ghosh, Introducing Diversity and Uncertainty Create
Moving Attack Surfaces for Web Services. New York, NY: Springer, 2011,
pp. 131–151, doi: 10.1007/978-1-4614-0977-9_8.
[26] M. Taguinod, A. Doupé, Z. Zhao, and G.-J. Ahn, “Toward a moving
target defense for web applications,” in Proc. IEEE Int. Conf. Inf. Reuse
Integration, 2015, pp. 510–517.
[27] Y. Li, R. Dai, and J. Zhang, “Morphing communications of cyber-physical
systems towards moving-target defense,” in Proc. IEEE Int. Conf. Commun., 2014, pp. 592–598.
[28] H. Alavizadeh, D. S. Kim, and J. Jang-Jaccard, “Model-based evaluation of combinations of shuffle and diversity MTD techniques on
the cloud,” Future Gener. Comput. Syst., vol. 111, pp. 507–522,
2020. [Online]. Available: https://www.sciencedirect.com/science/article/
pii/S0167739X19315183
[29] H. Alavizadeh, S. Aref, D. S. Kim, and J. Jang-Jaccard, “Evaluating the
security and economic effects of moving target defense techniques on the
cloud,” IEEE Trans. Emerg. Topics Comput., vol. 10, no. 4, pp. 1772–1788,
Fourth Quarter 2022.
[30] J. Tan et al., “A survey: When moving target defense meets game theory,”
Comput. Sci. Rev., vol. 48, 2023, Art. no. 100544. [Online]. Available:
https://www.sciencedirect.com/science/article/pii/S1574013723000114
[31] A. Aydeger, M. H. Manshaei, M. A. Rahman, and K. Akkaya, “Strategic defense against stealthy link flooding attacks: A signaling game
approach,” IEEE Trans. Netw. Sci. Eng., vol. 8, no. 1, pp. 751–764,
First Quarter 2021.
[32] M. Priyadarsini, P. Bera, S. K. Das, and M. A. Rahman, “A security enforcement framework for SDN controller using game theoretic approach,”
IEEE Trans. Dependable Secure Comput., vol. 20, no. 2, pp. 1500–1515,
Mar./Apr. 2023.
[33] Y. Zhou, G. Cheng, and S. Yu, “An SDN-enabled proactive defense framework for DDoS mitigation in IoT networks,” IEEE Trans. Inf. Forensics
Secur., vol. 16, pp. 5366–5380, 2021.
[34] S. Lakshminarayana, E. V. Belmega, and H. V. Poor, “Moving-target
defense against cyber-physical attacks in power grids via game theory,”
IEEE Trans. Smart Grid, vol. 12, no. 6, pp. 5244–5257, Nov. 2021.
[35] J. Tian, R. Tan, X. Guan, and T. Liu, “Enhanced hidden moving target defense in smart grids,” IEEE Trans. Smart Grid, vol. 10, no. 2,
pp. 2208–2223, Mar. 2019.
[36] Z. Zhang, R. Deng, D. K. Y. Yau, P. Cheng, and J. Chen, “Analysis of
moving target defense against false data injection attacks on power grid,”
IEEE Trans. Inf. Forensics Secur., vol. 15, pp. 2320–2335, 2020.
[37] Y. Chen, S. Lakshminarayana, and H. Vincent Poor, “Moving target
defense against adversarial false data injection attacks in power grids,”
IEEE Internet Things J., vol. 12, no. 14, pp. 26315–26327, Jul. 2025.
[38] Z. Zhang, R. Deng, D. K. Y. Yau, P. Cheng, and M.-Y. Chow, “Security
enhancement of power system state estimation with an effective and lowcost moving target defense,” IEEE Trans. Syst., Man, Cybern. Syst., vol. 53,
no. 5, pp. 3066–3081, May2023.
[39] Q. Wang et al., “Topology switching-based moving target defense against
false data injection attacks on a power system,” Int. J. Elect. Power Energy
Syst., vol. 163, 2024, Art. no. 110350. [Online]. Available: https://www.
sciencedirect.com/science/article/pii/S0142061524005738
[40] A. Kanellopoulos and K. G. Vamvoudakis, “A moving target defense control framework for cyber-physical systems,” IEEE Trans. Autom. Control,
vol. 65, no. 3, pp. 1029–1043, Mar. 2020.

5179

[41] J. Tian, R. Tan, X. Guan, Z. Xu, and T. Liu, “Moving target defense
approach to detecting stuxnet-like attacks,” IEEE Trans. Smart Grid,
vol. 11, no. 1, pp. 291–300, 2020.
[42] J. A. Giraldo, M. El Hariri, and M. Parvania, “Moving target defense for
cyber–physical systems using IoT-enabled data replication,” IEEE Internet
Things J., vol. 9, no. 15, pp. 13223–13232, Aug. 2022.
[43] J. Giraldo, M. E. Hariri, and M. Parvania, “Decentralized moving target
defense for microgrid protection against false-data injection attacks,” IEEE
Trans. Smart Grid, vol. 13, no. 5, pp. 3700–3710, Sep. 2022.
[44] F. Mvah, V. K. Tchendji, C. T. Djamegni, A. H. Anwar, D. K. Tosh,
and C. Kamhoua, “Countering ARP spoofing attacks in software-defined
networks using a game-theoretic approach,” Comput. Secur., vol. 139,
2024, Art. no. 103696. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S0167404823006065
[45] S. Deng, W. Dai, X. Qing, and X. Gao, “Vulnerabilities in SDN topology discovery mechanism: Novel attacks and countermeasures,” IEEE
Trans. Dependable Secure Comput., vol. 21, no. 4, pp. 2541–2551,
Jul./Aug. 2024.
[46] M. Krotofil, J. Larsen, and D. Gollmann, “The process matters: Ensuring
data veracity in cyber-physical systems,” in Proc. 10th ACM Symp. Inf.,
Comput. Commun. Secur., New York, NY, USA, 2015, pp. 133–144,
doi: 10.1145/2714576.2714599.
[47] W. Aoudi, M. Iturbe, and M. Almgren, “Truth will out: Departure-based
process-level detection of stealthy attacks on control systems,” in Proc.
ACM SIGSAC Conf. Comput. Commun. Secur., New York, NY, USA, 2018,
pp. 817–831, doi: 10.1145/3243734.3243781.
[48] O. N. Foundation, Openflow switch specification, version 1.5.1,
(2015). [Online]. Available: https://opennetworking.org/wp-content/
uploads/2014/10/openflow-switch-v1.5.1.pdf
[49] J. McCarthy et al., “Securing manufacturing industrial control systems:
Behavioral anomaly detection,” US Department of Commerce, National
Institute of Standards and Technology, 2020.
[50] D. Fudenberg and J. Tirole, Game Theory. Cambridge, MA, USA: MIT
Press, 1991.
[51] D. Antonioli and N. O. Tippenhauer, “MiniCPS: A toolkit for security research on CPS networks,” in Proc. 1st ACM Workshop CyberPhys. Syst.-Secur. PrivaCy. New York, NY, USA, 2015, pp. 91–100,
doi: 10.1145/2808705.2808715.
[52] A. P. Mathur and N. O. Tippenhauer, “SWaT: A water treatment testbed
for research and training on ICS security,” in Proc. Int. Workshop CyberPhys. Syst. Smart Water Netw., 2016, pp. 31–36.
[53] Siemens, “Setting up a mesh network based on RSTP,” Siemens, Tech.
Rep. SCALANCE X., 2016.
[54] Siemens, “Setup of a ring topology based on MRPD,” Siemens, Tech. Rep.
SIMATIC S7-1500 / ET 200SP, 2017.
[55] I. Cisco Systems, “High-availability seamless redundancy in the factory
network,” Cisco Systems, Inc., Tech. Rep., 2018.
[56] Y. E. Oktian, S. Lee, H. Lee, and J. Lam, “Distributed SDN controller
system: A survey on design choice,” Comput. Netw., vol. 121, pp. 100–111,
2017. [Online]. Available: https://www.sciencedirect.com/science/article/
pii/S1389128617301706
[57] F. Bannour, S. Souihi, and A. Mellouk, “Distributed SDN control: Survey,
taxonomy, and challenges,” IEEE Commun. Surv. Tut., vol. 20, no. 1,
pp. 333–354, 1st Quart., 2018.
[58] X. Zhang, L. Cui, K. Wei, F. P. Tso, Y. Ji, and W. Jia, “A survey on
stateful data plane in software defined networks,” Comput. Netw., vol. 184,
2021, Art. no. 107597. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S1389128620312305

Xabier Etxezarreta received the PhD degree, in
2024 with a thesis on software-defined networking
approaches for intrusion response in industrial control systems. He is a researcher/lecturer and member
with the Data Analysis and Cybersecurity research
group, Mondragon Unibertsitatea. His research interests include securing critical infrastructure, specifically through networking security and the development of automated intrusion response strategies.

5180

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 23, NO. 3, MAY/JUNE 2026

Federico Turrin received the PhD degree in brain,
mind, and computer science from the University of
Padua, in 2023, under the supervision of Prof. Mauro
Conti. In 2023 he was a post doc researcher with
the SPRITZ research group, University of Padua.
Currently he serves as a cybersecurity engineer with
SpritzMatter srl. His research interests include security of cyber-physical systems, specifically industrial
control systems and vehicular systems, as well as
the development of anomaly and intrusion detection.
In 2022, he was a visiting researcher with SUTD in
Singapore, under the guidance of Prof. Jianying Zhou and Prof. Tien Tuan Anh
Dinh.

Iñaki Garitano received the MSc degree in telecommunication engineering and the PhD degree in behavioral modeling for anomaly detection in industrial
control systems. He is a researcher/lecturer with the
Intelligent Systems for Industrial Systems research
group, and member with the Data Analysis and Cybersecurity research area of Mondragon Unibertsitatea. Before joining Mondragon Unibertsitatea in
2015, he worked with Universitetssenteret på Kjeller
(UNIK) as postdoctoral researcher. In addition, he is
the CTO of the Basic Internet Foundation. His main
research interests include in the area of Cybersecurity applied to industrial
automation and control systems and information and communication networks
including Internet of Things, and application container technologies. He currently participates in several European, national and regional level public funding
projects.

Mikel Iturbe received the MSc degree in ICT security
from the Open University of Catalonia, Barcelona,
Spain, in 2013, and the PhD degree from Mondragon
Unibertsitatea, Arrasate-Mondragón, Spain, in 2017,
where he worked on data-driven intrusion detection in
industrial networks. He is a lecturer and a researcher
with Mondragon Unibertsitatea. He is currently part
of the Data Analysis and Cybersecurity Research
Group. His main research interest is related to cybersecurity, primarily in the industrial sector. The
main lines he works on are industrial control system
security, embedded security, and software security. He also works in exploring
novel data-driven applications for cybersecurity.

Urko Zurutuza received the PhD degree from Mondragon Unibertsitatea, in 2008, in collaboration with
the Zürich IBM Research Lab. He is the principal
investigator with the Intelligent Systems for Industrial Systems research group, and coordinator with
the Data Analysis and Cybersecurity research team.
His research interests revolve around applications
of machine learning to real world problems, and
specially network security. He has published more
than 25 articles in high impact journals, more than
44 publications in blind peer-reviewed conferences,
edited 3 books (2 of them as conference proceedings), and coauthored 9 book
chapters. He serves as Program Committee member in conferences such as
RAID, DIMVA or SECRYPT, and as Steering Committee member in RAID and
DIMVA.

Mauro Conti (Fellow, IEEE) received the PhD degree from the Sapienza University of Rome, Italy,
in 2009. He is a full professor with the University
of Padua, Italy. He is also a Wallenber-WASP guest
professor Örebro University. After his PhD, he was
a post-doc researcher with Vrije Universiteit Amsterdam, The Netherlands. In 2011 he joined as assistant [rofessor with the University of Padua, where
he became a associate professor in 2015, and a full
professor in 2018. He has been visiting researcher
with GMU, UCLA, UCI, TU Darmstadt, UF, and
FIU. He has been awarded with a Marie Curie Fellowship (2012) by the
European Commission, and with a Fellowship by the German DAAD (2013).
His research is also funded by companies, including Cisco, Intel, and Huawei.
His main research interest is in the area of security and privacy. In this area, he
published more than 550 papers in topmost international peer-reviewed journals
and conferences. He is a editor-in-chief for IEEE Transactions on Information
Forensics and Security, area editor-in-chief for IEEE Communications Surveys
& Tutorials, and has been associate editor for several journals, including IEEE
Communications Surveys & Tutorials, IEEE Transactions on Dependable and
Secure Computing, IEEE Transactions on Information Forensics and Security,
and IEEE Transactions on Network and Service Management. He was program
chair for TRUST 2015, ICISS 2016, WiSec 2017, ACNS 2020, CANS 2021,
CSS 2021, WiMob 2023 and ESORICS 2023, and general chair for SecureComm
2012, SACMAT 2013, NSS 2021 and ACNS 2022. He is fellow of the AAIA,
distinguished member of the ACM, and fellow of the Young Academy of Europe.
PAPER_TEXT
