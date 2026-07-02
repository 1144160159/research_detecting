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
# [815] SYNAPS: A Neuro-Symbolic Framework for Proactive Security in Consumer Electronics
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
编号：815
题名：SYNAPS: A Neuro-Symbolic Framework for Proactive Security in Consumer Electronics
年份：2025
DOI：10.1109/tce.2025.3642082
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2025.3642082.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：无
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\815.txt
- 原始字符数：41047
- 本次发送字符数：41047
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2300

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

SYNAPS: A Neuro-Symbolic Framework for
Proactive Security in Consumer Electronics
Debashis Das , Member, IEEE

Abstract— Proactive security risk assessment and prediction
(SRAP) is essential to defend against dynamic and evolving
threats in the modern interconnected consumer electronics
domain. With the rapid emergence of polymorphic attacks and
complex network behaviors, traditional systems are often insufficient due to their static nature and limited adaptability. Neural
systems alone fail to incorporate the domain expertise necessary
for identifying well-known risk indicators in high-stakes cybersecurity contexts. To address these gaps, we propose SYNAPS:
a neuro-symbolic framework for a proactive security model that
fuses data-driven anomaly detection with transparent symbolic
reasoning to boost risk scoring and prediction accuracy for
consumer device security. Our design first trains an LSTM
autoencoder on benign device telemetry to compute continuous
neural anomaly scores, and a curated set of device-specific
symbolic rules generates interpretable risk scores based on
established security indicators. These scores are then blended
into a hybrid risk estimate, which feeds into a shallow MLP for
multiclass threat classification (NS-MLP). To further strengthen
SYNAPS against device-targeted evasions, we introduce three
variants: Gaussian-noise augmentation to mimic polymorphic
attacks (NS-Aug), adversarial training via a lightweight Generative Adversarial Network (GAN) to model firmware-level exploits
(NS-Adv), and transfer learning to adapt our autoencoder to new
device models and firmware versions (NS-Trans). Our experiment results indicate that SYNAPS and its enhanced versions
substantially outperform neural-only baselines. NS-Adv achieves
93.3% test accuracy with a 12.3% relative improvement over
the neural-only model. Overall, the integration of data-driven
learning and symbolic reasoning significantly boosts the accuracy
and reliability of threat detection in consumer electronics.
Index Terms— Consumer electronics security, neural-symbolic
reasoning, symbolic risk optimization, multiclass threat classification, transfer learning, zero-day resilience.

I. I NTRODUCTION
YBER threats in consumer electronic devices are becoming increasingly advanced, adaptive, and stealthy [1].
Attackers now use AI tools to probe firmware vulnerabilities, automate exploitation of smart-home hubs and employ
zero-day exploits or compromised insider credentials to persist
undetected on devices [2]. Meanwhile, the proliferation of
smart wearable health monitors, voice-activated assistants, and
connected appliances has expanded the consumer electronics
attack surface [3]. Each new device and its accompanying
cloud or mobile companion app provides fresh entry points

C

Received 27 August 2025; revised 22 October 2025; accepted 6 December
2025. Date of publication 9 December 2025; date of current version 25 March
2026.
The author is with the Department of CS and DS, Meharry Medical College,
Nashville, TN 37208 USA (e-mail: debashis.das@ieee.org).
Digital Object Identifier 10.1109/TCE.2025.3642082

for adversaries. On the other hand, defenders must grapple
with monitoring and securing a heterogeneous ecosystem of
resource-constrained endpoints [4]. This rapid evolution underscores the need to move beyond reactive and signature-based
defenses toward proactive risk assessment and intelligent threat
prediction in consumer electronic environments.
Traditional security mechanisms for consumer electronic
devices typically operate reactively [5]. While these defenses
can block well-understood malware or repeat attacks, they
struggle against novel device-specific threats, such as zero-day
firmware vulnerabilities or obfuscated payloads that do not
match predefined signatures [6]. To overcome these limitations in the consumer electronics domain, machine learning
(ML) techniques have gained traction for automated threat
detection and anomaly classification [7]. Meanwhile, deep
neural networks can learn from large volumes of device
telemetry ranging from sensor readings and API call sequences
to network traffic and user interaction patterns to identify
subtle deviations indicative of emerging threats [8]. But, recent
studies have further found that consumer devices are uniquely
vulnerable due to their resource-constrained hardware and
diverse vendor-specific firmware [9]. High-profile incidents,
such as large-scale IoT botnet attacks and exploitation of insecure smart-home hubs, highlight the urgent need for proactive
defenses [10].
To fill this gap, we introduce SYNAPS, a symbolic-neural
framework [11] for proactive risk scoring and threat prediction on consumer electronics devices. SYNAPS fuses a
single-step LSTM autoencoder trained on benign telemetry
(API calls, sensor readings, network flows), which generates
continuous neural anomaly scores, with an expert-driven rule
engine that produces symbolic risk signals. These streams
are combined into a hybrid risk estimate and, together with
select raw telemetry features, fed into a shallow MLP classifier
(NS-MLP) for multiclass threat detection [12]. The standout
advantage of SYNAPS is that it delivers high-accuracy, realtime threat detection on resource-constrained devices. Overall,
the contributions of this paper are as follows:
• We design a trustworthy neuro-symbolic framework
that combines temporal deep learning with interpretable
rule-based reasoning for on-device threat detection and
risk scoring.
• We develop a hybrid scoring mechanism that combines
the reconstruction error from unsupervised LSTM autoencoders with symbolic scores derived from expert-crafted
rules to ensure cross-device consistency.

