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
# [303] SLA2P: Self-Supervised Anomaly Detection With Adversarial Perturbation
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
编号：303
题名：SLA2P: Self-Supervised Anomaly Detection With Adversarial Perturbation
年份：2024
DOI：10.1109/tkde.2024.3448473
来源：IEEE Transactions on Knowledge and Data Engineering
PDF：paper/10.1109_TKDE.2024.3448473.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测
相关性：弱相关，分数 3
已有代码状态：已下载；SLA2P -> source\SLA2P

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\303.txt
- 原始字符数：62400
- 本次发送字符数：62400
- 是否截断：False

代码包：
- 仓库：SLA2P
  - URL：https://github.com/wyzjack/SLA2P
  - 状态：downloaded
  - 本地目录：source\SLA2P
  - 顶层结构：.gitignore、LICENSE.md、README.md、data/、data_loader.py、env.yaml、eval_accuracy.py、evaluate_pr_auc.py、evaluate_roc_auc.py、extract_BERT_embedding_20news.py、extract_BERT_embedding_arrhythmia.py、extract_GPT3_embedding_20news.py、extract_GPT3_embedding_arrhythmia.py、images/、keras2pytorch_dataset.py、misc.py、models/、outlier_datasets.py、reproduce.py、sla.py、sla2p.py、utils.py
  - 主要语言：Python:17、YAML:1
  - README 标题：SLA²P: Self-supervised Anomaly Detection with Adversarial Perturbation (TKDE 2024).、Short version: Self-supervision Meets Adversarial Perturbation: A Novel Framework for Anomaly Detect、Abstract、Usage、Environment setup、Prepare data、Run the experiments、CIFAR-10、CIFAR-100、Caltech 101
  - README 运行线索：bash conda env create -f env.yaml；bash python extract_bert_embeddings_20news.py；bash python extract_bert_embeddings_arrhythmia.py；bash python extract_GPT3_embedding_20news.py；python extract_GPT3_embedding_arrhythmia.py；bash # CIFAR-10；python sla2p.py --dataset cifar10 --n_rots 256 --d_out 256 --acc_thres 0.6 --epsilon 1000；python sla2p.py --dataset cifar100 --n_rots 256 --d_out 256 --acc_thres 0.6 --epsilon 10000
  - 关键文件：{"依赖环境": ["env.yaml"], "数据处理入口": ["extract_BERT_embedding_20news.py", "extract_BERT_embedding_arrhythmia.py", "extract_GPT3_embedding_20news.py", "extract_GPT3_embedding_arrhythmia.py"], "评估/测试入口": ["evaluate_pr_auc.py", "evaluate_roc_auc.py", "eval_accuracy.py"]}
  - 数据集线索：KDD、Tor、cert、kdd、nsl、tor

论文正文包开始：
<<<PAPER_TEXT
9282

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 12, DECEMBER 2024

SLA2P: Self-Supervised Anomaly Detection With
Adversarial Perturbation
Yizhou Wang , Member, IEEE, Can Qin , Rongzhe Wei , Yi Xu, Graduate Student Member, IEEE, Yue Bai ,
and Yun Fu , Fellow, IEEE

Abstract—Anomaly detection is a foundational yet difficult problem in machine learning. In this work, we propose a new and
effective framework, dubbed as SLA2 P, for unsupervised anomaly
detection. Following the extraction of delegate embeddings from
raw data, we implement random projections on the features and
consider features transformed by disparate projections as being
associated with separate pseudo-classes. We then train a neural
network for classification on these transformed features to conduct
self-supervised learning. Subsequently, we introduce adversarial
disturbances to the modified attributes, and we develop anomaly
scores built on the classifier’s predictive uncertainties concerning
these disrupted features. Our approach is motivated by the fact that
as anomalies are relatively rare and decentralized, 1) the training
of the pseudo-label classifier concentrates more on acquiring the
semantic knowledge of regular data instead of anomalous data; 2)
the altered attributes of the normal data exhibit greater resilience to
disturbances compared to those of the anomalous data. Therefore,
the disrupted modified attributes of anomalies can not be well
classified and correspondingly tend to attain lesser anomaly scores.
The results of experiments on various benchmark datasets for
images, text, and inherently tabular data demonstrate that SLA2 P
achieves state-of-the-art performance consistently.
Index Terms—Data mining- anomaly detection, machine
learning- deep learning, representation learning.

I. INTRODUCTION
NOMALIES, also known as outliers, are characterized as
“data instances that significantly deviate from the majority
of data instances” [1]. Correspondingly, anomaly detection (AD)
involves identifying anomalous data points using a data-driven
approach. This has been a crucial problem in machine learning
for a long time and has numerous real-world applications, such

A

Received 24 April 2023; revised 30 May 2024; accepted 6 August 2024. Date
of publication 23 August 2024; date of current version 13 November 2024.
This work was supported by the Air Force Office of Scientific Research under
Grant FA9550-23-1-0290. Recommended for acceptance by M.A. Cheema.
(Corresponding author: Yizhou Wang.)
Yizhou Wang, Can Qin, Yi Xu, and Yue Bai are with the Department of
Electrical and Computer Engineering, Northeastern University, Boston, MA
02115 USA (e-mail: wyzjack990122@gmail.com; qin.ca@northeastern.edu;
xu.yi@northeastern.edu; bai.yue@northeastern.edu).
Rongzhe Wei is with the Georgia Institute of Technology, Atlanta, GA 30332
USA (e-mail: rwei42@gatech.edu).
Yun Fu is with the Department of Electrical and Computer Engineering,
Khoury College of Computer Science, Northeastern University, Boston, MA
02115 USA (e-mail: yunfu@ece.neu.edu).
The code is available at: https://github.com/wyzjack/SLA2P.
This article has supplementary downloadable material available at
https://doi.org/10.1109/TKDE.2024.3448473, provided by the authors.
Digital Object Identifier 10.1109/TKDE.2024.3448473

as medical health [2], [3], fraud detection [4], [5], [6], cybersecurity [7], [8] and video surveillance [9], [10], etc.
Tasks for anomaly detection is able to be broadly categorized
into three groups based on the availability of labels and their
degree, as follows: 1) Supervised anomaly detection involves
training models on a labeled dataset which is composed of both
normal and abnormal data and then utilizing them to detect
anomalies in test data. 2) Semi-supervised anomaly detection
(SSAD), or one-class classification, deals with the setting that
the training dataset is only composed of normal data and the
trained model is expected to detect outliers during the testing
time. 3) Unsupervised anomaly detection (UAD), which is the
most common and challenging case, complies with the condition
that only unmarked data containing both typical and atypical
instances are supplied, and the anomaly detection approach is
required to be able to detect the outliers [11]. These three categories of tasks consider anomalies as data that belong to classes
that are intrinsically distinct from the classes of the normal data.
Besides, there exists another type of related but quite different
detection task called out-of-distribution (OOD) detection [12],
[13], [14], [15], which aims to distinguish samples that have
a disjoint distribution from the training samples in the testing
phase (usually from a different dataset).
We primarily concentrate on the unsupervised setting, i.e.,
UAD, which has the broadest applicability due to the fact that
obtaining labels is expensive for anomaly detection in a many
real-world scenarios [1], [16], [17]. UAD has a diverse range
of applications in practice, including construction of largescale dataset, website management, news management, etc. We
must clarify that in some literature, the so-called “unsupervised
anomaly detection” actually refers to SSAD (e.g., [18], [19],
[20]) or OOD (e.g., [21]) by our definition, which is beyond the
scope of this paper.
In this study, we present a novel SeLf-supervised outline
for unsupervised Anomaly Detection employing Adversarial
Perturbation, which we refer to as SLA2 P. Utilizing the obtained
representations from the unmarked original data, we project
them into distinct subspaces through multiplicating random
matrices. Despite having no explicit idea of the subspaces, we
deem the transformation to be digging various unknown aspects
of latent information of the data. Subsequently, we train a deep
neural network (DNN) classifier upon the transformed features
to identify which specific subspace they are projected into. The
training procedure of the classifier network is equipped with
an early stopping technique to refrain from overfitting, and

