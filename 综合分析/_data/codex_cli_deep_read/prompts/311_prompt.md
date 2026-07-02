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
# [311] Time Series Anomaly Detection in Vehicle Sensors Using Self-Attention Mechanisms
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
编号：311
题名：Time Series Anomaly Detection in Vehicle Sensors Using Self-Attention Mechanisms
年份：2024
DOI：10.1109/tits.2024.3415435
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2024.3415435.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\311.txt
- 原始字符数：61926
- 本次发送字符数：61926
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
15964

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 11, NOVEMBER 2024

Time Series Anomaly Detection in Vehicle Sensors
Using Self-Attention Mechanisms
Ze Zhang , Yue Yao , Windo Hutabarat, Michael Farnsworth , Divya Tiwari , and Ashutosh Tiwari

Abstract— Connected autonomous vehicles (CAVs) offer significant enhancements in coordinated traffic and safety through
real-time vehicle-to-vehicle or vehicle-to-infrastructure communications, establishing them as a potent tool for augmenting driving
tasks. However, the extensive information-sharing framework
inherent in CAVs amplifies the risk associated with sensor
anomalies, posing challenges to the reliability and security of the
system. Responding to this timely research challenge, this study
proposes a novel anomaly detection method, namely Dual-channel
Self-attention-based Convolutional Neural Network (DSA-CNN)
for multivariate time series data. Through the introduction of the
Dual-channel Self-attention Mechanism, DSA-CNN can progressively and autonomously extract spatiotemporal features from
multivariate time series data. The proposed method was tested
under a variety of common threatening sensor anomaly patterns
of CAVs summarised in the literature, and evaluated under
multiple different performance metrics. The results demonstrate
its advantages in detecting minor anomalies and enhancing
sensitivity, outperforming previously reported methods in the
literature. Across all experimental scenarios, an average sensitivity improvement of 2.53% was observed, complemented by an
average F1 score increase of 1.47%. In CAV settings, maintaining
high sensitivity to ensure fewer undetected anomalies, alongside
the ability to detect small anomalies, can be more important for
the robustness and safety measures of CAV systems.
Index Terms— Anomaly detection, connected and autonomous
vehicles (CAVs), deep learning, attention mechanism, multisensor system, intelligent transportation system (ITS).

I. I NTRODUCTION

C

ONNECTED and Automated Vehicles (CAVs), reflecting
a convergence of automation and connectivity advancements, are receiving a surge in interest from academia,
industry, and governments. For example, the CAVs are anticipated by the UK government to create a multi-billion pound
industry [1] and ranked top 10 in KPMG’s Autonomous Vehicles Readiness Index 2020 [2]. The center of this paradigm
can be the incorporation of a variety of technologies, such as
Manuscript received 2 June 2023; revised 11 November 2023 and 24 March
2024; accepted 20 May 2024. Date of publication 2 September 2024; date
of current version 1 November 2024. This work was supported in part by
the Engineering and Physical Sciences Research Council (EPSRC) through
the Made Smarter Innovation–Research Centre for Connected Factories under
Grant EP/V062123/1, and in part by the Royal Academy of Engineering
(RAEng) and Airbus under the Research Chairs and Senior Research Fellowships Scheme under Grant RCSRF1718/5/41. The Associate Editor for
this article was F. Xia. (Corresponding author: Ze Zhang.)
The authors are with the Department of Automatic Control and
Systems Engineering, The University of Sheffield, S1 3JD Sheffield, U.K.
(e-mail: ze.zhang@sheffield.ac.uk; yue.yao@sheffield.ac.uk; w.hutabarat@
sheffield.ac.uk; m.j.farnsworth@sheffield.ac.uk; d.tiwari@sheffield.ac.uk;
a.tiwari@sheffield.ac.uk).
Digital Object Identifier 10.1109/TITS.2024.3415435

advanced sensors, vehicle-to-vehicle (V2V) communications,
vehicle-to-infrastructure (V2I) communications, and Artificial
Intelligence (AI) for autonomous navigation and decisionmaking [3]. By leveraging connectivity, real-time traffic
information such as changing road conditions, unforeseen
events, and safety warnings can be shared among vehicles,
enabling the global optimisation of traffic flow, reduced
congestion, and enhanced road safety [4], [5]. Therefore,
compared with conventional autonomous vehicles, CAVs offer
considerable advantages to the future of transportation.
Due to the extensive information-sharing framework inherent in CAVs, the reliability of sensors, which can be
intrinsically tied to the safety and security of CAVs, has
emerged as a matter of concern in recent years [2]. However,
given a large amount of data transmission [6], cyber-attacks,
and the highly complex operating environment of the vehicles,
sensor anomalies which refer to where sensor readings fail
to accurately represent the actual physical processes they are
monitoring can be difficult to avoid and pose a significant
threat to the core functions of CAVs, such as autopilot control
system and traffic coordination [6]. As a result, sensor anomaly
detection for CAVs has become a research focus in recent
years.
The aim of sensor anomaly detection is to identify the readings that deviate from the expected values, which can result
from many reasons, such as sensor malfunction and cyberattacks [7]. By doing so, timely intervention can be enabled
to avoid potentially severe consequences. Anomaly detection
has been extensively researched in the literature and commonly used methods include, but are not limited to, statistical
methods, signal processing, time series analysis (TSA), and
data-driven methods, especially deep learning. In a statistical
method, sensor data can be modelled by a statistical model and
readings that deviate from the model prediction can be considered anomalous according to a pre-defined threshold [8]. The
statistical models for this type of method can either be built
from domain knowledge or statistically derived from the data
collected, such as the Gaussian model [9], histogram-based
model [10], or Hypothesis testing method [11]. Generally
speaking, most of them can be interpretable and computationally efficient. However, this type of method requires that
the sensor data can be characterised by a specific distribution,
which may not be the case for many applications, especially
for data of high dimensionality [12]. Signal processing-based
anomaly detection, such as the Fourier transform and the
wavelet transform is another commonly used method, which
can be used for a variety of sensor data, such as acoustic,

© 2024 The Authors. This work is licensed under a Creative Commons Attribution 4.0 License.
For more information, see https://creativecommons.org/licenses/by/4.0/

ZHANG et al.: TIME SERIES ANOMALY DETECTION IN VEHICLE SENSORS