1558-4127 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

DAS: SYNAPS: A NS FRAMEWORK FOR PROACTIVE SECURITY IN CONSUMER ELECTRONICS

We improve model robustness through three targeted
techniques: (i) NS-Aug: Gaussian noise injection to
enhance generalization; (ii) NS-Adv: GAN-based generation of adversarial telemetry traces for resilient learning;
and (iii) NS-Trans: transfer learning to adapt to firmware
environments.
• We present an extensive empirical evaluation of SYNAPS
and its variants on a multi-device telemetry dataset.
• We analyze the latency and memory usage of all
variants on Mac-based hardware for real-time resourceconstrained environments.
The rest of this paper is organized as follows. In Section II,
we review prior work on anomaly detection, symbolic reasoning, and neuro-symbolic security systems. Section III
introduces our SYNAPS architecture in detail. In Section IV,
we describe our experimental setup, datasets, and evaluation
metrics, then present and analyze performance results across
all SYNAPS variants. Finally, Section V concludes with a
summary of findings and outlines future enhancements.
•

II. R ELATED W ORKS
Recent advances in cybersecurity have sparked growing
interest in neuro-symbolic AI, as detailed in Table I, which
seeks to integrate neural networks with the reasoning and
interpretability of symbolic systems [13]. This approach is
increasingly recognized as a promising solution to address the
limitations of purely neural or symbolic models in complex
threat areas.
To improve network intrusion detection systems (NIDS),
Almadhor et al. [13] introduced a framework that fuses deep
learning with symbolic reasoning. Their system achieved
better detection accuracy and maintained human-interpretable
outcomes. Kalutharage et al. [14] explored the use of reinforcement learning in combination with symbolic reasoning
for cyber defense. Their system was designed to generate timely and explainable responses to evolving threats
using symbolic knowledge to guide the learning process. In the domain of explainable AI for privacy and
threat modeling, Piplai et al. [15] proposed a neuro-symbolic
framework that integrates knowledge graphs with neural
learning. Their work addresses the crucial challenge of
explainability in cybersecurity using structured domain knowledge. Similarly, Himmelhuber et al. [16] demonstrated how
sub-symbolic models could be enhanced through symbolic
overlays. Their approach focuses on the explanation of cyberattacks for a more intuitive and traceable detection process.
In the context of cloud-based intrusion detection, a recent
study [22] applied neuro-symbolic methods to enable real-time
threat detection and monitoring. The model proved effective
in cloud-native environments. Bertrand Van Ouytsel et al. [17]
introduced an approach combining symbolic system call
analysis with federated learning. It enables collaborative
malware identification without sharing raw data. However,
Jagatheesaperumal et al. [18] proposed a neuro-symbolic perception framework to enhance situational awareness and
resilience. Deep perceptual models with formal symbolic
constraints ensure safe and reliable operation in adversarial
environments. In efforts to support real-time cyber threat

2301

Algorithm 1 Neural Anomaly Detection
Input : Time-series dataset X ∈ RTmax ×d , window
length T , false-alarm rate αFA
Output: Reconstruction-error threshold τ , anomaly
scores Sanom [t] ∀t
Initialize LSTM-AE parameters θ;
for epoch ← 1 to Nepochs do
3
Sample minibatch of windows {xt−T +1:t } from
nominal X ;
4
Compute reconstruction x̂t−T +1:t = f θ (xt−T +1:t );
5
Update θ to minimize ∥x − x̂∥2 ;

1
2

Initialize list Etrain ← [];
for t ← T, . . . , Tmax do
8
x̂t ← f θ (xt−T +1:t );
9
et ← ∥xt − x̂t ∥22 ;
10
append et to Etrain ;
6
7

τ ← the (1 − αFA ) quantile of Etrain ;
for t ← T, . . . , Tmax do
13
x̂t ← f θ (xt−T +1:t );
14
Sanom [t] ← ∥xt − x̂t ∥22 ;
11

12

15

return τ, Sanom

detection, another study [14] presented a system that merges
deep anomaly detection with rule-based symbolic reasoning.
This work balances data-driven adaptability with transparent
rule logic. For proactive threat modeling, Lei et al. [19] developed the ADAPT framework, which integrates game-theoretic
reasoning with neuro-symbolic agents.
Finally, a recent study in [23] explored the role of
neuro-symbolic AI in incident response and analyst decision
support. Through initial case studies, the authors demonstrated how symbolic knowledge can be embedded into neural
pipelines to bridge the gap between theoretical AI capabilities
and operational cybersecurity needs. Many existing approaches
focus on narrow applications such as static intrusion detection
or policy enforcement, with limited adaptability to evolving
threats and polymorphic attack patterns. These gaps motivate
the development of our proposed system, which aims to deliver
a robust approach to threat detection in consumer electronics
security systems.

