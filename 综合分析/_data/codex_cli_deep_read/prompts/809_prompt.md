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
# [809] SpectraBayes: Exploring Traffic Series Reconstruction in Frequency Domain for Anomaly Detection
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
编号：809
题名：SpectraBayes: Exploring Traffic Series Reconstruction in Frequency Domain for Anomaly Detection
年份：2026
DOI：10.1109/tits.2026.3667876
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2026.3667876.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 11
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\809.txt
- 原始字符数：62249
- 本次发送字符数：62249
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

1

SpectraBayes: Exploring Traffic Series
Reconstruction in Frequency Domain for
Anomaly Detection
Ruoheng Li , Diyin Tang , Member, IEEE, Fei Wang , Xi Zhu , and Xianbin Cao , Senior Member, IEEE

Abstract—Timely detection of anomalies in traffic systems
is crucial for mitigating risks and economic losses. Current
time series anomaly detection methods often use reconstruction errors to identify anomalies, and their accuracy depends
on how well they can reconstruct normal patterns from the
original series. However, traffic data typically exhibit high
noise, spatiotemporal heterogeneity, and uncertain inter-series
correlations, complicating the learning of normal patterns. To
address these challenges, we introduce SpectraBayes, which
explores the reconstruction of density and volume series in the
frequency domain for anomaly detection. First, we transform
the series into the frequency domain and apply a low-pass filter
to remove noise. Then, we embed periodic information into the
frequency-domain representation through phase shifts to enhance
the temporal awareness. Additionally, we model the inter-series
correlations between density and volume resiliently using crossspectrum probabilistic modeling. Optimized by maximizing the
Evidence Lower Bound (ELBO), SpectraBayes ensures robust
reconstruction while avoiding overfitting against the uncertain
data. SpectraBayes outperforms 21 existing anomaly detection
models on traffic series anomaly detection tasks, achieving mean
improvements of 2.71% across three metrics over the secondbest model. Furthermore, it is lightweight and maintains robust
performance under varying noise levels.

Fig. 1. Spatial-temporal heterogeneity of traffic volume, which is revealed by
varied distribution and autocorrelation coefficient across different dates and
locations. Data are selected from [1].

Index Terms—Traffic anomaly detection, Bayesian neural network, frequency-domain representation.

I. I NTRODUCTION

T

RAFFIC anomalies, such as congestion or accidents,
disrupt transportation systems and incur significant

Received 8 April 2025; revised 14 November 2025 and 25 January
2026; accepted 22 February 2026. This work was supported in part by
Beijing Natural Science Foundation under Grant 4254101 and in part by the
National Natural Science Foundation of China under Grant 62373029 and
Grant 62372430. The Associate Editor for this article was M. Mesbah.
(Corresponding author: Xi Zhu.)
Ruoheng Li, Xi Zhu, and Xianbin Cao are with the School of Electronic
and Information Engineering, Beihang University, Beijing 100191, China,
also with the MIIT Key Laboratory of Aerospace Mobile Communications,
Beijing 100191, China, and also with the National Engineering Laboratory for Comprehensive Transportation Big Data Application Technology,
Beijing 100191, China (e-mail: ruohengli@buaa.edu.cn; zhuxi@buaa.edu.cn;
xbcao@buaa.edu.cn).
Diyin Tang is with the School of Automation Science and Electrical Engineering, Beihang University, Beijing 100191, China (e-mail:
tangdiyin@buaa.edu.cn).
Fei Wang is with the State Key Laboratory of AI Safety, Institute of
Computing Technology, Chinese Academy of Sciences, Beijing 100190,
China, and also with the University of Chinese Academy of Sciences, Beijing
100049, China (e-mail: wangfei@ict.ac.cn).
Digital Object Identifier 10.1109/TITS.2026.3667876

economic losses. Timely detection of such anomalies is crucial
for traffic management and mitigation [1], [2].
Macroscopic traffic data, such as volume and density,
are readily obtained from widely deployed loop detectors,
providing a convenient resource for anomaly detection. Existing traffic time series anomaly detection methods can be
broadly categorized as supervised or unsupervised. Supervised
approaches rely on labeled data, limiting their generalization [3]. Early unsupervised methods assume normal patterns
are in low-rank and detect anomalies as samples with
large deviations [4], [5], [6]. However, these models often
requires large time windows for offline analysis. Recently,
deep learning–based reconstruction methods enhance temporal
modeling and anomaly identification by using the advanced
architecture [7], [8].
However, traffic time series pose three main challenges
for modeling normal patterns and detecting anomalies. First,
they are highly noisy due to random individual behaviors
and detector inaccuracies, which can impair model robustness
and discrimination. Second, traffic exhibits pronounced spatiotemporal heterogeneity, as shown in Figure 1. Volume distributions and autocorrelation vary across locations and dates,

1558-0016 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
2

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

II. R ELATED W ORK
In this section, we review the current state of research on
traffic time series anomaly detection, as well as the general
time series representation models for anomaly detection.
A. Traffic Time Series Anomaly Detection Methods

Fig. 2. Radar plots illustrate the normalized traffic volume and density
across various dates at a specific location, revealing a variable correlation
between these variables. Under normal conditions, the correlation between
traffic volume and density varies within a range. A rapid negative correlation,
marked by a red background, indicates potential anomalies. Data and labels
are sourced from [1].

complicating the consistent definition of anomaly features.
Third, although traffic flow and density are strongly correlated
in ideal normal patterns [9], their relationship fluctuates under
normal conditions and deviates during anomalies (Figure 2),
highlighting the need for probabilistic modeling of inter-series
correlations.
To address above challenging, we introduce SpectraBayes,
a frequency-domain reconstruction model that utilizes the
periodicity and cross-spectrum information for robust traffic
series anomaly detection. Specifically, SpectraBayes employs
the real Fast Fourier Transform (rFFT) for domain transformation and integrates a low-pass filter for data denoising.
Then, SpectraBayes enhances the temporal awareness of
model by embedding daily periodicity into the frequency
domain. Meanwhile, the model explicitly quantifies correlations between traffic volume and density, leveraging the
Bayesian neural parameters to adaptively learn the desirable
correlated strength. The refined frequency representation is
then reconstructed back to the time domain through an inverse
FFT. The model is trained with the Evidence Lower Bound
(ELBO) for probabilistic parameters estimation, which ensures
both reconstruction accuracy and regularization.
The main contributions of this paper are as follows:
1) We propose SpectraBayes, to our knowledge, which is
the first probabilistic frequency-domain reconstructionbased anomaly detection model that specifically
designed for traffic series, which enables efficient temporal modeling and robust pattern reconstruction in an
integrated framework.
2) We introduce a periodicity embedding mechanism that
explicitly models daily cycles through phase-shifts in the
frequency domain, enhancing detection performance by
introducing temporal awareness.
3) We design a probabilistic cross-spectrum learning module that jointly models the spectral relationship between
traffic density and volume, which can handle the
aleatoric uncertainty inherent in traffic data.
4) Extensive evaluations against 21 state-of-the-art baselines confirm that SpectraBayes achieves superior
detection performance (+2.71% over the second-best),
along with significant improvements in computational
efficiency and model robustness.

