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
# [518] Reliable Open-Set Network Traffic Classification
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
编号：518
题名：Reliable Open-Set Network Traffic Classification
年份：2025
DOI：10.1109/tifs.2025.3544067
来源：IEEE Transactions on Information Forensics and Security
PDF：paper/10.1109_tifs.2025.3544067.pdf
已有粗分类：加密流量分类与应用识别
二级关联：其他AI安全与跨域异常检测
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\518.txt
- 原始字符数：80052
- 本次发送字符数：80052
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

2313

Reliable Open-Set Network Traffic Classification
Xueman Wang , Yipeng Wang , Senior Member, IEEE, Yingxu Lai , Zhiyu Hao ,
and Alex X. Liu , Fellow, IEEE
Abstract—The widespread use of modern network communications necessitates effective resource control and management
in TCP/IP networks. However, most existing network traffic
classification methods are limited to labeled known classes and
struggle to handle open-set scenarios, where known classes coexist
with significant volumes of unknown classes of traffic. To solve
this problem more accurately and reliably, we propose RoNeTC.
This method achieves high-precision classification by enhancing
feature extraction and quantifying the reliability of classification
decisions through uncertainty estimation. For feature extraction,
we divide each packet of a flow into three views for parallel
training, integrating both local and global feature representations
across multiple packets to enhance accuracy. We devise a secondorder classification probability to quantify the reliability of
the classifier’s results and to visualize the reliability of openset flow classification in terms of uncertainty. Additionally, we
dynamically fuse classification decisions from multiple views,
evaluating decision uncertainty to classify known and unknown
flows and ensure robust, reliable results. We compare RoNeTC
with four state-of-the-art (SOTA) methods in six open-set scenarios. RoNeTC outperforms the other methods by an average of
25.94% in F1 across all open-set scenarios, indicating its superior
performance in open-set network traffic classification.
Index Terms—Network security and privacy, open-world network traffic classification, unknown classes, deep learning.

I. I NTRODUCTION

T

HIS paper focuses on network traffic classification in
open-set environments, which are scenarios that contain
both known and unknown classes of network traffic. Network
traffic classification is a task that associates network traffic
with application protocols or the applications that generate
the traffic. It is crucial for network security areas such as differentiated services, network intrusion detection, and resource
assignment [1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11].
However, with the rapid development of network technology,
a new challenge has emerges. This challenge arises from
the mismatch between the increasing number of unknown
application classes and the limitations of traditional classifiers,
Received 11 June 2024; revised 7 December 2024 and 24 January 2025;
accepted 10 February 2025. Date of current version 27 February 2025. This
work was supported in part by the National Natural Science Foundation of
China under Grant 62472011 and in part by the Beijing Natural Science
Foundation under Grant L244009. The associate editor coordinating the review
of this article and approving it for publication was Prof. Mika Ylianttila.
(Corresponding author: Yipeng Wang.)
Xueman Wang, Yipeng Wang, and Yingxu Lai are with the College
of Computer Science, Beijing University of Technology, Beijing 100124,
China (e-mail: wangxueman@emails.bjut.edu.cn; yipeng.wang1@gmail.com;
laiyingxu@bjut.edu.cn).
Zhiyu Hao is with the Zhongguancun Laboratory, Beijing 102629, China
(e-mail: haozy@zgclab.edu.cn).
Alex X. Liu is with Midea Group, Foshan 528311, China (e-mail:
alexliu360@outlook.com).
Digital Object Identifier 10.1109/TIFS.2025.3544067

Fig. 1. The red ‘×’ marks indicate instances where unknown classes have
been incorrectly classified as known classes.

which can only recognize known application classes. As
shown in Fig. 1, in open-set scenarios containing both known
and unknown classes, traditional closed-set classifiers fail to
identify unknown classes of flows. Typically, they wrongly
classify all unknown classes as known ones, significantly
reducing the accuracy of the classification results. To address
this issue, several scholars have begun initial explorations into
correctly classifying known and unknown application traffic in
open-set scenarios.
Open-set network traffic classification can be broadly categorized into two groups based on the type of model input:
packet payload-based methods [4], [5] and packet time seriesbased methods [1]. The packet payload method uses raw bytes
from the packet as model inputs. However, features focuses
solely on the byte contents within a packet, making it difficult
to capture the correlation between different packets of a flow.
Methods based on packet time series primarily use the total
packet length from the network layer as input and focus on
constructing the time series correlation of packets in a flow.
However, these methods often omit crucial protocol fields,
such as port number, window size, and server name indication,
in the transport or application layers, which are vital for
classifying network traffic.
Open-set network traffic classification can also be roughly
divided into two categories according to its threshold division:
methods based on classification probability thresholds [4], [5]
and methods based on gradient thresholds [1]. The classification probability threshold-based uses a softmax function
to output a classification probability value for each sample
and divides the probabilistic threshold to classify known and
unknown flow with the help of a Cumulative Distribution
Function (CDF) of probability scores. The gradient thresholdbased methods evaluate the feed-forward inference derived
from backpropagation and classify by evaluating gradient sensitivity for known and unknown classes flows. Both methods
use softmax to output the classification probability value of
the flow and assign the corresponding labels based on the
classification probability. However, since the softmax function
tends to inflates the classification probability values due to

1556-6021 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and
similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.
Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

2314

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Fig. 2. Classification probability density figure for known and unknown
classes output by softmax function.

its computational mechanism, leading to unreliable results
[12], [13]. This issue becomes more pronounced in open-set
scenarios.
As shown in Fig. 2, for the unknown class flows, the
softmax function still outputs highly confident classification
probability value (> 95%) and wrongly assigns the unknown
class flows to the known class label sets, resulting in unreliable
results.
In this paper, we propose RoNeTC, a Reliable OpenSet Network Traffic Classification. RoNeTC is based on
a key insight: Due to a priori knowledge of the known
classes, the classification decision output by the classifier for
known class flows, which is the probability mass function
of the sample, is highly certain. For unknown class flows,
the probability mass function is uncertain. Therefore, we
can deal with the classification problem of network traffic
in an open-set environment by quantifying the reliability of
the classifier’s output decision. This involves enhancing the
classifier’s decision process by utilizing uncertainty estimates,
adding a metric into the classifier’s decision in the form of
a second-order classification probability, and visualising the
reliability of the classification decision in an intuitively probabilistic manner. For known class flows, the classifier outputs a
classification probability value with a highly confident decision
reliability metric, leveraging prior knowledge from training.
In contrast, for unknown class flows, due to the absence of
training samples and inconsistency with known class distributions, the classifier still provides a classification probability
value but with a lower confidence decision metric. Using
this decision reliability metric, we can accurately distinguish
between known and unknown class flows and subdivide known
classes.
RoNeTC aims to classify known and unknown classes in
open-set scenarios while ensuring the reliability and robustness
of classification decisions. To fully utilize the effective information from packets, our input includes raw bytes from the
network layer, transport layer, and application layer of multiple
packets in one flow. Combined with multi-view learning, each
view captures global features across multiple packets and local
features within a single packet. To avoid inflated classification
probabilities from the softmax layer, we remove it and model
the second-order classification probabilities. This approach
provides trustworthy classification results with an uncertainty estimation metric for the reliability of the classification
decision.

Next, to measure the reliability of classification decisions,
we construct second-order classification probabilities using the
Dirichlet distribution. The Dirichlet distribution is parameterized with evidence supporting the classification, forming
a distribution of classification probabilities distributions and
expressing decision reliability through uncertainty estimates.
Finally, dynamically fuse classification decisions from multiple views. The uncertainty of each view’s classification
decision is used as a weight, resulting in the final reliable
classification decision and the overall decision uncertainty. In
open-set flow classification, we distinguish between known
and unknown classes based on decision uncertainty and further
subdivide the known classes of flows based on the probability
value of the decision.
Our major contributions in this paper can be concluded as
follows:
• We propose RoNeTC, a novel robust and reliable method
for open-set network traffic classification. RoNeTC
achieves reliable classification results by measuring the
degree of reliability of the classification decisions and
accurately distinguishing between known and unknown
classes based on decision uncertainty.
• We combine multi-view and global-local feature representations to achieve fine-grained feature characterization.
Reliable classification decisions are obtained by constructing second-order classification probabilities and
decision uncertainty estimates. In addition, we dynamically fuse classification decisions from multiple views
based on uncertainty, enhancing the reliability and robustness of open-set classification.
• We compare RoNeTC with four SOTA open-set classification methods across six open-set scenarios. The
experiments show that RoNeTC outperforms the other
methods in F1 by an average of 25.94% in all openset scenarios, demonstrating its superior classification
capabilities.
The rest of the paper proceeds as follows. In Section II, we
introduce several recent related works. In Sections III and IV,
we present the technical details of each phase of RoNeTC. In
Section V, we evaluate RoNeTC with real-world application
datasets. We compare RoNeTC with existing methods in
Section VI. Finally, we conclude our work in Section VII.
II. R ELATED W ORK
Network traffic classification can be broadly divided into
closed-set and open-set scenarios, depending on the application environment. Table I provides a summary of the related
work.
A. Network Traffic Classification in the Closed-Set Scenarios
In recent years, the field of network traffic classification
[2], [3], [4], [5], [6], [7], [8], [9], [18], [23] in a closedset setting has experienced rapid advancement, fueled by the
proliferation of deep learning techniques. Li et al. [2] were
the first to use deep learning techniques to analyze packet
payloads for network traffic classification. They designed a
BSNN network that consists of a recurrent neural network

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