III. P ROPOSED M ETHODOLOGY
The proposed SYNAPS is designed with a dual-pipeline
neuro-symbolic architecture that unifies data-driven learning
with expert-defined reasoning for proactive cybersecurity. The
system processes incoming device telemetry through two
parallel paths: (1) a neural anomaly detection pipeline, where
an LSTM autoencoder models normal behavioral patterns and
produces a continuous anomaly score, and (2) a symbolic
reasoning pipeline, where a curated set of human-defined security rules computes risk indicators based on policy violations.
These two risk signals are fused into a hybrid risk score that
balances contextual adaptability with explainable logic.

2302

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

TABLE I
C OMPARATIVE S UMMARY OF N EURO -S YMBOLIC C YBERSECURITY A PPROACHES

After minimizing this loss, the network learns benign operating patterns. The hidden state h i from the LSTM captures
temporal context and is projected into a probabilistic neural
anomaly score:
h i = LSTM(xi−T :i ),

Fig. 1.

The risk assessment module in SYNAPS.

A. Risk Score Generation
This component of the SYNAPS is depicted in Fig. 1, which
provides context-aware cybersecurity risk assessments. The
neuro-symbolic (NS) design fuses data-driven learning with
expert-defined rules. The neural network captures nonlinear
patterns and contextual anomalies from device telemetry, and
the symbolic reasoning layer enforces domain-specific policies
derived from expert knowledge.
1) Model Initialization: First, we define the input data as
a sequence of feature vectors: X = {x1 , x2 , . . . , xn }, xi ∈
Rd where each xi is a multidimensional feature set extracted
from system behavior such as login timestamps, activities, file
accesses, and network flows.
2) Neural Component: Once the input feature sequences
are defined, they are passed into the neural module, which
learns to model temporal dependencies and behavioral patterns
that simple rule-based systems cannot capture. We employ an
LSTM-based autoencoder [24], where the encoder compresses
a sliding window of past observations (xi−T :i ) into a latent
vector z i , and the decoder reconstructs the sequence x̂i−T :i :
Lrec (xi−T :i ) =

i
X
1
T +1

j=i−T

2

x j − x̂ j 2

(1)

f N N (xi ) = σ (W h i + b)

(2)

where W and b are learnable parameters and σ (·) is a sigmoid
activation mapping the score to [0, 1].
3) Symbolic Component and Fusion (NS-Only): After
deriving the neural anomaly scores, the outputs are passed
to the symbolic reasoning module, which interprets them
alongside predefined security rules to produce an explainable
risk estimate. This module g S R (xi ) evaluates expert-defined
security rules and computes a normalized symbolic risk score.
Each rule ri has a severity weight wi normalized such that
P
i wi = 1. The final hybrid risk estimate integrates neural
and symbolic evidence as follows:
R(xi ) = α f N N (xi ) + (1 − α) g S R (xi )

(3)

where α controls the contribution of the neural component and
(1−α) the symbolic one. The NS-Only model terminates here
and uses R(xi ) as a continuous risk level for binary assessment
(benign vs. malicious).
4) Extension to Multiclass Threat Prediction (NS-MLP): To
move beyond binary decisions, the NS-MLP variant uses the
fused NS representation as input to a shallow MLP. The neural
hidden state h i , symbolic activations g S R (xi ), and hybrid risk
score R(xi ) are concatenated into:
zi = [ h i ∥ g S R (xi ) ∥ R(xi ) ]

(4)

The vector zi is then passed through a lightweight MLP
classifier:

ŷi = Softmax W2 ReLU(W1 zi + b1 ) + b2
(5)
This extension differentiates among multiple attack types to
transform fused risk estimates into fine-grained threat labels.

DAS: SYNAPS: A NS FRAMEWORK FOR PROACTIVE SECURITY IN CONSUMER ELECTRONICS

2303

Algorithm 2 Symbolic Risk Weight Optimization
Input : Set of symbolic rules {ri } with base weights wi
and observed violation rates vi
Output: Updated risk weights w̃i
1 foreach rule ri do
2
Compute adjusted weight: w̃i = wi · (1 + λvi );
P
3 Normalize weights: w̃i = w̃i /
j w̃ j ;
4 return {w̃i }

