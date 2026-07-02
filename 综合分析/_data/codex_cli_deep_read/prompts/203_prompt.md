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
# [203] Curved Geometric Networks for Visual Anomaly Recognition
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
编号：203
题名：Curved Geometric Networks for Visual Anomaly Recognition
年份：2023
DOI：10.1109/tnnls.2023.3309846
来源：IEEE Transactions on Neural Networks and Learning Systems
PDF：paper/10.1109_TNNLS.2023.3309846.pdf
已有粗分类：多媒体、医学、遥感与视频异常检测
二级关联：其他AI安全与跨域异常检测
相关性：弱相关，分数 2
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\203.txt
- 原始字符数：70386
- 本次发送字符数：70386
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 12, DECEMBER 2024

17921

Curved Geometric Networks for
Visual Anomaly Recognition
Jie Hong , Pengfei Fang , Weihao Li, Junlin Han, Lars Petersson, and Mehrtash Harandi

Abstract— Learning a latent embedding to understand the
underlying nature of data distribution is often formulated in
Euclidean spaces with zero curvature. However, the success
of the geometry constraints, posed in the embedding space,
indicates that curved spaces might encode more structural
information, leading to better discriminative power and
hence richer representations. In this work, we investigate
the benefits of the curved space for analyzing anomalous,
open-set, or out-of-distribution (OOD) objects in data. This
is achieved by considering embeddings via three geometry
constraints, namely, spherical geometry (with positive curvature),
hyperbolic geometry (with negative curvature), or mixed
geometry (with both positive and negative curvatures). Three
geometric constraints can be chosen interchangeably in a unified
design, given the task at hand. Tailored for the embeddings in
the curved space, we also formulate functions to compute the
anomaly score. Two types of geometric modules (i.e., geometricin-one (GiO) and geometric-in-two (GiT) models) are proposed
to plug in the original Euclidean classifier, and anomaly scores
are computed from the curved embeddings. We evaluate the
resulting designs under a diverse set of visual recognition
scenarios, including image detection (multiclass OOD detection
and one-class anomaly detection) and segmentation (multiclass
anomaly segmentation and one-class anomaly segmentation). The
empirical results show the effectiveness of our proposal through
consistent improvement over various scenarios. The code is made
available at https://github.com/JHome1/GiO-GiT.

Manuscript received 28 July 2022; revised 27 May 2023;
accepted 18 August 2023. Date of publication 8 September 2023; date
of current version 3 December 2024. This work was supported in part by
the National Science Foundation of China under Grant 62306070 and in part
by the Southeast University Start-Up Grant for New Faculty under Grant
4009002309. The work of Mehrtash Harandi was supported by the Australian
Research Council (ARC) under Project DP230101176. (Corresponding
author: Pengfei Fang.)
Jie Hong and Junlin Han are with the College of Engineering,
Computing and Cybernetics, Australian National University, Canberra,
ACT 2601, Australia, and also with Data61-CSIRO, Black Mountain
Laboratories, Canberra, ACT 2601, Australia (e-mail: jie.hong@anu.edu.au;
u6835134@anu.edu.au).
Pengfei Fang is with the School of Computer Science and Engineering and
the Key Laboratory of New Generation Artificial Intelligence Technology and
Its Interdisciplinary Applications, Ministry of Education, Southeast University,
Nanjing, 210096, China (e-mail: fangpengfei@seu.edu.cn).
Weihao Li is with the College of Engineering, Computing and Cybernetics,
Australian National University, Canberra, ACT 2601, Australia (e-mail:
weihao.li1@anu.edu.au).
Lars Petersson is with Data61-CSIRO, Black Mountain Laboratories,
Canberra, ACT 2601, Australia (e-mail: lars.petersson@data61.csiro.au).
Mehrtash Harandi is with the Department of Electrical and Computer
Systems Engineering, Monash University, Clayton, VIC 3800, Australia
(e-mail: mehrtash.harandi@monash.edu).
This article has supplementary downloadable material available at
https://doi.org/10.1109/TNNLS.2023.3309846, provided by the authors.
Digital Object Identifier 10.1109/TNNLS.2023.3309846

Index Terms— Anomaly recognition, geometric learning,
hyperbolic space, mixed-curvature space, open-set recognition,
out-of-distribution (OOD) detection, spherical space.

I. I NTRODUCTION

I

N THIS article, we aim to leverage the curved geometry for
learning embeddings, which in return allows us to analyze
and identify anomalous, open-set, or out-of-distribution (OOD)
objects from normal, closed-set, or in-distribution (ID) input
data. Nonflat geometry has gained an increasing amount
of interest in various machine learning approaches due to
its intriguing properties in encoding the inherent geometry
or hidden structure information of the data [1], [2], [3],
[4], [5], [6]. For example, spherical spaces with constant
positive curvature show appealing properties along with
deep neural networks (DNNs) to encode samples resembling
the sphere [7], [8]. Hyperbolic spaces, featured with a
constant negative curvature, are shown to be rich in encoding
the underlying hierarchical structure in the data. Such a
property enables hyperbolic spaces to better discriminate
input samples [4]. Fig. 1 conceptualizes the distinctive
characteristics of Euclidean, spherical, and hyperbolic spaces
and highlights their disparities. Euclidean spaces with zero
curvature are familiar faces in DNNs [see Fig. 1(a)]. Spherical
geometry, as shown in Fig. 1(b), has been successfully
employed to encode directional data (i.e., samples where
the magnitude does not carry important information). The
Poincaré ball model for the hyperbolic spaces, as shown in
Fig. 1(c), provides a structure with constant negative curvature
to encode data.
Previous studies, such as [4], [11], and [12], show that
curved spaces can attain a superior performance gain over
the Euclidean space, especially for tasks relying on image
embeddings (e.g., zero-/few-shot learning or metric learning).
For example, in [12], by employing the similarity metric
in spherical embedding spaces, the model enhances its
discriminative ability in zero-shot classification for unknown
classes. In [4] and [13], hyperbolic spaces are shown to
have a better distribution across unknown classes, therefore
improving few-shot learning performance. Based on the
interpretations in Fig. 1, we infer that the curved geometric
embeddings exhibit enhanced discrimination due to the
following reasons.
1) In the spherical space, all points are constrained to lie
on the surface of a hypersphere, as shown in Fig. 1(b).
On the surface of the hypersphere, the embedding

2162-237X © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

17922

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 12, DECEMBER 2024

Fig. 1. Illustration of Euclidean space and curved spaces (i.e., spherical and hyperbolic spaces). (a) Euclidean space represents a flat space without curvature.
(b) In contrast, the spherical space restricts all points to lie on the surface of a hypersphere. (c) Hyperbolic space, represented by the Poincaré ball model,
makes points exist inside the ball, demonstrating its negatively curved nature. The transformation from Euclidean space to spherical or hyperbolic space can
be achieved through respective spherical or hyperbolic transformation, which project points onto the corresponding curved space.

Fig. 2.
Illustration of the discrimination ability of curved spaces on
unknown data. We train two models using Euclidean and hyperbolic geometry
on miniImageNet dataset [9], following the few-shot learning protocol.
We randomly choose four unknown classes and plot the class embeddings
using t-SNE [10]. Each unknown class is represented by one color. From
this visualization, we can directly observe that within each unknown class,
embeddings in hyperbolic space (see the figure on the right) show a more
compact distribution than embeddings in Euclidean space (see the figure
on left). Moreover, it can be observed that hyperbolic embeddings exhibit
improved separations based on the discovered hierarchies. For instance,
when compared to the distribution of Euclidean embeddings, hyperbolic
embeddings show closer proximity between classes (i.e., the yellow-colored
“African hunting dog” and the green-colored “lion”) that belong to the same
superclass (i.e., “animal”). Conversely, hyperbolic embeddings of classes (i.e.,
the olive-colored “ant” and the purple-colored “bookshop”), which belong to
different superclasses (i.e., “insect” and “building”), are pulled further apart.

space is enforced to have a uniform distribution
across multiple classes, promoting a more unbiased
classification. Furthermore, scale-free analysis, the
inclusion of spherical spaces, e.g., via ℓ2 normalization
in a DNN, provides useful constraints for learning and
has been used with success in the majority of modern
neural structures [7], [8], [14].
2) As shown in Fig. 1(c), points in the hyperbolic space
lie inside the ball. The volume in a hyperbolic space
expands exponentially with dimensions. This enables us
to embed tree-like structures with less distortion (see
the green-colored triangle) and aids the discovery of
hierarchical relationships among samples. For instance,
as shown in Fig. 2 and compared to Euclidean
embeddings, the hyperbolic embeddings of “African
hunting dog” (yellow) and “lion” (green) are closer,
emphasizing their similarity at the superclass level (i.e.,
“animals”). Moreover, the hyperbolic embeddings of

