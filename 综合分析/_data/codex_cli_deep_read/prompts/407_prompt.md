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
# [407] Dual Temporal Masked Modeling for KPI Anomaly Detection via Similarity Aggregation
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
编号：407
题名：Dual Temporal Masked Modeling for KPI Anomaly Detection via Similarity Aggregation
年份：2024
DOI：10.1109/tnsm.2024.3486167
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2024.3486167.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：其他AI安全与跨域异常检测、入侵检测与网络异常检测
相关性：中相关，分数 7
已有代码状态：已下载；GT-DMASA -> source\GT-DMASA

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\407.txt
- 原始字符数：67340
- 本次发送字符数：67340
- 是否截断：False

代码包：
- 仓库：GT-DMASA
  - URL：https://github.com/colaudiolab/GT-DMASA
  - 状态：downloaded
  - 本地目录：source\GT-DMASA
  - 顶层结构：RevIN.py、args.py、classification.py、combine_all_scores.py、dataset.py、datautils.py、loss.py、main.py、metrics/、model/、preprocessData.py、process.py、sr/、visualize.py
  - 主要语言：Python:40
  - README 标题：
  - README 运行线索：
  - 关键文件：{"推理/演示入口": ["main.py"], "数据处理入口": ["dataset.py", "preprocessData.py", "process.py", "metrics/vus/models/feature.py"], "模型定义": ["model/layers.py"], "评估/测试入口": ["metrics/evaluate_utils.py", "metrics/evaluator.py"]}
  - 数据集线索：MSL、SMAP、SMD、SWAT、TOR、WADI、msl、smap、smd、swat、tor

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

317

Dual Temporal Masked Modeling for KPI Anomaly
Detection via Similarity Aggregation
Ting Yu , Zijian Gao , Kele Xu , Xu Wang , Peichang Shi , Bo Ding , and Dawei Feng

Abstract—With the expanding scale of current industries,
monitoring systems centered around Key Performance Indicators
(KPIs) play an increasingly crucial role. KPI anomaly detection
can monitor the potential risks according to KPI data and has
garnered widespread attention due to its rapid responsiveness
and adaptability to dynamic changes. Considering the absence
of labels and the high cost of manual annotation of KPI
data, the self-supervised approaches are proposed. Among them,
mask modeling methods draw great attention and can learn
the intrinsic distribution of data without relying on prior
assumptions. However, conventional mask modeling often overlooks the examination of relationships between unsynchronized
variables, treating them with equal importance, and inducing
inaccurate detection results. To address this, this paper proposes
a Dual Masked modeling Approach combined with Similarity
Aggregation, named DMASA. Starting from a self-supervised
approach based on mask modeling, DMASA incorporates spectral residual techniques to explore inter-variable dependencies
and aggregates information from similar data to eliminate
interference from irrelevant variables in anomaly detection.
Extensive experiments on eight datasets and state-of-the-art
results demonstrate the effectiveness of our approach. Our code
is available at https://github.com/colaudiolab/GT-DMASA.
Index Terms—Anomaly detection, key performance indicators,
self-supervised learning, monitoring.

I. I NTRODUCTION
N CONTEMPORARY industrial landscape, the continuous expansion of infrastructure, and the proliferation of
sensors underscore the significance of monitoring systems.
Employing monitoring systems is crucial for ensuring the
continuous and reliable operation of diverse systems, including financial systems [1], [2], Internet-based online service
systems [3], [4], and critical infrastructures such as network
systems [5], [6] and water treatment facilities [7]. For example, Key Performance Indicators (KPIs), in the context of
network security, encompass a wide array of data points, such
as login failures, unusual data transfers, and unauthorized
access attempts, which are vital for detecting anomalies that
could signify security breaches or system irregularities. This

I

Received 27 January 2024; revised 30 July 2024 and 19 October 2024;
accepted 19 October 2024. Date of publication 24 October 2024; date of
current version 14 March 2025. This paper is Supported by the National Key
Research and Development Program of China (No. 2021ZD0112904). The
associate editor coordinating the review of this article and approving it for
publication was Y. Diao. (Ting Yu and Zijian Gao contributed equally to this
work.) (Corresponding author: Kele Xu.)
The authors are with the College of Computer, National University of
Defense Technology, Changsha 410073, China, and also with the State Key
Laboratory of Complex & Critical Software Environment, Beihang University,
Beijing 100191, China (e-mail: xukelele@163.com).
Digital Object Identifier 10.1109/TNSM.2024.3486167

is essential for preventing potential risks, mitigating economic
losses, and maintaining overall safety [8]. Common monitoring
techniques encompass the utilization of KPIs and the analysis
of logs and trace data. Considering the dynamic nature and
time sensitivity of these systems, many opt for monitoring
strategies centered around KPIs.
KPIs, often time series data, face anomaly detection challenges due to scarce labeled data and high labeling costs
in large-scale systems [9]. Consequently, many KPI anomaly
detection algorithms resort to unsupervised methods, assuming
anomalies are hard to reconstruct or predict such as [10]
and [11]. The disparity between the reconstructed or predicted
data and the original data is utilized as the anomaly score
and performs well under the assumption of Gaussian noise.
Performance can falter with complex, non-Gaussian noise [12],
especially in fluctuating time series data where differentiating anomalies is tough. Hence, some methods attempt to
incorporate certain supervised information, as demonstrated
by Huang et al. [13], who combine active learning and
variational autoencoders to boost accuracy. However, these
approaches necessitate a prior hypothesis of the data. A
more universal and convenient choice would be a method
capable of autonomously extracting features from the data
itself.
Defining anomalies is intricate, often involving outliers
with unusual data patterns [14] that necessitate contextual
consideration [15]. For example, seasonal variations in power
system operations can affect anomaly assessment. A comprehensive evaluation, including frequency domain insights,
is crucial. Microsoft [4] employs spectral residual for processing one-dimensional KPIs, introducing frequency domain
information to aid in anomaly identification. Park et al. [16]
refine the Fast Fourier Transform (FFT) by computing only
a subset of Fourier coefficients to expedite computation. The
incorporation of frequency domain information contributes to
enhancing detection effectiveness.
Additionally, monitoring data’s multidimensionality introduces complex interdependencies among time and indicator
dimensions [17]. Taking the IT operations domain as an
example, as depicted in Figure 1, similar indicator types like
CPU usage and load show related patterns, yet many methods
incorrectly equate their correlation with dissimilar indicators
such as disk and database metrics. Especially in anomaly
detection, not all indicators exhibit anomalies simultaneously.
Given the multitude of metrics in monitoring systems, treating
various indicators equally may result in the features of indicators undergoing significant changes being submerged within
numerous data points where no substantial changes have

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1932-4537 
See https://www.ieee.org/publications/rights/index.html for more information.

318

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

Fig. 1.
Partial indicators obtained from an entity within the Internet
monitoring system. The segments highlighted in red denote anomalies. Not
all metrics are in an anomalous state when anomalies occur. The variables
indicated by red arrows have experienced anomalies, while those indicated
by green arrows have not exhibited significant changes. In particular, the
Transformer structure facilitates extensive information exchange among different variables. Treating all variables equally may result in the changes occurring
in anomalous indicators being averaged, potentially making it challenging to
identify anomalous states comprehensively.

occurred, hindering timely anomaly capture. Exploring the
correlations between variables and mitigating the interference
of irrelevant variables on those experiencing anomalies can
contribute to enhancing detection accuracy.
To address the challenges mentioned earlier, we propose the
KPI anomaly detection method DMASA. First, the method
tackles the issue of limited labels in KPI data by using selfsupervised mask modeling. In contrast to contrastive learning,
relying on prior assumptions and may introduce inductive
bias, mask modeling excavates information from the data to
learn richer representations with better generality. Secondly, it
introduces frequency-domain information to identify anomalies from multiple perspectives based on spectral residual,
which highlights anomalies by accentuating deviations from
the frequency domain mean and enhances detection accuracy
and timeliness. This helps the model in rapidly identifying
the starting point of anomalies and capturing them earlier.
Additionally, the distinct boundaries facilitate the observation
of whether anomalies occur simultaneously across different
variables.
Furthermore, treating all variables as equivalent may result
in interference of irrelevant variables. Especially for models
employing the Transformer method, akin to the “oversmoothing” issue [18], with the stacking of Transformer layers,
variables tend to become increasingly similar, implying that
local anomalous trends are flattened. Thus, DMASA introduces similarity aggregation to segregate irrelevant variables,
preventing the dilution of anomaly signals and ensuring that
only related variables influence the detection process. This
targeted approach helps maintain the clarity of anomaly trends