1041-4347 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

WANG et al.: SLA2 P: SELF-SUPERVISED ANOMALY DETECTION WITH ADVERSARIAL PERTURBATION

the reason behind this is that outliers fail to be trained well
owing to their smaller population size and more diverse modes.
The trained classifier is expected to primarily acquire beneficial
information concerning characteristics of the normal data and
consistently make inaccurate predictions on anomaly data. For
normal data, the early stopping mechanism, with a threshold
between 0 and 1, allows for a mix of accurate and inaccurate
predictions due to the higher volume of normal samples. Hence
the predictive uncertainties can be employed to create anomaly
scores, where anomalies exhibit more consistent predictions,
while normal instances display more distinct predictions. The
differences in prediction distributions can be intensified by
incorporating adversarial perturbations to the transformed features. The aim of the perturbations is to decrease the softmax
values corresponding to the anticipated labels of the transformed
features by the classifier, which are empirically shown to boost
detection performance. To summarize, our contributions are
three-fold:
r We introduce an innovative framework SLA2 P for UAD,
which can be applied to the image, text, and inherently
tabular datasets. Our approach is the first attempt to use
feature-level transformation to create a pretext classification task as surrogate supervision for the Unsupervised
Anomaly Detection task.
r We investigate UAD task by involving adversarial perturbation in a self-supervised fashion to achieve considerable
performance improvement. We are not aware of any other
analogous approach in the anomaly detection field.
r Our approach attains cutting-edge results on 7 challenging
datasets, consistently surpassing the current best methods
by a considerable margin. Besides, it is highly robust
and can maintain excellent detection performance under
particularly high or small anomaly ratios.
The prior edition of this paper is presented in [22]. The main
extensions include: (1) the theoretical foundation of our proposed SLA2 P approach (Section I) on the similarity-preserving
property of random projections which connects it with geometric
transformations, (2) new experimental results when the normal
data are multimodal, which further verifies that our approach
can work beyond unimodal setting. (3) freshly designed ablation
study about the robustness of the performance of SLA2 P w.r.t.
the transformed dimension which echos Theorem 1, (4) a comprehensive related work demonstrated in terms of unsupervised
anomaly detection, anomaly detection with pretrained networks,
self-supervised learning and input perturbation.
II. RELATED WORKS
Unsupervised anomaly detection Conventional approaches
to UAD are based mostly on classic unsupervised learning
tools, encompassing density estimation techniques [23], [24],
[25], clustering methods [26], [27], dimensionality reduction
methods [28], [29] and one-class SVM methods [30], [31].
Owing to the extraordinary expressive capacity of DNNs, a lot
of reconstruction-based techniques that use DNNs have been
created for UAD recently. They mainly employ deep generative
models [32], [33], [34] or autoencoders (AE) [35], [36], [37]

9283

to reconstruct data and determine abnormality of data via its
reconstruction error. For instance, DAGMM [38] feed the AE
latent representations into a GMM and cooperatively optimize
them. RSRAE [39] incorporates a robust Principal Component
Analysis layer [40] into deep autoencoders, which is intended to
project the inliers into their subspace while leaving the outliers
out. However, it is unavoidable that such kind of reconstructionbased approaches concentrate more on element-wise or lowlevel error instead of semantic information in the high level, as
pointed out by [41].
Anomaly detection with pretrained networks Transferring
discriminative embeddings of pretrained nets to AD has been
widely studied and achieved great success [42], [43], [44].
Andrews et al. [45] shows that transfer-representation-learning
approaches offer viable representations for AD tasks without
prior knowledge of the data. Methods in [46], [47] improve
AD performance on target domains via transferring information
of related domains. Burlina et al. [48] employs pretrained
VGGNets [49] to perform novelty detection. Recently DNNs
pretrained on ImageNet have been used to extract features for unsupervised anomaly detection and segmentation on images [20],
[50], [51], [52] and videos [53], [54].
Self-supervised learning (SSL) has been an increasingly prevailing unsupervised learning method. SSL methods learn representations via designing a pretext task between inputs and
self-defined signals [55], [56] or contrastive learning [57], [58].
Employing SSL techniques to assist semi-supervised AD has
shown promising results recently [59], [60], [61], [62]. In UAD
task, E3 Outlier [41] trains a Convolutional Net via SSL and
uses the network outputs of the CNN to design anomaly scores.
Nevertheless, such practice can only be applied to image data
and requires manually pre-defined transformations. By contrast,
our method can be applied to both image and tabular data, and
in our framework, random transformations are able to exhibit
promising performance.
Input Perturbation: Input adversarial perturbation technique
is proposed by [63] for the first time to yield adversarial data
samples to dupe the classifier. In OOD detection literature,
several works take advantage of the opposite perturbation to the
raw input data employing the gradient of the maximum softmax
score of the label predicted from pre-trained network [12], [14].
Lee et al. [64] add perturbation to increase the proposed Mahalanobis distance-based confidence score for OOD detection. In
the anomaly/outlier detection area, there are not many efforts to
use input-level perturbations to enhance AD performance as we
fail to directly use some pre-trained network softmax outputs.
As far as we know, we are the first to seamlessly combine the
perturbation technique with self-supervised learning to address
anomaly detection problems.
III. PROBLEM STATEMENT
We contemplate data space X ⊂ Rd and we are provided
an dataset X ⊂ X which is unlabeled. X is composed of both
inliers (normal data) Xin of size n and outliers (anomalous data)
Xout of size np, where 0 < p < 1 is the anomaly ratio which is
the ratio of the number of the outliers to that of the inliers. The

9284

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 12, DECEMBER 2024

Fig. 1. Overview of our proposed framework SLA2 P on image data. Given unlabeled image data with both inliers and outliers, we first extract representative
features from raw data and normalize them into a unit sphere vector space (features of anomalies are shaded). We then apply random projections to the features
through multiplicating matrices randomly sampled from standard normal distribution. Transformations by different matrices result in pseudo labels, on which
we train a DNN classifier. Next, we adversarially perturb the transformed samples using the gradients of the softmax output scores of the predicted labels of the
classifier. Finally, the scores for identifying anomalies are produced by utilizing the uncertainty estimates of the network’s predictions on the altered transformed
characteristics.

primary goal of UAD is to create an indicator function I(x) that
is universally applicable: X → {0, 1} such that I(x) = 1 for
x ∈ Xin and I(x) = 0 for x ∈ Xout . However, directly pursuing
such function is hard and inefficient, as there is a compromise
existing between type-I error (rate of normal samples which
are classified as anomalies) and type-II error (rate of anomalous
samples that are classified as normal) [59]. The standard practice
to deal with this problem is to instead design a score function
S(x) : X → R such that lower scores indicate more abnormality
while higher scores indicate more normality.
IV. METHOD
A. Utilizing L2 Normalization for Feature Extraction
Fig. 1 illustrates our proposed outline SLA2 P. Provided a raw
datum x, we transform it into its distinguishing representation
as an embedding f (x) ∈ Rd using a feature extractor f . The detailed choice setting of the embedding extraction function f for
different datasets is elaborated in Section VI. L2 normalization
is implemented on the features after embedding extraction:
v(x) =

f (x)
.
f (x)2

