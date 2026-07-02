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
# [705] Honeypot-Driven Proactive Detection Network for Attacks in Smart Grids
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
编号：705
题名：Honeypot-Driven Proactive Detection Network for Attacks in Smart Grids
年份：2026
DOI：10.1109/tase.2026.3681594
来源：IEEE Transactions on Automation Science and Engineering
PDF：paper/10.1109_TASE.2026.3681594.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：恶意流量、暗网与攻击检测
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\705.txt
- 原始字符数：61060
- 本次发送字符数：61060
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

8415

Honeypot-Driven Proactive Detection Network
for Attacks in Smart Grids
Yi-Xuan Chen , Xi-Ming Sun , Senior Member, IEEE, Xue-Fang Wang , Member, IEEE, and Tianju Sui

Abstract—This paper proposes a honeypot-driven active detection framework to address the growing cyber threats targeting
smart grids. To address the limitations of existing detection
methods and the lack of proactive defense capabilities, the
framework integrates interpretable decision mechanisms with an
adaptive modular architecture, through the dynamic weighting
of the gated aggregation mechanism. It incorporates data preprocessing, honeypot interaction, dual-path detection, and decision
fusion to more effectively capture diverse attack behaviors and
strengthen overall detection reliability. The framework integrates
a GBDT-based anomaly scorer with a dedicated Denial-of-Service
(DoS) detector, and combines multidimensional evidence using
a gated aggregation mechanism. Moreover, theoretical analyses
establish a lower bound on feature distinguishability, prove model
convergence, and demonstrate effective false-alarm suppression,
providing formal guarantees for feasibility. Finally, experiments
on real-world smart grid datasets show that the proposed framework accurately detects DoS, replay, and integrity attacks while
maintaining strong overall performance. The results confirm its
effectiveness as a theoretically grounded and proactive defense
solution for smart grid security.
Note to Practitioners—Smart grids face unique cybersecurity
challenges. Attacks like data replay or network floods can
disrupt physical operations, leading to outages or equipment
damage. Traditional IT security tools often struggle here, as
they may only respond after the system has been attacked.
This work addresses this gap by integrating deceptive honeypot
nodes directly into the operational network architecture. These
honeypots act as intelligent sensors, attracting and engaging
attackers. The core innovation is a method to automatically
convert the observed attacker interactions into clear, actionable
signals. These signals are then fused with conventional traffic
analysis in a decision framework to reliably distinguish between
Replay attacks, Integrity tampering, Denial-of-Service attempts,
and normal operations. For security teams, this means more
precise alerts with contextual evidence, intercepting attacks
before any damage occurs.
Index Terms—Smart grid security, honeypot interaction, active
defense, attack detection.
Received 6 January 2026; revised 12 March 2026; accepted 2 April 2026.
Date of publication 7 April 2026; date of current version 24 April 2026.
This article was recommended for publication by Associate Editor M. Zhang
and Editor Q. Zhao upon evaluation of the reviewers’ comments. This
work was supported in part by the National Natural Science Foundation
(NNSF) of China under Grant 61890920 and Grant 08120003 and in part
by the Fundamental Research Funds for the Central Universities under Grant
DUT22RT(3)090. (Corresponding author: Xi-Ming Sun.)
Yi-Xuan Chen, Xi-Ming Sun, and Tianju Sui are with the School of
Control Science and Engineering, Dalian University of Technology, Dalian
116024, China (e-mail: chenyixuan@mail.dlut.edu.cn; sunxm@dlut.edu.cn;
suitj@dlut.edu.cn).
Xue-Fang Wang is with the School of Engineering, University of Leicester,
LE1 7RH Leicester, U.K. (e-mail: xw259@leicester.ac.uk).
Digital Object Identifier 10.1109/TASE.2026.3681594

I. I NTRODUCTION
MERGING from the deep integration of information and
communication technologies (ICT), the smart grid significantly enhances the efficiency, reliability, and sustainability
of traditional power systems [1]. However, this transformation
also introduces new cybersecurity challenges. The smart grid’s
distributed architecture, extensive sensor deployment, and deep
integration with the Internet and IoT significantly expand
its attack surface, exposing the system to a wide range of
cyber threats, including false data injection [2], denial of
service (DoS) attacks, data tampering, malware propagation,
and eavesdropping, all of which can compromise its physical,
communication, and control layers [3]. Attacks that target grid
reliability are particularly critical. By compromising measurement devices (e.g. PMUs, SCADA), attackers can circumvent
bad-data detection mechanisms [4], distort state estimation,
and induce unsafe control decisions. Such failures in realtime monitoring may lead to frequency deviations, localized
outages, or even large-scale system collapse.
To address these challenges, attack detection in smart
grids is evolving toward deeper integration of data-driven
AI methods, cross-layer coordinated defense, and improved
real-time adaptability. Machine learning and deep learning
are widely applied to attack identification: supervised and
semi-supervised models achieve high accuracy in detecting false data injection attacks, while Convolutional Neural
Networks (CNN)- and Long Short Term Memory(LSTM)based architectures enhance time-series anomaly detection
[5]. Generative adversarial networks(GANs) further enhance
robustness against adversarial samples [6]. Hybrid detection
frameworks that combine power system dynamics with datadriven methods are also gaining maturity, enabling cross-layer
attack identification of coordinated attacks through residual
analysis and state estimation deviation in Cyber-Physical
Systems (CPS) [7]. Mitigation strategies such as adversarial
training and moving target defense address model vulnerabilities and evolving attack environments, and online or
reinforcement learning techniques enable real-time adaptation
[8]. In addition, distributed detection architectures prevent
single points of failure [9], and privacy-preserving techniques,
including federated learning, support secure multi-party collaboration without exposing sensitive data [10].
Within this broader landscape, proactive defense has
emerged as a critical direction for smart grid cybersecurity
due to its capability for early warning and early intervention
[1]. Unlike passive detection methods, proactive approaches
facilitate early identification and dynamic response to complex
attacks behaviors [11]. They offer three key advantages. First

E

1558-3783 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

8416

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

