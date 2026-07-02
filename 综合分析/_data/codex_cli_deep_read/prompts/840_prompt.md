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
# [840] VDDFormer: A Variable Dependency Discrepancy-Based Transformer for Multivariate Time Series Anomaly Detection
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
编号：840
题名：VDDFormer: A Variable Dependency Discrepancy-Based Transformer for Multivariate Time Series Anomaly Detection
年份：2025
DOI：10.1109/tbdata.2025.3600004
来源：IEEE Transactions on Big Data
PDF：paper/10.1109_TBDATA.2025.3600004.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\840.txt
- 原始字符数：68773
- 本次发送字符数：68773
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
34

IEEE TRANSACTIONS ON BIG DATA, VOL. 12, NO. 1, JANUARY/FEBRUARY 2026

VDDFormer: A Variable Dependency
Discrepancy-Based Transformer for
Multivariate Time Series Anomaly Detection
Bo Liu , Lingling Tao , Xiaodan Chen , and Zhijun Li

Abstract—The dynamics of multivariate time series (MTS) data
are jointly characterized by its nonlinear temporal dependencies
and complex variable dependencies, making unsupervised time
series anomaly detection a challenging task. Existing methods
primarily rely on prediction or reconstruction errors, neglecting
the valuable information within the variable dependencies. In
this paper, we propose a variable dependency discrepancy-based
Transformer (VDDFormer) for unsupervised MTS anomaly detection. VDDFormer comprises a variable correlation encoder, a
temporal dependency encoder, and a reconstruction decoder. The
variable correlation encoder capitalizes on a variable dependency
attention mechanism, which employs self-attention to learn the
global variable dependencies; meanwhile, the local variable dependencies are captured by the adaptive correlation matrix. The
global and local variable dependencies are then used to compute
the variable dependency discrepancy as a new intrinsic property to
distinguish between normal and abnormal patterns. By integrating
this new discrepancy with the reconstruction error, the model
effectively enhances its anomaly differentiation capability. Extensive experiments on five real-world anomaly detection datasets
demonstrate that VDDFormer effectively and robustly detects
group anomaly patterns by leveraging the variable dependency
discrepancy and achieves state-of-the-art performance on four out
of the five datasets.
Index Terms—Multivariate time series, anomaly detection,
variable dependency discrepancy, variable dependency attention.

I. INTRODUCTION
HE proliferation of interconnected devices in modern industrial systems necessitates the use of numerous sensors
to monitor their health since anomalies are inevitable and can
incur significant economic losses. The continuously recorded
sensor data forms a vast collection of multivariate time series. To
ensure security and prevent financial repercussions, effectively
detecting abnormal time points within the multivariate time

T

Received 10 September 2024; revised 1 August 2025; accepted 11 August
2025. Date of publication 19 August 2025; date of current version 14 January
2026. This work was supported in part by the Shenzhen College Stability
Support Plan under Grant GXWD20220811173233001, and in part by Shenzhen Science and Technology Program under Grant JCYJ20241202123503005,
Grant ZDSYS20230626091203008, Grant KQTD20240729102154066, and
Grant ZDSYS20210623091809029. Recommended for acceptance by L. Y. Wu.
(Corresponding authors: Lingling Tao; Zhijun Li.)
Bo Liu, Xiaodan Chen, and Zhijun Li are with the Harbin Institute
of Technology, Harbin 150001, China (e-mail: 23B936027@stu.hit.edu.cn;
21B303004@stu.hit.edu.cn; lizhijun_os@hit.edu.cn).
Lingling Tao is with the Harbin Institute of Technology, Shenzhen 518055,
China (e-mail: taolingling@hit.edu.cn).
Digital Object Identifier 10.1109/TBDATA.2025.3600004

Fig. 1. Example of anomalies in the SWaT dataset and anomaly scores
obtained by existing methods. FIT101, LIT101, MV101, P101, and AIT201
are the five sensors in the SWaT dataset. Moments with higher anomaly scores
obtained by GDN, Anomaly Transformer (A.T.), MEMTO, and VDDFormer
(ours) methods are more likely to be identified as anomalies. The red background
interval in the figure represents the abnormal segment. The red dashed circles
enclose events that are incorrectly identified as anomalies.

series data becomes crucial in modern industrial systems [1], [2],
[3]. However, anomalies are often rare and hidden by the sheer
volume of normal data in practice. This makes manual labeling
of anomalies very expensive and even impractical, rendering
supervised anomaly detection techniques unsuitable.
Unsupervised anomaly detection for real-world MTS is challenging due to the intricate temporal and variable dependencies
inherent in the data. These dependencies are further complicated
by the dynamic variable correlations, where changes in one
variable can trigger a cascade of corresponding changes in
others. For instance, as illustrated in Fig. 1, the sensors FIT101,
LIT101, MV101, and P101 exhibit intricate correlations and
synchronized periodic fluctuations. When FIT101 experiences
an anomaly, similar abnormalities appear in LIT101, MV101,
and P101, demonstrating a group anomaly pattern characterized by: during anomalies, long-term and short-term abnormal
variable clusters maintain similar dependency patterns (relatively small distribution discrepancy), whereas normal states

2332-7790 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

LIU et al.: VDDFORMER: A VARIABLE DEPENDENCY DISCREPANCY-BASED TRANSFORMER FOR MULTIVARIATE

exhibit stable long-term variable dependencies contrasting with
dynamic short-term variable interactions (relatively large distributional contrast).
This discrepancy underscores the necessity of examining
collective behaviors to reveal group anomaly patterns, while
individual and local inspections might miss them.
Spurred by its immense practical utility, a plethora of unsupervised anomaly detection algorithms have been proposed in the
literature. Among these, classical statistical learning methods
form a notable category, encompassing principal component
analysis-based techniques [4], [5], one-class learning-based approaches [6], [7], [8], and density estimation-based methods [9],
[10]. These statistical methodologies often depend on manually engineered features and generally fail to account for the
temporal dynamics or intricate relationships between variables.
As a result, their efficacy in capturing normal patterns within
multivariate time series data is compromised. To leverage the
powerful representation learning ability of deep neural networks,
deep learning-based methods have gained prominence in recent
years. These methods involve the use of specifically designed
Recurrent Neural Networks (RNNs) [11], [12], [13] that perform
self-supervised prediction or reconstruction tasks to discern
normal patterns. During the detection phase, reconstruction
errors are commonly employed as discriminative criteria, where
patterns with substantial reconstruction errors are classified as
anomalous.
Despite the advancements in prediction and reconstructionbased anomaly detection methods, a critical oversight in these
approaches is the failure to account for the intricate relationships
between variables. This oversight can result in sub-optimal performance during reconstruction or prediction, which in turn diminishes the overall effectiveness of the anomaly detection process. To address this shortcoming, several methodologies [14],
[15], [16], [17] have emerged that harness the power of Graph
Neural Networks (GNNs) or Variational Auto-Encoder networks (VAEs) to model the dependencies or distributions of
dependencies among variables. However, these strategies predominantly continue to rely on prediction error or reconstruction
error as the benchmarks for identifying anomalies, a criterion
that may not suffice in the presence of complex dependencies,
as it does not fully exploit the rich information embedded
within variable dependencies. Figure 1 highlights that when
faced with complex variable interdependencies, the anomaly
scores produced by current techniques (such as GDN [14] and
MEMTO [18]) may result in erroneous alerts, culminating in
the incorrect classification of numerous normal occurrences as
anomalies. Recent developments in Transformer-based models
have yielded significant progress in time series prediction [19],
[20], [21], [22], [23], [24] and anomaly detection [18], [25],
largely owing to their wide receptive field. Despite these strides,
these approaches have not fully capitalized on the exploitation
of variable dependencies, thus constraining their detection capability for group anomalies.
To address the shortcomings of existing methods, in this paper,
we propose a VDDFormer developed with a new criterion—
variable dependency discrepancy. VDDFormer comprises three
components: a variable correlation encoder, a temporal dependency encoder, and a reconstruction decoder. The variable

