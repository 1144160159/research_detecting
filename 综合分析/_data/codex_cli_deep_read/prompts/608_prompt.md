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
# [608] An Efficient Website Fingerprinting for New Websites Emerging Based on Incremental Learning
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
编号：608
题名：An Efficient Website Fingerprinting for New Websites Emerging Based on Incremental Learning
年份：2025
DOI：10.1109/tnsm.2025.3627441
来源：IEEE Transactions on Network and Service Management
PDF：paper/10.1109_TNSM.2025.3627441.pdf
已有粗分类：加密流量分类与应用识别
二级关联：无
相关性：强相关，分数 12
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\608.txt
- 原始字符数：86151
- 本次发送字符数：86151
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

365

An Efficient Website Fingerprinting for New
Websites Emerging Based on Incremental Learning
Zhengge Yi , Tengyao Li , Meng Zhang, Xiaoyun Yuan , Shaoyong Du , and Xiangyang Luo

Abstract—Website fingerprinting attacks leverage encrypted
traffic features to identify specific services accessed by users
within anonymity networks such as Tor. Although existing WF
methods achieve high accuracy on static datasets using deep
learning techniques, they struggle in dynamic environments
where anonymous Websites continually evolve. These methods
typically require full retraining on composite datasets, resulting
in substantial computational and storage burdens, and are particularly vulnerable to classification bias caused by data imbalance
and concept drift. To address these challenges, we propose EILWF, a dynamic WF framework based on incremental learning
that enables efficient adaptation to newly emerging websites
without the need for full retraining. EIL-WF incrementally
trains lightweight, independent classifiers for new website classes
and integrates them through classifier normalization and energy
alignment strategies grounded in energy-based model theory,
thereby constructing a unified and robust classification model.
Comprehensive experiments on two public Tor traffic datasets
demonstrate that EIL-WF outperforms existing incremental
learning methods by 6.2%–20.2% in identifying new websites
and reduces catastrophic forgetting by 5.4%–20%. Notably, EILWF exhibits strong resilience against data imbalance and concept
drift, maintaining stable classification performance across evolving distributions. Furthermore, EIL-WF decreases training time
during model updates by 2–3 orders of magnitude, demonstrating substantial advantages over conventional full retraining
paradigms.
Index Terms—Website fingerprinting, Tor anonymous network,
traffic analysis, incremental learning.

I. I NTRODUCTION
NONYMOUS communication networks, particularly the
Tor network, are widely valued for their strong privacy
protection features [1]. Through its distinctive onion routing and multi-hop encryption mechanisms, the Tor network
effectively obscures the traceability of user communications,

A

Received 14 February 2025; revised 29 June 2025; accepted 26
October 2025. Date of publication 30 October 2025; date of current
version 29 December 2025. This work is supported by the National
Natural Science Foundation of China (No.62402523, No.U23A20305,
No.62172435), Innovatior Scientists and Technicians Troop Construction
Proiects of Henan Province(No.254000510007), National Key R&D Program
of China (No.2022YFB3102900), Key Research and Development Project
of Henan Province (No.252102211087, No.221111321200), and Natural
Science Foundation of Henan (Grant No.232300421098). The associate editor
coordinating the review of this article and approving it for publication was
Q. Yan. (Corresponding author: Xiangyang Luo.)
The authors are with the Henan Province Key Laboratory of Cyberspace
Situation Awareness, People’s Liberation Army Information Engineering
University, Zhengzhou 450001, China (e-mail: yzhengge@163.com;
litengyao@aliyun.com; zhangmeng_ieu@sina.com; yuanxyzz@outlook.com;
shaoyong.du.cs@gmail.com; luoxy_ieu@sina.com).
Digital Object Identifier 10.1109/TNSM.2025.3627441

thereby significantly enhancing privacy security. However,
this high level of anonymity remains vulnerable to certain
advanced traffic analysis techniques [2], [3], such as Website
Fingerprinting (WF) attacks [4], [5].
Websites display distinctive traffic characteristics due to
variations in their structure, content, and interaction patterns,
collectively termed the fingerprints of websites. The WF methods rely on classification models, where attackers collect traffic
from target websites to train models and extract fingerprints,
thus constructing a set of monitored websites. As shown in
Figure 1, during the deployment phase, attackers only need to
analyze the traffic characteristics of users accessing the Tor
network to identify the websites they visit.
In recent years, DL-based WF methods have demonstrated remarkable effectiveness in static data classification
tasks [6], [7], [8], [9], [10], [11], [12], [13]. State-of-theart benchmark models like DF [6], TikTok [7], VarCNN [8],
WF-Transformer [10] and ARES [12], achieve classification
accuracy rates of 98%–99% on both AWF [14] and DF [6]
datasets. However, these static classification paradigms struggle to maintain performance in dynamic network environments
where new website categories continuously emerge. When new
website categories are introduced, as illustrated in Figure 1,
the model must be retrained on both old and new data and
subsequently deployed. This retraining paradigm incurs significant computational costs and introduces memory challenges
from storing large historical datasets, particularly for devices
with constrained storage capacity.
Class Incremental Learning (CIL) [15], originally developed
in the field of computer vision, has recently gained substantial
attention as a promising paradigm for addressing the challenge
of dynamically expanding monitored datasets. This approach
focuses on building deep learning models with the capability
for continual learning, enabling them to incrementally acquire
knowledge of new classes from sequential data streams while
maintaining recognition performance on previously encountered classes [16], [17]. The concept of CIL offers valuable
insights for WF, where the set of monitored websites evolves
over time. However, the Tor network’s distinctive multihop encrypted routing mechanism enhances the anonymity
and resistance to traffic analysis, introducing fundamental
differences in the feature space between WF and conventional
visual domains. Consequently, directly transferring existing
CIL techniques to WF scenarios often results in suboptimal
performance.
Moreover, applying continual learning to WF in
dynamic network environments introduces two challenges:

c 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence
1932-4537 
and similar technologies. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

366

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

Fig. 1.
The illustration of WF deployments, during the update of the
monitored set, the saved data of old websites and the data of new websites are
combined to retrain the WF classification model, which is then redeployed.

1) Imbalanced training samples: In many stages, training data
are collected under favorable conditions, with popular websites
and relaxed security policies providing abundant samples.
In contrast, strict privacy protections, limited monitoring
access, or narrow data collection windows at some stages
result in scarce data. This imbalance can cause the model
to favor well-represented websites, introducing bias in its
predictions. 2) Traffic feature drift: Over time, updates to
network protocols, changes in webpage content structures,
and adjustments in server response behaviors can all lead to
shifts in the traffic feature distribution of a given website.
These shifts may lead to inter-class feature space drift, making
it difficult for conventional CIL methods to maintain stable
recognition performance across different stages.
To address the aforementioned challenges, this paper proposes the EIL-WF framework, a lightweight solution that
dynamically updates the monitoring set via stage-specific classifiers, eliminating the need to cache historical data. Initially,
a fixed backbone network is trained to extract general traffic
features. For each new batch of websites, only the corresponding lightweight classifier is trained, while parameters
from earlier stages remain frozen. This architectural separation
ensures parameter independence across classifiers. As a result,
classifiers trained on low-sample data are shielded from
the influence of high-sample distributions, thereby mitigating
model bias caused by data imbalance. At the same time,
allocating frequently updated website traffic to dedicated classifiers enables targeted local optimization, thereby reducing
interference with traditionally stable categories and isolating
their feature spaces from contamination.
To support effective classifier selection during inference
in a unified model, we introduce free energy scores as the
confidence metric, inspired by energy-based modeling theory.
This metric provides a more robust and flexible alternative
to conventional confidence estimators, especially under the
backward-compatible constraints of incremental learning. By
assigning lower energy to in-distribution data and higher
energy to out-of-distribution data, it enables more accurate and
dynamic routing of samples across classifiers. Furthermore, to
improve the fairness inference of classifiers, we design two
normalization loss functions that normalize the energy output

distribution of classifiers from each phase. By reducing the
mutual information between data and non-target classifiers and
constraining excessively high energy values of classifiers, we
ensure that the energy output levels remain consistent across
different stages. In addition, we propose an energy alignment
strategy which improves the performance of classifiers trained
on low-sample data without introducing additional parameter
calculations.
The specific contributions are as follows:
• We propose EIL-WF, an incremental learning framework
for website fingerprinting, which trains multiple independent lightweight classifiers. This design enables efficient
model updates without requiring access to previously collected data from old websites. Additionally, we introduce
a free energy-based confidence metric to quantify the
reliability of each classifier.
• We develop a classifier normalization training strategy,
incorporating two dedicated regularization loss functions.
This strategy ensures both the independence of classifiers
and consistently high confidence levels for in-distribution
data, effectively improving model stability during incremental updates.
• We design an energy alignment strategy that mitigates
the negative impacts of data imbalance and distribution
shifts. By aligning the energy outputs of classifiers trained
on datasets with varying scales, this approach enhances
model robustness in dynamic environments.
• We conduct comprehensive experiments on two widelyused public WF datasets, DF and AWF. The results
demonstrate that EIL-WF significantly outperforms existing incremental learning methods in terms of both
accuracy and resistance to catastrophic forgetting.
Furthermore, we thoroughly evaluate the generalization
ability and practical effectiveness of EIL-WF in dynamic
website fingerprinting scenarios.
II. R ELATED W ORK
In this section, we first introduce website fingerprinting,
which has been significantly enhanced on static data through
the use of deep learning in recent years. We then discuss class
incremental learning, a technique that has gained considerable
attention in the field of computer vision.
A. Website Fingerprinting Attack
WF attack is a technique that identifies specific websites
visited by users through the analysis of patterns in network
traffic. It leverages information such as packet size, timing
intervals, and traffic direction to identify visited websites,
effectively bypassing the protections offered by anonymity
networks such as Tor [18]. As network environments become
increasingly complex and as Tor’s defensive measures are
implemented, WF methods continuously evolve and improve.
Earlier WF methods primarily relied on manually configured feature extraction techniques and traditional classifier [3],
[19], [20], [21], [22], such as Support Vector Machines [21]
and k-Nearest Neighbors [22]. However, the effectiveness of
these methods is constrained by feature selection processes and