“ant” (olive) and “bookshop” (purple) exhibit better
separation than Euclidean embeddings as they originate
from distinct superclasses, “insect” and “building.”
Learning such hierarchies will lead to success at the
inference.
With the appealing observations shown above, in this
article, we investigate the practice of using geometries with
fixed nonzero curvature in visual anomaly, open-set, or OOD
recognition tasks. For the purpose of realizing our idea,
a natural solution is to simply replace the existing Euclidean
classifier with one based on a curved geometry. This idea
is behind the design of our geometric-in-one (GiO) model.
In addition, we also find that the “divergence” between
Euclidean embeddings and curved embeddings can provide
a reliable indicator useful for anomaly, open-set, or OOD
identification. To benefit from this interesting observation,
we further develop a geometric-in-two (GiT) model. Having
multiple geometry-aware networks at our disposal, we further
present approaches for getting the anomaly score to identify
abnormal objects.
Our main objective is to show that geometry plays an
essential role in identifying anomalies. As such, we develop
a generic solution and incorporate it into various baselines in
our empirical study. The contributions of this work can be
summarized as follows.
1) We propose two types of lightweight curvature-aware
geometric networks for visual anomaly, open-set,
or OOD recognition. To the best of our knowledge,
this is the first attempt to adopt curved manifolds as
embedding spaces to distinguish normal/closed-set/ID
and anomalous/open-set/OOD data. In addition, multiple
curved spaces, including spherical, hyperbolic, and
mixed spaces, are studied.
2) Extensive experiments on a wide range of visual
anomaly, open-set, or OOD recognition tasks (e.g.,
multiclass OOD detection, one-class anomaly detection, multiclass anomaly segmentation, and one-class
anomaly segmentation) suggest that the proposed
technique leads to a substantial performance gain over
the Euclidean geometry.

HONG et al.: CURVED GEOMETRIC NETWORKS FOR VISUAL ANOMALY RECOGNITION

II. R ELATED W ORK
A. Visual Anomaly Recognition
Three main approaches are developed for doing visual
anomaly (or open-set/OOD) recognition: confidence-,
generative-, and self-supervised-based methods. However,
a few works are learning features in non-Euclidean spaces.
1) Confidence-Based Method: It is well known that the
confidence from the softmax in a classifier helps to detect
OOD samples from ID samples since ID samples are
more likely to have a greater maximum softmax confidence
compared to ODD samples [15]. OOD detector for neural
network (ODIN) [16] applies temperature scaling to the
confidence vector and adds small perturbations to input
samples for more accurate OOD detection. Additional
confidence-based methods, which make use of the confidence,
have been studied in [17], [18], [19], [20], and [21].
2) Generative-Based Method: One of the generative-based
methods is to synthesize effective training samples to avoid the
DNNs becoming overconfident in their predictions [22], [23],
[24], [25], [26]. Another choice is to optimize features in the
latent space of an encoder–decoder network toward generating
a more general distribution [27], [28], [29], [30], [31] or a
more representative attention map [32], [33], [34].
3) Self-Supervised-Based Method: Self-supervised learning
techniques have been widely employed in anomaly recognition. Ensemble leave-out classifier (ELOC) [35] trains
classifiers in a self-supervised manner by setting a subset
of training data as OOD data. One main idea behind the
self-learning method is to apply geometric transformations
(GTs) or augmentations on the input images and train a
multiclass model to discriminate such transformations (or
augmentations). Prediction of image rotation is used in
rotation network (RotNet) [36]. Jittered patches of an image
are classified in Patch-SVDD [37] for anomaly localization.
Another idea is to use contrastive learning for better visual
representations [38], [39], [40]. More works using selfsupervised learning are presented in [38], [41], [42], [43], [44],
[45], and [46].
Some other facts should be noted.
1) Confidence-based as well as self-supervised-based
methods mainly adopt “encoder–classifier” structures
and generative-based models with “encoder–decoder”
architectures. The proposed modules in our work are
best applied to an “encoder–classifier” rather than an
“encoder–decoder” structure.
2) Teacher–student structures have been utilized in anomaly
recognition problems [47], [48], [49], [50]. These
approaches demonstrate the effectiveness of leveraging
the discrepancy between the teacher and student
branches to identify and localize anomalies. In [49],
a pair of networks are employed for anomaly detection,
where the teacher network is pretrainedon ImageNet.
The discrepancy between multilevel layers is utilized to
compute anomaly scores. In the case of the local–global
net proposed in [50], a teacher–student architecture is
trained to compute local and global features. In the

17923

inference, local and global features are compared to
compute the anomaly score.
3) Some approaches compute the anomaly score of
test samples by comparing their features with those
of training samples [37], [45]. In the Patch-SVDD
method [37], for instance, the anomaly scores of test
samples are obtained by calculating the L2 distance
between the features of the test and training samples.
B. Geometric Learning
Geometric learning has been studied extensively to encode
structured representations [51]. For example, the set has been
used to model order-invariant data (e.g., 3-D point clouds [52]
or video data [53]). Orthogonal constraints, i.e., subspaces,
are often used to encode set data [54], [55], for its potential
to be robust against illumination variations, background, and
so on. In vectorized representations, spherical or hyperbolic
spaces are also very effective for metric learning-related tasks.
In the spherical space, the similarity of representations is upper
bounded. Hence, such a space is particularly well-behaved
at learning a metric space [7], [56], [57]. As opposed to
the spherical space, tree-like data can be embedded in the
hyperbolic space for its intriguing property to capture the
hierarchical structure of the data [4], [11], [58]. To further
increase the discrimination power of the learned embeddings
in curved spaces, the kernel methods, which implicitly map the
geometric representation to a high or even infinite-dimensional
feature space, are studied for spherical embgedings [59] or
hyperbolic embeddings [13]. To fully model the structure
of the data, mixed-curved spaces are good candidates as
embedding spaces [14], [60].
III. P RELIMINARIES AND BACKGROUND
In this section, we will briefly introduce the preliminary
knowledge and background used in this article.
A. Notation
We use κ to denote the curvature of a manifold. In general,
a vectorized representation or an embedding can be embedded
in three types of manifolds: the Euclidean space M E ,
the spherical space M S , and the hyperbolic space M H ,
corresponding to κ = 0, κ > 0, and κ < 0, respectively.
Throughout this article, we call any space with κ ̸ = 0, as a
curvature-aware space or a curved space. A mixed-curvature
manifold M M is a product space, consisting of a set of
different spaces [14], [60]. In our work, the mixed-curvature
manifold is defined as M M = M1 × M2 × M3 × · · · × M N ,
in which we mix N different manifolds. For example, the
mixed-curvature manifold M M = M E × M S × M H includes
a Euclidean space, a spherical space, and a hyperbolic space.
B. Spherical Geometry
The n-sphere with curvature κ > 0 is defined as

Sn−1
= x ∈ Rn : ∥x∥2 = 1/κ .
κ

(1)

17924

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 12, DECEMBER 2024

Fig. 3. General frameworks of the models and their training processes are depicted. (a) Baseline model follows an “encoder–classifier” structure. The
image encoder takes the input image I and encodes it into an embedding vector e E . The classifier, primarily composed of an FC layer, generates the
confidence vector for loss computation. We propose two models in our work: GiO and GiT. GiO and GiT differ from the baseline model in that they integrate
the GT and geometric FC layer into the classifier. In essence, while the baseline model follows an “encoder–classifier” structure, GiO and GiT adopt an
“encoder-geometric-classifier” structure. (b) In the GiO model, the original Euclidean FC layer is replaced with a geometric FC layer based on a curved
geometry. (c) GiT model adopts the geometric FC layer as the additional branch. In the training stage, we follow the setting that the training data do not
include any anomalous or OOD samples.

The mapping 0S : Rn → Sn−1
projects an embedding x ∈ Rn
κ
generated by an image encoder to n-sphere as
x
x S = 0S (x) = √
.
(2)
κ∥x∥
The embedding x S indicates a point in the n-sphere,
satisfying the constraint in (1). In practice, the angular
mapping in the n-sphere, analogous to the linear mapping in
the Euclidean space, can be realized by a fully connected (FC)
layer with weight W. Let W = [w1 , w2 , . . . , w j , . . . , wC ],
where w j ∈ Sn−1
is the corresponding column, representing
κ
the parameters of the classifier. The prediction associated
with the jth class for an embedding x is determined by w j .
We note that for x, w j ∈ Sn−1
κ , the term for the jth class,
lS (x, w j ) = ⟨x, w j ⟩, is indeed related to the geodesic distance
on Sn−1
κ ; hence, one can understand this term as a form of
the distance-based value. Here, we use the notation lS (x, W)
to show a vector obtained by applying the columns of W to
x ∈ Sn−1
κ .
For the spherical network, we compute the angular loss ℓS
based on B samples in one batch

exp lS,yi
1 X

ℓS = −
log P
(3)
B i
j exp lS, j
where lS, j is the jth element in lS (x, W) under the ith input
sample and x ∈ Sn−1
κ . Accordingly, l S,yi is the the yi th element
in lS (x, W) and yi indicates the label class to the ith input
sample.
C. Hyperbolic Geometry
In contrast to the n-sphere Sn−1
κ , the hyperbolic space
is a curved space with a constant negative curvature (i.e.,
κ < 0). The hyperbolic space offers an appealing property for
anomaly problems. Specifically, the volume in the hyperbolic
space increases exponentially. This allows the algorithm to
incorporate more embeddings of unknown objects, particularly

