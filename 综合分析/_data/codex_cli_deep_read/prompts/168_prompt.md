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
# [168] Adaptive Working Condition Recognition With Clustering-Based Contrastive Learning for Unsupervised Anomaly Detection
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
编号：168
题名：Adaptive Working Condition Recognition With Clustering-Based Contrastive Learning for Unsupervised Anomaly Detection
年份：2024
DOI：10.1109/tii.2024.3413952
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2024.3413952.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测
相关性：弱相关，分数 3
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\168.txt
- 原始字符数：52229
- 本次发送字符数：52229
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

12103

Adaptive Working Condition Recognition With
Clustering-Based Contrastive Learning for
Unsupervised Anomaly Detection
Qifa Xu , Tianming Xie , Cuixia Jiang , Qiliang Cheng , and Xiangxiang Wang

Abstract—In real industrial processes, machines usually run under variable working conditions, which impose
challenges for anomaly detection. To complete anomaly
detection for machines under variable working conditions,
we develop a reconstruction-based autoencoder called
clustering-based contrastive learning autoencoder (CBCLAE). It integrates clustering-based contrastive learning
(CBCL) to perform clustering in the feature space and enhance the differentiation of features from different working
conditions, thereby achieving adaptive working condition
recognition. Considering the crucial role of the clustering of CBCL, we theoretically and experimentally demonstrate its convergence property during the training process,
which directly determines the effectiveness of CBCL-AE.
CBCL-AE’s superiority has been validated on three public
datasets and two private datasets collected from an actual industrial process. These validations highlight its superiority over five state-of-the-art models in unsupervised
anomaly detection.
Index Terms—Adaptive working condition recognition,
anomaly detection, clustering-based contrastive learning
(CBCL), multivariate time series (MTS), reconstructionbased autoencoder, variable working conditions.

I. INTRODUCTION
N THE era of Industry 4.0, the significance of anomaly
detection is growing exponentially across various industries, encompassing wind power, transportation, oil, natural
gas, aerospace, vehicles, etc. [1], [2]. As the earliest stage of
Prognostics Health Management, anomaly detection is capable

I

Manuscript received 4 November 2023; revised 14 April 2024 and 19
May 2024; accepted 2 June 2024. Date of publication 24 June 2024;
date of current version 7 October 2024. This work was supported by
the National Natural Science Foundation of PR China under Grant
72171070. Paper no. TII-23-4355. (Corresponding author: Tianming
Xie.)
Qifa Xu and Cuixia Jiang are with the School of Management, Hefei University of Technology, Hefei 230009, China (e-mail:
xuqifa@hfut.edu.cn; jiangcuixia@hfut.edu.cn).
Tianming Xie is with the School of Management, Hefei University of
Technology, Hefei 230009, China, and also with the Faculty of Engineering and Environment, Northumbria University, NE1 8ST Newcastle upon
Tyne, U.K. (e-mail: xietianming@mail.hfut.edu.cn).
Qiliang Cheng and Xiangxiang Wang are with RONDS Science and
Technology Incorporated Company, Hefei 230000, China (e-mail: qiliang.cheng@ronds.com.cn; xiangxiang.wang@ronds.com.cn).
Color versions of one or more figures in this article are available at
https://doi.org/10.1109/TII.2024.3413952.
Digital Object Identifier 10.1109/TII.2024.3413952

of promptly capturing abnormal behaviors during machine operations. This lays a crucial foundation for subsequent machine
fault diagnosis and repair processes. To date, there have been
numerous studies on anomaly detection using various types of
data, including images [3], videos [4], multivariate time series
(MTS) [5], and so on. In general, MTS can retain more information in the temporal dimension than in images and videos with
the same storage capacity. As a result, MTS anomaly detection
has been increasingly applied in various industrial production
environments as a cost-effective solution to reduce storage costs.
In real industrial processes, the existing anomaly detection
methods can be primarily grouped into three types: model-based,
signal-based, and knowledge-based methods. First, model-based
methods [6], [7], [8] leverage prior information from industrial processes or practical system models, enabling accurate
anomaly detection even with limited data. However, it is difficult to acquire accurate, comprehensive, and reliable models in
complicated industrial production environments. Moreover, the
system’s outputs are instability and may be influenced by various factors, such as environmental noise, machine lubrication,
and temperature, which reduce the efficiency of model-based
methods. Second, signal-based methods [9] extract features
from measured signals, then analyze symptoms and make diagnostic decisions based on prior knowledge of the system.
Owing to the rich information contained in time-domain and
frequency-domain signals, the performance of fault diagnosis
in motors [10] and rotary machines [11] can be improved.
For this reason, signal-based anomaly detection requires high
storage capacity to preserve more detailed information. Third,
the characteristic of knowledge-based methods is to extract
underlying knowledge from a large volume of historical data
using artificial intelligence techniques. The knowledge-based
method [12], [13], [14] is also referred to as a data-driven
method for its reliance on historical data for decision-making.
With the rapid progress in big data and computing capability,
knowledge-based methods that rely on artificial intelligence
models have gained significant attention as a popular research
area in recent years.
In industrial production environments, a machine anomaly is
a typical low-probability event and presents some characteristics, such as unpredictability, unknown patterns, and diversity.
Therefore, unsupervised data-driven methods are more suitable
for anomaly detection. In these methods, autoencoders [15]
are usually employed to construct reconstruction-based models,

1551-3203 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

12104

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

