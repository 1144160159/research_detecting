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
# [206] Detecting Cloud Anomaly via Broad Network-Based Contrastive Autoencoder
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
编号：206
题名：Detecting Cloud Anomaly via Broad Network-Based Contrastive Autoencoder
年份：2024
DOI：10.1109/tnsm.2024.3353772
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_tnsm.2024.3353772.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：时序、日志、KPI 与云原生异常检测
相关性：弱相关，分数 4
已有代码状态：候选不可访问；BroadCAE

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\206.txt
- 原始字符数：67293
- 本次发送字符数：67293
- 是否截断：False

代码包：
- 仓库：BroadCAE
  - URL：https://github.com/zhongguoxiang/BroadCAE
  - 状态：failed
  - 本地目录：source\BroadCAE
  - 顶层结构：
  - 主要语言：
  - README 标题：
  - README 运行线索：
  - 关键文件：{}
  - 数据集线索：

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 3, JUNE 2024

3249

Detecting Cloud Anomaly via Broad
Network-Based Contrastive Autoencoder
Guoxiang Zhong , Fagui Liu , Member, IEEE, Jun Jiang , Member, IEEE,
Bin Wang , Xi Yao, and C. L. Philip Chen , Fellow, IEEE

Abstract—Anomaly detection is indispensable for achieving
higher availability and reliability in the cloud computing. The
traditional autoencoder-based method only models the historical
normal samples and then identifies the current online anomaly
samples by the fixed threshold of anomaly score. Although more
advances have been made in recent years, two main challenges
remain: (i) ignoring the historical anomaly samples, (ii) poor
self-adaptive ability for online detection. To address the above
challenges, we propose a unified detector, namely BroadCAE,
which integrates autoencoder with contrastive learning and broad
network. Specifically, the reconstruction loss is first replaced
by contrastive loss, which equally formulates both normal and
anomaly samples. These samples belonging to the same class
become closer in a lower-dimensional space. Conversely, different
classes of samples are far away from each other. Next, we apply
the anomaly-score-based pseudo thresholds to train the dynamic
threshold selection, which generates the threshold according to
the coming sample. The broad network in dynamic threshold
selection takes the place of the deep network, which overcomes
catastrophic forgetting and adapts to new online samples.
Finally, validation experiments are conducted on four benchmark
datasets. Our BroadCAE outperforms the comparative baseline
methods by averaging over 4% of the f1-score.
Index Terms—Anomaly detection, contrastive learning, broad
network, cloud computing.

I. I NTRODUCTION
ITH the wide application of cloud computing, the
scales of cloud services and their users are dramatically
increasing. For a better user experience, the cloud operation

W

Manuscript received 16 August 2023; revised 22 December 2023; accepted
10 January 2024. Date of publication 15 January 2024; date of current version
12 July 2024. This work was supported in part by the Guangdong Major
Project of Basic and Applied Basic Research under Grant 2019B030302002, in
part by the Science and Technology Major Project of Guangzhou under Grant
202007030006, in part by the Science and Technology Project of Guangdong
Province under Grant 2021B1111600001, and in part by the Major Key Project
of PCL, China under Grant PCL2023A09. The associate editor coordinating
the review of this article and approving it for publication was H. Lutfiyya.
(Corresponding authors: Fagui Liu; Jun Jiang.)
Guoxiang Zhong, Xi Yao, and C. L. Philip Chen are with the School of
Computer Science and Engineering, South China University of Technology,
Guangzhou 510006, China (e-mail: cszhongguoxiang111@mail.scut.edu.cn;
201930330247@mail.scut.edu.cn; philip.chen@ieee.org).
Fagui Liu is with the School of Computer Science and Engineering, South
China University of Technology, Guangzhou 510006, China, and also with
the Department of New Networks, Peng Cheng Laboratory, Shenzhen 518000,
China (e-mail: fgliu@scut.edu.cn).
Jun Jiang is with the College of Information Science and Technology,
Nanjing Forestry University, Nanjing 210037, China (e-mail: junjiang@
ieee.org).
Bin Wang is with the Department of New Networks, Peng Cheng
Laboratory, Shenzhen 518000, China (e-mail: wangb02@pcl.ac.cn).
Digital Object Identifier 10.1109/TNSM.2024.3353772

Fig. 1. Faults of the server cluster in SMD benchmark dataset. The red
metric curves in blue boxes indicate the faults. These faults are described as
anomalies of 9-th, 13-th, 14-th, and 15-th metrics, which also are referred to
as root causes.

system must continuously improve the availability and reliability of cloud services [1], [2]. However, accidental faults,
such as network delay [3], [4] and resource hog [5], [6],
frequently pose a substantial threat to the system running.
These faults cause the anomalous behaviors of the related
monitoring metrics [7], [8], which is shown in Fig. 1. The
operation system always discovers the faults by detecting
the anomaly of running data and then starts the corresponding fault tolerance solutions [9], [10], [11]. In other words,
anomaly detection is the first step to actively removing the
faults [12], [13]. The powerful detection result maintains
a solid foundation of higher availability and reliability in
cloud [14], [15].
The autoencoder-based anomaly detection algorithm combines the robust neural network to mine the intrinsic patterns,
which has significantly been concerned [16], [17], [18], [19].
More recent literature has also demonstrated that the encoderdecoder architecture outperforms traditional methods by a
large margin, such as Bagel [20] and USAD [21]. The
autoencoder-based method adopts the historical normal data
to train the representation network. The reconstruction error
provided by this representation is regarded as an anomaly
score. The online testing data with a larger anomaly score

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1932-4537 
See https://www.ieee.org/publications/rights/index.html for more information.

3250

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 3, JUNE 2024

indicates the presented anomaly. More proposed works focus
on optimizing the above-mentioned procedures [22], [23].
However, there still exist two main challenges, which are in
the following:
• The first challenge is related to feature representation,
which ignores the historical anomaly samples. For universal anomaly detection applications, normal samples
constitute the majority of the training sample owing to the
higher overhead of labeling scarce anomaly samples. The
feature representation rebuilds the normal sample, which
only formulates the intra-class features. Both intra-class
features of anomalies and inter-class features between
two kinds of samples are absent. The anomaly detection
in the cloud is a special case with complete running documents [11], [24], [25]. The recorded anomalous events
are abundant, which can provide feature representation
with adequate and cheap labeled anomaly samples.
• The second challenge comes from poor self-adaptive
ability in online detection. Cloud resource utilization is
in a constant state of change due to various practical
requirements. For example, if the computing-intensive
task is uploaded, more computing nodes are in need. The
CPU available percentage becomes lower. Subsequently,
the cloud user deploys network-intensive tasks. The
network byte sent rate will be higher. In the meanwhile,
the metrics about computing return to normal. Without
the self-adaptive ability, anomaly detection identifies the
lower CPU available percentage and higher network byte
sent rate as anomaly behaviors.
In this paper, we overcome these limitations and propose
an improved autoencoder framework BroadCAE, which integrates contrastive learning and broad network. For the first
challenge, contrastive loss is introduced to formulate the
latent variable in the autoencoder. The anomaly samples in
an embedding space are closer to each other as possible,
which is the same operation for normal samples. Inversely,
the training samples from different classes are separated. The
feature representation extracts both intra-class and inter-class
features, which further optimizes the margin between normal
and anomaly samples. To tackle the second challenge, the
BroadCAE incorporates the broad network module to develop
dynamic threshold selection. We first apply the anomaly scores
to calculate the pseudo thresholds. Specifically, the anomaly
bias shrinks the anomaly scores of anomalies as their pseudo
thresholds, while the normal bias amplifies the anomaly scores
of normal samples to develop the normal-sample thresholds.
Thus, the violation of the actual label would be minimal.
Then we attain the threshold pattern by feeding the pseudo
thresholds and initial samples into the broad network. In the
online testing stage, this trained broad learning model outputs
the individual threshold according to the coming sample. A
portion of the network weight is updated while the actual label
of the testing sample is acquired, which fits the need for the
new detection setting.
The major contributions of our proposed BroadCAE are:
• The BroadCAE innovates anomaly samples into the
traditional normal-only encoder-decoder framework,
which develops both inter-class and intra-class features

