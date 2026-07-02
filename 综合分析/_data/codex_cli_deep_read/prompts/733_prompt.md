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
# [733] MAD-MulW: A Multi-Window Anomaly Detection Framework for BGP Security Events
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
编号：733
题名：MAD-MulW: A Multi-Window Anomaly Detection Framework for BGP Security Events
年份：2026
DOI：10.1109/tnsm.2026.3696319
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2026.3696319.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 11
已有代码状态：已下载；MAD-MulW -> source\MAD-MulW

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\733.txt
- 原始字符数：81416
- 本次发送字符数：81416
- 是否截断：False

代码包：
- 仓库：MAD-MulW
  - URL：https://github.com/2024ChenYP/MAD-MulW
  - 状态：downloaded
  - 本地目录：source\MAD-MulW
  - 顶层结构：.gitignore、.idea/、README.md、config_files/、data/、dataGAT.py、dataloader.py、loss.py、model1.py、overlook.png、picture/、requirements.txt、run_interface.py、show.py、train_model.py、trainer.py、utils.py
  - 主要语言：Python:28
  - README 标题：MAD-MulW、Installation、Datasets、Quick Start、Multivariate Datasets Quick Start、MAD-MulW、Installation、Datasets、Quick Start、Multivariate Datasets Quick Start
  - README 运行线索：Python 3.7；Python 3.7；Python 3.7
  - 关键文件：{"依赖环境": ["requirements.txt"], "推理/演示入口": ["run_interface.py"], "数据处理入口": ["dataloader.py"], "模型定义": ["model1.py"], "训练入口": ["trainer.py", "train_model.py"]}
  - 数据集线索：KDD、Quic、Tor、dapt、tor

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

1

MAD-MulW: A Multi-Window Anomaly Detection
Framework for BGP Security Events
Songtao Peng, Yiping Chen, Xincheng Shu, Wu Shuai, Shenhao Fang, Zhongyuan Ruan, and
Qi Xuan, Senior Member, IEEE

Abstract—In recent years, various international security events
have occurred frequently and interacted between real society
and cyberspace. Traditional traffic monitoring mainly focuses on
the local anomalous status of events due to a large amount of
data. BGP-based event monitoring makes it possible to perform
differential analysis of international events. For many existing
traffic anomaly detection methods, we have observed that the
window-based noise reduction strategy effectively improves the
success rate of time series anomaly detection. Motivated by this,
we propose an unsupervised anomaly detection model, MADMulW, which introduces a multi-window serial framework. The
W-GAT module adaptively updates sample weights within the
window to reduce noise, while the W-LAE module captures temporal trends through predictive reconstruction, enhancing interclass separation. Our model has been experimentally validated
on multiple BGP anomalous events with an average F1 score
of over 90%, which demonstrates the significant improvement
effect of the stage windows and adaptive strategy on the efficiency
and stability of the timing model. The source code is available
at://github.com/2024ChenYP/MAD-MulW.

(a)

(b)

(c)

𝒔𝒍𝒊𝒅𝒊𝒏𝒈 𝒘𝒊𝒏𝒅𝒐𝒘 (𝒘 = 𝟏𝟓)

…

…

…

Index Terms—Anomaly Detection, Time Series, Unsupervised
Model, Multi-Window

I. I NTRODUCTION

T

ODAY, the rapid development of the Internet has provided quality services in business, education, and entertainment. With society’s increasing dependence on the Internet, its reliability and security have become critical concerns.
Researchers have long focused on threats such as distributed
denial-of-service attacks, network worms, and IP hijacking.
Meanwhile, international conflicts (e.g., the Russia-Ukraine
war) and natural disasters (e.g., earthquakes, hurricanes) can
also trigger cascading network failures, causing incalculable
losses. For instance, Hurricane Fiona struck Puerto Rico in
2022, damaging optical fiber and wireless networks and disrupting communication between Autonomous Systems (ASes).
Although emergency services such as CISA and FEMA deployed mobile facilities, the disruption still had a significant
impact. These examples highlight the necessity of accurate
anomaly detection and warning to ensure network security.
In large-scale anomalous events, interface-level traffic monitoring is limited to a narrow view. As the most widely used
inter-domain routing protocol, the Border Gateway Protocol
(BGP) makes it possible to detect anomalies by managing
S. Peng, Y. Chen, X. Shu, W. Shuai, S. Fang, Z. Ruan, and Q. Xuan are
with the Institute of Cyberspace Security, Zhejiang University of Technology,
Hangzhou 310023, China. (Corresponding author: Zhongyuan Ruan, e-mail:
zyruan@zjut.edu.cn.)
S. Peng, Z. Ruan, and Q. Xuan are also with Binjiang Institute of Artificial
Intelligence, ZJUT, Hangzhou 310056, China.

Fig. 1. (a) Illustration of different BGP anomaly events in the router network.
(b) IBGP (internal) and EBGP (external) protocols both operate on port 179
for data exchange. (c) Time-series visualization of features under different
processing methods: original, interval, and sliding window.

network reachability information. BGP anomalies are usually
reflected in a surge of update messages when communication
links are disrupted (Figure 1 (a)). By parsing and analyzing
update packets from port 179 (Figure 1 (b)), one can derive
time series suitable for anomaly detection. In this work,
the investigated problem is defined as detecting abnormal
timestamps from BGP update-derived multivariate time series
under an unsupervised setting. The key challenge is that
BGP security events disturb routing behaviors in different
forms and intensities, while reliable anomaly labels are usually
unavailable before detection. Therefore, the model is expected
to learn normal BGP communication patterns and identify
abnormal routing fluctuations through anomaly scores.
In terms of data, Semenoglou et al. [1] summarized the existing data enhancement methods and showed that the sliding
window strategy is useful for most data analysis. Dimoudis
et al. [2] proposed an anomaly detection algorithm for rolling
median with an adaptive sliding window to detect anomalous
data points in time series. These data enhancement strategies
can smooth out the data noise and facilitate the task of
classification, prediction, and detection. In terms of models,
the field of time series provides many proven theories and techniques. The existing unsupervised methods are mostly based

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

on three categories: Long Short Term Memory (LSTM)-used
temporal models include LSTM-AD [3] and LSTM-GSVM
[4], which specifically focus on the temporal attributes present
in the samples. Additionally, sequence models structured with
Autoencoders (AE) like TCN-AE [5] and LSTM-AE [6] create
sequence mappings by encoding and decoding. Moreover,
Generative Adversarial Network (GAN) models such as MTSDCGAN [7] and MAD-GAN [8] play a role in generalizing
the distribution of data. These methods have demonstrated
excellent performance in a wide range of fields, including the
Internet, industry, and medicine.
Sliding windows are widely used for data enhancement
and model design (Figure 1 (c)), aiming to weaken noise
through averaging or feature expansion. However, two major
limitations remain: (1) no fixed optimal window size exists
for different data distributions, and (2) window expansion
increases computational cost. Moreover, when combined with
LSTM-based models, it is difficult to provide interpretable
and precise utilization of temporal properties. Therefore, it
is worthwhile to explore generalizable and stable multi-stage
window methods that can adapt to different anomaly scenarios.
Based on the above findings and ideas, we propose a stagetwo window for feature remodeling and sequence prediction,
respectively. Using anomalous event traffic data as input, we
group them through a stage-one window and reshape the
features using the Graph Attention Networks (GAT) module to
reflect the state after noise reduction with the tail samples of
the window; we use the LSTM-AutoEncoder (LAE) module to
internally predict and externally reconstruct the data through
window grouping in the second stage to achieve stable interclass differences. The overall purpose is to generalize the
strong similarity of feature fluctuation trends of normal samples. We take this similarity as a major basis for unsupervised
anomaly detection, and the difference in anomalous samples
will be expressed as high scores. We validate our model
on several Internet traffic anomalies, and its performance is
outstanding compared to many superior methods. In summary,
the contributions of our study are mainly in the following:
• Domain-focused perspective: Unlike generic time-series
anomaly detection, our work specifically addresses
anomalous events in BGP communications, covering
routing dynamics, prefix updates, and inter-domain fluctuations in real-world routing data. We formulate this
problem in an unsupervised setting, where the absence of
ground truth increases the challenge of learning abnormal
patterns from unseen events.
• Efficient multi-window design: We propose Multivariate time-series Anomaly Detection with Multi-Window
(MAD-MulW), which integrates W-GAT and W-LAE
modules. W-GAT achieves adaptive noise reduction
within windows, while W-LAE enhances detection by
predictive reconstruction.
• Stable and robust performance: The proposed method
achieves consistently superior detection performance
across various anomalous events, improving the average
F1 score by at least 20% compared to baseline models.
Moreover, adaptive windowing contributes up to an 8%
improvement in F1, while maintaining robustness under

