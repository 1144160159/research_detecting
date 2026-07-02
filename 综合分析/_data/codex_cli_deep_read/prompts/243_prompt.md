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
# [243] HybridAD: A Hybrid Model-Driven Anomaly Detection Approach for Multivariate Time Series
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
编号：243
题名：HybridAD: A Hybrid Model-Driven Anomaly Detection Approach for Multivariate Time Series
年份：2023
DOI：10.1109/tetci.2023.3290027
来源：IEEE Transactions on Emerging Topics in Computational Intelligence
PDF：paper/10.1109_TETCI.2023.3290027.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\243.txt
- 原始字符数：62110
- 本次发送字符数：62110
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
866

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 8, NO. 1, FEBRUARY 2024

HybridAD: A Hybrid Model-Driven Anomaly
Detection Approach for Multivariate Time Series
Weiwei Lin , Member, IEEE, Songbo Wang , Wentai Wu , Member, IEEE, Dongdong Li,
and Albert Y. Zomaya , Fellow, IEEE

Abstract—Anomaly detection, in recent years, has gained increasing attention in the research and practice of time series processing. However, the task is particularly challenging with multivariate time series which complicates the temporal dependency
between observations and introduces complex inter-channel correlation. Meanwhile, in order to fit a broader range of applications, robustness during both training and detection is also a
critical aspect. In this paper, we propose an unsupervised, hybrid
model-driven anomaly detection scheme capable of (1) transforming sequences into a fused representation of temporal dependency
embeddings and inter-channel correlation embeddings, and (2)
achieving robust anomaly detection using a temporal prediction
network for sample-wise posterior estimation combined with a
data reconstruction network to assess the source of prediction. On
this basis, we develop a probability density-based anomaly scoring
mechanism for online detection in multivariate time series, where
the anomaly score for each observation is rectified by the reliability
of the prediction source. The results of extensive experiments on
five publicly available datasets show that our proposed solution
outperforms various state-of-the-art anomaly detection algorithms
(including DL-based and non-DL-based), achieving a performance
improvement (in F1-Score) by up to 10.42%.
Index Terms—Anomaly detection, multivariate time series,
unsupervised learning, deep learning.

I. INTRODUCTION

I

N RECENT years, automated anomaly detection has been
widely employed in production systems concerning domains

Manuscript received 9 December 2022; revised 10 May 2023; accepted
18 May 2023. Date of publication 10 July 2023; date of current version 23
January 2024. This work was supported in part by the National Natural Science
Foundation of China under Grant 62072187, in part by Guangdong Marine
Economic Development Special Fund Project under Grant GDNRC[2022]17,
in part by Guangdong Major Project of Basic and Applied Basic Research
under Grant 2019B030302002, in part by the Major Key Project of PCL under
Grant PCL2021A09, and in part by Guangzhou Development Zone Science and
Technology under Grants 2021GH10 and 2020GH10. (Corresponding author:
Wentai Wu.)
Weiwei Lin is with the School of Computer Science and Engineering,
South China University of Technology, Guangdong 510641, China, and
also with the Peng Cheng Laboratory, Guangdong 518000, China (e-mail:
nnwtwu@pcl.ac.cn).
Songbo Wang and Dongdong Li are with the School of Computer Science
and Engineering, South China University of Technology, Guangdong 510641,
China (e-mail: songbo1998@foxmail.com; dongdonglee1994@foxmail.com).
Wentai Wu is with the Peng Cheng Laboratory, Guangdong 518000, China
(e-mail: wentai_wu@outlook.com).
Albert Y. Zomaya is with the School of Computer Science, The University of
Sydney, Sydney, NSW 2006, Australia (e-mail: albert.zomaya@sydney.edu.au).
This article has supplementary downloadable material available at
https://doi.org/10.1109/TETCI.2023.3290027, provided by the authors.
Digital Object Identifier 10.1109/TETCI.2023.3290027

Fig. 1. Example of multivariate time series as a collection of server performance indicators (from SMD dataset [5]) that vary over 300 time steps.

including finance, cybersecurity, and industrial process control.
It also involves a broad range of critical applications such as
credit card fraud detection, intrusion detection, fault diagnosis,
etc [1]. The application of deep learning in anomaly detection
tasks is becoming increasingly widespread [2]. Unlike other
types of anomaly detection tasks, anomaly detection for time
series data often requires consideration of temporal dependencies between the objects being detected [3], making it a
challenging task and a significant research topic. Depending
on the dimension of the data, time series can be classified as
either univariate time series (UTS) or multivariate time series
(MTS) [4]. In comparison to UTS, the presence of MTS extends
the dimensionality and is more common in real-world systems
where any critical changes are reflected by the dynamics of
multiple variables that may correlate with each other. (Fig. 1
shows the trace of server performance indicators as an example).
Aside from the intrinsic patterns exhibited along the temporal
dimension, the interplay of multiple channels brings additional
challenges to the anomaly detection for MTS especially when
no prior knowledge or reliable data sources are available.
Intuitively, an anomaly detection system works by distinguishing normal data from anomalous data in a similar way
to the binary classification problem. However, it is usually
not practical in the context of Big Data for many reasons [6].
Specifically, classification-based approaches are greatly affected
by (i) severe data imbalance, which means that the proportion
of anomalous data is much smaller than that of normal data in a
time series; and (ii) high cost of manual labeling, which means
that labeling each data point is cost-prohibitive and thus we
have to deal with unlabeled data in most cases. In this regard,
unsupervised methods are frequently adopted as a promising

2471-285X © 2023 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

LIN et al.: HYBRIDAD: A HYBRID MODEL-DRIVEN ANOMALY DETECTION APPROACH FOR MULTIVARIATE TIME SERIES

alternative to supervised or semi-supervised methods for
anomaly detection [7], [8], [9], [10]. Despite the way of training
and the model to be used, it is always essential to capture
the temporal dependency between observations within different
ranges of a time series. For MTS, inter-channel correlation,
characterized as a complicated linear or non-linear relationship between different variables within the same time period,
should also be considered particularly in anomaly detection
systems [3]. However, traditional unsupervised anomaly detection methods, such as local outlier factor (LOF) [11], principal
component analysis (PCA) [12], one-class SVM (OCSVM) [13],
and Isolation Forest (IF) [14], are unable to extract the temporal
dependency and inter-channel correlation of MTS effectively
and therefore fail to meet the requirements of the majority
of anomaly detection systems. DL-based approaches, such as
the variants of recurrent neural networks (RNNs) and onedimensional convolutional neural networks, have been proven
effective in terms of time series feature extraction [10], [15],
[16], [17]. Studies on DL-based unsupervised anomaly detection
usually make the following assumptions: (i) the training data
contains no or a negligible number of anomalous samples; (ii)
the data patterns that anomalous data display differ significantly
from those of normal data [6]. These assumptions encourage
prediction-driven and reconstruction-based anomaly detection
where a deep model is trained to learn normal series patterns.
Following this rationale, a number of practical DL-based
algorithms have been developed for time series anomaly detection [7], [18], [19], [20], [21], [22]. However, there are still several limitations. First, existing networks often struggle in simultaneously learning the temporal dependency and inter-channel
correlation of MTS. Second, the majority of existing anomaly
detection models are either based on temporal prediction or
data reconstruction, resulting in reduced effectiveness during
training or prediction in the presence of anomalies. Finally, the
performance improvement of anomaly detection model is hindered by the absence of an efficient anomaly scoring mechanism,
resulting in anomalies being easily overlooked.
In this work, we propose HybridAD (Hybrid Model-driven
Anomaly Detection Approach for MTS), a hybrid anomaly detection approach based on deep learning. For the first limitation,
we design a feature extraction module mainly consisting a Gated
Recurrent Unit (GRU) and a one-dimensional convolutional
neural network to extract the inter-channel correlation and temporal dependency feature of MTS, respectively. Then we build a
hybrid anomaly detection model that is jointly optimized based
on temporal prediction and data reconstruction to address the
second limitation. A novel anomaly scoring mechanism that
focuses on prediction probability density is presented to enhance
the anomaly detection performance.
To summarize, the main contributions of our work are as
follows:
r We design a feature extraction module that combines a
GRU network and a one-dimensional convolutional neural
network to simultaneously learn the temporal dependency
and inter-channel correlation of MTS.
r We propose a hybrid model-driven framework empowered
by a temporal prediction network and a data reconstruction
network for robust anomaly detection.

