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
# [756] Multivariate Time Series Anomaly Detection in IIoT Using Spatial-temporal Dynamic Mask Diffusion Model
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
编号：756
题名：Multivariate Time Series Anomaly Detection in IIoT Using Spatial-temporal Dynamic Mask Diffusion Model
年份：2026
DOI：10.1109/tdsc.2026.3692551
来源：IEEE Transactions on Dependable and Secure Computing
PDF：paper/10.1109_TDSC.2026.3692551.pdf
已有粗分类：时序、日志、KPI 与云原生异常检测
二级关联：IoT、车联网、工业互联网与边缘安全、其他AI安全与跨域异常检测
相关性：中相关，分数 7
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\756.txt
- 原始字符数：72373
- 本次发送字符数：72373
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

1

Multivariate Time Series Anomaly Detection in
IIoT Using Spatial-temporal Dynamic Mask
Diffusion Model
Jing Bai, Senior Member, IEEE, Zhengyang Zhang, Zhuo Zhang, Tong Li, Member, IEEE,
Zhu Xiao, Senior Member, IEEE, Licheng Jiao, Fellow, IEEE

Abstract—In recent years, multivariate time series anomaly
detection has become an important research topic in the field
of anomaly detection. In Industrial Internet of Things (IIoT)
systems, the collected data may be affected by internal failures,
external disturbances, or other adverse factors. In such cases,
appropriate anomaly detection methods are required to ensure
the stable operation of the system. However, existing methods
based on reconstruction, prediction, or hybrid approaches often
suffer performance degradation when anomalies are present
in large amounts of training data, as these anomalies can
negatively impact the training process. To address this challenge,
we propose a dynamic masking strategy in both temporal
and spatial dimensions. We develop a time series imputation
framework based on a diffusion model that integrates Graph
Neural Network (GNN) and Transformer architectures. This
framework, termed Spatial-Temporal Dynamic Mask Diffusion
for Anomaly Detection (STDMD-AD), incorporates a dynamic
masking mechanism: temporally, reconstruction errors are used
to mask data by randomly concealing values with higher errors;
spatially, attention is applied to mask channels that are more
likely to contain anomalies during training. Experiments on
five real-world datasets demonstrate that the proposed method
outperforms existing benchmarks and achieves state-of-the-art
anomaly detection performance.
Index Terms—multivariate time series, anomaly detection, Industrial Internet of Things (IIoT), diffusion models, transformer.

I. I NTRODUCTION

I

NDUSTRIAL Internet of Things (IIoT) [1]–[3] refers to
the integration of internet technologies with the industrial
sector by applying IoT technologies to manufacturing, energy,
transportation, logistics, and other industrial fields to achieve
interconnection of devices, systems, and factories. In the
operation of large-scale systems related to this technology,
the system heavily relies on the analysis of collected logs
and other data. Internal failures or negative external impacts
may occur, leading to anomalies that make it difficult for the
system or program to achieve the expected performance in
practical applications. This situation often arises in network
Manuscript received 2024 XX XX.
Jing Bai, Zhengyang Zhang, Zhuo Zhang and Licheng Jiao are with the Key
Laboratory of Intelligent Perception and Image Understanding of Ministry of
Education, School of Artificial Intelligence, Xidian University, Xi’an 710071,
China (e-mail: baijing@mail.xidian.edu.cn; zzy123@stu.xidian.edu.cn;
zhangzhuo@stu.xidian.edu.cn; lchjiao@mail.xidian.edu.cn).
Tong Li and Zhu Xiao are with the College of Computer Science and Electronics Engineering, Hunan University, Changsha 410082,
China (emails: {litong, zhxiao}@hnu.edu.cn).

Fig. 1. The framework for anomaly detection in IIoT is shown below in the
line graph of detecting anomalies (highlighted in red) from multidimensional
time series data obtained from sensors.

security traffic monitoring [4], cyberattack [5], infrastructure
monitoring [6], and fault diagnosis and system defects in
the industrial field [7]. To address these issues and detect
anomalies in the collected data, anomaly detection technology
has emerged.
Anomaly detection techniques have applications in many
fields and can be used to detect anomalies in data types such
as images, graphs, and time series. The goal of these methods
is to identify samples in the data that deviate significantly
from other observations [8]. Multivariate time series anomaly
detection is used to identify anomalies, abnormal time periods,
or sudden events in multivariate time series data. In IIoT,
the anomaly detection framework is illustrated in Fig. 1. It
primarily involves monitoring data through multiple sensors
and performing anomaly detection on the acquired multidimensional data to determine when anomalies occur. With the
rapid development of industrial intelligence, this method has
been proven effective in enabling the timely detection and collection of problems in data, thereby avoiding excessive losses.
By leveraging advanced algorithms, this approach enhances
a system’s ability to respond to unexpected events, thereby
improving operational efficiency. Furthermore, the integration

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

2

motivating example illustrating these limitations is presented in Fig. 2. Prediction-based methods often struggle
with the intrinsic stochasticity of future observations,
leading to deviations in normal regions or insensitivity
to actual anomalies. Similarly, the Reconstruction panel
demonstrates a generalization trap where the model learns
to reconstruct the anomalous patterns alongside the normal data. Consequently, the reconstruction error remains
low even during anomalies, causing missed detections.
•

Fig. 2. A motivating example comparing failure modes of existing methods
and our approach. Top two panels show prediction/reconstruction methods
failing due to stochasticity or overfitting anomalies. Bottom panel demonstrates our strategy effectively ignoring anomalies, restoring normal patterns,
and creating a detectable error gap.

of anomaly detection in IIoT systems facilitates predictive
maintenance, allowing proactive measures to be taken before
issues escalate into significant failures.
Currently, most research focuses on unsupervised methods, mainly because anomalies usually account for only a
small proportion of the collected data and are difficult to
label in large quantities [7]. Traditional approaches include
clustering-based and density estimation-based methods. However, these methods rely heavily on manually crafted features
and struggle to ensure model robustness when dealing with
increasingly complex data. In recent years, with the rapid
development of deep learning, anomaly detection methods
that integrate deep learning have achieved significant performance improvements and demonstrated strong practical
effectiveness [9]. Those methods can generally be categorized
into three groups: reconstruction-based, prediction-based [10],
and hybrid approaches [11]. Reconstruction-based methods
determine anomalies by evaluating reconstruction errors, while
prediction-based methods rely on deviations between predicted and actual data. Although these methods have achieved
promising results, two major challenges remain in this task.
•

The high-dimensional nature of Industrial Internet of
Things (IIoT) data, accompanied by its intricate internal
dependencies, necessitates the development of models
with superior representational capacity. [12] Typical IIoT
systems employ a multitude of sensors that collectively
generate voluminous, uncertain, and highly correlated
multivariate time-series data. Conventional reconstruction
and prediction-based anomaly detection algorithms often
exhibit limited efficacy in such challenging settings. A

The uneven distribution of anomalies within real-world
IIoT data streams gives rise to the issue of anomaly
concentration, which substantially complicates both data
preprocessing and model training [3]. Owing to the
impracticality of manual annotation for large-scale multivariate time series, anomaly detection models frequently
depend on unsupervised learning paradigms. In such
settings, the inadvertent inclusion of anomalous instances
in the training set—such as contiguous fault sequences
misleadingly treated as normal—can severely disrupt the
learning dynamics, causing the model to assimilate abnormal patterns into its representation of normal behavior.
For instance, reconstruction-based methods are prone to
regenerating anomalous patterns—especially when such
anomalies recur frequently during training. In contrast,
as illustrated in the Imputation + Dynamic Mask panel
of Fig. 2, this method proactively masks the suspected
region. By forcing the model to infer the missing segment
based solely on the surrounding spatial-temporal context,
it recovers the underlying normal pattern, effectively
rejecting the anomalous inputs. This creates a distinct
discrepancy between the predicted series and the true
anomaly, thereby avoiding the generalization trap and
significantly enhancing detection sensitivity.

