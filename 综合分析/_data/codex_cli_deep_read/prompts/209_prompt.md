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
# [209] DroneSSL: Self-Supervised Multimodal Anomaly Detection in Internet of Drone Things
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
编号：209
题名：DroneSSL: Self-Supervised Multimodal Anomaly Detection in Internet of Drone Things
年份：2024
DOI：10.1109/tce.2024.3376440
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2024.3376440.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、入侵检测与网络异常检测
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\209.txt
- 原始字符数：59081
- 本次发送字符数：59081
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

4287

DroneSSL: Self-Supervised Multimodal Anomaly
Detection in Internet of Drone Things
Junaid Akram , Ali Anaissi , Wajdy Othman, Abdulatif Alabdulatif , Member, IEEE, and Awais Akram

Abstract—In this study, we introduce a pioneering framework,
DroneSSL, that integrates the concept of spatial crowdsourcing
with TinyML to enhance anomaly detection in the Internet
of Drone Things (IoDT). This innovative approach leverages
drones and unmanned ground vehicles (UGVs) for expansive
data collection in environments that are typically inaccessible
or hazardous, such as during Australian bushfire incidents.
By employing lightweight machine learning models alongside
advanced communication technologies, DroneSSL transcends
traditional spatial-temporal data analysis methods. It efficiently
processes multimodal data from diverse Points-of-Interest (PoIs),
significantly improving the quality and speed of data collection
and analysis. The framework’s integration of a temporal feature
extraction module with a Graph Neural Network (GNN) and
its adaptable, scalable GNN architecture tailor DroneSSL for
real-time operations in resource-constrained IoDT environments.
Achieving an 89.6% F1 score, DroneSSL marks a substantial 4.9% improvement over existing approaches, highlighting
its effectiveness in critical applications such as environmental
surveillance and emergency response. This advancement not
only showcases the potential of combining TinyML with spatial
crowdsourcing for IoDT but also sets a new standard for efficient,
scalable anomaly detection, paving the way for future innovations
in IoT edge devices and environmental monitoring systems.
Index Terms—Self-supervised learning, autoencoder, GNN,
anomaly detection, drones, data fusion, TinyML.

I. I NTRODUCTION
N THE evolving landscape of consumer electronics, deeply
intertwined with our daily lives, TinyML emerges as a
pivotal technology reshaping how we interact with smart
devices [1]. From smartphones to wearable technologies, the
integration of TinyML is propelling these gadgets beyond their
traditional roles, aligning with the Internet of Things (IoT)
paradigm [2]. This progression has ushered in a new era
where consumer electronics transcend individual functionality,

I

Manuscript received 17 December 2023; revised 7 February 2024 and 29
February 2024; accepted 4 March 2024. Date of publication 12 March 2024;
date of current version 26 April 2024. (Corresponding authors: Junaid Akram;
Wajdy Othman.)
Junaid Akram and Ali Anaissi are with the School of Computer Science,
University of Sydney, Sydney, NSW 2008, Australia (e-mail: jakr7229@
sydney.edu.au; ali.anaissi@sydney.edu.au).
Wajdy Othman is with the School of Computer Science and Technology,
Anhui University, Hefei 230601, China (e-mail: wajdy@ahu.edu.cn).
Abdulatif Alabdulatif is with the Department of Computer Science,
College of Computer, Qassim University, Buraidah 52571, Saudi Arabia
(e-mail: ab.alabdulatif@qu.edu.sa).
Awais Akram is with the Department of Computer Science, COMSATS
University Islamabad, Islamabad 61100, Pakistan (e-mail: awaisakram1212@
gmail.com).
Digital Object Identifier 10.1109/TCE.2024.3376440

becoming integrated elements of a broader, interconnected
ecosystem [3].
The advent of the Internet of Drone Things (IoDT) epitomizes this technological leap, extending the reach of consumer
electronics into the skies [4]. IoDT networks, encompassing
sensor-laden drones, cater to a spectrum of applications,
from environmental surveillance, such as Australian bushfire monitoring, to defense and healthcare [5], [6], [7], [8],
[9], [10]. However, deploying IoDT systems, especially in
remote or challenging environments, invites a range of disruptions and security risks, including signal interference and
data breaches [11], [12]. These systems are further strained
by inherent limitations in resources like energy and bandwidth [13].
Integrating the concept of spatial crowdsourcing with IoDT
represents a groundbreaking approach to overcoming these
challenges, particularly in environmental monitoring contexts
such as Australian bushfire management [4], [5]. Spatial
crowdsourcing, when combined with IoDT, leverages drones
and unmanned ground vehicles (UGVs) for expansive, realtime data collection in areas that are typically hazardous
or unreachable by humans. This synergy not only addresses
the limitations of traditional human-operated spatial crowdsourcing by covering larger areas with greater efficiency but
also enhances the quality and speed of data collection from
Points-of-Interest (PoIs) through advanced communication
technologies like WiFi/5G [8], [10]. The incorporation of
air-ground non-orthogonal multiple access (AG-NOMA) techniques further optimizes data transmission between drones and
UGVs, facilitating high-quality data relay and decoding [9].
One of the critical aspects of IoDT, enhanced by the
integration of spatial crowdsourcing, is the development of
lightweight models for anomaly detection. These models are
essential for identifying deviations in data flow patterns, which
could indicate bushfire developments or other environmental
anomalies. Current research often overlooks the spatial location information among drones and the correlation of data
across various modes, a gap that our approach, DroneSSL,
aims to fill. DroneSSL, a unique lightweight self-supervised
learning framework designed for IoDT, incorporates TinyML
principles with spatial-temporal data analysis. This not only
advances anomaly detection but also significantly improves
the functionalities of consumer electronics within the IoDT
domain. By leveraging spatial crowdsourcing, DroneSSL can
process and analyze data from a broader area more efficiently,
enhancing the system’s adaptability and performance in critical
applications like bushfire monitoring.

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1558-4127 
See https://www.ieee.org/publications/rights/index.html for more information.

4288

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

TABLE I
C OMPARISON OF A NOMALY D ETECTION M ETHODS IN I O DT

The following is a summary of this paper’s main
contributions.
1) TinyML-Driven Multimodal Data Analysis: Our framework leverages the strengths of TinyML and spatial
crowdsourcing to process complex multimodal data
flows in IoDT systems. By employing lightweight
machine learning models and drones for data collection,
we ensure efficient processing of data from diverse
spatial locations, enhancing spatiotemporal correlation
analysis. This approach surpasses traditional methods by
integrating the temporal attributes of multimodal multidrone data and the spatial connections among drones
and UGVs, providing a comprehensive overview of
environmental conditions.
2) Lightweight Anomaly Detection with Temporal Feature
Extraction and GNN: Introducing DroneSSL, a novel
anomaly detection system that embodies the fusion of
spatial crowdsourcing with TinyML. DroneSSL integrates a temporal feature extraction module and a Graph
Neural Network (GNN) for advanced spatiotemporal
analysis. Optimized for IoDT devices with limited
computational resources, this system leverages selfsupervised learning and autoencoder methodologies,
allowing for the efficient processing of uplinked data
from drones and additional sensory data from PoIs
through UGVs.
3) Adaptable and Scalable GNN Architecture: Our framework addresses the scalability challenge in IoDT by
introducing a flexible GNN architecture that can adapt

