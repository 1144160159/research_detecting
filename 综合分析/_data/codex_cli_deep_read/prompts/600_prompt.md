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
# [600] Adaptive Unsupervised Anomaly Detection for Low-Quality Multivariate Time-Series Data
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
编号：600
题名：Adaptive Unsupervised Anomaly Detection for Low-Quality Multivariate Time-Series Data
年份：2026
DOI：10.1109/tkde.2026.3700672
来源：IEEE Transactions on Knowledge and Data Engineering
PDF：paper/10.1109_TKDE.2026.3700672.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\600.txt
- 原始字符数：93512
- 本次发送字符数：93512
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

1

Adaptive Unsupervised Anomaly Detection for
Low-Quality Multivariate Time-Series Data
Jiayi Liu, Donghua Yang, Jinbao Wang, Hong Gao, Jianzhong Li

Abstract—How should we perform anomaly detection on multivariate time-series data with missing data, attribute misplacement
and concept drift? The majority of existing anomaly detection
methods overlook the fact that data are often of low quality.
To address this challenge, we propose an adaptive unsupervised
anomaly detection method for low-quality multivariate time series
data. Our method introduces a self-attention mechanism that
integrates masked information and missing length information
to enhance the model’s capability in handling incomplete data.
Furthermore, we design a deep probabilistic adaptive memory network to improve the model’s adaptability to attribute
misplacement and concept drift. We also discuss the optimal
window size for effectively dealing with concept drift. Comparative experiments on multiple real-world datasets demonstrate
that our method can effectively detect anomalies in low-quality
multivariate time series data. The experimental results further
highlight the robustness of our model, proving its ability to
maintain high performance in the presence of data quality issues.
Index Terms—Anomaly detection, Low-Quality, Multivariate
Time-series data.

I. I NTRODUCTION
Multivariate time series are widely exist in industries, finance, and the internet, among other fields. By conducting indepth analysis of multivariate time series data, we can reveal
hidden abnormal patterns and behaviors within the data. For
instance, in the industrial field, analyzing these data helps us
monitor equipment performance and prevent potential failures.
In the financial industry, in-depth analysis of this data can
help us identify abnormal transactions and prevent fraudulent
behavior. In the field of cyber security, analyzing these data is
crucial for uncovering attack patterns and ensuring the security
and stability of networks. Anomaly detection, as a key means
of identifying and warning of these potential risks, provides
strong support for risk management and decision-making [1].
Therefore, the development of accurate and robust anomaly
detection for multivariate time series is particularly important.
Due to the lack of labels in the collected data and the
high cost of manual annotation on large-scale datasets, the
advantages of unsupervised learning methods in anomaly
This work was supported in part by the National Natural Science
Foundation of China under Grants U22A2025.(Corresponding author: Hong
Gao.)
Jiayi Liu, Donghua Yang, Jinbao Wang and Jianzhong Li are with the
Faculty of Computing, Harbin Institute of Technology, Harbin 150001, China
(e-mail: jiayiliu@stu.hit.edu.cn; yang.dh@hit.edu.cn; wangjinbao@hit.edu.cn;
lijzh@hit.edu.cn).
Hong Gao is with the Faculty of Computing, Harbin Institute of
Technology, Harbin 150001, China and is with the School of Computer
Science and Technology, Zhejiang Normal University, Jinhua 321000, China
(e-mail: honggao@zjnu.edu.cn).

detection of multivariate time series data are highlighted.
However, traditional unsupervised methods, such as distancebased methods [2], density-based [3], and tree-based methods
[4], have some limitations in capturing the complex spatiotemporal dependencies within multivariate time series and in
handling large-scale data [5]. In recent years, neural networks
have become a research hotspot for deep learning based
multivariate time series anomaly detection methods due to
their powerful feature learning and representation capabilities
[6]. For instance, autoencoders, as a powerful unsupervised
learning model, can effectively cope with the impact of noise
and identify anomalies by comparing the differences between
input and reconstructed output, thus being widely used.
Deep learning-based unsupervised anomaly detection aims
to learn general patterns from normal data to enable accurate
anomaly detection. Although existing methods have achieved
strong performances, most of them rely on well-structured
time series data while overlooking the pervasive data quality
issues in real-world scenarios. In practice, time series data
in real-world settings often suffer from missing data and
attribute misplacement caused by errors in data transmission
or acquisition, as well as distribution drift due to dynamic
data changes. These issues severely impair a model’s ability
to learn and reason, thereby posing fundamental challenges to
building high-precision and robust anomaly detection systems.
Specifically, existing methods still face significant challenges
in the following three aspects.
Firstly, in the real world, missing data is a common issue.
Data can be lost during the collection process due to equipment
failures, environmental factors such as sensors being affected
by weather or electromagnetic interference, transmission errors
such as data transmission interruptions caused by system
maintenance or updates, and human errors such as medical
testing equipment not being properly connected to patients
[7], [8]. However, missing values can disrupt the continuity
and integrity of the data, which may lead to inadequate model
training and reduced detection quality. It can be seen that
the existence of missing values fundamentally affects the performance of anomaly detection algorithms [9], [10]. Existing
methods mainly focus on imputing missing data reasonably
[5], [10]. However, these methods may mask anomalies and introduce errors. Additionally, they may increase computational
complexity due to sophisticated imputation methods.
Secondly, during the data collection process, misplaced
attribute values may occur, where a value of one attribute is
erroneously entered into another attribute, resulting in incorrect swaps between attribute values. Misplaced attribute values
are often observed in practice, such as in IoT environments

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

where workers might accidentally plug the sensor cables of a
wind turbine in the wrong positions, causing a misplacement
in the recorded data for attributes like voltage and temperature
[11]. When integrating data from different sources, the process
of information extraction and transformation can also easily
lead to misplaced attribute values [12]. Misplaced attribute
values are a type of error rather than an anomalies because
the correct data is indeed existing in the dataset, just placed
in the wrong location [11]. Typically, anomalies are defined
as observations that deviate from the normal pattern [13],
[14]. Unfortunately, misplaced attribute values also exhibit
this behavior, leading to the possibility that existing anomaly
detection may misidentify them as anomalies, which can
cause significant bias in data analysis and decision-making.
Therefore, the presence of misplaced attribute values in time
series significantly reduces the accuracy of anomaly detection.
However, the issue of misplaced attribute has not yet been
addressed in existing research [11].
Thirdly, the dynamic nature and non-stationarity of realworld environments cause the data distribution to change
over time, a phenomenon known as concept drift [15], [16].
The presence of concept drift can affect the accuracy of
anomaly detection [17], [18]. Since deep anomaly detection
models are typically trained on historical data, when the data
distribution changes during anomaly detection, the model may
not effectively adapt to the new data distribution, thereby
affecting its performance to detect anomalies. To ensure the
accuracy of anomaly detection methods, it is necessary to
identify and adapt to changes in data distribution.
In recent years, several methods have been proposed for
anomaly detection in time series with missing data, attribute
misplacement or concept drift [5], [19], [20]. However, these
researches have not consider the above three challenges at
the same time. However, these methods can only address one
specific challenge individually and are unable to tackle the
three major issues in low-quality data: missing data, attribute
misplacement, and concept drift at the same time.
To address the aforementioned challenges, this paper proposes an Adaptive Unsupervised Anomaly Detection method
(AUAD). It consists of two major networks: the Self-Attention
and Convolutional Neural Network(SA-CNN) and the Deep
Probabilistic Adaptive Memory Network.
In the SA-CNN network, we introduce a self-attention
mechanism that incorporates masking and missing length information. This mechanism provides the model with temporal
contextual information about missing values, enabling it to
handle missing data more flexibly. Subsequently, we employ
a multi-scale convolutional neural network for encoding, allowing the model to understand the integrity and structure
of the data at different scales. This effectively captures the
spatiotemporal features of the time series. We further introduce
a memory network to enhance the model’s ability to remember
normal data patterns. Specifically, the memory module is
designed to store normal feature representations learned from
the probabilistic model. By reintegrating the encoded features
of the input data with the similarity-weighted items from
the memory module, the model’s adaptability to misplaced
attribute is significantly enhanced.

2

The feature representations obtained from the two modules
are then fused into a final representation for reconstruction.
The two modules work in concert, leveraging the feature extraction and memory augmentation mechanisms to effectively
address anomaly detection in low-quality data.
During the detection phase, the anomaly score is computed
by combining the similarity between the input data and the
memory module with the reconstruction error. To adapt to
changes in the data distribution, we dynamically update the
memory information and threshold of the memory network
based on extreme value theory. This approach enhances the
accuracy and robustness of anomaly detection. Additionally,
we theoretically demonstrate the optimal window size for
effectively handling concept drift.
The contributions of this paper are highlighted as below.
1. To our knowledge, this paper is the first study to propose
anomaly detection for multivariate time series data in the
presence of missing data, attribute misplacement, and concept
drift. To this end, we have designed an adaptive unsupervised
anomaly detection method to address the challenge of detecting anomalies in low-quality multivariate time-series data.
2. This paper proposes a self-attention mechanism that
combines masking and missing length information to enhance
the model’s ability to handle incomplete data.
3. This paper proposes a method that enhances the model’s
ability to handle misplaced attribute by re-integrating the encoded features through fusion with similarity-weighted items
from the memory module.
4. This paper proposes a method for dynamically updating
the memory module, enabling the model to adapt to concept
drift in time-series data. Moreover, we discuss the optimal
window size for effectively handling concept drift.
5. Experimental results demonstrate that our method
achieves high accuracy and robustness in the presence of lowquality time-series data.
II. R ELATED W ORK
In recent years, deep learning-based anomaly detection
have been proposed and demonstrated well performance [21].
Compared to traditional anomaly detection algorithms, their
main advantage lies in their strong ability to learn nonlinear features. Currently, unsupervised multivariate time series
anomaly detection methods can be mainly divided into two
categories: prediction-based models and reconstruction-based
models.
The reconstruction-based models are to detect anomalies
through reconstruction errors. USAD [22] proposed a reconstruction method based on adversarial learning, which trains
two AE adversarially to amplify the reconstruction errors of inputs containing anomalies. MADGAN [23] uses LSTM-RNN
as the basic model for GAN generators and discriminators
to capture dependencies in time series data and integrates
reconstruction errors and discrimination errors as the basis for
judging anomalies. MSCRED [24] proposes an attention-based
convolutional long short-term memory (ConvLSTM) network
to capture spatiotemporal dependencies and utilizes a convolutional decoder to reconstruct the feature matrix for end-to-end

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

