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
# [720] Learning in Multiple Spaces: Prototypical Few-Shot Learning With Metric Fusion for Next-Generation Network Security
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
编号：720
题名：Learning in Multiple Spaces: Prototypical Few-Shot Learning With Metric Fusion for Next-Generation Network Security
年份：2026
DOI：10.1109/tnsm.2026.3665647
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2026.3665647.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：无
相关性：强相关，分数 11
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\720.txt
- 原始字符数：54131
- 本次发送字符数：54131
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
3156

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Learning in Multiple Spaces: Prototypical Few-Shot
Learning With Metric Fusion for Next-Generation
Network Security
Fernando Martinez-Lopez, Lesther Santana, Mohamed Rahouti , Member, IEEE,
Abdellah Chehri , Senior Member, IEEE, Shawqi Al-Maliki, and Gwanggil Jeon , Senior Member, IEEE
Abstract—As next-generation communication networks
increasingly rely on AI-driven automation, ensuring robust
and secure intrusion detection becomes critical, especially
under limited labeled data. In this context, we introduce
Multi-Space Prototypical Learning (MSPL), a few-shot intrusion
detection framework that improves prototype-based classification
by fusing complementary metric-induced spaces (Euclidean,
Cosine, Chebyshev, and Wasserstein) via a constrained weighting
mechanism. MSPL further enhances stability through Polyakaveraged prototype generation and balanced episodic training
to mitigate class imbalance across diverse attack categories. In
a few-shot setting with as few as 200 training samples, MSPL
consistently outperforms single-metric baselines across three
benchmarks: on CICEVSE Network2024, AUPRC improves
from 0.3719 to 0.7324 and F1 increases from 0.4194 to 0.8502;
on CICIDS2017, AUPRC improves from 0.4319 to 0.4799; and
on CICIoV2024, AUPRC improves from 0.5881 to 0.6144. These
results demonstrate that multi-space metric fusion yields more
discriminative and robust representations for detecting rare and
emerging attacks in intelligent network environments.
Index Terms—Few-shot learning, network intrusion detection,
metric-based learning, multi-space prototypical learning.

I. I NTRODUCTION
HE integration of artificial intelligence (AI) into nextgeneration communication networks has revolutionized
threat detection. However, it has also introduced new vulnerabilities that adversaries increasingly exploit. The rapid
evolution of cyber threats poses a critical challenge in cybersecurity. Attackers now leverage sophisticated techniques to
compromise AI-driven systems and exploit model weaknesses
[1]. While traditional network intrusion detection systems
(NIDS) remain effective against known attack signatures, they

T

Received 4 August 2025; revised 9 January 2026; accepted 13 February
2026. Date of publication 20 February 2026; date of current version 17 March
2026. The associate editor coordinating the review of this article and approving
it for publication was A. Khowaja. (Corresponding author: Abdellah Chehri.)
Fernando Martinez-Lopez, Lesther Santana, and Mohamed Rahouti are with
the Department of Computer and Information Science, Fordham University,
New York City, NY 10458 USA (e-mail: fmartinezlopez@fordham.edu;
lsantanacarmona@fordham.edu; mrahouti@fordham.edu).
Abdellah Chehri is with the Department of Mathematics and Computer
Science, Royal Military College of Canada (RMC), Kingston, ON K7K 7B4,
Canada (e-mail: chehri@rmc.ca).
Shawqi Al-Maliki is with the Information and Computing Technology (ICT)
Division, College of Science and Engineering, Hamad Bin Khalifa University,
Doha, Qatar (e-mail: shalmaliki@hbku.edu.qa).
Gwanggil Jeon is with the Department of Embedded Systems Engineering, Incheon National University, Incheon 22012, South Korea (e-mail:
gjeon@inu.ac.kr).
Digital Object Identifier 10.1109/TNSM.2026.3665647

struggle to detect emerging, rare, or zero-day attacks. This
challenge is especially acute when labeled data is scarce and
attack behaviors evolve dynamically [2], [3], [4]. This growing
gap highlights the urgent need for adaptive, data-efficient, and
resilient detection frameworks. Such frameworks must operate
reliably in complex, AI-augmented network environments.
Few-shot learning (FSL) has emerged as a promising solution to these challenges by enabling models to generalize from
minimal labeled data using meta-learning principles [5], [6],
[7]. In the context of federated and distributed AI systems,
FSL offers a pathway to privacy-preserving and scalable
intrusion detection. However, early applications of FSL in
cybersecurity have revealed persistent issues—including data
imbalance, limited scalability, and poor generalization to realworld network conditions [8], [9]. These limitations are further
exacerbated by the rise of generative AI, model inversion,
and poisoning attacks, which threaten both data integrity and
model trustworthiness. Addressing these concerns requires
a new generation of secure and trustable AI-based systems
that can withstand adversarial manipulation while maintaining high detection performance in dynamic network
environments.
Recent advancements have sought to overcome these challenges through innovative frameworks and methodologies. For
instance, Ma et al. [10] introduced a few-shot IoT attack
detection framework that integrates adaptive loss weighting to
enhance detection performance. Similarly, hybrid and metricbased approaches, such as those proposed by Liang et al.
[11] and Zhou et al. [12], have shown promise in detecting
anomalies in complex environments like industrial IoT and
cyber-physical systems. Despite these advancements, critical
gaps still need to be addressed, including the inability to
robustly handle diverse attack scenarios and limited scalability
for real-world deployment.
We present a multi-space prototypical learning (MSPL)
framework for few-shot attack detection that leverages complementary metric spaces - Euclidean, Cosine, Chebyshev,
and Wasserstein distances - to capture diverse attack pattern
properties [13], [14]. Our approach extends beyond Martinez et al.’s dual-space methodology [15] to capture attack
pattern characteristic through distinct geometric and statistical
perspectives. In addition to that, our framework enables the
use of Polyak-averaged prototype generation and balanced
episodic training to improve detection stability and representation across attack types.
The main contributions of this work include:

1932-4537 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

MARTINEZ-LOPEZ et al.: LEARNING IN MULTIPLE SPACES: PROTOTYPICAL FSL WITH METRIC FUSION

