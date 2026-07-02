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
# [636] Cyber Resilience in Solar-Rich Networked Microgrids: A Real Time End-to-End DER Outage Management Framework
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
编号：636
题名：Cyber Resilience in Solar-Rich Networked Microgrids: A Real Time End-to-End DER Outage Management Framework
年份：2025
DOI：10.1109/tia.2025.3625887
来源：IEEE Transactions on Industry Applications
PDF：paper/10.1109_TIA.2025.3625887.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：无
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\636.txt
- 原始字符数：67270
- 本次发送字符数：67270
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INDUSTRY APPLICATIONS, VOL. 62, NO. 2, MARCH/APRIL 2026

3433

Cyber Resilience in Solar-Rich Networked
Microgrids: A Real Time End-to-End
DER Outage Management Framework
Jannatul Adan , Graduate Student Member, IEEE, Md Fazley Rafy , Member, IEEE,
and Anurag K. Srivastava , Fellow, IEEE

Abstract—The increasing integration of distributed energy resources (DERs), especially solar PV with distribution automation and inherent cyber-vulnerabilities, introduces new challenges
in outage detection, diagnosis, and recovery due to integrated
cyber-physical dependency. Traditional outage management systems (OMS) focus primarily on load-side faults and overlook
DER-specific outages, particularly those caused by cyber-induced
anomalies in the data or control planes. This work proposes a
cyber-resilient DER Outage Management System (DEROMS) tailored for solar-rich, networked microgrids, considering the increasing integration of solar generation within distribution systems
among DERs. The developed framework includes a TraceAlignDPI module for real-time data integrity checking and hidden outage
detection, a TraceAlign-RCA engine for multi-source root cause
inference, and scenario-specific restoration optimization leveraging networked microgrid flexibility. A testbed built in Real-Time
Digital Simulator (RTDS) validates the developed framework for
physical faults and cyberattack scenarios. Results show improved
accuracy in outage classification and enhanced system resilience
through adaptive restoration under uncertainty.
Index Terms—Cyber resilience, networked microgrids, outage
management, real-time testbed, synchrophasor data.

I. INTRODUCTION
A. Background and Motivation
HE distribution system is rapidly evolving with the rise
of microgrids and renewable-based DERs. Once niche,
microgrids are now a key resilience strategy for utilities like
PG&E, SDG&E, and ComEd, offering islanding and local control capabilities [1]. The solar PV microgrid market alone is
expected to top USD 25 billion by 2034, driven by electrification
and decarbonization goals [2]. The U.S. DOE has recognized

T

Received 2 July 2025; revised 2 October 2025; accepted 7 October 2025. Date
of publication 24 October 2025; date of current version 10 February 2026. Paper
2025-CRNM-0717.R1, approved for publication in the IEEE TRANSACTIONS
ON INDUSTRY APPLICATIONS by the Cybersecurity and resilience of networked
microgrids of the IEEE Industry Applications Society. This work was supported
in part by the US Department of Energy and in part by Appalachian Regional
Commission (ARC) ARISE Grants. (Corresponding author: Jannatul Adan.)
The authors are with the Lane Department of Computer Science and Electrical
Engineering, West Virginia University (WVU), Morgantown, WV 26506 USA
(e-mail: ja00060@mix.wvu.edu; anurag.srivastava@mail.wvu.edu).
Color versions of one or more figures in this article are available at
https://doi.org/10.1109/TIA.2025.3625887.
Digital Object Identifier 10.1109/TIA.2025.3625887

microgrids as vital for enhancing reliability, efficiency, and
emissions reduction, targeting 98% outage reduction and 20%
efficiency gains over conventional systems [3]. Meanwhile,
utility-scale microgrids are projected to exceed USD 50 billion
[4].
At the same time, utility-scale solar PV has become the
leading source for new capacity additions in the U.S., adding
20.2 GW in 2022 alone, surpassing investments in other DERs
such as wind and battery storage [5]. Falling costs and supportive
policies are pushing distributed and grid-scale solar deeper into
the distribution system [6], [7], [8], [9], [10]. A critical enabler
of these trends is the proliferation of smart inverters embedded
in solar PV and battery storage systems. They allow DERs to
deliver voltage regulation, frequency support, and ride-through
capabilities, turning them into active grid assets. These features
enable Non-Wires Alternatives (NWA), helping defer costly
grid upgrades while improving flexibility [11], [12], [13], [14],
[15], [16]. Moreover, these renewable resources can provide
critical self healing capabilities through potential formation of
networked microgrids (NMG) and coordinated energy management [17].
As DER penetration grows, ensuring their secure and resilient
operation becomes critical for grid stability, which has led to
significant improvements in visibility and observability, driven
by widespread sensor deployment and advances in communication protocols [18], [19], [20]. Real-time data streams from
smart inverters, PMUs, advanced meters, and grid-edge monitoring devices now enable utilities to better monitor and control
DER operations [21]. However, the very features that enhance
DER operation - namely, remote monitoring and remote controllability simultaneously expand the cyber failures, including
expansion of the cyberattack surface, exposing DER assets to
a range of potential cyber-physical manipulations and failures
[22], [23]. Traditionally, Outage Management Systems (OMS)
under Advanced Distribution Management Systems (ADMS)
were designed primarily to address load outages, as distribution
systems historically operated as passive networks where load
was the critical component. Yet, with the increasing integration of DERs, particularly utility-scale DERs, these resources
have become equally critical. Unmonitored or unplanned DER
outages can now trigger cascading failures, resulting in severe operational disruptions and significant economic losses

0093-9994 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

3434

IEEE TRANSACTIONS ON INDUSTRY APPLICATIONS, VOL. 62, NO. 2, MARCH/APRIL 2026

[24]. The DER Outage Management System (DEROMS) can
therefore be integrated within a Microgrid Management System
(MGMS), which usually has full observability of internal DERs,
or DER management system (DERMS) or ADMS. Reports and
industry analyses consistently stress that while DERMS, MGMS
or ADMS are maturing, DEROMS must also evolve to address
these emerging cyber-physical risks [24], [25].
In existing literature, few works related to DER outages have
primarily focused on detecting and managing outages originating from physical faults. There is a pressing need to transition
toward cyber-informed DEROMS capable of real-time monitoring, outage detection, and outage classification that spans
both physical and cyber domains. Such a system must not only
identify and diagnose the root cause of an outage to be operational or cyber-induced, but also tailor appropriate, scenariospecific response strategies specially utilizing the potential of
networked microgrids. Motivated by this gap, the current work
proposes a real-time end-to-end outage management framework
designed to leverage multi-domain DER data streams, detect
and diagnose both physical and cyber induced outage scenarios,
identify the root cause of disruptions, and enable adaptive,
cyber-resilient response measures incorporating flexibilities of
networked microgrids suited for real-time or near real-time
application.
B. Literature Review and Research Gap
While traditional outage detection methods rely heavily on
trustworthy measurements and sensor data, it is critical to first
address data plane inconsistencies. Several existing approaches
effectively implemented real-time integrity checks by identifying deviations from expected “normal” behavior during system
operation based on PMU measurements, fault alarms, SCADA,
and/or breaker status [26], [27]. However, a common vulnerability in these methods is the implicit assumption that the reported
as well as historical data used for model training is inherently
uncompromised. These event detection tools may provide false
positives if the reported data is falsified and there is a lack of a
distinct, preliminary validation stage to trust this baseline data
before it is used to build or run the detection algorithms, which
leaves the models susceptible to being trained on corrupted data.
Furthermore, even methods that monitor high-level network
parameters, such as aggregate power flow patterns, to detect
database anomalies [28] often lack the granularity to address
device-specific events. A data-driven cyber physical detection
model uses PMU coherence features and a stack of Deep belief
networks to flag corrupted measurements in real time [29],
an isolation forest approach applies PCA for dimensionality
reduction, followed by an unsupervised forest model to isolate
anomalous patterns [30], and an OPF-forecast deviation method
continuously compares live OPF outputs against a statistical
forecast of expected power flow patterns to detect database tampering [28]. However, none of these works perform a separate,
standalone assessment of its historical “natural” (attack-free)
dataset before model training. The sanity check occurs only
as part of the anomaly-detection or forecasting process itself.
Furthermore, a key challenge remains unaddressed: the inability
to confirm the genuine operational status of individual DERs

