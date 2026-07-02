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
# [740] MFAD: A Multimodal Feature Fusion-Enhanced Time Series Anomaly Detection Framework in Industrial Cyber-Physical Systems
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
编号：740
题名：MFAD: A Multimodal Feature Fusion-Enhanced Time Series Anomaly Detection Framework in Industrial Cyber-Physical Systems
年份：2026
DOI：10.1109/tase.2026.3683936
来源：IEEE Transactions on Automation Science and Engineering
PDF：paper/10.1109_TASE.2026.3683936.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：时序、日志、KPI 与云原生异常检测、入侵检测与网络异常检测
相关性：中相关，分数 7
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\740.txt
- 原始字符数：81924
- 本次发送字符数：81924
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
8318

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

MFAD: A Multimodal Feature Fusion-Enhanced
Time Series Anomaly Detection Framework in
Industrial Cyber-Physical Systems
Silin Peng , Yu Han , Lichen Liu , Jinlong Li , Ruonan Li , Zhaoquan Gu , Jie Liu , Fellow, IEEE,
and Xiaowen Chu , Fellow, IEEE

Abstract—Industrial Cyber-Physical Systems (ICPS) are
increasingly vulnerable to sophisticated attacks and operational
disturbances that induce subtle and hard-to-detect anomalies,
particularly in industrial edge environments. Existing anomaly
detection methods often rely on sufficient labeled data and
involve excessive computational overhead, hindering real-time
detection and lightweight deployment. To address these challenges, we propose a Multimodal Feature fusion-enhanced time
series Anomaly Detection framework (MFAD) in ICPS. MFAD
enhances the representation of subtle anomalies by jointly modeling temporal dynamics and industrial characteristics through a
unified multimodal feature fusion mechanism. Moreover, MFAD
adopts a three-stage detection strategy with adaptive thresholding, which further improves robustness under varying operating
conditions, while its lightweight overall architecture supports
edge deployment. In addition, we provide the Industrial Gas
Cyber-Physical System (IGCPS) dataset collected from real-world
industrial operations. Experiments on ICPS benchmark datasets
of varying scales, including IGCPS, PUMP, WADI, and SWaT,
demonstrate that MFAD achieves an F1 score exceeding 96.7%
with efficient resource utilization, validating its effectiveness
Received 23 November 2025; revised 20 February 2026; accepted 10 April
2026. Date of publication 14 April 2026; date of current version 22 April
2026. This article was recommended for publication by Associate Editor J.
Xiao and Editor H. Zhang upon evaluation of the reviewers’ comments. This
work was supported in part by Shenzhen Science and Technology Program
under Grant KJZD20240903103811016, in part by the Major Key Project
of Pengcheng Laboratory (PCL) under Grant PCL2024A05, and in part by
the National Natural Science Foundation of China under Grant 62350710797.
(Corresponding authors: Zhaoquan Gu; Ruonan Li.)
Silin Peng is with the School of Intelligent Systems Engineering,
Sun Yat-sen University, Shenzhen 518107, China, and also with the Department of New Networks, Peng Cheng Laboratory, Shenzhen 518108, China
(e-mail: pengslin6@mail2.sysu.edu.cn).
Yu Han is with the School of Intelligent Systems Engineering, Sun Yat-sen
University, Shenzhen 518107, China (e-mail: hanyu25@mail.sysu.edu.cn).
Lichen Liu and Ruonan Li are with the Department of New Networks,
Peng Cheng Laboratory, Shenzhen 518108, China (e-mail: liulch@pcl.ac.cn;
lirn@pcl.ac.cn).
Jinlong Li is with the Cyberspace Institute of Advanced
Technology, Guangzhou University, Guangzhou 510006, China (e-mail:
jinlongli@gzhu.edu.cn).
Zhaoquan Gu is with the College of Computer Science and Technology,
Harbin Institute of Technology, Shenzhen 518055, China, and also with the
Department of New Networks, Peng Cheng Laboratory, Shenzhen 518108,
China (e-mail: guzhaoquan@hit.edu.cn).
Jie Liu is with the International Research Institute for Artificial Intelligence, Harbin Institute of Technology, Shenzhen 518055, China, and also
with the State Key Laboratory of Smart Farm Technologies and Systems,
Harbin 150030, China (e-mail: jieliu@hit.edu.cn).
Xiaowen Chu is with the Department of Computer Science, The Hong Kong
University of Science and Technology (Guangzhou), Guangzhou 511458,
China (e-mail: xwchu@ust.hk).
Digital Object Identifier 10.1109/TASE.2026.3683936

for real-time detection and lightweight deployment in resourceconstrained industrial edge environments.

Note to Practitioners—This paper is motivated by the increasing need for reliable and efficient anomaly detection in
Industrial Cyber-Physical Systems (ICPS), particularly deployed
in resource-constrained industrial edge environments. Existing
approaches often treat temporal and industrial features separately, rely on sufficient labeled data, and require substantial
computational resources, which limits their applicability in realworld industrial settings. In contrast, the proposed MFAD
provides a lightweight and practical solution that integrates
multimodal feature fusion with robust semi-supervised detection
mechanisms to effectively capture subtle anomalies in time series
industrial data. The framework is designed with deployment
feasibility that it offers strong detection accuracy, low latency,
and efficient resource consumption suitable for industrial edge
devices. The methods presented here can inform practitioners
seeking to enhance the reliability and real-time performance of
ICPS anomaly detection systems. Future extensions may focus
on expanding MFAD for broader online industrial applications,
integrating it with more edge platforms, and enabling large-scale
distributed deployment.
Index Terms—Industrial cyber-physical systems, multimodal
feature fusion, time series anomaly detection, resourceconstrained industrial edge environments.

I. I NTRODUCTION

I

NDUSTRIAL Cyber–Physical Systems (ICPS) constitute
the operational backbone of modern industrial automation,
critical infrastructure, and edge intelligence systems [1]. ICPS
tightly couple computational processes with physical dynamics
through interconnected sensors, actuators, controllers, and
communication interfaces, thereby achieving high levels of
automation, efficiency, and resilience [1], [2], [3], [4]. However, this tight cyber–physical integration also significantly
enlarges the attack surface: sophisticated cyber intrusions,
stealthy signal manipulations, and cross-layer disturbances
may propagate across both cyber and physical domains, giving
rise to subtle yet safety-critical anomalies [5], [6], [7]. In addition, the migration of ICPS toward edge-assisted architectures
for real-time processing further exacerbates the challenge of
deploying effective anomaly detection under stringent resource
constraints [8], [9], [10].

1558-3783 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

PENG et al.: MULTIMODAL FEATURE FUSION-ENHANCED TIME SERIES ANOMALY DETECTION FRAMEWORK

Compared with conventional Information Technology (IT)
anomaly detection tasks [11], [12], [13], anomaly detection
in ICPS exhibits several distinctive challenges. First, ICPS
sensor streams exhibit strong temporal dependencies and
multimodal heterogeneity. Anomalies in such systems often
manifest simultaneously across physical measurements and
control logic [14]. Such multimodal properties hinder the
effectiveness of detection methods using single features, while
multimodal fusion has been extensively explored in the image
domain but remains under-investigated for time series anomaly
detection [15]. Second, industrial edge devices operate under
strict computational, memory, and latency constraints, rendering many deep anomaly detection frameworks impractical
for real-world deployment [16]. Third, severe data imbalance,
incomplete labeling, and the presence of noise or distribution
drift further complicate training and degrade the robustness
of fully supervised models [17], [18]. As a result, designing
a lightweight yet robust anomaly detection framework under
edge constraints remains an open problem.
Traditional statistical and machine learning methods [19]
offer interpretability and low computational cost, but their
reliance on handcrafted features and large amounts of labeled
data limits their ability to capture complex temporal dynamics
in modern ICPS. Deep learning approaches [20], including
autoencoders, recurrent networks, and attention-based models,
have demonstrated strong capability in modeling temporal
dependencies and nonlinear patterns. Nevertheless, most existing deep models focus on temporal features, underutilize
rich industrial feature representations, and incur computational
overhead that exceeds the capacity of edge devices. Moreover,
the lack of effective multimodal feature fusion and adaptive
thresholding mechanisms further constrains their robustness
across diverse operational conditions.
To address these challenges, this paper proposes propose
a Multimodal Feature fusion-enhanced time series Anomaly
Detection framework (MFAD) in resource-constrained ICPS
environments. MFAD constructs a unified multimodal representation by jointly modeling temporal dynamics and
industrial statistical features, enabling more accurate detection
of subtle cyber–physical anomalies. A lightweight architecture
and semi-supervised learning paradigm are adopted to reduce
computational overhead and alleviate label scarcity. Furthermore, MFAD incorporates a three-stage detection mechanism
with an adaptive threshold strategy, achieving strong detection performance, robustness against Gaussian noise and
distribution shifts, and consistent performance across varying
industrial operating conditions.
The main contributions of this work are summarized as
follows:
1) We propose MFAD, a lightweight Multimodal Feature fusion-enhanced time series Anomaly Detection
framework that jointly models temporal dependencies and industrial domain characteristics, enabling
effective cross-domain anomaly representation in ICPS
environments.
2) We design a lightweight semi-supervised learning architecture incorporating a progressive three-stage detection
mechanism with adaptive threshold calibration, which

8319

