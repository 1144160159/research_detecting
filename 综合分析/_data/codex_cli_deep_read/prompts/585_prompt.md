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
# [585] A Joint Masked Spectral Group Framework for Hyperspectral Representation Learning
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
编号：585
题名：A Joint Masked Spectral Group Framework for Hyperspectral Representation Learning
年份：2026
DOI：10.1109/tgrs.2026.3674733
来源：IEEE Transactions on Geoscience and Remote Sensing
PDF：paper/10.1109_TGRS.2026.3674733.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：其他AI安全与跨域异常检测
相关性：弱相关，分数 2
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\585.txt
- 原始字符数：76213
- 本次发送字符数：76213
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

5509418

A Joint Masked Spectral Group Framework for
Hyperspectral Representation Learning
Minzhen Cao , Graduate Student Member, IEEE, Hao Deng , Senior Member, IEEE,
Bowen Du , Member, IEEE, and Shengjie Zhao , Senior Member, IEEE

Abstract—Given the scarcity of labeled data, hyperspectral image (HSI) analysis has increasingly relied on selfsupervised representation learning. Masked reconstruction and
contrastive learning are two dominant paradigms that emphasize
spectral–spatial fidelity and feature discrimination, respectively,
yet their objectives are not naturally aligned in HSI: reconstruction is vulnerable to redundancy-induced shortcut solutions,
while contrastive learning may under-emphasize subtle but classcritical spectral cues. Motivated by this gap, we propose a
joint masked spectral group (MSG) framework for hyperspectral
representation learning that couples the two objectives through
a shared spectral-group representation and objective-consistent
structured masking. At its core, MSG builds on spectral group
embedding and masking (SGEM), which organizes contiguous
bands into compact groups and performs group-wise masking to
suppress redundancy while preserving coherent spectral context
for stable view formation. This design encourages reconstruction
and discrimination to complement rather than interfere with
each other, yielding representations that are both discriminative
and transferable. Extensive experiments under linear evaluation and few-shot fine-tuning (FT) across multiple downstream
benchmarks demonstrate that MSG consistently outperforms
strong masked reconstruction and contrastive learning baselines,
achieving higher accuracy, more stable class-wise performance,
and stronger transferability.
Index Terms—Contrastive learning, hyperspectral image
(HSI), masked reconstruction, self-supervised learning (SSL),
spectral grouping, transformer.

I. I NTRODUCTION

H

YPERSPECTRAL images (HSIs) provide continuous
spectral responses with fine-grained material information, supporting diverse applications such as land-cover
classification, vegetation monitoring, environmental assessment, and urban or disaster surveillance [1], [2], [3]. To fully
exploit this rich spectral–spatial information, however, several
key challenges must be addressed. The high dimensionality
Received 5 February 2026; accepted 10 March 2026. Date of publication
17 March 2026; date of current version 3 April 2026. This work was supported
in part by the National Key Research and Development Program of China
under Grant 2023YFC3806000 and Grant 2023YFC3806002, in part by the
National Natural Science Foundation of China under Grant 62371342 and
Grant 62406227, in part by Shanghai Pujiang Program under Grant 25PJD128,
and in part by the Fundamental Research Funds for the Central Universities.
(Corresponding author: Hao Deng.)
The authors are with the School of Computer Science and Technology and
the Engineering Research Center of Key Software Technologies for Smart City
Perception and Planning, Ministry of Education, Tongji University, Shanghai
201804, China (e-mail: denghao1984@tongji.edu.cn).
Data is available on-line at https://github.com/Viento1027/MSG
Digital Object Identifier 10.1109/TGRS.2026.3674733

of hundreds of correlated bands, variations across sensors
and acquisition conditions, and the presence of noise and
mixed pixels complicate reliable data interpretation [4], [5].
Moreover, the scarcity of large-scale, high-quality labeled
data, together with the heterogeneity of acquisition conditions,
further limits the scalability and robustness of hyperspectral
analysis in practice [6], [7].
Over the past decades, HSI analysis has evolved through
several methodological stages. Early studies relied on handcrafted features and shallow classifiers, including spectral
indices [8], subspace-based methods [9], dictionary learning
[10], and kernel-based support vector machines [11]. With
the advent of deep learning, convolutional neural networks
(CNNs) and their 2-D/3-D extensions became dominant, effectively capturing spectral–spatial correlations and achieving
substantial gains in classification accuracy [12], [13]. More
recently, attention-based architectures and transformer variants
have further advanced HSI representation learning by enabling
the modeling of long-range dependencies across spectral and
spatial dimensions [14], [15]. Despite these advances, the
strong reliance on annotated data remains a critical bottleneck,
motivating the exploration of unsupervised and self-supervised
paradigms for more generalizable hyperspectral representation
learning.
Self-supervised learning (SSL) has emerged as a promising solution for HSI analysis, as it enables the extraction
of transferable representations from abundant unlabeled data
[16], [17]. In computer vision (CV), SSL has evolved into
several dominant paradigms, such as masked reconstruction
[18], contrastive learning [19], clustering-based representation
learning [20], and generative pretraining [21]. When transferred to HSI, these paradigms have achieved encouraging
progress but still struggle to fully capture the hierarchical spectral–spatial dependencies inherent in hyperspectral
data [22], [23]. This limitation largely stems from the
predominant reliance on a single pretext objective, which
restricts the ability to exploit complementary learning cues.
Specifically, masked reconstruction focuses on fine-grained
spectral–spatial reconstruction, whereas contrastive learning
emphasizes global feature consistency between augmented
views. While a few studies have explored multiobjective SSL
frameworks, they typically combine different objectives only at
the loss level, leaving the two objectives to compete on inconsistent inputs and learning signals, which often yields limited
synergy [24]. These limitations highlight the need for an SSL

1558-0644 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

5509418

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

framework that can explicitly coordinate reconstruction- and
contrastive-driven supervision in a shared spectral–spatial representation space, rather than merely summing losses.
To address these limitations, we propose the joint masked
spectral group (MSG) framework for self-supervised hyperspectral representation learning. Instead of treating masked
reconstruction and contrastive learning as two loosely coupled
branches, MSG introduces an objective-consistent coordination mechanism that aligns their supervision through a shared
spectral-group representation and structured masking. Concretely, MSG uses a shallow shared encoder to establish
a common spectral–spatial feature space, upon which two
lightweight task heads are optimized with different masking
ratios to provide complementary learning signals. At its core
lies the spectral group embedding and masking (SGEM)
module, which aggregates contiguous spectral bands into
coherent group-wise tokens and applies group-wise masking
aligned with the grouped representation. In this way, reconstruction emphasizes intragroup spectral–spatial fidelity while
contrastive learning promotes global invariance on consistent
grouped views, so that the two objectives complement rather
than interfere with each other.
The main contributions of this work are summarized as
follows.
1) We propose MSG, a joint self-supervised framework
for hyperspectral representation learning. It integrates
spectral-group masked reconstruction and group-wise
contrastive learning within a partially shared encoder
architecture to balance fidelity and discriminability.
2) We design the SGEM module, which employs a spectral
stem and group-wise patchification to partition contiguous spectral bands into groups, generating coherent
spectral–spatial tokens. This module allows the transformer to jointly capture spatial and spectral correlations
and provides a unified foundation for both reconstruction
and contrastive learning.
3) We comprehensively evaluate MSG across multiple
benchmark datasets through comparative and ablation
analyses. The results demonstrate its consistent superiority over strong baselines and verify the generalization
and robustness of the proposed framework.
The remainder of this article is organized as follows. Section II provides a review of related work. Section III describes
the proposed MSG methodology. Section IV presents the
datasets and experimental setup, and then reports the performance comparison and ablation studies. Section V concludes
the article and discusses potential future research directions.
II. R ELATED W ORK
A. Masked Reconstruction for HSIs
Masked reconstruction has become a prominent paradigm in
self-supervised representation learning, which aims to recover
missing input regions from partial observations [25]. In CV,
this principle has been instantiated in various architectures,
among which masked autoencoders (MAEs) are particularly
influential [26]. Key design principles include employing a
high masking ratio to increase task difficulty, adopting an