Traffic time series anomaly detection methods can
be broadly categorized into statistics-based, density-based,
classification-based, and reconstruction-based approaches.
Early statistical methods applied thresholds to macroscopic
[10], [11], [12] and microscopic [13] variables, enabling initial
anomaly identification but offering limited adaptability. Fundamental Diagram-based approaches [14], [15] detect deviations
in flow-occupancy pairs, despite the strong interpretability, their reliance on manual calibration restricts robustness
to dynamic traffic conditions. Incoperating nonparametric
density-based methods, such as kernel density estimation [16]
and FastABOD [1], can help identify abnormal flow-density
pairs, but require retraining for different road segments.
Classification-based methods, including logistic regression
[17], feedforward and recurrent neural networks [18], [19],
and graph convolutional networks [20], learn mappings from
spatiotemporal data to anomaly labels, but are limited by the
availability of labeled data. Reconstruction-based approaches,
encompassing tensor learning [5], [6], self-expressive models
[21], and deep time-series representation models [7], [22],
detect anomalies through deviations from learned normal
patterns, offering finer temporal modeling but with performance varying across different setups [23]. Overall, traffic
anomaly detection remains challenging due to system uncertainty and dynamics, motivating the development of tailored
methods.
B. General Time Series Representation Models for Anomaly
Detection
Time-series representation models can be broadly categorized into Encoder-Decoder and Encoder-only architectures.
Classic Encoder-Decoder frameworks, such as Transformers
[24], GANs [25], and VAEs [26], involve both encoding and
decoding, increasing training complexity, whereas Encoderonly models offer simpler structures for series modeling [22],
[27]. Recent studies suggest that merely increasing model
complexity does not consistently improve anomaly detection
[28], motivating approaches that explicitly capture anomalyspecific features, including inconsistency [29] and association
discrepancies [7].
For traffic data, spatiotemporal heterogeneity, inherent daily
periodicity, and stochastic variations due to road conditions
and human factors complicate the modeling of general patterns. These characteristics should be explicitly considered
when designing time-series representation models for traffic
anomaly detection.
III. M ETHOD
A. Problem Formulation
Let {Xtw }Tt=1 denote the traffic time series within window w, where temporal vector at each time Xtw ∈ R2 is

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LI et al.: SpectraBayes: EXPLORING TRAFFIC SERIES RECONSTRUCTION IN FREQUENCY DOMAIN

3

Fig. 3. Model structure of SpectraBayes. Input series Xtw are normalized and transformed into the frequency domain as X wf using the real Fast Fourier Transform
(rFFT), followed by low-pass filtering for denoising. Periodicity is then encoded through sinusoidal encoding as φw
t , which is embed into frequency domain
w , H w ) and phase differences (∆φw ,∆φw ) are measured, with
as phase shifts. To quantify the correlation between volume and density, amplitude ratios (Hqd
dq
qd
dq
Bayesian parameters (α, β, γ, δ) adaptively adjusting their correlation strength. The resulted frequency representation is then upsampled using a complex-valued
linear layer to obtain the Xtu,w with the required length for the inverse real Fast Fourier Transform (irFFT). The series then undergoes inverse normalization
to recover the original scale. The Evidence Lower Bound (ELBO) optimizes the model, and reconstruction errors serve as anomaly indicators. During testing,
anomaly scores are rated based on the reconstruction error kXtw − X̂tw k22 .

defined as:
Xtw =



Qwt Dwt



,

(1)

where Qwt and Dwt represent traffic volume and density.

w

Our objective is to learn a reconstruction model fζ that
reconstructs the normal traffic pattern from the original series
X̂tw = fζ (Xtw ). The anomaly scores is then determined by the
reconstruction error:
swt = kX̂tw − Xtw k22 .

(2)

An anomalous alert occurs when swt > ξ, where ξ is a
predetermined threshold.
B. Architecture
The SpectraBayes model, illustrated in Figure 3, first transforms each traffic time window {Xtw }Tt=1 ∈ RT ×2 into the
spectral domain using rFFT and denoise it with a low-pass
filter. Daily periodicity is embedded through sinusoidal phase
shifts, and cross-spectral correlations between density and
volume are refined through Bayesian learning. The spectrum
is then inverted back to the time domain using irFFT, with
model parameters optimized by maximizing the ELBO. During
testing, the reconstruction error serves as the anomaly score.
The details explanation for each component is presented in
subsequent sections.
C. Domain Transformation and Denosing
A reversible instance-wise normalization (RIN) [22] is first
applied on the time series Xtw to mitigate the influence of
a prominent zero-frequency component. The rFFT is then
employed to convert the time-domain series Xtw into the
frequency domain, as expressed by:
X wf = rFFT(Xtw ) ∈ CF×2 ,

The complex value of volume and density Qw ( f ) and Dw ( f )
can be expressed in polar form:

(3)

where F = bT /2c + 1 denotes the number of frequency
bins, with T denoting the size of detection window. X wf is
a complex-valued matrix with dimensions F × 2, including
complex-valued elements for volume and density:


X w ( f ) = Qw ( f ) Dw ( f ) .
(4)

Qw ( f ) = Awq ( f )e jφq ( f ) ,

w

Dw ( f ) = Awd ( f )e jφd ( f ) ,

(5)

where Awq ( f ) and Awd ( f ) represent the amplitudes of Qw ( f ) and
Dw ( f ), and φwq ( f ) and φwd ( f ) denote the phases of Qw ( f ) and
w

D ( f ).
To suppress noise in the frequency domain, a low-pass filter
is applied on X w ( f ). Specifically, a cut-off frequency F p is
applied to retain frequency components below this threshold.
The selection of F p governs the denoising strength and can be
determined by the harmonic content of the dominant frequency
[22]. However, given the heterogeneity across datasets, we
treat F p as a hyperparameter, whose impact is explored in
the parameter study.
D. Periodicity Encoding
Traffic series exhibit strong periodicity, and embedding
periodicity into the data can enhance the capabilities of
temporal modeling [30], [31]. In Transformer architectures,
Sinusoidal Positional Encoding is commonly employed to
provide positional awareness for the input. Drawing on the
properties of the Fourier transform [32], a time-domain shift
x(t − τ) corresponds to a phase shift in the frequency domain,
as given by:
Xτ ( f ) = A( f )e j(φ( f )−2π f τ) ,
(6)

where τ denotes the time shift.
Inspired by this principle, we encode periodicity information
as phase shifts to capture temporal features. Specifically, for
a time window w containing T minute-of-day timestamps
tm ∈ [0, 1439] (m = 1, . . . , T ), we generate a base temporal
embedding ewd (t) for each timestamp following Time2Vec [30]:


i
h 
2πtm
m
ewd (t) = sin 2πt
cos
,
(7)
τd
τd
where τd = 1440 minutes denotes the daily period.
Next, the base embeddings for the window are concatenated
and flattened into a vector e0 wd ∈ R2T . The flattened temporal

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
4

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

embedding is then processed through a Multilayer Perceptron
(MLP) and transformed into φwt ∈ RF p to ensure dimension
alignment:
φwt = W2 · σ(W1 e0 wd + b1 ) + b2 ,

(8)

where W1 ∈ RDt ×2T and W2 ∈ RF p ×Dt are weight matrices,
b1 ∈ RDt and b2 ∈ RF p are bias vectors, and σ is the ReLU
activation function.
Finally, φwt is applied to adjust the phases of both density
w
φd and volume φwq components, expressed as:
φ̃wq = φwq + φwt ,

φ̃wd = φwd + φwt ,

where µ and σ2 denote the mean and variance of Gaussian
priors. The Gaussian distribution enables closed-form updates
and facilitates the optimization of the Evidence Lower Bound
(ELBO) during training [37]. While other distributions can
be used as alternatives, they may result in computational
inefficiencies.
Based on the learnable parameters, the phase and amplitude
of the spectra are then refined as:

where φ̃wd and φ̃wq denote the adjusted phase.

Incorporating inter-series information can enhance the
reconstruction of normal patterns and improve anomaly detection performance, particularly in systems where variables
exhibit strong correlations [33]. In the frequency domain, the
relationship between volume (Qw ) and density (Dw ) can be
quantified using cross-spectral information: amplitude ratios
and phase differences. For volume relative to density, the
w
( f ) and phase difference ∆φwqd ( f ) can be
amplitude ratio Hqd
calculated as:
 w 
Q (f)
|Qw ( f )|
w
w
Hqd ( f ) = w
, ∆φqd ( f ) = arg
,
(10)
|D ( f )| + 
Dw ( f )

(14)

β( f )),