867

r We present an anomaly scoring mechanism that focuses
on prediction probability density. By taking the reliability
of the prediction source into account, the effectiveness of
anomaly detection is further improved.
r Our experimental results on five real-world datasets show
that the proposed HybridAD outperforms several stateof-the-art models for MTS anomaly detection, achieving
a maximum performance improvement of 10.42% in F1Score.
The rest of this article is organized as follows: Section II
discusses the studies related to DL-based anomaly detection
models. In Section III, we introduce in detail the proposed unsupervised anomaly detection scheme. In Section IV, we present
and analyze the experimental results, and finally conclude the
article in Section V.
II. RELATED WORK
Due to the fact that DL-based anomaly detection models are
typically trained on anomaly-free datasets to learn the normal
data patterns, greater detection error will be produced in case that
the anomalies exist. Based on the different techniques, DL-based
anomaly detection models can be categorized as follows.
Temporal prediction-based models: On the basis of normal
pattern derived from the historical data, the model could detect the anomaly through the difference between the predicted
and real value of the incoming observation. RNN-based models [10], [15], [23] were proposed for temporal prediction and
usually determined the anomalies utilizing the prediction errors.
Specially, Hundman et al. [23] built an LSTM-based model
for each channel of MTS. However, simplistically combining
the anomaly detection results of multiple UTS may neglect
the anomalies of inter-channel correlation. Incorporating lowdimensional embeddings to capture temporal dependencies [24],
[25] and leveraging graph structures to capture inter-channel
correlation in time series [21], can further improve the efficiency
of anomaly detection models. However, these approaches do
not simultaneously consider both types of feature factors during
the time series modeling process. Meanwhile, to the best of our
knowledge, there are very few studies on anomaly detection that
consider the reliability of the prediction source. Similar to [10],
our work also takes into account the reliability of the prediction
source.
Data reconstruction-based models: When an input sequence
deviates from the normal pattern due to the existence of anomalies, a well-trained reconstruction model will struggle to recover
the input sequence and output greater reconstruction errors.
The Variational Auto-Encoders (VAE)-based models [22], [26],
[27] were proposed to reconstruct the sequences’ expected distribution and used the reconstruction probability as anomaly
score. Zong et al. [20] used a deep autoencoder to generate a
low-dimensional representations from both the reduced space
and the reconstruction error features, which were then fed to a
Gaussian mixture model to estimate their likelihood. However,
the robustness of the model in anomaly detection using only
data reconstruction needs further improvement. Some works
conducted an anomaly detection scheme based on the paradigm
of hybrid models [6], [19], but the error-based methods for

868

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 8, NO. 1, FEBRUARY 2024

TABLE I
LIST OF SYMBOLS

details in Section III-B), allowing the model to learn the temporal
dependency and inter-channel correlation features of MTS in a
normal pattern. After training, the model will provide anomaly
score for each observation in the training set and employ an
adaptive threshold selection strategy to generate the anomaly
threshold TS for the online anomaly detection.
Online anomaly detection: After training, the model is able
to detect the MTS input in real-time and assign a score to
each observation. Observations with scores over the threshold
determined in offline training are considered anomalous.
B. Design of HybridAD

Fig. 2. Overall process of unsupervised anomaly detection for MTS. It consists
of an offline training phase and an online detection phase.