to empower the representation of cloud anomaly
detection.
• The BroadCAE adopts the broad network without deep
structure to dynamically generate thresholds in the light
of the coming samples, which provides a different perspective to refine the anomaly detection system.
• In validation experiments, our BroadCAE outperforms
other comparative algorithms, which demonstrates the
applicability of BroadCAE for cloud anomaly identification. The open-source codes1 will continue to motivate
the research in cloud anomaly detection.
The rest of the paper is organized as follows. Section II
reviews the BroadCAE’s related work. The design details of
BroadCAE are discussed in Section III, containing problem
formulation, BroadCAE’s overview, contrastive autoencoder,
broad network-based dynamic threshold selection, and
BroadCAE’s pseudo code. The experiment in Section IV
validates the effectiveness of BroadCAE by answering three
research questions. Finally, the conclusion is presented in
Section V.
II. R ELATED W ORK
A. Background of Cloud Anomaly
The anomaly in the cloud is a running behavior that deviates
from the normal system setting on account of fault. According
to different fault locations, cloud anomaly can be divided into
internal and external behavior. The external factor caused by
other services leads to an external anomaly. For example, the
cloud SaaS application downloads a large file, which brings
about network congestion [26]. Besides, cyber attack [27] is
the most common external fault. Internal processes induce
internal anomalies, such as authentication failure and network
packet loss. The operation system uses several reactive and
proactive fault tolerance methods, such as auto-scaling [5],
to remove the presented fault [28], which avoids further
affecting the regular cloud services. Before that, the operation
system still needs to consider identifying the fault through
the anomaly. They always analyze the anomaly state by
monitoring metric, log, and trace. Particularly, the monitoring
metric is easier to embed and reveal the most comprehensive
data pattern. In this paper, we focus on the monitoring-metricbased anomaly detection algorithm.
B. Cloud Anomaly Detection Algorithm
In the early stage, the cloud operation system primarily
adopts keyword-based [29] and statistics-based [30] anomaly
detection methods. The keyword-based method identifies the
anomaly recorded in the log by matching the related words,
such as ERROR and FAILURE [31]. The statistics-based
methods focus on several key performance indicators [32].
If their values exceed a certain setting threshold, an alert is
triggered. The keyword-based and statistics-based methods are
only suitable for anomalies with relatively simple patterns.
With the development of artificial intelligence operations in
the cloud, more machine-learning-based anomaly detections
1 https://github.com/zhongguoxiang/BroadCAE

ZHONG et al.: DETECTING CLOUD ANOMALY VIA BROAD NETWORK-BASED CONTRASTIVE AUTOENCODER

TABLE I
T HE C OMPARISON OF R ELATED A LGORITHMS AND O UR B ROAD CAE

are deployed [31], [33], [34], [35]. They always depend
on the distribution divergence between normal and anomaly
samples. For instance, the local outliers factor (LOF) [36]
believes that the distribution density of normal is higher
than the anomaly sample’s. The one-class support vector
machine (OCSVM) [37] considers that all normal samples
are in a hyper-sphere. However, these methods have limited feature modeling ability and are not robust enough.
As a result, they are even invalidated when the largescale samples do not follow the corresponding assumed
distribution.
At the same time, the cloud architecture is becoming larger.
The coordination between cloud components steadily grows,
leading to more monitoring data. It is difficult for the classic
machine-learning-based method to meet the practical application requirements. The root cause is their weak modeling of
mining data patterns. The autoencoder (AE) algorithm [38] is
an effective solution that formulates massive historical normal
sample data to obtain deep-level features. More potential
patterns can be employed to identify complex cloud anomalies.
Some proposed works improve the vanilla autoencoder, which
has obvious advantages in terms of detection efficiency and
accuracy. For instance, Donut [39] formulates the anomalies
and missing points into the ELBO of variational autoencoder (VAE) [40], which outperforms the random-forest-based
Opprentice [41]. As an improved method of Donut, Bagel [20]
handles the time information based on the conditional VAE
(CVAE) [42]. The superiority of Bagel in detection accuracy is also significant. Both Donut and Bagel modify the
loss function. In addition, other approaches concentrate on
developing the network architecture. The VAE-LSTM [43]
introduces long short-term memory (LSTM) into the backbone
network of VAE for modeling metric-based time series. The
UASD [21] inherits the encoder-decoder architecture and adds
one more decoder as a discriminator for adversarial training.
The Anomaly Transformer [22] and TranAD [23] integrate
the attention mechanism [44], which enjoys long-term series
modeling.
As displayed in Table I, our BroadCAE goes beyond
the previous autoencoder-based algorithm and considers the
anomaly sample for formulating more features. It is also the
first time to unify anomaly and normal sample patterns under
the autoencoder representation.

3251

C. Broad Network
The broad network [45] is an improved single-layer feedforward neuron model. Without the deep architecture, the
broad network still has universal approximation properties [46]
and is much faster with credible classification accuracy. The
weight in the broad network is solved by the pseudoinverse
rather than gradient-descent-based methods used in deep
networks. The generalization ability of the broad network is
improved through the broad expansion. More broad network
variants are proposed. For example, fuzzy broad learning
system [47] introduces the Takagi-Sugeno fuzzy approach
into the feature node. Stacked broad learning system [48]
develops the incremental flatted framework to deep network,
which outperforms the deep residual network in experimental
comparison. Although the broad network is still in the early
developing stage, some application researches continuously
model this novel network. The broad network combines the
graph neural network to achieve the emotion recognition [49].
The semi-supervised broad network is built for spammer
detection in social communication networks [50].
Unlike the above broad network application, our BroadCAE
unifies the deep-network-based autoencoder and broad
network for cloud anomaly detection. For the broad network,
we apply the increment of input samples, which is designed
for self-adaptive ability in the online setting.
III. M ETHODOLOGY
A. Problem Formulation
Suppose there are several metrics for monitoring cloud
components. We attain their labeled history running data as
D = {(xi , yi )|i = 1, . . . , N },
xi = [xi1 , xi2 , . . . , xid ]T ∈ Rd ,
yi ∈ {+1, −1},

(1)

where xi represents the i-th sample in D and yi is the label
of xi . The N is the number of samples in D. The d indicates
the number of monitoring metrics. The “+1” and “−1” are
the label marks of normal and anomaly samples, respectively.
The autoencoder-based anomaly detection algorithm regards
D as the training dataset and formulates the feature representation with D. The representation of this anomaly detector
contains encoder fe and decoder fd . For the normal sample
(xi , yi = +1) ∈ D, the encoder fe transforms xi into latent
variable Z.
zi = fe (xi ), zi ∈ Z ,
yi = +1,

(2)

where zi is the latent variable corresponding to xi . Then, the
decoder fd inversely transforms zi into xi :
xi = fd (zi ), xi ∈ Rd ,

(3)

where xi is the reconstruction of xi . What is more, both fe
and fd are in the form of deep neural networks. We optimize

3252

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 3, JUNE 2024

Fig. 2. The overview of BroadCAE. The training-use historical dataset includes the labeled normal and anomaly samples in cloud computing. Our BroadCAE
consists of contrastive-learning-based CAE and broad network-based dynamic threshold selection. The CAE improves the feature representation by adding
anomaly samples. The dynamic threshold selection has the powerful self-adaptive ability for online detection. The update procedure () empowers the
broad network.

the objective representation by minimizing the following
reconstruction loss function Lr :
N



1 
x i − x  2 ,
L = Lr X , X  =
i 2
N

(4)

if the threshold value is too small, the predicted anomaly
samples may contain more normal ones. The autoencoderbased methods need the self-adaptive threshold selection,
which offers the dynamic threshold.

i=1

where  · 22 denotes the metric of similarity in Euclidean
distance. Because the normal sample is always far from the
anomaly ones, the reconstruction error of the normal sample is
smaller than the anomaly’s. This divergence in reconstruction
error is the core of achieving the autoencoder-based anomaly
detector. The reconstruction error is referred to as the anomaly
score. Given the online testing sample xiu ∈ D u where D u
represents the online testing dataset, ŷiu is the predicted label
of xiu . The autoencoder-based anomaly detector outputs the
predicted label as

+1, ASiu ≤ θ;
u
ŷi =
−1, ASiu > θ;
ASiu = xiu − fd [fe (xiu )]22 ,

(5)

where θ is a threshold and ASiu is the anomaly score
of xiu .
Challenges: (i) Ignoring the historical anomaly samples in
training the feature representation. From Equation (2), only the
normal sample is formulated by fe . Actually, anomaly samples
also can enlarge the reconstruction divergence. In detail,
The inter-class feature between anomaly and normal samples
requires that the latent variable of anomaly samples should be
separated as possible. The intra-class feature from anomaly
samples distinguishes the overlapping normal samples, which
enhance the robustness of fe and fd . (ii) Poor self-adaptive
ability for online detection. In Equation (5), the threshold θ is
fixed, which does not enjoy dealing with the online continual
change samples. A small portion of anomaly samples will be
detected if the threshold value is larger enough. In contrast,