2

parameter changes and limited training samples.
Subsequently, Section II focuses on the related work to
anomaly detection. Section III presents a detailed explanation
of our model. Section IV contains an introduction to the
datasets, comparative models, and evaluation metrics. Section
V evaluates the model and analyzes the experimental results.
Finally, a summary of our work is presented in Section VI.
II. R ELATED W ORK
In this section, we describe the BGP anomaly detection
work and extend it to the development of anomaly detection
techniques for time series in recent years.
A. BGP Anomaly Detection Techniques
BGP is the Internet’s default inter-domain routing protocol
used to manage the connectivity between ASes. Over the past
20 years, many BGP events have been captured that threaten
the stability of the Internet.
Supervised learning-based BGP anomaly detection has
been extensively studied, and some of these methods affect
anomaly detection performance mainly by improving the
quantity or quality of features. Urbina Cazenave et al. [9]
showed that Support Vector Machines (SVM), Decision Trees,
and Naive Bayesian methods are evaluated for BGP event
classification. Arai et al. [10] and Xu et al. [11] extracted
features by an importance assessment algorithm to enhance the
model efficiency. Innovatively, Sanchez et al. [12] introduced
graph features to detect BGP anomalies, which are more robust
than traditional features. Another class of methods focused on
sample temporal relationships. The stacked-LSTM [13] and
the MSLSTM [14] both achieved significant improvement in
anomaly detection performance by mining temporal information. Peng et al. [15] went further by introducing a multidimensional attention mechanism to improve performance.
The supervised approach requires the labeling of the dataset,
so its applicability is limited to specific instances.
Unsupervised learning-based work is more sparse. Earlier
statistical-based methods used probabilistic models to detect
changes in the data, such as Principal Component Analysis
(PCA) [16], Generalized Likelihood Ratio Test [17] and ttest [18]. In recent years, Andrian et al. [19] implemented
DenStream, an anomaly detection engine based on clustering
techniques, and applied it to a large testbed consisting of
dozens of routers. Tal et al. [20] proposed the AP2Vec method,
which embeds both ASes and IP address prefixes into feature
vectors for BGP hijacking detection. BGP anomaly detection
still has a lot of room for research in unsupervised anomaly
detection techniques.
B. Time Series Unsupervised Anomaly Detection
Network traffic anomalous events can be viewed as anomaly
detection problems under multivariate time series, and the
design of unsupervised methods for this problem is highly
challenging and has been widely studied in many fields.
Classical unsupervised methods are widely used for
time series data anomaly detection, distance-based (K-Nearest

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

Neighbor, KNN [21]) methods modeled the local behavior
around each data point, density-based (Local Outlier Factor,
LOF [22]) methods discovered outliers by judging the density
around the object domain, clustering-based (Gaussian Mixture
Model, GMM [23]) methods grouped similar data points, and
projection-based (PCA [24]) and classification-based (Oneclass SVM, OCSVM [25]) methods performed spatial separation of the original data by a linear transformation to achieve
anomaly detection.
Deep learning-based unsupervised methods have numerous perspectives to model inter-metric dependencies. Convolutional networks have been applied to sequences for decades,
and Bai et al. [26] proposed a Temporal Convolutional Network (TCN) that focuses more on the importance of temporal
properties. On modeling inter-metric dependencies, Thill et al.
[3] and Ergen et al. [4] used LSTM for anomaly detection of
ECG and HTTP data after preprocessing the data with sliding windows for dimensionality enhancement, and designed
window-based error correction methods to optimize the results.
AE detects anomalies by deviations between encoded and decoded data of time series. Mo et al. [5] reconstruct time series
using TCN-AE and Hou et al. [6] use LSTM-AE for higherorder feature learning, both of which are groundbreaking in
anomaly detection. A relatively new area is the application of
GAN [27]. Similarly, Liang et al. [7] proposed a new multitimescale deep convolutional generative adversarial network
(MTS-DCGAN) framework for industrial time series anomaly
detection. Based on the several approaches mentioned above,
most of the existing studies focused on enhancement and
fusion. DAGMM [28] jointly optimized the parameters of the
deep autoencoder and the mixture model simultaneously in
an end-to-end fashion. MTAD-GAT [29] combined windows
with GAT to learn complex dependencies of multivariate time
series in time and feature dimensions and jointly predicted and
reconstructed models to achieve detection functions. MADGAN [8] took window subsequences with different resolutions as input and captured the temporal correlation of time
series distribution using LSTM-RNN. OmniAnomaly [30]
identified anomalies using key techniques such as random
variable concatenation, planar normalized flow, and robust
representation after segmenting the sequence with a window.
More recently, D3R [31] addressed the challenge of unstable
data by dynamically decomposing long-period time series
and employing diffusion-based reconstruction to control the
information bottleneck externally, which effectively reduces
false alarms caused by distribution drift.
In addition, several recent studies have further explored
advanced representation learning, uncertainty-aware reconstruction, and diffusion-based generative modeling for timeseries anomaly detection. Feng et al. [32] proposed SensitiveHUE for multivariate time-series anomaly detection, which
enhances the sensitivity to normal patterns by combining
reconstruction with heteroscedastic uncertainty estimation. Su
et al. [33] proposed an enhanced recurrent convolutional encoding method with attention-based representation learning for
chaotic time series anomaly detection, where empirical mode
decomposition, recurrent convolutional encoding, and attention
mechanisms are integrated to suppress noise and capture

3

nonlinear temporal dependencies. Zuo et al. [34] explored
unsupervised diffusion-based anomaly detection for time series, showing the potential of diffusion models in learning
normal temporal patterns and identifying abnormal deviations.
More recently, Pan et al. [35] proposed CT-DDPM, a copula
and Transformer-based denoising diffusion probabilistic model
for multivariate time-series anomaly detection, which uses
Gaussian Copula to model multivariate joint distributions and
Transformer-based denoising diffusion to capture temporal
dependencies and distributional deviations. Liu et al. [36]
further summarized recent advances in diffusion models for
anomaly detection, indicating that diffusion-based anomaly
detection has become an emerging research direction. In Table
I, we compare the different methods from four perspectives:
feature augmentation, time dependence, feature correlation,
and interpretability. The more targeted mining analysis of these
techniques improves the performance of each domain further
while also observing the high frequency of windows in both
data analysis and model construction. The performance of such
methods depends heavily on the length of the time window
and, therefore, requires targeted window lengths to provide
satisfactory performance. Some of the methods consider data
with different window sizes simultaneously in a multi-scale
manner, which brings the problem of data dimension multiplication along with stable performance. The relationship
between performance and consumption needs to be considered.

TABLE I
M ETHOD C OMPARE
Model

Data
Augmentation

TCN-AE

Data scaling

✓

LSTM-AE

✓

MTAD-GAT

/
Multi-time scale
sliding windows
Sliding windows

MAD-GAN

Sliding windows

✓

OmniAnomaly

Sliding windows

✓

D3R

Disturbance
Adaptive
sliding windows

✓

✓

✓

✓

✓

✓

MTS-DCGAN

Ours

Time
Dependence

✓

Feature
Correlation

Interpre.

✓

✓

✓

✓
✓

Undoubtedly, the main trends of existing methods focus on temporal properties guided by LSTM and are concerned with reconstructive adversarial methods, mainly AE
and GAN. Meanwhile, recent cutting-edge methods further
extend this trend toward attention-guided representation learning, uncertainty-aware reconstruction, multivariate distribution
modeling, and diffusion-based generation. These methods improve anomaly detection from different perspectives, but they
are mainly designed for general time-series or chaotic timeseries scenarios. At the same time, facing the problems of
irregular size and increased resource consumption brought
by the window strategies found above, we expect to design
adaptive window optimization models to achieve efficient and
generalized stable anomaly detection performance.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

4

W-LAE

Adaptive threshold

window
1× n

1× n

𝝎𝟏 × 𝒏

…

…
*

*

*

*

…

AEScore

×M

M× n

Mean
Min
Max

M× n

Data Processing

W-GAT

Train data：Normal
multivariate time series

window
*

…

*

Test data： Mixture
multivariate time series

*

𝝎𝟐 × 𝒏

…

M× n
Data processing

W-GAT: Stage-one

*

1× n

W-LAE: Stage-two

×M
Adaptive threshold

Fig. 2. Model Framework, MAD-MulW. The model has four main components: data processing, stage-one window, stage-two window, and adaptive threshold
strategy. Among them, we indicate in detail the learning of sample relationships and retention of the last sample by GAT (blue); and the reconstruction and
prediction of samples by LSTM-AE (green). Finally, the sample scores are obtained without changing the data dimensionality to achieve anomaly detection.

