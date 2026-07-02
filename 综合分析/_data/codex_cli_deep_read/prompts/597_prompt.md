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
# [597] Adaptive Latent Distribution Modeling for Industrial Time Series Anomaly Detection
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
编号：597
题名：Adaptive Latent Distribution Modeling for Industrial Time Series Anomaly Detection
年份：2026
DOI：10.1109/tase.2026.3674236
来源：IEEE Transactions on Automation Science and Engineering
PDF：paper/10.1109_TASE.2026.3674236.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：时序、日志、KPI 与云原生异常检测、其他AI安全与跨域异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\597.txt
- 原始字符数：72387
- 本次发送字符数：72387
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

7893

Adaptive Latent Distribution Modeling for
Industrial Time Series Anomaly Detection
Yu Liu , Yifan Song , Shaolong Shu , Senior Member, IEEE, Feng Lin , Life Fellow, IEEE,
Jun Wang , Senior Member, IEEE, and Yafeng Guo

Abstract—Anomaly detection is critical for ensuring the reliability of industrial cyber-physical systems. Identifying anomalies
based on data distribution is regarded as a promising approach.
However, inherent noise in data collection and complex dependencies within the underlying structure can lead to class ambiguity.
This ambiguity obscures the boundary between normal data and
anomalies, thereby degrading the accuracy of distribution modeling. To address this issue, we shift the distribution modeling from
the data space to a latent space to mitigate ambiguity and then
propose a label free anomaly detection network, named ALDM.
In ALDM, a contrastive-based methods is designed to facilitate
the construction of a latent space, where the margin between
normal data and anomalies has been expanded. Anomalies are
then discerned through embeddings using a flow-based process.
Recognizing the importance of distance metrics in contrastivebased methods, we propose an adaptive approach to obtain the
optimal distance metric during network training instead of presetting a fixed formula. Furthermore, to accommodate anomalies
of varying durations, we propose another event-wise performance
index for evaluation. Extensive evaluations on three widely used
benchmarks and a newly constructed dataset demonstrate that
ALDM achieves state-of-the-art detection performance across
both conventional metrics and our proposed index.
Note to Practitioners—Accurately detecting faults (anomalies)
in industrial systems, such as factories or power grids, is vital
to prevent costly downtime. However, noisy data and complex
interactions make it challenging. Our solution, ALDM, tackles
this by learning a clearer representation of system’s data where
normal and abnormal patterns are easier to distinguish. ALDM
employs an adaptive projection to aid in anomaly detection,
which minimizes expert tuning and enhances uptime. This
approach improves detection accuracy, leading to enhanced
system reliability and fewer unplanned stoppages. Although
ALDM requires sufficient training data for reliable detection,
its label-free methodology provides a practical solution for more
robust monitoring in industrial systems.

Received 8 August 2025; revised 30 January 2026; accepted 11 March 2026.
Date of publication 16 March 2026; date of current version 16 April 2026.
This article was recommended for publication by Associate Editor B. Lacevic
and Editor L. Moench upon evaluation of the reviewers’ comments. This
work was supported in part by the National Key Research and Development
Program under Grant 2022YFB3305300 and in part by the National Natural
Science Foundation of China under Grant 62473289. (Corresponding author:
Shaolong Shu.)
Yu Liu is with the School of Computer Science and Technology, Tongji
University, Shanghai 201804, China (e-mail: liu y@tongji.edu.cn).
Yifan Song, Shaolong Shu, Jun Wang, and Yafeng Guo are with the College
of Electronics and Information Engineering, Tongji University, Shanghai
201804, China (e-mail: shushaolong@tongji.edu.cn).
Feng Lin is with the Department of Electrical and Computer Engineering,
Wayne State University, Detroit, MI 48202 USA (e-mail: flin@wayne.edu).
Digital Object Identifier 10.1109/TASE.2026.3674236

Index Terms—Anomaly detection, cyber-physical systems, fault
diagnosis, time series analysis, unsupervised learning.

I. I NTRODUCTION
ECURITY monitoring is essential for maintaining modern
infrastructures. Deep-learning-based models enhance the
efficiency of monitoring and provide timely alerts for potential
anomalies, thereby preventing damage from escalating. It is
widely adopted in various domains, including healthcare, smart
buildings, and industrial monitoring [1], [2]. Among these
scenarios, industrial cyber-physical systems (CPS) are characterized by their extensive use of sensors to monitor system
behavior [3]. This generates complex, multivariate dynamics,
thereby making anomaly detection more challenging [4].
Traditional anomaly detection methods depend on statistical analysis, which assumes linearity, stationarity, or
specific distributions [5]. These methods often struggle with
high-dimensional data or complex temporal dependencies.
Considering the robust capability in handling high-dimensional
data, AI-based methods have been developed to improve the
reliability of various industrial CPS [6].
In the scope of AI-based methods, due to the scarcity of
labeled anomaly data, anomaly detection is typically studied
in an unsupervised manner. Some previous methods exploit
unlabeled time series data and treat anomaly detection as
a one-class classification (OCC) problem. Many predictionbased methods and reconstruction-based methods are proposed
to achieve anomaly detection under the OCC setting [7], [8].
The basic assumption of the OCC setting is that the training
dataset covers all possible normal samples that can be easily
obtained [9]. This premise is hard to hold in the real world,
and its application requires additional calibration [10], [11].
Due to the typically sparse density of anomalies compared
to normal instances, density-based methods have been widely
explored for anomaly detection. These approaches transform
the problem into estimating the likelihood that a given instance
belongs to the normal data distribution. Anomalies are then
detected as instances with a low probability of being normal.
Density estimation involves calculating the probability of
an observed data vector. Common techniques for this task
include energy-based models (EBMs), undirected probabilistic
graphical models (UPGMs), autoregressive models (ARMs),
and normalizing flow (NF) models [12], [13]. However,
EBMs and UPGMs typically yield only approximate density
estimates, limiting their suitability for anomaly detection.

S

1558-3783 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

7894

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

Fig. 2. Underexplored aspects of F1 score and AUROC in performance
evaluation of anomaly detection.

Fig. 1. Anomaly scores of existing methods on SWaT dataset. All moments
are normal. Vertical drift occurs in the blue area. The moment with a higher
anomaly score is more likely to be identified as an anomaly.

Similarly, ARMs suffer from computational inefficiency due
to their inherently fixed sequential structure. Consequently,
research in density-based anomaly detection has increasingly
focused on normalizing flow (NF) models [14], which have
demonstrated superior performance in industrial applications.
NF models capture complex, high-dimensional data distributions by applying a learnable, invertible transformation to a
simple base distribution (or prior) and leveraging the change of
variables formula. Building upon this, conditional normalizing
flow models [10] have been developed to exploit evolving
mutual information within the data.
In industrial CPS, inherent noise and bias in data transmission and collection lead to data drifts [15], causing the
distributions of normal and abnormal data to overlap. This
overlap gives rise to the class ambiguity problem [16], [17],
obscuring the boundary between different classes in the current
data space. However, existing methods often overlook this
issue and proceed to model the data distribution directly, which
limits further improvement in detection performance. Figure 1
shows the anomaly detection in an industrial water treatment
plant. Existing methods tend to increase the anomaly score
in the blue area during data drift, leading to false alarms. To
address this issue, we propose an Adaptive Latent Distribution
Model (ALDM). ALDM incorporates a contrastive objective
to adaptively reweight the loss function, guiding the model
to learn a latent space optimized for distribution modeling.
Within this space, negative data pairs are pushed apart while
positive pairs are pulled closer, thereby intrinsically increasing
the inter-class margin.
The distance metric plays a crucial role in the contrastive
process of ALDM. While recent contrastive methods [18] use
a fixed metric for assignments, they fail to enhance separability between normal and anomalous distributions. This preset
metric is often suboptimal and adversely impacts learning the
projection from data space to latent space. To address this,
ALDM proposes a learnable, decomposition-based approach
that adaptively optimizes the distance metric during training,
eliminating reliance on predefined fixed formulations.
In terms of performance evaluation, anomalies in industrial
CPS exhibit variable durations [19], necessitating event-level
analysis for many applications. However, established metrics