anomaly detection faced challenges in distinguishing anomalies
of different scales. Inspired by GAN [28] that enables the model
to fit the target distribution of any dataset through adversarial
training, [18], [29], [30] proposed a GAN-based model to perform anomaly detection for time series. However, the instability
of the adversarial training may hinder the efficiency and effectiveness of anomaly detection in practice.
III. METHODOLOGY
In this section, we present the overall process of unsupervised
anomaly detection for MTS and introduce the design of the proposed anomaly detection model HybridAD in detail. In addition,
we also provide an anomaly scoring mechanism and a threshold
selection strategy, which make significant influence on model’s
performance. For clarity, Table I lists all the symbols frequently
used in this article.
A. Overview
The workflow of our anomaly detection system involves two
phases: offline model training and online anomaly detection
(as depicted in Fig. 2).
Offline model training: During this phase, the data preprocessing module receives a MTS and outputs a set of sequences (after window slicing and data normalization), each
of which is formatted as Wt = {xt−L+1 , . . . , xt }(t ≥ L). The
sequences are loaded into the model training module (which

As shown in Fig. 3, this article proposes a probability densitybased anomaly detection model combined with temporal prediction and data reconstruction to address the challenges in MTS
anomaly detection. The data pre-processing module divides the
MTS into a set of sequences based on the specified window size.
The feature extraction network permits the efficient extraction of
temporal dependency and inter-channel correlation. Finally, the
joint optimization of the anomaly detection model is achieved by
feeding the fused embeddings to the data reconstruction network
and the temporal prediction network, respectively.
Feature Extraction Network: To extract the inter-channel
correlation and temporal dependency of MTS simultaneously,
the feature extraction network employs a GRU module and
a one-dimensional convolutional neural module. In particular,
the GRU module is used to obtain inter-channel embedding, and
the length L of the compressed series remains constant while the
number of dimensions decreases to M  (M  < M ). The onedimensional convolutional module is used to obtain temporal
embedding with a fixed number of dimensions, and the length
of the series decreases to L (L < L). With the inter-channel
embedding hch and temporal embedding htp as input to the fully
connected layer, the embedding fusion is performed. Then the
fused embedding ht is fed to the temporal prediction network
and data reconstruction network to achieve joint optimization.
Temporal Prediction Network: One of the typical ways used in
temporal prediction-based anomaly detection model updating is
based on the prediction error. In contrast to the majority of temporal prediction-based anomaly detection models, HybridAD
employs maximum likelihood estimation to fit the probability
distribution of future observations, and the model’s output is the
probability density of the observation under that distribution.
Similar to other works on probability prediction by assuming
an underlying distribution of the time series [31], [32], in our
work, we assume that each feature of the future observation
xt+1 = [x1t+1 , x2t+1 , . . . , xM
t+1 ] follows a Gaussian distribution
N (μxit+1 , σxit+1 ), where i represents the ith feature of xt+1
and i ≤ M . The loss function of the temporal prediction-based
model is defined as the negative logarithm of the likelihood
function:


M

(1)
p xit+1 | μxit+1 , σxit+1 ,
Losspre = − log
i=0

where μxit+1 and σxit+1 are the mean and standard deviation of
the distribution, obtained from a liner layer and a Softplus layer,
respectively.

LIN et al.: HYBRIDAD: A HYBRID MODEL-DRIVEN ANOMALY DETECTION APPROACH FOR MULTIVARIATE TIME SERIES

Fig. 3.

869

Design of hybrid anomaly detection model.

Data reconstruction network: The data reconstruction network is designed based on the idea of Variational Autoencoder [33]. In this work, the feature extraction network and data
reconstruction network are combined to form a complete variational autoencoder structure. The main component of the data
reconstruction network is a multilayer, fully-connected neural
network. Assume the prior pθ (zt ) follows a normal distribution
N (0, I), where zt is a latent representation with a reduced
dimension in VAE, representing a high-dimensional input Wt .
The posterior distributions of Wt and zt are described by the
2
I)
diagonal Gaussian distributions pθ (Wt | zt ) = N (μWt , σW
t
2
and qφ (zt | Wt ) = N (μzt , σzt I), respectively, where the parameters μ and σ 2 of the Gaussian diagonal distributions are
obtained from a linear layer and a Softplus layer, respectively.
The Softplus layer ensures that the standard deviation σ of the
output is consistently greater than 0. A constant  is added to
the Softplus layer to address the issue that the parameter σ
may be too small for training the model [26]. As input to the
decoder, the hidden state distribution is sampled to produce the
vector zt , which is then used to reconstruct the distribution of
the sequence Wt . It should be noted that the output of the VAE in
this work is not the reconstructed sequence but rather the mean
and standard deviation of the distribution that the reconstructed
sequence follows. The loss function of the data reconstruction
network can be defined as:
Lossrec = KL (qφ (zt | Wt ) pθ (zt ))
+ Ezt ∼qφ [log pθ (Wt | zt )] ,

(2)

where the first term represents the degree of similarity between
the approximate posterior distribution qφ (zt | Wt ) of the latent
variable zt and the prior distribution pθ (zt ), which can be
calculated by using the KL divergence. Under the assumption

that the prior distribution of the latent variable zt is a standard
Gaussian distribution, the KL divergence of the two distributions
above is calculated as (where ‘ ∼ ‘ denotes qφ (zt | Wt )pθ (zt )):

1 
1 + 2 log σzti − μ2zi − σz2i ,
KL (∼) = −
t
t
2 i=0
D

(3)

where D is the size of the latent variable zt . The second term in
(2) represents the degree of similarity between the given input
Wt and the reconstructed sequence, which can be calculated
using the maximum likelihood estimation as follows (where ‘ ∼
‘ denotes log pθ (Wt | zt )):
⎞
⎛
t
M



1  ⎝
Ezt ∼qφ [∼] =
− log
p xji | μxj , σxj ⎠ . (4)
i
i
L
j=0
i=t−L

Based on the parameters output by the data reconstruction
network, the reconstruction probability density of the input
sample Wt can be inferred. Wt is used as a prediction source
for future observation xt+1 in the temporal prediction network.
In this work, the reconstruction probability density of the input
Wt is utilized to assess the reliability of the prediction source.
When the prediction source Wt contains anomalies (i.e., the
reconstruction probability density is below a normal level), the
prediction result xt+1 based on the input Wt will be considered
unreliable. The anomaly score (to be introduced in Section III-C) can be amplified further by integrating the reliability of
the prediction source, thereby making the distinction between
anomalous and normal data more obvious and improving the
accuracy of anomaly detection.
By the joint optimization by the temporal prediction and data
reconstruction network, the loss of the hybrid anomaly detection

870

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 8, NO. 1, FEBRUARY 2024

the reliability of the prediction result for xt+1 is significantly dependent on the proportion of normal data points in the sequence
Wt (as the prediction source). As a result, we rectify the anomaly
score by using the reconstruction probability to measure the
reliability of the prediction source. Moreover, we believe that
data closer to the predicted point xt+1 is more crucial, so we
employ an exponentially decaying weights approach that assigns
a weight di = αi−(t−L+1) to each observation in sequence Wt .
The final reconstruction probability after weighting rectification
is:



t
M
j
i=t−L+1 di ×
j=0 p xi | μxji , σxji
, (7)
pr =
DL

Algorithm 1: HybridAD Training Algorithm.
Input: training set Xtrain = {(Wt , xt+1 )}(t ≥ L),
iteration epoch number N , feature extraction network
f N et, temporal prediction network pN et, data
reconstruction network reN et.
Output: trained f N et, pN et, reN et
1: f N et, pN et, reN et ← initialize parameters
2: n ← 1
3: repeat
4:
for (Wt , xt+1 ) in Xtrain do
5:
ht ← f N et(Wt )
6:
μxt+1 , σxt+1 ← pN et(ht )
7:
zt , μWt , σWt ← reN et(ht )
8:
compute Losspre via (1)
9:
compute Lossrec via (2)
10:
Loss ← Losspre + Lossrec
11:
f N et, pN et, reN et ← model parameters
optimization according to the Loss
12:
end for
13:
n←n+1
14: until n = N
15: return trained f N et, pN et, reN et

where DL = ti=t−L+1 di .
In summary, this work provides an anomaly score mechanism
that focuses on prediction probability density while also incorporating the reliability of the prediction source, which allows
the model to distinguish normal data from anomalous data more
accurately. The anomaly score Sxt+1 for the observation xt+1
is defined in this study as the negative logarithm of the product
of the prediction source’s reconstruction probability density and
the prediction probability density, as given in (8).
Sxt+1 = − log (pp × pr ) .

model can be calculated as:
Loss = Losspre + Lossrec .

(5)

The training process of HybridAD model can be described in
Algorithm 1.
C. Anomaly Scoring
On the basis of HybridAD, we propose an anomaly scoring
mechanism as a mixture of the prediction probability density
and reconstruction probability density.
Prediction probability density: For the sequence Wt =
{xt−L+1 , . . . , xt } with a given window size L, the temporal
prediction network fits the probability distribution p(xt+1 | Wt )
of the future observation xt+1 via maximum likelihood estimation. The anomaly score is then calculated as the probability
density of the observation under the distribution p(xt+1 | Wt ).
The lower the probability density, the more likely the observation
is an anomaly. Consequently, the score of the observations for
the temporal prediction model can be calculated as:

D. Threshold Selection Strategy
In practice, using the manual selection of score threshold in
complex anomaly detection systems not only requires expert
knowledge but also compromises the robustness of the solution.
Extreme Value Theory (EVT), a statistical theory that explores
the extreme value law, has been applied in some anomaly
detection work [12], [34]. Peaks Over Threshold (POT) is the
second theory of EVT, which is used to fit the tail distribution of
the data probability distribution. This work uses a POT method
to concentrate on the high end of the distribution which the
extreme values (i.e., the scores of anomalies) in the set of scores
follows [5], [19]. Algorithm 2 depicts the anomaly detection
flow of the HybridAD model combined with the POT-based
threshold selection strategy. Note that applying POT to achieve
anomaly threshold selection is not the main contribution in this
work.
IV. EXPERIMENTS AND EVALUATION

pp = p xt+1 | μxt+1 , σxt+1
M  


p xit+1 | μxit+1 , σxit+1 .
=

(8)

(6)

i=0

Reconstruction probability density: For the sequence Wt =
{xt−L+1 , . . . , xt }, the data reconstruction network outputs the
mean and standard deviation of the distribution pθ (Wt | zt ) of
the reconstructed sequence. Therefore, the reconstruction probability refers to the probability density of the sequence Wt under
the distribution pθ (Wt | zt ). In the temporal prediction network,

In this section, we first introduce the datasets and the evaluation metric used in our experiment (Section IV-A). We compare
the performance of HybridAD to that of state-of-the-art anomaly
detection algorithms using the F1-Score on five publicly available datasets (Section IV-B). Then, the effectiveness of the
feature extraction network and the probability density-based
model are validated through a series of ablation experiments
(Section IV-C). Finally, we discuss the effect of the POT-based
threshold selection strategy and the hyperparameter on model’s
performance (Section IV-D).

LIN et al.: HYBRIDAD: A HYBRID MODEL-DRIVEN ANOMALY DETECTION APPROACH FOR MULTIVARIATE TIME SERIES

871

TABLE II
OVERVIEW OF THE FIVE PUBLICLY AVAILABLE DATASETS

Algorithm 2: Anomaly Detection Algorithm Based on
HybridAD.
Input: window length L, trained f N et, pN et and reN et,
hyperparameters q and level associated with POT,
training set Xtrain = {(Wt , xt+1 )}(t ≥ L), test set
Xtest = {(Wt , xt+1 )}(t ≥ L).
Output: anomaly detection results Y = {yt+1 }(t ≥ L)
1: Strain ← ∅
2: for (Wt , xt+1 ) in Xtrain do
3:
ht ← cN et(Wt )
4:
μxt+1 , σxt+1 ← pN et(ht )
5:
z, μWt , σWt ← reN et(ht )
6:
compute Sxt+1 via (8)
7:
add Sxt+1 to Strain
8: end for
9: th ← P OT _threshold_selection(Strain , q, level)
10: Y ← ∅
11: for (Wt , xt+1 ) in Xtest do
12:
ht ← f N et(Wt )
13:
μxt+1 , σxt+1 ← pN et(ht )
14:
zt , μWt , σWt ← reN et(ht )
15:
compute Sxt+1 via (8)
16:
if Sxt+1 > th then

17:
yt+1
←1
18:
else

←0
19:
yt+1
20:
end if

to Y
21:
add yt+1
22: end for
23: return Y
A. Datasets and Evaluation Metric
In our experiments, the performance of the HybridAD model
is evaluated on five publicly available datasets: Secure Water Treatment (SWaT) [35], Water Distribution (WADI) [29],
Server Machine Dataset (SMD) [5], Soil Moisture Active Passive (SMAP) satellite and Mars Science Laboratory (MSL)
rover [23]. The overview of each dataset is shown in Table II.
To demonstrate the performance of the models, we mainly use
F1-Score. In practice, anomalies in time series are typically
exhibited as successive segments of anomalous data rather than
as a single anomaly. Similar to [26], we consider an anomalous
sequence to be correctly detected if the model detects at least
one anomalous observation in the sequence, which implies that
all other anomalies in the anomalous sequence are also deemed
to be correctly detected. More details are in Appendix A.

Fig. 4. Performance (with standard deviation) of HybridAD and other baseline
methods measured in F1-Score.

B. Performance Analysis
In this experiment, we compare HybridAD’s performance
with both DL-based and non-DL-based methods, including
OCSVM [13], Isolation Forest (IF) [14], DAGMM [20], LSTMVAE [22], BeatGAN [18], MTAD-GAT [19], USAD [7],
GDN [21] algorithms, and adopt the optimal threshold for each
method when calculating the corresponding F1-Score. Table III
shows the performance of all models on five datasets. Note that
the symbol P, R and F1 in Table III denote precision, recall,
and F1-Score, respectively, where the bold denotes the best
performance and the italic denotes the second-best performance.
It can be seen that the proposed hybrid model-driven method
achieves the best performance on all the datasets. In addition, we
find that the majority of deep learning-based models (other than
OCSVM and IF) performed well on SMD, SMAP, and MSL, as
the anomaly patterns of the sequences in these three datasets are
relatively simple, consisting primarily of temporal dependency
anomalies with substantial numerical variations in some of
dimensions. Even when the anomaly pattern is straightforward,
HybridAD outperforms the other models in terms of F1-Score.
For SWaT and WADI with more complex anomaly patterns,
the performance advantage of HybridAD is more significant.
Especially on the WADI, only MTAD-GAT obtains better performance among all baseline models with F1-Score of 0.8811,
while HybridAD achieves a 10.42% performance improvement
with an F1-Score of 0.9729. In Appendix B-D, we further
provide significance test results for reference. As shown in
Fig. 4, when the performance of all models is averaged across all
datasets, HybridAD achieves the highest average performance
and more excellent stability.
C. Ablation Study
1) Effectiveness of the Feature Extraction Network: Effective extraction of feature information from time series is of great
importance for improving the performance of the model. In this
article, we designed a feature extraction network composed of a
GRU network and a one-dimensional convolutional network to
extract the inter-channel correlation and temporal dependency
information of the time series. To verify the effectiveness of
these components, we designed three model variants. In the first
variant (HybridAD_Wo_T), we removed the one-dimensional

