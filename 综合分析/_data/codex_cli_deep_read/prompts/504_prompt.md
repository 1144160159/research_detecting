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
# [504] One-Class Classification Constraint in Reconstruction Networks for Multivariate Time Series Anomaly Detection
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
编号：504
题名：One-Class Classification Constraint in Reconstruction Networks for Multivariate Time Series Anomaly Detection
年份：2025
DOI：10.1109/tim.2025.3548251
来源：IEEE Transactions on Instrumentation and Measurement
PDF：paper/10.1109_TIM.2025.3548251.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：时序、日志、KPI 与云原生异常检测、入侵检测与网络异常检测
相关性：中相关，分数 5
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\504.txt
- 原始字符数：64351
- 本次发送字符数：64351
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

3518513

One-Class Classification Constraint
in Reconstruction Networks for Multivariate
Time Series Anomaly Detection
Jiazhen Li , Zhenhua Yu , Qingchao Jiang , Senior Member, IEEE, and Zhixing Cao

Abstract— Detecting the anomalies in multivariate time
series (MTS) data is crucial for maintaining the stability of
industrial manufacturing processes and biochemical operations.
However, current methods often focus on capturing the normal
patterns of training data while overlooking the potential of
latent representations. This research introduces the hypersphere
constraint network (HSC), an innovative self-supervised model
for anomaly detection in MTS. This approach uniquely integrates a one-class classification framework to regulate latent
distribution. First, the HSC employs a temporal convolutional
network (TCN) and a multilayer perceptron (MLP) to extract
latent representations of input data, imposing constraints on the
latent distribution to achieve a one-class loss. Second, a selfattention mechanism is applied to reconstruct the input data
and calculate the reconstruction loss. Anomalies are identified
by combining the one-class loss with the reconstruction loss.
By integrating one-class classification with a reconstruction-based
method, the HSC significantly increases sensitivity to anomalous
data, enhancing the distinction between normal and abnormal
data. Evaluations on three real-world datasets and a simulated
dataset demonstrate that the HSC model outperforms existing
state-of-the-art methods in anomaly detection.
Index Terms— Anomaly detection, deep learning, multivariate
time series (MTS), one-class classification, transformer.

Xinput
xint
xtn
y
yt
X
xn
c
Z
z

N OMENCLATURE
Input multivariate time series data.
Input data at time t.
Input data at time t for the nth variable.
Output label vector representing anomalies.
Output label at time step t.
Input matrix for the encoder.
Feature vector for the nth variable.
Center of the hypersphere in latent space.
Latent representation matrix.
Latent representation.

Received 7 November 2024; accepted 17 December 2024. Date of publication 5 March 2025; date of current version 25 March 2025. This work was
supported in part by the National Natural Science Foundation of China under
Grant 62322309, in part by Shanghai Pilot Program for Basic Research under
Grant 22TQ1400100-16, and in part by Shanghai Science and Technology
Innovation Action Plan under Grant 23S41900500. The Associate Editor coordinating the review process was Dr. Zhigang Liu. (Corresponding authors:
Qingchao Jiang; Zhixing Cao.)
The authors are with the Key Laboratory of Smart Manufacturing in Energy
Chemical Process, Ministry of Education, East China University of Science
and Technology, Shanghai 200237, China (e-mail: y30220958@mail.ecust.
edu.cn; y10210100@mail.ecust.edu.cn; qchjiang@ecust.edu.cn; zcao@ecust.
edu.cn).
Digital Object Identifier 10.1109/TIM.2025.3548251

α
α att
σ (·)
f encoder (·)
H
R
b
X
x̂ nt
WMLP , bMLP
β

Attention score in the self-attention
mechanism.
Linear feedforward network. Used to
calculate the attention score.
Activation function (e.g., ReLU).
Encoder function.
Number of heads used in multihead
attention.
Radius of the hypersphere in latent space.
Reconstructed input data.
Reconstructed feature data at time step t for
the nth variable.
Learnable parameters in MLP.
Hyperparameter balancing one-class and
reconstruction loss.

I. I NTRODUCTION

M

ULTIVARIATE time series (MTS) data are of great significance across various domains. In modern industrial
production, data continuously monitored by sensors reflect the
operating conditions of manufacturing processes [1]. Similarly,
in aerospace missions, hundreds of sensors track the real-time
performance of an aircraft [2], [3]. Such sophisticated systems
require efficient, reliable, and continuous operations, as even
subtle anomalies can lead to severe system failures and significant economic loss [4]. Therefore, prompt identification
and early warning of potential anomalies in MTS are critical.
Efficient MTS anomaly detection methods can assist in timely
discovery of system abnormalities, thereby prompt identification and early warning of potential anomalies in MTS are
critical. Efficient MTS anomaly detection methods averting
drastic consequences.
Anomaly detection in MTS refers to the identification of
data that deviate from the expected distribution within a
collection of interconnected time series [5]. The main challenges in MTS anomaly detection are threefold. First, in real
industrial environments, most data are in a normal state, making it labor-intensive to label anomalous data, which render
supervised methods unsuitable [6]. Second, MTS anomaly
detection involves capturing both complex relationships among
variables and temporal dependencies. Therefore, an effective
MTS anomaly detection method must capture both spatial and
temporal relationships [7]. Lastly, the model must exhibit high
sensitivity to the distribution of anomalous data and give a

1557-9662 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

3518513

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

clear distinction between outputs for normal and anomalous
data [8], [9].
To address the MTS anomaly detection problem, several
feature-based methods from classical unsupervised machine
learning have been developed. OC-SVM [10], [11] reframes
the anomaly detection task as a one-class classification challenge, while SVDD [12] projects latent representations of data
into a hypersphere, classifying normal and anomalous data
based on their positions within this hypersphere. Clustering
strategies such as K -means [13] and DBSCAN [14] designate samples as anomalies when their distance from cluster
centroids exceed a predefined threshold. Principal component analysis (PCA) can be employed to extract statistical
models of normal data, with anomalies identified based on
deviations from principal component scores [15]. TTAD [16]
uses K -means [17] or SMOTE [18] algorithms to augment
the test data, thereby boosting the efficiency and robustness
of anomaly detection. These methods use an unsupervised
approach to achieve anomaly detection. However, they only
capture relationships among variables and neglect temporal
relationships.
Recently, deep learning has gained widespread attention for its exceptional ability to capture both intervariable relationships and temporal dependencies simultaneously.
Current mainstream MTS anomaly detection methods can
be divided into three categories: prediction-based methods, reconstruction-based methods, and distribution-based
methods [19], [20].
A. Prediction-Based Methods
Detect anomalies by analyzing prediction errors. LSTMNDT [21] employs LSTM [22] networks and combines
them with unsupervised dynamic thresholding techniques for
anomaly detection. GDN [23] utilizes graph neural networks to
assess the interconnections across sensors and performs time
series prediction based on attention mechanisms. Deviations
between predicted and actual results are then used to detect
anomalies. The GTA [24] method leverages a Transformerbased architecture to automatically learn graph structures,
apply graph convolution, and model temporal dependencies for
effective MTS anomaly detection. DTAAD [25] model combines temporal convolutional network (TCN) and Transformer
models [26] and improves prediction accuracy through global
and local temporal convolutions via Dual TCN. Additionally,
it leverages meta-learning to enhance anomaly detection performance in scenarios with small sample data.
B. Reconstruction-Based Methods
Identify anomalies by analyzing reconstruction errors [27].
DAGMM [28] combines a deep autoencoder and a Gaussian mixture model to identify anomalies in MTS by
modeling data distributions and detecting deviations using
energy-based representations. MEGA [29] leverages multiscale discrete wavelet transform and graph convolutional
network modules to enhance autoencoder architecture, effectively capturing subtle anomalies. KalmanAE [30] leverages
an autoencoder-optimized Kalman filter to adaptively estimate

