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
# [741] Mitigating Membership Inference and Model Inversion in 6G Federated Anomaly Detection
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
编号：741
题名：Mitigating Membership Inference and Model Inversion in 6G Federated Anomaly Detection
年份：2026
DOI：10.1109/tce.2026.3699521
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2026.3699521.pdf
已有粗分类：联邦学习、隐私保护与分布式协同
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\741.txt
- 原始字符数：70016
- 本次发送字符数：70016
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

1

Mitigating Membership Inference and Model
Inversion in 6G Federated Anomaly Detection
M. Junaid Gul, Member, IEEE, Anal Paul, Member, IEEE, and Keshav Singh, Senior Member, IEEE

Abstract—In sixth-generation (6G) networks, federated learning (FL) enables collaborative anomaly detection across distributed edge devices without exposing raw data; however,
exchanged gradients can leak privacy via membership inference
attacks (MIA) and model inversion attacks (MInvA). Meanwhile,
6G network slicing imposes heterogeneous quality-of-service
(QoS) requirements across ultra-reliable low-latency communications (URLLC), enhanced mobile broadband (eMBB), and
massive machine-type communications (mMTC), where uniform
defenses often incur 30–60% accuracy loss. We propose a
slice-aware, defense-in-depth framework that calibrates three
coordinated layers: Layer 1 statistical screening with thresholds τURLLC =4.5, τeMBB =5.0, and τmMTC =6.0; Layer 2 sliceaware differential privacy with Gaussian noise σURLLC =0.001,
σeMBB =0.05, and σmMTC =0.10, where URLLC uses lightweight
perturbation to preserve stringent latency while stronger formal
differential privacy is concentrated in eMBB/mMTC; and Layer
3 adversarial retraining using the fast gradient sign method
(FGSM). Coordinating these layers yields complementary benefits: screening reduces attack surface, differential privacy masks
leakage, and adversarial retraining hardens models. Experiments
on CICIDS2017 and N-BaIoT show 95.2% utility retention with
82.15% accuracy, a +16.7% macro-F1 improvement, 91–94%
communication reduction, MIA success reduced from 78.3% to
52.1%, model inversion error increased by 34.7%, and an overall
privacy accounting budget ϵtotal ≤ 2.1.
Index Terms—6G, Network Slicing, FL, Anomaly Detection,
Membership Inference, Model Inversion, Differential Privacy,
Defense-in-Depth.

I. I NTRODUCTION
EDERATED learning (FL) has emerged as a transformative paradigm for enabling collaborative model training
across distributed devices without exposing raw data, making
it particularly suited for privacy-sensitive applications in nextgeneration wireless networks. However, in Sixth-Generation
(6G) networks, federated anomaly detection faces a critical
challenge: attackers observing gradient exchanges can infer
membership in training datasets through membership inference attacks (MIA) or reconstruct private training samples

F

The work of A. Paul was supported by the National Science and Technology
Council of Taiwan under Grant NSTC 114-2222-E-155-005. The work of K.
Singh was supported by the National Science and Technology Council of
Taiwan under Grants NSTC 114-2218-E-110-005 and NSTC 115-2923-E-110003-MY3, and the Sixth Generation Communication and Sensing Research
Center funded by the Higher Education SPROUT Project, the Ministry of
Education of Taiwan. (Corresponding authors: Keshav Singh; Anal Paul)
M. J. Gul is with the Department of Information and Communication
Engineering, Yeungnam University, Gyeongsan, Gyeongbuk 38541, Republic
of Korea (e-mail: drmalik@yu.ac.kr).
A. Paul is with the Department of Computer Science and Engineering, Yuan
Ze University, Taoyuan 320315, Taiwan (e-mail: apaul@saturn.yzu.edu.tw).
K. Singh is with the Institute of Communications Engineering, National Sun Yat-sen University, Kaohsiung 804201, Taiwan (e-mail: keshav.singh@mail.nsysu.edu.tw).

through model inversion attacks (MInvA) [1], [2]. Simultaneously, the stringent quality-of-service (QoS) requirements
across ultra-reliable low-latency communications (URLLC)
requiring sub-millisecond latency, enhanced mobile broadband
(eMBB) demanding high throughput, and massive machinetype communications (mMTC) serving billions of internet-ofthings (IoT) devices demand slice-aware defense strategies that
balance privacy, robustness, and communication efficiency [3],
[4]. These slices have fundamentally conflicting operational
constraints that a single privacy defense parameter cannot
satisfy.
Existing defense mechanisms for FL primarily focus on
individual techniques, such as statistical screening for malicious updates, differential privacy (DP) to mask sensitive
information, or adversarial retraining to harden models against
inversion attacks, but often neglect the interplay among these
layers within a multi-slice environment [5], [6]. Statistical
screening filters anomalous updates but provides no formal privacy guarantees, leaving membership inference attacks viable.
Differential privacy provides formal privacy bounds but causes
30–60% accuracy degradation when applied uniformly across
all slices, with mMTC slices achieving only 47.98% accuracy
on CICIDS2017 (baseline 83.84%), a 35.86 percentage-point
loss that creates security blind spots for detecting distributed
IoT botnets. Adversarial retraining using fast gradient sign
method (FGSM) improves robustness to gradient inference but
does not prevent membership inference attacks, with success
rates remaining at 63.5% compared to 52.1% when all three
layers are coordinated. Most critically, existing approaches
do not adapt defense parameters to slice-specific requirements: URLLC slices requiring sub-millisecond latency cannot
tolerate heavy privacy perturbation, yet without multi-layer
coordination they become high-value attack targets, while
mMTC slices can benefit from stronger privacy but may
suffer utility collapse under uniform defenses. This creates
a false dichotomy where practitioners must choose between
accepting privacy risks or sacrificing utility in latency-critical
services [7]–[9].
To address this gap, we propose a framework that coordinates defense layers and adapts to slice-specific requirements.
This paper proposes a defense-in-depth hybrid framework tailored for federated anomaly detection in 6G network slices by
coordinating three defense layers and calibrating parameters
to slice-specific QoS requirements. The framework comprises
(i) slice-calibrated statistical update screening using per-slice
thresholds to filter anomalous contributions while preserving
signal in latency-critical slices, (ii) selective Gaussian perturbation with advanced composition accounting for formal

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

2

(ϵ, δ)-DP guarantees while respecting latency constraints, and
(iii) adversarial retraining using FGSM-generated adversarial
examples to smooth loss landscapes and reduce gradient leakage vulnerability. Because DP strength scales with the noise
magnitude, URLLC employs intentionally lightweight perturbation to preserve strict latency, while the strongest formal
DP contribution is concentrated in the less latency-constrained
eMBB/mMTC slices and reinforced by the overall defense-indepth coordination. By coordinating these layers rather than
applying them independently, the framework creates emergent
benefits: screening reduces attack surface dimensionality, differential privacy masks remaining information leakage, and
adversarial training hardens models against inference attacks.
Our approach dynamically adapts to slice-specific privacy–
utility trade-offs and stringent service-level objectives. Experimental results on CICIDS2017 and N-BaIoT demonstrate
95.2% utility retention, a +16.7% macro-F1 improvement, 91–
94% communication reduction, reduced MIA success (from
78.3% to 52.1%), increased model inversion error (+34.7%),
and an overall DP accounting budget of ϵtotal ≤ 2.1 under
slice-calibrated noise.
II. R ELATED W ORK
FL represents a promising approach for distributed anomaly
detection while preserving data privacy. The FedLog framework [10] addresses communication and computation overheads in IoT systems through customizable federated anomaly
detection, achieving 98.7% accuracy with 60% reduction in
communication overhead compared to centralized approaches.
However, the approach focuses primarily on IoT environments
without addressing the specific challenges of 6G network
slicing or sophisticated privacy attacks such as membership
inference and model inversion. Cloud threat forensics has
been enhanced through interpretable federated transformer
architectures [11] that leverage attention mechanisms to identify malicious log patterns across distributed environments.
The framework combines FL with transformer-based sequence
modeling to enable privacy-preserving threat detection while
maintaining model interpretability, achieving 94.3% precision
and 92.1% recall on real-world cloud security datasets. While
demonstrating the effectiveness of transformer-based FL, the
approach lacks comprehensive defense mechanisms against
gradient-based privacy attacks. It does not consider the heterogeneous QoS requirements inherent to network slicing.
Recent comprehensive analysis of FL deep learning for logevent sequence anomaly detection [12] highlights several critical challenges, including privacy preservation, communication
efficiency, and model robustness. The survey identifies the necessity for multi-layered defense mechanisms in federated settings while emphasizing the importance of addressing sophisticated adversarial attacks. Contemporary FL anomaly detection
approaches typically employ single-layer defense strategies,
failing to address the complex threat landscape characteristic
of next-generation networks. Transformer-based architectures
have demonstrated significant potential for log anomaly detection applications. The HitAnomaly framework [13] employs
hierarchical transformer architectures to capture both local