The embeddings are projected onto a sphere in Rd through L2
normalization, which merely decreases the dimension of the
feature by one but gets rid of the magnitude discrepancies among
the unlabeled data [65]. Our idea is that anomalies differ from
normal data in intrinsic and latent distribution, not magnitudes.
Therefore the normalization step is supposed to help the subsequent modules of SLA2 P to concentrate on semantic level
discrepancies and attenuate low-level variances between normal
and anomalous data. Our theoretical argument also corroborates
its effectiveness in that the proof of our similarity preserving
Theorem 1 requires the L2-norm of the processed vectors to be
1 (see Section V for more details).
The function f (x) can be any embedding function that converts raw input data into vector representations with semantic
information. The selection of models or approaches for feature
extraction is not constrained, as our SLA2 P framework is designed to operate effectively regardless of the feature extractor

employed. For inherently tabular data, the raw data is qualified
to serve as its embedding, i.e., choosing f to be identity mapping
is enough.
B. Self-Supervised Learning At the Feature Level
Inspiration drawn from geometric transformations in images:
Geometric transformations as self-supervision have obtained
tremendous success in unsupervised learning of image data [41],
[56], [59] and the central concept revolves around the notion
that DNNs are thought to have the ability to extract valubale
information from image data if they can detect their transformed
patterns [56]. Nevertheless, the majority of data utilized in
machine learning tasks is presented in a tabular format that
does not have a structure identical to that of two-dimensional
images, and there exist no in-hand “geometric transformations”
for vector-form data. In fact, geometric transformations are
executed via implementing affine transformations on the homogeneous coordinates of images. Given a coordinate pair
(x, y) , it is first symboled as a three-dimensional vector through
adding an additional dimension with element 1. Then the new
coordinates (x , y  ) are generated through the multiplication of
a transformation matrix:
⎛ ⎞ ⎛
⎞⎛ ⎞
x
a b c
x
⎝ y  ⎠ = ⎝d e f ⎠ ⎝ y ⎠ .
1
0 0 1
1
When a = cos θ, b = sin θ, d = − sin θ, e = cos θ, c = f = 0,
the manipulation carries out rotation by angle θ; when a =
e = 1, b = d = 0, c = x0 , f = y0 , it conducts image translation
along the x axis by x0 and along the y axis by y0 .
Motivated by this point, we suggest an extension of this type
of transformation to data in vector form by substituting the coordinate vectors with the vectors themselves. Consequently, we are
able to execute transformations from the feature level to perform
self-supervised learning. The designing of the transformation
matrix still remains a problem since a rotation matrix of vectors
does not have the same meanings as a rotation matrix for image
2D coordinates. Intriguingly, our experiments show that employing random matrices of which each element is independent and

WANG et al.: SLA2 P: SELF-SUPERVISED ANOMALY DETECTION WITH ADVERSARIAL PERTURBATION

identically distributed (i.i.d.) sampled from the standard normal
distribution, is sufficient to produce exceptional results. Next,
we give a detailed description of using random matrices for
self-supervision.
Random Matrix Multiplications as Surrogate Supervision:
We denote the random matrix set as A = {A(1) , A(2) , . . . ,
d)
A(M ) }. For any 1 ≤ m ≤ M , A(m) = (aij ) ∈ Rk×d (k
are i.i.d. sampled and the components of the matrix are also
sampled i.i.d. from standard normal distribution
aij ∼ N (0, 1).
The random transformation we create is intended to be the
operation of multiplying the aforementioned random matrices
to data features:
v(m) = A(m) v,
As a result, we have created a self-labeled dataset


DA 
v(m) (x), m x ∈ X , A(m) ∈ A .
Here we treat m as the pseudo label of A(m) v, and therefore
We possess a self-determined classification dataset featuring
M n(1 + p) transformed features. The random projections serve
a dual purpose of projecting feature embeddings into distinct
spaces and reducing their dimensions. We observe that a random
matrix multiplication projects one subspace or convex set in
Rd to another subspace or convex set in Rk , as claimed in
Proposition 1. Considering that extracted features of normal data
tend to be in a certain subspace or convex set, Proposition 1
guarantees that the transformed features of normal data are still
in one subspace or convex set.
Proposition 1. For any matrix A ∈ Rk×d , linear subspace
V ⊂ Rd and convex set U ⊂ Rd , AV is a linear subspace in
Rk and AU is a convex set in Rk .
Pseudo label classifier training We can straightforwardly
train a multi-class classifier Cθ with parameters θ on the dataset
which is self-labeled, i.e., the classifier network is supposed to
categorize the transformed features {v(m) (xi )} into pseudoclass m for any 1 ≤ m ≤ M . We adopt the cross-entropy loss
as the loss function. The output vector generated by the softmax
function of Cθ is denoted as y(·|θ) with mth element y (m) (·|θ),
and then the pretext task we define for ourselves is able to be
formulated as
min
θ

1
n(1 + p)

L(xi |θ),
i=1




1
log y (m) v(m) (xi )|θ
M m=1
M




1
log y (m) A(m) v(xi )|θ .
M m=1
M

=−

μ as a threshold of classification accuracy so that the training process terminates once the categorization precision of the classifier
network of the current batch gets to μ ∈ (0, 1). This strategy
actually holds a crucial function within our framework because
if the classifier Cθ is capable of discerning all the transformed
data well, the classification outcome struggles to effortlessly
identify the irregular data.
The random projections transform the extracted features of
the data into various subspaces, and the DNN classifier is subsequently trained to discern the specific subspace into which
these features have been projected. This methodology draws
inspiration from the 2D geometric transformations prevalent
in computer vision literature, which encompasses numerous
studies focusing on applying geometric transformations to images and training CNNs to recognize the specific transformations applied for representation learning [56], [59], [66]. The
underlying rationale for these methods is that if a CNN can
accurately predict the applied geometric transformation, the
network has acquired robust orientation-invariant features of
the image. Analogously, random projections can be perceived
as geometric transformations of vector representations within
vector space. Therefore, if our DNN classifier can successfully
identify the applied transformations, it is indicative of the network’s ability to learn robust rotation-invariant features of the
vector representations.
C. Adversarial Perturbation-Driven Scoring Using Network
Uncertainty
Our anomaly score function S(x) is defined based on the
predictive uncertainties of the classifier Cθ . Our goal is to assign
higher scores to normal data compared to anomalies. Rather than
employing the outcomes from training on the initial transformed
examples like [41], [59] did, We incorporate adversarial perturbation into the modified attributes prior to inputting them into
the classification model Cθ .
Adversarial Perturbation to the Transformed Features: We
adversarially perturb the transformed features using the gradient
of the negative log softmax score of the predicted class of the
trained classifier Cθ w.r.t. the input sample. In mathematical
terms, for any 1 ≤ m ≤ M and x, we let
vm (x) = v(m) (x) + η(−∇v(m) (x) log y (m) (x|θ)),

(1)

n(1+p)

where
L(xi |θ) = −

9285

In the training stage, we use an early stopping strategy to
abstain from the overfitting problem. We set a hyperparameter

where y (m) (x|θ) = maxi y (i) (v(m) (x)|θ), and η is the perturbation magnitude. Considering that Cθ has been trained comparatively well on the majority of the transformed data samples, this
approach intends to reduce the pseudo-class’s softmax score that
has the highest predicted probability, which means to increase
the difficulty in classifying the projected features. Note that our
adversarial perturbation form is different from [63] as we do not
involve the pseudo labels when computing the gradient. Empirically, we discover that following this operation, the anomaly
scores for both outliers and inliers will experience a reduction,
however, inliers will exhibit greater resilience to perturbations
than outliers.

9286

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 12, DECEMBER 2024

Negative Brier Score: Stimulated by reconstruction-based
anomaly detection methods [35], [38], [39] which use L2 distance error of input and reconstruction as score, we employ
euclidean distance for anomaly scoring by means of viewing the
one-hot embedding of the correct label as ground truth within
the classification task:
M  
2

1


S(x) = −
y v(m) (x)|θ − em  ,
2
M m=1
where em is the m-th canonical basis vector representing the
label vector of m-th pseudo-class. −S(x) refers to the mean
squared error of the output predictions of Cθ and one-hot ground
truth pseudo labels, corresponding to a classic proper score rule
known as Brier Score [67]. The ideal case is that the normal data
have lower errors and, accordingly, higher anomaly scores.
V. THEORETICAL FOUNDATION OF SLA2 P
Random projections do not manifestly preserve semantic
information of data, which contrasts with geometric transformations (e.g., a rotated or translated plane is still a plane, not
a bird). Due to randomness, one may have no explicit idea of
what subspace the features are projected into and whether the
random transformations have an influence on the discrepancies
among original features. Intriguingly, we find that as long as
the dimension k is sufficiently large, the L2 distance and inner
product of transformed embeddings, which are two effective
measures of similarities between high-dimensional vectors, are
roughly in proportion to their original values by a constant
factor k.
Theorem 1 (Similarity-preserving Property): Given any fixed
m and index pair of the unlabeled dataset (i, j), for any 0 <  <
1 and 0 < δ < 1,
4 log 2
1) when k > 2 −3δ , we have with at least 1 − δ probability
over the random sampling of matrix A(m) ,
2

 (m)