to various GNN kernels, suitable for different anomaly
detection scenarios. By clustering drones and employing
spatial crowdsourcing for data collection and processing,
we propose a strategy for conducting data flow training
and inference on selected anchor drones and UGVs.
This approach ensures minimal hardware strain on
IoDT devices and maximizes the efficiency of TinyML
models, crucial for real-time operations in the spatially
diverse and resource-constrained environments of IoDT
networks.
The structure of this manuscript is as follows: In Section II,
the fundamental concepts and relevant studies in anomaly
detection are presented. We describe our proposed selfsupervised learning anomaly detection approach for the
Internet of Drone Things in further depth in Section III. In
Section IV, we do an extensive experimental evaluation of
our techniques. The study concludes with a summary and
concluding remarks in Section V.
II. R ELATED W ORK
In recent years, the Internet of Drone Things (IoDT) has
posed significant challenges in anomaly detection, prompting
researchers to propose various solutions. For instance, [14]
utilized Euclidean distances to cluster IoDT data points for
anomaly detection, but this method did not leverage the
spatial correlations between drones. An alternative method
proposed by [15] focuses on anomaly detection in multinode data flows using correlation analysis, adeptly managing

AKRAM et al.: DroneSSL: SELF-SUPERVISED MULTIMODAL ANOMALY DETECTION IN IoDT

high-dimensional time series data in IoDT and optimizing
computational resources. Yet, this approach does not account
for the multimodal nature of IoDT, where each drone is
capable of recording data across various modalities.
The escalating scale and intricacy of IoDT, characterized by
varied data sources and dynamic threat landscapes, highlight
the shortcomings of current anomaly detection techniques.
These include limited generalization, and struggles with highdimensional, heterogeneous, and imbalanced datasets. Deep
learning technologies [23] are being progressively employed
to surmount these challenges. Research such as [16] has
delved into unsupervised multivariate anomaly detection utilizing generative adversarial networks (GAN) coupled with
LSTM to discern temporal patterns in complex data streams.
Likewise, [17] developed an anomaly detection methodology
combining a variational autoencoder (VAE) with LSTM,
and [18] introduced a CNN-based framework augmented with
incremental learning.
Using spatial properties of network topologies is essential
for robust anomaly detection in the Internet of Things. In
IoDT networks, adjacency and attribute matrices are rich
sources of important characteristics that are well-suited for
graph neural networks (GNNs). Important GNN types are
GraphSage [24], graph convolution networks (GCNs) [25], and
graph attention networks (GATs) [26]. They are all widely
used for graph representation learning in IoDT, with the goal
of extracting low-dimensional representations from intricate
graph structures.
Graph embedding technologies and unsupervised learning
play a critical role in IoDT anomaly detection. Unsupervised
techniques, reliant solely on normal samples for model
training, are bifurcated into reconstruction and predictive
modalities. Methods such as [27] employed GCNs for node
embedding and data reconstruction, while [28] advanced to
GATs. Reference [29] merged structure learning with GNNs
for anticipatory anomaly detection, and [30] fused forecastcentric models with reconstruction-centric frameworks to forge
an innovative anomaly detection paradigm.
Addressing the challenge of overfitting in traditional unsupervised reconstruction methods, self-supervised learning has
emerged as a solution to enhance neural network generalization. In their work, [31] crafted a model predicated on
a two-phase adversarial training approach. In parallel, [32]
combined GraphSage approaches with the Deep Graph
Infomax (DGI) methodology to improve the performance of
their model. Other innovative frameworks like [33] explored
multiscale adversarial training.
However, these methods typically overlook the IoDT’s
unique three-dimensional data flow nature, encompassing
nodes, modes, and time. To address this, [22] processed
multimodal data flows separately, extracting spatial features
and using prediction errors for anomaly detection. Despite
its effectiveness, the method faced challenges in large-scale
IoDT scenarios due to branch expansion with increasing drone
numbers.
Combining the benefits of self-supervised learning and
reconstruction-based models, our method combines the temporal properties of local and global drones. This integration

4289

not only augments detection efficacy but also minimizes
the requirements for time and computational resources. This
approach is particularly suited for large-scale IoDT applications, such as Australian bushfire monitoring.
III. S YSTEM M ODEL
A. Problem Formulation
In the domain of the Internet of Drone Things (IoDT),
systems typically monitor extensive areas through a network
of densely deployed drones. The data collected by a drone and
its neighboring drones often show significant correlations due
to their spatial proximity. For instance, when a drone detects
a bushfire, it is expected that nearby drones will also register
changes in their environmental readings, such as a noticeable
increase in temperature.
The data collected by drones are not isolated; they are
multimodal, indicating that changes in one type of data
(e.g., temperature increase) are often accompanied by changes
in other types (e.g., increase in CO2 levels and decrease
in humidity). This suggests a direct relationship between
temperature and CO2 concentration and an inverse relationship
with humidity.
The primary aim of this research is to exploit these
spatiotemporal correlations for effective anomaly detection
in IoDT environments. We approach the anomaly detection
challenge as a regression problem focused on forecasting time
series data. The regression model for a univariate time series
{Xt }t∈T is defined as follows:
Xt+W = f (Xt , Xt−1 , . . . , Xt+W−1 |θ )

(1)

Here, f represents a mapping function with parameters θ
that need to be estimated within the model f . By utilizing
the time series {Xt }t∈T and considering W as the window
length of the timestamp, we aim to create a graph neural
network mapping model f . Assuming f as a neural network
mapping function (with a single hidden layer for simplicity),
our original equation transforms to:


D
W


Xt+W = θ0 +
θj g θ0j +
θij Xt+i−1
(2)
j=1

i=1

In this equation, D represents the number of nodes in the
hidden layer, g is an activation function, and θ0 , θj , θ0j , and
θij are all trainable parameters. This graph neural network
model, which extends conventional neural network models,
uses traditional time-series data for training. The historical data
is aligned with current data to identify θ within f , capturing
essential characteristics of standard time-series data flow.
For anomaly detection testing and evaluation, the function
f predicts data for the current timestamp. An IoDT system is
considered to be in an anomalous state at a given time if the
prediction error exceeds a predefined threshold.
We define A, a matrix representing spatial relationships
among IoDT nodes, and Xt ∈ RM×N , which consolidates
readings from multiple modalities across M drone nodes.
Given a timestamp window W, Xt , covering W timestamps,
along with A, yields:
X̃t+W = f (Xt , Xt+1 , . . . , Xt+W−1 ; A|θ )

