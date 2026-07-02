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
# [306] Space Decoupled Prototype Learning for Few-Shot Attack Detection in Cyber–Physical Systems
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
编号：306
题名：Space Decoupled Prototype Learning for Few-Shot Attack Detection in Cyber–Physical Systems
年份：2024
DOI：10.1109/tii.2024.3423327
来源：IEEE Transactions on Industrial Informatics
PDF：paper/10.1109_TII.2024.3423327.pdf
已有粗分类：恶意流量、暗网与攻击检测
二级关联：无
相关性：强相关，分数 10
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\306.txt
- 原始字符数：64336
- 本次发送字符数：64336
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
12350

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

Space Decoupled Prototype Learning for
Few-Shot Attack Detection in
Cyber–Physical Systems
Haili Sun , Yan Huang , Member, IEEE, Chunjie Zhou , Lansheng Han , Hongle Liu, Juan Chen ,
and Xin Li

Abstract—Due to the lack of effective attack detection
measures, cyberattacks may cause strong damage to industrial cyber–physical systems (CPSs). The embedding
of attack categories learned by the existing attack detection methods is highly coupled to each other with fuzzy
boundaries and overlapped neighborhood, leading to weak
robustness and high false positive rates. To address these
issues, in this article, we propose a few-shot attack detection method based on decoupled prototype learning
(DPL-FSAD), aiming to enhance the detection accuracy and
generalization capabilities for malicious attacks in CPS.
Specifically, we first introduce feature contrastive learning
to extract differentiated features from highly similar samples, achieving compact intraclass and sparse interclass
feature embedding space. To solve the problem of fuzzy
boundaries of different attack categories, prototype contrastive learning is then employed to reduce the coupling
degree among prototypes and enhance their discriminability. A regularization term is exploited to mitigate the overfitting problem by reducing the gap between the feature
embedding and prototypes. Furthermore, an orthogonal
constraint is employed to separate prototypes of different
attack types, generating a decoupled prototype embedding

Manuscript received 22 January 2024; revised 2 May 2024; accepted
18 June 2024. Date of publication 16 July 2024; date of current version
7 October 2024. The work of Lansheng Han was supported in part by
the National Key Research and Development Program of China under
Grant 2022YFB3103402 and in part by the National Natural Science
Foundation of China under Grant 62072200, Grant 62172176, and Grant
62127808. The work of Chunjie Zhou was supported by the National
Natural Science Foundation of China under Grant 61873103, Grant
62127808, and Grant 61433006. Paper no. TII-24-0342. (Haili Sun and
Yan Huang contributed equally to this work.) (Corresponding author:
Lansheng Han.)
Haili Sun, Lansheng Han, Hongle Liu, Juan Chen, and Xin Li are
with the Hubei Key Laboratory of Distributed System Security, Hubei
Engineering Research Center on Big Data Security, School of Cyber Science and Engineering, Huazhong University of Science and Technology,
Wuhan 430074, China (e-mail: hailisun@hust.edu.cn; hanlansheng@
hust.edu.cn; hongleliu@hust.edu.cn; juanchen1737@hust.edu.cn; zsgkljhy@126.com).
Yan Huang is with the National Key Laboratory of Science and Technology on Multispectral Information Processing, School of Artificial Intelligence and Automation, Huazhong University of Science and Technology, Wuhan 430074, China (e-mail: platanus@hust.edu.cn).
Chunjie Zhou is with the Key Laboratory of Image Processing and
Intelligent Control, Ministry of Education, School of Artificial Intelligence and Automation, Huazhong University of Science and Technology, Wuhan 430074, China (e-mail: cjiezhou@hust.edu.cn).
Color versions of one or more figures in this article are available at
https://doi.org/10.1109/TII.2024.3423327.
Digital Object Identifier 10.1109/TII.2024.3423327

space. The experimental results on three public cyberattack
datasets show that, compared with the suboptimal model a
few-shot learning model with Siamese convolutional neural
network (FSL-SCNN), the proposed DPL-FSAD can improve
the precision by 5.53%, F1-score by 3.3%, and reduce the
false positive rate by 2.37% in average, which proves that
the space decoupled prototype learning is effective for improving the generalization and robustness of industrial CPS
attack detection in few-shot scenario.
Index Terms—Few-shot learning (FSL), industrial cyber–
physical system (CPS), network attack detection, prototype
contrastive learning (PCL), space decoupling.

I. INTRODUCTION
HE rapid development of Industry 4.0 has promoted the
integration of cyber network and physical systems, giving
rise to a new paradigm: Cyber–physical systems (CPSs). CPSs
are large, distributed, heterogeneous, and multidimensional intelligent systems, integrating communication, computation, and
control to realize close combination and coordination of physical and software resources [1]. These systems provide a wide
range of functionalities, including intelligent production and
collaborative control, which play significant roles in advancing
industrial intelligence. However, they are vulnerable to cyber–
physical attacks due to the lack of effective network security
defense measures [2]. Attackers may invade controllers of CPS
by launching malicious code injection attacks to disrupt the
normal operation of equipment and the production order of an
enterprise, which may cause catastrophic consequences on the
economy, environment, and life security [3], [4]. Therefore, the
detection of cyberattacks against CPS is of paramount importance for timely warning, ensuring enterprise production safety,
and reducing economic loss.
Attack detection aims to distinguish attack behaviors from
normal system states within multivariate time series (MTS), such
as network traffic, sensor signals, and system logs generated by
CPS. However, due to the complexity of network attacks and
the variety of network functionalities, detection technologies
based on mathematical statistics, state estimation, and traditional
machine learning encounter issues, such as high false alarm rate
(FAR), poor adaptability, and low detection accuracy. Recently,
attack detection algorithms based on deep learning have been
widely explored [3], [5]. These attacks are usually sparse or even
unseen in real-world scenarios, leading to insufficient labeled

T

1551-3203 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

SUN et al.: SPACE DECOUPLED PROTOTYPE LEARNING FOR FEW-SHOT ATTACK DETECTION IN CYBER–PHYSICAL SYSTEMS

Fig. 1. Illustration of the problems and motivations. (a) Highly correlated features with large coupling degrees (e.g., c>0.2) and fuzzy
boundaries. (b) Overlapped prototype neighborhood. (c) Feature space
decoupling based on FCL. (d) Prototype space decoupling based on
PCL and regularization. (e) Decoupling via prototype orthogonal constraint.

samples for model training and problems, such as overfitting
and weak generalization ability. This poses great challenges
for existing attack detection methods that rely heavily on rich
labeled data.
To this end, some researchers have attempted to introduce the
few-shot learning (FSL) method to overcome the challenge of
insufficient labeled samples. FSL enables models to effectively
distinguish novel categories with few labeled samples. In recent
years, several works based on FSL have been proposed for attack
detection in industrial CPS. Zhou et al. [6] created a Siamese
neural network for detecting industrial attacks to solve the
overfitting issue. Huang et al. [7] proposed a gated network that
detects different attacks by aggregating both seen and unseen
types within few-shot settings.
However, due to the inherent high correlation and coupling
degree of sample features between attack categories, as shown
in the upper layer of Fig. 1, methods based on feature learning,
such as convolutional neural networks [see Fig. 1(a)], and metalearning methods based on prototypical networks (PNs) [see
Fig. 1(b)] face the problems of fuzzy boundaries and overlapped
prototype neighborhood, leading to poor robustness and high
FAR in the scenario of sample sparsity and few-shot cases.
Furthermore, Tian et al. [8] have demonstrated that a welldesigned feature extractor is more effective than models relying
solely on complex metalearning algorithm for few-shot classification tasks, as they are hard to extract more discriminative and
differentiated features from industrial CPS data. To overcome
the above challenges, our intuitive idea is to achieve feature
space decoupling by extracting differentiated sample features
and prototype space decoupling by prototypical intraclass aggregation and interclass separation so as to reduce the feature
correlation and coupling degree between different attack categories, as shown in the lower layer of Fig. 1.
Therefore, this article proposes a few-shot attack detection
method based on space decoupled prototype learning, called
DPL-FSAD, for industrial CPS security. Specifically, to extract

