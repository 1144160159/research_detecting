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
# [201] Coupled Attention Networks for Multivariate Time Series Anomaly Detection
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
编号：201
题名：Coupled Attention Networks for Multivariate Time Series Anomaly Detection
年份：2023
DOI：10.1109/tetc.2023.3280577
来源：IEEE Transactions on Emerging Topics in Computing
PDF：paper/10.1109_TETC.2023.3280577.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\201.txt
- 原始字符数：70704
- 本次发送字符数：70704
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
240

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTING, VOL. 12, NO. 1, JANUARY-MARCH 2024

Coupled Attention Networks for Multivariate
Time Series Anomaly Detection
Feng Xia , Senior Member, IEEE, Xin Chen , Shuo Yu , Member, IEEE, Mingliang Hou , Mujie Liu ,
and Linlin You , Member, IEEE

Abstract—Multivariate time series anomaly detection
(MTAD) plays a vital role in a wide variety of real-world
application domains. Over the past few years, MTAD
has attracted rapidly increasing attention from both
academia and industry. Many deep learning and graph
learning models have been developed for effective anomaly
detection in multivariate time series data, which enable
advanced applications such as smart surveillance and risk
management with unprecedented capabilities. Nevertheless, MTAD is facing critical challenges deriving from the
dependencies among sensors and variables, which often
change over time. To address this issue, we propose a
coupled attention-based neural network framework (CAN)
for anomaly detection in multivariate time series data
featuring dynamic variable relationships. We combine
adaptive graph learning methods with graph attention
to generate a global-local graph that can represent both
global correlations and dynamic local correlations among
sensors. To capture inter-sensor relationships and temporal dependencies, a convolutional neural network based
on the global-local graph is integrated with a temporal
self-attention module to construct a coupled attention
module. In addition, we develop a multilevel encoderdecoder architecture that accommodates reconstruction
and prediction tasks to better characterize multivariate time
series data. Extensive experiments on real-world datasets
have been conducted to evaluate the performance of the
proposed CAN approach, and the results show that CAN
significantly outperforms state-of-the-art baselines.
Index Terms—Anomaly detection, multivariate time series, graph learning, graph attention networks.

Manuscript received 14 July 2022; revised 8 May 2023; accepted 21
May 2023. Date of publication 2 June 2023; date of current version 15
March 2024. This work was partially supported by the National Natural
Science Foundation of China under Grant 62102060 and in part by the
Fundamental Research Funds for the Central Universities under Grant
DUT22RC(3)060. (Corresponding author: Shuo Yu.)
Feng Xia is with the School of Computing Technologies, RMIT University, Melbourne, VIC 3000, Australia (e-mail: f.xia@ieee.org).
Xin Chen and Mingliang Hou are with the School of Software,
Dalian University of Technology, Dalian 116620, China (e-mail: xin.chen.
jx@outlook.com; teemohold@outlook.com).
Shuo Yu is with the School of Computer Science and Technology,
Dalian University of Technology, Dalian 116024, China (e-mail: shuo.
yu@ieee.org).
Mujie Liu is with the Institute of Innovation, Science and Sustainability,
Federation University Australia, Ballarat, VIC 3353, Australia (e-mail:
mujie.liu@ieee.org).
Linlin You is with the School of Intelligent Systems Engineering,
Sun Yat-Sen University, Guangzhou 510275, China (e-mail: youllin@
mail.sysu.edu.cn).
Digital Object Identifier 10.1109/TETC.2023.3280577

I. INTRODUCTION
ENSORS of various types have been deployed in the real
world to perceive the state of entities or systems. The prevalence of smart sensors has enabled advanced infrastructures
such as the Internet of Things (IoT) and cyber-physical systems
(CPS), which in turn have led to a technological revolution
in many domains, including smart cities, automated factories,
digital twins, public security, self-driving vehicles, and epidemic disease control. With increased sensing, computing, and
communication capabilities, smart sensors continue to generate
large amounts of time series data in many real-world systems.
Detecting various anomalies in these time series data in an
automatic and timely manner is critical to intelligent systems
and services [1]. Over these years, a great number of machine
learning models and algorithms have been developed to fulfill
this demand [2]. For instance, many researchers [3], [4] have
made use of deep learning and/or graph learning to achieve
real-time and accurate anomaly detection.
Despite significant advancements in deep anomaly detection,
multivariate time series data, which have become ubiquitous
due to the use of a large number of smart sensors, cause
unprecedented challenges for anomaly detection [5], [6], [7].
In systems that feature multivariate time series data, traditional anomaly detection methods might become inapplicable
due to their inability to address multidimensional data and
complex/temporal relationships. As a consequence, multivariate time series anomaly detection (MTAD) has attracted much
attention in recent years [8], [9], [10]. In particular, deep learning
provides a basis for learning complex multidimensional dependencies in multivariate time series [11], [12].
Another promising line of research in MTAD is the use of
graph learning (i.e., machine learning on graphs) [13]. Graph
learning is applicable to a variety of tasks (such as node classification, graph classification, link prediction, and clustering) in
many domains (such as medical diagnosis, knowledge graphs,
drug discovery, computer vision, natural language processing,
and recommender systems). In particular, graph neural networks
(GNNs) are widely used to capture the dependencies among variables [14]. A popular trend is to represent relationships between
variables in the form of a graph [15]. In practice, there is often a
lack of a priori knowledge about variable correlations in multivariate time series, and consequently, the corresponding graphs
are missing. Some researchers (e.g., [16]) have used adaptive
learning methods to learn static graph structures from data.

S

2168-6750 © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

XIA et al.: COUPLED ATTENTION NETWORKS FOR MULTIVARIATE TIME SERIES ANOMALY DETECTION

However, it has been recognized that the relationship in time series data is dynamic transformation [17], and using a static graph
to represent dynamic variable relationships is impracticable. To
address this challenge, graph attention networks (GATs) [18],
[19] have been used to detect dynamic variable interactions
while ignoring global correlations between variables. Although
GNNs have demonstrated strong representational capabilities in
non-euclidean space [20], [21], GNNs and their variants lack the
ability to comprehensively construct dynamic graphs without a
priori knowledge.
To address the above knowledge gap in MTAD, this paper
proposes a novel coupled attention network (CAN), which takes
advantage of graph learning, attention mechanisms, and convolutional neural networks. A global-local graph is established to
describe the dynamic correlations between variables in multivariate time series. Specifically, learnable embedding vectors
are used to represent variable features, and embeddings can
learn global correlations between variables from training data.
The global graph represents the correlations in the entire time
series. Furthermore, the local correlations are obtained through
the attention mechanism, and the local graph represents the
relationships between variables in the current input local time
series. Therefore, the relationships in the global graph are used
as candidate neighbors to filter the local graph. The global-local
graph convolution module and the temporal self-attention module are combined to construct the coupled attention layer, which
is the primary layer of the model. This layer has the ability
to model complex dependencies among variables and temporal
dependencies. To fully utilize time series data, we use a novel
multilevel encoder-decoder framework that facilitates reconstruction and prediction. The proposed framework consists of an
encoder and two decoders for prediction and reconstruction. To
minimize the risk of overfitting, reconstructed models are only
used to assist in learning multivariate time series representations
during training, while predictive models are ultimately used for
anomaly detection.
The contributions of this paper are summarized as follows:
r Global-local graph convolutional network: To capture
complex and dynamic variable correlations in multivariate
time series data, we propose a novel global-local graph
convolutional network. This network can represent both
global correlations and dynamic local correlations among
sensors (or variables).
r Coupled attention network: We present a coupled attention
network based on the proposed global-local graph convolutional network and the attention mechanism. Specifically, a temporal self-attention module is exploited. The
integration of graph learning and attention mechanisms
ensures our CAN approach has the ability to model complex dependencies among variables and temporal dependencies in the absence of prior knowledge.
r Multilevel encoder-decoder framework for anomaly detection: We propose a novel multilevel encoder-decoder
framework to solve the problem of multivariate time series
anomaly detection. The framework is a prediction-based
anomaly detection method and uses reconstruction tasks
to jointly represent time series data.