(3)

4290

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

decoder reconstructs this into X  , mirroring the original data’s
format. The combination of Z and X  then passes through a
fully connected network and a softmax function to calculate
the probability of anomalies. The key equations are:
Z = fe (X; θe ), X  = fd (Z; θd )

 
y = Softmax FC Z, X 

Fig. 1. Illustration of IoDT’s multi-drone, multimodal data collection. It
shows drones acquiring various types of data, represented by M, such as
temperature and humidity.

The parameters (θ ) are fine-tuned by minimizing the root
mean square error between the predicted matrix X̃t+W and
the actual observations in matrix Xt+W . A ‘Score’ function
calculates inference scores, indicating the likelihood of anomalies in the system. A high prediction discrepancy leads to a
higher inference score, suggesting potential anomalies. If the
inference score at a specific timestamp exceeds a set threshold
η, it flags an anomaly. The threshold η is typically determined
by applying f to a validation dataset.
This research introduces a graph neural network model f and
a novel method for determining its parameters θ , considering
the topology of the IoDT system. By integrating data from
various nodes, modalities, and time instances, our approach
aims to accurately identify anomalies within the IoDT system’s
data flow.
B. Data Flow Model
In the Internet of Drone Things (IoDT), understanding the
interplay between different drones and data types demands a
unique IoDT data flow structure. Consider a network in the
IoDT spanning a specific area, with N drones equipped with
M sensors each, for monitoring environmental variables like
temperature, humidity, and CO2 levels. These drones use a
time synchronization approach for effective data sharing and
collection.
For real-time analysis of both past and current data, the
system utilizes a sliding window approach [34]. With the
present time marked as t and the window size as W, data
from the drones is collected over the interval {t − W − 1, t −
W, . . . , t − 1}, forming a tensor X ∈ RM×N×W . As new data
comes in, the window advances, turning the IoDT’s data flow
into a dynamic temporal network. In this approach, as seen
in Figure 1, every drone gathers time series data on a range
of parameters, including oxygen (O2 ), CO2 and temperature
(temp) levels.
C. Anomaly Detection Model
Figure 2 presents our IoDT anomaly detection approach,
centered on a Graph Neural Network (GNN) autoencoder,
building on the concepts of [22], [35]. The encoder fe and the
decoder fd in this autoencoder have the parameters θe and θd ,
respectively. Using dimension d, the encoder converts IoDT
data into a hidden layer representation Z. Subsequently, the

(4)
(5)

We train our methods using a two-stage process. In order
to recreate typical IoDT data patterns, the model first learns
the data distribution throughout the whole time series. In
the second stage, it is further trained with data incorporating
simulated anomalies, enhancing its capacity to differentiate
between normal and abnormal patterns at different times.
Further discussion on these training strategies appears in the
later sections.
D. Preprocessing Module
In the Internet of Drone Things (IoDT), where measurement
attributes vary widely, data standardization is essential to
maintain consistent scales. Uneven measurement scales can
skew analysis, either overstating or understating the importance of certain attributes. To counter this, we adopt Z score
normalization for our input tensor, as defined by:
 

Xij − μ Xij
 
(6)
X̃ij =
σ Xij
Here, the input tensor is denoted by X ∈ RM×N×W and
the data gathered by sensor i on drone j is indicated by Xij .
The mean and standard deviation of Xij are μ(Xij ) and σ (Xij ),
respectively. The multimodal data across drones is adjusted
using this Z score normalization approach to a standard
distribution with a mean of 0 and a standard deviation of 1,
harmonizing the diverse data readings.
To address the dynamic nature of IoDT environments,
where drone nodes exhibit mobility and network topology
may evolve, our graph neural network (GNN) model is
designed with adaptability and scalability in mind. GNNs are
particularly well-suited for dynamic networks due to their
ability to learn and update node representations based on the
changing structure of the graph. In the context of IoDT, as
drones move and the network topology changes, the GNN
model dynamically adjusts the node embeddings to reflect
new spatial relationships and connectivity patterns among
drones. This allows the anomaly detection process to remain
accurate and reliable even as drones enter or leave the network,
move within the environment, or when the data patterns they
generate evolve over time.
Furthermore, the model’s training process can be periodically updated with new data to refine the graph representations
and adapt to long-term changes in the IoDT environment. This
continual learning approach ensures that the model remains
effective in detecting anomalies in a changing environment.
Future enhancements will focus on improving the model’s
real-time adaptability to sudden changes in network topology
and exploring strategies for incremental learning that minimize
computational overhead while maintaining detection accuracy.

AKRAM et al.: DroneSSL: SELF-SUPERVISED MULTIMODAL ANOMALY DETECTION IN IoDT

4291

Fig. 2. Overview of the DroneSSL framework, processing IoDT’s time series data. It involves encoding this data into a hidden layer Z, then decoding
to reconstruct it as X  , and finally, employing a fully connected network using both the reconstructed output and encoder’s hidden layer to assess anomaly
probabilities in the system.

Fig. 3. A module for extracting spatial-temporal features from IoDT data, focusing on a single data type. It extracts temporal and spatial characteristics from
multiple drones’ data, resulting in a feature matrix that encapsulates the characteristics of multiple drones focusing on a single mode.

E. Encoder and Decoder
The encoder in our IoDT system comprises two primary
elements: a module for extracting spatiotemporal features from
drones based on individual data types, and an adaptive fusion
module for integrating these features.
In the IoDT setup, each data type forms a separate layer,
with Xi ∈ RN×W representing the data flow for modality
i, embodying multinode data streams of that modality. The
first step involves processing data through a module dedicated
to deriving spatial and temporal features for each drone,
specific to a single modality. This results in specialized spatiotemporal feature representations for each drone, respective
to the modality. After processing all modal branches, these
features are combined using adaptive fusion, facilitating the
extraction of intermodal correlations. Then, to handle longterm dependencies, a Gated Recurrent Unit (GRU) is utilized,
which serves as the foundation for the encoder’s hidden
layer. The decoder, structured similarly to the encoder, focuses
on reconstructing the original input from this hidden layer.
Detailed explanations of these components are provided in the
following sections.
1) Spatial-Temporal Feature Extraction Module: As illustrated in Figure 3, this module within the IoDT framework
is bifurcated into two parts: one for local temporal feature
extraction, and another for global spatial-temporal feature
extraction.

Adhering to [19]’s approach for time series feature extraction, our module for local temporal features employs a fully
connected neural network. It processes IoDT data Xij (the data
from drone j in mode i), a W-dimensional vector, to distill
it into a d/2-dimensional vector. This is achieved through a
series of layers, with K denoting the total number of layers.
The operations at each layer k involve the hidden layer output
H k , the initial data vector H 0 , the layer weights ak , biases
bk , and the output function g. The process transforms Xij ∈
RW into a reduced feature vector Xijl ∈ Rd/2 , as detailed in
Equations (7)-(9).
H 0 = Xij