12351

distinctive features and enhance the discriminability, we first design a feature contrastive learning (FCL) [see Fig. 1(c)] module
via maximizing mutual information to obtain a compact intraclass and sparse interclass feature embedding space. Second, to
alleviate the problem of sample sparsity and fuzzy boundaries
of different attack categories, we propose prototype contrastive
learning (PCL) [see Fig. 1(d)] to reduce the coupling degree
between different prototypes. In addition, the FCL and PCL
may overfit in few-shot cases; thus, a robust regularization term
is exploited based on the mutual information from features to
prototypes. Finally, the orthogonal constraints between prototypes [see Fig. 1(e)] are introduced to make the prototype spaces
of different attack categories orthogonal to each other so as to
realize prototype decoupling in the latent embedding space. This
not only improves the robustness of model classification but also
reduces the FAR.
The main contributions of this article are as follows.
1) A two-stage few-shot attack detection model DPL-FSAD
based on FCL and PCL is proposed to tackle the problem
of high coupling degree and fuzzy boundaries between
different attack types. Different attacks are spatially decoupled from the feature level and prototype level, respectively, which improves the discriminability of complex
CPS attacks.
2) To learn more differentiated features from few labeled
samples, a lightweight FCL module is designed to generate a compact intraclass and sparse interclass embedding
space.
3) To reduce the coupling degree between different prototypes, PCL and orthogonal constraints are exploited for
generating highly decoupled embedding space.
4) An efficient attack detection algorithm is developed based
on the decoupled feature and prototype embedding space,
which identifies CPS attacks with few labeled samples
through the nearest neighbor in the prototype embedding
space.
II. RELATED WORK
In recent years, attack detection algorithms [10], [12] have
been extensively analyzed and studied for the security and reliability of industrial CPS. It is crucial to develop appropriate detection architectures to identify attacks on these systems. Several
methods based on deep learning have been designed to protect
CPS against cyber–physical attacks [11], such as error diagnosis
[13], attack detection, and fault-tolerant control [14]. Pearce
et al. [15] proposed a bidirectional runtime enforcement to
mitigate the damages posed by compromised controllers in CPS.
To alleviate misclassification errors, Khan et al. [27] designed a
statistical feature extraction algorithm and developed an intrusion detection system based on long-short term memory network
(LSTM) autoencoder to distinguish malicious actions from industrial control systems. Zhou et al. [3] proposed a variational
long short-term memory model (VLSTM) for guaranteeing industry security. They designed a variational reparameterization
scheme to capture the low-dimensional feature embeddings and
identified anomalies by an estimation network. Wu and Guo [28]
detect attacks by designing a hierarchical convolution neural

12352

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

network and recurrent neural network (CNN+RNN) architecture named LuNet with a gradually increasing granularity to
extract both spatial and temporal features of the data. Obviously,
the aforementioned approaches show that deep-learning-based
methods are promising to identify cyber–physical attacks in
industrial CPS. However, as traditional supervised learning
methods typically rely on rich labeled data and prior knowledge,
they are difficult to detect novel attacks from few labeled samples
effectively in the smart industrial environment.
Semisupervised anomaly detection: To alleviate the above
problem, several researchers have developed semisupervised
learning anomaly detection techniques. Huang et al. [16] developed a semisupervised learning-based framework named a semisupervised learning based active anomaly detection framework
using variational auto-encoder (SLA-VAE) to detect anomalies
in an industrial environment using a variational autoencoder. To
detect anomaly patterns in MTS, Zheng et al. [17] integrated
reconstruction model, prediction model, and auxiliary discriminator and proposed an end-to-end semisupervised anomaly detection model to make reasonable use of the limited labeled data.
Contrastive learning for attack detection: Contrast learning
is widely used in computer vision [18], [19]. Due to its
powerful representation learning ability, many researchers
have introduced it to attack detection field [20], [21]. Kopuklu
et al. [20] adopt supervised contrastive learning for detecting
anomalous driving behavior. For the out-of-class detection
task, Shenkar and Wolf [21] proposed to maximize the
mapping relationship of mutual information between samples
and their shielded part through contrastive loss. However,
these methods do not incorporate the label information for
temperature coefficient adjustment, which may lose some
class-level features. In addition, the correlation between
different categories has not been well measured.
FSL for attack detection: Few-shot learning (FSL) is a new
type of transfer learning technique [22]. By reusing the transferable knowledge of existing classes, it can identify novel
categories with limited supervisory information [6], [23]. Zhou
et al. [6] develop an anomaly detection model named a fewshot learning model with Siamese convolutional neural network
(FSL-SCNN) based on Siamese convolutional neural network
to detect the anomalies in industrial CPS. Kale and Thing
[24] propose an enhanced anomaly detection network based on
FSL to identify anomalies using few seen class anomalies and
evaluated the network on three public datasets. To optimize the
resource consumption in systems, Puzanov et al. [25] propose
a deep reinforcement one-shot learning framework and train a
deep-Q network to obtain a policy for identifying unseen classes
in testing data. To overcome the class imbalance problem,
Bedi et al. [26] design a new type of intrusion system named
Siam-intrusion detection systems (IDS) based on a Siamese
neural network to detect attacks without using oversampling
and random undersampling. However, these methods neglect
the possible coupling between different classes in the learned
feature space, which may lead to high false positive rates.
Different from the existing approaches, we solve the problems
of fuzzy boundaries and neighborhood overlapping of different
attack categories via space decoupling techniques, i.e., feature
decoupling via FCL and prototype decoupling via PCL, regularization, and orthogonal constraint, to achieve a high intraclass
variance and low interclass coupling degree. To facilitate comparison, we also analyzed the strengths and weaknesses of the
above models, as shown in Table I.
III. PROBLEM DEFINITION
In this article, the attack detection of industrial CPS is defined
as an FSL task. Given a dataset D containing two general
subsets Dnor and Datt indicating normal and attack samples,
respectively, Dnor = {(xnori , ynori )|i = 1, 2, . . . , Nnor } contains
Nnor labeled normal samples in which xnori is the ith normal
sample and ynori is the corresponding class label. Likewise,
Datt = {(xatti , yatti )|i = 1, 2, . . . , Natt } contains Natt labeled attack samples in which xatti is the attack sample and yatti is the
corresponding class label. To describe the few-shot scenario, we
assume that the scale of attack samples is far less than normal
samples, i.e., Nnor  Natt . Thus, a set of samples from Datt is
selected to form the support set TrS in each training episode, and
the corresponding query set TrQ , which is used to indicate the
unobserved samples of novel classes between different episodes,
can be described as TrQ = {(xattj , yattj )|j = 1, 2, . . . , Nq }.
Specifically, to form the N -way k-shot learning task, we randomly select N malicious attack categories from Datt , each
category contains k samples to form the support set TrS and
the corresponding unseen query set TrQ , which indicates other
samples of the same categories in each training episode. The
few-shot attack detection task based on prototype learning aims
to learn the prototypes for each of the N attack categories
using the corresponding k samples, then classify unseen samples
according to the distance to the N different prototypes.
IV. METHODOLOGY
A. Framework Overview
The left part of Fig. 2 illustrates a typical architecture for
attack detection in artificial intelligence (AI)-enhanced industrial CPS in which attackers may send the malicious code to
compromise the CPS systems through hacking into the CANbus
network or programmable logic controller (PLC) controllers.
The supervisory control and data acquisition system is involved
to monitor and collect sensor signals (e.g., pressure and temperature) and network flows (e.g., TX&RX packet data) generated
across the cyber network, in which the AI-based attack detection
module is deployed to identify malicious attacks.
Unlike the traditional classification models in industry, we
formulate the detection of malicious attacks with few labeled
abnormal samples in CPS as a few-shot classification task and
proposed a novel and efficient attack detection architecture based
on prototype learning to ensure its security and safety (upper
right of Fig. 2).
Fig. 3 illustrates the architecture of the proposed DPL-FSAD,
which consists of three modules, i.e., feature extractor, FCL, and
decoupled prototype generation (PCL). The feature extractor
is composed of two residual blocks and each block contains
two convolution layers. One of the main components of the
FCL module is a contrastive head with a multilayer perceptron
(MLP) that maps feature into a hypersphere. In addition, the PCL