improves robustness against Gaussian noise and distribution shifts in resource-constrained ICPS edge
environments.
3) We contribute the Industrial Gas Cyber-Physical System
(IGCPS) dataset, a real-world benchmark collected from
Shenzhen Gas Corporation operational environments,
containing both normal operations and cyber-physical
attack scenarios.
4) We conduct extensive experiments on ICPS time series
datasets of varying scales (IGCPS, PUMP, SWaT, and
WADI), demonstrating that MFAD consistently achieves
superior detection performance, with F1-scores exceeding 96.7% across all benchmarks, while maintaining
efficient resource utilization and real-time detection performance for industrial edge deployment.
The remainder of this paper is organized as follows.
Section II reviews existing ICPS time series anomaly detection
research. Section III describes the proposed MFAD framework
in detail. Section IV introduces the experimental results. Section V presents robustness evaluation and analysis. Section VI
concludes the paper with future directions.
II. R ELATED W ORK
This section provides a comprehensive review of anomaly
detection research in industrial cyber–physical systems ICPS.
Existing work can be grouped into three categories: traditional
statistical and machine-learning methods, deep learning models, and advanced techniques.
A. Traditional Methods
Traditional anomaly detection methods mainly consist of
statistical modeling and classical machine learning techniques. Breunig et al. [21] introduced the Local Outlier
Factor (LOF), which measures density deviation to detect
local anomalies. Although LOF effectively detects contextual anomalies, its sensitivity to parameter settings limits its stability in heterogeneous ICPS environments. To
model nonlinear system behaviors, Martinez-Guerra and
Mata-Machuca [22] proposed fault detection schemes based on
the Ensemble Kalman Filter (EnKF), which exploit recursive
Bayesian estimation to identify abnormal state deviations.
Although offering strong theoretical guarantees, the computational burden of EnKF increases rapidly in high-dimensional
industrial processes.
Furthermore, Wu et al. [23] incorporated Bayesian learning
and Gaussian processing into LSTM models for anomaly
detection, enabling interpretable probabilistic reasoning over
multivariate temporal data. However, the introduced Bayesian
components increase inference latency and restrict real-time
usage in edge devices. In parallel, Qin and Lou [24] employed
Isolation Forest (IF) for hydrological anomaly detection, leveraging random partitioning to efficiently isolate rare events.
Nevertheless, its lack of temporal awareness limits its applicability in dynamical ICPS environments. To support industrial
streaming applications, Rosenberger et al. [25] extended
Kernel Density Estimation (KDE) for real-time anomaly
scoring. Despite its lightweight nature, KDE struggles with

8320

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

non-stationary distributions and concept drift. Similarly,
Razzak et al. [26] enhanced One-Class SVM (OCSVM) using
bounded loss functions and randomized nonlinear kernels to
handle large-scale IoT data. While improving robustness, the
kernel operations introduce scalability issues for continuous
ICPS monitoring.
Overall, traditional methods provide interpretability and
computational efficiency. However, their limited capability in modeling multimodal features and complex temporal dependencies poses challenges in modern ICPS
scenarios, motivating the need for data-driven sequence
modeling.
B. Deep Learning Approaches
With the success of representation learning, deep
learning–based anomaly detectors have become mainstream.
Park et al. [27] developed the LSTM-VAE architecture,
combining recurrent networks with variational inference
to model nonlinear temporal dynamics. Although effective
for reconstructing multivariate sequences, this approach
requires significant computation and memory. To further
improve robustness, Gao et al. [28] proposed RobustTAD,
integrating time–frequency decomposition with convolutional
learning. Despite improved noise resilience, the heavy
decomposition pipeline hinders real-time deployment.
Advancing toward attention mechanisms, Yang et al. [29]
introduced DCdetector, which applies dual-attention
contrastive learning to enhance discriminative representations.
While achieving strong performance, the dual-branch
architecture incurs quadratic memory usage. Meanwhile,
Su et al. [30] proposed OmniAnomaly, which incorporates
planar normalizing flows into a GRU-VAE architecture to
represent the stochastic characteristics of multivariate time
series. Despite its robustness, the model faces challenges in
handling extremely high-dimensional ICPS data.
On the one hand, Audibert et al. [31] presented USAD,
a lightweight adversarial autoencoder that amplifies
reconstruction discrepancies. Though training-efficient,
USAD often becomes sensitive to unstable ICPS signals. On
the other hand, Wang et al. [32] proposed CutAddPaste, a
data augmentation strategy that creates pseudo anomalies by
injecting synthetic patterns into normal sequences. Although
alleviating data scarcity, these artificial patterns cannot fully
capture the diversity of real industrial anomalies. To address
system identification, Feng and Tian [18] developed NSIBF,
a neural system identification model equipped with Bayesian
filtering. Its robustness is strong, but parameter tuning is nontrivial. In addition, Kim et al. [33] proposed CTAD, which
utilizes contrastive learning with multiscale augmentations
to enhance noise robustness; yet, handling cross-component
interactions in ICPS remains challenging. Recently,
Tian et al. [34] designed SSDCL, a denoising-aware semisupervised contrastive learning framework achieving strong
anomaly tolerance, but it requires delicate hyperparameter
balancing.
In summary, deep learning methods significantly improve
detection accuracy and feature learning, but often introduce

high computational overhead, limiting their feasibility for realtime and resource-constrained industrial deployment.
C. Advanced Techniques
Beyond traditional and deep learning approaches,
researchers have introduced advanced generative and
graph-based models to capture spatiotemporal dependencies.
Han and Woo [35] introduced FuSAGNet, which integrates
sparse autoencoders with graph structures, effectively
modeling sensor dependencies. However, its static graph
assumption limits adaptability to dynamically changing
industrial relations. Similarly, Chen et al. [36] introduced
DVGCRN, a deep variational graph convolutional recurrent
network capable of learning spatial and temporal correlations
jointly. Although effective on server and satellite data,
its computational complexity restricts its applicability
to edge devices. Building on graph relational learning,
Zhang et al. [37] designed GRELeN, integrating GNN-based
relational modeling with VAE structures. While maintaining
strong anomaly discrimination, its generalization to diverse
industrial scenarios remains limited. More recently, Dai and
Chen [38] proposed GANF, a graph-augmented normalizing
flow framework that embeds causal structure learning
into invertible flows. This method provides interpretable
dependency learning but suffers from high computational
cost due to the invertibility constraints of flow-based models.
Additionally, Lin et al. [39] introduced PddBLS-AE, an
ensemble denoising autoencoder framework based on Broad
Learning System (BLS) for time series anomaly detection.
PddBLS-AE leverages the incremental learning capability of
BLS combined with ensemble denoising strategies to achieve
strong reconstruction-based anomaly detection. However,
its reliance on ensemble mechanisms leads to substantial
floating-point operations (FLOPs) and moderate computational
overhead, limiting its applicability in resource-constrained
industrial edge environments.
As systematically compared in Table I, traditional methods
offer valuable interpretability and computational efficiency
yet lack sophisticated multimodal fusion capabilities essential for heterogeneous ICPS data. Deep learning approaches
provide superior temporal modeling and detection performance but demand significant computational resources that
challenge real-time edge deployment in industrial settings.
Graph-based and other emerging models capture complex
relational structures and data distributions effectively but suffer
from limited adaptability to dynamic conditions and substantial computational overhead. As a result, the fundamental
limitation across all methodological categories is the inability to simultaneously support efficient and robust anomaly
detection capabilities, lightweight computational footprint, and
real-time performance under the noisy, evolving conditions
characteristic of industrial environments. These identified
research gaps directly motivate our proposed MFAD framework, which strategically unifies industrial feature extraction,
lightweight bidirectional temporal representation learning,
adaptive semi-supervised anomaly detection with dynamic
thresholds to comprehensively address the stringent requirements of resource-constrained ICPS deployment.

PENG et al.: MULTIMODAL FEATURE FUSION-ENHANCED TIME SERIES ANOMALY DETECTION FRAMEWORK

8321

TABLE I
C OMPARISON OF T IME S ERIES A NOMALY D ETECTION M ETHODS IN ICPS

Fig. 1. Overall framework of MFAD for industrial anomaly detection.

III. M ETHODOLOGY
This section provides a comprehensive description of the
MFAD framework for anomaly detection in ICPS.

A. Overall Architecture
The MFAD model is specifically designed to extract
multimodal features from the physical layer through capturing industrial characteristics and temporal dependencies
of industrial processes. It also supports semi-supervised
learning under limited labeled data. As shown in Fig. 1,
the architecture of MFAD consists of three primary
modules: (i) Multimodal Feature Fusion (MF) module,
including industrial feature extraction and temporal representation learning through Bidirectional Gated Recurrent Unit–Multi-Head Self-Attention–Temporal Convolutional
Network (BiGRU–Attention–TCN) architecture, (ii) SemiSupervised Learning (SSL) module, including reconstructor
and three-stage classifier, and (iii) Time Series Anomaly

Detection (TSAD) module, adaptive anomaly scoring on the
output of SSL module with dynamic threshold.
Let the multivariate time series input be X ∈ RB×T ×F ,
where B, T , and F denote the batch size, sequence length, and
feature dimension respectively. The MFAD model outputs an
anomaly score S ∈ [0, 1] for each sample, which indicates the
probability that the input sequence exhibits abnormal behavior.
The overall pipeline is formulated as:


S = Fdetect Ffusion Ftemp (X), Find (X)
(1)
where Find represents the industrial feature extractor,
Ftemp denotes the temporal feature encoder consisting of
BiGRU–Attention–TCN architecture, Ffusion refers to the
multimodal feature fusion, and Fdetect represents the final
time series anomaly detection after semi-supervised learning
through reconstructor and classifiers. This hierarchical design
implements a three-stage information-refinement pipeline:
(i) the MF module that jointly encodes industrial domain
characteristics and temporal dependencies into a unified latent
representation; (ii) the SSL module that performs cascaded

8322

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

classification (the three-stage classifier) and reconstruction
regularization to learn discriminative and robust representations; and (iii) the TSAD module that integrates MC-Dropout
uncertainty estimation, weighted fusion with temporal smoothing and adaptive thresholding to produce calibrated anomaly
scores. We will describe the detailed process of each module
in the following sections.
B. MF Module
MF module contains industrial feature extractor and temporal feature encoder, and fuses their representation as the
foundation for the subsequent SSL module.
1) Industrial Feature Extractor: To capture the inherent
characteristics of industrial processes, the industrial feature
extractor Find integrates three complementary perspectives:
statistical features that capture distributional behaviors, frequency features that reflect spectral energy changes, and
trend features that reveal variation dynamics. Specific feature
descriptions are as follows:
a) Statistical features: Given the input sequence X ∈
RB×T ×F , where B denotes batch size, T denotes sequence
length, and F denotes feature dimension, for each input signal,
six statistics are extracted, including mean, standard deviation,
minimum, maximum, median, and range:
fstat = [µ, σ, min, max, median, range]

(2)

