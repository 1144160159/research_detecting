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
# [637] DAIR-FedMoE: Hierarchical MoE for Federated Encrypted Traffic Classification under Compound Drift
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
编号：637
题名：DAIR-FedMoE: Hierarchical MoE for Federated Encrypted Traffic Classification under Compound Drift
年份：2026
DOI：10.1109/tdsc.2026.3676447
来源：IEEE Transactions on Dependable and Secure Computing
PDF：paper/10.1109_TDSC.2026.3676447.pdf
已有粗分类：加密流量分类与应用识别
二级关联：联邦学习、隐私保护与分布式协同、其他AI安全与跨域异常检测
相关性：强相关，分数 15
已有代码状态：已下载；DairFM -> source\DairFM

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\637.txt
- 原始字符数：117048
- 本次发送字符数：117048
- 是否截断：False

代码包：
- 仓库：DairFM
  - URL：https://github.com/dairfedmoe/DairFM
  - 状态：downloaded
  - 本地目录：source\DairFM
  - 顶层结构：.gitignore、README.md、assets/、configs/、dair_fedmoe/、examples/、requirements.txt
  - 主要语言：Python:34、YAML:1
  - README 标题：DAIR-FedMoE: Hierarchical MoE for Federated Encrypted Traffic Classification、Table of Contents、Prerequisites、1. Python Environment、2. External Tools、3. Dataset、Installation、For CUDA 11.8、For CPU only、Dataset Setup
  - README 运行线索：Python Environment；Python 3.8 or higher；bash git clone https://github.com/yourusername/dair-fedmoe.git；conda environment:；bash conda create -n dair-fedmoe python=3.8；conda activate dair-fedmoe；bash # For CUDA 11.8；conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
  - 关键文件：{"依赖环境": ["requirements.txt", "dair_fedmoe/simulation/federated_env.py"], "数据处理入口": ["dair_fedmoe/utils/dataset.py"], "训练入口": ["examples/train.py"], "配置文件": ["dair_fedmoe/config.py"]}
  - 数据集线索：ISCX、TOR、Tor、UNSW、USTC、VPN、dapt、iscx、tor、unsw、ustc、vpn

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

1

DAIR-FedMoE: Hierarchical MoE for Federated
Encrypted Traffic Classification under Compound
Drift
Shamaila Fardous, Kashif Sharif, Senior Member, IEEE, Fan Li, Member, IEEE, Ali Asghar Manjotho, and
Liehuang Zhu, Senior Member, IEEE

Abstract—Federated learning (FL) offers a decentralized,
privacy-preserving framework for encrypted traffic classification
(ETC), enabling network management and security. However,
real-world deployment of federated ETC faces compound clientspecific feature, concept, and label drift, which degrades model
performance. Existing ETC methods under FL settings typically address these drift types in isolation or partial combinations, overlooking their entanglement. Moreover, multiple-global
model and personalized FL approaches are computational and
communication expensive. To fill this gap, we propose DAIRFedMoE, a Drift-Adaptive, Imbalance-Aware, RL-Managed Federated Mixture-of-Experts framework to simultaneously handle
the drift triad with single-global model while minimizing the
computational and communication overhead. DAIR-FedMoE integrates a GShard Transformer with a hierarchical Mixtureof-Experts (MoE) layer that routes encrypsted flows to either
stable or drift-specialist experts based on per-client drift scores.
Within each expert, entropy-guided loss reweighting emphasizes low-confidence classes to address dynamic label imbalance.
Additionally, a reinforcement learning-based policy dynamically
manages the expert pool by spawning, pruning, and merging
experts, enabling efficient adaptation to evolving traffic patterns.
Experiments on federated splits of ISCX-VPN, ISCX-Tor, VNAT,
and USTC-TFC2016 show that DAIR-FedMoE achieves superior macro-F1, minority-class recall, and drift-recovery speed
compared to state-of-the-art baselines, while preserving privacy
and communication efficiency. The source code is available at
https://github.com/dairfedmoe/DairFM.
Index Terms—Federated Learning, Encrypted Traffic Classification, Distributed Concept Drift, Class Imbalance, Mixture-ofExpert, Reinforcement Learning.

I. I NTRODUCTION
FFECTIVE identification of traffic types and security
threats is essential for network management, intrusion
detection, and quality of service enforcement, particularly
in modern IoT and edge computing environments [15]. In
this context, federated learning has emerged as a promising
paradigm for ETC, offering a privacy-preserving alternative
to centralized training by enabling distributed model training

E

The work of Fan Li was supported in part by the National Natural ScienceFoundation of China (NSFC) under Grant 62372045. Co-corresponding
authors: K. Sharif and F. Li.
S. Fardous, K. Sharif, and F. Li are with the school of Computer Science
and Technology, Beijing Institute of Technology, China. (email: shamailafardous@bit.edu.cn, kashif@bit.edu.cn, fli@bit.edu.cn)
A. Manjotho is with the department of Computer Systems Engineering,
Mehran University of Engineering and Technology, Jamshoro, Pakistan.
(email: ali.manjotho@faculty.muet.edu.pk)
L. Zhu is with the School of Cyberspace Science and Technology, Beijing
Institute of Technology, Beijing, China (email: liehuangz@bit.edu.cn).

A B

A B

A B

Fig. 1: Drift entanglement scenario shown as drift event
timeline and global parameter response in a federated setting.

across edge clients without sharing raw data [20], [51]. Unlike
typical FL tasks, federated ETC faces highly non-independent
and identically distributed (non-IID) and volatile traffic patterns driven by diverse applications, encryption protocols, temporal behaviors, and regional policies [28]. These factors lead
to simultaneous and distributed drift across clients, as shown
in Fig. 1, each of five clients records feature drifts ∆P (X )
(green circles), concept drifts ∆P (Y|X ) (brown squares),
and label drifts ∆P (Y) (purple diamonds) from t0 to t8 ;
overlapping events (entanglement) are shaded in pink. The
Global Model row shows the aggregated parameter θ evolving
over time, with pronounced oscillations aligned to entanglement intervals. Bottom panels illustrate schematic examples
of each drift type: (1) feature drift, reflecting changes in
the feature marginal P (X ) (evolving encryption patterns); (2)
concept drift, as shifts in the conditional distribution P (Y|X )
(changing semantics of traffic behavior); and (3) label drift,
involving fluctuations in the label distribution P (Y) (varying
traffic class distribution). Such complex, client-specific drift
undermines model robustness and remains a central obstacle
in real-world federated ETC deployments.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

Existing approaches in federated ETC have attempted to
tackle these challenges with partial or specialized solutions as
summarized in Table I. For instance, FedPacket [3] and FLETC [51] apply FL protocols to encrypted packet features,
but do not account for temporal drift or client imbalance.
Other works like FedDrift [21] and FedCCFA [7] adapt general
FL frameworks to concept drift using confidence calibration
or entropy heuristics, yet they overlook label skew. Multiglobal model frameworks [9], [21], [41] and personalized
federated ETC approaches [11], [13], [14] aim to improve
client-specific adaptation by assigning dedicated models or
embedding personalized components, but they introduce significant computational, communication, and storage overhead.
To reduce this complexity, MoE models such as FedMoE-DA
[52] leverages task-specific expert routing. However, they typically rely on static expert configurations, lacking mechanisms
to grow, prune, or merge experts in response to evolving traffic.
As a result, these models often fail to generalize across diverse
clients or collapse under overlapping drift conditions.
Despite prior efforts, federated ETC continues to face two
critical challenges: (1) real-world deployments frequently encounter distributed and entangled drift (overlapping feature,
concept, and label drift across clients). Existing methods
typically address these drifts in isolation, failing to capture
their simultaneous and distributed nature. This complicates
targeted mitigation strategy and degrades model robustness,
fairness, and accuracy over time. To date, no existing model
has been proposed that explicitly detects and adapts to this
entangled drift despite its frequent occurrence in federated
ETC scenarios. Moreover, potential of MoEs in handling entangled drift has not been explored. (2) approaches that assign
clients to separate global models or introduce personalized
components improve local adaptation but incur significant
communication, storage, and coordination costs. These methods often rely on drift-prone client clustering and suffer from
reduced generalization, as each model is trained on a smaller
data subset.
To address the multifaceted challenges of distributed drift
and system efficiency in federated ETC, we propose DAIRFedMoE, a unified framework that jointly addresses feature,
concept, and label drift while ensuring scalability and privacy.
DAIR-FedMoE integrates a hierarchical Mixture-of-Experts
(HMoE) architecture within a GShard Transformer to perform
drift-aware expert routing, selectively isolating stable and
drifting traffic patterns. It leverages confidence-guided loss
reweighting to adapt to dynamic label imbalance by upweighting uncertain classes based on expert entropy, improving
robustness without manual tuning. To maintain a compact and
responsive model, DAIR-FedMoE introduces a reinforcement
learning-based policy that dynamically adjusts the expert pool
by spawning new specialists or pruning underutilized ones in
response to drift signals. These components work in concert to
ensure targeted drift adaptation, balanced learning, and adaptive capacity control, all within a single privacy-preserving
global model. To the best of our knowledge, this is the first
work to explore the potential of MoEs for drift adaptation
and to systematically study the impact of entangled drift in
federated ETC.

2

TABLE I: Coverage of distributed drift types in existing
federated learning literature.
Study

Joint
Drift
P (X , Y)

Feature
Drift
P (X )

Label
Drift
P (Y)

Concept
Drift
P (Y|X )

AC

TV

FairFedDrift [40]

✗

✗

✓

✓

✓

✓

FedStream [12]

✗

✗

Partial

✓

✓

✓

FAC-Fed [1]

✗

✗

✓

✓

✓

✓

FedDrift [21]

✓

✗

✗

✗

✓

✓

FedCCFA [7]

✗

✗

✓

✓

✓

✗

ConceptFL [33]

✗

✗

Partial

✓

✓

✓

EnsembleFL [6]

✓

✗

✗

✓

✓

✓

FedMoE-DA [52]
✓
✓
✗
✓
✓
✓
AC: Across Clients, TV: Time Varying, ✓:Full support, ✗: No support.

The main contributions of the paper are:
• We propose DAIR-FedMoE, a novel drift-resilient architecture for federated ETC that concurrently addresses
feature, concept, and label drift distributed across time
and clients. It incorporates a two-tier hierarchical MoE
within a GShard Transformer to route encrypted-flow
tokens based on drift type, while entropy-based loss
reweighting within each expert dynamically emphasizes
low-confidence (often minority) classes to mitigate imbalance.
• We develop a reinforcement learning-driven expert management strategy that dynamically adjusts the expert pool
in response to real-time drift and workload signals. A
server-side actor-critic policy learns to optimize model
capacity by monitoring expert usage, drift exposure, and
performance trends, enabling efficient spawning, pruning,
and merging of experts as traffic patterns evolve.
• We demonstrate effectiveness our unified framework
DAIR-FedMoE on federated splits of ISCX-VPN, ISCXTor, VNAT, and USTC-TFC2016, achieving significant
improvements in macro-F1, minority-class recall, and
drift-recovery speed, while preserving privacy and communication efficiency.
The remainder of the paper is organized as follows. Section II reviews related works. Section III introduces preliminaries and background. Section IV describes the threat model.
Section V presents the proposed DAIR-FedMoE method. Section VI provides experimental details and evaluation analysis.
Section VII concludes the paper. Additional baseline configurations and metric definitions are included in Appendices A
and B, computational complexity and overhead analysis in
Appendix C, and extended discussion of limitations and future
directions in Appendix D.
II. R ELATED W ORKS
A. Encrypted Traffic Classification
Encrypted traffic classification has evolved from traditional
port- and payload-based inspection to data-driven methods
that operate over statistical and flow-level metadata. Deep
learning approaches such as DeepPacket [31], FS-Net [26],

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

and FlowPic [42] extract discriminative features from raw or
transformed encrypted flows. More advanced models incorporate temporal patterns [24], [55] or inter-flow relations [19],
[44] to enhance semantic understanding. Recent trends explore
self-supervised pretraining [17], [25] and vision-inspired architectures [30]. Despite their expressiveness, these methods
typically rely on centralized training and assume stationary
traffic distributions.
In real-world settings, encrypted traffic evolves constantly
due to protocol changes, user behavior, and evasion tactics,
causing feature, concept, and label drift. Most ETC frameworks lack mechanisms to jointly detect and adapt to these
drifts, particularly in distributed, privacy-preserving settings
like federated learning. To address this, we propose a unified
framework that leverages mixture-of-experts and confidence
reweighting to adapt to simultaneous feature, concept and label
drifts over time.
B. FL with Heterogeneous & Evolving Traffic
FL has gained significant traction in ETC by enabling collaborative model training across edge devices without exposing
raw traffic data. Early efforts in federated ETC emphasize
protocol-agnostic feature learning without centralized access.
Works such as FedETC [20] and FedPacket [3] applied
standard FL protocols to encrypted traffic features, showing
initial success but limited robustness under non-IID client
distributions or evolving attack patterns. Several ETC-focused
frameworks integrate FL with MoE for computation and communication efficiency. For instance, Zec et al. [50] introduced a
gated fusion of global and local models to balance personalization and scalability. FedMix [49] employed client-specific gating to improve alignment of local updates. FedMoE-DA [52]
enabled dynamic expert routing across clients, enhancing both
efficiency and cross-client adaptation. Moreover, in domaintailored scenarios, Bai et al. [2] used weighted aggregation for
hospital-wise domain shifts in medical imaging. Sievers et al.
[46] applied FL-MoE to heterogeneous smart energy datasets.
Architecturally, FtMoE [29] adapted expert assignment via
task-aware transfer learning for image classification.
While existing FL-MoE approaches enhance personalization, scalability, and robustness, they overlook entangled drift,
the simultaneous and interacting shifts in feature, concept,
and label distributions, where conventional detection and
adaptation often fail. In contrast, DAIR-FedMoE is the first
unified framework tailored for ETC under such complex drift
scenarios, enabling dynamic, fine-grained adaptation across
clients and time while maintaining privacy and communication
efficiency.

3

