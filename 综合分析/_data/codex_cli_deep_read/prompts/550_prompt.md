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
# [550] Spatio-Temporal Predictive Learning Using Crossover Attention for Communications and Networking Applications
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
编号：550
题名：Spatio-Temporal Predictive Learning Using Crossover Attention for Communications and Networking Applications
年份：2025
DOI：10.1109/tmlcn.2025.3555975
来源：IEEE Transactions on Machine Learning in Communications and Networking
PDF：paper/10.1109_TMLCN.2025.3555975.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：无
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\550.txt
- 原始字符数：59388
- 本次发送字符数：59388
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Received 5 September 2024; revised 17 December 2024 and 4 February 2025; accepted 20 March 2025.
Date of publication 31 March 2025; date of current version 9 April 2025.
The associate editor coordinating the review of this article and approving it for publication was X. Chu.
Digital Object Identifier 10.1109/TMLCN.2025.3555975

Spatio-Temporal Predictive Learning Using
Crossover Attention for Communications
and Networking Applications
KE HE

1 (Graduate Student Member, IEEE), THANG XUAN VU
2 , SYMEON CHATZINOTAS

LISHENG FAN
AND BJÖRN OTTERSTEN

1 (Senior Member, IEEE),

1 (Fellow, IEEE),

1 (Fellow, IEEE)

1 Interdisciplinary Centre for Security, Reliability and Trust (SnT), University of Luxembourg, 1855 Luxembourg City, Luxembourg
2 School of Computer Science, Guangzhou University, Guangzhou 510006, China

CORRESPONDING AUTHOR: T. X. VU (thang.vu@uni.lu)
This work was supported in part by Luxembourg National Research Fund (FNR) under Grant FNR/C19/IS/13718904/ASWELL, Grant
FNR/C22/IS/17220888/RUTINE, Grant INTER/23/17941203/PASSIONATE, and Grant INTER/MOBILITY/2023/IS/18014377/MCR; in part by
the National Natural Science Foundation of China (NSFC) under Grant U23A20273; and in part by Guangdong Provincial Key Research and
Development Program under Grant 2024B0101040006.

This paper investigates the spatio-temporal predictive learning problem, which is crucial
in diverse applications such as MIMO channel prediction, mobile traffic analysis, and network slicing.
To address this problem, the attention mechanism has been adopted by many existing models to predict future
outputs. However, most of these models use a single-domain attention which captures input dependency
structures only in the temporal domain. This limitation reduces their prediction accuracy in spatio-temporal
predictive learning, where understanding both spatial and temporal dependencies is essential. To tackle this
issue and enhance the prediction performance, we propose a novel crossover attention mechanism in this
paper. The crossover attention can be understood as a learnable regression kernel which prioritizes the input
sequence with both spatial and temporal similarities and extracts relevant information for generating the
output of future time slots. Simulation results and ablation studies based on synthetic and realistic datasets
show that the proposed crossover attention achieves considerable prediction accuracy improvement compared
to the conventional attention layers.

ABSTRACT

INDEX TERMS
Spatio-temporal, multivariate time series, traffic prediction, crossover attention, transformer model, deep learning.

I. INTRODUCTION

S

PATIO-TEMPORAL multivariate time series (STMTS)
are defined by their sequential order and spatio-temporal
dependencies, containing valuable information into the
dynamics of various systems and processes in communications and networking. Spatio-temporal predictive learning
seeks to generate future frames of STMTS by analyzing the available historical frames. The importance of
spatio-temporal predictive learning lies mainly in its ability
to analyze and model both the spatial correlations and temporal state transitions of the system dynamics. Analyzing and
modeling STMTS is a crucial aspect of data mining, providing essential insights and informing decisions across various
applications such as multiple-input multiple-output (MIMO)

channel prediction [1], [2], [3], mobile traffic analysis [4], [5],
network slicing [6], [7], and smart cities [8]. For instance,
accurate and timely mobile traffic prediction is needed for
the intelligent resource management in network slicing [9],
which could mitigate network congestion and improve the
quality of services (QoS). Meanwhile, channel prediction
can help solve the channel aging issue [1], reduce the pilot
overhead [3] and thereby enhance the system performance.
In spatio-temporal predictive learning, understanding both
the temporal and spatial dependencies is crucial for enhancing prediction accuracy. Conventional statistical techniques
like Historical Average (HA) and Auto-Regressive Integrated Moving Average (ARIMA) often perform poorly in
this task, as they were designed to capture only temporal

2025 The Authors. This work is licensed under a Creative Commons Attribution 4.0 License.
For more information, see https://creativecommons.org/licenses/by/4.0/
VOLUME 3, 2025

479

correlations [10]. Additionally, these traditional algorithms
inefficiently deal with the non-linear dynamics of time
series data. Fortunately, the remarkable advancements in
deep learning over the past decade have led researchers to
explore numerous data-driven approaches to tackle this challenge, enabling adaptive learning and the modeling of complex non-linear dependencies in spatio-temporal predictive
learning.
A. LITERATURE REVIEW

Initially, pioneering studies in communication and networking were conducted by exploring Convolutional Neural
Networks (CNNs) and Recurrent Neural Networks (RNNs)
to predict STMTS [2], [11], [12]. In practice, researchers
frequently integrate RNNs and CNNs as a hybrid network
to simultaneously learn patterns in data over time and space
domain [13]. This is because RNNs are good at capturing
temporal dependencies, while CNNs focus on identifying
spatial dependencies. It has been shown that such hybrid
architectures can efficiently capture the spatio-temporal
dynamics in time series forecasting. For example, the authors
in [14] demonstrated that a neural network with convolutional
long-short term memory (ConvLSTM) layers significantly
outperform conventional linear regression methods in the
spatio-temporal MIMO channel prediction problem. In [15],
the authors leveraged CNN and ConvLSTM to predict channel state information (CSI) in high-speed railway networks
and verified that the hybrid architecture outperformed the
classical CNN and RNN networks in terms of prediction
accuracy.
Besides CNNs, Graph Convolutional Networks (GCNs)
have recently attracted significant research interest in spatiotemporal forecasting. Unlike CNNs, GCNs are specifically
designed to better capture the spatial correlations of graphs
in non-Euclidean space. As a result, GCNs are considered as
better substitutions for the CNN modules in existing networks
to efficiently understand the spatial structure of data. For
example, the authors of [16] proposed to model mobile terminals as a time-evolving graph and used GCN to predict the
future mobile traffic data. Their experiments demonstrated
that the proposed GCN-based model outperformed CNNbased models across various prediction metrics. Likewise, the
authors of [17] demonstrated that a GCN backbone achieves
superior traffic flow prediction performance compared to
CNN backbones.
RNN models, such as LSTM, are widely recognized for
their limitations in handling long-range temporal dependencies [18]. To address this issue, Transformers based
on attention mechanisms have recently been proposed [7].
One of the key advantages of Transformers is their ability
to capture long-range dependencies and interactions [19].
This capability, stemming from the core attention mechanism within Transformers, is particularly beneficial for
time series modeling, leading to significant advancements
across various applications. For example, the authors in [20]
480

