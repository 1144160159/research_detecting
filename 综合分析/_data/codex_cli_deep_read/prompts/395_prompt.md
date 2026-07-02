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
# [395] Deep Multimanifold Transformation-Based Multivariate Time Series Fault Detection
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
编号：395
题名：Deep Multimanifold Transformation-Based Multivariate Time Series Fault Detection
年份：2025
DOI：10.1109/tnnls.2025.3584988
来源：IEEE Transactions on Neural Networks and Learning Systems
PDF：paper/10.1109_TNNLS.2025.3584988.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：无
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\395.txt
- 原始字符数：53877
- 本次发送字符数：53877
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

18397

Deep Multimanifold Transformation-Based
Multivariate Time Series Fault Detection
Hong Liu , Member, IEEE, Xiuxiu Qiu , Yiming Shi, Miao Xu, Zelin Zang , Member, IEEE,
and Zhen Lei , Fellow, IEEE

Abstract—Unsupervised fault detection in multivariate time
series (MTS) plays a vital role in ensuring the stable operation of
complex systems. Traditional methods often assume that normal
data follow a single Gaussian distribution and identify anomalies
as deviations from this distribution. However, this simplified
assumption fails to capture the diversity and structural complexity of real-world time series, which can lead to misjudgments
and reduced detection performance in practical applications. To
address this issue, we propose a new method that combines a
neighborhood-driven data augmentation strategy with a multimanifold representation learning framework. By incorporating
information from local neighborhoods, the augmentation module
can simulate contextual variations of normal data, enhancing
the model’s adaptability to distributional changes. In addition, we design a structure-aware feature learning approach
that encourages natural clustering of similar patterns in the
feature space while maintaining sufficient distinction between
different operational states. Extensive experiments on several
public benchmark datasets demonstrate that our method achieves
superior performance in terms of both accuracy and robustness, showing strong potential for generalization and real-world
deployment.
Index Terms—Data augmentation, fault detection, multivariate
time series, unsupervised soft contrastive learning (CL).

Received 29 July 2024; revised 13 February 2025 and 4 June 2025;
accepted 25 June 2025. Date of publication 11 August 2025; date of current
version 9 October 2025. This work was supported in part by the “Pioneer”
and “Leading Goose” Research and Development Program of Zhejiang under
Grant 2024C01140, in part by the Key Research and Development Program
of Hangzhou under Grant 2023SZD0073, in part by Beijing Natural Science
Foundation under Grant L221013, and in part by the InnoHK Program.
(Corresponding author: Zelin Zang.)
Hong Liu is with the School of Information and Electrical Engineering,
Academy of Edge Intelligence, Hangzhou City University, Hangzhou 310015,
China.
Xiuxiu Qiu is with the College of Information Engineering, Zhejiang
University of Technology, Hangzhou 310012, China.
Yiming Shi is with the Institute of Cyber-Systems and Control, Zhejiang
University, Hangzhou 310027, China.
Miao Xu is with the Centre for Artificial Intelligence and Robotics (CAIR),
HKISI-CAS, Hong Kong, China.
Zelin Zang is with the School of Engineering, Westlake University,
Hangzhou 310015, China, and also with the Centre for Artificial Intelligence and Robotics (CAIR), HKISI-CAS, Hong Kong, China (e-mail:
zangzelin@westlake.edu.cn).
Zhen Lei is with the Centre for Artificial Intelligence and Robotics (CAIR),
HKISI-CAS, Hong Kong, China, also with the State Key Laboratory of
Multimodal Artificial Intelligence Systems (MAIS), Institute of Automation,
Chinese Academy of Sciences (CASIA), Beijing 100190, China, and also
with the School of Artificial Intelligence, University of Chinese Academy of
Sciences (UCAS), Beijing 100049, China (e-mail: zhen.lei@ia.ac.cn).
This article has supplementary downloadable material available at
https://doi.org/10.1109/TNNLS.2025.3584988, provided by the authors.
Digital Object Identifier 10.1109/TNNLS.2025.3584988

I. I NTRODUCTION

U

N SUPERVISED fault detection [15], [23] in multivariate time series (MTS) has become increasingly vital
in both academic research and practical domains, especially
within industrial environments and the management of largescale systems [21], [29], [36]. By eliminating the need for
labeled data, it enables early identification of anomalies and
incipient faults [6], [38], which is crucial for minimizing maintenance overhead and averting potential system failures [17].
This capability makes it an indispensable tool for real-time
monitoring and predictive maintenance in scenarios where
labeled samples are scarce or entirely unavailable [40].
To address this challenge, a wide range of approaches
have been explored, from classical statistical methods to
modern deep learning-based models [32], [37]. Despite the
notable progress made in recent years [20], most existing
techniques still exhibit unsatisfactory detection performance in
practical applications, characterized by frequent false positives
and missed anomalies (see Tables I and II). This is largely
due to the restrictive assumptions imposed during modeling,
often necessitated by the absence of supervision. A prevailing
strategy is to model normal behavior as a Gaussian distribution
and to flag deviations as anomalies [39], as illustrated in
Fig. 1(a). While computationally convenient, such assumptions
fail to capture the intrinsic diversity and nuanced dynamics of
real-world systems.
In reality, both normal and anomalous behaviors often
comprise multiple heterogeneous subpatterns, each exhibiting
distinct temporal and structural traits [Fig. 1(b)]. Relying on
a single Gaussian model obscures these internal variations,
leading to suboptimal representations and a reduced capacity
to detect subtle deviations [23]. This oversimplification not
only impairs the model’s ability to capture gradual state
transitions but also undermines robustness in highly variable
environments [10], [25]. Consequently, there is a pressing
need to move beyond Gaussian-centric assumptions and adopt
more expressive modeling paradigms capable of characterizing
complex, multimodal system behaviors.
To address the limitations caused by the oversimplified
Gaussian distribution assumption, we propose an unsupervised
framework, termed deep multimanifold transformation for
fault detection (DMTFD). Unlike prior methods that characterize normal states with a single Gaussian distribution
[39], DMTFD adopts a multimanifold assumption, which

2162-237X © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

18398

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

TABLE I
FAULT D ETECTION P ERFORMANCE OF AUROC ON F IVE P UBLIC DATASETS . W E C OMPARE THE P ERFORMANCE OF D IFFERENT M ETHODS U SING
A C ONSISTENT W INDOW S IZE (DMTFD) W ITH O UR O PTIMAL R ESULTS O BTAINED T HROUGH VARYING W INDOW S IZES (DMTFD*) TO
S HOWCASE THE M AXIMUM P OTENTIAL . T HE B EST R ESULTS A RE G IVEN IN B OLD