normal system states, using deep embeddings to optimize
filter parameters and detect anomalies based on reconstruction
errors from the filtered signal. USAD [5] employs a dual
reconstruction strategy with variational autoencoders (VAEs)
to learn the normal data distribution and detect anomalies
by identifying deviations from these learned distributions.
In MAD-GAN [31], LSTM functions as both generator
and discriminator in a GAN [32], combining the discriminator’s judgment with the generator’s reconstruction loss
to score anomalies. The TranAD [33] method employs an
encoder–decoder structure with adversarial training to amplify
reconstruction errors and improve detection performance.
CAE-AD [34] utilizes a contrastive autoencoder framework
with data augmentation in both time and frequency domains
to achieve robust representations. MANomaly [35] employs a
mutual adversarial network for data reconstruction and implements a high anomaly suppression mechanism to enhance its
effectiveness. D3R [36] uses noise diffusion and a designed
attention structure to address the challenges of MTS anomaly
detection in unstable environments. AT-DCAEP [37] combines
convolutional autoencoders and attention mechanisms to better
capture temporal relationships. In addition to the methods
mentioned above, recent approaches have integrated graph
neural networks to capture relationships among non-Euclidean
data variables [38], [39]. For example, in the GReLeN [40],
the VAE [41] serves as an overall framework, and graph
neural networks are integrated to learn dependencies across
different features. MTAD-GAT [42] leverages graph attention networks (GATs) to capture both temporal dependencies
and intervariable relationships for effective MTS anomaly
detection.
C. Distribution-Based Methods
Introduce normalizing flows, which use a series of invertible transformations to map complex distributions to simpler
ones, thereby estimating data probability [43], [44]. A lower
probability density indicates a higher likelihood of anomalies.
GANF [45] integrates Bayesian networks with normalizing
flows to model conditional dependencies among time series,
enabling effective density estimation and anomaly detection
in MTS. MTGFlow [46] employs dynamic graph structure
learning and entity-aware normalizing flows for unsupervised
anomaly detection, enhancing anomaly detection. Compared to
classical methods, deep learning approaches can better capture
the temporal features of data.
However, these methods primarily focus on capturing the
characteristics of normal data, without emphasizing the distinctions between normal and anomalous data and may not
fully utilize latent data representations.
To address these existing issues, this article proposes the
hypersphere constraint network (HSC) model for anomaly
detection. First, to better understand the temporal dependencies, the HSC model uses a TCN encoder to identify temporal
dependencies. Second, to fully leverage the data in the hidden space, the model applies constraints within the latent
representation, differentiating normal from abnormal data to
amplify the reconstruction loss. Finally, to better extract the

LI et al.: ONE-CLASS CLASSIFICATION CONSTRAINT IN RECONSTRUCTION NETWORKS

features in the latent space, the decoder uses a self-attention
mechanism that combines the GAT [47] and transformer
model [26] to effectively extract features and reconstruct the
input data. Finally, anomaly detection is achieved by merging
the reconstruction and one-class classification losses.
The contributions of this research are as follows.
1) This study introduces a novel network model
named HSC. By integrating one-class classification with
a reconstruction-based neural network, the HSC model
effectively separates normal and anomalous data in the
latent space. This separation amplifies reconstruction
errors and enhances the model’s anomaly detection
capability.
2) To enable effective reconstruction of the input data and
capture the relationships between multivariate data, HSC
utilizes a self-attention mechanism that combines the
GAT and Transformer models to extract features in the
latent representation.
3) In evaluations conducted across three publicly available real-world datasets and six penicillin fermentation
test datasets, the HSC model outperformed other
state-of-the-art methods. These results underscore the
effectiveness of the HSC model in anomaly detection
tasks.
The remainder of this article is organized as follows: Section II presents the preliminary knowledge
of HSC. Section III elaborates on the details of the proposed
method. Section IV evaluates the effectiveness of the HSC
model on three public datasets and six penicillin fermentation
test datasets, assessing its ability to amplify the distinction
between anomalous and normal data. Section V discusses the
scalability and robustness of the HSC model and explores
potential future research directions. Finally, Section VI provides a summary of this study.
II. P RELIMINARY W ORK
In this study, two key methods are employed: TCN [40]
and an attention mechanism. Both approaches have proven
effective in time series analysis.
A. TCN Model
The TCN model, introduced by Bai et al. [48], is an
effective method for capturing temporal data features using
convolutional networks. The TCN consists of three key components: causal convolutions [49], dilated convolutions [50],
and residual connections [51].
Causal convolution [49] prevents the leakage of future
information by introducing an appropriate offset during the
convolution operation. This ensures that the output yt depends
only on the current and past data. The corresponding formula
is given as follows:
yt =

K
−1
X

wk · xt−k

(1)

k=0

where xt−k represents the data at time t − k, K denotes the
kernel size, and wk is the convolution kernel weight.

Fig. 1.

3518513

Overall structure of the TCN model.

Dilated convolution [50] enables TCN to capture long-range
dependencies in sequence data. The formula is expressed as
follows:
K
−1
X
yt =
wk · xt−d·k
(2)
k=0

where d is the dilation factor, i is the current layer in the
hidden state, and d = 2i . The greater the number of hidden
layers, the longer the temporal dependencies that can be
captured.
Residual connections [51] are widely used in deep learning to mitigate the vanishing gradient problem. To capture
longer sequences, TCN require stacking of multiple layers.
To maintain training stability, TCN also incorporate residual
connections. The formula is expressed as follows:
y = σ (x + F(x))

(3)

where x is the input, F(x) represents the transformation
applied to x, and σ is the activation function. The addition
(x + F(x)) provides a direct gradient path, improving the
training stability of deep networks.
The overall architecture of the TCN is illustrated in Fig. 1.
The orange circles represent the nodes observed at the
output yt . Through multiple layers of dilated convolutions, the
model effectively captures long-range sequence features.
B. Attention Mechanism
The design of the attention mechanism is inspired by the
cognitive abilities of humans, where information processing
is not uniform across all data. Humans identify key information and allocate additional cognitive resources to processing
and understanding crucial aspects. Similarly, the attention
mechanism extracts significant features and allocates resources
efficiently [52].
The canonical attention mechanism proposed by
Vaswani et al. [26] is used to overcome the limitations
of traditional RNN methods and capture information from
all positions in long sequence. The principle of obtaining an
attention score is given by


QK T
V
(4)
Attention(Q, K , V ) = softmax √
dk
where dk is a scaling factor. Q, K , and V represent the query,
key, and value, respectively, derived from the input data to
calculate attention scores.

3518513

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

B. Model Overview

Fig. 2.

Overall structure of the multihead attention mechanism.

To enhance model expressivity, the multihead attention
mechanism is often used. This mechanism is a fundamental
and pivotal module within the Transformer model. It runs
the attention mechanism in parallel multiple times, applying
different linear transformations to the original Q, K , and V .
This approach captures various aspects of the input data,
enriching the representation of the input. The concept can be
formulated as follows:
MultiHead(Q, K , V ) = Concat(head1 , . . . , headh )W O