asymmetric encoder–decoder structure with most capacity
allocated to the encoder, and performing reconstruction either
in the pixel domain or in compact latent spaces [27], [28].
These advances demonstrate that such reconstruction objectives can effectively capture contextual dependencies without
reliance on manual annotations.
When extended to an HSI, masked reconstruction needs to
account for the intrinsic spectral–spatial structure. Prior works
have attempted to reconstruct full spectral signatures [22],
low-dimensional subspace projections [29], or hybrid targets
combining spectral and spatial cues [30]. Spatial masking
encourages the modeling of local context, whereas spectral
masking compels the encoder to capture interband correlations.
Several studies further integrate spatial and spectral masking
to model joint dependencies [31]. Decoders are generally
designed to be lightweight, thereby avoiding trivial copying
and forcing the encoder to assume the representational burden
[32]. Nevertheless, recent analyses indicate that reconstruction
with pixel-space or other low-level targets does not necessarily induce semantically meaningful high-level representations,
even under high masking ratios [33]. Consistent observations
further show that MAE-style pretraining often produces features with limited abstraction and entanglement of object and
background cues, thereby increasing reliance on labeled finetuning (FT) for achieving strong downstream performance
[34]. It also exhibits limited cross-sensor transferability, as
fidelity objectives alone do not ensure domain invariance
[35]. Consequently, reconstruction-based pretraining remains
constrained in semantic abstraction and cross-domain generalization in HSI.
B. Contrastive Learning for HSIs
In parallel, contrastive learning has emerged as a central paradigm for self-supervised representation learning. By
maximizing agreement between positive pairs and enforcing
separation from negatives, it produces compact, discriminative,
and transferable embeddings [36]. Technical innovations such
as momentum encoders, memory queues, and temperature
scaling have substantially improved its scalability and effectiveness in large-scale visual representation learning [19], [37].
In the hyperspectral domain, contrastive learning presents
both opportunities and unique challenges. Spatial augmentations (e.g., cropping, flipping, and translation) enrich spatial
diversity, whereas spectral perturbations (e.g., band dropout,
jittering, and smooth distortions) expand the view space while
preserving spectral structure [38]. The design of augmentations is particularly delicate: they must increase variability
while maintaining the physical continuity of spectral signatures. To improve scalability and stability, momentum-based
encoders and prototype-based clustering have been adapted
to hyperspectral settings [39], [40]. Despite these efforts,
several issues persist. Highly similar spectra across classes can
generate false negatives, undermining the contrastive objective.
Excessive spectral perturbations may destroy essential classdiscriminative cues, while insufficient perturbations fail to
provide meaningful contrast. Moreover, large-batch training
and reliance on memory banks introduce computational burdens for high-resolution hyperspectral datasets [41]. These

CAO et al.: JOINT MSG FRAMEWORK FOR HYPERSPECTRAL REPRESENTATION LEARNING

limitations highlight that contrastive learning for HSI remains
sensitive to augmentation design, spectral redundancy, and
computational scalability, calling for further exploration of
more adaptive and domain-aware strategies.
C. Spectral Information Handling in Hyperspectral
Representation Learning
A fundamental challenge in hyperspectral representation
learning lies in efficiently encoding spectral information while
capturing spectral correlation and preserving spatial structure.
Early methods treated each band as an independent channel,
which resulted in sequence lengths proportional to the number
of bands or required computationally demanding 3-D convolutional networks [42], [43]. While effective in modeling
fine-grained dependencies, these approaches are computationally expensive and prone to overfitting and noise.
Later studies introduced spatial-only patchification strategies inspired by vision transformers [44]. Although this
improves computational efficiency, it weakens spectral correlation and undermines the advantages of hyperspectral
data in complex spectral scenarios. To address this, more
targeted spectral modeling techniques—such as channel attention, band selection, clustering, and subspace methods—have
been explored to reduce redundancy and enhance robustness
[45], [46], [47]. However, these strategies inevitably involve
tradeoffs among fidelity, efficiency, and generalization.
In self-supervised pretraining, spectral handling becomes
even more critical, because redundancy across bands can
lead to shortcut solutions in masked reconstruction. Existing
masking strategies typically rely on random band masking
or contiguous block masking [48], [49]. Random masking
may disrupt spectral continuity and leave highly similar bands
unmasked, enabling the model to reconstruct masked bands by
referencing redundant spectra. To mitigate such redundancyinduced information leakage, mining redundant spectra (MRS)
introduces a redundancy-aware spectral masking policy that
jointly masks highly similar bands selected via band-wise similarity, thereby increasing reconstruction difficulty and serving
as a plug-and-play replacement for spectral-wise masking [50].
These redundancy-aware designs primarily refine the masking
policy in masked reconstruction by determining which raw
spectral components should be jointly hidden. Blockwise
spectral embedding has also been explored to improve spectral
continuity in masked pretraining [51], but it directly partitions
raw bands without explicitly enhancing interband representation and remains primarily reconstruction-oriented.
Overall, effective spectral representation in hyperspectral
pretraining requires not only preserving local continuity
but also capturing higher level spectral relationships and
cross-region coherence, while aligning spectral and spatial
dependencies. Achieving such a balance remains challenging
within existing designs, motivating the exploration of structured spectral modeling schemes that can organize correlated
bands into coherent representations and better align spectral
and spatial dependencies. Based on these insights, we propose
a dual-task pretraining framework that coordinates masked
reconstruction and contrastive learning via objective-consistent
spectral-group representations and structured masking, aiming

5509418

to obtain balanced spectral–spatial representations for hyperspectral pretraining.
III. M ETHODOLOGY
A. Overall Framework
To learn transferable representations from unlabeled HSIs,
we present the MSG framework, which couples masked
reconstruction and group-level contrastive learning through
objective-consistent spectral-group representations and structured masking.
Raw hyperspectral patches X̃ ∈ RH0 ×W0 ×C0 are first
processed by group-wise principal component analysis (GWPCA) followed by spatial sampling. This step reduces spectral
redundancy and yields preprocessed inputs X ∈ RH×W×C for
the subsequent SGEM module.
As illustrated in Fig. 1, the SGEM module partitions
contiguous spectral bands into groups and converts X into
structured group-wise tokens, preserving intragroup spectral
continuity while encoding local spatial structure. This design
aggregates contiguous bands to enrich token information
content, while avoiding the excessive sequence length of bandwise tokenization and maintaining computational efficiency.
The grouped tokens are then fed into a shallow shared
encoder to learn task-agnostic spectral–spatial representations.
These representations serve as a common space for two
complementary branches: one focusing on fine-grained reconstruction and the other on global contrastive discrimination.
The reconstruction branch adopts a relatively high mask ratio
τh and employs an asymmetric decoder to recover masked
group-patch values, enforcing fine-grained spectral–spatial
fidelity. In contrast, the contrastive branch applies a lower
mask ratio τl together with mild stochastic perturbations to
generate correlated group-level views for contrastive optimization, thereby enhancing feature discriminability and
robustness. During pretraining, these two objectives are jointly
optimized through a weighted loss.
After pretraining, both the decoder and the projector are
discarded. For downstream applications, encoder outputs are
aggregated at the group level, such as by mean pooling
or lightweight feature aggregation and forwarded to a taskspecific prediction head.
B. Spectral Group Embedding and Masking
While the preprocessing step reduces redundancy, directly
treating each spectral band as an independent token still
leads to excessive sequence length, whereas purely spatial
patchification neglects spectral correlations. To address these
limitations, we design an SGEM module that first performs
channel expansion and group-wise patchification to form
coherent spectral–spatial tokens, and then applies structured
masking aligned with the grouped representation. This process
is illustrated in the lower part of Fig. 1, which depicts the
transformation from the input hyperspectral sample to grouped
tokens and their masked variants.
1) Spectral Stem: Let X ∈ RH×W×C denote a local
hyperspectral sample. Before spectral grouping, a lightweight
spectral stem φ s composed of a 1 × 1 convolution, batch

5509418

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

Fig. 1. Overall architecture of the proposed MSG framework. The model performs coordinated dual-objective pretraining, comprising a reconstruction objective
with a high masking ratio and a contrastive objective with a low masking ratio. The SGEM module converts hyperspectral samples into spectral-grouped
patch tokens, which are fed into the shared encoder and branch-specific heads. The bottom illustrates the detailed workflow of the SGEM module.

normalization, and GELU activation is applied along the
spectral dimension
0

X0 = φ s (X) ∈ RH×W×C ,

C 0 ≥ C.

(1)

This operation performs pointwise channel mixing to linearly
project each spectral vector into a more expressive subspace,
while normalization and nonlinear activation further stabilize
training and capture subtle interband dependencies. Serving
as a spectral preprocessing stage, the stem enhances spectral
decorrelation and feature discriminability before grouping,
without introducing additional spatial computation. Its effect is
more evident in improving feature adaptation and optimization
stability, as it facilitates the alignment of spectral representations across varying domains and training dynamics.
2) Group-Wise Patchification: The spectral dimension of
X0 is partitioned into G groups, each containing Cg = C 0 /G
contiguous bands by zero-padding if needed. The spatial
domain is divided into nonoverlapping patches of size p × p,
yielding T = (H/p)(W/p) patches per group. Stacking across
groups gives N = G · T tokens in total.
For each group g, the corresponding patch matrix is
Pg X = vec
0





X0g,1



, . . ., vec

X0g,T

 >

T ×p2 Cg

∈R

(2)

and concatenating all groups yields
2
3
P1 (X0 )
 6
2
7
P X0 = 4 ... 5 ∈ RN×p Cg .
PG (X0 )

(3)

This operation preserves both spatial ordering and spectral
grouping, ensuring that tokens encode contiguous spectral
information while remaining computationally tractable.
3) Group-Specific Token Projection and Positional Embeddings: Instead of using a single shared projection, groupspecific projections are adopted (equivalent to a grouped p× p
convolution with stride p). For each group g