B. Overview
This paper focuses on the above challenge and proposes
the BroadCAE that introduces contrastive learning and broad
network. The overview of BroadCAE is shown in Fig. 2.
The historical running data of normal and anomalous cloud
components are collected. The data preprocessing includes
padding and normalization, which is omitted in the overview.
The contrastive autoencoder (CAE) innovates contrastive
learning into the autoencoder. The autoencoder reconstruct
X = [xi ]1×N as X  = [xi ]1×N . The feature representation
ignores the anomaly samples, which ascribes to the dimension
reduction transformation in the encoder. For the latent variable
Z = [zi ]1×N , the divergence of normal and anomaly samples
should be more obvious. Thus, we add the contrastive loss Lc
to the latent variable. The contrastive loss uses the constraint
about sample label Y = [yi ]1×N and latent variable Z.
The broad network combines dynamic threshold selection,
which is designed for self-adaptive online detection. The
combination of anomaly score X − X  22 and sample label
Y calculates the pseudo label Θ∗ for threshold selection. The
predicted threshold Θu is provided while the online coming
sample X u = [xiu ] is fed into the trained broad network.
Furthermore, the relationship between Θu and anomaly score
of X u decides the predicted label Ŷ u = [yiu ]. The broad
network weight can be updated when the actual label Y u of
X u is acquired. It is noteworthy that only the network weights
related to the online coming samples are retrained. The broad
network avoids updating the whole network weights, which is
a great substitute for the deep network.

ZHONG et al.: DETECTING CLOUD ANOMALY VIA BROAD NETWORK-BASED CONTRASTIVE AUTOENCODER

Fig. 3.

Potential deployment of BroadCAE in microservice.

For example, Fig. 3 describes our BroadCAE, which is
deployed into the cloud-based microservice system. The monitoring data of each microservice is collected and delivered to
the database. The detector BroadCAE identifies the anomaly
data from the database and transmits the alert signal to
operations.
C. Contrastive Autoencoder
The general autoencoder-based method builds up the representation by training with normal samples. The extracted
features in the representation can be regarded as intra-class
ones of normal samples. The anomaly samples are discovered,
which follows the principle “normal is not anomalous”. In
other words, the normal-sample intra-class features provide the
manifold of normal. The testing sample far away from this
manifold is not normal. The approaches only model the seen or
occurred normal samples. However, the novel normal pattern
constantly emerges in cloud operation. It is unachievable to
model all types of normal samples under the evolving cloud.
The representation manifold only the training normal samples,
which will gradually lose efficacy in the future. Besides, in the
cloud environment, the deployed cloud component needs more
preliminary tests. The anomaly events supply more anomaly
samples to optimize the autoencoder. The anomaly-sample
intra-class features indicate whether the sample is not normal.
The inter-class features between normal and anomaly samples
lead to the margin for dividing the samples. The additional
intra-class and inter-class features enhance the representation.
Thus, it is necessary to incorporate anomaly samples into
the representation. The CAE in our BroadCAE introduces
contrastive loss for formulating the anomaly samples. The contrastive loss focuses on the lower-dimensional latent variable,
which is compacted by the encoder fe . Suppose that (xi , yi ) ∈
D and (xj , yj ) ∈ D are given, their latent variables are
 
(6)
zi = fe (xi ), zj = fe xj .
The contrastive loss is
N



1 

2

2
Lc =
1
−
y
S
max
0,
m
−
S
, (7)
+
y
ij
ij
ij
ij
2N 2
i,j =1

where Sij = zi − zj 22 is the Euclidean-distance similarity
between zi and zj . The max(·, ·) returns the largest value.
The m > 0 is the classification margin about distance. In our
experiments, m = 2. The pairs of samples far away from this

3253

Fig. 4.
Distribution of anomaly score using different loss functions. In
(a), the majority of anomaly samples are covered by normal samples, which
indicates that the anomaly-score divergence is too smaller. However, in (b),
more anomaly samples have larger anomaly scores than normal samples,
which contributes to anomaly identification.

margin do not contribute to the contrastive loss. If xi and xj
are in the same classes, we annotate the pseudo label yij = 0.
While they belong to different classes, the pseudo label is
shown as yij = 1.

0, yi = yj

yij =
, Y  = yij
(8)
1, yi = yj
N ×N .
In the first part of Lc , the fr strains every nerve to pull closer
points, which are from the same class. The intra-class features
of normal and anomaly samples are extracted. The second part
aims at separating samples into different classes by a large
margin. This operation enjoys the inter-class features between
normal and anomaly samples.
During the training stage, all labeled training samples are
fed into fe and fd , which are optimized by contrastive loss
rather than reconstruction loss.
L = Lc (X , Y ).

(9)

On the one hand, both contrastive loss and reconstruction loss
can formalize the normal-sample intra-class features. In the
meanwhile, beyond the reconstruction loss, the contrastive loss
develops the anomaly-sample intra-class and anomaly-normal
inter-class features. On the other hand, the latent variable
divergence between normal and anomaly samples achieves a
more powerful effect than reconstruction divergence, using the
identical decoder. For example, Fig. 4 displays the anomaly
score of the first SMD subset. The contrastive loss enlarges
the anomaly score of anomaly samples.
D. Dynamic Threshold Selection Based on Broad Network
Suppose that G(·) is the dynamic threshold selection in our
BroadCAE. As for different inputs xiu and xju , their output
thresholds are also different.
 
θiu = G(xiu ), θju = G xju ,
θiu = θju .

(10)

For the self-adaptive ability, G(·) should be update to reflect
the online coming sample. The classical deep-network-based
threshold selection algorithm repeats the training procedure
to update the network weights. After several above replications, the knowledge about the previous training samples

3254

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 3, JUNE 2024

Fig. 5. The overview of broad network. This flattened network has only one input layer and one output layer. There are k feature mapped nodes and r
enhancement nodes in the input layer. The network weight is solved by pseudoinverse. The increment of xiu is in green.

will disappear, which is called as catastrophic forgetting [51].
The G(·) addresses this problem by incorporating the broad
network, not the deep network. As shown in Fig. 5, the broad
network consists of two main components: feature mapped
node and enhancement node. Given X = [xi ]1×N as the
training sample, the k-th feature mapped node projects X as


Fk = φ XWfk + βfk ,
(11)
where Wfk and βfk are the initial weights and bias of
Fk , respectively. The φ is a mapping function. The F k =
[F1 , . . . , Fk ] denotes all the first k-th feature mapped nodes
in the form of concatenation. The output of F k is mapped by
enhancement nodes. The r-th enhancement node is


(12)
Hr = ξ F k W h r + βh r ,
where Whr and βhr are the initial weights and bias of Hr ,
respectively. The ξ is a mapping function. The first r-th
enhancement nodes are also in the form of concatenation.
H r = [H1 , . . . , Hr ].

(13)

The broad network has k feature mapped nodes and r enhancement nodes, which is formulated as
Θ∗ = [F1 , . . . , Fk | H1 , . . . , Hr ]W
= Fk | Hr W ,

(14)

where Θ∗ = [θi∗ ]1×N

is the threshold training label of X in
G(·). The W is the network weight for the broad network.
Different from the deep network, the broad network attains the
optimal W through Moore-Penrose generalized inverse theory.
k

W = F |H

r

+

∗

Θ ,

(15)

where [F k | H r ]+ denotes the pseudoinverse of [F k | H r ].
Suppose that Ark = [F k | H r ], we have

−1
(Ark )+ = lim λI + AAT
AT .
(16)
λ→0

As for Θ∗ = [θi∗ ]1×N , we can not directly attain from the
previous problem setting. Instead, we develop the supervised
pseudo threshold.

β+1 · ASi , yi = +1,
∗
θi =
β−1 · ASi , yi = −1,

2
ASi = xi − xi 2 ,
(17)
where β−1 and β+1 are anomaly bias and normal bias,
respectively.
0 < β−1 < 1, β+1 ≥ 1.

(18)

In this solution, it is not hard to show
min

N


|yi − yi∗ | = 0,

i=1

s.t. yi∗ =