headi = Attention QWiQ , K WiK , V WiV
(5)
where WiQ , WiK , WiV are the projection matrices for the Q, K ,
and V , respectively, for each attention head i.The operation of
multihead attention is illustrated in Fig. 2.
III. P ROPOSED M ETHOD
A. Problem Statement
In the MTS anomaly detection problem, the input data are
denoted by Xinput = (xin1 , xin2 , xin3 , . . . , xinT ) ∈ RT ×N , where
T represents the number of timestamps in the input time
series and N equals the number of features. The data at each
timestamp t are represented as xint = (xt1 , xt2 , xt3 , . . . , xtN ) ∈
R N , where N = 1 for univariate time series and N ≥ 1 for
MTS. The primary aim of MTS anomaly detection is to
identify unusual deviations within the data.
Following the data processing method described in previous
works [23], [31], [40], [42], continuous data segments X =
(x1 , x2 , x3 , . . . , x L ) ∈ R L×W ×N are used as inputs for HSC.
These segments are obtained by applying a sliding window
method, characterized by a window size W , a stride S, and
the number of segments L = (floor(T − W )/S) + 1, where
floor(·) denotes rounding down.
The output is y = (y1 , y2 , y3 , . . . , yT ) ∈ RT , yt ∈ {0, 1}.
This vector represents the anomaly detection results at each
timestamp. Specifically, an output value of 1 indicates an
anomaly at time t, while a value of 0 signifies that no anomaly
is detected.
The variables used in our proposed method are summarized
in Nomenclature.

The HSC model utilizes an encoder–decoder architecture,
as illustrated in Fig. 3, and is a reconstruction-based neural
network designed for anomaly detection in MTS.
Encoder: The encoder processes the input data through a
sliding window method and employs a TCN model to capture
temporal dependencies in MTS. After applying the TCN,
the data are transformed into a latent space through linear
mapping. The distribution in latent space is controlled by a
modified one-class classification loss function to better handle
latent representations.
Decoder: The primary function of the decoder is to reconstruct the input data from the latent representation and compute
the reconstruction loss. The core of the decoder network is
a self-attention mechanism, which differs from the canonical
version by incorporating the GAT [47] model. This incorporation enhances the flexibility of attention score calculation.
The final loss score, which combines the reconstruction loss
and the one-class classification loss, effectively evaluates data
abnormalities.
C. Encoder and One-Class Classification Loss
In the encoder module, two primary tasks are performed.
The first task is to set the center of the data in the latent
space. In this study, the method from the COUTA [53] model
is adopted, where the initial encoder output point is set as the
data center.
The second task involves finding a latent space representation for the decoder input, similar to standard encoder–decoder
models. To better capture temporal features, the encoder of
the HSC model employs both TCN and multilayer perceptron (MLP). As represented by (6), these two modules are
used to derive the latent space representation
h
i
(K )
(K −1)
(1)
f encoder = f TCN
◦ f TCN
◦ · · · ◦ f TCN
(X) WMLP1 + bMLP1
(6)
where K represents the number of TCN layers used in the
encoder, WMLP1 and bMLP1 are the parameters of the MLP.
To fully utilize the latent representation, HSC adopts a
method similar to SVDD [12], projecting normal data into
the hypersphere’s interior. The loss function for this task is
given by
Lossorig = Ex∼X [∥ f (x) − c ∥2 ]

(7)

where f (·) the denotes the feature extraction process, and c
represents the center of the hypersphere. Optimizing this loss
function ensures normal data maps inside the hypersphere,
while anomalies are mapped outside.
However, using (7) as the loss function can centralize normal data near the hypersphere’s center, reducing its
radius and causing similar representations. This diminishes
unique features and compromises the effectiveness of TCN.
Consequently, the downstream decoder struggles to extract
reliable features for reconstruction. An optimized loss function, as shown in (8), addresses this by projecting data onto the
hypersphere’s surface, preserving more features and alleviating

LI et al.: ONE-CLASS CLASSIFICATION CONSTRAINT IN RECONSTRUCTION NETWORKS

Fig. 3.

3518513

Overall structure of HSC.

original input is to the reconstructed output. The architecture
of the decoder consists of two fundamental components: a
self-attention mechanism and linear mapping.
To some extent, self-attention can be viewed as a self-loop
in the GAT model. The key difference between these two
mechanisms lies in how they compute the attention score.
As illustrated in (4), the canonical attention uses the dot
product to compute the attention score. In GAT, the attention
score is computed using a feedforward neural network. This
method of computing the attention score is known as the
“additive attention mechanism” also referred to as “Bahdanau
attention” [54]. Compared with the canonical attention mechanism, this method provides greater flexibility and the ability
to learn complex patterns.
In the HSC model, the attention score is calculated as
follows:
Fig. 4. Comparison of the effects of original one-class classification loss
function and optimized loss function in HSC. (a) Effect of the original loss
function. (b) Effect of the optimized loss function in HSC.

the issue of feature disappearance
Z = f encoder (X),

Z = (z1 , z2 , . . . , z N )

Lossone-class = Ez∼Z (||z − c|| − R)2

(8)
W ×1

where R is the hypersphere radius, zi ∈ R
represents the
latent representation after the encoder module.
The effects of the original one-class loss function and the
optimized loss function are illustrated in Fig. 4. Fig. 4(a)
shows the effect of applying the original loss function to the
latent representation, where normal data tend to centralize
around the hypersphere’s center during training. In contrast,
Fig. 4(b) demonstrates the effect of the optimized loss function
as defined by (8), where the data are projected onto the surface
of the hypersphere. This approach significantly preserves more
features of the data by ensuring that the unique characteristics
of data point are maintained on the hypersphere’s surface.
D. Decoder and Reconstruction Loss
In decoder, the primary task is to reconstruct data by
using the previously obtained latent representation. The extent
of reconstruction is determined by comparing how similar the

T
α = σ (α att
(wz))

(9)

V ×W

where w ∈ R
represents a transformation matrix. The activation function σ (·) computes α, the attention score α att ∈ RV
represents the parameters of the feedforward network used to
calculate the attention score. These parameters are updated
iteratively during network training.
After obtaining the attention score, the output is calculated
using a layer of linear transformation, with parameters determined by wout ∈ R N ×V . The output denoted as z′ ∈ R N is
calculated according to the following equation:
z′ = σ [wout (α · wz)].

(10)

HSC also incorporates a multihead attention mechanism.
The multihead attention score is computed as follows:
  T

exp σ α att
(wh z)
h
(11)
αh = P H
  T

k
k=1 exp σ α attk (w z)
where H represents the number of heads. The SoftMax operation is applied after calculating the attention score for each
head. In the GAT model, SoftMax operation is applied across
adjacent nodes. However, self-attention inherently applies a
self-loop graph, where adjacent nodes essentially refer to
themselves. This can result in all output attention scores
converging to 1. For this situation to be avoided, the SoftMax
operation is applied across each head rather than each node.

3518513

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

The final output of the self-attention module is computed
based on the calculated scores, following the same approach as
canonical attention. The output of each head is concatenated
and linearly transformed using Wout ∈ R N ×(V ·H ) . After passing
through an activation function σ (·) and an MLP transformation
which is defined by WMLP2 and bMLP2 , the final output is
 


H
x̂ = WMLP2 σ Wout || αh · wz
+ bMLP2 .
(12)

TABLE I
D ETAILS OF THE DATASETS

h=1

The reconstructed data b
X = (b
x1 ,b
x2 ,b
x3 , . . . ,b
xT ) ∈ RT ×N
are obtained. By comparing the reconstructed output with the
input data using MSE, the reconstruction loss can be computed
as follows:
T
N
2
1 XX n
(13)
x̂ t − xtn .
Lossrecon =
T × N t=1 n=1
E. Anomaly Detection
In HSC, the final error score is calculated by combining the
reconstruction loss and the one-class classification loss. A ratio
hyperparameter, denoted as β ∈ [0, 1], is used to calculate the
final loss score, as shown in the following equation:
Score = ||b
x − x|| + β × (|| f encoder (x) − c|| − R)2 .

