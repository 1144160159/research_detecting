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
# [807] Sparse Gaussian–Markov Modeling for Robust and Trustworthy Unknown Cyber Defense
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
编号：807
题名：Sparse Gaussian–Markov Modeling for Robust and Trustworthy Unknown Cyber Defense
年份：2026
DOI：10.1109/tccn.2026.3668824
来源：IEEE Transactions on Cognitive Communications and Networking
PDF：paper/10.1109_TCCN.2026.3668824.pdf
已有粗分类：入侵检测与网络异常检测
二级关联：无
相关性：中相关，分数 6
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\807.txt
- 原始字符数：80130
- 本次发送字符数：80130
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
6524

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

Sparse Gaussian–Markov Modeling for Robust and
Trustworthy Unknown Cyber Defense
Chao Zha , Tian Liu, Chungang Lin , Bing Bai , and Ruyun Zhang

Abstract—Network intrusion detection systems (NIDS) are
essential for enhancing network security by detecting and
responding to attacks promptly. NIDS based on artificial
intelligence (AI) offer better adaptability to unknown (out-ofdistribution (OOD)) attacks compared to traditional anomaly
detection methods. However, many existing AI-based NIDS
directly adopt methods from other domains without adequately
considering OOD data, which often leads to severe overfitting in trained classifiers and insufficient model reliability and
robustness. This issue largely arises because most approaches
focus solely on the relationship between individual features and
predictions while neglecting the interactions among features,
resulting in overfitting and overconfident predictions. Moreover,
the retention of certain weak parameters may cause the model
to maintain artificially high confidence when confronted with
OOD data. To address this, we propose a Gaussian Markov
Random Field that better captures traffic data distribution and
feature correlations. Furthermore, our GMRF-based classification model uses sparsification with regularization L0 to remove
weak parameters. L0 regularization counts the number of nonzero parameters and penalizes model complexity, thereby forcing
insignificant weights to become exactly zero and improving
generalization. This prevents high prediction probabilities for
unknown attacks and effectively distinguishes them from benign
traffic. Finally, we evaluated our method in the CICIDS-2017
and CSE-CICIDS-2018 datasets, achieving recall rates of 57%
and 77% for unknown attacks while maintaining a recall of
more than 95% for known traffic. Our approach significantly
outperforms existing SOTA methods, and performance tests on
a low-specification machine show a low detection latency of
approximately 130 microseconds, making it suitable for real-time
applications.

Received 2 September 2025; revised 29 December 2025; accepted 23 February 2026. Date of publication 27 February 2026; date of current version
5 March 2026. This work is supported by the National Key Research
and Development Program of China (No. 2022YFB2900102) and the
Key Research and Development Program of Zhejiang Province (No.
2024SSYS0001). The associate editor coordinating the review of this article
and approving it for publication was G. Han. (Corresponding author: Ruyun
Zhang.)
Chao Zha is with the Institute of Computing Technology, Chinese Academy
of Sciences, Beijing 100190, China, also with the University of Chinese
Academy of Sciences, Beijing 100049, China, and also with the Research Center for High Efficiency Computing Infrastructure, Zhejiang Lab, Hangzhou,
Zhejiang 311121, China (e-mail: zhachao21@mails.ucas.ac.cn).
Tian Liu is with the Institute of Agricultural Equipment, Zhejiang Academy
of Agricultural Sciences, Hangzhou, Zhejiang 310021, China (e-mail:
liutian@zaas.ac.cn).
Chungang Lin is with the Institute of Computing Technology, Chinese
Academy of Sciences, Beijing 100190, China, and also with the University of Chinese Academy of Sciences, Beijing 100049, China (e-mail:
linchungang22s@ict.ac.cn).
Bing Bai and Ruyun Zhang are with the Research Center for High Efficiency Computing Infrastructure, Zhejiang Lab, Hangzhou, Zhejiang 311121,
China (e-mail: baibing@zhejianglab.org; zcor2021@gmail.com).
Digital Object Identifier 10.1109/TCCN.2026.3668824

Index Terms—Unknown attacks, out-of-distribution, intrusion
detection, GMRF, sparsification, real time.

I. I NTRODUCTION

T

HE rapid development of the Internet has led to an explosion of cyber attacks, resulting in significant information
and financial losses in critical sectors such as national defense,
power grids, transportation and healthcare systems. In this
context, NIDS have become essential components to ensure
the security of modern information infrastructures. Traditional
IDS approaches, which are based mainly on predefined rules
and signatures, such as deep packet inspection [1], [2], [3],
[4], [5], tend to be ineffective against previously unseen threats
[6], [7]. As a result, recent research efforts have increasingly
shifted toward AI-driven paradigms for intrusion detection [8],
[9], [10], [11].
A. Existing AI-Based Work
As AI technologies continue to achieve remarkable success
in various domains [12], [13], [14], their empowering role
in intrusion detection has become increasingly prominent.
Compared to traditional methods, AI-based approaches offer a
distinct advantage in identifying unknown threats - those that
lie beyond the distribution of in-distribution (ID) data [9], [15],
[16], [17], [18], [19], [20], [21], [22], [23], [24], [25], [26],
[27], [28], [29]. These emerging attack types often masquerade
as normal traffic, evading detection by intrusion detection
models, and thereby achieving malicious objectives. Existing
research on detecting such unknown threats falls mainly into
the following categories:
1) Unsupervised or Semi-Supervised Methods: In recent
years, some researchers have explored reconstruction-based
approaches to identify unknown threats [10], [15], [16], [17],
[18]. These methods can be broadly categorized into two types.
The first involves encoding ID data, often combined with
a classification head to optimize classification performance
and extract semantic representations of ID samples. This is
followed by a reconstruction phase using a decoder. The
second type trains directly an encoder-decoder framework to
reconstruct ID data. In both cases, the detection of unknown
threats is based on the reconstruction error: since out-ofdistribution (OOD) samples are not involved in training, they
typically exhibit higher reconstruction errors compared to ID
samples.
Although this approach has achieved notable success in
other domains, its direct application to the security domain
remains limited due to domain-specific challenges. First, the

2332-7731 © 2026 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

ZHA et al.: SPARSE GAUSSIAN–MARKOV MODELING FOR ROBUST AND TRUSTWORTHY UNKNOWN CYBER DEFENSE

data used for training in this context often consists of highly
sparse network flow features. This sparsity significantly undermines the effectiveness of cosine similarity (as we demonstrate
in Appendix A), which is commonly used as both an optimization objective and a detection metric. Second, due to the high
similarity between benign and malicious flows, and the lack
of genuine negative (malicious) samples during reconstruction
training, the reconstruction-based mechanism often struggles
to distinguish unknown threats effectively.
2) Supervised Methods: This category of methods uses
traditional machine learning (ML) algorithms, such as decision trees, random forests, and support vector machines, as
well as deep learning models, including multilayer perceptrons (MLPs), auto-encoders, stacked encoders, graph neural
networks, and transformers, to build intrusion classification
models using ID data [5], [20], [22], [24], [25], [30], [31],
[32], [33], [34]. In addition, strategies such as contrastive
learning and transfer learning have also been applied to NIDS
research [21], [35], [36]. Despite their success in classifying
known threats, these methods face two major limitations when
encountering unknown threats.
Firstly, existing machine learning applications in NIDS
often adopt standard algorithms directly without incorporating the specific context of cybersecurity. That is, they
typically overlook the joint effects among features, the semantic relationships between attributes, and their associations
with different types of attacks. This can lead to a high
risk of overfitting during training. Secondly, since models
are trained solely on ID data, they tend to learn superficial patterns of known traffic. Meanwhile, unknown threats
are often designed to closely mimic benign traffic [15],
[26], [37]. Although they fall outside the training distribution (i.e., they are OOD), they can still evade detection by
these classifiers, further exacerbating the overfitting issue and
undermining the model’s ability to generalize to novel attack
types.
B. Our Work
Our research is based on supervised learning methods and
proposes a novel intrusion detection system, named ZeroXpert,
which is specifically designed to enhance model reliability
while mitigating overfitting. ZeroXpert utilizes the Gaussian
Markov Random Field (GMRF) [38], [39] and sparsification
with regularization L0 , effectively captures spatial correlations between feature vectors, helping to reduce the risk of
overfitting the model. Additionally, by applying sparsification
to the model, we further decrease its dependence on weakly
correlated features, thereby lowering the prediction probability
when encountering unknown attacks. This approach enables
us to identify unknown attacks by setting a threshold on
the prediction probability. Finally, we conducted extensive
experiments on two public datasets, CICIDS-2017 [40], [41]
and CSE-CICIDS-2018 [41], [42]. Our method achieves recall
rates of 55% and 77% for unknown attacks while maintaining a recall of more than 95% for known attacks and low
false positive rates (around 2% and 4%) for benign traffic,
demonstrating strong practical applicability. Compared with
existing SOTA methods, ZeroXpert delivers superior performance across multiple metrics. In addition, detection latency

6525

