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
# [401] Detection of Voltage Droop-Induced Timing Fault Attacks Due to Hardware Trojans
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
编号：401
题名：Detection of Voltage Droop-Induced Timing Fault Attacks Due to Hardware Trojans
年份：2024
DOI：10.1109/tcad.2024.3418395
来源：IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems
PDF：paper/10.1109_TCAD.2024.3418395.pdf
已有粗分类：恶意流量、暗网与攻击检测
二级关联：无
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\401.txt
- 原始字符数：77075
- 本次发送字符数：77075
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
280

IEEE TRANSACTIONS ON COMPUTER-AIDED DESIGN OF INTEGRATED CIRCUITS AND SYSTEMS, VOL. 44, NO. 1, JANUARY 2025

Detection of Voltage Droop-Induced Timing Fault
Attacks Due to Hardware Trojans
Jonti Talukdar , Akshay Vyas , and Krishnendu Chakrabarty , Fellow, IEEE

Abstract—Recent breakthroughs in heterogeneous integration
(HI) using 2.5-D/3-D packaging technology have led to several
advances in the semiconductor industry, increasing yield while
reducing overall cost and time-to-market. However, the diversification of the HI supply chain has led to several sources of distrust
due to the use of black-boxed third-party intellectual property
(IP), outsourced fabrication, assembly and test facilities during
the design and manufacturing process. We demonstrate the
susceptibility of chiplet IPs to timing failure due to voltage droop
in the power distribution network (PDN) induced by the insertion
of chiplet level ring-oscillator (RO)-based hardware Trojans. We
present an end-to-end methodology for design, placement, and
insertion of RO-based Trojans in chiplet designs followed by
characterizing their contribution to the dynamic voltage droop
induced within the on-chip PDN. We quantify this PDN impact
on timing paths and develop a systematic method to rank the
susceptibility of different data paths toward a voltage droop
event. We utilize this presilicon security analysis framework to
evaluate voltage droop-based attack susceptibility for a variety
of IPs, including some from the CEP benchmark. We also
develop a machine learning-guided time-series anomaly detection
framework to detect voltage droop-based anomalies on functional
workloads running on different benchmarks, demonstrating the
effectiveness of an convolutional autoencoders in detecting voltage
droop-induced timing anomalies.
Index Terms—2.5D ICs, anomaly Detection, autoencoders,
hardware Trojans, runtime security, voltage droop.

I. I NTRODUCTION
HE GLOBALIZATION of the integrated circuit (IC)
supply chain has led to considerable challenges in intellectual property (IP) security. Of particular concern is the
vulnerability to IP theft through attacks, such as counterfeiting,
IC overbuilding, netlist reverse-engineering, as well as the
vulnerability, to runtime security due to malicious design
modifications [1], [2]. Security challenges associated with the
integration of chiplets on an interposer can lead to threats

T

Manuscript received 21 October 2023; revised 6 April 2024 and 5 June
2024; accepted 15 June 2024. Date of publication 24 June 2024; date of
current version 26 December 2024. This work was supported in part by the
Semiconductor Research Corporation under Grant 3199.001, by CHIMES,
one of the seven centers in JUMP 2.0, an SRC Program sponsored by DARPA
under Grant 3136.005; and in part by the National Science Foundation under
Grant CNS-2011561. This article was recommended by Associate Editor
J. Rajendran. (Corresponding author: Jonti Talukdar.)
Jonti Talukdar is with the Department of Electrical and Computer
Engineering, Duke University, Durham, NC 27708 USA (e-mail:
jonti.talukdar@duke.edu).
Akshay Vyas and Krishnendu Chakrabarty are with the School of Electrical,
Computer and Energy Engineering, Arizona State University, Tempe, AZ
85287 USA.
Digital Object Identifier 10.1109/TCAD.2024.3418395

arising from within the system, e.g., through rogue or untrusted
chiplets. Threats can also arise from outside the system, e.g.,
through an untrusted end-user [3]. Attacks may be launched
with the objective of either stealing the IP (IP theft) or
disrupting the normal functioning of the system [denial of
service (DoS)]. For example, untrusted chiplets in a system
can deliberately affect the functioning of trusted chiplets by
increasing the levels of electromagnetic interference (EMI)induced voltage fluctuations or affect the power distribution
networks (PDNs) by introducing voltage droops through malicious modifications in the design [4]. Similarly, an attacker can
steal IP by extracting the point-to-point interconnects across
chiplet IPs and observing data transfers between chiplets
through physical side-channels, such as data buses on the
interposer or scan chains [5], [6].
In this work, we explore the security challenges arising from
the integration of chiplets that contain malicious modifications.
We first review existing solutions for runtime security and
identify their shortcomings [7], [8]. A key shortcoming is
the assumption of a secure runtime environment during functional operation, which limits the scope of existing protection
schemes to threats arising from within the system and restrict
them to solutions implemented at a bus-level, e.g., rogue
chiplets issuing malicious instructions to make unauthorized
requests to memory addresses [8]. We describe a more comprehensive threat model that considers the relevant attack surfaces
applicable for chiplet IPs that may be part of a heterogeneously
integrated system. We next demonstrate the susceptibility of
such IPs to timing failure due to voltage droop in the PDNs.
Based on the proposed threat model, malicious modifications,
such as the insertion of ring oscillators (ROs), can be made
to chiplets fabricated throughout the untrusted supply chain.
These ROs, when triggered, can induce voltage droop in the
PDNs across both chiplets as well as the interposer. This
can exacerbate the delay of functional paths in the design,
potentially leading to timing failure during runtime.
We present an end-to-end vertically integrated EDA toolflow
that leverages existing industry tools to support the design,
layout, and full-chip simulation of chiplet IPs using the
ASAP 7-nm standard cell library. We utilize this toolflow to
analyze the voltage-droop induced on the PDN due to the
activation of RO-based Trojans inserted in chiplets. We next
evaluate the voltage droop susceptibility of functional timing
paths by derating each timing path based on the worst-case
voltage droop experienced by the design running a functional
workload. This framework can be used as a presilicon security
verification tool to identify potential functional paths that are

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1937-4151 
See https://www.ieee.org/publications/rights/index.html for more information.

TALUKDAR et al.: DETECTION OF VOLTAGE DROOP-INDUCED TIMING FAULT ATTACKS

281

Fig. 1. Sources of distrust arising from the globalized supply chain along with their associated threats: IP vendors, COTS chiplets, untrusted foundries, test
facilities, and end users [5].

susceptible to voltage droop-induced timing failures due to the
malicious modifications in the supply chain. We also evaluate
the sensitivity of the voltage droop anomalies as a function
of the number of Trojans inserted in the chiplets of varying
sizes. In addition, we develop a machine learning-based time
series anomaly detection framework that utilizes autoencoders
to detect anomalous voltage droop values triggered due to the
activation of RO-based hardware Trojans during runtime. We
also investigate the performance of autoencoders in detecting
voltage droop anomalies induced by non RO-based Trojans,
such as glitch-based power wasting circuits, demonstrating the
effectiveness of the ML-based method in detecting voltage
droop anomalies for different Trojan types.
The main contributions of this article are as follows:
1) we demonstrate the susceptibility of chiplet IPs to timing
failure due to voltage droop in the PDN through insertion
of RO-based Trojans and glitch-based power wasting circuits;
2) we develop an end-to-end EDA methodology for design,
layout, post-layout voltage droop characterization and timing
deration analysis of various chiplet designs with hardware
Trojan inserted; 3) we develop a convolutional autoencoderbased time series anomaly detection framework to identify
anomalous voltage droop values across chiplet PDNs arising
from RO-based and glitch-based hardware Trojans; and 4) we
perform a security analysis for different numbers of chipletbased Trojan insertions in IPs of various sizes.
The remainder of this article is organized as follows:
Section II reviews background and prior work. Section III
presents the RO-based Trojan design and its characterization.
Section IV presents the overall end-to-end flow for voltage
droop analysis. Section V presents the security evaluation for
timing deration on different IP-level functional workloads.
Section VI presents the time series anomaly detection in voltage droop data across different benchmarks IPs. Section VII
presents a discussion on mitigating voltage droop-based
attacks and Section VIII concludes this article.
II. BACKGROUND AND P RIOR W ORK
A. Security Threats in Heterogeneous Supply Chain
Emerging threats for heterogeneous integration (HI) systems
can be aimed at either IP theft or disruption of functionality
during runtime. These threats can be mounted from untrusted

