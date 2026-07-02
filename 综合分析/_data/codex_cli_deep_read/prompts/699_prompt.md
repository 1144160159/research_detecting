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
# [699] HFLAD: AI-Driven Hierarchical Fusion Learning for Predictive Anomaly Detection in Consumer-Centric Systems
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
编号：699
题名：HFLAD: AI-Driven Hierarchical Fusion Learning for Predictive Anomaly Detection in Consumer-Centric Systems
年份：2026
DOI：10.1109/tce.2026.3663615
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2026.3663615.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测、时序、日志、KPI 与云原生异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\699.txt
- 原始字符数：53182
- 本次发送字符数：53182
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3663615

1

HFLAD: AI-Driven Hierarchical Fusion Learning
for Predictive Anomaly Detection in
Consumer-Centric Systems
Wei Liu, Hongbo Zhao, Nan Chen, Xu Yang* (IEEE Member), Jiwu Shu* (IEEE Fellow), Hui Cui, Xiaoding
Wang (IEEE Senior Member) and Md. Jalil Piran (IEEE Senior Member)

Abstract—Audit logs, crucial for service auditing and security,
capture user and system activities, which can be effectively
represented as multivariate time series data to enable efficient
log analysis, such as behavior analytics for anomaly detection.
However, it is technically challenging to analyze such data
due to its high dimensionality and strong time correlation. To
address these challenges and enhance predictive security for consumer applications, we propose an AI-driven anomaly detection
model named HFLAD. This model comprehensively considers
the feature and time correlation of multivariate time series
data. It employs causal and dilated convolutions for encoding to
capture multi-scale temporal dependencies, and utilizes an HVAE
(Hierarchical Variational Autoencoder) generator for information
reconstruction. Then, it identifies anomalies by leveraging the
difference between the reconstructed data and the original data.
By leveraging hierarchical fusion learning, HFLAD proactively
detects deviations in consumer-related system activities and audit
logs, aligning with modern security demands in smart devices,
IoT, and online services. Experimental results demonstrate that
HFLAD outperforms other existing techniques in identifying
anomalies, thereby improving the effectiveness of predictive
security measures for consumer systems.
Index Terms—Multivariate Time Series, Anomaly Detection,
Feature Correlation, Time Correlation

I. I NTRODUCTION
In consumer-facing systems such as smart appliances, wearables, and mobile services, audit logs and telemetry streams
are increasingly used to track user–device interactions and
operational status. These data, typically modeled as multivariate time series, form the foundation for AI-driven predictive

This work was supported in part by the National Natural Science Foundation
of China under Grant No. 62302203, and in part by the Science and
Technology Project of State Grid Corporation of China under Grant No. 5700202440239A-1-1-ZN.
Wei Liu, Hongbo Zhao and Jiwu Shu are with the Institute of Artificial Intelligence, Xiamen University, Xiamen, and Wei Liu is also with
NARI Group Corporation/State Grid Electric Power Research Institute,
Nanjing, China, e-mail: liuwei5@stu.xmu.edu.cn, hbzhao@stu.xmu.edu.cn,
shujw@tsinghua.edu.cn.
Nan Chen and Xiaoding Wang are with College of Computer
and Cyber Security, Fujian Normal University, Fuzhou, China, e-mail:
qsx20221346@student.fjnu.edu.cn, wangdin1982@fjnu.edu.cn.
Xu Yang and Jiwu Shu are with the School of Cyber Science and Engineering, Minjiang University, Fuzhou, China, e-mail: xu.yang@mju.edu.cn.
Hui Cui is with the Department of Software Systems & Cybersecurity,
Monash University, Melbourne, Australia, e-mail: hui.cui@monash.edu.
Md. Jalil Piran is with the Department of Computer Science and Engineering, Sejong University, Seoul, South Korea. e-mail: piran@sejong.ac.kr.
Corresponding Authors: Xu Yang and Jiwu Shu

security. As consumer devices become more interconnected
and autonomous, ensuring their behavioral reliability through
predictive anomaly detection is essential [1]–[3].
Notably, consumer systems bear unique characteristics that
make early anomaly detection far more critical than in traditional industrial or enterprise scenarios. For smart home
ecosystems [4], for instance, a delayed response to anomalies
in HVAC (heating, ventilation, and air conditioning) sensor
data could lead to excessive energy consumption or equipment
overheating[1]. In wearable devices, timely identification of
irregularities in heart rate or blood glucose sensor streams
is directly tied to user health—delays could result in missed
warnings for potential medical emergencies, a risk emphasized
in studies of healthcare wearables where real-time anomaly
alerts improve clinical intervention timelines [5]. For mobile
services, early detection of anomalous login patterns (e.g.,
unrecognized locations or unusual device types) can block
account breaches before sensitive user data (such as payment
information or personal messages) is compromised, a capability highlighted as critical for consumer privacy protection in
mobile security frameworks [6].
Traditional approaches such as statistical methods (e.g.,
LOF and Gaussian mixture models) and machine learning
techniques (e.g., clustering or density-based methods) have
laid the foundation for anomaly detection [7]–[9]. However,
these methods often fail to fully capture the intricate temporal
and feature-based interdependencies of multivariate time series
data [10], which are particularly common in telemetry streams
generated by smart consumer devices, such as home sensors,
wearables, and IoT services.
More recently, deep learning models like LSTM [11],
VAE [12], and GAN [13] have demonstrated their ability to
model complex patterns, but they typically focus on either
temporal or feature-based attributes, leading to incomplete
representations. This limitation is especially problematic for
predictive security in consumer environments, where anomalies may manifest through subtle, multi-dimensional interactions—such as coordinated behavior deviations, delayed fault
accumulation, or cross-device anomalies [14]. Hence, there
is a pressing need for AI-driven models that can holistically
integrate temporal dynamics and feature relationships to enable early and accurate identification of abnormal behavior in
consumer-facing applications.
Existing anomaly detection models for multivariate time
series primarily encode either feature correlations or temporal

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3663615

2