as a whole. To overcome this, we need an integrated detection
framework that combines broad network analysis with granular,
device-level sensor measurements.
For outage root cause analysis, solar-rich systems present
unique challenges because these resources are both generation
assets and cyber-physical systems. Most existing work on solar
DER outage root cause inference focuses on PV fault detection
and classification [31], [32], [33], [34], [35], [36], [37]. Authors
in [38] review islanding detection techniques, whereas [39]
proposes a sensor failure detection mechanism. These studies,
although valuable for identifying PV system and inverter faults,
only comprise a subset of outage types and often exclude the
systematic diagnosis of cyber-physical vulnerabilities under
complex protection schemes [40], [41], [42]. Authors found two
works [43], [44] that account for cyber-induced scenarios behind
outage, but implement the strategy primarily on load outages.
Though the work in [45] advances large scale cyber network
simulation and detects critical cyber nodes, it has limited applicability towards cyber-aware restoration strategies or DER
outage from a power system perspective.
Again, in evolving outage mitigation strategies, networked
microgrids are becoming popular due to their resilient service
restoration post-disturbance [46], [47]. These works optimize
load recovery and network reconfiguration but largely ignore
cyber-physical threats. For instance, they assume reliable DER
operation and neglect compromised assets or data integrity loss
during the restoration planning process.
To summarize, there is a lack of holistic, system-wide perspective that integrates different operational layers and a complete
end-to-end DER outage management framework. Most data
falsification detection techniques are not tailored for DER outage
scenarios. Few works offer integrated cyber-aware outage RCA,
and almost none integrate this insight into restoration decisionmaking in the presence of DERs, creating a dire need for a
comprehensive framework that can enforce true system-wide
coherence by aligning data traces from both cyber-physical
domains. The key gaps are as follows,
r Lack of a comprehensive related work on possible outage
scenarios in emerging cyber-physical systems from DER
perspective.
r Outage management remains limited primarily focusing
on physical faults rather than root-cause resilience across
data/ control failure modes.
r Lack of system-wide, cross-domain trace alignment, limiting the detection of sophisticated masked or unobserved
DER outages.
r No end-to-end framework that integrates detection, RCA,
and restoration under both physical and cyber disruption
scenarios for solar-rich DER systems.
r Restoration strategies in networked microgrids seldom incorporate cyber-awareness, leading to sub-optimal restoration or risk amplification.
C. Contributions
This work proposes a real-time DER outage management
framework for solar-rich networked microgrids that is both
cyber-aware and restoration-oriented. While many recent works

ADAN et al.: CYBER RESILIENCE IN SOLAR-RICH NETWORKED MICROGRIDS: A REAL TIME END-TO-END DER OUTAGE

apply ML methods to largely target individual functions, our
proposed DEROMS emphasizes the interaction and hierarchy of
detection, RCA, and restoration modules, with ML techniques
embedded as support tools in a coordinated manner. The contributions are summarized as,
1) Analyzed DER outage scenarios considering cyber failure
in data and control planes.
2) Proposed an end-to-end DER outage management framework, identifying vital tools, defining their specific functions and proposing precise hierarchy on how these tools
will be triggered and coordinated.
3) Proposed TraceAlign-DPI, a DEROMS framework that
ensures data plane integrity by aligning cross-domain
traces while using forecast-aware estimation to compensate for DER visibility loss.
4) Proposed TraceAlign-RCA, a DEROMS framework to
align cross-domain pre-outage traces to distinguish fault
induced vs. cyber-induced outages.
5) Discussed restoration strategies informed with improved
situational awareness on DERs based on previous outage
detection and RCA layers.
6) Developed real-time testbed of networked microgrid with
power electronics and protection interfaces as well as realtime data acquisition and monitoring.
7) Developed two case studies to demonstrate the workflow
of the DEROMS on a cyber-compromised vs. normal
scenario.
The proposed end-to-end DEROMS framework is classified
into three functional layers namely - Outage Detection Layer,
Outage Root Cause Analysis Layer and Outage Response and
Recovery Layer. The detailed description of each of these layers
is discussed in the following three sections with the complete
architecture in Fig. 1.
II. OUTAGE DETECTION LAYER
A. Understanding Outage Scenarios Considering Cyber
Failure in Data Plane
In an ideal scenario, reliable and synchronized streaming data
from DER-end monitoring devices, such as PMUs, SCADA
gateways, smart meters, breaker status, would allow precise
real-time detection of the DER status. Throughout this work, the
term DER status refers to either connected and supplying power
or offline/facing outage. However, real-world cyber-physical
systems are prone to cyber failures that degrade or distort
system observability. These failures, located in the data plane,
can arise from multiple sources such as sensor malfunctions or
calibration drift, communication errors, including dropped or
corrupted packets, complete or partial loss of data transmission
or attack-induced falsification of measurement data streams. In
such conditions, the outage detection layer must account for a
range of possible visibility scenarios that may occur during DER
monitoring:
1) Visible True Outage: A physical outage occurs at the DER,
and the event is correctly reflected in the incoming data
streams. This is the ideal case where outage detection
operates as expected.

3435

2) Falsely Reported Outage: A DER remains operational,
but due to data plane failures (such as erroneous measurements, corrupted packets, or falsified data injection), an
artificial loss of power is reported in the monitoring data,
incorrectly indicating that a DER outage has occurred.
3) Masked Outage: A DER experiences a physical outage,
but the event is not reported or captured in the data
stream due to complete sensor inaccuracies, delayed measurements, or data masking attacks that suppress outage
signatures.
4) Unobserved Outage due to Loss of Data / Visibility: The
monitoring system loses all or most communication with
the DER, resulting in total visibility loss. The DEROMS
cannot ascertain the DER’s current operational status under this condition.
Traditional DERMS and MGMS architectures primarily rely
on observing direct data indicators to declare an outage, which
limits their reliability in non-ideal monitoring conditions. In
contrast, a cyber-resilient DER Outage Management System
(DEROMS) must be designed to distinguish true physical outages from data plane anomalies, detect inconsistencies across
multiple data sources, and operate under degraded or adversarial
observability conditions.
B. Proposed Cyber-Resilient Outage Detection &
Classification Architecture With TraceAlign-DPI
The outage detection mechanism in the proposed framework
incorporates both conventional outage indicators and advanced
data plane integrity verification to improve resilience against
cyber-physical inconsistencies. The central module within the
detection layer is the proposed TraceAlign-DPI (Cross Domain Outage Trace Alignment for Data Plane Integrity)
tool, which operates both as a reactive and proactive data integrity evaluator across the operational states of the DER. Three
other tools are incorporated in the framework named Solar
Forecasting tool, Forecast-Aware Data Estimation tool, and
Cyber Anomaly Detection tool. Hence a brief description of
the purpose of these tools as well as how they interact with
TraceAlign-DPI to enhance the DEROMS framework is added
in this section.
1) Functional Objective of TraceAlign-DPI: TraceAlignDPI is a lightweight, event-triggered or periodic data plane
integrity checking module embedded inside MGMS, designed to
cross-validate DER observability data streams with system level
dynamics to ensure sensor-level data is consistent and coherent
with the system before outage RCA or response actions are
taken. TraceAlign-DPI aims to verify whether the operational
status reported by a DER (either as connected and supplying
power or as tripped/ offline) is consistent with the dynamic
behavior of the surrounding system as observed via system-wide
monitoring. The module utilizes the physics of power system
balance: any real DER outage will alter the load-generation
equilibrium, thus inducing measurable changes in network-wide
variables commonly manifesting through shifts/ anomalies in
SCADA-measured PQ flows across feeders, loads, and neighboring DERs or in frequency, ROCOF and voltage profile from

3436