(14)

Anomalies are determined based on the final loss score.
If the score exceeds a predetermined threshold, the associated
timestamp is classified as an anomaly. Most anomaly detection
methods adopt a point adjustment (PA) strategy to refine
their outputs and determine a suitable threshold. However,
the details of the PA strategy and threshold-setting method
vary depending on the application scenario. For instance, the
method in [55] uses the PA%K method to adjust results for
different anomaly types. In [1] and [42], the threshold is
dynamically adjusted according to the anomaly scores.
This work primarily emphasizes the network framework
design for efficient MTSs anomaly detection. Hence, HSC
follows prior works [21], [34], [40], [53], adjusting its results
and performs a grid search over potential thresholds, selecting
the one yielding the best F1 scores.
IV. E XPERIMENTS
The effectiveness of the proposed method was validated
through several experiments. First, three public datasets for
MTS anomaly detection were used as standard test cases
to demonstrate the method’s capabilities and compare the
results with other methods. Second, ablation studies assessed
the impact of applying one-class constraints in the latent
space and evaluated the modified attention mechanism in the
decoder. Third, parameter sensitivity analysis was conducted
to thoroughly explore the characteristics of HSC. Finally,
a simulated penicillin dataset was used as an application test
case to perform a comprehensive analysis of performance
under various anomaly scenarios.
A. Datasets and Metrics
1) Datasets: Four datasets were employed to evaluate the
effectiveness of the proposed method: Secure Water Treatment
(SWaT) [56], the Mars Science Laboratory Rover (MSL)

dataset [3], Server Machine dataset (SMD) [1], and the Penicillin Simulation dataset [57].
The first three datasets are real-world datasets commonly
utilized in the field of anomaly detection for MTS. These
datasets were chosen as standard test cases in this research
because they cover a wide range of characteristic scenarios,
ensuring the generalizability of HSC.
The penicillin simulation dataset, generated based on the
simulation platform described in [57], includes 100 batches of
normal data used as training data and six batches of test data.
The test data were designed cover different fault causes, fault
variables, and fault time zones to achieve a comprehensive
validation of the proposed method. The characteristics of the
four datasets are presented in Table I.
2) Evaluation Metrics: In the experiments, the precision (P), recall (R), F1, and AUC score were adopted as
metrics to evaluate the performance of the proposed model.
The formulas for these metrics are given by the following
equations:
TP
Precision =
(15)
TP + FP
TP
Recall =
(16)
TP + FN
Precision × Recall
F1 = 2 ×
(17)
Precision + Recall


Z 1
TP
FP
AUC =
d
.
(18)
TP
+
FN
FP
+ TN
0
In the task of anomaly detection, TP refers to correctly
flagged anomalies. FP denotes normal data that are incorrectly
classified as anomalies, and FN represents actual anomalies
that are mistakenly identified as normal data. In MTS anomaly
detection, precision indicates the proportion of correctly identified anomalies among all flagged anomalies, while recall
represents the proportion of detected anomalies among all
actual anomalies. The F1 score combines precision and recall,
providing a balanced measurement. AUC, which measures the
area under the ROC curve, provides an aggregate performance
measure across all classification thresholds.
B. Standard Test Cases
1) Benchmark Comparison:
a) Baseline models: The efficacy of the proposed method
was compared with several state-of-the-art methods. The
proposed method incorporates techniques from one-class classification, self-attention, autoencoder, and the GAT model.

LI et al.: ONE-CLASS CLASSIFICATION CONSTRAINT IN RECONSTRUCTION NETWORKS

3518513

TABLE II
P ERFORMANCE C OMPARISON OF HSC W ITH OTHER BASELINE M ETHODS ON T HREE P UBLIC DATASETS

Therefore, eight methods were selected as benchmarks:
COUTA [53], TranAD [33], GReLeN [40], GDN [23], MTADGAT [42], CAE-AD [34], DeepSVDD [58], and anomaly
transformer [9]. Among these methods, Deep SVDD [58]
and COUTA [53] utilize one-class classification for anomaly
detection. TranAD [33] and anomaly transformer [9] employ
transformer architectures to extract features for anomaly
detection. CAE-AD [34] uses an autoencoder framework
for reconstruction-based anomaly detection. Finally, GReLeN [40], GDN [23], and MTAD-GAT [42] leverage graph
neural networks to achieve high-efficiency anomaly detection.
b) Results and analysis: The results presented in Table II
are derived from ten independent repeated experiments to
ensure the robustness and reliability of the findings. For
each method, we report the average values along with the
corresponding standard deviations.
The HSC model demonstrates outstanding performance
across all four metrics. Specifically, it achieves the highest
F1 score on all datasets, with improvements of 1.1%, 6.3%,
and 1.4% on the SMD, SWaT, and MSL datasets, respectively,
compared to the second-best method, highlighting its superior
anomaly detection capability. In addition to F1 scores, the
HSC model also achieves the highest AUC scores on all
three datasets, with increases of 1.7%, 1.6%, and 2%. The
model also shows strong competitiveness in terms of precision
and recall. Moreover, across ten repeated experiments, the
standard deviation is consistently below 0.04, demonstrating
the robustness and stability of the HSC model. Although recall
and precision did not achieve the highest scores across all
datasets, they are still highly competitive.
Among the compared methods, DeepSVDD underperformed, primarily because it is not designed for MTS anomaly
detection and lacks the ability to capture temporal dependencies, focusing only on inter-variable relationships. This
limitation impacts its effectiveness in MTS anomaly detection.
COUTA, being a purely one-class classification-based method,
lacks a sufficient understanding of data distribution compared to reconstruction-based models, resulting in relatively
weaker performance. CAE-AD, while using an autoencoder
and contrastive learning, does not fully utilize the latent

Fig. 5.

Log ratio of anomaly-to-normal scores for models.

space distribution as effectively as HSC. Methods such as
GDN, GReLeN, and MTAD-GAT use graph neural networks
to capture inter-variable relationships. However, their focus
on modeling normal data makes it harder to detect subtle anomalies. TranAD and Anomaly Transformer, based on
transformer architectures, are more complex and prone to overfitting, especially when training data are limited, as seen in the
SMD and MSL datasets, resulting in suboptimal performance.
The proposed HSC model is capable of capturing both temporal dependencies and intervariable relationships. By applying a HSC in the latent space, HSC effectively differentiates
between normal and anomalous data, enhancing its ability
to detect subtle anomalies that may be overlooked by other
models. Additionally, compared to purely reconstruction-based
or prediction-based models, HSC benefits from the integration
of one-class classification loss and reconstruction loss, which
contributes to its robustness.
c) Anomaly distinction: To validate the effectiveness
of HSC in enhancing the distinction between normal and
anomalous data, we first calculate the average score of normal
data Sn and anomalous data Sa ; then compute the ratio of
these two scores. The formula for this calculation is given
by log(Sa /Sn ), The results, as shown in Fig. 5, demonstrate
that HSC achieves the highest distinction between normal and
anomalous data across all three datasets.
d) Case study: To further demonstrate the effectiveness
of latent space constraints in the HSC model, the machine-1-1

3518513

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

Fig. 7. Comparison of F1 scores between having and not having latent space
restrictions across the three public datasets.

