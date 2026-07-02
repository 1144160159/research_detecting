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
# [506] PASTA : Neural Architecture Search for Anomaly Detection in Multivariate Time Series
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
编号：506
题名：PASTA : Neural Architecture Search for Anomaly Detection in Multivariate Time Series
年份：2024
DOI：10.1109/tetci.2024.3508845
来源：IEEE Transactions on Emerging Topics in Computational Intelligence
PDF：paper/10.1109_TETCI.2024.3508845.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：中相关，分数 7
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\506.txt
- 原始字符数：84035
- 本次发送字符数：84035
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2924

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 9, NO. 4, AUGUST 2025

PASTA: Neural Architecture Search for Anomaly
Detection in Multivariate Time Series
Patara Trirat , Member, IEEE, and Jae-Gil Lee , Senior Member, IEEE

Abstract—Time-series anomaly detection uncovers rare errors
or intriguing events of interest that significantly deviate from
normal patterns. In order to precisely detect anomalies, a detector needs to capture intricate underlying temporal dynamics
of a time series, often in multiple scales. Thus, a fixed-designed
neural network may not be optimal for capturing such complex
dynamics as different time-series data require different learning
processes to reflect their unique characteristics. This paper proposes a Prediction-based neural Architecture Search for Time series
Anomaly detection framework, dubbed PASTA. Unlike previous
work, besides searching for a connection between operations, we
design a novel search space to search for optimal connections in the
temporal dimension among recurrent cells within/between each
layer, i.e., temporal connectivity, and encode them via multi-level
configuration encoding networks. Experimental results from both
real-world and synthetic benchmarks show that the discovered architectures by PASTA outperform the second-best state-of-the-art
baseline by around 13.6% in the enhanced time-series aware F1
score on average, confirming that the design of temporal connectivity is critical for time-series anomaly detection.
Index Terms—Neural architecture search, AutoML, time-series
anomaly detection, temporal connectivity encoding.

I. INTRODUCTION
IME-SERIES anomaly detection (TSAD) aims at determining abnormal patterns or deviant behaviors that are
extremely rare in a time series. For half a century [1], it has
served as one of the fundamental tasks in data mining and
has been an active research area with various applications,
e.g., fraud detection and fault diagnosis. Early endeavors [2],
[3] solved this problem using statistical or machine learning
methods. However, the massive amount of multivariate time
series generated nowadays makes the problem more challenging
for the traditional approaches. In addition to the well-known
challenges, e.g., high complexity of data and diverse types of
anomalies, a model for multivariate TSAD also needs to capture

T

Received 29 July 2024; accepted 5 November 2024. Date of publication 9
December 2024; date of current version 24 July 2025. This work was supported
by the Institute of Information & Communications Technology Planning &
Evaluation (IITP) grant funded by the Korea government (MSIT) (No. RS-2020II200862, DB4DL: High-Usability and Performance In-Memory Distributed
DBMS for Deep Learning, 50% and No. RS-2022-II220157, Robust, Fair,
Extensible Data-Centric Continual Learning, 50%). (Corresponding author:
Jae-Gil Lee.)
The authors are with the School of Computing, KAIST, Daejeon 34141,
Republic of Korea (e-mail: patara.t@kaist.ac.kr; jaegil@kaist.ac.kr).
This article has supplementary downloadable material available at
https://doi.org/10.1109/TETCI.2024.3508845, provided by the authors.
Recommended for acceptance by Y. Zhou.
Digital Object Identifier 10.1109/TETCI.2024.3508845

intricate temporal dynamics and relationships within/between
multiple variables, i.e., sensors [4], [5].
In recent years, unsupervised deep learning (DL) models
have achieved state-of-the-art performance in TSAD, surpassing
traditional methods by a large margin. Specifically, recurrentbased layers [6], [7], [8], [9], [10] were adopted with generative
networks, such as autoencoder (AE), to capture the nonlinear
complexity of high-dimensional multivariate time series. Like
other domains, ensemble learning [11], [12] was also adopted
to enhance the model’s robustness when deciding whether a
particular instance is anomalous. Moreover, multi-resolution
learning1 [13], [14], [15] was used to enhance the representations
of normal patterns on different scales and learn long-range
and diverse temporal dependencies. However, such efficient
DL-based detectors rely laboriously on human experts to design
the neural architecture, tune the hyperparameters, and select a
proper anomaly scoring function, impeding its wider adoption.
These efforts are usually time-consuming, less systematic trialand-error, and the resulting solutions may still be suboptimal
given that different time series have different unique characteristics to be considered.
Neural architecture search (NAS) was proposed to reduce
human efforts by automatically designing deep neural networks and sometimes selecting their hyperparameters accordingly [16]. Despite the substantial progress of NAS techniques
in several tasks, NAS for time-series data is still underexplored
with only a few papers on classification [17], [18], [19] and
forecasting [20], [21], [22] problems. In addition, we cannot
directly use them for TSAD due to the following challenges.
1) Lack of a suitable search space for TSAD: Most existing search spaces [23] consist of convolutional networks (CNN), whereas a few include recurrent networks (RNN). Still, the RNN-based spaces are designed
by following the CNN-based spaces to find a new connection between operations within a micro-level motif.
Thus, other essential settings for RNN-based AEs, such
as macro configurations and layer hyperparameters, are
ignored. Moreover, to achieve state-of-the-art results, information on how recurrent cells are connected in the
time dimension is vital for TSAD using RNN-based architectures to model multi-scale temporal dependency [11],
[13], [14]. We call such connection temporal connectivity,
i.e., the connection between different time steps. As in
1 In this paper, multi-resolution or multi-scale learning broadly refers to
learning or extracting multiple time-scale information.

2471-285X © 2024 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

TRIRAT AND LEE: PASTA: NEURAL ARCHITECTURE SEARCH FOR ANOMALY DETECTION IN MULTIVARIATE TIME SERIES

Fig. 1.

Proposed multi-level search space and architecture encoding scheme.

Fig. 1, we argue that the search space for TSAD should
cover not only architecture configurations, e.g., layer
hyperparameters, but also the TSAD task-specific settings
for global configurations and temporal connectivity because the operation-only search space is insufficient to
build high-performance TSAD [4], [24].
2) Lack of multi-level configuration encoding for RNNbased AEs: Current studies on architecture encoding for
NAS mainly focus on layer-level or operation-level connections to distinguish architectures as a directed acyclic
graph (DAG) in the search space [25], [26]. This simple single-level DAG-based encoding will not be able to
differentiate the RNN-based AE models having different cell-level2 configurations, e.g., temporal connectivity.
Hence, with the hierarchical structure of our search space,
a novel way to encode these multi-level configurations—
from network to layer to cell—effectively is indispensable
for the subsequent search process.
Motivated by the above TSAD challenges, we propose a
novel Prediction-based neural Architecture Search framework
for Time-series Anomaly detection called PASTA. To tackle
the first challenge, we design and construct a new search space
based on the insights from deep TSAD [11], [13], [14], [15], [27]
and preliminary experiments (see Section III) that the temporal
connectivity between recurrent cells and layers significantly affects TSAD performance. Accordingly, with the introduction of
temporal connectivity subspace, the search method can systematically learn how to form the connections for capturing multiple
resolutions of complex temporal dynamics in multivariate time
series instead of relying solely on randomness [11], [14], which
is significant for the anomaly detection task.
Although having temporal connectivity subspace provides
better detection performance, it comes with the cost of having
a larger search space. This motivates us to figure out how to
incorporate it into the NAS setting effectively. As architecture
encoding plays a vital role in NAS [28], [29], for the second challenge, we propose a multi-level configuration encoding based on
unsupervised architecture representation learning to accompany
the new search space by aggregating task-specific settings, network configurations, and temporal connectivity subspaces. The
encoder will map these multi-level configurations into a learned
latent space. It improves the embedding quality by learning the
2 Throughout this paper, the term “cell” refers to a recurrent cell at a time step
within a recurrent layer.

2925

hierarchical structure of connections in the neural networks and
boosts the search efficiency of a performance predictor by using
high-quality low-dimensional learned latent spaces instead of
massive raw representations.
Finally, we realize the PASTA framework by bridging the
newly proposed two components with a performance predictorguided search method. The predictor learns to predict the architecture performance based on the encoded representations
from the multi-level configuration encoder and guides the search
process with its predicted performance given a set of encoded
architectures on the search space.
Our main contributions are listed below.
r We propose a new search space tailored for TSAD, including TSAD-specific settings, architecture configurations,
and various temporal connectivity types between recurrent
cells. This search space allows a search method to search
on different levels of an anomaly detection model more
flexibly.
r We introduce a new architecture encoding technique for
prediction-based NAS that learns the relationships between
different levels of TSAD model configurations, including the temporal connectivity between/within recurrent
layers. This encoding enables a search method to find
high-performing models based on the encoded features
more effectively.
r We propose a novel prediction-based NAS for TSAD,
PASTA, based on the newly introduced search space and
multi-level configuration encoding. To verify the effectiveness of PASTA, we conduct thorough experiments on
both synthetic and real-world benchmarks compared with
diverse handcrafted TSAD, AutoML, and random search.
On average, the models discovered by PASTA increase the
enhanced time-series aware F1 [30] scores by at least
13.6%.
The paper is organized as follows. Section II reviews related
work. Section III explains problem statements and the proposed
PASTA. Then, Section IV presents the experimental setup and
results. Finally, Section V concludes this study.
II. RELATED WORK
A. Time-Series Anomaly Detection (TSAD)
Although we can perform TSAD in (semi-)supervised settings, unsupervised methods are the most prevalent due to the
insufficiency of labeled data. Traditionally, we can classify
TSAD approaches into statistical and machine learning-based
methods [3], [31], [32]. Recently, several DL-based studies [4],
[33], [34] have shown to be superior to the traditional methods.
The most well-known deep TSAD are prediction-based [6],
[35], [36] and reconstruction-based [7], [8], [11], [12], [14],
[15], [27], [35], [37], [38], [39], [40], [41], [42], [43], [44],
[45] methods. The former uses prediction (or forecasting) errors
as anomaly scores, while the latter uses reconstruction errors.
Previous research has shown that reconstruction-based methods significantly outperform forecasting-based ones. Among
different network types, Transformer-based models [41], [42],
[43], [46] have achieved state-of-the-art results in the past few
years. However, recent findings [34], [47] reveal that a simple