those closer to the origin, as the space expands from the
origin [4].
In this article, we employ the Poincaré ball [1], [4] to
model and work with the hyperbolic space. The n-dimensional
Poincaré ball, with curvature κ, is defined by the manifold

Hnκ = x ∈ Rn : ∥x∥ < −1/κ .1
To embed x ∈ Rn , obtained by an image encoder to the
Poincaré ball, we use the following transformation:

1

 x,
if ∥x∥ ≤
|κ|
x H = 0H (x) = 1 − ξ x
(4)


, else
|κ| ∥x∥
where ξ > 0 is a small value to ensure numerical stability.
The embedding x H is a point in the Poincaré ball. To enable
the vector operations in the Poincaré ball, we make use of the
Möbius addition for x, y ∈ Hnκ as


1 + 2|κ|⟨x, y⟩ + |κ|∥y∥2 x + 1 − |κ|∥x∥2 y
x ⊕κ y =
(5)
1 + 2|κ|⟨x, y⟩ + |κ|2 ∥x∥2 ∥y∥2
where ⟨, ⟩ is the inner product. The geodesic distance between
x, y ∈ Hnκ is defined as
p

2
dGeo (x, y) = √ tanh−1 |κ|∥ − x ⊕κ y∥ .
(6)
|κ|
One can also generalize the hyperbolic linear operation,
parameterized by W (e.g., the hyperbolic linear layer), in the
Poincaré ball [4]

p
 Wx
1
∥Wx∥
−1
tanh
|κ|∥x∥
.
W⊕κ (x) := √ tanh
∥x∥
∥Wx∥
|κ|
(7)
The proposed network contains the multiclass classification
layer. We employ the generalization of multiclass logistic
regression (MLR) to the hyperbolic spaces [4]. Following the
1 In this case, the Riemannian metric is defined as g H (x) = λ2 (x) · g E ,
κ
κ
1
E is the Euclidean metric.
where λκ (x) = 1+κ∥x∥
2 , and g

HONG et al.: CURVED GEOMETRIC NETWORKS FOR VISUAL ANOMALY RECOGNITION

17925

work in [4], the formulation of the hyperbolic MLR for C
classes is given by:

function tanh(.) is employed to make sure that the anomaly
score AS falls between 0 and 1.

l H (y = j|x)

A. GiO Model

λκ (x)∥W j ∥
sinh−1
∝ exp
√
|κ|

!!
√
2 |κ|⟨−p j ⊕κ x, W j ⟩

1 − |κ| · ∥ − p j ⊕κ x∥2 ∥W j ∥
(8)

where j ∈ {1, 2, . . . , C}. Here, x ∈ Hnκ is an embedding in the
hyperbolic space, and p j ∈ Hnκ , W j ∈ Tpκ Hnκ \{0} are learnable
weights.
IV. A PPROACH
Visual anomaly (or open-set/OOD) recognition aims to
identify abnormal (or open-set/OOD) samples from normal (or
closed-set/ID) samples. During the training process, as shown
in Fig. 3, only normal, closed-set, or ID data can be accessed.
For the evaluation stage, as shown in Fig. 4, both normal
(or ID) and anomalous (or OOD) inputs to be recognized
exist.
The pipeline of the baseline is shown in Fig. 3(a) for
the training phase and Fig. 4(a) for the inference phase.
Specifically, an image encoder first maps the input image
to a feature embedding e E , lying in a Euclidean space. The
following FC layer and Softmax function further predict the
probability belonging to each normal (or ID) class, denoted
by c E [see Fig. 3(a)]. In the evaluation process, to identify
whether the input image or pixel is an outlier (also known
as anomalous, open-set, or OOD data), one needs to define
the anomaly score AS ∈ [0, 1]. In this vanilla model
[see Fig. 4(a)], we follow the common practice in [15] to
define the anomaly score by leveraging the predication c E as
AS = 1 − max(c E ).
A curvature-aware geometric model indicates a model
where its classifier operates in a curved space MG , and
we term its classifier geometric classifier. Two curvatureaware geometric models are presented in this section: GiO
and GiT, as shown in Fig. 3(b) and (c). Compared to the
baseline model, the curvature-aware geometric model has two
geometric layers, namely, GT and geometric FC layer. The
GT is to transform the Euclidean embedding e E computed by
an image encoder to the geometric embedding eG (see (2)
for the spherical geometry M S and (4) for the hyperbolic
geometry M H ). The geometric FC layer is a generalization
of the FC layer in MG (e.g., the angular linear layers in M S
or the hyperbolic linear layers in M H ). As shown in Fig. 3,
we learn geometric classifiers where embeddings extracted
from an image encoder are manipulated in the curved spaces.
During the inference phase, as shown in Fig. 4(b) and (c),
the geometric score z is initially obtained from the curved
embedding. In GiO, the variable z can be interpreted as the
distance value between the curved embedding point and the
reference point in the curved space. In GiT, z represents
the discrepancy between two embeddings originating from
different spaces. Subsequently, the anomaly score in our
geometric model is computed as AS = 1 − tanh(z). Since
z ∈ [0, +∞) is not constrained within the range of 0–1, the

We first introduce a single-branch framework, i.e., the GiO
model. The GiO model [see Fig. 3(b)] is a natural modification
that replaces the Euclidean embeddings with curved geometry
embeddings. It provides a straightforward comparison to
justify the advantages of using curved geometry for anomaly
recognition. Specifically, as shown in Fig. 3(b), the image or
pixel embeddings can be obtained by applying the GT function
(i.e., (2) for M S and (4) for M H ) to the feature vectors
encoded by the image encoder. Then, the following geometric
classifier, realized by the geometric FC layer, is further used to
predict the class of its input. For example, the hyperbolic-inone (HiO) model refers to a network with a geometric classifier
in the hyperbolic space. Compared to the baseline model [see
Fig. 3(a)], the GiO model only modifies the embedding layer
and classifier without bringing extra parameters, thereby being
a cheap yet flexible solution.
In the GiO model, the geometric score z G ∈ {z S , z H , z M }
can be obtained from embedding eG . In our work, the
geometric score from the spherical manifold M S is defined
as
z S (e S ) = max(lS (e S , W))

(9)

where e S ∈ Sn−1
κ . Experiments in [7] and [31] verified that

z S from M S is suitable for visual tasks under the open-set
protocol. Hence, we expect that z S could help in anomaly,
open-set, or OOD recognition. For the hyperbolic space M H ,
the geometric score is defined as
z H (e H ) = dGeo (e H , 0 H )

(10)

where dGeo (e H , 0 H ) is also known as the geodesic distance
between the point e H and the origin 0 H , for e H , 0 H ∈ Hnκ .
The experiment of image-level OOD detection in [4] shows
the property of e H , and the hyperbolic embedding points of
OOD samples are closer to the origin. In the mixed-curvature
manifold M M , the geometric score z M is formulated as
z 2M =

N
X

z 2M,i

(11)

i

where there are N spaces in M M and z M,i is the
geometric score from the ith component space. For instance,
in M M = M S × M H , z 2M = z 2S + z 2H . The GiO model with
M M = M S × M H is actually a two-branch architecture.
We can even incorporate the Euclidean space into the mixedin-one (MiO) model. In M M = M E ×M S ×M H , we can have
z 2M = z 2E + z 2S + z 2H where the geometric score from Euclidean
space is z E = max(c E ) [15]. Table I lists the proposed
geometric networks, in conjunction with the geometry score,
in the GiO model.
Having the geometry score z G at our disposal, the anomaly
score is defined as AS = 1 − tanh(z G ). A higher value of AS
indicates a higher probability that the input is coming from the
anomalous distribution. The purpose of tanh(·) is to normalize
z G to a value that is in the range of 0–1 [see Fig. 4(b)].

17926

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 12, DECEMBER 2024

Fig. 4. General frameworks of the models and their evaluation processes are depicted. In the evaluation stage, the model would process both normal (or
ID) and anomalous (or OOD) inputs. The geometric score z G is extracted from the curved embedding for anomaly score computation in the GiO model. For
the GiT model, the geometric score z E G is obtained via Euclidean and curved embeddings. During the evaluation process, GiO and GiT models use the less
parameters than the baseline. (a) Baseline model. (b) GiO model. (c) GiT model.

TABLE I
P ROPOSED G EOMETRIC N ETWORKS IN THE G I O M ODEL AND THE G I T
M ODEL . “A BB .,” “G EO . C OMPONENTS ,” AND “G EO . S CORE ” I NDICATE
“ABBREVIATION ,” “G EOMETRY C OMPONENTS ,” AND “G EOMETRY
S CORE ,” R ESPECTIVELY

spherical-in-two (SiT), hyperbolic-in-two (HiT), and mixedin-two (MiT) models, and thereby, z E G ∈ {z E S , z E H , z E M }
where z E S , z E H , and z E M are from three models. The values
z E S and z E H can be easily calculated by (12). Inspired by (11),
we define z E M in M M as follows:
z 2E M =

N
X

z 2E M,i

(13)

i