tests show an average of about 130 microseconds, highlighting
its real-time capability.
In summary, our contributions to this article are as
follows:
• We propose a novel approach using a pre-trained GMRF
model for fine-grained classification of known data,
which captures feature interactions to reduce overfitting
and enhance robustness, improving detection of unseen
attacks.
• We introduce a L0 regularized parameter sparsification
method built on a pre-trained GMRF model. Reduces
reliance on weakly correlated features while preserving
accuracy, further enhancing robustness in distinguishing
unknown attacks through the prediction distribution.
• We evaluated our approach in the CICIDS-2017 and CSECICIDS-2018 datasets, achieving recall rates of 57%
and 77% for unknown attacks and more than 95% for
known traffic, surpassing several SOTA methods. On
low-spec hardware, the detection latency is around 130
microseconds, confirming real-time applicability.
The remainder of the paper is organized as follows. Section II introduces the background of GMRF. Section III
presents the detailed designs of our method. In Section IV
and Section V, we describe the implementation of GMRF
and sparsification, respectively. In Section VI, we experimentally evaluate the performance. Section VII reviews related
work. Section VIII discusses our proposed method and further
explores some potential future work directions. Finally, we
conclude this paper in Section IX.
II. BACKGROUND
In this section, we detail the theoretical foundations of the
Gaussian Markov Random Field [38], [39] to better address
the two challenges we face:
• We should consider the effect of feature interactions on
intrusion detection predictions.
• We need to minimize the impact of weakly correlated
features on the prediction results.
GMRF is a probabilistic graphical model that is used to
represent a set of random variables with Gaussian distributions, where the relationships between these variables satisfy
the Markov property. Specifically, given the neighborhood
of a random variable, the remaining variables are conditionally independent of the neighborhood of that random
variable. This Markov property can be represented by a graph,
where the edges indicate the conditional dependencies between
variables.
Assume that a random feature vector X is represented
as [x1 , x2 , x3 , . . . , xd ]. Its joint probability distribution P (X)
follows a multivariate Gaussian distribution, which can be
expressed as:


1
1
T −1
exp
−
(X
−
µ)
Σ
(X
−
µ)
,
P (X) =
d
1
2
(2π) 2 |Σ| 2
(1)
where µ is the mean vector, Σ is the covariance matrix, |Σ|
denotes the determinant of the covariance matrix.

6526

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

Since

1
d

1

(2π) 2 |Σ| 2

is the model parameter and is independent

of X, the probability distribution P (X) can be expressed as
follows:


1
P (X) ∝ exp − (X − µ)T Ω(X − µ)
2


1 T
T
∝ exp − (X Ω − µ Ω)(X − µ)
2


1
∝ exp − (X T ΩX − X T Ωµ − µT ΩX + µT Ωµ) ,
2
(2)
where Ω represents the precision matrix, Ω = Σ−1 .
Consider X and µ as a column vector of shape [d, 1]. Thus,
X T Ωµ = µT ΩX


1 T
T
T
P (X) ∝ exp − (X ΩX − 2µ ΩX + µ Ωµ) .
2

(3)

Similarly, µT Ωµ is independent of X, and Ω is a real
symmetric matrix, i.e. Ω = ΩT , then
µT ΩT = (Ωµ)T


1 T
T
P (X) ∝ exp − (X ΩX − 2(Ωµ) X) .
2

(4)

We analyze the density distribution of the flow features of
the network. Taking flow duration as an example, in reality,
most users’ network flows end in a short time, with fewer
users maintaining a long-duration network flow. After MinMax normalization, the flow duration value density distribution
approximates a normal distribution with a mean of 0. The
features we extracted include time-related and packet lengthrelated features, and our analysis shows that they conform to
these characteristics.
Furthermore, we visualize the data distribution (randomly
selecting six characteristics) in the CICIDS-2017 [40], [41]
and CSE-CICIDS-2018 [41], [42] datasets in Fig. 1, and the
results are consistent with our analysis. Based on the above
analysis, we can set µ in Eq. (4) to a zero vector; thus,


1 T
(5)
P (X) ∝ exp − (X ΩX)
2

 
λ11 , λ12 , . . . λ1d
x1
λ21 , λ22 , . . . λ2d  x2 

 
X T ΩX = [x1 , x2 , . . . , xd ] 
  .. 
..

 . 
.
λd1 , λd2 , . . . λdd
=

d X
d
X

xd

xi xj λij

i=1 j=1

=

d X
d
X

XX T

Ω,

(6)

i=1 j=1

where represents element-wise multiplication.
We can obtain the expected objective:



d X
d
X
1
XX T Ω .
P (X) ∝ exp − 
2 i=1 i=j

(7)

Ultimately, GMRF can be represented by a graphical model
that describes the joint probability distribution of the nodes in

Fig. 1. The density distribution of CICIDS-2017 and CSE-CICIDS-2018
datasets. The x-axis represents the feature value, while the y-axis indicates
the density, and darker colors correspond to higher density.

an undirected graph through cliques and potential functions.
In this graphical model, each variable is represented as a node,
and conditional independence relationships are represented as
undirected edges, forming an undirected graph. In this model,
cliques are fully connected subgraphs, and potential functions
define the joint distribution of these cliques, thereby capturing
dependencies between variables (as shown in Eq. (6), if
λij = 0, it indicates that there is no direct edge connecting
the two nodes, meaning that they are independent). These
potential functions allow the GMRF to flexibly represent
complex probability distributions, effectively capturing local
interactions and spatial dependencies.
Compared with traditional graph-based NIDS methods,
GMRF does not construct graphs based on IP nodes, but
instead models the relationships among features. Graph construction based on IP nodes faces a fundamental challenge:
when the number of IP nodes is large, the resulting graph
becomes extremely large, and the construction and computation overhead grow rapidly, making such models difficult
to deploy in practice. In contrast, GMRF builds the graph
over features, enabling the model to capture local interactions
and spatial dependencies among features, which contributes
to improved robustness. Traditional models tend to overfit
to a few dominant features, whereas GMRF emphasizes the
joint effects of multiple features, which is a key reason it
can effectively alleviate overfitting. Moreover, our approach
does not rely solely on GMRF. We aim to address these
issues through the combination of structural constraints and
parameter constraints. The former is imposed by GMRF-based
feature dependency modeling, while the latter is achieved
through parameter sparsification (pruning).

ZHA et al.: SPARSE GAUSSIAN–MARKOV MODELING FOR ROBUST AND TRUSTWORTHY UNKNOWN CYBER DEFENSE

III. OVERVIEW OF O UR M ETHOD
In this section, we develop a real-time NIDS, named ZeroXpert, aimed at accurately predicting known traffic patterns
while improving the detection capability for unknown attacks.

A. Design Philosophy
Unknown attacks may locally resemble benign traffic, making it easy to evade existing NIDS and be classified as benign
by current AI models with a high prediction probability. We
consider this phenomenon an issue of overconfidence in AI
models and attribute it to their neglect of extensive spatial
relationships between features, which refer to the combined
effects of multiple features on model predictions.
To solve the above issues, we propose using a GMRF
to learn the distribution of traffic features, with the aim
of strengthening the learning of spatial relationships among
feature vectors. Additionally, by sparsifying the model parameters, we further eliminate features weakly related to the
prediction results, thereby reducing the model’s overconfidence in predictions.
Specifically, we use P (X; Ω) to denote the probability
distribution of GMRF based on the feature data X, and
P (Y |X; Ω) to represent the maximum predict probability
based on P (X; Ω), Ω represents the parameters of the model,
Y labels the feature data X. If P (Y |X; Ω) → 1.0, X is
identified as the label Y ; conversely, if P (Y |X; Ω) → 0.0, it is
not identified as such. P (Y |X; Ω) can be considered a general
form of a ML model for intrusion detection, which poses
little problem when only considering the closed set scenario.
However, in practical research, we found that when the model
receives unknown feature data XU , the predicted probability
P (Y |XU ; Ω) often approaches the larger probability, which
means that it is identified as a known type. If an unknown
attack is identified as a known attack, the harm is relatively
minor but still detrimental to our defense analysis work; if it
is identified as benign traffic, the damage can be enormous
and immeasurable.
We decompose the model overconfidence problem into two
stages. In the first stage, we build a multiclass classification
model based on the known traffic space (including benign
traffic and known attack traffic) and optimize it by minimizing
its empirical risk. The specific process can be expressed as
follows.
!
N
1 X
L (P (Yi |Xi ; Ω), Yi ) ,
(8)
R1 (Ω) =
N i=1
where N denotes the number of sample pairs, L (·) corresponds to a loss function, e.g., cross-entropy loss for
classification.
Clearly, the first stage aims to learn the probability distribution of the GMRF for the characteristic vector X and perform
classification tasks within the known space. To further eliminate the impact of weakly correlated features on the prediction
results and improve the confidence of the model, we perform
parameter sparsification with L0 regularization in the second
stage inspired by [43]. This is achieved by retraining based
on the pre-trained model from the first stage. Specifically, we

6527

consider the regularized empirical risk minimization process
with regularization L0 on spurious parameters:
!
N
1 X
R2 (Ω) =
L (P (Yi |Xi ; Ω), Yi ) + λkΩk0 ,
N i=1
kΩk0 =

|Ω|
X

I[Ωj 6= 0],

(9)

j=1