proposed spatio-temporal Transformer networks (STTN) for
traffic flow prediction, demonstrating significant improvements in prediction accuracy compared to ConvLSTM [21].
The authors in [6] employed the attention mechanism in
spatio-temporal cellular mobile traffic prediction, achieving a
higher prediction accuracy compared with RNN backbones.
The encoder-decoder Transformer has shown its advantages
in MIMO channel prediction [22], which can accurately predict future channels in parallel. In [23], the authors employed
a hybrid network including GCNs and attention mechanism
to predict cellular traffic. It has been shown therein that the
hybrid architecture effectively leverage the temporal dependencies of cellular traffic and spatial dependencies of the
physical network topology.
B. MOTIVATIONS AND CONTRIBUTIONS

The continuous development of spatio-temporal predictive
learning for time series has highlighted the essential role
of Transformers for the temporal module of hybrid network
architectures [24], [25]. The attention model, which forms
the foundation of Transformer models, has recently been
extensively investigated in time series forecasting [18]. Different variants such as Pyraformer [26], Informer [27], and
Reformer [28] primarily focus on reducing computational
complexity without compromising prediction performance.
Consequently, the vanilla attention model remains widely
used in many applications [6], [7], [21], [22], [23], [29],
[30], provided the sequence length is manageable. Despite its
common use for handling spatially and temporally correlated
data, the vanilla attention model was originally designed
as a learnable regression kernel based solely on temporal similarities [24], which potentially limits its capability
for spatio-temporal predictive learning. For this reason, the
existing approaches often integrate Tranformers models and
convolutional networks to jointly capture the spatio-temporal
correlations among data frames [7], [22], [31]. Based on this
consideration, we argue that addressing this issue can further
enhance its efficiency in predicting spatially and temporally
correlated data.
In this work, we propose a novel Crossover Attention (XOA) model for spatio-temporal predictive learning.
It functions as a learnable regression kernel that predicts values by simultaneously considering both spatial and
temporal similarities. This feature is particularly appealing for spatio-temporal predictive learning, as it prioritizes
input sequences with both spatial and temporal similarities, extracting relevant information for generating future
outputs. Our simulation results using synthesized and realworld datasets [8], [32] show that the proposed crossover
attention achieves around 1 dB gains on reducing the prediction errors when comparing to the vanilla attention and
outperforms recent reference schemes. The novelty of the
proposed crossover attention lies on the simple yet effective
modification of the vanilla attention mechanism. Extensive
ablation simulations verified that performance improvements
VOLUME 3, 2025

He et al.: Spatio-Temporal Predictive Learning Using Crossover Attention

are achieved by improving the attention mechanism itself
rather than employing more traditional attention layers. This
demonstrates the effectiveness of the proposed crossover
attention mechanism. To conclude, our contributions are
twofold:
• Enhanced Spatio-Temporal Predictive Learning: We
improved the attention model by learning a regression
kernel based on both temporal and spatial similarities,
which is crucial for applications like channel prediction,
traffic prediction, and more. To the best of our knowledge, our work is the first to introduce a spatial attention
layer which captures spatial correlations without relying
on convolutional networks. The proposed dual attention
layer allows the model to prioritize input sequences that
are similar in both dimensions, making it more effective
for spatio-temporal predictive learning.
• Simple but Effective Modification: The proposed
crossover attention is a straightforward modification of
the vanilla attention model, making it easy to implement
while significantly enhancing performance. This simplicity ensures that it can be readily adopted in various
existing frameworks.

FIGURE 1. Hourly cellular traffic pattern in two weeks of the

(50, 50)-th cell in Milan, Italy.

II. PRELIMINARIES
A. SPATIO-TEMPORAL PREDICTIVE LEARNING

Let Z1:T = {zt }Tt=1 ∈ RT ×Dz be a multivariate time series,
where each vector z t = [zt,1 , . . . , zt,i , . . . , zt,Dz ] ∈ RDz
represents the variables observed at time t, and Zt1 :t2 ∈
R(t2 −t1 +1)×Dz represents all values within the time slice t ∈
[t1 , t2 ]. This time series exhibits both temporal and spatial correlations. It may be associated with an independent
sequence of covariates, denoted by X1:T = {xt }Tt=1 ∈ RT ×Dx ,
where each vector xt ∈ RDx can contains both dynamic and
static domain-specific features.
The goal of spatio-temporal predictive learning is to learn
the prediction model
Zt+1:t+h ∼ p(Zt+1:t+h |Zt−w+1:t , Xt−w+1:t+h ; θ ),

(1)

where w represents the maximum length of the moving
history window, h represents the prediction horizon, and
θ represents the parameters of the model. This model is
then employed to predict the future h steps targets Zt+1:t+h
based on a moving window of past w steps observations and
the corresponding covariates. In particular, in the absence
of covariates, (1) simplifies to an auto-regressive prediction
model. Additionally, one might want to learn a mapping
from input features to the parameters of the prediction model
as
θ = 9 (Z1:t , X1:t+h ; ω ) ,

(2)

where 9 (·; ω ) is typically a neural network parameterized
by a set of learning parameters ω , such as weights and bias.
It is worth noting that 9 (·; ω ) is often used to learn the
dependency structure among the time series.
VOLUME 3, 2025

FIGURE 2. Heat map of the internet activities in in Milan, Italy.

B. SPATIO-TEMPORAL DYNAMICS

In practical applications of spatio-temporal predictive learning, the time series frequently exhibits spatial and temporal
correlations. Generally, these spatio-temporal dependencies
should be leveraged to enhance the prediction accuracy.
To illustrate this, we refer to Fig. 1 and Fig. 2, which demonstrate the spatio-temporal effects of cellular traffic data in
Milan. This data is sourced from a public dataset released
by Italia Telecom [32]. The city is partitioned into a grid of
100 × 100 cells, each measuring 235 × 235 square meters.
A period of 62 days of communication record details (CDRs)
was gathered within this area. The original CDRs, aggregated
at 10-minute intervals, were resampled at an hourly interval
for this demonstration.
Fig. 1 presents the hourly aggregated traffic data for a specific cell within the city for the first two weeks of November
2013. It is evident that the traffic data follows a distinct
seasonal pattern, demonstrating the temporal correlation of
the time series. The daily or weekly traffic for a particular
cell is correlated and varies in a similar manner. Additionally,
Fig. 2 displays a city-wide heatmap of internet activities.
481

It can be observed that the cellular traffic data collected at
neighboring cells varies according to their spatial distribution
and traffic data collected within the same zone may exhibit
similar variations over time, indicating the spatial correlation
of the time series.
C. ATTENTION MECHANISM

The attention mechanism, initially introduced for machine
translation in [33], has become a fundamental concept in
the deep learning literature. It is designed to capture the
long-range dependency structures of the input sequence. The
attention mechanism operates as a query-key-value model
and typically employs scaled dot-product to calculate the
temporal similarities between queries and keys [24]. The
outcome is the normalized weighted sum of the training
values. The general form of the traditional temporal attention
mechanism can be mathematically expressed as



QKT
V, (3)
A (Q, K, V) = softmax Mt + √
Dk
where Q ∈ RN ×Dk , K ∈ RM ×Dk , V ∈ RM ×Dv represent queries and training key-value pairs with lengths of N
and M , respectively. In addition, Mt ∈ RN ×M denotes the
temporal causality mask for masking out similarities that
include future frames, which is achieved by adding −∞ to the
corresponding components. The symbol (·)T represents the
matrix transpose, and the softmax (·) function computes
the normalized weights on the last axis of the input tensor.
The attention mechanism has been widely used in various
spatio-temporal predictive learning tasks, including cellular
traffic prediction [1], [2] and MIMO channel prediction [6],
[7]. Recent research has adequately confirmed the effectiveness of the attention mechanism in these domains.