SUN et al.: SPACE DECOUPLED PROTOTYPE LEARNING FOR FEW-SHOT ATTACK DETECTION IN CYBER–PHYSICAL SYSTEMS

12353

TABLE I
STRENGTHS AND WEAKNESSES OF THE METHODS (UL DENOTES UNSUPERVISED LEARNING, SSL DENOTES SEMISUPERVISED LEARNING, SL DENOTES
SUPERVISED LEARNING, CL DENOTES CONTRASTIVE LEARNING, AND FSL DENOTES FEW-SHOT LEARNING)

Fig. 2.

Overview of a typical hierarchical layered architecture of security protection for industrial CPS.

module consists of three convolution layers with regularization
constraint and orthogonal constraint to generate prototype embedding space, in which the query sample can be classified via
searching for the nearest prototype.
On the one hand, the quality of features captured from input
data determines the upper bound of the model. A well-designed
encoder is of more significance than a complex metalearning
framework in FSL [8]. Therefore, we design the specific FCL
module for industrial CPS attack samples to extract differentiated high-level features (see Section IV-B for details). On
the other hand, to identify unseen attacks, we formulate the
attack detection process as a classification task based on class
prototypes. Intuitively, the more accurate the class prototype is,
the better performance the detection achieves. However, in the
FSL scenario, the learned prototypes usually deviate from the
true center of the class due to few labeled samples [9]. To solve

this problem, we propose decoupled PCL to make prototypes
closer to the real class center and design orthogonal constraints
on prototypes to separate the different prototype spaces of the
attack classes, thereby reducing the coupling degree of each
prototype space.
Furthermore, as industrial processes are sensitive to the false
positive rate, even a minute of downtime may cause serious loss
[2]. To this end, a robust regularization term is also designed
based on the distance between samples and the corresponding
prototypes so that similar samples will distribute closer in the
feature space to generate more distinctive prototypes, which can
benefit from improving the generalization ability of the model
(see Section IV-C for details).
Overall, the proposed attack detection algorithm consists of
two stages: the FCL stage and the PCL stage. FCL is the premise
of PCL, providing it with decoupled feature representation. The

12354

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

Fig. 3. Architecture of the proposed DPL-FSAD. Inputs xs and xq denote the samples of the support set and the query set, respectively. The
input is first passed through the feature extractor to obtain the features zs and zq , which are then fed into the FCL and PCL modules for FCL and
prototype generation tasks, respectively. In addition, in the FCL module, the contrastive head is an MLP, which encodes the features zs and zq
into a 1 × 128-dimensional vector; in the PCL module, Ω(·) denotes the prototype generation function, and C1 , C2 , and C3 denote the generated
prototypes.

purpose of FCL is to generate a distinctive high-level feature
embedding space that is compact within classes and sparse
between classes. Based on the feature embedding space, the
PCL aims to learn a high-quality prototype space in which
prototypes are located close to the real class centers. Meanwhile,
orthogonal constraints and regularization terms are designed to
reduce the coupling degree of the prototype space and improve
the generalization ability of the model.

During the FCL process, specifically, for a minibatch of K
features {ri , yi }N
i=1 , they are mapped into a hypersphere denoted
by
the contrastive head, where zi = MLP(ri ) ∈
as {zi , yi }N
i=1
R1×128 and yi ∈ R1×128 is the label of the ground truth, MLP
denotes the multilayer perceptron, then the FCL loss LFCL can
be defined as follows:
N

LFCL =

1 
Lz
N i=1 i

Lz i =


−1
exp (d (zi , zk ) /τ )
.
log N
|Nyi | − 1
q=1 exp (d (zi , zq ) /τ )

B. Stage 1: FCL
Aiming at the problem that most existing attack detection
methods may fail to extract the differentiated features of CPS
network attacks and fuzzy boundaries, we propose the following
hypothesis.
Hypothesis 1. FCL can capture common features of positive
samples and differentiated features of negative samples, thus
improving the significance level of key features.
According to Hypothesis 1, we first design a specific feature
extractor f for CPS attacks to encode samples into an embedding
space. Then, to improve the quality of the embedding space, we
conduct the FCL as a supervised instance-level classification
task, which is designed to recognize latent fine-grained structure
in the low-dimensional feature space by separating the representations of different latent classes and aggregating those of the
same latent classes simultaneously. Meanwhile, we develop a
class-information injection (CII) technique for the FCL to obtain
a compact intraclass and sparse interclass embedding space. The
FCL process is shown in the upper right of Fig. 3.
Given input data xi , the feature extractor f encodes it as a
feature embedding ri that can be represented as follows:
ri = f (xi , θ)

(1)

where θ denotes the parameters of f and ri denotes the encoded
feature embedding. After that, ri is passed to a contrastive head
to conduct the following FCL process.

(2)
(3)

k∈Nyi

Here, we denote samples with the same labels as positive
samples, and samples with different labels as negative samples.
Nyi is the set of indices of positive samples with the same label
as yi in an episode, |Nyi | is its cardinality, and τ is a scalar
temperature coefficient.
As in (3), d(zi , zk ) denotes the similarity between the ith
and kth samples in the feature embedding space, zk (k ∈ Nyi )
denotes the samples from the same cluster as zi . The objective of
LFCL and Lzi is to narrow the instance-level distance between
samples with the same label, i.e., d(zi , zk ), and enlarge those
/ Nyi . Consequently, the
with different labels, i.e., d(zi , zq ), q ∈
samples of each category will form a compact cluster Ci with
lower variance, and the boundaries between different clusters
will be enlarged with a higher coupling degree. This will capture
differentiated features and facilitate the following classification
task to obtain more accurate class prototypes, which are evaluated in Section V-E.
Control of temperature coefficient: The temperature coefficient is used to adjust the degree of attention paid to hard samples
in contrastive loss (3). The lower the temperature coefficient
is, the more attention will be paid to similar samples. But
for supervised contrastive learning, the category information is
known. To learn the embedding space with clearer boundaries,

SUN et al.: SPACE DECOUPLED PROTOTYPE LEARNING FOR FEW-SHOT ATTACK DETECTION IN CYBER–PHYSICAL SYSTEMS

we design a CII technique to inject label-specific features into
the FCL module so that the model will pay more attention to
the category-related common features instead of the distinction
between similar samples. The CII can be defined as follows:

1/β yi = yk
CII (i, k) =
(4)
1/τ, yi = yk
where 0 < τ < β. CII assigns a lower temperature coefficient β
to positive samples’ pairs, resulting in the repulsion strength of
the anchor toward positive samples being lower compared with
negative samples. Then, the CII is multiplied by the similarity
score between sample pair, so Lzi in (3) can be converted to

−1
exp (d (zi , zk ) /τ )
.
Lz i =
log N
|Nyi | − 1
q=1 exp (d (zi , zq ) ∗CII (i, q))
k∈Nyi