like F1-score and AUROC focus solely on point-wise assessment, making them inadequate for event-level evaluation.
Figure 2 illustrates this limitation: While Method 1 detects
more anomaly points (yielding higher point-wise scores), it
identifies only one anomaly event. Method 2 detects fewer
points but captures all three events. To address this gap,
we propose a new metric for the auxiliary of performance
evaluation at the event level.
Extensive experiments are conducted on three widely used
benchmarks and a newly constructed dataset. All these datasets
are sourced from representative industrial CPSs. ALDM
demonstrates superior detection performance, outperforming
existing methods on both established point-wise metrics and
our proposed event-level evaluation metric.
Compared with existing works, the contributions of this
paper are summarized as follows:
• We propose ALDM, a novel unsupervised model for
multivariate anomaly detection. To the best of our knowledge, this represents the first flow-based method explicitly
focused on modeling latent distributions within this
context.
• We design an adaptive latent distribution projection
method. This innovation employs a decomposition-based
learnable distance metric to construct an optimized latent
space, effectively expanding the margin between normal
and anomalous distributions.
• We propose a new event-level performance evaluation
metric to address limitations of point-wise assessment.
• We comprehensively validate the effectiveness of ALDM
on three public industrial CPS datasets and a newly
constructed dataset.
The rest of this article is organized as follows. Section II
reviews related work on industrial CPS anomaly detection.
Section III details the proposed ALDM network. Section IV
comprehensively validates the effectiveness of ALDM through
extensive experiments across four datasets and three performance metrics. Finally, Section V concludes the paper.
II. R ELATED W ORK
A. Anomaly Detection in Industrial CPS
Industrial Cyber-Physical Systems (CPS) generate highdimensional data with complex structures. These structures
involve nonlinear dynamics and intricate spatiotemporal
dependencies. Traditional anomaly detection methods [20]
struggle with this complexity. They often fail to capture the
necessary patterns, leading to poor detection performance.
Deep neural networks provide a solution to this challenge.
They excel at modeling the spatiotemporal features of multidimensional time series. This capability enables a shift from

LIU et al.: ADAPTIVE LATENT DISTRIBUTION MODELING FOR INDUSTRIAL TIME SERIES ANOMALY DETECTION

shallow statistical models to deep representation learning for
anomaly detection.
Labeled anomaly data is scarce in practice. Therefore, most
deep learning approaches for this task are unsupervised. These
methods fall into three main categories: prediction-based,
reconstruction-based, and density-based approaches.
Prediction-based and reconstruction-based methods share a
core idea: they learn representations of normal time series
patterns. Anomalies are detected by measuring the difference between actual observations and the model’s output
(either predictions or reconstructions). The core module of
these methods typically employs Transformer as the feature
extractor to process time series data. Li et al. developed a
hierarchical multi-attention block to better reconstruct normal
time series [21]. Belay et al. proposed to leverage Transformer
architectures and optimal truncated singular value decomposition for anomaly detection [22]. While these methods have
advanced time series anomaly detection research, they face
a limitation. They typically require the training data to be
completely free of anomalies. This allows the model to learn
an accurate representation of “normal” behavior. But in real
industrial settings, ensuring perfectly clean training data is
often challenging. This requirement limits the practical use
of prediction and reconstruction methods.
To overcome these limitations and better use inherent
data properties, researchers developed density-based methods. These approaches rely on a key observation: abnormal
instances usually lie in low probability density regions
compared to normal data. Among density-based techniques,
Normalizing Flow (NF) stands out as particularly promising. It
offers theoretical guarantees, flexible architecture, and precise
density estimation.
The development of NF for industrial CPS anomaly detection has evolved over time. Dinh et al. pioneered NF for
general density estimation [23]. Later, Trippe and Turner introduced Conditional Normalizing Flow (CNF) [24], enabling
conditioning on relevant variables. Recognizing the dynamic
nature of industrial CPS data, Zhou et al. further advanced
CNF. They explicitly modeled the evolving structure of mutual
dependencies [10]. Building on this progress, Li et al. explored
a CNF-based approach specifically for industrial CPS anomaly
detection [25]. The core principle uniting these NF-based
methods is explicit. They learn a direct model of the data
distribution. Anomalies are then identified as data points
residing in areas of exceptionally low probability density under
this learned model.
B. Distribution Modeling
Detecting anomalies by modeling the data distribution is
promising. This approach has succeeded in various areas like
image, audio, and time series analysis. Traditional time series
distribution modeling often assumes the whole series follows
a single, static distribution (e.g., Gaussian or Poisson). However, this rigid assumption hurts performance. Probabilistic
models built on it often perform poorly with non-stationary
sequences [9].
Modern distribution modeling uses deep generative models
(DGMs). Their core idea is to model complex data distribu-

7895

tions using neural networks [26]. DGMs are mainly grouped
by how they handle the likelihood function: approximate
likelihood models and exact likelihood models.
Approximate likelihood models (e.g., Variational Autoencoders (VAE) [27], Generative Adversarial Networks (GAN)
[28], and Diffusion Models [29]) do not provide direct access
to the exact likelihood. Instead, they optimize lower bounds or
alternative objectives via variational inference and adversarial
training to indirectly approximate the true data distribution.
In contrast, exact likelihood models (e.g., Normalizing
Flows (NF) [30] and Autoregressive Models (ARM) [31]) can
calculate the exact probability density for any data point. Their
core principle involves decomposing complex distributions
into simpler, tractable base distributions. This is achieved using
reversible transformations or the chain rule of probability. This
paradigm offers key benefits, including theoretical soundness,
better training stability, and improved interpretability. Typical
applications include density estimation and data compression.
Density estimation is a major task for exact likelihood models. It learns how data is generated to quantify the probability
of any data point occurring. Recently, this capability has been
applied to time series anomaly detection. Compared to ARM,
NF avoids the sequential computation constraints. This offers
NF significant computational efficiency advantages, especially
with high-dimensional data. As a result, recent research has
increasingly focused on using NF for time series anomaly
detection [25], [32], [33].
III. M ETHODOLOGY
A. Overview of Anomaly Detection Framework
Consider a multivariate time series collected from an industrial CPS that includes N sensors. The time series data D =
[d1 , d2 , · · · , dL ]> ∈ RL×N consists of L observations, where
dt ∈ RN represents the system state observed at timestamp t.
Note that N sensors are viewed as N variables. To prepare
training samples, we partition D into segments using a sliding
window of length T and stride S . The resulting dataset is
denoted X = {x1 , x2 , · · · , x M }, where M represents the the
total number of segments. We have M = b L−T
S c + 1, where
b·c is the floor operation. The anomaly detection task is to
determine whether any given segment x ∈ X originating from
the same CPS exhibits anomalous behavior.
To address this task, we propose the Adaptive Latent
Distribution Modeling (ALDM) network, an unsupervised
anomaly detection framework illustrated in Fig. 3. ALDM
comprises three core modules: context learning, adaptive latent
distribution projection, and anomaly determination.
The context learning module generates spatio-temporal conditioning signals to guide subsequent distribution modeling. It
explicitly captures both the mutual dependencies among system variables (via self-attention) and the temporal correlations
within the context (via recurrent neural networks) [10], [14].
Graph convolution then integrates these elements to produce
unified conditioning features.
The Adaptive Latent Distribution Projection Module maps
input segments into a latent space and estimates their probability density. This process unfolds through four sequential

7896

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

Fig. 3. Overview of ALDM. Within each detection window xc , the time series data is first processed to generate conditional information (Cc ) and temporal
embeddings (H c ). This temporal embedding H c is then used to compute a distance measure Dc . Based on Dc , soft assignments are calculated. These assignments
directly form the basis for the adaptive soft contrastive loss (LAdSCL ). Minimizing LAdSCL optimizes the parameters of the latent encoding network. This
optimized network transforms the input data into a latent representation rc . Crucially, rc becomes the explicit target for the subsequent normalizing flow to
model. After the normalizing flow adaptively models the distribution of rc , the anomaly score is finally derived from the estimated likelihood.

steps: 1. Adaptive Distance Computation: A learnable distance
metric is first initialized randomly and then optimized during
the training process. 2. Soft Assignments: Using this optimized
metric, the module computes soft labels for each data point.
3. Latent Encoding: Guided by these soft assignments, a
projection function then maps the input segments into their
latent representations, denoted as r. 4. Distribution Projection: Finally, Normalizing Flows (NFs) model the probability
density of the latent vectors r. These NFs are conditioned
on the spatio-temporal features derived from the Context
Learning Module. Specifically, the NFs utilize fully connected
layers to parameterize invertible transformations, converting
the complex distribution of r into a tractable base distribution,
such as a Gaussian.
Finally, the anomaly determination module establishes a
detection threshold using the Interquartile Range (IQR) rule
applied to the estimated log-likelihoods of the latent representations. A segment x is flagged as anomalous if its
log-likelihood falls below this threshold.
ALDM takes a segment x as input and outputs a binary
label ŷ ∈ 0, 1, where 0 indicates normality and 1 indicates
an anomaly. The entire network trains on X without labels.
Implementation and training specifics are detailed in the
following section.
B. Context Learning
Consider data segment xc , a multivariate time series of
length T comprising N variables. The data at timestep t is
denoted xct ∈ RN , while the time series of the i-th variable is
xc,i ∈ RT . We model these N variables as nodes in a graph
whose structure is learned via attention mechanisms.
For each node i, we compute its query and key vectors as:
qc,i = xc,i W Q ,