which describe the operational envelope and stability of each
sensor. These statistics are computed along the temporal
dimension, resulting in fstat ∈ RB×6F , which is then projected
to RB×96 through a linear layer with LayerNorm and GELU
activation.
b) Frequency features: To identify periodic patterns
or oscillations, a lightweight Short-Time Fourier Transform
(STFT) with window size nfft = 8 and hop length = 4 is
applied. The corresponding spectral power density is expressed
as:


(3)
ffreq = E |F{x}|2
which emphasizes the dominant frequencies in the signal
evolution. The STFT produces nfreq = nfft /2 + 1 = 5 frequency
bins per feature, yielding ffreq ∈ RB×5F , which is projected to
RB×96 through a dedicated frequency projection layer.
c) Trend features: Temporal variation is characterized by
first- and second-order derivatives:
ftrend = [∆x, ∆2 x]

(4)

reflecting both the instantaneous change rate and acceleration
trend of process variables. The trend features ftrend ∈ RB×2F
are projected to RB×48 (half the hidden dimension) to balance
representation capacity.
All three components are concatenated and form the complete industrial feature representation:
 proj proj proj 
zind = Concat fstat , ffreq , ftrend
(5)
resulting in zind ∈ RB×240 (i.e., 96 + 96 + 48 = 240), as illustrated in the Feature Concat block of Fig. 1. This dimension
is designed to match the subsequent fusion layer requirements
while preserving sufficient representational capacity for industrial domain characteristics.

2) Temporal Feature Encoder: Temporal modeling is crucial for identifying evolving abnormal behaviors. The MFAD
temporal feature encoder Ftemp integrates both bidirectional
and hierarchical representations through a combination of
BiGRU, Multi-Head Self-Attention, and Temporal Convolution Network (TCN).
a) BiGRU: Given the input sequence X ∈ RB×T ×F , an
input projection layer first maps it to Xproj ∈ RB×T ×H where
H = 96 is the hidden dimension. The two-layer bidirectional
GRU captures both forward and backward temporal dependencies:
−−−−→
←−−−−
ht = [GRU(x1:t ), GRU(xt:T )] ∈ RH
(6)
producing contextualized embeddings H ∈ RB×T ×H , where
H is is the hidden dimension of the model (number of
output channels for BiGRU–Attention–TCN architecture). The
BiGRU uses 2 layers with H/2 = 48 hidden units per direction,
and the bidirectional outputs are concatenated to maintain
dimension H = 96.
b) Multi-head self-attention: Self-attention is employed
to dynamically emphasize temporally salient events:


QK>
V
(7)
Attention(Q, K, V) = Softmax √
dk
where Q, K, and V are linear projections of H, and dk
denotes the attention head dimension. This mechanism allows
the model to adaptively focus on timestamps that exhibit
higher anomaly potential. With 4 attention heads and perhead dimension dk = H/4 = 24, the multi-head attention
output maintains the shape Hattn ∈ RB×T ×H through output
projection, preserving the temporal resolution for subsequent
TCN processing.
c) TCN: The Temporal Convolutional Network (TCN)
module receives the attention-enhanced sequence Hattn ∈
RB×T ×H and is designed to capture short-range patterns and
multi-scale temporal dependencies through dilated convolutions and residual connections. Formally, for the l-th TCN
layer, the output is computed as:


y(l) = GELU BN Conv1D(y(l−1) ) + y(l−1) ,
(8)
where Conv1D(·) is a one-dimensional dilated convolution,
BN(·) denotes batch normalization, and the non-linear activation function GELU(·) is defined as:
GELU(x) = x Φ(x)

(9)

with Φ(·) being the standard Gaussian cumulative distribution
function (CDF). The residual connection guarantees stable
gradient propagation in deep stacks of dilated convolutions.
The TCN comprises 3 layers with dilation factors {1, 2, 4}
and kernel size 3, maintaining the hidden dimension H =
96 throughout via channel-preserving convolutions, yielding
HTCN ∈ RB×T ×H .
After the final layer, temporal aggregation is performed
using global average pooling:
ytcn = AvgPool(y(L) )

(10)

where AvgPool(·) denotes average pooling along the temporal
dimension. This pooling operation compresses the temporal

PENG et al.: MULTIMODAL FEATURE FUSION-ENHANCED TIME SERIES ANOMALY DETECTION FRAMEWORK

dimension, producing ytcn ∈ RB×H (i.e., RB×96 ), which is
subsequently concatenated with the industrial features zind ∈
RB×240 to form the input to the fusion layer.
3) Multimodal Feature Fusion: To ensure proper temporal
alignment, both the industrial feature extractor and temporal
encoder operate on the same input window X ∈ RB×T ×F .
Statistical features aggregate distributional properties over the
complete sequence, STFT features capture frequency content
through overlapping windows spanning the temporal range,
and trend features compute derivatives across consecutive
time steps. The temporal encoder produces sequence-level
representations through average pooling after TCN processing. This synchronized computation ensures that both feature
modalities represent the same temporal context before fusion.
As illustrated in Fig. 1, the Feature Fusion block receives
the concatenated input [ytcn ; zind ] ∈ RB×336 (ytcn ∈ RB×96 and
zind ∈ RB×240 ) and projects it to the target hidden dimension
H = 96 through a linear transformation:

(11)
hfusion = GELU LayerNorm W[ytcn ; zind ]
where LayerNorm(·) is layer normalization, [·; ·] denotes vector concatenation, and W ∈ R96×336 is a trainable projection
matrix. This projection compresses the high-dimensional concatenated features while preserving discriminative information
from both modalities, producing the unified latent representation hfusion ∈ RB×96 , which serves as the shared input
to both the three-stage classifier and reconstruction module.
The dimensional reduction from 336 to 96 is intentionally
designed to prevent overfitting while maintaining sufficient
representational capacity for anomaly discrimination.
C. SSL Module
1) Three-Stage Cascaded Detection Strategy: To achieve
a balance among recall, discrimination robustness, and precision, the proposed framework employs a cascaded three-stage
classifier with progressive refinement and adaptive early-exit.
Let hfusion ∈ RH denote the fused multimodal representation.
The three-stage classifier is defined as:
Fclf = {Fcoarse , Ffine , Fexpert }

(12)

where each stage is a two-layer MLP with progressively higher
regularization (Dropout: 0.3 → 0.4 → 0.5) to transition
from high recall to high precision. All stages are jointly
optimized with information flowing from coarse to expert
through concatenation:
o(1) = Fcoarse (hfusion ) ∈ R2

(13)

= Ffine ([hfusion ; o ]) ∈ R

(14)

o(3) = Fexpert ([hfusion ; o(1) ; o(2) ]) ∈ R2

(15)

(2)

o

(1)

2

where [·; ·] denotes concatenation. As shown in Fig. 1, the
input dimensions progress as: Coarse stage receives (B, 96) →
(B, 2), Fine stage receives (B, 98) → (B, 2), and Expert
stage receives (B, 100) → (B, 2). The input dimensionality
progressively increases from H to H + 2 to H + 4 implementing a cascaded refinement mechanism. Each subsequent
stage receives both the original fused representation and
the prediction logits from all preceding stages. This design

8323

enables later stages to: (1) correct potential errors from earlier
stages by observing their confidence distributions, (2) focus
computational capacity on samples where earlier predictions
exhibit uncertainty, and (3) leverage inter-stage information
flow without requiring separate feature re-extraction. The
2-dimensional increments correspond to binary classification
logits (normal vs. anomaly) passed between stages. Each
(s)
stage outputs binary logits o(s) = [o(s)
0 , o1 ] with classification
probabilities:
exp(o(s)
k )
,
P(s)
=
P
k
1
(s)
j=0 exp(o j )

k ∈ {0, 1}

(16)

This cascaded architecture enables later stages to refine decisions by leveraging predictions from earlier stages. To reduce
computational cost, samples are routed through stages based
on confidence thresholds τ1 = 0.85 and τ2 = 0.90. Let
c(s) = maxk P(s)
k denote the confidence at stage s. The routing
logic is:
8
(1)
ˆ
<i = 1 if c ≥ τ1
Stage(i) = i = 2 if c(1) < τ1 and c(2) ≥ τ2
(17)
ˆ
:
(1)
(2)
i = 3 if c < τ1 and c < τ2
The final prediction uses the output from the deepest stage
reached:
final )
ŷ = arg max P(s
(18)
k
k∈{0,1}

where sfinal ∈ {1, 2, 3} is determined by Eq. (17). This adaptive mechanism processes approximately 70% of samples at
Stage 1, 20% at Stage 2, and 10% at Stage 3, reducing average
inference cost while maintaining detection accuracy. Stage 1
(Coarse) prioritizes recall, minimizing false negatives with low
dropout of 0.3, Stage 2 (Fine) balances precision and recall
with moderate dropout of 0.4, and Stage 3 (Expert) enhances
precision for hard samples with high dropout of 0.5. The progressive increase in input dimensionality (H → H+2 → H+4)
and regularization strength ensures each stage specializes in
increasingly difficult discrimination tasks without deepening
the network.
2) Reconstruction Regularization: The Reconstructor module, as shown in Fig. 1, operates on the TCN output HTCN ∈
RB×T ×96 and maps it back to the original feature space
through a point-wise MLP: Frec : R96 → RF , producing
the reconstructed sequence X̂ ∈ RB×T ×F . This dimensional
transformation (B, T , 96) → (B, T , F) enables point-wise
reconstruction across all timestamps for accurate anomaly
localization. To preserve the smoothness and geometry of
the latent normal manifold, a reconstruction branch is jointly
optimized with the classifier. The reconstructor estimates an
approximation of the original input sequence:
X̂ = Frec (HTCN )

(19)

The reconstruction error is measured using the normalized
squared Frobenius norm:
1
2
X̂ − X F
(20)
Erec =
TF
which serves as a self-supervised constraint encouraging normal operational patterns to stay consistent across temporal
evolutions.

8324

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

3) Joint Optimization Objective: The total loss function
integrates three-stage classification, hard sample mining, label
smoothing, and reconstruction regularization:
Ltotal =

3
X

wi LCE
i + w f Lfocal + w s Lsmooth

i=1

+ wr Lrec + wa Lanom

(21)