across variables. Our main contributions can be distilled to the
following points:
1. We introduce a novel anomaly detection approach that
integrates mask modeling to adaptly capture the inherent structure of KPI data through self-supervised learning, overcoming
the challenge of sparse labeling.
2. By utilizing spectral residual in conjunction with
frequency-domain insights, our method bolsters the identification of anomalies, allowing for prompt detection and precise
delineation of anomalous patterns.
3. Our model incorporates similarity aggregation to segregate irrelevant variables, ensuring that only closely related
variables contribute to the reconstruction process. This refines
the detection of anomalies without being obscured by unrelated data.
4. The vast majority of state-of-the-art experimental results
obtained on eight datasets demonstrate the effectiveness and
competitiveness of our proposed method.
The remaining sections of this paper are organized as follows. Section II provides a concise overview of KPI anomaly
detection, the utilization of self-supervised methods in time
series anomaly detection, and the application of Transformers
in time series analysis. In Section III, we provide a detailed
introduction to our DMASA method. Section IV comprehensively outlines the experimental details and analyzes the results
of our approach. The article culminates with a conclusion that
encapsulates our findings, contributions, and future works.
II. R ELATED W ORK
Operation and maintenance monitoring system analysis data
comprise KPI data, logs, traces, and other relevant information,
and KPI data draws widespread attention due to its capacity to
effectively address dynamic changes in complex systems and
facilitate prompt responses. First, we review self-supervised
methods for unlabeled KPI data. Furthermore, recognizing the
predominance of masking and predictive techniques within the
Transformer framework in current self-supervised methods, we
offer a comprehensive review of their application to time series
data. Subsequently, we delve into the specifics of KPI anomaly
detection, self-supervised methods for time series anomaly
detection, and the utilization of Transformer-based strategies
in time series analysis.
KPI Anomaly Detection: KPI data fundamentally is continuous time series data. Consequently, we will review methods
designed for anomaly detection in time series data. They can
be broadly categorized into statistical approaches, classical
machine learning algorithms, and deep learning methods.
Statistical methods, including mean-based approaches, feature
prominently in this domain, with classic methods such as
moving average [19] and Autoregression [20], autoregressive integrated moving average, and exponentially weighted
moving average [21] being extensively explored. Classical
machine learning algorithms, such as K-means [22], support
vector machines [23], GBRT [24], and Gaussian Mixture
Models [25], have also found applications. Deep learning
methods encompass various network structures, including
autoencoders [26], variational autoencoders (VAE) [27],
temporal convolutional networks [28], recurrent neural

YU et al.: DUAL TEMPORAL MASKED MODELING FOR KPI ANOMALY DETECTION VIA SIMILARITY AGGREGATION

319

Fig. 2. DMASA network structure. Transformer Structure Combining Similarity Aggregation (Left): Following spectral residual processing, the unmasked
sequence learns similarity relationships and embeddings. The masked sequence segment acquires hidden layer data through one-dimensional convolution.
Both components are then integrated and fed into the Transformer block, where the attention mechanism incorporates the learned similarity relationships for
information fusion. The sequence is ultimately reconstructed after this process.

networks (RNN) [29], [30], long short-term memory networks
(LSTM) [31], graph neural networks [7], and Transformers.
These methods operate under both supervised and unsupervised training paradigms. Supervised methods include
EGADS [32] and Opprentice [33], while prevalent unsupervised methods include OmniAnomaly [29], GDN [7],
TranAD [34], and Anomaly Transformer [35].
Self-Supervised Anomaly Detection Methods for Time
Series: KPIs are predominantly characterized by unlabeled
time series data. Self-supervised methods excel at distilling
meaningful information from extensive data, thereby providing
a robust representation for further analytical tasks. In the
context of time series anomaly detection, self-supervised techniques predominantly harness contrastive learning strategies.
For example, AnomalyBERT [36] defines and employs four
types of methods to synthesize anomalous values, distinguishing positive and negative samples by replacing certain data
with anomalous data. TimeAutoAd [37] uses three different
strategies to augment training data for generating pseudonegative time series and utilizes self-supervised contrastive
loss to differentiate between original and generated time
series. CSL [38] utilizes a shapelet-based encoder, incorporating multi-grained contrasting, multi-scale alignment, and a
data augmentation library to learn time series features in a
comprehensive manner. CTAD [39] incorporates seven types
of general time-series data augmentation methods from the
perspectives of variables and points, integrating a one-class
learning approach into the contrastive learning loss. Despite
the promising results of contrastive learning methods, they
are not without limitations. The introduction of inductive
bias based on researchers’ prior assumptions can lead to
performance inconsistencies when applied to time series data
with different characteristics, as seen in the augmentation
strategies employed by AnomalyBERT and TimeAutoAd.
However, when transferred to time series problems in other
domains with inconsistent data characteristics and prior
assumptions, model performance can significantly decline.
Transformer Architecture for Time Series Analysis:
Transformers have demonstrated remarkable success

in handling sequential data, including text and audio.
Consequently, they have attracted considerable attention
from researchers in the time series domain. Approaches like
FEDformer [40] and PatchTST [41] have shown progress in
time series prediction. In the realm of time series anomaly
detection, Anomaly Transformer [35], AnomalyBERT [36],
DCdetector [42], and others have achieved notable results.
The application of Transformers in both prediction and
anomaly detection signifies their versatility and effectiveness
in handling diverse time series tasks.
III. A PPROACH
A. Notation
KPI anomaly detection involves collecting metrics from
monitored systems, with the aim of analyzing whether the
system is in an abnormal state. Let d represent the number of variables and T1 denote the length of the training
data. We train on the given unlabeled KPI data X  train =
(x1 , x2 , . . . , xi , . . . , xT1 ). For evaluation, we use the test set
Xtest for unsupervised assessment. We assess the model’s
performance by comparing its predictions with the test labels
Ytest = (y1 , y2 , . . . , yi , . . . , yT2 ), where yi ∈ {0, 1}. Here, 0
indicates a normal state and 1 indicates an abnormal state.
B. Overall Framework
Our approach employs a self-supervised approach grounded
in masked modeling to distill essential features from KPI data.
Recognizing that KPI changes may not be synchronous across
variables, our framework is designed to capture the intervariable relationships, which is crucial for reducing the impact
of irrelevant variables on the anomaly detection process. To
achieve this, we integrate the learning of similarity relations
and apply spectral residual methods to enhance the understanding of inter-variable dynamics and emphasize temporal
changes.
As depicted in Figure 2, our model initiates with the spectral
residual enhancement of the data, which is then merged with
the original sequence. This processed data is directed into

320

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

