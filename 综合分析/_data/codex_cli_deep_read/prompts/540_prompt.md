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
# [540] Self-Supervised Anomaly Detection With Neural Transformations
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
编号：540
题名：Self-Supervised Anomaly Detection With Neural Transformations
年份：2024
DOI：10.1109/tpami.2024.3519543
来源：IEEE Transactions on Pattern Analysis and Machine Intelligence
PDF：paper/10.1109_TPAMI.2024.3519543.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测
相关性：弱相关，分数 2
已有代码状态：已下载；NeuTraL-AD -> source\NeuTraL-AD

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\540.txt
- 原始字符数：92553
- 本次发送字符数：92553
- 是否截断：False

代码包：
- 仓库：NeuTraL-AD
  - URL：https://github.com/boschresearch/NeuTraL-AD
  - 状态：downloaded
  - 本地目录：source\NeuTraL-AD
  - 顶层结构：.gitignore、3rd-party-licenses.txt、DATA/、Extract_img_features.py、LICENSE、Launch_Exps.py、README.md、config/、config_files/、evaluation/、loader/、models/、requiresments.txt、utils.py
  - 主要语言：Python:22、YAML:11
  - README 标题：Neural Transformation Learning for Anomaly Detection (NeuTraLAD)、Purpose of the project、Reproduce the Results、How to Use、Datasets、Citation、License、Neural Transformation Learning for Anomaly Detection (NeuTraLAD)、Purpose of the project、Reproduce the Results
  - README 运行线索：python Launch_Exps.py --config-file $1 --dataset-name $2；python Launch_Exps.py --config-file $1 --dataset-name $2；python Launch_Exps.py --config-file $1 --dataset-name $2
  - 关键文件：{"数据处理入口": ["Extract_img_features.py", "config/Dataset_Class.py", "DATA/arabic_digits/processing.py"], "配置文件": ["config_files/config_arabic.yml", "config_files/config_arrhy.yml", "config_files/config_characters.yml", "config_files/config_cifar10_feat.yml", "config_files/config_epilepsy.yml", "config_files/config_fmnist.yml", "config_files/config_kdd.yml", "config_files/config_kddrev.yml", "config_files/config_natops.yml", "config_files/config_rs.yml", "config_files/config_thyroid.yml"]}
  - 数据集线索：KDD、Tor、cert、dapt、kdd、tor

论文正文包开始：
<<<PAPER_TEXT
2170

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 47, NO. 3, MARCH 2025

Self-Supervised Anomaly Detection
With Neural Transformations
Chen Qiu , Marius Kloft , Senior Member, IEEE, Stephan Mandt , Member, IEEE, and Maja Rudolph

Abstract—Data augmentation plays a critical role in
self-supervised learning, including anomaly detection. While
hand-crafted transformations such as image rotations can achieve
impressive performance on image data, effective transformations
of non-image data are lacking. In this work, we study learning such
transformations for end-to-end anomaly detection on arbitrary
data. We find that a contrastive loss–which encourages learning
diverse data transformations while preserving the relevant
semantic content of the data–is more suitable than previously
proposed losses for transformation learning, a fact that we prove
theoretically and empirically. We demonstrate that anomaly
detection using neural transformation learning can achieve
state-of-the-art results for time series data, tabular data, text data
and graph data. Furthermore, our approach can make image
anomaly detection more interpretable by learning transformations
at different levels of abstraction.
Index Terms—Deep anomaly detection, self-supervised anomaly
detection, self-supervised learning, neural transformations.

I. INTRODUCTION
ANY recent advances in anomaly detection rely on the
paradigm of data augmentation. In the self-supervised
setting, especially for image data, predefined transformations
such as rotations, reflections, and cropping are used to generate
varying views of the data. This idea has led to strong anomaly
detectors based on either transformation prediction [25], [31],

M

Received 10 January 2024; revised 31 October 2024; accepted 12 December
2024. Date of publication 18 December 2024; date of current version 5 February
2025. The work of Stephan Mandt was supported in part by the National Science
Foundation (NSF) under Grant IIS-2047418 and Grant IIS-2007719, in part
by NSF LEAP Center, in part by the Department of Energy under Grant DESC0022331, in part by IARPA WRIVA program, in part by Hasso Plattner
Research Center, UCI, in part by Chan Zuckerberg Initiative, and in part by gifts
from Qualcomm and Disney. The work of Marius Kloft was supported in part by
Carl-Zeiss Foundation, in part by DFG under Grant KL 2698/2-1 and Grant KL
2698/5-1, in part by BMBF under Grant 03-B0770E and Grant 01-S21010C, and
in part by the DFG research unit under Grant 5359 (BU 4042/2-1, KL 2698/6-1,
and KL 2698/7-1). Recommended for acceptance by Y. Yu. (Corresponding
authors: Chen Qiu; Maja Rudolph.)
Chen Qiu is with the Bosch Center for AI, Pittsburgh, PA 15222 USA (e-mail:
chen.qiu@us.bosch.com).
Marius Kloft is with the Department of Computer Science at RPTU
Kaiserslautern-Landau, 67663 Kaiserslautern, Germany (e-mail: kloft@
cs.uni-kl.de).
Stephan Mandt is with the Department of Computer Science and Statistics,
University of California, Irvine, CA 92697 USA (e-mail: mandt@uci.edu).
Maja Rudolph is with the Bosch Center for AI, Pittsburgh, PA 15222 USA,
and also with the University of Wisconsin, Madison, WI 53706 USA (e-mail:
maja.rudolph@wisc.edu).
The code is available at https://github.com/boschresearch/NeuTraL-AD.git.
This article has supplementary downloadable material available at
https://doi.org/10.1109/TPAMI.2024.3519543, provided by the authors.
Digital Object Identifier 10.1109/TPAMI.2024.3519543

[82] or using representations learned using these views [15] for
downstream anomaly detection tasks [74], [75].
Unfortunately, for data other than images, such as time series,
tabular data, graphs, or text, it is much less well known which
transformations are useful, and it is hard to design these transformations manually. This paper studies self-supervised anomaly
detection for general data types. We develop Neural Transformation Learning for Anomaly Detection (NeuTraL AD): a simple
end-to-end procedure for anomaly detection with learnable
transformations. Instead of manually designing data transformations to construct auxiliary prediction tasks that can be used
for anomaly detection, we derive a single objective function
for jointly learning useful data transformations and anomaly
scoring. As detailed below, the idea is to learn a variety of transformations such that the transformed samples share semantic
information with their original form while different views are
easily distinguishable.
NeuTraL AD has only two components: a fixed set of learnable transformations and an encoder model. Both elements are
jointly trained on a noise-free Deterministic Contrastive Loss
(DCL) designed to learn faithful transformations. Our DCL is
different from other contrastive losses in representation learning [8], [15], [28], [50], [56] and image anomaly detection [74],
[75], all of which use negative samples from a noise distribution.
In contrast, our approach constructs other learnable transformations as negative samples and leads to a non-stochastic objective
that neither needs any additional regularization nor adversarial
training [76] and can be directly used as the anomaly score.
In Section II we describe NeuTraL AD and DCL, a novel
objective for learning diverse and semantically meaningful
transformations. We also establish the connections between
NeuTraL AD and popular alternative deep anomaly detection
method, specifically deep One-Class Classification (OCC). We
show that NeuTraL AD generalizes deep OCC and has several
advantages thanks to the learnable transformations.
Our approach leads to a new state-of-the-art in deep anomaly
detection. For time series and tabular data, NeuTraL AD significantly improves the anomaly detection accuracy. For example,
on an epilepsy time series dataset, we raised the state-of-the-art
from an AUC of 82.6% to 92.6% (+10%). On an arrhythmia tabular dataset, we raised the F1-score by 3.7 percentage
points. In the case of anomaly detection on text, we raised the
state-of-the-art (no outlier exposure) from an AUC of 93.4% to
94.7% (+1.3%) on the Reuters dataset. For graph-level anomaly
detection, we raised the bar in terms of AUC by 7.5 percentage
points averaged over six datasets from various domains. In terms

© 2024 The Authors. This work is licensed under a Creative Commons Attribution 4.0 License. For more information, see
https://creativecommons.org/licenses/by/4.0/

QIU et al.: SELF-SUPERVISED ANOMALY DETECTION WITH NEURAL TRANSFORMATIONS

of images, NeuTraL AD generalizes self-supervised anomaly
detection to image features and achieves comparable results to
the state-of-the-art method.
We begin by presenting NeuTraL AD in Section II. We then
demonstrate the effectiveness of our method with comprehensive experiments in Section III Finally, we discuss related work
in Section IV and conclude the paper in Section V.
Our previous work, Qiu et al. [60], introduced NeuTraL AD
for deep anomaly detection beyond images, focusing primarily
on time series and tabular data. In that study, we proposed using
a fixed set of learnable transformations and an encoder model,
jointly trained with a noise-free contrastive loss. The approach
was limited in its application to specific data types and did not
fully explore the potential of the model formulation.
In this paper, we extend NeuTraL AD in several key ways:
r Generalized Model Formulation: We broaden the model by
exploring various similarity functions in the loss, showing
that deep one-class classification is a special case of our
framework.
r Extension to New Data Modalities: We expand NeuTraL AD to handle images, text, and graphs, demonstrating
its versatility and effectiveness across different domains.
r Comprehensive Theoretical and Empirical Analysis: We
provide a detailed analysis of the DCL, including theoretical justification and empirical studies that balance the
objectives of aligning with original data embeddings while
encouraging diversity among transformed views.
r Extensive Experiments and Ablation Studies: We conduct
comprehensive experiments and ablation studies that offer
deeper insights into the model’s effectiveness and robustness across various datasets and data types including time
series, tabular data, images, text, and graphs.
These advancements represent significant contributions beyond our earlier work, offering a more comprehensive understanding and broader applicability of NeuTraL AD.
II. ALGORITHM AND METHODOLOGY
We develop neural transformation learning for anomaly detection (NeuTraL AD), a deep anomaly detection method based on
contrastive learning for general data types. It is a simple pipeline
with two components: a set of learnable transformations and a
loss function. The transformations are trained jointly on a DCL.
The objective has two purposes. During training, it is optimized
to find the parameters of the transformations. During testing, it is
also used to score each sample as either an inlier or an anomaly.
We now describe our approach in detail.
A. Preliminaries
The essence of an anomaly detection algorithm is to produce
a score function s(x) : X → R, which measures the degree of
abnormality of each sample in the data space X . The score function is used during test time to detect anomalies by evaluating
whether the score is above a threshold τa ,

1, if s(x) ≥ τa meaning x abnormal ,
(1)
ŷ =
0, otherwise
meaning x normal .

2171

TABLE I
MAIN NOTATIONS USED IN THE ALGORITHM