B. GiT Model
Several recent works [47], [48], [49], [50] develop the
dual-branch architecture and exploit the discrepancy between
features in separate classifiers for anomaly, open-set, or OOD
recognition. Motivated by this fact, we further introduce our
second framework, termed GiT, where a Euclidean classifier
and a geometric classifier are integrated after the image
encoder [see Fig. 3(c)]. In the GiT model, in parallel with
a branch of the Euclidean classifier, the other branch learns
the feature embedding in the curved space, and the following
geometric FC layer is used as a class predictor. The embedding
in the curved space MG is achieved by transforming e E
to eG via a GT function, as shown in Fig. 3(c). In such
a pipeline, the geometry-aware score z E G is defined as the
discrepancy between distributions of e E and eG , measured via
the Kullback–Leibler (KL) divergence, as follows:
X
p E,i
zEG =
p E,i log
(12)
p
G,i
i
where p E,i and pG,i are the ith element in p E and pG ,
respectively. Here, p E = softmax(e E ) and pG = softmax(eG ).
The geometric score z E G is essentially the distribution
discrepancy between the learned embedding e E from M E
and eG from MG . We have three types of GiT models:

where N indicates the number of component spaces in M M .
For example, when M M = M S × M H , the score metric
can be obtained by z 2E M = z 2E S + z 2E H . The GiT model with
M M = M S × M H is actually a three-branch architecture.
Our experiments show that z E G is able to provide reliable
discrimination information for anomaly identification. We find
that similar to our GiO models, the anomaly score of GiT
models should be AS = 1 − tanh(z E G ) [see Fig. 4(c)]. Table I
lists the networks and the geometry score in the GiT model.
C. Model Training
In the baseline model, as shown in Fig. 3(a), the Euclidean
classifier is optimized by a standard cross-entropy loss
function, as ℓ = ℓ E (c E ). Similarly, we optimize the GiO model
using the confidence vector cG , predicted in its geometric
classifier with its own specific loss ℓ = ℓG (cG ) [see Fig. 3(b)].
The loss functions for the spherical and hyperbolic geometric
networks are described in (3) and (8).
The GiT model, as shown in Fig. 3(c), is trained in a
multitask learning manner by optimizing a Euclidean classifier
and a geometric classifier, as ℓ = ℓ E (c E )+ℓG (cG ). To be more
specific, a shared image encoder encodes the input image in
a Euclidean space M E and the curved spaces MG . Then,
the following Euclidean classifier and geometric classifier are
optimized separately. In contrast to the well-studied studentteacher models [48], [49], which aim to transfer the knowledge
from the teacher model to the student model, our GiT model
learns subbranches guided by its own spaces and objective
functions [see (3) and (8)].

HONG et al.: CURVED GEOMETRIC NETWORKS FOR VISUAL ANOMALY RECOGNITION

17927

TABLE II
V ISUAL A NOMALY TASKS W HERE W E E VALUATE THE P ROPOSED G EOMETRIC M ODELS

TABLE III
M ULTICLASS OOD D ETECTION ON CIFAR-10/CIFAR-100 [61] W ITH D ENSE N ET /WRN-28-10 I MAGE E NCODER . M IXED -G EOMETRY E MBEDDING IN
THE M I O/M I T M ODEL I NCLUDES S PHERICAL E MBEDDING AND H YPERBOLIC E MBEDDING . W E P ROVIDE AVERAGING R ESULTS OVER F IVE
M ULTIPLE OOD DATASETS : TIN C , TIN R , LSUN C , LSUN R , AND iSUN. “*” I NDICATES T HAT THE R ESULTS A RE O BTAINED VIA A
S ELF -I MPLEMENTED N ETWORK . T HE C URVATURES OF SiO, SiT, HiO, HiT, MiO, AND MiT A RE S ET TO 1.0, 1.0, −0.01, −1.0,
(1.0, −0.01), AND (1.0, −1.0), R ESPECTIVELY

TABLE IV
M ULTICLASS OOD D ETECTION ON CIFAR-10/CIFAR-100 [61] W ITH D ENSE N ET /WRN-28-10 I MAGE E NCODER . W E P ROVIDE AVERAGING R ESULTS
OVER F IVE M ULTIPLE OOD DATASETS : TIN C , TIN R , LSUN C , LSUNr, AND iSUN. “*” I NDICATES T HAT THE R ESULTS A RE O BTAINED VIA
S ELF -I MPLEMENTED N ETWORKS . T HE C URVATURE OF HiO I S S ET TO −0.01

TABLE V
M ULTICLASS OOD D ETECTION ON CIFAR-100 [61] W ITH D ENSE N ET [62] AND WRN-28-10 [63] I MAGE E NCODERS . M IXED -G EOMETRY E MBEDDING
IN THE M I T M ODEL C OMBINES A S PHERICAL E MBEDDING AND H YPERBOLIC E MBEDDING . W E P ROVIDE AVERAGING R ESULTS OVER F OUR
M ULTIPLE OOD DATASETS : TINc, TINr, LSUNc, AND LSUNr. T HE C URVATURES OF SiT, HiT, AND MiT A RE S ET TO 1.0, −0.001, AND
(1.0, −0.001), R ESPECTIVELY

V. E XPERIMENTS
In this section, we evaluate our models on four visual
anomaly, open-set, or OOD tasks: 1) multiclass OOD detection; 2) one-class anomaly detection; 3) multiclass anomaly
segmentation; and 4) one-class anomaly segmentation. Table II

shows the difference between each task used in this article.
For simplicity, we use the following abbreviations for our
models: spherical-in-one (SiO), SiT, HiO, HiT, MiO, and MiT.
It is notable that such terms (e.g., SiO and SiT) indicate that
the curved geometric models apply the geometric classifiers

17928

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 12, DECEMBER 2024

TABLE VI
O NE -C LASS A NOMALY D ETECTION ON CIFAR-10 [61]. I MAGE -L EVEL AUROC IN % I S G IVEN . classi I NDICATES THE i TH C LASS . “E XTRA” I NDICATES
U TILIZING E XTRA DATA FOR T RAINING ( E . G ., U SING P RETRAINED M ODELS ON I MAGE N ET [64]). “*” I NDICATES T HAT THE R ESULTS A RE
O BTAINED VIA A S ELF -I MPLEMENTED N ETWORK . M IXED -G EOMETRY E MBEDDING IN THE M I T M ODEL I NCORPORATES B OTH THE
S PHERICAL E MBEDDING AND H YPERBOLIC E MBEDDING . ROT N ET∗ , SiT, HiT, AND MiT A DOPT WRN-28-10 [63] AS I MAGE
E NCODER , W HILE CSI, SiT, HiT, AND MiT U TILIZE R ES N ET-18 [65]. T HE C URVATURES OF SiT, HiT, AND M I T BASED
ON ROT N ET ∗ A RE S ET TO 1.0, −0.005, AND (1.0, −0.005), R ESPECTIVELY. T HE C URVATURES OF SiT, HiT, AND MiT
BASED ON CSI A RE G IVEN AS 1.0, −0.01, AND (1.0, −0.01), R ESPECTIVELY

TABLE VII
M ULTICLASS A NOMALY S EGMENTATION ON S TREET H AZARDS [19].
FPR (95% TPR), P IXEL -L EVEL AUROC, AND AUPR IN % A RE
G IVEN . T HE M ETRIC S TD OVER F IVE RUNS . T HE R ESULTS
OF AE, D ROPOUT, AND MSP A RE P ROVIDED IN [19]. T HE
C URVATURES OF SiT, HiT, AND MiT BASED ON MSP A RE
S ET TO 1.0, −0.01, AND (1.0, −0.01), R ESPECTIVELY

compared to their corresponding baselines (see Table I for
more details). Metrics, including the false positive rate at
95% true positive rate (FPR at 95% TPR), the detection
error, the area under the receiver operating characteristics
(AUROC) [72], [73], and the area under the precision-recall
(AUPR) [74], [75], are measured. All results are averaged over
five independent trials.
For the experiments on multiclass OOD detection,
we train the geometric models for 300/300/100 epochs
using Hendrycks&Gimpel [15]/ODIN [16]/ELOC [35] as
the baselines, with a learning rate of 0.05/0.05/0.1. In the
experiments of one-class anomaly detection, the models based
on RotNet [36]/CSI [38] are trained for 100/1000 epochs with
learning rates of 0.01/0.1. For the multiclass segmentation
task, the models are trained for 30 epochs with a learning
rate of 0.02. In one-class anomaly segmentation, the models
are trained for 1200 epochs with a learning rate of 1e−4 . The
values of curvatures for the GiO/GiT models are provided in
the captions of Tables III–IX.