vision, and physical parameters data. In [13], a wavelet-based
method was proposed to detect anomalies in the presence of
noise, and they achieved remarkable performance with respect
to detection rate and computational efficiency. As signal
processing methods attempt to form unique descriptions of
different signals, they often have an advantage when dealing with unseen anomalies. However, similar to statistical
methods, their performance may heavily depend on making
assumptions (e.g. quasi-stationarity) to processes such as noise
distribution, which may limit their applications [12]. In terms
of time-series analysis-based anomaly detection, it can also be
a prevailing methodology [14], such as Kalman filtering [15],
autoregressive moving average [16], symbolic TSA [17]. However, according to [12], this type of method may suffer from
degrading performance when the anomaly causes dramatic
changes to the original sensor readings.
Deep learning as a promising option for sensor anomaly
detection has received more attention recently, particularly
in scenarios where there are large amounts of data with
complex patterns and high dimensionality [18], [19]. This is
because deep learning methods typically can learn feature
representations of the data that contain complex patterns
and dependencies automatically. Compared with conventional
methods, deep learning-based methods normally do not require
any assumptions on the distribution of input data or noise,
making it applicable in most areas with a certain amount of
data. Convolutional Neural Network (CNN) can be one of
the most commonly used methods and it has been shown to
be effective in sensor anomaly detection [20], especially for
multivariate inputs. For example, in [21], Chen et al. proposed
a CNN-based anomaly detection algorithm for multiple sensor
streams. However, CNN can be limited in its ability to model
global features due to its reliance on a large number of local
kernels to extract features, resulting in difficulty in capturing
long-range dependencies, such as inter-sensor dependencies
and time dependencies. The above shortcomings of CNNs
can be well compensated by the Recurrent Neural Networks
(RNNs), which model time dependence through a recurrent
structure. The Long Short-Term Memory (LSTM) can be one
of the representative RNNs. In [22], LSTM and CNN were
combined to detect sensor anomalies for CAVs. They achieved
a state-of-the-art performance on a public CAV dataset. However, since LSTM can be an RNN structure, despite the
advantage over CNNs of introducing time-dependent modelling, the vanishing gradient may be non-negligible, which
inherently limits its ability to retain information over long
sequences [23], resulting in small anomalies in the time series
being difficult to detect. Therefore, this work proposes a Dualchannel Self-attention-based CNN (DSA-CNN) to mitigate
the limitations of both CNNs and RNNs in sensor anomaly
detection, aiming to enhance the detection of small anomalies
and reduce the incidence of undetected faults.
Transformer architectures have shown great potential for
anomaly detection [24], [25]. In the self-attention mechanism
of the Transformer method, data from all time points can be
processed in parallel, instead of the recurrent computation in
RNNs, making it significantly better than RNNs in capturing long-range dependence without suffering from vanishing

15965

gradient problem [26], [27]. Due to the advantages of CNN
in local feature extraction, our proposed DSA-CNN combines
two different deep learning building blocks, self-attention, and
CNN, to improve its performance for anomaly detection in
multi-sensor time series, especially for small anomalies. The
main contributions can be summarised as follows:
• A new method, the DSA-CNN, has been developed,
incorporating the self-attention mechanism specifically
for detecting anomalies in multivariate time series sensor
data. This model effectively identifies anomalous readings
within the sensor data streams over a given time window.
• In our proposed method, the spatiotemporal features
which can be vital for anomaly detection [28] can be
extracted and integrated progressively and automatically
with the help of separate attention channels during the
learning process, eliminating the artificial signal processing stage for extracting the spatiotemporal features before
designing an anomaly detection algorithm.
• This study has achieved a notable incremental improvement in performance compared to existing methods
applied to the dataset used by this study. The experiment
results show that our proposed DSA-CNN has a clear
advantage in handling small anomalies, and improves
the sensitivity significantly among all the experimental
conditions being evaluated. This means our proposed
method has fewer undetected anomalies which can be
harmful in real systems compared with the other methods
in the literature.
The rest of the paper is organised as follows. Section II
formulates the problem being worked on and describes the
dataset being used in this paper. Section III provides the details
of our methodology, including the model architecture design
and computation flow. Section IV provides the experiment
settings and results comparison of the proposed method.
A comprehensive discussion as well as the drawbacks of the
proposed method can be found in Section V before Section VI
where the conclusion is presented.
II. P ROBLEM S TATEMENT AND DATASET D ESCRIPTION
The concept of sensor anomaly refers to the situation in
which sensor readings deviate from their expected values by
producing faulty data and failing to reflect the actual physical
processes, causing potential errors in decisions that depend
on these readings. Addressing sensor anomaly, as a subset of
Corner Cases, can be a necessary part of the consideration
in the design of autonomous systems [29]. This work focuses
on developing a supervised learning-based method to identify
anomalous data in multi-sensor time-series signals to avoid
serious consequences. The output of our proposed model can
be the anomaly conditions of the current time window, hence
we formulated the anomaly detection problem as a multivariate time series classification (TSC) problem. According
to [30], [31], [32], and [33], in CAV settings, the commonly
observed sensor abnormal patterns caused by cyber-attacks
and sensor malfunctions can be summarised by the 4 types,
namely Instant, Constant, Gradual drift, and Bias. A detailed
description of the above-mentioned patterns in CAVs can be
found in [15].

15966

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 11, NOVEMBER 2024

Fig. 1.

Algorithm 1 Anomaly Injection
t ← time step
T ← total number of data points
p ← anomaly possibility
i ← sensor index
n ← number of sensors
xi ← sensor data
x i ′ ← sensor anomaly # A full description of the anomaly
patterns can be found in [15] and [22]
for t ∈ T do
if a ∼ U (0, 1) ≤ p then
i ← randint (n)
x i ′ ← xi + Anomaly
else
x i ′ ← xi
end if
end for

Snippet of the raw data.

In order to maintain comparability, the CAVs dataset used
in [15] and [22] was employed. This dataset was provided
by the Safety Pilot Model Deployment (SPMD) program as
reported in [34] and can be found in their research data
exchange (RDE) database [35]. This dataset was composed
of a variety of information generated during the driving
process of vehicles, including the Basic Safety Messages
(BSM), driving trajectories, driver-vehicle interaction data,
and environmental information, collected by the onboard Data
Acquisition System (DAS), Global Positioning System (GPS),
and roadside units. To keep consistent with [15] and [22],
in this work, we employed three sensors to evaluate our proposed sensor anomaly detection method, namely, (1) Sensor 1:
speed measured on the vehicle, (2) Sensor 2: speed given by
GPS, and (3) Sensor 3: in-vehicle acceleration. A snippet of
the raw sensor data is shown in Figrue 1.
It is important to mention here that, in this work, no information about driving control, road conditions, environment,
trajectory, or car dynamics was employed, and the external
environment of driving was not controlled. Given that a car’s
driving decisions can be influenced by numerous factors such
as traffic conditions, driving behavior, weather conditions, road
quality, and legal speed limits, it is highly likely that the
statistical properties of the speed of a car will vary over time,
making it a non-stationary process which can be expressed by
the following equation:


yt = yt−1 + ut , ut ∼ IID 0, σ 2
(1)
where yt denotes the speed at time t, IID means independent
and identically distributed.
Since this dataset did not provide anomalous sensor data,
to keep consistent with [15] and [22], the anomaly injection
algorithm was kept the same as theirs as shown in Algorithm 1.
Four common sensor anomalies caused by cyber-attacks and
sensor failures were injected in this work, namely instant,
constant, gradual drift, and bias. As stated in [15] and [22],
in a practical system, the probability of two sensors being
abnormal at the same time can be very low due to the high
reliability of the sensors, so we assume that only one sensor
can be abnormal at the same time point.
It is important to note here that, in this study, no data
normalization operations were employed. This is because,
firstly, if sensor anomalies were injected after normalisation,
those severe outliers would be significantly different from the
normal values and thus make the task less difficult. Secondly,
if the data were normalised after anomaly injection, the severe
outliers would cause the variance of the original data to