YI et al.: AN EFFICIENT WEBSITE FINGERPRINTING FOR NEW WEBSITES EMERGING

classifier designs [23]. Their performance often degrades in the
presence of dynamic traffic patterns and adversarial defenses
deployed in realistic, large-scale network environments.
With the rise of deep learning, WF leveraging deep
learning have become a focal point of research. The Deep
Fingerprinting (DF) [6] method utilizes one-dimensional
(1D) convolutional neural networks to automatically learn
and extract traffic features. Notably, it achieves high classification accuracy by solely relying on packet direction
features. Subsequent advancements have further enhanced the
performance and robustness of WF attacks by incorporating
novel deep learning techniques [7], [8], [9], [10], [24]. For
instance, such as VarCNN [8] and WF-Transformer [10],
enhance classification performance further by incorporating architectures like ResNet, dilated convolutions, and
Transformer models. These additions allow the models to
handle high-dimensional and complex network traffic more
effectively. TikTok [7] and RF [9] models further exploit
packet temporal dynamics to generate more robust traffic
representations, underscoring the distinctive role of temporal features in WF attacks, particularly when dealing with
defensive data, where they exhibit enhanced performance. The
Holmes [24] method leverages temporal and spatial traffic
patterns to identify websites early in transmission, enhancing
attack efficiency and reliability.
To address the identification challenges arising from
traffic mixing during multi-tab browsing in the Tor
network, [25], [26], [27] proposed a traffic conversion
technique based on segmentation point extraction, which
segregates multi-tab flows into distinct single-label streams to
facilitate classification. However, its classification performance
deteriorates markedly as the number of open pages increases.
Subsequently, BAPM [28] introduced an attention mechanism that substantially enhances the model’s capacity to
represent multi-label data, thereby improving identification
accuracy. TMWF [11] tackles multi-label WF identification
as an ordered set prediction problem, introducing an end-toend multi-label WF model capable of accurately classifying
multi-label network traffic. ARES [12] reframes the problem
as a multi-classifier task based on local traffic patterns and
incorporates an improved Transformer model (Trans-WF),
achieving high recognition accuracy even under unknown label
counts and adversarial defense conditions.
Faced with the common issue of limited training samples in real-world network environments, researchers have
proposed various few-shot learning-based fingerprinting methods. These approaches maintain high recognition accuracy
despite limited training data, effectively reducing dependence on large-scale labeled datasets. For instance, Triplet
Fingerprinting (TF) [29] employs a triplet network to
achieve N-shot learning, enhancing the model’s generalization capability. Contrastive Fingerprinting (CF) [30] adopts a
contrastive learning framework combined with data augmentation strategies, demonstrating good accuracy and robustness
under data-scarce conditions. NetCLR [13] integrates semisupervised and self-supervised learning to enhance traffic
representation, maintaining strong classification performance
even in previously unseen network conditions. However, WF

367

methods based on few-shot learning models often entail high
spatial complexity (e.g., TF with a complexity of O(n!)),
making them less suitable for large-scale data processing.
Furthermore, although methods such as NetCLR can maintain
accuracy over time, they still struggle with rapidly changing
websites, whose evolving feature space requires retraining on
complete datasets.
In summary, although current WF methods have attained
notable advancements, several critical challenges persist. Most
existing website fingerprinting approaches assume a static
monitored set and lack systematic investigation into the
dynamic expansion of monitored websites, limiting their
adaptability to real-world scenarios where website categories
evolve continuously. Additionally, challenges such as model
bias due to imbalanced sample distributions and local feature drift in frequently updated websites remain inadequately
addressed.
B. Class Incremental Learning
When a deep learning model is trained on new tasks
or data, it tends to over-adapt to the new data, resulting
in poor performance on previously learned knowledge. This
phenomenon is known as catastrophic forgetting. To address
this issue, researchers have focused on developing efficient
algorithms that enable models to continuously learn new
categories from dynamically evolving data streams. These
algorithms allow models to incrementally absorb and adapt
to new information without requiring complete retraining,
thereby significantly reducing computational and storage costs.
This emerging learning paradigm is widely referred to as Class
Incremental Learning (CIL) [31], [32].
Class incremental learning has made notable strides in
the field of computer vision. Depending on the nature of
the problem and the applied strategies, current CIL methods
can be broadly classified into two categories: data-based
methods [15], [33] and parameter-based methods [34], [35].
Data-based CIL methods focus on preserving knowledge of
previous categories by storing portions of data or generating
representative samples, with the aim of mitigating the forgetting of old categories when new ones are learned [34].
These methods, especially replay-based algorithms, have been
widely adopted in image classification tasks due to their
simplicity and practicality. However, they typically rely on
relatively small sample sets for rehearsal, often much smaller
than the size of the training set in each incremental learning
phase, potentially causing data imbalance problems. Moreover,
the requirement to replay old category samples increases
storage overhead and risks that these samples may no longer
accurately represent their features over time. This problem is
particularly pronounced in network traffic scenarios, where the
dynamic nature of data can cause past samples to become
misaligned with current conditions.
Parameter-based class incremental learning, on the contrary,
focuses on adjusting and optimizing model parameters to
retain knowledge of old categories while integrating new ones.
One commonly used approach is parameter regularization,
which evaluates the importance of model parameters and

368

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

constrains their updates to preserve knowledge of previous
categories [36]. However, due to the inherent ambiguity
and imbalance in network traffic, maintaining the consistent importance of the parameters across different learning
stages becomes challenging, complicating the training and
deployment of such models in real-world scenarios. Another
approach involves dynamically modifying the model structure
by expanding or pruning it to incorporate new category knowledge [16], [37], [38]. Zhou et al. proposed EASE [16], which
introduces an expandable subspace ensemble, generating taskspecific subspaces via adapters and synthesizing historical
class features through semantic-guided prototype completion
without exemplars. Subspace recombination enables incremental learning in high-dimensional decision space, offering
a novel methodological perspective for CIL. Although this
method effectively adapts to new categories, it also needs
to address potential interference between models at different
learning stages.
III. P RELIMINARIES
Although early research achieved significant success in WF
within static classification tasks, dynamically updating website
classification models has remained a persistent challenge. In
this section, we first define a novel WF learning paradigm
based on incremental learning. Furthermore, we introduce the
energy model theory, which serves as an effective classification
confidence evaluation metric for the proposed incremental
learning framework.
A. CIL Problem Definition of WF
Both class incremental learning-based WF and traditional
WF fundamentally train a classification model to recognize
websites in the monitored set. The difference lies in the
updating of the monitored set: traditional methods require
saving all historical data and retraining the model by replaying
this data to ensure that the model can recognize all historical
samples [31]. In contrast, the CIL method only necessitates
the use of the latest sample data for training, allowing the
model to gradually learn new classes or samples without the
need to retain all historical data. Below is a brief definition of
incremental learning in WF.
Incremental learning for WF constructs an initial deep
learning-based classification model M0 . At each subsequent
learning stage t ∈ τ = {0, 1, . . . , t}, the model is updated
t
using only the current monitored subset Dt = {(xi , yi )}K
i=1 ,
where Kt denotes the number of website classes at stage t and
t represents the data distribution at this stage. The
(x , y) ∼ PD
updated model
 Mt is expected to preserve knowledge of prior
websites ti=0 Di while minimizing catastrophic forgetting
across stages.
In the multi-classifier framework considered in this study,
each classifier fθi , where i ∈ τ and θ represent the parameters of
the classifier, is trained on the data from a specific incremental
stage Di . During inference, for an input sample x, we define
it as in-distribution with respect to classifier fθi if x ∈ Di ,
meaning the sample conforms to the distribution seen during
training of that classifier. Conversely, if x ∈
/ Di , it is considered

Fig. 2. Illustration of the softmax and free energy scores of sample across
target and non-target classifiers.

out-of-distribution relative to fθi . For a given input x, the
classifier fθi such that x ∈ Di is referred to as the target
classifier, and the remaining classifiers fθj for which x ∈
/ Dj
are considered non-target classifiers. The central challenge lies
in correctly identifying the target classifier for each test sample
and effectively distinguishing in-distribution samples from outof-distribution samples, particularly in the presence of limited
training data and evolving decision boundaries.

