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
# [266] Multichannel Anomaly Detection for Spacecraft Time Series Using MAP Estimation
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
编号：266
题名：Multichannel Anomaly Detection for Spacecraft Time Series Using MAP Estimation
年份：2024
DOI：10.1109/taes.2024.3400943
来源：IEEE Transactions on Aerospace and Electronic Systems
PDF：paper/10.1109_TAES.2024.3400943.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：时序、日志、KPI 与云原生异常检测、其他AI安全与跨域异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\266.txt
- 原始字符数：62761
- 本次发送字符数：62761
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
Multichannel Anomaly
Detection for Spacecraft Time
Series Using MAP Estimation

anomaly extraction process not only considers the prediction error
values, but also takes the length of detected anomaly sequences and
the interchannel dependencies into account. A case study is given in
the experimental section to illustrate the use of the model on a real
dataset. Also, the effectiveness of our method is evaluated on an Mars
Reconnaissance Orbiter dataset with inserted known anomalies and
two public datasets: Secure Water Treatment and Water Distribution.

I. INTRODUCTION

TIANYU LI
SRIRAM BAIREDDY
MARY COMER , Member, IEEE
EDWARD DELP , Life Fellow, IEEE
Purdue University, West Lafayette, IN USA
SUNDIP R. DESAI
RICHARD H. FOSTER
MOSES W. CHAN , Member, IEEE
Lockheed Martin Corporation, Palo Alto, CA USA

Automated anomaly detection in spacecraft telemetry systems
is essential for analyzing abnormal events and system failures. A
widely adopted strategy is to predict the target time sequences using
a machine learning method first, then extract the anomalies from
the residuals between the target time sequences and the predicted
sequences by a thresholding method. Although thresholding-based
anomaly extraction is simple and fast, it fails to take advantage of correlations between anomaly sequences over time and across channels.
To make the process of anomaly extraction more flexible and more
accurate, a statistical model referred as an anomaly marked point
process (Anomaly-MPP) is proposed in this article. This model treats
anomaly sequences as objects to be detected, making the anomaly
detection a classical object detection problem. Formulating this as
an optimization problem, we find the maximum a posteriori estimate
of the set of anomaly objects in a multichannel time-series dataset,
modeling the prediction error sequences generated from the output
of a transformer with the proposed Anomaly-MPP for the posterior
distribution. The prior distribution can incorporate domain knowledge and user-specified context into the problem formulation, thus
providing additional detection “power.” By including a length prior
energy term and a correlation prior energy term into the model, the
Manuscript received 19 March 2023; revised 20 February 2024 and 29
April 2024; accepted 1 May 2024. Date of publication 14 May 2024; date
of current version 11 October 2024.
DOI. No. 10.1109/TAES.2024.3400943
Refereeing of this contribution was handled by Q. Zhu.
This work was supported by Lockheed Martin Corporation.
Authors’ addresses: Tianyu Li, Sriram Baireddy, Mary Comer, and Edward
Delp are with Purdue University, West Lafayette, IN 47907 USA, E-mail:
(cosmos.yu9@gmail.com; sbairedd@gmail.com; comerm@purdue.edu;
ace@ecn.purdue.edu); Sundip R. Desai, Richard H. Foster, and Moses
W. Chan are with Advanced Technology Center, Lockheed Martin Corporation, Palo Alto, CA 94304 USA, E-mail: (sundip.r.desai@lmco.com;
richard.h.foster@lmco.com; moses.w.chan@lmco.com). (Corresponding
author: Edward Delp.)
0018-9251 © 2024 IEEE
5842

There are thousands of sensors in a typical spacecraft
for collecting various information about the state of the
spacecraft [1], such as temperature, power consumption,
and wheel speed. This information can be used to determine
the status of the spacecraft and help experts to understand
the reasons for a system failure. Usually, subject matter
experts utilize their domain-based knowledge to analyze
subsystem components during root cause analysis by inspecting abnormal events from downlink telemetry [2].
However, massive amounts of time-series data are collected
every day, and it is extremely time-consuming to analyze all
the data manually. Hence, a dependable automated anomaly
detection algorithm is essential for reducing the burden on
domain experts.
Due to the lack of labeled anomalous data, anomaly
detection in time series is often realized in a semisupervised
way. Such semisupervised anomaly detection approaches
can learn the normal and expected behavior of a telemetry
channel, so the anomalies can be identified by the deviations from this behavior [3]. To learn the normal behavior
of a time series, there are mainly two kinds of models:
prediction-based learning models and reconstruction-based
learning models.
A prediction-based model usually learns to predict the
unknown data in the future from past known data. Traditionally, an autoregressive integrated moving average model [4]
has been a common choice for time series prediction. However, it makes a stationarity assumption on the data that
may not be satisfied in a spacecraft system. Support vector
machines are also a potential choice for prediction [5],
[6], and their use in anomaly detection in time series has
been demonstrated in [7]. The ability to learn long patterns
and contextual reasoning makes long short-term memorys
(LSTMs) [8], [9] a popular model for anomaly detection
in time series [10], [11], [12]. They have also proven to be
effective at adapting to new data via transfer learning [13].
Ahmad et al. [14] proposed the hierarchical temporary
memory for online anomaly detection without labeled data.
Baireddy et al. [15] applied extreme learning machines to
real-time anomaly detection. With the successful application of transformers [16], [17] in natural language processing and time series forecasting [18], [19], their potential for
anomaly detection has been demonstrated in [20] and [21].
To fully use the spatial and temporal information of
multichannel time series for predicting the unknown future
behavior, Tian et al. [22] proposed an anomaly detection
network using spatial and temporal information, which
models the relationship graph between variables for a graph

IEEE TRANSACTIONS ON AEROSPACE AND ELECTRONIC SYSTEMS VOL. 60, NO. 5 OCTOBER 2024

attention network to capture the spatial dependency between variables and utilizes an LSTM to mine the temporal dependency of time series. Due to the usefulness of
graphs in depicting objects and their relationships, several
studies have utilized dynamic graphs [23], [24], [25] to
represent multivariate time series and their correlations
over continuous time intervals. Examples include the multivariate time-series anomaly detection via graph attention
network proposed by Zhao et al. [23] and the multimodal
spatial–temporal graph attention network proposed by Ding
et al. [25].
A reconstruction-based model represents the input data
by some latent variables first, then reconstructs the input
data from such latent variables. In [26], generative adversarial networks [27] were proposed as a reconstruction model
for anomaly detection. In [28], the OmniAnomaly detector
is proposed to use a stochastic recurrent neural network to
reconstruct the input data and determine anomalies according to the reconstruction probabilities. Given the capability
of the variational autoencoder model (VAE) [29] to learn a
low-dimensional latent space representation of input time
series, Lin et al. [30] combined VAE with an LSTM model
for input data reconstruction in anomaly detection. To further learn the long-term dependence of time series data,
Chen et al. [31] proposed an RT-Semi VAE, which combines
transformer and VAE.
No matter whether the learning model is prediction
based or reconstruction based, for each target sequence,
it is necessary to generate a residual sequence by deducting the prediction/reconstruction sequence from the target
sequence. Then, an anomaly extraction algorithm will be
applied to the residual sequences to identify the anomaly
sequences. In [10], the anomalies are extracted from the
prediction error sequences by a dynamic thresholding algorithm. In our previous work [2], instead of extracting the
anomalies from the prediction error sequence directly, we
model the distribution of error values by kernel density estimation [32] and convert the error sequence to a likelihood
value sequence based on the error distribution first, then
extract the anomalies from the likelihood value sequence
by a dynamic thresholding method. A peaks-over-threshold
(POT) model [33] is another choice for anomaly extraction from prediction error sequences, having been applied
in [21], [23], [28], and [34].
Thresholding-based anomaly extraction algorithms
work fine for single-channel time series when the learning
model is reliable (the prediction sequence matches the normal part of the target sequence well and the abnormal part
of the target sequence poorly). However, when the performance of the learning model is not sufficient or there is a lot
of noise in the target sequence, the extraction results can be
poor. Moreover, for the case of multichannel time series,
the single-channel thresholding method fails to consider
channel dependencies, rendering it inadequate for anomaly
detection in spacecraft time series as anomalies in different
channels could be related.
To make the anomaly extraction process more flexible and robust for spacecraft time series, we propose an