The threshold τa is calibrated for the specific application (e.g.,
using a labeled validation set). A data-driven anomaly detection algorithm relies on an unlabeled training dataset D =
{x1 , . . . , xN } ⊂ X to learn a score function. Here we consider
a self-supervised approach.
Self-supervised methods typically learn a feature extractor
and representations by solving auxiliary tasks. The tasks are typically formulated by defining a training loss. In self-supervised
anomaly detection [25], task performance (i.e., the loss function
used during training) is directly used as the score function. For
example, in Golan and El-Yaniv [25] and Wang et al. [82] image
transformations such as rotations, blurring, and cropping are
applied to input images. The learning task consists of predicting
which transformation has been applied given a transformed
input image. This task is formalized in a loss function (e.g.,
cross-entropy of prediction). During training, the loss will decrease on most training examples. Due to the principle of inlier
priority [82] and assuming that most training examples are
normal inliers, training will promote the model to generalize
better to held-out inliers than anomalies. The loss on a held-out
example can therefore be used as the anomaly score.
Our approach also follows the principles of self-supervised
anomaly detection. We next develop the NeuTraL AD training
task which defines our approach.
B. Methodology
NeuTraL AD learns an anomaly detector which contains
K + 1 transformations T := {T0 , T1 , . . ., TK }. Each transformation is a parameterized function (e.g., a neural network)
Tk (·; θk ) : X → Z that maps samples into an embedding space
Z. We sometimes drop the parameter dependence for brevity,
Tk (·; θk ) ≡ Tk (·). These embeddings include one reference
embedding T0 (x) and K transformed embeddings Tk (x) for
k = 1, . . . , K. We assume that all transformations are learnable,
i.e., they can be modeled by any parameterized function whose
parameters θk are accessible to gradient-based optimization. A
schematic of NeuTraL AD is in Fig. 1. Each sample is transformed by a set of learnable transformations and then embedded

2172

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 47, NO. 3, MARCH 2025

Fig. 1. NeuTraL AD is an end-to-end procedure for self-supervised anomaly detection with learnable neural transformations Tk (·) : X → Z. Each sample is
transformed by a set of learned transformations and then embedded into a semantic space. The neural transformations are trained jointly on a contrastive objective
(3), which is also used to score anomalies.

into a semantic space such that (1) all transformed embeddings
preserve some semantic information about the input sample,
while (2) all transformations remain distinct from another. As
follows, we motivate NeuTraL AD’s loss function and its usage
in anomaly scoring.
1) Loss Function: A key ingredient of NeuTraL AD is a
new loss function that we call “Deterministic Contrastive Loss”
(DCL), explained below. This loss is constructed such as to
encourage the transformations to learn salient features of the
training data (which is assumed to belong to the normal class).
The DCL encourages each transformed embedding to be similar
to the reference embedding while encouraging it to be dissimilar
from other transformed embeddings of the same sample. We
define the similarity function of two embeddings a, b ∈ Z as
h(a, b) = exp(sim(a, b)/τ ), sim(a, b) := a b/ab, (2)
T

where τ denotes a temperature parameter. Unless mentioned
otherwise, we work with cosine similarity as sim(a, b). By
plugging K + 1 transformations and averaging over all data
samples, DCL is defined using the similarity function h as
1 
l(xi ) with
N i=1
N

L=

l(x) := −

K

k=1

log 

h(Tk (x), T0 (x))
.
Tl ∈T \{Tk } h(Tk (x), Tl (x))

(3)

Intuitively, the term in the nominator pulls the transformed
embeddings close to the reference embedding. This encourages
the transformed embeddings to preserve relevant semantic information of the reference embedding. The denominator pushes all
transformed embeddings away from each other, thereby encouraging diverse transformations. We empirically demonstrate that
the DCL manages to balance these two competing objectives
in an ablation in Section III-B4. A detailed explanation on the
trade-off between the loss terms can be found in Appendix A.4,
available online.
2) Optimization: The parameters of all transformations
θ0,...,K are optimized jointly with stochastic gradient descent or
∗
its variants (e.g., Adam [38]). The optimal parameters θ0,...,K

are computed by minimizing (3) on the training samples as
∗
θ0,...,K

= argmin −
θ0,...,K

N 
K

i=1 k=1

log 

h(Tk (xi ), T0 (xi ))
. (4)
Tl ∈T \{Tk } h(Tk (xi ), Tl (xi ))

This training objective leads to neural transformations that produce diverse views of each sample. Next, we describe how it is
used to detect anomalies.
3) Score Function: One advantage of our approach over
other methods is that our loss function is also our anomaly score.
We define an anomaly score s(x) as
s(x) := l(x).

(5)

By minimizing the DCL (3), we minimize the score for training
examples (inliers). The transformations learn to highlight salient
features of the data such that a low loss can be achieved. After
training, samples from the normal class have a low anomaly
score, while anomalies are handled less well by the model and
thus have a high score. The higher the anomaly score, the more
likely that a sample is an anomaly. Unlike most other contrastive
losses in representation learning [15], [28] and image anomaly
detection [74], [75], the “negative samples” are not drawn from a
noise distribution (e.g., other samples in the minibatch) but constructed deterministically from x in our loss and score function.
Dependence on the minibatch for negative samples would need
to be accounted for at test time. Drawing negative samples from
the test data is biased, and using the training data is infeasible
in practice. In contrast, the deterministic nature of (5) makes it
a simple choice for anomaly detection.
This concludes the proposed method NeuTraL AD, an endto-end procedure for transformation learning and anomaly detection. The detailed training process and test process of NeuTraL AD are in Algorithm 1. We stress that it is simple and
effective without the need of any additional regularization.
Qiu et al. [60] provide several theoretical arguments why
NeuTraL AD is better suited for transformation learning than
alternative loss functions. The theorems in Qiu et al. [60] which
are included with proofs in Appendix A, available online state

QIU et al.: SELF-SUPERVISED ANOMALY DETECTION WITH NEURAL TRANSFORMATIONS

Algorithm 1: Algorithm of NeuTraL AD.

that optimizing certain existing losses for self-supervised learning w.r.t. the transformations leads to trivial edge-cases, while
these edge-cases are not optimal under the DCL objective. It
follows, that the DCL does not produce these trivial edge cases
and is suited for transformation learning and anomaly detection.
Next, we describe how it relates to one-class classification.
C. Connection to One-Class Classification
One of the most influential deep anomaly detection methods is
deep OCC due to its simplicity and applicability to various types
of data [26], [44], [64]. Below we explore how NeuTraL AD is
connected to deep OCC. We show that NeuTraL AD can be
interpreted as a generalization of deep OCC. We also discuss
why NeuTraL AD is more powerful and more flexible than deep
OCC.
The main idea of deep OCC [64] is to use a parametrized
function (e.g., neural network) T (·) : X → Z to map input data
into a latent space Z. Every input datum xi is mapped as close
as possible to the same point c ∈ Z termed “the center”. The
loss function, also used for scoring anomalies, is
1 
||T (xi ) − c||22 .
N i=1
N

LOCC :=

(6)

The center has to be fixed in advance to avoid a trivial solution [64] and is typically set to the mean of the embeddings
obtained by an initial forward pass.
We can specialize DCL so that it has a similar form to LOCC . To
this end, we set the similarity function to the negative squared
euclidean distance, sim(a, b) := −||a − b||22 . This results in a
multi-view generalization of deep OCC involving multiple mappings Tk (·) : X → Z,
τ 
exp(−||Tk (xi ) − T0 (xi )||22 /τ )
log
N i=1
Zk,i
N

LMOCC := −

K

k=1

1 
||Tk (xi ) − T0 (xi )||22 + τ log Zk,i ,
N i=1
k=1

where Zk,i =
exp(−||Tk (xi ) − Tl (xi )||22 /τ ). (7)
N

K

=

Tl ∈T \{Tk }

2173

After rearranging the loss terms, its connection to deep OCC
becomes apparent. LMOCC ties together K OCC-type losses and
a regularization term. Instead of a fixed center c, the one-class
terms now have datapoint-dependent centers T0 (xi ). There are
multiple embeddings Tk (xi ) of each data point, and the regularizer log Zk,i prevents all embeddings from being the same.
For K = 1 and removing log Zk,i (or sending τ → 0), LMOCC
is equivalent to LOCC when T0 (x) is replaced by a constant,
independent of xi .
Discussion. We empirically find that LMOCC is more powerful
than LOCC (see Section III), which could be explained as follows.
First, compared to deep OCC, NeuTraL AD learns to extract
multiple, different features for anomaly detection (as opposed
to only one feature) by including multiple learnable views. All
extracted features are enforced to be diverse by the regularization
term. Second, T0 (x) serves as a datapoint-dependent center.
Compared with the fixed center c in LOCC , T0 (x) is more flexible
since it can be optimized jointly with the other parameters.
T0 (x) is also more informative since it preserves instance-level
information beyond the common factors of variation in the
dataset at large. Interestingly, the DCL does not couple any data
points explicitly, while LOCC couples the data points by pulling
them to a shared center c. NeuTraL AD seeks to find “intrinsic”
features within learnable views that characterize the normality of
data. By measuring the similarity of each view/feature with the
reference embedding T0 (x), NeuTraL AD detects the anomalies.
Next, we present an empirical study on five application domains to show the benefit of NeuTraL AD over state-of-the-art
(deep) anomaly detection methods.

III. APPLICATIONS
NeuTraL AD is applicable to many application domains: it can
be used to detect abnormal time series, it is applicable to anomaly
detection on tabular data, and it can be applied to graphs. The
advantages of NeuTraL AD include that it outperforms other
deep anomaly detection methods (as our experimental results in
this section will show) and that it does not require hand-crafted
data augmentation schemes for specialized domains. Since the
neural transformations are learned together with the other architecture components, they automatically lead to an appropriate
data augmentation scheme. In fact, since the transformations do
not need to be hand-crafted, they can even be applied to data
representations that are not easily accessible to human intuition,
such as image features that are extracted from an image using
a pretrained neural network, or to word embeddings from a
language model. This allows us to use NeuTraL AD to also
perform anomaly detection on images and on text.
In this section, we present the following applications of NeuTraL AD:
1) Section III-B: Time-series anomaly detection. We evaluate
NeuTraL AD on identifying whole abnormal sequences.
We find that it can effectively find anomalies in audio
signals, health care signals, as well as motion signals.
2) Section III-C: Anomaly detection on visual data. We study
NeuTraL AD on raw images and image features.

2174

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 47, NO. 3, MARCH 2025