and global patterns in system logs through multi-head attention mechanisms, achieving state-of-the-art performance on
benchmark datasets including HDFS, BGL, and Thunderbird
[13]. While the hierarchical design aligns conceptually with
defense-in-depth approaches, the framework focuses on centralized settings without considering FL constraints or privacy
attack scenarios. Pre-trained transformer models have been
leveraged in the Loader framework [14] for enhanced sequence
understanding in log anomaly detection, demonstrating superior performance with F1-scores exceeding 95% on multiple
datasets. The framework emphasizes contextual understanding
in log analysis, which proves crucial for accurate anomaly
detection in complex network environments. However, the centralized approach fails to address the distributed nature of 6G
networks or associated privacy concerns. Hybrid architectures
combining transformers with complementary deep learning
techniques have emerged as promising solutions. Integration of
transformer attention mechanisms with temporal convolutional
networks [15] enables capture of both long-term dependencies
and local temporal patterns in log sequences, achieving notable
improvements in detection accuracy while reducing computational complexity compared to pure transformer models. The
hybrid approach demonstrates the effectiveness of combining
multiple architectural components, analogous to multi-layered
defense strategies.
A. Multi-Feature Extraction and Robustness
Comprehensive feature extraction represents a fundamental requirement for robust anomaly detection systems. The
AllInfoLog framework [16] extracts and utilizes all available
log features, including semantic content, parameter values,
and temporal information, demonstrating that comprehensive
feature utilization significantly improves detection robustness
with over 97% accuracy across diverse anomaly types. The
multi-feature approach parallels defense-in-depth frameworks
that integrate multiple protection layers for comprehensive
security. Hierarchical contrastive learning has been applied
to enhance the robustness of anomaly detection [17] through
discriminative representations that remain resilient to noise and
adversarial perturbations. The hierarchical structure enables
feature capture at multiple abstraction levels, improving generalization across different log types and attack scenarios. The
approach demonstrates the importance of multi-level defense
mechanisms for achieving robustness in adversarial environments. Contrastive learning combined with dual objective optimization [18] addresses the challenge of limited labeled data in
log analysis through self-supervised learning techniques. The
CLDTLog framework enables simultaneous optimization for
both anomaly detection and representation learning, resulting
in improved model generalization. While demonstrating multiobjective optimization effectiveness, the approach does not
address the FL context or privacy-preserving requirements
essential for 6G network applications.
B. Security Privacy Threats and Present Limitations
Adversarial attacks against anomaly detection systems have
received increasing research attention. Black-box attack investigations [19] demonstrate that adversaries can craft malicious

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

3

log entries that evade detection while maintaining semantic coherence, revealing significant vulnerabilities in existing
anomaly detection approaches and highlighting the necessity for robust defense mechanisms. Such research directly
supports threat models considering sophisticated adversaries
capable of launching privacy attacks against FL systems.
Contrastive adversarial training combined with dual feature
extraction [20] enhances model robustness through explicit
training against adversarial examples while maintaining detection accuracy on benign inputs. The contrastive learning
component enables learning of discriminative representations
resilient to adversarial perturbations. However, the approach
does not consider the FL context or specific privacy attacks relevant to 6G network slicing scenarios. Further, comprehensive
surveys [21], [22] identify several critical limitations in contemporary log-based anomaly detection approaches, including
insufficient privacy preservation consideration in distributed
settings, limited robustness against sophisticated attacks, and
a lack of adaptability to heterogeneous network environments
such as 6G slices. Current approaches typically focus on
single-aspect improvements rather than comprehensive defense
strategies. Critical analysis of deep learning approaches for log
anomaly detection [22] questions the practical applicability of
existing methods, noting significant gaps between academic
research and real-world deployment requirements. Most existing methods fail to address complex operational constraints of
production networks, including privacy requirements, communication limitations, and service differentiation needs. Table
I provides a comprehensive comparison of related work,
limitations, and other aspects with our proposed framework.
C. Literature Basis for Our Experimental Baselines
To ensure a credible and reproducible experimental evaluation, we ground our baseline implementations in established FL security and privacy literature. Privacy-preserving
FL has been explored for IoT-centric multiparty data sharing, using mechanisms such as local differential privacy and
cryptographic protection to mitigate information leakage during collaborative training [32]. Robust FL under malicious
or abnormal client behavior has also been studied through
Byzantine-tolerant aggregation and filtering strategies, which
motivate screening-based defenses that identify and reject
anomalous updates prior to aggregation [33]. Furthermore,
robust asynchronous FL has been investigated in networked
service scenarios such as cellular traffic prediction, highlighting the practical importance of robustness and privacy considerations in real network deployments [34]. In contrast to these
prior-work directions that typically emphasize a single aspect
(privacy or robustness), our proposed framework coordinates
multiple defense layers and calibrates them to heterogeneous
6G slice QoS requirements.
D. Motivation and Contributions
FL for anomaly detection in 6G network slices faces advanced privacy challenges and requires adaptable solutions to
suit diverse QoS constraints. Existing approaches often lack
multi-layered defenses and do not provide adequate robustness

against membership inference, model inversion, or gradientbased privacy attacks. There exists a notable gap in solutions that simultaneously address communication efficiency,
adaptive privacy, and attack resilience for heterogeneous slice
types. In this work, we propose a slice-aware, defense-in-depth
framework for federated anomaly detection that coordinates
three established defense layers.
• Multi-layer defense architecture: Unified statistical
update screening (per-parameter Z-scores), slice-aware
DP(selective Gaussian perturbation with advanced composition), and adversarial retraining FGSM to defend
against multiple attack vectors.
• Slice-based adaptation: Calibration of privacy parameters to match URLLC, eMBB, and mMTC service
requirements, enabling dynamic privacy-utility trade-off
across network conditions.
• Comprehensive attack mitigation: Integrated design defending against membership inference, model inversion,
and gradient leakage across all clients without performance loss.
• Service-aware differentiation: Real-time adjustment of
defenses per slice, balancing privacy, robustness, and
latency or throughput needs.
• Theoretical and empirical validation: Rigorous privacy
analysis and extensive experiments on CICIDS2017 and
N-BaIoT datasets demonstrate high accuracy (over 82%
and 95%), improved F1-scores, up to 94% reduction in
communication, and strong resistance to privacy attacks.
This defense-in-depth, slice-aware framework addresses key
gaps in federated anomaly detection and provides a practical
approach for balancing privacy, robustness, and efficiency in
6G network slicing deployments.
III. M ETHODOLOGY
A. Overview and Workflow
This section presents the proposed Defense-in-Depth framework designed to secure federated anomaly detection across
heterogeneous 6G network slices. We focus on the threat
model of honest-but-curious adversaries capable of inferring
sensitive information via membership inference and model
inversion, while simultaneously satisfying slice-specific QoS
constraints. The experimental datasets, preprocessing, and
federated simulation settings are described in Section IV.
Fig. 1 shows the system overview, and Table II summarizes
the key symbols used in this section. We employ a lightweight
multi-layer perceptron (MLP) optimized for edge devices with
limited computational resources. The model is trained using
cross-entropy loss and stochastic gradient descent (SGD) with
a learning rate of 0.01, batch size of 64, and 5 local epochs
per communication round. To enhance robustness, adversarial
retraining is incorporated using the FGSM with perturbation
magnitude ϵadv = 0.05.
B. System Model and Notation
Consider a FL system F = (C, S, A), where C =
{C1 , C2 , . . . , CN } denotes the set of N clients, S =

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