2926

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 9, NO. 4, AUGUST 2025

reconstruction-based LSTM model can outperform state-of-theart Transformer-based models under an appropriate experimental setup.
There have been several attempts to enhance the effectiveness
of reconstruction-based methods using RNNs. Kieu et al. [11] introduce TSAD models based on ensembles of recurrent AEs with
sparsely-connected RNNs to create multiple AEs having different temporal connection structures. This framework reduces
the overfitting of individual AEs, while promoting diversity and
robustness. The recurrent reconstructive network [27] uses skip
transitions to enhance the connectivity between recurrent units
by reducing the path length for a more efficient information
flow, resulting in faster convergence, mitigating gradient-related
issues, and more accurate detection.
From multi-resolution learning perspectives, THOC [13] uses
a dilated RNN with skip connections to capture temporal dynamics at multiple scales. RAMED [14] further incorporates ensembles of multiple decoders with different decoding lengths to
capture anomalies that may be evident at different granularities.
On top of ensembling, RAMED [14] proposes coarse-to-fine
fusion mechanism to integrate lower-resolution information into
higher-resolution decoders to improve the long-range decoding capabilities, allowing the model to capture both local and
global temporal patterns. Lately, Qingning et al. [15] employ
an attention-based recurrent AE model that captures features
at various scales through a hierarchically connected recurrent
encoder. These multi-scale approaches enable the models to
understand both fine-grained and coarse-grained temporal patterns, improving their ability to detect anomalies that manifest
differently across various temporal granularities compared to
traditional RNNs that focus only on single-scale features and
short-term dependencies likely insufficient to detect anomalies
occurring at multiple scales.
In line with recent findings, this paper focuses on finding
the best ensembles of multi-resolution RNN architectures with
the unsupervised reconstruction-based method, especially for
multivariate TSAD, which has consistently shown state-of-theart performance.
B. Neural Architecture Search (NAS)
NAS was initiated as neuroevolution [48], [49] in the 1990s
and has become popular in the last five years thanks to hardware
advancements [50], [51]. A NAS framework requires three core
components. First, we need a search space to define which
architectures can be represented in principle. It can be either
convolutional-based [50], [52], [53], [54], [55], [56], [57], [58],
[59], [60], [61] or recurrent-based search space [50], [54], [55],
[62], [63]. Recently, Transformer-based search spaces [64], [65],
[66], [67] have started drawing attention from the computer
vision and natural language processing (NLP) communities.
However, as discussed above, RNN-based models can outperform Transformer-based models for TSAD. Second, a search
strategy is developed to explore the search space. Commonlyused search strategies include reinforcement learning [50], [51],
[68], evolutionary algorithms [69], [70], gradient-based methods [54], [71], [72], Bayesian optimization [73], [74], [75], and

prediction-based methods [76], [77], [78], [79], [80]. Among
these strategies, prediction-based NAS has proven to be the
most efficient [77], [81]. Third, to evaluate candidate architectures on the downstream task with unseen data, we need a
performance estimator. Early NAS [69], [82] evaluated candidate architectures by training from scratch with enormous
computational costs, restricting the wide adoption in real-world
environments. Therefore, many attempts tried to solve this issue
by early stopping, low-fidelity training with proxy datasets or
architectures [83], weight sharing [54], [71], [84], and, more recently, surrogate models for performance prediction, resulting in
increased sample efficiency and decreased computation burden.
Although NAS has demonstrated its successes in diverse
tasks [26], e.g., adversarial learning [85], [86], NLP [59], [64],
[87], and spatial-temporal prediction [60], [61], NAS for time
series is still underexplored despite the fact that there are various
tasks in time-series data mining [88]. There are a few studies
for classification [17], [18], [19] and forecasting [20], [62],
[89] tasks. Even though these studies also propose new search
spaces, they adopt existing motifs from previous studies in other
domains and do not consider the temporal connectivity when
designing search spaces for temporal modeling. In addition,
since existing RNN-based studies for other tasks [26], [59],
[63], [90], [91], [92] focus on finding neural networks using
single-level macro or micro search spaces without considering
temporal connection between RNN cells required for TSAD,
we need to design the new search space for effective TSAD.
Meanwhile, automated model selection methods [93], [94] focus
only on building a pipeline from a collection of existing models,
not searching for new architectures. A comprehensive review
can be found in the survey papers [16], [95], [96], [97].
C. Neural Architecture Encoding
Early NAS [50], [55], [69], [98] used discrete encodings (e.g.,
text sequence or adjacency matrix) to represent design choices
in search space. Unfortunately, these simple encodings faced
the scalability problem in large search spaces [97]. Due to the
impact of architecture representation on the search and final
task-specific performance [25], recent studies seek for more
efficient ways of architecture encoding to maximize the final
performance and reduce the search cost, including continuous relaxation-based [54], learning-based structure-aware [28],
[76], [99], [100] or computation-aware [29], [78], [101], and
path-based [75], [79], [102] encodings. As reported by Yan
et al. [28], the learning-based encodings have proven to be the
optimal solution, especially for those trained without supervision signals (i.e., accuracy) from a search process, because the
supervision signals could bias the architecture representation
learning and search direction.
III. PROPOSED FRAMEWORK: PASTA
This section formulates the problem of NAS for TSAD and
describes the details of PASTA, including the search space, multilevel configuration encoding, and predictor-guided search. An
overview of PASTA is illustrated in Fig. 2.

TRIRAT AND LEE: PASTA: NEURAL ARCHITECTURE SEARCH FOR ANOMALY DETECTION IN MULTIVARIATE TIME SERIES

2927

Fig. 2. Overall procedure of PASTA. Phase 1 first randomly samples M configurations from the search space for pre-training the multi-level configuration
encoder. Phase 2 then samples |Ntrain | + |Neval | configurations and uses the pre-trained encoder to get their embeddings for the subsequent search process.

A. Problem Formulation
We contend that NAS for TSAD has two key characteristics.
First, the architecture in the RNN-based AE—notably, the temporal connectivity between recurrent cells—needs to be adaptive for the given dataset to achieve competitive performance.
Second, TSAD also requires the designs of anomaly scoring
and corresponding objective functions. Formally, we outline the
problem of NAS for TSAD as follows. Suppose that a model
for TSAD consists of three components: the anomaly detectionspecific (hereafter, task-specific) settings S, the RNN-based AE
architecture A, and the temporal connectivity C. We denote a
model as a triple (S, A, C).
Given a time series of length T having d-dimensional vectors X = {x1 , . . . , xT }, xt ∈ Rd , the input of (S, A, C) is a
sequence of time windows W = {W1 , . . . , WT −K+1 }, Wt =
{xt , . . . , xt+K−1 } of length K with stride 1 normalized and
split from X, following Kim et al. [103]. The goal of (S, A, C)
is to predict the anomaly label ŷt ∈ {0, 1}, t > T for the test
windows Wtest . The labels are obtained by comparing anomaly
scores Sscore (Wt ) with a predefined threshold δ; ŷt = 1 if
Sscore (Wt ) > δ, otherwise 0.
Then, let the triple (S, A, C) denote the search space of TSAD
models, where S denotes the task-specific subspace, A denotes
the architecture subspace, and C denotes the temporal connectivity subspace. Given the training set Wtrain and validation set
Wvalid , we aim to find the optimal model (S  , A , C  ) trained
on Wtrain that maximizes the predicted validation performance
on Wvalid (e.g., F1 score) by a predictor P,
(S  , A , C  ) =

arg max P(S, A, C).

(1)

S∈S,A∈A,C∈C

S is a task-specific setting for an architecture A with a temporal
connectivity C.
B. Tailored Search Space for TSAD
Due to the lack of intrinsic search space for TSAD, we newly
design the search space for the RNN-based AEs, following the
latest successful deep TSAD models [4], [11], [13], [14], which

can learn complex temporal dynamics in multiple scales and
construct an ensemble of multiple AEs to increase the robustness
of TSAD. As summarized in Table I, it is a triple (S, A, C) which
represents the task-specific setting, architecture configuration,
and temporal connectivity. Details and formal descriptions are as
follows. Due to the space limit, we skip the details of architecture
configurations (A) subspace as they are already well-known.
1) Task-Specific Settings: We design the task-specific subspace S to accompany the global-level choices and constraints
for the entire TSAD model, which affect the detection performance [4], [24]. The possible configurations are as follows.
Anomaly Scoring Function: The scoring function Sscore of
a model (S, A, C) determines how likely a value at a particular time step is anomalous. In reconstruction-based methods,
Sscore compares the original input and its reconstructed version.
Formally, the anomaly scoring functions in our search space are
defined by
absolute error
= |Wt − Ŵt |
Sscore
squared error
Sscore
= (Wt − Ŵt )2
normal distribution
Sscore
= (et − μe )T Σ−1
e (et − μe )

Mahalanobis distance
= (et − μt )Σ−1 (et − μt )T
Sscore
max normalized error
Sscore
= max ait , where ait =
i

eit − μ̃i
.
σ̃i

(2)

Wt is the original input time-series windows. Ŵt is the reconstructed version. et = Wt − Ŵt . N (μe , Σe ) is the normal
distribution estimated by et . eit is the error at time t of a
sensor/variable i. μ̃i and σ̃i are the median and inter-quartile
range across time steps of the eit values, respectively.
Output Direction: In addition to the forward output direction, which is the same as the input, as shown in previous
work [11], [14], [27], training with the backward (i.e., reverse)
output direction is beneficial for TSAD. Thus, we also include
this option in the search space.

2928

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 9, NO. 4, AUGUST 2025

TABLE I
SUMMARY OF PASTA’S SEARCH SPACE

Loss Function: The loss functions Sloss are defined by
MAE
=
Sloss

1
|Wt − Ŵt |
T t=1

MSE
=
Sloss

1
(Wt − Ŵt )2
T t=1