two parallel components: Similarity Relation Learning and
Random Masking. The Similarity Relation Learning module
is tasked with identifying the relationships between variables,
while the Random Masking module, following the application
of random masks, is directed into a one-dimensional convolutional network to project the input data effectively. The outputs
of these components are then consolidated and channeled
into the Transformer module, where the similarity relation
insights are deployed to modulate self-attention mechanisms.
This strategic integration ensures that the model focuses on
relevant connections between variables. This process is the
reconstruction of the sequence, which is refined through minimizing reconstruction error, thereby optimizing the network’s
performance.
In the subsequent sections, we will delve deeper into the
intricacies of each component and elucidate their synergistic
contribution to the anomaly detection framework.
C. Enhancing Data With Spectral Residual
Anomalies, by nature, present a complex challenge to define
and detect within data sets. In the context of KPI anomaly
detection, while a certain degree of detection latency (the
time lag between the anomaly’s actual occurrence and its
identification) might be tolerated, our goal is to minimize this
delay to ensure the timeliness of monitoring systems. To boost
the detection capabilities, we introduce the spectral residual
method, which combines spectral information to amplify
the deviation between each data point and the frequencydomain mean of its preceding data within a window. It is
well-established that the frequency attributes of normal data
differ markedly from those of anomalous data. When an
anomaly emerges, the spectral residual method accentuates the
divergence of the affected segment from the normal segment
that precedes it, in terms of the frequency-domain mean.
This amplification allows our network to more accurately
and swiftly detect the onset of an anomaly, thereby reducing
detection latency.
In multivariate scenarios, the spectral residual method
further aids in identifying anomalies by accentuating their fluctuations, which in turn promotes the clustering of these points.
This clustering facilitates the recognition of analogous patterns
across variable fluctuations. Synchronous anomalies across
variables suggest a heightened correlation between them,
which is beneficial for our subsequent similarity aggregation
processes. Our approach considers each of the d dimensions
in the multivariate data as an independent univariate dataset,
applying spectral residual operations to each one individually.
By adding the spectral residual to the original data, we
effectively increase the deviation of each data point, enhancing
the model’s sensitivity to anomalies. This methodical enhancement of the data not only refines the detection process but
also enriches the model’s ability to discern meaningful patterns
within the data. The process is shown in Equation (1):


Xtrain = X  train + SR X  train ,

(1)

where the process of SR is described by Equations (2)-(5):

Fig. 3.
Example of spectral residual results. The red points indicate
anomalous data points. Following the application of spectral residual, the
anomalous points are magnified.

A(f ) = Amplitude(F(x)),

(2)

P (f ) = Phase(F(x)),
R(f ) = log(A(f )) − Ip (f ) · log(A(f )),




S (x) = F−1 (exp(R(f ) + iP (f ))),

(3)
(4)
(5)

where F and F−1 denote Fourier Transform and Inverse
Fourier Transform respectively. x is the input sequence of
shape n × 1. A(f ) is the amplitude spectrum of sequence
x. P(f ) represents the corresponding phase spectrum of the
sequence. Ip (f ) is a local average filter of a p × p matrix,
in which each element is p12 , to convolute the input sequence
log(A(f )).
Following spectral residual operations, the data exhibits
the characteristics illustrated in the accompanying Figure 3.
As observed, spectral residual amplifies the deviation of
data from the frequency domain baseline. If a point is an
anomaly, it will exhibit more pronounced behavior along the
temporal dimension. Additionally, if multiple variables change
simultaneously at a certain moment, it indicates a potentially
closer relationship among them. The spectral residual method
amplifies such changes, thereby distinguishing them from
other variables that do not change synchronously, aiding in
capturing the connections between variables.
D. Partitioning Variables Through Similarity Relationships
For KPI data, each dimension encapsulates a distinct metric
or sensor, with each KPI exhibiting its own unique traits. The
interplay among various features is often intricate. Consider a
software operation system, where CPU-related metrics might
fluctuate independently of database metrics. Similarly, in a
water treatment system, the levels indicated by water level
sensors may not consistently align with those of temperature
sensors. In the realm of anomaly detection, it’s crucial to
recognize that anomalies across different variables are not
uniformly synchronized. Applying a one-size-fits-all approach
to variable analysis could potentially obscure the distinctive
features of variables that exhibit anomalies, especially when
other variables show no signs of anomalies. To counteract
this, it’s imperative to understand and leverage the underlying

YU et al.: DUAL TEMPORAL MASKED MODELING FOR KPI ANOMALY DETECTION VIA SIMILARITY AGGREGATION

dependencies between variables. This understanding allows
for the aggregation of similar metrics, thereby minimizing the
interference from irrelevant variables.
To achieve this, our methodology employs a learning
process that discerns and respects the complex relationships
between variables. By doing so, it ensures that the anomaly
detection process is both sensitive and specific, acknowledging
the unique characteristics of each KPI while identifying the
subtleties of anomalies within their respective contexts. This
approach is essential for developing a nuanced and effective
anomaly detection system that can accurately interpret and
respond to the multifaceted nature of KPI data.
Inspired by the graph neural network approach GDN [7],
we employ a graph adjacency matrix to describe variable relationships. First, if we have prior knowledge about relationships
between different metrics, we can incorporate this knowledge
into the graph structure. Let Aij represent the adjacency matrix
indicating relationships between different variables, where
Aij = 1 indicates an edge from variable i to j, signifying an
influence from variable i to j. However, in many cases, we
may not have prior knowledge about the relationships between
variables. We need to learn the proximity information from the
data. Initially, we utilize Embedding(·) network to characterize
each dimension of the variable x and get the embedding ei ,
dmodel

ei ∈ R

, for i ∈ {1, 2, . . . , d }.

321

in the temporal dimension. Random masking involves independently selecting data in the time dimension with a proportion
r for masking across different variable dimensions. That is,
a proportion r of the data is masked in the time dimension,
and variables at the same time may not necessarily be
simultaneously masked across different variable dimensions.
We take the window data X = [xt , xt+1 , . . . , xt+w −1 ] as
input. Let the mask matrix be denoted as M, which is a binary
matrix with elements 0 and 1. The proportion of 0s in each
row is r, and it is of the same dimension as X. After applying
the mask, the updated representation X is as shown in the
Equation (9):
X := M  X ,

(9)

where  represents element-wise multiplication. The
one-dimensional convolution in the temporal dimension
captures dependencies in the time series while also serving as
a method for input projection. It is important to note that we
process each variable separately, and the 1D-CNN is solely
used to capture dependencies in a single dimension, as shown
in the Equation (10),
X  = 1D − Conv (X ).

(10)

(6)

Then, assess the proximity between variables by measuring
cosine similarity,
ei ej
  , for j = i .
(7)
||ei || · ej 
Aji = 1, j ∈ Top − k ({vki : k ∈ {1, 2, . . . , d }\{i }}). (8)
vji =

We calculate the cosine similarity between embeddings for
each pair of variables, and for each variable, we select the
k variables corresponding to the embeddings with the highest
similarity as neighbors. This indicates that these k neighbors
are the variables most likely to influence it. The learning of
embeddings ei and the adjacency matrix Aij will be utilized
in subsequent information fusion using Transformer.
E. Self-Supervised Learning via Mask Modeling
KPI data, as a kind of time series data, exhibits temporal
redundancy. As we claimed, some reconstruction methods
assume that anomalies are challenging to identify based on
reconstruction errors. However, the potent fitting capability of
neural networks and the temporal redundancy in time series
data make the reconstruction of anomalies less challenging.
Conventional contrastive learning methods construct positive
and negative samples and introduce inductive bias, limiting its
universality and performance in various scenarios, as well as
its transferability and generalization capabilities. To deal with
it, we introduce mask modeling, starting from the distribution
of the data itself, which achieves excellent results without
additional assumptions about the data.
In this process, the primary steps of the model involve
random masking and one-dimensional convolution processing