III. M ETHODOLOGY
We propose the unsupervised anomaly detection model
MAD-MulW for the current problems of low feature utilization, high model fluctuation, and weak event generalization in
the field of BGP anomaly detection. The overall structure is
shown in Figure 2.
A. Problem Definition
Our study concentrates on diverse large-scale network security events, specifically traffic monitoring and characterization
within a specified range. In practical inter-domain routing
systems, abnormal events such as worm propagation, power
failures, prefix leaks, and other network disruptions may cause
sudden and irregular changes in BGP update messages. These
changes are reflected in routing-related measurements, including announcement and withdrawal variations, prefix dynamics,
AS-path changes, and other communication-flow features.
Therefore, the actual problem addressed in this paper is to
identify abnormal timestamps whose routing behaviors significantly deviate from normal BGP communication patterns.
This paper focuses on features of the communication flow
change information, which can be regarded as a multivariate
time series of unsupervised anomaly detection. The input data
is defined as T = {x1 , x2 , . . . , xM } , x ∈ Rn , M represents
the number of time series samples, and n represents the feature
dimension corresponding to each time series sample.
Therefore

the tth sample can be represented as xt = x1t , x2t , . . . , xnt .
It should be noted that the univariate setting n = 1 is a special
case of multivariate time series [37].
We define the binary variable y ∈ 0, 1, where yt is labeled
as 0 if no unusual event occurs at timestamp t and 1 otherwise.
However, in real BGP monitoring scenarios, accurate anomaly
labels are usually unavailable before detection, and anomalous

events may appear with different durations, intensities, and
routing impacts. To address the problem of unsupervised
anomaly detection, we study the data features associated with
anomaly detection. The training input T should consist solely
of normal samples, denoted as yt = 0 for 1 ≤ t ≤ M .
After learning the normal temporal fluctuation patterns of BGP
communication features, a score of a trained model measures
the difference between the invisible sample x̂t , t > M
(All subsequent vectors with the symbol ˆ represent invisible
samples.) and T . The normal or abnormal labels of the
invisible sample are obtained by adaptive threshold strategy.
In this way, the proposed formulation is consistent with the
actual BGP anomaly detection scenario: the model learns
stable normal routing behaviors from historical BGP update
features and detects abnormal timestamps according to their
deviations from learned normal patterns, without relying on
labeled anomalous samples during training.
B. Data Processing
Standard data processing methods include data cleaning,
data normalization, and feature engineering, among others.
We process time series datasets in a targeted way to enhance
subsequent model learning.
First, we check the data for missing values. If any are
found, we fill the vacant part with feature values from the
previous time step. Subsequently, we manually clean the
columns containing unlearnable features. If the time series’
order already captures moment-specific information, the corresponding feature becomes redundant and can be cleaned.
Then, since the dataset comes with labels and our model is
an unsupervised model, we separate the features and labels.
Finally, the dataset is divided into a training set with all normal
samples and a testing set with both normal and abnormal
samples in a certain proportion.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

5

C. Multi-window Structure



Time series are characterized by their inherent temporal
continuity. On the one hand, this property can be exploited to
re-represent time series and construct datasets with enhanced
temporal properties. Thus, we propose and design a stage-one
window module W-GAT, which employs self-attentive generation to optimize the dataset. On the other hand, we incorporate
a stage-two window module W-LAE that replaces individual
time points with groups. This is achieved by utilizing the
LSTM model in conjunction with the AE model, enabling
prediction and anomaly detection in time series data.
1) Stage-one window W-GAT: Time series representation
is a process of reshaping the data, which facilitates the
completion of subsequent model tasks and more significantly
improves model efficiency. Ding et al. [38] used GAT to
explicitly model the different relationships in multimodal time
series to obtain a better representation of the input data. We
designed a stage-one window module W-GAT for reshaping
the representation of time series data, which consists of two
parts: the first part is a stage-one window design, and the
second part is a self-attentive model, as shown in Figure 3.
…

…

…

…

*

M
Hidden layers

n

…

…
*

…

*

…

GATwin× n
Window

*

*

*

1× n
…

Graph attention networks

Single

Fig. 3. stage-one window W-GAT.

Stage-one window group: The first part applies to all
datasets. We design a uniform window size parameter w1 and
wish to represent a timestamp xt with the past timestamps
[xt−w1 +1 , ..., xt−1 , xt ]. To avoid ambiguity between the
original sample and the remodeled representation, we denote
the W-GAT output at timestamp t as x̃t . A fully connected
network is constructed using graph nodes to represent each
timestamp in the window and weights α to indicate the degree
of association. The final theoretical representation is
x̃t =

wX
1 −1
i=0

αt,i xt−i ,

wX
1 −1

hi = σ 


X

(2)

where W is the weight matrix, σ(·) is the nonlinear activation
function, Ni represents the set of all neighbors of timestamp
i, and αij is attention coefficient in GAT which is calculated
as:
αij = P

exp LR aT [W xi ∥W xj ]



LR aT [W xi ∥W xk ]

k∈Ni exp

(3)



The updated node representation hi is a new feature representation for timestamp i, which reinforces the influence
of historical feature information on the current timestamp.
For each stage-one window ending at timestamp t, the final
W-GAT-remodeled feature x̃t is obtained from the output
representation of the current timestamp node in the window.
The stage-one window W-GAT plays a role in reshaping the
features in the overall model and is the key point of this paper.
Unlike previous work that utilized GAT to capture strong and
weak correlations at the time level or feature level, this section
uses samples as the updating unit and focuses only on the
degree of influence of all historical samples on the most recent
sample. By using GAT to adaptively update the weights, the
stability of the input information is improved by smoothing the
current feature fluctuations with historical information. At the
same time, it ensures that the dimension of the output data
is equal to the dimension of the original data, avoiding the
increase in space cost brought by GAT.
2) Stage-two window W-LAE: The focus of the stage-two
window is on data reconstruction based on time-series prediction. Distinguishing from traditional autoencoders, our approach specifies a window size of historical samples, predicts
the sample information at the next moment, and reconstructs
the individual timestamps using the property of multi-featured
variables, i.e., the size of the encoder’s inputs is not equal
to the size of the outputs. This design captures the temporal
relationship between samples and also increases the variability
between different classes of samples to achieve improved
detection performance. The structure of stage-two window WLAE is shown in Fig 4.
…

αt,i = 1

αij W xj 

j∈Ni

(1)

…

…

…

*

M

LSTM

LSTM

n

i=0

T

T

*

*

Window

1× n
*

…

AEwin× n

…

where αt,i denotes the attention weight assigned to the i-th
historical sample within the stage-one window at timestamp t.
Graph attention networks: It is difficult to capture the
optimal situation of different datasets by manually adjusting
the parameter α. So we utilize the self-attention network to
correlate the time series and obtain the timestamp attention
weights automatically.
The input of stacking graph attention layers is a set of
timestamp feature vectors, [xt−w1 +1 , ..., xt−1 , xt ]. For a
node i in the window graph, the updated representation is
defined as:

1× n

*

Encoder

Z

Decoder

Single

Fig. 4. stage-two window W-LAE.

Stage-two window group: The first part of the window
group is designed to allow multiple previous timestamps to
replace the current timestamp. In this case, we set the stagetwo window parameter w2 . Based on the remodeled sequence

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

6

T̃ = {x̃1 , x̃2 , . . . , x̃M }, the input window for predicting
timestamp t is defined as:
(w )
X t 2 = [x̃t−w2 , x̃t−w2 +1 , . . . , x̃t−1 ] ∈ Rw2 ×n

(4)

Note that here the window group represents a certain timestamp but does not contain the time series at that time so that
the purpose of predicting the unknown time series from known
previous data can be achieved.
The role of the encoder is to map the historical window in(w )
put X t 2 into the latent representation zt through a nonlinear
transformation.


(w )
zt = fenc X t 2 ; θ enc
(5)
(w )
where X t 2

= [x̃t−w2 , . . . , x̃t−2 , x̃t−1 ] denotes the stagetwo historical window input, and θ enc denotes the parameters
of the LSTM encoder.
The role of the decoder is to predict the feature representation at timestamp t from the latent variable zt . The mapping
process can be expressed as follows:
x̂t = fdec (zt ; θ dec )

n

st =

(6)