dynamics but often neglect their joint modeling, leading to the
following limitations:
Isolated Modeling: Most approaches focus on feature correlations or temporal dependencies in isolation, which limits
the ability to fully represent the interdependencies and complexity inherent in multivariate time series data [15], [16].
Single Time-Scale Modeling: Short time-span encodings
often miss critical long-term dependencies, while long timespan encodings may overlook local patterns. This reliance on
a single time scale prevents effective modeling of inter-scale
temporal impacts [17].
To address these challenges, we propose HFLAD, a hierarchical fusion learning-based anomaly detection model that
captures both temporal trends and latent feature dependencies. HFLAD leverages multiscale time encoders and a relational feature extractor to model normal system behavior
and identifies anomalies based on reconstruction deviation.
This design enables predictive detection of subtle behavioral
shifts in consumer-centric systems before service disruption
or security compromise occurs. The key contributions of this
work include:
(1) We propose a predictive anomaly detection framework
(HFLAD) designed for multivariate time series data,
particularly suited for consumer-centric systems such as
smart home platforms and mobile services. It integrates
temporal modeling and relational reasoning to address
complex behavior monitoring needs.
(2) We design a hierarchical fusion architecture that incorporates a multiscale time encoder and latent relational modeling via a structured recurrent neural network
(SRNN), enabling proactive detection of subtle and
evolving anomalies.
(3) We implement and evaluate HFLAD on four real-world
datasets, demonstrating its superior detection performance across multiple anomaly types and scenarios. The
results highlight its effectiveness in early identification
of risks in consumer-facing applications.
Extensive experiments conducted on public datasets confirm
that HFLAD achieves state-of-the-art performance in anomaly
detection, surpassing existing methods while providing interpretable results.
The rest of this paper is organized as follows: Section II
reviews related work, Section III details the proposed HFLAD
model, Section IV evaluates its performance, and Section VI
concludes this article.
II. R ELATED W ORK
Anomaly detection for multivariate time series has evolved
from statistical approaches to machine learning and deep learning techniques. A summary of their advantages and limitations
is provided in Table I.
A. Statistic-based Methods
Statistical anomaly detection methods typically fit data to
a predefined distribution and identify deviations as anomalies. Parametric approaches, such as Gaussian mixture models [18], assume that data follow fixed distributions, while nonparametric techniques, such as kernel density estimation [19],

do not require prior distribution assumptions. Although statistical methods are interpretable and efficient for small datasets,
they often struggle with scalability and high-dimensional data
complexity.
B. Machine Learning Methods
Machine learning techniques extend statistical methods by
introducing more flexible and adaptive algorithms. Densitybased methods, such as LOF [7], identify anomalies by
measuring the density of local neighborhoods. Distance-based
approaches [20] flag anomalies based on deviations from proximity thresholds. These methods can effectively detect outliers
but are often sensitive to parameter tuning and computationally
intensive for large-scale datasets.
C. Deep Learning Methods
Deep learning has driven significant advancements in
anomaly detection, particularly for complex, high-dimensional
multivariate time series. Prediction-based models, such as
LSTM-NDT [11] and HilBERT [21], forecast time series data
and use prediction errors to detect anomalies. Reconstructionbased methods, including LSTM-VAE [12] and DAGMM [8],
learn latent representations to reconstruct input data, identifying anomalies as reconstruction errors. GAN-based models,
such as MAD-GAN [22], use adversarial training to implicitly
model normal data distributions and detect deviations [23].
While these approaches have achieved success, most focus on either temporal dependencies or feature correlations,
limiting their ability to comprehensively model multivariate
time series. Recent efforts, such as OmniAnomaly [13] and
InterFusion [10], have attempted joint modeling of temporal
and feature information. However, challenges remain in capturing inter-scale temporal patterns and complex inter-variable
relationships.
In recent years, methods based on Transformers and related temporal modeling have significantly advanced robust
anomaly detection [24], [25] for high-dimensional multivariate time series. Addressing the scarcity of anomalous
samples, Anomaly Transformer [26] proposes the ”adjacency
concentration bias” hypothesis, computes association discrepancies via an anomaly-attention mechanism, and amplifies
the discriminability between normal and anomalous samples,
achieving state-of-the-art (SOTA) results across multiple scenarios. TimesNet [27] innovatively transforms 1D time series
into 2D tensors, integrating 2D convolutions with adaptive
Fourier transforms to capture multi-scale temporal patterns,
demonstrating outstanding performance on non-stationary industrial data. Dual-TF [28] adopts a dual-branch Transformer
architecture to process time-domain and frequency-domain
data in parallel, enhancing detection accuracy for noisy industrial scenarios.
III. T HE S TRUCTURE OF HFLAD
Our anomaly detection model, HFLAD, reconstructs multivariate time series data to uncover abnormal patterns deviating
from normal distributions. Unlike general data, multivariate

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3663615

3

TABLE I
A DVANTAGES AND L IMITATIONS OF D IFFERENT M ETHODS

Method

Advantages

Limitations

Statistic-based (Parametric)

Simple, reusable

Assumes fixed distribution

Statistic-based (Non-parametric)

Flexible, adaptive

Greater complexity

Density-based (ML)

Identifies low-density anomalies

Sensitive to density thresholds

Distance-based (ML)

Effective for local patterns

Parameter-dependent

Prediction-based (DL)

Good at time series forecasting

Relies on representation learning

Reconstruction-based (DL)

Extracts informative latent features

Complex latent space learning

GAN-based (DL)

Implicit modeling of normal data

Difficulty overcoming mode collapse

time series possess two defining characteristics: temporal
dependencies and feature correlations. Effective anomaly detection requires jointly modeling both attributes, which many
existing methods fail to address.
As shown in Figure 1, the proposed model consists of three
key modules:
●

Hierarchical Time Encoder: Captures multi-scale temporal patterns using causal, dilated, and temporal convolutional networks.
● Feature Encoder: Extracts inter-variable relationships
with dimensionality reduction.
● HVAE-Based Generator: Reconstructs the original input
by combining multi-level latent representations.

Hierarchical Time Encoder
Causal Convolution

x̂

Feature Encoder

a

zt-1

zt

zt+1

z1

