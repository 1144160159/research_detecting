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
# [678] Falcon: Federated Incremental Learning Framework for Intrusion Detection in Heterogeneous Consumer-Centric Internet of Things
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
编号：678
题名：Falcon: Federated Incremental Learning Framework for Intrusion Detection in Heterogeneous Consumer-Centric Internet of Things
年份：2026
DOI：10.1109/tce.2026.3690484
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2026.3690484.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、联邦学习、隐私保护与分布式协同
相关性：强相关，分数 11
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\678.txt
- 原始字符数：75417
- 本次发送字符数：75417
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

1

Falcon: Federated Incremental Learning Framework
for Intrusion Detection in Heterogeneous
Consumer-Centric Internet of Things
Pengyi Yang1 , Xinyao Gu1 , Xiao Cai1 , Wenhai He2 , Mianjie Li3 , Bowen Zhao4 , and Cheng Qiao1
1 Cyberspace Institute of Advanced Technology, Guangzhou University
2 School of Information Technology and Engineering, Guangzhou College of Commerce
3 Electronics and Information, Guangdong Polytechnic Normal University
4 Guangzhou Institute of Technology, Xidian University
yangpengyi.sec@gmail.com, guxy@e.gzhu.edu.cn, caixiao327327@163.com,
hewenhai@gcc.edu.cn, mianjieli@gpnu.edu.cn, bwinzhao@gmail.com, mcheng.qiao@gmail.com

Abstract—The growing heterogeneity of consumer-centric IoT
and the continuous evolution of cyber threats are increasingly
rendering traditional intrusion detection systems insufficient.
Such systems suffer from data silos, severe class imbalance,
and limited adaptability to novel attacks. To address these
challenges, we propose Falcon, a federated incremental learning
framework for intrusion detection in heterogeneous consumercentric IoT traffic. Falcon enables collaborative training across
multiple clients and remains effective under non-IID client data
distributions and concept drift. It combines a hybrid databalancing scheme with a CNN–BiLSTM–Attention backbone
for learning rich, class-balanced representations, and a drifttriggered incremental module that integrates KL-based drift
detection with a dual-head classifier, memory replay, and multiteacher distillation to learn emerging attacks without catastrophic
forgetting. Experiments on three benchmark datasets show that
Falcon achieves absolute Precision gains of up to 20.76% over
strong centralized and federated baselines in both binary and
multi-class tasks.
Index Terms—Federated learning, Incremental learning, Intrusion detection, Consumer-centric internet of things, Imbalanced
classification, Knowledge distillation, Memory replay, Distribution drift.

I. I NTRODUCTION
MART wearables and consumer electronics (e.g., smartwatches, AR/VR headsets, home gateways, and healthcare
devices) are increasingly pervasive and continuously interact
with smartphones, residential networks, and cloud services.
Such connectivity enlarges the attack surface and makes intrusion detection essential. Deep learning-based IDS has therefore
become an important solution due to its ability to learn highdimensional traffic representations [1], [2], [3]. However, practical deployment is constrained by privacy requirements that
prevent raw traffic from being centrally aggregated, resulting
in fragmented data silos and limited local coverage [4].
However, practical IDS deployment for consumer devices
is constrained by strict privacy and compliance requirements (e.g., health-related data and fine-grained user-behavior
traces), which typically prohibit raw data from being centrally

S

Corresponding authors: Wenhai He and Cheng Qiao.

aggregated across vendors, service providers, or user domains.
This results in fragmented data silos and limited coverage at
each participant, making it difficult to build globally consistent
detectors under privacy-preserving constraints [4].
Federated learning (FL) provides a promising paradigm for
privacy-preserving collaboration [5]. Participants (e.g., device
cohorts, smartphone proxies, and edge sites) keep raw data
locally and only exchange model updates during collaborative
training. In this manner, statistical knowledge from heterogeneous multi-source device traffic can be aggregated without
directly violating data-sharing restrictions, alleviating siloed
learning and improving generalization of the resulting global
model.
Nevertheless, deploying IDS within an FL pipeline does
not automatically resolve the core learning challenges in
consumer-centric IoT ecosystems. First, local data are typically severely imbalanced: benign synchronization and routine
service traffic dominate, while intrusions are rare, diverse,
and often long-tailed [6]. Such skewed local distributions
can bias federated aggregation toward the majority benign
behavior, causing poor sensitivity to minority intrusions [7].
Second, consumer-centric IoT traffic is high-dimensional, temporally dependent, and structurally complex. A single deep
architecture often struggles to simultaneously capture shortterm burst patterns (e.g., repeated pairing attempts), longrange temporal dependencies (e.g., slow-moving compromise),
and fine-grained anomaly cues. Third, real-world CIoT is
inherently dynamic: shifting user behavior, device mobility,
and the continuous emergence of novel attack variants induce
distribution drift, degrading the effectiveness of static global
models even under privacy-preserving training.
These observations indicate that simply porting a centralized
IDS into an FL setting is insufficient. A practical FL-based IDS
for CIoT should satisfy three requirements: (i) re-balancing
highly skewed local datasets to avoid collapsing into benigndominated decision boundaries, (ii) learning rich and stable
representations that capture both local patterns and long-range
temporal dependencies under heterogeneous clients, and (iii)
enabling incremental adaptation to distribution drift and novel

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

2

intrusions without catastrophic forgetting.
Motivated by these requirements, we propose Falcon—a
Federated incrementAL framework for intrusion deteCtiOn
in heterOgeneous coNsumer-centric IoT. Falcon advances
along three lines: data rebalancing, representation modeling,
and incremental adaptation. In the federated stage, Falcon
jointly employs data-layer rebalancing and Focal Loss to
increase both the effective sampling frequency and gradient
contribution of minority intrusion classes, mitigating benigndominant bias. A hybrid CNN–BiLSTM–Attention backbone is
constructed to capture local patterns, temporal dependencies,
and salient segments in traffic sequences. To handle evolving
environments, a sliding window with KL divergence detects
distribution drift and triggers incremental updates. During
incremental adaptation, Falcon integrates a dual-head classifier, memory replay, and multi-teacher knowledge distillation
to balance stability and plasticity, absorbing new intrusion
behaviors while preserving performance on previously learned
classes. Compared with existing federated intrusion detection
and incremental learning approaches, Falcon introduces several key novelties. First, it provides a unified framework that
jointly addresses class imbalance, representation learning, and
incremental adaptation under heterogeneous IoT environments.
Second, it incorporates a drift-triggered incremental learning
mechanism, enabling the model to dynamically adapt to evolving attack patterns. Third, it integrates multi-teacher knowledge distillation with memory replay, effectively balancing
stability and plasticity during incremental updates. The main
contributions of this work are summarized as follows:
• We propose a federated rebalancing strategy that combines balanced sampling and Focal Loss, jointly reshaping the effective sample distribution and the gradient
contributions of minority classes. This strategy improves
F1-Score by up to 97.96% and Recall by up to 89.32%
over vanilla federated learning on imbalanced intrusion
datasets.
• We design a CNN–BiLSTM–Attention feature extractor to capture local patterns, bidirectional temporal dependencies, and salient segments, enabling more discriminative representations under heterogeneous clients.
Compared to a vanilla LSTM baseline, this architecture
achieves an 88.37% improvement in Accuracy and a
95.80% improvement in F1-Score on severely imbalanced multi-class tasks.
• We develop a drift-triggered incremental adaptation
mechanism that integrates sliding-window KL-based drift
detection with a dual-head classifier, memory replay, and
multi-teacher distillation. This mechanism enables crossdataset incremental learning with up to 90% relative
improvement in adaptation performance while maintaining over 96% knowledge retention on previously learned
classes.
The remainder of this paper is organized as follows.
Section II reviews related work on intrusion detection for
consumer devices, federated IDS, imbalanced learning, and
incremental learning. Section III presents the proposed Falcon
framework, including rebalancing with Focal Loss, the CNN–