kc,i = xc,i W K ,

(1)

where W , W ∈ R
are learnable weight matrices. The
pairwise relationship ecij between nodes i and j is then:
Q

K

T ×T

ecij =

(qc,i )(kc, j )>
.
√
T

(2)

The attention score acij (normalized influence of node i on j)
and the resulting adjacency matrix Ac are:
3
2 c
a11 · · · ac1N
c
exp(ei j )
6
.. 7 .
..
(3)
acij = PN
, Ac = 4 ...
.
. 5
c
k=1 exp(eik )
c
c
aN1 · · · aNN
Note that this adjacency matrix represents the learned graph
structure for each input segment. It is randomly initialized and
subsequently refined through attention mechanisms. Specifically, the edge weight between two nodes is determined
by the temporal similarity of their respective time series,
computed through self-attention. This allows the model to
capture context-dependent, non-linear relationships that evolve
over time.
To capture temporal dynamics, we employ recurrent neural
networks (RNNs; e.g., LSTM or GRU). For each timestep t
in xc , the hidden state Ht ∈ RN×dh is updated as:
Ht = RNN(xct , Ht−1 ),

(4)

where dh is the hidden state dimension. The segment-level
contextual embedding Hc is derived by aggregating all hidden
states:
Hc = fc([H1 , · · · , HT ]> ).
(5)
where fc denotes a fully connected layer.
Finally, we fuse spatial and temporal information using the
learned graph structure. Given that explicitly feeding Ht−1
into the fusion operation establishes a more direct and stable
“shortcut connection” for modeling the critical short-term
dynamics between adjacent steps [34], we integrating Ht−1 in
the fusion to enhance condition learning. The spatio-temporal
representation Ct at time t is computed via:


Ct = ReLU Ac Ht W 1 + Ht−1W 2 W 3 ,
(6)
„ ƒ‚ … „ ƒ‚ …
spatial

temporal

where the weight matrices transform features between dimensions. W 1 ∈ Rdh ×d f transforms spatial features. W 2 ∈ Rdh ×d f
transforms temporal features. W 3 ∈ Rd f ×do enhances representational capacity. Note that d f is the fused feature dimension

LIU et al.: ADAPTIVE LATENT DISTRIBUTION MODELING FOR INDUSTRIAL TIME SERIES ANOMALY DETECTION

and do is the output dimension. The full spatio-temporal
embedding is Cc = [C1 , · · · , CT ]> ∈ RT ×N×do .
C. Adaptive Latent Distribution Projection
The adaptive latent distribution projection module consists of four components: adaptive distance computation, soft
assignment, latent encoding, and distribution projection. In
this module, adaptive distance computation and soft assignment collaboratively guide the latent encoding network in
mapping input data to representations within a latent space.
Subsequently, the distribution projection component builds a
transformation chain that maps complex latent distributions
onto simple base distributions. We formalize this process
below.
1) Adaptive Distance Computation: We define a positive semi-definite distance metric matrix M via Cholesky
decomposition:
M = L> ΛL,
(7)
where L ∈ RE×E is a lower triangular matrix and Λ ∈ RE×E is
a diagonal matrix. Both L and Λ are initialized randomly and
optimized using gradient descent during training. This decomposition ensures numerical stability and mitigates overfitting
compared to direct learning of M.
Unlike prior approaches that compute distances directly
from raw data, we propose to compute contextual distance
between temporal embeddings. Let Hc = [h1 , . . ., hT ]> ∈ RT ×E
denote the temporal embeddings from RNN in context learning. The distance matrix Dc ∈ RT ×T is computed as:
p
(8)
Dc [t][t0 ] = (ht − ht0 )> M(ht − ht0 )
p
>
>
(9)
= (ht − ht0 ) L ΛL(ht − ht0 ),
where ht , ht0 ∈ RE are temporal embeddings at timesteps t and
t0 . Equation (8) represents the Mahalanobis distance, which
generalizes Euclidean distance (obtained when M = I) by
incorporating covariance structure. This learnable formulation
adapts to data distributions, overcoming limitations of preset
metrics in prior work.
2) Soft Assignment: From Dc , we compute a soft assignment matrix Wc ∈ RT ×T :

Wc [t][t0 ] = 2σ −τT · Dc [t][t0 ] ,
(10)
where τT > 0 controls distribution sharpness and σ is the
sigmoid function. Soft assignments provide adaptive similarity
measures that capture the correlation of temporal embeddings,
enhancing the flexibility of the contrastive process.
3) Latent Encoding: Given a batch of K time series segments X = {x1 , . . ., xK }, where each xc ∈ RT ×N (c ∈ [1, K]),
we generate augmented views as follows: For each segment,
we sample two overlapping intervals [a1 , b1 ] and [a2 , b2 ]
satisfying 0 < a1 ≤ a2 ≤ b1 ≤ b2 ≤ T . The augmented
views xc+ and xc− are created by masking all elements outside
[a1 , b1 ] and [a2 , b2 ], respectively. This yields augmented pairs
K
{(x1+ , x1− ), . . ., (x+
, x−K )}.
A feature extractor fθAdSC projects segments to latent
representations:
rc = fθAdSC (xc ) ∈ RT ×N ,

(11)

7897

where θ denotes trainable parameters. The encoder fθAdSCL consists of three components, including an input projection layer, a
timestamp masking module, and a dilated convolutional neural
network (CNN) module.
Specifically, for each input segment xc ∈ RT ×N , the processing pipeline is as follows:
1) Input Projection: A fully connected layer maps each
timestamp observation xc,t ∈ RN to a high-dimensional
latent vector rc,t ∈ Rd :
rc,t = fc(xc,t )
2) Timestamp Masking: This module randomly selects
timestamps and masks their corresponding vectors to
generate augmented context views. Note that the masking operates on latent representations rather than raw
temporal indices. We choose to mask latent vectors
instead of raw values. This decision is based on the fact
that time series data can be unbounded (R), and thus
lacks a natural masking token.
3) Dilated CNN: A 10-block residual network processes
the sequence {rc,1 , . . ., rc,T }. Each block contains two
1-D convolutional layers with exponentially increasing
dilation rates: for the l-th block (l ∈ {1, . . ., 10}), the
dilation parameter is 2l .
The latent encoding network enhances separability between
normal and anomalous patterns. The encoder parameters θ
are optimized through a composite contrastive loss function
containing two complementary components:
(1) Instance-level loss promotes segment discrimination: Let
c be the index of the input time series segment, t be the
c,t
c
timestamp, rc,t
+ and r− be the representation of x+ and
(c,t)
c
x− for the timestamp t, LI is denoted as

c,t
exp rc,t
− · r+
(c,t)
LI = − log B h

i


P
j,t
j,t
c,t
exp rc,t
− · r+ + I[c, j] exp r− · r−
j=1

(12)
where B is the batch size, and I is the indicator function.
LI measures the similarity of segments, guiding the
model to learn robust representations through instancewise contrast.
(2) Temporal loss captures contextual relationships:
L(c,t)
= − log p+
c (t, t) − AdL(c, t)
T

(13)

where
AdL(c, t) =

T
X

0
−
0
WT (t, t0 )(log p+
c (t, t ) + log pc (t, t ))

t0 =1,t0 ,t
0

0
p+
c (t, t ) = P

c,t
exp(rc,t
− · r+ )

c,t
c,s
c,t
c,s
s∈Ω (exp(r− · r+ ) + I[s,t] exp(r− · r− ))
c,t0
exp(rc,t
− · r− )
p−c (t, t0 ) = P
c,t
c,s
c,t
c,s
s∈Ω (exp(r− · r+ ) + I[s,t] exp(r− · r− ))

Note that Ω denotes timestamps in the augmented views’
overlap region.

7898

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

Algorithm 1 Training Procedure for ALDM

The composite contrastive loss is:
K

T


1 X X  (c,t)
.
LAdSCL =
LT + L(c,t)
I
KT

(14)

c=1 t=1