• A novel multi-space integration that combines four complementary distances through a constrained weighting
scheme, demonstrating consistent improvements over
single-metric baselines.
• Comprehensive validation across three benchmark
datasets (CICEVSE2024 [16], CICIDS2017 [17], and
CICIoV2024 [18]) demonstrating the framework’s
generalizability and superior performance in detecting
both high-profile and low-profile attacks, particularly
excelling at identifying rare and zero-day threats with as
few as 200 training samples.
• A balanced episodic training strategy that ensures equal
representation of attack classes through stratified sampling and controlled repetition, specifically addressing the
challenge of imbalanced cybersecurity datasets.
• Polyak-averaged prototype generation that maintains
exponential moving averages of prototypes across training episodes, substantially reducing representation variability and improving convergence.
Collectively, these contributions form a cohesive MSPL
framework that is both practically deployable and theoretically grounded for next-generation network settings. In turn,
tackling these challenges not only progresses the forefront
of few-shot intrusion detection but also lays the groundwork
for creating more resilient and adaptable cybersecurity systems. The integration of complementary learning paradigms
highlights the potential for future research to explore hybrid
methodologies that extend the framework’s capabilities to
multimodal datasets and real-time detection systems [10], [19].
The remainder of this paper is organized as follows:
Section II reviews related work; Section III introduces the
foundations of multi-space few-shot attack detection; Section IV presents MSPL; Section V analyzes its theoretical
properties; Section VI reports the experimental results; and
Section VII concludes the paper.
II. R ELATED W ORK
FSL has emerged as a powerful approach to address data
scarcity in network intrusion detection [5], [6], [20]. Early
work by Chowdhury et al. [21] demonstrated the effectiveness of deep learning for detecting common attacks, though
scalability remained a challenge. Iliyasu et al. [22] improved
discriminative power using supervised autoencoders, particularly for low-profile and imbalanced attacks. Other studies
applied FSL with prototypical networks [8], FS-IDS for imbalanced data [9], and IoT attack detection via self-supervised
learning and adaptive loss weighting [10]. While these methods enhance generalization, they rely on a single similarity
space, limiting expressiveness under distributional shifts. In
contrast, our MSPL framework fuses four complementary metrics through constrained weighting, enabling richer prototype
comparisons under data scarcity.
Generative and retrieval-based strategies have also been
explored. Aharon et al. proposed a GAN-inspired framework for API attack detection [23] and a classificationby-retrieval approach leveraging embeddings [24], both
addressing dynamic API threats. Compared to these, MSPL
strengthens prototype geometry by integrating multiple metric
perspectives. Further advancements include FSL for SCADA
[25], industrial IoT [11], and cyber-physical systems [12], as

3157

well as meta-learning [26], class-incremental learning [27],
space-decoupled prototypes [28], and graph-based methods
[29], [30].
Unlike approaches that modify the embedding architecture
(e.g., space decoupling or graph structure), MSPL improves
robustness by enriching the distance computation itself via
multi-metric fusion.
A. Metric-Based Learning in Cybersecurity
The metric space is critical in FSL for intrusion detection. While traditional approaches rely on Euclidean or
cosine metrics, recent studies explore advanced spaces to
improve performance. Xu et al. [31] apply meta-learning with
task-specific adaptations, and Tian et al. [13] use the Wasserstein metric for spoofing detection in WiFi systems. These
works show that different metrics capture distinct notions of
similarity
Unlike such single-metric formulations, MSPL integrates
Euclidean, Cosine, Chebyshev, and Wasserstein distances concurrently, allowing the decision rule to benefit from both
pointwise and distributional discrepancies.
In [12], a Siamese network-based approach integrates multiple metrics for anomaly detection in industrial environments.
While Siamese-style designs can combine similarity cues, they
are not designed as a constrained multi-space prototype fusion
mechanism for few-shot intrusion detection. MSPL complements this line of work by formalizing multi-metric fusion
around prototypical representations and stabilizing learning
across episodes.
Additionally, Miao et al. [32] proposed a Siamese prototypical network (SPN) incorporating out-of-distribution detection
for traffic classification. This method is particularly adept
at identifying anomalous traffic patterns that deviate significantly from known attack profiles, demonstrating the utility
of integrating prototypical networks with robust metric-based
evaluation mechanisms. Autoencoder-based approaches have
also been explored for metric-driven FSL. He et al. [33] utilized deep autoencoders to capture rich feature representations
for malicious traffic detection. Their approach combines feature learning with metric-based classification, achieving high
accuracy in few-shot scenarios. Further, Vijayakanthi et al.
[14] introduced a differential metric-based methodology for
non-profiled side-channel analysis, primarily in cryptographic
contexts. While their work is focused on a different domain,
it provides valuable insights into designing adaptive metriclearning systems that could be applied to intrusion detection.
B. Hybrid and Multi-Space Approaches
Hybrid and multi-space learning approaches have shown
promise in addressing the limitations of single-metric models.
For instance, ProtÉdge [19] combines multiple metrics to
improve detection accuracy in software-defined networks, and
[34] applies cross-network meta-learning for unseen malware variants. The effectiveness of metric fusion is further
demonstrated in [15], where a dual-space prototypical network
enhances DDoS attack detection by integrating complementary
metric spaces. Compared to prior fusion efforts that typically
combine a small number of metrics/spaces (e.g., dual-space
designs), MSPL broadens the fusion to four complementary

3158

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

metrics and couples it with a constrained weighting scheme
to maintain stable prototype-based decision boundaries.
Further studies, such as [22] and [35], focus on combining
supervised and unsupervised learning techniques to improve
generalization. Additionally, [36] proposes a model-agnostic
framework that integrates generative models with metric-based
learning, significantly improving the detection of low-profile
attacks. Graph neural networks (GNNs) have also been utilized
for few-shot anomaly detection [37], demonstrating the potential of graph-based metrics in capturing structural patterns. In
contrast to hybrid pipelines that expand training signals via
auxiliary objectives (e.g., generative or contrastive learning),
MSPL targets the metric layer directly, using multi-metric
fusion and episode-level stabilization to improve few-shot
robustness.
Qin et al. [38] developed a meta-learning-based framework
for zero- and few-shot face anti-spoofing. Although their
focus is on biometric security, the proposed meta-model offers
insights into how meta-learning can generalize across unseen
attack scenarios, a principle that could be extended to intrusion
detection systems. More efforts include FewM-HGCL [39],
which employs contrastive learning on heterogeneous graphs
for malware detection, and utilizes graph contrastive learning
for classifying network flow attacks. These approaches underscore the importance of leveraging diverse feature spaces and
learning paradigms to tackle the evolving landscape of cyber
threats.
C. Uniqueness of This Paper
This paper introduces the MSPL framework, which combines four complementary metric spaces, Euclidean, Cosine,
Chebyshev, and Wasserstein, via a constrained fusion of
normalized distancesP(z-score with clipping) with simplex
weights (wm ≥ 0,
m wm = 1), preventing scale dominance across metrics and yielding a well-behaved combined
distance. Unlike existing single-metric or dual-metric prototypical baselines, MSPL uses this metric-preserving fusion to
exploit distinct topological cues under data scarcity. MSPL
further incorporates two stabilizers tailored to few-shot NIDS:
(i) Polyak/EMA-based prototype generation to reduce episodeto-episode embedding variance, and (ii) a balanced episodic
sampling strategy that enforces per-episode class parity (with
controlled repetition when needed). Together, these design
choices lead to more robust detection of both high-profile
and low-profile attacks, with consistent gains on rare/zero-day
categories.
III. F OUNDATIONS OF M ULTI -S PACE L EARNING FOR
F EW-S HOT ATTACK D ETECTION
Conventional metric-based FSL frameworks typically
employ Euclidean distance to quantify relationships between
samples. While this is effective in many applications, this
approach imposes a fixed topological assumption on the data,
potentially overlooking critical variations in attack patterns. In
contrast, cyber threats manifest in diverse ways, ranging from
subtle deviations in statistical distributions to structural anomalies in network traffic, requiring a multi-faceted approach.
Single metric-based methods, like regular prototypical networks, often fail to capture the full complexity of attack
patterns due to:

• Attack variability across feature representations: Certain attacks (e.g., adversarial traffic) exhibit directional
similarity in feature space, while others (e.g., protocol
abuse) differ in absolute magnitude.
• Class distribution skewness: Network intrusion datasets
are inherently imbalanced, with some attack types significantly underrepresented. A single distance metric can
overfit to dominant classes while failing to generalize to
rare attack instances.
• Data geometry and structure: Some attack types are
better differentiated based on distributional discrepancies
(e.g., statistical shifts), while others require pointwise
comparisons based on individual feature deviations. In
fact, critical discriminative features can alternate between
localized anomalies (single-feature spikes detectable
through Chebyshev distance) and systemic distribution
shifts (Wasserstein-visible pattern deformations).
By introducing multiple metric spaces, we can mitigate
the biases inherent in monolithic learning and enhance the
ability to differentiate between diverse and overlapping traffic patterns across multiple threat categories. Specifically,
integrating Euclidean, Cosine, Chebyshev, and Wasserstein
distances enables the framework to capture local and global
structural variations in attack data.
A. Complementary Roles of Multiple Metric Spaces
Each metric space directly addresses the limitations of
single-space learning through complementary geometric perspectives:
• Euclidean distance: Measures absolute differences
between feature vectors, effective for attacks with clear
separability based on magnitude.
• Cosine distance: Captures angular similarity between
samples, useful for detecting adversarial perturbations or
slight variations in network traffic patterns.
• Chebyshev distance: Emphasizes the largest feature
deviation across dimensions, helping to detect localized
anomalies in specific network attributes.
• Wasserstein distance: Compares entire statistical distributions, enabling the detection of subtle, aggregated
deviations in attack behaviors.
Each metric captures a different notion of similarity
(geometry, direction, worst-case deviation, distributional shift).
MSPL normalizes these distances and fuses them with
learned/assigned weights to leverage their complementary
biases within each episode. The integration of these spaces
ensures that MSPL can effectively adapt to different attack
distributions and intrusion scenarios, leading to improved
generalization.
B. The Need for a Proper Metric Space Fusion
While individual metric spaces offer distinct geometric
perspectives, their isolated application restricts the topological expressiveness necessary for comprehensive attack
characterization. Integrating these metrics requires addressing fundamental challenges in distance synthesis. First,
the numerical scales across metrics exhibit significant
√
heterogeneity—Euclidean distances typically scale with d
for d-dimensional data, while Cosine distances are bounded

MARTINEZ-LOPEZ et al.: LEARNING IN MULTIPLE SPACES: PROTOTYPICAL FSL WITH METRIC FUSION

within [0, 1], and Wasserstein distances reflect distributional
properties with domain-specific magnitudes. These discrepancies create disproportionate gradient contributions during
optimization, potentially destabilizing the learning process.
Second, direct linear combination of distances can compromise
the mathematical properties that ensure consistent prototype
generation, particularly the triangle inequality essential for
well-formed decision boundaries. Specifically, for any pair
of samples xi and xj , the fusion process must preserve the
relationship:
D(xi , xj ) ≤ D(xi , xk ) + D(xk , xj ) ∀xk ∈ X ,

(1)

where xi , xj , and xk represent individual data samples from
the input space X . The function D(xa , xb ) denotes the fused
distance between two samples xa and xb , calculated as a
weighted sum of normalized distances across multiple metric
spaces. Each individual distance is first normalized using
z-score normalization (with clipping), P
and then combined
using non-negative weights wm such that wm = 1, ensuring
that the resulting fused distance maintains essential metric
properties like the triangle inequality.
Third, attack patterns demonstrate contextual metric relevance. Some intrusions primarily manifest through direction
shifts (favoring Cosine), while others show magnitude anomalies (favoring Euclidean) or localized feature deviations
(favoring Chebyshev). Although a dynamic context-dependent
weighting method might offer flexibility in highlighting the
most informative metric for each attack type, our approach
opts for a predetermined weighting strategy. In practice, we
assign fixed, even-split weights—for instance, configurations
such as (1, 0, 0, 0), (1/2, 1/2, 0, 0), or (0, 1/3, 1/3,
1/3)—to ensure a consistent contribution from each metric
space according to the experimental setup.

3159

While traditional regularization techniques (e.g., L1 /L2
penalties, dropout) mitigate overfitting, they fail to address
the systemic instability arising from support set variability.
This requires specialized stabilization mechanisms, such as
temporal smoothing through parameter averaging and balanced
episodic construction, that specifically target the unique challenges of learning from minimal network attack samples.
IV. M ETHODOLOGY
The source code for our MSPL implementation is
available at.1
A. Problem Formulation
d
Given a dataset D = {(xi , yi )}N
i=1 , where xi ∈ X ⊆ R and
yi ∈ {1, . . ., C} is a single-label (multi-class) attack category.
For notational convenience
PC we also use its one-hot encoding
yi ∈ {0, 1}C with
k=1 yi,k = 1 (mutually exclusive
classes). Our objective is to learn a robust embedding function
fθ : X → Rm that maps traffic inputs into a representation
space where multiple distance metrics collectively enhance
intrusion pattern detection.
B. FSL for Attack Detection
In operational network environments, novel attack patterns frequently emerge with extremely limited samples,
particularly in zero-day scenarios where attack signatures
are initially unknown. Our framework addresses this FSL
challenge through a C-way K-shot formulation, where C
represents distinct attack classes, and K denotes the minimal
number of labeled samples available per attack type. Formally,
for each episodic task:
T = {(c, Sc , Qc )|c ∈ Attack Classes}