BiLSTM–Attention model, KL-based drift detection, and federated incremental learning with multi-teacher distillation and
memory replay. Section IV reports experimental results on
three benchmark datasets, including comparisons with stateof-the-art baselines, cross-dataset incremental learning, and
ablation studies. Section V concludes the paper and discusses
future directions.
II. RELATED WORK
This section reviews representative studies related to intrusion detection in CIoT, with an emphasis on three threads:
(i) deep-learning and federated-learning-based intrusion detection, (ii) imbalanced and long-tailed learning for intrusion
detection, and (iii) incremental learning under evolving threats.
We highlight the limitations of existing works in heterogeneous and dynamic deployments and position our Falcon
framework accordingly.
A. Deep Learning and Federated Learning for Intrusion Detection
Centralized intrusion detection has evolved from signature/statistical approaches to machine learning and deep representation learning. Early signature-based methods can efficiently identify known patterns and remain useful in stable environments. For example, Roughan et al. proposed a statisticalsignature-based scheme for IP traffic classification [8]. However, such approaches rely on relatively fixed signatures or
features and tend to degrade under encrypted traffic, dynamic
ports, or rapidly evolving behaviors.
To reduce reliance on plaintext payloads, traditional machine learning methods extract flow-level statistics and observable side-channel features and train classical classifiers.
Recent work shows that even under TLS 1.3, encrypted
traffic in malware detection settings can be passively characterized using metadata-derived representations (e.g., TLS
record-length and direction patterns) together with protocolaware preprocessing [9]. This enables feature-based classifiers
without decrypting payloads. Although such methods improve
practicality under encryption, they typically require non-trivial
feature engineering and often generalize poorly across domains due to dataset bias and distribution shift.
Deep learning further enables end-to-end representation
learning and has become a dominant paradigm in NIDS/IDS.
Recent advances also leverage pretraining to enhance representation robustness. For instance, Trafficformer adopts a pretrained model for traffic data modeling [10]. In consumerelectronics scenarios, deep IDS models have been explored
for healthcare/IoMT electronics and medical traffic monitoring [11], [12], as well as vehicular electronics (e.g., VANEToriented detection) [13]. Despite their strong detection performance in controlled settings, centralized deep IDS generally
struggles in real deployments due to privacy constraints and
the difficulty of collecting sufficiently labeled and representative data, where labeling itself is a persistent bottleneck [4].
Federated learning (FL) provides a privacy-preserving collaborative training paradigm where network traffic data remain local and only model updates are exchanged. This

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

3

paradigm is particularly relevant for CIoT, where sensitive
user behaviors and privacy-sensitive traffic traces cannot be
easily centralized. Hendaoui et al. proposed FLADEN, a
federated learning framework for anomaly detection in IoT
networks [14]. Olanrewaju-George and Pranggono developed
a federated intrusion detection system for IoT using both
unsupervised and supervised deep learning models [15], while
Beuran et al. introduced FedMSE, a semi-supervised federated
learning approach for IoT network intrusion detection to
further reduce dependence on labeled data [16]. To improve
robustness under non-IID data, Yan et al. studied personalized
FL for IoT intrusion detection [17], and Ding et al. explored
meta-learning-based federated detection for large-scale IoT
settings [18]. Recent works in consumer-electronics contexts
further investigated federated deep IDS for consumer-centric
IoT [19], privacy-preserving designs (e.g., quantum FL) [20],
and SDN-assisted federated hybrid IDS frameworks [21].
However, existing FL-based IDS studies still face three
fundamental gaps in consumer-centric IoT. First, client data are
often severely imbalanced and long-tailed, amplifying the bias
of global aggregation. Second, heterogeneous device behaviors
and dynamic participation intensify representation instability
and distribution drift. Third, many FL-IDS solutions are designed as static training pipelines and lack systematic mechanisms for drift-triggered incremental adaptation. Moreover,
while long-tailed heterogeneous learning has been studied
in consumer electronics (e.g., FedHLC) [22], such advances
are not yet fully integrated into an end-to-end federated IDS
pipeline that simultaneously handles imbalance, rich temporal
representation, and drift-driven incremental updates.
B. Learning with Imbalanced and Long-Tailed Intrusion Data
Class imbalance is ubiquitous in intrusion detection: benign
traffic dominates while attacks are rare, diverse, and often
long-tailed [6]. Imbalance learning approaches are typically
categorized into data-level, algorithm-level, and ensemblelevel methods.
Data-level methods rebalance the training distribution via
over-/under-sampling. Recent synthetic over-sampling methods generate minority-class samples for imbalanced classification by jointly considering minority and majority class distributions [23], and SMOTE-style resampling has been further
tailored to intrusion detection in IoT and sensor networks.
Recent work on WSN intrusion detection integrates SMOTE
with Tomek links (SMOTE-Tomek), which synthesizes minority instances while removing borderline/overlapping samples,
yielding a cleaner and more balanced training set for classical
machine-learning detectors [24]. Recent studies have further
integrated synthetic sample generation with deep representation learning to improve intrusion detection under severe class
imbalance [25]. Despite their effectiveness, oversamplingbased methods may still introduce redundant synthetic samples
and increase the risk of overfitting, while undersampling may
discard informative majority-class samples, both of which can
be detrimental under complex attack mixtures.
Algorithm-level methods improve the learning process to
better emphasize minority classes. Recent optimization-aware

intrusion detection approaches have combined imbalanceaware sampling, feature embedding, and classifier design to
mitigate the adverse effect of skewed data distributions [26].
However, such methods may still be sensitive to optimization
settings and training stability under highly heterogeneous
attack scenarios. More generally, class-imbalance learning in
FL has been recognized as a key challenge, as skewed client
distributions can bias global updates [7]. Recent FL methods explicitly target imbalanced intrusion detection, such as
undersampling-aware learning and aggregation strategies [27],
yet they often do not jointly address representation modeling
and incremental adaptation under drift.
Ensemble methods combine multiple learners to improve robustness under imbalance. Evolutionary and geneticprogramming-based classifiers have also been explored for
imbalanced data classification, including recent distance-based
genetic programming approaches designed specifically for
imbalanced binary settings [28]. For example, boosting-based
IDS systems [29] and recent SMOTE-style imbalance-aware
IDS designs [30] can enhance stability but may incur higher
training cost and be less suitable for dynamic deployment
environments.
Overall, although imbalance mitigation has been widely
studied, existing solutions are often applied as isolated components. In consumer-centric IoT, imbalance learning must
be coupled with strong temporal representation modeling and
drift-aware adaptation to maintain sustained effectiveness.
C. Incremental Intrusion Detection under Evolving Threats
Real-world CIoT evolves rapidly due to shifting user behavior, device mobility, and changing device participation. These
factors induce concept drift and are often accompanied by the
emergence of novel attacks. A common industrial practice is
periodic full retraining using historical repositories [31], but
this is computationally expensive and often impractical due
to high computation/communication costs, privacy constraints,
and limited storage. Moreover, the continuous emergence of
novel attacks has motivated intelligent cybersecurity frameworks for adaptive defense [32].
Incremental learning aims to update models with newly
arriving data (e.g., emerging attack types or shifted traffic
distributions) while preserving previously learned knowledge,
which is essential for intrusion detection under concept drift.
Sun et al. proposed temporal-incremental learning for Android
malware detection to handle evolving families and drift [33],
yet catastrophic forgetting remains a central challenge without principled stability–plasticity control. In traffic modeling, representation advances (e.g., transformer-style multilevel representations) highlight the potential of richer sequence
modeling under evolving behaviors [34]. In federated settings,
incremental IDS pipelines have also been explored [35], but
many studies either lack robust drift triggering or do not
explicitly address long-tail imbalance together with incremental updates. Recent generative few-shot IDS methods further
attempt to mitigate data scarcity during adaptation and improve
trustworthiness via explainability [36], but integrating such
ideas into an FL pipeline still requires careful design to avoid
instability and privacy leakage.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

4

Fig. 1. Overall architecture of the proposed Falcon framework. Clients perform data balancing and feature extraction, train local models, and collaboratively
contribute to the global model through federated aggregation, while a drift detector monitors incoming traffic and triggers incremental learning to adapt to
emerging attacks.