where x̂t ∈ Rn is the predicted representation of the current
timestamp, and θ dec denotes the parameters of the decoder.
For normal samples, the prediction output x̂t is expected to
be close to the corresponding W-GAT-remodeled feature x̃t ,
i.e., x̂t ≈ x̃t .
The main feature of the W-LAE module in this part is
that the neural network used for the mapping process is fixed
as LSTM. The principle of training W-LAE is to minimize
reconstruction errors. On the one hand, it retains the strong
generalization of the reconstruction-based approach under unsupervised tasks, and on the other hand, it also preserves the
information on the relationship between features in the process
of encoding and decoding. Meanwhile, the hidden variable zt
can be regarded as an important feature extracted from the
input data that is sufficient for subsequent analysis. All these
factors guarantee the excellent performance of W-LAE in the
unsupervised anomaly detection task, which will be verified
in the subsequent experiments.

1X d
1
x̂t − x̃dt
∥x̂t − x̃t ∥1 =
n
n

where n is the feature dimension and d indexes each feature. A
larger st indicates a larger deviation from the learned normal
temporal pattern.
The reconstruction error is returned as a loss function during
the training process, to make the prediction result similar to
the actual timestamp. Given N valid training timestamps after
window construction, the training objective is formulated as
follows:
L=

N
N
1 X1
1 X
st =
∥x̂t − x̃t ∥1
N t=1
N t=1 n

Our unsupervised anomaly detection model is mainly divided into a training part and a testing part, and these parts of
the model are made to unite into a whole by designing suitable
loss functions and score functions by ourselves.
The original dataset has been cleaned up after data processing. We completed the data reshaping through a stage-one
window W-GAT, which step changed the data feature values
in the time dimension to reduce noise in continuous samples.
After that, the prediction task is implemented by the W-LAE
module with data grouping and data reconstruction. For each
(w )
timestamp t, the W-LAE module takes X t 2 as input and
outputs the predicted feature vector x̂t . The deviation between
x̂t and the corresponding W-GAT-remodeled feature x̃t is used
to measure the abnormality of timestamp t. Specifically, the
timestamp-level anomaly score is defined as follows:

(8)

During testing, the timestamp-level anomaly score st is used
for adaptive threshold-based anomaly detection. The Mean and
Standard Deviation approach is a commonly used statistical
method to set adaptive thresholds based on the distribution of
the model’s output loss values.
Calculation of Mean and Standard Deviation: Let
Strain = {s1 , s2 , . . . , sN } denote the set of anomaly scores
computed from the normal training samples, where N is the
number of valid training timestamps after window construction. The mean (µ) and standard deviation (σ) of the anomaly
scores are calculated as follows:
N

1 X
µ=
st
N t=1

(9)

v
u
N
u1 X
σ=t
(st − µ)2
N t=1

(10)

Threshold Determination: The anomaly detection threshold is defined by setting a threshold level that incorporates a
multiple of the standard deviation added to the mean. This is
expressed as:
δ =µ+k×σ

D. Our Model

(7)

d=1

(11)