35

correlation encoder is designed to capture both global and local
dependencies, thereby quantifying the variable dependency discrepancy. The temporal dependency encoder is constructed to
model the temporal dependencies of MTS data by embedding
observations at each time step as tokens and learning their
self-attention map to capture temporal dependencies. Finally,
the reconstruction decoder is designed to combine the outputs
of the above two encoders to reconstruct the data. VDDFormer
is developed based on the characteristic that group anomalies
exhibit relatively small discrepancies between long-term and
short-term variable dependencies, contrasting with relatively
large distribution discrepancies in normal states. Specifically,
we embed the entire series of each variable within a long time
window as individual tokens and compute their self-attention
map. This attention map, which can reflect the long-time variable dependencies, is referred to as global dependency. For
short-term variable relationships, the dependency weight matrix at each time step is modeled using the adaptive adjacency matrix approach proposed in [26]. This matrix captures
instantaneous interactive correlations among variables and is
termed local dependency. As both global dependency and local dependency measure the group behavior collectively, they
offer us a new criterion, dubbed variable dependency discrepancy, to identify group anomaly patterns by quantifying
the discrepancy between global dependency and local dependency. The combination of variable dependency discrepancy
and reconstruction error establishes the eventual criterion, effectively enhancing the performance of group anomaly detection. In summary, our main contributions are summarized as
follows:
r We propose a new criterion for unsupervised MTS anomaly
detection, variable dependency discrepancy, which can
identify group anomaly patterns that are beyond the detection capability of existing methods.
r We develop a new unsupervised MTS anomaly detection method—VDDFormer—equipped with the proposed
variable dependency discrepancy. VDDFormer consists of
a variable correlation encoder with variable dependency
attention, a temporal dependency encoder for modeling
temporal dependencies, and a reconstruction decoder that
generates reconstruction output.
r VDDFormer achieves state-of-the-art performance on four
out of five public MTS anomaly detection benchmarks,
which verifies the effectiveness of our proposed variable
dependency discrepancy and anomaly detection method.
The remainder of this paper is organized as follows. In Section II, we briefly review the related work in MTS anomaly
detection. The problem statement is presented in Section III. We
then give the details of the proposed VDDFormer in Section IV
and present the experimental results as well as the corresponding analysis in Section V. Finally, we conclude the paper in
Section VI.
II. RELATED WORK
Due to the importance of MTS in various fields, unsupervised
MTS anomaly detection is a well-researched area. In this section,
we provide an overview of existing approaches, and then discuss

36

IEEE TRANSACTIONS ON BIG DATA, VOL. 12, NO. 1, JANUARY/FEBRUARY 2026

the rise of Transformer-based approaches for unsupervised MTS
anomaly detection.

variable dependencies, ensuring more accurate reconstruction
in MTS.
To effectively model relationships between variables,
GNNs [37], [38] have been widely applied to anomaly detection
tasks. For example, the CoLA algorithm [39] develops a GNNbased contrastive learning framework for anomaly detection in
attributed networks. In MTS anomaly detection, GNN-based
methods [14], [15] have also been widely adopted. GReLeN [16]
leverages VAE for feature representation and integrates GNN to
model variable dependencies, thereby enhancing the model’s
capability to predict normal patterns and to identify anomalies.

A. Unsupervised Multivariate Time Series Anomaly Detection
Unsupervised MTS anomaly detection methods can be
broadly categorized into two types of algorithms: classical methods and deep learning-based methods.
Classical methods primarily include one-class learning-based
methods and density estimation-based methods. One-class
SVM [6] and SVDD [7] are typical one-class learning-based
anomaly detection algorithms. Specifically, one-class SVM
learns a separating hyperplane to distinguish normal data from
anomalies, while SVDD constructs a hypersphere to encapsulate
the normal data, both leveraging the concept of support vectors
in their modeling. A typical density-based algorithm is LOF [9],
which identifies outliers by calculating the local outlier factor.
The local outlier factor measures the isolation of an object from
its neighbors.
Deep learning methods detect anomalies in MTS by learning normal patterns through neural networks. These models primarily identify anomalies by measuring reconstruction errors (reconstruction-based methods) or prediction errors
(prediction-based methods). The reconstruction-based method
LSTM-VAE [13] combines Long Short-Term Memory (LSTM)
and VAE to respectively capture temporal patterns and reconstruct the expected distribution of normal patterns. Additionally,
Generative Adversarial Network (GAN)-based approaches [27],
[28], [29] employ adversarial regularization to learn temporal
normal patterns for anomaly detection. In contrast to anomaly
detection based on reconstruction error, autoregressive models
detect anomalies using prediction error. Hundman et al. [11]
employ LSTM networks to learn temporal representations and
perform anomaly detection by leveraging prediction error. Recently, hybrid methods have been proposed to integrate the
strengths of different models for enhanced anomaly detection.
For example, Deep SVDD [30] uses deep neural networks to
minimize features to separate hyperplanes and identify anomalies. DAGMM [31] and MPPCACD [32] combine deep representation methods with Gaussian Mixture Models (GMMs) to
estimate representation density for anomaly detection. Frehner
et al. [33] propose an autoencoder-based framework combined
with Kernel Density Estimation (KDE) on reconstruction errors
to enhance the robustness of time series anomaly detection.
ITAD [34] proposes an anomaly detection method based on
tensor decomposition and clustering. THOC [35] leverages
one-class learning with a dilated RNN to capture multi-scale
temporal patterns and employs hierarchical clustering to define
one-class targets for anomaly detection.
The aforementioned deep learning methods predominantly
model temporal patterns in MTS but neglect the crucial assistance of variable correlations for time series modeling. To
address this issue, OmniAnomaly [36] employs a Stochastic Recurrent Neural Network (SRNN) with planar normalization flow
to model temporal dependencies in latent variables, enhancing
the reconstruction of normal patterns. InterFusion [17] adopts
a hierarchical VAE to jointly model temporal dynamics and

B. Transformer-Based Multivariate Time Series Anomaly
Detection
Benefiting from the ability of self-attention to capture longterm dependencies, Transformers [40], [41], [42], [43] have
achieved remarkable results in MTS analysis. Recently, many
Transformer-based models have achieved significant performance improvements in MTS prediction [19], [20], [21], [22],
[23], [24], [44]. PatchTST [45] demonstrates effectiveness in
prediction through its patching design of Transformer-based
model. For the task of MTS anomaly detection, Xu et al. [25]
propose the Anomaly Transformer to detect anomalies in MTS.
This method combines the association discrepancy of temporal patterns in MTS with the reconstruction error as a detection criterion, achieving effective anomaly detection. Song et
al. [18] introduce a memory-guided Transformer architecture
employing a reconstruction-based approach to mitigate the overgeneralization problem in the anomaly detection task.
Some existing Transformer-based methods [44] embed subseries of each variable as tokens and apply self-attention to these
tokens for time series modeling. While enhancing modeling
capabilities through variable relationships, these methods do not
adequately explore the discriminative potential of variable correlations for anomaly differentiation. To address this limitation, we
propose VDDFormer with a variable dependency attention that
simultaneously models global and local dependencies among
variables, leveraging their distribution discrepancy as a new
intrinsic criterion (termed variable dependency discrepancy) to
distinguish normal and abnormal patterns. By integrating this
discrepancy with the reconstruction error, VDDFormer achieves
robust anomaly detection performance.
III. PROBLEM STATEMENT
Multivariate Time Series: We define the multivariate time
series used as input for anomaly detection as X ∈ RT ×N , where
N variables are observed over T timestamps. The i-th row of
X, xi ∈ RN , corresponds to the observations of all variables at
timestamp i. The n-th column of X, denoted as x(n) ∈ RT , represents the observations of the variable n. For a long time series,
we use a sliding window of length T to generate fixed-length
inputs. Additionally, we use xi,n to denote the observation of
the variable n at timestamp i.
Anomaly Detection: The task of multivariate time series
anomaly detection is to output a binary vector y ∈ RT based on