241

r Comprehensive experimental evaluation: We conducted
extensive experiments on three real-world multivariate
time series datasets. The experimental results demonstrate
the effectiveness and superiority of the proposed approach,
CAN, in comparison with state-of-the-art baselines.
The remainder of the paper is organized as follows: We review
related work on time series anomaly detection in Section II.
Section III provides relevant preliminaries in which the problem
statement is given. The details of the proposed framework CAN
are presented in Section IV, and in Section V, the performance
evaluation of CAN is discussed, and the experimental results are
analyzed. Finally, we conclude the paper in Section VI.
II. RELATED WORK
Time series can be univariate or multivariate. Accordingly,
we categorize time series anomaly detection into univariate (time
series) anomaly detection and multivariate (time series) anomaly
detection. Univariate anomaly detection models each variable
independently, while multivariate anomaly detection considers
the connection between multiple variables to detect anomalies.
A. Univariate Anomaly Detection
Before deep learning became popular, various mathematical
and statistical models were developed to analyze time series
data, most of which have already been used for anomaly detection. For example, the autoregressive integrated moving average
(ARIMA) [22] is used to forecast future states based on past
states. The discrepancy between the forecasted value and the
ground truth is used to deduce anomalies. In [23], the mathematical analysis of time series data generates a statistical model
by calculating statistical measures, such as the mean, variance,
and quantile. The statistical model can detect the tested data to
determine whether it belongs to the normal boundary. Recently,
machine learning and deep learning methods have achieved
remarkable improvements in time series anomaly detection [2],
[4], [24]. In particular, autoencoders (AEs) [25] and variational
autoencoders (VAEs) [26] are widely used as reconstruction
models that employ reconstruction errors as anomaly scores.
For example, DAGMM [27] combines Gaussian mixture models
and AEs to obtain reconstruction models for anomaly detection.
In addition, long short-term memory (LSTM) has also been
frequently utilized in time series modeling, and researchers have
introduced LSTM-based autoencoders for reconstruction-based
anomaly detection [28].
B. Multivariate Time Series Anomaly Detection
In the context of MTAD, there are often correlations between
variables in the same entity or system in the real world. Many
researchers have started using multivariate time series data as input to improve anomaly detection accuracy [9], [11], [12], [19].
MTAD methods based on deep learning can be roughly classified
into two categories: reconstruction-based and prediction-based.
Reconstruction-based methods learn low-dimensional representations of multivariate time series, reconstruct normal values,

242

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTING, VOL. 12, NO. 1, JANUARY-MARCH 2024

and detect anomalies based on reconstruction errors. For example, LSTM-VAE [29] combines LSTM with a VAE to fuse signals and reconstruct the expected distribution. The LSTM-based
encoder projects multivariate observations into a latent space.
The decoder then reconstructs the expected distribution of the
multivariate inputs. OmniAnomaly [30] uses a stochastic recurrent neural network to avoid potential misguidance by uncertain
instances. Its core idea is to build robust representations of multivariate data to capture their normal patterns and reconstruct the
input data. The above methods reconstruct the input sequence but
also reconstruct the constructed features. MSCRED [31] detects
anomalies by reconstructing the signature matrices of multiscale
relationships between variables. These methods are good at
capturing global data distributions. Prediction-based methods
attempt to predict the normal values of indicators based on
historical data and detect anomalies based on prediction errors.
For example, LSTM-NDT [10] uses an LSTM-based prediction
approach with unsupervised nonparametric dynamic thresholding for anomaly detection. These methods are specialized for
feature engineering in the prediction of the next timestamp.
Reconstruction-based and prediction-based methods have their
own advantages, but few methods consider joint reconstruction
and prediction tasks to simultaneously characterize multivariate
time series data [32], [33]. In addition to reconstruction-based
and prediction-based anomaly detection, many novel anomaly
detection methods have emerged, including base classification
anomaly detection [34] and contrast learning-based anomaly
detection [8].
Although these methods use multivariate time series as input,
none of them explicitly learn or demonstrate the relationship
between different time series. This relationship is critical for the
diagnosis of anomalies. Graph-structured data have been widely
utilized to describe variable relationships in a variety of domains,
such as smart cities, transportation, and finance. In addition,
graph convolutional networks (GCNs) [35] and GATs [18] are
widely used in various fields. For instance, the GDN [36] depends on sensor embedding to flexibly capture the characteristics
of each sensor and learns the relationships between sensors
by cosine similarity. MTAD-GAN [19] concatenates two graph
attention layers in parallel to learn the complex dependencies in
temporal and feature dimensions. GTA [16] uses a transformerbased architecture to model temporal correlation and proposes
a self-learning graph structure to capture bidirectional links
between sensors. DVGCRN [33] designs adaptive variational
graph convolutional recurrent networks to model spatial and
temporal fine-grained correlations and capture multilevel information at different layers.
Table I provides an evaluation of the relevant models, where
KNN [37], PCA [38], and IF [39] stand for k-nearest neighbors,
principal component analysis, and isolated forests, respectively.
Almost all existing methods use only one task to train the
model, and rarely do they combine both tasks to train the model.
However, the reconstruction and prediction tasks actually have
the potential to complement each other. In addition, although
many researchers use GNNs to capture the correlation between
variables, constructing the graph and representing the dynamics
of the graph for MTAD has not been solved. Global relationships

TABLE I
REVIEW OF EXISTING SOLUTIONS

TABLE II
NOTATIONS

that depend on the characteristics of variables and local relationships that change over time are not considered simultaneously.
In this paper, we propose an effective approach to address these
challenges.
III. PRELIMINARIES
The main focus of the paper is on MTAD at the entity level.
This section introduces the definitions and then formalizes the
MTAD problem.
A. Notations and Definitions
Regarding notations, lowercase letters (e.g., a) represent
variables, while uppercase letters (e.g., A) represent constants.
Moreover, letters in bold (e.g., a, A) represent vectors or matrices. For the sake of readability, the notations used throughout
the paper are listed in Table II.
Definition 1. Multivariate Time Series (MTS): A time series is
a collection of observations recorded at equal-space timestamps.

XIA et al.: COUPLED ATTENTION NETWORKS FOR MULTIVARIATE TIME SERIES ANOMALY DETECTION

In this paper, assuming that an entity or system A contains
multiple features or sensors, the characteristics of entity A over
a period of time can be expressed as MTS X ∈ RN ×L , where
L is the sequence length and N is the number of features
or sensors. Moreover, X n,: ∈ RL represents the nth feature
(n ∈ {0, 1, . . . , N − 1}) of A throughout all timestamps, and
X :,t ∈ RN represents all features of A at the tth timestamp
(t ∈ {0, 1, . . . , L − 1}).
Definition 2. Sensor Graph (SG): The SG is represented as
G = {V, A}, where V = {0, 1, . . . , N − 1} is a set of nodes
(in terms of sensors or their features) and A ∈ RN ×N is the
adjacency matrix of N nodes in which a cell ai,j is used to
record the edge weight between the ith and j th nodes.
B. Problem Statement
In general, MTAD determines whether an entity or system
is anomalous at the tth timestamp based on the corresponding
observation X :,t :
y t = C(X :,t ),

(1)

where y t is a Boolean value indicating the state of the system at
the tth timestamp (if y t = 1, the system is anomalous at the tth
timestamp; otherwise not) and C denotes the anomaly detection
function.
Moreover, as historical data are beneficial in terms of analyzing the current state of the system, a period of historical data can
be utilized to support MTAD. Accordingly, (1) can be rewritten
as (2):
y t = C(X :,t−K:t−1 , X :,t ),

(2)