where |Ω| represents the number of parameters, λ is a weighting factor for the regularization of L0 .
We reduce the prediction probability of the model when
encountering unknown attack data in the second stage.
Subsequently, by setting a minimum prediction probability
threshold, we will distinguish unknown attack types.
B. Practical Solution
To achieve the objectives outlined in Eq. (8) and Eq. (9),
we decompose the task into three modules as shown in Fig. 2,
specifically: Pre-Processing, GMRF, and Sparsification.
1) Pre-Processing: We use CICFlowMeter [44] to parse the
raw data, extracting more than 80 features related to network
flows. We remove all discrete features (as the experiments
showed that they had no impact on model results) and remove
a small number of continuous features with many outliers.
Ultimately, we applied the Min-Max Scaler [45] to the feature
data.
a) GMRF: According to Eq. (7), we calculate XX T , the
covariance matrix, which served as input to the model. Then,
we model GMRF using a convolutional network [46] and an
attention network [47]. The convolutional network is used to
implement a Patch Embedding, sampling the relational subgraphs (clusters) within the traffic feature space. The attention
network is used to learn the edge potential functions. Through
these two components, we can realize the GMRF. Additionally,
we add a fully connected layer after the GMRF to guide its
learning according to Eq. (8) and Eq. (9). Details of GMRF
are provided in Section IV.
2) Sparsification: To better address the issue of model
overconfidence, we employ a sparsification method with L0
regularization [43] for the over-parameterized model to retrain
the pre-trained model from the first stage. The calibrated
prediction probability distribution of the retrained model can
more effectively distinguish unknown attacks. Details of Sparsification are provided in Section V.
In general, the workflow in the training phase is as follows.
Firstly, the traffic data are processed by the Pre-Processing
module and normalized into one-dimensional feature vectors.
These vectors are then transformed into covariance matrices
according to Eq. (7) and fed into the GMRF module, where
the first training stage is performed using the optimization
objective defined in Eq. (8). This stage enables the model
to achieve strong detection performance within the known
traffic space, although it may also lead to overconfidence
when encountering unknown attack traffic. The model then
undergoes a second training stage with the Sparsification
module, whose optimization objective as described in Eq. (9).
This step reduces the parameters that contribute to model
overconfidence while offering limited practical value, thus
improving the reliability of the final model decisions. In

6528

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

Fig. 2. The overview of our method. It consists of three main modules: Pre-Processing, GMRF, Sparsification. Pre-Processing involves extracting feature
information from the network flow and computing its covariance matrix for model input. GMRF includes a Patch Embedding layer and a shallow Attention
Block. Patch Embedding layer flattens the covariance matrix to meet the input requirements of the attention mechanism, while the Attention Block performs
feature extraction to accomplish the classification task. After Pre-Processing, we optimize the model using a Sparsification module to remove learning related
to weakly relevant features, thereby reducing the model’s overconfident predictions.

the inference phase, the workflow only requires the PreProcessing module and the GMRF model. Compared with
traditional AI-based classification models, ZeroXpert differs
in that it determines whether a sample corresponds to an
unknown attack based on the output probability distribution
of the model.
IV. GMRF
In this section, we provide a detailed explanation of the
implementation of the GMRF model. It mainly consists of a
Patch Embedding layer and an Encoder layer, which respectively implement the clusters and edge potential functions in
the GMRF.

B. Encoder
The attention mechanism [47] is widely used in tasks
such as natural language processing and computer vision,
demonstrating strong performance. We utilize an encoder
composed of blocks of the attention mechanism to model the
edge potential functions in GMRF, aiming to extract spatial
relationships between the feature subgraphs. Considering the
need for real-time performance in network intrusion detection
systems, we employ a shallow neural network to achieve
this functionality and remove the residual structure from
the attention mechanism blocks. Modified blocks include an
attention layer, a feedforward neural network, and two layers
of layer normalization [48], as specified below:
0

0

Xmha =M HA(Xtrans , Xtrans , Xtrans ), Xmha ∈ R(d ×d )×C ,
0

0

A. Patch Embedding

Xln = LayerN (Xmha ), Xmha ∈ R(d ×d )×C ,

Assuming that the input covariance matrix is Xcov ∈
R
, we perform a 3 ∗ 3 convolution on it. This operation can extract spatial correlation information within partial
feature subgraphs of the matrix, thus capturing the cluster
structure of the GMRF model described in Eq. (7). Specifically, it can be expressed as follows.

Xf f n = F F N (Xln ), Xf f n ∈ R(d ×d )×C ,

1×d×d

0

0

Xconv = Conv2D(Xcov , k = 3), Xconv ∈ RC×d ×d , (10)
where C denotes the output channels of Conv2D.
Then, to meet the input shape requirements of the attention
mechanism (Encoder), we flatten the last two dimensions of
Xconv , followed by a matrix transpose. This is expressed as
follows:
C×(d0 ×d0 )

Xf la = F latten(Xconv , −1, −2), Xf al ∈ R
Xtrans = XfTla ,

(d0 ×d0 )×C

Xtrans ∈ R

where F latten(·) refers to Flatten.

,

,

(11)

0

0

0

0

Xout = F latten(LayerN (Xf f n )), Xout ∈ R(d ×d ×C) ,
(12)
where M HA(·) denotes Multi Head Attention mechanism,
LayerN (·) represents Layer Normalization, F F N (·) stands
for FeedForward Neural Network.
After the encoding layer, we add a fully connected layer
to output the predicted probabilities and perform empirical
risk minimization according to Eq. (8) and Eq. (9) during two
different training stages.
V. S PARSIFICATION
To further optimize the objective in Eq. (9), due to the nondifferentiability and combinatorial nature (2|θ| possible states)
of the parameter vector θ, optimizing under this penalty is
computationally infeasible. How can we relax the discreteness

ZHA et al.: SPARSE GAUSSIAN–MARKOV MODELING FOR ROBUST AND TRUSTWORTHY UNKNOWN CYBER DEFENSE

6529

TABLE I
E XPLANATION OF ATTACK T YPES IN THE DATASET

of the L0 penalty to allow efficient continuous optimization of
Eq. (9) while still permitting exact zeros in the parameters?
Following [43], we introduce a binary gate zj to indicate
whether a parameter exists, where the L0 regularization represents the number of open gates.
e j zj , zj ∈ {0, 1}, Ω
e j 6= 0, kΩk0 =
Ωj = Ω

|Ω|
X

zj .

(13)

j=1

Letting each gate follow a Bernoulli distribution q(zj |πj ) =
Bern(πj ), we can reformulate Eq. (9), as follows:
!
|Ω|
N

X
1 X 
e
e
L P (Yi |Xi ; Ω z), Yi
+λ
πj
R2 (Ω, π) =
N i=1
j=1
= LE + λLC ,

(14)

where denotes the product in elemental terms.
Due to the discrete nature of z, it is challenging to optimize
Eq. (14) using gradient-based methods. Using a uniform
distribution u and a binary concrete random variable s which
is distributed in the interval (0, 1), we can reparameterize
(“smooth”) z in Eq. (14) as follows:
u ∼ U(0, 1),
s = Sigmoid ((log(u) − log(1 − u) + log(α))/β) ,
se = s(ζ − γ) + γ,
z = min (1, max(0, se)) ,
(15)
where α denotes location and β represents temperature, (ζ >
1, γ < 0) are constants to stretch the distribution interval of
s.
Consequently, the L0 complexity loss LC of the objective
in Eq. (14) can be expressed as:



|Ω|
X
−γ
.
(16)
LC =
Sigmoid log(αj ) − β log
ζ
j=1
VI. E XPERIMENTAL E VALUATION
A. Experiment Setup
1) Implementation: We developed the ZeroXpert prototype
using Python 3.8.12, and the other modules are built using
scikit-learn [49] and PyTorch (2.0.1+cu117) [50].

2) Implementation: The system is deployed on a Supermicro server with an 80-core Intel(R) Xeon(R) Gold 6138
CPU, 1 NVIDIA A100-PCIE-40GB, Ubuntu 22.04.4 LTS and
64GB of DRAM (details of our implementation can be found
in Appendix B).
3) Datasets: We used two publicly available datasets,
CICIDS-2017 [40], [41] and CSE-CICIDS-2018 [41], [42], to
evaluate the performance of ZeroXpert. Both datasets contain
benign traffic and up-to-date samples of common attacks,
with data characteristics that closely resemble real-world data
(such as in PCAP format). The CICIDS-2017 dataset includes
common attack types based on the 2016 McAfee report,
such as Web attacks, brute force, DoS, DDoS, Infiltration,
Heartbleed vulnerabilities, Botnet and scanning attacks, and
the CSE-CICIDS-2018 dataset covers various attack types
including brute force, heartbleed, botnet, DoS, DDoS, Web
attacks, and internal network penetration. The explanations of
the attack abbreviations are provided in Table I.
We used CICFlowMeter [44] to extract network flow features, resulting in more than 80 features. Network flow features
are typically indexed using five tuples (source IP, source port,
destination IP, destination port, protocol), extracting protocolrelated, packet length-related, and time-related features. These
flow features can be analyzed without accessing the plaintext
content of the packets, making them particularly suitable
for encrypted traffic scenarios. Since there is no need to
decrypt the traffic, using flow features for detection effectively
protects user privacy. Calculating flow features is generally
more efficient than content analysis, enabling more real-time
intrusion detection. We partition attacks in both datasets into
known and unknown categories: benign traffic and known
attack data are used for model training, while unknown attack
data are excluded from the training process. For known traffic,
the data set is randomly divided into the training set and the
test set with a 7:3 ratio, and the partitioning and size of the
data set are summarized in Table II. Furthermore, considering
the size of the data set and the need to reduce computational
costs, we performed random sampling on the experimental
data set.
4) Baselines: We used three state-of-the-art unknown
attack detection methods and one traditional machine learningbased method as baselines.

6530

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

TABLE II

TABLE III

PARTITION OF K NOWN T RAFFIC & U NKNOWN ATTACKS

FPR (B ENIGN ) ON CICIDS-2017 AND CSE-CICIDS-2018 DATASET

B. Accuracy Evaluation