3) Section III-D: Anomaly detection on tabular data. We
find that NeuTraL AD is the most effective method for
detecting anomalies in four different datasets from the
medical and cyber security domains.
4) Section III-E: Anomaly detection on text. We build NeuTraL AD on word embeddings to detect whole abnormal
sentences in the Reuters dataset.
5) Section III-F: Graph-level anomaly detection. We assess
how well NeuTraL AD detects whole abnormal graphs in
six datasets from bioinformatics, molecular, and socialnetworks domains.
For each application, we specify the choice of the neural
transformations Tk (·) and the similarity function sim(a, b) included in the DCL. We present an extensive empirical evaluation
in comparison with other successful approaches for anomaly
detection and discuss the results and their implications.
A. Evaluation Protocol
An anomaly detection method is useful if it is good at detecting anomalies in unseen test data. To test this, we follow
the standard evaluation protocol for anomaly detection in the
literature e.g., [1], [4], [9], [18], [25], [31], [37], [58], [64], [65],
[74], [75], [80]. Since in many domains it is hard to find labeled
test sets for anomaly detection, a common approach for setting
up an evaluation pipeline is to repurpose classification datasets.
We consider two such evaluation protocols: the standard ‘one-vsrest’ and the more challenging ‘n-vs-rest’ evaluation protocol.
Both settings turn a classification dataset into a quantifiable
anomaly detection benchmark.
a) One-vs-Rest: This evaluation setup has been used in
virtually all recent papers on deep anomaly detection published
at top-tier venues e.g., [1], [4], [9], [18], [25], [31], [37], [58],
[64], [65], [74], [75], [80]. For ‘one-vs.-rest’, the dataset is split
by the N class labels, creating N one-class classification task, in
each of which one class is considered normal, and only samples
drawn from this class are used as training data. All other classes
are considered abnormal. The test and validation sets contain
samples from all classes including the normal class. The samples
from the other classes should be detected as anomalies. By
iterating over the classes and changing which class is considered
normal, we obtain N separate anomaly detection tasks for
evaluation.
b) N-vs-rest: An alternative evaluation protocol we also
consider follows the insight that it is more realistic in practice
that the “normal distribution” is more diverse than a single
class (i.e., it is more realistic that it contains multiple classes,
Deecke et al. [2], [19]). So we also evaluate methods on the
more challenging n-vs.-rest protocol, where n classes (for 1 <
n < N ) are treated as normal, and the remaining classes provide
the anomalies in the test and validation set. By increasing the
variability of what is considered normal data, anomaly detection
becomes more challenging.

time series but equally important in practice. For example, one
might want to detect abnormal sound or find production quality
issues by detecting abnormal sensor measurements recorded
over the duration of producing a batch. Other applications
include sports and health monitoring; e.g., finding abnormal
movement patterns during sports can be indicative of fatigue
or injury.
We first present the datasets and baselines used to study NeuTraL AD. We then present the implementation details and finally
describe the empirical results. We find that NeuTraL AD learns
meaningful and diverse transformations and detects anomalous
time series successfully.
1) Datasets and Baselines. Time Series Datasets: We select
datasets from various domains. The datasets come from the UEA
multivariate time series classification archive1 [7]. We evaluate
NeuTraL AD on them with both one-vs-rest setting and n-vs-rest
setting.
r Spoken Arabic Digits (SAD): Sound of ten Arabic digits,
spoken by 88 speakers. The samples are stored as 13 Mel
Frequency Cepstral Coefficients. We select sequences with
the length between 20 and 50 and get a dataset of 7824
samples. The sequences that are shorter than 50 are zero
padded to have the length of 50.
r Naval Air Training and Operating Procedures Standardization (NATOPS): The data is from a motion detection
competition of various movement patterns used to control
planes in naval air training. The data has six classes of
distinct actions. The dataset has 360 samples, each being
a sequence of x, y, z coordinates for eight body parts of
length 51.
r Character Trajectories (CT): The data consists of 2858
character samples from 20 classes. Each instance is a
3-dimensional pen tip velocity trajectory. The data is truncated to the length of the shortest, which is 182.
r Epilepsy (EPSY): The data was generated with healthy
participants simulating four different activities: walking,
running, sawing with a saw, and seizure mimicking whilst
seated. The dataset has 275 samples, each being a 3dimensional sequence of length 203.
r Racket Sports (RS): The data is a record of university students playing badminton or squash. The data records the x,
y, z coordinates for both the gyroscope and accelerometer.
Sport and stroke types separate the data into four classes.
The dataset has 303 samples, each being a 6-dimensional
sequence with a length of 30.
Time Series Baselines: We study NeuTraL AD in comparison
to unsupervised and self-supervised anomaly detection methods.
They include three anomaly detection baselines: The One-Class
Support Vector Machine (OCSVM) [48], Isolation Forest (IF)
[43], a tree-based model which aims to isolate anomalies, and
Local Outlier Factor (LOF) [11], which uses density estimation
with K-Nearest Neighbor (KNN).

B. Anomaly Detection on Time Series
Our goal is to detect abnormal time series on a whole-sequence
level. This is a different set-up than anomaly detection within

1 We selected datasets on which supervised multi-class classification methods
achieve strong results [68]. Only datasets with separable classes can be repurposed for anomaly detection.

QIU et al.: SELF-SUPERVISED ANOMALY DETECTION WITH NEURAL TRANSFORMATIONS

Next, we include two deep anomaly detection methods, Deep
Support Vector Data Description (deep SVDD) [64], which fits
a one-class classification in the feature space of a neural net,
and Deep Autoencoding Gaussian Mixture Model (DAGMM)
[93], which estimates the density in the latent space of an
autoencoder. We also include two baselines specifically designed for time series data: The RNN-Based Model
 (RNN)
directly models the data distribution p(x1:T ) = p(xt |x<t )
and uses the log-likelihood as the anomaly score. LSTM-Based
Encoder-Decoder (LSTM-ED) [47] is an encoder-decoder
time series model where the anomaly score is based on the
reconstruction error.
Finally, We choose two self-supervised baselines, which are
technically also deep anomaly detection methods, deep support vector data description (deep SVDD) [9] is a distancebased classification method based on random affine transformations. Golan and El-Yaniv [25] is a softmax-based classification
method based on hand-crafted transformations, which show impressive performance on images. We adopt their pipeline to time
series here by crafting specific time series transformations (fixed
Ts). Their implementation details are provided in Appendix A,
available online.
2) Neural Transformation Learning on Time Series: We consider a dataset of time series x ∈ Rd×l , where d is the data
dimension and l is the time series length. T0 is modeled by
a composition of an identity transformation and an encoder
f . The transformations Tk with k ∈ {1, . . . , K} are modeled
by composing transformation functions φk with the shared encoder f . We consider two parametrizations of the transformation
function φk : residual φk (x) := Mk (x) + x with Mk (x) ∈ Rd ,
and multiplicative φk (x) := Mk (x) x with Mk (x) ∈ (0, 1)d .
Both Mk and the encoder f are modeled by convolutional neural
networks. In the embedding space, we define the similarity
function as the cosine similarity sim(a, b) := aT b/ab.
Implementation Details: Mk is a neural network that consists
of one 1d convolutional layer on the bottom, a stack of three
residual blocks of 1d convolutional layers with affine-free instance normalization layers and ReLU activations, as well as
one 1d convolutional layer on the top. All bias terms in the
network are fixed as zero. The network of the encoder f consists
of several residual blocks of 1d convolutional layers with a
hidden dimension of 32, as well as one final linear layer to extract
the embeddings. The number of residual blocks depends on the
data dimension. Specifically, we use four residual blocks in the
encoder for RS, five residual blocks for SAD and NATOPS,
seven residual blocks for CT and Epilepsy (EPSY). The output
dimensions of the encoders are 32 for SAD, 128 for EPSY, and
64 for others. On all time series datasets, we set the number of
transformations K = 11.
3) Empirical Results: The results of NeuTraL AD in comparison to the baselines on time series datasets from various
fields are reported in Table II. NeuTraL AD raises the detection
accuracy in terms of AUC by 7.2% on average. NeuTraL AD
outperforms all shallow baselines in all experiments and outperforms the deep learning baselines in 4 out of 5 experiments. Only
on the RS data, it is outperformed by transformation prediction
with fixed transformations, which we designed to understand

2175

TABLE II
AVERAGE AUCS (%) WITH STANDARD DEVIATION FOR ONE-VS-REST
ANOMALY DETECTION ON TIME SERIES DATASETS

Fig. 2. 3D visualizations (projected using PCA) of different views in the data
space and the embedding space of the encoder. The original samples (blue) from
the SAD dataset and the different views created by the neural transformations
(one color per transformation type) cluster in the data space [Fig. 2(a) and (c)]
and in the embedding space [Fig. 2(b) and (d)]. The crisp separation of the
different transformations of held-out inliers [Fig. 2(b)] in contrast to the overlap
between transformed anomalies [Fig. 2(d)] visualizes how NeuTraL AD is able
to detect anomalies.

the value of learning transformations with NeuTraL AD vs using
hand-crafted transformations. The results confirm that designing
the transformations only succeeds sometimes, whereas with
NeuTraL AD we can learn the appropriate transformations. The
learned transformations also give NeuTraL AD a competitive
advantage over the other self-supervised baseline GOAD which
uses random affine transformations. The performance of the
traditional anomaly detection baselines hints at the difficulty
of each anomaly detection task; the traditional methods perform
well on SAD and CT, but perform worse than the deep learning
based methods on other data.
What does NeuTraL AD learn? For visualization purposes,
we train NeuTraL AD with the learnable transformations on
the SAD data. Fig. 2 shows the structure in the data space
X and the embedding space of the encoder Z after training.
Held-out data samples (blue) are transformed by each of the
learned transformations with the multiplicative transformation
function φk (x) = Mk (x) x to produce K = 4 different views
of each sample (the transformations are color-coded by the other
colors). Projection to three principal components with PCA
allows for visualization in 3D. In Fig. 2(a) and (c), we can
see that the transformations already cluster together in the data
space, but with the help of the encoder, the different views of

2176

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 47, NO. 3, MARCH 2025

TABLE III
AVERAGE AUCS (%) WITH STANDARD DEVIATION FOR n-VS-REST
(n = N − 1) ANOMALY DETECTION ON TIME SERIES DATASETS

Fig. 3. Heat maps of four learned masks M1:4 for SAD spectrograms. The
dark horizontal lines indicate where M1 and M2 mask out frequency bands
almost entirely, while the bright spot in the middle left part of M4 indicates that
this mask brings the intermediate frequencies in the first half of the recording
into focus. NeuTraL AD learns dissimilar transformations.

Fig. 4. AUCs of n-vs-all experiments on time series datasets SAD and
NATOPS with error bars. NeuTraL AD (ours) outperforms all baselines on
NATOPS and all deep learning baselines on SAD. LOF, a method based on
k-nearest neighbors, outperforms NeuTraL AD, when n > 3 on SAD. NeuTraL AD is more robust to the variability of inliers than deep learning baselines.

inliers are separated from each other (Fig. 2(b)). In comparison,
the anomalies and their transformations are less structured in Z
(Fig. 2(d)), visually explaining why they incur a higher anomaly
score and can be detected as anomalies.
The learned masks M1:4 (x) of one inlier x are visualized
in Fig. 3. We can see that the four masks are dissimilar from
each other and have learned to focus on different aspects of
the spectrogram. The masks take values between 0 and 1, with
dark areas corresponding to values close to 0 that are zeroed out
by the masks, while light colors correspond to the areas of the
spectrogram that are not masked out. Interestingly, in M1 , M2 ,
and M3 , we can see ‘black lines’ where they mask out entire
frequency bands at least for part of the sequence. In contrast,
M4 has a bright spot in the middle left part of the spectrogram;
it creates views that focus on the content of the intermediate
frequencies in the first half of the recording.
How do the methods cope with an increased variability of
inliers? To study this empirically, we increase the number of
classes n considered to be inliers. We test all methods on SAD
and NATOPS under the n-vs-rest setting with varying n consecutive classes. From Fig. 4 we can observe that the performance
of all methods drops as the number of classes included in the
normal data increases. This shows that the increased variance in
the nominal data makes the task more challenging. NeuTraL AD
outperforms all baselines on NATOPS and all deep-learning
baselines on SAD. It is interesting that LOF, a method based on
KNN, performs better than our method (and all other baselines)
on SAD when n is larger than three.

