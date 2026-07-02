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
# [082] Flow Transformer: A Novel Anonymity Network Traffic Classifier with Attention Mechanism
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
编号：082
题名：Flow Transformer: A Novel Anonymity Network Traffic Classifier with Attention Mechanism
年份：2021
DOI：10.1109/msn53354.2021.00045
来源：2021 17th International Conference on Mobility, Sensing and Networking (MSN)
PDF：paper/10.1109_msn53354.2021.00045.pdf
已有粗分类：其他AI安全与跨域异常检测
二级关联：加密流量分类与应用识别
相关性：中相关，分数 7
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\082.txt
- 原始字符数：40819
- 本次发送字符数：40819
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
2021 17th International Conference on Mobility, Sensing and Networking (MSN) | 978-1-6654-0668-0/21/$31.00 ©2021 IEEE | DOI: 10.1109/MSN53354.2021.00045

2021 17th International Conference on Mobility, Sensing and Networking (MSN)

Flow Transformer: A Novel Anonymity Network
Trafﬁc Classiﬁer with Attention Mechanism
Ruijie Zhao†¶ , Yiteng Huang†¶ , Xianwen Deng† , Zhi Xue† , Jiabin Li† , Zijing Huang‡ , and Yijun Wang†∗

† School of Electronic Information and Electrical Engineering, Shanghai Jiao Tong University, Shanghai, China
‡ School of Computer Science, Fudan University, Shanghai, China
¶ Contributed Equally

∗ Corresponding Author

Abstract—Supervising anonymity network is a critical issue
in the ﬁeld of network security, and traditional trafﬁc analysis
methods cannot cope with complex anonymity trafﬁc. In recent
years, the trafﬁc analysis method based on deep learning has
achieved good performance. However, most of the existing studies
do not consider the temporal-spatial correlation of the trafﬁc,
and only use a single ﬂow for classiﬁcation. A few works take
continuous ﬂows as ﬂow sequence for trafﬁc classiﬁcation, but
they do not distinguish the different importance of each ﬂow. To
tackle this issue, we propose a novel ﬂow-based trafﬁc classiﬁer
called F LOW T RANSFORMER to classify anonymity network trafﬁc. F LOW T RANSFORMER uses multi-head attention mechanism to
set higher weights for important ﬂows, and extracts ﬂow sequence
features according to the importance weights. Besides, the RFbased feature selection method is designed to select the optimal
feature combination, which can effectively avoid the insigniﬁcant
features from reducing the performance and efﬁciency of the
classiﬁer. Experimental results on two real-world trafﬁc datasets
demonstrate that the proposed method outperforms state-of-theart methods with a large margin.
Index Terms—Anonymity network, trafﬁc classiﬁcation, deep
learning, transformer, attention mechanism.

in various network violations, which brings new challenges
to network supervision. Some studies [1], [2] analyzed the
structure and content of Tor and I2P, which pointed out
that there is a large amount of illegal content in anonymity
networks. Thus, it is necessary to adopt effective methods to
supervise anonymity networks.
With the public release of anonymity network datasets
ISCX2016 and Anon17 [3], [4], the classiﬁcation of anonymity
network trafﬁc has also become a hot research ﬁeld. To
identify anonymity network services in massive and complex
trafﬁc data, many studies have used machine learning (ML)
algorithms such as Naive Bayes (NB), Random Forest (RF),
k-Nearest Neighbor (KNN) as classiﬁers and achieved good
performance [3]–[6]. However, the ML-based methods have
some constraints, which have limited feature extraction capabilities and require manual feature selection. Deep learning
(DL) algorithms have better feature extraction capabilities and
have been widely used in trafﬁc classiﬁcation tasks recently.
For instance, the Convolutional Neural Network (CNN) [7]–
[9] and the Long Short-Term Memory (LSTM) [10] have
better performance in classifying network trafﬁc, and the
accuracy of classifying application trafﬁc is more than 80%.
However, most of the aforementioned methods only consider
the characteristics of a single ﬂow, i.e., do not consider the
relationship between the ﬂows. Since each ﬂow is regarded as
an isolated individual and is sequentially input into the neural
network for feature extraction, the relationship between the
ﬂows is not effectively utilized. According to the temporal
and spatial correlation of the trafﬁc, there are usually some
correlations among multiple continuous ﬂows generated in a
short period of time. Although some works [11]–[14] regarded
continuous multiple ﬂows as a ﬂow sequence for feature
extraction, they did not distinguish the importance of different
ﬂows. Real-world trafﬁc is often mixed with unimportant or
irrelevant ﬂows, which will adversely affect the identiﬁcation
performance of such methods. To achieve an anonymity network trafﬁc classiﬁer with excellent performance, we design
our method from the following three key points:

I. I NTRODUCTION
With the continuous development of Internet services, people pay more attention to the privacy and security of the
Internet, which can be well meet by anonymity networks.
In recent years, anonymity communication technology has
developed rapidly, and onion routing theory based on the MIX
network has been widely used. Many anonymity networks (e.g.
Tor1 , I2P2 , JonDoNym3 , etc.) are implemented based on the
MIX network. Based on the different anonymity characteristics
of these networks, a variety of technologies (e.g. content
encryption, multi-hop mechanism, trafﬁc obfuscation) are used
to realize the hiding of communication relationships and
content. At present, the number of anonymity network users
has reached millions. According to the statistics on Tor and
I2P ofﬁcial websites, about 3 million users use Tor repeaters
to connect to the Internet, and 36,000 I2P network routing
nodes are running.
However, while the anonymity network brings privacy protection and greater freedom to ordinary users, it also hides the
identity information of malicious users. Malicious users use
anonymity networks to evade network supervision and engage

Use ﬂow sequence for classiﬁcation: The ﬂow sequence
is composed of continuous ﬂows in time, which obviously
contains more information than a single ﬂow.
• Distinguish the importance of ﬂows: To reduce the
noise brought by irrelevant ﬂows and pay more attention
•

1 https://www.torproject.org/
2 https://geti2p.net/
3 https://anonymous-proxy-servers.net/

978-1-6654-0668-0/21/$31.00 ©2021 IEEE
DOI 10.1109/MSN53354.2021.00045

223

Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:02 UTC from IEEE Xplore. Restrictions apply.

to important ﬂows, it is necessary to distinguish the
importance of different ﬂows in the ﬂow sequence.
• Select the optimal feature combination: Dozens of
features are parsed from the original trafﬁc, and feature
selection can avoid the insigniﬁcant features from reducing the performance and efﬁciency of the classiﬁer.
Based on the aforementioned ﬁrst two key design points,
we propose a novel ﬂow-based anonymity network trafﬁc
classiﬁer with multi-head attention mechanism, called F LOW
T RANSFORMER. Based on the third point, we adopt the RFbased method to select the optimal feature combination. In our
proposed method, the ﬂow sequence is the input feature, which
is composed of multiple continuous ﬂows within a certain
time range. We represent the input ﬂow sequence as three
vectors of query (Q), key (K), and value (V), where Q and
K are used to extract representative features of the ﬂow, and
V is the information of the ﬂow itself. Through an effective
multi-head attention mechanism (i.e calculate Q · K), F LOW
T RANSFORMER can distinguish the importance of different
ﬂows in each ﬂow sequence. The major contributions of the
proposed work are three-fold:
• We propose an anonymity network trafﬁc classiﬁer with
multi-head attention mechanism, which can pay more
attention to important ﬂows and extract ﬂow sequence
features more effectively. To the best of our knowledge,
this is the ﬁrst work to use the multi-head attention
mechanism to distinguish the importance of different
ﬂows in each ﬂow sequence.
• Insigniﬁcant features in the ﬂow can be characterized as
noise under certain conditions, which can have a very
adverse effect on the identiﬁcation result. In addition,
too many features will bring more model parameters,
which leads to slower training and classiﬁcation. Thus,
in order to improve the performance and efﬁciency of
the classiﬁer, we adopt the RF-based method to select
the optimal feature combination.
• To comprehensively evaluate the effectiveness and generality of F LOW T RANSFORMER, we conducted experiments on SJTU-AN21 and ISCXVPN2016 datasets. Experiments show that F LOW T RANSFORMER can achieve
better performance than other classiﬁers.

detect Tor trafﬁc through time features. The experimental results show that only 10 time features are needed to effectively
detect different applications in Tor trafﬁc. Elike et al. [16]
proposed a Tor network off-line trafﬁc classiﬁcation system
using SVM classiﬁer to improve the performance of trafﬁc
classiﬁcation. Montieri et al. [17] proposed the classiﬁcation
of different anonymous services at different granularity levels,
which uses ﬁve ML algorithms to classify anonymity services
with a maximum accuracy of 85.8%.
The above results show that these ML-based methods can
achieve good classiﬁcation accuracy in the face of uncomplicated network trafﬁc. However, they cannot cope with increasingly complex network trafﬁc. Due to better robustness and
feature extraction capabilities, DL-based method has become
the most ideal trafﬁc classiﬁcation method. Wang et al. [7],
[8] transformed the problem of trafﬁc classiﬁcation into an
end-to-end image classiﬁcation problem, and proposed an encrypted trafﬁc classiﬁcation method based on 2D-CNN, which
achieved good accuracy by classifying trafﬁc images. Chen et
al. [18] proposed a capsule neural network method to identify
encrypted trafﬁc and achieved higher classiﬁcation accuracy.
Lotfollahi et al. [19] proposed a trafﬁc classiﬁcation model
based on CNN combined with stacked autoencoder (SAE),
which achieves more effective classiﬁcation by reconstructing
the characteristics of raw trafﬁc data.
The aforementioned methods automatically extract the characteristics of ﬂows, but ignore the temporal-spatial correlation
of the trafﬁc or the different importance of the ﬂow. Thus, we
explore the problem of anonymity network trafﬁc classiﬁcation
from the perspective of ﬂow sequence. Our goal is to learn
the importance of different ﬂows and apply it for feature
extraction.
III. P RELIMINARIES
In this section, we introduce some background of anonymity
network trafﬁc classiﬁers, including the operating mechanism
of anonymity networks and the overview of Transformer.
A. Anonymity Network
The three most popular anonymous networks are Tor, I2P
and JonDonym. Tor is an anonymity communication network
with the largest number of users. It is based on TCP and
uses a multi-hop mechanism to build communication links.
In an established communication link, between the ingress
node and the egress node, the Tor network will randomly
select more than three relay nodes from the directory server.
Each relay node only knows its previous and next nodes,
the selection of nodes is random, and the link is constantly
changing. At the same time, the data in the Tor network
link is hidden in multiple encryption layers, and all communications are encrypted layer by layer. I2P is an improved
anonymity network based on Tor, which removes the central
node and adopts a completely distributed structure to improve
the anonymity and stability of the network. It uses a multi-level
encrypted tunnel mechanism to hide the identity information
and communication relationship of the communicating parties.