they help prevent physical-level cascading failures through
real-time monitoring and behavior analysis [12]. Second,
they adapt to evolving threats by employing dynamic policy
updates and attack graph-based reasoning [13]. Third, they
safeguard data integrity using spatiotemporal anomaly detection [14], [15]. Advanced AI techniques further strengthen
proactive defense. Hybrid architectures such as CNN-LSTM
models enable multi-source data fusion and early anomaly
detection [17], [18]. Spatiotemporal Transformers capture grid
patterns via self-attention mechanisms [19] while federated
learning enables distributed, privacy-preserving detection in
large-scale smart grid environments [20]. However, despite
these advancements, practical implementation faces significant
challenges, including the need for high-fidelity attack data,
real-time adaptation to evolving threats, and balancing detection accuracy with computational efficiency in large-scale grid
environments. These limitations highlight the critical need for
novel frameworks that can translate theoretical advantages into
operational reliability.
To enhance proactive sensing and intervention, deceptionbased strategies, particularly honeypot techniques, are gaining
increasing attention [21]. While mixed H− /H∞ optimization
effectively balances detection sensitivity and robustness in
local physical systems [25], its integration with such proactive
deception mechanisms is imperative for achieving resilient
defense in large-scale, heterogeneous smart grids. Traditionally, honeypots have proven effective in cybersecurity for
attracting attackers and gathering threat intelligence [22], [23],
and their growing potential in power systems is becoming
increasingly evident as a means to bridge the gap between
reactive detection and active defense. By deploying dynamic
and scalable decoys, honeypots enable active defenses through
attack deception and early intervention. This “deception-forearly-warning” paradigm plays a crucial role in evolving grid
security from passive protection to active engagement. Nevertheless, applying honeypots in smart grids introduces unique
complexities, such as designing grid-specific lure services,
mitigating false alarms induced by legitimate operational variations, and ensuring seamless integration with existing grid
control systems. Addressing these challenges is essential to
unlock the full potential of honeypot-driven defense, ultimately
enhancing grid resilience against sophisticated cyber-physical
attacks.
To provide security solutions that are both reliable and
adaptive to emerging threats, this paper presents the following contributions. First, a formal framework is established
through mathematically defined models of industrial communication sequences, enabling precise characterization of
system input–output behaviors and principled identification of
potential threats. Second, a multi-layer detection architecture is
developed, incorporating data preprocessing, honeypot-driven
interaction, dual-path detection, and decision fusion mechanism, along with a gated aggregation strategy for integrating
heterogeneous evidence under dynamic conditions. Third, a
comprehensive theoretical analysis framework is developed to
substantiate the reliability of the proposed detection scheme.
The analysis derives a lower bound on feature discriminability,
ensuring sufficient separability between normal and malicious
behaviors, and establishes an upper bound on the generalization error of the GBDT-based component. Moreover, a

temporal consistency criterion is additionally incorporated
to reduce false alarms by enforcing stability across sliding
time windows. Finally, the proposed framework is evaluated
within operational smart grid environments under diverse and
complex attack scenarios. Experimental findings demonstrate
that the system achieves high detection accuracy, strong generalization capability, and stable long-term performance.
The rest of this paper is organized as follows. Section II
presents the current status and challenges of smart grid
security, followed by a detailed description of the system.
Section III details a construction of the attack detection network, covering the data preprocessing module, the honeypot
interaction layer, the dual-path detection module, and the
decision fusion with post-processing mechanisms. Section IV
provides a theoretical analysis and feasibility demonstration of
the proposed approach. Section V provides experimental evaluations on real-world datasets, demonstrating the effectiveness
of the framework in detecting multiple types of cyber-physical
attacks. Finally, Section VI concludes the paper and discusses
future research directions.
II. P ROBLEM F ORMULATION
The growing openness and interconnectedness of smart
grids enhance operational efficiency and system flexibility but
also increase their vulnerability to sophisticated cyber attacks.
Current attack detection methods face two major challenges.
First, relying on a single detection model makes it difficult to
capture both general anomalies, such as data tampering, and
specific, targeted attacks, leaving vulnerabilities in the highdimensional feature space. Second, many AI-based models
operate as unobservable systems, providing limited interpretability regarding their decision-making processes. This
lack of explainability poses significant risks when deploying
such models in critical power infrastructure. Although some
studies attempt to fuse data from multiple sources, these
approaches are typically reactive, detecting attacks only after
they occur and failing to identify early indicators of emerging
threats. These limitations collectively lead to a critical gap: the
inability to proactively sense and characterize attacks during
their initial stages with high confidence and clear reasoning,
which is paramount for preventing cascading failures in smart
grids.
The smart grid communication environment can be
described as a dynamic time-series system. The main idea is
to build a clear mathematical connection between what goes
into the system and what comes out. Industrial communication
sequences are represented as a collection of quadruples:
N
D = {(ti , fi , ci , si )}i=1
,

(1)

where ti is the timestamp, fi stands for the protocol field, ci is
the instruction code, and si is the device status vector. We use
a sliding window approach to break the continuous stream of
communication into separate session segments {S j } M
j=1 . Each
session includes Q consecutive interaction events. The core
objective of the detection system is to map each session
segment S j to a comprehensive output Γ j = (y j , R j , E j ). Here,
y j ∈ {0, 1} is the final attack determination, R j ∈ [0, 1] is a finegrained risk score indicating the severity level, and E j is a set
of evidence supporting the decision. Designing this detection

CHEN et al.: HONEYPOT-DRIVEN PROACTIVE DETECTION NETWORK FOR ATTACKS IN SMART GRIDS

Fig. 1. Architecture of the honeypot-driven proactive detection network for
smart grids.

function F : D → Γ necessitates balancing multiple critical
requirements. First, it must achieve a high detection rate while
controlling the false alarm rate below an acceptable threshold
α. Second, it must ensure real-time performance such that
the average detection delay E[τdetection ] does not exceed a
maximum tolerable time T max . Third, it must provide inherent
explainability for every decision, ideally by quantifying the
∂R
contribution of each feature (e.g., E j = {φi }di=1 , where φi = ∂ fij ).
To address the limitations of existing detection methods, this
paper proposes a honeypot-driven active detection network. By
simulating decoy services to attract and engage attackers, the
honeypot generates discriminative behavioral features while
providing interpretable real-time evidence for detection. This
proactive mechanism shifts defense efforts upstream, capturing
attack signatures at the source and overcoming the delayed
responses typical of traditional approaches. However, effectively leveraging honeypot interactions requires addressing
two key technical challenges, including ensuring the discriminability of extracted features against evolving attacks and
designing a robust fusion mechanism that integrates multisource evidence reliably.
This paper aims to propose an attack detection network
framework to meet the aforementioned requirements by construction. Its modular architecture, detailed in the next section,
is architected to transform raw communication sequences
into trustworthy detection outcomes Γ j , explicitly tackling the
challenges of model generalization, operational stability, and
decision transparency outlined in this problem formulation.
The next section will describe the detailed structure and
implementation of the detection system.
III. ATTACK D ETECTION N ETWORK F RAMEWORK D ESIGN
In this section, we construct the details of the detection
network, which is designed to fulfill the requirements of accurate detection, false alarm control, real-time performance, and
explainability as outlined in Section II. The system translates
the abstract detection function F : D → Γ into a practical,
layered architecture. As shown in Fig. 1, the system leverages
time-series interaction data from grid communications to accurately classify behaviors. It is worth noting that, preprocessing
and interaction operate in parallel to minimize detection
latency. It computes two key probabilities: a general anomaly
score (Path Y) and a DoS-specific probability (Path X). These
probabilities, together with honeypot-derived evidence, are