WANG et al.: RELIABLE OPEN-SET NETWORK TRAFFIC CLASSIFICATION

2315

TABLE I
S UMMARY OF R ELATED W ORK ON N ETWORK T RAFFIC C LASSIFICATION

and an attention mechanism. Aceto et al. proposed MIMETIC
[3], a multi-model deep learning solution for network traffic
classification. MIMETIC enables the examination of network traffic from complementary views. Later, Aceto et al.
[14] expanded on the idea of multi-modality based on deep
learning and proposed DISTILLER, which combines deep
learning with multi-task learning. The aim of DISTILLER
is to overcome the limitations of single-task deep learning.
Nascita et al. [15] pioneered the application of deep learning
model interpretation in network classification by introducing
the MIMETIC-ENHANCED framework. This framework aims
to enhance the reliability and interpretability of network flows
using interpretable artificial intelligence (XAI) techniques.
Xiao et al. proposed EBSNN [16], an extended byte segment
neural network to classify network traffic. EBSNN divides
a packet into header segments and payload segments, which
are then fed into encoders composed of the recurrent neural
networks with the attention mechanism. Wang et al. [10]
proposed TaTic, a two-stage early classification scheme for
encrypted traffic, which quickly distinguishes between ‘easy
flow’ and ‘hard flow’ by observing only the first few packets.
Nascita et al. [19] employed advanced interpretable techniques
to analyze flow reliability at the biflow level within a multimodal, multitask framework, thereby achieving faster and
more efficient classification models.
B. Network Traffic Classification in the Open-Set Scenarios
All of the above methods assume that there are only known
class flows in the environment. However, in real applications there is a mixture of known class flows and unknown
class flows. Therefore, open-set network traffic classification,
which is crucial for improving network traffic management,
has become a focus of attention. AutoUA [4] is an openset flow classification method for autonomous learning. This
method involves conducting flow classification on an open-set
classification dataset using a classifier trained with knownclass samples, and then setting a probability threshold to
classify known and unknown-class. GradBP [1] is similar to
AutoUA, but it differs in threshold calculation. Instead of
using a probability threshold, it employs a gradient threshold.
Here, the threshold is derived from the assessment of feedforward inference through gradient backpropagation. ETC-PS

[5] is a classification method for analyzing encrypted network
traffic using path signature features. It constructs traffic paths
based on session packet lengths, converts these into salient
structural features, and employs multi-scale path signatures
alongside random forests for both closed and open-set traffic
classification. However, in the open-set context, ETC-PS is
limited to two coarse classifications: known and unknown.
However, all the open-set network traffic classification methods mentioned above rely on regular classification networks
with softmax functions to compute classification probabilities.
In the open-set scenarios, the use of softmax to calculate
classification probabilities is not reliable.
C. Discussion on Conformal Prediction
Uncertainty is defined as the measure of the reliability
of classification results, unlike traditional models that only
output the classification probability of a sample. Our proposed
method, RoNeTC, outputs the model’s classification decision
through a Dirichlet distribution, which includes the predicted
value of the sample and the uncertainty. Visualize how confident the model is in the decisions it outputs by quantifying
uncertainty.
Conformal Prediction is a framework designed to provide
reliable and quantitative uncertainty estimates for ML and
DL prediction results. Based on statistical theory, it expresses
prediction uncertainty by generating a confidence interval or
a confidence set instead of a single point prediction.
We demonstrate the advantages of using the Dirichlet distribution in open-set network traffic classification from the
following points.
Sample-Level Distribution Information: The Dirichlet distribution can provide sample-level probabilistic distribution
information for open-set network traffic classification, enabling
finer-grained decision-making. In contrast, Conformal Prediction only offers confidence intervals, which are insufficient for
detailed analysis in complex scenarios.
Dynamic Adaptability: Encrypted traffic often contains both
plaintext and encrypted packets. By leveraging a multi-view
approach to process network traffic and incorporating the
Dirichlet distribution, it is possible to dynamically integrate
information from different views, thereby better adapting to
complex network traffic environments.

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

2316

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

Fig. 3. Overview of RoNeTC, including training phase and classification phase.

Handling Unknown Samples: In open-set network traffic
classification, where the quantity and distribution of unknown
classes are unpredictable, the Dirichlet distribution does not
rely on historical data calibration. It can efficiently adapt
to changes in data distribution in real-time. In contrast,
Conformal Prediction requires offline calibration, lacking the
flexibility and dynamism needed for such scenarios.
III. T RAINING P HASE OF RO N E TC
Our proposed RoNeTC framework, designed for reliable
network traffic classification in open-set settings, is depicted in
Fig. 3. It comprises four modules: Flow Preprocessing, GlobalLocal Feature Extractor, Opinion Generator, and Opinion
Fusion. In the training phase, since no samples of unknown
class are involved, we can only rely on the prior knowledge of
the known class. To obtain more reliable classification results
for open-set network traffic, we design the Flow Preprocessing
module to divide each packet of a bi-directional flow into
three distinct views according to the TCP/IP protocol stack.
Subsequently, we apply the deep learning-based feature extractor to each view, performing inter-packet and intra-packet
feature refinement to achieve global-local feature extraction.
Each view then outputs a classification opinion, namely, a
classification decision accompanied by a measure of decision
reliability termed the opinion uncertainty, generated through
an opinion generator that utilizes second-order classification
probabilities. Finally, the ultimate classification decision and
its associated uncertainty are determined by dynamically integrating all classification opinions through the opinion fusion
module, using the uncertainty of each viewpoint as a weighting
factor.
A. Flow Preprocessing
The main objective of this subsection is to transform raw
network traffic into a tensor for use in subsequent feature
extractor. To construct this input tensor, we combine multiple

Fig. 4. A flow is divided into three parts, each represented as a separate view:
IP Header, Transport Layer Header, and Packet Payload, and then encoded
into a two-dimensional tensor.

views to comprehensively capture the features of known class
flows. We intercept the first l packets of a bi-directional
flow, where each packet shares the same 5-tuple (i.e., the
same source IP address, source port, destination IP address,
destination port, and the Layer 4 protocol). To more finely
utilize packet characteristics, we divide each packet of a flow
into three views according to the TCP/IP protocol stack,
as shown in Fig. 4. In this module, the network layer is
represented by the ‘IP Header View’, the transport layer
by the ‘Transport Layer Header View’, and the application
layer by the ‘Packet Payload View’. Each packet of a flow
is divided into three sets of data to form three views, and
the one-dimensional bytes of each view are converted into
two-dimensional tensor through the embedding layer. A flow
sample is processed by the flow processing module to generate
two-dimensional tensors, representing three views of multiple
packets within a single flow. To prepare for the subsequent
deep learning-based feature extractor, each view is trained in

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

WANG et al.: RELIABLE OPEN-SET NETWORK TRAFFIC CLASSIFICATION

2317

Fig. 5. (a) The Global-Local Feature Extractor. (b) The schematic of global feature representation. Each color represents a packet. Medium-sized solid grid
lines indicate patches, assumed to be p × p in size (divided by dashed lines). The Transformer operates at the corresponding positions between the patches
(shown by the red curves with arrows).