4

TABLE I
C OMPARISON OF R ELATED W ORK WITH O UR D EFENSE - IN -D EPTH F RAMEWORK .

Reference
Anyanwu
al. [23]

Short Title
CLDP-FATD for Vehicle
Networks

Connection to Our Work
Uses client-level DPfor
threat detection in federated
settings

et

Layer-Wise Personalized
FL for Anomaly Detection

Transformer-based
federated
anomaly
detection
with
layerwise personalization

Wang et al. [25]

Federated BiWGAN-GP
for Network Slicing

Federated
GAN-based
anomaly
detection
for
virtualized network slicing

Zhang et al. [26]

DP FL with Second-Order
Optimization

Differential privacy with
Hessian information for
faster convergence

Li et al. [27]

Selective Shield Hybrid
Defense

Combines selective homomorphic encryption with DP

Hu et al. [28]

Sparsification-Amplified
Privacy

Integrates random sparsification with gradient perturbation

Liu et al. [29]

Cross-silo
FL
Record-level DP

with

Record-level personalized
DP for cross-silo settings

Xu et al. [30]

Optimal Client Sampling
with Heterogeneous DP

Client grouping based on
privacy budgets with optimized sampling

Shi et al. [25]

DP-FedSAM
Sharpness-Aware
Minimization

with

Uses SAM optimizer to improve robustness against DP
noise

Kiani et al. [31]

Overlapping
Grouped
Learning with DP

Privacy guarantees for overlapping group memberships

Barbieri
al. [24]

et

Limitations
Limited to vehicular networks; no slice-aware
adaptation; single defense layer
Focuses only on personalization; lacks privacy
attack defense; no network slicing consideration
Uses only generative
models; no differential
privacy; vulnerable to
membership inference
attacks
Uniform privacy budget; no anomaly detection focus; lacks adversarial robustness
Focuses on gradient
leakage;
no
slice
differentiation; limited
to parameter sensitivity
analysis
General FL; no anomaly
detection; lacks slicespecific optimization
Complex
sampling
mechanisms; no realtime anomaly detection;
lacks network slicing
support
Focuses on client sampling; no anomaly detection; lacks adversarial
defense mechanisms
General
FL;
no
anomaly-specific
optimization;
lacks
slice awareness
Complex group management; no anomaly detection focus; lacks realtime adaptation

Our Work Addresses Gaps
Our framework provides sliceaware DPwith multi-layer defense (screening + DP + adversarial training)
We integrate comprehensive
privacy attack defense with
slice-aware service differentiation
Our
defense-in-depth
combines statistical screening,
differential
privacy,
and
adversarial training
We provide adaptive sliceaware privacy budgets with
multi-layer anomaly-specific
defenses
Our framework addresses multiple privacy attacks with QoSaware slice management

We provide anomaly detection
with slice-aware privacy amplification and service differentiation
Our approach provides realtime slice-aware anomaly detection with adaptive privacy
mechanisms
We integrate optimal privacy
allocation with comprehensive
anomaly detection and adversarial training
Our
framework
provides
anomaly-specific robustness
with
slice-differentiated
service guarantees
We provide real-time sliceaware anomaly detection
with
simplified
privacy
management

Key Contributions of Our Defense-in-Depth Framework:
1. Multi-Layer Defense Integration: Unlike existing works that focus on single defense mechanisms, our framework integrates statistical
screening, slice-aware differential privacy, and adversarial retraining in a unified architecture.
2. Slice-Aware Privacy Adaptation: We propose a slice-aware framework that calibrates privacy parameters to URLLC, eMBB, and mMTC
service requirements, addressing heterogeneous QoS constraints.
3. Comprehensive Attack Coverage: Our approach simultaneously defends against membership inference attacks, model inversion attacks,
and gradient leakage while maintaining anomaly detection accuracy.
4. Real-Time Service Differentiation: We enable dynamic privacy-utility trade-offs that adapt to slice-specific performance requirements
without compromising security guarantees.
5. Theoretical and Practical Validation: Our framework provides rigorous privacy analysis with practical deployment considerations for 6G
network environments.

{URLLC, eMBB, mMTC} represents the network slices, and
A is the central aggregation server. Each client Ck is associated with a slice sk ∈ {0, 1, 2} and holds a private dataset
k
Dk = {(xi , yi )}ni=1
, where xi ∈ Rd and yi ∈ {0, 1}.

The global objective is to minimize the weighted empirical
risk across all clients:
minp L(θ) =

θ∈R

N
X
|Dk |
k=1

D

Lk (θ, Dk ),

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

(1)

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

5

Fig. 1. System model of the proposed federated learning system with multi-layer defense.

TABLE II
S UMMARY OF K EY S YMBOLS
Symbol
F
C
S
θt
θ tk
∆θ tk
Dk
sk
t
zk,j

Description
FL system
Set of N clients
Network slices (URLLC, eMBB, mMTC)
Global model parameter vector at round t
Local model parameters of client k at round t
Parameter update from client k at round t
Local dataset of client k
Slice assignment for client k
Normalized Z-score for parameter j of client k at
round t
Slice-specific Z-score threshold
Slice-specific DP noise standard deviation
Differential privacy parameters
Total privacy budget across all rounds
Loss function
Adversarial loss
FGSM perturbation magnitude
Adversarial example

τsk
σ sk
(ϵ, δ)
ϵtotal
L
Ladv
ϵadv
xadv

PN
where D = k=1 |Dk | and θ ∈ Rp denotes the global model
parameters. Eq. (1) ensures that clients contribute proportionally to their dataset size, preserving fairness in aggregation.
C. Threat Model
We assume an honest-but-curious adversary capable of
observing exchanged parameter updates ∆θ tk = θ tk − θ t−1
but without access to raw data. The adversary aims to infer sensitive information through gradient-based analysis or
statistical correlations, motivating the need for multi-layered
defenses. In our slice-aware setting, defense parameters are explicitly calibrated to heterogeneous QoS constraints: URLLC
employs intentionally lightweight DP perturbation (near-zero
noise) to preserve stringent latency, while stronger formal DP
contributions are concentrated in the less latency-constrained
eMBB/mMTC slices via higher noise scales. Consequently,
URLLC protection is delivered by the coordinated defensein-depth pipeline, where statistical screening reduces the
exposed/abnormal update surface and adversarial retraining

reduces gradient exploitability, providing practical privacy
hardening under URLLC-grade QoS.
D. Slice-Aware Defense-in-Depth Framework
To mitigate these threats, we propose a three-layer defense
mechanism (Algorithm 1) comprising: (i) statistical update
screening, (ii) slice-aware differential privacy, and (iii) adversarial retraining. The overall framework achieves a balance
between privacy, robustness, and efficiency, tailored to the
differentiated requirements of 6G network slices.
1) Layer 1: Statistical Update Screening: Z-score screening operates as a pre-aggregation filter, checking whether
each client’s parameter updates deviate significantly from the
population mean. This design differs from robust aggregation rules (e.g., Krum, Trimmed Mean) which operate at
the aggregation stage by down-weighting outlier clients. Our
pre-aggregation screening is lightweight and communicationefficient but may be less effective against stealthy poisoning
attacks that craft updates remaining within per-coordinate
acceptance bounds. Future work should investigate combining
screening with robust aggregation (screen then aggregate) for
enhanced Byzantine resilience. At each communication round
t, client k computes its local update as:
∆θ tk = θ tk − θ t−1 .

