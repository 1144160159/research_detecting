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
# [838] Unsupervised Cross-Domain Attack Traffic Classifier for Intelligent Connected Vehicle
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
编号：838
题名：Unsupervised Cross-Domain Attack Traffic Classifier for Intelligent Connected Vehicle
年份：2025
DOI：10.1109/tie.2025.3600524
来源：IEEE Transactions on Industrial Electronics
PDF：paper/10.1109_TIE.2025.3600524.pdf
已有粗分类：IoT、车联网、工业互联网与边缘安全
二级关联：恶意流量、暗网与攻击检测
相关性：中相关，分数 8
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\838.txt
- 原始字符数：61511
- 本次发送字符数：61511
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
IEEE TRANSACTIONS ON INDUSTRIAL ELECTRONICS, VOL. 73, NO. 2, FEBRUARY 2026

3025

Unsupervised Cross-Domain Attack Traffic
Classifier for Intelligent Connected Vehicle
Yongping He , Yuanqing Xia , Fellow, IEEE, Tijin Yan , Yufeng Zhan , Jiaru Song , and
Zihang Feng

Abstract—The heterogeneous communication ecosystem in intelligent connected vehicles (ICVs) has significantly broadened attack surfaces, making accurate attack traffic classification crucial for the security of vehicular networks. Existing deep learning (DL)-based classification methods face challenges such as reliance on labeled data and susceptibility to cross-domain data distribution discrepancies. To mitigate these challenges, a
cross-domain attack traffic classifier named domain adaptation noisy label (DANL) is proposed in this article. DANL
integrates uncertainty-aware sample selection and graph
spectral alignment into unsupervised domain adaptation
(UDA) frameworks to bridge domain gaps. Furthermore, a
dual correction framework integrating noisy label learning
(LNL) with pseudolabel aggregation is developed to further
correct misclassifications caused by erroneous alignment.
Extensive experiments on public datasets demonstrate
DANL’s superiority, achieving an improvement of classification accuracy up to 5.8% over baselines. Further validation
in real-world tests on self-constructed ICV testbed with
simulated attacks confirming its effectiveness.
Index Terms—Attack traffic classification, cyber-physical
system, deep learning (DL), intelligent connected vehicle
(ICV), unsupervised learning.

I. INTRODUCTION

I

NTELLIGENT connected vehicles (ICVs) are rapidly transforming the future of transportation by integrating advanced sensors, controllers, and communication technologies.
Although this interconnected ecosystem improves safety and
efficiency, it also introduces substantial cybersecurity risks. [1].
The multilayered and heterogeneous communication architecture of ICVs, including in-vehicle networks [such as controller

Received 26 May 2025; revised 25 July 2025; accepted 9 August 2025.
Date of publication 10 October 2025; date of current version 23 January
2026. This work was supported by Beijing Natural Science Foundation
Haidian Original Innovation Joint Fund Project under Grant L252035.
(Corresponding author: Yuanqing Xia.)
Yongping He, Tijin Yan, Yufeng Zhan, and Zihang Feng are with
the School of Automation, Beijing Institute of Technology, Beijing
100081, China (e-mail: 3120215481@bit.edu.cn; yantijin@bit.edu.cn;
yu-feng.zhan@bit.edu.cn; 3120185474@bit.edu.cn).
Yuanqing Xia is with Zhongyuan University of Technology,
Zhengzhou 450007, China, and also with the School of Automation,
Beijing Institute of Technology, Beijing 100081, China (e-mail:
xia_yuanqing@bit.edu.cn).
Jiaru Song is with Jilin University, Changchun 130012, China
(e-mail: songjr22@mails.jlu.edu.cn).
Digital Object Identifier 10.1109/TIE.2025.3600524

area network (CAN) and FlexRay], vehicle-to-everything
(V2X) communication (such as DSRC and C-V2X), and cloud
connectivity via transmission control protocol/internet protocol
(TCP/IP), which creates a broad and diverse attack surface that
is vulnerable to both conventional network attacks and cyberphysical threats [2].
Attack traffic classification technology is a pivotal tool in
the network security of industrial control systems (ICS), which
holds significant strategic value when applied to ICVs. As invehicle networks have evolved from transmitting simple control
messages to encompassing sensor data and external communication signals, the dimensionality and complexity of data
have significantly increased. Traditional attack classification
models for single regions have struggled to meet the security requirements of complex environments. Unsupervised clusteringbased methods struggle to achieve accurate classification when
handling such data, as they are prone to getting trapped in local
optima and sensitive to noise [3]. On the other hand, supervised
deep learning (DL)-based methods have demonstrated promising classification performance in many classification tasks [4],
they also face practical limitations in real-world connected vehicle environments. This is mainly due to the significant time
and labor costs associated with constructing labeled datasets.
Additionally, the dynamic nature of driving environments, such
as variations in speed, road conditions, and weather, causes
shifts in sensor data distributions, which reduces the effectiveness of static attack classification models. Furthermore, overthe-air (OTA) updates in ICVs often modify ECU software
and may alter communication patterns, these changes highlight
the imperative for adaptive learning frameworks capable of
generalizing across diverse deployment scenarios.
Existing domain adaptation methods predominantly focus on
aligning the marginal distributions of features across source and
target domains, employing techniques such as adversarial adaptation or discrepancy minimization [5], [6], [7]. While effective
in certain scenarios, these approaches often overlook the critical importance of sample-level uncertainty. This is particularly
crucial in complex vehicle environments where data quality and
reliability vary significantly. To mitigate these challenges, we
propose domain adaptation noisy label (DANL), a cross-domain
attack traffic classifier for ICVs based on unsupervised domain
adaptation (UDA). DANL aims to achieve strong performance
in attack traffic classification by integrating learning from noisy
labels (LNL), all without requiring pretrained models from

1557-9948 © 2025 IEEE. All rights reserved, including rights for text and data mining, and training of artificial intelligence and similar technologies.
Personal use is permitted, but republication/redistribution requires IEEE permission. See https://www.ieee.org/publications/rights/index.html
for more information.

3026

IEEE TRANSACTIONS ON INDUSTRIAL ELECTRONICS, VOL. 73, NO. 2, FEBRUARY 2026

other environments. This approach enhances adaptability across
different network environments while maintaining robust classification accuracy. DANL constructs a graph based on feature
similarities and aligns its spectral properties across domains
using a graph spectral alignment loss. This facilitates a more
nuanced and discriminative alignment that captures both local
and global data structures, providing a more effective and flexible way to achieve domain invariance in the heterogeneous and
dynamic settings characteristic of ICV environments. Furthermore, by integrating an uncertainty-aware selection mechanism
that estimates the confidence of pseudolabels during adaptation,
DANL can reduce the negative impact of noisy labels and enhance the overall robustness of the learning process. To mitigate
inconsistencies in pseudolabels generated by different models,
we frame the issue as a learning from noisy labels (LNL) problem and apply a decoupling method to reduce model discrepancies and refine the pseudolabels. Additionally, we design an
aggregation mechanism to unify these pseudolabels. Through
this iterative process, the pseudolabels are consolidated into
hard labels and used for the next round of training. Repeating
this process over several iterations leads to promising improvements in performance. The main contributions of this work are
as follows.
1) A cross-domain attack traffic classifier DANL is introduced in this article, which enables attack traffic classification in ICVs without requiring labeled data from
the specific target vehicle or environment. By integrating
uncertainty-aware sample selection and alignment loss
into existing UDA frameworks, DANL bridges the domain gap caused by variations in vehicle models, sensor
configurations, and driving conditions, while maintaining
resilience against heterogeneous data distributions common in ICV deployments.
2) To mitigate the inherent noise in pseudolabels caused by
alignment, a dual correction framework integrating noiseresistant LNL mechanism and iterative pseudolabel refinement strategy is further introduced.
3) The effectiveness of DANL is evaluated through comprehensive experiments on benchmark datasets and a
self-constructed ICV testbed. It achieves up to 5.8% improvement in classification accuracy compared with baselines on public datasets, while simulated attack scenario
testing on the ICV testbed further confirms its robustness
and practical viability for securing real-world intelligent
transportation systems.
The structure of the remaining sections of this article is
arranged as follows. In Section II, we detail some of the most
related works. In Section III, we provide a detailed description
of the main methods. In Sections IV and V, we demonstrate the
results of the proposed framework by experiments. Our work
is concluded in the final Section VI.
II. RELATED WORK
In this section, we give some reviews on classical works in
attack traffic classification and detection, deep domain adaptation, and LNL.