II. R ELATED W ORK
The task of network trafﬁc classiﬁcation has been continuously concerned by researchers, but not all network trafﬁc
analysis methods are suitable for anonymity network trafﬁc.
In this section, we will introduce the existing research status
of anonymity network or other encrypted network trafﬁc
classiﬁcation methods.
The anonymity network uses encryption for communication
and transmission. Thus, methods such as deep packet inspection (DPI) [15] that requires analysis of packet information
cannot classify encrypted trafﬁc. Recently, researchers identify
anonymity network trafﬁc by analyzing behavior and statistical
characteristics, which are mainly based on ML or DL algorithms. Lashkari et al. [3] proposed a ML-based method to

224
Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:02 UTC from IEEE Xplore. Restrictions apply.

j-th feature

Output

MLP

FT
Units

Flow Sequences

Ă

Raw Traffic Data

Radom Forst

High

Input

i-th flow

IMPOTRANCE
uppQuartileIat
pktps
ipMinTTL
ipMaxTTL
dsIqdIat
MaxIAT

GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV
GLUSNWSVWFQWĂE\WSV

Low

Feature Selection

Flow Transformer

Fig. 1. Overview of proposed method for anonymity network trafﬁc classiﬁcation. The ﬂow sequence represents a set of continuous multiple ﬂows. The Flow
Transformer Unit (FT Unit) is a ﬂow sequence feature extraction unit with multi-head attention mechanism.

JonDonym provides users with anonymous services through
multiple hybrid cascades. There is a set of two or three
encrypted hybrid servers in each hybrid cascade. Unlike Tor,
the link of the JonDonym network is ﬁxed. The user can select
the link for data transmission, but cannot change the mix of
different nodes on the link.
Due to the application of encryption technology, the classiﬁcation of anonymous network trafﬁc is more challenging.

ﬂow sequence, which realizes reasonable and effective feature
extraction of the ﬂow sequence.
IV. S CHEME OF A NONYMITY N ETWORK T RAFFIC
C LASSIFICATION
In this section, we introduce the scheme of anonymity
network trafﬁc classiﬁcation. After data preprocessing and
feature selection, F LOW T RANSFORMER is adopted to realize
the anonymity services classiﬁcation. The overview of the
proposed method is shown in Fig. 1 and the process of our
approach is summarized in Algorithm 1.

B. Transformer with Multi-head Attention Mechanism
The Transformer was ﬁrst proposed by Vaswani et al. [20]
in 2017 and has achieved great success in the ﬁeld of
NLP [21] and CV [22]. The Transformer employs an encoderdecoder structure. The self-attention layer is one of the most
important structures of the Transformer network, which uses
residual connections followed by layer normalization. Therefore, the output of self-attention layer is LayerN orm(x +
Sublayer(x)).
The self-attention layer employs h attention heads. The
results of different heads are concatenated together and a linear
transformation is used. As for attention head i, ﬁrst calculate
Qi , Ki , Vi by using linear transformation, representing Query
Matrix, Key Matrix and Value Matrix respectively.
Qi = xWiQ , Ki = xWiK , Vi = xWiV
WiQ , WiK , WiV

Algorithm 1 Pseudocode of the Proposed Method
Input: raw training dataset Dr , total epoch times n
Output: F LOW T RANSFORMER for anonymity network trafﬁc classiﬁcation
1: procedure Data Preprocessing (Dr )
2:
Compute the standardization result according to (4)
3:
Take continuous multiple ﬂows as ﬂow sequences
4:
Use RF-based method to select feature combination
5:
Dp ←− New training dataset after preprocessing
6: return Dp
7: procedure Flow Transformer Model (Dp )
8: while i ≤ n do
9:
Load the proposed network
10:
Input Dp into the network for training
11:
Update the model according to cross entropy loss
12:
Save F low T ransf ormeri model
13: end while
14: Save F low T ransf ormern as the ﬁnal model

(1)

dx ×dk

∈R
are learnable parameters. Then the
output of a single attention head is computed:
Qi K T
Attention(Qi , Ki , Vi ) = sof tmax( √ i )Vi
dk

(2)