T

T

1
log(cosh(Ŵt − Wt )),
T t=1
T

LogCosh
Sloss
=

(3)

where Wt is the original input time-series windows, Ŵt is the
reconstructed version, and T is the length of a time series.
Number of Autoencoders: Due to the robustness of ensemble
learning [11], [14], we allow the search method to explore
whether learning with multiple AE networks is really helpful.
Recurrent Cell Types: Since our focus is mainly on searching
for better temporal connectivity and commonly-used recurrent
layers are powerful enough to achieve state-of-the-art performance, we only include the vanilla RNN [104], LSTM [105],
and GRU [106] in our search space, denoted as Scell .
2) Architecture Configurations: The architecture configuration subspace A is a set of hyperparameters for each layer in
an AE network. This subspace directly accounts for the representation power of the neural architecture. Here, we consider a
number of hidden units, an activation function, and the use of
dropout.
3) Temporal Connectivity: Given the identical task-specific
and architecture configurations, we conduct preliminary experiments and find that only adjusting the connection between cells
can significantly affect the TSAD performance. For example, the
F1 score increases from 0.697 to 0.809 by changing the default
connection to dense random skip with feedback transition. The
preliminary results of 16 types of temporal connectivity are presented in Fig. 3. Accordingly, we design this temporal connectivity subspace C to systematically find the optimal connections
between recurrent cells for modeling the temporal dynamics of
time series on multiple scales.
As exemplified in Fig. 4, we include two types—within-layer
and between-layer—of connectivity for each cell in a layer. For

Fig. 3. F1 scores between different types of temporal connectivity. Numbers
in parenthesis are the indices indicating the type of connections in the search
space. Specifically, {0: Default connections, 1: (Full connection, uniform skip),
2: (Feedback transition, dense random skip), 3: (Skip transition, sparse random
skip)}. The experimental setup is in the supplementary material.

the within-layer connection, we include three special connections successfully applied for TSAD [11], [13], [14]: uniform
skip, dense random skip, and sparse random skip. The uniform
skip connects time steps with a constant rate of 2l−1 in l-th layer
(see Fig. 4(b)). For the random skips, the dense one randomly
forms an extra connection on top of the default connection, while
the sparse one fully forms the random connections for the entire
layer.
Within-Layer Temporal Connectivity: This type of connectivity designates how different cells in the same layer are connected.
Let rt,l be a recurrent cell r at time t in any layer l. The four
choices for within-layer temporal connectivity are
default
= Scell (ht,l−1 , ht−1,l )
rt,l
uniform skip
rt,l
= Scell (ht,l−1 , ht−2l−1 ,l )

Scell (ht,l−1 , ht−1,l ) + Scell (ht,l−1 , ht−L,l )
2
Scell (ht,l−1 , w1 ht−L1 ,l )+Scell (ht,l−1 , w2 ht−L2 ,l )
sparse rand.
,
=
rt,l
|w1 | + |w2 |
(4)
dense rand.
=
rt,l

where ht,l is a hidden state of layer l at time t, h0,l = 0,
and ht,0 = xt . In the random skips (denoted as rand.) [11],
[14], L is the skip length randomly sampled from [1, 10], and
w1 , w2 are the weight coefficients randomly sampled from

TRIRAT AND LEE: PASTA: NEURAL ARCHITECTURE SEARCH FOR ANOMALY DETECTION IN MULTIVARIATE TIME SERIES

Fig. 4.

2929

Examples of within (dotted-green) and between (dashed-red) layer temporal connectivity. Uni. means uniform skip. Rand. means random skip.

{(1, 0), (0, 1), (1, 1)} to ensure that the cell is connected to at
least one previous cell.
Similarly, regarding the between-layer connection, we include
three special connections reported to be helpful in temporal
modeling [27]: feedback transition, skip transition, and full
connection, as shown in Fig. 4(b)–(d), respectively.
Between-Layer Temporal Connectivity: This type of connectivity represents how cells in a layer connect to other cells in
the upper or lower layers. Let rt,l be a recurrent cell r in layer l
at time step t. For between-layer temporal connectivity, the four
choices are defined by
default
rt,l
= Scell (ht,l−1 )
full connection
rt,l
= Scell (ht−1,l−1 , ht−1,l+1 )

Fig. 5. Importance of temporal connectivity encoding. The same architectures
with different temporal connectivity would give an identical embedding when
the connections in the temporal dimension were disregarded.

feedback transition
rt,l
= Scell (ht−1,l+1 )
skip transition
rt,l
= Scell (ht−1,l−1 ),

(5)

where ht,l is a hidden state of the layer l at time t, h0,l = 0, and
ht,0 = xt .
In particular, the dense and sparse random skip connections
are formed independently for each layer, making the subspace
size dependent on the input sequence length K = |Wt |. That
is, as the input sequence length increases, the search space size
increases exponentially, because the number of possible choices
for each timestamp is multiplied to the search space size. Since
K is usually around 100in practice [8], [41] and there can be
up to two connections per cell within the same layer, the search
space size becomes about up to 299 ≈ 6.34 × 1029 only for a
single layer.
Note that other settings, configurations, and customized connections can also be added to the above subspaces.
C. Phase 1: Multi-Level Configuration Encoding
As the encoding method of candidate architectures significantly affects the search speed and downstream task performance [25], [28], [29], we need to encode the configurations
of each candidate architecture into the latent space before the
search phase to enhance the search efficiency, given the large
and complex search space. Formally, an encoder E is a function
that maps a set of candidate models (S, A, C) to n-dimensional
Euclidean space, i.e., E : (S, A, C) → Rn .
1) Encoder Networks: Given the heterogeneous properties
of the configuration subspaces, we design three encoder networks, each of which learns a representation for a particular
subspace. Then, we aggregate the three learned representations
into a latent space Z = {z1 , . . . , zM }, zi ∈ Rn . The proposed

search method and performance predictor will use this continuous latent space instead of the raw discrete one.
Encoder for Task-Specific Settings: To map the raw representations of S to the latent space ZS , we use the fully
connected (F C) layer. Given that the raw representations are
one-hot vectors, F C is powerful enough to learn the features
as used in standard AE because it does not require specific
dependency modeling, e.g., spatial or temporal dependency.
Hence, ZS = F CS (S).
Encoder for Architecture Configurations: To encode architecture configurations A effectively, we need an encoder that
can capture the local relationships of different hyperparameters
between layers. Therefore, we use two-dimensional convolutional (Conv) layers with max-pooling (Mpool ) followed by
an F C layer to learn the input of 3D tensors that represent
the architecture hyperparameters in candidate networks. The
latent representation for A is denoted as ZA . Thus, ZA =
F CA (Mpool (Conv(A))).
Encoder for Temporal Connectivity: Unlike current encoding
techniques that learn to represent the connection between layers
or operations, we argue that they are unsuitable for our search
space because using only layer-level representation cannot distinguish the architectures with distinct temporal connectivity
even though their performances (i.e., F1 score) are significantly
different. Hence, embedding connectivity information in the
temporal dimension into the latent space is inevitable for the
subsequent search.
As depicted in Fig. 5, we show that for identical task-specific
and architecture configurations with different temporal connectivity having significantly different performance (e.g., F1 score)

2930

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 9, NO. 4, AUGUST 2025

Fig. 6. An example of an adjacency matrix and a connection tensor for
temporal connectivity representation.

like the models in the preliminary experiments, we cannot use
only operation-level or layer-level connections to distinguish
them. Hence, we need to encode the temporal connectivity so
that the search method can correctly find a well-performing
model. We also verify this argument by running an ablation
study under this scenario in Section IV-E.
Since the temporal connectivity forms the DAG, the natural
choice for representing the connection in each encoder/decoder
of an AE could be an adjacency matrix. It is possible for
most existing NAS because the number of nodes for the entire
network is merely about 10 to 20. However, the adjacency matrix
approach faces the scalability problem as the growth rate is K 2 .
Moreover, computation-aware methods [29] have been shown
to be superior to the adjacency matrix-based structure-aware
methods. As a remedy, we propose to use a connection tensor
instead of the hefty adjacency matrix to represent the temporal
connectivity of candidate architectures, reducing the memory
usage while having the property of a computation-aware method.
The connection tensor consists of K × L c-tuple vectors, where
L is the number of layers, c is the number of possible connections
in a cell, and L × c  K. The information in each vector is a
list of negative numbers representing how far the current cell is
connected to its previous cells, both within the same layer and
between different layers. Thus, the smaller numbers indicate that
the cell computes the longer-term dependency modeling, while
the larger numbers indicate the shorter ones. This computation
information cannot be represented by the adjacency matrix
approach.
Fig. 6 illustrates an example of the proposed connection tensor
with L = 2, K = 4, and c = 4, where Li and Ct denote the i-th
layer and the t-th recurrent cell, respectively. Here, despite the
substantial space consumption, 64, the adjacency matrix only
represents the topological connection of the entire structure
without containing the type of connectivity in each value or
local relationship between cells. In contrast, the connection
tensor meaningfully describes each cell’s local connectivity and
underlying computation using position-based negative values
with a smaller space consumption, 32. Specifically, the upper
part (colored in red) indicates between-layer connectivity in
the example, while the lower part (colored in green) indicates
within-layer connectivity. Moreover, the scalability issue of the
adjacency matrix will be more intensified in practice because
K is usually large for the model to capture a long and diverse
temporal dependency. When K is increased to 100, the adjacency matrix size becomes 200 × 200 for the encoder part and
200 × 200 for the decoder part, while the connection tensor uses