which aim at differentiating between abnormal and normal
behaviors by learning patterns or features from normal behaviors. Wulsin et al. [16] applied deep belief networks to construct
an encoding–decoding model, which utilizes reconstruction error to detect anomalies in clinical electroencephalography data.
However, without considering temporal dependencies, such
encoding–decoding models [17] and [18] are limited significantly in terms of accuracy in unsupervised anomaly detection.
To take temporal dependencies into account, many studies use
recurrent neural networks (RNNs) [5], [19], [20], including
traditional RNNs, long short-term memory (LSTM), and gate
recurrent unit (GRU), to construct autoencoder. These studies
have demonstrated that such models excel in reconstructing
MTS data. Indeed, in real-world data, it is common to encounter
various noises that can potentially decrease the robustness of
the model during the training process, even in normal data. To
address this issue, the authors in [5], [20], and [21] incorporated
variational inference [22] into the autoencoder. By introducing
variational inference, the autoencoder can represent features
in the form of distributions, reducing the impact of noises
at the tails of the distribution on the model significantly. In
recent years, the transformer has also been gradually introduced
into MTS anomaly detection since its powerful text processing
capability. Based on the characteristics of the transformer, Xu
et al. [23] constructed two types of associations: the association
between the current point and local context, as well as the
association between the current point and the global sequence.
As a result, the distinguishability between normal data and
anomalies has been successfully increased. The self-attention
mechanism in the transformer calculates temporal dependencies
with parallel matrix multiplication operations, which enables
the transformer to run much faster than RNNs with the same
number of parameters. However, this computational advantage
in terms of time is accompanied by an increased storage burden.
In addition to the methods mentioned previously, there are
also autoencoders built by integrating generative adversarial
networks [24] or combined with graph neural networks [25],
[26]. The former aims at enhancing the model’s generation or
data reconstruction capabilities, while the latter focuses on establishing better correlations among variables in high-dimensional
data. Current research on anomaly detection is primarily focused
on steady-state or single-machine scenarios. However, due to
the complex industrial processes, some machines often work
under variable conditions. In fact, for machines under variable
working conditions, having a large amount of data with such
different working conditions in the training set might enhance
the model’s ability to reconstruct genuine anomalies. Variable
working conditions lead to the characteristic of concept drift
in multisensor time series data, where the distribution, such as
mean and/or variance, of the MTS changes abruptly over time.
This makes it more difficult to identify true anomalies. Research
on anomaly detection specifically for machines under variable
working conditions is scarce, which remains a significant challenge within the industrial sector.
To this end, we develop a reconstruction-based autoencoder called clustering-based contrastive learning autoencoder
(CBCL-AE). It integrates clustering-based contrastive learning
(CBCL) to perform clustering in the feature space and enhance

the differentiation of features from different working conditions,
thereby achieving adaptive working condition recognition. The
contributions of this study can be summarized as follows.
1) We integrate CBCL into a specific autoencoder built with
GRU and realize end-to-end training. It can adaptively
group similar working condition data into the same category with the clustering method. By leveraging contrastive learning, the CBCL-AE model can effectively
improve the proximity of features from identical working conditions. It can also enhance the differentiation of
features from different working conditions by designing
a specific constraint to ensure a sufficient distance among
these features.
2) We conclude that the clustering process in the feature
space can converge by theoretically proving the model’s
convergence during the training process, as the clustering
process relies on model optimization. The proof of convergence of this clustering process provides theoretical
support for the effectiveness of the integrated CBCL module in CBCL-AE. By experimentally visualizing the trace
of cluster center iteration during the training process, we
further confirm the convergence of the clustering process.
3) We conduct experiments on three public datasets and two
private datasets. The comparison results on three public
datasets demonstrate that the CBCL-AE model achieves
acceptable results in general MTS anomaly when compared to five state-of-the-art models (SOTAs). The main
results on our private datasets show that our model is
superior to the five SOTAs in monitoring machines under
variable working conditions. In addition, the ablation
study proves the efficacy of integrating CBCL into our
model.
The rest of this article is organized as follows. Section II
introduces relevant theories and definitions. Section III details
the proposed CBCL-AE model. Section IV considers real-world
applications on three public datasets and two private datasets.
Finally, Section V concludes this article.
II. PRELIMINARIES
A. Reconstruction-Based Anomaly Detection
Due to the unpredictability, unknown patterns, and diversity
of anomalies in MTS, supervised methods are in general not
suitable for MTS anomaly detection. To this end, we develop
a reconstruction-based model using an autoencoder to realize unsupervised anomaly detection. Let us consider an MTS
X = [x1 , x2 , . . . , xt , . . . , xT ] with a length of T , where each
element xt ∈ Rm is an m-dimensional vector. Our goal is to
build a reconstruction-based model, denoted as f (.), which takes
X as inputs and produces X̂ as outputs. The model aims to
maximize the similarity between X and X̂. Consequently, the
residuals e = X − X̂ can be used to identify anomalies.
B. Contrastive Learning
The core idea of contrastive learning is to bring observations
from the same category closer together in the feature space, while
simultaneously increasing the separation between observations

XU et al.: ADAPTIVE WORKING CONDITION RECOGNITION WITH CBCL FOR UNSUPERVISED ANOMALY DETECTION

12105

to LSTM, GRU is capable of alleviating the issue of gradient
vanishing and has a simpler architecture. Therefore, we employ
GRU to construct the autoencoder. In Fig. 2, EU and DU denote
the encoder unit and the decoder unit that consist of GRU, which
are defined as
r t = σ(W rx xt + W rh ht−1 + br )
z t = σ(W zx xt + W zh ht−1 + bz )
h̃t = φ(W x xt + W rh (r t  ht ) + bh )

Fig. 1. Overall architecture of unsupervised anomaly detection based
on CBCL-AE.

from different categories. This can be achieved by minimizing
the distance between observations within the same category and
maximizing the distance between observations from different
categories. This nature of contrastive learning can help improve
the quality of feature representations.
Following Hadsell et al.’s [27] work, we introduce a traditional contrastive learning method with the objective function

LC (θ) =

N 


2
 
1 
(n)
(n)
, fθ X 2
yD fθ X 1
N n=1

 
 2 
 
(n)
(n)
,0
+(1−y)max λ−D fθ X 1 , fθ X 2


(1)
where N is the batch size, y indicates whether X 1 and X 2
belong to the same category, D(.) represents the distance calculation function, θ is the parameter set of the network fθ (.), and
λ is a tunable parameter to control the minimum distance that
should be maintained between different categories. In addition,
we will present the integration of CBCL into the model in
Section III-B.
III. CLUSTERING-BASED CONTRASTIVE LEARNING
AUTOENCODER
A. Overall Architecture
1) Scheme: Fig. 1 presents the overall architecture of unsupervised anomaly detection based on CBCL-AE. First, data
from sensors installed on different components of a pump under
variable working conditions are collected using edge computing
techniques. Second, the data are transmitted to both the clients
and servers of the diagnostic center, allowing access to historical
data for offline training of CBCL-AE. Third, thresholds for
different working conditions are selected. Finally, based on these
chosen thresholds and the trained model, anomalies in real-time
data can be effectively detected and the results are promptly
communicated back to the clients.
2) Architecture: Fig. 2 shows the architecture of the proposed
CBCL-AE model. It integrates the contrastive learning method
and requires that model’s inputs are a pair of observations. This
pair of observations is randomly sampled from the training set,
which means they could either come from the same working
condition or different working conditions. This pair of inputs, X
and X  , will be fed to an autoencoder built with RNN. Similar