learning. OmniAnomaly [25] combines the advantages of GRU
and VAE, learning the normal patterns of multivariate time
series through a stochastic recurrent neural network model,
and uses reconstruction probabilities for anomaly judgment.
InterFusion [26] models the interdependencies and internal dependencies of multiple time series through a hierarchical Variational Auto-Encoder with two random latent variables, and
finally detects anomalies based on reconstruction information.
The EdgeConvFormer model [50] integrates dynamic graph
convolution with Transformer, employing Time2Vec encoding
and parallel sensor-specific attention to extract spatiotemporal features, and achieves anomaly detection in multivariate
time series via reconstruction error. Liu et al. [51] further
introduce a novel ”localization score” combined with physicsinformed knowledge, enabling EdgeConvFormer to perform
both anomaly detection and localization, thereby enhancing the
model’s interpretability. CT-DDPM [52] proposed a denoising
diffusion probabilistic model that integrates a Gaussian Copula
with a Transformer architecture. This method models the joint
distribution of noise using a Gaussian Copula during the
forward diffusion process and reconstructs the normal data
distribution through the reverse denoising process, thereby enabling effective anomaly detection in multivariate time series.
Based on prediction models detect anomalies by predicting
the future values of time series. Hundman et al. [27] proposed
an improved LSTM model that proposes a non-parametric
dynamic threshold to assess prediction errors. GDN [28] combines sensor embedding, graph structure learning, and graph
attention prediction, effectively learning the relationship graph
of sensors from multivariate time series data and detecting
anomalies within it. GTA [29] combines multi-scale dilated
convolution and graph convolution to obtain encodings, which
are then fed into the Transformer model to build and predict
time series data for future moments. RC-Attention [53] proposed a model that combines empirical mode decomposition
with recurrent convolutional encoding attention. It captures the
chaotic temporal dependencies of sequences through phase
space reconstruction and recurrent convolutional encoding,
reduces the interference of anomalous states on prediction
using a centered steady attention mechanism, and finally
identifies anomalies based on prediction errors.
Combining prediction-based and reconstruction-based models, such as MTAD-GAT [30] utilizes two parallel graph
attention network layers to learn the temporal and feature
dependencies among multiple time series, CAE-M [31] model
combines a deep convolutional autoencoder with an attentionbased bidirectional LSTM, aiming to describe complex spatiotemporal patterns through simultaneous reconstruction and
predictive analysis. DAGMM [32] combines a reconstructionbased autoencoder with a probability density-based GMM to
enhance the accuracy of anomaly detection. Xu et al. [33]
proposed a model based on an association-based criterion and
reconstruction, capturing the reconstruction characteristics of
data indirectly by evaluating the differences in association
between data points and sequences, thereby achieving anomaly
detection.
The aforementioned researches have overlooked a fact that,
in addition to noise and anomalies in the data, there are

3

also issues such as missing data and attribute misplacement.
Regrettably, attribute misplacement has not yet been explored
[11]. Regarding the issue of missing data, Xu et al. [9]
proposed an unsupervised anomaly detection algorithm called
Donut based on the Variational Auto-Encoder (VAE), which
incorporates missing data into the training to enhance the
model’s robustness against anomalous data. FluxEV [10] applies preprocessing on missing data and designs two interpolation strategies. GST-Pro [5] proposed dynamic graph neural
differential equations (DG-NCDEs) to model multivariate time
series, effectively capturing the spatiotemporal features of the
data even when it contains missing values. Based on a deep
probabilistic graphical model, SCNF-EM [34] is designed as a
new framework for unified data imputation and unsupervised
learning to improve the robustness of anomaly detection in
the presence of missing data. AD-CIFC [8] is an anomaly
detection method that combines data imputation and feature
collaboration. Besides, it introduces a new method for calculating the loss function under missing data conditions.
In addition, in dynamic environments, the distribution of
data changes over time, which is known as concept drift.
However, static detection methods often have a decrease in accuracy over time and environmental changes due to their lack
of adaptability. Siffer et al. [17] proposed the extreme value
theory-based anomaly detection SPOT and DSPOT, which are
only sensitive to extreme values and have limited adaptability
to concept drift. StepWise [18] proposed a framework that
can let any type of anomaly detection algorithm quickly adapt
to concept drift. However, this method can only handle the
data that trends are almost consistent before and after the
occurrence of concept drift. Based on RNN for multi-step
prediction of time series, Saurav et al. [19] use prediction
errors to update the model and enable the model to adapt to
changes in data distribution.
In summary, there is currently no research that discusses
anomaly detection in the presence of missing data, attribute
misplacement, and concept drift. The limitations of existing
methods have inspired our research on anomaly detection in
multivariate time series when facing these challenges at the
same time.
III. PROBLEM FORMULATION
A. Problem Definition
Definition 1(Multivariate time series) A multivariate time
series can be represented as X = (X1 , · · · , Xn )T ∈ Rn×T ,
where n represents the total number of attributes, and T
denotes the data length of each attributes. The value of the
ith attribute at j th timestep is denoted as Xij .
Anomaly detection: To take into account contextual information, we apply a sliding window of length W on multivariate time series (MTS) to calculate the anomaly detection
results. Specifically, we calculate the detection score for the
sample data within the current window; if it exceeds the
model’s preset threshold, the sample is marked as an anomaly.
B. Overview
In this paper, we propose an Adaptive Unsupervised
Anomaly Detection(AUAD) method for low-quality data,

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

which consists of two main components, as illustrated in
Fig.1. Fig.1(a) is an attention-based multi-scale convolutional
network, and Fig.1(b) is a deep probabilistic adaptive memory
network.
In the SA-CNN network, the input data X is first concatenated with the missing mask M and temporal information
T to form an enhanced data representation. This step aims
to integrate crucial temporal and missingness information to
enrich the semantic content of the data. Subsequently, the
data is re-represented through a self-attention mechanism to
improve data integrity and feature expressiveness. The rerepresented data is mapped into a latent feature space via
a multi-scale convolutional neural network to further extract
and understand the complex spatiotemporal features of the
data. In the memory network, the input data X is transformed
into a feature representation Z through an RNN network. The
memory module stores feature information derived from Z
after probabilistic distribution modeling.
The feature representation Z is re-integrated by fusing it
with the similarity-weighted items of the memory module
to obtain a new encoded feature Zm . Subsequently, Zm is
combined with the features Zc extracted by the convolutional
network and passed through a fully connected layer for reconstruction. Finally, an integrated anomaly scoring mechanism
is constructed by combining the similarity between the data
and the memory module with the reconstruction error of the
data. This mechanism employs extreme value theory to set
the critical threshold for anomaly detection, which is used
to determine whether a data point is anomalous and whether
the information stored in the memory module needs to be
updated to adapt to new changes in the data distribution. This
approach not only enhances the accuracy of anomaly detection
but also enables the memory module to dynamically adapt
to the evolution of the data, thereby improving the model’s
adaptability and robustness for time-series anomaly detection.
IV. M ETHOD
A. Self Attention-based Multi-Scale Convolutional Neural Network
The key to anomaly detection in multivariate time-series
data lies in the ability to capture temporal dependencies within
variables and correlations between variables. In order to capture the spatiotemporal features of data more accurately and
reliably, we introduce missing position and length information
to comprehensively consider the missing data regions.
We designed a mask matrix M and a missing length
information T to assist in the encoding of raw data and the
acquisition of latent space. The primary function of the mask
matrix M is to indicate which data are missing. The missing
length information T, on the other hand, can mark the duration
of the missing data. The construction formulas for the mask
matrix M and the missing length information T are as follows,

1 if Xij is observed
Mij =
,
(1)
0 if Xij is missing

1 + Ti(j−1) if Mij = 0
Tij =
,
(2)
0
if Mij = 1

4

where Xij represents the data corresponding to the j th timestamp of the ith attribute. If Mij = 0, it means that data Xij
is missing. For any ith attribute in j th timestamp, if data Xij
is missing, The value of Tij is obtained by adding 1 to the
value from the previous moment.
Given a multivariate time series data X, along with the mask
matrix M and the missing length information T, we construct
a new input matrix X̂ as follows:
X̂ = Concat(X, M, T),

(3)

where Concat is a concatenation operation that can combine
the temporal data X, the mask matrix M, and the missing
length information T to form a new matrix.
To enhance the accuracy of the model’s reconstruction
results, we attempt to artificially create missing data for the
existing data X For each batch of data input into the model, we
artificially make some missing of the originally existing data
at a certain ratio randomly. These values do exist, but they are
invisible to the model, i.e., artificially missing. To calculate
the reconstruction of these artificially missing values in the
subsequent loss function, we construct an artificial missing
indicator matrix I as follows.

1 if Xij is artificially masked
Iij =
,
(4)
0 otherwise
where Xij represents the data corresponding to the j th timestamp of the ith attribute. If Iij = 1, it means that data Xij
is an artificial missing. It is important to note that regardless
of whether the data is naturally missing or artificially missing,
our M matrix will mark it out, while the I matrix will only
mark the artificially missing data.
In the field of time series data research, the attention
mechanism is also an effective way to focus on important data
and information. We use self-attention mechanisms to mine the
effective information from time series data. Attention weights
are calculated through matrix dot products and softmax functions. Given the query matrix Q, key matrix K, the matrix X̂
get by formula (3) and value matrix V as follows,
Q = Wq X̂, K = Wk X̂, V = Wv X̂,

(5)

where Wq ∈ Rdk ×dk ,Wk ∈ Rdk ×dk and Wv ∈ Rdk ×dk
are the attention weight matrices for the query matrix Q,
key matrix K, and value matrix V , respectively. The dk is
the dimension of weight matrices. The formula for the selfattention mechanism is as follows,