sources that may be internal to the system (untrusted or rogue
chiplets) or external in nature (untrusted end users) (Fig. 1).
Rogue or Untrusted IP: Commercial off-the-shelf (COTS)
IPs may be sourced from different manufacturers and thirdparty IP distributors. As a result, without proper trust and
authentication, an untrusted chiplet with rogue IP may exercise
unauthenticated functions through the shared interconnects
implemented on the interposer. Since rogue IPs may have
access to the data being transferred through the interconnect,
they may intercept, interrupt, modify, or fabricate the data
flowing through the common interconnect. Untrusted IPs may
include malicious modifications that can cause timing failures
due to PDN voltage droop, as demonstrated in this work.
Untrusted End-Users: While rogue chiplets with may pose
threats that are internal to the functioning of the system,
untrusted end users may present threats external to the system.
In such a scenario, IP theft is the most prominent threat
posed by an untrusted end user because they may try to
exploit both physical and scan-based side channels, as well
as traditional approaches, such as netlist reverse engineering
(RE), to achieve their objectives. Threats arising from rogue
or untrusted chiplets are likely to be targeted at disruption
of service while those arising from untrusted end users are
targeted toward IP theft.
B. Prior Work on IP Security
In [8], a root-of-trust (RoT) system is proposed to protect
against system-level threats through the use of a security monitor that implements security policies, also known as hardware
security features or HWSFs, that monitor against malicious
access of the system’s shared memory resources in real
time. The protocol consists of policies that manage memory
access in a fully controlled setting, ensuring shared memory
transactions emanating from trusted and untrusted chiplets
are segregated and verified. This protocol is implemented
through a secure transaction monitor (TRANSMON) that is
also implemented as part of the active interposer. Similarly,
another security scheme focuses on achieving runtime security
by enforcing system level runtime monitoring of a chiplets
through a secure network-on-chip (NoC) architecture, which is
implemented in a trusted setting [9]. This NoC runs a protocol
called Hybrid Link protocol or HL protocol and supports both
point to point and broadcast mode.

282

IEEE TRANSACTIONS ON COMPUTER-AIDED DESIGN OF INTEGRATED CIRCUITS AND SYSTEMS, VOL. 44, NO. 1, JANUARY 2025

Existing RoT-based solutions focus on protection against
malicious modifications or system level threats arising from
untrusted chiplets or IP theft [5]. This is ensured through
the following: 1) a secure interposer that is fabricated in a
trusted environment and 2) runtime monitoring protocols that
are integrated with the chiplet and enforced by the secure
interposer. These security policies are aimed at preventing
malicious modification of shared memory and ensure data
integrity. However, these methods fail to consider attacks that
may be mounted through PDN characteristics such as voltage
droops. As such side-channel attacks remain outside the scope
of bus-based security solutions, they can manifest as timing
failures in functional datapaths of the design. Thus, there exists
a need for a side-channel vulnerability assessment framework.
C. Threats Due to Voltage Droop-Based Power Side
Channels
Prior work in power-based side channel security has focused
on exploiting information leakage through the collection of
numerous power traces with the objective of launching differential cryptanalysis attacks against cryptographic IP [10]. Such
cryptanalysis-based attacks are targeted to reveal encryption
keys. Cryptographic applications have been shown to be
easily susceptible to power-based side channel attacks due to
correlation between the total power consumed by an IP and
the cryptographic workload being run on the IP [11]. The
importance of on-chip PDNs in the context of such powerbased side channel attacks has also been investigated [12].
The increasing use of secure programmable hardware,
including FPGAs, as on-chip security engines has also motivated the analysis of power-based side-channel attacks for
programmable logic. Gnad et al. [13] showed voltage droop
due to the insertion and activation of ROs as an effective method to induce runtime faults, leading to functional
failure of cloud-based FPGAs. In [14], the effectiveness
of asynchronous ROs to launch voltage-based timing failures on FPGA-based deep learning accelerators has been
demonstrated. Both these attacks exploit RO-based malicious
modifications to introduce timing failures. Designing methods
have also been studied to mitigate such power-based side channel leakage in FPGA settings. In [15], ROs were repurposed to
act as sensors that remain sensitive to changes in the voltage
droop. These sensors can be implemented at the PCB level to
monitor voltage droop, but they remain susceptible to errors
and noise. In [16], an active fence of ROs is inserted between
the victim and the attacker IP that creates an additional layer of
workload-independent voltage fluctuations, thereby reducing
the susceptibility to correlation-based power analysis attacks.
D. Limitations of Prior Work on Voltage Droop-Induced
PDN Security
Voltage droop-based attacks and countermeasures for both
cryptographic and FPGA-based use-cases have been studied
in prior work [17], [18]. Attacks, such as [17], exploit the
timing vulnerability of FPGA platforms to on-chip voltage
droop events triggered by on-board ROs. While ROs are used
to cause timing failure, no countermeasures are proposed in

that work to either detect or prevent such RO-induced timing
attacks during runtime.
A technique to detect Trojans that specifically impact circuit
path delay has been proposed in [19]. This method uses clock
frequency sweeping to generate delay signatures for different
logic paths in the design. These signatures can be impacted
by a Trojan’s load capacitance, thereby allowing designers to
identify delay-based Trojans. Vakil et al. [20] extended this
work by improving the timing model to account for delay noise
and uses a neural network to track process drift. However, both
these methods remain workload agnostic and fail to account
for situations where dynamic workloads may induce timing
failure during runtime. These methods also do not provide a
learnable mechanism to track the state of the IP during runtime
and detect attacks in functional mode. Individual currentsensing path delay monitors that convert current activity on
local power grid into a timing pulse have also been proposed
to screen delay-based hardware Trojans [21]. These monitors
can be integrated with current comparators calibrated to reduce
the impact of process variations and deployed in clusters
connected to scan chains. This method relies on the use of
scan chains to detect Trojans, thereby preventing the ability
to detect them during runtime in functional mode. In [22], an
accurate characterization of path delays is performed while
also modeling worst-case IR drop in power rails. This IR dropaware timing characterization is then used to suggest design
optimizations to improve circuit power and performance.
However, these optimization-based methods [22], [23] in IP
design can lead to narrower margins on many timing paths,
making such designs even more susceptible to workloaddriven voltage droop events. Zeng et al. [24] presented a
method to calibrate ROs under the presence of IR-drop for
hardware Trojan detection, but it also does not consider
dynamic workloads or timing impact on path delays.
The prior methods discussed above also do not perform a
Trojan-based sensitivity analysis to deal with scenarios where
dynamic loading conditions of the IP may cause Trojans,
which originally have minimal impact on path delays, to cause
timing failure due to dynamic changes in workload. They
also do not include a learnable method to characterize Trojan
behavior in dynamic runtime conditions, and therefore have
limited applicability for runtime detection.
E. Threat Model
As discussed in Section II-A, there exist multiple sources of
distrust in the paradigm of heterogeneously integrated systems.
Therefore, the threat model assumes the following: 1) use of
black-boxed COTS IPs with limited visibility to the internals
of the IP, allowing attackers to insert malicious modifications
in the design and 2) use of untrusted foundries and OSATs
for chiplet/IP fabrication. Thus, the integrated system can
be vulnerable to attacks mounted by either the COTS IP
designers, untrusted foundry, or OSAT facilities. Without an
effective solution to protect the different IPs in the design,
it is impossible to guarantee the security of a heterogeneous
system, given that many of its components are sourced from
untrusted entities.

TALUKDAR et al.: DETECTION OF VOLTAGE DROOP-INDUCED TIMING FAULT ATTACKS

Fig. 2.

283

Example RO design that can be inserted in a malicious chiplet.

Exhaustive security verification of black-box IPs is challenging; it might not always be possible for system integrators
to visually inspect and verify such blocks. Thus, it is possible
for untrusted users to make malicious modifications that can
then be triggered during functional operation of the design,
leading to DoS type attacks. For this study, we focus on
modifications made within the same chiplet. Prior work has
shown that these modifications can be introduced through
foundry side engineering change order (ECO) flows that make
layout level modifications within third-party chiplets [25],
[26], [27], [28].

Fig. 3. (a) Illustration of layout for a 31-stage RO with mesh-type PDN
and (b) distribution of Vdroop for the same RO across a range of values from
1.2 mV (blue) to 11.9 mV (orange).

III. RO-BASED T ROJANS IN F UNCTIONAL IP S
ROs are widely used for a variety of in-silicon applications, including process characterization, aging monitoring,
and lifecycle management [29], [30], [31]. The voltage carried
across a PDN droops due to variable loading characteristics
across the PDN. The voltage droop Vdroop across a power line
is proportional to the resistance of the line along with the
inductive impedance across the same line. Inductive effects
arise from rapid differences in the electrical current and is
influenced by both spatial and temporal circuit switching
activity, which in turn is dependent on system behavior. Thus,
Vdroop = IR + L(di/dt).
ROs, when triggered, act as fast switching components
drawing significant amount of current and inducing voltage
droop in the power rails for downstream logic. This can
exacerbate the delay of timing critical paths in the design.
This voltage droop induced timing deration is quantified as
follows [32]:
Tdroop = Tnom ×

th
1 − VVnom

1−

Vth

(1)

(Vnom −Vdroop )