become extremely small, thus increasing the demand for the
precision of the data processed by the model and resulting in
an unnecessary computational burden.
III. M ETHODOLOGY
In this section, an introduction to the overall model architecture of DSA-CNN is provided along with a detailed
explanation of the two fundamental building blocks of DSACNN, namely DAM block and CNN block. This is followed by
an explanation of how the DAM block extracts and integrates
the temporal patterns (time-wise attention) and spatial patterns
(sensor-wise attention) based on the self-attention mechanism.
A. Overall Architecture of DSA-CNN
The overall architecture can be described by Figure 2. The
multiple sensor time series data will be first passed into the
class token concatenation function, which will be explained in
detail in a later section, to add a class token that will be used
as the feature representation for classification. Then, the output
of class token concatenation can be fed to the Dual-channel
attention mechanism (DAM) block to generate the feature
maps of the attention mechanism, followed by a CNN block
to further extract features. The DAM block and CNN block
will be repeated several times before using a linear layer to
perform the final classification. The output of this model can
be the anomaly conditions of the data being passed to this
model.
In terms of the input, let X denote the multiple sensor
streams as shown in the following expression:
X = [X 1 , X 2 , . . . , X C ]

(2)

where X C denotes the C-th sensor data stream. Each sensor
stream can be composed of a series of readings over a
predefined time window as shown in the following equation:
X C = [x1 , x2 , . . . , x L ]

(3)

where L is the number of readings in a time window. Hence
the input space of the model can be expressed by X ∈ RC×L .

ZHANG et al.: TIME SERIES ANOMALY DETECTION IN VEHICLE SENSORS

Fig. 2. Architecture of dual-channel self-attention-based convolutional neural
network (DSA-CNN) for sensor anomaly detection.

15967

In the proposed CNN blocks, the dimensionality of the
output feature map can be kept equal to the dimensionality of
the input data to maintain extensibility. This can be achieved
by: (1) organising the number of output channels of the
second convolutional layer to be equal to the number of input
channels of the first convolutional layer, (2) configuring the
convolutional kernels to 3 in size with a stride of 1 and padding
of 1. This means the length of input and output can be kept
the same as shown in the following equation:
L out =

Fig. 3.

CNN block.

B. CNN Block
The proposed CNN Blocks employ 1d-CNN as a basic
building element, and the architecture can be demonstrated
by Figure 3. As shown in Figure 3, the inputs can be first
processed by a 1d-CNN layer and fed into a ReLU activation
layer, before passing to the second 1d-CNN layer. Then, after
the dropout operation, the original inputs can be added to
the current feature maps via a shortcut connection. Finally,
a normalisation layer is employed to form the final feature
maps. The computation flow can be described by the following
equation:
OutC N N = LN(Dropout(Conv2(ReLU(Conv1 (X )))) + X )
(4)
where L N denotes the Layer normalisation, Conv1() and
Conv1() are the convolution operation, ReLU () is the activation function, X is the input multiple sensor time series.
1) 1d-CNN: CNNs have been proven effective and achieved
some of the state-of-the-art results for TSC among data-driven
methods in literature [36], [37]. This is because the sensitivity
of CNNs to local features can be higher and their feature
learning can be spatial invariant, compared with ANNs that
treat all features equally [38]. In this study, 1d-CNN was
used instead of the normal CNNs with two-dimensional convolutional kernels. This is because the attention mechanism
was relied on to model the spatial dependencies, CNNs were
only expected to focus on a single series. For using 1dCNN to TSC, the kernel size can be a key factor affecting
performance [39]. Most of the works using 1d-CNN regarded
the kernel size as a hyper-parameter and optimised it by
grid search which can be time-consuming and computationexpensive. As this work does not rely on 1d-CNN to capture
the major spatiotemporal features, a small kernel of size (1, 3)
was used. This is because, firstly, smaller kernels can be
computationally efficient. Secondly, as the speed was assumed
non-stationary, which means the signal behaviour is likely to
vary over a long period, and therefore the feature in a smaller
perception field can be more representative.

L in + 2 × padding − (ker nel_si ze − 1) − 1
+1
stride
(5)

2) Activation Layer: As the convolution operation can be
considered as a linear mapping, a non-linear activation layer is
used after the first 1d convolution layer to introduce non-linear
modelling capabilities and thus enhance the representativeness
of the learned features, enhancing the capacity to model
complex input space. In the CNN Blocks of our proposed
model, the ReLU is employed as the activation function, which
can be expressed by the following equation:
ReLU(H ) = max(0, H )

(6)

where H is the feature map passed to ReLU. This is because
ReLU has a significant advantage over other activation functions such as tanh and sigmoid in terms of computational
complexity, mitigation of the gradient saturation problem, and
sparsity [40].
3) Layer Normalisation: The normalisation layer can be a
critical component in the deep neural network. By normalising
the inputs to a layer to zero mean and unit variance, the
training process can be stabilised and the performance of the
network can also be improved [41], [42]. Batch Normalisation
(BN) and Layer Normalisation (LN) can be the prevailing normalisation methods. While BN normalises each feature within
a sample, LN normalises all features within each sample.
To be specific, BN erases the relative magnitudes of the different features but preserves the relative magnitudes of the
different samples. Hence, BN can be more effective when
the statistical behaviours among different samples are more
important. In contrast, LN wipes out the relative magnitudes
between different samples but keeps the relative magnitudes
between different features within a sample. Therefore, it can
be more suitable for tasks where the features within a sample
are closely related, such as anomaly detection for multiple
sensors. Speaking to the TSC task on CAV with unmanaged
driving behaviour, as the speeds and acceleration can be
treated as non-stationary processes, the statistical features
among samples can be very uninformative for sensor anomaly
detection. As a result, LN can be more suitable for this task.
LN performs normalisation over the last 2 dimensions based
on the following equation:
x − E[x]
∗γ +β
y=√
Var[x] + ϵ

(7)

where y and x denote the normalised matrix and input matrix
respectively, ϵ is a minimum preventing the denominator to
be zero, γ and β are trainable affine transform weight and

15968

Fig. 4.

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 11, NOVEMBER 2024

Dual-channel attention mechanism (DAM).

bias. E[x] and Var[x] denote the mean and variance of input
x, which can be defined by the following equations:
E(x) = (1/t)
Var[x] = (1/t)

t
X
i=1
t
X

xi

(8)

(xi − E(x))2

(9)

i=1

C. Dual-Channel Attention Mechanism (DAM)
In multiple sensor anomaly detection tasks, abnormal data
can appear at any time and in any sensor, making both temporal and spatial (sensor-wise) features very important. In this
work, the Dual-channel Attention Mechanism (DAM) was
proposed to integrate the learning of spatiotemporal features
into the training process, hence the spatiotemporal features can
be extracted progressively and automatically.
The overall architecture of DAM can be illustrated by
Figure 4. The input can be passed to two attention modules
simultaneously, namely sensor-wise attention and time-wise
attention. The former is responsible for extracting spatial
dependencies among different sensors and the latter is for
extracting temporal dependencies among different time points.
Then, the feature maps generated by these two modules and
the original input will be added together, forming a shortcut
connection, before normalisation. The output of the DAM
is therefore a feature map with integrated spatiotemporal
features. The computation flow of DAM can be described by
the following equation:
OU TD AM = LN(LP(SWA(X )) + LP(TWA(X T )T ) + X )
(10)
where LP denotes linear projection, SWA and TWA mean
sensor-wise attention and time-wise attention respectively. The
details of sensor-wise attention and time-wise attention will be
explained in the following section.
1) Sensor-Wise Attention: The sensor-wise attention processes the dependencies among different sensors based on
the self-attention mechanism proposed in [26] as shown in
Figure 5a. Analogous to the operation of retrieval systems,
the self-attention mechanism utilizes a query vector to initiate
an information search. The mechanism subsequently identifies
corresponding keys in its database to align with the query
vector, ultimately resulting in an output represented by value

