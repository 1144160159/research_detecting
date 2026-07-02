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
# [279] Poison-Resilient Anomaly Detection: Mitigating Poisoning Attacks in Semi-Supervised Encrypted Traffic Anomaly Detection
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
编号：279
题名：Poison-Resilient Anomaly Detection: Mitigating Poisoning Attacks in Semi-Supervised Encrypted Traffic Anomaly Detection
年份：2024
DOI：10.1109/tnse.2024.3397719
来源：IEEE Transactions on Network Science and Engineering
PDF：paper/10.1109_TNSE.2024.3397719.pdf
已有粗分类：加密流量分类与应用识别
二级关联：入侵检测与网络异常检测、其他AI安全与跨域异常检测
相关性：强相关，分数 15
已有代码状态：未发现；无

正文包信息：
- 正文来源：综合分析\_data\full_text_cache_plain\279.txt
- 原始字符数：70287
- 本次发送字符数：70287
- 是否截断：False

代码包：
未发现该论文对应的本地开源代码。

论文正文包开始：
<<<PAPER_TEXT
4744

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 5, SEPTEMBER/OCTOBER 2024

Poison-Resilient Anomaly Detection: Mitigating
Poisoning Attacks in Semi-Supervised Encrypted
Traffic Anomaly Detection
Zhangfa Wu , Huifang Li , Yekui Qian , Yi Hua , and Hongping Gan , Member, IEEE

Abstract—Semi-supervised encrypted traffic anomaly detection
models in zero-positive scenarios are susceptible to human labeling
errors or poisoning attacks, thereby compromising the stability and
reliability of the model. However, existing methods are insufficient
to address the challenge of reduced inter-class distance caused
by poisoning attacks and the inability of reconstruction error to
serve as a reliable detection criterion. To alleviate these challenges,
a framework called Poison-Resistant Anomaly Detection (PRAD)
is proposed to mitigate poisoning attacks and enhance anomaly
detection performance. Specifically, a feature encoding module
autoencoder-based is first designed that simultaneously leverages
the Amsgrad gradient descent algorithm and the warm-up strategy
to enhance the feature extraction and generalization capabilities,
thereby alleviating the reduction of inter-class distance. Additionally, a feature analysis module is introduced to measure the impact
of poisoning attacks on inter-class distance and the distribution
of reconstruction errors, which provides valuable prior information for subsequent anomaly detection tasks. Finally, an online
clustering-based anomaly detection algorithm that utilizes the extracted features and their corresponding reconstruction errors are
developed to address the issue of detection criteria. Experimental
results on public benchmark datasets demonstrate that PRAD exhibits significantly superior poison-resilient capabilities compared
to other semi-supervised anomaly detection methods in anomaly
detection tasks under poisoning attacks.
Index Terms—Encrypted traffic, online clustering, poisoning
attack defense, semi-supervised anomaly detection.

I. INTRODUCTION
HE encrypted communication protocols, while safeguarding user data privacy [1], pose challenges to conventional
anomaly detection techniques that operate on plaintext data [2],

T

Manuscript received 13 January 2024; revised 7 April 2024; accepted 29 April
2024. Date of publication 10 May 2024; date of current version 16 August 2024.
This work was supported in part by the Innovation Workstation of State Key
Laboratory of Intelligent Gaming under Grant ZBKF-23-03, and in part by the
Basic Research Programs of Taicang under Grant TC2022JC19. Recommended
for acceptance by Dr. Y. Wu. (Corresponding author: Huifang Li.)
Zhangfa Wu and Huifang Li are with the School of Electronic Information, Northwestern Polytechnical University, Xi’an 710129, China (e-mail:
zhangfa_wu2021100697@mail.nwpu.edu.cn; Lhuifang@nwpu.edu.cn).
Yekui Qian is with People’s Liberation Army Air Force Academy, Zhengzhou
450052, China (e-mail: qyk1129@163.com).
Yi Hua is with the School of Aeronautics, Northwestern Polytechnical University, Xi’an 710072, China (e-mail: yihua@mail.nwpu.edu.cn).
Hongping Gan is with the School of Software, Northwestern Polytechnical
University, Xi’an 710129, China (e-mail: ganhongping@nwpu.edu.cn).
Digital Object Identifier 10.1109/TNSE.2024.3397719

[3]. To detect anomalous behaviors in encrypted communications, researchers employ diverse anomaly detection methods
to identify data that exhibit significant deviations from the
majority of samples. These approaches help mitigate potential
risks and abnormal behaviors in communication networks, ensuring the security of communication systems and safeguarding
user privacy. Given the scarcity of abnormal data in real-world
scenarios and the difficulty in obtaining labeled samples due
to their concealment by normal data points. Semi-supervised
learning algorithms have emerged as a promising approach,
which require only a limited amount of labeled data and reduced
labor costs, offering a solid theoretical foundation for anomaly
detection in encrypted traffic.
Semi-supervised anomaly detection methods can be categorized into traditional anomaly detection methods and Deep
Learning (DL) methods. Traditional anomaly detection methods
typically begin by modeling the statistical characteristics of
normal data and subsequently identify anomalous data points by
detecting those that deviate significantly from this model. Examples of such methods include the density estimation method
LOF [4], the clustering method OC-SVM [5], probabilitybased estimation methods such as ECOD [6], COPOD [7],
etc., as well as ensemble learning anomaly detection methods
such as IForest [8], SUOD [9], LSCP [10], etc. In practical
applications, traditional anomaly detection methods often face
challenges in capturing intricate data patterns and sample dependencies, and are highly sensitive to noisy data. Consequently,
researchers gradually shifted their focus to DL-based anomaly
detection methods, which typically employ deep neural networks to automatically learn complex feature representations of
data, enabling the identification of abnormal data. In comparison
to traditional anomaly detection methods, DL-based methods
excel in effectively capturing data patterns and sample features,
leading to enhanced anomaly detection performance.
DL-based anomaly detection methods can be categorized into
two types based on their training approaches, i.e., Based on
End-to-End learning (E2E) methods and based on Representation Learning (RL) methods. The E2E-based methods entail
directly mapping input data to output results, bypassing intermediate processing stages like feature extraction and data transformation [11]. In real-world scenarios, E2E-based methods frequently face significant susceptibility to noise or contaminated
data present in the training set. This susceptibility results in the

2327-4697 © 2024 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission.
See https://www.ieee.org/publications/rights/index.html for more information.

WU et al.: POISON-RESILIENT ANOMALY DETECTION: MITIGATING POISONING ATTACKS

4745

r Poisoning attacks substantially reduce the inter-class distance, hindering the model’s ability to accurately learn and
represent normal traffic data. Consequently, this severely
degrades the performance of anomaly detection.
r Meticulously crafted poisoned samples exhibit similar distributions to normal samples, rendering the reconstruction
error ineffective as a classification criterion for anomaly
detection.
A. Motivation and Contributions
Fig. 1. Change trends of representation features under normal training and
poisoning attacks. (a) represents the data distribution in the original data space
and the process of filtering and injecting poisoned samples. (b) represents the
change of spatial features in the hidden layer. The mathematical symbols C and
C  represent the class centers of the original space and the hidden layer feature
space, respectively. The mathematical symbols E(Gn , Gm ) and Ẽ(Gn , Gm )
represent the inter-class distance under normal training and the inter-class
distance under poisoning attack, respectively.

model overfitting to the training data and subsequently exhibiting subpar performance on the test set. Moreover, a notable limitation of these methods is their lack of interpretability. RL-based
anomaly detection methods offer several advantages, including
effective dimensionality reduction, efficient data storage, and
compatibility with conventional anomaly detection algorithms.
RL-based anomaly detection methods can additionally provide
interpretability, rendering them valuable in real-world applications. Nevertheless, the presence of human labeling errors or
data poisoning attacks significantly restricts the applicability of
RL-based semi-supervised anomaly detection algorithms [12].
In summary, the E2E-based methods offer a direct mapping
approach but are susceptible to issues like overfitting and data
poisoning attacks. Conversely, RL-based methods provide the
advantages of dimensionality reduction and interpretability but
are also limited by the impact of human labeling errors and data
poisoning attacks in real-world scenarios.
To address the limitations of the aforementioned methods, researchers have devised and implemented various improvements
and techniques aimed at mitigating poisoning attacks in anomaly
detection problems. For instance, Bovenzia et al. [13] proposed
an enhanced version of KitNet to address the issue of poisoning
attacks in E2E-based learning. This enhancement aims to mitigate the impact of poisoned data on the E2E-based learning process. Regarding semi-supervised anomaly detection problems
RL-based, researchers often adopt poisoning defense strategies
inspired by traditional anomaly detection algorithms [14], [15].
These defense strategies employ the proportion of outliers in
the dataset to define the threshold of the decision function in the
fitting process. However, these strategies often prove inadequate
when confronted with complex attack scenarios, particularly
when adversaries construct poisoning attack samples with high
similarity to normal samples. Fig. 1 depicts the changes in hidden
layer features and reconstruction errors during normal training
and under poisoning attacks. In summary, researchers have made
some progress to address the shortcomings of existing methods,
but the following challenges still remain:

