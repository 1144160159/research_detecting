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
# [765] Normality in Anomaly: Rethinking Traffic Labels
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
编号：765
题名：Normality in Anomaly: Rethinking Traffic Labels
年份：2026
DOI：10.1109/tdsc.2026.3688655
来源：IEEE Transactions on Dependable and Secure Computing
PDF：paper/10.1109_TDSC.2026.3688655.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：无
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\765.txt
- 原始字符数：104842
- 本次发送字符数：104842
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

1

Normality in Anomaly: Rethinking Traffic Labels
Chao Zha, Dakun Shen*, Ruyun Zhang, and Kui Ren, Fellow, IEEE

Abstract—Network traffic detection plays a critical role in
protecting digital infrastructures from increasingly sophisticated
cyber threats. Although AI-based detection methods have shown
clear advantages over traditional rule-based approaches, most existing approaches either rely on the unrealistic closed-set assumption or address distribution shifts only through model retraining
after data drift. As a result, the robustness of detection models
under fixed closed-set training conditions remains insufficiently
explored. To address this limitation, we revisit malicious traffic
modeling from an attacker’s perspective and formulate the detection process as a Min–Max adversarial optimization problem.
Instead of relying on conventional binary labels, we introduce
a self-generating mask mechanism with sparsity constraints,
which dynamically identifies malicious feature components and
produces adaptive labels during training. This design allows
the model to focus on attack-relevant feature dimensions while
suppressing benign patterns embedded within malicious traffic.
The proposed method is architecture-agnostic and can be integrated with multiple neural architectures, including multilayer
perceptrons and Transformers. Extensive ablation studies and
comparative evaluations conducted in a real-world environment
and three public datasets, CICIDS-2017, UNSW-NB15, and
Bot-IoT, demonstrate that the proposed approach consistently
outperforms existing baselines in terms of detection robustness
and classification performance, achieving improvements of up to
138% in accuracy, 65% in the F1 score and 52% in TPR.
Index Terms—Network traffic detection, traffic label, robustness, self-generating mask, adaptive label.

I. I NTRODUCTION
ETWORK traffic detection constitutes a critical component of modern security infrastructures, protecting a
wide range of services and applications against diverse and
sophisticated attacks [1]. In recent years, artificial intelligence
(AI)-driven traffic analysis techniques have been extensively
explored, due to their ability to extract complex patterns
from massive volumes of data [2]–[6]. Such capabilities make
them particularly promising for detecting traffic in openworld settings [7]–[11]. A substantial body of research has
already emerged, including efforts in traffic classification [12]–
[14], intrusion detection [7], [11], [15], [16], and advanced
persistent threat (APT) detection [17], [18].

N

This paper was produced by the IEEE Publication Technology Group. They
are in Piscataway, NJ.
Manuscript received April 19, 2021; revised August 16, 2021 (Corresponding author: Dakun Shen).
Chao Zha is with the Institute of Computing Technology, Chinese Academy
of Sciences, Beijing 100190, China; the University of Chinese Academy of
Sciences, Beijing 100049, China; and the Research Center for High Efficiency
Computing Infrastructure, Zhejiang Lab, Hangzhou 311500, Zhejiang, China.
(email: zhachao21@mails.ucas.ac.cn).
Dakun Shen, Kui Ren are with the School of Cyber Science and
Technology, and the College of Computer Science and Technology, Zhejiang University, Hangzhou, 310027, China. (email: dakun@zju.edu.cn,
kuiren@zju.edu.cn).
Ruyun Zhang is with the Research Center for High Efficiency Computing
Infrastructure, Zhejiang Lab, Hangzhou 311500, Zhejiang, China (email:
zcor2021@gmail.com).

TABLE I
COMPARISON WITH REPRESENTATIVE RELATED WORKS
Features

Closed-Set

Open-Set

Ours

Historical data
Drifted data
Label flexibility
Non-redundant features
Generalization
(

= true,

= partially true,

= false.)

Unfortunately, existing studies often prioritize improvements in benchmark metrics, often relying on a set of unrealistic assumptions that rarely hold in real-world deployments [19]. For example, many reported gains are achieved
under the closed-world assumption, where training and testing
data are drawn independently and identically from the same
distribution [20], [21]. In practice, this assumption is easily
violated: real network environments are inherently dynamic,
where concept drift is prevalent, and diverse attack traffic
emerges unpredictably over time [22]. As a result, models
trained under the closed-world assumption rapidly degrade,
since the distribution of test data under concept drift can differ
substantially from that of the original training set.
To address this challenge, open-set network traffic detection
research has gradually emerged to mitigate model failures
caused by concept drift [23], [24]. One line of work periodically trains models [25]–[29]; however, such strategies lack
proactive mechanisms for drift detection, making it difficult
to determine appropriate retraining intervals, and delayed
updates can lead to model collapse or a surge in false alarms.
Another line of work first detects distributional shifts and then
actively adapts the model after drift occurs [11], [30]–[32].
These approaches mainly focus on post-drift problems: taking
action only after new data become available, and according to
existing definitions, can be classified as open-set research.
Although open set approaches can achieve certain effectiveness after drift occurs [11], [31], they are inherently limited:
they rely on the presence of drift data to update the model and
therefore cannot provide timely defense or decision-making at
the moment drift emerges. In other words, existing methods
typically partition the continuously evolving cyberspace into
a sequence of closed sets and focus on transitions between
them, while largely overlooking attempts to study model
generalization using pre-drift data. Motivated by this gap, our
work explores a relatively underexamined direction: whether
pre-drift closed-set data can be leveraged to enhance model
generalization in open-set scenarios. Specifically, we aim to
investigate how a model can proactively withstand potential
unknown attacks or concept drift without relying on post-

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

drift data, thereby enabling preemptive defense and robust
detection. A more concise comparison between our research
and representative related works is presented in Table I.
a) Challenges: In existing network traffic detection research, the detection task is typically modeled as a standard
classification problem, where traffic samples are strictly black
and white labeled as benign or malicious. However, malicious traffic is not always an independent black sample; it
is often camouflaged within benign traffic, embedding malicious content to increase stealth and avoid detection. Models
optimized under the closed-set assumption with such blackand-white labels may achieve high classification performance
on test sets, but they often fail to capture traffic features
comprehensively, resulting in a large number of redundant
features. Although these redundant features may have little
impact on classification results within a closed set, they
can substantially undermine model generalization in open set
scenarios, including unknown or drifted traffic, leading to
degraded detection performance. Based on this analysis, three
core challenges arise: (1) how to enhance model generalization
on open set data using only closed set training data; (2) how
to redefine traffic labels so that models can more accurately
characterize the complexity of anomalous traffic; and (3) how
to mitigate the influence of redundant features during feature
extraction, thereby improving the robustness and stability of
detection models in open-world environments.
b) Our Work: We propose a general-purpose network
traffic detection method with strong generalization and high
robustness, which we call Camero (Camouflage Removal).
First, from the attacker’s point of view, we analyze the
possible strategies by which malicious traffic can masquerade
as benign traffic and model this scenario as a Min-Max
adversarial optimization problem. This formulation highlights
the limitations of naively classifying traffic as benign or
malicious (that is, a strictly black-and-white approach). Instead, malicious traffic should be regarded as the combination
of benign traffic and attacker-crafted deceptive perturbations.
Building on this framework, we introduce a self-generating
mask mechanism that leverages a mask loss to adaptively
capture the latent perturbations hidden within benign traffic. This approach abandons the traditional binary labeling
paradigm in favor of a self-generating mask and an adaptive
label modeling strategy. Furthermore, considering that an
attacker cannot arbitrarily manipulate all feature dimensions,
we incorporate a sparsity-constrained mask loss to ensure that
the mask focuses on key features rather than covering all
features indiscriminately. Finally, Camero jointly optimizes
the classification task using traditional cross-entropy loss,
mask loss, and sparsity-constrained mask loss, significantly
improving generalization and robustness to open-set data even
when trained solely on closed-set data. Importantly, Camero
is highly versatile, supporting multiple model architectures,
including multilayer perceptrons (MLPs) and Transformers
[33]. Nevertheless, the proposed framework is instantiated on
flow-level tabular representations derived from bidirectional
network flows. Therefore, the method is instantiated under the
NetFlow/flowmeter telemetry paradigm rather than a modalityagnostic security data interface.

2

c) Evaluation and Development: We conducted performance evaluation experiments in a real-world network
traffic environment. Raw data were collected from various
scenarios, including enterprise networks, research institutions,
educational institutions, and home networks. Malicious traffic
from publicly available datasets such as CICIDS-2017 [34],
UNSW-NB15 [35], and Bot-IoT [36] was injected, resulting
in three distinct datasets without overlap samples. One data
set was used for training, while the other two served as open
set test sets to evaluate the generalization and robustness
of the model. We used eight metrics to assess both overall
performance and fine-grained detection capability. Through
multiple ablation studies, we demonstrated that the proposed
self-generating mask strategy in Camero consistently improves
model generalization at both global and local levels. Furthermore, comprehensive comparisons with six widely discussed
state-of-the-art (SOTA) baselines highlight Camero’s superior
detection performance in open-set data, achieved without access to open-set samples during training. Camero consistently
outperforms all baselines in accuracy, F1 score and TPR, with
improvements of up to 138%, 65% and 52%, respectively.
Finally, in the Discussion section, we analyze factors such as
model parameter size and assess the suitability of the method
for real-world deployment, including its compliance with realtime requirements.
d) Contributions: The main contributions of this work
are summarized as follows:
• We revisit traffic labeling from an attacker’s perspective
and model malicious traffic as benign traffic with embedded perturbations, formulating traffic detection as a
Min-Max adversarial optimization problem.
• We propose Camero, a mask-based adversarial learning
framework that uses a self-generating mask to approximate hidden perturbations and guide the classifier to learn
perturbation-aware decision boundaries.
• We introduce a sparsity-constrained mask design to ensure that the learned perturbations focus on a limited
set of critical traffic features, improving robustness and
preventing trivial solutions where all features are masked.
e) Abbreviations: Table II presents all abbreviations
used in this paper together with their full expressions.
f) Paper Structure: The remainder of this paper is organized as follows. Section II reviews the related representative
work. Section III describes our threat model. In Section IV,
we describe the detailed design of our method. In Section V,
we experimentally evaluate the performance of our method.
Section VI discusses the usage of decoder in Camero, the
limitations of our proposed method and future work. Finally,
we conclude this paper in Section VII.
II. R ELATED W ORK
In this section, we provide an overview of existing closedset and open-set research on network traffic detection and
summarize the key findings in Table III.
a) Closed-set Methods: In recent years, great effort has
been put into building traffic detection systems using machine
learning (ML), which demonstrate superior accuracy compared to traditional deep packet inspection [37]–[39]. Several

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

TABLE II
L IST OF A BBREVIATIONS
Abbreviations

Full Expressions

AI
APT
MLP
SOTA
ML

Artificial Intelligence
Advanced Persistent Threat
Multilayer Perceptron
State of the Art
Machine Learning
Conditional Variational Autoencoders with
Extreme Value Theory
graph neural network
Point-wise Mutual Information
Strategy Selection and Forgetting
Temporal Fusion Encoder using Graph Neural
Network
Open World Anomaly Detection
True Positive Rate
False Positive Rate
Receiver Operating Characteristic
Precision–Recall
Denial of Service
Distributed Denial of Service
Command and Control
Cross Site Script

CVAE-EVT
GNN
PMI
SSF
TFE-GNN
OWAD
TPR
FPR
ROC
PRC
DoS
DDoS
C2
XSS

