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
# [485] MFFTD: A Multiscale Feature Fusion Transformer Detector for Electricity Theft Based on Semi-Supervised Learning
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
编号：485
题名：MFFTD: A Multiscale Feature Fusion Transformer Detector for Electricity Theft Based on Semi-Supervised Learning
年份：2025
DOI：10.1109/tim.2025.3552857
来源：IEEE Transactions on Instrumentation and Measurement
PDF：paper/10.1109_TIM.2025.3552857.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：无
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\485.txt
- 原始字符数：53556
- 本次发送字符数：53556
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

3522810

MFFTD: A Multiscale Feature Fusion Transformer
Detector for Electricity Theft Based
on Semi-Supervised Learning
Yufeng Wang , Senior Member, IEEE, Zhijie Wu , Jianhua Ma , Senior Member, IEEE,
and Qun Jin , Senior Member, IEEE
Abstract— The wide deployment of advanced metering infrastructure (AMI) in power systems allows utility companies to
automatically and accurately collect and process the time-series
load profiles of households, but meanwhile incurs the severe
electricity theft (ET) that some illegal residential users may
manipulate their electricity consumptions to reduce their billings.
Although, due to the powerful ability of modeling long-range
dependencies in sequential data, transformer has been widely
used for time-series modeling including ET detection (ETD), the
significant weakpoint lies in that it only considers the attention weights between either points or prepatched subsequences
(i.e., patches) of fixed size within the input sequence, which
cannot fully characterize the relationships among multiscale
temporal patches and lead to suboptimal detection performance.
To address the above issue, based on self-supervised feature
extraction and supervised fine-tuning, our work proposes a novel
multiscale feature fusion transformer encoder (TE)-based ETD
framework, MFFTD. Specifically, our work’s contributions are
following. First, in MFFTD, a hierarchical patching enhanced
TE (HPTE) is explicitly designed, in which each layer patches
the input sequence with variable patch size. Then, through
hierarchically stacked multiple HPTE layers, the feature combining multiscale patches can be effectively extracted. Second,
considering the constraint that only a small percentage of labeled
theft samples are practically available, our work first pretrains
the structure parameters of MFFTD through a self-supervised
pretext task of forecasting the randomly masked segments in time
series. Then, the small percentage of labeled anomalous samples
is used to fine-tune the MFFTD model. Extensive experiments
on multiple real datasets demonstrate our proposed MFFTD
scheme outperforms the state-of-the-art (SOTA) transformerbased supervised and semi-supervised ETD methods.
Index Terms— Electricity theft detection (ETD), multiscale
feature fusion, self-supervised learning, semi-supervised learning,
transformer, variable patching.

T

I. I NTRODUCTION
HE advanced metering infrastructure (AMI) has been
widely deployed into modern power systems, which

Received 10 December 2024; revised 21 February 2025; accepted 7 March
2025. Date of publication 19 March 2025; date of current version 1 April
2025. The Associate Editor coordinating the review process was Dr. Lei Mao.
(Corresponding author: Yufeng Wang.)
Yufeng Wang and Zhijie Wu are with the School of Telecommunications and Information Engineering, Nanjing University of Posts
and Telecommunications, Nanjing 210049, China (e-mail: wfwang1974@
gmail.com).
Jianhua Ma is with the Faculty of Computer and Information Sciences,
Hosei University, Tokyo 102-8160, Japan (e-mail: jianhua@hosei.ac.jp).
Qun Jin is with the Faculty of Human Sciences, Waseda University,
Tokyo 169-8050, Japan (e-mail: jin@waseda.jp).
Digital Object Identifier 10.1109/TIM.2025.3552857

provides two-way communications between customers and
utility companies [1]. Through AMI, utility companies are
able to gather sequentially temporal information about individual consumption, i.e., time series, and accordingly charge
customers. Wide deployment of AMI is a milestone that
denotes traditional power systems are evolved into smart grids,
where pervasive control at all levels is a basic premise [2].
Although many benefits have been brought by AMI, it also
introduces a number of security vulnerabilities. For example,
adversaries can launch a variety of cyberphysical attacks
against AMI devices and network components [3]. One of
the main purposes of these adversaries is to manipulate their
electricity consumptions such that their billings can be lowered
down, so-called the behavior of electricity theft (ET) [4].
A. Research Motivation
Recently, based on the massive amount of data provided by
AMI, deep neural network (DNN)-based ET detection (ETD)
schemes have been widely developed [5], [6], [7], since
DNNs can automatically extract features and have powerful
functional approximation ability, including convolutional neural networks (CNNs) and recurrent neural networks (RNNs).
Technically, CNN-based detectors [8], [9] transform 1-D
temporal electricity consumption data into 2-D matrix to
extract spatial feature. Different from CNN-based detectors,
long short-term memory (LSTM, a specific variant of RNN)based ET detectors accept time series sequentially as input
and inherently learn the temporal dependencies of electricity
consumption data [10], [11]. However, their weakpoint lies in
that: LSTM cannot compute in parallel and cannot efficiently
learn a long-range temporal dependencies and CNN-based
detectors mainly focus on extracting local features of the
electricity consumption data. Although there existed work in
literature that design two-level CNNs [12] or adopt ConvLSTM block [13] to attempt to simultaneously capture the
long-range and local features, both the structures still have
the problem of not sufficiently learning global information
of the input temporal sequence. Recently, transformer-based
detectors [14], [15] have been proposed to solve the aforementioned issues. Transformer is built on multihead attention
mechanism and is regarded as suitable modeling time series
including ETD task: It concurrently represents each input
sequence element by considering its context (future–past),
while multiple attention heads can incorporate different representation subspaces [16]. However, there are two limitations

1557-9662 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

3522810

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