A. DL-Based Attack Traffic Classification and
Detection Method
DL plays a crucial role in protecting connected devices such
as the internet of vehicles (IoV) and vehicular ad hoc networks
(VANETs) [8], [9]. By harnessing labeled data, supervised DLbased methods exhibit remarkable efficacy, surpassing conventional methods. For example, Desta et al. [10] proposed
an intrusion detection system for in-vehicle networks, which
utilizes recurrence plots to generate images from in-vehicle
network data and classifies by a convolutional neural network
model. On the other hand, Seo et al. [11] proposed a generative
adversarial network (GAN)-based unsupervised vehicle network intrusion detection model GIDS, which detects unknown
attacks by learning normal data. As unsupervised methods often
rely on threshold selection, leading to high false positive rates
and limited to binary classification. To address this problem,
Xu et al. [12] utilized a few-shot meta-learning framework to
extract valuable information from a limited set of anomalous
data for intrusion detection. In this article, we employ domain
adaptation to extract effective information from attack traffic in
other domains to assist in unsupervised attack traffic classification on the target domain. Compared with existing methods, our
approach refrains from utilizing any labels from the target domain. Instead, it adeptly harnesses information from the source
domain to achieve fine-grained classification of network traffic.
B. Deep Domain Adaptation
Deep domain adaptation offers a feasible solution by endeavoring to map data from disparate source and target domains
with distinct distributions into a shared feature space. The primary objective is to minimize the distances of data distributions
within this shared space. There are a few works concentrating
on attack traffic classification and anomaly detection. Hu et al.
[13] combined DSAN [14] with attention mechanism to identify
malware variant traffic at an IoT edge gateway, but data used
in the source and target domains are sampled from a same
dataset. Wu et al. [15] proposed a multisource heterogeneous
semisupervised domain adaptation method called joint semantic
transfer network (JSTN) to achieve a more effective intrusion
knowledge transfer. They further proposed a geometric graph
alignment approach with a pseudolabel election mechanism
to refine the pseudolabel of domain adaptation for intrusion
detection [16]. Building models for detection and classification without any prior knowledge of target domain is first a
significant challenge. In this article, we also ensemble some
domain adaptation methods together to extract diverse valuable
information from attack traffic in source domain to aid in classification on the target domain. Besides, we discover that when
the attack traffic patterns in different domains vary significantly,
relying only on domain adaptation will lead to suboptimal results. Consequently, uncertainty assessment and pseudolabels
refinement are introduced to further rectify these results.
III. METHOD
In this section, the designed method for cross-domain attack
traffic classification in ICVs is described in detail. We aim to

HE et al.: UNSUPERVISED CROSS-DOMAIN ATTACK TRAFFIC CLASSIFIER

Fig. 1. Overview. (a) Workflow of DANL. Initially, different domain
adaptation methods are employed to train models, which subsequently
generate pseudolabels for the target data. In the subsequent phase, the
decoupling method is utilized to retrain models, refining the pseudolabels
of target data. Further, the pseudolabels of target data obtained by each
well-trained model are aggregated in the last phase. These aggregated
pseudolabeled target data are incorporated into the source data as prior
information for training in next round. (b) Backbone of DANL. It takes data
xi as input and outs the extracted feature Zi and the probability logit pi ,
which are normalized via softmax.

distill knowledge from the source domain data, where “domain”
refers to different vehicles or heterogeneous communication
networks in the internet of vehicles (IoV), making it applicable
for identifying target domain data. The primary workflow of
our designed DANL, as illustrated in Fig. 1(a), comprises three
main components: domain adaptation, pseudolabel refinement,
and pseudolabel aggregation. Uncertainty assessment and pseudolabel refinement are also introduced to refine pseudolabels in
domain adaptation training. Furthermore, a training loss function is utilized to alleviate the alignment and class-imbalance
issues. Following sections will provide detailed descriptions of
each component. The backbone of the DANL can be found in
Fig. 1(b).
A. UDA With Uncertainty
In the cross-domain scenario, the correlation knowledge of
attack traffic is expected to be transferred from source domain to
target domain, for effectively capturing the temporal dynamics
and spatial structural characteristics of attack traffic. To improve
computational efficiency and support parallel training, a random
partitioning strategy is adopted to divide the source domain
into multiple independent subdomains. Each subdomain forms
a domain pair with the target domain, and UDA learning is carried out separately through parallel training. This multiperspective learning mechanism can not only accelerate the training
process through a distributed computing architecture but also
mine cross-domain relationships from multiple perspectives by
aligning the feature distributions of different subdomains, thus
enabling a more comprehensive understanding of the characteristics of the target domain.
However, in the initial training stage, due to the significant
differences between the source domain and the target domain,

3027

the training process of GAN-based models is often extremely
unstable. The alignment loss Lalign in DSAN is based on the
proposed local maximum mean discrepancy (LMMD) criterion,
which can effectively measure the difference in kernel mean
embeddings between relevant subdomains of the source domain
and the target domain. Therefore, a natural improvement idea
is to integrate a similar metric criterion into DANN to help the
model achieve stable training. Given that attack traffic contains
rich temporal information and spatial structural information, we
model it as a graph structure. By constructing a self-correlation
graph, we can model the relationships between different traffic
samples within the domain and capture the underlying data
distribution characteristics.
Specifically, the backbone network f extracts features fs and
ft from source and target domain data, respectively. An undirected weighted graph Gs = (Vs , Es ) is constructed where each
vertex vi ∈ Vs corresponds to a feature vector fsi . Edge weights
ei,j ∈ Es are determined by a distance metric δ(fsi , fsj ), with
δ(·) being a predefined metric function. The adjacency matrix
of Gs is denoted as As . By modeling source and target domains
as graphs Gs1 , Gs2 , . . . , Gsk and Gt , the cross-domain alignment problem is transformed into a graph matching task [17].
Given a finite graph G = (V, E), the graph Laplacian Δ acting
on vertex function φ : V → R and edge
 weighting function
