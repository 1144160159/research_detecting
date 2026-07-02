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
# [706] HTDC: Hyperbolic Transformer With Dual-Momentum Contrastive Learning for Hyperspectral Anomaly Detection
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
编号：706
题名：HTDC: Hyperbolic Transformer With Dual-Momentum Contrastive Learning for Hyperspectral Anomaly Detection
年份：2026
DOI：10.1109/tgrs.2026.3670890
来源：IEEE Transactions on Geoscience and Remote Sensing
PDF：paper/10.1109_TGRS.2026.3670890.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：多媒体、医学、遥感与视频异常检测、入侵检测与网络异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\706.txt
- 原始字符数：75926
- 本次发送字符数：75926
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

5507217

HTDC: Hyperbolic Transformer With
Dual-Momentum Contrastive Learning for
Hyperspectral Anomaly Detection
Yulei Wang , Member, IEEE, Chao Deng , Enyu Zhao , Member, IEEE,
and Chunyan Yu , Senior Member, IEEE

Abstract—Hyperspectral anomaly detection (HAD) remains a
challenging task due to the complex spectral variability and
spatial heterogeneity of real-world scenes. Reconstruction-based
methods have been widely explored for deep learning-based HAD,
but they rely on the assumption that background pixels can be
faithfully reconstructed while anomalous pixels cannot. Although
intuitive, this dichotomy oversimplifies the spectral–spatial characteristics of hyperspectral data and often fails in practice. In
particular, when background regions exhibit strong variability
or when anomalies share spectral similarities with their surroundings, reconstruction-based methods tend to generate false
alarms and suffer from limited robustness. To overcome these
limitations, this article moves beyond the reconstruction-based
paradigm and proposes HTDC, a novel hyperbolic Transformer
with a dual-momentum contrastive learning (DMCL) framework, which shifts the focus from background reconstruction
to discriminative representation learning at both global and
local levels. First, a custom-designed multiview data augmentation module generates complementary views from different
perspectives, enriching spectral diversity and alleviating the
limitations of contrastive learning (CL) under homogeneous
samples. Second, a hyperbolic Transformer encoder exploits the
hierarchical and structured nature of hyperspectral data, where
hyperbolic geometry enables more effective attention aggregation
than Euclidean space. Subsequently, a dual-momentum mechanism with dual temporal queues further stabilizes global learning
while dynamically adapting to local changes, thereby mitigating
sensitivity to class imbalance and spectral drift. Finally, in the
detection stage, a sliding dual-window detection strategy with
exponential mapping and guided filtering is employed to suppress
background interference and enhance spatial contrast. Extensive
experiments on multiple real hyperspectral images acquired by
different sensors across various scenes demonstrate that the
proposed HTDC consistently outperforms the state-of-the-art
methods in HAD tasks.
Index Terms—Contrastive learning (CL), dual-momentum,
hyperbolic transformer, hyperspectral anomaly detection (HAD),
multiview data augmentation.
Received 23 September 2025; revised 22 January 2026; accepted
23 February 2026. Date of publication 9 March 2026; date of current version
13 March 2026. This work was supported in part by the National Natural
Science Foundation of China under Grant 42271355 and Grant 62471079,
in part by the Natural Science Foundation of Liaoning Province under Grant
2022-MS-160, and in part by the Fundamental Research Funds for Central
Universities under Grant 3132025251. (Corresponding authors: Enyu Zhao;
Chao Deng.)
The authors are with the Center of Hyperspectral Imaging in Remote Sensing (CHIRS) and the Information Science and Technology College, Dalian
Maritime University, Dalian 116026, China (e-mail: wangyulei@dlmu.edu.cn;
dengchao@dlmu.edu.cn; zhaoenyu@dlmu.edu.cn; yucy@dlmu.edu.cn).
Digital Object Identifier 10.1109/TGRS.2026.3670890

I. I NTRODUCTION
YPERSPECTRAL imaging (HSI) acquires detailed
spectral information across tens to hundreds of contiguous narrow bands, enabling the generation of high-dimensional
spectral response vectors for each pixel while preserving
spatial structures [1], [2]. Due to this unique capability, HSI
has been extensively employed in a wide range of remote
sensing tasks, including classification [3], [4], [5], anomaly
detection [6], [7], [8], target detection [9], [10], [11], and
band selection [12], [13]. From a perspective of material
identification, the fine spectral resolution of HSI enables precise discrimination of subtle compositional variations, which
is particularly advantageous for detecting anomalous targets
in complex backgrounds such as camouflage detection and
pollutant monitoring. In general, anomalies in HSIs exhibit
three characteristics: 1) low probability of occurrence; 2) small
spatial extent; and 3) significant spectral differences from
the surrounding background [14], [15]. Existing hyperspectral
anomaly detection (HAD) methods can be broadly classified
into three categories: statistical-based methods, representationbased methods, and deep learning-based methods, each of
which has produced representative approaches as outlined
below.
Statistical-based methods assume that background pixels
follow a specific distribution, with anomalies identified as
outliers. One of the most representative approaches is the RX
detector [16], which models the background pixels using a
multivariate Gaussian distribution and detects anomalies as
pixels that exhibit significant deviations from this distribution.
However, in real-world scenarios, the background is often too
complex to be accurately represented by a single multivariate
Gaussian model, resulting in degraded detection performance.
Various such as local RX (LRX) [17], weighted RX (WRX)
[18], kernel-based RX (KRX) [19], and recursive RX with
multiattribute profiles [20] attempt to improve the robustness
of the conventional RX detector, but all remain fundamentally constrained by their reliance on predefined distributional
assumptions.
To avoid reliance on inaccurate distribution assumptions,
representation-based methods have attracted significant attention [21]. These approaches represent hyperspectral data
as linear or nonlinear combinations of a set of bases
or dictionaries. Main approaches in this category include

H

1558-0644 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

5507217

low-rank representation (LRR), sparse representation, collaborative representation, and tensor-based modeling. For instance,
the collaborative representation-based detector (CRD) [22] is
designed to exploit the sparsity and locality characteristics of
HSI by assuming that background pixels can be linearly represented by their neighboring pixels, while anomalies cannot.
However, the performance of CRD is sensitive to the selection
of dual-window sizes across different datasets. LRR-based
methods model hyperspectral data as a linear combination
of a small number of intrinsic components, reconstruct the
background, and detect anomalies as reconstruction residuals.
While effective in capturing global structures, LRR tends to
ignore local structural information. To address this limitation,
GTVLRR incorporates graph regularization and total variation
regularization into the LRR model [23], preserving global
structural characteristics while simultaneously capturing local
geometric properties. Given the widespread nature of background distributions in HSI and the rarity of anomalies,
hybrid methods combining low-rank and sparse constraints
have been explored to refine anomaly-background separation.
Representative methods include low-rank and sparse representation (LRASR) [24] and low-rank matrix decomposition using
Mahalanobis distance (LSMAD) [25].
In practical applications, both statistical-based and
representation-based methods encounter significant challenges
when dealing with the complex and high-dimensional nature of
hyperspectral backgrounds. To address these limitations, deep
learning has been increasingly explored in recent years [26],
[27], owing to its ability to model nonlinear spectral–spatial
features. Current deep learning-based HAD methods primarily
focus on three types of architectures: convolutional neural
networks (CNNs), generative adversarial networks (GANs),
and autoencoders (AEs). CNN-based methods are generally
unsuitable for practical anomaly detection tasks due to
their reliance on prior labeled information for supervised
training [28], [29]. To overcome this, DeCNN-AD [30]
introduces a plug-and-play CNN denoiser to regularize
representation coefficients, enabling unsupervised learning
within a traditional framework. Furthermore, to address the
computational burden of retraining and the constraints of
fixed input dimensions often faced by CNNs, AdaptHAD
[31] proposes an adaptive hybrid network that integrates a
CNN with a Transformer to simultaneously extract local
and global features. GANs enhance the generalization ability
of neural networks through adversarial learning [32], [33].
Although their effectiveness in HAD has been demonstrated,
many GAN-based variants suffer from unstable training
and interference from redundant information, leading to
high false-alarm rates and reduced detection accuracy. To
mitigate this, CL-BioGAN [8] incorporates biologically
inspired synaptic plasticity to actively balance memory
stability and learning flexibility, ensuring robust detection in
cross-domain scenarios. In contrast, AE-based methods have
been increasingly adopted in HAD owing to their capacity to
extract deep features with nonlinear characteristics and their
strong unsupervised learning capabilities [34]. For instance,
RGAE [35] integrates graph constraints and superpixel
segmentation, while Auto-AD [36] employs adaptive loss

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