in the existing transformer-based ET detectors. The first is that
patching with fixed size used in traditional transformer [17]
cannot sufficiently capture multiscale feature. The multiscale
feature fusion method, by combining information from different scales, can effectively improve the detection accuracy of
ETD systems. In [12] and [18], CNNs are used to extract features at different time scales from electricity consumption data.
However, the aforementioned CNN-based methods primarily
focus on local features and are not effective at capturing global
and temporal information in electricity consumption data.
The second is the so-called insufficiency of labeled
anomalous samples. Since extensive data labeling is often
prohibitively expensive or impractical: require the knowledge
of domain expertise, therefore, it is imperative to achieve high
detection performance using only a limited amount of labeled
data or by leveraging the existing plethora of unlabeled data.
Generally, pretraining and fine-tuning learning paradigm is
well-suited to address this issue. In this paradigm, the model
is first pretrained for a pretext task on a dataset containing
large number of normal samples, and then fine-tuned with
few anomalous samples for a specific downstream task, such
as ETD. Following this paradigm, several TE-based architectures have been proposed, including time-series transformer
(TST) [19] and Patch TST (PatchTST) [17]. Specifically,
to extract the temporal relations in the time series, patching is
usually used, in which the long temporal sequence is divided
into several subsequences with a certain patch size, and the
obtained subsequences are called patches. It is shown [17] that
patching can effectively retain local semantic information and
quadratically reduce computation and memory usage of the
attention maps. However, such patching with fixed size has one
fatal flaw: Once the input sequence is patched, the following
TE can only learn the attention weights between patches of a
fixed size, which fully did not exploit the relationships between
multiscale patches at all, and may lead to a poor detection
performance.
B. Main Contributions of Our Work
To address the above issues, different from the existing works, this article proposes a novel multiscale feature
fusion TE-based ETD architecture MFFTD, based on semisupervised learning paradigm consisting of self-supervised
feature extraction and supervised fine-tuning. This approach
leverages both unlabeled and labeled data, enhancing model
performance even with limited labeled anomalous data.
Especially, a novel multiscale feature fusion TE, named as
hierarchical patching enhanced transformer encoder (HPTE),
is designed to intentionally extract and fuse multiscale features. Since electricity consumption data typically contain
patterns at different time scales, HPTE can effectively capture
these complex temporal dependencies, thereby improving the
identification of ET behaviors.
In detail, the main contributions of this article can be
summarized as follows.
1) In MFFTD, the core component, the HPTE, is designed.
In detail, at each HPTE layer, the input temporal
sequence is patched with variable patch size, and
then the multihead attentions are used to infer the
correlation between any pair of patches. Then, hierarchically stacked HPTE layers are used to automatically

Fig. 1. Summary of DNN-based ET detectors categorized from learning
paradigm.

extract multiscale features of the input long temporal
sequence.
2) To accurately detect ET under the constraint of only
limited number of labeled data available, MFFTD is
trained in a semi-supervised manner. Specifically, a selfsupervised pretrained scheme is implemented to learn
the structure parameters of MFFTD, in which the
self-supervised pretext task is intentionally designed to
forecast the randomly masked segments in time series.
Then, the penultimate of the pretrained model as the
feature extractor (FE) and the added output layer as
classifier are fine-tuned with a small percentage of
labeled samples in a supervised way. In brief, this
hybrid approach can merge the advantages of supervised
and unsupervised learning paradigms and improve ETD
performance and generalization.
3) Extensive experiments on multiple electricity consumption datasets are conducted to compare our proposed
MFFTD scheme with various state-of-the-art (SOTA)
methods. In terms of main performance metrics, the
effectiveness of the proposed ETD scheme MFFTD is
verified.
The rest of this article is organized as follows. In Section II,
typical DNN (including transformer)-based ETD schemes are
summarized and their disadvantages are discussed. Section III
presents the proposed ETD framework MFFTD and describes
its main modules in detail. Section IV provides the comprehensive performance comparison between the proposed MFFTD
framework and SOTA ETD methods. Finally, we briefly conclude this article and point out future work.
II. R ELATED W ORK
DNN-based time-series anomaly detection schemes can
automatically extract temporal features from historical electricity consumption data and then detect anomalies. Generally,
from the perspective of learning paradigm, the existing
schemes can be classified into three categories, as shown
in Fig. 1: supervised-learning-based, unsupervised-learningbased, and semi-supervised-learning, which are correspondingly discussed in Sections II-A–II-C.
A. Supervised-Learning-Based Methods
Supervised-learning-based methods focus on building predictive models from labeled data to detect ET. There are

WANG et al.: MULTISCALE FEATURE FUSION TRANSFORMER DETECTOR FOR ET BASED ON SEMI-SUPERVISED LEARNING

two mainly used DNNs: CNN and LSTM. Wide and deep
CNNs (WDCNNs) [12] consist of a wide component and
a deep component. The wide component extracts the global
features of 1-D electricity consumption data, and the deep
component captures the periodical and nonperiodical features
from the transformed 2-D data matrix. Then the features
from two components are added together to predict anomaly
probability. But the wide component (i.e., the fully connected
layer) cannot effectively learn temporal dependencies from
customers’ electricity consumption data [6], and the simple
adding operation cannot effectively fuse two types of features.
Hybrid-order representation learning network (HORLN) [20]
learns the hybrid-order representations of the transformed 2-D
data matrix. The first-order representations contain inter-andintra week information, and the second-order representations
are composed of global temporal dependencies learned from
self-correlation matrices. Through integrating both sequential and nonsequential data, hybrid DNNs for detection of
nontechnical losses (HNN-NTLs) [21] combines an LSTM
network and a multilayer perceptrons (MLPs) to detect ET,
in which LSTM analyzes the raw daily energy consumption
history, MLP processes nonsequential data, and then the hybrid
features are used to predict the anomaly probability. To capture
both the global and local temporal dependencies of input time
series, convolutional LSTM (ConvLSTM) is applied into ETD,
in which convolutional operations are used into both the inputto-state and state-to-state transitions in LSTM [13].
Recently, since TE can automatically learn the relationships between elements in a long sequence through multihead
attention mechanism, transformer has witnessed great application for processing sequential data, including ETD task.
Conv-attentional transformer neural network (CA-TNN) [14]
is a hybrid model of conv-attentional module and transformer
model to extract local features and global features successively,
and the final hybrid features are used for ETD. Specifically,
the whole load sequence is divided into multiple segments,
and the global features of consumption data are extracted
by calculating the self-attention between segments. Moreover,
conv-attentional module is used to embed the input data and
capture the local features in each segment. The weakness of
CA-TNN lies in that it can only capture dependencies of
segments of a fixed size. In summary, although supervised
paradigm is intentionally designed for anomaly detection using
training dataset with explicit normal/anomalous labels, it may
accurately conduct ETD. However, its significant weakpoint
is that a large amount of labeled data are needed to train the
detection model. Otherwise, the limited number of labeled data
constrains the detection performance (overfitting to the small
dataset). However, the availability of sufficient labeled temporal samples is extremely limited. Therefore, it is imperative to
leverage the existing plethora of unlabeled data.
B. Unsupervised-Learning-Based Methods
For the category of unsupervised-learning-based ETD,
stacked sparse denoising autoencoder (SSDAE) [22] uses
a stacked sparse denoising autoencoder to learn feature of
normality through minimizing reconstruction error and takes
the testing samples with the error higher than the threshold as anomalies. Similarly, [23] incorporates LSTM into
autoencoders and is also based on reconstruction method.