studies used statistical features with ML classifiers for traffic
detection [40]–[42]. Yang et al. [7] proposed a two-stage
learning framework that integrates Conditional Variational
Autoencoders with Extreme Value Theory (CVAE-EVT) to
classify known attacks and previously unseen ones, while
using benign traffic clustering to control the false-positive rate.
Mirsky et al. [43] proposed an unsupervised approach using
autoencoders for lightweight malicious traffic detection. Fu
et al. [44] extracted features of the frequency domain via a
discrete Fourier transform and combined them with clustering
algorithms such as K-Means for anomaly detection. Tang et
al. [45] used recurrent encoder-decoder neural networks to
model the syntactic and semantic patterns of benign requests,
identifying incomprehensible requests as potential attacks.
More recently, Fu et al. [58] introduced an unsupervised pointcloud analysis method that aggregates traffic features into
voxels and utilizes voxel density to reduce false positives in
malicious traffic detection. Zha et al. [59] proposed FlowXpert,
a self-supervised network flow representation learning framework that leverages clustering-generated pseudo labels and
contrastive learning to learn discriminative traffic embeddings.
Contrastive learning has also been widely applied to traffic
feature extraction. For example, Wu et al. [47] modeled the
traffic features of the network using a temporal contrastive
graph neural network (GNN). Huang et al. [48] incorporated
contrastive learning into transfer learning to enhance the
robustness of intrusion detection models. Wang et al. [49]
combined federated learning with contrastive learning, improving the representation of normal traffic while preserving user
privacy. Ma et al. [50] proposed specific data preprocessing
and contrastive task construction strategies to improve traffic
classification performance on imbalanced datasets. Furthermore, Yue et al. [46] applied random masking to network
packet sequences to construct contrastive tasks, thus improving
the model’s ability to perceive differences between samples.
Graph neural networks have increasingly attracted attention

3

for capturing interactive features within network traffic. For
example, Shen et al. [51] transformed fingerprint identification
into a graph classification problem by constructing graphs
of traffic interactions. Agiollo et al. [52] employed GNNs
to model the global network topology, enabling detection
of interest flood attacks based on non-local information. Li
et al. [53] proposed to construct event provenance graphs
using log correlation analysis to trace complex and previously
unseen APT activities. Zhang et al. [54] proposed a bytelevel traffic graph construction method based on point-wise
mutual information (PMI) and also designed a temporal fusion
encoder model. Using graph neural networks, their approach
enables efficient feature extraction from encrypted traffic. Fu
et al. [21] used unsupervised graph learning to analyze traffic
interaction patterns to detect encrypted traffic. Rehman et
al. [55] applied GNN to data provenance graphs, capturing
event features through semantic and contextual encodings, and
improving efficiency on large graphs through embedding reuse
mechanisms for APT detection. Furthermore, Ghadermazi et
al. [56] constructed packet-based graph structures using unsupervised GNN combined with graph autoencoders to perform
attack detection.
Since the relationship between benign and malicious traffic
is not strictly black-and-white, malicious flows often exhibit
a high degree of similarity to benign ones. This inherent
ambiguity undermines the generalizability of supervised learning methods that rely on cross-entropy loss and unsupervised
approaches such as clustering-based [44] or auto-encoders
[43], [45]. Although contrastive learning has achieved remarkable success in other domains, its effectiveness diminishes in
traffic detection tasks, where indistinct class boundaries make
it difficult to construct reliable positive and negative pairs.
Graph-based learning can capture richer interaction features
within traffic [21], [51]–[53], [55], [56]; however, building
graph representations typically incurs substantial computational overhead, which poses a serious challenge for real-time
detection. Moreover, these methods still rely on black-andwhite labeling as the optimization objective, which fails to
guide the model in accurately capturing the nuanced characteristics of malicious traffic. Finally, due to the absence of drifted
data, closed-set–based methods often struggle to generalize
when faced with open-set traffic.
b) Open-set Methods: Unlike closed-set research, openset approaches explicitly consider the presence of drifted data
and update detection models through adaptation strategies
to improve generalization. One common strategy is periodic
model retraining. For example, Cretu et al. [25] constructed
lightweight models and used a voting mechanism to automatically clean training data, thus improving the quality of
unlabeled samples and mitigating attacks targeting individual
sites through cross-network collaboration. In addition, Cretu
et al. [26] introduced a self-calibration phase to achieve fully
automated parameter tuning and maintenance for anomaly
detection sensors, which, combined with data cleaning, enables
online adaptation to traffic changes. Pendlebury et al. [27]
highlighted that the existing Android malware classification
results are often biased in both space and time. By incorporating constrained experimental design, robustness metrics,

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

4

TABLE III
COMPARING THE EXISTING NETWORK TRAFFIC DETECTION METHODS
High
Accuracy

Category of Detection Methods

Key findings

Rule-based Methods [37]–[39]

Predefined fix rules,
Explainable.

Closed-set
Methods

Statistical learning
[40]–[42]

Simple implementation, no
reliance on plaintext.

Unsupervised Learning
[43]–[45]

No labeling, reducing
manual intervention.

Contrastive learning
[46]–[50]

Better feature representation
and sample discrimination.

Graph learning [21],
[51]–[56]

Interactive features.

Retraining regularly
[25]–[29]

Improved generalization.

Adaptive methods [8],
[15], [30], [31], [57]

Automatically detect drift
and update.

Camero

Non-redundant features,
Label flexibility

Open-set
Methods

Ours
(= true,

= some methods meet this property,

Low False
Positive Rate

Open-set
Detection

Generalization

Realtime
Detection

= false.)

and tuning algorithms, they enabled reliable evaluation of
classifiers in real-world settings and provided an open source
framework to support fair comparison and performance optimization. Jan et al. [28] proposed a distribution-aware data
synthesis approach to train machine learning models with only
a limited amount of labeled data, facilitating the detection of
unknown or future bot behavior and improving model usability
and generalization. Wang et al. [29] addressed real-world
traffic drift and adversarial attacks by leveraging incremental
feature extraction and subclassifier generation, thus enhancing
detection performance.
Periodic retraining can, to some extent, improve generalization against drifted data; however, determining the appropriate
retraining interval is inherently challenging [8], and such
retraining often leads to forgetting historical knowledge, even
though past data may still persist in current network environments. To address this issue, adaptive drift detection and
model update techniques have been proposed. For example,
Andresini et al. [30] employed clustering-based drift detection
and leveraged a neighborhood strategy to generate pseudolabels to update detection models. Han et al. [8] introduced
a method that assigns different importance weights to the
model parameters, constraining updates to critical parameters
to mitigate catastrophic forgetting of prior knowledge, while
allowing less important parameters to adapt to new distributions. Yang et al. [31] designed a masking-based approach to
generate drift-sensitive perturbation vectors, align them with
historical representations, and then fine-tune a constrained
classifier using representative samples from historical data
to achieve adaptive learning. Zhang et al. [57] proposed an
incremental learning approach for intrusion detection, termed
SSF (Strategy Selection and Forgetting), which selectively
retains the most representative new samples to capture concept
drift, while discarding obsolete ones through a forgetting
mechanism. Zha et al. [11] combined historical data replay

using the conditional tabular generative adversarial network
with recent data to update detection models; however, replay
through generative models inevitably incurs information loss,
leading to degraded performance. Despite their progress, these
methods generally require access to drifted or historical data,
which not only fails to mitigate the immediate impact of
adversarial activities during drift events, but also offers limited
improvement in model generalization when drifted data are
absent.
c) Baselines Selection: We select several representative
baselines, including AppScanner [40], Kitsune [43], and FlowPrint [41] as classical closed-set traffic classification methods.
Meanwhile, we include CVAE-EVT [7], Temporal Fusion
Encoder using GNN (TFE-GNN) [54] is adopted for GNNbased traffic analysis, and Open-World Anomaly Detection
(OWAD) [8] is used for open-world anomaly detection. These
baselines are chosen because they cover diverse detection
paradigms, including closed-set, open-set, and adaptive settings, providing a broad perspective and enabling a more
comprehensive validation of our approach.
III. T HREAT M ODEL
In particular, we focus on robust network traffic detection
and assume a threat model as illustrated in Fig. 1.
a) Adversary’s Goal: The attacker’s goal is to generate
open-world camouflage attack samples that can evade detection by the network traffic analysis model. In other words, the
attacker seeks to conduct malicious activities while preserving
the outward appearance of benign communication, thereby
avoiding identification. Specifically, the attacker expects the
model to correctly classify benign traffic while failing to
recognize previously unseen malicious traffic as an attack.
b) Adversary’s Capabilities: We assume that the attacker
cannot directly influence the model training process and cannot
manipulate the training data or model parameters. However,

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

5

TABLE IV
D EFINITION OF M ATHEMATICAL S YMBOLS

Fig. 1. Threat Model.

the attacker can observe and collect partial statistical information about training data and has the ability to design
open-world attack strategies. Given the limited generalization
of traditional closed-set detection methods, the attacker can
exploit this weakness to evade detection.
c) Adversary’s Knowledge: We assume that the attacker
has no access to the model architecture, training procedure,
or internal detection mechanisms (e.g., automatic feature
extraction or robustness enhancements). However, they may
have a small set of unlabeled traffic samples from a similar
distribution and some known benign examples. The attacker
may also infer which salient features the system relies on and
exploit this to craft targeted adversarial examples.
d) Defense Assumptions: To counter the aforementioned
open-world threats, we assume that the traffic detection system
adopts a detection framework that integrates masking and
generative mechanisms. Specifically, the system leverages a
self-generating masking mechanism derived from latent variables during the classification optimization process to enhance
generalization while mitigating feature redundancy and model
overfitting. This design effectively addresses the robustness
and generalization limitations of closed-set methods and can
be realized solely with closed-set data, without requiring
access to open-world samples.
IV. M ETHODOLOGY
In this section, we provide a detailed analysis of the attackdefense problem and, on the basis of this formulation, propose
our corresponding practical solution.
A. Problem Statement

Notations

Definitions

D
Xi
yi
yˆi
f (·)
θ
θ∗
L
δi
∆
E(·)
Lce
M
ϵ
Lmce
Lcon
Lobj
α, β

The network traffic data.
The vectors of traffic flow features.
The traffic labels (benign or malicious).
The prediction labels (benign or malicious).
The detection model.
The parameters of detection model.
The robust parameters of detection model.
The loss function used in model optimization.
The perturbation applied to the input sample Xi .
The feasible set of perturbations.
The expectation operator over the data distribution.
The cross entropy loss function.
The mask to capture perturbations δ.
The mask constraint term.
The mask-based cross entropy loss function.
The sparsity constraint loss function.
The overall optimization goal.
The hyper-parameters used in Lobj .

fields, adjusting traffic rates, or inserting disguised packets, in
order to evade detection. Here, δ denotes the set of perturbations that the attacker can apply.
Consequently, the problem can be formalized as the following min-max adversarial optimization problem:
h
i
min E(Xi ,yi )∼D max L fθ (Xi + δi ), yi .
(2)
θ

δ∈∆

Specifically:
• Inner maximization (attacker): Identifies the most misleading perturbations that cause the detector to misclassify, thus maximizing the loss function.
• Outer minimization (defender): Optimizes the parameters of the detection model to maintain detection accuracy
even under worst-case perturbations.
This Min-Max framework characterizes the zero-sum game
between the attacker and the defender: The attacker aims
to compromise the effectiveness of the detector, whereas the
defender leverages adversarial training to enhance the robustness of the model. The ultimate objective is to obtain robust
parameters θ∗ such that the model maintains high detection
performance even under optimal perturbations by the attacker,
that is,
θ∗ = arg min max L(fθ (Xi + δi ), yi ).
(3)
θ∈Θ δ∈∆

