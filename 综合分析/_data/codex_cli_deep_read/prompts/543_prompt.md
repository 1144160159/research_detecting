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
# [543] Self-Supervised Production Anomaly Detection and Progress Prediction Based on High-Streaming Videos
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
编号：543
题名：Self-Supervised Production Anomaly Detection and Progress Prediction Based on High-Streaming Videos
年份：2025
DOI：10.1109/tase.2025.3538328
来源：IEEE Transactions on Automation Science and Engineering
PDF：paper/10.1109_TASE.2025.3538328.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：多媒体、医学、遥感与视频异常检测、入侵检测与网络异常检测
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\543.txt
- 原始字符数：64465
- 本次发送字符数：64465
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 22, 2025

11843

Self-Supervised Production Anomaly Detection
and Progress Prediction Based on
High-Streaming Videos
Yifan Li , Zhi-Hai Zhang , Senior Member, IEEE, Jiaqi Xu ,
Xiaowei Yue , Senior Member, IEEE, and Li Zheng

Abstract— Real-time production monitoring incorporating
progress prediction and anomaly detection is essential for quality
and efficiency. Traditional vision-based anomaly detection methods struggle to differentiate between production-related features
and background noise, and fail to consider the heterogeneity of production stages. This paper introduces an integrated
approach that merges progress prediction and anomaly detection, employing the Autoencoder Process Probability Embedding
(APPE) method. APPE maps the distribution of images from
normal production to a progress-related Gaussian Mixture Model
(GMM), focusing on identifying production-relevant features
while minimizing background interference through the proposed
Spatial Activation Map (SAM). The proposed SAM improves
the interpretability of the neural network by highlighting the
specific features that influence the model’s decisions. The method
is assessed through real-world datasets in the assembly of
water valves and the production of commercial aircraft spoilers.
The case study shows that our approach can achieve superior
effectiveness compared to the benchmark, notably improving
both task performances by integrating progress prediction with
anomaly detection.
Note to Practitioners—In many manufacturing settings, such as
aircraft production, tasks that involve human-robot collaboration
or high-precision manual assembly play a significant role. The
ability to detect anomalies and monitor progress in real-time is
critical for ensuring the quality and efficiency of production. The
manual nature of these operations makes them challenging to
monitor through in-situ embedded digital sensors, yet real-time
operation videos are readily available. Vision-based production
monitoring has been widely used in applications such as product
surface inspection, but existing algorithms often face difficulties distinguishing between normal background variations and
anomalies related to production. This paper introduces a new
approach, called Autoencoder Process Probability Embedding
Received 19 August 2024; accepted 9 November 2024. Date of publication
4 February 2025; date of current version 11 April 2025. This article was
recommended for publication by Associate Editor X. Zhang and Editor K. Liu
upon evaluation of the reviewers’ comments. The work of Yifan Li was
supported by NSFC under Grant 724B2019 and Grant 72188101. The work
of Zhi-Hai Zhang was supported by NSFC under Grant 72250710683. The
work of Li Zheng was supported by NSFC under Grant 72188101. The
work of Xiaowei Yue was supported by Beijing National Science Foundation
under Grant 3244032 and Grant L241039. (Corresponding authors: Li Zheng;
Xiaowei Yue.)
Yifan Li, Zhi-Hai Zhang, Xiaowei Yue, and Li Zheng are with the
Department of Industrial Engineering, Tsinghua University, Beijing 100190,
China (e-mail: lyf21@mails.tsinghua.edu.cn; zhzhang@tsinghua.edu.cn;
yuex@tsinghua.edu.cn; lzheng@mail.tsinghua.edu.cn).
Jiaqi Xu is with the Economic Policy and Development Strategy Research
Center, China Waterborne Transport Research Institute, Beijing 100088, China
(e-mail: xujiaqi@wti.ac.cn).
Digital Object Identifier 10.1109/TASE.2025.3538328

(APPE), which integrates progress recognition and anomaly
detection into a cohesive monitoring task, allowing the model to
differentiate between background elements and features related
to production. Although our method is demonstrated in production scenarios as case studies, the proposed SAM mechanism is
versatile to be applied in other contexts with similar types of
categorical labels.
Index Terms— Production monitoring, self-supervised learning, anomaly detection, aircraft assembly monitoring.

I. I NTRODUCTION
RODUCTION monitoring is vital to improve manufacturing efficiency and product quality, reduce the risk
of injuries, and prevent safety accidents. Although existing
methods based on sensor data show promise in automating process control [1], anomaly detection [2], production
monitoring and diagnosis [3], they fall short in industrial
production scenarios that involve continuous manual operations, such as human-robot collaboration tasks or manual
high-precision aerospace assembly. Specifically, these methods
are not sufficient for real-time tracking of progress and process
surveillance because of the lack of well-targeted sensors.
High-streaming videos become ubiquitous in smart factories,
especially as high-resolution video surveillance systems tend
to be more affordable. There is an urgent need to develop production monitoring based on real-time high-streaming videos
and mine values from the collected data.
In production monitoring, there are two major problems:
(i) Progress Prediction: Predicting the ongoing process steps;
(ii)Anomaly Detection: Detecting abnormal activities during
the production process. Vision-based production monitoring
has been increasingly studied in recent years. Notably, welldesigned algorithms have been developed and applied in
various scenarios, including surveillance cameras [4], surface anomaly detection [5], and additive manufacturing [6].
A more comprehensive literature review will be analyzed in
Section II. Although there are some research progresses, the
vision-based monitoring for industrial production processes
still faces unique challenges and complexity:
• Variations in unrelated pixels can significantly exceed
those in areas of interest. As illustrated in Figure 1, the
background variation within the green box is substantially
more pronounced than the anomalous pixels in the red
box. This necessitates training the model to focus more
acutely on pixels pertinent to the anomaly.

P

1558-3783 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

11844

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 22, 2025

Fig. 1. An image comparison between normal and anomaly production
operations.

The appearance of workpieces undergoes considerable
dynamic changes throughout the production process,
resulting in spatial-temporal heterogeneity. The substantial dynamic variation and the heterogeneity make
production anomaly detection extremely complicated.
• There is an inherent scarcity of abnormal data in the
production process since the production line runs in a
normal condition most of the time. The data scarcity
and imbalance raise significant challenges for model
development and parameter learning.
Due to these challenges, the typical video monitoring methods
in the Computer Vision (CV) domain may not work well
in industrial production monitoring. Additionally and more
importantly, the anomaly classification in CV and the anomaly
classification in production monitoring are quite different.
We elucidate the mapping relationship between industrial
production and CV in Figure 2. The first column in this figure
lists the anomaly classes typically identified in the CV domain,
as detailed in [4]. The second column enumerates potential
anomalies that might arise during production operations. These
are further consolidated in the third column, where we provide
a synthesis of these anomalies along with four illustrative
examples.
Anomalies within our focus encompass four categories as
follows. Foreign Object Anomalies: These anomalies arise
from the presence of extraneous or unrelated objects within
the production environment, which could potentially disrupt
the manufacturing process [7]. Worker Operation Anomalies:
This category includes anomalies related to the actions or
postures of workers that are discernible without reference
to the workpiece. Examples include inappropriate assembly
actions or unsafe behaviors [8]. Part Interaction Anomalies:
Anomalies in this category are identifiable without observing
the worker’s actions. They involve the interactions between
parts, such as incorrect assembly order or mispositioning,
indicating a deviation from the intended assembly process [9],
[10]. Progress Correlated Anomalies: These anomalies are
specific to different assembly stages. They may involve the
misuse of tools not intended for certain production stages or
operations that stray from the prescribed process.
Existing research on abnormal production activities primarily focuses on predefined anomaly classes or rules [7], [11],
[12]. However, the anticipation and annotation of all possible
•