x
Dilated Convolution

b

dt-1

dt

dt+1

z2

Temporal Convolutional
Networks

c

yt-1

yt

yt+1

z3

xt

at

xt-1

at-1

xt-2
.
.
.

at-2
Hidden
Layer 1

.
.
.

Hidden
Layer 2

...

.
.
.

Hidden
Layer n

.
.
.

x3

a3

x2

a2

x1

a1

Fig. 2. Causal Convolution

computes the encoded output a = {a1 , a2 , ..., aT } with K
hidden layers is computed as:
K

HVAE
Generative
Module

Fig. 1. Model Architecture

A. Hierarchical Time Encoder
The time encoding module processes input data X ∈ RM ×T ,
where M represents the feature dimension and T denotes
the time series length. This module integrates three techniques—causal convolution, dilated convolution, and temporal
convolutional networks (TCN)-to capture both short- and longterm temporal patterns.
1) Causal Convolution: As shown in Figure 2, the causal
convolutional network module can be divided into input,
hidden, and output layers. The hidden layers, which is the
key module, perform time series encoding. Causal convolution
ensures the output at time t depends only on the current and
preceding inputs, respecting temporal causality. Given input
x = {x1 , x2 , ..., xT } over time T , the causal convolution

at = ∑ hk xt−k

(1)

k=1

where K is the kernel size and hk denotes the filter coefficients. This operation efficiently captures local temporal
dependencies and provides a foundation for hierarchical encoding. In Algorithm 1, g1 (∗) serves as the causal convolution
module to generate the encoded sequence a.
2) Dilated Convolution: To capture long-term dependencies, dilated convolution expands the receptive field by introducing a dilation rate l. As depicted in Figure 3, dilated
convolution shares the causal convolution architecture but
introduces dilation rate l within convolutional hidden layers.
For input x, the encoded output with K hidden layers is given
by:
K

bt = ∑ hk xt−kl .

(2)

k=1

The receptive field span (K − 1)l + 1, allowing information
from distant time points to be encoded efficiently. By adjusting
l and K, the encoder dynamically balances between local and
global information. In Algorithm 1, g2 (∗) serves as the dilated
convolution module to generate the encoded sequence b.
3) Temporal Convolutional Network (TCN): TCNs integrate causal and dilated convolutions(DC) with additional enhancements, such as weight normalization(WN), dropout, and

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3663615

4

Output b
l=8
Hidden
l=4
Hidden
l=2
Hidden
l=1
Input x

Fig. 3. Dilated Convolution

ReLU activation, ensuring stable training and better scalability.
The TCN outputs c are computed hierarchically, combining
information across multiple temporal scales:
tmp(x) = Dropout (ReLU (WN (DC (x))))

(3)

K

ct = ∑ wk (tmp (tmp(x)))t−lk + x

(4)

B. Feature Encoder
After the Hierarchical Time Encoder generates multi-scale
temporal feature sequences a, b, and c via causal convolution,
dilated convolution, and TCN, these sequences are fed into
the Feature Encoder as independent inputs y (e.g., y = a =
{a1 , a2 , ..., aT }). The core goal of this module is to map
these temporal features to latent variables z1 , z2 , and z3 (via
the mapping function g4 (∗)) while preserving inter-variable
relationships and reducing dimensionality. To achieve this,
we adopt an adapted State-Space Recurrent Neural Network
(SRNN) architecture that integrates state space models with
recurrent neural networks, enabling joint encoding of feature
and temporal dependencies.
At each time step t, the SRNN computes the hidden state
dt and random latent variable zt by balancing the update of
new information and retention of historical states. The hidden
state dt is defined as:
dt = f (ut , dt−1 ) + (1 − ut )d′t ,

(5)

k=1

where wk are learnable weights and b is the bias term. As
shown in Figure 4, TCN effectively captures both local and
long-term dependencies, making it a critical component of
the hierarchical time encoder. In Algorithm 1, g3 (∗) serves
as the temporal convolution network to generate the encoded
sequence c.

where ut is the update gate that controls how much new
information is integrated, d′t is the temporary state capturing
current input features, and f is a learned transition function.
To compute ut and d′t , we introduce the reset parameter
rt that regulates the influence of the previous hidden state
dt−1 . The update gate ut and reset parameter rt are calculated
using the sigmoid activation function σ (which outputs values
between 0 and 1) as:

Dropout

ut = σ(An yt + Bn zt + Cn dt−1 + biasn ),

(6)

ReLU

rt = σ(Ar yt + Br zt + Cr dt−1 + biasr ).

(7)

WeightNorm

Dilated
Concolution

+

c

Here, An , Bn , Cn (and analogous matrices for rt ) are learnable parameters, and biasn (and biasr ) are bias matrices
that adjust the linear transformations of the input yt , latent
variable zt , and previous hidden state dt−1 .The temporary
state d′t is then computed using the tanh activation function
(which constrains values between -1 and 1) to introduce nonlinearity, with the reset parameter rt modulating the contribution of dt−1 via element-wise multiplication (⊙):

Dropout

d′t = tanh(Ad yt + Bd zt + rt ⊙ (Cd dt−1 ) + biasd ),
ReLU

(8)

To model the statistical distribution of latent variables, we
assume the joint distribution of z and d follows a sequential
probabilistic structure, where each time step’s variables depend
on the previous step’s state:

WeightNorm

pθ (z, d∣y, z0 , d0 ) = pθz (z∣d, z0 )pθd (d∣y, d0 )
Dilated
Concolution

x

T

= ∏ pθz (zt ∣zt−1 , dt )pθd (dt ∣dt−1 , yt )

(9)

t=1

Fig. 4. Temporal Convolutional Network. It captures local and long term
dependencies, serving as a key part of the hierarchical time encoder to generate
c.

with z0 and d0 initialized as zero vectors to provide a
starting point for the sequence.We further specify that the
conditional probability of zt given zt−1 and dt follows a
Gaussian distribution, as Gaussian distributions effectively

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3663615

5

model continuous latent spaces and enable efficient learning:
pθz (zt ∣zt−1 , dt ) = N(zt , µt , σt2 I),