TABLE II
A NOMALY D ETECTION P ERFORMANCE OF PR ON F IVE P UBLIC DATASETS . W E C OMPARE THE P ERFORMANCE OF D IFFERENT M ETHODS U SING
A C ONSISTENT W INDOW S IZE (DMTFD) W ITH O UR O PTIMAL R ESULTS O BTAINED T HROUGH VARYING W INDOW S IZES (DMTFD*) TO
S HOWCASE THE M AXIMUM P OTENTIAL . T HE B EST R ESULTS A RE G IVEN IN B OLD

USD

Fig. 1. Motivation of DMTFD. (a) Existing methods rely on Gaussian
assumptions and fail to capture complex latent structures with multiple
substates. (b) Our proposed DMTFD introduces a multimanifold assumption
to better model state variations and improve fault detection accuracy.

ones. To construct a meaningful representation space under
this assumption, we introduce a neighbor-aware augmentation
strategy that generates context-consistent variants of each
sample [18] and adopt a softened similarity constraint to
gently pull semantically close instances. This design alleviates
the rigidity of binary contrastive signals and supports more
nuanced anomaly boundary modeling [41].
Comprehensive experiments show that DMTFD significantly outperforms existing methods in both AUC
and precision-recall (PR) metrics. On benchmark datasets,
DMTFD achieves consistently lower false alarm rates and
higher detection accuracy.
Furthermore, our visualization analysis supports the plausibility of the multi-Gaussian assumption and illustrates how
soft contrastive learning (CL) effectively captures underlying
substate structures.

acknowledges the intrinsic diversity of normal operating conditions across different system states [see Fig. 1(b)].
Concretely, DMTFD leverages a multimanifold transformation module that maps MTS into a latent space where
heterogeneous local patterns are better disentangled and
aligned. This transformation enables the model to preserve
fine-grained distinctions between submanifolds of normal
behaviors while amplifying their deviation from anomalous

1) Multimanifold Modeling of Operational States: We
break away from the conventional single-Gaussian
assumption and adopt a multimanifold view that reflects
the heterogeneity of both normal and abnormal conditions. This insight leads to a more faithful and flexible
modeling of system behaviors.
2) New Framework for Unsupervised Representation:
We propose a novel framework that integrates

LIU et al.: DEEP MULTIMANIFOLD TRANSFORMATION-BASED MTS FAULT DETECTION

neighbor-based data augmentation and loss function to
construct a smooth and discriminative latent space.
3) Superior Empirical Performance Across Benchmarks:
Our method achieves over 5% improvement in detection
metrics compared to existing baselines, demonstrating
strong robustness and generalization in real-world industrial scenarios.
II. R ELATED W ORK
A. Time Series Anomaly Detection
In time series anomaly detection, one-class classification (OCC) methods—such as USAD [4] and DAEMON
[8]—typically assume access to purely normal data during
training [5], [16]. GANF [9] employs graph neural networks (GNNs) for anomaly detection in MTS. MTGFlow
[39] combines dynamic graphs with normalizing flows, while
MTGFlow-cluster [40] further boosts accuracy by clustering
entities. AnomalyLLM [22] leverages large language models
for knowledge distillation, using prototypical signals and synthetic anomalies to achieve an improvement on UCR datasets
across 15 benchmarks. PeFAD [31] introduces PLM-based
parameter-efficient federated learning with anomaly masking
and synthetic distillation, improving performance by up to
28.74%. Graph-MoE [15] enhances GNN-based detection via
expert mixtures and memory routers, effectively utilizing hierarchical features. In addition, prior work USD [23] proposes
a CL framework tailored for MTS fault detection, addressing
limitations of hard contrastive loss in the presence of viewlevel noise. Building upon this, the present work introduces
a multimanifold transformation strategy and a generalized
similarity modeling approach, enabling more expressive representations and significantly improving detection performance
and robustness across benchmarks.

B. Contrastive Learning and SoftCL
Soft CL (SoftCL) [33], [35] and deep manifold learning [19], [24] represent two advanced methodologies in the
domain of machine learning, particularly in the tasks of
unsupervised learning and representation learning. These techniques aim to leverage the intrinsic structure of the data
to learn meaningful and discriminative features. At its core,
SoftCL [28], [33], [35] is an extension of the CL framework
[7], [13], [14], which aims to learn representations by bringing
similar samples closer and pushing dissimilar samples apart in
the representation space. However, SoftCL introduces a more
nuanced approach by incorporating the degrees of similarity
between samples into the learning process, rather than treating
similarity as a binary concept. This is achieved through the
use of soft labels or continuous similarity scores, allowing the
model to learn richer and more flexible representations. The
softness in the approach accounts for the varying degrees of
relevance or similarity among data points, making it particularly useful in tasks where the relationship between samples is
not strictly binary or categorical, such as in semi-supervised
learning or in scenarios with noisy labels.

18399

III. P RELIMINARY
Normalizing flow is an unsupervised density estimation
approach to map the original distribution to an arbitrary target
distribution by a stack of invertible affine transformations.
When density estimation on original data distribution X is
intractable, an alternative option is to estimate z density on
target distribution Z. Specifically, suppose a source sample
x ∈ RD ∼ X and a target distribution sample z ∈ RD ∼ Z.
Bijective invertible transformation Fθ aims to achieve one-toone mapping z = fθ (x) from X to Z. According to the change
of variable formula, we can get
ˇ
ˇ
ˇ
∂ fθ ˇˇ
ˇ
(1)
PX (x) = PZ (z) ˇdet T ˇ .
∂x
Benefiting from the invertibility of mapping functions and
tractable Jacobian determinants | det(∂ fθ /∂xT )|, the objective
of flow models is to achieve ẑ = z, where ẑ = fθ (x).
Flow models are able to achieve more superior density
estimation performance when additional conditions C are input
[3]. Such a flow model is called conditional normalizing flow,
and its corresponding mapping is derived as z = fθ (x|C).
Parameters θ of fθ are updated by maximum likelihood estimation (MLE)
ˇ