(15)

w
w
φc,w
q ( f ) = φ̃q ( f ) + (∆φdq ( f )
w
w
(f)
Ac,w
(Hdq
q ( f ) = Aq ( f )

γ( f )),

(16)

δ( f )),

(17)

w
Ac,w
d ( f ) = Ad ( f )

(9)

E. Probabilistic Cross-Spectrum Learning

α( f )),

w
(f)
(Hqd

w
w
φc,w
d ( f ) = φ̃d ( f ) + (∆φqd ( f )

where denotes element-wise multiplication.
The spectral representation that incorporates the crossspectral information is denoted as:


X c,w ( f ) = Qc,w ( f ) Dc,w ( f ) ,
(18)
where:
c,w

jφq ( f )
Qc,w ( f ) = Ac,w
,
q ( f )e

(19)

jφc,w
d ( f ).
( f ) = Ac,w
d ( f )e

(20)

c,w

D

The refined spectra X c,w
models and utilizes the dynamic
f
correlation between traffic volume and density, allowing for a
more integrated spectral representation.

where  is a small positive constant to prevent division by
zero. Conversely, for density relative to volume:
 w 
|Dw ( f )|
D (f)
w
w
Hdq ( f ) = w
, ∆φdq ( f ) = arg
.
(11)
|Q ( f )| + 
Qw ( f )

F. Series Reconstruction and Uncertainty-Aware Training

The amplitude ratios reflect traffic efficiency, corresponding
to the slope of the Fundamental Diagram under varying
w
traffic states [9]. In ideal normal conditions, Hqd
( f ) and
w
Hdq ( f ) approximate constants that determined by road charw
( f ) indicates free-flow pattern where
acteristics. A high Hqd
w
volume dominates, while a high Hdq
( f ) signals congestion
where density prevails. Phase differences, meanwhile, encode
propagation delays in traffic waves. Positive ∆φwqd ( f ) typically suggests downstream acceleration waves where volume
changes precede density, whereas negative values indicate
upstream shockwaves during congestion or incidents where
density increases precede volume reductions.
Applying these cross-spectral information can be viewed
as adaptive filtering between variables [34]. Parameters
are introduced as learnable scalars to modulate the crosscorrelation strength of cross-spectral learning. Considering the
stochasticity of traffic data [35], [36], we employ Bayesian
parameterization [37] within a variational inference framework
to model cross-correlations strength probabilistically. Considering both of the computational efficiency and stochastic
characteristic of traffic data [35], [36], we assign the priors of
parameters as Gaussian distributions:

where Wc ∈ CF×F p and bc ∈ CF are learnable parameters of
the complex-value linear layer, mapping the frequency bins
from F p back to F. After that, X uf is reconstructed back to
time domain through the irFFT:

α( f ) ∼ N (µα ( f ), σ2α ( f )),

β( f ) ∼ N (µβ ( f ), σ2β ( f )),

(12)

γ( f ) ∼ N (µγ ( f ), σ2γ ( f )),

δ( f ) ∼ N (µδ ( f ), σ2δ ( f )),

(13)

Then, X c,w
are upsampled through a complex-value linear
f
layer:
X uf = Wc X c,w
(21)
f + bc ,

X̂tw = irFFT(X uf ).

(22)

Finally, the reconstructed series X̂tw undergoes an inverse
RIN to reverse the initial normalization.
To train SpectraBayes, we employ variational inference to
approximate the posterior p(θ|X ) of the Bayesian parameters
θ = {α, β, γ, δ} given the observed data X . A Gaussian
approximate posterior q(θ|X ) is used to approximate p(θ|X ),
and the model is optimized by maximizing the Evidence
Lower Bound (ELBO) [38]:
L = Eq(θ|X ) [log p(X |θ)] − KL(q(θ|X )kp(θ)),

(23)

where Eq(θ|X ) [log p(X |θ)] represents the expected loglikelihood of the observed data X with respect to the
variational approximate posterior q(θ|X ), encouraging the
model to reconstruct the observed data. The second term in
loss function KL(q(θ|X )kp(θ)) measures the Kullback-Leibler
(KL) divergence between approximate posterior q(θ|X ) and the
prior p(θ) over all Bayesian parameters, acting as a regularizer.
During training, θ is sampled using the reparameterization
trick for gradient computation.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LI et al.: SpectraBayes: EXPLORING TRAFFIC SERIES RECONSTRUCTION IN FREQUENCY DOMAIN

Assuming a Gaussian likelihood
Q for the observed data,
which can be given by p(X |θ) = ni=1 N (Xi |X̂i (θ), σ2X ) (where
i represents the i-th data point), the expected log-likelihood
becomes:
n
Eq(θ|X ) [log p(X |θ)] = − log(2πσ2X )
2
n
1 X
−
Eq(θ|X ) [(Xi − X̂i (θ))2 ]. (24)
2σ2X i=1
Based on the assumption, σ2X is a constant and can be omitted during optimization, the training objective is equivalent to
minimizing:
Lloss =

n
X

Eq(θ|X ) [(Xi − X̂i (θ))2 ] + KL(q(θ|X )kp(θ)).

(25)

i=1

For Gaussian priors p(θ) ∼ N (µ p , σ2p ) and posteriors
q(θ|X ) ∼ N (µq , σ2q ), the KL divergence can be obtained by:
ˇ


 
ˇ
σp
2 ˇ
KL N (µq , σq )ˇN (µ p , σ2p ) = log
σq
σ2q + (µq − µ p )2 1
− . (26)
+
2σ2p
2
During test, means of the variational posterior q(θ|X ) are
used for inference, representing the most likely parameters.
G. Adaptive Anomaly Measurement
Reconstruction error swt serves as the anomaly score for each
detection window, reflecting deviations from learned traffic
patterns. Anomaly is identified when swt exceeds a threshold
. Considering the spatiotemporal heterogeneity of traffic, we
adopt two adaptive strategies to determine the threshold. First,
a scenario-specific threshold is optimized on each validation
dataset using grid search:
 s = arg max F1(; Dval,s ).


(27)

Second, an adaptive threshold based on rolling statistics is
employed, which adapts online during testing. Specifically, the
threshold is updated within a sliding window of length W in
a causal manner:
r (t) = µ̃t + k · e
σt ,
(28)
where µ̃t and e
σt denote the median and median absolute
deviation (MAD) calculated from the window of size W that
includes data from time (t − W + 1) to time t. If t is less than
W, the window will include all available data up to time t. The
parameter k acts as a scaling factor, controlling the sensitivity
of the threshold. It can be optimized offline on the validation
data to accommodate diverse datasets.
H. Complexity Analysis
We analyze the computational complexity of SpectraBayes
per detection window using big O notation [39], which
provides asymptotic upper bounds while omitting constant factors and less significant contributions. Influencing parameters
including the window size T , cutoff frequency F p , and hidden
dimension Dt for periodicity encoding. The time complexity

5

is dominated by rFFT (O(T log T )), periodicity embedding
(O(Dt ×T )), and frequency-domain reconstruction (O(T ×F p )),
resulting in an overall time complexity of

T (T , F p , Dt ) = O max(T log T , Dt × T , T × F p ) .
(29)
The space complexity is mainly determined by storing
temporal embeddings and frequency-domain representations,
resulting in a space complexity of S (T , F p , Dt ) = O(T × Dt ).
IV. E XPERIMENTS
We conducted various experiments to answer the following
questions about our model: Q1. Accuracy. How accurately
does our method detect anomalies compared to other baseline?
Q2. Effectiveness. How do the modules designed in SpectraBayes work? Q3. Robustness. How does the performance
vary under datasets of different noisy levels and parameter
configurations?
A. Experimental Details
Below present details about our experimental setting,
including dataset configurations, baselines for comparison, and
parameter settings.
1) Dataset Setup: We adopt the traffic time-series anomaly
dataset released by Sarteshnizi et al. [1], which consists of
10 sub-datasets sampled at 15-minute intervals. To obtain
higher temporal resolution, we linearly interpolated the data to
1-minute intervals. Unlike real-world minute-level traffic measurements, which typically exhibit high stochasticity and low
signal-to-noise ratios due to sensor noise and environmental
factors [16], [40], interpolated series tend to be overly smooth.
To better approximate realistic traffic fluctuations, we injected
zero-mean Gaussian noise into the interpolated data.
The mean z-score of anomaly points in the original dataset
is 0.27, indicating that excessive noise may introduce artificial
anomalies and distort ground-truth labels. Accordingly, we set
the noise variance to 0.01 to simulate mild stochasticity while
preserving anomaly integrity. To further assess robustness,
higher noise variances (0.04, 0.09, 0.16, and 0.25) were also
evaluated, with results reported in Section IV-F.
The task is formulated as series-level anomaly detection.
Time series are segmented into sequences using a sliding
window with window size T = 80 and stride 1. Samples are
split into training, validation, and testing sets with a 6:2:2
ratio. The average anomaly ratios across the 10 datasets are
26.36%, 20.12%, and 28.04%, respectively.
2) Baselines: To comprehensively evaluate the performance of SpectraBayes, we compared it with 21 representative anomaly detection methods covering density-based,
distance-based, and reconstruction-based paradigms. Specifically, density-based methods include LOF [41], KDE [42], and
ConFlow [43], which identify anomalies as low-density samples. ConFlow further models temporal dependencies through
graph-augmented normalizing flows. Distance-based methods,
including iForest [44], KNN [45], and Fast-ABOD [46], detect
anomalies based on isolation characteristics or distance and
angular deviations.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
6

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