Fig. 1.

IEEE TRANSACTIONS ON INDUSTRY APPLICATIONS, VOL. 62, NO. 2, MARCH/APRIL 2026

Proposed architecture of end-to-end deroms framework.

ADAN et al.: CYBER RESILIENCE IN SOLAR-RICH NETWORKED MICROGRIDS: A REAL TIME END-TO-END DER OUTAGE

PMU measurements. Three thresholds are defined in this case:
Tp , primary anomaly threshold - above which a system anomaly/
shift indicates possible outage and raises a positive outcome
of the tool, Tls , secondary lower threshold - below which
system shift is considered too low to have incurred a DER outage
and Tus , secondary upper threshold - above which means
very strong post-outage effect detected. Tus and Tls are needed
when data-DPI contradicts. By aligning the reported DER status
against system-wide dynamic signatures, TraceAlign-DPI establishes whether the DER-side data is trustworthy or possible data
plane corruption exists.
2) Operational
Deployment
of
TraceAlign-DPI:
TraceAlign-DPI operates in the following modes within
DEROMS:
a) Invocation Driven by DER Power Loss Detection
(Reactive Mode 1): Upon detection of a DER power loss via
streaming power system (PS) measurements, it is first checked
whether the power loss is expected due to weather conditions
(i.e. low irradiance region) by utilizing a solar forecasting tool.
The Solar Forecasting tool utilizes site specific or area based
meteorological data to nowcast a range of tentative solar generation. The tool leverages varying irradiance profiles to account
for natural solar intermittency, ensuring that power loss from low
irradiance is not misclassified as an outage. Also, to account for
second-level variability, a tolerance band around the forecasted
value should be considered where measured PV power within
this band is attributed to irradiance changes rather than outages.
If the generation forecast is not in the low generation region
but power loss was reported, TraceAlign-DPI is triggered after
a wait time twait to validate the authenticity of the detected
outage event. An explanation of twait is added at the end of this
subsection. The consistency check proceeds as follows:
r If the reported DER power loss is corroborated by systemwide shifts consistent with load-generation rebalancing,
then true DER outage is predicted.
r If inconsistency is observed, that is, the DER reports power
loss while the system shows no expected system wide
response - this suggests possible data plane corruption or
falsely reported outage (e.g., falsified zero-power reading,
data masking). The proposed framework tries to detect a
system shift with a lowered secondary anomaly threshold
as well as evaluating the trustworthiness of the incoming
packets through a cyber anomaly detection tool to confirm the actual DER status. If outage is predicted through
the combined output of these tools, relay/ inverter log is
invoked for the root cause of outage. This adds an additional
confidence on DER outage detection and if data is found
to be unreliable and inaccurate, DER side data is replaced
by forecast aware estimated data for continued analysis.
b) Invocation Triggered by Cyber-Layer Anomaly Detection (Reactive Mode 2): TraceAlign-DPI is also triggered
though a cyber anomaly detection tool upon the detection of
cyber anomalies observed in the metadata or protocol layers of
incoming streaming packets from dPMU and SCADA sources
even if the PS data shows no power loss from the DER end. These
packets traverse multiple network layers including Ethernet, IP,
transport protocols (TCP/UDP), and application-layer protocols

3437

such as IEEE C37.118, DNP3, or Modbus. While their payloads
contain physical system measurements, the surrounding protocol headers embed cyber-relevant metadata such as:
r IP/MAC address mismatches compared to expected
r Unexpected function codes or command flags
r Missing or altered CRC values
r Irregular sequence numbers or timestamp fields
r Abnormal response delays or jitter patterns
These diagnostics distinguish between: Non-critical anomalies (e.g., jitter, retransmission) which do not question payload
trustworthiness, and Critical anomalies which directly question
the credibility of DER measurements. Malicious events may
leave metadata traces (e.g., abnormal source/ destination IP/
port, sequence number gaps, replayed timestamps, checksum
errors) that the cyber anomaly tool can flag as critical anomalies.
In contrast, communication loss or sensor failures which are
also critical cyber anomalies may have metadata features (e.g.,
missing sequence counters, link-layer flags, quality indicators
in PMU streams) which indicate degraded data integrity. Perhaps, considering practical limitations and exclusivity of the
cyber configuration, these anomalies may not always manifest
as explicit metadata violations or be clearly distinguishable as
critical vs. non-critical. Therefore, our framework uses metadata anomalies to provide early suspicion of integrity threats,
but final classification integrates both metadata diagnostics and
system-level Data and DPI findings.
Thus, upon observing critical cyber-layer inconsistencies, the
DEROMS invokes TraceAlign-DPI to validate the power system
measurements themselves. When the payload containing the
PS measurements shows DER power supply, a consistent DER
status indicates coherent system-wide dynamics even though
cyber anomaly exists. An inconsistency by TraceAlign-DPI
would mean that, the system reflects a possible DER outage
though the DER end data shows power supply- masking an
outage, further reinforcing the suspicion that the data stream
is corrupted.
c) Periodic Invocation (Proactive Mode): Independently
of event triggers, TraceAlign-DPI is periodically called as a
continuous data integrity monitor. In this mode:
r The system predicts expected DER output based on realtime network-wide measurements and compares it with
reported DER status.
r If the DER reports being active, but system-wide data
suggests power imbalance consistent with an outage,
TraceAlign-DPI flags a masked/hidden DER outage when a
very strong system wide shift is observed (system anomaly
score (AS)> Tus , secondary upper threshold). Again,
checking with cyber traces and invoking relay and inverter
logs can confirm or discard the finding of TraceAlign-DPI.
This mechanism enables detection of silent outages where no
direct trip signal is reported due to data falsification.
d) Invocation Under Data Loss Conditions (Visibility Loss
Compensation): As per previous discussion, upon investigation
through TraceAlign-DPI, cyber anomaly tool and further relay/inverter log, when DEROMS confirms that data does not reflect the system (i.e. data is falsified or lost), it flags the scenarios
as data visibility loss. In these cases, DEROMS substitutes the

3438

IEEE TRANSACTIONS ON INDUSTRY APPLICATIONS, VOL. 62, NO. 2, MARCH/APRIL 2026

missing data with forecast-based synthetic estimation through
Forecast-aware data estimation tool. This tool assumes the
DER continues to operate at its last-known status on forecasted
capacity. Before the visibility returns, estimation followed by
TraceAlign-DPI is periodically invoked to keep verifying:
r Whether the system-wide measurements remain consistent
with the synthetic estimate.
r Whether an abrupt deviation suggests the DER has actually tripped while remaining unobservable to predict an
unobserved outage.
Through these multiple operational pathways, TraceAlignDPI addresses all major categories of data plane failures in case
of DER outages which is illustrated in detail in Table I. Additionally, if relay and inverter log confirms validity of reported data
from DER end after an inconsistency was flagged by TraceAlignDPI, then it indicates false predictions of TraceAlign-DPI. This
observed label is then given as a feedback to the learning module
of TraceAlign-DPI to improve its accuracy. While the cyber
anomaly tool is responsible for distinguishing attack-induced vs.
benign data loss, TraceAlign-DPI and RCA ensure system-level
consistency checks and diagnosis by looking into available PS
measurements. Rather than considering the flags by TraceAlignDPI as final anomaly, cyber diagnosis and selective invocation of
relay and inverter logs confirm the DER status. This layered approach allows DEROMS to maintain observability and resilience
even when data is missing or manipulated and TraceAlign-DPI
or cyber anomaly tool gives false positives/ negatives.
3) Processing Methodology: TraceAlign-DPI operates as a
continuous integrity monitor by converting incoming measurements into stride-1 overlapping windows of length L (L = 10
samples in our testcase). Each window Xt−L+1:t ∈ RL×F is
scored independently by the model, and anomaly scores are
aligned to the window end time t. To ensure continuity when
data are processed in segments, the last L−1 samples of each
segment are carried over into the next. The system averages
scores from overlapping data chunks to keep them in sync with
time. It only triggers an alert if the score stays high for several
steps in a row, helping avoid false alarms.
4) DEROMS Waiting Time Parameter twait for TraceAlignDPI Invocation: Upon initial detection or suspicion of a DER
outage, DEROMS does not immediately trigger the TraceAlignDPI integrity checker. Instead, a predefined delay interval, denoted as twait , is introduced to allow the system to stabilize and
to account for momentary disturbances that do not constitute
actual outages.
The need for twait is rooted in the dynamic response behavior
of inverter-based DERs under abnormal grid conditions, as
governed by the IEEE 1547-2018 standard [40]. According to
this standard, DERs must support specific grid ride-through capabilities during voltage and frequency excursions, with defined
thresholds and response modes.
One critical mode is cease to energize, or momentary cessation, defined as a temporary suspension of active current
exchange between the DER and the area electric power system
(EPS), while remaining electrically connected. Besides, IEEE
1547 permits DERs to enter momentary cessation or continue
operation under what is termed permissive operation mode. The