anomaly marked point process (Anomaly-MPP) to model
the anomaly sequence objects in the target sequences. The
MPP objects in this case are the anomaly sequences. To fit
an anomaly object with the prediction error sequences, a
data energy term is defined based on the contrast between
the prediction errors in a region and those in its neighboring
regions. Also, a length prior term is proposed to penalize
short anomaly sequence objects, which are likely to be
noise. Moreover, a correlation prior term is proposed in
our model, allowing us to identify an anomaly object with
the information of detected anomaly objects in all other
channels. Note that very short anomalies and single-channel
anomalies might still be detected as detection depends on
the complete posterior distribution.
Considering the ability of a transformer to draw global
dependencies between input and output through its attention mechanism [16], we use a bidirectional transformerbased predictor to learn the normal behavior from time
series and generate the predicted sequences. For the task
of anomaly detection in multiple-channel time series, a
residual sequence is calculated by subtracting the prediction
sequence from the target sequence for each channel. Then,
the proposed Anomaly-MPP model is used for the residual
sequences, and maximum a posteriori (MAP) estimation is
used for anomaly extraction. Note that the novelty in this
article is in the modeling and optimization of the multichannel prediction error sequences, and although we use a
transformer in this work, the method proposed here could
be used with other prediction/reconstruction approaches.
In summary, our work makes the following contributions.
1) We propose a novel statistical model Anomaly-MPP
with MAP estimation for anomaly extraction in multichannel time series.
2) We introduce the length prior energy term and the
correlation prior energy term into our model to
suppress short anomaly objects and establish relationships among anomaly objects across different
channels, which is essential for anomaly detection
in spacecraft time series.
3) Extensive experiments show the flexibility and effectiveness of our approach, outperforming the commonly used thresholding-based methods.
The rest of this article is organized as follows. In
Section II, the problem of anomaly detection is properly
defined. In Section III, we briefly review the structure of the
transformer and how we use it in our application first, then
the Anomaly-MPP model is presented in detail. A standard
method for MAP optimization for MPPs is used, so we
describe it briefly. In Section IV, experimental results are
given to show the performance of our approach. Finally,
Section V concludes this article.
II. PROBLEM STATEMENT

In this work, we address the problem of anomaly detection in multichannel time series. Denote the target time

LI ET AL.: MULTICHANNEL ANOMALY DETECTION FOR SPACECRAFT TIME SERIES USING MAP ESTIMATION

5843

greater lengths. In addition, the correlation prior energy
incorporates insights from other channels.
In this section, we describe the structure of the transformer and introduce how we use it in our work first, then
the proposed Anomaly-MPP model is discussed in detail.
Finally, we give a brief description of the MAP optimization
method we use.

A. Transformer Review

Fig. 1. Diagram of the proposed anomaly detection method. The gray
block is the novel contribution of this article.

series as X = [x1 , x2 , . . ., xN ], where xt ∈ RM , N is the
number of samples in X , and M is the total number of
channels.
In a spacecraft system, a system-level anomaly may
trigger anomalies in several channels, and these anomalies
may not always occur at the same time. For example, an
anomaly could occur in an electrical power channel before
a corresponding anomaly appears in a related temperature
channel. To assist with root cause analysis, our objective is
not only to answer the question of when an anomaly occurs
but also to give information about which channels are
questionable. That is, for the target time series X ∈ RM×N ,
our objective is to find a set of anomaly sequences
[(i, ki , starti , endi )], where i means the ith anomaly, ki is the
channel where the anomaly is found, and starti and endi are
the starting and ending time of the ith anomaly, respectively.
III. METHODOLOGY

Fig. 1 shows the diagram of our method for multichannel
anomaly detection. There are mainly two parts: the first is
the time series predictor, which is a pure transformer-based
predictor. We train the predictor with sequences assumed
to have no anomalies. Since the spacecraft system runs
at a normal status most of the time, such normal data are
easily accessible. In the anomaly detection process, we feed
the target multichannel sequences into the trained predictor
to generate the predicted sequences. An error sequence is
computed as the difference between a target sequence and
its predicted sequence. The second part of our approach is
an anomaly extractor that uses MAP estimation to detect
anomaly objects from the error sequences, which are modeled using an Anomaly-MPP. With the data energy, length
prior energy, and correlation prior energy defined in the
Anomaly-MPP model, it is flexible to extract the anomaly
objects with different settings. The data energy promotes the
detection of objects with high error contrast. Meanwhile, the
length prior energy discourages the identification of short
objects with low error contrast while favoring those with
5844

Our choice of a transformer-based predictor stems from
its exceptional capabilities in capturing temporal dependencies and modeling complex sequences. Unlike traditional
sequence models, such as recurrent neural networks, transformers leverage self-attention mechanisms to efficiently
capture long-range dependencies across sequences. This
ability is crucial for our task, which involves predicting
data points where signals may exhibit complex temporal
patterns. In addition, transformers offer scalability and
parallelization, enabling efficient processing of large-scale
sequential data without sacrificing model performance.
The transformer-based predictor utilized in our method
follows the original transformer architecture [16]. The
main differences between the transformer-based forecasting
model used in [18] and our predictor are the input and
output. Since our task is neither real-time anomaly detection
nor forecasting of unknown future data, we do not use
the left-to-right forecasting model. Instead, a bidirectional
prediction model is used, as shown in Fig. 2. Intuitively,
a bidirectional model is more powerful [17], especially for
predicting the data at points where a signal changes abruptly.
For a subsequence [xt−L , xt−L+1 , . . ., xt , . . .xt +L ] of the
test sequence X = [x1 , x2 , . . ., xN ], where L controls the
size of the transformer input. We mask the middle three data
samples with 0 s to generate the input data for time t: X t =
[xt−L , . . ., xt−2 , 0, 0, 0, xt +2 . . .xt +L ]. We try to predict xt
based on the input X t . The reason for masking the middle
three data samples rather than only masking xt is to avoid the
trivial prediction of replicating the immediately preceding
or succeeding values or by the average of the two [35].
The transformer has an encoder–decoder architecture.
The encoder encodes the input representation X t into a hidden state representation Zt = [zt−L , zt−L+1 , . . ., zt , . . .zt +L ],
where zi ∈ Rdmodel , and dmodel is the model dimension.
The decoder decodes an output representation At =
[a1 , a2 , . . ., aLd ] from the hidden representation Zt and the
rightmost Ld elements of X t , where Ld is the size of the
input of the decoder, ai ∈ Rdmodel . Finally, a linear layer is
applied to map At to the prediction x̂t .
The encoder is composed of an input layer, a positional
encoding layer, and a stack of four identical encoder layers.
The input layer linearly projects the M-dimensional input
onto a dmodel -dimensional vector space. Since the attention
model contains no recurrence and no convolution operations, to make use of the order information of the sequence,
the positional encoding layer is applied to inject position information with sine and cosine functions [16]. The encoder