TABLE I
S ELECTED BASELINES AND THE T UNED H YPERPARAMETERS

CUDA 12.4. Each model was trained for 40 epochs using
the Adam optimizer, with a learning rate of 0.0001 and a
weight decay of 0.0005. Optimal hyperparameters for each
model were determined through a parameter search, with
candidate values detailed in Table I. For Transformer-based
architecture and TimeNet, a fixed dropout rate of 0.1 and
the GELU activation function were applied. All models are
trained and evaluated five times with fixed random seeds, with
mean performance reported. Deterministic methods, such as
LOF, KDE, Fast-ABOD, KNN, and PCA, had identical results
across runs.
4) Evaluation Metrics: Model performance is evaluated
using the Area Under the Receiver Operating Characteristic
Curve (AUC-ROC) and the F1 score (F1). AUC-ROC measures the trade-off between true positive and false positive rates
across varying thresholds, reflecting the overall discriminative
capability. The F1 score evaluates detection performance at a
specific decision threshold.
To account for spatiotemporal heterogeneity, we adopt
both offline scenario-specific thresholding and an online
dynamic thresholding strategy, which is explained in detail in
Section III-G. The offline threshold is optimized for using
grid search on validation data. The online threshold is determined through a rolling statistics method that adapts causally
during testing. For online thresholding, the window size is
fixed to W = 500 for all methods, while the scaling factor
k ∈ {0.5, 1, 1.5, 2, 2.5, 3} is selected based on validation performance.
B. Comparative Study

Reconstruction-based methods include both classical
and deep learning approaches. Classical PCA [47]
identifies anomalies by low-rank reconstruction errors.
Deep learning–based models span recurrent architectures
(AE-LSTM, OmniAnomaly [8]), graph neural networks
(MTAD-GAT [33]), convolutional models (TimesNet [48]),
linear models (Dlinear [49], FreTS [50], FITS [22]), and
Transformer-based methods, including Anomaly Transformer
[7], TranAD [24], DCdetector [29], InverseTransformer
[51], PatchTST [52], FEDformer [53], and Freqformer [54].
These models enhance temporal representation ability of
Transformer architecture through attention mechanisms,
patch-wise modeling, adversarial training, dual-attention
designs, or frequency-domain modeling.
3) Experimental Setting: All experiments were conducted
on a server running Ubuntu 20.04.5 LTS, equipped with
192 GB of RAM, an Intel Xeon Gold 6242R CPU @
3.10 GHz, and an NVIDIA GeForce RTX 4090 GPU. All
models were implemented using PyTorch version 1.7.1 with

We compared SpectraBayes with 21 baseline models
using three evaluation metrics: AUC-ROC (Table II), F1score with a scenario-specific threshold  s (F1- s , Table III),
and F1-score with a rolling-statistic threshold r (F1-r ,
Table IV). Generally, the scenario-specific threshold  s , determined through a fine-grained search on validation datasets,
achieved higher detection accuracy than the rolling-statistic
threshold r . Across all datasets and metrics, SpectraBayes demonstrated superior performance, achieving the best
results on 9 out of 10 datasets in terms of AUC-ROC,
7 out of 10 for F1- s , and 8 out of 10 for F1-r .
Notably, SpectraBayes outperformed the second-best method
by up to 4.65% in AUC-ROC (dataset 8-E), 6.21% in
F1- s (dataset 1-W), and 3.03% in F1-r (dataset 8-E). On
average, SpectraBayes consistently led across all three metrics, surpassing competitors such as InverseTransformer and
PatchTST by ranges from 1.78% to 3.3%.
Classical machine learning methods, including LOF, iForest,
KNN, FastABOD, PCA, and KDE, exhibited limited effectiveness due to their inability to model temporal patterns.
Among these, PCA achieved the highest average AUC-ROC
(61.08%), KNN led in F1- s (46.73%), and PCA led in F1-r
(38.54%). ConFlow, which employs conditional normalizing
flows to integrate temporal information, outperformed traditional methods with an average AUC-ROC of 74.02%, F1- s of
50.37%, and F1-r of 47.04%. However, its performance was
constrained by the noisy nature of traffic data, which diminished the discriminative ability of density-based approaches.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LI et al.: SpectraBayes: EXPLORING TRAFFIC SERIES RECONSTRUCTION IN FREQUENCY DOMAIN

7

TABLE II
C OMPARISON OF AUC-ROC (%) B ETWEEN S PECTRA BAYES AND BASELINE M ODELS

TABLE III
C OMPARISON OF F1-S CORE (%) B ETWEEN S PECTRA BAYES AND BASELINE M ODELS W ITH S CENARIO -S PECIFIC T HRESHOLD  s

Among deep learning models, simpler linear architectures
often outperformed more complex ones. SpectraBayes, Dlinear, FITS, and FreTS are linear-based models that operate
in the time or frequency domain, performing better than
complex architectures specifically designed for multivariate
time series. Dlinear, which decomposes series into high- and
low-frequency components for separate temporal modeling,
achieved the third-highest average AUC-ROC (76.05%). Interseries correlation remains important for improving detection