In the setting of spatio-temporal predictive learning as
outlined in (1), it is appropriate to view key-value pairs as historical covariate-target (features-label) pairs, i.e., (K, V) ≜
(X1:t , Z1:t ). Additionally, queries can be viewed as future
h-step covariates, that is, Q ≜ Xt+1:t+h . The training space
contains all observed key-value pairs D = {(ki , vi )}M
i=1 ,
and (4) forecasts the targets by projecting each q in D using
the similarity kernel σ (q, k).
In the attention mechanism defined in (3), the scaled
dot-product similarity between vectors is utilized as the similarity kernel, which is
!
qi kTj

σ qi , kj = softmax √
.
(5)
Dk
This similarity kernel generates the sample cross-covariance
matrix C = QKT ∈ RN ×M between Q and K, where
the (n, m)-th element Cn,m = Cov(qn , km ) denotes the
covariance between the n-th query and the m-th key in D.
Consequently, the resulting attention is computed in the
temporal domain. In particular, the sample temporal correlation coefficients are explicitly computed in the self-attention
A (Z, Z, Z). Therefore, we refer to A(Q, K, V) as the temporal attention querying by temporal correlations.
B. QUERYING BY SPATIAL CORRELATIONS

Motivated by the preceding analysis, it is suitable to factorize
queries and key-value pairs as the spatial view of Q =
Dk
Dv
k
N ×1 ,
{q̄i }D
i=1 , K = {k̄i }i=1 and V = {v̄i }i=1 , where q̄i ∈ R
k̄i ∈ RM ×1 and v̄i ∈ RM ×1 are the corresponding temporal
vectors. In this case, the regression model can be adjusted as
si =

Dk
X


σ v̄i , k̄j q̄i ,

∀i = 1, 2, . . . , Dv

(6)

j=1

III. THE PROPOSED CROSSOVER ATTENTION
MECHANISM

Although the attention mechanism has achieved significant success in spatio-temporal predictive learning, it is not
designed for efficiently utilizing cross-domain correlations.
In this section, we present the proposed direct yet effective
variant to augment the capabilities of attention models in
spatio-temporal predictive learning.
A. QUERYING BY TEMPORAL CORRELATIONS

The vanilla attention mechanism, as outlined in (3), can be
viewed as a realization of the Naradaya-Watson regression
model [24]. Let us denote the temporal view of queries,
M
keys, and values as Q = {qi }N
i=1 , K = {ki }i=1 , and
M
1×D
1×D
k, k ∈ R
k , and v ∈
V = {vi }i=1 , where qi ∈ R
i
i
R1×Dv are the corresponding spatial vectors. Consequently,
the Naradaya-Watson regression model can be expressed as
XM

σ qi , kj vj , ∀i = 1, 2, . . . , N
ai =
(4)
j=1

where σ (·) denotes a scalar similarity kernel.
482

with a scalar similarity kernel being the scaled dot-product
!
k̄Tj v̄i

σ v̄i , k̄j = softmax √
.
(7)
M
When implementing this regression model as a differentiable
neural network layer, it can be expressed as



KT V
S (Q, K, V) = Q softmax Ms + √
, (8)
M
Now it is evident that the similarity kernel in (8) is computed
in the spatial domain, and we employ an optional spatial mask
Ms for masking out unavailable components in the spatial
similarity matrix. These unavailable components are typically caused by malfunctioning sensors and can be masked
out by adding −∞ before the softmax operation. After the
masking, each row of the spatial similarity matrix is normalized using the softmax activation function. This similarity
kernel simply generates the sample cross-covariance matrix
G = KT V ∈ RDk ×Dv between K and V, in which the
(k, v)-th element Ck,v = Cov(k̄k , v̄v ) denotes the covariance
VOLUME 3, 2025

He et al.: Spatio-Temporal Predictive Learning Using Crossover Attention

and spatial dependencies. As will be shown in the simulation results, the introduced crossover attention outperforms
the standard attention mechanism, yielding significantly
improved prediction results across diverse applications and
datasets.
D. COMPLEXITY ANALYSIS

FIGURE 3. Computation graph of the proposed crossover

attention mechanism.

between the k-th spatial position of keys and the v-th spatial position of values in D. Specifically, the sample spatial
correlation coefficients are explicitly calculated in the selfattention S (Z, Z, Z). Therefore, we refer to S(Q, K, V) as
the spatial attention querying by spatial correlations.
C. CROSSOVER ATTENTION

In the implementation of a neural network, the results of
querying are determined by the similarity kernel σ (·), and the
kernel is learned implicitly through the projections Q = IWq ,
K = IWk and V = IWv , where I represents the input to the
network layer, and Wq , Wk and Wv are learnable projection
matrices. To fully utilize the spatio-temporal dependency of
the input sequence, the results of querying from the temporal attention and the proposed spatial attention should be
integrated. With this consideration in mind, we design the
crossover attention as


XOA (Q, K, V) = A (Q, K, V) , S (Q, K, V) WO , (9)
where WO ∈ R2Dv ×Dv is utilized to integrate the attention
values computed by temporal and spatial correlations. In general, (9) can be viewed as a component-wise weighted summation of the attention matrices A(Q, K, V ) and S(Q, K, V )
with the weights controlled by the learnable weight matrix
W O . The structure of the network implementation of the
proposed crossover attention is illustrated in Fig. 3. It is
important to note that a mask layer is optional before the
softmax operation if there are some entries that should
be masked out for, e.g., computation purpose. The intuition
behind the crossover attention design is rather simple: the
integration of the cross-domain attentions could help the
neural network to learn a more powerful and expressive
regression kernel σ (·) which jointly considers the temporal
VOLUME 3, 2025

Analyzing the computational complexity of crossover attention is straightforward. The complexity for the crossover
attention described in (9) is influenced by both temporal and
spatial attentions. For the temporal attention in (3), it involves
matrix multiplication between an N × Dk matrix and a Dk ×
M matrix, followed by multiplying the resulting N × M
matrix by an M × Dv matrix. Thus, the complexity of (3) is
generally O (NM (Dk + Dv )). Specifically,
for self-attention

A (Z1:t , Z1:t , Z1:t ), it is O T 2 Dz . Similarly, the spatial
attention in (8) has a complexity of O (Dk Dv (N + M )),

and for self-attention S (Z1:t , Z1:t , Z1:t ), it is O TD2z .
Therefore, the total complexity of the proposed crossover

attention is O Dk Dv (N + M ) + NM (Dk + Dv ) + 2ND2v ,
and for self-crossover-attention
XOA (Z1:t , Z1:t , Z1:t ), it is

O T 2 Dz + 2TD2z ) . For a fixed Dz , it is clear while the
computational complexity of the proposed crossover attention is slightly higher than that of traditional attention,
it still operates in quadratic time, similar to traditional
attention.
Additionally, crossover attention uses the same set of
queries, keys, and values for both temporal and spatial
attention sub-modules, making it easy to replace the vanilla
attention layer with the crossover attention layer. Since the
temporal and spatial attentions share the same Q, K, and V ,
the number of learnable parameters in the proposed crossover
attention consists only of the weights W q , W k , W v and W O .
For self-attention, we have Dk = Dv = Dz , resulting in
W q , W k , W v ∈ RDz ×Dz and W O ∈ R2Dz ×Dz . Consequently,
the number of parameters in the proposed crossover attention
is 5D2z , whereas the number of parameters in traditional attention is 3D2z .
IV. THE PROPOSED XOATRAN ARCHITECTURE