We include quantitative results for n = N − 1 under the nvs-rest setting for all time series datasets, where only one class
is considered abnormal, and the remaining N − 1 classes are
normal. As shown in Table III, NeuTraL AD raises the detection
AUC by 7.9% on average and outperforms other deep learning
methods on 4 out of 5 datasets. On RS, it is just outperformed
by transformation prediction with hand-crafted transformations.
The traditional method LOF performs better than deep learning
methods on CT and SAD.
4) Ablation Study on DCL Loss Terms: We investigate in
an ablation study how the DCL manages the trade-off between
semantics and diversity discussed in Section II-B1 (for a detailed
discussion see also Appendix A.4, available online). This ablation also demonstrates empirically that when it comes to learning
transformations for anomaly detection, the DCL is better suited
than the contrastive loss or the classification loss. To study
the trade-off between semantics and diversity we introduce a
hyperparameter β to adjust the relative importance of the two
terms in the DCL:
lk (x) = − log h(Tk (x), T0 (x))

+ β log
h (Tk (x), Tl (x)) .
Tl ∈T \{Tk }

In our default DCL (β = 1), the weight between the two objectives is balanced. To analyze the effect of this weighting, we
perform an ablation study with β = 0.1 and β = 10. A lower β
(e.g., 0.1) reduces the emphasis on the diversity objective, while
a higher β (e.g., 10) reduces the emphasis on aligning with the
original data.
To evaluate these objectives, we introduce the following metrics:
r Semantics 1 K h(Tk (x), T0 (x)):2 This score meak=1
K
sures how similar the transformed embeddings are to the
embedding of the original
K data.

1
1
r Diversity
Tl ∈T \{Tk ,T0 } h(Tk (x),Tl (x)) ,
k=1
K(K−1)
which measures the dissimilarity between the transformed
embeddings. A higher score indicates greater diversity
among the transformations.
r Semantics × Diversity: a product of semantics and diversity scores evaluates the balance between the two
objectives. A high product value indicates that both objectives are well balanced.
2 h(·) is the exponential function of the cosine similarity

QIU et al.: SELF-SUPERVISED ANOMALY DETECTION WITH NEURAL TRANSFORMATIONS

2177

TABLE IV
AN ABLATION STUDY COMPARING THE CONTRASTIVE LOSS, THE CLASSIFICATION LOSS, AND THE DCL WITH VARIOUS WEIGHTS BETWEEN THE TWO LOG
TERMS IN THE LOSS ON LEARNING TRANSFORMATIONS FOR ANOMALY DETECTION

We fit this loss to the arabic digits in the SAD data. As shown in
Table IV, our default DCL (β = 1) achieves the highest product
of the semantics and diversity scores, indicating the best balance
between these objectives. In contrast, the contrastive loss learns
transformations (with a semantics score of exp(1) = 2.72 and
a diversity score of exp(−1) = 0.37) that are perfectly aligned
with the original data but sacrifices diversity, the classification
loss learns transformations that are diverse but share much less
relevant information with original data than others. Similarly, the
DCL (β = 0.1) achieves a higher semantics score but sacrifices
diversity, the DCL (β = 10) achieves a higher diversity score
but compromises on semantics. This empirical result aligns
with our theoretical analysis, confirming that the default DCL
(β = 1) best balances the objectives of aligning with the original
data while maintaining diversity among transformed views,
ultimately resulting in superior anomaly detection performance.
C. Anomaly Detection for Image Data
Anomaly detection on images is important for many machine
learning applications and has received a lot of attention in the
last few years. Recent work [10], [63], [74] employs shallow
anomaly detectors (KNN or OCSVM) upon the image features
obtained from a pretrained model often achieving better detection accuracy than self-supervised anomaly detection on raw
images. This raises the question of how to apply self-supervised
anomaly detection to image features which might lead to an additional performance boost. However, applying self-supervised
anomaly detection methods (such as Golan and El-Yaniv [9],
[25], [82]) to image features is difficult since all of them rely
on hand-crafted data augmentations designed for raw images.
Hand-crafting transformations requires intuition about image
invariances (e.g., humans still recognize dogs in rotated images
of dogs). These intuitions do not readily generalize to image
features. In contrast, NeuTraL AD learns transformations and
hence requires no intuition, enabling a direct deployment on
image features.
In this Section, we first present how to apply neural transformations to raw images and image features. We then show
that when applying NeuTraL AD on image features, we
learn meaningful and semantically diverse transformations and
achieve competitive anomaly detection accuracy. We finally
compare NeuTraL AD to strong baselines on large-scale outof-distribution benchmarks.
1) Neural Transformation Learning for Image Data: NeuTraL AD learns data-dependent transformations automatically.
Therefore, we can apply neural transformations to raw images or

features obtained from existing pretrained feature extractors. For
both variants, we define the similarity function as the cosine similarity sim(a, b) := aT b/ab, set the temperature τ = 0.1.
T0 is modeled by a composition of an identity transformation
and an encoder f . The transformation Tk with k ∈ {1, . . . , K}
is modeled by a composition of a transformation function φk
and the shared encoder f .
Neural Transformation Learning on Raw Images (NeuTral-I):
We consider a dataset of images x. The transformation function
is parametrized multiplicatively as φk (x) = x Mk (x), where
Mk (x) is an attention mask (with values between 0 and 1) and
the multiplication is applied element-wise. Mk is modeled by
a residual convolutional neural network with affine-free batch
normalization layers and a final sigmoid activation. All bias
terms in the network are fixed as zero. We set the number
of neural transformations K = 15 for all image datasets. As
in Bergman and Hoshen [9], we use a ResNet architecture as
the encoder f . Its output dimension is 64, and its parameters
are learned together with the parameters of the transformation
functions.
Neural Transformation Learning on Image Features
(NeuTral-F): We process images with a pretrained model and
obtain a dataset of image features x as in Bergman et al.
[10]. We consider two parametrizations of the transformation
function: forward φk (x) := Mk (x) and multiplicative φk (x) :=
Mk (x) x. Mk (x) is computed by three bias-free linear layers
with affine-free batch normalization layers and ReLU activations. A sigmoid activation is applied on the final layer of Mk
when using the multiplicative parametrization. We set the number of neural transformations K = 15. The encoder f is modeled
by two linear layers with an intermediate ReLU activation. The
output dimension of the encoder is 256.
2) Anomaly Detection Experiments. Anomaly detection
datasets: We study three image datasets, F-MINST, CIFAR-10,
and CIFAR-100, which are commonly used in prior works e.g.,
[10], [25], [63], [64], [74]. For CIFAR-100, we use 20 superclass labels in the experiments. On F-MNIST, we study the
one-vs-rest setting. On the more challenging datasets, CIFAR-10
and CIFAR-100, we consider both the one-vs-rest setting and
n-vs-rest setting with n = N − 1.
Anomaly detection baselines: We compare NeuTraL AD with
modern baselines based on different techniques. We include
one deep anomaly detection baseline, deep SVDD [64], which
learns a compact boundary in the embedding space to detect
anomalies. As self-supervised baselines, we include GeometricTransformation Classification (GEOM) [25] which designs an

2178

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 47, NO. 3, MARCH 2025

TABLE V
AVERAGE AUCS (%) WITH STANDARD DEVIATIONS ON IMAGE DATASETS

auxiliary transformation classification task for anomaly detection, and CSI which relies on contrastive learning. We also
include three baselines, which build anomaly detectors upon
image features. They are Distribution-Augmented Contrastive
Learning (Contra-DA) [74], which proposed to use traditional
anomaly detectors (e.g., OCSVM) on features from an encoder
pretrained with a contrastive loss, Deep Nearest-Neighbors
(DN2) [10] using a KNN based detector on features from a
ResNet pretrained on ImageNet, and a state-of-the-art method
PANDA [63], which improves over DN2 by finetuning the
pretrained ResNet.
Empirical results: The results on image datasets with the
one-vs-rest setting are reported in Table V, where the results of
baselines are taken from the original papers. When neural transformations are applied to raw images, NeuTraL-I performs better
than deep SVDD but worse than GEOM using hand-crafted
transformations. It turns out that learning good transformations
from the noisy raw images is still hard, and the learned transformations are not competitive with transformations selected by
human experts. One reason for the poor performance on raw images could be the learned transformations affect mostly low-level
features and do not interact with higher-level semantic features,
as would be desired for a strong self-supervision task. This
motivates applying NeuTraL AD to pretrained image features.
NeuTraL-F outperforms DN2 that uses the same pretrained
feature extractor, and all baselines that have no access to a
feature extractor pretrained on ImageNet. PANDA outperforms
NeuTraL-F using the same pretrained feature extractor but also
requires a careful finetuning of the large ResNet model and
has a risk of performance degradation caused by catastrophic
forgetting [63]. Additional stronger results of NeuTraL-F using
the other pretrained feature extractor are provided in Appendix
B, available online. Moreover, using PANDA at test-time is
expensive; the KNN-based detection is slower than the forwardpass of the other methods in Table V and it requires storing
the training data for test time. Our method achieves the highest
performance among all methods that do not suffer from this
drawback. When using PANDA with a more efficient distance
for detection, the results will be 2% lower (e.g., CIFAR-10: from
96.2% to 94.2%) [63] and then outperformed by NeuTraL-F
(95.3%). It is very hard even for human experts to design good
transformations on the feature vectors, while NeuTraL AD can
learn them from data automatically. NeuTraL AD offers a convenient way to do self-supervised learning on the image features
to utilize the powerful existing pretrained models continuously
being developed and improved by the community.
What do the transformed features look like?
For an interpretable visualization of the transformed features
learned by NeuTraL-F, we invert them back to the image space

by seeking an image that best matches the source representation [46]. From the resulting images shown in the first row
of Fig. 5, we can see that the transformations disrupt different local regions and textures of the image but preserve the
global shape of the object. The learned local disruptions preserve global semantics and vary, thereby satisfying the diversity
requirement.
Furthermore, we analyze the semantic information contained
in the transformed features by checking the class prediction of
a downstream classifier trained on the raw features and ground
truth class labels. In the second row of Fig. 5 we can see that the
predictions given transformed features (blue) perfectly match
the predictions given the raw features (orange).3 This confirms
the claim that the learned transformations manipulate the image
without changing the global semantics as encoded by the class
label.
How do the methods cope with an increased variability
of inliers? To study this, we consider the n-vs-rest setting
with n = N − 1. As shown in Table VII, NeuTraL-F (with
forward parametrization of the transformations) outperforms
baselines on CIFAR-10 but performs worse than DN2 on
CIFAR-100. This is consistent with the results on time series in Table III, where the KNN-based methods (DN2 in vision and LOF in sequences) have an advantage in anomaly
detection when the normal distribution contains multiple
modes.
3) Out-of-Distribution (OOD) Experiments. OOD datasets:
We follow the experiment setup of Li et al. [40] and test the
methods on CIFAR-10, CIFAR-100, and ImageNet-30. When
assuming CIFAR-10 is in distribution, we consider CIFAR-100,
SVHN, and LSUN as OOD datasets. For CIFAR-100, OOD
samples are from CIFAR-10, SVHN, and LSUN. For ImageNet30, OOD samples are from Stanford Dogs, Places365, Oxford
Flowers, Oxford Pets, Food101, Caltech256, and Describable
Textures Dataset (DTD).
OOD baselines: We compare NeuTraL AD with four recent
strong OOD baselines. They are three contrastive learning-based
methods including SupContrast [35], CSI [75], SSD+ [71], and
MOOD [40] which uses representations from a masked image
model pretrained and finetuned on ImageNet.
Empirical rqesults: We evaluate NeuTraL-F for OOD detection following the setup in Li et al. [40] and report the
results in Table VI. NeuTraL-F is equipped with the image
features from the finetuned masked image modeling models in
MOOD [40]. As shown in Table VI, NeuTraL-F improves over
the SOTA baseline MOOD on both CIFAR-10 and CIFAR-100.