In the cybersecurity setting, we formulate an adversarial
optimization problem from the perspective of the attacker,
where both the attacker and the defender are involved. Table
IV presents all mathematical symbols used in this paper
together with their definitions.
Firstly, let the network traffic data set be denoted as
D = {(Xi , yi )}N
i , yi ∈ {0, 1},

(1)

where Xi ∈ Rd represents the vectors of traffic flow features
and yi denotes the corresponding labels (benign or malicious).
The detection model f is parameterized by θ ∈ Θ, and its
associated loss function is denoted as L(fθ (Xi ), yi ).
In practical deployment scenarios, an attacker may apply
subtle perturbations to benign traffic, such as modifying packet

This modeling approach provides a theoretical foundation
for analyzing the robustness of traffic detection systems.
B. Practical Solution
From the defender’s perspective, the primary objective is
not to impose a simplistic binary judgment that categorizes
an entire flow as benign or malicious. Instead, the goal
is to accurately identify and isolate fine-grained adversarial
perturbations δ hidden within otherwise benign traffic. Such
perturbations are often deliberately crafted to embed malicious
components without disrupting the overall semantics of benign
traffic, thereby significantly enhancing the stealthiness and
evasiveness of the attack. Conventional detection approaches

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

tend to be fragile when faced with this type of mixed traffic. To
address this challenge, we propose a new paradigm: leveraging
adversarial training to guide the model in recognizing and capturing these hidden perturbations, rather than indiscriminately
labeling the entire flow as malicious.

6

Specifically, in addition to the standard cross-entropy loss
defined in Eq. (4), Camero incorporates a mask-based crossentropy loss Lmce , formulated as follows.

Lmce = Lce fθ (Xi ⊙ (1 − M )), 0
(

(7)
Lce fθ (Xi ⊙ M ), 0 , yi is benign,

+
Lce fθ (Xi ⊙ M ), 1 , yi is malicious.
In Eq. (7), the mask employs a soft label strategy, indicating
that during optimization, the application of the mask does
not affect the classification of benign traffic. However, for
malicious traffic, the mask enables the model to correctly
identify it as malicious when applied and to classify it as
benign when the mask is inverted.
Furthermore, considering that real-world attacks do not
apply perturbations indiscriminately across all feature dimensions, and that the detection model must maintain its ability to
distinguish between malicious and benign traffic under limited
perturbations, we introduce a sparsity constraint in the mask
design. This ensures that the mask focuses on critical features
rather than covering all dimensions. The corresponding loss
constraint Lcon is formulated as follows:
Lcon = max(0, ||M ||1 − ϵ).

Fig. 2. The overview of Camero.

Motivated by this insight, we propose a self-generating
masking mechanism based on decoder to characterize and
extract potential adversarial perturbations δ and integrate it
with the loss of cross-entropy of standard classification to
construct a robust network traffic detection model, named
Camero, as illustrated in Fig. 2. In terms of the classification
task, Camero still adheres to the conventional supervised
learning paradigm, consisting of an encoder followed by a
fully connected classification head, and optimized with crossentropy loss Lce :

(8)

Therefore, the overall goal of the optimization Lobj of
Camero can be formally expressed as follows:
Lobj = Lce + α · Lmce + Lcon ,

(9)

where α is hyperparameters.
C. Training Process

M :∥M ∥1 <ϵ

Camero effectively addresses the limited generalizability of
existing traffic detection models when relying solely on closedset data. Unlike conventional binary labeling approaches,
Camero introduces a more robust self-generating mask mechanism that adversarially captures deceptive perturbations embedded within malicious traffic. By adopting the attacker’s
perspective, this design enables the construction of a traffic
detection model with significantly improved robustness. The
complete training process is detailed in Algorithm 1. Importantly, our approach is model-agnostic: it can be seamlessly applied to different model architectures. In our experiments (see
§ V), we verify that Camero consistently improves robustness
and detection accuracy on both MLP-based and transformerbased models.

Lce = Lce (fθ (Xi ⊙ M ), 1) + Lce (fθ (Xi ⊙ (1 − M )), 0), (6)

V. E XPERIMENTAL E VALUATION

N
i
1 Xh
Lce = −
yi log ŷi + (1 − yi ) log(1 − ŷi )
N i=1

(4)

The key distinction lies in the fact that we use the latent
variables generated during the classification decision process
to produce an effective mask M to capture perturbations δ. As
formalized in Eq. (2), the adversarial objective of the attacker
can be expressed as follows:
h
i
′
min Lce (fθ , Xi , yi ) + max Lce (fθ , Xi , M, yi ) , (5)
θ

′

where ϵ denotes the mask constraint term.
In other words, the attacker aims to select a mask M
that maximizes the difficulty of the model in distinguishing
between benign and malicious traffic, while the defender tries
to adjust the model parameters to minimize the overall loss.
By explicitly introducing the self-generating mask mechanism,
the model is guided during optimization to simultaneously
preserve the overall classification accuracy of the traffic and
capture embedded adversarial perturbations δ.

A. Experiment Setup
a) Implementation: Our prototype is implemented in
Python (3.8.12) and C++ (g++ 10.5.0), the feature extraction
tool is built using C++, and the other modules are built using
scikit-learn [60] and PyTorch (2.0.1+cu117) [61].
b) Tested: We deployed Camero on a computer with the
following main configuration: Intel(R) Xeon(R) Gold 6138
CPU @ 2.00GHz, Ubuntu 20.04.6 LTS, 64GB DRAM, and
512GB SSD.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

Algorithm 1 Training process of Camero
Require: Network traffic dataset D = {(Xi , yi )}N
i=1 , detection model fθ , decoder model Dec, hyperparameters α, β,
mask constraint ϵ, number of epochs E, learning rate η.
1: for ep := 1, 2, ..., E do
2:
# Stage 1: → goal: Compute standard CE loss Lce .
3:
ŷ, z ← fθ (X)
4:
Lce ← use Eq. (4)
5:
6:
7:
8:
9:
10:

# Stage 2: → goal: Compute masked CE loss Lmce .
M ← Dec(z)
Lmce ← use Eq. (7)
# Stage 3: → goal: Compute constraint loss Lcon .

11:
Lcon ← use Eq. (8)
12:
13:
Lobj ← Lce + α · Lmce + β · Lcon
14:
fθ ← fθ − η · ∇fθ · Lobj
15:
Dec ← Dec − η · ∇Dec · Lobj
16: end for
17: return

Detection model fθ .

c) Model Details: To evaluate the general applicability
of our proposed game-based masking mechanism to enhance
model generalization, we used two widely used base model
architectures to construct the encoder and decoder: a multilayer perceptron (MLP) [62], [63] and a transformer [33],
as illustrated in Fig. 3. The MLP-based encoder and decoder
are each composed of three fully connected layers interleaved with two LeakyReLU activation layers [64]. In another
configuration, the Transformer-based encoder consists of N
stacked attention blocks, where each block includes a MultiHead Self-Attention layer and a Feed-Forward layer, along
with the corresponding Residual Connections [65] and Layer
Normalization components [66]. In the following, Camero-M
and Camero-T refer to the prototypes built using the MLP and
Transformer architectures, respectively.

(a) MLP-based Encoder &
Decoder.

(b) Transformer-based Encoder & Decoder.

Fig. 3. Model Architectures.

d) Baselines: We used seven SOTA methods as baselines
for comparison, in order to evaluate Camero’s generalization
ability to open world traffic, demonstrating its superiority over
SOTA methods.

7

Kitsune (K.S.): Mirsky et al. [43] introduced an unsupervised method based on autoencoders to enable
lightweight detection of malicious traffic.
• Appscanner (A.S.): Taylor et al. [40] proposed a traffic
detection system that uses statistical traffic features to
identify mobile applications.
• Flowprint (F.P.): Ede et al. [41] introduced a semisupervised method that derives application fingerprints by
exploiting temporal correlations among relevant traffic
features.
• CVAE-EVT (C.E): Yang et al. [7] proposed a two-stage
learning framework that integrates a CVAE with EVT,
while incorporating clustering to reduce false positives.
• TFE-GNN (T.G.): Zhang et al. [54] introduced a PMIbased byte-level traffic graph and a GNN-driven temporal fusion encoder to efficiently extract features from
encrypted traffic.
• OWAD (O.A.): Han et al. [8] proposed assigning importance weights to parameters, preserving crucial ones
against forgetting while allowing others to adapt.
• FlowXpert (F.X.): Zha et al. [59] proposed a selfsupervised framework that learns network traffic embeddings via clustering-based pseudo labels and contrastive
learning.
e) Metrics: We use the following metrics [67] to evaluate
the detection accuracy: (i) Accuracy, true positive rates (TPR),
false positive rates (FPR), (ii) Precision (P.R.), Recall (R.C.),
F1 score (F.S.), (iii) the area under the Receiver Operating
Characteristic (ROC) curve, and (iv) the area under the Precision–Recall (PRC) curve. Moreover, we measure throughput
and processing latency to demonstrate that Camero achieves
real-time detection.
•

B. Datasets
The attack traffic used in our experiments is sourced from
three widely adopted public datasets: CICIDS-2017 [34],
UNSW-NB15 [35], and BoT-IoT [36]. In addition, we capture
benign traffic from a variety of real-world environments,
including enterprise, industrial, and residential networks, and
inject the attack traffic into these real flows to construct openworld datasets that allow a thorough evaluation of the generalizability of the model. Specifically, we first extracted attack
traffic samples from external datasets and then integrated them
with the target dataset at the flow level, achieving results consistent with traffic replay. Throughout this process, all samples
employed the same feature representation and identical data
preprocessing procedures, without introducing any identifiers
or additional features related to the data source. Moreover,
during flow feature extraction and model training, we paid
particular attention to information that could potentially be
correlated with labels, such as IP addresses and ports. These
pieces of information were only used during the construction
of flows and were not involved in model training, effectively
eliminating any potential influence on the model. These data
sets are denoted as D-I, D-II, and D-III. Importantly, the
traffic contained in these datasets has no overlap, and each
originates from distinct network environments. Specifically,

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

our evaluation covers a diverse set of attack categories, including the following:
Brute-Force Attacks: This includes FTP-Patator, SSHPatator, and Web-Bruteforce, which attempt to gain legitimate credentials or session tokens by systematically
trying large numbers of username/password combinations. These attacks can lead to account compromise,
data leakage, unauthorized access, and, through lateral
movement, broader network damage [68].
• Denial of Service (DoS): This includes DoS-GoldenEye,
DoS-Slowhttptest, DoS-Slowloris, DoS-Hulk, and DDoSLOIT, which aim to exhaust target resources (bandwidth,
connections, central processing unit (CPU), or memory)
and block legitimate access [69]–[71]. Attacks from a
single machine are DoS, whereas attacks from multiple
hosts are distributed DoS (DDoS). Both are common and
frequent attacks.
• Scanning and Reconnaissance: This includes Portscan,
Service Scan, and Operation System Scan, which probe
open ports and service versions on target networks or
hosts to identify potential vulnerabilities or entry points
[72]. Low-speed scans (e.g., slow port scans) are often
difficult to distinguish from legitimate traffic, posing
challenges for detection systems.
• Distributed Botnets: This includes Botnet, Backdoor, and
Worms, where a large number of infected hosts (bots)
are controlled by a single command-and-control (C2)
server to launch coordinated DDoS attacks, send spam,
propagate malware, or perform proxy attacks [73]. Traffic
may exhibit similar patterns originating from numerous
distributed sources, and periodic communication to the
same C2 domain or IP can often be observed.
• Web Application Attacks: This includes Cross-Site Script
(XSS) and Structured Query Language (SQL) injection,
which target vulnerabilities in web application logic or
input validation [74], [75]. XSS injects malicious scripts
to compromise client-side behavior, while SQL injection
manipulates back-end database queries through crafted
inputs, potentially leading to data leakage, session hijacking, persistent backdoors, and unauthorized modification
of web content.
• Protocol Exploits: This includes Heartbleed, Fuzzers,
Exploits, and Shellcode, which exploits flaws in protocols
or their implementations (e.g. Heartbleed vulnerability in
OpenSSL) to read memory that should not be accessible
or perform unauthorized operations [76]. Such attacks
can lead to the leakage of sensitive data, including
cryptographic keys and credentials, and result in severe
trust violations.
• Generic or Unknown Attacks: This includes generic attacks that do not fall into standard categories or combine
multiple attack patterns. These are useful for evaluating
detection methods against unknown or novel attacks.