H k = σ ak H k−1 + bk ,
 
Xijl = g H K

(7)
k ∈ 1, 2, . . . , K

(8)
(9)

For global spatial-temporal features, a Graph Neural
Network (GNN) is employed. It integrates mode i data Xij
from drone j with the spatial topology of the IoDT, considering
adjacent drone data to extract common global features. This
process reduces the data dimensionality to d/2 and is described
g
in Equation (10). Here, Xij results from combining adjacent
drone data {Xiu , {Hju }} and processing through GNN functions
GNN and fGNN . Our framework is adaptable to various GNN
types, optimizing anomaly detection in IoDT data.



g
, u ∈ N(j) (10)
Xij = GNN Xij , fGNN Xiu , Hju

4292

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

2) Adaptive Fusion Module: The IoDT framework incorporates an adaptive fusion module to integrate unique and
common features from different modalities of drones. The
procedure initiates by concatenating these distinct and shared
attributes, followed by the application of a modality-specific
fusion weight q to create a comprehensive feature set for each
drone, denoted as X:jc . Equation (11) describes this process,
where the fusion weight for the ith modality is qi ∈ Rd . During
training, these originally random weights are adjusted.
X:jc =

M



g
qi Xij Xijl

(11)

i=0

To better capture temporal features in IoDT data and address
long-term dependencies, the study incorporates dual Gated
Recurrent Unit (GRU) layers [36]. This leads to the creation
of the encoder’s hidden layer representation, denoted by h. As
discussed in Section IV-B, an autoencoder network is used for
data reconstruction and classification. The decoder, mirroring
the encoder’s architecture, reconstructs the initial input X  from
the hidden layer, as outlined in Equations (12) and (13).


Z = GRU X c , h
(12)
X  = decoder(Z)
(13)
F. Training
IoDT anomaly detection using deep learning on unlabeled
data mainly falls into two categories: unsupervised and selfsupervised learning techniques.
Unsupervised Methods: These methods focus on reconstructing normal input data or predicting future values, using
the resulting errors for anomaly detection. A key tool here is
the autoencoder, designed to encode and then decode input
data. Its goal is to learn the data distribution, minimizing
reconstruction errors to create a compact representation in its
hidden layer. Significant reconstruction errors indicate data
anomalies.
Self-Supervised Methods: To avoid overfitting, especially
with limited normal data samples, self-supervised learning is
used. This technique employs adversarial learning, distinguishing between real (positive) and fake (negative) samples, with
negative samples generated through methods like Generative
Adversarial Networks (GANs). Self-supervised learning essentially converts an unsupervised task into a supervised one.
Our IoDT framework employs a dual-phase training strategy. It combines the reconstruction efficiency of unsupervised
methods with the graph representation benefits of selfsupervised learning. The first phase acquaints the model with
normal data distribution, while the second involves introducing
anomalies to generate negative samples. This is crucial for the
model to learn to distinguish between artificial anomalies and
regular data.
1) Stage 1: Reconstruction in DroneSSL Training: The first
phase of DroneSSL training is focused on reconstructing
standard IoDT input data, as shown in (14). In this step, the
encoder is used to transform IoDT data X into a hidden layer
representation Z, and the decoder is used to reconstruct it.
The primary goal is to minimize the reconstruction error. The

Fig. 4. DroneSSL’s two-stage training process: initial reconstruction of standard input, followed by distinguishing anomalies. The visual representation
is simplified for clarity, showing data flow for a single modality from one
drone.

calculation for the loss function is as follows: l is the total
number of elements in X, and xi and xi are the elements in X
and X  respectively.
2
1 
xi − xi
l
l

Lrec =

(14)

i=0

2) Stage 2: Self-Supervised Learning in DroneSSL: The
second phase of DroneSSL training aims to teach the model
to identify anomalies in new data. This involves creating
negative samples by inserting anomalies into normal data. The
primary goal is to distinguish between abnormal and normal
data. Equation (15) defines the loss function, which aims to
reduce classification error. It takes two inputs: the projected
probability of having a positive sample (yp ) and the actual
label (y.


 
(15)
Lce = −y log yp − (1 − y) log 1 − yp
Figure 4 illustrates DroneSSL’s two-stage training process.
The training combines elements from (14) and (15) into an
overall training formula, given in (16). The number of training
epochs is indicated by n in this case. In order to evaluate the
present state of the system, the binary classification probability
is calculated during the inference phase using the classification
output branch.
L=

1
1
Lrec + 1 −
Lce
n
n

(16)

G. Enhancing Scalability: Strategy for Large-Scale IoDT
Scenarios
In IoDT applications with large datasets, the computational
and storage requirements increase significantly, especially
with the complex layers of Graph Neural Networks (GNNs).
This research presents an enhanced DroneSSL technique,
termed DroneSSL+, that integrates Piecewise Aggregate

AKRAM et al.: DroneSSL: SELF-SUPERVISED MULTIMODAL ANOMALY DETECTION IN IoDT

4293

strictly necessary parameters, avoiding the capture of irrelevant personal information. Furthermore, the deployment of
DroneSSL involves stakeholder engagement and transparency
measures, ensuring that individuals in monitored areas are
informed about the data collection practices and their rights.
By prioritizing ethical considerations and privacy protection,
DroneSSL aims to foster trust and acceptance among the
public, ensuring its ethical deployment in diverse environments
while safeguarding individuals’ privacy rights.
IV. A NALYSIS AND D ISCUSSION
Fig. 5.

DroneSSL+ optimization strategy in a large-scale IoDT scenario.

Approximation (PAA) with K-means clustering to overcome
these issues in large-scale IoDT.
K-means clustering, known for its efficiency and simplicity,
segments drones into clusters based on their spatial coordinates
C and a user-defined cluster number k, using Euclidean
distances. PAA, as per [37], is effective for reducing data
dimensionality while retaining key attributes. It compresses a
temporal data sequence Y = {Y1 , Y2 , . . . , Yn } of length n into a
shorter sequence Ȳ = {Ȳ1 , Ȳ2 , . . . , Ȳm } of length m, as shown
in (17).

A. Dataset

n

m
Yi =
n

mi


To validate the effectiveness of our anomaly detection
approach for the Internet of Drone Things (IoDT), several
experiments were conducted. For the experimental setup,
we utilized sensor data from the Internet of Drone Things
(IoDT). The hardware configuration included an AMD Ryzen
7 3700X CPU running at 3.6 GHz, coupled with an NVIDIA
GTX 1080 Ti GPU. The software framework was based on
Python, with PyTorch-1.9.0 serving as the primary tool for
model implementation and testing of various approaches. Data
visualization was managed using Python’s matplotlib library.
For enhanced computational efficiency, GPU acceleration was
enabled through CUDA version 11.2.

Yj ,

m≤n

(17)

j= mn (i−1)+1

Figure 5 displays the initial step of DroneSSL+, where
drones are grouped into k clusters via K-means based on
their locations. Each drone is positioned closer to its cluster
center than to others. Afterwards, the temporal data dimension
is reduced using PAA. The segmented dataset then undergoes independent training and inference on separate devices.
This division in DroneSSL+ significantly reduces model
parameters, enabling parallel processing on multiple devices
and improving efficiency. The temporal dimension reduction
converts D data points into fewer points (D1 ), thus lessening
the input data points and preserving essential information,
thereby enhancing system speed.
H. Ethical Considerations and Privacy
In the deployment of DroneSSL for anomaly detection
within the Internet of Drone Things (IoDT), ethical considerations and privacy concerns take on paramount importance,
especially given the system’s potential application in sensitive
and diverse environments. The utilization of drones equipped
with various sensors for monitoring purposes raises significant
privacy issues, as these devices can inadvertently collect
personal data without consent. To mitigate such risks, our
framework incorporates strict data handling and processing
protocols that align with established privacy regulations, such
as the General Data Protection Regulation (GDPR) in the
European Union. These protocols ensure that all data collected
by drones are anonymized and encrypted, preventing the
identification of individuals from the sensor data. Additionally,
DroneSSL employs mechanisms to limit data collection to

Our model’s validation employed the dataset from the
Intel Berkeley Research Lab (IBRL) [38], adapted to an
IoDT context. The original IBRL network had 54 sensors
measuring temperature, humidity, illumination, and voltage
from 28 February to 5 May 2004.
In our experiments, we used data from 51 drones, capturing three modalities (temperature, humidity, and voltage)
over 5000 moments between March 4 and March 9. This
created a 50 × 3 × 5000 data tensor. The training and test
sets were split 6:4, with 3000 time points for training and
2000 for testing, covering three modalities across 51 drones.
DroneSSL’s second stage employed self-supervised learning,
including negative sample creation through anomaly injection.
B. Anomaly Injection Methods
We tested five anomaly detection methods:
1) Scale Change: Multiplying IoDT data values by random
constants within the sliding window.
2) Negation: Inverting IoDT data values by a factor of −1
to create mirrored data.
3) Sudden Change: Significantly altering IoDT data values,
as shown in (18).