To directly address the challenges, we propose the SpatioTemporal Diffusion Model for Detection (STDMD). Our design makes explicit, targeted improvements to the diffusion
model framework to mitigate the specific issues of anomaly
reconstruction and model contamination. Mitigating Challenge 1 (Complex Dependencies): Instead of prediction or
reconstruction-based approaches, which struggle with complex
dependencies and often regenerate anomalies, our model is
built upon a time series imputation framework (Conditional
score-based diffusion models, CSDI [13]). This foundation
provides a key advantage: by learning to accurately impute
masked normal values based on their highly correlated spatiotemporal context, the model learns a robust representation
of the system’s healthy dynamics. To further enhance its
capacity to capture intricate dependencies, we integrate a
Masked Graph Network and a Transformer as the feature
extraction backbone. This hybrid design explicitly models
the complex spatial relationships between sensors (via the
Graph Network) and long-range temporal patterns (via the
Transformer), enabling the model to discern subtle deviations
that constitute anomalies, rather than reconstructing them.
Mitigating Challenge 2 (Anomaly Concentration): To prevent the model from assimilating anomalies present in the
unsupervised training set, we introduce a novel Dual Dynamic

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

3

Masking Mechanism. The Temporal Dynamic Mask applied
to the input of the diffusion model randomly occludes contiguous segments of the time series. This prevents the model
from over-relying on any specific time period that might be
contaminated by a concentrated anomaly, forcing it to learn
a generalized representation of normality from the unmasked
context. The Spatial Dynamic Mask Attention mechanism
operates on the feature level. It adaptively attenuates the
contribution of sensor channels (features) that exhibit large
reconstruction errors during training. This dynamically reduces
the influence of potentially anomalous channels, preventing
them from polluting the model’s latent representations.
Through this dual strategy, we proactively preprocess potentially anomalous regions in both the temporal and feature
domains, thereby significantly mitigating their adverse effects
on model training and enhancing overall robustness. The core
architecture of our STDMD-AD is built on an existing conditional denoising diffusion model originally designed for time
series imputation, and all our contributions represent targeted
modifications, innovative component designs and systematic
integrations rather than simple adoption of off-the-shelf models, with each design tailored to the unique challenges of
multivariate time series anomaly detection. The contributions
of this paper are as follows:
• We propose a novel anomaly detection framework,
Spatial-temporal Dynamic Mask Diffusion Anomaly Detection (STDMD-AD), which incorporates time series
interpolation and leverages temporal and spatial dynamic
masks. The framework integrates Graph Neural Networks
(GNN), Transformers, and Denoising Diffusion Models
to achieve precise anomaly detection. Anomalies are
identified by selectively masking regions with higher
anomaly likelihood and gradually denoising them to
recover the original signals.
• We introduce a temporal dynamic masking method that
utilizes a Transformer-based encoder for data reconstruction. The input data is preprocessed by masking values
with large reconstruction errors, which are indicative of
potential anomalies, to hide these regions before model
training. This approach alleviates the negative impact of
high anomaly concentrations on the training process.
• We incorporate a dynamic mask attention mechanism
into the spatial layer of the network to mask anomalous
regions during training. This allows the model to focus
on cleaner, more representative data, thereby improving
its learning efficiency and detection performance.
The remainder of this paper is structured as follows: The
related work is presented in the Section II. The section III
provides a detailed introduction to the proposed STDMD-AD
framework and each module, while the section IV includes
experimental results, comparisons, and analysis of ablation
experiments. Finally, Section V summarizes the work.

and deep learning approaches, with a specific focus on studies
modeling correlations between multi-sensor data.
A. Multivariate Time Series Anomaly Detection
Multivariate time series anomaly detection has been a
significant focus for researchers and the academic community.
In the realm of deep learning, methods in this field can be
primarily categorized into three types [7]: (1) Prediction-based
methods, which utilize models for forecasting time series
data, such as Long Short-Term Memory (LSTM) [14] and
Gated Recurrent Units (GRU) [15], to predict future values
and compare them with actual values to detect anomalies.
(2) Reconstruction-based methods, which employ generative
models like Generative Adversarial Networks (GANs) [16]–
[19] and Variational Autoencoders (VAEs) [20], [21] to train
and reconstruct data, creating pseudo-samples that are then
compared to real samples to identify anomalies. (3) Hybrid
methods, which typically combine the above two approaches,
using a fusion of results from various methods to obtain the
final outcome.
In recent literature, prediction and reconstruction-based
methods have become popular for their effectiveness in
anomaly detection, with many typical works focusing on
modeling multi-sensor correlations to enhance detection performance. For example, OmniAnomaly [22] combines GRU
and VAE to form a stochastic recurrent neural network model,
learning the normal patterns of multivariate time series and
using reconstruction probability for anomaly detection. GDN
[23] constructs graph structures based on multi-sensor physical connections and proposes a cross-network meta-learning
algorithm to aggregate inter-sensor information for few-shot
anomaly detection. MTAD-GAT [24] leverages Graph Attention Networks to learn adaptive spatial correlations between
sensors and capture temporal trends, enhancing detection performance through a joint prediction and reconstruction model.
TranAD [25] incorporates an attention-based sequence encoder
into the Transformer model to implicitly capture multi-sensor
feature correlations via embedding fusion, combining adversarial training to improve model accuracy. In addition, other
graph-based methods [26]–[29] have also been utilized by
researchers for modeling inter-sensor dependencies in anomaly
detection and have achieved promising results. However, these
methods either rely on prior physical knowledge for static
graph construction, ignore the dynamic coupling of spatial
and temporal dependencies between sensors, or suffer from
interference of anomalous sensor segments when learning
valid correlations.
The method proposed in this paper differs from the above
categories. It primarily utilizes time series interpolation and
applies dynamic masking in both temporal and spatial
dimensions to model multi-sensor spatiotemporal correlations
adaptively, which mitigates the interference of anomalous data
on dependency learning and thus enhance anomaly detection
performance.

II. R ELATED W ORK
In this section, we briefly introduce the methods of multivariate time series anomaly detection based on prediction,
reconstruction and diffusion models, including both traditional

B. Diffusion model
In recent years, the emergence of denoising diffusion models [30] has brought about significant changes in the field

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

4