(m) 
v i − v j 
2
≤ (1+) vi − vj 22 ,
(1−) vi − vj 22 ≤
k
4 log 4

2) when k > 2 −3δ , we have with at least 1 − δ probability
over the random sampling of matrix A(m) ,
(m)

(m)

· vj
≤ vi · vj + .
k
The supplementary contains the proof of Theorem 1, which
is based on Johnson–Lindenstrauss lemma [68]. As stated in
Theorem 1, random projections are likely to preserve the similarities among features, i.e., originally distant features (e.g., one
normal and one anomalous instance) will still be comparatively
distant, and features originally closely distributed (e.g., normal
data) tend to be near each other after projection. This lays the
theoretical foundation of our SLA2 P framework in that, although
the transformations are random, they still preserve the structure
and inner relationship of the data, which is coherent with handcrafted 2D geometric transformations. We leave the theoretical
analysis on probabilities/error of our method for future work.
vi · vj −  ≤

vi

VI. EXPERIMENTS
We conduct diverse experiments to illustrate the effectiveness
and generality of our SLA2 P approach for unsupervised anomaly
detection.
A. Datasets
We conducted an empirical evaluation of our framework,
SLA2 P, on three image datasets and four tabular datasets to
demonstrate its capability and generality. The datasets of image data are CIFAR-10 [69], CIFAR-100 [69] and Caltech
101 [70]. The datasets of tabular data consists of text datasets
20 Newsgroups [71], Reuters-215781 and inherently tabular
datasets KDDCUP99 [72] and Arrhythmia. For the text and
image classification datasets, each category of data serves as
inliers in turn, and the reported outcome is the mean performance across all classes. The detailed descriptions are as
follows.
CIFAR-10 is composed of 60,000 images distributed across
10 categories with resolution 32 × 32. There are 6,000 images
per class. In each experiment, the inliers are 6,000 images from
one class, and the outliers are 6000p images randomly selected
from the rest classes.
CIFAR-100 contains 60,000 images of resolution 32×32
labeled according to 100 distinct categories. The 100 categories
are grouped into 20 superclasses and there are 3,000 images
within each superclass. In each experiment, the inliers are 3,000
images from one superclass, and the outliers are 3000p images
randomly chosen from the rest of the superclasses.
Caltech 101 contains 9,146 images of 101 different classes.
Each image’s size is 300 × 200. Following the experiment setting of [39], we select 11 classes that consist of at least 100
images and randomly sample 100 out of them for each class. In
each individual experiment, the inliers are 100 images from one
certain class, and the outliers are 100 × p images selected from
the rest ten classes at random.
20 Newsgroups is a text classification dataset with approximately 20,000 evenly distributed newsgroup articles, divided
across 20 classes. We randomly sample 360 documents per class.
In each individual experiment, the inliers are 360 documents
from one class, and the outliers are 360p documents randomly
chosen from the rest of the classes.
Reuters-21578 is a text classification dataset containing 90
text categories. We choose the five largest single-label classes
and randomly sample 360 documents for each class. In each
individual experiment, the inliers data are the documents from
one class, and 360p outliers are sampled randomly from the
remaining classes.
Arrhythmia is a small-scale medical dataset containing attributes on the diagnosis of cardiac arrhythmia in patients and
includes 16 classes. We construct the anomalous dataset using
the smallest classes 3,4,5,7,8,9,14,15 and the normal set using
the rest. There are 452 data instances among which 66 are
anomalous.
1 http://www.daviddlewis.com/resources/testcollections/reuters21578/

WANG et al.: SLA2 P: SELF-SUPERVISED ANOMALY DETECTION WITH ADVERSARIAL PERTURBATION

KDDCUP99 is a large-scale intrusion detection dataset. Following [38] we utilize the full UCI 10% dataset, where the
non-attack classes are treated as anomalies. There are 97278
abnormal instances and 396743 normal ones.
B. Experiment Setup
We contrast SLA2 P against six state-of-the-art techniques for
anomaly detection: IF [75], OCSVM [30], [31], DAGMM
[38], E3 Outlier [41], RSRAE [39] and PANDA [76]. We adopt
the commonly used Area under the Receiver Operating Characteristic curve (AUROC) and Area under the Precision-Recall
curve (AUPR) as the assessment criteria. For AUPR, we consider
outliers as “positive” when computing. All the experiments are
conducted independently 5 times using the same random
seeds 0, 1, 2, 3, 4 for fair comparison, and the averaged scores
are reported in the main paper. More experimental details (including each single classwise experiment result) are provided in
the supplementary file.
Hyperparameter Tuning Rule: We implement a K-fold crossvalidation strategy for hyperparameter tuning. This method involves dividing the dataset into l subsets. For each fold, K − 1
subsets are used for training, while the remaining subset is
designated as the validation set. This process is repeated K
times, ensuring each subset is used as the validation set exactly
once. The consistency of anomaly scores across the different
subsets of the dataset serves as our internal validation metric.
Specifically, we calculate the variance of the variance of the
anomaly scores for each fold, selecting the hyperparameter set
that minimizes this metric. For all the individual experiments,
the hyperparameter search range is defined as follows: for M ,
the candidate set is {64, 128, 256, 512}; for k, it is {128, 256};
for μ, it is {0.3, 0.4, 0.5, 0.6, 0.75, 0.9}; and for η, it is {10,
100, 1000, 10000}. We choose the fold number K = 5 for all
the experiments. The motivation of our hyperparameter tuning
rule is that the hyperparameter configuration exhibiting the
minimum variance of variance across multiple folds ensures that
our model’s performance remains stable and consistent across
various data splits.
Setup of SLA2 P: For image data, we use ResNets [77] pretrained using ImageNet dataset without the last fully connected
layer to obtain embeddings. To match the image input shapes, we
first resize raw images to 224 × 224 using Bilinear Interpolation
and then feed it into the extractor network. We preprocess raw
text data into vectors by sequentially utilizing the TFIDF transformer and Hashing-vector techniques [78], which is the same
process as in [39]. When dealing with data that is inherently in a
tabular format, we use the raw data vectors as input without any
further processing. We also conduct experiments using modern
pretrained language model for embedding extraction. We take
BERT [73] and GPT-3 [74] which are the two main-stream
and archetypal pretrained LLMs. Specifically, for BERT, we
use “bert-base-uncased” model from package transformers;2 for
GPT-3, we use “text-embedding-ada-002” model from package
openai.3 For Reuters dataset, we choose M = 512 and k = 128

9287