where k is a scaling factor that determines the sensitivity of
the threshold to variations in the loss distribution. The value
of k should be selected based on the specific application and
acceptable risk levels of false positives and negatives. In the
BGP anomaly detection task, k = 25.
For each new data point, the corresponding loss value is
computed and compared against the established threshold. For
an unseen sample, if its anomaly score satisfies st > δ, it is
identified as abnormal; otherwise, it is regarded as normal:
(
1, st > δ,
ŷt =
(12)
0, st ≤ δ.
Following multiple training rounds and optimization based
on the complete process described above, the model performance can be validated on a test set.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

IV. E XPERIMENTAL S ETUP
A. Datasets
The datasets used in this thesis are derived from several
classes of classical BGP anomalous events [39]. We summarize the information of each dataset in Table II, and its detailed
description is shown below.
TABLE II
BGP A NOMALY E VENT DATASETS
Dataset

Total

Code Red II

7136

Nimda

10336

Slammer

7200

Moscow

7200

Malaysian

7200

Anomaly
(Rate)
472
(6.61%)
353
(3.42%)
1130
(15.69%)
171
(2.38%)
185
(2.57%)

Features

Time or Field

48

2001.07.17-2001.07.21

48

2001.09.15-2001.09.23

48

2003.01.23-2003.01.27

48

2005.05.23-2005.05.27

48

2015.06.10-2015.06.14

Code Red II: On July 19, 2001, the Code Red II worm
started its spreading across the global network. Since the
beginning of the anomaly, an exponentially growing eight-fold
increase in the BGP advertisement rate was observed over a
period of about eight hours.
Nimda: On September 18, 2001, as the Nimda worm started
its propagation, Over a period of roughly two hours, the rrc00
collector perceived BGP advertisement rates exponentially
ramped up by a factor of 25. The advertisement rate then
decayed gradually over several days.
Slammer: The Slammer worm was released on Jan 25,
2003, 5:31 UTC, infected at least 75,000 hosts in just over
30 minutes and it was reported that a number of critical ASAS peering links were operating above critical load thresholds
during the attack period.
Moscow Blackout: The Moscow Power Blackout occurred
on May 25, 2005, and lasted several hours. The effect was
apparent at the RIS remote route collector in Vienna (rrc05)
through a surge in announcement messages arriving from peer
AS 12793.
Malaysian Telecom Leak: Malaysian Telecom (AS 4788)
leaked one-third of the IP prefixes in its global routing table
to backbone provider Level 3 (AS 3549) from June 12, 2015.
It left the company inundated with data, resulting in severe
packet loss and performance degradation.
By using the event time period and the ASes involved,
complete BGP update data can be obtained from the Route
Views [40] and RIPE NCC [41] websites. Several statistical
features can be constructed by parsing the packets and extracting specific information. Our dataset contains 48 features,
which are divided into two categories: Volume features and
AS-path features, and described in Appendix Table VI.
B. Comparative Methods
To ensure comprehensive coverage of the comparison methods, we carefully selected 11 techniques that encompass
a wide range of unsupervised approaches, including both

7

classical and the latest methods. Among them, the classical
methods include KNN, Cluster-based Local Outlier Factor
(CBLOF), Histogram-based Outlier Score (HBOS), Isolation
Forest (iForest), OCSVM, and Principal Component Analysis
(PCA). The latest methods include Deep Autoencoding Gaussian Mixture Model (DAGMM) [28], Multivariate Time-series
Anomaly Detection via Graph Attention Network (MTADGAT) [29], Multivariate Anomaly Detection with Generative
Adversarial Network (MAD-GAN) [8], OmniAnomaly [30],
and D3R [31], and these methods have been widely approved
and used in time series anomaly detection work in recent years.
C. Evaluation Metrics
We view the BGP anomaly detection as a classification
problem, thus choosing Accuracy, P recision, Recall, and
F 1 as the evaluation metrics. The dataset of real anomalous
events exhibits a significant class imbalance. Among them, F 1
is a weighted average of model precision and recall that can be
used to measure the precision of unbalanced data. To facilitate
comparison, we assign the abnormal samples as the positive
class and the normal samples as the negative class. This allows
classification into True Positive (TP), False Positive (FP), True
Negative (TN), or False Negative (FN).
According to the above four situations, we can calculate
each performance metric as follows:
Accuracy =

TP + TN
TP + TN + FP + FN

(13)

TP
TP + FP

(14)

TP
TP + FN

(15)

Precision =
Recall =
F1 =

2 × Precision × Recall
Precision + Recall

(16)

D. Model Parameters
The performance of a model is sensitive to variable parameters. We split the normal data into a training set and a testing
set with a ratio of 7:3, the training set consists of normal
data and the test set contains normal and abnormal data. The
training parameters are chosen as follows: learning rate is
1e−2, the epoch is 10, the W-GAT window is 15, and W-LAE
is 11. Part of the parameter setting of the model is adjusted
according to the aggregation of the concrete experiment. This
selection can help the model achieve excellent and stable
results on many datasets. Our model and all experiments are
implemented on Python, relying on the PyTorch framework,
the sklearn library, and other related libraries and functions.
V. E XPERIMENTS AND R ESULTS
This section focuses on evaluating the model’s performance
in unsupervised anomaly detection and assessing the effectiveness of the stage-two window design for each structure
component. We then discuss the rationality of each of the three
hyperparameter designs separately.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

8

TABLE III
E XPERIMENT RESULTS

Dataset

Code Red II

Nimda

Slammer

Moscow

Malaysian

Average

Classical Model

Model

Latest Model

Ours

KNN

CBLOF

HBOS

iForest

OCSVM

PCA

MTAD-GAT

MAD-GAN

DAGMM

OmniAnomaly

D3R

Acc.

85.29

85.03

85.31

87.22

84.87

85.85

88.96

76.62

94.96

90.65

81.53

97.82

Pre.

51.62

50.92

51.69

56.99

50.45

53.17

66.11

64.96

65.57

65.81

79.98

96.54

Rec.

52.36

51.34

52.47

60.18

50.65

54.63

81.33

64.04

50.53

72.79

52.87

96.13

F1

51.72

50.89

51.81

57.07

50.34

53.56

70.23

64.46

57.14

68.43

50.54

96.33

Acc.

65.78

64.48

66.75

70.69

64.43

67.37

69.75

72.72

67.41

68.09

39.54

86.76

Pre.

58.72

55.12

61.41

72.37

54.96

63.13

66.28

65.48

69.41

66.12

62.96

86.21

Rec.

53.49

52.05

54.56

58.95

51.99

55.25

66.06

70.66

8.35

65.34

52.28

85.04

F1

50.31

48.43

51.72

57.45

48.34

52.61

66.17

66.28

14.90

65.60

32.64

85.55

Acc.

83.06

82.14

84.36

87.47

82.03

83.78

83.63

77.32

83.19

80.20

62.11

98.19

Pre.

65.59

63.04

69.21

77.85

62.73

67.59

69.54

70.20

38.24

69.43

74.47

98.12

Rec.

60.60

58.87

63.07

68.95

58.66

61.97

70.79

76.58

11.50

79.97

51.08

97.93

F1

62.17

60.12

65.08

72.03

59.87

63.78

70.07

71.65

17.69

71.72

40.51

98.02

Acc.

91.99

91.90

91.99

92.12

91.74

91.99

98.24

73.38

97.92

98.06

95.34

99.36

Pre.

60.79

60.56

60.79

61.18

60.10

60.79

80.92

66.16

53.85

81.13

81.00

99.67

Rec.

91.90

91.00

91.90

93.40

89.21

91.90

80.92

71.55

100.00

71.13

97.21

91.03

F1

65.49

65.13

65.49

66.08

64.41

65.49

80.92

67.06

70.00

75.11

86.91

94.90

Acc.

91.71

91.51

91.51

92.26

90.96

91.99

97.13

83.52

96.94

95.97

96.24

99.26

Pre.

60.46

59.92

59.92

62.00

58.37

61.23

70.79

76.80

45.45

66.41

84.54

99.62

Rec.

87.60

85.65

85.65

93.14

80.10

90.36

69.13

70.17

94.59

75.83

96.48

90.24

F1

64.80

63.98

63.98

67.16

61.62

65.98

70.02

72.48

61.40

69.94

89.36

94.40

Acc.

83.57

83.01

83.98

85.95

82.81

84.20

87.54

76.71

88.08

86.59

74.95

96.28

Pre.

59.44

57.91

60.60

66.08

57.32

61.18

70.73

68.72

54.50

69.78

76.59

96.03

Rec.

69.19

67.78

69.53

74.92

66.12

70.82

73.65

70.60

52.99

73.01

69.98

92.07

F1

58.90

57.71

59.62

63.96

56.92

60.28

71.48

68.39

44.23

70.16

59.99

93.84

A. Basic Experiment
In this section, we compare the performance differences of
numerous unsupervised anomaly detection methods on BGP
anomaly traffic datasets, and the results are shown in Table
III. Under each metric, the optimal results are bolded and
underlined. Due to the small proportion of anomaly samples
in datasets, detection becomes significantly more challenging.
Consequently, the F1 metric provides a more comprehensive
evaluation of the model’s performance in both normal and
anomalous sample identification. From the experimental results, we can clearly see that the latest methods generally
outperform the classical detection models, mainly because the
classical methods focus more on the partial attributes of events.
Although more efficient, they are not as comprehensive as
the latter in terms of detection performance after all. However, despite their general applicability, these latest models
exhibit considerable performance fluctuations across different
BGP anomaly events, indicating limited adaptability to eventspecific characteristics.
We calculate the average of each model metric at the end of
Table III, and the results clearly show that our model improves
by over 20% on the most critical F1 metric compared to the
best baseline and consistently achieves above 90% on accuracy, precision, and recall. To further present the results from a
statistical perspective, we analyze the F1 scores across the five
BGP anomaly datasets. Our method achieves an average F1
score of 93.84%±4.84%, while the strongest baseline in terms
of average F1 score, MTAD-GAT, achieves 71.48% ± 5.55%.
This indicates an absolute improvement of 22.36 percentage
points and a relative improvement of 31.28%. Moreover, when
comparing our method with the best-performing baseline on
each individual dataset, the F1 improvements on Code Red II,
Nimda, Slammer, Moscow, and Malaysian are 26.10, 19.27,
25.99, 7.99, and 5.04 percentage points, respectively. The
improvement is positive on all five datasets, with an average
gain of 16.88±9.91 percentage points. These statistical results
demonstrate that the proposed method achieves consistent and
substantial improvement across different BGP anomaly events,
rather than only a slight numerical increase. More importantly,
our approach demonstrates strong stability across all tested
events, benefiting from its capability to capture BGP-specific
anomaly features.
B. Window validity
We have two window parameters, where the W-GAT window focuses on enhancing temporal correlations and feature

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

Code Red II

Nimda

9

Slammer

Error Num = 37

1

Error Num = 124

7.94

5.83

1
0
Error Num = 257

Noise Reduction

Window Size

0
1.19

1
0

75

Anomaly Sample

F1 Score

(a)

Normal Sample

(b)

Fig. 5. W-GAT module validation. (a) Performance differences between the manual and adaptive windows; (b) The predicted labels of the test samples under
different window sizes.

reconstruction, and the W-LAE window is responsible for prediction. To validate their effectiveness, we design experiments
by selectively enabling or disabling these two components.
Specifically, the W-LAE window is verified by comparing
cases with and without W-LAE, while the W-GAT window is
further examined under multiple conditions: (i) w/o W-GAT,
(ii) w/ Manual W-GAT, and (iii) w/ Adaptive W-GAT. When
the W-GAT window size is set to 15 and the W-LAE window
size is set to 11, the experimental results on three datasets are
shown in Table IV. The findings indicate that enabling only
W-LAE (without W-GAT) achieves moderate performance
improvement compared to using only W-GAT, confirming the
necessity of both windows. Introducing a manual W-GAT
window (with W-LAE) results in a 4%-11% increase in the F1
score, while the GAT-based adaptive window (with W-LAE)
achieves the best performance, improving the F1 score by an
additional 1%-6% and reaching 96.33%, 85.55%, and 98.02%
for Code Red II, Nimda, and Slammer, respectively. These
results clearly demonstrate that (i) both W-GAT and W-LAE
windows contribute significantly to performance gains, and (ii)
adaptive W-GAT design provides the most effective enhancement by dynamically optimizing temporal feature aggregation.
TABLE IV
W INDOW EXPERIMENT RESULTS

performance improvement, even up to an 8% difference on
the Slammer dataset. The optimal manual window value is
not fixed for different datasets, and the impact of the window
is inconsistent, showing a tendency to fluctuate upward with
the window size. In contrast, the GAT adaptive window can
determine the importance of the sample by the parameter value
instead of fixing it to 0 or 1. This adaptive nature allows
the F1 score to show a steady upward trend as the window
size increases, ensuring that each dataset achieves near-optimal
results in the GAT window.
A potential explanation is that the adaptive window of GAT
simulates a manual window, using the connection weights
between the time series within the window to simulate the
window size, ultimately achieving a near-optimal result. In
particular, the performance improvement of the window from
presence to absence is the largest, and the explanation is also
related to the presence of noise in the time series itself, as it
is a non-ideal curve. The addition of the window effectively
smoothes out the noise, eliminates outliers, and ensures overall
smoothness. As shown in Figure 5(b), the fluctuations of the
samples due to misclassification decrease significantly with
the increase of the window size. Additionally, we artificially
assign weights to the manual windows to simulate the adaptive
windows of GAT, aiming to assess the impact of weights as
opposed to fixed-value windows.

Dataset

Window 1
(Size 15)

Window 2
(Size 11)

Code Red II

Nimda

Slammer

w/ W-GAT

w/o W-LAE

88.64

68.43

81.02

w/o W-GAT

w W-LAE

86.31

73.46

86.32

w/ Manual W-GAT

w W-LAE

95.14

79.72

90.08

w/ Adaptive W-GAT

w W-LAE

96.33

85.55

98.02

However, is it a coincidence that the current window size
makes excellent results? To answer this question, we obtain
the experimental results in Figure 5(a). It is obvious from
the three figures that the results of manual and adaptive are
similar for small windows in the early stage, but as the
window increases, the adaptive window shows a significant

C. Parameter Validity
In the course of our experiments, three questions arose as
follows:
• Q1: What is the effect of the number of training samples
on the results?
• Q2: How does the threshold value affect the results?
• Q3: What are the stage-two window parameters set to?
• Q4: How does the model balance training, inference, size,
and performance?
1) The number of training samples: The first question is
due to the excellent performance and reasonable design of our
model in the basic experiments described above, which makes

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