In this section, we introduce a decoder-only Transformer
architecture, namely XOATrans, which is constructed based
on the proposed crossover attention.
A. MULTI-HEAD CROSSOVER ATTENTION

In practice, transformer models often use multi-head attention
mechanism instead of full (single-head) attention [34]. This
approach allows the model to jointly attend to information
from different representation subspaces at various positions,
enhancing the network’s expressive power and modeling
capabilities. Therefore, we adopt the multi-head pattern for
our proposed crossover attention in this paper, and the mathematical model can be expressed as


MHXOA(Q, K, V) = h1 , h2 , . . . , hH WM ,

(10)
483

attention layer will be processed by the Add&Norm operation
given by,
Add&Norm(I, P) = Norm(I + P),

(12)

where I is the input of this layer, P is the input of previous
layer and Norm(·) denotes the layer normalization operation [34]. The Add&Norm operation is actually a normalized
residual connection which adds the original input to the
output of a deeper layer. Residual connections are crucial
for the Transformer model architecture. Because they enable
effective handling of very deep networks and mitigate the
vanishing gradient problem [36]. For the feed-forward network, it can be described as
FFN(I) = max (0, IW1 + B1 ) W2 + B2 .

The FFN(·) layer is essentially a two-layer perceptron with
Rectified Linear Unit (ReLU) activation function and W1 ,
W1 , B1 and B1 being the learnable weights and bias with
appropriate shapes. Hence, the output of the decoder block
can be described as

FIGURE 4. Network architecture of XOATran.

O1 = Add&Norm(I, MHXOA(I, I, I)),
O2 = FFN(O1 ),
O3 = Add&Norm(O1 , O2 ).

where H denotes the total number of heads and each head hi
is given
Q

V
hi = XOA(QWi , KWK
i , VWi ),

(11)

Q

Dk ×dk , WV ∈ RDv ×dv and
where Wi ∈ RDk ×dk , WK
i
i ∈ R
M
Hd
×D
v
v
W ∈R
are parameter matrices for the projections.
We denote dk = Dk /H , dv = Dv /H as the dimensionality of each subspace. Because each head operates on a
reduced dimension, the overall computational cost remains
similar to that of single-head crossover attention with full
dimensionality.

The Transformer model was initially proposed with an
encoder-decoder architecture [34]. However, recent designs
of Transformers have favored a decoder-only paradigm,
especially for large language models (LLMs) [35], [36].
Following this best practice and simplifying the architecture, we adopt the decoder-only paradigm for our proposed
XOATran.
As shown in Fig. 4, the XOATran comprises a positional
encoding layer, L decoder blocks, and an output layer for
generating the output with expected shape. Unlike RNNs
and CNNs, attention layers lack recurrent states and convolutions, potentially losing relative or absolute positional
information during forward passes. To maintain the sequential order, we use a fixed positional encoding similar to [34].
The encoded positional information is added to the input,
which is then processed by L decoder blocks. Each decoder
block includes a masked multi-head crossover attention layer
and a feed-forward network. It should be noted that the
output of the decoder blocks will retain the same shape as the
input. Following the forward pass, the output of the crossover

(14)
(15)
(16)

This process will repeat for L blocks, and the output of the last
block will be processed by a CNN layer and/or linear layer
to produce the final prediction, depending on the specific
application.
C. TRAINING

In this paper, we adopt a supervising learning approach to
train the proposed XOATran. Let the final output of the whole
network be denoted as
b
Zt+1:t+h = XOATrans(Zt−w+1:t ),

B. MODEL ARCHITECTURE

484

(13)

(17)

where Zt−w+1:t is the input sequence with a window length
of w, b
Zt+1:t+h is the h-step prediction of the ground truth
Zt+1:t+h . Then, we compute the loss as
1
∥XOATrans(Zt−w+1:t ) − Zt+1:t+h ∥2 ,
T
1 b
2
=
Zt+1:t+h − Zt+1:t+h ,
T

L(D) =

(18)
(19)

t +T

0
where D = {Zt−w+1:t , Zt+1:t+h }t=t
is a dataset of T training
0
pairs. The loss function is the mean squared error (MSE)
on the training dataset. We employ the PyTorch framework
and the Adam stochastic optimizer [37] to implement and
train the model.

V. PERFORMANCE EVALUATION

In this section, we present numerical results to verify the
effectiveness of the proposed crossover attention in two
spatio-temporal predictive learning applications: (i) MIMO
channel prediction and (ii) traffic prediction. We also conduct
ablation studies by replacing the attention layers inside of
VOLUME 3, 2025

He et al.: Spatio-Temporal Predictive Learning Using Crossover Attention

recent developed Transformers with our proposed crossover
attention, simplifying the performance comparison.
We adopt several metrics for evaluating the prediction
accuracy of each model, including mean absolute error
(MAE), mean absolute percentage error (MAPE), mean
square error (MSE), normalized root mean square errors
(NRMSE), normalized mean squared error (NMSE) and
R-squared coefficient of determination (R2 ). Note that R2 provides information about the goodness of a fitting model, and
its value normally varies within [0, 1] with 1 indicating the
perfect fitting.
In general, all hyper-parameters should be determined
based on our available computing resources. While scaling
up the model may enhance the network’s learning capacity,
it can also complicate the training process. Considering these
factors, we first establish ranges for all hyper-parameters
based on our available computing resources. We then empirically select appropriate values within these ranges, guided
by training performance and convergence speed. Notably, for
ablation simulations, we follow the same values as specified
by the original methods, if applicable.
A. MIMO CHANNEL PREDICTION

One important application of spatio-temporal predictive
learning in 5G/6G communications systems is the channel
prediction. Predicting CSI from the historical observed CSI
could help mitigate the channel aging issue and reduce unnecessary pilot overheads. In this case, we perform simulations
for MIMO channel prediction by following a similar problem
settings as in [3]. Before showing the simulation results,
we will briefly introduce the environment setup.
1) ENVIRONMENT SETUP

We perform simulations based on the downlink of a massive
multiuser MISO (MU-MISO) system, where a base station
(BS) serves Nu single-antenna users. The system operates
in time division duplexing (TDD) mode, and the BS has
a limited transmit power Ptot , Nt transmit antennas and
Nf (0 < Nf ≪ Nt ) RF chains. Initially, the users are
randomly located within the coverage area of the BS and
are assumed to move with constant velocities. Additionally,
the channels between the BS and users are time-varying.
On the downlink transmission, the CSI acquisition is accomplished via uplink pilot-assisted channel measurement, and
multi-user precoding is then adopted to mitigate inter-user
interference. The pilot overhead could be prohibitive with
limited RF chains in the system. To tackle this issue, one
feasible approach is to estimate only partial CSI at each
frame and employ channel prediction to recover the full CSI
from the historical incomplete observations [38]. Then, the
predicted full CSI will be used for selecting antennas for
downlink transmission [3], [39]. Due to the Doppler effect
and spatially dependent antenna patterns, real propagation
environments often exhibit temporal and spatial correlations [40], which can be leveraged to predict future channel
VOLUME 3, 2025