3 The transformed features have not been used to train the classifier.

QIU et al.: SELF-SUPERVISED ANOMALY DETECTION WITH NEURAL TRANSFORMATIONS

2179

Fig. 5. Visualization and semantics checking examples from CIFAR-10. By inverting the original and transformed image features, we visualize the features in
the image space in the first row. In the second row, we plot their class prediction results from a downstream classifier. The transformed features are diverse and still
preserve the semantic information.
TABLE VI
AUCS (%) FOR MULTI-CLASS OOD DETECTION ON CIFAR-10, CIFAR-100, IMAGENET-30

TABLE VII
AVERAGE AUCS (%) WITH STANDARD DEVIATIONS ON CIFAR-10 AND
CIFAR-100 UNDER n-VS-REST SETTING WITH n = N − 1

NeuTraL-F also achieves decent and comparable results on the
large-scale ImageNet-30 benchmark.
D. Anomaly Detection on Tabular Data
Tabular data is another important application area of anomaly
detection. For example, many types of health data come in
tabular form. To unleash the power of self-supervised anomaly
detection for these domains, Bergman and Hoshen [9] suggest
using random affine transformation. Here we study the benefit of
learning the transformations on tabular data with NeuTraL AD.
In this Section, we first present the datasets and baselines we
use. We then present specific architecture choices and implementation details and finally describe the empirical results. We
find that NeuTraL AD raises the detection accuracy by 2.9% on
average in terms of F1-score.
1) Datasets and Baselines: Tabular Datasets. We base our
empirical study of tabular anomaly detection on previous

work [9], [93] and follow their choice of datasets as well as
their precedent of reporting results in terms of F1-scores. The
datasets include the small-scale medical datasets Arrhythmia
and Thyroid as well as the large-scale cyber intrusion detection datasets KDD and KDDRev. We follow the configuration
of Bergman and Hoshen [9] to train all models on half of the
normal data and test on the rest of the normal data as well as
the anomalies.
r Arrhythmia: A cardiology dataset from the UCI repository
contains 274 continuous and 5 categorical attributes.
r Thyroid: A medical dataset from the UCI repository contains attributes related to hyperthyroid diagnosis.
r KDD: KDDCUP99 10 percent dataset from the UCI repository contains 34 continuous and 7 categorical attributes.
r KDDRev: It is derived from the KDDCUP99 10 percent
dataset. The non-attack samples are considered normal,
and attack samples are considered abnormal.
On these 4 datasets we use the same preprocessing steps
as Bergman and Hoshen [9].
Tabular Baselines: We compare NeuTraL AD to shallow
anomaly detection baselines, including OCSVM [48], IF [43],
and LOF [11], and to the deep anomaly detection methods deep
SVDD [64], DAGMM [93], GOAD [9], and Deep Robust OneClass Classification (DROCC) [26]. The results of OCSVM,

2180

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 47, NO. 3, MARCH 2025

TABLE VIII
F1-SCORES (%) WITH STANDARD DEVIATION FOR ANOMALY DETECTION ON
TABULAR DATASETS (CHOICE OF F1-SCORE CONSISTENT WITH PRIOR WORK)

LOF, DAGMM, and GOAD are from Bergman and Hoshen [9].
We obtained the results for deep SVDD and DROCC using the
code with the respective publications.
2) Neural Transformation Learning on Tabular Data: We
consider a dataset of tabular data x ∈ Rd . T0 is modeled by
a composition of an identity transformation and an encoder f .
The transformations Tk with k ∈ {1, . . . , K} are modeled by a
composition of a transformation function φk and the shared encoder f . We consider two parametrizations of the transformation
function φk : residual φk (x) := Mk (x) + x with Mk (x) ∈ Rd ,
and multiplicative φk (x) := Mk (x) x with Mk (x) ∈ (0, 1)d .
Mk and the encoder f are both modeled by feed-forward neural
networks. In the embedding space, we define the similarity
function as the cosine similarity sim(a, b) := aT b/ab.
Implementation Details: The neural network of Mk consists
of two bias-free linear layers with an intermediate ReLU activation. When using the multiplicative parametrization, it has
a sigmoid activation on the final layer. We use the residual
parametrization for the neural transformations on Thyroid and
Arrhythmia, and use the multiplicative parametrization on KDDCUP, and KDDCUP-Rev. The neural network of the encoder
f consists of five bias-free linear layers with ReLU activations.
The output dimensions of the encoder are 24 for Thyroid and
32 for the other datasets. We set the number of neural transformations K = 11 and the temperature τ = 0.1 on all tabular
datasets.
3) Empirical Results: In line with prior work, we use the
averaged F1-score (%) with standard deviation as the evaluation metric and report the results in Table VIII. The results of
OCSVM, LOF, DAGMM, and GOAD are taken from [9]. For
deep SVDD and DROCC, we run their official implementations
and report the results. NeuTraL AD outperforms all baselines
on all tabular datasets. In particular, NeuTraL AD raises the
F1-score on Arrhythmia by 3.7% and on Thyroid by 2.4%.
Compared with the self-supervised baseline GOAD with random
affine transformations, the neural transformations learned from
data lead to better detection accuracy. In addition, we find that
NeuTraL AD needs fewer transformations than GOAD. On the
medical datasets, for example, GOAD uses 256 transformations, while NeuTraL AD achieves superior performance with
only 11 transformations.
E. Anomaly Detection on Text
There are many beneficial applications of anomaly detection
on text such as detecting spam emails, fake tweets, or other

anomalous content on the web. Here we present NeuTraL AD
for text and compare it with recent approaches for sentence-level
anomaly detection.
NeuTraL AD on text uses a pre-trained language model to
preprocess the text. To create different views of each sentence,
neural transformations are then applied to the list of word
embeddings comprising each sentence. Below, we describe how
the individual word embeddings are transformed and how an
attention mechanism is used to aggregate word embeddings
to create the different views of each sentence needed for the
NeuTraL AD loss.
1) Datasets and Baselines. Text Datasets: We study NeuTraL AD on the Reuters-21578 dataset, which is commonly
used in previous text anomaly detection work [34], [48], [66].
We used the same pre-processing as in Ruff et al. [66], including
lowercasing, removing stopwords, and tokenization. As in Ruff
et al. [66], we select seven classes that have exactly one label.
They are earn, acq, crude, trade, money-fx, interest, and ship.
We evaluate NeuTraL AD on them with the one-vs-rest setting.
Text Baselines: The text anomaly detection baselines include
deep SVDD [64], which aim to encompass normal data within
a hypersphere in the embedding space, and Multi-Modal Deep
Support Vector Data Description (mSVDD) [34] which extends
the idea of deep SVDD to multiple hyperspheres. Further,
the baselines include Deep Multi-Sphere Support Vector Data
Description (DMSVDD) [23], a hard version of mSVDD, and
Context Vector Data Description (CVDD) [66], which augments
deep SVDD for text with multiple attention heads to reflect that
there are multiple normal semantic contexts for each word. All
baselines are built upon the same word embeddings. Specifically,
all embeddings are extracted using GloVe 6B [57].
2) Neural Transformation Learning on Text: NeuTraL AD
on text uses a pretrained language model to preprocess the text.
To create different views of each sentence, neural transformations are then applied to the list of word embeddings comprising
each sentence. Below, we describe how the individual word
embeddings are transformed and how an attention mechanism
is used afterwards to aggregate the word embeddings to create
the different views of each sentence needed for its loss.
As in previous work [23], [34], [66], we preprocess the data
with a language model such that each sentence x is represented
by a sequence of word embeddings x = [e1 , . . . , el ] ∈ Rd×l .
The length l of the sentences is variable from sentence to
sentence. T0 is modeled by a composition of an identity transformation and an encoder f . The transformation Tk with k ∈
{1, . . . , K} is modeled by a composition of a transformation
function φk and the shared encoder f . The transformation function φk is applied to the individual word embeddings, producing
the transformed embeddings,
xk = φk (x) = Mk (x)

x,

where Mk is a feed-forward neural network with a final sigmoid
activation. It is applied to each embedding in the sentence separately, i.e., Mk (x) = [Mk (e1 ), . . . , Mk (el )] ∈ (0, 1)d×l . After
element-wise multiplication with the word embeddings, we have
the transformed embedding xk = [Mk (e1 ) e1 , . . . , Mk (el )
el ] ∈ Rd×l . The embeddings are aggregated using attention

QIU et al.: SELF-SUPERVISED ANOMALY DETECTION WITH NEURAL TRANSFORMATIONS

TABLE IX
AVERAGE AUCS (%) WITH STANDARD DEVIATIONS ON REUTERS DATASETS

TABLE X
EXAMPLE OF WORDS WITH LARGE ATTENTION WEIGHTS FOR EACH CLASS

A(x) ∈ (0, 1)l and are then encoded. In summary,
f (xk ) = g(xk A(x))




with A(x) = sigmoid tanh xT W1 W2 ,

(8)

where W1 and W1 are learnable weights, and g is a feedforward neural network that maps the aggregated embeddings
to a low dimensional embedding space.4 In this embedding
space, we define the similarity function as the cosine similarity
sim(a, b) := aT b/ab.
Implementation Details: For Mk we use a neural network of
three bias-free linear layers of units [300,300,300] with ReLU
activations and affine-free batch normalization layers and a
sigmoid activation on the top. W1 and W1 have the shapes
of [300,300] and [300,1]. For g we use a neural network of
three bias-free linear layers of units [300,100,100] with ReLU
activations. We set the number of transformations K = 10 and
the temperature τ = 0.1.
3) Empirical Results: The anomaly detection results in terms
of average AUC (%) with standard deviation are reported in
Table IX. NeuTraL AD achieves the best detection accuracy
on 6 of 7 experimental variants. On average, NeuTraL AD
outperforms all baselines by at least 1.3% in terms of AUC.
In Table X, we record the three most relevant words (in terms of
highest attention weight A(x)) for each class. We can see that the
attention mechanism of NeuTraL AD learns to highlight words
with similar semantic content.
F. Graph-Level Anomaly Detection
Graphs offer a powerful representation for many types of
structured data, including chemical processes, molecules, financial or social networks. There is much work focused on the task
of detecting anomalous nodes and edges within a graph [5].
However, in many applications, it is much more relevant to ask
whether an entire graph is abnormal.
4 For the untransformed x, (8) becomes f (x) = g(xA(x)).

2181