Label drift, prevalent in ETC due to class imbalance from
underrepresented attack types or services, is mitigated using
oversampling [34] or fairness-aware aggregation [16]. To handle co-occurring drifts, recent methods combine augmentation,
memory replay, and ensemble learning. These include hybrid
rehearsal strategies [36] and class-wise MixUp/AugMix [22].
Ensemble- and stream-adaptive techniques [45], [53] further
boost resilience under evolving, imbalanced conditions.
Despite these advances, most methods treat drift types
in isolation or in limited combinations, overlooking their
joint entanglement, where feature, concept, and label drift
interact simultaneously and non-linearly across clients and
time. DAIR-FedMoE addresses this by integrating entropydriven class reweighting and modular expert routing to adapt to
compound drifts in a unified, scalable, and privacy-preserving
framework.

III. P RELIMINARIES
A. Federated Learning (FL)
FL is a decentralized paradigm that enables multiple clients
to collaboratively train a global model without exposing their
raw data [35]. Each client ck holds a private dataset Dk and
performs local updates to a shared model parameters θ, which
are then aggregated by a central server. The global objective
is to minimize the weighted sum of local loss functions as
expressed in (1).
min
θ

K
X
|Dk |
k=1

|D|

Lk (θ),

(1)

where |Dk | and |D| are the total number of samples with client
k and across all clients, respectively and K is the total number
of participating clients.

B. Mixture-of-Experts (MoE)
MoE is a modular neural architecture designed to improve
model capacity and specialization while maintaining computational efficiency [43]. It consists of a collection of expert
subnetworks and a gating mechanism that routes each input
to a subset of these experts, enabling sparse activation and
dynamic inference. Given an input x, the output of an MoE
layer is a weighted combination of the top-k selected experts:
X
MoE(x) =
gi (x) · Ei (x),
(2)
i∈S

C. Drift Adaptation in Federated Learning
Drift handling in FL has largely focused on individual drift
types through global or sample-level adjustments. Concept
drift is commonly addressed via entropy-based scoring or
confidence calibration, as in FedDrift [21] and FedCCFA
[7], while FedBSS [2] applies bias-aware training schedules
for sample-specific adaptation. Feature drift is tackled in
methods like pMixFed [39] using interpolation strategies.

where S denotes the set of selected experts, gi (x) is the
gating score, and Ei (x) is the output of expert i. However,
traditional MoE architectures do not inherently handle timevarying data distributions or dynamic class imbalance, as the
gating decisions are typically static and agnostic to temporal
drift or class-wise uncertainty. This limits their robustness in
non-stationary environments where traffic semantics and class
distributions evolve over time.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

C. Differential Privacy (DP)
In the context of federated learning, DP is a privacyenhancing technique employed to ensure that model updates
do not leak private information from any client’s local dataset.
A randomized algorithm A is said to satisfy (ε, δ)-differential
privacy if, for any two neighboring datasets D and D′ differing
by at most one sample, and for any subset of outputs S as
defined in (3).
P[A(D) ∈ S] ≤ eε · P[A(D′ ) ∈ S] + δ,

(3)

where ε measures the privacy loss and δ accounts for a small
probability of failure. The DP is implemented by injecting
zero-mean Gaussian noise into the clipped local gradient
before sending it to the server as expressed in (4).
e k = clip(∇Lk , C) + N (0, σ 2 I),
∆

(4)

e k is the DP preserved local update for client k, C is
where ∆
the clipping bound to limit sensitivity, and σ controls the noise
scale.
IV. T HREAT M ODEL
We consider a semi-honest adversary in our federated
encrypted traffic classification setup, where a central server
orchestrates a hierarchical MoE across distributed clients.
The adversary may corrupt some clients or observe aggregated updates. Such an adversary has full knowledge of
our GShard Transformer backbone, hierarchical MoE gating
logic, PPO policy network, hyperparameters (including drift
thresholds, gating dimensions, and clipping norms), and even
the differential-privacy noise distribution, but never accesses
raw packet data or internal client states. Its objectives include:
(1) inferring properties of individual flows or rare attack
classes by analyzing expert- and gate-parameter updates and
confidence summaries, (2) mounting membership-inference
attacks to determine whether specific flows were used in
training, and (3) reconstructing feature vectors and tracking
drift events through routing and lifecycle decisions.
To mitigate these risks, we employ DP-SGD, a widely validated technique that offers strong formal privacy guarantees
while preserving high model performance [10], [38]. To ensure
that our privacy claims are transparent and reproducible, we
explicitly report the inputs used for privacy accounting under
DP-SGD. At each client, we apply per-sample gradient clipping with norm bound C to all trainable components updated
locally, including the shared encoder, expert parameters, and
gating networks, and add Gaussian noise N (0, σ 2 C 2 I) to the
clipped gradients before the local optimizer step. The resulting
model updates are shared only via secure aggregation. Let B
denote the local minibatch size and |Dk | the local dataset size,
yielding a per-step sampling rate q = B/|Dk |; with E local
epochs per round and T federated rounds, the total number
of composed DP steps per client is Sk = T · E · ⌈|Dk |/B⌉.
We compute the overall privacy budget (ε, δ) using a standard Moments Accountant for the (subsampled) Gaussian
mechanism with the above (q, σ, C, Sk ), fixing δ = 10−5
in our experiments (with B = 32, E = 5, and T = 250
unless stated otherwise). Together, differential privacy, secure

4

aggregation, constrained confidence reporting, and threshold
obfuscation prevent adversaries from inferring sensitive traffic
patterns, client membership, or concept-drift behavior from
model updates.
All server-side operations in DAIR-FedMoE, including hierarchical routing, drift-aware expert selection, and PPO-based
expert lifecycle management (expert spawning, pruning, and
merging), operate solely on differentially private aggregated
updates. By the post-processing property of differential privacy, these operations do not weaken the underlying (ε, δ)-DP
guarantee.
Routing and Side-Channel Considerations. DAIR-FedMoE
does not transmit per-client routing decisions, drift scores,
or expert selection indicators to the server. The server observes only secure-aggregated (optionally expert-partitioned)
model updates, without access to client identities or expert
usage frequencies. Consequently, while aggregated updates
may reflect population-level traffic evolution, routing behavior
and drift states cannot be attributed to individual clients,
and expert lifecycle decisions operate solely on differentially
private aggregates.
V. M ETHOD
A. Problem Formulation
In a federated encrypted traffic classification problem, we
consider K clients and a central server. Client k holds a
private dataset Dkt at round t, sampled from a joint distribution
Pkt (X , Y) over encrypted-flow features X ∈ Rd and labels
Y ∈ {1, . . . , C}. The objective is to learn model parameters
θ of a mixture-of-experts classifier:
fθ (x) =

M
X

gj (x) Ej (x)

j=1

by minimizing the federated empirical risk:
min
θ

K
X
k=1



|Dt |
P k t E(x,y)∼Dt ℓ fθ (x), y
k
ℓ |Dℓ |

In real-world encrypted traffic, the feature distribution
Pk (X ), the label distribution Pk (Y), and the conditional
distribution Pk (Y|X ) often evolve over time, a phenomenon
collectively referred to as feature drift, label drift, and con(t)
cept drift, respectively. Formally, at round t: Pk (X ) ̸=
(t−1)
(t)
(t−1)
(t)
Pk
(X ) ∧ Pk (Y) ̸= Pk
(Y) ∧ Pk (Y|X ) ̸=
(t−1)
Pk
(Y|X ).
In federated settings, these drifts may also differ across
(t)
(t−1)
(t)
(t−1)
clients, i.e., Pi (X ) ̸= Pj
(X ) ∧ Pi (Y) ̸= Pj
(Y) ∧
(t)
(t−1)
Pi (Y|X ) ̸= Pj
(Y|X ) for i ̸= j, which we denote as
distributed drift. A robust federated classifier must therefore
adapt simultaneously to all three types of drift across time and
clients. In this work, we consider a synchronous FL setting,
where all clients participate in each communication round
and updates are aggregated by the central server. However,
clients experience asynchronous and overlapping drift events
at different times and with different intensities across clients.
While the federated training proceeds in synchronized rounds,

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

5

YES

NO

YES

NO

Fig. 2: Overview of the DAIR-FedMoE framework. (a) GShard Transformer backbone in which each MoE layer is replaced by a
hierarchical Mixture-of-Experts (HMoE) sublayer. (b) Server-side HMoE pipeline, where encrypted-flow embeddings are scored
for drift, smoothed, and routed by a root gate to stable or drift-specialist experts; model updates are aggregated federatively and
expert spawning, pruning, and merging are controlled by a PPO-based policy. (c) Client-side workflow, where local drift scores
guide hierarchical routing, adaptive confidence-based loss reweighting is applied during training, and differentially private
expert and gate updates with confidence summaries are returned to the server.

the distributional shifts are modeled as continuous and clientspecific, reflecting real-world non-stationary traffic environments.
B. Overview of DAIR-FedMoE Framework
The overall workflow of DAIR-FedMoE, built upon a
GShard transformer backbone, is shown in Fig. 2. DAIRFedMoE extends a GShard Transformer by embedding driftaware expert trees and confidence-guided loss reweighting into
MoE layer. In each federated round, the server broadcasts
latest expert shards, gating networks and global confidence
coefficients to all clients. Each client then detects local concept
drift on its encrypted-flow data, routes inputs to either stable or
drift experts, and trains experts using class-confidence weights.
During local training, each expert maintains a running average of its softmax entropy to estimate class confidence. The
class confidence coefficients are updated at the end of every
local epoch and later averaged across clients to form global
weights. Clients convert these scores into weights for the
cross-entropy loss, up-weighting rare or uncertain classes to
handle class imbalance, and backpropagate gradients through
both experts and gating networks. After local updates, clients
performs differential privacy and return updated parameters
and revised confidence summaries back to the server, which
aggregates them via weighted FedAvg. Moreover, a reinforcement learning-based policy network on the server monitors
expert utilization and drift trends to manage the life cycle
of experts and to keep capacity aligned with evolving data.
The expert lifecycle management is triggered once per communication round to maintain alignment with traffic evolution

and system capacity. This seamless integration of a GShard
transformer backbone, drift-aware routing, confidence-guided
loss reweighting and RL-managed expert lifecycle underpins
the adaptability and robustness of DAIR-FedMoE in handling
label concept drift and class imbalance simultaneously.
C. GShard Transformer Backbone
The DAIR-FedMoE framework is built on the GShard
transformer architecture of Lepikhin et al. [23]. We replace
the standard MoE layer with our Hierarchical MoE (HMoE)
layer, while retaining the multi-head self-attention, layer normalization, and feed forward network components, resulting in a sparse and drift-aware attention architecture. Each
encrypted-flow session x (byte sequence) is first tokenized
into a sequence of embeddings enriched with sinusoidal positional encodings. These embeddings represent fixed-length
vectorized representations of individual byte chunks derived
from the raw encrypted flow, capturing both structural and
statistical characteristics of the traffic. The resulting token
sequence is then passed through a stack of L transformer
blocks. Within each block, multi-head self-attention is applied
to the tokens, followed by the HMoE layer where a twotier gating mechanism guided by per-token drift scores routes
tokens to either stable experts or drift-specialist experts. The
updated embeddings entering the HMoE layer are denoted
by h. After routing and expert processing, these outputs pass
through a standard feed-forward network. Furthermore, residual connections and layer normalization follow every sublayer
to ensure stable training at scale, and the final representation

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

of the [CLS] token is fed into a two-layer MLP classification
head with a softmax output to produce the class logits. In each
communication round t, the GShard transformer is partitioned
into shards, with client k receiving Shardk .
D. Hierarchical Mixture-of-Experts (HMoE) layer
In DAIR-FedMoE, the HMoE layer groups experts into
two regimes, stable and drift, and uses a two-level gating
mechanism to route encrypted-flow samples. Each sample is
first assigned a drift score and sent to the root gate, which
chooses between the stable or drift regime. A second, regimespecific gate then selects the specialist expert within that
regime. This two-tier structure isolates evolving traffic patterns
for rapid adaptation while preserving stable behavior.
Local Drift Detection Mechanism. To support the top-level
routing in our expert tree, each client computes a local drift
score for every incoming feature vector. This score quantifies how much the current encrypted-flow distribution has
shifted relative to historical observations, allowing the model
to distinguish between consistent and drifting traffic before
classification.
At each communication round t, client k first evaluates
a drift score dk (h) for each encrypted-flow feature vector
embedding h. This score measures the divergence between
two empirical feature distributions over a sliding window of
size W , as
Pkt,hist =

1
W

t−1
X



Eh∼Dks δ(h)

(5)

s=t−W



Pkt,curr = Eh∼Dkt δ(h) ,

(6)

where δ(h) denotes the Dirac mass at h. We employ the
Jensen-Shannon divergence to quantify the shift, as

dk (h) = JS Pkt,curr ∥Pkt,hist
(7)


