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
# [448] Fuzzy State-Driven Cross-Time Spatial Dependence Learning for Multivariate Time-Series Anomaly Detection
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
编号：448
题名：Fuzzy State-Driven Cross-Time Spatial Dependence Learning for Multivariate Time-Series Anomaly Detection
年份：2024
DOI：10.1109/tnnls.2024.3371109
来源：IEEE Transactions on Neural Networks and Learning Systems
PDF：paper/10.1109_TNNLS.2024.3371109.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：中相关，分数 7
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\448.txt
- 原始字符数：64370
- 本次发送字符数：64370
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
4532

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 3, MARCH 2025

Fuzzy State-Driven Cross-Time Spatial Dependence
Learning for Multivariate Time-Series
Anomaly Detection
Kun Zhu , Pengyu Song , and Chunhui Zhao , Senior Member, IEEE
Abstract— Cross-time spatial dependence (i.e., the interaction
between different variables at different time points) is indispensable for detecting anomalies in multivariate time series, as certain
anomalies may have time delays in their propagation from one
variable to another. However, accurately capturing cross-time
spatial dependence remains a challenge. Specifically, real-world
time series usually exhibits complex and incomprehensible evolutions that may be compounded by multiple temporal states
(i.e., temporal patterns, such as rising, fluctuating, and peak).
These temporal states mix and overlap with each other and
exhibit dynamic and heterogeneous evolution laws in different
time series, making the cross-time spatial dependence extremely
intricate and mutable. Therefore, a cross-time spatial graph
network with fuzzy embedding is proposed to disentangle latent
and mixing temporal states and exploit it to meticulously learn
cross-time spatial dependence. First, considering that temporal
states are diversiform and their mixing modes are unknown,
we introduce a fuzzy state set to uniformly characterize potential
temporal states and adaptively generate corresponding membership degrees to depict how these states mix. Further, we propose
a cross-time spatial graph, quantifying similarities among fuzzy
states and sensing their dynamic evolutions, to flexibly learn
mutable cross-time spatial dependence. Finally, we design state
diversity and temporal proximity constraints to ensure the
differences among fuzzy states and the evolution continuity of
fuzzy states. Experiments on real-world datasets show that the
proposed model outperforms the state-of-the-art models.
Index Terms— Anomaly detection, cross-time spatial dependence, fuzzy state, multivariate time series, temporal state.

N
T
ϑ
MFqn
mdnt,q
µqn and σqn
W, b
LV
LC
LR
LP

N OMENCLATURE
Number of variables.
Number of time points.
Convolution kernels.
Membership function.
Membership degree.
Center and width of membership function.
Weight parameter and bias.
State diversity constraint.
Temporal proximity constraint.
Reconstruction constraint.
Prediction constraint.

Manuscript received 15 July 2023; revised 27 November 2023;
accepted 25 February 2024. Date of publication 8 March 2024; date of current
version 1 March 2025. This work was supported in part by the National
Natural Science Foundation of China under Grant 62125306, in part by the
Zhejiang Key Research and Development Project under Grant 2024C01163,
and in part by the Guangdong Basic and Applied Basic Research Foundation
under Grant 2022A1515240003. (Corresponding author: Chunhui Zhao.)
The authors are with the College of Control Science and Engineering,
Zhejiang University, Hangzhou 310027, China (e-mail: chhzhao@zju.edu.cn).
Digital Object Identifier 10.1109/TNNLS.2024.3371109

C1 , C2 , and C3
λ1 , λ2 , λ3
ω1 , ω2
φscore
η
xt
n
x1:T
X 1:T
X̃ 1:T
x̂ T
ŷ t
fmvnt
FEX1:T
CTSGt:t+1
At:t+1

Desired dimensions of output channel.
Tradeoff coefficients.
Tradeoff coefficients.
Anomaly score.
Threshold to estimate anomalies.
Values of N variables at time point t.
Values of T time points of variable n.
Input sample sequence.
Reconstructed values for input sample
sequence.
Predicted values of time series at time
point T.
Anomaly label.
Membership vector.
Fuzzy embedding data for input sample
sequence.
Cross-time spatial graph.
Normalized adjacency matrix.
I. I NTRODUCTION

M

ULTIVARIATE time-series anomaly detection has been
extensively developed and researched across diverse
domains, aiming at finding abnormal conditions to ensure
system security and reduce financial loss [1]. Since anomaly
data are rare and difficult to gather, a popular and promising
paradigm in multivariate time-series anomaly detection is to
leverage unsupervised methods to learn specific patterns of
time series to recognize underlying anomalies [2]. Nowadays,
various unsupervised methods have been proposed and realized fruitful progress, such as Gaussian mixture model [3] and
isolation forest (IF) [4].
However, the above methods remain limited ability because
they do not consider crucial spatiotemporal dependencies in
multivariate time series [5], [6]. Unlike other data (e.g., image
and text), spatiotemporal dependencies are the distinguishing
characteristic of multivariate time series [7]. As shown in
Fig. 1(a), spatiotemporal dependencies are extremely complicated because they contain three parts, dubbed temporal
dependence (cross-time interactions within the same variable),
spatial dependence (interactions between different variables at
the same time point), and cross-time spatial dependence (interactions between different variables at different time points).
Vast studies have shown that accurately capturing spatiotemporal dependencies is vital to learning specific patterns of time
series for detecting anomalies [8], [9].

2162-237X © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

ZHU et al.: FUZZY STATE-DRIVEN CROSS-TIME SPATIAL DEPENDENCE LEARNING

Fig. 1. Example of complex spatiotemporal dependencies and latent temporal
states of time series. (a) Three different dependencies in spatiotemporal
dependencies. (b) Multiple temporal states mix and overlap with each other,
and present dynamic and heterogeneous evolution laws.

To this end, various deep learning-based studies have been
proposed to mine spatiotemporal dependencies and gained
remarkable momentum [10], [11]. For instance, transformer
model [1], [12] and long short-term memory (LSTM) network [13] focus on capturing temporal dependence across the
time dimension, while graph neural network (GNN) [14], [15]
aims at explicitly modeling spatial dependence across the variable dimension. Unfortunately, these studies may suffer from
false negative problems as the captured temporal dependence
and spatial dependence are ineffective for detecting certain
latent time-delay anomalies. In real-world industrial processes,
the time-delay phenomenon in the propagation of anomalies
is common because the effect of one entity (e.g., device or
machine) may take a certain time to spread to another. One
decent scheme for detecting time-delay anomalies is to exploit
the cross-time spatial dependence because it can effectively
reflect the intervariable influences at different time points, thus
helping to model the propagation mechanism of time-delay
anomalies.
However, modeling cross-time spatial dependence is still
a challenging task as its intricateness and mutability. These
characteristics may be induced by multiple temporal states
hidden in time-series evolutions. Specifically, as shown in
Fig. 1(b), time series of variable 1 and variable 2 present
complex and incomprehensible evolutions, where multiple
temporal states (or referred to temporal patterns) mix and
overlap with each other, e.g., state 1 (rising), state 2 (falling),
state 3 (fluctuating), and state 4 (peak) [16], [17]. It can be
seen that latent temporal states show the specific mixing mode
in each evolution phase of time series, in which different
temporal states have different influence degrees on time-series
evolutions. For example, assuming that variable 1 represents
the altitude of an airplane, state 1 (rising) may exert larger
influences during the take-off phase (roughly located at t2 ).

4533