In this work, a framework called Poison-Resistant Anomaly
Detection (PRAD) is proposed to address the challenge of
detecting anomalies in encrypted traffic, which may arise from
poisoning attacks and lead to diminished inter-class distance and
unavailable reconstruction errors. PRAD can effectively alleviate poisoning attacks and improve anomaly detection performance. Specifically, we first design a feature encoding module
based on a variant of Variational Recurrent Neural Network
(VRNN) to address the inherent curse of dimensionality in
high-dimensional traffic data. The Amsgrad gradient descent
algorithm and warm-up strategy are employed to further enhance PRAD’s feature extraction and generalization capabilities, thereby mitigating the reduction of inter-class distance.
Furthermore, a feature analysis module is designed to quantify
the impact of poisoning attacks on inter-class distance and
reconstruction error distribution, which can provide valuable
prior information for subsequent anomaly detection tasks. Finally, we design an anomaly detection algorithm that employs
online clustering, which leverages the extracted features and
their associated reconstruction errors. This proposed algorithm
performs clustering on the extracted features using a Gaussian
Mixture Model (GMM) and assigns labels to distinct clusters
based on the corresponding reconstruction errors.
The main contributions of this paper can be summarized as
follows:
r We propose a PRAD framework for detecting encrypted
traffic anomalies in semi-supervised poisoning attack scenarios, which effectively leverages the interdependencies
between labeled samples and data priors for mitigating
poisoning attacks, leading to superior anomaly detection
performance.
r We introduce a feature extraction module that utilizes
VRNN-based feature encoding, and subsequently utilize
the Amsgrad gradient descent algorithm combined with a
warm-up strategy to alleviate the reduction of inter-class
distance.
r We propose feature-based inter-class distance similarity
and intra-class reconstruction error distribution-based shift
evaluation for poisoning attack impact estimation.
r We design an online clustering algorithm to efficiently
detect anomalies in encrypted traffic, which leverages the
extracted features and their associated reconstruction errors. By clustering the extracted features using a GMM
and assigning labels to different clusters based on the
reconstruction errors, anomalies in the encrypted traffic
can be efficiently identified.

4746

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 5, SEPTEMBER/OCTOBER 2024

Experimental results demonstrate that PRAD outperforms
other RL-based semi-supervised anomaly detection algorithms
in terms of AUCROC and AUCPR scores on both the CTU13
and CIRA-CIC-DoHBrw-2020 datasets.
B. Organization
The remainder of this paper is organized as follows. Section II
briefly reviews related work. Section III describes the threat
model and defense capabilities. Section IV presents the details
of the proposed PRAD framework. Section V compares the
test results of the PRAD framework and ablation experiments.
Finally, Section VI concludes the paper.
II. RELATED WORKS
A. Semi-Supervised Traffic Anomaly Detection Algorithm
Given the limited availability of labeled abnormal traffic
data, most large-scale traffic anomaly detection tasks are carried
out under zero-positive settings. Traffic camouflage techniques
(such as traffic shaping and link padding) and the “curse of dimensionality” resulting from the inherently high dimensionality
of traffic data can impede the training and prediction capabilities
of conventional models. DL-based anomaly detection methods
can effectively address this challenge and substantially enhance
the performance of anomaly detection in encrypted traffic scenarios. Most E2E-based traffic anomaly detection methods leverage neural networks to extract local or global features from traffic
data. These features are then used in scoring mechanisms or
sample reconstruction errors to evaluate test samples and identify anomalous data [11], [16], [17]. RL-based traffic anomaly
detection algorithms also employ neural networks to embed
the original data into low dimensions using manifold learning
techniques. This low-dimensional feature representation is then
utilized in conjunction with traditional anomaly detection algorithms for anomaly detection tasks [6], [7], [9], [10]. For example, Cao et al. [12] proposed an anomaly detection algorithm
that combines deep features extracted from Autoencoders (AEs)
with traditional one-class classification. This approach leverages
the powerful feature learning capabilities of DL and the concept
of manifold learning to transform the original high-dimensional
data into a low-dimensional space. Subsequently, anomalies are
classified using an anomaly detection algorithm without altering
the original data distribution.
B. Semi-Supervised Anomaly Detection Poisoning Attacks and
Defense
1) Semi-Supervised Poisoning Attack: Poisoning attacks, as
proposed by Barreno et al. [18], pose a threat to the training
phase of Machine Learning (ML) models. Adversaries aim to
compromise the integrity and reliability of the classifier by
poisoning the training data. Poisoning attacks employ various
techniques, such as modifying labels, injecting malicious samples, and manipulating data. These attacks can be categorized
into two types: untargeted attacks, which aim to degrade a
model’s overall performance [19], [20], and targeted attacks,
which aim to manipulate a model’s predictions for specific

outcomes [21], [22], [23]. With respect to the construction of
poisoning samples, attacks can be categorized into label manipulation and data manipulation. Data manipulation attacks include
optimization-based methods [24], [25] and training-based methods [26], [27], [28], [29]. The integrity and auditability requirements imposed by network protocols on encrypted traffic data
pose significant challenges to anomaly detection in poisoning
attacks based on training, necessitating the predominant use of
optimization-based methods. Bovenzi et al. [30] demonstrated
the impact of poisoning attacks, specifically using label flipping,
on semi-supervised anomaly detection models.
2) Semi-Supervised Poisoning Attack Defense: Data poisoning defense can be broadly categorized into traditional data poisoning defense methods and DL-based data poisoning defense
methods. Traditional data poisoning defense methods emphasize
preprocessing the data before model training to identify and
eliminate anomalies, exemplified by data cleaning techniques
employing anomaly detectors [14], [15]. In contrast, DL-based
data poisoning defense methods typically involve preprocessing the dataset before training, such as leveraging knowledge
extracted from a small set of clean data to bolster robustness [31]. Optimization-based methods enhance the model’s
resilience [31], [32], [33], including dynamic model training [32]
and loss correction using a trusted small dataset [31]. Within
the context of Android malware detection, label-based semisupervised defense, cluster-based semi-supervised defense [34],
and deep K-NN [33] defense have been proposed as effective
countermeasures to detect and eliminate poisoned samples.
Poisoning attack defense methods are designed to mitigate
the impact of poisoning attacks on anomaly detection algorithms. However, traditional poisoning defense methods may
be insufficient in eliminating similar poisoned samples, while
deep learning-based poisoning defense methods, while dependent on affected training samples, cannot ensure the complete
eradication of poisoned data. Existing methods also struggle
due to limited data availability and similarities in poisoned data
patterns. The proposed PRAD framework adopts feature encoding to enhance feature extraction and alleviate the reduction of
inter-class distance. An online clustering algorithm combined
with reconstruction loss is used to effectively detect anomalies.
PRAD demonstrates superior performance compared to other
methods in mitigating attacks and achieving superior anomaly
detection performance.
III. THREAT MODEL AND DEFENSE CAPABILITY
In this section, we present a threat model for the poisoning
attack and analyze the advantages it provides to defenders. The
threat model includes the adversary’s goal, knowledge, and capabilities in manipulating training data, as detailed in Section III-A.
The strategies employed by defenders to effectively prevent
poisoning attacks are significantly influenced by the information
obtained from these threat models, as discussed in Section III-B.
A. Goal, Knowledge and Capability of Adversary
The adversary’s goal is to undermine the model’s performance. Their level of knowledge regarding the target ML model

WU et al.: POISON-RESILIENT ANOMALY DETECTION: MITIGATING POISONING ATTACKS