>
>
Eg = Pg X0 W(g)
+ 1 b(g)
∈ RT ×D
(4)
e
e
D×p Cg
D
with independent parameters W(g)
and b(g)
e ∈ R
e ∈ R .
>
> >
N×D
, forming a blockStacking yields E = [E1 , . . ., EG ] ∈ R
diagonal mapping that preserves intergroup separation while
reducing parameter coupling. To encode spatial layout and
spectral-group identity, we add
2

spatial

Zi,: = Ei,: + Pt,:

+ Pgroup
g,:

(5)

where i 7→ (g, t), Pspatial ∈ RT ×D encodes the 2-D spatial
coordinates of patch t using sinusoidal functions, and Pgroup ∈

CAO et al.: JOINT MSG FRAMEWORK FOR HYPERSPECTRAL REPRESENTATION LEARNING

RG×D encodes the 1-D spectral group index g in the same
manner.
The resulting sequence Z ∈ RN×D integrates both spatial
and spectral priors and is passed to the shared encoder for
further processing.
4) Group-Wise Masking: Masking is sampled independently across spectral groups, so that at a fixed spatial location,
some groups may be masked while others remain visible. This
cross-group asynchrony at identical spatial patches encourages
the encoder to infer missing spectra from neighboring bands
while retaining spatial context. Let T denote the number of
spatial patches per group. For group g, we first generate a
random vector

ug = ug,1 , . . ., ug,T , ug,t ∼ U (0, 1) i.i.d
(6)
where each entry is independently drawn from the uniform
distribution on (0, 1). Sorting ug in ascending order yields a
permutation of patch indices

πg = argsort ug ∈ S T
(7)
where S T denotes the set of all permutations of {1, . . ., T }.
Given a mask ratio τ ∈ (0, 1), the number of visible tokens
per group is
T keep = b(1 − τ) T c .
(8)
We retain the first T keep indices of πg as the visible set
˚

Vg = πg (1) , . . ., πg T keep .

(9)

G×T

The final binary mask matrix M ∈ {0, 1}
is then defined
by the convention
(
0, t ∈ Vg (visible)
Mg,t =
(10)
1, t < Vg (masked)
so that visible tokens (M = 0) are passed to the encoder, while
masked tokens (M = 1) are replaced by mask tokens during
reconstruction. In practice, a higher mask ratio τh is used for
the reconstruction branch, while a lower ratio τl is applied for
contrastive view generation, both relying on this same groupwise masking scheme.
C. Shared Encoder and Dual-Task Architecture
The proposed framework adopts a partially shared encoder
and a dual-task architecture. This design ensures complementary representation learning, where one branch focuses on
capturing fine-grained spectral–spatial patterns while the other
enforces global discriminability among samples.
1) Shared Encoder: Given the input embedding sequence
Zvisible obtained under the task-specific mask M, the shared
encoder E s extracts a common spectral–spatial representation
F s , which serves as the shared feature space for both downstream objectives. The reconstruction adapter Erec and the
contrastive adapter Econ further process F s to produce taskspecific representations
F s = E s (Zvisible ) , Frec = Erec (F s ) , Fcon = Econ (F s ) .

5509418

2) Reconstruction Task: For the reconstruction task, a
group-wise mask M rec ∈ {0, 1}G×T is applied. The decoder
receives the encoded visible features Frec together with
learnable mask tokens and predicts the original patchified
2
group-patch targets. Let P(X0 ) ∈ RN×p Cg be the ground-truth
patch targets and P̂ the predicted ones. The reconstruction loss
is computed only on masked positions
X
 2
1
rec
Mg,t
P̂g,t − Pg,t X0 2 .
(12)
Lrec = P
rec
M
g,t g,t
g,t
The decoder is asymmetric and intentionally lightweight:
it projects encoded visible features to a lower dimensional
decoder embedding of dimension Ddec < D and applies
Ldec transformer blocks with reduced width and fewer attention heads than the encoder. This design reduces compute,
mitigates shortcut solutions that may arise with an overly
expressive decoder, and encourages the shared encoder to
encode informative visible-context features.
3) Contrastive Task: For the contrastive task, two correlated
views are generated by sampling two independent masks
M (1) and M (2) with ratio τl , without applying additional
augmentations. The shared encoder and contrastive branch
(2)
produce features F(1)
con and Fcon for the two views. Group-level
(k)
descriptors v for each view are obtained by mean-pooling
spatial tokens within each group and concatenating them
1
0
X (k)
1
(13)
fc,g,t A
v(k) = concatGg=1 @ (k)
|S g | (k)
t∈S g