B. Energy-Based Model Theory
In this method, we use free energy as a confidence scoring
criterion to replace the commonly adopted softmax function
in WF tasks. Although softmax is computationally efficient,
its strong reliance on posterior probabilities often leads to
overconfidence when the model encounters out-of-distribution
samples [39]. As shown in Figure 2, softmax tends to produce
scores close to 1 across multiple classifiers, resulting in a lack
of clear separation and reduced effectiveness in selecting the
appropriate target classifier during inference. In contrast, the
energy-based scoring function does not depend on a shared
class probability structure and supports task-wise independent
modeling. This property is particularly advantageous for discriminative selection in multi-classifier settings. Free energy
provides a meaningful measure of the compatibility between
the input and each sub-classifier, enabling dynamic selection
and effective inter-class discrimination. Such a mechanism
offers greater robustness and discriminative power in incremental scenarios characterized by ambiguous class boundaries
and sparse samples.Below, we provide a brief overview of the
fundamental principles of energy models.
The foundational concept of the energy model, as proposed
by LeCun et al. [40], involves the creation of a function that
translates the model’s output values into an energy scalar,
which indicates the interdependence between the data and the
model parameters. This energy scalar, through the application
of the Gibbs distribution, can be converted into probability density, thereby enabling a more flexible classification
approach for the model.
Firstly, the classifier of a deep learning model can be
abstracted as a function f with a value domain in RK , where
K denotes the total number of classes. For a given input data
point x, after passing through the neural network, it yields
a logits vector. For class yi ∈ RK , the energy score is

YI et al.: AN EFFICIENT WEBSITE FINGERPRINTING FOR NEW WEBSITES EMERGING

369

Fig. 3. The illustration of the training phase of EIL-WF. The system incrementally learns from a continuously evolving stream of website traffic data. In
the initial stage, a pre-trained and frozen feature extractor is used to train the first classifier for the initial set of monitored websites. In each new stage, a
classifier is independently trained for newly added websites, while the backbone and previous classifiers remain fixed to preserve past knowledge. The final
model consists of the shared feature extractor and all stage-specific classifiers, each handling data from its respective training stage.

defined as:
E (x , yi ) = −f (x )[yi ].

(1)

Here, f(x) provides the logits vector, and −f (x )[yi ] represents
the logit for class yi .
Through Gibbs distribution, the energy values can be transformed into probability densities [40]:
p(y i |x ) =

e −E (x ,yi )/T
,


e −E (x ,y )/T

(2)

y  ∈RK

where T is the temperature parameter controlling the smoothness of the distribution; specifically, as T → 1 , the Gibbs
distribution approximates the softmax activation values. The
denominator serves as the normalization constant, known as
the partition function. The negative logarithm of the partition
function defines the Helmholtz free energy F (x , fθ ), which is
expressed as:

e f (x ,y)/T .
(3)
F (x ; f ) = −T log
y∈RK

Unlike softmax confidence scores, which are prone to overconfidence issues, energy scores are theoretically aligned with
the input’s probability density. A classifier typically assigns
lower energy scores to data observed within the training set,
while higher energy scores are associated with unseen out-ofdistribution data. Additionally, under the same parameters, the
energy output of the target classifier should be lower than that
of non-target classifiers.
IV. D ESIGN OF EIL-WF
In this section, we first present an overview of the proposed
EIL-WF. Subsequently, we detail the optimization procedure
of our method.

existing WF methods to have continuous learning capability.
The proposed EIL-WF is an incremental learning method
that employs the dynamic network structure strategy, and
its network structure consists of two main components: the
backbone network and the classifier. To simplify the design
and effectively extract raw traffic features, we select the wellestablished DFnet as the backbone network for extracting
network traffic features. The classifier is composed of fully
connected layers using linear activations. Our proposed solution is also suitable for other WF models, such as VarCNN,
WF-Transformer, and others.
The training phase of the proposed EIL-WF involves a
continuous process of appending classifiers. As illustrated in
Figure 3, the proposed EIL-WF trains an isolated classifier
for the newly added websites of each stage, updating the
monitored set while completing the model update. In the
initial stage, a pre-trained backbone network fη is provided,
which is frozen for subsequent stages. The initial model
M0 consists of {fη |fθ0 }, where fθ0 denotes the classifier of
stage 0. η and θ represent the parameters of the backbone
and classifier, respectively. Subsequently, for each incremental
stage i , i ∈ τ , we train a specific classifier fθi to learn the
i of that stage. Upon completing
website traffic knowledge PD
t learning stages, the updated model Mt is represented as
{fη |fθ0 , fθ1 , . . . , fθt }.
In the testing phase, traffic first passes through the backbone
network for feature extraction, and then the extracted features
are fed into each classifier. The system selects the classifier
with the highest confidence for the test data (Eq. (4)), and
the classification result of that classifier is taken as the final
prediction result (Eq. (5)).
i ∗ = arg max H i (x ),
i∈τ

y∈Y ∗

A. Solution Overview
In this work, we propose a general incremental learning framework free of rehearsal for WF, aiming to enable

∗

y ∗ = arg max fθi (y | x ).

(4)
(5)

As shown above, a fair confidence function is essential to
ensure that the data is predicted in the correct classifier. The
energy score, which is theoretically consistent with probability

370

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

density and less susceptible to overconfidence, demonstrates
an effective ability to distinguish between in-distribution and
out-of-distribution data [34], [39]. However, when applied to
website fingerprinting, the inherent homogeneity and ambiguity in the traffic of certain websites compromise the
capability of the aforementioned approach to mitigate interstage interference. Furthermore, it is prone to the influence
of website sample imbalance, resulting in an inability to
effectively standardize output levels across different classifiers
trained on dynamic website data streams.
To unify the energy output levels across different stages of
WF classifiers, we design two regularization loss functions:
energy constraining and parameter distancing. These functions are employed to normalize the training of classifiers,
thereby mitigating overfitting issues and inter-stage classifier
interference. The details of the classifier normalization training
are elaborated in Section IV-B. In response to the challenge
of website sample imbalance during WF model training, we
introduce energy scalars for their corresponding classifiers.
This alignment of energy scores with classifiers trained on
high-sample website datasets aims to prevent model bias, as
further described in Section IV-C. During the testing phase, a
fair confidence function is designed to ensure that test traffic
is accurately classified by the corresponding classifiers, with
the specifics outlined in Section IV-D.
B. Classifier Normalization Training
Similar to traditional classifier training, the multi-classifiers
trained by the proposed EIL-WF need to maintain high
classification confidence for the websites at their respective
stages. To this end, we first employ softmax cross-entropy to
optimize the model parameters:
(t)

LCE = E

(t)

(x ,y)∼PD

[− log p(y|x )].

(6)

Combining Eq. (2) and Eq. (3) reveals that cross-entropy
optimization inherently minimizes free energy F (x ; fθt ) =


− log y  e fθt (x ,y ) , as shown in Eq. (6) and Eq. (7). From an
information-theoretic perspective, cross-entropy loss directly
bounds mutual information between data x and labels y
through:
(t)

I (x ; y) ≥ log K − LCE ,

constraint mechanism that limits outputs with excessively low
energy values. This ensures that classifiers from different
stages maintain a reasonable distribution of energy values
within the energy space when processing data from both target
and non-target websites. Since the free energy is a negative
value, we use its square as a loss function to penalize the low
free energy values during output. The energy constraining loss
function can be calculated by Eq. (8).
  



2 
,
(8)
LtF = Ex ∼P t I F x ; fθt < ζ · F x ; fθt
D

where ζ represents the threshold value for the triggering free
energy constraining, and I denotes the discriminant function,
the output of which is a boolean value. When F (x ; fθt ) is
less than the energy threshold ζ, the value is set to 1, thereby
triggering the constraining to avoid over-sharp distributions.
Conversely, if F (x ; fθt ) is equal to or exceeds ζ, the value is
set to 0, indicating that the constraining is not triggered.
Moreover, the training process of a neural network can
be understood as optimizing the mutual information between
data and model parameters. As free energy decreases, this
mutual information increases, reflecting the model’s improved
capacity to capture data structure. However, classifiers trained
at the current stage may still output high confidence scores for
data from earlier stages, leading to false activations on out-ofdistribution samples. This occurs because the current classifier
θt may inadvertently encode feature patterns from historical
data Dt  , resulting in logit overlap, where predicted scores for
target and non-target classes become indistinguishably close.
As a consequence, the mutual information I (Dt  ; θt ) becomes
undesirably high.
To mitigate this, we aim to reduce the current classifier’s
ability to encode features from previous stages. Since the EILWF framework avoids retaining historical data, we cannot
explicitly correct this behavior through data replay. Instead, we
reduce mutual information indirectly by encouraging parameter distancing: the current classifier θt is encouraged to stay
distant from historical classifiers {θ1 , . . . , θt−1 } in parameter
space, thereby minimizing latent representational overlap. We
implement this through the Parameter Distancing Mechanism,
which seeks to reduce I (Dt  ; θt ) for t  = t. The corresponding
loss function term is:

(7)

where K is the number of categories. Maximizing I(x;y)
ensures classifier θt focuses on current-stage features.
Unlike traditional approaches, our approach also requires
each classifier to exhibit low classification confidence for data
from non-target stages. The energy model theory requires
Fin-distribution  Fout-of-distribution . However, the emerging
of new websites data causes distribution non-stationarity
and class boundary blurring, leading to two critical issues:
1) Excessive sharpness in prediction distributions leads to
suboptimal energy minimization, eroding prior classifier capabilities; 2) Non-target classifiers generate spurious low energy
responses to current-stage data, violating distribution separation requirements.
To prevent the overall energy of certain classifiers from
being lower than that of non-target, we design an energy

(t)

Ldis =

t−1


θt − θi 2 .

(9)

i=1

This encourages the model to decouple from obsolete representations, reduces interference across stages, and promotes
specialization on current tasks without relying on stored
historical data.
The unified loss function combines these objectives:
(t)

(t)

(t)

(t)

Ltotal = LCE + λLenergy + γLdis ,

(10)