F. Isolating Irrelevant Variables Through Similarity
Aggregation
Transformer-based models excel in sequence tasks and
are prevalent in sequence modeling. Yet, a common challenge arises with deep Transformers: as layers accumulate,
information fusion can homogenize variables, obscuring
anomalous trends. In cases where only a subset of system
components malfunction, while others remain normal, the
extensive interaction can mask the anomalies, leading to a false
sense of normalcy and potential false negatives in monitoring.
To address this, we refine the Transformer architecture
by limiting information fusion to closely related variables,
thereby preserving the distinctiveness of anomalies. We integrate the Transformer with learned similarity relations to
selectively fuse information, enhancing the model’s ability to
detect anomalies without being confounded by normal data
variability. This nuanced approach ensures that only pertinent
variables influence the anomaly detection process, improving
the model’s accuracy and reliability.
In comparison to a standard Transformer, our enhancements
are primarily focused on the self-attention mechanism. Here,
ed ], we use a linear
assuming E = [e1 , e2 , . . . , ei , . . . ,
 trans-
W1 X  and E
W2 X
formation W3 X  for value V, E
as query Q and key K for self-attention calculation. Note that
the components at corresponding positions of E and W1 X 
represent the same variables. Moreover, attention needs to
incorporate the adjacency matrix A, with the attention matrix
result being valid only when Aij = 1. As shown in the
following Equation (11),
Z = softmax (AQK T )V .

(11)

322

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

Algorithm 1 The Training Phase of DMASA
Input: X 

train

∈ Rd×T1 , window size w of X 

Algorithm 2 The Testing Phase of DMASA
train ;

Output: Network that maps to the embedding Embedding(·),
Adjacency matrix A, 1D − Conv (·), Fully connected
network fθ , Our Transformer network incorporating the
masking mechanism ModifiedTransformer (·);
X  train ← X  train + SR(X  train );
Ntrain ← Tw1 ;
for ntrain ← 1 to Ntrain do

[ntrain · w :(ntrain + 1) · w ];
X ← Xtrain
for i ← 1 to d do
ei ← Embedding(Xi∗ );
end for
for i ← 1 to d do
for j ← 1 to d do
ei ej
, j = i ;
vji = ||e ||·||e
i
j ||
end for
Aji ← 1 if j in Top-k(vki , k = i );
end for
M ∈ RD×w , with Mij ∈ {0, 1};
X  = 1D-Conv(M  X );
E = [e1 , e2 , . . . , ei , . . . , ed ];
Zhidden = Modified Transformer(E , X  , A);
1 ||f (Z
LossMAE = m
θ hidden ) − X ||;
end for
utilize LossMAE to improve the entire network;

Additionally, before entering the feedforward network, we
perform a dot product between embeddings E and Z, as shown
in the following Equation (12),
Z := EZ .

(12)

After several Transformer layers, we utilize a simple fully
connected network to aggregate data from different dimensions. The Mean Absolute Error (MAE) reconstruction error
is employed as the optimization objective, aiming to minimize
the overall objective function. As shown in the following
Equation (13), (14),
Z  = fθ (Zhidden ),
1
LossMAE = ||Z  − X ||,
m

(13)
(14)

where fθ is a fully connected network, and m is the number of
matrix elements. Zhidden represents the output data obtained
after the input data has undergone the modified Transformer
component. The comprehensive algorithm for the training
phase is illustrated in Algorithm 1.
G. Anomaly Detection Scoring
Finally, in the process of assigning anomaly scores, we
enhance the evaluation using spectral residual. Spectral residual amplifies the deviation of values from a frequency domain
perspective. By leveraging the disparity between the data
processed through spectral residual and the original data, we

Input: Xtest ∈ Rd×T2 , Embedding(·), A, 1D − Conv (·),
ModifiedTransformer (·), fθ , w;
Output: AnomalyScore
Ntest ← Tw2 ;
for ntest ← 1 to Ntest do
X ← Xtest [ntest · w :(ntest + 1) · w ];
for i ← 1 to d do
ei ← Embedding(Xi∗ );
end for
X  = 1D-Conv(X );
E = [e1 , e2 , . . . , ei , . . . , ed ];
Zhidden = Modified Transformer(E , X  , A);
Z  = fθ (Zhidden );
1 ||Z  − X || + SR( 1 ||Z  − X ||)
AnomalyScore = m
m
end for

assess whether the current time point is in an anomalous state
based on the level of deviation:
1
1
AnomalyScore = ||Z  − X || + SR( ||Z  − X ||) (15)
m
m
The comprehensive algorithm for the testing phase is illustrated in Algorithm 2. In line with standard procedures in
current self-supervised studies, our testing phase begins with
scoring each test sample, followed by threshold adjustment
to align with the benchmark’s anomaly likelihood. Anomalies
are flagged when their scores exceed this threshold. This
process mirrors the operations within real-world systems. A
better detection model can offer clearer statistical distinctions
between normal data points and anomalies, facilitating the
determination of an appropriate threshold to perform this task
more effectively.
H. Computational Complexity
Our proposed method incurs two additional computational
costs compared to conventional Transformer approaches.
Firstly, we employ spectral residuals to augment the data,
which involves the use of FFT with a time complexity of
O(d · T1 log T1 ). Secondly, the method includes learning
similarity relationships, which entails calculating pairwise
neighbor relationships between embeddings of dimension
dmodel across d variable dimensions, resulting in a complexity of O(d · dmodel 2 ). As a comparison, the Anomaly
Transformer requires additional Gaussian kernel overhead,
while the DCdetector applies self-attention both within and
between patches to facilitate contrastive learning. In comparison, our method does not result in a significant increase in
overhead. With the GPU acceleration, the additional computational overhead introduced by our method is acceptable.
IV. E XPERIMENTS
A. Benchmark Dataset
We employ five of the most classic and widely compared datasets, including PSM (Pooled Server Metrics), MSL
(Mars Science Laboratory rover), SMAP (Soil Moisture

YU et al.: DUAL TEMPORAL MASKED MODELING FOR KPI ANOMALY DETECTION VIA SIMILARITY AGGREGATION

323

Active Passive satellite), SWaT (Secure Water Treatment),
and SMD (Server Machine Dataset). Additionally, to visually
demonstrate the model’s detection capabilities across various
anomaly types, we utilize NeurIPS-TS. Furthermore, we add
two real-world multidimensional time series datasets from
different domains: NIPS-TS-SWAN and NIPS-TS-GECCO.
Here is a brief overview of the datasets, as shown in Table II:
1) PSM: The PSM dataset, featuring 25 dimensions, is
collected from multiple application server nodes at eBay. It
includes 13 weeks of training data and 8 weeks of testing data,
and is characterized by a relatively high anomaly ratio.
2) MSL & SMAP: The MSL dataset contains sensor data
from NASA’s Mars Curiosity Rover, while the SMAP dataset,
comprising 25 dimensions, includes soil samples and telemetry
from the Soil Moisture Active Passive (SMAP) satellite.
The data represents real spacecraft telemetry and anomalies from both missions, fully anonymized with respect to
channel IDs.
3) SWaT: The dataset, consisting of 51 dimensions, is
collected from a continuously operating water treatment infrastructure. It spans 11 days of network traffic and sensor data,
with 7 days of normal operation and 4 days of attack scenarios
involving 41 documented attacks, all labeled as either normal
or abnormal behavior.
4) SMD: A five-week dataset gathered from an Internet
company’s cluster. As per the instructions provided by the data
provider, the detection process is required to be carried out on
individual entities separately. Thus, we chose the first entity
from the first cluster.
5) NeurIPS-TS: A synthetic dataset provided by [45] for
detecting various anomaly types.
6) NIPS-TS-SWAN: The NIPS-TS-SWAN dataset, focused
on drinking water quality in the “Internet of Things” context,
featuring a relatively high anomaly rate and posing challenge
for anomaly detection.
7) NIPS-TS-GECCO: The NIPS-TS-GECCO dataset is
derived from vector magnetograms of the solar photosphere
in Spaceweet HMI active regions,and presents a very low
anomaly rate, making it another difficult anomaly detection
dataset.

sequences. InterFusion employs a hierarchical VAE to learn
low-dimensional inter-metric and temporal embeddings.
Anomaly Transformer detects anomalies by leveraging
differences between local and global correlations in normal
and anomalous data. DCdetector combines contrastive learning
to learn permutation invariant representations from a multiscale perspective.
Common evaluation metrics, including accuracy, precision,
recall, and F1-score, are utilized. In alignment with [11], [29],
[35], [42], [52], we adopt common adjustment strategies for a
fair evaluation. Additionally, we have supplemented recently
proposed metrics such as affiliation precision/recall [57],
Range-AUC-ROC, Range-AUC-PR, V_ROC, and V_PR [58].
Affiliation precision and recall [57] are determined by measuring the distance between true labels and predicted labels.
Range AUC-ROC and Range AUC-PR add a buffer transition
area at anomaly boundaries, mapping discrete data to a
continuous region and calculating the area under the ROC and
PR curves for different thresholds. The VUS metric represents
the volume corresponding to Range AUC-ROC and Range
AUC-PR for various buffer sizes [58].