In comparison, state 3 (fluctuating) influences more when
encountering unstable airflow (roughly located at t1 ). Moreover, it can also be found that temporal states exhibit dynamic
and heterogeneous evolution laws in different time series (e.g.,
from mixing mode 1 to mixing mode 2 in variable 1 and
from mixing mode 3 to mixing mode 4 in variable 2), thus
making cross-time spatial dependence complex and mutable
and further increasing its modeling difficulty.
In complex real scenarios, temporal states are usually
diversiform and their mixing modes are often unknown (the
influences from temporal states on time-series evolutions
are difficult to quantify by precise and hard binary values).
In light of this, we extend the analysis of time series from
a 1-D space to a high-dimensional fuzzy space, aiming to
construct a fuzzy state set (containing multiple fuzzy states)
to uniformly characterize diversiform temporal states and
generate soft membership degrees to portray their mixing
modes. Through this manner, we can break the bottleneck of
limited representation ability of 1-D time series and disentangle mixing temporal states, which helps to sense the mutability
of cross-time spatial dependence and facilitate its fine-grained
modeling, thus boosting the ability to discover time-delay
anomalies.
Technically, we propose a novel cross-time spatial graph
network with fuzzy embedding (FE-CTSNet), which consists
of a fuzzy embedding method called time series to membership
vector (TS2MVec), and a cross-time spatial graph (CTSG).
TS2MVec constructs multiple fuzzy states and each of them
represents a type of temporal state. Then, each time-series
data point is transformed into a membership vector containing
a series of membership degrees, where each membership
degree indicates the degree to which the corresponding fuzzy
state influences time-series evolutions. Based on the generated membership degrees, CTSG can quantify the similarity
between fuzzy states of any two time-series data points,
thereby flexibly learning cross-time spatial dependence. Moreover, membership degrees can adaptively change along with
dynamic evolutions of time series, thereby enabling CTSG to
sense the mutability of cross-time spatial dependence. Finally,
to strengthen the ability of fuzzy states to characterize potential
temporal states, we design state diversity and temporal proximity constraints, which not only make different fuzzy states
have differences, but also ensure the evolution continuity of
fuzzy states.
The main contributions of this study are threefold.
1) We propose a TS2MVec to construct a fine-grained
fuzzy state set to uniformly characterize latent temporal
states and adaptively generate corresponding membership degrees to depict their mixing modes. To the best
of authors’ knowledge, it is the first time to realize the
disentanglement for mixing temporal states from a fuzzy
embedding perspective.
2) We propose a CTSG to meticulously learn the cross-time
spatial dependence. Different from the existing graph
structures, it not only realizes flexible representations
for cross-time spatial dependence, but also senses its
mutability by capturing dynamic evolutions of fuzzy
states.

4534

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 3, MARCH 2025

TABLE I
D IFFERENCES B ETWEEN FE-CTSN ET AND OTHER M ETHODS

spatial dependence and used it to discover anomalies, such as
GNN-based models [26] and autoencoder-based models [27],
[28]. Further, some other studies [29], [30], [31], [32] simultaneously considered the above two dependencies to promote
anomaly detection results.
However, it can be seen from Table I that the existing unsupervised studies neglect the cross-time spatial dependence,
making it hard to discover certain latent time-delay anomalies.
In comparison, FE-CTSNet can model complete spatiotemporal dependencies (especially, cross-time spatial dependence),
thereby realizing satisfactory anomaly detection results.
B. Membership Functions in Fuzzy Logic

3) We design state diversity and temporal proximity constraints, which can guarantee the differences among
fuzzy states and the evolution continuity of fuzzy states,
thereby further improving its ability to characterize
temporal states.
II. R ELATED W ORK
A. Multivariate Time-Series Anomaly Detection
Unsupervised paradigms have been widely studied in the
time-series anomaly detection field. Some popular methods
focus on capturing complex spatiotemporal dependencies to
learn specific patterns of time series and then detect latent
anomalies. As shown in Table I, machine learning methods
contain principal component analysis (PCA) [18], slow feature
analysis (SFA) [19], [20], and canonical variate analysis (CVA)
[21]. They aim to obtain low-dimensional latent variables from
multivariate time series to represent its important information
and then design customized indicators for latent variable
spaces to detect anomalies. Among them, PCA considers spatial dependence while SFA and CVA can exploit both spatial
dependence and temporal dependence. Although they have
gained meaningful anomaly detection results, their extracted
features are linear and thus not sufficient to perform well in
complicated nonlinear scenarios.
At present, in unsupervised anomaly detection studies,
deep learning methods have emerged frequently due to their
superior ability to generate multilevel and nonlinear feature
representations [22], [23]. On the one hand, some models
focused on mining temporal dependence: such as LSTM-based
models [24], autoencoder-based models [25], and transformerbased models [1], [12]. The first two types of models
were only good at modeling short-range dependencies, while
transformer-based models can use self-attention to capture reliable long-range dependencies, but with higher computational
complexity. On the other hand, some models mainly modeled

Fuzzy logic and probability theory are two different reasoning methods [33]. Specifically, fuzzy logic can generate
the membership degree to represent the degree to which an
object has an abstract attribute (i.e., state) (generally without
randomness) [34], [35]. Probability theory can generate the
probability value to represent the likelihood of an object
happening (generally with randomness) [36]. For each latent
temporal state, membership degree portrays the degree of its
influence on time-series evolutions, while probability value
portrays the likelihood that it can influence time-series evolutions. Intuitively, fuzzy logic is more appropriate for this
study since the influence of temporal states on time series has
actually happened and directly induced its evolutions.
Recently, a promising method is to combine membership
functions in the fuzzy logic with neural networks. For example,
Deng et al. [37] used the Gaussian function as the membership
function to generate fuzzy representations, which reduced the
uncertainties in original data and showed its superiority in
classification tasks. Ebadzadeh and Salimi-Badr [38] introduced a shapeable membership function with an adjustable
shape and proposed interpretable correlated-contours fuzzy
rules to realize better function approximation. All these studies
use membership functions to generate fuzzy representations
and automatically learn optimal parameters of membership
functions, which is conducive to enhancing the representation
of complex data.
III. M ETHODOLOGY
A. Problem Statement
In this study, we focus on introducing a fuzzy state set
to characterize diversiform and mixing temporal states and
exploit it to learn mutable cross-time spatial dependence for
identifying potential time-delay anomalies. To formalize this
problem, some key concepts are defined as follows.
Definition 1 (Task Description): A multivariate time series
can be denoted as X = {x1 , x2 , . . . , xτ } ∈ R N ×τ , where N is
the number of variables and τ is the sequence length of X .
xt = {xt1 , xt2 , . . . , xtN } ∈ R N is an N -dimensional sample (i.e.,
N variable values at time point t). Our goal is to predict the
anomaly label of xt , i.e., 1 (abnormal) or 0 (normal).
Definition 2 (Temporal States and Fuzzy States): We refer
to mixing and overlapping temporal patterns involved in
time-series evolutions as temporal states. Since temporal
states are diversiform and their mixing modes are unknown,

ZHU et al.: FUZZY STATE-DRIVEN CROSS-TIME SPATIAL DEPENDENCE LEARNING

4535

Fig. 2. Overall framework of FE-CTSNet. Module A is dedicated to generating fuzzy embedding data and ensuring its diversity, modules C and D are
dedicated to using fuzzy embedding data from module A to achieve anomaly detection, and module B, as an auxiliary module, is dedicated to endowing the
fuzzy embedding data from module A with temporal dependence and further facilitating the performance of modules C and D. These modules work together
to gain the FE-CTSNet with superior performance.

we depict them by a fuzzy state set, in which each fuzzy state
characterizes a type of temporal state. Then, we map each
time-series data point into a membership vector (consisting of
multiple membership degrees), where each membership degree
indicates the degree to which the corresponding fuzzy state
influences time-series evolutions.
The main notations in this study are summarized in
Nomenclature.
B. Overall Framework
As shown in Fig. 2, FE-CTSNet contains four modules
and exploits a joint evolution objective to co-optimize all
the modules and guide end-to-end training. The process and
contribution of each module are illustrated as follows.
1) Fuzzy Embedding Module (Module A): We propose a
new TS2MVec to build a fuzzy state set and design a new state
diversity constraint to ensure differences among different fuzzy
states, thereby enabling fuzzy states to characterize potential
temporal states from as many perspectives as possible. Then,
we introduce multiple membership functions to transform each
time-series data point into a membership vector (containing
a series of membership degrees). Finally, we combine all
membership vectors along the time axis to generate fuzzy
embedding data to effectively describe the evolution law of
time series and is used as input for modules B–D.
2) Global–Local Correlation-Based Refining Module (Module B): Considering that temporal states natively have
temporal dependence, we design a new temporal proximity constraint to endow all membership vectors in fuzzy
embedding data with temporal dependence, thus ensuring
the evolution continuity of fuzzy states and improving its
characterization ability for temporal states.