parallel within the feature extractor. This design facilitates the
generation of classification decisions and their corresponding
reliability metrics for each view.
B. Global-Local Feature Extractor
The Global-Local Feature Extractor is designed to extract
local features within individual packets and global features
across multiple packets. This extractor, which combines CNN
and Transformer techniques, is illustrated in Fig. 5(a). In
contrast to the weak correlation observed within single packets
of a flow sequence, the inter-packet correlation proves to
be strong and significant [17]. This characteristic sets our
approach apart from prior methods [8], [16], which only
account for local information from a single packet. It allows us
to fully extract flow characteristics from both intra- and interpacket aspects. Therefore, we designed a global-local feature
extraction module to provide sufficient evidence for the subsequent modeling of second-order classification probabilities
and for estimating uncertainty in classification decisions.
The Global-Local Feature Extractor is comprised of three
parts: the local feature representation, the global feature
representation, and the feature fusion. Specifically, for an input
tensor X ∈ RH×W×C , where H, W, and C are the height, width,
and number of channels of the input embedding of the single
view, respectively.
Local Feature Representation: This part is employed to
encode the local feature information of a single packet in
the flow sequence. It uses a standard convolutional layer with
a 3 × 3 receptive field, followed by a point-wise (or 1 × 1)
convolution layer that projects the tensor to a high-dimensional
space (D-dimensional space, where D > C) by learning linear
combinations of the input channels to generate XL ∈ RH×W×D .
Global Feature Representation: This part combines all the
packets of a flow to generate a global feature representation.
First, we unfold XL into N non-overlapping small blocks,
known as patches p ∈ {1, 2, · · · , P}. Patches at the same position across different packets represent the same field within
those packets. Extracting features from patches at the same
position enables capturing the state transition information of
the same field across packets, resulting in XU ∈ RP×N×D . Here
P = w × h is the patch size, w ≤ n and h ≤ n are the height
and width of the patch, respectively, N = HW
P is the number of
patches, and the number of channels D is unchanged. Next, we

use the Transformer [24], [25] to compute global dependencies at corresponding positions between patches, generating
XT ∈ RP×N×D . We then fold XT back into its original tensor
arrangement to obtain XF ∈ RH×W×D .
XT (p) = Transformer(XU (p)), 1 < p < P

(1)

In the experimental setup, we use the initial first l packets
of each flow. To capture the global feature representation of
the entire flow, we design a specific method: every r packets
are arranged in a non-overlapping, cross-shaped configuration
and combined into a tensor that serves as a channel. As an
example, as illustrated in Fig. 5(b), suppose we process the
initial first 12 packets of a bi-directional flow and splice every
four packets together to form a tensor that serves as a channel.
This approach results in a total of three channels. Finally, a
p× p patch is delineated on each channel (with p commonly set
to 2 in the experiments), and Transformer operation is used to
perform global feature extraction at the corresponding position
of each patch.
Feature Fusion: In this process, XF is projected into a
low C-dimensional space using a point-wise convolution and
then combined with X via a concatenation operation. These
concatenated features are subsequently fused by another CNN
layer, producing X0 ∈ RH×W×C .
C. Single View Opinion Generator
In order to quantify the degree of reliability of the classification results output by the classifier, we express the reliability
of these results in a convenient and intuitive probabilistic
manner. We design the opinion generator specifically to add a
reliability metric to the classification results of the classifier.
In this context, the opinion refers to the outcome produced by
the opinion generator, which includes both the classification
decision and uncertainty value that indicates the reliability of
that decision. In this module, we use uncertainty estimation to
measure the reliability of the classification decision for each
view. This is achieved by modeling second-order classification
probabilities, which form a distribution of classification probability distributions with uncertainty. Since the softmax function
inflates the probability values, it can easily output high probability values for the unknown classes in open-set scenarios
[12], [13], leading to the misclassification of unknown classes
as known ones. To avoid the above problem, we replace

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

2318

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

the softmax function with a softplus layer and introduce the
Dirichlet distribution to uncertainty estimation, which helps in
constructing the distribution of the classification probability
distribution [26], [27].
More specifically, for the v-th view, assume there are K
classes. The value derived from the softplus layer serves
as a measure of support for classifying the sample into a
specific class k (i.e., Evidence ev = [1, · · · , evk , · · · , evK ]), where
evk ≥ 0 represents the value of evidence learned by the model
to classify this sample into the k-th class. Parameterizing

the Dirichlet distribution αv = 1, · · · , αvk , · · · , αvK (where
αvk = evk + 1) with evidence, the Dirichlet distribution is given
by:
8
K
Y
ˆ
< 1
pαk −1 for p ∈ SK
(2)
D(p | α) = B(α) k=1 k
ˆ
:
0
otherwise
The Dirichlet distribution is a probability density function for possible values of the probability mass function (PMF) p. Here, B(α) is the K-dimensional beta
and SK is the Dirichlet strength,
and SK =
nfunction,
o
PK
p | k=1
pk = 1 and 0 ≤ p1 , . . . , pK ≤ 1 .
We use the Dirichlet distribution to quantify the probability
density of classification, treating each classification decision
from different views as distinct opinions. This method assigns
a belief score b to each class and introduces uncertainty u to
the classification decision.
K
X
uv +
bvk = 1
(3)
k=1

where uv ≥ 0 and bvk ≥ 0 (k = 1, . . . , K) represent decision
result uncertainty and the belief score (i.e. probability) of class
k-th, respectively. The calculation of these values is expressed
as follows:
ev
K
bvk = kv , uv = v
S
S
K
K
X
X
Sv =
evi + 1 =
avi
(4)
i=1

i=1

v

where S is the Dirichlet intensity at the v-th view.
When the classifier detects increased evidence for the kth class in a sample, both the probability and belief score
for that class increase, thereby reducing the uncertainty of
its classification decision. Conversely, when evidence is scant,
the belief score approaches zero, which increases the overall
uncertainty of the classification decision, tending it toward
one on the scale. Ideally, for samples from known classes,
the uncertainty of their decisions is close to zero due to
prior knowledge, while for samples from unknown classes,
the uncertainty is significantly higher than zero due to having
never been seen. For class k in the current view v, the expected
probability p̂vk of an opinion is equal to the projection of the
αv
Dirichlet distribution onto the base, i.e., p̂vk = S kv [28].
D. Multi-View Opinion Fusion
Since the reliability of classification decisions varies across
different views and samples, we need to assess the reliability of

Fig. 6. Fuse the classification opinions of the two views and use the three
vertices of the triangle to represent the three classes. Within the triangle, red
indicates high probability density, while blue signifies low probability density.

decisions for each view in each sample adaptively. Therefore,
it is necessary to dynamically fuse the classification decisions
from all views based on the uncertainty in the opinions. In
subsection III-A, we partition a flow into three views (i.e.,
IP Header, Transport Layer
n˚ Header,
o and Packet Payload) to
v K
v
v
learn the opinions M = bk k=1 , u for each view separately,
each consisting of the classification decision and its associated
uncertainty, which serves as an indicator of the decision’s
reliability. In order to fuse the three views with classification
decision
to form a reliable final joint opinion
˚ uncertainty
K
M = {bk }k=1
, u , we introduce the Dempster-Shafer evidence
theory [26], [29], [30] to fuse the classification opinions from
different sources.
As illustrated in Fig. 6, the figure presentsn an exampleo
˚ 1 K
bk k=1 , u1
of fusing opinions from two views, M1 =
n˚
o
K
and M2 = b2k k=1 , u2 . Each view gathers evidence e and
parameterizes the Dirichlet distribution to obtain the view with
uncertainty u and belief score b of classification decision.
Ultimately, the final joint opinion M is then derived using
the fusion criterion.
M = M1 ⊕ M2

(5)

The specific belief score and uncertainty are given by:

1
1
b1k b2k + b1k u2 + b2k u1 , u =
u1 u2 (6)
bk =
1−C
1−C
P
C = i, j b1i b2j represents a measure of the degree of conflict
1
between two probability score sets. 1−C
is the normalization
factor.
The joint opinion M from the three views is also derived
based on the aforementioned fusion criterion. The subsequent
evidence and Dirichlet distribution parameters are induced as:
K
S = , ek = bk × S , ak = ek + 1
(7)
u
To more concretely illustrate the fusion of opinions from
multiple views, we present the example of two views in
open-set scenarios. When there is a lack of evidence favoring
classification in both views, this leads to low joint belief scores
and final prediction probabilities, and increased joint uncertainty in the classification opinions. In contrast, if both views
receive sufficient evidence, the outcome is high joint belief
scores and reliable, high-scoring final prediction probabilities,
alongside reduced joint uncertainty. When a significant disparity exists in the amount of classification evidence between the

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

WANG et al.: RELIABLE OPEN-SET NETWORK TRAFFIC CLASSIFICATION

2319

two views, we give preference to the view with the stronger
evidence. Thus, the joint uncertainty for unknown samples,
which the classifier has never encountered, is significantly
higher than for known classes. Based on the aforementioned
analysis, the joint uncertainty between known and unknown
samples varies greatly—specifically, the classification decision
uncertainty for known samples is considerably lower than for
unknown samples. Consequently, we apply this principle to
classify known and unknown classes in the open-set scenario.
E. Joint Loss
In this subsection, we construct our loss function. The
common cross-entropy loss function is:
Lce = −

K
X


yi j log pi j ,

(8)

j=1

where pi j is the prediction probability that the i-th sample is
predicted to be class j. Since we use the Dirichlet distribution
to simulate the distribution of the classification probability
distribution, and we denote the loss function after amending
Eq. 8 as:
2
3
Z X
K
K

1 Y αi j −1
4
5
pi j dpi
Lace (αi ) =
−yi j log pi j
B (αi )
j=1