where K represents the length of the historical data and
X :,t−K:t−1 is the observation of K historical timestamps. By
comparing X :,t with the patterns presented by X :,t−K:t−1 , the
detection function C generates the detection result.
To compare the current observation with the historical observations for MTAD, a prediction-based approach is studied
in this paper; it determines the anomaly based on prediction
bias. Specifically, following the unsupervised anomaly detection
formulation [16], [30], [36], the prediction model is trained
based on normal data X and used to make predictions about
data containing anomalies X  . According to the definition of
K, X and X  can be transformed into two windowed series
W = {[X :,0:K−1 , X :,K ], [X :,1:K , X :,K+1 ], . . .} and W  with
the same sliding window (i.e., K + 1). Furthermore, during the
training process, given a sample [X :,t−K:t−1 , X :,t ] from W,
X :,t−K:t−1 are used to predict X :,t , which can be expressed in
(3) as follows:
Y :,t = Fθ (X :,t−K:t−1 ),

(3)

where Y :,t denotes the prediction result at the tth timestamp,
and θ denotes the parameters of the predicting model. Note that
the training goal is to find a function Fθ to minimize the gap
between Y :,t and X :,t .
During the testing/detecting process, the same function Fθ is
used to predict Y :,t based on X :,t−K:t−1 . Then, the predicted
value and the actual value are passed to C to calculate the system

243

state y t according to (4) as follows:
y t = C(Fθ (X :,t−K:t−1 ), X :,t ),

(4)

To make the final determination on the anomaly, C can be implemented with two steps: first, the anomaly score is computed,
and then, it is compared with a chosen threshold to obtain the
final result.
IV. METHODOLOGY
As shown in Fig. 1, a multilevel coupled attention network
(CAN) is proposed to support MTAD with the three following
components:
r An encoder network Encoder: The Encoder consists of
multiple layers of coupled attention modules to process
training samples with position encodings;
r A decoder network for prediction Decoderpre : The
Decoderpre consists of multiple layers of mask selfattention modules to make the prediction based on training
samples with position encoding and the representation
vectors of Encoder;
r A decoder network for reconstruction Decoderrec :
Decoderrec has a structure similar to Decoderpre , but
it is used to reconstruct the input processed by Encoder.
These three components make up the CAN framework. In
general, the model input is first expanded with a new dimension,
and a positional embedding is added in the dimension, similar to
other multivariate time series models [40]. Second, the encoder
represents the input multivariate time series data using layered coupled attention modules and transmits the representation
vectors to two decoders. The encoder and two decoders form
encoder-decoder structures for prediction and reconstruction,
respectively. Third, based on this multilevel structure, the model
is trained by minimizing the joint loss of prediction and reconstruction. Finally, the trained model is used on the test set to infer
the predictions and detects anomalies based on the predicted and
actual values.
A. Coupled Attention Module
Based on attention mechanisms, the coupled attention module (CAM) is designed to learn the complex temporal and
variable-dependent relationships in multivariate time series data.
As shown in Fig. 2, CAM consists of a set of temporal selfattention layers to learn temporal correlations in time series and a
global-local graph convolutional layer to learn macro and micro
correlations between variables. In addition, the input to CAM
is a 3D tensor, denoted as H ∈ RN ×K×dt , with dt channels for
N sensors at K timestamps. Layer normalization and residual
connections are applied to solve the gradient disappearance
problem and improve the learning performance.
1) Temporal Self-Attention Layer: The self-attention mechanism can effectively and efficiently learn temporal dependencies
due to its superior capability for sequential data. Regarding MTS
data H ∈ RN ×K×dt , N parallel self-attention layers are used
to learn the temporal dependence of each sensor separately.
Particularly, for the nth sensor, a single layer input is represented
by H n ∈ RK×dt .

244

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTING, VOL. 12, NO. 1, JANUARY-MARCH 2024

Fig. 1. Overall CAN framework with one encoder and two decoders. The rounded rectangles represent neural networks, and the sharp rectangles
represent tensors. The normal linear layers are hidden. The last layer of the two decoders intercepts the tensor to obtain a tensor of target length 1
and K. During training, the model is jointly trained by the outputs of the two decoders. Only the predicted decoder operates to calculate the anomaly
score when detecting anomalies.

To compute temporal dependencies, first, the input H n is
passed to three full connection layers separately. Then, H n is
projected into three high-dimensional latent subspaces, namely,
a query subspace Qn ∈ RK×dk , a key subspace by K n ∈
RK×dk and a value subspace by V n ∈ RK×dv according to (5):
Qn = H n W q ,
K n = H nW k ,

(5)

V n = H nW v ,
dt ×dk

, W k ∈ Rdt ×dk , and W v ∈ Rdt ×dv are
where W q ∈ R
learnable parameters.
Second, the scaled dot-product of Qn and K n is used to
compute the temporal dependencies, and then, the related results
are used to update V n for the layer output. Accordingly, the
procedure can be described by (6):


Qn (K n )T
√
V n . (6)
Attention (Qn , K n , V n ) = Softmax
dk

Fig. 2. Coupled attention module consisting of N parallel temporal
self-attention layers and a global-local graph convolutional layer.

Finally, to capture richer information from the three representational subspaces, the multi-head attention mechanism is
applied, and it can be expressed by (7) and (8):


Headi = Attention H n W iq , H n W ik , H n W iv , (7)
h

MultiHead(H n ) =  Headi W o ,
(8)
i=1

XIA et al.: COUPLED ATTENTION NETWORKS FOR MULTIVARIATE TIME SERIES ANOMALY DETECTION

where h is the number of heads,  denotes the concatenation
operation, and W o contains parameters to be learned. Both
static global correlation and dynamic local correlation between
variables exist in multivariate time series. From a global view,
the correlation among sensors of the same type can be easily
established over a long time series because the curves of the
same senor type are similar. However, when the correlation
changes, employing local information is critical. For example, in
a water treatment system, we can easily establish the connection
between two water quality sensors in close proximity. However,
the connection may be broken by the closing of a particular
gate. To learn about such complex dependencies, we represent
them with a global-local graph. The global graph is used to
represent static relationships based on sensor similarity, and the
local graph is employed to dynamically adjust the global graph
based on the local sequence. In other words, the local graph filters
out potential neighbors that are first identified by the global graph
to establish and formulate a real-time relationship.
We define a learnable embedding en representing the inherent
characteristics of the nth sensor. We initialize the vector using
random initialization (using prior knowledge to initialize the
vector when prior knowledge exists). Accordingly, an undirected
adjacency matrix Ag representing the relationship among global
sensors can be created by calculating the similarity of their
embeddings as defined in (9):
Ag = Relu(E × E T ),

(9)

where E represents the sensor embedding vector matrix (consisting of en ).
The global adjacency matrix Ag represents the general similarity of the sensors, but it cannot measure their time-varying
local relationships [17]. Inspired by GAT, a local adjacency
matrix Al is created based on an enhanced attention mechanism,
which processes the temporal input together with the intrinsic
features of the sensor to calculate the attention coefficient ali,j
as follows:
reshape

W H (size=(N,K,ds )) −→ V (size=(N,K×ds )) ,
eli,j = LeakyReLU (c ([v i v j ])) ,
 
exp eli,j
l
ai,j = N
 l ,
l=1 exp ei,j

(10)
(11)
(12)

where W is a weight matrix that transforms the feature dimension, “” represents the concatenation of two nodes’ representations, c ∈ R2Kds is a column vector of learnable parameters, and
LeakyReLU denotes a nonlinear activation function. Since Al
depends on the current input, it can reflect the local inter-sensor
dependencies.
Based on the synergistic relationship between the two graphs,
Ag and Al are used to design a new graph convolution layer
to further model the influence propagation process and update
the representation of each node by combining information from
neighboring nodes. Specifically, first, the mask adjacency matrix
Am of the neighbor candidates is selected from Ag by filtering
the K m most significant values according to (13):
m g
am
i,j = 1{i ∈ {1, 2, . . . , N }, j ∈ argtopK (ai,: )}.

(13)

245

Second, the information propagation step is defined as follows:
g

Agl = Am (Al + Ã ),
H = (βH + (1 − β)Agl H)W ,

(14)