where LCE
is the cross-entropy loss for stage i ∈
i
{1, 2, 3} (coarse/fine/expert), Lfocal is the hard example
mining loss, Lsmooth is label smoothing regularization,
Lrec is normal reconstruction loss, Lanom is anomaly
reconstruction penalty, and (w1 , w2 , w3 , w f , w s , wr , wa ) =
(0.15, 0.25, 0.25, 0.20, 0.05, 0.05, 0.05) balance the competing
objectives. To handle class imbalance [40], we use dynamic
class weighting. The weighted cross-entropy loss for stage i
is defined as:
B
1X

LCE
i =−

B

ωy j log pi (y j |x j )

(22)

j=1

where B is batch size, y j ∈ {0, 1} is the ground-truth label
(0 = normal, 1 = anomaly), and pi (y j |x j ) is the predicted
probability from stage i. The class weight ωy j is determined
by the sample’s label according to:
(
ω0 = 1.0 if y j = 0 (normal)
ωy j =
(23)
ω1
if y j = 1 (anomaly)
where the anomaly class weight ω1 adapts dynamically with
training progress:

 
N0
e
(24)
ω1 = clip
, 5.0, 20.0 · 1.5 + 0.5 ·
N1
E
where N0 and N1 respectively denote the sample counts normal
and anomaly, e is the current epoch, E is total epochs,
and clip(·, a, b) constrains values to [a, b]. The base weight
N0
N1 follows the inverse frequency weighting principle [41].
The clipping bounds [5.0, 20.0] prevent numerical instability
while maintaining effective
 class rebalancing. The progressive
multiplier 1.5 + 0.5 · Ee implements a curriculum learning
schedule [42] that gradually increases emphasis on anomaly
samples from 1.5× to 2.0× throughout training, allowing the
model to first establish stable representations before focusing
on harder anomaly discrimination tasks. To emphasize hard
examples, we apply adaptive Focal Loss [41] on the expert
stage:
B
γ(e)
1X
1 − pj
log(p j + )
(25)
Lfocal = −
B
j=1

where p j = pexpert (y j |x j ) is clamped to [10−7 , 1 − 10−7 ] for
numerical stability,  = 10−8 , and γ(e) = 2.0 + e/E increases
from 2.0 to 3.0. Class-aware aggregation prevents imbalanced
training:
8
anom
normal
ˆ
if N1 > 0
ˆ
<0.7Lfocal + 0.3Lfocal
B
X
Lfocal = 1
(26)
ˆ
Lfocal (p j )
otherwise
ˆ
:B
j=1

Label smoothing with  = 0.05 improves calibration [43]
using fine-stage predictions:
(
X
0.95 if k = y
(2)
Lsmooth = −
ỹk log pk (x), ỹk =
(27)
0.05 otherwise
k
where k ∈ {0, 1} and p(2)
denotes fine-stage probability.
k
Two reconstruction objectives enforce normal pattern learning. Given TCN output HTCN ∈ RB×T ×H and reconstructor
Frec : RH → RF :
1
2
Frec (HTCN ) − X F
BT
F
8
1 X
2
ˆ
<
X̂ j − X j F if N1 > 0
N
T
F
1
Lanom =
j∈I1
ˆ
:0
otherwise
Lrec =

(28)

where I1 = { j : y j = 1}, T is sequence length, F is feature
dimension, and k · kF denotes Frobenius norm.
U
For unlabeled data DU = {xuj }Nj=1
(assumed predominantly
normal), we minimize reconstruction loss with weight wu =
0.3:
NU

2
1 X
Frec (Hu,TCN
) − Xuj
Lunsup = 0.3 ·
j
F
NU T F

(29)

j=1

Gradient clipping (k∇k2 ≤ 1.0) and NaN handling ensure
robust training:
(
Ltotal if finite
Lfinal =
(30)
LCE
otherwise
2
where LCE
2 is the fine-stage cross-entropy as a fallback.
D. TSAD Module
To improve detection robustness under noise and drift, the
proposed framework employs a comprehensive TSAD module,
as illustrated in Fig. 1. The TSAD module receives five
input signals from upstream components and processes them
through MC Dropout uncertainty estimation, normalization,
weighted score fusion, temporal smoothing, and adaptive
thresholding to produce the final anomaly detection results.
1) Input Components: The TSAD module integrates five
complementary signals from the SSL module:
• Classification probabilities Pcoarse , Pfine , Pexpert ∈ RB×2 :
The anomaly probabilities from the three-stage classifier,
where the second dimension represents the softmax output for the anomaly class.
• Reconstruction error Erec ∈ RB : Computed from the
Reconstructor as Erec = T1F kX̂ − Xk2F , measuring the deviation between the input sequence and its reconstruction.
• Embedding distance Demb ∈ RB : Derived from the fused
representation hfusion ∈ RB×H , quantifying the deviation
from the normal manifold. The embedding distance is
computed as:
v
u H 

uX h j − µ j 2
t
Demb =
(31)
σj + 
j=1

PENG et al.: MULTIMODAL FEATURE FUSION-ENHANCED TIME SERIES ANOMALY DETECTION FRAMEWORK

where h j is the j-th dimension of the fused embedding
hfusion , µ j and σ j are the mean and standard deviation
of the j-th dimension estimated from normal training
samples, and  = 10−6 ensures numerical stability. This
standardized Euclidean distance effectively measures how
far each sample deviates from the learned normal manifold in the latent space.
2) MC Dropout Uncertainty Estimation: To quantify prediction uncertainty, the classification probabilities undergo MC
Dropout sampling during inference. Dropout layers remain
active at test time, and M = 5 stochastic forward passes
M
are performed. Let {S (m) }m=1
denote the anomaly scores from
these passes, the ensemble score and epistemic uncertainty are
computed as:
M

1 X (m)
S ,
S̄ =
M

M

U=

m=1

2
1 X (m)
S −S
M

!1/2
(32)

m=1

The uncertainty U ∈ RB serves three critical purposes
in industrial deployment: (1) identifying fuzzy samples near
decision boundaries; (2) detecting distribution shift, where systematic uncertainty increases may indicate operational regime
changes or sensor drift; and (3) supporting risk-aware decisionmaking by enabling operators to adjust detection sensitivity
based on uncertainty levels. As illustrated in Fig. 1, the
uncertainty is directly output alongside the anomaly score for
downstream applications.
3) Normalization: The reconstruction error and embedding
distance are normalized to [0, 1] range using min-max normalization for consistent fusion with probability-based scores:
Êrec =

Erec − Emin
,
Emax − Emin

D̂emb =

Demb − Dmin
Dmax − Dmin

(33)

where the normalization bounds are estimated from the training set statistics.
4) Weighted Score Fusion: The score fusion adapts to the
stage reached by each sample during cascaded inference.
Let sfinal ∈ {1, 2, 3} denote the terminal stage determined
by Eq. (17). The anomaly score is computed as:
S =

sfinal
X

αi P(i)
anom + α4 Ê rec + α5 D̂emb

(34)

i=1

where P(i)
anom denotes the anomaly probability from stage i, and
the stage-adaptive weights are defined as:
8
ˆ
if sfinal = 1
<(0.85, 0, 0)
(α1 , α2 , α3 ) = (0.30, 0.55, 0)
(35)
if sfinal = 2
ˆ
:
(0.20, 0.35, 0.30) if sfinal = 3
with (α4 , α5 ) = (0.10, 0.05) for reconstruction and embedding
components. This formulation ensures that samples exiting
at Stage 1 (approximately 70% of test samples) utilize
only coarse-stage predictions, while harder samples benefit
from refined multi-stage fusion. The stage-adaptive design
reduces unnecessary computation while maintaining detection
accuracy.

8325

5) Temporal Smoothing: Considering that cyber-physical
attacks typically persist across multiple consecutive time steps,
the fused scores undergo temporal smoothing with window
size W:
bW/2c
1 X
S t+k
(36)
S̃ t =
W
k=−bW/2c

The final score combines smoothed and raw components:
S final = λS̃ + (1 − λ)S̄

(37)

where λ ∈ (0, 1) controls the balance between temporal consistency and instantaneous sensitivity. This formulation captures
sustained attack patterns while preserving responsiveness to
sudden anomalies.
6) Adaptive Dynamic Threshold: The detection threshold
is determined through a hierarchical search strategy that
prioritizes high precision while maximizing overall detection
performance. The optimal threshold τ∗ is obtained by solving:
τ∗ = arg max F1 (τ)
τ

s.t.

Precision(τ) ≥ γ

(38)

where F1 (τ) is the harmonic mean of precision and recall:
F1 (τ) = 2 ·

Precision(τ) · Recall(τ)
Precision(τ) + Recall(τ)

(39)

with:
Precision(τ) =

TP
,
TP + FP

Recall(τ) =

TP
TP + FN

(40)

Here, TP, FP, and FN denote true positives, false positives,
and false negatives at threshold τ, respectively. The constraint
parameter γ starts at 0.95 and relaxes to 0.90 if no feasible
solution exists. The search range is [µ0 + 0.2(µ1 − µ0 ), µ1 ],
where µ0 and µ1 are the mean scores of normal and anomalous
samples. This strategy ensures Precision ≥ 95% when achievable, minimizing false alarms in safety-critical applications.
Unlike methods that only minimize |Precision(τ) − 0.95|, our
approach explicitly balances precision and recall through the
F1 objective. This balance is essential for ICPS, where both
false alarms and missed detections have serious operational
consequences.
7) Anomaly Detection: The TSAD module produces two
outputs with dimensions (B, ): (1) the anomaly score S final ∈
RB computed by comparing with threshold τ∗ , yielding a
binary decision per sample, and (2) the uncertainty score
U ∈ RB quantifying prediction confidence for each sample, as
illustrated in Fig. 1. The final Score and Uncertainty both have
shape (B, ), representing per-sample scalar values. High uncertainty samples can be flagged for manual review, enhancing
the practical utility of MFAD in industrial operations. Algorithm 1 summarizes the complete anomaly detection workflow.
The procedure alternates between multimodal feature extraction, temporal encoding, fusion, hierarchical classification,
and reconstruction. Both labeled and unlabeled samples are
incorporated through a semi-supervised optimization loop.
Algorithm 1 summarizes the MFAD for time series anomaly
detection procedure in ICPS. For each epoch, the model
processes labeled mini-batches by extracting industrial features
zind via Find , encoding temporal patterns HTCN via Ftemp ,