872

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 8, NO. 1, FEBRUARY 2024

TABLE III
PERFORMANCE OF EACH MODEL ON THE PUBLICLY AVAILABLE DATASETS

Fig. 5. Results of ablation experiments on the effectiveness of the feature
extraction network.

convolutional network to make the module not explicitly extract
temporal dependency information. In the second variant (HybridAD_Wo_C), we removed the GRU network to make the
module not explicitly extract channel correlation information. In
the third variant (HybridAD_Wo_TC), we removed the entire
feature extraction module and directly input the preprocessed sequence into the prediction network and reconstruction network.
Fig. 5 shows the results of the experiment.
The results in Fig. 5 indicate that in time series anomaly
detection tasks, extracting temporal features and using them as
inputs to downstream models (which are temporal prediction
and data reconstruction networks in this article) is effective
for improving model performance. As temporal dependency
and inter-channel correlation are important features of MTS,
considering a single feature in the model cannot achieve optimal
performance.
2) Effectiveness of the Probability Density-Based Model: To
validate the effectiveness of probability density-based model in
HybridAD, the probability-based prediction model is replaced
by a value-based prediction model, and its loss function is modified to (9). As shown in (10), the likelihood of the reconstructed
sequence in the data reconstruction model is modified to be
accounted for by the mean square error. The structure of the
modified model variants of data reconstruction network and
temporal prediction network is given in Fig. 6.
Losspre = xt+1 − x̂t+1 22 ,
2