is trained on the ID dataset only. In this setting, CIFAR-10
and CIFAR-100 [61] are chosen as ID datasets, while the
cropped TinyImageNet (TINc), the resized TinyImageNet
(TINr) [64], the cropped LSUN (LSUNc), the resized LSUN
(LSUNr) [76], and iSUN [77] are OOD datasets. We first adopt
the Hendrycks&Gimpel model [15] as the baseline network.
Both Dense-BC [62] and WRN-28-10 [63] are used as image
encoders. As shown in Table III, we can observe that the
HiO model attains the overall best accuracy. In addition, our
models, except the SiO model, bring the performance gain over
the baselines, showing the superiority of curved geometries
as embedding spaces. It is also notable that our models are
light. For example, the HiT model surpasses the baseline by
4.2% with WRN-28-10 on CIFAR-100, while it only uses an
extra 0.02 M parameters, i.e., from 146.05 M to 146.07 M.
Moreover, in most cases, the performance of the mixedcurvature model, MiO or MiT, is in between that of hyperbolic
and spherical models. Besides the Hendrycks&Gimpel model,
we also use ODIN [16] as the baseline where we employ the
input preprocessing at the test phase. The results of geometric
models that adopt ODIN as the baseline are reported in
Table IV. From Table III, we identify HiO as the model,
which obtains the best performance. Hence, we choose and test
HiO for ODIN. Except for the experiment of WRN-28-10 on
CIFAR-100, we see that HiO boosts the performance against
the baseline.
In addition to Hendrycks&Gimpel and ODIN models,
we also incorporate the proposed geometric classifier into
advanced baselines. In this study, we employ the ELOC [35]
as the baseline network. As shown in Table V, the HiT
model performs the best over two image encoders. Specifically,
it surpasses the baseline by 0.77%/1.60% in AUROC under
Dense-BC/WRN-28-10. Similar to the results shown in
Table III, the performance of the MiT model is in between SiT
and HiT with Dense-BC on CIFAR-100, but it unexpectedly
becomes the worst with WRN-28-10.

A. Multiclass OOD Detection
The objective of multiclass OOD detection, traditionally
termed OOD detection, is to identify whether a sample is
from the given dataset with multiple ID classes. The model

B. One-Class Anomaly Detection
In the one-class anomaly (or open-set) detection setting,
only one class is set as the normal class, while other classes

HONG et al.: CURVED GEOMETRIC NETWORKS FOR VISUAL ANOMALY RECOGNITION

17929

TABLE VIII
O NE -C LASS A NOMALY S EGMENTATION (A NOMALY L OCALIZATION ) ON MVT EC AD [68]. P IXEL -L EVEL AUROC IN % I S G IVEN . “E XTRA” I NDICATES
U TILIZING E XTRA DATA FOR T RAINING ( E . G ., U SING P RETRAINED M ODELS ON I MAGE N ET [64]). “C PR ” I NDICATES U SING THE C OMPARISON
W ITH THE T RAINING DATA FOR A NOMALY S CORE C OMPUTATION D URING E VALUATION . T HE R ESULTS OF AVID AND A NO GAN/AE A RE
P ROVIDED IN [32] AND [49], R ESPECTIVELY. M IXED -G EOMETRY E MBEDDING IN THE MiO/MiT M ODEL I NCLUDES S PHERICAL
E MBEDDING AND H YPERBOLIC E MBEDDING . T HE C URVATURES OF SiO, HiO, MiO, SiT, HiT, AND MiT A RE S ET TO 1.0,
−0.01, (1.0, −0.01), 1.0, −1.0, AND (1.0, −1.0), R ESPECTIVELY. T HE M ODEL S IZES OF PATCH -SVDD† , SiO, HiO,
MiO, SiT, HiT, AND MiT A RE 1.72 M, 1.72 M, 1.72 M, 1.82 M, 1.82 M, 1.83 M, AND 1.93 M, R ESPECTIVELY

are used as abnormal classes. The common practice of
creating discriminative representations under this setting is
modeled as a multiclass classification problem using the selfsupervised learning (SSL) algorithms [36], [38], [38], [41],
[42], [43]. In this task, we evaluate our models on the oneclass CIFAR-10 dataset [61].
Our geometric classifier is built on RotNet [36] and
CSI [38]. RotNet predicts the rotation angles as supervision for
SSL. Following the setting in [36], we set the rotation angles
to 0◦ , 90◦ , 180◦ , and 270◦ . A 4-D classifier that predicts the
angle of rotation is applied to the input image. CSI adopts
the contrastive learning scheme, which contrasts the negative
samples coming from the data augmentation. The results are
shown in Table VI. We can observe that either of our models
can improve the baselines, showing that embedding in curved
spaces indeed benefits the discrimination of data embedding.
For example, in RotNet, the method with mixed-curvature
geometry, MiT, attains the best performance improvement,
e.g., 1.53%, and outperforms the SiT and HiT models.
It verifies that mixed-curvature geometry indeed benefits from
the advantages of both spherical geometry and hyperbolic
geometry. In CSI [38], as a strong baseline, our models again
bring a performance gain, and the MiT method achieves the
best average performance, revealing that our models generalize
and are effective.

C. Multiclass Anomaly Segmentation
In contrast to multiclass OOD detection, which recognizes
the OOD samples at the image level, multiclass anomaly
(or open-set) segmentation is required to predict anomalous
objects at the pixel level. Following [19] and [25],
we evaluate this task using the StreetHazards dataset [19].
The Hendrycks&Gimpel model [15] with maximum softmax
probability (MSP) is adopted as the baseline. We report the
results in Table VII. As suggested in Table VII, this task
also benefits the most from the mixed-curvature geometry
(MiT), again showing that multiple geometries are essential
to learning discriminative embeddings.

D. One-Class Anomaly Segmentation
One-class anomaly segmentation, also known as anomaly
localization, aims to identify whether the input pixel is
an anomalous pixel or not [33], [68]. In contrast to the
multiclass anomaly segmentation, the training samples in oneclass anomaly segmentation are drawn from only one class of
the dataset.
We verify the effectiveness of our models on the MVTecAD
dataset [68] and adopt the SOTA model Patch-SVDD [37]
as a baseline without using extra data. A possible limitation
of Patch-SVDD is that the computation of the anomaly
scores AS for inference depends to a great extent on the
comparison with training samples. To simplify the evaluation
process, we calculate the anomaly score directly from its
normalized classifier’s value without utilizing any training
data (denoted by Patch-SVDD† ). We then plug our geometric
models on top of Patch-SVDD† . The results are reported
in Table VIII. As suggested in Table VIII, all geometric
models, except the SiO model, boost the performance of
the baseline, and the mixed-curvature geometric model, MiT,
performs the best. It gains 17.55% improvement. In this task,
the dual-branch architecture (i.e., SiT/HiT/MiT) consistently
outperforms the single-branch model (i.e., SiO/HiO/MiO).
Along with a considerable improvement, our proposal is also
cheap. For example, the SiT improves the baseline by a margin
of 16.41%, while it only brings extra 0.1 M parameters, i.e.,
1.82 M versus 1.72 M, again showing the benefits from curved
geometric embeddings.
The idea of Patch-SVDD† is to evaluate our method on a
toy example to illustrate the advantage of curved geometries.
However, after we remove the comparison process with
training images from Patch-SVDD, we find its identification
performance significantly drops. To show the full potential
of our design in conjunction with the original Patch-SVDD,
we employ our geometric model over the original PatchSVDD where training images are considered for calculating
the anomaly score. As shown in Table IX, the accuracy
of Patch-SVDD on MVTecAD is boosted from 95.7% to
96.5%/96.5%/96.7% once using SiT/HiT/MiT. We follow

17930

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 12, DECEMBER 2024

TABLE IX
O NE -C LASS A NOMALY S EGMENTATION (A NOMALY L OCALIZATION ) ON MVT EC AD [68]. P IXEL -L EVEL AUROC IN % I S G IVEN . “E XTRA” I NDICATES
U TILIZING E XTRA DATA FOR T RAINING ( E . G ., U SING P RETRAINED M ODELS ON I MAGE N ET [64]). “C PR ” I NDICATES U SING THE C OMPARISON
W ITH THE T RAINING DATA FOR A NOMALY S CORE C OMPUTATION D URING E VALUATION . T HE R ESULTS OF LSA A RE P ROVIDED IN [32].
M IXED -G EOMETRY E MBEDDING IN THE MiT M ODEL I NCLUDES S PHERICAL E MBEDDING AND H YPERBOLIC E MBEDDING . T HE
C URVATURES OF SiT, HiT, AND MiT A RE S ET TO 1.0, −1.0, AND (1.0, −1.0), R ESPECTIVELY

TABLE X
M ULTICLASS A NOMALY S EGMENTATION ON MVT EC AD [68]. P IXEL -L EVEL AUROC IN % I S G IVEN . M IXED -G EOMETRY E MBEDDING
IN THE M I T M ODEL I NCLUDES S PHERICAL E MBEDDING AND H YPERBOLIC E MBEDDING . T HE C URVATURES OF SiT, HiT, AND MiT
A RE S ET TO 1.0, −1.0, AND (1.0, −1.0), R ESPECTIVELY