γ : E → R is defined as (Δγ φ) (v) = w:d(w,v)=1 γwv [φ(v) −
φ(w)], where d(w, v) is the graph distance and γwv is the edge
weight. Then for two simple nonisomorphic graphs Gs and
Gt with Laplacian spectra Λs = {λsi }ni=1 (λs1 ≥ λs2 ≥ · · · ≥ λsn )
and Λt = {λti }ni=1 (λt1 ≥ λt2 ≥ · · · ≥ λtn ), the spectral distance
is σ(Gs , Gt ) = Λs − Λt d , d ≥ 1, where d denotes the order
of the norm. The Laplacian matrices Ls and Lt and their eigenvalues Λs and Λt can be computed by the adjacency matrices
As and At , and the graph spectral alignment loss is Lgsa =
Λs − Λt d , which measures the spectral difference between
domain graphs. Then for DANN, its domain classifier is D(·),
f represents its feature extractor, the alignment loss is
Lalign = Ladv + Lgsa
= Exs ∼D̃s log[D(f (xsi ))] + Ext ∼D̃t log[1 − D(f (xti ))]
i

i

+ Λs − Λt d

(1)

where D̃s and D̃t denote the induced feature distributions of
Ds and Dt respectively, and Lce (·, ·) is the cross-entropy loss
function.
Furthermore, in cross-domain multiclass classification tasks,
DL-based models employing cross-entropy loss are inherently
prone to class bias. This bias occurs because simpler classes are
learned more readily and converge faster than complex classes,
even when the labels are accurate, ultimately resulting in class
imbalance problems. Consequently, the following classification
loss function is incorporated into our design
Lcls = −
+

K


q(k|x) log p(k|x) −

k=1
m


λ
fi − cyi 22
2 i=1

K


p(k|x) log q(k|x)

k=1

(2)

3028

IEEE TRANSACTIONS ON INDUSTRIAL ELECTRONICS, VOL. 73, NO. 2, FEBRUARY 2026

where fi represents the extracted features, cyi refers to the
center of the yi th class associated with deep features, which can
be update during training. The parameter λ balances these two
components. This regularization term helps limit the distance
between outliers and class centroids, which not only accelerates convergence and slightly improves performance but also
distinguishes clean samples from mislabeled ones.
Furthermore, we can easily get the loss in the phase of domain adaptation as
LDA = Lcls + Lalign .

(3)

Furthermore, existing UDA methods generate pseudolabels
for the target domain. However, pseudolabel errors tend to
accumulate during iterations. To mitigate noise in early iterations and avoid error propagation, we introduce an entropybased uncertainty measure during training. This augmentation
strategy enhances alignment by alleviating error accumulation in pseudolabels. The uncertainty Hi of each sample is
calculated as

pij log(pij )
(4)
Hi = −
j

where pij denotes the probability of sample i belonging to class
j as predicted by the final classifier layer. The uncertaintysorting mechanism is introduced to progressively remove data
with higher uncertainty.
B. Pseudolabels Refinement by Learning
From Noisy Labels
Despite enhancing pseudolabels through ensemble methods,
well-trained models face challenges aligning the source and
target domain distributions due to these disparities. As a result,
the pseudolabels retain numerous inaccuracies. To tackle this,
we employ LNL methods to transform the task of aligning
data distributions into robust learning from noisy labels. It’s
worth noting that the noisy labels within the pseudolabel dataset
of the target domain, acquired through the proposed ensemble
domain adaptation method, represent a prevalent type of realworld label noise. In our studying scenario, this noise stems
from the diverse knowledge acquired by each model from the
source domain and the inherent disparities found within the
target domain data.
After obtaining abundant data with pseudolabels by domain
adaptation, a natural idea is to filter out certain data points
that might be irrelevant or contaminated. We use a simple but
effective decoupling method introduced in Malach et al. [18] to
train models by their disagreement. We found that this decoupling method could stably improve domain adaptation results,
although it gradually tends to converge. When trained on noisy
labels, DL-based model first fits data with clean labels during an
early learning phase. However, it then tends to memorize examples annotated with erroneous labels, consequently limiting the
model’s improvement. Specifically, we train two identical models h1 and h2 on target domain data with pseudolabel obtained
from the previously well-trained model in the aforementioned
domain adaptation. During the later phases of the training process, an update rule U is adopted for updating models only when

Fig. 2. Pseudolabel aggregation strategy. The pseudosoft labels of the
target domain are generated by the trained model. Redundant data are
then removed through a standardized preprocessing pipeline. Conflicting
annotations are resolved by majority voting. The refined labels are
converted into hard labels to form a labeled dataset, which is aggregated with the original source dataset for next-round training by domain
adaptation.

their judgment are in disagreement (h1 (xi ) = h2 (xi )). For each
data sample (xi , yi ), the update strategy can be explained
as follow:
S = {(xi , yi ) : h1 (xi ) = h2 (xi )}
h1 ← U (h1 , S)
h2 ← U (h2 , S)

(5)

where S represents the dataset composed of the data that cause
the different judgments between model h1 and h2 , and h ←
U (h, S) represents the model h updating with dataset S, which
is usually the standard gradient descent method. For simplicity,
we directly employ the backbone used in domain adaptation as
the model for training.
C. Pseudolabel Aggregation Strategy
We further employ an approach to improve our model’s performance in target domain through ensemble learning, which
can be found in Fig. 2. After the pseudolabel refinement, each
model can provide good predictions in the target domain by
integrating insights from their individual source domains.
First, we directly leverage these trained models to generate
pseudo soft labels (per-label logit vectors) within the target
domain. Subsequently, per-label logit vectors from each model
are aggregated to derive the global logit vectors. This step
facilitates the assimilation of transferable knowledge from multiple source domains, enhancing classification capabilities in
the target domain. Then the global logit vectors are converted
into hard labels, constituting a novel pseudolabeled dataset with
the corresponding features. Following this, each model is retrained with domain adaptation by incorporating this pseudolabeled dataset alongside their respective source domain datasets.
Finally, models are trained by employing the target domain
data with the aggregated pseudolabels. This whole process can
alleviate the negative impact of irrelevant source information,
enabling the model to refine its initial judgments and achieve
improved performance of classification. Despite the inclusion
of diverse judgments from various models, potentially containing inaccurate pseudolabels, within the source domain data for

HE et al.: UNSUPERVISED CROSS-DOMAIN ATTACK TRAFFIC CLASSIFIER

Algorithm 1: EM Algorithm for the Pseudo-Missing Strategy.

3029

process continues until convergence, progressively enhancing
target domain performance through collaborative model training and robust pseudolabel refinement.
IV. EXPERIMENT IN PUBLIC DATASETS
In this section, we perform comprehensive experiments on
four benchmark datasets to assess the effectiveness of the proposed DANL against several baseline methods. We also examine its sensitivity to some key parameters. The ablation experiments are conducted to demonstrate the efficacy of each module
within DANL as well.
A. Experimental Setup

subsequent training iterations, it is found that models’ performance will continue to improve [19], after iterating this process
several times, our models have a certain ability to classify the
target domain by domain adaptation.
The entire workflow consists of three phases, as shown in
Algorithm 1. Initially, the labeled source domain data Ds is
partitioned into N random subdomains {Ds1 , . . . , DsN } using
a predefined seed (Line 2). The main training loop commences
with the domain adaptation phase, where each model θk is
trained on the subdomain Dsi combined with target domain
data Dt using the specified domain adaptation method M with
uncertainty sorting (lines 3–5). Subsequently, pseudo soft labels
are generated for Dt by the trained model (line 6). In the decoupling phase (lines 7–9), each model pair is trained based on
their disagreement regarding these pseudolabels to encourage
diversity (lines 7–8). Pseudosoft labels for Dt are then generated by the decoupled models (line 9). During the pseudolabel
aggregation phase (lines 10–12), these pseudosoft labels are
aggregated and processed (e.g., duplicate removal) to generate
global logits (line 10). These logits are converted into hard
labels to create a new pseudolabeled dataset (line 11), which
is then used to update each subdomain (line 12). This iterative