only 100 × 2 × 4 to represent each part, which is 50x smaller
than the adjacency matrix representation.
Then, considering the connection tensor resembles the characteristics of multivariate time series having length K with
L × c variables, we use the T ransf ormer network [107] to
embed the temporal connectivity by capturing the dependency
of significant computation information between cells and highlighting them via the attention mechanism. The global average
pooling (Gpool ) further summarizes the learned representations
outputting ZC . Other networks, e.g., RNN or CNN, can also be
used if they are capable of learning such dependency. Hence,
ZC = Gpool (T ransf ormer(C)).
Ultimately, ZS , ZA , and ZC are concatenated and input to
a final F C layer to learn the final aggregated representation
Z. Formally, the final output of the encoder network E is Z =
F C(Concat([ZS , ZA , ZC ])).
2) Decoder Network: The decoder is a generative model
aiming at reconstructing Ŝ, Â, and Cˆ from the latent variables
Z. Specifically, its constituent is a stack of F C layers. The
final activation functions for Ŝ and Â are the row-wise softmax σ to reconstruct the one-hot choices, while for Cˆ is the
ReLU with the negative slope coefficient = 1 to reconstruct
the negative values of the connection tensor. Hence, the decoder is formulated as Ŝ = σ(F CŜ (Z)), Â = σ(F CÂ (Z)), and
Cˆ = ReLU (F CĈ (Z)).
3) Unsupervised Pre-Training: As in Fig. 2, we train the
multi-level configuration encoding model on M configurations
randomly sampled from the search space by minimizing the
ˆ 2.
reconstruction loss L = S − Ŝ2 + A − Â2 + C − C
D. Phase 2: Performance Predictor-Guided Search
Given the vast and complex search space, we need a highly
efficient search strategy. To achieve the highest efficiency possible, given a limited sample budget, this paper combines the
idea of recent work [76], [77] to search on the proposed search
space based on the learned latent space Z from the multi-level
configuration encoding. With the performance predictor P, we
reformulate (1) as
(S  , A , C  ) =

arg max P(E(S, A, C)).
  

S∈S,A∈A,C∈C

(6)

z∈Z

It is worth noting that PASTA is a predictor-agnostic framework,
so any prediction-based method can also be used. As illustrated
in Fig. 2, after pre-training the multi-level configuration autoencoder network, we use the performance predictor P to guide the
search procedure as follows.
1) Architecture-Performance Data Generation: To train the
predictor P, we first need a dataset of (architecture, performance) pairs. Unlike previous studies, we both uniformly and selectively sample (S, A, C) models from (S, A, C). We uniformly
select the models to preserve the overall structure of the search
space. The selectively sampled subset is expected to contain the
representative models for the full coverage of temporal connectivity subspace. Thus, the task-specific and architecture configurations of the representative models are fixed. For simplicity,
we denote Ntrain = {(S, A, C)1 , . . . , (S, A, C)|Ntrain | }. Here, we

TRIRAT AND LEE: PASTA: NEURAL ARCHITECTURE SEARCH FOR ANOMALY DETECTION IN MULTIVARIATE TIME SERIES

TABLE II
BENCHMARK DATASET STATISTICS

first train each model in Ntrain on the given time-series windows
Wtrain . Then, to generate the dataset for P, we validate the
trained models on Wvalid . For this purpose, we need a few
anomaly labels for Wvalid . However, unlabeled datasets can still
be supported by model transfer, as discussed in Section IV-D.
Depending on the computation resource, the models in Ntrain can
be trained using either a reduced [83] or full training scheme.
2) Search With Performance Predictor: After generating the
training data, we use the pre-trained multi-level configuration
encoder to obtain the latent space z of each model in Ntrain .
Thus, we redefine Ntrain = {z1 , . . . , z|Ntrain | }. Then, to predict the
performance of any candidate configurations in the search space,
we initially train P on Ntrain and iteratively update its parameters
with subsampled sets of predicted top-k candidates until the budget is reached. We denote the subset of candidate configurations
for evaluation during the search as Neval = {z̃1 , . . . , z̃|Neval | }.
Since we cannot predict the entire search space, the Neval is
usually a large subset of the search space (e.g., |Neval | = 104 ).
The model(s) in Neval having the highest predicted performance
by P, i.e., (S  , A , C  ), will be trained from scratch on Wtrain .
Finally, the trained model that has the best validation score on
Wvalid will be selected.
IV. EXPERIMENTS
This section presents a series of empirical studies to evaluate the effectiveness of PASTA for TSAD. The source code is
available at https://github.com/kaist-dmlab/PASTA.
A. Experimental Setup
1) Benchmark Datasets: To comprehensively evaluate the
TSAD models, we use the following public synthetic and realworld multivariate time-series benchmarks. TODS [108] is a
synthetic time-series generator based on behavior-driven taxonomy of anomalies categorized into point-global (Global), pointcontextual (Contextual), pattern-shapelet (Shapelet), patternseasonal (Seasonal), and pattern-trend (Trend). Thus, we have
5 entities from this benchmark. ASD [8] is the recently introduced application server benchmark containing 12 entities with
19 metrics of the servers’ status. PSM [12] is also a newly
introduced pooled server metrics dataset containing 1 entity
collected internally from multiple application server nodes at
eBay. SWaT [109] is the most widely-used 1-entity dataset
for TSAD collected from a real-world secure water treatment
plant. The statistics of all benchmarks are presented in Table II.
TODS is used to evaluate the detection performance on diverse
difficulties and anomaly types, while ASD, PSM, and SWaT are
used to evaluate the performance in real-world scenarios.

2931

2) Evaluation Metrics: Many problems caused by evaluation
metrics have been recently brought to attention [30], [47], [103],
[110]. We thus adopt new evaluation metrics designed for TSAD
to rigorously assess the performance. To tackle the overrating
issue, we use the enhanced time-series aware precision-recall
metrics [30] for calculating the best F1 score. For a fair comparison, we use the default hyperparameters of the evaluation
metric to evaluate all models. As it is more important to have
an excellent F1 score at a certain threshold δ in practice than to
have a generally good performance on most thresholds [40], we
report the highest F1 score of a model computed by enumerating
1K thresholds uniformly distributed from the minimum to the
maximum anomaly score over all time steps in the test set [10],
[14]. This measurement helps eliminate the effect of threshold
selection.
To increase the robustness in evaluating the model quality
under the threshold-independent setting, we adopt another set
of new metrics named Range Area Under the Curve (R_AUC)
and Volume Under the Surface (VUS) [110], considering both
the receiver operating characteristic (ROC) and precision-recall
(PR) curves. The VUS extends the mathematical model of the
R_AUC by allowing the buffer length to be varied. Hence,
R_AUC_ROC and R_AUC_PR are defined for the former, and
VUC_ROC and VUC_PR are defined for the latter.
3) Comparison Baselines: We compare the architectures discovered by PASTA with traditional methods, state-of-the-art
handcrafted DL models, and search-based approaches. For traditional methods, we include Isolation Forest (IF) [111], Local
Outlier Factor (LOF) [112], One-Class Support Vector Machine (OC-SVM) [113], Matrix Profile (MP) [114], and MERLIN [115]. For prediction-based DL models, Telemanom [6]
and GDN [36] are included, while DAGMM [116], OmniAnomaly [7], RAE-SF [11], USAD [39], RANSynCoders [12],
InterFusion [8], TranAD [42], and TimesNet [45] are included
for reconstruction-based DL models. For search-based approaches, we include random search (RS) with PASTA’s search
space and TODS-AutoML [93]. As mentioned in Section II, we
focus on finding the reconstruction-based neural architectures.
We also include random anomaly score (RA) [103] to ensure
that the results are meaningful. See supplementary material for
baseline descriptions.
B. Implementation Details
1) Multi-Level Configuration Autoencoder:
r Model Hyperparameters: We set the hyperparameters of
the multi-level configuration network as follows. For the
encoder, the number of hidden units for all F C layers is
16. The Conv filter size is 16 with 2 × 2 kernel and 3 × 3
max pooling. We use the ReLU activation function for both
F C and Conv. The T ransf ormer block has 8 attention
heads with a hidden state size of 20 and hidden units for
F C layers set to be the same size as the latent space z.
Here, the default latent space size is 32, i.e., z ∈ R32 . The
dropout rate for T ransf ormer is 0.1. For the decoder, the
number of hidden units in all F C layers is also 16, except
for the output layer.

2932

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 9, NO. 4, AUGUST 2025

r Training Hyperparameters: To train the multi-level configuration network, we first randomly sample 600K configurations from the search space, i.e., M = 600K. We use
90% of them for training and the remaining 10% are for
testing, following Yan et al. [28]. The number of training
epochs is 100. Also, we adopt early stopping with patience
10. The batch size is 32. The loss L is optimized using
Adam optimizer with initial learning rate of 0.001.
2) Performance Predictor:
r Architecture-Performance Generation: As mentioned in
Section III-D2, we use both reduced-training and fulltraining schemes to construct (architecture, performance)
pairs Ntrain with less computation time and resources. The
first 30% of the testing data is used as validation set
Wvalid . The performance scores of reduced-trained models
are further recalibrated to mitigate potential noises by
averaging the fully-trained performance scores of top-3
similar models based on their similarity scores computed
by the cosine similarity function given their embeddings.
In particular, we have fully-trained 256 models for each
benchmark covering the possible options in the temporal
connectivity subspace. For each benchmark, we get the
following numbers of models under the fixed settings.
TODS: 618, ASD: 874, SWaT: 662, and PSM: 393.
r Prediction Model: As an ensemble of predictors has shown
to be efficient for performance prediction [117], we adopt
NGBoost [118] as the default performance predictor P,
given its short training time with competitive accuracy. For
all experiments, the default model and training hyperparameters of NGBoost are used.
r Search Hyperparameters: The search budget, i.e., number
of total queries, is 200. We use half of search budget
to initialize the performance predictor. Then, similarly to
WeakNAS [77], we iteratively retrain the predictor using
extra 20 models randomly sampled from top-100 predicted
performance by P on the samples in Neval until the limit is
reached, where |Neval | = 20K. Last, models having top-5
predicted validation performance by the final predictor
are selected to be trained and validated from scratch for
final validation, following Wen et al. [76]. The model that
achieves best validation performance is selected. Notably,
the search hyperparameters can be adjusted based on the
availability of computation resources.
3) Anomaly Detection Models:
r Model Hyperparameters: All model hyperparameters of
the state-of-the-art baselines are set as suggested in their
source code or original papers. For IF, LOF, and OCSVM, we search the model hyperparameters as suggested by Shen et al. [13]. For MP, we tune the subsequence length based on the default K value within
{K/2, K/1.5, K, K × 1.5, K × 2}. For MERLIN, we
use both recommeded hyperparameters [42] and search
for minimum (minL) and maximum (maxL) values that
correspond to the discord lengths when train on the
new benchmarks. Here, minL ∈ {1, 5, 10, 20, 50, 80, 100}
and maxL ∈ {10, 20, 40, 60, 100, 140, 200}. For TODSAutoML, we select the best detection results from different