up
Xij (t) = Xij (t) ± Xi − Xidown , t ∈ {1, 2, . . . , τ } (18)
4) Intermodal Anomaly: Introducing anomalies that disrupt
correlations between different modalities.
5) Internode Anomaly: Injecting anomalies to break correlations in a single mode among multiple drones.
These experiments aimed to evaluate DroneSSL’s anomaly
detection capabilities in a complex IoDT environment, adapting traditional wireless sensor network methods to IoDT.

4294

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

C. Performance Assessment Metrics for DroneSSL
For evaluating the efficacy of the DroneSSL method
in detecting anomalies within the IoDT framework, we
focus on three primary metrics: the F1 score (F1), recall
(Rec) and precision (Prec), all calculated on the test
dataset.
Prec (Precision): Precision is the ratio of correctly predicted
abnormal samples to all samples that DroneSSL expected to
be abnormal.
Rec (Recall): Recall assesses the percentage of correctly
identified abnormal samples by DroneSSL compared to the
actual abnormal samples present in the dataset.
F1 Score: Precision and recall are seen in balance by
the F1 score, which is a harmonic mean of the two. It’s
derived from the confusion matrix elements: True Positives
(TP), True Negatives (TN), False Positives (FP), and False
Negatives (FN). TP indicates accurately detected anomalies,
FP represents incorrect anomaly detections, TN counts correct
identifications of normal instances, and FN refers to anomalies
that were not detected. The formula for F1 is F1 = 2 ×
Prec×Rec
Prec+Rec .
For testing, the test set is split into two subsets: one
with timestamps for anomaly injection (set-1) and another
without anomalies (set-2). Every test set undergoes a total of T
anomaly detection iterations. In each iteration, one of the four
anomaly injection methods is applied at a random timestamp in
set-1. Anomaly detection by DroneSSL is considered accurate
(TP) if it occurs within [t, t + delaystep] after an anomaly is
injected, where t is the timestamp and delaystep is the allowed
detection delay, set equal to the sliding window length W.
Missed detections are marked as FN.
For set-2, DroneSSL correctly identifying a normal point as
normal is labeled TN, and wrongly predicting an anomaly is
considered FP.
D. Sensitivity Analysis of the Model
To assess our model’s sensitivity to abnormal data, we
initially trained it using standard parameters and then tested
its response to anomalies with varying deviations from normal
data.
The outcomes of this sensitivity analysis are shown in
Figure 6. As previously mentioned in Section III, the deviation
factor for internode and intermodal anomalies is represented
by the symbol p. An increase in p signifies a smaller deviation
from normal data. The graph indicates that as p rises, the
model’s recall diminishes, suggesting the model is more adept
at distinguishing significant anomalies (lower p values) from
normal data.
After establishing the model’s capability to differentiate
normal and abnormal data, we fine-tuned its parameters to
optimize performance. The sliding window length W was
adjusted within the range {10, 15, 20, 25, 30}, the learning
rate lr was set within the range {0.00001, 0.00005, 0.0001,
0.0005}, the GRU hidden layer size was adjusted with the
range {8, 16, 32, 64}, and the anomaly deviation control
variable p was set to 40. The anomaly injection duration (te −
ts ) was fixed at 10. DroneSSL and baseline methods underwent

Fig. 6. Graph depicting the sensitivity test results, where a higher p value
corresponds to a smaller anomaly deviation from normal data.

multiple tests within these parameters to derive the best results,
which are detailed in the following sections.
E. Baseline Method Comparisons for DroneSSL
We examined our DroneSSL approach against three deep
learning-based anomaly detection techniques in order to assess
its effectiveness in the IoDT environment.
1) CNN-LSTM Model: An 8-layer CNN-LSTM model was
built using PyTorch, comprising a sequence of Conv2d,
MaxPool2d, LSTM, and FC layers. This model classifies
normal IoDT data as class 0 and data altered by anomalies
as class 1. Its four-dimensional tensor input, matching the
IoDT data structure, is formatted as [batch, modal_num,
drone_num, window_size]. However, unlike GNNs, CNNs
lack the capability to exploit the inherent topological features
of IoDT networks.
2) Anomaly Detection Using Multivariate Time-Series
Data: Zhao et al. [30] introduced a model combining
prediction-based and reconstruction-based approaches. This
method employs dual Graph Attention Networks (GATs)
to extract correlation features between modes and temporal
features over time. After concatenation, these features are
processed through a GRU, and the network bifurcates for
next-timestamp prediction and input data reconstruction. The
model, initially designed for single-node multimodal data,
was adapted to our multi-drone scenario. For our dataset,
51 separate Zhao et al. [30] models were developed, one for
each drone, with performance metrics representing an average
of these models’ results.
3) Anomaly Detection Using Multinode Multimodal TimeSeries Data: Zhang et al. [22] extended Zhao et al. [30]’s
approach by including spatial location information of multiple
drones. The model uses multiple GAT branches to extract
features from various modalities and time sequences across
drones. A GRU is utilized for long-term dependencies, and a
GAT captures the spatial position of drones. It predicts nexttimestamp values for all modes and drones, with anomalies
identified when the prediction error exceeds a certain threshold. When anomalous data greatly deviates from the usual data
distribution, this approach works especially well.
Table II presents the experimental results comparing the
performance of DroneSSL with other baseline methods in
IoDT anomaly detection. The results include precision (Prec),
recall (Rec), F1 score, and accuracy (Acc) for each method.