can vary. In a white-box attack [35], they possess direct access
to training parameters, while in a black-box attack [36], they can
obtain similar data through manipulation techniques. Consider
a victim training an anomaly detection algorithm on a limited
dataset, an adversary who can upload data to the Internet can manipulate parts of the unlabeled dataset. To ensure data integrity
and auditability, adversaries may use label-flipping attacks and
optimization-based data manipulation.
Formally, poisoning adversary A in the unlabeled dataset constructs a set of poisoning examples SP , the input x∗ represents
the adversary’s carefully crafted poisoning samples injected into
the training set, y ∗ = c(x∗ ) represents the desired false target
label, NP denotes the maximum number of poisoning samples
that the adversary can inject, the neural network model is denoted
by f , the training algorithm is represented by Ts and x is a
labeled subset of the original dataset X , there we have:
SP ← A (x∗ , y ∗ , NP , f, Ts , x) .

4747

IV. ARCHITECTURE OF PRAD
A. Overview of PRAD
An overview of PRAD is shown in Fig. 2. The PRAD comprises a front-end Data Preprocessing Module (DPM) and three
primary back-end algorithm modules: Feature Encoding Module (FEM), Feature Analysis Module (FAM), and GMM-based
online clustering Anomaly Detection Module (ADM). Specifically, FEM extracts the low-dimensional hidden layer feature
representation z and the reconstruction error e from the input
sample x. FAM then analyzes the differences in features and
reconstruction losses between normal and abnormal traffic data.
Subsequently, ADM employs the GMM clustering algorithm to
cluster the hidden layer features z and assigns different clusters
based on the average reconstruction loss μeci . Therefore, PRAD
captures feature dependencies by combining prior knowledge
and clustering algorithms to efficiently detect traffic anomalies
in poisoning attack scenarios.

(1)
B. Feature Encoding Module

The adversary’s goal is to manipulate the victim’s model such
that the resulting model f ← T s(SP ∪ X ) classifies the selected
example as the desired target, i.e., f (x∗ ) = y ∗ . A constraint
must be imposed to ensure that the number of poisoned samples
|SP | ≤ P% × Dtrain does not surpass a specified proportion
P% of the total training data size Dtrain , where Dtrain =
X ∪ SP . In practice, the adversary is typically limited in the
amount of data they can poison, often less than 30% of the entire
training set [35], [36].
In the experiment, malicious samples exhibiting a high degree of similarity to normal training samples were meticulously
selected for poisoning attacks to evade direct elimination during the data cleaning process [21], [37]. These samples were
then uniformly treated as normal samples through label-flipping
attacks and incorporated into training sessions. Additionally,
considering that the poisoned samples are malicious samples
very similar to normal data and that the amount of data limits
the intensity of the poisoning attack, the poisoning proportion in
the experiment was controlled to be between 0% ∼ 20%. This
is consistent with the poisoning proportion of less than 30%
reported in the literature.

B. Capability of Defender
The acquisition of target model knowledge and training data
by defenders depends on the threat model. Deep-kNN [33]
assumes access to ground-truth labels, and Taheri et al. [34]
proposed label-based semi-supervised defense and clusteringbased semi-supervised defense. Similar to [34], PRAD operates
under the assumption that an adversary has access to trusted
training data and utilizes this access to acquire the distribution
of normal training data, thereby enabling the forging of poisoned
samples that closely resemble legitimate data. The capabilities
of defenders may vary under different threat models, as defense
may require access to corresponding resources.

The FEM is used to extract the hidden layer feature representation z from the input data x to alleviate algorithmic complexity. The FEM is constructed using a variant of the VRNN
architecture [38], which comprises three primary components:
encoder, decoder, and variational lower bound. Specifically, the
FEM employs encoder to extract the latent representation z from
the original high-dimensional data x. Subsequently, decoder
reconstructs the original data, providing the reconstruction error
e and the reconstruction error residual ε. The variational lower
bound is employed to evaluate the convergence of the algorithm.
z, e, and ε jointly characterize the deviations of anomalous
samples from the normal data distribution. ADM trained with
these three factors is expected to achieve enhanced generalization capabilities on unseen data.
1) Encoder: Given N multivariate time series data of normal traffic flow, a set of observations is represented by x =
(n)
= {xn1 , . . . , xnt , . . . , xnT } ∈
{x(n) }N
n=1 . For each flow, x
T
R , where T represents the length of the stream. To infer the
current data x(n) , we employ FEM for encoding, which also
updates the hidden variable h at each time step t. Simultaneously, the prior probability p(zt |x<t , z<t ) of zt is obtained.
We input the hidden content of the previous time step ht−1
into the prior network to generate the mean μpri,t and standard
deviation σpri,t of the data distribution. Subsequently, we apply
this to a random sampling of the standard normal distribution to
obtain subsequent output calculations and hidden state updates.
Therefore, we have:


2
,
ztn ∼ N μpri,t , σpri,t
[μpri,t , σpri,t ] = ϕpri (ht−1 ) ,

(2)

where μpri,t and σpri,t represent the mean and standard deviation of the prior conditional probability, and ϕ represents the
parameters obtained by the encoder. By inputting data xnt into
the encoder, we obtain our hidden layer feature representation

4748

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 5, SEPTEMBER/OCTOBER 2024

Fig. 2. PRAD consists of four parts, i.e., (a) Data Preprocessing Module (DPM); (b) Feature Encoding Module (FEM); (c) Feature Analysis Module (FAM); and
(d) Anomaly Detection Module (ADM).

ztn through the encoder:



2
ztn |xnt ∼ N μenc , σenc
,


2
μenc , σenc = ϕenc (ht−1 , ϕx (xt )) .

required reconstruction residual εi as follows:
εi = e i − δ e ,
(3)

2) Decoder: The decoder’s decoding process aims to reconstruct the input data xnt . Its output depends not only on ztn but
also on the hidden layer variable ht−1 , we have:


2
,
xnt |ztn ∼ N μdec,t , σdec,t


2
n
μdec,t , σdec,t = ϕdec (ϕz (zt ) , ht−1 ) ,
(4)
where ϕx and ϕz are feedforward neural networks used to
extract features from x(n) and z (n) , respectively. Finally, a GRU
neural network is employed to update ht :
ht = ϕGRU (xt , z t , ht−1 ) .

(5)

3) Variational Lower Bound: FEM employs VRNN to enhance the accuracy of prior probability prediction, thereby improving data reconstruction and obtaining the correct hidden
layer representation z (n) . The Evidence Lower Bound (ELBO)
determines its lower bound, so our loss function Lloss is the
negative of the optimal lower bound:
Lloss=−

T


E [log p (xt |z <t , x<t ) − KL (Nenc,t ||Npri,t )],

t=1

(6)
which the first term is to minimize the reconstruction error
log p(xt |z <t , x<t ), while the second term aims to make the
posterior distribution Nenc,t closely approximate the prior distribution Npri,t .
Leveraging FEM, the high-dimensional original data x is
reconstructed into x and the hidden layer feature representation
N ). Additionally, another key
z = {fT s (x)|z ∈ RM } (M
element is obtained, which is the reconstruction error ei :
ei = x i − x  i ,

(7)

where · is the L2-norm, and ei also serves as an indicator
of anomalous samples. Thus, the set of all reconstruction errors
is obtained: e = {e1 , · · · eN } ∈ RN . We select the maximum
reconstruction error δe as the threshold to calculate our final

(8)

where εi is represents the difference between the reconstruction
error of the data set and the maximum reconstruction error
in the training set. Essentially, it indicates the direction of
the input data. To sum up, z, e, and ε characterize the input
samples. Notably, these three elements uniquely represent the
input samples. With the FEM module, typical anomalies with
large reconstruction errors can deviate significantly from normal
samples.
C. Feature Analysis Module
The purpose of FAM is to analyze the impact of poisoning
attacks on the zero-positive training set. We analyze the impact
of the poisoned model on the unlabeled data set Dtest from two
perspectives: (1) the changes in the feature space caused by the
poisoned model, and (2) the changes in the distribution of the
reconstruction error loss. This analysis also provides a foundation for subsequent ADM anomaly identification by providing
a priori information. Consider a pure training set Dtrain and a

. The training processes of the pure
poisoned training set Dtrain
training set and the poisoned training set can be simplified to

), respectively. The elements of the
Ts (Dtrain ) and Ts (Dtrain
unlabeled data set Dtest obtained by different FAM encoding
processes f are f (z, eT , εT ) and f (z̃, ẽT , ε̃T ), respectively.
To quantify the impact of poisoning attacks on normal and
abnormal data in unlabeled sample sets, we propose two metrics,
i.e., feature-based inter-class distance similarity evaluation, and
intra-class reconstruction error distribution-based shift evaluation.
1) Feature-Based Inter-Class Distance Similarity Evaluation: The RL-based method currently employs a classificationbased anomaly detection approach to tackle the dimensionality
challenge posed by the high-dimensional nature of traffic data.
However, the inter-class distance of the representation data in
the unlabeled data set obtained through FEM decreases due
to the influence of poisoning attacks on the training set. To
quantify the changes in the feature space induced by model
poisoning, we employ the ratio of the inter-class distance after
poisoning to the inter-class distance obtained through normal