1) Datasets: We utilize four benchmark network traffic
datasets (KDDCup99 [20], NSL-KDD [21], CIC-IDS2017 [22],
and CSE-CIC-IDS2018 [22]) to evaluate the effectiveness of the
proposed DANL. These datasets are widely used in the field of
network security for connected vehicles and have been proven
suitable for evaluating attack traffic classification and detection
performance in vehicular communication environments [23],
[24]. For the aforementioned four datasets, we formulate two
tasks.
The first task involves utilizing the KDDCup1999 and NSLKDD datasets to assess the efficacy of our method across diverse data distributions. We further employ the CIC-IDS2017
and CSE-CIC-IDS2018 datasets to create a more challenging
task. These datasets were collected at different times and in different environments. To ensure consistent feature dimensions,
identical data preprocessing methods are applied. This allows
us to assess the performance of our method when handling
entirely distinct data sources with significant variations in data
distribution.
2) Baselines: Several representative classical domain adaptation algorithms [batch nuclear-norm maximization (BNM)
[25], deep adaptation network (DAN) [6], dynamic adversarial adaptation network (DAAN) [7], deep subdomain adaptation network (DSAN) [14], domain adaptive neural network
(DANN) [26], graph spectral alignment framework (SPA) [27],
a discriminator-free adversarial-based unsupervised domain
adaptation for multilabel image classification (DDA-MLIC)
(D-M, for short) [28]] are utilized to compare and confirm the
effectiveness of the proposed DANL. It is worth noting that
the absence of labels in the target domain renders traditional
supervised intrusion detection or classification methods inapplicable, and the nuanced nature of fine-grained multiclassification
problems precludes the utilization of conventional unsupervised
intrusion detection techniques.
3) Implementation Details: To evaluate the experimental results, accuracy is adopted as a metric. Additionally, the confusion matrices is presented to provide a detailed view of the
class-wise performance. In the domain adaptation phase, the
model is trained with a batch size of 128 across 100 epochs,
utilizing the Stochastic gradient descent (SGD) optimizer. The
learning rate for the backbone is set at 1e-4, while the other
layers are trained with the learning rate of 1e-3. The parameter
λ in (2)is set as 1. The output dimension in Task 1 is 4, while

3030

IEEE TRANSACTIONS ON INDUSTRIAL ELECTRONICS, VOL. 73, NO. 2, FEBRUARY 2026

TABLE I
CLASSIFICATION ACCURACY RESULTS FOR TRANSFERRING BETWEEN
KDDCUP99 AND NSL-KDD
KDDCup99 to NSL-KDD
DoS Probe U2R R2L Avg.
T-T
0.999 0.997 0.994 0.993 0.996
S-T
0.973 0.973 0.913 0.978 0.959
BNM
0.943 0.922 0.758 0.924 0.887
DAN
0.972 0.968 0.846 0.965 0.938
DAAN 0.975 0.971 0.902 0.896 0.936
DSAN 0.970 0.969 0.916 0.947 0.951
DANN 0.972 0.970 0.848 0.966 0.939
SPA
0.989 0.979 0.963 0.982 0.978
D-M
0.986 0.965 0.970 0.962 0.971
DSAN+ 0.973 0.973 0.959 0.947 0.963
DANN+ 0.975 0.974 0.969 0.946 0.966
DANL 0.991 0.976 0.957 0.994 0.980
Method

NSL-KDD to KDDCup99
DoS Probe U2R R2L Avg.
0.992 0.998 0.996 0.997 0.996
0.994 0.986 0.879 0.856 0.929
0.994 0.974 0.932 0.612 0.878
0.994 0.991 0.908 0.893 0.947
0.995 0.994 0.913 0.894 0.949
0.995 0.994 0.902 0.896 0.947
0.994 0.994 0.913 0.892 0.948
0.990 0.999 0.942 0.937 0.967
0.995 0.992 0.921 0.924 0.958
0.973 0.966 0.964 0.942 0.961
1.000 0.998 0.912 0.922 0.958
0.986 0.971 0.970 0.951 0.970

Note: Bold values are in tables I-IV identify and emphasize the results
obtained using DANL, the method proposed in this paper.

TABLE II
CLASSIFICATION ACCURACY RESULTS FOR TRANSFERRING FROM
CIC-IDS2017 TO CSE-CIC-IDS2018
Method

Botnet DDoS

DoS

BF

Infiltra

WA

Avg.

T-T
S-T
BNM
DAN
DAAN
DSAN
DANN
SPA
D-M
DSAN+
DANN+
DANL

0.998
0.000
0.030
0.990
0.961
0.980
0.961
0.970
0.959
0.961
0.961
0.972

0.971
0.644
0.141
0.146
0.206
0.623
0.220
0.754
0.707
0.690
0.206
0.761

0.988
0.533
0.000
0.999
1.000
0.999
1.000
0.930
0.990
0.999
0.999
0.814

0.990
0.069
0.062
0.106
0.272
0.115
0.271
0.563
0.303
0.115
0.272
0.540

0.967
0.000
0.417
0.286
0.569
0.285
0.568
0.693
0.591
0.286
0.569
.865

0.985
0.208
0.146
0.506
0.566
0.509
0.504
0.767
0.668
0.515
0.566
0.825

0.996
0.000
0.225
0.509
0.388
0.054
0.001
0.689
0.460
0.037
0.388
0.999

Fig. 3. Confusion matrices of the target datasets. Different colors denote diverse sample counts, where lighter shades correspond to higher
counts. For the transfer tasks on KDDCup99 and NSL-KDD datasets,
the diagonal values typically range from 0 to approximately 60 000. For
the transfer tasks on CIC-IDS2017 and CEC-CIC-IDS2018 datasets, the
diagonal values range from 0 to approximately 80 000.

TABLE III
CLASSIFICATION ACCURACY RESULTS FOR TRANSFERRING FROM
CSE-CIC-IDS2018 TO CIC-IDS2017
Method

Botnet DDoS

DoS

BF

Infiltra

WA

Avg.

T-T
S-T
BNM
DAN
DAAN
DSAN
DANN
SPA
D-M
DSAN+
DANN+
DANL

0.995
0.000
0.604
0.603
0.600
0.940
0.811
0.969
0.941
0.937
0.806
0.973

0.999
0.260
0.114
0.530
0.551
0.846
0.600
0.892
0.747
0.893
0.660
0.883

0.999
0.341
0.813
0.812
0.823
0.814
0.814
0.821
0.816
0.816
0.823
0.813

0.693
0.590
0.022
0.524
0.566
0.471
0.453
0.562
0.593
0.573
0.566
0.860

0.991
0.006
0.041
0.041
0.041
0.049
0.095
0.082
0.052
0.041
0.001
0.045

0.944
0.230
0.343
0.488
0.431
0.605
0.547
0.686
0.627
0.671
0.560
0.732

0.987
0.180
0.462
0.416
0.002
0.508
0.507
0.787
0.613
0.767
0.502
0.817