Lossrec = Wt − Ŵt  ,
2

(9)
(10)

Fig. 6. Variant models in ablation studies. The variant model of the network
for data reconstruction is shown on the left, and the variant model of the network
for temporal prediction is shown on the right.

Fig. 7. Results of ablation experiments on the effectiveness of the probability
density-based model.

Following the modified model variants, the anomaly scoring
is calculated in accordance with the Euclidean distance (ED).
This experiment takes into account only the prediction error
(ED-Only Prediction), the reconstruction error (ED-Only Reconstruct), and the combination of both in anomaly scoring
mechanism (ED-Composite), respectively. Meanwhile, the experiments additionally consider only the prediction probability
density (PD-Only Prediction) and the reconstruction probability density (PD-Only Reconstruct), respectively. More details
will be presented in Appendix B-E.
As depicted in Fig. 7, the anomaly detection model proposed
in this article achieves superior performance on each dataset
when compared to any model variant. We discover that the
detection performance of the probability density-based temporal
prediction model (PD-Only Prediction) is improved on the five
datasets when the prediction source reliability is taken into
account. The ED-Composite model variant still performs poorly,

LIN et al.: HYBRIDAD: A HYBRID MODEL-DRIVEN ANOMALY DETECTION APPROACH FOR MULTIVARIATE TIME SERIES

Fig. 9.
Fig. 8. Comparison of the performance of HybridAD using the optimal threshold and the POT-based threshold, respectively. ‘PD‘ specifies the percentage of
performance degradation.

even though taking the reliability of the prediction source into
account. It can be observed that utilizing the probability-based
anomaly scoring mechanism is superior to using the error-based
one in the majority of cases, and the combination of the reliability
of the prediction source can improve the detection performance
of the model to some extent.
D. Parameter Study
1) Performance Degradation With POT: Without labels, it
is theoretically challenging for the anomaly detection model
to obtain the anomaly threshold when the optimal F1-Score is
achieved. As introduced in Section III-D, we apply the POT
method to HybridAD to implement the automatic selection
of anomaly thresholds. Fig. 8 illustrates the performance of
HybridAD after applying the POT-based threshold selection
strategy. It can be seen that the performance of the model
on various datasets decreases in comparison to its theoretically optimal F1-Score. Nevertheless, the performance degradation of the model is within a tolerable range (5.81% ∼
8.56%), indicating that HybridAD still achieves a superior
performance that is acceptable in practical anomaly detection
systems.
2) Hyperparameter Sensitivity: We study the sensitivity of
our HybridAD with respect to two hyperparameters, namely
the number of iteration epochs during training and the window size set during the pre-processing for MTS. Note that
the hyperparameter sensitivity analysis experiments for HybridAD in this article are conducted on SWaT and WADI.
On the basis of the significant performance differences among
the models on SWaT and WADI in Table III, we believe that
the hyperparameter sensitivity analysis experiments on these
two datasets can reflect the worst performance of the HybridAD on hyperparameter sensitivity to some extent and more
closely match the performance in complex anomaly detection
systems.
Multiple Iteration Epochs: During model training, the training
cost increases as the greater iteration epochs required to improve
the performance of the model. This article focuses on whether
or not HybridAD can achieve satisfactory performance and
stability with fewer iteration epochs.

873

Sensitivity analysis of HybridAD to the number of iteration epochs.

To explore the performance of HybridAD model under different training iteration epochs, we evaluate the model performance using F1-Score. Note that this experiment is conducted under a window size of 30. Fig. 9 demonstrates that
the HybridAD model performs well on both datasets within
a limited number of iteration epochs, which is indicative of
the inexpensive training cost of the model. However, the performance of HybridAD on WADI fluctuates dramatically more
than on SWaT. We analyze that this is due to the WADI’s more
complex inter-channel features (which we know has the highest
number of dimensions among the five publicly available datasets
with 127 according to Table II). Consequently, improving the
performance stability of the model on datasets with complex
inter-channel features is one of the objectives in our future
work.
Sliding Window Length: One of the most frequently addressed
issues in time series research is how to select an appropriate
sliding window size under keeping the balance between model
performance and training cost. We examine the performance
(i.e., precision, recall and F1-Score) of the HybridAD model
with different sliding window size settings. For each window size
setting, we demonstrate the performance of HybridAD across 30
iteration epochs.
As depicted in Fig. 10, the HybridAD model performs well
on both SWaT and WADI despite varying window size settings.
Similar to the results of the training epoch sensitivity analysis
experiments, the performance on WADI exhibits greater variation than on SWaT. Specifically, HybridAD performs better
on WADI than on SWaT in terms of average recall but is less
impressive in terms of average precision and F1-Score. This
indicates that HybridAD has a significant capacity for learning
complex anomaly patterns of MTS and identifying anomalies
with a higher recall. It is a satisfactory outcome for some detection cases where missing anomalies are prohibited. However,
the existence of the complex time series anomaly pattern may
cause the model to incorrectly classify the normal data. Overall,
the performance of the HybridAD model is still acceptable even
though performance fluctuation exists. Due to the fact that realworld anomaly detection systems place a greater emphasis on
model recall, the recommended settings for the sliding window
on SWaT and WADI are 60 and 30, respectively, considering
multiple performance metrics including recall. Although the
performance of the proposed HybridAD on SWaT and WADI is

874

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 8, NO. 1, FEBRUARY 2024

Fig. 10. Performance of HybridAD with varying sliding window sizes. Specifically, (a)∼(c) and (d)∼(f) denote the precision, recall and F1-Score of HybridAD
on SWaT and WADI, respectively, with different sliding window sizes.

comparable to that of the model in the article [29], our model
still achieves an improvement in terms of precision, recall, and
F1-Score.
V. CONCLUSION
In this article, we propose an unsupervised, hybrid modeldriven anomaly detection scheme targeting at complex multivariate time series. First, a feature extraction module that
employs a GRU network and a one-dimensional convolutional
neural network is designed to extract the inter-channel correlation and temporal dependency of multivariate time series
for enhanced sequence embedding. To improve the robustness
of the model, we propose a hybrid anomaly detection model
that is jointly optimized by learning the posterior probability distribution of incoming observations and the probability
distribution of the input sequences. In addition, an anomaly
scoring mechanism focused on prediction probability density
takes into account prediction source’s reliability which is calculated as reconstruction probability density, thereby enhancing
the anomaly detection performance. We evaluate our proposed
anomaly detection algorithm on five publicly available datasets,
and the experimental results show that our scheme outperforms
the baseline models chosen in this article in terms of F1-Score,
with a maximum performance improvement of 10.42%. We
also empirically demonstrate that HybridAD only experiences
minor performance loss given a sub-optimal threshold and that
our model still provides satisfactory performance given smaller
training budgets that concern the number of training epochs and
the input sequence length.
APPENDIX A
DETAILS OF DATASETS AND EVALUATION METRICS
SWaT [35] records a total of 11 days of operational data from
the industrial water treatment plant, with the first 7 days in normal operation mode (i.e., the training set) and the last 4 days in

