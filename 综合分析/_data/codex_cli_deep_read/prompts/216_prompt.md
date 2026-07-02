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
# [216] Energy-Efficient Self-Supervised Technique to Identify Abnormal User Over 5G Network for E-Commerce
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
编号：216
题名：Energy-Efficient Self-Supervised Technique to Identify Abnormal User Over 5G Network for E-Commerce
年份：2024
DOI：10.1109/tce.2024.3355477
来源：IEEE Transactions on Consumer Electronics
PDF：paper/10.1109_TCE.2024.3355477.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：入侵检测与网络异常检测、IoT、车联网、工业互联网与边缘安全
相关性：弱相关，分数 4
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\216.txt
- 原始字符数：42539
- 本次发送字符数：42539
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

1631

Energy-Efficient Self-Supervised Technique to
Identify Abnormal User Over 5G
Network for E-Commerce
Sami Ahmed Haider , Mohammad Zia Ur Rahman , Sachin Gupta , Ataniyazov Jasurbek Hamidovich,
Arsalan Muhammad Soomar, Bhoomi Gupta , Jagdish Chandra Patni, and Venkata Chunduri

Abstract—Within the realm of e-commerce networks, it is
frequently observed that certain users exhibit behavior patterns
that differ substantially from the normative behaviors exhibited
by the majority of users. The identification of these atypical
individuals and the understanding of their behavioral patterns
are of significant practical significance in maintaining order
on e-commerce platforms. One such method for accomplishing
this objective entails examining the behavioral tendencies of
atypical users through the abstraction of e-commerce networks
as heterogeneous information networks. These networks are
then transformed into a bipartite graph that establishes associations between users and devices. The Self-Supervised Aberrant
Detection Model (SAD) has been proposed within this theoretical
framework as a means to identify and detect users who exhibit
aberrant behavior. The SSADM methodology utilizes a selfsupervised learning process that utilizes autoencoders to encode
representations of user nodes. The proposed method aims to
maximize a combined objective function for backpropagation
while utilizing support vector data description to detect abnormalities in the representations of user nodes. In summary,
many tests have been conducted utilizing both authentic network
datasets and partially synthetic network datasets to demonstrate
the efficacy and superiority of the SAD technique, specifically
within the domain of an energy-efficient 5G network.
Index Terms—Energy efficiency, aberrant detection model,
optimization technique, behavioral analysis, social networks.
Manuscript received 8 November 2023; revised 8 December
2023 and 7 January 2024; accepted 15 January 2024. Date
of publication 24 January 2024; date of current version
26 April 2024. (Corresponding author: Sami Ahmed Haider.)
Sami Ahmed Haider is with the Glasgow College, University of
Electronics Science and Technology, Chengdu 610056, China (e-mail:
samiahmed.haider@glasgow.ac.uk).
Mohammad Zia Ur Rahman is with the Department of Electronics and
Communication Engineering, Koneru Lakshmaiah Education Foundation,
Vaddeswaram 522302, India (e-mail: mdzr55@gmail.com).
Sachin Gupta is with the Department of CSE, Maharaja Agrasen Institute
of Technology, Meerut 250005, India (e-mail: sachin.gupta@mait.ac.in).
Ataniyazov Jasurbek Hamidovich is with the Department of International
Finance and Credit, Tashkent Institute of Finance, Tashkent 1000000,
Uzbekistan (e-mail: j_ataniyazov@tfi.uz).
Arsalan Muhammad Soomar is with the Faculty of Electrical and Control
Engineering, Gdańsk University of Technology, 80-226 Gdańsk, Poland
(e-mail: Arsalan.muhammad.soomar@pg.edu.pl).
Bhoomi Gupta is with the Department of Information Technology,
Maharaja Agrasen Institute of Technology, New Delhi 110086, India (e-mail:
bhoomigupta@mait.ac.in).
Jagdish Chandra Patni is with the Symbiosis Institute of Technology
(Nagpur Campus), Symbiosis International (Deemed University), Nagpur
440008, India (e-mail: jagdish.patni@sitnagpur.siu.edu.in).
Venkata Chunduri is with the Senior Software Developer, Department of
Mathematics and Computer Science, Indiana State University, Terre Haute,
IN 47809 USA (e-mail: vchunduri@sycamores.indstate.edu).
Digital Object Identifier 10.1109/TCE.2024.3355477