•

Some features that could potentially leak label information,
such as IP addresses and ports, were excluded from the
training process to explicitly prevent any inadvertent cheating
[19], as the majority of the samples in the data sets are

8

concentrated within a limited set of IPs or ports. Labeling
was performed according to the rules provided in the original
dataset publications [34]–[36] while addressing known issues
previously reported, such as incorrect labels [77].
In addition, context-sensitive session features were used to
construct model input vectors, as extracted by the proposed
FlowVision [59] bidirectional flow feature extraction tool. The
definitions of the specific features used in our experiments are
summarized in Table V. Furthermore, in all our experiments,
only a subset of D-I was used for model training, which was
divided into training and validation sets with a 7: 3 ratio. The
D-II and D-III data sets were excluded from the training and
only reserved to evaluate the generalizability of the model.
TABLE V
FEATURES USED IN OUR EXPERIMENTS
Type

Features

Description

protocol
flow dur

The protocol of transmission layer.
The duration of the flow.
The mean value of inter-arrival time
(iat) between packets.
The standard deviation of iat between
packets.
The total FIN packets of the flow.
The total SYN packets of the flow.
The total RST packets of the flow.
The total packets of the flow.
The packets per second of the flow.

iat mean
Flow-Level

iat std
fin num
syn num
rst num
pkt num
pkts per sec
num s port

Context-Aware
num d ip
num d port
con per sec

The number of distinct source ports
used by the same source IP.
The number of distinct destination IPs
contacted by the same source IP.
The number of distinct destination
ports accessed by the same source IP.
The number of connections established
per second by the source IP.

It should be noted that a portion of the benign traffic in the
dataset is overly simplistic and can be easily allowed through
by rule-based mechanisms in practical deployment. Therefore,
in our experiments, this subset of traffic was excluded from
the testing of both the Camero and the baseline methods.
Including these samples in the evaluation could not only
increase network latency, but could also potentially inflate the
performance metrics, thereby affecting an accurate assessment
of the actual performance differences.
C. Evaluation of Camero and Ablation Experiments
In this experiment, we conducted an ablation study on
Camero in two model architectures, MLP and Transformer,
to compare performance with and without the self-generating
mask mechanism. We perform a comprehensive evaluation of
the models using metrics such as accuracy, F1 score, and TPR,
with the results presented in Fig. 4a and Fig. 4b. During
training, Camero was trained exclusively on data sets D-I,
while data sets D-II and D-III remained completely unseen
to simulate an open-world scenario.
The experimental results demonstrate that incorporating
the self-generating mask mechanism consistently improves
Camero performance in both the MLP and Transformer architectures. Specifically, on data sets D-II and D-III, all 12

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

9

(a) Accuracy, F1 score, TPR of Camero-M.

(b) Accuracy, F1 score, TPR of Camero-T.

(c) Fine grained detection (Recall) of Camero-M.

(d) Fine grained detection (Recall) of Camero-T.

(e) Fine grained detection (F1 score) of Camero-M.

(f) Fine grained detection (F1 score) of Camero-T.

Fig. 4. Ablation experiments of Camero.

evaluation metrics show superior results compared to models
without the mask, indicating that the self-generating mask
significantly improves the generalization capacity of the model
and is effective in different architectures, highlighting its
versatility. In detail, in data set D-II, Camero-M achieves an
increase in accuracy from 0.77 to 0.86, an F1 score from 0.73
to 0.85 and a TPR from 0.59 to 0.76; Camero-T shows an
increase in accuracy from 0.81 to 0.90, an F1 score from 0.79
to 0.90, and a TPR from 0.65 to 0.84, corresponding to an
overall improvement of approximately 10%–30%. In the DIII data set, the accuracy of Camero-M increases from 0.78
to 0.81, the F1 score from 0.74 to 0.78, and the TPR from
0.61 to 0.66; the accuracy of Camero-T increases from 0.78
to 0.87, the F1 score from 0.76 to 0.86, and the TPR from
0.64 to 0.78, with overall gains of approximately 5%-20%.
D. Evaluation of Fine Grained Attack Detection
Considering the significant class imbalance in network
traffic datasets, for instance, benign traffic samples are often
several times more numerous than certain attack types, relying
solely on overall metrics such as accuracy cannot sufficiently
capture the improvements in detection performance. Therefore,
we further evaluate the fine-grained detection capability of
Camero. The experimental setup is largely consistent with §
V-C, and we adopt the recall and the F1 score as evaluation
metrics. Recall provides a direct measure of the model’s ability
to identify each specific attack type, without being obscured
by the dominance of benign traffic or aggregated attack categories. F1 score, which combines precision (false positives)
and recall (false negatives), offers a more comprehensive
assessment of the effectiveness of the model in detecting
individual classes. The evaluation results are presented in Fig.
4c - Fig. 4f.

Based on the experimental results, we observe that both
Camero-M and Camero-T consistently achieve higher recall
and F1 scores across all 13 fine-grained attack categories
compared to their counterparts without the self-generating
masking strategy. In particular, Camero-M exhibits substantial improvements for categories that are traditionally more
challenging. For example, recall in DoS increases from 0.73
to 0.83, Fuzzers from 0.62 to 0.80, and Reconnaissance from
0.57 to 0.75, corresponding to relative gains of approximately
15%–30%. Even in categories with inherently lower baseline performance, such as Backdoor and Worms, Camero-M
achieves notable increases (0.45 to 0.57 and 0.31 to 0.42,
respectively). Camero-T also shows even more pronounced
improvements. For instance, in DoS, recall rises from 0.75 to
0.88, in Generic from 0.76 to 0.89, and in Exploits from 0.73
to 0.89. Moreover, in Service Scan and OS Scan, CameroT achieves increases of 0.75 to 0.83 and 0.70 to 0.85,
respectively, highlighting the model’s ability to generalize
across diverse attack patterns. In general, Camero-T achieves
consistent gains ranging from 10% to more than 20% in
most categories, underscoring that the self-generating mask
not only improves the average detection performance, but also
strengthens the robustness in the more unbalanced and difficult
attack classes.
E. Feature Ablation Analysis
Considering that the masking mechanism introduced in
Camero is designed to suppress certain features, reduce the
influence of less informative features during the decision
process, and enhance the impact of more important ones,
we further conduct a feature-subset–based ablation study to
verify the effectiveness of this mechanism and strengthen the
persuasiveness of the proposed method. Specifically, we design

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

a controlled experiment in which, while keeping the model
architecture and training parameters as consistent as possible,
half of the features are randomly selected as input and compared with Camero using the complete feature set with the
masking mechanism enabled. By comparing the performance
differences between these two settings, we can more clearly
evaluate the contribution of the masking mechanism to the
model’s decision-making capability. The experimental results
are illustrated in Fig. 5.

(a) Feature Ablation Analysis of Camero-M.

10

susceptible to the omission of critical traffic statistical information. In contrast, Camero’s masking mechanism is adaptively
optimized during the training process, enabling the model to
assign importance weights to features based on their relevance
to the classification objective. This targeted feature modulation
not only preserves key discriminative information but also
enhances the overall robustness and reliability of the model.
F. Sensitivity Analysis
To evaluate the robustness of the proposed method with
respect to key hyperparameters, we conducted a sensitivity
analysis on two important parameters, α and ϵ. As illustrated
in Fig. 6, we varied α from 0.05 to 0.30 and ϵ from 0.35 to
0.60, and report the corresponding Accuracy and TPR on three
datasets (D-I, D-II, and D-III).

(b) Feature Ablation Analysis of Camero-T.

Fig. 5. Ablation experiments of Camero.

From the ablation results shown in Fig. 5, the robustness
advantage of Camero over the random subset (Subset) method
can be clearly observed. Overall, under both the Camero-M
and Camero-T experimental settings, Camero demonstrates
more stable and consistent performance across the Accuracy,
F1-score, and FPR metrics. This indicates that the masking
mechanism employed by Camero is more effective than simple
random feature subset selection in preserving the model’s
discriminative capability.
First, regarding Accuracy and F1-score, Camero consistently demonstrates higher or more stable performance across
the three datasets (D-I, D-II, and D-III). For example, on D-I
and D-II, Camero’s Accuracy and F1-score are significantly
higher than those of the random subset method, while on DIII, the performances are closer but Camero still maintains
a modest advantage. This indicates that Camero’s masking
mechanism can preserve strong classification capability even
when some features are perturbed or suppressed, whereas
randomly selecting a feature subset is more likely to remove
critical discriminative features, causing performance fluctuations. Second, for the FPR metric, Camero shows a more pronounced advantage. Across all three datasets, Camero maintains a consistently low FPR, while the random subset method
exhibits noticeable variability, with significant increases on
some datasets. This suggests that randomly dropping features
can disrupt the model’s ability to characterize normal traffic
patterns, leading to more false positives. In contrast, Camero
learns targeted masks that perturb the input features in a more
informed manner, effectively preserving detection capability
while controlling the FPR.
This performance discrepancy highlights the fundamental
distinction between Camero’s learned masking mechanism and
a naı̈ve random feature subset approach. The random subset
strategy indiscriminately samples input features, rendering it

(a) Sensitivity Analysis of α on D-I.

(b) Sensitivity Analysis of ϵ on D-I.

(c) Sensitivity Analysis of α on D-II.

(d) Sensitivity Analysis of ϵ on D-II.

(e) Sensitivity Analysis of α on D-III.

(f) Sensitivity Analysis of ϵ on D-III.

Fig. 6. Sensitivity Analysis of Hyperparameters.

From the results, it was observed that the performance
remained relatively stable across most parameter settings,
indicating that the proposed method was not highly sensitive
to moderate changes in the hyperparameters. However, when
the parameter values were relatively small, larger fluctuations
in performance were observed. In particular, a small value of
α weakened the sparsity constraint imposed by the mask regularization term, which reduced its ability to effectively guide
the model to informative feature dimensions. Similarly, when
ϵ was too small, the proportion of features that participated in
the inference process became limited, weakened the robustness
of the model and led to an unstable detection performance.
As the values of α and ϵ increased to moderate ranges, the
model achieved more stable and reliable performance in all
datasets. Overall, these results demonstrated that the proposed

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

framework maintained stable performance within a reasonably
wide parameter range, while excessively small parameter
values could reduce the effectiveness of the regularization and
robustness mechanisms.
G. Comparison with SOTA Methods
To highlight Camero’s improvements in terms of generalization to open-world traffic, we conduct a fair comparison
against six representative state-of-the-art approaches: Kitsune
[43], Appscanner [40], Flowprint [41], CVAE-EVT [7], TFEGNN [54], OWAD [8] and FlowXpert [59]. All methods
are trained on the D-I dataset (where different approaches
construct their corresponding input representations from the
same raw data) to ensure consistency. The evaluation is carried
out multiple times on three complementary aspects, enabling
a comprehensive and unbiased evaluation.
1) Evaluation of Overall Performance: We first compared
Camero with six baseline methods using four evaluation
metrics. Accuracy, F1 score, TPR and FPR, in order to assess
overall performance improvement. The results are presented
in Table VI and Table VII. For clarity, the performance
differences (improvements or degradations) of the baseline
methods are reported relative to the best results achieved by
Camero and vise versa.
TABLE VI
COMPARISON WITH SOTA METHODS ON D-II DATASET
Methods