III. M ETHOD
In this section, we present the overall design of Falcon, which consists of four stages: (1) local data balancing
on each client’s network traffic; (2) local training of the
CNN–BiLSTM–Attention model on the balanced data; (3)
sliding-window drift detection for emerging attack patterns;
and (4) incremental global model updating at the central server.
Among these, stages (1)–(2) correspond to the federated local
training process, while stages (3)–(4) represent the incremental
adaptation mechanism. The overall workflow is illustrated in
Fig. 1.
A. Balanced Sampler and Focal Loss Function
To address severe class imbalance, we combine a balanced sampler and Focal Loss to jointly mitigate sample
and gradient imbalance. The sampler increases minority-class
frequency, while Focal Loss emphasizes hard samples. The
overall training procedure is shown in Algorithm 1, and
experimental results demonstrate significant improvements in
minority-class detection.
First, at the sampling level, suppose the dataset contains K
classes, denoted as C = {1, 2, . . . , K}, and each class k has
nk samples. The objective of the oversampling balancer is to
ensure that the number of samples per class in each training
batch remains balanced. Specifically, given a batch size B, the
number of samples drawn from each class k is defined as
B
.
(1)
K
If the number of available samples in a particular class is
insufficient, sampling with replacement is applied to that class
to ensure that the batch composition satisfies:
Bk ≈

K
X
k=1

Bk = B,

and

Bk ≥ 1, ∀k.

(2)

At the optimization level, we adopt the Focal Loss function
instead of the standard cross-entropy loss to further enhance
the model’s learning capability for hard-to-classify minority
samples. For a given sample i belonging to class yi , let
the model’s predicted probability for that class be pt,i . The
traditional cross-entropy loss is defined as:
LCE = − log pt,i .

(3)

The Focal Loss, on the other hand, introduces a classbalancing factor αyi and a focusing parameter γ, defined as:
γ

Lfocal (xi , yi ) = −αyi (1 − pt,i ) log (pt,i ) ,

(4)

where αyi ∈ (0, 1) is the class weight (usually larger for
minority classes), γ ≥ 0 controls the focusing strength, and
pt,i is the model’s predicted probability for the true class of
sample i.
The total batch loss is then computed as:
B

Lbatch =

1 X
Lfocal (xi , yi ).
B i=1

(5)

By jointly applying the balanced sampler and Focal Loss
(as detailed in Algorithm 1), each training iteration ensures
that the model sufficiently learns from minority-class samples
while concentrating optimization on difficult or misclassified
instances. This dual strategy not only alleviates the bias
caused by class imbalance but also mitigates overfitting risks
introduced by oversampling, thereby enhancing the model’s
generalization ability and detection performance in highly
imbalanced network intrusion detection scenarios.
B. Deep Model Integrating CNN-BiLSTM and Attention
Mechanism
To effectively identify evolving and fine-grained attack
behaviors in network traffic, it is crucial to capture both spatial

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

5

Algorithm 1: Balanced Sampler + Focal Loss Training
(BS-FL)
Input: Dataset D = {(xi , yi )}N
i=1 , batch size B, epochs
E, model fθ , optimizer O, Focal Loss params
(α, γ), grad clip c; sampler option: either
BalancedBatchSampler (per-class balanced
mini-batches) or WeightedRandomSampler
(inverse-frequency weights).
Output: Trained parameters θ⋆ .
Build label indices: group sample indices by class to
obtain {Ik }K
k=1 ;
2 if BalancedBatchSampler then
3
Compute per-class quota qk ← ⌊B/K⌋; distribute the
remainder B mod K to the first classes;
4
Initialize
sampler that yields batches with
P
q
=
B (with replacement if a class is scarce);
k k
1

of length T , denoted as
X = [x1 , x2 , . . . , xT ] ,

(6)

where each time-step input xt ∈ RF , and F represents the
feature dimension.
First, in the local feature extraction stage, a one-dimensional
convolutional layer is applied to slide along the temporal
dimension. Suppose there are D convolutional kernels, with
weights
W (k) ∈ RK×F
(7)
and kernel width K. The output of the k-th kernel at position
t is given by:
!
K−1
X (k)
(k)
(k)
ct = σ
Wj · xt+j + b
,
(8)
j=0

6

where σ(·) denotes the activation function and b(k) is the bias
term. After concatenating all kernel outputs, the feature map
sequence is obtained as

8

C = [c1 , c2 , . . . , cT ′ ],

else
// WeightedRandomSampler
nk ← |Ik |; set per-sample weight wi ∝ 1/nyi ;
7
Initialize sampler with weights {wi }N
i=1 to draw B
i.i.d. indices per step;

5

for e ← 1 to E do
10
foreach batch indices B yielded by the sampler do
11
Load mini-batch (XB , yB );
12
z ← fθ (XB ) ;
// logits
/* Focal Loss
*/
13
ℓCE ← CrossEntropy(z, yB ) ; // per-sample
14
pt ← exp(−ℓCE );
15
ℓFocal ← α · (1 − pt )γ · ℓCE ;
16
L ← mean(ℓFocal );
O.zero grad(); backprop L;
17
18
clip grad norm(θ, c) ;
// e.g., c = 2.0
19
O.step();
9

20

(9)

where ct ∈ RD and T ′ = T − K + 1.
Next, the feature map sequence is fed into a bidirectional
LSTM (BiLSTM) layer to model long-range temporal dependencies. For each time step t, the forward LSTM recursively
computes the hidden state:
⃗ht , ⃗ct = LSTMf (xt , ht−1 , ct−1 ),

(10)

and the backward LSTM recursively computes the backward
hidden state:
←
− −
h t, ←
c t = LSTMb (xt , ht+1 , ct+1 ).
(11)
The forward and backward hidden states are concatenated to
obtain the comprehensive output at time t:
h
−(b) i
(f ) ←
ht = ⃗ht ; h t ,
(12)

return θ⋆ ← θ;

and temporal dependencies embedded in packet sequences.
Convolutional neural networks excel at extracting local spatial
patterns, such as statistical and structural features within
packets, but lack the ability to model long-range temporal
relationships. In contrast, bidirectional long short-term memory networks (BiLSTMs) are capable of learning sequential
dependencies and contextual transitions over time, yet they
often treat all temporal features with equal importance. The
attention mechanism further complements these models by
adaptively assigning higher weights to critical traffic features,
thereby enhancing the interpretability and focusing capability of the model. Therefore, combining CNN, BiLSTM,
and attention allows the model to jointly learn hierarchical
representations—spatial features through convolution, temporal dependencies through recurrent connections, and feature
saliency through attention—resulting in a more comprehensive
understanding of dynamic network behaviors, as illustrated in
Fig. 2.
Specifically, the model input is a temporal feature sequence

where ht ∈ R2H and H is the number of hidden units in a
single-direction LSTM.
On this basis, a self-attention mechanism is introduced to
adaptively focus on key time steps. Specifically, each BiLSTM
output ht is linearly transformed into query, key, and value
vectors:
qt = Wq ht ,

kt = Wk ht ,

vt = Wv ht ,

(13)

where Wq , Wk , and Wv are trainable parameter matrices.
The similarity between each query qt and all keys kj is
computed to obtain unnormalized attention scores:
qt⊤ kj
,
stj = √
dk

(14)

where dk is the dimension of the key vector for scaling.
The attention weights are obtained by applying the softmax
function:
exp(stj )
αtj = PT ′
.
(15)
l=1 exp(stl )

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

6

Fig. 2. Pipeline of the proposed CNN-BiLSTM-Attention model for network traffic classification. Raw traffic is converted into multivariate temporal sequences
and fed to a 1D-CNN to extract local patterns, followed by a BiLSTM to capture bidirectional temporal dependencies and a self-attention module to aggregate
salient features before final classification.

Each query’s aggregated representation zt is obtained as a
weighted sum of the value vectors:

Algorithm 2: Sliding-Window Data Drift Detection Based
on KL Divergence
Input: Traffic stream S ordered by time, window size
W , step size s, threshold τ , bin size B.
Output: Drift decisions {Driftt } for each window.

′

zt =

T
X

αtj vj .

(16)

j=1