where Vnom is the nominal supply voltage and Tnom is the path
delay without any voltage droop. For the ASAP 7-nm process,
Vnom = 1.1 V and Vth = 0.15 V.
A. Characterizing RO-Induced Voltage Droop
In this section, we describe the design and architecture of
an example RO-based Trojan that can be potentially inserted
into a chiplet or the interposer. Fig. 2 illustrates the design of
a 3-stage RO. Each RO is triggered by an AND gate that is
driven by an enable signal. The standard cells used for the RO
design share the same PDN as the functional logic within the
chiplet (and the interposer if it is of the active type), thereby
inducing voltage droop for the functional logic downstream.
Fig. 3 illustrates the layout (a) and voltage droop distribution
(b) for every standard cell in a 31-inverter RO. Each inverter in
the RO chain has a total internal power consumption of about
49.3 mW, with the 31-inverter RO occupying a footprint of
39.09 μm2 . The small footprint makes it easy to insert such
ROs in black-boxed chiplet IPs as well as insertion within the

Fig. 4. Percentage change in voltage droop at four different locations within
the FIR chiplet due to a 31-stage RO, evaluated across four different switching
activities (denoted by α) of the IP.

untrusted interposer. Existing work considers the interposer to
be the hardware RoT, assuming it to be fabricated in a trusted
environment. However, we consider the most conservative
threat model, which includes the design and fabrication of
both chiplets and the interposer in untrusted environments,
thereby making it easy for attackers to place such RO-based
modifications within the design.
The ROs inserted in the design can impact the voltage droop
dynamically. As an illustration, we evaluate the impact of a
31-stage RO on the worst-case voltage droop when the RO is
inserted in a single chiplet implementing the FIR filter IP from
the common evaluation platform (CEP) benchmark suite [33]
as illustrated in Fig. 4. We insert the RO at the center of the
FIR chiplet and evaluate the change in the worst-case voltage
droop across four different locations in the FIR chiplet through
static power analysis. In static power analysis, we vary the
switching activity, also known as the activity factor (α), of the
inputs and sequential elements in the design. This evaluation
is done for different values of activity factor and meant to
simulate a variety of loading conditions on the IP. Higher
the value of α, greater is the switching activity of the IP.
The input and sequential activity factors are together varied
from 0.3 and 0.7. The four locations are picked from the
standard cells located at the center of the four quadrants of the
FIR chiplet, when it is partitioned in equal halves vertically
and horizontally across the center. Details of the evaluation
methodology are presented in the next section.
RO Sensitivity: Note that the voltage droop value can vary
for the same location depending on the dynamic loading
conditions imposed on the system due to change in inputs
over time. Thus, it is important to analyze variations in the
voltage droop across a variety of system specific switching

284

IEEE TRANSACTIONS ON COMPUTER-AIDED DESIGN OF INTEGRATED CIRCUITS AND SYSTEMS, VOL. 44, NO. 1, JANUARY 2025

activity. This implies that at any given time, the functional
state of the IP determines the sensitivity of the voltage droop.
Similarly, for a given state of the IP, different locations in the
IP are susceptible to different values of voltage droop. Thus,
Vdroop is a function of the input state of the system as well as
the location. Thus, the presilicon evaluation of the worst-case
voltage droop can help in evaluating likely regions or hotspots
most susceptible to timing failure.
IV. VOLTAGE D ROOP -BASED PDN A NALYSIS
In this section, we describe how existing RTL-to-GDSII
flows (using standard industry EDA tools, such as Synopsys
design compiler and Cadence Innovus) can be utilized to
perform timing-aware voltage droop analysis. The overall
methodology that we have developed can perform design,
layout, and post-layout voltage droop and timing analysis for
chiplet IPs that could be later integrated in 2.5-D/3-D systems.

Fig. 5.

PDN insertion flow using Cadence Innovus.

is closest to its maximum possible operational frequency,
called fmax . Static power analysis only requires specifying
the switching activity for both inputs and sequential cells,
respectively, ranging between 0.1 and 0.9. Dynamic analysis
needs a functional workload that is specified within the Verilog
testbench customized for an individual chiplet based on its
functional specifications.
C. Case Study—FIR Filter Chiplet

A. Tool Specific Layout Details
The system-level RTL is synthesized using Synopsys DC.
We rely on the ASAP 7-nm standard cell library for our
RTL-to-GDSII flow. The different chiplet IPs can be either
black-boxed COTS IPs or designed in house. The chiplets
are then passed through the floorplanning stage followed by
micro-bump assignment, place, and route; all done using
Cadence Innovus. All designs are based on the ASAP 7-nm
PDK. The μ-bump pitch considered is 20 μm. The bottom six
metal layers of the ASAP back-end-of-line (BEOL) stack are
used for intrachiplet routing to create hard chiplet macros. The
μ-bump arrays for the chiplets are placed on metal-7 (M7) as
pin constraints for interposer routing.
B. Chiplet PDN Design and Voltage Droop Analysis
PDN Architecture: Chiplet PDN is implemented through the
insertion of VDD and VSS stripes. Sets of VDD and VSS lines are
placed in an alternating fashion with a fixed spacing between
the two. The power stripes are inserted in metal layers M5 and
M6. The set-to-set distance between each set of alternating
VDD and VSS lines is also predefined as 5 μm for both M6
and M7. Stripes along M6 run in the X-direction while stripes
along M5 run in the Y-direction. VDD and VSS rings enclose
each chiplet.
Fig. 5 illustrates the PDN insertion flow using Cadence
Innovus. Power rings can also be inserted in such designs.
Following PDN insertion, the chiplet level routing is performed that generates the final outputs.
Once the PDN insertion is completed and the final GDSII
files are generated, the voltage droop analysis workflow can be
invoked through Cadence Voltus, which supports both static
and dynamic power analysis. Our flow supports voltage droop
evaluation through static power analysis (vector-less) using
activity factors (α) that specify switching activity of sequential
cells and inputs, that can range between 0.1 and 0.9. Our flow
also supports voltage droop evaluation through dynamic power
analysis (vector-based) using value change dump (VCD)
files that are generated from functional Verilog testbenches
for the chiplet designs being evaluated. The chiplet is first
designed to operate on a particular clock frequency which

We utilize the above tool flow to evaluate the voltage droop
for the FIR chiplet through static analysis. The FIR chiplet
consists of a 32-bit digital FIR filter that has been obtained
from the CEP benchmark suite [33]. We use the ASAP 7-nm
library for the flow. Note that ASAP7 is a predictive PDK and
implemented designs may contain DRC errors specific to the
libraries used. A list of such DRC errors and justification for
their waivers is provided in [34]. This has no impact on voltage
droop analysis.. The chiplet aspect ratio is set at 0.7 which is
very close to 1. This allows for a more uniform distribution of
microbumps, which are responsible for connecting the input
and output pins of the chiplet to the interposer, across the
entire area of the chiplet. Power stripes are also added along
both horizontal and vertical directions. A single pair of power
pins are inserted at the center of the design, for VDD and
VSS , respectively. No routing constraints are placed other than
microbump insertion at M7.
When Voltus is executed, the chiplet-level voltage droop is
evaluated for a full range of input activity factors. Fig. 6 shows
the step-by-step breakdown of the entire flow for chipletlevel voltage droop evaluation with respect to the FIR chiplet
design. Chiplet-level voltage droop values are evaluated for
four different input activity factors: (0.3, 0.4, 0.5, 0.6, and 0.7).
Note that blue indicates the lowest-voltage droop while red
indicates region of maximum voltage droop. We observe that
as the distance from the power pins (blue regions at the center
of the chip) increases, the voltage droop values also increase.
The worst-case voltage droop across the chip is in the range
of 9 mV to 60 mV.
V. S ECURITY A NALYSIS —E VALUATING VOLTAGE
D ROOP -I NDUCED T IMING FAILURE
In this section, we present the overall security verification
methodology for ranking functional timing paths in the design
based on their susceptibility to the worst-case PDN voltage
droop through dynamic power analysis. We evaluate the
derating factor for each timing-critical path with ROs inserted
in the chiplets and present an approach to rank functional
timing paths based on the voltage droop impact. Since voltage
drooping in chiplet PDNs is a dynamic phenomenon that

TALUKDAR et al.: DETECTION OF VOLTAGE DROOP-INDUCED TIMING FAULT ATTACKS

285

Fig. 6. Illustration of the end-to-end design and voltage droop evaluation toolflow, including the chiplet floorplan output, PDN placement output, chiplet
layout output, and voltage droop output across four activity factors for the FIR chiplet.