WU et al.: POISON-RESILIENT ANOMALY DETECTION: MITIGATING POISONING ATTACKS

encoding as a metric for measuring similarity changes. Consider
z = {z n ∈ Rn∗M , z m ∈ Rm∗M }, (n + m = NT ) as the unlabeled data set representation data obtained by pure encoding,
where z n represents the hidden layer representation of normal
samples and z m represents the hidden layer representation
of abnormal samples, and M is the dimensionality of hidden
layer features. Similarly, z̃ = {z̃ n ∈ Rn∗M , z̃ m ∈ Rm∗M } is
the unlabeled data set representation data obtained by poisoned
encoding. {η1 , · · · ηn , ηn+1 , · · · ηn+m } positive numbers, think
of these as weights, or better yet, as “multiplication” of axes. Let
Cn (yn ) and Cm (ym ) denote the weighted sum of the distances
between the positive class center yn and the positive data points
z n , and the weighted sum of the distances between the abnormal
class center ym and the abnormal data points z m , respectively:
Cn (yn ) =

n


ηi di (yn ), Cm (ym ) =

i=1

n+m


4749

data classes in the unlabeled dataset Dtest . Let e = {en , em }
denote the unlabeled dataset Dtest reconstruction errors obtained by pure encoding, where n represents the number of
normal samples in the unlabeled data set and m represents the
number of abnormal samples. Similarly, the unlabeled dataset
Dtest reconstruction errors obtained by poisoned encoding can
be obtained: ẽ = {ẽn , ẽm }. The distribution of intra-class reconstruction errors can then be measured by calculating the mean
μ and variance σ 2 :

μn =

ei ,

2
σn
=

1
(ei − μn )2 ,
n i=1

(13)

ei ,

2
σm
=

1 
(ei − μm )2 .
m i=1

(14)

i=1

μm =
ηi di (ym ), (9)

n


m

i=1

n

m

i=n+1

where di (y) = y − zi represents the Euclidean distance from
the class center y to zi . The objective is to identify a point y (or a
set of points) that minimizes the specified “cost function” C(y):


Gn (z n , ηn ) = arg min Cn (yn ) , y ∈ RM ,
(10)


(11)
Gm (z m , ηm ) = arg min Cm (ym ) , y ∈ RM ,
where G is referred to as the weighted geometric median [39],
which employ the improved Weiszfeld algorithm [40] to solve
this problem. Subsequently, the impact of the poisoning attack
on the unlabeled data set Dtest can be assessed by calculating
the Euclidean distance E(Gn , Gm ) between the normal data
distribution Gn and the distribution of poisoned data Gm ,
which is obtained using the improved Weiszfeld algorithm. This
allows us to compare the inter-class distance of the pure encoded
data E(Gn , Gm ) with the inter-class distance of the poisoned
encoded data Ẽ(Gn , Gm ), thereby quantifying the impact of
poisoning attacks. Furthermore, to gain a clearer understanding
of the change in inter-class distance after surface poisoning, we
opt to measure similarity based on distance.
Sim =

 (Gn , Gm )
E
,
E (Gn , Gm )

(12)

where “Sim” represents the feature-based inter-class distance
“similarity” evaluation index. A smaller value indicates a smaller
class distance, making the classification task of normal and
abnormal data more challenging. Section V-D1 presents the
experimental analysis of feature space similarity evaluation for
unlabeled datasets under poisoning attacks.
2) Intra-Class Reconstruction Error Distribution-Based
Shift Evaluation: Reconstruction errors are commonly employed as indicators for anomaly detection. However, anomaly
detection methods based on reconstruction errors become ineffective when the training data is compromised by poisoning
attacks. In this work, we propose a strategy based on reconstruction error distribution shift evaluation to quantify the impact of
poisoning attacks on unlabeled datasets Dtest . Specifically, we
measure the impact of training data poisoning by comparing the
changes in the reconstruction errors distribution across different

By comparing the reconstruction error distributions of different
data types in the unlabeled dataset Dtest obtained through pure
encoding and poisoning encoding, we can quantify the impact
of poisoning attacks on the reconstruction error distribution of
various data types in the unlabeled dataset Dtest . It is noteworthy
that under the influence of poisoning attacks, as the attack
intensity increases, the average reconstruction loss distribution
of abnormal data in the unlabeled dataset becomes increasingly similar to the average reconstruction loss distribution of
normal data, making the anomaly detection classification task
progressively more challenging. Our subsequent classification
hypothesis posits that the average reconstruction error distribution of abnormal data is higher than that of normal data.
In the entire unlabeled dataset, the number of abnormal data
samples is smaller than that of normal samples. Therefore, the
bias based on the intra-class reconstruction error distributionbased shift evaluation also provides valuable prior information
for subsequent anomaly detection algorithms. The experimental
results are analyzed in Section V-D2, which corroborate our
hypothesis.

D. Abnormal Detection Module
Leveraging the a priori information provided by FAM and the
features encoded by FEM, we propose an ADM based on GMM
online clustering. Specifically, the ADM employs an online
GMM clustering algorithm to cluster the encoded features z.
Subsequently, it assigns different clusters based on the average
reconstruction loss μeci , thereby achieving anomaly detection.
The detailed process of the ADM module is illustrated in Fig. 3.
Consider a set of J mixed multivariate Gaussian distributions, indexed by the parameter set Θ = {αj , ϑj }, where ϑj =
{μj , Σj } denote the parameters of the j-th Gaussian distribution, where the mean vector is denoted by μj , Σj is the
covariance matrix, and αj ∈ [0, 1] is the mixing probability.
Suppose that the encoded feature sets z ∈ RNT ∗M obtained by
applying FEM to the original data x ∈ RNT ∗T are i.i.d according
to the mixed probability density function. We estimate the parameters Θ using the maximum likelihood estimation procedure,

4750

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 5, SEPTEMBER/OCTOBER 2024

NT
1 
γij (z i − μj ) (z i − μj )T ,
Σj =
Φij j=1

Fig. 3. The ADM consists of (a) encoded feature set; (b) reconstruction error
set; and (c) online GMM clustering algorithm. The last (d) is the cluster result
obtained by online GMM clustering.

T
where Φij = N
j=1 γij . E-step and M-step are calculated
iteratively until the condition converges according to the
likelihood function of the formula (16).
Employing the online GMM clustering algorithm, J (J =
2) clusters are obtained. Subsequently, the a priori information
provided by the FAM is leveraged to identify the corresponding
reconstruction loss for the feature representation in each cluster.
The average reconstruction loss μecj of the two clusters is then
calculated, respectively:

μec1 =
as shown in (15), where the log-likelihood is given by (16):
⎛
⎞

 
⎝
L (Θ|z) =
p (z i |ϑj ) =
αj pj (z i |μj , Σj )⎠,
i∈NT

j∈J

⎛
⎞


log (Θ|z) =
log ⎝
αj pj (z i |μj , Σj )⎠ ,
i∈NT

(15)
(16)

j∈J

where Σj is a symmetric positive definite matrix, z i represents
the observable elements of the i-th sample, pj (z i |μj , Σj ) represents the probability density of the j-th sample value corresponding to the j-th Gaussian component, and its mathematical
expression is as follows:
P (z i |μj , Σj ) =

1
(2π)NT /2 |Σj |1/2

e−1/2(zi −μj )

T

Σj−1 (z i −μj )

.

(17)
Given the structural complexity of (15), the optimal Θ cannot
be obtained by setting the derivative to zero. The Expectation
Maximization (EM) procedure [41] is a powerful method for
maximizing the log-likelihood function (16) and finding the
optimal parameters. The latter iteratively updates the parameters of each Gaussian distribution. Therefore, the parameter set of GMM consists of {αj , μj , Σj }, where 1 ≤ j ≤ J.
And the parameters are estimated under the maximum likelihood setting. Optimization is usually performed using the EM
algorithm, which is divided into two steps, i.e., E-step and
M-step:
1) E-step: The posterior probability γij is calculated by the
equation, according to the given value of {αj , μj , Σj }:
γij =