(2)

Eq. (2) defines the parameter difference transmitted to the
server for aggregation.
To detect anomalous updates, normalized Z-scores are computed for each parameter j:
t
zk,j
=

t
∆θk,j
− µtj
,
σjt + 10−9

(3)

where 10−9 prevents division by zero.
The mean and standard deviation for parameter j across all
N clients are computed as:
v
u
N
N
u1 X
X

1
t
t
t
t − µt 2 .
∆θi,j , σj = t
µj =
∆θi,j
(4)
j
N i=1
N i=1

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

6

Algorithm 1 Slice-Aware Defense-in-Depth FL Training.

An update is accepted if:
t
≤ τsk ,
zk,j

∀j ∈ {1, . . . , p},

(5)

where τsk is the slice-specific threshold. For example,
τURLLC = 4.5, τeMBB = 5.0, and τmMTC = 6.0. These
thresholds are motivated by a normal-approximation heuristic
that makes Z-score cutoffs interpretable as conservative outlier
filters; however, strict Gaussianity is not required, and we treat
this assumption as a practical guideline for threshold selection
rather than a formal prerequisite.
2) Layer 2: Slice-Aware Differential Privacy: After screening, we enforce a bounded sensitivity via ℓ2 clipping and then
apply the Gaussian mechanism with slice-calibrated noise.
Each accepted client update is clipped as
!
C
t
¯ = ∆θ t · min 1,
,
(6)
∆θ
k
k
∆θ tk 2
where C is the clipping bound. The server then perturbs the
clipped update:

¯ t + nt , nt ∼ N 0, σ 2 C 2 I .
˜ t = ∆θ
∆θ
(7)
k
k
k
k
sk
Noise magnitudes are calibrated to balance privacy and
utility:
σURLLC = 0.001,

σeMBB = 0.05,

σmMTC = 0.10.

(8)

Using the standard Gaussian mechanism bound, a per-round
privacy loss can be related (conservatively) to (C, σsk , δ) as
s
s




C
1.25
1.25
1
ϵt ≈
2 ln
2 ln
=
, (9)
σsk C
δ
σsk
δ
where the approximation reflects the commonly used analytical bound for the Gaussian mechanism and assumes the sensitivity is bounded by clipping in (6). The total privacy budget
across T rounds is then computed via composition (or a tighter
accountant, e.g., Rényi/moments accountant), yielding ϵtotal for
a chosen δ. Because formal DP strength increases with the
noise magnitude, URLLC employs intentionally lightweight
perturbation to preserve strict latency, while the strongest
formal DP contribution is concentrated in the less latencyconstrained eMBB/mMTC slices via larger noise. Accordingly,
URLLC protection is reinforced by defense-in-depth coordination (screening + adversarial retraining + lightweight DP)
rather than DP noise alone.
3) Layer 3: Adversarial Retraining: To enhance robustness
against inference attacks exploiting model gradients, each
client augments its local training with adversarial examples
generated using the FGSM. For a clean input x, the adversarial
example is computed as:

Require: Initial global model θ 0 , client set C, slice assignments sk , thresholds τs , noise parameters σs , total rounds
T.
1: for t = 1 to T do
2:
Ut ← ∅.
3:
for all clients k ∈ C do
4:
Perform local training with adversarial retraining
using Eqs. (10) and (11).
5:
Compute update ∆θ tk = θ tk − θ t−1 via Eq. (2).
6:
Calculate Z-scores using Eq. (3).
7:
if update passes screening by Eq. (5) then
t
f = ∆θ t + nt , where nt ∼
8:
Apply DP noise: ∆θ
k
k
k
k
N (0, σs2k I) (Eq. (7)).
t
f }.
9:
Ut ← Ut ∪ {∆θ
k
10:
else
11:
Reject update.
12:
end if
13:
end for
14:
if |Ut | > 0 then
P
15:
θ t ← θ t−1 + |U1t | ∆∈Ut ∆.
16:
else
17:
θ t ← θ t−1 .
18:
end if
19: end for
Ensure: Final global model θ T .

where λ ∈ [0, 1] satisfies λ + (1 − λ) = 1, and typically
λ = 0.5.
4) Integrated Training Procedure: Algorithm 1 provides
the end-to-end realization of the proposed slice-aware
Defense-in-Depth framework by explicitly integrating the
three defense layers into a single federated training loop.
Specifically, it formalizes (i) the local adversarial retraining
step using FGSM (Eqs. (10)–(11)), (ii) the statistical update
screening performed on each client update using the Z-score
test (Eqs. (3)–(5)), and (iii) the slice-aware differential privacy
perturbation applied to accepted updates (Eqs. (7)–(9)). The
accepted and perturbed updates are then aggregated to update
the global model for the next round, making Algorithm 1 the
operational counterpart of the analytical formulation presented
in this section.
E. Complexity and Theoretical Guarantees

The per-round complexity is O(N p) for local training and
Z-score computation, and O(p) for aggregation, where N
is the number of clients and p is the model dimension.
xadv = x + ϵadv · sign(∇x L(θ k , x, y)) ,
(10) The framework provides an overall DP accounting bound
through Eq. (9), robustness via Eqs. (10)–(11), and Byzantine
where L denotes the loss function, θ k represents the local
resilience through Eqs. (3)–(5). Consistent with the slice-aware
model parameters, and ϵadv controls the perturbation magnidesign, the effective DP strength is slice-dependent due to the
tude.
calibrated noise scales in Eq. (8).
The local training objective is modified to combine clean
Privacy Analysis: After statistical screening, we bound the
and adversarial samples:
ℓ2 -sensitivity of each accepted client update by applying ℓ2
Ladv (θ k , Dk ) = λ Lclean (θ k , Dk )+(1−λ) Lperturbed (θ k , Dkadv ),clipping with norm bound C in Eq. (6). Given this bounded
(11) sensitivity, adding Gaussian noise with covariance σs2k C 2 I
© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

7

in Eq. (7) implements the Gaussian mechanism and yields
a per-round (ϵt , δ)-differential privacy guarantee, where ϵt is
conservatively related to (σsk , δ) as in Eq. (9). The cumulative
privacy loss over T communication rounds is then obtained
via composition (e.g., advanced composition or a tighter
Rényi/moments accountant), resulting in an overall privacy
budget ϵtotal for the chosen δ.
Utility Preservation: Noise variance σs2k is minimized
for latency-critical slices (i.e., URLLC) to preserve accuracy,
while higher noise is applied to eMBB and mMTC for stronger
privacy.
Robustness
Enhancement: Adversarial retraining
(Eqs. (10)–(11)) increases the perturbation required to
compromise predictions, improving resilience against
gradient-based inference attacks.
IV. S IMULATION AND P ERFORMANCE A NALYSIS
To evaluate the proposed Defense-in-Depth framework,
we conduct simulations on two widely adopted benchmark
datasets for network anomaly detection and compare against
multiple baselines. Hereafter, the term baseline/baselines
refers only to our implemented experimental reference methods (Vanilla FL, Screening-only, Uniform Screening+DP,
Adversarial-only, and Uniform Full Defenses) evaluated under
the same protocol; Section II discusses prior work only. We
use (i) CICIDS2017 [35], [36], a comprehensive intrusion
detection dataset, and (ii) N-BaIoT [37], [38], a large-scale
IoT botnet dataset. All features are normalized to zero mean
and unit variance. We use a fixed split of each dataset into
training (70%), validation (15%), and test (15%) sets with
a fixed random seed (seed = 42) to ensure reproducibility,
and the same split is used for all baselines and defense configurations to ensure fair comparison. We then partition only
the training split across clients to emulate realistic federated
non-independent and identically distributed (i.e., non-i.i.d.)
slice distributions, where each client is assigned to a slice
(URLLC/eMBB/mMTC) reflecting heterogeneous QoS and
traffic characteristics anticipated in 6G deployments (the validation split is used only for hyperparameter selection/tuning).
Unless otherwise stated, all reported metrics (accuracy, macroF1, precision, and recall) are computed on the held-out centralized test split using the global model (final round for summary
tables and per-round values for learning curves). CICIDS2017
provides diverse benign and attack traffic traces suitable for
intrusion/anomaly detection evaluation. N-BaIoT captures IoT
telemetry under botnet behaviors (e.g., Mirai/BASHLITE),
making it suitable for evaluating robustness under non-i.i.d.
and high-dimensional settings. We evaluate on two widely
adopted, complementary benchmarks (CICIDS2017 and NBaIoT) to provide controlled and reproducible comparison
of slice-aware defense coordination under heterogeneous QoS
constraints. While these datasets cover distinct traffic modalities (enterprise intrusion traces vs. IoT botnet telemetry)
and enable fair benchmarking, cross-dataset transfer (unseendomain) evaluation is beyond the scope of this study; therefore,
robustness under arbitrary dataset/environment shift remains
an open question and is deferred to future work.