changes with time depending on the type of workload running
on the IP, it is important to perform timing deration analysis
of chiplet logic paths while simulating functionally accurate
workloads. These functional workloads must be determined
based on the chiplet’s functional specifications. Therefore, we
ensure that the workloads used for timing deration studies
using vector-based voltage droop analysis are characterized
to represent the functional use-case of the IP and match the
type of input vectors the IP will experience during functional
operation in-field.
A. Timing Deration Due to Voltage Droop
Let P denote the set of all timing paths in a chiplet. Let
us consider the ith path, pi ∈ P, such that its nominal path
delay is given by tnom,i . For a given workload W running on
the chiplet with an average activity factor of α, the worstcase voltage droop for all standard cells in the path pi will
change the total path delay to tW ,i such that tW ,i = tnom,i +
tdroop,W , where tdroop,W is the Vdroop induced timing deration
factor added to the overall delay. Using this approach, we
evaluate the timing deration metric for the different paths
in the design. Depending on its size and the process node
used for fabrication, a chiplet can have a large number of
timing paths [35]. For example, design supported by Intel’s
Foveros 3-D packaging technology may contain hundreds
of thousands of paths [36], [37]. As a result, depending
on design complexity, security engineers can restrict this
evaluation to the N most critical timing paths in the design.
Furthermore, functionally critical paths that may not be timing
critical but require security coverage (e.g., paths responsible
for FSM control logic, paths in fan-out cones of primary
outputs [38], [39]), can also be added to this analysis. For
every standard cell instance in the path, we obtain the worstcase voltage droop experienced by that instance upon the
activation of the RO-based Trojan. This worst-case voltage
droop value is obtained through dynamic vector-based analysis
while running a functionally characterized workload on the
IP. In our analysis, without loss of generality the value of
N is set to 100. As the voltage droop data used to evaluate
timing degradation is obtained from workload-based postlayout simulation, an accurate estimate of the timing derating
factor tdroop,ω can be obtained.
The selection of timing paths to be included for timing
deration in P can be carried out by the designers based

on their security requirements. The total time incurred in
calculating path derating factors is directly proportional to the
number of instances in each path and the total number of paths
in the design. Thus, the total time for calculating the path
derating factors is directly proportional to the total number
of instances in all the paths in P. Thus, the designers can
limit the total number of paths in P based on the following
factors.
1) Slack Threshold: The minimum value of slack that is
deemed necessary for all the paths in the design. This
is determined based on the system requirements and
operating clock frequency. All paths with slacks lower
than the threshold are subject to timing deration analysis.
2) Functional Criticality: Certain paths in the design might
be functionally critical and are subject to timing deration
analysis [40].
3) Voltage Droop Distribution: The distribution of the
worst-case voltage droop for the chiplet design can
be obtained using the methodology presented in this
article. Designers can then identify instances in the
layout that experience worst-case voltage droop above a
given threshold (say 10% of nominal voltage droop), and
paths containing those instances, for timing deration.
B. Security Analysis Methodology
We propose a presilicon security analysis framework/methodology that can generate a ranked list of paths that
are most susceptible to timing failure due to voltage droop
in the PDN induced through malicious modifications. The
security analysis consists of the following steps.
1) Generating the layout of the 2-D chiplet IP including
PDN.
2) Extracting the timing report of all the critical paths
through Cadence Tempus.
3) Running Trojan-free voltage droop simulation to identify
the distribution of worst-case voltage droop.
4) Inserting RO blocks within the design and extracting
worst-case voltage droop for different workloads (static
or dynamic). Note that for dynamic analysis, a workload
consists of the application of functionally correct inputs
to the chiplet IP based on its system specifications
through a Verilog testbench.
5) Evaluating timing deration due to worst-case voltage
droop for the timing (and security) critical paths.

286

IEEE TRANSACTIONS ON COMPUTER-AIDED DESIGN OF INTEGRATED CIRCUITS AND SYSTEMS, VOL. 44, NO. 1, JANUARY 2025

Fig. 8. Gaussian distribution of the sample space of all functional input
patterns associated with the FIR filter.

Fig. 7. Methodology for ranking timing-critical paths due to voltage droop
through dynamic power analysis.

Parasitic extraction is done on the post-layout netlists using
Cadence Innovus, following which Cadence Tempus is used
to perform timing analysis. The overall security analysis
methodology is illustrated in Fig. 7. We begin with chiplet
designs, such as FIR, IIR, or 3DES IPs from the CEP
benchmark suite. The chiplets for each of these IPs are
designed through Cadence Innovus using the ASAP 7-nm
PDK. The gate-level netlists are generated using Synopsys
Design Compiler. Following chiplet design, the post-layout
parasitics are extracted for running timing analysis using
Cadence Tempus, which provides a detailed timing report. ROs
are then inserted in the layout and Cadence Voltus is used to
obtain the worst-case voltage droop for all the instances in
the design using both static (vector-less) and dynamic (vectorbased) power analysis. For dynamic power analysis, Synopsys
VCS is used to generate the chiplet’s VCD file, which is
based on its functional Verilog testbench. The VCD file along
with the chiplet layout is then used by Voltus to evaluate
workload specific voltage droop. Using the voltage droop data,
all the timing paths reported through Cadence Tempus are
re-evaluated, taking into account the timing derating factor
computed from the instance-level voltage droop data. This
analysis allows us to analyze the timing degradation due to
RO-induced voltage droop for the selected paths in the design.
C. Workload Characterization for Vector-Based Voltage
Droop Analysis
As described earlier, it is essential to match the vectorbased inputs (used during dynamic voltage droop analysis) as
closely as possible to the type of inputs experienced by the
IP during functional operation. As a result, the workload for
an IP X, represented as WX , is characterized by a sequence
of l input patterns, such that WX = [I1 , I2 , . . . , Il ]. Here, Ij
corresponds to the jth input pattern/vector in the workload or
sequence WX . Since every sample Ij in the workload WX is
applied consecutively, WX can also be considered to be time
series data. The size or width of the input pattern/vector Ij
is determined by the size of the primary inputs associated
with the IP X. Note that clock and reset signals are not

considered to be a part of Ij as they are global signals for
any IP. Furthermore, the length of the time series workload
or input sequence, l, can be set depending on the number of
input samples required for time series data analysis. For our
experiments, l = 1000, i.e., every workload consists of a series
of 1000 samples. Dynamic voltage droop analysis can now be
run any window of consecutive input samples in WX to obtain
the worst-case voltage droop value due to switching activity
caused by inputs in that window. The window size, , can vary
from 2 (worst-case voltage droop between two consecutive
inputs patterns) to l (worst-case voltage droop across all input
patterns in WX ). Note that time series voltage droop values can
be obtained for an IP X, running a workload WX , by setting
 = 2. This is given by VX = [V1−2 , V2−3 , V3−4 , . . . , Vl−1−l ],
where V1−2 is the worst-case voltage droop value between
I1 and I2 . Time series voltage droop data, VX , will be used
for runtime anomaly detection described later in Section VI.
For timing deration analysis, we utilize the worst-case voltage
droop across the entire workload. Therefore,  = l for timing
deration analysis. This voltage droop data can be obtained for
every cell instance in a chiplet logic path.
To ensure that the workload used for dynamic Vdroop analysis is as close to functional in-field specification for the IP,
we further characterize WX into two modes of operation, busy
mode (WX,busy ) and bursty mode (WX,bursty ). In busy mode,
the IP receives input transactions (input patterns) consecutively
with no idle time in between. Every input, Ij in WX,busy ,is
sampled from a Gaussian distribution of all possible input
samples. In bursty mode, the inputs patterns sampled from
the same Gaussian distribution are interspersed with periods
of low-switching activity (α = 0.1). As a result, depending
on the burst factor, β ∈ [0, 1], the workload WX,bursty
can have a fraction of inputs (given by β) sampled from a
Gaussian distribution with the other inputs having α of 0.1.
Fig. 8 illustrates the distribution of functional input patterns
associated with the FIR filter, which is part of the CEP
benchmark suite. Note that X-axis represents the decimal value
associated with the 32-bit input vector for the FIR filter.
D. Results and Evaluation
1) Benchmark Setup: We illustrate this methodology on
chiplet designs obtained from the CEP and OpenCores benchmark suites. We utilize the chiplet design flow presented in
Section IV to design five different chiplets, namely, the FIR

TALUKDAR et al.: DETECTION OF VOLTAGE DROOP-INDUCED TIMING FAULT ATTACKS