IEEE TRANSACTIONS ON AEROSPACE AND ELECTRONIC SYSTEMS VOL. 60, NO. 5 OCTOBER 2024

Fig. 2. Structure of the bidirectional transformer-based predictor with L = 3 and Ld = 2.

layer uses one multi-attention block to learn the dependencies of data with different positions. A multi-attention
block consists of six attention blocks, each attention block
realizing the “scaled dot-product attention” by


QK T
Attention(Q, K, V ) = softmax √
dk


V

(1)

where Q, K, and V are the query matrix, key matrix,
and value matrix, respectively, Q ∈ Rq×dk , K ∈ R p×dk , V ∈
R p×dv , q is the number of queries, p is the number of
key–value pairs, dk is the dimension of each key and query,
and dv is the dimension of each value.
The decoder is composed of an input layer and a stack
of four identical decoder layers. The input layer is the same
as the one in the encoder. The decoder layer has two multiattention blocks, one for learning the dependencies of input
data and the other for integrating the information from the
hidden representation Zt . To read the details of the encoder
layer and the decoder layer, see the original transformer
paper [16].
The commonly-used mean squared error loss function
is used to train the transformer-based predictor in our application.
B. Anomaly-MPP Model

With the transformer trained on the training data, we can
generate a predicted sequence X̂ = [x̂L+1 , x̂L+2 , . . ., x̂N−L ]

from the test sequence X = [x1 , x2 , . . ., xN ], where x̂n =
[x̂1,n , x̂2,n , . . ., x̂M,n ] and xn = [x1,n , x2,n , . . ., xM,n ].
Let E = [e1 , e2 , . . ., eN ] be the absolute error sequence,
where en = [e1,n , e2,n , . . ., eM,n ] and em,n = |xm,n − x̂m,n |
(Note: for convenience, we ignore the first and last L data
points in the test sequence). When em,n is relatively large, it
indicates potential abnormal behavior at time n in channel
m.
The Anomaly-MPP is proposed to model the set of
anomalies in the multichannel input based on the error sequence E . In this section, we will define the Anomaly-MPP
model first, then discuss the data and prior energy terms
of the model, and finally, briefly describe the optimization
method we use to find the MAP estimate of the set of
anomaly sequences.
1) Anomaly-MPP Model: Let S be the M × N lattice,
S = [1, M ] × [1, N ] ⊂ R2 , upon which the input data X
are defined. Then, a point process on S is a set of points
{S1 , S2 , . . ., SK } ⊆ S, with random variables Si = (mi , ni )
representing the random location of the ith point, where mi
is its channel identifier (ID) and ni is the time location. The
random variable K is the total number of points in the point
process [36], [37].
By associating a mark bi to each point object Si ,
we get an MPP [38], [39]. In the Anomaly-MPP model,
bi ∈ B is the random width of the ith anomaly object,
where B = [bmin , bmax ] is the mark space with parameters
bmin and bmax . A marked object is denoted as Wi = (Si , bi ) ∈
S × B. Then, an anomaly configuration is defined as W =

LI ET AL.: MULTICHANNEL ANOMALY DETECTION FOR SPACECRAFT TIME SERIES USING MAP ESTIMATION

5845

Fig. 4. Inner area (yellow) and outer area (green) of an object.

Fig. 3. Example of anomaly object configuration.

{W1 , W2 , . . ., WK }. The space of all possible configurations W has elements of the form w = {w1 , w2 , . . ., wk },
containing anomaly objects w1 , . . ., wk . Fig. 3 shows an
example of an object configuration within three channels.
A Gibbs model is used for the MPP, which results in a
posterior density function given by
1
exp{−Vd (e|w) − Vp (w)}
(2)
Z
where w is an anomaly object configuration, e is the observed error sequence, Vd (e|w) is the data energy, which
determines the fit of the anomaly configuration w to the
observed error sequence e, Vp (w) is the prior energy, and Z
is the normalizing constant. Our goal is to find the object
configuration that maximizes f (w|e ), that is, the MAP
estimate of W given that the observation error sequence
is e.
It remains to define the energy functions Vd and Vp in
(2). We will use a common “reward” function [40] [given
in (6)] for Vd and for each part of Vp , as described next.
2) Data Energy: Under the assumption that the elements of the error sequence E are conditionally independent
given that W = w for any configuration w ∈ W , the data
energy term of (2) can be written as

f (w|e ) =

Vd (e|w) =

k


Ṽd (e|wi )

where k is the number of anomalies in configuration w. The
basic idea of the data energy we propose is this: if the mean
error value of object wi is larger than the mean error value
of its neighboring regions, then it has higher probability to
be a true anomaly object, and thus should have a smaller
Ṽd (e|wi ).
Define the outer area of object wi as the union of its left
neighborhood lefti and right neighborhood righti , which are
the green areas shown in Fig. 4. We set the neighborhood
area length to bmax , where bmax is the parameter of the
maximum object width. Then, let uin (wi ) be the mean error
value of object wi , and uout (wi ) be the mean error value of
its outer area. Define the error contrast as
uin (wi ) − uout (wi )
contrast(wi ) =
.
(4)
uout (wi )
Let D (wi ) = Gd contrast(wi )2 with data gain Gd , being
fixed for our experiments, and set

5846

Fig. 6. Function of h (x, T, K ) with K = 2 and T = 0.1, 0.5, 0.8, 1, 2,
respectively.

(3)

i=1

Ṽd (e|wi ) = h (D (wi ), Gd Td2 , Kd )

Fig. 5. Function of h (x, T, K ) with T = 0.5 and K = 0.1, 0.5, 1, 2, 5,
respectively.

(5)

where the data term threshold Td and data reward coefficient
Kd are parameters settable by the user, and h is the reward
function defined as

1 − Tx ,
if x < T
(6)
h (x, T, K ) =
 −(x−T ) 
− 1, else.
exp
Kx
Figs. 5 and 6 present the function h with fixed T and
fixed K, respectively. As we can see, when x < T , the function returns a linear positive value, which can be taken as a
linear penalty. When x > T , the function returns a negative
reward, which is controlled by the reward coefficient K.
3) Prior Energy: The prior energy Vp (w) describes
prior information about objects, and is given by
Vp (w) = Vpol (w) + αVplen (w) + βVpco (w).

(7)

The overlap prior Vpol (w) rejects overlapping between
any two objects in the same channel, the length priorVplen (w)
penalizes objects with short length, the correlation prior
Vpco (w) takes account of the relationship among objects in

IEEE TRANSACTIONS ON AEROSPACE AND ELECTRONIC SYSTEMS VOL. 60, NO. 5 OCTOBER 2024

Fig. 7. Overlapping of two objects.

different channels, and α and β are the weights for the last
two terms.
a) Overlap prior: For the task of anomaly detection, we
do not allow overlapping between any two objects within a
channel. That is if two objects are in the same channel and
overlap with each other, as shown in Fig. 7, then the one
with larger data energy should be removed. This helps to
avoid the detection of a single anomaly as multiple different
anomalies. Define