LIU et al.: VDDFORMER: A VARIABLE DEPENDENCY DISCREPANCY-BASED TRANSFORMER FOR MULTIVARIATE

37

Fig. 2. VDDFormer architecture. VDDFormer consists of a temporal dependency encoder, a variable correlation encoder, and a reconstruction decoder.
The temporal dependency encoder learns the temporal dependencies of MTS. Variable correlation encoder utilizes the variable dependency attention to embody
the variable dependency discrepancy, which is the inherent distinguishing property between normal and anomaly based on variable dependency. The reconstruction
decoder combines the outputs of the temporal dependency encoder and variable correlation encoder to obtain the final model’s reconstruction output.

the given input X ∈ RT ×N , where yi ∈ {0, 1}, with 0 indicating
a normal time point and 1 denoting an abnormal time point.
IV. METHODOLOGY
In this section, we introduce the proposed method
VDDFormer. VDDFormer comprises three components: a variable correlation encoder, a temporal dependency encoder, and
a reconstruction decoder. The architecture of VDDFormer is
shown in Fig. 2. First, we present the variable correlation encoder. Based on the discovery of variable dependency discrepancy, we devise a variable dependency attention mechanism
that simultaneously models global and local dependencies. By
quantifying the distribution divergence between global and local
dependencies, the variable dependency discrepancy is derived
and used as a criterion for anomaly detection. In addition,
recognizing the importance of modeling temporal dependencies
in MTS data, we construct the temporal dependency encoder,
which treats the data corresponding to each time step as tokens
and models the temporal dependencies of MTS by computing
self-attention map. Subsequently, to enable the model to better
capture temporal patterns and variable dependencies in MTS
data, we design a reconstruction decoder that integrates dual
encoder representations, generating temporal-variable reconstructions of MTS. This dual feature fusion mechanism captures
joint temporal-variable properties, effectively guiding the model
to learn normal patterns in MTS data. Finally, for robust anomaly
detection, the combination of reconstruction error and variable
dependency discrepancy is utilized as a new anomaly detection
criterion.
A. Variable Correlation Encoder
The vanilla single-branch self-attention in Transformers [46]
cannot simultaneously capture global dependency and local
dependency. To address this limitation, we propose a variable
dependency attention mechanism that concurrently models both
global and local dependencies to compute variable dependency
discrepancy. We construct a variable correlation encoder using

this mechanism as the core component. The variable correlation
encoder consists of multiple basic modules, each containing a
variable dependency attention block and a feed-forward layer.
The stacking of multiple modules enables the learning of latent
variable dependencies at different levels. Assuming the variable
correlation encoder consists of L modules, with length-T input
time series denoted as X ∈ RT ×N , the operations of the l-th
module can be expressed as follows:




Zvar,l = LN VDA Xvar,l-1 , X + Xvar,l-1




Xvar,l = LN FeedFoward Zvar,l + Zvar,l ,
(1)
where Xvar,l ∈ RN ×dvar , l ∈ {1, · · ·, L} denotes the output of
the l-th module in the variable correlation encoder with dvar
channels. The initial input Xvar,0 = VariableEmbedding(X)
represents the embedded raw series, where Xvar,0 ∈ RN ×dvar .
Specifically, unlike previous Transformer-based models [18],
[25] that embed all variables at the same timestamp as a token,
our VariableEmbedding(·) method embeds the entire series of
each variable within the sliding window as individual tokens.
LN(·) denotes layer normalization as widely adopted in [46].
Zvar,l ∈ RN ×dvar is the hidden representation of the l-th module.
VDA(·, ·) represents the variable dependency attention, which
captures global and local dependencies to compute the variable
dependency discrepancy. We will elaborate on this attention
mechanism in the following content.
Variable Dependency Attention Mechanism: The variable dependency attention mechanism is the core component of the
variable correlation encoder, whose pipeline is illustrated in
Fig. 3. As aforementioned, the variable dependency discrepancy
is computed by measuring the distribution distance between
global and local dependencies. To overcome the limitations of
vanilla single-branch self-attention, we implement a dual-branch
attention mechanism that allows for the concurrent extraction
of both global and local dependencies. For local dependency,
the adaptive adjacency matrix method [26] is employed to
obtain the dependency weights among variables at each time
step, followed by the application of the TopK strategy to prune

38

IEEE TRANSACTIONS ON BIG DATA, VOL. 12, NO. 1, JANUARY/FEBRUARY 2026

Fig. 3. Variable dependency attention mechanism (left) and diagram of variable dependency discrepancy (right). Variable dependency attention captures the
local dependency and global dependency simultaneously. The symmetrized KL divergence between local dependency and global dependency offers us a new
criterion, dubbed variable dependency discrepancy: In the right figure, the solid lines depict variable dependencies with color intensity indicating weight strength.
During anomalies, long-term and short-term abnormal variable clusters exhibit similar dependency patterns (relatively small distribution discrepancy), while normal
conditions feature stable long-term dependencies contrasting with dynamic fluctuating short-term dependencies, yielding relatively large distributional contrasts.

negligible weights from the local dependency. Specifically, the
local dependency is computed as follows:
M = Tanh (αEWe )




 
,
Al = TopK Softmax ReLU Tanh α MMT

(2)

where E ∈ RT ×N ×T is constructed by expanding the input
series X ∈ RT ×N with a singleton dimension and replicating
it T times to facilitate learning variable dependencies at each
timestep. α is a hyperparameter that controls the saturation
rate of the Tanh(·) activation function. The parameter matrix
of the linear layer is denoted by We ∈ RT ×de , while the TopK
operation retains the top K relation values from the local dependency. The final learned local dependency tensor is represented
as Al ∈ RT ×N ×N .
In the global dependency branch, the data corresponding to
each variable within the sliding window are embedded as tokens.
These tokens are fed into a self-attention mechanism to derive
the attention map among variables. The weights in the attention
map represent long-term dependencies among variables, i.e. the
global dependency. The global dependency computation for the
l-th module of the variable correlation encoder is formulated as
follows:
l
Q = Xvar,l-1 WQ
l
K = Xvar,l-1 WK
l
V = Xvar,l-1 WV


QKT
l
G = Softmax √
dvar

 var,l = Gl V,
Z

(3)

where Q, K, V ∈ RN ×dvar denote the query, key, and value of
the variable dependency attention, respectively. The parameter
l
l
l
, WK
, WV
∈ Rdvar ×dvar correspond to Q, K, V in
matrices WQ
the l-th module. In (3), the discrete weight matrix Gl ∈ RN ×N
representing global variable dependency is derived via the
 var,l ∈ RN ×dvar is the hidden represenSoftmax(·) operation. Z
tation of variable dependency attention in the l-th module of the
variable correlation encoder.
In summary, the variable dependency attention mechanism is
constructed by integrating the two branches, which essentially
combines (2) and (3). The function of the mechanism in the l-th
module is formalized as:


 var,l = VDA Xvar,l-1 , X ,
(4)
Al , Gl , Z
where VDA(·, ·) denotes the overall function of the variable
dependency attention, which takes Xvar,l-1 and X as inputs, and
produces Al (local dependency), Gl (global dependency) and
 var,l (hidden representation) as outputs.
Z
In the implementation of the global dependency branch for the
variable dependency attention mechanism, we employ a multihead attention version with h heads. Computing the variable
dependency discrepancy at each time step requires adaptively
generating a global dependency matrix for the corresponding
time step. To this end, we set the number of attention heads h
equal to the input series length T . For the m-th head in the
variable dependency attention, the query, key, and value are
dvar
defined as Qm , Km , Vm ∈ RN × h . After computing multihead attention, the attention maps {Glm ∈ RN ×N }1≤m≤h are
generated. To aggregate information across all heads, these
maps are stacked along a new dimension to form a new tensor Gl ∈ Rh×N ×N . Since h equals T , Gl ∈ RT ×N ×N . Furthermore, the variable dependency attention concatenates the