Fig. 2. Final performance comparison on CICIDS2017 dataset across different
defense methods.

Fig. 2 shows that the baseline FL (Vanilla FL) achieves
a macro-averaged F1-score of 0.36 on CICIDS2017, reflecting limited detection of minority anomaly classes. Applying
uniform defenses reduces the F1-macro to 0.13, a 63.9%
relative drop that underscores the detrimental impact of nonadaptive defense strategies. In contrast, the Hybrid Defense
increases the F1-macro to 0.42, marking a 16.7% improvement over the baseline and more than tripling performance
relative to uniform defenses. This gain demonstrates that sliceaware calibration of screening thresholds and noise parameters
substantially enhances robustness to class imbalance.

Fig. 3. Performance comparison on N-BaIoT dataset across defense methods.

Fig. 3 demonstrates the performance comparison on the NBaIoT dataset, which exhibits different characteristics from
CICIDS2017. The baseline FL achieves 95.41% accuracy and
F1-macro of 0.49, establishing performance bounds for IoT
botnet detection. Uniform defenses cause catastrophic degradation to 40.64% accuracy and 0.33 F1-macro representing
57.4% and 32.7% relative performance losses, respectively.
This severe utility degradation illustrates the inadequacy of
one-size-fits-all privacy mechanisms for high-dimensional IoT
data with 115 features. In stark contrast, the Hybrid Defense
maintains 95.15% accuracy (99.7% utility retention) while
achieving 0.78 F1-macro (59.2% improvement over baseline). The 54.51 percentage point accuracy improvement and
136.4% F1-macro increase over uniform defenses quantitatively validate the superior privacy-utility balance achieved
through slice-aware defense calibration. These results confirm
that intelligent differentiation of defense parameters is crucial
for maintaining practical utility in diverse 6G network slice environments, particularly for IoT-dense scenarios requiring high
detection accuracy and robust minority class identification.
Fig. 4 illustrates the communication reduction achieved by
different defense strategies across both datasets. Vanilla FL
(no-defense baseline) exhibits zero communication reduction
as it transmits all client updates without screening. Uniform

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

8

TABLE III
P ERFORMANCE C OMPARISON OF D EFENSE M ETHODS .
Method
Vanilla FL
Screening-only
Uniform Screening+DP
Adversarial-only
Uniform Full Defenses
Hybrid Defense (proposed)

Accuracy (%)
83.84
82.50
47.98
81.30
44.12
82.15

Fig. 4. Communication reduction comparison across defense methods: (a)
CICIDS2017 dataset, (b) N-BaIoT dataset.

Screening+DP (i.e., Applies the same screening threshold
and the same DP noise level to all slices (no slice-aware
calibration)) achieves complete communication reduction (∼
100%) by applying strict screening that rejects nearly all
updates, but this comes at the severe cost of model utility
degradation as demonstrated in previous figures. The Hybrid
Defense achieves remarkable communication efficiency with
91.3% reduction on CICIDS2017 and 94.2% on N-BaIoT
while maintaining near-baseline performance. This 8.7% and
5.8% transmission overhead represents the minimal communication cost required to preserve model utility through sliceaware screening. The higher reduction on N-BaIoT (94.2%
vs. 91.3%) reflects the dataset’s inherent characteristics that
enable more aggressive screening without utility loss. The
integration of statistical screening and slice-aware DP achieves
dramatic communication reduction exceeding ∼ 90%, by
selectively rejecting anomalous updates and reducing uplink
transmission payload. This efficiency gain not only conserves
network bandwidth but also prolongs battery life in resourceconstrained clients.
a) Interpretation: The results demonstrate that intelligently combining slice-specific defense layers substantially
improves robustness and privacy without incurring the typical
accuracy and communication penalties observed in uniform
defense models. This balance is critical for practical deployment in heterogeneous 6G network slicing environments.
Table III summarizes the performance on CICIDS2017 and
N-BaIoT datasets. The Hybrid Defense approach attains nearbaseline accuracy (e.g., exceeding ∼ 82% on CICIDS2017
and ∼ 95% on N-BaIoT), closely matching Vanilla FL,
while significantly improving the macro F1-score compared to
uniform defenses. This indicates enhanced detection capability,
especially for minority anomaly classes. The accuracy comparison reveals critical insights into the privacy-utility trade-off
inherent in federated defense mechanisms. Vanilla FL achieves

Macro F1-score
0.36
0.39
0.13
0.41
0.15
0.42

Comm. Reduction (%)
0.0
15.2
100.0
0.0
100.0
91.3

Fig. 5. Round-by-round macro F1-score evolution on CICIDS2017: Baseline
vs. Full Defenses vs. Hybrid (tuned).

83.84% accuracy without privacy protections, establishing the
upper bound for model utility. The Full Defenses Uniform
approach, applying uniform noise and screening across all
slices, suffers severe utility degradation to 47.98% accuracy, a
substantial 35.86% point reduction. This dramatic performance
loss demonstrates the inadequacy of uniform defense strategies
that fail to account for slice heterogeneity and QoS requirements. In contrast, the proposed Hybrid Defense maintains
82.15% accuracy, representing only a 1.69% point decrease
from the baseline a 95.6% utility retention rate. This remarkable preservation of model performance while providing robust
privacy guarantees validates the effectiveness of slice-aware
defense mechanisms. The 34.17% point improvement over
uniform defenses (82.15% vs. 47.98%) quantitatively demonstrates the superior privacy-utility balance achieved through
tailored slice-specific calibration of screening thresholds and
noise parameters.
Fig. 5 shows the evolution of macro F1-score over 10 rounds
on the CICIDS2017 dataset for three scenarios. The Baseline
FL starts at 0.14 in Round 1 and steadily rises to 0.36 by
Round 6, after which it plateaus, indicating rapid convergence.
The Full Defenses Uniform remains constant at 0.13 across
all rounds, reflecting its inability to learn meaningful class
distinctions due to overly aggressive defenses. The Hybrid
Defense (tuned) begins at 0.26, already 85.7% higher than
the baseline’s initial performance, and increases consistently
each round, reaching 0.42 by Round 8. This represents a
61.5% improvement over the baseline’s final F1 (0.42 vs.
0.26) at convergence and more than a 223% gain over uniform
defenses. The steady upward trend and higher plateau demonstrate that slice-aware calibration accelerates learning dynamics and enhances minority class detection without sacrificing
convergence speed. These metrics over communication rounds
indicate stable convergence of the federated optimization pro-

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

9

cess under defensive perturbations. In particular, the accuracy
and macro-F1 improve steadily from early rounds, and the
Hybrid Defense converges toward near-baseline performance
while improving minority-class detection. As specified in the
evaluation protocol above, the per-round curves and summary
tables report held-out test performance of the global model
rather than training-set performance.
A. Component Ablation Study
Fig. 7. Parameter sweep on CICIDS2017: (a) Final accuracy vs. screening
threshold T0 , (b) Final F1-Macro vs. screening threshold T0 .