In a financial network, for example, with nodes representing
individuals, businesses, and banks and the edges representing
transactions, it might be difficult to detect all criminal activity by
looking at individual nodes and edges. By using tools for graphlevel anomaly detection, we might be able to detect an entire
criminal network rather than suspicious individual entities. In
alternative healthcare applications, one might be interested in
detecting novel (anomalous) molecules whose atoms and bonds
are nodes and edges in the molecular graphs. Thus, while every
atom may be known, the molecule might be novel as a whole.
This, and many other applications, can profit from automated
methods for detecting abnormal graphs.
For applying self-supervised methods to graph-level anomaly
detection, good graph transformations are required. You et
al. [87] observe that different graph datasets require different
transformation types. For example, edge perturbation benefits
representation learning on social networks but hurts the quality of representations of molecules learned from biochemical
graph data. Here NeuTraL AD has a conceptual advantage; the
appropriate transformations are directly learned from the data.
We demonstrate that this advantage makes neural transformation learning a useful tool for graph-level anomaly detection, significantly outperforming existing methods. We use it
to analyze graphs from various important domains, including
bioinformatics, molecular data, and social networks.
1) Datasets and Baselines. Graph Datasets: We study NeuTraL AD on six graph classification datasets that are representative of three domains. They are two bioinformatics datasets: DD
and PROTEINS, two molecular datasets: NCI1 and AIDS, and
two datasets of social networks: IMDB-BINARY and REDDITBINARY. In IMDB-BINARY, node attributes are derived by
encoding the degree of each node in a one-hot vector. In
REDDIT-BINARY, node attributes are set to a constant. All
datasets are made available by Morris et al. [51].
Following the one-vs-rest evaluation setup, we create N
experimental variants for each dataset (N is the number of
classes). We use 10-fold cross-validation to estimate the model
performance. In each fold, 10% of the training set is held-out
for validation. Results are reported in terms of average AUC
(%) with standard deviation averaged over 10 folds and over all
experimental variants.
In addition, all methods are evaluated in terms of their
susceptibility to performance flip. Zhao and Akoglu [90] coined
the term “performance flip” for anomaly detection benchmarks
derived from binary classification datasets. An effective graphlevel anomaly detection method should not suffer from the
performance flip issue.
Definition 1. (Performance flip [90]:) A model suffers from
performance flip on an anomaly detection benchmark derived
from a classification dataset if it performs worse than random
on at least one experimental variant.
Graph Baselines: To build a comprehensive benchmark for
graph-level anomaly detection, we include both graph Neural
Network (GNN)-based methods and non-GNN-based methods
as baselines. Two GNN-based baselines are One-Class Graph
Isomorphism Network (OCGIN) [90], extending the idea of deep

2182

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 47, NO. 3, MARCH 2025

TABLE XI
AVERAGE AUCS (%) WITH STANDARD DEVIATIONS FOR GRAPH-LEVEL ANOMALY DETECTION ON SIX DATASETS FROM THREE DOMAINS

SVDD to graph-level anomaly detection, and Graph Transformation Prediction (GTP), a self-supervised detection baseline
proposed by us based on graph transformation prediction (see
details in Appendix B, available online).
Four non-GNN-based methods are two-stage detection methods using different feature extractors and a downstream OCSVM
[48] for anomaly detection. Two of them use unsupervised
graph embedding methods, Graph-to-Vector (Graph2Vec) [52]
or Family of Graph Spectral Distances (FGSD) [79], to extract
graph-level representations. The other two make use of graph
kernels (Weisfeiler-Leman Subtree Kernel (WLK) [73] or Propagation Kernel (PK) [53]), which measure the similarity between
graphs. Details are in Appendix B, available online.
2) Neural Transformation Learning on Graphs: We consider
a dataset of attributed graphs x. For graph data, the neural
transformations Tk are parameterized by GNNs. Each neural
transformation Tk is an individual GNN, which transforms the
graph and maps it to the embedding space.
Since graphs have varying sizes, the number of nodes can be
an informative feature for distinguishing graphs and detecting
abnormal ones. By using an appropriate GNN architecture for
the neural transformations, we can introduce a correlation between the norm of embeddings and graph size. To ensure that this
information is not lost, we use the negative euclidean distance
as the similarity function sim(a, b) := −a − b2 for the DCL.5
The resulting multi-view deep OCC loss (7) is a special case
of the DCL. In Section II-C, we discuss how it is related to
deep OCC. The results reported support the arguments that our
method is more informative and more flexible than deep OCC.
Implementation Details: We use Graph Isomorphism Networks (GINs) [85] as Tk to extract graph-level representations.
The network has 4 GIN layers, each of which includes two
bias-free linear layers with an intermediate ReLU activation.
On datasets from molecular and social-networks domains, graph
normalization [12] is applied after each GIN layer. A readout
function modeled by two bias-free linear layers with an intermediate ReLU activation and an add pooling layer is applied on each
layer to get the graph-level representation on each hierarchical
level. As in Xu et al. [86], the final graph-level representation
of dimension 128 is obtained by concatenating all layer-wise
graph-level representations. None of the transformations use
biases, except the network T0 , which adds a trainable bias term
to the final graph-level representations. On all graph datasets,
we set the number of transformations K = 5.
5 The cosine similarity only considers angles between embeddings, thereby
ignoring the information encoded in their norm.

3) Empirical Results: The anomaly detection results in terms
of average AUC (%) with standard deviation are reported in
Table XI. We can see that NeuTraL AD outperforms all baselines
on all datasets and raises the detection accuracy in terms of
AUC by 7.5% on average. NeuTraL AD improves over the
previous deep method OCGIN, which is an extension of deep
SVDD on graph-level anomaly detection, by 15.4% on average. We can empirically conclude that NeuTraL AD is more
sensitive to anomalies than OCGIN since it extracts features
from different views. The results with performance flip are
marked with a ∗ (it is preferable for a method not to suffer
from performance flip). We can see that all baselines suffer
from the performance flip issue, while NeuTraL AD is the only
model without performance flip on any of the datasets. We
provide the detailed results on both experimental variants of
bioinformatic and molecular datasets in Appendix C, available
online.
IV. RELATED WORK
Here we relate NeuTraL AD to existing work in deep anomaly
detection, self-supervised learning, and the more specific contrastive representation learning.
Deep Anomaly Detection: Recently, there has been a rapidly
growing interest in developing deep-learning approaches for
anomaly detection [67]. While deep learning—by removing the
burden of manual feature engineering for complex problems—
has brought about tremendous technological advances, its application to anomaly detection is rather recent. Related work on
deep anomaly detection includes deep autoencoder variants [16],
[59], [91], deep OCC [22], [65], [66], multi-sphere OCC [23],
[34], [66], [84], deep generative models [18], [69], and outlier
exposure [30], [39], [61].
Self-supervised anomaly detection has led to drastic improvements in detection accuracy [25], [31], [74], [75], [82]. For
images, Golan and El-Yaniv [25] and and Wang et al. [82]
augment images and learn to predict which transformation has
been applied. After training, the resulting classifier is used
for anomaly detection. An alternative approach is to train a
model with a contrastive loss to tell if two views are of the
same original image. This leads to strong representations [15],
which can be used for anomaly detection [74], [75]. For time
series anomaly detection, Zhou et al. [36], [81], [92] combine
autoencoder-based methods or deep OCC with contrastive learning based on hand-crafted data augmentations. Following the
work of Qiu et al. [60], several recent studies [13], [14], [54],
[70] integrate contrastive learning with neural transformations

QIU et al.: SELF-SUPERVISED ANOMALY DETECTION WITH NEURAL TRANSFORMATIONS

on times series. In the domain of tabular anomaly detection,
Bergman and Hoshen [9] design an auxiliary classification tasks
using random affine transformations, while ICL [72], a contemporaneous work of NeuTraL AD, proposes contrasting two complementary subsets of the tabular data. For graph-level anomaly
detection, Luo et al. [45] employ contrastive learning with two
perturbed graph encoders, while Ai et al. [3] design two types
of topology augmentations for graph-level contrastive learning.
Unlike all prior works, NeuTraL AD learns transformations that
are effective for self-supervised anomaly detection on various
data types.
Self-Supervised Learning: Self-supervised learning typically
relies on data augmentation for auxiliary tasks [20], [24],
[49], [55], [88]. The networks trained on these auxiliary tasks
(e.g., patch prediction [20], solving jigsaw-puzzles [55], crosschannel prediction [88], or rotation prediction [24]) are used
as feature extractors for downstream tasks. While many of these
methods are developed for images, Misra et al. [49] propose temporal order verification as an auxiliary task for self-supervised
learning of time series representations.
Contrastive Representation Learning: Many recent selfsupervised methods have relied on the InfoMax principle [32],
[42]. These methods are trained on the task to maximize the Mutual Information (MI) between the data and their context [56] or
between different “views” of the data [6]. Computing the mutual
information in these settings is often intractable, and various
approximation schemes and bounds have been introduced [78].
By using noise contrastive estimation [27], [28] to bound MI,
Oord et al. [56] bridge the gap between contrastive losses for
MI-based representation learning and the use of contrastive
losses in discriminative methods for representation learning [6],
[15], [21], [29], [50]. We also use a contrastive loss. But while
the contrastive loss of Chen et al. [15] (which is used for anomaly
detection of images in Sohn et al. [74], [75],) contrast two
views of the same sample with views of other samples in the
minibatch, NeuTraL AD is tasked with determining the original
version of a sample from different views of the same sample.
The dependence on only a single sample is advantageous for
scoring anomalies at test time and enables us to learn the data
transformations.
Learning Data Augmentation Schemes: The idea of learning
data augmentation schemes is not new. “AutoAugmentation”
has usually relied on composing hand-crafted data augmentations [17], [33], [41], [62], [89]. Tran et al. [77] learn Bayesian
augmentation schemes for neural networks, and Wong and
Kolter [83] learn perturbation sets for adversarial robustness.
Though their setting and approach are different, our work is
most closely related to Tamkin et al. [76], who study how to
generate views for representation learning in the framework
of Chen et al. [15]. They parametrize their “viewmakers” as
residual perturbations, which are trained adversarially to avoid
trivial solutions where the views share no semantic information
with the original sample.
NeuTraL AD falls into the area of deep, self-supervised
anomaly detection, with the core novelty of learning the transformations so that we can effectively use them for anomaly
detection on general data types.

2183