3522810

Unsupervised-learning-based methods usually aim to learn the
latent distribution of unlabeled data. The objective function of
the data reconstruction is designed for dimension reduction or
data compression, rather than anomaly detection.
As a result, purely unsupervised paradigm did not assume
the existence of anomalous temporal samples. Its main goal is
not specially designed for anomaly detection, but for generally
learning the normality of time series [24], which may lead to
relatively poor ETD performance.
C. Semi-Supervised-Learning-Based Methods
To integrate the benefits of supervised and unsupervised
paradigms under the constraint of insufficient labeled data,
semi-supervised-learning-based methods are proposed, which
fully exploit both labeled and unlabeled data to build the
predictive models. Multitask feature extracting fraud detector
(MFEFD) [25] simply uses the stacked fully connected layers
as DNN structure and is trained in a semi-supervised manner,
which combines supervised and unsupervised learning through
multitask learning. Recently, some unified TE-based semisupervised learning frameworks are proposed [17], [19], which
can be naturally used in ETD task. Specifically, TST [19]
presents an unsupervised pretraining framework for multivariate time series, in which segments of different sizes are masked
and the model is trained to predict the masked contents with
mean square error loss, and offers substantial performance
benefits over fully supervised learning on downstream tasks.
However, the original TE architecture used in TST can
only learn temporal dependencies between each data point
at different timestamps, which neglects the local semantic
information. Besides, the efficiency of the method is limited
by the length of the time series (L) with computational
complexity overhead as O(L 2 ). To solve the above issue,
before feeding the temporal sequence to TE, the latest work
PatchTST [17] segments the long time series into subserieslevel patches as input tokens to transformer. The so-called
patching design can both retain the local semantic information
in embedding and quadratically reduce computation and memory usage. However, the total number of patches is prefixed,
which can only capture the relationships between patches in
a fixed granularity way. Different from PatchTST, our work
designs an HPTE with variable patch sizes in each HPTE
layer, which can effectively extract multiscale latent temporal
dependencies in time series and greatly improve the ETD
performance. Furthermore, the impact of variable patch size
in each HPTE layer is investigated.
III. MFFTD: P ROPOSED M ETHOD FOR ETD
A. Overall Architecture
Fig. 2 presents the overview framework of the proposed
MFFTD scheme, which consists of training phase and operating phase: the purpose of training phase is to train the
MFFTD framework, and then the operating phase uses the
trained MFFTD to conduct ETD. The training phase is explicitly composed of two modules: self-supervised pretraining
and supervised two-stage fine-tuning. In module 1, a selfsupervised pretraining regression task is used to learn the
structural parameters of HPTE used as the FE. In module 2,
the pretrained FE in module 1 and classifier are fine-tuned
in a supervised-based two-stage way: in the first stage, the

3522810

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

in Fig. 3, that is, FiHPE = P ′ W + b, where W and b are
learnable parameters.
Note that it is shown that transformer with positional
encoding can hardly preserve temporal information [26], and
moreover, we empirically found out that adding both learnable
and fixed positional encoding each layer actually reduces,
instead of improving, detection performance. Our empirical
results comply with the conclusion obtained by [26] that the
vanilla transformer is not sufficiently effective for modeling
time series, which acts as the rationale that our work patches
time series with multiple variable patch sizes, to effectively
capture the multiple-scale temporal relationships in time series.
2) Transformer Encoder: In TE module, the existing
TE [27] is used to characterize the relationships between
different patches, which, as shown in Fig. 3, consists of a multihead attention (MHA) layer and an MLP layer. Specifically,
each head in the MHA transforms the feature map FiHPE into
query matrices Q h , key matrices K h , and value matrices Vh .
The scaled dot-product attention [Attention(.)] is conducted for
each head and outputs the concatenated matrices [MHA(.)] as
follows:

Fig. 2.
Overall framework of the proposed MFFTD with training and
operating phases.

parameters of pretrained FE are frozen, and only the classifier
is trained; and in the second stage, both are trained, which can
protect the pretrained parameters of FE and stabilize the whole
training processes. In the operating phase, the trained FE and
classifier, i.e., our scheme MFFTD takes load profile as input
and outputs its anomaly probability. Electricity customers with
anomaly probability larger than 0.5 are judged as illegal.
Note that the designed HPTE is the core component in our
framework shown as Fig. 2, which is specifically described
in Fig. 3.
B. Hierarchical Patching Enhanced Transformer Encoder
In Fig. 2, HPTE is used as the FE, which is composed of
multiple stacked HPTE layers. The ith HPTE layer is shown
in Fig. 3, which consists of two modules: hierarchical patch
embedding (HPE) and TE. In the ith HPTE layer, the length
of input sequence is denoted as L i−1 , the length of output
sequence as L i , the embedding dimension as d, and the patch
size as pi . The first (i.e., gray) rectangle represents the input
feature matrix Fi−1 of the ith layer, the second (i.e., blue)
rectangle represents the feature matrix FiHPE output by HPE,
and the third (i.e., red) rectangle represents the final output
feature matrix Fi of the ith layer. Note that L i = (L i−1 / pi ).
The detailed operations of HPE and TE modules are as
follows.
1) Hierarchical Patch Embedding: Given the input feature
of the ith HPTE layer, Fi−1 ∈ R L i−1 ×d , HPE module, using
patch size pi , first divides the input feature into multiple,
i.e., (L i−1 / pi ) patches, each patch P ∈ R pi ×d . Then all the
patches are put together and reshaped into a matrix P ′ ∈
R(L i−1 / pi )×( pi ×d) , which are further projected into a feature map
FiHPE with length (L i−1 / pi ) formulated in HPE module shown