it is set to 6 in task 2. Each training iteration involves selecting
the top 10% of samples based on their uncertainty for domain
adaptation.
B. Effectiveness Evaluation
In Tables I–III, we demonstrate the effectiveness of DANL in
attack traffic classification across four network traffic datasets,
confusion matrices of these target datasets are also visualized

Fig. 4. Computation complexity analysis. DANL mainly consists of three
modules, and the total FLOPs are represented by the pink rectangle.

in Fig. 3. We compare it with established benchmark algorithms, presenting both the overall accuracy and class-specific
accuracies in these Tables. “T-T” signifies that training and
testing models both on the same target domain, which is also
the common practice of supervised methods. These methods
rely heavily on a large amount of labeled data, which is usually
impossible to achieve in practical scenarios. Notably, this “TT” displays effective recognition of various attack traffic behaviors, achieving commendable results and representing our
method’s ultimate aspiration. The “S-T” illustrates the results
of training the model directly on the source domain and testing
on the target domain. Although the model exhibits acceptable
performance on task 1, its efficacy significantly diminishes on
the more challenging task 2. Specifically, it suggests that applying knowledge solely acquired from CIC-IDS2017 directly
to the CSE-CIC-IDS2018 dataset fails to identify Botnet and

HE et al.: UNSUPERVISED CROSS-DOMAIN ATTACK TRAFFIC CLASSIFIER

(a)

3031

(b)

(c)

Fig. 5. Accuracy result of model robustness study. (a) Accuracy result of model robustness study with uncertainty. The boxplots depict the impact of
varying uncertainty levels on the performance of two domain adaptation methods. Numerical values represent the means, while gray lines indicate
medians. The trends in maximum and minimum values are illustrated by dashed connections, reflecting their fluctuations. (b) Accuracy result of
model robustness study with different numbers of subdomain. (c) Accuracy result of model robustness study with iterations. The performance of
models improves with increasing iterations, eventually tend to stabilize.

DDoS attacks effectively. The results of comparative algorithms
are also presented in these tables, most of which surpass the
“S-T”, which signifies the rationality and applicability of domain adaptation in addressing cross-domain attack traffic classification problems. Additionally, “DSAN+” and “DANN+” denote the classification results achieved by replacing the original
classification loss in these two domain adaptation methods with
our proposed loss function. It is evident across all tasks that
these modifications yield performance improvements over the
original methods, underscoring the efficacy of our designed loss
function. The last row in each table showcases the results of
our proposed DANL, it surpasses all comparative algorithms,
thereby substantiating the effectiveness of our approach.
Furthermore, we have also provided the computational complexity of DANL compared with the baselines, as shown in
Fig. 4. The designed lightweight backbone enables DSAN+ and
DANN+ to achieve lower computational complexity. The decoupling module’s dual-model training roughly doubles FLOPs
to 8.688M, leading to a total of approximately 52.393M FLOPs
for the DANL framework. While overall FLOPs are comparable
to baseline models, our modular decoupling and collaborative
optimization ensure component independence and reduce individual module costs. This design balances controllable complexity with full functionality, ideal for resource-constrained
domain adaptation tasks such as edge deployment and realtime processing.
C. Sensitive Analysis
To further assess the stability and robustness of our proposed
model, we conduct sensitivity experiments on some critical
parameters. First, we evaluate the strategy of selecting training sample based on uncertainty during the domain adaptation phase, and observe its impact on the model’s performance
by adjusting the proportion of training data. As depicted in
Fig. 5(a), using 100% of the target data increases training time
and may reduce model performance due to the accumulation
of incorrect pseudolabels. After gradually filtering out samples
with lower confidence, the model performance shows an upward trend. However, when an extremely small proportion of
data is used, the model performance also degrades, indicating
that the model cannot fully learn effective knowledge from

the target domain due to insufficient training samples. There
appears an inflection point in model performance as the proportion gradually decreases. It can be observed that for DSAN,
this turning point is around 10%, while for DANN, it lies between 5% and 10%, with little difference in model performance
between these two proportions.
We further investigate how partitioning the source domain
affects model performance in domain adaptation for the task of
transferring from CIC-IDS2017 to CSE-CIC-IDS2018, which
can be viewed as leveraging limited attack traffic knowledge
from multiple vehicles to assist classification in the target vehicle [Fig. 5(b)]. The results reveal a gradual performance decline
as the number of subdomains increases (with correspondingly
fewer training samples per subdomain), though the model eventually stabilizes at an acceptable accuracy level. While this
partitioning approach incurs a modest performance reduction
in the initial phase, it offers significant practical advantages by
enabling efficient deployment across multiple lightweight devices. This trade-off proves particularly valuable for real-world
IoV applications, where the model’s ability to run concurrently
on more resource-constrained edge devices (e.g., vehicle ECUs
or roadside units) outweighs the marginal accuracy decrease,
while maintaining sufficient classification capability for most
attack scenarios. Additional experiments analyzing the impact
of different random seeds on domain partitioning can be found
in Fig. 6. As can be seen from the training results of the
first round, compared with DSAN+, the accuracy fluctuation of
DANN+ across various subdomains is slightly larger; however,
the average accuracy of both models remains relatively stable
under different seed settings.
Subsequently, we delve deeper into the impact of iteration
rounds on the performance using the task from CIC-IDS2018
to CSE-CIC-IDS2017 as an example. As illustrated in Fig. 5(c),
the results indicate that relying solely on source domain information obtained from some single domain adaptation method
is insufficient for handling the complexity of extensive highdimensional attack traffic. This inadequacy becomes evident
in effective classification of attack traffic in the target domain.
In addition, it can be seen from the figure that implementing
only one iteration strategy can significantly improve the model’s
ability. Moreover, as the round of iteration increases, the model
consistently improves in classification performance. Notably,

3032

IEEE TRANSACTIONS ON INDUSTRIAL ELECTRONICS, VOL. 73, NO. 2, FEBRUARY 2026

TABLE IV
ABLATION EXPERIMENTS FOR TRANSFERRING FROM CIC-IDS2017 TO
CEC-CIC-IDS2018

(a)

Method

Botnet DDoS

DoS

BF

Infiltra

WA

Avg.

DSAN
DANN
DSAN+
DANN+
1st-D
2nd-DSAN+
2nd-DANN+
2nd-D
3rd-DSAN+
3rd-DANN+
3rd-D (DANL)

0.772
0.767
0.961
0.961
0.961
0.961
0.961
0.960
0.961
0.961
0.972

0.670
0.516
0.690
0.206
0.231
0.889
0.404
0.883
0.900
0.901
0.761

0.999
0.999
0.999
0.999
0.999
0.999
0.999
0.999
0.999
0.999
0.814

0.117
0.062
0.115
0.272
0.391
0.172
0.211
0.286
0.285
0.298
0.540

0.145
0.137
0.286
0.569
0.557
0.569
0.552
0.583
0.582
0.583
0.865

0.457
0.429
0.515
0.566
0.568
0.725
0.644
0.742
0.747
0.750
0.825

0.040
0.095
0.037
0.388
0.747
0.757
0.734
0.739
0.757
0.759
0.999

(b)

Fig. 6. Accuracy result of (a) DSAN+ and (b) DANN+ with random
seeds. The bar chart represents results on each subdomain under the
setting of splitting the source domain into five parts, and the line chart
denotes the average value.

TABLE V
ABLATION STUDY ON THE EFFECTIVENESS OF
DISTANCE METRICS FOR THE ALIGNMENT LOSS
Distance Metric