Accuracy

F1 score

TPR

FPR

K.S
A.S
F.P.
C.E.
T.G.
O.A.
F.X.

0.491 ▼41%
0.585 ▼32%
0.853 ▼4%
0.755 ▼16%
0.380 ▼52%
0.741 ▼16%
0.819 ▼8%

0.220 ▼68%
0.853 ▼5%
0.704 ▼20%
0.722 ▼18%
0.798 ▼10%

0.136 ▼70%
0.700 ▼13%
0.554 ▼28%
0.641 ▼19%
0.682 ▼15%

0.115 ▲10%
0.264 ▲24%
0.008 ▼1%
0.022 —
0.010 —
0.148 ▲13%
0.029 —

Camero-M
Camero-T

0.863 ▲1%
0.904 ▲5%

0.854 ▲0%
0.901 ▲5%

0.759 ▲6%
0.832 ▲13%

0.021 ▲1%
0.017 ▲1%

- means that the value is lower than 0.10.

11

5% and 5%, respectively, while also achieving the highest
TPR of 0.832. Importantly, both Camero-M and CameroT maintain very low FPR values (0.021 and 0.017), which
are comparable to the lowest baseline values. This is crucial
because a higher FPR would lead to a substantial number
of benign flows being falsely flagged as malicious, thereby
disrupting normal business operations. In the D-III data set,
Camero again demonstrates consistent improvements. CameroT achieves an accuracy of 0.870 and an F1 score of 0.864,
improving over the strongest baseline (C.E.) by 7% and 8%,
respectively. Similarly, its TPR reaches 0.782, showing an
11% gain over the best baseline. Meanwhile, Camero-M also
matches or outperforms baselines with accuracy of 0.805 and a
F1 score of 0.780. In particular, both Camero-M and CameroT achieve very low FPRs (0.031 and 0.032), outperforming
most baselines such as O.A. (0.464) and A.S. (0.152), thus
significantly reducing the risk of benign traffic misclassification. Overall, the results in both datasets demonstrate that
Camero consistently achieves higher accuracy, F1 score, and
TPR, while maintaining exceptionally low FPR values. This
balance between strong detection capability and minimal false
alarms highlights Camero’s effectiveness and practicality for
real-world deployment.
Secondly, we further compared Camero with the baseline
methods using ROC and PRC curves, as shown in Fig. 7. For
clarity, baselines with an AUC lower than 0.5 were omitted
from the graphs.

(a) ROC on D-II.

(b) PRC on D-II.

(c) ROC on D-III.

(d) PRC on D-III.

TABLE VII
COMPARISON WITH SOTA METHODS ON D-III DATASET
Methods

Accuracy

F1 score

TPR

FPR

K.S.
A.S.
F.P.
C.E.
T.G.
O.A.
F.X.

0.740 ▼13%
0.807 ▼7%
0.564 ▼31%
0.804 ▼7%
0.639 ▼24%
0.341 ▼53%
0.713 ▼16%

0.715 ▼15%
0.152 ▼71%
0.334 ▼53%
0.784 ▼8%
0.210 ▼65%
0.684 ▼18%

0.620 ▼16%
0.257 ▼53%
0.211 ▼57%
0.674 ▼11%
0.167 ▼62%
0.590 ▼19%

0.127 ▲9%
0.152 ▲12%
0.003 ▼3%
0.050 ▲2%
0.002 ▼3%
0.464 ▲43%
0.149 ▼12%

Camero-M
Camero-T

0.805 ▲0%
0.870 ▲7%

0.780 ▲0%
0.864 ▲8%

0.657 ▲0%
0.782 ▲11%

0.031 ▲3%
0.032 ▲3%

- means that the value is lower than 0.10.

Comparison with baselines in the D-II and D-III datasets
highlights the superior performance of Camero in terms of
both detection capability and reliability. In the D-II data
set, Camero-T achieves the highest accuracy (0.904) and
the F1 score (0.901), surpassing the best baseline (F.P.) by

Fig. 7. Comparison with SOTA methods using ROC and PRC curves.

From the ROC results on D-I and D-III, Camero-M and
Camero-T achieve significantly higher TPR under the same
FPR compared with existing methods, highlighting their
stronger discriminative capability while maintaining a low
false alarm rate. In the PRC results of D-II and D-III, Camero
again demonstrates clear advantages, maintaining higher precision across a wide range of recall levels. In contrast, several
baselines suffer from a rapid drop in precision when recall
increases, indicating that they generate many false alarms

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

12

TABLE VIII
FINE GRAINED EVALUATION OF CAMERO AND THE BASELINES ON D-II AND D-III DATASET.
Attacks

Metrics

K.S.

A.S.

DoS

P.R.
R.C.
F.S.

0.205 ▼71%
0.133 ▼71%
0.042 ▼84%

-

0.639 ▼28% 0.832 ▼8% 0.326 ▼59% 0.509 ▼41% 0.845 ▼7% 0.891 ▲5%
0.700 ▼15% 0.499 ▼35%
0.694 ▼15% 0.728 ▼12% 0.782 ▲6%
0.667 ▼22% 0.624 ▼26%
0.588 ▼30% 0.782 ▼10% 0.833 ▲5%

0.919 ▲7%
0.849 ▲12%
0.883 ▲10%

Gen.

P.R.
R.C.
F.S.

0.206 ▼71%
0.149 ▼72%
0.173 ▼72%

-

0.640 ▼27% 0.822 ▼9% 0.184 ▼73% 0.469 ▼44% 0.834 ▼8% 0.881 ▲5%
0.700 ▼17% 0.519 ▼35%
0.656 ▼21% 0.741 ▼13% 0.788 ▲5%
0.668 ▼22% 0.637 ▼27%
0.547 ▼34% 0.785 ▼11% 0.832 ▲5%

0.913 ▲8%
0.869 ▲13%
0.890 ▲11%

Rec.

P.R.
R.C.
F.S.

0.162 ▼73%
0.127 ▼65%
0.142 ▼68%

-

0.654 ▼24% 0.834 ▼6% 0.194 ▼70% 0.389 ▼50% 0.777 ▼11% 0.848 ▲1%
0.700 ▼7% 0.645 ▼13%
0.540 ▼23% 0.589 ▼18% 0.675 ▼2%
0.676 ▼15% 0.728 ▼10%
0.452 ▼38% 0.670 ▼16% 0.752 ▲2%

0.891 ▲6%
0.775 ▲7%
0.829 ▲10%

Fuz.

P.R.
R.C.
F.S.

0.187 ▼70%
0.151 ▼65%
0.167 ▼68%

-

0.655 ▼24% 0.830 ▼6%
0.700 ▼10% 0.625 ▼17%
0.676 ▼17% 0.713 ▼13%

0.416 ▼48% 0.780 ▼11% 0.862 ▲3%
0.607 ▼20% 0.600 ▼20% 0.759 ▲6%
0.494 ▼35% 0.678 ▼17% 0.808 ▲9%

0.894 ▲6%
0.800 ▲10%
0.845 ▲13%

Exp.

P.R.
R.C.
F.S.

0.170 ▼73%
0.135 ▼76%
0.150 ▼74%

-

0.654 ▼25% 0.777 ▼12% 0.287 ▼61% 0.469 ▼43% 0.820 ▼8% 0.871 ▲7%
0.700 ▼17% 0.447 ▼43%
0.753 ▼12% 0.768 ▼11% 0.818 ▲5%
0.676 ▼21% 0.567 ▼32%
0.578 ▼31% 0.793 ▼9% 0.844 ▲5%

0.903 ▲8%
0.875 ▲11%
0.889 ▲9%

Shco.

P.R.
R.C.
F.S.

0.103 ▼72%
0.128 ▼65%
0.114 ▼68%

-

0.568 ▼26% 0.754 ▼7%
0.700 ▼7% 0.663 ▼11%
0.627 ▼17% 0.705 ▼9%

-

0.254 ▼57% 0.667 ▼12% 0.761 ▲1%
0.491 ▼28% 0.573 ▼20% 0.653 ▼5%
0.335 ▼46% 0.617 ▼18% 0.703 —

0.828 ▲7%
0.772 ▲7%
0.799 ▲9%

Anal.

P.R.
R.C.
F.S.

0.013 ▼54%
0.075 ▼91%
0.023 ▼69%

-

0.390 ▼16% 0.317 ▼24%
0.700 ▼29% 0.504 ▼49%
0.501 ▼21% 0.390 ▼32%

-

0.101 ▼45% 0.388 ▼17% 0.483 ▲9% 0.553 ▲16%
0.813 ▼18% 0.908 ▼8% 0.959 ▲5% 0.990 ▲8%
0.180 ▼53% 0.544 ▼17% 0.643 ▲10% 0.710 ▲17%

Bac.

P.R.
R.C.
F.S.

0.025 ▼51%
0.132 ▼71%
0.042 ▼61%

-

0.351 ▼18% 0.341 ▼19%
0.700 ▼14% 0.520 ▼32%
0.467 ▼19% 0.420 ▼21%

-

0.095 ▼44% 0.342 ▼19% 0.455 ▲10% 0.532 ▲18%
0.701 ▼14% 0.687 ▼16% 0.793 ▲9% 0.842 ▲14%
0.167 ▼49% 0.456 ▼20% 0.578 ▲11% 0.652 ▲19%

Wor.

P.R.
R.C.
F.S.

0.013 ▼37%
0.111 ▼67%
0.023 ▼49%

-

0.219 ▼17% 0.250 ▼13%
0.700 ▼8% 0.566 ▼22%
0.333 ▼18% 0.347 ▼17%

-

0.224 ▼16% 0.302 ▲5%
0.645 ▼14% 0.645 ▼5% 0.696 —
0.100 ▼41% 0.332 ▼18% 0.422 ▲8%

0.386 ▲13%
0.786 ▲8%
0.517 ▲17%

OSSc.

P.R.
R.C.
F.S.

0.666 ▼27%
0.403 ▼38% 0.742 ▼4%
0.502 ▼35%
-

0.516 ▼42% 0.897 ▼3%
0.694 ▼9%
0.783 ▼7%

0.428 ▼50%
0.100 ▼75%

0.721 ▼21% 0.935 ▲3%
0.622 ▼16% 0.712 ▼3%
0.668 ▼19% 0.810 ▲3%

0.936 ▲3%
0.784 ▲4%
0.854 ▲7%

SeSc.

P.R.
R.C.
F.S.

0.760 ▼15%
0.785 ▼12% 0.842 ▼6% 0.772 ▼13% 0.206 ▼70% 0.597 ▼31% 0.881 ▲4% 0.909 ▲6%
0.960 ▲19% 0.100 ▼67% 0.381 ▼39% 0.639 ▼13%
0.292 ▼48% 0.535 ▼24% 0.549 ▼41% 0.772 ▼19%
0.849 ▲1%
0.513 ▼32% 0.727 ▼11%
0.242 ▼59% 0.564 ▼27% 0.677 ▼17% 0.835 ▼1%

DDoS.

P.R.
R.C.
F.S.

0.248 ▼32%
0.997 —
0.397 ▼32%

Theft

P.R.
R.C.
F.S.

-

0.999 —
-

F.P.

C.E.

T.G.

0.731 ▲16% 0.454 ▼12%
0.800 ▼20% 0.997 —
0.764 ▲3% 0.624 ▼10%