• Binary-Cls (machine learning based method). We implemented a method based on a combination of random
forest [51] and one-class SVM [52], where random
forest is used for binary classification between benign
and known attacks, while one-class SVM distinguishes
between known and unknown attacks.
• Kitsune@NDSS
(reconstruction
based
method).
Mirsky et al. [18] employed a stacked auto-encoder
neural network to jointly differentiate between benign
and malicious traffic patterns.
• MTH-IDS@IoTJ (signature- or anomaly-based method).
Yang et al. [26] proposed using a clustering label (CL)
k-means model as the initial layer to detect unknown
threats. In the second layer of unknown threat detection,
they incorporated Bayesian optimization with Gaussian
processes and two biased classifiers to optimize the model
and reduce the classification errors of the CL-k model.
• CVAE-EVT@TIFS
(reconstruction-based
method).
Yang et al. [15] investigated the reconstruction error
between the generated instances, conditioned on labels
predicted by a probabilistic discriminative model (known
attack detector) and the input instances by training a
generative model. They then combined this approach
with extreme value theory to detect unknown attacks.
• CADE@Security (machine learning based method).
Yang et al. [53] proposed a contrastive learning–based
approach that models the distributions of different attack
families in the latent space. Using the distance to cluster
centroids together with robust statistics, the method can
detect distributional drifts and identify zero-day attacks.
5) Metrics: We validated the prototype using precision,
recall, F1 score, and false positive rate (FPR), as these are
widely used in the literature [15], [26].
6) Hyper-Parameter Selection: Our PatchEmbedding utilizes a 3×3 convolutional kernel with 1 input channel, 8 output
channels, and a padding of 1. In the encoder, we implemented
1 Attention Block configured with 4 heads and a dropout rate
of 0.5.

Fig. 3 summarizes the detection performance of ZeroXpert
and presents the results of related ablation experiments. Our
ablation study is conducted by sequentially removing the
GMRF component and the sparsification process to evaluate
their impact. Our evaluation focuses on unknown attacks,
and we paid particular attention to the rate of benign traffic
misclassified as attack traffic.
1) Detection Performance of ZeroXpert: First, we evaluated
the recall performance of ZeroXpert on two different datasets.
As shown in Fig. 3b, in the CICIDS-2017 data set, ZeroXpert demonstrates excellent recall rates for all known traffic
(benign + known attacks), with all attack types exceeding
99% recall, except for the DoS Slowloris attack, which has a
recall rate of 82%. Furthermore, the system achieves a recall
rate of approximately 57% for unknown attacks. Similarly,
as illustrated in Fig. 3e, ZeroXpert also achieves outstanding
recall rates on the CSE-CICIDS-2018 dataset, with results
ranging from 95% to 99% for known traffic and around 78%
for unknown attacks.
Second, we assessed the precision performance of ZeroXpert on two different datasets. As illustrated in Fig. 3a,
ZeroXpert achieves a detection precision between 90% and
99% in the CICIDS-2017 dataset, demonstrating excellent
performance. Similarly, as shown in Fig. 3d, ZeroXpert performs well in the CSE-CICIDS-2018 data set, with detection
precision ranging from 95% to 99% for all types of attacks
except benign traffic. Given that attack traffic can be mistaken
for benign traffic and that some false positives are inevitable, it
is understandable that the precision for detecting benign traffic
is slightly lower. The precision in attack traffic detection is
a crucial metric in intrusion detection, reflecting the extent
to which the model misclassifies attacks. Higher precision
indicates fewer benign traffic instances misclassified as attacks.
From an impact perspective, a large number of benign traffic
misclassified as attacks is particularly problematic, as it could
severely disrupt user services.
Third, we evaluated the F1-Score performance of ZeroXpert
on two different datasets. As shown in Fig. 3c, ZeroXpert
achieves excellent F1 scores in the CICIDS-2017 data set, with
all types except for unknown attacks scoring between 90%
and 99%. The F1 score for unknown attacks is approximately
70%. Similarly, Fig. 3f illustrates that ZeroXpert performs
exceptionally well on the CSE-CICIDS-2018 dataset, with F1
scores exceeding 90% for most types and the F1 score for
unknown attacks around 86%. It should be noted that unknown
attack data were not included in model training, and achieving
such high performance for unknown attack detection without
affecting the detection results for known traffic is particularly
impressive.
In real-world deployment scenarios, the FPR in benign
traffic is a crucial indicator of the practicality of an NIDS.

ZHA et al.: SPARSE GAUSSIAN–MARKOV MODELING FOR ROBUST AND TRUSTWORTHY UNKNOWN CYBER DEFENSE

6531

Fig. 3. Performance evaluation of ZeroXpert on different attack types in the CICIDS-2017 and CSE-CICIDS-2018 datasets, along with ablation study results.
The abbreviations in the figure are defined as follows: B.N. refers to Benign, F.P. refers to FTP-Patator, S.P. refers to SSH-Patator, D.G. refers to DoSGoldeneye, D.S. refers to DoS-Slowloris, D.T. refers to DoS-Slowhttptest, D.H. refers to DoS-Hulk, D.D. refers to DDoS, P.S. refers to Portscan, D.C. refers
to DDoS-HOIC, D.L. refers to DDoS-LOIC-HTTP, U.K. refers to Unknown attacks.

An excessively high FPR can cause a significant amount of
benign traffic to be incorrectly flagged as malicious, potentially disrupting legitimate operations and compromising the
usability and stability of the system. As presented in Table III,
our method achieved a test FPR of 1.02% in the CICIDS-2017
data set prior to the sparsity pruning process. After pruning and
subsequent reconstruction-based retraining, the FPR increased
slightly to 1.97%. Similarly, in the CICIDS-2018 dataset, the
FPR rose from 1.19% before pruning to 4.91% after pruning.
Although the pruning stage led to a moderate increase in FPR,
the overall values remained within an acceptable and practical
range for deployment.
2) Visual Analysis of Results: We conducted a visual analysis of the detection results to improve the trustworthiness of
the predictions made by the proposed ZeroXpert. Specifically,
we determined whether a sample is classified as an unknown
attack based on whether the model’s maximum prediction
probability exceeds a predefined trustworthiness threshold. To
visually compare the distribution of the maximum prediction
probabilities for unknown attacks versus known traffic, we
plotted the distribution for all test data. Fig. 4 presents these
results: Fig. 4a and Fig. 4b show the maximum prediction
probability distributions for ZeroXpert during the pretraining and retraining stages in the CICIDS-2017 dataset, while
Fig. 4c and Fig. 4d represent the same for the CSE-CICIDS2018 dataset.

Fig. 4. Distribution of maximum prediction probabilities for ZeroXpert at
different training stages.

As shown in Fig. 4a, after pre-training in the CICIDS-2017
dataset, the maximum prediction probabilities for known traffic
(including benign traffic and known attacks) in ZeroXpert
are mostly concentrated above 0.95. However, a significant
portion of the unknown attack traffic also has maximum
prediction probabilities exceeding 0.9, indicating that the
model is overly confident in detecting this type of traffic. In
addition, a small portion of the traffic has maximum prediction

6532

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

probabilities distributed across various ranges. After applying
sparse pruning, as depicted in Fig. 4b, the maximum prediction
probabilities for known traffic remain above 0.95, while more
than half of the unknown attack traffic has its maximum prediction probabilities concentrated between 0.3 and 0.4. Fig. 4c
shows the ZeroXpert pre-training results in the CSE-CICIDS2018 dataset, where the maximum prediction probabilities for
known attack traffic are also higher than 0.95, while those for
unknown attack traffic are concentrated between 0.8 and 1.0.
After sparse pruning, the maximum prediction probabilities
shift to between 0.5 and 0.65. These results demonstrate that
by analyzing the differences in probability distributions, it is
possible to effectively distinguish the presence of unknown
attacks. Sparse pruning helps reduce the influence of features
weakly correlated with the model’s predictions, thereby lowering the model’s overconfidence in unknown attack data and
enabling a more effective identification of unknown attack
traffic.
3) Ablation Experiments: We conducted three ablation
experiments on two different datasets, CICIDS-2017 and
CSE-CICIDS-2018, to evaluate the impact of GMRF and sparsification on model prediction performance. Initially, regarding
recall, when neither GMRF nor Sparsification is applied,
the model performs well in recognizing known traffic on
both datasets but struggles significantly in detecting unknown
attacks (for this experiment, we remove the Patch Embedding, leaving only one Attention Block, as spatial structure
extraction is unnecessary). Next, we applied sparsification to
the model, which does not lead to an improvement in recall.
We then assessed the effect of incorporating GMRF on the
prediction results. In the CICIDS-2017 dataset, the model
achieves a recall rate of approximately 30% to detect unknown
attacks, while in the CSE-CICIDS-2018 dataset, the recall
rate for unknown attacks is only about 10%. In comparison,
when both GMRF and sparse pruning are applied, the recall
rate to detect unknown attacks increases by nearly 30% in
the CICIDS-2017 dataset, reaching approximately 57%. The
improvement is even more pronounced on the CSE-CICIDS2018 data set, with an increase of nearly 70%, resulting in a
final recall rate of 78%.
Furthermore, we observed a significant improvement in
precision when GMRF and sparsification are combined. This
suggests that the integration of these two methods effectively
removes features weakly correlated with the prediction results,
thereby reducing the model’s overconfidence and substantially
lowering the likelihood of errors. In addition, the F1 score
on both data sets also shows superior performance after the
combination of GMRF and sparsification.
C. Sensitivity Analysis of Kernel Size
To evaluate the sensitivity of the Patch Embedding module
in the ZeroXpert model to convolutional kernel sizes, a series
of experiments were conducted on the CICIDS-2017 dataset
with varying kernel dimensions. In these experiments, the
convolutional kernel size was sequentially varied from 2 to
10, covering a total of nine different sizes with a stride of 1.
For each experimental setting, the recall rate and the F1 score
were separately assessed for benign traffic and unknown attack
traffic. The corresponding experimental results are presented
in Fig. 5.