3) Fuzzy
Inference-Based
Reconstructing
Module
(Module C): We design a customized fuzzy inference-based
defuzzification method (containing fuzzy rule, conclusion,
and defuzzification layers) for fuzzy embedding data to
generate reconstructed time series as close as possible to the
original time series.
4) Spatiotemporal Dependencies Modeling Module (Module
D): We propose a new CTSG to exploit fuzzy embedding
data to learn complete spatiotemporal dependencies (i.e., spatial dependence, temporal dependence, and cross-time spatial
dependence). Moreover, we design a cross-time spatial graphbased network (CTSNet) adapted to CTSG, exploiting deep
hierarchical architectures to mine long-term spatiotemporal
dependencies to obtain accurate forecasting results.
C. Fuzzy Embedding Module
In this module, we map all time series from a
low-dimensional space (1-D) into a common high-dimensional
fuzzy space, where each dimension corresponds to a fuzzy
state. Specifically, we build a fuzzy state set (containing
some membership functions) to transform each time-series
data point into a series of membership degrees, and each of
them indicates the degree to which the corresponding fuzzy
state influences time-series evolutions. Then, all membership
degrees of each time-series data point are concatenated to
generate a membership vector representing its mixing mode
of fuzzy states. In addition, considering that different variables
usually exhibit heterogeneous evolution laws, we assign fuzzy
state sets with different initial parameter values for different
variables, which can make TS2MVec to capture the particular
evolution law of each variable.

4536

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 3, MARCH 2025

Fig. 3. Schematic of integrating the contextual information. Each yellow
dotted box denotes a convolution kernel.

This module contains two stages: integration of contextual
information and TS2MVec.
1) Integration of Contextual Information: Assume that
X 1:T ∈ R N ×T denotes the input sample sequence, where N and
T are the number of variables and time points, respectively.
As shown in Fig. 3, to make the fuzzy embedding method not
be an isolated single-point embedding method, the contextual
information along the time dimension is first integrated into
each variable value
′
X 1:T
= X 1:T ∗ ϑct

(1)

′
where X 1:T
∈ R N ×T and ϑct ∈ R1×δ×1 denote the output data

and the contextual convolution kernel, respectively. δ denotes
the time span of contextual information.
In particular, the padding operation is performed during the
convolution process to ensure the size consistency between
′
′
X 1:T and X 1:T
. Then, X 1:T
is segmented into N feature slices
N
1
2
x1:T , x1:T , . . . , x1:T ∈ RT along the variable dimension, and
n
then, TS2MVec is carried out on each feature slice x1:T
(1 ≤
n ≤ N ), respectively.
2) TS2MVec: Following the classic research on fuzzy neural
network (FNN) [37], [39], we adopt the Gaussian function
as the membership function because it has the advantages of
differentiability and continuity. We construct different fuzzy
state sets for different variables and each fuzzy state set
contains Q different membership functions (denoting Q fuzzy
states). As shown in Fig. 4, taking the nth (1 ≤ n ≤ N )
variable as an example, its variable values at T time points
n
x1:T
are all input into the nth fuzzy state set that contains Q
membership functions, as shown in the following equation:

mdnt,q = MFqn xtn
(xtn −µqn )2
n 2
= e (σq ) ,

Fig. 4. Schematic of TS2MVec for nth variable. Q membership functions
can output Q membership degrees for each time-series data point to form a
membership vector to characterize Q fuzzy states.

where mdnt ∈ R Q denotes the joint of membership degrees.
fmvnt ∈ R Q denotes the final membership vector that can
characterize the mixing mode of Q fuzzy states for xtn ∈ R.
Wtn ∈ R Q×Q and btn ∈ R Q denote the weight parameter and
bias, respectively. || denotes the concatenation operation.
Subsequently, the membership vectors corresponding to T
n
variable values in x1:T
are concatenated together to gain the
n
fuzzy embedding data fmvn1:T ∈ RT×Q for x1:T
, as shown in
the following equation:
fmvn1:T = fmvn1 fmvn2 · · · fmvnT .

Finally, the fuzzy embedding data of N feature slices
N
1
2
{x1:T
, x1:T
, . . . , x1:T
} are concatenated together to obtain the
final fuzzy embedding data FEX1:T ∈ R N ×T×Q for the input
sample sequence X 1:T ∈ R N ×T , as shown in the following
equation:
N
.
FEX1:T = fmv11:T fmv21:T · · · fmv1:T

1 ≤ t ≤ T, 1 ≤ q ≤ Q

(2)

where xtn ∈ R denotes the time-series data point at tth time
point. mdnt,q and MFqn denote the membership degree (i.e., the
influence degree of qth fuzzy state) and membership function,
respectively. µqn and σqn denote the center and the width of
MFqn , respectively, which can be adaptively updated during
model training.
Then, the outputs of Q membership functions (i.e., Q
membership degrees) are concatenated together to constitute
the membership vector for xtn ∈ R. Moreover, we use the
nonlinear mapping to obtain the membership vector with
stronger characterization ability, as shown in the following
equations:
mdnt = mdnt,1 mdnt,2 · · · mdnt,Q

fmvnt = tanh mdnt Wtn + btn

(6)

To make different fuzzy states that can characterize temporal
states with different semantics, we design a state diversity constraint to guarantee parameter diversity of Gaussian functions
to make fuzzy states have differences. It can calculate the
variance values of the centers of all Gaussian functions in
N fuzzy state sets and maximize their sum, as shown in the
following equation:
N

LS = −

−

(5)


1 X
Var µn1 , µn2 , . . . , µnQ
N n=1

(7)

where L S and Var denote the state diversity constraint and
variance function, respectively.
D. Global–Local Correlation-Based Refining Module

(3)

Due to temporal states natively having temporal dependence, we design a temporal proximity constraint to make
fuzzy embedding data possess temporal dependence and
evolve continuously.
1) Global Perspective: As shown in the top of Fig. 2
(module A), the interleaved downsampling [40] is performed
on fuzzy embedding data, which separates odd and even
elements along the time dimension to obtain two subsequences
FEX(odd) and FEX(even), as shown in the following equation:

(4)

DS(FEX1:T ) = [FEX(odd), FEX(even)]

(8)

ZHU et al.: FUZZY STATE-DRIVEN CROSS-TIME SPATIAL DEPENDENCE LEARNING

4537

and its output indicates the firing strength of the fuzzy rule
in response to the original time-series data [35], [42]. We use
the product T -norm operator on the fuzzy embedding data,
as shown in the following equation:
FR1:T (q) =

N
Y

FEXn1:T (q),

1≤q≤Q

(12)

n

Fig. 5.
Fuzzy inference uses a fuzzy ruler layer, conclusion layer, and
defuzzification layer to reconstruct time series.

where DS denotes the interleaved downsampling operation.
Then, FEX(odd) and FEX(even) are flattened to calculate
the correlation between them, as shown in the following
equation:
Corglobal = Cossim(Ft[FEX(odd)], Ft[FEX(even)])

(9)

where Corglobal denotes the global correlation. Ft[·] denotes
the flattening operation. Cossim denotes the cosine similarity.
Due to the trend and closeness properties of time-series data,
two subsequences obtained by interleaved downsampling still
possess temporal dependence of original time-series data [40],
[41]. Therefore, if the global correlation between two subsequences [i.e., FEX(odd) and FEX(even)] is higher, the stronger
temporal dependence characteristic of fuzzy embedding data
will be resulted.
2) Local Perspective: As shown in the bottom of Fig. 2
(module A), the cosine similarity method is used to successively calculate the correlation between fuzzy embedding data
belonging to adjacent time points, as shown in the following
equation:
T −1
1 X
Corlocal =
Cossim(Ft[FEXt ], Ft[FEXt+1 ]) (10)
T − 1 t=1