j=1

=

K
X

yi j ψ (S i ) − ψ αi j



(9)

IV. C LASSIFICATION P HASE OF RO N E TC
The aim of the classification phase is to identify unknown
classes and accurately classify known classes into their respective corresponding label sets. After the training phase is
complete, the feature extractors for the three views and the
opinion fusion module, which includes the joint classification
decision and its associated uncertainty, are utilized. This uncertainty refers to the reliability of the decision. Subsequently,
the knowledge gained from the aforementioned processes is
used in the open-set classification phase. In this phase, the
threshold is determined using joint uncertainty to distinguish
between known and unknown classes. Uncertainty hinges
on the characteristic that flows with higher belief scores in
classification and more reliable classification outcomes have
correspondingly lower uncertainty, thus being classified into
the known class. Conversely, flows with lower belief scores
and unreliable classification results exhibit correspondingly
higher uncertainty, hence being classified into the unknown
class.
To facilitate the identification of the optimal threshold,
we draw inspiration from Youden’s index [31]. We define a
function η(σ) = 2 ∗ T PRs(σ) − FPRs(σ) based on the true
positive rates (TPRs) and false positive rates (FPRs) of the
samples. The optimal uncertainty threshold is then determined
by identifying the threshold σ̂ that maximizes the function,
i.e., σ̂ = argmaxσ η(σ), and considering the range around this
threshold.

j=1

where ψ(·) is the digamma function and Lace represents the
integral of the cross-entropy on the Dirichlet distribution.
To differentiate the classification evidence generated by data
samples according to their contributions to the classification,
more evidence is produced for the correct labels of the known
classes, while less evidence is generated for the open-set
unknown classes. We penalize unknown classes by using KL
divergence to produce less evidence of classification, The KL
divergence term is denoted as:


KL D (pi | α̃i ) kD (pi | 1)

 1
0
PK
Γ
α̃
k=1 ik
A
= log @
QK
Γ(K) k=1 Γ (α̃ik )
13
2
0
K
K
X
X
(α̃ik − 1) 4ψ (α̃ik ) − ψ @
α̃i j A5
(10)
+
j=1

k=1

where Γ(·) is the gamma function and ãi = yi + (1 − yi ) ai is
the adjustment parameter of the Dirichlet distribution that is
set to prevent the evidence of true label from being penalized
to zero. Consequently, the loss function of a single view flow
feature is then:


L (αi ) = Lace (αi ) + λt KL D (pi | α̃i ) kD (pi | 1)
(11)
where λt > 0 is the balance factor. Combining the classification
opinions of flow characteristics from three views, the final joint
classification loss function is:
"
#
N
3
X
X

v
Lall =
L (αi ) +
L αi
(12)
i=1

v=1

V. E XPERIMENTAL E VALUATION
In this section, we detail the experimental setup, parameter
selection and ablation study of RoNeTC.
A. Experimental Settings
1) Dataset: We use three publicly available datasets for
comprehensive evaluation in both closed-set and open-set
settings. Detailed information on each dataset is provided in
Table II.
Dataset-I: The UNSW traffic dataset was sourced from
different web-based devices and collected and stored in a smart
device environment built on campus by Sivanathan et al. [32].
The data collection period spanned from October 1, 2016, to
April 13, 2017, covering approximately 26 weeks, and was
organized into different pcaps by date. The selection criteria
for the classes specified exactly 1,000 samples per class.
Dataset-II: The CIC dataset (2022) [33] is utilized for the
behavioral analysis and vulnerability testing of various IoT
devices that operate on protocols such as IEEE 802.11, Zigbee,
and Z-Wave. We select 500 samples for each class.
Dataset-III: The Mapps dataset [34], derived from the
‘MApps’ public mobile application traffic dataset, was collected by Pham et al. in 2021. The authors recruited ten student
volunteers to collect traffic consistently over six months using
eight different smartphones. We chose flow numbers ranging
from 500 to 1,000 per class.
To rigorously and comprehensively evaluate the reliability
and robustness of RoNeTC in open-set settings, we elaborately established six unknown scenarios reflecting open-set

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

2320

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

TABLE II
B RIEF D ESCRIPTION OF THE DATASET

TABLE III
O PEN -S ET S CENARIOS D IVISION

conditions based on three datasets, as detailed in Table III.
For clarity, we take Scenarios-A as an example. We use the
entire set of Dataset-I as known samples, partitioning them
into training, validation, and test sets that represent 60%, 20%,
and 20% of the number of each class, respectively. In the
context of open-set testing, all samples from Dataset-II in
Scenario-A are treated as unknown classes and included in
the test sets.
2) Metrics: We define the metrics employed to evaluate
RoNeTC, specifically Recall, Precision, and F-macro, which
will hereafter be referred to as Rec, Pre, and F1, respectively.
The source code is available at: https://github.com/xuemanxm/RoNetTC/tree/main.
B. Parameter Selection
In order to achieve better classification performance, we
optimize the experimental setup through parameter selection experiments. We capture the initial first l packets of
each bi-directional flow, where l ∈ {4, 8, 12, 16}, and intercept the initial first b bytes of each packet, where b ∈
{64, 128, 256}. According to Section III-A, we partition the
packet into three components based on the TCP/IP protocol

stack: the IP Header, the Transport layer Header, and the
Packet Payload—collectively referred to as the three views.
In this way, we can perform a multi-view adaptive fusion
of classification opinions, based on the classification decision
and its uncertainty for each view of each flow, with the
uncertainty indicating the reliability of that decision. This
process results in the final classification decision and its associated uncertainty, which are then applied to the classification
tasks in open-set scenarios. We select appropriate parameters
for open-set scenarios in six open-set settings (Scenario-A
to Scenario-F), with the experimental results displayed in
Table IV. Its experimental results in the conventional closedset environment are shown in Table V.
1) Open-Set Network Traffic Classification: In the following, we evaluate the effects of the parameter experiments
for each of the six open-set scenarios, and the results are
shown in Table IV. As the number of bytes b and the number
of packets l increase, the F1 also increases. However, in
Scenario-A, Scenario-C, and Scenario-F, where b is 128 and
256, the increase in the size of the input tensor leads to
the model capturing more useless features along with useful
ones. Furthermore, as the number of packets l increases, the
dimension of the input tensor also increases, leading to a rise
in the volume of the input space. This results in sparser data
and higher computational complexity. Therefore, in all these
scenarios, as the values of b and l increase, the F1 initially
increase and then decrease.
In Scenario-A, we design Dataset-I as the known class
sample set and Dataset-II as the unknown class sample set.
We select 128 bytes (b = 128) and 8 packets (l = 8) as the
optimal parameters for the current scenario. As demonstrated
in Table IV, this configuration results in the highest openset classification F1 of 96.44% among various combinations
of byte and packet counts. Specifically, this parameter set
achieves a Rec of 95.92% and a Pre of 97.22%. ScenarioB, in alignment with the known class samples of Scenario-A,
employs Dataset-I, whereas the unknown class samples are
derived from Dataset-III. For this configuration, we choose
256 bytes (b = 256) and 16 packets (l = 16) as the optimal
parameters. With these settings, the classification F1 reaches
a maximum value of 98.16%, and its corresponding Rec =
98.11% and Pre = 98.32% are also close to the maximum
value. Although Scenario-B and Scenario-A share the same
known classes, the open-set classification performance of
Scenario-B surpasses that of Scenario-A. This improvement
is attributed to the greater disparity between the known and
unknown class samples in Scenario-B, making them easier to
distinguish.
The known class samples for both Scenarios-C and
Scenarios-D are sourced from Dataset-II. In Scenario-C, the
unknown class samples are taken from Dataset-I and are
entirely categorized as the test set. For this scenario, we select
256 bytes (b = 256) and 4 packets (l = 4) as the optimal
parameters. Under these conditions, the open-set classification
achieves a maximum F1 of 94.56%. Scenario-D is based on
Dataset-III as the unknown class, and b = 256, l = 16 is
selected as the best parameter for this scenario, based on
the criterion of maximum classification F1, which is 94.03%,

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

WANG et al.: RELIABLE OPEN-SET NETWORK TRAFFIC CLASSIFICATION

2321

TABLE IV
E XPERIMENTAL R ESULTS OF O PEN -S ET PARAMETER S ELECTION

TABLE V
E XPERIMENTAL R ESULTS OF C LOSED -S ET PARAMETER S ELECTION