accuracy. FreTS, with its Frequency Channel Learner for modeling inter-series correlations, outperformed FITS by 2.12%
in AUC-ROC and by 0.97% in F1- s . Complex architectures
designed for multivariate time series, such as MTAD-GAT
(which uses a dual graph attention network for fine-grained
inter- and intra-series correlation modeling), exhibited unsatisfactory performance (AUC-ROC: 61.75%, F1- s : 45.67%,
F1-r : 37.22%). OmniAnomaly performed better than MTADGAT by leveraging stochastic neural networks (AUC-ROC:

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
8

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

TABLE IV
C OMPARISON OF F1-S CORE (%) B ETWEEN S PECTRA BAYES AND BASELINE M ODELS W ITH ROLLING -S TATISTIC T HRESHOLD r

67.37%, F1- s : 46.63%, F1-r : 43.95%). However, it did
not explicitly incorporate inter-series correlations, resulting in
limited performance similar to that of AE-LSTM. The convolutional variant, TimeNet, achieved superior performance
(AUC-ROC: 70.50%, F1- s : 53.54%, F1-r : 53.54%) compared to OmniAnomaly, owing to its use of TimeBlocks for
embedding multi-periodicity.
Transformer-based methods exhibited varied performance.
InverseTransformer, which tokenized entire series for
global correlation modeling, achieved second-best results in
AUC-ROC (76.38%) and F1- s (55.44%). PatchTST,
employing a patching strategy for patch-wise dependencies,
secured the second-best F1-r (51.67%). However, the
frequency-variant Transformer architecture FEDformer
performed poorly due to its embedded random frequency
sampling mechanism, which retained many noisy components
(AUC-ROC: 61.79%, F1- s : 44.98%, F1-r : 38.84%).
Freqformer, a frequency-domain Transformer without such
sampling, performed better (AUC-ROC: 70.97%, F1- s :
52.24%, F1-r : 46.11%). Transformer-based models that
specifically designed for time series anomaly detection tasks
(AnomalyTransformer, DCdetector, and TranAD) exhibited
suboptimal performance on noisy traffic data, as their
discriminative strategies, such as association or representation
discrepancy, were less effective with uncertain data.
These results highlight that complex architectures do
not guarantee superior performance. Instead, decoupled
mechanisms (Dlinear), inter-series correlation modeling
(InverseTransformer, PatchTST), and frequency-domain
representations (FreTS, Freqformer, SpectraBayes) enhance
robustness against noisy traffic data. SpectraBayes, due to
its effective denoising and probabilistic correlation modeling,
consistently achieving the best performance.

Fig. 4. Ablation Results. Baseline (w/o all), with periodicity encoding
modules (w/ T), with cross-spectrum modules (w/ C), full model (w/ all).

C. Ablation Study
We evaluated the effectiveness of the modules designed
in SpectraBayes by testing various combinations of modules,
including temporal embedding (T), and cross-spectrum learning (C) module. The results of ablation study are illustrated
in Figure 4.
The baseline model (w/o all) demonstrated varied performance across datasets, ranging from 69.75% to 77.47%.
When evaluating the individual contributions of each module, the incorporation of Periodicity Encoding (w/ T) and
cross-spectrum learning (w/ C) module consistently improved
performance across all datasets. Specifically, the inclusion of
module C alone led to more significant performance gains
(2.52% on 1-N dataset, 6.03 on % 1-W dataset, 1,93%
on d005es1553 dataset, 2.08% on d090es0035 dataset). In

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LI et al.: SpectraBayes: EXPLORING TRAFFIC SERIES RECONSTRUCTION IN FREQUENCY DOMAIN

9

Fig. 6. Performance comparison between probabilistic and non-probabilistic
learning under various noisy level.

Fig. 5. Visualization of amplitude and phase adjustment for 1-N datasets.
Normal series are sampled to keep the same number with anomalous series.

contrast, Periodicity Encoding module achieves smaller performance gains (1.46% on 1-N dataset, 0.6 % on 1-W dataset,
0.56% on d005es1553 dataset, 0.63% on d090es0035 dataset).
When both modules were integrated (w/ all), the model
achieved the best detection performance across all datasets.
Notably, on Melbourne subset 1-W, the combination of all
modules boosted performance to 84.68%, representing an
improvement of 6.57% over the baseline model.
D. Module Analysis
1) Visualization of Cross-Spectrum Learning: To demonstrate the impact of our cross-spectrum module, we visualized
the amplitude and phase adjustments for density in crossspectrum learning, as shown in Figure 5. These heatmap
showed obvious difference between normal and anomalous
series. For instance, in Figure 5 (a), amplitude adjustments for
the 1-N dataset show that normal samples exhibit uniform and
minimal changes, consistently near 1.0, indicating negligible
modification of the original signal. In contrast, anomalous
samples display adjustments spanning a wider range (from 0
to 3), reflecting significant amplitude discrepancies between
density and volume. Regarding phase adjustments, normal
samples show minimal and uniform shifts, clustering near
zero, as depicted in Figure 5 (b). However, anomalous samples, particularly in the low-frequency range, exhibit larger
phase shifts (−π to π). By leveraging cross-spectrum learning,
SpectraBayes enhances the discriminability of reconstructed
sequences in the feature space, thereby improving detection
performance.
2) Effectiveness of the Bayesian Parameters: To assess
whether incorporating probabilistic modeling can enhance
detection robustness, we compared two model variants across
datasets with varying noise intensities, where Gaussian noise
variance was set to different levels. The first variant (nonprobabilistic) adopted conventional deterministic parameters in
cross-spectrum learning optimized through stochastic gradient

descent, which is a frequentist point estimate. In contrast, the
second (probabilistic) employed a Bayesian formulation that
explicitly modeled aleatoric uncertainty through probabilistic
parameter estimation. As illustrated in Figure 6, the Bayesian
model consistently outperformed its deterministic counterpart
across all noise levels, achieving up to a 3.8% improvement
in AUC-ROC. This consistent gain demonstrates the benefit
of uncertainty-aware modeling, which enables the system to
better capture the stochasticity inherent in traffic data and
maintain better performance under noisy conditions.
E. Computational Efficiency Comparison
Computational efficiency comparison experiments were
conducted on an Ubuntu 20.04.5 LTS server equipped with
an Intel Xeon Gold 6242R CPU (192 GB RAM) and
an NVIDIA RTX 4090 GPU. We evaluated the computational efficiency and deployment feasibility of SpectraBayes
compared to the baselines (TimesNet, AnomalyTransformer,
DCdetector, PatchTST, InverseTransformer, FEDformer, and
FreTS). The metrics evaluated are the number of trainable
parameters, Multiply-Accumulate Operations (MACs), and
average inference time per detection window, which correspond to the space complexity, theoretical computational
complexity, and empirical computational complexity, respectively. The low number of trainable parameters and MACs
suggests minimal memory usage and computational demand
on resource-constrained hardware, while the short inference
time demonstrates the high computational efficiency. All measurements were obtained using the standard PyTorch profiler,
with inference times averaged over five runs. For Transformerbased models (AnomalyTransformer, DCdetector, PatchTST,
InverseTransformer, and FEDformer), the number of layers,
attention heads, and hidden dimensions were set to 2, 4, and
128, respectively. For the convolutional model (TimesNet), the
layer depth, kernel size, and hidden dimension were fixed at
2, 3, and 128. The frequency-domain model (FreTS) used a
hidden dimension of 128. For SpectraBayes, the cut-frequency
Fq and temporal embedding dimension were set to 15 and 128.
The results in Table V show that SpectraBayes achieved
the lowest values across all metrics, demonstrating superior
efficiency. It required only 0.08 M trainable parameters,
approximately 38.5% fewer than the second-lightest model
(DCdetector, 0.13 M). In terms of theoretical computation,

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
10

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