adjustment to avoid manual parameter tuning. However,
AE-based methods may inadvertently reconstruct anomalies
along with the background, thereby degrading detection
performance. GAED [37] addresses this by incorporating a
feedback strategy to suppress the representation of anomaly
features. Similarly, to prevent anomaly leakage, a blind-spot
network [38] utilizing multiscale mask convolutions has
been proposed, while FCAE-DCAC [39] integrates dual
clustering priors with latent feature adversarial consistency
to ensure prioritized background reconstruction. Other
approaches embed physical priors, such as TAEF [40],
which integrates an extended multilinear mixing model and
employs a Transformer for improved performance. In order
to exploit the spatial–spectral characteristics inherent in HSI,
S3S-LTGRMA [41] integrates spectral, spatial, and structural
features through superpixel segmentation and a Transformer
backbone. Beyond Transformers, emerging architectures
have also been explored; MMR-HAD [42] leverages
the Mamba model with random masking to inhibit anomaly
reconstruction, while DWSDiff [43] introduces a dual-window
spectral diffusion model for precise background estimation.
Despite these advances, most AE-based methods remain
fundamentally tied to the reconstruction assumption—that
background pixels can be accurately reconstructed while
anomalies cannot. In practice, anomalies may be partially
reconstructed with the background, causing distortion and
reducing robustness. This problem is exacerbated in highdimensional data with complex land-cover distributions,
where the binary distinction of “background versus anomaly”
often breaks down.
To overcome these limitations, this article moves beyond the
reconstruction paradigm and adopts contrastive learning (CL)
[44], [45], [46] to develop a discriminative anomaly detection
approach driven by intersample differences. Building upon
this, this article proposes a hyperbolic transformer with dualmomentum contrastive learning (HTDC), a unified framework
that synergistically integrates multiview data augmentation, a
hyperbolic Transformer encoder, and a dual-momentum mechanism to enable HAD through CL. In particular, a multiview
data augmentation strategy is employed to generate semantically consistent yet diverse views, providing the foundation
for robust contrastive representation learning. A Transformer
equipped with hyperbolic attention is then constructed to
capture the hierarchical structural dependencies inherent in
HSI. During the CL, a dual-momentum strategy with dynamic
queues is introduced. The high-momentum encoder, updated
slowly with a large momentum coefficient, captures global
contextual semantics, whereas the low-momentum encoder,
updated more frequently with a smaller momentum, focuses
on local, fine-grained spectral representations. In this process, a spectral feature encoder serves as the query branch,
performing CL by comparing its outputs with those from
both momentum branches. Finally, in the detection stage, a
sliding dual-window strategy is applied, combined with a
guided filter and a power function, to effectively suppress
background interference and enhance spatial–spectral contrast.
The main contributions of this work are summarized as
follows.

WANG et al.: HTDC: HYPERBOLIC TRANSFORMER WITH DUAL-MOMENTUM CONTRASTIVE LEARNING FOR HAD

5507217

Fig. 1. Flowchart of the proposed HTDC method.

1) Multiview Augmentation for CL: A strategy that generates
diverse perspectives by simulating data completeness, resolution variation, and band absence. Through Gaussian noise
perturbation and random spectral band masking, it enriches
spectral diversity and alleviates the limitations of CL under
homogeneous samples.
2) Hyperbolic Transformer Encoder: An architecture
built upon the conventional Transformer, incorporating a
hyperbolic-optimized multihead self-attention to exploit the
hierarchical structure of hyperspectral data. By modeling
feature interactions in hyperbolic space, it enhances the representation of complex hierarchical dependencies.
3) DMCL: A spectral discriminative model fundamentally
different from reconstruction-based approaches, incorporating
a dual-momentum mechanism with two temporal queues to
stabilize global optimization while adapting to local variations,
thereby mitigating sensitivity to class imbalance and spectral
drift.
The remainder of this article is organized as follows.
Section II presents the details of the proposed HTDC.
Section III provides experimental results and analysis to
validate the effectiveness of the proposed approach. Finally,
conclusions are drawn in Section IV.
II. M ETHODOLOGY
This section presents a comprehensive overview of the proposed hyperbolic transformer with dual-momentum contrastive

learning (HTDC) framework for HAD. The framework consists of five main components: a multiview data augmentation
to enhance the quality and diversity of data samples, a spectral
feature extraction network based on a hyperbolic Transformer
to capture hierarchical spectral–spatial dependencies, a CL
mechanism with a dual-momentum strategy to improve feature
discrimination, and a dual-window anomaly detection module
that applies the proposed model with background suppression.
The overall architecture of the proposed HTDC is illustrated
in Fig. 1.
A. Multiview Data Augmentation
CL typically begins with data augmentation to increase
data variability and provide diverse views of the same
instance. Conventional augmentation techniques in computer vision—such as cropping, flipping, rotation, and color
transformations—are not well-suited for hyperspectral remote
sensing, particularly in HAD. The heavy reliance on spectral
information makes these conventional methods inadequate for
fully exploiting HSI characteristics. To address this limitation, a multiview data augmentation strategy is proposed that
considers three key aspects: spectral completeness, resolution
variation, and spectral absence, enriching the diversity of data
distribution within the CL framework, as illustrated in Fig. 1.
For spectral completeness, the original data is first preserved without any augmentation to retain its full spectral
information. To simulate resolution variation, Gaussian noise

5507217

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

Fig. 2. Spectral feature extraction via hyperbolic transformer.

is then introduced for the generation of positive and negative
sample pairs used in training [47], [48]. Zero-mean Gaussian
noise introduces mild perturbations to the original highfrequency features, which, in moderate amounts, can enhance
the network’s learning capability, expressed as follows:
X0 = X + β × N

(1)

where X denotes the original input, N is standard Gaussian
noise, and β is set to 0.005.
Finally, spectral absence is simulated through random bandwise masking. In particular, for each spectral band, a random
binary mask is applied to 20% of the pixel values, generating
diverse spectral views. This process emulates partial spectral loss and encourages the model to learn robust feature
representations under missing-band conditions.
B. Spectral Feature Extraction via Hyperbolic Transformer
This section is motivated by two key considerations. First,
constructing a fine-grained spectral feature extraction module
is essential for improving the effectiveness of CL. Second, hyperspectral data naturally exhibit hierarchical spectral
structures: local variations between adjacent bands, holistic
spectral signatures within individual pixels, and statistical
dependencies across the dataset. To model such structures, a
hyperbolic space is introduced, whose non-Euclidean properties are particularly well-suited for representing hierarchical
data distributions. Integrating this geometric framework with
the Transformer architecture enhances the model’s capacity
to represent structured spectral information, as illustrated in
Fig. 2. The spectral feature extraction process consists of two
components: spectral pixel encoding, which performs initial
spectral feature extraction, and the hyperbolic Transformer
module, which models hierarchical dependencies in a hyperbolic latent space.
1) Spectral Pixel Encoding: The first component, spectral pixel encoding, generates high-quality spectral token
sequences to support efficient and fine-grained feature extraction in the hyperbolic Transformer. Considering the inherent
correlations among hyperspectral bands, an Overlapping Spectral Block Embedding (OSBE) module is first employed to

construct these tokens by controlling the overlap between adjacent spectral blocks. This design preserves sufficient spectral
information within each token and enhances the Transformer
encoder’s ability to capture contextual dependencies. In particular, given an input HSI with C spectral bands, a 1-D
convolution layer with a kernel size of k is applied. The stride
parameter s (s < k) controls the degree of overlap between
spectral blocks, with the overlap v defined as
v = k − s.

(2)

In addition, to address the inherent position-invariance of the
standard Transformer self-attention mechanism, both relative
positional encoding (RPE) and dynamic positional encoding
(DPE) are incorporated into the architecture. The RPE module
captures relative positional relationships among spectral bands,
enhancing the Transformer’s capacity to model sequential
dependencies. The encoding is defined as:

pos 
(3)
RPE (pos, 2i) = sin
2i/d
100000

pos
RPE (pos, 2i + 1) = cos
(4)
1000002i/d
where pos denotes the position of the token, i represents the
dimension index, and d indicates the embedding dimension.
In contrast, DPE takes into account the strong local correlations of spectral features by integrating a depthwise separable
convolution (DWC) layer with a kernel size of k = 3, as can
be shown in the left side of Fig. 2.
2) Hyperbolic Transformer Module: While most existing
Transformer-based methods operate in Euclidean space, their
ability to represent the spatial hierarchies of HSI is limited.
Considering that real-world data commonly exhibit hierarchical structures, this article incorporates the geometric properties
of hyperbolic space into the Transformer architecture [49],
[50], [51], [52], [53], [54]. This integration enables more effective modeling of hierarchical dependencies while maintaining
the global context modeling capability of the Transformer, as
illustrated on the right side of Fig. 2, along with the design
of the Hyperbolic multihead self-attention (HMSA) module
shown in Fig. 3.
The hyperbolic Transformer module is built upon the conventional Transformer framework. In the HMSA mechanism,

WANG et al.: HTDC: HYPERBOLIC TRANSFORMER WITH DUAL-MOMENTUM CONTRASTIVE LEARNING FOR HAD

5507217

the Fréchet mean estimation, the number of iterations is fixed
at t = 2, balancing computational efficiency and aggregation
stability.
• Initialization

u1 = pro j A0 · V 0 .
(10)
• Iterative refinement
ut = expcut−1 A0 · logcut−1 V 0
A = pro j (ut )

Fig. 3. HMSA module.

the input matrix X is linearly projected to obtain the query
(Q), key (K), and value (V), as defined below
Q = W q X, K = W k X, V = W v X

(5)

where W q , W k , and W v are the corresponding weight matrices
To embed HMSA in hyperbolic space, a Poincaré projection
is applied, mapping Q, K, and V onto a hyperbolic ball of
radius r, as formulated in (6) and (7). This guarantees that all
computations are performed within hyperbolic space, enabling
more faithful modeling of hierarchical structures compared to
Euclidean formulations.