(10)

where µt (mean) and σt2 (variance) are dynamically updated
by two feedforward neural networks N N1 and N N2 that
take zt−1 and dt as inputs:
µt = N N1 (zt−1 , dt ),

σt2 = N N2 (zt−1 , dt ).

(11)

To optimize the model parameters θ = {θz , θd }, we maximize the log-likelihood of the latent variables given the input
data, ensuring the model learns meaningful latent representations:
m
τ (θ) = ∑ log pθ (zm ∣ym , zm
0 , d0 ),

(12)

m

where m indexes individual data points. For further refinement of hidden state dynamics, we simplify the transition
function f to fθd (parameterized by θd ):
dt = fθd (yt , dt−1 ),

The Hierarchical Time Encoder and Feature Encoder collectively produce three latent representations z1 , z2 , and z3 ,
each capturing distinct multi-scale temporal and feature dependencies. The HVAE-Based Generator’s role is to fuse
these hierarchical latent variables and reconstruct the original
input x into x̂, following the pipeline:
{z1 , z2 , z3 } → x̂.

The quality of this reconstruction directly determines
anomaly
detection
performance—anomalous
data
(unseen during training) will have larger discrepancies
between x and x̂ than normal data.To achieve effective fusion
and reconstruction, we employ a HVAE [29], which organizes
latent variables into a hierarchical structure to model the
intrinsic distribution of raw data. The key insight is to
impose a probabilistic chain structure on the latent variables,
where higher-level latent variables (capturing complex, global
patterns) guide the distribution of lower-level variables
(capturing fine-grained, local features). This hierarchical
dependency is formalized as:
pθ (z1 , z2 ) = pθ (z1 ∣z2 )pθ (z2 ).

pθ (x, z1 , z2 , z3 )
,
pθ (z1 , z2 , z3 ∣x)

(17)

This formulation ensures that x̂ adheres to the same distribution as the original input x by leveraging the hierarchical
latent structure to capture both local and global data patterns.
The HVAE’s architecture (illustrated in Fig.5) enables chain
conduction between latent variables: z3 (highest-level, complex features) influences z2 , which in turn guides z1 (lowestlevel, fine-grained features). This structure ensures that the
fused latent representation comprehensively encodes all critical dependencies, enabling precise reconstruction of x̂ for
normal data and noticeable deviations for anomalies.

z3
z2

(14)

C. HVAE-Based Generator

x → {z1 , z2 , z3 },

pθ (x̂) =

(13)

and define the likelihood of dt using a regularization function φ to prevent overfitting and stabilize training:
pθd (dt ∣dt−1 , yt ) = min(φ(dt − fθd (dt ))),

conditional probability of x given latent variables to the joint
and posterior probabilities:

(15)

Extending this to all three latent variables, the joint probability of the input x and latent variables z1 , z2 , z3 is decomposed into a product of conditional probabilities, reflecting the
hierarchical fusion process:

z1
x̂
Fig. 5. Hierarchical Variational Autoencoder (HVAE) Generative Module
Architecture. Hierarchical latent variables (z1 , z2 , z3 ) interaction for precise
x̂ reconstruction.

D. Model Training Algorithm
To optimize the model parameters and align the distributions
of reconstructed data x̂ and original data x, we design a
loss function Γloss based on reconstruction accuracy and KL
divergence:
Γloss = Epθ (x̂) Eqφ (z∣x) [log pθ (x∣z)]

(18)

−E[KL(qφ (z∣x)∥pθ (z))]
The training algorithm alternates between encoding time
and feature representations and reconstructing x̂ via HVAE.
Parameters θ and φ are updated using stochastic gradient
descent to minimize Γloss . The whole training process is
detailed in Algorithm 1.

pθ (x, z1 , z2 , z3 ) = pθ (x∣z1 , z2 , z3 )pθ (z1 ∣z2 , z3 )pθ (z2 ∣z3 )pθ (z3 ).
(16) E. Abnormal Score
During training, reconstruction deviations guide parameter
From this joint probability, we derive the distribution of the
reconstructed data x̂ using Bayes’ theorem, which relates the updates. For anomaly detection, we quantify abnormalities
© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3663615

6

Algorithm 1 Training Algorithm
Input: Datasets x
Output: Encoding distribution qφ (z∣x), reconstruction distribution pθ (x̂), parameter spaces θ and φ
Initialize φ, θ for e ← 0 to n do
// n is number of iterations
// time encoding stage
a ← g1 (x) ;
// g1 : causal convolution
b ← g2 (x) ;
// g2 : dilated convolution
c ← g3 (x) ;
// g3 : TCN
// feature encoding stage
z1 , z2 , z3 ← g4 (a, b, c) ; // g4 : feature encoder
// reconstruction stage
x̂ ← h(z1 , z2 , z3 ) ;
// h: HVAE
Floss ← Calculate loss as Eq. 18 Update φ, θ via stochastic gradient descent
end
return θ, φ

using a reconstruction-based anomaly score. Poor reconstruction on anomalous data results in higher scores, indicating
deviations from normal patterns.
The anomaly score is defined as:
Eqϕ (z1 ,z2 ,z3 ∣x) [log pθ (x∣z1 , z2 , z3 )]
=

1 M
i i i
∑[log pθ (x∣z1, z2, z3, )]
M i=1

(19)

Data points with scores exceeding a threshold λ are classified
as anomalous, as they represent patterns unseen during training. This score effectively quantifies model uncertainty and
highlights deviations in new data.
IV. P ERFORMANCE E VALUATION
This section evaluates HFLAD’s performance on multivariate time series datasets, including comparisons with state-ofthe-art models, analysis of detection capabilities on different
anomaly types, complexity evaluations, and ablation studies.
A. Datasets and Experimental Setup
HFLAD is evaluated on four public multivariate time series
datasets:
● SWaT [30]: Water recycling system with 7 days of normal
operation and 4 days of attack, which can simulate
changes in multivariate time series under scenarios such
as equipment anomalies and malicious attacks in industrial environments. It is a classic benchmark dataset for
anomaly detection in the industrial control field.
● MSL [11]: It records sensor perception data (e.g., ambient temperature, equipment voltage) and actuator status
data during the operation of the Mars Rover. Anomaly
types mainly include sensor malfunctions and equipment
operation deviations, which align with the requirements
for equipment reliability and anomaly prediction in the
aerospace field.
● KDD-Cup99 [31]: Constructed based on 9 weeks of
network connection data collected by simulating the U.S.