αj p (z i |μj , Σj )
.
J
j=1 αj p (z i |μj , Σj )

(18)

Φij
,
NT

μj =

NT
1 
γij z i ,
Φij j=1

n1


eci , μec2 =

i=1

n2


eci ,

(21)

i=1

where μec1 and μec2 represent the average reconstruction loss
of the two clusters, respectively, and n1 and n2 represent the
amount of data contained in each cluster, respectively. The
average loss is compared with the a priori information provided
by FAM. If μec1 > μec2 , then the cluster corresponding to μec2
is considered a normal sample, and the cluster corresponding
to μec1 is an abnormal sample. Conversely, if μec1 < μec2 , then
the cluster corresponding to μec1 is considered a normal sample,
and the cluster corresponding to μec2 is an abnormal sample.
The pseudocode for the online clustering ADM is shown in
Algorithm 1.
E. Training Procedure
A two-stage training strategy is employed to construct PRAD.
In the first stage, pre-training is performed using only the reconstruction loss to train the feature encoding network. During this
stage, all unlabeled training samples are utilized to pre-train
the FEM with the objective of obtaining the entire network for
subsequent stages. The fundamental encoding strategy involves
leveraging Amsgrad stochastic gradient descent algorithm and
the warm-up strategy to train the network, thereby mitigating
the issue of shrinking inter-class distance caused by poisoning
attacks. In the second stage, FAM is employed to acquire prior
knowledge of the data for the subsequent ADM module by utilizing the extracted features and their corresponding reconstruction
errors. The limited effectiveness of reconstruction error as a
sole classification criterion is addressed by utilizing a GMM to
cluster the extracted features. This approach involves assigning
cluster labels based on the reconstruction error values, thereby
enhancing the classification process.
V. EXPERIMENTS
A. Dataset Description

2) M-step: A new set of {αj , μj , Σj } can be obtained by
using the aforementioned γij :
αj =

(20)

(19)

In this part of the experiments, the performance of PRAD
is assessed on two publicly available encrypted traffic anomaly
detection datasets, i.e., CTU13 [42] and CIRA-CIC-DoHBrw2020 (DoH2020) [43]. Specifically, the CTU13 dataset consists
of botnet traffic combined with normal and background traffic,
encompassing 13 types of botnet traffic. The DoH2020 dataset

WU et al.: POISON-RESILIENT ANOMALY DETECTION: MITIGATING POISONING ATTACKS

Algorithm 1: Online Clustering ADM.
Input: Encoded feature set
z = {z 1 , z 2 , . . ., z N T } ∈ RNT ×M ;
The number of clusters J; Reconstruction errors set of z:
e ={e1 , e2 , . . ., eNT } ∈ RNT .
Output: {α1 , . . ., αJ }; {(μ1 , Σ1 ), . . ., (μJ , ΣJ )}; AD.
1. Initialize the parameters of GMM according to z.
2. Loop Body:
E-step: Calculate the posterior probability γij by (18)
M-step: Re-estimate the parameters using data samples
weighted by the posterior probabilities using
formulas (19) and (20).
3. Until the maximum iteration number rmax or the
termination condition is reached.
4. Output 1: The parameter sets of each GMM component
{(μ1 , Σ1 ), . . ., (μJ , ΣJ )} and {α1 , . . ., αJ }.
5. Count the number of samples in each cluster, and find
the corresponding reconstruction error in e.
6. Calculate the average reconstruction error of samples in
each cluster according to formula (21), recorded as μec1
and μec1 , respectively.
7. While μec1 = μec2 do
If μec1 > μec2 then
c1 is an abnormal sample cluster;
c2 is a normal sample cluster;
else
c1 is a normal sample cluster;
c2 is an abnormal sample cluster;
end while
8. Output 2: AD
TABLE I
DATASETS DETAILS

facilitates the analysis, testing, and evaluation of DoH traffic
in covert channels and tunnels, and can be utilized to assess
encrypted traffic anomaly detection algorithms. In our experiments, we carefully selected hundreds of thousands of data
points from the two datasets for further experimentation. Prior
to employing these datasets for anomaly detector evaluation,
standard preprocessing procedures were applied to each dataset.
Firstly, the initial 500 bytes of each dataset’s individual data
stream payload were extracted. Subsequently, excessively long
data streams were truncated, and excessively short data streams

4751

were padded, followed by data normalization. Table I presents
the details of the datasets, each dataset consists of a training
set and a unlabeled data set. The training set includes normal
samples and carefully selected poisoned samples, while the
unlabeled data set comprises a specific proportion of positive
samples and negative samples. Here, P% denotes the ratio of
poisoned data in the training set, and η represents the proportion
of abnormal samples in the unlabeled data set.

B. Performance Metrics
To gauge prediction performance, the AUCROC metric is
employed, which is particularly susceptible to poisoning attacks. Additionally, AUCPR is utilized to account for sample imbalance in measuring prediction performance. AUCROC
represents the area under the receiver operating characteristic
curve, while AUCPR denotes the area under the precision-recall
curve. AUCROC characterizes the relationship between the true
positive rate and false positive rate, whereas AUCPR focuses on
the association between precision and recall. While AUCROC
evaluates prediction performance for both normal and anomaly
categories, AUCPR emphasizes anomaly-centric performance.
It’s worth noting that both AUCROC and AUCPR range from 0
to 1, with higher values indicating superior performance.

C. Competitive Methods and Parameter Settings for PRAD
1) Competitive Methods: PRAD is compared with nine
methods: ECOD [6], COPOD [7], KDE [44], OCSVM [5],
LOF [4], iForest [8], LSCP [9], INNE [45], and SUOD [10].
Among these methods, KDE, LOF, and IForest do not employ
poisoning attack suppression strategies, while the other six methods all incorporate such strategies. All comparison algorithms
are implemented using Python’s PyOD library, and the default
parameters are utilized for all methods. Notably, OCSVM offers
two poisoning suppression strategies (μ = 0.1 and u = 0.5).
PRAD is implemented using PyTorch, and experiments are
conducted using the PyTorch 2.0.0 framework via PyCharm
2022.2.5 (Community Edition) on computers equipped with a
GeForce RTX 3090 GPU and an Intel (R) Xeon (R) Silver 4216
CPU.
2) Parameter Settings: By default, the input encoder and
prior encoding in PRAD’s FEM consist of two linear encodings and a layer of Batchnorm1D regularization. The decoder
is similar, with a GRU neural network as the middle hidden
layer. The activation function for the middle layer is ReLU,
while the final output layer employs the Sigmoid function as
its activation function. The input data dimension is 500, and
the dimensionality of the encoded data is 128. It’s worth noting
that varying the number of hidden layers in FEM (N = 4 by
default) can impact the performance of PRAD. The proposed
PRAD is trained for a total of 175 epochs with a batch size of
128, warm-up is 5 epochs. Validation results obtain at the end of
each training phase serve to assess the PRAD’s generalization
capability and aid in deciding whether to retain the trained FEM.
The clustering parameter J is set to 2.

4752

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 5, SEPTEMBER/OCTOBER 2024

Fig. 4. Feature analysis result: (a) feature-based inter-class distance similarity
evaluation for poisoning impact estimation; (b) intra-class reconstruction error
distribution-based shift evaluation for poisoning attack impact estimation.

D. Effect of Feature Analysis
1) Feature-Based Inter-Class Distance Similarity Evaluation: In this part, we employ feature-based inter-class distance
similarity to assess the impact of poisoned FEM on unlabeled
data sets when the training set data is subject to poisoning
attacks. Specifically, the concept of similarity here quantifies
the impact of poisoning attacks on the distance between the
center of normal samples and the centers of abnormal samples.
It is important to note that lower similarity values indicate a
reduced distance between data points of different classes, posing
significant challenges for subsequent anomaly detection tasks.
Fig. 4(a) illustrates that as the intensity of poisoning attacks in the
training set increases, the impact of poisoning attacks intensifies,
leading to a continuous decrease in the center distance between
positive samples and abnormal samples in the unlabeled data set.
The DOH2020 experiences the most significant impact, with the
distance between the centers of positive samples and abnormal
samples reduced to only 31% of the original class distance.
Similarly, in the CTU13, the distance between normal samples
and abnormal samples is reduced to approximately 56% of the
original class distance. The feature-based inter-class distance
similarity evaluation demonstrates that the impact of poisoning
attacks on the training set leads to a continuous reduction in the
class distance of positive anomaly data in the unlabeled dataset,
which poses significant challenges for subsequent anomaly detection tasks.
2) Intra-Class Reconstruction Error Distribution-Based
Shift Evaluation: In this part, we employ shift evaluation based
on intra-class reconstruction error distribution to quantify the
impact of the poisoned FEM module on the reconstruction error
distribution of positive anomaly samples in the unlabeled data
set when the training set is compromised by poisoning attacks.
Fig. 4(b) presents error bar plots depicting the reconstruction
errors for different components of the unlabeled samples in the
DOH2020 and CTU13. As evident from the Fig. 4(b), when
FEM is not affected by poisoning, the reconstruction errors
for normal samples and abnormal samples in the DOH2020
unlabeled dataset are 0.01 and 0.1, respectively, with an overall
unlabeled dataset error of 0.025. Similarly, in the absence of
poisoning attacks on FEM, the reconstruction errors in CTU13
are 0.02, 0.1, and 0.04 for normal samples, abnormal samples,
and the entire unlabeled dataset, respectively. When the training