10

Code Red II

Nimda

Slammer

98.89
97.41
85.54

98.14
98.10

F1 Score

Sample Num

98.14
86.01

85.20
87.74

Train Sample Num : Test Sample Num

Fig. 6. The variation of the results with different sample ratios.

at the lowest and highest thresholds. Since the change of
threshold value has little effect on the division at smoothing,
the model can achieve good experimental results within a
certain range of threshold values. The adaptive strategy clarifies the importance of threshold selection and also shows that
achieving dynamic thresholds is a problem that needs to be
studied in depth in subsequent work.
3) Manual window design: The third question is the setting
of the stage-two window parameters. The trends of detection
performance for different datasets with different window parameters are shown in Figure 8.

F1 Score

us look forward to further investigating whether the MADMulW model can achieve good detection performance with
only a small number of training samples. So, there was a fixed
number of test samples, and experiments were conducted for
different numbers of training samples, and the experimental
results are shown in Figure 6. The horizontal coordinates in
the figure are the ratio of the number of train sets to the number
of test sets, and the vertical coordinates correspond to the
different metric values. The overall trend is more intuitive,
and the detection performance improves as the number of
train samples increases. It is worth noting that our model
generally achieves optimal results using a train set with less
than the number of test samples, which again demonstrates the
stable and generalized detection performance of our model.
The small amount of train data and high detection results
indicate that the model requires low learning costs and fast
learning. Notably, near-optimal performance is attained even
with sparse samples, thereby reducing the restrictiveness of
the anomaly detection task and enhancing its applicability in
diverse situations.

Size=15

(a)
97.86

Acc
F1

85.20

F1 Score

96.40

86.34

Size=11
98.30

98.14

Window Size

(b)
Fig. 8. The variation of the results with different window sizes.
Threshold Block

Fig. 7. The variation of the results with different thresholds.

2) Adaptive threshold strategy: The second question focuses on the study of the adaptive threshold strategy. Figure 7
shows the trend of the effect of different thresholds (horizontal
coordinates) on the F1 score (vertical coordinates) of the three
datasets. Both too-small and too-large thresholds lead to many
misclassification cases, while the range of better thresholds is
narrower, and the selection of thresholds varies on different
datasets. Under our adaptive threshold strategy, the divided
thresholds do not go through the lowest classification results

Upon fixing the size of the AE window, we observed a
consistent trend in the size of the GAT window across all
datasets: a gradual increase followed by stabilization (Figure
8(a)). To ensure stable and outstanding results across multiple
datasets while considering the minimum sample size, we fixed
the window size at 15 for the W-GAT module.
The AE window serves to achieve prediction, so the size of
the AE window directly affects the temporal memorability of
the LSTM during computation. the LSTM needs to learn and
infer information from features at known moments to unknown
moments, while the long- and short-term dependence of the
samples also determines the amount of information required.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

11

Our experimental results found (Figure 8(b)) that when the
AE window increases, the different datasets do not show a
clear and uniform trend. However, when the window is at
11, a better state can be achieved by considering short-term
temporal information.
4) Model cost: To verify the claim that our method achieves
both computational efficiency and high detection performance,
we conducted a comparative experiment to measure the time,
space, and detection capability of our model against several
baseline methods. Specifically, we evaluated four metrics:
Training Time, Inference Time, Model Size, and Avg. F1. All
experiments were carried out on the same hardware and BGP
anomaly dataset to ensure fairness, allowing a direct comparison of computational efficiency and practical applicability.

Volume Feature
AS-path Feature

TABLE V
C OMPARISON OF COMPUTATIONAL COST, MODEL SIZE , AND DETECTION
PERFORMANCE

Method

Training Time
(s / epoch)

Inference Time
(s)

Model Size
(MB)

Avg. F1
(%)

MTAD-GAT

1.07

58.50

1.45

71.48

MAD-GAN

3.00

147.00

0.027

68.39

DAGMM

4.43

0.19

0.039

44.23

OmniAnomaly

167.68

32.04

8.45

70.16

D3R

4.02

31.78

12.70

59.99

Ours

18.86

16.03

0.80

93.84

Table V summarizes the results. Our method requires a
moderate training time of 18.86s per epoch, which is longer
than MTAD, MAD, DAGMM, and D3R but substantially
shorter than Omni. More importantly, it achieves the fastest
inference time among all methods (16.03s) while maintaining
a compact model size of only 0.80MB. In terms of detection
performance, our model reaches an average F1 score of
93.84%, which significantly surpasses all baselines, including
MTAD (71.48%) and Omni (70.16%). These results indicate
that our approach provides the best overall balance between
inference efficiency, lightweight memory footprint, and high
detection accuracy, demonstrating its strong practicality for
real-world BGP anomaly detection scenarios.
So far, we have demonstrated the stability and generalization
of our model design, as well as the stringency of the parameter
design, through several experiments.

Fig. 9. The distribution of the normalized features and the differential of their
distribution.

reflecting the sensitive relationship between the sample scores
and the data. The horizontal coordinates of the box plot are
the 48 different features, and the vertical coordinates are the
distributions of the output vectors of the different features after
being modeled (normalized due to the different scales of the
different features). The wider distribution of a feature means
that the feature is more sensitive to the variation of sample
scores and is therefore regarded as a more important feature in
the model output. Thus, we quantified the difference in the distribution of features using line plots, where the green solid line
represents the interquartile range difference between the value
represented by the upper quartile and the value represented
by the lower quartile of the box plot, and the blue dashed
line represents the full range difference between the upper and
lower whisker limits of the box plot. It is obvious from the
trend of the results that it is particularly important to focus
on the volume features of the announcements and the path
features of the ASes. This is in line with the mass broadcasting
and alternative path adjustment when BGP anomalies occur.
Meanwhile, the result also provides good guidance for the
subsequent optimization of feature engineering.
VI. C ONCLUSION

D. Result Interpretation
In parts A and B of this section, we validate the accuracy
and validity of the model. In part C, we validate the sensitivity
of the model involving the parameters, which is the most
important validation and debugging technique of the model
that maintains acceptable model behavior and predictions
when the data is intentionally interfered with or simulated by
other means [42]. In order to increase the credibility of the
model’s features and to gain a deeper understanding of the
reasons behind the model’s decisions, we have performed an
interpretability analysis of the results in this subsection. Figure
9 jointly characterizes the data features with the model outputs,

In this paper, we innovatively propose a stage-two window
model for multivariate time series anomaly detection in order
to achieve the detection and analysis of large-scale network
anomalous events. The model employs a stage-one W-GAT
window for feature reconstruction and a stage-two W-LAE
window for time series prediction. Our proposed method
outperforms baseline methods and advanced models on the
BGP dataset. Furthermore, our model is characterized by
low training costs and fast learning and achieves excellent
detection results even with limited training samples. These
characteristics also indicate the potential feasibility of MADMulW in resource-constrained router environments, since it

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