ˇ
ˇ
∂ fθ ˇˇ
∗
ˇ
θ = arg max log (PZ ( fθ (x|C)) + log ˇdet T ˇ
. (2)
∂x
θ

IV. M ETHODOLOGY
A. Notation and Problem Definition
Consider an MTS dataset X. The dataset encompassing
K entities, each with L observations, is denoted as X =
(x1 , x2 , . . . , xK ), where each xk ∈ RL . Z-score normalization
is employed to standardize the time series data across different entities. A sliding window approach, with a window
size of T and a stride size of S , is utilized to sample the
normalized MTS, generating training samples xc , where c
denotes the sampling count and xc represents the segment
x[cS −T /2]:[cS +T /2] .
The objective of unsupervised fault detection is to identify
segments xc within X exhibiting anomalous behavior. This
process operates under the premise that the normal behavior of
X is known, and any significant deviation from this behavior
is considered abnormal. Specifically, abnormal behavior is
characterized by its occurrence in low-density regions of the
normal behavior distribution, defined by a density threshold
θ < ρ(normal behavior). The task of unsupervised fault detection in MTS can thus be formalized as identifying segments
xc where ρ(xc ) < θ.
Definition 1: (Supervised Fault Detection in MTS): Let
N
D = {(xc , yc )}i=1
be a labeled dataset for an MTS, where each
c
segment x is annotated with a label yc ∈ {0, 1}, indicating normal (0) or abnormal (1) behavior. Supervised fault detection
aims to learn a function f : RL → {0, 1} that can accurately
classify new, unseen segments xnew as normal or abnormal
based on learned patterns of faults.
Definition 2: (Unsupervised Fault Detection under Gaussian
Assumption): In the Gaussian assumption context, unsupervised fault detection in an MTS operates on the premise that

18400

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

Fig. 2. Overview of the proposed DMTFD framework. (a) Temporal sequences x and x+ are processed via RNN to capture temporal dynamics, followed by
a GNN to model interentity dependencies, yielding embeddings y. A SoftCL head maps y to transformed features c, which are then used for density modeling
via a flow-based generative network. (b) SCL head helps cluster similar samples and separate dissimilar ones in the feature space.

the distribution of normal behavior can be modeled using a
Gaussian distribution. Anomalies are identified as segments
xc that fall in regions of low probability under this Gaussian
model, specifically where ρ(xc ) < θ, with θ being a predefined
density threshold.
Definition 3: (Unsupervised Fault Detection under MultiGaussian Assumption): Under the multi-Gaussian assumption,
unsupervised fault detection recognizes that the distribution of
normal behavior in an MTS may encompass multiple modes,
each fitting a Gaussian model. This assumption allows for a
more nuanced detection of anomalies, which are segments
xc that do not conform to any of the modeled Gaussian
distributions of normal behavior, detected through a composite
density threshold criterion ρ(xc ) < θ.

B. Neural Network Structure of DMTFD
The core idea of DMTFD is to learn precise and discriminative latent representations by integrating data augmentation
with SoftCL. As illustrated in Fig. 2, the DMTFD framework jointly leverages a recurrent neural network (RNN)
R(·; θ), a GNN G(·; φ), and a normalizing flow model F(·; α)
to effectively model the temporal patterns, relational structures, and distributional properties of MTS data for fault
detection.
1) RNN-GNN-Flow Architecture: To jointly capture temporal dynamics, interentity dependencies, and density patterns,
we adopt an RNN-GNN-Flow architecture. Given the multivariate input at time window c, denoted as xc , we first
compute the temporal encoding gc = R(xc ; θ) using an RNN
parameterized by θ; a GNN with parameters φ then produces
the spatiotemporal embedding yc = G(gc ; φ); and finally, a normalizing flow with parameters α estimates the log-likelihood
score `c = F(yc ; α), which is used to detect anomalies—where
low likelihood indicates high abnormality.

2) Manti-Manifold Transformation Head (MTH): To
enhance the discriminative quality of the learned representations, we introduce a multimanifold transformation head,
implemented as a multilayer perceptron (MLP) H(·; ω). This
module receives the spatiotemporal embedding yc from the
GNN as input and projects it into a latent feature space
optimized for CL zc = H (yc ; ω), where ω denotes the learnable
parameters of the MLP and zc is the contrastive representation
corresponding to time window c. The goal of this module is
to enforce semantic alignment between similar instances while
ensuring separation among dissimilar ones. This is achieved
via a soft contrastive loss, which penalizes embeddings of
positive pairs (semantically similar samples) that are far apart
and encourages larger distances for negative pairs (semantically dissimilar samples) that are too close. Unlike hard
contrastive formulations that impose strict binary similarity,
the soft version allows for graded similarity relationships,
thereby providing a smoother optimization landscape and
improving robustness to intraclass variability.

C. MLE Loss and Data Augmentation
A key objective of the DMTFD framework is to accurately
identify abnormal behaviors by modeling the underlying distribution of normal operational data. To this end, we employ
MLE as the training criterion for the flow-based density
estimation module. The core motivation behind this design is
to encourage the model to assign high likelihoods to normal
patterns while assigning low likelihoods to anomalous deviations, thus enabling precise and fine-grained fault detection.
Formally, given the contrastive representation zc for time
window c, the normalizing flow transformation f (·; α) maps
it into a latent variable ẑc = f (zc ; α) that follows a known
target distribution (typically standard Gaussian with mean µ

LIU et al.: DEEP MULTIMANIFOLD TRANSFORMATION-BASED MTS FAULT DETECTION

and identity covariance). The MLE loss is then defined as
ˇ 
 ˇ
N 
ˇ
∂ fα ˇˇ
1 X 1 c
(3)
LMLE =
− kẑ − µk22 + log ˇˇdet
N
2
∂zc ˇ
c=1

where N is the number of time windows and µ is the mean of
the target Gaussian distribution Z. The first term encourages
ẑc to match the target distribution, while the second term—i.e.,
the log-determinant of the Jacobian—ensures that the flow
transformation remains invertible and probability-preserving.
By optimizing LMLE , the flow model learns to model the
density landscape of normal patterns precisely. At inference
time, data points with significantly low log likelihoods under
the learned distribution are flagged as anomalies, enabling
accurate and interpretable fault detection across diverse temporal and relational contexts.
Data augmentation is crucial for improving the model’s
ability to generalize beyond the training data by artificially expanding the dataset’s size and diversity [34]. Our
methodology incorporates two primary strategies: neighborhood discovery and linear interpolation.
1) Neighborhood Discovery: This technique focuses on
leveraging the local structure of the data to generate new,
plausible data points that conform to the existing distribution.
For each data point xc , we define its neighborhood N(xc ) using
a distance metric d(·, ·), such as the Euclidean distance. The
c
neighborhood consists of points xnew
that meet the criterion

c
d xc , xnew
≤
(4)
where  is a predetermined threshold defining the
neighborhood’s radius. This method captures the local
density of the data, enabling the generation of new samples
within these densely populated areas and thus enhancing
the dataset with variations that align with the original data
distribution.
2) Data Augmentation by Linear Interpolation: Data
augmentation strategy augments the dataset by creating intermediate samples between existing data points. For two points
c
c
xc and xnew
, a new sample xnew
is formulated as
c
c
= αxc + (1 − α) xnew
xnew

(5)

where α is a random coefficient sampled from a uniform
distribution, α ∼ U(0, 1). This approach facilitates a smooth
transition between data points, effectively bridging gaps in the
data space and introducing a continuum of sample variations.
By interpolating between points either within the same neighborhood or across different neighborhoods, we substantially
enhance the dataset’s diversity and coverage, providing the
model with a more comprehensive set of examples for training.
D. MML With Data Augmentation
In data-augmentation-based CL, the task is framed as a
binary classification problem over pairs of samples. Positive
pairs, drawn from the joint distribution (xc1 , xc2 ) ∼ P xc1 ,xc2 ,
are labeled as Hc1,c2 = 1, whereas negative pairs, drawn from
the product of marginals (xc1 , xc2 ) ∼ P xc1 P xc2 , are labeled as
Hck = 0. The goal of CL is to learn representations that

18401

maximize the similarity between positive pairs and minimize
it between negative pairs, utilizing the InfoNCE loss
NK
LCL (xc1 , xc2 , {xcn }cn=1
)=



c1 T c2
exp z z
exp S zc1 ,zc2
 = −log PN

− log P

K
c1
NK
c1 Tz
k=1 exp S z ,zcn
cn
k=1 exp z

(6)

where (xc1 , xc2 ) constitutes a positive pair and (xc1 , xcn ) a
negative pair, with zc1 , zc2 , and zcn being the embeddings of
xc1 , xc2 , and zcn , respectively, and NK representing the number
of negative pairs. The similarity function S (zc1 , zc2 ) is typically defined using cosine similarity. This method effectively
enhances the model’s discriminative power by distinguishing
between closely related (positive) and less related (negative)
samples within the augmented data space.
The conventional CL (CCL) loss is structured around a
single positive sample contrasted against multiple negatives.
To refine this, we have restructured the CCL loss into a more
nuanced form that utilizes labels for positive and negative
samples, denoted by Hc1,c2 . Detailed explanations of this
transformation from (6) and (7) are available in Supplementary
Material A.
NK
LCCL (xc1 , {xc2 }c2=1
)
X˚

Hc1,c2 log Qc1,c2 + 1 − Hc1,c2 log Q̇c1,c2
=−

(7)

j=1

where Hc1,c2 indicates if samples c1 and c2 have been
augmented from the same source. Hc1,c2 = 1 signifies a
positive pair (xc1 , xc2 ), and Hc1,c2 = 0 indicates a negative
pair. The term Qc1,c2 = exp(S (zc1 , zc2 )) represents the density
ratio, as defined and computed by the backbone network.
To enhance robustness against view-level noise introduced by
data augmentation, we propose the multimanifold loss (MML).
Unlike conventional contrastive losses that treat pairwise labels
as binary constants, MML introduces soft similarity-based
weights, enabling the model to downweight uncertain or noisy
samples during training.
Given an anchor sample xc1 and a set of associated samples
c2 NK
{x }c2 =1 , the MML loss is defined as
LMML (xc1 , {xc2 }) =
−

NK
X




Pc1 ,c2 log Qc1 ,c2 + 1 − Pc1 ,c2 log 1 − Qc1 ,c2

(8)

c2 =1

where Pc1 ,c2 is the soft label (weight) reflecting the similarity in
input space and Qc1 ,c2 denotes the similarity in the contrastive
latent space. They are defined as
(
eα · κ (yc1 , yc2 ) if Hc1 ,c2 = 1
Pc1 ,c2 =
κ (yc1 , yc2 )
otherwise
Qc1 ,c2 = κ (zc1 , zc2 )

(9)

where Hc1 ,c2 ∈ {0, 1} indicates whether xc2 is a positive pair of
xc1 , α ∈ [0, 1] is a confidence prior that emphasizes positive
pairs, and κ(·, ·) is a similarity kernel.
To improve robustness against augmentation noise and
sample-level variability, we adopt a generalized Gaussian

18402

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

Fig. 3. ROC and PR plots of four datasets. The ROC and PR curves of the SWaT, WADI, PSM, and MSL datasets are shown. The ROC curves illustrate
the tradeoff between true positive rate and false positive rate, while the PR curves show the tradeoff between precision and recall. The performance of our
method is compared against SOTA methods, demonstrating the effectiveness of our approach.

kernel κβ (·, ·) as the similarity function in MML. Compared
to the standard Gaussian kernel, the generalized Gaussian
provides a tunable shape parameter that allows for heavier
tails when needed, enabling the model to assign meaningful
similarity scores even to moderately distant pairs. The kernel
is defined as

β !
ka − bk2
β
κ (a, b) = exp −
(10)
σ
where β > 0 controls the shape of the decay (with β = 2
reducing to a Gaussian kernel and β < 2 producing heavier
tails) and σ is a scale parameter. This formulation makes the
loss function more tolerant to view-level noise and nonuniform
sample structures, leading to smoother gradients and improved
generalization under multimanifold distributions. Unlike USD
[23], which relies on a fixed Gaussian assumption and sharp
contrastive margins, our generalized kernel formulation offers
adaptive flexibility across manifold structures and improves
tolerance to cross-view variation. Detailed comparisons and
analyses are provided in Supplementary Material A.
E. Optimization Objectives
The entire DMTFD framework, encompassing the RNN,
GNN, and FLOW models, is optimized jointly through MLE
to ensure effective anomaly detection. The joint optimization
process is formulated as follows:
LDMTFD = LMLE + LMML

(11)

where LMLE is the MLE loss and LMML is the MML loss. The
MLE loss is designed to maximize the likelihood of observing
the transformed data points ẑi under the model, while the
MML loss is designed to enhance the model’s sensitivity to
subtle differences between normal and abnormal patterns. By
embedding these mathematical formulations into each step of

the DMTFD framework, we ensure a rigorous approach to
modeling and detecting anomalies in MTS data, setting a new
standard for unsupervised fault detection in complex systems.
V. E XPERIMENTS
A. Dataset Information and Implementation Details
Datasets Information: We evaluate DMTFD on six widely
used MTS fault detection datasets (Table A-1 in the Supplementary Material). SWaT [11] and WADI [2] are collected
from water treatment and distribution testbeds, simulating
industrial cyberattacks with labeled anomalies. PSM [1]
contains server metrics from eBay, used to detect system
performance anomalies. MSL [16] provides telemetry from
NASA’s Curiosity rover for space mission anomaly detection.
SMD [27] is from a large-scale server farm and captures
system behavior across multiple machines; we report average
results and ensure that test sets include anomalies via fixed
random seeds. SMAP is a NASA dataset [16] that contains
data from a satellite’s attitude control system, used for detecting anomalies in space missions. All datasets are standard in
OCC for time series anomaly detection.
1) Dataset Split and Preprocessing: In our experimental
setup, we adhere to the dataset configurations used in the
GANF study [9]. MTGFlow [39] and MTGFlow Cluster [40].
Specifically, for the SWaT dataset, we partition the original
testing data into 60% for training, 20% for validation, and
20% for testing. For the other datasets, the training partition
comprises 60% of the data, while the test partition contains the
remaining 40%. The training data are used to train the model,
while the validation data are used to tune hyperparameters and
the test data are used to evaluate the model’s performance.
The datasets are preprocessed to remove missing values and
normalize the data to a range of [0, 1]. The data are then
divided into fixed-length sequences, with a window size of 60

LIU et al.: DEEP MULTIMANIFOLD TRANSFORMATION-BASED MTS FAULT DETECTION

18403

Fig. 4. Violin plot of AUROC scores on different training splits. The x-axis represents the training split ratio, and the y-axis represents the AUROC scores. The
DMTFD method consistently outperforms the baseline methods (MTGFLOW) across different training splits, demonstrating its robustness and effectiveness
in anomaly detection tasks.

Fig. 5. Visualization of multisubclass data distributions. (a) t-SNE visualization of embedding of DMTFD on SWAT datasets. The color shows the different
states of the data. Multiple clusters can be seen in the representation, which is consistent with the multiple manifold assumption of this article. The normal
and abnormal states are not a single cluster but can be divided into separate subclusters. (b) Heatmaps of individual data point, each row in the heatmap is
the index number of the time, and each column is the index number of the sensor. We selected four subclusters, and two samples from each cluster were
randomly selected for presentation. The similarity of samples within subclusters and the difference of samples between subclusters are illustrated.

and a stride of 10. The window size determines the number of
time steps in each sequence, while the stride determines the
step size between each sequence. The data are then fed into
the model for training and evaluation.
2) Implementation Details: For all datasets, we set the
window size to 60–80 and the stride size to 10–30. All
experiments were run for 400–600 epochs and executed using
PyTorch 2.2.1 on an NVIDIA RTX 3090 24GB GPU. Additional specific parameters can be found in the Supplementary
Material.

representation collapse. DeepSAD [26] is a semi-supervised
method that detects anomalies via entropy differences in latent
distributions. USAD [4] employs adversarially trained autoencoders for unsupervised time series anomaly detection. GANF
[9] enhances normalizing flows using Bayesian networks to
model interseries dependencies. MTGFlow [39] and MTGFlow
Cluster [40] utilize dynamic graph structure learning and
entity-aware flows for fine-grained density estimation, with the
latter introducing clustering for improved accuracy.
C. Fault Detection Performance on Five Benchmark Dataset

B. Evaluation Metric and Baselines Methods
Following prior work, DMTFD performs window-level
anomaly detection, where a window is labeled anomalous if
it contains any anomalous point. We evaluate performance
using two metrics: area under the receiver operating characteristic (AUROC), which measures overall discriminative ability
across thresholds, and AUPRC, which is more informative
under class imbalance, capturing the tradeoff between precision and recall.
1) Baselines: We compare DMTFD with several state-ofthe-art (SOTA) anomaly detection methods. DROCC [12] is a
robust OCC method assuming locally linear manifolds to avoid

First, we discuss the performance advantages of the
DMTFD method by comparing results on five common benchmarks. We list the results for the AUROC and AUPRC metrics
in Tables I and II, where the numbers in parentheses represent
the variance from five different seed experiments. In Tables I
and II, the results of DROCC, DeepSAD, USAD, DAGMM,
GANF, and MTGFlow are from the article [39].1 The results of
MTGFlow Cluster are from [40].2 We report on two variants
of DMTFD: one (DMTFD) uses the same hyperparameters
across all experiments and the other (DMTFD*) involves
1 https://github.com/zqhang/MTGFLOW
2 https://github.com/zqhang/MTGFLOW

Cluster

18404

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

TABLE III
A BLATION S TUDY. AUROC C OMPARISON ON F OUR DATASETS (SWAT,
WADI, PSM, AND MSL). T HE B EST R ESULTS A RE G IVEN IN B OLD .
T HE R ESULTS A RE AVERAGED OVER F IVE RUNS , AND THE
S TANDARD D EVIATION I S S HOWN IN PARENTHESES

Fig. 6. Point plot of the anomalies predicted outputs of MTGFLOW and
proposed DMTFD. The x-axis represents the anomaly index, and the y-axis
represents the log likelihood of the anomaly. Anomalous ground truths are
marked by a red background. This indicates that DMTFD is able to detect
anomalies more accurately and in a timely manner.

hyperparameter tuning specific to each target dataset. The
best results are highlighted in bold. To visualize the benefits
of DMTFD performance, the ROC and PR curves on four
datasets are shown in Fig. 3. In the ROC and PR curves,
the DMTFD method consistently outperforms the baseline
methods, demonstrating its robustness and effectiveness in
anomaly detection tasks.
1) Performance Improvement: In terms of performance
improvements, as shown in Tables I and II, the DMTFD
method shows significant enhancements compared to SOTA
methods. We compare the performance of different methods
using a consistent window size (DMTFD) with our optimal
results obtained through varying window sizes (DMTFD*)
to showcase the maximum potential. The best results are
shown in bold. These improvements are evident across both
PR and AUC curves, particularly on the SWAT dataset
with a 5.4% increase in AUROC and a 7.7% increase
in AUPRC, and on the MSL dataset with a 6% increase
in AUROC and a 7.0% increase in AUPRC. On average, there is a 4.1% increase in AUROC performance and
a 7.0% increase in AUPRC performance. The consistent
improvements in both AUROC and AUPRC indicate that the
DMTFD method has enhanced performance across multiple
aspects.
2) Stability Improvement: As shown in Tables I and II
and Fig. 3, the stability of the DMTFD method is also
noteworthy, exhibiting lower variance across all test datasets
compared to traditional methods. This indicates that the
DMTFD method is more robust and less sensitive to random
initialization, making it a reliable choice for anomaly detection
tasks.
3) Performance Potential: Furthermore, by comparing the
results of DMTFD and DMTFD*, we find that conducting
hyperparameter searches for each dataset can significantly
boost the model performance. This suggests that our method
has good hyperparameter adaptability and considerable potential for further performance enhancements.
4) Additional Results on Difference Train/Validation Splits:
To further investigate the influence of anomaly contamination
rates, we vary training splits to adjust anomalous contamination rates. For all the abovementioned datasets, the training
split increases from 60% to 80% with 5% stride. We present an

average result over five runs in Fig. 4. Although the anomaly
contamination ratio of training dataset rises, the anomaly
detection performance of MTGFlow remains at a stable high
level. This indicates that the proposed DMTFD method is
robust to the anomaly contamination ratio of the training
dataset.
D. Visualization of Multisubclass Data Distributions
To further investigate the effectiveness of the DMTFD
method, we visualize the multisubclass data distributions on
the SWAT dataset. As shown in Fig. 5, the t-SNE visualization of the embedding of DMTFD on SWAT datasets
reveals multiple clusters, consistent with the multiple manifold assumption of this article. The normal and abnormal
states are not a single cluster but can be divided into separate subclusters. The heatmaps of individual data points
further illustrate the similarity of samples within subclusters
and the differences between samples in different subclusters.
This visualization demonstrates the ability of the DMTFD
method to capture the diverse patterns present in both normal and abnormal states, enhancing its anomaly detection
capabilities.
In addition, we present the point plot of the anomalies
predicted outputs of MTGFLOW and the proposed DMTFD
in Fig. 6. The x-axis represents the anomaly index and the yaxis represents the log likelihood of the anomaly. Anomalous
ground truths are marked by a red background. This indicates
that DMTFD is able to detect anomalies more accurately and
in a timely manner, outperforming MTGFLOW in terms of
anomaly detection performance.
Fig. 7 shows the bar plot of the frequency of normalized anomaly scores on baseline methods and DMTFD.
The x-axis represents the anomaly scores and the y-axis
represents the frequency of each score. The normalized
anomaly scores of DMTFD are significantly lower than those
of GANF and MTGFlow, indicating that DMTFD is more
effective at distinguishing between normal and abnormal
states.
E. Ablation Study: The Effect of SoftCL Loss
To assess the effectiveness of each component designed
in our model, we conducted a series of ablation experiments. The results of these experiments are presented
in Table III.
We performed controlled experiments to verify the necessity
of the SoftCL Loss in the UNDA settings across all four

LIU et al.: DEEP MULTIMANIFOLD TRANSFORMATION-BASED MTS FAULT DETECTION

18405

Fig. 7. Bar plot of the frequency of normalized anomaly scores on baseline methods and DMTFD. The x-axis represents the anomaly scores and the y-axis
represents the frequency of each score. The normalized anomaly scores of DMTFD are significantly lower than those of GANF and MTGFlow, indicating
that DMTFD is more effective at distinguishing between normal and abnormal states.
TABLE IV
PARAMETERS A NALYSIS : L EARNING R ATES . TABLE OF AUC S CORES (AUROC%) FOR D IFFERENT L EARNING R ATES ON THE SWAT DATASET,
I NDICATING DMTFD’ S S ENSITIVITY TO THE L EARNING R ATE

TABLE V
PARAMETERS A NALYSIS : N UMBER OF E POCHS . TABLE OF AUC S CORES (AUROC%) FOR D IFFERENT E POCHS ON THE SWAT DATASET, I NDICATING
DMTFD’ S S ENSITIVITY TO THE N UMBER OF E POCHS

TABLE VI
PARAMETERS A NALYSIS : H YPERPARAMETER ν. TABLE OF (AUROC%)
S CORES (AUROC%) FOR D IFFERENT ν ON THE SWAT DATASET, I NDI CATING DMTFD’ S S ENSITIVITY TO THE H YPERPARAMETER ν

datasets. The performance of the proposed DMTFD method
is denoted as DMTFD in Table A-5 in the Supplementary
Material. The variant w/o. SoftCL represents the model performance with the SoftCL loss component, LMML (xti , yi t ),
removed from the overall loss function of DMTFD. The
variant w. CL indicates the model performance when the
SoftCL loss is replaced by a typical contrastive loss, LCCL ,
as defined in (6). The results clearly demonstrate that the
SoftCL Loss significantly outperforms the traditional CL loss.
We attribute the inferior performance of LCCL to its inability to adequately address the view-noise caused by domain
bias.
F. Hyperparameter Robustness
1) Hyperparameter Robustness: Window Size and Number
of Blocks: Table A-5 in the Supplementary Material presents
an ablation study investigating the robustness of hyperparameters, focusing on the window size and number of blocks. Three
distinct datasets, SWaT, WADI, and PSM, along with MSL, are

evaluated using DMTFD. Our method showcases promising
results, with consistently competitive AUROC scores across
varying hyperparameter configurations. Notably, the standard
deviations accompanying AUROC values indicate a high
degree of stability, underscoring the reliability of our approach.
Analysis of the table reveals that optimal configurations often
coincide with larger window sizes and moderate block numbers, suggesting a preference for capturing broader temporal
contexts while maintaining computational efficiency. Additionally, trends indicate that as the number of blocks increases,
there is a discernible improvement in performance, albeit
with diminishing returns beyond a certain threshold. This
observation highlights the importance of carefully balancing
model complexity with computational resources. Overall, the
DMTFD method demonstrates robustness and effectiveness in
anomaly detection tasks.

2) Hyperparameter Robustness: Learning Rate, ν, and
Number of Epoch: In order to further investigate the effectiveness of MTGFlow, we give a detailed analysis based on
the SWaT dataset. We conduct ablation studies on the learning
rate, ν, and the number of epochs. The results are shown
in Tables IV–VII. The results show that the performance of
MTGFlow is relatively stable across different learning rates,
ν, and the number of epochs. This indicates that MTGFlow
is robust to hyperparameter changes and can achieve good
performance with a wide range of hyperparameters.

18406

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 10, OCTOBER 2025

TABLE VII
PARAMETERS ANALYSIS : W EIGHT OF N EGATIVE (N E ) S AMPLE AND P OSITIVE (P O ) S AMPLE . TABLE OF AUC S CORES (AUROC%) FOR D IFFERENT
T OPOLOGICAL L OSS R ATIOS ON THE S WAT DATASET

VI. C ONCLUSION
In this work, we propose DMTFD, an unsupervised framework for fault detection in multivariate time series. To
overcome the limitations of Gaussian assumptions, DMTFD
models data with multi-Gaussian representations. A neighborbased augmentation strategy is designed to generate positive
pairs for learning, while a representation head enables optimization based on local streamform similarities. This enhances
the separation between normal and anomalous states and
broadens anomaly coverage. Experiments on standard benchmarks (e.g., SWaT and WADI) demonstrate that DMTFD
achieves superior AUC and PR scores, with lower false alarm
rates and improved detection accuracy. Visualizations also
validate the effectiveness of the multi-Gaussian modeling.
Although our current focus is unsupervised fault detection,
DMTFD can be extended to remaining useful life (RUL)
prediction. Its pretrained embeddings provide strong priors for
temporal degradation modeling and, with minimal finetuning,
can support few-shot RUL forecasting. We leave multitask
extensions integrating fault detection and RUL estimation for
future work.
R EFERENCES
[1]

[2]

[3]

[4]

[5]
[6]

[7]

A. Abdulaal, Z. Liu, and T. Lancewicki, “Practical approach to asynchronous multivariate time series anomaly detection and localization,”
in Proc. 27th ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug.
2021, pp. 2485–2494.
C. M. Ahmed, V. R. Palleti, and A. P. Mathur, “Wadi: A water
distribution testbed for research in the design of secure cyber physical
systems,” in Proc. 3rd Int. Workshop Cyber-Phys. Syst. Smart Water
Netw., Jul. 2017, pp. 25–28.
L. Ardizzone, C. Lüth, J. Kruse, C. Rother, and U. Köthe, “Guided
image generation with conditional invertible neural networks,” 2019,
arXiv:1907.02392.
J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Disc. Data Min., Jun.
2020, pp. 3395–3404.
R. Chalapathy and S. Chawla, “Deep learning for anomaly detection: A
survey,” 2019, arXiv:1901.03407.
H. Chen, Z. Chai, O. Dogru, B. Jiang, and B. Huang, “Data-driven
designs of fault detection systems via neural network-aided learning,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 10, pp. 5694–5705,
Oct. 2022.
T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, “A simple framework
for contrastive learning of visual representations,” in Proc. 37th Int.
Conf. Mach. Learn., Jun. 2020, pp. 1597–1607.

[8]

X. Chen et al., “DAEMON: Unsupervised anomaly detection and
interpretation for multivariate time series,” in Proc. IEEE 37th Int. Conf.
Data Eng. (ICDE), Aug. 2021, pp. 2225–2230.
[9] E. Dai and J. Chen, “Graph-augmented normalizing flows for anomaly
detection of multiple time series,” in Proc. Int. Conf. Learn. Represent.,
Jan. 2022, pp. 1–15.
[10] Y. Feng et al., “Computation-efficient fault detection framework for
partially known nonlinear distributed parameter systems,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 35, no. 9, pp. 12604–12616, Sep. 2023.
[11] J. Goh, S. Adepu, K. N. Junejo, and A. Mathur, “A dataset to support
research in the design of secure water treatment systems,” in Proc. Int.
Conf. Crit. Inf. Infrastruct. Secur. Cham, Switzerland: Springer, 2016,
pp. 88–99.
[12] S. Goyal, A. Raghunathan, M. Jain, H. V. Simhadri, and P. Jain,
“DROCC: Deep robust one-class classification,” in Proc. Int. Conf.
Mach. Learn., Jun. 2020, pp. 3711–3721.
[13] J.-B. Grill et al., “Bootstrap your own latent: A new approach to selfsupervised learning,” in Proc. Adv. Neural Inf. Process. Syst. (NIPS),
vol. 33, Dec. 2020, pp. 21271–21284.
[14] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum contrast for
unsupervised visual representation learning,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020, pp. 9729–9738.
[15] X. Huang, W. Chen, B. Hu, and Z. Mao, “Graph mixture of experts
and memory-augmented routers for multivariate time series anomaly
detection,” in Proc. AAAI Conf. Artif. Intell., vol. 39, Sep. 2025,
pp. 17476–17484.
[16] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and
T. Söderström, “Detecting spacecraft anomalies using LSTMs and
nonparametric dynamic thresholding,” in Proc. 24th ACM SIGKDD Int.
Conf. Knowl. Disc. Data Min., Jul. 2018, pp. 387–395.
[17] R. Li, W. J. C. Verhagen, and R. Curran, “A systematic methodology
for prognostic and health management system architecture definition,”
Rel. Eng. Syst. Saf., vol. 193, Jan. 2020, Art. no. 106598.
[18] S. Li, Z. Liu, Z. Zang, D. Wu, Z. Chen, and S. Z. Li, “GenURL:
A general framework for unsupervised representation learning,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 36, no. 1, pp. 286–298, Jan. 2025.
[19] S. Z. Li, Z. Zang, and L. Wu, “Deep manifold transformation for
nonlinear dimensionality reduction,” 2020, arXiv:2010.14831.
[20] S. Z. Li, Z. Zang, and L. Wu, “Markov-lipschitz deep learning,” 2020,
arXiv:2006.08256.
[21] A. Lin, J. Cheng, L. Rutkowski, S. Wen, M. Luo, and J. Cao,
“Asynchronous fault detection for memristive neural networks with
dwell-time-based communication protocol,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 34, no. 11, pp. 9004–9015, Sep. 2022.
[22] C. Liu, S. He, Q. Zhou, S. Li, and W. Meng, “Large language model
guided knowledge distillation for time series anomaly detection,” 2024,
arXiv:2401.15123.
[23] H. Liu, X. Qiu, Y. Shi, and Z. Zang, “USD: Unsupervised soft contrastive
learning for fault detection in multivariate time series,” in Proc. IEEE
Int. Conf. Acoust., Speech Signal Process. (ICASSP), Apr. 2025, pp. 1–5.
[24] N. D. Nguyen, J. Huang, and D. Wang, “A deep manifold-regularized
learning model for improving phenotype prediction from multi-modal
data,” Nature Comput. Sci., vol. 2, no. 1, pp. 38–46, 2022.
[25] C. Peng and M. Fanchao, “Fault detection of urban wastewater treatment
process based on combination of deep information and transformer
network,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35, no. 6,
pp. 8124–8133, Jun. 2022.

LIU et al.: DEEP MULTIMANIFOLD TRANSFORMATION-BASED MTS FAULT DETECTION

[26] L. Ruff et al., “Deep semi-supervised anomaly detection,” 2019,
arXiv:1906.02694.
[27] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Disc. Data
Min., Jun. 2019, pp. 2828–2837.
[28] J. Tang, Z. Gong, B. Tao, and Z. Yin, “Advancing generalizations of
multi-scale GAN via adversarial perturbation augmentations,” Knowl.Based Syst., vol. 284, Jan. 2024, Art. no. 111260.
[29] J. Wang, S. Shao, Y. Bai, J. Deng, and Y. Lin, “Multiscale wavelet
graph AutoEncoder for multivariate time-series anomaly detection,”
IEEE Trans. Instrum. Meas., vol. 72, pp. 1–11, 2023.
[30] H. Wu, J. Xu, J. Wang, and M. Long, “Autoformer: Decomposition
transformers with auto-correlation for long-term series forecasting,” in
Proc. Adv. Neural Inf. Process. Syst., Jan. 2021, pp. 1–12.
[31] R. Xu, H. Miao, S. Wang, P. S. Yu, and J. Wang, “PeFAD: A parameterefficient federated framework for time series anomaly detection,” in
Proc. 30th ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug.
2024, pp. 3621–3632.
[32] X. Yu, Z. Zhao, X. Zhang, X. Chen, and J. Cai, “Statistical identification
guided open-set domain adaptation in fault diagnosis,” Rel. Eng. Syst.
Saf., vol. 232, Apr. 2023, Art. no. 109047.
[33] Z. Zang et al., “DLME: Deep local-flatness manifold embedding,” in
Proc. ECCV. Cham, Switzerland: Springer, Jan. 2022, pp. 576–592.
[34] Z. Zang et al., “DiffAug: Enhance unsupervised contrastivelearning with
domain-knowledge-free diffusion-based data augmentation,” in Proc.
Int. Conf. Mach. Learn., 2024, pp. 58174–58196.
[35] Z. Zang et al., “Boosting novel category discovery over domains with
soft contrastive learning and all in one classifier,” in Proc. IEEE/CVF
Int. Conf. Comput. Vis. (ICCV), Oct. 2023, pp. 11824–11833.
[36] J. Zhang, K. Zhang, Y. An, H. Luo, and S. Yin, “An integrated multitasking intelligent bearing fault diagnosis scheme based on representation
learning under imbalanced sample condition,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 35, no. 5, pp. 6231–6242, May 2023.
[37] L. Zhang, J. Lin, H. Shao, Z. Zhang, X. Yan, and J. Long, “End-to-end
unsupervised fault detection using a flow-based model,” Rel. Eng. Syst.
Saf., vol. 215, Nov. 2021, Art. no. 107805.
[38] B. Zhao, X. Zhang, Q. Wu, Z. Yang, and Z. Zhan, “A novel unsupervised
directed hierarchical graph network with clustering representation for
intelligent fault diagnosis of machines,” Mech. Syst. Signal Process.,
vol. 183, Jan. 2023, Art. no. 109615.
[39] Q. Zhou, J. Chen, H. Liu, S. He, and W. Meng, “Detecting multivariate
time series anomalies with zero known label,” in Proc. AAAI Conf. Artif.
Intell., vol. 37, no. 4, Jun. 2023, pp. 4963–4971.
[40] Q. Zhou, S. He, H. Liu, J. Chen, and W. Meng, “Label-free multivariate
time series anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 36,
no. 7, pp. 3166–3179, Jul. 2024.
[41] T. Zonta, C. A. da Costa, R. da Rosa Righi, M. J. de Lima, E. S. da
Trindade, and G. P. Li, “Predictive maintenance in the industry 4.0: A
systematic literature review,” Comput. Ind. Eng., vol. 150, Dec. 2020,
Art. no. 106889.

Hong Liu (Member, IEEE) received the Ph.D.
degree from Zhejiang University, Hangzhou, China,
in 2014.
He had a post-doctoral experience in electronic
science major at Zhejiang University. He was a Visiting Researcher with The Hong Kong University of
Science and Technology, Hong Kong. He is currently
an Associate Professor with the School of Information and Electric Engineering, Hangzhou City
University, Hangzhou. His major research interests
include system modeling, optimization, and control.

18407

Xiuxiu Qiu received the master’s degree in electronic information from Zhejiang University of
Technology, Hangzhou, China, in 2025.
Her research focuses on affective computing and
intelligent information processing.

Yiming Shi received the master’s degree from Zhejiang University, Hangzhou, China, 2006.
With long-term dedication to industrial control
systems research, he specializes in fieldbus technologies, information security, and edge intelligence.

Miao Xu received the M.S. degree from the Institute
of Automation, Chinese Academy of Sciences, Beijing, China, in 2024, under the supervision of Zhen
Lei.
His research interests include computer vision and
3-D reconstruction.

Zelin Zang (Member, IEEE) received the Ph.D.
degree from Zhejiang University, Hangzhou, China,
in 2024, under the supervision of Prof. Stan Z. Li.
His research focuses on manifold learning, dimensionality reduction, and geometric deep learning,
with applications in single-cell omics, protein function analysis, and biomedical image understanding.
He has made notable contributions to deep manifold
transformation techniques and has proposed several
high-impact models in AI for Science, including
MuST for spatial transcriptomics integration and
DMT-HI for interpretable manifold visualization. His current research interests
lie in developing interpretable and structure-aware representation learning
methods for high-dimensional biological data, with an emphasis on tree-like
structure inference, large-scale biomedical foundation models, and multiagent
medical reasoning systems.

Zhen Lei (Fellow, IEEE) received the B.S. degree
in automation from the University of Science and
Technology of China, Hefei, China, in 2005, and
the Ph.D. degree from the Institute of Automation,
Chinese Academy of Sciences, Beijing, China, in
2010.
He is currently a Professor with the Institute of
Automation, Chinese Academy of Sciences. He has
published over 200 articles in international journals
and conferences with more than 30000 citations in
Google Scholar and an H-index of 81. His research
interests include computer vision, pattern recognition, image processing, and
face recognition in particular.
Dr. Lei is an IAPR Fellow and an AAIA Fellow. He was a winner of
the 2019 IAPR Young Biometrics Investigator Award. He was the Program
Co-Chair of IJCB2023, the Competition Co-Chair of IJCB2022, and the
area chair of several conferences. He is an Associate Editor of IEEE
T RANSACTIONS ON I NFORMATION F ORENSICS AND S ECURITY, IEEE
T RANSACTIONS ON B IOMETRICS , B EHAVIOR , AND I DENTITY S CIENCE,
Pattern Recognition, Neurocomputing, and IET Computer Vision.
PAPER_TEXT