8326

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

Algorithm 1 MFAD for Time Series Anomaly Detection in
ICPS
NL
Require: Labeled dataset DL = {(Xi , yi )}i=1
, unlabeled dataset
NU
DU = {X j } j=1 , learning rate η, total epochs E, confidence
thresholds τ1 , τ2
Ensure: Trained model parameters θ, calibrated temperature
T
1: for e = 1 to E do
2:
for each mini-batch (Xb , yb ) ∈ DL do
3:
zind ← Find (Xb ) {Industrial features}
4:
HTCN ← Ftemp (Xb ) {Temporal encoding}
5:
h ← Ffusion (HTCN , zind ) {Feature fusion}
6:
{o(s) }3s=1 ← Fclf (h) {Three-stage classification}
7:
X̂ ← Frec (HTCN ) {Reconstruction}
8:
Compute Ltotal via Eq. (21)
9:
θ ← θ − η∇θ Ltotal
10:
end for
11:
for each mini-batch Xu ∈ DU do
12:
Compute Lunsup and update θ
13:
end for
14: end for
15: Calibrate temperature T on validation set
16: Compute adaptive threshold τ∗ via precision-constrained
search

and fusing both modalities through Ffusion to obtain the unified representation h. The three-stage classifier Fclf produces
hierarchical predictions, while the reconstruction module Frec
generates X̂ for auxiliary supervision. The total loss Ltotal
(Eq. (21)) is computed and model parameters θ are updated
via gradient descent:
θ(t+1) = θ(t) − η∇θ Ltotal

(41)

where η denotes the learning rate controlling optimization step
size. For unlabeled data, the model computes unsupervised
losses Lunsup to leverage unlabeled samples in semi-supervised
learning. After training, temperature calibration adjusts probabilistic confidence on a validation set, and the adaptive
threshold τ∗ is determined via precision-constrained search to
optimize anomaly detection decisions.

E. Computational Complexity and Deployment Analysis
To evaluate the practicality of MFAD for real-world industrial scenarios, we analyze both computational efficiency and
edge deployment feasibility.
Let T denote the sequence length, F the feature dimension,
H the hidden dimension, and K the number of attention heads.
The total computational cost of MFAD can be expressed as:
OMFAD = O(T FH) + O(T H 2 ) + O(HKd)

(42)

where the first term corresponds to the BiGRU encoder, the
second to the multi-head self-attention with head dimension
d = H/K, and the last term to the TCN convolutional layers.

TABLE II
H YPERPARAMETER C ONFIGURATION

IV. E XPERIMENTS
This section introduce the evaluation metrics, the Industrial
Gas Cyber-Physical System (IGCPS) dataset and experimental
results for the ICPS datasets, respectively.

A. Experimental Environments and Hyperparameter Settings
To better approximate practical industrial edge-device conditions, all experimental simulations were conducted on
an NVIDIA Jetson Nano B01 platform equipped with an
ARMv8-based processor and 4 GB RAM. The trained MFAD
model was exported to ONNX format and deployed using
NVIDIA TensorRT with FP16 precision optimization, enabling
hardware-aware inference acceleration on the embedded GPU.
This setup provides a resource-constrained yet realistic computational environment for evaluating the deployment feasibility,
runtime performance, and hardware-adaptive efficiency of
edge-oriented anomaly detection models.
To ensure robust performance and fair comparison, all
hyperparameters are selected via empirical validation and gridbased exploration on a held-out validation set, as summarized
in Table II. The hidden dimension is fixed to H = 96,
providing a favorable trade-off between representation capacity
and computational efficiency under edge deployment constraints, while the learning rate is set to η = 8e−4 , chosen
from {e−4 , 5e−4 , 8e−4 , e−3 } based on convergence stability and
validation performance. To mitigate overfitting under class
imbalance and semi-supervised learning, a progressive dropout
strategy is adopted in the three-stage classifier, with dropout
rates of 0.3, 0.4, and 0.5 for the Coarse, Fine, and Expert
stages, respectively. During inference, confidence thresholds
τ1 = 0.85 and τ2 = 0.90 are used to enable early-exit decisions
based on prediction confidence, allowing a large proportion
of easy samples to terminate at earlier stages in practice and
thus reducing average inference latency. The batch size is
set to 64, weight decay to 5e−4 , and Monte Carlo dropout
is performed with 5 stochastic forward passes to balance
uncertainty estimation quality and efficiency. For temporal
smoothing, the window size W = 7 is selected based on
two considerations: (1) odd-sized windows enable symmetric
centered smoothing, and (2) empirical analysis indicates that
most ICPS attacks persist for 5-10 consecutive time steps. The
smoothing weight λ = 0.6 is determined via grid search to
balance temporal consistency with instantaneous sensitivity.

PENG et al.: MULTIMODAL FEATURE FUSION-ENHANCED TIME SERIES ANOMALY DETECTION FRAMEWORK

8327

The final configuration is selected according to the highest
validation F1-score.
B. Baselines and Evaluation Metrics
To provide a fair comparison, we benchmark our method
against recent representative anomaly detection algorithms
in ICPS, including LSTM-VAE (2018) [27], USAD (2020)
[31], NSIBF (2021) [18], FuSAGNet (2022) [35], CTAD
(2023) [14], DCdetector (2023) [15], and SSDCL (2025)
[16], PddBLS-AE (2025) [39], and we reproduced their work
based on relevant papers. The evaluation follows a standard
binary classification protocol in which each test sample is
assigned to one of four outcome categories: TP — the
model correctly labels an anomalous sequence as abnormal;
FN — an abnormal sequence is mistakenly classified as
normal; TN — a normal sequence is correctly recognized
as normal; FP — a normal sequence is incorrectly flagged
as anomalous.
To quantify detection performance, we employ three widely
used metrics: Precision (Pre) (Eq.(40)), Recall (Rec) (Eq.(40)),
and F1-Score (F1) (Eq.(39)). Precision measures how many
of the predicted anomalies are truly abnormal, while Recall
reflects the proportion of actual anomalies successfully
detected. The F1-Score represents their harmonic mean, balancing both detection accuracy and coverage.
Beyond detection quality, we also assess the computational
efficiency of the proposed framework using three additional
indicators: inference latency per sample (Infer), CPU usage
(CPU), and FLOPs, which collectively capture the suitability
of our method for deployment in resource-constrained industrial edge environments.

Fig. 2. Experimental edge-computing platform: NVIDIA Jetson Nano B01
with TensorRT-accelerated deployment.

TABLE III
D ESCRIPTIONS OF P HYSICAL -L AYER F EATURES IN THE IGCPS DATASET

C. ICPS Time Series Datasets
To thoroughly assess the performance of the MFAD framework, we carried out an extensive experimental study on
multiple ICPS time series datasets. The evaluation covered our
internally collected IGCPS dataset in addition to three widely
used public benchmarks: PUMP, WADI, and SWaT.
We split all datasets into a training set, a validation set,
and a test set following a semi-supervised learning paradigm.
The training set contains both labeled and unlabeled data:
5% labeled samples are used for supervised classification
training, while the remaining 95% unlabeled samples (assumed
predominantly normal operational data) are leveraged for
self-supervised reconstruction learning to capture normal
behavioral patterns. The validation set is used for hyperparameter tuning, temperature calibration, and early stopping. The
test set is used for final model evaluation and performance
validation.
1) IGCPS Dataset: The IGCPS dataset was obtained from
the real operational environment of Shenzhen Gas Corporation (Guangdong, China), where both cyber-layer network
traffic and physical-layer process variables were continuously
recorded. The data capture includes normal operating conditions as well as intentionally induced malfunction states
triggered by cyber–physical attack simulations.

Two representative adversarial behaviors were introduced to
assess anomaly detection performance:
• Shutdown-type attacks: Malicious control commands or
forged packets are injected to interrupt key gas supply
procedures, forcing the closure of valves or disabling
compressors. These actions directly compromise system
availability and cause abrupt operational stops.
• Parameter manipulation attacks: Attacks of this category subtly alter regulatory parameters, such as pressure
limits or flow rate setpoints, with the intention of misleading the control logic. Unlike shutdown attacks, the
resulting anomalies evolve gradually, making them considerably more challenging to detect in real time.
All experiments were conducted under controlled conditions
on April 24, 2025, between 15:17:08 and 15:31:59. During
this time window, physical-layer signals exhibiting deviations
in pressure, temperature, and flow rate were collected. The
resulting dataset contains 895 time stamped samples with
14 monitored sensor attributes. Fig. 3 illustrates the statistical

8328

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

Fig. 3. Physical layer characteristics distribution and simulation scenarios in IGCPS.

distribution of these physical-layer variables, and the meaning
of each feature is summarized in Table III.
In addition to the above physical indicators, the dataset
also includes controller status, controller command values, and
overall operational state variables. The final dataset contains
542 normal instances and 353 anomalous instances.
2) Public Benchmarks: Our experimental evaluation
encompasses three real-world industrial Cyber-Physical System datasets: PUMP, WADI, and SWaT, representing diverse
operational scenarios and scale characteristics. The fundamental attributes and distinctive features of these benchmark
datasets are elaborated as follows:
The PUMP dataset originates from a municipal water treatment and distribution facility, where 52 sensing devices were
installed. Data were recorded at one-minute intervals across a
five-month period. Each instance is labeled according to the
operational condition of the pump, namely normal, recovering,
or broken.
The SWaT dataset was collected from an industrialscale water purification testbed containing 25 sensors and
26 actuators. The full trace spans 11 days, consisting of seven
consecutive days of normal plant operation followed by four
days during which a variety of cyber–physical attacks were
executed.
The WADI dataset extends the SWaT architecture into
a water distribution scenario. It includes 67 sensors and
26 actuators, with data gathered over 16 days in total: 14 days
reflecting nominal behavior and 2 days incorporating attack
events.
D. Analysis of Anomaly Detection Results
Table IV presents the comprehensive experimental results
across four ICPS datasets of varying scales, comparing MFAD
against eight state-of-the-art baselines. On the IGCPS dataset,
MFAD achieves 98.98% precision, 95.10% recall, and 97.00%
F1-score. Among baselines, PddBLS-AE attains the closest
performance with 95.05% F1, followed by SSDCL at 89.64%.
NSIBF and CTAD exhibit lower F1-scores of 32.14% and
66.96% respectively, primarily due to limited recall. Regarding computational efficiency, USAD demonstrates the fastest