Fig. 8. Comparison of F1-score between the using GAT, Transformer as the
decoder of HSC, and original HSC decoder.

Fig. 6. Case study. (a) Visualization of four dimensions from the machine-1-1
dataset, where the black line represents the ground truth, the red line represents
the model’s predictions, and the five red-shaded areas indicate the time points
when anomalies occurred. (b) Anomaly scores with latent space constraints
applied. (c) Anomaly scores without latent space constraints.

dataset from the SMD benchmark is selected as a case
study. Specific dimensions of the reconstruction results are
visualized, and anomaly scores with and without latent space
constraints are compared, as illustrated in Fig. 6. The model
in Fig. 6(a) exhibits robust reconstruction capability for normal
data. The results in Fig. 6(b) and (c) indicate that the inclusion
of latent space constraints significantly improves the model’s
ability to distinguish between normal and anomalous data.
Notably, in the absence of the HSC, as shown in Fig. 6(c),
increased background noise in the anomaly scores is observed,
and high anomaly scores occur after the anomaly ends. These
findings highlight the importance of latent space constraints
in mitigating noise interference and enhancing the accuracy
of anomaly detection.
2) Ablation Test: The impact of constraining the distribution of representations in the latent space needs to be assessed.
Comparative experiments were conducted by removing this

constraint and assessing its effects on three datasets. The
results, using F1 as an evaluation metric, are shown in Fig. 7.
After removing the constraint in the latent space, the overall
average F1 score decreased by 6.23%. The smallest decrease
was observed on the SMD dataset, with a 3.9% reduction in
F1 score. The most significant decrease, 9.5%, was observed
on the SWaT dataset. These results indicate that applying constraints within the latent space significantly enhances anomaly
detection capability.
In the HSC model’s decoder, self-attention was employed
for feature extraction. The attention mechanisms of both GAT
and the transformer were then integrated into the framework.
The effectiveness of combining these two mechanisms was
assessed in this study. The self-attention mechanism in the
decoder was replaced by the attention mechanisms from the
transformer model and GAT. As shown in Fig. 8, the HSC
model achieved the best performance across the three datasets.
When the decoder’s self-attention module was substituted with
GAT, the average F1 score decreased by approximately 3%.
When the transformer model was used, the F1 score decreased
by 5.6%. The most significant improvement achieved using
the HSC model was on the SMD dataset. When GAT and the
transformer model were used, the F1 scores were only 88.2%
and 88.6%, respectively; by contrast, the F1 score of the HSC
model was 95.1%. These results demonstrate that combining
GAT and transformer architectures can effectively improve the
model’s capabilities.
3) Hyperparameter Sensitivity Analysis: This section analyzes the sensitivity of the proposed method to two crucial
hyperparameters: the hypersphere radius R and the ratio
hyperparameter β. The analysis is performed on the SWaT,
MSL (D-14), and SMD (machine-1-1) datasets.

LI et al.: ONE-CLASS CLASSIFICATION CONSTRAINT IN RECONSTRUCTION NETWORKS

3518513

TABLE III
I NFORMATION ON S IX A BNORMAL S ETTINGS
IN P ENICILLIN S IMULATION P ROCESS

Fig. 9. Reconstruction loss on different datasets (SWaT, MSL, and SMD)
with varying R values.

Fig. 10. AUC score on different datasets (SWaT, MSL, and SMD) with
varying β values.

of balancing the one-class loss and reconstruction loss for the
model. Setting β between 0.5 and 1 is a reasonable range.
C. Application Test Case

a) Hypersphere radius R: Our experiments reveal that
the hypersphere radius impacts feature retention and data
reconstruction. By varying R from 0 to 3 in increments of 0.1,
we assessed the reconstruction loss on each dataset, as shown
in Fig. 9.
1) SWaT: Small radius values cause significant fluctuations
in reconstruction loss. As R increases, the loss stabilizes, indicating that a larger radius ensures consistent
reconstruction performance.
2) MSL: The reconstruction loss consistently decreases
with an increasing radius, suggesting that a larger R
enhances the model’s reconstruction ability.
3) SMD: Although some fluctuations are observed, the
reconstruction loss generally decreases as the radius
increases, confirming that a larger R reduces reconstruction errors
In summary, a larger hypersphere radius R helps maintain
consistent and improved reconstruction performance across
different datasets.
b) Ratio hyperparameter β: To verify the impact of β on
the results, β was varied from 0 to 2 in increments of 0.1. The
AUC score under different β conditions are shown in Fig. 10.
1) SWaT: The AUC score increases as β approaches 1,
after which it starts to decline. This indicates that
a balanced emphasis on both losses leads to optimal
anomaly detection performance.
2) MSL: The AUC score reaches its maximum at β values around 0.5. Beyond this point, the performance
decreases. When β is greater than 1, the AUC score
remains relatively stable.
3) SMD: The AUC score peaks at β values around 0.6,
following this, the AUC score decreases similar to MSL,
though the decline is more gradual.
In summary, excessively large or small β values negatively impact the results. This demonstrates the importance

The capabilities of the HSC model were also evaluated
in this study. In particular, the complex process of penicillin
fermentation was introduced to assess the performance of the
HSC model under various anomalous conditions. This process
represents a typical dynamic and multistage batch production
process with long operational cycles and relatively complex
reactions. The penicillin fermentation simulation platform
“Pensim,” developed by Professor Cinar’s research group [57].
Pensim simulates growth variations across variables under
diverse production conditions, offering a standardized platform
for detecting anomalies in multivariate time-series data.
In this simulation platform, the duration of the entire fermentation reaction was set to 400 h, with data sampled every
hour, incorporating 16 variables. The training dataset included
100 instances of normal fermentation operations. Pensim
allows for the introduction of faults in three variables: aeration
rate, agitation power, and substrate feed rate. These faults are
categorized into step and ramp types, and their magnitude and
timing can be artificially set. During simulation, six different
sets of anomalous variable data, with specific conditions for
anomaly timing and types, were generated to validate the
effectiveness of the HSC model, as shown in Table III.
Comparisons were also performed with COUTA [53],
TranAD [33], GReLeN [40], GDN [23], MTAD-GAT [42], and
CAE-AD [34], DeepSVDD [58], and anomaly transformer [9].
The F1 score, precision, recall, and AUC score were used
as metrics. Each experiment was repeated ten times with
different random seeds. The comparative results are displayed
in Table IV.
Experimental results indicate that for the first two types of
anomaly patterns, all models were capable of effectively locating the occurrence of faults. However, the TranAD, GReLeN,
GDN, DeepSVDD, anomaly transformer, and MTAD-GAT
models experienced false positives in the first four relatively straightforward test datasets, failing to achieve 100%
precision. By contrast, the COUTA, CAE-AD, and HSC

3518513

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

TABLE IV
P ERFORMANCE C OMPARISON OF HSC W ITH OTHER BASELINE M ETHODS ON S IX P ENISM DATASETS

models performed flawlessly on the first four datasets, captured
anomalies with precision, and achieved an F1 score of 100%.
In the last two datasets, where anomalies were subtler and
posed greater detection challenges. The HSC model demonstrated its superior anomaly detection capability. Specifically,
HSC achieved the highest F1 scores on both the Penism5
and Penism6 datasets, with scores of 98.9% and 98.5%,
respectively. The AUC scores for HSC were also the highest: 87.1% on Penism5 and 85.3% on Penism6, representing
improvements of 5.2% and 8.7% over the next best methods,
respectively.
a) Anomaly distinction: In Penism dataset, to demonstrate the distinction between normal and anomalous data
for the HSC model, the same calculation was performed for
different models on various datasets. The anomaly distinction
score, log(Sa /Sn ), is presented in Fig. 11. On all six test
datasets, the HSC model consistently achieved the highest
scores. On the first four datasets, all models could effectively
distinguish between normal and anomalous patterns. However,
the models’ capabilities diverged on the Penism5 and Penism6
datasets. In particular, GDN, CAE-AD, GReLeN, DeepSVDD,
and anomaly transformer, exhibited negative scores which