5) Hyperparameter Selection: Once the architecture is
established, the main hyperparameters are optimized to balance accuracy in the NS-MLP model. To optimize the
LSTM window size T , we computed autocorrelations of each
time-series feature and conducted a validation grid search
T ∈ {5, 10, 20, 30, 50} by selecting T = 10 for the best
reconstruction-error AUC. In g S R (·), rule weights wi were
fine-tuned by ±10% on validation data to maximize symbolic score. The fusion weight α was optimized over α ∈
{0.0, 0.1, . . . , 1.0}, with α = 0.7 giving the highest validation
accuracy. Finally, the binary decision output is obtained by
thresholding R(xi ) at τ :
(
1, if R(xi ) ≥ τ,
ŷi =
(6)
0, otherwise.
B. Symbolic Logic Layer
After tuning the key hyperparameters, SYNAPS proceeds to
the symbolic reasoning layer, which applies explicit rules to
derive policy-aligned risk scores. The symbolic layer computes
a risk score based on rule violations. Each rule represents a
specific security policy or behavioral constraint, such as login
limits or access restrictions. Symbolic rules {r j }mj=1 originate
from three sources: (i) domain and compliance policies, (ii)
incident post-mortems and near-miss reports, and (iii) patterns surfaced by the neural component (LSTM-AE) through
reconstruction error and attention on features. A candidate
rule r j is admitted only if it satisfies coverage (flags ≥ θcov
fraction of historical incidents) and specificity (false-positive
rate ≤ θfpr ) on a validation set. Each rule is specified as a
temporal predicate ϕ j over a sliding window Wt :


δ j (xi , t) ∈ {0, 1}, δ j (xi , t) = ⊮ ϕ j (xi,[t−|Wt |+1:t] )
(7)
To handle uncertainty, we also define a soft indicator
δ̃ j (xi , t) = σ (s j (xi , t) − τ j )/γ j with logistic σ (·), score
s j (·), threshold τ j , and temperature γ j . Recent violations are
emphasized via time decay d(1) = exp(−λ1). For sequence
xi , the LSTM autoencoder produces per-timestep error et =
∥xt − x̂t ∥2 and latent embeddings z t . Rules may depend on
(et , z t ), which is linked to learned anomalies and context with
explicit constraints:
P K −1
⊮[ et−k > τe ] ≥ ρ, ϕcontext : z t ∈ Crestricted ,
ϕspike : K1 k=0
(8)
Each rule weight w j reflects impact and reliability. Let
I j be the operational impact (0–1), estimated with a risk

Fig. 2.

Overview of the SYNAPS threat prediction pipeline.

matrix score. TPR j , FPR j be empirical rates on validation
and Cfp , Cfn > 0 the costs. We define
a utility-aligned weight

w j ∝ I j · α TPR j − β FPR jP, α = Cfn , β = Cfp and
calibrate the proportionality by
j w j = 1. Thresholds τ j
are selected by maximizing Youden’s J = TPR − FPR subject
to FPR ≤ θfpr (operating constraint). To avoid redundant rules,
we solve a sparse selection [25] as given below:
X


min E ℓ(y,
w j δ̃ j ) + λ1 ∥w∥1 + λ2 overlap (w)
(9)
w≥0

j

where ℓ is logistic loss on labeled incidents y ∈ {0, 1} and
overlap penalizes jointly active highly correlated rules. With
time decay d(1) the score is:
gSR (xi , t) =

m
X

wj

j=1

g̃SR = P

j wj

|W
t |−1
X

d(1) δ̃ j (xi , t − 1)

1=0

gSR
P

1 d(1)

∈ [0, 1].

(10)

We evaluate each rule r j by removing it and measuring the
change in AUROC and F1 for incident detection. We also test
how sensitive the risk score g̃SR is to ±10% adjustments in
its weights w j and thresholds τ j , and we verify that the score
is well-calibrated to the observed risk. Each alert also reports
which rules were triggered, their individual contributions w j ·
δ̃ j , and the corresponding time window.
C. Threat Prediction Pipeline
To extend beyond basic anomaly detection, SYNAPS incorporates a threat prediction and simulation pipeline, as shown in
Fig. 2. It advances the NS model by adding layers for synthetic
attack generation, vulnerability prioritization, and adversarial
training.
1) Synthetic Attack Generation (NS-Aug): A key limitation
of device-level security datasets is the lack of diversity in
advanced or stealthy attack samples. To mitigate this, the
NS-Aug variant introduces a synthetic attack generation mechanism that expands the training data using domain-aware
transformations. Known attack traces xreal are perturbed to
create realistic variants:

xsynthetic = T xreal , θ θ
∼ U(θmin , θmax )
(11)

2304

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

where T is a transformation function (e.g., feature masking)
parameterized by θ. These additional synthetic samples diversify the model’s training distribution and reduce overfitting for
better generalization to unseen attack patterns.
2) Adversarial Training (NS-Adv): While synthetic augmentation enhances diversity, it does not guarantee robustness
against deliberately crafted evasions. To counter this, the
NS-Adv variant employs adversarial learning using a Generative Adversarial Network (GAN) [26]. The generator G
produces perturbed attack examples designed to fool the discriminator D, which learns to distinguish real from synthetic
inputs:

baseline profiling over a historical window of T time steps. For
each feature, the mean and variance are computed as follows:





min max V (D, G) = Ex∼ preal log D(x) + Ez∼ pz log 1 − D(G(z))

|x − µt | > k · σt

G

T

µt =

This min-max training process hardens the classifier by exposing it to evasive attack patterns for improving resilience to
zero-day and adversarial scenarios.
3) Critical Vulnerability Identification: To focus learning
and reasoning on the most severe threats, SYNAPS incorporates a vulnerability prioritization mechanism that adjusts
symbolic rule weights based on empirical exploit data. Each
vulnerability vi is scored by its observed frequency impact:
Scorevuln (vi ) = freq(vi ) × impact(vi )
] vuln (vi ) =
Score

Scorevuln (vi )
max j Scorevuln (v j )

(13)
(14)

The normalized score widetildeScorevuln ∈ [0, 1] dynamically scales each symbolic rule weight. These normalized
priorities then modulate our symbolic rule weights w j :

] vuln (vr j )
w j ← w j × 1 + Score

(15)