future anomalous activities become impractical, especially in
dynamic production environments [4]. Consequently, there
emerges a critical need for a self-supervised anomaly detection
algorithm trained exclusively on normal image data. This
methodology obviates the necessity for abnormal data and
predefined rules, significantly augmenting the model’s ability
to foresee unencountered anomalies.
Moreover, traditional studies often treat progress prediction
and anomaly detection as distinct, isolated tasks. It is essential
to integrate anomaly detection within the predictive model to
withhold stage predictions in anomalous situations. Given that
anomaly detection criteria may vary across different production stages, it is imperative for a model to assimilate real-time
progress information to facilitate precise and contextually
relevant anomaly identification. How to integrate these two
tasks into a unified model remains an open question.
This study endeavors to develop algorithms that can identify
forthcoming anomalies using solely normal production image
data. Utilizing the inherent characteristics of the production process as a self-supervised learning signal enables the
model to concentrate on features pertinent to production,
notwithstanding the extensive variation in background elements. Integrating anomaly detection with progress prediction
tasks not only enhances the model’s accuracy in forecasting
production stages but also furnishes predictions correlated with
progress-related anomalies.
The main contributions of the paper are as follows.
1) An Autoencoder Process Probability Embedding (APPE)
method considering the production state information
is developed to map the distribution of the normal
production process.
2) A Spatial Activation Map (SAM) is proposed to train the
model focus on production-related features. We provide
an interpretative formulation for SAM, thereby augments
the neural network’s explainability and makes its operations more transparent.
3) We advocate the integration of progress prediction and
anomaly prediction to enhance both tasks’ performance
and efficiency.
This paper is structured in the following manner: Section II
offers a detailed overview of relevant research in the field.
The proposed methodology is presented in Section III.
This is complemented by two case studies in Section IV,
which serve to demonstrate the practical effectiveness of our
approach. Finally, conclusions and future work are discussed
in Section V.
II. R ELATED L ITERATURE
As previously highlighted in Section I, the monitoring
task within the assembly process encompasses two principal
components: progress prediction and anomaly detection. This
section offers a detailed review of vision-based techniques for
both tasks. Furthermore, it delves into the attention mechanism
and foreground segmentation, due to their pertinence to the
proposed Spatial Activation Map (SAM).
A. Review on Progress Prediction
Progress prediction research can be segmented into
macro-scale workpiece state analysis and micro-scale action

LI et al.: SELF-SUPERVISED PRODUCTION ANOMALY DETECTION AND PROGRESS PREDICTION

Fig. 2.

11845

Anomaly comparison between computer vision (CV) and industrial production.

recognition. On the macro-scale, the state of production
can be recognized through techniques like RGB color-based
pixel segmentation and edge estimation against CAD models [13], operation classification with Desnet for predefined
operation classes [14], and semantic segmentation algorithms for mechanical part identification [9], [15]. Micro-scale
approaches focus on identifying operators’ actions through
object detection frameworks [16], augmented with pose
estimation [17], neural networks for part and action identification [8], and hand movement tracking to deduce picked
parts [18]. However, within actual production environments,
predictions may become unreliable due to anomalous situations, a critical aspect these methods often overlook.
B. Review on Anomaly Detection
Anomaly detection in production processes employs a
diverse array of vision-based techniques. Research in this
field ranges from the application of preset rules or supervised methods for detecting anomalies to advanced neural
network applications. For example, a neural network was
utilized to identify assembly defects with an 87% success
rate [11], whereas image-to-CAD model comparisons were
implemented to ensure accurate part installation [12], and
contrastive learning was employed to monitor conditions
within a flotation bank [19]. Nevertheless, these approaches
are generally confined to detecting anomalies defined by preset
rules, a limitation in production scenarios where anomaly data
may be scarce and future anomalies difficult to anticipate [4].
To address the scarcity of anomaly data and the unpredictability of anomalies, unsupervised methods have been
adopted. An unsupervised, image-based process monitoring
technique using deep belief networks was proposed [20],
leveraging the energy of restricted Boltzmann machines as a
control statistic for fire anomaly warnings. Specifically in additive manufacturing, an unsupervised method was developed

to target hot-spot detection—an overheating phenomenon,
and assess pixel auto-correlation [6]. A dynamic sparse
subspace learning approach has been developed for online
structural change-point detection of high-dimensional streaming data [21]. Furthermore, some researches [22], [23], [24]
delve into surface variation monitoring and quality status
evaluation in manufacturing by fusing in-plant multi-resolution
measurements and process information, along with employing
manifold learning for feature extraction. Within the wider
context of computer vision, anomaly detection techniques
are broadly categorized into reconstruction-based, probabilistic, and distance-based approaches [4]. Autoencoders (AE),
renowned for their reconstruction-based strategy, are predicated on the assumption that anomalies cannot be effectively
reconstructed. The Variational Autoencoder (VAE) [25] refines
this methodology by using reconstruction probability as an
anomaly indicator. Probabilistic approaches, like that suggested by [26], embed images within a probabilistic space,
flagging an image as anomalous when its probability value
dips below a predetermined threshold. On the other hand,
distance-based methods develop a “normality” model from
training data and evaluate deviations from this model to
determine anomaly scores [27]. Nonetheless, the inability
to distinguish between production-relevant pixels and background variations diminishes the efficacy of these models
in dynamic environments with frequent background changes,
as illustrated in Figure 1.
C. Review of the Attention Mechanism in Computer Vision
The attention mechanism has gained significant popularity in the field of computer vision (CV) following the
advent of transformer-based vision models [28]. Attention
mechanisms exhibit remarkable diversity; for instance, selfattention [28] utilizes the input features as the quer y, key,
and value simultaneously. There are also variants such as

11846

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 22, 2025