Model

the performance stabilizes after approximately 3–4 rounds of
iteration, validating the robustness of our iterative approach.
These findings underscore the necessity and effectiveness of
iterative strategies in bolstering classification capabilities and
effectively classifying attack traffic during the knowledge transfer across domains.

DANN+
DSAN+

Cosine

Euclidean

Gaussian

0.520
0.479

0.566
0.515

0.534
0.512

D. Ablation Study
We also conduct ablation experiments to validate the effectiveness of the components in the proposed DANL, as illustrated
in Table IV, where “1st-D” means the first round of decoupling. The original DSAN and DANN employ the standard
cross-entropy loss for classification assistance. Subsequently,
integrating our designed classification loss enhances the results.
After the first iteration with the decoupling method, the model
achieves a result of 0.568. This iteration enables the model to
learn the discrimination of “DDoS” and “Infiltra” (infiltration)
attack traffic from DSAN+ and DANN+. Upon involving the
target domain dataset with aggregated pseudolabels in domain
adaptation training, the model’s performance further improves.
After three iterations, the model reaches a final result of 0.825,
showcasing robust judgments across various classes. Notably,
our approach contributes to providing further granularity in
unsupervised methods, enabling the identification of diverse
attack traffic.
We then conduct ablation experiments to compare different
distance metrics in the alignment loss under the task from CICIDS2017 to CSE-CIC-IDS2018. The results are summarized
in Table V. The results indicate that using Euclidean distance
consistently outperforms other metrics for both DANN+ and
DSAN+. This superiority is likely attributed to its sensitivity to magnitude differences in feature distributions, which
aligns well with our Laplacian spectral framework. Based on
these findings, we have adopted Euclidean distance as the default choice for empirical evaluations, given its demonstrated
effectiveness.

(a)

(b)

Fig. 7. Ablation study on: (a) loss; and (b) backbone component effectiveness.

To further investigate the impact of each loss component on
the results we conduct study under the task of transferring from
CIC-IDS2017 to CSE-CIC-IDS2018, as shown in Fig. 7(a),
where “baseline” refers to the original DSAN and DANN models. It can be observed that the alignment loss appropriately
improves the model performance during the first round of training, while the addition of more robust classification losses helps
better distinguish decision boundaries and enhances classification accuracy. Furthermore, we conduct experiments to show
the results of replacing the designed CNN backbone in DANL
with RNN and Transformer, as presented in Fig. 7(b). It can be
observed that DANL, with its designed lightweight CNN-based
backbone, achieves detection results comparable to those of
the Transformer while maintaining relatively low training and
inference time per epoch, indicating its potential for application
in edge or lightweight devices in the ICVs.

HE et al.: UNSUPERVISED CROSS-DOMAIN ATTACK TRAFFIC CLASSIFIER

(a)

(b)

(c)

(d)

3033

(e)

Fig. 8. Cloud control platform for intelligent connected unmanned systems. (a) Outdoor operating scene of autonomous vehicles. (b) Close-up of
autonomous vehicle exterior. (c) Interior view of unmanned vehicle cockpit. (d) Data monitoring interface of unmanned vehicle system. (e) Interface
of cloud control platform for intelligent connected unmanned systems.

V. EXPERIMENT IN REAL-WORLD SCENARIO
In this section, we verify the effectiveness of the proposed
method by collecting data from real vehicles on a self-construct
intelligent connected unmanned platform.

Considerable research has been conducted on intrusion detection and attack classification for the CAN, as referenced [29],
[30], etc. We collect real-time CAN data from three autonomous
vehicles during their operation at different times to obtain
datasets for various scenarios. Similar to existing works [11],
[29], [31], three types of attacks are considered: DoS attack,
fuzzy attack, and injection attack.

A. Experimental Setup
The experimental platform is shown in Fig. 8. The vehicleroad-cloud integrated control system part of this platform
consists of three unmanned vehicles, a cloud data center, and
supporting monitoring equipment. Fig. 8(a)–(b) depicts the experimental scene and the full-view exterior of the autonomous
vehicle (Kayyi Showjet Pro EV), while Fig. 8(c)–(d) shows
the interior of the cockpit, including the steering wheel, dashboard, and related display devices. Each autonomous vehicle is
equipped with NVIDIA Orin. The autonomous driving system
operates on the Ubuntu 20.04 operating system, with robot
operating system2 (ROS2) framework, and the algorithms are
developed using Python 3. The system adopts a distributed
and modular design, covering core functional modules such
as perception, planning, control, coordination, status monitoring, positioning, and map building. These modules are both
independent and work in coordination, enabling the efficient
completion of autonomous driving tasks in complex scenarios.
Fig. 8(e) displays the real-time monitoring interface of the cloud
control platform. Multisource data (environmental perception,
device status, and vehicle trajectories) are collected by the
devices deployed on roadside sensors and onboard terminals.
These data are transmitted via 5G/4G networks to the platform.
A digital twin of physical road scenarios and vehicle operations
is dynamically updated through 3-D modeling and simulation
techniques. Structured information (e.g., vehicle speed and fault
alerts) and raw data are stored in Alibaba Cloud databases for
efficient storage, querying, and historical traceability.
The CAN protocol is a serial communication protocol designed for real-time communication, with wide applications in
automotive electronics, industrial automation, and other fields.

B. Effectiveness Evaluation
The effectiveness of the proposed DANL is evaluated using
the collected CAN dataset, with the corresponding experimental
results presented in Fig. 9. The figure illustrates the attack traffic
classification accuracy and F1 scores under various transfer
learning settings. For instance, following the experimental setup
described in Section IV, the label “From-Car1-to-Car2” on the
horizontal axis represents the scenario where attack detection
is performed on the second vehicle using knowledge extracted
from the first vehicle. The classification accuracy and F1 score
results suggest that the proposed DANL exhibits competitive
attack classification performance across most transfer settings,
indicating its potential as a viable solution for attack detection
in heterogeneous vehicular systems. Additionally, confusion
matrices for target datasets across three autonomous vehicles
are presented in Fig. 10. High diagonal values of these matrices indicate accurate classification of specific attack types,
highlighting the model’s reliability in threat detection. Low
off-diagonal entries further suggest minimal misclassification,
underscoring its robustness and capacity to distinguish traffic
patterns across heterogeneous vehicular systems.
Furthermore, to evaluate the attack traffic classification performance of DANL in cross-vehicle scenarios, experiments
are conducted using the public dataset OTIDS [31] and our
dataset. Taking the first car (car 1) as an example, the results are
shown in Fig. 11(a). The results of DNAL, first-round DSAN+,
DANN+, and direct training and testing (“S-T”) are provided.
The first-round results of DSAN+ and DANN+ reflect initial
improvements through migration over direct training and testing. DSAN+ shows limited attack classification performance

3034

IEEE TRANSACTIONS ON INDUSTRIAL ELECTRONICS, VOL. 73, NO. 2, FEBRUARY 2026

(a)

Fig. 9. Comparison of accuracy and F1 results with different transfer
settings in CAN datasets.

Fig. 10. Confusion matrices of the target datasets across three different
autonomous vehicles. For the transfer tasks between the three vehicles,
the diagonal values in the confusion matrices are generally in the range
of 0 to approximately 40 000.