of image generation. Their powerful generative capabilities
have made them perform excellently in downstream tasks
such as text generation, audio generation, and image anomaly
detection. In the field of image generation, Wolleb et al.
[31] proposed a weakly supervised anomaly detection method
based on the denoising diffusion implicit model, which is used
to generate abnormal maps of regions affected by disease in
patients. Wyatt et al. incorporated multi-scale (multi-octave)
simplex noise into the diffusion model, replacing the original
Gaussian noise, ultimately introducing AnoDDPM [32] for the
detection of anomalies in medical images.
In the field of time series data generation, Kong et al.
[33] introduced a universal diffusion probabilistic model called
DiffWave for original audio synthesis, which can generate
high-quality audio signals for conditional and unconditional
waveform generation tasks. Currently, there are several denoising diffusion model-based methods in time series research that
also explore multi-sensor correlation modeling for imputation
and anomaly detection. For example, Alcaraz et al. [34] combined the diffusion model with structured state space models,
proposing a new time series imputation method for multidimensional sensor data. Xiao et al. [35] extracted normal
observations using a density ratio-based selection strategy
and then used a conditional weighted incremental diffusion
model to estimate missing values of multi-sensor time series.
Chen et al. [36] designed a raster mask strategy to create
missing values in the data and used ImTransformer with a
spatial Transformer layer to capture inter-sensor correlations,
training the diffusion model for time series imputation and
subsequent anomaly detection tasks. Zeng et al. [37] proposed a wireless anomaly detection algorithm AE-DDPMs
for wireless communication security, based on an improved
denoising diffusion probabilistic model to model correlations
among wireless sensor data. These methods have achieved
high performance on public datasets but adopt fixed modeling
or masking strategies for multi-sensor dependencies, lacking
dynamic adaptation to anomalous data segments.
To the best of our knowledge, while our method is not
the first to use diffusion models for multivariate time series
anomaly detection, our approach to data masking is more
comprehensive. We perform dynamic masking operations
in both temporal and spatial dimensions to adaptively
focus on clean and representative multi-sensor spatiotemporal
correlations, which makes the modeling of inter-sensor dependencies more robust to anomalous data compared with existing
diffusion-based methods.
III. M ETHODOLOGY
In this section, we first briefly discuss the issues of multivariate time series anomaly detection. Then, we provide a
detailed explanation of the space-temporal dynamic masking
mechanism. After that, we elaborate the Space-temporal dynamic mask Diffusion for Anomaly Detection (SDMD-AD)
framework and its process.
A. Problem Overview
Given a multivariate time series dataset S = s1 , s2 , ..., sN ,
where each si is a D-dimensional vector representing the val-

Fig. 3. Line chart of an example of multivariate time series anomaly detection
task. The multidimensional time series is represented by blue and green lines,
and all anomalies are represented by red shaded areas.

ues of D features. Our goal is to detect outliers in the dataset,
i.e., samples that are far from the majority of observations
in the feature space. These outliers may represent underlying
issues or anomalous events.
To solve this problem, we can use an anomaly detection
model M that maps each sample si to an anomaly score adi ,
indicating the level of anomaly of sample si . Typically, we
expect higher adi to indicate a higher likelihood of sample si
being an outlier. As shown in the Fig. 3, our ultimate goal is
to identify which points or segments in the data are considered
anomalies, thus completing the anomaly detection task.
In our paper, We frame anomaly detection as a selfsupervised imputation task, where a binary mask matrix M ∈
{0, 1}T ×D is applied to the original series S to generate the
masked input Smasked = S ⊙ M. The model is then trained
to reconstruct the masked values from the observed context.
Unlike standard random masking, our mask M is dynamically
constructed by integrating two strategies detailed in Section
III-B: the Temporal Dynamic Mask, which conceals time
steps with high reconstruction errors, and the Spatial Dynamic
Mask, which targets channels exhibiting anomalous patterns.
This targeted masking strategy forces the model to recover
likely anomalies rather than random missing values, thereby
learning more robust representations of normal dynamics.
B. Spatial-temporal dynamic mask
Due to the presence of unlabeled outliers or segments in the
training dataset, in order to minimize their negative impact on
model training, this paper proposes two mask strategies from
both temporal and spatial dimensions: temporal dynamic mask
and Spatial dynamic mask.
1) Temporal dynamic mask: In terms of the time dimension
masking strategy, we first utilize a Transformer encoder to
reconstruct the original data and compute the reconstruction
error with the Mean Squared Error (MSE) loss between the reconstructed and original data. A threshold is then derived from
the reconstruction error, and points with values exceeding this
threshold are considered more likely to be anomalous. Finally,
a masking ratio is set to randomly conceal data with larger
reconstruction errors. This strategy serves as a preprocessing
step for the input data in the temporal dimension.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

5

Specifically, during the training phase, the raw data are fed
into the encoder network, which outputs a pseudo-sample of
the same dimensionality. To robustly identify potential anomalies without relying on fixed error thresholds, we employ a
confidence-based ranking mechanism. First, we compute the
element-wise reconstruction error (MSE) and transform it into
a confidence score S, formulated as:
S=

1
1 + LM SE (x, x̂)

(1)

where a higher reconstruction error corresponds to a lower
confidence score. Subsequently, we sort these scores and
derive a dynamic threshold based on the α-quantile. Points
falling into the bottom 5% of confidence scores are flagged as
potential anomalies and selected as candidates for masking.
Multivariate anomalies in IIoT systems typically manifest
as persistent shifts in system states rather than instantaneous,
isolated outliers. To capture this temporal continuity, we
extend the masking mechanism to adjacent time points that
exhibit similar spatial patterns. Let xt ∈ RD denote the feature
vector of a candidate anomaly at time t, where D represents
the number of sensor channels. To delineate the effective range
of this dependency, we introduce a temporal search radius
w. Consequently, the identification of potential neighbors is
constrained to the window [t−w, t+w] centered at the anomaly
candidate. For each neighboring time step t′ within this local
window, we quantify the structural similarity between the
candidate xt and the neighbor xt′ using the Pearson correlation
coefficient. A high correlation implies that the system state at
t′ mirrors the anomalous profile at t, thereby necessitating its
inclusion in the mask. The Pearson correlation coefficient [38]
is calculated across the feature dimension as follows:
PD
′
′
d=1 (xt,d − x̄t )(xt ,d − x̄t )
qP
rt,t′ = qP
d = 1D (xt,d − x̄t )2
d = 1D (xt′ ,d − x̄t′ )2
(2)
where xt,d represents the value of the d-th channel at time
PD
1
t, and x̄t = D
d=1 xt,d denotes the spatial average across
all channels at that specific timestamp. This metric robustly
evaluates the similarity of the multivariate distribution shapes
between the two time steps, ensuring that the masked region
covers the entire duration of the anomalous event.
Finally, simply masking all points identified by the error
and correlation criteria might lead to excessive information
loss, making model convergence difficult. To balance this,
we introduce a stochastic sampling strategy controlled by
a masking ratio parameter γ. From the expanded candidate
set obtained in the previous steps, we randomly select γ
proportion of points to generate the final binary mask. This
stochasticity acts as a regularization technique, preventing the
model from overfitting to specific masking patterns.
The T-Encoder network used for reconstruction consists
of one encoder layer from our Spatial-Temporal Transformer
and a simple decoder layer. Although the dynamic masking
strategy may occasionally conceal non-anomalous values, it
effectively reduces the negative impact of anomalous data on
model training and enhances the model’s robustness and generalization, thereby improving anomaly detection performance.

2) Spatial dynamic mask: For the spatial dimension masking strategy, we develop a dynamic mask attention mechanism
applied to the channels. Since certain channels may contain a
higher proportion or density of anomalous data, this attention
mechanism is integrated into the diffusion model. The procedure is as follows: first, each channel is treated as a node in a
graph; second, the attention feature of each node is computed;
and finally, the overall mean and standard deviation of these
features are calculated. Channels with feature values lower the
sum of the mean and one standard deviation are then masked.
Given the input feature map X ∈ RC×D , where C is
the number of channels and D is the feature dimension.
Unlike standard global attention which computes a C × C
dependency map, we focus the query solely on the target
channel to evaluate its relationship with all other channels. We
first generate the query vector for the target channel (qtarget ),
and the key (K) and value (V) matrices for all channels
through linear projections:
qtarget = xtarget WQ ,

K = XWK ,

V = XWV

(3)

where WQ , WK , WV are learnable weight matrices. We then
compute the raw attention scores vector z ∈ RC by performing
the dot product between the target query and all keys:
z=

qtarget KT
√
dk

(4)