where β denotes a hyperparameter controlling the ratio that
g
retains the original states, Ã is the normalized Ag , and W
represents a learnable parameter matrix.
B. Encoder
The encoder is the most important part of the whole framework. Regarding the input, the encoder’s input is X f eed_en =
{X, X 0 }, where X is equivalent to X :,t−K:t−1 denoting the
given historical data, and X 0 represents the virtual placeholder
time node that collects information about the whole sequence
using zero initialization. As shown in Fig. 1, the encoder handles
temporal dependence and sensor dependence based on CAMs.
Specifically, a CAM compresses MTS information into the virtual placeholder time node to update X 0 to obtain the sequence
embedding X e .
Moreover, the encoder consists of multiple layers of CAMs,
which are stacked to improve the model capacity, and each CAM
computes and transfers the corresponding X e to the decoder.
Since anomalies tend to have a low reconstruction probability
when the model is trained on normal data only [30], X e is further
embedded into the low-dimensional space through a series of
fully connected layers to improve the detection performance.
Then, it is reconstructed through a series of opposite fully
connected layers and transmitted to the decoder.
C. Decoder
As shown in Fig. 1, to make efficient use of the time series
data, two distinct decoders for reconstruction and prediction are
created. Both decoders consist of temporal self-attention layers
with a lower triangular form mask. In this way, self-attention is
bidirectional in the encoder and unidirectional in both decoders.
Furthermore, both decoders have the same number of network
layers as the encoder, and each layer in the decoder corresponds
to a layer in the encoder. Each layer in the encoder transmits an
embedding X e to the decoders, and the corresponding layer of
the decoders accepts the embedding X e and concatenates it to
the original sequence. The difference between the two decoders
is that one is used to predict the next value of the temporal
data, while the other is used to reconstruct the entire historical
sequence.
In the prediction decoder, the input to the decoder X f eed_pre
is X 0 because only one-step prediction is required. The last
timestamp of the output sequence is a prediction of the next moment, which can observe the entire historical series. Therefore,
we intercept the last timestamp and obtain the prediction result
Y :,K+1 using a fully connected layer as follows:
Y :,K+1 = FC(Cropping(H M
pre , −1)),

(15)

where −1 denotes cropping from the end to obtain a sequence
M
of length 1, Hpre
indicates the output of the stacked multiple

246

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTING, VOL. 12, NO. 1, JANUARY-MARCH 2024

attention layers in the decoder, and F C denotes a fully connected
layer.
The prediction loss is calculated using the root mean square
error (RMSE) as follows:


1 N
(X n,K+1 − Y n,K+1 )2 ,
(16)
Lpre =
N n=1
where X n,K+1 and Y n,K+1 are the actual and predicted values
of sensor n at timestamp K + 1, respectively.
In the reconstruction decoder, a placeholder X 0 is added to
the original sequence to reconstruct the entire series. The input
to the reconstructed decoder can be expressed as X f eed_rec =
{X 0 , X :−1,: }. Since the attention matrix in the decoder has
a lower triangular form mask, the input and output will be
misaligned by one timestamp. After multiple attention layers,
we obtain a sequence of length K by cropping from the tail and
transform it to obtain the reconstruction result Y :,:K as follows:
Y :,:K = FC(Cropping(H M
rec , −K)),

(17)

where −K denotes cropping from the end to obtain a sequence of
M
indicates the output of the stacked multiple
length K, and Hrec
attention layers in the decoder.
The RMSE was also selected to calculate the reconstruction
loss. The equation is expressed as follows:


 1 K N
(X n,t − Y n,t )2 ,
(18)
Lrec =
KN t=1 n=1
where X n,t and Y n,t are the actual and reconstructed values of
sensor n at timestamp t, respectively.
D. Joint Optimization
When representing MTS data, the prediction loss is mostly
used to predict a point in time, while the reconstruction loss
is primarily used to capture the distribution of the time period.
The combination of the two can reduce the difficulty of model
training, which better characterizes temporal data and captures
hidden features between sensors. Therefore, in the CAN model,
the loss function is defined as the weighted sum of the two
optimization objectives as follows:
L = φLpre + ϕLrec ,

(19)

where φ and ϕ denote the hyperparameters used to make a
tradeoff between the prediction and reconstruction models, respectively, and φ + ϕ = 1. In general, the reconstruction task
is considered to be easier than the prediction task. Thus, ϕ is
greater than φ during the first few training epochs, and then, φ
becomes more significant than ϕ during the last few training
epochs. The corresponding training algorithm is described in
Algorithm 1.
E. Model Inference
The prediction decoder is utilized to detect anomalies, and
the reconstruction module is only used to assist in the training.

Algorithm 1: Training Process.
Require: Training set X of datasets, the number of
attention module layers M , the batch size is B, and the
window length is K + 1;
Ensure: Well Trained model;
1: Divide the dataset X into W according to the sliding
window.
2: Initialize embedding vectors E for all sensors.
3: repeat
4:
Sample a batch (X ∈ RB×(K+1)×N ) from W.
5:
Construct model inputs X f eed_en , X f eed_pre and
X f eed_rec .
6:
Add positional embedding into model inputs to
obtain H 0 , H 0pre and H 0rec .
7:
Ag ← Relu(E × E T ).
8:
for i = 1, 2, . . . , M do
9:
// Encoder layer
10:
H i ← Self-Attention(H i−1 )
11:
Compute Al by H i according to (10) and (12).
12:
H i ← Global-localGraphConv(H i , Ag , Al ).
13:
X ie ← H i [: −1].
14:
// AE between encoder layer and decoder layers
15:
X̂ e ← AE(X e ).
16:
// Decoder layer for prediction
i−1
17:
H i−1
pre ← Concat(X̂ e , H pre ).
i
18:
H pre ← MaskSelf-Attention(H i−1
pre ).
19:
// Decoder layer for reconstruction
i−1
20:
H i−1
rec ← Concat(X̂ e , H rec ).
i
21:
H rec ← MaskSelf-Attention(H i−1
rec ).
22:
end for
23:
// Obtain the prediction result Y :,K+1 and
reconstruction result Y :,:K through cropping and
the fully connected layer
24:
Y :,K+1 ← FC(Cropping(H M
pre , −1)).
25:
Y :,:K ← FC(Cropping(H M
rec , −K)).
26:
Optimize the parameters by minimizing the loss
function defined in (19).
27: until convergence

The reconstruction-based method is more suitable for describing anomalies over the entire period. In point-in-time anomaly
detection based on reconstruction, the target timestamp can
be at a different position in the time window, and it becomes
difficult to utilize multiple reconstruction results. In addition, the
reconstruction-based model may neglect sudden perturbations
to disrupt periodicity in a time series, especially when the
values still follow the normal distribution [19]. Therefore, only
the predicted results of the timestamps are used for MTAD.
Accordingly, the predicted deviation for each sensor can be
calculated according to (20):
Errn (t) = |X n,t − Y n,t | ,

(20)

where Errn (t) denotes the deviation of sensor n in the t timestamp.

XIA et al.: COUPLED ATTENTION NETWORKS FOR MULTIVARIATE TIME SERIES ANOMALY DETECTION

TABLE III
DATASET DESCRIPTION AND STATISTICS

As different sensors may possess significantly different characteristics, their deviation values may have different scales. To
prevent the overall anomaly score from being overly dominated
by the deviation values produced by a particular sensor, the
deviation values are normalized for each sensor. Normalization
based on mean and interquartile range is used as defined in the
following equation:
S n (t) =

Errn (t) − μn
,
IQRn

(21)

where μn is the mean of Errn , IQRn is the interquartile range
of Errn , and S n (t) denotes the normalized deviation of sensor
n at the t timestamp.
To calculate the anomaly score at the t timestamp, the K s
sensor aggregation with the largest deviation value is selected,
as anomalies tend to affect only a small number of sensors, which
is expressed by the following equation:
idxt = argtopK s (S(t)),
st =

S i (t),

(22)

i∈idxt
s