Fig. 5. Sensitivity analysis of Kernel size on CICIDS-2017 dataset.

As shown in Fig. 5a, except for the case where the kernel
size is 2, the experimental results for other kernel sizes remain
within a stable range. The recall rate for benign traffic is
approximately between 0.98 and 0.99, while the recall rate
for unknown attack traffic fluctuates slightly within the range
of 0.55 to 0.57. Furthermore, as indicated in Fig. 5b, similarly,
except when the kernel size is 2, the other experimental results
also demonstrate considerable stability. This indicates that the
Patch Embedding exhibits favorable sensitivity to kernel size
variation, without relying on a specific kernel size to achieve
its effect, and highlights the method’s desirable stability and
robustness. When the kernel size is 2, the performance is
relatively poorer, which may be attributed to an insufficient
receptive field that fails to capture meaningful patches, thus
limiting the formation of discriminative patterns.
D. Comparison With SOTA
To compare detection performance with current research,
we selected three existing state-of-the-art (SOTA) methods:
Kitsune [18], MTH-IDS [26], CVAE-EVT [15] and CADE
[53]. In addition, we deployed a traditional machine learningbased intrusion detection system, Binary-Cls. This system first
uses a random forest algorithm to perform binary classification
between benign traffic and known attacks, followed by the
application of a one-class SVM model to distinguish between
known and unknown attacks. Our primary focus is on the
detection performance of unknown attacks while ensuring the
accuracy of detecting known data (if we solely pursued detection performance for unknown attacks, it can be achieved by
adjusting the threshold, but this would significantly decrease
the detection accuracy for known data). Therefore, we calculate the precision (Precision-B), recall (Recall-B), and the F1
score (F1 Score-B) for benign traffic, as well as the precision
(Precision-U), recall (Recall-U) and the F1 score (F1 ScoreU) for unknown attack traffic. The results are presented in
Table IV. (Given the instability of the MTH-IDS experimental
results, we conducted eight experiments and report the mean
values.)
Firstly, we observe the performance of two reconstructionbased methods. CVAE-EVT demonstrates relatively good
performance in the CICIDS-2017 data set, achieving a recall
rate of 97.66% for benign traffic and 49% for unknown attacks.
In addition, it achieves decent levels of precision and an F1
score. In contrast, Kitsune performs moderately, with a recall
rate of 50.25% for unknown attacks and only 40.94% for
benign traffic, alongside similarly average precision and F1
score results. In comparison, our ZeroXpert shows a recall rate
of 98% for benign traffic and 56.82% for unknown attacks on
the CICIDS-2017 dataset, surpassing the other two methods.

ZHA et al.: SPARSE GAUSSIAN–MARKOV MODELING FOR ROBUST AND TRUSTWORTHY UNKNOWN CYBER DEFENSE

6533

TABLE IV
C OMPARISON OF D IFFERENT M ETHODS FOR D ETECTION OF U NKNOWN ATTACKS

It also leads in precision and F1 score. In the CSE-CICIDS2018 dataset, CVAE-EVT performs poorly, with a recall rate
of around 90% for benign traffic but only 2% for unknown
attacks. Kitsune also shows moderate performance, with a
recall rate of 59.73% for unknown attacks and only 41.27%
for benign traffic. In contrast, our ZeroXpert maintains an
excellent recall rate of 95% for normal traffic in this data set,
despite a slight decrease compared to its performance on the
CICIDS-2017 data set. However, the recall rate for unknown
attacks increases significantly to 77%, with precision and the
F1 score far exceeding the other two methods.
Secondly, we focus on methods based on machine learning. In the CICIDS-2017 dataset, MTH-IDS and Binary-Cls
achieve recall rates for unknown attacks of approximately 16%
and 18%, respectively, with modest recall rates for benign
traffic (86% for MTH-IDS). CADE achieves 83.42% recall
for benign traffic but only 23.15% for unknown attacks,
outperforming MTH-IDS and Binary-Cls in known traffic
detection, but still lagging behind ZeroXpert in unknown
attack detection. In the CSE-CICIDS-2018 dataset, MTHIDS and Binary-Cls slightly outperform ZeroXpert in benign
traffic detection (98.56% and 99.27%), while CADE achieves
a recall of 74.32% for benign traffic and 86.81% for unknown
attacks, demonstrating strong performance in unknown attack
detection. Despite this, ZeroXpert still maintains superior
overall performance, balancing known and unknown traffic
detection effectively.
Due to the varying sample sizes of different classes across
datasets illustrated in Table II, the precision may differ
accordingly. In addition, the complexity of attacks can vary
significantly between datasets. For example, some anomalous
traffic may be disguised to closely resemble normal traffic.
Even for the same attack type, such variations can lead to
observable differences in metrics such as the FPR. Nevertheless, we strictly ensure that all comparisons among different
baselines are conducted fairly, and each method is evaluated
under the same experimental settings and benchmarks.
The effectiveness of ZeroXpert in detecting unknown
attacks while maintaining accuracy in detecting known traffic can be attributed to several factors. Firstly, it leverages
GMRF to understand the spatial correlations in traffic, thereby
preventing the model’s predictions from overly depending on
local features. This not only enhances the accuracy of known

Fig. 6. Detection latency.

traffic detection, but also improves the model’s robustness in
complex network environments. Secondly, by implementing
sparse operations, ZeroXpert effectively removes redundant
and unnecessary parameter branches, reducing the impact
of noise and anomalous data on predictions. This enables
the model to better distinguish between benign and anomalous traffic when facing unknown attacks, thereby reducing
misclassifications and lowering the risk of high prediction
probabilities. In contrast, several existing SOTA methods do
not thoroughly analyze the fundamental reasons for the difficulty in detecting unknown attacks. Although these methods
excel in detecting known attacks, they often perform poorly
in handling unknown attacks and do not achieve comparable
detection effectiveness.
E. Performance Results
1) Model Size: The number of model parameters directly
determines its memory storage requirements and affects computational complexity and inference time. Given the need for
real-time performance in intrusion detection systems, models
with a large number of parameters may struggle to meet this
requirement. Our proposed ZeroXpert uses a model with a
total of 21,936 parameters. This parameter count significantly
reduces memory consumption and computational complexity
while maintaining model performance, making it effective in
resource-constrained environments.
2) Latency: We conducted eight independent experiments
for each batch size on a low-specification (13th Gen Intel(R)
Core(TM) i5-13500H, 32GB DRAM) computer and calculated
the average to evaluate the detection latency of ZeroXpert; the

6534

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

TABLE V
R ECOMMENDED H YPER -PARAMETER C ONFIGURATION

is developed in Python. Although Python offers ease of use
and flexibility, it may not be the most optimal for performance
in computation-intensive tasks. Therefore, implementing the
system in a higher-level language like C++ could potentially
further reduce the detection latency, thereby enhancing the
overall performance and feasibility of the system in practical
applications.
VII. R ELATED W ORK
In this section, we summarize previous related research
efforts, with detailed information provided as follows.

TABLE VI
L ATENCY M EASUREMENTS FOR D IFFERENT BATCH S IZE

Fig. 7. Distribution of detection latency.

results are shown in Fig. 6 (the raw experimental data can be
found in Appendix B.2, Table VI)..
Fig. 6 illustrates that as the batch size increases, the
detection latency of ZeroXpert decreases from an initial
740 microseconds to approximately 130 microseconds. Furthermore, Fig. 7 presents the density distribution of the latency
statistics for all samples (with a batch size of 8). It is
evident from this figure that the sample detection latency
of ZeroXpert is predominantly within the range of 120 to
130 microseconds. Notably, this evaluation was conducted on
a low-spec machine without GPU acceleration. Despite these
constraints, ZeroXpert demonstrates a detection latency of
approximately 130 microseconds when concurrent processing
is considered, meeting the stringent requirements for real-time
detection. It is also important to note that our prototype system

A. Machine Learning Based NIDS
Machine learning-based network intrusion detection methods have shown superior performance compared to traditional
signature-based methods, particularly in the identification of
unknown attacks [3], [54]. Ahmad et al. [30] compared the
research methods and performance of traditional machine
learning algorithms (such as the support vector machine
(SVM) and decision trees) in the detection of zero-day attacks.
Fu et al. [25] proposed a real-time malicious traffic detection
system based on frequency domain analysis, which achieved
accurate and robust network attack detection through feature
extraction and automatic parameter selection, combined with
statistical clustering algorithms. Yang et al. [53] introduced
a contrastive learning–based method that models the distributions of different attack families in latent space, using
distances to cluster centroids and robust statistics (e.g., MAD)
to detect distributional drift and identify zero-day attacks.
Yang et al. [26] introduced a multilayer hybrid intrusion detection system named MTH-IDS to detect known and unknown
network attacks in vehicular networks. This system combined signature-based and anomaly-based detection methods
and optimized model performance through machine learning
algorithms. However, traditional machine learning methods
exhibited limited generalization capability and failed to clearly
distinguish between unknown and known attacks. Although
Yang et al. [26] attempted to separate these categories, the
false positive rate (normal traffic being misclassified as attack
traffic) became uncontrollable.
Transfer learning has also shown promising applications in
intrusion detection. For example, Sameera and Shashi [24]
proposed a deep transductive transfer learning framework for
zero-day attack detection. This framework aligns the source
and target domains into a common latent space through
manifold alignment, thereby avoiding discrepancies in feature
spaces and probability distributions. It generates soft labels
using cluster correspondence programs to address the scarcity
of labeled instances in the target domain and employs deep
neural networks (DNNs) to build a binary classifier for zeroday attack detection. Taghiyarrenani et al. [21] introduced
a knowledge transfer method based on transfer learning
to better handle unknown attacks. Furthermore, Kim et al.
[22] suggested using transfer deep convolutional generative
adversarial networks (tDCGANs) to generate pseudomalicious
traffic based on known attack traffic, thus enhancing zero-day
attack detection performance through data set enhancement.
Few-shot learning [55] and zero-shot learning [56] are becoming increasingly common in intrusion detection. For example,
Zhang et al. [57] introduced a zero-shot learning method based