B. Baselines

D. Research Question

We compared our model with 16 different approaches
for a comprehensive evaluation. DAGMM [25], LOF [48],
MPPCACD [49] utilize density estimation models;
OC-SVM [23], iForest [50] employ classical machine learning
algorithms. Deep SVDD [51], THOC [52], ITAD [53] use
clustering methods, VAR [54], LSTM [31] are autoregressive models, and LSTM-VAE [26], OmniAnomaly [29],
BeatGAN [55], InterFusion [56], Anomaly Transformer [35],
DCdetector [42] are reconstruction-based models. Among
reconstruction-based methods, LSTM-VAE employs LSTM
to extract temporal features and reconstruct the expected
distribution of the data by progress-based varying prior.
OmniAnomaly employs stochastic variable connection and
planar normalizing flow to acquire robust representations of
time series data. BeatGAN utilizes an adversarial generative
approach coupled with time series warping for reconstructing

In the following experiments, we endeavored to answer
these questions.
•RQ1: Faced with the challenge of unlabeled KPI data,
has the overall design of the DMASA framework resulted in
effective anomaly detection?
•RQ2: Do the various components of DMASA collaborate
effectively to identify different types of anomalies, including
point anomalies and pattern anomalies?
•RQ3: Has the use of similarity aggregation to isolate
irrelevant variables and the application of spectral residual to
strengthen anomaly boundaries yielded positive results?
•RQ4: Is similarity aggregation meaningful? Do features
of different variables exhibit meaningful correlations, either
proximity or divergence?
•RQ5: How does the model’s performance vary under
different parameters? Is it robust?

C. Implementation Details
We summarize the default hyper-parameters as follows. Our
model has a default of 3 layers for the Transformer. Except for
the SMAP dataset, where the hidden layer dimension is set to
64, the default dimension for hidden layers in other datasets
is 256. The default stride for one-dimensional convolution is
set to 32. For convenience in masking, the number of heads in
attention is set to 1 by default. The default masking rate for
the mask part is 0.3, the number of nearby variables (Top-k) is
set to 3, the window size is 128, and the default definition for
the anomaly threshold is 1. We utilize the Adam optimizer to
optimize network parameters, setting the initial learning rate
to 10−3 . The default batch size for both training and testing is
128. All experiments are conducted using the PyTorch 1.7.1
library on a computer equipped with a GeForce RTX 3060
GPU supporting NVIDIA CUDA.

324

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

TABLE I
R ESULTS ON F IVE W IDELY U SED R EAL -W ORLD DATASETS FOR P ERFORMANCE C OMPARISON . P ERFORMANCE IS R ANKED IN A SCENDING O RDER
BASED ON F1 S CORE . P, R, AND F1 R EPRESENT P RECISION , R ECALL , AND F1 S CORE , R ESPECTIVELY. A LL R ESULTS ARE P RESENTED IN
P ERCENTAGES (%), W ITH THE B EST R ESULTS H IGHLIGHTED IN R ED AND THE S ECOND -B EST R ESULTS I NDICATED BY A
B LUE U NDERSCORE . T HE R ESULTS OF OTHER M ETHODS ARE S OURCED F ROM DC DETECTOR [42]

TABLE II
B ENCHMARK DATASET D ETAILS , W HERE D IM R EPRESENTS
D IMENSIONS , AND AR R EPRESENTS A NOMALY R ATIO

E. Main Results
RQ1: We initially evaluate our model on five widely-used
and well-assessed real-world scenario datasets, comparing it
against 16 various baseline models as presented in Table I. Our
model continues to exhibit superiority compared to advanced
models like Anomaly Transformer [35] and DCdetector [42].
Notably, using the same evaluation metrics as the Anomaly
Transformer and DCdetector, our method achieves state-ofthe-art performance on most datasets. Despite the impressive
performance of current methods–DCdetector, for instance, has
garnered F1 scores of 96.33% on SWaT and 97.94% on PSM
benchmarks–our approach has managed to outperform them,
achieving F1 scores of 97.53% on SWaT and 98.17% on PSM.
We eschew the use of contrastive learning strategies for sample
augmentation, which, while beneficial for some methods like
DCdetector in enhancing performance on the MSL benchmark,
incurs higher training costs and can compromise generalization
across other benchmarks, as evidenced by the 87.18% F1 score
on the SMD benchmark. In comparison, our method not only
demonstrates superior performance across all benchmarks but
also significantly elevates the overall detection capabilities.
Despite ongoing controversies in evaluating anomaly detection algorithms, we argue that timely alerts and interventions
during anomalies align with the ultimate goal of anomaly

detection in practice. Therefore, we adhere to the evaluation methods consistent with the Anomaly Transformer and
DCdetector. Of course, for a more comprehensive assessment
of the performance of various methods, we complement the
additional evaluation with recently proposed metrics such
as affiliation precision/recall [57], Range-AUC-ROC, RangeAUC-PR, V_ROC, and V_PR [58]. Table I illustrates that the
best results are concentrated among Anomaly Transformer,
DCdetector, and our method. Therefore, we provide a broader
comparison of these three methods in Table III. The table
demonstrates that our method excels on most metrics and
datasets. The choice of anomaly threshold also affects the
corresponding evaluation metrics. If the goal is accurate
anomaly detection, aligning with our method involves selecting a smaller anomaly rate to raise the anomaly threshold.
Conversely, if the focus in anomaly detection is on the distance
between real situations and predicted events, selecting a larger
anomaly rate to relax the threshold produces better results.
Furthermore, considering the already high evaluation results
on several commonly used datasets, we increased the difficulty of anomaly detection by employing more challenging
datasets for comparison among various anomaly detection methods. We supplemented experimental data for the
NIPS-TS-SWAN and NIPS-TS-GECCO datasets in Table VI.
These datasets present challenging detection scenarios with
anomaly rates of 32.6% and 1.1%, respectively. We compared
our model with several representative methods that have
demonstrated good performance, including Matrix Profile,
GBRT, LSTM-RNN, Autoregression, OCSVM, AutoEncoder,
Anomaly Transformer, iForest, and DCdetector. Remarkably,
our model still achieved the best overall performance,
underscoring the competitiveness of our approach. Similarly,
considering that outstanding deep learning methods are still
Anomaly Transformer and DCdetector, we further compared
our model with these two methods. The results across different
metrics for the three models are presented in Table IV,
comprehensively showcasing the performance of our model. In
terms of both detection accuracy and the rapidity of response,

YU et al.: DUAL TEMPORAL MASKED MODELING FOR KPI ANOMALY DETECTION VIA SIMILARITY AGGREGATION

325

TABLE III
A DDITIONAL E VALUATION M ETRICS ON THE 5 DATASETS . A FF -P R EPRESENTS A FFILIATION P RECISION , A FF -R S TANDS FOR A FFILIATION
R ECALL [57], R_A_R, AND R_A_P [58] ARE R ANGE -AUC-ROC AND R ANGE -AUC-PR, R ESPECTIVELY, R EPRESENTING T WO S CORES BASED ON
L ABEL T RANSFORMATION U NDER ROC AND PR C URVES . V_ROC AND V_PR [58] R EPRESENT VOLUMES U NDER THE S URFACE C REATED BY ROC
AND PR C URVES , R ESPECTIVELY. A LL R ESULTS ARE P RESENTED IN P ERCENTAGES (%), W ITH THE B EST R ESULTS H IGHLIGHTED IN R ED AND THE
S ECOND -B EST R ESULTS I NDICATED BY A B LUE U NDERSCORE . T HE T WO VALUES OF AR R EPRESENT THE E VALUATION R ESULTS OF O UR M ODEL AT
D IFFERENT T HRESHOLDS