Rules tied to high-risk vulnerabilities have proportionally greater influence in the overall risk computation.
Each symbolic rule is represented as a pair: Ri =
(conditioni , severityi ), where severityi ∈ {1, 2, 3}. where
conditioni defines a security policy and severity severityi
quantifies its criticality. The aggregated symbolic score for a
device instance is then normalized as follows:
Sraw =

n
X

ai · severityi

(16)

i=1

where ai ∈ {0, 1} indicates whether the rule i is triggered
(1) or not (0). And, n is the total number of symbolic
rules defined for that device class. This score reflects the
cumulative symbolic risk before normalization. To map raw
symbolic scores, we perform min-max normalization based
on the maximum possible symbolic score:
Ssym =

Sraw
,
Smax

where Smax =

n
X

severityi

(17)

i=1

4) Anomaly Detection and Threat Classification (NS-MLP):
To model normal operational behavior, SYNAPS performs

(18)

i=1

However, systems naturally exhibit variation, so the framework
also calculates the variance σt2 to measure typical fluctuations:
T

σt2 =

1 X
(xi − µt )2
T

(19)

i=1

and deviations from the baseline are flagged when:

D

(12)

1 X
xi
T

(20)

Here x is the newly observed value, µt is the previously
computed baseline mean, and k is a tunable threshold parameter that controls the system’s sensitivity. A high threshold
k = 3 flags only extreme outliers, and smaller values (1.5–2)
capture subtle deviations relevant to insider or firmware-level
threats. Finally, to ensure model portability across heterogeneous devices and firmware versions, SYNAPS incorporates
a cross-device transfer learning module (NS-Trans) described
in the following section.
5) Cross-Device Transfer Learning Module (NS-Trans): To
enable reliable transfer across devices operating under different firmware versions, NS-Trans relies on a shared telemetry
schema rather than identical raw data [27]. All participating
devices record standardized behavioral indicators to ensure
that each input sample xi lies within a common feature space
Rd , where each dimension corresponds to a semantically
consistent measurement. During transfer, the pretrained source
model f source (x) is augmented by a lightweight correction term
1 f (x; θ1 ), parameterized by θ1 and fine-tuned using a small
N
. The objective
set of labeled target-domain samples (xi , yi )i=1
minimizes a regularized empirical loss to adapt the model with
minimal parameter updates, as given below:
∗
θ1
= arg min
θ1

N

1 X 
L yi , f source (xi ) + 1 f (xi ; θ1 ) + λ∥θ1 ∥22
N
i=1

(21)
Here, L denotes the loss function and λ controls the strength
of L∈ regularization to limit the correction magnitude. In our
implementation, λ = 0.01 provided stable adaptation and
prevented overfitting. The correction layer 1 f (x; θ1 ) is realized as a single dense layer stacked over frozen intermediate
representations from the LSTM encoder. Once trained, the
adapted model is obtained as stated below:
∗
f target (x) = f source (x) + 1 f (x; θ1
)

(22)

In practice, the correction function can be expressed as a
simple affine transformation:
1 f (x; θ1 ) = W1 φ(x) + b1

(23)

where φ(x) is the fixed feature representation extracted from
f source , and W1 , b1 are learnable adaptation parameters. This
strategy enables cross-device generalization with minimal

DAS: SYNAPS: A NS FRAMEWORK FOR PROACTIVE SECURITY IN CONSUMER ELECTRONICS

2305

Fig. 3. Model score behaviors observed with a window size T = 10, hidden dimension H = 128, batch size = 64, and learning rate = 10−3 . (a) Reconstruction
loss convergence. (b) Neural-score classification accuracy. (c) Distribution of symbolic rule-based scores across varying severity levels. (d) Combined hybrid
risk scores α = 0.7.

TABLE II
E XPERIMENTAL S ETUP AND T OOLS

C. Model Behavior and Anomaly Differentiation
As illustrated in Fig. 3, the anomaly detection components
of SYNAPS effectively separate normal and malicious device
behaviors. The LSTM autoencoder quickly learns compact
representations of benign telemetry patterns, and the symbolic
rule engine provides policy-driven risk signals. When fused,
the combined scores produce an amplified separation between
benign and attack distributions so that the NS fusion enhances
anomaly discrimination and robustness on edge devices.
D. Threat Prediction Metrics Across Models

retraining cost and ensures compatibility across firmware versions, which makes NS-Trans suitable for resource-constrained
IoT environments.
IV. E XPERIMENTAL R ESULTS AND A NALYSIS
We examine each component of SYNAPS: risk scoring,
anomaly detection, and threat prediction by comparing NeuralOnly, Symbolic-Only, NS-Only, and NS variants (NS-MLP,
NS-Aug, NS-Adv, and NS-Trans).
A. Environment Setup
The experimental setup and tools are summarized in
Table II. The symbolic rules were implemented in Python as
a custom logic engine. Each experiment is repeated five times
with different random seeds, and the mean values of accuracy,
precision, recall, F1-score, and ROC-AUC are reported. The
experiments are fully reproducible, and performance comparisons across all SYNAPS variants are fair and consistent. Our
experiment code is available on the GitHub repository [29].
B. Data Loading and Preprocessing
The UNSW-NB15 dataset [28] is used to evaluate the
proposed SYNAPS. The dataset covers ten traffic classes:
one normal class and nine attack categories. The testing set
contains 82,332 samples, and the training set includes 175,341
samples. Before training, all records are cleaned by removing
identifier fields, categorical variables are one-hot encoded,
and all numeric features are scaled to the [0,1] range using
min–max normalization. The dataset is then divided into 70%
training, 20% validation, and 10% test subsets using stratified
sampling to preserve class distribution.