C. Stability and Generalization in Few-Shot Learning
Network intrusion detection systems face heightened stability challenges in few-shot learning settings compared to
conventional applications in computer vision or natural language processing. The fundamental issue arises from statistical
irregularity; attack distributions exhibit multimodal characteristics with long-tailed distributions across feature dimensions.
Consequently, when forming prototypes from extremely limited samples (often K < 5 for rare attack types), the resulting
representations demonstrate high variance, particularly for
zero-day attacks where emerging patterns may manifest only
in specific feature subspaces [2].
This prototype variance problem manifests itself in three
critical ways specific to network security:
• Prototype instability: Minor variations in the support
set composition produce drastically different prototype
vectors, particularly for statistically heterogeneous attacks
like DDoS or port scanning.
• Catastrophic forgetting: Sequential learning of new
attack patterns can disrupt previously established decision
boundaries, a phenomenon exacerbated by the inherent
volatility of episodic sampling.
• Confidence calibration: High variance in prototype
computation leads to miscalibrated confidence scores,
reducing the model’s ability to differentiate between
known attacks and genuinely novel intrusions.

where Sc represents the support set containing K examples
of attack class c, and Qc is the query set for evaluation. The
stratified sampling ensures the representation of rare attack
patterns:
P(|Sc | ≥ Kmin ) = 1, ∀c ∈ Attack Classes
This formulation is particularly crucial for:
• Zero-day attack detection with limited samples, enabling
rapid response to emerging threats
• Attack variant identification despite adversarial modifications designed to evade detection
• Balanced learning across attack types regardless of their
natural frequency distribution, mitigating bias toward
common attack patterns at the expense of rare but potentially severe intrusions
C. Multi-Space Prototypical Framework
Our framework extends traditional prototypical networks
through three key innovations:
1) Simultaneous operation across complementary metric
spaces
2) Constrained metric space integration
3) Polyak-averaged prototype generation
1 https://anonymous.4open.science/r/Dos-Project-325F

3160

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

The framework operates across four carefully selected metric spaces M = {E, C, Ch, W }, each capturing distinct
topological properties:
1) Distance Metrics: For an embedding fθ (x) and prototype ck , we define:
1) Euclidean distance (dE ) to capture global geometric
relationships: dE (x, ck ) = kfθ (x) − ck k2 .
2) Cosine distance (dC ) to measure directional similarities:
(x)·ck
.
dC (x, ck ) = 1 − kffθθ(x)kkc
kk
3) Chebyshev distance (dCh ) to identify maximum deviations: dCh (x, ck ) = maxi |fθ (x)i − cki |.
4) Wasserstein distance (dW ) to capture distributionlevel differences: dW (x, ck ) = EU ∼U (0,1) [|Fx−1 (U ) −
Fc−1
(U )|].
k
2) Metric Space Integration: Each distance metric undergoes z-score normalization with clipping to ensure comparable
scales:


dm (x) − µm
dˆm (x) = clip
, −γ, γ ,
max(σm , )
where  prevents division by zero and γ controls the clipping
range. Without normalization, the raw metric with the largest
magnitude (typically Wasserstein, which scales O(102 − 103 )
compared to Cosine’s [0,2] range) would dominate gradient
contributions during backpropagation, effectively collapsing
the multi-space fusion to single-metric behavior.
The integration follows a constrained weighting scheme:
X
D(x, ck ) =
wm · dˆm (x, ck )