corresponding to Rec of 91.68%, Pre of 97.27%. ScenariosC and D share the same known classes; however, Scenario-C
has approximately one-third the number of unknown samples
compared to Scenario-D. Consequently, the F1 for Scenario-C
is slightly higher than that of Scenario-D, despite the identical
known classes.
Scenarios-E and F use Dataset-III as a known sample set. In
Scenario-E, Dataset-II is the unknown sample set, achieving
the highest classification F1 of 91.71%, which corresponds
to optimal parameters b = 256 and l = 16. However, in
Scenario-F, Dataset-I serves as the unknown class. Using
an F1 of 93.26% as the benchmark, the optimal parameters
selected are b = 256 and l = 4. Given that Scenarios-E and F
have a significantly larger number of known classes compared
to other scenarios, they exhibit the lowest classification F1.
However, the larger quantity of unknown class samples in
Scenario-E than in Scenario-F introduces additional classification interference, resulting in the lowest effect among the six
open-set classifications observed in Scenario-E. In contrast,
Scenario-B, with its smaller number of known classes and
greater disparity between known and unknown class samples,
achieves the highest classification F1 of 98.16% in the openset classification.
Uncertainty Analysis: As depicted in Fig. 7, we present a
plot illustrating the uncertainty distribution for both known
and unknown samples within the open-set context. In subsection III-D and section IV, we delve into the optimal

Fig. 7. Uncertainty distribution KDE figures for Known and Unknown Classes
in six open-set scenarios.

characteristics for both known and unknown classes. Ideally,
known classes should exhibit high belief scores and low
uncertainty, while the optimal scenario for unknown classes is
characterized by low belief scores and high uncertainty. The
uncertainty values of all known samples in the graph are tightly
clustered around the scale 0. However, in Fig. 7(c)(f), there
is a slightly looser distribution of known classes due to the
large number of known classes and the best effect of known
class classification is only 94.88%. Nevertheless, these values
remain tightly concentrated on the left side of the x-axis. In
contrast, the uncertainty values of the unknown class samples
should be far from the 0 point of the scale due to their lower
belief scores. This is indeed the case for the unknown classes

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

2322

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

TABLE VI
R ESULTS OF V IEWS A BLATION E XPERIMENTS

TABLE VII
R ESULTS OF C HANNEL A BLATION E XPERIMENTS

in the subfigure, all of which are essentially distant from the
0 scale. This presents a stark contrast with the known classes,
which are densely clustered around the 0 scale. Especially in
Fig. 7(c)(f), the uncertainty values of certain unknown classes
cluster around scale 1, providing a clear distinction from the
known classes.
2) Closed-Set Network Traffic Classification: Similarly, we
conduct a parametric analysis in the conventional closed-set
environment, defined as the closed-set environment containing
only known classes. The experimental results for the three
closed-set scenarios are presented in Table V. On Dataset-I,
all combinations of the number of bytes and packets achieve
excellent classification results, with F1, Rec, and Pre all
above 99%. The optimal results are observed in closed-set
network traffic classification using parameter settings of 128
bytes (b = 128) and 8 packets (l = 8), where all three
metrics reach 99.96%. On Dataset-II, the effectiveness of
traffic classification gradually improves as the number of bytes
increases. The optimal performance is achieved with a byte
count of 256 (b = 256) and a packet length of 4 (l = 4),
recording 99.11% for both F1 and Rec, and 99.13% for Pre.
As the number of classes increases and classification complexity rises, there is a noticeable decrease in the overall
network traffic classification results. On Dataset-III, which
has the highest number of classes, the classification results
are slightly weaker compared to the previous two closed-set
datasets. However, with parameters set at b = 256 and l = 12,
it still achieves an F1 of 94.88%, a Rec of 94.39%, and a Pre
of 96.04%.

conduct extensive ablation studies on these two features. We
assess the experimental outcomes using the F1, and the results
are presented in Tables VI and Tables VII.
1) Multi-View Ablation Studies: We analyze the ablation
effects on the IP Header, Transport Layer Header, and Packet
Payload by considering single-view and dual-view permutations, denoted as RoNeTC-S and RoNeTC-D, respectively. The
results are presented in Table VI. Notably, among the three
broad classes—RoNeTC-S, RoNeTC-D, and RoNeTC—our
proposed three-view scheme, RoNeTC, consistently achieves
the highest F1 in all open-set scenarios, demonstrating superior
performance. On the contrary, the single-view RoNeTC-S
exhibits the largest decline and the poorest performance in
open-set classification. Although it splices three parts into
a single view using the same amount of information as
RoNeTC, the performance still suffers from varying degrees
of degradation. The results clearly demonstrate that employing
multiple views to finely handle uncertainty estimation for each
view and enhance their reliability proves more effective for
open-set classification.
2) Packet Splicing Methods for Global Feature Representation: In this part, each packet in the flow is treated as
an individual tensor to form a channel, which we refer to
as RoNeTC-O. The results are presented in Table VII. As
described in subsection III-B, the global feature representation
illustrated in Fig. 5(b) employs a splice approach that arranges
every p packets of a flow in a non-overlapping, cross-shaped
arrangement into a tensor and treats it as a channel.
Our experiments show that RoNeTC achieves the best
performance in all six scenarios. More specifically, the F1
of RoNeTC-O decline in all open-set scenarios relative to
RoNeTC, indicating poorer performance in open-set classification. Most notably, the F1 in Scenario-F decreases
significantly, highlighting that RoNeTC-O struggles in complex situations with numerous known classes and ambiguous
identification of unknown classes. Our findings affirm that
RoNeTC, based on the principle that the correlation between
packets is greater than within packets, delivers superior
performance and greater robustness in challenging open-set
environments.

C. Ablation Study
To evaluate the effectiveness of the RoNeTC dynamic multiview uncertainty assessment and the global packet splicing
approach within the global-local Transformer module, we

VI. E XPERIMENTAL C OMPARISON W ITH SOTA M ETHODS
In this section, in order to fully evaluate the reliability
and robustness of our proposed method, RoNeTC, we

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

WANG et al.: RELIABLE OPEN-SET NETWORK TRAFFIC CLASSIFICATION

2323

TABLE VIII

TABLE IX

C OMPARISON W ITH T HE SOTA M ETHODS IN THE
C LOSED -S ET S CENARIOS

C OMPARISON W ITH T HE SOTA M ETHODS IN THE O PEN -S ET S CENARIOS

conduct experimental comparisons with state-of-the-art
(SOTA) open-set network traffic classification methods in
two major scenarios: open-set and closed-set scenarios. The
SOTA methods for network traffic classification in open-set
scenarios are as follows:
• ETC-PS [5]: ETC-PS constructs traffic paths using
sequences of packet lengths, applies path transformations
to extract information, and finally computes multi-scale
path signatures to handle both open-set and closed-set
network traffic methods.
• AutoUA [4]: AutoUA is an autonomous learning framework for open-set network traffic classification. It uses
the first l packets of each flow as input to build a
CNN network to identify network traffic. In the original paper, AutoUA plots the Cumulative Distribution
Function (CDF) based on probability values, using the
probability values on the CDF corresponding to the 1 − 
( represents Accuracy) of known classes as thresholds to
distinguish between known and unknown classes.
• GradBP (max): GradBP [1] is a method for evaluating
feed-forward inference using deep learning gradient backpropagation. It selects the gradient of the input layer
from the first step of backpropagation as a threshold
to classify flows into known and unknown classes. In
addition, GradBP is designed with two gradient thresholding methods. The first one is GradBP (max), where the
gradient threshold is computed as the maximum value of
the gradient.
• GradBP (square root): The second gradient threshold
method of GradBP is GradBP (square root). This method
is the same as GradBP (max), except that its gradient
threshold is computed as the square root of the sum of
the squares of the gradient.
A. Comparison on Closed-Set Network Traffic Classification
Methods
We begin by comparing the performance of all methods on
regular closed-set network traffic classification to observe the
experimental results, displayed in Table VIII. We conduct an
experimental comparison between RoNeTC and other SOTA
open-set network traffic classification methods across three
closed-set datasets. On all datasets, our method RoNeTC
achieves the highest values on all metrics, demonstrating

superior closed-set classification performance. On Dataset-I,
RoNeTC attains an optimal 99.96% across all three metrics.
However, as the number of classes increases, the classification effectiveness of all methods decreases. For instance,
in Dataset-III, which has the highest number of classes, all
methods encounter the worst classification performance ability,
such as AutoUA obtaining an F1 of 87.77%. Nevertheless,
RoNeTC maintains strong recognition capabilities, reaching an
optimal value of 94.88%. The confusion matrix of RoNeTC
is presented in the Appendix. Overall, our RoNeTC method
consistently achieves excellent results in network traffic classification on closed-set scenarios.
B. Comparison on Open-Set Network Traffic Classification
Methods
For the experimental comparison of network traffic classification for closed-set scenarios, the RoNeTC method achieves
excellent classification results. Next, we will move to more
complex open-set scenarios for further comparison. Our experimental comparison results with four state-of-the-art open-set
network traffic classification methods across six open-set scenarios are shown in Table IX.
Our proposed method, RoNeTC, consistently achieves the
highest values across all metrics, demonstrating superior performance in open-set classification compared to the other
methods. Particularly in Scenario-B, RoNeTC excels with an
impressive F1 of 98.16%, which reflects excellent classification of known classes and robust recognition of both known
and unknown classes in the open-set scenarios. RoNeTC
also demonstrates excellent classification performance in the
relatively complex Scenario-E and Scenario-F, achieving F1
of 91.71% and 93.26%, respectively. Combining the results
of previous closed-set comparison experiments, our RoNeTC

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