+1, ASi ≤ θi∗ ,
−1, ASi > θi∗ ,

(19)

where yi∗ is the label of xi provided by pseudo threshold.
Thus, the generative pseudo threshold is practicable.
After finishing the training of broad network, the dynamic
threshold selection G(·) will enter the online detection to
identify the presented anomaly. Given the online coming
sample xiu ∈ D u , the G(·) follows
θiu = G(xiu ),

+1, ASiu ≤ θiu ,
u
ŷi =
−1, ASiu > θiu .
(20)
while the predicted label ŷiu is equal to the actual label yiu ,
the accurate prediction offer the correct sample pattern. The
broad network in G(·) can be updated. The increments of the
feature mapping node and enhancement node are


F̂k = φ xiu Wfk + βfk ,


Ĥr = ξ F̂ k Whr + βhr ,
(21)

ZHONG et al.: DETECTING CLOUD ANOMALY VIA BROAD NETWORK-BASED CONTRASTIVE AUTOENCODER

3255

Algorithm 1 Training Algorithm of BroadCAE
Input: Encoder fe ; Decoder fd ; Training sample X; Training
label Y; Number of feature mapped node k; Number of
enhancement node r; Random mapping φ and ξ; Iteration
limitation Ne .
Output: Optimized encoder fe ; Optimized decoder fd ; Broad
network weight W; Network pseudoinverse (Ark )+ .
1: Initialize the network weights of fe and fd ;
2: Initialize the weights and biases of φ and ξ;
3: n ← 1;
4: repeat
5:
Feed X into fe and fd ;
6:
Calculate the contrastive loss Lc ;
7:
Optimize fe and fd with loss function L = Lc (X , Y );
8:
n ← n+1;
9: until (n = Ne ).
10: Generate the pseudo threshold Θ∗ ;
11: Fed X into feature mapped node Fk ;
12: Project F k = [F1 , . . . , Fk ] by enhancement node Hr ;
13: Deduce the pseudoinverse (Ark )+ and network weight W.

Algorithm 2 Testing Algorithm of BroadCAE
Input: Optimized encoder fe , Optimized decoder fd ; Broad
network weight W and pseudoinverse (Ark )+ ; Random
mapping φ and ξ; Testing sample X u .
Output: Predicted label Ŷ u .
1: Reconstruct X u through fe and fd ;
2: Compute the anomaly score of X u ;
3: Calculate the threshold of X u ;
4: Attain the predicted label Y u
5: while Ŷ u = Y u do
6:
Update pseudoinverse (Ark )+ as (Ârk )+ ;
7:
Update network weight W as Ŵ ;
8: end while

where F̂ k = [F̂1 , . . . , F̂k ] are the first k-th incremental
mapping features of xiu . The Ark in the initial network is
transformed as

O(N 2 ). The dynamic threshold selection is between Line 10
and Line 13. The dot-product for computing the pseudoinverse
makes the time complexity of dynamic threshold selection
O(N 2 ). Thus, our BroadCAE achieves the quadratic time
complexity. In Algorithm 2, our goal is to predict the label of
X u . Besides, the threshold selection adapts to the new coming
samples by updating the network weight and pseudoinverse,
which is presented from Line 5 to Line 8.

Ârk =

Ark
,
ÂT

(22)

where ÂT = [F̂ k |Ĥ r ] and Ĥ r = [Ĥ1 , . . . , Ĥr ]. The update
pseudoinverse is
 +
Ârk
= (Ark )+ − B D T |B ,
(23)
where D T = ÂT (Ark )+ ,
+

BT =

, C = 0,
(C )

−1  
+
T
r
1+D D
Ak D , C = 0,

(24)

and C = ÂT − D T Ark . The updated network weight is


Ŵ = W + θiu∗ − ÂT W B,
(25)
where θiu∗ is the pseudo threshold of xiu . From the
Equation (25), we can apply the initial network weight W and
initial pseudoinverse Ark to calculate the Ŵ . The previous
knowledge about W and Ark in the initial network are retained,
which avoids catastrophic forgetting. In the meanwhile, the
new pattern about the new xiu is described by ÂT , which
adapts quickly to the new developing environment.
E. Implementation
The implementation of our BroadCAE is composed of
training (Algorithm 1) and testing (Algorithm 2) blocks. All
of the input of these two Algorithms can be directly calculated
in the neural network. In Algorithm 1, we consider the feature
representation of CAE from Line 3 to Line 9. There are
N 2 pairs training samples. The quadratic computation about
similarity in Lc causes the time complexity of CAE to be

TABLE II
T HE C HARACTERISTICS OF F OUR E XPERIMENTAL DATASETS

IV. E XPERIMENT
We first introduce the experimental setting, including
datasets, performance metrics, and experimental details. Then,
the following research questions (RQ) about validating our
BroadCAE are answered by a series of experiments. Their
experimental results and analysis are displayed.
RQ1: How about the overall performance of BroadCAE
in cloud anomaly detection?
RQ2: How about the impact of parameters in BroadCAE?
RQ3: How about the effectiveness of each component in
BroadCAE?
A. Datasets
We conduct the experiments on four benchmark datasets,
including MBD [52], EMOS, SMD [53], and ASD [54]. These
datasets are collected from different cloud environments. The
first dataset is from a Hadoop-based distributed cluster. The
second one is related to a benchmark microservice-based
system.2 The last two datasets correlate with the server in the
cloud. The characteristics of these datasets are in Table II.
The MBD reflects the running behavior of five cluster
nodes, which process the big data batch. To imitate the
actual setting, the researchers randomly upload the large-scale
2 https://github.com/FudanSELab/train-ticket

3256

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 3, JUNE 2024

workload using HiBench.3 The faults of the CPU, network,
and application are randomly injected into the file system.
There are 26 monitoring metrics for each node, including CPU,
disk, memory, network, and process.
The EMOS presents the status of 41 microservices, which
service the train ticket booking application.4 The faults are
injected by Chaosblade5 and iPerf.6 These faults include CPU
hog, memory hog, disk input, disk output, DDOS delay, and
packet loss. We monitor four representative metrics, including
CPU usage, RAM usage, Net out, and Net in. All faults and
metrics are used in some published works [5], [52]. For the
purpose of research, we encourage anyone to use this dataset.
More details are provided here.7
The SMD is provided by a commercial computing cluster,
which includes 28 machines. During the 5-week-long period,
the collected data consists of two subset components. The first
half is used for training, and the remaining half is regarded as a
testing subset. However, only the testing subset provides both
the label and the dimensions of the anomaly. For performance
evaluation, we adopt the testing subset in our experiments.
The ASD describes the status of 12 servers in a large
Internet company. To avoid the concept drifts, the stable
workloads run on each server during a 45-days-long period.
We also utilize the testing subset of ASD. However, the ASD
contains fewer metrics, which differs from the SMD. The
monitoring metrics are related to CPU, memory, network, and
virtual machine.
B. Performance Metrics
In general, recall (R), precision (P), and f1-score (F1) are
used to evaluate anomaly detection algorithm performance.
The R focuses on presenting the accuracy of identifying
the goal samples. The P considers that the presented goal
samples are detected as more as possible. The F1 is introduced
to keep the balance between R and P. However, for more
comprehensive evaluation [21], [53], we import the macro R
(R̄), macro P (P̄ ), and macro F1 (F¯1) in this paper.
1
1
R, P̄ =
P,
R̄ =
2
2
2 · R̄ · P̄
F¯1 =
.
(26)
R̄ + P̄
C. Experimental Details
The BroadCAE is implemented in a Python program.
Both encoder fe and decoder fd with deep architectures
are employed through the Pytorch package. The fe contains
a 4-layer multi-layer perceptron (MLP), the size of output
features of which are d → 1024 → 512 → 256. The ReLU [55]
and batch normalization [56] are added into each layer. The
fd is made up of a 3-layer MLP (256 → 128 → d ) with batch
normalization. The ReLU is also added into the first layer of
fd . The fe and fd are optimized by the ADAM optimizer [57]
3 https://github.com/Intel-bigdata/HiBench
4 https://github.com/FudanSELab/train-ticket
5 https://github.com/chaosblade-io/chaosblade
6 https://iperf.fr/
7 https://github.com/zhongguoxiang/BroadCAE

TABLE III
T HE C HARACTERIZATIONS OF E XPERIMENTAL C OMPUTER S ERVER