Fig. 11. Log ratio of anomaly to normal data scores across models on six
Penism test datasets.

indicate an inability to effectively discriminate between normal
and anomalous data.
V. D ISCUSSION
In this section, the discussion focuses on the potential challenges the HSC model may encounter in real-world industrial
environments, particularly regarding its scalability and robustness to noise. In addition, the section provides an analysis of
potential future research directions for the HSC model.

LI et al.: ONE-CLASS CLASSIFICATION CONSTRAINT IN RECONSTRUCTION NETWORKS

3518513

degrades in environments characterized by high levels of noise
interference.
C. Future Research Directions

Fig. 12. AUC variation of the SWaT dataset and MSL D-14 dataset under
different noise levels.

A. Scalability
The primary computational bottleneck in the HSC model
stems from two factors: the 1-D convolution operation in the
TCN and the self-loop attention mechanism.
The time complexity of the TCN’s 1-D convolution is
O(W · k · N ), where W represents the sliding window length,
k is the kernel size, and N is the feature dimension. Given
its linear complexity, the model exhibits good scalability for
handling long sequence data.
For the self-loop attention mechanism, the time complexity
of embedding transformation is O(W · N 2 ). The complexity
of computing attention scores is O(W · N ), while applying
attention weights has a complexity of O(W · N 2 ). Given that
the window size can be adjusted, the complexity is primarily
constrained by the number of variables N .
Overall, the computational bottleneck in the HSC model is
largely determined by the number of variables in the data.
Nevertheless, it is particularly well suited for capturing global
relationships within the data, which are critical for MTS
anomaly detection tasks.
B. Robustness to Noise
To assess the robustness of the HSC model in industrial
scenarios, robustness experiments were performed on the
SWaT and MSL D-14 datasets. Gaussian noise with varying
intensities was introduced to both datasets, where the noise
intensity was controlled by the standard deviation (std) of the
Gaussian distribution. The std ranged from 0 to 1, increasing in
steps of 0.1. Each experiment was repeated five times, and the
average AUC scores were calculated for analysis. The results
are shown in Fig. 12.
As depicted in Fig. 12, when the noise level is low
(std ≤ 0.1), the model’s performance remains stable, with
AUC scores showing minimal variation, demonstrating strong
robustness. In moderate noise scenarios (0.1 < std ≤ 0.4),
slight fluctuations are observed; however, the overall performance remains satisfactory. However, under high noise
conditions (std > 0.4), the AUC scores drop significantly,
indicating that the model is sensitive to high levels of noise.
In conclusion, the HSC model demonstrates a certain
level of robustness to noise; however, its performance

The HSC model has demonstrated strong capabilities in
detecting MTS anomalies. However, to enhance its effectiveness in real-world production settings and to reduce losses,
there remains room for improvement.
First, although the HSC model exhibits strong performance
in various experiments, its reconstruction effectiveness is
sensitive to the radius of the hypersphere. Different datasets
require distinct hypersphere radii, and currently, there is
no effective method to determine the optimal radius. This
necessitates manual tuning for each dataset based on specific
application scenarios. We infer that this sensitivity may stem
because imposing constraints in the latent space inevitably
leads to the loss of certain important features. Therefore, future
research could focus on exploring ways to limit the distribution
of data in the latent space while minimizing feature loss,
in order to reduce the model’s sensitivity to hyperparameters.
Second, current MTS anomaly detection primarily focuses
on identifying the moment when an anomaly occurs, providing
early warnings. However, to more effectively reduce losses,
early warnings alone are insufficient; root cause analysis is
also required. Through root cause analysis, the specific cause
and location of the anomaly can be quickly identified, enabling
timely intervention and minimizing potential losses. Therefore,
future research could further explore how to integrate anomaly
detection with root cause analysis, enhancing the practical
utility and efficiency of handling anomalies.
VI. C ONCLUSION
This article proposes a new network architecture, termed
HSC, designed to address the challenge of anomaly detection
in MTS. First, HSC combines the one-class classification
with reconstruction-based deep learning method to accentuate
the distinctions between normal and anomalous data. Second,
HSC leverages a self-attention mechanism, integrating the
Transformer and GAT, to enhance input data reconstruction.
In the end, by combining the one-class classification loss and
reconstruction loss, HSC computes the final loss score, which
serves as a basis for anomaly detection.
Extensive experiments conducted on multiple datasets
demonstrate that the HSC model offers significant advantages
over baseline models, particularly in its ability to enhance
the distinction between normal and anomalous data, thus
improving anomaly detection performance. The effectiveness of the model’s components has been validated through
ablation studies, which underscore the contributions of each
module to the overall performance. Furthermore, noise experiments demonstrate the model’s robustness, indicating its
capability to perform reliably even in complex and noisy
environments.
Future research may focus on developing more efficient
approaches for constraining data distribution within the latent
space, with an emphasis on minimizing feature loss and reducing the model’s sensitivity to hyperparameters. Additionally,
incorporating root cause analysis into the framework could

3518513

IEEE TRANSACTIONS ON INSTRUMENTATION AND MEASUREMENT, VOL. 74, 2025