Air Force local area network environment, including 7
weeks of training data and 2 weeks of test data. Anomaly
types are subdivided into 4 major categories (DOS, R2L,
U2R, PROBING) with a total of 39 types, which can
effectively verify the model’s ability to identify network
attack behaviors.
● ASD [10]: Constructed based on 45 days of operation
monitoring data from 12 servers. Anomaly types mainly
include server performance degradation, resource overload, and service response delay, which are consistent
with the actual operation and maintenance monitoring
scenarios of server clusters in data centers.
Key statistics of the datasets, including the sizes of training/test set, number of dimensions (NoD), and anomaly rates
(ANR), are summarized in Table II. Each dataset contains distinct anomaly types, such as cyberattacks, sensor malfunctions,
intrusion attempts, and system degradations, reflecting realworld challenges in service auditing and security.
TABLE II
T HE DETAIL OF DATASETS

Dataset

Training set

Test set

NoD

ANR(%)

SWaT
MSL
KDD
ASD

475200
58317
56139
102331

449919
73729
24602
51840

51
27 * 55
34
19

12.13
10.72
5.69
4.61

Performance metrics include:
● Precision (P): Fraction of predicted positives that are true
P
positives, P = T PT+F
.
P
● Recall (R): Fraction of actual positives correctly preP
.
dicted, R = T PT+F
N
● F1 Score: Harmonic mean of precision and recall,
F1 =
R
2 PP+R
.
● AUC: Evaluates model discrimination ability, where
higher values indicate better performance with fewer false
positives.
B. Comparison with State-of-the-Art Models
HFLAD is compared with the following benchmarks:
● MSCRED [32]: Uses ConvLSTM networks with attention to model inter-variable correlations.
● MAD-GAN [22]: Leverages LSTM-based GANs for
anomaly detection.
● InterFusion [10]: Fuses temporal modeling and ensemble
learning.
● TFAD [33]: Utilizes time-frequency analysis for feature
extraction.
Performance Results:
● SWaT: HFLAD improves InterFusion’s F1 score by 2.5%
and AUC by 2.51%.
● MSL: HFLAD advances by 3.39% in F1 score and 3.09%
in AUC.
● ASD: Gains of 2.01% in both F1 score and AUC.
● KDD-Cup99: HFLAD exceeds InterFusion by 1.66% in
both metrics.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3663615

7

TABLE III
E XPERIMENTAL R ESULTS OF M ODELS ACROSS DATASETS

SWaT

Method
MSCRED
MAD-GAN
InterFusion
TFAD
Ours

MSL

ASD

KDD-Cup99

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

0.9041
0.8493
0.9182
0.9121
0.9391

0.8392
0.8821
0.9231
0.8604
0.9526

0.8698
0.8653
0.9206
0.8855
0.9458

0.8894
0.8295
0.9002
0.8558
0.9528

0.9106
0.7898
0.9207
0.9097
0.9298

0.8993
0.8089
0.9102
0.8819
0.9409

0.9121
0.9254
0.9513
0.8982
0.9719

0.8923
0.9345
0.9584
0.9181
0.9783

0.9020
0.9299
0.9548
0.9079
0.9751

0.9318
0.9226
0.9624
0.9284
0.9826

0.9229
0.9536
0.9715
0.9397
0.9842

0.9273
0.9378
0.9669
0.9339
0.9834

Fig. 6. The AUC values comparison of models

Fig. 7. F1 score of model in three abnormal modes of ASD dataset

Detailed Analysis:
● MSCRED: Focuses solely on temporal patterns, neglecting inter-variable dependencies, resulting in suboptimal
performance.
● MAD-GAN: Excels at capturing sequence correlations
but overlooks time-series dynamics.
● InterFusion: Combines temporal and feature modeling but
lacks hierarchical depth, limiting its capacity to capture
multi-scale dependencies.
● TFAD: Emphasizes time-frequency analysis, suitable for
specific types of anomalies but less robust for diverse
patterns.
HFLAD Advantage: The hierarchical time encoder and
feature modeling in HFLAD provide comprehensive anomaly
characterization, resulting in robust performance across
datasets.

Performance Analysis:
● MSCRED and TFAD: Detect time trend anomalies effectively due to their emphasis on temporal modeling.
● MAD-GAN: Performs better on sequence correlation
anomalies by leveraging inter-variable dependencies.
● InterFusion: Fuses temporal and feature information, outperforming MSCRED, TFAD, and MAD-GAN.
● HFLAD: Surpasses all benchmarks, demonstrating its
ability to detect diverse anomaly types through hierarchical temporal modeling and feature encoding.
These results highlight HFLAD’s capability to model both
local and global dependencies, ensuring accurate detection of
complex anomaly patterns.

C. Detection of Different Anomaly Types
The ASD dataset includes three types of anomalies:
● Time Trend Anomalies: Deviations from historical patterns.
● Sequence Correlation Anomalies: Changes in intervariable relationships.
● Bimodal Anomalies: A combination of trend and correlation deviations.
Figure 7 compares detection performance on these anomaly
types, and visualizes the results.

D. Time and Space Complexity Analysis
Time Complexity: The time complexity of HFLAD is determined by the operations in hierarchical time encoding, feature
encoding, and reconstruction with HVAE:
● Hierarchical Time Encoding: For n time-series points and
t time scales, assuming linear operations at each time
scale, the time complexity is O(nt).
● Feature Encoding: Assuming a linear transformation of
the d-dimensional data, the time complexity is O(nd).
● Reconstruction (HVAE): If the HVAE model has l layers
with a maximum of m nodes per layer, the time complexity for one data point is O(lmn). For n data points,
the total time complexity is O(nlmn).

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3663615