AKRAM et al.: DroneSSL: SELF-SUPERVISED MULTIMODAL ANOMALY DETECTION IN IoDT

Fig. 7.

4295

Point anomaly test visualization for DroneSSL.
TABLE II
C OMPARISON OF A NOMALY D ETECTION M ETHODS IN I O DT

The CNN-LSTM method exhibited lower performance metrics, primarily due to its limited ability to exploit the IoDT
network topology compared to GNNs. GNNs enable drones
to derive information from all adjacent drones, which proves
more effective than the CNN’s convolutional layers confined
to the kernel’s range. Zhao et al. [30], focusing on multimodal
data correlations, does not incorporate spatial location features
of drones, requiring separate model training for each drone.
Furthermore, Zhao et al. [30]‘s model sometimes experiences
training difficulties like gradient explosions, affecting its
performance relative to Zhang et al. [22] and DroneSSL.
Zhang et al. [22]‘s method, though utilizing GNNs and
GRUs for timestamp-based feature extraction, struggles with
long-term dependencies, especially in scenarios with larger
training sets than test sets. This limitation can impact its ability
to detect distant correlations, reducing its anomaly detection
accuracy.
In contrast, DroneSSL merges reconstruction-based models
with self-supervised learning for effective normal data feature
capture and graph representation learning generalization. It
employs GNNs for both global common node information
extraction and individual drone data analysis. DroneSSL supports various GNN types, with both GCN and GAT-based
approaches outperforming others. Specifically, GAT-based
DroneSSL achieves the highest overall performance, with
its F1 score surpassing Zhao et al. [30] by 4.9% and
Zhang et al. [22] by 8.7%.
F. Interpretability of DroneSSL
We ran a visual analysis on training and test data to confirm
that DroneSSL can comprehend normal data distribution and
detect anomalies. This involved looking at the reconstructed
data X  and the hidden layer representation Z for a particular
drone.

Point Anomaly Test: For the second modality from drone
47, an analysis of raw data over 5000 time points was
performed, as Fig. 7(a) illustrates. Test data is represented by
the green curve, while training data is shown by the purple
curve. Predicted values are displayed on the orange curve,
with a possible anomaly indicated by a spike. Notably, the
prediction curve’s multiple spikes to 1 might suggest either
misjudgments or unrecognized anomalies in the original data.
The response of DroneSSL to a purposefully created point
anomaly at the 500th moment in the test set is seen in Fig. 7(b),
which confirms the model’s capacity to identify significant
deviations from normal ranges by displaying a marked rise
in judgment values. Fig. 7(c) displays the alterations in the
hidden layer vector for the same modality and drone around
the 511th moment, where an anomaly was introduced. The
green line indicates the vector without anomalies, while
the purple line shows post-anomaly alterations, revealing a
distinct difference. Fig. 7(d) presents the reconstruction curves
with and without an anomaly at the 510th moment. The
normal input in this case is shown by the purple curve,
its reconstruction is shown by yellow, and the reconstruction post-anomaly is shown by brown. A notable numerical
shift in the reconstruction curve after the anomaly injection
demonstrates DroneSSL’s sensitivity to abrupt deviations from
normal data. These visual assessments affirm DroneSSL’s
efficiency in learning normal data patterns and its adeptness
in spotting and responding to anomalies within the IoDT
framework.
Contextual Anomaly Test: As seen in Fig. 8(a), we examined
5000 minutes of data from drone 45’s first modality in order
to further illustrate DroneSSL’s capacity to identify contextual abnormalities. The orange curve highlights anticipated
anomalies, whereas the purple curve shows training data and
the green curve indicates test data. DroneSSL’s response to
contextual anomalies inserted between test set moments 700–
1000, while adjacent drones exhibit similar declines, is shown
in Fig. 8(b). A subtle deviation from normal ranges was
introduced at the 850th moment, which DroneSSL successfully
identified as a contextual anomaly. Fig. 8(c) depicts changes in
the hidden layer vector for drone 45 around the 860th moment,
with the green line showing the vector without anomaly and
the purple line post-anomaly injection, highlighting a significant difference. Fig. 8(d) shows the reconstruction curves

4296

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Fig. 8.

Visualization of contextual anomaly detection in DroneSSL, showing data and prediction curves for drone 45.

Fig. 9.

Periodic anomaly test visualization for timestamps 150-180, showing DroneSSL’s response to injected anomalies.

Fig. 10.

Periodic anomaly test visualization for timestamps 1450-1480, highlighting DroneSSL’s ability to recognize periodic patterns in IoDT data.

before and after injecting the contextual anomaly at the 860th
moment. The numerical change in the reconstruction curve,
though less drastic than in point anomaly cases, confirms
DroneSSL’s sensitivity to subtle deviations from normal patterns.
Periodic Anomaly Test: This test evaluated DroneSSL’s
understanding of periodic normal data patterns. In the test
set data of drone 45, a unique form that resembled those in
the training set was added between moments 150-180 and
1450-1480. The results of the specific shape injection into
moments 150–180 are shown in Fig. 9. This shape introduces
a large anomaly, as shown in Fig. 9(b), which is accurately
detected by DroneSSL during the lag period. The hidden layer
vector and reconstruction curve changes at timestamp 183

are displayed in Fig. 9(c) and (d), respectively, illustrating
DroneSSL’s capability to identify and respond to the anomaly.
Fig. 10 displays outcomes of injecting the shape into moments
1450-1480. As seen in Fig. 10(b), since the injected shape
resembles the training set waveform and aligns with its
periodicity, DroneSSL does not classify it as an anomaly. This
response, along with the earlier results, showcases DroneSSL’s
proficiency in discerning periodic patterns in IoDT data.
Fig. 10(c) and (d) depict the hidden layer vector and reconstruction curve changes at timestamp 1483, illustrating slight
deviations but within acceptable ranges, leading DroneSSL
to not flag this instance as anomalous. These tests highlight
DroneSSL’s capacity to detect anomalies while respecting the
inherent periodic nature of normal IoDT data.