Fig. 5.

(a) Sensor-wise attention. (b) Time-wise attention.

vectors linked to these keys. In the context of the selfattention framework, input sequences can be converted via
linear projection into query vectors (Q), key vectors (K), and
value vectors (V), which is visually represented in Figure 5a
and elaborated on in the following equations:
Y = XWT + B

(11)

where X ∈ RC×L , W ∈ R3L×L , Y, B ∈ RC×3L , and
Q, K , V = Y [0 : C, 0 : L], Y [0 : C, L : 2L], Y [0 : C, 2L : 3L]
(12)
where Y [a : b, c : d] denotes the a to b rows and c to d
columns of Y . Then, the attention weights can be calculated
by:


QK T
Attention_weight = so f tmax √
(13)
dk
√
where dk represents the dimension of K and 1/ dk is a
scalar to prevent the predominance of a particular term in
SoftMax calculation, which might challenge the calculation
of the gradient [26]. Given that Q and K are independent
and adhere to the Gaussian distribution, the variance of their
dot product will be dk , posing a challenge when dealing with
the data with high dimensionality [26]. Finally, the attention
weight is multiplied by the V to form the output feature map
of self-attention:


QK T
V
(14)
Attention (Q, K , V ) = so f tmax √
dk
Clearly, the attention weights regulate the information transfer.
If a certain segment of the input data is assigned a weight of
zero, the propagation of information to the subsequent network

ZHANG et al.: TIME SERIES ANOMALY DETECTION IN VEHICLE SENSORS

layer can be impeded. Furthermore, each element (row) within
the attention output sequence integrates the information of all
elements in the entire input sequence. Hence, the dependencies
among different sensors can be modelled and integrated. It can
be found from the above calculations that, the dimension of
the output feature maps remains the same as the dimension of
the input data, namely Attention (Q, K , V ) ∈ RC×L .
2) Time-Wise Attention: Similarly, in time-wise attention,
the base unit for carrying out the calculation of the attention
mechanism can be replaced by the time steps, as shown in
Figure 5. Time-wise attention can be simply achieved by transposing the input and then performing similar computations to
obtain the Q, K and V before calculating the attention weights:
Y = XWT + B

(15)

where X ∈ R L×C , W ∈ R3C×C , Y, B ∈ R L×3C , and
Q, K , V= Y [0 : L , 0 : C], Y [0 : L , C : 2C], Y [0 : L , 2C : 3C]
(16)
Therefore, the feature maps with the integrated time dependencies over the entire time window can be obtained.
Then, the feature maps of Time-wise attention can be
transposed to keep the equal dimensionality with Sensor-wise
attention, before adding them to the original input to make a
shortcut connection. Finally, the constructed feature map can
be normalised, forming the output feature map of the DAM
block as shown in Figure 4.
D. Class Token Concatenation
Based on equation 14, it can be found that each row of
the output of the attention mechanism (corresponding to each
sensor in this work) is a weighted sum of all rows of the
feature map from the previous layer, and the weights are
calculated based on the data from each sensor. Theoretically,
it is reasonable to take any row in the final output of the
model’s feature map and use it as a multi-sensor feature
representation to perform classification. However, to avoid the
influence of specific sensor data on the feature representation
of multi-sensor data, a vector of random numbers was added
to the input data as a token for classification [26]. The features
of all sensors can be weighted and integrated into this token,
hence this vector can be used as a final feature representation.
This operation is illustrated in Figure 2, and the details can
be found in algorithm 2.
The overall computation flow of the proposed DSA-CNN
can be illustrated by algorithm 2.
IV. E XPERIMENTS AND R ESULTS

A. Training Process
This experiment was conducted on Google Colab environment with NVIDIA Tesla P100 PCIe 16 GB, and PyTorch
1.12 was used as the deep learning framework. The hyperparameters of the proposed model can be found in the Appendix.
As we formulated the sensor reading anomaly detection task

15969

Algorithm 2 Dual-Channel Attention CNN (DSA-CNN)
Input: X ← CAV Sensor Readings
Output: Normal reading, Anomalous reading
X ← X + Anomalies # Anomaly injection
Model Installation:
for l in range(Number of layers in DSA-CNN) do
Initiate W eights (l) ∼ N (0, 1)
Perform Singular Value Decomposition to W eights (l)
Ensure: W eights (l) W eights (l)T = I
Class Token Concatenation
T oken ← rand((1, L))
X ← Concatenate((X, T oken), dim = 0)
Forward:
for i in range(N) do
# DAM block calculations
X SW A ← L P(SW A(X ))
X T W A ← L P(T W A(X T )T )
X ← X SW A + X T W A + X
X ← L N (X )
# CNN block calculations
Residual ← X
X ← ReLU (Conv1(X )) # Conv1
X ← Dr opout (Conv2(X )) # Conv2
X ← L N (X + Residual)
Out puts = Classifier(X ) = X Wclassi f ier + bclassi f ier
Training:
for epoch in range(Number of epochs) do
Calculate Loss
Calculate Accuracy, Precision, Sensitivity, F-Score
Backpropagation
Return: Output

as a classification task, the cross entropy loss was used as the
loss function which can be defined by the following equation:
Loss(y, ŷ) = −

C
X

yi log ŷi



(17)

i=1

where y and ŷ are the true labels and model prediction using
one-hot encoding.
In terms of model initialisation, orthogonal initialisation was
employed, namely, the weight matrix W (l) of each layer will
be initialised to an orthogonal matrix, satisfying:
W (l) W (l) = I
T

(18)

where I is an identity matrix, and l is the layer index. This
is because the orthogonal initialisation is able to make the
error term norm-preserving during the backpropagation process [43], which can be expressed in the following equation:
δ (l−1)

2

= W (l) δ (l)
T

2

= δ (l)

2

(19)

where δ (l) is the loss term of the l layer of the model, and it
has shown great efficiency practically for training the model
based on the attention mechanism [44], [45]. Since in our
proposed model, the activation function was all ReLU and
the average gradient of ReLU around 0 can be approximated

15970

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 11, NOVEMBER 2024