additive attention [29] and dot-product attention. However,
these mechanisms primarily alter the network structure without
changing the learning target and is not suitable for introducing
domain preliminary knowledge. Meanwhile, a limited number
of studies have explored supervised attention mechanisms,
such as the work of [30], which leverages annotated arguments to establish supervised attention, thereby enabling a
more focused and effective event detection process. In our
case, we propose a weakly-supervised attention mechanism
using the progress information to construct an attention map
focusing on production-related pixels.
D. Review on Foreground Segmentation
In our research, it is crucial for the model to discern
unrelated variations in image pixels. Traditional foreground
detection algorithms, such as Mixture of Gaussian (MOG),
often simply categorize moving parts as the foreground.
Recently, Class Activation Map (CAM) [31] has become
widely used for weakly supervised identification of classrelated pixels. Based on CAM, foreground attention supervised
by image classes [32] is proposed to localize the object related
pixels. Other research approaches use CAM as a preliminary
foreground prediction, which is then refined through methods
like Expectation-Maximization (EM) [33], background awareness [34], or wave function [35], [36]. While these methods
are effective in localizing object-related areas, our objective
differs. In our context, various types of objects may appear
in the same image, and we lack object class labels, focusing instead on subsets that influence the production process.
Consequently, we propose a Spatial Activation Map extracting
method to determine the importance weights of pixels.
In summary, existing literature on anomaly detection and
attention mechanisms within computer vision underscores a
gap in addressing dynamic and complex production environments. While numerous techniques propose solutions for
specific scenarios, their adaptability is often lacking in the
face of rapidly changing backgrounds and the variety of
object types encountered in production settings, as described
in Figure 1. Moreover, the dependency on predefined rules
or class labels by many approaches limits their applicability
in situations devoid of such readily available information. Our
proposed APPE model seeks to fill this gap by concentrating
on production-relevant features without the prerequisite of
explicit object class labels, thus offering a more versatile and
robust solution for anomaly detection in challenging production environments. Furthermore, in contrast to existing models
that segregate progress prediction and anomaly detection, our
APPE model simultaneously outputs information for both
anomaly detection and progress prediction. This synergistic
approach not only enhances the effectiveness of both tasks
but also reduces computational complexity by half (instead
of training two separate models, we now get the prediction
in one).
III. AUTOENCODER P ROCESS P ROBABILITY E MBEDDING
In this section, we propose a probabilistic modeling network
to embed image data to a Gaussian latent space for anomaly
detection. The overall structure of the proposed APPE is

summarized in Figure 3. Given an image X ∈ R3×w×h with
height h and width w from a production process, the encoder
maps it to low dimensional GMM distributed latent variable
′
′
z ∈ Rd . Besides, the feature map Q ∈ Rl×w ×h with height
h ′ and width w′ generated just before the last convolutions
block is also extracted to a Multilayer Perceptron (MLP) to
generate the proposed SAM. SAM is used as attention weight
to refine the encoder feature. And the decoder reconstructs the
image X′ given z. Then the reconstruction error is calculated
and weighted by SAM to generate a Spatial Activated Reconstruction Error (SARE). The sum of Negative Loglikelihood
Loss (N L L), triplet loss and SARE is used as the loss value
to train the proposed APPE model.
A. Production Process Modeling
Distinct from conventional vision based anomaly detection,
the production process exhibits heterogeneity in image features
across both spatial and temporal dimensions, as depicted
in Figure 4. For spatial heterogeneity, some locations of
the image are production correlated while others are those
background features with different importance. For temporal
heterogeneity, the image features are various in different
production steps. This complexity necessitates a nuanced
approach to analyzing these features.
We assume that the image feature zk ∈ Rd , generated at a
specific progress percentage k ∈ [0, 1], adheres to a Gaussian
distribution with mean µk ∈ Rd and covariance 6 k ∈ Rd×d .
The mean and covariance are of functional heterogeneity along
the process timeline (refer to Eqs. (1)-(3)).
zk ∼ N (µk , 6 k ),
µk = Fµ (k),
6 k = F6 (k).

(1)
(2)
(3)

In our comprehensive study of manufacturing, certain stages of
the production process, like inspection or polishing tasks, were
observed to have minimal impact on the visual characteristics
of the components. Based on these observations, we propose
that Fµ (k) is not a function with continuous variation. Instead,
it takes the form of a piece-wise constant function, demarcated
by separating points y ∈ {0, . . . , n}, where k0 = 0 and kn = 1.
The methodology for unsupervised determination of separable
time-points k y can be defined as a change-point detection
problem [37]. We further elaborate on this concept with a
formula for the piece-wise function as Eq. (4) and Eq. (5).
Fµ (k) = µ y if k y < k ≤ k y+1 , y ∈ {0, . . . , n − 1},
F6 (k) = 6 y if k y < k ≤ k y+1 , y ∈ {0, . . . , n − 1}.

(4)
(5)

Consequently, the distribution of z aligns with a multivariate
Gaussian mixture distribution, as delineated in Eq. (6):
y=n−1

p(z) =

X

(k y+1 − k y )N (z|µ y , 6 y ).

(6)

y=0

There exist two prominent categories associated with selfsupervised, image-based Gaussian Mixture Model (GMM)
embedding. The first category leverages Variational Autoencoders (VAEs), which optimizes the Evidence Lower Bound
(ELBO) under the assumption of a GMM prior [38]. However,

LI et al.: SELF-SUPERVISED PRODUCTION ANOMALY DETECTION AND PROGRESS PREDICTION

Fig. 3.

11847

The structure of the proposed APPE model.

And after every epoch of training, we update Fµ (k) and F6 (k)
according to maximum likelihood estimation.

Fig. 4.

Illustration of spatial-temporal heterogeneity in image features.

this approach exhibits sensitivity to outliers [39]. The second
category combines Autoencoder (AE) with N L L loss, aligning
with other probabilistic embedding techniques [26].
In our research, we adopt the N L L function as our training objective. Unlike existing methods, the cluster y in our
framework is predefined by the production progress k, which
is known as priori during the training phase. Therefore, the
Log-Likelihood function in our context is represented by the
following equation:
log p(z|y) = −

1
(z − µ y )⊤ 6 y−1 (z − µ y )
2

+ log |6 y | + d log(2π ) .

(7)

In this formulation, Fµ (k) and F6 (k) are derived via Maximum Likelihood Estimation (MLE), providing statistical
foundation for our model.
Then the training objective Negative N L L can be formulated as Eq. (8).
NLL =


1
(z − µ y )⊤ 6 y−1 (z − µ y ) + log |6 y | .
2

(8)

B. Spatial Activation Map for Progress Correlated Features
As shown in Figure 1, the variation of anomaly pixels can
be much less than the normal background variation. Therefore,
it is vital for us to employ a mechanism to let the model focus
on production-related pixels. Utilizing object class as weaklysupervised signal, CAM [31] has been proposed to extract
object-related pixels. However, in our cases, it is hard or even
impossible to label the object classes, for each image may
present hundreds of parts in a complex production process.
Therefore, we propose a Spatial Activation Map (S AM ∈
′
′
Rw ×h ), which uses progress state y as a self-supervised signal
to extract a map. The idea of our approach is that when we
want to recognize the proceeding process state, the weight of
the pixels should be large only when it is highly relevant to
the process.
To realize this intuition, we train an MLP with input
feature Q, as visualized in Figure 5. Q is then passed to
a convolutional network with parameter θ generating a map
conv(Q, θ ) = Q′ with equal shape. A subsequent fully
connected network (FCN) without bias is then employed to
classify the process state given the feature map Q′ . We use
f ∈ Rn×l to denote the weights
for FCN. The prePwmatrix
′
−1 Ph ′ −1
′
dicted class vector pre = h ′1w′ i=0
j=0 f Q:,i, j . And the
predicted class is then calculated with a cross-entropy loss
LossC E = −log(pre y ) to train the weights of MLP. Moreover,
to emphasize features that are correlated with progress and to
differentiate the embedding features among classes, we have
integrated a triplet loss function, described in Eq. (9). This
function aims to maintain a margin m ∈ R:
Losstri p = max(|zanchor − z positive |2
− |zanchor − znegative |2 + m 2 , 0).

(9)

11848

Fig. 5.

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 22, 2025

The visualized procedure for producing SAM.