I. I NTRODUCTION
ITH the continuous spread and development of the
Internet, many unscrupulous merchants engage in
fraudulent activities on major e-commerce platforms by
manipulating a large number of users to post fake reviews,
engage in malicious ordering, and other deceptive practices.
These acts result in significant detriment to consumer interests.
To mitigate the adverse effects caused by atypical users,
the scholarly community has put forth many approaches for
detecting anomalies, which have proven to be efficacious in
practice.
Literature [1] proposed a density-based local outlier
detection algorithm that introduces information entropy to
uncover local outliers in homogeneous information networks.
Literature [2] combined the K-Nearest Neighbors (KNN) outlier detection algorithm with a multi-level random forest model
to detect abnormal behavior in homogeneous information
networks. A person’s behavior can be influenced by a variety
of personal circumstances, such as age, health, illness, pain,
and the effect of drugs or alcohol. Literature [3] proposed
an anomaly detection algorithm based on suffix trees, which
detects anomalies, based on the periodicity of anomalies
in time series data. Literature [4] used autoencoders and
probabilistic neural networks to achieve anomaly detection
goals. Most of the current research focuses on homogeneous
information networks, and many methods are still limited
and not suitable for heterogeneous information networks [5].
Literature [6] proposed a dynamic anomaly detection method
based on tensor representation for heterogeneous networks,
which constructs a tensor index tree for classification samples
and clustering, making dynamic anomaly point judgments
based on whether clusters transform effectively. In the realm
of literature, a study [7] has presented a method for detecting
anomalies in heterogeneous information networks. The importance of different kinds of nodes is ascertained by an attention
mechanism. By examining unique aggregation patterns, this
makes it possible to identify abnormal users. The differentiation embeddings from heterogeneous networks are adaptively
learned in the suggested technique. The literature [8] presents
a method for detecting outliers in the distribution of communities within diverse information networks. Literature [9]
proposed a fraud detection model called SAD for e-commerce
networks, which uses autoencoders to extract behavioral patterns of fraudulent accounts in heterogeneous graphs and uses

W

c 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
1558-4127 
See https://www.ieee.org/publications/rights/index.html for more information.

1632

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Density-Based Spatial Clustering of Applications with Noise
(DBSCAN) to detect fraud clusters. Unusual users appear as
a result of several fraudulent merchants registering a large
number of new users and logging in on particular devices
to conduct group fraud activities. Because of the Internet’s
continuous expansion, many dishonest merchants utilise wellknown e-commerce platforms. Literature [10] proposed a joint
embedding method to capture the structure of heterogeneous
graphs and detect fraud account groups in social networks.
End-to-end trainable joint model for e-commerce network false
review detection that combines neural random forests and
autoencoders. Literature [11] proposed an end-to-end trainable joint model combining autoencoders and neural random
forests to detect fake reviews in e-commerce networks. An
autoencoder consists of two neural networks: a decoder that
extends the latent representation back to its original size and
an encoder that compresses an input, like an image, to a lowdimensional latent representation. The thousands to millions of
transaction records that are generated everyday in e-commerce
platforms are made up of the registration, login, purchase,
review, and other behaviors of users, devices, products, and
retailers. A person’s Behavior can be influenced by a variety
of personal circumstances, such as age, health, illness, pain,
and the effect of drugs or alcohol. In light of this, we suggest
the Self-Supervised Anomaly Detection Model (SAD) as a
means of identifying anomalous users in e-commerce systems.
The network maintains consistent detection results while also
keeping the relatively complete bipartite graph structure and
user behavioural aspects in user node representations by
automatically supplying supervision information for anomaly
detection. In order to identify fraud clusters using DBSCAN
and extract fraudulent account behavior patterns from diverse
graphs, an integrated embedding technique to identify fraud
account clusters in social networks and capture the structure
of heterogeneous graphs. In the following sections, this paper
describes the behavioral characteristics of abnormal users in
e-commerce networks and introduces related work, details the
construction of SAD, summarizes the algorithm flow of SAD,
validates and compares SAD in experiments, analyzes its time
complexity, and concludes the paper while looking forward
to future work. This study outlines the development of SAD,
summarizes the algorithm flow of SAD, and describes the
Behavioral features of atypical users in e-commerce networks.
It also introduces related work. The SAD technique relies
on the analysis of popularity community distribution patterns
among various object kinds and employs non-negative matrix
factorization for outlier detection.
This article presents the Behavioral traits of abnormal users
in e-commerce networks, reviews relevant literature, goes into
detail on how SAD is constructed, outlines its algorithmic
flow, verifies and contrasts SAD in experiments, examines its
temporal complexity, and ends the paper by looking ahead to
future research. The following are the paper’s most significant
contributions:
1. The research abstracts the e-commerce network as a
heterogeneous information network and turns it into a
user-device bipartite graph in order to solve the problem
of detecting aberrant users in e-commerce platforms.