-

-

O.A.

-

F.X.

Camero-M

Camero-T

0.217 ▼46% 0.574 ▼15% 0.565 ▼16%
0.987 ▼ 1% 0.999 —
0.999 —
0.999 —
0.149 ▼57% 0.356 ▼37% 0.729 ▼3% 0.722 ▼4%

0.919 ▲52% 0.195 ▼20% 0.230 ▼17%
0.041 ▼36% 0.371 ▼54% 0.399 ▼52%
0.242 ▼36% 0.862 ▲26% 0.341 ▼26%
0.161 ▼44% 0.183 ▼42% 0.514 ▼35% 0.601 ▼26%
0.861 ▲38% 0.248 ▼24%
0.067 ▼42% 0.431 ▼43% 0.480 ▼38%

- means that the value is lower than 0.10.
- Gen: Generic, Rec: Reconnaissance, Fuz: Fuzzers, Exp: Exploits, Shco: Shellcode, Anal: Analysis, Bac: Backdoor, Wor: Worms, OSSc: OSScan, SeSc:
ServiceScan.

when attempting to capture more malicious samples. Taken
together, both ROC and PRC analyzes verify that Camero
achieves a favorable trade-off between detection effectiveness
and reliability, which makes it more suitable for practical
deployment in real-world intrusion detection scenarios.
2) Evaluation of Fine Grained Performance: Finally, we
conducted a more fine-grained comparison between Camero
and the baseline methods by evaluating the precision, recall,
and F1 score in different attack categories. This analysis
highlights Camero’s improvements at a more granular level.
The results are summarized in Table VIII.
As shown in the fine-grained evaluation results in Table VIII, Camero consistently outperforms existing baseline
methods in the vast majority of attack types. Specifically, in
terms of precision, both Camero-M and Camero-T achieve

substantial improvements on major attack categories such as
DoS, Generic, Reconnaissance, Fuzzers, and Exploits, typically stabilizing above 0.85, while the baseline methods often
fall below 0.7, with some dropping below 0.3. This indicates
that Camero offers a clear advantage in reducing false positives. For Recall, Camero also demonstrates superior detection
capability. Even in more challenging attack types such as
Reconnaissance, Fuzzers, and Shellcode, Camero maintains a
level of 0.75 to 0.85, while baselines generally lag behind
in the range of 0.5 to 0.7. This suggests that Camero is
more robust in covering attack samples and mitigating false
negatives. When considering the F1 score, which integrates
both precision and recall, the superiority of Camero becomes
even more evident. For both common attacks (e.g. DoS and

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

Generic) and stealthier ones (e.g. Exploits, Analysis, and
Backdoor), Camero-T consistently achieves scores above 0.80,
significantly outperforming all baselines and demonstrating
strong consistency and stability. The only exception arises
in the theft category, where Camero’s performance is less
pronounced compared to other types of attack. However, this
does not indicate a limitation of the model itself; rather, it
stems from the extremely limited number of samples (only
slightly over one hundred), which introduces statistical variability into the evaluation. Therefore, results on Theft should
be interpreted with caution.
VI. D ISCUSSION
In this section, we discuss the usage of the decoder, applicability in encrypted traffic scenarios, model interpretability,
outline its current limitations, and highlight potential directions
for future work.

13

TABLE IX
C OMPARISON OF MODEL PERFORMANCE AND INFERENCE TIME WITH AND
WITHOUT THE DECODER

Datasets

Methods

ACC

F1

TPR

Time

D-I

M-With-Dec
M-Without-Dec
T-With-Dec
T-Without-Dec

0.9779
0.9798
0.9921
0.9928

0.9794
0.9812
0.9927
0.9933

0.9677
0.9687
0.9865
0.9874

2.6795
1.9025
5.7005
3.0043

D-II

M-With-Dec
M-Without-Dec
T-With-Dec
T-Without-Dec

0.9265
0.8631
0.8486
0.9036

0.9261
0.8535
0.8321
0.9007

0.8754
0.7588
0.7136
0.8317

2.4504
1.4974
4.7559
2.8422

D-III

M-With-Dec
M-Without-Dec
T-With-Dec
T-Without-Dec

0.7793
0.8046
0.9065
0.8699

0.7454
0.7798
0.9045
0.8635

0.6135
0.6568
0.8405
0.7817

2.4787
1.4129
5.3765
2.9462

- The inference time reported in the table is measured in milliseconds.
- The above inference time corresponds to the time cost per batch, where
the batch size is 256.

B. Applicability in Encrypted Traffic Scenarios

A. Usage of the Decoder
In Camero, the decoder acts as an auxiliary module that generates a self-supervised mask from the latent representations
produced by the encoder to characterize potential adversarial
perturbations in the input traffic. During training, this mask is
used to construct a mask-based cross-entropy loss, guiding
the model to focus on potentially perturbed features and
learn more robust representations. Once training is completed,
this perturbation-aware capability has already been absorbed
into the encoder parameters, making the decoder unnecessary
during inference. Removing the decoder does not change
the prediction pipeline and generally maintains comparable
detection performance, while significantly reducing computational overhead and improving real-time efficiency. In contrast,
involving the decoder during inference would make the prediction dependent on the generated mask, whose semantics
are not stable due to its indirect optimization through training
objectives, potentially introducing additional uncertainty.
For memory overhead, Camero-M contains approximately
3.5K parameters, which corresponds to about 14 KB of
FP32 weight storage. Camero-T consists of roughly N × 1K
parameters, where N denotes the number of attention layers,
resulting in less than 4N KB of memory overhead. Moreover,
we compared the differences in inference time and model
performance between the settings with and without the decoder
involved during inference. The results are presented in the
Table IX below.
As shown in Table IX, removing the decoder during inference consistently reduces the inference time across all
datasets. For example, on D-I, the inference time of CameroM decreases from 2.6795 ms to 1.9025 ms, while Camero-T
decreases from 5.7005 ms to 3.0043 ms. In terms of detection
performance, the results remain generally comparable, and in
some cases even slightly improve without the decoder. Although minor fluctuations can be observed on certain datasets,
the overall results indicate that excluding the decoder can
effectively improve inference efficiency while maintaining
competitive detection performance.

The widespread adoption of traffic encryption has made
traffic analysis more difficult. It has also motivated a growing
body of research to rely on flow-level statistical features,
such as those used in this work, which have been extensively
validated in prior studies [6], [7], [20], [43], [59]. In this
section, we select a fully encrypted drift scenario to evaluate
the applicability of Camero. The data are drawn from the
MAWI dataset [78], [79], which contains network traces
collected from a real backbone network. We first filter out
encrypted traffic and then train the model using the data set
collected on March 1, 2021. The evaluation is conducted on
data collected three weeks later, namely March 22, 2021. The
results are presented in Table X.
TABLE X
P ERFORMANCE E VALUATION IN E NCRYPTED T RAFFIC S CENARIOS
Date

Methods

ACC

F1

FPR

TPR

2021/3/1

Unmasked
Masked

0.9812
0.9809

0.9695
0.9691

0.0001
0.0011

0.9409
0.9425

2021/3/22

Unmasked
Masked

0.6350
0.8506

0.0002
0.7472

0.0005
0.0085

0.0001
0.6052

The results show that on the training data, Camero achieves
performance comparable to methods optimized with the conventional cross-entropy objective. However, in terms of generalization to the data collected three weeks later, Camero
demonstrates a clear improvement. Specifically, the accuracy
increases from 0.63 to 0.85, the F1 score improves to 0.74, and
the true positive rate reaches approximately 0.60, indicating
that Camero remains effective even in encrypted traffic scenarios. Further analysis reveals that although the payload content
of the packet cannot be accessed directly after encryption,
the statistical features of the flow-level can still reflect the
structural patterns of communication behavior. In particular,
flow statistical features are primarily derived from connectionlevel metadata, including flow duration, packet counts, packet
size distributions, inter-arrival times, and bidirectional traffic

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

ratios. These features describe communication patterns rather
than the specific data content, and therefore are not directly
affected by encryption mechanisms.
C. Model Interpretability
The mask generated by Camero provides a degree of interpretability regarding the importance of input features for the
final prediction. Specifically, it reveals which input features
play a more significant role in the model’s decision to classify
a sample as an attack, as well as their potential semantic
relevance. To illustrate this, we randomly select one attack
sample as an example and rank the corresponding features
according to the magnitude of their mask weights and their
positions, as shown in Fig. 8.

14

between normal and anomalous communication patterns. For
instance, attack traffic often exhibits more bursty or irregular
inter-arrival time distributions. Consequently, these features
can still contribute useful discriminative signals, although their
importance is relatively lower than that of the aforementioned
connection-related statistical features.
D. Limitations and Future Work
Our proposed approach effectively enhances robustness in
detecting mixed traffic and adversarial perturbations, yet several limitations remain to be explored. For example, our current evaluation assumes a black-box attacker with no access to
model parameters or training data, stronger adversaries, such
as adaptive, query-based, or partially informed attackers, could
potentially craft malicious flows that evade detection. Such
adversarial perturbations may exploit the latent representations
or mask mechanism, challenging the robustness of the model.
Evaluating and enhancing the model’s resilience against these
stronger attack scenarios constitutes an important direction
for future research. Possible approaches include adversarial
training targeting the mask generation process, dynamic or
stochastic mask updates, and extending the method to handle
categorical or sequence-level features, which may be exploited
by sophisticated attackers.
VII. C ONCLUSION

Fig. 8. Interpretability Analysis of Input Feature Importance.

As illustrated in Fig. 8, different traffic features exhibit
noticeably different importance distributions under the masking mechanism, with several features receiving significantly
higher weights than others. For example, features such as
syn num, num s port, num d ip, fin num, and con per sec
obtain the highest mask weights (approximately 0.71–0.73),
indicating that the model tends to focus more on the network
connection behavior patterns reflected by these features during
the learning process. From the perspective of network security
semantics, these features are mainly associated with connection establishment behavior and connection frequency. For
instance, the number of SYN packets and FIN packets reflects
interaction characteristics during the connection establishment
and termination phases, while the number of source ports
and destination IP addresses can capture patterns of scanning
behavior or large-scale connection attempts. Such patterns
are typical indicators of attack activities, such as scanning
attacks or denial-of-service attacks. Therefore, the higher mask
weights assigned to these features suggest that the masking
mechanism enables the model to automatically capture key
statistical features that are highly correlated with anomalous
behaviors.
In contrast, statistical features related to traffic interarrival time and traffic volume, such as iat std, iat mean,
and num d port, exhibit moderate weights (approximately
0.61–0.65). These features typically reflect the temporal characteristics of network traffic and the scale of data transmission, which provide auxiliary information for distinguishing

We present a network traffic detection system with strong
generalization and robustness, namely Camero, designed to
address the challenge of generalizing from closed-set training
data to open-world traffic. We first model malicious behavior
from the attacker’s point of view as a min-max adversarial
optimization problem, exposing the limitations of conventional
black-or-white traffic labeling and its adverse impact on the
robustness. Building on this formulation, we proposed a selfgenerating mask strategy with sparsity constraints, replacing
binary labeling with a combination of self-generating masks
and adaptive labels. This approach is model-agnostic and
compatible with various architectures. Finally, we conducted
extensive ablation and comparative experiments in a real-world
network environment and in three public datasets CICIDS2017, UNSW-NB15 and Bot-IoT, evaluating both overall and
fine-grained performance using eight metrics. The results show
that Camero consistently outperforms all baselines in key
measures such as accuracy, F1 score, TPR, and FPR.
ACKNOWLEDGMENTS
This work was supported by the National Key R&D Program of China under Grant No. 2024YFE0203800.
R EFERENCES
[1] K. He, D. D. Kim, and M. R. Asghar, “Adversarial machine learning
for network intrusion detection systems: A comprehensive survey,” IEEE
Communications Surveys & Tutorials, vol. 25, no. 1, pp. 538–566, 2023.
[2] T. Bilot, B. Jiang, Z. Li, N. El Madhoun, K. Al Agha, A. Zouaoui, and
T. Pasquier, “Sometimes simpler is better: A comprehensive analysis
of {State-of-the-Art}{Provenance-Based} intrusion detection systems,”
in 34th USENIX Security Symposium (USENIX Security 25), 2025, pp.
7193–7212.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