8417

Fig. 2. Feature extraction engine and processing flow in the honeypot-driven
detection network.

used to make a final classification into one of four categories:
replay attack, integrity attack, DoS attack, or normal operation.
The following subsections detail the implementation of each
module.
A. Data Preprocessing Module
The data preprocessing module serves as the foundational
stage that transforms the raw communication event streams,
N
represented as a collection of quadruples D = {(ti , fi , ci , si )}i=1
(1) into a structured and analytically ready format. This module directly operationalizes the mathematical model defined in
Section II.
The preprocessing pipeline begins with sessionization,
where a configurable Land overlap sliding window is applied
to the continuous data stream, breaking it into discrete analyzable sessions {S j } M
j=1 . This approach balances the need for
sufficient contextual information with computational tractability. Each session window then undergoes a comprehensive
cleaning procedure. Missing values in temporally dependent
fields, such as device status si , are imputed via linear interpolation informed by neighboring time points. Meanwhile,
categorical variables including protocol fields fi and instruction codes ci are transformed through one-hot encoding to
yield structured categorical feature representations. Numerical
features are subsequently standardized to zero mean and unit
variance to prevent model bias towards features with larger
scales. Concurrently, a suite of statistical features is extracted
from each window, including time-domain characteristics
(e.g., mean, variance, and entropy of inter-arrival times) and
frequency-domain energy signatures derived via Fast Fourier
Transform (FFT). The output is a clean, normalized, and
feature-rich representation of each session, forming a reliable
base for subsequent detection modules and ensuring the input
data quality necessary for achieving the detection goals set
forth in Section II.
B. Honeypot Interaction Layer
The honeypot interaction layer acts as the core component
of the active defense system. It uses a decoy environment
with fake services and simulated systems, as shown in Fig. 2.
All interactions occurring within this controlled environment
are rigorously recorded, thereby producing a comprehensive

8418

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

dataset of attacker behaviors. A dedicated feature engine then
processes these logs to generate a multi-dimensional evidence
vector. The selected features are purposefully designed to
capture essential attack characteristics. Replay Similarity measures the proportion of session commands exhibiting strong
correspondence to historical attack sequences, quantified via a
normalized Hamming distance. Protocol Compliance evaluates
adherence to protocol state machines and syntax rules. Burst
Intensity calculates the Z-score of request rates to identify
flooding patterns. Timing Consistency examines the distribution of inter-packet delays to detect artificial timing patterns
typical of replay attacks. Categorical features are transformed
using one-hot encoding before GBDT scoring. And honeypots identify integrity violations by detecting deviations from
protocol templates
A primary technical challenge is to ensure the extracted features possess sufficient discriminability. This layer addresses
this by designing a feature engine that creates multiple evidence types (e.g., replay similarity, protocol compliance) from
the interaction data, with the explicit goal of maximizing
the separation between attack and normal patterns, thereby
satisfying the following condition:
Dtotal = kE[Φ(S j )|Pk ] − E[Φ(S j )|P0 ]k2 ≥ δ > 0.

(2)

Each piece of evidence is binarized by comparing it to a
set threshold. This practical setup ensures a clear separation
between normal and malicious behavior in the features we use,
providing the foundational input for the subsequent detection
modules.
C. Dual-Path Detection Module
The dual-path detection module employs a collaborative
two-model architecture designed to address the limitation of
single-model approaches by providing complementary analytical strengths.
The first path, referred to the general anomaly detector
(Path Y), is implemented using a gradient boosting decision
tree (GBDT) model, specifically the XGBoost algorithm. Its
input consists of a fused feature representation that integrates
statistical descriptors extracted during preprocessing with binarized threat evidence produced by the honeypot layer. The
model is trained to learn complex, non-linear relationships
that indicate broad-spectrum anomalies, including replay and
integrity attacks. The training process formalizes the model
adaptability requirement as an optimization problem:
min E[L(Fθ (S j ), y j )] + λR(θ),
θ

(3)

where L is the logistic loss function and R(θ) is an L2
regularization term applied to the weights of the decision
trees to control model complexity and prevent overfitting.
The output is a calibrated probability score PY reflecting the
likelihood of a general anomaly.
The second path, designed as the DoS-specific detector
(Path X), is a specialized component focusing exclusively on
DoS attacks. It takes as input the raw traffic volume time series
within the session and is conditioned on the anomaly probability PY produced by Path Y, thereby enabling contextual
interpretation of high-volume traffic in relation to the overall
system anomaly state. Path X is designed to detect the shortterm, high-frequency burst patterns that are characteristic of

DoS floods, which may remain inconspicuous in the general
feature space captured by Path Y. The output of this module
is a dedicated DoS probability PX .
By combining a general anomaly detector with this
specialized DoS-focused pathway, the system achieves complementary detection capabilities, ensuring high sensitivity
to both subtle, broad-spectrum anomalies and concentrated,
high-volume attacks, thereby significantly enhancing overall
robustness and reliability.
D. Decision Fusion and Post-Processing Module
The decision fusion module combines evidence from different sources to make the final decision about an attack,
ultimately producing the following output triplet:

Γ j = y j, R j, E j .
(4)
This module employs a parallel gating structure in which
independent triggers operate concurrently on different evidence streams. Specifically, the Replay Trigger is activated
when the replay similarity evidence is high AND the general
anomaly score PY exceeds a threshold. The Integrity Trigger is
engaged upon the detection of protocol compliance violations
OR abnormal timing consistency, while the DoS Trigger is
triggered if the burst intensity is high AND the DoS-specific
probability PX is elevated. This parallel configuration enables
the simultaneous detection of co-occurring attacks. In cases
where multiple triggers are simultaneously activated, a rulebased conflict resolution mechanism is employed, prioritizing
the attack with the highest potential impact, thereby producing a single, deterministic output y j . Furthermore, to ensure
operational reliability and meet the stability requirement, the
following measures are implemented:
kF(S j + ) − F(S j )k ≤ βkk.

(5)

This module incorporates a temporal stabilization mechanism, wherein a moving average filter to the risk score R j over
a short, configurable time window. An alarm is triggered only
if the smoothed risk score persistently exceeds the predefined
threshold for a minimum duration, temporal characteristics
are implicitly embedded in the input feature vectors. This
straightforward yet effective method achieves exponential suppression of isolated false alarms while maintaining sensitivity
to sustained attacks. Due to the shallow architecture of the
fusion layer, gradient issues are negligible. Consequently, it
ensures the crucial balance between detection sensitivity and
operational reliability, which is particularly essential in grid
and other high-stakes cyber-physical environments.
This section explains how the honeypot-based detection
network is built. The main idea is to turn the theoretical model
into a practical solution using a modular design. The data
preparation module first organizes raw communication flows
into sessions and standardizes them. This creates a foundation
for feature extraction. The honeypot interaction layer mimics
real services to attract attacks, generating evidence from
multiple aspects. The dual-path detection module uses two
methods: one provides general anomaly scores from a GBDT
model, and the other looks for specific signs of DoS attacks.
These two methods work together to improve detection. The
decision fusion module then brings all the evidence together