because of high dimensionality. For KDDCup99 dataset, we
assign M = 64 and k = 128 due to high computational burden.
For the remaining datasets, we set M = 256 and k = 256. As to
the early stopping threshold, we set μ = 0.75 on 20 Newsgroups
dataset, μ = 0.3 on Reuters dataset, and μ = 0.6 on all the
remaining datasets. We select the perturbation magnitude as
η = 10 for 20 Newsgroups, η = 1e2 for Reuters, η = 1e4 for
CIFAR-100 and η = 1e3 for all the remaining datasets. In fact,
setting μ = 0.6 and η = 1e3 is universally adequate for different
UAD tasks, and there is an implicit relationship between these
two hyperparameters (see ablation study). Given that the input
dimension of the classifier network is q, the classifier network
used in all experiments is a three-layer fully connected network,
which has the following structure: FC(q, 2q)-FC(2q, 4q)-FC(4q,
M ). Batch normalization [79] is applied to each layer and
LeakyReLU [80] is employed as activation function. We use
Adam [81] for the training with step size 1e-3 and weight decay
parameter 5e-4.
Setup of Baseline Methods: Our experiments indicate that
all the baseline methods, except E 3 outlier (which directly
manipulates images), work better using extracted representative
embeddings as input than using raw data as input. Hence to
enable a fair comparison, we evaluate our method against the
baseline approaches with extracted features as input in the
sequel. For the implementation of the benchmarks, we adapt
the code from package scikit-learn [82] for IF and OCSVM. We
implemented DAGMM and E3 Outlier using the code4 from [41]
with minimal modifications such that they are applicable to our
datasets and adapt to our experimental protocol. RSRAE results
are obtained running the official code.5 We adapt PANDA for
UAD setting by setting the testing set and the training set to be
the same with both inliers and outliers using the official code.6
All the data pre-processing processes follow the original papers.
C. Results
The average AUROC and AUPR of all the approaches on
all the datasets are summarized by us. To manifest the broad
applicability of our method, we show its performance under different anomaly ratios p = 10%, 30%, 50%. We call our method
without the adversarial perturbation step as SLA and include its
performance as well. Results on image datasets using pre-trained
ResNet-50 network are given in Table I. The results using
pre-trained ResNet-101 are provided in the supplementary for
completeness, where slightly better performances are achieved
owing to the usage of a deeper pre-trained DNN extractor. We
also summarize the results on text datasets and inherently tabular
datasets in Tables II, III, IV, and V respectively.
Results on Image Datasets: As shown in Table I, the performance of our two variants of our proposed approaches,
especially SLA2 P, consistently exceed existing approaches on
all the image datasets, including CIFAR-10 and CIFAR-100,
which are abidingly considered the most challenging datasets for
UAD [41]. In addition, SLA2 P is robust to the anomaly rate and
4 https://github.com/demonzyj56/E3Outlier

2 https://pypi.org/project/transformers/

5 https://github.com/dmzou/RSRAE

3 https://pypi.org/project/openai/

6 https://github.com/talreiss/PANDA

9288

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 12, DECEMBER 2024

TABLE I
AUROC/AUPR (%) PERFORMANCE ON IMAGE DATASETS FOR UAD WITH RESNET-50 AS THE FEATURE EXTRACTOR

TABLE II
AUROC/AUPR (%) PERFORMANCE ON TEXT DATASETS FOR UAD USING CLASSIC EMBEDDINGS

TABLE III
AUROC/AUPR (%) PERFORMANCE ON 20 NEWSGROUPS DATASET FOR UAD USING PRETRAINED LM EMBEDDINGS

TABLE IV
UAD PERFORMANCE ON INHERENTLY TABULAR DATASETS

TABLE V
UAD PERFORMANCE ON ARRHYTHMIA USING PRETRAINED LM EMBEDDINGS

can still obtain outstanding performance when the anomaly ratio
p is large, with AUROC score 86.63% on CIFAR-10, 82.48% on
CIFAR-100 dataset and 96.26% on Caltech 101 dataset when the
anomaly count reaches half the number of normal samples. This

is particularly commendable as when the number of anomalies
increases, no matter what UAD method is used, it is inevitable
that the adverse effect of the learning process of outliers to the
training of inliers will increase accordingly [34], [39].
Results on Tabular Datasets: Our framework demonstrates
superior performance not only on image datasets but also on
tabular datasets, as evidenced by Tables II, III, IV, and V.
Specifically, SLA2 P attains state-of-the-art (SOTA) outcomes
on 20 Newsgroups whether classic embedding or pretrained
language model embedding is used. When using classic embedding, SLA2 P surpasses the existing SOTA RSRAE by 3%-4% in
AUROC and approximately 10% in AUPR for varying anomaly
proportions. On Reuters, Our approach demonstrates a notable
improvement over the existing SOTA, achieving as much as
6.8% increase in AUROC and 16.6% enhancement in AUPR
when p = 0.3 compared to RSRAE. When using pretrained LM
embeddings, SLA2 P achieves SOTA results in both AUROC and
AUPR consistently on the 20 Newsgroups dataset, which indicates its generality. Moreover, our method exhibits dominating
performance on inherently tabular datasets, with more than 40%
AUPR improvement on Arrhythmia and in excess of 20% AUPR
increase on KDDCUP99 when raw data serves as input. The AUROCs and AUPRs of these two classical datasets all exceed 90%,
showcasing the practicality of SLA2 P on large-scale datasets
such as KDDCUP99. When using pretrained LM embeddings,

WANG et al.: SLA2 P: SELF-SUPERVISED ANOMALY DETECTION WITH ADVERSARIAL PERTURBATION

Fig. 2.

9289

AUROC and AUPR when the anomaly ratio is tiny.

TABLE VI
AUROC/AUPR (%) WHEN THE INLIERS OBEY MULTIMODAL DISTRIBUTION

SLA2 P demonstrates dominant performance whether BERT or
GPT-3 is used, exceeding all the current SOTA approaches. It
is worth noticing that, pretrained embedding might not always
perform better in our task than classic embedding. For instance,
on the 20 Newsgroups dataset, BERT embeddings lead to significantly worse results than classic embeddings generated utilizing
TFIDF transformer and Hashing-vector techniques.
Results Under Tiny Anomaly Ratios: The proportion of
anomalies may be exceptionally low in some unsupervised
anomaly detection tasks and circumstances. Therefore we further compare our methods to the baseline approaches when
the anomaly ratios are tiny: p = 1%, 2%, 3%, 4%, 5% (on text
datasets we employ classic embeddings). Obviously seen from
Fig. 2, our proposed SLA2 P still attains favorable performance
in comparison to other baseline approaches. Regarding all the
text and image datasets mentioned above, SLA2 P dominates in
AUPR and AUROC with minimal numerical deviations. Furthermore, as demonstrated by the steadiness of the SLA2 P curve
in Fig. 2, SLA2 P is remarkably stable with the alternation of p,
especially in AUROC, despite the fact that we require the random
sampling of the transformation matrices in our pipeline.
Results When the Normal Data are Multimodal: Many realworld applications for anomaly detection have a normal class
that exhibits multimodal distribution [83], [84]. In the multimodal scenarios, all but one class is considered normal, yielding
a dataset with a normal class that is multimodal and an abnormal
class with fewer instances. We experiment on image and text
datasets with anomaly ratio p = 0.3 and run 5 times under
this more challenging setting. We, in turn, use one class of data