set is subjected to poisoning attacks, each component of the
unlabeled dataset encoded by the poisoned FEM undergoes
changes. Specifically, the average reconstruction error distribution of abnormal samples exhibits a continuous decrease, while
the reconstruction error distribution of positive samples remains
largely unchanged. More specifically, in the unlabeled sample
sets of DOH2020 and CTU13, the average reconstruction error
distribution of normal samples remains stable at approximately
0.01 and 0.02, respectively. In contrast, the average reconstruction error distribution of abnormal samples gradually decreases
and eventually stabilizes around 0.025 and 0.06, respectively.
Concurrently, the mean distribution of the entire unlabeled
sample set also exhibits a gradual decrease, ultimately settling
around 0.015 and 0.03, respectively. It is noteworthy that the
mean reconstruction error of abnormal samples consistently exceeds that of normal samples in both datasets, offering valuable
prior information for the proposed ADM.
E. Experiment Results With Competitive Methods
In this part, we compare the proposed PRAD with other
competing methods. The performance of different algorithms
on data without FEM is evaluated, particularly under varying
proportions of poisoning attacks. Subsequently, the performance
of feature-encoded data using alternative comparison algorithms
is assessed under different degrees of poisoning attacks. PRAD
is adopted as a baseline for anomaly detection on poisoned
data, addressing the semi-supervised anomaly detection problem
trained on the poisoned data in the training set. Comparing the
results in Table II, it is evident that traditional anomaly detection
algorithms without RL exhibit satisfactory performance on two
metrics when faced with data poisoning attacks. However, due
to the high dimensionality of data attributes, the training cost of
these algorithms becomes prohibitively high. Conversely, when
utilizing RL-based solutions, traditional anomaly detection algorithms struggle in the presence of data poisoning attacks.
As the intensity of poisoning attacks escalates, the inter-class
distance between normal and abnormal samples progressively
diminishes, leading to the failure of traditional anomaly detection algorithms, especially on the CTU13. The average highest
AUCROC and AUCPR scores across all compared algorithms
on the DoH2020 and CTU13 are 0.821 and 0.533, respectively.
Undoubtedly, this poses a significant challenge for the anomaly
detection task. In comparison to previous anomaly detection
algorithms, the proposed PRAD demonstrates superior robustness against poisoning attacks. Firstly, PRAD maintains excellent performance levels even without data poisoning attacks.
Moreover, as the intensity of data poisoning attacks increases,
PRAD exhibits remarkable resilience in the face of decreasing
inter-class distance. With the increasing proportion of poisoned
data, the anomaly detection indicators AUCROC and AUCPR
scores stabilize above 0.980 and 0.986, respectively. Importantly, the PRAD emerges as the frontrunner in the presence of
various levels of data attack intensity. Additionally, the average
AUCROC and AUCPR scores across the two validation datasets
reach an astonishing 0.995 and 0.996, respectively. Thus, PRAD
achieves the highest average performance among all competing

WU et al.: POISON-RESILIENT ANOMALY DETECTION: MITIGATING POISONING ATTACKS

4753

TABLE II
AUCROC AND AUCPR OF PRAD AND COMPARISON ALGORITHMS UNDER POISONING INTENSITY OF 0% ∼ 20%

Fig. 5.

Clustering results of CTU13 and DoH2020 under different poisoning attack intensities.

approaches. Fig. 5 illustrates the clustering effect of PRAD on
the CTU13 and DoH2020. In the absence of data poisoning
attacks, the inter-class distance between positive and negative
data consistently exhibits a clear separation. However, as the
intensity of data poisoning attacks gradually intensifies, the distance between classes gradually diminishes, causing abnormal
data points to move closer to normal data points.
F. Ablative Analysis
1) The Effects of Different Encoding Strategies: We use
different encoding strategies to demonstrate the rationality of

selecting VRNN as FEM within the PRAD framework. For
comparison, we assess the performance of AE and VAE using
the same experimental setup as the VRNN FEM. Table III
presents the experimental results of the nine comparison algorithms. When AE and VAE are employed as FEM and are not
subjected to data poisoning attacks, their subsequent anomaly
detection performance surpasses that of traditional anomaly detection algorithms, as evident from Table III. Furthermore, their
simple architecture and low computational complexity make
them suitable options, especially when handling low-intensity
data poisoning attacks. This flexibility enables the FEM to be
seamlessly integrated as a plug-and-play component. However,

4754

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 5, SEPTEMBER/OCTOBER 2024

TABLE III
COMPARISON OF PERFORMANCE BETWEEN DIFFERENT COMPARISON ALGORITHMS

as the severity of poisoning attacks intensifies, particularly when
the poisoning rate surpasses 10%, the anomaly detection performance on the CTU13 degrades significantly when AE or
VAE is used as the FEM. Specifically, the AUCROC scores
undergoes a steep decline, even falling below that of certain
comparison algorithms. Additionally, the AUCPR scores also
drops to 0.892. Although AE and VAE still surpass traditional
anomaly detection algorithms as the intensity of data poisoning
attacks increases, their overall performance falls short of that
achieved by employing VRNN as the FEM, as indicated by
the average results. These observations validate our choice of
using VRNN as the FEM in our experiments. Despite its higher
complexity compared to AE and VAE, VRNN exhibits superior
experimental performance, particularly when confronted with
the increasing intensity of data poisoning attacks.
2) Effect of Amsgrad Backpropagation Algorithm on Poisoning Defense: We investigate the impact of incorporating the
Amsgrad backpropagation algorithm during FEM training on
the overall experimental results. Fig. 6 presents the experimental
results assessed using the AUCROC and AUCPR scores. An
analysis of the AUCROC scores reveals that employing the
Amsgrad backpropagation algorithm during FEM training leads
to noticeable variations in the resulting performance, particularly on the CTU13. When using the conventional AdamW

Fig. 6. The impact of Amsgrad backpropagation algorithm on anomaly detection results.

algorithm, even a moderately intensified poisoning attack results
in a significant decline in performance across the entire CTU13.
In contrast, on the DoH2020, as the intensity of the poisoning
attack escalates, its performance experiences a gradual decline
before eventually stabilizing. It is noteworthy that the impact
on the results for the CTU13 is markedly different. As the intensity of poisoning attacks increases, utilizing the conventional
AdamW algorithm leads to a sharp decrease in the AUCROC
and AUCPR scores on the CTU13, causing them to drop to

WU et al.: POISON-RESILIENT ANOMALY DETECTION: MITIGATING POISONING ATTACKS

4755

Fig. 7. The impact of poisoning attack intensity and data imbalance on anomaly detection performance: From left to right, the results of DoH2020 and CTU13
affected by different poisoning attack intensity and different data imbalance on the two indicators of AUCROC and AUCPR.