inference at 0.23 ms with minimal CPU usage of 1.32%,
while DCdetector incurs the highest overhead at 48.36 ms
inference time and 235.43 M FLOPs. MFAD maintains moderate resource consumption with 0.46 ms latency and 0.99 M
FLOPs.
On the PUMP dataset, MFAD attains 99.95% precision,
99.11% recall, and 99.93% F1-score. SSDCL follows with
97.55% F1, while DCdetector achieves perfect 100% recall but
lower precision at 91.12%, yielding 95.31% F1. USAD shows
the largest precision-recall imbalance with 96.72% precision
but only 60.61% recall, resulting in 74.52% F1. NSIBF
achieves the lowest FLOPs at 0.22 M but with 95.61% F1.
MFAD requires 0.58 ms inference time and 1.19 M FLOPs,
representing 5.4 times lower computational cost than NSIBF
while achieving 4.32% higher F1-score.
On the SWaT dataset, MFAD records 99.53% precision,
99.28% recall, and 99.40% F1-score. SSDCL ranks second with 93.02% F1, exhibiting 6.38% lower performance.
FuSAGNet and CTAD achieve high precision of 98.01% and
97.56% respectively, but their recall values of 73.70% and
73.15% limit F1-scores to 84.11% and 83.65%. PddBLS-AE
attains 88.72% F1 with 60.37 M FLOPs, which is 50.7 times
higher than MFAD. DCdetector requires 264.52 M FLOPs, the
largest among all methods, while achieving only 89.44% F1.
On the challenging WADI dataset with 5.8% anomaly ratio
and 67 sensors, performance degradation is observed across all
baselines. MFAD achieves 98.58% precision, 94.89% recall,
and 96.70% F1-score. PddBLS-AE follows with 87.25%
F1, representing a 9.45% gap. DCdetector exhibits extreme
imbalance with 54.49% precision and 98.48% recall, yielding
70.17% F1. SSDCL shows similar patterns with 64.02% precision and 88.82% recall. LSTM-VAE and USAD demonstrate
severe recall deficiency at 19.06% and 15.72% respectively,
resulting in F1-scores below 32%. NSIBF achieves the lowest
FLOPs at 0.29 M but with only 33.52% F1. DCdetector
requires 624.22 M FLOPs, while MFAD maintains 1.64 M
FLOPs with 26.53% higher F1-score.
Fig. 4 provides a unified radar-based comparison of detection accuracy and computational efficiency across ICPS
datasets of varying scales, namely IGCPS, PUMP, SWaT,
and WADI. Each subfigure jointly visualizes precision, recall,

PENG et al.: MULTIMODAL FEATURE FUSION-ENHANCED TIME SERIES ANOMALY DETECTION FRAMEWORK

8329

TABLE IV
E XPERIMENTAL R ESULTS OF A NOMALY D ETECTION ON D IFFERENT S CALES OF ICPS DATASETS

F1-score, inference latency, CPU usage, and FLOPs, where
efficiency-related metrics (inference latency, CPU usage, and
FLOPs) are reversely normalized using min–max scaling so
that larger values indicate lower latency and reduced resource
consumption. For the IGCPS dataset shown in Fig. 4 (a),
MFAD exhibits the largest radar coverage, indicating the most
balanced performance across both detection and efficiency
dimensions, which is consistent with its superior precision,
recall, and F1-score reported in Table Table IV. On the PUMP
dataset in Fig. 4 (b), MFAD forms an almost regular and
saturated radar profile, whereas methods such as DCdetector
present distorted shapes due to imbalanced precision–recall
behavior and high computational cost. Similar trends are
observed on SWaT dataset in Fig. 4 (c), where MFAD is the
only method maintaining consistently high values across all
six dimensions. The advantage of MFAD is most pronounced
on the WADI dataset in Fig. 4 (d), where severe class
imbalance leads to highly skewed radar profiles for baseline
methods, while MFAD preserves a well-proportioned shape
with strong detection accuracy and computational efficiency.
Overall, Fig. 4 visually demonstrates that MFAD achieves the
most favorable trade-off between detection performance and
efficiency across diverse ICPS scenarios.

TABLE V
A BLATION S TUDY OF MFAD C OMPONENTS

E. Ablation Study
To validate the contribution of each core component, we
perform ablation studies by removing a key module. As shown
in Table V, three primary variants are evaluated against the

8330

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

Fig. 5. Comparison of ablation study results on the ICPS datasets.

Fig. 4. Comparison of detection performance of different models on the ICPS
datasets.

“Full” model (MFAD). The variant “MFAD w/o Ind.” is
that MFAD removes the industrial feature extractor, relying
solely on the temporal encoder. The variant “MFAD w/o
Temp.” is that MFAD removes the entire BiGRU-AttentionTCN temporal encoder, leaving only the industrial features
for anomaly detection. The variant “MFAD w/o Thr.” is
that MFAD replaces the three-stage cascaded classifier with
a single MLP layer, while keeping both feature extraction
pathways.
1) Impact of the Industrial Feature Extractor: Removing
the industrial feature extractor in MFAD (MFAD w/o Ind. in
Table V) leads to a consistent performance reduction across
all datasets. On IGCPS dataset, the F1-score decreases by
0.48% from 97.00% to 96.52%. For PUMP, F1 drops by
1.30% from 99.93% to 98.63%, primarily due to a decline
in precision. The SWaT dataset shows a larger F1 reduction
of 3.67% from 99.40% to 95.73%. The most significant impact
is observed on WADI dataset, where F1 falls by 7.14% from
96.70% to 89.56%. The pronounced degradation on WADI
and SWaT datasets highlights the critical role of engineered
statistical, spectral, and trend features in complex, multi-sensor
environments for discerning subtle operational anomalies.
2) Impact of the Temporal Feature Encoder: As evaluated
in a dedicated ablation experiment (MFAD w/o Temp. in
Table V), removing the BiGRU-Attention-TCN encoder in
MFAD causes the most severe performance drop, affirming
its fundamental role. On IGCPS dataset, F1 falls by 3.74%.
The degradation is 3.52% on PUMP dataset and most acute on
SWaT dataset at 6.74%. WADI shows a reduction of 5.03%.
This confirms the encoder’s indispensability in capturing
bidirectional temporal dependencies and multi-scale patterns
necessary to detect evolving attacks.

3) Impact of the Three-Stage Classifier: Replacing the
cascaded classifier with a single MLP layer in MFAD (MFAD
w/o Thr. in Table V) also results in performance degradation,
highlighting the value of progressive refinement. For IGCPS,
F1 decreases by 0.45% from 97.00% to 96.55%. On PUMP
dataset, F1 drops by 1.69% from 99.93% to 98.24%. The
decline is more substantial on SWaT dataset, with a 3.42%
reduction in F1 from 99.40% to 95.98%. The WADI dataset
exhibits the largest impact, where F1 falls by 7.26% from
96.70% to 89.44%. These results confirm the efficacy of the
three-stage architecture, where successive stages with adaptive
thresholds specialize in high-recall screening, balanced judgment, and high-precision refinement to handle diverse attack
complexities.
Fig. 5 illustrates the ablation study results through grouped
bar charts. Each subfigure compares the complete MFAD
model (Full) with three variants, including MFAD w/o Ind.,
MFAD w/o Temp., and MFAD w/o Thr.. On IGCPS dataset
in Fig. 5 (a), all variants maintain F1 above 93%, with
the Full model achieving 97.00%. On PUMP dataset in
Fig. 5 (b), the Full model reaches 99.93% F1, while removing
the temporal encoder causes the largest drop to 96.41%. On
SWaT dataset in Fig. 5 (c), the temporal encoder removal
results in the most significant degradation from 99.40% to
92.66%. On WADI dataset in Fig. 5 (d), all ablation variants
show substantial performance drops, with F1 falling below
92% when any component is removed. Across all datasets, the
Full model consistently achieves the highest and most balanced
performance. The study establishes component importance
hierarchy: the temporal encoder is most critical with average F1 reduction of 4.76% upon removal, followed by the
three-stage classifier at 3.21% and industrial feature extractor
at 3.15%.
V. ROBUSTNESS E VALUATION
To assess the stability of MFAD in practical ICPS
environments, we conduct robustness evaluation under two

PENG et al.: MULTIMODAL FEATURE FUSION-ENHANCED TIME SERIES ANOMALY DETECTION FRAMEWORK

8331

Fig. 6. Effect of Gaussian noise injection and distribution shifts on MFAD across different ICPS datasets.

perturbation types: stochastic measurement corruption modeled as zero-mean Gaussian noise with standard deviations
from 0.00 to 0.10, and deterministic distribution shifts with
drift levels from 0.00 to 0.10 emulating device aging, recalibration offsets, and slow process regime changes.

Recall exhibits modest improvement from 94.89% to 95.83%
at noise 0.06 before stabilizing around 96.12% at 0.10. F1
ranges from 96.70% at baseline to 95.86% at maximum noise,
demonstrating 0.84% degradation.
B. Robustness to Distribution Shifts

A. Robustness to Gaussian Noise
Fig. 6 presents the detection robustness of MFAD across
different ICPS datasets. Fig. 6(a)-(d) illustrate the performance
of MFAD under Gaussian noise injection with standard deviations ranging from 0.00 to 0.10. On IGCPS dataset (Fig. 6(a)),
F1 ranges from 97.00% to 97.51%, with precision spanning
98.98% to 100.00% and recall maintaining around 95.10%.
At noise level 0.04, precision reaches 100.00% while recall
remains at 95.10%, yielding F1 of 97.49%. At maximum
noise level 0.10, the model achieves 99.01% precision, 95.10%
recall, and 97.01% F1, demonstrating minimal degradation
from baseline.
On PUMP dataset (Fig. 6(b)), performance remains nearperfect across all noise levels. Precision ranges from 99.86%
to 99.98%, recall spans 99.91% to 100.00%, and F1 stays
within 99.93%-99.94%. At noise level 0.06, recall achieves
100.00% while precision maintains 99.89%. The highest F1
of 99.94% occurs at noise level 0.02 with 99.98% precision
and 99.91% recall.
On SWaT dataset (Fig. 6(c)), controlled degradation is
observed. Precision decreases from 99.53% at baseline to
99.38% at noise 0.02, then to 99.12% at 0.04, 98.65% at
0.06, 98.21% at 0.08, and 97.89% at 0.10. Recall shows
gradual decline from 99.28% to 98.95% at noise 0.10. F1
decreases monotonically from 99.40% to 98.42% across the
noise range, representing only 0.98% degradation at maximum
perturbation.
On WADI dataset (Fig. 6(d)), the most pronounced
variations occur due to higher structural complexity with
67 sensors. Precision decreases from 98.58% at baseline to
97.82% at noise 0.04, 96.45% at 0.08, and 95.62% at 0.10.