ht = (1 − z t )  ht−1 + z t  ht

(2)

where r t and z t are the reset gate vector and update gate vector in
GRU, respectively; h̃t represents the candidate activation vector;
ht refers to the output vector of a GRU; xt is the input at time step
t, while W represents the weight vectors in GRU. In addition,
σ(.) denotes the sigmoid activation function and φ(.) is the tanh
activation function.
To construct the GRU autoencoder (GRU-AE), we adopt four
layers of GRU, with two layers employed for the encoder and
two layers for the decoder. The reconstruction process of the
GRU-AE can be presented as follows:


⎧
(l)
L
⎨EUl h(l−1)
,
h
t
t−1 , l ⩽ 2
(l)


(3)
ht =
⎩DUl h(l−1) , h(l) , L < l ⩽ L
t
t−1
2
(l)

where ht represents the hidden state of the lth layer; EUl (.)
denotes the encoder layer corresponding to the lth layer in
GRU-AE, and DUl (.) follows the same representation; Specific expression of EUl (.) and DUl (.) can be referred to the
calculation of ht in (2); L is the total number of layers in the
GRU-AE (L = 4 for the proposed model). In particular, when
(l−1)
in EUl (.) is actually the model’s input
L = 1, the input ht
xt ; when L = 4, the output hidden state ht is the reconstruction
x̂t . However, GRU-AE only possesses the ability to reconstruct
MTS and is unable to achieve adaptive condition recognition.
Therefore, we further introduce CBCL in GRU-AE.
B. Clustering-Based Contrastive Learning
Denote the hidden states of the pair of inputs X and X  ,

(2)
(2)
obtained by the encoder at time t, as ht , ht , which can also
be considered as the extracted features in the feature space. According to (1), the objective function of the contrastive learning
can be written as
N 

2

1 
(2)
(2)
LC (θ) =
yD htn , htn
N n=1


 2 

(2)
(2)
+ (1 − y) max λ − D htn , htn
.
,0
(4)
Since it is unknown whether X and X  belong to the same
working condition, i.e., y is unknown, we obtain y through a
k-means clustering algorithm of ht in a batch during the training
process.

12106

Fig. 2.

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

Architecture of CBCL-AE.

C. Loss Function

Algorithm 1: Iteration of CBCL.

The loss function of CBCL-AE can be defined as
L(θ) = (1 − α)Lmse (θ) + α(LC (θ) + L (θ))

(6)

where α serves as a tunable parameter that balances the tradeoff
between the two terms. The first term Lmse (θ) is an average
reconstruction loss of a pair of inputs with the form
N

Lmse (θ) =

1 
N n=1

(X − fθ (X))2 + (X  − fθ (X  ))
2

2

.
(7)

Assuming there are K working conditions in the data, during the ith batch iteration, we denote the converged cluster centers of this batch as Ci = {c1 , c2 , . . . , cK }. Let H =



(2)
(2)
(2)
(2)
(2)
(2)
{ht1 , ht1 , . . . , htn , htn , . . . , htN , htN } represent the set of
hidden states obtained after encoding in a batch. To make the
distribution of a batch closer to the overall distribution, we try
to make N as large as possible. This allows for more stable
(2)
cluster centers during the iteration. The distance between htn
(2)
and the kth cluster center can be defined as dk = D(htn , ck ).

(2)
Similarly, we can calculate the distance dk between htn and
ck . As a result, the distance sets can be represented as D =
(2)
{d1 , d2 , . . . , dK } and D = {d1 , d2 , . . . , dK }. Clusters that htn

(2)
and htn belong to can be determined as k ∗ = arg min(D) and

∗
k = arg min(D ), respectively. Finally, y in (4) can be defined
as
1, if k ∗ = k ∗
0, else.

k1 =1 k2 =1,k1 =k2

(8)
where γ is a tunable parameter that limits a minimum average
distance 
and can
be determined with a random search algorithm,
K
K
1
k1 =1
k2 =1,k1 =k2 D(ck1 , ck2 ) represents the average
K(K−1)
distance between all cluster centers, excluding the distance from
a cluster center to itself.
D. Convergence of Clustering Process



y=

The primary purpose of Lmse (θ) is to constrain the difference
between the input and the model’s reconstruction.
The second term contains two parts. The loss of contrastive
learning LC (θ) tends to improve the ability of feature extraction
by improving the proximity of features from identical working
conditions and enhancing the differentiation of features from
different working conditions. The constraint part L (θ) is used
to constrain the distance between cluster centers, ensuring that
there is sufficient differentiation in the feature space among
different working conditions. In this study, we define L (θ) as
⎛
⎞2
K
K


1
D(ck1 , ck2 ), 0⎠
L (θ) = max⎝γ −
K(K − 1)

(5)

We present the pseudocode for the iteration of CBCL during
the training process in Algorithm 1.

The convergence of the clustering process in the feature space
under different working conditions is very important for the
model’s performance. In general, the clustering process can
always reach convergence thanks to the nature of clustering

XU et al.: ADAPTIVE WORKING CONDITION RECOGNITION WITH CBCL FOR UNSUPERVISED ANOMALY DETECTION

algorithms. However, according to (4) and Algorithm 1, it can
be inferred that the cluster center iteration depends on the features obtained from the CBCL-AE model. For this reason, once
the features obtained from the model are unstable, it becomes
difficult for the clustering process to converge. Therefore, if the
convergence of the model during the training process does exist,
we infer that the CBCL-AE model can extract stable features.
Consequently, the iteration of cluster centers based on these
features will also converge.
For the theoretical proof of convergence, we need two assumptions. For two sets of parameters from the CBCL-AE model,
∀θ 1 , θ 2 , obtained from any two iterations during the training
process, they satisfy the following condition:
A1 :