where λ and γ balance the dual requirements of confident
in-distribution classification and energy-space separation from
non-target classifiers. When new stage data arrives, EIL-WF
(t)
initializes a classifier and optimizes θt using Ltotal , then
freezes and aggregates θt with prior classifiers. This process
is visualized in Algorithm 1 and the upper part of Figure 4.

YI et al.: AN EFFICIENT WEBSITE FINGERPRINTING FOR NEW WEBSITES EMERGING

371

Fig. 4. Overall framework of the proposed EIL-WF. The upper part illustrates the process of classifier normalized training for the latest stage of the training
phase, and the lower part depicts the classifier selecting process of multi-classifier aggregation during the testing phase. To aid comprehension, we provide
schematic diagrams of two types of normalized training loss functions: energy constraining and parameter distancing.

C. Energy Alignment
Within the EIL-WF framework, classifiers operate independently, minimizing interference and isolating the model bias
induced by imbalanced data. Furthermore, classifier normalization training constrains excessive energy outputs, ensuring
minimal interference between model parameters. However,
despite these advantages, EIL-WF encounters challenges in
enhancing the performance of classifiers trained on low-sample
data.
This limitation stems from practical constraints imposed
by real-world network environments and security policies,
which restrict the availability of low-sample data from certain
websites. As a result, classifiers trained on limited or noisy
data continue to exhibit suboptimal accuracy. This is particularly evident in the energy output space, where classifiers
trained on low-sample data display significantly higher energy
values compared to others. This discrepancy is illustrated
in Figure 5(a), where the classifiers from stages 1 and 3,
trained on low-sample data, exhibit notably higher energy
outputs than those trained on Sufficient data. Consequently,
classifiers trained on low-sample data may incorrectly classify
test samples, as their disproportionately high energy values
dominate the decision-making process despite the presence of
more reliable classifiers.
To address this issue and ensure that classifiers trained
on varying data qualities maintain comparable effectiveness
during inference, we introduce the Energy Alignment (EA)
strategy. EA is a lightweight and practical mechanism designed
to harmonize the energy outputs of classifiers trained on

Algorithm 1 Classifier Normalization Training
Given components: Pre-trained backbone fη , fixed stage
t−1
classifier fθi i=0 , latest stage identification t, temperature T, learning rate ;
Input: Training data Dt ;
Output: The t-th classifier parameters θt ;
1: for x in Dt do
2:
Initialize classifier fθt for the stage t;
3:
Extract the traffic feature
 fη (x
 );
4:
Generate the logits fθt fη (x ) ;
5:
Calculate the cross-entropy loss Ltce by Eq. (6);
6:
Calculate the free energy F x ; fθt by Eq. (3);
7:
if F (x ; fθt ) < ζ then
2

8:
Calculate LtF = F x ; fθt ;
9:
// Energy constraining loss
10:
end if
t−1

11:
Calculate Ltθ = 1t
||θt − θi ||2 ;
i=0

// Parameters distancing loss
Calculate the total loss by Lttotal = Ltce +λLtF +γLtθ ;
14:
Update θt by θt ← θt −  · Ltotal ;
15: end for
16: Return: θt .
12:
13:

imbalanced datasets, especially those with severely limited
training samples.
Rather than aligning the absolute energy values across classifiers, EA focuses on preserving a relative energy advantage

372

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

Fig. 5. Energy level of in-distribution data for stage classifiers with (b) and
without (a) using EA where the 1st and 3rd classifiers are trained on lowsample data. The Y-axis represents the average energy output of the stage
classifiers, and the X-axis represents the stage index of the classifiers.

for the target classifier. Specifically, the energy output of the
classifier trained on low-sample data is adjusted by an additive
scalar Δ, such that its total energy remains consistently
lower than the energy output of non-target classifiers, with a
safe margin defined by a tunable threshold . Formally, the
condition is enforced as:
EL + Δ < Enon-target − ,

(11)

where EL is the original energy output of the target classifier
trained on low-sample data, Enon-target denotes the energy
values of all non-target classifiers for the same input, and 
is a small positive constant that prevents ambiguous overlaps
due to numerical instability or noise.
This formulation ensures that, even in the presence of
limited training data, the classifier corresponding to the target label remains energetically favorable compared to its
non-target counterparts. As illustrated in Figure 5(b), the
application of this adjustment results in energy outputs for lowsample classifiers that are not only more comparable to those
from high-sample classifiers but also strategically prioritized
during inference. The EA strategy, therefore, establishes a
simple yet effective decision boundary in the energy space,
mitigating the adverse impact of low data availability while
enhancing prediction reliability.
To further enhance the performance of classifiers trained
on low-sample data, we employ four data augmentation
strategies: random insertion, random deletion, random splitting, and random merging. These techniques are designed to
enrich the model’s ability to capture the diverse features of
website traffic. The random insertion and deletion strategies
simulate fluctuations in packet size due to dynamic content changes [30], while the random merging and splitting
strategies account for variations in burst size, resulting from
differences in link bandwidths [13].
The EA strategy requires no modifications to the model’s
learning paradigm or the introduction of additional parameters.
Instead, it applies a scalar adjustment during inference to
improve the performance of classifiers trained on low-sample
data. By aligning the energy outputs, we mitigate the negative
effects of low-sample data and ensure that all classifiers,
regardless of their training data scale, maintain similar energy
levels, resulting in more accurate and robust predictions.

Algorithm 2 Classifier Selecting
Given components: The fixed backbone fη , stage classifiers, fθi i∈τ , energy scalars Δ(i ), i ∈ τ ;
Input: Test traffic sample x;
Output: The classification result y ∗ ;
1: Extract traffic feature fη (x );
2: for i = 1, . . . , t do


3:
Generate the i-th logits fθs fη (x ) ;
4:
Calculate the free energy F x ; fθi ;


5:
Calculate the classification confidence H x , fθi
6:
by Eq. (12);
7: end for
8: Selecting correct classifier identification i ∗ by Eq. (13);
∗
9: Classify x in i ∗ -th subset by y ∗ = arg max fθi (y | x );
y∈Y ∗

10: Return: y ∗ .

D. Classifier Selecting
In previous studies [39], researchers show that data within
the distribution generally have lower free energy compared to data outside the distribution, i.e., F (xi ; fθi ) >
j
j
F (xj ; fθi ), F (xj ; fθ ) > F (xi ; fθ ), where xi represents
in-distribution data of i-th stage, while j denotes out-ofdistribution data of j-th stage.
During the training phase, we normalize the Helmholtz
free energy outputs of each classifier, ensuring consistent
comparability of the energy scale between classifiers at different stages. When training classifiers on low-sample datasets,
we align their energy outputs with those trained on highsample datasets by adding a shift scalar. These two strategies
ensure that the energy outputs of classifiers at different stages
remain consistent for in-distribution data, i.e., F (xi ; fθi ) ≈
F (xj ; fθj ), i = j . Consequently, utilizing Helmholtz energy
values during testing to select the most appropriate classifier
for handling data represents a fair and reliable approach.
Specifically, the confidence score is defined as the negative
value of the Helmholtz free energy. For a given sample x, the
classification confidence value of H (x , fθi ) can be defined as:



i
H (x , fi ) = −F x ; fθi = T log
e fθ (x ,y)/T − Δ(i ),
y∈Y i

(12)
where Δ(i ) represents the energy shift scalar of the i-th
classifier output. If the classifier is trained on low-sample data,
Δ(i ) assumes a negative value; if it is trained on high-sample
data, Δ(i ) = 0.
Then, the classifier with the lowest energy value is selected
as the output result classifier (Eq. (13)).
⎛
⎞

i
e fθ (x ,y)/T − Δ(i )⎠. (13)
i ∗ = arg max ⎝T log
i∈τ

y∈Y i

Finally, the output result of the selected classifier is taken
as the traffic classification category by Eq. (5). The classifier
selecting process is introduced in Algorithm 2 and presented
in the lower part of Figure 4.

YI et al.: AN EFFICIENT WEBSITE FINGERPRINTING FOR NEW WEBSITES EMERGING

V. E XPERIMENTAL E VALUATION
In this section, we conduct a series of experiments to comprehensively evaluate the performance of the proposed EIL
WF method. We first outline the experimental setup, including
dataset construction, evaluation metrics, model architecture,
and training details in Section V-A.
We then assess the incremental learning capabilities of EIL
WF by adapting several state-of-the-art incremental learning
algorithms to the website fingerprinting scenario and comparing their classification accuracy and forgetting rates with
those of EIL WF (Section V-B). Section V-C examines the
adaptability of EIL WF across different backbone networks
and compares its consistency and robustness with other highperforming WF methods under multi-model structures. In
Section V-D, we compare free energy based scoring and
Softmax based scoring to evaluate their effectiveness in
incremental identification tasks. We further examine realworld scenarios in Section V-E and Section V-F, focusing
on performance under imbalanced dataset and concept drift
dataset. Finally, Section V-G presents ablation studies to
analyze the contribution of each loss function to overall
incremental performance. In addition, the experimental environment of this work is based on a 4060 GPU with 12GB
memory and PyTorch 2.1.1.
A. Experimental Setup
1) Dataset: To comprehensively verify the performance of
EIL-WF, we conduct experiments on two classic public WF
datasets, namely the DF95 dataset and the AWF100 dataset.
DF95: This dataset originates from [6], where Sirinam et al.
collected 95 monitored websites using the TBB 7.X version.
These websites are selected from the top 100 most popular
sites listed by Alexa, with each website having 1000 traces.
The sequence length of each sample is 5000.
AWF100: This dataset is sourced from [14], collected by
Rimmer et al. using TBB V6.X. All websites are from the
top of Alexa. In this paper, we use AWF100, which includes
100 monitored websites with non-intersecting URLs, each with
2500 traces, and each trace has a sequence length of 5000.
Drift dataset: To study the effect of distributional drift over
time in the context of website fingerprinting, we introduce a
series of temporally-shifted datasets derived from the original
AWF100, which were also collected by Rimmer et al. These
datasets, denoted as AWF3d, AWF10d, AWF2W, AWF4W, and
AWF6W, correspond to traffic collected approximately 3 days,
10 days, 2 weeks, 4 weeks, and 6 weeks after the original
AWF100 collection period, respectively. Each class contains
100 samples, and each sample has a trace length of 5000.
Incremental data setting: In the initial phase of the incremental learning model, the number of categories comprises
approximately half of the total categories in the dataset, with
ten new website categories added in each subsequent incremental stage. In the DF95 dataset (comprising 95 categories),
the initial phase includes 45 categories; in the AWF100 dataset
(comprising 100 categories), the initial phase includes 50 website categories. The dataset is divided into training, validation,
and test sets in an 8:1:1 ratio. For example, for each website in