where Corlocal denotes the local correlation. FEXt denotes the
fuzzy embedding data at time point t.
Finally, the global correlation and local correlation are synthetically considered to build the temporal proximity constraint
LT , which is defined by the following equation:
LT =

(Corglobal + Corlocal )
.
2

(11)

E. Fuzzy Inference-Based Reconstructing Module
In this section, the fuzzy inference method is introduced to
generate the reconstructed time series as close as possible to
the original time series. As shown in Fig. 5, the fuzzy inference
method contains a fuzzy rule layer, a conclusion layer, and a
defuzzification layer.
The description of them is elaborated as follows.
1) Fuzzy Rule Layer: The number of neurons in this layer
is Q, which is equal to the number of membership functions
in a fuzzy state set. Each neuron is regarded as a fuzzy rule,

where FR1:T (q) ∈ RT denotes the firing strength of qth neuron
(qth fuzzy rule). FEXn1:T (q) ∈ RT denotes the membership
vector corresponding to nth variable and qth membership
function.
2) Conclusion Layer: This layer normalizes the firing
strengths of all fuzzy rules and concatenates them together,
as shown in the following equations:
FR1:T (q)
FRN(q) = P Q
i=1 FR1:T (i)
FRNall = FRN(1)||FRN(2)|| · · · ||FRN(Q)

(13)
(14)

where FRN(q) ∈ RT denotes the normalized firing strength of
qth neuron (qth fuzzy rule). FRNall ∈ RT×Q denotes the final
firing strength matrix.
3) Defuzzification Layer: This layer uses the nonlinear
mapping to perform defuzzification operation for generating
the reconstructed time-series data, as shown in the following
equation:
X̃ 1:T = tanh(FRNall W R + b R )
Q×N

(15)

N

where W R ∈ R
and b R ∈ R denote the weight parameter
and bias, respectively. X̃ 1:T ∈ RT×N denotes the reconstructed
time series. Moreover, its shape is converted to R N ×T to ensure
consistency with the shape of the original time-series data.
Finally, the loss function L R is built, which is defined by
the following equation:
1
2
X 1:T − X̃ 1:T 2
(16)
N ×T
where N and T denote the number of variables and time
points, respectively. X 1:T and X̃ 1:T denote the original values and reconstructed values, respectively. ∥·∥2 denotes the
L2-norm.
LR =

F. Spatiotemporal Dependencies Modeling Module
This module adopts a prediction-oriented framework, using
the data at historical time points (1, 2, . . . , T − 1) to predict
the data at future time point T , and thus, the input of this
module is a partial of fuzzy embedding data, i.e., FEX1:T −1 ∈
R N ×(T−1)×Q .
1) CTSG Generation: As shown in Fig. 6, CTSG uses
the membership vectors generated by TS2MVec to calculate
similarities among all time-series data points (including all
variables) across two adjacent time points. Then, all the
similarities are aggregated to explicitly represent complete spatiotemporal dependencies (i.e., spatial dependence, temporal
dependence, and cross-time spatial dependence).
The generation process of CTSG is described as follows.
First,
FEX1:T −1
is
split
into
data
slices
FEX1:2 , FEX2:3 , . . . , FEXT −2:T −1 ∈ R N ×2×Q , and then,

4538

Fig. 6.

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 3, MARCH 2025

Example of CTSG generation.

the corresponding CTSG is generated for each data slice. For
FEXt:t+1 ∈ R N ×2×Q (1 ≤ t ≤ T − 2), it is first reshaped as
FEXt:t+1 ∈ R2N ×Q , which contains the membership vectors
of 2N variables (N variables at time point t and N variables
at time point t + 1). Then, the generation process can be
formulated by the following equation:
CTSGt:t+1 (i, j) = Cossim(FEXt:t+1 (i), FEXt:t+1 ( j))
i, j = 1, 2, . . . , 2N

(17)

where i and j denote ith and jth nodes in CTSG, respectively.
FEXt:t+1 (i) and FEXt:t+1 ( j) denote the membership vectors of
the ith and jth variables, respectively. Moreover, sparse operation is performed to preserve the most important correlations
to obtain the final CTSGt:t+1 ∈ R2N ×2N .
In particular, all the membership vectors change adaptively
as the time series evolves, which endows the CTSG with the
ability to learn mutable spatiotemporal dependencies (especially, cross-time spatial dependence). In CTSG, we only
consider the spatiotemporal dependencies within two adjacent time points because build larger size (e.g., 3N × 3N
or 4N × 4N ) to characterize longer time spans will bring
higher computational costs. Thus, we unite multiple CTSGs
to construct a deep hierarchical architecture (i.e., CTSNet),
which uses the stacking of graph convolution layers to capture
long-term spatiotemporal dependencies.
2) CTSNet: As shown in Fig. 7, CTSNet possesses a
deep hierarchical architecture, which contains multiple stacked
layers to capture long-term spatiotemporal dependencies, and
employs the skip connection to obtain high-level feature
representations. In each stacked layer, multiple independent
mix-hop graph neural networks (MHGNNs) are customized
for multiple data slices FEX1:2 , FEX2:3 , . . . , FEXT −2:T −1 , and
these MHGNNs can carry out in parallel to enhance the model
efficiency. Specifically, each MHGNN exploits multiple graph
convolutional structures to extract features and introduces
the activation function gated linear unit (GLU) to conduct
nonlinear transformations and then aggregate the features of
all graph convolutional structures by a max-pooling layer.
Technically, the reshaped data slice FEXt:t+1 ∈ R2N ×Q
and its corresponding CTSGt:t+1 ∈ R2N ×2N are input into a
mix-hop graph convolutional network (GCN), as shown in the
following equations:
− 12
− 21
At:t+1 = Dt:t+1
CTSGt:t+1 Dt:t+1

(18)

Fig. 7.
Hierarchical architecture of the proposed CTSNet. (a) CTSNet
adopts S layers to extract hierarchical feature representations and uses skip
connection to fuse them. (b) In each layer in CTSNet, multiple mix-hop GCNs
are conducted parallelly and independently.



At:t+1 FEXt:t+1 W1l + b1l




⊙σ A
l
l
t:t+1 FEXt:t+1 W2 + b2 , l = 1
l


Ht:t+1 =
l−1

At:t+1 Ht:t+1
W1l + b1l ⊙ σ At:t+1 Hil−1 W2l + b2l ,



l = 2, 3, . . . , L
(19)
where Dt:t+1 ∈ R2N ×2N is the degree matrix of CTSGt:t+1 .
At:t+1 ∈ R2N ×2N is the normalized adjacency matrix of
CTSGt:t+1 . W1l , W2l ∈ R Q×C1 , and b1l , b2l ∈ RC1 are the
parameters in the activation function GLU [43]. C1 is the
desired output channel dimension. L denotes the number of
l
layers in mix-hop GCN. Ht:t+1
∈ R2N ×C1 denotes the output
of the lth layer, which contains two parts of spatiotemporal
dependencies features (i.e., Htl ∈ R N ×C1 at time point t and
l
Ht+1
∈ R N ×C1 at time point t + 1).
Next, we aggregate them to obtain a consistent representation of spatiotemporal dependencies over this time period (t
and t + 1)

l
H Alt:t+1 = Agg Htl , Ht+1
(20)
where H Alt:t+1 ∈ R N ×C1 denotes the output. Agg(·) denote the
elementwise addition.
To eliminate useless information and retain important information in L layers, the max-pooling is performed, which is
formulated by the following equation:

L
H Mt:t+1 = Maxpooling H A1t:t+1 , H A2t:t+1 , . . . , H At:t+1
.
(21)
Then, the outputs of all mix-hop GCNs are concatenated to
(1)
form the final output UCTSN
∈ R N ×(T −2)×C1 , as shown in the
following equation:
(1)
UCTSN
= H M1:2 ||H M2:3 || · · · ||H MT −2:T −1 .

(22)

The outputs of S stacked layers are fused by the skip
connection to capture long-term spatiotemporal dependencies,
as shown in the following equation:
Uall =

S
X
s=1

(s)
UCTSN
∗ ϑs

(23)

ZHU et al.: FUZZY STATE-DRIVEN CROSS-TIME SPATIAL DEPENDENCE LEARNING
(s)
where UCTSN
∈ R N ×(T−1−s)×C1 denotes the output of the sth
layer in CTSNet. ϑs ∈ R1×(T−1−s)×C2 denotes the sth convolution kernel. C2 is the desired output channel dimension.
Uall ∈ R N ×C2 denotes the high-level feature representations.
Subsequently, two fully connected layers are used to refine
the feature information in Uall and output the predicted results
x̂ T ∈ R N , as shown in the following equation:

x̂ T = g(Uall W3 + b3 )W4 + b4

(24)

where W3 ∈ R
, W4 ∈ R
denote the weight parameters. b3 ∈ RC3 , b4 ∈ R denote the biases (C3 denotes the
number of neurons in the first fully connected layer). g denotes
the activation function rectified linear unit (ReLU) [44].
Finally, the loss function L P is built, which is defined by
the following equation:
C2 ×C3

C3 ×1

LP =

1
2
x T − x̂ T 2
N

(25)

where N denotes the number of variables. x T and x̂ T denote
the real and predicted values at time point T , respectively.

G. Joint Evolution Objective
In this section, a joint evolution objective is designed to
train the FE-CTSNet, including state diversity constraint L S ,
temporal proximity constraint LT , reconstruction constraint
L R , and prediction constraint L P , as shown in the following
equation:
epo

epo

λ
λ
L J = λ1 L S + 2 LT + 3 L R
2
2
+ 1 − λ1 −

epo

epo 

λ
λ2
− 3
2
2

LP

(26)

where λ1 , λ2 , and λ3 are the tradeoff coefficients. epo denotes
the training epoch.
The joint of L R and L P can exploit the advantages of both
reconstruction-oriented and prediction-oriented ideas to realize
anomaly detection. However, there exist two problems if only
using L R and L P to optimize FE-CTSNet.
Problem 1: Since only Gaussian functions are adopted to
construct fuzzy states, all fuzzy states may become similar
during training (the parameters of all Gaussian functions may
converge to similar values), which is ineffective to characterize
diversiform temporal states.
Problem 2: Since the membership degrees of fuzzy states
are randomly initialized before training, fuzzy states at adjacent time points may not have a temporal dependence, which is
unable to characterize continuously evolving temporal states.
Therefore, we add two auxiliary objectives L S and LT to
solve problems 1 and 2, respectively. Specifically, L S can
ensure the differences among fuzzy states to improve its ability
to characterize diversiform temporal states. LT can endow
fuzzy states with temporal dependence to enhance their ability
to represent continuously evolving temporal states. Through
synthetically co-optimizing L S , LT , L R , and L P , FE-CTSNet
with superior performance can be obtained.

4539

TABLE II
DATASET S TATISTICS

H. Anomaly Inference
In this section, only modules C and D are used to obtain
anomaly scores because module B is an auxiliary module
to improve the characterization ability of fuzzy states rather
than to detect anomalies. The detailed process is summarized
in Algorithm 1. It can be seen that each sample sequence
test
test
test
test
N ×T
X t−T
is input into
+1:t = {x t−T +1 , x t−T +2 , . . . , x t } ∈ R
the well-trained modules C and D to obtain the anomaly score
ϕ for xttest ∈ R N

2
2
φscore xttest = ω1 xttest − x̃ test
+ ω2 xttest − x̂ test
(27)
t
t
2
2
where x̃ test
and x̃ test
denote the reconstructed and predicted
t
t
values, respectively. Hyperparameters ω1 and ω2 are used
to tradeoff the reconstruction-oriented error and predictionoriented error.
Then, peak over threshold (POT) [45] is introduced to
adaptively choose the threshold η. If ϕ(xttest ) > η, the anomaly
label ŷ t is assigned 1 (abnormal), otherwise 0 (normal).
Algorithm 1 FE-CTSNet Anomaly Inference Process
Input: Module C parameter PC , module D parameter P D ,
abnormal and normal test set contains R sample sequences
test
test
test
N ×T
where
, X 2:T
X 1:T
+1 , . . . , X R:T +R−1 ∈ R
test
test
test
test
N
∈
R
(0 ≤ i ≤ R − 1).
,
.
.
.
,
x
,
x
=
x
X 1+i:T
T +i
2+i
1+i
+i
Output: All anomaly labels ŷ T +i for x Ttest
+i (0 ≤ i ≤ R − 1)
1: Calculate the threshold η through POT
2: for i = 0 to R-1 do
test
3: x̃ test
T +i ← PC (X 1+i:T +i )
test
4: x̂ test
←
P
(X
D
T +i
1+i:T +i−1 )
2
2
test
5: ϕ(x T +i ) ← ω1 xttest − x̃ test
+ ω2 xttest − x̂ test
t
t
2
2
test
6: if ϕ(x T +i ) > η then
7: ŷ T +i ← 1
8: else
9:
ŷ T +i ← 0
10: end if
11: end for
12: return all anomaly labels ŷ T +i (0 ≤ i ≤ R − 1)

IV. E XPERIMENTS
A. Datasets and Evaluation Metrics
To verify the superior performance of FE-CTSNet, we conducted experiments on three public datasets, including server
machine dataset (SMD) [24], application server dataset (ASD)
[8], and multisource distributed system (MSDS) [12]. In particular, for SMD, we selected machines 1-1, 2-2, and 3-2 as
verification objects and reported the average results of these
three machines. For ASD, we selected servers 7, 8, and 9 as
verification objects and also reported the average results of
these three servers. More statistics are shown in Table II.

4540

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 3, MARCH 2025

Moreover, we used four metrics including precision (P),
recall (R), F1 score (F1), and area under the receiver operating
characteristic curve (AUC) to evaluate the effectiveness of all
models. In particular, all the experimental results in this study
were average results recorded after five executions.
Currently, many prior studies [1], [24], [46], have calculated
the metrics based on a common strategy, i.e., point-adjust: if
at least one observation in an anomaly segment is correctly
detected as an anomaly, this whole anomaly segment will be
regarded as correctly detected. Following this paradigm, the
point-adjust strategy was also applied in this study.
B. Baseline Models
1) State-of-the-Art Models: To demonstrate our superiority,
we selected 14 anomaly detection models as comparison, including IF [4], PCA [18], SFA [20], CVA [21],
DAGMM [27], GDN [26], SG-AE [28], OmniAnomaly [24],
USAD [29], AAU-Net [25], TranAD [12], TopoMAD [32],
MSCRED [30], and MTAD-GAT [31].
2) Variants of FE-CTSNet: To show the necessity of each
component in FE-CTSNet, we exclude every important one to
construct multiple variants, as shown in Table III (each tick
denotes the elimination of a component).
C. Model Implementation
FE-CTSNet and all baseline models were implemented
using PyTorch on a computer with NVIDIA GeForce
RTX 2080 GPU. To ensure the comparison fairness,
we adopted POT to automatically select optimal thresholds
for FE-CTSNet and all baseline models. Moreover, we also
implemented the point-adjust strategy for FE-CTSNet and all
baseline models.
For FE-CTSNet, validation sets were used to select the
optimal combination of hyperparameters. The final hyperparameters in FE-CTSNet were depicted by the grid search
method: the length of sliding window T was 10, the size
of ϑct was 1 × 3 × 1, and the fuzzy state dimension Q
(the number of membership functions) was 150. The number
of layers in CTSNet was 3, the number of layers in each
mix-hop GCN was 4, the channel dimension C1 was 64, the
channel dimension C2 was 64, and the number of neurons in
the first fully connected layer C3 was 128. λ1 , λ2 , and λ3 were
0.01, 0.6, and 0.9, respectively. ω1 and ω2 were 0.2 and 0.8,
respectively. In addition, the training epoch was set to 30 and
the batch size was set to 256. In addition, the Adam optimizer
with a learning rate of 0.001 is used to conduct end-to-end
training.
D. Result Discussion
1) Overall Performance Comparison: Table IV reports the
anomaly detection results of all models on three datasets.
Among machine learning models, IF presents the inferior
performance because it neglects temporal and spatial dependencies. In addition, PCA, SFA, and CVA achieve better
results due to their consideration of temporal dependence or
spatial dependence. However, these models suffer from high
false detection rates because their linear hypothesis may not
handle complex nonlinear scenarios well.