Attention(Q h , K h , Vh )


Q h K hT
= Softmax √
Vh
dk

MHA FiHPE
= Concat(head1 , . . . , head H )W O + b O , where
headh


= Attention FiHPE WhQ , FiHPE WhK , FiHPE WhV

(1)

(2)

where Softmax is the softmax activation function, Concat is
the concatenation operation, dk is the embedding dimension
of K h , and H is the number of the heads. W O , WhQ , WhK , WhV ,
and b O are learnable parameters.
Besides, the residual connecting is used to avoid gradient
explosion as follows:

V ′ = Layernorm FiHPE + MHA FiHPE
(3)
′
′
Fi = Layernorm(V + MLP(V ))
(4)
where Layernorm refers to layer normalization, a technique
used to normalize the inputs to a layer in a neural network.
Fi is the output of ith HPTE layer, and V ′ is an intermediate
variable.
C. Training of MFFTD: Self-Supervised Pretraining and
Supervised Fine-Tuning
Specifically, we consider the load profile as an univariate
sequence of T data points X = {x1 , . . . , x T }. When detecting
whether xt is an anomaly, i.e., yt ∈ {0, 1} (1 denotes an
anomalous data point), we take into account the dependencies
within a local contextual window of length L, i.e., wt =
{xt−L+1 , . . . , xt } to help the model learn to detect anomalies.
Here we simply drop the window wt when t < L [28].
1) Self-Supervised Pretraining as Regression Task: To
strengthen the FE’s ability to capture underlying features of
unlabeled data, the regressive task of recovering the masked
input is used: the mathematical essence is using the relationships between patches to recover the missing contents.

WANG et al.: MULTISCALE FEATURE FUSION TRANSFORMER DETECTOR FOR ET BASED ON SEMI-SUPERVISED LEARNING

Fig. 3.

3522810

Illustration of the structure of the ith HPTE layer and its processing.

Given the detection window wt ∈ R L×1 , the masked input ŵt
for FE can be obtained as follows:
ŵt = M ⊙ wt

(5)

where ⊙ is the Hadamard product, and M ∈ R L×1 is a binary
mask which consists of alternating segments of 0 s and 1 s.
The length of segments of 0 s follows geometric distribution
of mean l0 : when the segment of 0 s stops, it is succeeded by
a segment of 1 s, whose length follows geometric distribution
of mean l1 . Let r denote the proportion of the mask to be 0,
thus l1 = ((1 − r )/r )l0 .
The masked detection window ŵt is then fed to the
FE. Afterward, the extracted feature F is fed to an FC
layer and flattened to output its forecasting of the partially
masked input window ŵt , denoted as w̃ t given as (6). The
predictive error on the masked values (with indices in the
set M0 ≡ {i : M(i) = 0}) is regarded as regression loss
(i.e., mean square error loss), shown as (7)
w̃ t = Flatten(F W + b)
X
2
L reg =
w̃t (i) − wt (i)

(6)
(7)

i∈M0

where Flatten is the flatten operation, and W and b are
learnable parameters.
Note that the objective of the self-supervised pretraining
is to bootstrap the structural parameters of FE for the successive supervised fine-tuning. That is, the FC layer used for
outputting the masked temporal points will be abandoned in
the following supervised fine-tuning.
2) Two-Stage-Based Supervised Fine-Tuning: The selfsupervised training learns the structure parameters of the
FE but leaves the classifier untrained after being initialized.
To better fit the ETD task, the whole MFFTD framework
is fine-tuned using the small percentage of the labeled
data. However, the different task goal, i.e., regressive task
in pretraining and anomaly detection (classification) downstream task, makes the whole model hard to converge. Thus,
we apply a two-stage training procedure to train the classifier
(implemented as a linear layer and a sigmoid activation
function) and the FE after self-supervised pretraining as
shown in Algorithm 1. The two-stage training can avoid
the condition that large gradient updates triggered by the
randomly initialized classifier will wreck the learned parameters in FE [25]. Specifically, in the first stage (lines 3–10
in Algorithm 1), we freeze the parameters of FE obtained

Algorithm 1 Two-Stage-Based Supervised Fine-Tuning
Input: (W, Y) the labeled time windows, M E 1 the maximal
epochs of training Classifier only, M E 2 the maximal
epochs of training both FE and Classifier, θ F E the pretrained parameters of FE
Output: θ = (θ F E , θc ) parameters of the whole MFFTD
1: Initialize FE and classifier with parameters θ F E , θc ,
respectively
2: Initialize count variables c1 ← 0, c2 ← 0
3: Stage 1: Train the Classifier (Freezing the FE)
4: for c1 = 1 to M E 1 do
5:
for each batch (wt , yt ) in (W, Y) do
6:
The values of
7:
p 1 , L 1cla are presented in (8) and (9)
8:
θc ← Make a gradient step to minimize L 1cla
9:
end for
10: end for
11: Stage 2: Fine-Tune the Entire Model (FE+Classifier)
12: for c2 = 1 to M E 2 do
13:
for each batch (wt , yt ) in (W, Y) do
14:
The values of
15:
p 2 , L 2cla are presented in (8) and (9)
16:
θ F E , θc ← Make a gradient step to minimize L 2cla
17:
end for
18: end for
19: return θ = (θ F E , θc )

by pretraining and only train the classifier; in the second
stage (lines 11–19 in Algorithm 1), we train the whole
MFFTD, including the parameters of FE and classifier). The
two-stage training shares the same model architecture (FE as
shown in Fig. 3) and loss function as (9). Given the input
window wt and its label yt , FE outputs the extracted features F, and classifier takes as input the flattened features,
and outputs the anomaly probability p (when p is more
than 0.5, the input window wt is judged as an anomaly) as
follows:
p = σ (Flatten(F)W + b)

(8)

where σ is the sigmoid activation function, Flatten is the flatten
operation, and W and b are learnable parameters. Considering
the data imbalance between normal and anomalous temporal
data, the weighted binary cross-entropy is adopted to evaluate
the difference between the predicted probability and true label

3522810

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

TABLE I

as follows:
L cla = −

n
X



1
wi yi log pi + (1 − yi ) log(1 − pi )
n i=1