when transferred from the OTIDS dataset to car 1. After incorporating the knowledge from DANN+ and applying iterative
optimization, DNAL achieves significantly improved classification accuracy.
We further investigate the impact of cross-network data on
the performance of attack traffic classification. Specifically,
we transfer knowledge between CAN data and external sensor
network data to simulate real-world scenarios. As illustrated
in Fig. 11(b), we extract historical sensor network data from
the Alibaba cloud database, which captures environmental conditions and traffic patterns. We then conduct transfer learning
experiments with the CAN data from car 1. The results show
that direct training on one network and testing on the other yield
accuracies of only 0.492 and 0.373, highlighting the challenge
of cross-network generalization, while DANL maintains stable
classification accuracy in both scenarios. This demonstrates
DANL’s superiority in handling heterogeneous data sources,
suggesting its potential as a viable option for securing interconnected vehicle systems in practical deployments.
Finally, we consider a new type of attack: a message injection
attack where we inject tampered data to switch the vehicle’s

(b)

Fig. 11. Classification performance results under: (a) different vehicles;
and (b) different networks.

Fig. 12. Classification performance results under the designed attack.
The notation ‘K to M’ represents the transfer learning scenario from the
Kayyi Showjet Pro EV (denoted as K) to the Wuling Hongguang Mini EV
(denoted as M), with the reverse transfer indicated accordingly.

high and low beam headlights. In real-world nighttime highway
conditions, sudden frequent switching of high and low beams
can indeed distract and impair the vision of oncoming drivers,
potentially leading to safety hazards. Since this attack primarily
affects the protocol related to the vehicle’s lighting system,
it poses relatively low risk during experiments. Specifically,
we implemented this by alternatingly injecting CAN messages
that switch the headlights during normal driving conditions and
collected corresponding data. To simulate cross-domain transfer scenarios, we included an additional vehicle of a different
model, the Wuling Hongguang MINIEV. The collected dataset
comprises three types of attack data: 1) DoS attack data; 2)
fuzzy attack data; and 3) message injection attack targeting
the lighting system. The results of experiments in transferring
between Kayyi (K) and MINI (M) can be found in Fig. 12.
It can be observed that, even though there are differences in
the CAN IDs and message formats associated with headlight
control among these distinct vehicle models, the cross-domain
feature alignment strategy of DANL sustained robust attack
classification performance in both scenarios. This serves to
validate the robustness of our proposed method with respect to
protocol variations across heterogeneous vehicles.

HE et al.: UNSUPERVISED CROSS-DOMAIN ATTACK TRAFFIC CLASSIFIER

VI. CONCLUSION
In this article, we proposed a cross-domain attack traffic
classifier for ICV named DANL, which leveraged attack traffic
information from other domains to aid the unlabeled target
domain in fine-grained attack traffic classification. It amalgamated various domain adaptation methods to train models
in the source domain, acquiring pseudolabels for target domains and subsequently refining these labels via learning from
noisy labels. By integrating a pseudolabel aggregation strategy,
a straightforward iterative process showcased promising performance. Experimental results showcased that the proposed
DANL outperformed existing methods by up to 5.8% in performance across classical network traffic datasets. Moreover,
the effectiveness of DNAL has been verified by real data experiments on the self-constructed ICV platform.
It can be found that DANL can be integrated with existing
unsupervised anomaly detectors to perform fine-grained network intrusion detection. After intercepting the data, most of
the easily identifiable normal traffic is filtered by traditional
unsupervised methods with set thresholds, and then DANL
is used to further classify the attack traffic data in the target
domain by learning the knowledge from other domains. In the
future, we will explore more appropriate data augmentation
methods for attack traffic classification, specifically addressing
class imbalance. Furthermore, we will investigate the incorporation of multimodal data sources to enrich feature representations and enhance detection capabilities. We will also consider
more practical and theoretically guaranteed adversarial attack
models, continuously improving our classification and detection methods from an adversarial perspective.
REFERENCES
[1] W. Gong et al., “Multi-order feature interaction-aware intrusion detection scheme for ensuring cyber security of intelligent connected
vehicles,” Eng. Appl. Artif. Intell., vol. 135, 2024, Art. no. 108815.
[2] C. I. Nwakanma et al., “Explainable artificial intelligence (XAI) for
intrusion detection and mitigation in intelligent connected vehicles: A
review,” Appl. Sci., vol. 13, no. 3, p. 1252, 2023.
[3] C. Sheng, Y. Yao, W. Li, W. Yang, and Y. Liu, “Unknown attack traffic
classification in SCADA network using heuristic clustering technique,”
IEEE Trans. Netw. Service Manag., vol. 20, no. 3, pp. 2625–2638, Sep.
2023.
[4] A. Yılmaz, T. Ateşci, H. Meral, and G. Bayrak, “A real-time improved
ML method for PQD classification of a PV-powered EV charging
station,” IEEE Trans. Ind. Electron., vol. 72, no. 3, pp. 2622–2632,
Mar. 2025.
[5] Y. Huang, J. Peng, G. Zhang, W. Sun, N. Chen, and Q. Du, “Adversarial
domain adaptation network with calibrated prototype and dynamic instance convolution for hyperspectral image classification,” IEEE Trans.
Geosci. Remote Sens., vol. 62, pp. 1–13, 2024, Art. no. 5514613.
[6] M. Long, Y. Cao, J. Wang, and M. Jordan, “Learning transferable
features with deep adaptation networks,” in Proc. Int. Conf. Mach.
Learn., 2015, pp. 97–105.
[7] C. Yu, J. Wang, Y. Chen, and M. Huang, “Transfer learning with
dynamic adversarial adaptation network,” in Proc. IEEE Int. Conf. Data
Mining, 2019, pp. 778–786.
[8] Z. Niu, J. Wu, and H. He, “A novel experience replay-based offline
deep reinforcement learning for energy management of hybrid electric
vehicles,” IEEE Trans. Ind. Electron., vol. 72, no. 7, pp. 7160–7169,
Jun. 2025.
[9] H. H. Kang and C. K. Ahn, “Distributed finite memory online learning
strategy for multi-UAV systems with neural networks,” IEEE Trans. Ind.
Electron., vol. 72, no. 1, pp. 919–927, Jan. 2025.

3035