QKT
(6)
V
SelfAtt (Q, K, V) = Softmax √
dk
We take X̂ = Wv X̂, with the added attention weights, as the
input to the multi-scale convolutional network.
We constructed a multi-scale convolutional network. Multiscale convolutional neural networks bring different receptive
fields to the network without introducing too many parameters
and computational complexity. We uses convolutional layers
to gradually reduce the size of the input data and extract
feature representations of the latent space. Similarly, the fully
connected networks gradually restores these features to their
original size through upsampling operations. The training

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

Self-Attention

(a)
� = Concat(X, M, T )

X

5

��

�

Convolutional Network
Kernel 1

Convolutional Network

在此处键入公式。

��

Kernel 2

�’

Kernel 3

w
Similarity
Calculation

RNN

FC

Convolutional Network

��

(b)

��

Memory

��

�
Fig. 1. The overview of unsupervised anomaly detection for low-quality data.

objective of the network is to reduce the reconstruction error
between the input data and the output data. In this process,
we capture the temporal and spatial relationships between
different attributes. Secondly, based on the mask matrix M
and the missing length information T, we effectively obtain
the latent representations of the data.
Specifically, assuming there are m different scales of convolution, which means there are m convolutional kernels. Each
convolutional kernel is composed of a set of parameters Wm
and bm then the output of the convolution can be expressed
as follows.
cm = Conv2D(X̂Wm + bm ),

(7)

hm = f1 (cm ),

(8)

where Conv2D is the two-dimensional convolution and f1
is a linear function. The convolution layer includes three
convolutional kernels with sizes of 3 × 3, 5 × 5, and 7 ×
7 respectively. The stride for all is 2. No activation functions
are used in the process of reconstructing the data.
This means that according to formula (7) and (8), we can
obtain h1 , h2 , and h3 which are affected at different convolutional scales. By combining the hidden layers at different
scales, we get the latent space Z1 as follows,
Z1 = (h1 + h2 + h3 )/3.

(9)

After the multi-scale convolutional network performs latent
feature extraction on the input data, the output Z1 is connected
to a multi-layer fully connected network, and then a Flatten
layer is used to flatten the obtained latent feature representation
into 1D data, denoted as Zc . The deep probabilistic adaptive
memory network for analyzing attribute misplacement and
concept drift will obtain a latent representation of the data
distribution, which is flattened and denoted as Zm (details are

described in Subection 4.2). Combining the two latent space
in a comprehensive latent space Z̄ as follows,
Z̄ = αZc + (1 − α)Zm ,

(10)

where α is a weight parameter used to measure the importance
of the two latent space representations.
Then, we use a multi-layer fully connected network to
gradually restore these latent space representations into reconstructed data X′ . The formal representation is as follows,
X′ = F C(Z̄Wd + bd ),

(11)

where F C represents the multi-layer fully connected network.
Wd and bd are the weight parameter vector and bias vector
of the fully connected layer, respectively.
B. Deep Probabilistic Adaptive Memory Network
Inspired by trajectory anomaly detection [35], we can
analogize attribute misplacement to trajectory switching. From
this perspective, each attribute can be regarded as an independent trajectory, and attribute misplacement is equivalent
to the process of switching from the current trajectory to
another. Unlike trajectory anomaly detection, our goal is not to
identify attribute misplacement itself, but to reduce the false
positives caused by attribute misplacement. To address this
issue, we designed a memory module that stores the timerelated encoded features of each attribute. Then, by querying
the similarity with memory items, we integrate the encoded
features to eliminate the bias in the input data caused by
attribute misplacement. We will introduce a deep probabilistic
network and provide a detailed description of the adaptive
memory module below.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

6

First, we construct an RNN model to map data into vector
representations in a low-dimensional space. The RNN structure can effectively capture information along the timeline. At
each time step t, the RNN updates its hidden state based on
the current input xt and the hidden state of the previous time
step ht−1 :
ht = f2 (xt , ht−1 ),
(12)
where f2 is a deterministic non-linear function to be learned,
which can be implemented with LSTM or GRU.
Due to the presence of noise and missing data in the input,
to address the impact of this uncertainty, we use probability
distributions to obtain latent features.
qϕ (z|x) = N (µx , diag(σx2 )),
M

(13)

M

where µx ∈ R and σx ∈ R , we use a neural network
g2 (ht ) to learn the mean and standard deviation {µx , σx },
latent feature z ∈ Z = {z1 , z2 , ..., zn }, Z ∈ Rn×L , where L
is the length of latent feature matrix Z.
In order to distinguish the normal latent features of different
data attributes, we utilize the Gaussian distribution to model
it as
(14)
pγ (z|n) = N (µn , diag(σn2 )),
where n is the number of data attributes. It follows a multinomial distribution as:
pγ (n) = Mult(π),

(15)

where π is the parameter of the multinomial distribution.
According to the research in [35], we can consider µn ∈
RM as the normal encoded features of each attribute in the
latent space. The encoded features corresponding to attributes
x1 ∼ xn are µ1 ∼ µn , respectively, and are stored in the
memory module, implemented by the matrix M ∈ Rn×L .
The memory module [36], [37] includes a memory representation to represent the encoded feature and a weight matrix
obtained from the similarity of the memory items and the
input z. To address attribute misplacement, we re-integrate
the encoded features by querying the similarity with memory
items. The specific operation is as follows. First, we calculate
the similarity between the encoded feature z and all memory
items to obtain the weight vector w. In this paper, we use
cosine similarity
z · µ⊤
i
(16)
.
wi =
∥z∥∥µi ∥
Then, the memory module outputs ẑ
ẑ = wM =

n
X

wi µi .

(17)

i=1

The ẑ is the final latent feature obtained by the deep probabilistic adaptive memory network. We use latent features ẑ to
reconstruction x′′ can be formalized as follows.
pθ (x′′ |ẑ) = N (µx , diag(σx2 )),

(18)

The latent feature ẑ ∈ Ẑ = {zˆ1 , zˆ2 , ..., zˆn }, Ẑ ∈ Rn×L . The
flattened output of Ẑ, denoted as Zm , and the flattened output
of the self attention-based multi-scale convolutional network,
denoted as Zc , constitute a new latent space.

When concept drift occurs, it means that the statistical
properties or distribution of the data have changed, which
may render the information stored in the memory module no
longer applicable to the current new data patterns. Therefore,
we need to update the information in memory. An intuition
is that we can assess whether concept drift has occurred by
evaluating the similarity between z and the memory items
stored in memory. If the similarity decreases, this indicates
that the memory items in memory may no longer represent
the current data distribution.
Definition 2(Memory similarity)For input data x, we can
get the similarity between its latent features z and each
memory item as wi . The similarity between x and memory
is defined as follows:
n
X
Wsim =
wi .
(19)
i=1

Memory similarity may be negative. A negative memory
similarity indicates the presence of unusual patterns in the
data. This will attract the attention of the model and facilitate the detection of anomalies. To prevent the introduction
of anomalies during memory updates, we have adopted the
following two measures. First, we construct a comprehensive
scoring mechanism that combines the similarity between the
data and the memory module with the reconstruction error of
the data. This mechanism provides a more accurate assessment
of when memory updates are necessary (details are described
in Subection 4.4). Second, when updating the memory module,
we select an appropriate window length to ensure that sufficient new data are available to accurately capture the current
data distribution (details are discussed in Section 5). We can
more effectively identify concept drift and update the memory
module accordingly by these measures. This ensures that the
model can adapt to the evolution of the data, thereby enhancing
the accuracy and robustness of anomaly detection.
C. Joint Optimization Objective
The objective of deep probabilistic adaptive memory network is to maximize the marginal log-likelihood of the training
data and the formula is as follow.
log pθ (X1 , X2 , ..., XN ) =

N
X

log pθ (Xj ),

(20)

i=1

where X1 , X2 , ..., XN are N training attribute samples. the
evidence lower bound on the marginal likelihood of each X
is


log pθ (X) ≥ Eqϕ (z|X) log pθ (X|z)


−Eqϕ (z|X) DKL (qϕ (c|X)||pγ (c))
(21)


−Eqϕ (c|X) DKL (qϕ (z|X)||pγ (z|c)) ,
where DKL (·||·) is the KL-divergence between two distributions.
After the model reconstructs all missing values, we measure the reconstruction error using the Mean Absolute Error
(MAE). The reconstruction error loss consists of two parts.
One part is the reconstruction error of the non-missing data

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

7

under the influence of the mask M , denoted as LM . The other
part is the reconstruction error of the artificially missing data
under the influence of the artificial missing mask I, denoted
as LI . The reconstruction error loss is calculated as follows:
Pn PT
′
i=1
j=1 |(Xij − Xij ) ⊙ Mij |
,
(22)
LM =
Pn PT
i=1
j=1 Mij
Pn
LI =

i=1

PT

′
j=1 |(Xij − Xij ) ⊙ Iij |
,
PT
i=1
j=1 Iij

Pn
loss =

1
(LM + LI ).
2

(23)

(24)

We adopt the standard supervised learning paradigm to train
the model, optimizing the network parameters by minimizing
the mean squared error loss between the predicted outputs and
ground-truth results. Based on the training dataset and the loss
function formulations in equations (22)-(24), we iteratively
refine the model parameters via backpropagation. The training
process terminates upon reaching the predefined number of
epochs.
D. Anomaly Detection of Adaptive Threshold
After the model training is completed, we use our proposed
model to perform anomaly detection on newly acquired data.
Given a multivariate time series X that needs to be detected,
obtain its reconstructed representation X ′ . The anomaly detection score s(X) is calculated as follows.
s=

|X·j − X·j′ |
Pn
.
n sim=1 Wsim

1

F̄t (x) = P (X − t > x|X > t) ∼ (1 +

γx − γ1
)
σ

(27)