where idxt is a set of K sensors with large deviation values. The larger the anomaly score, the more likely it is to
be an anomaly. According to a threshold defined by methods, such as the dynamic error threshold [10] and peaks-overthreshold [30], when the anomaly scores of a timestamp are
greater than the threshold, the timestamp is inferred to be an
anomaly.
F. Complexity Analysis
The time complexity of the main components of the proposed CAN model is analyzed. We skip the batch dimension
and analyze the complexity involved in multivariate temporal
data of temporal length K with N sensors. The hidden dimension size of the temporal self-attention layer is {dt , dk },
the hidden dimension size of the global-local graph convolutional layer is ds , and the sensor embedding dimension size
is de . The main complex computation of the temporal selfattention layer contains the computation of feature mapping
of Q, K, V and the attention coefficients. Their complexity
is O(K × dt × dk ) and O(K 2 × dk ) for each sensor, respectively. The temporal self-attention layer has a complexity of
O(N × K 2 × dk ). In addition, the global-local graph convolutional layer incurs O(N 2 (de + K × ds )) time complexity. The
computational complexity of the global graph is O(N 2 × de ),
and the computational complexity of the local graph computation is O(N 2 × K × ds ). The remainder no longer involves
high-complexity multiplication operations.
V. EXPERIMENTS
In this section, first, the datasets and evaluation metrics are
introduced. Second, we describe the experimental setup and the
prepared MTS data, selected baselines, and configuration of the
proposed model. Finally, dedicated analyses are performed to
illustrate the effectiveness of the proposed model.

247

A. Datasets
Three real-world MTS datasets, namely, the Secure Water
Treatment (SWaT) dataset [41], Water Distribution (WADI)
dataset [41] and Soil Moisture Active Passive satellite (SMAP)
dataset [10], were used for the evaluation. Specifically, SWaT
was collected from a water treatment testbed for cybersecurity,
where the testbed was a fully operational scaled-down water
treatment plant with a small footprint. The dataset consists of 11
days (7 days under normal operation and 4 days with attacks)
of continuous operation, and every second of the testbed’s
physical properties (25 sensors and 26 actuators) was recorded.
The transducer names define their roles, e.g., MV denotes a
motorized valve, P denotes a pump, FIT denotes a flow meter, and LIT denotes a level transmitter. The dataset contains
946,719 samples, of which 496,800 were collected under normal
operation, while 449,919 were collected with attack scenarios.
More details are available on the website.1 WADI is a natural
extension of SWaT. WADI has a more complex composition
and is equipped with more analytical equipment. It consists of
789,371 samples from 14 days of continuous normal operation
and 172,801 samples from two days collected in attack scenarios.
Similar to SWaT, WADI is a collection of all 103 sensor and
actuator data during the data collection period. Compared with
SWaT, WADI contains attacks on PLC and the network and
simulated physical attacks (such as water leakage and malicious
chemical injection). More details are available on the website.2
The SMAP dataset is a public dataset published by NASA. The
dataset is a record of telemetry data from sensors in individual
spacecraft with a set of relevant telemetry values labeled by
experts at NASA [10]. Table III summarizes the three datasets.
B. Evaluation Metrics
The precision, recall, and F1-score were used as the evaluation
metrics, which are defined in the following equations:
TP
,
(23)
TP + FP
TP
Recall =
,
(24)
TP + FN
2 × Precision × Recall
F1 =
,
(25)
Precision + Recall
where TP denotes the truly detected anomalies, FP represents the
falsely detected anomalies, TN denotes the truly detected normal
samples, and FN represents the falsely detected normal samples.
Precision =

1 https://itrust.sutd.edu.sg/testbeds/secure-water-treatment-swat/
2 https://itrust.sutd.edu.sg/testbeds/water-distribution-wadi/

248

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTING, VOL. 12, NO. 1, JANUARY-MARCH 2024

Moreover, the related metric scores may vary along with the
anomaly score threshold. Hence, an optimal global threshold is
defined based on a grid search.
In practice, an anomaly is often within a segment of consecutively observed anomalies marked by corresponding timestamps. A segment anomaly is correctly detected if any timestamp
in the time segment of the marked anomaly is detected as an
anomaly. In the proposed model, a point-adjust [42] strategy is
used to transform the anomaly detection results. Specifically, for
a continuous anomaly segment, if there is an observation in it that
is correctly identified as an anomaly, then the anomaly segment
has observations that are considered to be correctly detected
by the model. If the ground truth is observed to be normal, no
adjustments are made to the detection results.
C. Experimental Setup
1) Data Processing: Since the SWaT and WADI datasets
have a huge sample size, to speed up the model training, the
datasets were downsampled every ten seconds by taking the
median value. Moreover, to improve the stability, the raw data
were standardized using min-max normalization. Specifically,
the maximum and minimum values of each sensor feature in
the training set were calculated and then used to standardize the
training set and testing set as follows:

x̃n =

xn − min X ntrain
,
max X ntrain − min X ntrain

(26)

where min X ntrain and max X ntrain denote the minimum value
and the maximum value of sensor n in the training set, respectively.
2) Baselines: To highlight the performance of the proposed
method, it is compared with several baselines, which are listed
as follows:
1) PCA [38]: Principal component analysis obtains a lowdimensional projection by extracting the main feature
components of the data. The anomaly score is the reconstruction error of this projection.
2) KNN [37]: K-nearest neighbors uses the observation’s
distance to its k nearest neighbors as the anomaly score.
3) AE [25]: The autoencoder reconstructs the observation
using an encoder and decoder composed of MLPs.
Anomalies are frequently difficult to recreate, and the
reconstruction errors are used as anomaly scores to
detect anomalies.
4) IF [39]: Isolated forests use a binary search tree structure
called iTree to isolate samples and then detect anomalies
by using isolating sample points.
5) DAGMM [27]: The Deep Autoencoding Gaussian
Model combines a deep autoencoder and a Gaussian
mixture model to generate a low-dimensional representation of the samples and reconstruction results. The
samples’ reconstruction errors are considered anomaly
scores.
6) LSTM-VAE [29]: LSTM-VAE replaces the feed-forward
network in the VAE with LSTM and uses the reconstruction error as the anomaly score.

7) OmniAnomaly [30]: OmniAnomaly uses the VAE as
the main structure, and a GRU is utilized to capture
the complicated temporal correlation of multivariate
observations. The anomaly scores are calculated based
on the sample reconstruction errors.
8) MTAD-GAN [19]: MTAD-GAN learns the temporal
dependencies and interdependencies between variables
using the attention mechanism and then trains using a
combination of reconstruction and prediction models.
The anomaly scores are composed of the reconstruction
error and prediction error.
9) GDN [36]: The Graph Deviation Network learns the
graphic relationship between sensors and performs
single-step prediction using an attention mechanism; the
prediction error is treated as the anomaly score.
10) GTA [16]: GTA learns the relationship between sensors
and combines graph convolution and a transformer to
build a single-step time series prediction model; the
prediction error is considered an anomaly score.
11) DVGCRN [33]: DVGCRN combines a probabilistic
generative network with a variational graph convolutional recurrent network to model both spatial and
temporal fine-grained correlations and considers both
reconstruction-based and forecasting-based losses to optimize MTS representations.
3) Implementation Details: The proposed method was implemented based on PyTorch 1.9.0 with CUDA 10.2. All experiments were conducted on an NVIDIA GeForce RTX 2080Ti.
The model input was a historical time series with a window
size of 5 (50 in SMAP) for single-step prediction and sequence
reconstruction. The dimension size of the sensor embedding was
set to 10 for SWaT and SMAP and 20 for WADI. The number
of relations extracted K m was set to 10, and the number of
sensors extracted K s was set to 2. The AE module was set up as
a two-layer linear layer with the hidden layer dimension {8, 4,
8}. The encoder and two decoders both have three self-attention
layers. For the multi-head attention mechanism, the number of
heads was set to 8. The α and β parameters were initialized to
0.2 and 0.8 during training and transformed to 0.8 and 0.2 after
four epochs. The models were trained using the Adam optimizer
with a learning rate of 1e-4, which decays with the number of
training epochs. The early stopping strategy was also applied
during training, and the patience was set to 5, which means
that training stopped if there were five consecutive decreases in
performance.
To implement the baseline methods, the number of neighbors
was 5 in the KNN method, and the hidden layer dimension was
{64, 32, 32, 64} in the AE method. DAGMM,3 OmniAnomaly,4
MATD-GAT,5 GDN6 and DVGCRN7 were implemented and
reused in the evaluation. As the current implementation of GDN
does not use a point adjustment policy, to ensure fairness, a point
adjustment policy was added. Finally, for GTA, its paper does
3 https://github.com/tnakae/DAGMM/
4 https://github.com/NetManAIOps/OmniAnomaly
5 https://github.com/ML4ITS/mtad-gat-pytorch
6 https://github.com/d-ailin/GDN
7 https://github.com/SigmaLab01/DVGCRN