LIU et al.: VDDFORMER: A VARIABLE DEPENDENCY DISCREPANCY-BASED TRANSFORMER FOR MULTIVARIATE

 var,l ∈ RN × h }1≤m≤h of all heads to obtain the
outputs {Z
m
final hidden representation of the attention module, denoted as
 var,l ∈ RN ×dvar .
Z
Variable Dependency Discrepancy. The local and global
dependencies captured by the variable dependency attention
mechanism reflect different concentrations on the variable dependency distribution, whereas the prior and series associations
captured by Anomaly Transformer [25] reflect different concentrations on the temporal dependency distribution. Inspired by the
effectiveness of the symmetrized Kullback-Leibler (KL) divergence in Anomaly Transformer [25] for measuring distribution
discrepancy, we adopt it to quantify the discrepancy between
local and global dependencies. To amplify the discriminability
of the two distributions, we first aggregate and then average the
variable dependency discrepancy terms from the L modules of
the variable correlation encoder, yielding a more informative
metric. The variable dependency discrepancy is computed as:

L

1   l
KL Ai,:,:  Gli,:,:
VarDepDis(A, G) =
L
dvar

l=1



+ KL Gli,:,:  Ali,:,:

, (5)
i=1,...,T

where KL(·||·) denotes the KL divergence between two discrete
distributions. The term VarDepDis(A, G) ∈ RT , calculated as
the average of multiple module variable dependency discrepancies, reflects a more informative dissimilarity measure. Each
element in VarDepDis(A, G) corresponds to a time step in X.
As previously mentioned, global dependencies refer to longterm variable relationships that focus on learning stable intervariable correlations in extended temporal contexts, thus typically being stable. In normal scenarios, the variable correlations
at individual time steps are influenced by data variations and
periodic fluctuations, generating local dependencies that capture
complex relationships. This results in measurable distribution
discrepancies between local and global dependencies under
normal conditions. However, during anomalies, long-term and
short-term abnormal variable clusters maintain similar dependency patterns. Consequently, the local dependency distribution
approximates the global one, leading to relatively small variable
dependency discrepancies. This inherent property of the variable
dependency discrepancy is leveraged for anomaly detection.
B. Temporal Dependency Encoder
When modeling MTS data, temporal dependencies are
equally critical to consider along with variable dependencies.
To capture temporal dependency representations, we develop
the temporal dependency encoder specifically designed to learn
temporal features in MTS data. The encoder embeds all the
variables observed at each time step into tokens. These tokens are
then fed into a self-attention mechanism to compute an attention
map, in which the weights represent temporal dependencies
across time steps [25]. Effective learning of temporal dependencies plays a critical role in enhancing model performance.
The temporal dependency encoder is constructed by stacking

39

multiple basic modules, each composed of a self-attention block
and a feed-forward layer. Through this hierarchical architecture,
the encoder further improves the quality of temporal representations. Assuming the temporal dependency encoder consists of L
modules, with length-T input time series denoted as X ∈ RT ×N ,
the operations of the l-th module can be expressed as follows:


 
Ztemp,l = LN SA Xtemp,l-1 + Xtemp,l-1


 
Xtemp,l = LN SA Ztemp,l + Ztemp,l ,
(6)
where Xtemp,l ∈ RT ×dtemp , l ∈ {1, · · ·, L} denotes the output of
the l-th module in the temporal dependency encoder with dtemp
channels. The initial input Xtemp,0 = TemporalEmbedding (X)
represents the embedded raw series, where Xtemp,0 ∈ RT ×dtemp .
Specifically, TemporalEmbedding(·) embeds all variables at
the same timestamp as a token. Ztemp,l ∈ RT ×dtemp represents
the hidden representation of the l-th module of the temporal
dependency encoder. LN(·) denotes layer normalization. SA(·)
represents the self-attention.
C. Reconstruction Decoder
To enable the model to better learn the temporal patterns
and variable dependencies of normal MTS data, we propose the
reconstruction decoder that leverages the outputs of the dual encoders to reconstruct MTS. This dual feature fusion mechanism
captures temporal-variable characteristics, effectively guiding
the model to learn normal patterns in MTS data. The reconstruction output produced by the reconstruction decoder is formalized
as follows:


 = Xtemp,L Wtemp + Xvar,L Wvar T ,
(7)
X
where Xtemp,L ∈ RT ×dtemp denotes the output of the L-th module
(i.e., the final module) in the temporal dependency encoder.
Xvar,L ∈ RN ×dvar represents the output of the L-th module
(i.e., the final module) in the variable correlation encoder.
Wtemp ∈ Rdtemp ×N , Wvar ∈ Rdvar ×T denote the parameter matrices. Xtemp,L Wtemp ∈ RT ×N and (Xvar,L Wvar )T ∈ RT ×N are
combined to generate the final model’s reconstruction output
 ∈ RT ×N .
X
D. Optimization Strategy and Anomaly Criterion
Optimization Strategy: As an unsupervised anomaly detection
task, we utilize reconstruction loss to optimize the model. To
enhance the discriminability between normal and abnormal
patterns, we introduce the variable dependency discrepancy
as an auxiliary loss term. This loss term guides the model to
focus more on variable dependencies that facilitate time series
reconstruction, thus further sparsifying the global dependency.
Consequently, the enlarged distribution discrepancies between
local and global dependencies make normal patterns more distinguishable from abnormal patterns with relatively small variable
dependency discrepancies. The formula for the loss function is
as follows:
 A, G, λ; X = X − X
 2 −λ
L X,
F
× VarDepDis (A, G) 1 ,

(8)

40

IEEE TRANSACTIONS ON BIG DATA, VOL. 12, NO. 1, JANUARY/FEBRUARY 2026

 ∈ RT ×N denotes the final output of the model.  · F
where X
and  · 1 denote the Frobenius-norm and the 1-norm, respectively. λ is a hyperparameter to trade off the two loss terms.
When λ is positive, the optimization process amplifies the
variable dependency discrepancy of normal events during training, thereby better distinguishing normal events from abnormal
events through the enlarged discrepancy.
Anomaly Criterion: We combine the variable dependency discrepancy with the reconstruction error, using both the temporalvariable representation and the distinguishable variable dependency discrepancy. The final anomaly criterion is shown as
follows:

TABLE I
DETAILS OF DATASETS

AS (X) = Softmax (−VarDepDis(A, G))
 i,: 2
 Xi,: − X
2

i=1,···,T

,

(9)

where AS(X) ∈ RT denotes the anomaly score at each timestamp of X. An anomaly is flagged when the score exceeds
a certain threshold. The operator  represents element-wise
multiplication. Since anomalies exhibit relatively small variable dependency discrepancies, this characteristic distinguishes
them from normal patterns. By applying the negation operation
to the variable dependency discrepancies and performing the
Softmax(·) computation, then multiplying the resulting values
by reconstruction errors (typically large for abnormal events),
the anomaly scores become further amplified. Consequently, the
integration of the reconstruction error with the variable dependency discrepancy enables more discriminative identification of
anomalies, thereby enhancing the model’s anomaly detection
capability.
Notably, the variable dependency discrepancy captures differences in variable dependencies between short-term and longterm contexts to identify anomalies. In contrast, the association
discrepancy in Anomaly Transformer [25] identifies anomalies
solely through differences in association scope between normal
and abnormal time points but neglects variable correlations.
Therefore, the criterion combining reconstruction error with
variable dependency discrepancy is more discriminative than
the criterion combining reconstruction error with association
discrepancy, particularly for detecting group anomalies in MTS.
V. EXPERIMENTS
This section evaluates the effectiveness of VDDFormer using
five public MTS anomaly detection datasets. First, the benchmarks, baselines, experimental setups, and evaluation metrics
are described. Subsequently, the experimental results are presented and analyzed, including performance comparisons with
existing methods and findings from ablation studies. Finally,
systematic investigations are conducted to examine the impacts
of hyperparameters in VDDFormer, followed by an analysis of
its computational efficiency.
A. Datasets Description
Server Machine Dataset (SMD [36]): This 5-week MTS
dataset collects monitoring metrics from 28 servers at a large

internet company. Each server forms a sub-dataset split into
training and test sets of equal length. The test set labels every
timestamp as normal or abnormal. All servers share the same 38
synchronized metrics.
Soil Moisture Active Passive Satellite Dataset (SMAP [11]):
This dataset originates from telemetry data collected by NASA’s
Soil Moisture Active Passive satellite. It comprises 55 entities,
each characterized by 25 variables. The dataset is partitioned
into two subsets: an unlabeled training set and a labeled test set.
Mars Science Laboratory rover Dataset (MSL [11]): This
dataset is obtained from telemetry data generated by NASA’s
Curiosity Mars rover. The MSL dataset comprises 27 entities,
each containing 55 variable dimensions. It is split into a training
set and a test set. The training set does not contain labels, while
the test set contains labels.
Secure Water Treatment Dataset (SWaT [47]): The SWaT
dataset originates from experimental data collected on a water
treatment operation experiment bench. It comprises 51 variables
recorded over 11 days of continuous 24-hour operation. During
the first seven days, the system operated under normal conditions, while staged cyber-physical attacks were implemented
throughout the remaining four days. Each time step in the
final four-day period contains a binary label indicating whether
anomalies were present at that specific time point.
Pooled Server Metric Dataset (PSM [48]): This dataset is
collected by eBay, with data obtained from multiple internal
nodes of the application servers, and consists of 26 variable
dimensions. The following Table I provides information about
the five public datasets.
B. Baseline Methods
The proposed method is compared with 15 baseline
methods. The classical statistical learning approaches include OC-SVM [6], Isolation Forest [49] and LOF [9]). The
deep learning methods include reconstruction-based approaches
(LSTM-VAE [13], OmniAnomaly [36], InterFusion [17]);
prediction-based approaches (LSTM [11], GReLeN [16]); hybrid approaches (Deep SVDD [30], ITAD [34], DAGMM [31],
MPPCACD [32], THOC [35]); and Transformer-based