[10] A. K. Desta, S. Ohira, I. Arai, and K. Fujikawa, “REC-CNN: In-vehicle
networks intrusion detection using convolutional neural networks trained
on recurrence plots,” Veh. Commun., vol. 35, 2022, Art. no. 100470.
[11] E. Seo, H. M. Song, and H. K. Kim, “GIDS: GAN based intrusion
detection system for in-vehicle network,” in Proc. Annu. Conf. Privacy,
Secur. Trust, 2018, pp. 1–6.
[12] C. Xu, J. Shen, and X. Du, “A method of few-shot network intrusion detection based on meta-learning framework,” IEEE Trans. Inf. Forensics
Secur., vol. 15, pp. 3540–3552, 2020.
[13] X. Hu, C. Zhu, G. Cheng, R. Li, H. Wu, and J. Gong, “A deep
subdomain adaptation network with attention mechanism for malware
variant traffic identification at an IoT edge gateway,” IEEE Internet
Things J., vol. 10, no. 5, pp. 3814–3826, Mar. 2023.
[14] Y. Zhu et al., “Deep subdomain adaptation network for image classification,” IEEE Trans. Neural Netw. Learn. Syst., vol. 32, no. 4, pp.
1713–1722, Apr. 2020.
[15] J. Wu et al., “Joint semantic transfer network for IoT intrusion detection,” IEEE Internet Things J., vol. 10, no. 4, pp. 3368–3383, Feb. 2022.
[16] J. Wu, H. Dai, Y. Wang, K. Ye, and C. Xu, “Heterogeneous domain
adaptation for IoT intrusion detection: A geometric graph alignment
approach,” IEEE Internet Things J., vol. 10, no. 12, pp. 10 764–10 777,
Jun. 2023.
[17] L. Chen, Z. Gan, Y. Cheng, L. Li, L. Carin, and J. Liu, “Graph optimal
transport for cross-domain alignment,” in Proc. Int. Conf. Mach. Learn.
(PMLR), 2020, pp. 1542–1553.
[18] E. Malach and S. Shalev-Shwartz, “Decoupling ‘when to update’ from
‘how to update,” in Proc. Adv. Neural Inf. Process. Syst., vol. 30, 2017,
pp. 961–971.
[19] C. Wei, K. Shen, Y. Chen, and T. Ma, “Theoretical analysis of selftraining with deep networks on unlabeled data,” in Proc. Int. Conf.
Learn. Representations, 2021. [Online]. Available: https://openreview.
net/forum?id=rC8sJ4i6kaH
[20] S. Stolfo, W. Fan, W. Lee, A. Prodromidis, and P. Chan, “KDD
Cup 1999 Data,” UCI Machine Learning Repository, 1999, doi:
10.24432/C51C7N.
[21] M. Tavallaee, E. Bagheri, W. Lu, and A. A. Ghorbani, “A detailed
analysis of the KDD Cup 99 data set,” in Proc. IEEE Symp. Comput.
Intell. Secur. Defense Appl., 2009, pp. 1–6.
[22] I. Sharafaldin, A. H. Lashkari, and A. A. Ghorbani, “Toward generating
a new intrusion detection dataset and intrusion traffic characterization,” in Proc. Int. Conf. Inf. Syst. Secur. Privacy, vol. 1, 2018,
pp. 108–116.
[23] M. Fu, P. Wang, M. Liu, Z. Zhang, and X. Zhou, “IoV-BERT-IDS:
Hybrid network intrusion detection system in IOV using large language
models,” IEEE Trans. Veh. Technol., vol. 74, no. 2, pp. 1909–1921, Feb.
2025.
[24] J. Zhang, J. Zhang, Z. Ma, T. Li, X. Li, and J. Ma, “RUPT-FL:
Robust two-layered privacy-preserving federated learning framework
with unlinkability for IoV,” IEEE Trans. Veh. Technol., vol. 74, no.
4, pp. 5528–5541, Apr. 2025.
[25] S. Cui, S. Wang, J. Zhuo, L. Li, Q. Huang, and Q. Tian, “Towards
discriminability and diversity: Batch nuclear-norm maximization under
label insufficient situations,” in Proc. IEEE/CVF Conf. Comput. Vis.
Pattern Recognit., 2020, pp. 3941–3950.
[26] M. Ghifary, W. B. Kleijn, and M. Zhang, “Domain adaptive neural
networks for object recognition,” in Proc. Pacific Rim Int. Conf. Artif.
Intell., 2014, pp. 898–904.
[27] Z. Xiao et al., “SPA: A graph spectral alignment perspective for domain
adaptation,” Adv. Neural Inf. Process. Syst., vol. 36, pp. 37252–37272,
Sep. 2023.
[28] I. P. Singh, E. Ghorbel, A. Kacem, A. Rathinam, and D. Aouada,
“Discriminator-free unsupervised domain adaptation for multi-label image classification,” in Proc. IEEE/CVF Winter Conf. Appl. Comput. Vis.,
2024, pp. 3936–3945.
[29] S. Jeong, S. Lee, H. Lee, and H. K. Kim, “X-CANIDS: Signal-aware
explainable intrusion detection system for controller area network-based
in-vehicle network,” IEEE Trans. Veh. Technol., vol. 73, no. 3, pp. 3230–
3246, Mar. 2023.
[30] L. Du, Z. Gu, Y. Wang, and C. Gao, “Open world intrusion detection:
An open set recognition method for can bus in intelligent connected
vehicles,” IEEE Netw., vol. 38, no. 3, pp. 76–82, May 2024.
[31] H. Lee, S. H. Jeong, and H. K. Kim, “OTIDS: A novel intrusion
detection system for in-vehicle network by using remote frame,” in Proc.
Annu. Conf. Privacy, Secur. Trust., Piscataway, NJ, USA: IEEE Press,
2017, pp. 57–5709.

3036

IEEE TRANSACTIONS ON INDUSTRIAL ELECTRONICS, VOL. 73, NO. 2, FEBRUARY 2026

Yongping He is currently working toward the
Ph.D. degree in control science and engineering
from the School of Automation, Beijing Institute
of Technology (BIT), Beijing, China.
His research interests include Internet of
Things, time series anomaly detection, and generative models.

Yuanqing Xia (Fellow, IEEE) received the Ph.D.
degree in control theory and control engineering from Beijing University of Aeronautics and
Astronautics, Beijing, China, in 2001.
From 2002 to 2003, he was a Postdoctoral Research Associate with the Institute of Systems
Science, Academy of Mathematics and System
Sciences, Chinese Academy of Sciences, Beijing. From 2003 to 2004, he was with the National University of Singapore, Singapore, as a
Research Fellow, where he worked on variable
structure control. From 2004 to 2006, he was with the University of
Glamorgan, Pontypridd, U.K., as a Research Fellow. From 2007 to 2008,
he was a Guest Professor with Innsbruck Medical University, Innsbruck,
Austria. Since 2004, he has been with the Department of Automatic
Control, Beijing Institute of Technology, Beijing, first as an Associate Professor, then, since 2008, as a Professor. In 2023, he was also hired as the
President of Zhongyuan University of Technology, Zhengzhou, China. He
is currently both a Professor with Beijing Institute of Technology and the
President of Zhongyuan University of Technology. His research interests
include cloud control systems, networked control systems, robust control
and signal processing, active disturbance rejection control, unmanned
system control, and flight control.
Tijin Yan received the B.S. degree in control
science and engineering in 2019 from Beijing
Institute of Technology (BIT), Beijing, China,
where he is currently working toward the Ph.D.
degree in control science and engineering.
His research interests include graph representation learning, generative models, time series modeling, time series anomaly detection,
and dynamic systems.

Yufeng Zhan received the Ph.D. degree in control theory and control engineering from Beijing
Institute of Technology (BIT), Beijing, China, in
2018.
He is currently an Associate Professor with
the School of Automation, BIT. Prior to joining
BIT, he was a Postdoctoral Fellow with the Department of Computing, The Hong Kong Polytechnic University, Hong Kong. His research interests include Internet of Things, cloud/edge
computing, and machine learning systems.
Jiaru Song was born in Shanxi, China, in 2000.
He received the M.S. degree in computer science from Jilin University, Jilin, China, in 2025.
He is currently a Research Assistant at The
Hong Kong Polytechnic University, Shenzhen
Research Institute. His research interests include intelligent connected vehicle and intrusion
detection.

Zihang Feng was born in Shanxi, China, in
1997. He received the B.S. degree in automation in 2018 from Beijing Institute of Technology,
Beijing, China, where he is currently working toward the Ph.D. degree in control science and
engineering with the School of Automation.
His research interests include visual tracking
and multimodality fusion.
PAPER_TEXT