filter, IIR filter, 3DES, MD5, and JPEG encoding chiplet IPs.
All chiplet designs being analyzed range from small to large
sized IPs with the JPEG encoder being the largest design with
an area of 1, 546, 240 μm2 , the MD5 benchmark having an
area of 217, 800 μm2 , the FIR filter having an area of 5318
μm2 , the IIR filter having an area of 8812 μm2 , and the
3DES IP being the smallest at about 3272 μm2 . Table I shows
the relative size of every chiplet in terms of the number of
standard cells, pin count, X and Y dimensions, and total area.
We clarify that for voltage droop analysis, the active chiplet
area is enclosed by power and ground rings with multiple PG
pins placed along the periphery of the ring.
2) Evaluation Approach: The chiplets are designed to run
functional workloads (for dynamic power analysis) that are
obtained from the Verilog unit simulation testbench supplied
with the CEP and OpenCores benchmark suites for IP validation. The Verilog testbench exercises the IP’s functional inputs
based on the IP specifications. The workloads are designed
based on the approach outlined in Section V-C. Two workloads
are run, WX,busy and WX,bursty . Note that all the designs are run
at their corresponding fmax frequencies. Based on the sampling
of the workloads, the stimulus files for the testbenches are
generated in Verilog. The DSP chiplets (FIR and IIR filters)
accept input data packets to perform FIR and IIR-based cross
correlation operations while the 3DES chiplet computes the
ciphertext, respectively, for a set of plaintext input patterns.
RO-based Trojans are also inserted with their enable pins
connected to the system-level reset pin such that the ROs are
triggered whenever the reset pin is deasserted, ensuring that
the Trojans are activated as soon as the design is brought out
of the reset state. As the voltage droop in the PDN fluctuates
with the functional workload, we collect the worst-case voltage
droop data through Voltus for both workloads. The voltage
droop data obtained through power PDN rail simulations is
then used to calculate the derating factors for the N-worsttiming paths in the design (N being 100 for this analysis).
3) Experimental Results: We evaluate the average timing
degradation for the 100 worst-timing paths, due to different
numbers of ROs inserted in the 2.5-D chiplet design. We also
evaluate the number of paths that lead to a timing violation
due to the ROs inserted in the chiplets. All experiments were
conducted on an Intel Xeon Gold CPU running at 2.1 GHz.
For the largest benchmark, the average CPU runtime for voltage droop analysis using Cadence Voltus was approximately
four minutes. Similarly, timing analysis using Cadence Tempus
took less than two minutes. Table II shows the percentage
degradation in timing for the 100 worst paths, i.e., paths with
least amount of slack, in the different chiplet designs due to
the insertion and activation of different number of RO units.
We report both the average degradation in the 100 worst-paths,
μN,worst and also the standard deviation in the percentage
degradation across the 100 worst-paths, σN,worst . The timing
impact increases with the number of RO units inserted. This
is because increasing the number of ROs in the design also
increases the amount of voltage droop in the design.
Table II also presents the number of paths with timing
violation as a result of RO activation. We also analyze the
impact of the ROs on the worst-affected paths in the design.

287

TABLE I
C HIPLET S IZES FOR CEP AND O PEN C ORES E VALUATION B ENCHMARKS
I MPLEMENTED U SING ASAP7 PDK

We observe that for certain paths in the design, the timing
impact is much more significant, sometimes even leading
to timing failure. This is because although a path is not
originally timing critical, part of its logic passes through
the region experiencing the worst-case voltage droop in the
chiplet. As a result, running this analysis for the selected
paths in the design provides designers with insights into
potential regions on the chip that may be susceptible to timing
failures. This is made possible by combining both voltage
droop information obtained from the 2.5-D layout along with
accurate timing reports obtained using parasitic files extracted
post-layout.
E. PDN Voltage Droop Sensitivity for Variable Trojan Counts
In this section, we evaluate the sensitivity of PDN voltage
droop on the number of Trojans inserted in every chiplet.
We vary the number of RO-based Trojans embedded in every
chiplet and analyze the percentage change in voltage droop
as a function of Trojan count. We also evaluate the average
percentage degradation in the N worst-timing paths due to
Trojan insertion for every benchmark. This evaluation is done
on a mixed workload, WX,mix , which consists of equal number
of samples taken both WX,busy and WX,bursty and interspersed
uniformly to represent a general functional use case for every
chiplet IP. This ensures that a realistic workload setting is
maintained for the evaluation of voltage droop-induced timing
degradation for every IP. Fig. 9 (Top) shows the increasing
trend in PDN voltage droop as the number of embedded
Trojans is increased from one to thirty. The bottom figure
shows a corresponding increasing trend in the percentage
degradation of the N worst-timing paths (N = 100) due
to Trojan-induced change in Vdroop . Note that inserting a
single RO-based Trojan introduces an average degradation
of 0.5%–0.8% in critical timing paths across the chiplets
being evaluated. Increasing the Trojan count to three and five
increases the percentage degradation to approximately 1.5%.
We start observing timing path violations in IIR and FIR IPs
at the insertion of five Trojans with three and six violations,
respectively. Two and seven violations are observed in 3DES
and MD5 chiplets at the insertion of seven Trojans with none
before.
Susceptibility of Designs to RO-Based Trojan Insertion:
From the discussion above, it is evident that as little as
five RO-based Trojans when triggered in sync can cause
timing failure in certain chiplets. These RO-induced timing
failures can also be exacerbated for designs with narrow
timing margins, making such designs more sensitive to even

288

IEEE TRANSACTIONS ON COMPUTER-AIDED DESIGN OF INTEGRATED CIRCUITS AND SYSTEMS, VOL. 44, NO. 1, JANUARY 2025

TABLE II
P ERCENTAGE D EGRADATION IN N-W ORST-T IMING PATHS D UE TO T ROJAN -I NDUCED VOLTAGE D ROOP T IMING D EGRADATION I S E VALUATED
FOR WX,busy AND WX,bursty W HILE RUNNING AT fmax , W ITH N = 100

VI. D ETECTING VOLTAGE D ROOP ATTACKS USING
T IME -S ERIES A NOMALY D ETECTION
In the previous section, we demonstrated the effectiveness of RO-induced voltage droop in causing timing
degradation for critical paths in chiplets. In this section,
we present an ML-guided method to detect such voltage
droop attacks in time series data using convolutional autoencoders [41]. We also highlight our approach to minimize
false positives while demonstrating the effectiveness of convolutional autoencoders for time series attack detection in
voltage droop data across several benchmarks from the CEP
suite.

A. Time Series Anomaly Detection Using Autoencoders

Fig. 9.
(Top) Percentage change in Vdroop and (bottom) percentage
degradation in 100 worst-timing paths, as a function of increasing number of
Trojans in the design.

a small number of Trojan embeddings. Recent work has
shown that there exist several pathways for attackers to insert
malicious modifications in the design through the use of ECOs,
layout level modifications, and trust-gaps within the supply
chain [25], [26], [27]. Furthermore, ROs are widely used in
silicon for a variety of applications, such as process characterization, aging monitoring, and Silicon lifecycle management
[29], [30], [31]. Due to the prevalence of on-chip ROs, it is
easier for attackers in an untrusted supply chain to reconfigure
a certain subset of nets and derive a trigger signal from an
internal net in the design, making the process of malicious
modification for RO-based Trojans easier.

Autoencoders are neural networks that learn to reconstruct
the supplied input sample, thereby producing a mapping
between the reconstructed input sample and itself [41]. This is
achieved by downsampling an input feature vector, x through
an encoder architecture, Eθ to generate a latent space vector,
z. This is then upsampled through a decoder architecture, Dφ
to regenerate a feature vector, x which is the same size as the
input vector, x. The autoencoder can then be trained to minimize the reconstruction loss for an input sample, x
i , such that
minφ,θ {L(φ, θ ; xi )}, where L(φ, θ ; xi ) = (1/N) N
i=1 ||xi −
Dφ (Eθ (xi ))||22 . Here, || · || is used as the L2 norm, N is the
number of samples used for training. Autoencoders can learn
the distribution of a set of samples on which they are trained.
As a result, if a sample x, supplied to the trained autoencoder
belongs to the same distribution, the value of L(φ, θ ; x) will be
very low for that sample. Therefore, an autoencoder can also
be used identify anomalous data as the value of L(φ, θ ; x) for
such samples will be very high. After training an autoencoder
to in-distribution data, a reconstruction loss threshold, can be
identified. If L(φ, θ ; x) < , the incoming sample is classified
as nonanomalous. However, if L(φ, θ ; x) > , the sample is
classified as anomalous.

TALUKDAR et al.: DETECTION OF VOLTAGE DROOP-INDUCED TIMING FAULT ATTACKS

289

Fig. 10. Training and evaluation methodology for detecting anomalies in time series voltage droop data, including the sampling window for time series data
and the architecture of the convolutional autoencoder.

Consider a time series sequence of l data samples given by
= [γ1 , γ2 , . . . , γl ]. We can train autoencoders on time series
data by batching the continuous sequence of input samples
into groups based on a sliding window whose size is given
by δ. Assuming that this moving window has a stride of s,
the number of training samples is then given by [(l − δ)/s].
The size of the input and output layers of the autoencoder is
determined by the window size, δ.
B. Methodology for Detecting Voltage Droop Attacks
We develop a time series anomaly detection framework to
detect voltage droop attacks in chiplet PDNs using convolutional autoencoders. The voltage droop values are sampled
from standard cells that are part of timing critical paths in the
chiplet design. The time series voltage droop data, VX , consists
of 500 samples with the sampling window size, δ = 16, and
stride, s = 1. As a result, the size of the autoencoder’s input
and output layers is 16 × 1. The autoencoder consists of three
intermediate layers with filter sizes 7 × 1 × 32, 7 × 1 × 16,
and 7 × 1 × 32, respectively. Note that the padding after each
layer is adjusted such that the X − Y size of the intermediate
feature maps remains the same at 7 × 1. However, the feature
depth is changed after every layer. The first intermediate
layer upsamples the feature depth to 16 × 32. The second
intermediate layer downsamples the feature vector to a latent
space of size 16×16. This is then upsampled again by the third
intermediate layer to create a feature map of size 16 × 32. The
final filter is responsible to shrink the output feature map to
match the depth of the input feature at 16×1. Fig. 10 illustrates
the overall architecture of the convolutional autoencoder.
As described in Section V-C, time series voltage droop
data for an IP is collected, with and without the activation
of Trojans. The autoencoder is trained on nonanomalous
voltage droop data, also known as in-distribution voltage
droop data. Let the set UX,trian contain the reconstruction loss of the voltage droop samples in the training
dataset for the IP X, VX,train . Therefore, UX,train =
[L(φ, θ ; V1 ), L(φ, θ ; V2 ), . . . , L(φ, θ ; VN )], where N is the
number of samples in the training dataset. The loss threshold