√
as 0.5, we multiplied the initialised weight matrix by 2 to
preserve norm-preserving property. This is denoted by Gain =
1.41 in Table VI.
B. Results Evaluation Method
The performance of the proposed method was evaluated by
the following scores which can be normally used for assessing
classification algorithms:
TP +TN
Accuracy =
(20)
T P + FP + FN + T N
TP
Sensitivity =
(21)
T P + FN
TP
Precision =
(22)
T P + FP
2( Sensitivity ∗ Precision )
(23)
F1 Score =
Sensitivity + Precision
where TP, TN, FP, and FN mean True Positive, True Negative,
False Positive and False Negative respectively. In terms of the
sensor anomalies detection domain, as undetected abnormalities are far more damaging than classifying normal readings as
abnormal, the sensitivity score was highlighted in the results.
As the F1 score can be a comprehensive measure of precision
and sensitivity, it was used as a reference to compare the
performance of different models. Additional evaluations, such
as the ROC curve and the FPR95 metric (the false positive rate
at the true positive rate equal to 95%), which can be critical
in anomaly detection tasks can be found in the Appendix.
C. Single Anomaly Detection
In this section, the performance of DSA-CNN is evaluated
with respect to the occurrence of a single type of anomaly.
To ensure comparability, the same anomaly pattern, severity,
and possibility (5%) were used as in the current state of
the art [15] and [22]. The results from CNN Kalman Filter
(CNN-KF) [15], Multi-stage attention mechanism with an
LSTM-based CNN (MSALSTM-CNN) [22], and our proposed
DSA-CNN, in instant, bias, constant and drift detection are
compared in Table I to IV respectively. The mean F1 score and
sensitivity comparison for each type of anomaly is summarised
in Figure 6.
1) Instant Anomaly Detection: Table I shows the performance of DSA-CNN compared with the methods working on
the same dataset in literature for instant anomaly detection.
As the severity of the anomaly increases, an improvement
in the performance of all methods can be observed. However, the proposed DSA-CNN achieves higher F1 scores for
all severity levels of instant anomaly, compared with the
SOTA performance achieved by MSALSTM-CNN in the literature [22]. Speaking to sensitivity, except for the magnitude
of 500 × N (0, 0.01), DSA-CNN can be also better than the
other methods significantly. It is worth noting that DSA-CNN
shows outstanding performance in detecting mild anomalies.
While the F1 score of the MSALSTM-CNN at severity 25 ×
N (0, 0.01) is 70.18%, the DSA-CNN achieves 78.82%, and
the sensitivity at this severity can also be improved by 16.65%
by DSA-CNN. In case of severe anomalies, DSA-CNN shows
a slight improvement.

Fig. 6. Performance comparison of different models for single anomaly
detection.

2) Bias Anomaly Detection: Table II shows the performance
comparison for bias anomaly detection. For all methods in
this table, the longer the duration of the anomaly, the higher
the detection performance of the models for the same magnitude. Similarly, for anomalies of the same duration, the
higher the magnitude of the anomaly, the higher the detection
performance. Based on the results in this table, our proposed
DSA-CNN achieves improvements in both sensitivity and
F1 scores among most of the severity, compared to SOTA
performance in the literature, except for the magnitude of
U (0, 1) with a duration of 3, where MSALSTM-CNN achieves
the best F1 score (90.57%) and ours is 90.38%. However,
it can be found that DSA-CNN has significant advantages in
anomaly detection of small duration. In anomalies of duration
3 and 5, DSA-CNN improved on average by 2.57% and
1.28% in sensitivity and F1 score respectively compared to
MSALSTM-CNN.
3) Constant Anomaly Detection: Table III shows the performance comparison for Constant anomaly detection. It can
be observed that the performance of CNN-KF, MSALSTMCNN, and DSA-CNN methods consistently improves as the
anomaly duration increases while keeping the anomaly magnitude constant (U(0,5)). Their performance decreases as the
anomaly magnitude reduces while keeping the duration constant (d=10). The DSA-CNN method, however, demonstrates
superior performance in terms of sensitivity and F1 score
across all experiments. In addition, our proposed method
displays consistency in its performance, whereas the CNN-KF
and MSALSTM-CNN methods exhibit some variation. Nevertheless, all three methods show slightly declining performance in the last row with the lowest anomaly magnitude
(U(0,1)).
4) Drift Anomaly Detection: Table IV shows the results
of gradual drift anomaly detection using the CNNKF, MSALSTM-CNN, and DSA-CNN models. The
MSALSTM-CNN and DSA-CNN methods exhibit satisfactory
performance, while DSA-CNN outperforms MSALSTM-CNN
in sensitivity and F1 score for all experiments. The highest
F1-score of 98.97% is observed in row 2 by the DSA-CNN

ZHANG et al.: TIME SERIES ANOMALY DETECTION IN VEHICLE SENSORS

15971

TABLE I
I NSTANT

TABLE II
B IAS

TABLE III
C ONSTANT

TABLE IV
D RIFT

method when the duration is 20 and the anomaly magnitude is
linespace(0,4). The lowest F1-score is observed in row 3, with
94.2% achieved by the CNN-KF method when the anomaly
magnitude is the smallest. Furthermore, compared with the
MSALSTM-CNN and CNN-KF, the DSA-CNN demonstrates
consistent performance throughout the experiments, with
minor fluctuations. In [15], Wyk et al. stated that detecting
gradual drift can be one of the most challenging tasks of
anomaly detection. In the hardest situation, namely the
magnitude of linespace(0,2) with a duration of 20, DSA-CNN
can still improve the sensitivity and F1 score by 2.2% and
1.12% respectively.

D. Mixed Anomaly Detection
In our experiment, the performance of DSA-CNN was also
examined for the occurrences of all types of anomalies. The
performance evaluation of different algorithms with respect
to different sensors is given in Table V. As this type of
experiment is not provided in [22], only [15] and our proposed
method are shown in this table. Based on the results, DSACNN outperforms the other algorithms on all three sensors,
achieving the highest scores on almost all performance metrics, especially for sensitivity and F1 scores. This suggests that
DSA-CNN provides a more accurate and robust approach to
anomaly detection than the other algorithms evaluated.

15972

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 11, NOVEMBER 2024

TABLE V
M IX

V. D ISCUSSION

TABLE VI
H YPER PARAMETERS

It is clear that the DSA-CNN proposed in this paper
offers significant advantages in terms of sensitivity and F1
score, especially in minor sensor anomalies. Higher sensitivity
means fewer undetected anomalies, which can be crucial for
safety-critical application scenarios, such as the CAV velocity
and acceleration data used in this work, which can be the
important decision bases for autonomous driving systems [46].
As an important sensor anomaly detection algorithm,
Kalman filtering has the advantages of being easy to implement and computationally efficient, making it widely used.
It can predict the near future or current system state by tracing
back to a few past system state data, so by comparing the
difference between the estimated data and the measurements
and setting a threshold, it can determine if the sensor reading
now is in an abnormal state. However, Kalman filtering has
three disadvantages in sensor anomaly detection. Firstly, its
performance relies on artificial noise estimations, for example
in [15] where the sensor noise was assumed to be Gaussian
white noise, which is sometimes not representative of the real
noise in the actual system. Secondly, plain Kalman filtering
often requires the assumption that the system is linear and
time-invariant [47]. This assumption can be satisfied when
the time window taken for the analysis of CAV velocities
is small enough, but the time window for the analysis of
time-series data often cannot be too small to ensure that
sufficient information can be incorporated, so the non-linearity
introduced by the large time window becomes a source of error
in the Kalman filter estimations. Finally, defining thresholds
for normal intervals can be often difficult, as the intensity
of noise in a real system can be likely to vary according
to environmental conditions. These might be the reason why
the Kalman filter-based approach in [15] achieves relatively
poor performance despite the fact that the use of CNNs to
extract a representation of the system state can overcome to
some extent the problems of noise and non-linearity within
the time window. Since deep learning-based methods do
not require the aforementioned assumptions, they offer great
potential for anomaly detection due to their fewer restrictions
on applications and enhanced applicability.
LSTM is an RNN algorithm that excels in time series data
modelling, and plays an important role in the detection of
anomalies in time-series sensor data. LSTM-based methods
do not require an accurate estimation of noise, unlike Kalman
filtering, and do not rely on the assumption of linear timeinvariant systems. This can be the possible reason why the
LSTM-based method used in [22] outperforms the Kalman