S IX T YPES OF FDI ATTACKS

(9)

where n is the batch size, and wi ∈ {0.1, 0.9} is the weight
with 0.9 for an anomaly. yi is the true label, and pi is the
predicted probability.
IV. E VALUATION E XPERIMENTS
A. Experimental Settings
In our work, a Python-based software platform is developed
to simulate multiple and typical ET behaviors in real-world
electricity consumption data, based on which our proposed
MFFTD scheme and the SOTA ETD baselines are implemented and comprehensively evaluated. In detail, this section
first describes the publicly used datasets, including the IRISH
dataset (given in Section IV-A) and the State Grid Corporation
of China (SGCC) dataset (given in Section IV-E). Then, six
false data injection (FDI) attacks that simulate multiple typical
ET behaviors are clearly provided in Section IV-A2. The
commonly used evaluation metrics are given in Section IV-A3.
Finally, the implementation details are listed in Section IV-A4,
including hardware and software configurations and hyperparameters’ settings.
1) Smart Meter Datasets: The smart meter dataset adopted
for our performance evaluation is publicly available from
the Irish CER smart metering project [29] which is widely
used in the research of ETD. The dataset contains more
than 500 days of smart meter data collected from over
5000 residential users and small- and medium-sized business
users during 2009 and 2010. The dataset is considered as not
tampered and can be used as ground truth because all the users
completed the pretrial or posttrial surveys. The sampling rate
of the smart meter is one temporal data point every half an
hour such that a daily load profile consists of 48 data points.
In the experiments, we use the collected data of 365 days,
drop the data of any user with nan (nan represents a null
value), recover the incorrect data, and normalize the data with
min–max normalization [30]. The detection window is set to
seven days, i.e., L = 336 instead of one day to improve
the performance of the detection. We divide 5000 users into
4000, 500, and 500 users for the pretraining set, validation set,
and test set. In each set, the whole electricity consumption
data are viewed as a long time series. In the pretraining
set, we randomly pick 1% daily electricity consumption data
tampered with certain attacks, and pick 9% as honest daily
electricity consumption data. In summary, the proportion of
unlabeled, fraudulent, and honest samples are 90%, 1%,
and 9%, respectively. The pretraining set is used to learn
the structure parameters of FE, and labeled samples in the
fine-tuning set are used to fine-tune the pretrained model.
In the validation set and test set, we randomly pick 10% daily
electricity consumption data tampered with certain attacks.
The left ones are normal data. The validation set is used to
judge whether overfitting happens and choose the best learned
parameters. The test set is used to evaluate performance.
2) Attack Model: The tampering behaviors of ET on load
profiles can be simulated by various types of FDI attacks.
In this study, we consider six types of FDI attacks widely used

Fig. 4. Example of daily electricity consumption and its tampered data
corresponding to six types of FDI attacks.

in [14] and [25] which are defined in Table I. In Table I,
x̃ t and xt are tampered and real electricity consumption at
timestamp t, respectively. X = {x1 , x2 , . . . , x48 } is the daily
electricity consumption of 48 data points collected by the
smart meter. max(X ), min(X ), and mean(X ) are the maximum value, minimum value, and average value of the daily
electricity consumption X , respectively.
Basically, there are two types of consumption attacks,
called reduced consumption attacks and load profile shifting
attacks [6]. Reduced consumption attacks (types 1–4) directly
reduce the electricity consumption data, while load profile
shifting attacks (types 5 and 6) shift the consumption data
at a high electricity price to the consumption data at a
low electricity price. As shown in Table I, type 1 attack
multiples the electricity consumption at the timestamp t with a
changing-with-t parameter αt ranging from 0.2 to 0.8. Type 2
attack reduces the daily electricity consumption by a randomly
chosen value γ smaller than the maximum value of the daily
consumption and keeps the positive values. Type 3 attack
retains the value no bigger than γ . Type 4 attack picks a time
period and sets the data over the time period to zero. Type 5
attack replaces the raw data with the average value of the
daily consumption multiplied with a parameter α ∈ (0.2, 0.8).
Type 6 attack inverts the whole daily consumption. An example of the daily electricity consumption and its tampered data
corresponding to six types of FDI attacks are shown in Fig. 4.
3) Evaluation Metrics: We adopt the F1 score, the area
under a receiver operating characteristic (ROC) curve (AUC),
recall, and false positive rate (FPR) as evaluation metrics. The
detection results can be divided into four categories, including

WANG et al.: MULTISCALE FEATURE FUSION TRANSFORMER DETECTOR FOR ET BASED ON SEMI-SUPERVISED LEARNING

3522810

TABLE II
P ERFORMANCE OF D IFFERENT M ETHODS

true positive (TP), false positive (FP), false negative (FN), and
true negative (TN). Here, we take predicting illegal users as
positive, so that the meanings of TP, FP, FN, and TN are as
follows:
1) TP: Number of illegal users correctly predicted as illegal
users.
2) FP: Number of benign users wrongly predicted as illegal
users.
3) FN: Number of illegal users wrongly predicted as benign
users.
4) TN: Number of benign users correctly predicted as
benign users.
Based on the above concept, precision, recall, and FPR are
defined to reflect the model’s ability to make the true detection
of the ET behavior, where Precision = (TP/(TP + FP)),
Recall = (TP/(TP + FN)), and FPR = (FP/(FP + TN)).
A high precision can significantly reduce the additional costs
incurred due to error detection and subsequent manual inspections; a high recall means that most of the anomalies are
detected; and a good model should have a high recall and
a low FPR. Then the F1 score, which is a comprehensive consideration of both precision and recall, is defined as follows:
2 × precision × recall
F1 score =
.
(10)
precision + recall
AUC represents the area under the ROC curve, which plots
the TP rate against the FPR at various threshold settings.
A higher AUC indicates better discrimination ability of the
model, with an AUC of 1 representing a perfect classifier.
4) Implementation Details: We implement all the methods
with Python-3.8.17, PyTorch-2.0.1, and PyTorch-Ignite-0.3.0.
We use the Adam optimizer to train all the models with a
learning rate of 0.001. We implement all the methods three
times on an Intel i3-12100F CPU and an NVIDIA GeForce
RTX 2060 12G GPU and report the results as the mean of
six FDI attacks. We use the hyperparameters of the baseline
models as presented in their respective papers. We choose the
following hyperparameters for our method.
1) Dimension of the embedding d = 128.
2) Number of the heads H = 8.
3) Number of the layers N = 3.
Note that the rationale of selecting these hyperparameters
is given in Section IV-C.
B. Performance Comparison
In this part, we compare the proposed MFFTD with four
SOTA ET methods, of which two are supervised learning
methods and two are semi-supervised methods. We implement
all these methods on the preprocessed data for fair comparison.