duration of momentary cessation before initiating a trip depends
on the DER category:
r Category I and II DERs: Up to 0.5 seconds
r Category III DERs: Up to 12 seconds
Momentary cessations are not actual outages and typically
resolve autonomously. Thus, twait serves as a buffer to avoid
premature RCA or restoration actions in response to temporary
ride-through behavior. Also, during genuine DER outages, twait
allows the microgrid to settle into a new steady-state operating
point. Premature invocation of TraceAlign-DPI may capture
transient effects such as frequency deviations or PQ flow spikes,
which can distort its inference regarding the true DER status.
To balance responsiveness and accuracy, this work proposes the
following values:
r twait = 5 seconds for Category I and II DERs
r twait = 15 seconds for Category III DERs
These values are chosen to exceed the maximum permissible
momentary cessation windows while providing sufficient time
for post-outage transients to settle, ensuring that TraceAlign-DPI
operates on stable system data.
5) Discussion on Scalability and Adaptability: With an increasing number of solar DERs, the computational burden of
DEROMS may rise. However, the framework is designed as
part of the MGMS, which only monitors the DERs under its
own territory, primarily focusing on utility-scale solar DERs,
since their outages have greater cascading impacts on stability.
Thus, assuming a limited number of large DERs per MGMS
is both practical and consistent with real deployments. Besides, the TraceAlign-DPI module, though data-intensive, is
run periodically rather than continuously, reducing real-time
burden. Furthermore, the TraceAlign-DPI tool learns the correlations among system components from their measurements,
independent of DER location. This means it inherently captures
location-specific effects on system dynamics. The framework is
also adaptable to different topologies. Retraining with topologyspecific “normal” operating data enables DEROMS to adjust to
the unique dynamics of each configuration.

III. OUTAGE ROOT CAUSE ANALYSIS LAYER
A. Understanding Outage Scenarios Considering
Cyber-Physical Failures in Control Plane
To enable accurate and explainable outage diagnosis, the root
cause analysis engine must be grounded in a clear taxonomy of
DER outage scenarios, including both expected power system
behaviors and unexpected cyber-physical failure modes. This
subsection outlines the primary causes of DER outages, categorized into normal protection responses and cyber-induced
outages where cyber-induced outages may arise from either nonmalicious failures (e.g., packet loss, communication dropouts)
or adversarial intrusions (e.g., spoofing, replay, or malicious trip
commands), both of which are summarized in Table II.
1) Expected Outages Due to Legitimate Protection Mechanisms: These are normal operating responses of DERs to system
conditions that exceed safety thresholds as prescribed by IEEE
1547-2018:

TABLE I
DECISION OUTCOMES FOR OUTAGE DETECTION AND CLASSIFICATION INTEGRATING DATA FLAG, DPI RESULT, CYBER CLASS, AND RELAY/ INVERTER LOG

ADAN et al.: CYBER RESILIENCE IN SOLAR-RICH NETWORKED MICROGRIDS: A REAL TIME END-TO-END DER OUTAGE
3439

3440

IEEE TRANSACTIONS ON INDUSTRY APPLICATIONS, VOL. 62, NO. 2, MARCH/APRIL 2026

TABLE II
OUTAGE SCENARIOS AND TRACEALIGN-RCA DIAGNOSIS STRATEGIES

r Voltage and Frequency Violations: If voltage or frequency

r Communication Failures: DERs relying on external setdeviates outside predefined ride-through thresholds and
exceeds the allowable duration, DERs are required to trip.
This is common during major grid disturbances or blackouts.
r Overcurrent Events: Although inverter-based DERs have
limited fault current contributions, faults, particularly
ground faults, may induce backfeed currents. Protection relays respond by tripping breakers or commanding inverter
shutdown.
r Islanding Conditions: In case of upstream grid outage,
anti-islanding protection is invoked (e.g., via transfer trip),
disconnecting DERs to avoid unintentional island operation.
r Planned Maintenance Events: DERs may be deliberately
shut down via remote command for maintenance or operational coordination. These events are usually logged and
traceable.
2) Unexpected Outages Due to Non-Malicious CyberPhysical Failures: These failures arise from equipment malfunction, sensor corruption, or communication loss - without
active adversary presence:
r Sensor Failures: Faulty PTs or CTs may falsely indicate abnormal voltage, current, or frequency - erroneously
triggering protection functions. Similarly, falsely reported
breaker open status may force the inverter to enter standby
or offline mode.
r Breaker Failures: Spontaneous tripping or failure to reclose may result in DER disconnection despite acceptable
operating conditions.
r Inverter/Controller Instabilities: Failures in MPPT tracking, PLL desynchronization, or Q-control divergence can
result in internal protection trips.

points or reclose/trip commands from the MGMS/DERMS
may trip if those signals are lost, delayed, or corrupted due
to communication outages.
3) Cyber-Induced Outages From Adversarial Actions: These
events are intentionally triggered by attackers aiming to disrupt
DER operation through manipulation of control layers:
r Breaker Compromise: Attackers remotely issue trip commands or modify protection settings to cause unnecessary
DER disconnection.
r Inverter Hijacking: By injecting malicious commands or
destabilizing setpoints (e.g., PV voltage references, frequency setpoints), attackers can force the inverter into
protective shutdown.
r Denial-of-Service (DoS) Attacks: Saturating the communication channel or firewall with traffic can block the
transmission of essential reclose or operational commands,
leaving DERs inoperable.
Each of these scenarios exhibits unique cross-layer signatures
that the root cause inference engine must recognize and differentiate. Some are identifiable via consistent phasor and SCADA
measurements, while others require deeper analysis of relay
logs, inverter shutdown codes, or cyber-metadata anomalies. The
accuracy and timeliness of root cause classification depend on
the system’s ability to detect and reason over these nuanced
cyber-physical interactions.
B. Cyber-Aware Outage Root Cause Analysis With
TraceAlign-RCA
The TraceAlign-RCA module is designed to diagnose the
true cause of a DER outage by aligning heterogeneous evidence
across multiple layers of observability - physical measurements

ADAN et al.: CYBER RESILIENCE IN SOLAR-RICH NETWORKED MICROGRIDS: A REAL TIME END-TO-END DER OUTAGE