filter-based method in [15]. However, since LSTM can be
still recursive in nature, the features of the initial time steps
can still be difficult to learn, especially for small anomalies.
In terms of the proposed DSA-CNN, it combines the strengths
of CNNs in local feature extraction with the self-attention
mechanism’s ability to model global context. This synergy
enhances the model’s sensitivity to small anomalies in multisensor data. Traditional methods might overlook these small
anomalies due to their reliance on local patterns and inability
to capture long-range dependencies effectively. In addition, the
integration of a dual-channel self-attention mechanism allows
for the extraction of spatiotemporal features from sensor data,
enabling the system to extract subtle but crucial details that
might indicate an anomaly. This is particularly important for
small anomalies that may not produce significant changes
in sensor readings. The DSA-CNN method leverages these

ZHANG et al.: TIME SERIES ANOMALY DETECTION IN VEHICLE SENSORS

Fig. 7.

15973

ROC curves and FPR95 metrics of the experiments conducted in this study.

advancements, offering a more robust and sensitive approach
to anomaly detection. Additional experiments to verify the
effectiveness of the proposed dual-channel self-attention mechanism can be found in the Appendix.
However, due to the current supervised learning-based
training approach, the performance of the proposed model
in dealing with unknown complex anomalous patterns has
not been evaluated, which can be important in real applications [48]. A common deep learning-based approach in the
literature for handling anomalies of unknown patterns can
be the unsupervised learning-based autoencoder architecture.
In this type of approach, the original normal signal can be
mapped to latent spaces using a deep learning model, and then,
one of the latent spaces can be used as a feature representation.
The distance between the latent space of the anomalous data
and the latent space of the normal data can be calculated as
a criterion for the occurrence of anomalies [49], [50], [51].
It can be found that the patterns of anomaly behaviour will

not be treated as prior knowledge, giving this type of method
the potential to detect arbitrary anomalies. The performance
of DSA-CNN in this type of methodology can be an important
future direction to be evaluated. In addition, the assumption
of anomaly that only one sensor can be abnormal at the same
time can be violated in real-world applications. This setting
was adopted to maintain consistency with the two baselines
referenced in this study, thereby enabling the comparison of
algorithmic performance. Extending the proposed approach to
scenarios with multiple simultaneous sensor anomalies can be
another valuable direction for further research.
VI. C ONCLUSION AND F UTURE W ORK
Anomaly detection in multi-sensor data streams can be
an important foundation for CAVs and many safety-critical
systems. In this paper, a method, DSA-CNN, was proposed
based on the self-attention mechanism and CNN to detect
the anomalous behaviour of CAV velocity and acceleration

15974

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 11, NOVEMBER 2024

TABLE VII
P ERFORMANCE D IFFERENCE A MONG DSA-CNN, I TS S ENSOR -W ISE ATTENTION -O NLY V ERSION , AND I TS T IME -W ISE ATTENTION -O NLY V ERSION

sensors. We proposed a dual-channel self-attention structure
to enhance the sensitivity of the model with respect to small
anomalies, and this structure can integrate the learning of
spatiotemporal features into the training process of deep learning, eliminating artificial feature engineering. Our proposed
method was tested on a publicly available CAV dataset, and the
sensor anomaly was simulated based on the 4 most damaging
anomalies for CAVs [32], [33]. Based on the experimental
results, our proposed DSA-CNN achieved 2.57%, 2.07%,
1.78%, and 3.83% performance gains in sensitivity for drift,
constant, bias, and instant anomalies, and 1.53%, 1.32%,
0.94%, and 2.21% gains in F1 score, compared with the SOTA
performance model in the literature proposed in [22]. The
experimental results also show that DSA-CNN has a clear
advantage in handling small anomalies.
However, due to the current supervised-learning-based classification training scheme, it can be difficult to evaluate the
performance in the presence of unknown anomaly patterns in
a convincing manner. By reorganizing the deep learning model
proposed in this paper into an unsupervised learning form, all
sensor data can be mapped to a latent space. By comparing
the distance of anomalous data to normal data in the latent
space, the presence of sensor anomaly can be determined. As a
result, this type of model can be no longer limited by specific
anomaly patterns, improving the generalisation ability. This
can be an important future research direction.
A PPENDIX
H YPER PARAMETERS OF DSA-CNN
The hyperparameters of the model proposed in this work
are shown in Table VI.
A DDITIONAL E VALUATIONS
This section provides additional evaluations, namely the
ROC curve and the FPR95 metric (the false positive rate at
the true positive rate equal to 95%), which can be critical in
anomaly detection tasks. The ROC and FPR95 can be found
in Figure 7.
A BLATION E XPERIMENT
In order to verify the positive effect of one of the core
modules of the model proposed in this paper, namely the
DAM module, on performance, this section presents ablation
experiments.
Two distinct experiments were conducted to validate the
efficacy of integrating sensor-wise and time-wise attention mechanisms. In the initial experiment, we exclusively

employed sensor-wise attention across both channels, focusing
on the individual characteristics of each sensor. Conversely,
the second experiment solely utilized time-wise attention in
both channels, concentrating on temporal dynamics. This
ablation study was designed to rigorously assess the impact
and effectiveness of combining sensor-wise and time-wise
attention, providing a comprehensive understanding of their
synergistic potential in the proposed model.
To maintain comparability, all training parameters, data, the
rest of the model architecture, as well as the environment were
kept the same. The ablation experiments were only conducted
on the most challenging tasks on each of the anomaly types
(The tasks that received the lowest F1 scores). The results
can be found in Table VII. It can be found that neither the
use of sensor-wise attention alone nor time-wise attention can
achieve the performance of using them simultaneously, which
validates the effectiveness of the proposed DAM in anomaly
detection.
R EFERENCES
[1] T-Scotland, A CAV Roadmap for Scotland, Transp. Scotland, Glasgow,
U.K., 2019.
[2] Connected & Automated Mobility 2025: Realising the Benefits of SelfDriving Vehicles in the UK, HM Government, London, U.K., 2022.
[3] C-Advanced Automotive Technology. Connected and Automated
Vehicles. Accessed: May 25, 2023. [Online]. Available:
http://autocaat.org/Technologies/Automated_and_Connected_Vehicles/
[4] A. Coppola, D. G. Lui, A. Petrillo, and S. Santini, “Eco-driving control
architecture for platoons of uncertain heterogeneous nonlinear connected
autonomous electric vehicles,” IEEE Trans. Intell. Transp. Syst., vol. 23,
no. 12, pp. 24220–24234, Dec. 2022.
[5] RM Infrastructure and W-Management. Mobility. Accessed: May 25,
2023. [Online]. Available: https://www.rijkswaterstaat.nl/en/mobility
[6] C. Yan, W. Xu, and J. Liu, “Can you trust autonomous vehicles:
Contactless attacks against sensors of self-driving vehicle,” Defcon,
vol. 24, no. 8, p. 109, 2016.
[7] S. Rajasegarar, C. Leckie, and M. Palaniswami, “Anomaly detection
in wireless sensor networks,” IEEE Wireless Commun., vol. 15, no. 4,
pp. 34–40, Aug. 2008.
[8] I. C. Paschalidis and Y. Chen, “Statistical anomaly detection with sensor
networks,” ACM Trans. Sensor Netw., vol. 7, no. 2, pp. 1–23, Aug. 2010.
[9] R. Zhang, P. Ji, D. Mylaraswamy, M. Srivastava, and S. Zahedi, “Cooperative sensor anomaly detection using global information,” Tsinghua
Sci. Technol., vol. 18, no. 3, pp. 209–219, Jun. 2013.
[10] M. Xie, J. Hu, and B. Tian, “Histogram-based online anomaly detection
in hierarchical wireless sensor networks,” in Proc. IEEE 11th Int. Conf.
Trust, Secur. Privacy Comput. Commun., Jun. 2012, pp. 751–759.
[11] K. Cohen and Q. Zhao, “Active hypothesis testing for anomaly detection,” IEEE Trans. Inf. Theory, vol. 61, no. 3, pp. 1432–1450, Mar. 2015.
[12] L. Erhan et al., “Smart anomaly detection in sensor systems: A multiperspective review,” Inf. Fusion, vol. 67, pp. 64–79, Mar. 2021.
[13] V. Rajagopalan and A. Ray, “Symbolic time series analysis via waveletbased partitioning,” Signal Process., vol. 86, no. 11, pp. 3309–3320,
Nov. 2006.