In this equation, z positive ∈ Rd refers to an encoded feature
vector z from the same progress class as zanchor ∈ Rd , whereas
znegative ∈ Rd originates from a different progress class.
During training, we randomly extract two images of the same
class to act as the anchor and positive images, alongside an
image from a different class designated as the negative, and
encode them to get these three feature vectors.
Before computing the SAM, we initially derive a Progress
Activation Map (PAM) that maps the significance of each
progress class. In the absence of global pooling, we obtain
the following:
′
PAM y,i, j = abs(f⊤
:,y Q:,i, j ).

(10)

We use abs(·) to calculate PAM because we aim to measure
the magnitude of influence a spatial location has on the production state class, regardless of whether the influence is positive
or negative. Within this framework, PAM y,i, j represents the
progress scores at each spatial location, offering a precise
quantification of the impact that the location (i, j) has on
predicting the outcome as class y. This metric essentially
mirrors the significance of the specific spatial feature’s contribution to the overall result. A negligible absolute value of
this score implies that discarding the image feature at this
location would not substantially influence the current stage of
progress information. This indicates that the feature at this
specific location holds limited relevance to the process stage
y. Consequently, we can compute SAM according to Eq. 11,
which signifies the spatial feature importance in the production
process. And this interpretative formulation augments the
neural network’s explainability and making its operations more
transparent.
n−1

1X
PAM y .
S AM =
n y=0

(11)

With this interpretation of SAM, we propose to use it as
an attention weight both in the encoder and decoder. To be
specific, in the encoder, we multiply SAM with Q and the

refined feature is then passed through the subsequent network.
In the decoder, after computing the pixel-wise reconstruction
error (X′ − X)2 , SAM is then used as a weight to generate
Spatial Active Reconstruction Error (S A R E) according to
Eq. (12). S A R E is used as the reconstruction loss to train
the decoder. As shown in Figure 3, the reconstruction error
caused by the background or unrelated pixels is subtracted
in S A R E letting the APPE focus more on production-related
pixels. Moreover, the correlation between SAM and progress
classes bolsters the network’s interpretability, elucidating the
features instrumental in the model’s decision-making process.
XXX
S ARE =
(X′c,i, j − Xc,i, j )2 S AMi, j .
(12)
c

i

j

C. Random Erase
As noted by [34], Class Activation Maps (CAM) typically
highlight the most discriminative part of an object rather than
its entirety, a phenomenon that might also occur with our
proposed SAM. To address this issue, we introduce a random
erase procedure during the training process.
We define the procedure to randomly erase a portion of the
input image with a certain probability, dimensions, and aspect
ratio. We randomly generate the erasure rectangle’s position
(r x , r y ) and dimensions (rw , rh ) using uniform distributions,
constrained by the image width and height dimensions w × h
and the specified scale and ratio parameters:
r x ∼ U (0, w), r y ∼ U (0, h),
a ∼ U (al , au ), b ∼ U (bl , bu ),
r
√
awh
, rh = abwh.
rw =
b

(13)
(14)
(15)

In this paper, we let al = 0.02, au = 0.33, bl = 0.3, bu =
3.3. And the erased area will be filled with black pixels,
as visualized in Figure 3. Because in the training procedure,
the most discriminative can be erased. By erasing the image
randomly, the APPE is forced to learn not only the most

LI et al.: SELF-SUPERVISED PRODUCTION ANOMALY DETECTION AND PROGRESS PREDICTION

11849

discriminative part but also all the feature that may contribute
to the determination of process stage.
D. The Overall Learning Objective
Our model leverages an encoder-decoder architecture
to transform image features into a GMM representation.
As detailed in Sections III-B and III-A, the model’s loss
function comprises a weighted reconstruction loss (S A R E),
N L L for fitting the Gaussian mixture distribution, and a
cross-entropy loss together with a triplet loss that allows the
Multi-Layer Perceptron (MLP) to learn attention weights in a
self-supervised manner.
The composite loss function is summarized in Eq. (16),
where λ1 , λ2 , and λ3 ∈ R serve as balancing terms for the
respective loss components:
Loss = LossC E + λ1 Losstri p + λ2 N L L + λ3 S A R E. (16)
Regarding the update of the parameters of the GMM for the
embedded feature distribution, specifically Fµ (k) and F6 (k) in
Eq.(4) and Eq.(5), during the training process: While certain
studies advocate for the joint training of these parameters
to boost performance [26], our observations indicate that the
substantial variability inherent in the normal data distribution
precipitates instability during the joint training procedure.
Consequently, our methodology employs an ExpectationMaximization (EM) based iterative computational approach.
In every training epoch, we refine Fµ (k) and F6 (k) using the
maximum likelihood estimation derived from the features z.
E. Online Prediction and Post-Processing
Our approach, APPE, maps the image feature Xt , generated
during the production process at time t, to a GMM latent
variable z, which follows a GMM distribution:
y=n−1

p(z) =

X

α y N (µ y , 6 y ),

(17)

y=0

where α y = k y+1 −k y denotes the weight of the Gaussian component for process stage y, inferred from the average time cost
of stage y in training videos. The computed p(z) signifies the
likelihood of observing a feature value during normal assembly
conditions. Thus, p(z) is an anomaly score index, where
an image with little p(z) should be treated as an anomaly.
We abstain from employing the reconstruction error as an
anomaly score in this context, as the dynamic background
inherent in the production process can result in challenges
in accurately reconstructing even normal process images.
Additionally, the marginal differences between anomalous and
normal images mean that anomalous images may only exhibit
minimal reconstruction loss. This phenomenon is further elucidated by the performance of AE+SARE, as detailed in
Section IV.
1) Integrating Anomaly Detection with Progress Prediction:
Building upon the aforementioned strategies, we introduce
SAM and a progress-related GMM to direct the APPE’s focus
towards production-relevant features, thereby significantly
improving anomaly detection performance. For the second

Fig. 6. Pipeline of integrating anomaly detection and progress for online
prediction.

component of production monitoring—progress prediction—
we propose leveraging anomaly detection outcomes to refine
progress predictions.
Given a progress prediction ŷ, the reliability of this prediction is quantified by the posterior probability given z generated
in production stage y: p(z| ŷ). Predictions associated with
low confidence threshold p(z| ŷ) < ϵ, ϵ ∈ R, should be
dropped and wait for a reliable prediction afterward. The
online predicting and post-processing pipeline is summarized
in Figure 6. At time t, we get an image Xt and compute
the anomaly score and progress prediction result through the
proposed APPE in an online manner. If a progress prediction
is unreliable ( p(z| ŷ) < ϵ), then the progress prediction for
this image will be dropped, and the predicted progress will be
the same as the last reliable progress prediction yt−1 .
IV. E XPERIMENTAL S TUDY
We evaluate the proposed APPE method by using two
distinct datasets. The first dataset encompasses a water valve
production process, where the assembled parts are the predominant focus of the image data. The second dataset represents a
real-world production scenario, encompassing not only assembly operations but also tasks such as lamination, coating,
and vacuum extraction, involving both mechanical parts and
flexible composite materials.
Our project’s testing environment is configured with
Python 3.8 and CentOS 7.9. To ensure optimal performance
and efficiency in our training process, we utilized a setup
comprising either a single A100 GPU or a dual A100 GPU.
To maintain fairness in our evaluations, all models were
standardized using the ResNet50 architecture as their backbone [40].
A. Water Valve Production
In this section, we present the performance of our proposed model on a dataset from a single-station water valve
production process. The production stages is visualized in
Figure 7, including: (1) assembling the intermediate valve
body; (2) fastening the screw; (4) assembling the middle part
of the valve; (5) assembling the upper part of the valve;
(6) assembling the rocker arm; (7) assembling parts onto
the rocker arm; (8) completing the lower clamp assembly of
the water cut-off valve; and finally, (9) assembling the upper
clamp. The whole process lasts for about 3000 time-frames
per cycle.

