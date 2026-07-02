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
# [811] SSCTAD: Semi-Supervised Contrastive Learning for Trajectory Anomaly Detection
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
编号：811
题名：SSCTAD: Semi-Supervised Contrastive Learning for Trajectory Anomaly Detection
年份：2026
DOI：10.1109/tits.2026.3684057
来源：IEEE Transactions on Intelligent Transportation Systems
PDF：paper/10.1109_TITS.2026.3684057.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测、加密流量分类与应用识别
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\811.txt
- 原始字符数：60277
- 本次发送字符数：60277
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

1

SSCTAD: Semi-Supervised Contrastive Learning
for Trajectory Anomaly Detection
Jiaqi Zhang , Zipei Fan , Xuan Song , and Ryosuke Shibasaki

Abstract—Trajectory anomaly detection is critical for transportation safety, solving traffic congestion, optimizing routes, and
other smart city applications. Existing methods often misclassify
reasonable but non-standard trajectories, such as route changes
due to traffic congestion, as anomalies. Additionally, many
methods require extensive labeled datasets for training, however,
in real-world scenarios, trajectory anomaly labeled data are
often scarce and costly to obtain. To address the challenges,
we investigate a Semi-Supervised Contrastive learning approach
for Trajectory Anomaly Detection, namely SSCTAD. Specifically,
SSCTAD integrates a transformer based method to process
trajectories and utilizes the in-out flow encoder to capture the
spatial-temporal patterns from the trajectories, which can help
the model capture the traffic conditions. Then, by leveraging
a small subset of labeled data along with extensive unlabeled
data, SSCTAD utilizes a semi-supervised contrastive learning
component enables the model to better distinguish normal and
anomalous trajectories by maximizing the similarity of latent
representation from the same class and diversifying those from
different classes. This method improves the performance of trajectory anomaly detection and effectively reduces the dependence
of the model on the labeled dataset. Finally, experiments show
that SSCTAD outperforms the other baseline models.
Index Terms—Trajectory anomaly detection, semi-supervised
learning, spatio-temporal patterns, contrastive learning.

I. I NTRODUCTION

W

ITH the widespread adoption of GPS technology,
massive-scale trajectory data, i.e., vehicle trajectories,
are being generated at an unprecedented velocity and volume. These data contain rich behavioral signatures of human
mobility and traffic dynamics, through which many Intelligent
Received 17 August 2024; revised 6 July 2025 and 7 December 2025;
accepted 23 March 2026. This work was supported in part by the National
Science Foundation of China under Grant T2541001, in part by Jilin Provincial
International Cooperation Key Laboratory for Super Smart City, and in part by
Jilin Provincial Key Laboratory of Intelligent Policing. The Associate Editor
for this article was X. Ban. (Corresponding authors: Zipei Fan; Xuan Song.)
Jiaqi Zhang is with the SUSTech-UTokyo Joint Research Center for Super
Smart Cities, Department of Computer Science and Engineering, Southern
University of Science and Technology, Shenzhen, Guangdong 518055, China,
and also with the Research Institute of Trustworthy Autonomous System,
Southern University of Science and Technology, Shenzhen, Guangdong
518055, China (e-mail: 12031097@mail.sustech.edu.cn).
Zipei Fan and Xuan Song are with the School of Artificial Intelligence, Jilin University, Changchun, Jilin 130012, China, and also with the
Research Institute of Trustworthy Autonomous System, Southern University
of Science and Technology, Shenzhen, Guangdong 518055, China (e-mail:
fanzipei@jlu.edu.cn; songxuan@jlu.edu.cn).
Ryosuke Shibasaki is with LocationMind Inc., Tokyo 101-0048, Japan, and
also with the Japan Center for Spatial Information Science, The University of
Tokyo, Tokyo 113-8654, Japan (e-mail: shiba@locationmind.com).
Digital Object Identifier 10.1109/TITS.2026.3684057

Fig. 1. The example of normal trajectories, detour anomaly trajectories and
unexpected detour trajectories.

Transportation Systems (ITS) applications can be realized,
such as traffic management, urban planning, public safety, and
understanding urban human mobility patterns [1], [2], [3], [4].
In these various ITS applications, anomaly trajectory detection has become a critical concern to be solved in many urban
scenarios [5], [6], [7], [8], [9]. This is because trajectory
anomaly detection is valuable for Traffic Management, Urban
Event Management, and Smart Security Center. For instance,
in the Smart Security Center, the monitor can check the
warning detour trajectory after a system alarm to determine
whether it is necessary to take further action. Thus, the
anomaly detection model can be used as a frontline filter to
identify problematic trajectory behaviors, which are further
processed at the Smart Safety Center.
However, detecting anomaly trajectories presents significant
challenges due to the complexity and diversity of vehicle
trajectories. As shown in Fig. 1, the vehicle trajectories from
grid O to grid D in Shenzhen show that the vehicle trajectories
are different from each other, even though they have the same
starting and ending grids, which brings a significant challenge
for trajectory anomaly detection.
Existing methodologies for trajectory anomaly detection
often rely on predefined thresholds and distributions to identify
anomalies [10], [11]. However, these methods struggle with
the dynamic nature of trajectories, as trajectories are influenced
by numerous unpredictable factors such as traffic congestion.
Recent approaches have attempted to learn trajectory features
directly from data [12], [13], [14], but they depend heavily
on the quality of the labels of the datasets. This dependence
makes it challenging to address complex spatio-temporal correlations, leading to potential misclassification [14], [15], [16],
[17]. For instance, as shown in 1 (b), traffic congestion has
occurred on the blue route, causing some vehicles to change

1558-0016 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
2

to a slightly farther route to avoid the congestion, which should
be a normal rather than a detour anomaly.
Furthermore, GPS data usually lacks labels indicating
whether a trajectory is abnormal, necessitating manual labeling
by experts, which is both time-consuming and costly. Some
unsupervised methods attempt to identify anomalies but are
often unreliable due to assumptions about data distribution
or density [11], [18], [19]. The scarcity of labels hinders the
effectiveness of supervised learning approaches, which require
labeled data to learn distinguishing features. To address this,
researchers have proposed semi-supervised learning solutions
that utilize both a small amount of labeled data and a large
unlabeled dataset for training in time series classification [20],
[21].
In this paper, we introduce a contrastive semi-supervised
approach, SSCTAD, for trajectory anomaly detection. Unlike
most existing approaches, SSCTAD utilizes a transformerbased method to learn trajectory features, which allows our
model to better capture the positional information of each
trajectory point. Also, we employ an in-out flow encoder to
learn the traffic flow in a potential passing area, resulting in
more accurate trajectory representation and reduced misclassification.
Then, to overcome the scarcity of anomaly labels, our
model employs a contrastive semi-supervised learning method
that enhances the ability to identify anomalous trajectories
in limited labeled datasets. Specifically, we use a contrastive
learning method to establish a discriminative feature space
by maximizing the differences in the latent representations of
trajectories across categories while minimizing the differences
within each category. Through this process, our model effectively differentiates between normal, detour, and unexpected
detour trajectories with limited labels. Finally, the experiments
on Shenzhen and Chengdu datasets show that our proposed
SSCTAD has better accuracy in trajectory anomaly detection
than the baseline method.
In summary, the main contributions of SSCTAD include:
• SSCTAD utilizes a transformer based trajectory encoder
with an in-out flow encoder, significantly advancing
the capture of complex spatio-temporal dependencies,
thereby reducing misclassification.
• SSCTAD with a contrastive semi-supervised learning
approach enhancing the model’s ability to discern anomalies with a limited labeled datasets. This is particularly
effective in distinguishing trajectory behaviors, such as
normal, detour, and unexpected detour trajectories.
• We demonstrate the efficacy of SSCTAD on Shenzhen
and Chengdu trajectory datasets. The results show that
SSCTAD is better than the baseline model in detecting
anomaly trajectories.
The remainder of this paper is organized as follows:
Section II presents a review of related work in the field of
trajectory anomaly detection. In Section III, we introduce the
preliminary knowledge required to understand the proposed
SSCTAD framework. Section IV, we present the methodology
of our proposed SSCTAD framework. Section V presents an
evaluation of SSCTAD, demonstrating its better than baseline models in detecting both known and unknown anomaly

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