The result shows that the distribution of threshold exceeding
part (X − t) meets the requirements of Generalized Pareto
Distribution(GPD) with parameters γ, σ. That is, the tail
distribution can be fitted by the generalized Pareto distribution(GPD). γ and σ can be quickly calculated using the
Grimshaw algorithm. From this, we can get the threshold value
of the overall distribution, and the calculation formula is as
follows:
σ̂ qn
zq ≃ t + (( )−γ̂ − 1)
(28)
γ̂ Nt
where t is the initial threshold and the empirical value is
98%; σ and γ are parameters of GPD, which are obtained
by maximum likelihood; q is the expected probability; N is
the total number of current samples; Nt is the peak number,
i.e. Xi > t. The POT strategy provides us with a method to
estimate zq . With the support of the aforementioned methods,
the adaptive threshold approach is detailed in Algorithm 1.
According to the algorithm we proposed and Equation (25),
the anomaly score s(X) can be obtained. Based on Equations
(26) to (28) and the anomaly score s(X), we employ the POT
strategy following the procedure outlined in Algorithm 1 to
compute the anomaly threshold and produce the output. The
key aspect of the POT strategy lies in calculating zq using
Equation (28) and determining anomalies by comparing the
anomaly score s(X) with zq . Values of s(X) that exceed zq
are placed into the anomaly set and subsequently output.

(25)

where X·j represents all elements of the j th column of X.
The absolute average error between the j th column of X and
the j th column of X ′ is calculated. When this score s exceeds
a given threshold, we consider the data at this moment to be
anomalous.
In practice, the distribution of time-series data may change
over time due to concept drift, making it challenging to detect
anomalies using a single, static threshold. If the parameters
are not set accurately, this may lead to a large number of false
positives or false negatives. Therefore, we propose an adaptive
threshold algorithm based on Extreme Value Theory [17].
Extreme value theory refers to the distribution of extreme
events that we may observe by inferring without any distribution assumption based on the original data, which is the
extreme value distribution (EVD). Its mathematical expression
is as follows:
Gγ : x 7→ exp(−(1 + γx)− γ ), γ ∈ R, 1 + γx > 1.

Pickands-Balkema-de Haan theorem [40] (also called second
theorem in EVT) given below.

(26)

The γ is the extreme value index, which depends on the
extreme value data of different distributions. In order to fit
the EVD to the tail of the unknown input distribution, it
is necessary to estimate γ, But it is difficult to calculate it
effectively. To solve this problem, the Peaks-Over-Threshold
(POT) approach is proposed [17]. This method depends on the

Algorithm 1: ADAT(Anomaly Detection of Adaptive
Threshold)
Input: s1 , . . . , sn , n, q
Output: Set of anomalies A
1 A ← ∅, Yt ← ∅ zq , t ← POT(s1 , . . . , sn , q);
2 k ← n;
3 for i > n do
4
if si > zq then
5
Add (i, si ) in A;
6
else if si > t then
7
Yi ← si − t;
8
Add Yi in Yt ;
9
Nt ← Nt + 1;
10
k ← k + 1;
11
γ̂, σ̂ ← Grimshawk(Yt );
12
zq ← CalcThreshold(q, γ̂, σ̂, k, Nt , t);
13
Update Memory;
14
else
15
k ← k + 1;
To update memory, we first measure the gap between data
and memory within the window. Let Wcurr be the sets of
similarity scores on the current window and Wlast be those
on the last window used to update the model. To measure
the difference between Wlast and Wcurr , we use the mean

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

8

difference bound method based on the Hoeffding inequality
[48] to define reliability.
Theorem 1 (Hoeffding’s Inequality-Based Mean Difference
Bound): Given independent random variables X and Y
bounded by [amin , amax ], the
of the sample
Pprobability
Pm mean
n
1
difference between X̄ = n1 i=1 Xi and Ȳ = m
j=1 Yj is
bounded by
−2ϵ2

Pr{|X̄ − Ȳ | ≥ ϵ} ≤ e (n−1 +m−1 )(amax −amin )2 .

(29)

We calculate memory reliability based on Theorem 1. The
memory reliability within the current window is denoted as
rM and calculated as follows.
−bϵ2

rM = e (qmax −qmin )2 ,

(30)

where
b = |Wcurr | = |Wlast |,
ϵ = |avg(Wcurr ) − avg(Wlast )| ,
qmax = max(max(Wcurr ), max(Wlast )),

window is equal to the window size, that is, n = W . We
denote S = (bi − ai )2 . We have



W ϵ21
(33)
A : Pr X 1 − µ1 ≥ ϵ1 ≤ exp −
S



W ϵ22
(34)
B : Pr X 2 − µ2 ≥ ϵ2 ≤ exp −
S



2W ϵ2
(35)
Pr X w − µ ≥ ϵ ≤ exp −
S
Obviously, we have X w = (X 1 +X 2 )/2. Let the probability
W ϵ2
of event A occurring exp − S 1 be denoted as q1 , and the


W ϵ2
probability of event B occurring exp − S 2 be denoted
as q2 . The probability of both events A and B occurring
simultaneously Pr(AB) is given by
Pr(AB) = 1 − Pr(A) − Pr(B)

(31)

= 1 − (1 − q1 ) − (1 − q2 )
= q1 + q2 − 1.

qmin = min(min(Wcurr ), min(Wlast )).
If rM is less than the set threshold, the memory will perform
incremental updates based on the potential feature representations obtained from the data information in the current
window.
V. A NALYSIS
In this section, we investigate the optimal window size
for effectively handling concept drift. Theoretically, a larger
window can more accurately reflect the overall distribution of
the data. However, an excessively large window may impede
the model’s ability to rapidly adapt to changes in the data
distribution. Therefore, the key is to find a proper balance,
ensuring that the window collects a sufficient amount of data
in the shortest possible time to accurately understand the
current data distribution. Such a window size should not only
be representative of the overall data distribution but also be
capable of swiftly responding to any new changes in the data
distribution.
Our primary approach is to partition the data within the
window into two segments with equal sample sizes. We then
calculate the deviations of the sample means of the left
segment, the right segment, and the entire window from the
expected mean. If these sample means are close to the expected
mean with high probability, it indicates that the window size
is appropriate.
A window of length W is partitioned into two parts and the
sample means of these two parts are X 1 and X 2 , respectively.
The mean of all samples within the window is denoted as X w .
According to Hoeffding’s inequality, we have



2n2 ϵ2
Pr X − µ ≥ ϵ ≤ exp − Pn
,
(32)
2
i=1 (bi − ai )
where n denotes the number of samples within the window.
bi and ai represent the maximum and minimum values of
the samples, respectively. The number of samples within the

(36)

We choose reasonable values for ϵ1 and ϵ2 such that q1 and q2
are greater than 0.5, thereby ensuring that the sample means
X 1 , X 2 , and the population means µ, µ2 are likely to be close
with high probability.
Let ϵ = (ϵ1 + ϵ2 )/2and ϵ1 < ϵ2 . We
 have
 0 < ϵ1 <
W ϵ21
W ϵ22
ϵ < ϵ2 . Let D = exp − S
+ exp − S . Owing to




W ϵ21
W ϵ22
exp − S , exp − S
∈ (0.5, 1), we have D ∈ (1, 2)
If (µ1 + µ2 )/2 ≥ µ, we have






W ϵ21
W ϵ22
2W ϵ2
exp −
+ exp −
− 1 ≤ exp −
.
S
S
S
(37)
The inequality (37) can be rewritten as follows,


2W ϵ2
(38)
.
D − 1 ≤ exp −
S
We have
W ≤

Sln(Dmin − 1)
.
−2ϵ2

(39)

If (µ1 + µ2 )/2 ≤ µ, we have






W ϵ22
W ϵ2
W ϵ21
+ exp −
− 1 ≥ exp −
.
exp −
S
S
S
(40)
The inequality (40) can be rewritten as follows,


2W ϵ2
(41)
D − 1 ≥ exp −
.
S
We have
W ≥

Sln(Dmax − 1)
.
−2ϵ2

(42)