TABLE IV
C OMPARISON OF A DDITIONAL M ETRICS FOR THE NIPS-TS DATASET. A LL R ESULTS ARE P RESENTED IN P ERCENTAGES (%), W ITH THE B EST R ESULTS
H IGHLIGHTED IN R ED . T HE R ESULTS OF OTHER M ETHODS ARE S OURCED F ROM DC DETECTOR [42]

indicating the distance between real situations and predicted
events, our method consistently maintains a leading position.
F. Visualization of Anomaly Score
RQ2: To demonstrate the effectiveness of our model
in handling various types of anomalies, we adhere to the
benchmark conventions outlined in NeurIPS-TS and visually
present anomaly scores as shown in Figure 4. The NeurIPS-TS
benchmark is a meticulously designed artificially synthesized
anomaly detection benchmark that encompasses point anomalies, including global point anomalies and contextual point
anomalies, as well as pattern anomalies such as shapelet
anomalies, seasonal anomalies, and trend anomalies. In particular, from the experimental results, it can be observed
that our model is capable of promptly identifying and pinpointing point anomalies. Moreover, for pattern anomalies,

our model efficiently recognizes the onset points where patterns undergo abrupt changes, rapidly localizing the start
and end points of anomalous segments. Clearly, our model
proves capable of effectively addressing different types of
anomalies.
G. Ablation Studies
RQ3: Table V presents the ablation study of the two
main modules under consistent parameters. The attention mask
designates a module designed to discern similarity relations
and impose similarity adjacency structure onto the attention
module of the Transformer. This module restricts the fusion of
information across distinct variable dimensions, as elaborated
upon in Section III-D and Section III-F concerning the topic
of similarity aggregation. Spectral residual, on the other hand,
is the part of Section III-C and III-G that utilizes spectral

326

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

Fig. 4. Visualization of the detection of different types of anomalies by our model. It can be observed that for point anomalies, DMASA yields significantly
higher anomaly scores, allowing for the easy identification of anomalous points. For pattern anomalies, DMASA demonstrates the ability to locate such
anomalies by exhibiting notably elevated anomaly scores at the starting and ending points of the anomalous segment.
TABLE V
A BLATION S TUDY OF THE M ODEL , W HERE ATTENTION M ASK R EPRESENTS THE PART R ELATED TO S IMILARITY AGGREGATION , AND S PECTRAL
R ESIDUAL R EPRESENTS THE PART R ELATED TO S PECTRAL R ESIDUAL . A LL R ESULTS ARE P RESENTED IN P ERCENTAGE (%),
W ITH THE B EST R ESULTS H IGHLIGHTED IN R ED

TABLE VI
R ESULTS FOR THE NIPS-TS DATASET. P ERFORMANCE IS R ANKED F ROM
L OW TO H IGH . A LL R ESULTS ARE P RESENTED IN P ERCENTAGES (%),
W ITH THE B EST R ESULTS H IGHLIGHTED IN R ED AND THE S ECOND -B EST
R ESULTS I NDICATED BY A B LUE U NDERSCORE . T HE R ESULTS OF OTHER
M ETHOD S OURCED F ROM DC DETECTOR [42]

residuals to enhance the data, combining frequency domain
data to aid in learning similarity relations and reinforcing
the scoring mechanism. It can be observed that, although
the performance improvement seems not very significant on
some datasets such as MSL and PSM, there is a substantial
enhancement, particularly with the spectral residual method
on the SMAP dataset. The reason for this could be the high
anomaly rate in the SMAP dataset, along with a much larger
size of the test set compared to the training set, resulting
in overall large-scale and challenging detection scenarios.
The spectral residual method provides significant enhancement

from a frequency domain perspective, leading to substantial
performance improvement on the SMAP dataset.
H. Visualization of Variable Relationships
RQ4: In order to provide a more comprehensive and visually intuitive depiction of the relationships between variables,
we computed similarity using the ei embeddings learned from
the PSM dataset and represented them through a heatmap,
as illustrated in Figure 6. The color intensity in the heatmap
corresponds to the strength of the correlation between variables, with darker colors indicating stronger correlations.
Evidently, for each variable, only a limited set of other variables exhibit high correlation. This observation suggests that
when employing attention mechanisms for information fusion
among variables, focusing on these highly correlated variables
is sufficient. This focused attention facilitates the effective
transmission of relevant information, reducing the impact of
irrelevant variables on anomaly detection. Simultaneously, this
strategy contributes to a reduction in computational complexity
during self-attention computations.
I. Parameter Sensitivity
RQ5: Simultaneously, we investigated the sensitivity of our
model to different parameters, as illustrated in the Figure 5.
The mask_ratio represents the difficulty of reconstructing data
for the model. It is noteworthy that even with a high masking rate, our model maintains robust detection performance.
This robustness may be attributed, on one hand, to the
residual connection structure of the Transformer, allowing

YU et al.: DUAL TEMPORAL MASKED MODELING FOR KPI ANOMALY DETECTION VIA SIMILARITY AGGREGATION

327

Fig. 5. Sensitivity analysis of key parameters. mask_ratio denotes the proportion of masked data during self-supervised learning. Top-k represents the number
of other variables involved in information fusion for each variable. dmodel signifies the dimensionality of the hidden layer variables. step denotes the stride
in one-dimensional convolution. layers indicate the number of layers in the stacked Transformer.

few most relevant variables for information fusion is sufficient.
In the case of the MSL benchmark, the lack of a contrastive
strategy to enrich the data, along with a smaller training dataset
relative to the test dataset, leads to a slightly lower robustness.
However, the overall resilience of our method is confirmed
by its performance on other benchmarks. Balancing training
expenses with the performance trends shown in Figure 5 (b),
we recommend setting the parameter k optimally between 5
and 6.
V. C ONCLUSION AND F UTURE W ORK

Fig. 6. Visualization of pairwise similarity among different variables. The
darker the color, the greater the degree of correlation between the two
variables.

information to be effectively transmitted. On the other hand,
it could be because the learned embeddings ei carry essential information that remains unaffected by masking. The
parameter dmodel corresponds to the dimensionality of the
intermediate variable, and layers denotes the number of layers
in the Transformer, both of which can influence computational
efficiency. Increasing dmodel and layers sometimes leads
to improved detection efficiency. However, considering the
associated performance overhead, we opt for a trade-off. The
parameter step represents the stride during one-dimensional
convolution, indicating the aggregation of several time points.
Top-k determines the number of most relevant variables
selected, influencing the number of related variables each
variable can “see”. It is observed that allowing each variable to
interact with all variables may introduce interference, leading
to a decrease in detection efficiency. Therefore, selecting a

KPI anomaly detection plays a crucial role in maintaining
the overall reliability of operational systems. However, due
to the lack of labels in KPI data, self-supervised approaches
are proposed to learn data features for anomaly detection. In
this work, we introduce a pioneering self-supervised model,
DMASA, which stands out with its dual-masked approach coupled with similarity aggregation for KPI anomaly detection.
A key innovation is the integration of spectral residual methods to detect anomalies through frequency-domain analysis,
enhancing the identification of their onset points. Furthermore,
DMASA refines Transformer architecture to better assimilate
the complexities of multivariate time series, while a similarity
aggregation technique minimizes interference from irrelevant
variables to extract meaningful features from KPIs. The model
has proven to be superior and effective across various datasets
and can be used in various scenarios.
Our approach is well-suited for detecting anomalies in
multivariate KPIs, such as CPU utilization and socket status,
in dynamic environments like networks and servers, where
conditions are continuously evolving. Traditional methods
relying on contrastive learning might struggle with the varying
features of data over time. In contrast, our solution, grounded

328

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