time limits ∈ {600, 7200, 10800, 21600} seconds. We use
grid search for these hyperparameter search spaces.
r Training Hyperparameters: To use less computation cost,
we train the TSAD models using the following two sets
of training hyperparameters. The first set of training hyperparameters is for full training. Here, the batch size is
32, the number of epochs is 100, and early stopping is
applied with patience 5. Regarding the second set, it is
used for reduced training. The batch size is also 32, while
the number of epochs is only 5 without early stopping.
For both cases, we use the Adam optimizer with an initial
learning rate of 0.001. Note that all the baselines and final
validation step of the selected candidate in PASTA use full
training settings, while the reduced training settings are
used for architecture-performance sample generation and
validation of candidate architectures during search.
C. Overall Performance Comparison
1) Time-Series Anomaly Detection: We report the main experimental results for TSAD averaged from three runs on different random seeds3 across different datasets in the same benchmark. The averaged performance scores and standard deviations
are reported in Table III. On average, the results clearly indicate
that models discovered by PASTA significantly outperform both
traditional approaches and state-of-the-art handcrafted detectors; specifically, it yields a detection accuracy of 13.6–545.7%
higher than the other methods. InterFusion and TimesNet are
ranked second and third, respectively.
As in recent studies [43], [119], we also compare PASTA to the
well-performing models (InterFusion and TimesNet) using the
additional metrics [110]. As presented in Table IV, the improvement in the range-AUC metrics (R_AUC_ROC or R_AUC_PR)
is up to 31.9%, while the enhancement in the VUS-based metrics
(VUS_ROC or VUS_PR) is up to 32.4%.
Overall, these results indeed demonstrate that PASTA can
adaptively find a proper architecture given the different characteristics of time-series benchmarks. We conjecture that the improvement of the detection performance is from the integration
of temporal connectivity in the proposed search space because
it enables the search process to learn how to select the proper
connections for temporal dependency modeling. Interestingly,
even models found by random search (RS) also perform better
than several state-of-the-art handcrafted models.
2) Performance Prediction: This experiment examines the
usefulness of the multi-level configuration encoding on the
performance predictor by measuring how well the (learned) representations can predict the performance of the given candidate
models because good representations can facilitate the learning
of the predictor, thereby enhancing its performance. We use 80%
of the generated (architecture, performance) pairs dataset for
training, and the results averaged across different benchmarks
are reported based on the remaining test data. Following White
et al. [81], we use RMSE, Spearman’s ρ, and Kendall’s τ rank
3 The random seed for each run is 2r , where r is the running index starting
from 0. The seed for the search phase is 7.

TRIRAT AND LEE: PASTA: NEURAL ARCHITECTURE SEARCH FOR ANOMALY DETECTION IN MULTIVARIATE TIME SERIES

2933

TABLE III
PERFORMANCE COMPARISON BETWEEN TSAD METHODS IN TERMS OF THE BEST ENHANCED TIME-SERIES AWARE F1 SCORE [30] WITH THE HIGHEST SCORES
HIGHLIGHTED IN BOLD

TABLE IV
ADDITIONAL PERFORMANCE COMPARISON FOR PASTA IN VUS [110] EVALUATION METRICS WITH THE HIGHEST SCORES HIGHLIGHTED IN BOLD

2934

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 9, NO. 4, AUGUST 2025

TABLE V
COMPARISON OF ENCODING METHODS ON PERFORMANCE PREDICTOR

TABLE VI
COMPARISON OF ENCODING METHODS UNDER THE IDENTICAL CASES

correlation to evaluate the performance predictor in overall
prediction accuracy and ranking capability.
Here, we compare the multi-level configuration encoding, PASTA, with widely-used layer-level adjacency matrix [25] and state-of-the-art unsupervised architecture encoding
arch2vec [28]. Given the identical predictor NGBoost [118] (i.e.,
P in (6)) and experimental settings, Table V shows that our
multi-level configuration encoding of PASTA both reduces the
performance prediction error and increases the ranking capability. Expectedly, learned latent representations are better than raw
adjacency matrix representation.
Besides, we also include the scenario discussed earlier in
Section III-C to confirm the necessity of temporal connectivity
encoding. The result is reported in Table VI. In both cases,
PASTA’s multi-level configuration encoding demonstrates its
usefulness in enhancing the detection accuracy prediction, having the lowest RMSE and the highest ranking correlation scores.
Notably, layer-level adjacency matrix and arch2vec cannot differentiate models with different temporal connectivity; thus,
the exact same embeddings are produced, resulting in the NaN
values when the correlation scores were computed.
D. Transferability of Found Architectures
As the lack of labels is a key challenge in TSAD, we thus
examine the transferability of the found models to test whether
the proposed PASTA is practical. Specifically, we conduct an
in-domain transfer by using 50% of labeled datasets of the
ASD benchmark (i.e., 6 out of 12 datasets) to generate the
(architecture, performance) pairs and search for a TSAD model.
Then, we use the found model for the entire benchmark and
observe that the detection performance F1 only drops by about
10% from 0.471 to 0.411, which is still comparable to and outperforms several baselines. This result shows a certain level of
PASTA’s transferability for similar application domains, thereby
mitigating the lack of labels to some extent.
E. Ablation Studies
To investigate and understand how each component in
the proposed multi-level configuration encoding affects the
downstream detection and performance prediction accuracy, we

conduct the ablation experiments with three variants: w/o taskspecific settings, w/o network configurations, and w/o temporal
connectivity. Similar to the main experiments on performance
prediction, we use 80% of the generated (architecture, performance) pairs dataset for training, and the results averaged across
different benchmarks are reported based on the remaining test
data.
Table VII shows the results of anomaly detection and performance prediction accuracy. On average, we observe that
task-specific settings and temporal connectivity information are
the most crucial to search the well-performing TSAD models.
By varying PASTA encoder’s component, we notice that the
task-specific settings and temporal connectivity information are
also the most crucial for the predictor to predict the detection performance of given TSAD models accurately, which is
well-aligned with previous findings of deep TSAD designed
by human experts. This result suggests that a suitable anomaly
scoring function, an effective layer type, and connections in the
temporal dimension of RNN-based AEs are strongly associated
with anomaly detection performance.
In addition, Fig. 7 visualizes the anomaly scores produced
by models found using different encoding variants for qualitative examination. As shown in the figure, the model found by
PASTA gives the most distinguishable anomaly scores across
all anomaly types. In contrast, the absence of either temporal
connectivity or task-specific settings significantly affects the
final downstream detection quality due to the high fluctuation of
anomaly scores, leading to more false positives. These qualitative and quantitative results substantiate that PASTA’s multi-level
configuration encoding is helpful in guiding the search process
and effective for detecting various anomaly types, especially
with the proposed search space.
F. Effects of Hyperparameters
To further examine how different hyperparameters affect the
downstream detection and performance prediction accuracy, we
conduct the following hyperparameter studies. Unlike the main
ablation study on multi-level configuration encoding, we do not
conduct the experiments for all datasets through the entire NAS
process not only due to the unduly intensive computation cost,
but it is also clear that the subsequent search process relies on the
performance predictor, meaning that a well-performing predictor will lead to better downstream detection results (small-scaled
results are also reported below).
1) Effect of Search Strategy: Since the search strategy can
also affect downstream performance, we compare PASTA’s
variants in terms of the search strategy. As in Fig. 8(a), on
average, it is evident that combining the advantages of Neural
Predictor (NP) [76] and WeakNAS [77] achieves better results
given the same search budget of 100 samples. Here, we speculate
that NP provides high-quality results of performance prediction;
at the same time, WeakNAS provides a diversity of candidate
architectures.
2) Effect of Sample Budget: This experiment investigates
how the search budget or the number of total queries affects
the final detection performance. Although Fig. 8(b) shows that a
higher search budget gives better average detection performance,

TRIRAT AND LEE: PASTA: NEURAL ARCHITECTURE SEARCH FOR ANOMALY DETECTION IN MULTIVARIATE TIME SERIES

2935

TABLE VII
ABLATION STUDY ON MULTI-LEVEL CONFIGURATION ENCODING COMPONENTS FOR PASTA WITH THE BEST SCORES HIGHLIGHTED IN BOLD

Fig. 7. Original time-series subsequences (first row) with ground-truth anomaly regions highlighted in red and anomaly scores produced by models discovered
via each encoding method for different anomaly types from the TODS benchmark. Predicted anomalies of each model are highlighted in blue, corresponding to its
threshold marked by the red dashed line.

TABLE IX
PREDICTOR ACCURACY BY VARYING THE LATENT SPACE SIZE OF E

Fig. 8. Comparison of F1 score [30] given different search methods and
budgets on the first dataset (due to the computational cost) of each benchmark.

TABLE VIII
PREDICTION ACCURACY BY DIFFERENT ARCHITECTURE OF E

a lower search budget can still produce good detection results
for some datasets. This probably indicates the sample efficiency
of PASTA.
3) Effect of Encoder Architecture: In this experiment, we
show that the heterogeneity of each subspace needs a proper
encoder network. From Table VIII, it is apparent that combining
diverse types of layers is beneficial for modeling heterogeneous
search space because using only fully-connected (F C) layers is
not sufficient to capture the different properties of each subspace.
Similarly, a simple combination with only recurrent (RN N ,
LST M , or GRU ), convolutional (Conv), or T ransf ormer
block is not enough or even deteriorates the prediction accuracy.
Moreover, we also test PASTA with variational loss (VAE) as