ZHA et al.: SPARSE GAUSSIAN–MARKOV MODELING FOR ROBUST AND TRUSTWORTHY UNKNOWN CYBER DEFENSE

on sparse autoencoders to detect unknown attacks. Yang et al.
[58] proposed a mechanism for training models using a fewshot learning to acquire general knowledge about attacks rather
than specific knowledge about individual categories, thereby
enhancing the detection of unknown attacks. However, while
these methods demonstrated good generalization capabilities,
they still failed to explicitly distinguish between known and
unknown attacks, which is crucial for defensive purposes.
B. Reconstruction Based Zero-Day Detection
In recent years, reconstruction-based methods to address the
challenge of unknown attack detection have gained increasing
attention. The primary idea involves first auto-encoding the
known traffic and then reconstructing the encoded vectors.
Since unknown attack traffic is not included in the training process, it tends to exhibit higher reconstruction errors, making it
easier to identify as anomalous [59]. For example, Hindy et al.
[16] proposed using autoencoders with a reconstruction error
threshold to detect zero-day attacks. Zha et al. [10] suggested applying a sigmoid kernel transformation to map traffic
from a low-dimensional space to a high-dimensional space,
thus amplifying the differences between unknown attacks and
known traffic, and then using an encoder-decoder framework
for detection. Yang et al. [15] explored the training of a
generative model to examine the deviation between the generated instances conditioned on the labels predicted by a
probabilistic discriminative model (a known attack detector)
and the input instances. Additionally, they combined extreme
value theory to detect unknown attacks. Tang et al. [17]
recommended employing an encoder-decoder recurrent neural
network to train a self-translation machine, which captures
the syntactic and semantic patterns of benign requests while
marking incomprehensible requests as attacks. Furthermore,
Mirsky et al. [18] introduced a stacked autoencoder neural
network designed to jointly distinguish between normal and
anomalous traffic patterns.
Reconstruction-based methods have shown promise in the
field of unknown attack detection. These approaches not only
maintain effective detection performance, but also allow for
the adjustment of reconstruction error thresholds to control the
false positive rate (i.e., misclassifying normal traffic as attack
traffic), which is crucial. However, most of these methods
rely on cosine similarity or Euclidean distance to measure
the reconstruction error. Given the characteristics of network
traffic data (where, after normalization, most feature values are
close to 0 and a few are close to 1, as shown in Fig. 1), these
metrics tend to focus more on changes in larger values while
neglecting smaller ones, making the reconstruction process
relatively straightforward. Consequently, these methods are
subject to certain limitations. We provide a theoretical analysis
to support this point (see Appendix A).
VIII. D ISCUSSION
In this section, we discuss our proposed method further and
explore potential directions for future work.
A. Adaptation to Dynamic Network Environments
In real-world deployments, network environments are inherently dynamic, where attack patterns continuously evolve and
may deviate from previously observed distributions. Rather

6535

than relying on frequent model updates or explicit online
learning, ZeroXpert is designed to adapt to such dynamics
through robust uncertainty-aware detection. By modeling the
spatial relationships among the traffic features using GMRF,
ZeroXpert captures stable structural dependencies within the
known traffic space. The subsequent sparsification stage further suppresses weakly relevant or spurious features, reducing
the model’s tendency to produce overconfident predictions. As
a result, when encountering traffic generated by evolving or
previously unseen attacks, the model typically yields lower
prediction confidence instead of forcibly assigning them to
known classes. This confidence-aware decision mechanism
allows ZeroXpert to effectively flag evolving attack patterns as
unknown without immediate retraining, making it well suited
for deployment in dynamic network environments where traffic
characteristics and attack behaviors change over time.
B. Potential Directions for Future Work
ZeroXpert is designed to robustly identify evolving
and previously unseen attacks without frequent retraining.
Meanwhile, adapting to long-term distributional shifts and
continuously emerging attack patterns is also an important
direction for future research. One promising extension is
to incorporate lightweight drift detection mechanisms that
monitor changes in the statistical properties of incoming traffic
or the confidence distribution of the model, thus triggering
adaptive responses only when significant data drift is detected.
In addition, future work may explore selective or incremental
model updates, where newly observed unknown samples
with high confidence can be gradually incorporated into
the known traffic space without retraining the entire model
from scratch. Another potential direction lies in combining
ZeroXpert with generative or replay-based techniques to
mitigate catastrophic forgetting when adapting to new attack
types while maintaining stable performance on previously
learned patterns. Finally, investigating theoretically grounded
calibration strategies under data drift could further enhance
the reliability of confidence-based unknown attack detection
in highly dynamic network environments.
Meanwhile, data imbalance is an important issue that
deserves careful consideration in network traffic detection, as
the number of benign traffic samples typically far exceeds
that of attack traffic. Existing studies have explored mitigation strategies such as employing generative models [60]
to synthesize minority-class samples to improve class balance. However, these approaches also suffer from inherent
limitations, including the potential risk of data poisoning.
Developing a novel sampling strategy therefore represents a
promising research direction. Unlike random downsampling
methods, which reduce the majority class at the cost of
losing informative samples, an effective solution to traffic
imbalance should aim to reduce sample redundancy while
preserving critical information. Such a strategy would have
the additional benefit of significantly reducing model training
time. These considerations constitute an important part of our
future research agenda.
IX. C ONCLUSION
In this study, we propose a method based on a Gaussian Markov Random Field to capture the spatial feature

6536

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

distribution of network traffic, effectively modeling the relationships between local features. GMRF also better satisfies
the conditional independence assumption. Building on this, we
apply sparsification to the model by pruning weakly correlated
parameters, reducing the prediction probability of unknown
attack traffic. This creates a significant gap between the prediction probabilities of known and unknown traffic, enabling the
effective detection of unknown attacks. As a result, ZeroXpert
not only addresses the issue of model overfitting, but also
mitigates the problem of overconfident predictions when faced
with unknown attack traffic. We evaluated the performance of
our approach on two public datasets, CICIDS-2017 and CSECICIDS-2018, through both detection performance evaluation
and ablation experiments. The results show that our method
achieves recall rates of 57% and 77% for unknown attacks
while maintaining a recall rate above 95% for known traffic,
significantly outperforming several existing SOTA methods.
Additionally, performance tests on a low-spec machine demonstrate that the system maintains low detection latency, making
it well-suited for real-time requirement.
A PPENDIX
A. Limitations of Reconstruction-Based Methods
In this section, we will theoretically elaborate on the potential shortcomings and limitations of unknown attack detection
methods based on encoder-decoder architecture [15], [16],
[17], [18].
The main idea of the unknown attack detection method
based on the encoder-decoder architecture is to first encode
the known feature vectors, then decode the encoded semantic vectors, and finally determine the presence of unknown
attacks based on the reconstruction error. The calculation
of the reconstruction error mainly uses Cosine Similarity or
Euclidean Distance. However, we believe that methods such
as cosine similarity and Euclidean distance have theoretical
flaws in this direction: they tend to ignore features with
relatively small values, while features with larger values have
a more significant impact on the final result (e.g. cosine
similarity).
Assume there are two feature vectors X1 , X2 , each
with m larger features and n smaller features, denoted as
X1 = (x1,1 , x1,2 , . . . , x1,m , x1,m+1 , x1,m+2 , . . . , x1,m+n ) and
X2 = (x2,1 , x2,2 , . . . , x2,m , x2,m+1 , x2,m+2 , . . . , x2,m+n ).
The cosine similarity cos(X1 , X2 ) is expressed as:
Pm+n
Pm
x1,j x2,j
i=1 x1,i x2,i +
qP
qj=m+1
P
P
Pm+n
m
m+n
m
2
2
2
2
i=1 x1,i +
j=m+1 x1,j
i=1 x2,i +
j=m+1 x2,j
(17)
After normalization, all feature values are within
the range of [0, 1]. For larger value features x1,i and
x2,i (i ∈ {1, 2, . . . , m}), we assume x1,i → 1, x2,i → 1,
and
for
smaller
value
features
x1,m+j
and
x2,m+j (j ∈ {1, 2, . . . , n}), we assume x1,m+j → 0,
x2,m+j → 0. Therefore,
m
X
i=1

x1,i x2,i → 1,

m+n
X
j=m+1

x1,j x2,j → 0

m
X

x21,i → 1,

i=1
m
X
i=1

m+n
X

x21,j → 0

j=m+1

x22,i → 1,

m+n
X

x22,j → 0

(18)

j=m+1

By Eq. (17) and Eq. (18), we obtain the following.
Pm
x1,i x2,i
cos(X1 , X2 ) = qP i=1 qP
m
m
2
2
i=1 x1,i
i=1 x2,i

(19)