states. Because only partial CSIs are available in the history
windows, this problem is regarded as a partially observable Markov process (POMDP) which is much challenging
than the prediction problems with fully observable channel
states [14].
Due to the lack of real data set for this use case, we simulate
the propagation environment following the same configuration as in [3], [38], which models the channel evolution by a
Gaussian-Markov process with the Jakes’ model [41], [42],
given by
h k,t = ζk h k,t−1 +

q
1 − ζk21 t ,

(20)

where ζk ∈ [0, 1] represents the temporal correlation coefficient for user k, and 1 t ∼ CN (0, 6 ) is the innovative
complex Gaussian i.i.d. in time. The spatially correlated
channel vector 1 t follows the Kronecker model [43], and
we denote α ∈ [0, 1] as the spatial correlation coefficient
at BS. The value of ζk is determined by the maximum
Doppler frequency and is inversely proportional to the terminal speed [41], in which ζk = 1 represents a static channel and
ζk = 0 implies that the channel is i.i.d. over time. The fading
correlation coefficient
can be obtained from Jakes’ model

given by ζk = J0 2π vCk fc T , where J0 (·) denotes the zeroth
order Bessel function of the first kind, vk is the speed of user
k, C is the speed of light, and T is the frame duration [44].
It should be noted that although an explicit spatio-temporally
correlated channel model is adopted here, the algorithm does
not have any prior knowledge of the spatio-temporal correlation model. Hence, the prediction algorithm can be applied to
any spatio-temporal time series in real-world datasets, as will
be verified in Sec. V-B.
In the simulations, the BS is equipped with Nt = 32 antennas and Nf = 16 RF chains, and Ptot = 100 watt. The
number of users Nu = 4, and we adopt a uniform range
of speeds from 3.6 km/h to 72 km/h for all users, and the
spatial correlation coefficient α = 0.3. To train and test the
model, the data set is randomly generated with the POMDP
introduced in [3], [38]. The process starts by initially selecting an optimal subset of antennas for estimating partial CSI.
Subsequently, the full CSI is reconstructed using historical
partial estimations. Furthermore, the reconstructed full CSI
is used to select antennas for the next frame and the process
is repeated. With the POMDP involving, we store at most
1, 000, 000 time steps of partial CSIs in a ring buffer, and
the stored data is partitioned into a training set and a test set
with a ratio of 9 : 1. We train the model by using the generated
partial CSIs from the training dataset and use the ground-truth
CSIs from the same dataset to compute the training losses and
update the model’s parameters. After updating the parameters
at each epoch, we evaluate the model’s prediction accuracy
using the testing dataset. The number of decoder blocks is
L = 4, the length of the history window is w = 24, and
we set the prediction horizon as h = 1 since the interactive
process only needs to predict one-step targets.
485

FIGURE 5. NMSE testing results versus training epoch.

FIGURE 6. Sum-spectral efficiency testing results versus training

epoch.

To verify the effectiveness of proposed crossover attention mechanism, we perform simulations over the following
models,
• XOATran: The proposed crossover attention enabled
Transformer introduced in this paper.
• Transformer: The widely adopted decoder-only Transformer model with conventional attention mechanism.
In particular, this model is constructed by substituting the crossover attention layer of XOATran with the
vanilla attention layer.
• JCPAS: The joint channel prediction and antenna selection framework introduced in [3], where the probabilistic
prediction networks is based on convolutional network
with 24 layers and residual connections. It should be
noted that JCPAS is designed to output probabilistic
results, and we adjust it to output deterministic results
for the ease of comparison.
2) NUMERICAL RESULTS

Note that for every epoch we test these models on the same
test set, and Figs. 5- 6 illustrates the rolling testing results
during the training. Specifically, fig. 5 illustrates the NMSE
of prediction results during the training process of the aforementioned models. From Fig. 5, we can observe that all
three models are effective in predicting the full CSI from
the history of incomplete observations. Additionally, we can
see that Transformer model performs better than the JCPAS
using CNNs, as the CNNs struggle to capture the long-range
temporal dependencies among the input sequence. Moreover,
we can conclude from the figure that the proposed XOATrans
outperforms the two reference models. Specifically, XOATrans achieves a gain of about 1 dB and 2.5 dB compared
to Transformer and JCPAS, respectively. This confirms the
effectiveness of the proposed crossover attention in capturing
both the temporal and spatial structure of the input sequence.
Fig. 6 presents the tested sum-spectral efficiency of the
aforementioned models. In this figure, the sum-spectral efficiency is computed using the selected antennas, which are
chosen based on the predicted full CSI as in [3]. It should
486

be noted that the sum-spectral efficiency can be maximized
by selecting the best subset of antennas, and we adopted
the norm-based antenna selection algorithm for this purpose.
Therefore, accurate channel prediction will eventually result
in higher sum-spectral efficiency. From this perspective,
we can conclude from this figure that the proposed XOATrans
outperforms Transformer and JCPAS. This is because XOATrans not only achieves the lowest NMSE but also preserves
the ordering information of the norms of channel vectors,
which ultimately helps the algorithm to select a better subset
of antennas compared to the other two models. While NMSE
directly measures the prediction accuracy, the sum-spectral
efficiency of antenna selection is presented as an indirect
proxy measurement of the prediction accuracy in Fig. 6.
Therefore, the degree of sum-spectral efficiency gain may
appear to be less significant than the NMSE gain. However,
we can find from the figure that our proposed XOATrans
converges much faster than Transformer, which uses roughly
30% fewer epochs. These findings further verified the effectiveness of the proposed crossover attention.
B. TRAFFIC PREDICTION

In this section, we verify the effectiveness of the proposed
crossover attention using two real-world datasets for traffic prediction. Traffic prediction is an important application
of spatio-temporal predictive learning. Accurate and timely
prediction of the traffics allows more efficient resources
allocation and management. Before introducing the results,
we will first briefly describe the datasets used in the
simulations.
• Milan dataset [32]: As shown in Fig. 1, this dataset
comprises 62 days of cellular mobile traffic data for the
city of Milan, Italy. In this dataset, the entire city area is
divided into 100 × 100 square cells, with cellular traffic
data resampled at an hourly granularity. In the experiments, we focus on predicting the number of call-ins for
the selected 20 × 20 cells within this dataset under the
same settings in [6].
VOLUME 3, 2025

He et al.: Spatio-Temporal Predictive Learning Using Crossover Attention

•

SanDiego dataset [8]: Compared to the Milan dataset,
this dataset is significantly larger and is a subset of the
LargeST benchmark dataset. It includes road traffic data
for over 17,000 road segments and 700 sensors in the
area around San Diego, USA. The data is recorded at
5-minute intervals over five years, from 2017 to 2021.
In our experiments, we focus on predicting the traffic
volumes for all sensors within this dataset.

TABLE 1. Performance comparisons for the Milan dataset.

1) COMPETING ALGORITHMS