Further threshold increases to 5.0 and 5.5 reduce F1 to 0.40
and 0.38, showing reduced robustness to rare anomaly classes
as screening becomes lax. These results identify T0 = 4.5
as the optimal trade-off point that maximizes both accuracy
and F1-Macro, validating the importance of careful threshold
tuning in slice-aware statistical screening.
Fig. 6. Ablation study on CICIDS2017: (a) Final accuracy contribution by
component, (b) Final F1-Macro contribution by component.

Fig. 6(a) shows that Screening Only (tuned) retains 83.05%
accuracy and DP Only (tuned) 82.91%, each within 1% of the
83.84% baseline, indicating minimal utility loss when applied
in isolation. Adversarial Only slightly exceeds baseline at
83.86%, demonstrating its effectiveness at enhancing anomaly
separation without privacy noise. The Hybrid Defense (tuned)
yields 82.15%, a 1.69% point decrease from baseline but
a 39.7% improvement over uniform full defenses, confirming that combined defenses harmonize component strengths.
Fig. 6(b) indicates that Screening Only improves F1-macro
to 0.39 (+8.3% vs. baseline), while DP Only achieves 0.34
(–5.6%), showing that privacy noise alone can harm minority detection. Adversarial Only matches baseline at 0.36,
reflecting stable class discrimination. The Hybrid Defense
reaches 0.42, a 16.7% gain over baseline and ∼ 223% over
uniform defenses, illustrating that integrating screening, DP,
and adversarial retraining yields the most robust minority class
performance without excessive utility trade-off.
• Screening-only: Employs statistical update screening
without additional privacy or adversarial defenses.
• DP-only: Applies uniform Gaussian noise to all client
updates without screening or adversarial training.
• Adversarial-only: Incorporates adversarial retraining but
no screening or privacy noise.
• Hybrid Defense: Combines all three layers with sliceaware calibration as proposed.
Fig. 7(a) shows that the final accuracy sharply increases
from 3.85% at T0 = 4.0 to 82.15% at T0 = 4.5, indicating
that the screening threshold must exceed the anomaly Zscore distribution’s mean to allow meaningful updates. As T0
further increases to 5.0 and 5.5, accuracy gradually declines
to 81.76% and 81.23%, reflecting overly permissive screening
that admits noisy updates. Fig. 7(b) demonstrates a similar
trend for F1-Macro: at T0 = 4.0, the model barely learns
(F1=0.03), but performance surges to 0.42 at T0 = 4.5, matching the tuned Hybrid Defense’s optimal minority detection.

Fig. 8. Parameter sweep on CICIDS2017: (a) Final accuracy vs. DP noise
level σ0 , (b) Final F1-Macro vs. DP noise level σ0 .

Fig. 8(a) illustrates the impact of DP noise level σ0 on
final accuracy. At σ0 = 0.01, accuracy is 82.95%, only 0.89%
points below the optimum 82.15% at σ0 = 0.05. Increasing
σ0 to 0.10 further reduces accuracy to 81.60%, a total drop
of 1.35 points from the tuned optimum, demonstrating that
moderate noise balances privacy with performance. Fig. 8(b)
shows the corresponding F1-Macro trend. The F1-score peaks
at 0.42 for σ0 = 0.05, matching the tuned Hybrid Defense’s
optimal minority class detection. At σ0 = 0.01, F1 is 0.39
(7.1% below peak), while at σ0 = 0.10, it declines to 0.38
(9.5% below peak). These results confirm that σ0 = 0.05
provides the best trade-off between privacy noise and robust
anomaly detection, maximizing both accuracy and F1-Macro.

Fig. 9. Parameter sweep heatmaps on CICIDS2017: (a) Final accuracy vs.
screening threshold T0 and DP noise level σ0 (Fig. 15), (b) Final F1-Macro
vs. screening threshold T0 and DP noise level σ0 .

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

10

Fig. 9(a) shows accuracy heatmap: at T0 = 4.0, accuracy
remains near 3.8% regardless of σ0 , indicating ineffective
screening. At T0 = 4.5, accuracy peaks between 82.15%
and 82.95% for σ0 ∈ [0.01, 0.05] before slightly dropping
to 81.60% at σ0 = 0.10. For T0 = 5.0, accuracy stays above
∼ 81%, demonstrating robustness across noise levels. Fig. 9(b)
displays F1-Macro heatmap: minimal F1 (0.02–0.03) at T0 =
4.0 for all σ0 . Peak F1 (0.42) occurs at (T0 , σ0 ) = (4.5, 0.05),
with slightly lower values (0.39 and 0.38) at σ0 = 0.01, 0.10.
At T0 = 5.0, F1 remains above 0.36 across noise levels. These
heatmaps confirm that the optimal parameter region is centered
at T0 = 4.5 and σ0 = 0.05, maximizing both accuracy and F1Macro while offering tolerance to moderate noise variations.

Fig. 12. Accuracy vs. Communication Reduction on CICIDS2017.

Fig. 13. Accuracy vs. Communication Reduction on N-BaIoT dataset.
Fig. 10. Slice-aware update acceptance: (a) Updates accepted vs. rejected by
slice, (b) Acceptance rate by slice.

Fig. 10(a) shows that URLLC (Slice 0) accepted 26 updates
and rejected 4, eMBB (Slice 1) accepted 32 and rejected
8, while mMTC (Slice 2) accepted only 6 and rejected 24.
This reflects the framework’s slice-aware screening, which
admits the majority of URLLC and eMBB updates to preserve
low-latency and high-throughput requirements, but rigorously
filters mMTC to enforce stricter anomaly checks. Fig. 10(b)
reports acceptance rates of 86.7% for URLLC, 80.0% for
eMBB, and ∼ 20% for mMTC. The lower rate for mMTC
indicates conservative handling of massive IoT slices to mitigate potential privacy and security risks, whereas the high
rates for URLLC and eMBB balance performance and privacy
according to their QoS profiles.

Fig. 11. Contribution of accepted update (URLLC 26, eMBB 32, mMTC 6).

Fig. 11 shows that among 64 total accepted updates,
URLLC contributes 40.6%, eMBB ∼ 50.0%, and mMTC
only 9.4%. This distribution reflects the slice-aware screening’s prioritization of URLLC and eMBB requirements while
imposing strict scrutiny on mMTC updates. Notably, eMBB

and URLLC together capture 90.6% of all acceptances, underscoring their high-priority status in maintaining network
performance and user experience. eMBB’s dominance aligns
with its bandwidth-intensive applications such as video streaming and augmented reality, which demand frequent resource
reallocation. URLLC’s substantial share reflects the critical
nature of latency-sensitive services like autonomous driving
and industrial control, where even minor delays can have severe consequences. Conversely, mMTC’s minimal acceptance
rate appropriately matches its delay-tolerant IoT characteristics, where sporadic updates suffice for low-power sensor
communications.
Fig. 12 maps each strategy on CICIDS2017 by communication reduction (x-axis) versus final accuracy (y-axis). Vanilla
FL achieves 83.84% accuracy with 0.0% reduction. Uniform
Screening+DP and Uniform Full Defense reach 100.0% reduction but suffer severe utility degradation (47.98% and 44.12%
accuracy, respectively). In contrast, the proposed Hybrid Defense achieves 91.3% reduction while preserving 82.15%
accuracy, demonstrating a substantially better performance–
efficiency trade-off than uniform defenses.
Fig. 13 maps each strategy on the N-BaIoT dataset by communication reduction (x-axis) versus final accuracy (y-axis).
Vanilla FL achieves 95.42% accuracy with 0.0% reduction,
while Uniform Full Defense reaches 100.0% reduction but
drops to 48.67% accuracy. In contrast, the proposed Hybrid
Defense achieves 94.2% reduction while preserving 95.15%
accuracy, demonstrating a superior performance–efficiency
trade-off. The robustness against privacy attacks is quantified
by the reduction in MIA success rates and the increase in
MInvA reconstruction errors compared with Uniform Screening+DP baselines.
Table V summarizes these metrics alongside total privacy

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