where S g(k) denotes the set of visible spatial indices for group
g in view k. After projection via a multilayer perceptron
(projector) and `2 normalization, the descriptors are compared
across views.
With a batch of B samples, let the normalized projections
form Z ∈ R2B×d and define the similarity matrix S =
ZZ> /τtmp , where τtmp denotes the temperature. The positive
index p(i) pairs two views of the same sample. The contrastive
loss (NT-Xent) is defined as

2B
exp Si,p(i)
1 X
Lcon = −
log P2B
(14)
.
2B
j=1 exp Si, j
i=1

j,i

The overall pretraining objective combines the two tasks via
a convex combination
Ltotal = λ Lrec + (1 − λ) Lcon

(15)

where λ ∈ [0, 1] controls the tradeoff between reconstruction and contrastive objectives, and keeps the overall loss
magnitude on a comparable scale when adjusting the balance
coefficient. All parameters of the encoder, branches, decoder,
and projector are optimized end-to-end.
D. Rationale and Downstream Adaptation

(11)

Both branches operate on the same F s , ensuring that reconstruction and contrastive objectives are optimized in a common
representation space.

The dual-task design of MSG is intended to learn representations that are both locally precise and globally
discriminative. The reconstruction objective enforces finegrained spectral–spatial fidelity, while the contrastive objective

5509418

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

Fig. 2. Visualization of benchmark hyperspectral datasets used for downstream evaluation: (a) Berlin, (b) Salinas, (c) WHU-Hi-LongKou, and (d) Houston2013.
For (a)–(c), the left shows an RGB composite generated from selected spectral bands, while the right displays the corresponding ground-truth map. For
Houston2013 in (d), the RGB composite is shown on the top and the corresponding ground-truth map is shown below. All images are normalized for clarity
of visualization, and the spatial coverage and aspect ratio differ across datasets.

promotes invariance to perturbations and improves the linear
separability of features in the latent space by contrasting
different views. The joint optimization of these complementary
objectives enables the shared encoder to learn a compact,
robust, and transferable representation space.
After pretraining, the decoder and the projector are removed,
and the pretrained backbone consisting of SGEM and the
shared encoder can be flexibly adapted to a variety of downstream settings. Since the learned features are group-aware
and capture both spectral continuity and spatial structure,
they provide a stable basis that can be used with different
adaptation strategies depending on label availability, computational budgets, and the complexity of the target task.
Lightweight adaptation can exploit these pretrained features
with minimal parameter updates, while more comprehensive
tuning allows the model to specialize to specific application
domains.
Moreover, the structured design of MSG facilitates the
attachment of diverse task heads and aggregation schemes.
For example, group-level descriptors can be concatenated
or pooled for image-level classification, whereas token-level
outputs can be preserved before group pooling to support
dense prediction tasks such as segmentation or anomaly
detection. This flexibility makes MSG suitable not only
as a self-supervised pretraining framework but also as a

general-purpose backbone for a broad range of hyperspectral
applications.
IV. E XPERIMENTS AND R ESULTS
A. Dataset Description
To comprehensively evaluate the proposed MSG
framework, HySpecNet-11k is used for large-scale selfsupervised pretraining, whereas four publicly available
labeled benchmarks—Berlin, Salinas, WHU-Hi-LongKou,
and Houston2013—are used for downstream evaluation.
These datasets span different sensors, spatial resolutions, and
application domains, thereby enabling a fair and generalizable
evaluation of the learned representations. Representative
visualizations of the four labeled datasets are provided in
Fig. 2, and detailed category statistics are summarized in
Table I.
1) HySpecNet-11k: The HySpecNet-11k dataset is a largescale benchmark acquired by the Environmental Mapping and
Analysis Program (EnMAP) satellite during routine operations
in November 2022 [52]. It contains 11 483 nonoverlapping
image patches of size 128×128 pixels, each with 224 spectral
bands covering 420–2450 nm at a ground sampling distance of
30 m. After atmospheric correction, bands severely affected by
water vapor absorption were removed, leaving 202 valid bands.

CAO et al.: JOINT MSG FRAMEWORK FOR HYPERSPECTRAL REPRESENTATION LEARNING

5509418

TABLE I
C ATEGORY S TATISTICS OF THE B ENCHMARK H YPERSPECTRAL DATASETS

The dataset spans diverse geographic regions and land-cover
types, providing a large-scale corpus tailored for unsupervised
and self-supervised representation learning.
2) Berlin: The Berlin dataset originates from the DLR
EnMAP preparatory flight campaign conducted in 2009 [53].
Several flight lines were acquired using the HyMap airborne
sensor over the Berlin-urban-gradient region. In this work,
we use the subset with dimensions 1723 × 476 × 244,
which includes 244 spectral bands covering approximately
450–2500 nm with a nominal spatial resolution of 4 m. The
dataset captures a distinctive urban-to-rural gradient, including
built-up areas, vegetation, bare soil, and water bodies, making
it a valuable benchmark for hyperspectral classification in
heterogeneous urban landscapes.
3) Salinas: The Salinas dataset was collected by the
AVIRIS sensor over the agricultural area of Salinas Valley,
California. It consists of 512 × 217 pixels with 224 spectral bands covering 400–2500 nm at a spatial resolution of
3.7 m. After removing 20 water absorption bands, 204 bands
remain. The dataset contains 16 land-cover classes, primarily
corresponding to different crop types such as broccoli, lettuce,
and vineyards. Owing to its high intraclass variability and
large number of categories, Salinas serves as a challenging
benchmark widely adopted in HSI classification studies.
4) WHU-Hi-LongKou: The WHU-Hi-LongKou dataset is
part of the WHU-Hi UAV-borne benchmark suite, which was
designed for precise crop classification [54]. It was acquired
on July 17, 2018, in Longkou Town, Hubei Province, China,
using a Headwall Nano-Hyperspec sensor mounted on a DJI
M600 Pro UAV platform. The data cube has dimensions
of 550 × 400 × 270, with spectral coverage from 400 to
1000 nm and a ground sampling distance of approximately
0.46 m. The scene contains six major crop species, including
corn, cotton, sesame, broad-leaf soybean, narrow-leaf soybean,
and rice. With its fine spectral granularity and ultrahigh spatial resolution, WHU-Hi-LongKou provides a representative

benchmark for evaluating hyperspectral classification methods
in smallholder agricultural environments.
5) Houston2013: The Houston2013 dataset was released
as part of the IEEE GRSS Data Fusion Contest 2013 and has
become a widely used benchmark for urban HSI classification
[55]. It was acquired by the ITRES CASI-1500 airborne hyperspectral sensor over the University of Houston campus and its
surrounding urban areas. The data cube has a spatial size of
349 × 1905 pixels with a spatial resolution of 2.5 m, covering
the spectral range from 380 to 1050 nm with 144 spectral
bands. The scene represents a complex urban environment
with high spectral variability and strong spatial heterogeneity,
including materials such as roads, buildings, parking lots,
grass, trees, water, and residential areas. A total of 15 landcover classes are annotated, making the dataset particularly
suitable for evaluating the robustness and generalization ability of hyperspectral classification and representation learning
methods under challenging urban scenarios.

B. Experimental Setup
1) Evaluation Metrics: We adopt three widely used metrics
for HSI classification: overall accuracy (OA), average accuracy
(AA), and Cohen’s kappa coefficient (κ). These measures
provide complementary perspectives on model performance
across different classes.
Given a confusion matrix M ∈ Nnc ×nc with nc classes and
a total of N samples, OA is defined as
OA =

Pnc

i=1 Mii

N

.

(16)

The per-class accuracy for class i is defined as
Mii
ai = Pnc
j=1 Mi j

(17)

5509418

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

TABLE II
L INEAR E VALUATION R ESULTS ON B ERLIN DATASET

TABLE III
L INEAR E VALUATION R ESULTS ON S ALINAS DATASET

and AA is obtained as the macro-average across all classes
nc

AA =

1 X
ai .
nc

(18)

i=1

The κ coefficient is used to measure the level of agreement
beyond chance, where the expected agreement is given by
Pnc
nc Pnc
X
j=1 Mi j
j=1 M ji
pe =
·
.
(19)
N
N
i=1

It is then defined as
κ=

OA − pe
.
1 − pe

(20)

All reported results are presented as the mean ± standard
deviation over multiple random seeds to ensure statistical
reliability.

2) Baseline Methods: We compare MSG with several representative self-supervised approaches under a unified linear
evaluation protocol and few-shot FT. To better contextualize
the results, we categorize the baselines into two groups:
1) CV transfer methods, which were originally developed
for natural-image representation learning and are directly
transferred to hyperspectral data with minimal architectural or
objective changes; and 2) HSI self-supervised methods, which
are specifically designed for hyperspectral or multisource
remote sensing data and explicitly encode spectral–spatial
inductive biases through tailored masking strategies, factorized
spectral–spatial modeling, or dual-branch designs. houston
These two groups correspond to the column headers in
Tables II–IX.
a) MAE [26]: The original MAE adapted to hyperspectral data with adjusted hyperparameters. It partitions the
input into spatial patches, applies a high masking ratio, and

CAO et al.: JOINT MSG FRAMEWORK FOR HYPERSPECTRAL REPRESENTATION LEARNING

5509418

TABLE IV
L INEAR E VALUATION R ESULTS ON WHU-H I -L ONG KOU DATASET

TABLE V
L INEAR E VALUATION R ESULTS ON H OUSTON 2013 DATASET

TABLE VI
FT R ESULTS ON B ERLIN DATASET

reconstructs the missing pixels using a lightweight decoder,
without explicitly modeling spectral dependencies. This
baseline represents a reconstruction-only paradigm directly
transferred from CV.

b) SimCLR [19]: A contrastive learning framework originally proposed for natural images. In our implementation,
we adopt a ViT backbone consistent with other baselines
and MSG, and generate augmented views using spectral- and

5509418

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

TABLE VII
FT R ESULTS ON S ALINAS DATASET

TABLE VIII
FT R ESULTS ON WHU-H I -L ONG KOU DATASET

spatial-preserving transformations. This baseline represents a
contrastive-only paradigm for hyperspectral data.
c) SS-MAE [56]: A spatial–spectral MAE designed
for multisource remote sensing classification. It adopts a
dual-branch pretraining strategy, where one branch masks
spatial patches and the other masks entire spectral bands,
enabling joint modeling of spatial and spectral contexts. The
original design includes lightweight convolutional modules
for spatial enhancement during FT, which are omitted in
our experiments to ensure a fair linear evaluation across
baselines.
d) HSIMAE [57]: An MAE tailored for hyperspectral
data with a staged spatial–spectral masking strategy. Given a
3-D cube, spatial masking first removes all tokens at the same
spatial location across spectral bands, and spectral masking
subsequently removes tokens at the same spectral location

across the image. This two-stage design preserves spatial and
spectral consistency during masking and guides reconstruction to capture coupled spectral–spatial dependencies using a
lightweight MAE-style decoder.
e) TMAC [24]: A transformer-based MAE augmented
with a momentum contrastive branch for hyperspectral representation learning. The model jointly optimizes masked
reconstruction and contrastive objectives, where queries are
produced by a momentum encoder on visible tokens, and keys
are obtained by passing the corresponding features through a
lightweight decoder and a projection head. This design offers
a straightforward coupling between reconstruction and contrastive learning, yet the interaction between the two objectives
remains relatively shallow.
f) FactoFormer [58]: A factorized transformer pretraining framework for hyperspectral representation learning that

CAO et al.: JOINT MSG FRAMEWORK FOR HYPERSPECTRAL REPRESENTATION LEARNING

5509418

TABLE IX
FT R ESULTS ON H OUSTON 2013 DATASET

explicitly decouples spatial and spectral tokenization. It performs two-stage pretraining: a spatial branch partitions the
input cube into spatial patches and reconstructs masked patch
content, while a spectral branch treats each band as a token and
reconstructs masked band-wise responses. The two pretrained
encoders are then jointly transferred to downstream tasks
by concatenating their CLS representations and training a
lightweight classification head.
3) Implementation Details: All methods follow a consistent
preprocessing strategy to ensure fairness. GW-PCA is first
applied to reduce spectral redundancy and project each hyperspectral patch into 128 channels. Afterward, the processed data
is divided into 7×7 spatial patches, each of which is tokenized
with a patch size set to 1. Based on this representation, the
SGEM module partitions the 128 channels into eight groups
to generate group-wise tokens. The encoder consists of six
layers with an embedding dimension of 128 and eight attention
heads, while the decoder is lightweight with four layers and a
hidden dimension of 64. Unless otherwise stated, the masking
ratio is set to 0.7 in the reconstruction branch and 0.3 in
the contrastive branch. Contrastive representations are mainly
obtained by applying low-ratio masking, supplemented with
mild Gaussian noise to introduce variability while preserving
spectral continuity. The contrastive loss uses a balancing
weight of 1.0.
Pretraining runs for 200 epochs using the AdamW optimizer
with an initial learning rate of 1 × 10−4 and weight decay of
1 × 10−2 . A cosine learning-rate schedule with five warmup
epochs is adopted. The batch size is fixed at 128, and up
to 100 000 hyperspectral patches are sampled for each run.
Mixed-precision training with gradient scaling is used to
improve efficiency. An early stopping criterion with a patience
of 20 epochs is applied, and the model with the lowest
validation loss is retained.

For downstream experiments, two evaluation protocols are
considered: linear evaluation and FT. For both protocols, the
crop size is fixed at 7 × 7, and a stride of 7 is used by
default to avoid overlap between adjacent samples. The only
exception is the Houston dataset in the FT setting, where
the stride is reduced to 2 because a stride of 7 would yield
insufficient training samples under the 5% label ratio. In
linear evaluation, all pretrained weights are frozen, and only a
single linear classifier is trained on the concatenated features
from the reconstruction and contrastive branches using the
Adam optimizer with a learning rate of 1 × 10−3 . In FT,
all backbone parameters are unfrozen and jointly optimized
with the classifier under the same learning rate, while the
weight decay is set to 0 to encourage rapid adaptation in
the low-resource regime. Notably, all downstream experiments
are conducted on datasets that are strictly disjoint from the
pretraining data, ensuring a rigorous and unbiased assessment
of cross-dataset transferability.
All experiments are implemented in PyTorch and executed
on a system equipped with an NVIDIA GeForce RTX 5070Ti
graphics card with 16-GB memory and 32-GB RAM. All
reported results are averaged over five different random seeds
and presented as mean ± standard deviation to ensure statistical reliability.
C. Performance Comparison
1) Linear Evaluation: We assess representation quality
under a standard linear evaluation protocol. All backbone
parameters are frozen, and only a linear classifier is trained
on top of the pretrained features. For architectures with two
branches, their frozen outputs are concatenated before the classifier; single-branch methods use the encoder output directly.
We adopt a 70/15/15 split for train/validation/test and enforce
nonoverlapping patch sampling to avoid information leakage

5509418

for Berlin, Salinas, and WHU-Hi-LongKou. For Houston2013,
due to its limited and spatially sparse labeled samples, a small
amount of overlap may occur during dispersed patch sampling.
This setting isolates the intrinsic discriminative power of
the learned features by removing the confounding effects of
downstream FT.
As summarized in Tables II–V, MSG achieves the best
overall performance in terms of OA, AA, and κ across all
four benchmarks, outperforming both CV transfer and HSI
self-supervised methods. On Berlin, MSG reaches OA =
86.56%, AA = 79.92%, and κ = 78.80%. It performs
particularly well on structurally complex categories such as
industrial area (Class 3), commercial area (Class 7), and water
(Class 8), where accurate classification is challenging due
to strong spectral–spatial mixing. On Salinas, MSG obtains
OA = 93.41%, AA = 96.51%, and κ = 92.67%, achieving
nearly perfect accuracy on lettuce romaine categories (Classes
11–14) and stable performance on corn senesced green weeds
(Class 10), which involves subtle spectral differences. On
WHU-Hi-LongKou, the task is near-saturated, yet MSG still
secures the best aggregate results with OA = 99.27%, AA =
99.22%, and κ = 99.05%, reaching 100% accuracy on corn
(Class 1) and maintaining strong stability on roads and houses
(Class 8) and mixed weed (Class 9). On Houston2013, MSG
achieves OA = 86.30%, AA = 88.10%, and κ = 85.18%,
showing consistent gains on urban categories with high intraclass variability and confusing materials, indicating more
robust discriminative representations.
These results show that the proposed model learns highly
discriminative and separable features. MSG exhibits not only
strong performance on dominant categories but also robustness
on structurally or spectrally challenging classes, reflecting its
ability to capture both global and local structure effectively
during pretraining.
2) Fine-Tuning: To further examine the transferability and
robustness of the learned features, we conduct end-to-end
FT. A 5/5/90 split is adopted to emphasize small-sample
adaptation, with the same sampling strategy. Unlike linear
evaluation, the backbone parameters are unfrozen to allow full
network optimization. This setting evaluates whether MSG
provides a favorable initialization that accelerates and stabilizes downstream adaptation.
As shown in Tables VI–IX, MSG consistently achieves the
best OA, AA, and κ on all datasets, further confirming its
effectiveness. On the Berlin dataset, it achieves OA = 83.68%,
AA = 69.29%, and κ = 73.48%, with stable accuracy on
industrial area (Class 3) and water (Class 8), which are prone
to error under small-sample conditions. On Salinas dataset,
MSG obtains OA = 86.95%, AA = 91.42%, and κ = 85.47%,
showing clear advantages on fallow (Class 3) and lettuce
romaine 4wk (Class 11), which typically exhibit performance
degradation in low-data settings. On the WHU-Hi-LongKou
dataset, MSG achieves OA = 97.78%, AA = 93.80%, and
κ = 97.09%, maintaining strong accuracy on both major
classes like corn (Class 1) and water (Class 7), and more
difficult categories such as mixed weed (Class 9). On the
Houston2013 dataset, MSG achieves OA = 87.35%, AA =
88.27%, and κ = 86.33%, with clear gains on several confusing

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

categories such as water (Class 6, 85.29%), highway (Class 10,
88.56%), and parking lot 1 (Class 12, 77.65%). It also reaches
100.00% on soil (Class 5), tennis court (Class 14), and running
track (Class 15), indicating stable small-sample adaptation in
complex urban scenes.
This experiment highlights the adaptability of MSG under
small-sample supervision. More importantly, since the pretraining and FT datasets are disjoint, the results also
demonstrate the strong cross-dataset transferability of MSG,
showing that the learned representations generalize well to new
sensors, regions, and land-cover distributions.
D. Ablation Study and Analysis
1) Component Ablation: To better understand the contribution of each component to the overall performance of
MSG, we conduct a series of ablation experiments under the
linear evaluation protocol. These experiments are designed to
disentangle the effects of masking strategy, learning objective,
and architectural design, thereby offering a more granular
view of how different elements interact to shape representation
quality.
Seven experimental groups are configured by incrementally
enabling or disabling specific components. Groups 1 and 2
follow the original MAE paradigm with spatial and band-wise
masking, respectively, to examine the effectiveness of different
masking strategies. Groups 3 and 4 adopt spectral-group
masking while retaining only the reconstruction or contrastive
branch, respectively, to isolate and analyze the contribution of
each learning objective. Groups 5 and 6 keep both branches but
modify the architecture. Group 5 removes the spectral stem to
assess its role as an initial projection module, whereas Group
6 employs separate encoders (sep. enc.), meaning that the
two branches are optimized independently without interaction.
Finally, Group 7 corresponds to the full MSG model, which
integrates spectral-group masking, dual learning objectives, the
spectral stem, and a shared encoder. For clarity, we report OA
in percentage for all datasets.
The results summarized in Table X clearly demonstrate the
contribution of each component. Groups 1 and 2, which rely
on conventional spatial or band-wise masking, yield the lowest
OA, highlighting the limitations of these simple strategies for
capturing spectral–spatial dependencies. By contrast, Groups
3 and 4 achieve substantial OA improvements, confirming
that spectral-group masking provides stronger structural priors
even when used with a single learning objective. Moreover, the
OA gap between these single-objective variants and Group
7 indicates that reconstruction and contrastive learning are
complementary rather than interchangeable under the proposed
spectral-group representation.
When architectural modifications are introduced, both
Group 5 (without the spectral stem) and Group 6 (with separate
encoders) exhibit moderate but consistent OA degradation
compared with the full model. This suggests that both the
initial projection and the shared backbone are important for
coordinating the dual objectives and stabilizing representation
learning. Altogether, Group 7 achieves the best or near-best
OA across all datasets, validating the joint contribution of

CAO et al.: JOINT MSG FRAMEWORK FOR HYPERSPECTRAL REPRESENTATION LEARNING

5509418

TABLE X
C OMPONENT A BLATION R ESULTS U NDER THE L INEAR E VALUATION P ROTOCOL

Fig. 3. Visualization of group-wise cosine similarity matrices on four downstream datasets. Each matrix is computed from a randomly sampled patch
using the pretrained SGEM. Brighter diagonal entries and low off-diagonal responses indicate strong intragroup coherence and weak intergroup correlation.
(a) Berlin. (b) Salinas. (c) WHU-Hi-LongKou. (d) Houston2013.

Fig. 4. Sensitivity to mask ratios for (a) reconstruction branch and (b) contrastive branch. Results are obtained under single-branch settings following Groups
3 and 4 of the component ablation in Table X.

spectral-group masking, coordinated dual-objective pretraining, and the shared encoder design.
2) Group Similarity Visualization: To better understand
how the proposed spectral-group embedding facilitates redundancy reduction and promotes decorrelated spectral representations, we provide a qualitative visualization of group-wise
similarities produced by SGEM. Specifically, for a randomly
sampled patch, we compute a group prototype by averaging
all spatial tokens within each spectral group, and then calculate the pairwise cosine similarity between group prototypes,
resulting in a G × G similarity matrix.
Fig. 3 presents representative similarity matrices on four
downstream datasets. Across all datasets, the matrices exhibit

clear diagonal dominance, indicating strong intragroup coherence, while most off-diagonal entries remain close to zero,
suggesting weak intergroup correlation. This pattern implies
that different spectral groups capture complementary and
largely nonredundant information, validating the ability of
SGEM to organize spectral bands into coherent yet distinct
groups.
Moreover, the highly consistent visualization patterns across
datasets demonstrate that the learned grouping behavior is
stable and dataset-agnostic, reflecting an intrinsic property
of the proposed representation rather than a dataset-specific
artifact. These qualitative observations provide intuitive evidence that group-wise embedding and masking encourage

5509418

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

TABLE XI

TABLE XIII

E FFICIENCY AND C OMPLEXITY C OMPARISON

S ENSITIVITY TO E NCODER D EPTH Lenc U NDER L INEAR E VALUATION

TABLE XII
S ENSITIVITY TO S PECTRAL G ROUP S IZE g U NDER L INEAR E VALUATION

TABLE XIV
S ENSITIVITY TO E MBEDDING D IMENSION d U NDER L INEAR E VALUATION

decorrelated spectral representations, which complements the
quantitative ablation results in Section IV-D1 and helps explain
the performance gains of MSG.
3) Efficiency and Complexity Analysis: To complement
accuracy-oriented comparisons, we analyze the computational
complexity and practical inference efficiency of MSG and representative baselines. We report parameters, FLOPs, peak GPU
memory, and throughput under a unified patch-level setting.
All methods take hyperspectral patches of shape [B, 128, 7, 7].
Params and FLOPs are computed for a single forward pass
with B = 1 (per-sample complexity). Peak GPU memory
is measured by torch.cuda.max_memory_allocated
(MB), and throughput is measured as samples per second
(sps); both are obtained with B = 64 under forward-only
inference on the same GPU.
Table XI summarizes the results. MSG incurs the highest
computation and memory cost among the compared methods,
leading to a lower forward throughput under the same batch
size. This overhead is expected because MSG introduces
spectral-group modeling and couples two complementary
supervision signals (masked reconstruction and contrastive
discrimination), which increases intermediate activations and
computation relative to single-objective designs.
Despite being more demanding, MSG remains practical
in patch-based hyperspectral pipelines: the peak allocated
memory stays below a few hundred MB for 7 × 7 patches,
and the measured throughput supports both pretraining and
downstream FT. Combined with the consistent performance

TABLE XV
S ENSITIVITY TO THE BALANCING W EIGHT λ U NDER L INEAR E VALUATION

gains reported in Section IV, these results indicate an
accuracy–efficiency tradeoff: MSG is preferable when stronger
transferability/robustness is required, whereas lighter baselines
may be chosen when computational resources are the primary
constraint.
4) Summary of Hyperparameter Sensitivity: We further
perform extensive sensitivity studies on key hyperparameters,

CAO et al.: JOINT MSG FRAMEWORK FOR HYPERSPECTRAL REPRESENTATION LEARNING

TABLE XVI
S ENSITIVITY TO P RETRAINING S CALE N U NDER L INEAR E VALUATION

5509418

combining masked reconstruction and contrastive learning,
MSG formulates an objective-consistent joint pretraining
mechanism that couples the two objectives through a shared
spectral-group representation and coordinated group-wise
masking. By organizing contiguous bands into coherent groups
and enforcing consistent grouped views under complementary
masking ratios, MSG suppresses redundancy-induced shortcut
solutions while preserving informative spectral context, so
that reconstruction-driven fidelity learning and contrastivedriven discrimination can complement rather than interfere
with each other. Experiments under linear evaluation and fewshot FT on four downstream benchmarks that span diverse
scenes and sensors demonstrate that MSG consistently outperforms strong hyperspectral self-supervised baselines and
vision-transfer counterparts. Comprehensive ablation studies
and supplementary analyses further verify the contribution
of each key component and provide practical guidance on
hyperparameter robustness and efficiency tradeoffs.
Despite these improvements, several limitations remain.
First, our current evaluation mainly focuses on hyperspectral
classification, which may not fully reflect the generality of
the learned representations. Second, while spectral grouping
improves robustness and coordination, it introduces additional
computational overhead, and a more efficient implementation
is desirable for large-scale or high-resolution settings. Future
work will extend MSG to broader downstream tasks such as
segmentation, change detection, and anomaly detection, and
explore scaling MSG to larger pretraining corpora and crosssensor or multimodal pretraining, with further optimization of
efficiency and training stability.
A PPENDIX

Fig. 5. OA versus labeled ratio r under FT.
TABLE XVII
OA C OMPARISON B ETWEEN FS (S CRATCH ) AND FT (P RETRAINED )

This appendix provides supplementary results supporting
Section IV-D, mainly focusing on detailed hyperparameter
sensitivity under linear evaluation and additional FT analyses.
Unless otherwise stated, results are reported as mean±std
over multiple seeds. For conciseness in tables and figures, we
abbreviate WHU-Hi-LongKou as “WHU” and Houston2013
as “Houston.”
A. Detailed Hyperparameter Sensitivity

including mask ratios for the reconstruction and contrastive
branches, spectral group size, encoder depth, embedding
dimension, and other training settings. Overall, MSG remains
stable within a reasonably wide range and achieves a
favorable performance–efficiency balance under the default
configuration. It is worth noting that linear evaluation may
underestimate the impact of model capacity, since the shallow
classifier constrains the expressiveness of learned representations. Nevertheless, consistent performance–efficiency trends
can still be observed, motivating our choice of a balanced
configuration. To keep the main text concise, detailed hyperparameter tables and additional analyses are deferred to
Appendix A.
V. C ONCLUSION
In this article, we present MSG, a joint MSG framework
for hyperspectral representation learning. Rather than loosely

This section reports detailed sensitivity results of key hyperparameters under the linear evaluation protocol. We highlight
the adopted default configuration by boldfacing the corresponding column header.
1) Mask Ratio: To isolate the effects of the two pretraining objectives, we vary the mask ratios under single-branch
configurations, where only one branch is active at a time.
Specifically, the reconstruction sweep activates the reconstruction branch, whereas the contrastive sweep activates the
contrastive branch. As shown in Fig. 4, performance peaks
at τh = 0.7 for reconstruction and τl = 0.3 for contrastive
learning across datasets. A higher reconstruction masking ratio
encourages the model to infer missing spectral–spatial context,
promoting holistic feature learning. Conversely, a lower contrastive masking ratio preserves sufficient anchor information
for stable view alignment and robust discrimination. These
ratios are adopted as the default setting throughout the article.

5509418

2) Spectral Group Size: Table XII reports the sensitivity to the spectral group size g ∈ {8, 16, 32, 64}, which
controls the granularity of spectral tokenization. Smaller g
yields finer-grained tokens and tends to improve accuracy but
increases computational cost (FLOPs/Params). Considering
the performance–efficiency tradeoff, we adopt g = 16 as the
default.
3) Encoder Depth: Table XIII evaluates encoder depth L ∈
{2, 4, 6, 8}. Increasing depth typically improves representation
capacity and benefits performance, while the computational
cost grows roughly linearly with L. We adopt L = 6 as a
balanced default setting.
4) Encoder Dimension: Table XIV studies the embedding
dimension d ∈ {64, 128, 192, 256}. Larger d generally increases
capacity and improves accuracy, but FLOPs/Params grow
rapidly with d. We adopt d = 128 as the default for a favorable
performance–efficiency tradeoff.
5) Balancing Weight: We further examine the sensitivity to
the balancing weight λ, which controls the tradeoff between
masked reconstruction and contrastive discrimination during
joint pretraining. Table XV shows that MSG remains stable
within a moderate range around the default λ = 0.5. This
behavior suggests that the two objectives are well-coupled by
the shared spectral-group representation and do not require
delicate reweighting to work effectively.
6) Pretraining Scale: Finally, we study the impact of
pretraining scale by varying the number of pretraining iterations/samples N ∈ {50k, 100k, 200k, 400k}, while keeping all
other settings fixed. As shown in Table XVI, increasing N
generally improves performance and stabilizes representation
learning, with diminishing returns at larger scales. We adopt
N = 100k as the default to balance accuracy and computational
cost. Notably, the consistent gains across datasets indicate that
MSG benefits from additional unlabeled data without changing
the training recipe, which supports its scalability. This also
suggests that the framework can be readily extended to larger
corpora when computational resources allow.
B. Additional FT Analyses
This section provides supplementary FT results that complement the main experiments in Section IV-D, focusing on
robustness under limited labeled supervision and a comparison
to training from scratch (FS).
1) Robustness to Limited Labels in FT: To evaluate robustness under limited supervision, we vary the labeled ratio r
in FT using a synchronized split protocol: r for training,
r for validation, and 1 − 2r for testing. We consider r ∈
{1%, 2.5%, 5%, 10%} and report results as mean ± std over
multiple random seeds. In this ablation, stride-2 is used for all
datasets to ensure sufficient training samples, especially for
minority classes, at very small labeled ratios such as r = 1%.
Therefore, these results are not directly comparable to the main
FT results, where the default stride is 7 for Berlin, Salinas, and
WHU, and 2 for Houston.
As shown in Fig. 5, performance improves consistently
as more labeled samples become available. MSG remains
competitive even at very small r, indicating that the pretrained
representation transfers reliably to few-shot FT. Due to the
stride-2 sampling used in this ablation, the accuracies for

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

Berlin, Salinas, and WHU at r = 5% are generally higher
than those reported in the main text, while the Houston results
remain consistent.
2) Comparison to Training FS: We further compare fully
supervised training FS with FT from pretrained weights. Both
settings follow the same 5/5/90 split (5% training, 5% validation, and 90% testing). For a fair comparison, the architecture
and optimization settings are kept identical, and only the
initialization differs.
As shown in Table XVII, FT consistently outperforms FS
across all four datasets under the same split. The gains are
particularly pronounced in Houston, where FT improves OA
by more than 12 percentage points, while clear improvements are also observed in Berlin, Salinas, and WHU.
These results indicate that the proposed pretraining learns
transferable spatial–spectral representations that provide a substantially better initialization than random weights. In addition
to improving the final accuracy, pretrained initialization also
leads to lower variance on most datasets, suggesting more
stable optimization in the low-label regime.
R EFERENCES
[1]

F. D. Van der Meer et al., “Multi-and hyperspectral geologic remote
sensing: A review,” Int. J. Appl. Earth Observ. Geoinf., vol. 14, no. 1,
pp. 112–128, 2012.
[2] B. Lu, P. Dao, J. Liu, Y. He, and J. Shang, “Recent advances of hyperspectral imaging technology and applications in agriculture,” Remote
Sens., vol. 12, no. 16, p. 2659, Aug. 2020.
[3] S. Peyghambari and Y. Zhang, “Hyperspectral remote sensing in lithological mapping, mineral exploration, and environmental geology: An
updated review,” J. Appl. Remote Sens., vol. 15, no. 3, Jul. 2021, Art.
no. 031501.
[4] Q. Zhang, Y. Zheng, Q. Yuan, M. Song, H. Yu, and Y. Xiao,
“Hyperspectral image denoising: From model-driven, data-driven, to
model-data-driven,” IEEE Trans. Neural Netw. Learn. Syst., vol. 35,
no. 10, pp. 13143–13163, Oct. 2024.
[5] D. Datta, P. K. Mallick, A. K. Bhoi, M. F. Ijaz, J. Shafi, and J. Choi,
“Hyperspectral image classification: Potentials, challenges, and future
directions,” Comput. Intell. Neurosci., vol. 2022, Apr. 2022, Art. no.
3854635.
[6] X. Wang, J. Liu, W. Chi, W. Wang, and Y. Ni, “Advances in hyperspectral image classification methods with small samples: A review,”
Remote Sens., vol. 15, no. 15, p. 3795, Jul. 2023.
[7] R. Qin and T. Liu, “A review of landcover classification with veryhigh resolution remotely sensed optical images—Analysis unit, model
scalability and transferability,” Remote Sens., vol. 14, no. 3, p. 646,
Jan. 2022.
[8] P. S. Thenkabail, R. B. Smith, and E. De Pauw, “Hyperspectral vegetation indices and their relationships with agricultural crop characteristics,”
Remote Sens. Environ., vol. 71, no. 2, pp. 158–182, Feb. 2000.
[9] J. M. Bioucas-Dias and J. M. P. Nascimento, “Hyperspectral subspace identification,” IEEE Trans. Geosci. Remote Sens., vol. 46, no. 8,
pp. 2435–2445, Aug. 2008.
[10] A. Soltani-Farani, H. R. Rabiee, and S. A. Hosseini, “Spatial-aware
dictionary learning for hyperspectral image classification,” IEEE Trans.
Geosci. Remote Sens., vol. 53, no. 1, pp. 527–541, Jan. 2015.
[11] M. Pal and G. M. Foody, “Feature selection for classification of
hyperspectral data by SVM,” IEEE Trans. Geosci. Remote Sens., vol. 48,
no. 5, pp. 2297–2307, May 2010.
[12] Y. Chen, H. Jiang, C. Li, X. Jia, and P. Ghamisi, “Deep feature extraction and classification of hyperspectral images based on convolutional
neural networks,” IEEE Trans. Geosci. Remote Sens., vol. 54, no. 10,
pp. 6232–6251, Oct. 2016.
[13] S. Yu, S. Jia, and C. Xu, “Convolutional neural networks for hyperspectral image classification,” Neurocomputing, vol. 219, pp. 88–98,
Jan. 2017.
[14] X. He, Y. Chen, and Z. Lin, “Spatial–spectral transformer for hyperspectral image classification,” Remote Sens., vol. 13, no. 3, p. 498, Jan.
2021.

CAO et al.: JOINT MSG FRAMEWORK FOR HYPERSPECTRAL REPRESENTATION LEARNING

[15] X. Yang, W. Cao, Y. Lu, and Y. Zhou, “Hyperspectral image transformer
classification networks,” IEEE Trans. Geosci. Remote Sens., vol. 60,
2022, Art. no. 5528715.
[16] A. Jaiswal, A. R. Babu, M. Z. Zadeh, D. Banerjee, and F. Makedon,
“A survey on contrastive self-supervised learning,” Technologies, vol. 9,
no. 1, p. 2, Dec. 2020.
[17] Y. Wang, C. M. Albrecht, N. A. A. Braham, L. Mou, and X. X. Zhu,
“Self-supervised learning in remote sensing: A review,” IEEE Geosci.
Remote Sens. Mag., vol. 10, no. 4, pp. 213–247, Dec. 2022.
[18] Z. Xie et al., “SimMIM: A simple framework for masked image
modeling,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2022, pp. 9653–9663.
[19] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, “A simple framework
for contrastive learning of visual representations,” in Proc. 37th Int.
Conf. Mach. Learn., vol. 119, 2020, pp. 1597–1607.
[20] J. Chang, L. Wang, G. Meng, S. Xiang, and C. Pan, “Deep adaptive
image clustering,” in Proc. IEEE Int. Conf. Comput. Vis. (ICCV), Oct.
2017, pp. 5879–5887.
[21] I. J. Goodfellow et al., “Generative adversarial nets,” in Proc. Adv.
Neural Inf. Process. Syst., vol. 27, 2014, pp. 2672–2680.
[22] L. Zhu, J. Wu, W. Biao, Y. Liao, and D. Gu, “SpectralMAE:
Spectral masked autoencoder for hyperspectral remote sensing image
reconstruction,” Sensors, vol. 23, no. 7, p. 3728, Apr. 2023.
[23] S. Hou, H. Shi, X. Cao, X. Zhang, and L. Jiao, “Hyperspectral imagery
classification based on contrastive learning,” IEEE Trans. Geosci.
Remote Sens., vol. 60, 2022, Art. no. 5521213.
[24] X. Cao, H. Lin, S. Guo, T. Xiong, and L. Jiao, “Transformer-based
masked autoencoder with contrastive loss for hyperspectral image
classification,” IEEE Trans. Geosci. Remote Sens., vol. 61, 2023, Art.
no. 5524312.
[25] S. Li et al., “Masked modeling for self-supervised representation learning on vision and beyond,” 2023, arXiv:2401.00897.
[26] K. He, X. Chen, S. Xie, Y. Li, P. Dollár, and R. Girshick, “Masked
autoencoders are scalable vision learners,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2022, pp. 16000–16009.
[27] C. Zhang, C. Zhang, J. Song, J. S. K. Yi, K. Zhang, and I. So Kweon,
“A survey on masked autoencoder for self-supervised learning in vision
and beyond,” 2022, arXiv:2208.00173.
[28] Z. Zhou and X. Liu, “Masked autoencoders in computer vision: A comprehensive survey,” IEEE Access, vol. 11, pp. 113560–113579, 2023.
[29] M. Zhang, T. Han, X. Qu, X. Gao, X. Liu, and S. Niu, “Masked
superpixel contrastive subspace clustering network for unsupervised
large-scale hyperspectral image classification,” IEEE Trans. Geosci.
Remote Sens., vol. 63, 2025, Art. no. 5520616.
[30] X. Fang, G. Zhang, G. Zhang, X. Zhou, J. Wu, and L. Zhao, “A
hybrid self-supervised learning framework for hyperspectral image
classification,” in Proc. Int. Conf. Comput., Vis. Intell. Technol., Aug.
2023, pp. 1–7.
[31] Q. Guo, Y. Cen, L. Zhang, Y. Zhang, and Y. Huang, “Hyperspectral
anomaly detection based on spatial–spectral cross-guided mask
autoencoder,” IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens.,
vol. 17, pp. 9876–9889, 2024.
[32] M. Kukushkin, M. Bogdan, and T. Schmid, “BiMAE—A bimodal
masked autoencoder architecture for single-label hyperspectral image
classification,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
Workshops (CVPRW), Jun. 2024, pp. 2987–2996.
[33] V. Hondru, F. A. Croitoru, S. Minaee, R. T. Ionescu, and N. Sebe,
“Masked image modeling: A survey,” Int. J. Comput. Vis., vol. 133,
no. 10, pp. 1–47, Oct. 2025.
[34] J. M. Lehner, B. Alkin, A. Fürst, E. Rumetshofer, L. Miklautz, and
S. Hochreiter, “Contrastive tuning: A little help to make masked autoencoders forget,” in Proc. AAAI Conf. Artif. Intell., 2024, vol. 38, no. 4,
pp. 2965–2973.
[35] V. Marsocci and N. Audebert, “Cross-sensor self-supervised training and
alignment for remote sensing,” IEEE J. Sel. Topics Appl. Earth Observ.
Remote Sens., vol. 18, pp. 12278–12289, 2025.
[36] H. Hu, X. Wang, Y. Zhang, Q. Chen, and Q. Guan, “A comprehensive
survey on contrastive learning,” Neurocomputing, vol. 610, Dec. 2024,
Art. no. 128645.
[37] K. He, H. Fan, Y. Wu, S. Xie, and R. Girshick, “Momentum contrast for
unsupervised visual representation learning,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020, pp. 9729–9738.
[38] M. Wang, F. Gao, J. Dong, H.-C. Li, and Q. Du, “Nearest neighbor-based
contrastive learning for hyperspectral and LiDAR data classification,”
IEEE Trans. Geosci. Remote Sens., vol. 61, 2023, Art. no. 5501816.

5509418

[39] Y. Wang, X. Chen, E. Zhao, C. Zhao, M. Song, and C. Yu, “An
unsupervised momentum contrastive learning based transformer network
for hyperspectral target detection,” IEEE J. Sel. Topics Appl. Earth
Observ. Remote Sens., vol. 17, pp. 9053–9068, 2024.
[40] Q. Liu, J. Peng, N. Chen, W. Sun, Y. Ning, and Q. Du, “Category-specific
prototype self-refinement contrastive learning for few-shot hyperspectral image classification,” IEEE Trans. Geosci. Remote Sens., vol. 61,
2023, Art. no. 5524416.
[41] N. A. A. Braham, J. Mairal, J. Chanussot, L. Mou, and X. X. Zhu,
“Enhancing contrastive learning with positive pair mining for few-shot
hyperspectral image classification,” IEEE J. Sel. Topics Appl. Earth
Observ. Remote Sens., vol. 17, pp. 8509–8526, 2024.
[42] B. Yang and B. Wang, “Band-wise nonlinear unmixing for hyperspectral
imagery using an extended multilinear mixing model,” IEEE Trans.
Geosci. Remote Sens., vol. 56, no. 11, pp. 6747–6762, Nov. 2018.
[43] Y. Li, H. Zhang, and Q. Shen, “Spectral–spatial classification of hyperspectral imagery with 3D convolutional neural network,” Remote Sens.,
vol. 9, no. 1, p. 67, 2017.
[44] J. Yang, B. Du, and C. Wu, “Hybrid vision transformer model for
hyperspectral image classification,” in Proc. IEEE Int. Geosci. Remote
Sens. Symp. (IGARSS), Jul. 2022, pp. 1388–1391.
[45] J. Sun et al., “Fusing spatial attention with spectral-channel
attention mechanism for hyperspectral image classification via
encoder–decoder networks,” Remote Sens., vol. 14, no. 9, p. 1968,
Apr. 2022.
[46] L. Zhang, Y. Wei, J. Liu, J. Wu, and D. An, “A hyperspectral band
selection method based on sparse band attention network for maize seed
variety identification,” Expert Syst. Appl., vol. 238, Mar. 2024, Art. no.
122273.
[47] J. Chen, S. Liu, Z. Zhang, and H. Wang, “Diffusion subspace clustering
for hyperspectral images,” IEEE J. Sel. Topics Appl. Earth Observ.
Remote Sens., vol. 16, pp. 6517–6530, 2023.
[48] W. Liu et al., “Self-supervised feature learning based on spectral
masking for hyperspectral image classification,” IEEE Trans. Geosci.
Remote Sens., vol. 61, 2023, Art. no. 4407715.
[49] Y. Li, R. Wu, Q. Tan, Z. Yang, and H. Huang, “Masked spectral bands
modeling with shifted windows: An excellent self-supervised learner for
classification of medical hyperspectral images,” IEEE Signal Process.
Lett., vol. 30, pp. 543–547, 2023.
[50] J. Lin, X. Jin, F. Gao, J. Dong, and H. Yu, “Boosting spatial–spectral
masked auto-encoder through mining redundant spectra for HSISAR/LiDAR classification,” in Proc. IEEE Int. Geosci. Remote Sens.
Symp. (IGARSS), Jul. 2024, pp. 9744–9747.
[51] L. Scheibenreif, M. Mommert, and D. Borth, “Masked vision transformers for hyperspectral image classification,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit. Workshops (CVPRW), Jun. 2023,
pp. 2166–2176.
[52] M. H. P. Fuchs and B. Demir, “HySpecNet-11k: A large-scale hyperspectral dataset for benchmarking learning-based hyperspectral image
compression methods,” in Proc. IEEE Int. Geosci. Remote Sens. Symp.
(IGARSS), Jul. 2023, pp. 1779–1782.
[53] A. Okujeni, S. van der Linden, and P. Hostert, “Berlin-urban-gradient
dataset 2009-an EnMAP preparatory flight campaign,” EnMAP Flight
Campaigns, GFZ Data Services, Potsdam, Germany, Tech. Rep., 2016,
pp. 1–9, doi: 10.2312/enmap.2016.008.
[54] Y. Zhong, X. Hu, C. Luo, X. Wang, J. Zhao, and L. Zhang, “WHU-hi:
UAV-borne hyperspectral with high spatial resolution (H2 ) benchmark
datasets and classifier for precise crop identification based on deep convolutional neural network with CRF,” Remote Sens. Environ., vol. 250,
Dec. 2020, Art. no. 112012.
[55] C. Debes et al., “Hyperspectral and LiDAR data fusion: Outcome of the 2013 GRSS data fusion contest,” IEEE J. Sel. Topics
Appl. Earth Observ. Remote Sens., vol. 7, no. 6, pp. 2405–2418,
Jun. 2014.
[56] J. Lin, F. Gao, X. Shi, J. Dong, and Q. Du, “SS-MAE:
Spatial–spectral masked autoencoder for multisource remote sensing
image classification,” IEEE Trans. Geosci. Remote Sens., vol. 61, 2023,
Art. no. 5531614.
[57] Y. Wang et al., “HSIMAE: A unified masked autoencoder with largescale pretraining for hyperspectral image classification,” IEEE J. Sel.
Topics Appl. Earth Observ. Remote Sens., vol. 17, pp. 14064–14079,
2024.
[58] S. Mohamed, M. Haghighat, T. Fernando, S. Sridharan, C. Fookes, and
P. Moghadam, “FactoFormer: Factorized hyperspectral transformers with
self-supervised pretraining,” IEEE Trans. Geosci. Remote Sens., vol. 62,
2023, Art. no. 5501614.

5509418

IEEE TRANSACTIONS ON GEOSCIENCE AND REMOTE SENSING, VOL. 64, 2026

Minzhen Cao (Graduate Student Member, IEEE)
received the B.Eng. degree in engineering mechanics from Dalian University of Technology, Dalian,
China, in 2021. He is currently pursuing the Ph.D.
degree with the School of Computer Science and
Technology, Tongji University, Shanghai, China.
His research interests include image analysis,
self-supervised learning, remote sensing, geographic
information systems, and disaster prediction.

Hao Deng (Senior Member, IEEE) received the B.S.
and Ph.D. degrees from the Department of Physical
Electronics, University of Electronic Science and
Technology of China, Chengdu, China, in 2007 and
2015, respectively.
He is currently an Associate Professor with the
School of Computer Science and Technology, Tongji
University, Shanghai, China. His research interests
include machine learning and dynamical models for
nonstationary open-world scenarios.

Bowen Du (Member, IEEE) received the B.Eng.
and M.Eng. degrees in software engineering from
Tongji University, Shanghai, China, in 2013 and
2016, respectively, and the Ph.D. degree in computer
science from the University of Warwick, Coventry,
U.K., in 2022.
He is currently an Assistant Professor with the
School of Computer Science and Technology, Tongji
University. His research interests include artificial
intelligence, cyber–physical systems, and software
engineering.

Shengjie Zhao (Senior Member, IEEE) received
the B.S. degree in electrical engineering from the
University of Science and Technology of China,
Hefei, China, in 1988, the M.S. degree in electrical
and computer engineering from China Aerospace
Institute, Beijing, China, in 1991, and the Ph.D.
degree in electrical and computer engineering from
Texas A&M University, College Station, TX, USA,
in 2004.
He is currently a Professor with the School of
Computer Science and Technology, Tongji University, Shanghai, China. In previous postings, he conducted research at Lucent
Technologies, Whippany, NJ, USA, and China Aerospace Science and Industry Corporation, Beijing. He is an Academician of the International Eurasian
Academy of Sciences. His research interests include artificial intelligence, big
data, wireless communications, image processing, and signal processing.
PAPER_TEXT