Matrix calculation can be parallelized and reduce calculation
time. The essence is to use the similarity between the query
vector and the key vector as the weight, and perform a
weighted summation on all value vectors.
Multi-head attention allows the model to jointly attend to
information from different head:
M ultiHead(x) = Concat(head1 , · · · , headn )W O

A. Data Preprocessing
Before the training dataset and the testing dataset are applied
to the F LOW T RANSFORMER model, the data need to be
preprocessed. This involves two steps.
1) Standardization: Due to the large range of values with
different characteristics in each ﬂow, directly using raw data
for training will weaken the effect of characteristics with lower
values. In addition, the convergence speed of the model will be
very slow. Therefore, it is necessary to use the standardization
algorithm to ensure the reliability of data. The algorithm is
adopted to standardization the data as follows:
x−μ
(4)
z=
σ

(3)

hdk ×dx

where headi = Attention(Qi , Ki , Vi ) and W ∈ R
is used for linear transformation. Through multi-headed attention, information in different spaces can be extracted effectively, and richer feature information can be captured.
The Transformer network with multi-head attention mechanism can assign different attention weights to ﬂows in the
O

225
Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:02 UTC from IEEE Xplore. Restrictions apply.

where μ represents the mean of the original data, and σ the
standard deviation of the original data.
2) Flow Sequences Generation: The ﬂow sequence is
composed of multiple continuous ﬂows. As these ﬂows are
continuous in time, they can reﬂect user behavior during this
period. Some studies have shown that trafﬁc classiﬁcation by
the ﬂow sequence has better performance than by only one
ﬂow [11]–[14]. Thus, in our method, we take 8 continuous
ﬂows as a sequence.

Output

Traffic Feature
Extraction
Add & Norm

Self-attention Layer

N

Erri2 − Erri1
i=1

N

Cal cul ate At tention W eight

Multi-Head
Attention

Res

Feature selection is to remove insigniﬁcant features in
the generated ﬂows, which can make the generated results
better in line with effectiveness and timeliness. In terms
of effectiveness, insigniﬁcant features in the ﬂow can be
characterized as noise under certain conditions, which can
have a very adverse effect on the identiﬁcation result. In terms
of timeliness, the removal of these features can reduce the
calculation of statistics in ﬂow generation process and speed
up ﬂow generation. In addition, low-dimensional features will
also reduce the complexity and classiﬁcation time of the
feature extraction network.
RF algorithm is robust and easy to use, making it one of the
most popular ML algorithms for classiﬁcation tasks. Moreover,
RF algorithm can be employed to calculate the contribution of
each feature, which is effective in feature selection. A total of
84 initial features are extracted from the raw trafﬁc data. We
use RF-based method to evaluate the importance of these 84
features and perform feature selection. The calculation of the
j-th feature contribution based on the RF method is divided
into four steps. First, randomly sample the original training
set D as the in-bag data Din , and the unselected data as the
out-of-bag data Dout ; Next, use the in-bag data Din to train
the RF model. For the i-th decision tree in RF model, use the
corresponding out-of-bag data Dout to calculate the data error,
denoted as Erri1 ; Then, randomly add noise to all the sample
features, and calculate the error of Dout again, denoted as
Erri2 ; Finally, the contribution of the j-th feature is calculated
according to the following formula:

Q

K

V

Flow Transformer Unit u6

Feature Extraction Layer

B. RF-based Method for Feature Selection

cj =

3 Layers

MLP

i-th flow
Features

Fig. 2. The structure of F LOW T RANSFORMER.

reasonable and effective feature extraction of the ﬂow sequence.
The input of F LOW T RANSFORMER is a ﬂow sequence
consisting of 8 continuous ﬂows after feature selection. Continuous ﬂows can be regarded as a sequence input. The model
structure of F LOW T RANSFORMER is shown in Fig. 2. It
consists of 6 Flow Transformer units and 3 fully connected
layers. Two key sub-layers form a Flow Transformer unit,
namely self-attention layer and feature extraction layer.
The self-attention layer is mainly used to distinguish the
importance of different ﬂows in each ﬂow sequence. Query
Matrix, Key Matrix and Value Matrix are calculated by linear
transformations, denoted as Q, K and V . Here, Q and K
represent key information of the ﬂows, while V represents
the actual information of the ﬂows. The higher the similarity
between Q and K, the higher the correlation between the
ﬂow corresponding to Q and the ﬂow corresponding to K,
and therefore the higher the weight when V is weighted and
summed. The multi-head attention mechanism strengthens the
information interaction between related ﬂows and effectively
improves the feature extraction effect of the model on the ﬂow
sequence.
The feature extraction layer can strengthen the expressive
ability of the output. It is able to provide non-linear transformation functions that self-attention layer does not have.
It ﬁrst uses a fully connected layer to map features to a
larger dimensional feature space, then uses ReLU for nonlinear
screening, and ﬁnally uses another fully connected layer to
restore the features to the original dimension.
Each sub-layer uses the residual structure, and added layer
normalization at the end. The residual structure can solve the

(5)