11

TABLE IV
C OMPREHENSIVE P ERFORMANCE R ESULTS OF D EFENSE - IN -D EPTH F RAMEWORK
Defense Method

Accuracy (%)

Macro F1

Precision

Recall

Comm. Reduction (%)

Vanilla FL
Screening-only
Uniform Screening+DP
Adversarial-only
Uniform Full Defense
Hybrid Defense (Proposed)

83.84
82.50
47.98
81.30
44.12
82.15

CICIDS2017 Dataset (2.83M samples, 78 features)
0.36
0.84
0.38
0.0
0.39
0.83
0.41
15.2
0.13
0.48
0.15
100.0
0.41
0.82
0.43
0.0
0.15
0.44
0.17
100.0
0.42
0.82
0.44
91.3

Vanilla FL
Screening-only
Uniform Screening+DP
Adversarial-only
Uniform Full Defense
Hybrid Defense (Proposed)

95.42
94.89
52.31
93.75
48.67
95.15

N-BaIoT Dataset (7.06M samples, 115 features)
0.75
0.95
0.77
0.0
0.76
0.95
0.78
18.4
0.21
0.52
0.23
100.0
0.77
0.94
0.79
0.0
0.19
0.49
0.21
100.0
0.78
0.95
0.80
94.2

TABLE V
S ECURITY E VALUATION : ATTACK S UCCESS AND P RIVACY B UDGET
Method
Uniform Screening+DP
Hybrid Defense

MIA Success (%)
78.3
52.1

MInvA Error
Baseline
+34.7%

ϵtotal
3.1
2.1

budget ϵtotal . The slice-aware hybrid approach achieves a
significant MIA success reduction and higher inversion reconstruction error, demonstrating strengthened protection.
The numerical analysis in Table IV reveals several critical
findings, such as the Hybrid Defense achieving a superior
balance, maintaining 82.15% accuracy on CICIDS2017 and
95.15% on N-BaIoT, while reducing MIA success rates to
52.1% and 53.8%, respectively. This represents a 33.5%
and 34.1% improvement in privacy protection compared to
Vanilla FL, with only marginal accuracy degradation (1.69%
and 0.27% respectively). Further, the framework achieves
remarkable communication reduction of 91.3% and 94.2%
through statistical screening, significantly outperforming uniform approaches while preserving model utility. This efficiency gain translates to substantial bandwidth savings and
reduced energy consumption in resource-constrained 6G environments.The slice-aware hybrid approach achieves a significant MIA success reduction and higher inversion reconstruction error, demonstrating strengthened protection (Table IV). The reported privacy budget (e.g., ϵtotal =2.1 and
ϵtotal =1.9 in Table V) is computed under slice-calibrated noise;
consequently, formal DP strength is slice-dependent because
URLLC uses intentionally lightweight perturbation to preserve
strict latency, while the strongest formal DP contribution is
concentrated in the less latency-constrained eMBB/mMTC
slices via higher noise.
V. C ONCLUSION
We presented a slice-aware, defense-in-depth framework
for federated anomaly detection in 6G network slices that
integrates (i) statistical update screening, (ii) selective Gaussian differential privacy, and (iii) FGSM-based adversarial

MIA Success (%)

ϵtotal

78.3
74.1
52.7
63.5
49.8
52.1

4.2
4.5
2.1

81.7
77.9
54.2
67.4
51.6
53.8

3.8
4.1
1.9

retraining. The framework is explicitly slice-calibrated, using
Z-score screening thresholds of 4.5 (URLLC), 5.0 (eMBB),
and 6.0 (mMTC), together with Gaussian perturbation standard
deviations of 0.001, 0.05, and 0.10, respectively, to align
privacy protection with heterogeneous QoS constraints while
reducing gradient leakage. Across CICIDS2017 and N-BaIoT,
the hybrid design preserves near-baseline accuracy (82.15%
and 95.15%), improves macro-F1 (0.42 and 0.78), and reduces
communication by more than 90% (91.3% and 94.2%). Privacy and robustness gains are concrete: membership inference
success drops to approximately 52% (52.1% on CICIDS2017
and 53.8% on N-BaIoT), model inversion reconstruction error
increases by 34.7, and the cumulative privacy loss under
advanced composition is bounded by an overall DP accounting
budget of ϵtotal ≤ 2.1 on CICIDS2017 and ϵtotal ≤ 1.9 on
N-BaIoT under slice-calibrated noise. Because DP strength
scales with perturbation magnitude, the strongest formal DP
contribution is concentrated in the less latency-constrained
eMBB and mMTC slices, while URLLC maintains stringent
latency by using lightweight perturbation and relying on the
coordinated protection of screening and adversarial retraining
rather than DP noise alone. Overall, these results indicate that
per-slice calibration yields a superior privacy utility efficiency
tradeoff compared with uniform defenses in heterogeneous 6G
slicing deployments (URLLC, eMBB, mMTC).
R EFERENCES
[1] G. Singh, K. Sood, P. Rajalakshmi, D. D. N. Nguyen, and Y. Xiang,
“Evaluating federated learning-based intrusion detection scheme for
next generation networks,” IEEE Transactions on Network and Service
Management, vol. 21, no. 4, pp. 4816–4829, 2024.
[2] B. Mi, H. Zou, and D. Huang, “Fedpp: Privacy-enhanced federated learning for parameter aggregation in heterogeneous intelligent connected
vehicles,” IEEE Transactions on Network and Service Management,
vol. 22, no. 6, pp. 5705–5722, 2025.
[3] M. Alsenwi, E. Lagunas, and S. Chatzinotas, “Distributed learning
framework for embb-urllc multiplexing in open radio access networks,”
IEEE Transactions on Network and Service Management, vol. 21, no. 5,
pp. 5718–5732, 2024.
[4] F. Saleh, A. O. Fapojuwo, and D. Krishnamurthy, “eslice: Elastic interslice resource allocation for smart city applications,” IEEE Transactions
on Network and Service Management, vol. 22, no. 6, pp. 5619–5639,
2025.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3699521

12