1) Time-Series Transformer: TST [19] uses the TE and
computes the relationship between data points at different
timestamps. TST is trained in the semi-supervised way. In the
unsupervised pretraining, TST completes the autoregressive
task of forecasting the masked temporal data points and is
implemented with lm = 8, r = 0.3. In supervised fine-tuning,
TST is trained to predict the probability of input being an
anomaly.
2) Patch TST: PatchTST [17] takes time-series segments
( p = 8) as input and is similarly trained in a semi-supervised
way. In the unsupervised pretraining, the model learns to
predict the randomly removed patches. In the supervised finetuning, the operation is the same as TST.
3) Conv-Attentional Transformer Neural Network: CATNN [14] divides the time series into several segments
( p = 8), uses conv-attentional module to embed the segments,
and uses transformer to extract global features by calculating
the self-attention between each segment. It is trained in a
supervised way to predict the anomaly probability of input.
4) Wide and Deep CNN (WDCNN): WDCNN [12] consists
of a wide component (a fully connected layer) and a deep CNN
component (stacked convolutional layers). We implement the
model with the length of fully connected layer in the wide and
deep CNN components as 90 and 90, respectively, the number
of filters in the convolutional layer as 60, and the number of
convolutional layers as 5.
Table II provide the performance comparison results of
different methods. The following results can be observed.
1) On average, MFFTD achieves the best results (0.848 in
F1 score, 0.972 in AUC, 0.862 in recall, and 0.019 in
FPR), with improvement of 3.8% in F1 score, 1.3%
in AUC, 2.6% in recall, and 17.3% in FPR over
the second-best method CA-TNN (0.809 in F1 score,
0.963 in AUC, 0.812 in recall, and 0.023 in FPR).
2) CA-TNN uses a conv-attentional module to automatically extract and implicitly fuse different types
of features in electricity consumption data ahead of
TE [14], which shares a similar idea with MFFTD
(adopting HPTE to fuse multiscale features). The advantage of our proposed MFFTD is to explicitly extract and
fuse multiple-scale features with variable patch size, and
therefore, MFFTD averagely outperforms CA-TNN.
3) Compared with TST, PatchTST roughly extracts the
temporal relationships in an ordered time-series through
one-shot and fix-sized patching, thus PatchTST performs
better than TST.
The number of parameters, average training time, and
average testing time for all the methods are also empirically
given in Table II for comparison. The number of trainable

3522810

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

TABLE III
T HEORETICAL A NALYSIS OF P ER -L AYER C OMPLEXITY
FOR D IFFERENT M ETHODS

parameters is derived from the neural network architectures,
encompassing both the FE and classifier components. Training
time reflects the duration required for the complete training
process across all the samples over 100 epochs on a GPU,
while testing time represents the time needed for a single
prediction for all the samples.
The theoretical analysis of per-layer complexity for different
methods is given in Table III. In our study, the sequence
length l is much bigger than embedding dimension d, thus
theoretically speaking, the training time of WDCNN should
be smaller than TST, which is consistent with our experimental results. CA-TNN is a hybrid model consisting of
CNN and TE with fixed patching size, such that its training
time is larger than WDCNN while being less than TST.
For our proposed
the computational complexity
P N MFFTD,
changes to O( i=1
li2 × d), where li is the sequence length
for the ith layer and different patching modes can greatly
influence the computational complexity, which is discussed
in Section IV-D.

Fig. 5.

Ablation analysis of MFFTD.

C. Analysis of the Selection of Main Hyperparameters
We conduct extensive experiments on the impact of three
important hyperparameters in MFFTD to empirically seek the
best settings. The results are presented in Table IV. As shown
in Table IV, the range of values for dimension of the embedding d and number of heads H are the same as TST [19] and
the best results are almost consistent, i.e., d = 128, H = 8.
The number of the HPTE layers decides the scales of fused
features. Empirically, moderate scales are suitable for anomaly
detection. The reason may lie in that our scheme uses the
variable patch size in each HPTE layer, and therefore, the
larger number of layers may lead to shorter size of each patch,
which results in TE focusing on local feature correlations, vice
versa for the smaller number of layers. In brief, empirically,
the dimension of the embedding, number of the heads, layers,
and patch size for each layer are chosen as 128, 8, 3, and
p1 , p2 , p3 = 2, 3, 8, respectively, in our experiments.
D. Ablation Analysis
An ablation study is conducted to demonstrate the impact
of the main components in the proposed MFFTD framework
on the ETD performance. Specifically, two variants of our
MFFTD are implemented as shown in Table V.
1) Variant MFFTD-H:MFFTD Without HPE: MFFTD-H
directly uses TE instead of HPTE and is trained with our
proposed semi-supervised way.

Fig. 6. Specific contribution to model performance in different settings of
multiscale patching. (a) Comparison between two patching modes: increasing
mode and decreasing mode. (b) Comparison within increasing mode.

2) Variant MFFTD-S:MFFTD Without Self-Supervised Pretraining: MFFTD-S keeps the neural network architecture, but
is directly trained in a supervised way.

WANG et al.: MULTISCALE FEATURE FUSION TRANSFORMER DETECTOR FOR ET BASED ON SEMI-SUPERVISED LEARNING

3522810

TABLE IV
P ERFORMANCE OF T HREE P RIMARY H YPERPARAMETERS

TABLE V

TABLE VI

S TRUCTURE OF MFFTD VARIANTS

P ERFORMANCE OF D IFFERENT M ETHODS ON THE SGCC DATASET