θ 1 − θ 2 2 ⩽ d

(9)

where d represents the distance boundary between θ 1 and θ 2 .
Since θ 1 and θ 2 are obtained through the stochastic gradient
descent (SGD) algorithm, A1 holds for any differentiable function. Another assumption is the boundedness of gradients for any
iteration, ∀i, during the training process. For the ith iteration,
the gradient g i satisfies
A2 :

g i 2 ⩽ dg .

C(N ) =

N


(Li (θ i ) − L(θ ∗ ))

training process, we have
θ i+1 = θ i − ηi g i
⇒ θ i+1 − θ ∗ = θ i − θ ∗ − ηi g i
⇒ θ i+1 − θ ∗ 22 = θ i − θ ∗ − ηi g i 22
⇒ θ i+1 −θ ∗ 22 = θ i − θ ∗ 22 −2ηi g i , θ i − θ ∗ + ηi2 g i 22
 η
1 
i
θ i −θ ∗ 22 −θ i+1 −θ ∗ 22 + g i 22 .
⇒ g i , θ i −θ ∗ =
2ηi
2
(14)
Therefore, (13) can be further expressed as
C(N ) ⩽

According to the assumption (A2) on the boundedness of
gradients, the second term in (15) can be transformed into the
following inequality:
N

ηi
i=1

Li (θ i ) − Li (θ ∗ ) ⩽ g i , θ i − θ ∗ .

According to (11) and (12), we derive the following inequality:
C(N ) ⩽

N


gi , θi − θ∗ .

(13)

N

ηi d2g
i=1

=

N
d2g 
ηi .
2 i=1

(16)

1
1
θ 1 − θ ∗ 22 −
θ 2 − θ ∗ 22
2η1
2η1
+

1
1
θ 2 − θ ∗ 22 −
θ 3 − θ ∗ 22 + . . .
2η1
2η1

1
1
θ N − θ ∗ 22 −
θ N +1 − θ ∗ 22
2ηN
2ηN

N 

1
1
1
∗ 2
=
θ 1 − θ 2 +
−
θ i − θ ∗ 22
2η1
2η
2η
i
i−1
i=2
+

−

1
θ N +1 − θ ∗ 22 .
2ηN

(17)

Based on the assumption (A1) on the boundedness of parameters and the monotonically nonincreasing nature of the learning
rate η during the training process, we obtain the following three
inequalities:
1
1 2
θ 1 − θ ∗ 22 ⩽
d
(18)
2η1
2η1


N 
N 


1
1
1
1
∗ 2
2
−
−
θ i − θ 2 ⩽ d
2ηi
2ηi−1
2ηi
2ηi−1
i=2
i=2
(19)

i=1

Therefore,
our objective shifts to providing the boundedness

∗
of N
i=1 g i , θ i − θ . Based on the stochastic SGD used in the

2

=

N


1 
θ i − θ ∗ 22 − θ i+1 − θ ∗ 22
2ηi
i=1

(11)

(12)

2

g i 22 ⩽

For the first term in (15), we expand it and obtain

i=1

where θ i denotes the parameters of the CBCL-AE model from
the ith iteration during the training process, θ ∗ represents the parameters that optimizes the loss function L(.). When N → ∞, if
there exists C(N )/N → 0, it implies that Li (θ i ) is approaching
Li (θ ∗ ), indicating that the loss function L(.) converges during
)
= 0 serves as the
the training process. Therefore, limN →∞ C(N
N
criterion for determining the convergence of the loss function
L(.).
For L(.), in the local optimum region that can guarantee the
convexity, there exists

N
N
 

1 
ηi
θ i −θ ∗ 22 −θ i+1 −θ ∗ 22 +
g i 22 .
2η
2
i
i=1
i=1

(15)

(10)

In fact, for any trainable deep learning model, once a local
optimum exists during the training process, this local region
can satisfy the above-mentioned first assumptions. In addition,
we employ the gradient clipping, Xavier initialization, and batch
normalization methods during the training to ensure that the second assumption regarding the boundedness of gradients is satisfied. Intuitively, this local optimum region can also guarantee
the convexity of the loss function. We measure the convergence
by introducing the regret conception in Zinkevich’s [28] work
with the form

12107

−

1
θ N +1 − θ ∗ 22 ⩽ 0.
2ηN

(20)

12108

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

Algorithm 2: Training procedure of CBCL-AE.

Taken (17)–(20) together, we have
N


1 
θ i − θ ∗ 22 − θ i+1 − θ ∗ 22
2ηi
i=1

⩽


N 

1
1
1 2
d2
d + d2
−
.
+0=
2η1
2ηi
2ηi−1
2ηN
i=2

(21)

Finally, we derive
C(N ) ⩽

N
d2g 
d2
+
ηi .
2ηN
2 i=1

(22)

Since both d and ηi are constant, and ηi is monotonically
nonincreasing, we can conclude that regret C(N ) is bound.
)
= 0, L(.) converges during the
Therefore, as limN →∞ C(N
N
training process. In this case, the convergence of L(.) implies the
features obtained from CBCL-AE tend to be stable. Therefore,
we can conclude that the feature clustering process also converges. This convergence can also be empirically confirmed by
visualizing the trace of cluster center iteration in Section IV-C.
E. Optimization Procedure
Once the final loss function is determined, the SGD algorithm
is used to train the model by optimizing
θ ∗ = arg min((1 − α)Lmse (θ) + α(LC (θ) + L (θ))). (23)
θ

We present the detailed optimization procedure in Algorithm

datasets. The five SOTAs are Anomaly-Transformer [23], OmniAnomaly [20], long short-term memory variational autoencoder (LSTM-VAE) [21], encoder–decoder anomaly detection
(EncDec-AD) [19], and unsupervised anomaly detection model
(USAD) [29], respectively.
Among the above-mentioned SOTAs, Xu et al. [23] utilized
the encoder component from the transformer architecture to
build the Anomaly Transformer model, which utilizes a specific
association discrepancy constraint to enhance the model’s ability
to handle MTS. Su et al. [20] extended the GRU-VAE model by
incorporating temporal dependencies into the latent variables,
resulting in the creation of OmniAnomaly. Park et al. [21]
expanded upon the LSTM autoencoder with variational inference techniques to improve the robustness. EncDec-AD [19] is
an LSTM-based autoencoder, while USAD [29] integrates the
generative adversarial strategy into a traditional autoencoder.
2) Threshold Selection: After obtaining the reconstruction
results based on the CBCL-AE model, it is necessary to calculate the residuals, e = X − X̂, using the input data and the
reconstruction results. The calculated residuals can thus be used
to identify anomalies with a given threshold.
To ensure fairness, we employ the same threshold selection
strategy for all models. First of all, we generate a sufficient
number of thresholds within the range of residuals. Then, we
select a threshold that yields the optimal result for anomaly
detection. Considering the capability of CBCL-AE to adaptively
recognize working conditions, we select different thresholds
for different working conditions. In other words, the threshold
selection process will be repeated for each working condition.
In addition, we adopt the same anomaly detection rule for all
models. The rule is relatively simple: an anomaly is identified if
the residual value is greater than the threshold.
3) Evaluation Metrics: Due to the significant imbalance between normal data and anomalies, accuracy is not suitable for
evaluating the model performance. Therefore, we employ the
evaluation metrics, such as precision, recall, and F1-score, which
are defined as follows:
TP
TP+FP
TP
recall =
TP+FN
2 × Precision × Recall
F1-score =
Precision + Recall