Vpol (w) =
g(wi , w j )
(8)

Fig. 8. Illustration for correlation prior.

To simplify computation, we compute the correlation
prior for each object separately and let
Vpco (w) =


g(wi , w j ) =

∞, if wi and w j overlap
.
0,
otherwise.

(9)

b) Length prior: To avoid false alarms caused by noise, the
length prior term Vplen (w) is introduced to encourage long
objects and penalize short objects. We let
Vplen (w) =

k


Ṽplen (wi )

(10)

i=1

where
Ṽplen (wi ) = h (L (bi ), L (Tl ), Kl ).

(11)

In this case
L (x ) = Gl Rl (x )2

(12)

and
Rl (x ) =

Ṽpco (wi ).

(14)

i=1

i= j

where

k


x − bmin
bmax − bmin

(13)

so the first argument to the reward function h is a quadratic
function of the length of anomaly i, the second argument is
the same quadratic function of the length threshold, and the
third argument is the length reward coefficient. The length
gain Gl is fixed for our experiments.
c) Correlation prior: The correlation prior Vpco (w) is introduced to model the relationships among objects in different
channels. Fig. 8 gives an example to illustrate the basic idea
of the correlation prior. For any two channels, say channel
m1 and channel m2 , suppose that an object w1 is in channel
m1 at location n1 , and another object w2 exists in channel
m2 at location n2 . We expand w1 and w2 by a width d, as
shown in the green area in Fig. 8. If the expanded object w1
and object w2 are overlapped in the timeline, then both of
them should have a higher probability to be true anomalies,
thus we reduce the prior energy for w1 and w2 .

For object wi in channel mi located at time ni , we count
the number ci of channels that have expanded objects, which
overlap with the expanded wi in the timeline. Then, we let
Ṽpco (wi ) = h (P (ci , M ), P (Tco , M ), Kco )

(15)

P (x, M ) = Gco R2 (x, M )

(16)

where

and
x
(17)
M −1
where Tco is the correlation threshold parameter, Kco is the
correlation reward coefficient, and Gco is the correlation
gain, which is fixed for our experiment.
4) Optimization Method: To find the MAP estimate
of the true anomaly configuration under our model, the
Gibbs energy in (2) must be minimized, so that the posterior
distribution is maximized. A reversible jump Markov chain
Monte Carlo [41] method is widely used for this type of
problem when the normalizing constant of the posterior
density is difficult to calculate. However, this algorithm is
mainly based on proposing local perturbations, which limits
its convergence speed. Instead, we use the multiple birth and
death (MBD) algorithm [42], [43], which is able to make
multiple perturbations in parallel, to search for the optimal
configuration.
The MBD algorithm runs a birth step and a death
step iteratively. At iteration i, given the previous configuration w(i − 1), we propose a new configuration w =
{w1 , w2 , . . ., wk  } to get w = w(i ) ∪ w in the birth step.
In the death step, we update w(i ) by removing nonfitting
objects from w. The algorithm keeps iterating until a convergence condition is satisfied or the maximum iterations
set by the user is reached.
R2 (x, M ) =

IV. EXPERIMENTS

To illustrate the proposed Anomaly-MPP-MAP approach in detail, a case study is made on five selected
channels from the Soil Moisture Active Passive satellite
(SMAP) dataset [44]. Then, we test the method on a Mars

LI ET AL.: MULTICHANNEL ANOMALY DETECTION FOR SPACECRAFT TIME SERIES USING MAP ESTIMATION

5847

Fig. 9. Example to compare different anomaly counting methods.

Reconnaissance Orbiter (MRO) dataset, to which we have
inserted multichannel anomalies, to show its advantage
over threshold-based methods for anomaly extraction in
multichannel series. Finally, we apply the Anomaly-MPPMAP approach to a single accumulated error sequence
generated from Secure Water Treatment (SWaT) and Water
Distribution (WADI) datasets [45], [46] to further verify its
effectiveness.
A. Datasets

Four datasets have been used in our experiments: SMAP
dataset [10], [44] which is a spacecraft dataset collected by
NASA; MRO dataset, which is a spacecraft dataset provided by Lockheed Martin; SWaT dataset [45], which was
collected from a water treatment testbed for cyber-attack
investigation in 2015; and WADI dataset [46], which was
collected from a water distribution testbed as an extension
of the SWaT testbed.
The SMAP dataset contains 54 channels of time series,
each with 25 features (the first feature is the telemetry value
and others are related to system status). There is a training
sequence and a test sequence for each channel, with the
test sequences varying in length. For our illustrative case
study, we select the telemetry value sequences from five
channels (A-2, A-3, A-4, E-1, and E-10) with similar length
to form a multichannel test case, which is partially shown
in Fig. 10. There are a total of seven anomaly sequences in
these channels.
The MRO dataset includes thousands of channels, which
encompass all spacecraft subsystems, and is downlinked to a
ground system at varying sample rates [2]. The MRO dataset
does not contain ground truth anomalies and is considered
an unlabeled dataset. For each channel, a single week of
data preceding a system reboot is given. We assume that
the first five-and-half days of data of the time series in each
channel represents normal functioning. By this assumption,
eight groups of data were created from the first five days
of data (the original data points were downsampled to one
measurement every 30 s). In each group, ten channels were
randomly selected from the MRO dataset. The time series
is divided into training sequences and test sequences for
each channel, with lengths of 5000 and 10 000, respectively.
Anomalies were injected into the test sequence in a similar
way as described in [47]. There are a total of 140 injected
5848

Fig. 10. Part of the test time series used in the case study.

anomaly sequences in all the groups. We treat each group
of data as a ten-channel test case.
The SWaT dataset contains 51 channels of data collected
in 11 days: seven days under normal operation and four days
with attack scenarios. A total of 41 attacks appear in the last
four days of data.
The WADI dataset contains 123 channels of data collected in 16 days: 14 days under normal operation and two
days with attack scenarios, with 15 attacks launched during
the last two days.
Following the work in [21] and [24], the original data
samples for SWaT and WADI are downsampled to one
measurement every 10 s by taking the median values. Since
the attacks (anomalies) are labeled for the whole system
rather than for every single channel in SWaT and WADI,
after getting the absolute prediction error sequence for
each channel, we add all of the error sequences together
to generate an accumulated error sequence. We test the

IEEE TRANSACTIONS ON AEROSPACE AND ELECTRONIC SYSTEMS VOL. 60, NO. 5 OCTOBER 2024

Anomaly-MPP model on this 1-D sequence without the
correlation prior.

TABLE I
Comparison of Different Anomaly Counting Methods

B. Evaluation Metrics