trajectories. Finally, in Section VI, we conclude the paper and
discuss potential directions for future work.
II. R ELATED W ORK
Trajectory anomaly detection has been developed recently,
driven by advances in sensing technologies and computational
methods, which has made it a key aspect in the fields of traffic
safety, smart city, and other directions. This section reviews
the evolution of trajectory anomaly detection methods and
highlights key contributions in the field.
A. Trajectory Anomaly Detection
In this section, we categorize the methods for trajectory
anomaly detection into traditional approaches and deep learning approaches.
1) Traditional Approach: The traditional approaches to
trajectory anomaly detection are based on statistical models,
which use distance or density metrics to produce a deviation
score between normal and anomaly trajectories. For example,
Guo et al. [10] proposed a kinematic estimation-based method
to detect anomalies in vessel trajectories. Lee et al. [18]
introduced a hybrid method combining distance-based and
density-based approaches to detect anomalous trajectories. As
anomaly trajectories are few and significantly dissimilar from
normal trajectories, also with the development of machine
learning, researchers are utilizing machine learning to discover anomaly trajectories. Such as Witayangkurn et al. [22]
proposed an anomaly detection method based on the Hidden
Markov Model (HMM), aiming to detect anomaly events by
identifying abnormal changes in trajectory speed and direction
in urban areas. Zhang et al. [23] introduced the isolation-based
method, called iBAT, to detect anomaly trajectories. However, these traditional methods can effectively detect simple
anomalies but cannot identify complex anomaly trajectories.
For example, the model will misclassify the unexpected detour
trajectories (driving route changes due to traffic congestion or
road closed) as anomalies.
2) Deep Learning Approach: Deep learning methods have
become more prevalent in trajectory-based applications due to
the fact that they can explore the rich context of the underlying
trajectory with remarkable results. We will introduce these
deep learning methods divided into supervised and unsupervised learning methods.
In supervised learning, it requires labeled data to classify
trajectories as either normal or anomalous. It can efficiently
capture complex patterns in the trajectory data. Such as Choi
et al. [17] demonstrated that CNN is highly capable of learning representations of large-scale sequences and identifying
anomalies in the data. Trinh et al. [24] employed LSTM to
process the trajectory in a sequential and recursive manner
to establish the anomaly detection system. Song et al. [19]
utilized labeled data and constructed a supervised learning
method based on RNN to detect anomaly trajectories. Both of
these methods have successfully captured the complex spatiotemporal dependence of vehicle trajectories. While supervised
methods often achieve high accuracy, they depend heavily
on the availability of large labeled datasets, which can be

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ZHANG et al.: SEMI-SUPERVISED CONTRASTIVE LEARNING FOR TRAJECTORY ANOMALY DETECTION

3

challenging to obtain in real-world scenarios, particularly for
rare or novel anomalies.
In contrast to supervised learning, unsupervised learning
methods do not require labeled data. These methods are
particularly useful when labeled data is scarce or unavailable. Among them, many recent anomaly detection methods
are built on generative inference networks, especially Variational AutoEncoder (VAE)-based methods. The VAE consists
of a generative and inference network, which enables the
model to capture complex spatio-temporal structure and to
detect anomalies by identifying deviations from the learned
data distribution. Several recent methods employ VAE variants to achieve anomaly trajectory detection. These methods
encode trajectories into a low-dimensional latent space and
identify anomalous behaviors by detecting trajectories that
deviate from latent clusters. For example, Liu et al. [25] and
Xie et al. [26] utilized a Gaussian Mixture Variational AutoEncoder (GM-VSAE) based method to map each sequence into
latent variables that follow a mixture of Gaussian prior, which
allows the model to represent multiple behavioral modes and
detect anomalous as low-probability samples in the latent
space. Han et al. [27] employed DeepTEA, a VAE-based
method, to identify the anomaly trajectories. It learn the latent
patterns from trajectories during the travel time, and uses the
learned latent patterns to detect anomalies from trajectories.
Additionally, Yu and Huang [28] employed a VAE-based
method, where the anomaly degree is quantified based on the
reconstruction probability of driving behavior feature vectors.
Above all, trajectory anomaly detection methods have
evolved from traditional methods and machine learning to
more advanced deep learning approaches. Although each
method has strengths and achieves better results, there are
still some challenges with these methods. One of the main
challenges is that they tend to misclassify unexpected detour
trajectories as anomaly trajectories. Additionally, many methods require extensive labeled datasets to achieve high anomaly
detection accuracy, which is often scarce in real-world applications. In contrast, SSCTAD integrates a transformer based
method to process trajectories and utilizes the in-out flow
encoder to capture the spatial-temporal patterns from the
trajectories, which can help the model capture the traffic conditions. Then, by leveraging a small subset of labeled data along
with extensive unlabeled data, SSCTAD utilizes a contrastive
semi-supervised learning component, which enables the model
to better distinguish normal and anomalous trajectories by
maximizing the similarity of latent representation from the
same class and diversifying those from different classes.