in mask modeling, is designed to adapt to the data’s intrinsic
distribution, offering greater flexibility. A key implementation
challenge in these contexts is calibrating the anomaly score
threshold to ensure timely alerts in response to the evolving
landscape. While setting a generalized threshold in advance is
difficult due to the varying nature of real-world systems, we
believe that dynamically adjusting the threshold based on the
statistical distribution of normal data points versus anomalies
could significantly improve the model’s practicality. Therefore,
in future work, we plan to explore how to implement a selfadaptive mechanism for adjusting the threshold at test time.
Additionally, while our current approach effectively identifies when anomalies occur, determining which specific
variables contribute to an overall anomaly remains a challenge
due to the complex relationships between variables. This topic
has not been thoroughly addressed in the field, and existing
datasets often lack labels indicating which individual variables
are abnormal. In future work, we aim to investigate how the
interactions between variables affect anomalies and whether it
is possible to attribute an anomaly to specific variables. This
will form a key part of our continued research. Meanwhile,
we are committed to collecting and incorporating more realworld data to further validate the applicability and robustness
of our approach, thereby reinforcing the practical relevance
and continuous improvement of our research.
ACRONYMS
FFT
Fast Fourier Transform
KPI
Key Performance Indicator
LSTM Long Short-term Memory
MAE Mean Absolute Error
MSL Mars Science Laboratory rover dataset
PSM Pooled Server Metrics dataset
RNN Recurrent Neural Network
SMAP Soil Moisture Active Passive satellite dataset
SMD Server Machine Dataset.
SR
Spectral Residual
SWaT Secure Water Treatment dataset
VAE Variational Autoencoder
R EFERENCES
[1] A. Anandakrishnan, S. Kumar, A. Statnikov, T. Faruquie, and D. Xu,
“Anomaly detection in finance: Editors’ introduction,” in Proc. KDD
Workshop Anom. Detect. Financ., 2018, pp. 1–7.
[2] G. Li and J. J. Jung, “Deep learning for anomaly detection in multivariate
time series: Approaches, applications, and challenges,” Inf. Fusion,
vol. 91, pp. 93–102, Mar. 2023.
[3] A. A. Cook, G. Mısırlı, and Z. Fan, “Anomaly detection for IoT
time-series data: A survey,” IEEE Internet Things J., vol. 7, no. 7,
pp. 6481–6494, Jul. 2020.
[4] H. Ren et al., “Time-series anomaly detection service at
Microsoft,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov.
Data Min., 2019, pp. 3009–3017.
[5] D. P. Kumar, T. Amgoth, and C. S. R. Annavarapu, “Machine learning
algorithms for wireless sensor networks: A survey,” Inf. Fusion, vol. 49,
pp. 1–25, Sep. 2019.
[6] Y. Li et al., “Federated domain generalization: A survey,” 2024,
arXiv:2306.01334.
[7] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proc. 35th AAAI Conf. Artif. Intell., 2021,
pp. 4027–4035.

[8] Y. Yang, H. Zhang, and Y. Li, “Pipeline safety early warning by
multifeature-fusion CNN and LightGBM analysis of signals from
distributed optical fiber sensors,” IEEE Trans. Instrum. Meas., vol. 70,
pp. 1–13, Sep. 2021.
[9] Y. Yang, Y. Li, and H. Zhang, “Long-distance pipeline safety early
warning: A distributed optical fiber sensing semi-supervised learning
method,” IEEE Sensors J., vol. 21, no. 17, pp. 19453–19461, Sep. 2021.
[10] T. Ergen and S. S. Kozat, “Unsupervised anomaly detection with LSTM
neural networks,” IEEE Trans. Neural Netw. Learn. Syst., vol. 31, no. 8,
pp. 3127–3141, Aug. 2020.
[11] H. Xu et al., “Unsupervised anomaly detection via variational autoencoder for seasonal KPIs in Web applications,” in Proc. World Wide
Web Conf., 2018, pp. 187–196.
[12] H. Zhu, S. Rho, S. Liu, and F. Jiang, “Learning spatial graph structure
for multivariate KPI anomaly detection in large-scale cyber-physical
systems,” IEEE Trans. Instrum. Meas., vol. 72, pp. 1–16, Jun. 2023.
[13] T. Huang, P. Chen, and R. Li, “A semi-supervised VAE based active
anomaly detection framework in multivariate time series for online
systems,” in Proc. ACM Web Conf., 2022, pp. 1797–1806.
[14] A. Blázquez-García, A. Conde, U. Mori, and J. A. Lozano, “A review
on outlier/anomaly detection in time series data,” ACM Comput. Surv.,
vol. 54, no. 3, pp. 1–33, 2021.
[15] L. Ruff et al., “A unifying review of deep and shallow anomaly
detection,” Proc. IEEE, vol. 109, no. 5, pp. 756–795, May 2021.
[16] Y.-c. Park, J.-G. Jang, and U. Kang, “Fast and accurate partial Fourier
transform for time series data,” in Proc. 27th ACM SIGKDD Int. Conf.
Knowl. Discov. Data Min., 2021, pp. 1309–1318.
[17] Y. Yang, Y. Li, and H. Zhang, “Pipeline safety early warning method for
distributed signal using bilinear CNN and LightGBM,” in Proc. IEEE
Int. Conf. Acoust., Speech Signal Process., 2021, pp. 4110–4114.
[18] A. Dosovitskiy et al., “An image is worth 16 × 16 words: Transformers
for image recognition at scale,” in Proc. Int. Conf. Learn. Represent.,
2021, pp. 1–22.
[19] D. R. Choffnes, F. E. Bustamante, and Z. Ge, “Crowdsourcing servicelevel network event monitoring,” in Proc. ACM SIGCOMM Conf., 2010,
pp. 387–398.
[20] P. J. Rousseeuw and A. M. Leroy, Robust Regression and Outlier
Detection. Hoboken, NJ, USA: Wiley, 2005.
[21] S. W. Roberts, “Control chart tests based on geometric moving averages,” Technometrics, vol. 1, no. 3, pp. 239–250, 1959.
[22] J. Li, H. Izakian, W. Pedrycz, and I. Jamal, “Clustering-based anomaly
detection in multivariate time series data,” Appl. Soft Comput., vol. 100,
Mar. 2021, Art. no. 106919.
[23] D. M. J. Tax and R. P. W. Duin, “Support vector data description,” Mach.
Learn., vol. 54, pp. 45–66, Jan. 2004.
[24] S. Elsayed, D. Thyssens, A. Rashed, H. S. Jomaa, and L. SchmidtThieme, “Do we really need deep learning models for time series
forecasting?” 2021, arXiv:2101.02118.
[25] B. Zong et al., “Deep autoencoding Gaussian mixture model for
unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Represent.,
2018, pp. 1–19.
[26] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly detector
for robot-assisted feeding using an LSTM-based variational autoencoder,” IEEE Robot. Autom. Lett., vol. 3, no. 3, pp. 1544–1551,
Jul. 2018.
[27] M. Sakurada and T. Yairi, “Anomaly detection using autoencoders
with nonlinear dimensionality reduction,” in Proc. 2nd Workshop Mach.
Learn. Sens. Data Anal., 2014, pp. 4–11.
[28] Z. Li, Y. Sun, L. Yang, Z. Zhao, and X. Chen, “Unsupervised
machine anomaly detection using autoencoder and temporal convolutional network,” IEEE Trans. Instrum. Meas., vol. 71, pp. 1–13,
Oct. 2022.
[29] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Min., 2019, pp. 2828–2837.
[30] L. Bontemps, V. L. Cao, J. McDermott, and N.-A. Le-Khac, “Collective
anomaly detection based on long short-term memory recurrent neural networks,” in Proc. Int. Conf. Future Data Secur. Eng., 2016,
pp. 141–152.
[31] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and
T. Soderstrom, “Detecting spacecraft anomalies using LSTMS and
nonparametric dynamic thresholding,” in Proc. 24th ACM SIGKDD Int.
Conf. Knowl. Discov. Data Min., 2018, pp. 387–395.
[32] N. Laptev, S. Amizadeh, and I. Flint, “Generic and scalable framework
for automated time-series anomaly detection,” in Proc. 21th ACM
SIGKDD Int. Conf. Knowl. Discov. Data Min., 2015, pp. 1939–1947.