Quantitative evaluation of the performance of anomaly
detection in time series is not straightforward. There are
mainly three ways commonly used to count anomalies:
strict-point-based method, adjusted-point-based method,
and segment-based method.
In the strict-point-based method, when a time point is
classified as an anomaly, if it is labeled as a true anomaly in
the ground truth, then this point is counted as a true positive
(TP); otherwise, it is a false positive (FP). When a point is
labeled as a true anomaly in the ground truth, but it is not
classified as an anomaly in the detection, then it is a false
negative (FN).
In the task of anomaly detection, the start and end points
of an anomaly segment are sometimes “blurry” [48]. Often,
partial detection of an anomaly is enough for experts to analyze the anomaly segment. Thus, the adjusted-point-based
metric has been broadly applied to anomaly detection [28].
In the adjusted-point-based method, if any point of a true
anomaly segment is detected as an anomaly point, then
the whole true anomaly window is considered as correctly
detected and every observation point in this segment will
be counted as a TP. If no point of a true anomaly segment is
detected as an anomaly, then all points belonging to this true
anomaly segment are taken as FNs. The detected anomaly
points outside the true anomaly segments are treated as FPs.
For the segment-based counting method [10], a detected
anomaly segment consists of consecutive detected anomaly
points. A TP is recorded if any portion of a true anomaly
segment falls within any detected segment of anomalies. An
FN is recorded if no detected segments overlap with a true
anomaly segment. An FP is recorded if a detected segment
does not overlap with any true anomaly segment.
After defining the TP, FP, and FN in different counting
methods, the standard evaluation metrics, namely, precision, recall, and F1-score can be used to evaluate the performance of an anomaly detection approach, where
TP
TP + FP
TP
,
Recall =
TP + FN
Precision × Recall
F1 = 2 ×
.
Precision + Recall
Precision =

(18)
(19)
(20)

To compare the point-based metrics and segment-based
metric, an example with ground truth (blue line) and detected anomalies (orange line) is shown in Fig. 9. The
evaluation results for this example are given in Table I.
Compared with the strict-point-based method, the adjustedpoint-based method re-labels 60 FN points to TP as the
second and the third detected anomaly segments are overlapped with two true anomaly segments. We can see that
the adjusted-point-based metric is insensitive to short FNs.
Even though two of the five true anomaly segments are

not detected, the recall is still as high as 0.86, which is
not reasonable in our application, since it is important to
discover the short anomaly segments for system diagnosis.
The segment-based method works on segments rather
than points, so each anomaly segment is equally counted.
The recall is 0.6 in the example, which is more reasonable for our application. However, by expanding the length
of a detected anomaly segment, one could improve the
segment-based recall without reducing the precision. The
first detected anomaly sequence in Fig. 9 gives an example
for this case. Although only a small portion of this detected
anomaly is covered by the true anomaly segment, the other
parts do not contribute to FPs, so the segment-based recall
and F1 scores could be improved by simply extending
each detected anomaly segment, without any penalty to the
precision.
The segment-based method is preferred in our task, but
to reduce the effect of the aforementioned problem, we
propose a split-segment-based method for counting anomalies. The way to count TP, FP, and FN is the same as the
segment-based method, but we will set a maximum length
Lmax for the detected anomaly sequence. When the length of
the detected anomaly sequence is larger than Lmax , the detected anomaly is split into shorter anomaly sequences with
length less or equal to Lmax before counting anomalies. In
the example of Fig. 9, we set Lmax = 50, so the first detected
anomaly segment is split into three parts by the dashed red
lines, which results in two more false alarms. Note that
this adjustment is made only for computing performance
metrics and does not affect the detected anomalies presented
to the user.
In analyzing the results of our experiments, we mainly
focus on the split-segment-based metrics, and the maximum
length of sequence Lmax is set to 1000. Meanwhile, we
present the adjusted-point-based results just for reference,
since that is often used in the literature. Since our method
considers not only the amplitude of the error value but also
the length of an anomaly object, a detected anomaly object
could contain many points with low error values, which
may result in low precision with the adjusted-point-based
metrics. Thus, we extract the peaks from a detected anomaly
segment as detected anomaly points for calculating the
adjusted-point-based results.

LI ET AL.: MULTICHANNEL ANOMALY DETECTION FOR SPACECRAFT TIME SERIES USING MAP ESTIMATION

5849

TABLE II
Parameters of Anomaly-MPP Model

Fig. 11. Correlation heatmap of the test channels in the case study.

C. Experiment Settings

A transformer-based predictor was used to generate the
prediction error sequences. To keep consistency, the parameters of the predictor were set to be the same for all of our
experiments. The input window size parameter L = 150,
model dimension dmodel = 36, value dimension dv = 36,
key dimension dk = 96, and decoder input size Ld = 6.
In the training process, Adam optimizer was used with
initial learning_rate = 0.001. Early stopping was applied
when validation loss did not decrease for 30 epochs, and
the maximum training epoch was 300. The batch size was
set to 128.
The 14 parameters of the proposed Anomaly-MPP
model are listed in Table II. There are three groups of
parameters, namely, data energy parameters, length prior
energy parameters, and correlation prior energy parameters.
The three gain parameters Gd , Gl , and Gco from each group,
which are used to control the range of the independent
variable of the reward function, were fixed to the values
in Table II for all of our experiments. The minimum and
maximum lengths (bmin and bmax ) of anomaly objects were
set to 6 and 600, respectively. The expanded width dcor
for calculating the correlation prior energy was set to 300.
The values of the other eight parameters (Td , Kd , wl , Tl ,
Kl , wco , Tco , and Kco ), whose values differ for the four
datasets for which we present results, are discussed in the
following section. Note that the fixed parameter values were
determined experimentally to work well for all four datasets
tested.
All the experiments were implemented by Python and
PyTorch, running on a workstation with an Intel Core i75930 K CPU and two 24 Gb Titan RTX GPUs.
D. Case Study

An anomaly detection example is presented in this section to illustrate how each term in the energy function of
the Anomaly-MPP model works. We select five channels
(A-2, A-3, A-4, E-1, and E-10) of telemetry time series
from the SMAP dataset as the test series for this illustration.
5850

Part of the time series is shown in Fig. 10 and its absolute
correlation heatmap is shown in Fig. 11. The two E-channels
are highly correlated, the A-2 channel and the A-4 channel
are weakly correlated, and A-3 seems not to be correlated
with any other channels. There are a total of seven anomalies
(red shaded segments in Fig. 10) in the test sequences of
these five channels. The three anomalies in A-channels
appear around time = 4500. Two short anomalies happen
in E-channels around time = 5000, followed by two long
anomalies around time = 5700.
Since the original time sequences are not aligned, we
trained each channel separately with the transformer-based
predictor. The absolute prediction error sequences are generated with the trained predictor. Fig. 12 shows all five of
the absolute prediction-error sequences for this case study,
superimposed. The Anomaly-MPP model aims to extract
the anomalies from these error sequences.
1) Data Energy With Overlap Prior Energy: In the
beginning, we only include the data energy and overlap prior
energy. Thus, the weights for length prior and correlation
prior are set to zero (α = 0, β = 0). The overlap prior is kept
to prohibit the overlapping of objects in the same channel. In
this case, the fitting of objects is mainly determined by the
data energy term Ṽd (e|wi ). When Ṽd (e|wi ) < 0, the object
wi is more likely to be an anomaly. When wi and w j are
overlapped in the same channel, the object with larger Ṽd
will be killed. According to (6), and as seen in Figs. 5 and 6,
the reward function h is monotonically decreasing with the
independent variable x, the threshold parameter T controls
when to reward, and the reward coefficient parameter K
is related to the degree of reward only when x > T . For a
fixed Kd = 5, we test with different Td . Table III gives the
test results with different Td . When Td is very small (e.g.,
Td = 0.8), we can extract all the TP with a lot of FPs. When
we increase Td , the precision goes up, however, the recall
may also decrease as in the case of Td = 2.4. Since the data
energy is based on the error contrast (between the inner and
outer area of the object), generally, it is impossible to extract
all the true anomalies without generating any false alarms.