373

the DF95 dataset, which contains 1,000 samples, 800 samples
are allocated for training, while both the validation and test
sets comprise 100 samples per website.
2) Evaluation Metrics: Considering that the primary objective of website fingerprinting is to accurately identify websites
and avoid mis-classification, average accuracy (AAC) is designated as a crucial evaluation metric. The purpose of
incremental learning is to reduce the forgetting rate of old
categories while continuously incorporating new categories.
Final forgetting rate (FF) serves as a measure to assess the
incremental capability of EIL-WF, which quantifies the degree
of performance degradation of old tasks or categories after the
introduction of new tasks or categories. Given that the classification accuracy within the classifier relies on the performance
of the selected backbone network, the classification accuracy
of EIL-WF is principally influenced by the ability to classify
the samples accurately within the correct classifier. We employ
average recall (AR) to demonstrate the capability of EIL-WF
in selecting the appropriate classifier for test data. AAC , AR,
and FF can be computed as follows:
t
Ni · AC Ci
AAC = i=1
Ntotal
t
Ni · Recal li
AR = i=1
Ntotal
old
FF = AAC old
(14)
UB − AAC new ,
where ACCi and Recalli denote the accuracy and recall rate
of each classifier for in-distribution data, Ni represents the
sample size of the i-th classifier, and Ntotal indicates the total
sample size of all current websites. AAC old
UB is the upper
bound average accuracy of the old data (the accuracy of the
model trained with the complete old data), while AAC old
new
reflects the average accuracy of the old data following the
model update.
3) Parameter Setting: The temperature T is set to 0.4, and
the regularization coefficients for the energy constraining loss
λ = 0.25 and the parameter distancing loss γ = 0.08 are determined. EIL-WF uses DFnet as the default backbone network
structure for benchmark testing and maintains consistency with
its network hyperparameters.
B. Comparison With CIL Methods in WF
In this part, we compare the incremental learning capacity
of EIL-WF with existing CIL methods in the WF scenario.
To enhance clarity, we adapt and apply classic CIL frameworks iCarl [15], Co2L [33], L2P [35], EASE [16], APER [38]
and ESN [34] to WF and conduct a comparison. iCarl and
Co2L represent incremental learning methods that require the
retention of 50 samples per historical category for model
training. L2P, EASE, APER and ESN are incremental learning
methods that do not require caching old data.
iCarl [15]: learns new classes incrementally by jointly
learning representations and classifiers while maintaining a
small memory buffer.
Co2L [33]: employs contrastive learning and selfsupervised distillation to improve representation robustness
and transferability.

374

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

TABLE I
C OMPARATIVE A NALYSIS OF AVERAGE ACCURACY (↑) AND F INAL F ORGETTING (↓) B ETWEEN EIL-WF AND E XISTING I NCREMENTAL L EARNING
M ETHODS ON DF95 AND AWF100 DATASETS . B UFFER S IZE R EPRESENTS THE N UMBER OF S AMPLES C ACHED FOR E ACH O LD W EBSITE , T D ENOTES
THE L ATEST S TAGE N UMBER . A LL N UMBERS A RE %, AND W E D O N OT S HOW S TANDARD D EVIATIONS L ESS T HAN 0.5%

L2P [35]: L2Puses prompt-based tuning of pre-trained
models, storing prompts as reusable memory for future tasks.
EASE [16]: EASE builds a scalable subspace via
lightweight adapters on frozen pre-trained models, leveraging
intra-class similarity in a collaborative space to synthesize
classifiers for old classes without accessing past data.
APER [38]: APER balances generalization and adaptability
by efficiently fine-tuning pre-trained models and combining
their features with adapter outputs.
ESN [34]: ESN expands its classifier set dynamically and
aligns their outputs via energy-based self-normalization and
ensemble inference.
The comparison results are presented in Table I. To facilitate
a more effective comparison, this study introduces the concept
of an upper bound (UB) at each stage, representing the
accuracy of training the model with the complete dataset at
each stage. The results demonstrate that EIL-WF, which does
not require caching historical data on the same traffic feature
extraction network, achieves superior performance in most
cases.
Over the AWF100 dataset, the final AAC of EIL-WF
reaches 96.6%, which is only 2.7% lower than the UB.
Compared to the best method among those relying on data
replay, the AAC improves by 19.8%, and EIL-WF outperforms Co2L in AAC at all stages. In comparison to methods
that do not require caching, the final AAC of EIL-WF is 6.2%
higher than the best method, ESN. Although the performance
remains similar in the initial incremental stage and is slightly
lower than ESN at the second stage, as the number of stages
increases, the classification interference between stages in
ESN intensifies, leading to a rapid decline in its performance.
After the number of stages t exceeds 2, EIL-WF consistently
achieves the best results.

On the DF95 dataset, the final AAC of EIL-WF reaches
95.3%, which is 2.8% lower than the UB and 20.1% higher
than the best method among those relying on data replay in
incremental learning approaches. EIL-WF also outperforms
Co2L in AAC at all stages. Compared to methods that do
not require caching, the final AAC of EIL-WF is 6.9% higher
than the best method, ESN. Although it is slightly lower
than ESN at stage t = 1, EIL-WF consistently performs
better than ESN in subsequent incremental stages, and its
advantage becomes more pronounced as the number of stages
increases. Due to the isolation between classifiers at each
stage in EIL-WF, the interference between new and old data
remains minimal, resulting in a lower forgetting rate for old
data. Compared to other methods, EIL-WF achieves the best
or similar performance. On the AWF100 dataset, the final
forgetting rate of EIL-WF is 1.7%, which is 20% lower than
iCarl, 11.4% lower than Co2L, 16.4% lower than L2P, and
5.4% lower than ESN. On the DF95 dataset, the final forgetting
rate of EIL-WF is 2.1%, which is 5.7% lower than the best
method, ESN, and 20.4% lower than the average of the four
compared methods. This indicates that the method proposed
in this paper provides continuous learning capabilities for WF
models, meeting the needs of long-term dynamic updates to
the monitored set.
C. Comparison With Existing WF Methods Under CIL
Setting
The EIL-WF is a general incremental learning framework designed for website fingerprinting, aiming to equip
the majority of WF models with the capability for continuous learning. To assess the effectiveness of EIL-WF
in enhancing incremental learning performance for website

YI et al.: AN EFFICIENT WEBSITE FINGERPRINTING FOR NEW WEBSITES EMERGING

375

Fig. 6. Comparison of classification accuracy across different WF models using EIL-WF and finetune strategies over five incremental learning stages.The
metrics includes average accuracy over all classes (AAC_all), average accuracy over old classes learned in previous stages (AAC_old), and average accuracy
over newly introduced classes in the current stage (AAC_new).

fingerprinting tasks, we design a controlled comparative
experiment. Specifically, eight representative WF models are
selected as fixed backbone architectures: DF [6], TikTok [7],
VarCNN [8], RF [9], WF-Transformer [10], BAPM [28],
TMWF [11], and ARES [12]. Among these, BAPM, TMWF
and ARES are multi-tab WF methods. For consistency, we
configure all models with a single tab during experimentation.
We establish a baseline method for comparison: a standard
fine-tuning-based incremental learning strategy, in which the
backbone network remains frozen during training, and a
dynamically decaying learning rate is applied to alleviate
catastrophic forgetting. Furthermore, to highlight the efficiency
of EIL-WF, we also compare its computational and time costs
with those incurred by a full retraining strategy, where the
model is retrained from scratch on the entire accumulated
dataset at each incremental stage.
To evaluate the incremental learning performance of
each method, we adopt three metrics: average accuracy over all classes (AAC_all), average accuracy over
old classes (AAC_old), and average accuracy over new
classes (AAC_new). These metrics are computed for each
approach across five incremental stages, from t = 1 to
t = 5. All experiments are conducted on the DF95
dataset.
The experimental results, illustrated in Figure 6, provide
strong empirical evidence for the effectiveness of EILWF across diverse WF backbone models. The framework
consistently achieves high classification accuracy across all