is set to the reconstruction loss of the sample with the maximum value in the set UX,train . Therefore, = max{UX,train }.
This ensures that a time-series window during evaluation is
flagged as anomalous only if the reconstruction loss for that
sample is higher than the maximum loss obtained on the
training samples. Furthermore, to reduce the number of false
positives, a history-based approach is also utilized, where a
voltage droop sample associated with the ith window, Vi , is
not considered anomalous until L(φ, θ ; Vi ) > and the loss
of at least eight previous sample windows was also greater
than , i.e., L(φ, θ ; Vi−j ) > ∀ j : (1 ≤ j ≤ 8), where j
iterates through the previous eight samples leading up to the
ith sample.
C. Results and Evaluation
We evaluate the effectiveness of the proposed autoencoder
architecture on time series voltage droop data collected across
different chiplet IPs from the CEP benchmark suite. Time
series data is collected for the FIR, IIR, 3DES, and MD5
chiplet IPs across two different functional workload types,
WX,busy and WX,bursty . The autoencoder is trained on indistribution data, i.e., data with Trojans not activated. For every
IP, two anomaly detection models are trained, one each for the
type of workload running on the IP. The training sets of voltage
droop data, i.e, VX,busy and VX,bursty , contain a sequence of
500 Vdroop samples. The models are trained for 150 epochs
with a learning rate of 0.001. Training on average takes less
than 4 min for all the benchmarks. Training is done on an
Intel Xeon Gold CPU running at 2.1 GHz. The trained models
are then evaluated on a test set containing time series voltage
droop data associated with the corresponding workloads with
different number of Trojans activated. For both busy and bursty
mode of workloads, four test sets are created for evaluation,
with 15, 20, 25, and 30 Trojans activated at a time in each
of the test set, respectively. The test set also consists of 500
voltage droop samples, with Trojans activated for 25% of the
time and triggered randomly in the sequence.
The effectiveness of the convolutional autoencoder in
detecting voltage droop anomalies stems from its ability to

290

IEEE TRANSACTIONS ON COMPUTER-AIDED DESIGN OF INTEGRATED CIRCUITS AND SYSTEMS, VOL. 44, NO. 1, JANUARY 2025

Fig. 11. Training (left) and testing (right) loss histograms for the 3DES and
FIR chiplet IPs. Note that the loss threshold derived from the training loss
histogram can be used to form a clear separation between anomalous data (in
red) and nonanomalous data samples in the testing loss histograms.

Fig. 12. Voltage droop anomalies detected by the convolutional autoencoder
model in time series data.

TABLE III
P ERFORMANCE OF C ONVOLUTIONAL AUTOENCODER M ODELS T RAINED
ON B USY AND B URSTY M ODE W ORKLOADS . T WO M ODELS A RE
T RAINED , O NE E ACH T YPE OF W ORKLOAD . T HESE A RE E VALUATED ON
T EST S ETS C ONTAINING D IFFERENT N UMBER OF ACTIVE T ROJANS

Fig. 13. Separation in the reconstruction loss distribution of anomalous and
nonanomalous samples for the IIR chiplet with a variety of RO-based Trojans
ranging from 3, 5, 7, and 15 ROs.

distinguish between the distribution of an anomalous voltage droop sample from a nonanomalous one. This can be
evaluated by distinguishing the reconstruction loss between a
nonanomalous Vdroop sample and an anomalous Vdroop sample
in the test set. To analyze this, we first plot the training loss
histogram associated with the data samples in the training
set. Fig. 11 shows the training loss histogram and the derived
reconstruction loss threshold for both the FIR and 3DES
chiplets running busy workloads. Note that the loss threshold,
FIR = 0.002. Similarly, 3DES = 0.0015. We observe that
these reconstruction loss thresholds, when superimposed on
the test loss histogram, are very effective in distinguishing
between anomalous data points and nonanomalous data points.
Observe that most of the outliers in case of both 3DES
and FIR chiplets have a loss value much greater than their
corresponding loss thresholds. This indicates that the convolutional autoencoder is effective in separating in-distribution
data samples (nonanomalous data on which training took
place) from out-of-distribution data samples (anomalous data
samples).

Table III shows the performance evaluation of the trained
anomaly detection models on different test sets. For every IP,
two models are trained, one each for the type of workload
running on the IP. Similarly, for every workload, there exist
four test sets that contain time series data with different
number of Trojans activated at a time. For each test set, the set
number of Trojans are randomly activated for 25% of the time.
From Table III, it is clear that the convolutional autoencoder
models achieve very high accuracy when evaluated on different
number of activated Trojans across both busy and bursty mode
workloads for all chiplet IPs. The false positives and test
escape values are also less than 2%, with no false positives
in some scenarios. Fig. 12 shows the voltage droop anomalies
detected by the convolutional autoencoder model for the 3DES
and FIR chiplets on the test set evaluating 15 active Trojans
on a busy workload.
D. Intuitive Explanation of Autoencoder’s Performance
The convolutional autoencoder is able to achieve good
anomaly detection performance in dynamic operational settings. This is due to the model’s ability to separate anomalous
and nonanomalous distributions so well in the latent space. As
a case study, we analyze the difference in the distribution of

TALUKDAR et al.: DETECTION OF VOLTAGE DROOP-INDUCED TIMING FAULT ATTACKS

291

TABLE IV
P ERFORMANCE OF THE C ONVOLUTIONAL AUTOENCODER M ODELS
T RAINED ON M IXED W ORKLOADS FOR A LL B ENCHMARK IP S
E VALUATED ON T EST S ETS C ONTAINING D IFFERENT N UMBER
OF RO- AND G LITCH -BASED T ROJANS

Fig. 14.

Glitch-based power wasting hardware Trojan.

reconstruction loss for anomalous and nonanomalous samples
for IIR chiplet with 15, 7, 5, and 3 active Trojans, respectively,
while running a mixed workload, WIIR,mix . As shown in
Fig. 13, we plot the mean of both the distributions (μbenign ,
μanomaly ) and observe a clear and significant separation
between the two points. We next observe that the anomalous
distribution is skewed significantly with μanomaly lying beyond
the 3σ point from μbenign , with less than 1% of anomalous
samples lying within 3σ of μbenign . Furthermore, we also
evaluate the kurtosis score for both the distributions, which is
the fourth standardized moment of a distribution and is given
by K(X) = E(([(X − μ)]/σ ))4 . A higher-kurtosis score is
indicative of a highly peaked distribution while a lower score is
indicative of a greater spread. For IIR IP, K(Xbenign,7 ) = 11.86
and (Xanomaly,7 ) = 1.62. Similarly, K(Xbenign,15 ) = 22.10
and (Xanomaly,15 ) = 2.87. These values also suggest that the
autoencoder can create highly peaked and narrow distributions
for nonanomalous samples (higher K(X)), thereby making
the detection of anomalous samples that are well separated
from these distributions easier (lower K(X)). A similar trend
is followed for lower Trojan counts with K(Xbenign,5 ) =
9.15, (Xanomaly,5 ) = 0.75, and K(Xbenign,3 ) = 7.05 and
(Xanomaly,15 ) = 0.43.
VII. D ISCUSSION
A. Time-Series Anomaly Detection on Non-RO Trojans
So far, we have analyzed the effectiveness of ROs in causing
PDN voltage droop events leading to timing failure. ROs
offer several advantages, including 1) high-switching activity;
2) ease of insertion and masking among large number of other
ROs that are part of the design; and 3) relatively simply design.
To investigate the effectiveness of the autoencoder-based time
series anomaly detection model against non-RO Trojans, we
implement a glitch-based power wasting Trojan as shown in
Fig. 14. This Trojan is a variant of a power hammering circuit
proposed in [42]. When the Trigger signal is enabled, a chain
of six inverters is used to generate multiple variable delay
glitches at the output of the XOR gate, which drives a power
wasting block comprising of a chain of 10 additional inverters
that propagate the glitch. The frequency of glitch generation
is N/2 times that of the input clock, where of N refers to
the number of inputs to the XOR gate. In our implementation,
N = 4, thereby producing two glitches every clock cycle.
As compared to RO-based Trojan, the glitch-based Trojan
generates almost twice the amount of switching activity and
has an area footprint comparable to the RO-based Trojan.
We compare the performance of our time series anomaly
detection model for both RO- and glitch-based Trojans. We