ZHANG et al.: TIME SERIES ANOMALY DETECTION IN VEHICLE SENSORS

[14] N. Mohamudally and M. Peermamode-Mohaboob, “Building an
anomaly detection engine (ADE) for IoT smart applications,” Proc.
Comput. Sci., vol. 134, pp. 10–17, Jan. 2018.
[15] F. Van Wyk, Y. Wang, A. Khojandi, and N. Masoud, “Real-time sensor
anomaly detection and identification in automated vehicles,” IEEE Trans.
Intell. Transp. Syst., vol. 21, no. 3, pp. 1264–1276, Apr. 2019.
[16] K. Thiyagarajan, S. Kodagoda, and L. Van Nguyen, “Predictive analytics
for detecting sensor failure using autoregressive integrated moving
average model,” in Proc. 12th IEEE Conf. Ind. Electron. Appl. (ICIEA),
Jun. 2017, pp. 1926–1931.
[17] N. Mohamudally, Introductory Chapter: Time Series Analysis (TSA) for
Anomaly Detection in IoT. London, U.K.: IntechOpen, 2018.
[18] D. Bogdoll, M. Nitsche, and J. M. Zöllner, “Anomaly detection in
autonomous driving: A survey,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit., Jun. 2022, pp. 4488–4499.
[19] Y. Luo, Y. Xiao, L. Cheng, G. Peng, and D. Yao, “Deep learning-based
anomaly detection in cyber-physical systems: Progress and opportunities,” ACM Comput. Surv., vol. 54, no. 5, pp. 1–36, 2021.
[20] T. Wen and R. Keyes, “Time series anomaly detection using convolutional neural networks and transfer learning,” 2019, arXiv:1905.13628.
[21] F. O. Ozkok and M. Celik, “Convolutional neural network analysis
of recurrence plots for high resolution melting classification,” Comput.
Methods Programs Biomed., vol. 207, Aug. 2021, Art. no. 106139.
[22] A. R. Javed, M. Usman, S. U. Rehman, M. U. Khan, and M. S. Haghighi,
“Anomaly detection in automated vehicles using multistage attentionbased convolutional neural network,” IEEE Trans. Intell. Transp. Syst.,
vol. 22, no. 7, pp. 4291–4300, Jul. 2021.
[23] M. Schak and A. Gepperth, “A study on catastrophic forgetting in deep
LSTM networks,” in Artificial Neural Networks and Machine Learning.
Munich, Germany: Springer, 2019, pp. 714–728.
[24] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” 2022,
arXiv:2201.07284.
[25] M. Ma, L. Han, and C. Zhou, “BTAD: A binary transformer deep neural
network model for anomaly detection in multivariate time series data,”
Adv. Eng. Informat., vol. 56, Apr. 2023, Art. no. 101949.
[26] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. neural Inf.
Process. Syst., vol. 30, 2017, pp. 1–11.
[27] Z. Zhang, M. Farnsworth, B. Song, D. Tiwari, and A. Tiwari, “Deep
transfer learning with self-attention for industry sensor fusion tasks,”
IEEE Sensors J., vol. 22, no. 15, pp. 15235–15247, Aug. 2022.
[28] L. Jiang, H. Xu, J. Liu, X. Shen, S. Lu, and Z. Shi, “Anomaly detection
of industrial multi-sensor signals based on enhanced spatiotemporal features,” Neural Comput. Appl., vol. 34, no. 11, pp. 8465–8477, Jun. 2022.
[29] J. Pfeil, J. Wieland, T. Michalke, and A. Theissler, “On why the
system makes the corner case: AI-based holistic anomaly detection
for autonomous driving,” in Proc. IEEE Intell. Vehicles Symp. (IV),
Jun. 2022, pp. 337–344.
[30] A. B. Sharma, L. Golubchik, and R. Govindan, “Sensor faults: Detection
methods and prevalence in real-world datasets,” ACM Trans. Sensor
Netw., vol. 6, no. 3, pp. 1–39, Jun. 2010.
[31] M. H. Bhuyan, D. K. Bhattacharyya, and J. K. Kalita, “Network anomaly
detection: Methods, systems and tools,” IEEE Commun. Surveys Tuts.,
vol. 16, no. 1, pp. 303–336, 1st Quart., 2014.
[32] J. Petit and S. E. Shladover, “Potential cyberattacks on automated
vehicles,” IEEE Trans. Intell. Transp. Syst., vol. 16, no. 2, pp. 546–556,
Apr. 2014.
[33] Y. Mo, E. Garone, A. Casavola, and B. Sinopoli, “False data injection
attacks against state estimation in wireless sensor networks,” in Proc.
49th IEEE Conf. Decis. Control (CDC), Dec. 2010, pp. 5967–5972.
[34] D. Bezzina and J. Sayer, “Safety pilot model deployment: Test conductor
team report,” Rep. DOT HS, vol. 812, no. 171, p. 18, 2014.
[35] UD Transportation. (Jan. 24, 2022). Safety Pilot Model Deployment
Data. [Online]. Available: https://catalog.data.gov/dataset/safety-pilotmodel-deployment-data
[36] J. Wang, S. Li, W. Ji, T. Jiang, and B. Song, “A T-CNN time series
classification method based on Gram matrix,” Sci. Rep., vol. 12, no. 1,
p. 15731, Sep. 2022.
[37] L. Xi, Z. Yun, H. Liu, R. Wang, X. Huang, and H. Fan, “Semi-supervised
time series classification model with self-supervised learning,” Eng.
Appl. Artif. Intell., vol. 116, Nov. 2022, Art. no. 105331.
[38] I. Goodfellow, Y. Bengio, and A. Courville, Deep Learning. Cambridge,
MA, USA: MIT Press, 2016.

15975