where dk is the scaling factor. Each element zi in z represents
the relevance of the i-th channel to the target channel.
To mask channels that contain anomalies or provide irrelevant information, we introduce a dynamic thresholding
strategy. We calculate a threshold θ based on the statistical
distribution of the attention scores z:
v
u
C
C
u1 X
X
1
θ = mean(z) + std(z) =
zi + t
(zi − z̄)2 (5)
C i=1
C i=1
Channels with scores below this threshold are deemed uninformative. Consequently, we define a set of valid channel
indices Set to serve as the effective receptive field for the
target channel:
Set = {i | zi ≥ θ,

i ∈ 1, . . . , C}

(6)

We then calculate the normalized attention weights ai only
for the channels within the valid set using the Softmax
function:
exp(zi )
ai = P
, ∀i ∈ Set.
(7)
j∈Set exp(zj )
Finally, we reconstruct the feature of the target channel
′
by
P aggregating the values from the valid set: vtarget =
i∈Set ai vi . To integrate this reconstructed feature back into
the multivariate time series without altering the non-target
channels, we employ a channel-wise concatenation operation
followed by a linear projection WO :
Y = WO · Concat(v′ target, Vothers)

(8)

where Vothers denotes the projected features of the non-target
channels, and Concat(·) splices the reconstructed target feature

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

6

with the original features of the remaining channels. This
design ensures that the model selectively repairs the anomaly
using only high-confidence spatial contexts.
C. STDMD-AD
1) Overview: The overall architecture of STDMD-AD, as
shown in Fig. 4. It can be seen that our framework is mainly
divided into three parts: training of the diffusion model based
on the spatial-temporal transformer, offline validation of the
model and the main framework of the spatial-temporal transformer, including the structure of its two main feature extraction layers: the spatial layer and the temporal layer. Moreover,
Table I presents a comparison of hyperparameters between
STDMD-AD and the baseline models. It can be observed
that both STDMD-AD and the baselines utilize the Spatialtemporal Transformer and share the same settings for several
hyperparameters such as the number of feature extraction
layers, batch size, time embedding dimension, feature embedding dimension, diffusion steps, and window size. However,
a notable difference lies in the adoption of dynamic masks:
STDMD-AD incorporates both temporal dynamic mask and
spatial dynamic mask, while the baseline models do not
employ these dynamic mask mechanisms.
TABLE I
C OMPARISON OF C OMPONENTS AND H YPERPARAMETERS BETWEEN
STDMD-AD AND BASELINES
Model

STDMD-AD

Baselines

Spatial-temporal Transformer

✓

✓

Temporal dynamic mask

✓

x

Spatial dynamic mask

✓

x

Hyper parameters

Feature extraction layers

4

4

Batch size

32

32

Time embedding dim

128

128

Feature embedding dim

16

16

Diffusion steps

50

50

Window size

100

100

2) Denoising Diffusion Model: The Denoising Diffusion
Implicit Models (DDIMs) is a more efficient iterative implicit
probabilistic model, building upon the Denoising Diffusion
Probabilistic Models (DDPMs) while maintaining the same
training process. DDIMs enables the generation of high-quality
samples with fewer iteration steps, significantly speeding up
the sampling process. The sample generation procedure in
DDIMs primarily involves two key stages: the forward diffusion process and the reverse diffusion process.
Forward noise addition process is consistent with that in
DDPMs, continuously adding Gaussian noise to data, which
can be represented as:

 p
(9)
q (st | st−1 ) := N st ; 1 − βt st−1 , βt I
T

where {βt }t=1 is the variance of the Gaussian noise. Subsequently, according
to the definition in the paper: at := 1 − βt
Qt
and āt := s=1 as , the formula for st can be obtained as:

st =

√

ᾱt s0 +

√

1 − ᾱt ϵ,

with ϵ ∼ N (0, I).

(10)

Then, based on equation (10), the forward noise addition
formula can be derived as follows:
√
st+1 = st + ᾱt+1
+

√
ᾱt+1

r

1
−
ᾱt

s

!

1

st
ᾱt+1
s
(11)
!
r
1
1
−1−
− 1 ϵθ (st , t) .
ᾱt+1
ᾱt

Reverse diffusion processes differs from DDPMs, where the
reverse process is still a Markov chain that depends on the
Bayesian formula. The time step must be the same as the
forward process to generate samples step by step. However, in
DDIMs, the sampling process does not depend on the Bayesian
formula. The defined generation process is:



 N f (1) (s1 ) , σ12 I
if t = 1;
θ


(t)
qσ st−1 | st , fθ (st )
otherwise.

(t)
pθ (st−1 | st ) =


(12)

Based on the derivation in the DDIMs paper, the formula
for st can be obtained as:
√


st − 1 − ᾱt ϵθ (t) (st )
√
ᾱt−1
ᾱt
q
(t)
+ 1 − ᾱt−1 − σt2 ϵθ (xt ) + σt ϵt

st−1 =

√

(13)

where ϵt
∼ N (0, I) is standard Gaussian noise,
σ
ϵ
represents
random
noise, and when σt
=
pt t
p
(1 − āt−1 )/(1 − āt ) 1 − āt /āt−1 for all t, the forward
process becomes a Markov process and the reverse process
becomes the process of DDPMs; when σt = 0, the reverse
process becomes the deterministic sampling process in
DDIMs.
For the optimization objective of this time series imputation task, we also use the MSE loss for training, following the loss calculation approach from the CSDI. During
training, the observed values sco
0 are used as conditional
inputs, while sta
represents
the
imputation target, i.e., the
0
masked √
missing values.
The
known
 noise ground truth is ϵ,
√
co
and ϵθ
+
is the noise predicted by
ᾱt sta
1
−
ᾱ
ϵ,
t
|
s
t
0
0
the model. The MSE loss is then computed between these
predicted and true values to train the model:
L := ϵ − ϵθ

√

ᾱt sta
0 +

√

1 − ᾱt ϵ, t | sco
0

 2
2

, with ϵ ∼ N (0, I).

(14)

3) Spatial-temporal Transformer Backbone: To effectively model the complex dependencies in multivariate time
series, we employ a Spatial-Temporal Transformer as the
denoising backbone, replacing the standard U-Net architecture
typically used in diffusion models. As illustrated in Fig. 4(a),
the framework processes data through a sequential pipeline of
embedding injection, spatio-temporal feature extraction, and
signal reconstruction.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

7

Fig. 4. The overall framework diagram of the spatial-temporal dynamic mask diffusion for anomaly detection. It showcases three parts: the training and
testing process, and the general structure of the network model.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

8

The network first accepts the masked noisy input projected
into a high-dimensional space. To preserve context during the
iterative denoising process, we fuse the input with auxiliary
embeddings. Specifically, we introduce a Diffusion Embedding
to indicate the current noise level and a joint spatio-temporal
embedding that encodes temporal positions and channel identifiers.
These embeddings are then processed by the core extraction
unit, which consists of stacked Temporal Layers and Spatial
Layers. The Temporal Layers utilize self-attention mechanisms
to capture long-range dependencies along the time axis. Subsequently, the Spatial Layers model inter-variable correlations at
each time step. Notably, our proposed Spatial Dynamic Mask
Attention is integrated within these spatial layers to explicitly
suppress anomalous channels.
To facilitate gradient propagation and feature integration,
we employ a global residual connection that fuses the input
features with the processed representations. Finally, a 1 × 1
convolutional projection layer maps the hidden features back
to the original data dimensions, yielding the predicted noise
or reconstructed signal.
4) Training and Testing Process of STDMD-AD: The
training process of our method is illustrated in the top block of
Fig.4. First, data preprocessing is performed using the Temporal Dynamic Mask. The input is fed into a Transformer encoder
for reconstruction, and masking positions are determined based
on the MSE loss between the reconstructed and original data,
along with correlations between adjacent points. Noise is then
added to the unmasked data, and combined with the masked
data to form the model input. Gaussian noise is applied to
train the spatial-temporal Transformer, which gradually learns
to denoise and predict the masked values. Finally, the loss is
computed between the predicted and true values to optimize
the model in inferring the masked normal data.