used in arch2vec. Still, PASTA with simple reconstruction loss
performs best.
4) Effect of Latent Space Size: In this experiment, we vary
the size of latent space Z to examine how it affects the predictor
accuracy. While there are slight differences between latent space
sizes, as presented in Table IX, we can observe that 32 is the
optimal size for our search space using multi-level configuration
encoding. Thus, we use it as the default value to pre-train the
multi-level configuration encoding for selected samples during
the search phase.
5) Effect of Predictor Choice: According to a recent
study [117], ensemble models are good at predicting the accuracy of architectures in search spaces. However, there are various
choices in the research community. Here, we vary the different
ensemble models to find the best one in terms of prediction
accuracy and speed. Evidently, natural gradient boosting (NGB)
is the most appropriate model, while extreme gradient boosting (XGB) and light gradient boosting (LGB) are too slow. The
faster models are ensembles of multi-layer perceptron (MLP)
based on the Bagging or AdaBoost method, yet their accuracy
is not strong enough to guide the search. The results are shown
in Table X.
G. Time Complexity
This subsection reports the computation costs used for the
entire NAS process. Although we cannot quantify the exact

2936

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 9, NO. 4, AUGUST 2025

TABLE X
PREDICTION ACCURACY BY DIFFERENT PREDICTORS

TABLE XIV
COMPARISON OF TRAINING TIME AVERAGED FROM THREE RUNS BETWEEN
THE BASELINE MODELS AND MODELS FOUND BY PASTA IN GPU HOURS

TABLE XI
COMPUTATION COSTS USED FOR EACH BENCHMARK

TABLE XII
COMPARISON OF AVERAGE TRAINING TIME IN GPU SECONDS PER EPOCH BY
VARYING ENCODING METHODS WITH THE LATENT SPACE SIZE OF 32

though with higher detection performance. Thus, future work
that jointly optimizes (like Pareto front) both performance and
computational complexity during the search phase will be a very
promising research direction.
V. CONCLUSION

TABLE XIII
COMPARISON OF AVERAGE TRAINING TIME IN GPU SECONDS PER EPOCH BY
VARYING ENCODER NETWORKS WITH THE LATENT SPACE SIZE OF 32

amount of time used for architecture-performance data generation, approximately, we use a month to generate the number of models mentioned earlier. Note that the architectureperformance data generation and multi-level configuration encoder pre-training are the one-time cost.
Concerning the actual computation during the search process,
Table XI shows the distribution of time in GPU hours used from
the search phase to the training time of the final candidate model.
The validation time is averaged from top-k models (i.e., 5in our
setting), while the training time is averaged from three runs. It
is worth noting that the computation cost mostly depends on the
dataset size and the complexity of the models selected during
the search phase.
Table XII shows the training time between different encoder
inputs, and Table XIII compares the training time depending on
encoder architectures. Finally, Table XIV presents the comparison of training time between state-of-the-art handcrafted baseline models and PASTA. According to these computation costs, it
is noticeable that PASTA relatively has high computational cost

This paper proposes PASTA, a prediction-based neural architecture search for multivariate time-series anomaly detection.
PASTA consists of a well-tailored search space, multi-level configuration encoding with a novel temporal connectivity encoding
between recurrent cells, and an efficient predictor-guided search.
With rigorous experiments, we verify that the models discovered
by PASTA show their superiority for detecting anomalies in
multivariate time series by improving the enhanced time-series
aware F1 score by at least 13.6% on average with the help
of multi-level configuration encoding. We also expect that our
work will facilitate researchers and practitioners in discovering
new deep TSAD models for the emerging time-series data using
fewer computation resources and human efforts.
REFERENCES
[1] A. J. Fox, “Outliers in time series,” J. Roy. Stat. Soc. Ser. B: Stat.
Methodol., vol. 34, no. 3, pp. 350–363, 1972.
[2] M. Gupta, J. Gao, C. C. Aggarwal, and J. Han, “Outlier detection for
temporal data: A survey,” IEEE Trans. Knowl. Data Eng., vol. 26, no. 9,
pp. 2250–2267, Sep. 2014.
[3] A. Blázquez-García, A. Conde, U. Mori, and J. A. Lozano, “A review
on outlier/anomaly detection in time series data,” ACM Comput. Surv.,
vol. 54, no. 3, pp. 1–33, 2021.
[4] K. Choi, J. Yi, C. Park, and S. Yoon, “Deep learning for anomaly detection
in time-series data: Review, analysis, and guidelines,” IEEE Access,
vol. 9, pp. 120043–120065, 2021.
[5] Y. Luo, Y. Xiao, L. Cheng, G. Peng, and D. Yao, “Deep learning-based
anomaly detection in cyber-physical systems: Progress and opportunities,” ACM Comput. Surv., vol. 54, no. 5, pp. 1–36, 2021.
[6] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom,
“Detecting spacecraft anomalies using LSTMs and nonparametric dynamic thresholding,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov.
Data Mining, 2018, pp. 387–395.
[7] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining,
2019, pp. 2828–2837.

TRIRAT AND LEE: PASTA: NEURAL ARCHITECTURE SEARCH FOR ANOMALY DETECTION IN MULTIVARIATE TIME SERIES

[8] Z. Li et al., “Multivariate time series anomaly detection and interpretation
using hierarchical inter-metric and temporal embedding,” in Proc. ACM
SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2021, pp. 3220–3230.
[9] W. Chen, L. Tian, B. Chen, L. Dai, Z. Duan, and M. Zhou, “Deep
variational graph convolutional recurrent network for multivariate time
series anomaly detection,” in Proc. Int. Conf. Mach. Learn., 2022,
pp. 3621–3633.
[10] Y. Nam, P. Trirat, T. Kim, Y. Lee, and J.-G. Lee, “Context-aware deep
time-series decomposition for anomaly detection in businesses,” in Proc.
Joint Eur. Conf. Mach. Learn. Knowl. Discov. Databases, 2023, pp. 330–
345.
[11] T. Kieu, B. Yang, C. Guo, and C. S. Jensen, “Outlier detection for time
series with recurrent autoencoder ensembles,” in Proc. Int. Joint Conf.
Artif. Intell., 2019, pp. 2725–2732.
[12] A. Abdulaal, Z. Liu, and T. Lancewicki, “Practical approach to asynchronous multivariate time series anomaly detection and localization,”
in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2021,
pp. 2485–2494.
[13] L. Shen, Z. Li, and J. Kwok, “Timeseries anomaly detection using
temporal hierarchical one-class network,” in Proc. Annu. Conf. Neural
Inf. Process. Syst., 2020, pp. 13016–13026.
[14] L. Shen, Z. Yu, Q. Ma, and J. T. Kwok, “Time series anomaly detection
with multiresolution ensemble decoding,” in Proc. AAAI Conf. Artif.
Intell., 2021, pp. 9567–9575.
[15] L. Qingning et al., “Multi-scale anomaly detection for time series with
attention-based recurrent autoencoders,” in Proc. Asian Conf. Mach.
Learn., 2023, pp. 674–689.
[16] T. Elsken, J. H. Metzen, and F. Hutter, “Neural architecture search:
A survey,” J. Mach. Learn. Res., vol. 20, no. 1, pp. 1997–2017,
2019.
[17] H. Rakhshani et al., “Neural architecture search for time series classification,” in Proc. Int. Joint Conf. Neural Netw., 2020, pp. 1–8.
[18] Z. Xiao, X. Xu, H. Xing, R. Qu, F. Song, and B. Zhao, “RNTS: Robust
neural temporal search for time series classification,” in Proc. Int. Joint
Conf. Neural Netw., 2021, pp. 1–8.
[19] Y. Ren, L. Li, X. Yang, and J. Zhou, “AutoTransformer: Automatic
transformer architecture design for time series classification,” in Proc.
Pacific-Asia Conf. Knowl. Discov. Data Mining, 2022, pp. 143–155.
[20] X. Wu, D. Zhang, C. Guo, C. He, B. Yang, and C. S. Jensen, “AutoCTS: Automated correlated time series forecasting,” VLDB Endowment, vol. 15, no. 4, pp. 971–983, 2021.
[21] D. Deng, F. Karl, F. Hutter, B. Bischl, and M. Lindauer, “Efficient
automated deep learning for time series forecasting,” in Proc. Joint Eur.
Conf. Mach. Learn. Knowl. Discov. Databases, 2022, pp. 664–680.
[22] Z. Lai, D. Zhang, H. Li, C. S. Jensen, H. Lu, and Y. Zhao, “LightCTS:
A lightweight framework for correlated time series forecasting,” in Proc.
ACM Manage. Data, 2023, pp. 1–26.
[23] Y. Mehta et al., “NAS-bench-suite: NAS evaluation is (now) surprisingly
easy,” in Proc. Int. Conf. Learn. Representations, 2022.
[24] A. Garg, W. Zhang, J. Samaran, R. Savitha, and C.-S. Foo, “An evaluation
of anomaly detection and diagnosis in multivariate time series,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2508–2517, Jun. 2022.
[25] C. White, W. Neiswanger, S. Nolen, and Y. Savani, “A study on encodings
for neural architecture search,” in Proc. Annu. Conf. Neural Inf. Process.
Syst., 2020, pp. 20309–20319.
[26] C. White et al., “Neural architecture search: Insights from 1000 papers,”
2023, arXiv:2301.08727.
[27] Y.-H. Yoo, U.-H. Kim, and J.-H. Kim, “Recurrent reconstructive network
for sequential anomaly detection,” IEEE Trans. Cybern., vol. 51, no. 3,
pp. 1704–1715, Mar. 2021.
[28] S. Yan, Y. Zheng, W. Ao, X. Zeng, and M. Zhang, “Does unsupervised
architecture representation learning help neural architecture search?,” in
Proc. Annu. Conf. Neural Inf. Process. Syst., 2020, pp. 12486–12498.
[29] S. Yan, K. Song, F. Liu, and M. Zhang, “CATE: Computation-aware
neural architecture encoding with transformers,” in Proc. Int. Conf. Mach.
Learn., 2021, pp. 11670–11681.
[30] W.-S. Hwang, J.-H. Yun, J. Kim, and B. G. Min, “Do you know existing
accuracy metrics overrate time-series anomaly detections?,” in Proc. 37th
ACM/SIGAPP Symp. Appl. Comput., 2022, pp. 403–412.
[31] M. Braei and S. Wagner, “Anomaly detection in univariate time-series:
A survey on the state-of-the-art,” 2020, arXiv:2004.00433.
[32] S. Schmidl, P. Wenig, and T. Papenbrock, “Anomaly detection in time
series: A comprehensive evaluation,” VLDB Endowment, vol. 15, no. 9,
pp. 1779–1797, 2022.