11850

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 22, 2025

Fig. 7.

Visualized production stages.

Fig. 8.

Examples of anomalies in assembly.

Fig. 10.

Visualized SAM and reconstructed X′ .

Fig. 11.

The spoilers of aircraft.

Fig. 9. t-SNE Visualization of features z of Water valve production dataset.

The training set contains 11 assembly videos and is
extracted as 29529 images for training. The test set contains
31 assembly videos and is annotated at ten time frames per
interval as normal or anomalous, with a total of 700 anomaly
data points and 5790 normal data points. Anomalies in
the dataset, as shown in Figure 8, include foreign object
anomalies (a), worker operation anomalies (d,e), progress
correlated anomalies (b), and part interaction anomalies (d,c).
It is important to note that some anomaly images may exhibit
characteristics of multiple cases of anomaly and our focus
is detecting if there exists any anomaly no matter what kind
it is.
We utilize t-distributed Stochastic Neighbor Embedding
(t-SNE) to visualize the high-dimensional feature space for
encoded z. t-SNE is a powerful dimensionality reduction
technique that helps to project high-dimensional data into
two or three dimensions while preserving the relative distances between data points. The visualization of the model’s
features is shown in Figure 9. The gradient from light to
dark shades corresponds to the process stages of the image
within the video sequence, with darker shades representing
later stages in the assembly process. We can see that each
process class is concentrated together either for the training
set or testing set. The visualized SAM and reconstructed X′
are shown in Figure 10. This visualized result shows that SAM
mainly focuses on the location where parts being assembled,
will be assembled or hands performing production-related
operations.

B. Commercial Aircraft Spoiler Production
In this study, we evaluate our model’s performance in the
real-world production of commercial aircraft spoilers. This
workstation is selected for its involvement with both mechanical parts and flexible materials. The finished spoiler product is
depicted in Figure 11. The production process is multifaceted,
involving initial pre-assembly work next to tooling, followed
by steps including primer drying, inspection of auxiliary materials, layering of composite materials, and applying films of
various colors. Subsequent stages involve assembling the rigid
structure, covering it with isolation film, and additional steps
like bagging and leak testing, culminating in autoclave curing.
This paper focuses on the spoiler production stages up to the
autoclave process, a period of approximately 3 hours characterized by mixed-line and entirely manual manufacturing. One
particular stage, involving waiting and inspecting, shows no
visible changes in the workpiece’s appearance. Additionally,
the tooling’s position varies in each cycle within the camera’s
shooting range. Visual image data was collected using the
workshop’s monitoring cameras, ensuring no disruption to
production or additional hardware costs.
Our dataset is meticulously compiled from three weeks
of factory surveillance footage. By extracting one frame

LI et al.: SELF-SUPERVISED PRODUCTION ANOMALY DETECTION AND PROGRESS PREDICTION

11851

TABLE I
DATASET D ESCRIPTION FOR C OMMERCIAL A IRCRAFT S POILER P RODUCTION

Fig. 12.

t-SNE Visualization of features z of spoiler production dataset.

every three seconds, we amass a comprehensive collection
of approximately 46,000 images. This dataset is methodically
divided into distinct units: six for training, and seven for
testing, as elaborated in Table I. The training set includs
footage of three different spoiler types, while the test and
validation sets comprise spoilers from both the training set
and an additional, previously untrained spoiler type. Variations
in spoilers are evident in their shapes (from rectangular to
trapezoidal), sizes, and specific structures for wing attachment.
Despite these variations, the production process remains consistent across different spoiler types. Production data during
factory downtime is excluded based on the operational hours
of the facility. For the evaluation of anomaly detection, the
test data is labeled with the collective expertise of multiple
factory personnel and managerial oversight. In total, 23 distinct
anomaly circumstances and 1847 normal circumstances are
labeled. Among the anomalies are instances of pre-assembly
parts getting jammed, workers remaining seated at the tooling
stations during active assembly phases, and premature relocation of tooling and equipment before the completion of the
assembly cycle. The visualized features are shown in Figure 12
with the same interpretation as Figure 9.
C. Baseline Comparison
Here we compare our method with three well-known
anomaly detection algorithms: an AE [41] with reconstruction
error as anomaly score; VAE [25] wherein the reconstruction
probability serves as the anomaly indicator and DaGMM [26].
In addition, we also test the performance of using SARE
in Eq. 12 instead of AE’s reconstruction loss (the column
AE+SARE in the table), to prove the effectiveness of SAM
in focusing on production related feature.

In our study, we employ two widely recognized metrics: the
Area Under the receiver operating characteristic Curve (AUC)
and the Equal Error Rate (EER), to evaluate the effectiveness of various methods. The quantitative results, as detailed
in Table II and III, demonstrate that our proposed method
surpasses all baseline models in overall anomaly detection
performance. Notably, we observ that the AE augmented with
the SAM (AE+SARE) outperform the other three baseline
models. This indicates that SAM’s role in directing the model’s
focus towards production-relevant features is indeed effective.
However, the detection performance still is not satisfactory
compared with or proposed APPE. The primary reason is that
although SAM highlights production-related features, normal
images are still challenging to reconstruct. This is largely
because, in typical production settings, the number of training
samples available is often limited and may not cover all
normal conditions present in the test set. As a result, the
model’s decoder part struggles to learn effectively, leading to
significant reconstruction loss for normal images (as shown in
the last row of Figure 10). However, the encoder part, which
only needs to extract relevant information for reconstructing
production-related features from images, faces a much simpler
task. Therefore, analyzing feature values’ probabilities instead
of the reconstruction loss can circumvent the issues associated
with a poorly trained decoder.
Furthermore, our model exhibits substantial superiority over
all baseline models in detecting specific anomaly subclasses,
including foreign object, worker operation, part interaction,
and progress-correlated anomalies, as shown in Table II.
D. Ablation Studies
To rigorously assess the indispensability of each component
within the APPE framework, we conduct a series of ablation
studies. These studies involve variations of the APPE model;
including the substitution of SAM with CAM, denoted as
APPEC AM ; the removal of SAM, indicated as APPE-noSAM;
the exclusion of N L L, referred to as APPE-noNLL; and
the exclusion of random erase, referred to as APPE-noErase.
Through these modifications, we aim to elucidate the contribution of each individual element to the overall performance
of the APPE model.
The results from our ablation studies are presented in
Table IV. As indicated in the second column, it is evident
that our SAM outperforms alternatives that employ CAM
as a substitute. This superiority stems from CAM’s limited
focus on features that determine the current stage of progress,
whereas SAM enables the capture of all production-relevant
features. This approach not only prevents the loss of crucial
information but also filters out irrelevant production features.

11852

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 22, 2025

TABLE II
Q UANTITATIVE R ESULT FOR A NOMALY D ETECTION IN WATER VALVE P RODUCTION

TABLE III
Q UANTITATIVE R ESULT FOR A NOMALY D ETECTION IN C OMMERCIAL A IRCRAFT S POILER P RODUCTION

TABLE IV
Q UANTITATIVE R ESULT FOR A BLATION S TUDY