where N represents the number of trees in the RF model. It
can be seen that if the accuracy of Dout drops signiﬁcantly
after random noise is added, it means that this feature has a
great inﬂuence on the prediction results of the sample, i.e., the
importance is relatively high. Based on this method, we sort
the importance of the initial features and optimize the feature
combination.
C. Flow Transformer Classiﬁer
Different from other methods, F LOW T RANSFORMER classiﬁer can assign different attention weights to different ﬂows
in the ﬂow sequence through the multi-head attention mechanism. The multi-head attention mechanism strengthens the
information interaction between related ﬂows, and can achieve

226
Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:02 UTC from IEEE Xplore. Restrictions apply.

degradation problem that occurs as the depth of the network
increases, while layer normalization can ensure the stability
of the data distribution and accelerate the convergence speed
of the model.
Finally, the output of Flow Transformer units is ﬂattened
and a MLP with three fully connected layers is used for
classiﬁcation. The ﬁnal layer has 10 or 7 neurons, which is
equal to the number of network service categories.

TABLE I
S UMMARY OF T HE DATASETS U SED FOR E VALUATION .

Dataset

V. E VALUATION
SJTU-AN21

In this section, we present and discuss our experimental
results. Especially, we answer the following three research
questions:
• RQ1: How effective is the RF-based method in feature
selection?
• RQ2: How well does F LOW T RANSFORMER work on
real-world anonymity network trafﬁc, identifying different
anonymity services?
• RQ3: How well does F LOW T RANSFORMER perform comparing to the state of art of trafﬁc classiﬁcation methods?

Category
Eepsites
IRC
Snark
Video
JonDonym
Bittorrent
Chat
FTP
Streaming
Browsing

1,825
3,009
7,284
12,577
1,254
198
624
364
949
1,130

1,197
484
1,784
581
967
76
150
184
598
958

Total

29,214

6,979

3,646
4,446
736
8,464
689
1,523
3,209

912
1,112
184
2,117
173
381
803

22,713

5,682

Browsing
FTP
P2P
VoIP
ISCXVPN2016
Email
Streaming
Chat

A. Dataset for Evaluation
The previous anonymity network datasets (i.e. ISCXTor2016 and Anon17) have become invalid due to the update
of the anonymity network version. The Tor network has
been signiﬁcantly changed in version 0.4.1.5 in 2018, which
adds circuit-level padding and SENDME units to prevent
deanonymization through trafﬁc analysis. The I2P network has
enabled the new protocol NTCP2 in version 0.9.36 in 2019.
The NTCP2 uses the Noise protocol framework to improve
the ability to resist DPI attacks. However, the previous two
anonymity network datasets were released before 2017 [3],
[4]. To make the classiﬁer applicable to the current anonymity
network trafﬁc analysis, in the latest version of the three most
popular anonymity networks (i.e. Tor, I2P, JonDonym), we
collected the trafﬁc data generated by 10 anonymity services.
This latest anonymity network trafﬁc dataset SJTU-AN214 is
publicly available for researchers.
In addition, encrypted trafﬁc has some similarities with
anonymous network trafﬁc, so the public encrypted trafﬁc
dataset ISCXVPN2016 is used to evaluate the generality of
the proposed method.
Details of these two datasets are summarized in TABLE I.
In the SJTU-AN21 dataset, Eepsites, IRC, Snark, and Video
are the four main anonymity services in the I2P network, and
Bittorrent, Chat, FTP, Streaming, and Browsing are the ﬁve
main anonymity services in the Tor network.

Train dataset Test dataset

Total

combination for subsequent experiments. To answer RQ2, we
analyze the training process of F LOW T RANSFORMER, and
discuss the confusion matrix of the classiﬁcation results on
the test dataset. To answer RQ3, we compare the classiﬁcation
performance of F LOW T RANSFORMER and other state of art
of trafﬁc classiﬁcation methods on the test dataset. It should be
noted that both SJTU-AN21 and ISCXVPN2016 datasets are
used to conduct the above evaluation experiments. To make the
experimental evaluation clearer, we introduce the experimental
environment and evaluation metrics as follows.
1) Experimental Environment: Our anonymity network
trafﬁc is collected by conﬁguring the mirror port of the switch
and using the real-time trafﬁc capture tool tcpdump. The raw
trafﬁc data of SJTU-AN21 and ISCXVPN2016 datasets are all
pcap ﬁles, which need to calculate statistical features to enrich
feature information. Thus, we use Tranalyzer, a lightweight
packet analyzer, to calculate the statistical characteristics of the
raw trafﬁc data. All the evaluations are conducted in Python
3.7 with the PyTorch framework of version 1.8.1 and running
on the PC with Intel® Core™ i7-10700@2.90 GHz, 16 GB
RAM, a 512G SSD, and an NIVIDIA GeForce RTX3060
12GB.
2) Evaluation Metrics: The related evaluation metrics used
in the evaluation are as follows. There are two situations in
which the classiﬁer performs a correct classiﬁcation. One is the
true positive Tp decision, which correctly classiﬁes the trafﬁc
corresponding to the service. The other is true negative Tn
decision, i.e. the trafﬁc of other services is correctly classiﬁed.