2937

[33] Z. Z. Darban, G. I. Webb, S. Pan, C. C. Aggarwal, and M. Salehi, “Deep
learning for time series anomaly detection: A survey,” ACM Comput.
Surv., vol. 57, no. 1, Oct. 2024, Art. No. 15.
[34] H. Si et al., “Timeseriesbench: An industrial-grade benchmark for time
series anomaly detection models,” in Proc. IEEE Int. Symp. Softw. Rel.
Eng., 2024.
[35] H. Zhao et al., “Multivariate time-series anomaly detection via graph
attention network,” in Proc. IEEE Int. Conf. Data Mining, 2020, pp. 841–
850.
[36] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 4027–4035.
[37] P. Malhotra, A. Ramakrishnan, G. Anand, L. Vig, P. Agarwal, and G.
Shroff, “LSTM-based encoder-decoder for multi-sensor anomaly detection,” in Proc. ICML Anomaly Detection Workshop, 2016.
[38] H. Xu et al., “Unsupervised anomaly detection via variational autoencoder for seasonal KPIs in web applications,” in Proc. 2018 World
Wide Web Conf., 2018, pp. 187–196.
[39] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,”
in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 3395–3404.
[40] C. Feng and P. Tian, “Time series anomaly detection for cyber-physical
systems via neural system identification and Bayesian filtering,” in
Proc. 27th ACM SIGKDD Conf. Knowl. Discov. & Data Mining, 2021,
pp. 2858–2867.
[41] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly Transformer: Time
series anomaly detection with association discrepancy,” in Proc. Int. Conf.
Learn. Representations, 2022.
[42] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” VLDB
Endow., vol. 15, pp. 1201–1214, 2022.
[43] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “Dcdetector: Dual
attention contrastive representation learning for time series anomaly detection,” in Proc. ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining,
2023, pp. 3033–3045.
[44] Y. Li, W. Chen, B. Chen, D. Wang, L. Tian, and M. Zhou, “Prototypeoriented unsupervised anomaly detection for multivariate time series,” in
Proc. Int. Conf. Mach. Learn., 2023, pp. 19407–19424.
[45] H. Wu, T. Hu, Y. Liu, H. Zhou, J. Wang, and M. Long, “TimesNet:
Temporal 2d-variation modeling for general time series analysis,” in Proc.
Int. Conf. Learn. Representations, 2023, pp. 1–23.
[46] I. U. Haq and B. S. Lee, “TransNAS-TSAD: Harnessing transformers
for multi-objective neural architecture search in time series anomaly
detection,” 2023, arXiv:2311.18061.
[47] R. Ghorbani, M. J. Reinders, and D. M. Tax, “PATE: Proximity-aware
time series anomaly evaluation,” in Proc. ACM SIGKDD Int. Conf.
Knowl. Discov. Data Mining, 2024, pp. 872–883.
[48] E. Galván and P. Mooney, “Neuroevolution in deep neural networks:
Current trends and future challenges,” IEEE Trans. Artif. Intell., vol. 2,
no. 6, pp. 476–493, Dec. 2021.
[49] M. Tenorio and W.-T. Lee, “Self organizing neural networks for the
identification problem,” in Proc. Annu. Conf. Neural Inf. Process. Syst.,
1988, pp. 57–64.
[50] B. Zoph and Q. V. Le, “Neural architecture search with reinforcement
learning,” in Proc. Int. Conf. Learn. Representations, 2017.
[51] B. Baker, O. Gupta, N. Naik, and R. Raskar, “Designing neural network
architectures using reinforcement learning,” in Proc. Int. Conf. Learn.
Representations, 2017.
[52] C. Ying, A. Klein, E. Christiansen, E. Real, K. Murphy, and F. Hutter,
“NAS-Bench-101: Towards reproducible neural architecture search,” in
Proc. Int. Conf. Mach. Learn., 2019, pp. 7105–7114.
[53] X. Dong and Y. Yang, “NAS-Bench-201: Extending the scope of reproducible neural architecture search,” in Proc. Int. Conf. Learn. Representations, 2020.
[54] H. Liu, K. Simonyan, and Y. Yang, “DARTS: Differentiable architecture
search,” in Proc. Int. Conf. Learn. Representations, 2018.
[55] H. Pham, M. Guan, B. Zoph, Q. Le, and J. Dean, “Efficient neural
architecture search via parameters sharing,” in Proc. Int. Conf. Mach.
Learn., 2018, pp. 4095–4104.
[56] D. Dimanov, E. Balaguer-Ballester, C. Singleton, and S. Rostami, “MONCAE: Multi-objective neuroevolution of convolutional autoencoders,” in
Proc. ICLR Workshop Neural Architecture Search, 2021.

2938

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 9, NO. 4, AUGUST 2025

[57] B. Wu et al., “FBNet: Hardware-aware efficient convnet design via differentiable neural architecture search,” in Proc. IEEE/CVF Conf. Comput.
Vis. Pattern Recognit., 2019, pp. 10726–10734.
[58] A. Howard et al., “Searching for MobileNetV3,” in Proc. IEEE/CVF Int.
Conf. Comput. Vis., 2019, pp. 1314–1324.
[59] Y. Wang et al., “TextNAS: A neural architecture search space tailored for
text representation,” in Proc. AAAI Conf. Artif. Intell., 2020, pp. 9242–
9249.
[60] T. Li, J. Zhang, K. Bao, Y. Liang, Y. Li, and Y. Zheng, “AutoST: Efficient
neural architecture search for spatio-temporal prediction,” in Proc. ACM
SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020, pp. 794–802.
[61] Z. Pan et al., “AutoSTG: Neural architecture search for predictions of
spatio-temporal graph,” in Proc. Web Conf., 2021, pp. 1846–1855.
[62] R. Jie and J. Gao, “Differentiable neural architecture search for
high-dimensional time series forecasting,” IEEE Access, vol. 9,
pp. 20922–20932, 2021.
[63] N. Klyuchnikov et al., “NAS-bench-NLP: Neural architecture search
benchmark for natural language processing,” IEEE Access, vol. 10,
pp. 45736–45747, 2022.
[64] Y. Fan, F. Tian, Y. Xia, T. Qin, X.-Y. Li, and T.-Y. Liu, “Searching better
architectures for neural machine translation,” IEEE/ACM Trans. Audio,
Speech, Lang. Process., vol. 28, pp. 1574–1585, 2020.
[65] J. Xu et al., “NAS-BERT: Task-agnostic and adaptive-size bert compression with neural architecture search,” in Proc. ACM SIGKDD Int. Conf.
Knowl. Discov. Data Mining, 2021, pp. 1933–1943.
[66] M. Ding et al., “HR-NAS: Searching efficient high-resolution neural
architectures with lightweight transformers,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2021, pp. 2981–2991.
[67] D. So, W. Mańke, H. Liu, Z. Dai, N. Shazeer, and Q. V. Le, “Primer:
Searching for efficient transformers for language modeling,” in Proc.
Annu. Conf. Neural Inf. Process. Syst., 2021, pp. 6010–6022.
[68] Y. Li et al., “Automated anomaly detection via curiosity-guided search
and self-imitation learning,” IEEE Trans. Neural Netw. Learn. Syst.,
vol. 33, no. 6, pp. 2365–2377, Jun. 2022.
[69] E. Real, A. Aggarwal, Y. Huang, and Q. V. Le, “Regularized evolution for
image classifier architecture search,” in Proc. AAAI Conf. Artif. Intell.,
2019, pp. 4780–4789.
[70] X. Chen, Y. Sun, M. Zhang, and D. Peng, “Evolving deep convolutional
variational autoencoders for image classification,” IEEE Trans. Evol.
Computation, vol. 25, no. 5, pp. 815–829, Oct. 2021.
[71] R. Luo, F. Tian, T. Qin, E. Chen, and T.-Y. Liu, “Neural architecture
optimization,” in Proc. Annu. Conf. Neural Inf. Process. Syst., 2018,
pp. 7816–7827.
[72] H. Peng, H. Du, H. Yu, Q. Li, J. Liao, and J. Fu, “Cream of the crop:
Distilling prioritized paths for one-shot neural architecture search,” in
Proc. Annu. Conf. Neural Inf. Process. Syst., 2020, pp. 17955–17964.
[73] H. Zhou, M. Yang, J. Wang, and W. Pan, “BayesNAS: A Bayesian
approach for neural architecture search,” in Proc. Int. Conf. Mach. Learn.,
2019, pp. 7603–7613.
[74] H. Shi, R. Pi, H. Xu, Z. Li, J. Kwok, and T. Zhang, “Bridging the
gap between sample-based and one-shot neural architecture search with
BONAS,” in Proc. Annu. Conf. Neural Inf. Process. Syst., 2020, pp. 1808–
1819.
[75] C. White, W. Neiswanger, and Y. Savani, “BANANAS: Bayesian optimization with neural architectures for neural architecture search,” in
Proc. AAAI Conf. Artif. Intell., 2021, pp. 10293–10301.
[76] W. Wen, H. Liu, Y. Chen, H. Li, G. Bender, and P.-J. Kindermans, “Neural
predictor for neural architecture search,” in Proc. Eur. Conf. Comput. Vis.,
2020, pp. 660–676.
[77] J. Wu et al., “Stronger NAS with weaker predictors,” in Proc. Annu. Conf.
Neural Inf. Process. Syst., 2021, pp. 28904–28918.
[78] X. Ning, Y. Zheng, T. Zhao, Y. Wang, and H. Yang, “A generic graphbased neural architecture encoding scheme for predictor-based NAS,” in
Proc. Eur. Conf. Comput. Vis., 2020, pp. 189–204.
[79] C. Wei, C. Niu, Y. Tang, and J. Liang, “NPENAS: Neural predictor
guided evolution for neural architecture search,” IEEE Trans. Neural
Netw. Learn. Syst., vol. 34, no. 11, pp. 8441–8455, Nov. 2023.
[80] L. Dudziak, T. C. P. Chau, M. S. Abdelfattah, R. Lee, H. Kim, and N. D.
Lane, “BRP-NAS: Prediction-based NAS using GCNs,” in Proc. Annu.
Conf. Neural Inf. Process. Syst., 2020, pp. 10480–10490.
[81] C. White, A. Zela, R. Ru, Y. Liu, and F. Hutter, “How powerful are
performance predictors in neural architecture search?,” in Proc. Annu.
Conf. Neural Inf. Process. Syst., 2021, pp. 28454–28469.
[82] B. Zoph, V. Vasudevan, J. Shlens, and Q. V. Le, “Learning transferable
architectures for scalable image recognition,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2018, pp. 8697–8710.