(PMU, SCADA), protection events (relay logs), inverter-side
feedback, and cyber-communication metadata. Given that cyberinduced, sensor-induced, and legitimate protection-induced outages can all manifest similarly at the DER output (e.g., power
drop), disambiguating these requires domain-specific signal
alignment.
Table II summarizes the distinct outage scenarios introduced
earlier along with the expected signatures and trace alignment
strategies used to infer their cause.TraceAlign-RCA traverses
these signal domains, aligns the timing and causality of observed
events, and infers the most likely cause of the outage. For
example, a fault-induced outage will be corroborated by a spike
in PMU current, a relay trip record, and a SCADA breaker
status change. In contrast, a sensor-induced false trip will show
mismatch between DER-end and adjacent-node data, while
cyber-induced outages often leave trails in command metadata,
access logs, or abnormal packet structures. By leveraging this
cross-domain consistency analysis, TraceAlign-RCA improves
outage explainability, enhances operator trust, and enables resilient downstream control decisions.
IV. OUTAGE RESPONSE AND RECOVERY LAYER
Timely and accurate identification of the root cause of a DER
outage is critical not only for system situational awareness but
also for enabling a cyber-resilient recovery strategy. Knowledge
of the outage origin, whether physical, cyber, or systemic,
empowers the MGMS to undertake context-specific responses.
For instance, if the outage is confirmed as a hardware fault,
appropriate field repair crews can be dispatched with the correct
tools, reducing diagnostic delays. If the outage is due to a cyberattack, containment measures (e.g., isolating compromised relay
or inverter units) can be prioritized to prevent lateral propagation.
Most importantly, the inferred cause provides a tentative repair
time estimate or DER recovery horizon, which is essential
for short-term grid reconfiguration, dispatch optimization, and
adaptive islanding decisions within the networked microgrid
cluster. Without this awareness, the system risks overreacting
or underutilizing available flexibility, leading to suboptimal
resilience.
A. Enforcing Scenario Specific Restoration Schemes
Once the root cause is identified and the DER’s operational
status is classified (e.g., trusted, unavailable, or compromised),
the outage response layer invokes scenario-specific restoration
strategies. These are formulated as optimization problems tailored to the physical and cyber-operational constraints of the
networked microgrid. Below, we describe several representative
scenarios along with their restoration objectives and key variables.
Scenario 1: DER Outage Requiring Repair + Redispatch
of Other DERs
In this case, one or more DERs are rendered inoperable due to
hardware failure or confirmed cyber compromise. The objective
is to minimize the overall operational cost of remaining DERs
while also discouraging excess dependency on grid import,
especially if the DER was originally deployed as a non-wires

3441

alternative (NWA). The modified economic dispatch problem is
modeled as:



2
2
DER
C
(P
)
+
λ
·
(P
)
−
(P
Rated)
min
i
PCC
PCC,
i
DER
Pi

, PPCC

i∈G

where: Ci (PiDER ) is the generation cost function of DER i, PPCC
is the real power imported from the main grid either at the point
of common coupling (PCC) of the MG or at distribution feeder
level with λ, being the weighting factor to penalize excess grid
import. The optimization constraints include power flow, power
balance and security constraints as well as topology constraints
if network reconfiguration is permitted with NMGs [48].
Scenario 2: Substation Feeder Outage with DERs Still
Operational
Here, the utility substation feeder is unavailable (e.g., gridside breaker trip), which primarily triggers DER trip due to loss
of grid. Since the DERs in MG boundary are healthy, MGMS
initiates off-grid mode and through coordination within self or
NMG boundary, aims to restore power partially. Restoration focuses on maximizing the supply of critical loads using DER coordination, involving one DER operating in grid-forming mode:

w j Pj
max
Pj

j∈Lcrit

where: Pj is the restored critical load at node j, wj is the priority
weight of load j and Lcrit is the set of critical loads. The MIP
problem is subject to power balance equations as well as DER
dispatch limits, voltage and current limits, and operational
mode constraints for the grid forming agents.
Scenario 3: DER Outage in an Off-grid Microgrid
This case considers an off-grid microgrid that loses a DER
asset. Restoration involves potentially collaborating with NMGs
for additional support and reallocating available DERs to restore
critical loads. DERs deemed operational are included, while
unavailable DERs are excluded. Additionally, if the DER facing
outage is the grid forming (GFM) asset of the corresponding
off- grid Microgrid, then the loss of the DER will result in
discontinuation of power supply from other healthy DERs in
the MG. The flexibilities of NMG have the potential to utilize
these functional DERs in this case by sharing the grid forming
capabilities. The restoration strategy must ensure at least one
GFM asset is reconnected with all healthy Grid following DERs
while maximizing critical loads.

wj Pj s.t. ∃ i ∈ GGFM : i ∈ Topology(T )
max
Pj ,T

j∈Lcrit

where GGFM is the set of grid-forming DERs and Topology(T )
denotes active configuration of the microgrid. Constraints ensure
that at least one GFM DER is present in the operating island,
along with standard load flow and security constraints.
B. Testbed Development
V. IMPLEMENTATION AND EXPERIMENTAL SETUP
The proposed DEROMS framework is validated on a simplified two-microgrid distribution testbed, modeled in RSCAD

3442

Fig. 2.

IEEE TRANSACTIONS ON INDUSTRY APPLICATIONS, VOL. 62, NO. 2, MARCH/APRIL 2026

Layout of the networked microgrid testbed.

and executed in real time using RTDS as shown in Fig. 2. Each
microgrid consists of:
r A solar PV system of 400 kW rated generation (V mpp ∼
2 kV, Impp ∼ 200 A), integrated with an average inverter
model, implementing MPPT and PLL-based grid synchronization, accepting Q setpoints.
r The BESS is modeled with 250 series cells per stack (∼
975V) and 250 stacks in parallel (∼212.5 Ah), yielding ∼
207kWh total energy capacity, corresponding up to 200kW
discharge power for one hour. The BESS is controlled via
operator input setpoints Pbat and Qbat .
r A grid-forming diesel generator with 1 MW of rated capacity capable of black-start and voltage and frequency
reference support.
r The inverters are rated at 1.25 times the DER capacity and
invert the DC side voltage to three phase grid voltage.
r Three loads each having 400 kW of peak demand and
dynamic load profile, is considered as part of the microgrid.
Their cumulative load is modeled with one aggregated
dynamic load component (setpoint for Pload ∼ 1.2M W
when all three loads are supplied at their peak demand).
The power factor is considered ∼ 0.9, making setpoints
for Qload around half of Pload .
r Relay and breakers are modeled at every DER connection
with proper protection mechanisms, which are also capable
of receiving remote commands.
r Control system consisting of PI loops for PLL, MPPT, and
Q setpoint calibration.
The two microgrids are tied to a single 480 V AC distribution
bus, with breakers at each PCC. Each MG connects to the grid
through a separate PCC feeder for independent operation and
operates in grid-connected mode by default. A tie-line breaker
which is normally open allows interconnection to enable networked microgrid operations during islanding or contingency
without creating loops.

well as digital breaker status, streamed at 1 frame/sec. Besides
that, PMUs are placed at the PCC of each microgrid which
streams Voltage and current phasors (V ∠θ, I∠θ), frequency,
and ROCOF at 60frames/sec via a phasor data concentrator.
Following our previous work [49], every 1-second aggregated
data window is processed for denoising, outlier removal, and
further analysis.

A. Data Stream and Monitoring Layer

C. Validation of the Proposed DEROMS Framework

Each DER is monitored through SCADA gateways that provide Analog measurements: Voltage (V ), Current (I), Active
Power (P ), Reactive Power (Q) or SOC levels for battery as

To validate the framework, we adopted our previously developed tools as integral detection modules. First, the multivariate
LSTM-autoencoder anomaly detection component from our

B. Cyber-Physical Attack Simulation
Cyberattack scenarios are implemented using multiple
MATLAB-based host agents interfaced with the testbed and a
python platform to run the DEROMS. These represent IEDs
(Intelligent Electronic Devices) and attacker nodes following
the MITRE ATT&CK for ICS framework [50]. Fig. 3 illustrates
three representative cyber cases and case 4 is the extreme case
of combined data and control plane attack:
r Case 1: No Cyber Manipulation – Events occur without
any adversarial control; used for baseline comparison.
r Case 2: Control Plane Attack – A malicious host (N5)
performs a man-in-the-middle (MITM) attack and sends
unauthorized trip commands, causing forced DER disconnection (ICS Tactic TA0105: Technique T0831 and
T0826).
r Case 3: Data Plane Attack – The attacker intercepts
and modifies the data stream (e.g., falsifies breaker status,
masks actual outages), without affecting physical control
(ICS Tactic TA0105: Technique T0832 and T0828).
r Case 4: Coordinated Control and Data Plane AttackA malicious host (N5) executes a sophisticated two-part
attack. It first sends an unauthorized trip command to force
a DER offline (control plane attack) and simultaneously
intercepts and modifies the outbound data stream to falsely
report that the DER is still operating normally, thereby
masking the forced outage from the operators (data plane
attack).