evaluation metrics, demonstrating both robustness and adaptability in incremental learning scenarios. After completing five
incremental learning stages, EIL-WF maintains high overall
accuracy across all tested architectures: DF, TikTok, VarCNN,
RF, WF-Transformer, BAPM, TMWF, and ARES were 95.3%,
95.2%, 95.2%, 96.4%, 96.1%, 93.9%, 95.1%, and 95.8%,
respectively. This consistency underscores the framework’s
ability to mitigate the negative effects of distributional shifts
and class expansion.
In stark contrast, traditional fine-tuning approaches show
a marked decline in overall performance, particularly in
AAC_all, as the learning progresses through incremental
stages. At stage five, DF, TikTok, VarCNN, RF, WFTransformer, BAPM, TMWF, and ARES dropped to 35.7%,
32.4%, 36.6%, 81.2%, 43.3%, 21.6%, 84%, and 46.4%,
respectively—highlighting their vulnerability to catastrophic
forgetting. This sharp performance drop is primarily due
to the erosion of learned representations for earlier tasks,
which are not adequately preserved during subsequent updates.
Notably, while fine-tuned models may demonstrate reasonable
performance on newly introduced classes (reflected in initially
elevated AAC_new scores), they fail to retain recognition
capabilities for previously learned classes, as evidenced by
rapidly declining AAC_old scores. In contrast, EIL-WF successfully balances plasticity and stability, allowing models
to acquire new knowledge while maintaining competence on
earlier tasks. This capability is particularly critical for realworld deployment of WF systems, where continuous updates

376

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

TABLE II
T IME OVERHEAD OF WF M ODELS FOR M ODEL U PDATING W ITH AND
W ITHOUT EIL-WF F RAMEWORK , M EASURED IN S ECONDS ( S )

are necessary without compromising historical classification
integrity.
In the incremental learning phase, EIL-WF utilizes only
the data from the current stage to train the classifier, thereby
facilitating rapid model updates. This approach proves particularly advantageous for WF scenarios characterized by
limited storage and computational resources. Table II presents
a comparison of computational time costs between traditional
methods and EIL-WF during model updates. The results
demonstrate that the training time of EIL-WF significantly
reduces in comparison to traditional methods, with a decrease
of 2 ∼ 3 orders of magnitude. This advantage arises from the
necessity of traditional methods to employ the entire dataset
for training the model from scratch, which results in gradually
increasing time costs. In contrast, EIL-WF maintains stability
and reduces training time consumption throughout the process
by utilizing only the current data for training.
Furthermore, EIL-WF training eliminates the need for
caching historical data, significantly reducing the storage space
required for model training. As the number of incremental
stages increases, traditional methods demand the continuous
retention of an expanding volume of original website category
data, leading to a substantial rise in storage costs. For instance,
when starting with 45 website categories and adding 10 new
categories at each incremental stage, EIL-WF retains only the
data relevant to the current classifier’s training, which can
be deleted after training. This process ensures that, at any
given stage, the model stores data for up to 10 website categories, thereby maintaining low overall storage consumption.
In contrast, traditional methods must store all data, resulting
in escalating storage costs over time. The efficiency of EILWF in utilizing computational and storage resources provides
it with a distinct advantage in long-term tasks.
D. Comparison With Softmax-Based Classifier Selecting
This section evaluates the effectiveness of the proposed
free energy-based scoring mechanism as a confidence measure
for classifier selection during inference. As the number of
classifiers increases across incremental stages, this mechanism
helps route each test sample to the most suitable classifier,
thereby maximizing classification accuracy. It plays a critical
role in the EIL-WF framework by preventing catastrophic
forgetting and supporting continual learning. We compare

this approach with the conventional Softmax-based confidence
measure, which serves as the baseline. To visualize how
well each method performs in classifier selection, we conduct
experiments on the DF95 dataset and test at every incremental
stage from t = 1 to t = 5. Figure 7 presents confusion matrices
that illustrate classifier assignment performance. Diagonal elements represent correctly routed samples, while off-diagonal
elements indicate misrouted samples, revealing inter-classifier
interference.
The results clearly demonstrate that the free energy-based
scoring strategy significantly outperforms the conventional
Softmax-based approach in selecting the correct classifier
during incremental inference. Under the free energy strategy,
the confusion matrices exhibit strong diagonal dominance,
indicating accurate sample-to-classifier routing and minimal
interference between classifiers. In contrast, the Softmax
method leads to increased off-diagonal errors and substantial
cross-classifier confusion, which intensifies with each incremental stage. At stage t = 5, the Softmax-based approach
shows a notable decline in recall, with average per-classifier
recall dropping to 47.9%, 86.0%, 85.1%, 92.3%, 92.5%, and
88.1%, respectively.
By contrast, the free energy-based method consistently
maintains high recall, successfully directing the majority of
test samples to their appropriate classifiers. At the same stage
(t = 5), the average recall across classifiers remains robust
at 99.0%, 97.7%, 97.4%, 96.8%, and 96.1%. These findings
confirm that the proposed energy-based scoring mechanism
not only improves routing accuracy and overall classification performance but also effectively suppresses classifier
interference in dynamic, multi-stage incremental learning
scenarios.
E. Performance on Imbalanced Dataset
In this part, we evaluate the performance of EIL-WF
on imbalanced datasets. Since existing WF methods are
not designed to address class imbalance issues and fewshot methods typically exhibit high spatial complexity, we
employ the original DF model as the baseline for comparative
analysis with the EIL-WF method on imbalanced datasets.
Specifically, EIL-WF is categorized into two settings: one with
energy alignment (EA) and the other without, to illustrate the
applicability of EIL-WF in addressing imbalanced datasets and
to assess the effect of energy alignment. We randomly select 20
categories from the DF95 and AWF100 datasets as low-sample
website categories, which contain fewer samples N ∼ (2 , 20 ),
to simulate dataset imbalance. We use L-ACC to represent the
average accuracy of low-sample websites during testing.
The experimental results, as shown in Figure 8, demonstrate
the comparative outcomes under varying degrees of data
imbalance. It is observed that EIL-WF with energy alignment
outperforms the baseline method when the number of samples
for poorly performing websites is fewer than 20. In the case
of N = 2, the initial method’s recognition AAC for these
websites is 0, indicating that it is challenging to learn about
these websites due to model training bias. However, EILWF (with EA) achieves a recognition AAC of 78.2% on the

YI et al.: AN EFFICIENT WEBSITE FINGERPRINTING FOR NEW WEBSITES EMERGING

377

Fig. 7. Confusion matrices comparing classifier selection performance using free energy-based versus Softmax-based scoring mechanisms across incremental
stages (t = 1 to t = 5) on the DF95 dataset.

DF95 dataset and over 70% on the AWF100 dataset for these
websites. Notably, EIL-WF without EA also recognizes these
poorly performing websites to some extent.
When the number of low-sample website examples N = 20
increases, the model bias issue of traditional methods is
somewhat mitigated, with recognition AAC reaching approximately 71.7% on the DF95 dataset and 77.5% on the AWF100
dataset for these websites, which remains below the ideal level.
In contrast, EIL-WF (with EA) significantly improves recognition performance, with AAC reaching 92.4% on the DF95
dataset and 92.1% on the AWF100 dataset, demonstrating its
strong ability to recognize websites with low-sample samples
in the presence of data imbalance.
To improve the principled and practical determination of the
energy scalar Δ in automated or large-scale deployments, we
conducted an in-depth analysis of its calculation. The primary
objective is to ensure that the majority of traffic from lowsample websites can be correctly classified. As discussed in
Section IV-C, this requires that during inference, the energy
output of the target classifier remains consistently lower than
that of the non-target classifiers, with a sufficient margin
defined by the threshold . The choice of  therefore directly
determines the extent to which the target classifier’s energy
must be reduced. Specifically, we compute the average energy
outputs for low-sample website data across both the target
and non-target classifiers, introduce an additive scalar to align
these outputs, and then determine an appropriate  to maintain
the target classifier’s relative advantage.
To systematically analyze the impact of different  values
on classification performance, we explored a range of 
values within [−2, 0] and observed that when  lies within
the interval [−0.8, −0.4], the overall classification accuracy
remains relatively stable across various sample size settings.
As the absolute value of  increases (i.e., becomes more
negative), the classification accuracy for low-sample websites
steadily improves. However, if the energy adjustment is too

Fig. 8. Average accuracy performance on imbalanced data, with the X-axis
representing the sample numbers of 20 low-sample data site categories.
(a) shows the results on the DF95 dataset, and (b) shows the results on the
AWF100 dataset.

aggressive, it introduces excessive interference to other classifiers, resulting in a noticeable decline in overall system
accuracy. To adopt a conservative approach and minimize
potential negative impact on other stages, we ultimately set
 = −0.5 as the default configuration for this experiment.
F. Performance on Concept Drifted Dataset
This section evaluates the performance of EIL-WF in
handling concept drift in dynamic environments. Concept drift
refers to changes in data distributions over time that lead to
model performance degradation. Traditional models trained on
static datasets often fail to adapt to such changes. Common

378

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

Fig. 9. Impact of concept drift on WF classification accuracy over time. The model is initially trained on the AWF100 dataset and evaluated on multiple
temporally drifted datasets (AWF3d, AWF10d, AWF2w, AWF4w, and AWF6w).

Fig. 10. Comparison of classification accuracy between EIL-WF and finetuning methods on the top 15 severely drifted website categories, showing
both current task accuracy for updated categories and overall accuracy.