an attack scenario (i.e., the test set), containing anomaly labels.
Details obtained from https://itrust.sutd.edu.sg/testbeds/securewater-treatment-swat/.
WADI [29], as an extended dataset of SWaT, records a total
of 16 days of operation data, with the first 14 days for normal
operation and the last two days for abnormal operation under
the attack scenarios. Details obtained from https://itrust.sutd.
edu.sg/testbeds/water-distribution-wadi/.
SMD [5] is a server machine dataset that records monitoring data for 28 servers with a total of 33 metrics over the
course of 5 weeks. Details obtained from https://github.com/
NetManAIOps/OmniAnomaly.
SMAP and MSL [23] are both expert labeled datasets from
NASA containing data for 55 and 27 entities, with 25 monitored
metrics per entity for SMAP and 55 monitored metrics per entity
for MSL. Details obtained from https://github.com/khundman/
telemanom.
To evaluate the performance of the models, the precision,
recall, and F1-Score (F1 for short) are utilized and can be
calculated as follows:
TP
,
TP + FP
TP
,
recall =
TP + FN
2 × precision × recall
F1 =
,
precision + recall

precision =

(11a)
(11b)
(11c)

where TP denotes the number of correctly detected anomalous
data, and FP denotes the number of normal data identified as
anomalous, and FN denotes the number of anomalous data
identified as normal. In practice, anomalies in time series are
typically exhibited as successive segments of anomalous data
rather than as a single anomaly. The schematic diagram of
prediction adjustment strategy mentioned in Section IV-A is
depicted in Fig. 11.

LIN et al.: HYBRIDAD: A HYBRID MODEL-DRIVEN ANOMALY DETECTION APPROACH FOR MULTIVARIATE TIME SERIES

875

TABLE VI
RESOURCE COST OF HYBRIDAD

Fig. 11.

Demonstration of prediction adjustment strategy.
TABLE IV
MODEL PARAMETERS TABLE

TABLE V
TRAINING PARAMETERS TABLE

the total number of epochs for model training is set to 30, and
the prediction step size is set to 1. In addition to the above
parameters, the parameter optimizer of the model is Adam on
all datasets, and the learning rate is set to 0.001. The validation
sets of SWaT, WADI, and SMD account for 10% of each dataset,
and for SMAP and MSL, where the number of data samples is
relatively small, the percentage is set to 30%.
B. Resource Cost

APPENDIX B
DETAILS OF EXPERIMENTS
A. Experimental Setup
Our experiments are conducted on a machine equipped with
a 16-cores CPU (model: Intel(R) Xeon(R) Gold 5218 CPU @
2.30 GHz), a GPU (model: Nvidia Tesla T4), and 256 GB of
memory. The HybridAD model is implemented on the platform
with Python 3.9.7 and Pytorch 1.10. Tables IV and V list the
model parameters and training parameters, respectively. Specially in Table IV, the Conv1d(Kernel, Stride) denotes the parameter of the one-dimensional convolutional neural network. The
inter-channel embedding size denotes the size of compressed
dimensions M  . The VAE latent variable size denotes the size
of the latent variable z in the VAE model. The q and level are
hyperparameters associated with POT. q denotes the expected
probability that the anomaly score exceeds the initial threshold.
The level denotes the quantile, while (1 − level) × Ntrain represents the number of samples with scores exceeding the initial
threshold.
Additional configurations are explained as follows. The number of layers of the one-dimensional convolutional neural network used to obtain the temporal embedding is 3. The activation
functions are all designed as ReLU functions, and the Batch
Normalization module is added to stabilize the training of the
model. The inter-channel embedding is obtained using a GRU
network of 1 layer with 128 hidden units. The body of both
temporal prediction network and the data reconstruction network
(i.e., the hidden dense layer) is a three-layer fully connected
neural network with the structure (512, 256, 128), and the
activation function is ReLU. The Batch Normalization module
is also implemented. The parameter  is set to 0.001 in the
Softplus layer. For the training parameters not listed in Table V,

In order to better demonstrate the resource costs of HybridAD
in practical applications, we recorded the model parameter size,
time cost per training epoch, time cost for outputting anomaly
scores for each observation point, and GPU memory usage of
HybridAD on five datasets, as shown in Table VI. The number
of model parameters is related to the size of the input window
and the number of channels. A larger window size and more
channels will result in a larger number of model parameters.
GPU memory usage is related to the batch size setting. A larger
batch size will result in larger memory usage. All of the above
factors will lead to longer training time for each epoch of the
model. Nevertheless, according to Section IV-D2, we know that
HybridAD can achieve good detection performance in a few
training iterations, so the training time cost of HybridAD on
these five datasets is acceptable. At the same time, HybridAD
requires very little time to score each observation point, enabling
it to detect more data points within a given time frame.
C. Baseline Algorithms Implementation
OCSVM [13] and Isolation Forest [14] use the existing implementation of scikit-learn. MTAD-GAT [19] comes from a
Github implementation on https://github.com/ML4ITS/mtadgat-pytorch. USAD [7] comes from a Github implementation on
https://github.com/manigalati/usad. GDN [21] comes from the
authors’ implementation on https://github.com/d-ailin/GDN.
The rest of the DL-based learning models [18], [20], [22] are
implemented followed their papers on the platform of Pytorch
1.10.
D. Further Performance Analysis
Results in Table III reveals that traditional anomaly detection
algorithms such as OCSVM [13] and IF [14] are not good options
for complex anomaly detection for MTS due to their inherent
restricted learning ability. DAGMM [20] focuses on anomaly
detection for multidimensional data, but in time series anomaly
detection, it only analyzes the current point of observation and
disregards historical information. However, it is essential to

876

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 8, NO. 1, FEBRUARY 2024

TABLE VII
PERFORMANCE SIGNIFICANCE ANALYSIS EXPERIMENT

in the dataset and the complexity of the anomaly patterns. At
the same time, we can see that deep learning-based anomaly detection models have greatly improved performance compared to
traditional anomaly detection models (such as IF and OCSVM),
which means that deep learning models still have great research
value in anomaly detection tasks.
E. Details of the Ablation Experiment

consider temporal dependency in the time series research. The
LSTM-VAE [22] model combines LSTM and VAE, but it only
considers the current moment zt in the distribution of latent
variables, which limits the decoder’s ability in the reconstruction
of the data and consequently affects anomaly detection performance. BeatGAN [18] and USAD [7] are based on the adversarial training in GAN model, but their performance in anomaly
detection is unreliable due to adversarial training being unstable
and prone to pattern collapse. Both the MTAD-GAT [19] and
the GDN [21] models are based on graph neural networks,
which have recently gained popularity. MTAD-GAT is a hybrid
anomaly detection model that combines temporal prediction and
data reconstruction. In addition, it integrates prediction error and
reconstruction error for anomaly scoring, thereby strengthening
the model’s robustness. However, the error-based anomaly scoring mechanism is verified inferior to the probability-based one
through the ablation experiments.
At the same time, we found that the performance of HybridAD
on the SMD, SMAP, and MSL datasets was not significantly
different from that of some baseline models. Therefore, in order
to give a more objective and comprehensive display of the
performance of HybridAD, we used the Mann-Whitney Test [36]
(which is a non-parametric statistical test) to verify whether the
performance difference between HybridAD and other baseline
models on the five datasets is significant. The significance level
was set to 0.05. Specifically, we conducted 10 repeated experiments for each model on each dataset and collected the best
performance of the model in each experiment as its optimal performance. Table VII shows whether the performance difference
between HybridAD and multiple baseline models is significant
or not significant on the five datasets. ‘*’ indicates that the performance improvement of HybridAD on that dataset is significant,
‘=’ indicates that the performance improvement of HybridAD
on that dataset is not significant. Moreover, we further divided
the significant combinations (where p-value < 0.05) into three
categories based on the magnitude of the calculated p-values
using the Mann-Whitney Test: strongly significant (p-value <
0.001, denoted by ‘***’), moderately significant (where 0.001
< p-value < 0.01, denoted by ‘**’), and marginally significant
(where 0.01 < p-value < 0.05, denoted by ‘*’).
We can see that HybridAD has significant performance improvement over other baseline models on the SWaT and WADI
datasets, while on the other three datasets, models such as
LSTM-VAE and MTAD-GAT also exhibit comparable performance. This phenomenon is related to the distribution of data