2324

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

method achieves excellent classification results on both closedset and open-set scenarios.
ETC-PS [5] processes open-set network traffic by performing binary classification to distinguish between known
and unknown classes. To adapt this approach for identifying
unknown classes and further classifying known classes, we
plot the Cumulative Distribution Function (CDF) of the output
probability values of ETC-PS. We select the point corresponding to the last flat region of the CDF, where the probability
value stops increasing, as a threshold to distinguish the known
from the unknown class. In Table IX, the F1 of ETC-PS
in each open-set scenarios is second only to our method,
RoNeTC. It performs best in Scenario-A, achieving an F1 of
93.03%, which is 3.41% lower than that of RoNeTC. The
classification performance of ETC-PS decreases significantly
as the number of known classes increases, with the worst
results in Scenario-E, which has the largest number of known
and unknown classes. In this scenario, ETC-PS achieves an
F1 of only 70.79%, which is 20.92% lower compare to our
RoNeTC.
AutoUA [4] is utilized in open-set network traffic comparison experiments, with parameter settings that are consistent
with the optimal parameters for each scenario, as derived
from Table IV. The results of these experiments are shown
in Table IX. Among all open-set scenarios, AutoUA achieved
its best performance in Scenario-F, recording the highest F1
of 65.85%, with a Rec of 87.11% and a Pre of 59.80%.
This indicates superior recognition of known classes over
unknown ones. Conversely, AutoUA was least effective in
Scenario-D, where it recorded an F1 of 36.11%, marking
a significant decrease of 57.92% compared to our method
RoNeTC. Overall, in open-set scenarios, AutoUA’s recall
consistently exceeds its precision. This indicates that while
AutoUA is able to identify most flows of the known classes
(high recall), it also incorrectly classifies many unknown class
flows as known class flows (low precision). This suggests
that AutoUA’s ability to recognize unknown classes needs
improvement.
GradBP [1] uses the sequence of packet lengths for the
first 100 packets from the original bi-directional flow as input
for all training data in open-set scenarios, as specified in the
original paper. The threshold calculation is divided into two
methods: GradBP (max) and GradBP (square root).
GradBP (max) achieves the best performance in Scenario-A
among all the open-set scenarios, with 85.19% for F1, 92.08%
for Rec, and 79.20% for Pre. This is the highest in both F1 and
Rec among all scenarios. However, compared to our proposed
method, RoNeTC, the F1 of GradBP (max) is still lower
by 11.25%. The weakest performance occurs in Scenario-B,
where the F1 is only 66.15% and the Rec significantly exceeds
the Pre. Overall, GradBP (max) does not perform as well with
unknown classes in open-set scenarios as it does with known
classes.
GradBP (square root) reaches peak performance in
Scenario-E, with an F1 of 80.31%, a Rec of 63.28%, and
a Pre of 94.10%. It degrades to its worst performance in
open-set classification in Scenario-D, with an F1 of 52.83%,
which is 41.20% lower than our method, RoNeTC. Overall,

Fig. 8. Comparison of ROC curves and AUC values for the known and
unknown classes in six open-set scenarios with the SOTA methods.

GradBP (max) consistently outperforms GradBP (square root)
in open-set classification. Notably, GradBP (max) demonstrates consistently higher Rec than Pre across all scenarios,
underscoring its strong ability to identify known classes.
Conversely, GradBP (square root) exhibits greater Pre than
Rec, indicating a more effective identification of unknown
classes.
To clearly illustrate the open-set classification capability,
we plot the ROC curves for both known and unknown classes
and calculate the AUC values, as shown in Fig. 8. RoNeTC
consistently achieves the highest AUC values across various scenarios, performing best in Scenario-B with an AUC
value of 99.66%. Its ROC curve is closest to the upper left
corner, indicating a low false positive rate and a very high
true positive rate. This demonstrates that the classifier can
accurately classify known classes while rarely misclassifying
unknown classes as known class flows, correctly identifying
almost all unknown samples in this scenario. In contrast, all
other methods lie below the RoNeTC curve as the false positive rate changes, particularly AutoUA and GradBP (square
root), which show a lower true positive rate at the same
false positive rate. This indicates that their classification
performance for known and unknown classes is inferior to
RoNeTC.

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

WANG et al.: RELIABLE OPEN-SET NETWORK TRAFFIC CLASSIFICATION

2325

Fig. 10. Heat map of field importance for TLS flow that does not include
the Handshake process.

Fig. 9. Comparison of F1 before and after adding a large number of unknown
classes in six open-set scenarios with the SOTA methods. The colored sections
with stripes indicate the magnitude of the decrease in F1 after addition.
TABLE X
O PEN -S ET S CENARIOS C HANGES FOR ROBUSTNESS A NALYSES
Fig. 11. Heat map of the field importance of TLS flow that contains the
Handshake process.

C. Robustness Analysis
In our open-set Scenario-A and B, C and D, and E and
F, each pair shares the same known training dataset, with
the only difference being the unknown class set. We aim to
assess the robustness performance of each open-set classification method by adding additional unknown sample classes
while maintaining the original known samples, parameters, and
thresholds unchanged. The experimental setup is detailed in
Table X. Initially, each scenario involves one dataset for known
classes and another for unknown samples. We expanded this
setup by adding an additional dataset as unknown samples set
without adjusting any parameters, including thresholds. The
results depicted in Fig. 9 reveal noteworthy fluctuations in
the F1 across the majority of open-set classification methods.
For instance, AutoUA exhibits a substantial decrease in F1
across all scenarios upon the inclusion of unknown classes.
Meanwhile, ETC-PS, recognized as one of the premier classification comparison methods overall, experiences a significant
decline specifically in Scenario-MixA and MixC. In contrast,
our proposed method, RoNeTC, demonstrates only minor
fluctuations. Although there is a slight 3% downturn in F1
in Scenario-MixB and MixF, it still achieves the highest F1
overall. This outcome highlights RoNeTC’s superior classification performance and excellent robustness when the number
of unknown classes is significantly increased.
D. Interpretability of Our Proposed Method
To explore what features the model has learned from
network traffic, in this subsection, we use an open-source
tool, “Lime” [35], which can explain the predictions of any
classifier, to help us understand the prediction results of
RoNetc. The results on Dataset-I are shown in Fig. 10 and

Fig. 11, highlighting the heat maps of the three views of
encrypted flows. Fig. 10 represents a TLS flow without the
handshake process, while Fig. 11 represents a TLS flow with
the handshake process. In both figures, it can be observed that
in the IP header and Transport layer header views, certain
fields within a single packet, as well as their corresponding
positions across packets, are critical for classification, such
as the “Total Length” and “Time to Live” in the IP header
view at their important positions, and the “Window Size” in
the Transport layer header view. Since these positions are fixed
across packets, we can effectively model the global features of
the flow by capturing the state transition relationships between
different packets. In contrast, the payload view shows that, due
to encryption, the importance of these fields for classification
is significantly reduced. This is particularly evident in Fig. 10,
which does not include the handshake process. However, for
Fig. 11, as it includes the handshake process, the first packet is
in plaintext, allowing extraction of information that contributes
significantly to classification.
E. Discussions
Currently, network traffic classification in open-set scenarios
relies on a fixed number of intercepted packets and bytes for
feature extraction. To handle flows that do not meet this fixed
number, padding with zeros is typically applied. However,
in real-world scenarios, the number of packets and bytes in
network traffic fluctuates. This fixed-length feature extraction
method lacks flexibility and often leads to wasted storage and
computational resources.
Especially for real-time classification, easily identifiable
classes might be accurately classified with only the first few
packets and a small number of bytes. However, to maintain
uniform input for the model, it is often necessary to wait for
the capture of additional packets. This significantly increases
processing time and reduces classification efficiency. There-

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

2326

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

TABLE XI
C OMPUTATIONAL C OMPLEXITY OF RO N E TC
IN THE C LASSIFICATION P HASE