with 10−3 initial learning rate and step-scheduler with step
size of 0.5. We run 100 epochs, where the size of the batch is
256. The other hyper-parameters of our BroadCAE are listed
in the following.
• Number of feature mapped nodes k = 35.
• Number of enhancement nodes r = 500.
• Anomaly bias β−1 = 0.01.
• Normal bias β+1 = 2.
For four datasets, we randomly split all samples into training
and testing subsets with a ratio of 5:5. Then, we follow the
above-mentioned parameters and repeat the identical procedure for one hundred independent runs. The mean of these
replications can be regarded as the final experimental results.
The comparative baselines also follow the same operations.
Some comparative anomaly detection methods only output the
anomaly score of the testing sample. The threshold selection
is absent. We plot the ROC curve [58] and search for the best
detection result.
The BroadCAE and other comparative anomaly detection
algorithms are tested in the server computer, which equips with
one NVIDIA GeForce RTX 3080. More details of experiment
equipment are shown in Table III.
D. Research Questions
We conduct the experiments about three research questions.
The experimental results and analysis should validate the
effectiveness of BroadCAE.
RQ1: How about the overall performance of
BroadCAE in cloud anomaly detection?
The RQ1 is designed to demonstrate whether BroadCAE
can outperform the state-of-the-art baseline approaches in
cloud anomaly detection. There are 12 comparative algorithms
used in this experiment. Among them, the LOF, OCSVM,
and iForest are proposed in the earlier period. With the rapid
development of deep learning, autoencoder-based methods are
more and more applied because of their strong generalization.
The AE, VAE, and CVAE are the baseline algorithms. The
Bagel are adapted from CVAE. The USAD and SaVAE-SR
innovate the training style, which is inspired by the adversarial
learning theory of GAN [62]. Both TranAD and Anomaly
Transformer are developed from the improved autoencoderbased architecture Transformer [44]. The CAE-M utilizes the
autoencoder-based architecture to mine the semantics features.
These comparative algorithms are introduced as follows:
• LOF [36]: The local reachability density (LRD) about
nearest neighbor samples is first released to measure the
anomaly degree. The higher values of LDR, the less
anomalous the sample is.

ZHONG et al.: DETECTING CLOUD ANOMALY VIA BROAD NETWORK-BASED CONTRASTIVE AUTOENCODER

3257

TABLE IV
T HE OVERALL P ERFORMANCE R ESULTS FOR O UR B ROAD CAE AND OTHER C OMPARATIVE M ETHODS IN F OUR B ENCHMARK DATASETS

• OCSVM [59]: The hyper-sphere is optimized in the
training dataset. The testing sample outside of the hypersphere is anomalous.
• iForest [60]: From its authors’ view, the anomaly is easier
to be isolated. The iForest adopts isolation instead of
distance and density to identify anomaly samples.
• AE [38]: Both the encoder and the decoder with a
deep network rebuild the samples. The back-propagation
algorithm with reconstruction loss optimizes the network
weight. The reconstruction error presents the anomaly
score.
• VAE [40]: Based on AE, the latent variable is described
in the form of Gaussian distribution. The reconstruction
probability of KL divergence is added into the ELBO loss
function and further indicates how anomalous the testing
sample is.
• CVAE [42]: Being distinguished from AE and VAE,
CVAE formulates the model about the relationship
between the input latent variable, input sample, and its
label. In fact, the CVAE is one of the semi-supervised
encoder-decoder-based methods.
• Bagel [20]: Compared to Dount [39], Bagel includes time
information into CVAE and enhances the robustness in
detecting the time-related anomaly.
• USAD [21]: In the encoder-decoder architecture, it
imports the adversarial training by adding a decoder
block. At the same time, it also avoids collapse and nonconvergence phenomena.
• SaVAE-SR [14]: It draws its strength from combining
spectral residual technique and self-adversarial training
manner, which still follow the framework of VAE.
• TranAD [23]: The Transformer [44] is introduced.
The vanilla attention mechanism is designed for

time-dependency relationship. Both the self-condition
approach and adversarial learning stabilize the training
procedure.
• Anomaly Transformer [22]: The Transformer architecture
is improved by developing a new anomaly-attention
mechanism. The association discrepancy and minimax
strategy enlarge the divergence between normal and
anomaly samples.
• CAE-M [61]: The deep convolutional characterization
network is employed as a feature extractor. The attentionbased bidirectional LSTM and auto-regression provide
the final predicted result.
Table IV presents the overall performance results of our
BroadCAE and 12 baseline algorithms in four benchmark datasets. The superiority of our BroadCAE can be
observed, compared with other baseline comparative algorithms. Especially our BroadCAE gets the highest score of F¯1
and R̄ in all four datasets. However, the lower P̄ is recorded in
the MBD (84.44%), SMD (94.90%), and ASD (74.46%). The
imbalance between anomaly and normal samples results in this
situation. The proportion of correct identification of normal
samples is larger than that of abnormal samples. The confusion
matrices of our BroadCAE detection results are displayed
in Fig. 6, which provides more details. As for EMOS, our
BroadCAE achieves the best P̄ (91.76%), which ascribes to
the less false negative samples.
In the next step, we further discuss comparative anomaly
detection algorithms. It is noteworthy that the deep encoderdecoder-based methods always outperform the traditional
machine-learning-based anomaly detection algorithms. For
example, Bagel attains the best P̄ in MBD (93.25%), SMD
(96.16%), and ASD (83.62%), although the quantity of predicted anomaly samples is smaller. The CAE-M and Anomaly

3258

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 3, JUNE 2024

Fig. 6. Confusion matrices on four datasets. The normal and anomaly samples
belong to the positive and negative classes, respectively. A majority of normal
and anomaly samples are well identified, which results in the higher F¯1.

Transformer acquire the second-best F¯1 and R̄ in SMD and
ASD, respectively. For the EMOS, USAD attains the secondbest F¯1 (84.06%) and P̄ (84.77%), which SaVAE-SR get the
second-best R̄ (84.94%).
To illustrate the efficiency, we select six competitive
algorithms in detection accuracy, including Bagel, USAD,
SaVAE-SR, TranAD, Anomaly Transformer, and CAE-M.
The averaged training time, averaged testing time, and averaged memory used by these algorithms are regarded as
baseline results. As we know from Fig. 7, our BroadCAE
does not outperform the baseline about efficiency. Although
the training procedure of BroadCAE takes less time,
BroadCAE needs more testing time and memory in SMD
and ASD. This ascribes to the broad network-based threshold
selection.
RQ2: How about the impact of parameters in
BroadCAE?
The parameter always has an impact on BroadCAE’s
performance. The following parameters are discussed for
answering this RQ.
• Dimension of latent variable.
• Number of feature mapped nodes.
• Number of enhancement nodes.
• Anomaly bias.
• Normal bias.
We follow the advantage of the encoder-decoder architecture
to develop BroadCAE. The dimension of the latent variable
is involved with the feature extractor. If the dimension is
larger enough, information is abundant, and parameter tuning
becomes time-consuming. In contrast, if it is in a lowerdimensional space, limited features will be modeled, and
encoder representation may be invalidated. We apply one more