= 21 KL Pkt,curr ∥M + 12 KL Pkt,hist ∥M ,
t,curr
1
+ Pkt,hist ).
2 (Pk

with M =
In practice, both distributions are estimated via Gaussian kernel density estimates
over packet payload to ensure efficiency on edge devices. To
reduce noise in the drift score, we further employ exponential
smoothing as defined in (8).
d˜k (h) = α d˜kt−1 (h) + (1 − α) dk (h)

(8)

Here α ∈ [0.9, 0.99] is a smoothing factor, selected via a small
grid search over {0.90, 0.95, 0.99} on a held-out validation
split. This range follows widely adopted conventions in ML
for EMA-based modules [5], balancing responsiveness to drift
with stability against transient noise. The normalized score
d˜k (h) is then concatenated with the feature embedding h and
fed into the root gating network. Samples with high d˜k (h)
are routed to drift-specialist experts, while those with low
scores proceed to stable experts, forming the foundation of
our hierarchical MoE.
Furthermore, we explicitly decouple representation drift
from input data drift. At round t, both the historical and
current windows are re-embedded using the same encoder

6

snapshot Et (·) before computing the JS divergence, preventing
confounding from encoder-update–induced embedding shifts.
The drift score is smoothed over time, and routing is learned
via the hierarchical gate (adaptive probabilities), rather than
using a fixed threshold.
Root Gating Network Design. The root gating network is
responsible for determining whether an input sample should
be routed through stable or drift experts. It takes as input the
feature embedding h ∈ Rdk of the encrypted-flow vector and
the normalized drift score d˜k (h) ∈ [0, 1], where dk is the
embedding dimension. These are concatenated into the vector,
as defined in (9).


h
z= ˜
∈ Rdk +1
(9)
dk (h)
This vector is then passed through a two-layer multilayer
perceptron to produce routing probabilities r = [rstable , rdrift ].
Here rstable and rdrift denote the probabilities of routing to the
stable or drift regime, respectively. The root gate’s parameters
are updated jointly with all other components via backpropagation through the hierarchical MoE loss.
Stable vs. Drift-Specialist Expert Routing. DAIR-FedMoE
employs a two-tier expert routing mechanism by explicitly
partitioning the total expert pool into two non-overlapping
subsets: stable experts and drift-specialist experts. This disjoint
design allows the model to isolate and preserve stable behavioral patterns while simultaneously adapting to evolving traffic
distributions. Based on this structure, after computing the root
gate probabilities r, each input sample is routed through the
branch with the higher activation score. If rstable ≥ rdrift , the
feature embedding h is forwarded to the stable-regime gate;
otherwise, it is directed to the drift-regime gate. Each regimespecific gate then applies a softmax over its corresponding
subset of experts, as defined in (10) and (11), to select the
most appropriate expert within that regime.
g S = softmax(Ws h + bs )

(10)

g D = softmax(Wd h + bd )

(11)

Here g S ∈ ∆l−1 indexes l stable experts and g D ∈ ∆m−1
indexes m drift experts. Here, Ws , Wd and bs , bd are the
corresponding weights and biases. A hard routing selects
expert j ∗ = arg maxj gjr .
Expert Network Architectures. Each expert Ej is a
lightweight classifier mapping h ∈ Rdk to class logits in RC .
In our implementation, all experts share a uniform two-layer
fully-connected architecture followed by a softmax to obtain
class probabilities. Dropout and batch normalization layers
are used in between for regularization. Although stable and
drift experts use the same architecture, their parameters are
updated using different client-data subsets as determined by
the hierarchical routing mechanism.
E. Adaptive Loss Reweighting via Expert Confidence
Following expert selection through hierarchical routing,
we further enhance per-expert learning by addressing class
imbalance within each expert’s data distribution. To this end,
we introduce an adaptive loss reweighting mechanism that

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

leverages per-class confidence estimates. By dynamically scaling the contribution of each class to the loss function based on
the expert’s predictive certainty, under-represented or harderto-classify classes receive greater emphasis. This improves the
model’s ability to maintain balanced performance, particularly
under drifting or skewed label distributions.
Per-Expert Confidence Estimation. For each expert Ej , we
first compute the predictive distribution pj (h) ∈ ∆C−1 over
C classes for samples h routed to that expert. The per-sample
Shannon entropy Hj (h) quantifies the expert’s uncertainty as
expressed in (12).
Hj (h) = −

C
X

pj (h)c log pj (h)c

(12)

c=1

To derive class-specific statistics, we average these entropies
over a sliding window of the most recent samples Bj,c with
true label c defined as in (13).
X
1
Hj (h)
(13)
H j,c =
|Bj,c |
h∈Bj,c

We then update an exponential moving average (EMA) of
these values to smooth temporal fluctuations, as
(t)

(t−1)

H̃j,c = α H̃j,c

+ (1 − α) H j,c ,

(14)

where α ∈ [0.9, 0.99] is a smoothing factor. Finally, we normalize the EMA-entropy scores into a confidence coefficient
ϕj,c in [0, 1] as computed in (15).
ϕj,c = 1 −

H̃j,c
maxc′ H̃j,c′

(15)

A lower ϕj,c indicates that expert Ej is less certain on
class c, directing subsequent loss reweighting to prioritize that
class. These entropy-based confidence scores are computed
independently on each client and subsequently averaged across
clients to obtain global confidence estimates. The aggregated
values {ϕj,c } are then communicated to the server along with
the model updates and are used in the following round to
compute class-wise loss weights.
Entropy-Based Weight Computation. Given the smoothed
confidence coefficients ϕj,c ∈ [0, 1] for expert Ej and class c,
we derive per-class weights wj,c by inverting confidence, as
wj,c =

1
,
ϕj,c + ε

(16)

where ε > 0 is a small constant to prevent division by zero.
Intuitively, lower confidence ϕj,c yields higher weight wj,c ,
thus emphasizing harder or under-represented classes. To avoid
extreme values that could destabilize training, we clip wj,c into
a bounded interval [ωmin , ωmax ].
Incorporation into Local Loss Function. During each
client’s local update, routed samples (xi , yi ) assigned to expert
Ej incur a weighted cross-entropy loss, as defined in (17).
X

1
Lk =
wj,yi ℓ Ej (h), yi
(17)
|Dk |
(hi ,yi )∈Dk

Here Dk is the local dataset at client k, wj,yi is the weight
for the true label yi , and h is the embedding for feature xi .

7

Gradients computed from Lk backpropagate through both the
expert network Ej and its upstream gating modules, ensuring
that high-weight (low-confidence) classes receive proportionally greater parameter updates.
To enforce differential privacy, each client applies DP to its
local parameter deltas as defined by (4). The same procedure
(k)
is applied to the gating updates ∆G· . Only the privatized up˜ (k) , ∆G
˜ (k)
dates {∆E
· } and the updated confidence summaries
j
are transmitted to the server.
F. RL-Based Expert Lifecycle Management
In DAIR-FedMoE, the server employs a reinforcement
learning (RL) agent to manage the set of active experts so
that model capacity continuously aligns with evolving traffic
patterns, as shown in Fig. 3. This includes, pruning underutilized networks, spawning new drift specialists, and merging
redundant experts. We formalize this as a Markov Decision
Process (MDP) and train a lightweight policy network to
optimize long-term classification performance and resource
efficiency. We define the MDP at federated round t as follows:
State st : A real-valued vector concatenating:
M
• Expert utilization rates {ūj }j=1 , where ūj is the average
gating probability of expert j over the past R rounds.
• Drift engagement {δj }, the fraction of samples routed to
each drift expert versus stable experts.
• Confidence profiles {ϕj,c } averaged across classes.
• Performance deltas ∆F1t and ∆DRt , the changes in
macro-F1 and drift-recovery speed between rounds t − 1
and t.
• Expert ages {aj }, the number of rounds since each expert
was created or last merged.
Action at : A discrete choice from the set A =
{Prune(j), Spawn(k), Merge(j1 , j2 ), NoOp}, where:
• Prune(j) removes expert j.
• Spawn(k) creates a new drift expert initialized from
drift-cluster centroid k.
• Merge(j1 , j2 ) combines experts j1 and j2 by averaging
their weights.
• NoOp leaves the expert pool unchanged.
Reward rt : We craft a scalar reward rt balancing classification
gains and model complexity as defined in (18).
rt = ∆F1t + λd ∆DRt − µ|∆Mt |

(18)

Here ∆Mt is the change in total expert count, and λd , µ >
0 weight the drift-recovery improvement and expert-count
penalty.
Policy Network Architecture. We implement a shared actorcritic network that processes the MDP state st through two
hidden layers. From the second layer, the policy head produces
action probabilities πθ (at |st ) and the value head estimates the
state value Vϕ (st ). The policy parameters are denoted by θ
and the value parameters by ϕ.
During each federated round, the server collects transitions (st , at , rt , st+1 , log πθold (at |st )) into an replay buffer.
Every U rounds, the policy is updated using the Proximal
Policy Optimization (PPO) clipped-surrogate objective. For

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

8

Algorithm 1 One Federated Training Round of DAIRFedMoE
(t)

broadcasts experts {Ej }M
j=1 , gating nets
(t)
(t)
(t)
(t)
Gr , Gs , Gd and confidences {ϕj,c }
2: for each client k ∈ St in parallel do
(t)
3:
for each minibatch B ⊂ Dk do
4:
Initialize local loss Lk ← 0
5:
for each (xi , yi ) ∈ B do
6:
Compute embedding h = Shardk (xi )
7:
Compute drift score dk (h)
8:
Perform EMA smoothing d˜k (h)
(t)
9:
[rstable , rdrift ] ← Gr ([h; d˜k (h)])
10:
if rstable ≥ rdrift then
(t)
11:
g ← Gs (h)
12:
else
(t)
13:
g ← Gd (h)
14:
end if
15:
j ∗ ← arg maxj gj
16:
Compute entropy Hj ∗ ,yi , update EMA H̃j ∗ ,yi
17:
Compute ϕj ∗ ,yi
18:
wj ∗ ,yi ← clip(1/(ϕj ∗ ,yi + ε), ωmin , ωmax )
(t)
19:
Lk + = wj ∗ ,yi ℓ(Ej ∗ (h), yi )
20:
end for
(k)
(k)
(k)
(k)
21:
Backprop. Lk , get ∆Ej , ∆Gr , ∆Gs , ∆Gd
22:
end for
23:
Client k applies DP as defined in (4)
˜ (k) ˜ (k) (k) }
˜ (k) , ∆G
˜ (k)
24:
Client k sends {∆E
r , ∆Gs , ∆Gd , ϕ
j
to server
25: end for
26: Server aggregates:
X |Dk |
(t+1)
(t)
˜ (k) )
P
Ej
=
(Ej + ∆E
j
|D
|
ℓ
ℓ
1: Server

Fig. 3: Architecture of the PPO-based expert lifecycle management module in DAIR-FedMoE.
each sampled minibatch, we compute the advantage estimates
Ât = R̂t − Vϕ (st ), where R̂t are the empirical returns. The
actor is trained by minimizing objective function as defined
in (19), while the critic is trained by minimizing the valuefunction loss as expressed in (20).
LPPO (θ) = −E[ min(Ât πθ (at |st )/πθold (at |st ),
clip(rt (θ), 1 − ϵ, 1 + ϵ) Ât )]
LVF (ϕ) = E[(Vϕ (st ) − R̂t )2 ]

(19)
(20)

Further to encourage exploration, we add an entropy bonus
Lent = −E[H(πθ (·|st ))]. We perform NPPO epochs of gradient
descent on the combined loss, as expressed in (21), using
separate learning rates for actor and critic. After updating, we
set θold ← θ before the next optimization cycle.
L = LPPO + cvf LVF + cent Lent ,

(21)

where cvf > 0 and cent > 0 scale the value-function loss
and entropy bonus, respectively. After completing the PPO
updates, we set θold ← θ before the next optimization cycle.
G. Federated Training Protocol
This section describes the federated training routine of
DAIR-FedMoE, which proceeds iteratively across communication rounds. Each round consists of three phases: server
broadcast, client-side local updates, and server aggregation
with expert policy invocation, as detailed in Algorithm 1.
At the beginning of round t, the server broadcasts the
current expert parameters, gating networks, and global confidence coefficients to all participating clients (line 1).
Each client k then processes its local minibatches in parallel
(lines 2-3). For each input sample, it extracts features
using a shared encoder (line 6), computes a drift score
(line 7), and applies EMA smoothing to obtain d˜k (h)
(line 8). These scores are passed to the root gating function
to obtain regime probabilities (line 9), which determine
whether the sample is routed through the stable or driftsensitive gate (lines 10-13).
Each expert Ej then outputs class scores, which are combined using the gate weights gj to compute soft predictions. The predicted class is selected (line 14), and its
entropy is computed and used to update the EMA of uncertainty (line 15). This entropy is used to derive the

k∈St

27: For Gr , Gs , Gd aggregate high-drift clients
28: Construct RL state st :

st = [{ūj }M
j=1 , δj , ϕj,c , ∆F1t , ∆DRt , aj ]
29: Sample action at ∼ πθ (·|st )
30: Execute action at ∈ {Prune, Spawn, Merge, NoOp}
(t+1)

31: Update expert set {Ej

}

adaptive loss weight and the clipped final weight is computed
(lines 16-17). Each client’s objective accumulates the
weighted cross-entropy loss (line 18), and gradients are
backpropagated through the expert and gating layers to obtain
local updates (line 20).
Before sending the updates back to the server, clients
apply differential privacy noise and transmit the privatized
updates (lines 22-23). Upon receiving updates from all
clients, the server aggregates them across the population
(lines 25-26) and forms an RL state vector based on drift
exposure and recent performance (line 28). The PPO policy
samples an action and executes it to adjust the expert pool
(e.g., spawn, prune, merge, or NoOp), concluding the round
(t+1)
with the updated expert set {Ej
} (lines 29-31).

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

Algorithm 2 Inference with DAIR-FedMoE
Require: Trained experts {Ej }, gates Gr , Gs , Gd
Require: Single encrypted-flow x
1: Extract features h = Shardk (x)
˜
2: Compute drift score d(h), EMA
 smoothed d(h)
˜
3: [rstable , rdrift ] ← Gr [h; d(h)]
4: if rstable ≥ rdrift then
5:
g ← Gs (h)
6: else
7:
g ← Gd (h)
8: end if
9: Compute final class probabilities:
X
p(c) =
gj [ softmax(Ej (h)) ]c
j

10: return arg maxc p(c)

H. Inference with DAIR-FedMoE
Algorithm 2 outlines the inference procedure of DAIRFedMoE for a single encrypted-flow input. First, the encrypted
input is transformed into feature representation via Shard
encoder (line 1). The drift score is then computed and
smoothed using an EMA filter (line 2), and routing scores
are derived using the routing gate Gr (line 3). Based on
the relative strengths of stable and drift indicators, the input
is routed either to the stable gate Gs or the drift-sensitive
gate Gd (lines 4-8). Each expert’s output is weighted
by the selected gating policy and aggregated to compute the
final class probabilities (line 9). The class with the highest
probability is returned as the predicted label (line 10).
VI. E XPERIMENTAL D ETAILS & E VALUATION A NALYSIS
A. Implementation Details
The DAIR-FedMoE framework is implemented using PyTorch 1.12 for model construction, Flower 0.19 for federated
orchestration, and Ray RLlib 1.8 for reinforcement learning.
All experiments are conducted on a Windows 11 24H2 system
equipped with dual NVIDIA V100 GPUs and 128 GB RAM.
Clients are simulated in CPU-only Docker containers to emulate edge deployments. All source code, pretrained models,
and configuration files will be publicly released.
We set the drift estimation window to W = 500 samples
and use an EMA smoothing factor α = 0.95. Confidence
weights are clipped to the interval [ωmin , ωmax ] = [1.0, 5.0].
The GShard Transformer backbone comprises L = 12 transformer blocks with hidden dimension dk = 512, 8-head selfattention, and a feed-forward expansion factor of 4. Each
HMoE sublayer includes l = 4 stable experts and m = 4 drift
experts, each implemented as a two-layer MLP with hidden
size He = 512. Gating networks use a hidden size Hg = 128.
Clients perform 5 local epochs per round with batch size 32,
using Adam optimizer with a learning rate of 10−3 for both
expert and gate modules. The PPO-based policy network for
expert lifecycle management has two hidden layers of size
Hp = 256. We set the PPO clip parameter ϵ = 0.2, valuefunction loss coefficient cvf = 0.5, entropy bonus coefficient

9

cent = 0.01, and perform NPPO = 4 optimization epochs per
update. The actor and critic use learning rates of 5 × 10−4
and 10−3 , respectively. The RL reward formulation (Eq. 18)
includes weights λd = 2.0 for drift-recovery improvement and
µ = 0.5 for expert-count regularization. These hyperparameters are tuned via grid search on a held-out validation split to
balance stability and performance.
To enforce (ϵ, δ)-differential privacy, each client clips gradient norms to C = 1.0 and adds Gaussian noise with
standard deviation σ = 1.2. The Moments Accountant tracks
cumulative privacy loss, ensuring δ = 10−5 over T = 250
communication rounds.
All clients run in CPU-only Docker containers to emulate
resource-constrained edge devices; we report per-round client
wall-clock time and memory usage collected on these CPUonly clients to reflect edge-side costs. This setup isolates
server-only components (global aggregation and PPO policy
updates) from client compute, mirroring a practical FL deployment where clients are low-power nodes and the server
has ample resources.
B. Baseline Solutions & Evaluation Metrics
We benchmark DAIR-FedMoE against representative baselines covering (i) strong centralized ETC backbones, including
FS-Net [26], FlowPic [42], DeepPacket [31], and Flow-GNN
[19]; (ii) federated ETC methods that primarily address privacy and decentralization but do not explicitly model drift,
including FedETC [20], FL-ETC [51], FedPacket [3], and BCFLETC [28]; and (iii) drift-aware or continual/fair FL baselines, including FedDrift [21], FedCCFA [7], FedIBD [18],
Cross-FCL [54], Master-FL [47], FairFedDrift [40], FedMoEDA [52], FairINC [8], and FedStream [12]. Implementation
details and configuration choices for all baselines follow their
original descriptions and are summarized in Appendix A.
We report Macro-F1 as the primary metric, along with
macro-precision, macro-recall, overall accuracy, minority-class
recall (bottom 25%), and drift-recovery score. Communication
cost, runtime overhead, expert-pool dynamics, and privacy
budget consumption are also evaluated; formal definitions
appear in Appendix B.
C. Datasets and Federated Splits
For evaluating DAIR-FedMoE framework, we consider four
widely-used encrypted-traffic benchmarks. The ISCX VPNnonVPN dataset comprises 14 traffic categories (e.g., VOIP,
P2P, HTTP) captured in both VPN and non-VPN sessions,
with flow-level statistics extracted via ISCXFlowMeter. The
ISCX Tor-nonTor dataset contains labeled PCAPs and flow
features for Tor-routed and direct traffic across 10 application classes. The VPN/Non-VPN Network Application Traffic
(VNAT) dataset comprises 165 PCAP files (82 VPN, 83 nonVPN) spanning 10 applications, totaling 36.1 GB of encrypted
and clear-text flows. Lastly, the USTC-TFC 2016 dataset [48]
comprises 20 classes, with an equal split between benign
encrypted traffic (e.g., Gmail, Facebook) and malware traffic
(e.g., Rbot, Virut), all encrypted via SSL/TLS. It is highly

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

ISCX-VPN under Dir(0.1)
2000
1000

Classes

0 1 2 3 4 5 6 7 8 910111213141516171819
Clients
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15

Classes

0
1
2
3
4
5
6
7
8
9
10
11

0

ISCX-Tor under Dir(0.1)
2000
1000

0 1 2 3 4 5 6 7 8 910111213141516171819
Clients

0
1
2
3
4
5
6
7
8
9
10
11

0

0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15

1000

Classes

USTC-TFC2016 under Dir(0.1)

01
23
45
67
89
10
11
12
13
14
15
16
17
18
19

0

1000
500

ISCX-Tor under Dir(0.5)
1500
1000
500

0 1 2 3 4 5 6 7 8 910111213141516171819
Clients

01
23
45
67
89
10
11
12
13
14
15
16
17
18
19

of flows from their dominant temporal segment and 20%
distributed across remaining segments. This yields 28003200 flows per client with both application preference
and temporal variations.
• USTC-TFC2016 contains 10 malware families and 10
benign categories. We implement hierarchical partitioning by grouping data into three threat severity levels.
Each client k samples severity preferences using ω k ∼
Dir(αt = 0.6) and receives 75% of flows from their
preferred level, with 25% from others. Within each severity group, we apply Dirichlet(α = 0.5) over constituent
classes to induce label heterogeneity. This produces 35004000 flows per client, capturing threat-level specialization
and class distribution differences.
D. Drift Injection Protocol

1000

1000
500

0 1 2 3 4 5 6 7 8 910111213141516171819
Clients

Fig. 4: Client-wise class distributions under Dirichlet non-IID
partitions for each dataset. Heatmaps show per-client class
sample counts for α = 0.1 (left, stronger heterogeneity) and
α = 0.5 (right, milder heterogeneity). Lower α induces sharper
class skew across clients, simulating distributed label drift.

imbalanced, making it ideal for evaluating models under
minority class scarcity.
We implement dataset-specific partitioning strategies to
simulate realistic non-IID conditions across federated clients.
These approaches ensure heterogeneous data distributions
while maintaining experimental validity.
For ISCX-VPN with 12 application classes, each client k
receives flows according to probability vector π k sampled
from a Dirichlet distribution over application categories.
Local data stores remain fixed throughout training rounds
to ensure reproducible conditions.
• ISCX-Tor contains 30 composite classes (15 applications
× 2 routing modes). We sample a 30-dimensional Dirichlet distribution for each client, allocating 3000-4500 flows
based on the resulting probabilities over the composite
class space.
• For VNAT with 20 Android VPN application categories,
we employ two-stage partitioning to capture mobile usage
patterns. We first sample application preferences using
Dirichlet(α = 0.5), as shown in Fig. 4, then introduce
temporal heterogeneity via four time-based segments with
weights ω k ∼ Dir(αt = 0.4). Each client receives 80%
•

10

2000

USTC-TFC2016 under Dir(0.5)

2000

0

0
1
2
3
4
5
6
7
0 1 2 3 4 5 6 7 8 910111213141516171819
Clients

1000

0 1 2 3 4 5 6 7 8 910111213141516171819
Clients

Classes

2000

0 1 2 3 4 5 6 7 8 910111213141516171819
Clients

1500

VNAT under Dir(0.5)

Classes

Classes

VNAT under Dir(0.1)
0
1
2
3
4
5
6
7

ISCX-VPN under Dir(0.5)

0 1 2 3 4 5 6 7 8 910111213141516171819
Clients

Classes

Classes

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

Malekghaini et al. [32] show that encrypted traffic exhibits
time-evolving drift, where even well-curated labeled data
can become irrelevant within six months due to changes in
protocols, software, and devices. Using ISP datasets, they
show 35.7%–41.1% performance decay as the train-test gap
reaches two years, driven by protocol evolution such as
>83.3% growth in HTTP/2 and declining SPDY usage. These
observations support our simulator’s assumptions that drift
is asynchronous, heterogeneous in timing and duration, and
variable in severity, reflecting protocol updates and traffic
shifts. Accordingly, we use randomized start rounds, durations,
magnitudes, and abrupt/gradual modes to capture months-toyears drift horizons, ensuring realistic patterns consistent with
empirical measurements.
To evaluate DAIR-FedMoE under realistic compound drift,
we adopt a stochastic, client-specific drift simulator that
generates asynchronous and entangled drift patterns rather
than injecting drift at fixed, predictable rounds. Concretely,
for each client k, we sample a set of drift events Ek =
{e1 , . . . , eNk }, where Nk controls how frequently drift occurs
(here, Nk ∼ Poisson(λ) for tighter control). Each event
e ∈ Ek is parameterized by: (i) a random start round τk,e ∼
Uniform{1, . . . , T }, (ii) a duration Lk,e , (iii) a compound
drift type-set sk,e ⊆ {F, L, C} drawn from a categorical
distribution over non-empty subsets (feature/label/concept),
(x)
(iv) drift magnitudes mk,e for each selected type x ∈ sk,e ,
and (v) a transition mode gk,e ∼ Bernoulli(pgrad ) indicating
whether the drift is abrupt or gradual. The event induces a
time-varying intensity

⊮[t ≥ τk,e ]
if gk,e = 0 (abrupt),


(22)
αk,e (t) =
t−τ
k,e
clip
if gk,e = 1 (gradual),
Lk,e , 0, 1
and the resulting per-type drift intensity for client k at round
t is aggregated as:
X
(x)
(x)
Ak (t) =
mk,e αk,e (t),
x ∈ {F, L, C}. (23)
e: x∈sk,e

Because events are sampled independently per client and may
overlap in time and type, this protocol naturally produces
asynchronous drift across clients and entangled drift within

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

and across rounds. The commonly used fixed-round injection
protocol is recovered as a special case by making τk,e deterministic (shared across clients), using fixed magnitudes, and
setting pgrad = 0 (abrupt-only).
Realism of Entangled Drift Simulation. Rather than injecting
drift at fixed or synchronized rounds, our simulator models
compound drift as an asynchronous, stochastic process with
client-specific onset, duration, magnitude, and transition mode
(abrupt or gradual). Drift events are sampled independently
and may overlap across drift types and clients, emulating
unpredictable protocol changes, traffic mix shifts, and emerging attack behaviors. Consequently, the PPO controller cannot
exploit deterministic timing cues and must adapt solely from
noisy population-level performance signals, reducing overfitting to any scripted drift schedule.
Injecting feature, label, and concept drift. At each round
t, the local data stream at client k is perturbed according to
(F)
(L)
(C)
(Ak (t), Ak (t), Ak (t)):
• Feature drift (F): we perturb flow-level feature vectors
(e.g., timing/burst statistics) via an intensity-scaled opera(F)
tor, x̃ = x ⊙ 1 + Ak (t) η , where η is sampled from a
zero-mean noise distribution. This models shifts caused by
protocol/app updates and changes in network conditions.
• Label drift (L): we model prior shift by interpolating
between a base class prior π 0k and a shifted prior π 1k
(sampled once per event or per client), i.e., π k (t) = (1 −
(L)
βk (t))π 0k +βk (t)π 1k with βk (t) = clip(Ak (t), 0, 1). Minibatches are drawn according to π k (t) to reflect changing
traffic composition over time.
• Concept drift (C): we model conditional shift by modifying P (y | x) through controlled relabeling/permutation on a
(C)
subset of classes, with drift rate γk (t) = clip(Ak (t), 0, 1).
This captures evolving semantics of encrypted traffic patterns (e.g., application behavior changes) even when feature
marginals may appear similar.
Domain randomization for PPO training. To prevent the
PPO-based expert lifecycle policy from overfitting to any particular drift schedule, we train it under domain randomization:
each PPO episode samples a drift-environment hyperparameter
set Θ (event rate, timing and duration ranges, magnitude
ranges, and pgrad ), then generates {Ek } and runs FL for T
rounds under that realization. This forces the policy to learn
robust expert management under diverse, unpredictable drift
processes rather than memorizing fixed injection rounds. For
fair comparison, all baselines are evaluated under the same
realized drift sequences (same random seed) for each trial, and
we report aggregate performance over multiple independent
drift realizations.
E. Results and Discussion
Table II and Table III provide a comprehensive quantitative comparison of DAIR-FedMoE against state-of-theart baselines across four benchmark datasets. On the traffic
classification tasks (Table II), DAIR-FedMoE consistently
improves overall macro-F1 by approximately 2-3% compared
to leading drift-aware models such as FedDrift and FedCCFA.

11

Fig. 5: Drift-recovery under domain-randomized asynchronous
entangled drift on ISCX-VPN. Macro-F1 over 250 federated
rounds comparing DAIR-FedMoE with state-of-the-art baselines. Vertical dashed markers denote randomly sampled drift
events (green: feature, red: concept, blue: label). Their random
start times and heterogeneous durations induce overlapping
intervals that simulate compound/entangled drift. Table reports
one realized random injection schedule, listing each event.

In addition, minority-class recall increases by 5-8%, indicating
more balanced classification performance across class distributions. These improvements are achieved without incurring
additional communication or privacy overhead, maintaining a
computational profile comparable to that of FedAvg. Likewise,
in the intrusion-detection scenarios (Table III), DAIR-FedMoE
outperforms both packet-level and flow-level baselines by 12% in macro-F1, while achieving similarly substantial reductions in error rates for rare or minority-class attack types.
Fig. 5 plots the Macro-F1 trajectories on ISCX-VPN under
our domain-randomized, asynchronous entangled drift protocol, where feature, label, and concept drift events start at
random rounds and persist for heterogeneous durations, creating overlapping intervals that emulate compound drift. DAIRFedMoE converges rapidly, reaching ≈0.95 Macro-F1 within
the first ∼23 rounds, and remains the best-performing method
throughout the 250-round horizon. When drift occurs, its performance degrades modestly and recovers quickly: it rebounds
after the early overlapping feature drifts (F1 –F2 ) and maintains
stable performance through subsequent feature/label shifts (F3 ,
L1 ). The most challenging period arises when concept drifts
(C1 , C2 ) overlap with label drift L2 (the highlighted compound
region around rounds ∼150–200), where DAIR-FedMoE still
sustains comparatively high Macro-F1 and returns to near predrift performance by the end of training. In contrast, state-ofthe-art baselines exhibit substantially larger drops and more
prolonged recovery during these drift intervals, indicating
limited robustness when drift types are entangled. Overall,
the curves demonstrate that jointly modeling compound drift

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

12

TABLE II: Comparison of DAIR-FedMoE with state-of-the-art baselines on the ISCX-VPN and ISCX-Tor encryptedtraffic classification benchmarks. Bold values indicate the best performance, and underlined values indicate the second-best
performance for each metric. The experiments are repeated for 20 times and reported as (mean±std).
Method

ISCX-VPN Dataset

ISCX-Tor Dataset

PRm

RCm

F1m

ACC

DR-Score

PRm

RCm

F1m

ACC

DR-Score

FS-Net [26]
FlowPic [42]
DeepPacket [31]
Flow-GNN [19]
FedETC [20]
FedPacket [3]
FL-ETC [51]
BC-FLETC [28]
FedDrift [21]
FedCCFA [7]
FedIBD [18]
Cross-FCL [54]
Master-FL [47]
FairFedDrift [40]
FairINC [8]
FedStream [12]
FedMoE-DA [52]

67.17±.40

70.08±.17

69.28±.20

69.17±.36

49.66±.12

67.90±.10

70.91±.26

67.27±.07

69.99±.36

86.90±.40
87.47±.16
89.49±.31
87.13±.42
85.78±.40
86.95±.35
88.44±.35
90.96±.20
90.55±.20
89.33±.44
87.44±.24
85.49±.35
89.18±.40
88.21±.34
87.18±.27
88.70±.19

90.69±.35
91.36±.37
93.47±.24
90.99±.20
89.57±.26
90.80±.17
92.34±.10
95.00±.22
94.57±.34
93.24±.14
91.27±.10
89.26±.16
93.16±.15
92.13±.33
91.09±.15
91.29±.20

89.66±.19
90.32±.28
92.41±.44
89.95±.54
88.55±.15
89.77±.18
91.29±.21
93.92±.51
93.50±.30
92.19±.12
90.23±.16
88.25±.31
92.11±.21
91.08±.13
90.05±.56
90.47±.49

89.52±.34
90.18±.10
92.26±.23
89.81±.25
88.41±.28
89.63±.40
91.15±.28
93.77±.14
93.35±.11
92.04±.33
90.09±.06
88.11±.29
91.96±.07
90.94±.16
89.91±.07
90.58±.09

45.27±.08
38.52±.04
28.52±.03
42.69±.14
45.04±.13
44.59±.03
32.19±.07
21.66±.04
25.98±.04
31.38±.16
41.96±.13
48.35±.11
32.07±.05
34.99±.05
41.13±.08
32.64±.14

86.97±.13
84.81±.09
85.90±.28
87.26±.41
90.83±.28
85.62±.09
86.74±.41
88.45±.16
86.19±.40
88.55±.23
92.67±.39
88.44±.10
86.93±.30
90.12±.18
91.88±.29
85.40±.31

90.85±.41
88.58±.22
89.70±.19
91.10±.07
94.87±.17
89.36±.09
90.63±.16
92.38±.12
89.99±.15
92.51±.35
96.77±.37
92.35±.32
90.75±.18
94.07±.09
95.92±.22
90.38±.35

87.03±.61
87.61±.22
89.64±.29
87.27±.63
85.92±.55
87.08±.26
88.58±.59
91.10±.43
90.70±.67
89.47±.36
87.58±.47
85.62±.48
89.32±.07
88.35±.28
87.32±.38
86.08±.42

89.68±.31
87.43±.08
88.54±.17
89.93±.13
93.64±.26
88.20±.28
89.46±.34
91.19±.12
88.83±.28
91.31±.23
95.52±.41
91.16±.25
89.58±.39
92.86±.45
94.68±.22
90.01±.29

48.14±.09
41.74±.07
32.40±.14
30.89±.12
47.53±.11
43.55±.11
45.62±.07
38.68±.07
18.67±.08
24.92±.08
33.10±.11
42.02±.14
44.28±.05
25.46±.15
30.27±.07
48.47±.05
37.50±.08

DAIR-FedMoE

93.28±.10 94.39±.07 96.28±.59 96.13±.34 15.38±.02 93.86±.08

95.00±.32

93.43±.35 96.73±.07 13.10±.03

TABLE III: Comparison of DAIR-FedMoE with state-of-the-art baselines on the VNAT and USTC-TFC2016 intrusion detection
benchmarks.
Method

VNAT Dataset

USTC-TFC2016 Dataset

PRm

RCm

F1m

ACC

DR-Score

PRm

RCm

F1m

ACC

DR-Score

FS-Net [26]
FlowPic [42]
DeepPacket [31]
Flow-GNN [19]
FedETC [20]
FedPacket [3]
FL-ETC [51]
BC-FLETC [28]
FedDrift [21]
FedCCFA [7]
FedIBD [18]
Cross-FCL [54]
Master-FL [47]
FairFedDrift [40]
FairINC [8]
FedStream [12]
FedMoE-DA [52]

71.16±.09

67.08±.34

70.55±.26

69.46±.15

51.87±.14

71.23±.33

67.08±.39

72.28±.65

69.46±.34

90.57±.29
91.59±.11
90.06±.47
91.04±.32
93.59±.25
89.65±.35
91.64±.36
93.35±.10
92.96±.14
91.43±.46
89.45±.40
89.99±.21
93.12±.22
91.78±.38
92.97±.46
90.29±.12

85.39±.19
86.35±.17
86.45±.23
85.82±.32
86.23±.28
84.49±.08
87.94±.24
88.00±.06
87.58±.27
88.04±.25
84.33±.25
84.80±.26
87.74±.30
86.50±.29
87.47±.35
93.44±.24

89.82±.11
90.82±.13
91.19±.41
90.27±.18
91.81±.49
88.87±.44
91.76±.40
92.56±.40
92.12±.34
90.60±.52
88.70±.16
89.19±.19
92.28±.55
90.98±.49
92.10±.43
92.89±.51

88.43±.11
89.42±.26
90.70±.10
88.87±.08
91.37±.25
87.50±.17
90.25±.26
91.13±.36
90.69±.27
89.17±.37
87.33±.09
87.81±.45
90.86±.18
89.58±.14
90.65±.39
93.72±.15

47.37±.06
37.26±.09
25.58±.11
40.30±.07
48.37±.06
42.18±.07
33.37±.15
18.76±.05
28.39±.03
33.93±.14
41.32±.07
50.30±.04
35.99±.02
35.54±.10
43.83±.12
29.07±.19

90.62±.34
91.64±.11
92.05±.44
91.10±.11
93.64±.10
89.69±.45
92.59±.32
93.34±.33
92.93±.26
91.40±.12
89.53±.44
89.99±.24
93.06±.09
91.81±.30
92.90±.44
89.31±.40

85.39±.23
86.35±.44
86.45±.25
85.82±.10
88.23±.41
84.49±.28
88.94±.18
88.00±.34
87.58±.33
87.04±.43
84.33±.29
84.80±.43
87.74±.25
86.50±.14
88.47±.20
88.13±.41

91.99±.54
93.02±.42
93.58±.59
92.47±.20
93.05±.60
91.05±.17
93.18±.29
94.81±.09
94.42±.32
90.89±.13
90.86±.11
91.40±.27
94.58±.20
93.21±.06
93.46±.25
90.42±.37

88.43±.06
89.42±.43
90.70±.30
88.87±.25
90.37±.19
87.50±.45
90.25±.11
91.13±.26
90.69±.12
90.17±.16
87.33±.22
87.81±.25
90.86±.21
89.58±.14
90.65±.14
92.98±.19

47.16±.08
41.13±.08
28.75±.03
28.83±.09
50.32±.15
44.31±.09
43.42±.12
39.03±.01
16.83±.09
26.62±.06
30.16±.05
43.03±.06
46.13±.14
28.57±.08
28.06±.04
44.54±.11
30.42±.19

DAIR-FedMoE

96.55±.43 91.04±.10 95.76±.41 94.28±.33 12.07±.15 97.59±.31 92.01±.07 98.06±.41 95.28±.18 11.82±.06

via drift-aware routing, adaptive reweighting, and dynamic
expert lifecycle management enables faster and more resilient
recovery than piecemeal drift-handling strategies.
This strong recovery capability can be attributed to DAIRFedMoE’s integrated adaptation mechanism. The hierarchical
MoE routing allows stable experts to retain accuracy during
distributional shifts, while newly spawned specialists rapidly
adapt to changing patterns. Concurrently, the entropy-guided
loss reweighting mechanism dynamically prioritizes underrepresented or emerging classes, preserving high minorityclass recall throughout training. Reinforcing this, the PPObased expert lifecycle manager modulates expert pool capacity
in response to drift signals, spawning new experts at drift
points and pruning or merging them during stable phases.

This cycle is visualized in Fig. 6, where the blue curve shows
macro-F1 evolution, the gray line tracks active experts, and
vertical dashed red lines mark simulated drift events (feature,
concept, label, and combined). Policy actions, spawn (green
triangles), prune (orange squares), and merge (red diamonds),
are annotated along the expert count curve, demonstrating the
policy’s effectiveness in managing capacity without overfitting
or unnecessary expansion. Complementing this, Fig. 7 presents
a detailed view of expert lifecycles across 250 federated rounds
for ISCX-VPN and ISCX-Tor. Each horizontal bar corresponds
to an expert, with active and inactive phases, while vertical
markers denote drift, spawn, prune, and merge events. The
visualization highlights how the policy dynamically regulates
expert activation, pruning, and merging in response to drift,

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

13

Expert

Expert Lifecycle Across 250 Federated Rounds for ISCX-VPN Dataset
E81
E79
E77
E75
E73
E71
E69
E67
E65
E63
E61
E59
E57
E55
E53
E51
E49
E47
E45
E43
E41
E39
E37
E35
E33
E31
E29
E27
E25
E23
E21
E19
E17
E15
E13
E11
E9
E7
E5
E3
E1

Inactive Expert
Active Expert
Feature Drift
Label Drift
Concept Drift
Spawn Event
Prune Event
Merge Event

50

100

150

200

250

Federated Round

Expert

Expert Lifecycle Across 250 Federated Rounds for ISCX-TOR Dataset

Fig. 6: Visualization of DAIR-FedMoE’s performance, expertpool dynamics, and policy actions on the ISCX-VPN (top) and
ISCX-Tor (bottom) datasets over 250 federated rounds.

E71
E69
E67
E65
E63
E61
E59
E57
E55
E53
E51
E49
E47
E45
E43
E41
E39
E37
E35
E33
E31
E29
E27
E25
E23
E21
E19
E17
E15
E13
E11
E9
E7
E5
E3
E1

Inactive Expert
Active Expert
Feature Drift
Label Drift
Concept Drift
Spawn Event
Prune Event
Merge Event

50

100

150

200

250

Federated Round

ensuring sustained adaptability while preventing uncontrolled
growth.
The framework’s ability to maintain robust performance
under drift comes with only modest computational overhead,
approximately 1.2× that of FedAvg, while maintaining a
strong privacy guarantee under a controlled differential privacy
budget ((ε, δ) ≈ (5.4, 10−5 ) after 250 rounds).
Finally, Fig. 8 compares the per-class precision-recall curves
for DAIR-FedMoE and a baseline classifier on ISCX-VPN and
ISCX-Tor. DAIR-FedMoE demonstrates balanced precision
and recall across both majority and minority classes, confirming its effectiveness under dynamic label shift. This behavior is
directly tied to the expert confidence-driven loss reweighting
mechanism, which enables the model to remain sensitive to
rare or fluctuating class distributions, a key requirement in
federated environments with common and volatile label skew.
In summary, DAIR-FedMoE’s integration of drift-adaptive
routing, entropy-aware optimization, and reinforcement
learning-based expert management yields a comprehensive and
effective solution for encrypted-traffic classification. It not
only achieves higher classification accuracy across multiple
datasets but also recovers more quickly and gracefully from
distributional drift, marking a significant advancement in federated learning under non-stationary conditions.
To provide deeper insight into DAIR-FedMoE’s classification behavior across datasets, we present the normalized confusion matrices for ISCX-VPN, ISCX-TOR, USTC-TFC2016,
and VNAT. These matrices, shown in Fig. 9, reports the
proportion of samples predicted for each class and offer a
class-wise view of prediction fidelity and confusion trends.
On the ISCX-VPN benchmark, DAIR-FedMoE maintains

Fig. 7: Expert lifecycle across 250 federated rounds for ISCXVPN (top) and ISCX-Tor (bottom) datasets.
highly consistent diagonal dominance, with all classes achieving above 94% correct classification. Minor misclassifications
are observed between similar traffic patterns such as VPNemail and VPN-chat, or between file transfer and streaming,
likely due to shared temporal characteristics. Importantly, both
base and VPN-prefixed classes exhibit strong separation, highlighting the model’s ability to preserve semantic distinctions
despite encryption obfuscation.
The ISCX-TOR results reinforce that mainline traffic types
(e.g., browsing, audio, video) and their TOR counterparts are
identified with over 95% accuracy, with only minor confusion
between adjacent variants such as TOR-video and TORaudio, reflecting the complexity of anonymized traffic and the
model’s robustness in preserving anonymity-aware features.
On USTC-TFC2016, which spans 20 application-level
classes encompassing both benign and malware traffic, DAIRFedMoE achieves strong category-level separation, maintaining 93-95% diagonal accuracy across nearly all classes. Despite overlaps (e.g., Virut vs. Tinba or benign services such
as Gmail, Outlook, and FTP), off-diagonal noise remains
minimal, indicating effective disentanglement of high-level
behaviors even in malware-heavy scenarios.
Finally, the VNAT confusion matrix demonstrates similarly
high fidelity, with all eight classes, comprising both raw
and VPN-encrypted streaming, file transfer, and VoIP traffic,
classified with over 92% accuracy. Although slight confusion
exists between VPN classes with overlapping packet dynamics

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

PR-Curve - ISCX-VPN Dataset Baseline

PR-Curve - ISCX-VPN Dataset DAIR-FedMoE

1.0

14

PR-Curve - ISCX-TOR Dataset Baseline

1.0

1.0

PR-Curve - ISCX-TOR Dataset DAIR-FedMoE
1.0

browse (AP=0.6656)

browse (AP=0.9845)

email (AP=0.5079)

email (AP=0.9842)

chat (AP=0.5594)

chat (AP=0.8117)

chat (AP=0.9883)

ft (AP=0.7644)

stream (AP=0.4643)

stream (AP=0.9865)

ft (AP=0.8525)
voip (AP=0.9142)
p2p (AP=0.4729)

0.4

vpn email (AP=0.2451)

ft (AP=0.9865)
voip (AP=0.9853)
p2p (AP=0.9851)

0.4

vpn email (AP=0.9847)

vpn chat (AP=0.5079)

0.0

tor email (AP=0.4729)

vpn p2p (AP=0.3169)

vpn p2p (AP=0.9779)

0.4

0.6

0.8

1.0

0.2

0.0

Recall

0.2

p2p (AP=0.9774)
tor browse (AP=0.9755)
tor email (AP=0.9720)

0.4

tor chat (AP=0.9696)
tor video (AP=0.9650)

0.2

tor ft (AP=0.9562)

tor voip (AP=0.3554)

0.0

0.4

0.6

0.8

1.0

tor voip (AP=0.9388)

tor p2p (AP=0.2451)

0.0

0.2

0.4

Recall

(a)

voip (AP=0.9777)

tor audio (AP=0.9684)

tor video (AP=0.6378)
tor ft (AP=0.3169)

vpn voip (AP=0.9810)

0.2

tor browse (AP=0.5287)

0.6

tor audio (AP=0.4560)

vpn ft (AP=0.9835)

vpn voip (AP=0.4824)

0.0

ft (AP=0.9825)

p2p (AP=0.8505)

0.4

audio (AP=0.9829)
video (AP=0.9829)

voip (AP=0.5189)

tor chat (AP=0.5997)

vpn stream (AP=0.9843)

0.2

vpn ft (AP=0.4560)

0.0

0.6

vpn chat (AP=0.9843)

vpn stream (AP=0.3554)

0.2

Precision

video (AP=0.4643)

0.6

chat (AP=0.9839)

0.8

audio (AP=0.5246)

email (AP=0.9887)

Precision

Precision

0.6

0.8

0.8

email (AP=0.6656)

Precision

0.8

0.6

0.8

0.0

1.0

Recall

(b)

tor p2p (AP=0.9053)

0.0

0.2

0.4

0.6

0.8

1.0

Recall

(c)

(d)

Fig. 8: Per-class precision-recall (PR) curves on the ISCX-VPN and ISCX-Tor datasets for both the baseline classifier (a, c)
and DAIR-FedMoE (b, d).

Predicted Label

Predicted Label

(a) ISCX-VPN

(b) ISCX-Tor

0.00

0.00

voip

0.01

0.93

0.01

0.01

0.00

0.02

0.01

0.00

ft

0.00

0.00

0.94

0.01

0.01

0.01

0.01

0.02

p2p

0.00

0.01

0.01

0.94

0.01

0.02

0.00

0.01

vpn stream

0.01

0.00

0.01

0.00

0.92

0.00

0.03

0.03

vpn voip

0.02

0.01

0.00

0.02

0.01

0.93

0.00

0.01

vpn ft

0.00

0.03

0.00

0.01

0.00

0.01

0.93

0.01

vpn p2p

0.00

0.02

0.01

0.02

0.01

0.01

0.01

0.92

0.8

p
p2

ft

0.2

n

n

Predicted Label

(c) VNAT

True Label

0.4

vp

vo
ip

vp

p

am
re

st

vp
n

p2

ft

0.6

n

br

ow
em se
a
ch il
au at
di
vi o
de
o
f
vo t
i
to
r b p2p
to row p
r e se
to ma
to r ch il
r a
to aud t
r v io
id
t eo
to or
r ft
to voip
rp
2p

ft
vo
ip
p2
p
e
vp ma
vp n c il
n ha
st t
re
a
vp m
vp n f
n t
vo
vp ip
n
p2
p
n

vp

em

ail
ch
st at
re
am

vpn p2p

0.2

0.00

vp

0.2

0.02 0.00 0.00 0.00 0.00 0.01 0.01 0.00 0.01 0.00 0.00 0.94

0.01

am

vpn ft 0.00 0.00 0.01 0.00 0.01 0.02 0.00 0.00 0.01 0.94 0.00 0.00
vpn voip 0.00 0.00 0.01 0.01 0.00 0.01 0.01 0.00 0.01 0.00 0.95 0.01

0.4

0.01

vo
ip

True Label

True Label

0.4

0.03

Cridex 0.95 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.01 0.01 0.00 0.00 0.00 0.00 0.00 0.00
Geodo 0.00 0.94 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.01 0.01 0.00 0.00
Htbot 0.00 0.00 0.95 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.01 0.01 0.00 0.01 0.00
Miuref 0.00 0.00 0.00 0.94 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.01 0.00 0.01 0.01 0.00 0.00 0.01 0.00 0.00
Neris 0.00 0.00 0.00 0.00 0.95 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.00
Nsis-ay 0.00 0.00 0.00 0.00 0.00 0.95 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.01
Shifu 0.00 0.01 0.00 0.00 0.01 0.00 0.95 0.00 0.01 0.00 0.00 0.00 0.00 0.01 0.01 0.00 0.00 0.00 0.00 0.00
Tinba 0.00 0.01 0.00 0.00 0.00 0.00 0.01 0.94 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00
Virut 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.95 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00
Zeus 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.94 0.00 0.00 0.01 0.01 0.00 0.00 0.01 0.00 0.00 0.00
BitTorrent 0.00 0.01 0.01 0.00 0.00 0.00 0.00 0.01 0.01 0.00 0.94 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00
Facetime 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.01 0.93 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00
FTP 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.95 0.01 0.01 0.01 0.00 0.00 0.01 0.00
Gmail 0.01 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.94 0.00 0.01 0.00 0.00 0.00 0.00
MySQL 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.94 0.01 0.00 0.00 0.00 0.00
Outlook 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.01 0.00 0.01 0.00 0.94 0.00 0.00 0.00 0.01
Skype 0.00 0.01 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.01 0.01 0.00 0.00 0.00 0.00 0.00 0.94 0.00 0.00 0.00
SMB 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.95 0.00 0.00
Weibo 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.95 0.00
WW 0.00 0.00 0.00 0.01 0.00 0.01 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.01 0.00 0.94

0.8

0.6

Proportion

vpn chat 0.00 0.00 0.00 0.01 0.01 0.00 0.00 0.95 0.00 0.00 0.01 0.01
vpn stream 0.01 0.00 0.00 0.01 0.01 0.00 0.01 0.00 0.94 0.00 0.00 0.00

0.6

0.00

Proportion

vpn email 0.00 0.01 0.00 0.02 0.01 0.00 0.94 0.00 0.01 0.01 0.01 0.01

0.6

Proportion

p2p 0.02 0.00 0.00 0.00 0.00 0.95 0.00 0.00 0.01 0.00 0.00 0.01

Proportion

voip 0.00 0.00 0.00 0.00 0.96 0.00 0.00 0.01 0.00 0.01 0.01 0.00

0.8

0.94

re

0.8

ft 0.01 0.01 0.01 0.96 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01

Confusion Matrix for USTC-TFC2016

Confusion Matrix for VNAT
stream

st

stream 0.00 0.00 0.94 0.01 0.01 0.00 0.01 0.01 0.00 0.01 0.00 0.00

browse 0.97 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00
email 0.00 0.95 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00
chat 0.00 0.00 0.96 0.00 0.01 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00
audio 0.00 0.00 0.00 0.96 0.00 0.00 0.01 0.00 0.01 0.01 0.00 0.01 0.00 0.00 0.00 0.00
video 0.00 0.00 0.00 0.00 0.96 0.00 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00
ft 0.00 0.00 0.00 0.00 0.00 0.96 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.00
voip 0.00 0.00 0.00 0.00 0.01 0.00 0.96 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01
p2p 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.97 0.01 0.00 0.00 0.00 0.00 0.00 0.01 0.00
tor browse 0.01 0.01 0.00 0.00 0.00 0.00 0.01 0.01 0.95 0.00 0.00 0.00 0.00 0.00 0.00 0.01
tor email 0.00 0.00 0.01 0.00 0.02 0.01 0.00 0.00 0.00 0.94 0.00 0.00 0.00 0.00 0.00 0.00
tor chat 0.01 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.95 0.00 0.00 0.00 0.00 0.00
tor audio 0.01 0.00 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.95 0.01 0.00 0.01 0.00
tor video 0.00 0.00 0.01 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.01 0.95 0.01 0.00 0.00
tor ft 0.00 0.01 0.01 0.01 0.01 0.00 0.00 0.00 0.01 0.00 0.00 0.00 0.00 0.94 0.00 0.00
tor voip 0.00 0.01 0.00 0.00 0.01 0.00 0.00 0.01 0.00 0.01 0.00 0.00 0.00 0.00 0.94 0.00
tor p2p 0.00 0.01 0.00 0.01 0.00 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.95

True Label

chat 0.02 0.96 0.01 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00 0.00

0.4

0.2

Cr
G idex
e
H od
M tboo
iu t
r
NsNeref
is is
Sh-ay
Ti ifu
n
Vb
Bi irua
tT Z t
Fa orreus
ce en
tim t
F e
GT
M mP
O ySQail
ut L
Sklook
y
S pe
W MB
ei
Wbo
W

Confusion Matrix for ISCX-TOR

Confusion Matrix for ISCX-VPN
email 0.95 0.00 0.01 0.01 0.00 0.00 0.00 0.00 0.01 0.00 0.01 0.00

Predicted Label

(d) USTC-TFC2016

Fig. 9: Confusion matrices for DAIR-FedMoE on four datasets.
Client-wise Macro-F1 Distribution at Convergence
across Four Datasets

1.00

0.008-0.009) and low variance indicate stable generalization
despite non-IID client data distributions, while the absence
of extreme outliers confirms that even the lowest-performing
clients maintain strong classification performance (>0.92 for
ISCX-Tor and >0.94 for others). This demonstrates DAIRF ED M O E’s robustness and fairness in distributed encrypted
traffic classification.