V. CONCLUSION
We propose NeuTraL AD, a self-supervised anomaly detection method with learnable transformations. The key ingredient
is a novel training objective based on a DCL, which encourages
the learned transformations to be diverse and semantically meaningful. This unleashes the power of self-supervised anomaly
detection to various data types. We show that NeuTraL AD generalizes deep OCC, leading to a more powerful and more flexible
anomaly detection method thanks to the learnable transformations. Our extensive empirical study finds that NeuTraL AD as
a unified anomaly detection method improves over many strong
baselines on various non-image data types, including time series,
tabular data, text data, and graphs, and achieves competitive
results on images.
ACKNOWLEDGMENT
The Bosch Group is carbon neutral. Administration, manufacturing and research activities do no longer leave a carbon
footprint. This also includes GPU clusters on which the experiments have been performed.
REFERENCES
[1] D. Abati, A. Porrello, S. Calderara, and R. Cucchiara, “Latent space
autoregression for novelty detection,” in Proc. IEEE Conf. Comput. Vis.
Pattern Recognit., 2019, pp. 481–490.
[2] F. Ahmed and A. Courville, “Detecting semantic anomalies,” in Proc.
AAAI Conf. Artif. Intell., 2020, pp. 3154–3162.
[3] X. Ai et al., “Graph anomaly detection at group level: A topology pattern
enhanced unsupervised approach,” 2023, arXiv:2308.01063.
[4] S. Akcay, A. Atapour-Abarghouei, and T. P. Breckon, “GANomaly: Semisupervised anomaly detection via adversarial training,” in Proc. Asian
Conf. Comput. Vis., Springer, 2018, pp. 622–637.
[5] L. Akoglu, H. Tong, and D. Koutra, “Graph based anomaly detection
and description: A survey,” Data Mining Knowl. Discov., vol. 290, no. 3,
pp. 626–688, 2015.
[6] P. Bachman, R. D. Hjelm, and W. Buchwalter, “Learning representations by maximizing mutual information across views,” 2019, arXiv:
1906.00910.
[7] A. Bagnall et al., “The UEA multivariate time series classification archive,”
2018, arXiv: 1811.00075.
[8] R. Bamler and S. Mandt, “Extreme classification via adversarial softmax
approximation,” in Proc. Int. Conf. Learn. Representations, 2020.
[9] L. Bergman and Y. Hoshen, “Classification-based anomaly detection for
general data,” in Proc. Int. Conf. Learn. Representations, 2020.
[10] L. Bergman, N. Cohen, and Y. Hoshen, “Deep nearest neighbor anomaly
detection,” 2020, arXiv: 2002.10445.
[11] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LoF: Identifying
density-based local outliers,” in Proc. 2000 ACM SIGMOD Int. Conf.
Manage. Data, 2000, pp. 93–104.
[12] T. Cai, S. Luo, K. Xu, D. He, T.-Y. Liu, and L. Wang, “GraphNorm:
A principled approach to accelerating graph neural network training,” in
Proc. Int. Conf. Mach. Learn., 2021, pp. 1204–1215.
[13] J. Chen, M. Feng, and T. S. Wirjanto, “Harnessing contrastive learning
and neural transformation for time series anomaly detection,” Available at
SSRN 4757427, 2024.
[14] K. Chen, M. Feng, and T. S. Wirjanto, “Time-series anomaly detection via
contextual discriminative contrastive learning,” 2023, arXiv:2304.07898.
[15] T. Chen, S. Kornblith, M. Norouzi, and G. Hinton, “A simple framework
for contrastive learning of visual representations,” in Proc. Int. Conf. Mach.
Learn., 2020, pp. 1597–1607.
[16] X. Chen and E. Konukoglu, “Unsupervised detection of lesions in brain
MRI using constrained adversarial auto-encoders,” in Proc. MIDL Conf.
Book, 2018.
[17] E. D. Cubuk, B. Zoph, D. Mane, V. Vasudevan, and Q. V. Le, “AutoAugment: Learning augmentation strategies from data,” in Proc. IEEE/CVF
Conf. Comput. Vis. Pattern Recognit., 2019, pp. 113–123.

2184

IEEE TRANSACTIONS ON PATTERN ANALYSIS AND MACHINE INTELLIGENCE, VOL. 47, NO. 3, MARCH 2025

[18] L. Deecke, R. Vandermeulen, L. Ruff, S. Mandt, and M. Kloft, “Image
anomaly detection with generative adversarial networks,” in Proc. Joint
Eur. Conf. Mach. Learn. Knowl. Discov. Databases, Springer, 2018,
pp. 3–17.
[19] L. Deecke, L. Ruff, R. A. Vandermeulen, and H. Bilen, “Transfer-based
semantic anomaly detection,” in Proc. Int. Conf. Mach. Learn., 2021,
pp. 2546–2558.
[20] C. Doersch, A. Gupta, and A. A. Efros, “Unsupervised visual representation learning by context prediction,” in Proc. IEEE Int. Conf. Comput.
Vis., 2015, pp. 1422–1430.
[21] A. Dosovitskiy, P. Fischer, J. T. Springenberg, M. Riedmiller, and T. Brox,
“Discriminative unsupervised feature learning with exemplar convolutional neural networks,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 380,
no. 9, pp. 1734–1747, Sep., 2016.
[22] S. M. Erfani, S. Rajasegarar, S. Karunasekera, and C. Leckie, “Highdimensional and large-scale anomaly detection using a linear one-class
SVM with deep learning,” Pattern Recognit., vol. 58, pp. 121–134, 2016.
[23] Z. Ghafoori and C. Leckie, “Deep multi-sphere support vector data description,” in Proc. 2020 SIAM Int. Conf. Data Mining, 2020, pp. 109–117.
[24] S. Gidaris, P. Singh, and N. Komodakis, “Unsupervised representation
learning by predicting image rotations,” in Proc. Int. Conf. Learn. Representations, 2018.
[25] I. Golan and R. El-Yaniv, “Deep anomaly detection using geometric transformations,” in Proc. Adv. Neural Inf. Process. Syst., 2018, pp. 9758–9769.
[26] S. Goyal, A. Raghunathan, M. Jain, H. V. Simhadri, and P. Jain, “DROCC:
Deep robust one-class classification,” in Proc. Int. Conf. Mach. Learn.,
2020, pp. 3711–3721.
[27] M. Gutmann and A. Hyvärinen, “Noise-contrastive estimation: A new
estimation principle for unnormalized statistical models,” in Proc. 13th
Int. Conf. Artif. Intell. Statist., 2010, pp. 297–304.
[28] M. U. Gutmann and A. Hyvärinen, “Noise-contrastive estimation of unnormalized statistical models, with applications to natural image statistics,”
J. Mach. Learn. Res., vol. 130, no. 2, pp. 307–361 2012.
[29] R. Hadsell, S. Chopra, and Y. LeCun, “Dimensionality reduction by
learning an invariant mapping,” in Proc. IEEE Comput. Soc. Conf. Comput.
Vis. Pattern Recognit., 2006, pp. 1735–1742.
[30] D. Hendrycks, M. Mazeika, and T. Dietterich, “Deep anomaly detection with outlier exposure,” in Proc. Int. Conf. Learn. Representations,
2018.
[31] D. Hendrycks, M. Mazeika, S. Kadavath, and D. Song, “Using selfsupervised learning can improve model robustness and uncertainty,” in
Proc. Adv. Neural Inf. Process. Syst., 2019, pp. 15663–15674.
[32] R. D. Hjelm et al., “Learning deep representations by mutual information
estimation and maximization,” in Proc. Int. Conf. Learn. Representations,
2018.
[33] D. Ho, E. Liang, X. Chen, I. Stoica, and P. Abbeel, “Population based
augmentation: Efficient learning of augmentation policy schedules,” in
Proc. Int. Conf. Mach. Learn., 2019, pp. 2731–2741.
[34] C. Hu, Y. Feng, H. Kamigaito, H. Takamura, and M. Okumura, “One-class
text classification with multi-modal deep support vector data description,”
in Proc. 16th Conf. Eur. Chapter Assoc. Comput., 2021, pp. 3378–3390.
[35] P. Khosla et al., “Supervised contrastive learning,” in Proc. Adv. Neural
Inf. Process. Syst., 2020, pp. 18661–18673.
[36] H. Kim, S. Kim, S. Min, and B. Lee, “Contrastive time-series anomaly
detection,” IEEE Trans. Knowl. Data Eng., vol. 36, no. 10, pp. 5053–5065,
Oct. 2024.
[37] K. H. Kim et al., “RaPP: Novelty detection with reconstruction along
projection pathway,” in Proc. Int. Conf. Learn. Representations, 2019.
[38] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
in Proc. Int. Conf. Learn. Representations, 2015.
[39] A. Li, C. Qiu, M. Kloft, P. Smyth, S. Mandt, and M. Rudolph, “Deep
anomaly detection under labeling budget constraints,” in Proc. Int. Conf.
Mach. Learn., 2023, pp. 19882–19910.
[40] J. Li, P. Chen, Z. He, S. Yu, S. Liu, and J. Jia, “Rethinking out-ofdistribution (OOD) detection: Masked image modeling is all you need,” in
Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2023, pp. 11578–
11589.
[41] S. Lim, I. Kim, T. Kim, C. Kim, and S. Kim, “Fast autoaugment,” in
Proc. Adv. Neural Inf. Process. Syst., Curran Associates, Inc., 2019,
pp. 6665–6675.
[42] R. Linsker, “Self-organization in a perceptual network,” Computer,
vol. 210, no. 3, pp. 105–117 1988.
[43] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. 8th IEEE
Int. Conf. Data Mining, 2008, pp. 413–422.