performance metric, area under the ROC curve (AUC), to
evaluate the impact of the latent variable dimensions. Fig. 8
presents the experiment results of all the experimental datasets,
which are achieved by different dimensions. We start from
32 dimensions, keeping the interval of 32 and up to 320
dimensions. As we increase the dimensions, the performance
of BroadCAE does not improve by a larger margin. For
example, the detection results about four evaluation metrics
become poorer in MBD. As for SMD, the value of F¯1, R̄,
and AUC are relatively steady. It is noteworthy that the AUC
of MBD, EMOS, and ASD have dropped. However, the F¯1 of
EMOS and ASD do not descend, which ascribes to dynamic
threshold selection.
The remaining parameters come from the dynamic threshold
selection, of which the first two are related to broad network
learning, and the others form the supervised pseudo threshold.
Because the AUC is always considered for feature representation, we only use F¯1, R̄, and P̄ as performance metrics to
evaluate the impact of these parameters.
In Fig. 9, the impact of different numbers of feature mapped
nodes is shown. We select up to 50 feature mapped nodes in
each experiment, starting from only 5. The F¯1 about ASD
achieves the maximum values and stops rising. As for MBD,
the F¯1 also improves with the increase of feature mapped
nodes. The P̄ of these two datasets keep the same pace as
well. In the view of R̄, the improvement is weak, although
more feature mapped nodes are added. In other words, more
network parameters can not bring more powerful detection
results. Considering the experiment setting, we recommend
that the number of feature mapped nodes is between 25
and 35.
In Fig. 10, we pay attention to the influence of enhancement
nodes. The number of enhancement nodes is between 100 and
1000 with an interval of 100. For the F¯1, the SMD presents
a growing tendency from 100 to 300. The improvement of P̄
in the SMD occurs again. For the R̄, the MBD also keeps an
upward trend. However, the P̄ about MMS is in fluctuation.
Besides, the EMOS in P̄ reaches the peak and then begins to
drop in the next stage. We deem the increasing feature mapped
node is not good at broad network generalization for learning
threshold patterns. The overfitting still exists. Considering the
actual setting, we recommend that the number of enhancement
nodes should be under 500.
In Fig. 11, we analyze the effect of different anomaly
biases. Before the anomaly bias is 0.2, all of the datasets
reach their peak of F¯1. After that, the ASD decreases. In
the meanwhile, MBD, EMOS, and SMD are still at the top.
With the decreasing of anomaly bias, the increase of R̄ in four
benchmark datasets is in the range of 2% to 8%. Inversely, the
P̄ is down by about averaged 3% with the smaller anomaly
bias. The anomaly bias should be between 0.01 and 0.1.
Fig. 12 displays how the normal bias impacts the
performance of BroadCAE. The value of normal bias starts
from 1.2 and is up to 3 with an interval of 0.2. For the
F¯1, MBD, SMD, and ASD present a growing tendency. The
EMOS achieves a peak and then decreases. The EMOS, MBD,
and ASD are at the peak of R̄ while the normal bias is 1.4.

ZHONG et al.: DETECTING CLOUD ANOMALY VIA BROAD NETWORK-BASED CONTRASTIVE AUTOENCODER

Fig. 7.

3259

Training time, testing time, and memory consumption of BroadCAE and baseline algorithm.

TABLE V
T HE E FFECTIVENESS OF DYNAMIC T HRESHOLD S ELECTION

Fig. 8.

Impact of latent variable dimension.

After the best normal bias, they fall sharply, which leads to
the decrease of EMOS’s F¯1. Similar to the F¯1, P̄ keeps an
upward trend with the larger normal bias. We suggest that the
normal bias is between 1.8 and 2.8.
RQ3: How about the effectiveness of each component
in BroadCAE?
Our design of BroadCAE is to optimize the feature representation and add the dynamic threshold selection. The
reconstruction loss Lr is replaced by contrastive loss Lc ,
which extracts both intra-class and inter-class features in
representation. The dynamic threshold selection generates the
different thresholds for different testing samples, instead of
the fixed value. To analyze the effect of the above-mentioned
components, we conduct ablation experiments.
1) Effect of contrastive loss. The experimental results
are displayed in Fig. 13. The F¯1, R̄, P̄ , and AUC are
referred to as performance metrics. The brown “L” denotes
the combination of “Lr ” and “Lc ”. The green “Lr ” and

red “Lc ” indicate the reconstruction loss and contrastive
loss, respectively. For F¯1, P̄ , and AUC, the “Lc ” outperforms the “Lr ” and “L”. However, the R̄ of “Lc ” in
MBD does not attain the improvement. The reason for this
phenomena is that broad-learning-based threshold selection
can cover the shortcoming of feature representation. Besides,
in some benchmark datasets, the result of “L” is improved
by a margin, which illustrates that the inter-class feature is
effective.
2) Effect of dynamic threshold selection. This part is
directly related to the identification of anomalies. The F¯1,
R̄, P̄ are used. In addition, we adopt detection accuracy
(Acc), a performance metric about the ground truth of normal
and anomaly samples in testing data. Table V displays the
experiment results. The “Dynamic” is the dynamic threshold
selection in our BraodCAE. The “Fixed A” denotes the
threshold that comes from the best result in the ROC curve.
The “Fixed B” denotes the 3-sigma criterion. Compared to
the " Fixed A” and “Fixed B”, the new “Dynamic” sees the
maximum 10.01% jump in F¯1 and the maximum 3.07% leap
in Acc. Form this reference’s view [46], broad learning is more

3260

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 3, JUNE 2024

Fig. 9.

Impact of the number of feature mapped nodes.

Fig. 10.

Impact of the number of enhancement nodes.

Fig. 11.

Impact of anomaly bias.

Fig. 12.

Impact of normal bias.

suitable to the online setting. In addition, we do not need to
consider the selection and combination of deep network blocs
while adopting broad learning. This is the reason why we

recommend broad-learning-based dynamic threshold selection.
In addition, for ASD, the “Dynamic” only acquires the 0.37%
improvement of F¯1.

ZHONG et al.: DETECTING CLOUD ANOMALY VIA BROAD NETWORK-BASED CONTRASTIVE AUTOENCODER

Fig. 13.

Effectiveness of contrastive loss.

V. C ONCLUSION
In this paper, we propose the cloud anomaly detector,
BroadCAE, which incorporates contrastive learning and broad
network under the autoencoder framework. The contrastive
loss enriches the representation by extracting additional
intra-class and inter-class features. The cloud anomaly and
normal sample are equally exploited. The broad network-based
dynamic threshold selection aims at the changing cloud environment. The learned threshold pattern provides the dynamic
threshold, instead of the fixed one. The experimental results
in four datasets illustrate that our BroadCAE outperforms
the comparative method, and the improved components of
BroadCAE are practical.
For cloud operation, the accuracy of the anomaly detector is
essential to address the fault. The BroadCAE can be regarded
as one of the state-of-the-art methods. In future works, we will
explore the following research points for application-driven
anomaly detection:
1) the classification of anomaly or system fault,
2) the location and cause root of anomaly or system fault.
R EFERENCES
[1] H. Jayathilaka, C. Krintz, and R. Wolski, “Detecting performance
anomalies in cloud platform applications,” IEEE Trans. Cloud Comput.,
vol. 8, no. 3, pp. 764–777, Jul.–Sep. 2020.
[2] D. Saxena, I. Gupta, A. K. Singh, and C.-N. Lee, “A fault tolerant
elastic resource management framework toward high availability of
cloud services,” IEEE Trans. Netw. Service Manag., vol. 19, no. 3,
pp. 3048–3061, Sep. 2022.
[3] M. Soualhia, F. Khomh, and S. Tahar, “A dynamic and failure-aware
task scheduling framework for Hadoop,” IEEE Trans. Cloud Comput.,
vol. 8, no. 2, pp. 553–569, Apr.–Jun. 2020.
[4] M. Zoure, T. Ahmed, and L. Réveillère, “Network services anomalies in
NFV: Survey, taxonomy, and verification methods,” IEEE Trans. Netw.
Service Manag., vol. 19, no. 2, pp. 1567–1584, Jun. 2022.
[5] T. Wang, W. Zhang, J. Xu, and Z. Gu, “Workflow-aware automatic
fault diagnosis for microservice-based applications with statistics,” IEEE
Trans. Netw. Service Manag., vol. 17, no. 4, pp. 2350–2363, Dec. 2020.
[6] S. Kardani-Moghaddam, R. Buyya, and K. Ramamohanarao, “ADRL:
A hybrid anomaly-aware deep reinforcement learning-based resource
scaling in clouds,” IEEE Trans. Parallel Distrib. Syst., vol. 32, no. 3,
pp. 514–526, Mar. 2021.

3261