where K is the number of instances, T is the sequence length.
4) Distribution Projection: This component utilizes normalizing flows to transform the complex high-dimensional
data distribution pX (x) into a simple base distribution πU (u)
through a series of learnable, invertible affine transformations.
Following established approaches [34], we incorporate spatiotemporal correlations as conditioning information to enhance
density estimation. This is formalized through a conditional
normalizing flow:
u = fθ (x | C)
(15)
where C represents the spatio-temporal conditioning variable,
fθ : X → U is a parametric, bijective transformation. θ denotes
the parameters of fθ , and u ∼ πU (u) with πU (u) typically
chosen as a standard Gaussian distribution.
Unlike previous work that estimates density in the data
space (pX (x)), we propose modeling the density of learned representations r = fθAdSC (x) in latent space. To our knowledge,
this represents the first flow-based method explicitly focused
on modeling latent distributions within this context.
The formal density estimation process is as follows: Given
a segment xc ∼ pX (x) and its associated condition Cc , we first
obtain the latent representation rc = fθAdSC (xc ). The density of
rc is then given by:
ˇ
ˇ
ˇ
∂ fθ (rc | Cc ) ˇˇ
(16)
pR (rc | Cc ) = πU ( fθ (rc | Cc )) ˇˇdet
ˇ
∂rc
ˇ ˇ
ˇ ˇ
where πU (·) = N (µ, I) and the Jacobian determinant ˇ ∂∂rfθ ˇ
accounts for the volume change under the transformation.
During training, the conditional normalizing flow (CNF)
is optimized jointly with the context learning module via
maximum likelihood estimation. The objective function is:
LMLE = − log pR (rc | Cc )

N1
Input: Training Data: Dtrain = {xi }i=1
; Learning Rate: α; Total
Epochs: E; Batch Size: B; Loss Weight: λ; Networks: fθCL
,
1
NF
fθAdSC
,
f
.
θ3
2
Output: Trained model parameters θ1 , θ2 , θ3 .
1: epoch ← 0
.Initialize epoch counter
2: while epoch < E do
3:
idx1 ← 0
.Reset batch index for each epoch
4:
while idx1 < dN1 /Be do
.Iterate over batches
5:
xc ← SampleBatch(Dtrain , idx1 , B) .Sample mini-batch
xc of size B
6:
Cc ← fθCL
(xc ) .Compute spatio-temporal condition Cc
1
7:
rc , W(t, t0 ) ← fθAdSC
(xc ) .Learn latent embeddings rc
2
and adaptive assignments W
8:
ûc ← fθNF
(rc , Cc ) .Estimate latent density
3
9:
LAdSCL ← LAdSCL (rc , W(t, t0 )) .Compute adaptive soft
contrastive loss
10:
LMLE ← LMLE (ûc , rc ) .Compute maximum likelihood
estimation loss
11:
LALDM ← (1 − λ) · LMLE + λ · LAdSCL
.Compute
combined loss
12:
θ1 ← θ1 − α · ∇θ1 LALDM
.Update GL parameters
13:
θ2 ← θ2 − α · ∇θ2 LALDM .Update AdSCL parameters
14:
θ3 ← θ3 − α · ∇θ3 LALDM
.Update NF parameters
15:
idx1 ← idx1 + 1
.Increment batch index
16:
end while
17:
epoch ← epoch + 1
.Increment epoch counter
18: end while

where rc,n denotes the n-th dimension of the embedding
vector rc .
Directly thresholding the anomaly score S c to label anomalies has been shown to increase anomaly detection interference
[35]. To mitigate this, we compute the anomaly scores S c for
the entire training set. The detection threshold is then robustly
set using the Interquartile Range (IQR) method:
Threshold = Q3 + 1.5 × (Q3 − Q1 )

ˇ
ˇ

K
N
ˇ
1 XX
∂ fθ ˇˇ
c ˇ
c
=−
log πU fθ (rn | Cn ) ˇdet c ˇ
NK
∂rn
c=1 n=1
ˇ
ˇ

K
N
ˇ
∂ fθ ˇ
1 XX 1 c
kûn − µn k22 + log ˇˇdet c ˇˇ
≈
(17)
NK
2
∂rn
c=1 n=1

This MLE objective LMLE will integrate with contrastive
loss LAdSCL to form the complete optimization target.

where Q1 and Q3 represent the 25th and 75th percentiles of
the anomaly scores S c observed in the training data.
E. Joint Optimization
The proposed model employs joint optimization of the
context learning module and the adaptive latent distribution
projection network to enhance training stability. The overall
objective function for ALDM is formulated as:
LALDM = (1 − λ) · LMLE + λ · LAdSCL

D. Anomaly Determination
An anomaly is flagged when the representation vector rc
falls within a low-density region of the learned distribution.
This position indicates that the original input xc is more likely
to be anomalous. The anomaly score S c for c-th sample is
computed as the mean negative log-likelihood across all N
dimensions of its embedding rc :
N

1 X
Sc = −
log PR (rc,n )
N
n=1

(18)

(19)

(20)

where λ ∈ [0, 1] is a hyperparameter balancing the contribution
of each loss component (λ = 0.5 by default). The loss terms
LAdSCL and LMLE are defined by Equations (14) and (17),
respectively.
Algorithm 1 details the ALDM training procedure.
IV. E XPERIMENTS AND A NALYSIS
This section first introduces the proposed event-level auxiliary metric and a new anomaly detection dataset. We then

LIU et al.: ADAPTIVE LATENT DISTRIBUTION MODELING FOR INDUSTRIAL TIME SERIES ANOMALY DETECTION

7899

The base TEP models a plant-wide chemical process featuring
five major unit operations: reactor, product condenser, vaporliquid separator, recycle compressor, and product stripper. The
TEPE dataset contains 53 process variables, including flow
rates, pressures, temperatures, levels, and chemical component
concentrations. It incorporates 20 distinct anomaly types,
simulating 180 artificial anomaly events at 1-minute sampling
intervals over 360 operational days. Fig. 4 shows the piping
and instrumentation diagram.
B. Experimental Setup
Fig. 4. Piping and instrumentation diagram of the TEPE.

detail the experimental setup, present comparative results
across four datasets using three evaluation metrics, and conduct ablation studies to validate the effectiveness of the
proposed modules.1
A. Auxiliary Metric and New Dataset
1) Event-Level Auxiliary Metric: As shown in Fig. 2, classic metrics exhibit limitations in capturing event-level anomaly
characteristics. To address this, we propose an auxiliary metric
based on anomaly event recall. Adopting the standard time
series definition, an anomaly event is a contiguous sequence of
anomalous points, while a prediction segment is a contiguous
set of points flagged as anomalous by the model.
We define the true positive predictions TPE as the number
of ground truth (GT) events that fully or partially overlap with
one prediction segment or more. The false negative predictions
FNE is the number of GT events that do not overlap with any
prediction segment. Event recall (RE ) is computed as:
TPE
(21)
TPE + FNE
Event precision (PE ) incorporates point-level false positives
with a normalization factor:
TP
FP
PE =
× λFE , λFE = 1 −
(22)
TP + FP
N
where TP/FP denote point-level true/false positives, and N is
the total normal points. The event-level F1 score is:
RE =

2 · PE · RE
(23)
PE + RE
Alongside F1E , we report classic point-level F1 score and
AUROC for comprehensive evaluation.
2) TEPE Simulation Dataset: As illustrated in Fig. 2, we
would like to perform an event-level analysis for anomaly
detection. However, existing public datasets contain a relatively small number of anomaly events (e.g., 35 in SWaT,
72 in PSM, 36 in MSL). To overcome this limitation, we
developed a new simulation dataset TEPE (Tennessee Eastman
Process Extension), extending the benchmark Tennessee Eastman Process (TEP) [36] to include diverse anomaly events.
F1E =

1 The source code of ALDM and the proposed TEPE dataset are available
at https://github.com/YuLiu-61/ALDM