IEEE TRANSACTIONS ON AEROSPACE AND ELECTRONIC SYSTEMS VOL. 60, NO. 5 OCTOBER 2024

Fig. 12. Superimposed absolute prediction errors for each channel in the case study.

TABLE III
Extracted Results With Fixed Kd = 5 and Different Td

TABLE IV
Extracted Results With Fixed Kl = 5 and Different Tl

TABLE V
Extracted Results With Fixed Kco = 5 and Different Tco

Fig. 13. Detecting results from channel A-4 with data energy and
overlap energy. Red shaded area: ground truth, and green hatched area:
detection results.

Fig. 13 shows the extraction results in channel A-4 when
Td = 1.6. In addition to the true anomalies, the detected
false alarms also have high error contrast. They generally
also have short lengths.
2) Adding Length Prior Energy: In this section, we
fix Kd = 5 and Td = 1.6 and add the length prior energy
to our previous test model by setting the weight of length
prior α = 0.15 to penalize the short objects and encourage
long objects. Again, we keep the length reward parameter
Kl = 5 and try different Tl in our test. From the results
given in Table IV, by introducing the length prior term,
the precision improved in all of the five cases. The short
FP in A-4 presented in Fig. 13 is killed in the case Tl = 60.
However, it is still not easy to remove all false alarms with
the added length prior energy.

3) Adding Correlation Prior Energy: We may remove all the false alarms by fine-tuning the parameters
of Kd , Td , α, Kl , and Tl . However, the parameter tuning
process for just a few false detections could be tedious
and time-consuming due to the tradeoff between recall
and precision. Instead of fine-tuning parameters, we can
introduce some more prior knowledge to improve the
detection results. Here, we add the correlation prior energy to the previous model by setting the weight of the
correlation prior β = 0.15 and keeping Kd = 5, Td = 1.6,
α = 0.15, Kl = 5, Tl = 60, and Kco = 5 in the new test.
Also, we fix the neighbor distance dcor = 300 for the correlation prior. The test results with different Tco are given
in Table V. For the cases of Tco = 1.0 and Tco = 1.5, we
reached the 1.0 F-1 score in the segment-based metric.
It is worth noting that the correlation prior is introduced
to capture dependencies among anomaly objects occurring in different channels. This is particularly beneficial
for scenarios where an anomaly appears in one channel,
followed by anomalies occurring in other channels, which
is a common case in spacecraft subsystems. When anomaly

LI ET AL.: MULTICHANNEL ANOMALY DETECTION FOR SPACECRAFT TIME SERIES USING MAP ESTIMATION

5851

Fig. 14. Detection results of SWaT dataset. Red shaded area: ground truth, and green hatched area: detection results.

TABLE VI
Anomaly Detection Results of MRO-MUL Dataset

TABLE VII
Anomaly Detection Results of SWaT Dataset

objects in different channels are independent, it is preferable to conduct single-channel analysis by setting β = 0 to
disregard the correlation prior energy.
E. Test on MRO-MUL Dataset

There are eight groups of data in MRO-MUL dataset,
each containing ten channels. For each group of data, a
transformer-based predictor is trained in a multichannel-in
and multichannel-out manner. By applying the trained
predictor on the test data, we can generate ten absolute
error sequences for each group. Then, we extract the
anomalies from the error sequences by several different
anomaly extraction methods for comparison: POT [34],
dynamic threshold (DT) [10], and Anomaly-MPP. For our
proposed method, we set the same parameters for all of the
eight groups of tests by trial and error: Td = 2.2, Kd = 5,
α = 0.2, Tl = 120, Kl = 5, β = 0.3, Tco = 3, and Kco =
6. The quantitative test results are given in Table VI.
F. Test on SWaT and WADI Dataset

There are 51 channels of data in the SWaT dataset. We
trained a transformer-based predictor on all the channels in
a multi-in and multi-out manner. Absolute prediction error
sequences are generated from the test data spanning four
days. Unlike what we do in the test of MRO-MUL dataset,
we do not extract anomalies from each channel separately.
Instead, we treat the combination of the 51 channels as a
single system since the true anomaly points are labeled at
the system level rather than the channel level. We added the
51 absolute prediction error sequences into a single error
5852

Fig. 15. SWaT detection results in the range of [16 300, 18 200]. Red
shaded area: ground truth, and green hatched area: detection results.

sequence and scaled the error value into range [0, 1] as the
blue line shown in Fig. 14. To extract the anomalies from
this sequence, we reset the parameters of the AnomalyMPP model as: Td = 0.4, Kd = 6, α = 0.4, Tl = 120, and
Kl = 1. The correlation prior is not used, thus β = 0. The
detected results are given in Table VII. Our method still
outperforms the threshold-based anomaly extraction methods even though the target error sequence is single. To
see why this happens, let us focus on the sample range
[16 300, 18 200] of the error sequence, which is presented
in Fig. 15. The maximum prediction error value in the true
anomaly sequence is smaller than the errors in other normal
places, which makes it impossible for a threshold-based
method to extract the true anomalies without extracting
other false alarms. But with the length prior in our model, the
true anomaly is extracted without any false alarms because
its accumulated error is larger than the accumulated error in
other places and the length prior encourages longer anomaly
objects while penalizing shorter anomaly objects. Note that

IEEE TRANSACTIONS ON AEROSPACE AND ELECTRONIC SYSTEMS VOL. 60, NO. 5 OCTOBER 2024

Fig. 16. Detection results of WADI dataset. Red shaded area: ground truth, and green hatched area: detection results.

TABLE VIII
Anomaly Detection Results of WADI Dataset

G. Computational Considerations

Compared with the simple and fast thresholding-based
anomaly extraction methods, the proposed Anomaly-MPP
in the above experiments has slower processing speeds for
different time series, with additional running times ranging
from a few seconds to dozens of seconds. As an MPP
optimized by MBD, the process of extracting anomalies
by Anomaly-MPP involves simulating the birth (creation)
and death (removal) of points (anomaly objects) in a point
process, which require complex calculations. In addition,
like many Monte Carlo simulation algorithms, MBD may
require many iterations to converge to a stable solution,
which can contribute to the algorithm’s overall running
time. To accelerate the proposed method, one potential
approach is to carefully parallelize the birth and death
operations across multiple processing units, although this
is beyond the current scope of this work.
V. CONCLUSION

Fig. 17. One of the FNs in the WADI detection results. Red shaded
area: ground truth, and green hatched area: detection results.

although shorter anomaly objects are penalized, it is still
possible to detect short anomalies if the other energy terms
in the model favor it enough.
Although there are a total of 123 channels in the WADI
dataset, we processed it in the same way as we did for the
SWaT dataset. The anomaly detection results are shown in
Fig. 16 and Table VIII. Note that the recall for this dataset
is not as high as for the other datasets. By checking the
error sequence, there are no obvious clues for the missed
anomalies. Fig. 17 shows the subsequence with one of the
FNs. The error values in the true anomaly region are not
significantly larger than the error values in other places,
which resulted in the missed detection. This example shows
that the extraction results are still highly dependent on the
prediction results from the learning model since the data
energy depends on the prediction errors.