r · (1 − ε)
pro j (x) = x · min 1,
(6)
kxk + ε
Q0 = pro j (Q) , K 0 = pro j (K) , V 0 = pro j (V)
(7)
where r denotes a learnable radius parameter.
After projection, the attention weights are computed by
measuring the hyperbolic distance between Q and K under
the Poincaré ball model, as defined in the following equation:

d Q0 , K 0
!
2c · kQ0 − K 0 k22
2
−1


= √ cosh
1+
(8)
c
1 − ckQ0 k22 1 − ckK 0 k22 + ε


d (Q0 , K 0 )
0
A = softmax − √
(9)
dk
where c = 1/r2 , ε is a small constant introduced for numerical
stability, and dk is a scaling factor used to prevent the attention
weights from becoming excessively large, thereby ensuring the
stability of the computed values.
Because Euclidean weighted averaging is not directly applicable in hyperbolic space, a hyperbolic aggregation strategy
based on the Fréchet mean is adopted. In particular, the Fréchet
mean is approximated by first performing a logarithmic map
to project the points onto the tangent space, applying weighted
averaging in the Euclidean domain, and then using an exponential map to project the result back into the hyperbolic
space. To ensure numerical stability and geometric validity,
a Poincaré projection is introduced throughout the process to
constrain all results within the unit ball, as demonstrated in
(10)–(15). Furthermore, given the rapid convergence speed of



(11)
(12)

where proj(·) denotes the Poincaré projection operator, and t
refers to the aggregation iteration step.
• Exponential and logarithmic maps




√ λcx kvk
v
c
c
(13)
exp x (v) = x ⊕c tanh
√
2
ckvk
 −x ⊕c y
√
2
logcx (y) = √ c · tanh−1 ck−x ⊕c yk ·
(14)
k−x ⊕c yk
cλ x
where λcx = 2/(1 − ckxk2 ) is the conformal factor, and ⊕c
denotes the Möbius addition in the Poincaré ball in the
following equation:


1 + 2chx, yi + ckyk2 x + 1 − ckxk2 y
(15)
x ⊕c y =
1 + 2chx, yi + c2 kxk2 kyk2
where h·, ·i denotes the inner product, c = 1/r2 , and r denotes
a learnable radius parameter.
Finally, the outputs of all attention heads are concatenated to
form the final output of the HMSA module, shown as follows:
HMSA (X) = Concat (A1 , A2 , . . . , AN )

(16)

where N denotes the number of attention heads.
Subsequently, this concatenated feature is fed into a feedforward network. The feed-forward network in the Hyperbolic
Transformer encoder consists of two linear layers with a
Gaussian error linear units (GELUs) activation in between,
as shown in Fig. 2.
Following the feed-forward stage, a layer normalization
(LN) operation is applied to the output of the Transformer
encoder. This standardizes the feature distribution, mitigating
the internal covariate shift and facilitating smoother convergence for the subsequent contrastive mapping.
C. Dual-Momentum CL
To enable fine-grained CL in HAD tasks, this article moves
beyond the conventional background anomaly dichotomy and
focuses instead on capturing structural differences in spectral
features. To this end, a DMCL framework is proposed to
support hierarchical feature comparison across multiple scales.
In particular, two encoders with distinct momentum coefficients are employed to maintain dual temporal queues: the
high-momentum branch captures stable semantic structures,
while the low-momentum branch enhances responsiveness to
fine-grained spectral anomalies. In addition, a multiview data
augmentation strategy is applied to enrich the diversity and
informativeness of sample pairs. This design facilitates a more
nuanced and hierarchical modeling of contrastive features.

5507217

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

First, a small batch of spectral pixels Xq is randomly
sampled from the original HSI X ∈ RH×W×C . After applying multiview data augmentation, three augmented views are
generated: Xq , Xb , and X s , as defined in (17). Spectral pixels at
the same spatial location across different views are considered
as positive pairs, while those at different locations are treated
as negative pairs
8
 1 2

N
N×B
ˆ
<Xq =  xq ; xq ; · · ·; xq  ∈ R
1 2
N
N×B
(17)
X = x ; x ; · · ·; xb ∈ R
ˆ b  1b 2b

:
N
N×B
X s = x s ; x s ; · · ·; x s ∈ R
where Xq denotes the original spectral data, Xb is produced via
random band masking, and X s is obtained by adding Gaussian
noise.
The query encoder Eq is then applied to Xq , followed
by a projection head MLPq to obtain the feature matrix
Uq . Simultaneously, the high-momentum encoder Eb and the
low-momentum encoder E s extract spectral features from Xb
and X s , respectively. These features are then passed through
corresponding projection heads, MLPb and MLP s , to produce
feature matrices Ub and U s , which are stored in two temporally updated queues for subsequent CL, as expressed in the
following equation:
8
 1 2

N
N×dMLPq
ˆ
<Uq = uq ; uq ; · · ·; uq  ∈ R
1 2
N
(18)
Ub = ub ; ub ; · · ·; ub ∈ RN×dMLPb
ˆ
 1 2

:
N
N×dMLP s
U s = u s ; u s ; · · ·; u s ∈ R
.
Finally, the feature Uq is jointly compared with the features
Ub and U s , which are stored in the high-momentum queue Q1
and the low-momentum queue Q2 , respectively. These features
are fed into a contrastive loss function designed to maximize
the similarity between positive pairs while minimizing the similarity between negative pairs, thereby enforcing the encoder
to learn discriminative spectral representations. In this work,
the similarity between feature pairs is measured using the dot
product. The proposed dual-momentum contrastive loss adopts
the InfoNCE formulation [55], which is defined as follows:

N
exp uiq · uib /τ1
1 X


− log P
(19)
lb =
j
Q1
N
i
i=1
j=0 exp uq · ub /τ1

N
exp uiq · uis /τ2
1 X


ls =
− log P
(20)
Q2
N
exp ui · u j /τ
i=1

j=0

l = λ · lb + (1 − λ) · l s

q

s

2

(21)

where λ serves as a balancing parameter that controls the
relative contributions of two branches, while τ1 and τ2 denote
the temperature parameters associated with the two momentum
queues, respectively. Each InfoNCE loss term consists of one
positive sample embedding (anchor) and a set of negative
sample embeddings drawn from the queues Q1 and Q2 .
During training, the consistency of the dual memory queues
is maintained via momentum update mechanisms. To balance
the learning of global and local spectral features.
1) The high-momentum encoder Eb employs a larger
momentum coefficient n, resulting in slower parameter updates
that preserve the long-term statistical characteristics of HSI.

A larger queue, Q1 , is also maintained to store extensive
historical negatives, enhancing the learning of global spectral
invariance.
2) The low-momentum encoder E s , in contrast, uses a
smaller momentum coefficient m, enabling faster updates that
improve sensitivity to local spectral variations. A smaller
negative sample queue Q2 is also adopted to reduce the impact
of outdated negative samples on local discriminative learning.
The overall parameter update process can be formally defined
as follows:
8
θb ← nθb + (1 − n) θq
ˆ
ˆ
ˆ
<θ
b-MLP ← nθb-MLP + (1 − n) θq-MLP
(22)
ˆ
(1
θ
ˆ
ˆ s ← mθ s + − m) θq
:
θ s-MLP ← mθ s-MLP + (1 − m) θq-MLP
where θq , θb , and θ s denote the parameters of the encoders
Eq , Eb , and E s , respectively, while θq−MLP , θb−MLP , and θ s−MLP
correspond to the parameters of the projection heads MLPq ,
MLPb , and MLP s , respectively. In contrast, the query encoder
Eq and its projection head MLPq are updated through gradient
backpropagation. An overview of the relationships among
these parameters is provided in Fig. 1.
D. Anomaly Detection
In the detection phase, the original HSI is fed into the
well-trained model to effectively identify anomalies in the
feature space. Owing to its self-supervised training scheme,
the proposed method functions as a reliable discriminative
detector. In the learned feature space, the anomalous targets
exhibit distinctive characteristics compared to their surrounding backgrounds.
1) Sliding Dual-Window Anomaly Detection: An anomaly
detection strategy based on a sliding dual window is adopted.
The inner and outer window sizes of the dual window are set
to 3 and 5, respectively. Given an input HSI, each pixel to be
tested is paired with its 16 surrounding pixels within the outer
window to form multiple pixel pairs. The model computes
similarity scores for each pair, and the average of these scores
is taken as the final output. If the score exceeds a predefined
threshold η, the pixel is classified as an anomaly; otherwise,
it is considered background.
2) Background Suppression: To suppress background
responses in the detection map R, a three-stage suppression
strategy is employed. First of all, an exponential mapping is
applied to amplify the relative intensity differences between
anomalous and background pixels. This operation enhances
anomaly saliency by expanding the separation between weak
anomaly signals and background clutter, thereby producing a
refined detection map Y [as can be described in (23)]. Then,
a guided filtering with spatial smoothing is applied, where
the 2-D spatial structure of the HSI is leveraged through
recursive filtering within a guided filter. This step enforces
local spatial consistency, suppresses isolated noisy responses,
and preserves structural boundaries, ensuring that anomalies
are highlighted without introducing excessive blurring. Finally,
a normalization operation is performed to standardize the
refined detection scores across the entire image. This operation