enhance the learning process. This is particularly relevant in
anomaly detection, where the anomalies themselves are rare
and diverse, making it challenging to collect sufficient labeled
examples for effective supervised learning. For example,
Zhu et al. [29] were among the early pioneers in SSL,
introducing a graph-based approach that propagates labels
from a small set of labeled samples to a large set of unlabeled
data. This method demonstrated that by exploiting the structure
of the data, one could achieve substantial improvements in
classification accuracy, even with limited labeled data. In the
specific context of trajectory anomaly detection, SSL has been
employed to address the scarcity of labeled anomaly data.
In the specific context of trajectory anomaly detection,
SSL has been employed to address the scarcity of labeled
anomaly data. Sillito and Fisher [30] explored this approach by
developing a semi-supervised learning framework tailored to
the unique challenges of trajectory data in a video surveillance
scenario. His work leverages a small set of labeled normal
trajectories and a large pool of unlabeled data to build a model
that can identify anomalies. This method effectively reduces
the reliance on labeled anomaly data, allowing the model to
generalize better to unseen anomalies.
In the context of trajectory anomaly detection, although
SSL has emerged as a powerful tool for anomaly detection,
particularly in addressing the challenge of limited labeled
data. However, in trajectory anomaly detection, it may often
fail to incorporate real-time contextual information, such as
traffic conditions, which are crucial for accurately identifying
anomalies in dynamic urban environments.
So, in our work, we propose a novel deep learning framework, SSCTAD, which employs a trajectory transformer with
contrastive semi-supervised learning to address these challenges. The framework is designed to address the unique
characteristics and complexities inherent in trajectory data, and
the training process does not depend on extensive labeled data.
Additionally, SSCTAD integrates in-out flows with the model,
which addresses the limitations of both traditional anomaly
detection methods and existing SSL frameworks, offering a
more robust solution for dynamic urban environments.

B. Semi-Supervised Learning for Anomaly Detection

A. Definitions

The challenge of limited labeled data in anomaly detection
has led to the exploration of semi-supervised learning (SSL)
techniques. SSL offers a promising avenue by leveraging both
labeled and unlabeled data to improve model performance,
making it particularly well-suited for scenarios where labeled
data are scarce, costly, or difficult to obtain.
The fundamental premise of semi-supervised learning is that
the vast amounts of unlabeled data contain valuable information that, when appropriately harnessed, can significantly

Definition 1 (GPS Trajectory): A GPS trajectory is a
sequence of coordinates recorded by a GPS device during
a trip. Formally, a trajectory, denoted as T , is a sequence
of spatial-temporal points T = (p1 , p2 , . . ., pi ). Each point pi
within this trajectory is represented as a tuple (lati , Loni , ti ),
where Lati and Loni are the latitude and longitude coordinates,
and ti is the corresponding timestamp.
Definition 2 (Mapped Trajectory): In order to improve the
accuracy, we use the map matching process to convert the

III. P RELIMINARIES
This section provides the preliminary knowledge required
to understand the proposed SSCTAD framework. First, we
provide definitions related to trajectory and anomaly trajectory.
Then, we formally define the problem of anomaly trajectory
detection in urban areas.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
4

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

trajectory point p into grid cells r. For a raw GPS point pi ,
the transformation can be represented by a function fmap , as
shown in (1):
ri = fmap (pi )
(1)

embedding network to maintain the continuity of trajectory
points across spatial and temporal domains, as:
Z k
Conv(r) = ( f ∗ R)(r) =
f (y)R(ri + y)dy,
(3)
−k

In our paper, the grid cell information is implicitly embedded through spatial grid encoding based on the Uber H3
system. And we utilize the H3 grid cells at resolution 9, where
the grid is hexagonal and has an average edge length of about
200 meters.
So, an entire trajectory T = (p1 , p2 , . . ., pi ) can be transformed into R = (r1 , r2 , . . ., ri ).
Definition 3 (In-Out Flow): The inout flow of ith grid ri
is characterized by the count of vehicles entering and exiting
that grid over a given time slot. Formally, at the grid ri , the
inout flow IO(ri ) at time ti is defined by the following:
IO(ri ) = (IOin (ri ) : IOout (ri ))

(2)

Here, IOin (ri ) represents the number of vehicles entering
grid ri , IOout (ri ) represents the number of vehicles exiting grid
ri , and both are measured over the same time interval.
Definition 4 (Anomaly Trajectory): Given a trajectory T i ,
which begins at region ro and ends at region rd , if the T i
trajectory’s actual distance and the travel time are both longer
than the typical or expected trajectories from the ro to rd during
the same time period, then the trajectory T i is a detour anomaly
trajectory.
B. Problem Statements
Let c be the trajectory category labeled random variable with
domain c1 , c2 , c3 , where c1 denotes the normal trajectories,
c2 denotes the detour anomaly trajectories, c3 denotes the
unexpected detour trajectories.
The probability of the ith trajectory from area ro to rd
is p(T i ), and the conditional probability p(T i |c1 ) means the
probability of the trajectory T i is a normal trajectory. Higher
p(T i |c1 ) indicates a higher probability that T i is a normal trajectory. Thus, given a set of trajectories T = (T 1 , T 2 , · · · , T n )
from ro to rd , our objective is to identify whether these trajectories are normal trajectories c1 , detour anomaly trajectories
c2 or unexpected detour trajectories c3 .
IV. M ETHODOLOGY
In this section, we introduce the methodology of our proposed SSCTAD framework, as shown in Fig. 2, which contains
Trajectory encoder, Inout flow encoder, Trajectory generator,
Contrastive learning, and Anomaly detector.
A. Trajectory Encoder
The trajectory encoder transforms trajectory data into meaningful feature representations utilizing the convolutional neural
networks and the transformer layers. This process involves
several key steps:
Convolutional Embedding: In order to capture the correlation between the trajectory points and enable the model to
address the irregularity of trajectory points sampling. Inspired
by Trajformer [31], our model utilizes the convolutional

where R represents the input mapped trajectory points
sequence, f : F → R denotes the kernel applied to the input
trajectory points sequence, and F = {−k, −k + 1, · · · , k}. The
final output of the convolutional embedding process is a set
of feature vectors {x1 , x2 , · · · , xn }.
After the convolutional embedding module, the feature
vectors {x1 , x2 , · · · , xn } are passed to a transformer layer,
effectively solving the irregularity and computational cost of
trajectory data. To ensure the Transformer layer understands
the order of trajectory points, the positional encoding is added
to the feature vectors, which injects information about the
relative position of the points in the trajectory. Here, we use
sinusoidal functions, and the final input to the transformer
layer is the sum of the feature vector xi and its positional
embedding PEi :
x̂i = xi + PEi
(4)
Following positional encoding is the Transformer encoder,
the core of our trajectory encoder, which leverages multi-head
self-attention to capture the spatial-temporal dependencies.
The self-attention mechanism computes attention scores based
on three principal components derived from the input: queries
(Q), keys (K), and values (V). For input vector x̂i , such three
vectors are computed by the weight matrices Wq , Wk , Wv ,
respectively:
Q = x̂i Wq ,

K = x̂i Wk ,

V = x̂i Wv

(5)

Then, we perform multi-head self-attention (MSA) to capture the spatio-temporal correlations between each trajectory
point. The operation is defined as:


QK >
V
(6)
St = softmax √
dk
where St is the updated features, dk is the dimensionality of
the key vectors.
After attention is computed, we employ layer normalization
and a position-wise feed-forward network for each position in
the sequence. Then, in order to facilitate training the transformer encoder, residual connections are employed around
each of the sub-layers.
B. In-Out Flow Encoder
Inspired by the study of Zhang et al. [32], [33], our inout flow encoder is designed to capture the dynamic flow of
each urban area through the trajectories. Also, it is essential to
understand the spatial and temporal dynamics of traffic flow.
Firstly, for an hourly time interval, the in-out flow can
be denoted as a matrix Xh ∈ R2×O×D , where Xh is formed
by inflow Ih ∈ RO×D and outflow Oh ∈ RO×D . We apply
convolution kernels on the in-out flow matrices to integrate
the flow information and obtain their temporal embedding:
Xˆh = ReLU(Wh ∗ Xh + bh )

(7)

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ZHANG et al.: SEMI-SUPERVISED CONTRASTIVE LEARNING FOR TRAJECTORY ANOMALY DETECTION

5

Fig. 2. The framewrok of SSCTAD. It consists of four main components: 1) trajectory encoder: utilize the transformer based method to process the mapped
trajectory. 2) Inout flow encoder: We apply convolution kernel on the short-term and long-term in-out flow data to capture the traffic conditions. 3) Trajectory
generator: based the VAE method, our method encodes each trajectory and inflow-outflow into a low-dimensional space, and enables reconstruction of the
inputs by decoding. 4) Contrastive learning: our model attempts to train the trajectories with different modes to follow different Gaussian priors.

where Wh and bh are learnable parameters, ∗ denotes the
convolution operator, and we utilize the ReLU function as
an activation function. Similarly, we can obtain the daily and
weekly time interval of the in-out flow matrix Xd and Xw ,
temporal embedding Xˆd and Xˆw . Finally, we concatenate the
above temporal embedding as follows:
Sio = (Xˆh ; Xˆd ; Xˆw ) · Wt

(8)

where Wt is learnable parameters, and; is the concatenation
operation.
C. Trajectory Generator
The trajectory generator is responsible for producing latent
variable representations from the combined feature vectors
S obtained from the trajectory encoder St and the in-out
flow encoder Sio . This process is crucial for capturing the
underlying structure and variability in the trajectory data,
which aids in anomaly detection.
Inference Net. The Inference Net in our Trajectory Generator plays a critical role in mapping the input combined
feature Si into a lower-dimensional latent space based on the
Variational Autoencoder (VAE). This process allows us to
model the distribution of latent variables zi , which represent

the underlying structure of the trajectory T i , and enables
trajectory anomaly detection. In the context of our model, we
utilize a Gaussian distribution parameterized by a mean µi and
a standard deviation σi , as shown in (9).

zi ∼ q(zi | Si ) = N µi , σ2i
(9)

where N µi , σ2i represents a Gaussian distribution with mean
µi and standard deviation σi . Formally, it can be calculated as
shown below.
µi = g1 (Si )
σi = g2 (Si )

(10)
(11)

where g∗ (·) is the multi-layer perceptron (MLP) function.
Then, we sample from this posterior distribution using the
reparameterization trick, which enables efficient gradient backpropagation during training:
zi = µi + σi · 

(12)

where  is a noise vector sampled from a standard normal
distribution, formally  ∼ N (0, 1), which allows us to generate
latent variables zi from the learned distribution.
Generative Net. Following the recent research on Variational autoencoder (VAE) [34], [35], our generative net is to

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
6

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

utilizes the contrastive loss, which is designed to minimize
the distance between the latent representation of a trajectory
and the Gaussian distribution representing its actual category
while maximizing the distance with the Gaussian distributions
representing the other categories. It can be defined as Eq. (18)

TABLE I
S TATISTICS OF THE DATASETS

cn =

i
X

fI [zi ∈ cn ] · disws (zi , cn )

i=1

generate the original input features through maps of the latent
variables z, ensuring that the latent representation captures the
essential information of the trajectory.
Ŝi = ReLU(Wg zi + bg )

(13)

where Wg and bg are learned weight matrices and bias vectors
of the generative net.
Reconstruction Loss: The reconstruction loss measures
the difference between the input feature vectors S and the
reconstructed feature vectors Ŝ, which guides the learning of
the latent representations.
n

1X
Lrec =
ksi − ŝi k22
n

(14)

i=1

Then, a regularization term based on the KL divergence is
added to the loss function to ensure the latent variables follow
a standard normal distribution. This term penalizes deviations
from the standard normal distribution.


LKL = disKL qφ (zi |si )kpθ (zi )
(15)
The total loss function of the trajectory generator combines
the reconstruction loss and the KL divergence as follows:
Ltg = Lrec + LKL

(16)

The final output of the trajectory generator is the set of
latent variables {z1 , z2 , · · · , zn }. These latent variables provide
a compact and informative representation for our trajectory
anomaly detection.

− log

i
X

!
exp (−disws (zi , cn ))

(18)

i=1

In this equation, fI [zi ∈ cn ] is an indicator function that
equals 1 if the real category of the given trajectory representation zi is in cn , and 0 otherwise. disws (·) is a distance
function, inspired by [35], we devise the distance by a
2-Wasserstein distance [36], [37], which is a metric in the
space of probability, to measure the distance between the latent
representation and the category distribution. It is defined as the
minimum cost of transforming the shape of one probability
distribution into the shape of the other distribution, where
the cost is assumed to be the amount of distribution weight
moved times the moving distance. The 2-Wasserstein distance
between the distribution zi and the distribution cn can be
calculated as Eq. (19)