XIA et al.: COUPLED ATTENTION NETWORKS FOR MULTIVARIATE TIME SERIES ANOMALY DETECTION

249

TABLE IV
PERFORMANCE ON SWAT, WADI AND SMAP DATASETS

not provide the source code. However, it uses the same dataset
as ours. Hence, its reported performance is directly used for
comparison.

D. Experimental Results
Table IV reports the overall performance of the baselines
and the proposed method on SWaT, WADI and SMAP. Since
different methods have different threshold selection mechanisms, we tested the possible thresholds for each model and
report the results with the highest F1-scores. On all datasets,
CAN outperforms all previous techniques by achieving the best
F1-score of 0.9266 for SWaT, 0.8955 for WADI and 0.9428 for
SMAP. On the SWaT dataset, many methods achieved high detection performance, but the best CAN F1-score still improves by
approximately 2% compared to the second-best method (GTA).
While most approaches perform poorly on WADI, which has
more complicated sensors, the best CAN F1-score is 6% better
than those of the second-best approach (DVGCRN). Additionally, because of the simpler sensor relationships in the SMAP
dataset, the effect enhancement is less. On the precision index,
the proposed model is marginally inferior to other techniques.
Because we use the traversal strategy to obtain the threshold for
all models, some models choose a lower threshold to increase
precision and thus obtained a better F1-score. However, models
with a low threshold, such as KNN and OmniAnomaly, have
an extremely low recall. When considering the three indicators
simultaneously, the effect of our approach remains ideal with
balanced performance.
The traditional methods, i.e., PCA, KNN, and AE, perform
worse than deep learning-based methods. These machine learning methods are simple and fast, but their ability to process
complex time series data is limited. There is no efficient way
to model temporal correlation in multivariate time series data

using traditional methods. To improve the performance, temporal dependencies should be properly measured. However,
DAGMM directly detects each observation independently, completely ignoring the relationship between sensors. LSTM-VAE
and OmniAnomaly accept multivariate continuous observations
as input and use recurrent neural networks (LSTM, GRU) to
model the temporal dependency. However, they do not explicitly learn the dependencies between sensors. Thus, they
have less competitive performance than graph learning-based
detection methods. Specifically, MTAD-GAN uses an attention
mechanism to model the dependencies between sensors, and
it represents the relationships as a complete graph, which is
unrealistic. GDN uses adaptive learning to learn the relationship
between sensors but weakly models time series, leading to poor
results on the SMAP dataset. GTA designs a directed graph
structure learning approach to automatically learn the adjacency
matrix among sensors, and within the model, dilated convolution
and a transformer are used to learn the time dependence in
time series. However, training such a complicated model is
difficult. DVGCRN focuses on the robustness of the model under
noise and does not model sensor correlations more accurately.
CAN employs a global-local graph convolutional network to
learn the correlation between variables in a comprehensive
manner. CAN thus performs better when handling datasets that
have complicated relationships. In addition, the proposed CAN
method reduces the difficulty of model training by combining
the reconstruction and prediction tasks.
E. Parameter Sensitivity
In this section, the effect of the CAN parameters is analyzed.
Specifically, parameter sensitivity experiments were conducted
on SWaT for the three parameters: dimension size of the sensor embedding, number of relations extracted, and number of
encoder (or decoder) layers.

250

Fig. 3.

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTING, VOL. 12, NO. 1, JANUARY-MARCH 2024

Effect of parameters.

The sensor embedding records the global dependencies between sensors, and its dimension size is one key parameter.
Fig. 3 shows the model performance results when the dimensions
are 2, 5, 10, 15, and 20. The results show that the model
performs optimally with a dimension size of 10. Too small of a
dimension makes it difficult to include all the dependencies,
while too large of a dimension makes it more challenging
to learn the embedding vectors due to increased parameters.
The number of extracted relations determines the number of
dependencies established between sensors, which is crucial for
learning dependencies between sensors. The most appropriate
K m for SWaT is 10, which indicates that the dataset may have
approximately ten dependencies for each sensor. Finally, parameter sensitivity experiments were performed on the number
of layers in the model’s encoder. The model performs poorly
when the number of layers is 2, as it is difficult to simulate the
complex dependencies in multivariate time series data. When the
number of layers is increased to 3, the model’s learning ability
is improved, and the performance is significantly enhanced.
However, when the number of layers continues to increase to 4
and 5, the model training difficulty increases, and the detection
accuracy starts to decline slowly. In general, the model is robust
in retaining a strong performance level across a wide range of
parameters.
F. Ablation Studies
To investigate the effectiveness of each component in CAN,
we exclude the elements to observe how the related performance
declines on WADI. Accordingly, five variant models of CAN
were designed as follows:
1) Without a local graph: The model only uses an adaptive
static graph for graph convolution and removes the graph
attention module.
2) Without graph convolution: The graph convolution layer
in CAN is replaced with a fully connected layer.
3) Without AE: CAN without autoencoder between the encoder and decoders. Sequence embedding is transferred
directly from the encoder to the prediction decoder and
reconstruction decoder.
4) Without Decoderrec : The model is simplified to a
prediction-based multivariate time series anomaly detection model.

TABLE V
ABLATION EXPERIMENTS ON THE WADI DATASET

5) CAN + : The method considers the reconstruction error
when the target timestamp is the last timestamp of the
input sequence to detect anomalies, and we fuse the
reconstruction error and the prediction error in a certain
proportion (0.1 is used in the paper) as the anomaly
score.
The results are summarized in Table V. Comparing the five
variants, the complete model has the best performance. The
performance degradation from the absence of both a local graph
and graph convolution illustrates the necessity of inter-sensor
dependencies for multivariate time series anomaly detection.
The effectiveness without the local graph is reduced, demonstrating the local graph’s significance in capturing the dependencies
between sensors. The AE module has the effect of filtering some
anomalies through reduction and reconstruction. A significant
decrease in model effectiveness is observed when the model
lacks the reconstruction decoder. This observation illustrates the
effectiveness of the reconstruction decoder on multivariate time
series data for encoder-assisted training. The reconstruction decoder helps the encoder represent multivariate time series data by
reconstructing the task properly. In addition, the reconstruction
error is typically influenced by the full input sequence and is not
appropriate for timestamp anomaly detection directly; hence,
the performance of CAN + is not improved in comparison with
CAN.
G. Visualization
1) Effect of the Global Graph: To evaluate the effect of
the model global graph, the sensor embedding vectors learned
through training on SWaT are visualized based on t-SNE [43],

XIA et al.: COUPLED ATTENTION NETWORKS FOR MULTIVARIATE TIME SERIES ANOMALY DETECTION

Fig. 4.

251

t-SNE plot of the sensor embeddings.