WANG et al.: HTDC: HYPERBOLIC TRANSFORMER WITH DUAL-MOMENTUM CONTRASTIVE LEARNING FOR HAD

5507217

TABLE I
S OME H YPERSPECTRAL I MAGE C HARACTERISTICS OF F IVE DATASETS

Fig. 4. (Top row) Pseudo-color images of five hyperspectral datasets, (middle
row) corresponding ground truth maps, and (bottom row) 3-D view of the GT
maps.

balances scale variations among different datasets and further
clarifies the separation between anomalies and background
regions. The overall suppression process is formulated in the
following equations:
Y = βR

(23)

√ !o !
√ !o
2
2
hi = 1 − exp −
hi−1
yi + exp −
ε1
ε1

i 
X
ε1
si = f0 +
1 + | f j − f j−1 |
ε2

(24)
(25)

j=1

mi =

hi − hmin
hmax − hmin

(26)

where β is a parameter that controls the strength of background
suppression, hi denotes the filtered result, yi represents the
anomaly score obtained from the sliding dual-window, and
mi is the final detection result. The spatial distance between
adjacent pixels in the transformed domain is denoted as o =
si –si−1 , while ε1 and ε2 correspond to the standard deviations
in the spatial and range domains, respectively. Furthermore, fi
denotes the value of the ith pixel in the guidance image F,
which is constructed as a pseudo-color image formed by the
first three principal components (PCs) of the input HSI.
III. E XPERIMENTAL R ESULTS AND A NALYSIS
In this section, a comprehensive set of experiments is
conducted on five hyperspectral datasets to validate the effectiveness of the proposed HTDC in terms of anomaly detection
performance, where Section III-A describes the hyperspectral datasets used in the experiments, Section III-B outlines
the comparison methods and evaluation metrics employed
in the experiments, Section III-C provides a brief introduction of hardware environment and parameter settings,
Section III-D presents the experimental results of the proposed
method against eight state-of-the-art methods, Section III-E
discusses the ablation studies, and Section III-F discusses the
computational complexity analysis.

A. Experimental Datasets
To validate the proposed HTDC framework, experiments
are conducted on five real-world datasets: Texas Coast, Los
Angeles, Beach, Gulfport, and Pavia. These datasets represent
diverse anomaly detection scenarios, with variations in spectral
bands, spatial resolution, anomaly percentage, and anomaly
type. The detailed characteristics of each dataset, including
sensor type, spatial resolution, image size, number of spectral
bands, number of anomalies, anomaly ratio, and anomaly
types, are summarized in Table I. Furthermore, Fig. 4 presents
the pseudo-color images, the corresponding ground-truth (GT)
maps of anomalous targets, and the 3-D visualizations of
the GT maps for each dataset. In Figs. 4–14, the color
gradient from blue to red indicates anomaly probability, with
regions approaching bright red signifying a higher likelihood
of anomalies.
B. Comparison Methods and Evaluation Criteria
This section introduces comparison methods, including traditional methods and deep learning, as well as evaluation
metrics, including AUC values, ROC curves, and box plots.
1) Comparison Methods: To validate the effectiveness of
the proposed HTDC framework, it is compared against eight
representative state-of-the-art approaches, encompassing both
traditional statistical models and deep learning-based models.
The traditional baselines include 2S-GLRT [56], GTVLRR
[23], and AHMID [57], while the deep learning-based models
include GAED [37], RGAE [35], Auto-AD [36], GIL-HAD
[58], and NL2Net [59]. These baselines are carefully chosen
to ensure a fair and comprehensive evaluation, as they collectively cover different methodological paradigms.
2) Evaluation Metrics: The detection performance of different methods is assessed using both visual and quantitative
evaluation metrics. For visual evaluation, both 2-D view and
3-D view of detection results are provided, together with 3-D
ROC (3-D ROC) curves and their corresponding 2-D projections (2-D ROC) of (PD , PF ), (PD , τ), and (PF , τ) [60], [61].
These visualizations provide intuitive insight into the tradeoffs
between detection probability, false-alarm rate, and threshold

5507217

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

Fig. 5. 2-D view of anomaly detection results for the Texas Coast dataset.

Fig. 6. 3-D view of anomaly detection results for the Texas Coast dataset.

Fig. 7. 2-D view of anomaly detection results for the Los Angeles dataset.

Fig. 8. 3-D view of anomaly detection results for the Los Angeles dataset.

Fig. 9. 2-D view of anomaly detection results for the Beach dataset.

Fig. 10. 3-D view of anomaly detection results for the Beach dataset.

variation. For quantitative evaluation with a more rigorous
comparison, multiple AUC metrics as listed in Table II
are employed, including AUC (PD , PF ), AUCTD , AUCBS ,
AUCODP , AUCTD−BS , and AUCSNPR [62]. AUC (PD , PF ) is the

fundamental metric, reflecting the overall effectiveness of the
anomaly detector. AUCTD evaluates the effectiveness of both
the detector and the detectability of the targets. AUCBS measures the background suppression capability of the detector.

WANG et al.: HTDC: HYPERBOLIC TRANSFORMER WITH DUAL-MOMENTUM CONTRASTIVE LEARNING FOR HAD

5507217

Fig. 11. 2-D view of anomaly detection results for the Gulfport dataset.

Fig. 12. 3-D view of anomaly detection results for the Gulfport dataset.

Fig. 13. 2-D view of anomaly detection results for the Pavia dataset.

Fig. 14. 3-D view of anomaly detection results for the Pavia dataset.

TABLE II
S UMMARY OF THE AUC I NDEXES

performance, incorporating aspects such as signal-to-noise
ratio and target–background discrimination. This combination
of visual and quantitative metrics ensures a comprehensive and
multiperspective evaluation of different models, allowing both
qualitative interpretation and numerical comparison of detector
performance.
Moreover, to further evaluate the separation between backgrounds and anomalies obtained by different algorithms, box
plots are employed for comparative analysis. In particular, the
values of the detected anomalies and backgrounds are first
normalized, after which statistical computations are used to
generate box representations for both categories. For all five
datasets, values within the [10% and 90%] range are retained
to characterize the distributions of anomaly and background
pixels, reducing the influence of extreme outliers. It is worth
noting that although the percentile thresholds can be adjusted,
the [10%, 90%] range is commonly adopted in most cases.
C. Experimental Setup

AUCODP indicates the overall detection probability. AUCTD-BS
assesses the separability between background and target.
AUCSNPR provides a comprehensive assessment of detection

This section mainly introduces the experimental environment and parameter configurations of both the proposed
HTDC and the comparison baselines.

5507217

1) Experimental Environment: The experiments are conducted on two hardware platforms. For deep learning-based
methods, the environment consists of a 24 vCPU AMD EPYC
7642 48-Core Processor and RTX 3090 24-GB GPU. The
implementation is carried out using PyTorch 1.10, Python
3.8, and MATLAB R2023a. While for traditional statistical
methods, an Intel Core i7-10510U CPU is used, with implementations completed in MATLAB R2023a.
2) Parameter Settings of HTDC: All hyperparameters of
the proposed HTDC are empirically selected to ensure consistent performance across datasets: the OSBE parameters (k, s)
are set to (9, 4) for all datasets. The hyperbolic Transformer
module is configured with a depth of 2, 8 attention heads, and
8 neurons in each MLP layer. The sizes of the dual temporal
queues (Q1 , Q2 ) are set to (10 000, 2000) across all datasets.
During the training phase, the network is optimized using the
layerwise adaptive rate scaling (LARS) optimizer. The initial
learning rate l is set to 0.05 and is dynamically adjusted using
a cosine annealing scheduler. The temperature coefficients (τ1 ,
τ2 ) are set to (0.1, 0.05), and the momentum coefficients (n, m)
are set to (0.999, 0.8). The number of training epochs is set to
50 for the contrastive stage and 200 for dataset-specific finetuning. For all datasets, the batch size is set to 400, and the
balance parameter λ is set to 0.5. The detection dual-window
sizes are fixed at (3, 5). As for the background suppression
process, β is set to 10, 20, 50, 20, and 10 for the Texas Coast,
Los Angeles, Beach, Gulfport, and Pavia datasets, respectively. The parameter ε1 (used to control the window size of
the filter), the parameter ε2 (used to control the ambiguity
of the filter), and the number of iterations (performed in the
guided filter) are set to (3, 2.5, 0.5), (3, 1.2, 0.5), (3, 2.5, 1), (3,
2.5, 0.5), and (3, 2.5, 0.5) for the Texas Coast, Los Angeles,
Beach, Gulfport, and Pavia datasets, respectively.
3) Parameter Settings of Comparison Methods: For a fair
comparison, baseline methods are configured according to the
optimal parameters recommended in their respective references. For 2S-GLRT in [56], the outer and inner window sizes
are set to 7 and 5. For GTVLRR in [23], the number of clusters
K and total number of pixels per cluster P are set to 15 and 20,
respectively, with parameters λ = 0.5, β = 0.2, and γ = 0.05.
For AHMID [57], the parameters α, λ, and the number of
layers are set to 1, 0.05, and 1, respectively. For GAED in
[37], the second to sixth layer sizes are set to 100, 50, 25, 50,
and 100, respectively, window size c = 7, learning rate l = 0.4,
number of iterations = 300, and penalty β = 1. For RGAE in
[35], the weight parameter, number of superpixels, and hidden
layer dimension are set to 0.01, 150, and 100, respectively. For
Auto-AD in [36], the number of training epochs is set to 50
across all five datasets, with a loss threshold of 1.0 × 10−5 .
For GIL-HAD in [58], the size of the N(p) = 7 × 7, learning
rate LR = 0.01, reg noise = 0.1, layers = 5, and threshold
τ = 0.000015. For NL2Net in [59], the parameter PD = 5,
the learning rate = 1.0 × 10−4 , and the number of training
epochs = 100.
D. Results and Analysis
This section presents a comprehensive evaluation of the
proposed HTDC method through a series of experiments,

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