[7] L. Yang and A. Shami, “A multi-stage automated online network
data stream analytics framework for IIoT systems,” IEEE Trans. Ind.
Informat., vol. 19, no. 2, pp. 2107–2116, Feb. 2023.
[8] G. Zhong, F. Liu, J. Jiang, and C. L. P. Chen, “CauseFormer:
Interpretable anomaly detection with stepwise attention for cloud service,” IEEE Trans. Netw. Service Manag., early access, Jul. 31, 2023,
doi: 10.1109/TNSM.2023.3299846.
[9] Z. Zou, Y. Xie, K. Huang, G. Xu, D. Feng, and D. Long, “A docker
container tnsm-zhong-3353772 isolation forest,” IEEE Trans. Cloud
Comput., vol. 10, no. 1, pp. 134–145, Jan.–Mar. 2022.
[10] Y. Song, R. Xin, P. Chen, R. Zhang, J. Chen, and Z. Zhao, “Identifying
performance anomalies in fluctuating cloud environments: A robust
correlative-GNN-based explainable approach,” Future Gener. Comput.
Syst., vol. 145, pp. 77–86, Aug. 2023.
[11] J. Soldani and A. Brogi, “Anomaly detection and failure root cause
analysis in (micro) service-based cloud applications: A survey,” ACM
Comput. Surv., vol. 55, no. 3, pp. 1–39, 2023.
[12] Y. Chen et al., “Outage prediction and diagnosis for cloud service
systems,” in Proc. World Wide Web Conf., 2019, pp. 2659–2665.
[13] G. Fan, L. Chen, H. Yu, and D. Liu, “Modeling and analyzing dynamic
fault-tolerant strategy for deadline constrained task scheduling in cloud
computing,” IEEE Trans. Syst., Man, Cybern., Syst., vol. 50, no. 4,
pp. 1260–1274, Apr. 2020.
[14] Y. Liu, Y. Lin, Q. Xiao, G. Hu, and J. Wang, “Self-adversarial variational
autoencoder with spectral residual for time series anomaly detection,”
Neurocomputing, vol. 458, pp. 349–363, Oct. 2021.
[15] M. S. Islam, W. Pourmajidi, L. Zhang, J. Steinbacher, T. Erwin, and
A. Miranskyy, “Anomaly detection in a large-scale cloud platform,” in
Proc. IEEE/ACM 43rd Int. Conf. Softw. Eng. Pract. (ICSE-SEIP), 2021,
pp. 150–159.
[16] L. Li, J. Yan, H. Wang, and Y. Jin, “Anomaly detection of time
series with smoothness-inducing sequential variational auto-encoder,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 32, no. 3, pp. 1177–1191,
Mar. 2021.
[17] A. Garg, W. Zhang, J. Samaran, R. Savitha, and C.-S. Foo, “An evaluation of anomaly detection and diagnosis in multivariate time series,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2508–2517,
Jun. 2022.
[18] T. Zhao, T. Jiang, N. Shah, and M. Jiang, “A synergistic approach
for graph anomaly detection with pattern mining and feature learning,”
IEEE Trans. Neural Netw. Learn. Syst., vol. 33, no. 6, pp. 2393–2405,
Jun. 2022.
[19] G. Zhong, F. Liu, J. Jiang, B. Wang, and C. L. P. Chen, “Refining oneclass representation: A unified transformer for unsupervised time-series
anomaly detection,” Inf. Sci., vol. 656, Jan. 2024, Art. no. 119914.
[20] Z. Li, W. Chen, and D. Pei, “Robust and unsupervised KPI anomaly
detection based on conditional variational autoencoder,” in Proc. IEEE
37th Int. Perform. Comput. Commun. Conf. (IPCCC), 2018, pp. 1–9.
[21] J. Audibert, P. Michiardi, F. Guyard, S. Marti, and M. A. Zuluaga,
“USAD: UnSupervised anomaly detection on multivariate time series,”
in Proc. 26th ACM SIGKDD Int. Conf. Knowl. Discov. Data Min., 2020,
pp. 3395–3404.
[22] J. Xu, H. Wu, J. Wang, and M. Long, “Anomaly transformer: Time
series anomaly detection with association discrepancy,” in Proc. Int.
Conf. Learn. Represent., 2022, pp. 1–20.
[23] S. Tuli, G. Casale, and N. R. Jennings, “TranAD: Deep transformer
networks for anomaly detection in multivariate time series data,” Proc.
VLDB Endowment, vol. 15, no. 6, pp. 1201–1214, 2022.
[24] Q. Lin et al., “EDITS: An easy-to-difficult training strategy for cloud
failure prediction,” in Proc. ACM Web Conf., 2023, pp. 371–375.
[25] B. Li, D. Yu, J. Wu, P. Ju, and Z. Li, “Coordinated cloud-edge
anomaly identification for active distribution networks,” IEEE Trans.
Cloud Comput., vol. 11, no. 2, pp. 1204–1216, Apr.–Jun. 2023.
[26] F. Schmidt et al., “IFTM-unsupervised anomaly detection for virtualized
network function services,” in Proc. IEEE Int. Conf. Web Services
(ICWS), 2018, pp. 187–194.
[27] L. Yang et al., “Multi-perspective content delivery networks security
framework using optimized unsupervised anomaly detection,” IEEE
Trans. Netw. Service Manag., vol. 19, no. 1, pp. 686–705, Mar. 2022.
[28] M. A. Mukwevho and T. Celik, “Toward a smart cloud: A review
of fault-tolerance methods in cloud systems,” IEEE Trans. Services
Comput., vol. 14, no. 2, pp. 589–605, Mar./Apr. 2021.
[29] S. He, J. Zhu, P. He, and M. R. Lyu, “Experience report: System log
analysis for anomaly detection,” in Proc. 27th IEEE Int. Symp. Softw.
Rel. Eng., 2016, pp. 207–218.

3262

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOL. 21, NO. 3, JUNE 2024

[30] M. Smara, M. Aliouat, A.-S. K. Pathan, and Z. Aliouat, “Acceptance test
for fault detection in component-based cloud computing and systems,”
Future Gener. Comput. Syst., vol. 70, pp. 74–93, May 2017.
[31] Q. Lin, H. Zhang, J.-G. Lou, Y. Zhang, and X. Chen, “Log clustering
based problem identification for online service systems,” in Proc.
IEEE/ACM 38st Int. Conf. Softw. Eng., Companion (ICSE-Companion),
2016, pp. 102–111.
[32] N. Zhao, J. Zhu, R. Liu, D. Liu, M. Zhang, and D. Pei, “Label-less:
A semi-automatic labelling tool for KPI anomalies,” in Proc. IEEE
INFOCOM Conf. Comput. Commun., 2019, pp. 1882–1890.
[33] T. Huang et al., “An LOF-based adaptive anomaly detection scheme for
cloud computing,” in Proc. IEEE 37th Annu. Comput. Softw. Appl. Conf.
Workshops (COMPSAC), 2013, pp. 206–211.
[34] J. Álvarez Cid-Fuentes, C. Szabo, and K. Falkner, “Adaptive
performance anomaly detection in distributed systems using online
SVMs,” IEEE Trans. Dependable Secure Comput., vol. 17, no. 5,
pp. 928–941, Sep./Oct. 2020.
[35] N. Zhao et al., “Understanding and handling alert storm for online
service systems,” in Proc. IEEE/ACM 42st Int. Conf. Softw. Eng., Softw.
Eng. Pract. (ICSE-SEIP), 2020, pp. 162–171.
[36] M. M. Breunig, H.-P. Kriegel, R. T. Ng, and J. Sander, “LOF:
Identifying density-based local outliers,” in Proc. Int. Conf. Manag. Data
(SIG-MOD), 2000, pp. 93–104.
[37] D. M. J. Tax and R. P. W. Duin, “Support vector data description,” Mach.
Learn., vol. 54, no. 1, pp. 45–66, 2004.
[38] S. Hawkins, H. He, G. Williams, and R. Baxter, “Outlier detection using
replicator neural networks,” in Proc. 4th Int. Conf. Data Ware. Knowl.
Discov., 2002, pp. 170–180.
[39] H. Xu et al., “Unsupervised anomaly detection via variational autoencoder for seasonal KPIs in Web applications,” in Proc. World Wide
Web Conf., 2018, pp. 187–196.
[40] D. P. Kingma and M. Welling, “Auto-encoding variational Bayes,” in
Proc. Int. Conf. Learn. Represent., 2014, pp. 1–14.
[41] D. Liu et al., “Opprentice: Towards practical and automatic anomaly
detection through machine learning,” in Proc. ACM Int. Meas. Conf.,
2015, pp. 211–224.
[42] K. Sohn, H. Lee, and X. Yan, “Learning structured output representation
using deep conditional generative models,” in Proc. Adv. Neural Inf.
Process. Syst., 2015, pp. 3483–3491.
[43] S. Lin, R. Clark, R. Birke, S. Schönborn, N. Trigoni, and S. Roberts,
“Anomaly detection for time series using VAE-LSTM hybrid model,” in
Proc. IEEE Int. Conf. Acoust., Speech Signal, 2020, pp. 4322–4326.
[44] A. Vaswani et al., “Attention is all you need,” in Proc. 31st Adv. Neural
Inf. Process. Syst., 2017, pp. 5998–6008.
[45] C. L. P. Chen and Z. Liu, “Broad learning system: An effective
and efficient incremental learning system without the need for deep
architecture,” IEEE Trans. Neural Netw. Learn. Syst., vol. 29, no. 1,
pp. 10–24, Jan. 2018.
[46] C. L. P. Chen, Z. Liu, and F. Shuang, “Universal approximation capability of broad learning system and its structural variations,” IEEE Trans.
Neural Netw. Learn. Syst., vol. 30, no. 4, pp. 1191–1204, Apr. 2019.
[47] S. Feng and C. L. P. Chen, “Fuzzy broad learning system: A novel neurofuzzy model for regression and classification,” IEEE Trans. Cybern.,
vol. 50, no. 2, pp. 414–424, Feb. 2020.
[48] Z. Liu, C. L. P. Chen, S. Feng, Q. Feng, and T. Zhang, “Stacked broad
learning system: From incremental flatted structure to deep model,”
IEEE Trans. Syst., Man, Cybern., Syst., vol. 51, no. 1, pp. 209–222,
Jan. 2021.
[49] T. Song, W. Zheng, P. Song, and Z. Cui, “EEG emotion recognition using
dynamical graph convolutional neural networks,” IEEE Trans. Affect.
Comput., vol. 11, no. 3, pp. 532–541, Jul.–Sep. 2020.
[50] T. Qiu, X. Liu, X. Zhou, W. Qu, Z. Ning, and C. L. P. Chen,
“An adaptive social spammer detection model with semi-supervised
broad learning,” IEEE Trans. Knowl. Data Eng., vol. 34, no. 10,
pp. 4622–4635, Oct. 2022.
[51] F. Zhou and C. Cao, “Overcoming catastrophic forgetting in graph neural
networks with experience replay,” in Proc. 35th AAAI Conf. Artif. Intell.,
2021, pp. 4714–4722.
[52] Z. He et al., “A spatiotemporal deep learning approach for unsupervised
anomaly detection in cloud systems,” IEEE Trans. Neural Netw. Learn.
Syst., vol. 34, no. 4, pp. 1705–1719, Apr. 2023.
[53] Y. Su, Y. Zhao, C. Niu, R. Liu, W. Sun, and D. Pei, “Robust anomaly
detection for multivariate time series through stochastic recurrent neural
network,” in Proc. 25th ACM SIGKDD Int. Conf. Knowl. Discov. Data
Min., 2019, pp. 2828–2837.