[3] H. Kheddar, D. W. Dawoud, A. I. Awad, Y. Himeur, and M. K. Khan,
“Reinforcement-learning-based intrusion detection in communication
networks: A review,” IEEE Communications Surveys & Tutorials, 2024.
[4] A. Awadallah, K. Eledlebi, M. J. Zemerly, D. Puthal, E. Damiani,
K. Taha, T.-Y. Kim, P. D. Yoo, K.-K. R. Choo, M.-S. Yim et al.,
“Artificial intelligence-based cybersecurity for the metaverse: Research
challenges and opportunities,” IEEE Communications Surveys & Tutorials, vol. 27, no. 2, pp. 1008–1052, 2024.
[5] F. Wei, H. Li, Z. Zhao, and H. Hu, “{xNIDS}: Explaining deep
learning-based network intrusion detection systems for active intrusion
responses,” in 32nd USENIX Security Symposium (USENIX Security 23),
2023, pp. 4337–4354.
[6] C. Zha, T. Liu, C. Lin, B. Bai, and R. Zhang, “Sparse gaussian markov
modeling for robust and trustworthy unknown cyber defense,” IEEE
Transactions on Cognitive Communications and Networking, 2026.
[7] J. Yang, X. Chen, S. Chen, X. Jiang, and X. Tan, “Conditional variational
auto-encoder and extreme value theory aided two-stage learning approach for intelligent fine-grained known/unknown intrusion detection,”
IEEE Transactions on Information Forensics and Security, vol. 16, pp.
3538–3553, 2021.
[8] D. Han, Z. Wang, W. Chen, K. Wang, R. Yu, S. Wang, H. Zhang,
Z. Wang, M. Jin, J. Yang et al., “Anomaly detection in the open world:
Normality shift detection, explanation, and adaptation.” in NDSS, 2023.
[9] K. Borders, J. Springer, and M. Burnside, “Chimera: A declarative language for streaming network traffic analysis,” in 21st USENIX security
symposium (USENIX Security 12), 2012, pp. 365–379.
[10] H. Li, H. Hu, G. Gu, G.-J. Ahn, and F. Zhang, “vnids: Towards elastic
security with safe and efficient virtualization of network intrusion detection systems,” in Proceedings of the 2018 ACM SIGSAC Conference
on Computer and Communications Security, 2018, pp. 17–34.
[11] C. Zha, Z. Wang, Y. Fan, B. Bai, Y. Zhang, S. Shi, and R. Zhang, “Anids: adaptive network intrusion detection system based on clustering
and stacked ctgan,” IEEE Transactions on Information Forensics and
Security, 2025.
[12] J. Zhang, X. Chen, Y. Xiang, W. Zhou, and J. Wu, “Robust network
traffic classification,” IEEE/ACM transactions on networking, vol. 23,
no. 4, pp. 1257–1270, 2014.
[13] S.-J. Xu, G.-G. Geng, X.-B. Jin, D.-J. Liu, and J. Weng, “Seeing traffic
paths: Encrypted traffic classification with path signature features,” IEEE
Transactions on Information Forensics and Security, vol. 17, pp. 2166–
2181, 2022.
[14] X. Xiao, S. Wang, G. Hu, Q. Li, K. Mao, X. Luo, B. Zhang, and
S. Xia, “Rbljan: Robust byte-label joint attention network for network
traffic classification,” IEEE Transactions on Dependable and Secure
Computing, 2024.
[15] C. Zha, Z. Wang, Y. Fan, X. Zhang, B. Bai, Y. Zhang, S. Shi, and
R. Zhang, “Skt-ids: Unknown attack detection method based on sigmoid
kernel transformation and encoder–decoder architecture,” Computers &
Security, vol. 146, p. 104056, 2024.
[16] C. Zha, Z. Wang, Y. Fan, B. Bai, Y. Zhang, S. Shi, and R. Zhang, “Dmids-a network intrusion detection method based on dual-modal fusion,”
IEEE Transactions on Network and Service Management, 2025.
[17] K. A. Akbar, Y. Wang, G. Ayoade, Y. Gao, A. Singhal, L. Khan,
B. Thuraisingham, and K. Jee, “Advanced persistent threat detection
using data provenance and metric learning,” IEEE Transactions on
Dependable and Secure Computing, vol. 20, no. 5, pp. 3957–3969, 2022.
[18] Z. Chen, J. Liu, Y. Shen, M. Simsek, B. Kantarci, H. T. Mouftah,
and P. Djukic, “Machine learning-enabled iot security: Open issues and
challenges under advanced persistent threats,” ACM Computing Surveys,
vol. 55, no. 5, pp. 1–37, 2022.
[19] R. Sommer and V. Paxson, “Outside the closed world: On using machine
learning for network intrusion detection,” in 2010 IEEE symposium on
security and privacy. IEEE, 2010, pp. 305–316.
[20] L. Yang, A. Moubayed, and A. Shami, “Mth-ids: A multitiered hybrid
intrusion detection system for internet of vehicles,” IEEE Internet of
Things Journal, vol. 9, no. 1, pp. 616–632, 2021.
[21] C. Fu, Q. Li, and K. Xu, “Flow interaction graph analysis: Unknown
encrypted malicious traffic detection,” IEEE/ACM Transactions on Networking, vol. 32, no. 4, pp. 2972–2987, 2024.
[22] D. Arp, E. Quiring, F. Pendlebury, A. Warnecke, F. Pierazzi, C. Wressnegger, L. Cavallaro, and K. Rieck, “Dos and don’ts of machine learning
in computer security,” in 31st USENIX Security Symposium (USENIX
Security 22), 2022, pp. 3971–3988.
[23] L. Du, Y. Chai, Y. Jia, B. Fang, H. Li, and Z. Gu, “Toward open-world
network intrusion detection via open recognition and inspection,” IEEE
Transactions on Information Forensics and Security, 2025.

15

[24] X. Yang, F. Tong, F. Jiang, and G. Cheng, “A lightweight and dynamic
open-set intrusion detection for industrial internet of things,” IEEE
Transactions on Information Forensics and Security, 2025.
[25] G. F. Cretu, A. Stavrou, M. E. Locasto, S. J. Stolfo, and A. D. Keromytis,
“Casting out demons: Sanitizing training data for anomaly sensors,” in
2008 IEEE Symposium on Security and Privacy (sp 2008). IEEE, 2008,
pp. 81–95.
[26] G. F. Cretu-Ciocarlie, A. Stavrou, M. E. Locasto, and S. J. Stolfo,
“Adaptive anomaly detection via self-calibration and dynamic updating,”
in International workshop on recent advances in intrusion detection.
Springer, 2009, pp. 41–60.
[27] F. Pendlebury, F. Pierazzi, R. Jordaney, J. Kinder, and L. Cavallaro,
“{TESSERACT}: Eliminating experimental bias in malware classification across space and time,” in 28th USENIX security symposium
(USENIX Security 19), 2019, pp. 729–746.
[28] S. T. Jan, Q. Hao, T. Hu, J. Pu, S. Oswal, G. Wang, and B. Viswanath,
“Throwing darts in the dark? detecting bots with limited data using
neural data augmentation,” in 2020 IEEE symposium on security and
privacy (SP). IEEE, 2020, pp. 1190–1206.
[29] X. Wang, “Enidrift: A fast and adaptive ensemble system for network
intrusion detection under real-world drift,” in Proceedings of the 38th
Annual Computer Security Applications Conference, 2022, pp. 785–798.
[30] G. Andresini, F. Pendlebury, F. Pierazzi, C. Loglisci, A. Appice, and
L. Cavallaro, “Insomnia: Towards concept-drift robustness in network
intrusion detection,” in Proceedings of the 14th ACM workshop on
artificial intelligence and security, 2021, pp. 111–122.
[31] S. Yang, X. Zheng, J. Li, J. Xu, X. Wang, and E. C. Ngai, “Recda:
Concept drift adaptation with representation enhancement for network
intrusion detection,” in Proceedings of the 30th ACM SIGKDD Conference on Knowledge Discovery and Data Mining, 2024, pp. 3818–3828.
[32] R. Jordaney, K. Sharad, S. K. Dash, Z. Wang, D. Papini, I. Nouretdinov,
and L. Cavallaro, “Transcend: Detecting concept drift in malware
classification models,” in 26th USENIX security symposium (USENIX
security 17), 2017, pp. 625–642.
[33] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez,
Ł. Kaiser, and I. Polosukhin, “Attention is all you need,” Advances in
neural information processing systems, vol. 30, 2017.
[34] I. Sharafaldin, A. H. Lashkari, A. A. Ghorbani et al., “Toward generating
a new intrusion detection dataset and intrusion traffic characterization.”
ICISSp, vol. 1, no. 2018, pp. 108–116, 2018.
[35] N. Moustafa and J. Slay, “Unsw-nb15: a comprehensive data set for
network intrusion detection systems (unsw-nb15 network data set),”
in 2015 military communications and information systems conference
(MilCIS). IEEE, 2015, pp. 1–6.
[36] N. Koroniotis, N. Moustafa, E. Sitnikova, and B. Turnbull, “Towards
the development of realistic botnet dataset in the internet of things
for network forensic analytics: Bot-iot dataset,” Future Generation
Computer Systems, vol. 100, pp. 779–796, 2019.
[37] S. Gupta, D. Gosain, M. Kwon, and H. B. Acharya, “Deep4r: Deep
packet inspection in p4 using packet recirculation,” in IEEE INFOCOM
2023-IEEE Conference on Computer Communications. IEEE, 2023,
pp. 1–10.
[38] L. Deri and F. Fusco, “Using deep packet inspection in cybertraffic
analysis,” in 2021 IEEE International Conference on Cyber Security
and Resilience (CSR). IEEE, 2021, pp. 89–94.
[39] P. Wu, J. Ning, X. Huang, R. Chen, K. Zhang, and K. Liang, “Privbox:
Privacy-preserving deep packet inspection with dual double-masking
obfuscated rule generation,” IEEE Transactions on Dependable and
Secure Computing, 2025.
[40] V. F. Taylor, R. Spolaor, M. Conti, and I. Martinovic, “Appscanner:
Automatic fingerprinting of smartphone apps from encrypted network
traffic,” in 2016 IEEE European Symposium on Security and Privacy
(EuroS&P). IEEE, 2016, pp. 439–454.
[41] T. Van Ede, R. Bortolameotti, A. Continella, J. Ren, D. J. Dubois,
M. Lindorfer, D. Choffnes, M. Van Steen, and A. Peter, “Flowprint:
Semi-supervised mobile-app fingerprinting on encrypted network traffic,” in Network and distributed system security symposium (NDSS),
vol. 27, 2020.
[42] L. Invernizzi, S. Miskovic, R. Torres, C. Kruegel, S. Saha, G. Vigna,
S.-J. Lee, and M. Mellia, “Nazca: Detecting malware distribution in
large-scale networks.” in NDSS, vol. 14, 2014, pp. 23–26.
[43] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “Kitsune: an
ensemble of autoencoders for online network intrusion detection,” arXiv
preprint arXiv:1802.09089, 2018.
[44] C. Fu, Q. Li, M. Shen, and K. Xu, “Realtime robust malicious traffic
detection via frequency domain analysis,” in Proceedings of the 2021

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