1) Datasets and Baselines: Apart from the proposed new
dataset TEPE, three additional datasets are evaluated:
• SWaT (Secure Water Treatment) [37]: Originating from
a scaled-down version of an industrial water treatment
plant, the SWaT dataset is used for research in cybersecurity and anomaly detection in critical infrastructure
systems. SWaT collects 51 sensor data from a real-world
industrial water treatment plant, at a frequency of one
second. The dataset provides ground truths of 41 attacks
launched during 4 days.
• MSL (Mars Science Laboratory rover) [38]: This dataset
originates from the Mars Science Laboratory rover,
specifically the Curiosity rover. It includes telemetry
data used to detect anomalies in the rover’s operational
parameters during its mission on Mars.
• PSM (Pooled Server Metrics) [39]: This dataset aggregates performance metrics from multiple server nodes
managed by eBay. It is utilized to identify outliers, indicating potential issues in server performance or security
breaches.
For the baseline methods, we used publicly available implementations under the contaminated training setting. These
methods include DeepSAD [40], DeepSVDD [41], USAD
[42], DAGMM [43], GANF [34], MTGFlow [10], FITS [44],
and CrossAD [45]. We retained their original network and
trained them follows the best hyperparameter reported in their
paper.
2) Implementation Details: All experiments were conducted on an Ubuntu Linux 64-bit operating system, with
the support of Python 3.8 environment and Pytorch platform.
The hardware configuration is listed as follows: an Intel Core
i9-13900KF CPU @5.8 GHz, a 32 GB memory card, and an
NVIDIA RTX 4090 @24 GB GPU.
In the comparison study, we set the anomaly detection
window size to 60 and the stride size to 10 for all experiments.
The total number of training epochs is 40 (TEPE), 100
(SWaT), 250 (PSM), and 250 (MSL). For the batch size, we
used 512 for the SWaT dataset and 256 for the other datasets.
Adaptive Moment Estimation with Weight Decay (AdamW)
is chosen as the optimizer, and the learning rate scheduler is
OneCycleLR with a percentage start of 0.2, an initial learning
rate of 0.002, and a maximum learning rate of 0.004. Detailed
parameter settings of our model are provided in Table I.
For the parameter selection of our model, we aligned the
general parameters such as window size, stride size, weight
decay, batch size, threshold ratio, and block size with those

7900

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

TABLE I
E XPERIMENTAL PARAMETERS OF ALDM IN C OMPARATIVE E XPERIMENTS

TABLE II
E XPERIMENTAL R ESULTS OF ALDM AND B ENCHMARK M ETHODS
ON AUROC(%)

of the open-sourced state-of-the-art density-based method
MTGFlow, as detailed in Table I. With these parameters set,
we further optimized the remaining tunable hyperparameters
through extensive experimentation.
C. Performance Evaluation of ALDM
The results across the four datasets on three metrics are
presented in Tables II and III. Bold and underlined numbers
denote the optimal and suboptimal values, respectively.
As shown in Table II, the ALDM model proposed in
this paper exhibits the best AUROC performance across all
scenarios, including cyber-physical attacks in SWaT and PSM,
as well as system-level faults in TEPE and MSL. Notably,
on the SWaT dataset, the AUROC of ALDM reaches 0.905,
marking a 5.7 percentage point improvement over the suboptimal model MTGFlow. MTGFlow ranks second overall,
with its AUROC value (0.811) on the TEPE dataset slightly
lower than the USAD model by 0.5 percentage points. In terms
of standard deviations, ALDM shows stable performance on
datasets with low anomaly ratios but relatively higher variance
on datasets with more anomalies. This instability stems from
its density-based framework and latent encoding, which may
inadvertently incorporate prevalent anomalous patterns into the
learned latent structure, biasing the likelihood estimation and
affecting the detection threshold. In practice, this effect can be
effectively mitigated by collecting more normal data.
Table III presents a comparison on F1 and F1E scores.
The proposed ALDM persists the superior F1 score across
all datasets, with a particularly notable performance on the
SWaT, where it outperforms the second-ranked model by 0.12
(0.68 vs 0.56). The F1E score indicates that ALDM still
delivers the best performance. The suboptimal F1E for SWaT,
PSM, MSL, and TEPE are achieved by DAGMM (0.7734),
MTGFlow (0.6743), MTGFlow (0.4949), and DeepSVDD

(0.7403), respectively. It is noteworthy that the suboptimal
model on the F1E score significantly differs from the pointlevel indicator (F1/AUROC). For example, DeepSVDD ranks
second in the F1E of TEPE, but its F1 score is lower than that
of MTGFlow. This verifies the difference between event-level
indicators and point-level indicators: the former requires the
model to have the ability to identify the temporal continuity
of abnormal events, while the latter focuses on the detection
accuracy of individual points. This finding confirms the supplementary value of the F1E score to the existing evaluation
metrics.
To visualize the benefits of ALDM, Fig. 5 presents the ROC
curves for four datasets. In these curves, ALDM consistently
outperforms the baseline methods, highlighting its robustness
and effectiveness in anomaly detection tasks.
Fig. 6 uses a point plot to compare the anomaly predictions
of the proposed ALDM and the second-ranked MTGFlow.
Time indices are on the x-axis, and anomaly scores per
data segment are on the y-axis. Red backgrounds highlight
ground-truth anomalies. ALDM consistently assigns higher
scores to anomalies (within red regions) and lower scores
to normal data compared to MTGFlow. It also exhibits
sharper score changes at anomaly boundaries (beginnings/ends
of red region), indicating more precise boundary detection.
Besides, ALDM achieves a significantly lower mean anomaly
score for normal periods, demonstrating superior false alarm
suppression.

D. Result Verification
Recall that the core problem comes from the observation
that inherent noise and bias in data transmission and collection
induce data drifts. These drifts cause the distributions of normal and abnormal data to overlap. The overlap gives rise to the
class ambiguity problem, where the boundary between classes
becomes obscured in the current data space. In the following,
we evaluate the effectiveness of ALDM in addressing the
above issue.
We first employ the Augmented Dickey-Fuller (ADF) test
statistics [46] to measure the extent of data drifts. The results
in Table IV reveal clear differences in time series stationarity
across the four datasets. SWaT (ADF = −0.780, p = 0.83)
and MSL (ADF = −1.228, p = 0.66) show high p-values,
indicating strong non-stationarity and significant data drift. In
contrast, TEPE (ADF = −9.48, p = 0.01) is clearly stationary,
while PSM (ADF = −6.060, p = 0.05) sits near the conventional significance threshold, suggesting mild or borderline
non-stationarity.

LIU et al.: ADAPTIVE LATENT DISTRIBUTION MODELING FOR INDUSTRIAL TIME SERIES ANOMALY DETECTION

7901

TABLE III
E XPERIMENTAL R ESULTS OF ALDM AND B ENCHMARK M ETHODS ON F1E AND F1 S CORE . P OINT A DJUSTMENT N OT A PPLIED

Fig. 5. The AUROC curves of the SWaT, PSM, MSL, and TEPE datasets.

Fig. 6. Point plot of the anomalies prediction of MTGFlow and ALDM on SWaT (left 2 columns) and TEPE (right 2 columns). The x-axis denotes time
points, and the y-axis denotes the anomaly score. The red region is ground truth anomalies.

These findings align with the observed performance gains.
ALDM delivers larger AUROC improvements on SWaT
(+ 5.7%) and MSL (+ 2.9%), i.e., the two most non-stationary
datasets, where data drift likely causes greater class ambiguity.
On the more stationary datasets (PSM and TEPE), where drift
is limited, the gains are smaller (+ 1.1% and + 1.4%, respectively). This supports the hypothesis that ALDM is particularly

effective in scenarios with pronounced non-stationarity and
associated data drift.
Next, we analyzed the probability density distributions.
Fig. 7 presents probability density plots comparing the distributions of anomaly scores for “Normal” and “Abnormal”
data segments. The x-axis represents the anomaly score, while
the y-axis shows the corresponding probability density of

7902

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

Fig. 7. Probability density plots of MTGFlow (up) and ALDM (bottom) on SWaT (a), PSM (b), MSL (c), and TEPE (d).

TABLE IV
S TATIONARITY A SSESSMENT U SING AUGMENTED D ICKEY-F ULLER
(ADF) T EST S TATISTICS

segments. As expected, normal data segments are skewed
towards lower anomaly scores (left side), while anomalies are
skewed towards higher scores (right side). The overlap metric
quantifies the area where these two distributions overlap,
serving as an indicator of how effectively a method separates
normal and abnormal cases. Better separation manifests as less
overlap. The first row of subfigures in Fig. 7 displays results
achieved by MTGFlow on the four datasets, while the second
row shows results from the proposed ALDM.
Regarding the overlap metric: MTGFlow exhibits overlap values of 0.28, 0.44, 0.33, and 0.09 across subfigures
(a), (b), (c), and (d), respectively. Crucially, ALDM demonstrates smaller overlap areas than MTGFlow across all
datasets. This reduction in overlap indicates that ALDM
achieves superior performance in distinguishing between normal and abnormal data, resulting in a clearer boundary.
Regarding the distribution shape: In all subfigures, ALDM’s
distribution for normal data (blue) exhibits a smaller mean
value, while its distribution for abnormal data (red) exhibits a
larger mean value compared to MTGFlow. This increased separation between the means further confirms ALDM’s enhanced
ability to identify anomalies.
Regarding the range of anomaly scores: Compared to
MTGFlow, ALDM compresses the range of anomaly scores
across all datasets. For instance, considering subfigure
(a): MTGFlow assigns normal segments scores ranging from