CHEN et al.: HONEYPOT-DRIVEN PROACTIVE DETECTION NETWORK FOR ATTACKS IN SMART GRIDS

using parallel gating and a temporal stabilization mechanism.
Produces a final reliable risk score. The whole system works
as an end-to-end process, from raw data to final decision. Its
modular design makes it easy to extend or modify.
Remark 1: The four modules form a closely coordinated
detection pipeline. Data preprocessing serves as the starting
point. It converts raw communication traffic into structured
sessions suitable for analysis, delivering a unified input foundation for all following stages. The honeypot interaction layer
acts as the core component for active sensing. It simulates a
realistic environment to capture first-hand evidence of attacks,
supplying critical feature inputs to the detection module.
The dual-path detection module leverages the outputs from
the previous stages, including structured session data and
threat information obtained from the honeypot, to conduct indepth analysis from two complementary perspectives, namely
broad-spectrum anomalies and dedicated DoS attacks, thereby
producing initial probability assessments. Finally, the decision
fusion module integrates direct evidence from the honeypot
with detection results from the dual paths. Through parallel
triggering and temporal stability processing, it outputs the
final classification and risk score. The entire workflow is
data-driven. It not only preserves the functional independence
and extensibility of each module, but also ensures that the
system operates as an integrated whole, achieving end-to-end
detection from raw data to reliable decisions.
With the above architectural design established, the detection network not only accurately identifies attacks but also
makes its decisions understandable through feature importance
analysis. However, practical deployment in critical infrastructures requires that such a design be grounded in rigorous
theoretical justification. To this end, the following section
will explore the mathematical foundations of the proposed
framework. This includes an analysis of the lower bounds
on feature discriminability, the convergence properties of the
learning components, and the theoretical mechanism enabling
false-alarm suppression. These results collectively substantiate
the feasibility and robustness of the system when applied to
real-world power-grid environments.
IV. T HEORETICAL A NALYSIS AND
F EASIBILITY D EMONSTRATION
This section provides a systematic theoretical analysis to
ensure the feasibility and robustness of the proposed detection
framework. We establish a unified mathematical foundation
to verify three key aspects: the usefulness of the feature
representations, the learnability and convergence behavior
of the model, and the reliability of the overall decision
process. Specifically, we will first show that the features
created from honeypot interactions, such as replay similarity and protocol compliance, have a clear and measurable
difference between attack and normal traffic. We then demonstrate that GBDT algorithm under proper regularization learns
very efficiently with exponential convergence. Furthermore,
the system’s false alarm rate can be reduced exponentially
through a window-based consistency check. These results not
only provide theoretical support for the deployment of the
network’s design but also ensure its long-term robustness and
explainability.
We first analyze the effectiveness of the feature set.

8419

Theorem 1: (Lower Bound of Feature Discriminability)
Consider any feature fk extracted at the honeypot interaction layer of the industrial communication anomaly detection
system. Let P1 denote the attack distribution and P0 the
normal-operation distribution. Then the expected values of fk
under these two regimes exhibit a strictly positive separation,
ˇ
ˇ
Dk = ˇEP1 [ fk ] − EP0 [ fk ]ˇ > 0.
Moreover, for the full feature vector f = [ f1 , f2 , . . ., fd ]T , the
overall feature discriminability satisfies:
v
u d
uX
Dtotal = EP1 [f] − EP0 [f] 2 ≥ t
D2k > 0,
(6)
k=1

which establishes a nontrivial lower bound on the separability
of the attack and normal distributions in the feature space.
Proof: We use replay similarity r as an illustrative feature,
quantifying the repetition of session interactions relative to
historical honeypot responses. Under normal conditions (P0 ),
the expected value is EP0 [r] = pnormal , while under attack (P1 )
it becomes EP1 [r] = preplay + δ with δ > 0. The discriminative
power is then:
ˇ
ˇ ˇ
ˇ
(7)
Dr = ˇEP1 [r] − EP0 [r]ˇ = ˇ(preplay + δ) − pnormal ˇ .
Given that attacks inherently produce more repetition
(preplay  pnormal ) and δ > 0, we have:
Dr = δ + (preplay − pnormal ) > 0.

(8)

Thus, replay similarity effectively distinguishes attacks. The
same rationale applies to other features. For each designed
feature fk , the fundamental pattern difference ensures Dk > 0.
For the complete feature vector f = [ f1 , f2 , . . ., fd ]T , let µ1 =
EP1 [f] and µ0 = EP0 [f]. The overall discriminative power is
v
u d
uX
Dtotal = kµ1 − µ0 k2 = t
D2k .
(9)
k=1

Since each Dk > 0, we obtain Dtotal > 0, confirming that
attack and normal patterns form separable clusters.
For bounded features (e.g., ratios in [0,1]), statistical convergence is ensured by Hoeffding’s inequality:
P(| fˆk − E[ fk ]| ≥ ) ≤ 2 exp(−2n 2 ).

(10)

With sufficient samples n, feature estimates converge exponentially to their expectations, guaranteeing the theoretical
discriminative power manifests in practice.
The proof establishes both the inherent discriminative capability of features and their statistical estimability, completing
the demonstration of Theorem 1.

This upper bound 10 decays exponentially with sample size
n. For any predefined error tolerance  > 0 and confidence
level δ > 0, if the sample size satisfies n > log(2/δ)
2 2 , we can
guarantee with confidence at least 1 − δ that the estimation
error | fˆk − E[ fk ]| < . This observation provides theoretical
guidance for system design: ensuring that sessionization procedure yields communication fragments of sufficient length (n
large enough) enables feature estimates to converge to their
theoretical expectations with high probability. Consequently,
the guaranteed discriminative properties Dk and Dtotal are

8420

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

reliably reflected in practical observations, thereby enabling
effective model training and robust attack–benign separation
in real deployments.
We now analyze the convergence properties of the proposed
attack detection framework.
Theorem 2 (GBDT Convergence): Let L(y, F) be a convex and twice-differentiable loss function. Under appropriate
M
regularization conditions, the sequence of models {Fm }m=1
generated by the GBDT algorithm exhibits exponential convergence. Specifically, there exists a constant 0 < ρ < 1,
dependent on the condition number of the problem, such that
the gap between the empirical risk at iteration m, denoted by
R̂(Fm ), and the optimal empirical risk R̂∗ satisfies the following
bound
R̂(Fm ) − R̂∗ ≤ K · (1 − ρ)m ,
where K is a positive constant. This guaranties that the
algorithm converges to the optimal solution at an exponential
rate.
Proof: Gradient boosting constructs an additive model that
sequentially minimizes a differentiable loss function L(y, F(x))
through iterative weak learner incorporation. At each iteration
m, the model undergoes the update Fm (x) = Fm−1 (x) + fm (x),
where fm typically represents a decision tree with limited
depth, ensuring the weak learner condition.
The fundamental advancement of GBDT lies in its exploitation of both first and second-order gradient information for
more informed optimization. This approach provides superior
convergence properties compared to first-order methods. The
optimization objective in iteration m considers the composite
model:
n
X
L(m) =
L (yi , Fm−1 (xi ) + fm (xi )) ,
(11)
i=1