ployed for the training and testing phases. While the dynamic
mask is crucial for learning robust features during training, we
adopt an equal interval mask for the testing phase, as shown
in the right panel of Fig. 5. This approach avoids the computational overhead associated with the dynamic mechanism,
significantly reducing inference complexity.
The testing process of the framework is shown in the
middle block of Fig. 4. Specifically, the data is first processed
with equal interval mask, generating two inputs with identical
masking intervals. These inputs are then independently fed into
the model for time series interpolation, allowing it to capture
the spatial and temporal correlations in the data and accurately
reconstruct the masked values. The two outputs are subsequently concatenated to form the complete prediction, thereby
improving reconstruction quality. Finally, an anomaly score is
computed based on the difference between the reconstructed
output and the ground truth. By applying the computed threshold to these scores, the framework determines whether each
data point is anomalous, thereby enabling effective detection
of abnormal events.
IV. E XPERIMENTS AND R ESULTS
A. Datasets
We collect five real-world datasets to test our method. The
following is a description of the five experimental datasets [3]:
Mars Science Laboratory (MSL) and Soil Moisture Active
Passive (SMAP) [39]: The Mars Science Laboratory and Soil
Moisture Active Passive satellites are public datasets provided
by NASA. The Mars Science Laboratory dataset consists of
55 dimensions, while the Soil Moisture Active Passive satellite
dataset consists of 25 dimensions. These datasets include
telemetry anomaly data reported by the spacecraft detection
system, known as incident unexpected anomalies (ISA).
Server Machine Dataset (SMD) [22]: The SMD dataset was
collected at a large Internet company over a five-week period.
It consists of 38-dimensional multivariate time series data.
Pool Server Metrics (PSM) [5]: PSM is collected from
multiple application server nodes within eBay. It contains data
from 26 dimensions.
Safe Water Treatment (SWaT) [6]: The SWaT dataset includes data from 51 sensors that are continuously operating
in critical infrastructure systems, particularly water treatment
facilities.

B. Experimental setup

Fig. 5. Explanation of Masking Strategy in Training and Testing Phases:
The left side shows the result processed with temporal dynamic mask in the
training phase, while the right side shows the result processed with equal
interval mask in the testing phase. The T-Encoder consists of one encoder
layer from our Spatial-Temporal Transformer and a simple decoder layer.

As illustrated in Fig. 5, distinct masking strategies are em-

The STDMD-AD framework is implemented based on PyTorch version 3.8 and is trained and tested on an NVIDIA
Titan Xp device. The batch size is set to 32, with each data
sample having a length of 100. A random masking ratio
of 0.7 is applied, and the diffusion model’s time step is
set to 50. During training, a random search method is used
to find the optimal combination of hyperparameters, while
other comparison models follow the settings specified in their
respective original papers.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

9

C. Evaluation Metrics
Anomaly detection is a critical task in various domains,
requiring robust methods to identify outliers or abnormal patterns within datasets. Evaluating the performance of anomaly
detection models involves specific metrics tailored to assess
their effectiveness in identifying anomalies. The primary evaluation metrics used in anomaly detection include Precision,
Recall, and F1-Score.
Precision measures the proportion of true anomalies correctly identified by the model out of all the instances it
classified as anomalies. It is defined as:
True Positives
(15)
Precision =
True Positives + False Positives
A high precision indicates that the model has a low false
positive rate, meaning it does not incorrectly label normal data
as anomalous frequently.
Recall, also known as Sensitivity or True Positive Rate,
measures the proportion of actual anomalies that are correctly
identified by the model. It is defined as:
Recall =

True Positives
True Positives + False Negatives

(16)

A high recall indicates that the model successfully identifies
most of the actual anomalies present in the dataset, minimizing
the false negatives.
F1-Score is the harmonic mean of Precision and Recall,
providing a single metric that balances both aspects. It is
particularly useful when dealing with imbalanced datasets
where the number of normal instances far outweighs the
anomalies. The F1-Score is defined as:
Precision × Recall
F1-Score = 2 ×
(17)
Precision + Recall
The F1-Score ranges from 0 to 1, where a higher value
indicates a better balance between precision and recall.
D. Ablation experiment
In this section, we conduct an ablation study to systematically investigate the impact of various components and
hyperparameters on the performance of our proposed model.
By isolating and modifying specific aspects of the model, we
aim to understand their contributions and effectiveness in the
context of anomaly detection in time series data.
1) Model components: The results of the ablation studies
in Table II indicate that our STDMD-AD model consistently
performs well across all five datasets. Specifically, the temporal and spatial dynamic masking strategies are critical for
enhancing model performance. The removal of the temporal
dynamic mask resulted in a significant decrease in F1 scores
across all datasets. In the MSL, SMAP, PSM, SMD, and
SWaT datasets, the performance dropped by 5.20, 4.52, 5.45,
5.12, and 7.97 percentage points, respectively. The findings
demonstrate the key role of the temporal dynamic mask in
improving the accuracy of time series anomaly detection.
Similarly, removing the spatial dynamic mask also led to
substantial performance degradation, particularly in the MSL,
SMAP, and PSM datasets, with decreases of 6.44, 4.53, and

Fig. 6. The model’s performance parameters P, R, and F1 as the mask
probability changes on the dataset.

4.14 percentage points, respectively. These results validate
the importance of spatial masking in capturing multivariate
dependencies and processing anomalous features across channels. Overall, the ablation results confirm the rationality and
effectiveness of our model design and provide a solid basis
for further optimization.
Moreover, in terms of efficiency, the dynamic masking
strategy only increases the training time per epoch by approximately 14.2% to 22.7% compared to static masking,
primarily due to the iterative reconstruction process and
adaptive threshold computation. However, even with dynamic
masking, the maximum total training time across all datasets
remains within 120 minutes. Furthermore, during the inference
phase, we employ fixed-interval masking (static masking) for
data preprocessing to ensure stable and consistent anomaly
detection results. Consequently, the dynamic masking strategy
has negligible impact on inference efficiency.
2) Masking probability: In our experiments, we conduct
an ablation study to evaluate the impact of varying mask
probabilities on the performance of our STDMD-AD model.
Mask probability refers to the fraction of data points that are
randomly masked during training. We test mask probabilities
ranging from 0.1 to 0.9 and analyzed the results in terms of
precision, recall, and F1-score across PSM datasets. It can be
seen from the Fig. 6 that as the mask probability increases, the
performance of the model continues to improve until the mask
probability reaches 0.7, at which point the performance begins
to decline. This is because increasing the mask probability
obscures more anomalous information in the data, and a higher
mask probability may cause the model to lose more important
information during training, thereby affecting its ability to
recognize true positives.
3) Diffusion steps: The sensitivity experiment and the
results in Fig. 7 reveal significant differences in the model
performance of various indicators as the diffusion step size
increases from 10 to 80. Initially, from 10 to 50 steps, the
model showed a significant improvement in F1 and Recall.
However, as the diffusion steps further increased, the performance gains became less noticeable, and there might even be

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

10

E. Comparative experiment

Fig. 7. The model’s performance parameters P, R, and F1 as the diffusion
steps changes on the dataset.

Fig. 8. The model’s performance parameters P, R, and F1 as the window
sizes changes on the dataset.