2. In light of this, we propose the Supervised Anomaly
Detection Model (SAD). The suggested method
improves the efficiency of abnormal user detection by
automatically optimizing the network in iterative cycles,
while preserving the bipartite graph structure and user
behavioral features.
3. Second, the usefulness and superiority of the proposed
method is demonstrated through comparative experiments and analysis of SAD on three real network
datasets and one semi-synthetic network dataset.
II. R ELATED W ORK
A. Behavioral Patterns of Abnormal Users
In e-commerce platforms, many fraudulent merchants register numerous new users and log in on specific devices to carry
out collective fraudulent activities, leading to the emergence
of abnormal users. Literature [7] conducted an analysis of user
data on e-commerce platforms. Device clustering and activity
clustering are the two main Behavioral tendencies of aberrant users. Device Clustering: Unusual users in e-commerce
networks have access to a large number of computer machines
for fraudulent purposes, but this Behavior has a hefty price.
The majority of anomalous users usually log in on particular
groupings of devices in order to control expenditures. The
Supervised Anomaly Identification Model (SAD) preserves
the bipartite graph structure and user behavioural data while
automatically optimising the network in iterative cycles to
increase the effectiveness of anomalous user identification.
Device Clustering: In e-commerce networks, abnormal users
control a significant number of computing devices for fraudulent activities, but this behavior comes at a high cost. To
control costs, most abnormal users typically log in on specific
groups of devices. Activity Clustering:
In e-commerce networks, abnormal users need to complete
tasks within a short time frame, which leads to a burst of
collective activity during specific time intervals. In [12], a
thorough analysis of the methods for detecting novelty is
provided. A detailed study of DL-based anomaly detection
algorithms was recently published in [13]. A review of the
data mining methods for anomaly detection is covered in [14].
Regression, rule learning, and clustering are the approaches
that are covered.
B. Autoencoders
The concept of autoencoders was first introduced by
Literature [15], and subsequent literature [16] provided
detailed explanations. Autoencoders consist of two main parts:
the encoder (E) and the decoder (D), and their structures are
symmetric, meaning that the number of hidden layers in the
encoder is the same as the number of hidden layers in the
decoder. The encoding process of the encoder is as follows:
z = σe (W1 x + b1 )

(1)

The decoding process of the decoder can be described as:
y = σd (W2 z + b2 )

(2)

HAIDER et al.: ENERGY-EFFICIENT SELF-SUPERVISED TECHNIQUE TO IDENTIFY ABNORMAL USER

1633

The feature representation in the hidden space is denoted by
z, where W1 and b1 are the encoding weights and biases and
W2 and b2 are the decoding weights and biases. The activation
function is denoted by e, commonly used ones include ReLU,
Sigmoid, and Tanh, while σd can be the same as σe [17].
J(W, b) = (L(x, y)) = y − x22

(3)