[5] M. A. Khan, N. Kumar, S. H. Alsamhi, G. Barb, J. Zywiołek, I. Ullah,
F. Noor, J. A. Shah, and A. M. Almuhaideb, “Security and privacy issues
and solutions for uavs in b5g networks: A review,” IEEE Transactions
on Network and Service Management, vol. 22, no. 1, pp. 892–912, 2025.
[6] L. Yang, M. E. Rajab, A. Shami, and S. Muhaidat, “Enabling automl
for zero-touch network security: Use-case driven analysis,” IEEE Transactions on Network and Service Management, vol. 21, no. 3, pp. 3555–
3582, 2024.
[7] A. Kamal Abasi, M. Aloqaily, and M. Guizani, “6g mmwave security
advancements through federated learning and differential privacy,” IEEE
Transactions on Network and Service Management, vol. 22, no. 2, pp.
1911–1928, 2025.
[8] J. Chen, C. Hu, W. Sheng, R. Li, R. Zhao, and J. Yu, “A trust-based
personalized differential privacy guarantees for online social networks,”
IEEE Transactions on Network and Service Management, vol. 22, no. 4,
pp. 3213–3227, 2025.
[9] T. Cao, Z. Zhang, X. Wang, H. Xiao, and C. Xu, “Ptcc: A privacypreserving and trajectory clustering-based approach for cooperative
caching optimization in vehicular networks,” IEEE Transactions on
Sustainable Computing, vol. 9, no. 4, pp. 615–630, 2024.
[10] B. Li, S. Ma, R. Deng, K.-K. R. Choo, and J. Yang, “Federated anomaly
detection on system logs for the internet of things: A customizable and
communication-efficient approach,” IEEE Transactions on Network and
Service Management, vol. 19, no. 2, pp. 1705–1716, 2022.
[11] G. D. Parra, L. Selvera, J. Khoury, H. Irizarry, E. Bou-Harb, and
P. Rad, “Interpretable federated transformer log learning for cloud threat
forensics,” in Proc. 2022 Network and Distributed System Security
Symp., San Diego, CA, USA, 2022.
[12] P. Himler, M. Landauer, F. Skopik, and M. Wurzenberger, “Anomaly
detection in log-event sequences: A federated deep learning approach
and open challenges,” Machine Learning with Applications, vol. 16,
p. 100554, 2024. [Online]. Available: https://www.sciencedirect.com/
science/article/pii/S2666827024000306
[13] S. Huang, Y. Liu, C. Fung, R. He, Y. Zhao, H. Yang, and Z. Luan,
“Hitanomaly: Hierarchical transformers for anomaly detection in system
log,” IEEE Transactions on Network and Service Management, vol. 17,
no. 4, pp. 2064–2076, 2020.
[14] T. Xiao, Z. Quan, Z.-J. Wang, Y. Le, Y. Du, X. Liao, K. Li, and
K. Li, “Loader: A log anomaly detector based on transformer,” IEEE
Transactions on Services Computing, vol. 16, no. 5, pp. 3479–3492,
2023.
[15] N. Liao and Z. Liu, “Log anomaly detection method based on transformer and temporal convolutional networks,” IEEE Access, vol. 13, pp.
68 547–68 560, 2025.
[16] R. Xiao, H. Chen, J. Lu, W. Li, and S. Jin, “Allinfolog: Robust diverse
anomalies detection based on all log features,” IEEE Transactions on
Network and Service Management, vol. 20, no. 3, pp. 2529–2543, 2023.
[17] Y. Zhao, R. Yang, N. Yang, T. Lin, Q. Fu, and Y. Ma, “Robust log-based
anomaly detection with hierarchical contrastive learning,” in ICASSP
2023 - 2023 IEEE International Conference on Acoustics, Speech and
Signal Processing (ICASSP), 2023, pp. 1–5.
[18] G. Tian, N. Luktarhan, H. Wu, and Z. Shi, “Cldtlog: System log
anomaly detection method based on contrastive learning and dual
objective tasks,” Sensors, vol. 23, no. 11, 2023. [Online]. Available:
https://www.mdpi.com/1424-8220/23/11/5042
[19] S. Huang, Y. Liu, C. Fung, H. Yang, and Z. Luan, “Black-box attacks
to log-based anomaly detection,” in 2022 18th International Conference
on Network and Service Management (CNSM), 2022, pp. 310–316.
[20] Q. Wang, X. Zhang, X. Wang, and Z. Cao, “Log sequence anomaly
detection method based on contrastive adversarial training and dual
feature extraction,” Entropy, vol. 24, no. 1, 2022. [Online]. Available:
https://www.mdpi.com/1099-4300/24/1/69
[21] X. Zhao, Z. Jiang, and J. Ma, “A survey of deep anomaly detection
for system logs,” in 2022 International Joint Conference on Neural
Networks (IJCNN), 2022, pp. 1–8.

[22] V.-H. Le and H. Zhang, “Log-based anomaly detection with deep
learning: How far are we?” in 2022 IEEE/ACM 44th International
Conference on Software Engineering (ICSE), 2022, pp. 1356–1367.
[23] G. O. Anyanwu and H. Karimipour, “Cldp=fatd: Secure federated
averaging threat detection framework for intelligent vehicle sensor
networks based on client-level differential privacy,” IEEE Internet of
Things Journal, vol. 12, no. 7, pp. 7693–7707, 2025.
[24] L. Barbieri, M. Brambilla, and M. Roveri, “A layer-wise personalization
approach for transformer-based federated anomaly detection,” in 2024
2nd International Conference on Federated Learning Technologies and
Applications (FLTA), 2024, pp. 32–38.
[25] W. Wang, C. Liang, L. Tang, H. Yanikomeroglu, and Q. Chen, “Federated multi-discriminator biwgan-gp based collaborative anomaly detection for virtualized network slicing,” IEEE Transactions on Mobile
Computing, vol. 22, no. 11, pp. 6445–6459, 2023.
[26] Q. Zhang, L.-F. Li, X. Yang, L.-M. Zhao, and M.-X. Luo, “Differentially
private federated learning model with second-order optimization,” in
2025 10th International Conference on Cloud Computing and Big Data
Analytics (ICCCBDA), 2025, pp. 10–17.
[27] B. Li, L. Yan, and J. Liu, “Selectiveshield: Lightweight hybrid
defense against gradient leakage in federated learning,” 2025. [Online].
Available: https://arxiv.org/abs/2508.04265
[28] R. Hu, Y. Gong, and Y. Guo, “Federated learning with sparsificationamplified privacy and adaptive optimization,” in Proceedings of the
Thirtieth International Joint Conference on Artificial Intelligence,
IJCAI-21, Z.-H. Zhou, Ed. International Joint Conferences on
Artificial Intelligence Organization, 8 2021, pp. 1463–1469, main
Track. [Online]. Available: https://doi.org/10.24963/ijcai.2021/202
[29] J. Liu, J. Lou, L. Xiong, J. Liu, and X. Meng, “Cross-silo
federated learning with record-level personalized differential privacy,”
in Proceedings of the 2024 on ACM SIGSAC Conference on Computer
and Communications Security, ser. CCS ’24. New York, NY, USA:
Association for Computing Machinery, 2024, p. 303–317. [Online].
Available: https://doi.org/10.1145/3658644.3670351
[30] J. Xu, R. Hu, and O. Kotevska, “Optimal client sampling in
federated learning with client-level heterogeneous differential privacy,”
CoRR, vol. abs/2505.13655, May 2025. [Online]. Available: https:
//doi.org/10.48550/arXiv.2505.13655
[31] S. Kiani, F. Boenisch, and S. C. Draper, “Controlled privacy leakage
propagation throughout overlapping grouped learning,” IEEE Journal
on Selected Areas in Information Theory, vol. 5, pp. 442–463, 2024.
[32] L. Yin, J. Feng, H. Xun, Z. Sun, and X. Cheng, “A privacy-preserving
federated learning for multiparty data sharing in social iots,” IEEE
Transactions on Network Science and Engineering, vol. 8, no. 3, pp.
2706–2718, 2021.
[33] Q. Xia, Z. Tao, Q. Li, and S. Chen, “Byzantine tolerant algorithms
for federated learning,” IEEE Transactions on Network Science and
Engineering, vol. 10, no. 6, pp. 3172–3183, 2023.
[34] H. Ma, K. Yang, and Y. Jiao, “Cellular traffic prediction via byzantinerobust asynchronous federated learning,” IEEE Transactions on Network
Science and Engineering, vol. 12, no. 4, pp. 2402–2414, 2025.
[35] I. Sharafaldin, A. H. Lashkari, and A. A. Ghorbani, “Toward generating a
new intrusion detection dataset and intrusion traffic characterization,” in
Proceedings of the 4th International Conference on Information Systems
Security and Privacy - Volume 1: ICISSP,, INSTICC. SciTePress, 2018,
pp. 108–116.
[36] Canadian Institute for Cybersecurity, “Intrusion detection evaluation
dataset (cic-ids2017),” University of New Brunswick. [Online].
Available: https://www.unb.ca/cic/datasets/ids-2017.html
[37] Y. Meidan, M. Bohadana, Y. Mathov, Y. Mirsky, D. Breitenbacher,
A. Shabtai, and Y. Elovici, “N-baiot-network-based detection of iot
botnet attacks using deep autoencoders,” IEEE Pervasive Computing,
vol. 17, no. 3, pp. 12–22, 2018. [Online]. Available: https:
//ieeexplore.ieee.org/document/8490192/
[38] Y. Meidan et al., “detection of IoT botnet attacks N BaIoT,” UCI
Machine Learning Repository, 2018, DOI: https://doi.org/10.24432/
C5RC8J.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