where n denotes the training sample size. x denotes a
d-dimensional feature vector.
When the incremental update fm is relatively small compared to the current model Fm−1 , we employ a second-order
Taylor expansion around Fm−1 :
1
L (yi , Fm−1 + fm ) ≈ L (yi , Fm−1 ) + gi fm (xi ) + hi fm2 (xi ),
2
ˇ
∂L(yi ,F) ˇ
where gi = ∂F F=Fm−1 is the first-order gradient and hi =
ˇ
∂2 L(yi ,F) ˇ
is the second-order derivative (i.e., Hessian).
∂F 2
F=Fm−1
This quadratic approximation captures the local curvature of
the loss function, leading to more precise updates. Since
L(yi , Fm−1 ) remains constant with respect to fm , the optimization objective is reduced to:

n 
X
1
(12)
L̃(m) =
gi fm (xi ) + hi fm2 (xi ) .
2
i=1

For a tree structure partitioning the feature space into J
disjoint regions R1 , . . ., R J , we assign a constant weight ω j to
all samples falling into leaf node R j . The objective function
can be regrouped by leaf nodes:

J 
X
1
(m)
2
L̃ =
G jω j + H jω j ,
2
j=1
P
P
where G j =
i∈R j gi and H j =
i∈R j hi represent the sum
of gradients and Hessians within each leaf. Introducing L2

P
regularization 12 λ Jj=1 ω2j with parameter λ ≥ 0 yields the
regularized objective:

J 
X
1
(m)
2
L̃reg =
G j ω j + (H j + λ)ω j .
2
j=1

This quadratic form admits a closed-form solution by setting
the derivative to be zero:
∂L̃(m)
reg
= G j + (H j + λ)ω j = 0
∂ω j

⇒

ω∗j = −

Gj
.
Hj + λ

The regularization term λ in the denominator prevents excessively large weights, enhancing generalization.
The convexity of the optimization problem is ensured by the
positive definiteness of the Hessian matrix. For the quadratic
approximation,
the second derivative with respect to ω j is H j =
P
h
.
Thus,
we
require hi > 0 for all i to guarantee a unique
i∈R j i
minimum. For binary classification with logistic loss:
L(y, F) = −y log(σ(F)) − (1 − y) log(1 − σ(F)),

(13)

where σ(F) = 1/(1 + e−F ) is the sigmoid function, and the
second derivative is:
∂2 L
= σ(F)(1 − σ(F)) > 0 for all finite F,
∂F 2
satisfying the convexity condition.
Under appropriate regularity conditions (strong convexity,
exact solving), GBDT exhibits linear convergence. After m
iterations, the gap between the current loss and the optimal
value decreases as (1 − ρ)m , where 0 < ρ < 1 depends on the
problem’s condition number. The generalization error bound
follows from statistical learning theory:
r
log(1/δ)
R(F) ≤ R̂(F) + Rn (F) +
,
(14)
2n
h=

where R̂(F) is the empirical risk, Rn (F) is the Rademacher
complexity of the hypothesis space F, and the third term
is a confidence bound. Regularization techniques effectively
control model complexity, ensuring the bound remains tight
and preventing overfitting.
The proof thus establishes theoretical convergence guarantees and generalization properties of GBDT, thereby
completing the demonstration of Theorem 2.

Theorem 2 shows the effectiveness and reliability of the
GBDT model as the core detector. The analysis provides a
theoretical explanation for GBDT’s capability to efficiently
learn complex nonlinear relationships through an iterative
process. The resulting model exhibits strong generalization
performance, thereby ensuring the learning capability of the
industrial communication anomaly detection system.
Theorem 3 (False Alarm Rate Reduction): The window
consistency check mechanism reduces the probability of isolated false alarms from the single-time-point probability pFP
to:
!
W k
window
PFP
≈
pFP ,
(15)
k
where W is the time window size and k is the minimum
number of threshold exceedances required for a positive decision, with k ≤ W. For pFP  1, this mechanism yields an

CHEN et al.: HONEYPOT-DRIVEN PROACTIVE DETECTION NETWORK FOR ATTACKS IN SMART GRIDS