To obtain a global representation vector of the sequence, all
zt are pooled:
T′
1 X
z= ′
zt .
(17)
T t=1
Finally, the aggregated global feature vector z is fed into a
fully connected layer to output multi-class prediction probabilities:
ŷ = softmax(Wo z + bo ),
(18)
where Wo and bo are the output layer parameters.
Through this architecture, the model first extracts local
short-term features via CNN, captures global temporal dependencies via BiLSTM, and then adaptively integrates information across different time steps via the self-attention mechanism. This significantly enhances the model’s capability to
recognize and classify critical behavioral segments in complex
and imbalanced network traffic scenarios.

Initialize reference window:
Extract the first W samples from S to form Dref ;
3 Extract packet-length and direction sequences (Lref , Dref )
from Dref ;
L
D
4 Build histograms href , href with B bins and apply
L
D
Laplace smoothing to obtain Pref
, Pref
;

1
2

Divergence computation:
P L
PL
;
KLlen ← i Pref,i
log Qref,i
L
6
cur,i
D
P D
P
KLdir ← i Pref,i log Qref,i
D ;
7
cur,i
1
8 KLtot ← 2 KLlen + KLdir ;
5

(Optional) Robustness check:
D
L
D
← 12 (Pref
M L ← 12 (Pref
+ QL
+ QD
cur ), M
cur );
1
L
L
L
L
11 JS ← 2 KL(Pref ∥M ) + KL(Qcur ∥M )


D
D
// backup
+ 12 KL(Pref
∥M D ) + KL(QD
cur ∥M ) ;
divergence
9

10

if KLtot > τ then
Driftt ← True;
14
D
ref ← Dcur ; ; // update reference window
C. Data Drift Detection
L
D
D
15
Pref
, Pref
← QL
cur , Qcur ;
To enable the recognition of novel attacks and support 16 else
incremental learning of network traffic, we introduce a sliding 17
Driftt ← False;
window-based data drift detection mechanism, as described in
Algorithm 2. This mechanism continuously monitors whether
data drift occurs within the current window of network traffic,
providing a foundation for subsequent federated incremental
To quantify changes in the data distribution, we employ the
learning.
Kullback–Leibler (KL) divergence:
Specifically, the system maintains a sliding window conB
X
taining network traffic samples over several time slices. For
P (i)
D
(P
∥
Q)
=
P (i) log
,
(19)
KL
this window, we extract the packet length sequences and
Q(i)
i=1
direction sequences of all flows, concatenate these features into
one-dimensional vectors, and then compute the normalized where P and Q represent the normalized probability distriprobability distributions for each feature type.
butions of the reference window and the current window,
12

13

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

7

Fig. 3. Federated incremental learning with knowledge distillation for new attack adaptation. When novel attacks are detected, each client locally trains on
new traffic and maintains an instance queue Di of representative samples, while the global server aggregates client updates and applies distillation to adapt
the global model without catastrophic forgetting.

respectively. To improve numerical stability, all distributions
are smoothed using Laplace smoothing:
Pi′ =

Pi + ϵ
,
1 + ϵB

Q′i =

Qi + ϵ
.
1 + ϵB

(20)