ACM SIGSAC Conference on Computer and Communications Security,
2021, pp. 3431–3446.
[45] R. Tang, Z. Yang, Z. Li, W. Meng, H. Wang, Q. Li, Y. Sun, D. Pei,
T. Wei, Y. Xu et al., “Zerowall: Detecting zero-day web attacks through
encoder-decoder recurrent neural networks,” in IEEE INFOCOM 2020IEEE Conference on Computer Communications.
IEEE, 2020, pp.
2479–2488.
[46] Y. Yue, X. Chen, Z. Han, X. Zeng, and Y. Zhu, “Contrastive learning
enhanced intrusion detection,” IEEE Transactions on Network and
Service Management, vol. 19, no. 4, pp. 4232–4247, 2022.
[47] C. Wu, J. Sun, J. Chen, M. Alazab, Y. Liu, and Y. Xiang, “Tcgids: Robust network intrusion detection via temporal contrastive graph
learning,” IEEE Transactions on Information Forensics and Security,
2025.
[48] M. Huang, Y. Lin, N. Li, X. Chen, and E. Bertino, “Card: Robustnesspreserving transfer learning for network intrusion detection via contrastive adversarial representation distillation,” IEEE Transactions on
Dependable and Secure Computing, 2025.
[49] N. Wang, S. Shi, Y. Chen, W. Lou, and Y. T. Hou, “Feco: Boosting
intrusion detection capability in iot networks via contrastive learning,”
IEEE Transactions on Dependable and Secure Computing, 2025.
[50] Y. Ma, Z. Li, H. Xue, and J. Chang, “A balanced supervised contrastive
learning-based method for encrypted network traffic classification,”
Computers & Security, vol. 145, p. 104023, 2024.
[51] M. Shen, J. Zhang, L. Zhu, K. Xu, and X. Du, “Accurate decentralized
application identification via encrypted traffic analysis using graph
neural networks,” IEEE Transactions on Information Forensics and
Security, vol. 16, pp. 2367–2380, 2021.
[52] A. Agiollo, E. Bardhi, M. Conti, R. Lazzeretti, E. Losiouk, and
A. Omicini, “Gnn4ifa: Interest flooding attack detection with graph
neural networks,” in 2023 IEEE 8th European Symposium on Security
and Privacy (EuroS&P). IEEE, 2023, pp. 615–630.
[53] T. Li, X. Liu, W. Qiao, X. Zhu, Y. Shen, and J. Ma, “T-trace: Constructing the apts provenance graphs through multiple syslogs correlation,”
IEEE Transactions on Dependable and Secure Computing, vol. 21, no. 3,
pp. 1179–1195, 2023.
[54] H. Zhang, L. Yu, X. Xiao, Q. Li, F. Mercaldo, X. Luo, and Q. Liu,
“Tfe-gnn: A temporal fusion encoder using graph neural networks for
fine-grained encrypted traffic classification,” in Proceedings of the ACM
web conference 2023, 2023, pp. 2066–2075.
[55] M. U. Rehman, H. Ahmadi, and W. U. Hassan, “Flash: A comprehensive
approach to intrusion detection via provenance graph representation
learning,” in 2024 IEEE Symposium on Security and Privacy (SP).
IEEE, 2024, pp. 3552–3570.
[56] J. Ghadermazi, S. Hore, A. Shah, and N. D. Bastian, “Gtae-ids:
Graph transformer-based autoencoder framework for real-time network
intrusion detection,” IEEE Transactions on Information Forensics and
Security, 2025.
[57] X. Zhang, R. Zhao, Z. Jiang, H. Chen, Y. Ding, E. C. Ngai, and S.-H.
Yang, “Continual learning with strategic selection and forgetting for network intrusion detection,” in IEEE INFOCOM 2025-IEEE Conference
on Computer Communications. IEEE, 2025, pp. 1–10.
[58] C. Fu, Q. Li, K. Xu, and J. Wu, “Point cloud analysis for ml-based
malicious traffic detection: Reducing majorities of false positive alarms,”
in Proceedings of the 2023 ACM SIGSAC Conference on Computer and
Communications Security, 2023, pp. 1005–1019.
[59] C. Zha, H. Pan, B. Bai, J. Wu, and R. Zhang, “Flowxpert: Contextaware flow embedding for enhanced traffic detection in iot network,”
IEEE Transactions on Mobile Computing, 2026.
[60] F. Pedregosa, G. Varoquaux, A. Gramfort, V. Michel, B. Thirion,
O. Grisel, M. Blondel, P. Prettenhofer, R. Weiss, V. Dubourg et al.,
“Scikit-learn: Machine learning in python,” the Journal of machine
Learning research, vol. 12, pp. 2825–2830, 2011.
[61] A. Paszke, S. Gross, F. Massa, A. Lerer, J. Bradbury, G. Chanan,
T. Killeen, Z. Lin, N. Gimelshein, L. Antiga et al., “Pytorch: An
imperative style, high-performance deep learning library,” Advances in
neural information processing systems, vol. 32, 2019.
[62] D. E. Rumelhart, G. E. Hinton, and R. J. Williams, “Learning representations by back-propagating errors,” nature, vol. 323, no. 6088, pp.
533–536, 1986.
[63] Y. LeCun, Y. Bengio, and G. Hinton, “Deep learning,” nature, vol. 521,
no. 7553, pp. 436–444, 2015.
[64] J. Xu, Z. Li, B. Du, M. Zhang, and J. Liu, “Reluplex made more
practical: Leaky relu,” in 2020 IEEE Symposium on Computers and
communications (ISCC). IEEE, 2020, pp. 1–7.

16

[65] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for image
recognition,” in Proceedings of the IEEE conference on computer vision
and pattern recognition, 2016, pp. 770–778.
[66] J. L. Ba, J. R. Kiros, and G. E. Hinton, “Layer normalization,” arXiv
preprint arXiv:1607.06450, 2016.
[67] N. Japkowicz and M. Shah, Evaluating learning algorithms: a classification perspective. Cambridge University Press, 2011.
[68] Z. Huang, E. Ayday, J. Fellay, J.-P. Hubaux, and A. Juels, “Genoguard:
Protecting genomic data against brute-force attacks,” in 2015 IEEE
Symposium on Security and Privacy. IEEE, 2015, pp. 447–462.
[69] C. L. Schuba, I. V. Krsul, M. G. Kuhn, E. H. Spafford, A. Sundaram,
and D. Zamboni, “Analysis of a denial of service attack on tcp,” in
Proceedings. 1997 IEEE Symposium on Security and Privacy (Cat. No.
97CB36097). IEEE, 1997, pp. 208–223.
[70] G. Carl, G. Kesidis, R. R. Brooks, and S. Rai, “Denial-of-service attackdetection techniques,” IEEE Internet computing, vol. 10, no. 1, pp. 82–
89, 2006.
[71] K. Pelechrinis, M. Iliofotou, and S. V. Krishnamurthy, “Denial of
service attacks in wireless networks: The case of jammers,” IEEE
Communications surveys & tutorials, vol. 13, no. 2, pp. 245–257, 2010.
[72] S. Roy, N. Sharmin, J. C. Acosta, C. Kiekintveld, and A. Laszka,
“Survey and taxonomy of adversarial reconnaissance techniques,” ACM
Computing Surveys, vol. 55, no. 6, pp. 1–38, 2022.
[73] S. Salamatian, W. Huleihel, A. Beirami, A. Cohen, and M. Médard,
“Why botnets work: Distributed brute-force attacks need no synchronization,” IEEE Transactions on Information Forensics and Security,
vol. 14, no. 9, pp. 2288–2299, 2019.
[74] D. Mitropoulos, P. Louridas, M. Polychronakis, and A. D. Keromytis,
“Defending against web application attacks: Approaches, challenges and
implications,” IEEE Transactions on Dependable and Secure Computing,
vol. 16, no. 2, pp. 188–203, 2017.
[75] J. Kaur, U. Garg, and G. Bathla, “Detection of cross-site scripting
(xss) attacks using machine learning techniques: a review,” Artificial
Intelligence Review, vol. 56, no. 11, pp. 12 725–12 769, 2023.
[76] D. R. dos Santos, “Access control vulnerabilities in network protocol
implementations: How attackers exploit them and what to do about it,”
in Proceedings of the 28th ACM Symposium on Access Control Models
and Technologies, 2023, pp. 5–6.
[77] G. Engelen, V. Rimmer, and W. Joosen, “Troubleshooting an intrusion
detection dataset: the cicids2017 case study,” in 2021 IEEE Security and
Privacy Workshops (SPW). IEEE, 2021, pp. 7–12.
[78] MAWI Working Group, “MAWI Working Group Traffic Archive,” https:
//mawi.wide.ad.jp/mawi/, 2000, accessed: 2025-05-22.
[79] R. Fontugne, P. Borgnat, P. Abry, and K. Fukuda, “Mawilab: Combining diverse anomaly detectors for automated anomaly labeling and
performance benchmarking,” in Proceedings of the 6th International
COnference, 2010, pp. 1–12.

Chao Zha is currently pursuing a Ph.D. in Computer Science and Technology through a combined
M.S. - Ph.D. program since 2021 at the Institute
of Computing Technology, Chinese Academy of
Sciences, Beijing, China. His research focuses on
network security, with particular interests in network
intrusion detection systems (NIDS), encrypted traffic
detection, malware analysis, and intelligent defense
systems. He has published some papers in peerreviewed journals, including IEEE Transactions on
Information Forensics and Security (TIFS), IEEE
Transactions on Mobile Computing (TMC), Computers & Security, and IEEE
Transactions on Network and Service Management (TNSM), among others.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3688655

IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING, VOL. 14, NO. 8, AUGUST 2021

Dakun Shen is a Scientific Researcher at Zhejiang
University, where he has worked since 2024. Prior to
this role, he was a Principal Investigator at Zhejiang
Lab from 2022 to 2024, and an Assistant Professor
in the Department of Computer Science at Central
Michigan University from 2019 to 2022. He received
his Ph.D. degree in Computer Science from the
University of South Florida in 2019.

Ruyun Zhang received his Ph.D. degree in Communications and Information Systems in 2011. Having
been a researcher and Ph.D. supervisor for years,
he is currently working as principal investigator of
the Research Center for High-Efficiency Computing
Infrastructure at Zhejiang Lab. His research interests include communication networks and security.
He has published several papers in international
conferences and peer-reviewed journals, including
IEEE Transactions on Information Forensics and
Security (TIFS), IEEE Transactions on Dependable
and Secure Computing (TDSC), IEEE Transactions on Mobile Computing
(TMC), Computers & Security, and IEEE Transactions on Network and
Service Management (TNSM), among others.

Kui Ren is a Professor and Associate Dean of
College of Computer Science and Technology at
Zhejiang University, where he also directs the Institute of Cyber Science and Technology. Before that,
he was SUNY Empire Innovation Professor at State
University of New York at Buffalo. He received his
Ph.D. degree from Worcester Polytechnic Institute.
His current research interests include Data Security,
IoT Security, AI Security, and Privacy. Kui is a
Fellow of ACM and IEEE. He currently serves as
an area/associate editor for ACM Transactions On
Cyber Physical Systems, IEEE Transactions on Dependable and Secure
Computing, IEEE Transactions on Service Computing, IEEE Transactions
on Networking, IEEE Transactions on Mobile Computing, IEEE Wireless
Communications, IEEE Internet of Things Journal, and Computer Networks.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

17
PAPER_TEXT