(5)
By setting a small penalty rate of 1/β for the positive sample
pair, the unique representations of different samples can be
learned and can avoid the characteristics of positive samples
from being too similar.
C. Stage 2: Decoupled Prototype Generation
Considering the prevalent issues of prototype-based FSL, in
which prototypes tend to overlap and exhibit a high degree of
coupling, we posit the following hypothesis.
Hypothesis 2. PCL can improve the degree of intraclass
aggregation and reduce the coupling degree between prototypes.
Based on Hypothesis 2, we design a mutual information
maximization (InfoMax) training objective to treat normal and
attack samples as contrastive views to alleviate that problem.
During the training stage, we maximize the mutual information
between the same samples in query set and the corresponding
prototype, which is generated based on the samples in support
set, while penalizing other samples that do not belong to the prototype. In this way, samples from the query set also participate
in generating prototypes. Theoretically, incorporating both the
query set and the support set into the fine-tuning prototype is
beneficial to obtain more accurate prototypes because the more
samples involved in the prototype generation, the more accurate
the prototype will be [9].
Therefore, we formalize the PCL as an InfoMax and
prototype-based classification task. The proposed DPL-FSAD
is forced to learn a multivariate classified F partitioning the embedding space according to the classes. For the few-shot attack
detection task, introducing the multivariate classified function
F cannot only alleviate the problem of inaccurate mean-based
prototype computation but also simplify the whole training
mechanism. That is, F can be approximated as a simple crossentropy implementation of the InfoMax objective. Additionally,
to improve the generalization ability and avoid overfitting, a
regularization term and orthogonal constraints are designed to
enhance the internal compactness of prototypes and reduce the
coupling degree between prototypes.
Given the prototype of class i, i.e., Ci , the prototype contrastive loss can be formalized as the approximate mutual information I(Ci , TrQ ) between all the samples in query set and the

12355

prototype vector
I (Ci , TrQ ) ≥ E [log (d (Ci , xin ))] + E [log (1 − d (Ci , xnot ))]
(6)
where E denotes the expectation, and xin and xnot denote the
samples in the query set TrQ that in Ci or not in Ci . d(Ci , x)
denotes the similarity between Ci and x; here, we choose the dot
product as the metric, i.e., d(Ci , x) = Ci · x. Then, the InfoMax
loss for prototype Ci can be defined as follows:
−1 
L (Ci ) =
log (d (Ci , xin ))
|Qin |
xin ∈Qin

−

1
|Qnot |



log (1 − d (Ci , xnot ))

(7)

xnot ∈Qnot

where {Qin , Qnot } ⊂ TrQ denotes the samples that belong to Ci
and the samples that not belong to Ci , respectively. Thus, for N way k-shot attack detection task, the final prototype contrastive
loss can be defined as the sum of the InfoMax losses of the N
prototypes
1 
L (Ci ) .
(8)
LPCL =
N
Intuitively, minimizing the InfoMax loss (mutual information) is equivalent to narrowing the distance between the sample
and its prototype and enlarging the distance between the sample
and other prototypes, resulting in a more compact prototype
embedding space with a larger margin between classes. Thus,
the deviation of the prototype from the true center of the samples
is reduced, refer to Section V-E for more detail.
Distance-based regularization term: Since industry (such as
smart manufacturing plants) is sensitive to FAR, overfitting is
usually an issue to consider in a few-shot scenario. To overcome
this issue, we design a regularization term based on the distance
between the sample feature embedding r and the corresponding
prototype C to improve the generalization ability of the model.
This distance-based regularization term is defined as follows:
Lregu = D (r, C) .

(9)

Lregu can further improve the performance of the classifier
due to the following reasons.
1) It enables the sample features of the same class distribute
more compactly, which can implicitly enlarge the margin
between different classes and, therefore, boosting the
classification.
2) LPCL emphasizes the separation of prototypes, thus by
combining LPCL and Lregu together, we can learn intraclass compact and interclass distinctive feature embeddings.
Orthogonal constraint: As shown in Fig. 1(b), the neighborhoods of prototypes learned may overlap with each other, which
make it difficult to learn classification boundaries with high discriminative power. To solve this issue, we propose Hypothesis 3
as follows.
Hypothesis 3. The prototype orthogonal constraint can improve the interclass sparsity of the classifier’s spatial distribution and reduce the degree of overlapping.

12356

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

Algorithm 1: Training process of the proposed model DPLFSAD
Input: A set of normal signal samples
Dnor = {(xnori , ynori )|i = 1, 2, . . . , Nnor }.
A set of attack samples
Datt = {(xatti , yatti )|i = 1, 2, . . . , Natt }
Output: A trained attack detection model DPL-FSAD
1: Initialize hyperparameter epoch E, batch size B, loss
threshold ε, hyperparameter τ , β, λ1 , λ2
2: for epoch =1 to E do
3:
for each episode do
4:
Choose N classes with K samples from Dnor and
Datt to build support set TrS
5:
Choose N classes with K samples from Datt to build
query set TrQ
6:
for xq in TrQ do
7:
Transform xq into feature embedding rq by (1)
8:
for xs in TrS do
9:
Transform xs into feature embedding rs by (1)
10:
Calculate the feature contrastive loss LFCL by (2)
and (5)
11:
for k=1 to N do
12:
Calculate the prototype Ck of class k using rs by
(11)
13:
Calculate the prototype contrastive loss LPCL
based on rq and Ck by (8)
14:
for rj in rq do
15:
Calculate the regularization term Lregu using (9)
16:
for k =1 to N − 1 do
17:
Calculate the orthogonal loss Lorth between Ck
and Ck+1 by (10)
18: Update DPL-FSAD to minimize LDPL−FSAD by (12)
19: if LDPL−FSAD < ε then
20:
break
21: return DPL-FSAD

The orthogonal constraint enforces the prototype embedding
to be orthogonal to each other, that is, their inner product is
approaching 0. This increases the interclass sparsity because if
two prototypes are orthogonal, their projections on a dimension
will not overlap. Furthermore, under orthogonal constraints, to
maximize the interclass distance, the optimization algorithm
will automatically adjust the prototype embedding to separate
them as much as possible, thereby reducing the overlap between
different categories.
According to Hypothesis 3, the correlation of different categories can be reduced by prototype space decoupling via the
orthogonal constraint. To impose the orthogonal constraint, we
first map the sample features to the prototype space by matrix
mapping, calculate the mean of the feature maps to obtain the
prototype embedding C, and then calculate the dot product
between the prototypes and make it approximate to zero so that
the prototype spaces are orthogonal to each other. The prototype
orthogonal loss function is defined as follows:

Ci · Cj
(10)
Lorth (M ) =
i,j∈[1,N ],i=j

where M is a matrix to map each sample from feature embedding
space to prototype embedding space and trained according to the
prototype orthogonal constraint.
Prototype generation: For the proposed model, we generate
prototypes based on feature mapping and average operations.
Given a minibatch of k features {ri , i ∈ [1, k]}, the support set
TrS , the feature extractor first embeds all samples into the latent
feature space. Then, feature embedding of the same class is
mapped by a matrix M and aggregated into a prototype C in
the prototype embedding space. Typically, it is calculated as an
average of those embedding
k

C = Ω (·) =

1
M ∗ ri
k i=1

(11)

where k denotes the number of samples per class in TrS and ri
is the feature embedding of the ith sample.
D. Learning Strategy
To achieve efficient training performance, the overall loss of
the proposed DPL-FSAD model is a combination of the four
losses introduced above, which can be formulated as follows:
LDPL−FSAD = LFCL + LPCL + λ1 Lregu + λ2 Lorth

(12)

where λ1 and λ2 are the coefficients to balance the loss of regularization and orthogonal terms, respectively. The training process
of the proposed model DPL-FSAD is shown in Algorithm 1, and
the parameters are learned via minimizing LDPL−FSAD .
E. Attack Detection With DPL-FSAD
During the test stage, given the learned prototype embedding,
the model first extracts the feature of the test samples and then
predicts the category of the sample based on the similarity
between the feature embedding and each prototype.
In detail, we measure the similarity of samples and prototypes
by the distance between them. Thus, the probability p(x ∈ yi |x)
that x belongs to the prototype Ci should be proportional to the
negative of the distance between them. To satisfy the property
that probability must be normalized and nonnegative, we define
p(x ∈ yi |x) as follows:
exp (−D (f (x) , Ci ))
p (x ∈ yi |x) = 
j exp (−D (f (x) , Cj ))