ADAN et al.: CYBER RESILIENCE IN SOLAR-RICH NETWORKED MICROGRIDS: A REAL TIME END-TO-END DER OUTAGE

Fig. 3.

Cyber-physical scenario simulation encompassing data and control plane.

Fig. 4.

Training loss history from TraceAlign-DPI.

previous work on “Cyber Anomaly-Aware Distributed Voltage
Control with Active Power Curtailment and DERs” framework
[51] was embedded into TraceAlign-DPI’s architecture. Here,
the reconstruction-error scores of the autoencoder on power
and voltage deviations trigger cross-domain PQ-flow alignment
checks, enabling TraceAlign-DPI to confirm or refute data-layer
anomalies against system-wide dynamics [51]. While originally developed for voltage control applications, performance
of this tool can be further enhanced through customized design
adaptations aligned with the proposed framework, which will
be explored in future work. Subsequently, the cyber anomaly
detection technique proposed in [52] serves as the cyber anomaly
detection tool. Besides, the nowcasting method described in
[53], providing a 5 minute forecast, works as the forecasting tool

Fig. 5.

3443

Actual vs. falsified measurements from solar DER.

and is modified with domain knowledge and a tolerance band of
20 percent to serve as the Forecast-aware estimation tool. Simplified restoration problems are solved using python optimization
packages. As part of the microgrid restoration problem, three
loads (400 kW peak each, pf ∼ 0.9) are treated separately with
criticality factors of 1.0, 0.8, and 0.6. The dispatch optimization
applies cost and capacity constraints to BESS and DG units,
while PV output follows irradiation-driven variability.

3444

IEEE TRANSACTIONS ON INDUSTRY APPLICATIONS, VOL. 62, NO. 2, MARCH/APRIL 2026

Fig. 6.

Workflow of proposed DEROMS for case study 1 (corresponding to cyber-physical attack case 4).

Fig. 7.

Workflow of proposed DEROMS for case study 2 (corresponding to cyber-physical attack case 1).

Using the validation dataset, the model achieved Recall of
0.66, Precision of 0.28, and an F1-score of 0.40. The confusion
matrix corresponds to a false negative rate (FNR) of 0.34 and
a false positive rate (FPR) of 0.60. These results confirm that
the model is highly sensitive (successfully detecting two-thirds
of anomalies) while leaving room for improvement in the following steps of root cause analysis of the framework. Through
invocation of relay/inverter log precision and recall improves to
nearly 1. The learning curve shown in Fig. 4 shows the effective
training accuracy of the model.
1) Case Study 1: To demonstrate the cyber resilience of the
proposed DEROMS framework, Case Study 1 simulates an
extreme case of Coordinated Control and Data Plane Attack as
referred to cyber-physical attack case 4 (V-B). Here an attacker
forcefully disconnects the solar from the system and masks this
outage, thus introducing a data plane failure. In our testbed,
the solar DER in Microgrid 2 (MG2) undergoes an outage,
but the real-time measurements are replaced with historical
values as shown in Fig. 5, emulating a replay attack or sensor
malfunction. As a result, OMS is not triggered immediately
since no power loss is reported from DER. However, the periodic TraceAlign-DPI check detects a post-outage like system
shift (e.g., increased import at PCC) and prompts DEROMS
to trigger log inspection from the associated relay/inverter. The
logs confirm the outage but the waveform analysis reveals no
pre-outage fault signature. Instead, the cyber log containing a
trip command issued from an unknown IP address, confirms
that the outage was attack-induced.

Upon confirmed outage, DEROMS proceeds to the recovery
phase. As the root cause is cyber-related, the repair plan focuses
on securing the DER’s IED and relay access. In parallel, economic dispatch is solved under various cost and dispatch limit
constraints resulting in the following solution approaches:
r Solution 1: Penalizing substation power supply causes the
MG2 diesel generator and BESS to increase output locally.
r Solution 2: When MG2 DER dispatch limits are enforced,
MG1 compensates by increasing generation and eventually
reducing substation power supply.
r Solution 3: Penalizing import at MG2 PCC specifically
leads to optimized radial reconfiguration from MG1 to
share power to MG2.
r Solution 4: For tighter operational limits, DEROMS selectively curtails non-critical loads within MG2.
This case demonstrates DEROMS’s ability to detect masked
outages, confirm cyber-induced trip causes, and apply flexible
restoration strategies using the networked microgrid topology
as shown in Fig. 6.
2) Case Study 2: In Case Study 2, the DEROMS framework
is evaluated under a visible outage scenario where the solar trips
due to a grid-side event. The DER power loss is directly observed
in the reported measurements, triggering TraceAlign-DPI. The
DPI module verifies the outage by matching with system-wide
dynamics. This case study corresponds to cyber-physical attack
case 1- No cyber manipulation (V-B).
Relay and inverter logs are then queried to determine the root
cause. The relay waveform reveals an islanding signature, and

ADAN et al.: CYBER RESILIENCE IN SOLAR-RICH NETWORKED MICROGRIDS: A REAL TIME END-TO-END DER OUTAGE

the cyber log confirms receipt of a transfer trip command issued
by the substation relay, likely due to upstream grid loss. Thus,
the outage is classified as an islanding-induced DER trip.
In the recovery layer, the primary repair objective is to restore
the grid-side connection. Meanwhile, MGMS-1 and MGMS-2
independently reconfigure and supply local loads using internal
DERs. A secondary recovery solution is identified when MG2’s
load criticality is increased and networked operation is enabled,
allowing MG1 to export power and support MG2 via the tieline, demonstrating adaptive coordination between networked
microgrids. The workflow is demonstrated in Fig. 7.
In our implementation, TraceAlign detection runs in the millisecond range, with restoration optimization also completed
in milliseconds. Excluding the twait parameter, the framework
generates a decision within 1 s. Perhaps, fast detection is essential to prevent local outages from cascading, and to limit
adversarial dwell time during cyber events. While communication and actuation may add latency in practice, the framework
remains suitable for real-time microgrid operation.

VI. CONCLUSIONS AND FUTURE WORK
This work presented a novel cyber-resilient DER Outage
Management System Framework (DEROMS) designed for
solar-rich networked microgrids. The primary contribution of
this paper is the theoretical formulation and architectural design
of the DEROMS, which includes a multi-layer architecture
comprising: (i) real-time outage detection through TraceAlignDPI, (ii) root cause analysis via TraceAlign-RCA using synchronized physical and cyber traces, and (iii) scenario-aware
restoration optimization leveraging the flexibility of networked
microgrids. As a critical proof-of-concept, a real-time hardwarein-the-loop testbed was developed to validate the system under both physical faults and cyber-attack scenarios, including
data falsification and unauthorized control plane manipulation.
Results demonstrated DEROMS’s capability to detect visible
and hidden outages, infer cyber-physical root causes, and adaptively reconfigure microgrid operations for resilient restoration.
By integrating real-time monitoring, data authenticity validation, and adaptive restoration strategies, the system aims to
enhance the resilience and reliability of modern distribution
systems.
The work presented herein is positioned as a theoretical and
methodological foundation upon which more extensive, largescale experimental analysis must be built. This work mainly
focuses on solar DERs, but the DEROMS framework is broadly
applicable to other DER types such as wind turbines, BESS,
EV chargers, and hybrid inverters. Since the outage root causes,
fault signatures, and forecasting techniques are DER-specific,
tailoring the analytics to diverse resources remains an important
direction for future research. Additionally, periodic invocation
of the TraceAlign-DPI tool reduces the real-time computational
burden but improvements can be made for faster response, better
accuracy and greater robustness against advanced cyber threats.
Integrating forecasting techniques, state estimation, and distributed optimization methods will further enhance the system’s
autonomy and scalability.

3445