Fig. 5 illustrates the average F1 score, AUC, recall, and FPR
of six ET attacks and the following results can be obtained.
1) MFFTD-H performs much worse, compared with
MFFTD, with nearly 14.7% drop in terms of F1
score, 2.7% drop in terms of AUC, 13.5% drop in
terms of recall, and 110.5% growth in terms of FPR.
It demonstrates that the designed HPTE can effectively
fuse multiscale feature thus improving the detection
performance.
2) MFFTD achieves better performance than MFFTD-S,
which implies that semi-supervised learning effectively
leverages the underlying distribution and general patterns of both labeled and unlabeled data to enhance
predictive performance over a broader dataset. The
ablation results show that our proposed semi-supervised
training strategy can improve the ETD performance.
We also provide the results of two patching modes as
shown in Fig. 6 to analyze each specific contribution to model
performance. In detail, the temporal sequence of length 48
(i.e., the number of temporal data points gathered in a whole
day) is hierarchically divided into three layers, i.e., p1 × p2 ×
p3 = 48, and two kind of patching strategies are designed:
decreasing mode p1 ≥ p2 ≥ p3 and increasing mode p1 ≤
p2 ≤ p3 .
The following results can be empirically obtained.
1) Increasing mode is better than decreasing mode in
terms of performance metrics: Fig. 6(a) shows that
the setting p1 × p2 × p3 = 2 × 4 × 6 achieves 1.9%
higher recall than the opposite P
setting. However the
N
computational complexity is O( i=1
li2 × d). In the
increasing mode, the sequence length li for the ith layer
is normally bigger than that in decreasing mode. So it
takes more time to train the whole model.
2) For the detailed choice in increasing mode, we empirically find from Fig. 6(b) that the model performs
best under the setting where the front patching size is
slightly smaller, and the rear patching size increases
significantly. The observations are analogous to the