fore, dynamically processing feature extraction could become
a promising research direction for network traffic classification
in open-set scenarios.
F. Computational Complexity
We present the computational complexity of the core
components during the classification phase, namely the
global-local feature extractor and the Dirichlet distribution.
Specifically, we demonstrate the computational complexity
of these core components for a single view during the
classification phase. The results are presented in Table XI,
where Table XI(a) provides the meanings of acronyms, and
Table XI(b) presents the computational complexity details.
Since this is the classification phase, loss calculation is
unnecessary, and thus KL divergence is excluded from the
computational complexity.
From Table XI(b), it can be seen that the computational
complexity of the Dirichlet distribution is O(K 2 ), where K
represents the number of traffic classes. The computational
complexity of the Dirichlet distribution is related to the
number of classes, whereas the computational complexity of
the global-local feature extractor is independent of the number
of classes. Moreover, we have the following relationship:


H·W
(C
)
·
·
d
+
N
·
d
·
(H
+
d)
+
N
·
d
·
f
O
head
p2
 O(K 2 )
(13)
Therefore, the computational cost of our method is less
affected by the number of classes.
Additionally, we perform a quantitative analysis. We analyzed the time consumption of RoNeTC’s classification phase
in six open-set scenarios. The details of the scenario settings
are presented in Table XII(a), and the time consumption results
are shown in Table XII(b). The experiments are conducted on
an A800 GPU paired with a 14 vCPU Intel(R) Xeon(R) Gold
6348 CPU @ 2.60GHz. For each of the six open-set scenarios,
RoNeTC is run 20 times during the testing phase, and the
average processing time is recorded.
The results indicate that RoNeTC achieves the highest processing speed and throughput in Scenario-A, reaching 220,361
flows/second. Across the other scenarios, there are minimal

TABLE XII
T IME C ONSUMPTION OF RO N E TC IN THE C LASSIFICATION P HASE

differences in terms of “Feature Extractor Time”, “Dirichlet
Distribution Time”, “Total Time”, and “Throughput”. For
example, in Scenario-E(48 classes, 16 packets, with both batch
size and byte count set to 256), the “Feature Extractor Time”
is 1.97 × 10−5 s/flow, the “Dirichlet Distribution Time” is
3.43 × 10−6 s/flow, the “Total Time” is 2.31 × 10−5 s/flow, and
the “Throughput” is 43290 flows/s. In contrast, in ScenarioB(13 classes, 16 packets, with both batch size and byte count
set to 256), the “Feature Extractor Time” is 1.97 × 10−5 s/flow,
the “Dirichlet Distribution Time” is 3.53 × 10−6 s/flow, the
“Total Time” is 2.32 × 10−5 s/flow, and the “Throughput” is
43103 flows/s.
Notably, when the batch size in Scenario-A is set to
the same as other scenarios (denoted as Scenario-A, with
a batch size of 256), the differences in “Feature Extractor Time”, “Dirichlet Distribution Time”, “Total Time”, and
“Throughput” are similarly negligible compared to the other
scenarios. These findings demonstrate that the time cost of
RoNeTC is less influenced by the number of classes and
more significantly affected by the batch size. In scenarios
with a large number of samples, increasing the batch size
can enhance processing efficiency. Alternatively, multi-GPU
parallel processing can also be considered.
VII. C ONCLUSION
In this paper, we propose a novel and reliable open-set
network traffic classification method, RoNeTC. The method
is based on uncertainty estimation to quantify the reliability
of the classification results and to demonstrate the decision
reliability of open-set flow classification in a probabilistic
manner, achieving robust and reliable performance. It combines multiple views by dividing a packet into three segments
and extracting both global and local features from across
and within packets from each view respectively, making full
use of the prior knowledge of the known class samples to
improve the accuracy rate. We perform uncertainty estimation by designing second-order classification probabilities and
assess the reliability of classification decisions by constructing
a distribution of classification probability distributions based
on the classification evidence for each view. Finally, the
classification decisions from multiple views are dynamically
fused through the Dempster combination rule. We extensively
evaluate RoNeTC on six open-set scenarios consisting of three
datasets, as well as adding a large number of unknown samples

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

WANG et al.: RELIABLE OPEN-SET NETWORK TRAFFIC CLASSIFICATION

Fig. 12. Confusion Matrix of ReNeTC on Dataset-I.

Fig. 13. Confusion Matrix of ReNeTC on Dataset-II.

Fig. 14. Confusion Matrix of ReNeTC on Dataset-III.

for robustness comparisons. The experimental results show
that RoNeTC is capable of handling open-set network traffic
classification with superior robustness and reliability.
A PPENDIX
The confusion matrices of RoNeTC on the three closed-set
datasets are shown in Fig. 12, Fig. 13, and Fig. 14.
R EFERENCES
[1] L. Yang, A. Finamore, F. Jun, and D. Rossi, “Deep learning and zero-day
traffic classification: Lessons learned from a commercial-grade dataset,”
IEEE Trans. Netw. Service Manag., vol. 18, no. 4, pp. 4103–4118, Dec.
2021.
[2] R. Li, X. Xiao, S. Ni, H. Zheng, and S. Xia, “Byte segment neural
network for network traffic classification,” in Proc. IEEE/ACM Int. Symp.
Quality Service, Sep. 2018, pp. 1–10.

2327

[3] G. Aceto, D. Ciuonzo, A. Montieri, and A. Pescapè, “MIMETIC: Mobile
encrypted traffic classification using multimodal deep learning,” Comput.
Netw., vol. 165, Dec. 2019, Art. no. 106944.
[4] J. Zhang, F. Li, F. Ye, and H. Wu, “Autonomous unknown-application
filtering and labeling for DL-based traffic classifier update,” in Proc.
IEEE Conf. Comput. Commun., Oct. 2020, pp. 397–405.
[5] S.-J. Xu, G.-G. Geng, X.-B. Jin, D.-J. Liu, and J. Weng, “Seeing traffic
paths: Encrypted traffic classification with path signature features,” IEEE
Trans. Inf. Forensics Security, vol. 17, pp. 2166–2181, 2022.
[6] G. Aceto, D. Ciuonzo, A. Montieri, and A. Pescapé, “Mobile encrypted
traffic classification using deep learning: Experimental evaluation,
lessons learned, and challenges,” IEEE Trans. Netw. Service Manag.,
vol. 16, no. 2, pp. 445–458, Jun. 2019.
[7] R. F. Bikmukhamedov and A. F. Nadeev, “Lightweight machine learning
classifiers of IoT traffic flows,” in Proc. Syst. Signal Synchronization, Generating Process. Telecommun. (SYNCHROINFO), Jul. 2019,
pp. 1–5.
[8] C. Liu, L. He, G. Xiong, Z. Cao, and Z. Li, “FS-Net: A flow sequence
network for encrypted traffic classification,” in Proc. IEEE Conf. Comput. Commun. (INFOCOM), Aug. 2019, pp. 1171–1179.
[9] C. Liu, Z. Cao, G. Xiong, G. Gou, S.-M. Yiu, and L. He, “MaMPF:
Encrypted traffic classification based on multi-attribute Markov probability fingerprints,” in Proc. IEEE/ACM 26th Int. Symp. Quality Service
(IWQoS), Jun. 2018, pp. 1–10.
[10] Y. Wang, H. He, Y. Lai, and A. X. Liu, “A two-phase approach to fast
and accurate classification of encrypted traffic,” IEEE/ACM Trans. Netw.,
vol. 31, no. 3, pp. 1071–1086, Jun. 2023.
[11] Q. Zhou, L. Wang, H. Zhu, T. Lu, and V. S. Sheng, “WF-transformer:
Learning temporal features for accurate anonymous traffic identification
by using transformer networks,” IEEE Trans. Inf. Forensics Security,
vol. 19, pp. 30–43, 2024.
[12] J. Van Amersfoort, L. Smith, Y. W. Teh, and Y. Gal, “Uncertainty
estimation using a single deep deterministic neural network,” in Proc.
Int. Conf. Mach. Learn., 2020, pp. 9690–9700.
[13] J. Moon, J. Kim, Y. Shin, and S. Hwang, “Confidence-aware learning
for deep neural networks,” in Proc. Int. Conf. Mach. Learn., 2020,
pp. 7034–7044.
[14] G. Aceto, D. Ciuonzo, A. Montieri, and A. Pescapé, “DISTILLER:
Encrypted traffic classification via multimodal multitask deep learning,”
J. Netw. Comput. Appl., vols. 183–184, Jun. 2021, Art. no. 102985.
[15] A. Nascita, A. Montieri, G. Aceto, D. Ciuonzo, V. Persico, and
A. Pescapé, “XAI meets mobile traffic classification: Understanding and
improving multimodal deep learning architectures,” IEEE Trans. Netw.
Service Manag., vol. 18, no. 4, pp. 4225–4246, Dec. 2021.
[16] X. Xiao, W. Xiao, R. Li, X. Luo, H. Zheng, and S. Xia,
“EBSNN: Extended byte segment neural network for network traffic
classification,” IEEE Trans. Dependable Secure Comput., vol. 19, no. 5,
pp. 3521–3538, Sep. 2022.
[17] Y. Wang, X. Yun, Y. Zhang, C. Zhao, and X. Liu, “A multi-scale
feature attention approach to network traffic classification and its
model explanation,” IEEE Trans. Netw. Service Manag., vol. 19, no. 2,
pp. 875–889, Jun. 2022.
[18] G. Bovenzi et al., “Benchmarking class incremental learning in deep
learning traffic classification,” IEEE Trans. Netw. Service Manage.,
vol. 21, no. 1, pp. 51–69, Feb. 2023.
[19] A. Nascita, A. Montieri, G. Aceto, D. Ciuonzo, V. Persico, and
A. Pescapé, “Improving performance, reliability, and feasibility in multimodal multitask traffic classification with XAI,” IEEE Trans. Netw.
Service Manage., vol. 20, no. 2, pp. 1267–1289, Jun. 2023.
[20] J. Qu et al., “An input-agnostic hierarchical deep learning framework
for traffic fingerprinting,” in Proc. 32nd USENIX Secur. Symp., 2023,
pp. 589–606.
[21] Y. Chen and Y. Wang, “MPAF: Encrypted traffic classification with
multi-phase attribute fingerprint,” IEEE Trans. Inf. Forensics Security,
vol. 19, pp. 7091–7105, 2024.
[22] Y. Qian et al., “Enhancing resilience in website fingerprinting: Novel
adversary strategies for noisy traffic environments,” IEEE Trans. Inf.
Forensics Security, vol. 19, pp. 7216–7231, 2024.
[23] G. Aceto, D. Ciuonzo, A. Montieri, V. Persico, and A. Pescapé, “AIpowered internet traffic classification: Past, present, and future,” IEEE
Commun. Mag., vol. 62, no. 9, pp. 168–175, Sep. 2024.
[24] S. Mehta and M. Rastegari, “MobileViT: Light-weight, general-purpose,
and mobile-friendly vision transformer,” 2021, arXiv:2110.02178.
[25] A. Dosovitskiy et al., “An image is worth 16×16 words: Transformers
for image recognition at scale,” 2020, arXiv:2010.11929.
[26] A. P. Dempster, “A generalization of Bayesian inference,” J. Roy. Stat.
Soc. B, Methodol., vol. 30, no. 2, pp. 205–232, 1968.

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.