B. Experiment Setup
We design several experiments to evaluate the efﬁcacy of
our method for classifying anonymity network trafﬁc. To
answer RQ1, we evaluate the performance of the RF-based
feature selection method and the traditional PCA method on
different number of features, and determine the optimal feature
4 https://github.com/iZRJ/The-SJTU-AN21-Dataset

227
Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:02 UTC from IEEE Xplore. Restrictions apply.

(a)

(b)

Fig. 3. Classiﬁcation accuracy with different numbers of features on (a) SJTU-AN21 dataset, (b) ISCXVPN2016 dataset. The shadow in the ﬁgure indicates
the variation range of the top-3 accuracy, and the connection point represents the second highest accuracy using different number of features.

Moreover, we can see that if the number of features is
less than 20, satisfactory performance cannot be achieved on
either the SJTU-AN21 dataset or the ISCXVPN2016 dataset.
On the SJTU-AN21 dataset, when the number of features is
50, the F LOW T RANSFORMER reaches the highest accuracy
of 85.29%. On ISCXVPN2016, the highest accuracy of the
classiﬁer is 95.29% when the number of features is 35. Due to
the use of more complex and up-to-date encryption technology,
the anonymity network requires more features to effectively
classify trafﬁc than encrypted networks. We use the above
optimal feature combination on these two datasets to conduct
subsequent experiments.

The corresponding erroneous output of the classiﬁer is false
positive Fp decision and false negative Fn decision. Based on
the above deﬁnition, Recall, Precision and Fn can be obtained:
Recall =

Tp
Tp + Fn

P recision =

Fn =

Tp
T p + Fp

(n2 + 1)P recision · Recall
(n2 P recision + Recall)

(6)

(7)

(8)

where n is a penalty factor to provide more weight to recall,
and we choose F1 in this paper.

D. Performance of Flow Transformer Classiﬁer (to RQ2)
The train accuracy and loss using the F LOW T RANS classiﬁer for SJTU-AN21 and ISCXVPN2016
datasets are shown in Fig. 4. The loss of F LOW T RANS FORMER classiﬁer decreases rapidly and eventually converge
to near zero, which indicates that the classiﬁer has learned the
feature information of the training dataset very well. Beneﬁting
from the excellent feature extraction ability of the F LOW
T RANSFORMER for network trafﬁc, its ﬁnal training accuracy
is very high.
To comprehensively evaluate the classiﬁcation performance
of F LOW T RANSFORMER, we analyze the confusion matrix
of the classiﬁcation results on the test datasets. As shown in
Fig. 5, our classiﬁer can effectively classify the trafﬁc generated by different services. In Fig. 5(a), the trafﬁc of the three
types of anonymity networks (i.e., I2P, Tor, JonDoNym) are
correctly distinguished. Some of the Chat services of the Tor
network are misclassiﬁed as the Streaming service. Since some
ﬁles are transferred during the Chat service, the corresponding
trafﬁc is very similar to Streaming service. In Fig. 5(b), we can
see that the classiﬁer has some classiﬁcation errors between
the FTP and Chat service trafﬁc. By referring to the ofﬁcial
description of the ISCXVPN2016 dataset, we found that both

C. Efﬁcacy of RF-based Feature Selection Method (to RQ1)

FORMER

As we mentioned before, insigniﬁcant features can adversely affect the performance of the classiﬁer. At the same
time, more features mean longer training time and prediction
time. Thus, in order to obtain the optimal feature combination,
we ﬁrst conduct the evaluation of feature selection.
In this stage, we choose another representative feature
selection method, principal component analysis (PCA) algorithm to compare the performance of feature selection. As an
unsupervised method, the PCA algorithm is widely used for
data analysis. According to the RF-based and the PCA-based
feature selection methods, we investigate the performance of
the classiﬁer with different number of features (i.e., the top
J features in the rank). The experimental results are shown
in Fig. 3. To avoid the contingency of the classiﬁer performance, we take top-3 accuracy during the training process.
The shadow in the ﬁgure indicates the variation range of
the top-3 accuracy, and the connection point represents the
second highest accuracy using different number of features.
Obviously, the RF-based method for feature selection has
better effectiveness and stability.

228
Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:02 UTC from IEEE Xplore. Restrictions apply.

(a)

(a)

(b)

(b)
Fig. 5. Performance confusion matrices of F LOW T RANSFORMER classiﬁer
on (a) SJTU-AN21 dataset, (b) ISCXVPN2016 dataset.

Fig. 4. Train accuracy and loss of F LOW T RANSFORMER classiﬁer on (a)
SJTU-AN21 dataset, (b) ISCXVPN2016 dataset.

services contain the trafﬁc generated by the Skype application,
which is the main cause of misclassiﬁcation.