operates on extracted BGP update features, preserves the
original feature dimension after W-GAT processing, and can
be deployed as a lightweight monitoring component on the
router control plane or an external route collector without
directly affecting packet forwarding. Future work will further
investigate model compression, quantization, and hardwarespecific optimization for practical router-side deployment.
Moreover, our method demonstrates applicability to a wide
range of datasets thanks to its automatic reshaping capability
and stable prediction performance.
ACKNOWLEDGMENTS
This work was supported in part by the National Key R&D
Program of China 2025YFA1510900, by the National Natural
Science Foundation of China 62503423 and 62301492, by the
Baima Lake Laboratory Joint Fund of Zhejiang Provincial
Natural Science Foundation of China LBMHZ25F020002,
by the Zhejiang Provincial Natural Science Foundation of
China ZCLY24F0302. All authors are with the Institute
of Cyberspace Security, Zhejiang University of Technology,
Hangzhou 310023, China. S. Peng, Z. Ruan, and Q. Xuan are
also with Binjiang Institute of Artificial Intelligence, ZJUT,
Hangzhou 310056, China.
A PPENDIX
F EATURE D ESCRIPTION
A detailed description of the 48 features of the BGP
anomaly event datasets.
R EFERENCES
[1] A. M. Khan and M. Osińska, “Comparing forecasting accuracy of
selected grey and time series models based on energy consumption in
brazil and india,” Expert Systems with Applications, vol. 212, p. 118840,
2023.
[2] D. Dimoudis, T. Vafeiadis, A. Nizamis, D. Ioannidis, and D. Tzovaras,
“Utilizing an adaptive window rolling median methodology for time
series anomaly detection,” Procedia Computer Science, vol. 217, pp.
584–593, 2023.
[3] M. Thill, S. Däubener, W. Konen, T. Bäck, P. Barancikova, M. Holena,
T. Horvat, M. Pleva, and R. Rosa, “Anomaly detection in electrocardiogram readings with stacked lstm networks,” in Proceedings of the 19th
Conference Information Technologies-Applications and Theory (ITAT
2019). CEUR-WS, 2019, pp. 17–25.
[4] T. Ergen and S. S. Kozat, “Unsupervised anomaly detection with lstm
neural networks,” IEEE transactions on neural networks and learning
systems, vol. 31, no. 8, pp. 3127–3141, 2019.
[5] R. Mo, Y. Pei, N. V. Venkatarayalu, P. Nathaniel, A. Premkumar, S. Sun,
and S. K. K. Foo, “Unsupervised tcn-ae-based outlier detection for
time series with seasonality and trend for cellular networks,” IEEE
Transactions on Wireless Communications, 2022.
[6] B. Hou, J. Yang, P. Wang, and R. Yan, “Lstm-based auto-encoder model
for ecg arrhythmias classification,” IEEE Transactions on Instrumentation and Measurement, vol. 69, no. 4, pp. 1232–1240, 2019.
[7] H. Liang, L. Song, J. Wang, L. Guo, X. Li, and J. Liang, “Robust unsupervised anomaly detection via multi-time scale dcgans with forgetting
mechanism for industrial multivariate time series,” Neurocomputing, vol.
423, pp. 444–462, 2021.
[8] D. Li, D. Chen, B. Jin, L. Shi, J. Goh, and S.-K. Ng, “Mad-gan:
Multivariate anomaly detection for time series data with generative
adversarial networks,” in International conference on artificial neural
networks. Springer, 2019, pp. 703–716.
[9] I. O. de Urbina Cazenave, E. Köşlük, and M. C. Ganiz, “An anomaly
detection framework for bgp,” in 2011 International Symposium on
Innovations in Intelligent Systems and Applications. IEEE, 2011, pp.
107–111.

12

[10] T. Arai, K. Nakano, and B. Chakraborty, “Selection of effective features
for bgp anomaly detection,” in 2019 IEEE 10th International Conference
on Awareness Science and Technology (iCAST). IEEE, 2019, pp. 1–6.
[11] M. Xu and X. Li, “Bgp anomaly detection based on automatic feature
extraction by neural network,” in 2020 IEEE 5th Information Technology
and Mechatronics Engineering Conference (ITOEC). IEEE, 2020, pp.
46–50.
[12] O. R. Sanchez, S. Ferlin, C. Pelsser, and R. Bush, “Comparing machine
learning algorithms for bgp anomaly detection using graph features,” in
Proceedings of the 3rd ACM CoNEXT Workshop on Big DAta, Machine
Learning and Artificial Intelligence for Data Communication Networks,
2019, pp. 35–41.
[13] S. Chauhan and L. Vig, “Anomaly detection in ecg time signals via
deep long short-term memory networks,” in 2015 IEEE International
Conference on Data Science and Advanced Analytics (DSAA). IEEE,
2015, pp. 1–7.
[14] M. Cheng, Q. Li, J. Lv, W. Liu, and J. Wang, “Multi-scale lstm model for
bgp anomaly classification,” IEEE Transactions on Services Computing,
vol. 14, no. 3, pp. 765–778, 2018.
[15] S. Peng, J. Nie, X. Shu, Z. Ruan, L. Wang, Y. Sheng, and Q. Xuan,
“A multi-view framework for bgp anomaly detection via graph attention
network,” Computer Networks, vol. 214, p. 109129, 2022.
[16] A. Lakhina, M. Crovella, and C. Diot, “Diagnosing network-wide traffic
anomalies,” ACM SIGCOMM computer communication review, vol. 34,
no. 4, pp. 219–230, 2004.
[17] S. Deshpande, M. Thottan, T. K. Ho, and B. Sikdar, “An online
mechanism for bgp instability detection and analysis,” IEEE transactions
on Computers, vol. 58, no. 11, pp. 1470–1484, 2009.
[18] M. C. Ganiz, S. Kanitkar, M. C. Chuah, and W. M. Pottenger, “Detection
of interdomain routing anomalies based on higher-order path analysis,”
in Sixth International Conference on Data Mining (ICDM’06). IEEE,
2006, pp. 874–879.
[19] A. Putina and D. Rossi, “Online anomaly detection leveraging streambased clustering and real-time telemetry,” IEEE Transactions on Network
and Service Management, vol. 18, no. 1, pp. 839–854, 2020.
[20] T. Shapira and Y. Shavitt, “Ap2vec: an unsupervised approach for
bgp hijacking detection,” IEEE Transactions on Network and Service
Management, 2022.
[21] V. Hautamaki, I. Karkkainen, and P. Franti, “Outlier detection using
k-nearest neighbour graph,” in Proceedings of the 17th International
Conference on Pattern Recognition, 2004. ICPR 2004., vol. 3. IEEE,
2004, pp. 430–433.
[22] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “Lof: identifying
density-based local outliers,” in Proceedings of the 2000 ACM SIGMOD
international conference on Management of data, 2000, pp. 93–104.
[23] M. Bahrololum and M. Khaleghi, “Anomaly intrusion detection system
using gaussian mixture model,” in 2008 Third International Conference
on Convergence and Hybrid Information Technology, vol. 1. IEEE,
2008, pp. 1162–1167.
[24] A. Lakhina, M. Crovella, and C. Diot, “Characterization of network-wide
anomalies in traffic flows,” in Proceedings of the 4th ACM SIGCOMM
conference on Internet measurement, 2004, pp. 201–206.
[25] S. M. Erfani, S. Rajasegarar, S. Karunasekera, and C. Leckie, “Highdimensional and large-scale anomaly detection using a linear one-class
svm with deep learning,” Pattern Recognition, vol. 58, pp. 121–134,
2016.
[26] S. Bai, J. Z. Kolter, and V. Koltun, “An empirical evaluation of generic
convolutional and recurrent networks for sequence modeling,” arXiv
preprint arXiv:1803.01271, 2018.
[27] W. Jiang, Y. Hong, B. Zhou, X. He, and C. Cheng, “A gan-based
anomaly detection approach for imbalanced industrial time series,” IEEE
Access, vol. 7, pp. 143 608–143 619, 2019.
[28] B. Zong, Q. Song, M. R. Min, W. Cheng, C. Lumezanu, D. Cho, and
H. Chen, “Deep autoencoding gaussian mixture model for unsupervised
anomaly detection,” in International conference on learning representations, 2018.
[29] H. Zhao, Y. Wang, J. Duan, C. Huang, D. Cao, Y. Tong, B. Xu, J. Bai,
J. Tong, and Q. Zhang, “Multivariate time-series anomaly detection via
graph attention network,” in 2020 IEEE International Conference on
Data Mining (ICDM). IEEE, 2020, pp. 841–850.
[30] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proceedings of the 25th ACM SIGKDD international
conference on knowledge discovery & data mining, 2019, pp. 2828–
2837.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

13

TABLE VI
F EATURE D ESCRIPTION
No.

Feature name

Describe

Category

1

Number of
announcements

General number of messages received that contain a request to include a BGP AS path in the Routing
Information Base (RIB).

Volume

2

Number of withdrawals

General number of messages received that contain a request to remove a BGP AS path in the RIB.

Volume

3

Number of duplicate
announcements

The mechanism keeps track of previously announced paths and marks consecutive announcements with
the same attributes as duplicates.

Volume

4

Number of duplicate
withdrawals

The mechanism keeps track of previously announced paths and marks consecutive announcements with
the same attributes as duplicates.

Volume

5

Number of non-duplicate
announcements

Announcements that contain information different from the stored in the RIB.

Volume

6

Number of non-duplicate
withdrawals

Withdrawals that contain information different from the stored in the RIB.

Volume

7

Number of flaps

When a path is announced, succeeded by a withdrawal message that removes it from the RIB, then the
same path is announced again with the same attributes.

Volume

8

Number of new
announcements after
withdrawal

When a path to a prefix is announced, then removed from the RIB, and then a path to the same prefix
is announced with different attributes.

Volume

9

Number of plain new
announcements

Announcements for a prefix that was never stored in the RIB.

Volume

10

Number of implicit
withdrawals with same
path

Consecutive announcements for the same prefix with the same path but with at least one different
attribute (e.g. MED, LOCAL PREF, ORIGIN).