REFERENCES
[1] E. Wesoff, “Microgrids on the march: Utilities are building out new business models to make islanding work,” Greentech Media, 2020. archived
web article.
[2] “Solar PV microgrid market size & share, growth forecasts 2034,” 2024,
archived industry report. [Online]. Available: https://www.gminsights.
com/industry-analysis/solar-pv-microgrid-market
[3] D. T. Ton and M. A. Smith, “The U.S. department of energy’s microgrid
initiative,” Electricity J., vol. 25, no. 8, pp. 84–94, 2012.
[4] “Utility scale microgrid market size, industry report 2025–2034,” 2024,
archived industry report. [Online]. Available: https://www.gminsights.
com/industry-analysis/utility-scale-microgrid-market
[5] “2023 sustainable energy in America factbook,” 2023, public release
via BCSE and BNEF collaboration. [Online]. Available: https://bcse.org/
factbook
[6] “Community solar: State, local, and tribal governments,” Nat. Renewable
Energy Lab. (NREL), Golden, CO, USA, 2025. [Online]. Available: https:
//www.nrel.gov/state-local-tribal/community-solar
[7] K. Eber and D. Corbus, “Hawaii solar integration study: Executive summary,” Nat. Renewable Energy Lab., Tech. Rep. NREL/TP-5500-57215,
Jun. 2013. [Online]. Available: https://docs.nrel.gov/docs/fy13osti/57215.
pdf
[8] J. J. Cook, K. Ardani, E. O’Shaughnessy, B. Smith, and R. Margolis,
“Expanding pv value: Lessons learned from utility-led distributed energy
resource aggregation in the United States,” Nat. Renewable Energy Lab.,
Golden, CO, USA, Tech. Rep. NREL/TP-6A20-71984, 2018. [Online].
Available: https://www.nrel.gov/docs/fy19osti/71984.pdf
[9] “Solar case studies,” Nat. Rural Electric Cooperative Assoc.
(NRECA), Arlington, VA, USA, Aug. 2015. [Online]. Available:
https://www.cooperative.com/programs-services/bts/documents/sunda/
solar-case-studies.pdf
[10] “Solar plant dynamic modeling guidelines,” Western Electricity Coordinating Council (WECC), Tech. Rep., 2014. [Online]. Available: https:
//www.wecc.org/sites/default/files/documents/program/2024/WECC\
%20Solar\%20Plant\%20Dynamic\%20Modeling\%20Guidelines.pdf
[11] J. St John, “A snapshot of key US non-wires alternatives projects,
from Brooklyn to Booth Bay and beyond,” Greentech Media, 2018,
archived web article. [Online]. Available: https://www.greentechmedia.
com/articles/read/a-snapshot-of-key-us-non-wires-alternatives-projects
[12] P. De Martini and L. Schwartz, “Distribution system evolution,” U. S.
Department of Energy, Office of Electricity, Washington, DC, USA,
Tech. Rep., Nov. 2023. [Online]. Available: https://www.energy.gov/
sites/default/files/2023-11/2023-11-01\%20Distributed\%20System\
%20Evolution\%20nov\%202023\%20r1_optimized.pdf
[13] “The role of distributed energy resources in today’s grid transition,” GridLab, Tech. Rep., Aug. 2018. [Online]. Available: https://gridlab.org/wpcontent/uploads/2022/10/GridLab_RoleOfDER_online.pdf
[14] C. Volkmann, “Integrated distribution planning: A path forward,” GridLab,
Tech. Rep., 2018, technical white paper developed for regulatory proceedings. [Online]. Available: https://gridlab.org/portfolio-item/integrateddistribution-planning/
[15] B. Palmintier, “On the Path to SunShot: Emerging issues and challenges
in integrating solar with the distribution system,” Nat. Renewable Energy
Lab., Golden, CO, USA, Tech. Rep. NREL/TP-5D00-65331, May 2016.
[Online]. Available: https://docs.nrel.gov/docs/fy16osti/65331.pdf
[16] “EPIC 2.03A: Smart Inverters – Project 2.03A Final Report,” Pacific Gas
and Electric Company (PG&E), San Francisco, CA, USA, Feb. 2019. [Online]. Available: https://www.pge.com/assets/pge/docs/about/corporateresponsibility-and-sustainability/PGE-EPIC-Project-2.03A-Final.pdf
[17] S. E. Ahmadi, N. Rezaei, and H. Khayyam, “Energy management system
of networked microgrids through optimal reliability-oriented day-ahead
self-healing scheduling,” Sustain. Energy, Grids, Netw., vol. 23, 2020, Art.
no. 100387. [Online]. Available: https://www.sciencedirect.com/science/
article/pii/S2352467720303180
[18] “System planning impacts from distributed energy resources (spiderwg)
scope document,” North Amer. Electric Rel. Corporation, Tech. Rep.,
Mar. 2023. [Online]. Available: https://www.nerc.com/comm/RSTC/
SPIDERWG/SPIDERWG\%20Scope.pdf
[19] “How DERMS delivers modern utility management,” 2022, Oracle Utilities Resources. [Online]. Available: https://www.oracle.com/industries/
utilities/resources/how-derms-delivers-modern-utility-management/
[20] “Visibility of distributed energy resources for future power system security,” 2023. [Online]. Available: https://policycommons.net
[21] “Making the connection: The importance of der visibility to grid support
and modernization,” Electric Power Res. Inst. (EPRI), Palo Alto, CA, USA,
Tech. Rep. 3002013388, 2018. [Online]. Available: https://www.epri.com/
research/products/000000003002013388

3446

IEEE TRANSACTIONS ON INDUSTRY APPLICATIONS, VOL. 62, NO. 2, MARCH/APRIL 2026