which is used to draw a scatter plot projecting the embedding
vector into two-dimensional space. Accordingly, six different
types of sensors with six different colors are presented in Fig. 4.
It can be observed that sensors of the same type tend to be close
to each other. This observation also verifies that the learned
embedding vectors can respond to a particular global feature
of the sensors.
2) Case Study: A case study is prepared on an anomalous
segment with a known attack in WADI to further evaluate
our model. WADI’s log file records an anomalous segment
located between 19:25:00 and 19:50:16 on October 17. During this attack period, the attacker caused motorized valve
1_MV_001 to turn on maliciously to overflow the raw water
tank.
The WADI test distribution treatment is divided into three
stages: the water supply P1, distribution network P2, and return
water system P3. P1 consists of two raw water tanks with a
capacity of 2500 liters. Water intake into these two tanks can be
from the water treatment plant named SWaT, from the public
utility board inlet, or from the return water grid in WADI.
Therefore, when the 1_MV_001 motorized valve is turned on,
water flows into the raw water tank. The sensor 1_FIT_101
inflow meter increases rapidly, and the sensor 1_LT_101 level
transmitter gradually climbs. At the same time, the attack on
the motorized valve will also be transmitted to the P2 stage.
For example, the pressure meter 2_PIT_001 sensor will change
due to the increase in the P1 stage water level. In the global
graph learned from training, 1_MV_001 and 1_FIT_101 are
neighbors, and 1_LT_101 and 2_PIT_001 are neighbors to each
other. The learned relationship is consistent with the actual
relationship, which proves the effectiveness of the global graph
we learned. Fig. 5 visualizes the transformation of the four
sensors 1_MV_001, 1_FIT_101, 1_LT_101, and 2_PIT_001 in
the anomaly segment; the green line represents the ground truth,
the orange line represents the value calculated by the prediction
model, and the red shading indicates the attack period. After
1_MV_001 was maliciously turned on, the values of 1_MV_001,
1_FIT_101, and 1_LT_101 were still in a normal range, but the
2_PIT_001 sensor in P2 was clearly out of the normal range and
detected by the model. These results indicate that graph learning
implemented in CAN is critical, and the proposed framework
is effective and efficient in detecting multivariate time series
anomalies.

Fig. 5. The attacked sensor with three other sensors. The abscissa
represents the timestamp, and the ordinate represents the sensor value.

VI. CONCLUSION
In this work, we propose CAN, an anomaly detection framework based on self-attention and global-local graph convolution.
It combines the advantages of predictive models and reconstruction models. In detail, to capture the dynamic inter-sensor
dependencies in multivariate time series data, we propose to use
a global graph to capture the static dependencies that depend on
the features of the sensor itself and use graph attention to capture
the dynamic sensor dependencies over time. Then, we combine
temporal self-attention and graph convolution based on global
and local graphs into a multilevel encoder-decoder framework.
To better represent multivariate time series data, we jointly
use reconstruction and prediction tasks to implement model
optimization. When performing anomaly detection, we only
compute anomaly scores that pass from the predictive model. A
complex reconstructed model is prone to overfitting and ignores
anomalies, and it is not suitable for anomaly detection at a single
time point. Comprehensive experiments on three real datasets
demonstrate that our model outperforms other state-of-the-art
methods.
Most state-of-the-art methods use prediction-based methods
for time series anomaly detection because of the overfitting problem in the reconstructed model. However, the reconstruction
task is a crucial unsupervised task in time series data. In the
representation learning of time series data, the reconstructionbased model has advantages that the prediction-based model
does not have, such as robustness to perturbations and noise. This
paper also demonstrates the effect of the reconstructed model on
anomaly detection systems. However, the reconstruction task in
our work only plays a role that is similar to pretraining. There
must be a more appropriate method that can perfectly combine
the predictive model and the reconstructed model for anomaly
detection. Therefore, solving the overfitting of the reconstructed
model and better combining prediction and reconstruction tasks
will be a new direction for time series anomaly detection.
REFERENCES
[1] A. A. Cook, G. Mısırlı, and Z. Fan, “Anomaly detection for IoT time-series
data: A survey,” IEEE Internet Things J., vol. 7, no. 7, pp. 6481–6494,
Jul. 2020.

252

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTING, VOL. 12, NO. 1, JANUARY-MARCH 2024

[2] A. Blázquez-García, A. Conde, U. Mori, and J. A. Lozano, “A review on
outlier/anomaly detection in time series data,” ACM Comput. Surv., vol. 54,
no. 3, pp. 1–33, 2021.
[3] L. Ruff et al., “A unifying review of deep and shallow anomaly detection,”
Proc. IEEE, vol. 109, no. 5, pp. 756–795, May 2021.
[4] G. Pang, C. Shen, L. Cao, and A. V. D. Hengel, “Deep learning for anomaly
detection: A review,” ACM Comput. Surv., vol. 54, no. 2, Mar. 2021,
Art. no. 38.
[5] A. P. Ruiz, M. Flynn, J. Large, M. Middlehurst, and A. J. Bagnall,
“The great multivariate time series classification bake off: A review and
experimental evaluation of recent algorithmic advances,” Data Mining
Knowl. Discov., vol. 35, no. 2, pp. 401–449, 2021.
[6] A. Garg, W. Zhang, J. Samaran, R. Savitha, and C.-S. Foo, “An evaluation
of anomaly detection and diagnosis in multivariate time series,” IEEE
Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2508–2517, Jun. 2022.
[7] X. Kong et al., “Spatial-temporal-cost combination based taxi driving
fraud detection for collaborative internet of vehicles,” IEEE Trans. Ind.
Informat., vol. 18, no. 5, pp. 3426–3436, May 2022.
[8] Y. Jiao, K. Yang, D. Song, and D. Tao, “TimeAutoAD: Autonomous
anomaly detection with self-supervised contrastive loss for multivariate
time series,” IEEE Trans. Netw. Sci. Eng., vol. 9, no. 3, pp. 1604–1619,
May/Jun. 2022.
[9] T. Huang, P. Chen, and R. Li, “A semi-supervised VAE based active
anomaly detection framework in multivariate time series for online systems,” in Proc. ACM Web Conf., 2022, pp. 1797–1806.
[10] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric
dynamic thresholding,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, 2018, pp. 387–395.
[11] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” Proc.
VLDB Endowment, vol. 15, no. 6, pp. 1201–1214, Feb. 2022.
[12] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,” in
Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 3395–3404.
[13] F. Xia et al., “Graph learning: A survey,” IEEE Trans. Artif. Intell., vol. 2,
no. 2, pp. 109–127, Apr. 2021.
[14] Y. Wu, H.-N. Dai, and H. Tang, “Graph neural networks for anomaly
detection in industrial Internet of Things,” IEEE Internet of Things J.,
vol. 9, no. 12, pp. 9214–9231, Jun. 2022.
[15] H. Liang, L. Song, J. Du, X. Li, and L. Guo, “Consistent anomaly detection
and localization of multivariate time series via cross-correlation graphbased encoder-decoder GAN,” IEEE Trans. Instrum. Meas., vol. 71, 2022,
Art. no. 3504210, doi: 10.1109/TIM.2021.3139696.
[16] Z. Chen, D. Chen, X. Zhang, Z. Yuan, and X. Cheng, “Learning graph
structures with transformer for multivariate time series anomaly detection
in IoT,” IEEE Internet Things J., vol. 9, no. 12, pp. 9179–9189, Jun. 2022.
[17] M. Li and Z. Zhu, “Spatial-temporal fusion graph neural networks
for traffic flow forecasting,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 4189–4196.
[18] P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Liò, and Y. Bengio,
“Graph attention networks,” in Proc. Int. Conf. Learn. Representations,
2018, pp. 1–12.
[19] H. Zhao et al., “Multivariate time-series anomaly detection via graph attention network,” in Proc. IEEE Int. Conf. Data Mining, 2020, pp. 841–850.
[20] F. Xia et al., “CenGCN: Centralized convolutional networks with vertex
imbalance for scale-free graphs,” IEEE Trans. Knowl. Data Eng., vol. 35,
no. 5, pp. 4555–4569, May 2023.
[21] M. Lin, W. Li, D. Li, Y. Chen, and S. Lu, “Resource-efficient training
for large graph convolutional networks with label-centric cumulative sampling,” in Proc. World Wide Web Conf., 2022, pp. 1170–1180.
[22] G. E. Box and D. A. Pierce, “Distribution of residual autocorrelations in
autoregressive-integrated moving average time series models,” J. Amer.
Statist. Assoc., vol. 65, no. 332, pp. 1509–1526, 1970.
[23] M. Markou and S. Singh, “Novelty detection: A review—Part 1: Statistical
approaches,” Signal Process., vol. 83, no. 12, pp. 2481–2497, 2003.
[24] L. Erhan et al., “Smart anomaly detection in sensor systems: A multiperspective review,” Inf. Fusion, vol. 67, pp. 64–79, 2021.
[25] S. Agarwal, “Data mining: Data mining concepts and techniques,” in Proc.
Int. Conf. Mach. Intell. Res. Advance., 2013, pp. 203–207.
[26] D. Kingma and M. Welling, “Auto-encoding variational bayes,” in Proc.
Int. Conf. Learn. Representations, 2014, pp. 1–14.
[27] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Representations,
2018, pp. 1–19.