It can be seen from TABLE II that our F LOW T RANS FORMER achieves the best performance in both two datasets in
terms of all evaluation metrics. We can observe that the classiﬁcation results of traditional ML-based methods are usually
not ideal, demonstrating the limited ability of these methods
to classify complex network trafﬁc. The classiﬁcation performance of the 2D-CNN and 3D-CNN models (i.e., directly
reading pcap ﬁles without calculating the statistical features)
is very limited. CNN and LSTM models use statistical features
and the ﬂow sequence to achieve signiﬁcant performance
improvements. However, due to the lack of mining the inherent
information of the ﬂow sequence, it is still unable to achieve
high accuracy. We introduce a self-attention mechanism on
the LSTM model, and the detection performance has been
improved by about 3%, which shows that the attention mechanism is very effective for the ﬂow sequence. Our F LOW
T RANSFORMER uses the multi-head attention mechanism to
distinguish the importance of ﬂows, and the feature extraction
layer to fully extract ﬂow sequence features, which greatly

E. Comparison with Other Methods (to RQ3)
We compare our with the following nine baseline methods
on SJTU-AN21 and ISCXVPN2016. The ML models (i.e. NB,
RF, SVM, and C4.5) are implemented through the popular
data mining tool Weka. CNN, LSTM, and LSTM+Attn models all use the structure similar to F LOW T RANSFORMER (i.e.
the same number of layers and input/output size), and use ﬂow
sequences as input for classiﬁcation. In addition, LSTM+Attn
uses LSTM combined with a self-attention mechanism to pay
attention to important ﬂows in the ﬂow sequence. 2D-CNN is
proposed by Wang et al. [7] that directly reads trafﬁc pcap ﬁles
and converts them into images for classiﬁcation. 3D-CNN is
an improved model of the 2D-CNN proposed by Zhang et al.
[9], which uses multiple channels to enrich feature information
during image conversion.

229
Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:02 UTC from IEEE Xplore. Restrictions apply.

R EFERENCES

TABLE II
T HE P ERFORMANCE C OMPARISON WITH OTHER M ETHODS .

Model

SJTU-AN21
Acc. Prec.
F1

NB
RF
SVM
C4.5

34.0% 34.1% 27.0% 54.7% 68.1% 57.2%
67.9% 73.7% 67.1% 85.8% 88.0% 85.8%
46.8% 58.0% 42.8% 71.8% 75.2% 72.0%
48.4% 55.8% 48.7% 78.5% 78.0% 76.2%

[1] N. P. Hoang, P. Kintis, M. Antonakakis and M. Polychronakis, “An
empirical study of the i2p anonymity network and its censorship
resistance”, in Internet Measurement Conference 2018, Boston, MA,
USA, Oct. 31– Nov. 2, 2018, pp. 379–392.
[2] L. Liu, H. Zhang, J. Shi, X. Yu and H. Xu, “I2P Anonymous
Communication Network Measurement and Analysis”, in International
Conference on Smart Computing and Communication, Birmingham, UK,
Oct. 11–13, 2019, pp. 105–115.
[3] A. H. Lashkari, et al., “Characterization of tor trafﬁc using time
based features,” in 3rd International Conference on Information System
Security and Privacy, Porto, Portugal, Feb. 19–21, 2017, pp. 253–262.
[4] K. Shahbar and A. N. Zincir-Heywood, “Packet momentum for identiﬁcation of anonymity networks,” Journal of Cyber Security and Mobility,
vol. 6, no. 1, pp. 27–56, 2017.
[5] H. Yin and Y. He, “I2P anonymous trafﬁc detection and identiﬁcation”,
in 5th International Conference on Advanced Computing & Communication Systems, Coimbatore, India, Mar. 15–16, 2019, pp. 157–162.
[6] A. Cuzzocrea, F. Martinelli, F. Mercaldo and G. Vercelli, “Tor trafﬁc
analysis and detection via machine learning techniques”, in 2017 IEEE
International Conference on Big Data (Big Data), Boston, MA, USA,
Dec. 11–14, 2017, pp. 4474–4480.
[7] W. Wang, M. Zhu, X. Zeng, X. Ye and Y. Sheng, “Malware trafﬁc
classiﬁcation using convolutional neural network for representation
learning”, in 2017 International Conference on Information Networking
(ICOIN), Da Nang, Vietnam, Jan. 11–13, 2017, pp. 712–717.
[8] W. Wang, M. Zhu, J. Wang, X. Zeng and Z. Yang, “End-to-end encrypted
trafﬁc classiﬁcation with one-dimensional convolution neural networks”,
in 2017 IEEE International Conference on Intelligence and Security
Informatics (ISI), Beijing, China, Jul. 22–24, 2017, pp. 43–48.
[9] J. Zhang, F. Li, F. Ye and H. Wu, “Autonomous unknown-application
ﬁltering and labeling for DL-based trafﬁc classiﬁer update,” in IEEE
INFOCOM 2020, Toronto, Canada, Jul. 6–9, 2020, pp. 397–405.
[10] H. Yao, et al., “Identiﬁcation of encrypted trafﬁc through attention
mechanism based long short term memory”, IEEE Transactions on Big
Data, doi: 10.1109/TBDATA.2019.2940675, 2019.
[11] T. Shapira and Y. Shavitt, “Flowpic: Encrypted internet trafﬁc classiﬁcation is as easy as image recognition”, in IEEE INFOCOM WKSHPS
2019, Paris, France, Apr 29 – May 2, 2019, pp. 680–687.
[12] Y. Lin, J. Wang, Y. Tu, L. Chen and Z. Dou, “Time-related network intrusion detection model: a deep learning method,” in IEEE GLOBECOM
2019, Waikoloa, USA, Dec. 9–13, 2019, pp. 1–6.
[13] R. Zhao, et al., “An efﬁcient and lightweight approach for intrusion
detection based on knowledge distillation,” in IEEE ICC 2021, Montreal,
Canada, Jun. 14–23, 2021, pp. 1–6.
[14] R. Zhao, J. Yin, Z. Xue, G. Gui, B. Adebisi, T. Ohtsuki, H.
Gacanin and H. Sari, “An efﬁcient intrusion detection method based
on dynamic autoencoder,” IEEE Wireless Communications Letters, doi:
10.1109/LWC.2021.3077946.
[15] T. Bujlow, et al., “Independent comparison of popular DPI tools for
trafﬁc classiﬁcation”, Computer Networks, vol. 76, pp. 75–89, 2015.
[16] E. Hodo, et al., “Machine learning approach for detection of nontor
trafﬁc”, in 12th International Conference on Availability, Reliability and
Security, Reggio Calabria, Italy, Aug. 29 – Sep. 1, 2017, pp. 1–6.
[17] A. Montieri, D. Ciuonzo, G. Aceto and A. Pescapé, “Anonymity services
tor, i2p, jondonym: classifying in the dark (web)”, IEEE Transactions on
Dependable and Secure Computing, vol. 17, no. 3, pp. 662–675, 2018.
[18] Z. Chen, et al., “Length matters: Fast internet encrypted trafﬁc service
classiﬁcation based on multi-PDU lengths”, in 2020 16th International
Conference on Mobility, Sensing and Networking (MSN), Tokyo, Japan,
Dec. 17–19, 2020, pp. 531–538.
[19] M. Lotfollahi, M. J. Siavoshani, R. S. H. Zade and M. Saberian, “Deep
packet: A novel approach for encrypted trafﬁc classiﬁcation using deep
learning”, Soft Computing, vol. 24, no. 3, pp. 1999-2012, 2020.
[20] A. Vaswani, et al., “Attention is all you need”, Advances in neural
information processing systems (NIPS), pp. 5998–6008, 2017.
[21] J. Devlin, MW. Chang, K. Lee, and K. Toutanova, “Bert: Pre-training
of deep bidirectional transformers for language understanding”, North
American Association for Computational Linguistics (NAACL), pp.
4171–4186, 2019.
[22] A. Dosovitskiy, et al., “An image is worth 16x16 words: transformers
for image recognition at scale”, in International Conference on Learning
Representations (ICLR), Virtual, May 4–7, 2021, pp. 1–21.