YU et al.: DUAL TEMPORAL MASKED MODELING FOR KPI ANOMALY DETECTION VIA SIMILARITY AGGREGATION

[33] D. Liu et al., “Opprentice: Towards practical and automatic anomaly
detection through machine learning,” in Proc. Internet Meas. Conf.,
2015, pp. 211–224.
[34] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” Proc.
VLDB Endow., vol. 15, no. 6, pp. 1201–1214, 2022.
[35] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time
series anomaly detection with association discrepancy,” in Proc. Int.
Conf. Learn. Represent., 2022, pp. 1–20.
[36] Y. Jeong, E. Yang, J. H. Ryu, I. Park, and M. Kang, “AnomalyBERT:
Self-supervised transformer for time series anomaly detection using data
degradation scheme,” in Proc. Int. Conf. Learn. Represent. Workshop
Mach. Learn. IoT, Datasets, Percept., Underst., 2023, pp. 1–11.
[37] Y. Jiao, K. Yang, D. Song, and D. Tao, “TimeAutoAD: Autonomous
anomaly detection with self-supervised contrastive loss for multivariate
time series,” IEEE Trans. Netw. Sci. Eng., vol. 9, no. 3, pp. 1604–1619,
May/Jun. 2022.
[38] Z. Liang, J. Zhang, C. Liang, H. Wang, Z. Liang, and L. Pan, “A
shapelet-based framework for unsupervised multivariate time series representation learning,” Proc. VLDB Endow., vol. 17, no. 3, pp. 386–399,
2024.
[39] H. Kim, S. Kim, S. Min, and B. Lee, “Contrastive time-series
anomaly detection,” IEEE Trans. Knowl. Data Eng., vol. 36, no. 10,
pp. 5053–5065, Oct. 2024.
[40] T. Zhou, Z. Ma, Q. Wen, X. Wang, L. Sun, and R. Jin, “Fedformer:
Frequency enhanced decomposed transformer for long-term series forecasting,” in Proc. Int. Conf. Mach. Learn., 2022, pp. 27268–27286.
[41] Y. Nie, N. H. Nguyen, P. Sinthong, and J. Kalagnanam, “A time series
is worth 64 words: Long-term forecasting with transformers,” in Proc.
Int. Conf. Learn. Represent., 2023, pp. 1–24.
[42] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “DCdetector: Dual
attention contrastive representation learning for time series anomaly
detection,” in Proc. 29th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Min., 2023, pp. 3033–3045.
[43] A. Abdulaal, Z. Liu, and T. Lancewicki, “Practical approach to
asynchronous multivariate time series anomaly detection and localization,” in Proc. 27th ACM SIGKDD Conf. Knowl. Discov. Data Min.,
2021, pp. 2485–2494.
[44] A. P. Mathur and N. O. Tippenhauer, “SWaT: A water treatment testbed
for research and training on ICS security,” in Proc. Int. Workshop CyberPhys. Syst. Smart Water Netw., 2016, pp. 31–36.
[45] K.-H. Lai, D. Zha, J. Xu, Y. Zhao, G. Wang, and X. Hu, “Revisiting time
series outlier detection: Definitions and benchmarks,” in Proc. 35th Conf.
Neural Inf. Process. Syst. Datasets Benchmarks Track, 2021, pp. 1–13.
[46] R. Angryk et al., 2020, “SWAN-SF,” Dataset. [Online]. Available:
https://doi.org/10.7910/DVN/EBCFKM
[47] F. Rehbach, S. Moritz, S. Chandrasekaran, M. Rebolledo, M. Friese,
and T. Bartz-Beielstein, “GECCO 2018 industrial challenge: Monitoring
of drinking-water quality,” in Proc. Genet. Evol. Comput. Conf., 2018,
p. 2019.
[48] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF: Identifying
density-based local outliers,” SIGMOD Rec., vol. 29, no. 2, pp. 93–104,
2000.
[49] T. Yairi, N. Takeishi, T. Oda, Y. Nakajima, N. Nishimura, and N. Takata,
“A data-driven health monitoring method for satellite housekeeping data
based on probabilistic clustering and dimensionality reduction,” IEEE
Trans. Aerosp. Electron. Syst., vol. 53, no. 3, pp. 1384–1401, Jun. 2017.
[50] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. 8th
IEEE Int. Conf. Data Min., 2008, pp. 413–422.
[51] L. Ruff et al., “Deep one-class classification,” in Proc. 35th Int. Conf.
Mach. Learn., 2018, pp. 4393–4402.
[52] L. Shen, Z. Li, and J. Kwok, “Timeseries anomaly detection using
temporal hierarchical one-class network,” in Proc. 34th Conf. Neural
Inf. Process. Syst., 2020, pp. 13016–13026.
[53] Y. Shin et al., “ITAD: Integrative tensor-based anomaly detection system
for reducing false positives of satellite systems,” in Proc. 29th ACM Int.
Conf. Inf. Knowl. Manag., 2020, pp. 2733–2740.
[54] O. D. Anderson and M. Kendall, “Time-series. 2nd edn,” J. Roy. Stat.
Soc. Ser. D Stat., vol. 25, no. 4, pp. 308–310, 1976.
[55] B. Zhou, S. Liu, B. Hooi, X. Cheng, and J. Ye, “BeatGAN: Anomalous
rhythm detection using adversarially generated time series,” in Proc.
28th Int. Joint Conf. Artif. Intell., Jul. 2019, pp. 4433–4439.
[56] Z. Li et al., “Multivariate time series anomaly detection and
interpretation using hierarchical inter-metric and temporal embedding,” in Proc. 27th ACM SIGKDD Conf. Knowl. Discov. Data Min.,
2021, pp. 3220–3230.

329

[57] A. Huet, J. M. Navarro, and D. Rossi, “Local evaluation of time series
anomaly detection algorithms,” in Proc. 28th ACM SIGKDD Conf.
Knowl. Discov. Data Min., 2022, pp. 635–645.
[58] J. Paparrizos, P. Boniol, T. Palpanas, R. S. Tsay, A. Elmore, and
M. J. Franklin, “Volume under the surface: A new accuracy evaluation measure for time-series anomaly detection,” Proc. VLDB Endow.,
vol. 15, no. 11, pp. 2774–2787, 2022.

Ting Yu received the bachelor’s degree in computer
science from the Harbin Institute of Technology,
China, in 2020 and the master’s degree from
the College of Computer, National University of
Defense Technology, China. Her research focuses on
time series analysis and artificial intelligence for IT
operations.

Zijian Gao received the B.E. degree from Sichuan
University, Chengdu, China, in 2019 and the
master’s degree in software engineering from
the National University of Defense Technology,
Changsha, China, in 2022, where he is currently pursuing the Ph.D. degree with the School of Computer.
His research interests include continual learning and
reinforcement learning.

Kele Xu received the Ph.D. degree from the
University of Paris VI, France, in 2017. He is an
Associate Professor with the School of Computer,
National University of Defense Technology. His primary research interests in acoustic signal processing,
machine learning, and intelligent software systems.

Xu Wang received the B.E. degree from the
Southwest University of Finance and Economics,
Chengdu, China, in 2021 and the master’s degree
in electronic and information engineering from
the National University of Defense Technology,
Changsha, China, in 2024.

Peichang Shi received the Ph.D. degree from
the National University of Defense Technology,
Changsha, China, in 2012, where he is an Associate
Professor. His current research interests include
cloud computing, blockchain, AI, software engineer,
and distributed computing technology.

330

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 22, NO. 1, FEBRUARY 2025

Bo Ding received the Ph.D. degree in computer
science from the National University of Defense
Technology, Changsha, in 2010, where he is currently a Professor. His research interests include
distributed computing and systems.

Dawei Feng received the Ph.D. degree from the
University of Paris XI, France, in 2014. He is an
Associate Professor with the School of Computer,
National University of Defense Technology. His
main research interests are distributed computing
and intelligent software systems. He has presided
over several national scientific research projects.
PAPER_TEXT