0 to 1. In contrast, ALDM compresses the anomaly scores
of most normal segments tightly around 0.02, demonstrating
excellent separation from abnormal segments.
In summary, ALDM shows better performance across all
test conditions, especially in reducing the overlap between
normal and abnormal data and improving the accuracy of
anomaly detection.

E. Ablation Study
To assess the validity of each designed module, we conducted several ablation experiments on the proposed methods.
1) Module Effectiveness: The ablation experiments presented in Table V provide insights into the contributions of
context learning (CL), adaptive distance computation (ADC),
and soft assignment (SA) to the performance of various
models across different datasets. The results indicate that
incorporating SA significantly enhances model performance,
as evidenced by the substantial improvements when comparing
M0 (which lacks all three components) with M1 (which
includes only SA). For instance, on the SWaT dataset, the
AUROC increases from 73.5±4.3 to 88.5±0.9, the F1 score
rises from 0.3206 to 0.6592, and the F1E score increases
from 0.4267 to 0.9790. Further enhancements are observed
when ADC is added (M2), suggesting that both SA and ADC
play crucial roles in improving model accuracy. The inclusion
of CL (as seen in M3 and M0) also contributes positively,
although its impact is less pronounced compared to SA and
ADC. The final model, ALDM, which integrates all three
components, achieves the highest performance across most
datasets, demonstrating that the combination of CL, ADC,
and SA is essential for optimal results. This comprehensive
analysis underscores the importance of these components in
enhancing the model’s ability to learn contextual information,

LIU et al.: ADAPTIVE LATENT DISTRIBUTION MODELING FOR INDUSTRIAL TIME SERIES ANOMALY DETECTION

7903

TABLE V
A BLATION E XPERIMENTS ON C ONTEXT L EARNING (CL), A DAPTIVE D ISTANCE C OMPUTATION (ADC), AND S OFT A SSIGNMENT (SA)

TABLE VI
A BLATION E XPERIMENTS ON S TATIC D ISTANCE M ETRICS AND A DAPTIVE D ISTANCE C OMPUTATION (ADC)

compute distances adaptively, and assign labels softly, leading
to superior detection performance.
2) Impact of Distance Metrics: To further evaluate the
benefits of adaptive distance computation, we present a
comprehensive comparison between static distance metrics
(TD, COS, DTW) and the Adaptive Distance Computation
(ADC) method across four datasets in Table VI. The evaluation metrics include AUROC, F1 score, and F1E score,
which collectively offer insights into the models’ capabilities
in distinguishing normal from anomalous instances, balancing point-wise precision/recall, and addressing event-wise
anomaly detection, respectively. ADC consistently outperforms the static distance metrics across nearly every evaluation
measure and dataset. These observations suggest that ADC
not only provides superior discrimination power but also
ensures better precision-recall trade-off and enhanced eventwise detection capability. Furthermore, the relatively smaller
standard deviations achieved by ADC indicate its stability and
robustness across different configurations. In contrast, while
TD, COS, and DTW exhibit varying degrees of effectiveness
depending on the dataset, none of them can universally outmatch ADC. This evidence shows the advantage of employing
adaptive mechanisms in distance calculation for improving the
accuracy and reliability of anomaly detection systems.
We also validated the effectiveness of Cholesky decomposition in ADC by comparing it with two alternatives:
eigenvalue clipping and directly learning the metric matrix
M. Directly learning M caused immediate training failure
due to NaN loss, underscoring the need to enforce positive
semi-definiteness. Eigenvalue clipping required costly projections onto the positive semi-definite cone after each iteration,
leading to computational overhead (283 seconds/epoch vs.
30 seconds for Cholesky on SWaT) and potential optimization
instability.
3) Impact on Event-Wise Index: The complete model
(ALDM) achieves the best event-level F1E scores across all
four datasets (SWaT, PSM, MSL, TEPE). This demonstrates

that the combined components effectively improve the completeness of anomaly event detection. SA provides significant
boost to event-level performance. For instance, on SWaT,
adding SA (M0 vs. M1) improves F1E from 0.4267 to 0.8790.
Stable gains are observed on other datasets, indicating SA’s
crucial role in reducing missed detections for continuous
events. Building upon SA, ADC further refines event detection.
Comparing M1 (w/o ADC) to M2 (w/ ADC), F1E improves on
SWaT (0.8790 to 0.8979) and PSM (0.6770 to 0.7026). This
suggests ADC helps better delineate event boundaries through
learned similarity. The impact of CL is dataset-dependent.
While it offers a large gain on SWaT (M0 vs. M3: 0.4267
to 0.7702), its effect is more modest or slightly negative on
others (e.g., TEPE). This implies its utility is tied to the
specific contextual nature of anomalies in the data. The full
combination (CL+ADC+SA) yields the best overall eventlevel performance. Notably, adding ADC to the CL+SA setup
(M4 vs. ALDM) leads to substantial gains on PSM (0.6916 to
0.7516) and MSL (0.4953 to 0.5303), confirming ADC’s key
role in synthesizing context and soft assignment for superior
event detection.
4) Analysis of Soft Assignment: Based on the ablation
studies (Table V), the soft assignment (SA) mechanism delivers largest performance gains. Its most significant impact is
observed on the SWaT dataset, where introducing SA alone
(M0 vs. M1) boosts AUROC by 15.0 points and F1-score by
0.3386. When integrated with the context learning module (M3
vs. M4), SA provides further improvements, such as increasing
the F1-score on SWaT by 0.1018. These quantitative results
confirm the importance of SA in enhancing the model’s
discriminative power. By generating soft labels to guide the
latent encoding, SA significantly refines the estimation of
data probabilities, leading to more accurate anomaly detection
across multiple benchmarks. We also performed a t-SNE
visualization of the latent vector following SA-guided latent
projection, as shown in Fig. 8. The figure illustrates the
distribution of latent vectors at 1, 30, 60, and 100 epochs. It is

7904

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

Fig. 8. The t-SNE visualization of the latent vector on SWaT after 1, 30, 60, and 100 epochs, from left to right. The blue and red points correspond to
normal and anomalous samples, respectively.

TABLE VII

TABLE VIII

T RAINING T IME OF ALDM AND BASELINES ON W HOLE
DATASET (M IN )

T EST T IME OF ALDM AND BASELINES ON W HOLE
DATASET (S EC )

evident that the boundary between normal and abnormal samples becomes increasingly clear, indicating that the SA-guided
latent projection effectively helps to separate the distributions
of normal and abnormal data.
Reviewing the ablation studies presented in Tables V
and VI, the following conclusions can be drawn: 1) The
proposed ALDM consistently improves performance across
experiments. This validates the underlying motivation that
increasing the margin between normal data and anomalies
through contrastive latent encoding is effective. 2) The best
static distance metric varies depending on the dataset, suggesting that different variable dependencies favor different
metrics. Crucially, the proposed ADC module addresses this
by adaptively learning the optimal metric, enabling ALDM
to consistently achieve state-of-the-art (SOTA) performance.
3) The context learning module further enhances ALDM’s
effectiveness. This demonstrates that context information is
valuable not only for modeling data distributions but also for
modeling latent distributions.
F. Computational Complexity
The computational complexity of ALDM is approximately
223 MFLOPs (i.e., 2.23 × 108 floating-point operations) per
inference, measured in single-precision (FP32) arithmetic.
This level of computational demand is well within the capabilities of modern edge devices and mobile platforms. For
instance, on the NVIDIA Jetson Nano, a modest embedded
platform with 141 GFLOPs, the model is estimated to achieve
a latency of 20–50 ms per inference. This satisfies real-time

requirements for most time series monitoring applications. We
also compared the training time and inference time of ALDM
and other baselines on whole dataset. The results are shown
in Tables VII and VIII.
ALDM shows a trade-off between improved performance
and increased computation. During training, ALDM takes
much longer than all baseline methods on every dataset. For
example, on SWaT, ALDM requires 38.34 minutes-about 6
times longer than FITS (6.41 min) and over 13 times longer
than the top competitor MTGFlow (2.86 min). Similar gaps
appear on PSM (6.74 vs. 1.01 min for FITS), MSL (6.09
vs. 0.61 min for GANF), and TEPE (18.31 vs. 4.55 min for
GANF). The longer training time is attributed to the synergistic
impact of the latent encoding and contextual learning modules
within the ALDM. This collaboration necessitates additional
epochs for the model to effectively map data to a suitable
latent distribution. Although ALDM requires a longer training
duration compared to other benchmark models, the training
completion time remains on the minute level (less than an
hour), which is still acceptable.
At test time, however, ALDM is more efficient. Though
slower than lightweight models like DeepSVDD and USAD,
its inference speed is still practical for real-time inference.
On SWaT, ALDM processes the full test set in 9.36 secondsmuch faster than FITS (74.49s) and only 2-3 times slower than
MTGFlow (4.84s). This trend continues on other datasets, with
test times of 2.59s (PSM), 2.46s (MSL), and 7.58s (TEPE).
The reasonable inference cost, despite the model’s complexity,
means that once trained, ALDM can compute representations