Combining the characteristics of the network flow feature
values, most of the feature values do not follow a normal
distribution. Typically, a feature value’s distribution contains
a small number of extremely large values, while the majority
are distributed as smaller values (for example, flow duration,
where very few flows last for an extended period, while most
end within a relatively short time). We have confirmed this
phenomenon in several existing datasets [40], [41], [42], [61],
which fully supports our assumption. According to Eq. (19),
we can see that the reconstruction error depends on the few
features with larger values, making the reconstruction less
challenging and presenting the “illusion” that unknown attack
traffic is highly similar to known traffic.
Similarly, the Euclidean distance is also more sensitive to
large feature values and less sensitive to small feature values.
This indicates that the Euclidean distance calculation, in cases
where feature value differences are substantial, tends to reflect
the differences in large feature values more prominently,
thereby neglecting the impact of small feature values.
B. Details of Implementations
1) Detail of Recommended Hyper-Parameter: Table V
shows the hyperparameters used in ZeroXpert and the recommended values.
In the sparsification process, two important hyperparameters
ζ and γ are required to satisfy ζ < 0.0 and γ > 1.0.
This design ensures that, after the hard-thresholding operation
z = min(1, max(0, s̃)), the model can still produce exact 0 and
1 values rather than only approximate ones. We recommend
setting ζ = −0.1 and γ = 1.1, which are empirically
chosen [43]. If ζ becomes too negative (e.g., −10), the sigmoid/logistic transformation will push the gating probability
excessively toward 0 or 1, damaging the smoothness of the
gradient; if ζ is too close to 0, the model will be unable to
produce exact zeros. The parameter γ plays a symmetric role
in controlling the upper bound. In practice, a small outward
stretch (around ±0.1) is sufficient to allow some samples to
fall outside the interval [0, 1], allowing exact 0/1 values after
hard thresholding.
Furthermore, in relation to the hyperparameter β, it controls
the smoothness of the Concrete distribution. A larger β makes
the distribution closer to Bernoulli, whereas a smaller β yields
smoother relaxations with a lower gradient variance but a
higher bias. We set β = 0.66, which has been shown in
previous work [62] to provide a good balance between training
stability and the desired level of sparsity.
2) Raw Data of Latency Experiments: Table VI illustrates
the raw data from eight independent experiments for the
performance test (latency) described in Section VI-E.

ZHA et al.: SPARSE GAUSSIAN–MARKOV MODELING FOR ROBUST AND TRUSTWORTHY UNKNOWN CYBER DEFENSE

R EFERENCES
[1]

J. Cao, Z. Yang, K. Sun, Q. Li, M. Xu, and P. Han, “Fingerprinting SDN
applications via encrypted control traffic,” in Proc. 22nd Int. Symp. Res.
Attacks, Intrusions Defenses (RAID), 2019, pp. 501–515.
[2] M. A. Jamshed et al., “Kargus: A highly-scalable software-based intrusion detection system,” in Proc. ACM Conf. Comput. Commun. Secur.,
Oct. 2012, pp. 317–328.
[3] H. Li, H. Hu, G. Gu, G.-J. Ahn, and F. Zhang, “VNIDS: Towards
elastic security with safe and efficient virtualization of network intrusion
detection systems,” in Proc. ACM SIGSAC Conf. Comput. Commun.
Secur. (CCS), Oct. 2018, pp. 17–34.
[4] J. Nam, M. Jamshed, B. Choi, D. Han, and K. Park, “Haetae: Scaling the
performance of network intrusion detection with many-core processors,”
in Proc. 18th Int. Symp. Res. Attacks, 2015, pp. 89–110, doi: 10.1007/
978-3-319-26362-5 5.
[5] C. Fu, Q. Li, and K. Xu, “Flow interaction graph analysis: Unknown
encrypted malicious traffic detection,” IEEE/ACM Trans. Netw., vol. 32,
no. 4, pp. 2972–2987, Aug. 2024.
[6] V. Chandola, A. Banerjee, and V. Kumar, “Anomaly detection: A
survey,” ACM Comput. surveys (CSUR), vol. 41, no. 3, pp. 1–58, 2009.
[7] P. Garcı́a-Teodoro, J. Dı́az-Verdejo, G. Maciá-Fernández, and
E. Vázquez, “Anomaly-based network intrusion detection: Techniques,
systems and challenges,” Comput. Secur., vol. 28, nos. 1–2, pp. 18–28,
Feb. 2009.
[8] C. Lin, Y. Jiang, W. Zhang, X. Meng, T. Zuo, and Y. Zhang, “TraGe: A
generic packet representation for traffic classification based on headerpayload differences,” in Proc. IEEE/ACM 33rd Int. Symp. Quality
Service (IWQoS), Jul. 2025, pp. 1–6.
[9] C. Zha et al., “A-NIDS: Adaptive network intrusion detection system
based on clustering and stacked CTGAN,” IEEE Trans. Inf. Forensics
Security, vol. 20, pp. 3204–3219, 2025.
[10] C. Zha et al., “SKT-IDS: Unknown attack detection method based
on sigmoid kernel transformation and encoder–decoder architecture,”
Comput. Secur., vol. 146, Nov. 2024, Art. no. 104056.
[11] C. Lin et al., “Convolutions are competitive with transformers for encrypted traffic classification with pre-training,” 2025,
arXiv:2508.02001.
[12] M. Wang and W. Deng, “Deep face recognition: A survey,” Neurocomputing, vol. 429, pp. 215–244, Mar. 2021.
[13] A. Holzinger, G. Langs, H. Denk, K. Zatloukal, and H. Müller,
“Causability and explainability of artificial intelligence in medicine,”
WIREs Data Mining Knowl. Discovery, vol. 9, no. 4, p. 1312, Jul. 2019.
[14] S. Jiang, H. Yang, Q. Xie, C. Ma, S. Wang, and G. Xing,
“Lancelot: Towards efficient and privacy-preserving Byzantine-robust
federated learning within fully homomorphic encryption,” 2024,
arXiv:2408.06197.
[15] J. Yang, X. Chen, S. Chen, X. Jiang, and X. Tan, “Conditional
variational auto-encoder and extreme value theory aided two-stage
learning approach for intelligent fine-grained known/unknown intrusion
detection,” IEEE Trans. Inf. Forensics Security, vol. 16, pp. 3538–3553,
2021.
[16] H. Hindy, R. Atkinson, C. Tachtatzis, J.-N. Colin, E. Bayne, and
X. Bellekens, “Towards an effective zero-day attack detection using
outlier-based deep learning techniques,” 2020, arXiv:2006.15344.
[17] R. Tang et al., “ZeroWall: Detecting zero-day web attacks through
encoder–decoder recurrent neural networks,” in Proc. IEEE INFOCOM
Conf. Comput. Commun., Jul. 2020, pp. 2479–2488.
[18] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “Kitsune: An
ensemble of autoencoders for online network intrusion detection,” 2018,
arXiv:1802.09089.
[19] T. Zoppi, A. Ceccarelli, and A. Bondavalli, “Unsupervised algorithms to
detect zero-day attacks: Strategy and application,” IEEE Access, vol. 9,
pp. 90603–90615, 2021.
[20] I. Ahmad, M. Basheri, M. J. Iqbal, and A. Rahim, “Performance comparison of support vector machine, random forest, and extreme learning
machine for intrusion detection,” IEEE Access, vol. 6, pp. 33789–33795,
2018.
[21] Z. Taghiyarrenani, A. Fanian, E. Mahdavi, A. Mirzaei, and H. Farsi,
“Transfer learning based intrusion detection,” in Proc. 8th Int. Conf.
Comput. Knowl. Eng. (ICCKE), Oct. 2018, pp. 92–97.
[22] J.-Y. Kim, S.-J. Bu, and S.-B. Cho, “Zero-day malware detection using transferred generative adversarial networks based on deep
autoencoders,” Inf. Sci., vols. 460–461, pp. 83–102, Sep. 2018.
[23] S. Cui et al., “FG-SAT: Efficient flow graph for encrypted traffic
classification under environment shifts,” IEEE Trans. Inf. Forensics
Security, vol. 20, pp. 5326–5339, 2025.

6537