the anomaly score computation of the original Patch-SVDD
except for replacing the patch’s embedding with the geometric
score z E G .
As described in Section V-C, the multiclass setting allows
training data from multiple classes. We utilize this multiclass
data to train PatchSVDD† and the proposed geometric models
on the MVTecAD dataset [68]. Consistent with the approach
outlined in [79], we do not employ class label information. The
results, presented in Table X, demonstrate the clear superiority
of the geometric approaches over the baseline model.
E. Analysis
In this section, we aim to provide studies to analyze the
superiority of our design.
1) Performance: We learn from empirical observations
in Sections V-A–V-D that the curved spaces are able to
consistently provide reliable information for anomaly, openset, or OOD recognition. In most cases, our curvature-aware
geometric networks clearly outperform Euclidean networks.
One possible explanation is that the geometric representations
benefit particular problems. For example, as we discussed
in Section I, hyperbolic geometry is good at encoding
hierarchical structures inside the data. The datasets we test
include hierarchical information to some extent. For instance,
the CIFAR dataset includes ten superclasses and ten subclasses
under each superclass. The 15 classes of MVTecAD can
be categorized into two main supercategories, “object” and
“texture.” Hence, the hyperbolic space takes effect.
2) Mixed Geometry: Another interesting fact has been
observed is that the mixed-curvature geometry beats its
component single-curvature geometries in several cases:
MiT based on RotNet∗ /CSI of one-class anomaly detection,
MiT based on MSP of multiclass anomaly segmentation,
and MiT based on Patch-SVDD† of one-class anomaly
segmentation in Tables VI–VIII, respectively. In some cases,

TABLE XI
A BLATION S TUDY: M ULTICLASS OOD D ETECTION . I MAGE -L EVEL
AUROC IN % I S G IVEN . D IFFERENT C ASES A RE E VALUATED
ON CIFAR-10 [61] TO V ERIFY THE I NTERACTIONS B ETWEEN
H YPERBOLIC OR S PHERICAL AND E UCLIDEAN S PACES

the mixed-curvature geometry has a balanced performance.
For example, in the task of multiclass OOD detection, there
exists a significant performance gap between hyperbolic and
spherical geometries, as evidenced by SiO versus HiO. Thus,
the mixed space MiO might be expected to have an average
performance.
3) Interactions Among Geometries: The GiT model
requires meanwhile learning two embeddings (e.g.,
a Euclidean e E , and a hyperbolic e H or spherical
embedding e S ). We observe that it happens in the interactions
between different geometric components. For instance,
in multiclass OOD detection (see Table III), e E could enrich
e S (SiO versus SiT); however, for e H , it has less or even
negative impact (HiO versus HiT). To further understand the
influence, we analyzed the experiments of WRN-28-10 on
CIFAR-10 where we separately test e E and e H (or e S ) in
HiT (or SiT). Results in Table XI suggest the aforementioned
point (HiO versus e H in HiT and SiO versus e S in SiT).
4) Curvature: The curvature κ is the only hyperparameter
in the proposed curvature-aware geometric networks. The
study of one-class anomaly segmentation of HiT based on
Patch-SVDD† in Table XII suggests that κ clearly has an
impact on anomaly recognition performance. Table XII shows
that for each category, there exists an optimal curvature value κ
that leads to the best performance. Deviating from this optimal
value results in a decrease in performance.

HONG et al.: CURVED GEOMETRIC NETWORKS FOR VISUAL ANOMALY RECOGNITION

17931

Fig. 5. Visualization: multiclass OOD detection. Density distributions of max(c E ), tanh(z S ), tanh(z E S ), tanh(z H ), and tanh(z E H ) of Hendrycks&Gimpel,
SiO, SiT, HiO, and HiT models with Dense-BC on CIFAR10→TINc are provided. The obtained AUROC for these five models are 94.8%, 94.7%, 98.1%,
98.7%, and 96.0%. More corresponding results can be referred to in Table III.

TABLE XII
A BLATION S TUDY: O NE -C LASS A NOMALY S EGMENTATION (A NOMALY
L OCALIZATION ). P IXEL -L EVEL AUROC IN % I S G IVEN . D IFFERENT
F IXED C URVATURES ON MVT EC AD [68] A RE E VALUATED . F OR
E ACH C ATEGORY, D IFFERENT C URVATURES B RING A BOUT
D IFFERENT P ERFORMANCES . A LSO , THE O PTIMAL C URVA TURE C HOICE I S N OT C ONSISTENT A MONG
D IFFERENT C ATEGORIES

Fig. 6. Visualization: one-class anomaly detection. Density distribution of
anomaly score AS(z E H ) of HiT based on RotNet∗ on CIFAR-10 [61] is
visualized. We choose cases where class1 , class5 , or class9 is taken as the
normal class. The distribution of one case is shown in one column. More
corresponding results can be referred to in Table VI.

5) Method Choice: Our comprehensive empirical study
suggests that a single definitive conclusion cannot be made.
This is in line with observations made in recent works. For
example, in [14], the best geometry choice depends on the task.
Our study clearly shows that curved geometry is beneficial
in capturing the geometry of data, contributing tangibly to
identifying anomalies in data. Specifically, our empirical study
suggests that the preferred model for each task is shown
as follows—multiclass OOD detection: HiO/HiT; multiclass
anomaly segmentation: MiT; one-class anomaly detection:
MiT; and one-class anomaly segmentation: MiT. If one model
should be chosen in all instances, then we will opt for MiT as
the potential model for the visual anomaly recognition tasks.

Fig. 7. Visualization: one-class anomaly detection. Examples with anomaly
scores AS computed by RotNet∗ , HiT, and MiT are provided (see the top).
In addition, AUROC curves along the training epoch are plotted in the
bottom.

F. Visualization
In this section, we qualitatively study our method in imagelevel classification task and pixel-level segmentation task,
to understand why our method can bring performance gain
over the baseline model.
1) Image-Level Classification: In this work, we particularly
study whether the geometric score z G and z E G from the curved

embedding spaces can provide more useful information than
the confidence vector c E from the Euclidean space in distinguishing normal (or closed-set/ID) and abnormal (or openset/OOD) objects. We visualize the distribution of max(c E ),
tanh(z S ), tanh(z E S ), tanh(z H ), and tanh(z E H ) on multiclass

17932

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 12, DECEMBER 2024

VI. C ONCLUSION

Fig. 8. Visualization: one-class anomaly segmentation (anomaly localization).
The heatmaps of anomaly score AS(c E ), AS(z E S ), AS(z E H ), and AS(z E M )
of Patch-SVDD† , SiT, HiT, and MiT on MVTecAD [68] are visualized.
We provide examples from “bottle,” “metal nut,” “tile,” and “grid.” More
corresponding results can be found in Table VIII. In addition, for the category
“bottle,” AUROC curves of different models along the training epoch are
plotted in the bottom.

OOD detection over CIFAR-10 (CIFAR10→TINc) in Fig. 5.
As shown in Fig. 5, the curved embedding spaces help to
better separate ID and OOD distributions. The distribution of
anomaly score AS(z E H ) of one-class anomaly detection on
one-class CIFAR-10 is visualized in Fig. 6. The visualization
shows that z E H provides reliable information for distinguishing the normal one-class and the abnormal classes. We present
some examples in Fig. 7 to verify the performance differences
among models, where we compare RotNet∗ /HiT/MiT on
Class 2 as a normal class. The anomaly scores AS in
the top figure show different models that have different
capacities to recognize abnormal classes. Also, the AUROC
curve suggests substantial improvements led by the curved
geometries.
2) Pixel-Level Segmentation: From experiments, we find
that besides image-level tasks, curved spaces as embedding
spaces do help in pixel-level anomaly tasks. In Fig. 8,
we show examples in which we visualize the anomaly score
AS of Patch-SVDD† , SiT, HiT, and MiT on MVTecAD [68].
As shown in Fig. 8, z E G from MG outperforms c E from M E
in identifying anomalous pixels.