The encoding process maps the input signal to a feature
representation in the hidden space deterministically, while the
decoding process attempts to remap the feature representation
in the hidden space back to the input signal [17 Autoencoders
have advantages such as a simple reconstruction process,
the ability to stack multiple layers, and support from neuroscience [17]. Today, methods based on autoencoders, such as
image classification [18], [19], anomaly detection [20], [21],
and pattern recognition [22], are widely applied in various
research fields and have achieved success. Large amount
of data to obtain sufficient training samples, which is very
labor and resource intensive [23]. An information entropybased density-based technique for local outlier detection in
homogeneous information networks. A multi-level random
forest model combined with the KNN outlier detection technique is used to identify anomalous activity in homogeneous
information networks.
Therefore, unsupervised anomaly detection has received
widespread attention, and autoencoder-based anomaly detection methods are widely used in fields such as e-commerce
fraud detection [24] and social network abnormal user detection [25] due to their excellent performance.
III. A NOMALY U SER D ETECTION M ETHOD FOR
E-C OMMERCE N ETWORKS
This section introduces an anomaly user detection method
for e-commerce networks - the Supervised Anomaly Detection
Model (SAD). It provides a detailed description of SAD
from three aspects: basic definition, model structure, and
optimization stage.
A. Basic Definition
In e-commerce platforms, every user leaf records when
they log in, browse, make purchases, and provide reviews.
As shown in Figure 1, these records cover the relationships
between different entities, such as users, devices, products,
and merchants, including the behavioral traces of abnormal
users. The links between various entities, including users,
devices, items, and merchants, as well as the Behavioral
traces of problematic users, are covered by these records,
as seen in Figure 1. The e-commerce network is abstracted
as a heterogeneous information network in order to more
intuitively analyze the Behavioral traits of various users inside
the network.
According to the first definition provided by the
Heterogeneous Information Network [6], Consider a directed
graph G = (V, E; τ , ϕ; A, R). In this graph, V represents the
set of nodes, E represents the set of edges, τ is a function
that maps each object to its object type, ϕ is a function that
maps each relationship to its relationship type, and τ (v) ∈

Fig. 1. Association relationships between different entities in the e-commerce
network.

A indicates that each object v ∈ V belongs to a specific
object class, while ϕ(e) ∈ R indicates that each relationship e
∈ E belongs to a specific relationship class. An information
network is referred to as a heterogeneous information network
when the number of node types |A| is greater than 1 or the
number of edge types |R| is greater than 1. Conversely, if |A|
= 1 and |R| = 1, the information network is classified as a
homogeneous information network.
In Section II-A, Literature [7] analyzed the login patterns of users on different devices in e-commerce platforms.
We concentrate on the relationships that exist between two
different types of entities: people and gadgets. End-to-end
trainable joint model that blends neural random forests and
autoencoders for e-commerce network false review detection.
When describing different things and their relationships, heterogeneous information networks are an abstraction of the
underlying real-world systems. The method aims to convert
the heterogeneous information network into a bipartite graph
that accurately represents the relationship between individuals
and devices. This graph is going to be an essential part of
our next research projects. The e-commerce infrastructure is
modelled as a bipartite graph of consumers and their devices
after being abstracted as a heterogeneous information network.
Definition 1 (Bipartite Graph Structure): Given a directed
graph G = (X, Y, E), where X = {x1 , x2 , . . . , xm } represents
a set of m user nodes, Y = {y1 , y2 , . . . , yn } represents a set
j=1,2,...,n
of n device nodes, and E = {eij }i=1,2,...,m represents a set of
directed edges from X to Y. If there is an edge from xi to yj ,
then eij = 1; otherwise, eij = 0. Therefore, the bipartite graph
structure can be represented as a matrix S = [s1 , s2 , . . . , sm ]T ,
where si = [ei1 , ei2 , . . . , ein ].
B. Model Structure of S-SAD
This section offers a comprehensive explanation of the
model structure of S-SAD, and Figure 2 illustrates the entirety
of the SAD framework.
Most users typically log in to e-commerce platforms only
on their personal devices, while abnormal users tend to log in
on specific groups of devices. Any Behavior that differs from
what is deemed normal is termed abnormal. Psychologists
utilize four broad criteria to classify conduct as abnormal:

1634

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

Furthermore, the Euclidean distance can be transformed into
behavioral similarity between user node representations using
the following mapping function:


ij = exp −disij
(10)
sim

Fig. 2. The complete framework of the abnormal user detection method
SAD for e-commerce networks.

statistical rarity, emotional suffering, maladaptive Behavior,
and breach of social norms.
Formally, by taking the bipartite graph structure matrix S
as the input to the autoencoder, the encoding process can be
represented as:
Z = σ (WS + b)

(4)

Then, the user node representations Z are decoded to
reconstruct the bipartite graph structure matrix 
S, and the
formal representation of the decoding process is as follows:

S = σ (WZ + b)

In which, Ni := {yj ∈ Y:eij = 1} represents the set of device
nodes associated with the user node xi .
According to activity clustering, it is known that an abnormal user group will engage in collective activities during a
specific time period of the day. Therefore, the day is divided
into 24 time periods, and the number of times each user logs
in to different devices is counted, denoted as T for each time
period. The login behavior of each user is described as ti =
[T0 , T1 , . . . , T23 ]. The activity similarity between user nodes
is defined as:
ti ·tj
 
(7)
sim− tij =
|ti |×tj 
Combining the two types of similarity, the behavioral
similarity between user nodes in the original space is defined
as follows:
(8)

As user nodes xi and xj are represented in the latent space
as zi and zj , the behavioral differences between user node
representations can be defined using Euclidean distance:
disij = zi − zj 22

1
zi
m
m

c=

(5)

where Z = [z1 , z2 , . . . , zm ]T , and zm represents the user node
representation corresponding to the m-th user node in the latent
space. W and b are the decoding weights and biases, and σ
is the activation function. Both the encoder and decoder parts
use the ReLU activation function [7]. The device similarity
between user nodes is defined as:


Ni ∩Nj 


(6)
sim− dij =
Ni ∪Nj 

simij = sim_ dij × sim− tij

ij ranges from (0, 1). For user nodes xi and xj ,
where sim
ij is approximately 1,
when their distance is close to 0, sim
representing that xi and xj have small behavioral differences.
ij is approximately 0,
When their distance is large enough, sim
indicating that xi and xj have significant behavioral differences.
ij and simij , you
By narrowing the difference between sim
can obtain node representations that capture user behavioral
characteristics.
Backpropagation is used to optimise the joint objective
function in order to offer SAD a self-supervised mechanism,
which allows user node representations to autonomously provide supervision for anomaly detection. updating the weights
and biases in the autoencoder network.
Next, the Support Vector Data Description (SVDD) is
employed for anomaly detection on the user node representations Z.
First, the core c of the hypersphere in the latent space is
computed:

(9)

(11)

i=1

Then, the Euclidean distances between each user node
representation and the core are calculated:
di =zi −c22

(12)

And a set of distances D is formed: D = {d1 , d2 , . . . , dm }.
To find an appropriate hypersphere radius r, the normal
distribution of the set D is discussed using the 3σ criterion.
The following text defines the 3σ criterion.

If x ∼ N μ,σ 2 , then:
P{|x − μ| < σ } = 0.
P{|x − μ| < 2σ } = 0.9445
P{|x − μ| < 3σ } = 0.9977

(13)
(14)
(15)

Based on Equation (15), it is evident that the likelihood of
a normally distributed variable x falling outside the range (μ
–3σ , μ + 3σ ) is below 0.003, a probability that is commonly
regarded as being exceedingly low.
C. Optimization Phase
The joint objective function of the SAD model comprises
three components. The initial component of the objective
function pertains to the reconstruction error of the autoencoder,
which quantifies the disparity between the original input S and
the reconstructed output Ŝ. Minimizing the reconstruction error
helps preserve the bipartite graph structure more effectively.
The definition of the objective function Lrec is as follows:
Lrec =

m

i=1


si −si 22

(16)

HAIDER et al.: ENERGY-EFFICIENT SELF-SUPERVISED TECHNIQUE TO IDENTIFY ABNORMAL USER

The second part of the objective function concerns the difij and simij . Minimizing this objective
ference between sim
function helps obtain user node representations with behavioral
characteristics. The objective function Lsim is defined as
follows:
m

ij −simij 2
sim
(17)
Lsim =
2
i=1,j=1

In the paper [26], Deep SVDD optimizes the objective
function of SVDD to place the majority of user nodes within
the minimum hypersphere around the core, while anomalous
user nodes lie outside the hypersphere. To constrain user node
representations, the third part of the objective function is
defined as in [26]:
1
zi −c 22
m
m

Lsvdd =

(18)

i=1

Finally, to simultaneously preserve the bipartite graph
structure and user behavioral characteristics in user node
representations and constrain them, the joint objective function
is defined based on Equations (16) to (18). The definition of
the objective function L is as follows:
L =Lrec +α(Lsim + Lsvdd )

(19)

where α is a hyperparameter. Minimizing L helps obtain user
node representations with supervised information.
IV. SAD A LGORITHM F LOW
This section presents the algorithmic flow of SAD,
providing theoretical guidance for subsequent experimental
validation and comparative analysis.
V. E XPERIMENTAL R ESULTS AND A NALYSIS
To validate the effectiveness and superiority of SAD, several existing baseline methods were selected for comparative
experiments. The experimental environment utilized an Intel
Core i7-7700 CPU with a clock speed of 3.60GHz, 8GB of
memory, and a 64-bit Windows 10 operating system.
A. Baseline Methods
Firstly, the baseline methods used in the experiments
are introduced, including three classical anomaly detection
methods such as Isolation Forest, classic autoencoder-based
anomaly detection methods, and recent anomaly detection
methods like Deep FD [9] and Fraud NE [10].
B. Datasets
In this study, experiments were conducted using three
real e-commerce network datasets obtained from Kaggle and
one semi-synthetic e-commerce network dataset. The datasets
are shown in Table I, and the subsequent descriptions offer
comprehensive information regarding each dataset.
(1) Real Dataset 1: The dataset encompasses user purchase
records derived from a certain e-commerce platform. It
comprises various attributes such as user IDs, user ages,

1635

Algorithm 1 SAD Anomaly Detection Method for
E-Commerce Networks
Input: Heterogeneous information network data
Output: Anomaly detection evaluation metrics results
Convert heterogeneous network data to a user-device bipartite
graph and construct the bipartite graph structure matrix S using
Definition 1.
for i, j = 0 to m
Calculate behavioral similarity between user nodes using
Equation (8).
end
Use matrix S as input to the autoencoder. Choose the optimizer
as stochastic gradient descent and set the values for epochs,
batch size, and learning rate (EPO, batch size, learning rate).
for i = 0 to epoch
Calculate user node representations using Equation (4) and
complete forward propagation. Calculate behavioral similarity
between user node representations using Equation (10).
Optimize the joint objective function L using Equation (19)
and complete backward propagation.
Calculate the core of the hypersphere latent space using
Equation (11).
end
for i = 0 to m
Calculate distances between user node representations and
the core using Equation (12) to form the set D.
end
Remove di values in D that fall outside the interval using
principles from Equation (13) to (15). Select the maximum
value in the remaining set as the radius r.
for i = 0 to m
if di > r
The node is considered an anomalous user node.
else
The node is considered a normal user node.
end
end
Return the anomaly detection evaluation metrics results.
end

user genders, login device IDs, purchase timings, and
more relevant information. In this experiment, a subset
of the original dataset was
(2) Real Dataset 2: The dataset encompasses user purchase
records obtained from a certain e-commerce platform,
encompassing various user information such as IP
addresses, email addresses, phone numbers, login device
IDs, and more data.
(3) Real Dataset 3: The information encompasses user purchase records obtained from a prominent online retailer,
spanning the time frame between October 2019 and
April 2020.
(4) Semi-Synthetic Dataset: This dataset contains user purchase records from a certain e-commerce platform,
including user IDs, user ages, user genders, login device
IDs, and purchase times. It was created by randomly
sampling from the original data and adding behavioral

1636

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

TABLE I
E-C OMMERCE N ETWORK DATA S ET

TABLE III
E VALUATION I NDEX R ESULTS OF D IFFERENT
M ETHODS IN R EAL DATA S ET 1

TABLE II
B EWILDERMENT M ATRIX

TABLE IV
E VALUATION I NDEX R ESULTS OF D IFFERENT
M ETHODS IN R EAL DATA S ET 2

records for some anomalous users, where the number of
anomalous user’s accounts for 5% of all users.
C. Evaluation Metrics
Since anomaly detection datasets are typically imbalanced,
evaluating performance can be more complex. Finding data
points or patterns in a dataset that substantially depart from
the norm is known as anomaly detection. Five evaluation
metrics are used to assess the performance of various methods.
These metrics include Precision (P), Recall (R), F1-score, Area
Under the Curve (AUC), and the G-mean.
The evaluation of measurements is conducted by employing
a bewilderment matrix, exemplified in Table II. Similarly,
“FP” designates the count of false positive samples that
have been inaccurately classified, while “TN” represents the
quantity of true negative samples that have been correctly
classified.
(1) Precision is defined as:
TP
P=
TP + FP

(20)

TP
TP + FN

(21)

(2) Recall is defined as:
R=

(3) In general, there exists a trade-off between precision
and recall. The F1-measure is computed by using the
following formula:
F1 =

2×P×R
P+R

(22)

(4) The evaluation statistic known as AUC (Area Under
the Curve) holds significant importance in the context
of classification algorithms, since it quantifies the area

beneath the Receiver Operating Characteristic (ROC)
curve. The calculation is performed as follows:
TP
(23)
TP + FN
FP
FPR =
(24)
FP + TN
(5) G-mean is used for imbalanced datasets and is defined
as:
√
G mean = R × TNR
(25)
TPR =

where TNR (True Negative Rate) represents the proportion of detected negatives among all actual negatives,
calculated as:
TN
TNR =
(26)
TN + FP
D. Experimental Validation and Comparative Analysis
The tests were carried out utilizing the TensorFlow framework, wherein the latent space dimension was configured to
be 10. The experimental findings are displayed in Tables III
to 6, whereby the most favorable outcomes for each statistic
are highlighted in bold.
A comparative analysis is performed between SAD and
baseline methods in the four experiments. Table III presents
the evaluation metric results for different methods on Real
Dataset 1, where SAD performs better in Recall, F1-measure,
AUC, and G-mean.

HAIDER et al.: ENERGY-EFFICIENT SELF-SUPERVISED TECHNIQUE TO IDENTIFY ABNORMAL USER

TABLE V
E VALUATION I NDEX R ESULTS OF D IFFERENT
M ETHODS IN R EAL DATA S ET 3

1637

TABLE VII
O RDINAL VALUE TABLE

TABLE VI
E VALUATION I NDEX R ESULTS OF D IFFERENT
M ETHODS IN S EMI -S YNTHETIC DATA S ETS

Table IV lists the evaluation metric results for different
methods on Real Dataset 2, where SAD outperforms the
baseline methods in various metrics.
Table V presents the evaluation metric results for different methods on Real Dataset 3. KNN achieves the highest
Precision in this experiment, while Deep FD performs best in
Recall. SAD outperforms the baseline methods in F1-measure,
AUC, and G-mean, and its performance is second only to Deep
FD in Recall.
Table VI displays the evaluation metric results for different
methods on the semi-synthetic dataset. Deep FD performs best
in Precision, with SAD closely following. SAD outperforms
the baseline methods in other evaluation metrics. Improved
feature representations of the data through self-supervised
learning can improve computer vision model performance.
Furthermore, the use of an SSL method improves a model’s
capacity to learn in the absence of the structure that labelled
data provides.
Analyzing the experimental results, SAD demonstrates its
effectiveness and superiority in various evaluation metrics
across different datasets. Within this theoretical framework,
the Self-Supervised Aberrant Detection Model (SAD) has been
presented to recognize and identify people who display aberrant behavior. Autoencoders are used in the self-supervised
learning process of the SSADM methodology to encode
user node representations. the usage of the Self-Supervised
Anomaly Detection Model (SAD) in e-commerce systems to
detect unusual user Behavior. It finishes forward propagation

by encoding user node representations using autoencoders.
This indicates that the anomaly detection method with a
self-supervised learning mechanism exhibits strong detection
performance and generalization capabilities.
To comprehensively compare the generalization capabilities
of all methods, a Friedman test is performed on the F1measure evaluation metric results for different methods across
different datasets.
The null hypothesis (H0) and alternative hypothesis (H1)
for the Friedman test are as follows:
H0: There is no difference in F1-measure evaluation metric
results among different methods across different datasets,
meaning that the performance of different methods is the same.
H1: There is a difference in F1-measure evaluation metric
results among different methods across different datasets,
indicating that the performance of different methods varies.
First, the F1-measure evaluation metric results for different
methods across different datasets are ranked, and the average
ranks are calculated for each row to obtain the average rank,
as shown in Table VII.
Assuming the comparison of k methods on N datasets, let ri
represent the average rank of the i-th method. The ri follows
a normal distribution with a mean of (k+1)/2 and a variance
of (k2 − 1)/12. This leads to a χ 2 distribution:
τχ 2 =

k

12N
k(k + 1)2
ri2 −
k(k + 1)
4

(27)

i=1

Based on Equation (27), the F-distribution can be derived:
τF =

(N − 1)τχ 2
N(k − 1) −τχ 2

(28)

where τF follows an F-distribution with degrees of freedom
k-1 and (k–1)(N–1) [27]. At a significance level α = 0.05 and
degrees of freedom of 8, by calculation, τF = 13.94, which is
greater than the critical value 2.355 [27]. This confirms that
the null hypothesis H0 is not valid, indicating that there is a
difference in the performance of different methods.
Next, a sensitivity analysis of the hyperparameter α is
performed. When α takes different values in the range (0,1),
the evaluation metric results of SAD on different datasets are
observed to see if they change. The statistical distribution

1638

IEEE TRANSACTIONS ON CONSUMER ELECTRONICS, VOL. 70, NO. 1, FEBRUARY 2024

to classical anomaly detection methods but similar to other
baseline methods. With the same time complexity, this method
shows more outstanding performance on different datasets.
VI. C ONCLUSION

Fig. 3. Different evaluation index results of SAD when α changes in data
set 1-3.
TABLE VIII
F1G MEASURE E VALUATION I NDEX R ESULTS OF SAD W HEN THE
ACTIVATION F UNCTION C HANGES IN R EAL DATA S ET 1

TABLE IX
F1-M EASURE E VALUATION I NDEX R ESULTS OF SAD W HEN THE
ACTIVATION F UNCTION C HANGES IN R EAL DATA S ET 2

of precision and recall over all three data set are shown in
Figures 3.
Based on the analysis of experimental results, it can be
concluded that as the α value gradually increases, the values
of different evaluation metrics continue to increase. When α
reaches a certain value, the changes in the values of different
evaluation metrics stabilizes.
This paper examines the impact of activation functions in
SAD (Self-Attention Distillation) and presents a comparative
analysis of the evaluation metric outcomes of SAD on various
datasets, specifically focusing on the F1-G measure. Based
on the data shown in Table VIII, it is apparent that the
Rectified Linear Unit (ReLU) function demonstrates superior
performance in precision, F1-G measure, and G-mean across
three assessment criteria. Tables IX show that the ReLU
function excels in various evaluation metrics.
According to the algorithm procedure in Section IV, the
time complexity of SAD is O(m) + O( epoch ∗ 2m), which
is O(n2 ), making it have a higher time complexity compared

E-commerce networks involve relationships between different entities and have a structure of a heterogeneous
information network. By analyzing anomalous user behavior
patterns, a self-supervised anomaly detection method, SAD,
is proposed for e-commerce networks. A self-supervised
anomaly detection technique called SAD is presented for
e-commerce networks. It operates by examining unusual
user Behavior patterns. Within this theoretical framework,
a method for identifying and detecting users who display
aberrant Behavior has been proposed: the Self-Supervised
Aberrant Detection Model (SAD). Experimental verification
and comparative analysis demonstrate that SAD outperforms
baseline methods in various evaluation metrics, proving the
feasibility and superiority of this method. Despite having great
anomaly detection performance, the SAD approach described
in this paper ignores node and edge attribute information in
heterogeneous information networks. Furthermore, although
there are other links among various entities in e-commerce
networks, this research primarily focuses on the relationships
between users and devices. In the future, we hope to further
expand research on anomaly user detection by analyzing
behavior patterns among different entities.
R EFERENCES
[1] M. R. Kondamudi, S. R. Sahoo, L. Chouhan, and N. Yadav, “A comprehensive survey of fake news in social networks: Attributes, features,
and detection approaches,” J. King Saud Univ.-Comput. Inf. Sci., vol. 35,
no. 6, Art. no. 101571, doi: 10.1016/j.jksuci.2023.101571.
[2] A. Mewada and R. K. Dewang, “Research on false review
detection Methods: A state-of-the-art review,” J. King Saud
Univ.-Comput. Inf. Sci., vol. 34, no. 9, pp. 7530–7546, 2022,
doi: 10.1016/j.jksuci.2023.101571.
[3] A. Abdallah, M. A. Maarof, and A. Zainal, “Fraud detection system:
A survey,” J. Netw. Comput. Appl., vol. 68, pp. 90–113, Jun. 2016,
doi: 10.1016/j.jnca.2016.04.007.
[4] Q. Zheng, Y. Xu, H. Liu, B. Shi, J. Wang, and B. Dong, “A survey
of tax risk detection using data mining techniques,” Engineering, early
access, Sep. 25, 2023, doi: 10.1016/j.eng.2023.07.014.
[5] T. Limbasiya, K. Z. Teng, S. Chattopadhyay, and J. Zhou, “A systematic
survey of attack detection and prevention in connected and autonomous
vehicles,” Veh. Commun., vol. 37, Oct. 2022, Art. no. 100515,
doi: 10.1016/j.vehcom.2022.100515.
[6] M. A. Javed, M. S. Younis, S. Latif, J. Qadir, and A. Baig, “Community
detection in networks: A multidisciplinary review,” J. Netw. Comput.
Appl., vol. 108, pp. 87–111, Apr. 2018, doi: 10.1016/j.jnca.2018.02.011.
[7] P. Bindu and P. S. Thilagam, “Mining social networks for anomalies:
Methods and challenges,” J. Netw. Comput. Appl., vol. 68, pp. 213–229,
Jun. 2016, doi: 10.1016/j.jnca.2016.02.021.
[8] S. Rao, A. K. Verma, and T. Bhatia, “A review on social spam detection:
Challenges, open issues, and future directions,” Expert Syst. Appl.,
vol. 186, Dec. 2021, Art. no. 115742, doi: 10.1016/j.eswa.2021.115742.
[9] S. Lee et al. “Towards secure intrusion detection systems
using deep learning techniques: Comprehensive analysis and
review,” J. Netw. Comput. Appl., vol. 187, Aug. 2021, Art. no. 103111,
doi: 10.1016/j.jnca.2021.103111.
[10] A. Cherif, A. Badhib, H. Ammar, S. Alshehri, M. Kalkatawi, and
A. Imine, “Credit card fraud detection in the era of disruptive technologies: A systematic review,” J. King Saud Univ.-Comput. Inf. Sci., vol. 35,
no. 1, pp. 145–174, 2022, doi: 10.1016/j.jksuci.2022.11.008.

HAIDER et al.: ENERGY-EFFICIENT SELF-SUPERVISED TECHNIQUE TO IDENTIFY ABNORMAL USER

[11] T. Taleb, C. Benzaïd, R. A. Addad, and K. Samdanis, “AI/ML
for beyond 5G systems: Concepts, technology enablers & solutions,” Comput. Netw., vol. 237, Dec. 2023, Art. no. 110044,
doi: 10.1016/j.comnet.2023.110044.
[12] M. A. F. Pimentel, D. A. Clifton, L. Clifton, and L. Tarassenko,
“A review of novelty detection,” Signal Process., vol. 99, pp. 215–249,
Jun. 2014.
[13] R. Chalapathy and S. Chawla, “Deep learning for anomaly detection:
A survey,” 2019, arXiv: 1901.03407.
[14] S. Agrawal and J. Agrawal, “Survey on anomaly detection using data
mining techniques,” Procedia Comput. Sci., vol. 60, pp. 708–713, 2015,
doi: 10.1016/j.procs.2015.08.220.
[15] H. Fourati, R. Maaloul, L. Chaari, and M. Jmaiel, “Comprehensive
survey on self-organizing cellular network approaches applied to 5G
networks,” Comput. Netw., vol. 199, Nov. 2021, Art. no. 108435,
doi: 10.1016/j.comnet.2021.108435.
[16] M. Menchón, E. Talavera, J. Massa, and P. Radeva, “Behavioural
patterns discovery for lifestyle analysis from egocentric photostreams,” Pervasive Mobile Comput., vol. 95, Oct. 2023, Art. no. 101846,
doi: 10.1016/j.pmcj.2023.101846.
[17] X. Lian et al., “Recognition of typical environmental control behavior
patterns of indoor occupants based on temporal series association
analysis,” Build. Environ., vol. 234, Apr. 2023, Art. no. 110170,
doi: 10.1016/j.buildenv.2023.110170.
[18] D. Li et al., “Association between behavioral risks and Alzheimer’s
disease: Elucidated with an integrated analysis of gene expression
patterns and molecular mechanisms,” Neurosci. Biobehav. Rev., vol. 150,
Apr. 2023, Art. no. 105207, doi: 10.1016/j.neubiorev.2023.105207.
[19] J. Wu et al., “Sedentary behavior patterns and the risk of noncommunicable diseases and all-cause mortality: A systematic review and
meta-analysis,” Int. J. Nurs. Stud., vol. 146, Oct. 2023, Art. no. 104563,
doi: 10.1016/j.ijnurstu.2023.104563.

1639

[20] E. Quagliarini, G. Romano, and G. Bernardini, “Investigating pedestrian
behavioral patterns under different floodwater conditions: A video
analysis on real flood evacuations,” Safety Sci., vol. 161, May 2023,
Art. no. 106083, doi: 10.1016/j.ssci.2023.106083.
[21] X. Yi et al., “Gas-theft suspect detection among boiler room users:
A data-driven approach,” IEEE Trans. Knowl. Data Eng., vol. 34, no. 12,
pp. 5796–5808, 1 Dec. 2022, doi: 10.1109/TKDE.2021.3062707.
[22] J. Bian, L. Wang, R. Scherer, M. Woźniak, P. Zhang, and W. Wei,
“Abnormal detection of electricity consumption of user based on
particle swarm optimization and long short term memory with the
attention mechanism,” IEEE Access, vol. 9, pp. 47252–47265, 2021,
doi: 10.1109/ACCESS.2021.3062675.
[23] Z. Wang, S. Li, X. Zhang, and G. Feng, “Exploring abnormal behavior
in swarm: Identify user using adversarial examples,” IEEE Trans.
Emerg. Topics Comput. Intell., vol. 7, no. 1, pp. 250–260, Feb. 2023,
doi: 10.1109/TETCI.2022.3201294.
[24] A. Naser, A. Lotfi, M. D. Mwanje, and J. Zhong, “Privacy-preserving,
thermal vision with human in the loop fall detection alert system,” IEEE
Trans. Hum.-Mach. Syst., vol. 53, no. 1, pp. 164–175, Feb. 2023,
doi: 10.1109/THMS.2022.3203021.
[25] S. Dong, Y. Xia, and T. Peng, “Network abnormal traffic detection
model based on semi-supervised deep reinforcement learning,” IEEE
Trans. Netw. Service Manag., vol. 18, no. 4, pp. 4197–4212, Dec. 2021,
doi: 10.1109/TNSM.2021.3120804.
[26] Z. Peng, M. Luo, J. Li, L. Xue, and Q. Zheng, “A deep multiview framework for anomaly detection on attributed networks,” IEEE
Trans. Knowl. Data Eng., vol. 34, no. 6, pp. 2539–2552, Jun. 2022,
doi: 10.1109/TKDE.2020.3015098.
[27] U. Islam, A. Al-Atawi, H. S. Alwageed, M. Ahsan, F. A. Awwad, and
M. R. Abonazel, “Real-time detection schemes for memory DoS (MDoS) attacks on cloud computing applications,” IEEE Access, vol. 11,
pp. 74641–74656, 2023, doi: 10.1109/ACCESS.2023.3290910.
PAPER_TEXT