TABLE V
A NOMALY D ETECTION W ITH D IFFERENT N UMBERS OF A NNOTATED P RODUCTION S TAGES

Additionally, the overall performance of both APPE-noNLL
and APPE-noSAM, as shown in the third and fourth columns,
is inferior to that of our proposed APPE model, thereby
underscoring the indispensable nature of both SAM and the
progress-related GMM embedding proposed in this study.
Besides, we observer that the subtraction of NLL influences
much less compared with the subtraction of SAM. This is
because after the subtraction of NLL, the model become a
metrics learning without considering the correlation matrix of
features vectors. And information loss from the correlation
matrix is minor compared with the progress related attention
SAM which is the key in our anomaly detection. Furthermore,
APPE outperforms APPE-noErase, proofing the proposed random erase procedure in III-C being vital in improving the
proposed APPE performance.

E. Sensitivity Analysis
Although we can apply the method proposed in [37] to
optimally and unsupervisedly divide and annotate process
stages, it is also important to explore the impact of suboptimal progress information on anomaly detection. To explore
this issue, we conduct a sensitivity analysis by varying the
number of annotated production stages. We investigate how
the anomaly detection performance changes as the number
of annotated production stages n decreases. The quantitative
results are shown in Table V and Figure 13.
As shown in Figure 13, we observe that as the number of
annotated progress stages decreases, the detection performance
for different types of anomalies declines. However, we also
notice some interesting phenomena: when the number of
stages n is greater than 4, the model’s anomaly detection per-

LI et al.: SELF-SUPERVISED PRODUCTION ANOMALY DETECTION AND PROGRESS PREDICTION

11853

TABLE VI
P ROGRESS P REDICTION ACCURACY B EFORE AND A FTER
I NTEGRATING W ITH A NOMALY D ETECTION

Fig. 13. Sensitivity analysis for anomaly detection with different number of
annotated production stages on water valve production dataset.

depicting normal operations as the validation set and compute
the 99% quantile of p(z| ŷ) to determine the threshold value ϵ.
The remaining 30 test videos are used as the test set for
evaluating the performance of progress prediction.
To assess the efficacy of our model in predicting the progression of tasks, we utilize two key metrics. The primary metric
is classification accuracy, which directly measures the model’s
ability to correctly identify the current stage of the production
process. The second metric, Mean Absolute Percentage Error
(MAPE) of time, is calculated as per Eq. 18:
N −1 Ti,n −1
1 X X t−
M A P E% =
N i=0 t=0

Fig. 14.
stages.

SAM learned under different numbers of annotated production

formance does not significantly drop. But when n is less than
or equal to 4, the model’s performance decreases significantly
as the number of annotated stages decreases. To explore the
underlying mechanism behind this phenomenon, we visualize
the SAM learned by the model under different n in Figure 14.
In the first column of the figure, the red box indicates the part
of the workpiece currently being operated on, which needs to
be focused on. We can see that when the number of stages
decreases to 4 or less, the attention weights learned by SAM
are no longer accurate, and the model cannot focus on the
part being operated on. In some images with n = 4, SAM
even completely focuses on incorrect positions, which can be
the cause of detection drop of worker operation anomaly when
n = 4. The above results indicate that the decrease of n makes
SAM unable to learn accurate attention weights which leads
to detection performance drop of anomaly detection.
F. Integrating Anomaly Detection With Progress Prediction
In addition to anomaly detection, our model concurrently
outputs predictions for the current stage of the production process, denoted as ŷ. Anomalous operations can adversely affect
the accuracy of stage recognition. Consequently, as discussed
in Section III-E, we employ post-processing on the recognition
results based on the probability of the ongoing process stage ŷ
to get the final prediction yt for time t. We select a video

Ti,(yi,t )+1 +Ti,yi,t
2

Ti,n

,

(18)

where Ti,yi,t denotes the starting time of the predicted process
stage yi,t in video i at time t, Ti,n is the ending time of the last
stage (i.e., the total number of frames in video i), and N is the
number of videos in the testing set. This formulation portrays
progress prediction as a continuous endeavor by computing the
Ti,yi,t +Ti,(yi,t )+1
temporal midpoint,
, of the anticipated category
2
as the predicted value. This approach not only evaluates the
likelihood of accurate model predictions but also quantitatively
measures the model’s prediction deviation by juxtaposing this
predicted value with the actual occurrence time. This dual
assessment strategy effectively captures both the precision
in distinguishing distinct process stages and the accuracy of
temporal predictions.
The comparative results before and after integration are
presented in Table VI. It is observed that both accuracy and
Mean Absolute Percentage Error (MAPE) improve across both
datasets following integration, especially under anomaly situations. This demonstrates that integrating anomaly detection
with progress prediction can enhance the performance of both
tasks.
G. Discussion
In conclusion, the comparative analyses with baseline models across two distinct datasets, as illustrated in Table II
and Table III, unequivocally demonstrates the superior efficacy of our proposed APPE approach in detecting all the
anomalies summarized in Figure 2. Further reinforcement of
our model’s effectiveness is provided by the ablation studies
detailed in Table IV, which highlight the critical contribution
of each component within our framework. Our APPE model
adeptly addresses the dual challenges of anomaly detection
and progress prediction within a singular, cohesive framework.
This integration not only halves the computational complexity

11854

IEEE TRANSACTIONS ON AUTOMATION SCIENCE AND ENGINEERING, VOL. 22, 2025

traditionally associated with handling these tasks independently but also synergistically enhances the performance of
both functions. Moreover, the visual insights offered by the
SAM, exemplified in Figure 10.
V. C ONCLUSION
In this study, we propose the APPE model, designed to
map images from normal production operations to a GMM,
taking into account the heterogeneity of image features across
different stages of the process. The implementation of the
SAM as an attention mechanism within both the encoder
and decoder significantly enhances the APPE’s focus on
production-relevant features. Furthermore, SAM contributes to
improving the interpretability of the APPE model, allowing
for a clearer understanding of how it identifies and reacts to
various features within the production environment.
Our approach uniquely integrates progress prediction and
anomaly detection into a cohesive task, leveraging the SAM
and progress-related GMM to establish a framework enhancing
the anomaly detection performance. This also enables the
refinement of progress prediction through posterior anomaly
scoring, resulting in improved accuracy and MAPE across both
datasets examined.
Through the lens of two case studies, the APPE model
demonstrates superior performance in anomaly detection,
achieving higher AUC and EER metrics compared to four
well-established baselines. This underscores the effectiveness
and adaptability of our model in addressing the complexities
of real-world production monitoring, marking a significant
advancement in the fields of anomaly detection and progress
prediction within industrial environments.
For future research, exploring anomaly clustering to classify
various types and diagnose the causes of anomalies presents
a compelling direction. Additionally, considering the use of
multi-frame images as input to account for the temporal
association of features offers another avenue for advancing
the field.
VI. DATA AND C ODE AVAILABILITY
To uphold the principles of transparency and reproducibility in research, we provide the code, model checkpoints,
logs for the method proposed in this paper with this
link: https://cloud.tsinghua.edu.cn/d/cfb8aeafcd174b748167/.
And the dataset for the water-valve production can be found
at [37].
R EFERENCES
[1] L. Zhou, H. Wang, C. Berry, X. Weng, and S. J. Hu, “Functional
morphing in multistage manufacturing and its applications in highdefinition metrology-based process control,” IEEE Trans. Autom. Sci.
Eng., vol. 9, no. 1, pp. 124–136, Jan. 2012.
[2] D. Li, J. Lu, T. Zhang, and J. Ding, “Self-supervised learning and
multisource heterogeneous information fusion based quality anomaly
detection for heavy-plate shape,” IEEE Trans. Autom. Sci. Eng., vol. 21,
no. 2, pp. 1223–1234, Apr. 2024.
[3] R. Guo, K. Guo, and J. Dong, “Phase partition and online monitoring
for batch process based on multiway BEAM,” IEEE Trans. Autom. Sci.
Eng., vol. 14, no. 4, pp. 1582–1589, Oct. 2017.
[4] B. Ramachandra, M. J. Jones, and R. R. Vatsavai, “A survey of singlescene video anomaly detection,” IEEE Trans. Pattern Anal. Mach. Intell.,
vol. 44, no. 5, pp. 2293–2312, May 2022.