AKRAM et al.: DroneSSL: SELF-SUPERVISED MULTIMODAL ANOMALY DETECTION IN IoDT

TABLE III
L ARGE -S CALE I MPROVEMENT S TRATEGY W ITH D RONE SSL+

G. DroneSSL+ in Large-Scale IoDT Scenarios
In response to the computational and memory demands
of expanding Internet of Drone Things (IoDT) networks,
we introduce an advanced version of DroneSSL, termed
DroneSSL+ . This version integrates K-means clustering and
Piecewise Aggregate Approximation (PAA) for enhanced efficiency, as discussed in Section IV-F.
Two sets of experiments were conducted to assess
DroneSSL+ ’s time complexity performance. The first set
(Experiment 1) involved clustering the IoDT network and
running the DroneSSL framework on separate devices per
cluster, reducing model parameters and GPU usage. The
second set (Experiment 2) utilized PAA to compress the time
dimension of the dataset while maintaining a constant number
of clusters, performing anomaly detection at specified intervals
to further cut down on runs and time overhead.
The results, shown in Table III, reveal that increasing the
number of clusters leads to a slight decline in DroneSSL+ ’s
performance but significantly reduces the average testing
time. Notably, reducing the dataset size to 4/5 through PAA
improves performance, likely due to PAA’s efficiency in
preserving general data trends while eliminating some irregularities. However, more substantial reductions, such as to 2/5
of the original size, result in a marked performance drop, with
the F1 score falling to 70.4% despite a substantial decrease in
average testing time.
Therefore, striking a balance between performance and testing time efficiency is crucial, depending on the specific IoDT
application needs. Selecting an optimal number of clusters
and PAA reduction ratio is key to successfully implementing
DroneSSL+ in large-scale IoDT anomaly detection scenarios.
V. C ONCLUSION AND F UTURE W ORK
To sum up, this paper has introduced DroneSSL, an innovative anomaly detection framework that seamlessly integrates
spatial crowdsourcing with the Internet of Drone Things
(IoDT) and TinyML to address the complexities of environmental monitoring, notably in scenarios like Australian
bushfire management. By utilizing drones and unmanned
ground vehicles for data collection across inaccessible terrains,
DroneSSL embodies a cutting-edge approach that leverages
lightweight machine learning models for efficient and effective spatiotemporal analysis. This framework’s combination
of temporal feature extraction and a scalable Graph Neural
Network (GNN) architecture optimizes anomaly detection in
IoDT, demonstrating a significant improvement in performance

4297

metrics. DroneSSL’s successful application in challenging
environments not only highlights its potential in critical monitoring tasks but also underscores the transformative impact
of merging spatial crowdsourcing with advanced computational technologies. Looking ahead, the exploration of further
optimizations and the expansion of DroneSSL’s application
scope promise to enrich the IoDT landscape, paving the way
for groundbreaking developments in IoT edge computing and
environmental surveillance technologies.
Future enhancements to DroneSSL could significantly
enhance its efficacy and extend its applicability across a
wider range of Internet of Things (IoT) environments, addressing critical challenges such as computational efficiency and
real-time data processing. By integrating edge computing
and federated learning, DroneSSL could offer decentralized
anomaly detection capabilities, reducing latency and bandwidth usage while ensuring data privacy and security through
advanced encryption techniques. Additionally, expanding its
adaptability to various IoT domains, including industrial
IoT (IIoT) for predictive maintenance and smart cities for
urban monitoring, necessitates the development of flexible,
generalized models that can effortlessly learn from diverse
data types and sources. Incorporating transfer learning could
further streamline DroneSSL’s deployment across different
scenarios, minimizing the dependency on extensive labeled
datasets. Overcoming regulatory and standardization hurdles,
especially in drone airspace management, alongside ensuring
robust privacy and security measures, will be paramount
for DroneSSL’s broader implementation. Such advancements
promise to solidify DroneSSL’s position as a versatile, efficient
tool for monitoring and surveillance within the ever-evolving
IoT landscape, offering promising prospects for future research
and application in this domain.
Enhancing the validation of DroneSSL’s performance further, future work could explore a broader array of datasets,
specifically those capturing a wider range of real-world IoDT
applications, such as urban surveillance, environmental monitoring, and industrial inspections. Integrating datasets with
varying characteristics and challenges, such as different scales
of IoDT deployments and diverse anomaly types, would provide a more robust evaluation of DroneSSL’s adaptability and
efficacy across different scenarios. Additionally, incorporating
a wider range of performance metrics, such as detection
latency, scalability, and computational efficiency, alongside
precision, recall, and F1 score, would offer a more comprehensive assessment of the system’s overall performance. A
comparative analysis with industry standards and state-of-theart methods, particularly those deployed in real-world IoDT
applications, would further elucidate DroneSSL’s competitive
advantages, shedding light on its practical implications and
potential for widespread adoption.
R EFERENCES
[1] J. Akram, Z. Najam, and A. Rafi, “Efficient resource utilization in cloudfog environment integrated with smart grids,” in Proc. Int. Conf. Front.
Inf. Technol. (FIT), 2018, pp. 188–193.
[2] M. T. R. Khan, M. M. Saad, M. A. Tariq, J. Akram, and D. Kim,
“SPICE-IT: Smart COVID-19 pandemic controlled eradication over
NDN-IoT,” Inf. Fusion, vol. 74, pp. 50–64, Oct. 2021.

4298

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