In this article, we study the potential use and benefit of
employing curved spaces for the purpose of visual anomaly,
open-set, or OOD recognition tasks. Our idea is inspired by
the observation that curved embedding spaces help better
represent “unknown” data in low-shot problems. Our work
proposes two novel geometric networks, GiO and GiT,
for the visual anomaly data analysis. In each geometric
model, we fully study the potential of different geometry
constraints. To the best of our knowledge, our curvatureaware geometric networks are the first attempt to employ
curved geometries in visual anomaly, open-set, or OOD
recognition. Based on extensive experiments, we confirm
that more distinct representations between normal (or closedset/ID) and anomalous (or open-set/OOD) samples can be
learned using curved spaces, clearly showing the benefits
of the curved spaces. We hope that this work can inspire
researchers to explore curved geometries further in other
domains.
While the proposed geometric modules successfully
enhance performance, their applicability is currently limited
to baselines employing the “encoder–classifier” structure.
Furthermore, the fixed curvature of these designs does
not guarantee the optimal performance. To address these
limitations, future research could explore the integration
of curved embeddings into generative-based models with
“encoder–decoder” structures. In addition, efforts can be
directed toward developing adaptive-curvature designs to
achieve the optimal performance.
R EFERENCES
[1] M. Nickel and D. Kiela, “Poincaré embeddings for learning hierarchical
representations,” in Proc. Adv. Neural Inf. Process. Syst., vol. 30, 2017,
pp. 6338–6347.
[2] A. Tifrea, G. Bécigneul, and O.-E. Ganea, “Poincaré GloVe: Hyperbolic
word embeddings,” 2018, arXiv:1810.06546.
[3] B. Dhingra, C. J. Shallue, M. Norouzi, A. M. Dai, and G. E. Dahl,
“Embedding text in hyperbolic spaces,” 2018, arXiv:1806.04313.
[4] V. Khrulkov, L. Mirvakhabova, E. Ustinova, I. Oseledets, and V.
Lempitsky, “Hyperbolic image embeddings,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2020, pp. 6418–6428.
[5] J. Park, J. Cho, H. J. Chang, and J. Young Choi, “Unsupervised
hyperbolic representation learning via message passing auto-encoders,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2021, pp. 5516–5526.
[6] Y. Zhang, L. Luo, W. Xian, and H. Huang, “Learning better visual
data similarities via new grouplet non-Euclidean embedding,” in Proc.
IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021, pp. 9918–9927.
[7] W. Liu, Y. Wen, Z. Yu, M. Li, B. Raj, and L. Song, “SphereFace:
Deep hypersphere embedding for face recognition,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jul. 2017, pp. 212–220.
[8] X. Fan, W. Jiang, H. Luo, and M. Fei, “SphereReID: Deep hypersphere
manifold embedding for person re-identification,” J. Vis. Commun. Image
Represent., vol. 60, pp. 51–58, Apr. 2019.
[9] S. Ravi and H. Larochelle, “Optimization as a model for few-shot
learning,” in Proc. Int. Conf. Learn. Represent. (ICLR), 2017, pp. 1–11.
[10] L. Van der Maaten and G. Hinton, “Visualizing data using t-SNE,”
J. Mach. Learn. Res., vol. 9, no. 11, pp. 2579–2605, 2008.
[11] S. Liu, J. Chen, L. Pan, C.-W. Ngo, T.-S. Chua, and Y.-G. Jiang,
“Hyperbolic visual embedding learning for zero-shot recognition,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), 2020,
pp. 9273–9281.
[12] J. Shen, Z. Xiao, X. Zhen, and L. Zhang, “Spherical zero-shot learning,”
IEEE Trans. Circuits Syst. Video Technol., vol. 32, no. 2, pp. 634–645,
Feb. 2022.

HONG et al.: CURVED GEOMETRIC NETWORKS FOR VISUAL ANOMALY RECOGNITION

[13] P. Fang, M. Harandi, and L. Petersson, “Kernel methods in hyperbolic
spaces,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021,
pp. 10665–10674.
[14] O. Skopek, O.-E. Ganea, and G. Bécigneul, “Mixed-curvature variational
autoencoders,” in Proc. ICLR, 2020, pp. 1–44.
[15] D. Hendrycks and K. Gimpel, “A baseline for detecting misclassified
and out-of-distribution examples in neural networks,” in Proc. ICLR,
2017, pp. 1–12.
[16] S. Liang, Y. Li, and R. Srikant, “Enhancing the reliability of out-ofdistribution image detection in neural networks,” in Proc. ICLR, 2018,
pp. 1–27.
[17] T. DeVries and G. W. Taylor, “Learning confidence for out-ofdistribution detection in neural networks,” 2018, arXiv:1802.04865.
[18] C. Corbière, N. Thome, A. Bar-Hen, M. Cord, and P. Pèrez, “Addressing
failure prediction by learning model confidence,” in Proc. NeurIPS,
2019, pp. 1–12.
[19] D. Hendrycks et al., “Scaling out-of-distribution detection for realworld settings,” in Proc. 39th Int. Conf. Mach. Learn. (ICML), 2022,
pp. 8759–8773.
[20] Y.-C. Hsu, Y. Shen, H. Jin, and Z. Kira, “Generalized ODIN: Detecting
out-of-distribution image without learning from out-of-distribution data,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2020, pp. 10951–10960.
[21] J. Jang and C. O. Kim, “Collective decision of one-vs-rest networks
for open-set recognition,” IEEE Trans. Neural Netw. Learn. Syst., early
access, Jul. 14, 2022, doi: 10.1109/TNNLS.2022.3189996.
[22] K. Lee, H. Lee, K. Lee, and J. Shin, “Training confidence-calibrated
classifiers for detecting out-of-distribution samples,” in Proc. ICLR,
2018, pp. 1–16.
[23] M. Sabokrou et al., “AVID: Adversarial visual irregularity detection,”
in Proc. Asian Conf. Comput. Vis. Cham, Switzerland: Springer, 2018,
pp. 488–505.
[24] K. Lis, K. K. Nakka, P. Fua, and M. Salzmann, “Detecting the
unexpected via image resynthesis,” in Proc. IEEE/CVF Int. Conf.
Comput. Vis. (ICCV), Oct. 2019, pp. 2152–2161.
[25] Y. Xia, Y. Zhang, F. Liu, W. Shen, and A. L. Yuille, “Synthesize then
compare: Detecting failures and anomalies for semantic segmentation,”
in Proc. Eur. Conf. Comput. Vis. Cham, Switzerland: Springer, 2020,
pp. 145–161.
[26] S. Kong and D. Ramanan, “OpenGAN: Open-set recognition via open
data generation,” in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV),
Oct. 2021, pp. 813–822.
[27] J. Ren et al., “Likelihood ratios for out-of-distribution detection,” in
Proc. NeurIPS, 2019, pp. 1–12.
[28] D. Abati, A. Porrello, S. Calderara, and R. Cucchiara, “Latent space
autoregression for novelty detection,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit. (CVPR), Jun. 2019, pp. 481–490.
[29] P. Perera, R. Nallapati, and B. Xiang, “OCGAN: One-class novelty
detection using GANs with constrained latent representations,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2019,
pp. 2898–2906.
[30] D. Gong et al., “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2019,
pp. 1705–1714.
[31] F. V. Massoli, F. Falchi, A. Kantarci, S. Akti, H. K. Ekenel, and
G. Amato, “MOCCA: Multilayer one-class classification for anomaly
detection,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 6,
pp. 2313–2323, Jun. 2022.
[32] S. Venkataramanan, K.-C. Peng, R. V. Singh, and A. Mahalanobis,
“Attention guided anomaly localization in images,” in Proc. Eur. Conf.
Comput. Vis. Cham, Switzerland: Springer, 2020, pp. 485–503.
[33] W. Liu et al., “Towards visually explaining variational autoencoders,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2020, pp. 8642–8651.
[34] K. Zhou et al., “Memorizing structure-texture correspondence for image
anomaly detection,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33,
no. 6, pp. 2335–2349, Jun. 2022.
[35] A. Vyas, N. Jammalamadaka, X. Zhu, D. Das, B. Kaul, and T. L. Willke,
“Out-of-distribution detection using an ensemble of self supervised
leave-out classifiers,” in Proc. Eur. Conf. Comput. Vis. (ECCV), 2018,
pp. 550–564.
[36] S. Gidaris, P. Singh, and N. Komodakis, “Unsupervised representation
learning by predicting image rotations,” in Proc. ICLR, 2018, pp. 1–14.

17933