As part of the experimental evaluation, we benchmarked all
SYNAPS variants against pure neural and symbolic baselines
to assess predictive robustness and adaptability under realistic
IoT conditions. The results (Fig. 4) show that SYNAPS consistently outperforms both standalone components across all key
metrics. In particular, NS-Adv achieves the highest accuracy,
F1 score, and ROC-AUC, as summarized in Table III. NS variants such as NS-Aug, NS-MLP, and NS-Trans also yield
significant gains and enhance threat prediction in resourceconstrained environments.
E. Class Imbalance Mitigation
Telemetry-based threat detection often suffers from severe
class imbalance [30], where benign samples dominate, and
certain attack types appear rarely. To address the class imbalance inherent in telemetry-based threat detection, we apply
strategies at both the anomaly detection (LSTM autoencoder)
and classification (NS-MLP) stages. On the other hand, the
NS-MLP classifier is responsible for multiclass threat prediction that directly addresses class imbalance using a weighted
cross-entropy loss function.
F. Symbolic Score Analysis
To demonstrate the discriminative power of the symbolic
risk component, we analyzed two representative telemetry logs: one benign and one malicious. In the benign
example (Listing 1), the device executed standard API
calls (open_socket, read_config, send_data) and
accessed only a secure port. The symbolic rule engine
matched no rules with a raw symbolic score of Sraw =
0, and consequently a normalized symbolic risk score of

2306

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

TABLE III
P ERFORMANCE C OMPARISON ACROSS M ODELS AND VARIANTS

Fig. 4. Test set evaluation across SYNAPS variants: (a) threat prediction accuracy for each model, (b) heatmap of test-set metrics, (c) ROC-AUC curves for
each variant, and (d) Precision-Recall curves with average precision for each variant.

Fig. 5. Training metrics for all SYNAPS variants: (a) training accuracy, (b) training loss, (c) training precision, (d) training F1 score, (e) training recall, and
(f) overall training performance comparison across variants.

Listing 1: No anomalies and symbolic risk contribution is 0.

Ssym = 0.0. Listing 2 illustrates a device report in which
several high-severity security rules are triggered. The log

contains suspicious API calls, abnormal port activity, and rule
matches that correspond to critical threat patterns. In contrast, the attack example includes unauthorized flash memory
access (access_flash, write_flash) of system logs
(disable_logging), and use of insecure network ports.
Three symbolic rules were fired, with severities of 3, 2, and 3,
respectively, with a raw score of Sraw = (1·3)+(1·2)+(1·3) =
8. The maximumPpossible symbolic score for this device
n
type is Smax =
i=1 severityi = 21. And the normalized
8
raw
symbolic risk score becomes Ssym = SSmax
= 21
≈ 0.381 (from
equation 17). This non-zero value illustrates that the symbolic
module contributes a meaningful and explainable component
to the overall risk assessment.

DAS: SYNAPS: A NS FRAMEWORK FOR PROACTIVE SECURITY IN CONSUMER ELECTRONICS

2307

Fig. 6. Validation metrics for all SYNAPS variants: (a) validation accuracy, (b) validation loss, (c) validation precision, (d) validation F1 score, (e) validation
recall, and (f) overall validation performance comparison across variants.

TABLE IV
O N -D EVICE I NFERENCE L ATENCY AND M EMORY U SAGE

Listing 2: Multiple high-severity rules fired.

G. Training, Validation, and Test Performance Across Models
Table III reports detailed metrics for each model on training,
validation, and test splits. Across all phases, neural-only and
symbolic-only models lag behind the hybrid variants. NSMLP already outperforms both baselines. NS-Adv achieves
the best overall results, with a test accuracy of 93.3% and
ROC-AUC of 0.971, with a clear benefit from its adversarial
robustness training. Fig. 5 and Fig. 6 compare training and
validation metrics for all variants. On the other hand, NS-Adv
and NS-Aug converge faster and maintain higher precision and
recall curves than the other models. The lightweight NS-MLP
variant also shows stable learning behavior. The latency and
memory consumption results of various SYNAPS variants are
summarized in Table IV. Furthermore, the NS-Adv model
achieves a balanced trade-off between inference speed and
accuracy, with a mean latency of 0.6192 ms and a standard
deviation of 0.0545 ms.
H. Future Work and Limitations
The proposed SYNAPS shows strong performance, but
it still has some limitations and areas for improvement.