Inequalities (39) and (42) demonstrate that when the value
Sln(Dmax −1) Sln(Dmin −1)
of W is within the interval
,  −2ϵ2 ], the
−2ϵ
 [
 2
W ϵ2

W with probability exp − S 1
reasonable.

W ϵ2

+ exp − S 2

− 1 is

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

VI. E XPERIMENT R ESULTS
A. Dataset
SWaT (Secure Water Treatment) Dataset: This dataset originates from a water treatment experimental platform. Data is
collected at a frequency of once per second over a period of
11 days, encompassing records from 51 sensors. The dataset is
divided into a training set and a testing set, with the first 7 days
serving as the training set, which does not contain anomalies
or attack behaviors; the last 4 days serve as the testing set,
which includes 36 attacks, with approximately 11% of the
time steps labeled as anomalies.
WADI (Water Distribution) Dataset: This dataset simulates a
water distribution system composed of a large number of water
supply pipes, forming a more complete and realistic network
for water treatment, storage, and distribution. The dataset
includes 14 days of normal operation data, which constitute the
training set. In the following days, several controlled physical
attacks were conducted, which correspond to anomalies in the
testing set, with attacks occurring at different time intervals.
SMD (Server Machine Dataset) Dataset: This dataset is collected from server machine data of a large internet company.
The dataset is evenly divided into two parts, with the first half
containing no anomalies and can be used as a training set; the
second half contains attack behaviors and can be used as a
testing set.
Regarding the above data, we will conduct experiments
without any modifications for comparison and also experiments where data is altered to include position swapping and
data missing for comparison.
Baselines: Several methods for detecting anomalies are
used as baselines and be compared with our algorithm. An
introduction to the baseline is shown below.
(1) DAGMM [41]: It is a Deep Autoencoding Gaussian
Mixture Model (DAGMM) for unsupervised anomaly detection. The model utilizes a deep autoencoder to generate a lowdimensional representation and reconstruction error for each
input data point, which is further fed into a Gaussian Mixture
Model.
(2) LSTM-VAE [42]: The LSTM-VAE is a type of variational autoencoder that leverages the characteristics of long
short-term memory networks. This model integrates signals
and reconstructs their expected distribution by introducing a
prior that varies with progress. When the detector finds that the
anomaly score based on reconstruction exceeds the threshold
set based on the state, it will report an anomaly.
(3) GDN [43]: Given high-dimensional time series data.
This approach combines a structure learning approach with
graph neural networks, additionally using attention weights to
provide explainability for the detected anomalies.
(4) USAD [44]: It is based on adversely trained autoencoders. Its autoencoder architecture makes it capable of learning in an unsupervised way. The use of adversarial training and
its architecture allows it to isolate anomalies while providing
fast training.
(5) TimesNet [45]: To tackle the limitations of 1D time
series in representation capability, TimesNet extends the analysis of temporal variations into the 2D space by transforming

9

the 1D time series into a set of 2D tensors based on multiple
periods. This transformation can embed the intraperiod and
interperiod-variations into the columns and rows of the 2D
tensors respectively, making the 2D-variations to be easily
modeled by 2D kernels.
(6) DCdetector [46]: DCdetector is a multi-scale dual attention contrastive representation learning model. DCdetector
utilizes a novel dual attention asymmetric design to create the
permutated environment and pure contrastive loss to guide
the learning process, thus learning a permutation invariant
representation with superior discrimination abilities.
(7) FluxEV [10]: FluxEV applies preprocessing on missing
data and designs two interpolation strategies.
(8) GST-Pro [5]: GST-Pro proposed dynamic graph neural
differential equations (DG-NCDEs) to model multivariate time
series, effectively capturing the spatiotemporal features of the
data even when it contains missing values.
(9) AERO [47] : AERO is a novel twostage framework
tailored for unsupervised anomaly detection in astronomical
observations. AERO is not only capable of distinguishing
normal temporal patterns from potential anomalies but also
effectively differentiating concurrent noise, thus decreasing the
number of false alarms.

B. Metrics
We use precision, recall, and F1 score to represent the
performance of our algorithm. F1 score is such an efficient
method that many researchers use it as an evaluation criterion
and we will use it as well. To calculate the F1 score, true
positive (TP), false positive (FP), true negative (TN), and false
negative (FN) are needed to calculate accuracy and recall. The
formula is as follows,
precision =

recall =

F1 =

TP
,
TP + FP

TP
,
TP + FN

2 × precision × recall
.
precision + recall

(43)

(44)

(45)

In all datasets, we currently adopt the point adjustment strategy
that is commonly employed in the majority of existing literature. Although the point adjustment strategy has been widely
adopted by many mainstream studies, to further rigorously validate the performance of our proposed method, we additionally
report F1 scores computed without point adjustment(F1-w/o
PA) for both our proposed method and baseline approaches.
These results are presented in table III to table II.
Furthermore, in recent research works, several scholars have
begun to adopt F1-PA%K [49], an evaluation metric that
represents an intermediate compromise between the F1 pointadjusted strategy and the F1 non-point-adjusted strategy. Let
ŷt denote a data point to be detected. The computation for this

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

10

90

60

F1 (%)

SWaT
SMD
WADI

50

80

70

70

60
SWaT
SMD
WADI

50
40

40

60

120

180

240

300

20

360

20
60

120

180

Epochs

+80

+60

+40

+20

0

SMD
Dataset

WADI

Fig. 5. The impact of altering sample length on
the data with 10% missing rate

F1 (%)

F1 (%)

300

360

60

120

90
80
70
60
50
40
30
20
10
0

100
200
300
400
500

+60

+20

0

SMD
Dataset

WADI

Fig. 6. The impact of altering sample length on
the data with 20% missing rate

point being labeled as anomalous, i.e., ŷt = 1, is formulated
as follows,


1, if

 A(wt ) > δ or′ ′




|{t | t ∈ Sm , A(wt′ ) > δ}|
t
∈
S
and
>
K
m
ŷt =
|Sm |




0, otherwise,
(46)
m
where Sm = {tm
s , . . . , te } denotes the m-th contiguous
m
anomalous time segment, with tm
s and te representing the
start and end timestamps of this segment, respectively. |Sm | =
m
tm
e − ts + 1 indicates the length of the anomaly segment;
′
A(wt ) represents the anomaly score output by the model for
time window wt′ ; δ is the threshold employed for determining
whether a single time point is anomalous; and K∈ [0, 100]
serves as the core hyperparameter of the PA%K protocol,
specifying the minimum detection ratio required to trigger the
point adjustment mechanism. Specifically, point adjustment is
applied to all time points within segment Sm only when the
proportion of detected anomalous time points exceeds K%. In
this paper, the value of K is set to 30.
C. Performance Comparison
The original experimental data is complete without any
missing values,attribute misplacement and concept drift. To
meet the needs of our experiments, we make some missing values in some attributes of the original data. The types of missing
values include single-point missing and continuous missing.
The experiment designed three missing value scenarios to
test the performance of anomaly detection algorithms after

240

300

360

Fig. 4. The impact of varying epochs with 30%
missing rate

+80

+40

SWaT

180

Epochs

Fig. 3. The impact of varying epochs with 20%
missing rate

+100

100
200
300
400
500

SWaT

240

Epochs

Fig. 2. The impact of varying epochs with 10%
data missing rate
100
90
80
70
60
50
40
30
20
10
0

SWaT
SMD
WADI

50

30

30

30

60

40

F1 (%)

F1 (%)

70

80

F1 (%)

80

90
80
70
60
50
40
30
20
10
0

100
200
300
400
500

+80

+60

+40

+20

0

SWaT

SMD
Dataset

WADI

Fig. 7. The impact of altering sample length on
the data with 30% missing rate

data deletion under different missing rates. These scenarios
include a missing rate of 10%, 20%, and 30%. Additionally,
we swapped 2% of the data between two attributes of the
original data and created a single instance of concept drift.
In the following All experiments, we will adopt this setup.
Considering that traditional multivariate time series anomaly
detection models can only perform anomaly detection tasks
on datasets without missing values, introducing missing values
may render traditional models inexecutable. Therefore, before
applying traditional models to datasets with missing values, it
is necessary to first fill in the missing values. For different
datasets, this study selected a value that is not within the
reasonable range of these datasets, such as using -1000 to fill
in missing values in a dataset with a value range of [0,100].
The comparison between our algorithm and the baseline
methods is presented in table III to table II. The experimental results indicate that our algorithm performs better on
low-quality data. This implies that our algorithm has better
robustness.
To verify the superior performance of our algorithm in
anomaly detection on missing data compared with other
algorithms, we conducted comparisons with FluxEV, GSTPro, USAD-mean and USAD-linear. FluxEV and GST-Pro
are anomaly detection algorithms proposed to address data
missing issues. USAD-mean and USAD-linear represent algorithms using mean value method and linear imputation
respectively to fill in missing data before executing USAD
algorithm. For the remaining baseline algorithms, we adopt
the cubic spline imputation provided by GST-Pro. Ours-mean
and Ours-linear represent our proposed method using mean

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

90

90

+90

80

+80

75
+70

65
Mem-2
No Mem-2
Mem-4
No Mem-4

60
55
20%
Missing Rate

Fig. 8. The impact of memory network on the data
with 10% missing rate

60
SWaT
SMD
WADI

4%

5%

6%

Artificial Missing Rate

Fig. 11. The impact of artificial missing rate on
the data with 10% missing rate

F1 (%)

F1 (%)

70

3%

Mem-2
No Mem-2
Mem-4
No Mem-4

+60

+50

10%

20%
Missing Rate

30%

Fig. 9. The impact of memory network on the data
with 20% missing rate

80

2%

+70

65

50

90

40

70

55

30%

50

75

60

+60

+50

10%

+80

45
40
35
30
25
20
15
10
5
0

80

80

70

70

60

60

50
SWaT
SMD
WADI

40
30
20

+40

+30

+20

Mem-2
No Mem-2
Mem-4
No Mem-4

+10

0

10%

20%
Missing Rate

30%

Fig. 10. The impact of memory network on the
data with 30% missing rate

F1 (%)

70

F1 (%)

F1 (%)

80

30

+90

85

F1 (%)

85

50

11

50
SWaT
SMD
WADI

40
30

2%

3%

4%

5%

6%

Artificial Missing Rate

Fig. 12. The impact of artificial missing rate on
the data with 20% missing rate

imputation and linear imputation to address missing data. The
F1 results of Ours-mean, Ours-linear, and Ours in table III to
table II indicate that simple use of mean and linear imputation
may miss some anomalies. We use -1000, mask matrix M
and missing length information T to better label missing data,
rather than assuming that the missing data is a normal value
like other imputation methods.
In table III to table II, our algorithm achieved overall
higher F1, F1-w/o PA and F1-PA%K scores than other algorithms, indicating its stronger multivariate anomaly detection
capability and better ability in handling complex missing data
with situations like attribute misplacement and concept drift.
In scenarios that include a missing rate of 10%, 20%,
30%. and 2% data misplacement between two attributes of
the original data and a single instance of concept drift, we
investigate the impact of the number of epochs on the model’s
performance. From the experimental results in Fig.2 to Fig.4,
we can observe that as the number of epochs increases, the
model’s accuracy also improves. When the model’s number of
epochs becomes excessively high, the rate of improvement in
accuracy begins to slow down.
For different datasets, we set different training sample
lengths to verify the impact of sample length on our experimental results. In low-quality datasets that include anomalies,
concept drift, attribute misplacement, and data missing, the
frequency and duration of anomalies are irregular. Sometimes,
a larger sample length helps the model identify these anomalies, while sometimes the opposite is true. We conducted
experiments on three datasets, simulating a data with different
missing rate, and compared the impact of different sample

2%

3%

4%

5%

6%

Artificial Missing Rate

Fig. 13. The impact of artificial missing rate on
the data with 30% missing rate

lengths such as 100, 200, 300, 400, and 500 on model
performance. For example, in a dataset with S around 20,
if we set the error ϵ = 0.07, Dmax = 1.9 and Dmin = 1.8
then according to our optimal window size analysis, the most
suitable window size is [215, 455].
The experimental results show that although there are cases
where the model’s F1 score is highest when the sample length
is 400. Overall, however, the model’s F1 score is highest and
performs best when the sample length is 300. The specific
comparative experimental results are shown in Fig.5 to Fig.7.
In fact, a too short sample length is not conducive to model
training, and a too long sample length will not improve training
effectiveness.
D. Ablation Study and Parameter Analysis
We conducted an ablation study on the memory network
to verify its function. The experimental results are displayed
in Fig.8 to Fig.10. ”Memo-2” indicates that the model has a
memory network and 2 attributes are misplaced. ”No Memo-2”
indicates that the model does not have a memory network and
2 attributes are misplaced. ”Memo-4” and ”No Memo-4” have
similar meanings. Without the use of a memory network, the
occurrence of misplacement can lead to model misjudgments,
thereby affecting the F1 score. What’s worse, an increase in
misplaced attributes can impact the model’s performance and
robustness.
To provide the model with reasonable feedback during
training, we artificially make missing data in the low-quality
data we set up. The proportion of this artificial missing data is
an empirical value and we attempt to conduct a guided analysis

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

12

TABLE I
P ERFORMANCE C OMPARISON UNDER C ONDITIONS OF 20% DATA M ISSING , ATTRIBUTE M ISPLACEMENT AND C ONCEPT D RIFT

Dataset
Metric(%)
DAGMM
USAD
LSTM-VAE
GDN
TimesNet
DCdetector
AERO
FluxEV
GST-Pro
USAD-mean
USAD-linear
Ours-mean
Ours-linear
Ours

F1
42.06
73.54
59.34
68.13
69.61
71.80
71.85
71.08
69.86
71.41
72.25
76.07
76.63
78.45

SWaT
F1-PA%K
38.69
69.54
55.57
64.74
66.10
68.03
68.57
67.26
66.11
67.73
68.88
73.41
73.68
76.07

F1-w/o PA
33.62
66.33
50.75
59.34
61.67
63.81
63.47
62.91
61.68
63.40
64.44
70.79
70.87
71.99

F1
57.98
65.75
77.88
53.55
76.85
80.91
69.88
76.59
77.11
66.53
66.71
80.96
81.04
82.96

SMD
F1-PA%K
54.74
61.45
74.11
50.21
73.34
77.15
66.60
72.92
73.53
62.90
63.02
77.07
76.84
78.32

F1-w/o PA
49.90
58.03
69.32
45.10
68.96
73.01
61.95
68.44
69.39
57.59
57.82
75.76
75.83
76.71

F1
13.55
20.23
22.19
14.63
28.69
29.65
25.09
28.91
29.49
21.05
21.06
31.94
31.68
33.37

WADI
F1-PA%K F1-w/o PA
10.82
10.03
16.13
12.73
18.26
13.49
9.04
1.97
24.30
18.62
25.06
20.01
21.04
15.94
24.79
18.16
25.47
20.85
17.31
12.98
17.68
12.69
29.20
26.26
29.06
27.77
31.82
27.09

TABLE II
P ERFORMANCE C OMPARISON UNDER C ONDITIONS OF 30% DATA M ISSING , ATTRIBUTE M ISPLACEMENT AND C ONCEPT D RIFT

86
85
84
83
82
81

SWaT
F1-PA%K
36.17
53.91
56.06
64.71
65.78
68.81
66.98
66.09
64.52
65.84
70.38
71.31
71.38
73.86

+86

m=3
m=4
m=5
m=6
m=7

38

+84

+82

+38

37
36
35

F1-w/o PA
31.84
49.65
52.07
60.39
61.91
63.90
63.07
62.23
61.02
61.61
66.57
69.36
70.58
71.36

+36

SWaT

SMD
Dataset

WADI

Fig. 14. The impact of the data with one attribute
drift and varying memory number

F1
56.27
62.92
74.95
39.74
74.49
78.76
67.57
74.51
74.01
64.25
65.61
78.72
78.87
80.90

SMD
F1-PA%K
53.77
59.89
72.44
37.38
71.82
76.21
65.04
71.89
71.30
61.90
62.99
75.92
75.98
78.57

89
88
87
86
85
84
83
82
39
38
37
36
35

F1-w/o PA
49.76
55.65
68.42
32.48
68.04
72.36
61.26
68.08
67.94
57.00
58.93
74.11
74.31
75.94

m=3
m=4
m=5
m=6
m=7

+88

+86

+84

+82

+38

+36

SWaT

SMD
Dataset

F1
18.86
19.07
28.09
12.45
25.78
27.31
23.26
26.09
26.58
20.20
20.86
27.85
27.73
30.34

WADI

Fig. 15. The impact of the data with two attribute
drift and varying memory number

F1 (%)

F1
38.90
56.94
58.62
66.95
68.57
71.80
69.64
68.77
67.31
68.29
73.07
74.14
74.22
76.21

F1 (%)

F1 (%)

Dataset
Metric(%)
DAGMM
USAD
LSTM-VAE
GDN
TimesNet
DCdetector
AERO
FluxEV
GST-Pro
USAD-mean
USAD-linear
Ours-mean
Ours-linear
Ours

90
89
88
87
86
85
84
83
40
39
38
37
36
35

WADI
F1-PA%K F1-w/o PA
14.44
14.25
16.49
15.11
25.32
23.41
8.47
1.82
22.92
18.56
24.29
20.01
20.38
15.71
23.14
18.16
23.61
19.89
17.64
13.35
17.70
13.80
24.75
23.17
25.76
24.45
27.82
24.23

+90

m=3
m=4
m=5
m=6
m=7

+88

+86

+84

+40

+38

+36

SWaT

SMD
Dataset

WADI

Fig. 16. The impact of the data with three attribute
drift and varying memory number

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

13

TABLE III
P ERFORMANCE C OMPARISON UNDER C ONDITIONS OF 10% DATA M ISSING , ATTRIBUTE M ISPLACEMENT AND C ONCEPT D RIFT

90
89
87
86
84
83
81

SWaT
F1-PA%K
42.41
65.72
55.27
64.55
64.29
70.44
67.49
64.30
64.58
67.19
66.17
72.90
72.95
75.84

F1-w/o PA
39.85
64.20
55.17
61.92
61.83
68.29
65.07
63.96
62.58
65.84
64.44
70.79
71.07
74.13

+90

Sim=0.3
Sim=0.4
Sim=0.5
Sim=0.6
Sim=0.7

+87

+84

+81

41
39

+39

38

F1
64.34
69.81
81.32
67.11
80.36
83.44
75.65
78.88
78.02
69.87
72.58
82.60
81.93
84.50

SMD
F1-PA%K
57.31
61.61
73.04
60.59
73.18
76.31
68.11
70.99
71.14
62.64
65.48
78.36
78.55
80.60

90
89
87
86
84
83
81

F1-w/o PA
54.84
59.28
72.92
58.20
70.39
73.90
65.58
70.47
68.99
60.34
62.67
75.76
74.93
76.71

+90

Sim=0.3
Sim=0.4
Sim=0.5
Sim=0.6
Sim=0.7

+87

+84

+81

41

SMD
Dataset

WADI

39
SWaT

SMD
Dataset

Fig. 18. The impact of model with 6 memories
and varying similarity coefficient

85.52

87.37

37.54

(2,mean)

81.27

82.73

36.56

81.38

82.19

36.21

SWaT

+84

SMD
Dataset

85

87

37.5

86

37.0

85

36.5

82.38

36.52

80.63

81.57

34.74

84

36.0

(3,mean)

82

83

35.5

(3,var)

80.76

81.44

34.53

81

82

35.0

80

81

34.5

80.27

34.25

SWaT

SMD
Dataset

WADI

83

WADI Range

80.35

SMD Range

(2,both)

79.57

WADI

Fig. 19. The impact of model with 7 memories
and varying similarity coefficient

84

(4,both)

+87

+39

WADI

(0,No)

(2,var)

+90

Sim=0.3
Sim=0.4
Sim=0.5
Sim=0.6
Sim=0.7

+39

SWaT Range

Concept Drift Configuration

Fig. 17. The impact of model with 5 memories
and varying similarity coefficient

90
89
87
86
84
83
41

39
38

SWaT

WADI
F1-PA%K F1-w/o PA
11.69
11.46
20.54
19.11
12.41
11.21
15.89
11.13
31.55
28.01
33.50
30.53
24.93
21.18
29.22
26.46
30.14
27.30
20.75
17.62
20.91
18.53
33.82
32.22
33.46
31.81
34.89
34.23

F1
12.13
21.78
13.09
19.26
33.59
35.57
26.15
31.76
32.63
22.79
22.97
36.17
35.73
37.18

F1 (%)

F1
49.54
74.03
63.59
71.53
71.97
77.87
75.23
72.69
71.96
74.86
74.09
78.58
79.23
82.13

F1 (%)

F1 (%)

Dataset
Metric(%)
DAGMM
USAD
LSTM-VAE
GDN
TimesNet
DCdetector
AERO
FluxEV
GST-Pro
USAD-mean
USAD-linear
Ours-mean
Ours-linear
Ours

Fig. 20. Concept drift impact on anomaly detection performance.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

14

(a) Raw data with three attributes and anomaly detection results

(b) Raw data curves, reconstructed curves and corresponding anomaly detection F1 scores from three attributes.
Fig. 21. Visualization of output from the proposed algorithm ADAT.

of it. The experiments are conducted on the low-quality
dataset set up above, which includes anomalies, concept drift,
attribute misplacement, and data missing. The data missing
rates are still 10%, 20%, and 30%, respectively. Fig.11 to
Fig.13 indicate that when the proportion of artificial missing
data is low, such as 2% and 3%, the impact on the model’s
performance is limited. As the proportion of artificial missing
data increases, the model’s performance declines. The decline
in model performance becomes more pronounced when the
data itself has a higher missing rate. An increasing amount of
missing data makes it more difficult for the model to accurately
capture the relationships between attributes during the training
phase.
We investigate the impact of the number of memories and
the similarity coefficient on model performance. Additionally,
we validate the model’s capability in handling concept drift.
The similarity threshold for the memories is set to 0.6. Under
this configuration, we examine the effect of varying the number of memories from 3 to 7 on the F1 score. The experimental

results, depicted in Fig.14 to Fig.16, demonstrate that as the
number of memories increases, the F1 score achieved by our
algorithm also rises, indicating improved model performance.
Furthermore, an increase in drifting attributes enhances the
model’s performance, as a greater number of drifting attributes
more effectively substantiates the occurrence of concept drift,
thereby reducing the false positive (FP) rate.
Since the number of memories significantly influences the
model’s performance, we fine-tuned the similarity coefficient
threshold of the memories to regulate their quantity. We
fixed the number of drifting attributes to 3. Under this
data configuration, we investigated the effect of varying the
similarity coefficient threshold from 0.3 to 0.7 on the F1
score. The experimental results are presented in Fig.17 to
Fig.19. As the similarity coefficient threshold increased, the
model’s performance exhibited consistent improvement. A
higher similarity coefficient threshold facilitates the merging
of highly similar memories, ensuring that each memory retains
distinct information. This optimization enhances the model’s

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

ability to accurately detect anomalies in the data.
To verify the capability of our algorithm in handling concept
drift, we designed an experiment incorporating multiple drifts
and two types of drift scenarios. Based on a test set with a
default configuration of 10% missing data and a misplacement
ratio of 2% for two attributes, we introduced 2 to 4 drifts in
two attributes of the test data, covering both mean and variance
drift scenarios. The experimental results are shown in Fig.20.
The X-axis represents the datasets, while the Y-axis denotes
the configuration type and number of data drifts. The format
for data drift configuration is (Number of concept drifts, Drift
type). For example, (2, both) indicates that each attribute
undergoes two concept drifts, including both mean drift and
variance drift. The (0, No) indicates no drift occurrence.
The experimental results demonstrate that, compared to the
test outcomes with only a single drift instance presented in
table III to table II, an increase in the number of drifts leads
to a certain degree of performance degradation in our algorithm. However, the rate of degradation slows down, and the
extent of the decline remains limited. On the SWaT, SMD, and
WADI datasets, the maximum performance degradation rates
compared to scenarios without drift are 6.96%, 8.13%, and
8.76%, respectively. Furthermore, the impact of the two drift
types on model performance varies across datasets, indicating
that no single drift type consistently causes more significant
performance deterioration.

E. Visual results analysis
In Fig.21, we visualize the prediction results of our algorithm on multivariate time series data containing both point
anomalies and sequential anomalies. A segment with 4300
timestamps of the SMD test data including attribute 1, 2, and
3 is selected for visualization. In Fig.21(a), data issues such
as data missing(yellow region), attribute misplacement(orange
region), and concept drift(pink region) are each introduced
twice in this segment. The green region indicates the groundtruth anomalies. Attribute misplacement occurs in attribute 1
and attribute 2. Other issues occur simultaneously in attribute
1, 2, and 3. We maintain the original values of other attribute
data and use all attributes for model testing.
In Fig.21(b), the light blue region represents the detected
anomalies. The blue, black, and purple raw data curves from
three different attributes are each placed together with their
corresponding red reconstructed curves. Below each attribute’s
raw data curve, the pink curve represents the anomaly score,
and the dashed line indicates the anomaly threshold. Although
we add different types of data issues to these three attributes in
the raw data, the results show that our algorithm, by integrating
data from other attributes, remains unaffected and successfully
detects the true anomalies. In the anomaly detection of the
third attribute, we do not find the first anomaly. However, after
incorporating the detection results from the other attributes,
this anomaly is ultimately not missed. Our model captures the
spatiotemporal relationships across different attributes, rather
than relying solely on a single or a few attributes.

15

VII. C ONCLUSION
To tackle multivariate time series which includes datasets
with missing data, attribute misplacement and concept drift,
we propose an unsupervised anomaly detection framework. we
propose a self-attention mechanism that incorporates masking
and missing length information, thereby enhancing the model’s
capacity to manage incomplete data effectively. Besides,
we propose a memory mechanism that leverages similarityweighted items to obtain a reconstruction representation, correcting biases induced by attribute misplacement during the
reconstruction process. Our experimental results demonstrate
that our method outperforms other baseline algorithms in F1
Score when dealing with low-uality multivariate time series
data.
R EFERENCES
[1] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A survey,”
ACM computing surveys (CSUR), vol. 41, no. 3, pp. 1–58, 2009.
[2] E. Keogh, J. Lin, and A. Fu, “Hot sax: Efficiently finding the most unusual
time series subsequence,” in Fifth IEEE International Conference on Data
Mining (ICDM’05). Ieee, 2005, pp. 8–pp.
[3] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “Lof: identifying
density-based local outliers,” in Proceedings of the 2000 ACM SIGMOD
international conference on Management of data, 2000, pp. 93–104.
[4] S. Guha, N. Mishra, G. Roy, and O. Schrijvers, “Robust random cut
forest based anomaly detection on streams,” in International conference
on machine learning. PMLR, 2016, pp. 2712–2721.
[5] Y. Zheng, H. Y. Koh, M. Jin, L. Chi, H. Wang, K. T. Phan, Y.-P. P. Chen,
S. Pan, and W. Xiang, “Graph spatiotemporal process for multivariate
time series anomaly detection with missing values,” Information Fusion,
vol. 106, p. 102255, 2024.
[6] G. Pang, C. Shen, L. Cao, and A. V. D. Hengel, “Deep learning for
anomaly detection: A review,” ACM computing surveys (CSUR), vol. 54,
no. 2, pp. 1–38, 2021.
[7] Y. Zhang, B. Zhou, X. Cai, W. Guo, X. Ding, and X. Yuan, “Missing
value imputation in multivariate time series with end-to-end generative
adversarial networks,” Information Sciences, vol. 551, pp. 67–82, 2021.
[8] B. Yang, W. Long, Y. Zhang, Z. Xi, J. Jiao, and Y. Li, “Multivariate time
series anomaly detection: Missing data handling and feature collaborative
analysis in robot joint data,” Journal of Manufacturing Systems, vol. 75,
pp. 132–149, 2024.
[9] H. Xu, W. Chen, N. Zhao, Z. Li, J. Bu, Z. Li, Y. Liu, Y. Zhao, D. Pei,
Y. Feng et al., “Unsupervised anomaly detection via variational autoencoder for seasonal kpis in web applications,” in Proceedings of the
2018 world wide web conference, 2018, pp. 187–196.
[10] J. Li, S. Di, Y. Shen, and L. Chen, “Fluxev: a fast and effective unsupervised framework for time-series anomaly detection,” in Proceedings of
the 14th ACM International Conference on Web Search and Data Mining,
2021, pp. 824–832.
[11] Y. Sun, S. Song, C. Wang, and J. Wang, “Swapping repair for misplaced
attribute values,” in 2020 IEEE 36th International Conference on Data
Engineering (ICDE). IEEE, 2020, pp. 721–732.
[12] G. J. van den Burg, A. Nazábal, and C. Sutton, “Wrangling messy csv
files by detecting row and type patterns,” Data Mining and Knowledge
Discovery, vol. 33, no. 6, pp. 1799–1820, 2019.
[13] A. Blázquez-Garcı́a, A. Conde, U. Mori, and J. A. Lozano, “A review on
outlier/anomaly detection in time series data,” ACM computing surveys
(CSUR), vol. 54, no. 3, pp. 1–33, 2021.
[14] K.-H. Le and P. Papotti, “User-driven error detection for time series
with events,” in 2020 IEEE 36th International Conference on Data
Engineering (ICDE). IEEE, 2020, pp. 745–757.
[15] A. A. Cook, G. Mısırlı, and Z. Fan, “Anomaly detection for iot timeseries data: A survey,” IEEE Internet of Things Journal, vol. 7, no. 7, pp.
6481–6494, 2019.
[16] S. Aminikhanghahi and D. J. Cook, “A survey of methods for time series
change point detection,” Knowledge and information systems, vol. 51,
no. 2, pp. 339–367, 2017.
[17] A. Siffer, P.-A. Fouque, A. Termier, and C. Largouet, “Anomaly detection in streams with extreme value theory,” in Proceedings of the 23rd
ACM SIGKDD international conference on knowledge discovery and data
mining, 2017, pp. 1067–1075.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

[18] M. Ma, S. Zhang, D. Pei, X. Huang, and H. Dai, “Robust and rapid
adaption for concept drift in software system anomaly detection,” in 2018
IEEE 29th International Symposium on Software Reliability Engineering
(ISSRE). IEEE, 2018, pp. 13–24.
[19] S. Saurav, P. Malhotra, V. TV, N. Gugulothu, L. Vig, P. Agarwal,
and G. Shroff, “Online anomaly detection with concept drift adaptation
using recurrent neural networks,” in Proceedings of the acm india joint
international conference on data science and management of data, 2018,
pp. 78–87.
[20] S. Bhatia, A. Jain, S. Srivastava, K. Kawaguchi, and B. Hooi, “Memstream: Memory-based streaming anomaly detection,” in Proceedings of
the ACM Web Conference 2022, 2022, pp. 610–621.
[21] Z. Zamanzadeh Darban, G. I. Webb, S. Pan, C. Aggarwal, and M. Salehi,
“Deep learning for time series anomaly detection: A survey,” ACM
Computing Surveys, vol. 57, no. 1, pp. 1–42, 2024.
[22] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“Usad: Unsupervised anomaly detection on multivariate time series,”
in Proceedings of the 26th ACM SIGKDD international conference on
knowledge discovery & data mining, 2020, pp. 3395–3404.
[23] D. Li, D. Chen, B. Jin, L. Shi, J. Goh, and S.-K. Ng, “Mad-gan:
Multivariate anomaly detection for time series data with generative
adversarial networks,” in International conference on artificial neural
networks. Springer, 2019, pp. 703–716.
[24] C. Zhang, D. Song, Y. Chen, X. Feng, C. Lumezanu, W. Cheng, J. Ni,
B. Zong, H. Chen, and N. V. Chawla, “A deep neural network for
unsupervised anomaly detection and diagnosis in multivariate time series
data,” in Proceedings of the AAAI conference on artificial intelligence,
vol. 33, no. 01, 2019, pp. 1409–1416.
[25] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proceedings of the 25th ACM SIGKDD international conference on knowledge discovery & data mining, 2019, pp. 2828–2837.
[26] Z. Li, Y. Zhao, J. Han, Y. Su, R. Jiao, X. Wen, and D. Pei, “Multivariate
time series anomaly detection and interpretation using hierarchical intermetric and temporal embedding,” in Proceedings of the 27th ACM
SIGKDD conference on knowledge discovery & data mining, 2021, pp.
3220–3230.
[27] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom, “Detecting spacecraft anomalies using lstms and nonparametric
dynamic thresholding,” in Proceedings of the 24th ACM SIGKDD international conference on knowledge discovery & data mining, 2018, pp.
387–395.
[28] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proceedings of the AAAI conference on
artificial intelligence, vol. 35, no. 5, 2021, pp. 4027–4035.
[29] Z. Chen, D. Chen, X. Zhang, Z. Yuan, and X. Cheng, “Learning graph
structures with transformer for multivariate time-series anomaly detection
in iot,” IEEE Internet of Things Journal, vol. 9, no. 12, pp. 9179–9189,
2021.
[30] H. Zhao, Y. Wang, J. Duan, C. Huang, D. Cao, Y. Tong, B. Xu, J. Bai,
J. Tong, and Q. Zhang, “Multivariate time-series anomaly detection via
graph attention network,” in 2020 IEEE international conference on data
mining (ICDM). IEEE, 2020, pp. 841–850.
[31] Y. Zhang, Y. Chen, J. Wang, and Z. Pan, “Unsupervised deep anomaly
detection for multi-sensor time-series signals,” IEEE Transactions on
Knowledge and Data Engineering, vol. 35, no. 2, pp. 2118–2132, 2021.
[32] B. Zong, Q. Song, M. R. Min, W. Cheng, C. Lumezanu, D. Cho, and
H. Chen, “Deep autoencoding gaussian mixture model for unsupervised
anomaly detection,” in International conference on learning representations, 2018.
[33] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time
series anomaly detection with association discrepancy,” in The Tenth
International Conference on Learning Representations, ICLR, 2022.
[34] J. Yang, Z. Yue, and Y. Yuan, “Deep probabilistic graphical modeling
for robust multivariate time series anomaly detection with missing data,”
Reliability Engineering & System Safety, vol. 238, p. 109410, 2023.
[35] Y. Liu, K. Zhao, G. Cong, and Z. Bao, “Online anomalous trajectory
detection with deep generative sequence modeling,” in 2020 IEEE 36th
International Conference on Data Engineering (ICDE). IEEE, 2020, pp.
949–960.
[36] L. Wang, J. Tian, S. Zhou, H. Shi, and G. Hua, “Memory-augmented
appearance-motion network for video anomaly detection,” Pattern Recognition, vol. 138, p. 109335, 2023.
[37] D. Gong, L. Liu, V. Le, B. Saha, M. R. Mansour, S. Venkatesh, and
A. v. d. Hengel, “Memorizing normality to detect anomaly: Memoryaugmented deep autoencoder for unsupervised anomaly detection,” in

16

Proceedings of the IEEE/CVF international conference on computer
vision, 2019, pp. 1705–1714.
[38] S. Yoon, Y. Lee, J.-G. Lee, and B. S. Lee, “Adaptive model pooling for
online deep anomaly detection from a complex evolving data stream,”
in Proceedings of the 28th ACM SIGKDD Conference on Knowledge
Discovery and Data Mining, 2022, pp. 2347–2357.
[39] I. Frias-Blanco, J. del Campo-Ávila, G. Ramos-Jimenez, R. MoralesBueno, A. Ortiz-Diaz, and Y. Caballero-Mota, “Online and nonparametric drift detection methods based on hoeffding’s bounds,” IEEE
Transactions on Knowledge and Data Engineering, vol. 27, no. 3, pp.
810–823, 2014.
[40] J. Pickands III, “Statistical inference using extreme order statistics,” the
Annals of Statistics, pp. 119–131, 1975.
[41] B. Zong, Q. Song, M. R. Min, W. Cheng, C. Lumezanu, D. Cho, and
H. Chen, “Deep autoencoding gaussian mixture model for unsupervised
anomaly detection,” in 6th International Conference on Learning Representations, ICLR 2018, Vancouver, BC, Canada, April 30 - May 3, 2018,
Conference Track Proceedings. OpenReview.net, 2018.
[42] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly detector
for robot-assisted feeding using an lstm-based variational autoencoder,”
IEEE Robotics Autom. Lett., vol. 3, no. 2, pp. 1544–1551, 2018.
[43] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Thirty-Fifth AAAI Conference on Artificial
Intelligence, AAAI 2021, Thirty-Third Conference on Innovative Applications of Artificial Intelligence, IAAI 2021, The Eleventh Symposium on
Educational Advances in Artificial Intelligence, EAAI 2021, Virtual Event,
February 2-9, 2021. AAAI Press, 2021, pp. 4027–4035.
[44] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: unsupervised anomaly detection on multivariate time series,” in
KDD ’20: The 26th ACM SIGKDD Conference on Knowledge Discovery
and Data Mining, Virtual Event, CA, USA, August 23-27, 2020, R. Gupta,
Y. Liu, J. Tang, and B. A. Prakash, Eds. ACM, 2020, pp. 3395–3404.
[45] H. Wu, T. Hu, Y. Liu, H. Zhou, J. Wang, and M. Long, “Timesnet:
Temporal 2d-variation modeling for general time series analysis,” in The
Eleventh International Conference on Learning Representations, ICLR
2023, Kigali, Rwanda, May 1-5, 2023. OpenReview.net, 2023.
[46] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “Dcdetector: Dual
attention contrastive representation learning for time series anomaly
detection,” in Proceedings of the 29th ACM SIGKDD Conference on
Knowledge Discovery and Data Mining, KDD 2023, Long Beach, CA,
USA, August 6-10, 2023, A. K. Singh, Y. Sun, L. Akoglu, D. Gunopulos,
X. Yan, R. Kumar, F. Ozcan, and J. Ye, Eds. ACM, 2023, pp. 3033–3045.
[47] X. Hao, Y. Chen, C. Yang, Z. Du, C. Ma, C. Wu, and X. Meng,
“From chaos to clarity: Time series anomaly detection in astronomical
observations,” in 2024 IEEE 40th International Conference on Data
Engineering (ICDE), 2024.
[48] S. Yoon, Y. Lee, J.-G. Lee, and B. S. Lee, “Adaptive model pooling for
online deep anomaly detection from a complex evolving data stream,”
in Proc. of the 28th ACM SIGKDD Conf. on Knowledge Discovery and
Data Mining (KDD), Washington, DC, USA, Aug. 2022, pp. 2347–2357.
[49] S. Kim, K. Choi, H.-S. Choi, B. Lee, and S. Yoon, “Towards a rigorous
evaluation of time-series anomaly detection,” in Proc. of the 36th AAAI
Conf. on Artificial Intelligence, vol. 36, no. 7, 2022, pp. 7194–7201.
[50] J. Liu, Q. Li, S. An, B. Ezard, and L. Li, “EdgeConvFormer: An
unsupervised anomaly detection method for multivariate time series,” in
International Conference on Pattern Recognition, pp. 367–382, Springer,
2024.
[51] J. Liu, Q. Li, L. Li, and S. An, “Structural damage detection and
localization via an unsupervised anomaly detection method,” Reliability
Engineering & System Safety, vol. 252, p. 110465, Elsevier, 2024.
[52] C. Pan, L. Su, L. Xiong, J. Yang, and F. Li, “CT-DDPM: anomaly
detection of multivariate time series with copula and transformer-based
denoising diffusion probabilistic models,” Information Sciences, vol. 717,
p. 122279, 2025.
[53] L. Su, Q. Li, J. Quan, and F. Li, “Enhanced recurrent convolutional
encoding with attention-based representation learning for chaotic time
series anomaly detection,” Physica Scripta, vol. 100, no. 11, p. 115215,
2025.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Knowledge and Data Engineering. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TKDE.2026.3700672

JOURNAL OF LATEX CLASS FILES, VOL. 14, NO. 8, AUGUST 2021

Jiayi Liu is currently working toward the PhD
degree with the Harbin Institute of Technology. Her
research interests include machine learning and data
anomaly detection.

Donghua Yang received the BS, MS and PhD
degrees from the School of Computer Science and
Technology, Harbin Institute of Technology, Harbin,
China,in 1999, 2003,and 2008, respectively. He is
currently an associate professor with the School of
Computer Science and Technology,Harbin Institute
of Technology. His research interests include Big
Data management and cloud computing.

Jinbao Wang received the BS,MS,PhD degrees
from the School of Computer Science and Technology, Harbin Institute of Technology. He is currently
an associate professor with the School of Computer
Science and Technology, Harbin Institute of Technology of China. His research interests include focus
on Big Data analytic and data privacy.

Hong Gao received the BS degree from Heilongjiang University, the MS degree from Harbin
Engineering University, and the PhD degree from
the Harbin Institute of Technology. She is currently
a distinguished professor with the School of Computer Science and Technology, Zhejiang Normal
University. Her research interests include database
systems, graph data analysis, time series data analysis, IOT data collection, and edge computing. She
has received the National Science and Technology
Progress Award.
Jianzhong Li is a professor with the Department
of Computing, Harbin Institute of Technology. He
worked with the Department of Computer Science,
Lawrence Berkeley National Laboratory, as a scientist, from 1986 to 1987 and from 1992 to 1993. He
was also a visiting professor with the University of
Minnesota at Minneapolis, Minnesota. His research
interests include massive data intensive computing
and wireless sensor networks. He has published
more than 200 papers in refereed journals and conference proceedings, such as the VLDB Journal,
Algorithmica, IEEE Transactions on Knowledge and Data Engineering, SIGMOD, SIGKDD, VLDB, ICDE, and INFOCOM.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

17
PAPER_TEXT