comparing it with eight state-of-the-art approaches mentioned
above.
Figs. 5–14 show the detection maps of nine different
anomaly detection methods on five HSI datasets. Since 2-D
detection maps cannot fully reflect the detection performance,
this article provides corresponding 3-D visualizations for
enhanced interpretability. Figs. 15(b)–19(b) present the ROC
curves in the (PD , PF ) space for all methods on each dataset,
where curves closer to the upper-left corner indicate better
performance. Figs. 15(c)–19(c) illustrate the ROC curves in the
(PD , τ) space, where curves approaching the upper-left corner
signify superior results. Figs. 15(d)–19(c) display the ROC
curves in the (PF , τ) space, with curves closer to the lowerleft corner indicating better performance. Figs. 15(a)–19(a)
show the 3-D ROC curves for each dataset, from which
eight key evaluation metrics are derived to comprehensively
assess detection capability. The highest performance indices
are highlighted in bold, and the second-best results are marked
with an underline.
To provide a detailed analysis of the evaluation metrics,
the Texas Coast dataset is taken as an example. As shown
in Fig. 5, the detection results of different methods are compared. Traditional methods fail to achieve clear and complete
anomaly detection. Except for GAED and Auto-AD, most
deep learning-based methods can identify the contours and
locations of anomalies; however, they exhibit relatively weak
background suppression. Taking GIL-HAD as an example,
both the proposed HTDC and GIL-HAD can effectively detect
anomalies, but the targets detected by GIL-HAD are less
prominent compared to those by HTDC. As reported in
Table III, the proposed method achieves a detection accuracy
of 0.9987, which is 12% higher than that of GTVLRR, the
method with the lowest performance. For the AUC (PF , τ)
metric, the proposed method ranks second, slightly behind
Auto-AD. However, HTDC outperforms Auto-AD by 1.12% in
the AUC (PD , PF ) metric, indicating that Auto-AD’s superior
anomaly detection comes at the cost of weaker background
suppression. Compared with GIL-HAD, the HTDC improves
the overall detection accuracy by 0.54% and outperforms it
across the remaining seven evaluation metrics.
For the Los Angeles dataset, the detection results are shown
in Fig. 7. AHMID, RGAE, GIL-HAD, NL2Net, and HTDC
can accurately localize all anomaly positions and contours.
However, the results of 2S-GLRT and Auto-AD contain
significant background interference, embedding the detected
targets into the background and making them difficult to
observe. GTVLRR is severely affected by noise. As shown
in Table III, with background suppression evaluated using the
AUC (PF , τ), the proposed method ranks second. For all other
evaluation metrics, HTDC outperforms all competing methods.
Compared with Auto-AD, although the proposed method ranks
slightly lower in background suppression, it surpasses AutoAD across all other metrics.
For the Beach dataset, the detection results are shown
in Fig. 9. Except for 2S-GLRT, all other methods are able
to accurately localize the anomaly positions and contours.
The 2S-GLRT result map contains significant background
interference, embedding the detected targets and making them

WANG et al.: HTDC: HYPERBOLIC TRANSFORMER WITH DUAL-MOMENTUM CONTRASTIVE LEARNING FOR HAD

5507217

Fig. 15. ROC curves for the Texas Coast dataset. (a) 3-D ROC curve. (b) 2-D ROC curve of (PD , PF ). (c) 2-D ROC curve of (PD , τ). (d) 2-D ROC curve
of (PF , τ).

Fig. 16. ROC curves for the Los Angeles dataset. (a) 3-D ROC curve. (b) 2-D ROC curve of (PD , PF ). (c) 2-D ROC curve of (PD , τ). (d) 2-D ROC curve
of (PF , τ).

Fig. 17. ROC curves for the Beach dataset. (a) 3-D ROC curve. (b) 2-D ROC curve of (PD , PF ). (c) 2-D ROC curve of (PD , τ). (d) 2-D ROC curve of (PF ,
τ).

Fig. 18. ROC curves for the Gulfport dataset. (a) 3-D ROC curve. (b) 2-D ROC curve of (PD , PF ). (c) 2-D ROC curve of (PD , τ). (d) 2-D ROC curve of
(PF , τ).

unobservable, along with a number of false alarms. GTVLRR
is heavily affected by noise. AHMID, RGAE, GAED, GILHAD, and NL2Net exhibit varying degrees of background
interference, and AHMID in particular produces a large number of false detections. As shown in Table III, the HTDC
method ranks second in terms of AUC (PF , τ), AUC (PD ,
τ), and AUCTD , while outperforming all other methods in

the remaining evaluation metrics. Compared with Auto-AD,
although the detection map of HTDC shows similar background suppression and target detection performance, the
proposed method outperforms Auto-AD across all evaluation
metrics, as detailed in Table III.
For the Gulfport dataset, the detection results are shown in
Fig. 11. HTDC and NL2Net successfully detect most small

5507217

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

Fig. 19. ROC curves for the Pavia dataset. (a) 3-D ROC curve. (b) 2-D ROC curve of (PD , PF ). (c) 2-D ROC curve of (PD , τ). (d) 2-D ROC curve of (PF ,
τ).
TABLE III
AUC VALUES C OMPUTATION OF D IFFERENT M ETHODS ON F IVE DATASETS : (I) T EXAS C OAST,
(II) L OS A NGELES , (III) B EACH , (IV) G ULFPORT, AND (V) PAVIA

targets as well as some large ones. In contrast, the other
methods fail to detect small targets by visual inspection, as
they tend to over-suppress the background at the cost of
missing a large portion of the anomalies. The targets detected
by GAED remain embedded in the background and are barely
visible upon inspection. As illustrated in Fig. 11, HTDC

demonstrates superior anomaly highlighting and background
suppression capabilities compared with other competing algorithms. According to Table III, although the AUC (PF , τ)
metric is not dominant, the proposed method ranks first across
the remaining seven evaluation metrics, indicating strong performance in anomaly detection, background suppression, and

WANG et al.: HTDC: HYPERBOLIC TRANSFORMER WITH DUAL-MOMENTUM CONTRASTIVE LEARNING FOR HAD

5507217

Fig. 20. Box plot of comparison algorithms for five datasets. (a) Coast dataset. (b) Los Angeles dataset. (c) Beach dataset. (d) Gulfport dataset. (e) Pavia.

background–target separation. Moreover, the method achieves
a detection accuracy of 0.9860, which is 6.17% higher than
the second-best result achieved by NL2Net. Compared with
GIL-HAD, the proposed method improves the detection rate
by 12.22%.
For the Pavia dataset, the detection results are shown in
Fig. 13. The experimental results demonstrate the superior
robustness of the proposed method compared to state-ofthe-art competitors. While Auto-AD struggles significantly
with a lower detection rate of 0.9910, likely due to oversuppression of targets in complex backgrounds, the proposed
method maintains high confidence and stability. According
to the table, although the AUCSNPR metric is not dominant
compared to Auto-AD, the proposed method ranks first in
critical metrics, including AUCTD , AUCODP , and AUC (PD ,
τ). This indicates exceptional capabilities in background-target
separation and anomaly highlighting without sacrificing signal
integrity. In particular, the method achieves a remarkable
detection accuracy of 0.9993. This result is 0.45% higher
than the runner-up GAED and outperforms Auto-AD by a
significant margin of 0.83%, comprehensively validating its
effectiveness in handling challenging scenarios.
To further validate the detection results, 3-D views
of the detection results were performed, as shown in
Figs. 6, 8, 10, 12, and 14. Compared to traditional 2-D
detection results, the 3-D visualization represents the “anomaly
score” in the form of height, offering a clearer representation
of the prominence of anomalies relative to the background.
As shown in Figs. 6, 8, 10, 12, and 14, anomalies in all
five datasets are significantly elevated above the background,
demonstrating the method’s strong separability. Moreover, the
anomaly detection results exhibit high spatial consistency with
the ground truth maps, being more closely aligned with the
true anomalies than other methods, thereby reflecting a higher
detection accuracy. Simultaneously, the background regions in
all five datasets are relatively flat, indicating strong background
suppression capability. In conclusion, the proposed method
effectively enhances detection performance and the ability to
separate anomalies from the background.
To visually verify the separability between the background
and anomalies, boxplots of the detection scores from nine
methods are illustrated in Fig. 20. To mitigate the influence
of outliers, the distributions are plotted after excluding the