enable the rapid identification of anomaly causes and locations,
further enhancing the model’s ability to provide early warnings
and support timely intervention.
R EFERENCES
[1] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discovery Data
Mining, Anchorage, AK, USA, Jul. 2019, pp. 2828–2837.
[2] J. Yu, Y. Song, D. Tang, D. Han, and J. Dai, “Telemetry data-based
spacecraft anomaly detection with spatial–temporal generative adversarial networks,” IEEE Trans. Instrum. Meas., vol. 70, pp. 1–9, 2021, doi:
10.1109/TIM.2021.3073442.
[3] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and
T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric dynamic thresholding,” in Proc. 24th ACM SIGKDD Int.
Conf. Knowl. Discovery Data Mining, Jul. 2018, pp. 387–395.
[4] H. Liang, L. Song, J. Du, X. Li, and L. Guo, “Consistent anomaly detection and localization of multivariate time series via cross-correlation
graph-based encoder–decoder GAN,” IEEE Trans. Instrum. Meas.,
vol. 71, pp. 1–10, 2022, doi: 10.1109/TIM.2021.3139696.
[5] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: UnSupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining,
Virtual Event, CA, USA, Aug. 2020, pp. 3395–3404.
[6] Y. Yang, H. Zhang, and Y. Li, “Long-distance pipeline safety early
warning: A distributed optical fiber sensing semi-supervised learning
method,” IEEE Sensors J., vol. 21, no. 17, pp. 19453–19461, Sep. 2021,
doi: 10.1109/JSEN.2021.3087537.
[7] C. Zhang et al., “A deep neural net-work for unsupervised
anomaly detection and diagnosis in multivariate time series data,”
in Proc. 33rd AAAI Conf. Artif. Intell., Honolulu, HI, USA, 2019,
pp. 1409–1416.
[8] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “DCdetector: Dual
attention contrastive representation learning for time series anomaly
detection,” in Proc. 29th ACM SIGKDD Conf. Knowl. Discovery Data
Mining, Long Beach, CA, USA, Aug. 2023, pp. 3033–3045.
[9] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time
series anomaly detection with association discrepancy,” in Proc. Int.
Conf. Learn. Represent., Vienna, Austria, 2022, pp. 1–20.
[10] B. Schölkopf, R. C. Williamson, A. Smola, J. Shawe-Taylor, and J. Platt,
“Support vector method for novelty detection,” in Proc. 12th Int. Conf.
Neural Inf. Process. Syst., vol. 12, Denver, CO, USA, Nov. 1999,
pp. 582–588.
[11] J. Ma and S. Perkins, “Time-series novelty detection using one-class
support vector machines,” in Proc. Int. Joint Conf. Neural Netw., 2003,
pp. 1741–1745.
[12] D. M. J. Tax and R. P. W. Duin, “Support vector data description,” Mach. Learn., vol. 54, no. 1, pp. 45–66, 2004, doi:
10.1023/B:MACH.0000008084.60811.49.
[13] J. MacQueen, “Some methods for classification and analysis of multivariate observations,” in Proc. 5th Berkeley Symp. Math. Statist. Probab.,
1967, pp. 281–297.
[14] M. Ester, H. Kriegel, J. Sander, and X. Xu, “A density-based algorithm
for discovering clusters in large spatial databases with noise,” in Proc.
2nd Int. Conf. Knowl. Discov. Data Min., Port-land, OR, USA, Jan. 1996,
pp. 226–231.
[15] M. Shyu, S. Chen, K. Sarinnapakorn, and L. Chang, “A novel
anomaly detection scheme based on principal component classifier,”
in Proc. Int. Conf. Data Min, Melbourne, FL, USA, Jan. 2003,
pp. 172–179.
[16] S. Cohen, N. Goldshlager, L. Rokach, and B. Shapira, “Boosting anomaly detection using unsupervised diverse test-time augmentation,” Inf. Sci., vol. 626, pp. 821–836, May 2023, doi:
10.1016/j.ins.2023.01.081.
[17] S. Lloyd, “Least squares quantization in PCM,” IEEE Trans.
Inf. Theory, vol. IT-28, no. 2, pp. 129–137, Mar. 1982, doi:
10.1109/TIT.1982.1056489.
[18] N. V. Chawla, K. W. Bowyer, L. O. Hall, and W. P. Kegelmeyer,
“SMOTE: Synthetic minority over-sampling technique,” J. Artif. Intell.
Res., vol. 16, pp. 321–357, Jun. 2002, doi: 10.1613/jair.953.
[19] Z. Li et al., “Multivariate time series anomaly detection and interpretation using hierarchical inter-metric and temporal embedding,” in Proc.
27th ACM SIGKDD Conf. Knowl. Discovery Data Mining, Aug. 2021,
pp. 3220–3230.

[20] Y. Zheng et al., “Graph spatiotemporal process for multivariate time
series anomaly detection with missing values,” Inf. Fusion, vol. 106,
Jun. 2024, Art. no. 102255, doi: 10.1016/j.inffus.2024.102255.
[21] C. Yin, S. Zhang, J. Wang, and N. N. Xiong, “Anomaly detection based
on convolutional recurrent autoencoder for IoT time series,” IEEE Trans.
Syst. Man, Cybern. Syst., vol. 52, no. 1, pp. 112–122, Jan. 2022, doi:
10.1109/TSMC.2020.2968516.
[22] S. Hochreiter and J. Schmidhuber, “Long short-term memory,”
Neural Comput., vol. 9, no. 8, pp. 1735–1780, 1997, doi:
10.1162/neco.1997.9.8.1735.
[23] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 4027–4035.
[24] Z. Chen, D. Chen, X. Zhang, Z. Yuan, and X. Cheng, “Learning
graph structures with transformer for multivariate time-series anomaly
detection in IoT,” IEEE Internet Things J., vol. 9, no. 12, pp. 9179–9189,
Jun. 2022, doi: 10.1109/JIOT.2021.3100509.
[25] L.-R. Yu, Q.-H. Lu, and Y. Xue, “DTAAD: Dual TCN-attention
networks for anomaly detection in multivariate time series data,”
Knowl.-Based Syst., vol. 295, Jul. 2024, Art. no. 111849, doi:
10.1016/j.knosys.2024.111849.
[26] A. Vaswani et al., “Attention is all you need,” in Proc. 31st Int. Conf.
Neural Inf. Process. Syst., vol. 30, Long Beach, CA, USA, Jun. 2017,
pp. 5998–6008.
[27] Y. Bai, J. Wang, X. Zhang, X. Miao, and Y. Lin, “CrossFuN: Multiview joint cross-fusion network for time-series anomaly detection,”
IEEE Trans. Instrum. Meas., vol. 73, 2024, Art. no. 10254685, doi:
10.1109/TIM.2024.10254685.
[28] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Represent.,
Vancouver, BC, Canada, May 2018, pp. 1–19.
[29] J. Wang, S. Shao, Y. Bai, J. Deng, and Y. Lin, “Multiscale
wavelet graph AutoEncoder for multivariate time-series anomaly detection,” IEEE Trans. Instrum. Meas., vol. 72, pp. 1–11, 2023, doi:
10.1109/TIM.2022.3223142.
[30] X. Huang, F. Zhang, R. Wang, X. Lin, H. Liu, and H. Fan, “KalmanAE:
Deep embedding optimized Kalman filter for time series anomaly
detection,” IEEE Trans. Instrum. Meas., vol. 72, pp. 1–11, 2023, doi:
10.1109/TIM.2023.3329098.
[31] D. Li, D. Chen, B. Jin, L. Shi, J. Goh, and S.-K. Ng, “MAD-GAN:
Multivariate anomaly detection for time series data with generative
adversarial networks,” in Proc. Int. Conf. Artif. Neural Netw., Munich,
Germany, Jan. 2019, pp. 703–716.
[32] I. Goodfellow et al., “Generative adversarial networks,” Commun. ACM,
vol. 63, no. 11, pp. 139–144, Oct. 2020, doi: 10.1145/3422622.
[33] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” Proc.
VLDB Endowment, vol. 15, no. 6, pp. 1201–1214, Feb. 2022, doi:
10.14778/3514061.3514067.
[34] H. Zhou, K. Yu, X. Zhang, G. Wu, and A. Yazidi, “Contrastive
autoencoder for anomaly detection in multivariate time series,” Inf. Sci.,
vol. 610, pp. 266–280, Sep. 2022, doi: 10.1016/j.ins.2022.07.179.
[35] L. Zhang, X. Xie, K. Xiao, W. Bai, K. Liu, and P. Dong, “MANomaly:
Mutual adversarial networks for semi-supervised anomaly detection,”
Inf. Sci., vol. 611, pp. 65–80, Sep. 2022, doi: 10.1016/j.ins.2022.08.033.
[36] C. Wang et al., “Drift doesn’t matter: Dynamic decomposition with
diffusion reconstruction for unstable multivariate time series anomaly
detection,” in Proc. 37th Int. Conf. Neural Inf. Process. Syst., New
Orleans, LA, USA, 2024, p. 473.
[37] W. Liu et al., “Unsupervised deep anomaly detection for industrial
multivariate time series data,” Appl. Sci., vol. 14, no. 2, p. 774, Jan. 2024,
doi: 10.3390/app14020774.
[38] J. Zhou et al., “Graph neural networks: A review of methods
and applications,” AI Open, vol. 1, pp. 57–81, Jan. 2020, doi:
10.1016/j.aiopen.2021.01.001.
[39] M. M. Bronstein, J. Bruna, Y. LeCun, A. Szlam, and P. Vandergheynst,
“Geometric deep learning: Going beyond Euclidean data,” IEEE
Signal Process. Mag., vol. 34, no. 4, pp. 18–42, Jul. 2017, doi:
10.1109/MSP.2017.2693418.
[40] W. Zhang, C. Zhang, and F. Tsung, “GRELEN: Multivariate time series
anomaly detection from the perspective of graph relational learning,”
in Proc. 31st Int. Joint Conf. Artif. Intell., Vienna, Austria, Jul. 2022,
pp. 2390–2397.
[41] D. P. Kingma and M. Welling, “Auto-encoding variational Bayes,” in
Proc. 2nd Int. Conf. Learn. Represent., Banff, AB, Canada, Apr. 2014,
pp. 1–14.