precision =

(24)

where TP represents true positives, FP represents false positives,
and FN represents false negatives. Since the F1-score is the
harmonic mean of precision and recall, we concentrate on and
use it as the main evaluation metric.

2.
IV. EXPERIMENTAL DESIGN AND RESULTS
A. Experimental Design
1) Baseline Models: To validate the effectiveness of our
model, we compare the proposed CBCL-AE model with
five other SOTAs on three public datasets and two private

B. Experimental Results
1) Data: We consider three public datasets: Server machine
datasets (SMD) by Su et al. [20], Soil Moisture Active Passive (SMAP) satellite, and Curiosity Rover on Mars (MSL)
by citeRN22, as well as our two private datasets: Dataset of
multisensor on pump (MSPD) and dataset of multisensor on fan

XU et al.: ADAPTIVE WORKING CONDITION RECOGNITION WITH CBCL FOR UNSUPERVISED ANOMALY DETECTION

12109

TABLE I
DETAILED INFORMATION ON DATASETS

Fig. 4.

Data visualization of private datasets. (a) MSPD. (b) MSFD.
TABLE II
COMPARISON RESULTS ON THREE PUBLIC DATASETS

Fig. 3. Installation of sensors. (a) Sensors on a pump. (b) Sensors on
an induced draft fan.

(MSFD). These datasets detailed in Table I are used to demonstrate the superiority of CBCL-AE in unsupervised anomaly
detection. The three public datasets do not exhibit the nature of
variable working conditions and are considered as general MTS
in this study. They are used to demonstrate that CBCL-AE can
achieve satisfactory anomaly detection performance on general
MTS.
The MSPD and MSFD are both 3-D MTS data. The former
is collected from multiple sensors on a pump, and the latter
is from an induced draft fan. The three dimensions represent
the root-mean-square of velocity, the energy at the fundamental
frequency, and the energy at twice the fundamental frequency,
respectively. These three metrics are primarily used to detect
rotation anomalies in bearings, such as imbalance and misalignment. Here, the fundamental frequency indicates the rotational
frequency. The installation of multiple sensors on a machine
(e.g., pump, induced draft fan) is illustrated in Fig. 3. The
MSPD consists of a training set and a test set. The training
set comprises normal data from 40 pumps, while the test set
contains 1251 anomalies collected from 35 pumps. Similarly, the
training set of MSFD comprises normal data from ten induced
draft fans, while the test set contains 420 anomalies collected
from seven induced draft fans. In these two datasets, the time
interval between two consecutive data points is two hours in both
the training and test sets. The working condition is measured
by the three metrics mentioned previously. We visualize the
data collected from a specific pump and an induced draft fan
in Fig. 4, where three different working conditions are marked
with different colors. Obviously, the MTS evolves and presents

several abrupt changes in mean and variance values. This implies
that working conditions are not fixed but may change from one
to another, also called variable working conditions.
Since we have prior knowledge of the working condition
labels for machines on these two private datasets, this study has
three working conditions. Therefore, we fix this hyperparameter,
the number of clustering centers K, to three in the CBCL module for subsequent experiments. However, in general scenarios
where the number of working conditions is unknown, we should
treat K as a hyperparameter and select it through sensitivity
analysis.
The main difference between the three public datasets and
the two private datasets (e.g., the MSPD and MSFD) is that the
public datasets do not have the nature of variable conditions,
namely their distribution, including mean and variance, remains
relatively stable over time.
2) Comparison Results: To demonstrate that CBCL-AE has
satisfactory anomaly detection performance for general MTS,
we conduct experiments on three public datasets: SMD, MSL,
and SMAP. We compare it with the five SOTAs and report the
comparison results in Table II, with the average value across ten
repeated experiments.
Table II shows that although the CBCL-AE model does not
perform best among the five SOTAs on the three public datasets,
it still achieves the average level. As for the F1-score, we
can observe that the CBCL-AE model exhibits the fourth-best
performance on both SMD (F1-score=0.8445) and MSL (F1score=0.8255) while achieving only the fifth-best on SMAP
(F1-score=0.7295). Specifically, although the CBCL-AE model
ranks fourth in the F1-score on SMD and MSL, its performance
does not differ significantly from the models that are suboptimal
or third best. Therefore, we believe that the CBCL-AE model
achieves acceptable anomaly detection performance on the three
public datasets. We also find that the model GRU-AE, without
the CBCL module, maintains acceptable anomaly detection
results on those public datasets with the F1-scores of 0.8436,
0.7431, and 0.8276, respectively.

12110

Fig. 5.

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

Comparison results on the MSPD.
TABLE III
PAIRED T-TEST RESULTS ON TWO PRIVATE DATASETS