approximately 0.75. This substantial decline results in a notable
increase in false positives and false negatives. In summary, integrating the Amsgrad algorithm during FEM training effectively
mitigates the issues caused by poisoning attacks in subsequent
anomaly detection tasks. It demonstrates significant benefits in
preserving performance stability and minimizing false positives
and false negatives.
3) The Joint Effect of Data Imbalance and Poisoning Attacks:
We study the overall performance of PRAD in the context of
data poisoning attacks and data imbalance issues. The results
of these experiments are illustrated in Fig. 7. We investigate
the impact of increasing data poisoning attacks and the growing
problem of data imbalance. In the absence of data poisoning
attacks, PRAD demonstrates robust performance in the face
of data imbalance problems. However, as the intensity of data
poisoning attacks increases and the proportion of abnormal
data decreases, PRAD’s performance on the DoH2020 dataset
remains remarkably resilient. The AUCROC scores gradually
decreases and stabilizes around 0.975. Meanwhile, the AUCPR
scores only experiences a significant decrease when the poisoning rate reaches 20%. It is important to note that the CTU13
displays distinct characteristics. The impact of data imbalance
becomes more evident as the intensity of poisoning attacks
deepens. Particularly, when the poisoning rate is 20%, and the
abnormal data accounts for 1/6 of the overall test data, the
effect becomes most pronounced. Similarly, the AUCPR scores
indicator exhibits a more prominent impact of data imbalance
as the intensity of poisoning attacks intensifies. In conclusion,
when confronted with data poisoning attacks, it is crucial to
ensure that the proportion of abnormal samples in the total
dataset is no less than 20% when utilizing PRAD for anomaly
detection.
4) Time Complexity: In this part, we present a time complexity evaluation of the proposed PRAD approach. To facilitate
a comprehensive comparison, we have additionally included
the training complexity analysis of competing algorithms in
Table IV. In the table, n denotes the size of the input data, t represents the number of trees, and ψ represents the subspace sample
size. We perform a time complexity analysis on each component
of the model. Notably, since the front end of the model is based
on the FEM of VRNN, we employ two indicators: Floating-point
Operations (Flops) and Parameters (Params). The training Flops
and Params of the proposed model are approximately 11.9 times

TABLE IV
TIME COMPLEXITY ANALYSIS OF PRAD AND COMPETITIVE ALGORITHMS

and 13.1 times higher compared to VAE and AE, respectively.
However, the predicted Params of the proposed model is 2.12 M,
which is around 3.3 times that of VAE and AE. Similarly, the
back end of PRAD employs a clustering ADM based on GMM.
The back end’s training time complexity is O(n2 ), while the
prediction process time complexity is O(n), indicating that the
training of the model’s front-end feature extraction and back-end
clustering anomaly detection modules incurs the highest time
complexity.
VI. CONCLUSION
In this paper, we proposed PRAD, a semi-supervised encrypted traffic anomaly detection framework under poisoning
attack scenarios. Specifically, to solve the inter-class reduction
problem caused by poisoning attacks, we first propose a feature
encoding module based on VRNN variants, and then adopt the
Amsgrad gradient descent algorithm and warm-up strategy to
alleviate this problem. In addition, FAM is also introduced to
evaluate the impact of poisoning attacks on inter-class distances
and analyze the distribution of reconstruction errors, providing
important prior information for subsequent anomaly detection
tasks. Finally, an online clustering algorithm is designed to
effectively detect anomalies in encrypted traffic, which utilizes
the extracted features and their associated reconstruction errors
to effectively identify anomalies in encrypted traffic. Extensive
experiments have verified that PRAD can cope with anomaly
detection of encrypted traffic in poisoning attack scenarios. In
future work, we will address the issue of backdoor attacks in
encrypted traffic.

4756

IEEE TRANSACTIONS ON NETWORK SCIENCE AND ENGINEERING, VOL. 11, NO. 5, SEPTEMBER/OCTOBER 2024

REFERENCES
[1] Z. Durumeric et al., “The security impact of HTTPS interception,” in Proc.
24th Annu. Netw. Distrib. Syst. Secur. Symp., 2017, pp. 1–14.
[2] G. D. L. T. Parra, P. Rad, and K.-K. R. Choo, “Implementation of deep
packet inspection in smart grids and industrial Internet of Things: Challenges and opportunities,” J. Netw. Comput. Appl., vol. 135, pp. 32–46,
2019.
[3] J. Sherry, C. Lan, R. A. Popa, and S. Ratnasamy, “BlindBox: Deep packet
inspection over encrypted traffic,” in Proc. ACM Conf. Special Int. Group
Data Commun., 2015, pp. 213–226.
[4] H. Gao, B. Qiu, R. J. D. Barroso, W. Hussain, Y. Xu, and X. Wang,
“TSMAE: A novel anomaly detection approach for Internet of Things time
series data using memory-augmented autoencoder,” IEEE Trans. Netw. Sci.
Eng., vol. 10, no. 5, pp. 2978–2990, Sep./Oct. 2022.
[5] J. Ahmed, H. H. Gharakheili, C. Russell, and V. Sivaraman, “Automatic
detection of DGA-enabled malware using SDN and traffic behavioral
modeling,” IEEE Trans. Netw. Sci. Eng., vol. 9, no. 4, pp. 2922–2939,
Jul./Aug. 2022.
[6] Z. Li, Y. Zhao, X. Hu, N. Botta, C. Ionescu, and G. Chen, “ECOD: Unsupervised outlier detection using empirical cumulative distribution functions,” IEEE Trans. Knowl. Data Eng., vol. 35, no. 12, pp. 12181–12193,
Dec. 2023.
[7] Z. Li, Y. Zhao, N. Botta, C. Ionescu, and X. Hu, “COPOD: Copulabased outlier detection,” in Proc. IEEE Int. Conf. Data Mining, 2020,
pp. 1118–1123.
[8] F. T. Liu, K. M. Ting, and Z.-H. Zhou, “Isolation-based anomaly detection,”
ACM Trans. Knowl. Discov. Data, vol. 6, no. 1, pp. 1–39, 2012.
[9] Y. Zhao, Z. Nasrullah, M. K. Hryniewicki, and Z. Li, “LSCP: Locally
selective combination in parallel outlier ensembles,” in Proc. SIAM Int.
Conf. Data Mining, 2019, pp. 585–593.
[10] Y. Zhao et al., “SUOD: Accelerating large-scale unsupervised heterogeneous outlier detection,” Proc. Mach. Learn. Syst., vol. 3, pp. 463–478,
2021.
[11] Y. Mirsky, T. Doitshman, Y. Elovici, and A. Shabtai, “KITSUNE: An
ensemble of autoencoders for online network intrusion detection,” in Proc.
25th Annu. Netw. Distrib. Syst. Secur. Symp., 2018, pp. 1–15.
[12] V. L. Cao, M. Nicolau, and J. McDermott, “Learning neural representations
for network anomaly detection,” IEEE Trans. Cybern., vol. 49, no. 8,
pp. 3074–3087, Aug. 2019.
[13] G. Bovenzi, G. Aceto, D. Ciuonzo, A. Montieri, V. Persico, and A.
Pescapé, “Network anomaly detection methods in IoT environments via
deep learning: A fair comparison of performance and robustness,” Comput.
Secur., vol. 128, pp. 103–167, 2023.
[14] I. Diakonikolas, G. Kamath, D. Kane, J. Li, J. Steinhardt, and A. Stewart,
“Sever: A robust meta-algorithm for stochastic optimization,” in Proc. Int.
Conf. Mach. Learn., 2019, pp. 1596–1606.
[15] J. Steinhardt, P. W. W. Koh, and P. S. Liang, “Certified defenses for
data poisoning attacks,” in Proc. Adv. Neural Inf. Process. Syst., 2017,
pp. 3517–3529.
[16] H. Lu, T. Wang, X. Xu, and T. Wang, “Cognitive memory-guided autoencoder for effective intrusion detection in Internet of Things,” IEEE Trans.
Ind. Informat., vol. 18, no. 5, pp. 3358–3366, May 2022.
[17] J. Ashraf, A. D. Bakhshi, N. Moustafa, H. Khurshid, A. Javed, and A.
Beheshti, “Novel deep learning-enabled LSTM autoencoder architecture
for discovering anomalous events from intelligent transportation systems,”
IEEE Trans. Intell. Transp. Syst., vol. 22, no. 7, pp. 4507–4518, Jul. 2021.
[18] M. Barreno, B. Nelson, R. Sears, A. D. Joseph, and J. D. Tygar, “Can
machine learning be secure?,” in Proc. ACM Symp. Inf., Comput. Commun.
Secur., 2006, pp. 16–25.
[19] Y. Hua, F. Wan, H. Gan, Y. Zhang, and X. Qing, “Distributed estimation
with cross-verification under false data-injection attacks,” IEEE Trans.
Cybern., vol. 53, no. 9, pp. 5840–5853, Sep. 2023.
[20] M. Fang, X. Cao, J. Jia, and N. Gong, “Local model poisoning attacks
to {Byzantine-Robust} federated learning,” in Proc. 29th USENIX Secur.
Symp., 2020, pp. 1605–1622.
[21] P. Zhao et al., “Garbage in, garbage out: Poisoning attacks disguised with
plausible mobility in data aggregation,” IEEE Trans. Netw. Sci. Eng., vol. 8,
no. 3, pp. 2679–2693, Jul.–Sep. 2021.
[22] Y. Liu et al., “Trojaning attack on neural networks,” in Proc. 25th Annu.
Netw. Distrib. Syst. Secur. Symp., 2018, pp. 1–17.
[23] A. Shafahi et al., “Poison frogs! targeted clean-label poisoning attacks
on neural networks,” in Proc. Adv. Neural Inf. Process. Syst., 2018,
pp. 151–178.
[24] W. R. Huang, J. Geiping, L. Fowl, G. Taylor, and T. Goldstein, “MetaPoison: Practical general-purpose clean-label data poisoning,” in Proc. Adv.
Neural Inf. Process. Syst., 2020, pp. 12080–12091.