[24] N. Sameera and M. Shashi, “Deep transductive transfer learning
framework for zero-day attack detection,” ICT Exp., vol. 6, no. 4,
pp. 361–367, Dec. 2020.
[25] C. Fu, Q. Li, M. Shen, and K. Xu, “Frequency domain feature based
robust malicious traffic detection,” IEEE/ACM Trans. Netw., vol. 31,
no. 1, pp. 452–467, Feb. 2023.
[26] L. Yang, A. Moubayed, and A. Shami, “MTH-IDS: A multitiered hybrid
intrusion detection system for Internet of Vehicles,” IEEE Internet
Things J., vol. 9, no. 1, pp. 616–632, Jan. 2022.
[27] T. van Ede et al., “FlowPrint: Semi-supervised mobile-app fingerprinting
on encrypted network traffic,” in Proc. Netw. Distrib. Syst. Secur. Symp.,
2020.
[28] X. Lin, G. Xiong, G. Gou, Z. Li, J. Shi, and J. Yu, “ET-BERT: A
contextualized datagram representation with pre-training transformers
for encrypted traffic classification,” in Proc. ACM Web Conf., Apr. 2022,
pp. 633–642.
[29] C. Zha, H. Pan, B. Bai, J. Wu, and R. Zhang, “FlowXpert: Contextaware flow embedding for enhanced traffic detection in IoT network,”
IEEE Trans. Mobile Comput., pp. 1–18, 2026.
[30] R. Ahmad, I. Alsmadi, W. Alhamdani, and L. Tawalbeh, “Zero-day
attack detection: A systematic literature review,” Artif. Intell. Rev.,
vol. 56, no. 10, pp. 10733–10811, Oct. 2023.
[31] C. Zha et al., “DM-IDS—A network intrusion detection method based
on dual-modal fusion,” IEEE Trans. Netw. Service Manage., vol. 22,
no. 4, pp. 3646–3661, Aug. 2025.
[32] J. Zhao et al., “ReTrial: Robust encrypted malicious traffic detection via
discriminative relation incorporation and misleading relation correction,”
IEEE Trans. Inf. Forensics Security, vol. 20, pp. 677–692, 2025.
[33] X. Wang, Z. Lu, X. Wang, M. He, and X. Wang, “GETRF: A general
framework for encrypted traffic identification with robust representation
based on datagram structure,” IEEE Trans. Cognit. Commun. Netw.,
vol. 10, no. 6, pp. 2045–2060, Dec. 2024.
[34] Y. Liu and K. Yang, “Asynchronous decentralized federated anomaly
detection for 6G networks,” IEEE Trans. Cognit. Commun. Netw.,
vol. 11, no. 5, pp. 3384–3396, Oct. 2025.
[35] C. Wu, J. Sun, J. Chen, M. Alazab, Y. Liu, and Y. Xiang, “TCGIDS: Robust network intrusion detection via temporal contrastive graph
learning,” IEEE Trans. Inf. Forensics Security, vol. 20, pp. 1475–1486,
2025.
[36] N. Wang, S. Shi, Y. Chen, W. Lou, and Y. T. Hou, “FeCo: Boosting
intrusion detection capability in IoT networks via contrastive learning,”
IEEE Trans. Depend. Secure Comput., vol. 22, no. 4, pp. 4215–4230,
Jul. 2025.
[37] W. Wang, X. Du, D. Shan, R. Qin, and N. Wang, “Cloud intrusion detection method based on stacked contractive auto-encoder and
support vector machine,” IEEE Trans. Cloud Comput., vol. 10, no. 3,
pp. 1634–1646, Jul. 2022.
[38] H. Rue and L. Held, Gaussian Markov Random Fields: Theory and
Applications. London, U.K.: Chapman & Hall, 2005.
[39] P. Sidén and F. Lindsten, “Deep Gaussian Markov random fields,” in
Proc. Int. Conf. Mach. Learn., 2020, pp. 8916–8926.
[40] C. I. for Cybersecurity. (2017). Cicids 2017 Dataset. [Online]. Available:
https://www.unb.ca/cic/datasets/ids-2017.html
[41] I. Sharafaldin, A. H. Lashkari, and A. A. Ghorbani, “Toward generating
a new intrusion detection dataset and intrusion traffic characterization,”
ICISSp, vol. 1, pp. 108–116, Jan. 2018.
[42] C. I. for Cybersecurity (CIC). (2018). Cicids 2018 Dataset. [Online].
Available: https://www.unb.ca/cic/datasets/ids-2018.html
[43] C. Louizos, M. Welling, and D. P. Kingma, “Learning sparse neural
networks through L0 regularization,” 2017, arXiv:1712.01312.
[44] A. H. Lashkari, G. D. Gil, M. S. I. Mamun, and A. A. Ghorbani,
“Characterization of Tor traffic using time based features,” in Proc. 3rd
Int. Conf. Inf. Syst. Secur. Privacy (ICISSP), Porto, Portugal, Feb. 2017,
pp. 253–262.
[45] V. N. G. Raju, K. P. Lakshmi, V. M. Jain, A. Kalidindi, and V. Padma,
“Study the influence of normalization/transformation process on the
accuracy of supervised classification,” in Proc. 3rd Int. Conf. Smart
Syst. Inventive Technol. (ICSSIT), Aug. 2020, pp. 729–735.
[46] Y. Lecun, L. Bottou, Y. Bengio, and P. Haffner, “Gradient-based
learning applied to document recognition,” Proc. IEEE, vol. 86, no. 11,
pp. 2278–2324, 1998.
[47] A. Vaswani et al., “Attention is all you need,” in Proc. Adv. Neural Inf.
Process. Syst., vol. 30, 2017.
[48] J. L. Ba, J. R. Kiros, and G. E. Hinton, “Layer normalization,” 2016,
arXiv:1607.06450.
[49] F. Pedregosa et al., “Scikit-learn: Machine learning in Python,” J. Mach.
Learn. Res., vol. 12, pp. 2825–2830, Nov. 2011.

6538

IEEE TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING, VOL. 12, 2026

[50] A. Paszke et al., “Pytorch: An imperative style, high-performance deep
learning library,” in Proc. Adv. Neural Inf. Process. Syst., vol. 32, 2019.
[51] L. Breiman, “Random forests,” Mach. Learn., vol. 45, no. 1, pp. 5–32,
2001.
[52] M. Amer, M. Goldstein, and S. Abdennadher, “Enhancing one-class
support vector machines for unsupervised anomaly detection,” in Proc.
ACM SIGKDD Workshop Outlier Detection Description, Aug. 2013,
pp. 8–15.
[53] L. Yang et al., “CADE: Detecting and explaining concept drift samples
for security applications,” in Proc. 30th USENIX Secur. Symp., Vancouver, BC, Canada, 2021, pp. 2327–2344. [Online]. Available: https://
www.usenix.org/conference/usenixsecurity21/presentation/yang-limin
[54] K. Borders, J. Springer, and M. Burnside, “Chimera: A declarative
language for streaming network traffic analysis,” in Proc. USENIX Secur.
Symp., 2012, pp. 365–379.
[55] F. Sung, Y. Yang, L. Zhang, T. Xiang, P. H. S. Torr, and
T. M. Hospedales, “Learning to compare: Relation network for few-shot
learning,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., Jun.
2018, pp. 1199–1208.
[56] F. Pourpanah et al., “A review of generalized zero-shot learning
methods,” IEEE Trans. Pattern Anal. Mach. Intell., vol. 45, no. 4,
pp. 4051–4070, Apr. 2023.
[57] Z. Zhang, Q. Liu, S. Qiu, S. Zhou, and C. Zhang, “Unknown
attack detection based on zero-shot learning,” IEEE Access, vol. 8,
pp. 193981–193991, 2020.
[58] J. Yang, H. Li, S. Shao, F. Zou, and Y. Wu, “FS-IDS: A framework
for intrusion detection based on few-shot learning,” Comput. Secur.,
vol. 122, Nov. 2022, Art. no. 102899.
[59] M. Gharib, B. Mohammadi, S. H. Dastgerdi, and M. Sabokrou,
“AutoIDS: Auto-encoder based method for intrusion detection system,”
2019, arXiv:1911.03306.
[60] H. Ding, Y. Sun, N. Huang, Z. Shen, and X. Cui, “TMG-GAN:
Generative adversarial networks-based imbalanced learning for network intrusion detection,” IEEE Trans. Inf. Forensics Security, vol. 19,
pp. 1156–1167, 2024.
[61] Y. Kim, S. Hakak, and A. Ghorbani, “DDoS attack dataset (CICEV2023)
against EV authentication in charging infrastructure,” in Proc. 20th
Annu. Int. Conf. Privacy, Secur. Trust (PST), Aug. 2023, pp. 1–9.
[62] C. J. Maddison, A. Mnih, and Y. W. Teh, “The concrete distribution: A continuous relaxation of discrete random variables,” 2016,
arXiv:1611.00712.

Chao Zha is currently pursuing the combined M.S.Ph.D. degree in computer science and technology
with the Institute of Computing Technology, Chinese
Academy of Sciences, Beijing, China. His research
focuses on network security, with particular interests in network intrusion detection systems (NIDS),
encrypted traffic detection, malware analysis, and
intelligent defense systems. He has published some
papers in peer-reviewed journals, including IEEE
T RANSACTIONS ON I NFORMATION F ORENSICS
AND S ECURITY , Computers & Security, and IEEE
T RANSACTIONS ON N ETWORK AND S ERVICE M ANAGEMENT.

Tian Liu received the B.S. degree in mathematics
and applied mathematics from Sichuan University, China, in 2011, and the M.S. degree in
probability and statistics and the Ph.D. degree in
computer science and software engineering from
Auburn University, Auburn, AL, USA, in 2016
and 2022, respectively. She is currently a Research
Associate with Zhejiang Academy of Agricultural
Sciences (ZAAS). Before joining ZAAS, she was a
Research Staff Member with Zhejiang Laboratory.
Her research interests include distributed machine
learning and wireless computer networking, with an emphasis on system
performance, optimization, and security/privacy.

Chungang Lin received the B.S. degree from Xidian
University in 2022. He is currently pursuing the
Ph.D. degree with the Institute of Computing Technology, Chinese Academy of Sciences. His current
research interests include network traffic analysis,
traffic classification, traffic engineering, and intelligent networking and systems.

Bing Bai received the M.S. degree in computer
science and technology from the National University
of Defense Technology. He is currently an Associate
Investigator with the Research Center for HighEfficiency Computing Infrastructure, Zhejiang Lab.
His research interests include communication networks and security.

Ruyun Zhang received the Ph.D. degree in communications and information systems in 2011.
He is currently working as a Principal Investigator with the Research Center for High-Efficiency
Computing Infrastructure, Zhejiang Lab. He is a
Researcher and a Ph.D. Supervisor for many years.
He has published several papers in international
conferences and peer-reviewed journals, including
IEEE T RANSACTIONS ON I NFORMATION F OREN SICS AND S ECURITY , IEEE T RANSACTIONS ON
D EPENDABLE AND S ECURE C OMPUTING, Computers & Security, and IEEE T RANSACTIONS ON N ETWORK AND S ERVICE
M ANAGEMENT. His research interests include communication networks and
security.
PAPER_TEXT