[22] J. F. Clemente, “Cyber security for critical energy infrastructure,” Ph.D.
dissertation, Dept. Nat. Secur. Affairs, Naval Postgraduate Sch., Monterey,
CA, USA, 2018.
[23] J. Qi, A. Hahn, X. Lu, J. Wang, and C.-C. Liu, “Cybersecurity for
distributed energy resources and smart inverters,” IET Cyber-Phys. Syst.,
Theory Appl., vol. 1, no. 1, pp. 28–39, 2016.
[24] E. M. Stewart, M. J. Culler, and R. V. Stolworthy, “Utility-scale operational consequences for solar grid services,” Idaho Nat. Lab., Tech. Rep.,
Feb. 2025. [Online]. Available: https://inldigitallibrary.inl.gov/sites/STI/
STI/Sort_151062.pdf
[25] “Grid impacts from distributed energy resources: Research and
development priorities,” Electric Power Res. Inst. (EPRI), Palo
Alto, CA, USA, Tech. Rep., Jun. 2020. [Online]. Available:
https://www.dret-ca.com/wp-content/uploads/2021/03/Grid-Impactsfrom-Distributed-Energy-Resources.pdf
[26] Y. Liao, Y. Weng, C.-W. Tan, and R. Rajagopal, “Quick line
outage identification in urban distribution grids via smart meters,” CSEE J. Power Energy Syst., vol. 8, no. 4, pp. 1074–1086,
Jul. 2022.
[27] Y. Liao, C. Xiao, and Y. Weng, “Quickest line outage detection with low
false alarm rate and no prior outage knowledge,” in Proc. IEEE Power
Energy Soc. Gen. Meeting, 2022, pp. 1–5.
[28] A. Anwar, A. N. Mahmood, and Z. Tari, “Ensuring data integrity of opf
module and energy database by detecting changes in power flow patterns
in smart grids,” IEEE Trans. Ind. Informat., vol. 13, no. 6, pp. 3299–3311,
Dec. 2017.
[29] J. Wei, “A data-driven cyber-physical detection and defense strategy
against data integrity attacks in smart grid systems,” in Proc. IEEE Glob.
Conf. Signal Inf. Process. 2015, pp. 667–671.
[30] S. Ahmed, Y. Lee, S.-H. Hyun, and I. Koo, “Unsupervised machine
learning-based detection of covert data integrity assault in smart grid
networks utilizing isolation forest,” IEEE Trans. Inf. Forensics Secur.,
vol. 14, no. 10, pp. 2765–2777, Oct. 2019.
[31] S. Lu, B. Phung, and D. Zhang, “A comprehensive review on DC arc
faults and their diagnosis methods in photovoltaic systems,” Renewable
Sustain. Energy Rev., vol. 89, pp. 88–98, 2018. [Online]. Available: https:
//www.sciencedirect.com/science/article/pii/S1364032118300996
[32] B. Li, C. Delpha, D. Diallo, and A. Migan-Dubois, “Application of
artificial neural networks to photovoltaic fault detection and diagnosis: A review,” Renewable Sustain. Energy Rev., vol. 138, 2021,
Art. no. 110512.
[33] Y.-Y. Hong and R. A. Pula, “Methods of photovoltaic fault detection and classification: A review,” Energy Rep., vol. 8, pp. 5898–5929,
2022. [Online]. Available: https://www.sciencedirect.com/science/article/
pii/S2352484722008022
[34] D. S. Pillai and N. Rajasekar, “A comprehensive review on protection
challenges and fault diagnosis in PV systems,” Renewable Sustain. Energy
Rev., vol. 91, pp. 18–40, Aug. 2018.
[35] S. Madeti and S. Singh, “A comprehensive study on different types of
faults and detection techniques for solar photovoltaic system,” Sol. Energy,
vol. 158, pp. 161–185, Dec. 2017.
[36] A. Mellit and S. A. Kalogirou, “Artificial intelligence techniques for photovoltaic applications: A review,” Prog. Energy Combustion Sci., vol. 34,
no. 5, pp. 574–632, 2008. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S0360128508000026
[37] A. Triki-Lahiani, A. Bennani-Ben Abdelghani, and I. Slama-Belkhodja,
“Fault detection and monitoring systems for photovoltaic installations:
A review,” Renewable Sustain. Energy Rev., vol. 82, pp. 2680–2692,
2018. [Online]. Available: https://www.sciencedirect.com/science/article/
pii/S1364032117313618
[38] M. Y. Worku, M. A. Hassan, L. S. Maraaba, and M. A. Abido, “Islanding detection methods for microgrids: A comprehensive review,”
Mathematics, vol. 9, no. 24, 2021, Art. no. 3174. [Online]. Available:
https://www.mdpi.com/2227-7390/9/24/3174
[39] A. Salazar-Llinas, A. Ginart, and C. Restrepo, “Observer based sensor
fault tolerant for grid tied - solar inverters,” in Proc. 6th Annu. IEEE Green
Technol. Conf., 2014, pp. 69–74.
[40] T. Basso, “IEEE 1547 and 2030 Standards for Distributed Energy Resources Interconnection and Interoperability with the Electricity Grid,”
Tech. Rep. NREL/TP-5D00-63157, Nat. Renewable Energy Lab., Golden,
CO, USA, Dec. 2014. [Online]. Available: https://docs.nrel.gov/docs/
fy15osti/63157.pdf
[41] “Distributed energy resources connection, modeling, and reliability
considerations,” 2017. Accessed: May 30, 2025. [Online]. Available: https://www.nerc.com/pa/RAPA/ra/Reliability\%20Assessments\
%20DL/Distributed_Energy_Resources_Report.pdf

[42] “Electric Rule 21: Generating facility interconnections,” Pacific
Gas and Electric Company (PG&E), San Francisco, CA, USA,
Aug. 2025. [Online]. Available:https://www.pge.com/tariffs/assets/pdf/
tariffbook/ELEC_RULES_21.pdf
[43] A. Gholami and A. K. Srivastava, “ORCA: Outage root cause analysis
in DER-rich power distribution system using data fusion, hierarchical
clustering and FP-growth rule mining,” IEEE Trans. Smart Grid, vol. 15,
no. 1, pp. 667–676, Jan. 2024.
[44] L. Che, X. Liu, Z. Li, and Y. Wen, “False data injection attacks induced
sequential outages in power systems,” IEEE Trans. Power Syst., vol. 34,
no. 2, pp. 1513–1523, Mar. 2019.
[45] K. A. Haque, S. Sun, X. Huo, A. E. Goulart, and K. R. Davis, “Scalable
discrete event simulation tool for large-scale cyber-physical energy systems: Advancing system efficiency and scalability,”, IEEE Access, vol. 13,
pp. 101900–101921, 2025.
[46] Z. Wang, B. Chen, J. Wang, and C. Chen, “Networked microgrids for
self-healing power systems,” IEEE Trans. Smart Grid, vol. 7, no. 1,
pp. 310–319, Jan. 2016.
[47] A. Arif and Z. Wang, “Networked microgrids for service restoration
in resilient distribution systems,” IET Gener., Transmiss. Distribution,
vol. 11, pp. 3612–3619, 2017. [Online]. Available: https://digital-library.
theiet.org/doi/abs/10.1049/iet-gtd.2017.0380
[48] S. Konar, A. K. Srivastava, and A. Dubey, “Distributed optimization
for autonomous restoration in der-rich distribution system,” IEEE Trans.
Power Del., vol. 38, no. 5, pp. 3205–3217, Oct. 2023.
[49] J. Adan, D. Aggarwal, S. Basumallik, and A. Srivastava, “D-syncaed:
Distribution synchrophasor anomaly and event detection tool in real-time,”
in Proc. Int. Conf. Smart Grid Synchronized Meas. Analytics 2024, pp. 1–6.
[50] B. E. Strom, A. Applebaum, D. P. Miller, K. C. Nickels, A. G. Pennington,
and C. B. Thomas, “Mitre att&ck: Design and philosophy,” MITRE
Corporation, McLean, VA, USA, Tech. Rep. 10AOH08A-JC, 2018.
[51] P. S. Sarker, M. F. Rafy, A.K. Srivastava, and R. K. Singh, “Cyber anomalyaware distributed voltage control with active power curtailment and ders,”
IEEE Trans. Ind. Appl., vol. 60, no. 1, pp. 1622–1633, Jan./Feb. 2024.
[52] A. Ahmed et al., “Cyber physical security analytics for anomalies in
transmission protection systems,” IEEE Trans. Ind. Appl., vol. 55, no. 6,
pp. 6313–6323, Nov./Dec. 2019.
[53] S. Nazaralizadeh, P. Banerjee, S. Karimi, A.K. Srivastava, and P.
Famouri, “Very-short-term solar power prediction using a suboptimal
multiple fading Kalman filter,” in Proc. IEEE Texas Power Energy Conf.,
2025, pp. 1–6. [Online]. Available: http://dx.doi.org/10.36227/techrxiv.
173808181.11951244/v1
Jannatul Adan (Graduate Student Member, IEEE)
received the B.Sc. degree in electrical and electronics
engineering from the Bangladesh University of Engineering and Technology, Dhaka, Bangladesh, in 2019.
She is currently working toward the Ph.D. degree in
electrical engineering with West Virginia University,
Morgantown, WV, USA. Her research focuses on
cyber-physical resiliency of DER-rich distribution
power systems.
Md Fazley Rafy (Member, IEEE) received the B.Sc.
degree in electrical and electronics engineering from
the University of Dhaka, Dhaka, Bangladesh, in 2017.
He is currently working toward the Ph.D. degree
in computer science with West Virginia University,
Morgantown, WV, USA. His research focuses on
the security and resilience of cyber-physical energy
systems.

Anurag K. Srivastava (Fellow, IEEE) received the
Ph.D. degree in electrical engineering from the Illinois Institute of Technology, Chicago, IL, USA, in
2005. He is currently the Raymond J. Lane Professor
and Chairperson with Computer Science and Electrical Engineering Department, West Virginia University, Morgantown, WV, USA. His research focuses
on data-driven algorithms for power system operation
and control, including resiliency analysis. He is the
Chair of IEEE PES Power System Operation SC,
Co-Chair of Tools for Power Grid Resilience TF, and
Co-Chair of Microgrid Application and Implementation WG.
PAPER_TEXT