ISCXVPN2016
Acc. Prec.
F1

CNN
78.3% 78.4% 77.0% 90.2% 90.7% 90.4%
LSTM
79.1% 80.2% 77.9% 90.2% 90.8% 90.3%
2D-CNN 65.0% 70.8% 66.9% 86.2% 86.7% 86.1%
3D-CNN 71.9% 75.6% 73.2% 87.6% 88.1% 87.9%
LSTM+Attn 81.5% 82.1% 81.1% 92.3% 92.9% 92.3%
Ours

86.0% 86.8% 85.5% 95.2% 95.3% 95.2%

improves the classiﬁcation performance of anonymity network
and encrypted network trafﬁc. Further, we also try to add
CNN, LSTM or autoencoder network to the existing network
structure of F LOW T RANSFORMER for feature extraction.
Experimental results show that these methods will not improve
the performance of the classiﬁer, and we do not want our
F LOW T RANSFORMER to be a highly complex model. Thus,
the multi-head attention mechanism and the feature extraction
layer of F LOW T RANSFORMER are all we need.
VI. C ONCLUSION
In this paper, a novel ﬂow-based trafﬁc classiﬁer called
F LOW T RANSFORMER is proposed and successfully applied
to classifying anonymity network and encrypted network trafﬁc. The model uses the multi-head attention mechanism to
effectively distinguish the importance of the ﬂow in the ﬂow
sequence, and the feature extraction layer to fully extract the
ﬂow sequence features. Besides, to avoid the insigniﬁcant
features from reducing the performance and efﬁciency of the
classiﬁer, we use the RF-based feature selection method to
select the optimal feature combination. Experiments on two
real-world trafﬁc datasets show that the classifying accuracy
of the proposed model is superior to existing models. In the
future, we will consider combining character features in trafﬁc
to further improve classiﬁcation performance. Since the F LOW
T RANSFORMER is a general classiﬁer for network trafﬁc, we
can also apply it to other trafﬁc analysis tasks, such as network
intrusion detection.
ACKNOWLEDGMENT
This work was supported by the Foundation Item: Cyber Security from the National Key Research and Development Program of Shanghai Jiao Tong University under Grant
2019QY0703.

230
Authorized licensed use limited to: INDIAN INSTITUTE OF TECHNOLOGY MADRAS. Downloaded on August 19,2025 at 06:16:02 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