a slight decline after 50 steps. Specifically, the model showed
an average precision increase of about 18% between 10 and 50
steps. Beyond 50 steps, while the model maintained a stable
performance level, the rate of precision improvement slowed
down, indicating potential overfitting or convergence to a local
optimum through excessive iteration. Therefore, to balance
model stability and efficiency, the optimal number of diffusion
steps is 50, ensuring performance in anomaly detection while
maximizing computational efficiency and resource utilization
in practical applications.
4) Window size: The size of the window is also an important parameter that affects the performance of the model. For
the PSM dataset, we conduct experiments on STDMD-AD
using different window sizes (mainly 25, 50, 75, and 100).
As shown in Fig. 8, it can be seen that as the window size
increases, the anomaly detection performance of the model
gradually improves. The experiment shows that window size
has a significant impact on the final result and cannot be
ignored. A window that is too small will reduce the amount
of information in each sample, thereby affecting the model’s
learning of features.

We conduct a comparative evaluation of our STDMD-AD
model against various existing models on five common publicly available anomaly detection datasets: MSL, SMAP, PSM,
SMD, and SWaT. The performance metrics evaluated include
Precision (P), Recall (R), and F1-Score (F1). Furthermore, we
compare the STDMD-AD model with seven state-of-the-art
methods based on prediction, reconstruction, and diffusion
models, using evaluation metrics including Precision (P),
Recall (R), and F1-Score (F1): (1) Isolation Forest (IForest)
detects anomalies by isolating anomalous data points from
the rest. (2) LSTM-VAE leverages Long Short-Term Memory
networks and Variational Autoencoders to reconstruct data and
detect sequence anomalies through reconstruction error analysis. (3) TranAD employs Transformer architectures to capture
broader temporal trends in the data for anomaly prediction.
(4) MTAD-GAT utilizes Graph Attention Networks to model
multivariate time series (MTS) and combines prediction-based
and reconstruction-based approaches to enhance representation
learning. (5) GDN proposes a Graph Neural Network-based
method to aggregate information among sensors for anomaly
detection. (6) ImDiffusion designs a raster mask strategy to
create missing values in the data and leverages diffusion
models for prediction and anomaly detection. (7) DDMT
integrates denoising diffusion models with Transformers for
multivariate time series anomaly detection.
The selected baselines fully cover the three mainstream
methodological paradigms in anomaly detection: predictionbased (TranAD, MTAD-GAT), reconstruction-based (LSTMVAE, GDN) and diffusion-based (ImDiffusion, DDMT), enabling a systematic evaluation of our STDMD-AD model
against the core research directions of the field. This setup not
only highlights the superior performance of our method over
traditional prediction and reconstruction-based approaches
with inherent limitations elaborated in Sections 1 and 2,
but also demonstrates its notable improvements over stateof-the-art emerging diffusion-based techniques. In terms of
representativeness, the first five methods (IForest, LSTM-VAE,
TranAD, MTAD-GAT, GDN) are well-recognized benchmark
models widely adopted in top international conferences and
prestigious journals, while the two diffusion-based models
(ImDiffusion, DDMT) represent the latest research advances
published in ICML and ICLR during 2022–2023, ensuring
the representativeness and cutting-edge nature of the comparative experiments. In addition, the selected baselines span
the entire performance spectrum of anomaly detection methods, ranging from classical statistical approaches (IForest) to
modern deep learning architectures covering prediction-based,
reconstruction-based and diffusion-based types, which offers
readers a clear overview of the developmental progression of
the anomaly detection field and an intuitive understanding
of the relative performance positioning of our STDMD-AD
model.
As shown in the results of Table III, for the MSL dataset, our
model STDMD-AD achieves the highest F1 score of 94.72. In
contrast, the best performing model after SDMD-AD is DDMT
(F1: 94.26). For the SMAP dataset, the F1 score is 97.00,

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

11

TABLE II
T HE ABLATION EXPERIMENT RESULTS OF BASELINE AND OTHER MODULES ON FIVE COMMON PUBLICLY AVAILABLE ANOMALY DETECTION DATASETS ,
INCLUDING MSL, SMAP, SMD, PSM, AND SWAT.
MSL
Model

SMAP

PSM

SMD

SWaT

P

R

F1

P

R

F1

P

R

F1

P

R

F1

P

R

F1

STDMD-AD

91.32

98.37

94.72

99.44

94.68

97.00

99.06

98.28

98.67

88.93

80.91

84.73

95.37

93.03

94.19

Temporal mask

90.05

87.32

89.52

94.10

89.45

92.48

97.41

89.37

93.22

86.42

73.79

79.61

92.80

80.51

86.22

Spatial mask

87.13

89.46

88.28

97.95

87.57

92.47

98.64

90.75

94.53

83.30

81.72

82.50

97.84

80.63

88.41

TABLE III
C OMPARATIVE EXPERIMENTAL RESULTS OF STDMD-AD AND OTHER MODELS ON FIVE COMMON PUBLICLY AVAILABLE ANOMALY DETECTION
DATASETS , INCLUDING MSL, SMAP, SMD, PSM, AND SWAT.
MSL

SMAP

PSM

SMD

SWaT

Model

P

R

F1

P

R

F1

P

R

F1

P

R

F1

P

R

F1

STDMD-AD

91.32

98.37

94.72

99.44

94.68

97.00

99.06

98.28

98.67

88.93

80.91

84.73

95.37

93.03

94.19

IForest [40]

50.44

55.03

52.65

54.15

58.95

55.26

49.22

56.98

52.51

41.32

77.56

52.60

45.04

79.59

57.52

LSTM-VAE [41]

77.40

93.23

84.58

81.57

45.18

58.15

97.03

39.30

55.94

75.22

85.45

80.01

40.58

83.10

54.53

TranAD [25]

89.52

99.99

93.73

86.21

56.96

68.60

96.70

73.22

83.34

85.18

80.45

82.75

90.72

79.06

84.48

MTAD-GAT [24]

85.93

93.12

89.38

47.49

99.99

64.39

90.67

88.38

89.51

75.76

84.40

79.85

82.62

80.11

81.35

ImDiffusion [36]

92.76

89.65

91.17

97.95

87.57

92.47

93.48

98.71

96.02

83.30

81.72

82.50

99.99

65.73

79.32

DDMT [42]

91.03

97.73

94.26

93.43

99.11

96.19

95.42

97.50

96.45

88.07

81.50

84.66

90.03

82.51

86.11

GDN [43]

85.84

93.12

89.33

81.04

99.99

89.52

97.59

39.09

55.82

70.85

99.78

82.85

99.99

64.25

78.24

TABLE IV
C OMPARISON OF THE AVERAGE VALUES OF EVALUATION INDEXES OF
STDMD - AD AND OTHER MODELS ON FIVE DATA SETS .
Average
Model

P

R

F1

STDMD-AD

94.82

93.05

93.86

IForest

48.03

65.62

54.10

LSTM-VAE

74.36

69.25

66.64

TranAD

89.66

77.93

82.58

MTAD-GAT

76.49

89.20

80.89

ImDiffusion

93.49

84.67

88.29

DDMT

91.59

91.67

91.53

GDN

87.06

79.24

79.15

making it the best performing dataset. The closest competitor
is DDMT (F1: 96.19). For the PSM dataset, our model
achieves an F1 score of 98.67, the highest among all models.
The second best performing model is DDMT (F1: 96.45). For
the SMD dataset, STDMD-AD achieves an F1 score of 84.73,
making it one of the best performing datasets. For the SWaT
dataset, our model increases the F1 score to 94.19, making
it one of the best performing models. DDMT performs the
best with an F1 score of 86.11. The observed performance
variation across datasets can be attributed to differences in
their inherent characteristics. Generally, achieving significant
performance improvements becomes more challenging as the
dimensionality of the data increases. For instance, PSM,