[83] D. Zhou et al., “EcoNAS: Finding proxies for economical neural architecture search,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit.,
2020, pp. 11393–11401.
[84] L. Li and A. Talwalkar, “Random search and reproducibility for
neural architecture search,” in Proc. Uncertainty Artif. Intell., 2020,
pp. 367–377.
[85] X. Gong, S. Chang, Y. Jiang, and Z. Wang, “AutoGAN: Neural architecture search for generative adversarial networks,” in Proc. IEEE/CVF Int.
Conf. Comput. Vis., 2019, pp. 3223–3233.
[86] C. Gao, Y. Chen, S. Liu, Z. Tan, and S. Yan, “AdversarialNAS: Adversarial neural architecture search for GANs,” in Proc. IEEE/CVF Conf.
Comput. Vis. Pattern Recognit., 2020, pp. 5679–5688.
[87] T. Mo and B. Liu, “Encoder-decoder neural architecture optimization for
keyword spotting,” 2021, arXiv:2106.02738.
[88] P. Esling and C. Agon, “Time-series data mining,” ACM Comput. Surv.,
vol. 45, no. 1, pp. 1–34, 2012.
[89] S. Y. Shah et al., “AutoAI-TS: AutoAI for time series forecasting,” in
Proc. 2021 Int. Conf. Manage. Data, 2021, pp. 2584–2596.
[90] A. D. Kini, S. S. Yadav, A. S. Thakur, A. B. Awari, Z. Lyu, and T. Desell,
“Co-evolving recurrent neural networks and their hyperparameters with
simplex hyperparameter optimization,” in Proc. Companion Conf. Genet.
Evol. Computation, 2023, pp. 1639–1647.
[91] P. Arora, S. M. J. Jalali, S. Ahmadian, B. K. Panigrahi, P. N. Suganthan,
and A. Khosravi, “Probabilistic wind power forecasting using optimized
deep auto-regressive recurrent neural networks,” IEEE Trans. Ind. Informat., vol. 19, no. 3, pp. 2814–2825, Mar. 2023.
[92] B. B. Moser, F. Raue, J. Hees, and A. Dengel, “DartsReNet: Exploring
new RNN cells in ReNet architectures,” in Proc. Artif. Neural Netw.
Mach. Learn.–ICANN 2020: 29th Int. Conf. Artif. Neural Netw., Proc.,
Part I. 29., Bratislava, Slovakia, Sep. 15–18, 2020, pp. 850–861.
[93] K.-H. Lai et al., “TODS: An automated time series outlier detection
system,” in Proc. AAAI Conf. Artif. Intell., 2021, pp. 16060–16062.
[94] M. Goswami, C. I. Challu, L. Callot, L. Minorics, and A. Kan, “Unsupervised model selection for time series anomaly detection,” in Proc. Int.
Conf. Learn. Representations, 2023.
[95] Y. Liu, Y. Sun, B. Xue, M. Zhang, G. G. Yen, and K. C. Tan, “A survey
on evolutionary neural architecture search,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 34, no. 2, pp. 550–570, Feb. 2023.
[96] E.-G. Talbi, “Automated design of deep neural networks: A survey
and unified taxonomy,” ACM Comput. Surv., vol. 54, no. 2, pp. 1–37,
2021.
[97] P. Ren et al., “A comprehensive survey of neural architecture search:
Challenges and solutions,” ACM Comput. Surv., vol. 54, no. 4, pp. 1–34,
2021.
[98] L. Wang, Y. Zhao, Y. Jinnai, Y. Tian, and R. Fonseca, “Neural architecture
search using deep neural networks and Monte Carlo tree search,” in Proc.
AAAI Conf. Artif. Intell., 2020, pp. 9983–9991.
[99] H. Cheng et al., “NASGEM: Neural architecture search via graph
embedding method,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 7090–7098.
[100] K. Jing, J. Xu, and P. Li, “Graph masked autoencoder enhanced predictor
for neural architecture search,” in Proc. Int. Joint Conf. Artif. Intell., 2022,
pp. 3114–3120.
[101] M. Zhang, S. Jiang, Z. Cui, R. Garnett, and Y. Chen, “D-VAE: A
variational autoencoder for directed acyclic graphs,” in Proc. Annu. Conf.
Neural Inf. Process. Syst., 2019, pp. 1586–1598.
[102] C. Wei, Y. Tang, C. Niu, H. Hu, Y. Wang, and J. Liang, “Self-supervised
representation learning for evolutionary neural architecture search,” IEEE
Comput. Intell. Mag., vol. 16, no. 3, pp. 33–49, Aug. 2021.
[103] S. Kim, K. Choi, H.-S. Choi, B. Lee, and S. Yoon, “Towards a rigorous
evaluation of time-series anomaly detection,” in Proc. AAAI Conf. Artif.
Intell., 2022, pp. 7194–7201.
[104] B. Horne and C. Giles, “An experimental comparison of recurrent neural
networks,” in Proc. Annu. Conf. Neural Inf. Process. Syst., 1994, pp. 697–
704.
[105] S. Hochreiter and J. Schmidhuber, “Long short-term memory,” Neural
Computation, vol. 9, no. 8, pp. 1735–1780, 1997.
[106] K. Cho et al., “Learning phrase representations using RNN encoderdecoder for statistical machine translation,” in Proc. Conf. Empirical
Methods Natural Lang. Process., 2014, pp.1724–1734.
[107] A. Vaswani et al., “Attention is all you need,” in Proc. Annu. Conf. Neural
Inf. Process. Syst., 2017, pp. 5998–6008.
[108] K.-H. Lai, D. Zha, J. Xu, Y. Zhao, G. Wang, and X. Hu, “Revisiting time
series outlier detection: Definitions and benchmarks,” in Proc. Annu.
Conf. Neural Inf. Process. Syst., 2021.

TRIRAT AND LEE: PASTA: NEURAL ARCHITECTURE SEARCH FOR ANOMALY DETECTION IN MULTIVARIATE TIME SERIES

[109] J. Goh, S. Adepu, K. N. Junejo, and A. Mathur, “A dataset to support
research in the design of secure water treatment systems,” in Proc. Crit.
Inf. Infrastructures Secur., 2016, pp. 88–99.
[110] J. Paparrizos, P. Boniol, T. Palpanas, R. S. Tsay, A. Elmore, and M. J.
Franklin, “Volume under the surface: A new accuracy evaluation measure
for time-series anomaly detection,” VLDB Endowment, vol. 15, no. 11,
pp. 2774–2787, 2022.
[111] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. IEEE
Int. Conf. Data Mining, 2008, pp. 413–422.
[112] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” in Proc. 2000 ACM SIGMOD Int. Conf.
Manage. Data, 2000, pp. 93–104.
[113] B. Schölkopf, R. C. Williamson, A. Smola, J. Shawe-Taylor, and J. Platt,
“Support vector method for novelty detection,” in Proc. Annu. Conf.
Neural Inf. Process. Syst., 1999, pp. 582–588.
[114] C.-C. M. Yeh et al., “Matrix profile I: All pairs similarity joins for time
series: A unifying view that includes motifs, discords and shapelets,” in
Proc. IEEE Int. Conf. Data Mining, 2016, pp. 1317–1322.
[115] T. Nakamura, M. Imamura, R. Mercer, and E. Keogh, “MERLIN:
Parameter-free discovery of arbitrary length anomalies in massive time
series archives,” in Proc. IEEE Int. Conf. Data Mining, 2020, pp. 1190–
1195.
[116] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Representations,
2018, pp. 1190–1195.
[117] S. Yan, C. White, Y. Savani, and F. Hutter, “NAS-Bench-X11 and the
power of learning curves,” in Proc. Annu. Conf. Neural Inf. Process.
Syst., 2021, pp. 22534–22549.
[118] T. Duan et al., “NGBoost: Natural gradient boosting for probabilistic
prediction,” in Proc. Int. Conf. Mach. Learn., 2020, pp. 2690–2700.
[119] Y. Nam et al., “Breaking the time-frequency granularity discrepancy in
time-series anomaly detection,” in Proc. 2018 World Wide Web Conf.,
2024, pp. 4204–4215.

2939

Patara Trirat (Member, IEEE) received the B.S. degree in computer science from Kasetsart University,
Bangkok, Thailand, in 2016, and the M.S. degree in
knowledge service engineering from Korea Advanced
Institute of Science and Technology, Daejeon, South
Korea, in 2020, where he is currently working toward
the Ph.D. degree with the school of computing. His
research interests include data mining and analysis,
automated machine learning, and applied artificial
intelligence.

Jae-Gil Lee (Senior Member, IEEE) received the
B.S., M.S., and Ph.D. degrees in computer science from Korea Advanced Institute of Science and
Technology (KAIST), Daejeon, South Korea. He is
a Professor with KAIST and is leading the Data
Mining Lab. Previously, he was a Postdoctoral Researcher with the IBM Almaden Research Center
and a Postdoc Research Associate with the University of Illinois Urbana-Champaign, Champaign, IL,
USA. His research interests include data-centric AI,
deep learning-based Big Data analysis, mobility and
stream data mining, and large-scale distributed deep learning.
PAPER_TEXT