[44] P. Liznerski, L. Ruff, R. A. Vandermeulen, B. J. Franks, M. Kloft, and K.
R. Muller, “Explainable deep one-class classification,” in Proc. Int. Conf.
Learn. Representations, 2020.
[45] X. Luo et al., “Deep graph level anomaly detection with contrastive
learning,” Sci. Rep., vol. 120, no. 1, 2022, Art. no. 19867.
[46] A. Mahendran and A. Vedaldi, “Understanding deep image representations
by inverting them,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.,
2015, pp. 5188–5196.
[47] P. Malhotra, A. Ramakrishnan, G. Anand, L. Vig, P. Agarwal, and G.
Shroff, “LSTM-based encoder-decoder for multi-sensor anomaly detection,” 2016, arXiv:1607.00148.
[48] L. M. Manevitz and M. Yousef, “One-class SVMs for document classification,” J. Mach. Learn. Res., vol. 20, pp. 139–154, 2001.
[49] I. Misra, C. L. Zitnick, and M. Hebert, “Shuffle and learn: Unsupervised
learning using temporal order verification,” in Proc. Eur. Conf. Comput.
Vis., Springer, 2016, pp. 527–544.
[50] A. Mnih and K. Kavukcuoglu, “Learning word embeddings efficiently
with noise-contrastive estimation,” in Proc. Adv. Neural Inf. Process. Syst.,
2013, pp. 2265–2273.
[51] C. Morris, N. M. Kriege, F. Bause, K. Kersting, P. Mutzel, and M.
Neumann, “Tudataset: A collection of benchmark datasets for learning
with graphs,” in Proc. Workshop Graph Representation Learn. Beyond,
2020. URL www.graphlearning.io
[52] A. Narayanan, M. Chandramohan, R. Venkatesan, L. Chen, Y. Liu, and
S. Jaiswal, “graph2vec: Learning distributed representations of graphs,”
2017, arXiv: 1707.05005.
[53] M. Neumann, R. Garnett, C. Bauckhage, and K. Kersting, “Propagation
Kernels: Efficient graph Kernels from propagated information,” Mach.
Learn., vol. 1020, no. 2, pp. 209–245, 2016.
[54] H. C. V. Ngu and K. M. Lee, “CL-TAD: A contrastive-learning-based
method for time series anomaly detection,” Appl. Sci., vol. 130, no. 21,
2023, Art. no. 11938.
[55] M. Noroozi and P. Favaro, “Unsupervised learning of visual representations by solving jigsaw puzzles,” in Proc. Eur. Conf. Comput. Vis.,
Springer, 2016, pp. 69–84.
[56] A. v. d. Oord, Y. Li, and O. Vinyals, “Representation learning with
contrastive predictive coding,” 2018, arXiv: 1807.03748.
[57] J. Pennington, R. Socher, and C. D. Manning, “Glove: Global vectors for
word representation,” in Proc. Empirical Methods Natural Lang. Process.,
2014, pp. 1532–1543. URL http://www.aclweb.org/anthology/D14-1162
[58] P. Perera, R. Nallapati, and B. Xiang, “OCGAN: One-class novelty detection using GANs with constrained latent representations,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., 2019,
pp. 2898–2906.
[59] E. Principi, F. Vesperini, S. Squartini, and F. Piazza, “Acoustic novelty
detection with adversarial autoencoders,” in Proc. 2017 Int. Joint Conf.
Neural Netw., 2017, pp. 3324–3330.
[60] C. Qiu, T. Pfrommer, M. Kloft, S. Mandt, and M. Rudolph, “Neural
transformation learning for deep anomaly detection beyond images,” in
Proc. Int. Conf. Mach. Learn., 2021, pp. 8703–8714.
[61] C. Qiu, A. Li, M. Kloft, M. Rudolph, and S. Mandt, “Latent outlier
exposure for anomaly detection with contaminated data,” in Proc. Int.
Conf. Mach. Learn., 2022, pp. 18153–18167.
[62] A. J. Ratner, H. R. Ehrenberg, Z. Hussain, J. Dunnmon, and C. Ré, “Learning to compose domain-specific transformations for data augmentation,”
in Proc. Adv. Neural Inf. Process. Syst., 2017, pp. 3239–3249.
[63] T. Reiss, N. Cohen, L. Bergman, and Y. Hoshen, “Panda: Adapting pretrained features for anomaly detection and segmentation,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2021,
pp. 2806–2814.
[64] L. Ruff et al., “Deep one-class classification,” in Proc. Int. Conf. Mach.
Learn., 2018, pp. 4393–4402.
[65] L. Ruff et al., “Deep semi-supervised anomaly detection,” in Proc. Int.
Conf. Learn. Representations, 2019.
[66] L. Ruff, Y. Zemlyanskiy, R. Vandermeulen, T. Schnake, and M. Kloft,
“Self-attentive, multi-context one-class classification for unsupervised
anomaly detection on text,” in Proc. 57th Annu. Meeting Assoc. Comput.
Linguistics, 2019, pp. 4061–4071.
[67] L. Ruff et al., “A unifying review of deep and shallow anomaly detection,”
in Proc. IEEE, vol. 109, no. 5, pp. 756–795, May 2021.
[68] A. P. Ruiz, M. Flynn, J. Large, M. Middlehurst, and A. Bagnall, “The great
multivariate time series classification bake off: A review and experimental
evaluation of recent algorithmic advances,” Data Mining Knowl. Discov.,
vol. 35, pp. 1–49, 2020.

QIU et al.: SELF-SUPERVISED ANOMALY DETECTION WITH NEURAL TRANSFORMATIONS

[69] T. Schlegl, P. Seeböck, S. M. Waldstein, U. Schmidt-Erfurth, and G. Langs,
“Unsupervised anomaly detection with generative adversarial networks to
guide marker discovery,” in Proc. Int. Conf. Inf. Process. Med. Imag., 2017,
pp. 146–157.
[70] T. Schneider et al., “Detecting anomalies within time series using local
neural transformations,” 2022, arXiv:2202.03944.
[71] V. Sehwag, M. Chiang, and P. Mittal, “SSD: A unified framework for selfsupervised outlier detection,” in Proc. Int. Conf. Learn. Representations,
2020.
[72] T. Shenkar and L. Wolf, “Anomaly detection for tabular data with internal
contrastive learning,” in Proc. Int. Conf. Learn. Representations, 2022.
[73] N. Shervashidze, P. Schweitzer, E. J. Van Leeuwen, K. Mehlhorn, and K.
M. Borgwardt, “Weisfeiler-Lehman graph Kernels,” J. Mach. Learn. Res.,
vol. 120, no. 9, pp. 2539–2561, 2011.
[74] K. Sohn, C.-L. Li, J. Yoon, M. Jin, and T. Pfister, “Learning and evaluating
representations for deep one-class classification,” in Proc. Int. Conf. Learn.
Representations, 2021.
[75] J. Tack, S. Mo, J. Jeong, and J. Shin, “CSI: Novelty detection via contrastive
learning on distributionally shifted instances,” in Proc. 34th Conf. Neural
Inf. Process. Syst., 2020, pp. 11839–11852.
[76] A. Tamkin, M. Wu, and N. Goodman, “Viewmaker networks: Learning
views for unsupervised representation learning,” in Proc. Int. Conf. Learn.
Representations, 2021.
[77] T. Tran, T. Pham, G. Carneiro, L. Palmer, and I. Reid, “A Bayesian data
augmentation approach for learning deep models,” in Proc. 31st Int. Conf.
Neural Inf. Process. Syst., 2017, pp. 2794–2803.
[78] M. Tschannen, J. Djolonga, P. K. Rubenstein, S. Gelly, and M. Lucic, “On
mutual information maximization for representation learning,” in Proc.
Int. Conf. Learn. Representations, 2019.
[79] S. Verma and Z.-L. Zhang, “Hunt for the unique, stable, sparse and fast
feature learning on graphs,” in Proc. 31st Int. Conf. Neural Inf. Process.
Syst., 2017, pp. 87–97.
[80] J. Wang, S. Sun, and Y. Yu, “Multivariate triangular quantile maps
for novelty detection,” in Proc. Adv. Neural Inf. Process. Syst., 2019,
pp. 5060–5071.
[81] R. Wang et al., “Deep contrastive one-class time series anomaly detection,”
in Proc. 2023 SIAM Int. Conf. Data Mining, 2023, pp. 694–702.
[82] S. Wang et al., “Effective end-to-end unsupervised outlier detection via
inlier priority of discriminative network,” in Proc. Adv. Neural Inf. Process.
Syst., 2019, pp. 5962–5975.
[83] E. Wong and J. Z. Kolter, “Learning perturbation sets for robust machine
learning,” 2020, arXiv: 2007.08450.
[84] Y. Xiao et al., “Multi-sphere support vector data description for outliers
detection on multi-distribution data,” in Proc. 2009 IEEE Int. Conf. Data
Mining Workshops, 2009, pp. 82–87.
[85] K. Xu, W. Hu, J. Leskovec, and S. Jegelka, “How powerful are graph neural
networks?,” in Proc. Int. Conf. Learn. Representations, 2018.
[86] K. Xu, C. Li, Y. Tian, T. Sonobe, K.-I. Kawarabayashi, and S. Jegelka,
“Representation learning on graphs with jumping knowledge networks,”
in Proc. Int. Conf. Mach. Learn., 2018, pp. 5453–5462.
[87] Y. You, T. Chen, Y. Sui, T. Chen, Z. Wang, and Y. Shen, “Graph contrastive
learning with augmentations,” in Proc. Adv. Neural Inf. Process. Syst.,
2020, pp. 5812–5823.
[88] R. Zhang, P. Isola, and A. A. Efros, “Split-brain autoencoders: Unsupervised learning by cross-channel prediction,” in Proc. IEEE Conf. Comput.
Vis. Pattern Recognit., 2017, pp. 1058–1067.
[89] X. Zhang, Q. Wang, J. Zhang, and Z. Zhong, “Adversarial autoaugment,”
in Proc. Int. Conf. Learn. Representations, 2019.
[90] L. Zhao and L. Akoglu, “On using classification datasets to evaluate graph
outlier detection: Peculiar observations and new insights,” Big Data, Mary
Ann Liebert, Inc., vol. 11, no. 3, pp. 151–180, 2023.
[91] C. Zhou and R. C. Paffenroth, “Anomaly detection with robust deep
autoencoders,” in Proc. 23rd ACM SIGKDD Int. Conf. Knowl. Discov.
Data Mining, 2017, pp. 665–674.
[92] H. Zhou, K. Yu, X. Zhang, G. Wu, and A. Yazidi, “Contrastive autoencoder
for anomaly detection in multivariate time series,” Inf. Sci., vol. 610,
pp. 266–280, 2022.
[93] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Representations,
2018.

2185

Chen Qiu received the master’s degree in electrical engineering from the University of Erlangen–
Nuremberg and the PhD degree in computer science
from RPTU Kaiserslautern-Landau, Germany, where
he was supervised by Marius Kloft. He is a research
scientist with Bosch Research, USA, where he develops machine learning and deep learning models for
autonomous intelligent systems. His research focuses
on anomaly detection, generative models, and prompt
learning for foundation models. Additionally, he was
co-advised by Stephan Mandt and Maja Rudolph
during his tenure as a researcher with Bosch Research, Germany.
Marius Kloft (Senior Member, IEEE) received the
master’s degree in mathematics from the University
of Marburg with a thesis in algebraic geometry, in
2006. He is a professor of computer science with
RPTU Kaiserslautern-Landau, Germany. Previously,
he was an adjunct faculty member of the University of
Southern California (09/2018-03/2019), an assistant
professor with HU Berlin (2014-2017) and a joint
postdoctoral fellow (2012-2014) with the Courant
Institute of Mathematical Sciences and Memorial
Sloan-Kettering Cancer Center, New York, working
with Mehryar Mohri, Corinna Cortes, and Gunnar Rätsch. From 2007-2011,
he was a PhD student in the machine learning program of TU Berlin, headed
by Klaus-Robert Müller. He was co-advised by Gilles Blanchard and Peter L.
Bartlett, whose learning theory group with UC Berkeley he visited from 10/2009
to 10/2010.
Stephan Mandt (Member, IEEE) received the PhD
degree in theoretical physics from the University of
Cologne, where he received the German National
Merit Scholarship. He is an associate professor of
computer science and statistics with the University of
California, Irvine. His research centers on deep generative modeling, uncertainty quantification, neural
data compression, and AI for science. Previously, he
led the machine learning group with Disney Research
in Pittsburgh and Los Angeles and held postdoctoral
positions with Princeton and Columbia University. He
is furthermore a recipient of the NSF CAREER Award, the UCI ICS Mid-Career
Excellence in Research Award, the German Research Foundation’s Mercator
Fellowship, a Kavli Fellow of the U.S. National Academy of Sciences, a member
of the ELLIS Society, and a former visiting Researcher with Google Brain. His
research is currently supported by NSF, DARPA, IARPA, DOE, Disney, Intel,
and Qualcomm. Dr, Mandt is an action editor of the Journal of Machine Learning
Research and Transaction on Machine Learning Research, held tutorials with
NeurIPS, AAAI, and UAI, and regularly serves as (Senior) area chair for
NeurIPS, ICML, AAAI, and ICLR. He currently serves as program chair for
AISTATS 2024 and general chair for AISTATS 2025.
Maja Rudolph received the BS degree in mathematics from MIT and the PhD degree in computer
science from Columbia University, where she worked
with David Blei. She is a research professor with the
Data Science Institute of the University of WisconsinMadison, where she works in the areas of probabilistic
machine learning and generative AI. In addition to
her academic, Dr. Rudolph is a lead research scientist at Bosch, where she addresses machine learning
research questions derived from engineering applications, and has contributed to the fields of anomaly
detection and hybrid modeling.
PAPER_TEXT