At present, the experiments are based mainly on the UNSWNB15 dataset, which may not capture the full variety of
consumer devices or real-world network conditions. The symbolic rules depend on established expert knowledge, which
may overlook evolving attack patterns and adaptive adversaries to exploit unrecognized vulnerabilities. The system’s
real-time efficiency, energy consumption, and uncertainty
calibration have not been comprehensively evaluated on
resource-constrained devices. In addition, privacy and rigorous
threat-model verification need more scrutiny before extensive
implementation. In the future, we plan to extend SYNAPS with
multi-dataset validation for continuous adaptation and humanin-the-loop rule updates using knowledge graphs. We will add
stronger adversarial testing and uncertainty-aware thresholds
to improve trust and resilience. To support practical use, future
work will also include lightweight model compression for
edge devices and federated learning for secure collaboration
to ensure consistent protection across device types.
V. C ONCLUSION
In this work, we introduced SYNAPS, a hybrid system
that combines neural networks and symbolic rules to detect
and predict security threats. The proposed proactive approach
understands complex patterns and provides explainable decisions. We also improved the system resilience using variant

2308

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 72, NO. 1, FEBRUARY 2026

mechanisms, like data augmentation, adversarial training, and
transfer learning, to make it more robust and accurate. Our
experiment shows that the advanced versions of SYNAPS
perform much better than models that use purely neural or
symbolic baselines. The variant models achieved very high
accuracy and recall in detecting both common and hidden
attacks. Overall, SYNAPS shows that combining neural intelligence with symbolic reasoning can lead to more accurate and
explainable security systems for consumer electronic devices.
For future work, we plan to extend SYNAPS toward real-time
threat monitoring to enable on-the-fly defense against evolving
adversarial behaviors.

R EFERENCES
[1] D. Das, P. Chatterjee, S. Banerjee, U. Ghosh, and M. S. Al-Numay,
“Blockchain-enabled federated learning for security and privacy in
consumer electronics devices,” IEEE Trans. Consum. Electron., vol. 71,
no. 1, pp. 2262–2270, Feb. 2025.
[2] P. Chatterjee, D. Das, D. B. Rawat, U. Ghosh, S. Banerjee, and
M. S. Al-Numay, “Digital twins and blockchain fusion for security
in metaverse-driven consumer supply chains,” IEEE Trans. Consum.
Electron., vol. 70, no. 3, pp. 5688–5697, Aug. 2024.
[3] S. Qin et al., “A partially labeled anomaly data detection approach based
on prioritized deep reinforcement learning for consumer electronics
security,” IEEE Trans. Consum. Electron., vol. 70, no. 4, pp. 6452–6462,
Nov. 2024.
[4] B. R. Maddireddy and B. R. Maddireddy, “Cybersecurity threat landscape: Predictive modelling using advanced ai algorithms,” Int. J. Adv.
Eng. Technol. Innov., vol. 1, no. 2, pp. 270–285, 2022.
[5] R. Dong, B. Cui, Y. Sun, and J. Yang, “BTIDEC: A novel detection
scheme for CPU security of consumer electronics,” IEEE Trans. Consum. Electron., vol. 70, no. 1, pp. 4515–4523, Feb. 2024.
[6] S. Ul Haq, Y. Singh, A. Sharma, R. Gupta, and D. Gupta, “A survey
on IoT & embedded device firmware security: Architecture, extraction
techniques, and vulnerability analysis frameworks,” Discover Internet
Things, vol. 3, no. 1, p. 17, Oct. 2023.
[7] Y. Nasser and M. Nassar, “Toward hardware-assisted malware detection
utilizing explainable machine learning: A survey,” IEEE Access, vol. 11,
pp. 131273–131288, 2023.
[8] Y. K. Sharma, D. S. Tomar, R. K. Pateriya, and S. Solanki, “GNSTAM:
Integrating graph networks with spatial and temporal signature analysis for enhanced Android malware detection,” IEEE Access, vol. 13,
pp. 81326–81346, 2025.
[9] J. Yu, A. V. Shvetsov, and S. Hamood Alsamhi, “Leveraging machine
learning for cybersecurity resilience in Industry 4.0: Challenges and
future directions,” IEEE Access, vol. 12, pp. 159579–159596, 2024.
[10] P. Huang, E. Gönültaş, M. Arnold, K. P. Srinath, J. Hoydis, and
C. Studer, “Attacking and defending deep-learning-based off-device
wireless positioning systems,” IEEE Trans. Wireless Commun., vol. 23,
no. 8, pp. 8883–8895, Aug. 2024.
[11] B. P. Bhuyan, A. Ramdane-Chérif, R. Tomar, and T. P. Singh, “Neurosymbolic artificial intelligence: A survey,” Neural Comput. Appl.,
vol. 36, no. 21, pp. 12809–12844, 2024.
[12] B. Li et al., “LogiCity: Advancing neuro-symbolic AI with abstract
urban simulation,” in Proc. Adv. Neural Inf. Process. Syst., 2024,
pp. 69840–69864.
[13] A. Almadhor, S. Alsubai, A. A. Hejaili, Z. Klai, B. Bouallegue, and
U. Kovac, “Designing a neuro-symbolic dual-model architecture for
explainable and resilient intrusion detection in IoT networks,” Sci. Rep.,
vol. 15, no. 1, p. 42786, Nov. 2025.
[14] C. S. Kalutharage, X. Liu, and C. Chrysoulas, “Neurosymbolic learning
and domain knowledge-driven explainable AI for enhanced IoT network
attack detection and response,” Comput. Secur., vol. 151, Apr. 2025,
Art. no. 104318.
[15] A. Piplai, A. Kotal, S. Mohseni, M. Gaur, S. Mittal, and A. Joshi,
“Knowledge-enhanced neurosymbolic artificial intelligence for cybersecurity and privacy,” IEEE Internet Comput., vol. 27, no. 5, pp. 43–48,
Sep. 2023.