(13)

where D (f (x), Ci ) = f (x) − Ci 22 represents the Euclidean
distance between sample x and class yi . Based on this probability, the overall prediction error can be measured via the negative
log probability
Lpred = − log p (x ∈ yi |x) .

(14)

The attack type of the input sample x can be identified via the
closest prototype with the highest probability p(xࢠyi |x).
V. EXPERIMENTS AND ANALYSIS
A. Experimental Settings
Datasets: To verify the effectiveness of our proposed model
on attack detection, we conducted a plenty of experiments on

SUN et al.: SPACE DECOUPLED PROTOTYPE LEARNING FOR FEW-SHOT ATTACK DETECTION IN CYBER–PHYSICAL SYSTEMS

TABLE II
STATICS OF THE THREE PUBLIC DATASETS

four public datasets, i.e., UNSW-NB15 [29], a network security
detection dataset upgraded from the KDD CUP99 dataset (NSLKDD) [30], TON_IoT [31], and ERENO IEC-61850 [32]. The
details of the four datasets are shown in Table II, which were
preprocessed accordingly for few-shot settings.
UNSW-NB15 was created by the Intelligent Security Group
of Australia and widely used to develop approaches in different
systems, such as the Internet of Things (IoT), SCADA, and
Industrial IoT. The IXIA PerfectStorm tool is utilized as an
attack traffic generator along with normal traffic, and the attack
behavior is nourished from the CVE site for the purpose of a
real representation of a modern threat environment. These attack
behaviors contain nine types of network attacks that may result
in data leakage, tampering, illegal control, or service interruption
of CPS systems.
NSL-KDD is an upgraded version of the KDD CUP99 [30]
dataset, addressing the inherent issues by incorporating data
from the DARPA ’98 IDS Evaluation Program. It utilizes the
same environment (U.S. Air Force LAN), and the simulation
ended with 41 features for each connection along with the
class label using the Bro-IDS tool. NSL-KDD offers a comprehensive benchmark for intrusion detection research. Notably,
both training and testing sets contain four simulated attacks,
including denial of service (Dos), probe, remote-to-local (R2L),
and user-to-root (U2R).
TON_IoT is a new generation Industry 4.0 and Industrial IoT
dataset collected from a realistic and large-scale network designed at the Cyber Range and IoT Labs, UNSW Canberra @ the
Australian Defence Force Academy. The whole dataset covers
nine attack families, including heterogeneous data sources collected from telemetry datasets of IoT and IIoT sensors, operating
systems datasets of Windows 7 and 10, as well as Ubuntu 14 and
18 TLS and network traffic datasets. The datasets were gathered
in parallel processing to collect several normal and cyberattack
events from network traffic, Windows audit traces, Linux audit
traces, and telemetry data of IoT services.
ERENO IEC-61850 is a simulation of an existing Brazilian
transmission line and generated more than 4.4 GB of data containing seven attack types that target the electric grid substations
networks based on the IEC-61850 standards. These attacks may

12357

compromise the IEC-61850 communication protocols and cause
improper functioning of the power system. It was collected by
Quincozes et al. [32] via simulating an electric grid substation
network traffic to produce representative features using an extensible tool ERENO.
Comparative models: To validate the advancement of DPLFSAD, four FSL methods (i.e., FSL-SCNN [6], AnoS_Net [24],
DeROL[25], and Siam_IDS [26]), three deep-learning-based
methods (i.e., VLSTM [3], AE_LSTM [27], and LuNet [32]),
and two semisupervised learning methods (i.e., SLA-VAE [16]
and MDAE-DT [17]) were selected for comparison.
Implementation details: The classifier of the model is implemented based on the PN. For the N -way k-shot attack detection
task, we set k= {1, 5, 10} in all experiments and select the best
results. The ratio of samples in support set TrS and query set
TrQ is set to 1:1. We set the initial learning rate to 0.001, choose
stochastic gradient descent as the optimizer, and iterate for 1000
epochs to train the model. Empirically, we choose λ1 and λ2
from {0.1, 0.05, 0.01, 0.005, 0.001} and set λ1 = 0.001 and
λ2 = 0.005 for the best performance.
Evaluation metrics: We apply and calculate four widely used
metrics, precision, recall, F1, and FAR depending on whether
normal and abnormal samples have been recognized correctly or
not, to prove the detection performances of the above methods.
Besides, we introduce the following two metrics, i.e., variance
σ and coupling degree c to measure the degree of intraclass
aggregation and coupling degree between different categories,
respectively, in the embedding space
σi = var (Ci )

(15)

|cov (Ci , Cj )|
c= √
√
σi × σj

(16)

where var(Ci ) denotes the variance of the class i, and
cov(Ci , Cj ) denotes the covariance of the classes i and j. The
range of c is [0, 1], namely, the larger the value of c, the higher
the coupling degree between two classes.
Feature selection: To avoid overfitting and curse of dimensionality, we performed feature selection before training by
using the SelectFromModel interface of sklearn, which selects
features by assessing their importance to the model performance.
Since this article focuses on the classification task, we used
SVM.LinearSVC as the sparse estimator and L1 norm as the
penalty term for feature selection. With this setting, the results
after feature selection for these four datasets were UNSW-NB15
with 31 features, NSL-KDD with 26 features, TON_IoT with 25
features, and ERENO IEC-61850 with 32 features.
B. Attack Detection Evaluation
Robustness evaluation: To evaluate the robustness of our
proposed DPL-FSAD method on detecting cyberattacks, we
conduct comparative experiments with nine models on UNSWNB15, NSL-KDD, TON_IoT, and ERENO IEC-61850 datasets.
Table III illustrates the remarkable detection capabilities of
DPL-FSAD on the four datasets, surpassing previously selected benchmark models. Impressively, DPL-FSAD achieves
the highest precision, recall, F1-score, and FAR on all four

12358

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

TABLE III
STATICS OF THE FOUR PUBLIC DATASETS

datasets. On UNSW-NB15 dataset, although achieving comparable performance in the recall metric with VLSTM, DPL-FSAD
outperforms the suboptimal model SLA-VAE by a significant
margin, marking an absolute improvement of 4.3% in precision,
2.3% in F1-score, and a reduction of 2.0% in FAR. On NSL-KDD
dataset, DPL-FSAD is significantly better than other comparison models. Compared with the suboptimal model SLA-VAE,
DPL-FSAD showcases an absolute improvement of 4.4% in precision and 2.9% in the F1-score. Moreover, our model exhibits
a notable reduction of 1.2% in FAR. On TON_IoT and ERENO
IEC-61850 datasets, compared with the suboptimal model, our
DPL-FSAD achieves an average improvement of 3.75% in
precision, 2.7% in recall, 3.2% in F1-score, and a reduction
of 4.9% in FAR, implying the effectiveness of the DPL-FSAD
in industrial CPS traffic attack detection. Overall, DPL-FSAD
outperforms the competing methods across all evaluated metrics,
demonstrating its superior robustness in detecting seen attacks.
Generalization evaluation: To verify the generalization ability of DPL-FSAD for detecting unseen attacks, taking the
UNSW-NB15 dataset as an example, we randomly excluded
two attacks (i.e., Analysis and Worms) from the training set
and retained both attacks in the testing set. Then, the two sets
were used to train and test the model, respectively. As a result,
an F1-score of 94.5% was obtained on detecting these two
types of attacks, which demonstrates the generalization ability
of DPL-FSAD.
C. Impact of Regularization Factor
As the proposed regularization term enhances the cohesion
of the prototypes, a higher level of cohesion leads to improved model performance. Hence, we conducted additional
experiments to examine the impact of the regularization factor
on model performance, as presented in Table III. The results
demonstrate that the model’s performance consistently improves
with decreasing values of the regularization factor. It reaches its
optimal point at 0.001 and, subsequently, declines as the regularization factor decreases further. This observation suggests that
there exists a nonlinear relationship between prototype cohesion
and the regularization term, which warrants future investigation.
D. Ablation Study
Ablation experiments are carried out on UNSW-NB15, NSLKDD, TON_IoT, and ERENO IEC-61850 datasets to verify the