TABLE V
C OMPARISON OF M ODEL PARAMETERS , MAC S , AND I NFERENCE T IME
FOR THE 1-N DATASET W ITH A D ETECTION W INDOW S IZE OF T = 80

SpectraBayes used just 0.13 M MACs, over ten times fewer
than the next-best baseline (InverseTransformer, 1.67 M) and
far below larger models like TimesNet (550.67 M). The
empirical inference time per window for SpectraBayes was
0.002 ms, which was four times faster than the second-fastest
baseline (InverseTransformer, 0.008 ms) and over 500 times
faster than the slowest (FEDformer, 1.081 ms).
F. Robustness Analysis
1) Robustness Comparison Under Different Noise Levels:
To evaluate the model robustness under varying noise conditions, we conducted comparative experiments on datasets
with different levels of injected Gaussian noise. We chose
Dlinear, FreTS, InverseTransformer, and PatchTST for comparison since they achieved competitive performance in the
comparative study under low noise levels. Specifically, the
noise level was parameterized by the variance of the Gaussian
noise, ranging from 0.01 to 0.25 times the variance of the
original data.
Results are shown in Figure 7. Specifically, increasing noise
levels led to performance degradation for all models, highlighting the challenges of increased data uncertainty. SpectraBayes
consistently outperformed the baselines at every noise level,
achieving the highest AUC-ROC scores consistently. With the
increasing of the noisy level, its performance had an absolute
drop of 11.4% and a relative decline of 14.36%. In comparison,
Dlinear showed the largest degradation, with scores dropping
from 76.1% to 60.4% (absolute drop of 15.7%, relative drop of
20.63%). FreTS, PatchTST, and InverseTransformer exhibited
relative drops of 18.41%, 18.10%, and 17.21%, respectively.
The robustness of SpectraBayes can be attributed to its explicit
low-pass denoising and probabilistic modeling mechanisms,
effectively separating the high-frequency noise and handling
the data uncertainty.
2) Model Robustness Under Missing Value: In this experiment, missing values are introduced by randomly masking
individual time points with a predefined missing ratio, simulating the scenarios where sensor readings may be incomplete.
We employ forward and backward fill to address this issue,
ensuring data continuity and allowing models to process
sequences without interruption. Model results are shown in
Table VI. As the missing ratio increases from 0.05 to 0.25,
the AUC-ROC decreases slightly from 79.24% to 78.06%,

Fig. 7. Model performance (AUC-ROC) under varying noise levels (with
Gaussian distribution variances set at different levels).
TABLE VI
M ODEL D ETECTION U NDER VARIOUS DATA M ISSING R ATIOS

indicating the filling strategy is effective in moderate data
missing.

G. Parameter Study
We tested how our model perform under different hyperparameters setting, including the selection of Low-pass
frequency F p , the size of detection window T , and the prior
distribution of Bayesian parameter.
1) Setting of Low-Pass Frequency: The effect of cutoff
frequency F p on the model performance was assessed across
distinct datasets, as shown in Figure 8. In general, the performance of the model reveals a consistent and stable trend
across the range of the F p settings. For the 1-N and 1-W
datasets, AUC-ROC performance showed almost no change
across different low-pass frequencies (variation <0.0002), with
no discernible pattern. For the d090es0035 and d005es15531
datasets, AUC-ROC performance decreased slightly as the
low-pass frequency increased.
2) Detection Window and Stride Size: Figure 9 summarize
the AUC-ROC performance under different combinations of
window size (ws) and stride size (ss). Across all datasets,
window size exhibits a substantially stronger influence on
detection performance than stride size.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LI et al.: SpectraBayes: EXPLORING TRAFFIC SERIES RECONSTRUCTION IN FREQUENCY DOMAIN

11

Fig. 8. Performance under different low-pass frequency on four selected
datasets.
Fig. 10. Performance under different prior distribution setting on four selected
datasets.

Fig. 9. Performance under different window and stride size on four selected
datasets, ws and ss are abbreviation for window size and stride size,
respectively.

For the Melbourne datasets (1)-N and 1-W), AUC-ROC
consistently improves as the window size increases, indicating that longer temporal contexts lead to more stable and
discriminative representations for anomaly detection. This
improvement is closely associated with an increase in the
proportion of stationary sub-series under larger windows,
suggesting that extended temporal aggregation enhances statistical stability in these datasets. In contrast, for the Seattle
datasets (d005es15531 and d090es00353), performance peaks
at moderate window sizes (typically ws = 30–40) and gradually degrades as the window size further increases. This
behavior can be attributed to a decreasing level of stationarity
under larger windows, where excessively long temporal contexts introduce stronger non-stationary variations that hinder
anomaly discrimination.
Meanwhile, variations in stride size lead to only marginal
performance changes when the stride is smaller than the
window size. For a fixed window size, AUC-ROC remains
relatively stable across a wide range of stride values, demonstrating that the proposed method is robust to stride selection.

Overall, these results indicate that appropriate window size
selection is critical for optimal performance.
3) Setting of Prior Distribution: We investigated the impact
of prior distribution settings on model performance, as illustrated in Figure 10. The Gaussian prior setting governs the
strength of the cross-spectrum learning, thereby influencing
the correlation intensity learned between traffic series. A larger
prior mean (µ p = 1) indicates a greater adjustment magnitude
and a larger prior variance (σ p = 1) indicates greater flexibility
in correlation learning. Overall, as depicted in Figure 10,
employing a higher prior mean (µ p = 1) and variance (σ p = 1)
generally leads to improved model performance. Specifically,
prior variance demonstrates a particularly pronounced effect.
Increasing it from 0.1 to 1 typically results in a significant
performance enhancement (e.g., up to 3.8% on 1-N dataset).
Prior mean also influences model performance, but to a
lesser extent than prior variance. This observation suggests
that macroscopic elements within the traffic system exhibit
strong correlations and inherent uncertainty. Consequently,
employing higher prior mean and variance values facilitates
improved model performance.
V. C ONCLUSION AND F UTURE W ORK
This paper introduced SpectraBayes, which is a novel
frequency-domain reconstruction model specially designed for
traffic series anomaly detection. SpectraBayes improved the
detection ability of frequency-domain model through the integration of periodicity embedding and probabilistic correlation
learning. Extensive evaluations against a broad range of baselines demonstrated the superior performance of SpectraBayes
on traffic series anomaly detection.
In response to the recent call by Sarteshnizi [1] for
advancements in deep learning-based anomaly detection for
traffic series anomaly detection, our comparative experiments
involved a diverse array of deep learning models. Our findings
indicated that architectural complexity alone is insufficient
to ensure superior detection performance. Complex models

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
12

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

trained on noisy time series tend to overfit noise, diminishing
the discrimination between normal and anomalous series.
Instead, our results corroborate the importance of decoupled
mechanisms, frequency representation, and correlation modeling as critical components for achieving effective traffic
anomaly detection.
However, SpectraBayes remains a data-driven approach that
lacks a certain level of physical interpretability, which holds
significant potential for advancement. Combining the Fundamental Diagram with the Physics-Informed Neural Networks
(PINNs) represents a potential solution. Explicitly integrating the domain-specific physical principles with machine
learning techniques can enhance model interpretability in
detecting anomalies. Moreover, the development of more
comprehensive, system-wide datasets with detailed annotations
is essential to support empirical studies, thereby fostering improvements in traffic system safety, efficiency, and
resilience.
R EFERENCES
[1]