exponential reduction (of order k) in the resulting false alarm
rate.
Proof: The temporal stabilization module continuously
monitors risk scores Rt over a sequence of consecutive time
segments t = 1, 2, . . ., W. This monitoring process forms the
basis for reducing transient false alarms while maintaining sensitivity to sustained attacks. For each time segment, we define
a Bernoulli random variable Xt that captures the threshold
exceedance event:
(
1 if Rt > Θ (indicating a false alarm occurrence)
Xt =
0 otherwise (normal operation)
where Θ represents the decision threshold for anomaly detection. Under the assumption that false alarm events at different
time segments are independent and occur with identical
probability, we have P(Xt = 1) = pFP for all t. This independence assumption is reasonable when considering sufficiently
spaced time segments where temporal correlations diminish.
Consequently, the sequence {Xt }W
t=1 constitutes independently
and identically distributed Bernoulli random variables with
parameter pFP .
The window consistency check mechanism implements a
robust decision rule where an alarm is triggered only when
the cumulative number of threshold exceedances, S W , within
a sliding window of length W reaches or exceeds a predetermined minimum count k, with k ≤ W. This approach ensures
that isolated anomalies do not trigger false alarms while
maintaining detection capability for sustained attack patterns.
The random variable S W , representing the total number of
exceedances, is defined as the sum of the W independent
Bernoulli variables:
SW =

W
X

Xt .

(16)

t=1

By the additive property of independent Bernoulli trials, S W
follows a binomial distribution: S W ∼ Binomial(W, pFP ). The
probability mass function characterizing this distribution is
described as follows:
!
W s
P(S W = s) =
pFP (1 − pFP )W−s , s = 0, 1, . . ., W.
s
The false alarm probability under the window-based mechanism corresponds to the probability that S W meets or exceeds
the threshold k under normal operating conditions (absence of
real attacks):
!
W
X
W s
window
PFP
= P(S W ≥ k) =
pFP (1 − pFP )W−s .
s
s=k

In practical industrial anomaly detection systems, stringent
reliability requirements dictate that the single-point false alarm
rate pFP must be maintained at very low levels (typically
pFP < 0.1). When pFP  1, we can perform an asymptotic
analysis of the summation. The dominant contribution comes
s
from the first term (s = k) since pFP
decreases superlinearly
with increasing s. The higher-order terms (s = k + 1, k +
s
2, . . ., W) become negligible because pFP
diminishes by orders

8421

of magnitude relative to pkFP . This dominance permits the
following approximation:
!
W k
window
PFP
≈
pFP (1 − pFP )W−k .
k
Given the small magnitude of pFP , the factor (1 − pFP )W−k
approaches unity, leading to the simplified expression:
!
W k
window
≈
pFP .
PFP
k
This result demonstrates that the window consistency check
mechanism reduces the false alarm rate exponentially with
exponent k when pFP  1, providing substantial improvement
over single-point detection schemes.
The proof of Theorem 3 is completed.

Remark 2 (Index reduction effect): The approximation
formula Wk pkFP clearly demonstrates that the false alarm rate
after window processing is proportional to the k-th power of
the single-point false alarm rate. Since k ≥ 1 and pFP < 1,
an exponential reduction in the false alarm rate is achieved
whenever k > 1. The coefficient Wk represents a binomial
coefficient, which typically remains a moderate constant under
practical parameter settings.
Notably, while effectively suppressing isolated false alarms,
this mechanism has minimal impact on the detection probability of sustained attacks. For a real attack lasting W time
segments, the risk score Rt at each segment has a high
probability pD (probability of detection) of exceeding the
threshold Θ. In this scenario, S W also follows a binomial
distribution Binomial(W, pD ). Since pD is designed to be much
larger than pFP , the value of P(S W ≥ k) remains very close to
1, ensuring a high attack recall rate.
Theorem 4 (System Effectiveness Lower Bound): The
overall detection probability of the industrial communication
anomaly detection system satisfies the following lower bound:
Psystem ≥ 1 − exp (−n · min(SNRY , SNRX )) − δcal ,

(17)

where n is the sample size used for feature estimation (e.g.,
number of interactions in a session fragment), SNRY and
SNRX represent the signal-to-noise ratios in the feature spaces
of Path Y and Path X detectors, respectively, δcal is the upper
bound of error introduced by model score calibration.
Proof: The overall detection process of the system can be
decomposed into three sequential stages: feature extraction
(F), model inference (M), and decision fusion (D). Successful
system operation requires correct execution across all stages.
To characterize this behavior, we derive a comprehensive lower
bound for the overall success probability by systematically
examining the error probability contributions from each individual stage.
Define the following success events:
• E F : Feature extraction successfully produces discriminative features that distinguish attacks from normal
behavior.
• E M : Model inference correctly maps features to accurate
risk scores.
• E D : Decision fusion properly classifies events based on
the synthesized evidence.

8422

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

The overall system detection probability is given by
Psystem = P(E F ∩ E M ∩ E D ). Applying the complement form
of the union bound from probability theory, we have
Psystem = 1 − P(¬E F ∪ ¬E M ∪ ¬E D )
≥ 1 − [P(¬E F ) + P(¬E M ) + P(¬E D )].

(18)

This inequality provides the foundation for establishing a
lower bound by analyzing the individual failure probabilities.
Feature extraction fails when the estimated feature vector
possesses insufficient signal-to-noise ratio (SNR) to reliably
distinguish between attack and normal patterns. From Theorem 1, the theoretical feature discriminability Dtotal > 0
under attack conditions. However, practical estimation from
finite samples introduces statistical uncertainty. For bounded
features, Hoeffding’s inequality bounds the estimation error:
P(| fˆ − E[ f ]| ≥ ) ≤ 2 exp(−2n 2 ).
This exponential concentration inequality ensures that with
sufficient sample size n, the feature estimation error becomes
negligible. The failure probability is consequently bounded by:
P(¬E F ) ≤ exp(−n · min(SNRY , SNRX )),

(19)

where the min operation ensures robustness regardless of
which detection path identifies the attack.
The model inference stage learns the mapping x 7→ s =
M(x) from features to risk scores. Theorem 2 guarantees
that under appropriate regularization, the GBDT algorithm
converges with bounded generalization error. Additionally, calibration techniques such as Platt scaling control the calibration
error within δcal , ensuring that the output scores accurately
represent true posterior probabilities. The model-specific errors
beyond those attributable to poor feature quality are considered
higher-order terms, as the primary discriminative capability
originates from the feature engineering stage.
Decision fusion integrates scores from both paths through
parallel gating and temporal stabilization. The OR-logic parallel gating ensures P(E D ) ≥ max(P(E DY ), P(E DX )), meaning
the system succeeds if either path produces correct detection.
Theorem 3 further guarantees that temporal stabilization provides exponential reduction in false alarms while maintaining
high detection probability for sustained attacks. Consequently,
P(¬E D ) represents a negligible higher-order contribution compared to the preceding stages.
Integrating the individual error bounds through the union
bound framework yields the comprehensive system guarantee:


Psystem ≥ 1 − exp(−n · min(SNRY , SNRX )) + δcal + σ
≈ 1 − exp(−n · min(SNRY , SNRX )) − δcal ,
where σ aggregates the higher-order terms from the decision
fusion stage. This result provides a rigorous theoretical guarantee for the overall system effectiveness.
The proof of Theorem 4 is completed.

Remark 3: Through the proofs of Theorems 1-4, this
paper develops a complete theoretical framework for the
proposed detection network. The derived lower bound on
feature discrimination, Dtotal > 0, ensures that behavioral
features extracted from honeypot interactions are separable
between attack and normal modes. The exponential convergence property of GBDT, together with its generalization

Fig. 3. Attack classification confusion matrix.

error bounds, theoretically supports the learning capability of
the model. Moreover, the window-based consistency check
mechanism exponentially suppresses the false positive rate, as
characterized by Pwindow
∝ pkFP , thereby ensuring the system’s
FP
reliability in practical deployments. Collectively, these results
not only validate the soundness of the proposed the network
design but also provide explicit mathematical guidance for
parameter selection, such as the decision threshold Θ and
window size W, reducing reliance on purely empirical tuning.
V. E XPERIMENT
In this section, we evaluate the proposed active defense
detection network using real-world datasets. The experimental
validation assesses the system’s feasibility and robustness
through a two-phase approach. Initial model training and
performance analysis are conducted on a single-phase representation of a realistic low-voltage grid in Denmark [24].
To examine generalization capability, the trained model is
subsequently evaluated on data collected from an IEEE
14-bus microgrid environment, which maintains consistent
attack logic while incorporating system noise.
The experimental design strictly follows theoretical guidelines, with emphasis on validating feature effectiveness,
model convergence, and decision mechanism rationality. This
approach establishes a complete verification chain from theoretical foundation to practical implementation.
A. Model Performance Validation on Danish Low-Voltage
Grid Data
This study presents a comprehensive evaluation of the
proposed anomaly detection network using real-world communication data collected from an operational low-voltage
grid infrastructure in Denmark. The experimental methodology
employs rigorous time-series splitting procedures, partitioning
the dataset into distinct validation and test sets containing
1,540 and 1,538 samples respectively. Attack scenarios constitute approximately 76% of the total samples, encompassing
three critical attack categories: DoS attacks, integrity violations, and replay attacks. This balanced distribution ensures
both statistical significance and practical relevance for industrial security applications.
The detection model demonstrates remarkable consistency
across both validation and test environments. Attack-specific
classification capabilities are quantitatively illustrated through
the confusion matrix presented in Fig. 3, which provides
detailed accuracy metrics for each attack category. Diagonal

CHEN et al.: HONEYPOT-DRIVEN PROACTIVE DETECTION NETWORK FOR ATTACKS IN SMART GRIDS

8423

Fig. 6. Hardware-in-the-loop security testbed for IEEE 14-Bus microgrid.
Fig. 4. Top-20 feature importance ranking.

Fig. 5. Class probability distribution comparison.

elements represent correct classification rates, achieving 0.984
for DoS attacks, 0.990 for integrity attacks, and 0.990 for
replay attacks. These near-perfect values indicate exceptional
recognition accuracy across all attack types. Off-diagonal
elements, representing misclassification errors, maintain values
below 0.01, confirming minimal false positive rates that satisfy
stringent industrial precision requirements. On the independent
test set, all three attack categories maintain detection rates
exceeding 98.4%, with DoS attacks at 98.4% while integrity
and replay attacks approach 99.0% accuracy. This consistently
high performance across diverse attack scenarios validates the
effectiveness of the parallel gating mechanism in complex
operational environments.
Feature importance analysis, depicted in Fig. 4, offers
valuable insights into the underlying operation of the detection mechanism. The three most influential features, namely
previous window similarity (0.15), replay ratio (0.14), and
excessive stability (0.12), are all originate from the honeypot
interaction layer and exhibit substantially stronger discriminative capability than the remaining features. This concentration
of honeypot-derived features provides empirical validation
for the theoretical principle of a lower bound on feature
discriminability established earlier in this work. In addition,
the top four features together contribute more than 50% of
the overall feature importance, demonstrating the efficiency
of the proposed feature engineering approach, which achieves
reliable decision-making while keeping computational complexity low.
Probability distribution analysis, illustrated in Fig. 5, reveals
distinct separation patterns between normal and attack classifications. Attack samples demonstrate significant concentration
in the high-probability region (0.8-1.0), while normal samples exhibit substantially lower densities within this critical
range. This clear probabilistic separation establishes a reliable
foundation for threshold configuration and enables precise
alert generation in high-risk operational scenarios. The welldefined boundary between classes further confirms the model’s
calibration quality and its suitability for practical deployment.
Generalization capability assessment through cross-dataset
performance comparison reveals exceptional stability. Key
detection metrics maintain consistency with less than 0.5%
degradation in detection rates across all three attack categories
between validation and test environments. This minimal performance variation confirms the temporal stability of learned
attack patterns and the system’s inherent adaptability to natural grid communication variations. The results collectively
demonstrate the practical viability and operational value of the
detection system in real-world low-voltage grid environments,
establishing it as a reliable security solution for industrial control systems requiring robust anomaly detection capabilities.
B. Model Generalization Validation on IEEE 14-Bus
Microgrid Data
The experimental platform for data acquisition is depicted in
Fig. 6, comprising core components including a DC-DC buck
converter, DC voltage source, oscilloscope, and rapid control
prototyping hardware. This setup provides reliable experimental conditions for collecting communication data with system
noise in an IEEE 14-bus microgrid environment. The detection
model, previously trained on Danish low-voltage grid data,
is directly applied to this new environment to evaluate the
practical performance of the honeypot-based active defense
detection network in cross-system deployment scenarios.
Experimental results demonstrate excellent generalization
capability and robustness. On the validation set, the model
achieved an accuracy of 0.989, with perfect normal sample
recall (1.0) and attack sample recall of 0.987. When evaluated
on the test set containing mild system noise, the model
maintained high performance with an accuracy of 0.974,
stable normal sample recall (1.0), and attack sample recall of
0.968. Although test set performance showed approximately
1.8 percentage points degradation due to noise interference,
this reduction remains within acceptable limits, indicating
overall stability.
Analysis of specific attack categories reveals strong detection capabilities across different attack patterns. DoS attacks
achieved the highest detection rate (0.984), while replay and

8424

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

integrity attacks maintained detection rates of 0.959 and 0.955,
respectively. Notably, DoS attacks demonstrated the strongest
noise immunity under current threshold settings. Both replay
and integrity attacks maintained detection rates above 95%
under mild noise conditions, confirming the significant discriminative power and stability of attack features extracted by
the honeypot-based active defense mechanism.
Validation on the practical microgrid experimental platform
further demonstrates the advantages of the proposed detection network, including strong generalization ability, modular
design that allows integration of new specialized detectors,
high tolerance to system noise, and a favorable balance
between accuracy and robustness. These results indicate that
the proposed approach provides a reliable and effective technical solution for power system security protection.
VI. C ONCLUSION
This paper addresses the challenge of industrial communication anomaly detection in smart grids by proposing
a honeypot-based active defense framework. A hierarchical
detection architecture is designed that integrates feature extraction, dual-path modeling, and decision fusion to accurately
identify multiple attack types while maintaining operational
reliability. Theoretical analysis establishes fundamental performance guarantees, including lower bounds on feature
discriminability, model convergence properties, and systemwide effectiveness thresholds. Experimental validation using
real-world power grid data demonstrates stable performance,
achieving detection accuracies exceeding 98.4% for DoS,
integrity, and replay attacks, with only degradation under
noisy conditions. Furthermore, the proposed implementation
translates theoretical insights into practical detection modules,
incorporating adaptive threshold calibration and evidencebased decision mechanisms. Overall, the framework provides
a mathematically grounded and practically deployable solution for power grid cybersecurity, achieving high detection
accuracy and robustness without compromising operational
stability.
Future work will focus on developing detection systems that
are more robust and adaptive. A primary focus is on deeply
integrating the physical laws of power grids as hard constraints
into the models. This allows the system to internalize these
principles, which naturally rules out unrealistic attack patterns
and makes its decisions more interpretable and trustworthy.
Another important direction involves creating online adaptive
mechanisms. Since the grid topology and operating conditions
constantly change, the system must dynamically adjust. Using
real-time feedback on its performance such as false alarms
and novel attack samples, which can continuously refine its
detection thresholds and parameters. The goal is to shift from
static defense to a self-evolving one, ultimately forming an
active defense framework that seamlessly blends physics-based
knowledge with data-driven learning for ongoing adaptation.
R EFERENCES
[1]

[2]

H. T. Reda, A. Anwar, A. N. Mahmood, and Z. Tari, “A taxonomy of
cyber defence strategies against false data attacks in smart grids,” ACM
Comput. Surv., vol. 55, no. 14s, pp. 1–37, Dec. 2023.
P. L. Bhattar and N. M. Pindoriya, “False data injection attack with maxmin optimization in smart grid,” Comput. Secur., vol. 140, May 2024,
Art. no. 103761.

[3]

S. Fahmeeda and B. K. Bhagyashree, “Detection and prevention of false
data injection attack in cyber physical power system,” in Proc. IEEE Int.
Conf. Mobile Netw. Wireless Commun. (ICMNWC), Dec. 2021, pp. 1–5.
[4] Z. Qu, J. Yang, Y. Wang, and P. M. Georgievitch, “Detection of false
data injection attack in power system based on Hellinger distance,” IEEE
Trans. Ind. Informat., vol. 20, no. 2, pp. 2119–2128, Feb. 2024.
[5] Z. Yan and H. Wen, “Performance analysis of electricity theft detection
for the smart grid: An overview,” IEEE Trans. Instrum. Meas., vol. 71,
pp. 1–28, 2022.
[6] R. Nawaz, R. Akhtar, S. U. Khan, S. Bu, and M. H. Mahmood, “Deep
learning-driven false data injection attack in renewable integrated smart
grids,” Eng. Appl. Artif. Intell., vol. 156, Sep. 2025, Art. no. 110953.
[7] W. Sun, M. Zamani, M. R. Hesamzadeh, and H.-T. Zhang, “Data-driven
probabilistic optimal power flow with nonparametric Bayesian modeling
and inference,” IEEE Trans. Smart Grid, vol. 11, no. 2, pp. 1077–1090,
Mar. 2020.
[8] R. Huang and Y. Li, “Adversarial attack mitigation strategy for machine
learning-based network attack detection model in power system,” IEEE
Trans. Smart Grid, vol. 14, no. 3, pp. 2367–2376, May 2023.
[9] Y. Zhang, L. Wang, W. Sun, R. C. Green II, and M. Alam, “Distributed
intrusion detection system in a multi-layer network architecture of smart
grids,” IEEE Trans. Smart Grid, vol. 2, no. 4, pp. 796–808, Dec. 2011.
[10] M. A. Husnoo et al., “FedDiSC: A computation-efficient federated
learning framework for power systems disturbance and cyber attack
discrimination,” Energy AI, vol. 14, Oct. 2023, Art. no. 100271.
[11] D. An et al., “Data integrity attack in dynamic state estimation of smart
grid: Attack model and countermeasures,” IEEE Trans. Autom. Sci. Eng.,
vol. 19, no. 3, pp. 1631–1644, Mar. 2022.
[12] J. Yan, H. He, and Y. Sun, “Integrated security analysis on cascading
failure in complex networks,” IEEE Trans. Inf. Forensics Security, vol. 9,
no. 3, pp. 451–463, Mar. 2014.
[13] Z. Ni and S. Paul, “A multistage game in smart grid security: A
reinforcement learning solution,” IEEE Trans. Neural Netw. Learn. Syst.,
vol. 30, no. 9, pp. 2684–2695, Sep. 2019.
[14] A. Farraj, E. Hammad, and D. Kundur, “On the impact of cyber attacks
on data integrity in storage-based transient stability control,” IEEE
Trans. Ind. Informat., vol. 13, no. 6, pp. 3322–3333, Dec. 2017.
[15] M. K. Hasan, A. A. Habib, Z. Shukur, F. Ibrahim, S. Islam, and
M. A. Razzaque, “Review on cyber-physical and cyber-security system
in smart grid: Standards, protocols, constraints, and recommendations,”
J. Netw. Comput. Appl., vol. 209, Jan. 2023, Art. no. 103540.
[16] C. Zhang et al., “Anomaly detection and defense techniques in federated learning: A comprehensive review,”
Artif. Intell. Rev., vol. 57, p. 150, 2024, doi: 10.1007/s10
462-024-10796-1.
[17] J. Wang et al., “Self-learning model fusion for network anomaly
detection: A hybrid CNN-LSTM-transformer framework,” PLoS ONE,
vol. 20, no. 10, Oct. 2025, Art. no. e0332502.
[18] K. Kharoubi, S. Cherbal, M. Akkal, and A. Gawanmeh, “Fed-CNNIDS: A privacy-preserving federated learning-based CNN intrusion
detection system for IoMT,” in Proc. Int. Conf. Commun., Comput., Netw., Control Cyber-Physical Syst. (CCNCPS), Jun. 2025,
pp. 151–156.
[19] S. Aboukadri, A. Ouaddah, and A. Mezrioui, “Machine learning in
identity and access management systems: Survey and deep dive,”
Comput. Secur., vol. 139, Apr. 2024, Art. no. 103729.
[20] A. Belenguer, J. A. Pascual, and J. Navaridas, “GöwFed: A novel
federated network intrusion detection system,” J. Netw. Comput. Appl.,
vol. 217, Aug. 2023, Art. no. 103653, doi: 10.1016/j.jnca.2023.103653.
[21] G. Pagnotta, F. De Gaspari, D. Hitaj, M. Andreolini, M. Colajanni,
and L. V. Mancini, “DOLOS: A novel architecture for moving target
defense,” IEEE Trans. Inf. Forensics Security, vol. 18, pp. 5890–5905,
2023, doi: 10.1109/TIFS.2023.3318964.
[22] A. Javadpour, F. Ja’fari, T. Taleb, M. Shojafar, and C. Benzaı̈d,
“A comprehensive survey on cyber deception techniques to improve
honeypot performance,” Comput. Secur., vol. 140, May 2024,
Art. no. 103792.
[23] L. Zhang and V. L. L. Thing, “Three decades of deception techniques in
active cyber defense–retrospect and outlook,” Comput. Secur., vol. 106,
Jul. 2021, Art. no. 102288.
[24] M. S. Kemal, W. Aoudi, R. L. Olsen, M. Almgren, and H.-P. Schwefel,
“Model-free detection of cyberattacks on voltage control in distribution
grids,” in Proc. 15th Eur. Dependable Comput. Conf. (EDCC), Naples,
Italy, Sep. 2019, pp. 171–176.
[25] X.-J. Li and X.-Y. Shen, “A data-driven attack detection approach for
DC servo motor systems based on mixed optimization strategy,” IEEE
Trans. Ind. Informat., vol. 16, no. 9, pp. 5806–5813, Sep. 2020, doi:
10.1109/TII.2019.2960616.
PAPER_TEXT