necessity and effectiveness of each module of the proposed
model in identifying attacks. We compare five variants of the
proposed model:
1) DPL-FSAD (ours);
2) w./o FCL: without feature contrastive learning;
3) w./o PCL: without prototype contrastive learning;
4) w./o Regu: without regularization constraint;
5) w./o Ortho: without orthogonal constraint.
Table IV presents the results of ablation experiments. As can
be seen from the table, each of our variants can effectively help
the model to obtain better performance. Compared with the
FSL-SCNN model from Table III, we see that all variants of
DPL-FSAD can outperform FSL-SCNN except for w./o Regu,
which indicate that the regularization term is essential for high
performance. From the metrics of variance σ and coupling
degree c, we can find that the absence of the regularization term
leads to an increase in the variance and coupling degree; this
exactly explains the decrease in attack detection performance.
In addition, all these variants without FCL, PCL, and orthogonal constraint show a decrease in F1 and an increase in FAR,
as well as an increase in σ and c. It proves that these modules
are necessary and can promote the performance of the model.
In these three variants, the absence of PCL module poses the
biggest impact on model performance, and the increase of σ and
c demonstrates that the reason for the performance degradation
may be that the intraclass dispersion and interclass coupling
become stronger.
In summary, the ablation results confirm the remarkable
capabilities of our proposed DPL-FSAD model. It excels in
accurately learning distinctive features, reducing the coupling
degree of prototypes, and delivers impressive performance enhancements, particularly in scenarios with few labeled samples.
These findings underscore the effectiveness and potential of our
model in the field of attack detection in industrial CPS.
E. Hypothesis Evaluation
To demonstrate the validity of the three hypotheses, as proposed in Section IV, we measured the degree of intraclass
aggregation and the degree of interclass dispersion by the variance metric σ and the coupling degree c in Table III.
As shown, without the FCL module, the variance σ and the
coupling degree c increased by 15.5% and 100.5% on average,

SUN et al.: SPACE DECOUPLED PROTOTYPE LEARNING FOR FEW-SHOT ATTACK DETECTION IN CYBER–PHYSICAL SYSTEMS

12359

TABLE IV
RESULTS OF ABLATION STUDY (F1 AND FAR ARE MEASURED IN PERCENTAGES)

Fig. 4.

Feature embedding visualization based on PCA. (a) AnoS_Net. (b) DeROL. (c) Siam_IDS. (d) FSL-SCNN. (e) DPL-FSAD.

which proves that FCL is helpful to reduce the coupling degree
and variance. The lower variance indicates that the extracted
features are more significant, and the lower coupling degree
indicates that the features are more distinctive, these confirm
the feasibility of Hypothesis 1.
Second, when without the PCL module, the variance σ and
coupling degree c increased by 30.1% and 110.9% on average,
which proves that PCL can significantly reduce the degree of
intraclass aggregation and the interclass coupling degree (Hypothesis 2), and the effect is more significant than that of FCL
module.
Finally, compared with the variant without Ortho, the variance
σ and coupling degree c of the proposed model reduced by 21.4%
and 23.8% on average, which indicates that the orthogonal
constraint on the prototypes can improve the sparsity of the
spatial distribution; it can also promote the degree of intraclass
aggregation; the lower variance and coupling degree are helpful
to mitigate the overlapping of neighborhoods (Hypothesis 3).

F. Feature Visualization
To further verify the decoupling effect of the proposed model,
the feature representations of the compared FSL methods are
visualized by performing dimensionality reduction via PCA
on the NSL-KDD dataset, as shown in Fig. 4. The average
intraclass variance and interclass coupling of the four models
are as follows: AnoS-Net (σ= 0.45 and c= 0.332), DeROL
(σ= 0.44 and c= 0.325), Siam_IDS (σ= 0.43 and c= 0.319),
FSL-SCNN (σ= 0.38 and c=0.207), and DPL-PSAD (σ=
0.34 and c= 0.127). It demonstrates that the proposed model
DPL-FSAD can effectively reduce the variance of the intraclass
distribution (by 10.5% compared with FSL-SCNN). In addition,
it reduces the coupling degree between prototypes (38.6% lower
than FSL-SCNN), thereby making different categories sparsely

TABLE V
INFERENCE TIME (S) OF THE FOUR FSL ATTACK DETECTION METHODS ON
UNSW-NB15 DATASET

distributed, this is beneficial to distinguish between different
attack types.
G. Complexity Analysis
As most terminal devices in CPS are resource constrained,
high performance and low overhead are usually priorities; computational complexity is an important indicator to measure
whether a detection model is practical for integration into realtime IDS systems. To evaluate the computational complexity of
the model, we calculated the inference time (taking the average
of 100 experiments) of the proposed model and four few-shot
detection models on the UNSW-NB15 and NSL-KDD datasets,
as shown in Table V. It can be seen that the proposed model can
quickly complete the detection task, and the inference time on
both datasets is better than the other four methods. This observation indicates that our method is more suitable for deployment
in resource-constrained CPS devices.
VI. CONCLUSION
To ensure the network security of industrial CPSs, this article
proposed a new model DPL-FSAD to address the problems of
existing attack detection methods with high coupling degrees
and fuzzy boundaries between attack categories. Comparative
experiments as well as ablation studies were conducted with

12360

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

existing advanced attack detection algorithms and several traditional machine learning methods on TON_IoT, UNSW-NB15,
and NSL-KDD in few-shot settings. The experimental results
showed that our proposed method outperforms the existing
models in terms of precision, recall, F1-score, and FAR metrics. It validated the effectiveness of the three hypotheses and
demonstrated the ability of DPL-FSAD for extracting distinctive
attack features, space decoupling of different prototypes, and
mitigating the fuzzy boundaries, which contribute to the robust
detection of attack signals in industrial CPS environment in
few-shot cases.

Therefore, through FCL, the significance level of the key
features can be improved by maximizing the eigenvalues of
positive samples and negative samples.
Proof of Hypothesis 2.
1) Intraclass aggregation can be measured by the average
expectation of the similarity between intraclass samples
and different class prototypes. Based on the prototype
contrastive loss defined in formula (7), since both the left
and right terms of the loss are positive, to minimize L(Ci ),
the left and right terms need to be minimized separately

min