In this article, we proposed an anomaly detection
method for multichannel time series, using a transformerbased predictor for generating prediction error sequences
and an Anomaly-MPP model with MAP estimation for
extracting the anomalies from the error sequences. The
proposed Anomaly-MPP model is mainly controlled by
three energy terms: the data energy, length prior energy, and
correlation prior energy. The data energy encourages objects
with high error contrast to be detected. The length prior
energy suppresses short objects with low error contrast and
rewards objects with longer lengths. The correlation prior
energy introduces the information from other channels. A
case study on the time sequences from the SMAP dataset is
given to show the function of each energy term. Experimental results on MRO-MUL dataset, SWaT dataset, and WADI
dataset prove the superiority of our Anomaly-MPP model
over the threshold-based anomaly extraction methods that
have been previously proposed.
Although our Anomaly-MPP model is quite flexible, the
performance is still highly dependent on the error sequences
generated by the predictor since the object data energy

LI ET AL.: MULTICHANNEL ANOMALY DETECTION FOR SPACECRAFT TIME SERIES USING MAP ESTIMATION

5853

is based on the error contrast. This is difficult to correct
with a deep-learning approach for prediction, because of
the “black-box” nature of deep learning systems. However,
it is not necessary for the data energy to be defined on
prediction error sequences. For example, we could define
the data energy according to the variance of the values in
the original input sequence. In our future work, we plan to
explore some other data energy terms that do not depend on
prediction error sequences.
REFERENCES
[1] A. E. Hassanien, A. Darwish, and S. Abdelghafar, “Machine learning
in telemetry data mining of space mission: Basics, challenging
and future directions,” Artif. Intell. Rev., vol. 53, pp. 3201–3230,
Jun. 2020.
[2] T. Li et al., “A stacked predictor and dynamic thresholding algorithm
for anomaly detection in spacecraft,” in Proc. IEEE Mil. Commun.
Conf., 2019, pp. 165–170.
[3] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A
survey,” ACM Comput. Surv., vol. 41, no. 3, 2009, Art. no. 15.
[4] R. Adhikari and R. Agrawal, An Introductory Study on Time series
Modeling and Forecasting. Saarbrücken, Germany: LAP LAMBERT
Academic Publishing, 2013.
[5] N. I. Sapankevych and R. Sankar, “Time series prediction using
support vector machines: A survey,” IEEE Comput. Intell. Mag.,
vol. 4, no. 2, pp. 24–38, May 2009.
[6] R. Samsudin, A. Shabri, and P. Saad, “A comparison of time series forecasting using support vector machine and artificial neural
network model,” J. Appl. Sci., vol. 10, pp. 950–958, 2010.
[7] S. R. Mounce, R. B. Mounce, and J. B. Boxall, “Novelty detection for
time series data analysis in water distribution systems using support
vector machines,” J. Hydroinformat., vol. 13, no. 4, pp. 672–686,
2010.
[8] S. Hochreiter and J. Schmidhuber, “Long short-term memory,” Neural Comput., vol. 9, no. 8, pp. 1735–1780, 1997.
[9] I. J. Goodfellow, Y. Bengio, and A. Courville, Deep Learning, Ser.
Adaptive Computation and Machine Learning Series. Cambridge,
MA, USA: MIT Press, 2016.
[10] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric dynamic thresholding,” in Proc. 24th ACM SIGKDD Int. Conf.
Knowl. Discov. Data Mining, 2018, pp. 387–395.
[11] P. Malhotra, L. Vig, G. Shroff, and P. Agarwal, “Long short term
memory networks for anomaly detection in time series,” in Proc.
Eur. Symp. Artif. Neural Netw., 2015, pp. 89–94.
[12] B. Lindemann, B. Maschler, N. Sahlab, and M. Weyrich, “A survey
on anomaly detection for technical systems using LSTM networks,”
Comput. Ind., vol. 131, 2021, Art. no. 103498.
[13] S. Baireddy et al., “Spacecraft time-series anomaly detection using
transfer learning,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit., AI Space Workshop, 2022, pp. 1951–1960.
[14] S. Ahmad, A. Lavin, S. Purdy, and Z. Agha, “Unsupervised real-time
anomaly detection for streaming data,” Neurocomputing, vol. 262,
pp. 134–147, 2017.
[15] S. Baireddy, M. Chan, S. Desai, R. Foster, M. Comer, and E. Delp,
“Spacecraft time-series online anomaly detection using extreme
learning machines,” in Proc. IEEE Aerosp. Conf., 2022, pp. 1–9.
[16] A. Vaswani et al., “Attention is all you need,” in Proc. Int. Conf. Adv.
Neural Inf. Process. Syst., 2017, pp. 6000–6010.
[17] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “BERT: Pretraining of deep bidirectional transformers for language understanding,” in Proc. Conf. North Amer. Chap. Ass. Comput. Linguistics:
Human Lang. Technol., Minneapolis, Minnesota, 2019, pp. 4171–
4186.
[18] N. Wu, B. Green, X. Ben, and S. O’Banion, “Deep transformer
models for time series forecasting: The influenza prevalence case,”
2020, arXiv:2001.08317.
5854

[19] H. Zhou et al., “Informer: Beyond efficient transformer for long
sequence time-series forecasting,” in Proc. AAAI Conf. Artif. Intell.,
2021, vol. 35, pp. 11106–11115.
[20] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer:
Time series anomaly detection with association discrepancy,” in
Proc. Int. Conf. Learn. Representations, 2022. [Online]. Available:
https://openreview.net/forum?id=LzQQ89U1qm_
[21] Z. Chen, D. Chen, X. Zhang, Z. Yuan, and X. Cheng, “Learning graph structures with transformer for multivariate time series
anomaly detection in IoT,” IEEE Internet Things J., vol. 9, no. 12,
pp. 9179–9189, Jun. 2022.
[22] Z. Tian, M. Zhuo, L. Liu, J. Chen, and S. Zhou, “Anomaly detection
using spatial and temporal information in multivariate time series,”
Sci. Rep., vol. 13, 2023, Art. no. 4400.
[23] H. Zhao et al., “Multivariate time-series anomaly detection via graph
attention network,” in Proc. IEEE Int. Conf. Data Mining, 2020,
pp. 841–850.
[24] A. Deng and B. Hooi, “Graph neural network-based anomaly detection in multivariate time series,” in Proc. AAAI Conf. Artif. Intell.,
2021, vol. 35, pp. 4027–4035.
[25] C. Ding, S. Sun, and J. Zhao, “MST-GAT: A multimodal spatial–
temporal graph attention network for time series anomaly detection,”
Inf. Fusion, vol. 89, pp. 527–536, 2023.
[26] A. Geiger, D. Liu, S. Alnegheimish, A. Cuesta-Infante, and
K. Veeramachaneni, “TadGAN: Time series anomaly detection using
generative adversarial networks,” in Proc. IEEE Int. Conf. Big Data,
2020, pp. 33–43.
[27] A. Creswell, T. White, V. Dumoulin, K. Arulkumaran, B. Sengupta, and A. A. Bharath, “Generative adversarial networks: An
overview,” IEEE Signal Process. Mag., vol. 35, no. 1, pp. 53–65,
Jan. 2018.
[28] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent
neural network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, 2019, pp. 2828–2837.
[29] J. An and S. Cho, “Variational autoencoder based anomaly detection
using reconstruction probability,” Special Lecture IE, vol. 2, no. 1,
pp. 1–18, 2015.
[30] S. Lin, R. Clark, R. Birke, S. Schönborn, N. Trigoni, and S. Roberts,
“Anomaly detection for time series using VAE-LSTM hybrid model,”
in Proc. IEEE Int. Conf. Acoust., Speech, Signal Process., 2020,
pp. 4322–4326.
[31] N. Chen, H. Tu, X. Duan, L. Hu, and C. Guo, “Semisupervised
anomaly detection of multivariate time series based on a variational
autoencoder,” Appl. Intell., vol. 53, pp. 6074–6098, 2023.
[32] B. W. Silverman, Density Estimation for Statistics and Data Analysis.
Evanston, IL, USA: Routledge, 2018.
[33] E. Simiu and N. Heckert, “Extreme wind distribution tails: A
“peaks over threshold” approach,” J. Struct. Eng., vol. 122, no. 5,
pp. 539–547, 1996.
[34] A. Siffer, P.-A. Fouque, A. Termier, and C. Largouet, “Anomaly
detection in streams with extreme value theory,” in Proc. 23rd ACM
SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2017, pp. 1067–
1075.
[35] G. Zerveas, S. Jayaraman, D. Patel, A. Bhamidipaty, and C. Eickhoff, “A transformer-based framework for multivariate time series
representation learning,” in Proc. 27th ACM SIGKDD Conf. Knowl.
Discov. Data Mining, 2021, pp. 2114–2124.
[36] C. J. Geyer and J. Møller, “Simulation and likehood inference for
spatial point processes,” Scand. J. Statist., vol. 21, no. 4, pp. 359–373,
1994.
[37] J. Illian, A. Penttinen, H. Stoyan, and D. Stoyan, Statistical Analysis
and Modelling of Spatial Point Patterns. Hoboken, NJ, USA: Wiley,
2008.
[38] M. N. M. V. Lieshout, Markov Point Processes and Their Applications. London, U.K.: Imperial College Press, 2000.
[39] X. Descombes and J. Zerubia, “Marked point process in image
analysis,” IEEE Signal Process. Mag., vol. 19, no. 5, pp. 77–84,
Sep. 2002.