LIU et al.: VDDFORMER: A VARIABLE DEPENDENCY DISCREPANCY-BASED TRANSFORMER FOR MULTIVARIATE

methods adhering to the reconstruction paradigm (Anomaly
Transformer [25], MEMTO [18]).
r OC-SVM [6]: One-Class SVM uses normal data to create
a hyperplane. This hyperplane then acts as a boundary to
identify abnormal data points.
r IsolationForest [49]: Abnormal data are rare and unique,
making them more likely to be isolated than normal data.
The IsolationForest method employs the isolation forest
algorithm to partition the data. After partitioning, nodes
closer to the root node in the resulting trees are identified
as anomalies.
r LOF [9]: LOF determines whether a point is abnormal by
comparing its density with its neighboring points.
r LSTM-VAE [13]: LSTM-VAE uses LSTM networks for
temporal representation and VAE to reconstruct the expected distribution of normal patterns. It detects anomalies
through large reconstruction errors caused by the model’s
inability to reconstruct anomalies.
r OmniAnomaly [36]: OmniAnomaly applies stochastic recurrent neural networks and planar normalization flow
techniques to capture the temporal dependencies among
random variables in space. Then it discriminates anomalies
by reconstructing probabilities.
r InterFusion [17]: InterFusion uses a hierarchical VAE to
jointly model temporal patterns and variable dependencies,
ensuring more accurate reconstruction in MTS.
r Deep SVDD [30]: Deep SVDD uses a neural network
to minimize the feature space of samples and defines a
hypersphere. It then uses the distance between sample
points and the hypersphere’s center to identify anomalies.
r ITAD [34]: ITAD first constructs a third-order tensor for the
entire dataset. It then decomposes the tensor into component matrices and performs clustering analysis. Anomalies
are identified by calculating the distance between each
sample and its cluster centroid.
r DAGMM [31]: DAGMM combines an autoencoder with
a Gaussian Mixture Model to generate low-dimensional
representations of data points, and uses the reconstruction
error to identify anomalies.
r MPPCACD [32]: MPPCACD detects anomalies using a
method based on probabilistic dimensionality reduction
and clustering.
r THOC [35]: THOC uses dilated recurrent neural networks
to capture multi-scale temporal patterns. It then detects
anomalies by defining a single-class object through hierarchical clustering.
r LSTM [11]: The method employs an LSTM network for
anomaly detection, combined with a complementary nonparametric unsupervised thresholding strategy to determine anomaly criterion.
r GReLeN [16]: GReLeN uses VAE for feature extraction
and combines GNN with a random graph relation learning strategy to capture dependencies between variables,
enabling effective anomaly detection.
r Anomaly Transformer [25]: Anomaly Transformer exploits the inherent distinguishability between normal and
anomaly in the temporal dimension, termed as association

41

discrepancy. Then, this method combines the association
discrepancy with the reconstruction error as a detection
criterion, achieving effective anomaly detection.
r MEMTO [18]: MEMTO uses a memory-guided Transformer based on the reconstruction paradigm to learn
normal patterns. This approach restricts the encoder from
capturing anomaly features, making abnormal data harder
to reconstruct.
C. Experimental Setup
Experimental Setup: In our experiments, the model inputs
are sub-series extracted using non-overlapping sliding windows
with a fixed length T of 100 across all datasets. A time point
is identified as anomalous if its anomaly score within a subseries exceeds the threshold δ. Following the threshold selection criterion from Anomaly Transformer [25], we set δ based
on the top-r percent of anomaly scores in the validation set,
specifically r = 0.3% for SWaT and SMD, 0.5% for PSM, and
1% for the other datasets. Additionally, we use the adjustment
method widely adopted in anomaly detection [25], [35], [36],
[50] to evaluate the experimental results. Both the temporal
dependency encoder and variable correlation encoder consist
of three modules. We set the number of hidden channels dtemp
in the temporal dependency encoder to 512 and configure the
number of attention heads to 8. The hidden channels dvar in the
variable correlation encoder is set to 800, and the number of
heads h is set to 100. The output feature dimension de in the
linear layer of (2) is set to 64. The hyperparameter λ in (8) is
set to 3 to trade off the terms of reconstruction loss and variable
dependency discrepancy. The parameter K in TopK is set to half
the number of variables. The Adam [51] optimizer is used in the
experiments with an initial learning rate of 10−4 . The batch size
in the experiment is set to 128, and the early stopping strategy
is adopted. We implement VDDFormer with PyTorch [52] and
conduct all experiments using a single TESLA V100S 32 GB
GPU.
Evaluation Metrics: In this paper, we utilize 3 commonly used
evaluation metrics for anomaly detection: Precision (P), Recall
(R), and F1 score (F1). These metrics are used to evaluate the
performance of the VDDFormer. The formula for calculating
the F1 score is as follows:
P×R
(10)
F1 = 2 ×
P+R
D. Main Results
Following the experimental setup previously introduced, we
conduct comparative experiments between VDDFormer and 15
baseline models across five public datasets. The experimental
results are summarized in Table II. We reproduce the results of
GReLeN, Anomaly Transformer, and MEMTO, while adopting
the performance metrics reported in [25] for other baselines.
As shown in Table II, we first observe that deep learningbased anomaly detection methods exhibit significantly better
performance compared to classical approaches. This discrepancy arises because classical methods cannot explicitly model
the temporal dependencies and variable correlations inherent

42

IEEE TRANSACTIONS ON BIG DATA, VOL. 12, NO. 1, JANUARY/FEBRUARY 2026

TABLE II
COMPARISON WITH OTHER BASELINES