top and bottom 10% of pixel values. In each subfigure, red
boxes indicate the distribution of anomalous targets, while
green boxes represent the background. The central horizontal
line denotes the median, and the upper and lower boundaries
indicate the value range. Ideally, a compact background box
(indicating strong suppression) and a large gap between the
target and background boxes (indicating high separability)
are desired. As observed, on the Texas Coast dataset, the
proposed HTDC exhibits strong target responses with background maximum values compressed near zero. For the Beach
and Gulfport datasets, although the median target scores
of HTDC are slightly lower than those of GTVLRR and
NL2Net, the latter methods exhibit significantly higher background residuals (elevated green boxes). Consequently, HTDC
achieves a superior contrast ratio. Consistently across all five
datasets, HTDC yields the distinctest margin between the
target and background distributions with virtually no overlap.
The highly compact background boxes further confirm the
method’s robust suppression capability. In summary, the proposed method effectively suppresses background interference
and maximizes the separability of anomalies.
Overall, the proposed HTDC method successfully and
comprehensively detects all of the anomalous targets while
demonstrating strong background suppression capabilities in
complex environments. As shown in Figs. 15–19, the 3-D ROC
and the corresponding 2-D ROC curves further highlight the
superior overall performance of HTDC. In addition, the eight
metrics in Table III also indicate that HTDC exhibits excellent
detection capabilities across various aspects. Therefore, HTDC
shows outstanding detection performance in both qualitative
and quantitative analyses.
E. Ablation Article
In this section, a comprehensive ablation study is conducted
to evaluate the effectiveness of different modules within the
proposed HTDC method. To clearly isolate the contribution
of each component, the study is divided into two parts: 1) an
analysis of the momentum CL framework and 2) an analysis
of the core functional components, specifically the geometric
space and data augmentation strategies. The visualization
of the detection accuracy for these variants is presented in
Figs. 21 and 22.

5507217

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

TABLE IV
D ETAILED S ETTINGS OF D IFFERENT C ASES IN A BLATION E XPERIMENTS

Fig. 21.
Detection accuracy comparison between MOCO-HAD and the
proposed method.

Fig. 23. Running time of the comparative methods on five datasets.

Fig. 22. Detection accuracy comparison for variants of the proposed method.

1) Effectiveness of Parameter Update Strategy: The impact
of the training framework is first evaluated by comparing
the proposed DMCL with the conventional single-momentum
[momentum contrast (MoCo)] approach (referred to as
MOCO-HAD) [52], [63]. For MOCO-HAD, data augmentation is performed using Gaussian noise (with β = 0.005),
the momentum coefficient is set to 0.999, the temperature
parameter is set to 0.07, and the queue length is set to
10 000. Crucially, to ensure a fair comparison, the feature
extraction networks of both the proposed method and MCT
are consistently based on the spectral feature extraction via
hyperbolic Transformer proposed in this article.
Fig. 21 visualizes the AUC (PD , PF ) performance comparison using a radar chart. Visually, the curve of the proposed
method completely encloses that of MOCO-HAD, indicating superior detection accuracy across all five hyperspectral
datasets. A critical observation lies in the shape of the
polygons. While MOCO-HAD exhibits a sharp contraction
along the Gulfport axis, the proposed method maintains a
high AUC (PD , PF ) of 0.9860. This result confirms that our
method effectively eliminates the “performance bottleneck”
observed in the baseline, demonstrating exceptional capability
in handling challenging scenarios.

2) Contribution of Core Components: Based on the dualmomentum framework, the specific contributions of the
hyperbolic geometry and multiview augmentation were further
investigated. As detailed in Table IV, four variants (denoted as
A, B, C, and proposed) are designed to isolate these components. In the experimental setup for Case C, the Euclidean
Transformer (i.e., the standard Transformer architecture) is
configured with a depth of 2, 8 attention heads, and 8 neurons
in each MLP layer. These hyperparameters are kept consistent with the Hyperbolic setting to ensure a fair comparison
regarding the geometric space.
Fig. 22 presents the radar chart of AUC (PD , PF ) performance across five hyperspectral datasets. Visually, the
enclosed area of the proposed method is the largest, indicating
superior overall performance. More importantly, the shape
consistency reveals significant differences in robustness. Methods A and B exhibit a “star-like” shape with sharp contractions
along the Los Angeles and Gulfport axes, indicating their
vulnerability to complex background clutter in these specific
scenes. In contrast, the proposed method maintains a quasiregular pentagonal shape, demonstrating that it effectively
mitigates the performance degradation observed in other methods. The proposed method essentially “closes the gap” on
the challenging datasets while retaining near-perfect scores
on easier tasks (e.g., Texas Coast), confirming its excellent
generalization capability.
F. Computational Complexity Analysis
To comprehensively evaluate the proposed HTDC, the
computational efficiency of all methods is further compared.
Table V reports the computational complexity metrics, including the number of parameters (Params) and floating point
operations (FLOPs) on the five datasets. Fig. 23 displays

WANG et al.: HTDC: HYPERBOLIC TRANSFORMER WITH DUAL-MOMENTUM CONTRASTIVE LEARNING FOR HAD

5507217

TABLE V
C OMPUTATIONAL C OMPLEXITY OF D IFFERENT M ETHODS ON F IVE DATASETS

the running times (e.g., training time and inference time) of
various detectors for all detectors applied to the five datasets
under consideration.
1) Model Complexity: Regarding model complexity, HTDC
demonstrates an exceptional lightweight advantage. As
reported in Table V, the parameter count of HTDC is constant
at 1.4604 M, which is significantly lower than that of largescale models like Auto-AD. Most notably, HTDC achieves the
lowest computational cost in terms of FLOPs. In particular
on the Texas Coast dataset, HTDC requires only 0.0399 G
FLOPs, standing in sharp contrast to the 11.9589 G required
by Auto-AD. This indicates that our method is extremely
energy-efficient, making it particularly suitable for resourceconstrained platforms where power consumption is a critical
constraint.
2) Time Consumption: The computational efficiency of
the compared methods is visualized in Fig. 23. Note that a
logarithmic scale is used to accommodate the vast differences
in time costs. In the train phase, traditional methods (e.g.,
GTVLRR and 2S-GLRT) do not involve a training stage. In
contrast, deep learning-based methods, including the proposed
HTDC, require a training phase to learn feature representations. The proposed HTDC incurs a moderate training time,
which is comparable to that of RGAE but higher than that of
simple lightweight models like Auto-AD. Crucially, it is worth
noting that training is a one-time, offline computational cost.
Once the model is trained, it can be deployed permanently
without reoptimization. Therefore, the training overhead does
not impact the real-time detection capability. Real-time capability is determined by inference time. Traditional methods
suffer from heavy computational burdens due to iterative
optimization, taking tens to hundreds of seconds per image. In
contrast, HTDC demonstrates a significant speedup. Taking the
Texas Coast dataset as an example, HTDC records an inference
time of approximately 4.5 s, achieving a speedup of nearly
two orders of magnitude compared to traditional approaches.
While slightly slower than millisecond-level networks due to
the sophisticated feature extraction, this acceptable latency is
a worthy tradeoff for the superior detection accuracy.
IV. C ONCLUSION
To address the vulnerability of reconstruction-based HAD
methods to contamination from anomalous pixels during
background reconstruction, this article proposes a multiview

DMCL framework. The proposed method adopts a two-stage
design. In the training stage, a multiview data augmentation strategy is employed to generate semantically consistent
yet diverse sample pairs for CL. Subsequently, a hyperbolic
Transformer-based feature extraction module is integrated with
CL, incorporating both a dual-momentum update strategy and
hyperbolic space optimization to facilitate multilevel modeling
of local geometric structures and global spectral information.
This design enhances the model’s ability to learn discriminative spectral representations for distinguishing anomalies
from the background. In the testing stage, the pretrained
model is applied to anomaly detection using a sliding dualwindow strategy, enabling fine-grained response to anomalous
regions. To further optimize detection results, several postprocessing techniques are employed, including exponential
transformation, normalization, and guided filtering, effectively
suppressing background interference and enhancing anomaly
saliency. Extensive experiments and ablation studies conducted
on five real-world hyperspectral datasets confirm that the
proposed HTDC framework consistently outperforms eight
state-of-the-art methods in terms of detection accuracy and
robustness.
Future efforts will be directed toward extending the
framework to address large-scale anomaly detection scenarios through implementation optimization. Moreover,
spatial–spectral attention mechanisms are planned to be integrated to enhance performance, with potential applications on
resource-constrained edge devices.
R EFERENCES
[1]
[2]
[3]

[4]

[5]

S.-E. Qian, “Hyperspectral satellites, evolution, and development
history,” IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens., vol. 14,
pp. 7032–7056, 2021.
C. Yu et al., “Distillation-constrained prototype representation network
for hyperspectral image incremental classification,” IEEE Trans. Geosci.
Remote Sens., vol. 62, 2024, Art. no. 5507414.
X. Chen, L. Gao, M. Zhang, C. Chen, and S. Yan, “Spectral–spatial
adversarial multidomain synthesis network for cross-scene hyperspectral
image classification,” IEEE Trans. Geosci. Remote Sens., vol. 62, 2024,
Art. no. 5518716.
C. Yu, Y. Zhu, Y. Wang, E. Zhao, Q. Zhang, and X. Lu, “Concern with
center-pixel labeling: Center-specific perception transformer network for
hyperspectral image classification,” IEEE Trans. Geosci. Remote Sens.,
vol. 63, 2025, Art. no. 5514614.
E. Zhao, N. Qu, Y. Wang, C. Gao, and J. Zeng, “TEBS:
Temperature–emissivity–driven band selection for thermal infrared
hyperspectral image classification with structured state-space model and
gated attention,” Int. J. Appl. Earth Obs. Geoinf., vol. 142, Aug. 2025,
Art. no. 104710.