8

TABLE IV
R ESULTS OF ABLATION EXPERIMENT

SWaT

Method
A
B
C
Ours

MSL

ASD

KDD-Cup99

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

0.8753
0.8989
0.9112
0.9404

0.8931
0.8832
0.8725
0.9538

0.8842
0.8911
0.8914
0.9471

0.8921
0.9123
0.9232
0.9541

0.9137
0.9035
0.8956
0.9314

0.9028
0.9078
0.9091
0.9426

0.9214
0.9032
0.9304
0.9715

0.9235
0.8978
0.9445
0.9680

0.9225
0.9005
0.9374
0.9718

0.9344
0.8997
0.9521
0.9822

0.9234
0.9168
0.9412
0.9789

0.9288
0.9188
0.9466
0.9824

Thus, the overall time complexity of HFLAD is O(nt + nd +
nlmn).
Space Complexity: The space complexity of HFLAD includes the storage for the time-series data, encoded features,
and HVAE model parameters:
● Time-series Data: For n data points, each with d dimensions, the storage requirement is O(nd).
● Encoded Features: If the encoded feature space has p
dimensions, the space required for storing the encoded
features is O(np).
● HVAE Model Parameters: For a model with l layers and
m nodes per layer, the storage required is O(lm).
Therefore, the overall space complexity is O(nd + np + lm).
E. Ablation Studies
To evaluate the contributions of HFLAD’s components, we
conduct ablation experiments with the following variants:
● Scheme A: Replace the time encoder with a simple
LSTM.
● Scheme B: Remove the feature encoder entirely.
● Scheme C: Replace the HVAE generator with a basic
decoder.
Results and Analysis: By selectively replacing or removing
key modules, we can quantify each component’s contribution
to anomaly detection performance. Table IV and Figure 8
illustrate the impact of these modifications:
● Scheme A: HFLAD (Ours) outperforms Scheme A on
all four datasets, with F1-score improvements of 0.0629
(SWaT), 0.0398 (MSL), 0.0532 (ASD), and 0.0554
(KDD-Cup99). Scheme A’s LSTM time encoder fails to
capture hierarchical multi-scale temporal dependencies
(e.g., simultaneous fine-grained pressure surges, flow rate
fluctuations, and coarse-grained temperature in SWaT),
reducing anomaly detection accuracy, while Ours’ hierarchical time encoder models multi-scale dependencies in
parallel.
● Scheme B: HFLAD outperforms Scheme B on all four
datasets, with F1-score improvements of 0.0559 (SWaT),
0.0398 (MSL), 0.0812 (ASD), and 0.0374 (KDD-Cup99).
When Scheme B completely removes the feature encoder, the model fails to capture multivariate collaborative
anomaly patterns due to the lack of inter-variable relationship modeling. In ASD, abnormal correlations between
CPU usage, memory utilization cannot be effectively
identified, while the feature encoder of the HFLAD
explicitly learns inter-variable associations.

●

Scheme C: HFLAD outperforms Scheme C on all four
datasets, with F1-score improvements of 0.0559 (SWaT),
0.0335 (MSL), 0.0423 (ASD), and 0.0396 (KDD-Cup99).
When Scheme C replaces the HVAE generator with a
basic decoder, its simplistic reconstruction capability fails
to capture complex data patterns, limiting anomaly detection performance. Taking KDD-Cup99 network traffic
data as an example, complex attack traffic patterns cannot
be accurately reconstructed by the basic decoder, while
the HVAE generator of HFLAD can learn complex data
distributions.
Summary: These findings validate the necessity of
HFLAD’s components. The hierarchical temporal modeling,
feature encoding, and HVAE generator synergistically enhance
anomaly detection in multivariate time series.

Fig. 8. F1 Score of model ablation experiment

V. D ISCUSSION
This study focuses on consumer-centric systems (e.g., smart
homes, wearables, IoT devices), where user interaction logs,
sensor readings, and device operational metrics often contain
sensitive information. Therefore, from the perspective of privacy preservation, this paper discusses the applicability of the
HFLAD model in real-world scenarios to address the gap. To
address this, HFLAD can be adapted to federated learning (FL)
and differential privacy (DP) as follows:
For FL, a two-tier decentralized framework aligns with
HFLAD’s modular design: resource-constrained consumer devices train lightweight local sub-models (e.g., simplified TCNs

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3663615

9

in the Hierarchical Time Encoder, compact HVAE decoders)
using on-device data, edge servers aggregate local parameter
updates via weighted federated averaging without centralizing
raw data, and only high-confidence anomaly flags are shared
for verification.
For DP, Gaussian noise is added to aggregated FL parameters during server-side aggregation, and Laplacian noise is
injected into local anomaly scores to meet (ε, δ)-DP guarantees—with noise scales calibrated to balance privacy and
detection performance (F1-score drops ≤ 6% on SWaT/ASD
datasets).
These adaptations, combined with parameter pruning to
reduce on-device overhead, enable HFLAD to retain its
multi-scale temporal modeling and hierarchical reconstruction
strengths while complying with regulations and protecting
consumer privacy, making it viable for real-world deployment
in smart homes, wearables, and IoT services.
VI. C ONCLUSION
In this paper, we proposed HFLAD, a hierarchical fusion
learning-based framework for predictive anomaly detection in
multivariate time series. The model integrates multiscale temporal encoding, latent dependency reasoning, and a hierarchical variational reconstruction module to detect abnormal system behaviors. Through extensive experiments on benchmark
datasets, HFLAD demonstrated robust performance across
various anomaly types and datasets. By capturing subtle deviations in time-evolving consumer behavior logs, HFLAD
addresses the growing need for predictive AI security in smart
homes, wearable devices, and mobile services. Its modular
design and general applicability make it suitable for deployment in diverse consumer-oriented scenarios. Future work
will focus on real-time adaptation and edge deployment for
resource-constrained consumer platforms, along with privacypreserving learning extensions to ensure secure and scalable
integration.
R EFERENCES
[1] Shujiang Xie, Lian Li, and Yian Zhu. Anomaly detection for multivariate
time series in iot using discrete wavelet decomposition and dual graph
attention networks. Computers & Security, 146:104075, 2024.
[2] Mohammed Ayalew Belay, Sindre Stenen Blakseth, Adil Rasheed, and
Pierluigi Salvo Rossi. Unsupervised anomaly detection for iot-based
multivariate time series: Existing solutions, performance analysis and
future directions. Sensors, 23(5):2844, 2023.
[3] Usama Tahir, Muhammad Kamran Abid, Muhammad Fuzail, and Naeem
Aslam. Enhancing iot security through machine learning-driven anomaly
detection. VFAST Transactions on Software Engineering, 12(2):01–13,
2024.
[4] Xuan Dai, Jian Mao, Jiawei Li, Qixiao Lin, and Jianwei Liu. Homeguardian: Detecting anomaly events in smart home systems. Wireless
Communications and Mobile Computing, 2022(1):8022033, 2022.
[5] D Pavithra, T Parameswaran, Mani Choudhry, S Amrutha, T Deepa,
and R Kiruthiga. Application of lstm networks for continuous patient
monitoring and anomaly detection in wearable health devices. Indian J.
Sci. Technol, 17(37):3909–3921, 2024.
[6] Viraaji Mothukuri, Prachi Khare, Reza M Parizi, Seyedamin Pouriyeh,
Ali Dehghantanha, and Gautam Srivastava. Federated-learning-based
anomaly detection for iot security attacks. IEEE Internet of Things
Journal, 9(4):2545–2554, 2021.
[7] Markus M Breunig, Hans-Peter Kriegel, Raymond T Ng, and Jörg
Sander. Lof: identifying density-based local outliers. In Proceedings
of the 2000 ACM SIGMOD international conference on Management of
data, pages 93–104, 2000.