Since the three public datasets do not exhibit the typical nature
of variable working conditions, we further conduct experiments
on our private datasets: the MSPD and MSFD, to demonstrate
the advantages of CBCL-AE in handling data under variable
working conditions. We compare the CBCL-AE model with the
five SOTAs on these two private datasets and report the average
values with standard deviations across ten repeated experiments
in Fig. 5.
It is evident from Fig. 5 that the CBCL-AE model exhibits
remarkable superiority on the two private datasets over the
other SOTAs in terms of three key metrics: precision (0.951
and 0.8931), recall (0.9302 and 0.8425), and Fl-score (0.9407
and 0.8671). Moreover, the CBCL-AE model also exhibits stable
performance, as evidenced by its low standard deviations in these
two datasets. In addition, the GRU-AE model without the CBCL
module is far inferior to the CBCL-AE model. These comparison
and ablation study results strongly demonstrate the capability of
CBCL-AE in handling data under variable working conditions,
primarily attributed to the utilization of the CBCL module.
We further use the paired t-test to test whether the superiority
of the CBCL-AE model to the others is statistically significant.
The alternative hypothesis (H1) is that the CBCL-AE model is
superior to another in terms of greater F1-score, i.e., μ1 > μj
for j = 2, 3, . . . , 7. In this case, μi denotes the average F1-score
of model i(i = 1, 2, . . . , 7) across ten repetitions. We present
the test results in Table III and find that all tests are statistically significant at the 1% level. Thus, we conclude that the
CBCL-AE model significantly outperforms the other models in
unsupervised anomaly detection on two private datasets.
In summary, although the CBCL-AE model is not optimal
on the three public datasets, it delivers a satisfactory performance, indicating its acceptable anomaly detection capability
for general MTS. More important experiments on the MSPD and
MSFD illustrate the superiority of CBCL-AE and demonstrate
its unique capability to detect anomalies in MTS under variable
working conditions.

Fig. 6. Sensitivity analysis of α and λ. (a) Precision. (b) Recall.
(c) F1-score.

C. Model Discussion
Since the MSPD provides a more extensive amount of data
and shows more typical natures of variable working conditions
than the MSFD, we further discuss the model performance of
the MSPD by conducting sensitivity analysis, model complexity,
reconstruction evaluation, verification of the convergence of
the clustering process, and evaluation of the model’s ability to
recognize working conditions.
1) Sensitivity Analysis of Hyperparameters: In the loss function of CBCL-AE, we introduce the tunable hyperparameter
that balances the trade-off between two different losses, see (6).
In addition, hyperparameter λ in the contrastive learning loss
limits the minimum feature distance between the observations
from different working conditions, see (4). To demonstrate the
impact of these two hyperparameters on the CBCL-AE model,
we conduct a sensitivity analysis and visualize the results in
Fig. 6. We find that the CBCL-AE model achieves optimal
performance on all three metrics (precision, recall, F1-score)
when the hyperparameters are selected around α = 0.2 and
λ = 2. In particular, the model’s performance significantly deteriorates when α = 0 or α = 1. This is because the model does
not integrate the CBCL module when α = 0. In this case, the
model is unable to recognize working conditions adaptively. In
addition, when α = 1„ the model essentially removes the MSE
loss function, which affects its crucial reconstruction capability
and weakens its anomaly detection ability. According to the
sensitivity analysis, we adopt the hyperparameter combination
α = 0.2 and λ = 2 in our experiment.
2) Model Complexity: Since the CBCL-AE model integrates
the CBCL module; the increase in computational burden is
unavoidable. However, this module is just introduced during
the training to enlarge the difference between features across
different working conditions. Therefore, the additional computational burden of CBCL-AE mainly occurs during the training
phase. Once the model completes training, no extra computation
is required during the online anomaly detection. To show the
model complexity of CBCL-AE, we compare the memory usage,
training time for each batch, and testing time for each batch
on the MSPD against all comparison models. According to
Table IV, although the CBCL-AE model takes longer to train, it
ranks second in testing time among all models. This suggests that
the CBCL-AE model is well-suited for online real-time anomaly
detection.
3) Evaluation of Reconstruction: In the reconstruction-based
anomaly detection model, the quality of normal data reconstruction indicates their capability for learning the normal behavior of
the data. In other words, when a model effectively reconstructs

XU et al.: ADAPTIVE WORKING CONDITION RECOGNITION WITH CBCL FOR UNSUPERVISED ANOMALY DETECTION

12111

TABLE IV
COMPARISON OF MODEL COMPLEXITY

batch

batch

Fig. 9.

Fig. 7. Visualizations of data reconstruction. (a) Pump 1. (b) Pump 2.
(c) Pump 3. (d) Pump 4.

Fig. 8. Iterations of cluster centers. (a) Iterations of cluster centers of
CBCL-AE. (b) Iterations of cluster centers without L (θ). (c) Iterations of
cluster centers without CBCL.

normal data while having poor reconstruction quality for anomalies, it enables the differentiation between the reconstructions
and actual anomalies. This helps to improve anomaly detection
by leveraging such differentiation. To evaluate the reconstruction capability, we visualize the reconstruction results from the
CBCL-AE model in Fig. 7, where the highlighted red areas
represent anomalies. The reconstruction results indicate that the
CBCL-AE model has effectively learned the normal behavior
of the data. This is evident in Fig. 7, where normal data can
be effectively reconstructed, while anomalies are difficult to
reconstruct. This results in larger reconstruction residuals for
abnormal instances, enabling accurate anomaly detection.
4) Visualization of the Clustering Process: Since the CBCL
module is introduced into the CBCL-AE model, it is necessary to
verify the convergence of the clustering process during the training process. In addition to the theoretical proof in Section III-D,
we further confirm the convergence of the clustering process
by visualizing the trace of the cluster center iteration in Fig. 8,
where the X and Y coordinates represent two dimensions of the

t-SNE visualization of the feature space.