[25] M. Al-Hawawreh, N. Moustafa, S. Garg, and M. S. Hossain, “Deep
learning-enabled threat intelligence scheme in the Internet of Things
networks,” IEEE Trans. Netw. Sci. Eng., vol. 8, no. 4, pp. 2968–2981,
Oct.–Dec. 2021.
[26] P. W. Koh, J. Steinhardt, and P. Liang, “Stronger data poisoning attacks
break data sanitization defenses,” Mach. Learn., vol. 111, no. 1, pp. 1–47,
2022.
[27] F. Suya, S. Mahloujifar, A. Suri, D. Evans, and Y. Tian, “Model-targeted
poisoning attacks with provable convergence,” in Proc. Int. Conf. Mach.
Learn., 2021, pp. 10000–10010.
[28] C. Zhu, W. R. Huang, H. Li, G. Taylor, C. Studer, and T. Goldstein,
“Transferable clean-label poisoning attacks on deep neural nets,” in Proc.
Int. Conf. Mach. Learn., 2019, pp. 7614–7623.
[29] S. Li et al., “Hidden backdoors in human-centric language models,” in
Proc. Conf. Comput. Commun. Secur., 2021, pp. 3123–3140.
[30] G. Bovenzi, A. Foggia, S. Santella, A. Testa, V. Persico, and A. Pescapé,
“Data poisoning attacks against autoencoder-based anomaly detection
models: A robustness analysis,” in Proc. IEEE Int. Conf. Commun., 2022,
pp. 5427–5432.
[31] Y. Li, J. Yang, Y. Song, L. Cao, J. Luo, and L.-J. Li, “Learning from
noisy labels with distillation,” in Proc. IEEE Int. Conf. Comput. Vis., 2017,
pp. 1910–1918.
[32] E. Malach and S. Shalev-Shwartz, “Decoupling” when to update”
from” how to update”,” in Proc. Adv. Neural Inf. Process. Syst., 2017,
pp. 961–971.
[33] N. Peri et al., “Deep k-NN defense against clean-label data poisoning
attacks,” in Proc. Eur. Conf. Comput. Vis., 2020, pp. 55–70.
[34] R. Taheri, R. Javidan, M. Shojafar, Z. Pooranian, A. Miri, and M. Conti,
“On defending against label flipping attacks on malware detection systems,” Neural Comput. Appl., vol. 32, pp. 14781–14800, 2020.
[35] M. Jagielski, A. Oprea, B. Biggio, C. Liu, C. Nita-Rotaru, and B. Li,
“Manipulating machine learning: Poisoning attacks and countermeasures
for regression learning,” in Proc. IEEE Symp. Secur. Privacy, 2018,
pp. 19–35.
[36] Z. Tian, L. Cui, J. Liang, and S. Yu, “A comprehensive survey on poisoning
attacks and countermeasures in machine learning,” ACM Comput. Surv.,
vol. 55, no. 8, pp. 1–35, 2022.
[37] J. Chen, X. Zhang, R. Zhang, C. Wang, and L. Liu, “De-Pois: An
attack-agnostic defense against data poisoning attacks,” IEEE Trans. Inf.
Forensics Secur., vol. 16, pp. 3412–3425, 2021.
[38] J. Chung, K. Kastner, L. Dinh, K. Goel, A. C. Courville, and Y. Bengio, “A
recurrent latent variable model for sequential data,” in Proc. Adv. Neural
Inf. Process. Syst., 2015, pp. 2980–2988.
[39] N. Megiddo and K. J. Supowit, “On the complexity of some common geometric location problems,” SIAM J. Comput., vol. 13, no. 1, pp. 182–196,
1984.
[40] K. Pillutla, S. M. Kakade, and Z. Harchaoui, “Robust aggregation for
federated learning,” IEEE Trans. Signal Process., vol. 70, pp. 1142–1154,
2022.
[41] M. Rashid and J. A. Nanzer, “Online expectation-maximization based
frequency and phase consensus in distributed phased arrays,” IEEE Trans.
Commun., vol. 71, no. 6, pp. 3721–3735, Jun. 2023.
[42] S. Garcia, M. Grill, J. Stiborek, and A. Zunino, “An empirical comparison
of botnet detection methods,” Comput. Secur., vol. 45, pp. 100–123, 2014.
[43] M. MontazeriShatoori, L. Davidson, G. Kaur, and A. H. Lashkari, “Detection of DoH tunnels using time-series classification of encrypted traffic,” in
Proc. IEEE Int. Conf. Dependable, Autonomic Secure Comput., Int. Conf.
Pervasive Intell. Comput., Int. Conf. Cloud Big Data Comput., Int. Conf.
Cyber Sci. Technol. Congr., 2020, pp. 63–70.
[44] W. Hu, J. Gao, B. Li, O. Wu, J. Du, and S. Maybank, “Anomaly detection
using local kernel density estimation and context-based regression,” IEEE
Trans. Knowl. Data Eng., vol. 32, no. 2, pp. 218–233, Feb. 2020.
[45] T. R. Bandaragoda, K. M. Ting, D. Albrecht, F. T. Liu, Y. Zhu, and
J. R. Wells, “Isolation-based anomaly detection using nearest-neighbor
ensembles,” Comput. Intell., vol. 34, no. 4, pp. 968–998, 2018.
Zhangfa Wu received the M.S. degree in electronic
science and technology in 2020 from the School
of Electronic Information Engineering, Northwestern Polytechnical University, Xi’an, China, where
he is currently working toward the Ph.D. degree in
electronic science and technology with the School
of Electronic Information Engineering. His research
interests include anomaly detection, network security,
deep learning, signal processing, and image processing.

WU et al.: POISON-RESILIENT ANOMALY DETECTION: MITIGATING POISONING ATTACKS

Huifang Li received the Ph.D degree from Northwestern Polytechnical University, Xi’an, China, in
2004. From 2010 to 2011, he was with the University of North Carolina, Chapel Hill, NC, USA, as a
Visiting Scholar sponsored by the China Scholarship
Council. He is currently a Professor with the School
of Electronic Information, Northwestern Polytechnical University. His research interests include deep
learning, network security, image processing, quantum information processing, intelligent information
processing, multimedia information processing, and
measurement and control technology.

Yekui Qian was born in 1980 in Anqing, Anhui,
China. He received the Ph.D. degree from People’s
Liberation Army University of Science and Technology, Beijing, China. He is currently a Professor
with People’s Liberation Army Air Force Academy,
Zhengzhou, China. His research interests include network measurement, vulnerability mining, deep learning, and network security.

4757

Yi Hua received the M.S. degree in signal and information processing from the School of Electronic
and Information Engineering, Southwest University,
Chongqing, China, in 2020. He is currently working
toward the Ph.D. degree in aerospace science and
technology with the School of Aeronautics, Northwestern Polytechnical University, Xi’an, China. From
2023, he is with the School of Electrical Engineering
and Computer Science, The University of Queensland, Brisbane, QLD, Australia, as a joint training
doctoral student under CSC scholarship. His research
interests include distributed signal processing, network security, image processing, robots, path planning, and information fusion of multiple aircraft.

Hongping Gan (Member, IEEE) received the Ph.D
degree in communication and information engineering from the State Key Laboratory of ISN, Xidian
University, Xi’an, China, in 2020. From 2018 to
2019, he was with the School of Information Technology and Electrical Engineering, The University of
Queensland, Brisbane, QLD, Australia, as a Visiting
Scholar sponsored by the China Scholarship Council.
He is currently an Associate Professor with the School
of Software, Northwestern Polytechnical University,
Xi’an. His research interests include deep learning,
compressive sensing, image processing, PolSAR ship detection, and network
security.
PAPER_TEXT