disws (zi , cn = kµzi − µcn k22 + tr(Σzi + Σcn
q
1
1
(19)
− 2 Σz2i Σcn Σz2i
where k · k2 denotes the Euclidean distance, and tr(·) denotes
the trace of a matrix.
In addition, following the existing supervised contrastive
learning [35], [38], our objective function also includes a
cross-entropy loss to further facilitate the training with some
manually added labels (normal, detour, unexpected detour). As
shown in Eq. (20).
Lcl =

i
X

ci log(ĉi )

(20)

i=1

D. Contrastive Learning
This subsection discusses how contrastive learning enhances
the discriminative power of trajectory anomaly detection. It is
designed to distinguish between normal, detour anomaly, and
unexpected detour, which can effectively solve the problem of
the scarcity of anomaly labels in trajectories, and the trajectory
was incorrectly identified as a detour anomaly due to traffic
congestion or road closure.
In contrastive net, we implicitly associate each given trajectory latent representation zi with a pattern category cn
(e.g., Normal, Detour, or unexpected detour) and assume each
pattern category to be a Gaussian distribution, as shown in
Eq. (17).

cn ∼ N µi , σ2i
(17)
Here, µi and σi are the mean and covariance matrix of
the latent representation zi of trajectories in category cn ,
respectively. Then, in order to estimate the probability of
the real pattern category of a given trajectory, our model

where ci is the real label for the trajectories, ĉi is the predicted
trajectory label by our model, and i is the total number of
categories.
E. Training and Anomaly Recognition
Training: The training process of the proposed framework
is designed to optimize the model parameters by minimizing
the combined loss function. Meanwhile, we also need to
maximize the distance between latent variables zi and other
categories ck,c .
K

Ldis (s, c) =

1 X
[lk − dis (z s , ck )]
K−1

(21)

k,c

Here, lk is the parameter that enforces all ck,c away from cc .
Above all, the total loss function integrates the Ltg , Ldis , and
Lcl , ensuring the model learns to reconstruct the input features
accurately while also discriminating between normal, detour

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ZHANG et al.: SEMI-SUPERVISED CONTRASTIVE LEARNING FOR TRAJECTORY ANOMALY DETECTION

7

anomaly and unexpected detour. The combined loss function
is as follows:
Ltotal = λtg Ltg + λcl Lcl + λdis Ldis

(22)

where λtg , λcl , and λdis are the loss weights used to measure
the importance of the trajectory generator, contrastive learning
module, and the margin-based separation loss. At the same
time, each module is crucial for the finally trajectory anomaly
detection, we adopt the balanced configuration and set λtg =
λcl = λdis = 1.
And our model implemented on Intel(R) Xeon(R) Silver
4214R CPU @ 2.40GHz, and NVIDIA GeForce RTX 3080
Ti (12GB) with python 3.12 and PyTorch 2.7.0. The training
phase is performed using the Adam [39] optimizer with
learning rate 0.001. The batch size is set to 128, and the model
will trained for 500 epochs.
Anomaly Recognition: The anomaly recognition process
leverages the trained model to identify anomaly trajectories.
To enable the SSCTAD to identify the anomaly, we devise
a probabilistic metric rule, inspired by [40], to discriminate
anomalies.
Specifically, we compared the distance between latent representation z with the trajectory categories ck = {c1 , c2 , c3 },
The distance metric dk can be calculated as Eq. (23)
dk = − log (Prec (si )) + disws (zi , ck )

(23)

where, Prec (si ) is the reconstruction probability of the input
features, disws (zi , ck ) is the Wasserstein distance between the
latent representation zi and the trajectory categories ck . And
the trajectory is assigned to the category ck with the minimum
distance, indicating the closest match among the learned
categories, as shown in Eq (24).
ĉ = arg min {dk }

This ensures the trajectory is classified into the most similar
category in the latent space.
V. E VALUATION
A. Datasets
We conducted the experiments using two datasets. As
shown in TABLE I, the Shenzhen dataset was collected from
taxis between 14 October 2019 and 14 November 2019.
The Chengdu dataset is collected from DiDi Chuxing ridehailing orders1 between 1 November 2016 and 30 November
2016. And in our dataset, only standard (non-shared) trips are
included, ride-sharing orders are not present. Therefore, all
trajectories in our experiments correspond to single-passenger
trips, and our anomaly detection results do not consider the
additional detour patterns caused by shared trips.
Following the previous studies [25], [41] and definition, we
first partitioned the urban area into Uber H3.2 Additionally,
we analyzed each trajectory’s distance, as shown in Fig. 3.
Ground Truth: Since the GPS data lacks labels (normal,
detour anomaly, or unexpected detour), and inspired by the
2 https://h3geo.org/

existing works [25], [27], we pick up about 10000 trajectories
from the dataset and manually label whether each trajectory
is normal (c1 ), anomaly (c2 ) or unexpected detour (c3 ). The
labeling process is based on a simple consensus. An example
is exhibited to show how to label a trajectory. Assuming a
trajectory T i starting at ro and ending at rd , the traveling
distance is d, and the traveling time is t s . First, we retrieve
all the trajectories from ro to rd , then identify the trajectory
by judging the trajectory’s traveling distance and time. If the
trajectory’s traveling distance and time are the median of the
retrieved trajectories, the trajectory is normal. If the traveling
distance and time are significantly larger than the median of
the retrieved trajectories, the trajectory is detour anomaly. If
the distance is much longer than the median, but the traveling
time is closer or smaller, the trajectory is unexpected detour.
We split the data into a training set and a testing set, with
90% of the data used for training and 10% for testing. And
we also inject 70% manually labeled data into the training set
and 30% for the testing set.

(24)

k

1 https://outreach.didichuxing.com

Fig. 3. The travel distance distribution of shenzhen and chengdu.

B. Evaluation Metrics
To assess the performance of our model, we employed
commonly used metrics from existing studies [25], [27]:
Precision, Recall, F1-score, Accuracy, and ROCAUC.
• Precision: It uses to measure of how many of the
predicted anomaly trajectories is correct (true anomaly
trajectories). A higher precision indicates fewer trajectories that are falsely identified as anomalies.
• Recall: It uses to measure the proportion of labels correctly identified. A higher recall indicates fewer false
negatives.
• F1-score: It is is the harmonic mean of precision and
recall, providing a balance between the two.
• Accuracy: It represents the ratio of correctly predicted
instances to the total number of instances in the dataset.
• ROCAUC The ROCAUC (Receiver Operating Characteristic/Area Under the Curve) plot visualizes the trade-off
between classifier sensitivity and specificity.
C. Baselines
In order to demonstrate the effectiveness of our proposed
model, we compare it with several existing methods for
trajectory anomaly detection.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
8

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

TABLE II
P ERFORMANCE C OMPARISON ON S HENZHEN AND C HENGDU DATASET

Fig. 4. The ROC curve in both shenzhen and chengdu dataset.

• TRAOD [18]: It employs a hybrid approach, combining
distance based and density based methods, within a partition and detect framework to identify trajectory outliers
by considering both spatial and temporal properties.
• IBOAT [13]: It is a trajectory outlier detection method
that utilizes an isolation based method for detection of
trajectory outliers in real time.
• STR [12]: It is a RNN based model that leverages spatialtemporal correlations for anomaly detection in trajectory
data.
• ATD-RNN [19]: It characterizes trajectories by learning
trajectory embeddings and then employs RNN based
model to capture temporal dependencies in trajectory data
for anomaly detection.
• GM-VSAE [25]: It is a VAE based model that employs
a Gaussian Mixture method to capture the multimodal
distribution of trajectory data for anomaly detection.
• DeepTEA [27]: It is a deep learning based method that
utilizes an attention mechanism with trajectory embedding to capture spatial-temporal features for anomaly
detection, with a focus on critical trajectory points.
• ATROM [42]: It based on spatio-temporal graph
convolutional adversarial network, which utilizes a

spatial-temporal graph to handle complex spatialtemporal dependencies and devises a spatio-temporal discriminator to determine whether a trajectory is anomaly
or not.
D. Performance
We evaluated the performance of our model, SSCTAD, and
compared it with several baseline models on two large-scale
real-world datasets: Shenzhen Taxi dataset and the Chengdu
DiDi dataset. The results are summarized in TABLE II,
highlight the best performance in bold and the second-best
in underlined.
In both Shenzhen and Chengdu datasets, our proposed
method achieves better results for detour anomaly detection.
This reflects the model’s ability to identify route deviations
caused by the driver’s behavior accurately. Compared to the
other methods, our method demonstrates a clear performance
margin.
For Unexpected Detour trajectories, SSCTAD also outperforms baselines. This type of trajectory is more challenging to
identify due to the fact that the route differs from the expected
route, but it has to be driven an extra distance to avoid traffic

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ZHANG et al.: SEMI-SUPERVISED CONTRASTIVE LEARNING FOR TRAJECTORY ANOMALY DETECTION

9

Fig. 5. The AUC performance of loss weights λ.

Fig. 7. The ablation study results on shenzhen and chengdu dataset.

Fig. 6. Detection time cost comparison.

congestion. Existing methods are struggling in this category,
which prefer to normalize such trajectories as anomalies.
The superiority of SSCTAD highlights the effectiveness of
integrating the in-out flow encoder into the learned latent
space, enabling better anomaly detection results. And for
identifying the normal trajectories, SSCTAD again delivers the
best overall performance.
These performance improvements are attributed to the
model’s combination of transformer-based trajectory encoder,
in-out flow encoder, and the semi-supervised contrastive learning. And by utilizing a small number of manually labeled
samples, our method achieve the better trajectory anomaly
detection results.
To further evaluate the discriminative capability of our
proposed method, we plotted the ROC curve and calculated
the Area Under the ROC Curve (AUC) for both the Shenzhen
and Chengdu datasets. As shown in Fig. 4, SSCTAD achieves
a higher AUC score than all baseline methods, which confirms
the superior performance of SSCTAD in identifying anomaly
trajectories.
Then, we also analyze the effect of loss weighting parameters during training process. As shown in Fig. 5, with the
weights increase, the performance improves, and the excessively large weights lead to a decline. So, we adopt the
balanced configuration and set λtg = λcl = λdis = 1.
To further evaluate the detection efficiency, we compared the
average detection time per trajectory with baseline methods.
For a fair comparison, all trained models were evaluated under
identical conditions. The detection time cost comparison as
shown in Fig. 6. Overall, the TROAD and iBOAT exhibit the
longest detection times, primarily because they extract normal
trajectories and compare target trajectories against these reference routes, which results in higher computational overhead.

Fig. 8. Visualization of trajectory latent representation in shenzhen.

Our proposed method maintains impressive efficiency, making
it well-suited for online anomaly trajectory detection scenarios.
Ablation Study: To better understand the contribution of
various components in our model, we designed two modified
versions: SSCTAD without the Contrastive Net (w/o CL)
and SSCTAD without the in-out flow encoder (w/o IOE).
As shown in Fig. 7, SSCTAD w/o IOE performs poorly
in identifying unexpected detour trajectories, indicating that
considering inflows and outflows in each area is crucial for
detecting such anomalies. The performance of SSCTAD w/o
CL is better than SSCTAD w/o IOE, but not as good as the
full SSCTAD model. Removing each component leads to a
performance degradation, suggesting that both the Contrastive
Net and the in-out flow encoder positively impact model
performance.
In the ablation study, we observed that the in-out flow
encoder is particularly critical for identifying unexpected
detour trajectories. This is because the encoder captures the
dynamic nature of traffic flow, allowing the model to recognize
deviations from typical patterns. And the Contrastive Net significantly enhances the model’s ability to differentiate between
normal and anomalous trajectories by learning more distinct
feature representations.
Interpretability Analysis: To analyze whether SSCTAD
can learn intuitive observations from an interpretable perspective, we visualized the distribution of the trajectory
latent representation using the t-SNE toolkit, comparing our
model and ATROM in Shenzhen over one day, as shown in

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
10

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

Fig. 9. Case study of shenzhen and chengdu. The green line represent normal trajectories. The red line represent detour anomaly trajectories. The blue line
represent unexpected detour trajectories.

Fig. 8. The results provide significant evidence that our model
effectively detects anomaly trajectories, including both detour
anomalies and unexpected detour trajectories.
Case Study
Detection of Anomalous Trajectories: In this case study,
we demonstrate the detection of anomalous trajectories across
various travel distances using our model in both Shenzhen
and Chengdu. Fig. 9 subfigures (a) to (d) depict data from a
single day in Shenzhen, and subfigures (e) to (h) show data
from one day in Chengdu. We detected detour trajectories
and unexpected detour trajectories without manually labeled
datasets using the trained model. The results are visualized
with red representing detour anomalies, blue for traffic congestion trajectories, and green for normal trajectories.
Distinguishing normal and traffic congestion trajectories: As shown in Fig. 9. Traditional methods often struggle to
discovery normal and traffic congestion trajectories. Our model
leverages the in-out flow graph to establish the spatio-temporal
relations between inflow and outflow across urban regions,
enabling effective detection traffic congestion trajectories.
As shown in Fig. 10, subfigure (a) presents an example of
traffic congestion trajectory detected during a morning peak
hour. Subfigure (b) compares the inflow to a designated red
region against its historical average. The data suggests that the
morning peak hour in the red area has shifted earlier, likely
due to traffic congestion in adjacent areas. This observation
supports the identification of trajectories as traffic congestion
trajectories.
Temporal Distribution Analysis: We further investigated
the temporal distribution of normal and traffic congestion

Fig. 10. An case study for our model in detecting traffic congestion
trajectories.

Fig. 11. Time distribution of normal trajectory and traffic congestion
trajectories.

trajectories identified by our model. As shown in Fig. 11, the
travel time distribution of these trajectories over a straightline distance of approximately 12 km in Shenzhen. Detection
becomes challenging for durations ranging from 1500 to

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
ZHANG et al.: SEMI-SUPERVISED CONTRASTIVE LEARNING FOR TRAJECTORY ANOMALY DETECTION

2000 seconds. Our model employs a transformer-based trajectory encoder and in-out flow encoder, combined with a
contrastive learning loss based on the Wasserstein metric, to
enhance anomaly detection accuracy.
In conclusion, our case study illustrates that SSCTAD
effectively identifies both normal and traffic congestion trajectories. By leveraging advanced spatio-temporal modeling
and visualization techniques, our model provides a robust
solution for detecting and interpreting anomalous trajectories
in urban environments. This capability is crucial for practical applications in urban traffic management, enabling more
informed decision-making and enhancing transportation safety
and efficiency.
VI. C ONCLUSION
In this study, we present SSCTAD, an effective and
efficient deep learning framework designed for detecting trajectory anomalies in urban environments. It utilizing trajectory
encoder, In-our flow encoder, trajectory generator and trained
with contrastive learning loss, thus excels in capturing the
inherent complexity of spatio-temporal data, while taking
into account the dynamic traffic state in urban environments.
The semi-supervised contrastive learning component further
enhances the model’s ability to distinguish between normal
trajectories, detours, and unexpected detours, especially under
conditions of limited labeling data. The experimental results
on large-scale real-world datasets from Shenzhen and Chengdu
demonstrate that our proposed method, SSCTAD, consistently
outperforms baselines model across all metrics, including precision, recall, F1-score, and accuracy. The case study further
demonstrates that our model can better detect normal, traffic
congestion, and detour anomaly trajectories.
In the future, we aim to enhance our model’s predictive
accuracy and perceptual capabilities by incorporating more
features, such as special events, so that our model can detect
the anomaly events. We will also incorporate an online detection module, enabling our proposed method achieve higher
accuracy anomaly trajectory detection in real-time. And we
also aim to extending our framework to explicitly handle
shared-trip scenarios. It will present a new challenge and
an interesting direction for future work, as the intentional
detour and intermediate stops cause the model to incorrectly
identify such trajectories as anomalies. Additionally, we plan
to transfer our framework to detect the anomalies behaviors in
maritime, such extensions will contribute to the development
of smart ocean system construction.
R EFERENCES
[1]
[2]
[3]

[4]

L. X. Pang, S. Chawla, W. Liu, and Y. Zheng, “On detection of emerging
anomalous traffic patterns using GPS data,” Data Knowl. Eng., vol. 87,
pp. 357–373, Sep. 2013.
Y. Zheng, L. Capra, O. Wolfson, and H. Yang, “Urban computing:
Concepts, methodologies, and applications,” ACM Trans. Intell. Syst.
Technol., vol. 5, no. 3, pp. 1–55, 2014.
Q. Chen, X. Song, H. Yamada, and R. Shibasaki, “Learning deep
representation from big and heterogeneous data for traffic accident
inference,” in Proc. AAAI Conf. Artif. Intell., 2016, vol. 30, no. 1,
pp. 1–7.
R. Jiang et al., “DeepCrowd: A deep model for large-scale citywide
crowd density and flow prediction,” IEEE Trans. Knowl. Data Eng.,
vol. 35, no. 1, pp. 276–290, Jan. 2023.

[5]

11

X. Zhang, Y. Zheng, Z. Zhao, Y. Liu, M. Blumenstein, and J. Li, “Deep
learning detection of anomalous patterns from bus trajectories for traffic
insight analysis,” Knowledge-Based Syst., vol. 217, Apr. 2021, Art. no.
106833.
[6] M. Zhang, T. Li, Y. Yu, Y. Li, P. Hui, and Y. Zheng, “Urban anomaly
analytics: Description, detection, and prediction,” IEEE Trans. Big Data,
vol. 8, no. 3, pp. 809–826, Jun. 2022.
[7] A. Belhadi, Y. Djenouri, J. C.-W. Lin, and A. Cano, “Trajectory outlier
detection: Algorithms, taxonomies, evaluation, and open challenges,”
ACM Trans. Manage. Inf. Syst., vol. 11, no. 3, pp. 1–29, Sep. 2020.
[8] R. Jiang et al., “DeepUrbanEvent: A system for predicting citywide
crowd dynamics at big events,” in Proc. 25th ACM SIGKDD Int. Conf.
Knowl. Discovery, Data Mining, Jul. 2019, pp. 2114–2122.
[9] Y. Zheng, “Trajectory data mining: An overview,” ACM Trans. Intell.
Syst. Technol., vol. 6, no. 3, pp. 1–41, 2015.
[10] S. Guo, J. Mou, L. Chen, and P. Chen, “An anomaly detection method
for AIS trajectory based on kinematic interpolation,” J. Mar. Sci. Eng.,
vol. 9, no. 6, p. 609, Jun. 2021.
[11] F. Ding, J. Wang, J. Ge, and W. Li, “Anomaly detection in largescale trajectories using hybrid grid-based hierarchical clustering,” Int.
J. Robot. Autom., vol. 33, no. 5, pp. 1–18, 2018.
[12] S. Qian et al., “Detecting taxi trajectory anomaly based on spatiotemporal relations,” IEEE Trans. Intell. Transp. Syst., vol. 23, no. 7,
pp. 6883–6894, Jul. 2022.
[13] C. Chen et al., “IBOAT: Isolation-based online anomalous trajectory
detection,” IEEE Trans. Intell. Transp. Syst., vol. 14, no. 2, pp. 806–818,
Jun. 2013.
[14] H. Zhang, Y. Luo, Q. Yu, L. Sun, X. Li, and Z. Sun, “A framework of
abnormal behavior detection and classification based on big trajectory
data for mobile networks,” Secur. Commun. Netw., vol. 2020, pp. 1–15,
Dec. 2020.
[15] A. Vahedian, X. Zhou, L. Tong, Y. Li, and J. Luo, “Forecasting gathering
events through continuous destination prediction on big trajectory data,”
in Proc. 25th ACM SIGSPATIAL Int. Conf. Adv. Geographic Inf. Syst.,
Nov. 2017, pp. 1–10.
[16] M.-H. Jeong, S.-B. Jeon, S. Park, and S. Kang, “Anomaly detection
in taxi flow by a projection method,” Sensors Mater., vol. 31, no. 11,
pp. 3827–3834, 2019.
[17] K. Choi, J. Yi, C. Park, and S. Yoon, “Deep learning for anomaly
detection in time-series data: Review, analysis, and guidelines,” IEEE
Access, vol. 9, pp. 120043–120065, 2021.
[18] J.-G. Lee, J. Han, and X. Li, “Trajectory outlier detection: A partitionand-detect framework,” in Proc. IEEE 24th Int. Conf. Data Eng., Apr.
2008, pp. 140–149.
[19] L. Song, R. Wang, D. Xiao, X. Han, Y. Cai, and C. Shi, “Anomalous
trajectory detection using recurrent neural network,” in Proc. Int. Conf.
Adv. Data Mining Appl. Cham, Switzerland: Springer, Nov. 2018,
pp. 263–277.
[20] H. Fan, F. Zhang, R. Wang, X. Huang, and Z. Li, “Semi-supervised
time series classification by temporal relation prediction,” in Proc.
IEEE Int. Conf. Acoust., Speech Signal Process. (ICASSP), Jun. 2021,
pp. 3545–3549.
[21] C. Wei, Z. Wang, J. Yuan, C. Li, and S. Chen, “Time-frequency based
multi-task learning for semi-supervised time series classification,” Inf.
Sci., vol. 619, pp. 762–780, Jan. 2023.
[22] A. Witayangkurn, T. Horanont, Y. Sekimoto, and R. Shibasaki,
“Anomalous event detection on large-scale GPS data from mobile
phones using hidden Markov model and cloud platform,” in Proc. ACM
Conf. Pervasive Ubiquitous Comput. Adjun. Publ., 2013, pp. 1219–1228.
[23] D. Zhang, N. Li, Z.-H. Zhou, C. Chen, L. Sun, and S. Li, “IBAT:
Detecting anomalous taxi trajectories from GPS traces,” in Proc. 13th
Int. Conf. Ubiquitous Comput., Sep. 2011, pp. 99–108.
[24] H. D. Trinh, L. Giupponi, and P. Dini, “Urban anomaly detection by
processing mobile traffic traces with LSTM neural networks,” in Proc.
16th Annu. IEEE Int. Conf. Sens., Commun., Netw. (SECON), Jun. 2019,
pp. 1–8.
[25] Y. Liu, K. Zhao, G. Cong, and Z. Bao, “Online anomalous trajectory
detection with deep generative sequence modeling,” in Proc. IEEE 36th
Int. Conf. Data Eng. (ICDE), Apr. 2020, pp. 949–960.
[26] L. Xie et al., “A novel model for ship trajectory anomaly detection
based on Gaussian mixture variational autoencoder,” IEEE Trans. Veh.
Technol., vol. 72, no. 11, pp. 13826–13835, Nov. 2023.
[27] X. Han, R. Cheng, C. Ma, and T. Grubenmann, “DeepTEA:
Effective and efficient online time-dependent trajectory outlier
detection,” Proc. VLDB Endowment, vol. 15, no. 7, pp. 1493–1505,
Mar. 2022.

This article has been accepted for inclusion in a future issue of this journal. Content is final as presented, with the exception of pagination.
12

IEEE TRANSACTIONS ON INTELLIGENT TRANSPORTATION SYSTEMS

[28] W. Yu and Q. Huang, “A deep encoder–decoder network for anomaly
detection in driving trajectory behavior under spatio-temporal context,”
Int. J. Appl. Earth Observ. Geoinformation, vol. 115, Dec. 2022, Art.
no. 103115.
[29] X. Zhu, Z. Ghahramani, and J. D. Lafferty, “Semi-supervised learning
using Gaussian fields and harmonic functions,” in Proc. 20th Int. Conf.
Mach. Learn. (ICML), 2003, pp. 912–919.
[30] R. R. Sillito and R. B. Fisher, “Semi-supervised learning for anomalous trajectory detection,” in Proc. Brit. Mach. Vis. Conf., 2008, pp.
1035–1044.
[31] Y. Liang et al., “TrajFormer: Efficient trajectory classification with
transformers,” in Proc. 31st ACM Int. Conf. Inf. Knowl. Manage., Oct.
2022, pp. 1229–1237.
[32] J. Zhang, Y. Zheng, and D. Qi, “Deep spatio-temporal residual networks
for citywide crowd flows prediction,” in Proc. AAAI Conf. Artif. Intell.,
Feb. 2017, vol. 31, no. 1, doi: 10.1609/aaai.v31i1.10735.
[33] J. Zhang, Y. Zheng, J. Sun, and D. Qi, “Flow prediction in spatiotemporal networks based on multitask deep learning,” IEEE Trans.
Knowl. Data Eng., vol. 32, no. 3, pp. 468–478, Mar. 2020.
[34] D. P. Kingma and M. Welling, “An introduction to variational autoencoders,” Found. Trends Mach. Learn., vol. 12, no. 4,
pp. 307–392, Nov. 2019.
[35] J. Bai, S. Kong, and C. P. Gomes, “Gaussian mixture variational
autoencoder with contrastive learning for multi-label classification,” in
Proc. Int. Conf. Mach. Learn., 2022, pp. 1383–1398.
[36] A. Mallasto and A. Feragen, “Learning from uncertain curves: The
2-Wasserstein metric for Gaussian processes,” in Proc. Adv. Neural Inf.
Process. Syst., vol. 30, J. Zhang, Y. Zheng, and D. Qi, Eds., Curran
Associates, 2017. [Online]. Available: https://proceedings.neurips.cc/
paper files/paper/2017/file/7a006957be65e608e863301eb98e1808Paper.pdf
[37] V. Masarotto, V. M. Panaretos, and Y. Zemel, “Procrustes metrics on
covariance operators and optimal transportation of Gaussian processes,”
Sankhya A, vol. 81, no. 1, pp. 172–213, Feb. 2019.
[38] P. Khosla et al., “Supervised contrastive learning,” in Proc. NIPS, 2020,
pp. 18661–18673.
[39] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,”
2014, arXiv:1412.6980.
[40] J. Lu, Y. Xu, H. Li, Z. Cheng, and Y. Niu, “PMAL: Open set recognition
via robust prototype mining,” in Proc. AAAI Conf. Artif. Intell., Jun.
2022, vol. 36, no. 2, pp. 1872–1880.
[41] Y. Zheng, M. Jin, Y. Liu, L. Chi, K. T. Phan, and Y. P. Chen, “Generative
and contrastive self-supervised learning for graph anomaly detection,”
IEEE Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12220–12233, Dec.
2021.
[42] Q. Gao, X. Wang, C. Liu, G. Trajcevski, L. Huang, and F. Zhou, “Open
anomalous trajectory recognition via probabilistic metric learning,” in
Proc. 32nd Int. Joint Conf. Artif. Intell., 2023, pp. 2095–2103.

Jiaqi Zhang is currently pursuing the Ph.D. degree
with the Department of Computer Science and
Engineering, Southern University of Science and
Technology (SUSTech), Shenzhen, China. His current research interests includes spatio-temporal data
mining, machine learning, and urban computing.

Zipei Fan received the B.S. degree in computer science from Beihang University, China, in 2012, and
the M.S. and Ph.D. degrees in civil engineering from
The University of Tokyo, Japan, in 2014 and 2017
respectively. He became a Project Researcher and a
Project Assistant Professor in 2017 and 2019, and
he promoted to a Project Lecturer with the Center
for Spatial Information Science, The University of
Tokyo, in 2020. He is currently a Professor with
the School of Artificial Intelligence, Jilin University.
His research interests include ubiquitous computing, machine learning, spatio-temporal data mining, and heterogeneous data
fusion.

Xuan Song received the Ph.D. degree in signal
and information processing from Peking University,
in 2010. In 2017, he was selected as an Excellent
Young Researcher of Japan MEXT. In the past ten
years, he led and participated in many important
projects as a Principal investigator or primary actor
in Japan, such as DIAS/GRENE Grant of MEXT,
Japan; Japan/U.S. Big Data and Disaster Project of
JST, Japan; Young Scientists Grant and Scientific
Research Grant of MEXT, Japan; Research Grant of
MLIT, Japan; CORE Project of Microsoft; Grant of
JR EAST Company; and Hitachi Company, Japan. He served as an Associate
Editor, a Guest Editor, the Area Chair, a Program Committee Member or a
reviewer for many famous journals and top-tier conferences, such as IMWUT,
IEEE T RANSACTIONS ON M ULTIMEDIA, WWW Journal, Big Data Journal,
ISTC, MIPR, ACM TIST, IEEE T RANSACTIONS ON K NOWLEDGE AND
DATA E NGINEERING, UbiComp, ICCV, CVPR, and ICRA.

Ryosuke Shibasaki received the B.S., M.S., and
Ph.D. degrees in civil engineering from The University of Tokyo, Japan, in 1980, 1982, and 1987,
respectively. From 1982 to 1988, he was with the
Public Works Research Institute, Ministry of Construction. From 1988 to 1991, he was an Associate
Professor with the Civil Engineering Department,
The University of Tokyo. In 1991, he joined the
Institute of Industrial Science, The University of
Tokyo. In 1998, he was promoted to a Professor
with the Center for Spatial Information Science, The
University of Tokyo. His research interests include cover three-dimensional
data acquisition for GIS, conceptual modeling for spatial objects, and agentbased microsimulation in a GIS environment.
PAPER_TEXT