I. Taheri Sarteshnizi, S. A. Bagloee, M. Sarvi, and N. Nassir,
“Traffic anomaly detection: Exploiting temporal positioning of flowdensity samples,” IEEE Trans. Intell. Transp. Syst., vol. 25, no. 5,
pp. 4166–4180, May 2024.
[2] S. Mu, Z. Gu, H. Lyu, Y. Gao, and S. Xu, “Stereo-based 3D anomaly
object detection for autonomous driving: A new dataset and baseline,”
2025, arXiv:2507.09214.
[3] M. A. Abdel-Aty and R. Pemmanaboina, “Calibrating a real-time
traffic crash-prediction model using archived weather and ITS traffic
data,” IEEE Trans. Intell. Transp. Syst., vol. 7, no. 2, pp. 167–174,
Jun. 2006.
[4] S. Yang, K. Kalpakis, and A. Biem, “Detecting road traffic events by
coupling multiple timeseries with a nonparametric Bayesian method,”
IEEE Trans. Intell. Transp. Syst., vol. 15, no. 5, pp. 1936–1946,
Oct. 2014.
[5] X. Wang and L. Sun, “Diagnosing spatiotemporal traffic anomalies
with low-rank tensor autoregression,” IEEE Trans. Intell. Transp. Syst.,
vol. 22, no. 12, pp. 7904–7913, Dec. 2021.
[6] Y. Hu and D. B. Work, “Robust tensor recovery with fiber outliers for
traffic events,” ACM Trans. Knowl. Discovery from Data, vol. 15, no. 1,
pp. 1–27, Feb. 2021.
[7] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time
series anomaly detection with association discrepancy,” in Proc. Int.
Conf. Learn. Represent., 2021, pp. 1–27.
[8] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discovery
Data Mining, Jul. 2019, pp. 2828–2837.
[9] M. Treiber and A. Kesting, Traffic Flow Dynamics. Cham, Switzerland:
Springer, 2013.
[10] A. Ceder, “Relationships between road accidents and hourly traffic
flow—II: Probabilistic approach,” Accident Anal. Prevention, vol. 14,
no. 1, pp. 35–44, Feb. 1982.
[11] J.-L. Martin, “Relationship between crash rate and hourly traffic flow
on interurban motorways,” Accident Anal. Prevention, vol. 34, no. 5,
pp. 619–629, Sep. 2002.
[12] P. Ferrari, “The reliability of the motorway transport system,” Transp.
Res. B, Methodol., vol. 22, no. 4, pp. 291–310, Aug. 1988.
[13] J. A. Barria and S. Thajchayapong, “Detection and classification of
traffic anomalies using microscopic traffic variables,” IEEE Trans. Intell.
Transp. Syst., vol. 12, no. 3, pp. 695–704, Sep. 2011.
[14] B. Persaud, F. L. Hall, and L. M. Hall, “Congestion identification
aspects of the mcmaster incident detection algorithm,” Transp. Res. Rec.,
no. 1287, pp. 167–175, 1990.
[15] F. L. Hall, Y. Shi, and G. Atala, “On-line testing of the mcmaster
incident detection algorithm under recurrent congestion,” Transp. Res.
Rec., no. 1394, pp. 1–7, 1993.
[16] K. Kalair and C. Connaughton, “Anomaly detection and classification
in traffic flow data from fluctuations in the flow–density relationship,”
Transp. Res. C, Emerg. Technol., vol. 127, Jun. 2021, Art. no. 103178.

[17] Z. Yuan, X. Zhou, and T. Yang, “Hetero-ConvLSTM: A deep learning
approach to traffic accident prediction on heterogeneous spatio-temporal
data,” in Proc. 24th ACM SIGKDD Int. Conf. Knowl. Discovery Data
Mining, Jul. 2018, pp. 984–992.
[18] S. Thajchayapong, E. S. Garcia-Trevino, and J. A. Barria, “Distributed
classification of traffic anomalies using microscopic traffic variables,”
IEEE Trans. Intell. Transp. Syst., vol. 14, no. 1, pp. 448–458, Mar. 2013.
[19] S. Zhao, D. Zhao, R. Liu, Z. Xia, B. Chen, and J. Chen,
“GMAT-DU: Traffic anomaly prediction with fine spatiotemporal granularity in sparse data,” IEEE Trans. Intell. Transp. Syst., vol. 24, no. 11,
pp. 13503–13517, Nov. 2023.
[20] J. Wang, J. Wu, Z. Wang, F. Gao, and Z. Xiong, “Understanding
urban dynamics via context-aware tensor factorization with neighboring regularization,” IEEE Trans. Knowl. Data Eng., vol. 32, no. 11,
pp. 2269–2283, Nov. 2020.
[21] M. Nouri, E. Konyar, M. Reisi Gahrooeri, and M. Ilbeigi, “Detecting
traffic anomalies during extreme events via a temporal selfexpressive model,” IEEE Trans. Intell. Transp. Syst., vol. 25, no. 10,
pp. 13613–13626, Oct. 2024.
[22] Z. Xu, A. Zeng, and Q. Xu, “FITS: Modeling time series with 10k
parameters,” in Proc. Int. Conf. Represent. Learning (ICRL), 2023,
pp. 26295–26318.
[23] S. Schmidl, P. Wenig, and T. Papenbrock, “Anomaly detection in time
series: A comprehensive evaluation,” Proc. VLDB Endowment, vol. 15,
no. 9, pp. 1779–1797, May 2022.
[24] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” Proc.
VLDB Endowment, vol. 15, no. 6, pp. 1201–1214, Feb. 2022.
[25] W. Zhang, C. Zhang, and F. Tsung, “GRELEN: Multivariate time series
anomaly detection from the perspective of graph relational learning,” in
Proc. Int. Joint Conf. Artif. Intell., Jul. 2022, pp. 2390–2397.
[26] Z. Zhang et al., “STAD-GAN: Unsupervised anomaly detection on multivariate time series with self-training generative adversarial networks,”
ACM Trans. Knowl. Discovery from Data, vol. 17, no. 5, pp. 1–18,
Oct. 2023.
[27] J. Wang, S. Shao, Y. Bai, J. Deng, and Y. Lin, “Multiscale wavelet
graph AutoEncoder for multivariate time-series anomaly detection,”
IEEE Trans. Instrum. Meas., vol. 72, pp. 1–11, 2023.
[28] R. Wu and E. J. Keogh, “Current time series anomaly detection
benchmarks are flawed and are creating the illusion of progress,” IEEE
Trans. Knowl. Data Eng., vol. 35, no. 3, pp. 2421–2429, Mar. 2023.
[29] Y. Yang, C. Zhang, T. Zhou, Q. Wen, and L. Sun, “DCdetector: Dual
attention contrastive representation learning for time series anomaly
detection,” in Proc. 29th ACM SIGKDD Conf. Knowl. Discovery Data
Mining, Aug. 2023, pp. 3033–3045.
[30] S. Mehran Kazemi et al., “Time2 Vec: Learning a vector representation
of time,” 2019, arXiv:1907.05321.
[31] Z. Shao, Z. Zhang, F. Wang, W. Wei, and Y. Xu, “Spatial–temporal
identity: A simple yet effective baseline for multivariate time series
forecasting,” in Proc. 31st ACM Int. Conf. Inf. Knowl. Manage.,
New York, NY, USA, Oct. 2022, pp. 4454–4458.
[32] J. G. Proakis, Digital Signal Processing: Principles Algorithms and
Applications. London, U.K.: Pearson, 2001.
[33] H. Zhao et al., “Multivariate time-series anomaly detection via graph
attention network,” in Proc. IEEE Int. Conf. Data Mining (ICDM),
Nov. 2020, pp. 841–850.
[34] B. Farhang-Boroujeny, Adaptive Filters: Theory and Applications. Hoboken, NJ, USA: Wiley, 2013.
[35] S. E. Jabari and H. X. Liu, “A stochastic model of traffic flow:
Theoretical foundations,” Transp. Res. B, Methodol., vol. 46, no. 1,
pp. 156–174, Jan. 2012.
[36] S. E. Jabari and H. X. Liu, “A stochastic model of traffic flow: Gaussian
approximation and estimation,” Transp. Res. B, Methodol., vol. 47,
pp. 15–41, Jan. 2013.
[37] L. V. Jospin, H. Laga, F. Boussaid, W. Buntine, and M. Bennamoun,
“Hands-on Bayesian neural networks—A tutorial for deep learning
users,” IEEE Comput. Intell. Mag., vol. 17, no. 2, pp. 29–48, Feb. 2022.
[38] D. P. Kingma and M. Welling, “Auto-encoding variational Bayes,” in
Proc. 2nd Int. Conf. Learn. Represent. (ICLR), Banff, AB, Canada, 2014,
pp. 1–14.
[39] I. Chivers and J. Sleightholme, “An introduction to algorithms and the
big O notation,” in Introduction to Programming With Fortran. Cham,
Switzerland: Springer, 2015, pp. 359–364.
[40] P. Varaiya, “Freeway data collection, storage, processing, and use,” in
Proc. Transp. Res. Board Workshop, Roadway Infostructure, Aug. 2002,
pp. 1–22.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
LI et al.: SpectraBayes: EXPLORING TRAFFIC SERIES RECONSTRUCTION IN FREQUENCY DOMAIN