SMAP, and MSL have relatively lower dimensionalities (25-26
dimensions), while SMD contains 38 dimensions and SWaT
has 51 dimensions. This explains why all models, including
both our approach and the baseline methods, demonstrate
relatively poorer performance on the SMD dataset compared to
others. However, the superior performance of STDMD-AD on
SWaT, despite its high dimensionality, may be attributed to the
concentrated nature of anomalies in SWaT, as opposed to the
more sparse and scattered anomaly distribution in SMD. These
factors collectively contribute to the performance differences
observed across the five datasets.
In Table IV, the evaluation results demonstrate the excellent
performance of our STDMD-AD model across various metrics. Specifically, the STDMD-AD model achieves an average
precision of 94.82, an average recall of 93.05, and an average
F1 score of 93.86 across all five datasets. Compared to other
models, STDMD-AD shows significantly better performance
in multivariate time series anomaly detection. IForest performs
poorly across all metrics, particularly in F1 score, reflecting its
limitations in handling complex time series data. The LSTMVAE model, while showing decent precision, has low recall,
leading to a lower F1 score and limiting its effectiveness
in anomaly detection. TranAD and MTAD-GAT outperform
IForest and LSTM-VAE on some datasets but still fall short of
STDMD-AD. TranAD, though close in precision, lags behind
in recall and F1 score, while MTAD-GAT achieves better recall
but remains weaker in precision and F1 score. The ImDiffusion
model demonstrates good precision and recall, but its overall
F1 score is still below that of STDMD-AD. DDMT and GDN
perform relatively well but do not reach the comprehensive

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

12

capability of STDMD-AD.
In summary, our proposed STDMD-AD model, especially
with the spatial-temporal masking mechanism, consistently
achieves the best or near-best performance across all five
datasets. This mechanism enhances robustness by mitigating
the impact of anomalous data during training, thereby improving anomaly detection and increasing precision, recall, and F1
score. These results highlight the robustness and generalization
capability of our approach in real-world multivariate time series anomaly detection tasks. In particular, the proposed graph
attention-inspired spatiotemporal Transformer and dynamic
spatial-temporal masking strategy enable precise and adaptive
modeling of complex spatiotemporal dependencies between
multiple sensors, which is the key to the superior performance
of STDMD-AD on high-dimensional multi-sensor time series
anomaly detection, and provides a new perspective for multisensor dependency modeling in related fields.
V. CONCLUSION
In this paper, we develope the Spatial-Temporal Dynamic
Mask Diffusion for Anomaly Detection (STDMD-AD) framework, designed to enhance anomaly detection in multidimensional time series data. Our method integrates a SpatialTemporal Transformer with a dynamic masking strategy, effectively mitigating the impact of anomalous data during
training and significantly improving the model’s robustness
and generalization capabilities.
Comprehensive experiments conduct on five real-world
datasets—SMD, PSM, MSL, SMAP, and SWaT—demonstrate
that our model outperforms existing state-of-the-art methods.
Specifically, the proposed STDMD-AD achieves an average
precision of 94.82, a recall of 93.05, and an F1-score of 93.86
across all datasets, highlighting its effectiveness in accurately
detecting anomalies in complex time series data. The success
of our approach is largely attributed to the dynamic masking
mechanism, which reduces the prevalence of anomalous data
during training, thereby enhancing the model’s ability to learn
normal patterns and effectively detect deviations. Furthermore,
the integration of spatial and temporal features through the
Spatial-Temporal Transformer allows our model to capture
intricate relationships within the data, further boosting its
performance.
Despite these improvements, the iterative nature of diffusion
sampling and the complexity of the Transformer architecture pose challenges for real-time deployment on resourceconstrained IIoT edge devices. Consequently, future work will
focus on three strategic directions to bridge this gap. First,
we will investigate model compression techniques, including
knowledge distillation and network quantization, and explore
Latent Diffusion Models (LDMs) to reduce computational
complexity while preserving representation capability. Second,
to facilitate scalable and secure deployment in distributed
industrial networks, we aim to extend STDMD-AD to a
Federated Learning (FL) paradigm. Drawing inspiration from
efficient aggregation protocols like LSFL [44], we plan to incorporate lightweight secure aggregation to ensure robustness
against bandwidth constraints and Byzantine attacks. Finally,

we will develop adaptive mechanisms that allow the model to
dynamically adjust masking ratios and diffusion steps based
on real-time noise levels and device resource availability.
R EFERENCES
[1] S. Villamil, C. Hernández, and G. Tarazona, “An overview of internet
of things,” Telkomnika (Telecommunication Computing Electronics and
Control), vol. 18, no. 5, pp. 2320–2327, 2020.
[2] M. Soori, B. Arezoo, and R. Dastres, “Internet of things for smart
factories in industry 4.0, a review,” Internet of Things and CyberPhysical Systems, vol. 3, pp. 192–204, 2023.
[3] A. A. Cook, G. Mısırlı, and Z. Fan, “Anomaly detection for iot timeseries data: A survey,” IEEE Internet of Things Journal, vol. 7, no. 7,
pp. 6481–6494, 2019.
[4] M. Abbasi, A. Shahraki, and A. Taherkordi, “Deep learning for network
traffic monitoring and analysis (ntma): A survey,” Computer Communications, vol. 170, pp. 19–41, 2021.
[5] A. Abdulaal, Z. Liu, and T. Lancewicki, “Practical approach to asynchronous multivariate time series anomaly detection and localization,”
in Proceedings of the 27th ACM SIGKDD conference on knowledge
discovery & data mining, 2021, pp. 2485–2494.
[6] A. P. Mathur and N. O. Tippenhauer, “Swat: A water treatment testbed
for research and training on ics security,” in 2016 international workshop
on cyber-physical systems for smart water networks (CySWater). IEEE,
2016, pp. 31–36.
[7] A. Blázquez-Garcı́a, A. Conde, U. Mori, and J. A. Lozano, “A review on
outlier/anomaly detection in time series data,” ACM computing surveys
(CSUR), vol. 54, no. 3, pp. 1–33, 2021.
[8] G. Pang, C. Shen, L. Cao, and A. V. D. Hengel, “Deep learning for
anomaly detection: A review,” ACM computing surveys (CSUR), vol. 54,
no. 2, pp. 1–38, 2021.
[9] K. Shaukat, T. M. Alam, S. Luo, S. Shabbir, I. A. Hameed, J. Li,
S. K. Abbas, and U. Javed, “A review of time-series anomaly detection
techniques: A step to future perspectives,” in Advances in Information
and Communication: Proceedings of the 2021 Future of Information
and Communication Conference (FICC), Volume 1. Springer, 2021,
pp. 865–877.
[10] R. Xu, Y. Cheng, Z. Liu, Y. Xie, and Y. Yang, “Improved long short-term
memory based anomaly detection with concept drift adaptive method for
supporting iot services,” Future Generation Computer Systems, vol. 112,
pp. 228–242, 2020.
[11] K. Choi, J. Yi, C. Park, and S. Yoon, “Deep learning for anomaly
detection in time-series data: Review, analysis, and guidelines,” IEEE
access, vol. 9, pp. 120 043–120 065, 2021.
[12] H. Xu, W. Chen, N. Zhao, Z. Li, J. Bu, Z. Li, Y. Liu, Y. Zhao, D. Pei,
Y. Feng et al., “Unsupervised anomaly detection via variational autoencoder for seasonal kpis in web applications,” in Proceedings of the
2018 world wide web conference, 2018, pp. 187–196.
[13] Y. Tashiro, J. Song, Y. Song, and S. Ermon, “Csdi: Conditional scorebased diffusion models for probabilistic time series imputation,” Advances in Neural Information Processing Systems, vol. 34, pp. 24 804–
24 816, 2021.
[14] A. Graves and A. Graves, “Long short-term memory,” Supervised
sequence labelling with recurrent neural networks, pp. 37–45, 2012.
[15] J. Chung, C. Gulcehre, K. Cho, and Y. Bengio, “Empirical evaluation of
gated recurrent neural networks on sequence modeling,” arXiv preprint
arXiv:1412.3555, 2014.
[16] Y. Sun, W. Yu, Y. Chen, and A. Kadam, “Time series anomaly detection
based on gan,” in 2019 sixth international conference on social networks
analysis, management and security (SNAMS). IEEE, 2019, pp. 375–
382.
[17] Y. Li, X. Peng, J. Zhang, Z. Li, and M. Wen, “Dct-gan: dilated
convolutional transformer-based gan for time series anomaly detection,”
IEEE Transactions on Knowledge and Data Engineering, vol. 35, no. 4,
pp. 3632–3644, 2021.
[18] A. Geiger, D. Liu, S. Alnegheimish, A. Cuesta-Infante, and K. Veeramachaneni, “Tadgan: Time series anomaly detection using generative
adversarial networks,” in 2020 ieee international conference on big data
(big data). IEEE, 2020, pp. 33–43.
[19] L. Li, J. Yan, H. Wang, and Y. Jin, “Anomaly detection of time series
with smoothness-inducing sequential variational auto-encoder,” IEEE
transactions on neural networks and learning systems, vol. 32, no. 3,
pp. 1177–1191, 2020.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Dependable and Secure Computing. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TDSC.2026.3692551