APPENDIX
Proof of Hypothesis 1.
1) Since log is an increasing function, to minimize Lzi in fori ,zk )/τ )
mula (3), we need to maximize log Nexp(D(z
,
exp(D(z ,z )/τ )
q=1

i

q

i.e., maximize the numerator term exp(D(zi , zk )/τ ) and

minimize the denominator term N
q=1 exp(D(zi , zq )/τ )
max {exp (D (zi , zk ) /τ )} ⇒ max {D (zi , zk )}
= max {zi · zk } = max {|zi | |zk | cos zi , zk }
⎧
⎫
N
⎨
⎬
min
exp (D (zi , zq ) /τ ) ⇒ min {D (zi , zq )}
⎩
⎭

⎧
⎨ −1
⎩ |Qin |

⇒ max

⇒ max

⇒ max

q=1

= min {zi · zq } = min {|zi | |zq | cos zi , zq } .
Under normalization condition, |zi | = |zk | = |zq | = 1, max
{|zi ||zk | cos zi , zk } = max{cos zi , zk }, i.e., to maximize
the similarity between the features of in-class samples
and capture the common features; min{|zi ||zq | cos zi , zq } =
min{cos zi , zq } = max{1 − cos zi , zq }, i.e., to minimize the
similarity and maximize the distance between the features of
different classes of samples. Therefore, for negative samples,
the model is more inclined to capture differentiated features that
are distinguishable from positive samples.
2) The significance level of a feature can be represented by
the eigenvalue λ corresponding to the feature vector.
z ·z T +z ·z T
max{zi · zk }
⇒
max
As
zi · zk ≤ i i 2 k k ,
{sup(zi · ziT + zk · zkT )} ⇒ max{zi · ziT } and max{zk · zkT },
zi and zk belong to the same category.
As zi · ziT is a square matrix, max{zi · ziT } ⇒ max
{det(zi · ziT )} ⇒ max{ nj=1 λi i }.
Similarly, max{zk · zkT } ⇒ max{ nj=1 λk }, i.e., the positive
sample eigenvalues can be maximized via orthogonal constraints.
z ·z T +z ·z T
In addition, as zi · zq ≥ − i i 2 q q , zi and zq belong to
different categories

min {zi · zq } ⇒ max inf zi · ziT + zq · zqT


⇒ max zi · ziT and max zq · zqT .
As zq · zqT is a square matrix, max{zq · zqT } ⇒
max{det(zq · zqT )} ⇒ max{ nj=1 λq }, i.e., to maximize
the eigenvalues of negative samples feature vectors.



⇒ max

⎧
⎨ 
⎩

log (d (Ci , xin ))

xin ∈Qin

⎧
⎨ 
⎩

d (Ci , xin )

xin ∈Qin

⎧
⎨ 
⎩
⎧
⎨
⎩

log (d (Ci , xin ))

xin ∈Qin

Ci · xin

xin ∈Qin

Ci ·

xin

xin ∈Qin

⎭

⎫
⎬
⎭

⎫
⎬
⎭

⎫
⎬
⎭
⎫
⎬



⎫
⎬

⎭

⇒ max {Ci · E (xin )} .

Therefore, for the cluster of prototype Ci , we only need to
maximize the similarity between the sample expectation E(xin )
and the prototype Ci , i.e., to maximize the degree of intraclass
aggregation.
2) Prototype coupling degree can be measured by formula
(16), where Ci and Cj denote the prototypes of different
categories, respectively, c denotes the coupling degree of
prototypes, c ∈ [0, 1], c = 1 exist only if i = j.
If i = j, to minimize the right term of formula (7)

min L (Ci ) ⇒ min

⎧
⎨

1
−
⎩ |Qnot |
⎧
⎨

1
⇒ max
⎩ |Qnot |
⎧
⎨

1
⇒ max
⎩ |Qnot |
⇒ min

⇒ min

⎧
⎨

1
⎩ |Qnot |
⎧
⎨

1
⎩ |Qnot |



log (1 − d (Ci , xnot ))

xnot ∈Qnot



log (1 − d (Ci , xnot ))

xnot ∈Qnot



(1 − d (Ci , xnot ))

xnot ∈Qnot



d (Ci , xnot )

xnot ∈Qnot


xnot ∈Qnot

Ci · xnot

⎫
⎬
⎭

⎫
⎬
⎭

.

⎫
⎬
⎭

⎫
⎬
⎭

⎫
⎬
⎭

SUN et al.: SPACE DECOUPLED PROTOTYPE LEARNING FOR FEW-SHOT ATTACK DETECTION IN CYBER–PHYSICAL SYSTEMS
Ci 
For any Cj = |Q
where i = j,
xj ∈Qj xj ∈ Qnot ,
j|
min L(Ci ) ⇒ min{Ci · Cj } ⇒ min{c}, i.e., to reduce the
coupling degree between prototypes.
Proof of Hypothesis 3.
1) To minimize Lorth (M ) in formula (10), we have
⎧
⎫
⎨
⎬

min{Lorth (M )} ⇒ min
Ci · Cj
⎩
⎭
i,j∈[1,N ],i=j

⇒ max

⎧
⎨
⎩


i,j∈[1,N ],i=j

(1 − Ci · Cj )

⎫
⎬
⎭

i.e., the similarity of different types of prototypes is minimized.
As the intraclass samples are aggregated near the prototypes,
i.e., d(Ci , xin ) → 0; therefore, the sparsity between different
classes increases.
2) Interclass overlapping can be measured by the distance
between samples of different classes
⎧
⎫
⎨
⎬

Ci · Cj
min{Lorth (M )} ⇒ min
⎩
⎭
i,j∈[1,N ],i=j
⎧
⎞⎫
⎛

kj
ki
⎬
⎨ 1 

1
M ∗ ri · ⎝
M ∗ rj ⎠
⇒ min
⎭
⎩ ki
kj j=1
i=1
⎧
⎞⎫
⎛

kj
ki
⎨ 
⎬

⎝
⇒ min
ri ·
rj ⎠
⎩
⎭
i=1
j=1
⎧⎛
⎞⎫
kj
ki 
⎨ 
⎬
⇒ min ⎝
ri · rj ⎠
⎩
⎭
i=1 j=1
⎧
⎫
kj
ki 
⎨
⎬
⇒ max
(1 − ri · rj ) .
⎩
⎭
i=1 j=1

The similarity between different types of samples is minimized, i.e., the distance between different types of samples is
maximized; thus, the degree of overlapping between different
classes is reduced.
REFERENCES
[1] L. Hou, Y. Li, W. Luo, and H. Sun, “Adaptive tracking control of switched
cyber-physical systems with cyberattacks,” Appl. Math. Comput., vol. 415,
2022, Art. no. 126721.
[2] A. Humayed, J. Lin, F. Li, and B. Luo, “Cyber-physical systems security—
A survey,” IEEE Internet Things J., vol. 4, no. 6, pp. 1802–1831, Dec. 2017.
[3] X. Zhou, Y. Hu, W. Liang, J. Ma, and Q. Jin, “Variational LSTM enhanced
anomaly detection for industrial big data,” IEEE Trans. Ind. Inform.,
vol. 17, no. 5, pp. 3469–3477, May 2021.
[4] J. Slay and M. Miller, “Lessons learned from the Maroochy water breach,”
in Proc. Int. Conf. Crit. Infrastruct. Protection, 2007, pp. 73–82.
[5] S. M. Kasongo and Y. Sun, “A deep long short-term memory based
classifier for wireless intrusion detection system,” ICT Exp., vol. 6, no. 2,
pp. 98–103, 2020.
[6] X. Zhou, W. Liang, S. Shimizu, J. Ma, and Q. Jin, “Siamese neural
network based few-shot learning for anomaly detection in industrial cyberphysical systems,” IEEE Trans. Ind. Inform., vol. 17, no. 8, pp. 5790–5798,
Aug. 2021.
[7] S. Huang et al., “A gated few-shot learning model for anomaly detection,”
in Proc. Int. Conf. Inf. Netw., 2020, pp. 505–509.

12361