perform this analysis on IPs running on mixed workloads
(WX,mix ) as described in Section V-E. The convolutional
autoencoder’s Trojan detection performance is evaluated on
three different test sets that contain both anomalous and
nonanomalous time series data. From the RO-induced Vdroop
susceptibility assessment done earlier in Section V-E, we recall
that some chiplets start exhibiting timing violations around
the activation of five or more Trojans. Thus, to perform a
practical assessment of the autoencoder performance on both
Trojan designs, we activate three, five, and seven Trojans
randomly over 25% of the time the three evaluation test sets,
respectively. Table IV summarizes the convolutional autoencoder’s performance across both Trojan types. We observe that
the model performs significantly well in case of both Trojan
types, achieving close to 90% anomaly detection accuracy in
case of both five and seven Trojan insertions. Furthermore,
we also observe that the model’s test escape is significantly
low even for three and five Trojan insertions. The highfalse positive rate for three Trojans can be explained due
to the increasing overlap of the tail distributions of both
nonanomalous and anomalous distributions, which can also
be seen in Fig. 13. It is important to note that as the Trojan
count decreases, there is greater overlap in tail distributions
of both anomalous and nonanomalous samples, with μanomaly
shifting closer to the 3σ threshold of the nonanomalous
distribution. This close proximity of an anomalous sample to
a benign sample is also indicative of a lesser likelihood of
timing path violation occurring for such scenarios. In fact,
the convolutional autoencoder is effective at catching voltage
droop anomalies that have a greater likelihood of causing
timing violations due to their increased separation from the 3σ
corner of the nonanomalous distribution, which is also why
the model’s test escape is low.
B. Mitigating PDN Voltage Droop Attacks
As discussed in Sections II and III, the nature of the threat
model for HI assumes the use of untrusted COTS IP, which
can lead to untrusted chiplets being integrated in the system.
As RO-based Trojans are significantly small in size, they

292

IEEE TRANSACTIONS ON COMPUTER-AIDED DESIGN OF INTEGRATED CIRCUITS AND SYSTEMS, VOL. 44, NO. 1, JANUARY 2025