LIU et al.: ADAPTIVE LATENT DISTRIBUTION MODELING FOR INDUSTRIAL TIME SERIES ANOMALY DETECTION

7905

Fig. 9. Sensitivity analysis of window size (up), latent dimension (mid), and loss balance weight (down) in SWaT, PSM, MSL, and TEPE.

and density estimates efficiently. This balance makes ALDM
viable for applications where offline training is acceptable and
detection accuracy is prioritized.

can often be fixed to a moderate value without significant
performance loss.
H. Limitations

G. Parameter Sensitivity Analysis
To better understand the robustness of ALDM and facilitate
its practical deployment, we conduct sensitivity analysis on
three key hyperparameters: window size (T ), latent dimension (d), and loss balancing weight (λ). We evaluate their
impact across four datasets using AUROC, F1 score, and
F1E score. The experiments are performed in the range of
T ∈ [40, 100], d ∈ [120, 512] and λ ∈ [0.2, 0.8].
The experimental results are shown in Fig. 9. It can be
observed that window size has a significant effect on anomaly
detection performance, especially on the SWaT and PSM
datasets, where AUROC and F1E peak when the window
size is between 60–80. This indicates that an appropriate
context length helps capture anomaly patterns, but overly long
windows introduce redundant information, reducing detection
accuracy. The impact of latent dimension is relatively smaller,
but excessively high dimensions (such as 512) can lead to a
slight performance drop, suggesting a potential risk of overfitting. Therefore, it is recommended to use moderate dimensions
(such as 256–320). Additionally, the loss balance weight is
also critical for model performance. On most datasets, AUROC
and F1E show the best performance when the weight is set to
0.5, indicating that the effective balance between contrastive
loss and distribution projection loss is crucial.
These findings underscore that reasonable hyperparameter selection is necessary for high-performance time series
anomaly detection. In particular, window size and loss weighting require dataset-specific tuning, whereas latent dimension

While ALDM demonstrates strong performance in unsupervised anomaly detection, several limitations are worth
discussing. First, when abundant and diverse normal data
that covers all typical scenarios is available (semi-supervised),
reconstruction-based or forecasting-based methods may outperform ALDM’s density estimation approach. These methods
explicitly learn the decision boundary of normal data, whereas
ALDM does not directly utilize the presence of clean training
samples.
Second, the anomaly threshold is determined heuristically
via the IQR rule on log-likelihoods. While unsupervised and
parameter-free, this approach assumes that the majority of
training data is normal (a common but not universal assumption). In scenarios with high contamination rates (>25%
anomalies in training data), the IQR-based threshold may be
biased, resulting in degraded generalization.
Third, while Normalizing Flows provide exact likelihood
estimation, their representational capacity is constrained by
the architecture of the invertible transformations. This architectural limitation may yield inadequate approximations of
highly multimodal or intricately structured latent distributions,
potentially causing false positives/negatives.
These limitations point to promising directions for future
work, such as incorporating robust thresholding mechanisms
or replacing NFs with more flexible generative priors.
V. C ONCLUSION
This study addressed the class ambiguity problem in industrial time series anomaly detection by proposing a novel latent

7906

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

distribution modeling approach. Our key finding demonstrates
that shifting the distribution modeling objective from the raw
data space to a latent space effectively enlarges the margin
between normal and abnormal patterns, thereby enhancing
the discrimination capability of density-based anomaly detectors. Furthermore, the proposed adaptive distance computation
mechanism actively separates representations of normal and
anomalous segments, making the proposed ALDM well-suited
for the anomaly detection task. The efficacy and generality of
the proposed latent space transformation principle suggest its
potential for adapting and improving existing density-based
anomaly detection methods. While this work successfully
employed a contrastive method for latent encoding, future
research could explore alternative projection techniques to
optimize latent space separability and model performance.
R EFERENCES
[1]

F. Quan, X. Sun, H. Zhao, Y. Li, and G. Qin, “Detection of rotating
stall inception of axial compressors based on deep dilated causal
convolutional neural networks,” IEEE Trans. Autom. Sci. Eng., vol. 21,
no. 2, pp. 1235–1243, Apr. 2024.
[2] J. Fang et al., “A new particle swarm optimization algorithm for outlier
detection: Industrial data clustering in wire arc additive manufacturing,”
IEEE Trans. Autom. Sci. Eng., vol. 21, no. 2, pp. 1244–1257, Apr. 2024.
[3] D. Meli, “Explainable online unsupervised anomaly detection for cyberphysical systems via causal discovery from time series*,” in Proc. IEEE
20th Int. Conf. Autom. Sci. Eng. (CASE), Aug. 2024, pp. 4120–4125.
[4] M. Yao, D. Tao, P. Qi, and R. Gao, “Rethinking discrepancy
analysis: Anomaly detection via meta-learning powered dual-source
representation differentiation,” IEEE Trans. Autom. Sci. Eng., vol. 22,
pp. 8579–8592, 2025.
[5] V. Barnett et al., Assessment of Outliers in Statistical Data Analysis,
vol. 3. Hoboken, NJ, USA: Wiley, 1994.
[6] S. He, Z. Li, J. Wang, and N. N. Xiong, “Intelligent detection for
key performance indicators in industrial-based cyber-physical systems,”
IEEE Trans. Ind. Informat., vol. 17, no. 8, pp. 5799–5809, Aug. 2021.
[7] A. S. Raihan and I. Ahmed, “A Bi-LSTM autoencoder framework for
anomaly detection—A case study of a wind power dataset,” in Proc.
IEEE 19th Int. Conf. Autom. Sci. Eng. (CASE), Aug. 2023, pp. 1–6.
[8] S. Liu et al., “Time series anomaly detection with adversarial reconstruction networks,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 4,
pp. 4293–4306, Apr. 2023.
[9] L. Ruff et al., “A unifying review of deep and shallow anomaly
detection,” Proc. IEEE, vol. 109, no. 5, pp. 756–795, May 2021.
[10] Q. Zhou, S. He, H. Liu, J. Chen, and W. Meng, “Label-free multivariate
time series anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 36,
no. 7, pp. 3166–3179, Jul. 2024.
[11] H. Xu, Y. Wang, S. Jian, Q. Liao, Y. Wang, and G. Pang, “Calibrated
one-class classification for unsupervised time series anomaly detection,”
IEEE Trans. Knowl. Data Eng., vol. 36, no. 11, pp. 5723–5736, Nov.
2024.
[12] A. B. Nassif, M. A. Talib, Q. Nasir, and F. M. Dakalbab, “Machine
learning for anomaly detection: A systematic review,” IEEE Access,
vol. 9, pp. 78658–78700, 2021.
[13] G. Papamakarios, E. Nalisnick, D. J. Rezende, S. Mohamed, and
B. Lakshminarayanan, “Normalizing flows for probabilistic modeling
and inference,” J. Mach. Learn. Res., vol. 22, no. 57, pp. 1–64, 2021.
[14] L. Zhang et al., “Spatial–temporal graph conditionalized normalizing
flows for nuclear power plant multivariate anomaly detection,” IEEE
Trans. Ind. Informat., vol. 20, no. 11, pp. 12945–12958, Nov. 2024.
[15] X. Wang, Q. Kang, M. Zhou, L. Pan, and A. Abusorrah, “Multiscale drift
detection test to enable fast learning in nonstationary environments,”
IEEE Trans. Cybern., vol. 51, no. 7, pp. 3483–3495, Jul. 2021.
[16] A. Abanda, U. Mori, and J. A. Lozano, “A review on distance based time
series classification,” Data Mining Knowl. Discovery, vol. 33, no. 2,
pp. 378–412, Mar. 2019.
[17] X. Yao, R. Li, J. Zhang, J. Sun, and C. Zhang, “Explicit boundary guided
semi-push-pull contrastive learning for supervised anomaly detection,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jul. 2023,
pp. 24490–24499.