5507217

[6]

H. Su, Z. Wu, H. Zhang, and Q. Du, “Hyperspectral anomaly detection:
A survey,” IEEE Geosci. Remote Sens. Mag., vol. 10, no. 1, pp. 64–90,
Mar. 2022.
[7] C.-I. Chang, “Hyperspectral anomaly detection: A dual theory of hyperspectral target detection,” IEEE Trans. Geosci. Remote Sens., vol. 60,
2022, Art. no. 5511720.
[8] J. Wang, Z. Hua, W. Zhang, S. Hao, Y. Yao, and M. Gong, “CLBioGAN: Biologically inspired cross-domain continual learning for
hyperspectral anomaly detection,” IEEE Trans. Geosci. Remote Sens.,
vol. 63, 2025, Art. no. 5514715.
[9] Y. Wang, X. Chen, F. Wang, M. Song, and C. Yu, “Meta-learning based
hyperspectral target detection using Siamese network,” IEEE Trans.
Geosci. Remote Sens., vol. 60, 2022, Art. no. 5527913.
[10] S. Feng, R. Feng, D. Wu, C. Zhao, W. Li, and R. Tao, “A coarseto-fine hyperspectral target detection method based on low-rank tensor
decomposition,” IEEE Trans. Geosci. Remote Sens., vol. 61, 2023, Art.
no. 5530413.
[11] H. Wang, Y. Wang, Y. Yang, E. Zhao, and J. Zeng, “Breaking dimensional barriers in hyperspectral target detection: Atrous convolution with
gramian angular field representations,” Infr. Phys. Technol., vol. 143,
Dec. 2024, Art. no. 105623.
[12] Y. Zhou, Q. Yao, S. Huo, and X. Li, “Hyperspectral band selection with
iterative graph autoencoder,” IEEE Trans. Geosci. Remote Sens., vol. 61,
2023, Art. no. 5511013.
[13] Y. Wang, H. Ma, Y. Yang, E. Zhao, M. Song, and C. Yu, “Self-supervised
deep multi-level representation learning fusion-based maximum entropy
subspace clustering for hyperspectral band selection,” Remote Sens.,
vol. 16, no. 2, p. 224, Jan. 2024.
[14] D. Manolakis and G. Shaw, “Detection algorithms for hyperspectral
imaging applications,” IEEE Signal Process. Mag., vol. 19, no. 1,
pp. 29–43, Jan. 2002.
[15] Z. Wu, W. Zhu, J. Chanussot, Y. Xu, and S. Osher, “Hyperspectral
anomaly detection via global and local joint modeling of background,”
IEEE Trans. Signal Process., vol. 67, no. 14, pp. 3858–3869, Jul. 2019.
[16] I. S. Reed and X. Yu, “Adaptive multiple-band CFAR detection of an
optical pattern with unknown spectral distribution,” IEEE Trans. Acoust.,
Speech, Signal Process., vol. 38, no. 10, pp. 1760–1770, Oct. 1990.
[17] S. Matteoli, T. Veracini, M. Diani, and G. Corsini, “A locally
adaptive background density estimator: An evolution for RX-based
anomaly detectors,” IEEE Geosci. Remote Sens. Lett., vol. 11, no. 1,
pp. 323–327, Jan. 2014.
[18] Q. Guo, B. Zhang, Q. Ran, L. Gao, J. Li, and A. Plaza, “Weighted-RXD
and linear filter-based RXD: Improving background statistics estimation
for anomaly detection in hyperspectral imagery,” IEEE J. Sel. Topics
Appl. Earth Observ. Remote Sens., vol. 7, no. 6, pp. 2351–2366, Jun.
2014.
[19] H. Kwon and N. M. Nasrabadi, “Kernel RX-algorithm: A nonlinear
anomaly detector for hyperspectral imagery,” IEEE Trans. Geosci.
Remote Sens., vol. 43, no. 2, pp. 388–397, Feb. 2005.
[20] F. He et al., “Recursive RX with extended multi-attribute profiles for
hyperspectral anomaly detection,” Remote Sens., vol. 15, no. 3, p. 589,
Jan. 2023.
[21] Q. Ling, Y. Guo, Z. Lin, and W. An, “A constrained sparse representation model for hyperspectral anomaly detection,” IEEE Trans. Geosci.
Remote Sens., vol. 57, no. 4, pp. 2358–2371, Apr. 2019.
[22] W. Li and Q. Du, “Collaborative representation for hyperspectral
anomaly detection,” IEEE Trans. Geosci. Remote Sens., vol. 53, no. 3,
pp. 1463–1474, Mar. 2015.
[23] T. Cheng and B. Wang, “Graph and total variation regularized lowrank representation for hyperspectral anomaly detection,” IEEE Trans.
Geosci. Remote Sens., vol. 58, no. 1, pp. 391–406, Jan. 2020.
[24] Y. Xu, Z. Wu, J. Li, A. Plaza, and Z. Wei, “Anomaly detection in
hyperspectral images based on low-rank and sparse representation,”
IEEE Trans. Geosci. Remote Sens., vol. 54, no. 4, pp. 1990–2000, Apr.
2016.
[25] Y. Zhang, B. Du, L. Zhang, and S. Wang, “A low-rank and sparse matrix
decomposition-based Mahalanobis distance method for hyperspectral
anomaly detection,” IEEE Trans. Geosci. Remote Sens., vol. 54, no. 3,
pp. 1376–1389, Mar. 2016.
[26] C. Zhao, X. Li, and H. Zhu, “Hyperspectral anomaly detection based on
stacked denoising autoencoders,” J. Appl. Remote Sens., vol. 11, no. 4,
p. 1, Sep. 2017.
[27] X. Wang, L. Wang, Q. Wang, A. Vizziello, and P. Gamba, “Hyperspectral
target detection via global spatial–spectral attention network and background suppression,” IEEE J. Sel. Topics Appl. Earth Observ. Remote
Sens., vol. 16, pp. 9011–9024, 2023.

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