TABLE III
VARIANTS OF FE-CTSN ET

In contrast, deep learning models perform better than
machine learning models. However, the detection results
of deep learning models show differences. Specifically,
DAGMM, SG-AE, GDN, OmniAnomaly, AAU-Net, and
TranAD obtain unsatisfactory detection results because they
only consider intervariable spatial dependence or intravariable
temporal dependence. Compared to the above models, USAD,
TopoMAD, MSCRED, and MTAD-GAT gain some promising
detection results, demonstrating that the importance of simultaneously considering intervariable spatial dependence and
intravariable temporal dependence. Among them, MSCRED
is not as reliable as MTAD-GAT and TopoMAD in most
metrics because the signature matrix used in MSCRED may
fail to identify subtle anomalies and model complex and
nonlinear spatial dependence well. Though MTAD-GAT and
TopoMAD use the graph structure to realize the relatively
great performance compared with other baseline models, it still
remains suboptimal performance because it ignores cross-time
spatial dependence. In summary, FE-CTSNet achieves the
best F1 and AUC on SMD and ASD, and the best F1 and
the second-best AUC on MSDS, which illustrates the importance of disentangling mixing temporal states and capturing
cross-time spatial dependence.
To further support the conclusion above, Fig. 8 visualizes
the anomaly detection results of FE-CTSNet and some deep
learning models. Gray solid lines and red dashed lines represent anomaly scores and threshold, respectively. Blue-shaded
regions represent the predicted anomalies, and red-shaded
regions represent the true anomalies, which contain two
types: pointwise anomalies and collectivewise anomalies. In all
models, the observations whose anomaly scores exceed the
corresponding threshold are marked as anomalies. For SMD
(machine 1-1), all models can identify all anomalies. However,
some deep learning models present many false alarms (e.g.,
GDN, USAD, MTAD-GAT, and OminAnomaly), which is
not conducive for practical scenarios. For ASD (server 7),
compared to other baseline models, FE-CTSNet can generate higher anomaly scores for true anomalies and smoother
anomaly scores for normal moments, which demonstrates that
FE-CTSNet is more sensitive and robust to the evolution laws
of time series.
2) Ablation Study: This section investigates the effectiveness of each important component in FE-CTSNet. The relevant
variants are listed in Table II, and the corresponding detection
results from dataset ASD (server 7) are shown in Fig. 9.
We can draw the following conclusions.

ZHU et al.: FUZZY STATE-DRIVEN CROSS-TIME SPATIAL DEPENDENCE LEARNING

4541

TABLE IV
P ERFORMANCE C OMPARISON OF FE-CTSN ET W ITH THE S TATE - OF - THE -A RT M ODELS ON T HREE DATASETS

Fig. 8. Predicted and true anomalies on SMD (machine 1-1) and ASD (server 7). Since collectivewise anomalies is a contiguous anomaly segment, the
point-adjust method is adopted: if at least one observation in collectivewise anomalies is predicted as an anomaly, the whole collectivewise anomalies will
be regarded as correctly detected. Therefore, some observations in collectivewise anomalies with anomaly scores below the threshold are also labeled to be
anomalies. (a) SMD (machine 1-1). (b) ASD (server 7).

1) Compare FE-CTSNet With Variants 1 and 2: The ignorance of cross-time spatial dependence and temporal
dependence can both remarkably degrade the model
performance.

2) Compare FE-CTSNet With Variant 3: Module A
(fuzzy embedding module) is superior to fully connected layers, which indicates that using fuzzy
states to characterize latent and mixing temporal

4542

Fig. 9.

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 3, MARCH 2025

Ablation study results on ASD (server 7).

states is helpful for improving anomaly detection
results.
3) Compare FE-CTSNet With Variants 4, 5, and 6: Modules
B, C, and D are all essential for FE-CTSNet. Moreover,
module D has a more significant contribution to model
performance than the other two modules, illustrating the
potential of CTSG in capturing complete spatiotemporal
dependencies for promoting detection results.
E. Specific Analysis
1) Effectiveness of CTSG: Fig. 10 visualizes an example of
CTSG after training. The horizontal coordinate and vertical
coordinate in the heatmap indicate the corresponding variable
indexes (ten variables at time point t1 and ten variables at time
point t2 ). A cell with a darker color indicates the stronger
interaction between pairwise variables, while a cell with a
lighter color indicates the opposite. As can be seen, CTSG can
uniformly and flexibly characterize complete spatiotemporal
dependencies. Specifically, CTSG captures strong autocorrelations of variables along the time axis (time interval 1),
as shown in the green area, which proves the effectiveness
of the designed temporal proximity constraint in ensuring
the temporal dependence of fuzzy states. Moreover, it can
also capture other intervariable correlations, i.e., intervariable
correlations at the same time point in the gray area and intervariable correlations at different time points in the orange area.
These intervariable correlations are crucial for discovering
anomalies in multivariable time series because anomalies often
propagate between different variables.
2) Effectiveness of Fuzzy States: Fig. 11 provides a real
server cluster example (a server is denoted as a variable)
of how FE-CTSNet exploiting fuzzy states to detect the
time-delay anomaly. Specifically, the time-delay anomaly
propagates from abnormal time period A in variable 2 to
abnormal time period B in variable 8. Through FE-CTSNet,
each data point in variables 2 and 8 is converted into a corresponding membership vector. Apparently, membership vectors
exhibit difference between abnormal time points and normal
time points (e.g., membership vectors at normal time point
755 and abnormal time point 758 in variable 2), indicating that
fuzzy states have the ability to distinguish between anomaly
and normal. Further, we find out that the membership vectors
of variable 2 at anomaly time period A are quite similar to
that of variable 8 at anomaly time period B, indicating that
fuzzy states successfully discovers strong cross-time spatial
dependencies between them, thereby endowing FE-CTSNet
with the ability to sense the time-delay anomaly propagating
from variable 2 to variable 8. Based on it, if the anomaly

Fig. 10.

Example of CTSG in the validation set on MSDS.