[8] Y. Tian, Y. Wang, D. Krishnan, J. B. Tenenbaum, and P. Isola, “Rethinking
few-shot image classification: A good embedding is all you need?,” in
Proc. Eur. Conf. Comput. Vis., 2020, pp. 266–282.
[9] J. Liu, L. Song, and Y. Qin, “Prototype rectification for few-shot learning,”
in Proc. Eur. Conf. Comput. Vis., 2020, pp. 741–756.
[10] O. A. Beg, T. T. Johnson, and A. Davoudi, “Detection of false-data
injection attacks in cyber-physical DC microgrids,” IEEE Trans. Ind.
Inform., vol. 13, no. 5, pp. 2693–2703, Oct. 2017.
[11] Q. Sun, K. Zhang, and Y. Shi, “Resilient model predictive control of cyber–
physical systems under DoS attacks,” IEEE Trans. Ind. Inform., vol. 16,
no. 7, pp. 4920–4927, Jul. 2020.
[12] F. Li, Y. Shi, A. Shinde, J. Ye, and W. Song, “Enhanced cyber-physical
security in Internet of things through energy auditing,” IEEE Internet
Things J., vol. 6, no. 3, pp. 5224–5231, Jun. 2019.
[13] M. Kravchik and A. Shabtai, “Detecting cyber attacks in industrial control
systems using convolutional neural networks,” in Proc. Workshop CyberPhysical Syst. Secur. Privacy, 2018, pp. 72–83.
[14] N. Moustafa and J. Slay, “The evaluation of network anomaly detection
systems: Statistical analysis of the UNSW-NB15 data set and the comparison with the KDD99 data set,” Inf. Secur. J., Glob. Perspective, vol. 25,
no. 1/3, pp. 18–31, 2016.
[15] H. Pearce, S. Pinisetty, P. S. Roop, M. M. Y. Kuo, and A. Ukil, “Smart
I/O modules for mitigating cyber-physical attacks on industrial control systems,” IEEE Trans. Ind. Inform., vol. 16, no. 7, pp. 4659–4669,
Jul. 2020.
[16] T. Huang, P. Chen, and R. Li, “A semi-supervised VAE based active anomaly detection framework in multivariate time series for
online systems,” in Proc. ACM Web Conf., 2022, pp. 1797–1806,
doi: 10.1145/3485447.3511984.
[17] M. Zheng, J. Man, D. Wang, Y. Chen, Q. Li, and Y. Liu, “Semisupervised multivariate time series anomaly detection for wind turbines
using generator SCADA data,” Reliab. Eng. Syst. Saf., vol. 235, Jul. 2023,
Art. no. 109235, doi: 10.1016/j.ress.2023.109235.
[18] H. Cho, J. Seol, and S.-G. Lee, “Masked contrastive learning for anomaly
detection,” in Proc. 30th Int. Joint Conf. Artif. Intell., 2021, pp. 1434–1441.
[19] R. D. Hjelm et al., “Learning deep representations by mutual information
estimation and maximization,” in Proc. Int. Conf. Learn. Representations,
2019, pp. 1–24.
[20] O. Kopuklu, J. Zheng, H. Xu, and G. Rigoll, “Driver anomaly detection:
A dataset and contrastive learning approach,” in Proc. IEEE Winter Conf.
Appl. Comput. Vis., 2021, pp. 91–100.
[21] T. Shenkar and L. Wolf, “Anomaly detection for tabular data with internal
contrastive learning,” in Proc. 10th Int. Conf. Learn. Representations,
2022, pp. 1–26.
[22] Y. Wang, Q. Yao, J. T. Kwok, and L. M. Ni, “Generalizing from a few
examples: A survey on few-shot learning,” ACM Comput. Surv., vol. 53,
no. 3, 2020, Art. no. 63.
[23] M. Uchida, “Human error tolerant anomaly detection based on timeperiodic packet sampling,” Knowl.-Based Syst., vol. 106, pp. 242–250,
2016.
[24] R. Kale and L. L. V. Thing, “Few-shot weakly supervised cybersecurity
anomaly detection,” Comput. Secur., vol. 130, 2023, Art. no. 103194.
[25] A. Puzanov, S. Zhang, and K. Cohen, “Deep reinforcement one-shot
learning for artificially intelligent classification in expert aided systems,”
Eng. Appl. Artif. Intell., vol. 91, 2020, Art. no. 103589.
[26] P. Bedi, N. Gupta, and V. Jindal, “Siam-IDS: Handling class imbalance
problem in intrusion detection systems using Siamese neural network,”
Procedia Comput. Sci., vol. 171, pp. 780–789, 2020.
[27] I. A. Khan, M. Keshk, D. Pi, N. Khan, Y. Hussain, and H. Soliman,
“Enhancing IIoT networks protection: A robust security model for attack
detection in Internet industrial control systems,” Ad Hoc Netw., vol. 134,
2022, Art. no. 102930.
[28] P. Wu and H. Guo, “LuNET: A deep neural network for network intrusion
detection,” in Proc. IEEE Symp. Ser. Comput. Intell., 2019, pp. 617–624.
[29] N. Moustafa and J. Slay, “UNSW-NB15: A comprehensive data set for
network intrusion detection systems (UNSW-NB15 network data set),” in
Proc. Mil. Commun. Inf. Syst. Conf., 2015, pp. 1–6.
[30] M. Tavallaee, E. Bagheri, W. Lu, and A. A. Ghorbani, “A detailed analysis
of the KDD CUP 99 data set,” in Proc. IEEE Symp. Comput. Intell. Secur.
Defense Appl., 2009, pp. 1–6.
[31] A. Alsaedi, N. Moustafa, Z. Tari, A. Mahmood, and A. Anwar, “TON_IoT
telemetry dataset: A new generation dataset of IoT and IIoT for data-driven
intrusion detection systems,” IEEE Access, vol. 8, pp. 165130–165150,
2020.
[32] S. E. Quincozes, C. Albuquerque, D. G. Passos, and D. Mossé, “ERENO: A
framework for generating realistic IEC–61850 intrusion detection datasets
for smart grids,” IEEE Trans. Depend. Secure Comput., pp. 1–15, 2023.

12362

IEEE TRANSACTIONS ON INDUSTRIAL INFORMATICS, VOL. 20, NO. 10, OCTOBER 2024

Haili Sun received the B.S. degree in information and computer science from Hainan University, Haikou, China, in 2013, and the M.S.
degree in computer technology in 2015 from
the School of Computer Science and Engineering, Huazhong University of Science and Technology, Wuhan, China, where she is currently
working toward the Ph.D. degree in cyberspace
security with the School of Cyber Security and
Engineering.
Her research interests include anomaly detection and security control of industrial IoT systems, and theory and
application of cyber-physical systems.

Yan Huang (Member, IEEE) received the M.S.
and Ph.D. degrees in computer science and
technology from the Huazhong University of Science and Technology, Wuhan, China, in 2016
and 2022, respectively.
Since 2022, he has been a Postdoctor with
the School of Artificial Intelligence and Automation, Huazhong University of Science and Technology. His research interests include knowledge graph embedding, knowledge inference,
and their application in object detection, cyber
security, and natural language processing.

Chunjie Zhou received the M.S. and Ph.D. degrees in control theory and control engineering
from the Huazhong University of Science and
Technology, Wuhan, China, in 1991 and 2001,
respectively.
He is currently a Professor with the School of
Artificial Intelligence and Automation, Huazhong
University of Science and Technology. His research interests include safety and security control of industrial control systems, theory and
application of networked control systems, and
artificial intelligence.

Lansheng Han received the B.S. degree from
Lanzhou University, Lanzhou, China, in 1995,
and the Ph.D. degree from the Huazhong University of Science and Technology, Wuhan,
China, in 2006, both in information security.
He is currently a Professor with the School
of Cyber Security and Engineering, Huazhong
University of Science and Technology, and the
Peng Cheng Laboratory, Shenzhen, China. His
research interests include computer virus, IoT
security, malicious code detection, and mobile
intelligent terminal security.

Hongle Liu received the B.S. degree in automation in 2022 from the Huazhong University of
Science and Technology, Wuhan, China, where
she is currently working toward the M.S. degree in cyber science and engineering with the
School of Cyber Security and Engineering.
Her current research focuses on software
security.

Juan Chen received the B.S. degree in information and computational science from Northeastern University, Boston, MA, USA, in 2021. She
is currently working toward the M.S. degree in
cyberspace security with the School of Cyber
Security and Engineering, Huazhong University
of Science and Technology, Wuhan, China.
Her current research focuses on malicious
behavior detection.

Xin Li received the B.S. degree in cyber science
and engineering in 2023 from the Huazhong
University of Science and Technology, Wuhan,
China, where he is currently working toward the
M.S. degree in cyber science and engineering
with the School of Cyber Science and Engineering.
His current research focuses on binary
vulnerability inversion and Java application
security.
PAPER_TEXT