[5] V. Zavrtanik, M. Kristan, and D. Skočaj, “DRAEM—A discriminatively trained reconstruction embedding for surface anomaly detection,”
in Proc. IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021,
pp. 8330–8339.
[6] H. Yan, M. Grasso, K. Paynabar, and B. M. Colosimo, “Real-time
detection of clustered events in video-imaging data with applications
to additive manufacturing,” IISE Trans., vol. 54, no. 5, pp. 464–480,
2021, doi: 10.1080/24725854.2021.1882013.
[7] R. J. Kuo and F. F. Nursyahid, “Foreign objects detection using deep
learning techniques for graphic card assembly line,” J. Intell. Manuf.,
vol. 34, no. 7, pp. 2989–3000, Oct. 2023, doi: 10.1007/s10845-02201980-7.
[8] C. Chen et al., “Monitoring of assembly process using deep learning
technology,” Sensors, vol. 20, no. 15, p. 4208, Jul. 2020.
[9] J. Wang, C. Chen, and C. Dai, “A mechanical assembly monitoring
method based on domain adaptive semantic segmentation,” Int. J. Adv.
Manuf. Technol., vol. 128, nos. 1–2, pp. 625–637, Sep. 2023.
[10] C. Chen, C. Zhang, C. Li, and J. Hong, “Assembly monitoring using
semantic segmentation network based on multiscale feature maps and
trainable guided filter,” IEEE Trans. Instrum. Meas., vol. 71, pp. 1–11,
2022.
[11] H. Huang, Z. Wei, and L. Yao, “A novel approach to component assembly inspection based on mask R-CNN and support vector machines,”
Information, vol. 10, no. 9, p. 282, Sep. 2019.
[12] H. Ben Abdallah, I. Jovančević, J.-J. Orteu, and L. Brèthes, “Automatic
inspection of aeronautical mechanical assemblies by matching the 3D
CAD model and real 2D images,” J. Imag., vol. 5, no. 10, p. 81,
Oct. 2019.
[13] M. Kim et al., “A vision-based system for monitoring block assembly
in shipbuilding,” Comput.-Aided Des., vol. 59, pp. 98–108, Feb. 2015.
[14] W. Tao, M. Al-Amin, H. Chen, M. C. Leu, Z. Yin, and R. Qin, “Realtime assembly operation recognition with fog computing and transfer
learning for human-centered intelligent manufacturing,” Proc. Manuf.,
vol. 48, pp. 926–931, Jan. 2020.
[15] C. Chen, C. Li, D. Li, Z. Zhao, and J. Hong, “Mechanical assembly
monitoring method based on depth image multiview change detection,”
IEEE Trans. Instrum. Meas., vol. 70, pp. 1–13, 2021.
[16] J. Patalas-Maliszewska, D. Halikowski, and R. Damaševičius, “An automated recognition of work activity in industrial manufacturing using
convolutional neural networks,” Electronics, vol. 10, no. 23, p. 2946,
Nov. 2021.
[17] C. Chen, T. Wang, D. Li, and J. Hong, “Repetitive assembly
action recognition based on object detection and pose estimation,”
J. Manuf. Syst., vol. 55, pp. 325–333, Apr. 2020. [Online]. Available:
https://www.sciencedirect.com/science/article/pii/S0278612520300625
[18] L. Liu, Y. Liu, and J. Zhang, “Learning-based hand motion capture and
understanding in assembly process,” IEEE Trans. Ind. Electron., vol. 66,
no. 12, pp. 9703–9712, Dec. 2019.
[19] M. Ai, Y. Xie, S. X. Ding, Z. Tang, and W. Gui, “Domain knowledge
distillation and supervised contrastive learning for industrial process
monitoring,” IEEE Trans. Ind. Electron., vol. 70, no. 9, pp. 9452–9462,
Sep. 2023.
[20] Y. Lyu, J. Chen, and Z. Song, “Image-based process monitoring using
deep learning framework,” Chemometric Intell. Lab. Syst., vol. 189,
pp. 8–17, Jun. 2019.
[21] R. Xu, J. Wu, X. Yue, and Y. Li, “Online structural change-point detection of high-dimensional streaming data via dynamic sparse subspace
learning,” Technometrics, vol. 65, no. 1, pp. 19–32, Jan. 2023, doi:
10.1080/00401706.2022.2046171.
[22] S. Suriano, H. Wang, C. Shao, S. J. Hu, and P. Sekhar, “Progressive
measurement and monitoring for multi-resolution data in surface manufacturing considering spatial and cross correlations,” IIE Trans., vol. 47,
no. 10, pp. 1033–1052, Oct. 2015.
[23] C. Liu, Z. Kong, S. Babu, C. Joslin, and J. Ferguson, “An integrated
manifold learning approach for high-dimensional data feature extractions
and its applications to online process monitoring of additive manufacturing,” IISE Trans., vol. 53, no. 11, pp. 1215–1230, 2021, doi:
10.1080/24725854.2020.1849876.
[24] A. AlBahar, I. Kim, and X. Yue, “A robust asymmetric kernel function
for Bayesian optimization, with application to image defect detection in
manufacturing systems,” IEEE Trans. Autom. Sci. Eng., vol. 19, no. 4,
pp. 3222–3233, Oct. 2022.
[25] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly detector for
robot-assisted feeding using an LSTM-based variational autoencoder,”
IEEE Robot. Autom. Lett., vol. 3, no. 3, pp. 1544–1551, Jul. 2018.

LI et al.: SELF-SUPERVISED PRODUCTION ANOMALY DETECTION AND PROGRESS PREDICTION