[16] A. Himmelhuber, D. Dold, S. Grimm, S. Zillner, and T. Runkler, “Detection, explanation and filtering of cyber attacks combining symbolic and
sub-symbolic methods,” in Proc. IEEE Symp. Ser. Comput. Intell. (SSCI),
Dec. 2022, pp. 381–388.
[17] C.-H. Bertrand Van Ouytsel, K. H. T. Dam, and A. Legay, “Symbolic
analysis meets federated learning to enhance malware identifier,” in
Proc. 17th Int. Conf. Availability, Rel. Secur., Aug. 2022, pp. 1–10.
[18] S. K. Jagatheesaperumal, S. Ali, A. Alotaibi, K. Muhammad,
V. H. C. De Albuquerque, and M. Guizani, “Generative AI-enhanced
neuro-symbolic quantum architectures for secure communications and
networking,” IEEE Netw., vol. 39, no. 5, pp. 36–43, Sep. 2025.
[19] H. Lei, Y. Ge, and Q. Zhu, “ADAPT: A game-theoretic and neurosymbolic framework for automated distributed adaptive penetration
testing,” in Proc. MILCOM-IEEE Mil. Commun. Conf. (MILCOM),
Oct. 2024, pp. 7–12.
[20] A. M. Abdallah, A. S. R. O. Alkaabi, G. B. N. D. Alameri, S. H. Rafique,
N. S. Musa, and T. Murugan, “Cloud network anomaly detection using
machine and deep learning techniques—Recent research advancements,”
IEEE Access, vol. 12, pp. 56749–56773, 2024.
[21] R. Jablaoui and N. Liouane, “Network security based combined CNNRNN models for IoT intrusion detection system,” Peer-Peer Netw. Appl.,
vol. 18, no. 3, p. 129, May 2025.
[22] S. Nalluri, M. M. Malyala, H. Kandagiri, and K. K. Kandagiri, “NSCTI:
A hybrid neuro-symbolic framework for AI-driven predictive cyber
threat intelligence,” in Proc. 4th Int. Conf. Comput. Modelling, Simulation Optim. (ICCMSO), Jun. 2025, pp. 14–21.
[23] G. Grov, J. Halvorsen, M. W. Eckhoff, B. J. Hansen, M. Eian, and
V. Mavroeidis, “On the use of neurosymbolic AI for defending against
cyber attacks,” in Proc. Int. Conf. Neural-Symbolic Learn. Reasoning,
2024, pp. 119–140.
[24] G. Wen, J. Qin, X. Fu, and W. Yu, “DLSTM: Distributed long shortterm memory neural networks for the Internet of Things,” IEEE Trans.
Netw. Sci. Eng., vol. 9, no. 1, pp. 111–120, Jan. 2022.
[25] R. Jiao, B. Xue, and M. Zhang, “Sparse learning-based feature selection
in classification: A multi-objective perspective,” IEEE Trans. Emerg.
Topics Comput. Intell., vol. 9, no. 4, pp. 2767–2781, Aug. 2025.
[26] Y. Zheng, Z. Li, X. Xu, and Q. Zhao, “Dynamic defenses in cyber
security: Techniques, methods and challenges,” Digit. Commun. Netw.,
vol. 8, no. 4, pp. 422–435, Aug. 2022.
[27] A. Hosna, E. Merry, J. Gyalmo, Z. Alom, Z. Aung, and M. A. Azim,
“Transfer learning: A friendly introduction,” J. Big Data, vol. 9, no. 1,
p. 102, Oct. 2022.
[28] UNSW_NB15. Accessed: Mar. 4, 2025. [Online]. Available:
https://research.unsw.edu.au/projects/unsw-nb15-dataset
[29] D. Das. (2025). Neuro-symbolic-threat-detection. [Online]. Available:
https://github.com/debashis2124/neuro-symbolic-threat-detection.git
[30] N. Naz et al., “Ensemble learning-based IDS for sensors telemetry data in IoT networks,” Math. Biosci. Eng., vol. 19, no. 10,
pp. 10550–10580, 2022.

Debashis Das (Member, IEEE) received the Ph.D.
degree in computer science and engineering from
the University of Kalyani, India, in 2023. He is currently with the Department of Computer Science and
Data Science, School of Applied Computational Sciences, Meharry Medical College. He has more than
50 publications in various peer-reviewed journals
and conferences and has over 1050 citations, with
an H-index of 19 and an i10-index of 33 by Google
Scholar. He is a reviewer for various peer-reviewed
journals of IEEE T RANSACTIONS, (Elsevier and
Springer). His research interests include cybersecurity, blockchain technology,
and artificial intelligence. He has served as an invited TPC Member or
the Chair for numerous international conferences, including CICBA, BCCA,
CCGRID, ICDCN, IEEE STP-CPS, ICSPIS, ISORC, and IoST. He was
recognized by Stanford University and Elsevier as among the world’s top
2 percent of scientists in 2025.
PAPER_TEXT