We conduct ablation experiments by replacing the attention
modules in two existing Transformers: (i) ST-Tran-TTB and
(ii) STTN. The details of these Transformers can be found
in [6], [8], and [20]. For the reader’s convenience, we list
below the abbreviations of the competing algorithms or neural networks:
• HA: The Historical Average (HA) algorithm, which
takes the average of its history as the prediction result.
• HL: The Historical Last (HL) algorithm, which simply
uses the last observation as the future prediction.
• ARIMA: The well-known Autoregressive Integrated
Moving Average (ARIMA) algorithm, implemented
using the statsmodels Python library.
• LSTM : The long-short term memory (LSTM) neural
network for time-series forecasting [12].
• ConvLSTM : The convolutional LSTM proposed for
STMTS forecasting in [21].
• STDenseNet: STDenseNet [11], a prediction model
that learns spatio-temporal dependency structures using
densely connected CNNs.
• DCRNN : The diffusion convolutional recurrent neural
network (DCRNN) proposed in [45].
• AGCRN : The adaptive graph convolutional recurrent
network (AGCRN) proposed in [46].
• STGCN : The spatio-temporal graph convolutional networks proposed in [47].
• ST-Tran-TTB: ST-Tran, an encoder-decoder Transformer designed for STMTS forecasting with a temporal
transformer block (TTB) [6].
• STTN : The spatio-temporal Transformer networks
(STTN) for spatio-temporal traffic forecasting [20],
which integrate GCNs alongside the attention
mechanism.
• ST-Tran-XOA: Our modified version of ST-Tran, where
the attention layers are replaced by our proposed
crossover attention layers.
• STTN-XOA: Our modified version of STTN, where the
attention layers are replaced by our proposed crossover
attention layers.
Note that ST-Tran-XOA and STTN-XOA are tested using
the same random seeds, hyper-parameters, instructions, and
datasets as described in the original papers. This approach
allows us to present a clear and straightforward performance
comparison to demonstrate the effectiveness of the proposed
crossover attention mechanism.
VOLUME 3, 2025

FIGURE 7. The fitness curve of ST-Tran-XOA for the cellular traffic

flows in Milan.

2) NUMERICAL RESULT AND DISCUSSION

Table 1 summarizes the prediction performance comparisons
of the competing models for the Milan dataset. From this
table, we can observe that our proposed crossover attention
mechanism achieves the best prediction accuracy in terms of
MAE, NRMSE, and R2 . Notably, ST-Tran-XOA attains the
highest R2 score among the seven competing models, indicating that it learns the most fitting model for the spatio-temporal
cellular traffic data in the Milan dataset. By comparing
ST-Tran-XOA with ST-Tran-TTB, we can conclude that the
proposed crossover attention mechanism helps the model
exploit the spatio-temporal dependencies of the data, resulting in lower prediction errors. In addition to the numerical
results presented in Table 1, we also depict the predicted
results in Fig. 7 to illustrate the model fitness of ST-TranXOA. As shown in the figure, ST-Tran-XOA can accurately
and smoothly predict the trends and values of future mobile
traffic data for a specific cell within the city area, clearly verifying the effectiveness of the proposed crossover attention
mechanism.
In addition to the Milan dataset, Table 2 presents the
prediction results of the aforementioned models for the
SanDiego dataset. From this table, we can see that our
proposed crossover attention mechanism outperforms the
competing models in terms of prediction errors. Specifically,
STTN-XOA achieves the lowest prediction errors among the
487

TABLE 2. Performance comparisons for the SanDiego dataset.

seven competing models for prediction horizons from 3 to
12. This demonstrates that the proposed crossover attention
mechanism is also effective in multi-step prediction tasks.
By comparing STTN-XOA with STTN, we can conclude that
the model’s capability of capturing spatio-temporal dependencies is significantly enhanced by the proposed crossover
attention. These results further validate the effectiveness of
the proposed crossover attention.
VI. CONCLUSION

In this paper, we investigated the spatio-temporal predictive
learning problem, focusing on predicting spatially and temporally correlated time series such as channel states and traffic
flows. To efficiently exploit the spatio-temporal correlations,
we designed a simple yet effective crossover attention mechanism to help the network understand the spatio-temporal
patterns of input data. Experimental results on two popular applications of channel and network traffic predictions
using both synthetic and realistic datasets clearly verified the
effectiveness of our proposed crossover attention. Since the
proposed crossover attention can be seamlessly integrated
into existing models, we believe it offers an attractive method
for enhancing the prediction performance of the existing
predictive models.
ACKNOWLEDGMENT

For the purpose of open access, and in fulfilment of the
obligations arising from the grant agreement, the authors have
applied a Creative Commons Attribution 4.0 (CC BY 4.0)
license to any Author Accepted Manuscript version arising
from this submission.
REFERENCES
[1] C. Wu, X. Yi, Y. Zhu, W. Wang, L. You, and X. Gao, ‘‘Channel
prediction in high-mobility massive MIMO: From spatio-temporal autoregression to deep learning,’’ IEEE J. Sel. Areas Commun., vol. 39, no. 7,
pp. 1915–1930, Jul. 2021.
[2] M. K. Shehzad, L. Rose, S. Wesemann, and M. Assaad, ‘‘MLbased massive MIMO channel prediction: Does it work on real-world
data?’’ IEEE Wireless Commun. Lett., vol. 11, no. 4, pp. 811–815,
Apr. 2022.
[3] K. He, T. X. Vu, D. T. Hoang, D. N. Nguyen, S. Chatzinotas, and
B. Ottersten, ‘‘Risk-aware antenna selection for multiuser massive MIMO
under incomplete CSI,’’ IEEE Trans. Wireless Commun., vol. 23, no. 9,
pp. 11001–11014, Sep. 2024.
488