LI et al.: ONE-CLASS CLASSIFICATION CONSTRAINT IN RECONSTRUCTION NETWORKS

[42] H. Zhao et al., “Multivariate time-series anomaly detection via graph
attention network,” in Proc. IEEE Int. Conf. Data Mining (ICDM),
Nov. 2020, pp. 841–850.
[43] I. Kobyzev, S. J. Prince, and M. A. Brubaker, “Normalizing flows:
An introduction and review of current methods,” IEEE Trans. Pattern
Anal. Mach. Intell., vol. 43, no. 11, pp. 3964–3979, Nov. 2021, doi:
10.1109/TPAMI.2020.2992934.
[44] G. Papamakarios, T. Pavlakou, and I. Murray, “Masked auto-regressive
flow for density estimation,” in Proc. 31st Int. Conf. Neural Inf. Process.
Syst., Long Beach, CA, USA, 2017, pp. 2335–2344.
[45] E. Dai and J. Chen, “Graph-augmented normalizing flows for anomaly
detection of multiple time series,” in Proc. Int. Conf. Learn. Represent.,
2022, pp. 1–16.
[46] Q. Zhou, S. He, H. Liu, J. Chen, and W. Meng, “Label-free multivariate
time series anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 36,
no. 7, pp. 3166–3179, Jul. 2024, doi: 10.1109/TKDE.2024.3349613.
[47] P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Liò, and
Y. Bengio, “Graph attention networks,” in Proc. 6th Int. Conf. Learn.
Represent., 2017.
[48] S. Bai, J. Z. Kolter, and V. Koltun, “An empirical evaluation of generic
convolutional and recurrent networks for sequence modeling,” 2018,
arXiv:1803.01271.
[49] A. Waibel, T. Hanazawa, G. Hinton, K. Shikano, and K. J. Lang,
“Phoneme recognition using time-delay neural networks,” IEEE Trans.
Acoust., Speech, Signal Process., vol. 37, no. 3, pp. 328–339, Mar. 1989,
doi: 10.1109/29.21701.
[50] F. Yu and V. Koltun, “Multi-scale context aggregation by dilated
convolutions,” presented at the Int. Conf. Learn. Represent., Apr. 2016.
[51] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 770–778.
[52] Z. Niu, G. Zhong, and H. Yu, “A review on the attention mechanism of
deep learning,” Neurocomputing, vol. 452, pp. 48–62, Sep. 2021, doi:
10.1016/j.neucom.2021.03.091.
[53] H. Xu, Y. Wang, S. Jian, Q. Liao, Y. Wang, and G. Pang, “Calibrated
one-class classification for unsupervised time series anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 36, no. 11, pp. 5723–5736,
Nov. 2024, doi: 10.1109/TKDE.2024.3393996.
[54] D. Bahdanau, K. Cho, and Y. Bengio, “Neural machine translation
by jointly learning to align and translate,” in Proc. Int. Conf. Learn.
Represent., 2015, pp. 1–15.
[55] S. Kim, K. Choi, H.-S. Choi, B. Lee, and S. Yoon, “Towards a rigorous
evaluation of time-series anomaly detection,” in Proc. AAAI Conf. Artif.
Intell., Jan. 2021, pp. 7194–7201.
[56] J. Goh, S. Adepu, K. N. Junejo, and A. Mathur, “A dataset to support
research in the design of secure water treatment systems,” in Proc. Crit.
Inf. Infrastruct. Secur., 2017, pp. 88–99.
[57] G. Birol, C. Ündey, and A. Çinar, “A modular simulation package for fed-batch fermentation: Penicillin production,” Comput. Chem.
Eng., vol. 26, no. 11, pp. 1553–1565, Nov. 2002, doi: 10.1016/s00981354(02)00127-8.
[58] L. Ruff et al., “Deep one-class classification,” in Proc. 35th Int. Conf.
Mach. Learn., vol. 80, Stockholm, Sweden, 2018, pp. 4393–4402.

Jiazhen Li received the B.S. degree in mechanical design, manufacturing, and automation from
Shanghai Normal University, Shanghai, China,
in 2022. She is currently pursuing the M.S. degree
in control science and engineering with East China
University of Science and Technology, Shanghai.
Her current research interests include multivariate
time series anomaly detection and fault root cause
analysis.

3518513

Zhenhua Yu received the B.S. degree in mechanical
engineering and automation and the M.S. degree
in mechanical engineering from Wuhan University
of Technology, Wuhan, China, in 2018 and 2021,
respectively. He is currently pursuing the Ph.D.
degree in control science and engineering with
East China University of Science and Technology,
Shanghai, China.
His current research interests include fault diagnosis, process modeling, and explainable deep learning.

Qingchao Jiang (Senior Member, IEEE) received
the B.E. and Ph.D. degrees from the Department
of Automation, East China University of Science
and Technology, Shanghai, China, in 2010 and 2015,
respectively.
From March to September 2015, he had been
a Post-Doctoral Fellow with the Department
of Chemical and Materials Engineering, University of Alberta, Edmonton, AB, Canada. From
September 2015 to September 2016, he had been
a Humboldt Research Fellow with the Institute for
Automatic Control and Complex Systems (AKS), University of DuisburgEssen, Duisburg, Germany. From October 2016 to May 2017, he had been a
Visiting Research Fellow with the Department of Chemical and Biomolecular
Engineering, Hong Kong University of Science and Technology (HKUST),
Hong Kong, China. He is currently an Associate Professor with East China
University of Science and Technology. His research interests include data
mining and analysis, data-driven soft sensing, multivariate statistical process
monitoring and deep learning-based process modeling.
Prof. Jiang was a recipient of the 2021 World Artificial Intelligence
Conference Youth Outstanding Paper Nomination Award. He is the Early
Career Advisory Board Member of the IFAC Journal Control Engineering
Practice and an Associate Editor of IEEE ACCESS.

Zhixing (Edward) Cao received the B.Eng. degree
in automation from the Department of Control Science and Engineering, Zhejiang University,
Hangzhou, China, in 2012, and the Ph.D. degree
in chemical and biomolecular engineering from
Hong Kong University of Science and Technology
(HKUST), Hong Kong, China, in 2016.
He used to work with the Harvard John A. Paulson School of Engineering and Applied Sciences,
Harvard University, Cambridge, MA, USA, and the
School of Biological Sciences, University of Edinburgh, Edinburgh, U.K., as Post-Doctoral Fellow. He is currently a Full
Professor with the School of Information Science and Engineering, East China
University of Science and Technology, Shanghai, China. His research interests
include deep learning, stochastic processes, and systems biology.
Dr. Cao serves as an Editorial Board Member for several prestigious
journals. In 2021, he was awarded the Massachusetts Institute of Technology (MIT) Technology Review Innovators Under 35 Asia Pacific.
PAPER_TEXT