The KL divergence is computed separately for the packet
length sequences and direction sequences, and their mean is
taken as the overall drift measure:
1
total
′
′
∥ Q′len ) + DKL (Pdir
∥ Q′dir )) . (21)
DKL
= (DKL (Plen
2
The system periodically slides the window forward and
recomputes the feature distributions. When the difference
between the current window’s feature distribution and the
reference distribution exceeds a predefined threshold, a significant data drift is detected, which triggers the incremental
learning process.
D. Federated Incremental Learning
When data drift occurs, the federated incremental learning
mechanism is triggered, as illustrated in Fig. 3. New samples
of traffic classes are collected, and a unified label mapping is
applied. In the model’s output layer, a dual-classification head
structure is adopted: the original classifier handles historical
classes, while an additional classifier handles new classes. The
outputs of both heads are concatenated for unified multi-class
prediction.
To effectively maintain previously acquired knowledge
while continuously learning new attack types, the model
must overcome catastrophic forgetting, a common issue in
incremental learning scenarios. Conventional single-teacher
knowledge distillation mitigates this problem by transferring
soft-label information from the previous model to the current
one, but it struggles to balance old and new knowledge when
data distributions shift significantly. To address this limitation,
we design a multi-teacher knowledge distillation mechanism
that integrates both the historical model and a new-class
teacher model. The new-class teacher is trained independently
on traffic samples identified by the data drift detection
module (Algorithm 2), which continuously monitors recent
network flows and detects emerging attack types that deviate
from previously seen distributions. This strategy enables the

student model to learn jointly from historical knowledge and
newly emerging class semantics, thereby improving adaptability and stability during incremental updates. Furthermore, to
reinforce the retention of previously learned representations,
a memory replay mechanism is incorporated, which periodically reuses a small subset of representative samples from
earlier classes during training. For each batch of samples,
let the outputs of the historical model, the new-class model,
and the student model be denoted by zold , znew , and zs ,
respectively. The knowledge distillation loss is divided into
two parts, corresponding to old-class and new-class data:


Lold = T 2 KL σ(zold /T ) ∥ σ(zs /T ) ,
(22)


Lnew = T 2 KL σ(znew /T ) ∥ σ(zs /T ) ,
(23)
where T is the temperature parameter and σ(·) denotes the
softmax function.
The overall loss function combines cross-entropy supervision with the two knowledge distillation terms:
L = α LCE (zs , y) + β Lold + γ Lnew ,

(24)

where LCE is the standard cross-entropy loss, and α, β, γ are
balancing coefficients. This design ensures that the student
model acquires discriminative capability for new classes while
inheriting knowledge from the historical model and mimicking
the new teacher model’s performance on new classes.
The memory replay mechanism mixes a portion of originalclass samples with new-class samples during training for joint
optimization. Let Dnew and Dold denote the new-class and
original-class sample sets, respectively, and let δ be the replay
ratio. Then the training set can be expressed as:
D = Dnew ∪ replay(Dold , δ).

(25)

In summary, the proposed federated incremental learning
method, combining multi-teacher knowledge distillation and
memory replay, leverages dual distillation supervision from
historical and new-class models. This approach effectively
enhances the model’s adaptability to new classes, mitigates
catastrophic forgetting, and enables incremental multi-class
learning in a federated environment, allowing the model to
continuously recognize new attacks.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

8

TABLE I
DATASET I NFORMATION
Dataset

Label

Class

Training Samples

IR

USTC-TFC2016

0
1
2
3

Benign
Htbot
Nsis-ay
Shifu

309,887
6,341
6,165
9,634

–
48.87
50.26
32.16

CICIDS2017

0
1
2
3

Benign
DDoS
FTP-Patator
SSH-Patator

923,281
14,039
3,973
2,979

–
65.79
232.45
310.01

CICIDS2018

0
1
2
3

Benign
Botnet Ares
Infiltration
Web Attack

296,245
50,946
106,397
19

–
5.82
2.78
15,591.84

Note: “Label” represents the label assigned to each class of data;
“Class” represents the class contained in the dataset; “Training Samples” indicates the number of samples of each class in the training set;
“IR” represents the imbalance ratio with respect to the Benign class.

channels and kernel size 3, a two-layer BiLSTM with hidden
size 64 and dropout 0.2, an attention module with projection
dimension 64, and a classification head (128→32→number of
classes) with ReLU and dropout 0.3.
Baseline and Comparison: For both binary and multiclass classification tasks, the proposed Falcon framework
was compared with five state-of-the-art baseline methods,
including Fed-ANIDS, FELIDS, FL-IIDS, FedUGI, and FeCoGraph [37], [38], [35], [27], [39]. In addition, we compared
the performance of Falcon with TMG-GAN, which was trained
locally without a federated learning framework [40].
Evaluation Metrics: Since the datasets are highly imbalanced, accuracy alone is insufficient. We therefore report
Accuracy, Precision, Recall, and F1-Score. Precision reflects
false-positive control, Recall measures attack detection capability, and F1-Score balances both, making it particularly
suitable for imbalanced intrusion detection.
B. Experimental Results

IV. E XPERIMENTS
In this section, we validate the effectiveness of Falcon
through empirical experiments. First, we provide detailed
experimental settings, including model parameters, evaluation
metrics, and an overview of the datasets. Next, we conduct
a series of experiments on the proposed Falcon framework,
comparing it with several state-of-the-art (SOTA) models and
verifying the effectiveness of incremental learning. Finally,
ablation studies are designed to demonstrate the effectiveness
of each improvement.
A. Experimental Settings
Datasets: Unlike prior works that directly use CSV files,
we extract flow features (e.g., packet-length sequences and
timestamp sequences) from raw PCAP traces based on 5-tuple
aggregation rules. Furthermore, class selection is applied to
the processed datasets. The final experimental datasets include
the following classes: USTC-TFC2016 (Benign, Htbot, Nsisay, Shifu), CICIDS2017 (Benign, DDos, FTP-Patator, SSHPatator), and CICIDS2018 (Benign, Botnet Ares, Infiltration,
Web Attack). Table I summarizes the detailed information of
the datasets used in this paper.
Implementation Details: We implemented Falcon using
PyTorch and Ray. Focal Loss was adopted with α = 1.0 and
γ = 2.0. The number of communication rounds was set to
R = 100. The server used SGD with momentum, an initial
global learning rate of 0.01, and weight decay 1 × 10−4 . Each
client performed E = 5 local epochs with batch size 128
using AdamW (learning rate 0.01, weight decay 1×10−2 ), and
gradient clipping with a maximum norm of 2.0 was applied
for stability.
To simulate heterogeneous federated scenarios, we generated non-IID client partitions using a Dirichlet-based allocation strategy, where smaller αdir indicates stronger heterogeneity. We also allowed different clients to have different sample
volumes to reflect realistic data imbalance across participants.
Both global and local models used a CNN–BiLSTM–
Attention backbone, including 1D convolutional layers with 64

In this section, we present the empirical results of extensive
validation experiments conducted on the USTC-TFC2016, CICIDS2017, and CICIDS2018 datasets, covering binary classification, multi-class classification, robustness evaluation under
client dropout and adversarial attacks, hyperparameter sensitivity analysis, non-IID heterogeneity analysis, incremental
learning, and ablation studies.
Binary Classification Experiments: In the binary setting,
we compare three families of methods: the centralized nonFL detector TMG-GAN, five representative FL-based NIDS
(Fed-ANIDS, FELIDS, FL-IIDS, FedUGI and FeCoGraph),
and the proposed Falcon framework (denoted as “Ours” in the
figures). As shown in Fig. 4, Falcon consistently achieves the
best performance on all three datasets and on all four metrics
(Accuracy, Precision, Recall and F1-Score), with its curves remaining at the very top of each plot. The superior performance
of Falcon can be attributed to its class-rebalancing mechanism.
As defined in Eq. (4), the Focal Loss introduces the modulation
term (1 − pt )γ , which suppresses the contribution of easy
majority-class samples and amplifies the gradients of hard and
minority-class samples. Combined with the balanced sampler
in Eqs. (1)–(2), Falcon effectively reshapes both the sample
distribution and the optimization dynamics. As a result, the
model maintains consistently high Precision, Recall, and F1Score on imbalanced intrusion traffic.
On USTC-TFC2016, TMG-GAN and FedUGI obtain relatively high recalls of 95.03% and 94.89%, respectively, but
their precisions (91.76% and 95.88%) and F1-Scores (93.36%
and 95.36%) are clearly lower than those of Falcon. Falcon
reaches 99.72% Accuracy, 99.70% Precision, 99.70% Recall
and 99.70% F1-Score, forming an almost flat line near 100%
in Fig. 4. A salient observation is Fed-ANIDS: despite its
very high accuracy of 99.64%, its Precision, Recall, and F1Score decline to 49.82%, 50.00%, and 49.91%, respectively,
indicating that it is heavily biased toward the majority class.
In contrast, Falcon maintains both high accuracy and wellbalanced error rates, outperforming all FL-based methods and
even the centralized TMG-GAN.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

9

Fig. 4. Overall binary (top) and multi-class (bottom) classification performance (Accuracy, Precision, Recall, F1-Score) of different methods on CICIDS2017,
CICIDS2018, and USTC-TFC2016.

On CICIDS2017, TMG-GAN serves as a strong centralized
upper bound with 99.63% Accuracy and 99.72% F1-Score.
Falcon still slightly improves upon this baseline, achieving
99.77% Accuracy, 99.67% Precision, 99.85% Recall and
99.79% F1-Score. Other FL baselines suffer from either low
precision or low recall: for example, FELIDS degrades to
about 50% on all three metrics (Precision, Recall and F1Score), and FeCoGraph reaches only 67.42% F1-Score although its accuracy is 96.00%. This behavior is reflected by
the steep declines from the Accuracy point to the Recall and
F1-Score points in Fig. 4, whereas Falcon remains close to the
upper boundary on every metric.
On CICIDS2018, Falcon attains 95.59% Accuracy, 94.37%
Precision, 95.59% Recall and 95.26% F1-Score, preserving a
good balance between Precision and Recall. FedUGI is the
strongest competitor in this case with 93.84% Accuracy and
93.23% F1-Score, while TMG-GAN yields 88.43% F1-Score.
Several baselines again exhibit strong metric imbalance: FedANIDS achieves 91.30% Accuracy but only 78.27% F1-Score,
and FeCoGraph attains 94.52% Accuracy yet only 81.38%
F1-Score. Overall, across the three datasets, Falcon not only
eliminates the performance gap between privacy-preserving
FL and centralized training, but also yields strictly higher F1Scores than TMG-GAN on all datasets.
Multi-class Classification Experiments: We further evaluate all methods in the multi-class setting. The results in Fig. 4
lead to similar conclusions: Falcon again provides the most
stable and superior performance on all datasets, and its curves
exhibit the smallest decline from Accuracy to F1-Score. This
effect becomes more pronounced in the multi-class setting,
where class imbalance is more severe. The combination of
balanced sampling and the loss reweighting mechanism in
Eq. (4) prevents the classifier from being dominated by majority classes, thereby improving the discriminative capability
for minority and long-tailed attack categories. On USTC-

TFC2016, Falcon achieves 99.82% Accuracy, 99.62% Precision, 99.72% Recall and 99.67% F1-Score, clearly surpassing
the centralized TMG-GAN (97.15% Accuracy and 96.23%
F1-Score). In contrast, Fed-ANIDS, FELIDS, FL-IIDS and
FedUGI obtain F1-Scores of 76.01%, 71.81%, 73.74% and
70.56%, respectively, and FeCoGraph reaches 81.77% F1Score. The pronounced declines of their curves from Accuracy to Recall/F1-Score in Fig. 4 show that these FL-based
baselines struggle with the imbalanced multi-class malware
traffic, while Falcon maintains almost perfectly horizontal
performance curves close to 100%.
On CICIDS2017, TMG-GAN again constitutes a strong
non-federated baseline, with 96.73% Accuracy and 93.66%
F1-Score. Falcon attains 99.66% Accuracy and 99.07% Precision, with 91.32% Recall and an F1-Score of 94.90%, thereby
outperforming TMG-GAN on all four metrics. Among the FL
baselines, FeCoGraph is the best, but its F1-Score is only
73.31%, and the remaining FL methods stay below 69%. Thus,
even in the more challenging multi-class scenario, Falcon
substantially narrows and in fact reverses the performance gap
between federated and centralized paradigms.
On CICIDS2018, Falcon maintains robust performance with
95.50% Accuracy, 97.38% Precision, 95.50% Recall and
96.43% F1-Score. By comparison, TMG-GAN attains 81.62%
Accuracy and 75.59% F1-Score, and the strongest FL baseline,
Fed-ANIDS, reaches 78.47% Accuracy and 80.96% F1-Score.
Several FL methods show severe degradation on minority
classes: for instance, FeCoGraph still reports 87.22% Accuracy, but its Precision, Recall and F1-Score decline to 31.63%,
45.22% and 37.22%, respectively, which is visualized as a
sharp decline of its curve in Fig. 4. Falcon, on the other
hand, preserves both high Recall and high Precision across all
classes, resulting in the highest F1-Score among all methods.
In summary, TMG-GAN is included as a strong centralized
NIDS baseline that assumes full access to globally aggregated

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

10

Fig. 5. Robustness evaluation under client dropout scenarios across three datasets (USTC-TFC2016, CICIDS2017, CICIDS2018) under varying dropout rates.

Fig. 6. Robustness evaluation under adversarial attacks across three datasets (USTC-TFC2016, CICIDS2017, CICIDS2018) under FGSM attacks with varying
perturbation magnitudes.

traffic at a single site. This baseline allows us to directly
examine whether a privacy-preserving federated design must
compromise detection performance compared with a centralized NIDS. Across all three datasets and in both binary and
multi-class settings, Falcon consistently achieves higher F1Scores and comparable or better accuracy than this centralized
baseline, while keeping raw traffic data on each client and
exchanging only model updates. These results show that the
proposed federated framework not only outperforms existing
FL-based NIDS, but also surpasses a state-of-the-art centralized NIDS, indicating that competitive or superior intrusiondetection performance can be attained without centralized
training on raw network flows.
Client Dropout Experiments: In real-world federated
learning deployments, client availability is often unstable due
to network interruptions, device failures, or resource constraints. To evaluate the robustness of Falcon under such
conditions, we conduct systematic experiments with client
dropout rates ranging from 0.2 to 0.8, as illustrated in Fig. 5.
On USTC-TFC2016, Falcon demonstrates exceptional stability across all dropout rates, with performance metrics remaining consistently above 99.6%. On CICIDS2017, similar
robustness is observed with only 0.03% degradation from rate
0.2 to 0.8. On CICIDS2018, despite more complex traffic
patterns, performance degradation remains within 0.2% across
all metrics. These results validate that Falcon maintains robust
intrusion detection performance under realistic federated scenarios where client participation is unstable.
Adversarial Attack Experiments: To assess the security robustness of Falcon against adversarial perturbations,
we conduct systematic evaluations using the Fast Gradient
Sign Method (FGSM) with perturbation magnitudes ϵ ∈
{0.01, 0.05, 0.1, 0.2}, as illustrated in Fig. 6.
On USTC-TFC2016, Falcon exhibits strong resilience with
performance metrics remaining above 99.64% even under the

strongest attacks. On CICIDS2017, performance degradation
is less than 0.05% across all perturbation magnitudes. On
CICIDS2018, despite more complex traffic patterns, the maximum degradation remains within 0.2%. These results validate
that Falcon’s architecture provides inherent defense against
gradient-based attacks, maintaining reliable intrusion detection
even when facing adversarially crafted malicious traffic.
Focal Loss Parameter Sensitivity: To validate the robustness of hyperparameter configuration, we conduct sensitivity
analysis on Focal Loss parameters: gamma (γ), alpha (α), and
tau (τ ), as illustrated in Fig. 7.
Across all datasets, the model demonstrates stable performance under varying parameter settings. Performance remains
consistent for gamma values from 0 to 5, alpha values between
0.1 and 0.75, and tau values from 0.01 to 0.2. These results
confirm that Falcon maintains reliable detection performance
across a wide range of hyperparameter configurations.
Non-IID Heterogeneity Analysis: To evaluate Falcon’s
robustness under heterogeneous data distributions, we conduct systematic experiments using Dirichlet-based non-IID
partitioning with varying concentration parameter α ∈
{1, 2, 3, 4, 5}, as illustrated in Fig. 8. Lower α values indicate
stronger statistical heterogeneity across clients.
On USTC-TFC2016, even under severe heterogeneity (α =
1), Falcon maintains over 97.4% performance across all
metrics, with only 2.3% degradation compared to the IID
baseline. As α increases to 5, performance converges to within
0.14% of the IID setting. On CICIDS2017, similar trends are
observed with 2.2% maximum degradation at α = 1 and nearIID performance at α = 5. On CICIDS2018, despite more
complex traffic patterns, Falcon achieves over 90.5% F1-Score
even under α = 1, demonstrating strong resilience to data
heterogeneity. These results validate that Falcon’s federated
rebalancing strategy and robust feature extraction effectively
mitigate the adverse impact of non-IID data distributions in

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

11

Fig. 7. Parameter sensitivity analysis for Focal Loss hyperparameters across three datasets.

Fig. 8. Impact of data heterogeneity on model performance under varying Dirichlet α values. Lower α indicates stronger non-IID conditions. The horizontal
dashed lines represent IID baseline performance. As α increases, performance converges toward the IID baseline, demonstrating Falcon’s robustness under
heterogeneous federated settings.

real-world federated intrusion detection scenarios. From a
theoretical perspective, this robustness can be explained by
the joint optimization design of Falcon. The balanced sampler
ensures a more uniform class distribution within each minibatch as described in Eqs. (1)–(2), while the Focal Loss in
Eq. (4) further increases the contribution of hard samples
during training. As a result, local model updates are less biased
toward client-specific majority classes, leading to improved

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

12

Fig. 9. Experimental results of incremental learning under cross-dataset drift scenarios. The figure illustrates the performance of the proposed framework before
and after incremental learning across different dataset combinations. Each subfigure represents a specific transfer pair, where the ”Original” dataset serves
as the base model training set and the ”New” dataset represents novel traffic introduced after drift. The results include binary and multi-class classification
tasks, evaluated in terms of Accuracy, Precision, Recall, and F1-score. It can be observed that after the incremental update, the model effectively adapts to
new traffic distributions while maintaining stable detection accuracy on previously learned datasets.

global aggregation under heterogeneous data distributions.
Incremental Learning Experiments: As illustrated in
Fig. 9, the model exhibits clear and consistent improvements
after adapting to new datasets across both binary and multiclass classification tasks. When using USTC-TFC2016 as the
original dataset and CICIDS2017 as the new dataset, the binary
classification metrics—Accuracy, Precision, Recall, and F1Score—are initially low before transfer, but all approach or
exceed 0.97 after incremental training, demonstrating strong
adaptability and generalization. Similarly, in the multi-class
task, performance rises dramatically from near-random levels (around 0.49) to approximately 0.97, indicating that the
proposed incremental learning strategy effectively mitigates
catastrophic forgetting. When extended to other dataset combinations, such as those involving CICIDS2018, the model
continues to maintain high Accuracy and Recall, with F1Score consistently within the 0.96–0.98 range, demonstrating
its stability under complex distribution shifts. The effectiveness of the incremental adaptation can be explained by the
KL-based drift detection mechanism. As defined in Eq. (19),
the KL divergence quantifies the discrepancy between the
reference distribution and the current data distribution. Once
the divergence exceeds a predefined threshold, the model
is updated accordingly, enabling Falcon to adapt to newly
emerging attack patterns in a timely manner. Furthermore, the
strong knowledge retention can be explained by the multiteacher distillation framework in Eqs. (22)–(24). By constraining the student model to align with both historical and newclass teacher outputs, and combining this with memory replay,
Falcon effectively balances stability and plasticity, thereby
mitigating catastrophic forgetting during incremental updates.
Furthermore, knowledge retention is evaluated during crossdataset incremental learning, as illustrated in Fig. 10. For
binary classification, retention typically remains around 99%,
and in some cases even exceeds 100%, suggesting that the
model not only preserves but also reinforces previously learned

Fig. 10. Knowledge retention after incremental learning. Retention rates of
binary and multi-class models on previously learned data under different incremental learning orders (2017→2016, 2016→2017, etc.), compared against
an ideal perfect-retention baseline.

knowledge. For multi-class classification, although minor fluctuations are observed, retention remains stable within 96%–
98%, with only slight declines in isolated cases. Overall,
these results confirm that the proposed method achieves robust
and scalable cross-domain incremental learning, effectively
absorbing new knowledge while preserving prior information.
Ablation Study: This section evaluates the contribution
of each module via ablation experiments: we use a vanilla
LSTM as the baseline, our proposed model as the improved
architecture, and then progressively introduce class-imbalance
handling (denoted as Balance). As shown in Table II, the
standalone LSTM is unstable under imbalanced settings—for
example, on USTC-TFC2016 (binary) it yields only 11.35%
Accuracy with an F1-Score of 3.90%; the multi-class results
on CICIDS2018 are likewise low. Adding Balance on top of
the baseline alleviates missed detections and improves Recall
substantially, but often leads to a skewed “high-precision, lowrecall” trade-off, so the overall F1-Score remains limited.
Replacing LSTM with our proposed model, even without Balance, produces markedly more stable decision

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

13

TABLE II
A BLATION R ESULTS ON B INARY AND M ULTI - CLASS C LASSIFICATION

Datasets

Combination

Model

Balance

Ours

USTC-TFC2016

CICIDS2017

CICIDS2018

1
2
3
4
1
2
3
4
1
2
3
4

Binary Metrics

LSTM

ACC

PRE

REC

F1

ACC

PRE

REC

F1

✓
✓

62.96
11.35
63.65
99.72

49.70
3.10
99.99
99.70

98.26
13.30
0.88
99.70

66.03
3.90
1.74
99.70

77.36
36.67
63.43
99.82

44.00
18.33
8.90
99.62

27.00
50.00
9.24
99.72

27.00
26.84
7.34
99.67

✓
✓

97.41
92.02
95.98
99.77

0
28.55
38.73
99.67

0
58.38
80.23
99.85

0
32.57
24.88
99.79

97.57
97.57
89.20
99.66

19.51
0
13.20
99.07

20.00
0
61.90
91.32

19.75
0
21.80
94.90

✓
✓

35.01
34.69
61.50
95.59

34.76
34.69
73.42
94.37

99.68
99.99
70.43
95.59

51.55
51.51
61.21
95.26

65.31
25.33
23.46
95.50

20.00
20.44
21.42
97.38

20.00
20.44
40.00
95.50

20.00
19.42
7.93
96.43

✓
✓
✓

✓
✓

✓
✓

✓
✓

✓
✓

Multi Metrics

✓

boundaries and tangible gains in F1-Score for both binary and multi-class tasks. When our model operates with
Balance, it achieves the global optimum. For example,
on USTC-TFC2016 (binary), Accuracy/Precision/Recall/F1Score reach 99.72/99.70/99.70/99.70; on CICIDS2017 (multiclass), Accuracy is 99.66% with an F1-Score of 94.90%;
and on CICIDS2018 (multi-class), the results further improve
to 95.50% Accuracy and 96.43% F1-Score. These findings
indicate that the vanilla LSTM provides only basic temporal
modeling, Balance mainly recovers Recall, while our model
supplies stable and interpretable discriminative features. No
single component alone can simultaneously optimize Precision
and Recall. Only the complete configuration—our model plus
Balance—consistently delivers the highest and most balanced
metrics across datasets and across both binary and multi-class
tasks, demonstrating that our improvements are both necessary
and complementary. These observations are consistent with the
mathematical design of Falcon. The balanced sampling mechanism modifies the effective training distribution, while the
Focal Loss in Eq. (4) adjusts the gradient contribution across
classes. Meanwhile, the CNN–BiLSTM–Attention architecture
enhances feature representation as defined in Eqs. (8)–(18).
Only the combination of these components leads to consistent
improvements across all evaluation metrics.

ablation study further verifies that each component contributes
substantially to the final performance.
Future Work: Future work will explore three promising
directions to further enhance Falcon’s robustness and applicability. First, we plan to integrate lightweight noise detection mechanisms by combining uncertainty quantification
(e.g., Monte Carlo dropout or ensemble-based confidence
estimation) with client-side data quality scoring, enabling the
server to adaptively down-weight noisy client updates during
aggregation without violating privacy constraints. Second, we
will investigate hard-example mining strategies that leverage
attention-weighted sample selection and curriculum learning
to prioritize challenging minority-class instances during local training, thereby improving the model’s discriminative
capability on rare and evolving attack patterns. Third, we
aim to develop communication-efficient incremental adaptation by exploring gradient compression techniques (e.g.,
top-k sparsification and quantization) combined with selective
model broadcasting, reducing the communication overhead of
frequent incremental updates in resource-constrained CIoT environments. These directions are motivated by recent surveys
highlighting the necessity of lightweight data quality control
and efficient communication for sustaining robustness under
heterogeneous and evolving environments [41].

V. C ONCLUSION

R EFERENCES

This paper proposed Falcon, an imbalance-aware federated
intrusion detection framework for heterogeneous consumercentric IoT. By integrating data balancing, multi-level feature
extraction, and robust federated training, Falcon effectively
addresses privacy constraints, class imbalance, and non-IID
client heterogeneity.
Experiments on three benchmark datasets demonstrate that
Falcon consistently improves F1-Score, Recall, and overall
detection stability over strong baselines, while remaining robust under non-IID data distributions and client dropout. The

[1] V. Kumar, K. Kumar, M. Singh, and N. Kumar, “Nids-da: Detecting
functionally preserved adversarial examples for network intrusion detection system using deep autoencoders,” Expert Systems with Applications,
vol. 270, p. 126513, 2025.
[2] A. Sarıkaya, B. G. Kılıç, and M. Demirci, “Raids: Robust autoencoderbased intrusion detection system model against adversarial attacks,”
Computers & Security, vol. 135, p. 103483, 2023.
[3] B. Sharma, L. Sharma, C. Lal, and S. Roy, “Explainable artificial
intelligence for intrusion detection in iot networks: A deep learning
based approach,” Expert Systems with Applications, vol. 238, p. 121751,
2024.
[4] P. Goldschmidt and D. Chudá, “Network intrusion datasets: A survey,
limitations, and recommendations,” Computers & Security, vol. 156, p.
104510, 2025.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3690484

14

[5] X. Hao, C. Lin, W. Dong, X. Huang, and H. Xiong, “Robust and secure
federated learning against hybrid attacks: A generic architecture,” IEEE
Transactions on Information Forensics and Security, vol. 19, pp. 1576–
1588, 2023.
[6] V. Shanmugam, R. Razavi-Far, and E. Hallaji, “Addressing class imbalance in intrusion detection: a comprehensive evaluation of machine
learning approaches,” Electronics, vol. 14, no. 1, p. 69, 2024.
[7] G. Zhu, X. Liu, J. Niu, Y. Wei, S. Tang, and J. Zhang, “Learning by
imitating the classics: Mitigating class imbalance in federated learning
via simulated centralized learning,” Expert Systems with Applications,
vol. 255, p. 124755, 2024.
[8] M. Roughan, S. Sen, O. Spatscheck, and N. Duffield, “Class-of-service
mapping for qos: a statistical signature-based approach to ip traffic
classification,” in Proceedings of the 4th ACM SIGCOMM conference
on Internet measurement, 2004, pp. 135–148.
[9] D. Barradas, C. Novo, B. Portela, S. Romeiro, and N. Santos, “Extending
c2 traffic detection methodologies: From tls 1.2 to tls 1.3-enabled
malware,” in Proceedings of the 27th International Symposium on
Research in Attacks, Intrusions and Defenses, 2024, pp. 181–196.
[10] G. Zhou, X. Guo, Z. Liu, T. Li, Q. Li, and K. Xu, “Trafficformer: an
efficient pre-trained model for traffic data,” in 2025 IEEE Symposium
on Security and Privacy (SP). IEEE, 2025, pp. 1844–1860.
[11] A. Alferaidi, K. Yadav, Y. Alharbi, E. J. Alreshidi, A. Alreshidi, B. W.
Aboshosha, R. Sharma, A. Alkhayyat, and D. G. Aray, “A novel hybrid,
bert and deep learning model network intrusion detection system for
healthcare electronics,” IEEE Transactions on Consumer Electronics,
vol. 71, no. 1, pp. 1322–1331, 2025.
[12] T. Sun, X. Zhang, X. Wang, Y. Zhuang, and Z. He, “Traffic intrusion
detection of medical consumption electronics in the field of medical
management based on integrated learning,” IEEE Transactions on Consumer Electronics, vol. 70, no. 1, pp. 1334–1341, 2024.
[13] P. Suman, S. Padhy, N. Kumar, A. Suman, A. Singh, K. Kant Singh,
Kuc Castilla, and T. S. S. AL-Zahrani, “An improved deep learningbased intrusion detection for reliable communication in vanet,” IEEE
Transactions on Consumer Electronics, vol. 71, no. 1, pp. 209–217,
2025.
[14] F. Hendaoui, R. Meddeb, L. Trabelsi, A. Ferchichi, and R. Ahmed,
“Fladen: federated learning for anomaly detection in iot networks,”
Computers & Security, vol. 155, p. 104446, 2025.
[15] B. Olanrewaju-George and B. Pranggono, “Federated learning-based
intrusion detection system for the internet of things using unsupervised
and supervised deep learning models,” Cyber Security and Applications,
vol. 3, p. 100068, 2025.
[16] V. T. Nguyen and R. Beuran, “Fedmse: Semi-supervised federated
learning approach for iot network intrusion detection,” Computers
Security, vol. 151, p. 104337, 2025. [Online]. Available: https:
//www.sciencedirect.com/science/article/pii/S0167404825000264
[17] H. Yan, X. Lin, S. Li, H. Peng, and B. Zhang, “Global or local
adaptation? client-sampled federated meta-learning for personalized iot
intrusion detection,” IEEE Transactions on Information Forensics and
Security, vol. 20, pp. 279–293, 2025.
[18] H. Ding, L. Chen, S. Li, Y. Bai, P. Zhou, and Z. Qu, “Divide,
conquer, and coalesce: Meta parallel graph neural network for iot
intrusion detection at scale,” in Proceedings of the ACM Web
Conference 2024, ser. WWW ’24. New York, NY, USA: Association
for Computing Machinery, 2024, p. 1656–1667. [Online]. Available:
https://doi.org/10.1145/3589334.3645457
[19] S. I. Popoola, A. L. Imoize, M. Hammoudeh, B. Adebisi, O. Jogunola,
and A. M. Aibinu, “Federated deep learning for intrusion detection in
consumer-centric internet of things,” IEEE Transactions on Consumer
Electronics, vol. 70, no. 1, pp. 1610–1622, 2024.
[20] Z. Abou El Houda, H. Moudoud, B. Brik, and M. Adil, “A privacypreserving framework for efficient network intrusion detection in consumer network using quantum federated learning,” IEEE Transactions
on Consumer Electronics, vol. 70, no. 4, pp. 7121–7128, 2024.
[21] H. Babbar and S. Rani, “Frhids: Federated learning recommender
hybrid intrusion detection system model in software-defined networking
for consumer devices,” IEEE Transactions on Consumer Electronics,
vol. 70, no. 1, pp. 2492–2499, 2024.
[22] Z. Qu and Z. Liang, “Fedhlc: A novel federated learning algorithm
targeting heterogeneous and long-tailed data for efficient image classification in consumer electronics,” IEEE Transactions on Consumer
Electronics, vol. 70, no. 4, pp. 7266–7278, 2024.
[23] H. A. Khorshidi and U. Aickelin, “A synthetic over-sampling method
with minority and majority classes for imbalance problems,” Knowledge
and Information Systems, vol. 67, no. 7, pp. 5965–5998, 2025.

[24] M. A. Talukder, S. Sharmin, M. A. Uddin, M. M. Islam, and S. Aryal,
“Mlstl-wsn: machine learning-based intrusion detection using smotetomek in wsns,” International Journal of Information Security, vol. 23,
no. 3, pp. 2139–2158, 2024.
[25] M. Arafah, I. Phillips, A. Adnane, W. Hadi, M. Alauthman, and
A.-K. Al-Banna, “Anomaly-based network intrusion detection using
denoising autoencoder and wasserstein gan synthetic attacks,” Applied
Soft Computing, vol. 168, p. 112455, 2025.
[26] M. A. Talukder, M. M. Islam, M. A. Uddin, K. F. Hasan, S. Sharmin,
S. A. Alyami, and M. A. Moni, “Machine learning-based network
intrusion detection for big and imbalanced data using oversampling,
stacking feature embedding and feature extraction,” Journal of big data,
vol. 11, no. 1, p. 33, 2024.
[27] M. Zheng, X. Hu, Y. Hu, X. Zheng, and Y. Luo, “Fed-ugi: Federated
undersampling learning framework with gini impurity for imbalanced
network intrusion detection,” IEEE Transactions on Information Forensics and Security, vol. 20, pp. 1262–1277, 2025.
[28] W. Meng, Y. Li, F. Zhang, X. Gao, and J. Ma, “Developing distancebased genetic programming classifiers by reconstructing datasets for
imbalanced binary classification,” Pattern Recognition, p. 112825, 2025.
[29] Reddy, C Kishor Kumar and Reddy, Pulakurthi Anaghaa and Reddy,
Pulakurthi Satyanarayana and Shuaib, Mohammed and Alam, Shadab
and Ahmad, Sadaf and Rajaram, A, “Twined ensemble framework for
network security: integrating Random Forest, AdaBoost, and Gradient
Boosting for enhanced intrusion detection,” Discover Internet of Things,
vol. 5, no. 1, p. 107, 2025.
[30] G. Zhao, L. Li, H. He, and J. Ren, “Lgsmote-ids: Line graph based
weighted-distance smote for imbalanced network traffic detection,”
Expert Systems with Applications, vol. 281, p. 127645, 2025.
[31] F. Jemili, K. Jouini, and O. Korbaa, “Intrusion detection based on
concept drift detection and online incremental learning,” International
Journal of Pervasive Computing and Communications, vol. 21, no. 1,
pp. 81–115, 10 2024. [Online]. Available: https://doi.org/10.1108/
IJPCC-12-2023-0358
[32] A. H. Salem, S. M. Azzam, O. E. Emam, and A. A. Abohany,
“Advancing cybersecurity: a comprehensive review of ai-driven detection
techniques,” Journal of Big Data, vol. 11, no. 1, p. 105, 2024.
[33] T. Sun, N. Daoudi, W. Pian, K. Kim, K. Allix, T. F. Bissyande, and
J. Klein, “Temporal-incremental learning for android malware detection,” ACM Transactions on Software Engineering and Methodology,
vol. 34, no. 4, pp. 1–30, 2025.
[34] R. Zhao, M. Zhan, X. Deng, Y. Wang, Y. Wang, G. Gui, and
Z. Xue, “Yet another traffic classifier: A masked autoencoder based
traffic transformer with multi-level flow representation,” Proceedings
of the AAAI Conference on Artificial Intelligence, vol. 37, no. 4, pp.
5420–5427, Jun. 2023. [Online]. Available: https://ojs.aaai.org/index.
php/AAAI/article/view/25674
[35] Z. Jin, J. Zhou, B. Li, X. Wu, and C. Duan, “Fl-iids: A novel
federated learning-based incremental intrusion detection system,” Future
Generation Computer Systems, vol. 151, pp. 57–70, 2024.
[36] Z. Zhang, P. Wang, T. Zhang, M. Liu, and X. Zhou, “Trustworthy
generative few-shot learning-based intrusion detection method in internet
of things,” IEEE Transactions on Consumer Electronics, vol. 71, no. 1,
pp. 1992–2002, 2025.
[37] M. J. Idrissi, H. Alami, A. El Mahdaouy, A. El Mekki, S. Oualil,
Z. Yartaoui, and I. Berrada, “Fed-anids: Federated learning for anomalybased network intrusion detection systems,” Expert Systems with Applications, vol. 234, p. 121000, 2023.
[38] O. Friha, M. A. Ferrag, L. Shu, L. Maglaras, K.-K. R. Choo, and
M. Nafaa, “Felids: Federated learning-based intrusion detection system
for agricultural internet of things,” Journal of Parallel and Distributed
Computing, vol. 165, pp. 17–31, 2022.
[39] Q. Mao, X. Lin, W. Xu, Y. Qi, X. Su, G. Li, and J. Li, “Fecograph:
Label-aware federated graph contrastive learning for few-shot network
intrusion detection,” IEEE Transactions on Information Forensics and
Security, vol. 20, pp. 2266–2280, 2025.
[40] H. Ding, Y. Sun, N. Huang, Z. Shen, and X. Cui, “Tmg-gan: Generative
adversarial networks-based imbalanced learning for network intrusion
detection,” IEEE Transactions on Information Forensics and Security,
vol. 19, pp. 1156–1167, 2023.
[41] C. Qiao, M. Li, Y. Liu, and Z. Tian, “Transitioning from federated learning to quantum federated learning in internet of things: A comprehensive
survey,” IEEE Communications Surveys & Tutorials, vol. 27, no. 1, pp.
509–545, 2024.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