[4] S. Mehrizi and S. Chatzinotas, ‘‘Network traffic modeling and prediction using graph Gaussian processes,’’ IEEE Access, vol. 10,
pp. 132644–132655, 2022.
[5] D. Cai, P. Fan, Q. Zou, Y. Xu, Z. Ding, and Z. Liu, ‘‘Active device detection
and performance analysis of massive non-orthogonal transmissions in
cellular Internet of Things,’’ Sci. China Inf. Sci., vol. 65, no. 8, Aug. 2022,
Art. no. 182301.
[6] Q. Liu, J. Li, and Z. Lu, ‘‘ST-TRAN: Spatial–temporal transformer
for cellular traffic prediction,’’ IEEE Commun. Lett., vol. 25, no. 10,
pp. 3325–3329, Oct. 2021.
[7] X. Wang et al., ‘‘A survey on deep learning for cellular traffic prediction,’’
Intell. Comput., vol. 3, p. 54, Jan. 2024.
[8] X. Liu et al., ‘‘LargeST: A benchmark dataset for large-scale traffic forecasting,’’ in Proc. NeurIPS, 2023, pp. 1–18.
[9] F. Chiariotti, M. Drago, P. Testolina, M. Lecci, A. Zanella, and M. Zorzi,
‘‘Temporal characterization and prediction of VR traffic: A network slicing
use case,’’ IEEE Trans. Mobile Comput., vol. 23, no. 5, pp. 3890–3908,
May 2024.
[10] S. Siami-Namini, N. Tavakoli, and A. S. Namin, ‘‘A comparison of ARIMA
and LSTM in forecasting time series,’’ in Proc. 17th IEEE Int. Conf.
Mach. Learn. Appl. (ICMLA), Dec. 2018, pp. 1394–1401.
[11] C. Zhang, H. Zhang, D. Yuan, and M. Zhang, ‘‘Citywide cellular traffic
prediction based on densely connected convolutional neural networks,’’
IEEE Commun. Lett., vol. 22, no. 8, pp. 1656–1659, Aug. 2018.
[12] C. Qiu, Y. Zhang, Z. Feng, P. Zhang, and S. Cui, ‘‘Spatio-temporal wireless
traffic prediction with recurrent neural network,’’ IEEE Wireless Commun.
Lett., vol. 7, no. 4, pp. 554–557, Aug. 2018.
[13] C. Tan et al., ‘‘Temporal attention unit: Towards efficient spatiotemporal predictive learning,’’ in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2023, pp. 18770–18782.
[14] G. Liu, Z. Hu, L. Wang, J. Xue, H. Yin, and D. Gesbert, ‘‘Spatio-temporal
neural network for channel prediction in massive MIMO-OFDM systems,’’
IEEE Trans. Commun., vol. 70, no. 12, pp. 8003–8016, Dec. 2022.
[15] T. Zhou, H. Zhang, B. Ai, C. Xue, and L. Liu, ‘‘Deep-learning-based
spatial–temporal channel prediction for smart high-speed railway communication networks,’’ IEEE Trans. Wireless Commun., vol. 21, no. 7,
pp. 5333–5345, Jul. 2022.
[16] F. Sun et al., ‘‘Mobile data traffic prediction by exploiting time-evolving
user mobility patterns,’’ IEEE Trans. Mobile Comput., vol. 21, no. 12,
pp. 4456–4470, Dec. 2022.
[17] T. Qi, G. Li, L. Chen, and Y. Xue, ‘‘ADGCN: An asynchronous dilation
graph convolutional network for traffic flow prediction,’’ IEEE Internet
Things J., vol. 9, no. 5, pp. 4001–4014, Mar. 2022.
[18] Z. Chen, M. Ma, T. Li, H. Wang, and C. Li, ‘‘Long sequence time-series
forecasting with deep learning: A survey,’’ Inf. Fusion, vol. 97, Sep. 2023,
Art. no. 101819.
[19] Q. Wen et al., ‘‘Transformers in time series: A survey,’’ in Proc. 32nd Int.
Joint Conf. Artif. Intell., Aug. 2023, pp. 6778–6786.
[20] M. Xu et al., ‘‘Spatial-temporal transformer networks for traffic flow
forecasting,’’ 2020, arXiv:2001.02908.
[21] X. Shi, Z. Chen, H. Wang, D. Yeung, W. Wong, and W. Woo, ‘‘Convolutional LSTM network: A machine learning approach for precipitation
nowcasting,’’ in Proc. NIPS, 2015, pp. 802–810.
[22] H. Jiang, M. Cui, D. W. K. Ng, and L. Dai, ‘‘Accurate channel prediction
based on transformer: Making mobility negligible,’’ IEEE J. Sel. Areas
Commun., vol. 40, no. 9, pp. 2717–2732, Sep. 2022.
VOLUME 3, 2025

He et al.: Spatio-Temporal Predictive Learning Using Crossover Attention

[23] Z. Wang, J. Hu, G. Min, Z. Zhao, Z. Chang, and Z. Wang, ‘‘Spatial–
temporal cellular traffic prediction for 5G and beyond: A graph neural
networks-based approach,’’ IEEE Trans. Ind. Informat., vol. 19, no. 4,
pp. 5722–5731, Apr. 2023.
[24] S. Chaudhari, V. Mithal, G. Polatkan, and R. Ramanath, ‘‘An attentive
survey of attention models,’’ ACM Trans. Intell. Syst. Technol., vol. 12,
no. 5, pp. 1–32, Oct. 2021.
[25] S. Ahmed, I. E. Nielsen, A. Tripathi, S. Siddiqui, R. P. Ramachandran, and G. Rasool, ‘‘Transformers in time-series analysis: A tutorial,’’ Circuits, Syst., Signal Process., vol. 42, no. 12, pp. 7433–7466,
Dec. 2023.
[26] S. Liu et al., ‘‘Pyraformer: Low-complexity pyramidal attention for longrange time series modeling and forecasting,’’ in Proc. Int. Conf. Learn.
Represent., 2021, pp. 1–20.
[27] H. Zhou et al., ‘‘Informer: Beyond efficient transformer for long sequence
time-series forecasting,’’ in Proc. AAAI Conf. Artif. Intell., May 2021,
vol. 35, no. 12, pp. 11106–11115.
[28] N. Kitaev, Ł. Kaiser, and A. Levskaya, ‘‘Reformer: The efficient transformer,’’ 2020, arXiv:2001.04451.
[29] A. Das, W. Kong, R. Sen, and Y. Zhou, ‘‘A decoder-only
foundation model for time-series forecasting,’’ 2023, arXiv:2310.
10688.
[30] S. Zheng, C. Shen, and X. Chen, ‘‘Design and analysis of
uplink and downlink communications for federated learning,’’
IEEE J. Sel. Areas Commun., vol. 39, no. 7, pp. 2150–2167,
Jul. 2021.
[31] R. Kumar, J. Mendes-Moreira, and J. Chandra, ‘‘Spatio-temporal parallel
transformer based model for traffic prediction,’’ ACM Trans. Knowl. Discovery Data, vol. 18, no. 9, pp. 1–25, Nov. 2024.
[32] G. Barlacchi et al., ‘‘A multi-source dataset of urban life in the city of
Milan and the Province of Trentino,’’ Sci. Data, vol. 2, no. 1, pp. 1–15,
Oct. 2015.
[33] D. Bahdanau, K. Cho, and Y. Bengio, ‘‘Neural machine translation by jointly learning to align and translate,’’ in Proc. ICLR,
2015.
[34] A. Vaswani et al., ‘‘Attention is all you need,’’ in Proc. Adv. Neural Inf.
Process. Syst., vol. 30, 2017, pp. 1–11.
[35] T. Wang et al., ‘‘What language model architecture and pretraining
objective works best for zero-shot generalization?’’ in Proc. Int. Conf.
Mach. Learn., 2022, pp. 22964–22984.
[36] M. Jin et al., ‘‘Large models for time series and spatio-temporal data: A
survey and outlook,’’ 2023, arXiv:2310.10196.
[37] D. P. Kingma and J. Ba, ‘‘Adam: A method for stochastic optimization,’’
2014, arXiv:1412.6980.
[38] S. Sharifi, S. Shahbazpanahi, and M. Dong, ‘‘A POMDP-based antenna
selection for massive MIMO communication,’’ IEEE Trans. Commun.,
vol. 70, no. 3, pp. 2025–2041, Mar. 2022.
[39] D. Eckles and M. Kaptein, ‘‘Thompson sampling with the online bootstrap,’’ 2014, arXiv:1410.4009.
[40] T. L. Marzetta, E. G. Larsson, and H. Yang, Fundamentals of Massive
MIMO. Cambridge, U.K.: Cambridge Univ. Press, 2016.
[41] H. S. Wang and P.-C. Chang, ‘‘On verifying the first-order Markovian
assumption for a Rayleigh fading channel model,’’ IEEE Trans. Veh.
Technol., vol. 45, no. 2, pp. 353–357, May 1996.
[42] G. J. Byers and F. Takawira, ‘‘Spatially and temporally correlated MIMO
channels: Modeling and capacity analysis,’’ IEEE Trans. Veh. Technol.,
vol. 53, no. 3, pp. 634–643, May 2004.
[43] L. Sanguinetti, E. Björnson, and J. Hoydis, ‘‘Toward massive MIMO
2.0: Understanding spatial correlation, interference suppression, and pilot
contamination,’’ IEEE Trans. Commun., vol. 68, no. 1, pp. 232–257,
Jan. 2020.
[44] G. Caire, N. Jindal, M. Kobayashi, and N. Ravindran, ‘‘Multiuser MIMO
achievable rates with downlink training and channel state feedback,’’ IEEE
Trans. Inf. Theory, vol. 56, no. 6, pp. 2845–2866, Jun. 2010.
[45] Y. Li, R. Yu, C. Shahabi, and Y. Liu, ‘‘Diffusion convolutional recurrent
neural network: Data-driven traffic forecasting,’’ in Proc. ICLR, 2018,
pp. 1–16.
[46] L. Bai, L. Yao, C. Li, X. Wang, and C. Wang, ‘‘Adaptive graph convolutional recurrent network for traffic forecasting,’’ in Proc. NIPS, 2020,
pp. 1–12.
[47] B. Yu, H. Yin, and Z. Zhu, ‘‘Spatio-temporal graph convolutional networks:
A deep learning framework for traffic forecasting,’’ in Proc. IJCAI, 2018,
pp. 3634–3640.