[26] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Represent., 2018.
[Online]. Available: https://openreview.net/pdf?id=BJJLHbb0[27] M. Sabokrou, M. Fayyaz, M. Fathy, and R. Klette, “Deep-cascade:
Cascading 3D deep neural networks for fast anomaly detection and
localization in crowded scenes,” IEEE Trans. Image Process., vol. 26,
no. 4, pp. 1992–2004, Apr. 2017.
[28] K. Han et al., “A survey on vision transformer,” IEEE Trans. Pattern
Anal. Mach. Intell., vol. 45, no. 1, pp. 87–110, Jan. 2023. [Online].
Available: https://www.ncbi.nlm.nih.gov/pubmed/35180075
[29] D. Bahdanau, K. Cho, and Y. Bengio, “Neural machine translation by
jointly learning to align and translate,” 2014, arXiv:1409.0473.
[30] S. Liu, Y. Chen, K. Liu, and J. Zhao, “Exploiting argument information to improve event detection via supervised attention mechanisms,”
in Proc. 55th Annu. Meeting Assoc. Comput. Linguistics, Jan. 2017,
pp. 1789–1798.
[31] B. Zhou, A. Khosla, A. Lapedriza, A. Oliva, and A. Torralba, “Learning
deep features for discriminative localization,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit. (CVPR), Jun. 2016, pp. 2921–2929.
[32] M. Meng, T. Zhang, Q. Tian, Y. Zhang, and F. Wu, “Foreground
activation maps for weakly supervised object localization,” in Proc.
IEEE/CVF Int. Conf. Comput. Vis. (ICCV), Oct. 2021, pp. 3385–3395.
[33] J. Xu et al., “CREAM: Weakly supervised object localization via class
RE-activation mapping,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern
Recognit. (CVPR), Jun. 2022, pp. 9437–9446.
[34] L. Zhu et al., “Background-aware classification activation map for
weakly supervised object localization,” IEEE Trans. Pattern Anal.
Mach. Intell., vol. 45, no. 12, pp. 14175–14191, Dec. 2023. [Online].
Available: https://www.ncbi.nlm.nih.gov/pubmed/37643092
[35] R. Xu, C. Wang, S. Xu, W. Meng, and X. Zhang, “Wave-like class activation map with representation fusion for weakly-supervised semantic
segmentation,” IEEE Trans. Multimedia, vol. 26, pp. 581–592, 2023.
[36] L. Huang, L. Wang, and H. Li, “Foreground-action consistency network
for weakly supervised temporal action localization,” in Proc. IEEE/CVF
Int. Conf. Comput. Vis. (ICCV), Oct. 2021, pp. 8002–8011.
[37] Y. Li, Z.-H. Zhang, X. Yue, and L. Zheng, “An unsupervised embedding method based on streaming videos for process monitoring in
repetitive production systems,” IISE Trans., pp. 1–16, Sep. 2024, doi:
10.1080/24725854.2024.2386415.
[38] Z. Jiang, Y. Zheng, H. Tan, B. Tang, and H. Zhou, “Variational deep
embedding: An unsupervised and generative approach to clustering,” in
Proc. 26th Int. Joint Conf. Artif. Intell., Aug. 2017, pp. 1965–1972.
[39] L. Yang, W. Fan, and N. Bouguila, “Clustering analysis via deep
generative models with mixture models,” IEEE Trans. Neural Netw.
Learn. Syst., vol. 33, no. 1, pp. 340–350, Jan. 2022. [Online]. Available:
https://www.ncbi.nlm.nih.gov/pubmed/33048769
[40] K. He, X. Zhang, S. Ren, and J. Sun, “Deep residual learning for
image recognition,” in Proc. IEEE Conf. Comput. Vis. Pattern Recognit.
(CVPR), Jun. 2016, pp. 770–778.
[41] M. Maggipinto, A. Beghi, and G. A. Susto, “A deep convolutional
autoencoder-based approach for anomaly detection with industrial,
non-images, 2-dimensional data: A semiconductor manufacturing case
study,” IEEE Trans. Autom. Sci. Eng., vol. 19, no. 3, pp. 1477–1490,
Jul. 2022.

Yifan Li received the B.S. degree from the Department of Industrial Engineering, Tsinghua University,
Beijing, China, and the B.S. degree from the
Department of Mechanical Engineering, Tsinghua
University, in 2021. He is currently pursuing the
Ph.D. degree with the Department of Industrial Engineering, Tsinghua University.
He was a Visiting Student at UC Berkeley in 2020.
He is a Visiting Ph.D. Scholar at ISyE, Georgia
Institute of Technology. His research interests focus
on machine learning for advanced manufacturing,
learning to optimize, computer vision, medical image, and large visionlanguage model. His researches have received several awards, including the
Winner of the IISE QCRE Best Student Paper Award and the Winner of the
INFORMS QSR Best Student Paper Award.

11855

Zhi-Hai Zhang (Senior Member, IEEE) received the
B.S. and Ph.D. degrees in mechanical engineering
from Tsinghua University in 1997 and 2002, respectively. He is currently an Associate Professor with
the Industrial Engineering Department, Tsinghua
University. His current research interests include
production and operational management, resource
allocation optimization, data-driven decision support, supply chain and logistics management, and
production planning and scheduling. He is a member of the IEEE Robotics and Automation Society
(RAS), the Institute for Operations Research and the Management Sciences
(INFORMS), and the Institute of Industrial and Systems Engineers (IISE).

Jiaqi Xu received the dual B.S. degree in industrial
engineering and economics and the Ph.D. degree in
industrial engineering from Tsinghua University in
2018 and 2024, respectively.
He is currently an Assistant Research Fellow
with China Waterborne Transport Research Institute, Beijing, China. His research pursuits primarily
revolve around robust optimization, informationdriven manufacturing, and learning to optimize.

Xiaowei Yue (Senior Member, IEEE) received the
B.S. degree in mechanical engineering from Beijing
Institute of Technology, Beijing, China, in 2011, the
M.S. degree in power engineering and engineering
thermophysics from Tsinghua University, Beijing,
in 2013, and the M.S. degree in statistics and the
Ph.D. degree in industrial engineering from Georgia
Institute of Technology, Atlanta, USA, in 2016 and
2018, respectively.
Currently, he is an Associate Professor at the
Department of Industrial Engineering, Tsinghua
University. Prior to that, he was an Assistant Professor at the Grado Department of Industrial and Systems Engineering, Virginia Tech, Blacksburg, USA.
His research interests focus on machine learning for advanced manufacturing.
He is a Senior Member of ASQ and IISE and a member of ASME and SME.
He was a recipient of the IISE Hamed K. Eldin Outstanding Early Career IE
in Academia Award, the SME Outstanding Young Manufacturing Engineer
Award, the IISE Manufacturing and Design Young Investigator Award, more
than ten best paper awards, and two best dissertation awards. He received the
Grainger Frontiers of Engineering Grant Award from U.S. National Academy
of Engineering (NAE). He serves as an Associate Editor for IISE Transactions,
IEEE T RANSACTIONS ON AUTOMATION S CIENCE AND E NGINEERING, and
IEEE T RANSACTIONS ON N EURAL N ETWORKS AND L EARNING S YSTEMS.
He is selected to be an Editorial Board Member for PNAS Nexus, an openaccess journal of the U.S. National Academy of Sciences (NAS).

Li Zheng received the B.S. and Ph.D. degrees from
Tsinghua University, Beijing, China, in 1986 and
1991, respectively.
He was a Visiting Professor with Georgia
Institute of Technology, Atlanta, GA, USA,
from 1994 to 1996. He is currently a Professor with
the Department of Industrial Engineering, Tsinghua
University. He has published academic articles
in various well-established journals, including
IISE Transactions, IEEE T RANSACTIONS ON
AUTOMATION S CIENCE AND E NGINEERING,
Production and Operations Management, European Journal of Operational
Research, and International Journal of Production Research. His research
interests include production system analysis, vision based production
monitoring, and information-driven manufacturing.
Prof. Zheng is an IISE Fellow. He received several important awards, such
as the National Science and Technology Progress Award in 2005 and the
National Invention Award in 1990.
PAPER_TEXT