in MTS data. Consequently, classical methods do not capture complex temporal variations and dynamic dependencies
among variables, limiting their effectiveness in addressing the
intricate patterns of real-world MTS anomalies. Additionally,
deep learning-based approaches that explicitly model variable
dependencies consistently outperform those neglecting such
interactions. For instance, methods such as ITAD, DAGMM,
MPPCACD, LSTM, and LSTM-VAE, which disregard variable
dependencies, yield suboptimal performance in comparison.
These results demonstrate that capturing dependencies among
variables is critical for effective time series modeling and should
not be omitted in anomaly detection frameworks.
The results in Table II further demonstrate the advantage of Transformer-based models for MTS anomaly detection, such as Anomaly Transformer, MEMTO, and our
proposed VDDFormer. These methods validate the effectiveness of the Transformer architecture in dynamically modeling temporal patterns and variable dependencies. Notably,
VDDFormer achieves state-of-the-art performance on four
benchmark datasets (SMAP, MSL, SWaT, and PSM), while
maintaining comparable results on SMD.
To clarify the technical distinctions, we elaborate on the key
differences between VDDFormer and Anomaly Transformer. In
principle, Anomaly Transformer focuses on temporal feature
modeling. It employs an attention divergence termed association discrepancy to distinguish anomalies, where abnormal
patterns primarily attend to adjacent timestamps while normal
patterns exhibit holistic temporal dependencies. The association
discrepancy is implemented through a dual-branch AnomalyAttention mechanism. The prior-association branch computes
temporal priors using a learnable Gaussian kernel based on

relative time distances. The series-association branch embeds
multivariate observations at each timestamp into tokens and
learns series dependencies through self-attention. The association discrepancy is quantified by measuring the symmetrized
KL divergence between the attention weight distributions of both
branches, enabling intrinsic discrimination between normal and
abnormal patterns. However, Anomaly Transformer design does
not explicitly address the intricate variable dependencies inherent in MTS. Our VDDFormer employs a variable dependency
attention mechanism to capture the aforementioned variable
dependency discrepancy for anomaly detection. Inspired by the
Anomaly-Attention architecture, the variable dependency attention mechanism comprises two branches: the local dependency
branch captures variable dependencies at each timestamp via
an adaptive adjacency matrix method; the global dependency
branch embeds subseries of each variable as tokens to learn
long-term variable dependencies through self-attention. The
variable dependency discrepancy is quantified by computing the
statistical distance between global and local dependencies using
symmetrized KL divergence. MTS encompass both dynamic
temporal patterns and complex inter-variable relationships, rendering purely temporal modeling prone to misjudgment due to
interference. As illustrated in Fig. 1, Anomaly Transformer generates false alarms during normal periods, while VDDFormer
effectively mitigates this issue through its proposed variable
dependency discrepancy criterion.
E. Ablation Analysis
Model Architecture and Discriminant Criteria: To impartially evaluate the effectiveness and contributions of both

LIU et al.: VDDFORMER: A VARIABLE DEPENDENCY DISCREPANCY-BASED TRANSFORMER FOR MULTIVARIATE

TABLE III
ABLATION STUDY ON MODEL ARCHITECTURE AND ANOMALY CRITERION

VDDFormer’s components and its discrimination criteria, comprehensive ablation studies are designed. First, a baseline is
established by exclusively employing the temporal dependency
encoder with reconstruction error as the anomaly criterion.
This configuration evaluates anomaly detection capability in
the absence of variable correlation encoder. Then, the temporal
dependency encoder is removed while retaining only the variable
correlation encoder. Three distinct criteria are examined: the
reconstruction error, the variable dependency discrepancy, and
the composite anomaly criterion proposed in (9). This setting
investigates model performance without temporal dependency
modeling. Finally, the complete model is evaluated using three
distinct criteria: reconstruction error, variable dependency discrepancy, and the proposed composite anomaly criterion. This
systematic approach enables thorough validation of the contributions and effectiveness of both the components and the
discrimination criteria.
The ablation study results for the three configurations are
presented in Table III, yielding the following conclusions. First,
the proposed composite anomaly discriminant criterion (combining reconstruction error and variable dependency discrepancy) significantly outperforms the conventional reconstruction
error-based criterion. As evidenced by the variable correlation
encoder and the VDDFormer results, the composite criterion
improves the average F1 score by 17.34% (76.56%→93.90%)
and 17.84% (77.06%→94.90%), respectively, compared to using reconstruction error alone. These improvements demonstrate the critical role of jointly considering the reconstruction
error and the variable dependency discrepancy for effective
anomaly detection. Second, the experimental results demonstrate that the temporal dependency encoder achieves an average
F1 score of 76.12%. This reveals the limitations of the model in
anomaly detection when it focuses solely on temporal pattern
learning while neglecting variable dependency discrepancies.
Third, when solely utilizing variable dependency discrepancy
as the discrimination criterion, both the variable correlation
encoder and VDDFormer deliver superior performance (93.30%
and 93.74%, respectively), demonstrating the inherent discriminative capability of the variable dependency discrepancy to
distinguish normal from abnormal patterns. Finally, under the
composite anomaly criterion, VDDFormer achieves an average

43

F1 score improvement of 1% (93.90%→94.90%) compared to
the variable correlation encoder. This outcome substantiates the
effectiveness and necessity of the temporal dependency encoder
in capturing temporal dependencies within MTS.
Statistical Distance Methods: To investigate the impact of the
variable dependency discrepancy computed by diverse statistical distance methods on anomaly detection performance, we
conducted comparative experiments using the following widely
adopted statistical approaches:
r L2 Distance (L2).
r Cross-Entropy (CE).
r Jensen-Shannon Divergence (JSD).
r Symmetrized Kullback-Leibler (KL) Divergence (Ours).
The experimental results in Table IV demonstrate that the
symmetrized KL divergence method achieves the best anomaly
detection performance across all five datasets with an average F1
score of 94.90%. While the L2 distance method (90.19% average
F1 score), CE method (92.34%), and JSD method (90.79%)
exhibit comparable performance across the five datasets, they
still show a noticeable gap compared to the symmetrized KL
divergence method. Based on these experimental results, the
symmetrized KL divergence is adopted to quantify variable
dependency discrepancies.
Multi-Module Quantization: During anomaly detection, we
calculate the average of variable dependency discrepancies
across all modules and integrate it with the reconstruction error
to derive the final anomaly score. The multi-module quantification is validated through comparison with all single-module
counterparts, where the anomaly criterion is defined by the
integration of each module’s dependency discrepancy and reconstruction error. As demonstrated in Table V, the multimodule approach outperforms all single-module counterparts.
The results not only confirm the efficacy of VDDFormer’s
multi-module stacking design, but also reveal that multi-module
quantification captures more informative variable dependency
discrepancies.
F. Analysis of Hyperparameters and Computational Efficiency
Analysis of Hyperparameters: The hyperparameters of the
model are experimentally analyzed. First, the effect of the
number of modules on detection performance is studied by
varying the module count L from 1 to 4. The derived variable dependency discrepancies are averaged and integrated with
the reconstruction error to calculate the anomaly scores for
evaluation. As illustrated in Fig. 4(a), three modules achieve
optimal performance across all datasets, thereby being adopted
as the final configuration. Next, the impact of hidden channels dvar is investigated by testing values of 400, 800, 1600,
and 3200. The results in Fig. 4(b) show that a channel number of 800 yields the best overall performance, serving as
the default setting. The output feature dimension de in the
linear layer of (2) is further analyzed, and Fig. 4(c) shows
that it achieves optimal performance when set to 64. These
parametric studies reveal limited sensitivity to parameter variations, demonstrating the robustness of VDDFormer in practical
applications.

44

IEEE TRANSACTIONS ON BIG DATA, VOL. 12, NO. 1, JANUARY/FEBRUARY 2026

TABLE IV
MODEL PERFORMANCE UNDER DIFFERENT DEFINITIONS OF VARIABLE DEPENDENCY DISCREPANCY