Volume

11

Number of implicit
withdrawals with
different paths

Consecutive announcements for the same prefix with a different path.

Volume

12

Number of IGP messages

Volume
The ORIGIN attribute indicates which protocol generated the BGP message, our mechanism keeps a
counter for each ORIGIN type (e.g. IGP, EGP, INCOMPLETE).

13

Number of EGP
messages

14

Number of
INCOMPLETE messages

15

Number of ORIGIN
changes

16

Announcements to longer
paths

17

Announcements to
shorter paths

Volume
Volume

Counts when a re-announcement changes the ORIGIN attribute previously announced.

This feature tracks whether a new path is longer or shorter than the path previously stored.

Volume
AS-path
AS-path

18

Average AS path length

Average AS path length considering the path announced in all BGP messages during a time window w.

AS-path

19

Maximum AS path length

Maximum AS path length found in received BGP messages during a time window w.

AS-path

20

Average AS path length
(unique)

Some ASes artificially inflate the path length of an announced path by including redundant hops in a
path (e.g., path = (A B B B C)). This strategy is widely used to decrease the chances of a route being
chosen by a peer (e.g. backup path). This metric calculates the average AS path ignoring prepending
and considering the paths announced in all BGP messages during a time window w.

AS-path

21

Maximum AS path length
(unique)

Maximum AS path length, ignoring prepending, found in received BGP messages during a time
window w.

AS-path

22

Average edit distance

When an AS path is announced to a prefix, we measure its difference in comparison with the
previously stored path by calculating the edit distance. This metric, which is also called Levenshtein
distance, is a sequence comparison method that indicates the minimum number of single-character edits
(i.e. insertions and deletions) required in order to turn one sequence into the other. The average edit
distance is calculated over all path changes.

AS-path

23

Maximum edit distance

This feature stores the highest edit distance in a given time window w.

AS-path

24-34

Edit distance with k
value

Counts the number of message updates with a given k(k = 0, . . . , 10) distance with respect to the
previous known route.

AS-path

35-45

Edit distance with k
value (unique)

Similar to the previous feature, but removes duplicate ASes in the path.

AS-path

46

Number of rare ASes

Keep track of how many times each AS appears in all the announced paths. Usually, an AS appears
multiple times in a given time window. We classify an AS as rare if its number of appearances is
below a given percentage threshold of ASes appearances (we set the default at the 95th percentile).

AS-path

47

Maximum number of rare
ASes

The maximum number of ASes that appear in a message during a given time window w.

AS-path

48

Average number of rare
ASes

The average number of ASes that appear in a given time window w.

AS-path

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Network and Service Management. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TNSM.2026.3696319

JOURNAL OF LATEX CLASS FILES, VOL. 10, NO. 8, SEPTEMBER 2023

14

[31] C. Wang, Z. Zhuang, Q. Qi, J. Wang, X. Wang, H. Sun, and J. Liao,
“Drift doesn’t matter: Dynamic decomposition with diffusion reconstruction for unstable multivariate time series anomaly detection,” Advances
in neural information processing systems, vol. 36, pp. 10 758–10 774,
2023.
[32] Y. Feng, W. Zhang, Y. Fu, W. Jiang, J. Zhu, and W. Ren, “Sensitivehue:
Multivariate time series anomaly detection by enhancing the sensitivity
to normal patterns,” in Proceedings of the 30th ACM SIGKDD Conference on knowledge discovery and data mining, 2024, pp. 782–793.
[33] L. Su, Q. Li, J. Quan, and F. Li, “Enhanced recurrent convolutional
encoding with attention-based representation learning for chaotic time
series anomaly detection,” Physica Scripta, vol. 100, no. 11, p. 115215,
2025.
[34] H. Zuo, A. Zhu, Y. Zhu, Y. Liao, S. Li, and Y. Chen, “Unsupervised
diffusion based anomaly detection for time series: H. zuo et al.” Applied
Intelligence, vol. 54, no. 19, pp. 8968–8981, 2024.
[35] C. Pan, L. Su, L. Xiong, J. Yang, and F. Li, “Ct-ddpm: anomaly
detection of multivariate time series with copula and transformer-based
denoising diffusion probabilistic models,” Information Sciences, vol.
717, p. 122279, 2025.
[36] J. Liu, Z. Ma, Z. Wang, C. Zou, J. Ren, Z. Wang, L. Song, B. Hu, Y. Liu,
and V. Leung, “A survey on diffusion models for anomaly detection,”
arXiv preprint arXiv:2501.11430, 2025.
[37] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“Usad: Unsupervised anomaly detection on multivariate time series,”
in Proceedings of the 26th ACM SIGKDD International Conference on
Knowledge Discovery & Data Mining, 2020, pp. 3395–3404.
[38] C. Ding, S. Sun, and J. Zhao, “Mst-gat: A multimodal spatial–temporal
graph attention network for time series anomaly detection,” Information
Fusion, vol. 89, pp. 527–536, 2023.
[39] P. Fonseca, E. S. Mota, R. Bennesby, and A. Passito, “Bgp dataset
generation and feature extraction for anomaly detection,” in 2019 IEEE
Symposium on Computers and Communications (ISCC). IEEE, 2019,
pp. 1–6.
[40] University of Oregon, Route views project, 1997. [Online]. Available:
http://www.routeviews.org/
[41] RIPE NCC, Routing information service (RIS), 1999. [Online].
Available: https://www.ripe.net/analyse/internet-measurements/
[42] S. Das, N. Agarwal, D. Venugopal, F. T. Sheldon, and S. Shiva,
“Taxonomy and survey of interpretable machine learning method,” in
2020 IEEE Symposium Series on Computational Intelligence (SSCI).
IEEE, 2020, pp. 670–677.

Xincheng Shu received the B.S. degree in Electrical Engineering and Automation and the M.S. and
Ph.D. degrees in Control Theory and Engineering
from Zhejiang University of Technology, Hangzhou,
China, in 2017, 2020, and 2025, respectively. He is
currently a Postdoctoral Fellow with the Computation Communication Research Center, Beijing Normal University, Zhuhai, China. His research interests
include graph neural networks, social physics, and
information diffusion.

B IOGRAPHIES

Zhongyuan Ruan received the Ph.D. degree in
physics from the East China Normal University, Shanghai, China, in 2013. He is currently
an associate professor with the Institute of Cyberspace Security, Zhejiang University of Technology, Hangzhou, China. His current research interests
include complex systems and complex networks.

Songtao Peng received the Ph.D. degree in Control
Science and Engineering from the College of Information Engineering, Zhejiang University of Technology, in 2025. He is currently a postdoctoral
researcher at Zhejiang University of Technology. His
research interests include network security, social
media analysis, recommendation security evaluation,
routing network security, and time-series anomaly
detection.

Yiping Chen received his bachelor’s degree from the
College of Mechanical and Electrical Engineering,
China Jiliang University, in 2021, and his master’s
degree from the College of Information Engineering,
Zhejiang University of Technology, in 2024. His
research interests include multivariate time series,
anomaly detection, and algorithm security.

Wu Shuai received his bachelor’s degree from the
School of Automation and Electrical Engineering,
Zhejiang University of Science and Technology, in
2022, and his master’s degree from the College
of Information Engineering, Zhejiang University of
Technology, in 2025. His research interests include
network security, few-shot traffic intrusion detection,
and incremental learning.

Shenhao Fang received his bachelor’s degree from
the College of Information Engineering at Zhejiang
University of Technology in 2024. He is currently
a master’s student at the Polytechnic Institute, Zhejiang University. His research interests include posttraining of large language models.

Qi Xuan (Senior Member, IEEE) received the B.S.
and Ph.D. degrees in control theory and engineering from Zhejiang University, Hangzhou, China, in
2003 and 2008, respectively. He was a Postdoctoral
Researcher with the Department of Information Science and Electronic Engineering, Zhejiang University from 2008 to 2010, and a Research Assistant
with the Department of Electronic Engineering, City
University of Hong Kong, Hong Kong, in 2010
and 2017, respectively. From 2012 to 2014, he
was a Postdoctoral Fellow with the Department of
Computer Science, University of California at Davis, Davis, CA, USA. He
is currently a Professor with the Institute of Cyberspace Security, College
of Information Engineering, Zhejiang University of Technology, Hangzhou,
and also with the PCL Research Center of Networks and Communications,
Peng Cheng Laboratory, Shenzhen, China. He is also with Utron Technology
Company Ltd., Xi’an, China, as a Hangzhou Qianjiang Distinguished Expert.
His current research interests include network science, graph data mining,
cyberspace security, machine learning, and computer vision.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