in abnormal time period A can be detected, FE-CTSNet will
easily infer the time-delay anomaly in abnormal time period B.
3) Hyperparameter Test: We evaluate the sensitivities of
some key hyperparameters in FE-CTSNet: tradeoff coefficients
in the joint evolution objective L J , the number of layers in
CTSNet S, and the number of fuzzy states Q.
a) Sensitivity of λ1 and λ2 in L J : λ1 and λ2 control
the influences of two auxiliary objectives (i.e., state diversity
constraint and temporal proximity constraint) on L J . Too small
λ1 and λ2 may make fuzzy states lose their diversity and
evolution continuity, thus degrading the ability to characterize
latent temporal states. Too large λ1 and λ2 may hamper the
normal optimization of main objectives (prediction and reconstruction for time series), leading to poor anomaly detection
performance. We test λ1 with values from {0.001, 0.01, 0.1,
0.5, 1} and λ2 with values from {0.2, 0.4, 0.6, 0.8, 1}. It can be
found that the superior results are gained when λ1 = 0.01 and
λ2 = 0.6 [Fig. 12(a) and (b)], which is consistent with the
previous theoretical analysis.
b) Sensitivity of λ3 in L J : λ3 controls the balance
between the prediction task and the reconstruction task.
Fig. 12(c) shows that λ3 with large value (0.9) realizes the
best performance, indicating that the joint evolution objective
should focus more on the reconstruction module in the early
training phase.
c) Sensitivity of S: S controls the ability of FE-CTSNet
to capture long-term cross-time spatial dependence. As shown
in Fig. 13(a) (solid lines and shadows indicate the average
results and the standard deviations, respectively), it is found
that S = 3 performs best in terms of all metrics, illustrating
that too small S may fail to effectively capture long-term
spatiotemporal dependencies, while too large S may lead to
overfitting problems.
d) Sensitivity of Q: Q controls the number of fuzzy
states for disentangling mixing temporal states. As shown in
Fig. 13(b), it is found that using Q = 150 obtains better
detection results than those obtained by using other values
in terms of the maximum, minimum, and median of F1. This
illustrates that a certain number of fuzzy states is necessary to
reasonably characterize latent and mixing temporal states, but
redundant fuzzy states may degrade its characterization ability.
4) Convergence of L J : To demonstrate the reasonability
of the optimization process in FE-CTSNet, the losses of
L J , L S , LT , L R , and L P in the validation set are shown
in Fig. 12(d). The loss of L J quickly reaches convergence
with small fluctuations, which verifies that all modules of

ZHU et al.: FUZZY STATE-DRIVEN CROSS-TIME SPATIAL DEPENDENCE LEARNING

4543

V. C ONCLUSION

Fig. 11. Five fuzzy states in the test set on ASD (server 9) are randomly
chosen as an example to illustrate its effectiveness. The color of each cell in
the membership vector represents the magnitude of the membership degree
(a cell with a darker color indicates the larger membership degree).

In this study, we propose a novel FE-CTSNet to realize the disentanglement for mixing temporal states from a
fuzzy embedding perspective and exploiting it to sense the
intricateness and mutability of cross-time spatial dependence,
thus improving the detection performance for time-delay
anomalies. Specifically, the proposed TS2Mvec can build
fine-grained fuzzy states to represent latent temporal states
and generate membership degrees to accurately reflect mixing
modes and dynamical evolutions of temporal states. Built upon
fuzzy states, the proposed CTSG can flexibly learn mutable
cross-time spatial dependence. Moreover, the designed state
diversity and temporal proximity constraints possess the great
convergence, which can effectively ensure the differences
among fuzzy states and the evolution continuity of fuzzy
states, thereby further enhancing their characterization ability
for latent temporal states. Experiments on three public datasets
demonstrate the superiority of FE-CTSNet and the effectiveness of its important components. In addition, the visualization
of fuzzy states and CTSG illustrates the excellent potential of
FE-CTSNet in discovering time-delay anomalies.
Future directions will focus on distinguishing transient
impulsive interferences and anomalies, enabling FE-CTSNet
to achieve more fine-grained and accurate anomaly detection
in practical industrial applications.
R EFERENCES

Fig. 12. Hyperparameter test results. (a)–(c) F1 and AUC of λ1 , λ2 , and λ3
on ASD (server 7) and MSDS. (d) Convergence analysis in the validation set
on ASD (server 9).

Fig. 13. Hyperparameter test results. (a) and (b) Sensitivity analysis of S
and Q on ASD (server 9).

FE-CTSNet can be co-optimized well during the training
iterations. Simultaneously, the losses of L S and LT rise
gradually at the beginning of training and then become stable,
which verifies that the L S and LT can effectively realize
their respective goals, that is, to enhance the diversity and
evolution continuity of fuzzy states; the loss of L R and L P
drops gradually during the training iterations, illustrating that
FE-CTSNet can successfully capture complete spatiotemporal
dependencies (especially, cross-time spatial dependence) and
learn specific patterns of time series to reconstruct and predict
time series, thereby achieving effective anomaly detection.

[1] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time
series anomaly detection with association discrepancy,” in Proc. Int.
Conf. Learn. Represent., 2019, pp. 3068–3075.
[2] Y. Zhang, J. Wang, Y. Chen, H. Yu, and T. Qin, “Adaptive memory
networks with self-supervised learning for unsupervised anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 2, pp. 12068–12080,
Dec. 2022.
[3] R. Laxhammar, G. Falkman, and E. Sviestins, “Anomaly detection in
sea traffic—A comparison of the Gaussian mixture model and the
kernel density estimator,” in Proc. 12th Int. Conf. Inf. Fusion, Jul. 2009,
pp. 756–763.
[4] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. 8th
IEEE Int. Conf. Data Mining, Dec. 2008, pp. 413–422.
[5] C. Song, Y. Lin, S. Guo, and H. Wan, “Spatial–temporal synchronous
graph convolutional networks: A new framework for spatial–temporal
network data forecasting,” in Proc. AAAI Conf. Artif. Intell., vol. 34,
no. 1, 2020, pp. 914–921.
[6] Y. Zhang, Y. Chen, J. Wang, and Z. Pan, “Unsupervised deep anomaly
detection for multi-sensor time-series signals,” IEEE Trans. Knowl. Data
Eng., vol. 35, no. 2, pp. 2118–2132, Feb. 2023.
[7] S. Zhang, K. Zhu, and W. Zhang, “Multivariate correlation matrix-based
deep learning model with enhanced heuristic optimization for short-term
traffic forecasting,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 3,
pp. 2847–2858, Mar. 2023.
[8] Z. Li et al., “Multivariate time series anomaly detection and interpretation using hierarchical inter-metric and temporal embedding,” in Proc.
27th ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug. 2021,
pp. 3220–3230.
[9] W. Chen, L. Tian, B. Chen, L. Dai, Z. Duan, and M. Zhou, “Deep
variational graph convolutional recurrent network for multivariate time
series anomaly detection,” in Proc. Int. Conf. Mach. Learn., 2022,
pp. 3621–3633.
[10] P. Song, C. Zhao, B. Huang, and J. Ding, “Explicit representation and
customized fault isolation framework for learning temporal and spatial
dependencies in industrial processes,” IEEE Trans. Neural Netw. Learn.
Syst., early access, Apr. 3, 2023, doi: 10.1109/TNNLS.2023.3262277.
[11] C. Zhao, “Perspectives on nonstationary process monitoring in the
era of industrial artificial intelligence,” J. Process Control, vol. 116,
pp. 255–272, Aug. 2022.

4544

IEEE TRANSACTIONS ON NEURAL NETWORKS AND LEARNING SYSTEMS, VOL. 36, NO. 3, MARCH 2025