[3] A. Tahir, A. Akram, A. Z. Kouzani, H. S. Munawar, J. Akram, and
M. P. Mahmud, “Cloud-and fog-integrated smart grid model for efficient
resource utilisation,” Sensors, vol. 21, no. 23, p. 7846, 2021.
[4] J. Akram, M. Umair, R. H. Jhaveri, M. N. Riaz, H. Chi, and S. Malebary,
“Chained-drones: Blockchain-based privacy-preserving framework for
secure and intelligent service provisioning in Internet of Drone Things,”
Comput. Elect. Eng., vol. 110, Sep. 2023, Art. no. 108772.
[5] J. Akram, A. Akram, R. H. Jhaveri, M. Alazab, and H. Chi, “BCIoDT: Blockchain-based framework for authentication in Internet of
Drone Things,” in Proc. 5th Int. ACM Mobicom Workshop Drone Assist.
Wireless Commun. 5G Beyond, 2022, pp. 115–120.
[6] A. Tahir, H. S. Munawar, M. Adil, S. Ali, A. Z. Kouzani, and
M. P. Mahmud, “Automatic target detection from satellite imagery using
machine learning,” Sensors, vol. 22, no. 3, p. 1147, 2022.
[7] A. W. A. Hammad, S. T. Waller, and M. Mojtahedi, J. Akram, and
H. S. Munawar, “Metaheuristics for capacitated vehicle routing for flood
victims evacuation,” in Proc. AIP Conf. Proc., 2023, Art. no. 30010.
[8] S. I. Khan, F. Ullah, H. S. Munawar, J. Akram, and B. J. Choi, “Droneas-a-service (DaaS) for COVID-19 self-testing kits delivery in smart
healthcare setups: A technological perspective,” ICT Exp., vol. 9, no. 4,
pp. 748–753, Aug. 2023.
[9] H. S. Munawar, Z. Gharineiat, J. Akram, and S. I. Khan, “A framework
for burnt area mapping and evacuation problem using aerial imagery
analysis,” Fire, vol. 5, no. 4, p. 122, 2022.
[10] H. S. Munawar, F. Ullah, D. Shahzad, A. Heravi, J. Akram, and
S. Qayyum, “Civil infrastructure damage and corrosion detection: An
application of machine learning,” Buildings, vol. 12, no. 2, p. 156, 2022.
[11] J. Akram, A. Javed, S. Khan, A. Akram, H. S. Munawar, and W. Ahmad,
“Swarm intelligence based localization in wireless sensor networks,” in
Proc. 36th Annu. ACM Symp. Appl. Comput., 2021, pp. 1906–1914.
[12] H. S. Munawar, A. Z. Kouzani, J. Akram, and M. P. Mahmud,
“Using adaptive sensors for optimised target coverage in wireless sensor
networks,” Sensors, vol. 22, no. 3, p. 1083, 2022.
[13] J. Akram, S. Malik, S. Ansari, H. Rizvi, D. Kim, and R. Hasnain„
“Intelligent target coverage in wireless sensor networks with adaptive
sensors,” in Proc. IEEE 92nd Veh. Technol. Conf. (VTC-Fall), 2020,
pp. 1–5.
[14] H. Fei and G. Li, “Abnormal data detection algorithm for WSN based on
k-means clustering,” Comput. Eng., vol. 41, no. 7, pp. 124–128, 2015.
[15] D. Xiaoou, Y. Shengjian, W. Muxian, W. Hongzhi, G. Hong, and
Y. Donghua, “Anomaly detection on industrial time series based on
correlation analysis,” J. Softw., vol. 31, no. 3, pp. 726–747, 2020.
[16] D. Li, D. Chen, B. Jin, L. Shi, J. Goh, and S.-K. Ng, “MAD-GAN:
Multivariate anomaly detection for time series data with generative
adversarial networks,” in Proc. Int. Conf. Artif. Neural Netw., 2019,
pp. 703–716.
[17] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly detector for
robot-assisted feeding using an LSTM-Based variational autoencoder,”
IEEE Robot. Autom. Lett., vol. 3, no. 3, pp. 1544–1551, Jul. 2019.
[18] W. Yu and C. Zhao, “Broad convolutional neural network based
industrial process fault diagnosis with incremental learning capability,”
IEEE Trans. Ind. Electron., vol. 67, no. 6, pp. 5081–5091, Jun. 2020.
[19] Y. Zhang, J. Wang, Y. Chen, H. Yu, and T. Qin, “Adaptive memory
networks with self-supervised learning for unsupervised anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12068–12080,
Dec. 2023.

[20] L. Zhao, M. Gao, and Z. Wang, “ST-GSP: Spatial-temporal global
semantic representation learning for urban flow prediction,” in Proc.
15th ACM Int. Conf. Web Search Data Min., 2022, pp. 1443–1451.
[21] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer:
Time series anomaly detection with association discrepancy,” 2021,
arXiv:2110.02642.
[22] Q. Zhang, M. Ye, and X. Deng, “A novel anomaly detection method
for multimodal WSN data flow via a dynamic graph neural network,”
Connect. Sci., vol. 34, no. 1, pp. 1609–1637, 2022.
[23] Z. Rong, L. Weiping, and M. Tong, “Review of deep learning,” Chin.
J. Inf. Control, vol. 47, no. 4, pp. 385–397, 2018.
[24] W. L. Hamilton, Z. Ying, and J. Leskovec, “Inductive representation
learning on large graphs,” in Proc. Adv. Neural Inf. Process. Syst.,
vol. 30, 2017, pp. 1–11.
[25] T. N. Kipf and M. Welling, “Semi-supervised classification with graph
convolutional networks,” 2016, arXiv:1609.02907.
[26] P. Veličković, G. Cucurull, A. Casanova, A. Romero, P. Lio, and
Y. Bengio, “Graph attention networks,” 2017, arXiv:1710.10903.
[27] K. Ding, J. Li, R. Bhanushali, and H. Liu, “Deep anomaly detection on
attributed networks,” in Proc. SIAM Int. Conf. Data Min., 2019, pp. 1–9.
[28] Z. You, X. Gan, L. Fu, and Z. Wang, “GATAE: Graph attention-based
anomaly detection on attributed networks,” in Proc. IEEE/CIC Int. Conf.
Commun. China (ICCC), 2020, pp. 389–394.
[29] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. AAAI Conf. Artif. Intell., vol. 35,
2021, pp. 4027–4035.
[30] H. Zhao et al., “Multivariate time-series anomaly detection via graph
attention network,” in Proc. IEEE Int. Conf. Data Min. (ICDM), 2020,
pp. 841–850.
[31] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Disc. Data Min., 2020,
pp. 3395–3404.
[32] Y. Liu, Z. Li, S. Pan, C. Gong, C. Zhou, and G. Karypis, “Anomaly
detection on attributed networks via contrastive self-supervised learning,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 6,
pp. 2378–2392, Jun. 2022.
[33] G. Jiayan, L. Ronghua, Z. Yan, and W. Guoren, “Graph neural network
based anomaly detection in dynamic networks,” J. Softw., vol. 31, no. 3,
pp. 748–762, 2020.
[34] M. Datar, A. Gionis, P. Indyk, and R. Motwani, “Maintaining stream
statistics over sliding windows,” SIAM J. Comput., vol. 31, no. 6,
pp. 1794–1813, 2002.
[35] M. Ye, Q. Zhang, X. Xue, Y. Wang, Q. Jiang, and H. Qiu, “A novel
self-supervised learning-based anomalous node detection method based
on an autoencoder for wireless sensor networks,” IEEE Syst. J., vol. 18,
no. 1, pp. 256–267, Mar. 2024.
[36] J. Chung, C. Gulcehre, K. Cho, and Y. Bengio, “Empirical evaluation
of gated recurrent neural networks on sequence modeling,” 2014,
arXiv:1412.3555.
[37] E. Keogh, K. Chakrabarti, M. Pazzani, and S. Mehrotra, “Dimensionality
reduction for fast similarity search in large time series databases,” Knowl.
Inf. Syst., vol. 3, pp. 263–286, Aug. 2001.
[38] S. Madden, P. Bodik, W. Hong, C. Guestrin, M. Paskin, and R. Thibaux.
“Intel lab data.” Intel Berkeley Res. lab. 2004. [Online]. Available: http://
db.csail.mit.edu/labdata/labdata.html
PAPER_TEXT