13

[20] S. Lin, R. Clark, R. Birke, S. Schönborn, N. Trigoni, and S. Roberts,
“Anomaly detection for time series using vae-lstm hybrid model,” in
ICASSP 2020-2020 IEEE International Conference on Acoustics, Speech
and Signal Processing (ICASSP). Ieee, 2020, pp. 4322–4326.
[21] Z. Niu, K. Yu, and X. Wu, “Lstm-based vae-gan for time-series anomaly
detection,” Sensors, vol. 20, no. 13, p. 3738, 2020.
[22] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proceedings of the 25th ACM SIGKDD international
conference on knowledge discovery & data mining, 2019, pp. 2828–
2837.
[23] K. Ding, Q. Zhou, H. Tong, and H. Liu, “Few-shot network anomaly
detection via cross-network meta-learning,” in Proceedings of the Web
Conference 2021, 2021, pp. 2448–2456.
[24] H. Zhao, Y. Wang, J. Duan, C. Huang, D. Cao, Y. Tong, B. Xu, J. Bai,
J. Tong, and Q. Zhang, “Multivariate time-series anomaly detection via
graph attention network,” in 2020 IEEE international conference on data
mining (ICDM). IEEE, 2020, pp. 841–850.
[25] S. Tuli, G. Casale, and N. R. Jennings, “Tranad: Deep transformer
networks for anomaly detection in multivariate time series data,” arXiv
preprint arXiv:2201.07284, 2022.
[26] S. He, G. Li, K. Xie, and P. K. Sharma, “Fusion graph structure learningbased multivariate time series anomaly detection with structured prior
knowledge,” IEEE Transactions on Information Forensics and Security,
vol. 19, pp. 8760–8772, 2024.
[27] H. Liu, W. Luo, L. Han, P. Gao, W. Yang, and G. Han, “Anomaly
detection via graph attention networks-augmented mask autoregressive
flow for multivariate time series,” IEEE Internet of Things Journal, 2024.
[28] X. Ma, J. Wu, S. Xue, J. Yang, C. Zhou, Q. Z. Sheng, H. Xiong, and
L. Akoglu, “A comprehensive survey on graph anomaly detection with
deep learning,” IEEE Transactions on Knowledge and Data Engineering,
vol. 35, no. 12, pp. 12 012–12 038, 2021.
[29] G. Duan, H. Lv, H. Wang, G. Feng, and X. Li, “Practical cyber attack
detection with continuous temporal graph in dynamic network system,”
IEEE Transactions on Information Forensics and Security, 2024.
[30] J. Ho, A. Jain, and P. Abbeel, “Denoising diffusion probabilistic models,”
Advances in neural information processing systems, vol. 33, pp. 6840–
6851, 2020.
[31] J. Wolleb, F. Bieder, R. Sandkühler, and P. C. Cattin, “Diffusion models
for medical anomaly detection,” in International Conference on Medical
image computing and computer-assisted intervention. Springer, 2022,
pp. 35–45.
[32] J. Wyatt, A. Leach, S. M. Schmon, and C. G. Willcocks, “Anoddpm:
Anomaly detection with denoising diffusion probabilistic models using
simplex noise,” in Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2022, pp. 650–656.
[33] Z. Kong, W. Ping, J. Huang, K. Zhao, and B. Catanzaro, “Diffwave: A versatile diffusion model for audio synthesis,” arXiv preprint
arXiv:2009.09761, 2020.
[34] J. M. L. Alcaraz and N. Strodthoff, “Diffusion-based time series imputation and forecasting with structured state space models,” arXiv preprint
arXiv:2208.09399, 2022.
[35] C. Xiao, Z. Gou, W. Tai, K. Zhang, and F. Zhou, “Imputation-based timeseries anomaly detection with conditional weight-incremental diffusion
models,” in Proceedings of the 29th ACM SIGKDD Conference on
Knowledge Discovery and Data Mining, 2023, pp. 2742–2751.
[36] Y. Chen, C. Zhang, M. Ma, Y. Liu, R. Ding, B. Li, S. He, S. Rajmohan,
Q. Lin, and D. Zhang, “Imdiffusion: Imputed diffusion models for multivariate time series anomaly detection,” arXiv preprint arXiv:2307.00754,
2023.
[37] J. Zeng, X. Liu, and Z. Li, “Radio anomaly detection based on improved denoising diffusion probabilistic models,” IEEE Communications
Letters, 2023.
[38] I. Cohen, Y. Huang, J. Chen, J. Benesty, J. Benesty, J. Chen, Y. Huang,
and I. Cohen, “Pearson correlation coefficient,” Noise reduction in
speech processing, pp. 1–4, 2009.
[39] K. Hundman, V. Constantinou, C. Laporte, I. Colwell, and T. Soderstrom, “Detecting spacecraft anomalies using lstms and nonparametric
dynamic thresholding,” in Proceedings of the 24th ACM SIGKDD
international conference on knowledge discovery & data mining, 2018,
pp. 387–395.
[40] F. T. Liu, K. M. Ting, and Z. H. Zhou, “Isolation-based anomaly
detection,” Acm Transactions on Knowledge Discovery from Data, vol. 6,
no. 1, pp. 1–39, 2012.
[41] S. Lin, R. Clark, R. Birke, S. Schonborn, and S. Roberts, “Anomaly
detection for time series using vae-lstm hybrid model,” IEEE, 2020.

[42] C. Yang, T. Wang, and X. Yan, “Ddmt: Denoising diffusion mask
transformer models for multivariate time series anomaly detection,”
arXiv preprint arXiv:2310.08800, 2023.
[43] A. Deng and B. Hooi, “Graph neural network-based anomaly detection
in multivariate time series,” in Proceedings of the AAAI conference on
artificial intelligence, vol. 35, no. 5, 2021, pp. 4027–4035.
[44] Z. Zhang, L. Wu, C. Ma, J. Li, J. Wang, Q. Wang, and S. Yu, “Lsfl: A
lightweight and secure federated learning scheme for edge computing,”
IEEE Transactions on Information Forensics and Security, vol. 18, pp.
365–379, 2022.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