IEEE TRANSACTIONS ON AEROSPACE AND ELECTRONIC SYSTEMS VOL. 60, NO. 5 OCTOBER 2024

[40] H. Zhao, M. L. Comer, and M. D. Graef, “A unified Markov random field/marked point process image model and its application to
computational materials,” in Proc. IEEE Int. Conf. Image Process.,
2014, pp. 6101–6105.
[41] P. J. Green, “Reversible jump Markov chain Monte Carlo computation and Bayesian model determination,” Biometrika, vol. 82, no. 4,
pp. 711–732, 1995.
[42] X. Descombes, “Multiple objects detection in biological images using a marked point process framework,” Methods, vol. 115, pp. 2–8,
2017.
[43] X. Descombes, R. Minlos, and E. Zhizhina, “Object extraction using
a stochastic birth-and-death dynamics in continuum,” J. Math. Imag.
Vis., vol. 33, no. 3, pp. 347–359, 2009.
[44] P. O’Neill, D. Entekhabi, E. Njoku, and K. Kellogg, “The NASA soil
moisture active passive (SMAP) mission: Overview,” in Proc. IEEE
Int. Geosci. Remote Sens. Symp., 2010, pp. 3236–3239.
[45] A. P. Mathur and N. O. Tippenhauer, “SWaT: A water treatment testbed for research and training on ICs security,” in Proc.
Int. Workshop Cyber- Phys. Syst. Smart Water Netw., 2016,
pp. 31–36.
[46] C. M. Ahmed, V. R. Palleti, and A. P. Mathur, “WADI: A water
distribution testbed for research in the design of secure cyber physical
systems,” in Proc. 3rd Int. Workshop Cyber- Phys. Syst. Smart Water
Netw., 2017, pp. 25–28.
[47] T. Li, M. Comer, E. Delp, S. R. Desai, R. H. Foster, and M. W. Chan,
“A matching-based method for anomaly verification in spacecraft
telemetry,” in Proc. IEEE Aerosp. Conf., 2022, pp. 1–8.
[48] Q. Wen et al., “Time series data augmentation for deep learning: A
survey,” in Proc. 13th Int. Joint Conf. Artif. Intell., Z.-H. Zhou, 2021,
pp. 4653–4660.

Tianyu Li received the Ph.D. degree in electrical
and computer engineering from the School of
Electrical and Computer Engineering, Purdue
University, West Lafayette, IN, USA, in 2023.
His research interests include image processing using statistical models and deep learning
models, as well as time series forecasting and
anomaly detection in time series.

Sriram Baireddy received the B.S. and M.S.
degrees in electrical engineering with minors
in economics, math, and physics in 2018 and
2021, respectively, from Purdue University,
West Lafayette, IN, USA, where he is currently
working toward the Ph.D. degree in electrical
engineering.
His research interests include the application
of machine learning techniques to signals, images, and videos for forensic and agricultural
research.

Edward Delp (Life Fellow, IEEE) received
the B.S. and M.S. degrees in electrical engineering from the University of Cincinnati,
OH, USA, in 1973 and 1975, respectively, and
the Ph.D. degree in electrical engineering from
Purdue University, West Lafayette, Indiana, in
1979.
He is a Charles William Harrison Distinguished Professor of electrical and computer engineering and Professor of biomedical engineering with Purdue University, West
Lafayette, IN, USA. His research interests include image and video
processing, image analysis, computer vision, image and video compression, multimedia security, medical imaging, multimedia systems, and
communication and information theory.

Sundip R. Desai received the B.S. degree
in aeronautical and astronautical engineering
from the California state polytechnic universityPomona, California, in 2004, and the M.S. degree in aeronautical and astronautical engineering from university of southern California, Los
Angeles, California, in 2011.
He is a Guidance, Navigation and Controls
Engineer and Associate Fellow with Lockheed
Martin Space Center, Palo Alto, CA, USA,
where his research interests include general machine learning, computer vision, explainable AI, recommender systems,
pose estimation, anomaly detection, and characterization of time series
signals.

Richard H. Foster is a Senior Principal Research Engineer with the Lockheed Martin
Space Advanced Technology Center, Palo Alto,
CA, USA. His research interests include system
protection using multiphenomenology observables and applying AI/machine learning techniques to advance the methods for the protection
of systems, and in addition, applying optimal
estimation techniques in optimizing the design
and performance of advance communication
systems, electronic warfare, and multidomain
remote sensing systems.

Moses W. Chan (Member, IEEE) received the
B.S., M.S., and Ph.D. degrees in electrical engineering from Purdue University, West Lafayette,
Indiana, in 1991, 1993, and 1999, respectively.
He is a Lockheed Martin Technical Fellow.
His research interests include primarily defensive systems with multisensor and multi-int fusion, missile defense, space tracking and surveillance, and spacecraft anomaly detection.

Mary Comer (Member, IEEE) received the
B.S., M.S., and Ph.D. degrees in electrical engineering from Purdue University, West Lafayette,
Indiana, in 1990, 1993, and 1995, respectively.
She is an Associate Professor of electrical and
computer engineering with Purdue University,
West Lafayette, IN, USA. Her research interests
include statistical image modeling and analysis,
stochastic simulation of images, rare event modeling and simulation, and anomaly detection.

LI ET AL.: MULTICHANNEL ANOMALY DETECTION FOR SPACECRAFT TIME SERIES USING MAP ESTIMATION

5855
PAPER_TEXT