Macro-F1 Score

0.98

0.96

0.94

0.92
ISCX-VPN

ISCX-Tor

VNAT

USTC-TFC2016

Fig. 10: Client-wise macro-F1 distribution at convergence
across four datasets.

(e.g., VPN-ft and VPN-p2p), the overall separability remains
intact. These results confirm DAIR-FedMoE’s generalizability across datasets with varying label cardinality, encryption
protocols, and application distributions.
F. Client-wise Macro-F1 Distribution
Fig. 10 illustrates the client-wise macro-F1 distribution
at convergence across four datasets, ISCX-VPN, ISCX-Tor,
VNAT, and USTC-TFC2016, using box plots that represent
the interquartile range (IQR), with medians shown as red
lines and individual client scores overlaid as gray dots. The
results show that DAIR-F ED M O E achieves consistent and
equitable performance across all clients, with median macroF1 scores closely matching the reported global performance
(≈ 0.963 for ISCX-VPN, 0.934 for ISCX-Tor, 0.958 for
VNAT, and 0.981 for USTC-TFC2016). The narrow IQRs (±

G. Ridgeline Density of Policy Actions
Fig. 11 shows the smoothed frequencies of Spawn, Prune,
and Merge selected by the PPO agent over 250 rounds
on ISCX-VPN and ISCX-Tor. We apply a 10-round moving
average to action counts and plot stacked ridgelines (Spawn
top, Prune middle, Merge bottom); vertical dashed red lines
indicate injected drift events.
Across both datasets, Spawn exhibits sharp peaks immediately after drift, indicating rapid allocation of new experts in
response to distribution shifts. Prune increases later during
stabilization windows, reflecting removal of under-utilized
experts once performance recovers, while Merge remains
low with occasional post-drift upticks, suggesting selective
consolidation of redundant specialists. Overall, the ridgelines
illustrate a consistent lifecycle pattern: aggressive capacity
expansion at drift onset followed by pruning/merging as the
system re-stabilizes.
H. Ablation Studies
To assess the individual contribution of each core module
within DAIR-FedMoE, we perform a series of ablation experiments on the ISCX-VPN benchmark, focusing on four key

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

Ridgeline Density of Policy Actions for ISCX-VPN Dataset
Spawn
Density
Prune
Density
Merge
Density
0

50

100
150
Federated Round

200

250

Ridgeline Density of Policy Actions for ISCX-TOR Dataset

Spawn
Density

Prune
Density

15

TABLE V: Sensitivity analysis of DAIR-FedMoE to PPO
reward weights λd (drift-recovery reward) and µ (expert-size
penalty) on the ISCX-VPN dataset.
λd

µ

Macro-F1(%)

Minority Recall(%)

#Experts

1.0
1.0
1.0
2.0
2.0
2.0
5.0
5.0
5.0

0.1
0.5
1.0
0.1
0.5
1.0
0.1
0.5
1.0

87.55
88.03
93.97
94.61
96.28
96.81
97.24
96.07
94.20

80.8
80.5
85.26
89.32
89.62
81.33
78.15.
72.97
69.88

8
7
6
10
11
7
12
8
7

TABLE VI: Hyperparameter sensitivity analysis of DAIRFedMoE on the ISCX-VPN dataset, evaluating the impact
of the drift-estimation window size W and EMA smoothing
factor α on macro-F1 and minority-class recall.

Merge
Density
0

50

100
150
Federated Round

200

250

TABLE IV: Ablation study on the ISCX-VPN dataset quantifying the impact of removing key components of DAIRFedMoE.

Full DAIR-FedMoE
w/o RL management
w/o adaptive reweighting
w/o routing

Macro-F1(%)

Minority Recall(%)

Drift-estimation window size W

Fig. 11: Ridgeline density of policy actions for ISCX-VPN
(top) and ISCX-Tor (bottom) datasets.

Model Variant

Parameter (value)

Macro-F1
(%)

Minority
Recall(%)

Drift Recovery
(rounds)

96.28
82.71
85.09
86.90

89.62
77.06
75.25
69.33

12
45
29
38

aspects: (1) the impact of removing core components, (2) the
behavior of the reinforcement learning policy, (3) sensitivity
to key hyperparameters, and (4) runtime overhead, communication cost, and privacy budget.
Effect of removing core components. We access the contribution of each core component by disabling the RL-managed
expert lifecycle, the entropy-driven loss reweighting, and the
drift-adaptive MoE routing. Table IV reports the macro-F1
score, minority-class recall, and drift-recovery speed for each
variant. Disabling RL-managed expert lifecycle, where the
expert pool remains static with no prune/spawn/merge decisions, leads to a substantial decline in macro-F1 by 13.57%,
minority-class recall by 12.56%, and drift recovery slows
markedly from 12 to 45 rounds. When the adaptive loss
reweighting module is removed, standard cross-entropy is used
in place of entropy-aware weighting, causing macro-F1 to
drop to 85.09% and minority recall to 75.25%, with recovery
extending to 29 rounds. Finally, disabling the drift-adaptive
MoE routing and collapsing to a flat expert regime yields
reduced macro-F1, minority recall, and increased rounds for
drift recovery. These findings highlight the necessity of each
module in sustaining DAIR-FedMoE’s robustness to drift and
performance on underrepresented classes.
RL Policy Analysis. To better understand the behavior and
robustness of the PPO-based expert lifecycle manager, we

W = 250
W = 500
W = 1000

95.67
96.28
89.66

86.04
89.62
84.93

EMA smoothing factor α
α = 0.90
α = 0.95
α = 0.99

92.51
96.28
95.08

87.74
89.62
83.29

analyze two aspects: the temporal evolution of the expert
pool and the sensitivity of performance to the reward-weight
hyperparameters λd (drift recovery reward) and µ (expert-size
penalty). First, we monitor the number of active experts across
rounds during training on ISCX-VPN. The policy dynamically
adjusts expert capacity: it spawns specialists in response to
initial feature drift (rounds 1-50), prunes underutilized experts
during stable phases (rounds 60-100), and reactivates spawning
after concept drift near round 100. As the system stabilizes,
redundant experts are merged (rounds 120-160). This behavior
results in peak pool sizes around 12 during high-drift periods,
contracting to 7-8 in low-drift phases, balancing adaptability
and efficiency. To evaluate robustness, we perform a grid
search over λd ∈ {1.0, 2.0, 5.0} and µ ∈ {0.1, 0.5, 1.0}.
As summarized in Table V, we observe that increasing λd
enhances both macro-F1 and minority recall, with improvements exceeding 8-10% compared to lower-weighted variants.
However, this comes at the cost of a larger expert pool.
Conversely, raising µ effectively reduces the number of experts
by up to 30%, but also induces a modest degradation in both
accuracy and minority-class performance. The default setting
(λd = 2.0, µ = 0.5) strikes the optimal trade-off, maximizing
predictive performance while maintaining a relatively compact
& responsive expert pool. These findings reinforce the stability
of the PPO-managed lifecycle & provide actionable insight
into balancing drift adaptability against model overhead.
Hyperparameter Sensitivity. We evaluate the robustness of
DAIR-FedMoE to two key hyperparameters in its drift detection module: the sliding window size W and the EMA
smoothing factor α. A grid search is conducted over W ∈

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

TABLE VII: Overall classification performance and communication cost of DAIR-FedMoE compared to FedAvg and
FedDrift, averaged across all four benchmarks.
Method

Macro-F1(%)

Minority
Recall(%)

Comm
Cost

Time/
Round (s)∗

FedAvg
85.03±.38
69.51±.29
1.00×
9.29
FedDrift
92.56±.40
87.21±.06
1.25×
11.61
DAIR-FedMoE
96.28±.59
89.62±.34
1.10×
10.22
∗ Average client-side wall-clock time per FL round, under the same setup.

{250, 500, 1000} and α ∈ {0.90, 0.95, 0.99} on the ISCXVPN dataset, with macro-F1 and minority-class recall reported in Table VI. We observe that smaller window sizes
(W = 250) enable quicker detection of abrupt distribution
shifts, resulting in a slight performance drop compared to
the default, particularly in minority-class recall. Conversely,
using a larger window (W = 1000) slows down drift responsiveness and leads to noticeable reductions in both macroF1 and recall, likely due to delayed adaptation. The default
setting of W = 500 offers a balanced trade-off, yielding
more stable performance than either extreme. Regarding EMA
smoothing, a lower α = 0.90 emphasizes recent drift signals,
leading to moderate improvements in recall but at the cost of
reduced macro-F1 due to sensitivity to transient noise. On the
other hand, a higher smoothing factor α = 0.99 stabilizes
the scoring but underreacts to shift boundaries, leading to
improved macro-F1 but noticeably reduced recall. The default
choice α = 0.95 provides a strong balance, maintaining both
high accuracy and equitable class-wise coverage, underscoring
the effectiveness of our drift-scoring mechanism across settings. Furthermore, even with suboptimal PPO weights, DAIRFedMoE consistently outperforms FedDrift and FedCCFA,
though with larger expert pools, demonstrating resilience to
hyperparameter variations.
Communication & Runtimes Cost Analysis. To assess the
deployment efficiency of DAIR-FedMoE, we evaluate its communication overhead and classification performance relative
to FedAvg and FedDrift, averaged across four benchmarks.
As shown in Table VII, DAIR-FedMoE achieves significantly
higher macro-F1 and minority-class recall compared to both
baselines. Specifically, it outperforms FedAvg by over 11%
in macro-F1 and 20% in minority recall, and improves upon
FedDrift by a notable margin as well, especially in fairness
across minority classes. Despite these gains, DAIR-FedMoE
incurs only a modest communication overhead, approximately
10% higher than FedAvg and still 15% lower than FedDrift.
This efficiency stems from its adaptive expert activation strategy, which avoids redundant communication by selectively
routing flows to active expert subsets. These results validate
that the proposed method not only enhances performance
across diverse drift scenarios, but also maintains practical communication cost, making it suitable for real-world federated
deployments.
Moreover, Table VIII summarizes the client-side resource
footprint at convergence when training with CPU-only Docker
containers to emulate edge devices. Each client maintains
a lightweight shard with approximately 3.6M parameters,

16

corresponding to a model size of only 15 MB. The computational demand is modest, requiring roughly 1.1 GFLOPs
per forward pass and 2.6 GFLOPs per training step, with a
peak memory footprint of 1.3 GB. The average wall-clock
cost per client round is 10 seconds, which is feasible for
resource-constrained nodes. Communication overhead remains
bounded, with uplink and downlink traffic of 16 MB and 15
MB per round, respectively, comparable to standard FedAvg
updates. These results confirm that DAIR-FedMoE imposes
minimal additional cost relative to baseline federated training
while remaining within the constraints of edge deployment.
A detailed computational complexity and overhead analysis,
including server-side costs and the stability of PPO under
differential privacy noise, is provided in Appendix C.
DAIR-FedMoE makes an explicit compute-robustness tradeoff and is most appropriate for capable gateways/enterprise
endpoints or edge servers, rather than highly constrained devices. Moreover, its value is not captured by the average 2–3%
Macro-F1 gain alone: the additional components primarily
limit performance collapse and accelerate recovery during
drift windows (improving worst-case accuracy and time-torecovery), which is critical for dependable security monitoring
where errors under drift are costly. To make this practical,
we also provide tunable deployment knobs (windowed drift
scoring every N steps, PPO updates every R rounds, and
a capped expert pool) that substantially reduce runtime with
minimal impact on drift recovery.
Privacy Budget Analysis. Table IX further quantifies the
privacy-utility trade-off of DP-SGD under a fixed δ = 10−5
and a fixed training schedule (B = 32, E = 5, T = 250).
As expected, increasing the noise multiplier σ strengthens
privacy by reducing the privacy loss ϵ (e.g., from ϵ = 26.62
at σ = 0.8 to ϵ = 4.36 at σ = 2.5). In terms of utility,
we observe a clear “sweet spot” at moderate noise: across
all clipping norms, performance peaks around σ = 1.2
(ϵ = 11.81), suggesting that moderate DP noise can act
as a regularizer that improves generalization, whereas both
weaker privacy (smaller σ) and very strong privacy (larger
σ) reduce accuracy. Notably, tightening privacy beyond this
point leads to a measurable degradation, with minority-class
recall typically dropping more sharply than Macro-F1 (e.g., for
C = 1.0, minority recall decreases from 89.62% at ϵ = 11.81
to 79.48% at ϵ = 4.36), indicating that minority detection is
more sensitive to aggressive noise.
Clipping norm C further modulates this trade-off: C = 1.0
consistently yields the best results over the entire sweep,
achieving the highest Macro-F1 (96.28%) and minority recall
(89.62%) at σ = 1.2. In contrast, C = 0.5 tends to underperform due to overly conservative clipping that attenuates
useful gradient signal, while C = 2.0 performs worst overall,
consistent with larger effective noise magnitude (σC) harming learning stability. Overall, these results support choosing
(C, σ) = (1.0, 1.2) as a strong default operating point that
provides a concrete privacy guarantee (ϵ ≈ 11.81 at δ = 10−5 )
while preserving high classification performance, and they
clearly illustrate the expected utility degradation as privacy
is tightened to very small ϵ. The chosen parameters follow
common DP-SGD practice: C = 1.0 is a standard setting for

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

17

TABLE VIII: Client-side resource footprint at convergence (batch size 32, CPU-only edge clients). Each value is averaged
across clients and final 5 rounds.
Client Shard
Params

Model
Size

FLOPs
/Fwd

FLOPs
/TrainStep

Peak
RAM

Client
Time/Round

Uplink
/round

Downlink
/round

3.57 M

15.08 MB

1.12 GFLOPs

2.63 GFLOPs

1.29 GB

10.22 sec

16.39 MB

15.92 MB

Notes. Clients run on CPU-only Docker containers to emulate edge devices; PPO policy and aggregation run only on the server.
FLOPs/TrainStep includes forward + backward for the GShard shard and sparse HMoE top-1 expert path; DP-SGD clipping and noise
are included. Uplink/Downlink reflect privatized deltas for the active shard + experts.

TABLE IX: Privacy-utility trade-off under DP-SGD (mean
over 3 seeds). We sweep the noise parameter σ for three
clipping norms C ∈ {0.5, 1.0, 2.0} and report the computed
privacy budget (ε, δ) with fixed δ = 10−5 , along with MacroF1, and minority-class recall. All ε values are computed using
the MA under same training schedule (batch size B = 32,
local epochs E = 5, and T = 250 rounds).
C

0.5

1.0

2.0

σ

ε (δ = 10−5 )

Macro-F1 (%)

Minority Recall (%)

0.8
1.0
1.2
1.5
2.0
2.5

26.62
16.17
11.81
8.34
5.75
4.36

83.49
88.07
91.13
90.56
87.60
84.72

74.91
79.88
83.51
80.73
75.05
71.59

0.8
1.0
1.2
1.5
2.0
2.5

26.62
16.17
11.81
8.34
5.75
4.36

91.28
94.07
96.28
92.88
89.34
86.08

85.22
87.10
89.62
85.26
82.93
79.48

0.8
1.0
1.2
1.5
2.0
2.5

26.62
16.17
11.81
8.34
5.75
4.36

84.07
87.55
89.27
86.67
82.60
79.04

70.15
73.63
78.06
74.08
72.02
69.91

bounding per-sample gradients with minimal bias [4], [27],
while σ = 1.2 balances privacy and utility, consistent with
frameworks such as Opacus [37]. These values thus provide a
practical trade-off aligned with related work.
Finally, expert lifecycle control (spawn/prune/merge) and
routing-policy learning operate only on DP-protected, secureaggregated outputs; by DP post-processing, they do not increase privacy leakage beyond the stated (ε, δ) budget. The
cumulative privacy loss over local steps and rounds is accounted for via standard DP composition using the accountant
described above.
VII. C ONCLUSION
This paper presented DAIR-FedMoE, a unified framework
for federated encrypted-traffic classification that jointly addresses feature, concept, and label drift through a hierarchical
mixture-of-experts architecture, entropy-guided loss reweighting, and a PPO-based expert lifecycle policy. Extensive experiments across four benchmark datasets demonstrate that
DAIR-FedMoE consistently outperforms state-of-the-art baselines in both steady-state accuracy and post-drift recovery,

while maintaining communication efficiency and differential
privacy guarantees. Overall, DAIR-FedMoE offers a practical
and robust solution for drift-resilient, privacy-preserving traffic
classification in non-stationary federated networks. A detailed
discussion of limitations and future research directions is
provided in Appendix D.
R EFERENCES
[1] M. Badar, W. Nejdl, and M. Fisichella, “Fac-fed: Federated adaptation
for fairness and concept drift aware stream classification,” Mach. Learn.,
vol. 112, no. 8, pp. 2761–2786, 2023.
[2] T. Bai, Y. Zhang, Y. Wang, Y. Qin, and F. Zhang, “Multi-site MRI
classification using weighted federated learning based on mixture of experts domain adaptation,” in Proc. Int. Conf. Bioinfor. Biomed. (BIBM),
December 6-8, 2022. Las Vegas, NV, USA: IEEE, pp. 916–921.
[3] E. Bakopoulou, B. Tillman, and A. Markopoulou, “Fedpacket: A federated learning approach to mobile packet classification,” IEEE Trans.
Mob. Comput., vol. 21, no. 10, pp. 3609–3628, 2022.
[4] Z. Bu, Y. Wang, S. Zha, and G. Karypis, “Automatic clipping: Differentially private deep learning made easier and stronger,” in Proc. Annu.
Conf. Neur. Info. Process. Sys. (NIPS), 10-16 December, 2023, New
Orleans, LA, USA, 2023.
[5] D. Busbridge, J. Ramapuram, P. Ablin, T. Likhomanenko, E. G.
Dhekane, X. S. Cuadros, and R. Webb, “How to scale your EMA,”
in Proc. Annu. Conf. Neur. Info. Process. Sys. (NIPS), 10-16 December,
2023. New Orleans, LA, USA: Curran Associates.
[6] F. E. Casado, D. Lema, R. Iglesias, C. V. Regueiro, and S. Barro,
“Ensemble and continual federated learning for classification tasks,”
Mach. Learn., vol. 112, no. 9, pp. 3413–3453, 2023.
[7] J. Chen, J. Xue, Y. Wang, Z. Liu, and L. Huang, “Classifier clustering
and feature alignment for federated learning under distributed concept
drift,” in Proc. 38th Annu. Conf. Neur. Info. Process. Sys. (NIPS),
December 10-15, 2024. Vancouver, BC, Canada: Curran Associates.
[8] Y. Deng, S. Yue, T. Wang, G. Wang, J. Ren, and Y. Zhang, “Fedinc: An
exemplar-free continual federated learning framework with small labeled
data,” in Proc. 21st Conf. Embedd. Networked Sensor Sys. (SenSys), 1315 November, 2023. New York, NY, USA: ACM, pp. 56–69.
[9] M. Duan, D. Liu, X. Ji, Y. Wu, L. Liang, X. Chen, Y. Tan, and A. Ren,
“Flexible clustered federated learning for client-level data distribution
shift,” IEEE Trans. Parallel Distrib. Syst., vol. 33, no. 11, pp. 2661–
2674, 2022.
[10] C. Dupuy, R. Arava, R. Gupta, and A. Rumshisky, “An efficient DP-SGD
mechanism for large scale NLU models,” in Proc. Int. Conf. Acoustics
Speech Sign. Process. (ICASSP), 23-27 May 2022.
Virtual Event,
Singapore: IEEE, pp. 4118–4122.
[11] Y. Feng, Y. Geng, Y. Zhu, Z. Han, X. Yu, K. Xue, H. Luo, M. Sun,
G. Zhang, and M. Song, “PM-MOE: mixture of experts on private model
parameters for personalized federated learning,” in Proc. ACM Web Conf.
(WWW), April 28-May 2, 2025. Sydney, Australia: ACM, pp. 134–146.
[12] B. Ganguly and V. Aggarwal, “Online federated learning via nonstationary detection and adaptation amidst concept drift,” IEEE/ACM
Trans. Networking, vol. 32, no. 01, pp. 643–653, 2024.
[13] X. Guan, R. Du, X. Wang, and H. Qu, “A personalized federated multitask learning scheme for encrypted traffic classification,” in Proc. 32nd
Int. Conf. Artif. Neur. Netw. (ICANN), 26-29 September, 2023, vol.
14256. Heraklion, Crete, Greece: Springer, pp. 258–270.
[14] B. Guo, Y. Mei, D. Xiao, and W. Wu, “Pfl-moe: Personalized federated
learning based on mixture of experts,” in Proc. 5th Int. Joint Conf. Web
Big Data (APWeb-WAIM), August 23-25, 2021, L. H. U, M. Spaniol,
Y. Sakurai, and J. Chen, Eds., vol. 12858. Guangzhou, China: Springer,
pp. 480–486.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3676447

JOURNAL OF IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 22, NO. 4, AUGUST 2025

[15] P. Hamedi, R. Razavi-Far, and E. Hallaji, “Federated continual learning:
Concepts, challenges, and solutions,” Neurocomputing, vol. 651, p.
130844, 2025.
[16] S. M. Hamidi, R. Tan, L. Ye, and E. Yang, “Fed-it: Addressing class
imbalance in federated learning through an information- theoretic lens,”
in Proc. Int. Symp. Info. Theory (ISIT), July 7-12, 2024. Athens, Greece:
IEEE, pp. 1848–1853.
[17] H. Y. He, Z. G. Yang, and X. N. Chen, “PERT: payload encoding
representation from transformer for encrypted traffic classification,” in
Proc. ITU Kaleidoscope: Indust. Driven Digit. Transform. (ITU K),
December 7-11, 2020. Ha Noi, Vietnam: IEEE, pp. 1–8.
[18] Y. Hou, H. Li, Z. Guo, W. Wu, R. Liu, and L. You, “Fedibd: a federated
learning framework in asynchronous mode for imbalanced data,” Appl.
Intell., vol. 55, no. 2, pp. 1–17, 2025.
[19] T. Huoh, Y. Luo, P. Li, and T. Zhang, “Flow-based encrypted network
traffic classification with graph neural networks,” IEEE Trans. Netw.
Serv. Manage., vol. 20, no. 2, pp. 1224–1237, 2023.
[20] Z. Jin, K. Duan, C. Chen, M. He, S. Jiang, and H. Xue, “Fedetc:
Encrypted traffic classification based on federated learning,” Heliyon,
vol. 10, no. 16, p. e35962, 2024.
[21] E. Jothimurugesan, K. Hsieh, J. Wang, G. Joshi, and P. B. Gibbons,
“Federated learning under distributed concept drift,” in Proc. Int. Conf.
Artif. Intell. Stat., April 25-27, 2023, vol. 206. Valencia, Spain: PMLR,
pp. 5834–5853.
[22] H. Lee, K. Deokseon, L. Joonseok, and H. Helen, “Class-wise combination of mixture-based data augmentation for class imbalance learning
of focal liver lesions in abdominal ct images,” J. Imaging Info. in Med.,
vol. 38, no. 2, 2025.
[23] D. Lepikhin, H. Lee, Y. Xu, D. Chen, O. Firat, Y. Huang, M. Krikun,
N. Shazeer, and Z. Chen, “Gshard: Scaling giant models with conditional
computation and automatic sharding,” in Proc. 9th Int. Conf. Learn. Rep.
(ICLR), 3-7 May, 2021. Virtual Event, Austria: ICLR.
[24] K. Lin, X. Xu, and H. Gao, “TSCRNN: A novel classification scheme
of encrypted traffic based on flow spatiotemporal features for efficient
management of iiot,” Comput. Networks, vol. 190, p. 107974, 2021.
[25] X. Lin, G. Xiong, G. Gou, Z. Li, J. Shi, and J. Yu, “Et-bert: A
contextualized datagram representation with pre-training transformers
for encrypted traffic classification,” in Proc. ACM Web Conf. (WWW),
April 25-29, 2022. Virtual Event Lyon, France: ACM, pp. 633–642.
[26] C. Liu, L. He, G. Xiong, Z. Cao, and Z. Li, “Fs-net: A flow sequence
network for encrypted traffic classification,” in Proc. IEEE Int. Conf.
Comput. Comm. (INFOCOM), 29 April-2 May, 2019. Paris, France:
IEEE, pp. 1171–1179.
[27] E. Liu and Z. Chu, “Wasserstein gan for moving differential privacy
protection,” Scientific Reports, vol. 15, no. 1, p. 19634, 2025.
[28] W. Liu, W. Cui, W. She, and Z. Tian, “Encrypted network traffic
detection based on blockchain and federated learning,” in Proc. 4th
Int. Conf. Blockchain Tech. Info. Secu. (ICBCTIS), 17-19 August, 2024.
Wuhan, China: IEEE, pp. 139–144.
[29] W. Liu, Y. Wang, K. Li, Z. Tian, and W. She, “Ftmoe: a federated
transfer model based on mixture-of-experts for heterogeneous image
classification,” Cluster Comput., vol. 28, no. 3, p. 165, 2025.
[30] Y. Liu, X. Wang, B. Qu, and F. Zhao, “Atvitsc: A novel encrypted
traffic classification method based on deep learning,” IEEE Trans. Inf.
Forensics Secur., 2024.
[31] M. Lotfollahi, M. Jafari Siavoshani, R. Shirali Hossein Zade, and
M. Saberian, “Deep packet: A novel approach for encrypted traffic
classification using deep learning,” Soft Comput., vol. 24, no. 3, pp.
1999–2012, 2020.
[32] N. Malekghaini, E. Akbari, M. A. Salahuddin, N. Limam, R. Boutaba,
B. Mathieu, S. Moteau, and S. Tuffin, “Data drift in dl: Lessons learned
from encrypted traffic classification,” in Proc. Int. Conf. Networking
Conference (IFIP), June 13-16, 2022. Catania, Italy: IEEE, 2022, pp.
1–9.
[33] D. M. Manias, I. Shaer, L. Yang, and A. Shami, “Concept drift
detection in federated networked systems,” in Proc. Glob. Comm. Conf.
(GLOBECOM), 7-11 December, 2021. Madrid, Spain: IEEE, pp. 1–6.
[34] D. R. Manjunath, J. J. Lohith, S. Selva Kumar, and A. Das, “Predicting diabetic retinopathy and nephropathy complications using machine
learning techniques,” IEEE Access, vol. 13, pp. 70 228–70 253, 2025.
[35] B. McMahan, E. Moore, D. Ramage, S. Hampson, and B. A. y. Arcas,
“Communication-efficient learning of deep networks from decentralized
data,” in Proc. 20th Int. Conf. Artif. Intell. Stat. (AISTATS), 20-22 April,
2017. Lauderdale, FL, USA: PMLR, pp. 1273–1282.
[36] M. K. Nori, I. Kim, and G. Wang, “Federated class-incremental learning:
A hybrid approach using latent exemplars and data-free techniques to

18

address local and global forgetting,” arXiv preprint arXiv:2501.15356,
2025.
[37] Opacus, “Opacus · Train PyTorch models with Differential Privacy — opacus.ai,” https://opacus.ai/tutorials/building_image_classifier,
2025, [Accessed: 02-09-2025].
[38] A. Pustozerova, J. Baumbach, and R. Mayer, “Differentially private
federated learning: Privacy and utility analysis of output perturbation
and DP-SGD,” in Proc. Int. Conf. Big Data (BigData), 15-18 December,
2023. Sorrento, Italy: IEEE, pp. 5549–5558.
[39] Y. Saadati, M. Rostami, and M. H. Amini, “pmixfed: Efficient personalized federated learning through adaptive layer-wise mixup,” arXiv
preprint arXiv:2501.11002, 2025.
[40] T. Salazar, J. Gama, H. Araújo, and P. H. Abreu, “Unveiling groupspecific distributed concept drift: A fairness imperative in federated
learning,” arXiv preprint arXiv:2402.07586, 2024.
[41] F. Sattler, K. Müller, and W. Samek, “Clustered federated learning:
Model-agnostic distributed multitask optimization under privacy constraints,” IEEE Trans. Neur. Netw. Learn. Syst., vol. 32, no. 8, pp. 3710–
3722, 2021.
[42] T. Shapira and Y. Shavitt, “Flowpic: A generic representation for
encrypted traffic classification and applications identification,” IEEE
Trans. Netw. Serv. Manage., vol. 18, no. 2, pp. 1218–1232, 2021.
[43] N. Shazeer, A. Mirhoseini, K. Maziarz, A. Davis, Q. V. Le, G. E. Hinton,
and J. Dean, “Outrageously large neural networks: The sparsely-gated
mixture-of-experts layer,” in Proc. 5th Int. Conf. Learn. Rep. (ICLR),
24-26 April, 2017. Toulon, France: ICLR.
[44] M. Shen, J. Zhang, L. Zhu, K. Xu, and X. Du, “Accurate decentralized
application identification via encrypted traffic analysis using graph
neural networks,” IEEE Trans. Inf. Forensics Secur., vol. 16, pp. 2367–
2380, 2021.
[45] Y. Shen, H. Wang, and H. Lv, “Federated learning with classifier shift
for class imbalance,” arXiv preprint arXiv:2304.04972, 2023.
[46] J. Sievers, T. Blank, and F. Simon, “Advancing accuracy in energy
forecasting using mixture-of-experts and federated learning,” in Proc.
15th Int. Conf. Future Sustain. Energy Sys. (e-Energy), June 4-7, 2024.
Singapore: ACM.
[47] N. Wang, X. Li, Z. Guan, and S. Yuan, “Fedstream: A federated learning
framework on heterogeneous streaming data for next-generation traffic
analysis,” IEEE Trans. Network Sci. Eng., vol. 11, no. 3, pp. 2485–2496,
2024.
[48] W. Wang, M. Zhu, X. Zeng, X. Ye, and Y. Sheng, “Malware traffic
classification using convolutional neural network for representation
learning,” in Proc. Int. Conf. Info. Networking (ICOIN), 11-13 January,
2017. Da Nang, Vietnam: IEEE, pp. 712–717.
[49] T. Yoon, S. Shin, S. J. Hwang, and E. Yang, “Fedmix: Approximation
of mixup under mean augmented federated learning,” in Proc. 9th Int.
Conf. Learn. Rep. (ICLR), May 3-7, 2021. Virtual Event, Austria:
OpenReview.net.
[50] E. L. Zec, J. Martinsson, O. Mogren, L. R. Sütfeld, and D. Gillblad,
“Federated learning using mixture of experts,” 2021.
[51] Y. Zeng, Z. Wang, X. Guo, K. Shi, Z. Liu, X. Zhu, and J. Ma,
“Social networks based robust federated learning for encrypted traffic
classification,” in Proc. Int. Conf. Comm. (ICC), May 28 - June 1, 2023.
Rome, Italy: IEEE, pp. 4937–4942.
[52] Z. Zhan, W. Zhao, Y. Li, W. Liu, X. Zhang, C. W. Tan, C. Wu, D. Guo,
and X. Chen, “Fedmoe-da: Federated mixture of experts via domain
aware fine-grained aggregation,” in Proc. 20th Int. Conf. Mobility,
Sensing Networking (MSN), 20-22 December, 2024. Harbin, China:
IEEE, pp. 122–129.
[53] H. Zhang, W. Liu, J. Shan, and Q. Liu, “Online active learning paired
ensemble for concept drift and class imbalance,” IEEE Access, vol. 6,
pp. 73 815–73 828, 2018.
[54] Z. Zhang, B. Guo, W. Sun, Y. Liu, and Z. Yu, “Cross-fcl: Toward a crossedge federated continual learning framework in mobile edge computing
systems,” IEEE Trans. Mob. Comput., vol. 23, no. 1, pp. 313–326, 2024.
[55] S. Zhu, X. Xu, H. Gao, and F. Xiao, “CMTSNN: A deep learning model
for multiclassification of abnormal and encrypted traffic of internet of
things,” IEEE Internet Things J., vol. 10, no. 13, pp. 11 773–11 791,
2023.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