VOLUME 3, 2025

KE HE (Graduate Student Member, IEEE)
received the bachelor’s degree from Wuhan University of Technology in 2015 and the master’s
degree in computer science from Guangzhou University in 2021. He is currently pursuing the
Ph.D. degree with the Interdisciplinary Centre
for Security, Reliability and Trust (SnT), University of Luxembourg. His current research interests
include signal processing, resource management,
and machine learning.

THANG XUAN VU (Senior Member, IEEE)
received the B.S. and M.Sc. degrees in electronics and telecommunications engineering from the
VNU University of Engineering and Technology,
Vietnam, in 2007 and 2009, respectively, and
the Ph.D. degree in electrical engineering from
Paris-Sud University, France, in 2014.
In 2010, he received the Allocation de
Recherche Fellowship to study Ph.D. degree in
France. From July 2014 to January 2016, he was
a Post-Doctoral Researcher with Singapore University of Technology and
Design (SUTD), Singapore. Currently, he is a Research Scientist with the
Interdisciplinary Centre for Security, Reliability and Trust (SnT), University
of Luxembourg. His research interests include wireless communications,
with particular interests of applications of optimization and machine learning
on design and analyze the multi-layer 6G networks. He has successfully
acquired, as the PI and vice PI, several Luxembourg national and ESA
projects. He was a recipient of the SigTelCom 2019 Best Paper Award. He is
also serving as an Associate Editor for IEEE COMMUNICATIONS SURVEYS AND
TUTORIALS.

LISHENG FAN received the bachelor’s degree
from the Department of Electronic Engineering,
Fudan University, in 2002, the master’s degree
from the Department of Electronic Engineering,
Tsinghua University, China, in 2005, and the Ph.D.
degree from the Department of Communications
and Integrated Systems, Tokyo Institute of Technology, Japan, in 2008.
He is currently a Professor with the School of
Computer Science, Guangzhou University. He has
published many articles in international journals, such as IEEE TRANSACTIONS
ON WIRELESS COMMUNICATIONS, IEEE TRANSACTIONS ON COMMUNICATIONS, and
IEEE TRANSACTIONS ON INFORMATION THEORY; and papers in conferences, such
as IEEE ICC, IEEE Globecom, and IEEE WCNC. His research interests
include wireless cooperative communications, physical-layer secure communications, intelligent communications, and system performance evaluation.
He was awarded as the Exemplary Reviewer by IEEE TRANSACTIONS ON
COMMUNICATIONS and IEEE COMMUNICATIONS LETTERS. He was a Guest Editor
of many journals, such as Physical Communication, EURASIP Journal on
Wireless Communications and Networking, and Wireless Communications
and Mobile Computing. He is currently an Editor of IEEE TRANSACTIONS ON
VEHICULAR TECHNOLOGY and China Communications.

489

SYMEON CHATZINOTAS (Fellow, IEEE)
received the M.Eng. degree in telecommunications
from the Aristotle University of Thessaloniki,
Greece, in 2003, and the M.Sc. and Ph.D. degrees
in electronic engineering from the University of
Surrey, U.K., in 2006 and 2009, respectively.
He is currently a Full Professor/Chief Scientist
I and the Head of the Research Group SIGCOM,
Interdisciplinary Centre for Security, Reliability
and Trust, University of Luxembourg. In parallel,
he is also an Adjunct Professor with the Department of Electronic Systems,
Norwegian University of Science and Technology, an Eminent Scholar
of Kyung Hee University, South Korea, and a Collaborating Scholar of
the Institute of Informatics & Telecommunications, National Center for
Scientific Research ‘‘Demokritos.’’ In the past, he has been a Visiting
Professor with EPFL, Switzerland, and University of Parma, Italy, and
contributed in numerous research and development projects of the Institute
of Telematics and Informatics, Center of Research and Technology Hellas
and Mobile Communications Research Group, Center of Communication
Systems Research, University of Surrey. He has authored more than 800 technical papers in refereed international journals, conferences, and scientific
books; and has received numerous awards and recognitions, including the
IEEE Fellowship and an IEEE Distinguished Contributions Award.
Dr. Chatzinotas has served in the editorial board for IEEE TRANSACTIONS
ON COMMUNICATIONS, IEEE OPEN JOURNAL OF VEHICULAR TECHNOLOGY, and the
International Journal of Satellite Communications and Networking.

490

BJÖRN OTTERSTEN (Fellow, IEEE) received
the M.S. degree in electrical engineering and
in applied physics from Linköping University,
Linköping, Sweden, in 1986, and the Ph.D. degree
in electrical engineering from Stanford University,
Stanford, CA, USA, in 1990.
He has held research positions with the
Department of Electrical Engineering, Linköping
University; the Information Systems Laboratory, Stanford University; Katholieke Universiteit
Leuven, Leuven, Belgium; and the University of Luxembourg, Luxembourg.
From 1996 to 1997, he was the Director of Research with ArrayComm Inc.,
a start-up in San Jose, CA, USA, based on his patented technology. In 1991,
he was appointed as a Professor in signal processing with the Royal Institute
of Technology (KTH), Stockholm, Sweden, where he has been the Head
of the Department of Signals, Sensors, and Systems, and the Dean of the
School of Electrical Engineering, KTH. He is also the Founding Director
of the Interdisciplinary Centre for Security, Reliability and Trust, University
of Luxembourg. He was a recipient of the IEEE Fourier Technical Field
Award, the IEEE Signal Processing Society Technical Achievement
Award, the EURASIP Group Technical Achievement Award, and European
Research Council (ERC) advanced research grant twice. He has co-authored
journal articles that received the IEEE Signal Processing Society Best Paper
Award in 1993, 2001, 2006, 2013, and 2019, and nine IEEE conference
papers best paper awards. He has been a Board Member of IEEE Signal
Processing Society and Swedish Research Council and currently serves of
the boards for EURASIP and the Swedish Foundation for Strategic Research
and on the ERC Scientific Council. He has served as the Editor-in-Chief
of EURASIP Journal on Advances in Signal Processing and acted on the
editorial boards of IEEE TRANSACTIONS ON SIGNAL PROCESSING, IEEE Signal
Processing Magazine, IEEE OPEN JOURNAL OF SIGNAL PROCESSING, EURASIP
Journal of Advances in Signal Processing, and Foundations and Trends in
Signal Processing. He is a fellow of EURASIP and AAIA and the Royal
Swedish Academy of Engineering Sciences.

VOLUME 3, 2025
PAPER_TEXT