[28] Y. Wang, H. Wang, E. Zhao, M. Song, and C. Zhao, “Tucker
decomposition-based network compression for anomaly detection with
large-scale hyperspectral images,” IEEE J. Sel. Topics Appl. Earth
Observ. Remote Sens., vol. 17, pp. 10674–10689, 2024.
[29] M. Zhao, W. Zheng, and J. Hu, “HTC-HAD: A hybrid transformer-CNN
approach for hyperspectral anomaly detection,” IEEE J. Sel. Topics Appl.
Earth Observ. Remote Sens., vol. 18, pp. 10144–10156, 2025.
[30] X. Fu, S. Jia, L. Zhuang, M. Xu, J. Zhou, and Q. Li,
“Hyperspectral anomaly detection via deep plug-and-play denoising
CNN regularization,” IEEE Trans. Geosci. Remote Sens., vol. 59, no. 11,
pp. 9553–9568, Nov. 2021.
[31] X. Dai, Y. Dong, Y. Zhang, and B. Du, “AdaptHAD: Adaptive onestep hybrid network for hyperspectral anomaly detection,” IEEE Trans.
Geosci. Remote Sens., vol. 63, 2025, Art. no. 5531614.
[32] Y. Li, T. Jiang, W. Xie, J. Lei, and Q. Du, “Sparse coding-inspired GAN
for hyperspectral anomaly detection in weakly supervised learning,”
IEEE Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no. 5512811.
[33] Z. Wang, X. Wang, K. Tan, B. Han, J. Ding, and Z. Liu, “Hyperspectral
anomaly detection based on variational background inference and generative adversarial network,” Pattern Recognit., vol. 143, pp. 1–16, Nov.
2023.
[34] X. Lu, W. Zhang, and J. Huang, “Exploiting embedding manifold of
autoencoders for hyperspectral anomaly detection,” IEEE Trans. Geosci.
Remote Sens., vol. 58, no. 3, pp. 1527–1537, Mar. 2020.
[35] G. Fan, Y. Ma, X. Mei, F. Fan, J. Huang, and J. Ma, “Hyperspectral
anomaly detection with robust graph autoencoders,” IEEE Trans. Geosci.
Remote Sens., vol. 60, 2022, Art. no. 5511314.
[36] S. Wang, X. Wang, L. Zhang, and Y. Zhong, “Auto-AD: Autonomous
hyperspectral anomaly detection network based on fully convolutional
autoencoder,” IEEE Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no.
5503314.
[37] P. Xiang, S. Ali, S. K. Jung, and H. Zhou, “Hyperspectral anomaly
detection with guided autoencoder,” IEEE Trans. Geosci. Remote Sens.,
vol. 60, 2022, Art. no. 5538818.
[38] Z. Yang et al., “A multi-scale mask convolution-based blind-spot
network for hyperspectral anomaly detection,” Remote Sens., vol. 16,
no. 16, p. 3036, Aug. 2024.
[39] R. Zhao, Z. Yang, X. Meng, and F. Shao, “A novel fully convolutional
auto-encoder based on dual clustering and latent feature adversarial
consistency for hyperspectral anomaly detection,” Remote Sens., vol. 16,
no. 4, p. 717, Feb. 2024.
[40] Z. Wu and B. Wang, “Transformer-based autoencoder framework
for nonlinear hyperspectral anomaly detection,” IEEE Trans. Geosci.
Remote Sens., vol. 62, 2024, Art. no. 5508015.
[41] X. Chen, Y. Cui, S. Gao, L. Wang, C. Zhao, and T. Luo, “S3S-LTGRMA:
Local-to-global based spatial-structural-spectral joint reconstruction with
residual multi-head autoencoder for hyperspectral anomaly detection,”
Infr. Phys. Technol., vol. 145, pp. 1–14, Mar. 2025.
[42] X. Fu, T. Zhang, J. Cheng, and S. Jia, “MMR-HAD: Multiscale mamba
reconstruction network for hyperspectral anomaly detection,” IEEE
Trans. Geosci. Remote Sens., vol. 63, 2025, Art. no. 5516914.
[43] W. Chen, X. Zhi, S. Jiang, Y. Huang, Q. Han, and W. Zhang, “DWSDiff:
Dual-window spectral diffusion for hyperspectral anomaly detection,”
IEEE Trans. Geosci. Remote Sens., vol. 63, 2025, Art. no. 5504617.
[44] Y. Wang, X. Chen, E. Zhao, and M. Song, “Self-supervised spectral-level
contrastive learning for hyperspectral target detection,” IEEE Trans.
Geosci. Remote Sens., vol. 61, 2023, Art. no. 5510515.
[45] X. Cao, J. Yu, R. Xu, J. Wei, and L. Jiao, “Mask-enhanced contrastive
learning for hyperspectral image classification,” IEEE Trans. Geosci.
Remote Sens., vol. 62, 2024, Art. no. 4415415.
[46] X. Sun, Y. Zhang, Y. Dong, and B. Du, “Contrastive self-supervised
learning-based background reconstruction for hyperspectral anomaly
detection,” IEEE Trans. Geosci. Remote Sens., vol. 63, 2025, Art. no.
5504312.
[47] Y. Wang, C. Deng, H. Wang, E. Zhao, and Q. Lan, “Deep spectral metric
learning with Siamese network for hyperspectral target detection,” Infr.
Phys. Technol., vol. 150, pp. 1–15, Nov. 2025.
[48] X. Ou, L. Liu, S. Tan, G. Zhang, W. Li, and B. Tu, “A hyperspectral
image change detection framework with self-supervised contrastive
learning pretrained model,” IEEE J. Sel. Topics Appl. Earth Observ.
Remote Sens., vol. 15, pp. 7724–7740, 2022.
[49] W. Peng, T. Varanka, A. Mostafa, H. Shi, and G. Zhao, “Hyperbolic deep
neural networks: A survey,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 44, no. 12, pp. 10023–10044, Dec. 2022.
[50] H. Sun, L. Wang, L. Zhang, and L. Gao, “Hyperbolic space-based
autoencoder for hyperspectral anomaly detection,” IEEE Trans. Geosci.
Remote Sens., vol. 62, 2024, Art. no. 5522115.

WANG et al.: HTDC: HYPERBOLIC TRANSFORMER WITH DUAL-MOMENTUM CONTRASTIVE LEARNING FOR HAD

[51] Y. Yang et al., “Spectral-enhanced sparse transformer network for
hyperspectral super-resolution reconstruction,” IEEE J. Sel. Topics Appl.
Earth Observ. Remote Sens., vol. 17, pp. 17278–17291, 2024.
[52] Y. Wang, X. Chen, E. Zhao, C. Zhao, M. Song, and C. Yu, “An
unsupervised momentum contrastive learning based transformer network
for hyperspectral target detection,” IEEE J. Sel. Topics Appl. Earth
Observ. Remote Sens., vol. 17, pp. 9053–9068, 2024.
[53] M. Luo, R. Zhao, S. Zhang, L. Chen, F. Shao, and X. Meng, “IMCMDet: An intramodal enhancement and cross-modal fusion network
for small object detection in UAV aerial visible-infrared imagery,” IEEE
Trans. Geosci. Remote Sens., vol. 63, 2025, Art. no. 5008316.
[54] Y. Yang, Y. Wang, X. Xu, and E. Zhao, “Butterfly residual network: A hybrid approach with spectral transformers and depth-wise
convolutions for hyperspectral image super-resolution,” IEEE Trans.
Neural Netw. Learn. Syst., early access, Nov. 20, 2025, doi: 10.1109/
TNNLS.2025.3631243.
[55] A. van den Oord, Y. Li, and O. Vinyals, “Representation learning with
contrastive predictive coding,” 2018, arXiv:1807.03748.
[56] J. Liu, Z. Hou, W. Li, R. Tao, D. Orlando, and H. Li, “Multipixel
anomaly detection with unknown patterns for hyperspectral imagery,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 10, pp. 5557–5567,
Oct. 2022.
[57] T. Guo, L. He, F. Luo, X. Gong, Y. Li, and L. Zhang, “Anomaly
detection of hyperspectral image with hierarchical antinoise mutualincoherence- induced low-rank representation,” IEEE Trans. Geosci.
Remote Sens., vol. 61, 2023, Art. no. 5510213.
[58] R. Wang and J. Hu, “Gaussian-inspired attention mechanism for hyperspectral anomaly detection,” IEEE Geosci. Remote Sens. Lett., vol. 22,
pp. 1–5, 2025.
[59] D. Wang, L. Ren, X. Sun, L. Gao, and J. Chanussot, “Nonlocal and
local feature-coupled self-supervised network for hyperspectral anomaly
detection,” IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens.,
vol. 18, pp. 6981–6993, 2025.
[60] C.-I. Chang, “An effective evaluation tool for hyperspectral target
detection: 3D receiver operating characteristic curve analysis,” IEEE
Trans. Geosci. Remote Sens., vol. 59, no. 6, pp. 5131–5153, Jun. 2021.
[61] C.-I. Chang, “Comprehensive analysis of receiver operating characteristic (ROC) curves for hyperspectral anomaly detection,” IEEE Trans.
Geosci. Remote Sens., vol. 60, 2022, Art. no. 5541124.
[62] C.-I. Chang, “Effective anomaly space for hyperspectral anomaly
detection,” IEEE Trans. Geosci. Remote Sens., vol. 60, 2022, Art. no.
5526624.
[63] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum contrast for
unsupervised visual representation learning,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020, pp. 9726–9735.
Yulei Wang (Member, IEEE) was born in Yantai,
Shandong, China, in 1986. She received the B.S. and
Ph.D. degrees in signal and information processing
from Harbin Engineering University, Harbin, China,
in 2009 and 2015, respectively.
She was a Joint Ph.D. Student with the Remote
Sensing Signal and Image Processing Laboratory,
University of Maryland, Baltimore County, Baltimore, MD, USA, from 2011 to 2013. From 2011 to
2013, she was a Research Assistant with the School
of Medicine, Shock, Trauma and Anesthesiology
Research Organized Research Center (STAR-ORC), University of Maryland.
She is currently an Associate Professor and a Doctoral Supervisor with the
Hyperspectral Imaging in Remote Sensing (CHIRS), Information Science and
Technology College, Dalian Maritime University, Dalian, China. Her research
interests include hyperspectral image processing, multisource remote sensing
fusion, and vital signs signal processing. For more information, please visit
the website https://github.com/YuleiWang1/

5507217

Chao Deng was born in Panzhou, Guizhou, China,
in 1998. He received the B.S. degree in electronic
information science and technology from the Information Science and Technology College, Dalian
Maritime University, Dalian, China, in 2023, where
he is currently pursuing the M.S. degree in information and communication engineering.
His research interests include hyperspectral
anomaly detection and deep learning.

Enyu Zhao (Member, IEEE) was born in Dalian,
Liaoning, China, in 1987. He received the Ph.D.
degree in cartography and geographic information
systems from the College of Resources and Environment, University of Chinese Academy of Sciences,
Beijing, China, in 2017.
He was a joint Ph.D. Student with the Engineering
Science, Computer Science, and Imaging Laboratory, University of Strasbourg, Strasbourg, France,
from 2014 to 2016. He is currently an Associate
Professor with the College of Information Science
and Technology, Dalian Maritime University, Dalian. His research interests
include quantitative remote sensing and hyperspectral image processing.

Chunyan Yu (Senior Member, IEEE) received the
B.S. and Ph.D. degrees in environmental engineering
from Dalian Maritime University, Dalian, China, in
2004 and 2012, respectively.
In 2004, she joined the College of Computer
Science and Technology, Dalian Maritime University. From 2013 to 2016, she was a Post-Doctoral
Fellow with the Information Science and Technology
College, Dalian Maritime University. From 2014 to
2015, she was a Visiting Scholar with the College of
Physicians and Surgeons, Columbia University, New
York, NY, USA. She is currently an Associate Professor with the Information
Science and Technology College, Dalian Maritime University. Her research
interests include image segmentation, hyperspectral image classification, and
pattern recognition.
PAPER_TEXT