Fig. 6(e)-(h) present the performance under distribution
shifts with drift levels from 0.00 to 0.10, simulating sensor recalibration and operational regime changes. On IGCPS
dataset (Fig. 6(e)), precision reaches 100.00% at shift levels
0.04-0.10, while F1 ranges from 96.97% to 97.49%. At shift
level 0.02, the model maintains 97.00% F1 with 98.98% precision, identical to baseline. At maximum shift 0.10, precision
achieves 100.00% with 95.10% recall, yielding 97.49% F1,
which is 0.52% higher than that under the initial condition.
On PUMP dataset (Fig. 6(f)), exceptional stability
is observed. Precision ranges from 99.86% to 99.98%,
recall spans 99.91% to 100.00%, and F1 stays within
99.93%-99.94%. At shift levels 0.06-0.10, recall achieves
100.00% while precision marginally decreases from 99.95%
to 99.86%. At shift level 0.02, precision increases to 99.98%
from baseline 99.95%, yielding the highest F1 of 99.94%.
On SWaT dataset (Fig. 6(g)), precision decreases from
99.53% at baseline to 99.72% at shift 0.02, then to 99.40%,
98.73%, 97.86%, and 97.64% at shift levels 0.04, 0.06, 0.08,
and 0.10 respectively. Recall shows different patterns: initially
dropping from 99.28% to 99.05% at shift 0.02, then to 98.79%
at 0.04, before recovering to 98.83% at 0.06, surging to
99.40% at 0.08, and stabilizing at 99.37% at 0.10. F1 decreases
monotonically from 99.40% to 98.49% across the shift range,
representing 0.91% degradation.
On WADI dataset (Fig. 6(h)), precision decreases from
98.58% at baseline to 98.81% at shift 0.02, then to 97.43%
at 0.06, and 95.39% at 0.10. Recall exhibits inverse behavior:
improving from 94.89% at baseline to 96.16% at shift 0.02,
peaking at 97.22% at shift 0.08, and stabilizing at 96.60%
at 0.10. This inverse relationship produces F1 values that

8332

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

initially rise from 96.70% to 97.32% at low shifts, then
gradually decline to 95.99% at maximum shift. The precisionrecall trade-off indicates that the three-stage classifier prioritizes anomaly coverage when facing drift-altered borderline
samples.
The superior detection accuracy and robustness of MFAD
stem from three complementary design choices. First,
multimodal feature fusion combines statistical moments,
STFT-based frequency features, and trend derivatives with
BiGRU–Attention–TCN temporal modeling, capturing both
industrial characteristics and temporal dependencies to form
compact normal manifolds that effectively distinguish abrupt
and gradual attacks under perturbations. Second, a three-stage
cascaded classifier with adaptive early-exit and confidence
gating directs most samples to lightweight stages, reducing
computation while reserving refined analysis for ambiguous
cases, thus balancing precision and recall. Third, a semisupervised learning scheme leverages abundant unlabeled
data via reconstruction regularization, improving robustness
to distribution shifts. With low FLOPs under 1.64 M and
sub-millisecond inference latency below 0.72 ms, MFAD is
well suited for deployment in resource-constrained ICPS edge
environments.
VI. C ONCLUSION AND F UTURE W ORK
This paper proposes MFAD, a lightweight Multimodal
Feature fusion-enhanced time series Anomaly Detection
framework in resource-constrained ICPS. MFAD integrates
three core components: a multimodal feature fusion module
that jointly captures industrial domain characteristics and
temporal dependencies, a semi-supervised learning architecture that achieves high detection performance using only 5%
labeled data, and a three-stage cascaded classifier with adaptive thresholding for efficient inference. Extensive experiments
on ICPS datasets of varying scales (IGCPS, PUMP, SWaT,
and WADI) demonstrate that MFAD consistently achieves
F1-scores above 96.7% while maintaining low FLOPs and
real-time performance suitable for edge deployment. Future
research directions include developing cross-modal attention mechanisms for bidirectional feature interaction prior to
fusion, incorporating physics-informed constraints to enhance
interpretability, deploying MFAD on a broader range of edge
hardware platforms to validate cross-device adaptability and
deployment robustness, and extending the framework toward
online adaptive detection for real-time cyber-physical anomaly
identification.
R EFERENCES
[1]

[2]

[3]

A. Humayed, J. Lin, F. Li, and B. Luo, “Cyber-physical systems security—A survey,” IEEE Internet Things J., vol. 4, no. 6,
pp. 1802–1831, Dec. 2017, doi: 10.1109/JIOT.2017.2703172.
H.-S. Wu, “A survey of research on anomaly detection for time series,”
in Proc. 13th Int. Comput. Conf. Wavelet Act. Media Technol. Inf.
Process. (ICCWAMTIP), Chengdu, China, Dec. 2016, pp. 426–431, doi:
10.1109/ICCWAMTIP.2016.8079887.
Y. Wang, R. Guo, and P. Min, “A survey of applications for anomaly
detection in the IoT: Methods, new perspectives, and future,” in Proc.
IEEE Int. Conf. Syst., Man, Cybern. (SMC), Kuching, Malaysia, Oct.
2024, pp. 2453–2460, doi: 10.1109/SMC54092.2024.10831268.

[4]

M. I. Sayyaf, P. Pascacio, N. Zhu, and V. Renaudin, “Timeseries anomaly detection for sensor data: Models, metrics, and
methodologies—A review,” IEEE Sensors J., vol. 25, no. 24,
pp. 43603–43619, Dec. 2025, doi: 10.1109/JSEN.2025.3616395.
[5] H. Kayan, M. Nunes, O. Rana, P. Burnap, and C. Perera, “Cybersecurity
of industrial cyber-physical systems: A review,” ACM Comput. Surveys,
vol. 54, no. 11s, pp. 1–35, Jan. 2022, doi: 10.1145/3510410.
[6] Z. Yu, Z. Kaplan, Q. Yan, and N. Zhang, “Security and privacy in
the emerging cyber-physical world: A survey,” IEEE Commun. Surveys
Tuts., vol. 23, no. 3, pp. 1879–1919, 3rd Quart., 2021, doi: 10.1109/
COMST.2021.3081450.
[7] K. Zhang et al., “Self-supervised learning for time series analysis: Taxonomy, progress, and prospects,” IEEE Trans. Pattern Anal.
Mach. Intell., vol. 46, no. 10, pp. 6775–6794, Oct. 2024, doi: 10.1109/
TPAMI.2024.3387317.
[8] L. Chen, Y. Xu, M. Li, B. Hu, H. Guo, and Z. Liu, “Privacy-preserving
lightweight time-series anomaly detection for resource-limited industrial IoT edge devices,” IEEE Trans. Ind. Informat., vol. 21, no. 6,
pp. 4435–4446, Jun. 2025, doi: 10.1109/TII.2025.3538127.
[9] S. V. Haldikar, O. F. M. A. Kader, and R. K. Yekollu, “Edge computing
and federated learning for real-time anomaly detection in industrial
Internet of Things (IIoT),” in Proc. Int. Conf. Inventive Comput. Technol.
(ICICT), Lalitpur, Nepal, Apr. 2024, pp. 1699–1703, doi: 10.1109/
icict60155.2024.10544912.
[10] X. Jiang, C. Lu, H. Luo, and Y. Sun, “Unsupervised distributed anomaly
detection framework for IoT in edge AI network,” IEEE Internet
Things J., vol. 12, no. 12, pp. 22058–22072, Jun. 2025, doi: 10.1109/
JIOT.2025.3549765.
[11] S. Peng, Y. Han, R. Li, L. Liu, J. Liu, and Z. Gu, “ROSE-BOX: A
lightweight and efficient intrusion detection framework for resourceconstrained IIoT environments,” Appl. Sci., vol. 15, no. 12, p. 6448, Jun.
2025, doi: 10.3390/app15126448.
[12] N. Chaabouni, M. Mosbah, A. Zemmari, C. Sauvignac, and
P. Faruki, “Network intrusion detection for IoT security based on
learning techniques,” IEEE Commun. Surveys Tuts., vol. 21, no. 3,
pp. 2671–2701, 3rd Quart., 2019, doi: 10.1109/COMST.2019.2896380.
[13] S. Peng, Y. Han, X. Liang, C. Yang, W. Gui, and N. Zhou, “ROSE-BOX:
An approach for intrusion detection in industrial Internet of Things,” in
Proc. IEEE Int. Symp. Parallel Distrib. Process. Appl. (ISPA), Kaifeng,
China, Oct. 2024, pp. 2276–2277, doi: 10.1109/ISPA63168.2024.00325.
[14] P. Yan et al., “A comprehensive survey of deep transfer learning for
anomaly detection in industrial time series: Methods, applications, and
directions,” IEEE Access, vol. 12, pp. 3768–3789, 2024, doi: 10.1109/
ACCESS.2023.3349132.
[15] C. Ding, S. Sun, and J. Zhao, “MST-GAT: A multimodal
spatial–temporal graph attention network for time series anomaly
detection,” Inf. Fusion, vol. 89, pp. 527–536, Jan. 2023.
[16] H. Nizam, S. Zafar, Z. Lv, F. Wang, and X. Hu, “Real-time deep anomaly
detection framework for multivariate time-series data in industrial IoT,”
IEEE Sensors J., vol. 22, no. 23, pp. 22836–22849, Dec. 2022, doi:
10.1109/JSEN.2022.3211874.
[17] E. Eldele et al., “Time-series representation learning via temporal and
contextual contrasting,” in Proc. 13th Int. Joint Conf. Artif. Intell.
(IJCAI), 2021, pp. 2352–2359, doi: 10.24963/IJCAI.2021/324.
[18] C. Feng and P. Tian, “Time series anomaly detection for cyber-physical
systems via neural system identification and Bayesian filtering,” in Proc.
27th ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug. 2021,
pp. 2858–2867, doi: 10.1145/3447548.3467137.
[19] M. Repeva and S. Polyakov, “Anomaly detection in the performance
of data center cooling system devices based on machine learning and
time series analysis,” in Proc. IEEE Ural-Siberian Conf. Biomed. Eng.,
Radioelectronics Inf. Technol. (USBEREIT), Yekaterinburg, Russia, May
2025, pp. 317–320, doi: 10.1109/USBEREIT65494.2025.11054137.
[20] U. A. Usmani, I. Abdul Aziz, J. Jaafar, and J. Watada, “Deep
learning for anomaly detection in time-series data: An analysis
of techniques, review of applications, and guidelines for future
research,” IEEE Access, vol. 12, pp. 174564–174590, 2024, doi:
10.1109/ACCESS.2024.3495819.
[21] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” in Proc. ACM SIGMOD Int. Conf. Manage.
Data, 2000, pp. 93–104.
[22] R. Martinez-Guerra and J. L. Mata-Machuca, Fault Detection and
Diagnosis in Nonlinear Systems. Cham, Switzerland: Springer, 2016.
[23] D. Wu, Z. Jiang, X. Xie, X. Wei, W. Yu, and R. Li, “LSTM learning with
Bayesian and Gaussian processing for anomaly detection in industrial
IoT,” IEEE Trans. Ind. Informat., vol. 16, no. 8, pp. 5244–5253, Aug.
2020, doi: 10.1109/TII.2019.2952917.