[39] W. Tang, G. Long, L. Liu, T. Zhou, M. Blumenstein, and J. Jiang,
“Omni-scale CNNs: A simple and effective kernel size configuration
for time series classification,” 2020, arXiv:2002.10061.
[40] A. F. Agarap, “Deep learning using rectified linear units (ReLU),” 2018,
arXiv:1803.08375.
[41] S. Santurkar, D. Tsipras, A. Ilyas, and A. Madry, “How does batch
normalization help optimization?” in Proc. Adv. Neural Inf. Process.
Syst., vol. 31, 2018, pp. 1–11.
[42] J. L. Ba, J. R. Kiros, and G. E. Hinton, “Layer normalization,” 2016,
arXiv:1607.06450.
[43] A. M. Saxe, J. L. McClelland, and S. Ganguli, “Exact solutions to the
nonlinear dynamics of learning in deep linear neural networks,” 2013,
arXiv:1312.6120.
[44] K. Lu, A. Grover, P. Abbeel, and I. Mordatch, “Pretrained transformers
as universal computation engines,” arXiv preprint arXiv: 2103. 05247,
vol. 1, 2021.
[45] Y. Fei, Y. Liu, X. Wei, and M. Chen, “O-ViT: Orthogonal vision
transformer,” 2022, arXiv:2201.12133.
[46] L. Nie, J. Guan, C. Lu, H. Zheng, and Z. Yin, “Longitudinal speed
control of autonomous vehicle based on a self-adaptive PID of radial
basis function neural network,” IET Intell. Transp. Syst., vol. 12, no. 6,
pp. 485–494, Aug. 2018.
[47] Q. Li, R. Li, K. Ji, and W. Dai, “Kalman filter and its application,”
in Proc. 8th Int. Conf. Intell. Netw. Intell. Syst. (ICINIS), Nov. 2015,
pp. 74–77.
[48] D. Bogdoll et al., “Description of corner cases in automated driving:
Goals and challenges,” in Proc. IEEE/CVF Int. Conf. Comput. Vis.
Workshops (ICCVW), Oct. 2021, pp. 1023–1028.
[49] W. Yu, I. Y. Kim, and C. Mechefske, “An improved similarity-based
prognostic algorithm for RUL estimation using an RNN autoencoder
scheme,” Rel. Eng. Syst. Saf., vol. 199, Jul. 2020, Art. no. 106926.
[50] W. Yu, I. Y. Kim, and C. Mechefske, “Analysis of different RNN autoencoder variants for time series classification and machine prognostics,”
Mech. Syst. Signal Process., vol. 149, Feb. 2021, Art. no. 107322.
[51] S. E. Huang, Y. Feng, and H. X. Liu, “A data-driven method for falsified
vehicle trajectory identification by anomaly detection,” Transp. Res. C,
Emerg. Technol., vol. 128, Jul. 2021, Art. no. 103196.

Ze Zhang received the B.Sc. degree from Jiangnan University in 2012 and the M.Sc. and Ph.D.
degrees in electronic and electrical engineering from
The University of Sheffield in 2018 and in 2024,
respectively.
Before his research career, he was with electric
power industry after graduating the B.Sc. degree.
He is currently a Research Associate with the
Department of Automatic Control and Systems
Engineering, The University of Sheffield, and Airbus
on industrial applications. He is a Research Theme
Lead with the EPSRC Made Smarter Innovation–Research Centre for Connected Factories. His main research interests are AI, sensor fusion, computer
vision for digital manufacturing, and manufacturing robot systems.

Yue Yao received the M.Sc. degree in robotics from
The University of Sheffield in 2022.
Prior to embarking on his research career,
he gained invaluable industry experience as a
Robotics Engineer with the energy sector. Currently,
he was a Research Assistant with the Department of
Automatic Control and Systems Engineering, The
University of Sheffield. In this role, he actively
contributes to cutting-edge research projects, with
a specific focus on robotics and sensing in digital
manufacturing, particularly in the context of assembly systems. He is interested in robotics, assembly systems, digital twin and
sensing for robots, and digital manufacturing. He received the Nicholson Prize
for masters studies.

15976

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS, VOL. 25, NO. 11, NOVEMBER 2024

Windo Hutabarat received the bachelor’s degree in
aeronautical engineering in 2001.
He worked in the aviation industry before joining academia. He is a Research Associate with
the Department of Automatic Control and Systems
Engineering, The University of Sheffield. He is part
of the Airbus/RAEng Research Team in Digitization
of Manufacturing and is an Application Research
Lead with the EPSRC Made Smarter Research Centre for Connected Factories. In addition to his role as
a Researcher, he is also a part-time Doctoral Student.
He has over 16 years of experience as an Applied Researcher, collaborating
closely with industry in the U.K. Inspired by the innovative use of sensors
in gaming devices, he has pioneered the use of affordable sensors to digitize
complex manufacturing processes. This innovative approach has led to six
collaborative research projects supported by Innovate U.K.

Michael Farnsworth received the degree in biochemistry with molecular biology from Cardiff
University in 2004, the M.Sc. degree in computer
science from the University of the West of England
in 2007, and the Ph.D. degree in computer science
from Cranfield University in 2013.
He is currently a Research Associate with the
Department of Automatic Control and Systems
Engineering, The University of Sheffield; and a
Research Lead with the EPSRC Future Electrical
Machines Manufacturing Hub. He has published
over 30 peer-reviewed articles. His research interests cover the field of digital
manufacturing and the application of machine learning and bioinspired artificial intelligence. His interest also includes understanding how evolutionary
processes can be used to develop systems of general intelligence that are
able to tackle hard problems within the field of manufacturing and robotics.
He is a Chartered Scientist and an Associate Fellow of the Higher Education
Authority and a member of IET.

Divya Tiwari received the B.Eng. degree in electronics and communication in 2002 and the Ph.D.
degree from Cranfield University in 2010.
Before joining academia, she was with electronics
industry on aerospace and automotive applications
in the U.K. She is a Research Fellow with the Digitization Laboratory for Manufacturing, Department
of Automatic Control and Systems Engineering,
The University of Sheffield. Her work focuses on
sensors and simulation for high-value manufacturing
processes. Previously, she has worked in the area of
development of photonic sensors for manufacturing and automotive applications. She has authored over 21 peer-reviewed articles. She received the
Daphne Jackson and Royal Academy of Engineering Fellowship in 2013 for
the development of novel photonic sensors for industrial applications.

Ashutosh Tiwari is a Deputy Vice-President for
Innovation at the University of Sheffield and
holds the prestigious Royal Academy of Engineering (RAEng) and Airbus Research Chair. He is
internationally renowned for research in digital manufacturing and works in partnership with industry
to develop new techniques and solutions for digitalisation, instrumentation, in-process monitoring and
real-time simulation of skill-intensive manufacturing
processes, such as wing manufacture and engine
assembly. He has a strong track record of leading
research and innovation projects across technology readiness levels, and
serves on the Engineering and Physical Sciences Research Council (EPSRC)
Strategic Advisory Team for Manufacturing and the Circular Economy. He is
the Deputy Director of the EPSRC Future Electrical Machines Manufacturing
Hub, Sheffield Lead of the Made Smarter Research Centre for Connected
Factories, and was awarded an EPSRC High-Value Manufacturing Catapult
Fellowship. He is passionate about training people for manufacturing research
and has graduated 38 Ph.D. students.
PAPER_TEXT