2328

IEEE TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, VOL. 20, 2025

[27] M. Sensoy, L. Kaplan, and M. Kandemir, “Evidential deep learning to
quantify classification uncertainty,” in Proc. Adv. Neural Inf. Process.
Syst., vol. 31, Jan. 2018, pp. 1–11.
[28] B. A. Frigyik, A. Kapila, and M. R. Gupta, “Introduction to the Dirichlet
distribution and related processes,” Dept. Elect. Eng., Univ. Washington,
Washington, DC, USA, Tech. Rep. UWEETR-2010-0006, 2010, vol. 6,
pp. 1–27.
[29] K. Sentz and S. Ferson, “Combination of evidence in Dempster–Shafer
theory,” Sandia Nat. Lab., CA, USA, Tech. Rep. SAND 2002-0835,
2002.
[30] A. Jsang, Subjective Logic: A Formalism for Reasoning Under Uncertainty. Cham, Switzerland: Springer, 2018.
[31] N. J. Perkins and E. F. Schisterman, “The youden index and the optimal
cut-point corrected for measurement error,” Biometrical J., J. Math.
Methods Biosci., vol. 47, no. 4, pp. 428–441, Jun. 2005.
[32] A. Sivanathan et al., “Classifying IoT devices in smart environments
using network traffic characteristics,” IEEE Trans. Mobile Comput.,
vol. 18, no. 8, pp. 1745–1759, Aug. 2019.
[33] S. Dadkhah, H. Mahdikhani, P. K. Danso, A. Zohourian, K. A. Truong,
and A. A. Ghorbani, “Towards the development of a realistic multidimensional IoT profiling dataset,” in Proc. 19th Annu. Int. Conf. Privacy,
Security Trust (PST), 2022, pp. 1–11.
[34] T.-D. Pham, T.-L. Ho, T. Truong-Huu, T.-D. Cao, and H.-L. Truong,
“MAppGraph: Mobile-app classification on encrypted network traffic
using deep graph convolution neural networks,” in Proc. Annu. Comput.
Security Appl. Conf., 2021, pp. 1025–1038.
[35] M. T. Ribeiro, S. Singh, and C. Guestrin, “‘Why should I trust
you?’ Explaining the predictions of any classifier,” in Proc. 22nd
ACM SIGKDD Int. Conf. Knowl. Discovery Data Mining, 2016,
pp. 1135–1144.
Xueman Wang is currently pursuing the Ph.D.
degree in computer technology with the College of
Computer Science, Beijing University of Technology, Beijing, China. Her current research interests
include network traffic classification and artificial
intelligence.

Yipeng Wang (Senior Member, IEEE) received the
Ph.D. degree in computer science from the Institute
of Computing Technology, Chinese Academy of
Sciences (CAS), China, in 2014. He is currently
with the College of Computer Science, Beijing
University of Technology, China. He has published
more than 50 research papers in refereed international journals and conferences, such as IEEE
TRANSACTIONS ON INFORMATION FORENSICS
AND S ECURITY , IEEE/ACM T RANSACTIONS ON
NETWORKING, the IEEE International Conference
on Network Protocols, and IEEE TRANSACTIONS ON NETWORK AND
SERVICE MANAGEMENT. His research interests include networking, network
security, and machine learning. He was a recipient of the Best Paper Award at
the IEEE International Conference on Network Protocols (ICNP) for his protocol format inference technology. He serves as a Regular Reviewer for IEEE
TRANSACTIONS ON INFORMATION FORENSICS AND SECURITY, IEEE/ACM
TRANSACTIONS ON NETWORKING, IEEE TRANSACTIONS ON MOBILE
COMPUTING, IEEE JOURNAL ON SELECTED AREAS IN COMMUNICATIONS,
IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, IEEE
TRANSACTIONS ON COGNITIVE COMMUNICATIONS AND NETWORKING,
and IEEE INTERNET OF THINGS JOURNAL. He serves as a Program Committee of IJCAI-21, IJCAI-22, IJCAI-23, IJCAI-24, and IJCAI-25.

Yingxu Lai received the Ph.D. degree from Chinese Academy of Sciences in 2003. She joined the
College of Computer Science, Beijing University of
Technology, in 2003. She was a Visiting Scholar
with Arizona State University from 2013 to 2014.
She is currently a Full Professor. She has had
over 70 papers published in various international
journals and conferences. Her research interests
include cloud computing, network security, edge
computing and trusted computing. She is an Associate Editor of Journal of Artificial Intelligence
and Technology.

Zhiyu Hao received the Ph.D. degree in computer system architecture from Harbin Institute of
Technology in 2007. He is currently a Professor with the Zhongguancun Laboratory, Beijing.
He has published over 40 papers in journals and
conferences, including IEEE TRANSACTIONS ON
PARALLEL AND DISTRIBUTED SYSTEMS, IEEE
TRANSACTIONS ON INFORMATION FORENSICS
AND S ECURITY , and IEEE T RANSACTIONS ON
SERVICES COMPUTING. His research interests
include network security and system virtualization.

Alex X. Liu (Fellow, IEEE) received the Ph.D.
degree in computer science from The University
of Texas at Austin in 2006. He is currently the
President of the Software Engineering Institute and
the Chief Security Officer of Midea Group. Before
that, he was the Chief Scientist of Ant Group and
further before that, he was a Professor with the
Department of Computer Science and Engineering,
Michigan State University. His research interests
include cybersecurity, cloud computing, dependable
computing, and privacy-preserving computing. He
is a member of Academia Europaea, a member of European Academy of
Sciences and Art, an IET Fellow, an AAIA Fellow, and an ACM Distinguished
Scientist. He received the IEEE & IFIP William C. Carter Award in 2004,
the National Science Foundation CAREER Award in 2009, Michigan State
University Withrow Distinguished Scholar (Junior) Award in 2011, and
Michigan State University Withrow Distinguished Scholar (Senior) Award in
2019. He received the Best Paper Awards from SECON-2018, ICNP-2012,
SRDS-2012, and LISA-2010. He has served as the TPC Co-Chair for ICNP
2014 and IFIP Networking 2019. He has served as an Editor for IEEE/ACM
TRANSACTIONS ON NETWORKING and an Area Editor for Computer Communications. He is also an Associate Editor of IEEE TRANSACTIONS ON
DEPENDABLE AND SECURE COMPUTING and IEEE TRANSACTIONS ON
MOBILE COMPUTING.

Authorized licensed use limited to: Indian Institute of Technology Hyderabad. Downloaded on February 27,2026 at 09:52:38 UTC from IEEE Xplore. Restrictions apply.
PAPER_TEXT