In Section IV-C2, we designed five model variants to verify
the effectiveness of the probability density model designed
in HybridAD. Each variant corresponds to an anomaly score
(which is strongly correlated with the model design). The first
three value-based model variants (ED-Only Prediction, EDOnly Reconstruct, ED-Composite) typically calculate anomaly
scores as the Euclidean distance between the model’s output
and the actual observation values. The latter two probability
density-based model variants (PD-Only Prediction, PD-Only
Reconstruct) calculate anomaly scores as the negative logarithm
of the probability density of the actual observation values under
the distribution output by the model. The specific definitions of
the anomaly scores in each model variant are shown below.
ED-Only Prediction: The anomaly score takes into account
only the prediction error, which is the mean square error between predicted and actual observations for each dimension, as
demonstrated by (12).
M

Sxt+1 =

1  i
2
x̂t+1 − xit+1 ,
M i=1

(12)

where M is the dimension size of the sequence.
ED-Only Reconstruct: The anomaly score only takes reconstruction error into account. As shown in (13), the error of the
observation at the moment t in the reconstruction sequence is
utilized as the anomaly score in this work.
M

Sx t =

1  i
2
x̂t − xit .
M i=1

(13)

ED-Composite: This anomaly score takes into account the
reliability of the prediction source, which is calculated as the
sum of the weighted reconstruction error and the prediction error
of the sequence, as shown in (14).

2
j
j
t
M
i=t−L+1 di ×
j=1 x̂i − xi
Sxt+1 =
DL
M

+

1  i
2
x̂
− xit+1 ,
M i=1 t+1

(14)

where di = αi−(t−L+1) and DL = ti=t−L+1 di . In experiment, α is a constant set to 1.25.
PD-Only Prediction: The anomaly score considers only the
prediction probability density, as specified in (15).
Sxt+1 = − log p xt+1 | μxt+1 , σxt+1 .

(15)

PD-Only Reconstruction: The anomaly score considers only
the reconstruction probability density and is defined as the

LIN et al.: HYBRIDAD: A HYBRID MODEL-DRIVEN ANOMALY DETECTION APPROACH FOR MULTIVARIATE TIME SERIES

reconstruction probability density of the observation xt in the
reconstructed sequence Wt , as given in (16).
Sxt+1 = − log p (xt | μxt , σxt ) .

(16)

REFERENCES
[1] L. Ruff et al., “A unifying review of deep and shallow anomaly detection,”
Proc. IEEE, vol. 109, no. 5, pp. 756–795, May 2021.
[2] G. Pang, C. Shen, L. Cao, and A. V. D. Hengel, “Deep learning for anomaly
detection: A review,” ACM Comput. Surv., vol. 54, pp. 1–38, 2021.
[3] Z. Li et al., “Multivariate time series anomaly detection and interpretation
using hierarchical inter-metric and temporal embedding,” in Proc. 27th
ACM SIGKDD Conf. Knowl. Discov. Data Mining, 2021, pp. 3220–3230.
[4] A. Blázquez-García, A. Conde, U. Mori, and J. A. Lozano, “A review on
outlier/anomaly detection in time series data,” ACM Comput. Surv., vol. 54,
pp. 1–33, 2021.
[5] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2019, pp. 2828–2837.
[6] Y. Zhang, Y. Chen, J. Wang, and Z. Pan, “Unsupervised deep anomaly
detection for multi-sensor time-series signals,” IEEE Trans. Knowl. Data
Eng., vol. 35, no. 2, pp. 2118–2132, Feb. 2023.
[7] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,” in
Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 3395–3404.
[8] J. Hou, Y. Zhang, Q. Zhong, D. Xie, S. Pu, and H. Zhou,
“Divide-and-assemble: Learning block-wise memory for unsupervised
anomaly detection,” in Proc. IEEE/CVF Int. Conf. Comput. Vis., 2021,
pp. 8791–8800.
[9] T. Kieu et al., “Anomaly detection in time series with robust variational
quasi-recurrent autoencoders,” in Proc. IEEE 38th Int. Conf. Data Eng.,
2022, pp. 1342–1354.
[10] W. Wu et al., “Developing an unsupervised real-time anomaly detection
scheme for time series with multi-seasonality,” IEEE Trans. Knowl. Data
Eng., vol. 34, no. 9, pp. 4147–4160, Sep. 2022.
[11] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” in Proc. ACM SIGMOD Int. Conf. Manage.
Data, 2000, pp. 93–104.
[12] H. Ringberg, A. Soule, J. Rexford, and C. Diot, “Sensitivity of PCA for
traffic anomaly detection,” in Proc. ACM SIGMETRICS Int. Conf. Meas.
Model. Comput. Syst., 2007, pp. 109–120.
[13] K.-L. Li, H.-K. Huang, S.-F. Tian, and W. Xu, “Improving one-class SVM
for anomaly detection,” in Proc. Int. Conf. Mach. Learn. Cybern., 2003,
pp. 3077–3081.
[14] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. IEEE
8th Int. Conf. Data Mining, 2008, pp. 413–422.
[15] P. Malhotra, L. Vig, G. Shroff, and P. Agarwal, “Long short term memory
networks for anomaly detection in time series,” in Proc. 23rd Eur. Symp.
Artif. Neural Netw., Comput. Intell. Mach. Learn., 2015, pp. 89–94.
[16] Z. Xiao, X. Xu, H. Xing, S. Luo, P. Dai, and D. Zhan, “RTFN: A robust
temporal feature network for time series classification,” Inf. Sci., vol. 571,
pp. 65–86, 2021.
[17] L. Zhong, L. Hu, and H. Zhou, “Deep learning based multi-temporal crop
classification,” Remote Sens. Environ., vol. 221, pp. 430–443, 2019.
[18] B. Zhou, S. Liu, B. Hooi, X. Cheng, and J. Ye, “BeatGAN: Anomalous
rhythm detection using adversarially generated time series,” in Proc. 28th
Int. Joint Conf. Artif. Intell., 2019, pp. 4433–4439.
[19] H. Zhao et al., “Multivariate time-series anomaly detection via graph attention network,” in Proc. IEEE Int. Conf. Data Mining, 2020, pp. 841–850.
[20] B. Zong et al., “Deep autoencoding gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Representations,
2018, pp. 1–19.
[21] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., 2021,
pp. 4027–4035.
[22] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly detector for
robot-assisted feeding using an lstm-based variational autoencoder,” IEEE
Robot. Automat. Lett., vol. 3, no. 3, pp. 1544–1551, Jul. 2018.
[23] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom, “Detecting spacecraft anomalies using LSTMs and nonparametric
dynamic thresholding,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl.
Discov. Data Mining, 2018, pp. 387–395.