design of the well-known architecture of ResNet [31],
in which the receptive field is also in an increasing way.
The rationale of beginning with small patch size lies in
that in early layers, the local features should be extracted
through small patch size, and as the network deepens,
more extract feature should be emphasized through large
patch size.
E. Performance Evaluation on the SGCC Dataset
We further evaluated the performance of MFFTD alongside the same baseline methods on another dataset: the
SGCC [12]. This dataset contains the electricity consumption
data of 42 372 electricity customers within 1035 days (from
January 1, 2014 to October 31, 2016) released by SGCC
(http://www.sgcc.com.cn/). We use the same data preprocessing methods for the Irish dataset, and for details refer
to Section IV-A.
Performance results are shown in Table VI. Similarly, our
proposed MFFTD achieves the best performance among all
the schemes, which is consistent with the results obtained on
the Irish dataset.
V. C ONCLUSION AND F UTURE W ORK
This article proposes a novel semi-supervised-learningbased multiscale feature fusion TE for effectively and
efficiently detecting ET, MFFTD. Specifically, the designed
hierarchical patching with variable patch size can fuse the
multiscale feature of the time series, and thus greatly facilitate the effective ETD. Furthermore, MFFTD is trained in
a semi-supervised manner, i.e., self-supervised pretraining
and supervised fine-tuning, which can efficiently leverage
both abundant unlabeled temporal data and a small percentage of labeled data available. Specifically, unlabeled data
are used in the pretraining process to extract general feature to assist the downstream ETD task. Experiments are
conducted on a real-world electricity consumption dataset,

3522810

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

and the results show that our proposed ETD framework
MFFTD can effectively detect the anomalous electricity behaviors and outperforms SOTA other transformer-based ETD
methods.
The future work includes the following aspects. First, our
work uses the historical load profile to train the ETD model,
which is essentially univariate time-series anomaly detection.
If other features would be available, e.g., customers’ traits
and weather information, multivariate and their relationships
can be explored for more accurate ETD. Second, our work
follows the semi-supervised learning paradigm: Pretraining
with pretext task, and fine-tune using small percentage of
labeled anomalous samples from downstream task, it can be
effective for known anomaly types, but may be vulnerable to
the emerging unknown anomaly types. One potential solution
is to learn data representations assisted by a few labeled
anomalous samples: The representations are optimized such
that these normal instances are located in dense neighborhoods
around the designated origin in latent space, while the anomalous samples are distributed far from origin. Then, the distance
of the representation of sample to the origin is viewed as its
anomaly score for ETD.
R EFERENCES
[1] M. Ahmed et al., “Energy theft detection in smart grids: Taxonomy, comparative analysis, challenges, and future research directions,” IEEE/CAA J. Autom. Sinica, vol. 9, no. 4, pp. 578–600,
Apr. 2022.
[2] T. Ahmad, H. Chen, J. Wang, and Y. Guo, “Review of various
modeling techniques for the detection of electricity theft in
smart grid environment,” Renew. Sustain. Energy Rev., vol. 82,
pp. 2916–2933, Feb. 2018. [Online]. Available: https://www.
sciencedirect.com/science/article/pii/S1364032117314090
[3] G. M. Messinis and N. D. Hatziargyriou, “Review of nontechnical loss detection methods,” Electr. Power Syst. Res., vol. 158,
pp. 250–266, May 2018. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S0378779618300051
[4] Y. Liu, T. Liu, H. Sun, K. Zhang, and P. Liu, “Hidden electricity theft by exploiting multiple-pricing scheme in smart grids,”
IEEE Trans. Inf. Forensics Security, vol. 15, pp. 2453–2468,
2020.
[5] Z. Yan and H. Wen, “Performance analysis of electricity theft detection
for the smart grid: An overview,” IEEE Trans. Instrum. Meas., vol. 71,
pp. 1–28, 2022.
[6] X. Xia, Y. Xiao, W. Liang, and J. Cui, “Detection methods in smart
meters for electricity thefts: A survey,” Proc. IEEE, vol. 110, no. 2,
pp. 273–319, Feb. 2022.
[7] E. Stracqualursi, A. Rosato, G. Di Lorenzo, M. Panella, and R. Araneo,
“Systematic review of energy theft practices and autonomous detection through artificial intelligence methods,” Renew. Sustain. Energy
Rev., vol. 184, Sep. 2023, Art. no. 113544. [Online]. Available:
https://www.sciencedirect.com/science/article/pii/S136403212300401X
[8] R. Xia, Y. Gao, Y. Zhu, D. Gu, and J. Wang, “An attentionbased wide and deep CNN with dilated convolutions for detecting
electricity theft considering imbalanced data,” Electric Power Syst.
Res., vol. 214, Jan. 2023, Art. no. 108886. [Online]. Available:
https://www.sciencedirect.com/science/article/pii/S0378779622009105
[9] E. U. Haq, C. Pei, R. Zhang, H. Jianjun, and F. Ahmad,
“Electricity-theft detection for smart grid security using smart
meter data: A deep-CNN based approach,” Energy Rep., vol. 9,
pp. 634–643, Mar. 2023. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S2352484722024581
[10] H.-X. Gao, S. Kuenzel, and X.-Y. Zhang, “A hybrid ConvLSTM-based
anomaly detection approach for combating energy theft,” IEEE Trans.
Instrum. Meas., vol. 71, pp. 1–10, 2022.
[11] A. Takiddin, M. Ismail, M. Nabil, M. M. E. A. Mahmoud, and
E. Serpedin, “Detecting electricity theft cyber-attacks in AMI networks using deep vector embeddings,” IEEE Syst. J., vol. 15, no. 3,
pp. 4189–4198, Sep. 2021.

[12] Z. Zheng, Y. Yang, X. Niu, H. Dai, and Y. Zhou, “Wide and deep
convolutional neural networks for electricity-theft detection to secure
smart grids,” IEEE Trans. Ind. Informat., vol. 14, no. 4, pp. 1606–1615,
Apr. 2018.
[13] X. Xia et al., “ETD-ConvLSTM: A deep learning approach for electricity
theft detection in smart grids,” IEEE Trans. Inf. Forensics Security,
vol. 18, pp. 2553–2568, 2023.
[14] J. Shi, Y. Gao, D. Gu, Y. Li, and K. Chen, “A novel approach to
detect electricity theft based on conv-attentional transformer neural
network,” Int. J. Electr. Power Energy Syst., vol. 145, Feb. 2023,
Art. no. 108642. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S014206152200638X
[15] J. Kim, H. Kang, and P. Kang, “Time-series anomaly detection
with stacked transformer representations and 1D convolutional
network,” Eng. Appl. Artif. Intell., vol. 120, Apr. 2023,
Art. no. 105964. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S0952197623001483
[16] Q. Wen et al., “Transformers in time series: A survey,” in Proc.
32nd Int. Joint Conf. Artif. Intell., 2023, pp. 6778–6786, doi:
10.24963/ijcai.2023/759.
[17] Y. Nie, N. H. Nguyen, P. Sinthong, and J. Kalagnanam, “A time
series is worth 64 words: Long-term forecasting with transformers,”
in Proc. 11th Int. Conf. Learn. Rep., Jan. 2022. [Online]. Available:
https://openreview.net/forum?id=Jbdc0vTOcol
[18] W. Zhang and Y. Dai, “A multiscale electricity theft detection model
based on feature engineering,” Big Data Res., vol. 36, May 2024,
Art. no. 100457. [Online]. Available: https://www.sciencedirect.
com/science/article/pii/S2214579624000339
[19] G. Zerveas, S. Jayaraman, D. Patel, A. Bhamidipaty, and C. Eickhoff,
“A transformer-based framework for multivariate time series representation learning,” in Proc. 27th ACM SIGKDD Conf. Knowl. Discovery
Data Mining, New York, NY, USA, Aug. 2021, pp. 2114–2124, doi:
10.1145/3447548.3467401.
[20] Y. Zhu et al., “Hybrid-order representation learning for electricity theft
detection,” IEEE Trans. Ind. Informat., vol. 19, no. 2, pp. 1248–1259,
Feb. 2023.
[21] M.
Buzau,
J.
Tejedor-Aguilera,
P.
Cruz-Romero,
and
A. Gómez-Expósito, “Hybrid deep neural networks for detection
of non-technical losses in electricity smart meters,” IEEE Trans. Power
Syst., vol. 35, no. 2, pp. 1254–1263, Mar. 2020.
[22] Y. Huang and Q. Xu, “Electricity theft detection based on
stacked sparse denoising autoencoder,” Int. J. Electr. Power Energy
Syst., vol. 125, Feb. 2021, Art. no. 106448. [Online]. Available:
https://www.sciencedirect.com/science/article/pii/S014206151933666X
[23] A. Takiddin, M. Ismail, U. Zafar, and E. Serpedin, “Deep autoencoderbased anomaly detection of electricity theft cyberattacks in smart grids,”
IEEE Syst. J., vol. 16, no. 3, pp. 4106–4117, Sep. 2022.
[24] G. Pang, C. Shen, L. Cao, and A. V. D. Hengel, “Deep learning for
anomaly detection: A review,” ACM Comput. Surveys, vol. 54, no. 2,
pp. 1–38, Mar. 2021, doi: 10.1145/3439950.
[25] T. Hu, Q. Guo, X. Shen, H. Sun, R. Wu, and H. Xi, “Utilizing unlabeled
data to detect electricity fraud in AMI: A semisupervised deep learning
approach,” IEEE Trans. Neural Netw. Learn. Syst., vol. 30, no. 11,
pp. 3287–3299, Nov. 2019.
[26] A. Zeng, M. Chen, L. Zhang, and Q. Xu, “Are transformers effective for
time series forecasting?” in Proc. AAAI Conf. Artif. Intell., Jun. 2023,
vol. 37, no. 9, pp. 11121–11128.
[27] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural
Inf. Process. Syst., vol. 30, I. Guyon et al., Ed. Red Hook, NY, USA:
Curran Associates, Jun. 2017, pp. 5998–6008. [Online]. Available:
https://proceedings.neurips.cc/paper_files/paper/2017/file/3f5ee243547
dee91fbd053c1c4a845aa-Paper.pdf
[28] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,”
Proc. VLDB Endow., vol. 15, no. 6, pp. 1201–1214, Feb. 2022, doi:
10.14778/3514061.3514067.
[29] Cer Smart Metering Project-Electricity Customer Behaviour Trial,
2009–2010, Commission Energy Regulation (CER), Dublin, Ireland,
2012.
[30] R. Qi, J. Zheng, Z. Luo, and Q. Li, “A novel unsupervised data-driven
method for electricity theft detection in AMI using observer meters,”
IEEE Trans. Instrum. Meas., vol. 71, pp. 1–10, 2022.
[31] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 770–778.
PAPER_TEXT