[28] P. Malhotra, A. Ramakrishnan, G. Anand, L. Vig, P. Agarwal, and G. M.
Shroff, “LSTM-based encoder-decoder for multi-sensor anomaly detection,” 2016, arXiv:1607.00148.
[29] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly detector
for robot-assisted feeding using an LSTM-based variational autoencoder,”
IEEE Robot. Automat. Lett., vol. 3, no. 3, pp. 1544–1551, Jul. 2018.
[30] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2019, pp. 2828–2837.
[31] C. Zhang et al., “A deep neural network for unsupervised anomaly detection and diagnosis in multivariate time series data,” in Proc. AAAI Conf.
Artif. Intell., 2019, pp. 1409–1416.
[32] S. Han and S. S. Woo, “Learning sparse latent graph representations for
anomaly detection in multivariate time series,” in Proc. 28th ACM SIGKDD
Conf. Knowl. Discov. Data Mining, 2022, pp. 2977–2986.
[33] W. Chen, L. Tian, B. Chen, L. Dai, Z. Duan, and M. Zhou, “Deep variational
graph convolutional recurrent network for multivariate time series anomaly
detection,” in Proc. 39th Int. Conf. Mach. Learn., 2022, pp. 3621–3633.
[34] L. Shen, Z. Li, and J. Kwok, “Timeseries anomaly detection using temporal
hierarchical one-class network,” in Proc. Int. Conf. Neural Inf. Process.
Syst., H. Larochelle, M. Ranzato, R. Hadsell, M. Balcan, and H. Lin, Eds.,
2020, pp. 13016–13026.
[35] T. N. Kipf and M. Welling, “Semi-supervised classification with graph
convolutional networks,” in Proc. Int. Conf. Learn. Representations, 2017,
pp. 1–14.
[36] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 4027–4035.
[37] F. Angiulli and C. Pizzuti, “Fast outlier detection in high dimensional
spaces,” in Proc. Eur. Conf. Princ. Data Mining Knowl. Discov., 2002,
pp. 15–27.
[38] S. Li and J. Wen, “A model-based fault detection and diagnostic methodology based on PCA method and wavelet transform,” Energy Buildings,
vol. 68, pp. 63–71, 2014.
[39] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. IEEE
8th Int. Conf. Data Mining, 2008, pp. 413–422.
[40] L. Bai, L. Yao, C. Li, X. Wang, and C. Wang, “Adaptive graph convolutional recurrent network for traffic forecasting,” in Proc. Int. Conf. Neural
Inf. Process. Syst., 2020, pp. 17804–17815.
[41] D. Li, D. Chen, B. Jin, L. Shi, J. Goh, and S.-K. Ng, “MAD-GAN: Multivariate anomaly detection for time series data with generative adversarial
networks,” in Proc. 28th Int. Conf. Artif. Neural Netw., 2019, pp. 703–716.
[42] H. Xu et al., “Unsupervised anomaly detection via variational auto-encoder
for seasonal KPIs in web applications,” in Proc. World Wide Web Conf.,
2018, pp. 187–196.
[43] L. van der Maaten and G. Hinton, “Visualizing data using t-SNE,” J. Mach.
Learn. Res., vol. 9, no. 86, pp. 2579–2605, 2008.
Feng Xia (Senior Member, IEEE) received the
BSc and PhD degrees from Zhejiang University,
Hangzhou, China. He is a professor with the
School of Computing Technologies, RMIT University, Australia. He has published two books
and more than 300 scientific papers in international journals and conferences (such as
the IEEE Transactions on Artificial Intelligence,
IEEE Transactions on Knowledge and Data Engineering, IEEE Transactions on Neural Networks and Learning Systems, IEEE Transactions on Computers, IEEE Transactions on Mobile Computing, IEEE
Transactions on Parallel and Distributed Systems, IEEE Transactions on
Big Data, IEEE Transactions on Computational Social Systems, IEEE
Transactions on Network Science and Engineering, IEEE Transactions
on Emerging Topics in Computational Intelligence, IEEE Transactions on
Emerging Topics in Computing, IEEE Transactions on Human-Machine
Systems, IEEE Transactions on Vehicular Technology, IEEE Transactions on Intelligent Transportation Systems, IEEE Transactions on Automation Science and Engineering, ACM Transactions on Knowledge
Discovery from Data, ACM Transactions on Intelligent Systems and
Technology, ACM Transactions on the Web, ACM Transactions on Multimedia Computing, Communications, and Applications, WWW, AAAI,
SIGIR, WSDM, CIKM, JCDL, EMNLP, and INFOCOM). His research
interests include data science, artificial intelligence, graph learning, and
systems engineering. He is a senior member of the ACM and an ACM
distinguished speaker.

XIA et al.: COUPLED ATTENTION NETWORKS FOR MULTIVARIATE TIME SERIES ANOMALY DETECTION

Xin Chen received the BSc degree in information security from Harbin Engineering University,
Harbin, China, in 2020. He is currently working toward the master’s degree with the School
of Software, Dalian University of Technology,
China. His research interests include spatiotemporal graph learning, urban science, and social
computing.

Shuo Yu (Member, IEEE) received the BSc
and MSc degrees from the School of Science,
Shenyang University of Technology, China, and
the PhD degree from the School of Software,
Dalian University of Technology, China. She is
currently an associate professor with the School
of Computer Science and Technology, Dalian
University of Technology. She has published
more than 50 papers and received several academic awards, including the IEEE DataCom
2017 Best Paper Award, IEEE CSDE 2020 Best
Paper Award, and ACM/IEEE JCDL 2020 The Vannevar Bush Best
Paper Honorable Mention. She has served as the track chair and PC
member of several international conferences. Her research interests
include data science, graph learning, and knowledge science.

Mingliang Hou received the BSc degree from
Dezhou University, and the MSc degree from
Shandong University, Shandong, China. He is
currently working toward the PhD degree in software engineering with the Dalian University of
Technology, Dalian, China. His research interests include graph learning, city science, and
social computing.

253

Mujie Liu received the BSc degree from Ningbo
Tech University, Ningbo, China, in 2021. She is
currently working toward the PhD degree with
the Institute of Innovation, Science and Sustainability, Federation University Australia, Ballarat,
Australia. Her research interests include graph
learning, anomaly detection, and artificial intelligence.

Linlin You (Member, IEEE) received the PhD
degree in computer science from the University
of Pavia, in 2015. He is an associate professor
with the School of Intelligent Systems Engineering, Sun Yat-sen University, and a research affiliate with the Intelligent Transportation System
Lab, Massachusetts Institute of Technology. He
was a senior postdoc with the Singapore-MIT
Alliance for Research and Technology and a
research fellow with the Architecture and Sustainable Design Pillar of Singapore University
of Technology and Design. He has published more than 40 journal
and conference papers in the research fields of smart cities, service
orchestration, multisource data fusion, machine learning, and federated
learning.
PAPER_TEXT