strategies for addressing this issue rely on full data recollection
and model retraining at regular intervals. These approaches are
rarely feasible in real-world deployment due to high demands
on storage, communication, and computation.
To evaluate the impact of concept drift on model
performance, we train an initial model based on DFnet using
the AWF100 dataset, and test it on several drifted versions
of the dataset: AWF3d, AWF10d, AWF2w, AWF4w, and
AWF6w. As shown in Figure 9, the model’s classification
accuracy is significantly affected by concept drift, dropping
from an initial 99.1% to 88.7% after six weeks. However, it
is worth noting that this performance degradation does not
occur uniformly across all classes. On the AWF6w dataset,
only 15 website classes exhibit classification accuracy below
90%, while the majority of classes maintain relatively stable
performance. This suggests that in practice, concept drift tends
to be non homogeneous and affects only a subset of high
dynamic websites within a given time window.
A more practical and cost effective solution involves periodically sampling small data subsets and selectively updating
classifiers for high drift categories. This approach preserves
system adaptability without requiring full model retraining.
EIL-WF performs well under this strategy. Its modular multi

classifier architecture allows each classifier to operate independently. Updating one does not interfere with the others, which
enables precise incremental learning. In contrast, fine tuning
improves recognition for selected categories but often causes
forgetting of stable ones. This problem is especially severe
under class imbalance, where accuracy for untrained classes
may degrade significantly and compromise system robustness.
We trained the DFnet model on AWF100 and then selected
the 15 most high drift categories from AWF6w. Each website
provided 80 training samples and 10 validation samples. Final
testing was conducted on the complete AWF6w dataset. In
the fine tuning experiments, we froze convolutional layers and
lowered the learning rate to limit gradient changes. In EIL-WF,
the selected categories were assigned to a separate classifier
that was trained independently while the remaining classifiers
remained unchanged.
Figure 10 presents the final results. Fine tuning raised the
AAC of selected categories to 99.1% but caused a drop in
overall performance. After 30 epochs of training, overall AAC
decreased to 87.8%. EIL-WF, on the other hand, improved
AAC for the 15 selected categories to 98.2% while maintaining
stable performance for the rest. Overall AAC reached 95.2%.
These results show that EIL-WF not only improves recognition
for high drift categories but also avoids disrupting stable ones.
G. Impact of Loss Function Configurations
To analyze the specific impact of the two loss functions
in classifier normalization training on the performance of the
enhanced learning method, we conduct ablation experiments.
These experiments evaluate the effect of each loss function
individually or in combination on the final performance of the
model.
As shown in Table III, when the model is trained solely
with cross-entropy loss, the overall performance remains
suboptimal, with AAC rates of 88.1% and 89.2% on the DF95
and AWF100 datasets, respectively. This is accompanied by
elevated forgetting rates, reaching 8.9% and 9.1%. The error in

YI et al.: AN EFFICIENT WEBSITE FINGERPRINTING FOR NEW WEBSITES EMERGING

TABLE III
I MPACT OF E ACH L OSS F UNCTION ON AAC AND AR,
A LL N UMBERS A RE %

selecting data for classifiers is also considerable, with average
recall rates of only 89.1% and 89.7% for each classifier. This
indicates that in the absence of additional loss functions, as
the number of learning stages increases, the model’s stages
become more susceptible to interference during classification,
leading to a more pronounced catastrophic forgetting problem.
In other words, the acquisition of new knowledge significantly
undermines the retention of prior knowledge.
Further analysis reveals that the introduction of the energy
constraining loss effectively alleviates this issue. Without this
loss function, the average recall rate for each classifier on
the two datasets is 92.2% and 92.6%, respectively, indicating
a significant decline compared to EIL-WF. This results in a
reduction in AAC rates by 3.7% and 4.5%, respectively. This
demonstrates the important role of the energy constraining loss
in reducing interference between classifiers at different stages
and maintaining long-term memory.
Additionally, the results show that the parameter distance
loss contributes to improving the model’s incremental learning
ability. By encouraging the model parameters to maintain a
distance from the parameters of specific classifiers, it reduces
the incorrect responses of non-target classifiers to new data.
The model without this loss has final AAC rates of 93.3% and
94.2%, which are 2.3% and 2.4% lower than those obtained
with the complete loss setting, indicating its positive role in
optimizing model generalization and preventing overfitting.
H. Discussion
This study proposes an incremental learning approach for
website fingerprinting attacks based on a multi-classifier architecture. The method enables traditional WF attack models to
learn continuously, overcoming their reliance on the assumption of static website categories. It provides structural support
for adapting WF models to dynamic network environments
and shows strong scalability and flexibility, particularly when
facing frequent category changes or rapid content updates.
Within the incremental learning framework, we introduce
mechanisms such as classifier-normalized training to align
the confidence output distributions of newly added classifiers across stages. This mitigates unfair inference caused
by distribution shifts between stages and reduces bias when
aggregating outputs from multiple classifiers. The design
improves overall model stability and generalization. However,
although each newly added classifier is designed to be
lightweight and accounts for approximately 1.6% of the
parameters of the backbone network, the model still faces
scalability challenges in practical deployment. As incremental

379

stages accumulate, the number of classifiers may grow to
dozens or even hundreds, resulting in a significant increase
in the total number of parameters and placing a considerable
burden on resource-constrained edge devices. To address this,
future work may explore model compression strategies such
as model distillation, which merges stage-wise classifiers into
a unified model, or structured pruning to eliminate redundant
parameters. These techniques can help control model size
without compromising performance, enhancing deployability.
We also introduce an energy alignment (EA) strategy
to calibrate output energies across classifiers trained with
imbalanced data. This effectively reduces performance discrepancies caused by varying training sample sizes across
stages. Experimental results confirm that EA significantly
improves performance in few-shot stages and offers a clear
and efficient solution to data imbalance in incremental WF
learning. However, the current EA approach focuses on interstage imbalance and does not fully account for intra-stage
distribution disparities. In reality, variations in sample quantity
within a single stage may also introduce training bias and
affect fine-grained classification. Future research could incorporate sample-level energy scaling or integrate established
techniques such as focal loss or class reweighting to better
address intra-stage imbalance.
From an architectural perspective, the proposed multiclassifier design supports localized updates, allowing targeted
optimization for specific domains without affecting other
components. This capability offers a practical solution for
addressing concept drift in WF attacks. When website structures evolve over time, lightweight classifiers can be trained
and deployed for affected sites, preserving adaptability and
monitoring accuracy. Compared to full retraining, localized
updates require fewer resources and offer faster responsiveness. A promising future direction is the development of
feature drift detection mechanisms. For instance, designing
lightweight drift-aware models that detect subtle structural or
behavioral changes could guide classifier updates and support
more precise and dynamic incremental learning.
VI. C ONCLUSION
This paper presents an incremental learning approach named
EIL-WF, enabling website fingerprinting models to evolve
continuously as new websites emerge. By training lightweight
classifiers to learn new knowledge and incorporating classifiernormalized training with a free energy-based selection
mechanism, the framework effectively integrates multi-stage
classifiers while preventing forgetting of previously learned
information. In addition, parameter-isolated training alleviates
bias caused by data imbalance and supports localized adaptation under concept drift. Experimental results demonstrate that
EIL-WF achieves strong accuracy, adaptability, and efficiency
in dynamic environments, making it well-suited for deployment in real-world continual learning scenarios.
R EFERENCES
[1] C. Wang, J. Luo, Z. Ling, L. Luo, and X. Fu, “A comprehensive and
long-term evaluation of Tor V3 onion services,” in Proc. IEEE Conf.
Comput. Commun., 2023, pp. 1–10.

380

IEEE TRANSACTIONS ON NETWORK AND SERVICE MANAGEMENT, VOLUME 23, 2026