[18] S. Lee, T. Park, and K. Lee, “Soft contrastive learning for time series,”
in Proc. Int. Conf. Learning Represent., 2024, pp. 1–14.
[19] W. Cho, Y. Kim, and J. Park, “Hierarchical anomaly detection using a
multioutput Gaussian process,” IEEE Trans. Autom. Sci. Eng., vol. 17,
no. 1, pp. 261–272, Jan. 2020.
[20] K. Yamanishi and J.-I. Takeuchi, “A unifying framework for detecting
outliers and change points from non-stationary time series data,” in Proc.
8th ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining, 2002,
pp. 676–681.
[21] M. Li et al., “SA2E-AD: A stacked attention autoencoder for anomaly
detection in multivariate time series,” ACM Trans. Knowl. Discovery
Data, vol. 18, no. 7, pp. 1–15, Jun. 2024.
[22] M. A. Belay, A. Rasheed, and P. S. Rossi, “MTAD: Multiobjective
transformer network for unsupervised multisensor anomaly detection,”
IEEE Sensors J., vol. 24, no. 12, pp. 20254–20265, Jun. 2024.
[23] L. Dinh, D. Krueger, and Y. Bengio, “NICE: Non-linear independent
components estimation,” 2014, arXiv:1410.8516.
[24] B. L. Trippe and R. E. Turner, “Conditional density estimation with
Bayesian normalising flows,” 2018, arXiv:1802.04908.
[25] R. Li, Z. Liu, X. Zhu, L. Li, and X. Cao, “Detecting multivariate time
series anomalies with cascade decomposition consistency,” IEEE Trans.
Instrum. Meas., vol. 74, pp. 1–14, 2025.
[26] S. Bond-Taylor, A. Leach, Y. Long, and C. G. Willcocks, “Deep generative modelling: A comparative review of VAEs, GANs, normalizing
flows, energy-based and autoregressive models,” IEEE Trans. Pattern
Anal. Mach. Intell., vol. 44, no. 11, pp. 7327–7347, Nov. 2022.
[27] D. P. Kingma and M. Welling, “Auto-encoding variational Bayes,” 2013,
arXiv:1312.6114.
[28] I. J. Goodfellow et al., “Generative adversarial nets,” in Proc. Adv.
Neural Inf. Process. Syst., vol. 27, 2014, pp. 2672–2680.
[29] J. Ho, A. Jain, and P. Abbeel, “Denoising diffusion probabilistic models,”
in Proc. Adv. Neural Inf. Process. Syst., vol. 33, 2020, pp. 6840–6851.
[30] L. Dinh, J. Sohl-Dickstein, and S. Bengio, “Density estimation using
real NVP,” in Proc. Int. Conf. Learning Represent., 2017, pp. 1–12.
[31] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer:
Time series anomaly detection with association discrepancy,” 2021,
arXiv:2110.02642.
[32] B. Yu, Y. Yu, G. Xiang, and R. Lin, “Triple attention: An integrated
approach for interpretable anomaly detection in temporal and association
dimensions,” IEEE Trans. Instrum. Meas., vol. 73, pp. 1–12, 2024.
[33] H. Liu, W. Luo, L. Han, P. Gao, W. Yang, and G. Han, “Anomaly
detection via graph attention networks-augmented mask autoregressive
flow for multivariate time series,” IEEE Internet Things J., vol. 11,
no. 11, pp. 19368–19379, Jun. 2024.
[34] E. Dai and J. Chen, “Graph-augmented normalizing flows for anomaly
detection of multiple time series,” in Proc. Int. Conf. Learning Represent., 2022, pp. 1–12.
[35] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell. (AAAI),
May 2021, pp. 4027–4035.
[36] J. J. Downs and E. F. Vogel, “A plant-wide industrial process control
problem,” Comput. Chem. Eng., vol. 17, no. 3, pp. 245–255, Mar. 1993.
[37] J. Goh, S. Adepu, K. N. Junejo, and A. Mathur, “A dataset to support
research in the design of secure water treatment systems,” in Proc.
11th Int. Conf. Crit. Inf. Infrastruct. Secur. Cham, Switzerland: Springer,
2017, pp. 88–99.
[38] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric
dynamic thresholding,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discovery Data Mining, Jul. 2018, pp. 387–395.
[39] A. Abdulaal, Z. Liu, and T. Lancewicki, “Practical approach to asynchronous multivariate time series anomaly detection and localization,”
in Proc. 27th ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug.
2021, pp. 2485–2494.
[40] L. Ruff et al., “Deep semi-supervised anomaly detection,” 2019,
arXiv:1906.02694.
[41] L. Ruff et al., “Deep one-class classification,” in Proc. Int. Conf. Mach.
Learn., 2018, pp. 4393–4402.
[42] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Disc. Data Min., 2020,
pp. 3395–3404.
[43] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Represent., 2018,
pp. 1–14.
[44] Z. Xu, A. Zeng, and Q. Xu, “FITS: Modeling time series with 10k
parameters,” in Proc. Int. Conf. Learn. Represent., 2024.

LIU et al.: ADAPTIVE LATENT DISTRIBUTION MODELING FOR INDUSTRIAL TIME SERIES ANOMALY DETECTION

[45] B. Li et al., “CrossAD: Time series anomaly detection with cross-scale
associations and cross-window modeling,” in Proc. 39th Annu. Conf.
Neural Inf. Process. Syst., 2025, pp. 1–14.
[46] D. A. Dickey and W. A. Fuller, “Distribution of the estimators for
autoregressive time series with a unit root,” J. Amer. Stat. Assoc., vol. 74,
no. 366, pp. 427–431, Jun. 1979.

Yu Liu was born in Hubei, China, in 1997. He
received the B.Eng. degree in automatic control from
China University of Petroleum, Shandong, China,
in 2019. He is currently pursuing the Ph.D. degree
with the School of Electronics and Information Engineering, Tongji University, Shanghai, China. His
main research interests include anomaly detection,
complex event recognition, and control of discrete
event systems and cyber-physical systems.

Yifan Song received the B.Eng. degree in mechanical design, manufacturing and automation from
China Agricultural University, Beijing, China, in
2019. He is currently pursuing the Master of
Engineering degree in electronic and information
engineering with the School of Electronics and Information Engineering, Tongji University, Shanghai,
China. His main research interests include time
series anomaly detection.

Shaolong Shu (Senior Member, IEEE) received the
B.Eng. degree in automatic control and the Ph.D.
degree in control theory and control engineering
from Tongji University, Shanghai, China, in 2003
and 2008, respectively. Since July 2008, he has been
with the School of Electronics and Information Engineering, Tongji University, where he is currently a
Full Professor. From August 2007 to February 2008
and from April 2014 to April 2015, he was a Visiting Scholar with Wayne State University, Detroit,
MI, USA. His main research interests include state
estimation and control of discrete event systems and cyber-physical systems.

7907

Feng Lin (Life Fellow, IEEE) received the B.Eng.
degree in electrical engineering from Shanghai Jiao
Tong University, Shanghai, China, in 1982, and the
M.A.Sc. and Ph.D. degrees in electrical engineering from the University of Toronto, Toronto, ON,
Canada, in 1984 and 1988, respectively. He was
a Post-Doctoral Fellow with Harvard University,
Cambridge, MA, USA, from 1987 to 1988. Since
1988, he has been with the Department of Electrical
and Computer Engineering, Wayne State University,
Detroit, MI, USA, where he is currently a Professor.
He authored a book entitled Robust Control Design: An Optimal Control
Approach. His current research interests include discrete event systems, hybrid
systems, neural networks, robust control, and their applications in alternative
energy, biomedical systems, machine learning, and automotive control. He
has co-authored a paper that received the George Axelby Outstanding Paper
Award from the IEEE Control Systems Society. He was an Associate Editor
of IEEE T RANSACTIONS ON AUTOMATIC C ONTROL.

Jun Wang (Senior Member, IEEE) received the
Ph.D. degree in control engineering from the University of Leeds, Leeds, U.K., in 2003. He was
the General Chair of IAVSD 2025, organized by
the International Association for Vehicle System
Dynamics. He is currently a Professor of control engineering with Tongji University, Shanghai,
China. He is the Director of the Enterprise Digital Technology Engineering Research Center of
the Ministry of Education of China. His research
interests include smart sensing, intelligent control,
and autonomous vehicles. He is a Board Member of Shanghai Association of
Automation and Shanghai Association of Artificial Intelligence.

Yafeng Guo received the B.Sc. degree in automatic
control and the M.Sc. degree in control theory
and control engineering from Xiamen University,
in 2001 and 2004, respectively, and the Ph.D.
degree in control theory and control engineering
from Shanghai Jiao Tong University, in 2009. In
2009, he joined the Department of Control Science and Engineering, Tongji University. He is
currently an Associate Professor with Tongji University. His research interests include principle-guided
neural networks, autonomous vehicle, and stochastic
systems.
PAPER_TEXT