13

[41] O. Alghushairy, R. Alsini, T. Soule, and X. Ma, “A review of local
outlier factor algorithms for outlier detection in big data streams,” Big
Data Cognit. Comput., vol. 5, no. 1, p. 1, Dec. 2020.
[42] G. R. Terrell and D. W. Scott, “Variable kernel density estimation,” Ann.
Statist., vol. 20, pp. 1236–1265, Sep. 1992.
[43] R. Li, Z. Liu, X. Zhu, L. Li, and X. Cao, “Detecting multivariate time
series anomalies with cascade decomposition consistency,” IEEE Trans.
Instrum. Meas., vol. 74, pp. 1–14, 2025.
[44] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation forest,” in Proc. 8th
IEEE Int. Conf. Data Min., Dec. 2008, pp. 413–422.
[45] T. M. Cover and P. E. Hart, “Nearest neighbor pattern classification,”
IEEE Trans. Inf. Theory, vol. IT-13, no. 1, pp. 21–27, Jan. 1967.
[46] H.-P. Kriegel, M. Schubert, and A. Zimek, “Angle-based outlier detection in high-dimensional data,” in Proc. 14th ACM SIGKDD Int. Conf.
Knowl. Discovery Data Mining, Aug. 2008, pp. 444–452.
[47] H. Abdi and L. J. Williams, “Principal component analysis,” Wiley
Interdiscipl. Reviews, Comput. Statist., vol. 2, no. 4, pp. 433–459,
2010.
[48] H. Wu, T. Hu, Y. Liu, H. Zhou, J. Wang, and M. Long, “TimesNet:
Temporal 2D-variation modeling for general time series analysis,” in
Proc. Int. Conf. Learn. Represent. (ICLR), 2022, pp. 1–23.
[49] A. Zeng, M. Chen, L. Zhang, and Q. Xu, “Are transformers effective
for time series forecasting?,” 2022, arXiv:2205.13504.
[50] K. Yi et al., “Frequency-domain MLPs are more effective learners in
time series forecasting,” in Proc. 37th Int. Conf. Neural Inf. Process.
Syst., Red Hook, NY, USA, 2023, pp. 1–24.
[51] Y. Liu et al., “ITransformer: Inverted transformers are effective for time
series forecasting,” in Proc. 12th Int. Conf. Learn. Represent. (ICLR),
2023, pp. 1–25.
[52] Y. Nie, N. H. Nguyen, P. Sinthong, and J. Kalagnanam, “A time series
is worth 64 words: Long-term forecasting with transformers,” in Proc.
Int. Conf. Learn. Represent. (ICLR), 2022, pp. 1–24.
[53] T. Zhou, Z. Ma, Q. Wen, X. Wang, L. Sun, and R. Jin, “FedFormer:
Frequency enhanced decomposed transformer for long-term series
forecasting,” in Proc. Int. Conf. Mach. Learn., 2022, pp. 27268–27286.
[54] T. Dai, J. Wang, H. Guo, J. Li, J. Wang, and Z. Zhu, “Freqformer:
Frequency-aware transformer for lightweight image super-resolution,”
in Proc. Int. Joint Conf. Artif. Intell. (IJCAI), 2024, pp. 731–739.

Diyin Tang (Member, IEEE) received the B.S.
and Ph.D. degrees from Beihang University, Beijing, China, in 2008 and 2015, respectively. From
2012 to 2013, she was a Visiting Ph.D. Student
with the Department of Mechanical and Industrial
Engineering, University of Toronto, Toronto, ON,
Canada. She is currently an Associate Professor
with the School of Automation Science and Electrical Engineering, Beihang University. Her research
interests include fault prognostics, degradation-based
modeling, and condition-based maintenance.

Ruoheng Li received the B.S. degree from Nanjing University of Aeronautics and Astronautics,
Nanjing, China, in 2020, the B.S. degree from the
Royal Melbourne Institute of Technology University,
Melbourne, VIC, Australia, in 2020, and the M.S.
degree from Nanjing University of Aeronautics and
Astronautics in 2023. She is currently pursuing the
Ph.D. degree with Beihang University. Her current
research interests include data science and intelligent
transportation.

Xianbin Cao (Senior Member, IEEE) received the
B.E. and M.E. degrees in computer applications and
information science from Anhui University, Hefei,
China, in 1990 and 1993, respectively, and the Ph.D.
degree in information science from the University
of Science and Technology of China, Hefei, in
1996. He is currently a Professor with the School
of Electronic and Information Engineering, Beihang University, Beijing, China. His current research
interests include intelligent transportation systems,
air traffic management, and intelligent computation.

Fei Wang received the Ph.D. degree in computer
architecture from the Institute of Computing Technology, Chinese Academy of Sciences, in 2017.
From 2017 to 2020, he was a Research Assistant
with the Institute of Technology, Chinese Academy
of Sciences. Since 2020, he has been working as an
Associate Professor with the Institute of Computing Technology, Chinese Academy of Sciences. His
main research interests include spatiotemporal data
mining, timeseries analysis, and AI for science.

Xi Zhu received the B.E. degree in electronic
and information engineering and the M.E. degree
in control science and engineering from Beijing
University of Technology, Beijing, China, in 2010
and 2013, respectively, and the Ph.D. degree in
signal and information processing from Beihang
University, Beijing, in 2018. He is currently an Associate Researcher with the School of Electronic and
Information Engineering, Beihang University. His
research interests include multivariate time series
analysis, spatiotemporal data mining, and target
behavior cognition.
PAPER_TEXT