feature space. Specifically, Fig. 8(a) illustrates the trace of cluster
center iteration of CBCL-AE. We observe that the three clusters
with three different colors, representing three working conditions, gradually converge. Moreover, the final cluster centers
maintain sufficient distance from each other, indicating that the
clusters can be effectively distinguished. In Fig. 8(b), although
the iteration of final cluster centers also maintains convergence,
the absence of distance constraint, L (θ), leads to a lack of
differentiation among the converged centers. This is reflected in
the fact that the converged cluster centers are close to each other.
In addition, once removing the CBCL constraints in (6), Fig. 8(c)
shows that the clustering process is no longer converged. This
means that the model loses the capability to adaptively recognize
different working conditions.
5) Evaluation of Working Conditions Recognition: To evaluate the effect in adaptively recognizing variable working conditions, we present the t-SNE visualization in the feature space of
CBCL-AE in Fig. 9. The three colors represent three different
working condition features in the feature space. The cluster
centers of the three different working conditions are marked with
crosses. The visualization results show that the three working
conditions are well separated in the feature space and features
under the same working condition tend to cluster together.
This indicates that our proposed CBCL-AE model is indeed
capable of recognizing variable working conditions adaptively.
In addition, we also mark the features of some anomalies in the
feature space with red dots. It is obvious that the features of
these anomalies are mostly distributed in the feature space of
normal data. This means that the CBCL-AE model can capture
the characteristics of normal behavior effectively. This ability
is good for the model to reconstruct abnormal inputs as normal
ones, thereby amplifying the residual results of anomalies and
making them easier to detect.
6) Strengths and Weaknesses: The CBCL-AE model has
at least three strengths. First, it leverages the CBCL module to
adaptively cluster different working conditions and enlarge the
difference between features across these working conditions.
Second, it not only achieves satisfactory performance in general
MTS but, more importantly, performs excellently on MTS data

12112

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

with the typical nature of working conditions. Third, it can be
deployed in online anomaly detection without excessive computational resources. In addition, the CBCL-AE model also has two
weaknesses. Although it achieves satisfactory performance on
general MTS without the nature of variable working conditions,
such performance still has room for improvement compared to
the best SOTA. In addition, its training process requires more
computational resources compared to other models.
V. CONCLUSION
To achieve unsupervised anomaly detection for machines under variable working conditions, we propose a novel CBCL-AE.
This model integrates CBCL to cluster data in the feature space
and can effectively improve the proximity of features from
identical working conditions while enhancing the differentiation
of features from different working conditions. By leveraging
the CBCL, our proposed model can achieve adaptive working
condition recognition. Furthermore, a specific loss function is
designed for CBCL-AE to ensure its effectiveness. We theoretically prove the convergence property of the clustering process
of CBCL during the training process, which directly determines
the effectiveness of CBCL-AE.
Due to the absence of variable working conditions in the three
public datasets (SMD, SMAP, and MSL), our CBCL-AE model
achieves acceptable anomaly detection performance on general
MTS compared to the five SOTAs. Moreover, the experimental
results on the two private datasets, namely the MSPD and MSFD,
show that the CBCL-AE model performs best and even achieves
an impressive F1-score of up to 0.9407 on MSPD and 0.8671 on
MSFD, respectively. The ablation study strongly validates the
role of CBCL in improving the performance of the CBCL-AE
model. Visualizing the trace of cluster center iteration during
the training process further confirms the convergence of the
clustering process and demonstrates the effectiveness of CBCL
as well as the role of the loss L (θ). In addition, the t-SNE
visualization demonstrates that the CBCL-AE model has an
excellent capability of adaptive working conditions recognition
and learning normal behavior.
REFERENCES
[1] X. Dai and Z. Gao, “From model, signal to knowledge: A data-driven
perspective of fault detection and diagnosis,” IEEE Trans. Ind. Informat.,
vol. 9, no. 4, pp. 2226–2238, Nov. 2013.
[2] Z. Gao, C. Cecati, and S. X. Ding, “A survey of fault diagnosis and
fault-tolerant techniques–part I: Fault diagnosis with model-based and
signal-based approaches,” IEEE Trans. Ind. Electron., vol. 62, no. 6,
pp. 3757–3767, Jun. 2015.
[3] B. Su, Z. Zhou, and H. Chen, “PVEL-AD: A large-scale open-world dataset
for photovoltaic cell anomaly detection,” IEEE Trans. Ind. Informat.,
vol. 19, no. 1, pp. 404–413, Jan. 2023.
[4] X. Wang et al., “Robust unsupervised video anomaly detection by multipath frame prediction,” IEEE Trans. Neural Netw. Learn. Syst., vol. 33,
no. 6, pp. 2301–2312, Jun. 2022.
[5] X. Zhou, Y. Hu, W. Liang, J. Ma, and Q. Jin, “Variational LSTM enhanced
anomaly detection for industrial Big Data,” IEEE Trans. Ind. Informat.,
vol. 17, no. 5, pp. 3469–3477, May 2021.
[6] Z. Gao, “Fault estimation and fault-tolerant control for discrete-time dynamic systems,” IEEE Trans. Ind. Electron., vol. 62, no. 6, pp. 3874–3884,
Jun. 2015.