[37] J. Yi and S. Yoon, “Patch SVDD: Patch-level SVDD for anomaly
detection and segmentation,” in Proc. Asian Conf. Comput. Vis., 2020,
pp. 1–16.
[38] J. Tack, S. Mo, J. Jeong, and J. Shin, “CSI: Novelty detection via
contrastive learning on distributionally shifted instances,” in Proc.
NeurIPS, 2020, pp. 1–14.
[39] J. Zheng, W. Li, J. Hong, L. Petersson, and N. Barnes, “Towards openset object detection and discovery,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit. Workshops (CVPRW), Jun. 2022, pp. 3960–3969.
[40] J. Hong et al., “GOSS: Towards generalized open-set semantic
segmentation,” 2022, arXiv:2203.12116.
[41] L. Ruff et al., “Deep one-class classification,” in Proc. Int. Conf. Mach.
Learn., 2018, pp. 4393–4402.
[42] I. Golan and R. El-Yaniv, “Deep anomaly detection using geometric
transformations,” in Proc. NeurIPS, 2018, pp. 1–12.
[43] D. Hendrycks, M. Mazeika, S. Kadavath, and D. Song, “Using selfsupervised learning can improve model robustness and uncertainty,” in
Proc. NeurIPS, 2019, pp. 1–13.
[44] L. Bergman and Y. Hoshen, “Classification-based anomaly detection for
general data,” in Proc. ICLR, 2020, pp. 1–12.
[45] C.-L. Li, K. Sohn, J. Yoon, and T. Pfister, “CutPaste: Selfsupervised learning for anomaly detection and localization,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 9659–9669.
[46] Y. Liu, Z. Li, S. Pan, C. Gong, C. Zhou, and G. Karypis,
“Anomaly detection on attributed networks via contrastive selfsupervised learning,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33,
no. 6, pp. 2378–2392, Jun. 2022.
[47] Q. Yu and K. Aizawa, “Unsupervised out-of-distribution detection by
maximum classifier discrepancy,” in Proc. IEEE/CVF Int. Conf. Comput.
Vis. (ICCV), Oct. 2019, pp. 9517–9525.
[48] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “Uninformed
students: Student-teacher anomaly detection with discriminative latent
embeddings,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2020, pp. 4182–4191.
[49] M. Salehi, N. Sadjadi, S. Baselizadeh, M. H. Rohban, and H. R. Rabiee,
“Multiresolution knowledge distillation for anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 14897–14907.
[50] S. Wang, L. Wu, L. Cui, and Y. Shen, “Glancing at the patch:
Anomaly localization with global and local feature comparison,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 254–263.
[51] M. M. Bronstein, J. Bruna, Y. LeCun, A. Szlam, and P. Vandergheynst,
“Geometric deep learning: Going beyond Euclidean data,” IEEE Signal
Process. Mag., vol. 34, no. 4, pp. 18–42, Jul. 2017.
[52] M. Zaheer et al., “Deep sets,” in Proc. NeurIPS, 2017, pp. 1–11.
[53] P. Fang, P. Ji, L. Petersson, and M. Harandi, “Set augmented triplet
loss for video person re-identification,” in Proc. WACV, Jan. 2021,
pp. 464–473.
[54] A. Cheraghian et al., “Synthesized feature based few-shot classincremental learning on a mixture of subspaces,” in Proc. ICCV,
Oct. 2021, pp. 8661–8670.
[55] C. Simon, P. Koniusz, R. Nock, and M. Harandi, “Adaptive subspaces
for few-shot learning,” in Proc. CVPR, Jun. 2020, pp. 1–10.
[56] A. M. Bronstein, M. M. Bronstein, and R. Kimmel, “Expressioninvariant face recognition via spherical embedding,” in Proc. IEEE Int.
Conf. Image Process., vol. 3, Sep. 2005, p. 756.
[57] W. Liu et al., “Deep hyperspherical learning,” 2017, arXiv:1711.03189.
[58] R. Ma, P. Fang, T. Drummond, and M. Harandi, “Adaptive poincaré
point to set distance for few-shot classification,” in Proc. AAAI Conf.
Artif. Intell., vol. 36, no. 2, 2022, pp. 1926–1934.
[59] S. Jayasumana, S. Ramalingam, and S. Kumar, “Model-efficient deep
learning with kernelized classification,” in Proc. ICLR, 2022, pp. 1–18.
[Online]. Available: https://openreview.net/forum?id=30SXt3-vvnM
[60] A. Gu, F. Sala, B. Gunel, and C. Ré, “Learning mixed-curvature
representations in product spaces,” in Proc. ICLR, 2019, pp. 1–21.
[61] A. Krizhevsky et al., “Learning multiple layers of features from tiny
images,” Univ. Toronto, Toronto, ON, Canada, Tech. Rep., 2009.
[62] G. Huang, Z. Liu, L. Van Der Maaten, and K. Q. Weinberger, “Densely
connected convolutional networks,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit. (CVPR), Jul. 2017, pp. 2261–2269.
[63] S. Zagoruyko and N. Komodakis, “Wide residual networks,” 2016,
arXiv:1605.07146.

17934

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 35, NO. 12, DECEMBER 2024

[64] J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and L. Fei-Fei, “ImageNet:
A large-scale hierarchical image database,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit., Jun. 2009, pp. 248–255.
[65] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 770–778.
[66] C. Baur, B. Wiestler, S. Albarqouni, and N. Navab, “Deep autoencoding
models for unsupervised anomaly segmentation in brain MR images,” in
Proc. Int. MICCAI Brainlesion Workshop. Cham, Switzerland: Springer,
2018, pp. 161–169.
[67] Y. Gal and Z. Ghahramani, “Dropout as a Bayesian approximation:
Representing model uncertainty in deep learning,” in Proc. Int. Conf.
Mach. Learn., 2016, pp. 1050–1059.
[68] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec AD—A
comprehensive real-world dataset for unsupervised anomaly detection,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR),
Jun. 2019, pp. 9584–9592.
[69] T. Schlegl et al., “Unsupervised anomaly detection with generative
adversarial networks to guide marker discovery,” in Proc. Int. Conf. Inf.
Process. Med. Imag. Cham, Switzerland: Springer, 2017, pp. 146–157.
[70] P. Bergmann, S. Löwe, M. Fauser, D. Sattlegger, and C. Steger,
“Improving unsupervised defect segmentation by applying structural
similarity to autoencoders,” 2018, arXiv:1807.02011.
[71] D. Dehaene, O. Frigo, S. Combrexelle, and P. Eline, “Iterative energybased projection on a normal data manifold for anomaly localization,”
in Proc. ICLR, 2020, pp. 1–17.
[72] J. Davis and M. Goadrich, “The relationship between precision-recall
and ROC curves,” in Proc. 23rd Int. Conf. Mach. Learn. (ICML), 2006,
pp. 233–240.
[73] T. Fawcett, “An introduction to ROC analysis,” Pattern Recognit. Lett.,
vol. 27, no. 8, pp. 861–874, Jun. 2006.
[74] C. Manning and H. Schutze, Foundations of Statistical Natural
Language Processing. Cambridge, MA, USA: MIT Press, 1999.
[75] T. Saito and M. Rehmsmeier, “The precision-recall plot is more
informative than the ROC plot when evaluating binary classifiers
on imbalanced datasets,” PLoS ONE, vol. 10, no. 3, Mar. 2015,
Art. no. e0118432.
[76] F. Yu, A. Seff, Y. Zhang, S. Song, T. Funkhouser, and J. Xiao, “LSUN:
Construction of a large-scale image dataset using deep learning with
humans in the loop,” 2015, arXiv:1506.03365.
[77] P. Xu, K. A. Ehinger, Y. Zhang, A. Finkelstein, S. R. Kulkarni, and
J. Xiao, “TurkerGaze: Crowdsourcing saliency with webcam based eye
tracking,” 2015, arXiv:1504.06755.
[78] T. Reiss, N. Cohen, L. Bergman, and Y. Hoshen, “PANDA: Adapting
pretrained features for anomaly detection and segmentation,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit. (CVPR), Jun. 2021,
pp. 2805–2813.
[79] Z. You et al., “A unified model for multi-class anomaly detection,” in
Proc. Adv. Neural Inf. Process. Syst., 2022, pp. 1–14.

Jie Hong received the M.Eng. degree from the
School of Electrical and Electronic Engineering, Nanyang Technological University (NTU),
Singapore, in 2017. He is currently pursuing the
Ph.D. degree with the College of Engineering,
Computing and Cybernetics, Australian National
University (ANU), Canberra, ACT, Australia, and
DATA61-CSIRO, Canberra.
His research interests include computer vision,
deep learning, robotics, and control systems.

Pengfei Fang received the M.E. degree from
Australian National University (ANU), Canberra,
ACT, Australia, in 2017, and the Ph.D. degree from
ANU and DATA61-CSIRO, Canberra, in 2022.
He was a Post-Doctoral Fellow at Monash
University, Clayton, VIC, Australia, in 2022. He is
currently an Associate Professor with the School
of Computer Science and Engineering, Southeast
University (SEU), Nanjing, China.
His research interests include computer vision and
machine learning.
Weihao Li received the Ph.D. degree in computer
science from Heidelberg University, Heidelberg,
Germany, in 2019, under the supervision of
Prof. Dr. Carsten Rother.
He is currently a Research Fellow at Australian
National University (ANU), Canberra, ACT,
Australia. Before joining ANU in 2022, he was a
Post-Doctoral Research Fellow at Data61-CSIRO,
Canberra, from 2019 to 2022. His research interests
include computer vision and machine learning.

Junlin Han received the Bachelor of Information
Technology degree (Hons.) from Australian National
University (ANU), Canberra, ACT, Australia,
in 2023.
His academic pursuits focus on computer vision,
deep learning, and artificial intelligence, with a
specific emphasis on leveraging data-centric methodologies to attain human-like visual intelligence.
Mr. Han actively participates as a reviewer for
esteemed conferences. He was honored as a top
reviewer in Conference on Neural Information
Processing Systems (NeurIPS) 2022.
Lars Petersson is currently the Group Leader and
a Principal Research Scientist with the Imaging and
Computer Vision Group, Data61-CSIRO, Canberra,
ACT, Australia. He is also leading one of the
activities under CSIRO’s Machine Learning and
Artificial Intelligence Future Science Platform effort
where data science problems from the smallest of
microscopy scales to the largest of astronomical
scales are addressed. Previous to joining Data61CSIRO, he was a Principal Researcher and the
Research Leader of the Computer Vision Research
Group, NICTA, Canberra, where he was leading projects, such as smart cars,
AutoMap, and distributed large-scale vision.
Mehrtash Harandi is currently an Associate Professor with the Department of Electrical and Computer
Systems Engineering, Monash University, Clayton,
VIC, Australia. He is also a contributing Research
Scientist with the Machine Learning Research Group
(MLRG), Data61-CSIRO, Canberra, ACT, Australia,
and an Associate Investigator with the Australian
Center for Robotic Vision (ACRV), Brisbane, QLD,
Australia. His current research interests include
theoretical and computational methods in machine
learning, computer vision, signal processing, and
Riemannian geometry.
PAPER_TEXT