can be easily incorporated into chiplets being fabricated and
tested across third-party locations. Furthermore, due to their
size and independence from control FSMs, such malicious
modifications can easily sneak past existing security mechanisms that rely on mere visual inspection. Furthermore, even
formal security verification techniques, such as logic equivalence checking, cannot guarantee security against Trojans
that impact functional behavior through power-based side
channels [43]. This necessitates the need for nonobtrusive
design-level safe guards that can ensure the security of the
overall HI system during runtime, especially against powerbased side channel attacks. As voltage droop across a power
rail is directly affected by the ability of that rail to supply
power to its load, the higher the driving capacity of the rail,
the lower is the voltage droop. We propose the use of power
and ground pins (PG pins) to mitigate the impact of voltage
droop-based attacks. The voltage droop distribution across a
chiplet is determined by the dynamic loading conditions on
the power and ground rails for the different instances (and/or
regions) within the chiplet. The closer an instance is to a PG
pin, the lower is the voltage droop experienced by that instance
(and/or region) under dynamic loading conditions.
In order to prevent voltage droop-based PDN side-channel
attacks, PG pins can thus be systematically inserted in locations that are: 1) experiencing high-voltage droop, also known
as voltage droop hotspots and 2) susceptible to timing failure
due to significantly low slack, i.e., have lower tolerance for
voltage droop events. Inserting PG pins systematically across
a chiplet not only reduces the susceptibility of specific paths
to voltage droop-induced timing failure, but also reduces the
worst-case value of voltage droop throughout the entire chiplet
itself. Fig. 15 shows the worst-case voltage droop distribution
for the FIR chiplet for a variety of PG pin configurations. Note
that the worst-case voltage droop is maximum in Fig. 15(a),
which has only one PG pin. Meanwhile, the worst-case voltage
droop distribution is much less and more evenly spread out
for the case with seven PG pins as shown in Fig. 15(d).
The methodology for inserting PG pins across chiplets can
enhance security against voltage droop-based PDN timing fault
attacks. This is because there are two limiting factors that
max : The maximum limit of the
affect timing degradation. Vdroop
min : The minimum slack threshold
worst-case voltage droop. tslack
that must be required to meet timing requirements.
Given the list of paths P that must meet the timing
min and the worst-case value V max that needs to
requirement tslack
droop
be tolerated, we can compute the worst-case timing derating
factors for the paths in P. Based on this computation, we
obtain a new list Pderated , which contains a list of paths out
of which some may now have become susceptible to timing
path
min ). We can now identify the instances
failure (if tslack < tslack
belonging to these susceptible paths within the chiplet layout,
and insert PG pins to power and ground rails belonging to
those instances to prevent the adverse impact of voltage droop.
This method provides designers the ability to guarantee timing
security against voltage droop-based attacks given the worstcase voltage and timing thresholds. The impact of Trojans
inserted in the active interposer and shared PDNs across

Fig. 15. Worst-case voltage droop across the FIR chiplet for different location
and number of PG pins inserted in the PDN (blue-minimum at 0 V, redmaximum at 90 mV). (a) One PG pin at center; (b) three PG pins with one
inserted at center and two in top half; (c) five PG pins across four corners
and one in center; and (d) seven PG pins inserted with three across both left
and right halves, and one in center.

multiple chiplets in HI systems can also be explored as part
of future work.
VIII. C ONCLUSION
We have presented the shortcomings associated with existing security solutions targeted toward runtime IP security and
developed a methodology for the design, synthesis, layout, and
simulation of voltage droop events for chiplet IPs. We have
described a method to analyze the susceptibility of chiplet IPs
toward voltage droop-based PDN timing attacks, resulting in
timing failure during functional runtime. We have developed
a convolutional autoencoder-based method that can detect
voltage droop anomalies in time series data, caused by RObased hardware Trojans in chiplet PDNs. This method achieves
very high accuracy with minimal amount of false positives and
test escape.
R EFERENCES
[1] J. Talukdar, S. Chen, A. Das, S. Aftabjahani, P. Song, and
K. Chakrabarty, “A BIST-based dynamic obfuscation scheme for
resilience against removal and oracle-guided attacks,” in Proc. IEEE Int.
Test Conf. (ITC), 2021, pp. 170–179.
[2] K. Xiao, D. Forte, Y. Jin, R. Karri, S. Bhunia, and M. Tehranipoor,
“Hardware trojans: Lessons learned after one decade of research,” ACM
Trans. Design Autom. Electron. Syst., vol. 22, no. 1, pp. 1–23, 2016.
[3] Technical Working Groups, “Heterogeneous integration roadmap:
Security,” in Proc. IEEE Electron. Packag. Soc., 2021, pp. 1–73.
[4] M. S. M. Khan et al., “Secure interposer-based heterogeneous integration,” IEEE Design Test, vol. 39, no. 6, pp. 156–164, Dec. 2022.
[5] J. Talukdar, A. Chaudhuri, J. Kim, S. K. Limt, and K. Chakrabarty,
“Securing heterogeneous 2.5-D ICs against IP Thef through dynamic
interposer obfuscation,” in Proc. IEEE DATE, 2023, pp. 1–2.
[6] J. Talukdar, A. Chaudhuri, and K. Chakrabarty, “TaintLock: Preventing
IP theft through lightweight dynamic scan encryption using taint bits,”
in Proc. IEEE Eur. Test Symp. (ETS), 2022, pp. 1–6.
[7] W. Chen and B. Bottoms, “Heterogeneous integration roadmap: Driving
force and enabling technology for systems of the future,” in Proc. IEEE
Symp. VLSI Technol., 2019, pp. T50–T51.
[8] M. Nabeel et al., “2.5-D root of trust: Secure system-level integration of untrusted chiplets,” IEEE Trans. Comput., vol. 69, no. 11,
pp. 1611–1625, Nov. 2020.
[9] H. Park et al., “Design flow for active interposer-based 2.5-D ICs and
study of RISC-V architecture with secure NoC,” IEEE Trans. Compon.,
Packag. Manuf. Technol., vol. 10, no. 12, pp. 2047–2060, Dec. 2020.
[10] F. Schellenberg et al., “Remote inter-chip power analysis side-channel
attacks at board-level,” in Proc. IEEE ICCAD, 2018, pp. 1–7.
[11] G. L. Ding, J. Chu, L. Yuan, and Q. Zhao, “Correlation electromagnetic
analysis for cryptographic device,” in Proc. IEEE Pacific–Asia Conf.
Circuits, Commun. Syst., 2009, pp. 388–391.
[12] X. Wang et al., “Role of power grid in side channel attack and powergrid-aware secure design,” in Proc. 50th Annu. Design Autom. Conf.,
2013, pp. 1–9.

TALUKDAR et al.: DETECTION OF VOLTAGE DROOP-INDUCED TIMING FAULT ATTACKS

[13] D. R. E. Gnad et al., “Voltage drop-based fault attacks on FPGAs using
valid bitstreams,” in Proc. 27th Intl. Conf. Field Programmable Logic
Appl. (FPL), 2017, pp. 1–7.
[14] A. Boutros, M. Hall, N. Papernot, and V. Betz, “Neighbors from
hell: Voltage attacks against deep learning accelerators on multi-tenant
FPGAs,” in Proc. Int. Conf. Field-Programmable Technol. (ICFPT),
2020, pp. 103–111.
[15] N. Gattu, M. N. I. Khan, A. De, and S. Ghosh, “Power side channel
attack analysis and detection,” in Proc. IEEE ICCAD, 2020, pp. 1–7.
[16] J. Krautter, D. R. E. Gnad, F. Schellenberg, A. Moradi, and
M. B. Tahoori, “Active fences against voltage-based side channels in
multi-tenant FPGAs,” in Proc. IEEE ICCAD, 2019, pp. 1–8.
[17] J. Krautter, D. R. E. Gnad, and M. B. Tahoori, “FPGAhammer: Remote
voltage fault attacks on shared FPGAs, suitable for DFA on AES,”
IACR Trans. Cryptograph. Hardw. Embedded Syst., vol. 2018, no. 3,
pp. 44–68, 2018.
[18] H. Nassar, P. Machauer, D. R. E. Gnad, L. Bauer, M. B. Tahoori, and
J. Henkel, “Covert-hammer: Coordinating power-hammering on multitenant FPGAs via covert channels,” in Proc. ACM FPGA, 2024, p. 43.
[19] K. Xiao, X. Zhang, and M. Tehranipoor, “A clock sweeping technique
for detecting hardware trojans impacting circuits delay,” IEEE Design
Test, vol. 30, no. 2, pp. 26–34, Apr. 2013.
[20] A. Vakil et al., “LASCA: Learning assisted side channel delay
analysis for hardware trojan detection,” in Proc. ISQED, 2020,
pp. 40–45.
[21] Y. Cao, C.-H. Chang, and S. Chen, “A cluster-based distributed active
current sensing circuit for hardware trojan detection,” IEEE Trans. Inf.
Forensics Security, vol. 9, pp. 2220–2231, 2014.
[22] A. Vakil, H. Homayoun, and A. Sasan, “IR-ATA: IR annotated timing
analysis, a flow for closing the loop between PDN design, IR analysis
& timing closure,” in Proc. IEEE ASPDAC, 2019, pp. 152–159.
[23] S. Beheshti-Shirazi et al., “A reinforced learning solution for clock
skew engineering to reduce peak current and IR drop,” in Proc. IEEE
GLSVLSI, 2021, pp. 181–187.
[24] Z. Zeng, L. Li, W. Zhou, J. Yang, and Y. He, “IR-drop calibration for
hardware trojan detection,” in Proc. IEEE ISCID, 2020, pp. 418–421.
[25] A. Hepp et al., “A pragmatic methodology for blind hardware trojan
insertion in finalized layouts,” in Proc. IEEE ICCAD, 2022, pp. 1–9.
[26] T. Perez, M. Imran, P. Vaz, and S. Pagliarini, “Side-channel trojan
insertion—A practical foundry-side attack via ECO,” in Proc. IEEE Int.
Symp. Circuits Syst. (ISCAS), 2021, pp. 1–5.
[27] M. S. U. I. Sami et al., “Advancing trustworthiness in systemin-package: A novel root-of-trust hardware security module for
heterogeneous integration,” IEEE Access, vol. 12, pp. 48081–48107,
2024.
[28] X. Wei, Y. Diao, and Y.-L. Wu, “To detect, locate, and mask hardware
trojans in digital circuits by reverse engineering and functional ECO,”
in Proc. 21st Asia South Pacific Design Autom. Conf. (ASP-DAC), 2016,
pp. 623–630.
[29] D. Sengupta and S. S. Sapatnekar, “Estimating circuit aging due to
BTI and HCI using ring-oscillator-based sensors,” IEEE Trans. Comput.Aided Design Integr. Circuits Syst., vol. 36, no. 10, pp. 1688–1701, Oct.
2017.
[30] M. Bhushan, A. Gattiker, M. B. Ketchen, and K. K. Das, “Ring
oscillators for CMOS process tuning and variability control,” IEEE
Trans. Semicond. Manuf., vol. 19, no. 1, pp. 10–18, Feb. 2006.
[31] T.-H. Kim et al., “Silicon odometer: An on-chip reliability monitor for
measuring frequency degradation of digital circuits,” IEEE J. Solid-State
Circuits, vol. 43, no. 4, pp. 874–880, Apr. 2008.
[32] S.-C. Hung et al., “Power supply noise-aware scan test pattern reshaping
for at-speed delay fault testing of monolithic 3-D ICs,” in Proc. IEEE
Asian Test Symp. (ATS), 2020, pp. 1–6.
[33] B. Tan et al., “Benchmarking at the frontier of hardware security:
Lessons from logic locking,” 2020, arXiv:2006.06806,
[34] “ASAP7 DRC violations and waiver justification.” 2024. [Online].
Available: https://shorturl.at/fLQ89
[35] M. Ahmad, J. DeLaCruz, and A. Ramamurthy, “Heterogeneous integration of chiplets: Cost and yield tradeoff analysis,” in Proc. IEEE
EuroSimE, 2022, pp. 1–9.
[36] S. R. Srinivasa et al., “Design methodology for scalable 2.5-D/3D heterogenous tiled chiplet systems,” in Proc. IEEE ISQED, 2022,
pp. 1–4.
[37] W. Gomes et al., “8.1 lakefield and mobility compute: A 3-D
stacked 10-nm and 22FFL hybrid processor system in 12×
12mm 2, 1mm package-on-package,” in Proc. IEEE ISSCC, 2020,
pp. 144–146.

293

[38] A. Chaudhuri, J. Talukdar, J. Jung, G.-J. Nam, and K. Chakrabarty,
“Fault-criticality assessment for AI accelerators using graph convolutional networks,” in Proc. IEEE DATE, 2021, pp. 1596–1599.
[39] A. Chaudhuri, C.-Y. Chen, J. Talukdar, S. Madala, A. K. Dubey, and
K. Chakrabarty, “Efficient fault-criticality analysis for AI accelerators
using a neural twin,” in Proc. IEEE Int. Test Conf. (ITC), 2021,
pp. 73–82.
[40] A. Chaudhuri, J. Talukdar, F. Su, and K. Chakrabarty, “Functional
criticality analysis of structural faults in AI accelerators,” IEEE
Trans. Comput.-Aided Design Integr. Circuits Syst., vol. 41, no. 12,
pp. 5657–5670, Dec. 2022.
[41] C. Zhou and R. C. Paffenroth, “Anomaly detection with robust deep
autoencoders,” in Proc. ACM SIGKDD, 2017, pp. 665–674.
[42] K. Matas et al., “Power-hammering through glitch amplification–attacks
and mitigation,” in Proc. IEEE FCCM, 2020, pp. 65–69.
[43] M. Eslami, J. Knechtel, O. Sinanoglu, R. Karri, and S. Pagliarini,
“Benchmarking advanced security closure of physical layouts: ISPD
2023 contest,” in Proc. Int. Symp. Phys. Design, 2023, pp. 256–264.

Jonti Talukdar received the B.Tech. degree in electronics and communication engineering from Nirma
University, Ahmedabad, India, in 2018, and the
M.S. and Ph.D. degrees in electrical and computer
engineering from Duke University, Durham, NC,
USA, in 2020 and 2024 respectively.
His Ph.D. thesis is on securing heterogeneously
integrated (HI) 2.5-D/3-D ICs against IP theft. He
has worked extensively on developing low-cost solutions for IP obfuscation, repurposing on-chip test
architecture for security, runtime memory and IP
security, and testing of AI accelerator hardware and mixed-signal circuits.
He has also spent time as a Research Intern with Intel, Santa Clara, CA,
USA; Synopsys, Sunnyvale, CA, USA; and NVIDIA, Santa Clara. He is
currently a Senior DFX Engineer with NVIDIA. His research interests lie at
the intersection of hardware security, test, and applied machine learning for
silicon security, health, and lifecycle management.

Akshay Vyas received the B.E. degree in electronics and communication engineering from Mumbai
University, Mumbai, India, in 2019, and the M.S.
degree in electrical engineering with Arizona State
University, Tempe, AZ, USA, in 2024.
His research interests lie in hardware security and
silicon lifecycle management.

Krishnendu Chakrabarty (Fellow, IEEE) received
the B.Tech. degree from the Indian Institute
of Technology, Kharagpur, Kharagpur, India, in
1990, and the M.S.E. and Ph.D. degrees from the
University of Michigan, Ann Arbor, MI, USA, in
1992 and 1995, respectively.
He is currently the Fulton Professor of
Microelectronics with the School of Electrical,
Computer and Energy Engineering, Arizona State
University (ASU), Tempe, AZ, USA. He is also
the Director of the ASU Center on Semiconductor
Microelectronics and the CTO of the Department of Defense Microelectronics
Commons Southwest Advanced Prototyping Hub. His current research
projects include design-for-testability of 2.5-D/3-D integrated circuits and
heterogeneous integration; hardware security; AI accelerators; microfluidic
biochips; and AI for healthcare.
Prof. Chakrabarty is a Fellow of ACM and AAAS, and a Golden Core
Member of the IEEE Computer Society.
PAPER_TEXT