[7] Z. Gao, X. Liu, and M. Z. Q. Chen, “Unknown input observer-based
robust fault estimation for systems corrupted by partially decoupled disturbances,” IEEE Trans. Ind. Electron., vol. 63, no. 4, pp. 2537–2547,
Apr. 2016.
[8] Z. Gao, X. Shi, and S. X. Ding, “Fuzzy state/disturbance observer design
for T-s fuzzy systems with application to sensor fault estimation,” IEEE
Trans. Syst. Man Cybern., Part B, vol. 38, no. 3, pp. 875–880, Jun. 2008.
[9] E. Cabal-Yepez, A. G. Garcia-Ramirez, R. J. Romero-Troncoso, A. GarciaPerez, and R. A. Osornio-Rios, “Reconfigurable monitoring system for
time-frequency analysis on industrial equipment through STFT and DWT,”
IEEE Trans. Ind. Informat., vol. 9, no. 2, pp. 760–771, May 2013.
[10] C. Wu, C. Guo, Z. Xie, F. Ni, and H. Liu, “A signal-based fault detection
and tolerance control method of current sensor for PMSM drive,” IEEE
Trans. Ind. Electron., vol. 65, no. 12, pp. 9646–9657, Dec. 2018.
[11] Y. Zhu, G. Li, S. Tang, R. Wang, H. Su, and C. Wang, “Acoustic
signal-based fault detection of hydraulic piston pump using a particle
swarm optimization enhancement CNN,” Appl. Acoust., vol. 192, 2022,
Art. no. 108718.
[12] Z. Fan, Q. Xu, C. Jiang, and S. X. Ding, “Deep mixed domain generalization network for intelligent fault diagnosis under unseen conditions,”
IEEE Trans. Ind. Electron., vol. 71, no. 1, pp. 965–974, Jan. 2024.
[13] S. Lu, Z. Gao, Q. Xu, C. Jiang, A. Zhang, and X. Wang, “Class-imbalance
privacy-preserving federated learning for decentralized fault diagnosis
with biometric authentication,” IEEE Trans. Ind. Informat., vol. 18, no. 12,
pp. 9101–9111, Dec. 2022.
[14] T. Xie, Q. Xu, C. Jiang, S. Lu, and X. Wang, “The fault frequency
priors fusion deep learning framework with application to fault diagnosis of offshore wind turbines,” Renew. Energy, vol. 202, pp. 143–153,
2023.
[15] G. E. Hinton and R. R. Salakhutdinov, “Reducing the dimensionality
of data with neural networks,” Sci., vol. 313, no. 5786, pp. 504–507,
2006.
[16] D. F. Wulsin, J. R. Gupta, R. Mani, J. A. Blanco, and B. Litt, “Modeling
electroencephalography waveforms with semi-supervised deep belief nets:
Fast classification and anomaly measurement,” J. Neural Eng., vol. 8, no. 3,
2011, Art. no. 36015.
[17] G. Jiang, P. Xie, H. He, and J. Yan, “Wind turbine fault detection using
a denoising autoencoder with temporal information,” IEEE/ASME Trans.
Mechatron., vol. 23, no. 1, pp. 89–100, Feb. 2018.
[18] B. Zong et al., “Deep autoencoding Gaussian mixture model for unsupervised anomaly detection,” in Proc. Int. Conf. Learn. Representation, 2018.
[19] P. Malhotra, A. Ramakrishnan, G. Anand, L. Vig, P. Agarwal, and G.
Shroff, “LSTM-based encoder-decoder for multi-sensor anomaly detection,” 2016, arXiv:1607.00148.
[20] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Mining, 2019, pp. 2828–2837.
[21] D. Park, Y. Hoshi, and C. C. Kemp, “A multimodal anomaly detector
for robot-assisted feeding using an LSTM-based variational autoencoder,”
IEEE Robot. Automat. Lett., vol. 3, no. 3, pp. 1544–1551, Jul. 2018.
[22] D. P. Kingma and M. Welling, “Auto-encoding variational bayes,” in Proc.
Int. Conf. Learn. Representations, 2013.
[23] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time series
anomaly detection with association discrepancy,” in Proc. Int. Conf. Learn.
Representation, 2022.
[24] B. Du, X. Sun, J. Ye, K. Cheng, J. Wang, and L. Sun, “GAN-based anomaly
detection for multivariate time series using polluted training set,” IEEE
Trans. Knowl. Data. Eng., vol. 35, no. 12, pp. 12208–12219, Dec. 2023.
[25] Z. Chen, D. Chen, X. Zhang, Z. Yuan, and X. Cheng, “Learning graph
structures with transformer for multivariate time-series anomaly detection
in IoT,” IEEE Internet Things J., vol. 9, no. 12, pp. 9179–9189, Jun. 2022.
[26] C. Ding, S. Sun, and J. Zhao, “MST-GAT: A multimodal spatial-temporal
graph attention network for time series anomaly detection,” Inf. Fusion,
vol. 89, pp. 527–536, 2023.
[27] R. Hadsell, S. Chopra, and Y. LeCun, “Dimensionality reduction by
learning an invariant mapping,” in Proc. IEEE Conf. Comput. Vis. Pattern
Recognit., 2006, pp. 1735–1742.
[28] M. Zinkevich, “Online convex programming and generalized infinitesimal
gradient ascent,” in Proc. Int. Conf. Mach. Learn., 2003, pp. 928–936.
[29] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: Unsupervised anomaly detection on multivariate time series,” in
Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discov. Data Mining, 2020,
pp. 3395–3404.

XU et al.: ADAPTIVE WORKING CONDITION RECOGNITION WITH CBCL FOR UNSUPERVISED ANOMALY DETECTION

Qifa Xu received the B.E. degree in mathematics education from the Department of Mathematics, Fuyang Normal University, Fuyang,
China, in 1997, the M.S. degree in quantitative
economics from the Dongbei University of Finance and Economics, Dalian, China, in 2000,
and the Ph.D. degree in technical economics
and management from the School of Management, Tianjin University, China, in 2006.
He is currently a Professor with the School
of Management, Hefei University of Technology,
Hefei, China. His research interests include financial big data analysis,
statistical learning, and smart manufacturing.

Tianming Xie received the B.S. degree in
business management from the Hefei University of Technology, Hefei, China, in 2019. He
is currently working toward the Ph.D. degree
in management science and engineering with
the School of Management, Hefei University of
Technology.
His research interests include anomaly detection and fault diagnosis, and their applications in
industrial equipment, and renewable energy.

Cuixia Jiang received the B.E. degree in
mathematics education from the Department
of Mathematics, Fuyang Normal University,
Fuyang, China, in 1997, and the Ph.D. degree
in technical economics and management from
the School of Management, Tianjin University,
Tianjin, China, in 2008.
She is currently an Associated Professor with
the School of Management, Hefei University of
Technology, Hefei, China. Her research interests include financial big data analysis, financial
time series analysis, and statistical learning.

12113

Qiliang Cheng received the B.S. and M.S. degrees in business management from Hefei University of Technology, Hefei, China, in 2018 and
2022, respectively.
He is currently with the Intelligent Algorithm
Department, Anhui RONDS Science and Technology Incorporated Company, a company that
provides monitoring and maintenance solutions
and services for various industries. His research
focuses on bearing fault diagnosis.

Xiangxiang Wang is currently working toward
the Ph.D. degree in management science and
engineering with the School of Management,
Hefei University of Technology, Hefei, China.
She is the Deputy Minister of Anhui
RONDS Science and Technology Incorporated
Company. She has extensive experience in
diagnosing components, such as bearings
and gearboxes. Her research interests include
data-driven fault diagnosis and prognosis,
reliability engineering, and edge computing.
PAPER_TEXT