[54] Z. Li et al., “Multivariate time series anomaly detection and
interpretation using hierarchical inter-metric and temporal embedding,”
in Proc. 27th ACM SIGKDD Int. Conf. Knowl. Discov. Data Min., 2021,
pp. 3220–3230.
[55] V. Nair and G. E. Hinton, “Rectified linear units improve restricted
Boltzmann machines,” in Proc. 27rd Int. Conf. Int. Conf. Mach. Learn.,
2010, pp. 807–814.
[56] S. Ioffe and C. Szegedy, “Batch normalization: Accelerating deep
network training by reducing internal covariate shift,” in Proc. 32rd Int.
Conf. Mach. Learn., 2015, pp. 448–456.
[57] D. P. Kingma and J. Ba, “ADAM: A method for stochastic optimization,”
in Proc. Int. Conf. Learn. Represent., 2015, pp. 1–15.
[58] J. Davis and M. Goadrich, “The relationship between precision-recall
and ROC curves,” in Proc. 23rd Int. Conf. Mach. Learn., 2006,
pp. 233–240.
[59] M. Amer, M. Goldstein, and S. Abdennadher, “Enhancing one-class
support vector machines for unsupervised anomaly detection,” in Proc.
ACM SIGKDD Workshop Outl. Detec. Descr., 2013, pp. 8–15.
[60] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation-based anomaly
detection,” ACM Trans. Knowl. Discov. Data, vol. 6, no. 1, pp. 1–39,
2012.
[61] Y. Zhang, Y. Chen, J. Wang, and Z. Pan, “Unsupervised deep anomaly
detection for multi-sensor time-series signals,” IEEE Trans. Knowl. Data
Eng., vol. 35, no. 2, pp. 2118–2132, Feb. 2023.
[62] I. J. Goodfellow et al., “Generative adversarial nets,” in Proc. Adv.
Neural Inf. Process. Syst., 2014, pp. 2672–2680.

Guoxiang Zhong received the M.S. degree from the
Guangdong University of Technology, Guangzhou,
China, in 2020. He is currently pursuing the Ph.D.
degree with the School of Computer Science and
Engineering, South China University of Technology,
Guangzhou. His research interests include cloud
computing and data mining.

Fagui Liu (Member, IEEE) received the M.S.
degree from Beihang University in 1991, and the
Ph.D. degree from the South China University of
Technology, China, in 2006, where she is currently a Professor with the School of Computer
Science and Engineering, South China University of
Technology. She is also with the Department of New
Networks, Peng Cheng Laboratory, Shenzhen. Her
current research interests include service computing,
Internet of Things, cloud computing, and big data.

Jun Jiang (Member, IEEE) received the Ph.D.
degree in computer science and technology from the
South China University of Technology, Guangzhou,
China, in 2022. He was a visiting student with Peng
Cheng Laboratory, Shenzhen, China, in 2023. He is
currently a Lecturer with the College of Information
Science and Technology and the College of Artificial
Intelligence, Nanjing Forestry University, Nanjing,
China. His research interests include data stream
classification, anomaly detection, cloud computing,
and Internet of Things.

ZHONG et al.: DETECTING CLOUD ANOMALY VIA BROAD NETWORK-BASED CONTRASTIVE AUTOENCODER

Bin Wang received the B.S. and Ph.D. degrees from
the South China University of Technology in 2014
and 2021, respectively. He is currently a Research
Scientist with the Department of New Networks,
Peng Cheng Laboratory, Shenzhen. His research
interests include cloud computing, edge computing,
and energy efficiency.

Xi Yao received the B.S. degree from the South
China University of Technology, Guangzhou, China,
in 2023. She will pursue the Ph.D. degree with
the School of Computer Science and Engineering,
South China University of Technology. Her research
interests include anomaly detection and cloud
computing.

3263

C. L. Philip Chen (Fellow, IEEE) is the Chair
Professor and the Dean of the College of Computer
Science and Engineering, South China University
of Technology, Guangzhou, China. Been a Program
Evaluator of the Accreditation Board of Engineering
and Technology Education, USA, for computer
engineering, electrical engineering, and software
engineering programs, he successfully architects the
University of Macau’s Engineering and Computer
Science programs receiving accreditations from
Washington/Seoul Accord through the Hong Kong
Institute of Engineers, of which is considered as his utmost contribution in
engineering/computer science education for Macau as the Former Dean of
the Faculty of Science and Technology. His current research interests include
cybernetics, computational intelligence, and systems.
Dr. Chen received the IEEE Norbert Wiener Award in 2018 for his
contribution in systems and cybernetics, and machine learnings and the
IEEE Joseph Wohl Award in 2021. He received two times Best Transactions
Paper Award from IEEE T RANSACTIONS ON N EURAL N ETWORKS AND
L EARNING S YSTEMS for his papers in 2014 and 2018. He was a recipient of
the 2016 Outstanding Electrical and Computer Engineers Award from his alma
mater, Purdue University, West Lafayette, IN, USA, in 1988, after he graduated from the University of Michigan at Ann Arbor, Ann Arbor, MI, USA,
in 1985. He is a Highly Cited Researcher by Clarivate Analytics from 2018
to 2021. He is a Fellow of the American Association for the Advancement
of Science, the International Association for Pattern Recognition, the Chinese
Association of Automation, and HKIE, and a member of the Academia
Europaea and the European Academy of Sciences and Arts. He was the
Editor-in-Chief of the IEEE T RANSACTIONS ON C YBERNETICS from 2020
to 2021 after he completed his term as the Editor-in-Chief of the IEEE
T RANSACTIONS ON S YSTEMS , M AN , AND C YBERNETICS : S YSTEMS from
2014 to 2019, followed by serving as the IEEE Systems, Man, and Cybernetics
Society President from 2012 to 2013. He is currently serving as the Deputy
Director for CAAI Transactions on Artificial Intelligence, an Associate
Editor for the IEEE T RANSACTIONS ON A RTIFICIAL I NTELLIGENCE, IEEE
T RANSACTIONS ON S YSTEMS , M AN , AND C YBERNETICS : S YSTEMS, IEEE
T RANSACTIONS ON F UZZY S YSTEMS, and China Sciences: Information
Sciences.
PAPER_TEXT