The episode construction process begins with initial dataset
sampling to ensure class representation:
(Xtrain , Ytrain ) = stratified sample(D, nsamples ).
Episodes E = {(Si , Qi )}N
i=1 are then constructed, where
each episode contains support and query sets of fixed sizes:
|Sk | = Ns and |Qk | = Nq , ∀k ∈ {1, . . . , C}.
To address the inherent class imbalance in attack detection,
we employ an adaptive sampling mechanism. For each class
k with insufficient samples, we utilize controlled repetition
sampling:
Sk = sample(Dk × d(Ns + Nq )/|Dk |e, Ns + Nq ).
If a class has at least Ns + Nq distinct samples, we sample
support/query without replacement and ensure Sk ∩ Qk = ∅.
For low-count classes, we use controlled repetition and avoid
overlap whenever possible; overlap may occur only when
unavoidable.
For a query sample x, we use the negative fused distances
as logits `k (x) = −D(x, ck ),
k ∈ {1, . . ., C}. The
class posterior is computed with a softmax as pθ (y = k |
k (x))
x) = PCexp(`
. We then optimize the multi-class crossj=1 exp(`j (x))
entropy over the query set Q:
X
L=−
log pθ (y | x)
(x,y)∈Q

=−

m∈M

C
X X

yk log pθ (y = k | x),

(2)

(x,y)∈Q k=1

subject to:
X

wm = 1,

wm ≥ 0

∀m ∈ M.

m∈M

D. Model Stabilization Through Polyak Averaging
We tested Polyak averaging at the model level to improve
stability and convergence in our few-sample setting. Rather
than averaging prototypes directly, we maintain an exponential
moving average (EMA) of the entire model parameters θ,
which implicitly stabilizes the prototype generation process
through a more robust embedding function fθ .
For model parameters at training iteration t, the EMA
parameters are updated as:
(t)

(t−1)

θEMA = βθEMA + (1 − β)θ(t) ,
where β controls the temporal decay of previous parameter
values. This averaging provides three key benefits in our fewshot context: (1) stabilization of the embedding function fθ
across episodes, reducing variance in prototype computation,
(2) implicit ensembling of models along the optimization
trajectory, and (3) smoothing of the optimization landscape
to avoid sharp minima that often lead to poor generalization.
The class prototypes ck are then computed
using the EMA
P
model during inference as ck = |S1k | (xi ,yi )∈Sk fθEMA (xi ).
E. Episodic Learning Framework
Our framework implements episodic training through stratified sampling to handle class imbalance in network attacks.

At inference, MSPL predicts ŷ(x) = arg maxk pθ (y = k |
x) (equivalently, arg mink D(x, ck )); thus, no thresholding is
used in the multi-class setting.
F. Training Procedure
The training process follows Algorithm 1, which implements our MSPL framework. The algorithm alternates between
episode-based training and validation phases, maintaining
model stability through gradient clipping and early stopping
mechanisms.
For each training iteration, the process:
1) Computes embeddings for support and query sets
through fθ .
2) Generates class prototypes from support set embeddings.
3) Calculates and normalizes distances across all metric
spaces.
4) Updates model parameters through gradient descent with
clipping.
When Polyak averaging is enabled, θEMA is updated after
each training parameter update, and only θEMA (not θ) is used
for validation/model selection and inference.
V. T HEORETICAL G UARANTEES AND M ODEL P ROPERTIES
Our framework operates on a collection of metric spaces
M, where each metric m ∈ M satisfies the fundamental properties of non-negativity (dm (x, y) ≥ 0), symmetry
(dm (x, y) = dm (y, x)), and triangle inequality (dm (x, z) ≤
dm (x, y) + dm (y, z)). To ensure comparable scales across

MARTINEZ-LOPEZ et al.: LEARNING IN MULTIPLE SPACES: PROTOTYPICAL FSL WITH METRIC FUSION

Algorithm 1 MSPL Training and Inference via Episodic MetaLearning, Combining Normalized Multi-Metric Distances,
Weighted Fusion, and Polyak (EMA) Averaging.
Input: Input: Dataset D, episodes Ne , ways Nway , support
size Ns , query size Nq , metric weights {wm }m∈M ,
Polyak decay β
Output: Best model parameters θ∗
1: Initialize model parameters θ randomly
2: (Xtrain , Ytrain ) ← sample(D)
3: if using Polyak averaging then
4:
Initialize θEMA ← θ
5: end if
6: E ← CreateEpisodes(Xtrain , Ytrain , Ne , Nway , Ns , Nq )
7: . Per episode: sample Nway classes; draw Ns support and
Nq query per class.
8: . If |Ik | ≥ Ns +Nq : sample w/o replacement so Sk ∩Qk =
∅; else use controlled repetition (avoid overlap if possible).
9: for epoch = 1 to E do
10:
for each (S, Q) ∈ E do
11:
Zs ← fθ (S)
12:
Zq ← fθ (Q)
13:
{ck } ← ComputePrototypes(Zs )
14:
for each metric m ∈ M do
15:
dm ← ComputeDistance(Zq , {ck }, m)
16:
dˆm ← NormalizeDistance(dm )
17:
end for
P
18:
D ← m∈M wm · dˆm
19:
L ← ComputeLoss(D, Q)
20:
Clip gradients and update θ using ∇θ L
21:
if using Polyak averaging then
22:
θEMA ← βθEMA + (1 − β)θ
23:
end if
24:
end for
25:
Validate model and save if improved
26: end for
27: return θ ∗

different metrics, each distance undergoes z-score normalization with clipping, transforming raw distances into normalized
metrics dˆm . The weighted combination
of these normalized
P
ˆ
metrics, defined
as
D(x,
y)
=
m∈M wm dm (x, y) under
P
the constraint
m∈M wm = 1, wm ≥ 0, preserves metric
properties while enabling flexible contributions from each
space. This preservation is demonstrated through the triangle
inequality:
X
D(x, z) =
wm dˆm (x, z)
m∈M

≤

X

wm (dˆm (x, y) + dˆm (y, z))

m∈M

= D(x, y) + D(y, z)
A. Convergence and Stability
The convergence properties of our framework are established under three key conditions: Lipschitz continuity of each
normalized metric dˆm with constant Lm , β-smoothness of the
combined loss, and bounded gradients k∇θ Lk ≤ G. Given

3161

these conditions and our episodic training procedure with
Polyak averaging, the expected error convergence is bounded
by the following:
E[kθ(T ) − θ∗ k2 ]


1 kθ(0) − θ∗ k2
ηG2
+
·
≤
T
η
2

!
X

wm Lm

m∈M

This bound accounts for the contribution of each metric
space through their respective weights and Lipschitz constants.

B. Space Complementarity
The effectiveness of our multi-space approach derives from
the fundamental properties of metric space interactions and
their collective contribution to learning discriminative representations.
1) Metric Space Interaction Properties: For any pair of
metrics m1 , m2 ∈ M, their interaction is characterized by:
Property 1 (Metric Complementarity): For any two metrics
m1 , m2 ∈ M, there exists a subset of points Xm1 ,m2 ⊂ X
where:
|dˆm (x, y) − dˆm (x, y)| ≥ m ,m
1

2

1

2

for some m1 ,m2 > 0, ensuring each metric contributes unique
discriminative information.
This means that there are pairs of samples for which
different metrics disagree by a nontrivial margin, so each
metric can highlight distinctions that another metric may miss.
Property 2 (Multi-Metric Coverage): For any embedding
fθ (x), the combined metric space ensures comprehensive
coverage:
max dˆm (x, y) ≥ λ · dtrue (x, y),
m∈M

where dtrue represents the true underlying distance and λ > 0.
In practice, at least one metric in the set provides a
sufficiently strong separation that scales with the underlying
notion of dissimilarity, preventing uniformly weak distances
across all metrics.
2) Extensibility Theorem: The framework maintains its
theoretical guarantees when extended with additional metrics
that satisfy:
∀mnew ∈ Mext : ∃αm > 0s.t. dmnew (x, y) ≥ αm kx − yk
In the context of attack detection, metric complementarity
provides:
1) Attack Pattern Coverage: For attack class c and normal
traffic n:
∃m ∈ M : P(dˆm (x, cc ) < dˆm (x, cn )|y = c) ≥ 1 − δm
2) Multi-Faceted Attack Characterization:
characterization(x) = [dˆE (x), dˆCh (x), dˆC (x), dˆW (x)]
capturing different aspects of attack patterns.

3162

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 1. Comparison of MSPL framework variants using different metric combinations (euclidean, chebyshev, cosine, and wasserstein) across three benchmark
intrusion detection datasets. The results highlight the impact of metric fusion on detection accuracy, F1-score, and AUPRC, demonstrating the advantages of
multi-space integration over single-metric baselines.

C. Multi-Space Optimization Properties
The optimization process in our framework maintains several key properties that ensure effective learning:
1) Distance Normalization Stability: For any metric m ∈
M, the normalized distance satisfies:
kdˆm (x, y)k∞ ≤ γ,
where γ is the clipping threshold, ensuring bounded gradients
during optimization.
2) Prototype Convergence: Given the bounded embeddings
from fθ and z-score normalized distances, the prototype convergence in expectation follows:
(t)

E[kck − c∗k k2 ] ≤ p

1
|Sk |

· σk ,

where σk represents the intra-class variance and |Sk | is the
support set size for class k.
D. Computational Complexity
The computational complexity of our framework for each
episode is O(Ns Nq |M|). This includes:
• Support set embedding computation:O(Ns )
• Query set distance calculations:O(Nq )
• Multi-space metric computations:O(|M|)
The memory complexity is bounded by O(Ns + Nq +
|M|C), where C is the number of classes.
VI. E VALUATION
This section comprehensively evaluates the proposed MSPL
framework, demonstrating its efficacy in few-shot network
intrusion detection.
The experiments employed three benchmark datasets with
distinct contexts to assess performance under varied traffic
scenarios: CICEVSE2024 [16] (EV charging-station network

traffic/attacks), CICIDS2017 [17] (traditional enterprise network traffic with common attacks), and CICIoV2024 [18]
(in-vehicle IoV CAN-bus traffic/attacks). To rigorously evaluate the FSL capabilities, we restricted the training to only
200 instances. This constrained setting mirrors real-world
scenarios where labeled attack data is scarce. The evaluation
emphasizes three key metrics, balanced accuracy, validation
F1-score, and area under the precision-recall curve (AUPRC),
providing insights into the framework’s ability to generalize, detect rare attack types, and maintain high classification
performance across imbalanced datasets. For AUPRC in the
multi-class setting, we compute one-vs-rest precision-recall
per class using the softmax score pθ (y = k | x) and report the
macro-average across classes.
A. Performance Analysis
1) Cicevse Datasets: On the CICEVSE Network2024
dataset, the baseline approach achieved a balanced accuracy of
0.7210, with a validation F1-score of 0.4194 and an AUPRC
of 0.3719 (Table I, Baseline results, and Fig. 1). The MSPL
framework significantly improved these metrics, increasing the
balanced accuracy to 0.8200, raising the validation F1-score to
0.8502, and elevating the AUPRC to 0.7324 (Table I, MSPL
results). Integrating tri-metric spaces, Euclidean, Chebyshev,
and Cosine, provided complementary perspectives on intrusion
patterns, contributing to substantial performance gains.
Each experiment was conducted over 40 random seeds.
Results are reported as the mean ± 95% confidence interval
(CI). The CIs are based on the Student’s t-distribution with
39 degrees of freedom (N = 40), that is, x̄ ± t0.975,39 · √s40 ,
where x̄ and s denote the sample mean and the sample
standard deviation, respectively.
2) CICIDS2017 Dataset: For the CICIDS2017 dataset, the
baseline (Regular Prototypical without Polyak) achieved a
balanced accuracy of 0.8585, a validation F1-score of 0.6327,

MARTINEZ-LOPEZ et al.: LEARNING IN MULTIPLE SPACES: PROTOTYPICAL FSL WITH METRIC FUSION

3163

TABLE I
FSL ATTACK D ETECTION P ERFORMANCE C OMPARISON U NDER FSL (200 S AMPLES , 40 SEEDS ). B EST R ESULTS P ER DATASET A RE BOLDED . S HADED
ROWS I NDICATE O UR MSPL F RAMEWORK

and an AUPRC of 0.4319 (Table I). The MSPL framework
improved these results by attaining a balanced accuracy of
0.8806, F1-score of 0.6731, and AUPRC of 0.4799. The use
of a tri-metric approach, combining Euclidean, Wasserstein,
and Cosine metrics, enabled better generalization across attack
types, resulting in robust and consistent improvements. This
improvement indicates higher sensitivity under CICIDS2017’s
long-tailed class distribution, i.e., fewer missed detections for
low-support attack categories in the few-shot regime.
3) CICIoV2024 Dataset: The CICIoV2024 dataset exhibited strong baseline results with a balanced accuracy of 0.8804,
F1-score of 0.7321, and AUPRC of 0.5881 (Regular Prototypical without Polyak). The MSPL approach delivered further
improvements, with balanced accuracy of 0.8875, F1-score
of 0.7540, and AUPRC of 0.6144. The use of a bi-metric
space combining Chebyshev and Cosine metrics demonstrated
adaptability, particularly in addressing class imbalance and
subtle attack signatures.
4) Non-DL Baseline:
Besides deep-learning-based
approaches, we experimented with traditional machine learning models. Table I shows that for CICEVSE-Network2024,
performance was relatively low (Balanced Accuracy:
0.7210, F1: 0.4194, AUPRC: 0.3719), and similarly for
CICEVSE-PowerB2024 (Balanced Accuracy: 0.7329, F1:
0.5420, AUPRC: 0.4187) and CICIDS2017 (Balanced
Accuracy: 0.7229, F1: 0.4147, AUPRC: 0.3669). In contrast,
performance was highest in CICIoV2024 (Balanced Accuracy:
0.8955, F1: 0.8274, AUPRC: 0.7615). These results indicate
that traditional approaches struggled with more complex or
imbalanced datasets, while performing reasonably well on
simpler ones. This gap is likely due to the higher heterogeneity
and imbalance of EV-charging traffic in CICEVSE under
few-shot supervision, whereas CICIoV2024 traces are more

structured/regular, yielding more separable attack patterns for
feature-based classifiers.
B. Polyak Averaging Effectiveness
The effectiveness of Polyak averaging was evaluated
across the datasets, revealing dataset-specific impacts. For
the CICEVSE datasets, Polyak averaging introduced minimal
variations, with performance metrics remaining stable (Table I,
Polyak rows). In the case of CICIoV2024, it contributed to
marginal stabilization in validation metrics, reflecting modest
gains in reliability. The CICEVSE dataset exhibited the most
significant benefits from Polyak averaging, with noticeable
stabilization and smoothing effects (Table I, Polyak rows),
highlighting its utility in high-performing environments.
C. Metric Space Contribution
The transition from a single-metric Euclidean baseline to
a multi-space approach underlines the importance of metric
complementarity. On the CICEVSE Network2024 dataset, the
tri-metric approach enhanced pattern recognition by leveraging distinct geometric and directional properties (Table I,
Metric Space column). For CICIDS2017, the tri-metric configuration (Euclidean, Wasserstein, Cosine) yielded consistent
gains across the reported metrics (Table I), including AUPRC
(0.4799 vs. 0.4319) and balanced accuracy (0.8806 vs.
0.8585). For CICIoV2024, the bi-metric configuration (Chebyshev, Cosine) achieved the best MSPL results on that dataset,
improving AUPRC from 0.5881 to 0.6144 and balanced accuracy from 0.8804 to 0.8875, indicating that the optimal metric
combination can be dataset dependent.
D. Key Observations and Discussions
1) Generalizability: The MSPL framework demonstrated
robust generalization capabilities in all datasets: CICEVSE

3164

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 23, 2026

Fig. 2. Imbalanced few-shot conditions. (left) mean precision-recall curve over four datasets show stable performance, with relatively high AUPRC on
CICEVSE network (0.78) and CICIoV (0.63). (Center) row-normalized confusion matrix on CICEVSE network data set shows significant diagonal, validating
that it can still distinguish the different types of attacks, even with few training samples. (Right) Per-class AP, sorted by test set class frequency (rare →
frequent).

Network2024, CICIDS2017, and CICIoV2024. For
CICIDS2017, balanced accuracy improved from 0.8585
to 0.8806 and AUPRC from 0.4319 to 0.4799. For CICEVSE
Network2024, balanced accuracy rose from 0.7210 to 0.8200
and AUPRC from 0.3719 to 0.7324. Even on the highperforming CICIoV2024 dataset, MSPL achieved further
gains from 0.8804 to 0.8875 in balanced accuracy and 0.5881
to 0.6144 in AUPRC. These improvements validate the
framework’s ability to generalize across heterogeneous traffic
profiles.
2) FSL Adaptation: The MSPL framework excelled in
limited-sample environments, particularly on datasets with low
baseline performance. In CICEVSE Network2024, AUPRC
improved from 0.3719 to 0.7324, and validation F1-score
increased from 0.4194 to 0.8502. These improvements highlight the power of episodic training and multi-metric fusion
in learning from sparse data and enhancing adaptation to rare
attacks.
3) Metric Space Complementarity: Integrating multiple distance metrics enhanced detection accuracy. In CICIDS2017, a
tri-metric design (Euclidean, Wasserstein, Cosine) improved
AUPRC (0.4799 vs. 0.4319). In CICIoV2024, a bi-metric
approach (Chebyshev, Cosine) raised AUPRC from 0.5881
to 0.6144. In CICEVSE Network2024, a tri-metric space
(Euclidean, Chebyshev, Cosine) boosted all metrics. These
results show that diverse metrics capture distinct intrusion
behaviors, enabling MSPL to model threats more effectively.
4) Per-Dataset Interpretation: The strongest practical
impact is observed on CICEVSE (EV-charging), where the
large AUPRC/F1 gains suggest MSPL substantially improves
the precision-recall tradeoff under severe class imbalance,
enabling more reliable detection of rare attacks in the few-shot
regime. On CICIDS2017 (enterprise traffic), improvements are
smaller but consistent, indicating MSPL primarily enhances
robustness across diverse attack types when baseline separability is already high. On CICIoV2024 (in-vehicle CAN bus),
the baseline performance is strong and MSPL yields modest
additional gains, implying better capture of subtle CAN-bus
attack signatures without requiring additional labeled data.
5) Online SDN/NFV Integration: MSPL can run online by
embedding each record x as z = fθEMA (x) and scoring fused
prototype distances D(z, ck ) to output a class/confidence,

which an SDN/NFV controller can map to actions (drop/deny,
throttling, rerouting/steering, or SFC updates). End-to-end
delay can be expressed as Ldec = Lfeat + Linfer + Lctrl
(controller-dependent); closed-loop latency/throughput benchmarking with a specific controller is left for future work.

E. Class-Imbalance Resilience
Figure 2 provides more detailed performance breakdown
under our strict few-shot settings. PR curves (left) show
strong detection performance across all the datasets we have
benchmarked, with AUPRC up to 0.78 on CICEVSE Network.
Importantly, the class-wise evaluation on this dataset shows
that MSPL can learn distinguishable signatures for minority
classes (e.g. slowloris, AP 0.45) in the presence of high
data imbalance. The heavy diagonal in the confusion matrix
(center) indicates that most attack types are predicted with low
error rates, while the lower benign class performance is more
likely due to its extreme sparsity (<0.01%) on this attackheavy dataset rather than model breakdown.
VII. C ONCLUSION
We proposed Multi-Space Prototypical Learning (MSPL)
for few-shot attack detection, targeting emerging and rare
intrusions under limited labeled data. By integrating complementary metric spaces (Euclidean, Cosine, Chebyshev, and
Wasserstein), MSPL captures diverse geometric and distributional cues, while Polyak-averaged prototype generation
improves stability and episodic training promotes balanced
adaptation across classes and datasets. Experiments show
consistent gains in balanced accuracy and AUPRC over strong
baselines, and our analyses confirm the benefits of metric
complementarity and scalability across diverse intrusion scenarios. From a deployment standpoint, MSPL is lightweight
and episodic, making it practical to integrate into SDN/NFVbased security controllers for near real-time detection and
response. Future extensions will explore multimodal network
data (e.g., flows, logs, and host telemetry) and real-time
integration with SDN/NFV platforms for online adaptation and
intrusion prevention.

MARTINEZ-LOPEZ et al.: LEARNING IN MULTIPLE SPACES: PROTOTYPICAL FSL WITH METRIC FUSION

R EFERENCES
[1]

M. Al-Zewairi, S. Almajali, M. Ayyash, M. Rahouti, F. Martinez, and
N. Quadar, “Multi-stage enhanced zero trust intrusion detection system
for unknown attack detection in Internet of Things and traditional
networks,” ACM Trans. Privacy Secur., vol. 28, no. 3, pp. 1–28, Aug.
2025.
[2] Y. Guo, “A review of machine learning-based zero-day attack detection: Challenges and future directions,” Comput. Commun., vol. 198,
pp. 175–185, Jan. 2023.
[3] W. Wei, H. Gu, W. Deng, Z. Xiao, and X. Ren, “ABL-TC: A lightweight
design for network traffic classification empowered by deep learning,”
Neurocomputing, vol. 489, pp. 333–344, Jun. 2022.
[4] E. Owusu et al., “Online network DoS/DDoS detection: Sampling,
change point detection, and machine learning methods,” IEEE Commun.
Surveys Tuts., vol. 27, no. 4, pp. 2543–2580, Aug. 2025.
[5] Y. Wang, Q. Yao, J. T. Kwok, and L. M. Ni, “Generalizing from a few
examples: A survey on few-shot learning,” ACM Comput. Surv., vol. 53,
no. 3, pp. 1–34, May 2021.
[6] R. Duan, D. Li, Q. Tong, T. Yang, X. Liu, and X. Liu, “A survey of
few-shot learning: An effective method for intrusion detection,” Secur.
Commun. Netw., vol. 2021, pp. 1–10, Oct. 2021.
[7] M. Fahad Malik, A. Gul, A. Saadia, and F. M. Alserhani, “Few-shot
learning with prototypical networks for improved memory forensics,”
IEEE Access, vol. 13, pp. 79397–79409, 2025.
[8] Y. Yu and N. Bian, “An intrusion detection method using few-shot
learning,” IEEE Access, vol. 8, pp. 49730–49740, 2020.
[9] J. Yang, H. Li, S. Shao, F. Zou, and Y. Wu, “FS-IDS: A framework
for intrusion detection based on few-shot learning,” Comput. Secur.,
vol. 122, Nov. 2022, Art. no. 102899.
[10] W. Ma, L. Ma, K. Li, and J. Guo, “Few-shot IoT attack detection based
on SSDSAE and adaptive loss weighted meta residual network,” Inf.
Fusion, vol. 98, Oct. 2023, Art. no. 101853.
[11] W. Liang, Y. Hu, X. Zhou, Y. Pan, and K. I. Wang, “Variational
few-shot learning for microservice-oriented intrusion detection in distributed industrial IoT,” IEEE Trans. Ind. Informat., vol. 18, no. 8,
pp. 5087–5095, Aug. 2022.
[12] X. Zhou, W. Liang, S. Shimizu, J. Ma, and Q. Jin, “Siamese neural
network based few-shot learning for anomaly detection in industrial
cyber-physical systems,” IEEE Trans. Ind. Informat., vol. 17, no. 8,
pp. 5790–5798, Aug. 2021.
[13] Y. Tian, N. Zheng, X. Chen, and L. Gao, “Wasserstein metric-based
location spoofing attack detection in WiFi positioning systems,” Secur.
Commun. Netw., vol. 2021, pp. 1–12, Apr. 2021.
[14] G. Vijayakanthi, J. P. Mohanty, A. K. Swain, and K. Mahapatra,
“Differential metric based deep learning methodology for non-profiled
side channel analysis,” in Proc. IEEE Int. Symp. Smart Electron. Syst.
(iSES), Dec. 2021, pp. 200–203.
[15] F. Martinez et al., “Redefining DDoS attack detection using a dual-space
prototypical network-based approach,” in Proc. 33rd Int. Conf. Comput.
Commun. Netw. (ICCCN), Jul. 2024, pp. 1–9.
[16] E. D. Buedi, A. A. Ghorbani, S. Dadkhah, and R. Ferreira, “Enhancing
EV charging station security using a multi-dimensional dataset:
Cicevse2024,” in Proc. ESORICS Conf., 2024, pp. 171–190.
[17] I. Sharafaldin, A. Habibi Lashkari, and A. A. Ghorbani, “Toward
generating a new intrusion detection dataset and intrusion traffic
characterization,” in Proc. 4th Int. Conf. Inf. Syst. Secur. Privacy,
Portugal, Jan. 2018, pp. 108–116.
[18] E. C. P. Neto et al., “CICIoV2024: Advancing realistic IDS approaches
against DoS and spoofing attack in IoV CAN bus,” Internet Things,
vol. 26, Jul. 2024, Art. no. 101209.
[19] A. Demirpolat, A. K. Sarica, and P. Angin, “ProtÉdge: A few-shot
ensemble learning approach to software-defined networking-assisted
edge security,” Trans. Emerg. Telecommun. Technol., vol. 32, no. 6,
p. 4138, Jun. 2021.

3165

[20] A. Parnami and M. Lee, “Learning from few examples: A summary of
approaches to few-shot learning,” 2022, arXiv:2203.04291.
[21] M. M. U. Chowdhury, F. Hammond, G. Konowicz, C. Xin, H. Wu,
and J. Li, “A few-shot deep learning approach for improved intrusion
detection,” in Proc. IEEE 8th Annu. Ubiquitous Comput., Electron.
Mobile Commun. Conf. (UEMCON), Oct. 2017, pp. 456–462.
[22] A. S. Iliyasu, U. A. Abdurrahman, and L. Zheng, “Few-shot network intrusion detection using discriminative representation learning
with supervised autoencoder,” Appl. Sci., vol. 12, no. 5, p. 2351,
Feb. 2022.
[23] U. Aharon, R. Marbel, R. Dubin, A. Dvir, and C. Hajaj, “Few-shot API
attack detection: Overcoming data scarcity with GAN-inspired learning,”
2024, arXiv:2405.11258.
[24] U. Aharon, R. Dubin, A. Dvir, and C. Hajaj, “Few-shot API attack
anomaly detection in a classification-by-retrieval framework,” 2024,
arXiv:2405.11247.
[25] Y. Ouyang, B. Li, Q. Kong, H. Song, and T. Li, “FS-IDS: A novel fewshot learning based intrusion detection system for SCADA networks,”
in Proc. IEEE Int. Conf. Commun., Jun. 2021, pp. 1–6.
[26] C. Lu, X. Wang, A. Yang, Y. Liu, and Z. Dong, “A few-shotbased model-agnostic meta-learning for intrusion detection in security
of Internet of Things,” IEEE Internet Things J., vol. 10, no. 24,
pp. 21309–21321, Dec. 2023.
[27] L. Du, Z. Gu, Y. Wang, L. Wang, and Y. Jia, “A few-shot classincremental learning method for network intrusion detection,” IEEE
Trans. Netw. Service Manage., vol. 21, no. 2, pp. 2389–2401, Apr. 2024.
[28] H. Sun et al., “Space decoupled prototype learning for few-shot attack
detection in cyber–physical systems,” IEEE Trans. Ind. Informat.,
vol. 20, no. 10, pp. 12350–12362, Oct. 2024.
[29] T. Bilot, N. El Madhoun, K. Al Agha, and A. Zouaoui, “Few edges are
enough: Few-shot network attack detection with graph neural networks,”
in Proc. Int. Workshop Secur., 2024, pp. 257–276.
[30] H. Pan, Y. Fang, W. Guo, Y. Xu, and C. Wang, “Few-shot graph
classification on cross-site scripting attacks detection,” Comput. Secur.,
vol. 140, May 2024, Art. no. 103749.
[31] C. Xu, J. Shen, and X. Du, “A method of few-shot network intrusion
detection based on meta-learning framework,” IEEE Trans. Inf. Forensics Security, vol. 15, pp. 3540–3552, 2020.
[32] G. Miao, G. Wu, Z. Zhang, Y. Tong, and B. Lu, “SPN: A
method of few-shot traffic classification with out-of-distribution detection based on Siamese prototypical network,” IEEE Access, vol. 11,
pp. 114403–114414, 2023.
[33] M. He, X. Wang, J. Zhou, Y. Xi, L. Jin, and X. Wang, “Deep-featurebased autoencoder network for few-shot malicious traffic detection,”
Secur. Commun. Netw., vol. 2021, pp. 1–13, Mar. 2021.
[34] C. Rong, G. Gou, C. Hou, Z. Li, G. Xiong, and L. Guo, “UMVD-FSL:
Unseen malware variants detection using few-shot learning,” in Proc.
Int. Joint Conf. Neural Netw. (IJCNN), Jul. 2021, pp. 1–8.
[35] R. Kale and V. L. L. Thing, “Few-shot weakly-supervised cybersecurity anomaly detection,” Comput. Secur., vol. 130, Jul. 2023, Art. no.
103194.
[36] J. He et al., “Model-agnostic generation-enhanced technology for fewshot intrusion detection,” Appl. Intell., vol. 54, no. 4, pp. 3181–3204,
Feb. 2024.
[37] T. T. Thein, Y. Shiraishi, and M. Morii, “Few-shot learningbased malicious IoT traffic detection with prototypical graph neural
networks,” IEICE Trans. Inf. Syst., vol. 106, no. 9, pp. 1480–1489,
2023.
[38] Y. Qin et al., “Learning meta model for zero-and few-shot face antispoofing,” in Proc. Conf. Artif. Intell. (AAAI), 2020, vol. 34, no. 7,
pp. 11916–11923.
[39] C. Liu, B. Li, J. Zhao, Z. Zhen, X. Liu, and Q. Zhang, “FewM-HGCL:
Few-shot malware variants detection via heterogeneous graph contrastive
learning,” IEEE Trans. Dependable Secure Comput., early access, Oct.
25, 2022, doi: 10.1109/TDSC.2022.3216902.
PAPER_TEXT