as anomalies and sample normal data from the rest categories.
Other settings are the same as the previous unimodal setting
(on text datasets we employ classic embeddings), with the mean
outcomes being presented in Table VI. As shown in the table,
our method performs the best consistently, and the performance
improvement is even larger than the unimodal setting (over 30%
AUROC gain on the Reuters dataset).
D. Sensitivity Analysis and Ablation Study
Impact of Adversarial Perturbation: To To additionally showcase the role of the adversarial perturbations on the transformed
features, we graph the distributions of anomaly scores prior
to and following the perturbations. We choose experiments
with normal sample class ’cat’ of CIFAR-10, normal sample
class ’non-insect invertebrates’ of CIFR-100, normal sample
class ’comp.sys.mac.hardware’ of 20 Newsgroups, and normal
sample class ’topics’ of Reuters. Additionally, we include the Arrhythmia experiment. As illustrated in Fig. 3, our self-supervised
SLA framework has been capable of separating outliers: the
anomaly scores of inliers are generally higher than those of
outliers, which means the transformed features of inliers can
be better classified by Cθ . However, outliers continue to exist,
with their anomaly scores intertwining with those of inliers.
However, following the perturbation, the scores for both regular
and anomalous data decrease, but the inliers demonstrate greater
resilience to the disturbances, making the anomalies more separable. This phenomenon shows that with the same magnitude of
perturbation, the adversarial perturbation makes the transformed

9290

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 12, DECEMBER 2024

Fig. 3.

Distribution visualization of the anomaly scores before (top row) and after (bottom row) adversarial perturbation of our framework.

Fig. 4.

AUPR heatmap of our SLA2 P method.

features of the outliers have comparatively larger classification
result degradation than those of the inliers in our self-defined
pretext classification task.
Relationship Between μ and η: SLA2 P exhibits high robustness to variations in the early stopping threshold μ and the
perturbation magnitude η as demonstrated by the fine-grained
AUPR score results we provide for CIFAR-10, 20 Newsgroups,
and Arrhythmia datasets when p = 0.1, and μ is tuned to values
in the range of 0.4, 0.5, 0.6, 0.7, 0.8 and η is tuned using a
logarithmic scale, as shown in Fig. 4. We observed an extensive
spectrum of hyperparameter combinations that yielded AUPR
scores above 60% for CIFAR-10, over 55% for 20 Newsgroups,
and over 50% for Arrhythmia, surpassing current state-of-the-art
baselines. Moreover, within the span of hyperparameter options
that exhibited competitive performance, we found that higher
values of μ generally require larger values of η to ensure satisfactory detection performance. This makes sense as the more
transformed samples are classified well, the larger the step size
of the perturbations should be to separate the anomalies out.
Robustness to Transformed Dimension k: We investigate the
robustness of AD performance of SLA2 P to the transformation
matrix dimension k. We perform an ablation analysis on Caltech
101 dataset with varying k in the interval [25,350]. The experiment is repeated 5 times, and the AUROC and AUPR curve
w.r.t. dimension k are depicted in Fig. 5. We can conclude that

Fig. 5. UAD Performance on Caltech 101 with varying k of our proposed
SLA2 P approach.

the UAD performance of SLA2 P is generally robust w.r.t. k with
moderate growth when k increases and the growth tends to flatten
out when k becomes comparatively larger. This phenomenon
may be elucidated by Theorem 1 as k needs to be large enough
to preserve the similarities between the transformed features.
VII. CONCLUSION
In this article, we present a novel structure, SLA2 P, designed
for unsupervised anomaly identification. Our method employs
random projections as a new self-supervised technique at the
feature level and combines it with adversarial perturbations to
create distinctive anomaly scores. We present both theoretical

WANG et al.: SLA2 P: SELF-SUPERVISED ANOMALY DETECTION WITH ADVERSARIAL PERTURBATION

and empirical support for the efficacy of SLA2 P. It is our hope
that this research will serve as a foundation for using pretext
task-based perturbation methods in other unsupervised learning
scenarios or objectives.

REFERENCES
[1] G. Pang, C. Shen, L. Cao, and A. V. D. Hengel, “Deep learning for anomaly
detection: A review,” 2020, arXiv: 2007.02500.
[2] S. Min, B. Lee, and S. Yoon, “Deep learning in bioinformatics,” Brief.
Bioinf., vol. 18, pp. 851–869, 2017.
[3] S. Khan and T. Yairi, “A review on the application of deep learning
in system health management,” Mech. Syst. Signal Process., vol. 107,
pp. 241–265, 2018.
[4] A. O. Adewumi and A. A. Akinyelu, “A survey of machine-learning and
nature-inspired based credit card fraud detection techniques,” Int. J. Syst.
Assurance Eng. Manage., vol. 8, pp. 937–953, 2017.
[5] A. Shen, R. Tong, and Y. Deng, “Application of classification models
on credit card fraud detection,” in Proc. IEEE Int. Conf. Serv. Syst. Serv.
Manage., 2007, pp. 1–4.
[6] K. Fu, D. Cheng, Y. Tu, and L. Zhang, “Credit card fraud detection using
convolutional neural networks,” in Proc. Int. Conf. Neural Inf. Process.,
2016, pp. 483–490.
[7] S. C. Tan, K. M. Ting, and F. T. Liu, “Fast anomaly detection for streaming
data,” in Proc. Int. Joint Conf. Artif. Intell., 2011, pp. 1511–1516.
[8] D. Kwon, H. Kim, J. Kim, S. C. Suh, I. Kim, and K. J. Kim, “A survey
of deep learning-based network anomaly detection,” Cluster Comput.,
vol. 22, pp. 949–961, 2019.
[9] Z. Chen, Y. Tian, W. Zeng, and T. Huang, “Detecting abnormal behaviors in
surveillance videos based on fuzzy clustering and multiple auto-encoders,”
in Proc. IEEE Int. Conf. Multimedia Expo, 2015, pp. 1–6.
[10] W. Sultani, C. Chen, and M. Shah, “Real-world anomaly detection in
surveillance videos,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2018, pp. 6479–6488.
[11] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A survey,”
ACM Comput. Surv., vol. 41, pp. 1–58, 2009.
[12] S. Liang, Y. Li, and R. Srikant, “Enhancing the reliability of out-ofdistribution image detection in neural networks,” in Proc. Int. Conf. Learn.
Representations, 2018, pp. 1–9.
[13] D. Hendrycks, M. Mazeika, and T. G. Dietterich, “Deep anomaly detection
with outlier exposure,” in Proc. Int. Conf. Learn. Representations, 2019,
pp. 1–9.
[14] Y.-C. Hsu, Y. Shen, H. Jin, and Z. Kira, “Generalized odin: Detecting out-of-distribution image without learning from out-of-distribution
data,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2020,
pp. 10951–10960.
[15] W. Liu, X. Wang, J. D. Owens, and Y. Li, “Energy-based out-of-distribution
detection,” 2020, arXiv: 2010.03759.
[16] R. Chalapathy and S. Chawla, “Deep learning for anomaly detection: A
survey,” 2019, arXiv: 1901.03407.
[17] V. Chandola, A. Banerjee, and V. Kumar, “Outlier detection: A survey,”
ACM Comput. Surv., vol. 14, 2007, Art. no. 15.
[18] G. Somepalli, Y. Wu, Y. Balaji, B. Vinzamuri, and S. Feizi, “Unsupervised
anomaly detection with adversarial mirrored autoencoders,” 2020, arXiv:
2003.10713.
[19] G. Kwon, M. Prabhushankar, D. Temel, and G. AlRegib, “Backpropagated gradient representations for anomaly detection,” in Proc. Eur. Conf.
Comput. Vis., 2020, pp. 206–226.
[20] S. Venkataramanan, K.-C. Peng, R. V. Singh, and A. Mahalanobis, “Attention guided anomaly detection and localization in images,” 2019, arXiv:
1911.08616.
[21] R. T. Schirrmeister, Y. Zhou, T. Ball, and D. Zhang, “Understanding
anomaly detection with deep invertible networks through hierarchies of
distributions and features,” 2020, arXiv: 2006.10848.
[22] Y. Wang, C. Qin, R. Wei, Y. Xu, Y. Bai, and Y. Fu, “Self-supervision meets
adversarial perturbation: A novel framework for anomaly detection,” in
Proc. Conf. Inf. Knowl. Manage., 2022, pp. 4555–4559.
[23] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” in Proc. ACM SIGMOD Int. Conf. Manage.
Data, 2000, pp. 93–104.
[24] X. Yang, L. J. Latecki, and D. Pokrajac, “Outlier detection with globally
optimal exemplar-based GMM,” in Proc. SIAM Int. Conf. Data Mining,
2009, pp. 145–154.