PENG et al.: MULTIMODAL FEATURE FUSION-ENHANCED TIME SERIES ANOMALY DETECTION FRAMEWORK

[24] Y. Qin and Y. Lou, “Hydrological time series anomaly pattern detection
based on isolation forest,” in Proc. IEEE 3rd Inf. Technol., Netw.,
Electron. Autom. Control Conf. (ITNEC), Mar. 2019, pp. 1706–1710,
doi: 10.1109/ITNEC.2019.8729405.
[25] J. Rosenberger, J. Müller, A. Selig, M. Bühren, and D. Schramm,
“Extended kernel density estimation for anomaly detection in streaming
data,” Proc. CIRP, vol. 112, pp. 156–161, Sep. 2022.
[26] I. Razzak, K. Zafar, M. Imran, and G. Xu, “Randomized nonlinear oneclass support vector machines with bounded loss function to detect of
outliers for large scale IoT data,” Future Gener. Comput. Syst., vol. 112,
pp. 715–723, Nov. 2020.
[27] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly
detector for robot-assisted feeding using an LSTM-based variational
autoencoder,” IEEE Robot. Autom. Lett., vol. 3, no. 3, pp. 1544–1551,
Jul. 2018.
[28] E. Dai and J. Chen, “Graph-augmented normalizing flows for anomaly
detection of multiple time series,” in Proc. Int. Conf. Learn. Represent.
(ICLR), 2022, pp. 1–10.
[29] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “DCdetector:
Dual attention contrastive representation learning for time series
anomaly detection,” in Proc. 29th ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug. 2023, pp. 3033–3045, doi: 10.1145/3580305.
3599295.
[30] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discovery Data
Mining, New York, NY, USA, Jul. 2019, pp. 2828–2837, doi: 10.1145/
3292500.3330672.
[31] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Disc. Data Min., 2020,
pp. 3395–3404, doi: 10.1145/3394486.3403392.
[32] R. Wang et al., “CutAddPaste: Time series anomaly detection by exploiting abnormal knowledge,” in Proc. 30th ACM SIGKDD Conf. Knowl.
Discovery Data Mining, Aug. 2024, pp. 3176–3187, doi: 10.1145/
3637528.3671739.
[33] H. Kim, S. Kim, S. Min, and B. Lee, “Contrastive time-series
anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 36, no. 10,
pp. 5053–5065, Nov. 2023.
[34] J. Tian, M. Li, L. Fang, and L. Chen, “SSDCL: Semi-supervised
denoising-aware contrastive learning for time series anomaly detection
in cyber-physical systems,” IEEE Trans. Inf. Forensics Security, vol. 20,
pp. 7302–7316, 2025, doi: 10.1109/TIFS.2025.3588674.
[35] J. Tian, M. Li, L. Fang, and L. Chen, “SSDCL: Semi-supervised
denoising-aware contrastive learning for time series anomaly detection
in cyber-physical systems,” IEEE Trans. Inf. Forensics Secur., vol. 20,
pp. 7302–7316, Jul. 2025, doi: 10.1109/TIFS.2025.3588674.
[36] W. Chen, L. Tian, B. Chen, L. Dai, Z. Duan, and M. Zhou, “Deep
variational graph convolutional recurrent network for multivariate time
series anomaly detection,” in Proc. Int. Conf. Mach. Learn. (ICML), Jul.
2022, pp. 3621–3633.
[37] W. Zhang, C. Zhang, and F. Tsung, “GRELEN: Multivariate
time series anomaly detection from the perspective of graph relational learning,” in Proc. Int. Joint Conf. Artif. Intell., Jul. 2022,
pp. 2390–2397.
[38] E. Dai and J. Chen, “Graph-augmented normalizing flows for anomaly
detection of multiple time series,” in Proc. Int. Conf. Learn. Represent.
(ICLR), May 2022.
[39] Y. Lin, Z. Yu, K. Yang, and C. L. Philip Chen, “Ensemble denoising autoencoders based on broad learning system for time-series
anomaly detection,” IEEE Trans. Neural Netw. Learn. Syst., vol. 36,
no. 8, pp. 13913–13926, Aug. 2025, doi: 10.1109/TNNLS.2025.3548
941.
[40] Y. Yao, J. Feng, and Y. Liu, “Domain knowledge-guided contrastive
learning framework based on complementary views for fault diagnosis
with limited labeled data,” IEEE Trans. Ind. Informat., vol. 20, no. 5,
pp. 8055–8063, May 2024.
[41] T.-Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, “Focal loss for
dense object detection,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 42,
no. 2, pp. 318–327, Feb. 2020, doi: 10.1109/TPAMI.2018.2858826.
[42] Y. Bengio, J. Louradour, and R. Collobert, “Curriculum
learning,” in Proc. Int. Conf. Mach. Learn., Aug. 2009,
pp. 41–48.
[43] R. Müller, S. Kornblith, and G. Hinton, “When does label smoothing
help,” in Proc. 33rd Int. Conf. Neural Inf. Process. Syst., Dec. 2019,
pp. 4694–4703.

8333

Silin Peng received the master’s degree in electronic
information from the Civil Aviation University of
China. He is currently pursuing the Ph.D. degree
in information security with the School of Intelligent Systems Engineering, Sun Yat-sen University,
and Peng Cheng Laboratory. His research interests
include network and information security.

Yu Han received the Ph.D. degree in control theory
and control engineering from Shanghai Jiao Tong
University, Shanghai, China, in 2011. He is currently
a Full Professor with the School of Intelligent
Systems Engineering, Sun Yat-sen University,
Shenzhen, China, and Guangdong Provincial
Key Laboratory of Fire Science and Intelligent
Emergency Technology, Shenzhen. His research
interests include robot control, multiinformation
fusion, machine vision, image processing,
evolutionary computing, and intelligent fire
emergency response.

Lichen Liu received the Ph.D. degree from the
Department of Information Engineering, Chang’an
University of Information, Xi’an, China, in 2025. He
is currently a Post-Doctoral Researcher with Peng
Cheng Laboratory. His research interests include
multi-modal information feature fusion anomaly
detection, encrypted traffic detection, and computer
vision.

Jinlong Li received the Ph.D. degree from
South China University of Technology, Guangzhou,
China, in 2024. He is currently a Lecturer with
the Cyberspace Institute of Advanced Technology, Guangzhou University, Guangzhou, China. His
research interests include generative AI, data mining and security, and hybrid intelligent information
systems modeling.

Ruonan Li received the Ph.D. degree from the
Department of Computer Science and Technology,
Harbin Institute of Technology, in 2024. She is
currently a Post-Doctoral Researcher with Peng
Cheng Laboratory. Her research interests include
blockchain, federated learning, AI empowered the
Internet-of-Things, and deep reinforcement learning
for networking.

8334

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 23, 2026

Zhaoquan Gu received the bachelor’s and Ph.D.
degrees in computer science from Tsinghua University, Beijing, China, in 2011 and 2015, respectively.
He is currently a Professor with the Department of
Computer Science and Technology, Harbin Institute
of Technology, Shenzhen, China, and a Researcher
with the Department of New Networks, Peng Cheng
Laboratory, Shenzhen. His research interests include
wireless networks, distributed computing, big data
analysis, and artificial intelligence security.

Jie Liu (Fellow, IEEE) received the Ph.D. degree
in electrical engineering and computer science from
the University of California, Berkeley, Berkeley, CA,
USA, in 2001. He is currently a Chair Professor with
Harbin Institute of Technology (HIT), Shenzhen,
China, and the Dean of the AI Research Institute.
Before joining HIT, he spent 18 years with Xerox
PARC and Microsoft. He was a Principal Research
Manager with Microsoft Research, Redmond, and
a Partner of the Company. His research interests
include cyber-physical systems, AI for IoT, and
energy efficient computing.

Xiaowen Chu (Fellow, IEEE) received the B.E.
degree in computer science from Tsinghua University, Beijing, China, in 1999, and the Ph.D. degree in
computer science from The Hong Kong University
of Science and Technology, Hong Kong, in 2003. He
is currently a Full Professor with the Department of
Computer Science, The Hong Kong University of
Science and Technology, Guangzhou.. His research
interests include distributed and parallel computing
and wireless networks. He is an Associate Editor for
IEEE ACCESS and IEEE Internet of Things.
PAPER_TEXT