TABLE V
ANOMALY DETECTION PERFORMANCE UNDER DIFFERENT SELECTIONS OF MODULES FOR VARIABLE DEPENDENCY DISCREPANCY

Fig. 4. Sensitivity analysis of model hyperparameters. (a) Impact of the number of modules L in VDDFormer on detection performance. (b) Impact of the hidden
channels dvar on detection performance. (c) Impact of the output feature dimension de of the linear layer on detection performance.

Fig. 5. Experimental results of the loss weight λ. (a) Performance of different
loss weight values on the SMD dataset. (b) Performance of different loss weight
values on the PSM dataset.

Fig. 6. Experimental results of the K in the TopK strategy. (a) Performance
of different K values in the TopK strategy on the SMD dataset. (b) Performance
of different K values in the TopK strategy on the PSM dataset. The horizontal
axis labels (e.g., 0.1N, 0.3N ) indicate the fraction of the total variables N .

To investigate the impact of loss weight λ and TopK parameter
K on detection results, experiments are conducted on the SMD
and PSM datasets. The experimental results are presented in
Figs. 5 and 6. Optimal detection performance occurs when λ is

equal to three, as shown in Fig. 5(a) and (b). Deviating from
this value reduces performance, confirming that balanced integration of reconstruction loss and variable dependency discrepancy strengthens normal-abnormal separability for improved

LIU et al.: VDDFORMER: A VARIABLE DEPENDENCY DISCREPANCY-BASED TRANSFORMER FOR MULTIVARIATE

detection. Fig. 6(a) and (b) demonstrate that setting K at half the
total number of variables achieves superior results. Performance
declines as K decreases, indicating that excessive information
loss in local dependency weakens the distinction between normal and abnormal patterns, thereby reducing performance.
Computational Efficiency. The time complexity of
VDDFormer is analyzed by examining its three main
components. The temporal dependency encoder exhibits a time
complexity of O(T d2temp ), while the variable correlation encoder
has a time complexity of O(N d2var + T 2 N de ). Meanwhile,
the reconstruction decoder exhibits a time complexity of
O(T dtemp N + T dvar N ). Under the experimental parameter settings, the inequality (T dtemp N + T dvar N )  T d2temp < N d2var
holds. Furthermore, given that T 2 N de equals N d2var (with
T = 100, de = 64, dvar = 800), the overall time complexity is
O(N d2var ). For comparison, the time complexity of Anomaly
Transformer is O(T d2temp ). Under the given parameter
configuration, VDDFormer achieves the same asymptotic order
of time complexity as Anomaly Transformer. Additionally,
inference time comparisons are performed on the SWaT dataset.
For the same 100 samples, VDDFormer achieves an average
inference time of 7.52 ms per sample, compared to 4.26 ms per
sample for Anomaly Transformer. Despite being marginally
slower, VDDFormer maintains computational practicality for
real-time anomaly detection scenarios.
VI. CONCLUSION
This paper proposes a new criterion for MTS anomaly detection, variable dependency discrepancy, which can identify
group anomaly patterns that are beyond the detection ability of
existing methods. Based on the proposed variable dependency
discrepancy, we have developed an unsupervised MTS anomaly
detection method, dubbed VDDFormer. VDDFormer consists of
a variable correlation encoder with variable dependency attention mechanism, a temporal dependency encoder to model temporal dependencies, and a reconstruction decoder that generates
reconstruction output. The integration of reconstruction error
and variable dependency discrepancy as a joint discriminative
criterion effectively improves anomaly detection performance.
The limitation of VDDFormer lies in its dual-encoder design,
which increases the complexity of the model. Specifically, the
temporal dependency encoder models temporal dependencies,
while the variable correlation encoder captures both global and
local dependencies to quantify variable dependency discrepancies. To address this limitation, future work will focus on
developing a unified encoder capable of simultaneously modeling temporal dependencies, capturing both global and local
dependencies to quantify variable dependency discrepancies.
This unified encoder will simplify the model architecture and
accelerate anomaly detection.
REFERENCES
[1] W. Haider, J. Hu, Y. Xie, X. Yu, and Q. Wu, “Detecting anomalous
behavior in cloud servers by nested-arc hidden SEMI-Markov model with
state summarization,” IEEE Trans. Big Data, vol. 5, no. 3, pp. 305–316,
Sep. 2019.

45

[2] N. Moustafa, J. Slay, and G. Creech, “Novel geometric area analysis
technique for anomaly detection using trapezoidal area estimation on
large-scale networks,” IEEE Trans. Big Data, vol. 5, no. 4, pp. 481–494,
Dec. 2019.
[3] C. Yang, Z. Du, X. Meng, X. Zhang, X. Hao, and D. A. Bader, “Anomaly
detection in catalog streams,” IEEE Trans. Big Data, vol. 9, no. 1,
pp. 294–311, Feb. 2023.
[4] R. Paffenroth, P. Du Toit, R. Nong, L. Scharf, A. P. Jayasumana, and V.
Bandara, “Space-time signal processing for distributed pattern detection in
sensor networks,” IEEE J. Sel. Top. Signal Process., vol. 7, no. 1, pp. 38–49,
Feb. 2013.
[5] H. Hoffmann, “Kernel PCA for novelty detection,” Pattern Recognit.,
vol. 40, no. 3, pp. 863–874, 2007.
[6] B. Schölkopf, J. C. Platt, J. Shawe-Taylor, A. J. Smola, and R. C.
Williamson, “Estimating the support of a high-dimensional distribution,”
Neural Comput., vol. 13, no. 7, pp. 1443–1471, 2001.
[7] D. M. Tax and R. P. Duin, “Support vector data description,” Mach. Learn.,
vol. 54, no. 1, pp. 45–66, 2004.
[8] C. Huang, G. Min, Y. Wu, Y. Ying, K. Pei, and Z. Xiang, “Time series
anomaly detection for trustworthy services in cloud computing systems,”
IEEE Trans. Big Data, vol. 8, no. 1, pp. 60–72, Feb. 2022.
[9] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” in Proc. ACM SIGMOD Int. Conf. Manage.
Data, 2000, pp. 93–104.
[10] J. Zhao, F. Deng, J. Zhu, and J. Chen, “Searching density-increasing path
to local density peaks for unsupervised anomaly detection,” IEEE Trans.
Big Data, vol. 9, no. 4, pp. 1198–1209, Aug. 2023.
[11] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom,
“Detecting spacecraft anomalies using LSTMs and nonparametric dynamic thresholding,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov.
Data Mining, 2018, pp. 387–395.
[12] C. Zhang et al., “A deep neural network for unsupervised anomaly detection and diagnosis in multivariate time series data,” in Proc. AAAI Conf.
Artif. Intell., 2019, pp. 1409–1416.
[13] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly detector
for robot-assisted feeding using an LSTM-based variational autoencoder,”
IEEE Robot. Autom. Lett., vol. 3, no. 3, pp. 1544–1551, Jul. 2018.
[14] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., 2022,
pp. 4027–4035.
[15] H. Zhao et al., “Multivariate time-series anomaly detection via graph attention network,” in Proc. IEEE Int. Conf. Data Mining, 2020, pp. 841–850.
[16] W. Zhang, C. Zhang, and F. Tsung, “GRELEN: Multivariate time series
anomaly detection from the perspective of graph relational learning,” in
Proc. Int. Joint Conf. Artif. Intell., 2022, pp. 2390–2397.
[17] Z. Li et al., “Multivariate time series anomaly detection and interpretation
using hierarchical inter-metric and temporal embedding,” in Proc. ACM
SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2021, pp. 3220–3230.
[18] S. Junho, K. Keonwoo, O. Jeonglyul, and C. Sungzoon, “MEMTO:
Memory-guided transformer for multivariate time series anomaly detection,” in Proc. Adv. Neural Inf. Process. Syst., 2024, pp. 57947–57963.
[19] H. Wu, J. Xu, J. Wang, and M. Long, “AutoFormer: Decomposition
transformers with auto-correlation for long-term series forecasting,” in
Proc. Adv. Neural Inf. Process. Syst., 2021, pp. 22 419–22 430.
[20] H. Zhou et al., “Informer: Beyond efficient transformer for long sequence
time-series forecasting,” in Proc. AAAI Conf. Artif. Intell., 2021, pp. 11
106–11 115.
[21] T. Zhou, Z. Ma, Q. Wen, X. Wang, L. Sun, and R. Jin, “FedFormer:
Frequency enhanced decomposed transformer for long-term series forecasting,” in Proc. Int. Conf. Mach. Learn., 2022, pp. 27 268–27 286.
[22] S. Li et al., “Enhancing the locality and breaking the memory bottleneck of
transformer on time series forecasting,” in Proc. Adv. Neural Inf. Process.
Syst., 2019, pp. 5244–5254.
[23] S. Liu et al., “Pyraformer: Low-complexity pyramidal attention for longrange time series modeling and forecasting,” in Proc. Int. Conf. Learn.
Representations, 2022.
[24] D. Du, B. Su, and Z. Wei, “Preformer: Predictive transformer with multiscale segment-wise correlations for long-term time series forecasting,” in
Proc. IEEE Int. Conf. Acoust. Speech Signal Process., 2023, pp. 1–5.
[25] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time series
anomaly detection with association discrepancy,” in Proc. Int. Conf. Learn.
Representations, 2022.
[26] Z. Wu, S. Pan, G. Long, J. Jiang, X. Chang, and C. Zhang, “Connecting
the dots: Multivariate time series forecasting with graph neural networks,”
in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 753–763.