9291

[25] J. Kim and C. D. Scott, “Robust kernel density estimation,” J. Mach. Learn.
Res., vol. 13, pp. 2529–2565, 2012.
[26] M. Ester et al., “A density-based algorithm for discovering clusters in
large spatial databases with noise,” in Proc. Int. Conf. Knowl. Discov.
Data Mining, 1996, pp. 226–231.
[27] Z. He, X. Xu, and S. Deng, “Discovering cluster-based local outliers,”
Pattern Recognit. Lett., vol. 24, pp. 1641–1650, 2003.
[28] M.-L. Shyu, S.-C. Chen, K. Sarinnapakorn, and L. Chang, “A novel
anomaly detection scheme based on principal component classifier,” Miami Univ Coral Gables FL Dept of Electrical and Computer Engineering,
Tech. Rep., 2003.
[29] R. Paffenroth, K. Kay, and L. Servi, “Robust PCA for anomaly detection
in cyber networks,” 2018, arXiv: 1801.01571.
[30] B. Schölkopf, R. C. Williamson, A. J. Smola, J. Shawe-Taylor, and J. C.
Platt, “Support vector method for novelty detection,” in Proc. Int. Conf.
Neural Inf. Process. Syst., 2000, pp. 582–588.
[31] M. Amer, M. Goldstein, and S. Abdennadher, “Enhancing one-class
support vector machines for unsupervised anomaly detection,” in Proc.
ACM SIGKDD Workshop Outlier Detection Description, 2013, pp. 8–15.
[32] H. Zenati, C. S. Foo, B. Lecouat, G. Manek, and V. R. Chandrasekhar,
“Efficient GAN-based anomaly detection,” 2018, arXiv: 1802.06222.
[33] P. Perera, R. Nallapati, and B. Xiang, “OCGAN: One-class novelty detection using GANs with constrained latent representations,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2019, pp. 2898–2906.
[34] C.-H. Lai, D. Zou, and G. Lerman, “Novelty detection via robust variational autoencoding,” 2020, arXiv: 2006.05534.
[35] J. Chen, S. Sathe, C. C. Aggarwal, and D. S. Turaga, “Outlier detection
with autoencoder ensembles,” in Proc. SIAM Int. Conf. Data Mining, 2017,
pp. 90–98.
[36] S. Pidhorskyi, R. Almohsen, and G. Doretto, “Generative probabilistic
novelty detection with adversarial autoencoders,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2018, pp. 6823–6834.
[37] D. Abati, A. Porrello, S. Calderara, and R. Cucchiara, “Latent space
autoregression for novelty detection,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit., 2019, pp. 481–490.
[38] B. Zong et al., “Deep autoencoding gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Representations,
2018, pp. 1–9.
[39] C. Lai, D. Zou, and G. Lerman, “Robust subspace recovery layer for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Representations,
2020, pp. 1–10.
[40] G. Lerman and T. Maunu, “An overview of robust subspace recovery,” in
Proc. IEEE, vol. 106, no. 8, pp. 1380–1410, Aug. 2018.
[41] S. Wang et al., “Effective end-to-end unsupervised outlier detection via
inlier priority of discriminative network,” in Proc. Int. Conf. Neural Inf.
Process. Syst., 2019, pp. 5962–5975.
[42] M. Sabokrou, M. Fayyaz, M. Fathy, Z. Moayed, and R. Klette, “Deepanomaly: Fully convolutional neural network for fast anomaly detection in
crowded scenes,” Comput. Vis. Image Understanding, vol. 172, pp. 88–97,
2018.
[43] O. Rippel, P. Mertens, and D. Merhof, “Modeling the distribution of normal
data in pre-trained deep features for anomaly detection,” 2020, arXiv:
2005.14140.
[44] L. Ruff et al., “A unifying review of deep and shallow anomaly detection,”
2020, arXiv: 2009.11732.
[45] J. Andrews, T. Tanay, E. J. Morton, and L. D. Griffin, “Transfer
representation-learning for anomaly detection,” J. Mach. Learn. Res.,
2016.
[46] A. Kumagai, T. Iwata, and Y. Fujiwara, “Transfer anomaly detection by
inferring latent domain representations,” in Proc. Int. Conf. Neural Inf.
Process. Syst., 2019, pp. 2471–2481.
[47] V. Vercruyssen, W. Meert, and J. Davis, “Transfer learning for anomaly
detection through localized and unsupervised instance selection,” in Proc.
Conf. Assoc. Advance. Artif. Intell., 2020, pp. 6054–6061.
[48] P. Burlina, N. Joshi, and I. Wang, “Where’s wally now? Deep generative
and discriminative embeddings for novelty detection,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit., 2019, pp. 11507–11516.
[49] K. Simonyan and A. Zisserman, “Very deep convolutional networks for
large-scale image recognition,” in Proc. Int. Conf. Learn. Representations,
2015, pp. 1–8.
[50] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “MVTec AD - A
comprehensive real-world dataset for unsupervised anomaly detection,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2019, pp. 11507–
11516.
[51] P. Bergmann, M. Fauser, D. Sattlegger, and C. Steger, “Uninformed
students: Student-teacher anomaly detection with discriminative latent

9292

IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING, VOL. 36, NO. 12, DECEMBER 2024