877

[24] S. Lin, R. Clark, R. Birke, S. Schönborn, N. Trigoni, and S. Roberts,
“Anomaly detection for time series using VAE-LSTM hybrid model,”
in Proc. IEEE Int. Conf. Acoust., Speech Signal Process., 2020,
pp. 4322–4326.
[25] M. Abdelaty, R. Doriguzzi-Corin, and D. Siracusa, “DAICS: A deep
learning solution for anomaly detection in industrial control systems,”
IEEE Trans. Emerg. Topics Comput., vol. 10, no. 2, pp. 1117–1129,
Apr.–Jun. 2022.
[26] H. Xu et al., “Unsupervised anomaly detection via variational auto-encoder
for seasonal KPIs in web applications,” in Proc. World Wide Web Conf.,
2018, pp. 187–196.
[27] S. Zhang et al., “Efficient KPI anomaly detection through transfer learning
for large-scale web services,” IEEE J. Sel. Areas Commun., vol. 40, no. 8,
pp. 2440–2455, Aug. 2022.
[28] I. Goodfellow et al., “Generative adversarial nets,” in Proc. 27th Int. Conf.
Neural Inf. Process. Syst., 2014, pp. 2672–2680.
[29] D. Li, D. Chen, B. Jin, L. Shi, J. Goh, and S.-K. Ng, “MAD-GAN: Multivariate anomaly detection for time series data with generative adversarial
networks,” in Proc. Int. Conf. Artif. Neural Netw., 2019, pp. 703–716.
[30] X. Chen et al., “DAEMON: Unsupervised anomaly detection and interpretation for multivariate time series,” in Proc. IEEE 37th Int. Conf. Data
Eng., 2021, pp. 2225–2230.
[31] Y. Wang, A. Smola, D. Maddix, J. Gasthaus, D. Foster, and T.
Januschowski, “Deep factors for forecasting,” in Proc. Int. Conf. Mach.
Learn., 2019, pp. 6607–6617.
[32] D. Salinas, V. Flunkert, J. Gasthaus, and T. Januschowski, “DeepAR:
Probabilistic forecasting with autoregressive recurrent networks,” Int. J.
Forecasting, vol. 36, pp. 1181–1191, 2020.
[33] D. P. Kingma and M. Welling, “Auto-encoding variational bayes,” 2013,
arXiv:1312.6114.
[34] A. Siffer, P.-A. Fouque, A. Termier, and C. Largouet, “Anomaly detection
in streams with extreme value theory,” in Proc. 23rd ACM SIGKDD Int.
Conf. Knowl. Discov. Data Mining, 2017, pp. 1067–1075.
[35] A. P. Mathur and N. O. Tippenhauer, “SWaT: A water treatment testbed
for research and training on ics security,” in Proc. IEEE Int. Workshop
Cyber- Phys. Syst. Smart Water Netw., 2016, pp. 31–36.
[36] P. E. McKnight and J. Najab, “Mann-whitney U test,” in The Corsini
Encyclopedia of Psychology, Hoboken, NJ, USA: Wiley, 2010. [Online].
Available: https://doi.org/10.1002/9780470479216.corpsy0524

Weiwei Lin (Member, IEEE) received the B.S. and
M.S. degrees from Nanchang University, Nanchang,
China, in 2001 and 2004, respectively, and the Ph.D.
degree in computer application from the South China
University of Technology, Guangzhou, China, in
2007. He is currently a Professor with the School
of Computer Science and Engineering, South China
University of Technology. His research interests include distributed systems, cloud computing, Big Data
computing, and AI application technologies. He has
authored or coauthored more than 150 papers in refereed journals and conference proceedings. He is the reviewers for many international journals, including IEEE TRANSACTIONS ON COMPUTERS, IEEE TRANSACTIONS ON SERVICES COMPUTING, and IEEE TRANSACTIONS ON CLOUD COMPUTING.

Songbo Wang received the bachelor’s degree in 2021
from the South China University of Technology,
Guangzhou, China, where he is currently working toward the master’s degree in computer technology with
the School of Computer Science and Engineering. His
research interests include Big Data computing and
anomaly detection.

878

IEEE TRANSACTIONS ON EMERGING TOPICS IN COMPUTATIONAL INTELLIGENCE, VOL. 8, NO. 1, FEBRUARY 2024

Wentai Wu (Member, IEEE) received the bachelor’s
and master’s degrees from the South China University of Technology, Guangzhou, China, in 2015 and
2018, respectively, and the Ph.D. degree in computer
science from the University of Warwick, Coventry,
U.K., in 2022, Sponsored by CSC. He is currently
an Assistant Researcher with Peng Cheng Laboratory, Shenzhen, China. His main research interests
include distributed systems, federated learning, and
sustainable computing. He is a reviewer for multiple
high-impact journals and conferences, such as IEEE
TRANSACTIONS ON PARALLEL AND DISTRIBUTED SYSTEMS, IEEE TRANSACTIONS ON MOBILE COMPUTING, IEEE TRANSACTIONS ON SUSTAINABLE COMPUTING, International Conference on Machine Learning, and NeurIPS.

Dongdong Li received the M.S. degree with the College of Mathematics, Physics and Electronic Information Engineering, Wenzhou University, Wenzhou,
China, in 2019. He is currently working toward the
Ph.D. degree with the School of Computer Science
and Engineering, South China University of Technology, Guangzhou, China. His general research interests include federated learning, bioinformatics, and
machine learning.

Albert Y. Zomaya (Fellow, IEEE) is currently a
Peter Nicol Russell Chair Professor of computer science and the Director of the Centre for Distributed
and High-Performance Computing, The University of
Sydney, Sydney, NSW, Australia. To date, he has authored or coauthored more than 700 scientific papers
and articles and is the (co-)author/Editor of more than
30 books. As a sought-after speaker, he has delivered
more than 250 keynote addresses, invited seminars,
and media briefings. His research interests include
parallel and distributed computing, networking, and
complex systems. He is the Editor in Chief of the ACM Computing Surveys
and was the Editor in Chief of the IEEE TRANSACTIONS ON COMPUTERS during
2010–2014, and IEEE TRANSACTIONS ON SUSTAINABLE COMPUTING during
2016–2020. He is a decorated scholar with numerous accolades, including
Fellowship of the IEEE, American Association for the Advancement of Science,
and the Institution of Engineering and Technology. He is also a Fellow of the
Australian Academy of Science, Royal Society of New South Wales, Foreign
Member of Academia Europaea, and Member of the European Academy of
Sciences and Arts. He is a Clarivate 2022 Highly Cited Researcher.
PAPER_TEXT