46

IEEE TRANSACTIONS ON BIG DATA, VOL. 12, NO. 1, JANUARY/FEBRUARY 2026

[27] D. Li, D. Chen, B. Jin, L. Shi, J. Goh, and S.-K. Ng, “MAD-GAN: Multivariate anomaly detection for time series data with generative adversarial
networks,” in Proc. Int. Conf. Artif. Neural Netw., 2019, pp. 703–716.
[28] B. Zhou, S. Liu, B. Hooi, X. Cheng, and J. Ye, “BeatGAN: Anomalous
rhythm detection using adversarially generated time series,” in Proc. Int.
Joint Conf. Artif. Intell., 2019, pp. 4433–4439.
[29] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,”
in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 3395–3404.
[30] L. Ruff et al., “Deep one-class classification,” in Proc. Int. Conf. Mach.
Learn., 2018, pp. 4393–4402.
[31] B. Zong et al., “Deep autoencoding gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Representations,
2018.
[32] T. Yairi, N. Takeishi, T. Oda, Y. Nakajima, N. Nishimura, and N. Takata,
“A data-driven health monitoring method for satellite housekeeping data
based on probabilistic clustering and dimensionality reduction,” IEEE
Trans. Aerosp. Electron. Syst., vol. 53, no. 3, pp. 1384–1401, Jun. 2017.
[33] R. Frehner, K. Wu, A. Sim, J. Kim, and K. Stockinger, “Detecting anomalies in time series using kernel density approaches,” IEEE Access, vol. 12,
pp. 33420–33439, 2024.
[34] Y. Shin et al., “ITAD: Integrative tensor-based anomaly detection system
for reducing false positives of satellite systems,” in Proc. Int. Conf. Inf.
Knowl. Manage., 2020, pp. 2733–2740.
[35] L. Shen, Z. Li, and J. Kwok, “Timeseries anomaly detection using temporal
hierarchical one-class network,” in Proc. Adv. Neural Inf. Process. Syst.,
2020, pp. 13 016–13 026.
[36] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining,
2019, pp. 2828–2837.
[37] K. Ding, Q. Zhou, H. Tong, and H. Liu, “Few-shot network anomaly
detection via cross-network meta-learning,” in Proc. Int. World Wide Web
Conf., 2021, pp. 2448–2456.
[38] M. Mesgaran and A. B. Hamza, “Graph fairing convolutional networks for
anomaly detection,” Pattern Recognit., vol. 145, 2024, Art. no. 109960.
[39] Y. Liu, Z. Li, S. Pan, C. Gong, C. Zhou, and G. Karypis, “Anomaly
detection on attributed networks via contrastive self-supervised learning,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2378–2392,
Jun. 2022.
[40] Z. Zhang et al., “PromptST: Prompt-enhanced spatio-temporal multiattribute prediction,” in Proc. ACM Int. Conf. Inf. Knowl. Manage., 2023,
pp. 3195–3205.
[41] Z. Zhang, X. Zhao, H. Miao, C. Zhang, H. Zhao, and J. Zhang, “AutoSTL:
Automated spatio-temporal multi-task learning,” in Proc. AAAI Conf. Artif.
Intell., 2023, pp. 4902–4910.
[42] H. Yan, X. Ma, and Z. Pu, “Learning dynamic and hierarchical traffic
spatiotemporal features with transformer,” IEEE Trans. Intell. Transp.
Syst., vol. 23, no. 11, pp. 22 386–22 399, Nov. 2022.
[43] G. Zerveas, S. Jayaraman, D. Patel, A. Bhamidipaty, and C. Eickhoff, “A
transformer-based framework for multivariate time series representation
learning,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining,
2021, pp. 2114–2124.
[44] Y. Zhang and J. Yan, “Crossformer: Transformer utilizing cross-dimension
dependency for multivariate time series forecasting,” in Proc. Int. Conf.
Learn. Representations, 2023.
[45] Y. Nie, N. H. Nguyen, P. Sinthong, and J. Kalagnanam, “A time series is
worth 64 words: Long-term forecasting with transformers,” in Proc. Int.
Conf. Learn. Representations, 2023.
[46] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural Inf.
Process. Syst., 2017, pp. 6000–6010.
[47] A. P. Mathur and N. O. Tippenhauer, “SWaT: A water treatment testbed for
research and training on ICS security,” in Proc. Int. Workshop Cyber-phys.
Syst. Smart Water Netw., 2016, pp. 31–36.
[48] A. Abdulaal, Z. Liu, and T. Lancewicki, “Practical approach to asynchronous multivariate time series anomaly detection and localization,”
in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2021,
pp. 2485–2494.

[49] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. IEEE
Int. Conf. Data Mining, 2008, pp. 413–422.
[50] H. Xu et al., “Unsupervised anomaly detection via variational auto-encoder
for seasonal KPIs in web applications,” in Proc. World Wide Web Conf.,
2018, pp. 187–196.
[51] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
in Proc. Int. Conf. Learn. Representations, 2015.
[52] A. Paszke et al., “PyTorch: An imperative style, high-performance deep
learning library,” in Proc. Adv. Neural Inf. Process. Syst., 2019, pp. 8026–
8037.

Bo Liu received the MS degree from the School of
Computer Science and Technology, Harbin Institute
of Technology. He is currently working toward the
PhD degree with the School of Computer Science
and Technology, Harbin Institute of Technology. His
current research interest is time series analysis.

Lingling Tao received the PhD degree from Northeastern University in 2022. She was a visiting student
with the School of Computer Science and Engineering of Nanyang Technological University from 2019
to 2020. She currently is a research fellow with the
School of Computer Science and Technology, Harbin
Institute of Technology, Shenzhen. Her research interests are time series data mining and optimal decision.

Xiaodan Chen received the MS degree from the
School of Computer Science and Technology, Harbin
Institute of Technology in 2020. She is currently
working toward the PhD degree with the School of
Computer Science and Technology, Harbin Institute
of Technology. Her current research interest is time
series analysis.

Zhijun Li received the MS degree in computer science and technology and the PhD degree in computer
science and technology from the Harbin Institute of
Technology, in 2001 and 2006, respectively. He is
currently a professor with the School of Computer
Science and Technology, Harbin Institute of Technology. His research focuses on wireless networks,
Internet of Things, and ubiquitous computing. He was
a recipient of the Mobicom17 Best Paper Award.
PAPER_TEXT