[8] Bo Zong, Qi Song, Martin Renqiang Min, Wei Cheng, Cristian
Lumezanu, Daeki Cho, and Haifeng Chen. Deep autoencoding gaussian
mixture model for unsupervised anomaly detection. In International
conference on learning representations, 2018.
[9] Gen Li and Jason J Jung. Deep learning for anomaly detection
in multivariate time series: Approaches, applications, and challenges.
Information Fusion, 91:93–102, 2023.
[10] Zhihan Li, Youjian Zhao, Jiaqi Han, Ya Su, Rui Jiao, Xidao Wen, and
Dan Pei. Multivariate time series anomaly detection and interpretation
using hierarchical inter-metric and temporal embedding. In Proceedings
of the 27th ACM SIGKDD conference on knowledge discovery & data
mining, pages 3220–3230, 2021.
[11] Kyle Hundman, Valentino Constantinou, Christopher Laporte, Ian Colwell, and Tom Soderstrom. Detecting spacecraft anomalies using lstms
and nonparametric dynamic thresholding. In Proceedings of the 24th
ACM SIGKDD international conference on knowledge discovery & data
mining, pages 387–395, 2018.
[12] Daehyung Park, Yuuna Hoshi, and Charles C Kemp. A multimodal
anomaly detector for robot-assisted feeding using an lstm-based variational autoencoder. IEEE Robotics and Automation Letters, 3(3):1544–
1551, 2018.
[13] Ya Su, Youjian Zhao, Chenhao Niu, Rong Liu, Wei Sun, and Dan Pei.
Robust anomaly detection for multivariate time series through stochastic
recurrent neural network. In Proceedings of the 25th ACM SIGKDD
international conference on knowledge discovery & data mining, pages
2828–2837, 2019.
[14] Xingguo Jiang, Hong Luo, Yan Sun, and Mohsen Guizani. Fast anomaly
detection for iot services based on multisource log fusion. IEEE Internet
of Things Journal, 11(6):9405–9419, 2023.
[15] Cheng Wang and Hangyu Zhu. Wrongdoing monitor: A graph-based
behavioral anomaly detection in cyber security. IEEE Transactions on
Information Forensics and Security, 17:2703–2718, 2022.
[16] Hengrun Zhang, Kai Zeng, and Shuai Lin. Federated graph neural
network for fast anomaly detection in controller area networks. IEEE
Transactions on Information Forensics and Security, 18:1566–1579,
2023.
[17] Min Cheng, Qian Xu, LV Jianming, Wenyin Liu, Qing Li, and Jianping
Wang. Ms-lstm: A multi-scale lstm model for bgp anomaly detection. In
2016 IEEE 24th international conference on network protocols (ICNP),
pages 1–6. IEEE, 2016.
[18] Xingwei Yang, Longin Jan Latecki, and Dragoljub Pokrajac. Outlier
detection with globally optimal exemplar-based gmm. In Proceedings
of the 2009 SIAM international conference on data mining, pages 145–
154. SIAM, 2009.
[19] M Pavlidou and G Zioutas. Kernel density outlier detector. In Topics
in Nonparametric Statistics: Proceedings of the First Conference of
the International Society for Nonparametric Statistics, pages 241–250.
Springer, 2014.
[20] Eamonn Keogh, Jessica Lin, Ada Waichee Fu, and Helga Van Herle.
Finding unusual medical time-series subsequences: Algorithms and
applications.
IEEE Transactions on Information Technology in
Biomedicine, 10(3):429–439, 2006.
[21] Shaohan Huang, Yi Liu, Carol Fung, He Wang, Hailong Yang, and
Zhongzhi Luan. Improving log-based anomaly detection by pre-training
hierarchical transformers. IEEE Transactions on Computers, 2023.
[22] Dan Li, Dacheng Chen, Baihong Jin, Lei Shi, Jonathan Goh, and SeeKiong Ng. Mad-gan: Multivariate anomaly detection for time series
data with generative adversarial networks. In International conference
on artificial neural networks, pages 703–716, 2019.
[23] Dongyang Zhan, Kai Tan, Lin Ye, Xiangzhan Yu, Hongli Zhang, and
Zheng He. An adversarial robust behavior sequence anomaly detection
approach based on critical behavior unit learning. IEEE Transactions
on Computers, 2023.
[24] Shaohan Huang, Yi Liu, Carol Fung, He Wang, Hailong Yang, and
Zhongzhi Luan. Improving log-based anomaly detection by pretraining hierarchical transformers. IEEE Transactions on Computers,
72(9):2656–2667, 2023.
[25] Defu Cao, Wen Ye, Yizhou Zhang, and Yan Liu. Timedit: Generalpurpose diffusion transformers for time series foundation model. arXiv
preprint arXiv:2409.02322, 2024.
[26] Jiehui Xu, Haixu Wu, Jianmin Wang, and Mingsheng Long. Anomaly
transformer: Time series anomaly detection with association discrepancy.
arXiv preprint arXiv:2110.02642, 2021.
[27] Haixu Wu, Tengge Hu, Yong Liu, Hang Zhou, Jianmin Wang, and
Mingsheng Long. Timesnet: Temporal 2d-variation modeling for general
time series analysis. arXiv preprint arXiv:2210.02186, 2022.

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for publication in IEEE Transactions on Consumer Electronics. This is the author's version which has not been fully edited and
content may change prior to final publication. Citation information: DOI 10.1109/TCE.2026.3663615