embeddings,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2020, pp. 4183–4192.
[52] L. Bergman, N. Cohen, and Y. Hoshen, “Deep nearest neighbor anomaly
detection,” 2020, arXiv: 2002.10445.
[53] T. S. Nazare, R. F. de Mello, and M. A. Ponti, “Are pre-trained CNNs
good feature extractors for anomaly detection in surveillance videos?,”
2018, arXiv: 1811.08495.
[54] G. Pang, C. Yan, C. Shen, A. van den Hengel, and X. Bai, “Self-trained
deep ordinal regression for end-to-end video anomaly detection,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2020, pp. 12173–12182.
[55] P. Bojanowski and A. Joulin, “Unsupervised learning by predicting noise,”
in Proc. Int. Conf. Mach. Learn., 2017, pp. 517–526.
[56] S. Gidaris, P. Singh, and N. Komodakis, “Unsupervised representation
learning by predicting image rotations,” in Proc. Int. Conf. Learn. Representations, 2018, pp. 1–12.
[57] A. v. d. Oord, Y. Li, and O. Vinyals, “Representation learning with
contrastive predictive coding,” 2018, arXiv: 1807.03748.
[58] T. Chen, S. Kornblith, M. Norouzi, and G. E. Hinton, “A simple framework
for contrastive learning of visual representations,” in Proc. Int. Conf. Mach.
Learn., 2020, pp. 1597–1607.
[59] I. Golan and R. El-Yaniv, “Deep anomaly detection using geometric
transformations,” in Proc. Int. Conf. Neural Inf. Process. Syst., 2018,
pp. 9781–9791.
[60] L. Bergman and Y. Hoshen, “Classification-based anomaly detection for
general data,” in Proc. Int. Conf. Learn. Representations, 2020, pp. 1–9.
[61] J. Tack, S. Mo, J. Jeong, and J. Shin, “CSI: Novelty detection via contrastive
learning on distributionally shifted instances,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2020, pp. 11839–11852.
[62] V. Sehwag, M. Chiang, and P. Mittal, “SSD: A unified framework for selfsupervised outlier detection,” in Proc. Int. Conf. Learn. Representations,
2021, pp. 1–9.
[63] I. J. Goodfellow, J. Shlens, and C. Szegedy, “Explaining and harnessing
adversarial examples,” in Proc. Int. Conf. Learn. Representations, 2014,
pp. 1–9.
[64] K. Lee, K. Lee, H. Lee, and J. Shin, “A simple unified framework for
detecting out-of-distribution samples and adversarial attacks,” in Proc.
Int. Conf. Neural Inf. Process. Syst., 2018, pp. 7167–7177.
[65] X. Gu, J. Sun, and Z. Xu, “Spherical space domain adaptation with
robust pseudo-label loss,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit., 2020, pp. 9101–9110.
[66] Z. Feng, C. Xu, and D. Tao, “Self-supervised representation learning
by rotation feature decoupling,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit., 2019, pp. 10 364–10 374.
[67] G. W. Brier et al., “Verification of forecasts expressed in terms of probability,” Monthly Weather Rev., vol. 78, pp. 1–3, 1950.
[68] S. Dasgupta and A. Gupta, “An elementary proof of a theorem of johnson
and lindenstrauss,” Random Struct. Algorithms, vol. 22, no. 1, pp. 60–65,
2003.
[69] A. Krizhevsky et al., “Learning multiple layers of features from tiny
images,” Master’s thesis, Dept. Comput. Sci., Univ. Toronto, 2009.
[70] L. Fei-Fei, R. Fergus, and P. Perona, “Learning generative visual models
from few training examples: An incremental Bayesian approach tested
on 101 object categories,” in Proc. Conf. Comput. Vis. Pattern Recognit.
Workshop, 2004, pp. 178–178.
[71] K. Lang, “Newsweeder: Learning to filter netnews,” in Machine Learning
Proceedings. San Mateo, CA, USA: Morgan Kaufmann, 1995.
[72] D. Dua and C. Graff, “UCI machine learning repository,” 2017. [Online].
Available: http://archive.ics.uci.edu/ml
[73] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pre-training of
deep bidirectional transformers for language understanding,” 2018, arXiv:
1810.04805.
[74] T. Brown et al., “Language models are few-shot learners,” in Proc. Adv.
Neural Inf. Process. Syst., 2020, pp. 1877–1901.
[75] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. 8th IEEE
Int. Conf. Data Mining, 2008, pp. 413–422.
[76] T. Reiss, N. Cohen, L. Bergman, and Y. Hoshen, “PANDA: Adapting
pretrained features for anomaly detection and segmentation,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2021, pp. 2805–2813.
[77] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for image
recognition,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2016, pp. 770–778.
[78] A. Rajaraman and J. D. Ullman, Mining of Massive Datasets. Cambridge,
U.K.: Cambridge Univ. Press, 2011.

[79] S. Ioffe and C. Szegedy, “Batch normalization: Accelerating deep network
training by reducing internal covariate shift,” in Proc. Int. Conf. Mach.
Learn., 2015, pp. 448–456.
[80] B. Xu, N. Wang, T. Chen, and M. Li, “Empirical evaluation of rectified
activations in convolutional network,” 2015, arXiv:1505.00853.
[81] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
in Proc. Int. Conf. Learn. Representations, 2015, pp. 1–10.
[82] F. Pedregosa et al., “Scikit-learn: Machine learning in Python,” J. Mach.
Learn. Res., vol. 12, pp. 2825–2830, 2011.
[83] F. Ahmed and A. Courville, “Detecting semantic anomalies,” in Proc.
Conf. Assoc. Advance. Artif. Intell., 2020, pp. 3154–3162.
[84] M. J. Cohen and S. Avidan, “Transformaly–two (feature spaces) are better
than one,” 2021, arXiv:2112.04185.

Yizhou Wang (Member, IEEE) received the BS degree in mathematics and applied mathematics (Honors Program) from the School of Mathematics and
Statistics, Xi’an Jiaotong University, Xi’an, China,
in 2020. He is currently working toward the PhD
degree with the Department of Electrical and Computer Engineering, Northeastern University, Boston,
Massachusetts, under the supervision of Prof. Yun
Raymond Fu. His research interests include machine
learning, computer vision and data mining. He has
published some papers at top-tier conferences including ICLR, CVPR, CIKM, ICDM and IJCAI. He has served as a reviewer for ACM
Transactions on Knowledge Discovery from Data, Knowledge and Information
Systems, ICML, NeurIPS, ICLR, CVPR, ECCV, KDD, AAAI, IJCAI, PAKDD,
ICME, etc.

Can Qin received the BE degree from Xidian University, China in 2018 and the PhD degree in computer
engineering from Northeastern University, Boston,
Massachusetts in 2023. He is now a research scientist
with Salesforce Research. His research focus spans
transfer learning, semi-supervised learning, and deep
learning in broad. He received awards for the Best
Paper Award of the Real-World Recognition from
Low-Quality Images and Videos workshop at ICCV,
2019. Additionally, he has published some papers
at top-tier conferences, including NeurIPS, ICLR,
AAAI, ICCV, ECCV, KDD, etc.

Rongzhe Wei received the BS degree from Xi’an
Jiaotong University in 2021. He is currently working
toward the PhD degree with the Georgia Institute
of Technology. His research interests are theoretical
foundations of graph neural networks, and data privacy (especially for graph data).

Yi Xu (Graduate Student Member, IEEE) received the
BS and MS degrees from Xi’an Jiaotong University in
2017 and 2020 respectively. Currently he is working
toward the PhD degree with Northeastern University.
His current research interests are machine learning,
computer vision, pattern recognition, and their applications to intelligent systems.

WANG et al.: SLA2 P: SELF-SUPERVISED ANOMALY DETECTION WITH ADVERSARIAL PERTURBATION

Yue Bai received the BSc degree in mathematics from
Donghua University, Shanghai, China in 2017 and
the MEng degree in data analytics engineering from
Northeastern University, Boston, MA, in 2019. He is
currently working toward the PhD degree with the
Department of Electrical and Computer Engineering,
Northeastern University, Boston, MA, USA. His research interests include machine learning, computer
vision, and deep learning. He has served as the reviewer for IEEE Transactions on Image Processing,
IEEE Transactions on Neural Networks and Learning
Systems, IEEE Transactions on Knowledge and Data Engineering, ICML,
NeurIPS, CVPR, IJCAI, etc.

9293

Yun Fu (Fellow, IEEE) received the BEng degree
in information engineering and the MEng degree in
pattern recognition and intelligence systems from
Xi’an Jiaotong University, China, and the MS degree in statistics and the PhD degree in electrical
and computer engineering from the University of
Illinois at Urbana–Champaign. He has been an interdisciplinary faculty member with the College of
Engineering and the College of Computer and Information Science, Northeastern University, since 2012
His research interests are machine learning, computational intelligence, Big Data mining, computer vision, pattern recognition,
and cyber-physical systems. He has extensive publications in leading journals,
books/book chapters, and international conferences/workshops. He serves as an
associate editor, the chair, a PC member, and a reviewer of many top journals
and international conferences/workshops. He received seven prestigious young
investigator awards from NAE, ONR, ARO, IEEE, INNS, UIUC, and Grainger
Foundation; eleven best paper awards from IEEE, ACM, IAPR, SPIE, and
SIAM; and many major industrial research awards from Google, Samsung,
Amazon, Konica Minolta, JP Morgan, Zebra, Adobe, and Mathworks. He is
currently an associate editor of IEEE Transactions on Pattern Analysis and
Machine Intelligence. He is member of Academia Europaea (MAE), member of
European Academy of Sciences and Arts (EASA), fellow of National Academy
of Inventors (NAI), AAAS Fellow, AIMBE fellow, IAPR fellow, OSA fellow,
SPIE fellow, AAIA fellow, and ACM distinguished scientist.
PAPER_TEXT