[12] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” in Proc.
Int. Conf. Very Large Data Bases, vol. 15, no. 6, 2022, pp. 1201–1214.
[13] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and
T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric dynamic thresholding,” in Proc. 24th ACM SIGKDD Int.
Conf. Knowl. Discovery Data Mining, Jul. 2018, pp. 387–395.
[14] L. Feng, C. Zhao, Y. Li, M. Zhou, H. Qiao, and C. Fu, “Multichannel
diffusion graph convolutional network for the prediction of endpoint
composition in the converter steelmaking process,” IEEE Trans. Instrum.
Meas., vol. 70, pp. 1–13, 2021.
[15] K. Zhu and C. Zhao, “Dynamic graph-based adaptive learning for online
industrial soft sensor with mutable spatial coupling relations,” IEEE
Trans. Ind. Electron., vol. 70, no. 9, pp. 9614–9622, Sep. 2023.
[16] H. Wu, T. Hu, Y. Liu, H. Zhou, J. Wang, and M. Long, “TimesNet:
Temporal 2D-variation modeling for general time series analysis,” in
Proc. Int. Conf. Learn. Represent., 2023, pp. 1–22.
[17] S. Liu, X. Li, G. Cong, Y. Chen, and Y. Jiang, “Multivariate time series
imputation with disentangled temporal representations,” in Proc. Int.
Conf. Learn. Represent., 2023, pp. 1–19.
[18] H. Hotelling, “Analysis of a complex of statistical variables into principal
components,” J. Educ. Psychol., vol. 24, no. 6, p. 417, 1933.
[19] P. Song and C. Zhao, “Slow down to go better: A survey on slow
feature analysis,” IEEE Trans. Neural Netw. Learn. Syst., early access,
Sep. 7, 2022, doi: 10.1109/TNNLS.2022.3201621.
[20] L. Wiskott and T. J. Sejnowski, “Slow feature analysis: Unsupervised
learning of invariances,” Neural Comput., vol. 14, no. 4, pp. 715–770,
Apr. 2002.
[21] A. Norvilas, A. Negiz, J. DeCicco, and A. Çinar, “Intelligent process
monitoring by interfacing knowledge-based systems and multivariate
statistical monitoring,” J. Process Control, vol. 10, no. 4, pp. 341–350,
Aug. 2000.
[22] Z. Chai, C. Zhao, and B. Huang, “Multisource-refined transfer network
for industrial fault diagnosis under domain and category inconsistencies,” IEEE Trans. Cybern., vol. 52, no. 9, pp. 9784–9796, Sep. 2022.
[23] Z. Liu, C. Zhao, Y. Lu, Y. Jiang, and J. Yan, “Multi-scale graph learning
for ovarian tumor segmentation from CT images,” Neurocomputing,
vol. 512, pp. 398–407, Nov. 2022.
[24] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discovery Data
Mining, Jul. 2019, pp. 2828–2837.
[25] B. An, S. Wang, F. Qin, Z. Zhao, R. Yan, and X. Chen, “Adversarial algorithm unrolling network for interpretable mechanical anomaly
detection,” IEEE Trans. Neural Netw. Learn. Syst., early access,
Mar. 14, 2023, doi: 10.1109/TNNLS.2023.3250664.
[26] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., Feb. 2021,
vol. 35, no. 5, pp. 4027–4035.
[27] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Represent., 2021,
pp. 1–19.
[28] Z. Huang, B. Zhang, G. Hu, L. Li, Y. Xu, and Y. Jin, “Enhancing
unsupervised anomaly detection with score-guided network,” IEEE
Trans. Neural Netw. Learn. Syst., early access, Jun. 7, 2023, doi:
10.1109/TNNLS.2023.3281501.
[29] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining,
Aug. 2020, pp. 3395–3404.
[30] C. Zhang et al., “A deep neural network for unsupervised anomaly
detection and diagnosis in multivariate time series data,” in Proc. AAAI
Conf. Artif. Intell., vol. 33, no. 1, 2019, pp. 1409–1416.
[31] H. Zhao et al., “Multivariate time-series anomaly detection via graph
attention network,” in Proc. IEEE Int. Conf. Data Mining (ICDM),
Nov. 2020, pp. 841–850.
[32] Z. He et al., “A spatiotemporal deep learning approach for unsupervised
anomaly detection in cloud systems,” IEEE Trans. Neural Netw. Learn.
Syst., vol. 34, no. 4, pp. 1705–1719, Apr. 2023.
[33] P. Hájek, L. Godo, and F. Esteva, “Fuzzy logic and probability,” in Proc.
Conf. Uncertainty Artif. Intell., 1995, pp. 237–244.
[34] L. A. Zadeh, “Fuzzy sets,” Inf. Control, vol. 8, no. 3, pp. 338–353, 1965.
[35] H. Nasiri and M. M. Ebadzadeh, “MFRFNN: Multi-functional recurrent
fuzzy neural network for chaotic time series prediction,” Neurocomputing, vol. 507, pp. 292–310, Oct. 2022.

[36] Q. Dai, C. Zhao, and B. Huang, “Incremental variational Bayesian
Gaussian mixture model with decremental optimization for distribution accommodation and fine-scale adaptive process monitoring,” IEEE
Trans. Cybern., vol. 53, no. 8, pp. 5094–5107, Aug. 2022.
[37] Y. Deng, Z. Ren, Y. Kong, F. Bao, and Q. Dai, “A hierarchical fused
fuzzy deep neural network for data classification,” IEEE Trans. Fuzzy
Syst., vol. 25, no. 4, pp. 1006–1012, Aug. 2017.
[38] M. M. Ebadzadeh and A. Salimi-Badr, “IC-FNN: A novel fuzzy neural
network with interpretable, intuitive, and correlated-contours fuzzy rules
for function approximation,” IEEE Trans. Fuzzy Syst., vol. 26, no. 3,
pp. 1288–1302, Jun. 2018.
[39] G. Wang and J. Qiao, “An efficient self-organizing deep fuzzy neural
network for nonlinear system modeling,” IEEE Trans. Fuzzy Syst.,
vol. 30, no. 7, pp. 2170–2182, Jul. 2022.
[40] M. Liu et al., “SCINet: Time series modeling and forecasting with
sample convolution and interaction,” in Proc. Adv. Neural Inf. Process.
Syst., vol. 35, 2022, pp. 5816–5828.
[41] A. Liu and Y. Zhang, “Spatial–temporal interactive dynamic graph
convolution network for traffic forecasting,” 2022, arXiv:2205.08689.
[42] A. Salimi-Badr and M. M. Ebadzadeh, “A novel learning algorithm
based on computing the rules’ desired outputs of a TSK fuzzy neural
network with non-separable fuzzy rules,” Neurocomputing, vol. 470,
pp. 139–153, Jan. 2022.
[43] Y. N. Dauphin, A. Fan, M. Auli, and D. Grangier, “Language modeling
with gated convolutional networks,” in Proc. Int. Conf. Mach. Learn.,
2017, pp. 933–941.
[44] V. Nair and G. E. Hinton, “Rectified linear units improve restricted
Boltzmann machines,” in Proc. Int. Conf. Mach. Learn., 2010,
pp. 807–814.
[45] A. Siffer, P.-A. Fouque, A. Termier, and C. Largouet, “Anomaly detection in streams with extreme value theory,” in Proc. 23rd ACM SIGKDD
Int. Conf. Knowl. Discovery Data Mining, Aug. 2017, pp. 1067–1075.
[46] H. Xu et al., “Unsupervised anomaly detection via variational
auto-encoder for seasonal KPIs in web applications,” in Proc. World
Wide Web Conf., 2018, pp. 187–196.

Kun Zhu received the M.S. degree from the
Zhejiang University of Finance and Economics,
Hangzhou, China, in 2022. He is currently pursuing
the Ph.D. degree with the College of Control Science
and Engineering, Zhejiang University, Hangzhou.
His research interests mainly include anomaly
detection and deep learning.

Pengyu Song received the B.Eng. degree in electronic information engineering from the College
of Electrical Engineering, Zhejiang University,
Hangzhou, China, in 2020, where he is currently
pursuing the Ph.D. degree in control science and
engineering with the College of Control Science and
Engineering.
His current research interests include anomaly
detection and root cause diagnosis.

Chunhui Zhao (Senior Member, IEEE) received
the Ph.D. degree from Northeastern University,
Shenyang, China, in 2009.
From 2009 to 2012, she was a Post-Doctoral
Fellow with the Hong Kong University of Science
and Technology, Hong Kong, and the University
of California at Santa Barbara, Santa Barbara, CA,
USA. Since January 2012, she has been a Professor
with the College of Control Science and Engineering, Zhejiang University, Hangzhou, China. She has
authored or coauthored more than 200 articles in
peer-reviewed international journals. Her research interests include statistical
machine learning and data mining for industrial application.
Dr. Zhao has served as a Senior Editor for Journal of Process Control and an
Associate Editor of two international journals, including Control Engineering
Practice and Neurocomputing.
PAPER_TEXT