10

[28] Youngeun Nam, Susik Yoon, Yooju Shin, Minyoung Bae, Hwanjun
Song, Jae-Gil Lee, and Byung Suk Lee. Breaking the time-frequency
granularity discrepancy in time-series anomaly detection. In Proceedings
of the ACM Web Conference 2024, pages 4204–4215, 2024.
[29] Jakub Tomczak and Max Welling. Vae with a vampprior. In International
Conference on Artificial Intelligence and Statistics, pages 1214–1223.
PMLR, 2018.
[30] Aditya P Mathur and Nils Ole Tippenhauer. Swat: A water treatment
testbed for research and training on ics security. In 2016 international
workshop on cyber-physical systems for smart water networks (CySWater), pages 31–36. IEEE, 2016.
[31] Richard Lippmann, Joshua W Haines, David J Fried, Jonathan Korba,
and Kumar Das. The 1999 darpa off-line intrusion detection evaluation.
Computer networks, 34(4):579–595, 2000.
[32] Chuxu Zhang, Dongjin Song, Yuncong Chen, Xinyang Feng, Cristian
Lumezanu, Wei Cheng, Jingchao Ni, Bo Zong, Haifeng Chen, and
Nitesh V. Chawla. A deep neural network for unsupervised anomaly
detection and diagnosis in multivariate time series data. In Proceedings
of the AAAI conference on artificial intelligence, pages 1409–1416.
AAAI Press, 2019.
[33] Chaoli Zhang, Tian Zhou, Qingsong Wen, and Liang Sun. Tfad: A
decomposition time series anomaly detection architecture with timefrequency analysis. In Proceedings of the 31st ACM International
Conference on Information & Knowledge Management, pages 2497–
2507, 2022.

Wei Liu is currently a Ph.D. candidate at the Department of Computer Science and Technology, Xiamen
University. He is currently an Senior Engineer of
NARI Group Corporation/State Grid Electric Power
Research Institute, Nanjing, China. His research
interests include deep learning, information security,
operating system, and security of power industry
control system.

Hongbo Zhao is currently a Master of Artificial
Intelligence student with the Institute of Artificial
Intelligence, Xiamen University, Xiamen, China. His
research interest is artificial intelligence.

Nan Chen is currently pursuing the M.S. degree in Network and Information Security from the
School of Computer and Cyberspace Security, Fujian
Normal University. His current research focuses on
anomaly detection and artificial intelligence security.

Xu Yang is currently an Associate Professor with the
School of Cyber Security and Engineering, Minjiang
University, China. He received the Ph.D. degree
from the School of Science, RMIT University, Australia, with Data61, CSIRO in 2021, and used to
be a Postdoctoral Researcher with Fujian Normal
University. He has published 50+ papers in major
conferences/journals, such as IEEE TDSC, TSC,
TIFS, TC, InfoCom, etc. His research interests include cryptography and information security.

Jiwu Shu received the PhD degree in computer
science from Nanjing University, in 1998, and finished the postdoctoral position research with Tsinghua University, in 2000. Since then, he has been
teaching with Tsinghua University, and currently he
is also the president of Minjiang university. His
current research interests include storage security
and reliability, non-volatile memory based storage
systems, and parallel and distributed computing.

Hui Cui received her PhD from University of Wollongong, Australia. Before joining the Department
of Software Systems and Cybersecurity, Faculty of
IT, Monash University, Australia, she was a lecturer
at Murdoch University, Australia. Prior to that, she
worked as a research fellow first at Singapore Management University, Singapore, and then at RMIT
University, Australia and Data61, CSIRO, Australia.

Xiaoding Wang (Member, IEEE) received the
Ph.D. degree from the College of Mathematics
and Informatics, Fujian Normal University, Fuzhou,
China,in 2016. He is currently a Professor with
Fujian Normal University. His research interests
include network optimization and fault tolerance.

Md. Jalil Piran (S’10, M’16, SM’21) is an Associate Professor in the Department of Computer Science and Engineering at Sejong University, Seoul,
South Korea. He earned his Ph.D. in Electronics
and Information Engineering from Kyung Hee University in 2016, followed by a postdoctoral fellowship focused on intelligent communication and datadriven systems. His research spans AI, Machine
Learning, Deep Learning, Big Data Analytics, intelligent, and data-centric systems. He has published
extensively and serves in editorial roles for IEEE
TITS and Engineering Applications of AI, among others, while holding leadership positions in IEEE technical committees and international conferences.
A Senior Member of IEEE, he represented South Korea at the ISO/IEC
MPEG standardization body and is a frequent keynote speaker on AI, machine
learning, and next-generation communication systems. His awards include the
2025 Research Excellence Professor Award (Sejong University), the 2017
Scientist Medal of the Year (IAAM, Sweden), and the 2016 Dissertation of
the Year Award in Engineering (Iran).

© 2026 IEEE. All rights reserved, including rights for text and data mining and training of artificial intelligence and similar technologies. Personal use is permitted,
but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html for more information.
PAPER_TEXT