[2] W. Feng, X. Luo, T. Li, and C. Yang, “IP-Pealing: A robust network flow
watermarking method based on IP packet sequence,” Chin. J. Electron.,
vol. 33, no. 3, pp. 694–707, 2024.
[3] D. Herrmann, R. Wendolsky, and H. Federrath, “Website fingerprinting:
attacking popular privacy enhancing technologies with the multinomial Na´’ıve-bayes classifier,” in Proc. ACM Workshop Cloud Comput.
Security, 2009, pp. 31–42.
[4] X. Yuan, T. Li, L. Li, R. Li, Z. Wang, and X. Luo, “HSWF: Enhancing
Website fingerprinting attacks on Tor to address real world distribution
mismatch,” Comput. Netw., vol. 241, Mar. 2024, Art. no. 110217.
[5] B. Gao, W. Liu, G. Liu, and F. Nie, “Resource knowledge-driven
heterogeneous graph learning for Website fingerprinting,” IEEE Trans.
Cogn. Commun. Netw., vol. 10, no. 3, pp. 968–981, Jun. 2024.
[6] P. Sirinam, M. Imani, M. Juarez, and M. Wright, “Deep fingerprinting: Undermining Website fingerprinting defenses with deep learning,”
in Proc. ACM SIGSAC Conf. Comput. Commun. Security, 2018,
pp. 1928–1943.
[7] M. S. Rahman, P. Sirinam, N. Mathews, K. G. Gangadhara, and
M. Wright, “Tik-Tok: The utility of packet timing in Website fingerprinting attacks,” in Proc. Privacy Enhanc. Technol., 2020, pp. 5–24.
[8] S. Bhat, D. Lu, A. Kwon, and S. Devadas, “VAR-CNN: A data-efficient
Website fingerprinting attack based on deep learning,” in Proc. Privacy
Enhanc. Technol., 2019, pp. 292–310.
[9] M. Shen, K. Ji, Z. Gao, Q. Li, L. Zhu, and K. Xu, “Subverting Website
fingerprinting defenses with robust traffic representation,” in Proc. 32nd
USENIX Security Symp. (USENIX Security), 2023, pp. 607–624.
[10] Q. Zhou, L. Wang, H. Zhu, T. Lu, and V. S. Sheng, “WF-transformer:
Learning temporal features for accurate anonymous traffic identification
by using transformer networks,” IEEE Trans. Inf. Forensics Security,
vol. 19, pp. 30–43, 2024.
[11] Z. Jin, T. Lu, S. Luo, and J. Shang, “Transformer-based model for multitab Website fingerprinting attack,” in Proc. ACM SIGSAC Conf. Comput.
Commun. Security, 2023, pp. 1050–1064.
[12] X. Deng et al., “Robust multi-tab Website fingerprinting attacks in the
wild,” in Proc. IEEE Symp. Security Privacy (SP), 2023, pp. 1005–1022.
[13] A. Bahramali, A. Bozorgi, and A. Houmansadr, “Realistic Website
fingerprinting by augmenting network traces,” in Proc. ACM SIGSAC
Conf. Comput. Commun. Security, 2023, pp. 1035–1049.
[14] V. Rimmer, D. Preuveneers, M. Juarez, T. Van Goethem, and W. Joosen,
“Automated Website fingerprinting through deep learning,” in Proc. 25th
Annu. Netw. Distrib. Syst. Security Symp., 2018, pp. 1–15.
[15] S.-A. Rebuffi, A. Kolesnikov, G. Sperl, and C. H. Lampert, “ICaRL:
Incremental classifier and representation learning,” in Proc. IEEE Conf.
Comput. Vis. Pattern Recognit., 2017, pp. 2001–2010.
[16] D.-W. Zhou, H.-L. Sun, H.-J. Ye, and D.-C. Zhan, “Expandable
subspace ensemble for pre-trained model-based class-incremental learning,” in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2024,
pp. 23554–23564.
[17] G. Bovenzi et al., “Benchmarking class incremental learning in deep
learning traffic classification,” IEEE Trans. Netw. Service Manag.,
vol. 21, no. 1, pp. 51–69, Feb. 2024.
[18] J. Dai, X. Xu, H. Gao, X. Wang, and F. Xiao, “Shape: A simultaneous
header and payload encoding model for encrypted traffic classification,”
IEEE Trans. Netw. Service Manag., vol. 20, no. 2, pp. 1993–2012, Jun.
2023.
[19] X. Cai, X. C. Zhang, B. Joshi, and R. Johnson, “Touching from a
distance: Website fingerprinting attacks and defenses,” in Proc. ACM
Conf. Comput. Commun. Security, 2012, pp. 605–616.
[20] T. Wang and I. Goldberg, “Improved Website fingerprinting on
Tor,” in Proc. 12th ACM Workshop Privacy Electron. Society, 2013,
pp. 201–212.
[21] A. Panchenko et al., “Website fingerprinting at Internet scale,” in Proc.
23rd Internet Society (ISOC) Netw. Distrib. Syst. Security Symp. (NDSS),
2016, pp. 1–15.
[22] J. Hayes and G. Danezis, “k-fingerprinting: A robust scalable Website
fingerprinting technique,” in Proc. 25th USENIX Security Symp., 2016,
pp. 1187–1203.
[23] Z. Chen, G. Cheng, Z. Wei, D. Niu, and N. Fu, “Classify traffic
rather than flow: Versatile multi-flow encrypted traffic classification with
flow clustering,” IEEE Trans. Netw. Service Manag., vol. 21, no. 2,
pp. 1446–1466, Apr. 2024.
[24] X. Deng, Q. Li, and K. Xu, “Robust and reliable early-stage Website
fingerprinting attacks via spatial-temporal distribution analysis,” in Proc.
ACM SIGSAC Conf. Comput. Commun. Security, 2024, pp. 1997–2011.

[25] W. Cui, T. Chen, C. Fields, J. Chen, A. Sierra, and E. Chan-Tin,
“Revisiting assumptions for Website fingerprinting attacks,” in Proc.
Asia Conf. Comput. Commun. Security, 2019, pp. 328–339.
[26] X. Gu, M. Yang, and J. Luo, “A novel Website fingerprinting attack
against multi-tab browsing behavior,” in Proc. 19th Int. Conf. Comput.
Supported Cooperative Work Design, CSCWD, 2015, pp. 234–239.
[27] G. Cherubin, R. Jansen, and C. Troncoso, “Online Website fingerprinting: Evaluating Website fingerprinting attacks on Tor in the real world,”
in Proc. 31st USENIX Security Symp., 2022, pp. 753–770.
[28] Z. Guan, G. Xiong, G. Gou, Z. Li, M. Cui, and C. Liu, “BAPM-block
attention profiling model for multi-tab Website fingerprinting attacks on
Tor,” in Proc. Annu. Comput. Security Appl. Conf., 2021, pp. 248–259.
[29] P. Sirinam, N. Mathews, M. S. Rahman, and M. Wright, “Triplet
fingerprinting: More practical and portable Website fingerprinting with
N-shot learning,” in Proc. ACM SIGSAC Conf. Comput. Commun.
Security, 2019, pp. 1131–1148.
[30] Y. Xie et al., “Contrastive fingerprinting: A novel Website fingerprinting attack over few-shot traces,” in Proc. ACM Web Conf., 2024,
pp. 1203–1214.
[31] X. Li et al., “Let model keep evolving: Incremental learning for
encrypted traffic classification,” Comput. Security, vol. 137, Feb. 2024,
Art. no. 103624.
[32] C. Zhang, N. Song, G. Lin, Y. Zheng, P. Pan, and Y. Xu,
“Few-shot incremental learning with continually evolved classifiers,”
in Proc. IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2021,
pp. 12455–12464.
[33] H. Cha, J. Lee, and J. Shin, “CO2L: Contrastive continual learning,” in
Proc. IEEE/CVF Int. Conf. Comput. Vis., 2021, pp. 9516–9525.
[34] Y. Wang, Z. Ma, Z. Huang, Y. Wang, Z. Su, and X. Hong, “Isolation
and impartial aggregation: A paradigm of incremental learning without
interference,” in Proc. AAAI Conf. Artif. Intell., vol. 37, no. 8, 2023,
pp. 10209–10217.
[35] Z. Wang et al., “Learning to prompt for continual learning,” in Proc.
IEEE/CVF Conf. Comput. Vis. Pattern Recognit., 2022, pp. 139–149.
[36] J. Kirkpatrick et al., “Overcoming catastrophic forgetting in neural
networks,” Proc. Nat. Acad. Sci., vol. 114, no. 13, pp. 3521–3526, 2017.
[37] S. Yan, J. Xie, and X. He, “DER: Dynamically expandable representation
for class incremental learning,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit., 2021, pp. 3014–3023.
[38] D.-W. Zhou, Z.-W. Cai, H.-J. Ye, D.-C. Zhan, and Z. Liu, “Revisiting
class-incremental learning with pre-trained models: Generalizability and
adaptivity are all you need,” Int. J. Comput. Vis., vol. 133, no. 3,
pp. 1012–1032, 2025.
[39] W. Liu, X. Wang, J. Owens, and Y. Li, “Energy-based out-of-distribution
detection,” in Proc. Adv. Neural Inf. Process. Syst., vol. 33, 2020,
pp. 21464–21475.
[40] Y. LeCun, S. Chopra, R. Hadsell, M. Ranzato, and F. J. Huang, “A
tutorial on energy-based learning,” in Predicting Structured Data, vol. 1.
Cambridge, MA, USA: MIT Press, 2006, pp. 1–59.

Zhengge Yi received the B.S. and M.S. degrees
in information security from the Engineering
University of PAP, Xi’an, China, in 2020 and
2022, respectively. He is currently pursuing the
doctorate degree with the Henan Key Laboratory
of Cyberspace Situation Awareness, Zhengzhou,
Henan, China. His current research interests include
anonymous network security and anonymous communications analysis.

Tengyao Li received the B.S. and M.S. degrees
in computer science and technology and the Ph.D.
degree in cyberspace security from Air Force
Engineering University, Xi’an, Shaanxi, China in
2014, 2016, and 2020, respectively. He is currently a Lecturer with the Henan Key Laboratory
of Cyberspace Situation Awareness, Zhengzhou,
Henan, China. His current research has focused on
active defense against uncertain attacks in large scale
network systems.

YI et al.: AN EFFICIENT WEBSITE FINGERPRINTING FOR NEW WEBSITES EMERGING

381

Meng Zhang is currently pursuing the Ph.D. degree
with the State Key Laboratory of Mathematical
Engineering and Advanced Computing. Her main
research interests include network security, data
mining, and social network analysis.

Shaoyong Du received the B.E. degree in software engineering from Zhengzhou University, in
2012, and the Ph.D. degree in computer science
and technology from Nanjing University, in 2019.
He is currently an Associate Professor with the
Henan Key Laboratory of Cyberspace Situation
Awareness, Zhengzhou, Henan, China. His current
research focuses on security and privacy in mobile
computing.

Xiaoyun Yuan received the B.S. and M.S. degrees
in computer science and technology from the
University of Science and Technology, Nanjing,
China, in 2008 and 2015, respectively. She is currently pursuing the doctorate degree with the Henan
Key Laboratory of Cyberspace Situation Awareness,
Zhengzhou, Henan, China. Her current research has
focused on privacy enhancing technologies such as
anonymous communications, and network security.

Xiangyang Luo received the B.S., M.S., and
Ph.D. degrees from the Henan Key Laboratory
of Cyberspace Situation Awareness, Zhengzhou,
Henan, China, in 2001, 2004, and 2010, respectively,
where he is currently a Professor. He is the author
or co-author of more than 150 refereed international
journal and conference manuscripts. His research
interests are image steganography and steganalysis
technique.
PAPER_TEXT
